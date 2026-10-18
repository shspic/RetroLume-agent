"""One-time TASK-083 source edit, with exact preimage anchors and no code execution."""
from pathlib import Path

path = Path("backend/app/activities/repository.py")
source = path.read_text(encoding="utf-8")
edits = [
    ('    ALREADY_SETTLED = "already_settled"\n\n\n@dataclass(frozen=True)\nclass SourceSnapshot:',
     '    ALREADY_SETTLED = "already_settled"\n\n\nclass CloseResult(enum.Enum):\n    CLOSED = "closed"\n    ALREADY_CLOSED = "already_closed"\n\n\n@dataclass(frozen=True)\nclass WindowSnapshot:\n    status: str\n    execution_generation: int\n    running_reserved_seconds: int\n    dispatch_closed: bool\n\n\n@dataclass(frozen=True)\nclass SourceSnapshot:'),
    ("                                  running_reserved_seconds = 0,\n                                  running_settled_seconds = %s,",
     "                                  dispatch_closed = TRUE,\n                                  running_reserved_seconds = 0,\n                                  running_settled_seconds = %s,"),
    ("                          lease_expires_at = %s, running_reserved_seconds = %s,\n                          running_settled_seconds = %s, updated_at = CURRENT_TIMESTAMP",
     "                          lease_expires_at = %s, running_reserved_seconds = %s,\n                          dispatch_closed = FALSE,\n                          running_settled_seconds = %s, updated_at = CURRENT_TIMESTAMP"),
    ("    async def settle_execution_window(\n",
     '''    async def inspect_window(self, activity_id: str) -> WindowSnapshot:
        """恢复入口的只读快照；调用方须持活动排他锁并在 claim 前核对旧 Job。"""
        activity_id = self._uuid(activity_id, "activity_id")

        async def operation(connection: object) -> WindowSnapshot:
            cursor = await connection.execute(
                """SELECT status, execution_generation, running_reserved_seconds, dispatch_closed
                     FROM activities WHERE id = %s""",
                (activity_id,),
            )
            row = await cursor.fetchone()
            if row is None:
                raise ActivityLedgerConflict("活动不存在")
            return WindowSnapshot(
                row["status"], row["execution_generation"],
                row["running_reserved_seconds"], row["dispatch_closed"],
            )

        return await self._transaction(operation)

    async def begin_window_close(
        self, activity_id: str, executor_id: str, execution_generation: int,
    ) -> CloseResult:
        """只关闭当前代次的出站门；不退款、不改预扣或代次。"""
        activity_id = self._uuid(activity_id, "activity_id")
        executor_id = self._bounded_name(executor_id, "executor_id")
        if (
            isinstance(execution_generation, bool)
            or not isinstance(execution_generation, int)
            or execution_generation < 0
        ):
            raise ValueError("执行代次必须是非负整数")

        async def operation(connection: object) -> CloseResult:
            snapshots = await self._source_rows(connection, activity_id)
            await self._lock_sources(connection, snapshots)
            cursor = await connection.execute("SELECT * FROM activities WHERE id = %s FOR UPDATE", (activity_id,))
            row = await cursor.fetchone()
            if (
                row is None or row["status"] != "running"
                or row["executor_id"] != executor_id
                or row["execution_generation"] != execution_generation
            ):
                raise ActivityLedgerConflict("关闭请求与当前运行代次不匹配")
            if row["dispatch_closed"]:
                return CloseResult.ALREADY_CLOSED
            await connection.execute(
                """UPDATE activities SET dispatch_closed = TRUE, updated_at = CURRENT_TIMESTAMP
                     WHERE id = %s""",
                (activity_id,),
            )
            return CloseResult.CLOSED

        return await self._transaction(operation)

    async def settle_execution_window(
'''),
    ('                or row["running_reserved_seconds"] != window_seconds\n',
     '                or row["running_reserved_seconds"] != window_seconds\n                or not row["dispatch_closed"]\n'),
    ("                          last_settled_generation = %s, last_settled_seconds = %s,\n",
     "                          dispatch_closed = TRUE,\n                          last_settled_generation = %s, last_settled_seconds = %s,\n"),
    ("                          lease_expires_at = NULL, cancelled_at = CURRENT_TIMESTAMP,\n",
     "                          lease_expires_at = NULL, cancelled_at = CURRENT_TIMESTAMP,\n                          dispatch_closed = TRUE,\n"),
    ('            activity["status"] == "running"\n',
     '            activity["status"] == "running"\n            and not activity["dispatch_closed"]\n'),
    ('            if call["state"] != "reserved" or not self._operation_is_current(activity, call, sources_valid):\n',
     '            if (\n                call["state"] != "reserved" or activity["dispatch_closed"]\n                or not self._operation_is_current(activity, call, sources_valid)\n            ):\n'),
]
for before, after in edits:
    count = source.count(before)
    if count < 1:
        raise RuntimeError(f"preimage anchor mismatch: {before[:60]!r} count={count}")
    source = source.replace(before, after, 1)
path.write_text(source, encoding="utf-8", newline="")
