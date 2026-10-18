"""先持久预扣、再启动唯一Job的内部Windows单窗监督器。

必须运行在专用SUP线程/进程，不接FastAPI事件循环；Win32轮询为有界阻塞。
本卡只接受显式注入的内部worker命令，不连接产品任务或外部供应商。
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import math
import os
import threading
import time
from typing import Callable, Protocol

from app.activities import ActivityLease, CloseResult, SettleResult, WindowSnapshot

from .windows_job import ActivityMutex, JobUnknown, NamedJob, job_name


_LOCAL_LOCKS_GUARD = threading.Lock()
_LOCAL_LOCKS: dict[str, threading.Lock] = {}


def _local_lock(activity_id: str) -> threading.Lock:
    with _LOCAL_LOCKS_GUARD:
        return _LOCAL_LOCKS.setdefault(activity_id, threading.Lock())


class WindowLedger(Protocol):
    async def inspect_window(self, activity_id: str) -> WindowSnapshot: ...
    async def claim_lease(self, activity_id: str, executor_id: str, *, lease_seconds: int, window_seconds: int) -> ActivityLease | None: ...
    async def begin_window_close(self, activity_id: str, executor_id: str, execution_generation: int) -> CloseResult: ...
    async def settle_execution_window(self, activity_id: str, executor_id: str, execution_generation: int, *, window_seconds: int, elapsed_seconds: float) -> SettleResult: ...


@dataclass(frozen=True)
class SessionConfig:
    window_seconds: int = 90
    request_timeout_seconds: float = 10.0
    stop_grace_seconds: float = 5.0
    startup_limit_seconds: float = 5.0
    manager_db_timeout_seconds: float = 5.0
    cleanup_seconds: float = 5.0
    mutex_wait_seconds: float = 3.0

    def __post_init__(self) -> None:
        if isinstance(self.window_seconds, bool) or not isinstance(self.window_seconds, int) or not 1 <= self.window_seconds <= 3600:
            raise ValueError("单窗秒数须在1到3600之间")
        values = (
            self.request_timeout_seconds, self.stop_grace_seconds,
            self.startup_limit_seconds, self.manager_db_timeout_seconds,
            self.cleanup_seconds, self.mutex_wait_seconds,
        )
        if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) or x <= 0 for x in values):
            raise ValueError("监督期限必须是有限正数")
        if self.window_seconds <= self.startup_limit_seconds + self.request_timeout_seconds + self.stop_grace_seconds:
            raise ValueError("W必须大于启动上限+请求超时+停止预留")


@dataclass(frozen=True)
class SessionOutcome:
    run_tag: str
    state: str
    activity_id: str
    generation: int | None = None
    job_name: str | None = None
    pid: int | None = None
    active_processes_at_end: int | None = None
    charged_seconds: int | None = None
    elapsed_seconds: float | None = None
    cleanup_incomplete: bool = False
    error_type: str | None = None


class SingleWindowSupervisor:
    """同一进程充当启动器和Job外SUP，活动互斥锁持有到整窗结束。

    SUP死亡时其Job最后句柄由OS关闭；若恢复无法取得旧Job的整树正证据，
    对running残留拒绝新claim。没有后台心跳或自动重启预算。
    """

    def __init__(self, ledger: WindowLedger, config: SessionConfig):
        self.ledger = ledger
        self.config = config

    async def _db(self, awaitable):
        return await asyncio.wait_for(awaitable, timeout=self.config.manager_db_timeout_seconds)

    async def run_once(
        self,
        activity_id: str,
        executor_id: str,
        command_for_lease: Callable[[ActivityLease], list[str]],
        *,
        cwd: str,
        run_tag: str,
    ) -> SessionOutcome:
        if not run_tag or len(run_tag) > 64 or not run_tag.isascii() or not run_tag.replace("-", "").replace("_", "").isalnum():
            raise ValueError("run_tag须是受限非空ASCII标识")
        if not os.path.isdir(cwd):
            raise ValueError("worker工作目录不存在")
        config = self.config
        lease: ActivityLease | None = None
        job: NamedJob | None = None
        t0_ns: int | None = None
        pid: int | None = None
        tree_empty = False
        cleanup_incomplete = False
        state = "not_started"
        error_type: str | None = None
        charged: int | None = None
        elapsed: float | None = None
        owner: ActivityMutex | None = None
        local_owner = _local_lock(activity_id)
        if not local_owner.acquire(blocking=False):
            return SessionOutcome(run_tag, "local_owner_busy", activity_id)
        try:
            owner = ActivityMutex(activity_id, wait_seconds=config.mutex_wait_seconds)
            snapshot = await self._db(self.ledger.inspect_window(activity_id))
            if snapshot.status == "cancelled":
                return SessionOutcome(run_tag, "cancelled", activity_id)
            if snapshot.status == "running":
                # 不把Open失败、主进程退出或KILL_ON_JOB_CLOSE推断为整树退出。
                with NamedJob.open_existing(activity_id, snapshot.execution_generation) as old:
                    old.terminate()
                    if not old.wait_empty_until(time.monotonic_ns() + int(config.cleanup_seconds * 1e9)):
                        raise JobUnknown("旧Job整树未确认退出")
                # 旧租约仍可能有效；claim自己的冲突合同决定是否可接续。
            elif snapshot.status != "pending":
                raise JobUnknown("未知活动状态")

            t0_ns = time.monotonic_ns()  # 必须在claim事务之前；失败/响应丢失绝不spawn。
            lease = await self._db(self.ledger.claim_lease(
                activity_id, executor_id,
                lease_seconds=config.window_seconds,
                window_seconds=config.window_seconds,
            ))
            if lease is None:
                return SessionOutcome(run_tag, "budget_exhausted", activity_id)
            window = lease.window_seconds
            deadline_ns = t0_ns + window * 1_000_000_000
            stop_ns = deadline_ns - int(config.stop_grace_seconds * 1e9)
            if window <= config.startup_limit_seconds + config.request_timeout_seconds + config.stop_grace_seconds:
                state = "partial_window_too_small"
                return SessionOutcome(run_tag, state, activity_id, lease.execution_generation)
            if time.monotonic_ns() >= t0_ns + int(config.startup_limit_seconds * 1e9):
                state = "startup_deadline"
                return SessionOutcome(run_tag, state, activity_id, lease.execution_generation)

            # 截止在Resume之前已固定；单进程SUP始终持确切Job句柄与互斥锁。
            job = NamedJob.create(activity_id, lease.execution_generation)
            command = command_for_lease(lease)
            pid = job.spawn_suspended(command, cwd=cwd)
            if time.monotonic_ns() >= t0_ns + int(config.startup_limit_seconds * 1e9):
                state = "startup_deadline"
                return SessionOutcome(run_tag, state, activity_id, lease.execution_generation, job.name, pid)
            job.resume()
            state = "running"

            tree_empty = job.wait_empty_until(stop_ns)
            if not tree_empty:
                # 窗口剩余g专用于精确终止与整树确认；该路径不部分退款。
                job.terminate()
                tree_empty = job.wait_empty_until(deadline_ns)
                state = "stopped_at_deadline" if tree_empty else "overrun_unconfirmed"
                return SessionOutcome(
                    run_tag, state, activity_id, lease.execution_generation,
                    job.name, pid, 0 if tree_empty else None, window,
                    (time.monotonic_ns() - t0_ns) / 1e9,
                    not tree_empty,
                )

            t1_ns = time.monotonic_ns()
            elapsed = (t1_ns - t0_ns) / 1e9
            charged = (t1_ns - t0_ns + 999_999_999) // 1_000_000_000
            if job.primary_exit_code() != 0:
                state = "worker_failed_full_charge"
            elif not 1 <= charged <= window:
                state = "elapsed_violation_full_charge"
            else:
                # Job已空，后续DB门/结算在Job外可信SUP中完成。
                await self._db(self.ledger.begin_window_close(activity_id, executor_id, lease.execution_generation))
                try:
                    settled = await self._db(self.ledger.settle_execution_window(
                        activity_id, executor_id, lease.execution_generation,
                        window_seconds=window, elapsed_seconds=elapsed,
                    ))
                except Exception:
                    # 仅按完全相同的G/W/C重试一次；持久受限幂等可判提交响应丢失。
                    settled = await self._db(self.ledger.settle_execution_window(
                        activity_id, executor_id, lease.execution_generation,
                        window_seconds=window, elapsed_seconds=elapsed,
                    ))
                state = "settled" if settled in (SettleResult.SETTLED, SettleResult.ALREADY_SETTLED) else "settle_unknown"
            return SessionOutcome(
                run_tag, state, activity_id, lease.execution_generation,
                job.name, pid, 0, charged if state == "settled" else window,
                elapsed,
            )
        except BaseException as exc:
            error_type = type(exc).__name__
            if isinstance(exc, asyncio.CancelledError):
                raise
            state = "failed_closed"
        finally:
            if job is not None:
                try:
                    if not tree_empty:
                        job.terminate()
                        tree_empty = job.wait_empty_until(time.monotonic_ns() + int(config.cleanup_seconds * 1e9))
                    if not tree_empty:
                        cleanup_incomplete = True
                except BaseException:
                    cleanup_incomplete = True
                finally:
                    job.close()
            if owner is not None:
                owner.close()
            local_owner.release()
        return SessionOutcome(
            run_tag, state, activity_id,
            lease.execution_generation if lease else None,
            job_name(activity_id, lease.execution_generation) if lease and job else None,
            pid, 0 if tree_empty else None,
            charged if state == "settled" else (lease.window_seconds if lease else None),
            elapsed, cleanup_incomplete, error_type,
        )
