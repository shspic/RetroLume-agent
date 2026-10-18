"""精确命名的 Windows Job 和活动级互斥所有权；不依赖进程名/端口。"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
import os
import subprocess
import time
from uuid import UUID


CREATE_SUSPENDED = 0x00000004
CREATE_NO_WINDOW = 0x08000000
JOB_OBJECT_LIMIT_ACTIVE_PROCESS = 0x00000008
JOB_OBJECT_LIMIT_JOB_MEMORY = 0x00000200
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
JOB_OBJECT_EXTENDED_LIMIT_INFORMATION_CLASS = 9
JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION_CLASS = 1
JOB_OBJECT_QUERY = 0x0004
JOB_OBJECT_TERMINATE = 0x0008
ERROR_ALREADY_EXISTS = 183
ERROR_FILE_NOT_FOUND = 2
ERROR_ACCESS_DENIED = 5
WAIT_OBJECT_0 = 0
WAIT_ABANDONED = 0x80
WAIT_TIMEOUT = 0x102


class JobUnknown(RuntimeError):
    """不能确认Job身份、状态或终止结果；调用者必须失败关闭。"""


class JobOpenError(JobUnknown):
    """保留 OpenJobObjectW 的原始 Windows 错误码。"""

    def __init__(self, code: int):
        self.code = code
        super().__init__(f"OpenJobObjectW Windows error {code}")


class _STARTUPINFOW(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD), ("lpReserved", wintypes.LPWSTR),
        ("lpDesktop", wintypes.LPWSTR), ("lpTitle", wintypes.LPWSTR),
        ("dwX", wintypes.DWORD), ("dwY", wintypes.DWORD),
        ("dwXSize", wintypes.DWORD), ("dwYSize", wintypes.DWORD),
        ("dwXCountChars", wintypes.DWORD), ("dwYCountChars", wintypes.DWORD),
        ("dwFillAttribute", wintypes.DWORD), ("dwFlags", wintypes.DWORD),
        ("wShowWindow", wintypes.WORD), ("cbReserved2", wintypes.WORD),
        ("lpReserved2", ctypes.POINTER(ctypes.c_ubyte)),
        ("hStdInput", wintypes.HANDLE), ("hStdOutput", wintypes.HANDLE),
        ("hStdError", wintypes.HANDLE),
    ]


class _PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("hProcess", wintypes.HANDLE), ("hThread", wintypes.HANDLE),
        ("dwProcessId", wintypes.DWORD), ("dwThreadId", wintypes.DWORD),
    ]


class _FILETIME(ctypes.Structure):
    _fields_ = [("dwLowDateTime", wintypes.DWORD), ("dwHighDateTime", wintypes.DWORD)]


class _IO_COUNTERS(ctypes.Structure):
    _fields_ = [(name, ctypes.c_ulonglong) for name in (
        "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
        "ReadTransferCount", "WriteTransferCount", "OtherTransferCount",
    )]


class _BASIC_LIMIT(ctypes.Structure):
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


class _EXTENDED_LIMIT(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", _BASIC_LIMIT), ("IoInfo", _IO_COUNTERS),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


class _BASIC_ACCOUNTING(ctypes.Structure):
    # JOBOBJECT_BASIC_ACCOUNTING_INFORMATION.ActiveProcesses 是官方字段名。
    _fields_ = [
        ("TotalUserTime", ctypes.c_longlong),
        ("TotalKernelTime", ctypes.c_longlong),
        ("ThisPeriodTotalUserTime", ctypes.c_longlong),
        ("ThisPeriodTotalKernelTime", ctypes.c_longlong),
        ("TotalPageFaultCount", wintypes.DWORD),
        ("TotalProcesses", wintypes.DWORD),
        ("ActiveProcesses", wintypes.DWORD),
        ("TotalTerminatedProcesses", wintypes.DWORD),
    ]


def _kernel():
    if os.name != "nt":
        raise JobUnknown("Windows Job不可用")
    api = ctypes.WinDLL("kernel32", use_last_error=True)
    api.GetCurrentProcessId.argtypes = []
    api.GetCurrentProcessId.restype = wintypes.DWORD
    api.ProcessIdToSessionId.argtypes = [wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
    api.ProcessIdToSessionId.restype = wintypes.BOOL
    api.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
    api.CreateMutexW.restype = wintypes.HANDLE
    api.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    api.WaitForSingleObject.restype = wintypes.DWORD
    api.ReleaseMutex.argtypes = [wintypes.HANDLE]
    api.ReleaseMutex.restype = wintypes.BOOL
    api.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    api.CreateJobObjectW.restype = wintypes.HANDLE
    api.OpenJobObjectW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
    api.OpenJobObjectW.restype = wintypes.HANDLE
    api.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    api.SetInformationJobObject.restype = wintypes.BOOL
    api.QueryInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.c_void_p]
    api.QueryInformationJobObject.restype = wintypes.BOOL
    api.CreateProcessW.argtypes = [
        wintypes.LPCWSTR, wintypes.LPWSTR, ctypes.c_void_p, ctypes.c_void_p,
        wintypes.BOOL, wintypes.DWORD, ctypes.c_void_p, wintypes.LPCWSTR,
        ctypes.POINTER(_STARTUPINFOW), ctypes.POINTER(_PROCESS_INFORMATION),
    ]
    api.CreateProcessW.restype = wintypes.BOOL
    api.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    api.AssignProcessToJobObject.restype = wintypes.BOOL
    api.ResumeThread.argtypes = [wintypes.HANDLE]
    api.ResumeThread.restype = wintypes.DWORD
    api.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
    api.TerminateJobObject.restype = wintypes.BOOL
    api.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
    api.TerminateProcess.restype = wintypes.BOOL
    api.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    api.GetExitCodeProcess.restype = wintypes.BOOL
    api.GetProcessTimes.argtypes = [wintypes.HANDLE, ctypes.POINTER(_FILETIME), ctypes.POINTER(_FILETIME), ctypes.POINTER(_FILETIME), ctypes.POINTER(_FILETIME)]
    api.GetProcessTimes.restype = wintypes.BOOL
    api.CloseHandle.argtypes = [wintypes.HANDLE]
    api.CloseHandle.restype = wintypes.BOOL
    return api


def _error(action: str) -> JobUnknown:
    return JobUnknown(f"{action} Windows error {ctypes.get_last_error()}")


def current_process_session_id() -> int:
    """可信 SUP 自身进程的 Windows 会话号；读取失败不得启动工作。"""
    api = _kernel()
    session = wintypes.DWORD()
    if not api.ProcessIdToSessionId(api.GetCurrentProcessId(), ctypes.byref(session)):
        raise _error("ProcessIdToSessionId")
    return int(session.value)


def _activity_key(activity_id: str) -> str:
    return UUID(activity_id).hex


def job_name(activity_id: str, generation: int) -> str:
    if isinstance(generation, bool) or not isinstance(generation, int) or generation < 0:
        raise ValueError("Job代次非法")
    return f"Local\\RetroLume.Activity.{_activity_key(activity_id)}.G{generation}"


class ActivityMutex:
    """同一Windows登录会话内活动排他；跨会话找不到旧Job时一律失败关闭。"""

    def __init__(self, activity_id: str, *, wait_seconds: float = 3.0):
        self.api = _kernel()
        self.name = f"Local\\RetroLume.Activity.{_activity_key(activity_id)}.Owner"
        self.handle = self.api.CreateMutexW(None, False, self.name)
        if not self.handle:
            raise _error("CreateMutexW")
        self.owned = False
        result = self.api.WaitForSingleObject(self.handle, max(1, int(wait_seconds * 1000)))
        if result not in (WAIT_OBJECT_0, WAIT_ABANDONED):
            self.api.CloseHandle(self.handle)
            self.handle = None
            raise JobUnknown(f"活动排他所有权不可得: wait={result}")
        self.owned = True

    def close(self) -> None:
        failures = []
        if self.owned:
            if not self.api.ReleaseMutex(self.handle):
                failures.append("ReleaseMutex")
            else:
                self.owned = False
        if self.handle:
            if not self.api.CloseHandle(self.handle):
                failures.append("CloseHandle(mutex)")
            else:
                self.handle = None
        if failures:
            raise JobUnknown("/".join(failures))

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


class NamedJob:
    """仅操作确切名字的Job；ActiveProcesses==0才提供整树退出正证据。"""

    def __init__(self, api, handle, name: str):
        self.api = api
        self.handle = handle
        self.name = name
        self.process = _PROCESS_INFORMATION()

    @classmethod
    def create(cls, activity_id: str, generation: int, *, max_processes: int = 4, memory_bytes: int = 256 * 1024 * 1024):
        if not 1 <= max_processes <= 4 or not 1 <= memory_bytes <= 256 * 1024 * 1024:
            raise ValueError("Job资源上限超出本卡边界")
        api = _kernel()
        name = job_name(activity_id, generation)
        ctypes.set_last_error(0)
        handle = api.CreateJobObjectW(None, name)  # 当前用户默认DACL；返回句柄不可继承。
        if not handle:
            raise _error("CreateJobObjectW")
        code = ctypes.get_last_error()
        if code == ERROR_ALREADY_EXISTS:
            api.CloseHandle(handle)
            raise JobUnknown("同名Job已存在，拒绝碰撞")
        job = cls(api, handle, name)
        try:
            limits = _EXTENDED_LIMIT()
            limits.BasicLimitInformation.LimitFlags = (
                JOB_OBJECT_LIMIT_ACTIVE_PROCESS | JOB_OBJECT_LIMIT_JOB_MEMORY
                | JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
            )
            limits.BasicLimitInformation.ActiveProcessLimit = max_processes
            limits.JobMemoryLimit = memory_bytes
            if not api.SetInformationJobObject(handle, JOB_OBJECT_EXTENDED_LIMIT_INFORMATION_CLASS, ctypes.byref(limits), ctypes.sizeof(limits)):
                raise _error("SetInformationJobObject")
            return job
        except BaseException:
            job.close()
            raise

    @classmethod
    def open_existing(cls, activity_id: str, generation: int):
        api = _kernel()
        name = job_name(activity_id, generation)
        handle = api.OpenJobObjectW(JOB_OBJECT_QUERY | JOB_OBJECT_TERMINATE, False, name)
        if not handle:
            # 只有 ERROR_FILE_NOT_FOUND 可成为同会话旧树不存在的候选证据。
            raise JobOpenError(ctypes.get_last_error())
        return cls(api, handle, name)

    def spawn_suspended(self, command: list[str], *, cwd: str) -> int:
        if not command or not os.path.isabs(command[0]) or not os.path.isdir(cwd):
            raise ValueError("worker命令须使用绝对可执行文件和既有工作目录")
        if self.process.hProcess:
            raise JobUnknown("单窗Job不能再次创建worker")
        startup = _STARTUPINFOW()
        startup.cb = ctypes.sizeof(startup)
        command_line = ctypes.create_unicode_buffer(subprocess.list2cmdline(command))
        created = self.api.CreateProcessW(
            None, command_line, None, None, False,
            CREATE_SUSPENDED | CREATE_NO_WINDOW, None, cwd,
            ctypes.byref(startup), ctypes.byref(self.process),
        )
        if not created:
            raise _error("CreateProcessW")
        try:
            if not self.api.AssignProcessToJobObject(self.handle, self.process.hProcess):
                raise _error("AssignProcessToJobObject")
            return int(self.process.dwProcessId)
        except BaseException:
            # 仅终止刚刚由本对象创建且持精确句柄的悬停进程。
            self.api.TerminateProcess(self.process.hProcess, 1)
            self.api.WaitForSingleObject(self.process.hProcess, 1000)
            raise

    def resume(self) -> None:
        if not self.process.hThread:
            raise JobUnknown("worker尚未创建")
        if self.api.ResumeThread(self.process.hThread) == 0xFFFFFFFF:
            raise _error("ResumeThread")

    def active_processes(self) -> int:
        if not self.handle:
            raise JobUnknown("Job句柄已关闭")
        data = _BASIC_ACCOUNTING()
        if not self.api.QueryInformationJobObject(
            self.handle, JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION_CLASS,
            ctypes.byref(data), ctypes.sizeof(data), None,
        ):
            raise _error("QueryInformationJobObject")
        return int(data.ActiveProcesses)

    def wait_empty_until(self, deadline_ns: int) -> bool:
        while True:
            if self.active_processes() == 0:
                return True
            remaining = (deadline_ns - time.monotonic_ns()) / 1_000_000_000
            if remaining <= 0:
                return False
            time.sleep(min(0.05, remaining))

    def terminate(self) -> None:
        if self.active_processes() > 0 and not self.api.TerminateJobObject(self.handle, 1):
            raise _error("TerminateJobObject")

    def primary_exit_code(self) -> int:
        if not self.process.hProcess or self.api.WaitForSingleObject(self.process.hProcess, 0) != WAIT_OBJECT_0:
            raise JobUnknown("主进程尚未退出；不把其状态冒充Job树状态")
        code = wintypes.DWORD()
        if not self.api.GetExitCodeProcess(self.process.hProcess, ctypes.byref(code)):
            raise _error("GetExitCodeProcess")
        return int(code.value)

    def process_creation_time_100ns(self) -> int:
        if not self.process.hProcess:
            raise JobUnknown("主进程句柄不存在")
        created, exited, kernel, user = (_FILETIME() for _ in range(4))
        if not self.api.GetProcessTimes(self.process.hProcess, ctypes.byref(created), ctypes.byref(exited), ctypes.byref(kernel), ctypes.byref(user)):
            raise _error("GetProcessTimes")
        return (int(created.dwHighDateTime) << 32) | int(created.dwLowDateTime)

    @property
    def pid(self) -> int | None:
        return int(self.process.dwProcessId) if self.process.hProcess else None

    def close(self) -> None:
        failures = []
        for label, holder, field in (
            ("thread", self.process, "hThread"),
            ("process", self.process, "hProcess"),
            ("job", self, "handle"),
        ):
            handle = getattr(holder, field)
            if handle:
                if self.api.CloseHandle(handle):
                    setattr(holder, field, None)
                else:
                    failures.append(label)
        if failures:
            raise JobUnknown("CloseHandle失败: " + ",".join(failures))

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
