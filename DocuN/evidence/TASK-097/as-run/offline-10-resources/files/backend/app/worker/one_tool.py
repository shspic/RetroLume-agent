"""内部工具动作的数据合同；工具外3／SUP↔worker内4，严格帧、不协商降级。

工具回执（协议4）仅 context、run_tag、business_commit 与 result；result 精确
包含 kind/name/call_id/arguments_sha256/status/error_code/payload_sha256，
不带参数、结果正文、tool_plans、provider 或 usage。SUCCEEDED 必须已获
record 提交确认并有合法结果 hash，business_commit=committed；
record_denied/record_unconfirmed 必须 UNKNOWN+unconfirmed 且无成功 hash；
其余本次未携带成功提交确认为 not_committed（不否定同键历史）。
"""

from __future__ import annotations

import time

from app.capabilities.contracts import (
    CallContext,
    ToolCallResult,
    ToolCallStatus,
    ToolExecutionInput,
)

from .one_call import _HEX64, _ID, bounded, exact, validate_identity

TOOL_PROTOCOL = 4

# 回执 result 的精确字段集；不使用动态fields同时接收两个版本。
_RESULT_FIELDS = ("kind", "name", "call_id", "arguments_sha256", "status", "error_code", "payload_sha256")


def worker_request_tool(call: ToolExecutionInput, ledger_data: dict, lease, run_tag: str,
                        stop_ns: int, call_seconds: float) -> dict:
    """SUP→worker 协议4请求；context 取 SUP 实际 lease，不来自调用方传参。"""
    wire = call.to_wire()
    context = CallContext(
        activity_id=lease.activity_id, executor_id=lease.executor_id,
        operation_id=call.operation_id, execution_generation=lease.execution_generation,
        scope_revision=lease.scope_revision,
    )
    frame = {
        "protocol": TOOL_PROTOCOL,
        "call": wire, "ledger": ledger_data, "context": context.model_dump(),
        "run_tag": run_tag, "stop_ns": stop_ns, "call_seconds": call_seconds,
    }
    bounded(frame)
    return frame


def decode_tool_worker_request(value: dict) -> tuple[ToolExecutionInput, CallContext]:
    exact(value, ("protocol", "call", "ledger", "context", "run_tag", "stop_ns", "call_seconds"))
    if type(value["protocol"]) is not int or value["protocol"] != TOOL_PROTOCOL:
        raise ValueError("worker protocol mismatch")
    call = ToolExecutionInput.from_wire(value["call"])
    context = CallContext.model_validate(value["context"], strict=True)
    validate_identity(context.activity_id, context.executor_id, call.operation_id, value["run_tag"])
    if context.operation_id != call.operation_id or context.execution_generation < 1:
        raise ValueError("worker identity mismatch")
    exact(value["ledger"], ("dsn", "connect_timeout_seconds", "statement_timeout_ms", "lock_timeout_ms"))
    dsn = value["ledger"]["dsn"]
    if type(dsn) is not str or not 1 <= len(dsn.encode("utf-8")) <= 4096 or "\0" in dsn:
        raise ValueError("invalid ledger configuration")
    seconds = value["call_seconds"]
    if type(seconds) not in (float, int) or not 0 < seconds <= 120:
        raise ValueError("tool call timeout invalid")
    if type(value["stop_ns"]) is not int or (value["stop_ns"] - time.monotonic_ns()) / 1e9 <= seconds + 0.25:
        raise ValueError("insufficient actual tool window")
    return call, context


def tool_receipt(result: ToolCallResult, context: CallContext, run_tag: str) -> dict:
    """协议4回执；正文永不夹带回执，仅携带已确认的 payload_sha256。"""
    if type(result) is not ToolCallResult or type(result.status) is not ToolCallStatus:
        raise ValueError("invalid tool result")
    status = result.status
    digest = result.payload_sha256
    if status is ToolCallStatus.SUCCEEDED:
        if type(digest) is not str or _HEX64.fullmatch(digest) is None:
            raise ValueError("succeeded tool result lacks confirmed payload digest")
        commit = "committed"
    elif status is ToolCallStatus.UNKNOWN and result.error_code in ("record_denied", "record_unconfirmed"):
        if digest is not None:
            raise ValueError("unconfirmed tool result carries payload digest")
        commit = "unconfirmed"
    else:
        if digest is not None:
            raise ValueError("non-committed tool result carries payload digest")
        commit = "not_committed"
    if result.error_code in ("record_denied", "record_unconfirmed") and status is not ToolCallStatus.UNKNOWN:
        raise ValueError("record uncertainty requires unknown status")
    data = {
        "kind": "tool",
        "name": result.name, "call_id": result.call_id,
        "arguments_sha256": result.arguments_sha256, "status": status.value,
        "error_code": result.error_code, "payload_sha256": digest,
    }
    frame = {
        "protocol": TOOL_PROTOCOL, "context": context.model_dump(), "run_tag": run_tag,
        "business_commit": commit, "result": data,
    }
    bounded(frame)
    return frame


def decode_tool_receipt(value: dict, context: CallContext, run_tag: str,
                        call: ToolExecutionInput) -> ToolCallResult:
    """逐跳复核工具回执：身份、参数与请求一致；三值提交确认严格配对。"""
    exact(value, ("protocol", "context", "run_tag", "business_commit", "result"))
    bounded(value)
    try:
        received_context = CallContext.model_validate(value["context"], strict=True)
    except Exception:
        raise ValueError("invalid receipt context") from None
    if (
        type(value["protocol"]) is not int or value["protocol"] != TOOL_PROTOCOL
        or value["context"] != context.model_dump() or received_context != context
        or value["run_tag"] != run_tag
        or value["business_commit"] not in ("committed", "not_committed", "unconfirmed")
    ):
        raise ValueError("tool receipt identity mismatch")
    data = value["result"]
    exact(data, _RESULT_FIELDS)
    if data["kind"] != "tool":
        raise ValueError("tool receipt kind mismatch")
    if (data["name"] != call.name or data["call_id"] != call.call_id
            or data["arguments_sha256"] != call.arguments_sha256):
        raise ValueError("tool receipt call mismatch")
    if type(data["arguments_sha256"]) is not str or _HEX64.fullmatch(data["arguments_sha256"]) is None:
        raise ValueError("invalid tool arguments digest")
    if data["status"] not in {item.value for item in ToolCallStatus}:
        raise ValueError("invalid tool status")
    error = data["error_code"]
    if error is not None and (type(error) is not str or _ID.fullmatch(error) is None or len(error) > 64):
        raise ValueError("invalid tool error code")
    digest = data["payload_sha256"]
    if digest is not None and (type(digest) is not str or _HEX64.fullmatch(digest) is None):
        raise ValueError("invalid tool payload digest")
    if data["status"] == "succeeded":
        if value["business_commit"] != "committed" or digest is None:
            raise ValueError("succeeded tool receipt requires committed hash")
    elif data["status"] == "unknown" and error in ("record_denied", "record_unconfirmed"):
        if value["business_commit"] != "unconfirmed" or digest is not None:
            raise ValueError("record uncertainty requires unconfirmed without hash")
    else:
        if value["business_commit"] != "not_committed" or digest is not None:
            raise ValueError("tool receipt commit does not match status")
    if error in ("record_denied", "record_unconfirmed") and data["status"] != "unknown":
        raise ValueError("record uncertainty requires unknown status")
    return ToolCallResult(
        ToolCallStatus(data["status"]), data["name"], data["call_id"],
        data["arguments_sha256"], error, digest,
    )


def run_one_tool(ledger, config, activity_id: str, executor_id: str,
                 call: ToolExecutionInput, *, run_tag: str):
    """阻塞受信内部入口：经既有受控 launcher/SUP/worker 执行一次工具动作。

    服务不claim、不execute、不settle；所有工具配置、规范字节、身份与
    有限时限在 launcher/SUP claim 之前早拒。
    """
    from .command import WorkerCommand
    from .launcher import run_supervised_window
    if type(call) is not ToolExecutionInput:
        raise TypeError("typed tool input required")
    validate_identity(activity_id, executor_id, call.operation_id, run_tag)
    call.to_wire()
    if config.request_timeout_seconds > 120:
        raise ValueError("tool request timeout exceeds 120s limit")
    return run_supervised_window(ledger, config, activity_id, executor_id, WorkerCommand("one_tool"),
                                 run_tag=run_tag, tool_action=call)
