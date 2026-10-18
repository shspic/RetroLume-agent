"""用 Windows Job Object 启动并监督单个受限子进程。"""
from __future__ import annotations

from dataclasses import dataclass
import ctypes
from ctypes import wintypes
import os
import subprocess
import time


CREATE_SUSPENDED = 0x00000004
CREATE_NO_WINDOW = 0x08000000
JOB_OBJECT_LIMIT_ACTIVE_PROCESS = 0x00000008
JOB_OBJECT_LIMIT_PROCESS_MEMORY = 0x00000100
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
JOB_OBJECT_EXTENDED_LIMIT_INFORMATION_CLASS = 9
WAIT_OBJECT_0 = 0x00000000
WAIT_TIMEOUT = 0x00000102


class JobSetupError(RuntimeError):
    pass


class JobTimeout(RuntimeError):
    pass


@dataclass(frozen=True)
class JobResult:
    exit_code: int
    elapsed_seconds: float


class _STARTUPINFOW(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("lpReserved", wintypes.LPWSTR),
        ("lpDesktop", wintypes.LPWSTR),
        ("lpTitle", wintypes.LPWSTR),
        ("dwX", wintypes.DWORD),
        ("dwY", wintypes.DWORD),
        ("dwXSize", wintypes.DWORD),
        ("dwYSize", wintypes.DWORD),
        ("dwXCountChars", wintypes.DWORD),
        ("dwYCountChars", wintypes.DWORD),
        ("dwFillAttribute", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("wShowWindow", wintypes.WORD),
        ("cbReserved2", wintypes.WORD),
        ("lpReserved2", ctypes.POINTER(ctypes.c_ubyte)),
        ("hStdInput", wintypes.HANDLE),
        ("hStdOutput", wintypes.HANDLE),
        ("hStdError", wintypes.HANDLE),
    ]


class _PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("hProcess", wintypes.HANDLE),
        ("hThread", wintypes.HANDLE),
        ("dwProcessId", wintypes.DWORD),
        ("dwThreadId", wintypes.DWORD),
    ]


class _IO_COUNTERS(ctypes.Structure):
    _fields_ = [(name, ctypes.c_ulonglong) for name in (
        "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
        "ReadTransferCount", "WriteTransferCount", "OtherTransferCount",
    )]


class _JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_longlong),
        ("PerJobUserTimeLimit", ctypes.c_longlong),
        ("LimitFlags", wintypes.DWORD),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", wintypes.DWORD),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", wintypes.DWORD),
        ("SchedulingClass", wintypes.DWORD),
    ]


class _JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", _JOBOBJECT_BASIC_LIMIT_INFORMATION),
        ("IoInfo", _IO_COUNTERS),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


def run_in_job(command: list[str], *, cwd: str, timeout_seconds: float, memory_bytes: int) -> JobResult:
    if os.name != "nt":
        raise JobSetupError("Windows Job Object is unavailable on this platform")

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _configure_signatures(kernel32)
    job = kernel32.CreateJobObjectW(None, None)
    if not job:
        raise JobSetupError(_last_error("CreateJobObjectW"))

    process_info = _PROCESS_INFORMATION()
    process_created = False
    assigned = False
    started = time.monotonic()
    try:
        limits = _JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        limits.BasicLimitInformation.LimitFlags = (
            JOB_OBJECT_LIMIT_ACTIVE_PROCESS
            | JOB_OBJECT_LIMIT_PROCESS_MEMORY
            | JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        )
        # Windows venv 的 python.exe 是转发器，会再启动真正解释器；两者均留在同一 Job。
        limits.BasicLimitInformation.ActiveProcessLimit = 2
        limits.ProcessMemoryLimit = memory_bytes
        if not kernel32.SetInformationJobObject(
            job,
            JOB_OBJECT_EXTENDED_LIMIT_INFORMATION_CLASS,
            ctypes.byref(limits),
            ctypes.sizeof(limits),
        ):
            raise JobSetupError(_last_error("SetInformationJobObject"))

        startup = _STARTUPINFOW()
        startup.cb = ctypes.sizeof(startup)
        command_line = ctypes.create_unicode_buffer(subprocess.list2cmdline(command))
        if not kernel32.CreateProcessW(
            None,
            command_line,
            None,
            None,
            False,
            CREATE_SUSPENDED | CREATE_NO_WINDOW,
            None,
            cwd,
            ctypes.byref(startup),
            ctypes.byref(process_info),
        ):
            raise JobSetupError(_last_error("CreateProcessW"))
        process_created = True

        if not kernel32.AssignProcessToJobObject(job, process_info.hProcess):
            raise JobSetupError(_last_error("AssignProcessToJobObject"))
        assigned = True
        if kernel32.ResumeThread(process_info.hThread) == 0xFFFFFFFF:
            raise JobSetupError(_last_error("ResumeThread"))

        wait_ms = max(1, int(timeout_seconds * 1000))
        wait_result = kernel32.WaitForSingleObject(process_info.hProcess, wait_ms)
        if wait_result == WAIT_TIMEOUT:
            kernel32.TerminateJobObject(job, 1)
            kernel32.WaitForSingleObject(process_info.hProcess, 5000)
            raise JobTimeout(f"PDF worker exceeded {timeout_seconds:g} seconds")
        if wait_result != WAIT_OBJECT_0:
            raise JobSetupError(_last_error("WaitForSingleObject"))

        exit_code = wintypes.DWORD()
        if not kernel32.GetExitCodeProcess(process_info.hProcess, ctypes.byref(exit_code)):
            raise JobSetupError(_last_error("GetExitCodeProcess"))
        return JobResult(exit_code=exit_code.value, elapsed_seconds=time.monotonic() - started)
    finally:
        if process_created and not assigned:
            kernel32.TerminateProcess(process_info.hProcess, 1)
            kernel32.WaitForSingleObject(process_info.hProcess, 5000)
        if process_info.hThread:
            kernel32.CloseHandle(process_info.hThread)
        if process_info.hProcess:
            kernel32.CloseHandle(process_info.hProcess)
        kernel32.CloseHandle(job)


def _last_error(operation: str) -> str:
    code = ctypes.get_last_error()
    return f"{operation} failed with Windows error {code}: {ctypes.FormatError(code).strip()}"


def _configure_signatures(kernel32: ctypes.WinDLL) -> None:
    kernel32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    kernel32.CreateJobObjectW.restype = wintypes.HANDLE
    kernel32.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    kernel32.SetInformationJobObject.restype = wintypes.BOOL
    kernel32.CreateProcessW.argtypes = [
        wintypes.LPCWSTR, wintypes.LPWSTR, ctypes.c_void_p, ctypes.c_void_p,
        wintypes.BOOL, wintypes.DWORD, ctypes.c_void_p, wintypes.LPCWSTR,
        ctypes.POINTER(_STARTUPINFOW), ctypes.POINTER(_PROCESS_INFORMATION),
    ]
    kernel32.CreateProcessW.restype = wintypes.BOOL
    kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
    kernel32.ResumeThread.argtypes = [wintypes.HANDLE]
    kernel32.ResumeThread.restype = wintypes.DWORD
    kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel32.WaitForSingleObject.restype = wintypes.DWORD
    kernel32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    kernel32.GetExitCodeProcess.restype = wintypes.BOOL
    kernel32.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
    kernel32.TerminateJobObject.restype = wintypes.BOOL
    kernel32.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
    kernel32.TerminateProcess.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
