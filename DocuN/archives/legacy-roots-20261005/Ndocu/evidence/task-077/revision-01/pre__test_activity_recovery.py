"""TASK-068 的旧代次未决操作发现/收敛真实 PostgreSQL 用例；不发送模型请求。

仅在存在专用测试 DSN（环境变量 RETROLUME_TASK_068_DATABASE_URL）时运行；
不回退到任何用户数据库连接。每例使用全新合成活动/来源 ID，
准备与清理都只定向操作本例创建的行，不做全表 DELETE。
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
import os
import unittest
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row

from app.activities import (
    ActivityLedgerConflict,
    ActivitySpec,
    PostgresAdmissionLedger,
    SourceSnapshot,
    UnresolvedOperation,
)
from app.capabilities import (
    AdmissionDenied,
    AdmissionIntent,
    CallContext,
    LedgerDisposition,
    LedgerOutcome,
    Provider,
)
from app.runtime import psycopg_compatible_loop_factory


DSN = os.environ.get("RETROLUME_TASK_068_DATABASE_URL", "")


class PsycopgLoopIsolatedAsyncioTestCase(unittest.IsolatedAsyncioTestCase):
    def _setupAsyncioRunner(self) -> None:
        assert self._asyncioRunner is None
        self._asyncioRunner = asyncio.Runner(
            debug=True,
            loop_factory=psycopg_compatible_loop_factory,
        )


@unittest.skipUnless(DSN, "仅在 TASK-068 专用合成 PostgreSQL 中运行")
class ActivityRecoveryPostgresTests(PsycopgLoopIsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.ledger = PostgresAdmissionLedger(DSN)
        self.activity_id = str(uuid4())
        self.source_id = str(uuid4())
        self.version_id = str(uuid4())
        # 本例额外创建的活动 ID（如 test_04 的隔离对照活动）。
        # 创建前先登记：即使创建中途失败，收尾也按 ID 清理，残留行为空操作。
        self.extra_activity_ids: list[str] = []

    async def asyncTearDown(self) -> None:
        """只删除本例合成的活动与来源行；不触碰任何其他数据。

        删除顺序遵循外键依赖：活动操作/模型许可/来源关联 → 活动；
        随后必须先解除本例 source.current_version 对版本的引用
        （001 的 material_current_version_source 立即组合外键），
        再删版本，最后删来源。清理失败如实抛出，不吞掉。
        """
        activity_ids = [self.activity_id, *self.extra_activity_ids]
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            async with connection.transaction():
                for activity_id in activity_ids:
                    for sql in (
                        "DELETE FROM activity_operations WHERE activity_id = %s",
                        "DELETE FROM activity_allowed_models WHERE activity_id = %s",
                        "DELETE FROM activity_scope_sources WHERE activity_id = %s",
                        "DELETE FROM activities WHERE id = %s",
                    ):
                        await connection.execute(sql, (activity_id,))
                await connection.execute(
                    "UPDATE material_sources SET current_version = NULL WHERE id = %s",
                    (self.source_id,),
                )
                await connection.execute("DELETE FROM material_versions WHERE id = %s", (self.version_id,))
                await connection.execute("DELETE FROM material_sources WHERE id = %s", (self.source_id,))

    async def db_rows(self, sql: str, params: tuple = ()) -> list[dict]:
        async with await psycopg.AsyncConnection.connect(DSN, row_factory=dict_row) as connection:
            cursor = await connection.execute(sql, params)
            return list(await cursor.fetchall())

    async def db_row(self, sql: str, params: tuple = ()) -> dict | None:
        rows = await self.db_rows(sql, params)
        return rows[0] if rows else None

    async def build_activity(self) -> tuple[ActivitySpec, object, SourceSnapshot]:
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            async with connection.transaction():
                await connection.execute(
                    "INSERT INTO material_sources(id, title, revision) VALUES (%s, 'synthetic-068', 0)",
                    (self.source_id,),
                )
                await connection.execute(
                    """INSERT INTO material_versions(id, source_id, filename, format, sha256, size)
                         VALUES (%s, %s, 'synthetic-068.txt', 'txt', %s, 9)""",
                    (self.version_id, self.source_id, "c" * 64),
                )
                await connection.execute(
                    "UPDATE material_sources SET current_version = %s, revision = 1 WHERE id = %s",
                    (self.version_id, self.source_id),
                )
        source = SourceSnapshot(self.source_id, self.version_id, 1)
        spec = ActivitySpec(
            activity_id=self.activity_id,
            sources=(source,),
            deadline_at=datetime.now(timezone.utc) + timedelta(minutes=20),
            max_requests=16,
            max_cost_microunits=1600,
            reserve_cost_microunits=100,
            max_request_bytes=4096,
            max_output_tokens=256,
            max_running_seconds=3600,
            allowed_models=((Provider.DEEPSEEK_CHAT_COMPLETIONS.value, "synthetic-model"),),
            allowed_tools=(),
            scope_revision=1,
        )
        await self.ledger.create_activity(spec)
        lease = await self.ledger.claim_lease(
            spec.activity_id, "worker-1", lease_seconds=300, window_seconds=300
        )
        self.assertIsNotNone(lease)
        return spec, lease, source

    @staticmethod
    def intent(spec: ActivitySpec, lease, operation_id: str) -> AdmissionIntent:
        return AdmissionIntent(
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

    async def expire_lease(self, spec: ActivitySpec) -> None:
        # 留 1 分钟余量，避免测试容器与应用进程之间的时钟偏差干扰判定
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            await connection.execute(
                "UPDATE activities SET lease_expires_at = CURRENT_TIMESTAMP - interval '1 minute' WHERE id = %s",
                (spec.activity_id,),
            )

    async def reclaim_next_generation(self, spec: ActivitySpec, *, executor: str = "worker-2"):
        await self.expire_lease(spec)
        lease = await self.ledger.claim_lease(
            spec.activity_id, executor, lease_seconds=300, window_seconds=300
        )
        self.assertIsNotNone(lease)
        return lease

    async def test_01_valid_lease_does_not_block_finding_and_converging_old_generation(self) -> None:
        spec, lease, _ = await self.build_activity()
        await self.ledger.admit(self.intent(spec, lease, "old-reserved-1"))
        dispatched = await self.ledger.admit(self.intent(spec, lease, "old-dispatched-1"))
        await self.ledger.mark_dispatch_started(dispatched)
        new_lease = await self.reclaim_next_generation(spec)
        self.assertEqual(new_lease.execution_generation, lease.execution_generation + 1)
        await self.ledger.admit(self.intent(spec, new_lease, "current-2"))

        found = await self.ledger.list_unresolved_operations(spec.activity_id)
        self.assertEqual([item.operation_id for item in found], ["current-2", "old-dispatched-1", "old-reserved-1"])
        self.assertTrue(all(isinstance(item, UnresolvedOperation) for item in found))
        generations = {item.operation_id: item.execution_generation for item in found}
        self.assertEqual(generations, {"current-2": 2, "old-dispatched-1": 1, "old-reserved-1": 1})
        by_id = {item.operation_id: item for item in found}
        self.assertIsNone(by_id["old-reserved-1"].dispatch_started_at)
        self.assertIsNotNone(by_id["old-dispatched-1"].dispatch_started_at)
        self.assertIsNotNone(by_id["current-2"].admission_id)

        changed = await self.ledger.recover_obsolete_operations(spec.activity_id)
        self.assertEqual(changed, 2)
        rows = {
            row["operation_id"]: row
            for row in await self.db_rows(
                "SELECT operation_id, state, disposition, error_code, execution_generation,"
                " dispatch_started_at, recorded_at"
                " FROM activity_operations WHERE activity_id = %s",
                (spec.activity_id,),
            )
        }
        self.assertEqual(rows["old-reserved-1"]["state"], "unknown")
        self.assertEqual(rows["old-dispatched-1"]["state"], "unknown")
        self.assertEqual(rows["old-reserved-1"]["disposition"], "unknown")
        self.assertEqual(rows["old-dispatched-1"]["error_code"], "executor_lost")
        self.assertIsNotNone(rows["old-dispatched-1"]["dispatch_started_at"])
        self.assertIsNotNone(rows["old-dispatched-1"]["recorded_at"])
        self.assertEqual(rows["current-2"]["state"], "reserved")
        self.assertIsNone(rows["current-2"]["disposition"])
        self.assertEqual(rows["current-2"]["execution_generation"], 2)

        remaining = await self.ledger.list_unresolved_operations(spec.activity_id)
        self.assertEqual([item.operation_id for item in remaining], ["current-2"])

    async def test_02_repeat_converge_is_noop_and_invalid_input_rejected(self) -> None:
        spec, lease, _ = await self.build_activity()
        await self.ledger.admit(self.intent(spec, lease, "old-1"))
        await self.reclaim_next_generation(spec)
        self.assertEqual(await self.ledger.recover_obsolete_operations(spec.activity_id), 1)
        self.assertEqual(await self.ledger.recover_obsolete_operations(spec.activity_id), 0)
        self.assertEqual(await self.ledger.recover_obsolete_operations(spec.activity_id, error_code="again"), 0)
        row = await self.db_row(
            "SELECT state, error_code FROM activity_operations WHERE activity_id = %s",
            (spec.activity_id,),
        )
        self.assertEqual(row, {"state": "unknown", "error_code": "executor_lost"})
        with self.assertRaises(ActivityLedgerConflict):
            await self.ledger.recover_obsolete_operations(str(uuid4()))
        with self.assertRaises(ValueError):
            await self.ledger.recover_obsolete_operations(spec.activity_id, error_code="bad code!")
        for bad_limit in (0, 201, True, "5"):
            with self.assertRaises(ValueError):
                await self.ledger.list_unresolved_operations(spec.activity_id, limit=bad_limit)
        with self.assertRaises(ValueError):
            await self.ledger.list_unresolved_operations("not-a-uuid")
        with self.assertRaises(ValueError):
            await self.ledger.list_unresolved_operations(spec.activity_id, after_operation_id="bad op!")

    async def test_03_existing_terminals_kept_and_reservation_not_refunded(self) -> None:
        spec, lease, _ = await self.build_activity()
        received = await self.ledger.admit(self.intent(spec, lease, "old-received-1"))
        await self.ledger.mark_dispatch_started(received)
        await self.ledger.record_outcome(
            received,
            LedgerOutcome(
                LedgerDisposition.RECEIVED,
                returned_model="synthetic-model",
                finish_reason="stop",
                prompt_tokens=7,
                completion_tokens=3,
                response_bytes=42,
            ),
        )
        unknown = await self.ledger.admit(self.intent(spec, lease, "old-unknown-1"))
        await self.ledger.mark_dispatch_started(unknown)
        await self.ledger.record_outcome(
            unknown, LedgerOutcome(LedgerDisposition.UNKNOWN, error_code="worker_died")
        )
        await self.ledger.admit(self.intent(spec, lease, "old-reserved-1"))
        await self.reclaim_next_generation(spec)

        changed = await self.ledger.recover_obsolete_operations(spec.activity_id)
        self.assertEqual(changed, 1)
        rows = {
            row["operation_id"]: row
            for row in await self.db_rows(
                "SELECT operation_id, state, error_code, prompt_tokens FROM activity_operations"
                " WHERE activity_id = %s ORDER BY operation_id",
                (spec.activity_id,),
            )
        }
        self.assertEqual(rows["old-received-1"]["state"], "received")
        self.assertEqual(rows["old-received-1"]["prompt_tokens"], 7)
        self.assertEqual(rows["old-unknown-1"]["state"], "unknown")
        self.assertEqual(rows["old-unknown-1"]["error_code"], "worker_died")
        self.assertEqual(rows["old-reserved-1"]["state"], "unknown")
        budget = await self.db_row(
            "SELECT requests_reserved, cost_reserved_microunits FROM activities WHERE id = %s",
            (spec.activity_id,),
        )
        self.assertEqual(budget, {"requests_reserved": 3, "cost_reserved_microunits": 300})

    async def test_04_listing_is_bounded_paginated_and_isolated_per_activity(self) -> None:
        spec, lease, source = await self.build_activity()
        for index in range(7):
            await self.ledger.admit(self.intent(spec, lease, f"op-{index:02d}"))
        second_lease = await self.reclaim_next_generation(spec)
        await self.ledger.admit(self.intent(spec, second_lease, "op-90"))

        other = ActivitySpec(
            activity_id=str(uuid4()),
            sources=(source,),
            deadline_at=datetime.now(timezone.utc) + timedelta(minutes=20),
            max_requests=16,
            max_cost_microunits=1600,
            reserve_cost_microunits=100,
            max_request_bytes=4096,
            max_output_tokens=256,
            allowed_models=((Provider.DEEPSEEK_CHAT_COMPLETIONS.value, "synthetic-model"),),
            allowed_tools=(),
            scope_revision=1,
        )
        # 创建前登记，消除"创建成功但后续准备步骤失败"时无人清理的窗口；
        # 创建本身失败会回滚，收尾按 ID 删除为空操作，重复清理无害。
        self.extra_activity_ids.append(other.activity_id)
        await self.ledger.create_activity(other)
        other_lease = await self.ledger.claim_lease(other.activity_id, "worker-1", lease_seconds=300)
        await self.ledger.admit(self.intent(other, other_lease, "xb-op-1"))
        await self.ledger.admit(self.intent(other, other_lease, "xb-op-2"))
        await self.reclaim_next_generation(other)
        full = await self.ledger.list_unresolved_operations(spec.activity_id)
        self.assertEqual(
            [item.operation_id for item in full],
            [f"op-{index:02d}" for index in range(7)] + ["op-90"],
        )
        page = await self.ledger.list_unresolved_operations(spec.activity_id, limit=3)
        self.assertEqual([item.operation_id for item in page], ["op-00", "op-01", "op-02"])
        collected: list[str] = []
        cursor = None
        while True:
            rows = await self.ledger.list_unresolved_operations(
                spec.activity_id, limit=3, after_operation_id=cursor
            )
            if not rows:
                break
            self.assertLessEqual(len(rows), 3)
            collected.extend(item.operation_id for item in rows)
            cursor = rows[-1].operation_id
        self.assertEqual(collected, [item.operation_id for item in full])
        self.assertEqual(len(collected), len(set(collected)))

        across = await self.ledger.list_unresolved_operations(
            other.activity_id, limit=200, after_operation_id="op-90"
        )
        self.assertEqual([item.operation_id for item in across], ["xb-op-1", "xb-op-2"])
        other_full = await self.ledger.list_unresolved_operations(other.activity_id)
        self.assertEqual([item.operation_id for item in other_full], ["xb-op-1", "xb-op-2"])

        changed = await self.ledger.recover_obsolete_operations(spec.activity_id)
        self.assertEqual(changed, 7)
        other_rows = await self.db_rows(
            "SELECT state FROM activity_operations WHERE activity_id = %s ORDER BY operation_id",
            (other.activity_id,),
        )
        self.assertEqual([row["state"] for row in other_rows], ["reserved", "reserved"])

    async def test_05_late_permit_cannot_overwrite_recovered_unknown(self) -> None:
        spec, lease, _ = await self.build_activity()
        permit = await self.ledger.admit(self.intent(spec, lease, "old-1"))
        await self.ledger.mark_dispatch_started(permit)
        await self.reclaim_next_generation(spec)
        self.assertEqual(await self.ledger.recover_obsolete_operations(spec.activity_id), 1)

        with self.assertRaises(AdmissionDenied):
            await self.ledger.record_outcome(
                permit,
                LedgerOutcome(
                    LedgerDisposition.RECEIVED,
                    returned_model="synthetic-model",
                    finish_reason="stop",
                    prompt_tokens=1,
                    completion_tokens=1,
                    response_bytes=10,
                ),
            )
        with self.assertRaises(AdmissionDenied):
            await self.ledger.record_outcome(
                permit, LedgerOutcome(LedgerDisposition.UNKNOWN, error_code="late_note")
            )
        await self.ledger.record_outcome(
            permit, LedgerOutcome(LedgerDisposition.UNKNOWN, error_code="executor_lost")
        )
        row = await self.db_row(
            """SELECT state, disposition, error_code, prompt_tokens, completion_tokens, response_bytes
                   FROM activity_operations WHERE admission_id = %s""",
            (permit.admission_id,),
        )
        self.assertEqual(
            row,
            {
                "state": "unknown",
                "disposition": "unknown",
                "error_code": "executor_lost",
                "prompt_tokens": None,
                "completion_tokens": None,
                "response_bytes": None,
            },
        )
        budget = await self.db_row(
            "SELECT requests_reserved, cost_reserved_microunits FROM activities WHERE id = %s",
            (spec.activity_id,),
        )
        self.assertEqual(budget, {"requests_reserved": 1, "cost_reserved_microunits": 100})

    async def test_06_bounded_single_batch_converges_incrementally(self) -> None:
        """TASK-071：limit=2 连续收敛 5 个旧未决项得到 2/2/1/0，逐批只动已选行。

        当前代次操作、活动代次与预算在整个收敛过程中保持不变；
        末尾补 recover_obsolete_operations 自身 limit 参数的非法拒绝。
        """
        spec, lease, _ = await self.build_activity()
        old_ids = [f"old-op-{index:02d}" for index in range(5)]
        for operation_id in old_ids:
            await self.ledger.admit(self.intent(spec, lease, operation_id))
        new_lease = await self.reclaim_next_generation(spec)
        await self.ledger.admit(self.intent(spec, new_lease, "cur-op-1"))

        async def operation_states() -> dict[str, str]:
            rows = await self.db_rows(
                "SELECT operation_id, state FROM activity_operations WHERE activity_id = %s",
                (spec.activity_id,),
            )
            return {row["operation_id"]: row["state"] for row in rows}

        async def assert_invariants(expected: dict[str, str]) -> None:
            self.assertEqual(await operation_states(), expected)
            # 当后代次/预算不变：代次仍为 2，6 次 admit 的预留不因收敛退还。
            snapshot = await self.db_row(
                "SELECT execution_generation, requests_reserved, cost_reserved_microunits"
                " FROM activities WHERE id = %s",
                (spec.activity_id,),
            )
            self.assertEqual(
                snapshot,
                {"execution_generation": 2, "requests_reserved": 6, "cost_reserved_microunits": 600},
            )

        # 批 1：limit=2 只收敛排序最前的 old-op-00/old-op-01。
        self.assertEqual(await self.ledger.recover_obsolete_operations(spec.activity_id, limit=2), 2)
        await assert_invariants(
            {
                "old-op-00": "unknown",
                "old-op-01": "unknown",
                "old-op-02": "reserved",
                "old-op-03": "reserved",
                "old-op-04": "reserved",
                "cur-op-1": "reserved",
            }
        )

        # 批 2：继续收敛 old-op-02/old-op-03。
        self.assertEqual(await self.ledger.recover_obsolete_operations(spec.activity_id, limit=2), 2)
        await assert_invariants(
            {
                "old-op-00": "unknown",
                "old-op-01": "unknown",
                "old-op-02": "unknown",
                "old-op-03": "unknown",
                "old-op-04": "reserved",
                "cur-op-1": "reserved",
            }
        )

        # 批 3：只剩 old-op-04，返回 1 而不是 limit。
        self.assertEqual(await self.ledger.recover_obsolete_operations(spec.activity_id, limit=2), 1)
        await assert_invariants(
            {
                "old-op-00": "unknown",
                "old-op-01": "unknown",
                "old-op-02": "unknown",
                "old-op-03": "unknown",
                "old-op-04": "unknown",
                "cur-op-1": "reserved",
            }
        )

        # 批 4：返回 0 表示本批无匹配，不产生任何写入。
        self.assertEqual(await self.ledger.recover_obsolete_operations(spec.activity_id, limit=2), 0)
        rows = {
            row["operation_id"]: row
            for row in await self.db_rows(
                "SELECT operation_id, state, disposition, error_code, recorded_at"
                " FROM activity_operations WHERE activity_id = %s",
                (spec.activity_id,),
            )
        }
        for operation_id in old_ids:
            self.assertEqual(rows[operation_id]["state"], "unknown")
            self.assertEqual(rows[operation_id]["disposition"], "unknown")
            self.assertEqual(rows[operation_id]["error_code"], "executor_lost")
            self.assertIsNotNone(rows[operation_id]["recorded_at"])
        self.assertEqual(rows["cur-op-1"]["state"], "reserved")
        self.assertIsNone(rows["cur-op-1"]["error_code"])
        self.assertIsNone(rows["cur-op-1"]["recorded_at"])
        self.assertEqual(
            [item.operation_id for item in await self.ledger.list_unresolved_operations(spec.activity_id)],
            ["cur-op-1"],
        )

        # limit 参数校验：bool/0/201/非 int 一律 ValueError，不静默截断。
        for bad_limit in (0, 201, True, "2"):
            with self.assertRaises(ValueError):
                await self.ledger.recover_obsolete_operations(spec.activity_id, limit=bad_limit)


if __name__ == "__main__":
    unittest.main(verbosity=2)
