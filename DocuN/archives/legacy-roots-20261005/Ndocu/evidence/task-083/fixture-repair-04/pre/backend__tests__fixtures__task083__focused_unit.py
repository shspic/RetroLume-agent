"""TASK-083 focused repair 03: pure substitutes; no OS object or database."""

from __future__ import annotations

import asyncio
from dataclasses import asdict
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch
from uuid import uuid4

BACKEND = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(BACKEND))

from app.activities import PostgresAdmissionLedger
from app.worker.command import WorkerCommand
from app.worker.launcher import ProcessCreationError, run_supervised_window
from app.worker.session import SessionConfig, SessionOutcome
from app.worker.supervisor_ipc import IpcUnknown, SLOT_SIZE, pack_frame, unpack_frame
from app.worker.supervisor_main import _validated_request
from job_control import JobScenarioUnsafe, _new_event_or_reject


class EventControlTests(unittest.TestCase):
    def test_04_start_collision_closes_only_returned_handle(self):
        class Kernel:
            def __init__(self): self.closed = []
            def CreateEventW(self, *_): return 41
            def CloseHandle(self, handle): self.closed.append(handle); return True
            def SetEvent(self, *_): raise AssertionError("foreign event must not be armed")
        kernel = Kernel()
        with patch("job_control.ctypes.set_last_error"), patch("job_control.ctypes.get_last_error", return_value=183):
            with self.assertRaises(JobScenarioUnsafe):
                _new_event_or_reject(kernel, "Local\\collision")
        self.assertEqual(kernel.closed, [41])

    def test_04_start_creation_error_and_new_handle(self):
        class Kernel:
            def __init__(self, handle): self.handle = handle; self.closed = []
            def CreateEventW(self, *_): return self.handle
            def CloseHandle(self, handle): self.closed.append(handle); return True
        absent = Kernel(0)
        with patch("job_control.ctypes.set_last_error"), patch("job_control.ctypes.get_last_error", return_value=5):
            with self.assertRaises(JobScenarioUnsafe): _new_event_or_reject(absent, "Local\\denied")
        self.assertEqual(absent.closed, [])
        fresh = Kernel(42)
        with patch("job_control.ctypes.set_last_error"), patch("job_control.ctypes.get_last_error", return_value=0):
            self.assertEqual(_new_event_or_reject(fresh, "Local\\new"), 42)
        self.assertEqual(fresh.closed, [])


class FrameTests(unittest.TestCase):
    def test_d1_bounded_frame_and_half_frame_rejection(self):
        packed = pack_frame({"protocol": 1, "data": "ok"})
        self.assertEqual(unpack_frame(packed.ljust(SLOT_SIZE, b"\0"))["data"], "ok")
        with self.assertRaises(IpcUnknown): pack_frame({"data": "x" * SLOT_SIZE})
        with self.assertRaises(IpcUnknown): unpack_frame(b"\0" * SLOT_SIZE)
        corrupt = bytearray(packed.ljust(SLOT_SIZE, b"\0"))
        corrupt[40] ^= 1
        with self.assertRaises(IpcUnknown): unpack_frame(bytes(corrupt))

    def test_d1_child_request_rejects_expired_deadline_without_connect(self):
        config = ConfigFactory.make()
        ledger = PostgresAdmissionLedger("postgresql://example.invalid/unused")
        with patch("app.worker.supervisor_main.time.monotonic_ns", return_value=10):
            request = request_data(ledger, config, deadline_ns=9)
            with self.assertRaisesRegex(ValueError, "deadline expired"):
                _validated_request(request, request["mapping_name"])


class ConfigFactory:
    @staticmethod
    def make():
        return SessionConfig(window_seconds=6, request_timeout_seconds=.5,
                             stop_grace_seconds=1, startup_limit_seconds=2,
                             manager_db_timeout_seconds=.5, cleanup_seconds=1,
                             mutex_wait_seconds=.5, manager_overhead_seconds=8)


def request_data(ledger, config, *, deadline_ns):
    return {"protocol": 1, "mapping_name": "Local\\RetroLume.SUP." + "a" * 32,
            "activity_id": str(uuid4()), "executor_id": "exec", "run_tag": "unit",
            "deadline_ns": deadline_ns, "command": {"task": "idle"},
            "config": asdict(config),
            "ledger": {"dsn": ledger._dsn,
                       "connect_timeout_seconds": ledger._connect_timeout,
                       "statement_timeout_ms": ledger._statement_timeout_ms,
                       "lock_timeout_ms": ledger._lock_timeout_ms}}


class Mapping:
    current = None
    result = None
    fail_close = False
    exit_status = 0

    def __init__(self):
        self.events = []
        self.request = None
        Mapping.current = self

    @classmethod
    def create(cls, name):
        return cls()

    def write_request(self, data):
        self.events.append("write_request")
        self.request = data

    def read_result(self):
        self.events.append("read_result")
        if self.result is None: raise IpcUnknown("half frame")
        return self.result

    def close(self):
        self.events.append("mapping_close")
        if self.fail_close: raise IpcUnknown("mapping close failed")


class Process:
    current = None
    fail_mode = None
    wait_values = (True, True)
    fail_close = False
    exit_status = 0

    def __init__(self):
        self.events = []
        self.wait_iter = iter(self.wait_values)
        Process.current = self

    @classmethod
    def create(cls, name):
        assert Mapping.current.request["mapping_name"] == name
        result = cls()
        result.events.append("create_suspended")
        if cls.fail_mode == "partial": raise ProcessCreationError(5, result)
        return result

    @property
    def pid(self): return 123

    def creation_time_100ns(self):
        self.events.append("identity")
        return 456

    def resume(self): self.events.append("resume")

    def wait(self, seconds):
        self.events.append(("wait", seconds))
        return next(self.wait_iter, False)

    def exit_code(self): return self.exit_status

    def terminate(self): self.events.append("terminate")

    def close(self):
        self.events.append("process_close")
        if self.fail_close: raise RuntimeError("close failed")


class LauncherTests(unittest.TestCase):
    def setUp(self):
        Mapping.current = None
        Mapping.result = None
        Mapping.fail_close = False
        Process.current = None
        Process.fail_mode = None
        Process.wait_values = (True, True)
        Process.fail_close = False
        Process.exit_status = 0
        self.config = ConfigFactory.make()
        self.ledger = PostgresAdmissionLedger("postgresql://example.invalid/unused")
        self.activity = str(uuid4())

    def invoke(self, **patches):
        with patch("app.worker.launcher.os.name", "nt"), patch("app.worker.launcher.NamedMapping", Mapping), patch(
            "app.worker.launcher._SuspendedSupervisor", Process
        ), patch("app.worker.launcher._remaining", side_effect=patches.get("remaining", lambda _: 5.0)):
            return run_supervised_window(self.ledger, self.config, self.activity,
                                         "exec", WorkerCommand(), run_tag="unit")

    def settled_frame(self):
        outcome = SessionOutcome("unit", "settled", self.activity,
                                 generation=1, active_processes_at_end=0,
                                 settled_seconds=1, reserved_seconds=0,
                                 pending_fold_seconds=0)
        data = asdict(outcome)
        data["cleanup_errors"] = []
        return {"protocol": 1, "run_tag": "unit", "activity_id": self.activity,
                "outcome": data}

    def test_d1_fixed_handoff_reads_only_after_exit_and_preserves_identity(self):
        Mapping.result = self.settled_frame()
        outcome = self.invoke()
        self.assertEqual((outcome.state, outcome.manager_pid, outcome.manager_created_100ns),
                         ("settled", 123, 456))
        self.assertEqual(Process.current.events[:3], ["create_suspended", "identity", "resume"])
        self.assertEqual(Mapping.current.events[:2], ["write_request", "read_result"])
        self.assertIn(("wait", 5.0), Process.current.events)
        self.assertFalse(outcome.cleanup_incomplete)

    def test_d1_partial_create_never_resumes_and_remains_unknown(self):
        Process.fail_mode = "partial"
        Process.wait_values = (False, True)
        outcome = self.invoke()
        self.assertTrue(outcome.cleanup_incomplete)
        self.assertIsNone(outcome.settled_seconds)
        self.assertIsNone(outcome.reserved_seconds)
        self.assertNotIn("resume", Process.current.events)
        self.assertIn("terminate", Process.current.events)

    def test_d1_deadline_before_resume_terminates_exact_owner(self):
        Process.wait_values = (False, True)
        values = iter((5.0, 5.0, 5.0, 0.0, 0.0))
        outcome = self.invoke(remaining=lambda _: next(values, 0.0))
        self.assertEqual(outcome.state, "manager_startup_deadline_unconfirmed")
        self.assertNotIn("resume", Process.current.events)
        self.assertIn("terminate", Process.current.events)

    def test_d1_timeout_or_half_frame_keeps_all_charges_unknown(self):
        Process.wait_values = (False, False, False)
        outcome = self.invoke()
        self.assertEqual(outcome.state, "manager_timeout_unconfirmed")
        self.assertTrue(outcome.cleanup_incomplete)
        self.assertEqual((outcome.settled_seconds, outcome.reserved_seconds, outcome.pending_fold_seconds),
                         (None, None, None))
        self.setUp()
        outcome = self.invoke()
        self.assertTrue(outcome.cleanup_incomplete)
        self.assertEqual((outcome.settled_seconds, outcome.reserved_seconds), (None, None))

    def test_d1_child_failure_and_request_write_error_do_not_read_result(self):
        Process.exit_status = 1
        outcome = self.invoke()
        self.assertTrue(outcome.cleanup_incomplete)
        self.assertEqual((outcome.settled_seconds, outcome.reserved_seconds), (None, None))
        self.assertNotIn("read_result", Mapping.current.events)
        self.setUp()
        def bad_write(self, data): raise IpcUnknown("write failed")
        with patch.object(Mapping, "write_request", bad_write):
            outcome = self.invoke()
        self.assertTrue(outcome.cleanup_incomplete)
        self.assertIsNone(Process.current)
        self.assertEqual((outcome.settled_seconds, outcome.reserved_seconds), (None, None))
    def test_d1_cleanup_failure_and_cancellation_preserve_unknown(self):
        Mapping.result = self.settled_frame()
        Process.fail_close = True
        outcome = self.invoke()
        self.assertEqual(outcome.state, "settled_cleanup_error")
        self.assertTrue(outcome.cleanup_incomplete)
        self.setUp()
        Process.wait_values = (False, True)
        calls = iter((5.0, 5.0, 5.0))
        def cancelled(_):
            try: return next(calls)
            except StopIteration: raise asyncio.CancelledError()
        with self.assertRaises(asyncio.CancelledError) as caught:
            self.invoke(remaining=cancelled)
        self.assertTrue(caught.exception.session_outcome.cleanup_incomplete)
        self.assertIsNone(caught.exception.session_outcome.settled_seconds)


if __name__ == "__main__":
    unittest.main(verbosity=2)
