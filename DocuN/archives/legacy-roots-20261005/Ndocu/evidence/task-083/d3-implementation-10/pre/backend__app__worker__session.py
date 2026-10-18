"""Windows 内部单窗 SUP。阻塞 Job 操作仅由 launcher 的专用子进程调用。"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import math
import threading
import time
from typing import Protocol

from app.activities import ActivityLease, CloseResult, SettleResult, WindowSnapshot

from .command import WorkerCommand
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
    manager_overhead_seconds: float = 30.0

    def __post_init__(self) -> None:
        if type(self.window_seconds) is not int or not 1 <= self.window_seconds <= 3600:
            raise ValueError("单窗秒数须在1到3600之间")
        values = (
            self.request_timeout_seconds, self.stop_grace_seconds,
            self.startup_limit_seconds, self.manager_db_timeout_seconds,
            self.cleanup_seconds, self.mutex_wait_seconds, self.manager_overhead_seconds,
        )
        if any(type(x) not in (int, float) or not math.isfinite(x) or x <= 0 for x in values):
            raise ValueError("监督期限必须是有限正数")
        if self.window_seconds <= self.startup_limit_seconds + self.request_timeout_seconds + self.stop_grace_seconds:
            raise ValueError("W必须大于启动上限+请求超时+停止预留")
        if self.manager_overhead_seconds <= self.mutex_wait_seconds + 3 * self.manager_db_timeout_seconds + self.cleanup_seconds:
            raise ValueError("管理总余量不足以覆盖互斥、DB与清理等待")

    @property
    def manager_total_seconds(self) -> float:
        return self.window_seconds + self.manager_overhead_seconds


@dataclass(frozen=True)
class SessionOutcome:
    run_tag: str
    state: str
    activity_id: str
    generation: int | None = None
    job_name: str | None = None
    pid: int | None = None
    active_processes_at_end: int | None = None
    settled_seconds: int | None = None  # 已确认写入 S；未知时为 None。
    reserved_seconds: int | None = None  # 已确认仍占 R；结算响应未知时为 None。
    pending_fold_seconds: int | None = None  # 以后按原规则保守折叠，未计入 S。
    elapsed_seconds: float | None = None
    cleanup_incomplete: bool = False
    error_type: str | None = None
    cleanup_errors: tuple[str, ...] = ()
    timing_diagnostic: tuple[int, int, int, int, int] | None = None
    manager_pid: int | None = None
    manager_created_100ns: int | None = None


class _StopSession(Exception):
    """已记录预期终态，继续统一清理后才构造结果。"""


class ManagerDeadline(RuntimeError):
    pass


class SingleWindowSupervisor:
    """仅供 launcher 子进程执行；任何旧树不明都不认领新代次。"""

    def __init__(self, ledger: WindowLedger, config: SessionConfig):
        self.ledger = ledger
        self.config = config

    @staticmethod
    def _remaining(deadline_ns: int) -> float:
        remaining = (deadline_ns - time.monotonic_ns()) / 1_000_000_000
        if remaining <= 0:
            raise ManagerDeadline("SUP管理总期限已耗尽")
        return remaining

    async def _db(self, awaitable, deadline_ns: int):
        try:
            timeout = min(self.config.manager_db_timeout_seconds, self._remaining(deadline_ns))
        except BaseException:
            if hasattr(awaitable, "close"):
                awaitable.close()
            raise
        return await asyncio.wait_for(awaitable, timeout=timeout)

    async def run_once(
        self,
        activity_id: str,
        executor_id: str,
        command: WorkerCommand,
        *,
        run_tag: str,
        manager_deadline_ns: int,
    ) -> SessionOutcome:
        # 产品调用只经 launcher.run_supervised_window；此方法供子进程与纯替身测试。
        if type(command) is not WorkerCommand:
            raise TypeError("SUP只接受已校验的WorkerCommand纯数据")
        if not run_tag or len(run_tag) > 64 or not run_tag.isascii() or not run_tag.replace("-", "").replace("_", "").isalnum():
            raise ValueError("run_tag须是受限非空ASCII标识")
        identity_name = job_name(activity_id, 0)  # 在任何副作用前验证 UUID。
        del identity_name
        self._remaining(manager_deadline_ns)

        config = self.config
        lease: ActivityLease | None = None
        job: NamedJob | None = None
        owner: ActivityMutex | None = None
        pid: int | None = None
        name: str | None = None
        t0_ns: int | None = None
        tree_empty = False
        created_job = False
        state = "not_started"
        error_type: str | None = None
        cleanup_errors: list[str] = []
        settled_seconds: int | None = 0
        reserved_seconds: int | None = 0
        pending_fold_seconds: int | None = 0
        elapsed_seconds: float | None = None
        timing_diagnostic: tuple[int, int, int, int, int] | None = None
        settlement_attempted = False
        claim_attempted = False
        interrupted: BaseException | None = None

        local_owner = _local_lock(activity_id)
        if not local_owner.acquire(blocking=False):
            return SessionOutcome(run_tag, "local_owner_busy", activity_id)
        try:
            owner = ActivityMutex(activity_id, wait_seconds=min(config.mutex_wait_seconds, self._remaining(manager_deadline_ns)))
            snapshot = await self._db(self.ledger.inspect_window(activity_id), manager_deadline_ns)
            if snapshot.status == "cancelled":
                state = "cancelled"
                raise _StopSession
            if snapshot.status == "running":
                old = NamedJob.open_existing(activity_id, snapshot.execution_generation)
                old_failure: BaseException | None = None
                try:
                    old.terminate()
                    old_deadline = min(manager_deadline_ns, time.monotonic_ns() + int(config.cleanup_seconds * 1e9))
                    if not old.wait_empty_until(old_deadline):
                        raise JobUnknown("旧Job整树未确认退出")
                except BaseException as exc:
                    old_failure = exc
                try:
                    old.close()
                except BaseException as exc:
                    if old_failure is None:
                        old_failure = exc
                    else:
                        cleanup_errors.append(type(exc).__name__)
                if old_failure is not None:
                    raise old_failure
            elif snapshot.status != "pending":
                raise JobUnknown("未知活动状态")

            t0_ns = time.monotonic_ns()  # claim前固定；响应丢失不spawn或重领。
            claim_attempted = True
            lease = await self._db(self.ledger.claim_lease(
                activity_id, executor_id,
                lease_seconds=config.window_seconds,
                window_seconds=config.window_seconds,
            ), manager_deadline_ns)
            if lease is None:
                state = "budget_exhausted"
                raise _StopSession
            window = lease.window_seconds
            reserved_seconds = window
            pending_fold_seconds = window
            deadline_ns = t0_ns + window * 1_000_000_000
            stop_ns = min(
                deadline_ns - int(config.stop_grace_seconds * 1e9),
                manager_deadline_ns - int(config.cleanup_seconds * 1e9),
            )
            if window <= config.startup_limit_seconds + config.request_timeout_seconds + config.stop_grace_seconds:
                state = "partial_window_too_small"
                raise _StopSession
            if time.monotonic_ns() >= min(t0_ns + int(config.startup_limit_seconds * 1e9), stop_ns):
                state = "startup_deadline"
                raise _StopSession

            self._remaining(manager_deadline_ns)
            job = NamedJob.create(activity_id, lease.execution_generation)
            created_job = True
            name = job.name
            pid = job.spawn_suspended(command.argv(), cwd=command.cwd)
            if time.monotonic_ns() >= min(t0_ns + int(config.startup_limit_seconds * 1e9), stop_ns):
                state = "startup_deadline"
                raise _StopSession
            # 唯一 Job/悬停 worker 已登记且截止固定，才 armed/Resume。
            job.resume()
            state = "running"
            tree_empty = job.wait_empty_until(stop_ns)
            if not tree_empty:
                job.terminate()
                tree_empty = job.wait_empty_until(min(deadline_ns, manager_deadline_ns))
                state = "stopped_at_deadline" if tree_empty else "overrun_unconfirmed"
                elapsed_seconds = (time.monotonic_ns() - t0_ns) / 1e9
                raise _StopSession

            t1_ns = time.monotonic_ns()
            elapsed_seconds = (t1_ns - t0_ns) / 1e9
            observed = (t1_ns - t0_ns + 999_999_999) // 1_000_000_000
            timing_diagnostic = (t0_ns, t1_ns, t1_ns - t0_ns, observed, window)
            if job.primary_exit_code() != 0:
                state = "worker_failed_full_reservation"
                raise _StopSession
            if not 1 <= observed <= window:
                state = "elapsed_violation_full_reservation"
                raise _StopSession
            # 树已确认0且主进程成功；先关闭自身全部Job/进程句柄，避免
            # 后续清理失败发生在部分退款之后。活动互斥仍保持到结算结束。
            job.close()
            job = None
            await self._db(self.ledger.begin_window_close(activity_id, executor_id, lease.execution_generation), manager_deadline_ns)
            settlement_attempted = True
            try:
                settled = await self._db(self.ledger.settle_execution_window(
                    activity_id, executor_id, lease.execution_generation,
                    window_seconds=window, elapsed_seconds=elapsed_seconds,
                ), manager_deadline_ns)
            except Exception:
                # 首次提交响应可能丢失，仅相同 G/W/C 重试一次。
                settled = await self._db(self.ledger.settle_execution_window(
                    activity_id, executor_id, lease.execution_generation,
                    window_seconds=window, elapsed_seconds=elapsed_seconds,
                ), manager_deadline_ns)
            if settled not in (SettleResult.SETTLED, SettleResult.ALREADY_SETTLED):
                state = "settlement_unconfirmed"
                reserved_seconds = None
                pending_fold_seconds = None
                raise _StopSession
            state = "settled"
            settled_seconds = observed
            reserved_seconds = 0
            pending_fold_seconds = 0
        except _StopSession:
            pass
        except BaseException as exc:
            interrupted = exc if isinstance(exc, (asyncio.CancelledError, KeyboardInterrupt, SystemExit)) else None
            error_type = type(exc).__name__
            state = "cancelled_by_caller" if isinstance(exc, asyncio.CancelledError) else "failed_closed"
            if settlement_attempted or (claim_attempted and lease is None):
                settled_seconds = None
                reserved_seconds = None
                pending_fold_seconds = None
        finally:
            if job is not None:
                if not tree_empty:
                    try:
                        job.terminate()
                    except BaseException as exc:
                        cleanup_errors.append(f"terminate:{type(exc).__name__}")
                    try:
                        limit = min(manager_deadline_ns, time.monotonic_ns() + int(config.cleanup_seconds * 1e9))
                        tree_empty = job.wait_empty_until(limit)
                    except BaseException as exc:
                        cleanup_errors.append(f"query:{type(exc).__name__}")
                try:
                    job.close()
                except BaseException as exc:
                    cleanup_errors.append(f"job_close:{type(exc).__name__}")
            if owner is not None:
                try:
                    owner.close()
                except BaseException as exc:
                    cleanup_errors.append(f"owner_close:{type(exc).__name__}")
            try:
                local_owner.release()
            except BaseException as exc:
                cleanup_errors.append(f"local_owner_release:{type(exc).__name__}")

        incomplete = (created_job and not tree_empty) or bool(cleanup_errors)
        if incomplete and state == "settled":
            state = "settled_cleanup_error"  # 已确认结算不能伪装成未结算。
        elif incomplete and state not in ("settlement_unconfirmed", "cancelled_by_caller"):
            state = "failed_closed"
        result = SessionOutcome(
            run_tag, state, activity_id,
            lease.execution_generation if lease else None,
            name, pid, 0 if created_job and tree_empty else None,
            settled_seconds, reserved_seconds, pending_fold_seconds,
            elapsed_seconds, incomplete, error_type, tuple(cleanup_errors),
            timing_diagnostic,
        )
        if interrupted is not None:
            interrupted.session_outcome = result
            raise interrupted
        return result

