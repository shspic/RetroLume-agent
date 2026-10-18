"""G6 活动工作区只读面与三类受控动作（TASK-095）。

只读读取每次恰一条 SQL 快照（状态判定与 read_committed_result 同源）；
新建/取消/显式继续遵循既有仓储与监督链，浏览器只提供业务键与文本，
不提供 DSN、密钥、provider、额度、executor、G 或 scope 授权值。
"""
from __future__ import annotations

import base64
import json
import re
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

from app.capabilities.contracts import AdmissionUnavailable
from app.local_session import local_session
from app.service_config import ActivityConfig
from app.worker.session import SessionConfig

from .repository import (
    ActivityFactView,
    ActivityLedgerConflict,
    ActivitySpec,
    OperationRow,
    PostgresAdmissionLedger,
    ResultIntegrityError,
    SourceSnapshot,
)
from .service import ActivityService

router = APIRouter(prefix="/api")

_ID_RE = re.compile(r"[A-Za-z0-9._:/-]{1,128}\Z")
_ACTIVITY_LIMIT_DEFAULT, _ACTIVITY_LIMIT_MAX = 20, 50
_OPERATION_LIMIT_DEFAULT, _OPERATION_LIMIT_MAX = 20, 100
_FOLLOWUP_MAX_CHARS = 4096
_EXECUTOR_ID = "local-ui"


from app.memory.contracts import MemorySelectionInput, MemoryRefusal, read_bounded_json


class CreateActivityInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    activity_id: str
    source_ids: list[str] = Field(min_length=1, max_length=128)
    memory_selection: MemorySelectionInput | None = None


class ContinueInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    parent_operation_id: str
    new_operation_id: str
    followup: str


def _error(status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code, detail={"code": code, "message": message})


def _uuid_text(value: str, field: str) -> str:
    try:
        return str(UUID(value))
    except (ValueError, TypeError, AttributeError):
        raise _error(400, "invalid_input", f"{field} 必须是 UUID") from None


def _ledger(request: Request) -> PostgresAdmissionLedger:
    ledger = getattr(request.app.state, "activities_ledger", None)
    if ledger is None:
        raise _error(503, "database_not_configured", "本地活动存储尚未配置")
    return ledger


def _config(request: Request) -> ActivityConfig:
    config = getattr(request.app.state, "activity_config", None)
    if config is None:
        raise _error(503, "config_unavailable", "活动配置尚未加载")
    return config


def _guard(request: Request) -> None:
    local_session(request, allow_own_origin=True)


def _iso(value: datetime | None) -> str | None:
    return None if value is None else value.isoformat()


def _fact_payload(fact: ActivityFactView, *, detail: bool) -> dict:
    data = {
        "activity_id": fact.activity_id,
        "status": fact.status,
        **({"memory_selection":fact.memory_selection} if fact.memory_selection is not None else {}),
        "created_at": _iso(fact.created_at),
        "updated_at": _iso(fact.updated_at),
        "deadline_at": _iso(fact.deadline_at),
        "cancelled_at": _iso(fact.cancelled_at),
        "scope_revision": fact.scope_revision,
        "max_requests": fact.max_requests,
        "requests_reserved": fact.requests_reserved,
        "max_cost_microunits": fact.max_cost_microunits,
        "cost_reserved_microunits": fact.cost_reserved_microunits,
        "reserve_cost_microunits": fact.reserve_cost_microunits,
        "max_running_seconds": fact.max_running_seconds,
        "running_reserved_seconds": fact.running_reserved_seconds,
        "running_settled_seconds": fact.running_settled_seconds,
        "max_tool_calls": fact.max_tool_calls,
        "tools_reserved": fact.tools_reserved,
        "source_count": len(fact.sources),
        "source_titles": [item.title for item in fact.sources[:2]],
    }
    if detail:
        data["last_settled_generation"] = fact.last_settled_generation
        data["last_settled_seconds"] = fact.last_settled_seconds
        data["allowed_models"] = [
            {"provider": provider, "model": model} for provider, model in fact.allowed_models
        ]
        data["sources"] = [
            {"source_id": item.source_id, "title": item.title, "valid": item.valid}
            for item in fact.sources
        ]
    return data


def _operation_payload(row: OperationRow, *, include_payload: bool) -> dict:
    data = {
        "operation_id": row.operation_id,
        "kind": row.kind,
        "state": row.state,
        "disposition": row.disposition,
        "error_code": row.error_code,
        "reserved_at": _iso(row.reserved_at),
        "dispatch_started_at": _iso(row.dispatch_started_at),
        "recorded_at": _iso(row.recorded_at),
        "prompt_tokens": row.prompt_tokens,
        "completion_tokens": row.completion_tokens,
        "finish_reason": row.finish_reason,
        "returned_model": row.returned_model,
        "committed_at": _iso(row.committed_at),
        "read_status": row.read_status.value,
        "payload_available": row.payload_available,
        "payload": None,
    }
    if row.operation_id.startswith(("teach8m.", "teach8t.")):
        # G8：通用 operation GET 对教学操作只给元数据，不泄露未暴露参考答案；
        # 正文读取走教学专用 workspace/records 端点。
        return data
    if include_payload and row.payload is not None:
        envelope = json.loads(row.payload)
        data["payload"] = {"format": envelope["format"], "value": envelope["value"]}
    return data


def _encode_cursor(fact: ActivityFactView) -> str:
    raw = json.dumps({"t": fact.created_at.isoformat(), "i": fact.activity_id}).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii")


def _decode_cursor(value: str) -> tuple[datetime, str]:
    try:
        data = json.loads(base64.urlsafe_b64decode(value.encode("ascii")).decode("utf-8"))
        created = datetime.fromisoformat(data["t"])
        if created.tzinfo is None or str(UUID(data["i"])) != data["i"]:
            raise ValueError
    except (ValueError, KeyError, TypeError, UnicodeDecodeError, json.JSONDecodeError):
        raise _error(400, "invalid_cursor", "游标无效，请刷新后重试") from None
    return created, data["i"]


def _bounded_limit(value: int | None, *, default: int, maximum: int, field: str) -> int:
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= maximum:
        raise _error(400, "invalid_input", f"{field} 必须在 1 到 {maximum} 之间")
    return value


def _map_read_error(exc: Exception) -> HTTPException:
    if isinstance(exc, ResultIntegrityError):
        return _error(409, "integrity_error", "活动数据完整性检查失败，未返回可能不可信的内容")
    if isinstance(exc, ActivityLedgerConflict):
        return _error(404 if "不存在" in str(exc) else 409, "ledger_conflict", "活动状态已变化，请刷新后重试")
    if isinstance(exc, ValueError):
        return _error(400, "invalid_input", "请求参数无效")
    return _error(503, "unavailable", "活动数据暂不可用，请稍后重试")


@router.get("/activities/capabilities")
async def capabilities(request: Request):
    _guard(request)
    config = _config(request)
    ledger = getattr(request.app.state, "activities_ledger", None)
    storage_ready = False
    storage_reason: str | None = "database_not_configured"
    if ledger is not None:
        try:
            storage_ready = await ActivityService(ledger).probe_storage()
            storage_reason = None if storage_ready else "storage_not_ready"
        except AdmissionUnavailable:
            storage_reason = "database_unavailable"
    create = config.create_layer
    cont = config.continue_layer
    learning = config.learning_layer
    teaching = getattr(config, "teaching_layer", None)
    calculation = getattr(config, "teaching_calculation_layer", None)
    create_state = {
        "available": bool(storage_ready and create.available),
        "reason": create.reason if not create.available else (None if storage_ready else storage_reason),
    }
    continue_state = {
        "available": bool(storage_ready and cont.available),
        "reason": cont.reason if not cont.available else (None if storage_ready else storage_reason),
    }
    provider_info = None
    if config.provider is not None and config.model is not None:
        provider_info = {"provider": config.provider, "model": config.model}
    return {
        "storage_ready": storage_ready,
        "storage_reason": storage_reason,
        "create": create_state,
        "continue": continue_state,
        "learning": {
            "available": bool(storage_ready and learning.available),
            "reason": learning.reason if not learning.available else (None if storage_ready else storage_reason),
            "mode": "terms.v1",
            "max_input_chars": 1024,
            "max_input_bytes": 4096,
            "max_sources": 10,
            "top_k": 8,
            "max_output_tokens": config.learning_output_tokens,
        },
        "teaching": {
            "available": bool(storage_ready and teaching is not None and teaching.available),
            "reason": (teaching.reason if teaching is not None and not teaching.available
                       else (None if storage_ready else storage_reason)) or "teaching_not_configured",
            "profile": "teaching.v1",
            "max_output_tokens": getattr(config, "teaching_output_tokens", None),
        },
        "teaching_calculation": {
            "available": bool(storage_ready and calculation is not None and calculation.available),
            "reason": (calculation.reason if calculation is not None and not calculation.available
                       else (None if storage_ready else storage_reason)) or "teaching_not_configured",
            "tool": "finite_calculate",
        },
        "memory_model":{"available":getattr(config,"memory_layer",None).available if getattr(config,"memory_layer",None) else False,
            "reason":getattr(config,"memory_layer",None).reason if getattr(config,"memory_layer",None) else "memory_not_configured",
            "selected_items":4,"max_memory_bytes":4096},
        "quota_preview": config.quota_preview,
        "provider": provider_info,
        "supervision_management_budget_seconds": SessionConfig().manager_total_seconds,
        "window_seconds": SessionConfig().window_seconds,
        "followup_max_chars": _FOLLOWUP_MAX_CHARS,
    }


@router.get("/activities")
async def list_activities(request: Request, limit: int | None = None, cursor: str | None = None):
    _guard(request)
    page = _bounded_limit(
        limit, default=_ACTIVITY_LIMIT_DEFAULT, maximum=_ACTIVITY_LIMIT_MAX, field="limit",
    )
    after_created, after_id = (None, None) if cursor is None else _decode_cursor(cursor)
    service = ActivityService(_ledger(request))
    try:
        facts = await service.list_activities(
            limit=page + 1, after_created_at=after_created, after_activity_id=after_id,
        )
    except Exception as exc:
        raise _map_read_error(exc) from None
    has_more = len(facts) > page
    facts = facts[:page]
    return {
        "items": [_fact_payload(fact, detail=False) for fact in facts],
        "next_cursor": _encode_cursor(facts[-1]) if has_more and facts else None,
    }


@router.post("/activities")
async def create_activity(request: Request):
    _guard(request)
    try:
        body=CreateActivityInput.model_validate(await read_bounded_json(request))
    except MemoryRefusal as exc:raise _error(exc.status,exc.code,exc.message) from None
    except ValueError:raise _error(422,'invalid_input','活动输入不可核对') from None
    activity_id = _uuid_text(body.activity_id, "activity_id")
    source_ids = [_uuid_text(item, "source_id") for item in body.source_ids]
    if len(set(source_ids)) != len(source_ids):
        raise _error(400, "invalid_input", "资料范围不能包含重复来源")
    config = _config(request)
    if not config.create_layer.available:
        raise _error(409, config.create_layer.reason or "config_invalid", "新建活动尚未开放：请先完成本地活动配置")
    ledger = _ledger(request)
    service = ActivityService(ledger)
    try:
        storage_ready = await service.probe_storage()
    except AdmissionUnavailable:
        raise _error(503, "database_unavailable", "活动数据暂不可用，请稍后重试") from None
    if not storage_ready:
        raise _error(409, "storage_not_ready", "活动存储尚未就绪")
    try:
        current = await service.list_scope_source_versions(source_ids)
    except Exception as exc:
        raise _map_read_error(exc) from None
    not_ready = [item for item in source_ids if item not in current or current[item]["current_version"] is None]
    if not_ready:
        raise HTTPException(
            409,
            detail={
                "code": "source_not_ready",
                "message": "所选资料尚未完成核对或已被移除；请刷新资料列表后重新选择",
                "sources": not_ready,
            },
        )
    quota = config.quota_preview or {}
    if not quota:
        raise _error(503, "config_unavailable", "活动额度配置不可用")
    spec = ActivitySpec(
        activity_id=activity_id,
        sources=tuple(
            SourceSnapshot(item, str(current[item]["current_version"]), int(current[item]["revision"]))
            for item in source_ids
        ),
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=int(quota["deadline_hours"])),
        max_requests=int(quota["max_requests"]),
        max_cost_microunits=int(quota["max_cost_microunits"]),
        reserve_cost_microunits=int(quota["reserve_cost_microunits"]),
        max_request_bytes=int(quota["max_request_bytes"]),
        max_output_tokens=int(quota["max_output_tokens"]),
        max_running_seconds=int(quota["max_running_seconds"]),
        allowed_models=((config.provider, config.model),),
        allowed_tools=tuple(quota.get('allowed_tools',[])) if config.teaching_calculation_layer.available else (),
        max_tool_calls=quota.get('max_tool_calls') if config.teaching_calculation_layer.available else None,
    )
    try:
        await ledger.create_activity(spec,memory_selection=body.memory_selection)
    except MemoryRefusal as exc:
        raise _error(exc.status,exc.code,exc.message) from None
    except ActivityLedgerConflict as exc:
        message = str(exc)
        if "已存在" in message:
            raise _error(409, "activity_exists", "该活动已存在") from None
        if "撤销" in message or "替换" in message:
            raise _error(409, "source_replaced", "资料版本已变化，请刷新后重新选择") from None
        raise _map_read_error(exc) from None
    except Exception as exc:
        raise _map_read_error(exc) from None
    try:
        fact = await service.read_activity(activity_id)
    except Exception as exc:
        raise _map_read_error(exc) from None
    if fact is None:
        raise _error(503, "unavailable", "活动创建后暂不可读取，请刷新列表")
    return {"activity": _fact_payload(fact, detail=True)}


@router.post("/activities/{activity_id}/cancel")
async def cancel_activity(request: Request, activity_id: str):
    _guard(request)
    activity_id = _uuid_text(activity_id, "activity_id")
    service = ActivityService(_ledger(request))
    try:
        await service.cancel_activity(activity_id)
    except ActivityLedgerConflict as exc:
        raise _map_read_error(exc) from None
    except Exception as exc:
        raise _map_read_error(exc) from None
    try:
        fact = await service.read_activity(activity_id)
    except Exception as exc:
        raise _map_read_error(exc) from None
    if fact is None:
        raise _error(404, "not_found", "活动不存在")
    return {"activity": _fact_payload(fact, detail=True)}


@router.post("/activities/{activity_id}/continuations")
async def continue_from_result(request: Request, activity_id: str, body: ContinueInput):
    _guard(request)
    activity_id = _uuid_text(activity_id, "activity_id")
    for field, value in (("parent_operation_id", body.parent_operation_id), ("new_operation_id", body.new_operation_id)):
        if type(value) is not str or _ID_RE.fullmatch(value) is None:
            raise _error(400, "invalid_input", f"{field} 格式非法")
    followup = body.followup
    if type(followup) is not str or not followup.strip() or len(followup) > _FOLLOWUP_MAX_CHARS:
        raise _error(400, "invalid_input", f"继续内容长度需在 1 到 {_FOLLOWUP_MAX_CHARS} 字符之间")
    config = _config(request)
    if not config.continue_layer.available:
        raise _error(
            409,
            config.continue_layer.reason or "config_invalid",
            "显式继续尚未开放：需要本地配置模型密钥与完整服务配置",
        )
    if config.model_service is None:
        raise _error(409, "config_invalid", "模型服务配置不完整")
    service = ActivityService(_ledger(request))
    run_tag = "ui-" + secrets.token_hex(16)
    try:
        outcome = await service.continue_from_result(
            activity_id, body.parent_operation_id, body.new_operation_id, followup,
            config.model_service, SessionConfig(), _EXECUTOR_ID, run_tag,
        )
    except Exception as exc:
        raise _map_read_error(exc) from None
    refusal = {
        "invalid_input": (400, "invalid_input"),
        "input_too_large": (413, "input_too_large"),
        "no_operation": (404, "not_found"),
        "read_unavailable": (503, "unavailable"),
        "cancelled": (409, "activity_cancelled"),
        "result_invalidated": (409, "result_invalidated"),
        "source_invalid": (409, "source_invalid"),
        "result_kind_not_consumable": (409, "result_kind_read_only"),
        "learning_followup_required": (409, "learning_followup_required"),
        "memory_profile_required": (409, "memory_profile_required"),
        "memory_dependency_invalid": (409, "memory_dependency_invalid"),
        "integrity_error": (409, "integrity_error"),
    }
    if outcome.status in refusal:
        status_code, code = refusal[outcome.status]
        raise _error(status_code, code, _REFUSAL_TEXT.get(code, "动作未开始"))
    supervision = outcome.supervision
    business = outcome.business
    business_payload = None
    if business is not None:
        business_payload = {
            "read_status": business.status,
            "payload_available": bool(business.snapshot is not None and business.snapshot.payload is not None),
        }
    return {
        "activity_id": activity_id,
        "new_operation_id": body.new_operation_id,
        "status": outcome.status,
        "business": business_payload,
        "supervision": None if supervision is None else {
            "state": supervision.state,
            "settled_seconds": supervision.settled_seconds,
            "reserved_seconds": supervision.reserved_seconds,
            "pending_fold_seconds": supervision.pending_fold_seconds,
            "cleanup_incomplete": supervision.cleanup_incomplete,
        },
    }


_REFUSAL_TEXT = {
    "invalid_input": "请求内容无效",
    "input_too_large": "继续内容加上已有成果超过单次调用上限；请缩短内容",
    "not_found": "活动或父操作不存在",
    "unavailable": "活动数据暂不可用，请稍后重试",
    "activity_cancelled": "活动已取消，不能继续",
    "result_invalidated": "父成果已失效（范围或来源已变化），不能继续",
    "source_invalid": "资料范围已失效，不能继续",
    "result_kind_read_only": "该成果仅可只读查看，不能作为继续依据",
    "learning_followup_required": "请使用该学习成果的显式续问入口，继续保持学习结构和引用校验",
    "memory_profile_required": "本活动已固定学习背景，请使用教学工作区",
    "memory_dependency_invalid": "所选学习背景或其依据已变化，请新建活动并明确重选",
    "integrity_error": "数据完整性检查失败，未启动任何调用",
}


@router.get("/activities/{activity_id}")
async def read_activity(request: Request, activity_id: str):
    _guard(request)
    activity_id = _uuid_text(activity_id, "activity_id")
    service = ActivityService(_ledger(request))
    try:
        fact = await service.read_activity(activity_id)
    except Exception as exc:
        raise _map_read_error(exc) from None
    if fact is None:
        raise _error(404, "not_found", "活动不存在")
    return {"activity": _fact_payload(fact, detail=True)}


@router.get("/activities/{activity_id}/operations")
async def list_operations(
    request: Request, activity_id: str, limit: int | None = None, cursor: str | None = None,
):
    _guard(request)
    activity_id = _uuid_text(activity_id, "activity_id")
    page = _bounded_limit(
        limit, default=_OPERATION_LIMIT_DEFAULT, maximum=_OPERATION_LIMIT_MAX, field="limit",
    )
    if cursor is not None and _ID_RE.fullmatch(cursor) is None:
        raise _error(400, "invalid_cursor", "游标无效，请刷新后重试")
    service = ActivityService(_ledger(request))
    try:
        rows = await service.list_activity_operations(
            activity_id, limit=page + 1, after_operation_id=cursor,
        )
    except Exception as exc:
        raise _map_read_error(exc) from None
    has_more = len(rows) > page
    rows = rows[:page]
    return {
        "items": [_operation_payload(row, include_payload=False) for row in rows],
        "next_cursor": rows[-1].operation_id if has_more and rows else None,
    }


@router.get("/activities/{activity_id}/operations/{operation_id}")
async def read_operation(request: Request, activity_id: str, operation_id: str):
    _guard(request)
    activity_id = _uuid_text(activity_id, "activity_id")
    if _ID_RE.fullmatch(operation_id) is None:
        raise _error(400, "invalid_input", "operation_id 格式非法")
    service = ActivityService(_ledger(request))
    try:
        row = await service.read_operation(activity_id, operation_id)
    except Exception as exc:
        raise _map_read_error(exc) from None
    if row is None:
        raise _error(404, "not_found", "操作不存在")
    return {"operation": _operation_payload(row, include_payload=True)}
