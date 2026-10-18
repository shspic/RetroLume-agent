"""限定目标/问题HTTP入口；不开放内部profile、资料或模型参数。"""
from typing import Literal
import secrets

from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict, Field

from app.activities.api import _guard, _ledger, _config, _uuid_text, _error, _operation_payload, _map_read_error
from app.capabilities.contracts import AdmissionUnavailable
from app.materials.repository import DatabaseUnavailable, VersionConflict
from .contracts import normalize_input
from .evidence import LearningRefusal, read_citation
from .service import LearningService

router = APIRouter(prefix="/api/activities")


class FirstInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    business_key: str
    goal: str = Field(max_length=1024)
    confirmed: Literal[True]


class FollowupInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    business_key: str
    parent_operation_id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:/-]+$")
    question: str = Field(max_length=1024)
    confirmed: Literal[True]


def _service(request):
    return LearningService(_ledger(request), getattr(request.app.state, "materials", None), request.app.state.originals)


def _refusal(exc):
    code = exc.code
    status = 409
    if code in {"invalid_input", "clarification_required"}:
        status = 400
    elif code in {"input_too_large", "learning_scope_limit", "learning_context_limit"}:
        status = 413
    elif code == "not_found" or code == "citation_not_found":
        status = 404
    elif code in {"unavailable", "config_missing", "config_invalid", "config_incompatible",
            "learning_not_configured", "learning_config_invalid", "learning_config_incompatible",
            "provider_key_not_configured"}:
        status = 503
    return _error(status, code, exc.message)


async def _execute(request, activity_id, key, text, parent=None):
    activity_id = _uuid_text(activity_id, "activity_id")
    key = _uuid_text(key, "business_key")
    try:
        text = normalize_input(text)
    except ValueError as exc:
        raise _error(413 if str(exc) == "input_too_large" else 400, str(exc), "请填写具体目标或问题，最多1024字和4096 UTF-8字节") from None
    try:
        value = await _service(request).execute(activity_id, key, text, _config(request),
            parent_operation_id=parent, run_tag="learn-" + secrets.token_hex(12))
    except LearningRefusal as exc:
        if exc.kind is not None:
            return {"status": "precheck", "model_called": False,
                "precheck": {"kind": exc.kind, "message": exc.message,
                    "questions": [exc.message] if exc.kind == "clarification" else []}}
        raise _refusal(exc) from None
    except (VersionConflict, OSError, UnicodeDecodeError, ValueError):
        raise _error(409, "source_invalid", "原文或版本完整性检查失败，未开始新调用") from None
    except (AdmissionUnavailable, DatabaseUnavailable):
        raise _error(503, "unavailable", "本地资料或活动存储暂不可用") from None
    supervision = value["supervision"]
    business = value["business"]
    return {"activity_id": activity_id, "business_key": key, "operation_id": value["operation_id"],
        "status": value["status"],
        "business": {"read_status": business.status, "payload_available": bool(business.snapshot and business.snapshot.payload is not None)},
        "supervision": None if supervision is None else {
            "state": supervision.state, "settled_seconds": supervision.settled_seconds,
            "reserved_seconds": supervision.reserved_seconds, "pending_fold_seconds": supervision.pending_fold_seconds,
            "cleanup_incomplete": supervision.cleanup_incomplete}}


@router.post("/{activity_id}/learning/first")
async def first(request: Request, activity_id: str, body: FirstInput):
    _guard(request)
    return await _execute(request, activity_id, body.business_key, body.goal)


@router.post("/{activity_id}/learning/followups")
async def followup(request: Request, activity_id: str, body: FollowupInput):
    _guard(request)
    return await _execute(request, activity_id, body.business_key, body.question, body.parent_operation_id)


@router.get("/{activity_id}/learning/intents/{business_key}")
async def reconcile(request: Request, activity_id: str, business_key: str, action: Literal["first", "followup"]):
    _guard(request)
    activity_id = _uuid_text(activity_id, "activity_id")
    business_key = _uuid_text(business_key, "business_key")
    try:
        row = await _service(request).reconcile(activity_id, business_key, action)
    except Exception as exc:
        raise _map_read_error(exc) from None
    return {"operation": None if row is None else _operation_payload(row, include_payload=True)}


@router.get("/{activity_id}/learning/operations/{operation_id}/citations/{citation_id}")
async def citation(request: Request, activity_id: str, operation_id: str, citation_id: str):
    _guard(request)
    activity_id = _uuid_text(activity_id, "activity_id")
    try:
        return await read_citation(_ledger(request), request.app.state.materials, request.app.state.originals,
            activity_id, operation_id, citation_id)
    except LearningRefusal as exc:
        raise _refusal(exc) from None
    except (ValueError, TypeError, VersionConflict, OSError, UnicodeDecodeError):
        raise _error(409, "citation_unavailable", "引用版本、原文或位置不可用，未用新版本代替") from None
    except (AdmissionUnavailable, DatabaseUnavailable):
        raise _error(503, "unavailable", "引用存储暂不可用") from None
