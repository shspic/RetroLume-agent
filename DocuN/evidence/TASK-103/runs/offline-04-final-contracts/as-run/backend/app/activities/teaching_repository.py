"""G8 教学领域仓储方法（TASK-100）。

作为 Mixin 挂到 PostgresAdmissionLedger；全部方法经 self._transaction
（同一短事务、同一锁序：来源 UUID 排序→活动→相关 operation→
teaching_heads→teaching_commands 键排序→新 records）执行。教学 helper
只使用传入 connection，不嵌套事务。网络/工具执行永远在事务外。
"""
from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from uuid import UUID, uuid4

# head 指针哨兵：显式置空；None 表示本次不改动该列。
_HEAD_CLEAR = "__clear__"

from app.capabilities.contracts import LedgerDisposition

from app.learning.teaching_contracts import (
    CONTEXT_SCHEMA,
    MAX_ANSWERS,
    MAX_COMMANDS_PER_ACTIVITY,
    MAX_CORRECTIONS,
    MAX_EXERCISES,
    MAX_GOAL_VERSION,
    MAX_PATHS,
    MAX_RECORDS,
    MAX_RECORD_BODY_BYTES,
    MAX_STATE_AFTER_BYTES,
    RECORD_KINDS,
    STATE_SCHEMA,
    TEACHING_PREFIX_MODEL,
    TEACHING_PREFIX_TOOL,
    RecordRef,
    TeachingCallBinding,
    TeachingCommandInput,
    TeachingCommandReceipt,
    TeachingFrozenContext,
    TeachingMemoryFrozenContext,
    parse_frozen_context,
    TeachingRefusal,
    semantic_slot,
)
from app.learning.contracts import canonical, sha
from app.learning.teaching_policy import validate_transition, validate_path, derive_support_checks

_HISTORY_LIMIT_DEFAULT = 20
_HISTORY_LIMIT_MAX = 50
_PROJECTION_DEFAULT = {}


class _TeachingLocked:
    """锁内教学行集合；仅内部使用。"""

    __slots__ = ("activity", "head", "command")

    def __init__(self, activity, head, command):
        self.activity, self.head, self.command = activity, head, command


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _row_receipt(row: dict, head_revision: int, *, record_ids=None, qualification="current",
                 duplicate_of=None) -> TeachingCommandReceipt:
    return TeachingCommandReceipt(
        activity_id=str(row["activity_id"]),
        business_key=str(row["business_key"]),
        action=row["action"],
        request_sha256=row["request_sha256"],
        status=row["status"],
        duplicate_of=duplicate_of,
        record_ids=record_ids or [],
        operation_id=row["operation_id"],
        payload_sha256=None,
        applied_revision=None,
        head_revision_now=head_revision,
        qualification=qualification,
        error_code=row["error_code"],
        model_called=None,
        tool_called=None,
        retry_policy="none",
        exposed_part=None,
    )


def _state_after(revision: int, head: dict) -> str:
    value = {
        "schema": STATE_SCHEMA, "revision": revision,
        "goal_version": head["goal_version"], "phase": head["phase"],
        "goal_record_id": head["goal_record_id"], "path_record_id": head["path_record_id"],
        "node_id": head["node_id"], "exercise_record_id": head["exercise_record_id"],
        "answer_record_id": head["answer_record_id"], "feedback_record_id": head["feedback_record_id"],
        "reason_record_id": head["reason_record_id"],
        "projection": _decode(head.get("projection") or {}),
    }
    encoded = canonical(_plain(value))
    if len(encoded.encode("utf-8")) > MAX_STATE_AFTER_BYTES:
        raise TeachingRefusal("result_limit", "教学状态投影超过上限")
    return encoded


def _plain(value):
    if isinstance(value, (UUID, datetime)):
        return str(value) if isinstance(value, UUID) else value.isoformat()
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    return value


def _decode(value):
    return json.loads(value) if isinstance(value, str) else value


class TeachingLedgerMethods:
    """教学命令/事实/投影的持久实现；失败关闭，不伪造资格。"""

    # --- 锁内公共 ---

    async def _teaching_lock(self, connection, activity_id: str, *, original_record_id=None) -> _TeachingLocked:
        from app.learning.teaching_views import bound_references
        extra=[]
        if original_record_id is not None:
            row=await self._teaching_read_record_row(connection,activity_id,original_record_id)
            refs=None if row is None else bound_references(row)
            if refs is None:raise TeachingRefusal('source_invalid','原练习来源身份不可核对')
            extra=refs
        state=await self._memory_lock_prefix(connection,activity_id,extra_sources=extra)
        activity=state['activity']
        if activity is None:raise TeachingRefusal('not_found','活动不存在')
        await self._teaching_lock_operations(connection,activity_id)
        activity['_teaching_sources_valid']=state['sources_valid'] and state['eligible']
        activity['_teaching_sources']=_plain(state['snapshots'])
        cursor=await connection.execute("SELECT * FROM teaching_heads WHERE activity_id=%s FOR UPDATE",(activity_id,))
        head=await cursor.fetchone()
        await connection.execute("SELECT business_key FROM teaching_commands WHERE activity_id=%s ORDER BY business_key FOR UPDATE",(activity_id,))
        return _TeachingLocked(activity,head,None)

    async def _teaching_lock_operations(self,connection,activity_id):
        await connection.execute("SELECT operation_id FROM activity_operations WHERE activity_id=%s ORDER BY operation_id FOR UPDATE",(activity_id,))

    async def _teaching_lock_command(self, connection, activity_id: str, business_key: str, *, original_record_id=None) -> _TeachingLocked:
        locked = await self._teaching_lock(connection, activity_id, original_record_id=original_record_id)
        cursor = await connection.execute(
            "SELECT * FROM teaching_commands WHERE activity_id = %s AND business_key = %s FOR UPDATE",
            (activity_id, business_key))
        locked.command = await cursor.fetchone()
        return locked

    @staticmethod
    def _teaching_replay(command_row: dict, request_sha: str, request_body: str) -> bool:
        return command_row["request_sha256"] == request_sha and command_row["request_body"] == request_body

    async def _teaching_slot_winner(self, connection, activity_id: str, action: str, slot: str):
        cursor = await connection.execute(
            """SELECT * FROM teaching_commands
                WHERE activity_id = %s AND action = %s AND slot_sha256 = %s
                  AND status IN ('accepted','started','unknown','committed','history')
                ORDER BY created_at, business_key LIMIT 1""",
            (activity_id, action, slot))
        return await cursor.fetchone()

    async def _teaching_counts(self, connection, activity_id: str) -> dict:
        cursor = await connection.execute(
            """SELECT
                 (SELECT count(*) FROM teaching_commands WHERE activity_id=%s) AS commands,
                 (SELECT count(*) FROM teaching_records WHERE activity_id=%s) AS records,
                 (SELECT count(*) FROM teaching_records WHERE activity_id=%s AND kind='exercise') AS exercises,
                 (SELECT count(*) FROM teaching_records WHERE activity_id=%s AND kind='answer') AS answers,
                 (SELECT count(*) FROM teaching_records WHERE activity_id=%s AND kind='correction') AS corrections,
                 (SELECT count(*) FROM teaching_records WHERE activity_id=%s AND kind='path_accept') AS paths""",
            (activity_id, activity_id, activity_id, activity_id, activity_id, activity_id))
        return await cursor.fetchone()

    @staticmethod
    def _teaching_cas(head, expected_revision: int, expected_goal_version: int,
                      expected_scope_revision: int, activity, action: str) -> None:
        if activity["scope_revision"] != expected_scope_revision:
            raise TeachingRefusal("version_conflict", "活动范围已变化，请刷新工作区")
        if head is None:
            if expected_revision != 0 or expected_goal_version != 0 or action != "goal":
                raise TeachingRefusal("version_conflict", "教学状态已存在或前提不符，请刷新工作区")
            return
        if head["revision"] != expected_revision:
            raise TeachingRefusal("version_conflict", "教学修订版本已变化，请刷新工作区")
        if head["goal_version"] != expected_goal_version:
            raise TeachingRefusal("goal_changed", "目标版本已变化，请刷新工作区")
        if activity["scope_revision"] != expected_scope_revision:
            raise TeachingRefusal("version_conflict", "活动范围已变化，请刷新工作区")

    @staticmethod
    def _teaching_gate(activity, *, for_write: bool = True) -> None:
        now = datetime.now(timezone.utc)
        if activity["status"] == "cancelled":
            raise TeachingRefusal("activity_cancelled", "活动已取消，教学动作不可用；历史可读")
        if activity["deadline_at"] <= now:
            raise TeachingRefusal("activity_expired", "活动已到期，教学动作不可用；历史可读")
        # pending/dispatch_closed 是已结算窗口的正常状态。新模型窗口由原
        # claim_lease 重开门；零费用户事实不消费这个正文发送门。

    @staticmethod
    def _teaching_budget(activity,frozen):
        if activity['max_running_seconds']-activity['running_reserved_seconds']-activity['running_settled_seconds']<=20:
            raise TeachingRefusal('budget_exhausted','剩余运行额度不足以完成有限窗口')
        if frozen.kind=='model':
            if (activity['requests_reserved']>=activity['max_requests'] or activity['cost_reserved_microunits']+activity['reserve_cost_microunits']>activity['max_cost_microunits']):
                raise TeachingRefusal('budget_exhausted','模型次数或费用额度已用尽')
            if frozen.max_output_tokens>activity['max_output_tokens']:
                raise TeachingRefusal('teaching_config_incompatible','教学输出超过活动上限')
        elif activity['max_tool_calls'] is None:
            raise TeachingRefusal('tool_limit_unconfigured','工具额度未配置')
        elif activity['tools_reserved']>=activity['max_tool_calls']:
            raise TeachingRefusal('tool_limit_exhausted','有限工具额度已用尽')

    async def _teaching_insert_record(self, connection, activity_id, record_id, seq, kind,
                                      business_key, ordinal, goal_version, scope_revision,
                                      body, body_sha, *, goal_record_id=None, parent_record_id=None,
                                      exercise_record_id=None, answer_record_id=None,
                                      supersedes_record_id=None, operation_id=None,
                                      applied_revision=None, state_after=None, source_refs=None) -> None:
        source_ref_text = source_refs if source_refs is not None else json.dumps(
            [], ensure_ascii=False, separators=(",", ":"))
        await connection.execute(
            """INSERT INTO teaching_records(activity_id,record_id,seq,kind,business_key,ordinal,
                   goal_version,scope_revision,goal_record_id,parent_record_id,exercise_record_id,
                   answer_record_id,supersedes_record_id,operation_id,body,body_sha256,source_refs,
                   applied_revision,state_after,created_at)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,CURRENT_TIMESTAMP)""",
            (activity_id, record_id, seq, kind, business_key, ordinal, goal_version, scope_revision,
             goal_record_id, parent_record_id, exercise_record_id, answer_record_id,
             supersedes_record_id, operation_id, body, body_sha, source_ref_text,
             applied_revision, state_after))

    async def _teaching_update_head(self, connection, activity_id, head, revision, phase=None,
                                   goal_version=None, goal_record_id=None, path_record_id=None,
                                   node_id=None, exercise_record_id=None, answer_record_id=None,
                                   feedback_record_id=None, reason_record_id=None,
                                   pending_business_key="unset", last_seq=None, projection=None) -> None:
        """head 增量更新。

        哨兵 CLEAR 表示「把该指针置空」；None 表示「本次不改动该列」。
        CLEAR 必须对所有列一致生效：只处理 node_id 会让 _HEAD_CLEAR 被当作
        UUID 字面量传给 PostgreSQL（22P02），第二版目标等路径必然失败。
        本方法只写 teaching_heads；教学事实正文一经 INSERT 不可再改
        （DEF-003：applied_revision/state_after 在插入时即为最终值）。
        """
        updates = ["revision = %s", "updated_at = CURRENT_TIMESTAMP"]
        params: list = [revision]
        for column, value in (("phase", phase), ("goal_version", goal_version),
                              ("goal_record_id", goal_record_id), ("path_record_id", path_record_id),
                              ("node_id", node_id), ("exercise_record_id", exercise_record_id),
                              ("answer_record_id", answer_record_id),
                              ("feedback_record_id", feedback_record_id),
                              ("reason_record_id", reason_record_id)):
            if value is None:
                continue
            if value == _HEAD_CLEAR:
                updates.append(f"{column} = NULL")
                continue
            updates.append(f"{column} = %s")
            params.append(value)
        if pending_business_key != "unset":
            updates.append("pending_business_key = %s")
            params.append(pending_business_key)
        if last_seq is not None:
            updates.append("last_seq = %s")
            params.append(last_seq)
        if projection is not None:
            updates.append("projection = %s")
            params.append(canonical(_plain(projection)))
        params.append(activity_id)
        await connection.execute(
            f"UPDATE teaching_heads SET {', '.join(updates)} WHERE activity_id = %s", tuple(params))

    async def _teaching_create_head(self, connection, activity_id, revision, goal_version,
                                    phase, goal_record_id, last_seq) -> None:
        await connection.execute(
            """INSERT INTO teaching_heads(activity_id,revision,goal_version,last_seq,phase,goal_record_id)
               VALUES (%s,%s,%s,%s,%s,%s)""",
            (activity_id, revision, goal_version, last_seq, phase, goal_record_id))

    async def _teaching_obsolete_pending(self, connection, activity_id, *, except_key=None,
                                         mark_goal=False) -> None:
        """旧 pending/在途命令 obsolete；不递增 G、不清租约或四账。"""
        conditions = "activity_id = %s AND status IN ('accepted','started') AND obsolete_at IS NULL"
        params: list = [activity_id]
        if except_key is not None:
            conditions += " AND business_key <> %s"
            params.append(except_key)
        await connection.execute(
            f"UPDATE teaching_commands SET obsolete_at=CURRENT_TIMESTAMP, "
            f"updated_at=CURRENT_TIMESTAMP WHERE {conditions}", tuple(params))

    async def _teaching_fact_result(self, connection, activity_id, row):
        """只在原连接读取并核对不可变正文；不接受缺失或伪 hash。"""
        if row is None:
            raise TeachingRefusal("record_not_found", "教学事实不存在")
        if row["body"] is not None:
            if sha(row["body"]) != row["body_sha256"]:
                raise TeachingRefusal("integrity_error", "教学事实摘要不一致")
            return _decode(row["body"])
        cursor = await connection.execute(
            "SELECT payload,payload_format,payload_sha256 FROM activity_operation_results "
            "WHERE activity_id=%s AND operation_id=%s", (activity_id, row["operation_id"]))
        payload = await cursor.fetchone()
        if payload is None or payload["payload_sha256"] != row["body_sha256"]:
            raise TeachingRefusal("integrity_error", "教学正文绑定缺失")
        from app.capabilities.contracts import validate_business_payload
        try:
            validate_business_payload(payload["payload"], payload["payload_format"], payload["payload_sha256"])
            envelope = _decode(payload["payload"])
            return envelope["value"] if row["kind"] == "calculation" else envelope["value"]["result"]
        except (ValueError, TypeError, KeyError):
            raise TeachingRefusal("integrity_error", "教学正文无法核对") from None

    async def _teaching_verify_current(self, connection, activity, head, command, frozen):
        """T-intent/launch/admit/mark 共用锁内当前资格，不用于拒绝合法迟到结果。"""
        if head is None or str(head.get("pending_business_key") or "") != str(command["business_key"]):
            raise TeachingRefusal("unknown_slot", "命令不是当前待执行动作")
        if (head["revision"] != command["expected_revision"]
                or head["goal_version"] != command["goal_version"]
                or activity["scope_revision"] != command["scope_revision"]
                or command.get("obsolete_at") is not None or command.get("abandoned_at") is not None):
            raise TeachingRefusal("version_conflict", "教学绑定已改变")
        if not activity.get('_memory_eligible',True):
            raise TeachingRefusal('memory_dependency_invalid','所选学习背景已更新或撤销')
        if isinstance(frozen,TeachingMemoryFrozenContext):
            cursor=await connection.execute("SELECT selection_sha256 FROM public.activity_memory_bindings WHERE activity_id=%s",(str(activity['id']),))
            selected=await cursor.fetchone()
            if selected is None or selected['selection_sha256']!=frozen.memory_selection_sha256:
                raise TeachingRefusal('memory_dependency_invalid','固定背景选择不符')
        if frozen.operation_id != command["operation_id"]:
            raise TeachingRefusal("unknown_slot", "冻结操作身份不一致")
        from app.learning.teaching_contracts import frozen_context_digest
        if frozen_context_digest(frozen) != frozen.context_sha256:
            raise TeachingRefusal("integrity_error", "冻结上下文摘要不一致")
        request = _decode(command["request_body"])
        if sha(command["request_body"]) != command["request_sha256"] or request["action"] != command["action"]:
            raise TeachingRefusal("integrity_error", "命令内容摘要不一致")
        body = request["body"]
        action = command["action"]
        validate_transition(action, head["phase"], purpose=body.get("purpose"))
        required = {str(head["goal_record_id"]): "goal"}
        if action in ("exercise", "evaluate", "calculate"):
            if head["path_record_id"] is None:
                raise TeachingRefusal("stage_conflict", "尚无已接受路径")
            required[str(head["path_record_id"])] = "path_accept"
        if action == "exercise":
            if str(head["path_record_id"]) != body["path_record_id"] or head["node_id"] != body["node_id"]:
                raise TeachingRefusal("version_conflict", "路径或节点已改变")
            if body.get("parent_feedback_record_id"):
                if str(head["feedback_record_id"]) != body["parent_feedback_record_id"]:
                    raise TeachingRefusal("version_conflict", "父反馈已改变")
                required[body["parent_feedback_record_id"]] = "feedback"
        if action in ("evaluate", "calculate"):
            if (str(head["exercise_record_id"]) != body["exercise_record_id"]
                    or str(head["answer_record_id"]) != body["answer_record_id"]):
                raise TeachingRefusal("answer_changed", "题目或答案已改变")
            required[body["exercise_record_id"]] = "exercise"
            required[body["answer_record_id"]] = "answer"
        if body.get("correction_record_id"):
            required[body["correction_record_id"]] = "correction"
        references = {r.record_id: r for r in frozen.reference_hashes}
        if not set(required).issubset(references):
            raise TeachingRefusal("integrity_error", "冻结上下文缺少必要事实")
        rows = {}
        for reference in frozen.reference_hashes:
            row = await self._teaching_read_record_row(connection, str(activity["id"]), reference.record_id)
            if row is None or row["body_sha256"] != reference.body_sha256:
                raise TeachingRefusal("version_conflict", "冻结引用已改变")
            if reference.record_id in required and row["kind"] != required[reference.record_id]:
                raise TeachingRefusal("integrity_error", "教学父事实类型不一致")
            if row["goal_version"] != head["goal_version"] or row["scope_revision"] != activity["scope_revision"]:
                raise TeachingRefusal("version_conflict", "冻结事实属于旧版本")
            await self._teaching_fact_result(connection, str(activity["id"]), row)
            rows[reference.record_id] = row
        if action in ("evaluate", "calculate") and str(rows[body["answer_record_id"]]["exercise_record_id"]) != body["exercise_record_id"]:
            raise TeachingRefusal("answer_changed", "作答与题目不一致")
        if body.get("correction_record_id") and action == "evaluate":
            correction = rows[body["correction_record_id"]]
            target = await self._teaching_read_record_row(connection, str(activity["id"]), correction["parent_record_id"])
            if target is None or str(target["answer_record_id"]) != body["answer_record_id"]:
                raise TeachingRefusal("answer_changed", "纠错不属于本次答案")
        if frozen.kind == "model":
            snapshots = await self._source_rows(connection, str(activity["id"]))
            authoritative = {(str(s["source_id"]),str(s["version_id"]),s["source_revision"]) for s in snapshots}
            if not frozen.catalog:
                raise TeachingRefusal("source_invalid", "教学目录为空")
            for entry in frozen.catalog:
                if (entry.source_id,entry.version_id,entry.source_revision) not in authoritative:
                    raise TeachingRefusal("source_invalid", "冻结资料不属于活动范围")
                cursor = await connection.execute(
                    "SELECT v.sha256,v.filename,v.format FROM material_versions v JOIN material_sources m "
                    "ON m.id=v.source_id WHERE v.id=%s AND m.id=%s AND m.current_version=v.id AND m.revision=%s",
                    (entry.version_id,entry.source_id,entry.source_revision))
                source = await cursor.fetchone()
                if source is None or source["sha256"] != entry.original_sha256 or source["filename"] != entry.title or source["format"] != entry.format:
                    raise TeachingRefusal("source_invalid", "冻结资料身份已改变")
                if source['format']=='pdf':
                    cursor=await connection.execute("SELECT EXISTS (SELECT 1 FROM pdf_review_candidates c WHERE c.version_id=%s "
                        "AND c.status='confirmed' AND c.page_count BETWEEN 1 AND 50 "
                        "AND (SELECT count(*) FROM pdf_review_pages p WHERE p.candidate_id=c.id)=c.page_count "
                        "AND (SELECT count(*) FROM pdf_extracted_pages p WHERE p.version_id=c.version_id)=c.page_count) AS ready",(entry.version_id,))
                    if not (await cursor.fetchone())['ready']:raise TeachingRefusal('source_invalid','PDF 尚未具备可核对页')
        return rows

    async def _teaching_rebuild_progress(self, connection, activity_id, head, extra=None):
        guard=await self._memory_sql_guard(connection,"%s")
        cursor=await connection.execute("SELECT "+guard+" AS valid",tuple(activity_id for _ in range(guard.count('%s'))))
        if not (await cursor.fetchone())['valid']:
            raise TeachingRefusal('memory_dependency_invalid','失效背景不能重建当前进度')
        path = await self._teaching_read_record_row(connection, activity_id, head["path_record_id"])
        path_body = await self._teaching_fact_result(connection, activity_id, path)
        cursor = await connection.execute(
            "SELECT r.*,p.parent_record_id AS correction_feedback_id,o.payload,o.payload_format,o.payload_sha256 FROM teaching_records r "
            "LEFT JOIN teaching_records p ON p.activity_id=r.activity_id AND p.record_id=r.parent_record_id AND r.kind='correction' AND p.kind='progress' "
            "LEFT JOIN activity_operation_results o ON o.activity_id=r.activity_id AND o.operation_id=r.operation_id "
            "WHERE r.activity_id=%s AND r.goal_version=%s AND r.kind=ANY(%s) ORDER BY r.seq",
            (activity_id,head["goal_version"],["exercise","answer","feedback","correction"]))
        facts = await cursor.fetchall()
        if extra:
            facts.append(extra)
        from app.capabilities.contracts import validate_business_payload
        for row in facts:
            if row.get('correction_feedback_id'):
                row['parent_record_id']=row['correction_feedback_id']
            if row["operation_id"]:
                try:
                    validate_business_payload(row["payload"],row["payload_format"],row["payload_sha256"])
                    if row["body_sha256"] != row["payload_sha256"]:
                        raise ValueError
                    row["document"] = _decode(row["payload"])["value"]
                except (ValueError,TypeError,KeyError):
                    raise TeachingRefusal("integrity_error","当前观察正文不完整") from None
            elif sha(row["body"]) != row["body_sha256"]:
                raise TeachingRefusal("integrity_error","当前观察摘要不一致")
        from app.learning.teaching_progress import rebuild_progress
        return rebuild_progress(path_body["nodes"],facts,str(head["path_record_id"])),path_body["nodes"]

    async def _teaching_original_receipt(self, connection, activity_id, command, head_revision):
        cursor = await connection.execute(
            "SELECT record_id,kind,seq,applied_revision,operation_id,body_sha256 FROM teaching_records "
            "WHERE activity_id=%s AND business_key=%s ORDER BY ordinal",(activity_id,command["business_key"]))
        rows = await cursor.fetchall()
        receipt = _row_receipt(command, head_revision, record_ids=[RecordRef(record_id=str(r["record_id"]),kind=r["kind"],seq=r["seq"]) for r in rows],
            qualification="history_only" if command["status"] == "history" else "current")
        data = receipt.model_dump()
        data["applied_revision"] = next((r["applied_revision"] for r in rows if r["applied_revision"]),None)
        data["payload_sha256"] = next((r["body_sha256"] for r in rows if r["operation_id"]),None)
        data['retry_policy']='read_only' if command['status'] in ('accepted','started','unknown') else 'explicit_new_key_after_confirmed_failure' if command['status'] in ('failed','not_sent') else 'none'
        if command['status'] in ('accepted','started','unknown'): data['qualification']='unconfirmed'
        if command['action'] not in ('plan','exercise','evaluate','calculate'):
            data.update(model_called=False,tool_called=False)
        return TeachingCommandReceipt(**data)

    # --- T-local：O01/03/05/06/09/11 及未启动 O10 ---

    async def apply_teaching_local(self, activity_id: str, command: TeachingCommandInput) -> TeachingCommandReceipt:
        activity_id = self._uuid(activity_id, "activity_id")
        request_body = canonical(command.canonical_request_body(activity_id))
        if len(request_body.encode("utf-8")) > 32768:
            raise TeachingRefusal("input_too_large", "命令正文超过上限")
        request_sha = sha(request_body)

        async def operation(connection) -> TeachingCommandReceipt:
            locked = await self._teaching_lock_command(connection, activity_id, command.business_key,
                original_record_id=command.body.get('exercise_record_id') if command.action == 'expose' else None)
            activity, head, existing = locked.activity, locked.head, locked.command
            if not activity.get('_memory_eligible',True) and command.action not in ('goal','answer','correct','abandon'):
                raise TeachingRefusal('memory_dependency_invalid','所选学习背景已更新或撤销')
            if existing is not None:
                if self._teaching_replay(existing, request_sha, request_body):
                    head_revision = 0 if head is None else head["revision"]
                    return await self._teaching_original_receipt(connection, activity_id, existing, head_revision)
                raise TeachingRefusal("command_key_conflict", "同键已绑定不同内容，保留原意图；如需修改请用新键")
            cursor = await connection.execute("SELECT * FROM teaching_commands WHERE activity_id=%s AND action=%s "
                "AND request_sha256=%s AND request_body=%s AND status IN ('committed','history','accepted','started','unknown') ORDER BY created_at LIMIT 1",
                (activity_id,command.action,request_sha,request_body))
            same = await cursor.fetchone()
            if same:
                original = await self._teaching_original_receipt(connection,activity_id,same,0 if head is None else head["revision"])
                return TeachingCommandReceipt(**(original.model_dump() | {"business_key":command.business_key,"duplicate_of":str(same["business_key"])}))
            self._teaching_cas(head, command.expected_revision, command.expected_goal_version,
                               command.expected_scope_revision, activity, command.action)
            self._teaching_gate(activity)
            if command.action not in ("goal", "answer", "correct", "abandon") and not activity["_teaching_sources_valid"]:
                raise TeachingRefusal("source_invalid", "资料失效，派生动作不可用")
            # 语义槽竞争（锁内查胜者）。
            slot = semantic_slot(activity_id, command, self._teaching_anchors(head, command))
            winner = await self._teaching_slot_winner(connection, activity_id, command.action, slot)
            duplicate_of = None
            if winner is not None:
                raise TeachingRefusal("unknown_slot" if winner.get("status") == "unknown" else "stage_conflict", "同父槽已有命令，保留双方输入")
            counts = await self._teaching_counts(connection, activity_id)
            if counts["commands"] >= MAX_COMMANDS_PER_ACTIVITY:
                raise TeachingRefusal("history_limit", "命令数已达上限，请新建活动")
            now = datetime.now(timezone.utc)
            await connection.execute(
                """INSERT INTO teaching_commands(activity_id,business_key,action,request_sha256,
                       request_body,slot_sha256,expected_revision,goal_version,scope_revision,status,created_at,updated_at)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,'committed',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)""",
                (activity_id, command.business_key, command.action, request_sha, request_body, slot,
                 command.expected_revision, command.expected_goal_version, command.expected_scope_revision))
            if duplicate_of is not None:
                head_revision = 0 if head is None else head["revision"]
                return TeachingCommandReceipt(
                    activity_id=activity_id, business_key=command.business_key, action=command.action,
                    request_sha256=request_sha, status="committed", duplicate_of=duplicate_of,
                    record_ids=[], operation_id=None, head_revision_now=head_revision,
                    qualification="current")
            if head is not None and command.action not in ('answer','expose'):
                validate_transition(command.action,head['phase'])
            records, revision = await self._teaching_apply_local_effects(
                connection, activity_id, head, activity, command, request_body, request_sha)
            if records:
                await connection.execute("UPDATE teaching_commands SET result_record_id=%s WHERE activity_id=%s AND business_key=%s",
                    (records[0].record_id,activity_id,command.business_key))
            stored=await self._teaching_read_command_row(connection,activity_id,command.business_key)
            receipt=await self._teaching_original_receipt(connection,activity_id,stored,revision)
            if command.action=='expose':
                exercise=await self._teaching_read_record_row(connection,activity_id,command.body['exercise_record_id'])
                result=await self._teaching_fact_result(connection,activity_id,exercise)
                part=command.body['part']
                exposed={'part':part,'exercise_record_id':command.body['exercise_record_id']}
                if part=='hint': exposed['hint']=result.get('hint')
                else: exposed.update(reference_points=result.get('reference_points'),reference_explanation=result.get('reference_explanation'))
                return TeachingCommandReceipt(**(receipt.model_dump()|{'exposed_part':exposed}))
            return receipt

        return await self._transaction(operation)

    def _teaching_anchors(self, head, command: TeachingCommandInput) -> dict:
        """服务端组包语义槽锚点：ID 一律转文本，None 保持 None。

        psycopg 的 UUID 列返回 UUID 对象，直接进 canonical 会抛
        Object of type UUID is not JSON serializable；语义槽必须只由
        可序列化的身份文本参与，故在服务端边界归一。
        """
        anchors: dict = {}
        if head is not None and head.get("goal_record_id") is not None:
            anchors["goal_record_id"] = str(head["goal_record_id"])
            anchors["reason_record_id"] = str(head.get("reason_record_id") or "")
            anchors["diagnostic_anchor"] = str(head.get("reason_record_id") or "")
        return anchors

    async def _teaching_validate_seed(self, connection, activity_id, activity, body):
        seed = body.get('seed_operation_id')
        if seed is None:
            return []
        if not activity['_teaching_sources_valid']:
            raise TeachingRefusal('source_invalid', 'G7来源已失效，不能沿用该成果')
        cursor = await connection.execute("""SELECT o.kind,o.disposition,o.admission_id AS op_admission,
                o.execution_generation AS op_generation,o.scope_revision AS op_scope,r.*
            FROM activity_operations o JOIN activity_operation_results r
                ON r.activity_id=o.activity_id AND r.operation_id=o.operation_id
            WHERE o.activity_id=%s AND o.operation_id=%s""", (activity_id, seed))
        row = await cursor.fetchone()
        if (row is None or row['kind'] != 'model' or row['disposition'] != 'received'
                or row['admission_id'] != row['op_admission'] or row['execution_generation'] != row['op_generation']
                or row['scope_revision'] != row['op_scope'] or row['scope_revision'] != activity['scope_revision']
                or row['payload_sha256'] != body['seed_payload_sha256']):
            raise TeachingRefusal('version_conflict', 'G7成果身份或当前资格不符，未沿用目标')
        try:
            from app.capabilities.contracts import validate_business_payload
            from app.learning.contracts import read_document
            validate_business_payload(row['payload'], row['payload_format'], row['payload_sha256'])
            profile, _ = read_document(json.loads(row['payload'])['value'], activity_id=activity_id, operation_id=seed)
            if (profile.scope_revision != activity['scope_revision'] or profile.goal != body['goal']
                    or self._scope_key([s.model_dump() for s in profile.sources]) != self._scope_key(activity['_teaching_sources'])):
                raise ValueError('seed_identity')
        except (ValueError, TypeError, KeyError):
            raise TeachingRefusal('version_conflict', 'G7目标、类型或范围身份不符') from None
        cursor = await connection.execute('SELECT source_id::text,id::text AS version_id,sha256 FROM material_versions WHERE id=ANY(%s::uuid[])',
            ([s.version_id for s in profile.sources],))
        hashes = {(s['source_id'],s['version_id']):s['sha256'] for s in await cursor.fetchall()}
        if any(hashes.get((e.source_id,e.version_id)) != e.original_sha256 for e in profile.catalog):
            raise TeachingRefusal('source_invalid', 'G7原资料hash不符')
        return [dict(source_id=e.source_id,version_id=e.version_id,source_revision=e.source_revision,
                     original_sha256=e.original_sha256) for e in profile.catalog]

    async def _teaching_apply_local_effects(self, connection, activity_id, head, activity,
                                             command: TeachingCommandInput, request_body, request_sha):
        """T-local 各 action 的 records+head 原子效果；返回 (record_refs, new_revision)。"""
        action, body = command.action, command.body
        seq_base = 0 if head is None else head["last_seq"]
        revision = 0 if head is None else head["revision"]
        goal_version = 0 if head is None else head["goal_version"]
        scope_revision = activity["scope_revision"]
        records: list[RecordRef] = []

        def next_seq() -> int:
            nonlocal seq_base
            seq_base += 1
            if seq_base > MAX_RECORDS:
                raise TeachingRefusal("history_limit", "教学记录数已达上限，请新建活动")
            return seq_base

        def bump_revision() -> int:
            nonlocal revision
            revision += 1
            return revision

        if action == "goal":
            seed_sources = await self._teaching_validate_seed(connection, activity_id, activity, body)
            if goal_version >= MAX_GOAL_VERSION:
                raise TeachingRefusal("history_limit", "目标版本已达上限")
            new_version = goal_version + 1
            goal_record = str(uuid4())
            goal_body = canonical({"goal": body["goal"], "self_report": body.get("self_report"),
                                   "domain": body.get("domain"), "seed_operation_id": body.get('seed_operation_id'),
                                   "seed_payload_sha256": body.get('seed_payload_sha256')})
            if head is not None:
                previous = await self._teaching_read_record_row(connection, activity_id, head["goal_record_id"])
                if previous is not None and previous["body"] == goal_body:
                    return records, revision
            if len(goal_body.encode("utf-8")) > MAX_RECORD_BODY_BYTES:
                raise TeachingRefusal("input_too_large", "目标正文超过上限")
            # DEF-003：同一事务内先定最终效果与唯一 state_after，再 INSERT 最终
            # 记录；records 在本事务内不发生第二次写（不可变触发器保护）。
            goal_seq = next_seq()
            # 旧目标在途命令 obsolete、清下游引用与 pending。
            await self._teaching_obsolete_pending(connection, activity_id)
            new_revision = bump_revision()
            state = _state_after(new_revision, {
                "goal_version": new_version, "phase": "needs_plan", "goal_record_id": goal_record,
                "path_record_id": None, "node_id": None, "exercise_record_id": None,
                "answer_record_id": None, "feedback_record_id": None, "reason_record_id": None})
            await self._teaching_insert_record(
                connection, activity_id, goal_record, goal_seq, "goal", command.business_key, 1,
                new_version, scope_revision, goal_body, sha(goal_body),
                applied_revision=new_revision, state_after=state, source_refs=canonical(seed_sources))
            if head is None:
                await self._teaching_create_head(connection, activity_id, new_revision, new_version,
                                                 "needs_plan", goal_record, seq_base)
            else:
                await self._teaching_update_head(
                    connection, activity_id, head, new_revision, phase="needs_plan",
                    goal_version=new_version, goal_record_id=goal_record,
                    path_record_id=_HEAD_CLEAR, node_id=_HEAD_CLEAR, exercise_record_id=_HEAD_CLEAR,
                    answer_record_id=_HEAD_CLEAR, feedback_record_id=_HEAD_CLEAR, reason_record_id=_HEAD_CLEAR,
                    projection={}, pending_business_key=None, last_seq=seq_base)
            records.append(RecordRef(record_id=goal_record, kind="goal", seq=goal_seq))
            return records, new_revision

        if action == "accept_path":
            if (await self._teaching_counts(connection, activity_id))["paths"] >= MAX_PATHS:
                raise TeachingRefusal("history_limit", "已接受路径数已达32条，请新建活动")
            proposal = await self._teaching_read_record_row(connection, activity_id, body["proposal_record_id"])
            if proposal is None or proposal["kind"] != "path_proposal":
                raise TeachingRefusal("record_not_found", "路径提案不存在")
            self._teaching_gate(activity)
            validate_transition(action, head["phase"])
            if (proposal["goal_version"] != goal_version or proposal["scope_revision"] != scope_revision
                    or head["pending_business_key"] is not None
                    or str(_decode(head['projection']).get('pending_proposal_record_id'))!=body['proposal_record_id']):
                raise TeachingRefusal("version_conflict", "提案不属于当前教学版本")
            proposed = await self._teaching_fact_result(connection, activity_id, proposal)
            if proposed.get("result_type") != "path":
                raise TeachingRefusal("stage_conflict", "该提案未形成可用路径")
            node_ids = validate_path(proposed["nodes"])
            nodes = [dict(n, node_id=nid) for n,nid in zip(proposed["nodes"],node_ids)]
            path_record = str(uuid4())
            path_body = canonical({"proposal_record_id": body["proposal_record_id"],
                                   "nodes": nodes})
            first_node = "n1"
            projection = {"pending_proposal_record_id": None,
                          "nodes": {nid:{"status":"not_started","independent_answers":[],"observations":{}} for nid in node_ids}}
            path_seq = next_seq()
            new_revision = bump_revision()
            state = _state_after(new_revision, {
                "goal_version": goal_version, "phase": "ready", "goal_record_id": head["goal_record_id"],
                "path_record_id": path_record, "node_id": first_node, "exercise_record_id": None,
                "answer_record_id": None, "feedback_record_id": None, "reason_record_id": path_record,
                "projection": projection})
            # DEF-003：INSERT 即最终事实；exercise/answer/feedback 指针由
            # _teaching_clear_exercise_pointers 清空，不经 head UPDATE 传哨兵。
            await self._teaching_insert_record(
                connection, activity_id, path_record, path_seq, "path_accept", command.business_key, 1,
                goal_version, scope_revision, path_body, sha(path_body),
                goal_record_id=head["goal_record_id"],
                parent_record_id=body["proposal_record_id"], source_refs=proposal["source_refs"],
                applied_revision=new_revision, state_after=state)
            await self._teaching_update_head(
                connection, activity_id, head, new_revision, phase="ready", path_record_id=path_record,
                node_id=first_node, reason_record_id=path_record, projection=projection,
                pending_business_key=None, last_seq=seq_base)
            await self._teaching_clear_exercise_pointers(connection, activity_id)
            records.append(RecordRef(record_id=path_record, kind="path_accept", seq=path_seq))
            return records, new_revision

        if action == "expose":
            exercise = await self._teaching_read_record_row(connection, activity_id, body["exercise_record_id"])
            if exercise is None or exercise["kind"] != "exercise":
                raise TeachingRefusal("record_not_found", "练习不存在")
            from app.learning.teaching_views import record_sources_valid, bound_references
            refs = bound_references(exercise)
            cursor = await connection.execute("""SELECT v.source_id::text,v.id::text AS version_id,
                    m.revision AS source_revision,v.sha256,
                    COALESCE(m.current_version=v.id,false) AS valid,
                    CASE WHEN v.format IN ('txt','md') THEN true WHEN v.format='pdf' THEN EXISTS (
                        SELECT 1 FROM pdf_review_candidates c WHERE c.version_id=v.id AND c.status='confirmed'
                        AND c.page_count BETWEEN 1 AND 50
                        AND (SELECT count(*) FROM pdf_review_pages p WHERE p.candidate_id=c.id)=c.page_count
                        AND (SELECT count(*) FROM pdf_extracted_pages p WHERE p.version_id=v.id)=c.page_count)
                        ELSE false END AS ready
                FROM material_versions v LEFT JOIN material_sources m ON m.id=v.source_id
                WHERE v.id=ANY(%s::uuid[])""", ([r['version_id'] for r in refs or []],))
            if not record_sources_valid(exercise, await cursor.fetchall()):
                raise TeachingRefusal('source_invalid', '原练习的资料版本、修订或原文hash已失效')
            await self._teaching_fact_result(connection, activity_id, exercise)
            # 重复 exposure：核对后返回原事实，不新记。
            cursor = await connection.execute(
                """SELECT 1 FROM teaching_records WHERE activity_id=%s AND kind='exposure'
                     AND business_key=%s""", (activity_id, command.business_key))
            if await cursor.fetchone() is not None:
                return records, revision
            exposure_record = str(uuid4())
            exposure_body = canonical({"exercise_record_id": body["exercise_record_id"], "part": body["part"]})
            exposure_seq = next_seq()
            is_current = head is not None and str(head["exercise_record_id"]) == body["exercise_record_id"]
            new_revision = bump_revision() if is_current else revision
            state = _state_after(new_revision, head) if is_current else None
            await self._teaching_insert_record(
                connection, activity_id, exposure_record, exposure_seq, "exposure", command.business_key, 1,
                exercise["goal_version"], exercise["scope_revision"], exposure_body, sha(exposure_body),
                goal_record_id=exercise["goal_record_id"],
                exercise_record_id=body["exercise_record_id"], source_refs=exercise["source_refs"],
                applied_revision=new_revision if is_current else None, state_after=state)
            if is_current:
                await self._teaching_update_head(connection, activity_id, head, new_revision, last_seq=seq_base)
            else:
                new_revision = revision
                await connection.execute(
                    "UPDATE teaching_heads SET last_seq=%s WHERE activity_id=%s", (seq_base, activity_id))
            records.append(RecordRef(record_id=exposure_record, kind="exposure", seq=seq_base))
            return records, new_revision

        if action == "answer":
            counts = await self._teaching_counts(connection, activity_id)
            if counts["answers"] >= MAX_ANSWERS:
                raise TeachingRefusal("history_limit", "作答数已达上限")
            exercise = await self._teaching_read_record_row(connection, activity_id, body["exercise_record_id"])
            if exercise is None or exercise["kind"] != "exercise":
                raise TeachingRefusal("record_not_found", "练习不存在")
            kind = body["kind"]
            supersedes = body.get("supersedes_answer_record_id")
            if kind == "initial":
                cursor = await connection.execute(
                    """SELECT 1 FROM teaching_records WHERE activity_id=%s AND kind='answer'
                         AND exercise_record_id=%s AND supersedes_record_id IS NULL""",
                    (activity_id, body["exercise_record_id"]))
                if await cursor.fetchone() is not None:
                    raise TeachingRefusal("stage_conflict", "本题首答已存在；续答请用 continuation/revision")
            if supersedes is not None:
                cursor = await connection.execute(
                    """SELECT exercise_record_id FROM teaching_records
                        WHERE activity_id=%s AND record_id=%s AND kind='answer'""",
                    (activity_id, supersedes))
                row = await cursor.fetchone()
                if row is None or str(row["exercise_record_id"]) != body["exercise_record_id"]:
                    raise TeachingRefusal("stage_conflict", "supersedes 必须指当前本题答案链末端")
                cursor = await connection.execute(
                    """SELECT count(*) FROM teaching_records
                        WHERE activity_id=%s AND supersedes_record_id=%s""",
                    (activity_id, supersedes))
                if (await cursor.fetchone())["count"] > 0:
                    raise TeachingRefusal("stage_conflict", "修正链不可分叉")
            answer_record = str(uuid4())
            exposure_state = await self._teaching_exercise_exposures(connection, activity_id, body["exercise_record_id"])
            answer_body = canonical({
                "exercise_record_id": body["exercise_record_id"], "kind": kind, "text": body["text"],
                "supersedes_answer_record_id": supersedes, "exposures_seen": sorted(exposure_state)})
            if len(answer_body.encode("utf-8")) > MAX_RECORD_BODY_BYTES:
                raise TeachingRefusal("input_too_large", "作答正文超过上限")
            answer_seq = next_seq()
            current = (str(head["exercise_record_id"]) == body["exercise_record_id"]
                       and exercise["goal_version"] == goal_version and exercise["scope_revision"] == scope_revision
                       and activity["_teaching_sources_valid"])
            if current and supersedes and str(head["answer_record_id"]) != supersedes:
                raise TeachingRefusal("answer_changed", "supersedes 不是当前答案")
            if current:
                await self._teaching_obsolete_pending(connection, activity_id)
            new_revision = bump_revision() if current else revision
            state = _state_after(new_revision, {
                "goal_version": goal_version, "phase": "answer_saved", "goal_record_id": head["goal_record_id"],
                "path_record_id": head["path_record_id"], "node_id": head["node_id"],
                "exercise_record_id": body["exercise_record_id"], "answer_record_id": answer_record,
                "feedback_record_id": None, "reason_record_id": head["reason_record_id"],
                "projection": head["projection"]}) if current else None
            # DEF-003：作答事实一次成型，无事后回填。
            await self._teaching_insert_record(
                connection, activity_id, answer_record, answer_seq, "answer", command.business_key, 1,
                exercise["goal_version"], exercise["scope_revision"], answer_body, sha(answer_body),
                goal_record_id=exercise["goal_record_id"],
                exercise_record_id=body["exercise_record_id"], supersedes_record_id=supersedes,
                source_refs=exercise["source_refs"], applied_revision=new_revision if current else None, state_after=state)
            if current:
                await self._teaching_update_head(
                    connection, activity_id, head, new_revision, phase="answer_saved", feedback_record_id=_HEAD_CLEAR,
                    answer_record_id=answer_record, pending_business_key=None, last_seq=seq_base)
            else:
                await connection.execute("UPDATE teaching_heads SET last_seq=%s WHERE activity_id=%s",(seq_base,activity_id))
                await connection.execute("UPDATE teaching_commands SET status='history' WHERE activity_id=%s AND business_key=%s",
                    (activity_id,command.business_key))
            records.append(RecordRef(record_id=answer_record, kind="answer", seq=answer_seq))
            return records, new_revision

        if action == "correct":
            counts = await self._teaching_counts(connection, activity_id)
            if counts["corrections"] >= MAX_CORRECTIONS:
                raise TeachingRefusal("history_limit", "纠错数已达上限")
            target = await self._teaching_read_record_row(connection, activity_id, body["target_record_id"])
            if target is None or target["kind"] not in ("path_proposal", "path_accept", "feedback", "progress"):
                raise TeachingRefusal("record_not_found", "纠错目标不存在或类型不符")
            correction_record = str(uuid4())
            correction_body = canonical({"target_record_id": body["target_record_id"],
                                         "text": body["text"],
                                         "disputed_dimensions": body["disputed_dimensions"]})
            current = (target["goal_version"] == goal_version and target["scope_revision"] == scope_revision
                       and activity["_teaching_sources_valid"])
            if current and target['kind'] in ('feedback','progress'):
                feedback=target if target['kind']=='feedback' else await self._teaching_read_record_row(connection,activity_id,target['parent_record_id'])
                bound=await self._teaching_read_command_row(connection,activity_id,str(feedback['business_key'])) if feedback else None
                refs=_decode(bound['context_body']).get('reference_hashes',[]) if bound else []
                current=any(r['record_id']==str(head['path_record_id']) for r in refs)
            elif current and target['kind'] in ('path_proposal','path_accept'):
                path=await self._teaching_read_record_row(connection,activity_id,head['path_record_id']) if head['path_record_id'] else None
                accepted_proposal=str(path['parent_record_id']) if path else None
                current=str(target['record_id']) in {str(head['path_record_id']),str(_decode(head['projection']).get('pending_proposal_record_id')),accepted_proposal}
            final_head = dict(head)
            projection = _decode(head["projection"])
            target_parent = str(target["parent_record_id"]) if target["kind"] == "progress" else str(target["record_id"])
            if current and head["path_record_id"] is not None and target["kind"] in ("feedback","progress"):
                projection,nodes = await self._teaching_rebuild_progress(connection,activity_id,head,
                    {"record_id":correction_record,"kind":"correction","body":correction_body,
                     "body_sha256":sha(correction_body),"operation_id":None,"parent_record_id":target_parent})
                invalid = next((nid for nid,n in projection["nodes"].items() if n["status"] == "needs_repair"),None)
                if invalid and invalid != head["node_id"]:
                    final_head.update(node_id=invalid,exercise_record_id=None,answer_record_id=None,feedback_record_id=None,phase="ready")
            new_revision = bump_revision() if current else revision
            final_head.update(reason_record_id=correction_record,projection=projection)
            correction_seq = next_seq()
            await self._teaching_insert_record(
                connection, activity_id, correction_record, correction_seq, "correction", command.business_key, 1,
                target["goal_version"], target["scope_revision"], correction_body, sha(correction_body),
                goal_record_id=target["goal_record_id"], parent_record_id=body["target_record_id"],
                exercise_record_id=target["exercise_record_id"],answer_record_id=target["answer_record_id"],source_refs=target["source_refs"],
                applied_revision=new_revision if current else None,state_after=_state_after(new_revision,final_head) if current else None)
            if current:
                await self._teaching_obsolete_pending(connection,activity_id)
                await self._teaching_update_head(connection,activity_id,head,new_revision,last_seq=seq_base,
                    phase=final_head["phase"],node_id=final_head["node_id"],reason_record_id=correction_record,projection=projection,
                    exercise_record_id=final_head["exercise_record_id"] or _HEAD_CLEAR,
                    answer_record_id=final_head["answer_record_id"] or _HEAD_CLEAR,
                    feedback_record_id=final_head["feedback_record_id"] or _HEAD_CLEAR,pending_business_key=None)
            else:
                await connection.execute("UPDATE teaching_heads SET last_seq=%s WHERE activity_id=%s",(seq_base,activity_id))
                await connection.execute("UPDATE teaching_commands SET status='history' WHERE activity_id=%s AND business_key=%s",(activity_id,command.business_key))
            records.append(RecordRef(record_id=correction_record, kind="correction", seq=seq_base))
            return records, new_revision

        if action == "abandon":
            target_key = body["target_business_key"]
            cursor = await connection.execute(
                "SELECT * FROM teaching_commands WHERE activity_id=%s AND business_key=%s FOR UPDATE",
                (activity_id, target_key))
            target = await cursor.fetchone()
            if target is None:
                raise TeachingRefusal("record_not_found", "目标命令不存在")
            if target["launch_claimed_at"] is None and target["status"] in ("accepted",):
                await connection.execute(
                    """UPDATE teaching_commands SET status='abandoned', abandoned_at=CURRENT_TIMESTAMP,
                           updated_at=CURRENT_TIMESTAMP WHERE activity_id=%s AND business_key=%s""",
                    (activity_id, target_key))
                if head is not None and head["pending_business_key"] is not None \
                        and str(head["pending_business_key"]) == target_key:
                    await self._teaching_update_head(connection, activity_id, head, revision,
                                                     pending_business_key=None)
            else:
                await connection.execute(
                    """UPDATE teaching_commands SET abandoned_at=CURRENT_TIMESTAMP, updated_at=CURRENT_TIMESTAMP
                        WHERE activity_id=%s AND business_key=%s""",
                    (activity_id, target_key))
                if head is not None and str(head.get("pending_business_key") or "") == target_key:
                    await self._teaching_update_head(connection,activity_id,head,revision,pending_business_key=None)
            return records, revision

        if action == "select_node":
            if head is None or head["path_record_id"] is None:
                raise TeachingRefusal("stage_conflict", "尚无已接受路径")
            if str(head["path_record_id"]) != body["path_record_id"] or head["pending_business_key"] is not None or activity["status"] == "running":
                raise TeachingRefusal("stage_conflict", "路径已改变或执行窗口尚未收尾")
            if head["exercise_record_id"] is not None and not body["archive_current"]:
                raise TeachingRefusal("stage_conflict", "先确认把当前未处理练习保留为历史")
            path = await self._teaching_read_record_row(connection,activity_id,head["path_record_id"])
            nodes = (await self._teaching_fact_result(connection,activity_id,path))["nodes"]
            projection = _decode(head["projection"])
            node = next((n for n in nodes if n["node_id"] == body["node_id"]),None)
            if node is None or any(projection.get("nodes",{}).get(f"n{p+1}",{}).get("status") != "evidence_sufficient" for p in node["prerequisites"]):
                raise TeachingRefusal("stage_conflict", "节点前置尚无足够证据")
            selection_record = str(uuid4())
            selection_body = canonical({"path_record_id": body["path_record_id"],
                                        "node_id": body["node_id"], "archive_current": body["archive_current"]})
            selection_seq = next_seq()
            new_revision = bump_revision()
            state = _state_after(new_revision, {
                "goal_version": goal_version, "phase": "ready", "goal_record_id": head["goal_record_id"],
                "path_record_id": body["path_record_id"], "node_id": body["node_id"],
                "exercise_record_id": None, "answer_record_id": None, "feedback_record_id": None,
                "reason_record_id": selection_record,"projection":projection})
            # DEF-003：节点选择事实一次成型。
            await self._teaching_insert_record(
                connection, activity_id, selection_record, selection_seq, "node_selection",
                command.business_key, 1, goal_version, scope_revision, selection_body,
                sha(selection_body), goal_record_id=head["goal_record_id"],source_refs=path["source_refs"],
                applied_revision=new_revision, state_after=state)
            await self._teaching_update_head(connection, activity_id, head, new_revision, phase="ready",
                                             path_record_id=body["path_record_id"],node_id=body["node_id"],reason_record_id=selection_record,
                                             pending_business_key=None, last_seq=seq_base)
            await self._teaching_clear_exercise_pointers(connection, activity_id)
            records.append(RecordRef(record_id=selection_record, kind="node_selection", seq=selection_seq))
            return records, new_revision

        raise TeachingRefusal("invalid_input", "该动作不属于本地事务")

    async def _teaching_clear_exercise_pointers(self, connection, activity_id) -> None:
        await connection.execute(
            """UPDATE teaching_heads SET exercise_record_id=NULL, answer_record_id=NULL,
                   feedback_record_id=NULL, updated_at=CURRENT_TIMESTAMP WHERE activity_id=%s""",
            (activity_id,))

    async def _teaching_exercise_exposures(self, connection, activity_id, exercise_record_id) -> set[str]:
        cursor = await connection.execute(
            "SELECT body,body_sha256 FROM teaching_records WHERE activity_id=%s AND kind='exposure' AND exercise_record_id=%s ORDER BY seq",
            (activity_id, exercise_record_id))
        parts = set()
        for row in await cursor.fetchall():
            try:
                if sha(row['body'])!=row['body_sha256']: raise TeachingRefusal('integrity_error','暴露记录损坏')
                parts.add(json.loads(row["body"])["part"])
            except (ValueError, TypeError, KeyError):
                continue
        return parts

    async def _teaching_read_record_row(self, connection, activity_id, record_id):
        cursor = await connection.execute(
            "SELECT * FROM teaching_records WHERE activity_id=%s AND record_id=%s",
            (activity_id, record_id))
        return await cursor.fetchone()

    # --- T-intent / T-launch / 监督收尾 ---

    async def accept_teaching_command(self, activity_id: str, command: TeachingCommandInput,
                                      frozen: TeachingFrozenContext) -> TeachingCommandReceipt:
        activity_id = self._uuid(activity_id, "activity_id")
        request_body = canonical(command.canonical_request_body(activity_id))
        request_sha = sha(request_body)
        context_body = canonical(frozen.model_dump(by_alias=True))
        if len(context_body.encode("utf-8")) > 49152:
            raise TeachingRefusal("context_limit", "冻结上下文超过上限")

        async def operation(connection) -> TeachingCommandReceipt:
            locked = await self._teaching_lock_command(connection, activity_id, command.business_key)
            activity, head, existing = locked.activity, locked.head, locked.command
            if activity.get('_memory_selected'):
                if not activity.get('_memory_eligible'):
                    raise TeachingRefusal('memory_dependency_invalid','所选学习背景已更新或撤销')
                if frozen.kind=='model' and not isinstance(frozen,TeachingMemoryFrozenContext):
                    raise TeachingRefusal('memory_profile_required','本活动须使用明确学习背景协议')
            elif isinstance(frozen,TeachingMemoryFrozenContext):
                raise TeachingRefusal('memory_profile_required','本活动未明确选用背景')

            if existing is not None:
                if self._teaching_replay(existing, request_sha, request_body):
                    return await self._teaching_original_receipt(connection,activity_id,existing,0 if head is None else head["revision"])
                raise TeachingRefusal("command_key_conflict", "同键已绑定不同内容")
            cursor=await connection.execute("SELECT * FROM teaching_commands WHERE activity_id=%s AND action=%s AND request_sha256=%s AND request_body=%s AND status IN ('accepted','started','unknown','committed','history') ORDER BY created_at LIMIT 1",(activity_id,command.action,request_sha,request_body))
            same=await cursor.fetchone()
            if same:
                original=await self._teaching_original_receipt(connection,activity_id,same,0 if head is None else head['revision'])
                return TeachingCommandReceipt(**(original.model_dump()|{'business_key':command.business_key,'duplicate_of':str(same['business_key'])}))
            if head is None:
                raise TeachingRefusal("version_conflict", "教学尚未初始化，先保存目标")
            self._teaching_cas(head, command.expected_revision, command.expected_goal_version,
                               command.expected_scope_revision, activity, command.action)
            self._teaching_gate(activity)
            self._teaching_budget(activity,frozen)
            if not activity["_teaching_sources_valid"]:
                raise TeachingRefusal("source_invalid", "资料已失效")
            if activity["status"] == "running":
                raise TeachingRefusal("stage_conflict", "当前执行窗口尚未收尾")
            if head["pending_business_key"] is not None and str(head["pending_business_key"]) != command.business_key:
                raise TeachingRefusal("stage_conflict", "已有在途命令，等待其收尾")
            # DEF-004：锁内核对冻结上下文引用的持久事实身份。组包在锁前，
            # 接受必须在锁内逐项确认引用仍在位且 body_sha256 与冻结值一致；
            # 任一漂移即拒（不能用旧组包绑定新版本实体）。
            for reference in frozen.reference_hashes:
                row = await self._teaching_read_record_row(connection, activity_id, reference.record_id)
                if row is None or row["body_sha256"] != reference.body_sha256:
                    raise TeachingRefusal("version_conflict",
                                          "冻结上下文引用的教学事实已变化，请刷新后重试")
            if head["goal_record_id"] is None:
                raise TeachingRefusal("version_conflict", "教学尚未初始化，先保存目标")
            slot = semantic_slot(activity_id, command, self._teaching_anchors(head, command))
            winner = await self._teaching_slot_winner(connection, activity_id, command.action, slot)
            duplicate_of = None
            if winner is not None:
                if winner["request_body"] == request_body:
                    original = await self._teaching_original_receipt(connection,activity_id,winner,head["revision"])
                    return TeachingCommandReceipt(**(original.model_dump() | {"business_key":command.business_key,"duplicate_of":str(winner["business_key"])}))
                else:
                    raise TeachingRefusal("unknown_slot" if winner["status"] == "unknown" else "stage_conflict", "同父槽已有不同内容")
            retry = command.body.get("retry_of")
            if retry:
                previous = await self._teaching_read_command_row(connection,activity_id,retry)
                if previous is None or previous["status"] not in ("failed","not_sent") or previous["action"] != command.action or previous["slot_sha256"] != slot:
                    raise TeachingRefusal("unknown_slot", "只能显式重试确定失败的同父命令")
            counts = await self._teaching_counts(connection, activity_id)
            if counts["commands"] >= MAX_COMMANDS_PER_ACTIVITY:
                raise TeachingRefusal("history_limit", "命令数已达上限")
            operation_id = command.operation_id(activity_id)
            await connection.execute(
                """INSERT INTO teaching_commands(activity_id,business_key,action,request_sha256,request_body,
                       slot_sha256,expected_revision,goal_version,scope_revision,parent_record_id,
                       context_body,context_sha256,operation_id,retry_of,status,created_at,updated_at)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'accepted',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)""",
                (activity_id, command.business_key, command.action, request_sha, request_body, slot,
                 command.expected_revision, command.expected_goal_version, command.expected_scope_revision,
                 command.body.get("answer_record_id") or command.body.get("parent_feedback_record_id") or head["goal_record_id"],
                 context_body, frozen.context_sha256, operation_id, retry))
            await self._teaching_update_head(connection, activity_id, head, head["revision"],
                                             pending_business_key=command.business_key)
            candidate = {"business_key":command.business_key,"expected_revision":command.expected_revision,
                         "goal_version":command.expected_goal_version,"scope_revision":command.expected_scope_revision,
                         "operation_id":operation_id,"request_body":request_body,"request_sha256":request_sha,"action":command.action}
            current_head = dict(head,pending_business_key=command.business_key)
            await self._teaching_verify_current(connection,activity,current_head,candidate,frozen)
            return _row_receipt(
                {"activity_id": activity_id, "business_key": command.business_key, "action": command.action,
                 "request_sha256": request_sha, "status": "accepted", "operation_id": operation_id,
                 "error_code": None},
                head["revision"], duplicate_of=duplicate_of)

        return await self._transaction(operation)

    async def claim_teaching_launch(self, activity_id: str, business_key: str,
                                    request_sha256: str) -> dict:
        activity_id = self._uuid(activity_id, "activity_id")
        business_key = self._uuid(business_key, "business_key")

        async def operation(connection) -> dict:
            locked = await self._teaching_lock_command(connection, activity_id, business_key)
            activity, head, command = locked.activity, locked.head, locked.command
            if command is None:
                raise TeachingRefusal("record_not_found", "命令不存在")
            if command["request_sha256"] != request_sha256:
                raise TeachingRefusal("command_key_conflict", "请求摘要不匹配")
            if command["obsolete_at"] is not None or command["abandoned_at"] is not None:
                return {"launch_allowed": False, "reason": "command_obsolete"}
            if command["status"] == "started":
                return {"launch_allowed": False, "reason": "already_claimed"}
            if command["status"] != "accepted":
                return {"launch_allowed": False, "reason": f"status_{command['status']}"}
            if command["launch_claimed_at"] is not None:
                return {"launch_allowed": False, "reason": "already_claimed"}
            # DEF-004：T-launch 锁内复核当前绑定。接受与 claim 之间教学
            # 状态可能变化（新目标/新答案会清 pending 并 obsolete 本命令）；
            # 仅当本命令仍是 head 当前 pending 时才可领取唯一启动收据。
            if head is None or str(head["pending_business_key"] or "") != str(business_key):
                return {"launch_allowed": False, "reason": "no_longer_current_binding"}
            cursor = await connection.execute(
                "SELECT 1 FROM activity_operations WHERE activity_id=%s AND operation_id=%s",
                (activity_id, command["operation_id"]))
            if await cursor.fetchone() is not None:
                return {"launch_allowed": False, "reason": "operation_exists"}
            if (activity["status"] != "pending" or activity["executor_id"] is not None
                    or activity["running_reserved_seconds"] != 0 or not activity["_teaching_sources_valid"]):
                return {"launch_allowed": False, "reason": "activity_not_launchable"}
            self._teaching_gate(activity)
            try:
                frozen = parse_frozen_context(_decode(command["context_body"]))
                self._teaching_budget(activity,frozen)
                await self._teaching_verify_current(connection,activity,head,command,frozen)
            except TeachingRefusal as exc:
                return {"launch_allowed":False,"reason":exc.code}
            except (ValueError,TypeError):
                return {"launch_allowed":False,"reason":"integrity_error"}
            await connection.execute(
                """UPDATE teaching_commands SET status='started', launch_claimed_at=CURRENT_TIMESTAMP,
                       updated_at=CURRENT_TIMESTAMP WHERE activity_id=%s AND business_key=%s""",
                (activity_id, business_key))
            return {"launch_allowed": True, "reason": None, "operation_id": command["operation_id"]}

        return await self._transaction(operation)

    async def finish_teaching_supervision(self, activity_id: str, business_key: str,
                                          supervision) -> TeachingCommandReceipt:
        activity_id = self._uuid(activity_id, "activity_id")
        business_key = self._uuid(business_key, "business_key")

        async def operation(connection) -> TeachingCommandReceipt:
            locked = await self._teaching_lock_command(connection, activity_id, business_key)
            activity, head, command = locked.activity, locked.head, locked.command
            if command is None:
                raise TeachingRefusal("record_not_found", "命令不存在")
            head_revision = 0 if head is None else head["revision"]
            if command["status"] in ("committed", "history", "failed", "not_sent", "unknown", "abandoned"):
                return await self._teaching_original_receipt(connection,activity_id,command,head_revision)
            # DEF-007：以「本次确认后的结局」处理指针，不得读 UPDATE 前的
            # 旧 command.status 判断（旧值恒为 started/accepted，会使失败
            # 收据永远清不掉 pending）。确定未准入 → failed 并清本键
            # pending；其余保守 unknown，pending 占槽保留（UNKNOWN 不解槽）。
            cursor = await connection.execute("SELECT state FROM activity_operations WHERE activity_id=%s AND operation_id=%s",
                (activity_id,command["operation_id"]))
            operation_row = await cursor.fetchone()
            startup_states = ("not_started","budget_exhausted","startup_deadline","partial_window_too_small")
            definitely = (getattr(supervision,"definitely_not_admitted",False) and getattr(supervision,"state",None) in startup_states
                          and not getattr(supervision,"model_receipt",None) and not getattr(supervision,"tool_receipt",None)
                          and operation_row is None)
            final_status = "failed" if definitely else "unknown"
            if final_status == "failed":
                await connection.execute(
                    """UPDATE teaching_commands SET status='failed', error_code='supervision_not_admitted',
                           updated_at=CURRENT_TIMESTAMP WHERE activity_id=%s AND business_key=%s""",
                    (activity_id, business_key))
            else:
                await connection.execute(
                    """UPDATE teaching_commands SET status='unknown', updated_at=CURRENT_TIMESTAMP
                        WHERE activity_id=%s AND business_key=%s""",
                    (activity_id, business_key))
            if final_status == "failed" and head is not None \
                    and head["pending_business_key"] is not None \
                    and str(head["pending_business_key"]) == business_key:
                await self._teaching_update_head(connection, activity_id, head, head["revision"],
                                                 pending_business_key=None)
            cursor = await connection.execute(
                "SELECT * FROM teaching_commands WHERE activity_id=%s AND business_key=%s",
                (activity_id, business_key))
            return await self._teaching_original_receipt(connection,activity_id,await cursor.fetchone(),head_revision)

        return await self._transaction(operation)

    # --- T-admit/T-mark 锁内绑定复核（供 admit/mark/record hook 调用） ---

    async def _locked_teaching_binding(self, connection, activity, operation_id: str,
                                       binding: TeachingCallBinding | None, phase: str) -> dict:
        """admit/mark 锁内教学身份复核；phase 仅 admit/mark/result。"""
        if phase not in ("admit", "mark", "result"):
            raise TeachingRefusal("invalid_input", "教学绑定阶段非法")
        if not operation_id.startswith((TEACHING_PREFIX_MODEL, TEACHING_PREFIX_TOOL)):
            raise TeachingRefusal("invalid_input", "非教学操作")
        digest = operation_id.rpartition(".")[2]
        key = operation_id.split(".")[1]
        if phase=='admit' and operation_id.startswith(TEACHING_PREFIX_MODEL) and binding is None:
            raise TeachingRefusal('profile_required','教学模型准入必须携带受信绑定')
        cursor = await connection.execute("SELECT * FROM teaching_heads WHERE activity_id=%s FOR UPDATE",(str(activity["id"]),))
        head = await cursor.fetchone()
        cursor = await connection.execute(
            "SELECT * FROM teaching_commands WHERE activity_id=%s AND business_key=%s FOR UPDATE",
            (str(activity["id"]), key))
        command = await cursor.fetchone()
        if command is None or command["operation_id"] != operation_id:
            raise TeachingRefusal("unknown_slot", "教学命令未找到或操作键不匹配")
        if command["request_sha256"] != digest:
            raise TeachingRefusal("unknown_slot", "教学请求摘要不匹配")
        if command["status"] != "started" or command["launch_claimed_at"] is None:
            raise TeachingRefusal("launch_already_claimed", "教学命令不在启动状态")
        if command["obsolete_at"] is not None or command["abandoned_at"] is not None:
            raise TeachingRefusal("unknown_slot", "教学命令已废弃")
        if binding is not None:
            if (str(command["business_key"]) != binding.command_key
                    or command["request_sha256"] != binding.request_sha256):
                raise TeachingRefusal("unknown_slot", "教学绑定不匹配")
            if command["context_sha256"] != binding.context_sha256:
                raise TeachingRefusal("unknown_slot", "教学上下文不匹配")
            if command["expected_revision"] != binding.expected_revision or command["goal_version"] != binding.goal_version:
                raise TeachingRefusal("version_conflict", "教学版本不匹配")
        try:
            frozen = parse_frozen_context(_decode(command["context_body"]))
        except (ValueError,TypeError):
            raise TeachingRefusal("integrity_error","冻结上下文不可解析") from None
        if isinstance(frozen,TeachingMemoryFrozenContext) and binding is not None:
            if (getattr(binding,'memory_selection_sha256',None)!=frozen.memory_selection_sha256
                    or getattr(binding,'assembled_messages_sha256',None)!=frozen.assembled_messages_sha256):
                raise TeachingRefusal('memory_profile_required','背景消息受信绑定不符')
        if phase != "result":
            await self._teaching_verify_current(connection,activity,head,command,frozen)
        return command

    # --- T-result：教学事实与原 record 同事务提交 ---

    async def _write_teaching_outcome(self, connection, activity, call, outcome, payload_triple) -> None:
        """原 record 事务内提交最终教学事实；任何缺链均拒绝并回滚原正文。"""
        activity_id, operation_id = str(activity["id"]), call["operation_id"]
        cursor = await connection.execute("SELECT * FROM teaching_heads WHERE activity_id=%s FOR UPDATE",(activity_id,))
        head = await cursor.fetchone()
        command = await self._teaching_read_command_row(connection,activity_id,operation_id.split(".")[1],lock=True)
        if command is None or head is None or command["operation_id"] != operation_id or command["request_sha256"] != operation_id.rpartition(".")[2]:
            raise TeachingRefusal("integrity_error","教学命令或当前投影缺失，原正文提交回滚")
        try:
            frozen = parse_frozen_context(_decode(command["context_body"]))
            request = _decode(command["request_body"])
        except (ValueError,TypeError):
            raise TeachingRefusal("integrity_error","教学命令上下文损坏") from None
        from app.learning.teaching_contracts import frozen_context_digest
        if frozen_context_digest(frozen) != command["context_sha256"] or sha(command["request_body"]) != command["request_sha256"]:
            raise TeachingRefusal("integrity_error","教学命令摘要不一致")
        disposition = outcome.disposition.value
        if payload_triple is None:
            status = {"not_sent":"not_sent","unknown":"unknown"}.get(disposition,"failed")
            await connection.execute("UPDATE teaching_commands SET status=%s,error_code=%s,updated_at=CURRENT_TIMESTAMP WHERE activity_id=%s AND business_key=%s",
                (status,outcome.error_code,activity_id,command["business_key"]))
            if status != "unknown" and str(head["pending_business_key"] or "") == str(command["business_key"]):
                await connection.execute("UPDATE teaching_heads SET pending_business_key=NULL WHERE activity_id=%s",(activity_id,))
            return
        if disposition != "received":
            raise TeachingRefusal("integrity_error","教学正文终态不一致")
        body,action = request["body"],command["action"]
        reference_rows = {}
        for ref in frozen.reference_hashes:
            row = await self._teaching_read_record_row(connection,activity_id,ref.record_id)
            if row is None or row["body_sha256"] != ref.body_sha256:
                raise TeachingRefusal("integrity_error","教学结果父事实缺失")
            reference_rows[ref.record_id] = row
        goal = next((r for r in reference_rows.values() if r["kind"] == "goal"),None)
        if goal is None:
            raise TeachingRefusal("integrity_error","教学结果缺少真实目标")
        value = _decode(payload_triple[1])["value"]
        if action == "calculate":
            if frozen.kind != "tool" or type(value) is not str or call["arguments_sha256"] != frozen.call.arguments_sha256 or call["tool_call_id"] != frozen.call.call_id:
                raise TeachingRefusal("integrity_error","核算身份或正文不一致")
            result = {"result_type":"calculation","value_decimal":value}
            source_refs = reference_rows[body["exercise_record_id"]]["source_refs"]
        else:
            expected = {"profile":frozen.profile_version,"action":action,"activity_id":activity_id,
                "command_key":str(command["business_key"]),"request_sha256":command["request_sha256"],
                "context_sha256":command["context_sha256"],"expected_revision":command["expected_revision"],
                "goal_record_id":str(goal["record_id"]),"goal_version":command["goal_version"],"scope_revision":command["scope_revision"]}
            if frozen.kind != "model" or not isinstance(value,dict) or any(value.get(k) != v for k,v in expected.items()):
                raise TeachingRefusal("integrity_error","教学结果受信身份不一致")
            result = value["result"]
            if value.get("catalog") != [e.model_dump() for e in frozen.catalog]:
                raise TeachingRefusal("integrity_error","教学结果目录不一致")
            source_refs = canonical([{"source_id":e.source_id,"version_id":e.version_id,"source_revision":e.source_revision,"original_sha256":e.original_sha256} for e in frozen.catalog])
        current = self._teaching_result_current(head,command,activity)
        revision,seq = head["revision"],head["last_seq"]
        record_id,key = str(uuid4()),str(command["business_key"])
        kind = {"plan":"path_proposal","exercise":"exercise","evaluate":"feedback","calculate":"calculation"}[action]
        new_revision = revision+1 if current else None
        final_head = dict(head)
        projection = _decode(head["projection"])
        state = None
        normal = result["result_type"] == {"plan":"path","exercise":"exercise","evaluate":"feedback","calculate":"calculation"}[action]
        if current:
            final_head["reason_record_id"] = record_id
            if action == "plan" and normal:
                projection["pending_proposal_record_id"] = record_id
                final_head["phase"] = "path_review"
            elif action == "exercise" and normal:
                final_head.update(phase="exercise_ready",exercise_record_id=record_id,answer_record_id=None,feedback_record_id=None)
            elif action == "evaluate" and normal:
                final_head.update(phase="feedback_ready",feedback_record_id=record_id)
            final_head["projection"] = projection
            if action != "evaluate" or not normal:
                state = _state_after(new_revision,final_head)
        if action == "exercise":
            cursor = await connection.execute("SELECT count(*) AS n FROM teaching_records WHERE activity_id=%s AND kind='exercise'",(activity_id,))
            if (await cursor.fetchone())["n"] >= MAX_EXERCISES:
                raise TeachingRefusal("history_limit","练习数已达上限")
        count = 3 if action == "evaluate" and normal and current else 2 if action == "evaluate" else 1
        if seq+count > MAX_RECORDS:
            raise TeachingRefusal("history_limit","教学记录已达上限")
        seq += 1
        await self._teaching_insert_record(connection,activity_id,record_id,seq,kind,key,1,
            command["goal_version"],command["scope_revision"],None,payload_triple[2],goal_record_id=goal["record_id"],
            operation_id=operation_id,parent_record_id=command["parent_record_id"],
            exercise_record_id=body.get("exercise_record_id"),answer_record_id=body.get("answer_record_id"),
            source_refs=source_refs,applied_revision=new_revision if state else None,state_after=state)
        if action == "evaluate":
            seq += 1
            exposure_body = canonical({"exercise_record_id":body["exercise_record_id"],"part":"reference","with_feedback":record_id})
            await self._teaching_insert_record(connection,activity_id,str(uuid4()),seq,"exposure",key,2,
                command["goal_version"],command["scope_revision"],exposure_body,sha(exposure_body),
                goal_record_id=goal["record_id"],exercise_record_id=body["exercise_record_id"],parent_record_id=record_id,source_refs=source_refs)
            if current and normal:
                projection,nodes = await self._teaching_rebuild_progress(connection,activity_id,head)
                current_node = projection["nodes"][head["node_id"]]
                candidate = None
                if current_node["status"] == "evidence_sufficient":
                    candidate = next((n["node_id"] for n in nodes if projection["nodes"][n["node_id"]]["status"] != "evidence_sufficient"
                        and all(projection["nodes"][f"n{p+1}"]["status"] == "evidence_sufficient" for p in n["prerequisites"])),None)
                progress_id = str(uuid4())
                seq += 1
                reason = "按当前评价已有两个不同的独立实例，含复测，可有限前进。" if candidate else "保留当前节点；独立实例不足、存在辅助或争议时不推定长期掌握。"
                progress_body = canonical({"feedback_record_id":record_id,"answer_record_id":body["answer_record_id"],
                    "advance":bool(candidate),"node_before":head["node_id"],"node_after":candidate or head["node_id"],
                    "reason":reason,"observations":current_node,"support_checks":derive_support_checks(
                        await self._teaching_fact_result(connection,activity_id,reference_rows[body["exercise_record_id"]]),
                        _decode(reference_rows[body["answer_record_id"]]["body"])["text"])})
                final_head.update(reason_record_id=progress_id,projection=projection)
                if candidate:
                    final_head.update(node_id=candidate,phase="ready",exercise_record_id=None,answer_record_id=None,feedback_record_id=None)
                await self._teaching_insert_record(connection,activity_id,progress_id,seq,"progress",key,3,
                    command["goal_version"],command["scope_revision"],progress_body,sha(progress_body),goal_record_id=goal["record_id"],
                    parent_record_id=record_id,exercise_record_id=body["exercise_record_id"],answer_record_id=body["answer_record_id"],
                    source_refs=source_refs,applied_revision=new_revision,state_after=_state_after(new_revision,final_head))
        if current:
            await self._teaching_update_head(connection,activity_id,head,new_revision,phase=final_head["phase"],
                node_id=final_head["node_id"],exercise_record_id=final_head["exercise_record_id"] or _HEAD_CLEAR,
                answer_record_id=final_head["answer_record_id"] or _HEAD_CLEAR,feedback_record_id=final_head["feedback_record_id"] or _HEAD_CLEAR,
                reason_record_id=final_head["reason_record_id"],projection=final_head["projection"],pending_business_key=None,last_seq=seq)
        else:
            await connection.execute("UPDATE teaching_heads SET last_seq=%s WHERE activity_id=%s",(seq,activity_id))
            if str(head["pending_business_key"] or "") == key:
                await connection.execute("UPDATE teaching_heads SET pending_business_key=NULL WHERE activity_id=%s",(activity_id,))
        await connection.execute("UPDATE teaching_commands SET status=%s,result_record_id=%s,updated_at=CURRENT_TIMESTAMP WHERE activity_id=%s AND business_key=%s",
            ("committed" if current else "history",record_id,activity_id,key))

    async def _teaching_read_command_row(self,connection,activity_id,key,lock=False):
        cursor = await connection.execute("SELECT * FROM teaching_commands WHERE activity_id=%s AND business_key=%s"+(" FOR UPDATE" if lock else ""),(activity_id,key))
        return await cursor.fetchone()

    async def _teaching_confirm_integrity(self,connection,call,payload_triple):
        command = await self._teaching_read_command_row(connection,str(call["activity_id"]),call["operation_id"].split(".")[1])
        if command is None or command["operation_id"] != call["operation_id"]:
            raise TeachingRefusal("integrity_error","终态缺少教学命令")
        if payload_triple is None:
            if command["status"] not in ("failed","not_sent","unknown"):
                raise TeachingRefusal("integrity_error","终态与教学收据不一致")
            return
        cursor = await connection.execute("SELECT * FROM teaching_records WHERE activity_id=%s AND business_key=%s ORDER BY ordinal",(call["activity_id"],command["business_key"]))
        records = await cursor.fetchall()
        if (not records or records[0]["operation_id"] != call["operation_id"] or records[0]["body_sha256"] != payload_triple[2]
                or str(command["result_record_id"]) != str(records[0]["record_id"]) or command["status"] not in ("committed","history")):
            raise TeachingRefusal("integrity_error","既有教学链不完整，禁止追补")
        if command["action"] == "evaluate" and (len(records)<2 or records[1]["kind"] != "exposure" or records[1]["exercise_record_id"] != records[0]["exercise_record_id"]):
            raise TeachingRefusal("integrity_error","既有反馈暴露链不完整")

    async def _teaching_set_exercise(self, connection, activity_id, record_id) -> None:
        await connection.execute(
            """UPDATE teaching_heads SET exercise_record_id=%s, answer_record_id=NULL,
                   feedback_record_id=NULL, updated_at=CURRENT_TIMESTAMP WHERE activity_id=%s""",
            (record_id, activity_id))

    @staticmethod
    def _teaching_result_current(head,command,activity):
        return (head is not None and command["status"] == "started" and command["obsolete_at"] is None
                and command["abandoned_at"] is None and head["revision"] == command["expected_revision"]
                and head["goal_version"] == command["goal_version"] and activity["scope_revision"] == command["scope_revision"]
                and str(head["pending_business_key"] or "") == str(command["business_key"]))

    # --- 只读投影 ---

    async def _teaching_read_snapshot(self, activity_id, *, limit=20, before=None,
                                      record_id=None, business_key=None):
        """每个公开读取只执行本语句；JSONB 由驱动解码，不二次拼装快照。"""
        async def operation(connection):
            cursor = await connection.execute(await self._memory_teaching_sql(connection,"""
                WITH a AS (SELECT * FROM activities WHERE id=%(aid)s),
                h AS (SELECT * FROM teaching_heads WHERE activity_id=%(aid)s),
                sources AS (
                    SELECT s.source_id::text,s.version_id::text,s.source_revision,
                        COALESCE(m.current_version=s.version_id AND m.revision=s.source_revision,false) AS valid,
                        v.filename AS title,v.format,v.sha256,v.size,
                        CASE WHEN v.format IN ('txt','md') THEN true
                             WHEN v.format='pdf' THEN EXISTS (
                                 SELECT 1 FROM pdf_review_candidates c WHERE c.version_id=s.version_id
                                 AND c.status='confirmed' AND c.page_count BETWEEN 1 AND 50
                                 AND (SELECT count(*) FROM pdf_review_pages p WHERE p.candidate_id=c.id)=c.page_count
                                 AND (SELECT count(*) FROM pdf_extracted_pages p WHERE p.version_id=c.version_id)=c.page_count)
                             ELSE false END AS ready
                    FROM activity_scope_sources s LEFT JOIN material_sources m ON m.id=s.source_id
                    LEFT JOIN material_versions v ON v.id=s.version_id AND v.source_id=s.source_id
                    WHERE s.activity_id=%(aid)s ORDER BY s.source_id LIMIT 11),
                record_versions AS (
                    SELECT DISTINCT ref.parts[1] AS version_id FROM teaching_records r
                    CROSS JOIN LATERAL regexp_matches(r.source_refs,
                        '"version_id"[[:space:]]*:[[:space:]]*"([0-9a-f-]{36})"', 'g') AS ref(parts)
                    WHERE r.activity_id=%(aid)s),
                record_sources AS (
                    SELECT v.source_id::text,v.id::text AS version_id,m.revision AS source_revision,
                        v.filename AS title,v.format,v.sha256,v.size,
                        COALESCE(m.current_version=v.id,false) AS valid,
                        CASE WHEN v.format IN ('txt','md') THEN true WHEN v.format='pdf' THEN EXISTS (
                            SELECT 1 FROM pdf_review_candidates c WHERE c.version_id=v.id AND c.status='confirmed'
                            AND c.page_count BETWEEN 1 AND 50
                            AND (SELECT count(*) FROM pdf_review_pages p WHERE p.candidate_id=c.id)=c.page_count
                            AND (SELECT count(*) FROM pdf_extracted_pages p WHERE p.version_id=v.id)=c.page_count)
                            ELSE false END AS ready
                    FROM record_versions rv JOIN material_versions v ON v.id::text=rv.version_id
                    LEFT JOIN material_sources m ON m.id=v.source_id),
                pending AS (SELECT business_key::text,action,status,error_code,created_at,
                    launch_claimed_at,obsolete_at,abandoned_at FROM teaching_commands
                    WHERE activity_id=%(aid)s ORDER BY created_at DESC,business_key LIMIT 8),
                history AS (SELECT record_id::text,kind,seq,goal_version,scope_revision,parent_record_id::text,created_at,source_refs
                    FROM teaching_records WHERE activity_id=%(aid)s
                    AND (%(before)s::bigint IS NULL OR seq<%(before)s) ORDER BY seq DESC LIMIT %(limit)s),
                command AS (SELECT * FROM teaching_commands WHERE activity_id=%(aid)s AND business_key=%(key)s::uuid),
                bodies AS (SELECT r.activity_id,r.record_id,r.seq,r.kind,r.business_key,r.ordinal,
                    r.goal_version,r.scope_revision,r.goal_record_id,r.parent_record_id,r.exercise_record_id,
                    r.answer_record_id,r.supersedes_record_id,r.operation_id,r.body_sha256,r.source_refs,
                    r.applied_revision,r.created_at,
                    CASE WHEN r.kind IN ('goal','answer','correction','exposure') OR /*teach_record_memory*/TRUE
                         THEN r.body ELSE NULL END AS body,
                    CASE WHEN /*teach_record_memory*/TRUE THEN r.state_after ELSE NULL END AS state_after,
                    r.business_key AS command_key,
                    CASE WHEN /*teach_record_memory*/TRUE THEN o.payload ELSE NULL END AS payload,
                    o.payload_format,o.payload_sha256 AS operation_payload_sha256,
                    CASE WHEN /*teach_record_memory*/TRUE THEN COALESCE(o.payload,po.payload) ELSE NULL END AS citation_payload,
                    COALESCE(o.payload_format,po.payload_format) AS citation_payload_format,
                    COALESCE(o.payload_sha256,po.payload_sha256) AS citation_payload_sha256
                    FROM teaching_records r LEFT JOIN activity_operation_results o
                    ON o.activity_id=r.activity_id AND o.operation_id=r.operation_id
                    LEFT JOIN teaching_records parent ON r.kind='path_accept' AND parent.activity_id=r.activity_id
                        AND parent.record_id=r.parent_record_id AND parent.kind='path_proposal'
                    LEFT JOIN activity_operation_results po ON po.activity_id=parent.activity_id AND po.operation_id=parent.operation_id
                    WHERE r.activity_id=%(aid)s AND (r.record_id=%(rid)s::uuid OR r.business_key=%(key)s::uuid
                      OR r.record_id IN (SELECT goal_record_id FROM h UNION ALL SELECT path_record_id FROM h
                      UNION ALL SELECT exercise_record_id FROM h UNION ALL SELECT answer_record_id FROM h
                      UNION ALL SELECT feedback_record_id FROM h UNION ALL SELECT reason_record_id FROM h
                      UNION ALL SELECT (projection::jsonb->>'pending_proposal_record_id')::uuid FROM h))),
                exposures AS (SELECT r.record_id::text,r.exercise_record_id::text,r.parent_record_id::text,
                    r.business_key::text AS command_key,r.body,r.body_sha256,r.goal_version,r.scope_revision
                    FROM teaching_records r WHERE r.activity_id=%(aid)s AND r.kind='exposure'
                    AND r.exercise_record_id IN (SELECT exercise_record_id FROM bodies
                                               UNION ALL SELECT record_id FROM bodies WHERE kind='exercise'))
                SELECT (SELECT to_jsonb(a) FROM a) AS activity,(SELECT to_jsonb(h) FROM h) AS head,
                    COALESCE((SELECT jsonb_agg(x ORDER BY x.source_id) FROM sources x),'[]'::jsonb) AS sources,
                    COALESCE((SELECT jsonb_agg(x ORDER BY x.source_id,x.version_id) FROM record_sources x),'[]'::jsonb) AS record_sources,
                    COALESCE((SELECT jsonb_agg(x ORDER BY x.created_at DESC) FROM pending x),'[]'::jsonb) AS pending,
                    COALESCE((SELECT jsonb_agg(x ORDER BY x.seq DESC) FROM history x),'[]'::jsonb) AS history,
                    COALESCE((SELECT jsonb_agg(x ORDER BY x.seq) FROM bodies x),'[]'::jsonb) AS bodies,
                    COALESCE((SELECT jsonb_agg(x) FROM exposures x),'[]'::jsonb) AS exposures,
                    (SELECT to_jsonb(command) FROM command) AS command,
                    /*teach_memory*/TRUE AS memory_qualified, /*teach_selected*/FALSE AS memory_selected,
                    CURRENT_TIMESTAMP AS read_at
                """), {"aid":activity_id,"key":business_key,"rid":record_id,"before":before,"limit":limit})
            row=await cursor.fetchone()
            if row is None or row['activity'] is None:
                return None
            view = {k:_decode(v) if k!='read_at' else v.isoformat() for k,v in row.items()}
            from app.learning.teaching_views import record_sources_valid, bound_references
            for fact in view['bodies']:
                fact['memory_qualified']=view['memory_qualified']
                fact['source_qualified'] = record_sources_valid(fact, view['record_sources'])
                refs = bound_references(fact) or []
                keys = {(r['source_id'],r['version_id']) for r in refs}
                fact['bound_sources'] = [s for s in view['record_sources'] if (s['source_id'],s['version_id']) in keys]
            for item in view['history']:
                item['qualification'] = ('source_invalid' if item['kind'] not in ('goal','answer','correction','exposure')
                                         and not record_sources_valid(item,view['record_sources']) else 'history')
                if not view['memory_qualified'] and item['kind'] not in ('goal','answer','correction','exposure'):
                    item['qualification']='memory_invalid'
                item.pop('source_refs')
            return view
        return await self._transaction(operation)

    async def read_teaching_workspace(self, activity_id: str, history_limit: int = _HISTORY_LIMIT_DEFAULT) -> dict | None:
        activity_id=self._uuid(activity_id,"activity_id")
        if not 1<=history_limit<=_HISTORY_LIMIT_MAX:
            raise ValueError("invalid_input")
        view=await self._teaching_read_snapshot(activity_id,limit=history_limit)
        if view is None:
            return None
        view["current_bodies"]=view.pop("bodies")
        view["pending_business_key"]=(view["head"] or {}).get("pending_business_key")
        return view

    async def read_teaching_command(self, activity_id: str, business_key: str) -> dict | None:
        activity_id=self._uuid(activity_id,"activity_id")
        business_key=self._uuid(business_key,"business_key")
        view=await self._teaching_read_snapshot(activity_id,business_key=business_key)
        if view is None or view["command"] is None:
            return None
        view["head_revision"]=(view["head"] or {}).get("revision",0)
        view["records"]=[r for r in view["bodies"] if r["command_key"]==business_key]
        return view

    async def read_teaching_history(self, activity_id: str, limit: int = _HISTORY_LIMIT_DEFAULT,
                                    before_seq: int | None = None) -> dict | None:
        activity_id=self._uuid(activity_id,"activity_id")
        if not 1<=limit<=_HISTORY_LIMIT_MAX or before_seq is not None and not 1<=before_seq<=MAX_RECORDS:
            raise ValueError("invalid_input")
        view=await self._teaching_read_snapshot(activity_id,limit=limit,before=before_seq)
        if view is None:
            return None
        view["items"]=view.pop("history")
        return view

    async def read_teaching_record(self, activity_id: str, record_id: str) -> dict | None:
        activity_id=self._uuid(activity_id,"activity_id")
        record_id=self._uuid(record_id,"record_id")
        view=await self._teaching_read_snapshot(activity_id,record_id=record_id)
        if view is None:
            return None
        row=next((r for r in view["bodies"] if r["record_id"]==record_id),None)
        if row is None:
            return None
        return row | {"snapshot_sources":view["sources"],"snapshot_head":view["head"],
                      "snapshot_activity":view["activity"],"snapshot_exposures":view["exposures"],
                      "snapshot_read_at":view["read_at"]}

    async def read_teaching_exposures(self, activity_id: str, exercise_record_id: str) -> set[str]:
        activity_id = self._uuid(activity_id, "activity_id")

        async def operation(connection) -> set[str]:
            return await self._teaching_exercise_exposures(connection, activity_id, exercise_record_id)

        return await self._transaction(operation)

    async def read_teaching_head(self, activity_id: str) -> dict | None:
        """当前教学 head 只读快照（锁前组包用；锁内以 CAS/核对为准）。"""
        activity_id = self._uuid(activity_id, "activity_id")

        async def operation(connection) -> dict | None:
            cursor = await connection.execute(
                "SELECT * FROM teaching_heads WHERE activity_id=%s", (activity_id,))
            return await cursor.fetchone()

        return await self._transaction(operation)

    async def read_teaching_facts(self, activity_id: str, *, exercise_record_id: str | None = None,
                                  answer_record_id: str | None = None, kinds: tuple[str, ...] = (),
                                  limit: int = 6) -> list[dict]:
        """按题/答定位有限教学事实（evaluate 组包：题/答/纠错/前史/核算）。

        只读；返回 seq 降序前 limit 条完整行。kinds 为空表示不过滤 kind。
        """
        activity_id = self._uuid(activity_id, "activity_id")
        if not 1 <= limit <= 12:
            raise ValueError("invalid_input")

        async def operation(connection) -> list[dict]:
            conditions = ["activity_id=%s"]
            params: list = [activity_id]
            if kinds:
                conditions += ["kind = ANY(%s)"]
                params.append(list(kinds))
            if exercise_record_id is not None:
                conditions += ["exercise_record_id=%s"]
                params.append(self._uuid(exercise_record_id, "exercise_record_id"))
            if answer_record_id is not None:
                conditions += ["answer_record_id=%s"]
                params.append(self._uuid(answer_record_id, "answer_record_id"))
            params.append(limit)
            cursor = await connection.execute(
                f"""SELECT * FROM teaching_records WHERE {" AND ".join(conditions)}
                      ORDER BY seq DESC LIMIT %s""", tuple(params))
            return list(await cursor.fetchall())

        return await self._transaction(operation)
