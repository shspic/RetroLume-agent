"""TASK-083 focused repair 03: pure substitutes; no OS object or database."""

from __future__ import annotations

import asyncio
from dataclasses import asdict
import json
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
from app.worker.windows_job import job_name
from job_control import JobScenarioUnsafe, _new_event_or_reject, verify_last_handle


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


class StartLifecycleTests(unittest.TestCase):
    """场景04 Start句柄生命周期：调用真实verify_last_handle，OS接口全替身。

    替身覆盖job_control内全部真实OS启动接口：ctypes.WinDLL（kernel32两处）、
    asyncio.create_subprocess_exec（无真实子进程）、NamedJob.open_existing
    （无真实Job对象）；job_name为纯字符串构造，time.monotonic_ns只读，
    os.environ.copy为纯复制。无任何真实事件/进程/Job。
    """

    def _identity_lines(self):
        activity = "11111111-1111-1111-1111-111111111111"
        created = {"phase": "suspended", "activity_id": activity, "generation": 7,
                   "run_tag": "lifecycle-unit", "job_name": job_name(activity, 7),
                   "pid": 123, "created_100ns": 0, "active_processes": 1}
        resumed = {"phase": "resumed", "pid": 123}
        return activity, [
            (json.dumps(created) + "\n").encode(),
            (json.dumps(resumed) + "\n").encode(),
        ]

    def _run(self, *, lines, spawn_error=None):
        """替身化OS边界后调用真实verify_last_handle；返回(次序log, kernels, result, 异常)。"""
        log = []
        kernels = []

        class Kernel:
            def __init__(self):
                self.start_handle = None
                self._next = 100

            def CreateEventW(self, *_):
                self.start_handle = self._next
                self._next += 1
                log.append(("create_event", self.start_handle))
                return self.start_handle

            def SetEvent(self, handle):
                log.append(("set_event", handle))
                return True

            def CloseHandle(self, handle):
                log.append(("close_handle", handle))
                return True

            def OpenProcess(self, *_):
                handle = self._next
                self._next += 1
                log.append(("open_process",))
                return handle

            def GetProcessTimes(self, handle, *_):
                # byref的_FILETIME保持全0；回执created_100ns=0与之匹配。
                log.append(("process_times",))
                return True

            def OpenEventW(self, *_):
                handle = self._next
                self._next += 1
                log.append(("open_event",))
                return handle

            def WaitForSingleObject(self, *_):
                log.append(("wait_object",))
                return 0

            def TerminateProcess(self, *_):
                log.append(("terminate_process",))
                return True

        class FakeStdout:
            def __init__(self):
                self._lines = list(lines)

            async def readline(self):
                log.append(("readline",))
                return self._lines.pop(0) if self._lines else b""

        class FakeProc:
            def __init__(self):
                self.stdout = FakeStdout()
                self.returncode = None

            def kill(self):
                log.append(("kill",))
                self.returncode = -9

            async def wait(self):
                log.append(("proc_wait",))
                if self.returncode is None:
                    self.returncode = 0
                return self.returncode

        async def fake_spawn(*_args, **_kwargs):
            if spawn_error is not None:
                log.append(("spawn_error",))
                raise spawn_error
            log.append(("spawn",))
            return FakeProc()

        class FakeOpened:
            def active_processes(self):
                log.append(("active_processes",))
                return 1

            def close(self):
                log.append(("job_close",))

        class FakeNamedJob:
            @classmethod
            def open_existing(cls, activity_id, generation):
                log.append(("open_existing", activity_id, generation))
                return FakeOpened()

        def fake_windll(*_args, **_kwargs):
            kernel = Kernel()
            kernels.append(kernel)
            return kernel

        with patch("job_control.ctypes.WinDLL", fake_windll), patch(
            "job_control.asyncio.create_subprocess_exec", fake_spawn
        ), patch("job_control.NamedJob", FakeNamedJob):
            try:
                result = asyncio.run(verify_last_handle(Path("fixture.py"), Path("backend")))
                exc = None
            except BaseException as raised:  # 替身边界内异常原样返回给断言。
                result, exc = None, raised
        return log, kernels, result, exc

    def test_04_start_handle_closes_after_identity_receipt(self):
        activity, lines = self._identity_lines()
        log, kernels, result, exc = self._run(lines=lines)
        self.assertIsNone(exc)
        self.assertEqual(result["phase"], "suspended")
        self.assertEqual(result["pid"], 123)
        self.assertEqual(result["active_processes_before_supervisor_exit"], 1)
        self.assertTrue(result["worker_signaled_after_last_job_handle_closed"])
        start_handle = kernels[0].start_handle
        # 父Start句柄恰好SetEvent一次、CloseHandle一次。
        self.assertEqual(log.count(("set_event", start_handle)), 1)
        self.assertEqual(log.count(("close_handle", start_handle)), 1)
        # 释放次序：子回执悬停身份（第一次readline）之后才关闭父Start句柄。
        self.assertLess(log.index(("readline",)), log.index(("close_handle", start_handle)))
        # 句柄释放后才取得精确worker句柄与观察Job（最后句柄死亡测试次序不变）。
        self.assertLess(log.index(("close_handle", start_handle)), log.index(("open_process",)))
        self.assertLess(log.index(("close_handle", start_handle)), log.index(("open_existing", activity, 7)))

    def test_04_start_handle_release_exactly_once_on_failure(self):
        # 分支A：提前异常（控制进程创建失败）——Start句柄仍在收尾中恰好关闭一次。
        activity, lines = self._identity_lines()
        log, kernels, result, exc = self._run(lines=lines, spawn_error=RuntimeError("spawn refused"))
        self.assertIsInstance(exc, RuntimeError)
        self.assertIsNone(result)
        start_handle = kernels[0].start_handle
        self.assertEqual(log.count(("close_handle", start_handle)), 1)
        self.assertNotIn(("readline",), log)
        self.assertNotIn(("open_process",), log)
        self.assertNotIn(("kill",), log)  # proc为None，不误杀。
        # 分支B：身份回执失败（SUP无输出）——同样恰好一次，且不进入身份后续。
        activity, lines = self._identity_lines()
        log, kernels, result, exc = self._run(lines=[b""])
        self.assertIsInstance(exc, AssertionError)
        self.assertIsNone(result)
        start_handle = kernels[0].start_handle
        self.assertEqual(log.count(("close_handle", start_handle)), 1)
        self.assertIn(("kill",), log)  # 精确收尾终止已启动的控制进程。
        self.assertNotIn(("open_process",), log)
        self.assertNotIn(("open_existing", activity, 7), log)
        self.assertLess(log.index(("readline",)), log.index(("close_handle", start_handle)))


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
        # 前两次运行窗检查仍有余额（5s）；第三次（取得精确SUP身份后、Resume前）
        # 返回0，触发Resume前截止。finally清理另行保有5s预算。SUP从未resume，
        # claim只可能在SUP子进程内发生，故结构上未claim；账字段保持未知。
        Process.wait_values = (False, True)
        values = iter((5.0, 5.0, 0.0, 5.0, 5.0))
        outcome = self.invoke(remaining=lambda _: next(values, 0.0))
        self.assertEqual(outcome.state, "manager_startup_deadline_unconfirmed")
        self.assertEqual(Process.current.events,
                         ["create_suspended", "identity", ("wait", 0), "terminate", ("wait", 5.0), "process_close"])
        self.assertNotIn("resume", Process.current.events)
        self.assertIn("terminate", Process.current.events)
        self.assertTrue(outcome.cleanup_incomplete)
        self.assertEqual((outcome.settled_seconds, outcome.reserved_seconds, outcome.pending_fold_seconds),
                         (None, None, None))
        self.assertNotIn("read_result", Mapping.current.events)

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
