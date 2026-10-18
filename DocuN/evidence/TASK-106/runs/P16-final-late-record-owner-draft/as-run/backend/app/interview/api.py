"""Local-session six-route interface. GET never claims or executes a command."""
from __future__ import annotations
import secrets
from fastapi import APIRouter,Request,Query
from fastapi.responses import Response
from app.activities.api import _guard,_ledger,_config,_uuid_text
from app.capabilities.contracts import AdmissionUnavailable
from .contracts import InterviewCommandInput,InterviewRefusal,load_json,MAX_COMMAND
from .views import bounded_wire
from .service import InterviewService

router=APIRouter(prefix='/api/activities')


def service(request):
    return InterviewService(_ledger(request),getattr(request.app.state,'materials',None),request.app.state.originals,
        session_config=getattr(request.app.state,'interview_session_config',None))


def reply(value,maximum=65536,status=200):
    return Response(bounded_wire(value,maximum),status_code=status,media_type='application/json')


def error(exc):
    code=exc.code if isinstance(exc,InterviewRefusal) else 'database_unavailable'
    status=(exc.status if isinstance(exc,InterviewRefusal) else None) or (404 if code=='not_found' else 422 if code=='interview_invalid_input' else
        413 if code=='interview_snapshot_limit' else 503 if code in ('interview_schema_not_ready','interview_not_configured','interview_config_invalid','interview_model_unavailable','database_unavailable') else 409)
    return reply(dict(schema='interview.error.v1',code=code,retryable=False,receipt=None,view_token=None,
        message=exc.message if isinstance(exc,InterviewRefusal) else '持久服务暂不可用；请核对原提交结果，不会自动重发'),status=status)


@router.post('/{activity_id}/interview/commands')
async def submit(request:Request,activity_id:str):
    _guard(request);activity_id=_uuid_text(activity_id,'activity_id')
    if request.headers.get('content-type','').split(';')[0].strip()!='application/json':return reply({'schema':'interview.error.v1','code':'unsupported_media_type','retryable':False},status=415)
    raw=bytearray()
    async for part in request.stream():
        if len(raw)+len(part)>MAX_COMMAND:return error(InterviewRefusal('interview_invalid_input','命令超过32768字节',413))
        raw.extend(part)
    try:command=InterviewCommandInput.model_validate(load_json(raw.decode('utf-8')))
    except (ValueError,TypeError,RecursionError):return error(InterviewRefusal('interview_invalid_input','命令字段、类型或正文非法',422))
    try:
        result=await service(request).submit_command(activity_id,command,_config(request),run_tag='interview-'+secrets.token_hex(12))
        return reply(result,status=202 if result['status'] in ('accepted','started','unknown') else 200)
    except (InterviewRefusal,AdmissionUnavailable) as exc:return error(exc)


@router.get('/{activity_id}/interview/workspace')
async def workspace(request:Request,activity_id:str):
    _guard(request);activity_id=_uuid_text(activity_id,'activity_id')
    try:return reply(await service(request).read_workspace(activity_id,_config(request)),131072)
    except (InterviewRefusal,AdmissionUnavailable) as exc:return error(exc)


@router.get('/{activity_id}/interview/commands/{business_key}')
async def command(request:Request,activity_id:str,business_key:str):
    _guard(request);activity_id=_uuid_text(activity_id,'activity_id');business_key=_uuid_text(business_key,'business_key')
    try:
        result=await _ledger(request).read_interview_command(activity_id,business_key)
        return reply(result) if result is not None else error(InterviewRefusal('not_found','命令不存在',404))
    except (InterviewRefusal,AdmissionUnavailable) as exc:return error(exc)


@router.get('/{activity_id}/interview/history')
async def history(request:Request,activity_id:str,limit:int=Query(20,ge=1,le=50),before_seq:int|None=Query(None,ge=1,le=4097),view_token:str|None=None):
    _guard(request);activity_id=_uuid_text(activity_id,'activity_id')
    try:return reply(await _ledger(request).read_interview_history(activity_id,limit,before_seq,view_token))
    except (InterviewRefusal,AdmissionUnavailable) as exc:return error(exc)


@router.get('/{activity_id}/interview/records/{record_id}')
async def record(request:Request,activity_id:str,record_id:str,view_token:str|None=None):
    _guard(request);activity_id=_uuid_text(activity_id,'activity_id');record_id=_uuid_text(record_id,'record_id')
    try:return reply(await _ledger(request).read_interview_record(activity_id,record_id,view_token))
    except (InterviewRefusal,AdmissionUnavailable) as exc:return error(exc)


@router.get('/{activity_id}/interview/records/{record_id}/citations/{citation_id}')
async def citation(request:Request,activity_id:str,record_id:str,citation_id:str,view_token:str|None=None):
    _guard(request);activity_id=_uuid_text(activity_id,'activity_id');record_id=_uuid_text(record_id,'record_id')
    try:return reply(await service(request).read_citation(activity_id,record_id,citation_id,view_token))
    except (InterviewRefusal,AdmissionUnavailable) as exc:return error(exc)
