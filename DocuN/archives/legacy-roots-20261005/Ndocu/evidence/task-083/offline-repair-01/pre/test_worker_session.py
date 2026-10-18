"""TASK-083 受门控调用与本机合成Job；无网络、PG、模型或产品入口。"""

from __future__ import annotations

import asyncio
import ctypes
from ctypes import wintypes
from datetime import datetime, timedelta, timezone
import math
import os
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch
from uuid import uuid4

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.activities import ActivityLease, CloseResult, SettleResult, WindowSnapshot
from app.worker.gate import ClosingCallGate, GateClosed
from app.worker.session import SessionConfig, SingleWindowSupervisor
from app.worker.windows_job import JobUnknown, NamedJob


FIXTURE = BACKEND / "tests" / "fixtures" / "task083" / "fixture.py"


class FakeLedger:
    def __init__(self, *, window: int = 6, claim_error: bool = False, old_running: bool = False):
        self.window = window
        self.claim_error = claim_error
        self.old_running = old_running
        self.events: list[str] = []
        self.generation = 0

    async def inspect_window(self, activity_id):
        self.events.append("inspect")
        return WindowSnapshot("running" if self.old_running else "pending", 1 if self.old_running else 0, 6 if self.old_running else 0, False)

    async def claim_lease(self, activity_id, executor_id, *, lease_seconds, window_seconds):
        self.events.append("claim")
        if self.claim_error:
            raise RuntimeError("synthetic commit response lost")
        self.generation += 1
        return ActivityLease(
            activity_id, executor_id, self.generation, 1,
            datetime.now(timezone.utc) + timedelta(seconds=window_seconds), self.window,
        )

    async def begin_window_close(self, activity_id, executor_id, execution_generation):
        self.events.append("close_db")
        return CloseResult.CLOSED

    async def settle_execution_window(self, activity_id, executor_id, execution_generation, *, window_seconds, elapsed_seconds):
        self.events.append("settle")
        if not 1 <= math.ceil(elapsed_seconds) <= window_seconds:
            raise AssertionError("SUP submitted invalid elapsed")
        return SettleResult.SETTLED


class _Gateway:
    def __init__(self):
        self.marked = asyncio.Event()
        self.release = asyncio.Event()
        self.events: list[str] = []

    async def call(self, context, request):
        self.events.extend(("admit", "mark"))
        self.marked.set()
        await self.release.wait()
        self.events.append("send")
        return "done"


class GateTests(unittest.IsolatedAsyncioTestCase):
    async def test_gate_closure_waits_for_marked_before_send_and_never_reopens(self):
        gateway = _Gateway()
        gate = ClosingCallGate(gateway)
        await gate.arm()
        first = asyncio.create_task(gate.call(None, None))
        await gateway.marked.wait()
        closing = asyncio.create_task(gate.close(timeout_seconds=2))
        await asyncio.sleep(0)
        with self.assertRaises(GateClosed):
            await gate.call(None, None)
        self.assertFalse(closing.done())
        gateway.release.set()
        self.assertEqual(await first, "done")
        await closing
        self.assertEqual(gateway.events, ["admit", "mark", "send"])
        with self.assertRaises(GateClosed):
            await gate.arm()

    async def test_gate_close_timeout_keeps_closed(self):
        gateway = _Gateway()
        gate = ClosingCallGate(gateway)
        await gate.arm()
        first = asyncio.create_task(gate.call(None, None))
        await gateway.marked.wait()
        with self.assertRaises(TimeoutError):
            await gate.close(timeout_seconds=0.01)
        with self.assertRaises(GateClosed):
            await gate.call(None, None)
        gateway.release.set()
        await first


class ProtocolUnitTests(unittest.IsolatedAsyncioTestCase):
    def config(self):
        return SessionConfig(window_seconds=6, request_timeout_seconds=0.5, stop_grace_seconds=1, startup_limit_seconds=2)

    async def test_claim_response_lost_and_partial_window_never_spawn(self):
        class Owner:
            def __init__(self, *args, **kwargs): pass
            def close(self): pass

        for ledger, expected in ((FakeLedger(claim_error=True), "failed_closed"), (FakeLedger(window=2), "partial_window_too_small")):
            supervisor = SingleWindowSupervisor(ledger, self.config())
            with patch("app.worker.session.ActivityMutex", Owner), patch("app.worker.session.NamedJob.create", side_effect=AssertionError("unexpected spawn")):
                outcome = await supervisor.run_once(str(uuid4()), "worker-1", lambda _: [sys.executable], cwd=str(BACKEND), run_tag="unit-no-spawn")
            self.assertEqual(outcome.state, expected)
            self.assertEqual(ledger.events, ["inspect", "claim"])

    async def test_unknown_old_job_fails_before_claim(self):
        class Owner:
            def __init__(self, *args, **kwargs): pass
            def close(self): pass
        ledger = FakeLedger(old_running=True)
        with patch("app.worker.session.ActivityMutex", Owner), patch("app.worker.session.NamedJob.open_existing", side_effect=JobUnknown("unknown")):
            outcome = await SingleWindowSupervisor(ledger, self.config()).run_once(str(uuid4()), "worker-1", lambda _: [sys.executable], cwd=str(BACKEND), run_tag="unit-old-unknown")
        self.assertEqual(outcome.state, "failed_closed")
        self.assertEqual(ledger.events, ["inspect"])


@unittest.skipUnless(os.name == "nt", "真实Job场景仅在Windows本机运行")
class WindowsJobTests(unittest.IsolatedAsyncioTestCase):
    def config(self):
        return SessionConfig(window_seconds=6, request_timeout_seconds=0.5, stop_grace_seconds=1, startup_limit_seconds=2, cleanup_seconds=2)

    def command(self, mode):
        return [sys._base_executable, "-B", str(FIXTURE), mode]

    async def test_01_normal_job_empty_precedes_close_and_refund(self):
        ledger = FakeLedger()
        outcome = await SingleWindowSupervisor(ledger, self.config()).run_once(
            str(uuid4()), "worker-1", lambda _: self.command("fast"), cwd=str(BACKEND), run_tag="job-normal"
        )
        self.assertEqual(outcome.state, "settled", outcome)
        self.assertEqual(outcome.active_processes_at_end, 0)
        self.assertGreaterEqual(outcome.charged_seconds, 1)
        self.assertEqual(ledger.events, ["inspect", "claim", "close_db", "settle"])

    async def test_02_hung_job_is_killed_and_not_refunded(self):
        ledger = FakeLedger()
        outcome = await SingleWindowSupervisor(ledger, self.config()).run_once(
            str(uuid4()), "worker-1", lambda _: self.command("hang"), cwd=str(BACKEND), run_tag="job-hang"
        )
        self.assertEqual(outcome.state, "stopped_at_deadline", outcome)
        self.assertEqual(outcome.active_processes_at_end, 0)
        self.assertEqual(outcome.charged_seconds, 6)
        self.assertNotIn("settle", ledger.events)

    async def test_03_main_exits_before_descendant(self):
        activity_id = str(uuid4())
        with NamedJob.create(activity_id, 1) as job:
            job.spawn_suspended(self.command("parent"), cwd=str(BACKEND))
            job.resume()
            self.assertEqual(job.api.WaitForSingleObject(job.process.hProcess, 4000), 0)
            self.assertGreater(job.active_processes(), 0, "主进程退出不能冒充整树退出")
            self.assertTrue(job.wait_empty_until(time.monotonic_ns() + 5_000_000_000))
            self.assertEqual(job.active_processes(), 0)

    async def test_04_supervisor_death_closes_last_job_handle(self):
        activity_id = str(uuid4())
        proc = await asyncio.create_subprocess_exec(
            sys._base_executable, "-B", str(FIXTURE), "controller", activity_id, "7",
            cwd=str(BACKEND), stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        worker_handle = None
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        kernel.WaitForSingleObject.restype = wintypes.DWORD
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel.CloseHandle.restype = wintypes.BOOL
        try:
            line = await asyncio.wait_for(proc.stdout.readline(), timeout=5)
            self.assertTrue(line, (await proc.stderr.read()).decode(errors="replace"))
            pid = int(line.strip())
            worker_handle = kernel.OpenProcess(0x00100000, False, pid)  # 精确PID仍活时取同步句柄。
            self.assertTrue(worker_handle)
            proc.stdin.write(b"x")
            await proc.stdin.drain()
            await asyncio.wait_for(proc.wait(), timeout=5)
            self.assertEqual(kernel.WaitForSingleObject(worker_handle, 4000), 0)
        finally:
            if proc.returncode is None:
                proc.kill()  # 仅本测试刚创建的精确SUP进程句柄。
                await asyncio.wait_for(proc.wait(), timeout=5)
            if worker_handle:
                kernel.CloseHandle(worker_handle)

    async def test_05_same_name_collision_fails_closed(self):
        activity_id = str(uuid4())
        with NamedJob.create(activity_id, 1) as job:
            with self.assertRaises(JobUnknown):
                NamedJob.create(activity_id, 1)
            self.assertEqual(job.active_processes(), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
