"""TeachingService：教学命令的受信编排（T-local/T-intent/T-launch/T-result 调用方）。

服务只做有限组包与仓储 CAS 调用；模型经 run_one_call 受控链、工具经
ActivityService.execute_tool_action 的 G5 链；零费动作不调用模型、不修改
G/R/S。教学效果与正文在仓储同一事务原子提交（_write_teaching_outcome）。
"""
from __future__ import annotations

import asyncio
import json
import secrets
from datetime import datetime, timezone

from app.activities.service import ActivityService
from app.capabilities.contracts import ModelCallRequest, ToolCallPlan
from app.capabilities.gateway import ControlledModelGateway
from app.worker.one_call import OneCallInput, run_one_call
from app.worker.session import SessionConfig

from .contracts import canonical, sha
from .evidence import LearningRefusal, load_units, validate_snapshot
from .teaching_contracts import (
    ALL_ACTIONS,
    MAX_HTTP_BODY_BYTES,
    MODEL_ACTIONS,
    TOOL_ACTIONS,
    RecordRef,
    ReferenceHash,
    TeachingCallBinding,
    TeachingCommandInput,
    TeachingCommandReceipt,
    TeachingFrozenContext,
    TeachingMemoryFrozenContext,
    TeachingMemoryProfile,
    parse_frozen_context,
    TeachingRefusal,
    ToolFrozenCall,
)
from .teaching_evidence import assemble_teaching_catalog
from .teaching_prompt import messages_for_teaching, prompt_version
from .teaching_policy import compute_view_token, normalize_output_for_action

_RUN_TAG_PREFIX = "teach-"


class TeachingService:
    def __init__(self, ledger, materials, originals):
        self.ledger, self.materials, self.originals = ledger, materials, originals

    # --- 命令入口 ---

    async def submit_command(self, activity_id: str, command: TeachingCommandInput,
                             config, *, run_tag: str | None = None) -> TeachingCommandReceipt:
        if command.action not in ALL_ACTIONS:
            raise TeachingRefusal("invalid_input", "未知教学动作")
        if command.action in MODEL_ACTIONS or command.action in TOOL_ACTIONS:
            current=await self.ledger.read_teaching_command(activity_id,command.business_key)
            if current is not None:
                row=current['command']
                if row['request_sha256']!=command.request_sha256(activity_id) or row['request_body']!=canonical(command.canonical_request_body(activity_id)):
                    raise TeachingRefusal('command_key_conflict','同键已经绑定不同正文')
                if (row['status'] != 'accepted' or row['launch_claimed_at'] is not None
                        or row['obsolete_at'] is not None or row['abandoned_at'] is not None):
                    return self._read_receipt(current)
                # 只恢复持久原意图；不得重新检索或换掉已接受的冻结上下文。
                original = json.loads(row['request_body'])
                original.pop('activity_id')
                original['business_key'] = str(row['business_key'])
                original = TeachingCommandInput.model_validate(original)
                frozen = parse_frozen_context(json.loads(row['context_body']))
                from .teaching_contracts import frozen_context_digest
                if (frozen_context_digest(frozen) != row['context_sha256']
                        or frozen.operation_id != row['operation_id']
                        or frozen.kind != ('model' if command.action in MODEL_ACTIONS else 'tool')):
                    raise TeachingRefusal('integrity_error', '持久冻结上下文不一致，未恢复执行')
                tag = run_tag or _RUN_TAG_PREFIX + secrets.token_hex(12)
                if command.action in MODEL_ACTIONS:
                    return await self._submit_model(activity_id, original, config, tag, recovered=(current, frozen))
                return await self._submit_tool(activity_id, original, config, tag, recovered=(current, frozen))
        if command.action in MODEL_ACTIONS:
            return await self._submit_model(activity_id, command, config,
                                            run_tag or _RUN_TAG_PREFIX + secrets.token_hex(12))
        if command.action in TOOL_ACTIONS:
            return await self._submit_tool(activity_id, command, config,
                                           run_tag or _RUN_TAG_PREFIX + secrets.token_hex(12))
        return await self.ledger.apply_teaching_local(activity_id, command)

    @staticmethod
    def _read_receipt(view):
        row=view['command']; records=view.get('records',[])
        return TeachingCommandReceipt(activity_id=str(row['activity_id']),business_key=str(row['business_key']),action=row['action'],
            request_sha256=row['request_sha256'],status=row['status'],operation_id=row['operation_id'],error_code=row['error_code'],
            head_revision_now=view['head_revision'],record_ids=[RecordRef(record_id=str(r['record_id']),kind=r['kind'],seq=r['seq']) for r in records],
            payload_sha256=next((r['body_sha256'] for r in records if r['operation_id']),None),
            applied_revision=next((r['applied_revision'] for r in records if r['applied_revision']),None),
            qualification='memory_invalid' if view.get('memory_qualified') is False and row['action'] in ('plan','exercise','evaluate','calculate') else 'history_only' if row['status']=='history' else 'unconfirmed' if row['status'] in ('accepted','started','unknown') else 'current',
            retry_policy='read_only' if view.get('memory_qualified') is False else 'same_key_before_claim' if row['status']=='accepted' and row['launch_claimed_at'] is None
                and row['obsolete_at'] is None and row['abandoned_at'] is None else
                'explicit_new_key_after_confirmed_failure' if row['status'] in ('failed','not_sent') else
                'read_only' if row['status'] in ('accepted','started','unknown') else 'none')

    # --- 只读 ---

    async def read_workspace(self, activity_id: str, history_limit: int = 20) -> dict | None:
        return await self.ledger.read_teaching_workspace(activity_id, history_limit)

    async def read_command(self, activity_id: str, business_key: str) -> dict | None:
        return await self.ledger.read_teaching_command(activity_id, business_key)

    async def read_history(self, activity_id: str, limit: int = 20, before_seq: int | None = None):
        return await self.ledger.read_teaching_history(activity_id, limit, before_seq)

    async def read_record(self, activity_id: str, record_id: str) -> dict | None:
        return await self.ledger.read_teaching_record(activity_id, record_id)

    # --- 模型动作：T-intent → T-launch → 受控链 ---

    async def _submit_model(self, activity_id, command, config, run_tag, *, recovered=None) -> TeachingCommandReceipt:
        if (not config.teaching_layer.available or config.model_service is None
                or config.teaching_output_tokens is None):
            raise TeachingRefusal(config.teaching_layer.reason or "teaching_not_configured",
                                  "教学模型层未就绪，请核对本地教学配置")
        # 锁前组包冻结上下文（真实教学实体 + 受限资料目录），并在接受前
        # 完成受控通道序列化/配置兼容核验：组包或编码失败不得进入 accept，
        # 防止仅因组包错误消耗一次持久 launch（DEF-004）。
        if recovered is None:
            frozen, identity = await self._freeze_model_context(activity_id, command, config)
        else:
            current, frozen = recovered
            head = current.get('head') or {}
            if (head.get('revision') != command.expected_revision
                    or head.get('goal_version') != command.expected_goal_version
                    or current['activity']['scope_revision'] != command.expected_scope_revision):
                return self._read_receipt(current)
            identity = {name: head.get(name) for name in ('goal_record_id', 'goal_version',
                        'path_record_id', 'node_id', 'exercise_record_id', 'answer_record_id')}
            identity['correction_record_id'] = command.body.get('correction_record_id')
        if isinstance(frozen,TeachingMemoryFrozenContext):
            from app.memory.context import materialize_recipe,check_capacity
            from app.memory.contracts import MemoryRefusal
            try:
                selection=await self.ledger.read_memory_selection(activity_id,include_bodies=True)
                messages=await materialize_recipe(self.ledger,frozen.recipe,frozen.catalog,selection)
                from app.capabilities.contracts import Message
                messages=[Message.model_validate(m).model_dump(mode='json',exclude_none=True) for m in messages]
                if sha(canonical(messages))!=frozen.assembled_messages_sha256:
                    raise MemoryRefusal('memory_dependency_invalid','原背景消息身份不可复建')
                snapshot=await self.ledger.read_learning_snapshot(activity_id)
                check_capacity(messages,selection,getattr(config,'memory_context',None),snapshot,config.model_service)
            except MemoryRefusal as exc:raise TeachingRefusal(exc.code,exc.message) from None
        else:
            messages=frozen.messages
        profile = self._build_profile(activity_id, command, frozen, identity)
        request = ModelCallRequest(
            messages=[{"role": m["role"], "content": m["content"]} for m in messages],
            max_output_tokens=frozen.max_output_tokens,
            allowed_tools=frozenset(), teaching_profile=profile)
        service = config.model_service
        try:
            OneCallInput(command.operation_id(activity_id), request, service).to_wire()
        except (ValueError, TypeError):
            raise TeachingRefusal("context_limit", "教学上下文超过受控通道限额") from None
        session = SessionConfig()
        if service.timeout_seconds > session.request_timeout_seconds:
            raise TeachingRefusal("teaching_config_incompatible", "模型超时配置超过本地监督预算")
        receipt = (await self.ledger.accept_teaching_command(activity_id, command, frozen)
                   if recovered is None else self._read_receipt(recovered[0]))
        if receipt.status != "accepted" or receipt.duplicate_of:
            return receipt
        decision = await self.ledger.claim_teaching_launch(activity_id, command.business_key,
                                                           receipt.request_sha256)
        if not decision.get("launch_allowed"):
            # 已被其他线程 claim：只读核对，不再创建第二执行。
            current = await self.ledger.read_teaching_command(activity_id, command.business_key)
            if current is not None:
                row = current["command"]
                return TeachingCommandReceipt(
                    activity_id=activity_id, business_key=command.business_key, action=command.action,
                    request_sha256=row["request_sha256"], status=row["status"],
                    duplicate_of=receipt.duplicate_of, record_ids=[], operation_id=row["operation_id"],
                    head_revision_now=current["head_revision"],
                    qualification="unconfirmed" if row["status"] == "unknown" else "current",
                    error_code=row["error_code"], retry_policy="read_only")
            return receipt
        operation_id = decision["operation_id"]
        task = asyncio.create_task(asyncio.to_thread(
            run_one_call, self.ledger, session, activity_id, "local-ui", operation_id,
            request, service, run_tag=run_tag))
        cancelled = False
        while True:
            try:
                supervision = await asyncio.shield(task)
                break
            except asyncio.CancelledError:
                cancelled = True
                if task.done():
                    supervision = task.result()
                    break
            except Exception:
                if cancelled:
                    raise asyncio.CancelledError
                supervision = None
                break
        if cancelled:
            raise asyncio.CancelledError
        if supervision is None:
            # 监督链异常：命令保持 started/unknown；只读核对。
            current = await self.ledger.read_teaching_command(activity_id, command.business_key)
            row = current["command"] if current else None
            return TeachingCommandReceipt(
                activity_id=activity_id, business_key=command.business_key, action=command.action,
                request_sha256=receipt.request_sha256, status="unknown" if row is None else row["status"],
                duplicate_of=None, record_ids=[], operation_id=operation_id,
                head_revision_now=current["head_revision"] if current else 0,
                qualification="unconfirmed", error_code=None, retry_policy="read_only")
        # 监督已收尾：整理命令收据（无 outcome 的启动失败/未知分类）。
        # DEF-007：取消且无 model_receipt 不是未准入证明——监督窗口可能
        # 在 admit/mark 之后才被取消。只有监督在启动阶段即结束且未观察
        # 到模型收据的确定状态（未启动/预算预检失败/启动期限/窗口过小）
        # 才可判定「确定未准入」；其余（含 cancelled/failed_closed/settled
        # 异常）一律保守按 unknown 对账，pending 占槽保留。
        state_value = getattr(supervision, "state", "") or ""
        receipt_present = bool(getattr(supervision, "model_receipt", None)) \
            or bool(getattr(supervision, "tool_receipt", None))
        facts = {
            "state": state_value,
            "definitely_not_admitted": not receipt_present and state_value in (
                "not_started", "budget_exhausted", "startup_deadline",
                "partial_window_too_small"),
            "model_receipt": getattr(supervision, "model_receipt", None),
            "settled_seconds": getattr(supervision, "settled_seconds", None),
        }
        from .teaching_contracts import TeachingSupervisionFacts
        supervision_facts = TeachingSupervisionFacts.model_validate(facts, strict=False)
        return await self.ledger.finish_teaching_supervision(activity_id, command.business_key,
                                                             supervision_facts)

    async def _freeze_model_context(self, activity_id, command, config):
        """锁前组包冻结上下文（099 第 5.2/6.1 节）。

        装配真实教学实体——目标正文、路径节点、题与参考、已保存作答、
        纠错、有限前史与核算事实；reference_hashes 填真实
        {record_id, body_sha256}（至多 12 个）。接受事务在锁内逐项核对这些
        引用与当前持久事实一致（DEF-004 数据库屏障）：组包所用的旧快照
        不会绑定到已变化的实体，漂移即拒。
        """
        snapshot = await self.ledger.read_learning_snapshot(activity_id)
        validate_snapshot(snapshot)
        if self.materials is None:
            raise TeachingRefusal("unavailable", "资料存储尚未配置")
        request_sha = command.request_sha256(activity_id)
        identity, facts = await self._load_teaching_entities(activity_id, command)
        if identity["goal_record_id"] is None:
            raise TeachingRefusal("version_conflict", "教学尚未初始化，先保存目标")
        snapshot["teaching_query"] = facts["goal_text"].split("；",1)[0]
        query = self._context_query(command, snapshot, facts)
        units = await asyncio.to_thread(load_units, snapshot, self.materials, self.originals)
        catalog = assemble_teaching_catalog(query, units, request_sha)
        document = self._stored_document(command, snapshot, catalog, identity, facts)
        messages = messages_for_teaching(command.action, document)
        if len(messages) > 3:
            raise TeachingRefusal("context_limit", "教学消息超过 3 条上限")
        from app.capabilities.contracts import Message
        messages = [Message.model_validate(m).model_dump(mode="json",exclude_none=True) for m in messages]
        tokens = config.teaching_output_tokens
        references = [
            ReferenceHash(record_id=str(row["record_id"]), body_sha256=row["body_sha256"])
            for row in facts["references"][:12]]
        selection=await self.ledger.read_memory_selection(activity_id,include_bodies=True)
        if selection.get('selected') or not selection.get('eligible',True):
            from app.memory.context import make_recipe,materialize_recipe,check_capacity
            from app.memory.contracts import MemoryRefusal
            try:
                recipe=make_recipe(activity_id,command,identity,facts['references'])
                recipe['scope_revision']=command.expected_scope_revision
                messages=await materialize_recipe(self.ledger,recipe,catalog,selection)
                from app.capabilities.contracts import Message
                messages=[Message.model_validate(m).model_dump(mode='json',exclude_none=True) for m in messages]
                check_capacity(messages,selection,getattr(config,'memory_context',None),snapshot,config.model_service)
                refs=[{k:x[k] for k in ('memory_id','version','revision','body_sha256')} for x in selection['entries']]
                value={'schema':'teaching.context.v2','kind':'model','reference_hashes':[r.model_dump() for r in references],
                 'operation_id':command.operation_id(activity_id),'profile_version':'teaching.v2',
                 'prompt_version':'teaching-memory-prompt-v1','projection_policy_version':'teaching.memory.recipe.v1',
                 'max_output_tokens':tokens,'catalog':[e.model_dump() for e in catalog],
                 'recipe':recipe,'memory_selection_sha256':selection['selection_sha256'],'memory_refs':refs,
                 'assembled_messages_sha256':sha(canonical(messages))}
                value['context_sha256']=sha(canonical(value))
                return TeachingMemoryFrozenContext.model_validate(value),identity
            except MemoryRefusal as exc:raise TeachingRefusal(exc.code,exc.message) from None
        context_value = {
            "schema": "teaching.context.v1", "kind": "model",
            "reference_hashes": [r.model_dump() for r in references],
            "operation_id": command.operation_id(activity_id),
            "profile_version": "teaching.v1", "prompt_version": prompt_version(),
            "max_output_tokens": tokens, "messages": messages,
            "catalog": [e.model_dump() for e in catalog],
        }
        context_value["call"] = None
        context_sha = sha(canonical(context_value))
        frozen = TeachingFrozenContext(
            kind="model", reference_hashes=references, operation_id=context_value["operation_id"],
            context_sha256=context_sha, profile_version="teaching.v1",
            prompt_version=prompt_version(), max_output_tokens=tokens,
            messages=messages, catalog=catalog)
        return frozen, identity

    async def _load_teaching_entities(self, activity_id, command):
        """只读装配当前教学身份与相关实体（锁前快照；锁内 accept 复核）。"""
        head = await self.ledger.read_teaching_head(activity_id)
        identity = {
            "head_revision": 0 if head is None else head["revision"],
            "goal_record_id": None if head is None or head["goal_record_id"] is None
                              else str(head["goal_record_id"]),
            "goal_version": 0 if head is None else head["goal_version"],
            "path_record_id": None if head is None or head["path_record_id"] is None
                              else str(head["path_record_id"]),
            "node_id": None if head is None else head["node_id"],
            "exercise_record_id": None if head is None or head["exercise_record_id"] is None
                                  else str(head["exercise_record_id"]),
            "answer_record_id": None if head is None or head["answer_record_id"] is None
                                else str(head["answer_record_id"]),
            "correction_record_id": command.body.get("correction_record_id"),
        }
        facts: dict = {"references": [], "goal_text": None, "path_nodes": None,
                       "exercise_projection": None, "answer_text": None,
                       "correction_texts": [], "prior_observations": [],
                       "calculation_summary": None, "parent_feedback_summary": None,
                       "parent_exercise_record_id":None}
        seen: set[str] = set()

        async def collect(row):
            if row is None:
                return None
            rid = str(row["record_id"])
            if rid not in seen:
                seen.add(rid)
                facts["references"].append(row)
            return row

        def _clip(value, limit=512):
            text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
            return text[:limit]

        async def seven_summary(operation_id, keep):
            """读 007 规范正文并投影有限摘要；缺失按完整性拒绝。"""
            row = await self.ledger.read_operation(activity_id, operation_id)
            if row is None or getattr(row, "payload", None) is None:
                raise TeachingRefusal("record_not_found", "教学操作正文缺失，无法装配上下文")
            try:
                result = json.loads(row.payload)["value"]["result"]
            except (ValueError, TypeError, KeyError):
                raise TeachingRefusal("record_not_found", "教学操作正文不可解析") from None
            return keep(result)

        if identity["goal_record_id"] is not None:
            goal_row = await collect(await self.ledger.read_teaching_record(
                activity_id, identity["goal_record_id"]))
            if goal_row is not None and goal_row["body"]:
                try:
                    goal_body = json.loads(goal_row["body"])
                except ValueError:
                    raise TeachingRefusal("record_not_found", "目标正文不可解析") from None
                parts = [goal_body.get("goal") or ""]
                if goal_body.get("self_report"):
                    parts.append("自报: " + str(goal_body["self_report"])[:256])
                if goal_body.get("domain"):
                    parts.append("领域: " + str(goal_body["domain"])[:80])
                facts["goal_text"] = "；".join(p for p in parts if p)
        if identity["path_record_id"] is not None:
            path_row = await collect(await self.ledger.read_teaching_record(
                activity_id, identity["path_record_id"]))
            if path_row is not None and path_row["body"]:
                try:
                    facts["path_nodes"] = json.loads(path_row["body"]).get("nodes")
                except ValueError:
                    facts["path_nodes"] = None
        action = command.action
        if action == "plan":
            correction_id = command.body.get("correction_record_id")
            if correction_id:
                row = await collect(await self.ledger.read_teaching_record(activity_id, correction_id))
                if row is None:
                    raise TeachingRefusal("record_not_found", "纠错记录不存在")
                if row["body"]:
                    facts["correction_texts"].append(row["body"][:1024])
        elif action == "exercise":
            parent_feedback_id = command.body.get("parent_feedback_record_id")
            if parent_feedback_id:
                row = await collect(await self.ledger.read_teaching_record(activity_id, parent_feedback_id))
                if row is None:
                    raise TeachingRefusal("record_not_found", "父反馈记录不存在")
                if row.get("operation_id"):
                    facts["parent_exercise_record_id"] = str(row["exercise_record_id"])
                    parent_exercise = await collect(await self.ledger.read_teaching_record(activity_id,str(row["exercise_record_id"])))
                    if parent_exercise is None:
                        raise TeachingRefusal("record_not_found","父练习不存在")
                    facts["parent_feedback_summary"] = await seven_summary(
                        row["operation_id"],
                        lambda r: {"message": _clip(r.get("message"), 240),
                                   "dimensions": r.get("dimension_observations")})
        elif action == "evaluate":
            exercise_id = command.body["exercise_record_id"]
            answer_id = command.body["answer_record_id"]
            exercise_row = await collect(await self.ledger.read_teaching_record(activity_id, exercise_id))
            if exercise_row is None or exercise_row["kind"] != "exercise":
                raise TeachingRefusal("record_not_found", "练习不存在，无法评价")
            answer_row = await collect(await self.ledger.read_teaching_record(activity_id, answer_id))
            if answer_row is None or answer_row["kind"] != "answer":
                raise TeachingRefusal("record_not_found", "作答不存在，无法评价")
            if exercise_row.get("operation_id"):
                facts["exercise_projection"] = await seven_summary(
                    exercise_row["operation_id"], lambda r: {
                        "exercise_type": r.get("exercise_type"), "difficulty": r.get("difficulty"),
                        "stem": r.get("stem"), "dimensions": r.get("dimensions"),
                        "reference_points": r.get("reference_points"),
                        "reference_explanation": r.get("reference_explanation")})
            if answer_row["body"]:
                try:
                    facts["answer_text"] = json.loads(answer_row["body"]).get("text")
                except ValueError:
                    raise TeachingRefusal("record_not_found", "作答正文不可解析") from None
            # 本题反馈（前史与纠错链锚点），限 2 条。
            feedback_rows = await self.ledger.read_teaching_facts(
                activity_id, exercise_record_id=exercise_id, answer_record_id=answer_id,
                kinds=("feedback",), limit=2)
            feedback_ids = {str(r["record_id"]) for r in feedback_rows}
            correction_id=command.body.get('correction_record_id')
            if correction_id:
                correction=await collect(await self.ledger.read_teaching_record(activity_id,correction_id))
                if correction is None or correction['kind']!='correction':
                    raise TeachingRefusal('record_not_found','纠错事实不存在')
                target=await collect(await self.ledger.read_teaching_record(activity_id,str(correction['parent_record_id'])))
                if target is None or target['kind'] not in ('feedback','progress') or str(target['answer_record_id'])!=answer_id:
                    raise TeachingRefusal('answer_changed','纠错不属于本次作答')
                facts['correction_texts'].append(correction['body'][:1024])
            calcs = await self.ledger.read_teaching_facts(
                activity_id, answer_record_id=answer_id, kinds=("calculation",), limit=1)
            for row in calcs:
                await collect(row)
                if row.get("operation_id"):
                    calculation = await self.ledger.read_operation(activity_id,row["operation_id"])
                    if calculation is None or not calculation.payload:
                        raise TeachingRefusal("integrity_error","核算正文缺失")
                    facts["calculation_summary"] = {"operation_id":row["operation_id"],
                        "payload_sha256":row["body_sha256"],"value_decimal":json.loads(calculation.payload)["value"]}
            for row in feedback_rows:
                await collect(row)
                if row.get("operation_id"):
                    facts["prior_observations"].append(await seven_summary(
                        row["operation_id"],
                        lambda r: {"message": _clip(r.get("message"), 200),
                                   "dimensions": r.get("dimension_observations")}))
            # 纠错链：parent 指向本题 feedback 的 correction（O08 合法锚）。
            if feedback_ids:
                for row in await self.ledger.read_teaching_facts(
                        activity_id, kinds=("correction",), limit=6):
                    if str(row.get("parent_record_id")) in feedback_ids:
                        if str(row['record_id'])==correction_id:continue
                        await collect(row)
                        if row["body"]:
                            facts["correction_texts"].append(row["body"][:512])
                        if len(facts["correction_texts"]) >= 2:
                            break
            # 前史合计 ≤2048 字节（099 第 5.3 节）。
            while facts["prior_observations"] and len(json.dumps(
                    facts["prior_observations"], ensure_ascii=False).encode("utf-8")) > 2048:
                facts["prior_observations"].pop()
        if len(facts["references"]) > 12:
            facts["references"] = facts["references"][:12]
        return identity, facts

    @staticmethod
    def _context_query(command, snapshot, facts=None) -> str:
        if facts and command.action == 'exercise':
            node = next((n for n in facts.get('path_nodes') or [] if n.get('node_id')==command.body.get('node_id')), None)
            if node:
                return node['title']+' '+node['objective']
        if facts and command.action == 'evaluate':
            exercise = facts.get('exercise_projection') or {}
            if exercise.get('stem'):
                return exercise['stem']
        return snapshot.get("teaching_query") or "教学"

    @staticmethod
    def _stored_document(command, snapshot, catalog, identity, facts) -> dict:
        """发给模型的 user 投影：真实教学实体 + 受限目录；不含摘要自引用。

        DEF-004：目标/路径/题/参考/作答/纠错/前史/核算全部来自持久事实
        组装，不再使用 answer_pending 占位或空引用。
        """
        document = {
            "goal": facts["goal_text"] or "",
            "goal_version": identity["goal_version"],
            "scope_revision": snapshot["scope_revision"],
            "evidence": [{"id": e.citation_id, "source": e.title, "origin_kind": e.origin_kind,
                          "physical_page": e.physical_page, "lines": [e.start_line, e.end_line],
                          "text": e.text} for e in catalog],
        }
        action = command.action
        if action == "plan":
            document["task"] = {"kind": "plan"}
            if facts["correction_texts"]:
                document["task"]["corrections"] = facts["correction_texts"]
        elif action == "exercise":
            document["task"] = {"kind": "exercise",
                                "purpose": command.body.get("purpose", "initial"),
                                "node_id": command.body.get("node_id"),
                                "parent_feedback_record_id":command.body.get("parent_feedback_record_id"),
                                "parent_exercise_record_id":facts["parent_exercise_record_id"]}
            if facts["path_nodes"]:
                document["task"]["path_nodes"] = facts["path_nodes"]
            if facts["parent_feedback_summary"]:
                document["task"]["parent_feedback"] = facts["parent_feedback_summary"]
        elif action == "evaluate":
            document["task"] = {"kind": "evaluate",
                                "exercise": facts["exercise_projection"] or {},
                                "answer_text": facts["answer_text"] or ""}
            if facts["correction_texts"]:
                document["task"]["corrections"] = facts["correction_texts"]
            if facts["prior_observations"]:
                document["task"]["prior_observations"] = facts["prior_observations"]
            if facts["calculation_summary"]:
                document["task"]["calculation"] = facts["calculation_summary"]
        return document

    def _build_profile(self, activity_id, command, frozen, identity) -> object:
        from .teaching_contracts import TeachingProfile
        from .contracts import SourceIdentity
        sources = [SourceIdentity(source_id=s.source_id, version_id=s.version_id,
                                   source_revision=s.source_revision) for s in (frozen.catalog or [])]
        # sources 去重排序（沿 profile 校验要求）。
        seen = {}
        for identity_entry in sources:
            seen[identity_entry.source_id] = identity_entry
        ordered = [seen[k] for k in sorted(seen)]
        # DEF-004：profile 携带真实当前教学身份（goal/路径/题/答/纠错），
        # 全零占位与 CAS 猜测值不再出现；admit 锁内再据 DB 复核。
        profile_type=TeachingMemoryProfile if isinstance(frozen,TeachingMemoryFrozenContext) else TeachingProfile
        return profile_type(
            action=command.action if command.action in ("plan", "exercise", "evaluate") else "plan",
            command_key=command.business_key,
            request_sha256=command.request_sha256(activity_id),
            context_sha256=frozen.context_sha256,
            activity_id=activity_id,
            expected_revision=command.expected_revision,
            goal_record_id=identity["goal_record_id"],
            goal_version=max(identity["goal_version"], 1),
            path_record_id=identity["path_record_id"],
            node_id=identity["node_id"],
            exercise_record_id=identity["exercise_record_id"],
            answer_record_id=identity["answer_record_id"],
            correction_record_id=identity["correction_record_id"],
            scope_revision=command.expected_scope_revision,
            sources=ordered,
            catalog=frozen.catalog or [],
            messages_sha256=frozen.assembled_messages_sha256 if isinstance(frozen,TeachingMemoryFrozenContext) else sha(canonical(frozen.messages or [])),
            max_output_tokens=frozen.max_output_tokens or 256,
            **({"memory_selection_sha256":frozen.memory_selection_sha256,"memory_refs":frozen.memory_refs,
                "assembled_messages_sha256":frozen.assembled_messages_sha256} if isinstance(frozen,TeachingMemoryFrozenContext) else {}))

    # --- 工具动作：沿 G5 原链（ActivityService.execute_tool_action） ---

    async def _submit_tool(self, activity_id, command, config, run_tag, *, recovered=None) -> TeachingCommandReceipt:
        if not config.teaching_calculation_layer.available:
            raise TeachingRefusal(config.teaching_calculation_layer.reason or "tool_limit_unconfigured",
                                  "教学核算未启用：需要显式 finite_calculate 配置与工具额度")
        if recovered is None:
            # 冻结工具上下文：从已存数值参考构造固定 recipe（服务器生成，非用户自然语言）。
            record = await self.ledger.read_teaching_record(activity_id, command.body["exercise_record_id"])
            if record is None or record["kind"] != "exercise":
                raise TeachingRefusal("record_not_found", "练习不存在，无法核算")
            # 参考正文在 007：读取已暴露的 reference point 数值。
            exposures = await self.ledger.read_teaching_exposures(activity_id, command.body["exercise_record_id"])
            if "reference" not in exposures:
                raise TeachingRefusal("source_invalid", "参考要点尚未暴露，先查看参考再核算")
            numeric = await self._reference_numeric(activity_id, record, command.body["reference_point_id"])
            if numeric is None:
                raise TeachingRefusal("source_invalid", "该题无可核算数值参考点")
            point_id, operation, left, right = numeric
            if point_id != command.body["reference_point_id"]:
                raise TeachingRefusal("record_not_found", "指定参考点不匹配")
            arguments = {"operation": operation, "left": left, "right": right}
            from app.capabilities.contracts import canonical_tool_arguments
            arguments_json, arguments_sha = canonical_tool_arguments(arguments)
            operation_id = command.operation_id(activity_id)
            # DEF-004：工具冻结上下文同样携带真实引用 hash（题/答），接受时
            # 锁内核对；作答必须存在且匹配。
            head = await self.ledger.read_teaching_head(activity_id)
            references = [ReferenceHash(record_id=str(record["record_id"]),
                                        body_sha256=record["body_sha256"])]
            for rid in (head["goal_record_id"],head["path_record_id"]):
                parent = await self.ledger.read_teaching_record(activity_id,str(rid))
                if parent is None:
                    raise TeachingRefusal("integrity_error","核算缺少当前目标或路径")
                references.append(ReferenceHash(record_id=str(rid),body_sha256=parent["body_sha256"]))
            answer_id = command.body.get("answer_record_id")
            if answer_id:
                answer_row = await self.ledger.read_teaching_record(activity_id, answer_id)
                if answer_row is None or answer_row["kind"] != "answer":
                    raise TeachingRefusal("record_not_found", "作答不存在，无法核算")
                references.append(ReferenceHash(record_id=str(answer_row["record_id"]),
                                                body_sha256=answer_row["body_sha256"]))
            from .teaching_contracts import frozen_context_digest
            frozen = TeachingFrozenContext(
                kind="tool", reference_hashes=references,
                operation_id=operation_id,
                context_sha256=sha(canonical({"kind": "tool", "operation_id": operation_id,
                                              "arguments_sha256": arguments_sha})),
                call=ToolFrozenCall(call_id="tc-" + command.business_key[:8], name="finite_calculate",
                                    arguments_json=arguments_json, arguments_sha256=arguments_sha))
            frozen = parse_frozen_context(frozen.model_dump(by_alias=True) | {"context_sha256":frozen_context_digest(frozen)})
            receipt = await self.ledger.accept_teaching_command(activity_id, command, frozen)
        else:
            current, frozen = recovered
            if frozen.kind != "tool" or frozen.call is None:
                raise TeachingRefusal("integrity_error", "持久工具上下文不一致")
            arguments = json.loads(frozen.call.arguments_json)
            operation_id = frozen.operation_id
            receipt = self._read_receipt(current)
        if receipt.status != "accepted" or receipt.duplicate_of:
            return receipt
        decision = await self.ledger.claim_teaching_launch(activity_id, command.business_key,
                                                           receipt.request_sha256)
        if not decision.get("launch_allowed"):
            return receipt
        plan = ToolCallPlan(call_id=frozen.call.call_id, name="finite_calculate", arguments=arguments)
        outcome = await ActivityService(self.ledger).execute_tool_action(
            activity_id, operation_id, plan, SessionConfig(), "local-ui", run_tag)
        status = outcome.status
        current = await self.ledger.read_teaching_command(activity_id, command.business_key)
        row = current["command"] if current else None
        if current is not None:
            return self._read_receipt(current)
        return TeachingCommandReceipt(
            activity_id=activity_id, business_key=command.business_key, action=command.action,
            request_sha256=receipt.request_sha256,
            status="unknown",
            duplicate_of=receipt.duplicate_of, record_ids=[], operation_id=operation_id,
            head_revision_now=current["head_revision"] if current else 0,
            qualification="current", error_code=row["error_code"] if row else None,
            model_called=False, tool_called=True, retry_policy="none")

    async def _reference_numeric(self, activity_id, exercise_record, point_id):
        """从已提交 007 教学正文读 reference_points 的首个 numeric。"""
        try:
            row = await self.ledger.read_operation(activity_id, exercise_record["operation_id"])
        except Exception:
            return None
        if row is None or row.payload is None:
            return None
        try:
            document = json.loads(row.payload)
            result = document["value"]["result"]
            for point in result.get("reference_points", []):
                numeric = point.get("numeric")
                if numeric and point.get("point_id") == point_id:
                    return (point.get("point_id"), numeric["operation"],
                            self._tool_number(numeric["left"]), self._tool_number(numeric["right"]))
        except (ValueError, TypeError, KeyError):
            return None
        return None

    @staticmethod
    def _tool_number(value):
        from decimal import Decimal
        number = Decimal(value)
        result = int(number) if number == number.to_integral_value() else float(number)
        if Decimal(str(result)) != number:
            raise TeachingRefusal("context_limit","数值不能无损进入既有有限工具域")
        return result
