"""G8 教学领域仓储方法（TASK-100）。

作为 Mixin 挂到 PostgresAdmissionLedger；全部方法经 self._transaction
（同一短事务、同一锁序：来源 UUID 排序→活动→相关 operation→
teaching_heads→teaching_commands 键排序→新 records）执行。教学 helper
只使用传入 connection，不嵌套事务。网络/工具执行永远在事务外。
"""
from __future__ import annotations

import json
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
    TeachingRefusal,
    semantic_slot,
)
from app.learning.contracts import canonical, sha

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
    }
    encoded = canonical(value)
    if len(encoded.encode("utf-8")) > MAX_STATE_AFTER_BYTES:
        raise TeachingRefusal("result_limit", "教学状态投影超过上限")
    return encoded


class TeachingLedgerMethods:
    """教学命令/事实/投影的持久实现；失败关闭，不伪造资格。"""

    # --- 锁内公共 ---

    async def _teaching_lock(self, connection, activity_id: str) -> _TeachingLocked:
        """来源→活动→head 锁序；head 惰性（不存在返回 head=None）。"""
        snapshots = await self._source_rows(connection, activity_id)
        await self._lock_sources(connection, snapshots)
        cursor = await connection.execute("SELECT * FROM activities WHERE id = %s FOR UPDATE", (activity_id,))
        activity = await cursor.fetchone()
        await self._verify_scope_hint(connection, activity_id, snapshots)
        if activity is None:
            raise TeachingRefusal("not_found", "活动不存在")
        cursor = await connection.execute("SELECT * FROM teaching_heads WHERE activity_id = %s FOR UPDATE",
                                          (activity_id,))
        head = await cursor.fetchone()
        return _TeachingLocked(activity, head, None)

    async def _teaching_lock_command(self, connection, activity_id: str, business_key: str) -> _TeachingLocked:
        locked = await self._teaching_lock(connection, activity_id)
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
            """SELECT business_key, request_body, request_sha256 FROM teaching_commands
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
                 (SELECT count(*) FROM teaching_records WHERE activity_id=%s AND kind='correction') AS corrections""",
            (activity_id, activity_id, activity_id, activity_id, activity_id))
        return await cursor.fetchone()

    @staticmethod
    def _teaching_cas(head, expected_revision: int, expected_goal_version: int,
                      expected_scope_revision: int, activity, action: str) -> None:
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
        if for_write and activity["dispatch_closed"]:
            # 零费保存允许在关门后仍拒绝新正文；与旧 G3 正文关门纪律一致。
            raise TeachingRefusal("activity_cancelled", "活动已关门，教学新写不可用")

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
                                   pending_business_key="unset", last_seq=None) -> None:
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
            f"UPDATE teaching_commands SET status='history', obsolete_at=CURRENT_TIMESTAMP, "
            f"updated_at=CURRENT_TIMESTAMP WHERE {conditions}", tuple(params))

    # --- T-local：O01/03/05/06/09/11 及未启动 O10 ---

    async def apply_teaching_local(self, activity_id: str, command: TeachingCommandInput) -> TeachingCommandReceipt:
        activity_id = self._uuid(activity_id, "activity_id")
        request_body = canonical(command.canonical_request_body(activity_id))
        if len(request_body.encode("utf-8")) > 32768:
            raise TeachingRefusal("input_too_large", "命令正文超过上限")
        request_sha = sha(request_body)

        async def operation(connection) -> TeachingCommandReceipt:
            locked = await self._teaching_lock_command(connection, activity_id, command.business_key)
            activity, head, existing = locked.activity, locked.head, locked.command
            if existing is not None:
                if self._teaching_replay(existing, request_sha, request_body):
                    head_revision = 0 if head is None else head["revision"]
                    return _row_receipt(existing, head_revision)
                raise TeachingRefusal("command_key_conflict", "同键已绑定不同内容，保留原意图；如需修改请用新键")
            self._teaching_cas(head, command.expected_revision, command.expected_goal_version,
                               command.expected_scope_revision, activity, command.action)
            self._teaching_gate(activity)
            # 语义槽竞争（锁内查胜者）。
            slot = semantic_slot(activity_id, command, self._teaching_anchors(head, command))
            winner = await self._teaching_slot_winner(connection, activity_id, command.action, slot)
            duplicate_of = None
            if winner is not None:
                if winner["request_body"] == request_body:
                    duplicate_of = str(winner["business_key"])
                else:
                    raise TeachingRefusal("stage_conflict", "同父槽已有不同内容，保留双方输入")
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
            records, revision = await self._teaching_apply_local_effects(
                connection, activity_id, head, activity, command, request_body, request_sha)
            head_revision = 0 if head is None else revision
            if head is not None and records:
                head_revision = revision
            return _row_receipt(
                {"activity_id": activity_id, "business_key": command.business_key, "action": command.action,
                 "request_sha256": request_sha, "status": "committed", "operation_id": None,
                 "error_code": None},
                head_revision, record_ids=records)
            del now

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
        return anchors

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
            if goal_version >= MAX_GOAL_VERSION:
                raise TeachingRefusal("history_limit", "目标版本已达上限")
            new_version = goal_version + 1
            goal_record = str(uuid4())
            goal_body = canonical({"goal": body["goal"], "self_report": body.get("self_report"),
                                   "domain": body.get("domain")})
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
                applied_revision=new_revision, state_after=state)
            if head is None:
                await self._teaching_create_head(connection, activity_id, new_revision, new_version,
                                                 "needs_plan", goal_record, seq_base)
            else:
                await self._teaching_update_head(
                    connection, activity_id, head, new_revision, phase="needs_plan",
                    goal_version=new_version, goal_record_id=goal_record,
                    path_record_id=_HEAD_CLEAR, pending_business_key=None, last_seq=seq_base)
            records.append(RecordRef(record_id=goal_record, kind="goal", seq=goal_seq))
            return records, new_revision

        if action == "accept_path":
            proposal = await self._teaching_read_record_row(connection, activity_id, body["proposal_record_id"])
            if proposal is None or proposal["kind"] != "path_proposal":
                raise TeachingRefusal("record_not_found", "路径提案不存在")
            self._teaching_gate(activity)
            path_record = str(uuid4())
            path_body = canonical({"proposal_record_id": body["proposal_record_id"],
                                   "nodes": json.loads(proposal["source_refs"]) if proposal["source_refs"] else []})
            first_node = "n1"
            path_seq = next_seq()
            new_revision = bump_revision()
            state = _state_after(new_revision, {
                "goal_version": goal_version, "phase": "ready", "goal_record_id": head["goal_record_id"],
                "path_record_id": path_record, "node_id": first_node, "exercise_record_id": None,
                "answer_record_id": None, "feedback_record_id": None, "reason_record_id": None})
            # DEF-003：INSERT 即最终事实；exercise/answer/feedback 指针由
            # _teaching_clear_exercise_pointers 清空，不经 head UPDATE 传哨兵。
            await self._teaching_insert_record(
                connection, activity_id, path_record, path_seq, "path_accept", command.business_key, 1,
                goal_version, scope_revision, path_body, sha(path_body),
                goal_record_id=head["goal_record_id"],
                applied_revision=new_revision, state_after=state)
            await self._teaching_update_head(
                connection, activity_id, head, new_revision, phase="ready", path_record_id=path_record,
                pending_business_key=None, last_seq=seq_base)
            await self._teaching_clear_exercise_pointers(connection, activity_id)
            records.append(RecordRef(record_id=path_record, kind="path_accept", seq=path_seq))
            return records, new_revision

        if action == "expose":
            exercise = await self._teaching_read_record_row(connection, activity_id, body["exercise_record_id"])
            if exercise is None or exercise["kind"] != "exercise":
                raise TeachingRefusal("record_not_found", "练习不存在")
            # 重复 exposure：核对后返回原事实，不新记。
            cursor = await connection.execute(
                """SELECT 1 FROM teaching_records WHERE activity_id=%s AND kind='exposure'
                     AND business_key=%s""", (activity_id, command.business_key))
            if await cursor.fetchone() is not None:
                return records, revision
            exposure_record = str(uuid4())
            exposure_body = canonical({"exercise_record_id": body["exercise_record_id"], "part": body["part"]})
            await self._teaching_insert_record(
                connection, activity_id, exposure_record, next_seq(), "exposure", command.business_key, 1,
                exercise["goal_version"], exercise["scope_revision"], exposure_body, sha(exposure_body),
                goal_record_id=exercise["goal_record_id"],
                exercise_record_id=body["exercise_record_id"])
            is_current = head is not None and head["exercise_record_id"] == body["exercise_record_id"]
            if is_current:
                new_revision = bump_revision()
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
                    """SELECT supersedes_record_id FROM teaching_records
                        WHERE activity_id=%s AND record_id=%s AND kind='answer'""",
                    (activity_id, supersedes))
                row = await cursor.fetchone()
                if row is None or row["supersedes_record_id"] is not None:
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
            await self._teaching_obsolete_pending(connection, activity_id)
            new_revision = bump_revision()
            state = _state_after(new_revision, {
                "goal_version": goal_version, "phase": "answer_saved", "goal_record_id": head["goal_record_id"],
                "path_record_id": head["path_record_id"], "node_id": head["node_id"],
                "exercise_record_id": body["exercise_record_id"], "answer_record_id": answer_record,
                "feedback_record_id": None, "reason_record_id": head["reason_record_id"]})
            # DEF-003：作答事实一次成型，无事后回填。
            await self._teaching_insert_record(
                connection, activity_id, answer_record, answer_seq, "answer", command.business_key, 1,
                exercise["goal_version"], exercise["scope_revision"], answer_body, sha(answer_body),
                goal_record_id=exercise["goal_record_id"],
                exercise_record_id=body["exercise_record_id"], supersedes_record_id=supersedes,
                applied_revision=new_revision, state_after=state)
            await self._teaching_update_head(
                connection, activity_id, head, new_revision, phase="answer_saved",
                answer_record_id=answer_record, pending_business_key=None, last_seq=seq_base)
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
            await self._teaching_insert_record(
                connection, activity_id, correction_record, next_seq(), "correction", command.business_key, 1,
                goal_version, scope_revision, correction_body, sha(correction_body),
                goal_record_id=head["goal_record_id"], parent_record_id=body["target_record_id"])
            # 当前图内 feedback/progress 的 answer 观察 contested：不删除，投影重算。
            new_revision = bump_revision()
            await self._teaching_update_head(connection, activity_id, head, new_revision, last_seq=seq_base)
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
            return records, revision

        if action == "select_node":
            if head is None or head["path_record_id"] is None:
                raise TeachingRefusal("stage_conflict", "尚无已接受路径")
            selection_record = str(uuid4())
            selection_body = canonical({"path_record_id": body["path_record_id"],
                                        "node_id": body["node_id"], "archive_current": body["archive_current"]})
            selection_seq = next_seq()
            new_revision = bump_revision()
            state = _state_after(new_revision, {
                "goal_version": goal_version, "phase": "ready", "goal_record_id": head["goal_record_id"],
                "path_record_id": body["path_record_id"], "node_id": body["node_id"],
                "exercise_record_id": None, "answer_record_id": None, "feedback_record_id": None,
                "reason_record_id": None})
            # DEF-003：节点选择事实一次成型。
            await self._teaching_insert_record(
                connection, activity_id, selection_record, selection_seq, "node_selection",
                command.business_key, 1, goal_version, scope_revision, selection_body,
                sha(selection_body), goal_record_id=head["goal_record_id"],
                applied_revision=new_revision, state_after=state)
            await self._teaching_update_head(connection, activity_id, head, new_revision, phase="ready",
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
            "SELECT body FROM teaching_records WHERE activity_id=%s AND kind='exposure' AND exercise_record_id=%s ORDER BY seq",
            (activity_id, exercise_record_id))
        parts = set()
        for row in await cursor.fetchall():
            try:
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
            if existing is not None:
                if self._teaching_replay(existing, request_sha, request_body):
                    return _row_receipt(existing, 0 if head is None else head["revision"])
                raise TeachingRefusal("command_key_conflict", "同键已绑定不同内容")
            if head is None:
                raise TeachingRefusal("version_conflict", "教学尚未初始化，先保存目标")
            self._teaching_cas(head, command.expected_revision, command.expected_goal_version,
                               command.expected_scope_revision, activity, command.action)
            self._teaching_gate(activity)
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
                    duplicate_of = str(winner["business_key"])
                else:
                    raise TeachingRefusal("stage_conflict", "同父槽已有不同内容")
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
                 None, context_body, frozen.context_sha256, operation_id, None))
            await self._teaching_update_head(connection, activity_id, head, head["revision"],
                                             pending_business_key=command.business_key)
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
            if head is not None and head["pending_business_key"] is not None \
                    and str(head["pending_business_key"]) != str(business_key):
                return {"launch_allowed": False, "reason": "no_longer_current_binding"}
            cursor = await connection.execute(
                "SELECT 1 FROM activity_operations WHERE activity_id=%s AND operation_id=%s",
                (activity_id, command["operation_id"]))
            if await cursor.fetchone() is not None:
                return {"launch_allowed": False, "reason": "operation_exists"}
            if activity["status"] != "pending" or activity["dispatch_closed"]:
                return {"launch_allowed": False, "reason": "activity_not_launchable"}
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
                return _row_receipt(command, head_revision)
            # DEF-007：以「本次确认后的结局」处理指针，不得读 UPDATE 前的
            # 旧 command.status 判断（旧值恒为 started/accepted，会使失败
            # 收据永远清不掉 pending）。确定未准入 → failed 并清本键
            # pending；其余保守 unknown，pending 占槽保留（UNKNOWN 不解槽）。
            final_status = "failed" if getattr(supervision, "definitely_not_admitted", False) else "unknown"
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
            return _row_receipt(await cursor.fetchone(), head_revision)

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
        cursor = await connection.execute(
            "SELECT * FROM teaching_commands WHERE activity_id=%s AND business_key=%s FOR UPDATE",
            (str(activity["id"]), key))
        command = await cursor.fetchone()
        if command is None or command["operation_id"] != operation_id:
            raise TeachingRefusal("unknown_slot", "教学命令未找到或操作键不匹配")
        if command["request_sha256"] != digest:
            raise TeachingRefusal("unknown_slot", "教学请求摘要不匹配")
        if command["status"] not in ("started",):
            if phase == "admit":
                raise TeachingRefusal("launch_already_claimed", "教学命令不在启动状态")
        if command["obsolete_at"] is not None or command["abandoned_at"] is not None:
            raise TeachingRefusal("unknown_slot", "教学命令已废弃")
        if binding is not None:
            if (str(command["business_key"]) != binding.command_key
                    or command["request_sha256"] != binding.request_sha256):
                raise TeachingRefusal("unknown_slot", "教学绑定不匹配")
            if command["context_sha256"] != binding.context_sha256:
                raise TeachingRefusal("unknown_slot", "教学上下文不匹配")
        return command

    # --- T-result：教学事实与原 record 同事务提交 ---

    async def _write_teaching_outcome(self, connection, activity, call, outcome, payload_triple) -> None:
        """record_outcome/record_tool_outcome 原事务内教学效果提交。

        调用前提（外层已保证）：原 _write_outcome 已写终态/正文。
        分支：
        - 无正文终态（failed/not_sent/unknown）：command 同状态 + 清本键 pending；
        - received 成功正文：教学当前资格合法 → 当前 facts + progress + head；
          教学版本已变（G3 资格仍合法，外层已放行正文） → history facts + 历史 exposure。
        """
        operation_id = call["operation_id"]
        if not operation_id.startswith((TEACHING_PREFIX_MODEL, TEACHING_PREFIX_TOOL)):
            return
        activity_id = str(activity["id"])
        key = operation_id.split(".")[1]
        cursor = await connection.execute(
            "SELECT * FROM teaching_commands WHERE activity_id=%s AND business_key=%s FOR UPDATE",
            (activity_id, key))
        command = await cursor.fetchone()
        if command is None or command["operation_id"] != operation_id:
            return
        cursor = await connection.execute(
            "SELECT * FROM teaching_heads WHERE activity_id=%s FOR UPDATE", (activity_id,))
        head = await cursor.fetchone()
        disposition = outcome.disposition.value if hasattr(outcome.disposition, "value") else str(outcome.disposition)
        if payload_triple is None or disposition != "received":
            status = {"not_sent": "not_sent", "unknown": "unknown"}.get(disposition, "failed")
            await connection.execute(
                """UPDATE teaching_commands SET status=%s, error_code=%s, updated_at=CURRENT_TIMESTAMP
                    WHERE activity_id=%s AND business_key=%s""",
                (status, call.get("error_code"), activity_id, key))
            if head is not None and head["pending_business_key"] is not None \
                    and str(head["pending_business_key"]) == key:
                await connection.execute(
                    "UPDATE teaching_heads SET pending_business_key=NULL, updated_at=CURRENT_TIMESTAMP WHERE activity_id=%s",
                    (activity_id,))
            return

        # 成功正文：解析 StoredTeachingDocument。
        try:
            document = json.loads(payload_triple[1])
            value = document["value"]
            result = value["result"]
            action = command["action"]
            result_type = result.get("result_type")
        except (ValueError, TypeError, KeyError):
            await connection.execute(
                """UPDATE teaching_commands SET status='failed', error_code='invalid_teaching_output',
                       updated_at=CURRENT_TIMESTAMP WHERE activity_id=%s AND business_key=%s""",
                (activity_id, key))
            if head is not None and str(head["pending_business_key"] or "") == key:
                await connection.execute(
                    "UPDATE teaching_heads SET pending_business_key=NULL WHERE activity_id=%s", (activity_id,))
            return

        current_ok = self._teaching_result_current(head, command, activity)
        seq_base = 0 if head is None else head["last_seq"]
        revision = 0 if head is None else head["revision"]
        goal_version = 0 if head is None else head["goal_version"]
        scope_revision = activity["scope_revision"]
        payload_sha = payload_triple[2]
        record_id = str(uuid4())

        def next_seq() -> int:
            nonlocal seq_base
            seq_base += 1
            if seq_base > MAX_RECORDS:
                raise TeachingRefusal("history_limit", "教学记录数已达上限")
            return seq_base

        if not current_ok:
            # 历史分支：不可变历史 fact（不含 progress），qualification=history_only。
            kind = {"plan": "path_proposal", "exercise": "exercise", "evaluate": "feedback",
                    "calculate": "calculation"}[action]
            await self._teaching_insert_record(
                connection, activity_id, record_id, next_seq(), kind, key, 1,
                max(goal_version, 1), scope_revision, None, payload_sha,
                goal_record_id=(head or {}).get("goal_record_id"), operation_id=operation_id,
                parent_record_id=command["parent_record_id"])
            if action == "evaluate":
                exposure_id = str(uuid4())
                exposure_body = canonical({"exercise_record_id": None, "part": "reference",
                                           "history_feedback_record_id": record_id})
                await self._teaching_insert_record(
                    connection, activity_id, exposure_id, next_seq(), "exposure", key, 2,
                    max(goal_version, 1), scope_revision, exposure_body, sha(exposure_body),
                    goal_record_id=(head or {}).get("goal_record_id"))
            await connection.execute(
                """UPDATE teaching_commands SET status='history', result_record_id=%s, updated_at=CURRENT_TIMESTAMP
                    WHERE activity_id=%s AND business_key=%s""",
                (record_id, activity_id, key))
            await connection.execute(
                "UPDATE teaching_heads SET last_seq=%s, pending_business_key=NULL WHERE activity_id=%s",
                (seq_base, activity_id))
            return

        # 当前分支：按 action 写当前 facts + progress（feedback）+ head。
        if action == "plan":
            if result_type == "path":
                new_revision = revision + 1
                state = _state_after(new_revision, {
                    "goal_version": goal_version, "phase": "path_review",
                    "goal_record_id": head["goal_record_id"], "path_record_id": head["path_record_id"],
                    "node_id": head["node_id"], "exercise_record_id": None, "answer_record_id": None,
                    "feedback_record_id": None, "reason_record_id": record_id})
                # DEF-003：提案事实一次成型（正文在 007，body=NULL + 007 封套 hash）。
                await self._teaching_insert_record(
                    connection, activity_id, record_id, next_seq(), "path_proposal", key, 1,
                    goal_version, scope_revision, None, payload_sha,
                    goal_record_id=head["goal_record_id"], operation_id=operation_id,
                    applied_revision=new_revision, state_after=state)
                await self._teaching_update_head(connection, activity_id, head, new_revision,
                                                 phase="path_review", reason_record_id=record_id,
                                                 pending_business_key=None, last_seq=seq_base)
            else:
                await self._teaching_insert_record(
                    connection, activity_id, record_id, next_seq(), "path_proposal", key, 1,
                    goal_version, scope_revision, None, payload_sha,
                    goal_record_id=head["goal_record_id"], operation_id=operation_id)
                await connection.execute(
                    "UPDATE teaching_heads SET last_seq=%s, pending_business_key=NULL WHERE activity_id=%s",
                    (seq_base, activity_id))
        elif action == "exercise":
            if result_type == "exercise":
                new_revision = revision + 1
                state = _state_after(new_revision, {
                    "goal_version": goal_version, "phase": "exercise_ready",
                    "goal_record_id": head["goal_record_id"], "path_record_id": head["path_record_id"],
                    "node_id": head["node_id"], "exercise_record_id": record_id, "answer_record_id": None,
                    "feedback_record_id": None, "reason_record_id": head["reason_record_id"]})
                # DEF-003：练习事实一次成型。
                await self._teaching_insert_record(
                    connection, activity_id, record_id, next_seq(), "exercise", key, 1,
                    goal_version, scope_revision, None, payload_sha,
                    goal_record_id=head["goal_record_id"], operation_id=operation_id,
                    applied_revision=new_revision, state_after=state)
                await self._teaching_update_head(connection, activity_id, head, new_revision,
                                                 phase="exercise_ready", last_seq=seq_base,
                                                 pending_business_key=None)
                await self._teaching_set_exercise(connection, activity_id, record_id)
            else:
                await self._teaching_insert_record(
                    connection, activity_id, record_id, next_seq(), "exercise", key, 1,
                    goal_version, scope_revision, None, payload_sha,
                    goal_record_id=head["goal_record_id"], operation_id=operation_id)
                await connection.execute(
                    "UPDATE teaching_heads SET last_seq=%s, pending_business_key=NULL WHERE activity_id=%s",
                    (seq_base, activity_id))
        elif action == "evaluate":
            feedback_record = record_id
            await self._teaching_insert_record(
                connection, activity_id, feedback_record, next_seq(), "feedback", key, 1,
                goal_version, scope_revision, None, payload_sha,
                goal_record_id=head["goal_record_id"], operation_id=operation_id,
                exercise_record_id=head["exercise_record_id"], answer_record_id=head["answer_record_id"])
            exposure_id = str(uuid4())
            exposure_body = canonical({"exercise_record_id": str(head["exercise_record_id"]),
                                       "part": "reference", "with_feedback": feedback_record})
            await self._teaching_insert_record(
                connection, activity_id, exposure_id, next_seq(), "exposure", key, 2,
                goal_version, scope_revision, exposure_body, sha(exposure_body),
                goal_record_id=head["goal_record_id"],
                exercise_record_id=head["exercise_record_id"])
            if result_type == "feedback":
                progress_id = str(uuid4())
                progress_body = canonical({"feedback_record_id": feedback_record,
                                           "answer_record_id": str(head["answer_record_id"]),
                                           "advance": False, "phase_after": "feedback_ready"})
                new_revision = revision + 1
                state = _state_after(new_revision, {
                    "goal_version": goal_version, "phase": "feedback_ready",
                    "goal_record_id": head["goal_record_id"], "path_record_id": head["path_record_id"],
                    "node_id": head["node_id"], "exercise_record_id": head["exercise_record_id"],
                    "answer_record_id": head["answer_record_id"], "feedback_record_id": feedback_record,
                    "reason_record_id": progress_id})
                # DEF-003：progress 事实一次成型；feedback/exposure 本身不带
                # state_after（head 效果归 progress 一条，一版本至多一个）。
                await self._teaching_insert_record(
                    connection, activity_id, progress_id, next_seq(), "progress", key, 3,
                    goal_version, scope_revision, progress_body, sha(progress_body),
                    goal_record_id=head["goal_record_id"], parent_record_id=feedback_record,
                    exercise_record_id=head["exercise_record_id"], answer_record_id=head["answer_record_id"],
                    applied_revision=new_revision, state_after=state)
                await self._teaching_update_head(connection, activity_id, head, new_revision,
                                                 phase="feedback_ready", feedback_record_id=feedback_record,
                                                 reason_record_id=progress_id, last_seq=seq_base,
                                                 pending_business_key=None)
            else:
                await connection.execute(
                    "UPDATE teaching_heads SET last_seq=%s, pending_business_key=NULL WHERE activity_id=%s",
                    (seq_base, activity_id))
        elif action == "calculate":
            new_revision = revision + 1
            state = _state_after(new_revision, {
                "goal_version": goal_version, "phase": head["phase"], "goal_record_id": head["goal_record_id"],
                "path_record_id": head["path_record_id"], "node_id": head["node_id"],
                "exercise_record_id": head["exercise_record_id"], "answer_record_id": head["answer_record_id"],
                "feedback_record_id": head["feedback_record_id"], "reason_record_id": head["reason_record_id"]})
            # DEF-003：核算事实一次成型（正文在 007）。
            await self._teaching_insert_record(
                connection, activity_id, record_id, next_seq(), "calculation", key, 1,
                goal_version, scope_revision, None, payload_sha,
                goal_record_id=head["goal_record_id"], operation_id=operation_id,
                exercise_record_id=head["exercise_record_id"], answer_record_id=head["answer_record_id"],
                applied_revision=new_revision, state_after=state)
            await self._teaching_update_head(connection, activity_id, head, new_revision, last_seq=seq_base,
                                             pending_business_key=None)
        else:
            raise TeachingRefusal("invalid_input", "未知教学动作")

        await connection.execute(
            """UPDATE teaching_commands SET status='committed', result_record_id=%s, updated_at=CURRENT_TIMESTAMP
                WHERE activity_id=%s AND business_key=%s""",
            (record_id, activity_id, key))

    async def _teaching_set_exercise(self, connection, activity_id, record_id) -> None:
        await connection.execute(
            """UPDATE teaching_heads SET exercise_record_id=%s, answer_record_id=NULL,
                   feedback_record_id=NULL, updated_at=CURRENT_TIMESTAMP WHERE activity_id=%s""",
            (record_id, activity_id))

    @staticmethod
    def _teaching_result_current(head, command, activity) -> bool:
        """T-result 教学当前资格：head/命令 CAS 与活动资格复核。"""
        if head is None:
            return False
        if command["status"] not in ("started",):
            return False
        if head["goal_version"] != command["goal_version"]:
            return False
        if head["revision"] != command["expected_revision"] + 1 and head["revision"] != command["expected_revision"]:
            # 启动后 head 只被本命令效果推进一次；超出即版本已变。
            if head["revision"] > command["expected_revision"] + 1:
                return False
        if command["obsolete_at"] is not None or command["abandoned_at"] is not None:
            return False
        return activity["status"] != "cancelled"

    # --- 只读投影 ---

    async def read_teaching_workspace(self, activity_id: str, history_limit: int = _HISTORY_LIMIT_DEFAULT) -> dict | None:
        activity_id = self._uuid(activity_id, "activity_id")
        if not 1 <= history_limit <= _HISTORY_LIMIT_MAX:
            raise ValueError("invalid_input")

        async def operation(connection) -> dict | None:
            # DEF-005：单条 CTE 语句构成一致读快照——活动、head、最近意图
            # 摘要、历史摘要、来源资格、当前实体正文（007 联查）与当前题
            # 暴露状态在同一语句内读取；默认隔离下单语句即单快照，不再
            # 用四条独立 SELECT 拼接多版本视图。
            cursor = await connection.execute(
                """
                WITH h AS (
                    SELECT * FROM teaching_heads WHERE activity_id = %s
                ),
                pending AS (
                    SELECT business_key::text AS business_key, action, status, error_code,
                           created_at, launch_claimed_at, obsolete_at, abandoned_at
                      FROM teaching_commands WHERE activity_id = %s
                     ORDER BY created_at DESC, business_key LIMIT 8
                ),
                history AS (
                    SELECT record_id::text AS record_id, kind, seq, goal_version,
                           parent_record_id::text AS parent_record_id, created_at
                      FROM teaching_records WHERE activity_id = %s
                     ORDER BY seq DESC LIMIT %s
                ),
                sources AS (
                    SELECT COALESCE(jsonb_agg(x ORDER BY x->>'source_id'), '[]'::jsonb) AS items
                      FROM (
                        SELECT jsonb_build_object('source_id', s.source_id::text,
                            'version_id', s.version_id::text, 'source_revision', s.source_revision,
                            'valid', COALESCE(m.current_version = s.version_id
                                      AND m.revision = s.source_revision, false),
                            'title', v.filename, 'format', v.format,
                            'sha256', v.sha256) AS x
                          FROM activity_scope_sources s
                          LEFT JOIN material_sources m ON m.id = s.source_id
                          LEFT JOIN material_versions v
                            ON v.id = s.version_id AND v.source_id = s.source_id
                         WHERE s.activity_id = %s ORDER BY s.source_id LIMIT 11) q
                ),
                pointers AS (
                    SELECT goal_record_id, path_record_id, exercise_record_id,
                           answer_record_id, feedback_record_id, reason_record_id
                      FROM teaching_heads WHERE activity_id = %s
                ),
                current_bodies AS (
                    SELECT r.record_id::text AS record_id, r.kind, r.seq,
                           r.goal_version, r.parent_record_id::text AS parent_record_id,
                           r.exercise_record_id::text AS exercise_record_id,
                           r.answer_record_id::text AS answer_record_id,
                           r.body, r.body_sha256, r.created_at, o.payload
                      FROM teaching_records r
                      LEFT JOIN activity_operation_results o
                        ON o.activity_id = r.activity_id AND o.operation_id = r.operation_id
                     WHERE r.activity_id = %s AND r.record_id IN (
                           SELECT goal_record_id FROM pointers
                           UNION ALL SELECT path_record_id FROM pointers
                           UNION ALL SELECT exercise_record_id FROM pointers
                           UNION ALL SELECT answer_record_id FROM pointers
                           UNION ALL SELECT feedback_record_id FROM pointers
                           UNION ALL SELECT reason_record_id FROM pointers)
                ),
                exposures AS (
                    SELECT COALESCE(jsonb_agg(DISTINCT r.body->>'part'), '[]'::jsonb) AS parts
                      FROM teaching_records r
                     WHERE r.activity_id = %s AND r.kind = 'exposure'
                       AND r.exercise_record_id = (SELECT exercise_record_id FROM pointers)
                )
                SELECT (SELECT to_jsonb(a) FROM activities a WHERE a.id = %s) AS activity,
                       (SELECT to_jsonb(h) FROM h) AS head,
                       COALESCE((SELECT jsonb_agg(x ORDER BY x.created_at DESC) FROM pending x), '[]'::jsonb) AS pending,
                       COALESCE((SELECT jsonb_agg(x ORDER BY x.seq DESC) FROM history x), '[]'::jsonb) AS history,
                       (SELECT items FROM sources) AS sources,
                       COALESCE((SELECT jsonb_agg(x ORDER BY x.seq) FROM current_bodies x), '[]'::jsonb) AS current_bodies,
                       (SELECT parts FROM exposures) AS exposed_parts,
                       (SELECT pending_business_key::text FROM h) AS pending_business_key
                """,
                (activity_id, activity_id, activity_id, history_limit, activity_id,
                 activity_id, activity_id, activity_id, activity_id))
            row = await cursor.fetchone()
            if row is None or row["activity"] is None:
                return None
            return {
                "activity": json.loads(row["activity"]),
                "head": json.loads(row["head"]) if row["head"] else None,
                "pending": json.loads(row["pending"]),
                "history": json.loads(row["history"]),
                "sources": json.loads(row["sources"]),
                "current_bodies": json.loads(row["current_bodies"]),
                "exposed_parts": json.loads(row["exposed_parts"]),
                "pending_business_key": row["pending_business_key"],
            }

        return await self._transaction(operation)

    async def read_teaching_command(self, activity_id: str, business_key: str) -> dict | None:
        activity_id = self._uuid(activity_id, "activity_id")
        business_key = self._uuid(business_key, "business_key")

        async def operation(connection) -> dict | None:
            cursor = await connection.execute(
                "SELECT * FROM teaching_commands WHERE activity_id=%s AND business_key=%s",
                (activity_id, business_key))
            row = await cursor.fetchone()
            if row is None:
                return None
            cursor = await connection.execute(
                "SELECT revision FROM teaching_heads WHERE activity_id=%s", (activity_id,))
            head = await cursor.fetchone()
            return {"command": row, "head_revision": 0 if head is None else head["revision"]}

        return await self._transaction(operation)

    async def read_teaching_history(self, activity_id: str, limit: int = _HISTORY_LIMIT_DEFAULT,
                                    before_seq: int | None = None) -> dict | None:
        activity_id = self._uuid(activity_id, "activity_id")
        if not 1 <= limit <= _HISTORY_LIMIT_MAX:
            raise ValueError("invalid_input")

        async def operation(connection) -> dict | None:
            cursor = await connection.execute("SELECT 1 FROM activities WHERE id=%s", (activity_id,))
            if await cursor.fetchone() is None:
                return None
            conditions, params = "activity_id=%s", [activity_id]
            if before_seq is not None:
                if not 1 <= before_seq <= MAX_RECORDS:
                    raise ValueError("invalid_input")
                conditions += " AND seq < %s"
                params.append(before_seq)
            params.append(limit)
            cursor = await connection.execute(
                f"""SELECT record_id, kind, seq, goal_version, parent_record_id, created_at
                      FROM teaching_records WHERE {conditions} ORDER BY seq DESC LIMIT %s""",
                tuple(params))
            return {"items": list(await cursor.fetchall())}

        return await self._transaction(operation)

    async def read_teaching_record(self, activity_id: str, record_id: str) -> dict | None:
        activity_id = self._uuid(activity_id, "activity_id")
        record_id = self._uuid(record_id, "record_id")

        async def operation(connection) -> dict | None:
            return await self._teaching_read_record_row(connection, activity_id, record_id)

        return await self._transaction(operation)

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
