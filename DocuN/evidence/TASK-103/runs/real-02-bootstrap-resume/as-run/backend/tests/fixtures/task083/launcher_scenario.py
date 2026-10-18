"""TASK-083 09轮 P子进程：父进程边界（Resume前/后退出）的真实调用入口。

仅测试夹具；不供产品引用。P 进程内只做两件事：
1. 在 launcher 真实函数调用边界（_SuspendedSupervisor.resume / wait 与
   NamedMapping.create）安装测试侧同步屏障——不复制生产实现，不削弱任何校验；
2. 以真实 PostgresAdmissionLedger + 固定 WorkerCommand 调用 run_supervised_window。

屏障证据经 JSONL 文件交外层控制者；P 自身被控制者按精确句柄终止，退出码不承
担验证语义。DSN 只经环境变量进入本进程并立即从 os.environ 移除，使 SUP/worker
子进程环境不含口令（launcher 的环境块复制父环境）。
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import asdict
import json
import os
from pathlib import Path
import sys

BACKEND = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(BACKEND))

import app.worker.launcher as launcher_module
from app.activities import PostgresAdmissionLedger
from app.worker.command import WorkerCommand
from app.worker.session import SessionConfig
from app.worker.supervisor_ipc import NamedMapping

EVENT_MODIFY_STATE = 0x0002
SYNCHRONIZE = 0x00100000
WAIT_OBJECT_0 = 0
GO_TIMEOUT_S = 120.0  # 正常流程中控制者在此之前精确终止本进程；超时是兜底非依赖。

CONFIG = SessionConfig(
    window_seconds=6, request_timeout_seconds=0.5, stop_grace_seconds=1.0,
    startup_limit_seconds=2.0, manager_db_timeout_seconds=1.5,
    cleanup_seconds=2.0, mutex_wait_seconds=1.0, manager_overhead_seconds=10.0,
)


def _event_kernel():
    api = ctypes.WinDLL("kernel32", use_last_error=True)
    api.OpenEventW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
    api.OpenEventW.restype = wintypes.HANDLE
    api.SetEvent.argtypes = [wintypes.HANDLE]
    api.SetEvent.restype = wintypes.BOOL
    api.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    api.WaitForSingleObject.restype = wintypes.DWORD
    api.CloseHandle.argtypes = [wintypes.HANDLE]
    api.CloseHandle.restype = wintypes.BOOL
    return api


class _Barrier:
    """P→控制者单向信号；控制者的放行事件本流程永不置位（P 由控制者终止）。"""

    def __init__(self, barrier_name: str, go_name: str):
        api = _event_kernel()
        self.api = api
        self.barrier = api.OpenEventW(EVENT_MODIFY_STATE, False, barrier_name)
        self.go = api.OpenEventW(EVENT_MODIFY_STATE | SYNCHRONIZE, False, go_name)
        if not self.barrier or not self.go:
            raise RuntimeError("barrier/go event absent; P must not proceed")

    def signal(self, record: dict, evidence_file: Path) -> None:
        with open(evidence_file, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            fh.flush()
        if not self.api.SetEvent(self.barrier):
            raise RuntimeError("SetEvent(barrier) failed")

    def wait_go_forever(self) -> bool:
        return self.api.WaitForSingleObject(self.go, int(GO_TIMEOUT_S * 1000)) == WAIT_OBJECT_0

    def close(self) -> None:
        for handle in (self.barrier, self.go):
            if handle:
                self.api.CloseHandle(handle)


def main() -> int:
    if len(sys.argv) != 8:
        return 2
    mode, activity_id, run_tag, barrier_name, go_name, evidence_file, schema = sys.argv[1:]
    if mode not in ("c1", "c2"):
        return 2
    dsn = os.environ.pop("RETROLUME_TASK_083_D1_DATABASE_URL", "")
    if not dsn:
        return 2
    from psycopg.conninfo import make_conninfo

    scoped = make_conninfo(dsn, options=f"-c search_path={schema}")
    barrier = _Barrier(barrier_name, go_name)
    mapping_name_seen: list[str] = []

    real_create = launcher_module.NamedMapping.create

    def observed_create(name: str) -> NamedMapping:
        mapping_name_seen.append(name)  # 记录创建顺序中的首个SUP映射名。
        return real_create(name)

    real_resume = launcher_module._SuspendedSupervisor.resume

    def pre_resume_record(self) -> dict:
        return {
            "phase": "pre_resume", "mode": mode,
            "activity_id": activity_id, "run_tag": run_tag,
            "python_pid": os.getpid(),
            "supervisor_pid": self.pid,
            "supervisor_created_100ns": self.creation_time_100ns(),
            "mapping_name": mapping_name_seen[0] if mapping_name_seen else None,
        }

    real_wait = launcher_module._SuspendedSupervisor.wait
    wait_signalled = False

    if mode == "c1":
        # Resume前边界：记录SUP精确身份后挂起等待放行；绝不调用真实resume。
        def held_resume(self) -> None:
            barrier.signal(pre_resume_record(self), Path(evidence_file))
            barrier.wait_go_forever()
            raise RuntimeError("c1 barrier released unexpectedly; no resume permitted")

        launcher_module._SuspendedSupervisor.resume = held_resume
    else:
        def recorded_resume(self) -> None:
            barrier.signal(pre_resume_record(self), Path(evidence_file))
            real_resume(self)  # SUP从此独立运行，父死亡不影响其生命周期。

        def barriered_wait(self, seconds):
            # 只在主等待（seconds>0）首次进入时设障；wait(0)为terminate内部探测，直接放行。
            nonlocal wait_signalled
            if seconds <= 0 or wait_signalled:
                return real_wait(self, seconds)
            wait_signalled = True
            barrier.signal({"phase": "at_wait", "mode": mode, "python_pid": os.getpid(),
                            "run_tag": run_tag}, Path(evidence_file))
            barrier.wait_go_forever()
            return real_wait(self, seconds)

        launcher_module._SuspendedSupervisor.resume = recorded_resume
        launcher_module._SuspendedSupervisor.wait = barriered_wait

    launcher_module.NamedMapping.create = observed_create
    outcome = None
    error = None
    try:
        outcome = launcher_module.run_supervised_window(
            PostgresAdmissionLedger(scoped), CONFIG, activity_id, f"worker-{run_tag}",
            WorkerCommand(), run_tag=run_tag,
        )
    except BaseException as exc:  # 不打印异常详情；SUP失败时父端如实报未知。
        error = type(exc).__name__
    finally:
        launcher_module._SuspendedSupervisor.resume = real_resume
        launcher_module._SuspendedSupervisor.wait = real_wait
        launcher_module.NamedMapping.create = real_create
        barrier.close()
        record = {"phase": "outcome", "mode": mode, "run_tag": run_tag}
        if outcome is not None:
            record["outcome"] = asdict(outcome)
        if error is not None:
            record["error_type"] = error
        with open(evidence_file, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
