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
from psycopg import sql
from psycopg.conninfo import make_conninfo
from psycopg.rows import dict_row

from app.activities import ActivityLedgerConflict, ActivitySpec, CloseResult, PostgresAdmissionLedger, SettleResult, SourceSnapshot
from app.capabilities import AdmissionDenied, AdmissionIntent, CallContext, LedgerDisposition, LedgerOutcome, Provider
from app.runtime import psycopg_compatible_loop_factory


DSN = os.environ.get("RETROLUME_TASK_083_DATABASE_URL", "")
MIGRATIONS = [BACKEND / "migrations" / name for name in ("001_materials.sql", "002_activities.sql", "003_pdf_review.sql", "004_activities_time_budget.sql", "005_activities_dispatch_closed.sql")]


class _PsycopgCase(unittest.IsolatedAsyncioTestCase):
    def _setupAsyncioRunner(self) -> None:
        assert self._asyncioRunner is None
        self._asyncioRunner = asyncio.Runner(debug=True, loop_factory=psycopg_compatible_loop_factory)


@unittest.skipUnless(DSN, "仅在TASK-083专用合成PG运行；不回退应用/用户DSN")
class PGCloseTests(_PsycopgCase):
    async def asyncSetUp(self):
        self.schema = "task083_close_" + uuid4().hex
        self.activity_id = str(uuid4())
        self.source_id = str(uuid4())
        self.version_id = str(uuid4())
        # The schema is intentionally retained. A later authorized PG run card
        # owns schema removal, including failed cases.
        async with await psycopg.AsyncConnection.connect(DSN, autocommit=True) as admin:
            await admin.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(self.schema)))
        self.scoped_dsn = make_conninfo(DSN, options=f"-c search_path={self.schema}")
        print(f"task083 PG case schema={self.schema} activity={self.activity_id} source={self.source_id} version={self.version_id}")
        async with await psycopg.AsyncConnection.connect(self.scoped_dsn, autocommit=True) as conn:
            for path in MIGRATIONS:
                await conn.execute(path.read_text(encoding="utf-8"))
        self.ledger = PostgresAdmissionLedger(self.scoped_dsn)

    async def asyncTearDown(self):
        # Failed assertions keep their UUID/FK rows and schema for targeted review.
        if not self._outcome.success:
            print(f"task083 PG failure retained schema={self.schema} activity={self.activity_id}")
            return
        async with await psycopg.AsyncConnection.connect(self.scoped_dsn) as conn:
            async with conn.transaction():
                for table in ("activity_operations", "activity_allowed_models", "activity_scope_sources", "activities"):
                    await conn.execute(f"DELETE FROM {table} WHERE {'id' if table == 'activities' else 'activity_id'} = %s", (self.activity_id,))
                await conn.execute("UPDATE material_sources SET current_version = NULL WHERE id = %s", (self.source_id,))
                await conn.execute("DELETE FROM material_versions WHERE id = %s", (self.version_id,))
                await conn.execute("DELETE FROM material_sources WHERE id = %s", (self.source_id,))

    async def row(self, sql, params=()):
        async with await psycopg.AsyncConnection.connect(self.scoped_dsn, row_factory=dict_row) as conn:
            return await (await conn.execute(sql, params)).fetchone()

    async def build(self):
        async with await psycopg.AsyncConnection.connect(self.scoped_dsn) as conn:
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
        await self.ledger.record_outcome(reserved, LedgerOutcome(LedgerDisposition.UNKNOWN, error_code="synthetic_reserved_unknown"))
        await self.ledger.record_outcome(dispatched, LedgerOutcome(LedgerDisposition.UNKNOWN, error_code="synthetic_unknown"))
        await self.ledger.record_outcome(received, LedgerOutcome(LedgerDisposition.RECEIVED, remote_request_id="synthetic-id", returned_model="synthetic-model", finish_reason="stop", prompt_tokens=1, completion_tokens=1, response_bytes=12))
        rows = await self.row("SELECT count(*) FILTER (WHERE state='not_sent') AS not_sent,count(*) FILTER (WHERE state='unknown') AS unknown,count(*) FILTER (WHERE state='received') AS received FROM activity_operations WHERE activity_id=%s", (self.activity_id,))
        self.assertEqual(rows, {"not_sent": 0, "unknown": 2, "received": 1})

    async def test_pg03_close_commits_before_concurrent_admit_and_mark(self):
        lease = await self.build()
        permit = await self.ledger.admit(self.intent(lease, "reserved-before-close"))
        # Positive order: a legal mark has committed before close.
        prior = await self.ledger.admit(self.intent(lease, "marked-before-close"))
        await self.ledger.mark_dispatch_started(prior)

        entered_close = asyncio.Event()
        release_close = asyncio.Event()
        close_ledger = PostgresAdmissionLedger(self.scoped_dsn)
        original_close_lock = close_ledger._lock_sources

        async def held_lock(connection, snapshots):
            valid = await original_close_lock(connection, snapshots)
            entered_close.set()  # close owns the real source row locks.
            await release_close.wait()
            return valid

        close_ledger._lock_sources = held_lock
        close_task = asyncio.create_task(close_ledger.begin_window_close(
            self.activity_id, "worker-1", lease.execution_generation,
        ))
        try:
            await asyncio.wait_for(entered_close.wait(), timeout=5)
            waiting = [asyncio.Event(), asyncio.Event()]
            admit_ledger = PostgresAdmissionLedger(self.scoped_dsn)
            mark_ledger = PostgresAdmissionLedger(self.scoped_dsn)
            for ledger, ready in ((admit_ledger, waiting[0]), (mark_ledger, waiting[1])):
                original = ledger._lock_sources
                async def observed(connection, snapshots, *, original=original, ready=ready):
                    ready.set()  # this transaction is about to request the held source lock.
                    return await original(connection, snapshots)
                ledger._lock_sources = observed
            admit_task = asyncio.create_task(admit_ledger.admit(self.intent(lease, "after-close")))
            mark_task = asyncio.create_task(mark_ledger.mark_dispatch_started(permit))
            for ready in waiting:
                await asyncio.wait_for(ready.wait(), timeout=5)
        finally:
            release_close.set()
        self.assertEqual(await asyncio.wait_for(close_task, timeout=5), CloseResult.CLOSED)
        for task in (admit_task, mark_task):
            with self.assertRaises(AdmissionDenied):
                await asyncio.wait_for(task, timeout=5)
        await self.ledger.record_outcome(prior, LedgerOutcome(LedgerDisposition.UNKNOWN, error_code="preclose_marked"))

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

