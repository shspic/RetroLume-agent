"""受控模型入口的公开数据契约。"""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Literal, Mapping, Protocol, Sequence
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator, model_validator


class Provider(StrEnum):
    DEEPSEEK_CHAT_COMPLETIONS = "deepseek_chat_completions"


class ThinkingMode(StrEnum):
    ENABLED = "enabled"
    DISABLED = "disabled"


_ALLOWED_BASE_URLS = {
    Provider.DEEPSEEK_CHAT_COMPLETIONS: frozenset({"https://api.deepseek.com"}),
}


class ModelServiceConfig(BaseModel):
    """只能由服务端配置构造；密钥不会出现在 repr 中。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    provider: Provider
    base_url: str
    model: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:/-]+$")
    api_key: SecretStr = Field(repr=False)
    thinking: ThinkingMode = ThinkingMode.DISABLED
    timeout_seconds: float = Field(default=30.0, gt=0, le=120)
    max_output_tokens_limit: int = Field(default=8192, ge=1, le=32768)
    max_request_bytes: int = Field(default=262_144, ge=1024, le=2_097_152)
    max_response_bytes: int = Field(default=1_048_576, ge=1024, le=4_194_304)

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, value: str, info: Any) -> str:
        normalized = value.rstrip("/")
        provider = info.data.get("provider")
        if provider is None or normalized not in _ALLOWED_BASE_URLS.get(provider, frozenset()):
            raise ValueError("base_url 不在所选服务类型的固定允许列表中")
        return normalized

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value().strip():
            raise ValueError("api_key 不能为空")
        return value


class ToolFunctionCall(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    arguments: str = Field(max_length=2048)


class AssistantToolCall(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = Field(min_length=1, max_length=128)
    type: Literal["function"] = "function"
    function: ToolFunctionCall


class Message(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    role: str = Field(pattern=r"^(system|user|assistant|tool)$")
    content: str | None = Field(default=None, max_length=100_000)
    tool_call_id: str | None = Field(default=None, min_length=1, max_length=128)
    tool_calls: tuple[AssistantToolCall, ...] = Field(default_factory=tuple, max_length=8)

    @model_validator(mode="after")
    def validate_tool_message(self) -> "Message":
        if self.role in {"system", "user"}:
            if self.content is None or self.tool_call_id is not None or self.tool_calls:
                raise ValueError("system/user 消息只能包含 content")
        elif self.role == "assistant":
            if self.tool_call_id is not None:
                raise ValueError("assistant 消息不能包含 tool_call_id")
            if not self.tool_calls and (self.content is None or not self.content.strip()):
                raise ValueError("assistant 消息必须包含正文或工具调用")
        elif self.role == "tool":
            if self.content is None or self.tool_call_id is None or self.tool_calls:
                raise ValueError("tool 消息必须包含 content 和 tool_call_id")
        return self


class ResponseMode(StrEnum):
    TEXT = "text"
    JSON_OBJECT = "json_object"


class ModelCallRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    messages: tuple[Message, ...] = Field(min_length=1, max_length=128)
    max_output_tokens: int = Field(ge=1)
    response_mode: ResponseMode = ResponseMode.JSON_OBJECT
    allowed_tools: frozenset[str] = Field(default_factory=frozenset, max_length=16)

    @field_validator("allowed_tools")
    @classmethod
    def validate_tool_names(cls, value: frozenset[str]) -> frozenset[str]:
        for name in value:
            if not name or len(name) > 64:
                raise ValueError("工具名称长度非法")
        return value


class CallContext(BaseModel):
    """账本定位信息；它本身不是授权，必须由 ledger 原子准入。

    ID 契约与持久账本仓储一致：activity_id 必须可解析为 UUID；
    operation_id/executor_id 使用仓储相同的受限字符集。
    无效输入在契约校验时即拒绝，不做自动改名或静默规范化。
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    activity_id: str = Field(min_length=1, max_length=128)
    operation_id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:/-]+$")
    executor_id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:/-]+$")
    execution_generation: int = Field(ge=0)
    scope_revision: int = Field(ge=0)

    @field_validator("activity_id")
    @classmethod
    def validate_activity_id(cls, value: str) -> str:
        try:
            UUID(value)
        except (ValueError, TypeError, AttributeError):
            raise ValueError("activity_id 必须是可解析为 UUID 的字符串") from None
        return value


@dataclass(frozen=True)
class AdmissionIntent:
    context: CallContext
    provider: Provider
    configured_model: str
    request_bytes: int
    max_output_tokens: int
    tool_names: tuple[str, ...]


@dataclass(frozen=True)
class AdmissionPermit:
    """由持久账本返回并绑定到一次操作的不可复用受理凭证。"""

    admission_id: str
    operation_id: str
    executor_id: str


class LedgerDisposition(StrEnum):
    NOT_SENT = "not_sent"
    RECEIVED = "received"
    UNKNOWN = "unknown"


# G3 业务正文封套上限：与 007 迁移的 payload octet_length 上界一致。
BUSINESS_PAYLOAD_MAX_BYTES = 131_072
_PAYLOAD_FORMATS = ("text", "json")
_PAYLOAD_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def canonical_payload_bytes(envelope: Mapping[str, Any]) -> bytes:
    """封套 {format, value} 的规范 UTF-8 字节；不 sort_keys，解析序即键序。"""
    return json.dumps(
        envelope, ensure_ascii=False, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def payload_digest(envelope: Mapping[str, Any]) -> str:
    """规范字节的 SHA-256 小写十六进制摘要。"""
    return hashlib.sha256(canonical_payload_bytes(envelope)).hexdigest()


def _walk_payload_value(value: Any) -> None:
    """封套 value 的类型/有限数/深度/节点复查；与 gateway 成功解析不变式同界。"""
    nodes = 0

    def visit(item: Any, depth: int) -> None:
        nonlocal nodes
        nodes += 1
        if nodes > 2000 or depth > 12:
            raise ValueError("payload_structure_limit")
        if isinstance(item, dict):
            for key, child in item.items():
                if not isinstance(key, str):
                    raise ValueError("invalid_payload_json")
                visit(child, depth + 1)
        elif isinstance(item, list):
            for child in item:
                visit(child, depth + 1)
        elif item is not None:
            if not isinstance(item, (str, int, float, bool)):
                raise ValueError("invalid_payload_json")
            if isinstance(item, float) and not math.isfinite(item):
                raise ValueError("invalid_payload_json")

    visit(value, 0)


def build_business_payload(*, text: str | None = None, json_object: Mapping[str, Any] | None = None) -> tuple[str, str, str]:
    """构建规范封套并返回 (payload_format, payload_text, payload_sha256)。

    规范化 = 规范字节等值（非 JSON 语义等值）：键序按对象插入序、int/float 按
    Python json 输出，不 sort_keys，不承诺跨语言语义等价。编码后超过
    BUSINESS_PAYLOAD_MAX_BYTES 抛 ValueError("payload_limit")（先拒后写）。
    """
    if (text is None) == (json_object is None):
        raise ValueError("business payload requires exactly one of text/json_object")
    if text is not None:
        if not isinstance(text, str) or not text:
            raise ValueError("invalid_payload_text")
        envelope: dict[str, Any] = {"format": "text", "value": text}
    else:
        if not isinstance(json_object, Mapping):
            raise ValueError("invalid_payload_json")
        _walk_payload_value(json_object)
        envelope = {"format": "json", "value": json_object}
    raw = canonical_payload_bytes(envelope)
    if not 1 <= len(raw) <= BUSINESS_PAYLOAD_MAX_BYTES:
        raise ValueError("payload_limit")
    return envelope["format"], raw.decode("utf-8"), hashlib.sha256(raw).hexdigest()


def validate_business_payload(payload: str, payload_format: str, payload_sha256: str) -> tuple[str, str, str]:
    """对实际 payload 文本复查封套合法性并返回规范三元组。

    校验：三字段非空；payload 可解析为恰好 {format, value} 的封套（不把已有
    封套字符串再包一层）；format 值域；value 类型（text→非空 str，json→dict）；
    有限数与深度 12/节点 2000；UTF-8 字节长度 1..131072；解析后规范字节与
    原文逐字节相等；SHA-256 与实际字节匹配。任一不符抛 ValueError。
    """
    if not isinstance(payload, str) or not isinstance(payload_format, str) or not isinstance(payload_sha256, str):
        raise ValueError("payload fields must be strings")
    if payload_format not in _PAYLOAD_FORMATS:
        raise ValueError("invalid_payload_format")
    if _PAYLOAD_SHA256_RE.fullmatch(payload_sha256) is None:
        raise ValueError("invalid_payload_sha256")
    encoded = payload.encode("utf-8")
    if not 1 <= len(encoded) <= BUSINESS_PAYLOAD_MAX_BYTES:
        raise ValueError("payload_limit")
    try:
        parsed = json.loads(payload, parse_constant=lambda _: (_ for _ in ()).throw(ValueError("非有限数值")))
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError, RecursionError):
        raise ValueError("invalid_payload_envelope") from None
    if not isinstance(parsed, dict) or set(parsed) != {"format", "value"}:
        raise ValueError("invalid_payload_envelope")
    if parsed["format"] != payload_format:
        raise ValueError("payload_format_mismatch")
    value = parsed["value"]
    if payload_format == "text":
        if not isinstance(value, str) or not value:
            raise ValueError("invalid_payload_text")
    else:
        if not isinstance(value, dict):
            raise ValueError("invalid_payload_json")
        try:
            _walk_payload_value(value)
        except ValueError:
            raise ValueError("invalid_payload_json") from None
    try:
        if canonical_payload_bytes(parsed) != encoded:
            raise ValueError("payload_not_canonical")
    except (ValueError, TypeError, RecursionError):
        raise ValueError("payload_not_canonical") from None
    if hashlib.sha256(encoded).hexdigest() != payload_sha256:
        raise ValueError("payload_sha256_mismatch")
    return payload_format, payload, payload_sha256


@dataclass(frozen=True)
class LedgerOutcome:
    disposition: LedgerDisposition
    error_code: str | None = None
    remote_request_id: str | None = None
    returned_model: str | None = None
    finish_reason: str | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    response_bytes: int | None = None
    # G3 业务正文三字段：同存同缺（仓储侧强校验）；repr 不泄漏正文。
    payload_format: str | None = None
    payload: str | None = field(default=None, repr=False)
    payload_sha256: str | None = None


class RecordOutcome(StrEnum):
    """record_outcome 的持久提交确认；枚举返回本身不是持久性的独立证明。

    RECORDED：本次事务新写入并已 COMMIT 确认；
    ALREADY_PRESENT：终态严格等值（含正文存在性与 format/hash/规范内容）的
    无写确认。committed 仅指本次已确认；not_committed 不否定同键历史。
    """

    RECORDED = "recorded"
    ALREADY_PRESENT = "already_present"


class AdmissionLedger(Protocol):
    """STEP-008 的最小持久实现边界。

    admit 必须在一个短事务中验证活动/代次/范围/权限/剩余额度并预留；
    mark_dispatch_started 必须持久化不可逆出站边界；record_outcome 必须幂等。
    """

    async def admit(self, intent: AdmissionIntent) -> AdmissionPermit: ...

    async def mark_dispatch_started(self, permit: AdmissionPermit) -> None: ...

    async def record_outcome(self, permit: AdmissionPermit, outcome: LedgerOutcome) -> RecordOutcome: ...


class AdmissionUnavailable(RuntimeError):
    pass


class AdmissionDenied(RuntimeError):
    pass


class RejectingAdmissionLedger:
    """持久账本未接入时的默认失败关闭实现。"""

    async def admit(self, intent: AdmissionIntent) -> AdmissionPermit:
        del intent
        raise AdmissionUnavailable("持久准入账本尚未接入")

    async def mark_dispatch_started(self, permit: AdmissionPermit) -> None:
        del permit
        raise AdmissionUnavailable("持久准入账本尚未接入")

    async def record_outcome(self, permit: AdmissionPermit, outcome: LedgerOutcome) -> RecordOutcome:
        del permit, outcome
        raise AdmissionUnavailable("持久准入账本尚未接入")


class CallStatus(StrEnum):
    SUCCEEDED = "succeeded"
    TOOL_PLAN = "tool_plan"
    REJECTED = "rejected"
    NOT_SENT = "not_sent"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Usage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass(frozen=True)
class ToolCallPlan:
    call_id: str
    name: str
    arguments: Mapping[str, Any]


@dataclass(frozen=True)
class ModelCallResult:
    status: CallStatus
    operation_id: str
    provider: Provider
    configured_model: str
    returned_model: str | None = None
    finish_reason: str | None = None
    text: str | None = field(default=None, repr=False)
    json_object: Mapping[str, Any] | None = field(default=None, repr=False)
    tool_plans: Sequence[ToolCallPlan] = field(default_factory=tuple, repr=False)
    usage: Usage | None = None
    error_code: str | None = None
    remote_request_id: str | None = None
    # G3：仅 SUCCEEDED 且已获持久提交确认时携带；repr 不展示（内部直接访问）。
    payload_sha256: str | None = field(default=None, repr=False)
