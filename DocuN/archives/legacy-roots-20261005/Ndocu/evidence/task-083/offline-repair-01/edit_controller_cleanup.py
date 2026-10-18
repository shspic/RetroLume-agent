"""Exact-anchor bounded synthetic controller cleanup repair; no scenario execution."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def replace_once(relative, old, new):
    path = ROOT / relative
    data = path.read_text(encoding="utf-8")
    assert data.count(old) == 1, (relative, data.count(old))
    path.write_text(data.replace(old, new), encoding="utf-8", newline="")


replace_once(
    "backend/tests/fixtures/task083/fixture.py",
    "            if not handle or ctypes.get_last_error() == ERROR_ALREADY_EXISTS:\n                raise RuntimeError(f\"event collision/error: {suffix}\")\n",
    "            if not handle or ctypes.get_last_error() == ERROR_ALREADY_EXISTS:\n                if handle:\n                    kernel.CloseHandle(handle)\n                raise RuntimeError(f\"event collision/error: {suffix}\")\n",
)
old = '''    finally:
        if parent_job is not None:
            parent_job.close()
        if proc.returncode is None:
            proc.kill()  # 精确控制者对象，不按名称或裸PID终止。
            await asyncio.wait_for(proc.wait(), timeout=max(0.1, remaining(4)))
        if worker_handle:
            if verified and kernel.WaitForSingleObject(worker_handle, 0) != 0:
                kernel.TerminateProcess(worker_handle, 1)
                if kernel.WaitForSingleObject(worker_handle, 4000) != 0:
                    raise AssertionError("cleanup_incomplete: 精确worker未退出")
            kernel.CloseHandle(worker_handle)
        for event in events:
            kernel.CloseHandle(event)
'''
new = '''    finally:
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
'''
replace_once("backend/tests/fixtures/task083/job_control.py", old, new)
