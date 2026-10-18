"""TASK-083 exact-anchor adaptation of existing exports and time-budget PG expectations."""
from pathlib import Path


def edit(name: str, changes: list[tuple[str, str]]) -> None:
    path = Path(name)
    source = path.read_text(encoding="utf-8")
    for before, after in changes:
        count = source.count(before)
        if count != 1:
            raise RuntimeError(f"{name}: anchor count={count}: {before[:80]!r}")
        source = source.replace(before, after, 1)
    path.write_text(source, encoding="utf-8", newline="")


edit("backend/app/activities/__init__.py", [
    ("    ActivitySpec,\n", "    ActivitySpec,\n    CloseResult,\n"),
    ("    UnresolvedOperation,\n", "    UnresolvedOperation,\n    WindowSnapshot,\n"),
    ('    "ActivitySpec",\n', '    "ActivitySpec",\n    "CloseResult",\n'),
    ('    "UnresolvedOperation",\n', '    "UnresolvedOperation",\n    "WindowSnapshot",\n'),
])

edit("backend/tests/test_activity_time_budget.py", [
    ('''    async def settle(self, lease, *, elapsed_seconds, executor: str | None = None, window: int | None = None):
        return await self.ledger.settle_execution_window(
''', '''    async def settle(self, lease, *, elapsed_seconds, executor: str | None = None, window: int | None = None):
        # 仅对仍是当前合法运行代次的基础合成用例先关门；旧幂等/旧代次请求不碰新门。
        row = await self.budget_row()
        if (
            row["status"] == "running"
            and row["execution_generation"] == lease.execution_generation
            and row["executor_id"] == (executor or lease.executor_id)
        ):
            await self.ledger.begin_window_close(
                self.activity_id, lease.executor_id, lease.execution_generation
            )
        return await self.ledger.settle_execution_window(
'''),
])
