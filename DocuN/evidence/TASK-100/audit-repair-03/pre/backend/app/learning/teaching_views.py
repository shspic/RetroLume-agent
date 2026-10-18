"""同一数据库快照的纯投影；不写暴露或执行命令。"""
from __future__ import annotations

import json
from .contracts import canonical, sha, CatalogEntry
from .teaching_contracts import parse_teaching_output
from .teaching_policy import compute_view_token, project_public_exercise
from app.capabilities.contracts import validate_business_payload


def source_invalid(sources):
    return not sources or len(sources)>10 or any(not s.get("valid") or not s.get("ready",True) for s in sources)


def view_token(view):
    head=view.get("head") or {}
    return compute_view_token(head.get("revision",0),head.get("last_seq",0),view["activity"]["scope_revision"],
        sha(canonical(view.get("sources",[]))),sha(canonical({"pending":view.get("pending",[]),
        "pending_business_key":head.get("pending_business_key")})))


def verified_document(row):
    if row.get("body") is not None:
        if sha(row["body"])!=row["body_sha256"]:
            raise ValueError("integrity_error")
        value=json.loads(row["body"])
        if canonical(value)!=row["body"]:
            raise ValueError("integrity_error")
        return value
    if not row.get("payload") or row["body_sha256"]!=row.get("operation_payload_sha256"):
        raise ValueError("integrity_error")
    validate_business_payload(row["payload"],row["payload_format"],row["operation_payload_sha256"])
    value=json.loads(row["payload"])["value"]
    if row["kind"]=="calculation":
        return value
    for name in ("activity_id","goal_version","scope_revision"):
        if value.get(name)!=row[name]:
            raise ValueError("integrity_error")
    if value.get("command_key")!=str(row["command_key"]):
        raise ValueError("integrity_error")
    action={"path_proposal":"plan","exercise":"exercise","feedback":"evaluate"}.get(row["kind"])
    if action is None:
        raise ValueError("integrity_error")
    parsed=parse_teaching_output(canonical(value["result"]),action)
    entries=[CatalogEntry.model_validate(e) for e in value["catalog"]]
    if any(e.citation_id!='lc_'+sha(value['request_sha256']+e.evidence_id)[:24] for e in entries):
        raise ValueError("integrity_error")
    return parsed


def exposure_parts(exposures,exercise_id, *, feedback=None):
    parts=set()
    for e in exposures:
        if str(e["exercise_record_id"])!=str(exercise_id):
            continue
        try:
            body=json.loads(e["body"])
            if sha(e["body"])!=e["body_sha256"] or canonical(body)!=e["body"]:
                continue
            if body.get("part") not in {"hint","reference"}:
                continue
            if feedback is not None and (str(e["parent_record_id"])!=str(feedback["record_id"])
                    or str(e["command_key"])!=str(feedback["command_key"])):
                continue
            parts.add(body["part"])
        except (ValueError,TypeError,KeyError):
            continue
    return parts


def public_record(row,sources,exposures,head,activity):
    kind=row["kind"]
    derived=kind not in {"goal","answer","correction","exposure"}
    if source_invalid(sources) and derived:
        return "source_invalid",None
    try:
        value=verified_document(row)
        if kind=='calculation':
            value={'value_decimal':value}
        elif kind=="exercise":
            value=project_public_exercise(value,exposure_parts(exposures,row["record_id"]))
        elif kind=="feedback":
            if "reference" not in exposure_parts(exposures,row["exercise_record_id"],feedback=row):
                raise ValueError("integrity_error")
        elif kind=="exposure":
            value={"part":value["part"],"exposed":True}
        elif kind=="path_proposal":
            value={k:v for k,v in value.items() if k in {"result_type","message","nodes","questions","gaps","conflicts"}}
        from datetime import datetime,timezone
        deadline=activity.get('deadline_at')
        if isinstance(deadline,str):deadline=datetime.fromisoformat(deadline)
        active=not deadline or deadline>datetime.now(timezone.utc)
        current=bool(head and row["goal_version"]==head["goal_version"]
                     and row["scope_revision"]==activity["scope_revision"] and activity["status"]!='cancelled'
                     and active and not source_invalid(sources))
        return ("current" if current else "history"),value
    except (ValueError,TypeError,KeyError):
        return "integrity_error",None


def regions(view):
    head=view.get("head") or {}
    projection=head.get("projection") or {}
    if isinstance(projection,str):
        try: projection=json.loads(projection)
        except ValueError: projection={}
    pointers={"goal":head.get("goal_record_id"),"path":head.get("path_record_id"),
        "proposal":projection.get("pending_proposal_record_id"),"exercise":head.get("exercise_record_id"),
        "answer":head.get("answer_record_id"),"feedback":head.get("feedback_record_id"),"reason":head.get("reason_record_id")}
    result={}
    by_id={str(r["record_id"]):r for r in view.get("current_bodies",view.get("bodies",[]))}
    for region,rid in pointers.items():
        if rid is None: continue
        row=by_id.get(str(rid))
        if row is None:
            result[region]={"qualification":"integrity_error"}
            continue
        qualification,body=public_record(row,view.get("sources",[]),view.get("exposures",[]),head,view["activity"])
        value={"qualification":qualification,"record_id":str(rid),"kind":row["kind"]}
        if body is not None:
            if region=='reason': value["body"]=body
            elif isinstance(body,dict): value.update(body)
            else: value["body"]=body
        result[region]=value
    result["nodes"]=[] if source_invalid(view.get("sources",[])) else projection.get("nodes",[])
    return result
