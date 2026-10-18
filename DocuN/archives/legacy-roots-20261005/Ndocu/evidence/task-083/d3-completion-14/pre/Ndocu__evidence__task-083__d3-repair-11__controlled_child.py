"""Test-only suspended child and outer Windows Job owner; never owns a business Job handle."""
from __future__ import annotations

import ctypes
from ctypes import wintypes
import msvcrt
import os
from pathlib import Path
import queue
import subprocess
import threading
import time

from app.worker.windows_job import (
    _BASIC_ACCOUNTING, _EXTENDED_LIMIT, _FILETIME, _PROCESS_INFORMATION,
    _STARTUPINFOW, _kernel, CREATE_NO_WINDOW, CREATE_SUSPENDED,
    JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION_CLASS, JOB_OBJECT_EXTENDED_LIMIT_INFORMATION_CLASS,
    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE, WAIT_OBJECT_0,
)

CREATE_UNICODE_ENVIRONMENT = 0x00000400
STARTF_USESTDHANDLES = 0x00000100


class OwnershipUnknown(RuntimeError):
    pass


def remaining(deadline: float, *, reserve: float = 0) -> float:
    value = deadline - time.monotonic() - reserve
    if value <= 0:
        raise TimeoutError("absolute deadline or cleanup reserve exhausted")
    return value


class ControlledChild:
    def __init__(self, api=None):
        self.api = api or _kernel()
        self.job = None
        self.process = _PROCESS_INFORMATION()
        self.assigned = False
        self.resumed = False
        self.created_100ns = None
        self.cleanup_confirmed = False
        self.lines = queue.Queue()
        self.readers = []
        self._reads = []

    @staticmethod
    def _error(operation):
        return OwnershipUnknown(f"{operation} Windows error {ctypes.get_last_error()}")

    def active(self):
        if not self.job:
            raise OwnershipUnknown("outer Job handle unavailable")
        info = _BASIC_ACCOUNTING()
        if not self.api.QueryInformationJobObject(self.job, JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION_CLASS,
                                                   ctypes.byref(info), ctypes.sizeof(info), None):
            raise self._error("QueryInformationJobObject")
        return int(info.ActiveProcesses)

    def _creation_time(self):
        values = [_FILETIME() for _ in range(4)]
        if not self.api.GetProcessTimes(self.process.hProcess, *(ctypes.byref(x) for x in values)):
            raise self._error("GetProcessTimes")
        return (int(values[0].dwHighDateTime) << 32) | int(values[0].dwLowDateTime)

    def _read_stream(self, fd: int, label: str):
        try:
            with os.fdopen(fd, "rb", buffering=0) as stream:
                for raw in stream:
                    self.lines.put((label, raw.decode("utf-8", errors="replace")))
        finally:
            self.lines.put((label, None))

    def start(self, command: list[str], *, cwd: Path, env: dict[str, str], deadline: float):
        """Create suspended, record exact identity, assign outer Job, then Resume."""
        remaining(deadline, reserve=1)
        if not command or not Path(command[0]).is_absolute() or not cwd.is_dir():
            raise ValueError("absolute executable and existing cwd required")
        if self.job or self.process.hProcess:
            raise OwnershipUnknown("controlled child already started")
        self.job = self.api.CreateJobObjectW(None, None)  # unnamed, non-inheritable, distinct from business Job
        if not self.job:
            raise self._error("CreateJobObjectW")
        limits = _EXTENDED_LIMIT()
        limits.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not self.api.SetInformationJobObject(self.job, JOB_OBJECT_EXTENDED_LIMIT_INFORMATION_CLASS,
                                                 ctypes.byref(limits), ctypes.sizeof(limits)):
            error = self._error("SetInformationJobObject")
            self.close()
            raise error
        writes = []
        devnull = None
        try:
            devnull = open(os.devnull, "rb", buffering=0)
            os.set_handle_inheritable(msvcrt.get_osfhandle(devnull.fileno()), True)
            for label in ("stdout", "stderr"):
                read_fd, write_fd = os.pipe()
                self._reads.append((read_fd, label))
                writes.append(write_fd)
                os.set_handle_inheritable(msvcrt.get_osfhandle(write_fd), True)
            startup = _STARTUPINFOW()
            startup.cb = ctypes.sizeof(startup)
            startup.dwFlags = STARTF_USESTDHANDLES
            startup.hStdInput = msvcrt.get_osfhandle(devnull.fileno())
            startup.hStdOutput = msvcrt.get_osfhandle(writes[0])
            startup.hStdError = msvcrt.get_osfhandle(writes[1])
            cmdline = ctypes.create_unicode_buffer(subprocess.list2cmdline(command))
            env_block = ctypes.create_unicode_buffer("\0".join(f"{k}={v}" for k, v in sorted(env.items())) + "\0\0")
            remaining(deadline, reserve=1)
            if not self.api.CreateProcessW(None, cmdline, None, None, True,
                                           CREATE_SUSPENDED | CREATE_NO_WINDOW | CREATE_UNICODE_ENVIRONMENT,
                                           ctypes.cast(env_block, ctypes.c_void_p), str(cwd),
                                           ctypes.byref(startup), ctypes.byref(self.process)):
                raise self._error("CreateProcessW")
            self.created_100ns = self._creation_time()
            if not self.created_100ns or not self.process.dwProcessId:
                raise OwnershipUnknown("suspended child identity unavailable")
            if not self.api.AssignProcessToJobObject(self.job, self.process.hProcess):
                raise self._error("AssignProcessToJobObject")
            self.assigned = True
            if self.active() != 1:
                raise OwnershipUnknown("outer Job did not report suspended child")
            remaining(deadline, reserve=1)
            if self.api.ResumeThread(self.process.hThread) == 0xFFFFFFFF:
                raise self._error("ResumeThread")
            self.resumed = True
            for read_fd, label in self._reads:
                reader = threading.Thread(target=self._read_stream, args=(read_fd, label), daemon=True)
                reader.start()
                self.readers.append(reader)
            self._reads = []
            return {"pid": int(self.process.dwProcessId), "created_100ns": self.created_100ns}
        except BaseException:
            try:
                self.stop(deadline)
            finally:
                self.close()
            raise
        finally:
            for fd in writes:
                os.close(fd)
            if devnull is not None:
                devnull.close()

    def exit_code(self):
        if not self.process.hProcess or self.api.WaitForSingleObject(self.process.hProcess, 0) != WAIT_OBJECT_0:
            return None
        code = wintypes.DWORD()
        if not self.api.GetExitCodeProcess(self.process.hProcess, ctypes.byref(code)):
            raise self._error("GetExitCodeProcess")
        return int(code.value)

    def stop(self, deadline: float):
        """Terminate only owned handles and prove outer Job ActiveProcesses==0."""
        if self.process.hProcess and not self.assigned:
            if not self.api.TerminateProcess(self.process.hProcess, 1):
                raise self._error("TerminateProcess(suspended)")
            ms = int(remaining(deadline) * 1000)
            if ms < 1:
                raise TimeoutError("suspended child cleanup deadline")
            if self.api.WaitForSingleObject(self.process.hProcess, ms) != WAIT_OBJECT_0:
                raise OwnershipUnknown("unassigned suspended child exit not confirmed")
        if self.assigned:
            if self.active() and not self.api.TerminateJobObject(self.job, 1):
                raise self._error("TerminateJobObject(outer)")
            while self.active():
                time.sleep(min(.05, remaining(deadline)))
        self.cleanup_confirmed = True
        return True

    def wait_empty(self, deadline: float):
        while True:
            exit_code = self.exit_code()
            count = self.active()
            if exit_code is not None and count == 0:
                self.cleanup_confirmed = True
                return exit_code
            time.sleep(min(.05, remaining(deadline)))

    def close(self):
        errors = []
        for holder, field in ((self.process, "hThread"), (self.process, "hProcess"), (self, "job")):
            handle = getattr(holder, field)
            if handle:
                if self.api.CloseHandle(handle):
                    setattr(holder, field, None)
                else:
                    errors.append(field)
        for fd, _ in self._reads:
            os.close(fd)
        self._reads = []
        if errors:
            self.cleanup_confirmed = False
            raise OwnershipUnknown("CloseHandle failed: " + ",".join(errors))