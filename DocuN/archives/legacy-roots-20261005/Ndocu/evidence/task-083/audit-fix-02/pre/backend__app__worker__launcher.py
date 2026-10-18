"""内部启动器：在专用 Windows 进程运行阻塞 SUP，并持整体管理截止。"""

from __future__ import annotations

import asyncio
import multiprocessing
import os
import time

from app.activities import PostgresAdmissionLedger
from app.runtime import psycopg_compatible_loop_factory

from .command import WorkerCommand
from .session import SessionConfig, SessionOutcome, SingleWindowSupervisor


def _supervisor_target(pipe, ledger, config, activity_id, executor_id, command, run_tag, deadline_ns):
    try:
        with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:
            outcome = runner.run(SingleWindowSupervisor(ledger, config).run_once(
                activity_id, executor_id, command,
                run_tag=run_tag, manager_deadline_ns=deadline_ns,
            ))
        pipe.send(outcome)  # 有界小对象；发送失败时父进程按未知失败关闭。
    finally:
        pipe.close()


def run_supervised_window(
    ledger: PostgresAdmissionLedger,
    config: SessionConfig,
    activity_id: str,
    executor_id: str,
    command: WorkerCommand,
    *,
    run_tag: str,
) -> SessionOutcome:
    """阻塞内部入口，不允许在应用事件循环调用；绝不返回业务执行资格。"""
    if os.name != "nt":
        raise RuntimeError("本内部监督切片仅在Windows可运行")
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        pass
    else:
        raise RuntimeError("启动器不能在应用事件循环运行")
    if type(ledger) is not PostgresAdmissionLedger or type(config) is not SessionConfig or type(command) is not WorkerCommand:
        raise TypeError("生产入口只接受固定账本、配置与不可执行命令数据")
    if not run_tag or len(run_tag) > 64 or not run_tag.isascii() or not run_tag.replace("-", "").replace("_", "").isalnum():
        raise ValueError("run_tag非法")

    started_ns = time.monotonic_ns()
    deadline_ns = started_ns + int(config.manager_total_seconds * 1e9)
    context = multiprocessing.get_context("spawn")
    receive, send = context.Pipe(duplex=False)
    process = context.Process(
        target=_supervisor_target,
        args=(send, ledger, config, activity_id, executor_id, command, run_tag, deadline_ns),
        name=f"RetroLumeSUP-{run_tag}",
    )
    started = False
    try:
        process.start()
        started = True
        send.close()
        remaining = max(0.0, (deadline_ns - time.monotonic_ns()) / 1e9)
        process.join(remaining)
        if process.is_alive():
            # 精确Process对象；不能凭名称/PID扫描。SUP句柄退出后Job由OS关闭，
            # 但父进程无法由此证明旧树已空，后续恢复必须失败关闭。
            process.terminate()
            process.join(config.cleanup_seconds)
            if process.is_alive():
                process.kill()
                process.join(config.cleanup_seconds)
            return SessionOutcome(
                run_tag, "manager_timeout_unconfirmed", activity_id,
                settled_seconds=None, reserved_seconds=None, pending_fold_seconds=None,
                cleanup_incomplete=process.is_alive(), error_type="ManagerDeadline",
            )
        if process.exitcode == 0 and receive.poll(0):
            outcome = receive.recv()
            if type(outcome) is SessionOutcome:
                return outcome
        return SessionOutcome(
            run_tag, "supervisor_lost_unconfirmed", activity_id,
            settled_seconds=None, reserved_seconds=None, pending_fold_seconds=None,
            error_type=f"SupervisorExit{process.exitcode}",
        )
    except BaseException as exc:
        if started and process.is_alive():
            process.terminate()
            process.join(config.cleanup_seconds)
            if process.is_alive():
                process.kill()
                process.join(config.cleanup_seconds)
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        return SessionOutcome(
            run_tag, "launcher_failed_unconfirmed", activity_id,
            settled_seconds=None, reserved_seconds=None, pending_fold_seconds=None,
            cleanup_incomplete=started and process.is_alive(), error_type=type(exc).__name__,
        )
    finally:
        receive.close()
        send.close()
        if started and not process.is_alive():
            process.close()
