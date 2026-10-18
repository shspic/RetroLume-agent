"""G6 本地活动与模型配置加载（能力分层 L0/L1/L2，失败关闭）。

- L0 读取与取消：仅需存储就绪，不需要本配置；
- L1 新建：需要有效的模型标识段与活动额度段（不含密钥）；
- L2 显式继续：在 L1 之上还需要可用密钥与完整 ModelServiceConfig。

配置文件不含密钥；密钥只经环境变量（变量名在配置中声明）注入，值不进
文件、不进响应、不进日志。任何缺项或非法值按层失败关闭并给出精确原因
（config_missing/config_invalid/config_incompatible/provider_key_not_configured）。
示例模板的占位值不能通过校验，直接复制示例不产生可用能力。加载只发生在
应用启动时；变更配置需要重启，不做热加载。
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, SecretStr, ValidationError, field_validator

from app.activities import ActivitySpec, PostgresAdmissionLedger, SourceSnapshot
from app.capabilities.contracts import (
    ModelCallRequest,
    ModelServiceConfig,
    Provider,
    ThinkingMode,
)
from app.worker.one_call import OneCallInput

_SERVICE_REQUEST_TIMEOUT = 10.0  # 与 SessionConfig 默认 request_timeout_seconds 一致
_ONECALL_CONFIGURED_BODY_LIMIT = 65_536  # one_call 受控通道配置字节上限
_MAX_CONTINUE_OUTPUT_TOKENS = 256  # continue_from_result 使用的固定输出预算


@dataclass(frozen=True)
class LayerState:
    available: bool
    reason: str | None = None


@dataclass(frozen=True)
class ActivityConfig:
    provider: str | None
    model: str | None
    quota_preview: dict | None
    model_service: ModelServiceConfig | None
    create_layer: LayerState
    continue_layer: LayerState
    learning_layer: LayerState = LayerState(False, "learning_not_configured")
    learning_output_tokens: int | None = None
    # G8 教学层（TASK-100）：独立 teaching.v1 输出 1..2048，默认关闭。
    teaching_layer: LayerState = LayerState(False, "teaching_not_configured")
    teaching_output_tokens: int | None = None
    teaching_calculation_layer: LayerState = LayerState(False, "teaching_not_configured")


class _ModelIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    provider: str = Field(min_length=1, max_length=64)
    model: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:/-]+$")


class _ActivityDefaults(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    deadline_hours: int = Field(ge=1, le=720)
    max_requests: int = Field(ge=1, le=2_147_483_647)
    max_cost_microunits: int = Field(ge=1, le=9_223_372_036_854_775_807)
    reserve_cost_microunits: int = Field(ge=1, le=9_223_372_036_854_775_807)
    max_request_bytes: int = Field(ge=1024, le=_ONECALL_CONFIGURED_BODY_LIMIT)
    max_output_tokens: int = Field(ge=1, le=32_768)
    max_running_seconds: int = Field(ge=1, le=2_147_483_647)
    allowed_tools: list[str] = Field(max_length=1)
    max_tool_calls: int | None = Field(default=None, ge=0, le=32)

    @field_validator("allowed_tools")
    @classmethod
    def _tool_whitelist(cls, value):
        # G8 薄扩展：仅容许显式 finite_calculate 白名单（教学核算）；
        # 普通模型及全部教学模型请求依然 allowed_tools 为空。
        for name in value:
            if name != "finite_calculate":
                raise ValueError("allowed_tools 仅允许 finite_calculate")
        return value

    def reserve_within_limit(self) -> bool:
        return self.reserve_cost_microunits <= self.max_cost_microunits


class _ServiceSection(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    base_url: str = Field(min_length=1, max_length=256)
    thinking: str
    timeout_seconds: float = Field(gt=0, le=120)
    max_output_tokens_limit: int = Field(ge=1, le=32_768)
    max_request_bytes: int = Field(ge=1024, le=2_097_152)
    max_response_bytes: int = Field(ge=1024, le=4_194_304)

    @field_validator("timeout_seconds", mode="before")
    @classmethod
    def _plain_number(cls, value):
        if type(value) is bool or type(value) not in (int, float):
            raise ValueError("timeout_seconds 必须是显式数字")
        return float(value)


class _LearningSection(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    profile: str = Field(pattern=r"^learning\.v1$")
    max_output_tokens: int = Field(ge=1, le=256)


def _learning_check(data, defaults, cont, service):
    if "learning" not in data:
        return LayerState(False, "learning_not_configured"), None
    try:
        section = _LearningSection.model_validate(data["learning"])
    except ValidationError:
        return LayerState(False, "learning_config_invalid"), None
    if not cont.available or service is None:
        return LayerState(False, cont.reason), None
    if section.max_output_tokens > min(defaults.max_output_tokens, service.max_output_tokens_limit):
        return LayerState(False, "learning_config_incompatible"), None
    return LayerState(True), section.max_output_tokens


class _TeachingSection(BaseModel):
    """G8 教学配置段：{profile, max_output_tokens, enable_calculation}。"""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    profile: str = Field(pattern=r"^teaching\.v1$")
    max_output_tokens: int = Field(ge=1, le=2048)
    enable_calculation: bool = False

    @field_validator("enable_calculation", mode="before")
    @classmethod
    def _strict_bool(cls, value):
        if type(value) is not bool:
            raise ValueError("enable_calculation 必须是显式布尔")
        return value


def _teaching_check(data, defaults, cont, service):
    """教学层校验：缺段默认关闭；模型动作需要 L2；核算需显式白名单与额度。

    旧 learning.v1 仍 1..256；teaching 独立 1..2048。核算启用还需
    activity_defaults 显式 allowed_tools=['finite_calculate'] 与
    max_tool_calls 0..32；旧 None/0 配置仍拒工具，不静默加额度。
    """
    if "teaching" not in data:
        return LayerState(False, "teaching_not_configured"), None, LayerState(False, "teaching_not_configured")
    try:
        section = _TeachingSection.model_validate(data["teaching"])
    except ValidationError:
        return LayerState(False, "teaching_config_invalid"), None, LayerState(False, "teaching_config_invalid")
    if not cont.available or service is None:
        return LayerState(False, cont.reason), None, LayerState(False, "teaching_not_configured")
    if section.max_output_tokens > min(defaults.max_output_tokens, service.max_output_tokens_limit):
        return LayerState(False, "teaching_config_incompatible"), None, LayerState(False, "teaching_not_configured")
    calculation = LayerState(False, "teaching_not_configured")
    if section.enable_calculation:
        if list(defaults.allowed_tools) != ["finite_calculate"] or not (
                isinstance(defaults.max_tool_calls, int) and 0 <= defaults.max_tool_calls <= 32):
            calculation = LayerState(False, "tool_limit_unconfigured")
        else:
            calculation = LayerState(True)
    return LayerState(True), section.max_output_tokens, calculation


def _unavailable(reason: str) -> ActivityConfig:
    return ActivityConfig(
        None, None, None, None, LayerState(False, reason), LayerState(False, reason),
    )


def _preview(defaults: _ActivityDefaults) -> dict:
    return {
        "deadline_hours": defaults.deadline_hours,
        "max_requests": defaults.max_requests,
        "max_cost_microunits": defaults.max_cost_microunits,
        "reserve_cost_microunits": defaults.reserve_cost_microunits,
        "max_request_bytes": defaults.max_request_bytes,
        "max_output_tokens": defaults.max_output_tokens,
        "max_running_seconds": defaults.max_running_seconds,
        "allowed_tools": list(defaults.allowed_tools),
        "max_tool_calls": defaults.max_tool_calls,
    }


def _l1_dry_run(provider: Provider, model: str, defaults: _ActivityDefaults) -> str | None:
    """用既有 ActivitySpec 校验器做一次纯内存演练；失败给出精确原因。"""
    if not defaults.reserve_within_limit():
        return "config_invalid"
    spec = ActivitySpec(
        activity_id=str(uuid4()),
        sources=(SourceSnapshot(str(uuid4()), str(uuid4()), 0),),
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=defaults.deadline_hours),
        max_requests=defaults.max_requests,
        max_cost_microunits=defaults.max_cost_microunits,
        reserve_cost_microunits=defaults.reserve_cost_microunits,
        max_request_bytes=defaults.max_request_bytes,
        max_output_tokens=defaults.max_output_tokens,
        max_running_seconds=defaults.max_running_seconds,
        allowed_models=((str(provider), model),),
        allowed_tools=tuple(defaults.allowed_tools),
        max_tool_calls=defaults.max_tool_calls,
    )
    try:
        PostgresAdmissionLedger._validate_spec(spec)
    except (ValueError, TypeError):
        return "config_invalid"
    return None


def _l2_check(
    data: dict, provider: Provider, model: str, defaults: _ActivityDefaults,
) -> tuple[LayerState, ModelServiceConfig | None]:
    section = data.get("service")
    if section is None:
        return LayerState(False, "config_invalid"), None
    try:
        service = _ServiceSection.model_validate(section)
    except ValidationError:
        return LayerState(False, "config_invalid"), None
    api_key_env = data.get("api_key_env")
    if type(api_key_env) is not str or not api_key_env:
        return LayerState(False, "config_invalid"), None
    key = os.environ.get(api_key_env, "").strip()
    if not key:
        return LayerState(False, "provider_key_not_configured"), None
    if service.thinking != ThinkingMode.DISABLED.value:
        return LayerState(False, "config_incompatible"), None
    if service.timeout_seconds > _SERVICE_REQUEST_TIMEOUT:
        return LayerState(False, "config_incompatible"), None
    if max(service.max_request_bytes, service.max_response_bytes) > _ONECALL_CONFIGURED_BODY_LIMIT:
        return LayerState(False, "config_incompatible"), None
    if min(_MAX_CONTINUE_OUTPUT_TOKENS, service.max_output_tokens_limit) > defaults.max_output_tokens:
        return LayerState(False, "config_incompatible"), None
    try:
        config = ModelServiceConfig(
            provider=provider,
            base_url=service.base_url,
            model=model,
            api_key=SecretStr(key),
            thinking=ThinkingMode(service.thinking),
            timeout_seconds=service.timeout_seconds,
            max_output_tokens_limit=service.max_output_tokens_limit,
            max_request_bytes=service.max_request_bytes,
            max_response_bytes=service.max_response_bytes,
        )
    except (ValidationError, ValueError):
        return LayerState(False, "config_invalid"), None
    # 可确定的序列化前置校验：完整构造并走一次 OneCallInput 线格式检查。
    try:
        OneCallInput(
            "config-probe",
            ModelCallRequest(messages=({"role": "user", "content": "probe"},), max_output_tokens=1),
            config,
        ).to_wire()
    except Exception:
        return LayerState(False, "config_incompatible"), None
    return LayerState(True), config


def load_activity_config(path: Path) -> ActivityConfig:
    """读取一次本地私有配置；任何失败都按 L1/L2 分层失败关闭，不抛出。"""
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return _unavailable("config_missing")
    except (OSError, UnicodeDecodeError):
        return _unavailable("config_invalid")
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, RecursionError):
        return _unavailable("config_invalid")
    if type(data) is not dict:
        return _unavailable("config_invalid")

    identity_raw, defaults_raw = data.get("model_identity"), data.get("activity_defaults")
    if identity_raw is None or defaults_raw is None:
        return _unavailable("config_missing")
    try:
        identity = _ModelIdentity.model_validate(identity_raw)
        defaults = _ActivityDefaults.model_validate(defaults_raw)
        provider = Provider(identity.provider)
    except (ValidationError, ValueError):
        return _unavailable("config_invalid")
    l1_reason = _l1_dry_run(provider, identity.model, defaults)
    if l1_reason is not None:
        return _unavailable(l1_reason)

    create_layer = LayerState(True)
    continue_layer, model_service = _l2_check(data, provider, identity.model, defaults)
    learning_layer, learning_tokens = _learning_check(data, defaults, continue_layer, model_service)
    teaching_layer, teaching_tokens, calculation_layer = _teaching_check(data, defaults, continue_layer, model_service)
    return ActivityConfig(
        provider=str(provider),
        model=identity.model,
        quota_preview=_preview(defaults),
        model_service=model_service,
        create_layer=create_layer,
        continue_layer=continue_layer,
        learning_layer=learning_layer,
        learning_output_tokens=learning_tokens,
        teaching_layer=teaching_layer,
        teaching_output_tokens=teaching_tokens,
        teaching_calculation_layer=calculation_layer,
    )
