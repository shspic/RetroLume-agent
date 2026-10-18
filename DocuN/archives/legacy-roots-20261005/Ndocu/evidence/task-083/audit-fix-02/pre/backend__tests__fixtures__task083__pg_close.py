"""TASK-083 专用真实PG用例准备；本轮严格 not_run。"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import sys
import unittest
from uuid import uuid4

BACKEND = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(BACKEND))

import psycopg
from psycopg.rows import dict_row

from app.activities import ActivityLedgerConflict, ActivitySpec, CloseResult, PostgresAdmissionLedger, SettleResult, SourceSnapshot
from app.capabilities import AdmissionDenied, AdmissionIntent, CallContext, LedgerDisposition, LedgerOutcome, Provider
from app.runtime import psycopg_compatible_loop_factory


DSN = os.environ.get("RETROLUME_TASK_083_DATABASE_URL", "")


class _PsycopgCase(unittest.IsolatedAsyncioTestCase):
    def _setupAsyncioRunner(self) -> None:
        assert self._asyncioRunner is None
        self._asyncioRunner = asyncio.Runner(debug=True, loop_factory=psycopg_compatible_loop_factory)


@unittest.skipUnless(DSN, "仅在TASK-083专用合成PG运行；不回退应用/用户DSN")
class PGCloseTests(_PsycopgCase):
    async def asyncSetUp(self):
        self.ledger = PostgresAdmissionLedger(DSN)
        self.activity_id = str(uuid4())
        self.source_id = str(uuid4())
        self.version_id = str(uuid4())

    async def asyncTearDown(self):
        # 只按本例合成ID、FK顺序清理；任何失败显式传播。
        async with await psycopg.AsyncConnection.connect(DSN) as conn:
            async with conn.transaction():
                for table in ("activity_operations", "activity_allowed_models", "activity_scope_sources", "activities"):
                    await conn.execute(f"DELETE FROM {table} WHERE {'id' if table == 'activities' else 'activity_id'} = %s", (self.activity_id,))
                await conn.execute("UPDATE material_sources SET current_version = NULL WHERE id = %s", (self.source_id,))
                await conn.execute("DELETE FROM material_versions WHERE id = %s", (self.version_id,))
                await conn.execute("DELETE FROM material_sources WHERE id = %s", (self.source_id,))

    async def row(self, sql, params=()):
        async with await psycopg.AsyncConnection.connect(DSN, row_factory=dict_row) as conn:
            return await (await conn.execute(sql, params)).fetchone()

    async def build(self):
        async with await psycopg.AsyncConnection.connect(DSN) as conn:
            async with conn.transaction():
                await conn.execute("INSERT INTO material_sources(id,title,revision) VALUES (%s,'task083',0)", (self.source_id,))
                await conn.execute(
                    "INSERT INTO material_versions(id,source_id,filename,format,sha256,size) VALUES (%s,%s,'task083.txt','txt',%s,1)",
                    (self.version_id, self.source_id, "d" * 64),
                )
                await conn.execute("UPDATE material_sources SET current_version=%s,revision=1 WHERE id=%s", (self.version_id, self.source_id))
        spec = ActivitySpec(
            activity_id=self.activity_id,
            sources=(SourceSnapshot(self.source_id, self.version_id, 1),),
            deadline_at=datetime.now(timezone.utc) + timedelta(minutes=20),
            max_requests=8, max_cost_microunits=800, reserve_cost_microunits=100,
            max_request_bytes=4096, max_output_tokens=256, max_running_seconds=180,
            allowed_models=((Provider.DEEPSEEK_CHAT_COMPLETIONS.value, "synthetic-model"),),
            allowed_tools=(), scope_revision=1,
        )
        await self.ledger.create_activity(spec)
        lease = await self.ledger.claim_lease(self.activity_id, "worker-1", lease_seconds=90, window_seconds=90)
        assert lease is not None
        return lease

    def intent(self, lease, operation_id):
        return AdmissionIntent(
            CallContext(activity_id=self.activity_id, operation_id=operation_id,
                        executor_id=lease.executor_id, execution_generation=lease.execution_generation,
                        scope_revision=lease.scope_revision),
            Provider.DEEPSEEK_CHAT_COMPLETIONS, "synthetic-model", 512, 64, (),
        )

    async def test_pg01_close_settle_and_old_gc_does_not_touch_new_window(self):
        lease = await self.build()
        before = await self.row("SELECT dispatch_closed,running_reserved_seconds FROM activities WHERE id=%s", (self.activity_id,))
        self.assertEqual(before, {"dispatch_closed": False, "running_reserved_seconds": 90})
        with self.assertRaises(ActivityLedgerConflict):
            await self.ledger.settle_execution_window(self.activity_id, "worker-1", lease.execution_generation,
                                                       window_seconds=90, elapsed_seconds=2)
        self.assertEqual(await self.ledger.begin_window_close(self.activity_id, "worker-1", lease.execution_generation), CloseResult.CLOSED)
        self.assertEqual(await self.ledger.begin_window_close(self.activity_id, "worker-1", lease.execution_generation), CloseResult.ALREADY_CLOSED)
        self.assertEqual(await self.ledger.settle_execution_window(self.activity_id, "worker-1", lease.execution_generation,
                                                                    window_seconds=90, elapsed_seconds=2), SettleResult.SETTLED)
        next_lease = await self.ledger.claim_lease(self.activity_id, "worker-2", lease_seconds=90, window_seconds=90)
        self.assertIsNotNone(next_lease)
        opened = await self.row("SELECT status,execution_generation,dispatch_closed,running_reserved_seconds,running_settled_seconds FROM activities WHERE id=%s", (self.activity_id,))
        self.assertEqual(await self.ledger.settle_execution_window(self.activity_id, "worker-1", lease.execution_generation,
                                                                    window_seconds=90, elapsed_seconds=2), SettleResult.ALREADY_SETTLED)
        self.assertEqual(await self.row("SELECT status,execution_generation,dispatch_closed,running_reserved_seconds,running_settled_seconds FROM activities WHERE id=%s", (self.activity_id,)), opened)
        with self.assertRaises(ActivityLedgerConflict):
            await self.ledger.begin_window_close(self.activity_id, "worker-1", lease.execution_generation)

    async def test_pg02_closed_gate_rejects_admit_mark_but_records_outcomes(self):
        lease = await self.build()
        reserved = await self.ledger.admit(self.intent(lease, "reserved-op"))
        dispatched = await self.ledger.admit(self.intent(lease, "dispatched-op"))
        received = await self.ledger.admit(self.intent(lease, "received-op"))
        await self.ledger.mark_dispatch_started(dispatched)
        await self.ledger.mark_dispatch_started(received)
        await self.ledger.begin_window_close(self.activity_id, "worker-1", lease.execution_generation)
        with self.assertRaises(AdmissionDenied):
            await self.ledger.admit(self.intent(lease, "new-op"))
        with self.assertRaises(AdmissionDenied):
            await self.ledger.mark_dispatch_started(reserved)
        await self.ledger.record_outcome(reserved, LedgerOutcome(LedgerDisposition.NOT_SENT))
        await self.ledger.record_outcome(dispatched, LedgerOutcome(LedgerDisposition.UNKNOWN, error_code="synthetic_unknown"))
        await self.ledger.record_outcome(received, LedgerOutcome(LedgerDisposition.RECEIVED, remote_request_id="synthetic-id", returned_model="synthetic-model", finish_reason="stop", prompt_tokens=1, completion_tokens=1, response_bytes=12))
        rows = await self.row("SELECT count(*) FILTER (WHERE state='not_sent') AS not_sent,count(*) FILTER (WHERE state='unknown') AS unknown,count(*) FILTER (WHERE state='received') AS received FROM activity_operations WHERE activity_id=%s", (self.activity_id,))
        self.assertEqual(rows, {"not_sent": 1, "unknown": 1, "received": 1})

    async def test_pg03_close_commits_before_concurrent_admit_and_mark(self):
        lease = await self.build()
        permit = await self.ledger.admit(self.intent(lease, "reserved-before-close"))
        entered = asyncio.Event()
        release = asyncio.Event()
        close_ledger = PostgresAdmissionLedger(DSN)
        original_lock = close_ledger._lock_sources

        async def held_lock(connection, snapshots):
            valid = await original_lock(connection, snapshots)
            entered.set()  # 已持真实来源行锁，尚未取得活动锁。
            await release.wait()
            return valid

        close_ledger._lock_sources = held_lock
        close_task = asyncio.create_task(close_ledger.begin_window_close(self.activity_id, "worker-1", lease.execution_generation))
        await asyncio.wait_for(entered.wait(), timeout=5)
        admit_task = asyncio.create_task(self.ledger.admit(self.intent(lease, "after-close")))
        mark_task = asyncio.create_task(self.ledger.mark_dispatch_started(permit))
        await asyncio.sleep(0)  # 让两连接进入同一来源行的锁队列。
        release.set()
        self.assertEqual(await asyncio.wait_for(close_task, timeout=5), CloseResult.CLOSED)
        for task in (admit_task, mark_task):
            with self.assertRaises(AdmissionDenied):
                await asyncio.wait_for(task, timeout=5)


    async def test_pg04_cancel_closes_gate_and_old_dispatched_unknown_converges(self):
        lease = await self.build()
        permit = await self.ledger.admit(self.intent(lease, "before-cancel"))
        await self.ledger.mark_dispatch_started(permit)
        cancelled_generation = await self.ledger.cancel_activity(self.activity_id)
        self.assertEqual(cancelled_generation, lease.execution_generation + 1)
        row = await self.row("SELECT status,dispatch_closed,running_reserved_seconds,running_settled_seconds FROM activities WHERE id=%s", (self.activity_id,))
        self.assertEqual(row, {"status": "cancelled", "dispatch_closed": True, "running_reserved_seconds": 0, "running_settled_seconds": 90})
        await self.ledger.record_outcome(permit, LedgerOutcome(LedgerDisposition.UNKNOWN, error_code="cancelled"))
        self.assertEqual(await self.row("SELECT state FROM activity_operations WHERE admission_id=%s", (permit.admission_id,)), {"state": "unknown"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
