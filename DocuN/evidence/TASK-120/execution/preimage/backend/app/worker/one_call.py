"""内部单次调用的数据合同；G3 协议3：回执仅身份/状态/hash，正文从数据库读取。

SUCCEEDED 回执表示正文已与 received 同事务提交并获 record 确认；只携带
payload_sha256，text/json_object 恒为 None。business_commit 三值：
committed（本次已确认持久正文）/ unconfirmed（尝试提交但未确认结果，不是
“未提交”）/ not_committed（本次返回不携带成功提交确认，不否定同键历史）。
"""
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
_HEX64 = re.compile(r"[0-9a-f]{64}\Z")


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

    @property
    def protocol(self):
        from app.capabilities.embedding import EmbeddingRequest
        return 4 if type(self.request) is EmbeddingRequest or self.request.retrieval_ref is not None or self.service.outbound_grant is not None else 3

    @property
    def capability_kind(self):
        from app.capabilities.embedding import EmbeddingRequest
        return 'embedding' if type(self.request) is EmbeddingRequest else 'model'

    def to_wire(self):
        if type(self.operation_id) is not str or _ID.fullmatch(self.operation_id) is None:
            raise ValueError("invalid operation identity")
        from app.capabilities.embedding import EmbeddingRequest, EmbeddingServiceConfig
        embedding = type(self.request) is EmbeddingRequest
        if not ((embedding and type(self.service) is EmbeddingServiceConfig)
                or (type(self.request) is ModelCallRequest and type(self.service) is ModelServiceConfig)):
            raise TypeError("typed request and service required")
        if max(self.service.max_request_bytes, self.service.max_response_bytes) > MAX_BODY_BYTES:
            raise ValueError("internal one_call supports at most 65536 configured body bytes")
        if len(self.service.api_key.get_secret_value().encode("utf-8")) > 4096:
            raise ValueError("credential exceeds internal limit")
        if self.request.input_result is not None and self.request.input_result.operation_id == self.operation_id:
            raise ValueError("invalid_input")
        request_wire=self.request.model_dump(mode="json",exclude_none=self.protocol!=4)
        bounded(request_wire, MAX_BODY_BYTES)
        # 原v3服务字段及字节保持；仅新v4承载新增受信grant。
        service = self.service.model_dump(mode="json", exclude={name for name in ('outbound_grant','outbound_source_manifest') if getattr(self.service,name,None) is None})
        service["api_key"] = self.service.api_key.get_secret_value()
        value = {"operation_id": self.operation_id,
                 "request": request_wire, "service": service}
        if self.protocol == 4:
            value = {'protocol': 4, 'capability_kind': self.capability_kind, **value}
        value = bounded(value)
        # 重新校验，避免 model_construct/model_copy 绕过冻结模型的正常验证。
        try:
            if embedding:
                EmbeddingServiceConfig.model_validate_json(json.dumps(service))
                EmbeddingRequest.model_validate_json(json.dumps(value['request']))
            else:
                ModelServiceConfig.model_validate(service)
                ModelCallRequest.model_validate(value["request"])
        except Exception:
            raise ValueError("invalid one_call configuration/request") from None
        return value

    @classmethod
    def from_wire(cls, value):
        v4 = type(value) is dict and type(value.get('protocol')) is int and value.get('protocol') == 4
        exact(value, ("protocol", "capability_kind", "operation_id", "request", "service") if v4 else ("operation_id", "request", "service"))
        bounded(value)
        try:
            if v4 and value['capability_kind'] == 'embedding':
                from app.capabilities.embedding import EmbeddingRequest, EmbeddingServiceConfig
                result = cls(value['operation_id'], EmbeddingRequest.model_validate_json(json.dumps(value['request'])),
                             EmbeddingServiceConfig.model_validate_json(json.dumps(value['service'])))
            else:
                if v4 and value['capability_kind'] != 'model': raise ValueError('capability_kind_invalid')
                result = cls(value["operation_id"], ModelCallRequest.model_validate(value["request"]),
                             ModelServiceConfig.model_validate(value["service"]))
            if v4 and result.protocol != 4: raise ValueError('capability_protocol_binding_invalid')
            result.to_wire()
            return result
        except Exception:
            raise ValueError("invalid one_call input") from None


def worker_request(call, ledger_data, lease, run_tag, stop_ns, call_seconds):
    if call.request.input_result is not None and call.request.input_result.activity_id != lease.activity_id:
        raise ValueError("invalid_input")
    context = CallContext(activity_id=lease.activity_id, executor_id=lease.executor_id,
                          operation_id=call.operation_id, execution_generation=lease.execution_generation,
                          scope_revision=lease.scope_revision)
    return {"protocol": call.protocol, "call": call.to_wire(), "ledger": ledger_data,
            "context": context.model_dump(), "run_tag": run_tag,
            "stop_ns": stop_ns, "call_seconds": call_seconds}


def decode_worker_request(value):
    exact(value, ("protocol", "call", "ledger", "context", "run_tag", "stop_ns", "call_seconds"))
    if type(value["protocol"]) is not int or value["protocol"] not in (3, 4):
        raise ValueError("worker protocol mismatch")
    call = OneCallInput.from_wire(value["call"])
    if call.protocol != value['protocol']: raise ValueError('capability_protocol_binding_invalid')
    context = CallContext.model_validate(value["context"], strict=True)
    validate_identity(context.activity_id, context.executor_id, call.operation_id, value["run_tag"])
    if call.request.input_result is not None and call.request.input_result.activity_id != context.activity_id:
        raise ValueError("worker input result activity mismatch")
    if context.operation_id != call.operation_id or context.execution_generation < 1:
        raise ValueError("worker identity mismatch")
    exact(value["ledger"], ("dsn", "connect_timeout_seconds", "statement_timeout_ms", "lock_timeout_ms") + (('data_guard',) if 'data_guard' in value['ledger'] else ()))
    dsn = value["ledger"]["dsn"]
    if type(dsn) is not str or not 1 <= len(dsn.encode("utf-8")) <= 4096 or "\0" in dsn:
        raise ValueError("invalid ledger configuration")
    seconds = value["call_seconds"]
    if type(seconds) not in (float, int) or not 0 < seconds <= 120 or call.service.timeout_seconds > seconds:
        raise ValueError("call timeout incompatible with session")
    if type(value["stop_ns"]) is not int or (value["stop_ns"] - time.monotonic_ns()) / 1e9 <= seconds + 0.25:
        raise ValueError("insufficient actual call window")
    return call, context


def receipt(result, context, run_tag, *, capability_kind=None):
    """协议3 回执：状态/身份/hash，result 去正文副本（text/json_object 恒 None）。

    business_commit 推导：succeeded→committed（缺合法 hash 属内部错误即拒）；
    unknown 且 record_denied/record_unconfirmed→unconfirmed；其余→not_committed。
    """
    status = result.status.value
    if status == "succeeded":
        if type(result.payload_sha256) is not str or _HEX64.fullmatch(result.payload_sha256) is None:
            raise ValueError("succeeded result lacks confirmed payload digest")
        commit = "committed"
    elif status == "unknown" and result.error_code in ("record_denied", "record_unconfirmed"):
        commit = "unconfirmed"
    else:
        commit = "not_committed"
    if result.error_code in ("record_denied", "record_unconfirmed") and status != "unknown":
        raise ValueError("record uncertainty requires unknown status")
    from app.capabilities.embedding import EmbeddingCallResult
    embedding = type(result) is EmbeddingCallResult
    data = asdict(result)
    if not embedding:
        data["text"] = None
        data["json_object"] = None
    value = {"protocol": 4 if embedding or capability_kind is not None else 3,
             "context": context.model_dump(), "run_tag": run_tag, "business_commit": commit, "result": data}
    if value['protocol'] == 4: value['capability_kind'] = 'embedding' if embedding else 'model'
    return bounded(value)


def decode_receipt(value, context, run_tag):
    if type(value) is dict and value.get('protocol') == 4:
        exact(value, ('protocol','context','run_tag','business_commit','capability_kind','result'))
        if value['capability_kind'] == 'model':
            legacy = dict(value); legacy.pop('capability_kind'); legacy['protocol'] = 3
            return decode_receipt(legacy, context, run_tag)
        if value['capability_kind'] != 'embedding' or value['context'] != context.model_dump() or value['run_tag'] != run_tag:
            raise ValueError('embedding_receipt_binding_invalid')
        from app.capabilities.embedding import EmbeddingCallResult
        from app.capabilities.contracts import CallStatus, Usage
        bounded(value)
        data = dict(value['result']); exact(data, (f.name for f in fields(EmbeddingCallResult)))
        if data['operation_id'] != context.operation_id or data['provider'] != 'zhipu_embeddings' or data['configured_model'] != 'embedding-3':
            raise ValueError('embedding_receipt_identity_invalid')
        data['status'] = CallStatus(data['status'])
        for name in ('returned_model','error_code','remote_request_id'):
            item=data[name]
            if item is not None and (type(item) is not str or _ID.fullmatch(item) is None):raise ValueError('embedding_receipt_invalid')
        usage=data['usage']
        if usage is not None:
            exact(usage, ('prompt_tokens','completion_tokens','total_tokens'))
            if any(type(x) is not int or x<0 for x in usage.values()) or usage['completion_tokens']!=0 or usage['total_tokens']!=usage['prompt_tokens']:
                raise ValueError('embedding_receipt_usage_invalid')
            data['usage']=Usage(**usage)
        succeeded=data['status'] is CallStatus.SUCCEEDED
        if succeeded:
            if type(data['payload_sha256']) is not str or _HEX64.fullmatch(data['payload_sha256']) is None or value['business_commit']!='committed':
                raise ValueError('embedding_receipt_commit_invalid')
        elif data['payload_sha256'] is not None or value['business_commit'] not in ('unconfirmed','not_committed'):
            raise ValueError('embedding_receipt_commit_invalid')
        return EmbeddingCallResult(**data)
    exact(value, ("protocol", "context", "run_tag", "business_commit", "result"))
    bounded(value)
    try:
        received_context = CallContext.model_validate(value["context"], strict=True)
    except Exception:
        raise ValueError("invalid receipt context") from None
    if (type(value["protocol"]) is not int or value["protocol"] != 3 or value["context"] != context.model_dump()
            or value["run_tag"] != run_tag or value["business_commit"] not in ("committed", "not_committed", "unconfirmed")):
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
    # 协议3 严格配对：正文永不夹带回执；SUCCEEDED 必须 committed 且 hash 合法。
    digest = data["payload_sha256"]
    if data["status"] == "succeeded":
        if value["business_commit"] != "committed":
            raise ValueError("succeeded receipt requires committed confirmation")
        if type(digest) is not str or _HEX64.fullmatch(digest) is None:
            raise ValueError("invalid payload digest")
        if data["text"] is not None or data["json_object"] is not None or data["tool_plans"]:
            raise ValueError("receipt carries business payload")
    elif data["status"] == "tool_plan":
        if value["business_commit"] != "not_committed":
            raise ValueError("plan receipt requires not_committed")
        if digest is not None or not data["tool_plans"] or data["text"] is not None or data["json_object"] is not None:
            raise ValueError("invalid plan receipt")
    else:
        expected_commit = (
            "unconfirmed" if data["status"] == "unknown"
            and data["error_code"] in ("record_denied", "record_unconfirmed") else "not_committed"
        )
        if value["business_commit"] != expected_commit:
            raise ValueError("receipt commit does not match status and error")
        if digest is not None or data["text"] is not None or data["json_object"] is not None or data["tool_plans"]:
            raise ValueError("failure receipt carries business output")
    if data["error_code"] in ("record_denied", "record_unconfirmed") and data["status"] != "unknown":
        raise ValueError("record uncertainty requires unknown status")
    try:
        return TypeAdapter(ModelCallResult).validate_json(json.dumps(data, allow_nan=False))
    except Exception:
        raise ValueError("invalid model receipt") from None


def run_one_call(ledger, config, activity_id: str, executor_id: str, operation_id: str,
                 request: ModelCallRequest, service: ModelServiceConfig, *, run_tag: str):
    """阻塞受信内部入口。SUCCEEDED 表示正文已同事务提交并获确认。

    取消/来源/代次可在返回后变化；回执仅携带 payload_sha256，正文经只读
    恢复接口从持久层读取，不夹带跨进程副本。
    """
    from .command import WorkerCommand
    from .launcher import run_supervised_window
    validate_identity(activity_id, executor_id, operation_id, run_tag)
    if request.input_result is not None and request.input_result.activity_id != activity_id:
        raise ValueError("invalid_input")
    call = OneCallInput(operation_id, request, service)
    call.to_wire()
    if config.request_timeout_seconds > 120:
        raise ValueError("one_call request timeout exceeds 120s limit")
    if service.timeout_seconds > config.request_timeout_seconds:
        raise ValueError("model timeout exceeds supervised call budget")
    return run_supervised_window(ledger, config, activity_id, executor_id, WorkerCommand("one_call"),
                                 run_tag=run_tag, one_call=call)


def run_one_embedding(ledger, config, activity_id, executor_id, operation_id, request, service, *, run_tag):
    """独立typed能力复用原SUP封套；不改停止、退款或RootLease主权。"""
    from app.capabilities.embedding import EmbeddingRequest, EmbeddingServiceConfig
    if type(request) is not EmbeddingRequest or type(service) is not EmbeddingServiceConfig:
        raise TypeError('typed_embedding_input_required')
    return run_one_call(ledger,config,activity_id,executor_id,operation_id,request,service,run_tag=run_tag)
