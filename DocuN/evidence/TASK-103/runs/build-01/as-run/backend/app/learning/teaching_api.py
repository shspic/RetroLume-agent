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
    "memory_dependency_invalid":409,"memory_invalid":409,"memory_profile_required":409,"memory_context_limit":409,
    "context_version_unavailable":409,"memory_not_configured":503,"memory_schema_not_ready":503,
    "not_found": 404, "record_not_found": 404, "citation_not_found": 404,
    "command_key_conflict": 409, "stage_conflict": 409, "version_conflict": 409,
    "goal_changed": 409, "answer_changed": 409, "source_invalid": 409,
    "activity_cancelled": 409, "activity_expired": 409, "unknown_slot": 409,
    "launch_already_claimed": 409, "budget_exhausted": 409,
    "tool_limit_unconfigured": 409, "tool_limit_exhausted": 409, "profile_required": 409,
    "input_too_large": 413, "context_limit": 413, "result_limit": 413, "history_limit": 413,
    "database_unavailable": 503, "teaching_not_configured": 503,
    "teaching_config_invalid": 503, "teaching_config_incompatible": 503,
    "unavailable": 503, "integrity_error":503, "snapshot_limit":413,
}


def _teaching_error(exc: TeachingRefusal):
    status = _STATUS_MAP.get(exc.code, 422)
    return _error(status, exc.code, exc.message)


def _service(request: Request) -> TeachingService:
    return TeachingService(_ledger(request), getattr(request.app.state, "materials", None),
                           request.app.state.originals,session_config=getattr(request.app.state,'teaching_session_config',None))

@router.get("/{activity_id}/teaching/seeds/{operation_id}")
async def read_teaching_seed(request: Request, activity_id: str, operation_id: str):
    _guard(request)
    activity_id = _uuid_text(activity_id, 'activity_id')
    try:
        row = await _ledger(request).read_committed_result(activity_id, operation_id)
        if row.read_status.value != 'committed_current' or row.kind != 'model' or row.payload is None:
            raise TeachingRefusal('version_conflict', 'G7成果目前不可沿用')
        from .contracts import read_document
        profile, _ = read_document(json.loads(row.payload)['value'], activity_id=activity_id, operation_id=operation_id)
        return _public_response({'activity_id':activity_id,'operation_id':operation_id,'goal':profile.goal,
                                 'payload_sha256':row.payload_sha256}, 65536)
    except TeachingRefusal as exc:
        raise _teaching_error(exc) from None
    except (ValueError, TypeError, KeyError):
        raise _error(409, 'version_conflict', '该成果不是可沿用的G7目标') from None
    except Exception as exc:
        raise _map_read_error(exc) from None


async def _read_bounded_body(request: Request) -> dict:
    raw = bytearray()
    async for chunk in request.stream():
        if len(chunk) > MAX_HTTP_BODY_BYTES - len(raw):
            raise _error(413, "input_too_large", "教学命令正文超过 32768 字节上限")
        raw.extend(chunk)
    def unique_pairs(items):
        result = {}
        for key, item in items:
            if key in result:
                raise ValueError("duplicate_teaching_field")
            result[key] = item
        return result
    try:
        value = json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=unique_pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(ValueError("invalid_input")))
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
    from .teaching_views import source_invalid
    row=current["command"]
    records=current["records"]
    result={"activity_id":activity_id,"business_key":business_key,"action":row["action"],
        "request_sha256":row["request_sha256"],"status":row["status"],"duplicate_of":None,
        "operation_id":row["operation_id"],"error_code":row["error_code"],
        "head_revision_now":current["head_revision"],
        "record_ids":[{"record_id":r["record_id"],"kind":r["kind"],"seq":r["seq"]} for r in records],
        "payload_sha256":next((r["operation_payload_sha256"] for r in records if r.get("operation_payload_sha256")),None),
        "applied_revision":next((r["applied_revision"] for r in records if r["applied_revision"] is not None),None),
        "qualification":"source_invalid" if source_invalid(current["sources"]) else
            "unconfirmed" if row["status"] in ('accepted','started','unknown') else
            "history_only" if row["status"]=='history' else "current",
        "model_called":None,"tool_called":None,
        "retry_policy":"same_key_before_claim" if row['status']=='accepted' and row['launch_claimed_at'] is None
            and row['obsolete_at'] is None and row['abandoned_at'] is None else
            "read_only" if row["status"] in ('accepted','started','unknown') else
            "explicit_new_key_after_confirmed_failure" if row["status"] in ('failed','not_sent') else "none",
        "created_at":row["created_at"],"launch_claimed_at":row["launch_claimed_at"],
        "obsolete_at":row["obsolete_at"],"abandoned_at":row["abandoned_at"],"exposed_part":None}
    return _public_response(result,65536)


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
    payload=_workspace_payload(activity_id,view)
    config=_config(request)
    payload['overlay']['teaching_disabled_reason']=None if config.teaching_layer.available else config.teaching_layer.reason
    return _public_response(payload,196608)


def _public_response(payload,limit):
    from fastapi.encoders import jsonable_encoder
    payload=jsonable_encoder(payload)
    if len(json.dumps(payload,ensure_ascii=False,separators=(",",":")).encode())>limit:
        raise _error(413,"snapshot_limit","快照超过限额，请单独查看记录")
    return JSONResponse(payload,headers={"Cache-Control":"no-store"})


def _workspace_payload(activity_id: str, view: dict) -> dict:
    from .teaching_views import regions,view_token,source_invalid
    activity,head=view["activity"],view["head"] or {}
    pending=view["pending"]
    own=head.get("pending_business_key")
    current=[p for p in pending if str(p["business_key"])==str(own)]
    projected=regions(view)
    budget_names=("requests_reserved","max_requests","cost_reserved_microunits","max_cost_microunits",
        "tools_reserved","max_tool_calls","running_settled_seconds","running_reserved_seconds","max_running_seconds","deadline_at")
    return {"schema":"teaching.workspace.v1","activity_id":activity_id,"memory_invalid":view.get("memory_qualified") is False,"memory_selected":view.get("memory_selected",False),"view_token":view_token(view),
        "read_at":view.get("read_at",datetime_utcnow().isoformat()),
        "head":{"revision":head.get("revision",0),"goal_version":head.get("goal_version",0),"phase":head.get("phase","needs_goal"),
            **{key:head.get(key) for key in ("goal_record_id","path_record_id","node_id","exercise_record_id","answer_record_id",
                                           "feedback_record_id","reason_record_id","pending_business_key")}},
        "overlay":{"source_invalid":source_invalid(view.get("sources",[])),"cancelled":activity["status"]=='cancelled',
            "expired":_deadline_passed(activity["deadline_at"]),"processing":any(p["status"] in ('accepted','started') for p in current),
            "unknown":any(p["status"]=='unknown' for p in current)},
        **{key:projected.get(key) for key in ('goal','path','proposal','exercise','answer','feedback','reason','nodes')},
        "sources":[{key:s.get(key) for key in ('source_id','version_id','valid','ready','title','format')} for s in view.get('sources',[])],
        "budgets":{key:activity.get(key) for key in budget_names},"pending":pending,
        "history":[{**r,"label":_kind_label(r['kind'])} for r in view['history']],
        "next_cursor":_history_cursor(activity_id,view_token(view),view['history'],head.get('last_seq',0)),
        "limits":{"goal_versions":32,"records":4096,"history_default":20,"history_max":50,
            "answer_chars":4096,"answer_bytes":12288,"output_tokens_max":2048}}


def _history_cursor(activity_id, token, items, watermark):
    if not items or items[-1]['seq'] <= 1:
        return None
    import base64
    return base64.urlsafe_b64encode(json.dumps({'activity_id':activity_id,'view_token':token,
        'watermark_last_seq':watermark,'before_seq':items[-1]['seq']},separators=(',',':')).encode()).decode().rstrip('=')


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
async def read_teaching_history(request: Request, activity_id: str, limit: int=20,
                                cursor: str | None=None, before_seq: int | None=None):
    import base64
    import binascii
    from .teaching_views import view_token
    _guard(request)
    activity_id=_uuid_text(activity_id,"activity_id")
    if not 1<=limit<=HISTORY_MAX:
        raise _error(400,"invalid_input","limit 须在 1 到 50 之间")
    decoded=None
    if cursor is not None:
        try:
            if len(cursor)>1024 or before_seq is not None: raise ValueError()
            decoded=json.loads(base64.urlsafe_b64decode(cursor+'='*(-len(cursor)%4)))
            if set(decoded)!={'activity_id','view_token','watermark_last_seq','before_seq'}: raise ValueError()
            if decoded['activity_id']!=activity_id: raise _error(404,'not_found','游标不属于此活动')
            before_seq=decoded['before_seq']
            if type(before_seq) is not int: raise ValueError()
        except (ValueError,TypeError,KeyError,binascii.Error):
            raise _error(400,'invalid_input','历史游标非法') from None
    try:
        page=await _service(request).read_history(activity_id,limit,before_seq)
    except ValueError:
        raise _error(400,'invalid_input','历史序号非法') from None
    except Exception as exc:
        raise _map_read_error(exc) from None
    if page is None: raise _error(404,'not_found','活动不存在')
    token=view_token(page)
    if decoded and decoded['view_token']!=token: raise _error(409,'snapshot_changed','当前版本变化，请刷新工作区')
    items=page['items']; watermark=(page['head'] or {}).get('last_seq',0)
    next_cursor=None
    if len(items)==limit:
        next_cursor=base64.urlsafe_b64encode(json.dumps({'activity_id':activity_id,'view_token':token,
            'watermark_last_seq':watermark,'before_seq':items[-1]['seq']},separators=(',',':')).encode()).decode().rstrip('=')
    return _public_response({'activity_id':activity_id,'view_token':token,'read_at':page['read_at'],
        'watermark_last_seq':watermark,'items':[{**r,'label':_kind_label(r['kind'])} for r in items],'next_cursor':next_cursor},65536)


@router.get("/{activity_id}/teaching/records/{record_id}")
async def read_teaching_record(request: Request, activity_id: str, record_id: str):
    from .teaching_views import public_record
    _guard(request)
    activity_id=_uuid_text(activity_id,'activity_id'); record_id=_uuid_text(record_id,'record_id')
    try: record=await _service(request).read_record(activity_id,record_id)
    except Exception as exc: raise _map_read_error(exc) from None
    if record is None: raise _error(404,'record_not_found','教学记录不存在')
    qualification,body=public_record(record,record['snapshot_sources'],record['snapshot_exposures'],record['snapshot_head'],record['snapshot_activity'])
    keys=('record_id','kind','seq','goal_version','scope_revision','parent_record_id','exercise_record_id',
          'answer_record_id','supersedes_record_id','body_sha256','created_at')
    return _public_response({**{key:record[key] for key in keys},'qualification':qualification,'public_body':body},65536)


@router.get("/{activity_id}/teaching/records/{record_id}/citations/{citation_id}")
async def read_teaching_citation(request: Request, activity_id: str, record_id: str, citation_id: str):
    import asyncio
    from .teaching_views import public_record
    from .contracts import CatalogEntry,sha
    from .evidence import load_units,LearningRefusal
    from app.retrieval.evidence import EvidenceFragment,verify_fragment
    _guard(request)
    activity_id=_uuid_text(activity_id,'activity_id'); record_id=_uuid_text(record_id,'record_id')
    service=_service(request)
    try:
        row=await service.read_record(activity_id,record_id)
        if row is None: raise TeachingRefusal('record_not_found','教学记录不存在')
        q,body=public_record(row,row['snapshot_sources'],row['snapshot_exposures'],row['snapshot_head'],row['snapshot_activity'])
        if q in ('source_invalid','integrity_error','memory_invalid'): raise TeachingRefusal(q,'引用目前不可核对')
        citation_payload = row.get('citation_payload') or row.get('payload')
        if citation_payload is None: raise TeachingRefusal('citation_not_found','该记录没有资料引用')
        # 未暴露参考不能通过猜引用 ID 查看其复制文本。
        visible=set()
        def collect(value):
            if isinstance(value,dict):
                visible.update(value.get('citations',[]))
                for v in value.values(): collect(v)
            elif isinstance(value,list):
                for v in value: collect(v)
        collect(body)
        from app.capabilities.contracts import validate_business_payload
        validate_business_payload(citation_payload,row.get('citation_payload_format') or row['payload_format'],
                                  row.get('citation_payload_sha256') or row['operation_payload_sha256'])
        value=json.loads(citation_payload)['value']
        entry=next((CatalogEntry.model_validate(e) for e in value.get('catalog',[]) if e['citation_id']==citation_id and citation_id in visible),None)
        if entry is None: raise TeachingRefusal('citation_not_found','引用不属于该公开内容')
        selected=[s for s in row.get('bound_sources',row['snapshot_sources']) if s['source_id']==entry.source_id and s['version_id']==entry.version_id
                  and s['source_revision']==entry.source_revision and s['sha256']==entry.original_sha256 and s.get('valid') and s.get('ready',True)]
        if len(selected)!=1: raise TeachingRefusal('source_invalid','原资料身份变化')
        units=await asyncio.to_thread(load_units,{'sources':selected,'source_count':1},service.materials,service.originals)
        item=next((u for u in units if u.unit.physical_page==entry.physical_page and u.unit.origin_kind==entry.origin_kind and u.supplement_id==entry.supplement_id),None)
        fragment=EvidenceFragment(entry.evidence_id,entry.source_id,entry.version_id,entry.source_revision,entry.physical_page,
            entry.origin_kind,entry.start_line,entry.end_line,entry.start_offset,entry.end_offset,entry.fragment_sha256,entry.text)
        if item is None or sha(item.unit.text)!=entry.unit_sha256 or not verify_fragment(item.unit,fragment):
            raise TeachingRefusal('source_invalid','原文位置或 hash 变化')
        return _public_response({'citation':entry.model_dump(),'read_at':row['snapshot_read_at']},65536)
    except TeachingRefusal as exc: raise _teaching_error(exc) from None
    except LearningRefusal: raise _error(409,'source_invalid','引用不可核对') from None
    except (ValueError,TypeError,KeyError): raise _error(503,'integrity_error','引用内容完整性未确认') from None
    except (AdmissionUnavailable,DatabaseUnavailable): raise _error(503,'unavailable','引用未确认') from None


@router.get("/{activity_id}/teaching/answers/{answer_record_id}/references/{reference_id}")
async def read_teaching_answer_reference(request: Request, activity_id: str, answer_record_id: str, reference_id: str):
    from .teaching_views import verified_document
    from .contracts import sha
    _guard(request)
    activity_id=_uuid_text(activity_id,'activity_id'); answer_record_id=_uuid_text(answer_record_id,'answer_record_id')
    try: row=await _service(request).read_record(activity_id,answer_record_id)
    except Exception as exc: raise _map_read_error(exc) from None
    if row is None or row['kind']!='answer': raise _error(404,'record_not_found','作答不存在')
    try: body=verified_document(row)
    except (ValueError,TypeError,KeyError): raise _error(503,'integrity_error','作答内容未确认') from None
    text=body['text']
    # 作答正文的完整、有 hash 的有限切片；不存在任意文件读取入口。
    expected='ar_'+sha(answer_record_id+row['body_sha256'])[:24]
    if reference_id!=expected: raise _error(404,'citation_not_found','作答引用不存在')
    return _public_response({'answer_record_id':answer_record_id,'reference_id':expected,'start_offset':0,'end_offset':len(text),
        'sha256':sha(text),'text':text,'read_at':row['snapshot_read_at']},65536)
