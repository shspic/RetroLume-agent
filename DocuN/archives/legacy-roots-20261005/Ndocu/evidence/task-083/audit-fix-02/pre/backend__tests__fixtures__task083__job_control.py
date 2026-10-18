"""TASK-083 场景04控制者：只备代码，Job复检冻结期间不得调用。"""

from __future__ import annotations

import asyncio
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import sys
import time
from uuid import uuid4

from app.worker.windows_job import NamedJob, _FILETIME, job_name


async def verify_last_handle(fixture: Path, backend: Path) -> dict:
    activity_id = str(uuid4())
    run_tag = "job-death-" + uuid4().hex[:8]
    generation = 7
    deadline_ns = time.monotonic_ns() + 20_000_000_000

    def remaining(cap: float = 5.0) -> float:
        value = min(cap, (deadline_ns - time.monotonic_ns()) / 1e9)
        if value <= 0:
            raise TimeoutError("场景控制者总期限已耗尽")
        return value

    # Python 3.12 Windows spawn同法绕过venv转发器，同时保留venv依赖路径。
    child_env = os.environ.copy()
    child_env["__PYVENV_LAUNCHER__"] = sys.executable
    proc = await asyncio.wait_for(asyncio.create_subprocess_exec(
        sys._base_executable, "-B", str(fixture), "controller", activity_id, str(generation), run_tag,
        cwd=str(backend), env=child_env, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    ), timeout=remaining())
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.GetProcessTimes.argtypes = [wintypes.HANDLE, *([ctypes.POINTER(_FILETIME)] * 4)]
    kernel.GetProcessTimes.restype = wintypes.BOOL
    kernel.OpenEventW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
    kernel.OpenEventW.restype = wintypes.HANDLE
    kernel.SetEvent.argtypes = [wintypes.HANDLE]
    kernel.SetEvent.restype = wintypes.BOOL
    kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel.WaitForSingleObject.restype = wintypes.DWORD
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    kernel.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
    kernel.TerminateProcess.restype = wintypes.BOOL

    worker_handle = None
    parent_job = None
    events = []
    verified = False
    try:
        line = await asyncio.wait_for(proc.stdout.readline(), timeout=remaining())
        if not line:
            raise AssertionError("SUP未在有限时间提供悬停worker身份")
        created = json.loads(line)
        expected = ("suspended", activity_id, generation, run_tag, job_name(activity_id, generation))
        actual = tuple(created[key] for key in ("phase", "activity_id", "generation", "run_tag", "job_name"))
        if actual != expected:
            raise AssertionError("Job/G/runTag身份不匹配")
        worker_handle = kernel.OpenProcess(0x00100000 | 0x1000, False, created["pid"])
        if not worker_handle:
            raise AssertionError("无法取得真实受控进程的精确句柄")
        times = [_FILETIME() for _ in range(4)]
        if not kernel.GetProcessTimes(worker_handle, *(ctypes.byref(x) for x in times)):
            raise AssertionError("无法核对受控进程创建时间")
        stamp = (int(times[0].dwHighDateTime) << 32) | int(times[0].dwLowDateTime)
        if stamp != created["created_100ns"]:
            raise AssertionError("PID创建时间不匹配")
        verified = True
        parent_job = NamedJob.open_existing(activity_id, generation)
        active_before = parent_job.active_processes()
        if active_before <= 0:
            raise AssertionError("Resume前Job中没有悬停worker")
        base = f"Local\\RetroLume.Task083.{activity_id}.G{generation}.{run_tag}"
        for suffix in ("Arm", "Exit"):
            event = kernel.OpenEventW(0x0002, False, f"{base}.{suffix}")
            if not event:
                raise AssertionError("控制事件归属不明")
            events.append(event)
        # 独立截止、精确Job和worker句柄均已取得，才允许Resume。
        if not kernel.SetEvent(events[0]):
            raise AssertionError("Arm事件设置失败")
        resumed_line = await asyncio.wait_for(proc.stdout.readline(), timeout=remaining())
        if not resumed_line:
            raise AssertionError("SUP未确认Resume")
        resumed = json.loads(resumed_line)
        if (resumed["phase"], resumed["pid"]) != ("resumed", created["pid"]):
            raise AssertionError("Resume回执身份不匹配")
        parent_job.close()
        parent_job = None  # 此后SUP独占Job最后句柄。
        if not kernel.SetEvent(events[1]):
            raise AssertionError("退出事件设置失败")
        await asyncio.wait_for(proc.wait(), timeout=remaining())
        if proc.returncode != 0:
            raise AssertionError(f"SUP退出码={proc.returncode}")
        if kernel.WaitForSingleObject(worker_handle, int(remaining(4) * 1000)) != 0:
            raise AssertionError("最后Job句柄关闭后worker未退出")
        return {**created, "active_processes_before_supervisor_exit": active_before,
                "worker_signaled_after_last_job_handle_closed": True}
    finally:
        primary = sys.exc_info()[1]
        failures = []
        if parent_job is not None:
            try:
                parent_job.close()
            except BaseException as exc:
                failures.append(f"parent_job_close:{type(exc).__name__}")
        if proc.returncode is None:
            try:
                proc.kill()  # 精确控制者对象，不按名称或裸PID终止。
                wait = max(0.1, min(4.0, (deadline_ns - time.monotonic_ns()) / 1e9))
                await asyncio.wait_for(proc.wait(), timeout=wait)
            except BaseException as exc:
                failures.append(f"controller_stop:{type(exc).__name__}")
        if worker_handle:
            if verified and kernel.WaitForSingleObject(worker_handle, 0) != 0:
                if not kernel.TerminateProcess(worker_handle, 1) or kernel.WaitForSingleObject(worker_handle, 4000) != 0:
                    failures.append("exact_worker_stop_unconfirmed")
            if not kernel.CloseHandle(worker_handle):
                failures.append("worker_handle_close")
        for event in events:
            if not kernel.CloseHandle(event):
                failures.append("event_close")
        if failures:
            detail = "cleanup_incomplete:" + ",".join(failures)
            if primary is not None:
                primary.add_note(detail)
            else:
                raise AssertionError(detail)
