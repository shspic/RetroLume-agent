"""TASK-083 补足轮01纯单元；只用内存替身，不创建OS进程/Job或连接DB。"""

from __future__ import annotations

import asyncio
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
from app.worker.worker_main import run_controlled_worker


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

    async def claim_lease(self, activity_id, executor_id, *, lease_seconds, window_seconds):
        self.events.append("claim")
        if self.claim_error:
            raise self.claim_error
        return ActivityLease(activity_id, executor_id, 1, 1, datetime.now(timezone.utc) + timedelta(seconds=6), self.window)

    async def begin_window_close(self, activity_id, executor_id, execution_generation):
        self.events.append("close_db")
        return CloseResult.CLOSED

    async def settle_execution_window(self, activity_id, executor_id, execution_generation, *, window_seconds, elapsed_seconds):
        self.events.append("settle")
        if self.settle_lost_once:
            self.settle_lost_once = False
            raise TimeoutError("committed response lost")
        return SettleResult.ALREADY_SETTLED if self.events.count("settle") > 1 else SettleResult.SETTLED


class Owner:
    fail_close = False

    def __init__(self, *args, **kwargs):
        pass

    def close(self):
        if self.fail_close:
            raise RuntimeError("owner close failed")


class FakeJob:
    def __init__(self, *, hang=False, terminate_error=False, close_error=False, external_events=None):
        self.name = "Local\\SyntheticJob"
        self.hang = hang
        self.terminated = False
        self.terminate_error = terminate_error
        self.close_error = close_error
        self.external_events = external_events
        self.events = []

    def spawn_suspended(self, command, *, cwd):
        self.events.append("spawn_suspended")
        return 123

    def resume(self):
        self.events.append("resume")

    def wait_empty_until(self, deadline):
        self.events.append("query")
        if not self.hang and not self.terminated:
            time.sleep(0.002)  # 纯替身模拟正耗时；真实C0仍拒绝部分退款。
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
        return WorkerCommand(sys._base_executable, ("-B", "-c", "pass"), str(BACKEND))

    async def run_fake(self, ledger, job=None, *, owner=Owner, deadline_offset=20):
        with patch("app.worker.session.ActivityMutex", owner), patch(
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
        self.assertEqual((result.reserved_seconds, result.settled_seconds), (0, 0))
        self.assertFalse(result.cleanup_incomplete)

    async def test_04_claim_response_lost_has_no_job_and_no_false_charge(self):
        result = await self.run_fake(Ledger(claim_error=RuntimeError("response lost")))
        self.assertEqual(result.state, "failed_closed")
        self.assertEqual((result.reserved_seconds, result.settled_seconds, result.pending_fold_seconds), (None, None, None))
        self.assertIsNone(result.job_name)

    async def test_05_early_success_uses_tree_zero_close_then_same_g_settle_retry(self):
        ledger = Ledger(settle_lost_once=True)
        job = FakeJob(external_events=ledger.events)
        result = await self.run_fake(ledger, job)
        self.assertEqual(result.state, "settled")
        self.assertEqual((result.settled_seconds, result.reserved_seconds, result.pending_fold_seconds), (1, 0, 0))
        self.assertEqual(result.active_processes_at_end, 0)
        self.assertIn("close_job", job.events)
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


class LauncherUnitTests(unittest.TestCase):
    def test_08_fake_process_timeout_terminates_exact_owner_without_charge_claim(self):
        class Pipe:
            def close(self): pass
            def poll(self, timeout): return False

        class Process:
            def __init__(self):
                self.alive = True
                self.calls = []
                self.exitcode = None

            def start(self): self.calls.append("start")
            def join(self, timeout): self.calls.append("join")
            def is_alive(self): return self.alive
            def terminate(self): self.calls.append("terminate"); self.alive = False
            def kill(self): self.calls.append("kill"); self.alive = False
            def close(self): self.calls.append("close")

        class Context:
            def __init__(self): self.process = Process()
            def Pipe(self, duplex): return Pipe(), Pipe()
            def Process(self, **kwargs): return self.process

        context = Context()
        with patch("app.worker.launcher.multiprocessing.get_context", return_value=context):
            result = run_supervised_window(
                PostgresAdmissionLedger("synthetic-not-connected"),
                SessionConfig(), str(uuid4()), "worker-1",
                WorkerCommand(sys._base_executable, ("-B", "-c", "pass"), str(BACKEND)),
                run_tag="offline-launcher",
            )
        self.assertEqual(result.state, "manager_timeout_unconfirmed")
        self.assertIsNone(result.reserved_seconds)
        self.assertIn("terminate", context.process.calls)
        self.assertNotIn("kill", context.process.calls)



if __name__ == "__main__":
    unittest.main(verbosity=2)
