"""TASK-077 时间账本基础切片的真实 PostgreSQL 用例准备；不发送模型请求。

仅在存在专用测试 DSN（环境变量 RETROLUME_TIME_BUDGET_TEST_DATABASE_URL）时
运行；缺失即明确跳过，绝不回退任何用户 DSN。每例使用全新合成活动/来源 ID，
准备与清理只定向操作本例创建的行，不做全表 DELETE。
本卡只准备不运行：真实 PG 执行、004 迁移与数据库 CHECK/非空拒绝验证由后续
独立任务卡安排。settle_execution_window 仅按内部可信合成调用对待。

租约过期样本通过改写本例合成行自身的 lease_expires_at 数据值构造，属于
合成行前提，不是真实时钟回拨实验；不改本机或数据库系统时间。
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
import math
import os
import unittest
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row

from app.activities import (
    ActivityLedgerConflict,
    ActivitySpec,
    PostgresAdmissionLedger,
    SettleResult,
    SourceSnapshot,
)
from app.capabilities import Provider
from app.runtime import psycopg_compatible_loop_factory


DSN = os.environ.get("RETROLUME_TIME_BUDGET_TEST_DATABASE_URL", "")


class PsycopgLoopIsolatedAsyncioTestCase(unittest.IsolatedAsyncioTestCase):
    def _setupAsyncioRunner(self) -> None:
        assert self._asyncioRunner is None
        self._asyncioRunner = asyncio.Runner(
            debug=True,
            loop_factory=psycopg_compatible_loop_factory,
        )


@unittest.skipUnless(DSN, "仅在 RETROLUME_TIME_BUDGET_TEST_DATABASE_URL 专用合成 PostgreSQL 中运行")
class ActivityTimeBudgetPostgresTests(PsycopgLoopIsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.ledger = PostgresAdmissionLedger(DSN)
        self.activity_id = str(uuid4())
        self.source_id = str(uuid4())
        self.version_id = str(uuid4())

    async def asyncTearDown(self) -> None:
        """只删除本例合成的活动与来源行；顺序遵循外键依赖，失败如实抛出。"""
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            async with connection.transaction():
                for sql in (
                    "DELETE FROM activity_operations WHERE activity_id = %s",
                    "DELETE FROM activity_allowed_models WHERE activity_id = %s",
                    "DELETE FROM activity_scope_sources WHERE activity_id = %s",
                    "DELETE FROM activities WHERE id = %s",
                ):
                    await connection.execute(sql, (self.activity_id,))
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

    async def budget_row(self) -> dict:
        return await self.db_row(
            """SELECT status, execution_generation, executor_id, lease_expires_at,
                      max_running_seconds, running_reserved_seconds, running_settled_seconds,
                      last_settled_generation, last_settled_seconds
                 FROM activities WHERE id = %s""",
            (self.activity_id,),
        )

    async def build_activity(self, *, max_running_seconds: int = 200) -> tuple[ActivitySpec, object]:
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            async with connection.transaction():
                await connection.execute(
                    "INSERT INTO material_sources(id, title, revision) VALUES (%s, 'synthetic-077', 0)",
                    (self.source_id,),
                )
                await connection.execute(
                    """INSERT INTO material_versions(id, source_id, filename, format, sha256, size)
                         VALUES (%s, %s, 'synthetic-077.txt', 'txt', %s, 9)""",
                    (self.version_id, self.source_id, "d" * 64),
                )
                await connection.execute(
                    "UPDATE material_sources SET current_version = %s, revision = 1 WHERE id = %s",
                    (self.version_id, self.source_id),
                )
        spec = ActivitySpec(
            activity_id=self.activity_id,
            sources=(SourceSnapshot(self.source_id, self.version_id, 1),),
            deadline_at=datetime.now(timezone.utc) + timedelta(minutes=20),
            max_requests=16,
            max_cost_microunits=1600,
            reserve_cost_microunits=100,
            max_request_bytes=4096,
            max_output_tokens=256,
            max_running_seconds=max_running_seconds,
            allowed_models=((Provider.DEEPSEEK_CHAT_COMPLETIONS.value, "synthetic-model"),),
            allowed_tools=(),
            scope_revision=1,
        )
        await self.ledger.create_activity(spec)
        return spec

    async def expire_lease(self) -> None:
        # 改写本例合成行自身的租约到期数据值；不是真实时钟回拨实验。
        async with await psycopg.AsyncConnection.connect(DSN) as connection:
            await connection.execute(
                "UPDATE activities SET lease_expires_at = CURRENT_TIMESTAMP - interval '1 minute' WHERE id = %s",
                (self.activity_id,),
            )

    async def claim(self, *, window_seconds: int, executor: str = "worker-1"):
        return await self.ledger.claim_lease(
            self.activity_id, executor, lease_seconds=300, window_seconds=window_seconds
        )

    async def settle(self, lease, *, elapsed_seconds, executor: str | None = None, window: int | None = None):
        return await self.ledger.settle_execution_window(
            self.activity_id,
            executor or lease.executor_id,
            lease.execution_generation,
            window_seconds=window if window is not None else lease.window_seconds,
            elapsed_seconds=elapsed_seconds,
        )

    async def test_01_settle_normal_path_and_idempotent_retry(self) -> None:
        # 紧密场景 M200 / W100 / C20 → S20 / R0 / A180。
        await self.build_activity(max_running_seconds=200)
        lease = await self.claim(window_seconds=100)
        self.assertIsNotNone(lease)
        self.assertEqual(lease.window_seconds, 100)
        self.assertEqual(lease.execution_generation, 1)
        self.assertEqual(
            await self.settle(lease, elapsed_seconds=20),
            SettleResult.SETTLED,
        )
        self.assertEqual(
            await self.budget_row(),
            {
                "status": "pending",
                "execution_generation": 2,
                "executor_id": None,
                "lease_expires_at": None,
                "max_running_seconds": 200,
                "running_reserved_seconds": 0,
                "running_settled_seconds": 20,
                "last_settled_generation": 1,
                "last_settled_seconds": 20,
            },
        )
        # 相同最近已结算请求：幂等确认，不改账。
        self.assertEqual(
            await self.settle(lease, elapsed_seconds=20),
            SettleResult.ALREADY_SETTLED,
        )
        self.assertEqual((await self.budget_row())["running_settled_seconds"], 20)
        # 相同代次不同 C：冲突拒绝且不改账。
        with self.assertRaises(ActivityLedgerConflict):
            await self.settle(lease, elapsed_seconds=25)
        self.assertEqual((await self.budget_row())["running_settled_seconds"], 20)

    async def test_02_new_claim_after_settle_does_not_fold(self) -> None:
        # 已结算窗口（pending、R=0）不折叠；新认领不动 S。
        await self.build_activity(max_running_seconds=200)
        first = await self.claim(window_seconds=100)
        await self.settle(first, elapsed_seconds=20)
        second = await self.claim(window_seconds=50)
        self.assertIsNotNone(second)
        row = await self.budget_row()
        self.assertEqual(row["running_settled_seconds"], 20)
        self.assertEqual(row["running_reserved_seconds"], 50)
        self.assertEqual(row["execution_generation"], 3)
        self.assertEqual(row["status"], "running")

    async def test_03_stale_residual_fully_folded_on_reclaim(self) -> None:
        # 未结算崩溃残留按允许接续条件全额折叠：R100 → S100，再预扣新窗口。
        await self.build_activity(max_running_seconds=400)
        first = await self.claim(window_seconds=100)
        self.assertEqual(first.window_seconds, 100)
        await self.expire_lease()
        second = await self.claim(window_seconds=60)
        self.assertIsNotNone(second)
        self.assertEqual(second.window_seconds, 60)
        row = await self.budget_row()
        self.assertEqual(row["running_settled_seconds"], 100)
        self.assertEqual(row["running_reserved_seconds"], 60)
        self.assertEqual(row["execution_generation"], 2)
        self.assertEqual(row["status"], "running")

    async def test_04_fold_exhaustion_returns_none_and_closure_committed(self) -> None:
        # 折叠后 A=0：提交折叠与关闭，返回 None；再认领仍 None 且不写行。
        await self.build_activity(max_running_seconds=200)
        first = await self.claim(window_seconds=200)
        self.assertEqual(first.window_seconds, 200)
        await self.expire_lease()
        self.assertIsNone(await self.claim(window_seconds=100))
        self.assertEqual(
            await self.budget_row(),
            {
                "status": "pending",
                "execution_generation": 2,
                "executor_id": None,
                "lease_expires_at": None,
                "max_running_seconds": 200,
                "running_reserved_seconds": 0,
                "running_settled_seconds": 200,
                "last_settled_generation": None,
                "last_settled_seconds": None,
            },
        )
        # 已是 pending 且 A=0：不写任何行、代次不再递增。
        self.assertIsNone(await self.claim(window_seconds=100))
        self.assertEqual((await self.budget_row())["execution_generation"], 2)

    async def test_05_cancel_folds_and_repeat_is_idempotent(self) -> None:
        await self.build_activity(max_running_seconds=300)
        lease = await self.claim(window_seconds=100)
        self.assertEqual(await self.ledger.cancel_activity(self.activity_id), 2)
        row = await self.budget_row()
        self.assertEqual(row["status"], "cancelled")
        self.assertEqual(row["running_reserved_seconds"], 0)
        self.assertEqual(row["running_settled_seconds"], 100)
        # 重复取消不重复扣账。
        self.assertEqual(await self.ledger.cancel_activity(self.activity_id), 2)
        self.assertEqual((await self.budget_row())["running_settled_seconds"], 100)
        # 取消终态后认领仍按既有冲突拒绝，与预算耗尽 None 可区分。
        with self.assertRaises(ActivityLedgerConflict):
            await self.claim(window_seconds=100)

    async def test_06_late_settlement_for_old_generation_rejected(self) -> None:
        await self.build_activity(max_running_seconds=400)
        first = await self.claim(window_seconds=100)
        await self.expire_lease()
        second = await self.claim(window_seconds=100, executor="worker-2")
        self.assertIsNotNone(second)
        # 旧代次晚到：拒绝且不改账。
        with self.assertRaises(ActivityLedgerConflict):
            await self.settle(first, elapsed_seconds=20)
        # 当后代次执行者不匹配：同样拒绝。
        with self.assertRaises(ActivityLedgerConflict):
            await self.settle(second, elapsed_seconds=20, executor=first.executor_id)
        row = await self.budget_row()
        self.assertEqual(row["running_settled_seconds"], 100)
        self.assertEqual(row["running_reserved_seconds"], 100)
        # 正确的当代结算成功；随后旧代次重试已不是最近结算，拒绝。
        self.assertEqual(await self.settle(second, elapsed_seconds=20), SettleResult.SETTLED)
        row = await self.budget_row()
        self.assertEqual(row["running_settled_seconds"], 120)
        self.assertEqual(row["last_settled_generation"], second.execution_generation)
        with self.assertRaises(ActivityLedgerConflict):
            await self.settle(first, elapsed_seconds=20)
        # 当代次已结算的幂等重试不受已关闭状态影响。
        self.assertEqual(await self.settle(second, elapsed_seconds=20), SettleResult.ALREADY_SETTLED)

    async def test_07_parameter_validation_rejects_invalid_input(self) -> None:
        await self.build_activity(max_running_seconds=200)
        # ActivitySpec.max_running_seconds：bool/非整数/非正/超存储范围。
        for bad in (0, -1, True, "100", 2**31):
            spec = ActivitySpec(
                activity_id=str(uuid4()),
                sources=(SourceSnapshot(self.source_id, self.version_id, 1),),
                deadline_at=datetime.now(timezone.utc) + timedelta(minutes=20),
                max_requests=4,
                max_cost_microunits=400,
                reserve_cost_microunits=100,
                max_request_bytes=4096,
                max_output_tokens=256,
                max_running_seconds=bad,
                allowed_models=((Provider.DEEPSEEK_CHAT_COMPLETIONS.value, "synthetic-model"),),
            )
            with self.assertRaises(ValueError):
                await self.ledger.create_activity(spec)
        # claim_lease window_seconds：bool/非整数/越界。
        for bad in (0, 3601, True, "60"):
            with self.assertRaises(ValueError):
                await self.ledger.claim_lease(
                    self.activity_id, "worker-1", lease_seconds=300, window_seconds=bad
                )
        lease = await self.claim(window_seconds=30)
        # settle elapsed_seconds：bool/NaN/无穷/负数。
        for bad in (True, math.nan, math.inf, -0.5):
            with self.assertRaises(ValueError):
                await self.settle(lease, elapsed_seconds=bad)
        # settle window_seconds 与执行代次非法。
        for bad in (0, 3601, True):
            with self.assertRaises(ValueError):
                await self.settle(lease, elapsed_seconds=1, window=bad)
        for bad in (-1, True):
            with self.assertRaises(ValueError):
                await self.ledger.settle_execution_window(
                    self.activity_id, lease.executor_id, bad,
                    window_seconds=lease.window_seconds, elapsed_seconds=1,
                )
        # C > W：拒绝而不钳制超额（30.5s → C31 > W30）。
        with self.assertRaises(ValueError):
            await self.settle(lease, elapsed_seconds=30.5)
        self.assertEqual((await self.budget_row())["running_reserved_seconds"], 30)
        # 未知活动：冲突异常，与预算耗尽 None 可区分。
        with self.assertRaises(ActivityLedgerConflict):
            await self.ledger.settle_execution_window(
                str(uuid4()), lease.executor_id, 1,
                window_seconds=30, elapsed_seconds=1,
            )

    async def test_08_ceiling_rounding_zero_and_fold_reclaim_partial_window(self) -> None:
        await self.build_activity(max_running_seconds=200)
        # 向上取整：20.2 → C21。
        first = await self.claim(window_seconds=100)
        self.assertEqual(await self.settle(first, elapsed_seconds=20.2), SettleResult.SETTLED)
        self.assertEqual((await self.budget_row())["last_settled_seconds"], 21)
        self.assertEqual((await self.budget_row())["running_settled_seconds"], 21)
        # 真实零耗时：C=0 合法，S 不变。
        second = await self.claim(window_seconds=50)
        self.assertEqual(await self.settle(second, elapsed_seconds=0), SettleResult.SETTLED)
        row = await self.budget_row()
        self.assertEqual(row["last_settled_seconds"], 0)
        self.assertEqual(row["running_settled_seconds"], 21)
        # 有效租约不被抢占：冲突异常。
        third = await self.claim(window_seconds=100)
        with self.assertRaises(ActivityLedgerConflict):
            await self.claim(window_seconds=100, executor="worker-2")
        # 过期残留全额折叠（R100 → S121）后 A=79，仍可取得 W_eff=79 的新租约，
        # 不因"余额不足全额窗口"误判为预算耗尽（预算耗尽路径由 test_04 覆盖）。
        await self.expire_lease()
        fourth = await self.claim(window_seconds=100, executor="worker-2")
        self.assertIsNotNone(fourth)
        self.assertEqual(fourth.window_seconds, 79)
        row = await self.budget_row()
        self.assertEqual(row["max_running_seconds"], 200)
        self.assertEqual(row["running_settled_seconds"], 121)
        self.assertEqual(row["running_reserved_seconds"], 79)
        # 折叠加新预扣后可用余额为 0：M - S - R = 0。
        self.assertEqual(
            row["max_running_seconds"]
            - row["running_settled_seconds"]
            - row["running_reserved_seconds"],
            0,
        )
        self.assertEqual(row["status"], "running")
        # 租约身份/代次与返回一致；不硬编码 generation 数字。
        self.assertEqual(row["execution_generation"], fourth.execution_generation)
        self.assertEqual(row["executor_id"], fourth.executor_id)
        # 未知活动：冲突异常，与预算耗尽 None 可区分。
        with self.assertRaises(ActivityLedgerConflict):
            await self.ledger.claim_lease(
                str(uuid4()), "worker-1", lease_seconds=300, window_seconds=100
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
