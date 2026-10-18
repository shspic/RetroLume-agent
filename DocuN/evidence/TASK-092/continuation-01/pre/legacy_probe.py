"""TASK-092 混用版本探针：旧版 SUP 校验与旧版 worker main 的行为等价副本。

正文对齐 pre/app_worker_supervisor_main.py 与 pre/app_worker_main.py（本卡
实施前原件，sha256 见 pre-hashes.txt）；只用于证明版本混用时失败关闭与
"时间可能已预扣"，不进入产品导入链。
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
import time
from dataclasses import fields
from uuid import UUID

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))


def pre_hashes() -> dict:
    pre = HERE / "pre"
    return {"supervisor_main": hashlib.sha256((pre / "app_worker_supervisor_main.py").read_bytes()).hexdigest(),
            "worker_main": hashlib.sha256((pre / "app_worker_worker_main.py").read_bytes()).hexdigest()}


def legacy_validated_request(value: dict, mapping_name: str):
    """旧版正文副本：只接受 protocol=2 的单形状请求。"""
    from app.activities import PostgresAdmissionLedger
    from app.worker.command import WorkerCommand
    from app.worker.one_call import OneCallInput, validate_identity
    from app.worker.session import SessionConfig
    import re
    _RUN_TAG = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")
    if (type(value) is not dict or set(value) != {"protocol", "mapping_name", "activity_id", "executor_id",
            "run_tag", "deadline_ns", "command", "config", "ledger", "one_call"}
            or value.get("protocol") != 2 or value.get("mapping_name") != mapping_name):
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
    one_call = OneCallInput.from_wire(value["one_call"]) if value["one_call"] is not None else None
    if command.task == "one_call":
        if one_call is None:
            raise ValueError("missing one_call data")
        validate_identity(activity_id, executor_id, one_call.operation_id, run_tag)
        if one_call.request.input_result is not None and one_call.request.input_result.activity_id != activity_id:
            raise ValueError("input result activity mismatch")
    elif one_call is not None:
        raise ValueError("unexpected business data")
    return ledger, config, activity_id, executor_id, command, run_tag, deadline_ns, one_call


def legacy_sup_main(evidence: Path, mapping_name: str) -> int:
    """旧版 SUP 主体：解码失败即退出1，无 claim、无任何数据库动作。"""
    from app.worker.supervisor_ipc import NamedMapping
    outcome = {"mode": "legacy-sup", "pid": os.getpid(), "protocol_seen": None, "rejected": False}
    mapping = None
    try:
        try:
            mapping = NamedMapping.open_existing(mapping_name)
            value = mapping.read_request()
            outcome["protocol_seen"] = value.get("protocol")
            legacy_validated_request(value, mapping_name)
        except BaseException as exc:
            outcome["rejected"] = True
            outcome["error_type"] = type(exc).__name__
            return 1
        raise AssertionError("legacy probe only models the rejection branch")
    finally:
        if mapping is not None:
            try:
                mapping.close()
            except BaseException:
                pass
        (evidence / f"legacy-sup-{os.getpid()}.json").write_text(
            json.dumps({**outcome, "pre_source_hashes": pre_hashes()}, indent=2), encoding="utf-8")


def legacy_worker_main() -> int:
    """旧版 worker main 正文副本：one_tool 不被承认，按旧 argv 规则退出2。"""
    if sys.argv[1:] == ["idle"]:
        return 0
    if len(sys.argv) != 3 or sys.argv[1] != "one_call":
        return 2
    raise AssertionError("legacy probe only models the rejection branch")


if __name__ == "__main__":
    if sys.argv[1] == "old_sup":
        raise SystemExit(legacy_sup_main(Path(sys.argv[2]).resolve(), sys.argv[3]))
    raise SystemExit(2)
