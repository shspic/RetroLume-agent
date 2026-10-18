"""Future controlled Job scenarios 01/02/03/05. Never import from product code."""

from __future__ import annotations

import asyncio
from dataclasses import asdict
import ctypes
from ctypes import wintypes
import json
from pathlib import Path
import sys
import time
from unittest.mock import patch

BACKEND = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(BACKEND / "tests"))

from app.worker.command import WorkerCommand
from app.worker.session import SessionConfig, SingleWindowSupervisor
from app.worker.windows_job import JobUnknown, NamedJob
from test_worker_session import FakeLedger


def _wait_event(name: str) -> None:
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenEventW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
    kernel.OpenEventW.restype = wintypes.HANDLE
    kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel.WaitForSingleObject.restype = wintypes.DWORD
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    handle = kernel.OpenEventW(0x00100000, False, name)
    if not handle:
        raise RuntimeError("controller event absent; no Job may be created")
    try:
        if kernel.WaitForSingleObject(handle, 5000) != 0:
            raise TimeoutError("controller event not armed")
    finally:
        kernel.CloseHandle(handle)


def _identity(job: NamedJob, activity_id: str, generation: int, run_tag: str) -> None:
    print(json.dumps({
        "phase": "suspended", "activity_id": activity_id, "generation": generation,
        "run_tag": run_tag, "job_name": job.name, "pid": job.pid,
        "created_100ns": job.process_creation_time_100ns(),
        "active_processes": job.active_processes(),
    }), flush=True)


def _run_supervised(mode: str, activity_id: str, generation: int, run_tag: str, arm_name: str) -> dict:
    ledger = FakeLedger()
    config = SessionConfig(window_seconds=6, request_timeout_seconds=0.5,
                           stop_grace_seconds=1, startup_limit_seconds=2,
                           cleanup_seconds=2)
    original_resume = NamedJob.resume

    def held_resume(job: NamedJob) -> None:
        _identity(job, activity_id, generation, run_tag)
        _wait_event(arm_name)
        original_resume(job)

    command = WorkerCommand()
    with patch.object(NamedJob, "resume", held_resume):
        if mode == "02":
            fixture = Path(__file__).with_name("fixture.py")
            with patch.object(WorkerCommand, "argv", lambda self: [sys._base_executable, "-B", str(fixture), "hang"]):
                outcome = asyncio.run(SingleWindowSupervisor(ledger, config).run_once(
                    activity_id, "worker-1", command, run_tag=run_tag,
                    manager_deadline_ns=time.monotonic_ns() + 20_000_000_000,
                ))
        else:
            outcome = asyncio.run(SingleWindowSupervisor(ledger, config).run_once(
                activity_id, "worker-1", command, run_tag=run_tag,
                manager_deadline_ns=time.monotonic_ns() + 20_000_000_000,
            ))
    return {"phase": "result", "outcome": asdict(outcome), "events": ledger.events}


def _run_direct(mode: str, activity_id: str, generation: int, run_tag: str, arm_name: str) -> dict:
    fixture = Path(__file__).with_name("fixture.py")
    worker_mode = "parent" if mode == "03" else "fast"
    with NamedJob.create(activity_id, generation) as job:
        job.spawn_suspended([sys._base_executable, "-B", str(fixture), worker_mode], cwd=str(BACKEND))
        _identity(job, activity_id, generation, run_tag)
        _wait_event(arm_name)
        collision = False
        if mode == "05":
            try:
                NamedJob.create(activity_id, generation)
            except JobUnknown:
                collision = True
            if not collision:
                raise AssertionError("same-name Job collision was accepted")
        job.resume()
        descendants_after_primary = None
        if mode == "03":
            if job.api.WaitForSingleObject(job.process.hProcess, 4000) != 0:
                raise TimeoutError("primary did not exit")
            descendants_after_primary = job.active_processes()
            if descendants_after_primary <= 0:
                raise AssertionError("primary exit hid descendant")
        if not job.wait_empty_until(time.monotonic_ns() + 5_000_000_000):
            raise TimeoutError("exact Job did not empty")
        return {"phase": "result", "active_processes_at_end": job.active_processes(),
                "descendants_after_primary": descendants_after_primary, "collision_rejected": collision}


def main() -> int:
    if len(sys.argv) != 7:
        return 2
    mode, activity_id, generation_s, run_tag, start_name, arm_name = sys.argv[1:]
    if mode not in ("01", "02", "03", "05"):
        return 2
    generation = int(generation_s)
    _wait_event(start_name)  # Late process creation cannot create a Job.
    result = (_run_supervised if mode in ("01", "02") else _run_direct)(
        mode, activity_id, generation, run_tag, arm_name,
    )
    print(json.dumps(result), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

