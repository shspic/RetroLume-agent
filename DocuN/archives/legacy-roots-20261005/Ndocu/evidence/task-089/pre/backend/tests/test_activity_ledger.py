"""TASK-048 的专用真实 PostgreSQL 反例；不发送模型请求。"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
import os
import unittest
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row

from app.activities import ActivityLedgerConflict, ActivitySpec, PostgresAdmissionLedger, SourceSnapshot
from app.capabilities import (
    AdmissionDenied,
    AdmissionIntent,
    AdmissionPermit,
    AdmissionUnavailable,
    CallContext,
    LedgerDisposition,
    LedgerOutcome,
    Provider,
)
from app.runtime import psycopg_compatible_loop_factory


DSN = os.environ.get("RETROLUME_TASK_048_DATABASE_URL", "")


class PsycopgLoopIsolatedAsyncioTestCase(unittest.IsolatedAsyncioTestCase):
    def _setupAsyncioRunner(self) -> None:
        assert self._asyncioRunner is None
        self._asyncioRunner = asyncio.Runner(
            debug=True,
            loop_factory=psycopg_compatible_loop_factory,
        )


@unittest.skipUnless(DSN, "仅在 TASK-048 专用合成 PostgreSQL 中运行")
class ActivityLedgerPostgresTests(PsycopgLoopIsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.ledger = PostgresAdmissionLedger(DSN)
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            await connection.execute("DROP TRIGGER IF EXISTS task048_force_failure ON activity_operations")
            await connection.execute("DROP FUNCTION IF EXISTS task048_force_failure()")
            # 007 子表存在时先删子表再删父表（旧 schema 无该表则跳过，不强塞新表清理）。
            await connection.execute(
                """DO $$
                     BEGIN
                       IF to_regclass('public.activity_operation_results') IS NOT NULL THEN
                         EXECUTE 'DELETE FROM activity_operation_results';
                       END IF;
                     END $$"""
            )
            await connection.execute("DELETE FROM activity_operations")
            await connection.execute("DELETE FROM activity_allowed_models")
            await connection.execute("DELETE FROM activity_scope_sources")
            await connection.execute("DELETE FROM activities")
            await connection.execute("UPDATE material_sources SET current_version = NULL")
            await connection.execute("DELETE FROM material_versions")
            await connection.execute("DELETE FROM material_sources")

    async def db_row(self, sql: str, params: tuple = ()) -> dict | None:
        async with await psycopg.AsyncConnection.connect(DSN, row_factory=dict_row) as connection:
            cursor = await connection.execute(sql, params)
            return await cursor.fetchone()

    async def source(self) -> SourceSnapshot:
        source_id, version_id = str(uuid4()), str(uuid4())
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            async with connection.transaction():
                await connection.execute(
                    "INSERT INTO material_sources(id, title, revision) VALUES (%s, 'synthetic', 0)",
                    (source_id,),
                )
                await connection.execute(
                    """INSERT INTO material_versions(id, source_id, filename, format, sha256, size)
                         VALUES (%s, %s, 'synthetic.txt', 'txt', %s, 9)""",
                    (version_id, source_id, "a" * 64),
                )
                await connection.execute(
                    "UPDATE material_sources SET current_version = %s, revision = 1 WHERE id = %s",
                    (version_id, source_id),
                )
        return SourceSnapshot(source_id, version_id, 1)

    async def activity(self, **changes):
        source = changes.pop("source", None) or await self.source()
        values = dict(
            activity_id=str(uuid4()),
            sources=(source,),
            deadline_at=datetime.now(timezone.utc) + timedelta(minutes=20),
            max_requests=4,
            max_cost_microunits=400,
            reserve_cost_microunits=100,
            max_request_bytes=4096,
            max_output_tokens=256,
            max_running_seconds=3600,
            allowed_models=((Provider.DEEPSEEK_CHAT_COMPLETIONS.value, "synthetic-model"),),
            allowed_tools=("finite_calculate",),
            scope_revision=1,
        )
        values.update(changes)
        spec = ActivitySpec(**values)
        await self.ledger.create_activity(spec)
        lease = await self.ledger.claim_lease(
            spec.activity_id, "worker-1", lease_seconds=300, window_seconds=300
        )
        self.assertIsNotNone(lease)
        return spec, lease, source

    @staticmethod
    def intent(spec: ActivitySpec, lease, operation_id: str = "operation-1", **changes) -> AdmissionIntent:
        values = dict(
            context=CallContext(
                activity_id=spec.activity_id,
                operation_id=operation_id,
                executor_id=lease.executor_id,
                execution_generation=lease.execution_generation,
                scope_revision=lease.scope_revision,
            ),
            provider=Provider.DEEPSEEK_CHAT_COMPLETIONS,
            configured_model="synthetic-model",
            request_bytes=512,
            max_output_tokens=64,
            tool_names=(),
        )
        values.update(changes)
        return AdmissionIntent(**values)

    async def test_01_legal_admission_dispatch_and_received(self) -> None:
        spec, lease, _ = await self.activity()
        permit = await self.ledger.admit(self.intent(spec, lease))
        await self.ledger.mark_dispatch_started(permit)
        await self.ledger.record_outcome(
            permit,
            LedgerOutcome(
                LedgerDisposition.RECEIVED,
                remote_request_id="synthetic-remote-1",
                returned_model="synthetic-model",
                finish_reason="stop",
                prompt_tokens=10,
                completion_tokens=4,
                response_bytes=200,
            ),
        )
        operation = await self.db_row("SELECT state, prompt_tokens FROM activity_operations WHERE admission_id = %s", (permit.admission_id,))
        activity = await self.db_row("SELECT requests_reserved, cost_reserved_microunits FROM activities WHERE id = %s", (spec.activity_id,))
        self.assertEqual(operation, {"state": "received", "prompt_tokens": 10})
        self.assertEqual(activity, {"requests_reserved": 1, "cost_reserved_microunits": 100})

    async def test_02_concurrent_duplicate_operation_gets_one_permit(self) -> None:
        spec, lease, _ = await self.activity()
        ledgers = (PostgresAdmissionLedger(DSN), PostgresAdmissionLedger(DSN))
        results = await asyncio.gather(
            *(item.admit(self.intent(spec, lease, "same-operation")) for item in ledgers),
            return_exceptions=True,
        )
        self.assertEqual(sum(isinstance(item, AdmissionPermit) for item in results), 1)
        self.assertEqual(sum(isinstance(item, AdmissionDenied) for item in results), 1)
        row = await self.db_row("SELECT requests_reserved, cost_reserved_microunits FROM activities WHERE id = %s", (spec.activity_id,))
        self.assertEqual(row, {"requests_reserved": 1, "cost_reserved_microunits": 100})

    async def test_03_nonpositive_creation_and_exhausted_limit_are_denied(self) -> None:
        source = await self.source()
        invalid = ActivitySpec(
            activity_id=str(uuid4()),
            sources=(source,),
            deadline_at=datetime.now(timezone.utc) + timedelta(minutes=5),
            max_requests=0,
            max_cost_microunits=100,
            reserve_cost_microunits=100,
            max_request_bytes=100,
            max_output_tokens=10,
            max_running_seconds=3600,
            allowed_models=((Provider.DEEPSEEK_CHAT_COMPLETIONS.value, "synthetic-model"),),
        )
        with self.assertRaises(ValueError):
            await self.ledger.create_activity(invalid)
        spec, lease, _ = await self.activity(max_requests=1, max_cost_microunits=100)
        await self.ledger.admit(self.intent(spec, lease, "first"))
        with self.assertRaises(AdmissionDenied):
            await self.ledger.admit(self.intent(spec, lease, "second"))

    async def test_04_source_version_replacement_revokes_admission(self) -> None:
        spec, lease, source = await self.activity()
        new_version = str(uuid4())
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            async with connection.transaction():
                await connection.execute("SELECT id FROM material_sources WHERE id = %s FOR UPDATE", (source.source_id,))
                await connection.execute(
                    """INSERT INTO material_versions(id, source_id, filename, format, sha256, size)
                         VALUES (%s, %s, 'replacement.txt', 'txt', %s, 11)""",
                    (new_version, source.source_id, "b" * 64),
                )
                await connection.execute(
                    "UPDATE material_sources SET current_version = %s, revision = revision + 1 WHERE id = %s",
                    (new_version, source.source_id),
                )
        with self.assertRaises(AdmissionDenied):
            await self.ledger.admit(self.intent(spec, lease))

    async def test_05_cancel_increments_generation_and_consumes_pending_permit(self) -> None:
        spec, lease, _ = await self.activity()
        permit = await self.ledger.admit(self.intent(spec, lease))
        cancelled_generation = await self.ledger.cancel_activity(spec.activity_id)
        self.assertEqual(cancelled_generation, lease.execution_generation + 1)
        with self.assertRaises(AdmissionDenied):
            await self.ledger.mark_dispatch_started(permit)
        await self.ledger.record_outcome(permit, LedgerOutcome(LedgerDisposition.UNKNOWN, error_code="cancelled"))
        row = await self.db_row("SELECT state FROM activity_operations WHERE admission_id = %s", (permit.admission_id,))
        self.assertEqual(row["state"], "unknown")

    async def test_06_unknown_survives_new_connection_and_keeps_budget(self) -> None:
        spec, lease, _ = await self.activity(max_requests=1, max_cost_microunits=100)
        permit = await self.ledger.admit(self.intent(spec, lease))
        await self.ledger.mark_dispatch_started(permit)
        await self.ledger.record_outcome(permit, LedgerOutcome(LedgerDisposition.UNKNOWN, error_code="deadline_exceeded"))
        reopened = PostgresAdmissionLedger(DSN)
        with self.assertRaises(AdmissionDenied):
            await reopened.admit(self.intent(spec, lease, "another-operation"))
        row = await self.db_row("SELECT requests_reserved, cost_reserved_microunits FROM activities WHERE id = %s", (spec.activity_id,))
        self.assertEqual(row, {"requests_reserved": 1, "cost_reserved_microunits": 100})

    async def test_07_same_outcome_is_idempotent_and_conflict_cannot_overwrite(self) -> None:
        spec, lease, _ = await self.activity()
        permit = await self.ledger.admit(self.intent(spec, lease))
        await self.ledger.mark_dispatch_started(permit)
        outcome = LedgerOutcome(
            LedgerDisposition.RECEIVED,
            returned_model="synthetic-model",
            finish_reason="stop",
            prompt_tokens=3,
            completion_tokens=2,
            response_bytes=80,
        )
        await self.ledger.record_outcome(permit, outcome)
        await PostgresAdmissionLedger(DSN).record_outcome(permit, outcome)
        with self.assertRaises(AdmissionDenied):
            await self.ledger.record_outcome(permit, LedgerOutcome(LedgerDisposition.UNKNOWN, error_code="different"))
        row = await self.db_row("SELECT requests_reserved, cost_reserved_microunits, state FROM activities JOIN activity_operations ON activities.id = activity_operations.activity_id WHERE admission_id = %s", (permit.admission_id,))
        self.assertEqual(row, {"requests_reserved": 1, "cost_reserved_microunits": 100, "state": "received"})

    async def test_08_transaction_failure_leaves_no_partial_reservation(self) -> None:
        spec, lease, _ = await self.activity()
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            await connection.execute(
                """CREATE FUNCTION task048_force_failure() RETURNS trigger LANGUAGE plpgsql AS $$
                     BEGIN
                       IF NEW.operation_id = 'force-db-failure' THEN
                         RAISE EXCEPTION 'synthetic transaction failure';
                       END IF;
                       RETURN NEW;
                     END $$"""
            )
            await connection.execute(
                """CREATE TRIGGER task048_force_failure BEFORE INSERT ON activity_operations
                     FOR EACH ROW EXECUTE FUNCTION task048_force_failure()"""
            )
        with self.assertRaises(AdmissionUnavailable):
            await self.ledger.admit(self.intent(spec, lease, "force-db-failure"))
        row = await self.db_row("SELECT requests_reserved, cost_reserved_microunits FROM activities WHERE id = %s", (spec.activity_id,))
        operation = await self.db_row("SELECT 1 AS found FROM activity_operations WHERE activity_id = %s", (spec.activity_id,))
        self.assertEqual(row, {"requests_reserved": 0, "cost_reserved_microunits": 0})
        self.assertIsNone(operation)


if __name__ == "__main__":
    unittest.main(verbosity=2)
