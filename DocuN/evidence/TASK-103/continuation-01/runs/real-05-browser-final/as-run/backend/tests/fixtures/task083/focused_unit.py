"""TASK-083 focused repair 03: pure substitutes; no OS object or database."""

from __future__ import annotations

import asyncio
from dataclasses import asdict
from functools import partial
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
    os.environ.copy为纯复制。无任何真实事件/进程/Job。Kernel各API经
    functools.partial包装为可设属性的实例闭包，使verify_last_handle对API的
    argtypes/restype赋值合法（修正04实证：普通绑定方法不可设属性）。
    回执身份由fake_spawn从真实spawn实参派生（修正06）：verify_last_handle
    自生成随机身份并经argv传给SUP子进程（job_control.py:34-36/:82-84），
    夹具回执与open_existing断言均使用同一派生身份，不硬编码、不patch
    控制器uuid4、不取消任何身份校验。两次WinDLL（starter/kernel）的句柄
    基址互不相交（修正06缺陷三），父Start句柄与worker/事件句柄不撞号。
    """

    def _run(self, *, receipt="identity", spawn_error=None):
        """替身化OS边界后调用真实verify_last_handle。

        返回(次序log, kernels, 派生身份, result, 异常)。receipt:
        "identity"=spawn成功后按派生身份回执created+resumed两行；
        "empty"=spawn成功但回执空行（身份校验失败分支）。spawn异常分支
        未产生派生身份（保持空dict），调用方不得引用。
        """
        log = []
        kernels = []
        identity = {}
        receipt_lines = []

        class Kernel:
            def __init__(self, base):
                self.start_handle = None
                self._next = base
                # verify_last_handle会向每个kernel API赋argtypes/restype
                # （job_control.py 49-71行）；普通绑定方法不可设属性
                # （AttributeError），故用partial包装的实例闭包占位：
                # partial实例支持任意属性赋值，调用语义与原绑定方法完全一致。
                self.CreateEventW = partial(self.CreateEventW)
                self.SetEvent = partial(self.SetEvent)
                self.CloseHandle = partial(self.CloseHandle)
                self.OpenProcess = partial(self.OpenProcess)
                self.GetProcessTimes = partial(self.GetProcessTimes)
                self.OpenEventW = partial(self.OpenEventW)
                self.WaitForSingleObject = partial(self.WaitForSingleObject)
                self.TerminateProcess = partial(self.TerminateProcess)

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
            async def readline(self):
                log.append(("readline",))
                return receipt_lines.pop(0) if receipt_lines else b""

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

        async def fake_spawn(*args, **_kwargs):
            if spawn_error is not None:
                log.append(("spawn_error",))
                raise spawn_error
            log.append(("spawn",))
            # job_control.py:82-84实参顺序核对：args[4]=activity_id、
            # args[5]=str(generation)、args[6]=run_tag、args[7]=start_name。
            # 从真实spawn实参派生活动UUID/G/runTag，按真实job_name函数构造
            # created/resumed回执，与SUP子进程从argv接收身份再回执的协议
            # 数据流一致；不patch控制器uuid4、不固定控制器内部随机身份。
            # pid/creation_time及现有协议字段保持不变。
            identity["activity_id"] = args[4]
            identity["generation"] = int(args[5])
            identity["run_tag"] = args[6]
            if receipt == "identity":
                created = {"phase": "suspended", "activity_id": identity["activity_id"],
                           "generation": identity["generation"], "run_tag": identity["run_tag"],
                           "job_name": job_name(identity["activity_id"], identity["generation"]),
                           "pid": 123, "created_100ns": 0, "active_processes": 1}
                receipt_lines.append((json.dumps(created) + "\n").encode())
                receipt_lines.append((json.dumps({"phase": "resumed", "pid": 123}) + "\n").encode())
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
            # 两次WinDLL分别构造starter与kernel（job_control.py:48/:57）；
            # 基址按实例序号分离（首例100起、次例100100起），父Start句柄与
            # worker/事件句柄互不相交，close/set次序断言不再互相混淆。
            kernel = Kernel(base=100 + 100000 * len(kernels))
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
        return log, kernels, identity, result, exc

    def test_04_start_handle_closes_after_identity_receipt(self):
        log, kernels, identity, result, exc = self._run(receipt="identity")
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
        # open_existing断言用派生身份：与控制器内部随机activity同源（spawn实参）。
        self.assertLess(log.index(("close_handle", start_handle)),
                        log.index(("open_existing", identity["activity_id"], 7)))

    def test_04_start_handle_release_exactly_once_on_failure(self):
        # 分支A：提前异常（控制进程创建失败）——Start句柄仍在收尾中恰好关闭一次。
        log, kernels, identity, result, exc = self._run(spawn_error=RuntimeError("spawn refused"))
        self.assertIsInstance(exc, RuntimeError)
        self.assertIsNone(result)
        self.assertEqual(identity, {})  # spawn未成功，未产生派生身份。
        start_handle = kernels[0].start_handle
        self.assertEqual(log.count(("close_handle", start_handle)), 1)
        self.assertNotIn(("readline",), log)
        self.assertNotIn(("open_process",), log)
        self.assertNotIn(("kill",), log)  # proc为None，不误杀。
        # 分支B：身份回执失败（SUP无输出）——同样恰好一次，且不进入身份后续。
        log, kernels, identity, result, exc = self._run(receipt="empty")
        self.assertIsInstance(exc, AssertionError)
        self.assertIsNone(result)
        start_handle = kernels[0].start_handle
        self.assertEqual(log.count(("close_handle", start_handle)), 1)
        self.assertIn(("kill",), log)  # 精确收尾终止已启动的控制进程。
        self.assertNotIn(("open_process",), log)
        # open_existing正反断言均用派生身份：控制器内部随机activity经spawn
        # 实参派生而来，若意外调用open_existing必被此断言发现，不以硬编码
        # 元组掩盖行为。
        self.assertNotIn(("open_existing", identity["activity_id"], 7), log)
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
