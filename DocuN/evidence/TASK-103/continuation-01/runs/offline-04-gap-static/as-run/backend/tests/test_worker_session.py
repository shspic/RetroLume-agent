"""TASK-083 受门控调用与本机合成Job；无网络、PG、模型或产品入口。"""

from __future__ import annotations

import asyncio
import ctypes
import json
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
from app.worker.command import WorkerCommand
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
        return WindowSnapshot("running" if self.old_running else "pending", 1 if self.old_running else 0, 6 if self.old_running else 0, False, 1 if self.old_running else None, self.old_running, True)

    async def claim_lease(self, activity_id, executor_id, *, lease_seconds, window_seconds, running_owner_session_id=None, expected_previous_generation=None):
        self.events.append("claim")
        if self.claim_error:
            raise RuntimeError("synthetic commit response lost")
        self.generation += 1
        return ActivityLease(
            activity_id, executor_id, self.generation, 1,
            datetime.now(timezone.utc) + timedelta(seconds=window_seconds), self.window,
            running_owner_session_id,
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
        return SessionConfig(window_seconds=6, request_timeout_seconds=0.5, stop_grace_seconds=1, startup_limit_seconds=2, single_host_single_session_recovery=True)

    def command(self):
        return WorkerCommand()

    async def test_claim_response_lost_and_partial_window_never_spawn(self):
        class Owner:
            def __init__(self, *args, **kwargs): pass
            def close(self): pass

        for ledger, expected in ((FakeLedger(claim_error=True), "failed_closed"), (FakeLedger(window=2), "partial_window_too_small")):
            supervisor = SingleWindowSupervisor(ledger, self.config())
            with patch("app.worker.session.current_process_session_id", return_value=1), patch("app.worker.session.ActivityMutex", Owner), patch("app.worker.session.NamedJob.create", side_effect=AssertionError("unexpected spawn")):
                outcome = await supervisor.run_once(str(uuid4()), "worker-1", self.command(), run_tag="unit-no-spawn", manager_deadline_ns=time.monotonic_ns() + 20_000_000_000)
            self.assertEqual(outcome.state, expected)
            self.assertEqual(ledger.events, ["inspect", "claim"])

    async def test_unknown_old_job_fails_before_claim(self):
        class Owner:
            def __init__(self, *args, **kwargs): pass
            def close(self): pass
        ledger = FakeLedger(old_running=True)
        with patch("app.worker.session.current_process_session_id", return_value=1), patch("app.worker.session.ActivityMutex", Owner), patch("app.worker.session.NamedJob.open_existing", side_effect=JobUnknown("unknown")):
            outcome = await SingleWindowSupervisor(ledger, self.config()).run_once(str(uuid4()), "worker-1", self.command(), run_tag="unit-old-unknown", manager_deadline_ns=time.monotonic_ns() + 20_000_000_000)
        self.assertEqual(outcome.state, "failed_closed")
        self.assertEqual(ledger.events, ["inspect"])


# Real Job scenarios 01-05 require fixtures.task083.job_batch and a new run card.


if __name__ == "__main__":
    unittest.main(verbosity=2)

