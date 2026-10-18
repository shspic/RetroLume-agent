"""受控模型调用的唯一稳定入口。"""

from __future__ import annotations

import asyncio
import json
import logging
import math
import re
from dataclasses import replace
from typing import Any, Mapping
from uuid import uuid4

from .contracts import (
    AdmissionDenied,
    AdmissionIntent,
    AdmissionLedger,
    AdmissionPermit,
    AdmissionUnavailable,
    CallContext,
    CallStatus,
    LedgerDisposition,
    LedgerOutcome,
    ModelCallRequest,
    ModelCallResult,
    ModelServiceConfig,
    RecordOutcome,
    RejectingAdmissionLedger,
    ResponseMode,
    Usage,
    build_business_payload,
)
from app.learning.teaching_contracts import TeachingCallBinding, TeachingMemoryCallBinding,TeachingHybridCallBinding
from .tools import ToolRegistry, ToolValidationError
from .transport import DeliveryUnknown, HttpxModelTransport, ModelTransport, RequestNotSent, TransportResponse


# 本地脱敏诊断日志：只记稳定事件码、随机关联标识、阶段与异常类型，
# 不记录异常消息、traceback、局部变量、密钥、请求正文、资料或完整 ID。
_logger = logging.getLogger(__name__)


class ResponseValidationError(ValueError):
    def __init__(self, error_code: str):
        super().__init__(error_code)
        self.error_code = error_code


def _safe_json_loads(raw: bytes | str) -> Any:
    return json.loads(raw, parse_constant=lambda _: (_ for _ in ()).throw(ValueError("非有限数值")))


def _safe_remote_id(value: str | None) -> str | None:
    if value is None:
        return None
    if len(value) > 128 or re.fullmatch(r"[A-Za-z0-9._:-]+", value) is None:
        return None
    return value


def _validate_json_shape(value: Any, *, max_depth: int = 12, max_nodes: int = 2000) -> None:
    nodes = 0

    def visit(item: Any, depth: int) -> None:
        nonlocal nodes
        nodes += 1
        if nodes > max_nodes or depth > max_depth:
            raise ResponseValidationError("response_structure_limit")
        if isinstance(item, dict):
            if not all(isinstance(key, str) for key in item):
                raise ResponseValidationError("invalid_response_json")
            for child in item.values():
                visit(child, depth + 1)
        elif isinstance(item, list):
            for child in item:
                visit(child, depth + 1)
        elif item is not None:
            if not isinstance(item, (str, int, float, bool)):
                raise ResponseValidationError("invalid_response_json")
            if isinstance(item, float) and not math.isfinite(item):
                raise ResponseValidationError("invalid_response_json")

    visit(value, 0)


class ControlledModelGateway:
    def __init__(
        self,
        config: ModelServiceConfig,
        *,
        ledger: AdmissionLedger | None = None,
        transport: ModelTransport | None = None,
        tools: ToolRegistry | None = None,
    ) -> None:
        self._config = config
        self._ledger = ledger or RejectingAdmissionLedger()
        self._transport = transport or HttpxModelTransport()
        self._tools = tools or ToolRegistry()

    async def call(self, context: CallContext, request: ModelCallRequest) -> ModelCallResult:
        # 冻结原请求及服务端配置；await不能把已核正文换成新正文。
        original_request = request
        request = request.model_copy(deep=True)
        config = self._config.model_copy(deep=True)
        request_snapshot = json.dumps(request.model_dump(mode='json'),sort_keys=True,separators=(',',':'),allow_nan=False)
        config_snapshot = json.dumps(config.model_dump(mode='json'),sort_keys=True,separators=(',',':'),allow_nan=False)
        def original_scope_unchanged():
            return (json.dumps(original_request.model_dump(mode='json'),sort_keys=True,separators=(',',':'),allow_nan=False)==request_snapshot
                and json.dumps(self._config.model_dump(mode='json'),sort_keys=True,separators=(',',':'),allow_nan=False)==config_snapshot)
        if context.operation_id.startswith("html11m.") and request.html_profile is None:
            return self._result(context, CallStatus.REJECTED, "html_profile_required")
        if request.html_profile is not None:
            from app.preview.model_policy import validate_request
            code = await validate_request(context, request, self._ledger)
            if code is not None:
                return self._result(context, CallStatus.REJECTED, code)
        if request.learning_profile is None and request.teaching_profile is None \
                and context.operation_id.startswith(("learn-first-v1.", "learn-next-v1.")):
            return self._result(context, CallStatus.REJECTED, "invalid_learning_profile")
        if context.operation_id.startswith(("int10m.",'int18m.')) and request.interview_profile is None:
            return self._result(context, CallStatus.REJECTED, "interview_profile_required")
        if request.interview_profile is not None:
            from app.interview.policy import validate_request
            code = await validate_request(context, request, self._ledger)
            if code is not None:
                return self._result(context, CallStatus.REJECTED, code)
        if request.teaching_profile is not None:
            if request.learning_profile is not None or request.allowed_tools \
                    or not context.operation_id.startswith("teach8m."):
                return self._result(context, CallStatus.REJECTED, "invalid_teaching_profile")
            from app.learning.teaching_adapter import validate_teaching_request
            code = await validate_teaching_request(context, request, self._ledger)
            if code is not None:
                return self._result(context, CallStatus.REJECTED, code)
        if request.learning_profile is not None:
            from app.learning.adapter import validate_learning_request
            code = await validate_learning_request(context, request, self._ledger)
            if code is not None:
                return self._result(context, CallStatus.REJECTED, code)
        if request.input_result is not None and (
            request.input_result.activity_id != context.activity_id
            or request.input_result.operation_id == context.operation_id
            or request.allowed_tools
        ):
            return self._result(context, CallStatus.REJECTED, "invalid_input")
        if request.max_output_tokens > config.max_output_tokens_limit:
            return self._result(context, CallStatus.REJECTED, "output_token_limit")
        try:
            payload = self._build_payload(request, config=config)
            encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
        except (ToolValidationError, ValueError, TypeError):
            return self._result(context, CallStatus.REJECTED, "invalid_request")
        if len(encoded) > config.max_request_bytes:
            return self._result(context, CallStatus.REJECTED, "context_limit")

        approved_grant = None
        approved_manifest=None
        if getattr(self._transport, 'is_external', True) or config.outbound_grant is not None:
            from .embedding import OutboundGrant,OutboundSourceManifest
            if config.outbound_grant is None:
                return self._result(context, CallStatus.REJECTED, 'outbound_not_authorized')
            try:
                grant = OutboundGrant.from_wire(config.outbound_grant)
                grant.check(context.activity_id,config.provider.value,config.model,len(encoded),request.max_output_tokens)
                manifest=OutboundSourceManifest.from_wire(config.outbound_source_manifest)
                if manifest.sha256!=grant.source_manifest_sha256:raise AdmissionDenied('outbound_manifest_mismatch')
                if not original_scope_unchanged():raise AdmissionDenied('outbound_scope_changed')
                manifest.check_model(request,payload)
                approved_grant = grant.model_dump(mode='json')
                approved_manifest=manifest.model_dump(mode='json')
            except (ValueError,AdmissionDenied):
                return self._result(context,CallStatus.REJECTED,'outbound_conditions_unverified')

        intent = AdmissionIntent(
            context=context,
            provider=config.provider,
            configured_model=config.model,
            request_bytes=len(encoded),
            max_output_tokens=request.max_output_tokens,
            tool_names=tuple(sorted(request.allowed_tools)),
            input_result=request.input_result,
            teaching_binding=((TeachingHybridCallBinding if request.teaching_profile.profile=='teaching.v3' else TeachingMemoryCallBinding if request.teaching_profile.profile=='teaching.v2' else TeachingCallBinding)(
                command_key=request.teaching_profile.command_key,
                request_sha256=request.teaching_profile.request_sha256,
                context_sha256=request.teaching_profile.context_sha256,
                expected_revision=request.teaching_profile.expected_revision,
                goal_version=request.teaching_profile.goal_version,
                **({'memory_selection_sha256':request.teaching_profile.memory_selection_sha256,'assembled_messages_sha256':request.teaching_profile.assembled_messages_sha256} if request.teaching_profile.profile in ('teaching.v2','teaching.v3') else {}),
                **({'memory_dependency_sha256':request.teaching_profile.memory_dependency_sha256,'retrieval_ref':request.teaching_profile.retrieval_ref} if request.teaching_profile.profile=='teaching.v3' else {}),
            ) if request.teaching_profile is not None else None),
        )
        if request.interview_profile is not None:
            from app.interview.contracts import InterviewCallBinding,InterviewHybridCallBinding
            p=request.interview_profile
            intent=AdmissionIntent(context=intent.context,provider=intent.provider,configured_model=intent.configured_model,request_bytes=intent.request_bytes,
                max_output_tokens=intent.max_output_tokens,tool_names=intent.tool_names,interview_binding=(InterviewHybridCallBinding if p.schema_id=='interview.v2' else InterviewCallBinding)(
                    business_key=p.business_key,request_sha256=p.request_sha256,context_sha256=p.context_sha256,expected_head_revision=p.expected_head_revision,goal_version=p.goal_version,
                    **({'retrieval_ref':p.retrieval_ref,'memory_selection_sha256':p.memory_selection_sha256,'memory_dependency_sha256':p.memory_dependency_sha256} if p.schema_id=='interview.v2' else {})))
        if request.html_profile is not None:
            from app.preview.business_contracts import HtmlCallBinding
            from app.preview.description import load_json
            p = request.html_profile
            frozen = load_json(p.context_json)
            intent = AdmissionIntent(context=intent.context, provider=intent.provider, configured_model=intent.configured_model,
                request_bytes=intent.request_bytes, max_output_tokens=intent.max_output_tokens, tool_names=intent.tool_names,
                html_binding=HtmlCallBinding(business_key=p.business_key, request_sha256=p.request_sha256,
                    context_sha256=p.context_sha256, renderer_sha256=p.renderer_sha256,
                    memory_selection_sha256=frozen.get("memory_selection_sha256")))
        intent = replace(intent,retrieval_ref=request.retrieval_ref,outbound_grant=approved_grant,outbound_source_manifest=approved_manifest)
        approved_wire = json.dumps([approved_grant,approved_manifest],sort_keys=True,separators=(',',':'))
        def check_approved_scope():
            if approved_grant is None:return
            if not original_scope_unchanged() or json.dumps([intent.outbound_grant,intent.outbound_source_manifest],sort_keys=True,separators=(',',':'))!=approved_wire:
                raise AdmissionDenied('outbound_scope_changed')
            grant.check(context.activity_id,config.provider.value,config.model,len(encoded),request.max_output_tokens)
            manifest.check_model(request,json.loads(encoded))
        stage = "admit"
        try:
            check_approved_scope()
            permit = await self._ledger.admit(intent)
            stage = "permit_check"
            self._validate_permit(permit, context)
            stage = "mark_dispatch"
            check_approved_scope()
            if request.retrieval_ref is not None:await self._ledger.mark_dispatch_started(permit,retrieval_ref=request.retrieval_ref)
            else:await self._ledger.mark_dispatch_started(permit)
            stage = "dispatch_scope_check"
            check_approved_scope()
        except AdmissionDenied as exc:
            code = str(exc)
            if stage=="dispatch_scope_check":
                # 已预扣/登记dispatch但尚未调用transport，明确未发送且不退款。
                return await self._finish(permit,context,LedgerOutcome(LedgerDisposition.NOT_SENT,error_code='outbound_scope_changed'),CallStatus.NOT_SENT)
            if not code.startswith("interview_") and code not in {"scope_conflict","source_invalid","result_invalidated","cancelled","budget_exhausted","integrity_error","invalid_input","outbound_scope_changed"}:
                code = "admission_denied"
            return self._result(context, CallStatus.REJECTED, code)
        except AdmissionUnavailable:
            return self._result(context, CallStatus.REJECTED, "admission_unavailable")
        except Exception as exc:
            # 意外异常：稳定独立错误码，保持 REJECTED 且不发送；保守账本语义不变
            #（已预留不退款、不重发、不假记业务成功）。
            _logger.warning(
                "admission_internal_error stage=%s correlation_id=%s exception_type=%s",
                stage,
                uuid4().hex,
                type(exc).__name__,
            )
            return self._result(context, CallStatus.REJECTED, "admission_internal_error")

        try:
            async with asyncio.timeout(config.timeout_seconds):
                response = await self._transport.send(
                    endpoint=f"{config.base_url}/chat/completions",
                    api_key=config.api_key.get_secret_value(),
                    payload=json.loads(encoded),
                    timeout_seconds=config.timeout_seconds,
                    max_response_bytes=config.max_response_bytes,
                )
        except RequestNotSent:
            outcome = LedgerOutcome(LedgerDisposition.NOT_SENT, error_code="request_not_sent")
            return await self._finish(permit, context, outcome, CallStatus.NOT_SENT)
        except asyncio.CancelledError:
            await self._record_unknown_best_effort(permit, "cancelled")
            raise
        except TimeoutError:
            outcome = LedgerOutcome(LedgerDisposition.UNKNOWN, error_code="deadline_exceeded")
            return await self._finish(permit, context, outcome, CallStatus.UNKNOWN)
        except DeliveryUnknown:
            outcome = LedgerOutcome(LedgerDisposition.UNKNOWN, error_code="delivery_unknown")
            return await self._finish(permit, context, outcome, CallStatus.UNKNOWN)
        except Exception:
            outcome = LedgerOutcome(LedgerDisposition.UNKNOWN, error_code="transport_unknown")
            return await self._finish(permit, context, outcome, CallStatus.UNKNOWN)

        return await self._handle_response(permit, context, request, response)

    def _build_payload(self, request: ModelCallRequest, *, config: ModelServiceConfig | None = None) -> dict[str, Any]:
        config = config or self._config
        self._validate_conversation(request)
        payload: dict[str, Any] = {
            "model": config.model,
            "messages": [message.model_dump(exclude_none=True) for message in request.messages],
            "max_tokens": request.max_output_tokens,
            "stream": False,
            "thinking": {"type": config.thinking.value},
        }
        if request.response_mode == ResponseMode.JSON_OBJECT:
            payload["response_format"] = {"type": "json_object"}
        schemas = self._tools.schemas_for(request.allowed_tools)
        if schemas:
            payload["tools"] = schemas
            payload["tool_choice"] = "auto"
        return payload

    def _validate_conversation(self, request: ModelCallRequest) -> None:
        pending: set[str] = set()
        seen: set[str] = set()
        for message in request.messages:
            if pending and message.role != "tool":
                raise ToolValidationError("assistant 工具调用后缺少对应工具结果")
            if message.role == "assistant" and message.tool_calls:
                for call in message.tool_calls:
                    if call.id in seen:
                        raise ToolValidationError("工具调用 ID 重复")
                    self._tools.plan(
                        call.id,
                        call.function.name,
                        call.function.arguments,
                        request.allowed_tools,
                    )
                    seen.add(call.id)
                    pending.add(call.id)
            elif message.role == "tool":
                if message.tool_call_id not in pending:
                    raise ToolValidationError("工具结果没有对应的 assistant 工具调用")
                pending.remove(message.tool_call_id)
        if pending:
            raise ToolValidationError("assistant 工具调用后缺少对应工具结果")

    @staticmethod
    def _validate_permit(permit: AdmissionPermit, context: CallContext) -> None:
        if (
            not isinstance(permit, AdmissionPermit)
            or not permit.admission_id
            or permit.operation_id != context.operation_id
            or permit.executor_id != context.executor_id
        ):
            raise AdmissionUnavailable("账本返回的受理凭证与调用不匹配")

    async def _handle_response(
        self,
        permit: AdmissionPermit,
        context: CallContext,
        request: ModelCallRequest,
        response: TransportResponse,
    ) -> ModelCallResult:
        remote_request_id = _safe_remote_id(response.remote_request_id)
        if response.body_too_large:
            outcome = LedgerOutcome(
                LedgerDisposition.RECEIVED,
                error_code="response_too_large",
                remote_request_id=remote_request_id,
                response_bytes=response.response_bytes,
            )
            return await self._finish(permit, context, outcome, CallStatus.FAILED)
        if response.status_code < 200 or response.status_code >= 300:
            outcome = LedgerOutcome(
                LedgerDisposition.RECEIVED,
                error_code=f"remote_http_{response.status_code}",
                remote_request_id=remote_request_id,
                response_bytes=response.response_bytes,
            )
            return await self._finish(permit, context, outcome, CallStatus.FAILED)

        try:
            parsed, result = self._parse_success(context, request, response, remote_request_id)
        except ResponseValidationError as exc:
            outcome = LedgerOutcome(
                LedgerDisposition.RECEIVED,
                error_code=exc.error_code,
                remote_request_id=remote_request_id,
                response_bytes=response.response_bytes,
            )
            return await self._finish(permit, context, outcome, CallStatus.FAILED)

        payload_format: str | None = None
        payload: str | None = None
        payload_sha256: str | None = None
        if result.status is CallStatus.SUCCEEDED:
            try:
                payload_format, payload, payload_sha256 = build_business_payload(
                    text=result.text, json_object=result.json_object
                )
            except (ValueError, TypeError, RecursionError) as exc:
                # 封套先拒后写：超限/非法正文转为 received 失败，不持久化正文。
                error_code = "payload_limit" if str(exc) == "payload_limit" else "invalid_payload"
                outcome = LedgerOutcome(
                    LedgerDisposition.RECEIVED,
                    error_code=error_code,
                    remote_request_id=remote_request_id,
                    response_bytes=response.response_bytes,
                )
                return await self._finish(permit, context, outcome, CallStatus.FAILED)

        outcome = LedgerOutcome(
            LedgerDisposition.RECEIVED,
            remote_request_id=remote_request_id,
            returned_model=result.returned_model,
            finish_reason=result.finish_reason,
            prompt_tokens=result.usage.prompt_tokens if result.usage else None,
            completion_tokens=result.usage.completion_tokens if result.usage else None,
            response_bytes=response.response_bytes,
            payload_format=payload_format,
            payload=payload,
            payload_sha256=payload_sha256,
        )
        final = await self._finish(permit, context, outcome, result.status, result=result)
        if final.status is CallStatus.UNKNOWN:
            return final
        del parsed
        return final

    def _parse_success(
        self,
        context: CallContext,
        request: ModelCallRequest,
        response: TransportResponse,
        remote_request_id: str | None,
    ) -> tuple[Mapping[str, Any], ModelCallResult]:
        try:
            data = _safe_json_loads(response.body)
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError, RecursionError) as exc:
            raise ResponseValidationError("invalid_response_json") from exc
        if not isinstance(data, dict):
            raise ResponseValidationError("invalid_response_shape")
        choices = data.get("choices")
        returned_model = data.get("model")
        usage_raw = data.get("usage")
        if (
            not isinstance(returned_model, str)
            or re.fullmatch(r"[A-Za-z0-9._:/-]{1,128}", returned_model) is None
        ):
            raise ResponseValidationError("invalid_response_shape")
        if not isinstance(choices, list) or len(choices) != 1 or not isinstance(choices[0], dict):
            raise ResponseValidationError("invalid_response_shape")
        if not isinstance(usage_raw, dict):
            raise ResponseValidationError("invalid_usage")
        try:
            prompt_tokens = usage_raw["prompt_tokens"]
            completion_tokens = usage_raw["completion_tokens"]
            total_tokens = usage_raw["total_tokens"]
        except KeyError as exc:
            raise ResponseValidationError("invalid_usage") from exc
        if any(isinstance(item, bool) or not isinstance(item, int) or item < 0 for item in (prompt_tokens, completion_tokens, total_tokens)):
            raise ResponseValidationError("invalid_usage")
        if total_tokens < prompt_tokens + completion_tokens:
            raise ResponseValidationError("invalid_usage")
        usage = Usage(prompt_tokens, completion_tokens, total_tokens)

        choice = choices[0]
        finish_reason = choice.get("finish_reason")
        message = choice.get("message")
        if not isinstance(finish_reason, str) or not isinstance(message, dict) or message.get("role") != "assistant":
            raise ResponseValidationError("invalid_response_shape")
        if finish_reason == "length":
            raise ResponseValidationError("truncated_output")
        if finish_reason in {"content_filter", "insufficient_system_resource"}:
            raise ResponseValidationError(f"finish_{finish_reason}")
        if finish_reason == "tool_calls":
            tool_calls = message.get("tool_calls")
            if not isinstance(tool_calls, list) or not 1 <= len(tool_calls) <= 8:
                raise ResponseValidationError("invalid_tool_calls")
            plans = []
            try:
                for item in tool_calls:
                    function = item.get("function") if isinstance(item, dict) else None
                    if not isinstance(function, dict) or item.get("type") != "function":
                        raise ToolValidationError("工具调用结构非法")
                    plans.append(
                        self._tools.plan(
                            item.get("id"),
                            function.get("name"),
                            function.get("arguments"),
                            request.allowed_tools,
                        )
                    )
            except ToolValidationError as exc:
                raise ResponseValidationError("invalid_tool_calls") from exc
            return data, self._result(
                context,
                CallStatus.TOOL_PLAN,
                returned_model=returned_model,
                finish_reason=finish_reason,
                tool_plans=tuple(plans),
                usage=usage,
                remote_request_id=remote_request_id,
            )
        if finish_reason != "stop":
            raise ResponseValidationError("unknown_finish_reason")

        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise ResponseValidationError("empty_output")
        if request.response_mode == ResponseMode.JSON_OBJECT:
            try:
                value = _safe_json_loads(content)
            except (json.JSONDecodeError, ValueError, RecursionError) as exc:
                raise ResponseValidationError("invalid_output_json") from exc
            if not isinstance(value, dict):
                raise ResponseValidationError("invalid_output_json")
            _validate_json_shape(value, max_depth=64 if request.html_profile is not None else 12,
                                 max_nodes=5000 if request.html_profile is not None else 2000)
            if request.html_profile is not None:
                from app.preview.model_policy import stored_result
                try:
                    if completion_tokens > request.max_output_tokens:
                        raise ValueError("invalid_interactive_output")
                    value = stored_result(content, request.html_profile)
                except (ValueError, TypeError, KeyError, RecursionError, UnicodeError):
                    raise ResponseValidationError("invalid_interactive_output") from None
            elif request.interview_profile is not None:
                from app.interview.policy import stored_result
                try:
                    if completion_tokens > request.max_output_tokens: raise ValueError("invalid_interview_output")
                    value=stored_result(content,request.interview_profile,request.messages)
                except (ValueError,TypeError,KeyError,RecursionError):
                    raise ResponseValidationError("invalid_interview_output") from None
            elif request.learning_profile is not None:
                from app.learning.contracts import normalize_result, parse_output
                try:
                    if completion_tokens > request.max_output_tokens:
                        raise ValueError("learning_output_limit")
                    value = normalize_result(request.learning_profile, parse_output(content))
                except (ValueError, TypeError, RecursionError):
                    raise ResponseValidationError("invalid_learning_output") from None
            elif request.teaching_profile is not None:
                from app.learning.teaching_policy import normalize_output_for_action
                try:
                    if completion_tokens > request.max_output_tokens:
                        raise ValueError("teaching_output_limit")
                    from app.learning.teaching_contracts import stored_teaching_result
                    value = stored_teaching_result(request.teaching_profile,
                        normalize_output_for_action(content, request.teaching_profile.action), request.messages)
                except (ValueError, TypeError, RecursionError):
                    raise ResponseValidationError("invalid_teaching_output") from None
            return data, self._result(
                context,
                CallStatus.SUCCEEDED,
                returned_model=returned_model,
                finish_reason=finish_reason,
                json_object=value,
                usage=usage,
                remote_request_id=remote_request_id,
            )
        return data, self._result(
            context,
            CallStatus.SUCCEEDED,
            returned_model=returned_model,
            finish_reason=finish_reason,
            text=content,
            usage=usage,
            remote_request_id=remote_request_id,
        )

    async def _finish(
        self,
        permit: AdmissionPermit,
        context: CallContext,
        outcome: LedgerOutcome,
        status: CallStatus,
        *,
        result: ModelCallResult | None = None,
    ) -> ModelCallResult:
        """记账并按提交确认三分类映射最终状态。

        AdmissionDenied → 本次未获确认：UNKNOWN + record_denied，不否认既有正文；
        其他异常（含 AdmissionUnavailable 与意外异常）或返回非法枚举/None →
        提交结果未确认：UNKNOWN + record_unconfirmed。两处 UNKNOWN 都不否定
        同键历史持久正文；恢复由 record 幂等与只读接口承担，不重发、不补写。
        SUCCEEDED 仅在合法正文获 RECORDED/ALREADY_PRESENT 确认后返回，实际
        返回对象携带 payload_sha256；TOOL_PLAN 不持久化业务正文、不自动执行。
        """
        try:
            confirmation = await self._ledger.record_outcome(permit, outcome)
        except AdmissionDenied:
            return self._result(context, CallStatus.UNKNOWN, "record_denied")
        except Exception:
            return self._result(context, CallStatus.UNKNOWN, "record_unconfirmed")
        if not isinstance(confirmation, RecordOutcome):
            return self._result(context, CallStatus.UNKNOWN, "record_unconfirmed")
        if result is not None:
            if result.status is CallStatus.SUCCEEDED:
                if not isinstance(outcome.payload_sha256, str):
                    return self._result(context, CallStatus.UNKNOWN, "record_unconfirmed")
                return replace(result, payload_sha256=outcome.payload_sha256)
            return result
        return self._result(
            context,
            status,
            outcome.error_code,
            returned_model=outcome.returned_model,
            finish_reason=outcome.finish_reason,
            remote_request_id=outcome.remote_request_id,
        )

    async def _record_unknown_best_effort(self, permit: AdmissionPermit, error_code: str) -> None:
        try:
            await self._ledger.record_outcome(
                permit,
                LedgerOutcome(LedgerDisposition.UNKNOWN, error_code=error_code),
            )
        except Exception:
            pass

    def _result(
        self,
        context: CallContext,
        status: CallStatus,
        error_code: str | None = None,
        **values: Any,
    ) -> ModelCallResult:
        return ModelCallResult(
            status=status,
            operation_id=context.operation_id,
            provider=self._config.provider,
            configured_model=self._config.model,
            error_code=error_code,
            **values,
        )
