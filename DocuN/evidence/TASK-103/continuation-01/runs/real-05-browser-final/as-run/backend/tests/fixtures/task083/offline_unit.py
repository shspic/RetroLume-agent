"""TASK-083 补足轮01纯单元；只用内存替身，不创建OS进程/Job或连接DB。"""

from __future__ import annotations

import asyncio
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch
from uuid import uuid4


BACKEND = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(BACKEND))

from app.activities import ActivityLease, CloseResult, PostgresAdmissionLedger, SettleResult, WindowSnapshot
from app.worker.launcher import run_supervised_window
from app.worker.command import WorkerCommand
from app.worker.gate import GateClosed
from app.worker.session import SessionConfig, SingleWindowSupervisor, ManagerDeadline
from app.worker.worker_main import run_controlled_worker, run_internal_task


class Ledger:
    def __init__(self, *, window=6, claim_error=None, cancelled=False, settle_lost_once=False):
        self.window = window
        self.claim_error = claim_error
        self.cancelled = cancelled
        self.settle_lost_once = settle_lost_once
        self.events = []

    async def inspect_window(self, activity_id):
        self.events.append("inspect")
        return WindowSnapshot("cancelled" if self.cancelled else "pending", 0, 0, True)

    async def claim_lease(self, activity_id, executor_id, *, lease_seconds, window_seconds, running_owner_session_id=None, expected_previous_generation=None):
        self.events.append("claim")
        if self.claim_error:
            raise self.claim_error
        return ActivityLease(activity_id, executor_id, 1, 1, datetime.now(timezone.utc) + timedelta(seconds=6), self.window, running_owner_session_id)

    async def begin_window_close(self, activity_id, executor_id, execution_generation):
        self.events.append("close_db")
        return CloseResult.CLOSED

    async def settle_execution_window(self, activity_id, executor_id, execution_generation, *, window_seconds, elapsed_seconds):
        self.events.append("settle")
        if self.settle_lost_once:
            self.settle_lost_once = False
            raise TimeoutError("committed response lost")
        return SettleResult.ALREADY_SETTLED if self.events.count("settle") > 1 else SettleResult.SETTLED


class _TestClock:
    """test_05专用的测试局部单调时钟：读取返回固定值，仅显式advance推进。

    经patch替换session与本测试模块引用的time，with结束即恢复；
    不触碰asyncio内建时钟或其他测试的全局时间。
    """

    def __init__(self, start_ns=1_000_000_000_000):
        self.now_ns = start_ns

    def monotonic_ns(self):
        return self.now_ns

    def advance(self, ns):
        self.now_ns += ns


class Owner:
    fail_close = False

    def __init__(self, *args, **kwargs):
        pass

    def close(self):
        if self.fail_close:
            raise RuntimeError("owner close failed")


class FakeJob:
    def __init__(self, *, hang=False, terminate_error=False, close_error=False, external_events=None, clock=None):
        self.name = "Local\\SyntheticJob"
        self.hang = hang
        self.terminated = False
        self.terminate_error = terminate_error
        self.close_error = close_error
        self.external_events = external_events
        self.clock = clock  # 注入测试局部可控时钟时，用确定性推进代替2ms真实睡眠。
        self.events = []
        self.sleep_before_ns = None
        self.sleep_after_ns = None

    def spawn_suspended(self, command, *, cwd):
        self.events.append("spawn_suspended")
        return 123

    def process_creation_time_100ns(self):
        return 1

    def resume(self):
        self.events.append("resume")

    def wait_empty_until(self, deadline):
        self.events.append("query")
        if not self.hang and not self.terminated:
            if self.clock is not None:
                # 确定性正耗时：可控时钟显式推进0.4s（ceil(Δ)=1秒），消除对
                # 2ms真实睡眠跨时钟刻度的依赖；只影响注入本钟的用例。
                self.sleep_before_ns = self.clock.monotonic_ns()
                self.clock.advance(400_000_000)
                self.sleep_after_ns = self.clock.monotonic_ns()
            else:
                self.sleep_before_ns = time.monotonic_ns()
                time.sleep(0.002)  # 纯替身模拟正耗时；真实C0仍拒绝部分退款。
                self.sleep_after_ns = time.monotonic_ns()
        return not self.hang or self.terminated

    def terminate(self):
        self.events.append("terminate")
        if self.terminate_error:
            raise RuntimeError("terminate failed")
        self.terminated = True

    def primary_exit_code(self):
        return 0

    def close(self):
        self.events.append("close_job")
        if self.external_events is not None:
            self.external_events.append("job_closed")
        if self.close_error:
            raise RuntimeError("job close failed")


class OfflineRepairTests(unittest.IsolatedAsyncioTestCase):
    def config(self):
        return SessionConfig(window_seconds=6, request_timeout_seconds=0.5, stop_grace_seconds=1,
                             startup_limit_seconds=2, manager_db_timeout_seconds=0.5,
                             cleanup_seconds=1, mutex_wait_seconds=0.5, manager_overhead_seconds=8)

    def command(self):
        return WorkerCommand()

    async def run_fake(self, ledger, job=None, *, owner=Owner, deadline_offset=20):
        with patch("app.worker.session.current_process_session_id", return_value=1), patch("app.worker.session.ActivityMutex", owner), patch(
            "app.worker.session.NamedJob.create", side_effect=([job] if job is not None else AssertionError("must not spawn"))
        ):
            return await SingleWindowSupervisor(ledger, self.config()).run_once(
                str(uuid4()), "worker-1", self.command(), run_tag="offline-unit",
                manager_deadline_ns=time.monotonic_ns() + int(deadline_offset * 1e9),
            )

    async def test_01_command_data_rejects_callable_and_expired_manager_never_spawns(self):
        ledger = Ledger()
        supervisor = SingleWindowSupervisor(ledger, self.config())
        with self.assertRaises(TypeError):
            await supervisor.run_once(str(uuid4()), "worker-1", lambda _: [sys.executable],
                                      run_tag="offline-unit", manager_deadline_ns=time.monotonic_ns() + 1_000_000_000)
        with self.assertRaises(ManagerDeadline):
            await supervisor.run_once(str(uuid4()), "worker-1", self.command(),
                                      run_tag="offline-unit", manager_deadline_ns=time.monotonic_ns() - 1)
        self.assertEqual(ledger.events, [])

    async def test_02_partial_window_early_exit_reports_cleanup_failure_and_full_reservation(self):
        class BadOwner(Owner):
            fail_close = True
        result = await self.run_fake(Ledger(window=2), owner=BadOwner)
        self.assertEqual(result.state, "failed_closed")
        self.assertEqual((result.settled_seconds, result.reserved_seconds, result.pending_fold_seconds), (0, 2, 2))
        self.assertTrue(result.cleanup_incomplete)
        self.assertIn("owner_close:RuntimeError", result.cleanup_errors)

    async def test_03_cancellation_preserves_diagnostic_and_cleans_owner(self):
        ledger = Ledger(claim_error=asyncio.CancelledError())
        with self.assertRaises(asyncio.CancelledError) as caught:
            await self.run_fake(ledger)
        result = caught.exception.session_outcome
        self.assertEqual(result.state, "cancelled_by_caller")
        self.assertEqual((result.reserved_seconds, result.settled_seconds), (None, None))
        self.assertFalse(result.cleanup_incomplete)

    async def test_04_claim_response_lost_has_no_job_and_no_false_charge(self):
        result = await self.run_fake(Ledger(claim_error=RuntimeError("response lost")))
        self.assertEqual(result.state, "failed_closed")
        self.assertEqual((result.reserved_seconds, result.settled_seconds, result.pending_fold_seconds), (None, None, None))
        self.assertIsNone(result.job_name)

    async def test_05_early_success_uses_tree_zero_close_then_same_g_settle_retry(self):
        clock = _TestClock()
        ledger = Ledger(settle_lost_once=True)
        job = FakeJob(external_events=ledger.events, clock=clock)
        module_name = sys.modules[__name__].__name__  # 脚本直跑时为__main__。
        with patch("app.worker.session.time", clock), patch(f"{module_name}.time", clock):
            result = await self.run_fake(ledger, job)
        session_module = sys.modules["app.worker.session"]
        locations = {}
        for label, source in (("session", Path(session_module.__file__)), ("test", Path(__file__))):
            locations[label] = {"path": str(source.resolve()), "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}
        print("TASK083_05_DIAGNOSTIC " + json.dumps({
            "imports": locations, "state": result.state,
            "t0_ns": result.timing_diagnostic[0] if result.timing_diagnostic else None,
            "t1_ns": result.timing_diagnostic[1] if result.timing_diagnostic else None,
            "delta_ns": result.timing_diagnostic[2] if result.timing_diagnostic else None,
            "observed": result.timing_diagnostic[3] if result.timing_diagnostic else None,
            "window": result.timing_diagnostic[4] if result.timing_diagnostic else ledger.window,
            "job_events": job.events,
            "sleep_before_ns": job.sleep_before_ns, "sleep_after_ns": job.sleep_after_ns,
            "elapsed_seconds": result.elapsed_seconds,
        }, sort_keys=True), flush=True)
        self.assertEqual(result.state, "settled")
        t0_ns, t1_ns, delta_ns, observed, window = result.timing_diagnostic
        self.assertGreater(t1_ns, t0_ns)  # 确定性时钟下t1>t0恒成立。
        self.assertEqual(delta_ns, 400_000_000)
        self.assertEqual(observed, 1)  # ceil(Δ)=1
        self.assertEqual(window, 6)  # W=6
        self.assertEqual((result.settled_seconds, result.reserved_seconds, result.pending_fold_seconds), (1, 0, 0))
        self.assertEqual(result.active_processes_at_end, 0)
        self.assertIn("close_job", job.events)
        # 先树0再关门：job_closed先于close_db；同G结算重试：settle两次。
        self.assertLess(ledger.events.index("job_closed"), ledger.events.index("close_db"))
        self.assertEqual(ledger.events, ["inspect", "claim", "job_closed", "close_db", "settle", "settle"])

    async def test_06_timeout_or_cleanup_failure_never_refunds(self):
        result = await self.run_fake(Ledger(), FakeJob(hang=True))
        self.assertEqual(result.state, "stopped_at_deadline")
        self.assertEqual((result.settled_seconds, result.reserved_seconds, result.pending_fold_seconds), (0, 6, 6))
        broken = await self.run_fake(Ledger(), FakeJob(hang=True, terminate_error=True, close_error=True))
        self.assertEqual(broken.state, "failed_closed")
        self.assertTrue(broken.cleanup_incomplete)
        self.assertEqual((broken.settled_seconds, broken.reserved_seconds), (0, 6))
        self.assertIn("job_close:RuntimeError", broken.cleanup_errors)

    async def test_07_controlled_worker_gateway_chain_drains_marked_call(self):
        class Gateway:
            def __init__(self):
                self.marked = asyncio.Event()
                self.release = asyncio.Event()
                self.events = []

            async def call(self, context, request):
                self.events.extend(("admit", "mark"))
                self.marked.set()
                await self.release.wait()
                self.events.extend(("send", "record"))
                return "done"

        gateway = Gateway()
        captured = []

        async def work(gate):
            captured.append(gate)
            asyncio.create_task(gate.call(None, None))
            await gateway.marked.wait()

        runner = asyncio.create_task(run_controlled_worker(gateway, work, drain_timeout_seconds=1))
        await gateway.marked.wait()
        for _ in range(10):
            if captured[0].closed:
                break
            await asyncio.sleep(0)
        self.assertTrue(captured[0].closed)
        self.assertFalse(runner.done())
        self.assertEqual(gateway.events, ["admit", "mark"])
        with self.assertRaises(GateClosed):
            await captured[0].call(None, None)
        gateway.release.set()
        await runner
        self.assertEqual(gateway.events, ["admit", "mark", "send", "record"])
        with self.assertRaises(GateClosed):
            await captured[0].call(None, None)


# The old multiprocessing launcher fakes were retired with the fixed SUP handoff.


class FixedEntryTests(unittest.IsolatedAsyncioTestCase):
    async def test_12_fixed_command_and_injected_gateway_pass_through_gate(self):
        with self.assertRaises(TypeError):
            WorkerCommand(sys._base_executable, ("-c", "pass"), str(BACKEND))
        with self.assertRaises(ValueError):
            WorkerCommand("arbitrary")
        self.assertEqual(WorkerCommand("one_call").argv()[0], str(BACKEND / ".venv" / "Scripts" / "python.exe"))
        self.assertEqual(WorkerCommand("one_call").argv()[2:4], ["-m", "app.worker.worker_main"])

        class Gateway:
            def __init__(self): self.calls = 0
            async def call(self, context, request):
                self.calls += 1
                return "synthetic"
        gateway = Gateway()
        await run_internal_task(gateway, "one_call")
        self.assertEqual(gateway.calls, 1)



if __name__ == "__main__":
    unittest.main(verbosity=2)


