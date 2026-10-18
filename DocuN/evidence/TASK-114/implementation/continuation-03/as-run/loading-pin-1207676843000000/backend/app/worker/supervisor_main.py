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
from .one_call import OneCallInput, validate_identity
from app.capabilities.contracts import ToolExecutionInput


_RUN_TAG = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")

_OUTER2_REQUEST_FIELDS = {"protocol", "mapping_name", "activity_id", "executor_id",
                          "run_tag", "deadline_ns", "command", "config", "ledger", "one_call"}
_OUTER3_REQUEST_FIELDS = {"protocol", "mapping_name", "activity_id", "executor_id",
                          "run_tag", "deadline_ns", "command", "config", "ledger", "tool_action"}


def _validated_request(value: dict, mapping_name: str):
    if type(value) is not dict or value.get("mapping_name") != mapping_name:
        raise ValueError("SUP request identity mismatch")
    protocol = value.get("protocol")
    if type(protocol) is not int or protocol not in (2, 3):
        raise ValueError("SUP request identity mismatch")
    if set(value) != (_OUTER2_REQUEST_FIELDS if protocol == 2 else _OUTER3_REQUEST_FIELDS):
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
    if type(ledger_data) is not dict or set(ledger_data)-{'data_guard'} != {
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
    if protocol == 2 and command.task not in ("idle", "one_call"):
        raise ValueError("protocol/command mismatch")
    if protocol == 3 and command.task != "one_tool":
        raise ValueError("protocol/command mismatch")
    if protocol == 3:
        tool_action = ToolExecutionInput.from_wire(value["tool_action"])
        validate_identity(activity_id, executor_id, tool_action.operation_id, run_tag)
        return ledger, config, activity_id, executor_id, command, run_tag, deadline_ns, None, tool_action
    one_call = OneCallInput.from_wire(value["one_call"]) if value["one_call"] is not None else None
    if command.task == "one_call":
        if one_call is None:
            raise ValueError("missing one_call data")
        validate_identity(activity_id, executor_id, one_call.operation_id, run_tag)
        if one_call.request.input_result is not None and one_call.request.input_result.activity_id != activity_id:
            raise ValueError("input result activity mismatch")
    elif one_call is not None:
        raise ValueError("unexpected business data")
    return ledger, config, activity_id, executor_id, command, run_tag, deadline_ns, one_call, None


def main() -> int:
    if len(sys.argv) != 2:
        return 2
    mapping = None
    try:
        mapping = NamedMapping.open_existing(sys.argv[1])
        ledger, config, activity_id, executor_id, command, run_tag, deadline_ns, one_call, tool_action = _validated_request(
            mapping.read_request(), sys.argv[1],
        )
        with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:
            outcome = runner.run(SingleWindowSupervisor(ledger, config).run_once(
                activity_id, executor_id, command, run_tag=run_tag,
                manager_deadline_ns=deadline_ns,
                one_call=one_call,
                tool_action=tool_action,
            ))
        protocol = 3 if command.task == "one_tool" else 2
        data = asdict(outcome)
        if protocol == 2:
            # 外2精确旧字段集：排除新tool_receipt。
            if data.pop("tool_receipt") is not None:
                raise ValueError("protocol 2 outcome carries tool receipt")
        mapping.write_result({"protocol": protocol, "run_tag": run_tag, "activity_id": activity_id,
                              "outcome": data})
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

