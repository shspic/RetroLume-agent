"""显式首学/续问薄服务，只经现有受监督one_call链调用。"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import json
from uuid import UUID

from app.activities.service import ActivityService
from app.capabilities.contracts import ModelCallRequest, ResultConsumptionRef
from app.capabilities.gateway import ControlledModelGateway
from app.worker.one_call import OneCallInput, run_one_call
from app.worker.session import SessionConfig
from .contracts import FIRST_PREFIX, NEXT_PREFIX, LearningProfile,LearningHybridProfile, canonical, normalize_input, read_document, request_fingerprint
from .evidence import LearningRefusal, assemble_catalog, load_units, query_check, validate_snapshot
from .prompt import messages_for
from app.data_exit.maintenance import owned_service


class LearningService:
    def __init__(self, ledger, materials, originals):
        self.ledger, self.materials, self.originals = ledger, materials, originals

    async def reconcile(self, activity_id, business_key, action):
        if str(UUID(business_key)) != business_key or action not in {"first", "followup"}:
            raise ValueError("invalid_input")
        prefix = FIRST_PREFIX if action == "first" else NEXT_PREFIX + business_key + "."
        operation_id = await self.ledger.find_learning_operation(activity_id, prefix)
        if operation_id is not None:return await self.ledger.read_operation(activity_id, operation_id)
        from app.capabilities.q_context import public_projection
        projection=await public_projection(self.ledger,activity_id,business_key)
        return {'outbound_approval':projection} if projection is not None else None

    @owned_service
    async def execute(self, activity_id, business_key, text, config, *, parent_operation_id=None, run_tag, retrieval_ref=None):
        from app.interview.contracts import InterviewRefusal
        try: await self.ledger.require_non_interview(activity_id)
        except InterviewRefusal as exc: raise LearningRefusal(exc.code,'此活动属于面试域或其资格不可核对') from None
        if parent_operation_id is not None and parent_operation_id.startswith('int10m.'):
            raise LearningRefusal('interview_parent_forbidden','面试成果不能成为学习输入')
        selection=await self.ledger.read_memory_selection(activity_id)
        if selection.get('selected') or not selection.get('eligible',True):
            raise LearningRefusal('memory_profile_required','此活动的背景请在教学工作区使用')
        if str(UUID(business_key)) != business_key:
            raise LearningRefusal("invalid_input", "业务键必须是规范UUID")
        if parent_operation_id is not None and parent_operation_id.startswith(("teach8m.", "teach8t.")):
            # G8：教学操作成果不能作为旧 learning.v1 续问父项，防绕教学阶段。
            raise LearningRefusal("result_kind_read_only", "教学成果请使用教学工作区续答入口")
        try:
            from app.capabilities.q_gateway import is_v2
            normalized=normalize_input(text)
            if config.model_service is not None and is_v2(config.model_service) and normalized!=text:
                raise ValueError('q_exact_input_required')
            text = normalized
        except ValueError as exc:
            raise LearningRefusal(str(exc), "请输入具体目标或问题，最多1024字和4096 UTF-8字节") from None
        action = "first" if parent_operation_id is None else "followup"
        goal, question, parent_sha, history, ref = text, None, None, None, None
        if action == "followup":
            parent = await self.ledger.read_committed_result(activity_id, parent_operation_id)
            if parent.read_status.value != "committed_current":
                raise LearningRefusal("result_invalidated", "父成果已失效或未提交，不能继续；历史成果保留")
            if parent.kind != "model":
                raise LearningRefusal("result_kind_read_only", "该成果不能作为学习续问依据")
            try:
                p, output = read_document(json.loads(parent.payload)["value"], activity_id=activity_id, operation_id=parent_operation_id)
            except (ValueError, TypeError, KeyError):
                raise LearningRefusal("result_kind_read_only", "普通模型成果请使用原显式继续入口") from None
            goal, question, parent_sha, history = p.goal, text, parent.payload_sha256, canonical(output.model_dump())
            ref = ResultConsumptionRef(activity_id=activity_id, operation_id=parent_operation_id,
                scope_revision=parent.scope_revision, payload_sha256=parent_sha)
        snapshot = await self.ledger.read_learning_snapshot(activity_id)
        sources = validate_snapshot(snapshot)
        query = question or goal
        if (not config.learning_layer.available or config.model_service is None
                or config.learning_output_tokens is None):
            raise LearningRefusal(config.learning_layer.reason or "learning_not_configured", "开始学习条件未就绪，请核对本地学习及模型配置")
        tokens = config.learning_output_tokens
        identity = dict(action=action, activity_id=activity_id, goal=goal, question=question,
            scope_revision=snapshot["scope_revision"], sources=[s.model_dump() for s in sources],
            parent_operation_id=parent_operation_id, parent_payload_sha256=parent_sha, max_output_tokens=tokens)
        if retrieval_ref is not None:identity['retrieval_ref']=retrieval_ref
        fingerprint = request_fingerprint(**identity)
        prefix = FIRST_PREFIX if action == "first" else NEXT_PREFIX + business_key + "."
        operation_id = prefix + fingerprint
        existing = await self.ledger.find_learning_operation(activity_id, prefix)
        if existing is not None:
            if existing != operation_id:
                raise LearningRefusal("learning_input_conflict", "该业务槽位已绑定不同目标、问题、范围或版本；请核对历史成果后显式续问或新建活动")
            business = await ActivityService(self.ledger).read_result(activity_id, existing)
            return {"operation_id": existing, "status": business.status, "business": business, "supervision": None}
        query_check(query, snapshot)
        if snapshot["deadline_at"] <= datetime.now(timezone.utc):
            raise LearningRefusal("activity_expired", "活动已到期，请创建新活动")
        if (snapshot["requests_reserved"] >= snapshot["max_requests"]
                or snapshot["cost_reserved_microunits"] + snapshot["reserve_cost_microunits"] > snapshot["max_cost_microunits"]
                or snapshot["running_reserved_seconds"] + snapshot["running_settled_seconds"] >= snapshot["max_running_seconds"]):
            raise LearningRefusal("budget_exhausted", "活动有限额度已用尽，不能开始新调用")
        if tokens > snapshot["max_output_tokens"] or tokens > config.model_service.max_output_tokens_limit:
            raise LearningRefusal("output_token_limit", "学习输出配置超过活动或服务上限，未开始调用")
        if self.materials is None:
            raise LearningRefusal("unavailable", "资料存储尚未配置")
        saved=None
        if is_v2(config.model_service):
            from app.data_exit.q_store import authority_for
            authority=authority_for(self.ledger)
            if authority is None:raise LearningRefusal('q_control_missing','本轮外发批准未就绪')
            saved=next((row for row in authority.hub.state()['q']['requests'].values() if row['prepared']['domain']=='learning'
                and row['prepared']['activity_id']==activity_id and (row['prepared']['business_key']==business_key
                or row['prepared']['action']==action=='first')),None)
            if saved is not None:
                if saved['prepared']['operation_id']!=operation_id or saved['prepared']['business_key']!=business_key:
                    raise LearningRefusal('learning_input_conflict','请保留已冻结的原目标、问题和原业务键')
                if saved.get('launch_claimed') or saved.get('claim'):
                    return {'operation_id':operation_id,'status':'supervision_unknown','business':await ActivityService(self.ledger).read_result(activity_id,operation_id),
                            'supervision':None,'outbound_approval':authority.projection(saved)}
        units = await asyncio.to_thread(load_units, snapshot, self.materials, self.originals) if saved is None else None
        if saved is not None:
            catalog=None
        elif retrieval_ref is not None:
            from app.retrieval.service import RetrievalService
            from app.retrieval.contracts import RetrievalRefusal
            try:catalog=await RetrievalService(self.ledger,self.materials,self.originals).catalog(activity_id,retrieval_ref,fingerprint)
            except RetrievalRefusal as exc:raise LearningRefusal(exc.code,'本轮检索不可用，请核对原操作') from None
        else:catalog = assemble_catalog(query, units, fingerprint)
        if saved is not None:
            artifact=authority.artifact(saved)
            if artifact['intent']!=json.loads(canonical(identity)):
                raise LearningRefusal('learning_input_conflict','原冻结意图与本次请求不同')
            request=ModelCallRequest.model_validate(artifact['request'])
        else:
            profile = (LearningHybridProfile if retrieval_ref is not None else LearningProfile)(**identity, request_sha256=fingerprint, catalog=catalog, history=history)
            request = ModelCallRequest(messages=messages_for(profile), max_output_tokens=tokens,
                allowed_tools=frozenset(), input_result=ref, learning_profile=profile,retrieval_ref=retrieval_ref)
        service = config.model_service
        encoded = json.dumps(ControlledModelGateway(service)._build_payload(request),
            ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
        if len(encoded) > min(snapshot["max_request_bytes"], service.max_request_bytes):
            raise LearningRefusal("learning_context_limit", "目标、历史与证据超过单次请求限额，请缩小问题或新建较小范围活动")
        try:
            OneCallInput(operation_id, request, service).to_wire()
        except (ValueError, TypeError):
            raise LearningRefusal("learning_context_limit", "学习上下文超过受控通道限额，请缩小问题或活动范围") from None
        session = SessionConfig()
        if service.timeout_seconds > session.request_timeout_seconds:
            raise LearningRefusal("config_incompatible", "模型超时配置超过本地监督预算")
        if is_v2(service):
            from app.capabilities.q_context import prepare,claim_approved
            projection,service=await prepare(self.ledger,activity_id,business_key,operation_id,request,service,
                ControlledModelGateway(service)._build_payload(request),domain='learning',action=action,intent=identity)
            if not projection['can_continue']:
                return {'operation_id':operation_id,'status':'awaiting_approval','business':await ActivityService(self.ledger).read_result(activity_id,operation_id),
                        'supervision':None,'outbound_approval':projection}
            await claim_approved(self.ledger,service)
        task = asyncio.create_task(asyncio.to_thread(run_one_call, self.ledger, session, activity_id,
            "local-ui", operation_id, request, service, run_tag=run_tag))
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
                return {"operation_id": operation_id, "status": "supervision_unknown",
                    "business": await ActivityService(self.ledger).read_result(activity_id, operation_id), "supervision": None}
        if cancelled:
            raise asyncio.CancelledError
        business = await ActivityService(self.ledger).read_result(activity_id, operation_id)
        status = business.status
        if status in {"no_operation", "unresolved"}:
            status = supervision.state if supervision.state in {"cancelled", "budget_exhausted"} else "supervision_unknown"
            receipt = supervision.model_receipt
            if receipt and receipt["result"].get("error_code"):
                status = receipt["result"]["error_code"]
        return {"operation_id": operation_id, "status": status, "business": business, "supervision": supervision}
