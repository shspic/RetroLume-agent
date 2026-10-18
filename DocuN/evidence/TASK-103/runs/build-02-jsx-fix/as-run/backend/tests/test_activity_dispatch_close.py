"""TASK-083 关闭门内部契约离线测试；真实PG行为留独立预算卡。"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest
from uuid import uuid4
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.activities import ActivityLedgerConflict, CloseResult, PostgresAdmissionLedger, SettleResult
from app.capabilities import AdmissionDenied, AdmissionIntent, CallContext, Provider


class _Cursor:
    def __init__(self, row):
        self.row = row

    async def fetchone(self):
        return self.row


class _Connection:
    def __init__(self):
        self.row = {
            "status": "running", "executor_id": "worker-1", "execution_generation": 1,
            "dispatch_closed": False, "running_reserved_seconds": 10,
            "last_settled_generation": None, "last_settled_seconds": None,
        }
        self.updates = 0

    async def execute(self, sql, params=()):
        if sql.startswith("SELECT * FROM activities"):
            return _Cursor(dict(self.row))
        if "UPDATE activities SET dispatch_closed = TRUE" in sql:
            self.row["dispatch_closed"] = True
            self.updates += 1
        elif "last_settled_generation = %s" in sql:
            self.row.update(
                status="pending", executor_id=None,
                execution_generation=self.row["execution_generation"] + 1,
                running_reserved_seconds=0,
                last_settled_generation=params[1], last_settled_seconds=params[2],
            )
            self.updates += 1
        return _Cursor(None)


class CloseGateRepositoryTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.ledger = PostgresAdmissionLedger("synthetic-not-connected")
        self.connection = _Connection()

        async def transaction(operation):
            return await operation(self.connection)

        async def source_rows(connection, activity_id):
            return []

        async def lock_sources(connection, snapshots):
            return True

        self.ledger._transaction = transaction
        self.ledger._source_rows = source_rows
        self.ledger._lock_sources = lock_sources
        self.activity_id = str(uuid4())

    async def test_01_close_current_is_idempotent_old_identity_cannot_touch_new_window(self):
        self.assertEqual(await self.ledger.begin_window_close(self.activity_id, "worker-1", 1), CloseResult.CLOSED)
        self.assertEqual(await self.ledger.begin_window_close(self.activity_id, "worker-1", 1), CloseResult.ALREADY_CLOSED)
        self.assertEqual(self.connection.updates, 1)
        for executor, generation in (("worker-2", 1), ("worker-1", 0)):
            with self.assertRaises(ActivityLedgerConflict):
                await self.ledger.begin_window_close(self.activity_id, executor, generation)
        self.assertEqual(self.connection.updates, 1)

    async def test_02_settle_requires_close_but_old_same_g_c_remains_idempotent(self):
        with self.assertRaises(ActivityLedgerConflict):
            await self.ledger.settle_execution_window(
                self.activity_id, "worker-1", 1, window_seconds=10, elapsed_seconds=2,
            )
        self.assertEqual(self.connection.updates, 0)
        await self.ledger.begin_window_close(self.activity_id, "worker-1", 1)
        self.assertEqual(await self.ledger.settle_execution_window(
            self.activity_id, "worker-1", 1, window_seconds=10, elapsed_seconds=2,
        ), SettleResult.SETTLED)
        self.assertEqual(await self.ledger.settle_execution_window(
            self.activity_id, "worker-1", 1, window_seconds=10, elapsed_seconds=2,
        ), SettleResult.ALREADY_SETTLED)
        self.assertEqual(self.connection.updates, 2)

    async def test_03_admit_denied_when_db_gate_closed(self):
        activity = {
            "status": "running", "dispatch_closed": True, "executor_id": "worker-1",
            "execution_generation": 1, "scope_revision": 1,
            "lease_expires_at": datetime.now(timezone.utc) + timedelta(seconds=60),
            "deadline_at": datetime.now(timezone.utc) + timedelta(seconds=60),
            "max_request_bytes": 1024, "max_output_tokens": 64, "allowed_tools": [],
            "requests_reserved": 0, "max_requests": 4,
            "cost_reserved_microunits": 0, "reserve_cost_microunits": 1,
            "max_cost_microunits": 10,
        }
        intent = AdmissionIntent(
            CallContext(activity_id=self.activity_id, operation_id="op-1", executor_id="worker-1", execution_generation=1, scope_revision=1),
            Provider.DEEPSEEK_CHAT_COMPLETIONS, "synthetic", 12, 16, (),
        )
        self.assertFalse(self.ledger._activity_allows(activity, intent, "worker-1", now=datetime.now(timezone.utc)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
