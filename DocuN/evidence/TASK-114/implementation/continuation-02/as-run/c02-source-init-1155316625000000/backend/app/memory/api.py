"""本地会话保护的有限记忆HTTP面，所有GET只读。"""
from __future__ import annotations
from fastapi import APIRouter,Request,HTTPException
from pydantic import ValidationError
from .contracts import MemoryCommandInput,MemoryRefusal,bounded_json,uuid_text,read_bounded_json
from .service import MemoryService
from app.local_session import local_session

router=APIRouter(prefix="/api")


def _guard(request):
    local_session(request,allow_own_origin=True)


def _service(request):
    ledger=getattr(request.app.state,"activities_ledger",None)
    if ledger is None:raise MemoryRefusal("memory_unavailable","学习记忆存储尚未配置",503)
    return MemoryService(ledger)


def _error(exc):
    if isinstance(exc,MemoryRefusal):
        return HTTPException(exc.status,{"code":exc.code,"message":exc.message})
    if isinstance(exc,(ValidationError,ValueError,UnicodeError)):
        return HTTPException(400,{"code":"invalid_input","message":"输入身份或内容不可核对"})
    return HTTPException(503,{"code":"memory_unavailable","message":"记忆状态未确认，请只读核对"})


@router.get("/memories/capabilities")
async def capabilities(request:Request):
    _guard(request)
    try:return await _service(request).capabilities()
    except Exception as exc:raise _error(exc) from None


@router.get("/memories/commands/{business_key}")
async def command_receipt(request:Request,business_key:str):
    _guard(request)
    try:
        row=await _service(request).ledger.read_memory_command(uuid_text(business_key))
        if row is None:raise MemoryRefusal("memory_not_found","尚未发现该动作收据",404)
        return bounded_json(row)
    except Exception as exc:raise _error(exc) from None


@router.post("/memories/commands")
async def submit_command(request:Request):
    _guard(request)
    try:
        command=MemoryCommandInput.model_validate(await read_bounded_json(request))
        return await _service(request).submit_command(command)
    except Exception as exc:raise _error(exc) from None


@router.get("/memories")
async def list_memories(request:Request,limit:int=20,cursor:str|None=None):
    _guard(request)
    try:return bounded_json(await _service(request).ledger.read_memory_snapshot(limit=limit,cursor_token=cursor))
    except Exception as exc:raise _error(exc) from None


@router.get("/memories/{memory_id}/impact")
async def preview_change(request:Request,memory_id:str,expected_revision:int,action:str):
    _guard(request)
    try:
        if action not in ("revise","revoke"):raise ValueError()
        return bounded_json(await _service(request).ledger.preview_memory_change(uuid_text(memory_id),expected_revision,action))
    except Exception as exc:raise _error(exc) from None


@router.get("/memories/{memory_id}")
async def read_memory(request:Request,memory_id:str,version:int|None=None):
    _guard(request)
    try:
        if version is not None and not 1<=version<=32:raise ValueError()
        result=await _service(request).ledger.read_memory_snapshot(uuid_text(memory_id),version=version)
        if result is None:raise MemoryRefusal("memory_not_found","记忆不存在",404)
        return bounded_json(result)
    except Exception as exc:raise _error(exc) from None


@router.get("/activities/{activity_id}/memory-selection")
async def read_selection(request:Request,activity_id:str):
    _guard(request)
    try:
        aid=uuid_text(activity_id)
        result=await _service(request).ledger.read_memory_selection(aid)
        return bounded_json({"activity_id":aid,**result})
    except Exception as exc:raise _error(exc) from None


@router.get("/activities/{activity_id}/teaching/records/{record_id}/memory-preview")
async def preview_observation(request:Request,activity_id:str,record_id:str):
    _guard(request)
    try:return bounded_json(await _service(request).ledger.preview_memory_observation(uuid_text(activity_id),uuid_text(record_id)))
    except Exception as exc:raise _error(exc) from None

