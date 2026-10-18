"""内部单次调用的数据合同；回执只是未提交的模型返回，不是业务写入授权。"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
import json
import re
import time
from uuid import UUID

from pydantic import TypeAdapter

from app.capabilities.contracts import (
    CallContext, ModelCallRequest, ModelCallResult, ModelServiceConfig,
)

MAX_BODY_BYTES = 65_536
MAX_DATA_BYTES = 131_072
_ID = re.compile(r"[A-Za-z0-9._:/-]{1,128}\Z")
_TAG = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")


def bounded(value, limit=MAX_DATA_BYTES):
    try:
        raw = json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
        if len(raw) > limit:
            raise ValueError
    except (ValueError, TypeError, RecursionError):
        raise ValueError("one_call data exceeds contract") from None
    return value


def exact(value, names):
    if type(value) is not dict or set(value) != set(names):
        raise ValueError("one_call schema mismatch")


def validate_identity(activity_id, executor_id, operation_id, run_tag):
    if type(activity_id) is not str or str(UUID(activity_id)) != activity_id:
        raise ValueError("invalid activity identity")
    if any(type(x) is not str or _ID.fullmatch(x) is None for x in (executor_id, operation_id)):
        raise ValueError("invalid executor/operation identity")
    if type(run_tag) is not str or _TAG.fullmatch(run_tag) is None:
        raise ValueError("invalid run identity")


@dataclass(frozen=True)
class OneCallInput:
    operation_id: str
    request: ModelCallRequest = field(repr=False)
    service: ModelServiceConfig = field(repr=False)

    def to_wire(self):
        if type(self.operation_id) is not str or _ID.fullmatch(self.operation_id) is None:
            raise ValueError("invalid operation identity")
        if type(self.request) is not ModelCallRequest or type(self.service) is not ModelServiceConfig:
            raise TypeError("typed request and service required")
        if max(self.service.max_request_bytes, self.service.max_response_bytes) > MAX_BODY_BYTES:
            raise ValueError("internal one_call supports at most 65536 configured body bytes")
        if len(self.service.api_key.get_secret_value().encode("utf-8")) > 4096:
            raise ValueError("credential exceeds internal limit")
        service = self.service.model_dump(mode="json")
        service["api_key"] = self.service.api_key.get_secret_value()
        value = bounded({"operation_id": self.operation_id,
                         "request": self.request.model_dump(mode="json"), "service": service})
        # 重新校验，避免 model_construct/model_copy 绕过冻结模型的正常验证。
        try:
            ModelServiceConfig.model_validate(service)
            ModelCallRequest.model_validate(value["request"])
        except Exception:
            raise ValueError("invalid one_call configuration/request") from None
        return value

    @classmethod
    def from_wire(cls, value):
        exact(value, ("operation_id", "request", "service"))
        bounded(value)
        try:
            result = cls(value["operation_id"], ModelCallRequest.model_validate(value["request"]),
                         ModelServiceConfig.model_validate(value["service"]))
            result.to_wire()
            return result
        except Exception:
            raise ValueError("invalid one_call input") from None


def worker_request(call, ledger_data, lease, run_tag, stop_ns, call_seconds):
    context = CallContext(activity_id=lease.activity_id, executor_id=lease.executor_id,
                          operation_id=call.operation_id, execution_generation=lease.execution_generation,
                          scope_revision=lease.scope_revision)
    return {"protocol": 2, "call": call.to_wire(), "ledger": ledger_data,
            "context": context.model_dump(), "run_tag": run_tag,
            "stop_ns": stop_ns, "call_seconds": call_seconds}


def decode_worker_request(value):
    exact(value, ("protocol", "call", "ledger", "context", "run_tag", "stop_ns", "call_seconds"))
    if type(value["protocol"]) is not int or value["protocol"] != 2:
        raise ValueError("worker protocol mismatch")
    call = OneCallInput.from_wire(value["call"])
    context = CallContext.model_validate(value["context"], strict=True)
    validate_identity(context.activity_id, context.executor_id, call.operation_id, value["run_tag"])
    if context.operation_id != call.operation_id or context.execution_generation < 1:
        raise ValueError("worker identity mismatch")
    exact(value["ledger"], ("dsn", "connect_timeout_seconds", "statement_timeout_ms", "lock_timeout_ms"))
    dsn = value["ledger"]["dsn"]
    if type(dsn) is not str or not 1 <= len(dsn.encode("utf-8")) <= 4096 or "\0" in dsn:
        raise ValueError("invalid ledger configuration")
    seconds = value["call_seconds"]
    if type(seconds) not in (float, int) or not 0 < seconds <= 120 or call.service.timeout_seconds > seconds:
        raise ValueError("call timeout incompatible with session")
    if type(value["stop_ns"]) is not int or (value["stop_ns"] - time.monotonic_ns()) / 1e9 <= seconds + 0.25:
        raise ValueError("insufficient actual call window")
    return call, context


def receipt(result, context, run_tag):
    return bounded({"protocol": 2, "context": context.model_dump(), "run_tag": run_tag,
                    "business_commit": "not_committed", "result": asdict(result)})


def decode_receipt(value, context, run_tag):
    exact(value, ("protocol", "context", "run_tag", "business_commit", "result"))
    bounded(value)
    try:
        received_context = CallContext.model_validate(value["context"], strict=True)
    except Exception:
        raise ValueError("invalid receipt context") from None
    if (type(value["protocol"]) is not int or value["protocol"] != 2 or value["context"] != context.model_dump()
            or value["run_tag"] != run_tag or value["business_commit"] != "not_committed"):
        raise ValueError("model receipt identity mismatch")
    data = value["result"]
    exact(data, (f.name for f in fields(ModelCallResult)))
    if data["operation_id"] != context.operation_id:
        raise ValueError("model operation mismatch")
    for name in ("configured_model", "returned_model", "finish_reason", "error_code", "remote_request_id"):
        item = data[name]
        if item is not None and (type(item) is not str or _ID.fullmatch(item) is None):
            raise ValueError("invalid receipt metadata")
    if data["usage"] is not None:
        exact(data["usage"], ("prompt_tokens", "completion_tokens", "total_tokens"))
        if any(type(n) is not int or n < 0 for n in data["usage"].values()):
            raise ValueError("invalid usage")
        if data["usage"]["total_tokens"] < data["usage"]["prompt_tokens"] + data["usage"]["completion_tokens"]:
            raise ValueError("invalid usage totals")
    if type(data["tool_plans"]) not in (list, tuple) or len(data["tool_plans"]) > 8:
        raise ValueError("invalid tool plans")
    for plan in data["tool_plans"]:
        exact(plan, ("call_id", "name", "arguments"))
        from app.capabilities.tools import ToolRegistry
        try:
            ToolRegistry().plan(plan["call_id"], plan["name"], json.dumps(plan["arguments"]), frozenset({"finite_calculate"}))
        except Exception:
            raise ValueError("invalid receipt tool plan") from None
    if data["status"] == "succeeded":
        if bool(data["text"] is not None) == bool(data["json_object"] is not None) or data["tool_plans"]:
            raise ValueError("invalid successful receipt")
    elif data["status"] == "tool_plan":
        if not data["tool_plans"] or data["text"] is not None or data["json_object"] is not None:
            raise ValueError("invalid plan receipt")
    elif data["text"] is not None or data["json_object"] is not None or data["tool_plans"]:
        raise ValueError("failure receipt carries business output")
    try:
        return TypeAdapter(ModelCallResult).validate_json(json.dumps(data, allow_nan=False))
    except Exception:
        raise ValueError("invalid model receipt") from None


def run_one_call(ledger, config, activity_id: str, executor_id: str, operation_id: str,
                 request: ModelCallRequest, service: ModelServiceConfig, *, run_tag: str):
    """阻塞受信内部入口。SUCCEEDED 仅为模型返回，业务成果尚未提交。

    调用者不得把本回执当作原子提交凭证；取消/来源/代次可在返回后变化。
    正文仅存于短生命周期内存，不支持重启后幂等取回。
    """
    from .command import WorkerCommand
    from .launcher import run_supervised_window
    validate_identity(activity_id, executor_id, operation_id, run_tag)
    call = OneCallInput(operation_id, request, service)
    call.to_wire()
    if service.timeout_seconds > config.request_timeout_seconds:
        raise ValueError("model timeout exceeds supervised call budget")
    return run_supervised_window(ledger, config, activity_id, executor_id, WorkerCommand("one_call"),
                                 run_tag=run_tag, one_call=call)
