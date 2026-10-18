"""API007有限生成/产物/画面/输入/停止，统一沿原本地会话权限。"""
from __future__ import annotations
import secrets
from fastapi import APIRouter,Request,Query
from fastapi.responses import Response
from app.activities.api import _guard,_ledger,_config,_uuid_text
from app.capabilities.contracts import AdmissionUnavailable
from .business_contracts import HtmlCommand,OpenPreview,PreviewInput,StopPreview,HtmlRefusal
from .description import canonical,load_json,DescriptionError
from .generation import HtmlGenerationService

router=APIRouter(prefix="/api/activities")


def reply(value,status=200,maximum=65536):
    data=canonical(value).encode("utf-8")
    if len(data)>maximum:return Response('{"code":"html_response_limit"}',status_code=503,media_type="application/json")
    return Response(data,status_code=status,media_type="application/json")


def error(exc):
    code=exc.code if isinstance(exc,(HtmlRefusal,DescriptionError)) else "html_database_unavailable"
    status=exc.status if isinstance(exc,HtmlRefusal) else 422 if isinstance(exc,DescriptionError) else 503
    return reply({"schema":"html.error.v2","code":code,"retryable":False,
                  "message":exc.message if isinstance(exc,HtmlRefusal) else "交互服务未确认，原学习成果与调用事实保留"},status)


def controller(request):
    value=getattr(request.app.state,"preview_controller",None)
    if value is None or not value.available:raise HtmlRefusal("html_host_not_authorized",status=503)
    return value


async def command_body(request,model,maximum):
    if request.headers.get("content-type","").split(";")[0].strip()!="application/json":raise HtmlRefusal("unsupported_media_type",status=415)
    data=bytearray()
    async for part in request.stream():
        if len(data)+len(part)>maximum:raise HtmlRefusal("html_input_limit",status=413)
        data.extend(part)
    try:return model.model_validate(load_json(data,maximum))
    except (ValueError,TypeError):raise HtmlRefusal("invalid_input",status=422) from None


def identity(request,activity_id):
    _guard(request);return _uuid_text(activity_id,"activity_id")


@router.get("/{activity_id}/html/capabilities")
async def capabilities(request:Request,activity_id:str):
    aid=identity(request,activity_id);control=getattr(request.app.state,"preview_controller",None);config=_config(request)
    enabled=control is not None and control.available and not control.blocked and config.html_generation_layer.available
    return reply({"available":enabled,"reason":None if enabled else "html_host_not_authorized" if control is None else "cleanup_unconfirmed" if control.blocked else config.html_generation_layer.reason,
                  "config_sha256":control.config_sha256 if control is not None else None,"max_starts":3,"max_seconds":180,"max_window":60,
                  "budget":await _ledger(request).html_preview_budget(aid) if enabled else None})


@router.post("/{activity_id}/html/commands")
async def generate(request:Request,activity_id:str):
    aid=identity(request,activity_id)
    try:
        command=await command_body(request,HtmlCommand,8192)
        result=await HtmlGenerationService(_ledger(request),controller(request)).generate(aid,command,_config(request),run_tag="html-"+secrets.token_hex(12))
        return reply(result)
    except (HtmlRefusal,DescriptionError,AdmissionUnavailable) as exc:return error(exc)


@router.get("/{activity_id}/html/commands/{business_key}")
async def read_command(request:Request,activity_id:str,business_key:str):
    aid=identity(request,activity_id);key=_uuid_text(business_key,"business_key")
    try:
        value=await _ledger(request).read_html_command(aid,key)
        return reply(value) if value is not None else error(HtmlRefusal("not_found",status=404))
    except (HtmlRefusal,AdmissionUnavailable) as exc:return error(exc)


@router.get("/{activity_id}/html/artifacts")
async def artifacts(request:Request,activity_id:str,cursor:str|None=None):
    aid=identity(request,activity_id)
    try:
        values=await _ledger(request).list_html_artifacts(aid,cursor)
        return reply({"items":values,"cursor":values[-1]["created_at"] if len(values)==20 else None})
    except (HtmlRefusal,AdmissionUnavailable,ValueError) as exc:return error(exc)


@router.get("/{activity_id}/html/artifacts/{artifact_id}")
async def artifact(request:Request,activity_id:str,artifact_id:str):
    aid=identity(request,activity_id);art=_uuid_text(artifact_id,"artifact_id")
    try:
        value=await _ledger(request).read_html_artifact(aid,art)
        frozen=value.pop("context");value["citations"]=frozen["catalog"];value["parent"]=frozen["parent"]
        return reply(value)
    except (HtmlRefusal,DescriptionError,AdmissionUnavailable) as exc:return error(exc)


@router.post("/{activity_id}/html/artifacts/{artifact_id}/previews")
async def open_preview(request:Request,activity_id:str,artifact_id:str):
    aid=identity(request,activity_id);art=_uuid_text(artifact_id,"artifact_id")
    try:return reply(await controller(request).open(aid,art,await command_body(request,OpenPreview,2048)))
    except (HtmlRefusal,DescriptionError,AdmissionUnavailable) as exc:return error(exc)


@router.get("/{activity_id}/html/previews/{preview_id}")
async def preview_status(request:Request,activity_id:str,preview_id:str):
    aid=identity(request,activity_id);pid=_uuid_text(preview_id,"preview_id")
    try:
        control=getattr(request.app.state,"preview_controller",None)
        if control is not None:value=await control.status(aid,pid,request.headers.get("x-retrolume-preview-owner"))
        else:value=await _ledger(request).read_html_preview(aid,pid);value.pop("owner_key_sha256",None)
        return reply(value)
    except (HtmlRefusal,AdmissionUnavailable) as exc:return error(exc)


@router.get("/{activity_id}/html/previews/{preview_id}/frames")
async def preview_frame(request:Request,activity_id:str,preview_id:str,generation:int=Query(ge=1),after_seq:int=Query(0,ge=0)):
    aid=identity(request,activity_id);pid=_uuid_text(preview_id,"preview_id")
    try:
        packet=await controller(request).frame(aid,pid,generation,after_seq,request.headers.get("x-retrolume-preview-owner",""))
        if packet is None:return Response(status_code=204)
        head,png=packet
        return Response(png,media_type="application/octet-stream",headers={"X-Preview-Id":pid,"X-Preview-Generation":str(generation),
          "X-Artifact-Sha256":head["artifact_sha256"],"X-Frame-Seq":str(head["seq"]),"X-Frame-Sha256":head["body_sha256"],"X-Frame-Width":"640","X-Frame-Height":"480"})
    except (HtmlRefusal,AdmissionUnavailable) as exc:return error(exc)


@router.post("/{activity_id}/html/previews/{preview_id}/inputs")
async def preview_input(request:Request,activity_id:str,preview_id:str):
    aid=identity(request,activity_id);pid=_uuid_text(preview_id,"preview_id")
    try:
        command=await command_body(request,PreviewInput,1024)
        return reply(await controller(request).input(aid,pid,command,request.headers.get("x-retrolume-preview-owner","")))
    except (HtmlRefusal,DescriptionError,AdmissionUnavailable) as exc:return error(exc)


@router.post("/{activity_id}/html/previews/{preview_id}/stop")
async def preview_stop(request:Request,activity_id:str,preview_id:str):
    aid=identity(request,activity_id);pid=_uuid_text(preview_id,"preview_id")
    try:
        command=await command_body(request,StopPreview,1024)
        return reply(await controller(request).stop(aid,pid,command.generation))
    except (HtmlRefusal,AdmissionUnavailable) as exc:return error(exc)
