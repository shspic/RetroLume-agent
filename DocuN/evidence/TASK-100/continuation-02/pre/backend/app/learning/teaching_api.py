"""教学 HTTP 面（TASK-100 第 7.1 节）：封闭命令 + 只读快照/历史/记录。

仍挂 /api/activities 且调用现有 _guard（local_session allow_own_origin）。
教学路由在 JSON 解析前计 32768 字节流量；纯 GET 不写暴露、不恢复 claim。
"""
from __future__ import annotations

import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.activities.api import _guard, _ledger, _config, _uuid_text, _error, _map_read_error
from app.capabilities.contracts import AdmissionUnavailable
from app.materials.repository import DatabaseUnavailable

from .teaching_contracts import (
    MAX_HTTP_BODY_BYTES,
    HISTORY_MAX,
    TeachingCommandInput,
    TeachingRefusal,
    validate_exposed_part,
)
from .teaching_service import TeachingService

router = APIRouter(prefix="/api/activities")

_STATUS_MAP = {
    "invalid_input": 400, "clarification_required": 400,
    "not_found": 404, "record_not_found": 404, "citation_not_found": 404,
    "command_key_conflict": 409, "stage_conflict": 409, "version_conflict": 409,
    "goal_changed": 409, "answer_changed": 409, "source_invalid": 409,
    "activity_cancelled": 409, "activity_expired": 409, "unknown_slot": 409,
    "launch_already_claimed": 409, "budget_exhausted": 409,
    "tool_limit_unconfigured": 409, "tool_limit_exhausted": 409, "profile_required": 409,
    "input_too_large": 413, "context_limit": 413, "result_limit": 413, "history_limit": 413,
    "database_unavailable": 503, "teaching_not_configured": 503,
    "teaching_config_invalid": 503, "teaching_config_incompatible": 503,
    "unavailable": 503,
}


def _teaching_error(exc: TeachingRefusal):
    status = _STATUS_MAP.get(exc.code, 422)
    return _error(status, exc.code, exc.message)


def _service(request: Request) -> TeachingService:
    return TeachingService(_ledger(request), getattr(request.app.state, "materials", None),
                           request.app.state.originals)


async def _read_bounded_body(request: Request) -> dict:
    raw = await request.body()
    if len(raw) > MAX_HTTP_BODY_BYTES:
        raise _error(413, "input_too_large", "教学命令正文超过 32768 字节上限")
    try:
        value = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        raise _error(400, "invalid_input", "教学命令正文不是合法 JSON") from None
    if not isinstance(value, dict):
        raise _error(400, "invalid_input", "教学命令正文必须是 JSON 对象")
    return value


@router.post("/{activity_id}/teaching/commands")
async def submit_teaching_command(request: Request, activity_id: str):
    _guard(request)
    activity_id = _uuid_text(activity_id, "activity_id")
    body = await _read_bounded_body(request)
    try:
        command = TeachingCommandInput.model_validate(body, strict=True)
    except Exception:
        raise _error(422, "invalid_input", "教学命令字段或类型非法") from None
    try:
        receipt = await _service(request).submit_command(
            activity_id, command, _config(request),
            run_tag="teach-" + __import__("secrets").token_hex(12))
    except TeachingRefusal as exc:
        raise _teaching_error(exc) from None
    except (AdmissionUnavailable, DatabaseUnavailable):
        raise _error(503, "database_unavailable", "教学数据暂不可用") from None
    return JSONResponse(_receipt_payload(receipt), status_code=200)


def _receipt_payload(receipt) -> dict:
    return {
        "activity_id": receipt.activity_id, "business_key": receipt.business_key,
        "action": receipt.action, "request_sha256": receipt.request_sha256,
        "status": receipt.status, "duplicate_of": receipt.duplicate_of,
        "record_ids": [r.model_dump() for r in receipt.record_ids],
        "operation_id": receipt.operation_id, "payload_sha256": receipt.payload_sha256,
        "applied_revision": receipt.applied_revision,
        "head_revision_now": receipt.head_revision_now,
        "qualification": receipt.qualification, "error_code": receipt.error_code,
        "model_called": receipt.model_called, "tool_called": receipt.tool_called,
        "retry_policy": receipt.retry_policy, "exposed_part": receipt.exposed_part,
    }


@router.get("/{activity_id}/teaching/commands/{business_key}")
async def read_teaching_command(request: Request, activity_id: str, business_key: str):
    _guard(request)
    activity_id = _uuid_text(activity_id, "activity_id")
    business_key = _uuid_text(business_key, "business_key")
    try:
        current = await _service(request).read_command(activity_id, business_key)
    except Exception as exc:
        raise _map_read_error(exc) from None
    if current is None:
        raise _error(404, "not_found", "命令不存在")
    row = current["command"]
    return {
        "activity_id": activity_id, "business_key": business_key, "action": row["action"],
        "request_sha256": row["request_sha256"], "status": row["status"],
        "operation_id": row["operation_id"], "error_code": row["error_code"],
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        "launch_claimed_at": row["launch_claimed_at"].isoformat() if row["launch_claimed_at"] else None,
        "obsolete_at": row["obsolete_at"].isoformat() if row["obsolete_at"] else None,
        "abandoned_at": row["abandoned_at"].isoformat() if row["abandoned_at"] else None,
        "head_revision_now": current["head_revision"],
    }


@router.get("/{activity_id}/teaching/workspace")
async def read_teaching_workspace(request: Request, activity_id: str, history_limit: int = 20):
    _guard(request)
    activity_id = _uuid_text(activity_id, "activity_id")
    if not 1 <= history_limit <= HISTORY_MAX:
        raise _error(400, "invalid_input", "history_limit 须在 1 到 50 之间")
    try:
        view = await _service(request).read_workspace(activity_id, history_limit)
    except Exception as exc:
        raise _map_read_error(exc) from None
    if view is None:
        raise _error(404, "not_found", "活动不存在")
    return _workspace_payload(activity_id, view)


def _workspace_payload(activity_id: str, view: dict) -> dict:
    from .contracts import canonical, sha
    from .teaching_policy import compute_view_token, project_public_exercise
    activity, head, pending, history = view["activity"], view["head"], view["pending"], view["history"]
    sources = view.get("sources") or []
    bodies = view.get("current_bodies") or []
    exposed_parts = set(view.get("exposed_parts") or [])
    revision = 0 if head is None else head["revision"]
    last_seq = 0 if head is None else head["last_seq"]
    cancelled = activity["status"] == "cancelled"
    expired = _deadline_passed(activity["deadline_at"])
    # DEF-005：view_token 含真实来源身份与命令状态摘要（na 占位取消）；
    # 来源代次或 pending 状态变化即不同 token。
    source_invalid = any(not s.get("valid") for s in sources)
    source_identity_sha = sha(canonical(sources))
    command_state_sha = sha(canonical(
        {"pending": pending, "pending_business_key": view.get("pending_business_key")}))
    view_token = compute_view_token(revision, last_seq, activity["scope_revision"],
                                    source_identity_sha, command_state_sha)
    # 当前实体正文区域：单语句取出的指针记录 + 007 联查投影；坏单项
    # 局部抑制（integrity_error），不拖垮其他成功事实；来源失效时抑制
    # 模型/工具派生正文、保留用户文字（goal/answer/correction）。
    regions = _current_regions(bodies, exposed_parts, project_public_exercise, source_invalid)
    payload = {
        "schema": "teaching.workspace.v1", "activity_id": activity_id,
        "view_token": view_token, "read_at": datetime_utcnow().isoformat(),
        "head": {
            "revision": revision,
            "goal_version": 0 if head is None else head["goal_version"],
            "phase": "needs_goal" if head is None else head["phase"],
            "goal_record_id": None if head is None else _s(head["goal_record_id"]),
            "path_record_id": None if head is None else _s(head["path_record_id"]),
            "node_id": None if head is None else head["node_id"],
            "exercise_record_id": None if head is None else _s(head["exercise_record_id"]),
            "answer_record_id": None if head is None else _s(head["answer_record_id"]),
            "feedback_record_id": None if head is None else _s(head["feedback_record_id"]),
            "reason_record_id": None if head is None else _s(head["reason_record_id"]),
            "pending_business_key": None if head is None else _s(head["pending_business_key"]),
        },
        "overlay": {
            "source_invalid": source_invalid, "cancelled": cancelled, "expired": expired,
            "processing": any(p["status"] in ("accepted", "started") for p in pending),
            "unknown": any(p["status"] == "unknown" for p in pending),
        },
        "goal": regions.get("goal"),
        "path": regions.get("path"),
        "proposal": regions.get("proposal"),
        "exercise": regions.get("exercise"),
        "answer": regions.get("answer"),
        "feedback": regions.get("feedback"),
        "reason": regions.get("reason"),
        "sources": [{"source_id": s.get("source_id"), "version_id": s.get("version_id"),
                     "valid": bool(s.get("valid")), "title": s.get("title"),
                     "format": s.get("format")} for s in sources],
        "budgets": {
            "requests_reserved": activity["requests_reserved"],
            "max_requests": activity["max_requests"],
            "cost_reserved_microunits": activity["cost_reserved_microunits"],
            "max_cost_microunits": activity["max_cost_microunits"],
            "tools_reserved": activity["tools_reserved"],
            "max_tool_calls": activity["max_tool_calls"],
            "running_settled_seconds": activity["running_settled_seconds"],
            "running_reserved_seconds": activity["running_reserved_seconds"],
            "max_running_seconds": activity["max_running_seconds"],
            "deadline_at": activity["deadline_at"],
        },
        "pending": [{"business_key": p["business_key"], "action": p["action"],
                     "status": p["status"], "error_code": p.get("error_code"),
                     "created_at": p["created_at"]} for p in pending],
        "history": [{"record_id": h["record_id"], "kind": h["kind"], "seq": h["seq"],
                     "goal_version": h["goal_version"],
                     "parent_record_id": h["parent_record_id"],
                     "created_at": h["created_at"],
                     "label": _kind_label(h["kind"])} for h in history],
        "next_cursor": None,
        "limits": {"goal_versions": 32, "records": 4096, "history_default": 20, "history_max": 50,
                   "answer_chars": 4096, "answer_bytes": 12288, "output_tokens_max": 2048},
    }
    return payload


def _deadline_passed(deadline) -> bool:
    from datetime import datetime, timezone
    if isinstance(deadline, str):
        try:
            deadline = datetime.fromisoformat(deadline)
        except ValueError:
            return False
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    return deadline <= datetime.now(timezone.utc)


def _seven_result(payload_text: str):
    """解析 007 规范封套中的低信任 result；失败返回 None（局部抑制）。"""
    if not payload_text:
        return None
    try:
        return json.loads(payload_text)["value"]["result"]
    except (ValueError, TypeError, KeyError):
        return None


def _current_regions(bodies: list, exposed_parts: set, project_public_exercise,
                     source_invalid: bool = False) -> dict:
    """把单语句取出的当前实体记录投影为工作区正文区域。

    派生正文（模型/工具产物）仅在来源有效时可读；来源失效时抑制派生
    内容但保留用户文字历史（goal/answer 是用户输入）。单条解析失败仅
    标记该区域 integrity_error，不影响其他区域。
    """
    regions: dict = {}
    by_kind: dict[str, list] = {}
    for row in bodies:
        by_kind.setdefault(row["kind"], []).append(row)

    def body_json(row):
        try:
            return json.loads(row["body"]) if row.get("body") else None
        except (ValueError, TypeError):
            return None

    def derived(value):
        """模型/工具派生区域的来源资格门：失效即抑制正文。"""
        if source_invalid:
            return {"qualification": "source_invalid"}
        return value

    goal_rows = by_kind.get("goal") or []
    if goal_rows:
        parsed = body_json(goal_rows[0])
        if parsed is None:
            regions["goal"] = {"qualification": "integrity_error"}
        else:
            # 用户本人目标文字：来源失效仍可历史查看。
            regions["goal"] = {"qualification": "current", "goal": parsed.get("goal"),
                               "self_report": parsed.get("self_report"),
                               "domain": parsed.get("domain")}

    path_rows = by_kind.get("path_accept") or []
    if path_rows:
        parsed = body_json(path_rows[0])
        if parsed is None:
            regions["path"] = {"qualification": "integrity_error"}
        else:
            regions["path"] = derived({"qualification": "current",
                                       "record_id": str(path_rows[0]["record_id"]),
                                       "nodes": parsed.get("nodes") or []})

    proposal_rows = by_kind.get("path_proposal") or []
    if proposal_rows:
        row = proposal_rows[0]
        result = _seven_result(row.get("payload"))
        if result is None:
            regions["proposal"] = {"qualification": "integrity_error"}
        else:
            regions["proposal"] = derived({"qualification": "current",
                                           "record_id": str(row["record_id"]),
                                           "message": result.get("message"),
                                           "nodes": result.get("nodes") or []})

    exercise_rows = by_kind.get("exercise") or []
    if exercise_rows:
        row = exercise_rows[0]
        result = _seven_result(row.get("payload"))
        if result is None:
            regions["exercise"] = {"qualification": "integrity_error"}
        else:
            # 未暴露的参考与提示绝不返回（project_public_exercise 裁决）。
            regions["exercise"] = derived({"qualification": "current",
                                           "record_id": str(row["record_id"]),
                                           **project_public_exercise(result, exposed_parts)})

    answer_rows = by_kind.get("answer") or []
    if answer_rows:
        parsed = body_json(answer_rows[0])
        if parsed is None:
            regions["answer"] = {"qualification": "integrity_error"}
        else:
            # 用户作答文字：来源失效仍可历史查看。
            regions["answer"] = {"qualification": "current",
                                 "record_id": str(answer_rows[0]["record_id"]),
                                 "text": parsed.get("text"), "kind": parsed.get("kind"),
                                 "supersedes": parsed.get("supersedes_answer_record_id")}

    feedback_rows = by_kind.get("feedback") or []
    if feedback_rows:
        row = feedback_rows[0]
        result = _seven_result(row.get("payload"))
        if result is None:
            regions["feedback"] = {"qualification": "integrity_error"}
        else:
            regions["feedback"] = derived({"qualification": "current",
                                           "record_id": str(row["record_id"]),
                                           "message": result.get("message"),
                                           "correct_parts": result.get("correct_parts") or [],
                                           "errors": result.get("errors") or [],
                                           "evidence_gaps": result.get("evidence_gaps") or [],
                                           "cause_hypotheses": result.get("cause_hypotheses") or [],
                                           "dimension_observations": result.get("dimension_observations") or [],
                                           "next_focus": result.get("next_focus")})

    reason_rows = (by_kind.get("progress") or []) + (by_kind.get("correction") or [])
    if reason_rows:
        row = sorted(reason_rows, key=lambda r: r["seq"])[-1]
        if row["kind"] == "progress":
            result = _seven_result(row.get("payload"))
            if result is None:
                regions["reason"] = {"qualification": "integrity_error"}
            else:
                regions["reason"] = derived({"qualification": "current",
                                             "record_id": str(row["record_id"]),
                                             "kind": "progress", "body": result})
        else:
            parsed = body_json(row)
            if parsed is None:
                regions["reason"] = {"qualification": "integrity_error"}
            else:
                # 用户纠错文字：来源失效仍可历史查看。
                regions["reason"] = {"qualification": "current",
                                     "record_id": str(row["record_id"]),
                                     "kind": "correction", "text": parsed.get("text"),
                                     "disputed_dimensions": parsed.get("disputed_dimensions") or []}
    return regions


def _kind_label(kind: str) -> str:
    labels = {"goal": "目标保存", "path_proposal": "路径建议", "path_accept": "路径接受",
              "exercise": "练习", "exposure": "参考暴露", "answer": "作答",
              "calculation": "核算", "feedback": "反馈", "progress": "进度",
              "correction": "纠错", "node_selection": "节点切换"}
    return labels.get(kind, kind)


def _s(value) -> str | None:
    return None if value is None else str(value)


def datetime_utcnow():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc)


@router.get("/{activity_id}/teaching/history")
async def read_teaching_history(request: Request, activity_id: str, limit: int = 20,
                                before_seq: int | None = None):
    _guard(request)
    activity_id = _uuid_text(activity_id, "activity_id")
    if not 1 <= limit <= HISTORY_MAX:
        raise _error(400, "invalid_input", "limit 须在 1 到 50 之间")
    try:
        page = await _service(request).read_history(activity_id, limit, before_seq)
    except ValueError:
        raise _error(400, "invalid_input", "before_seq 非法") from None
    except Exception as exc:
        raise _map_read_error(exc) from None
    if page is None:
        raise _error(404, "not_found", "活动不存在")
    items = page["items"]
    return {
        "activity_id": activity_id,
        "watermark_last_seq": items[-1]["seq"] if items else 0,
        "items": [{"record_id": _s(h["record_id"]), "kind": h["kind"], "seq": h["seq"],
                   "goal_version": h["goal_version"], "parent_record_id": _s(h["parent_record_id"]),
                   "created_at": h["created_at"].isoformat(), "label": _kind_label(h["kind"])}
                  for h in items],
        "next_cursor": None if len(items) < limit else f"before={items[-1]['seq']}",
    }


@router.get("/{activity_id}/teaching/records/{record_id}")
async def read_teaching_record(request: Request, activity_id: str, record_id: str):
    _guard(request)
    activity_id = _uuid_text(activity_id, "activity_id")
    record_id = _uuid_text(record_id, "record_id")
    try:
        record = await _service(request).read_record(activity_id, record_id)
    except Exception as exc:
        raise _map_read_error(exc) from None
    if record is None:
        raise _error(404, "record_not_found", "教学记录不存在")
    # 参考投影：只有已记录对应 exposure 才允许返回参考正文（DEF-005）。
    # exercise/feedback 正文在 007；此处读取并按暴露资格投影。
    public_body = None
    qualification = "current"
    service = _service(request)
    if record["kind"] == "exercise":
        exposures = await service.ledger.read_teaching_exposures(
            activity_id, str(record["record_id"]))
        operation_id = record.get("operation_id")
        result = None
        if operation_id:
            try:
                row = await service.ledger.read_operation(activity_id, operation_id)
                if row is not None and getattr(row, "payload", None):
                    result = json.loads(row.payload)["value"]["result"]
            except (ValueError, TypeError, KeyError):
                result = None
        if result is None:
            public_body = {"reference_available": "reference" in exposures,
                           "hint_available": "hint" in exposures,
                           "qualification": "integrity_error"}
        else:
            from .teaching_policy import project_public_exercise
            public_body = project_public_exercise(result, exposures)
    elif record["kind"] == "feedback":
        operation_id = record.get("operation_id")
        result = None
        if operation_id:
            try:
                row = await service.ledger.read_operation(activity_id, operation_id)
                if row is not None and getattr(row, "payload", None):
                    result = json.loads(row.payload)["value"]["result"]
            except (ValueError, TypeError, KeyError):
                result = None
        if result is None:
            public_body = {"qualification": "integrity_error"}
        else:
            # 反馈从 COMMIT 起与其暴露记录一起可读；缺暴露事实即完整性错误，
            # 抑制正文而不是泄露未登记参考。
            exposures = await service.ledger.read_teaching_exposures(
                activity_id, str(record["exercise_record_id"])) if record.get("exercise_record_id") else set()
            if "reference" not in exposures:
                public_body = {"qualification": "integrity_error"}
            else:
                public_body = {"message": result.get("message"),
                               "correct_parts": result.get("correct_parts") or [],
                               "errors": result.get("errors") or [],
                               "evidence_gaps": result.get("evidence_gaps") or [],
                               "cause_hypotheses": result.get("cause_hypotheses") or [],
                               "dimension_observations": result.get("dimension_observations") or [],
                               "next_focus": result.get("next_focus")}
    elif record["body"] is not None:
        try:
            public_body = json.loads(record["body"])
        except (ValueError, TypeError):
            public_body = {"qualification": "integrity_error"}
    return {
        "record_id": record_id, "kind": record["kind"], "seq": record["seq"],
        "goal_version": record["goal_version"], "scope_revision": record["scope_revision"],
        "parent_record_id": _s(record["parent_record_id"]),
        "exercise_record_id": _s(record["exercise_record_id"]),
        "answer_record_id": _s(record["answer_record_id"]),
        "supersedes_record_id": _s(record["supersedes_record_id"]),
        "body_sha256": record["body_sha256"],
        "created_at": record["created_at"].isoformat(),
        "qualification": qualification,
        "public_body": public_body,
    }
