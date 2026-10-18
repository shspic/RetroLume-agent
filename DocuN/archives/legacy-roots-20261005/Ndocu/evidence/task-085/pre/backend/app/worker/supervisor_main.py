"""Fixed SUP child module. Only a bounded named mapping carries runtime data."""

from __future__ import annotations

import asyncio
from dataclasses import asdict, fields
import re
import sys
import time
from uuid import UUID

from app.activities import PostgresAdmissionLedger
from app.runtime import psycopg_compatible_loop_factory

from .command import WorkerCommand
from .session import SessionConfig, SingleWindowSupervisor
from .supervisor_ipc import NamedMapping


_RUN_TAG = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")


def _validated_request(value: dict, mapping_name: str):
    if type(value) is not dict or value.get("protocol") != 1 or value.get("mapping_name") != mapping_name:
        raise ValueError("SUP request identity mismatch")
    activity_id = value.get("activity_id")
    executor_id = value.get("executor_id")
    run_tag = value.get("run_tag")
    if type(activity_id) is not str or str(UUID(activity_id)) != activity_id:
        raise ValueError("activity UUID invalid")
    if type(executor_id) is not str or not 1 <= len(executor_id) <= 128:
        raise ValueError("executor invalid")
    if type(run_tag) is not str or _RUN_TAG.fullmatch(run_tag) is None:
        raise ValueError("runTag invalid")
    deadline_ns = value.get("deadline_ns")
    if type(deadline_ns) is not int or deadline_ns <= time.monotonic_ns():
        raise ValueError("management deadline expired")
    ledger_data = value.get("ledger")
    if type(ledger_data) is not dict or set(ledger_data) != {
        "dsn", "connect_timeout_seconds", "statement_timeout_ms", "lock_timeout_ms",
    }:
        raise ValueError("ledger data invalid")
    dsn = ledger_data["dsn"]
    if type(dsn) is not str or not 1 <= len(dsn.encode("utf-8")) <= 4096:
        raise ValueError("ledger connection data invalid")
    config_data = value.get("config")
    if type(config_data) is not dict or set(config_data) != {f.name for f in fields(SessionConfig)}:
        raise ValueError("config data invalid")
    command_data = value.get("command")
    if type(command_data) is not dict or set(command_data) != {"task"}:
        raise ValueError("command data invalid")
    ledger = PostgresAdmissionLedger(**ledger_data)
    config = SessionConfig(**config_data)
    command = WorkerCommand(**command_data)
    return ledger, config, activity_id, executor_id, command, run_tag, deadline_ns


def main() -> int:
    if len(sys.argv) != 2:
        return 2
    mapping = None
    try:
        mapping = NamedMapping.open_existing(sys.argv[1])
        ledger, config, activity_id, executor_id, command, run_tag, deadline_ns = _validated_request(
            mapping.read_request(), sys.argv[1],
        )
        with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:
            outcome = runner.run(SingleWindowSupervisor(ledger, config).run_once(
                activity_id, executor_id, command, run_tag=run_tag,
                manager_deadline_ns=deadline_ns,
            ))
        mapping.write_result({"protocol": 1, "run_tag": run_tag, "activity_id": activity_id,
                              "outcome": asdict(outcome)})
        return 0
    except BaseException:
        # No traceback containing a DSN; the parent reports unknown and stops work.
        return 1
    finally:
        if mapping is not None:
            try:
                mapping.close()
            except BaseException:
                return 1


if __name__ == "__main__":
    raise SystemExit(main())

