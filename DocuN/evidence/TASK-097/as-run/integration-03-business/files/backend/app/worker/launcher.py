"""Fixed two-process Windows SUP launcher with suspended handoff and one deadline."""

from __future__ import annotations

import asyncio
import ctypes
from ctypes import wintypes
from dataclasses import asdict, replace
import os
import secrets
import subprocess
import sys
import time
from uuid import UUID

from app.activities import PostgresAdmissionLedger

from .command import WorkerCommand, _BACKEND, _INTERPRETER
from .session import SessionConfig, SessionOutcome
from .supervisor_ipc import NamedMapping
from .one_call import OneCallInput, decode_receipt, validate_identity
from .one_tool import decode_tool_receipt
from app.capabilities.contracts import CallContext, ToolExecutionInput
from .windows_job import (_FILETIME, _PROCESS_INFORMATION, _STARTUPINFOW,
                          CREATE_NO_WINDOW, CREATE_SUSPENDED, WAIT_OBJECT_0,
                          WAIT_TIMEOUT)


CREATE_UNICODE_ENVIRONMENT = 0x00000400
STILL_ACTIVE = 259

# 外2/外3回执的冻结字段集：不依赖动态fields同时接收两个版本。
_OUTER2_OUTCOME_FIELDS = (
    "run_tag", "state", "activity_id", "generation", "job_name", "pid",
    "active_processes_at_end", "settled_seconds", "reserved_seconds",
    "pending_fold_seconds", "elapsed_seconds", "cleanup_incomplete",
    "error_type", "cleanup_errors", "timing_diagnostic", "manager_pid",
    "manager_created_100ns", "running_owner_session_id", "worker_created_100ns",
    "model_receipt",
)
_OUTER3_OUTCOME_FIELDS = _OUTER2_OUTCOME_FIELDS + ("tool_receipt",)


class ManagerControlError(RuntimeError):
    pass


class ProcessCreationError(ManagerControlError):
    def __init__(self, error_code: int, partial=None):
        super().__init__(f"CreateProcessW failed: Windows error {error_code}")
        self.partial = partial


def _api():
    if os.name != "nt":
        raise ManagerControlError("Windows only")
    api = ctypes.WinDLL("kernel32", use_last_error=True)
    api.CreateProcessW.argtypes = [
        wintypes.LPCWSTR, wintypes.LPWSTR, ctypes.c_void_p, ctypes.c_void_p,
        wintypes.BOOL, wintypes.DWORD, ctypes.c_void_p, wintypes.LPCWSTR,
        ctypes.POINTER(_STARTUPINFOW), ctypes.POINTER(_PROCESS_INFORMATION),
    ]
    api.CreateProcessW.restype = wintypes.BOOL
    api.ResumeThread.argtypes = [wintypes.HANDLE]
    api.ResumeThread.restype = wintypes.DWORD
    api.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    api.WaitForSingleObject.restype = wintypes.DWORD
    api.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
    api.TerminateProcess.restype = wintypes.BOOL
    api.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    api.GetExitCodeProcess.restype = wintypes.BOOL
    api.GetProcessTimes.argtypes = [wintypes.HANDLE, ctypes.POINTER(_FILETIME),
                                    ctypes.POINTER(_FILETIME), ctypes.POINTER(_FILETIME),
                                    ctypes.POINTER(_FILETIME)]
    api.GetProcessTimes.restype = wintypes.BOOL
    api.CloseHandle.argtypes = [wintypes.HANDLE]
    api.CloseHandle.restype = wintypes.BOOL
    return api


def _remaining(deadline_ns: int) -> float:
    return max(0.0, (deadline_ns - time.monotonic_ns()) / 1e9)


def _environment_block() -> ctypes.Array:
    # The base Python executable needs the venv redirector path to find the
    # project dependencies, while the parent must own the actual base process.
    values = os.environ.copy()
    values["__PYVENV_LAUNCHER__"] = str(_INTERPRETER)
    if any("\x00" in key or "\x00" in value for key, value in values.items()):
        raise ManagerControlError("invalid process environment")
    block = "\x00".join(f"{key}={value}" for key, value in sorted(values.items(), key=lambda item: item[0].upper())) + "\x00\x00"
    if len(block) > 32767:
        raise ManagerControlError("process environment too large")
    return ctypes.create_unicode_buffer(block)


class _SuspendedSupervisor:
    """Owns the exact base interpreter process and primary-thread handles."""

    def __init__(self, api, info: _PROCESS_INFORMATION):
        self.api = api
        self.info = info
        self.resumed = False

    @classmethod
    def create(cls, mapping_name: str) -> "_SuspendedSupervisor":
        api = _api()
        executable = str(sys._base_executable)
        if not os.path.isabs(executable) or not os.path.isfile(executable):
            raise ManagerControlError("fixed base interpreter unavailable")
        argv = [executable, "-B", "-m", "app.worker.supervisor_main", mapping_name]
        command_line = ctypes.create_unicode_buffer(subprocess.list2cmdline(argv))
        environment = _environment_block()
        startup = _STARTUPINFOW()
        startup.cb = ctypes.sizeof(startup)
        info = _PROCESS_INFORMATION()
        created = api.CreateProcessW(
            executable, command_line, None, None, False,
            CREATE_SUSPENDED | CREATE_NO_WINDOW | CREATE_UNICODE_ENVIRONMENT,
            ctypes.cast(environment, ctypes.c_void_p), str(_BACKEND),
            ctypes.byref(startup), ctypes.byref(info),
        )
        if not created:
            partial = cls(api, info) if info.hProcess or info.hThread else None
            raise ProcessCreationError(ctypes.get_last_error(), partial)
        if not info.hProcess or not info.hThread:
            raise ProcessCreationError(0, cls(api, info))
        return cls(api, info)

    @property
    def pid(self) -> int | None:
        return int(self.info.dwProcessId) if self.info.hProcess else None

    def creation_time_100ns(self) -> int:
        created, exited, kernel, user = (_FILETIME() for _ in range(4))
        if not self.info.hProcess or not self.api.GetProcessTimes(
            self.info.hProcess, ctypes.byref(created), ctypes.byref(exited),
            ctypes.byref(kernel), ctypes.byref(user),
        ):
            raise ManagerControlError(f"GetProcessTimes: Windows error {ctypes.get_last_error()}")
        return (int(created.dwHighDateTime) << 32) | int(created.dwLowDateTime)

    def resume(self) -> None:
        if not self.info.hThread or self.api.ResumeThread(self.info.hThread) == 0xFFFFFFFF:
            raise ManagerControlError(f"ResumeThread: Windows error {ctypes.get_last_error()}")
        self.resumed = True

    def wait(self, seconds: float) -> bool:
        if not self.info.hProcess:
            raise ManagerControlError("SUP process handle missing")
        timeout_ms = max(0, min(0xFFFFFFFE, int(seconds * 1000)))
        result = self.api.WaitForSingleObject(self.info.hProcess, timeout_ms)
        if result == WAIT_OBJECT_0:
            return True
        if result == WAIT_TIMEOUT:
            return False
        raise ManagerControlError(f"WaitForSingleObject: result {result}")

    def exit_code(self) -> int:
        code = wintypes.DWORD()
        if not self.api.GetExitCodeProcess(self.info.hProcess, ctypes.byref(code)):
            raise ManagerControlError(f"GetExitCodeProcess: Windows error {ctypes.get_last_error()}")
        return int(code.value)

    def terminate(self) -> None:
        if not self.wait(0) and not self.api.TerminateProcess(self.info.hProcess, 1):
            if not self.wait(0):
                raise ManagerControlError(f"TerminateProcess: Windows error {ctypes.get_last_error()}")

    def close(self) -> None:
        errors = []
        for label, field in (("thread", "hThread"), ("process", "hProcess")):
            handle = getattr(self.info, field)
            if handle:
                if self.api.CloseHandle(handle):
                    setattr(self.info, field, None)
                else:
                    errors.append(label)
        if errors:
            raise ManagerControlError("CloseHandle(SUP): " + ",".join(errors))


def _request(ledger, config, activity_id, executor_id, command, run_tag, mapping_name, deadline_ns,
             one_call=None, tool_action=None) -> dict:
    if type(ledger) is not PostgresAdmissionLedger or type(config) is not SessionConfig or type(command) is not WorkerCommand:
        raise TypeError("fixed ledger, config and command required")
    if type(ledger._dsn) is not str or not 1 <= len(ledger._dsn.encode("utf-8")) <= 4096 or "\x00" in ledger._dsn:
        raise ValueError("bounded ledger connection data required")
    if type(activity_id) is not str or str(UUID(activity_id)) != activity_id:
        raise ValueError("activity UUID invalid")
    if type(executor_id) is not str or not 1 <= len(executor_id) <= 128:
        raise ValueError("executor invalid")
    if type(run_tag) is not str or not 1 <= len(run_tag) <= 64 or not run_tag.isascii() or not run_tag.replace("-", "").replace("_", "").isalnum():
        raise ValueError("runTag invalid")
    if command.task == "one_call":
        if type(one_call) is not OneCallInput or tool_action is not None:
            raise ValueError("one_call requires explicit input")
        validate_identity(activity_id, executor_id, one_call.operation_id, run_tag)
        if one_call.request.input_result is not None and one_call.request.input_result.activity_id != activity_id:
            raise ValueError("input result activity mismatch")
        if one_call.service.timeout_seconds > config.request_timeout_seconds:
            raise ValueError("model timeout exceeds session")
    elif command.task == "one_tool":
        if type(tool_action) is not ToolExecutionInput or one_call is not None:
            raise ValueError("one_tool requires explicit input")
        validate_identity(activity_id, executor_id, tool_action.operation_id, run_tag)
        tool_action.to_wire()
        if config.request_timeout_seconds > 120:
            raise ValueError("tool request timeout exceeds 120s limit")
    elif one_call is not None or tool_action is not None:
        raise ValueError("idle cannot carry business data")
    ledger_data = {
        "dsn": ledger._dsn,
        "connect_timeout_seconds": ledger._connect_timeout,
        "statement_timeout_ms": ledger._statement_timeout_ms,
        "lock_timeout_ms": ledger._lock_timeout_ms,
    }
    if command.task == "one_tool":
        # 工具外请求（协议3）精确字段：不带one_call/model service/API key。
        return {
            "protocol": 3, "mapping_name": mapping_name,
            "activity_id": activity_id, "executor_id": executor_id,
            "run_tag": run_tag, "deadline_ns": deadline_ns,
            "command": {"task": command.task},
            "config": asdict(config),
            "tool_action": tool_action.to_wire(),
            "ledger": ledger_data,
        }
    return {
        "protocol": 2, "mapping_name": mapping_name,
        "activity_id": activity_id, "executor_id": executor_id,
        "run_tag": run_tag, "deadline_ns": deadline_ns,
        "command": {"task": command.task},
        "config": asdict(config),
        "one_call": one_call.to_wire() if one_call is not None else None,
        "ledger": ledger_data,
    }


def _decode_outcome(frame: dict, run_tag: str, activity_id: str) -> SessionOutcome:
    if type(frame) is not dict or set(frame) != {"protocol", "run_tag", "activity_id", "outcome"}:
        raise ManagerControlError("SUP response identity mismatch")
    protocol = frame.get("protocol")
    if (
        type(protocol) is not int or protocol not in (2, 3)
        or frame.get("run_tag") != run_tag or frame.get("activity_id") != activity_id
    ):
        raise ManagerControlError("SUP response identity mismatch")
    data = frame.get("outcome")
    expected = _OUTER3_OUTCOME_FIELDS if protocol == 3 else _OUTER2_OUTCOME_FIELDS
    if type(data) is not dict or set(data) != set(expected):
        raise ManagerControlError("SUP response shape invalid")
    if data.get("run_tag") != run_tag or data.get("activity_id") != activity_id:
        raise ManagerControlError("SUP outcome identity mismatch")
    errors = data.get("cleanup_errors")
    timing = data.get("timing_diagnostic")
    if type(errors) is not list or any(type(item) is not str or len(item) > 128 for item in errors):
        raise ManagerControlError("SUP cleanup field invalid")
    if timing is not None and (type(timing) is not list or len(timing) != 5 or any(type(item) is not int for item in timing)):
        raise ManagerControlError("SUP timing field invalid")
    data["cleanup_errors"] = tuple(errors)
    data["timing_diagnostic"] = tuple(timing) if timing is not None else None
    if protocol == 2:
        # 外2精确旧字段集：排除新tool_receipt并补默认。
        data["tool_receipt"] = None
    else:
        receipt = data.get("tool_receipt")
        if receipt is not None and type(receipt) is not dict:
            raise ManagerControlError("SUP tool receipt field invalid")
    return SessionOutcome(**data)


def run_supervised_window(
    ledger: PostgresAdmissionLedger,
    config: SessionConfig,
    activity_id: str,
    executor_id: str,
    command: WorkerCommand,
    *,
    run_tag: str,
    one_call: OneCallInput | None = None,
    tool_action: ToolExecutionInput | None = None,
) -> SessionOutcome:
    """Blocking internal entry; no application event-loop or business grant."""
    if os.name != "nt":
        raise RuntimeError("Windows only")
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        pass
    else:
        raise RuntimeError("launcher cannot run in application event loop")

    started_ns = time.monotonic_ns()
    deadline_ns = started_ns + int(config.manager_total_seconds * 1e9)
    run_deadline_ns = deadline_ns - int(config.cleanup_seconds * 1e9)
    mapping_name = "Local\\RetroLume.SUP." + secrets.token_hex(16)
    request = _request(ledger, config, activity_id, executor_id, command, run_tag, mapping_name, deadline_ns,
                       one_call, tool_action)
    mapping = None
    process = None
    outcome = None
    failure: BaseException | None = None
    state = "launcher_failed_unconfirmed"
    errors: list[str] = []
    manager_pid = None
    manager_created = None
    exited = False
    try:
        if _remaining(run_deadline_ns) <= 0:
            state = "manager_startup_deadline_unconfirmed"
        else:
            mapping = NamedMapping.create(mapping_name)
            mapping.write_request(request)
            if _remaining(run_deadline_ns) <= 0:
                state = "manager_startup_deadline_unconfirmed"
            else:
                try:
                    process = _SuspendedSupervisor.create(mapping_name)
                except ProcessCreationError as exc:
                    process = exc.partial
                    raise
                manager_pid = process.pid
                manager_created = process.creation_time_100ns()
                if _remaining(run_deadline_ns) <= 0:
                    state = "manager_startup_deadline_unconfirmed"
                else:
                    process.resume()
                    state = "supervisor_lost_unconfirmed"
                    exited = process.wait(_remaining(run_deadline_ns))
                    if not exited:
                        state = "manager_timeout_unconfirmed"
                    elif process.exit_code() == 0:
                        outcome = _decode_outcome(mapping.read_result(), run_tag, activity_id)
                        if outcome.model_receipt is not None:
                            if one_call is None or outcome.generation is None:
                                raise ManagerControlError("unexpected business receipt")
                            context = CallContext.model_validate(outcome.model_receipt.get("context"), strict=True)
                            if (context.activity_id != activity_id or context.executor_id != executor_id
                                    or context.operation_id != one_call.operation_id
                                    or context.execution_generation != outcome.generation):
                                raise ManagerControlError("business identity mismatch")
                            result = decode_receipt(outcome.model_receipt, context, run_tag)
                            if result.provider != one_call.service.provider or result.configured_model != one_call.service.model:
                                raise ManagerControlError("business model mismatch")
                        elif outcome.tool_receipt is not None:
                            if tool_action is None or outcome.generation is None:
                                raise ManagerControlError("unexpected business receipt")
                            context = CallContext.model_validate(outcome.tool_receipt.get("context"), strict=True)
                            if (context.activity_id != activity_id or context.executor_id != executor_id
                                    or context.operation_id != tool_action.operation_id
                                    or context.execution_generation != outcome.generation):
                                raise ManagerControlError("business identity mismatch")
                            decode_tool_receipt(outcome.tool_receipt, context, run_tag, tool_action)
                        elif (one_call is not None or tool_action is not None) and outcome.state == "settled":
                            raise ManagerControlError("missing business receipt")
    except BaseException as exc:
        outcome = None
        failure = exc
        errors.append(f"launcher:{type(exc).__name__}")
    finally:
        if process is not None:
            try:
                exited = process.wait(0)
            except BaseException as exc:
                errors.append(f"exit_query:{type(exc).__name__}")
            if not exited:
                try:
                    process.terminate()
                except BaseException as exc:
                    errors.append(f"terminate:{type(exc).__name__}")
                try:
                    exited = process.wait(_remaining(deadline_ns))
                except BaseException as exc:
                    errors.append(f"exit_wait:{type(exc).__name__}")
            if not exited:
                errors.append("supervisor_exit_unknown")
            try:
                process.close()
            except BaseException as exc:
                errors.append(f"process_close:{type(exc).__name__}")
        if mapping is not None:
            try:
                mapping.close()
            except BaseException as exc:
                errors.append(f"mapping_close:{type(exc).__name__}")

    if outcome is not None:
        outcome = replace(outcome, manager_pid=manager_pid, manager_created_100ns=manager_created)
        if errors:
            outcome = replace(
                outcome,
                state="settled_cleanup_error" if outcome.state == "settled" else outcome.state,
                cleanup_incomplete=True,
                cleanup_errors=outcome.cleanup_errors + tuple(errors),
            )
    else:
        outcome = SessionOutcome(
            run_tag, state, activity_id,
            settled_seconds=None, reserved_seconds=None, pending_fold_seconds=None,
            cleanup_incomplete=True,
            error_type=type(failure).__name__ if failure is not None else state,
            cleanup_errors=tuple(errors),
            manager_pid=manager_pid, manager_created_100ns=manager_created,
        )
    if isinstance(failure, (KeyboardInterrupt, SystemExit, asyncio.CancelledError)):
        failure.session_outcome = outcome
        raise failure
    return outcome

