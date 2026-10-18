"""Internal Windows SUP launcher with one monotonic management deadline.

The CPython Process.start and Connection.recv calls do not expose a cancellable
operation handle. This module fails closed on every unconfirmed exit; D1's
pre-return start/partial-creation bound remains a run gate.
"""

from __future__ import annotations

import asyncio
from dataclasses import replace
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
        pipe.send(outcome)
    finally:
        pipe.close()


def _remaining(deadline_ns: int) -> float:
    return max(0.0, (deadline_ns - time.monotonic_ns()) / 1e9)


def _alive(process) -> bool | None:
    try:
        return process.is_alive()
    except BaseException:
        return None


def run_supervised_window(
    ledger: PostgresAdmissionLedger,
    config: SessionConfig,
    activity_id: str,
    executor_id: str,
    command: WorkerCommand,
    *,
    run_tag: str,
) -> SessionOutcome:
    """Blocking internal entry; its result never grants new work."""
    if os.name != "nt":
        raise RuntimeError("Windows only")
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        pass
    else:
        raise RuntimeError("launcher cannot run in application event loop")
    if type(ledger) is not PostgresAdmissionLedger or type(config) is not SessionConfig or type(command) is not WorkerCommand:
        raise TypeError("fixed ledger, config and command required")
    if not run_tag or len(run_tag) > 64 or not run_tag.isascii() or not run_tag.replace("-", "").replace("_", "").isalnum():
        raise ValueError("invalid run_tag")

    deadline_ns = time.monotonic_ns() + int(config.manager_total_seconds * 1e9)
    run_deadline_ns = deadline_ns - int(config.cleanup_seconds * 1e9)
    context = multiprocessing.get_context("spawn")
    receive = send = process = None
    launched = False
    outcome = None
    failure = None
    status = "launcher_failed_unconfirmed"
    errors: list[str] = []
    try:
        receive, send = context.Pipe(duplex=False)
        process = context.Process(
            target=_supervisor_target,
            args=(send, ledger, config, activity_id, executor_id, command, run_tag, deadline_ns),
            name=f"RetroLumeSUP-{run_tag}",
        )
        if _remaining(run_deadline_ns) == 0:
            status = "manager_timeout_unconfirmed"
        else:
            process.start()
            launched = True
            send.close()
            send = None
            process.join(_remaining(run_deadline_ns))
            if _alive(process) is True:
                status = "manager_timeout_unconfirmed"
            elif _alive(process) is False and process.exitcode == 0 and receive.poll(0):
                received = receive.recv()
                if type(received) is SessionOutcome:
                    outcome = received
                else:
                    status = "supervisor_lost_unconfirmed"
            else:
                status = "supervisor_lost_unconfirmed"
    except BaseException as exc:
        failure = exc
        errors.append(f"launcher:{type(exc).__name__}")
    finally:
        if process is not None:
            # A start exception may occur after OS creation. Probe the exact
            # Process object; no PID/name scan or optimistic cleanup claim.
            alive = _alive(process)
            if alive is not False and (launched or getattr(process, "pid", None) is not None):
                try:
                    process.terminate()
                except BaseException as exc:
                    errors.append(f"terminate:{type(exc).__name__}")
                try:
                    process.join(_remaining(deadline_ns))
                except BaseException as exc:
                    errors.append(f"terminate_join:{type(exc).__name__}")
                if _alive(process) is not False:
                    try:
                        process.kill()
                    except BaseException as exc:
                        errors.append(f"kill:{type(exc).__name__}")
                    try:
                        process.join(_remaining(deadline_ns))
                    except BaseException as exc:
                        errors.append(f"kill_join:{type(exc).__name__}")
            if _alive(process) is False:
                try:
                    process.close()
                except BaseException as exc:
                    errors.append(f"process_close:{type(exc).__name__}")
            elif launched or getattr(process, "pid", None) is not None:
                errors.append("supervisor_exit_unknown")
        for label, pipe in (("receive", receive), ("send", send)):
            if pipe is not None:
                try:
                    pipe.close()
                except BaseException as exc:
                    errors.append(f"{label}_close:{type(exc).__name__}")

    if isinstance(failure, (KeyboardInterrupt, SystemExit)):
        failure.add_note("launcher cleanup: " + ",".join(errors))
        raise failure
    if outcome is not None:
        if errors:
            return replace(outcome, state="settled_cleanup_error" if outcome.state == "settled" else outcome.state, cleanup_incomplete=True, cleanup_errors=outcome.cleanup_errors + tuple(errors))
        return outcome
    return SessionOutcome(
        run_tag, status, activity_id,
        settled_seconds=None, reserved_seconds=None, pending_fold_seconds=None,
        cleanup_incomplete=True,
        error_type=type(failure).__name__ if failure is not None else status,
        cleanup_errors=tuple(errors),
    )

