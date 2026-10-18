"""TASK-083 synthetic Job fixture; offline repair prepares bounded control, never auto-runs."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import subprocess
import sys
import time


HERE = Path(__file__).resolve()
WAIT_OBJECT_0 = 0
ERROR_ALREADY_EXISTS = 183


def _controller(activity_id: str, generation: int, run_tag: str, start_name: str) -> int:
    sys.path.insert(0, str(HERE.parents[3]))
    from app.worker.windows_job import NamedJob, job_name

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateEventW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.BOOL, wintypes.LPCWSTR]
    kernel.CreateEventW.restype = wintypes.HANDLE
    kernel.OpenEventW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
    kernel.OpenEventW.restype = wintypes.HANDLE
    kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel.WaitForSingleObject.restype = wintypes.DWORD
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    base = f"Local\\RetroLume.Task083.{activity_id}.G{generation}.{run_tag}"
    start = kernel.OpenEventW(0x00100000, False, start_name)
    if not start:
        return 10
    try:
        if kernel.WaitForSingleObject(start, 5000) != WAIT_OBJECT_0:
            return 10
    finally:
        kernel.CloseHandle(start)
    events = []
    job = None
    try:
        for suffix in ("Arm", "Exit"):
            ctypes.set_last_error(0)
            handle = kernel.CreateEventW(None, True, False, f"{base}.{suffix}")
            if not handle or ctypes.get_last_error() == ERROR_ALREADY_EXISTS:
                if handle:
                    kernel.CloseHandle(handle)
                raise RuntimeError(f"event collision/error: {suffix}")
            events.append(handle)
        job = NamedJob.create(activity_id, generation, max_processes=1)
        worker = job.spawn_suspended([sys._base_executable, "-B", str(HERE), "hang"], cwd=str(HERE.parents[3]))
        print(json.dumps({
            "phase": "suspended", "run_tag": run_tag, "activity_id": activity_id,
            "generation": generation, "job_name": job_name(activity_id, generation),
            "pid": worker, "created_100ns": job.process_creation_time_100ns(),
            "active_processes": job.active_processes(),
        }), flush=True)
        if kernel.WaitForSingleObject(events[0], 5000) != WAIT_OBJECT_0:
            return 11
        job.resume()
        print(json.dumps({"phase": "resumed", "run_tag": run_tag, "pid": worker}), flush=True)
        if kernel.WaitForSingleObject(events[1], 5000) != WAIT_OBJECT_0:
            return 12
        # OS 关闭该 SUP 的最后 Job 句柄；父测试此时已关闭自己的 Job 句柄。
        os._exit(0)
    finally:
        if job is not None:
            try:
                job.terminate()
            finally:
                job.close()
        for handle in events:
            kernel.CloseHandle(handle)


def main() -> int:
    mode = sys.argv[1]
    if mode == "fast":
        time.sleep(0.15)
        return 0
    if mode == "controlled_fast":
        import asyncio
        sys.path.insert(0, str(HERE.parents[3]))
        from app.worker.worker_main import run_controlled_worker

        class SyntheticGateway:
            async def call(self, context, request):
                await asyncio.sleep(0.05)
                return "synthetic-received"

        async def work(gate):
            assert await gate.call(None, None) == "synthetic-received"

        asyncio.run(run_controlled_worker(SyntheticGateway(), work, drain_timeout_seconds=1.0))
        return 0
    if mode in ("hang", "child"):
        time.sleep(20 if mode == "hang" else 1.5)
        return 0
    if mode == "parent":
        subprocess.Popen([sys._base_executable, "-B", str(HERE), "child"], close_fds=True)
        return 0
    if mode == "controller":
        return _controller(sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5])
    raise ValueError(f"unknown fixture mode: {mode}")


if __name__ == "__main__":
    raise SystemExit(main())
