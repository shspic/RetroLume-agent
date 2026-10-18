"""同源session/DataContext下的显式检索入口，GET始终零模型/Embedding/SUP。"""
from fastapi import APIRouter,Request,HTTPException
from app.activities.api import _ledger,_guard,_uuid_text
from app.memory.contracts import read_bounded_json
from .contracts import RetrievalCommandInput,RetrievalRefusal
from .service import RetrievalService,IntegrationConfig

router=APIRouter(prefix='/api/activities/{activity_id}/retrieval')


def service(request):return RetrievalService(_ledger(request),request.app.state.materials,request.app.state.originals)
def error(exc):return HTTPException(exc.status,detail={'code':exc.code,'message':'本轮资料检索未完成，请核对原操作；已有事实和预留保留'})


@router.get('/status')
async def status(activity_id:str,request:Request):
    _guard(request);activity_id=_uuid_text(activity_id,'activity_id')
    try:return await service(request).status(activity_id,getattr(request.app.state,'integration_config',IntegrationConfig()))
    except RetrievalRefusal as exc:raise error(exc)


@router.post('/commands')
async def submit(activity_id:str,request:Request):
    _guard(request);activity_id=_uuid_text(activity_id,'activity_id')
    try:
        value=await read_bounded_json(request,65536)
        command=RetrievalCommandInput.model_validate(value)
    except (ValueError,TypeError):raise HTTPException(400,detail={'code':'invalid_input','message':'请明确确认有限查询或索引'}) from None
    try:return await service(request).submit(activity_id,command,getattr(request.app.state,'integration_config',IntegrationConfig()))
    except RetrievalRefusal as exc:raise error(exc)


@router.get('/commands/{business_key}')
async def read(activity_id:str,business_key:str,request:Request):
    _guard(request)
    row=await _ledger(request).read_retrieval_command(_uuid_text(activity_id,'activity_id'),_uuid_text(business_key,'business_key'))
    if row is None:raise HTTPException(404,detail={'code':'not_found'})
    return RetrievalService._public(row)
