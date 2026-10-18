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
    starter = ctypes.WinDLL("kernel32", use_last_error=True)
    starter.CreateEventW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.BOOL, wintypes.LPCWSTR]
    starter.CreateEventW.restype = wintypes.HANDLE
    starter.SetEvent.argtypes = [wintypes.HANDLE]
    starter.SetEvent.restype = wintypes.BOOL
    starter.CloseHandle.argtypes = [wintypes.HANDLE]
    starter.CloseHandle.restype = wintypes.BOOL
    start_name = f"Local\\RetroLume.Task083.{activity_id}.G{generation}.{run_tag}.Start"
    start_event = starter.CreateEventW(None, True, False, start_name)
    if not start_event:
        raise AssertionError("无法建立独立Start截止控制事件")
    proc = None
    try:
        proc = await asyncio.wait_for(asyncio.create_subprocess_exec(
            sys._base_executable, "-B", str(fixture), "controller", activity_id, str(generation), run_tag, start_name,
            cwd=str(backend), env=child_env, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        ), timeout=remaining())
        if not starter.SetEvent(start_event):
            raise AssertionError("无法放行已持句柄的场景04控制进程")
    except BaseException:
        if proc is not None and proc.returncode is None:
            proc.kill()
            await asyncio.wait_for(proc.wait(), timeout=remaining())
        raise
    finally:
        starter.CloseHandle(start_event)
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
                "active_processes_at_end": None,
                "worker_signaled_after_last_job_handle_closed": True,
                "tree_evidence": "single-process Job limit plus exact worker signaled; post-close Job query unavailable"}
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

class JobScenarioUnsafe(AssertionError):
    """A later Job batch must stop when identity or cleanup is unconfirmed."""


async def verify_scenario(mode: str, backend: Path) -> dict:
    """Future-only outer controller for 01/02/03/05; no call in offline tests."""
    if mode not in ("01", "02", "03", "05"):
        raise ValueError("unsupported controlled scenario")
    activity_id = str(uuid4())
    generation = 1
    run_tag = f"job-{mode}-" + uuid4().hex[:8]
    base = f"Local\\RetroLume.Task083.{activity_id}.G{generation}.{run_tag}"
    deadline_ns = time.monotonic_ns() + 25_000_000_000
    run_deadline_ns = deadline_ns - 5_000_000_000

    def remaining(*, cleanup=False, cap=5.0):
        limit = deadline_ns if cleanup else run_deadline_ns
        value = min(cap, (limit - time.monotonic_ns()) / 1e9)
        if value <= 0:
            raise TimeoutError("scenario deadline exhausted")
        return value

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateEventW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.BOOL, wintypes.LPCWSTR]
    kernel.CreateEventW.restype = wintypes.HANDLE
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.GetProcessTimes.argtypes = [wintypes.HANDLE, *([ctypes.POINTER(_FILETIME)] * 4)]
    kernel.GetProcessTimes.restype = wintypes.BOOL
    kernel.SetEvent.argtypes = [wintypes.HANDLE]
    kernel.SetEvent.restype = wintypes.BOOL
    kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel.WaitForSingleObject.restype = wintypes.DWORD
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    kernel.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
    kernel.TerminateProcess.restype = wintypes.BOOL

    events = []
    proc = None
    worker_handle = None
    job = None
    active_before = None
    active_end = None
    result = None
    failures = []
    primary = None
    try:
        for suffix in ("Start", "Arm"):
            name = f"{base}.{suffix}"
            ctypes.set_last_error(0)
            event = kernel.CreateEventW(None, True, False, name)
            if not event or ctypes.get_last_error() == 183:
                if event:
                    kernel.CloseHandle(event)
                raise JobScenarioUnsafe(f"event collision: {suffix}")
            events.append(event)
        child = Path(__file__).with_name("scenario_child.py")
        child_env = os.environ.copy()
        child_env["__PYVENV_LAUNCHER__"] = sys.executable
        proc = await asyncio.wait_for(asyncio.create_subprocess_exec(
            sys._base_executable, "-B", str(child), mode, activity_id,
            str(generation), run_tag, f"{base}.Start", f"{base}.Arm",
            cwd=str(backend), env=child_env,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        ), timeout=remaining())
        # The child cannot create a Job before this existing controller arms Start.
        if not kernel.SetEvent(events[0]):
            raise JobScenarioUnsafe("start event failed")
        line = await asyncio.wait_for(proc.stdout.readline(), timeout=remaining())
        if not line:
            raise JobScenarioUnsafe("no suspended identity")
        created = json.loads(line)
        expected = ("suspended", activity_id, generation, run_tag, job_name(activity_id, generation))
        actual = tuple(created.get(key) for key in ("phase", "activity_id", "generation", "run_tag", "job_name"))
        if actual != expected:
            raise JobScenarioUnsafe("activity/G/runTag/Job mismatch")
        worker_handle = kernel.OpenProcess(0x00101001, False, created["pid"])
        if not worker_handle:
            raise JobScenarioUnsafe("exact worker handle unavailable")
        times = [_FILETIME() for _ in range(4)]
        if not kernel.GetProcessTimes(worker_handle, *(ctypes.byref(x) for x in times)):
            raise JobScenarioUnsafe("worker creation time unavailable")
        stamp = (int(times[0].dwHighDateTime) << 32) | int(times[0].dwLowDateTime)
        if stamp != created.get("created_100ns"):
            raise JobScenarioUnsafe("worker PID creation time changed")
        job = NamedJob.open_existing(activity_id, generation)
        active_before = job.active_processes()
        if active_before != 1 or created.get("active_processes") != 1:
            raise JobScenarioUnsafe("suspended Job did not contain exactly one worker")
        # Exact Job and process objects, creation time and deadline precede Resume.
        if not kernel.SetEvent(events[1]):
            raise JobScenarioUnsafe("arm event failed")
        line = await asyncio.wait_for(proc.stdout.readline(), timeout=remaining(cap=20.0))
        if not line:
            raise JobScenarioUnsafe("no scenario result")
        result = json.loads(line)
        await asyncio.wait_for(proc.wait(), timeout=remaining())
        if proc.returncode != 0 or result.get("phase") != "result":
            raise JobScenarioUnsafe("scenario process failed")
        active_end = job.active_processes()
        if active_end != 0:
            raise JobScenarioUnsafe("exact Job tree not empty")
        if mode == "01":
            outcome = result["outcome"]
            if outcome["state"] != "settled" or outcome["active_processes_at_end"] != 0 or result["events"] != ["inspect", "claim", "close_db", "settle"]:
                raise JobScenarioUnsafe("normal settlement order incorrect")
        elif mode == "02":
            outcome = result["outcome"]
            if outcome["state"] != "stopped_at_deadline" or outcome["reserved_seconds"] != 6 or outcome["settled_seconds"] != 0 or "settle" in result["events"]:
                raise JobScenarioUnsafe("hung worker refund discipline incorrect")
        elif mode == "03" and not result.get("descendants_after_primary", 0) > 0:
            raise JobScenarioUnsafe("primary exit hid descendant")
        elif mode == "05" and not result.get("collision_rejected"):
            raise JobScenarioUnsafe("same-name collision not rejected")
    except BaseException as exc:
        primary = exc
    finally:
        if job is not None:
            try:
                if job.active_processes() != 0:
                    job.terminate()
                if not job.wait_empty_until(deadline_ns):
                    failures.append("exact_job_empty_unconfirmed")
            except BaseException as exc:
                failures.append(f"exact_job_cleanup:{type(exc).__name__}")
            try:
                job.close()
            except BaseException as exc:
                failures.append(f"job_close:{type(exc).__name__}")
        if worker_handle:
            try:
                if kernel.WaitForSingleObject(worker_handle, 0) != 0:
                    if not kernel.TerminateProcess(worker_handle, 1):
                        failures.append("worker_terminate_failed")
                    elif kernel.WaitForSingleObject(worker_handle, int(remaining(cleanup=True) * 1000)) != 0:
                        failures.append("worker_exit_unconfirmed")
            except BaseException as exc:
                failures.append(f"worker_cleanup:{type(exc).__name__}")
            if not kernel.CloseHandle(worker_handle):
                failures.append("worker_handle_close")
        if proc is not None and proc.returncode is None:
            try:
                proc.kill()
                await asyncio.wait_for(proc.wait(), timeout=remaining(cleanup=True))
            except BaseException as exc:
                failures.append(f"controller_cleanup:{type(exc).__name__}")
        for event in events:
            if not kernel.CloseHandle(event):
                failures.append("event_close")
    if primary is not None or failures:
        message = (f"scenario {mode} runTag={run_tag} activity={activity_id} G={generation} "
                   f"job={job_name(activity_id, generation)} active_before={active_before} "
                   f"active_end={active_end} cleanup_incomplete={bool(failures) or active_end != 0} "
                   f"failure={type(primary).__name__ if primary else 'none'} cleanup={','.join(failures)}")
        raise JobScenarioUnsafe(message) from primary
    return {**result, "run_tag": run_tag, "activity_id": activity_id,
            "generation": generation, "job_name": job_name(activity_id, generation),
            "active_processes_before_resume": active_before,
            "active_processes_at_end": active_end, "cleanup_incomplete": False}

