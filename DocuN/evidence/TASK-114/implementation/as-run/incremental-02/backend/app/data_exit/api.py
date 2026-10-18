"""本地会话下的显式数据动作，查询与刷新始终只读。"""
import asyncio
import os
import time
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, ConfigDict, Field
from app.local_session import local_session
from .contracts import DataError, DataJobCommand, PROFILE, uuid
from .packages import PackageReader
from .files import publish
from .snapshot import validate_scope

router = APIRouter(prefix="/api/data")


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")


class JobInput(Input):
    kind: str
    business_key: str = Field(max_length=128)
    scope: dict = Field(default_factory=lambda: {"mode": "all"})
    confirm: bool


class PlanInput(Input):
    upload_id: str
    deletion_policy: str = "respect_current_deletions"


class ScopeInput(Input):
    scope:dict


class RestoreInput(Input):
    plan_id: str
    expected_plan_sha256: str
    business_key: str = Field(max_length=128)
    confirm: bool
    acknowledge_unknown_deletions: bool = False


class ActivateInput(Input):
    expected_plan_sha256: str
    business_key: str = Field(max_length=128)
    expected_selection_generation: int
    confirm: bool


class PreviewInput(Input):
    expected_revision: int


class DeleteInput(PreviewInput):
    impact_sha256: str
    business_key: str = Field(max_length=128)
    confirm: bool


def runtime(request):
    local_session(request, allow_own_origin=True)
    value = getattr(request.app.state, "data_exit", None)
    if value is None: raise DataError("storage_unavailable", 503)
    return value


def schedule(value, identity, function, *args):
    if identity in value.tasks: return
    async def work():
        try: await asyncio.to_thread(function, *args)
        except (Exception, asyncio.CancelledError) as error:
            # 获取操作锁之前的失败也须有收据，不能无限留 prepared。
            try:
                receipt=value.hub.get(identity)
                if receipt['state'] in ('prepared','running'):
                    value.hub.update_job(identity,receipt['revision'],state='failed',stage='failed',
                        error_code=error.code if isinstance(error,DataError) else 'storage_unavailable')
            except (DataError,OSError):pass
        finally: value.tasks.pop(identity, None)
    value.tasks[identity] = asyncio.create_task(work())


@router.get("/capabilities")
def capabilities(request: Request):
    local_session(request, allow_own_origin=True)
    value = getattr(request.app.state, "data_exit", None)
    if value is None:
        return {"format": PROFILE, "current_mode": "unavailable", "read_only": bool(getattr(request.app.state, "data_exit_error", None)),
                "backup_available": False, "restore_executor_configured": False, "browser_drafts_included": False}
    return value.caps()


@router.post("/jobs", status_code=202)
async def jobs(body: JobInput, request: Request):
    value = runtime(request)
    if not body.confirm or body.kind not in ("portable_export", "restore_checkpoint"): raise DataError("invalid_input", 400)
    if value.packages is None: raise DataError("snapshot_configuration_missing", 503)
    scope = validate_scope(body.scope, body.kind)
    try: existing = value.hub.get_by_key(body.business_key)
    except DataError as error:
        if error.status != 404: raise
        existing = None
    receipt = value.hub.create_or_get_job(DataJobCommand(body.kind, body.business_key, scope), value.context())
    if existing is None: schedule(value, receipt["job_id"], value.packages.capture_and_publish, receipt["job_id"], scope)
    return receipt


@router.post('/scope-preview')
async def scope_preview(body:ScopeInput,request:Request):
    value=runtime(request)
    if value.packages is None:raise DataError('snapshot_configuration_missing',503)
    return await run_in_threadpool(value.packages.snapshot.preview_scope,body.scope)


@router.get("/jobs/by-key/{business_key}")
def by_key(business_key: str, request: Request): return runtime(request).hub.get_by_key(business_key)


@router.get("/jobs/{job_id}")
def get_job(job_id: str, request: Request):
    value = runtime(request)
    job = value.hub.get(job_id)
    return value.packages.reconcile(job_id) if job["kind"] in ("portable_export", "restore_checkpoint") and value.packages else value.hub.reconcile(job_id)


@router.get("/packages")
def packages(request: Request):
    value = runtime(request)
    return {"items": [value.hub.receipt(j) for j in value.hub.state()["jobs"].values()
                      if j["kind"] in ("portable_export", "restore_checkpoint") and j["state"] in ("published", "published_unconfirmed")]}


@router.get('/saved-records')
async def saved_records(request:Request,category:str='activities',offset:int=0):
    value=runtime(request)
    if offset<0:raise DataError('invalid_input',400)
    mapping={'activities':'activities','learning':'activity_operation_results','teaching':'teaching_records',
             'interview':'interview_records','memories':'learning_memory_revisions','preview_history':'html_preview_sessions','versions':'material_versions'}
    table=mapping.get(category)
    if table is None:raise DataError('invalid_input',400)
    def read():
        from .repository import DataRepository
        from .schema import COLUMNS
        from .codec import encode_row
        ledger=request.app.state.activities_ledger
        if ledger is None:raise DataError('storage_unavailable',503)
        repository=DataRepository(ledger._dsn)
        columns=','.join(COLUMNS[table])
        with repository.connection(readonly=True,repeatable=True) as connection:
            rows=connection.execute('SELECT '+columns+' FROM public.'+table+' ORDER BY '+','.join(list(COLUMNS[table])[:2])+' LIMIT 20 OFFSET %s',(offset,)).fetchall()
            items=[]
            for row in rows:
                item=encode_row(table,row);availability='present'
                aid=row.get('activity_id')
                if aid is not None:
                    deleted=connection.execute("""SELECT EXISTS(SELECT 1 FROM public.activity_scope_sources s JOIN public.data_tombstones t
                      ON t.entity_kind='source' AND t.entity_id=s.source_id WHERE s.activity_id=%s) AS deleted""",(aid,)).fetchone()['deleted']
                    if deleted:
                        availability='source_deleted'
                        for name in ('body','payload','local_body','source_refs','state_after'):
                            if name in item:item[name]=None
                if table=='learning_memory_revisions':
                    head=connection.execute('SELECT state FROM public.learning_memories WHERE memory_id=%s',(row['memory_id'],)).fetchone()
                    body=connection.execute('SELECT body FROM public.learning_memory_bodies WHERE memory_id=%s AND version=%s',(row['memory_id'],row['version'])).fetchone()
                    item['body']=body['body'] if body is not None and head['state']=='active' else None
                    availability='revoked' if head['state']=='revoked' else 'present' if body else 'unavailable'
                items.append({'record':item,'availability':availability})
        return {'items':items,'next_offset':offset+len(items) if len(items)==20 else None,
                'accounting_point':'snapshot_observation','execution_frozen':value.context().mode!='normal'}
    return await run_in_threadpool(read)


@router.get("/packages/{package_id}/content")
async def content(package_id: str, request: Request):
    value = runtime(request)
    if value.packages is None: raise DataError("storage_unavailable", 503)
    path = await run_in_threadpool(value.packages.download, package_id)
    return FileResponse(path, media_type="application/octet-stream", filename=package_id + ".rldata")


@router.post("/uploads", status_code=201)
async def upload(request: Request, business_key:str, upload_id:str, expected_sha256:str, expected_bytes:int):
    value = runtime(request)
    import hashlib,re
    identity = uuid(upload_id)
    if not re.fullmatch(r'[0-9a-f]{64}',expected_sha256) or not 0<expected_bytes<=value.limits.package_bytes:raise DataError('invalid_input',400)
    command=DataJobCommand('upload',business_key,{'upload_id':identity,'sha256':expected_sha256,'bytes':str(expected_bytes)})
    try:existing=value.hub.get_by_key(business_key)
    except DataError as error:
        if error.status!=404:raise
        existing=None
    receipt=value.hub.create_or_get_job(command,value.context())
    if existing is not None:
        return {**value.hub.reconcile(receipt['job_id']),'upload_id':identity}
    temporary, destination = value.incoming / (identity + ".pending"), value.incoming / (identity + ".rldata")
    count, start = 0, time.monotonic()
    h=hashlib.sha256()
    try:
        with temporary.open("xb") as stream:
            async with asyncio.timeout(value.limits.upload_seconds):
                async for raw in request.stream():
                    count += len(raw)
                    if count > value.limits.package_bytes: raise DataError("capacity_exceeded", 413)
                    h.update(raw)
                    stream.write(raw)
                stream.flush(); os.fsync(stream.fileno())
        if count!=expected_bytes or h.hexdigest()!=expected_sha256:raise DataError('integrity_failed',422)
        def check_and_publish():
            with PackageReader(temporary, value.limits): pass
            publish(temporary, destination)
        await run_in_threadpool(check_and_publish)
        current=value.hub.get(receipt['job_id'])
        value.hub.update_job(receipt['job_id'],current['revision'],state='received',stage='received',counts={'bytes':str(count)})
        return {"upload_id": identity, "job_id":receipt['job_id'],"business_key":business_key,"bytes": str(count), "state": "received"}
    except TimeoutError:
        current=value.hub.get(receipt['job_id'])
        value.hub.update_job(receipt['job_id'],current['revision'],state='upload_unconfirmed',stage='upload_unconfirmed',error_code='operation_timeout')
        raise DataError("operation_timeout", 504) from None
    except BaseException as error:
        current=value.hub.get(receipt['job_id'])
        value.hub.update_job(receipt['job_id'],current['revision'],state='upload_unconfirmed',stage='upload_unconfirmed',
                             error_code=error.code if isinstance(error,DataError) else 'storage_unavailable')
        raise


@router.post("/restore-plans")
async def plans(body: PlanInput, request: Request):
    value = runtime(request)
    return await run_in_threadpool(value.restore.prepare, body.upload_id, body.deletion_policy, value.context())


@router.get('/restore-plans/{plan_id}')
def get_plan(plan_id:str,request:Request):
    value=runtime(request)
    record=value.hub.state()['plans'].get(uuid(plan_id))
    if record is None:raise DataError('not_found',404)
    value.restore.plan(plan_id,record['plan_sha256'])
    return record['public']


@router.post("/restore-jobs", status_code=202)
async def restore_jobs(body: RestoreInput, request: Request):
    value = runtime(request)
    if value.factory is None: raise DataError("restore_executor_missing", 503)
    if not body.confirm: raise DataError("invalid_input", 400)
    plan = value.restore.plan(body.plan_id, body.expected_plan_sha256)
    if plan["latest_status"] != "known" and not body.acknowledge_unknown_deletions: raise DataError("deletion_history_unknown")
    try: existing = value.hub.get_by_key(body.business_key)
    except DataError as error:
        if error.status != 404: raise
        existing = None
    receipt = value.hub.create_or_get_job(DataJobCommand("restore", body.business_key,
        {"plan_id": body.plan_id, "plan_sha256": body.expected_plan_sha256}), value.context())
    if existing is None: schedule(value, receipt["job_id"], value.restore.verify, receipt["job_id"], body.expected_plan_sha256)
    return receipt


@router.post("/restore-jobs/{job_id}/activate-readonly")
async def activate(job_id: str, body: ActivateInput, request: Request):
    value = runtime(request)
    if not body.confirm: raise DataError("invalid_input", 400)
    return await value.restore.activate_readonly(job_id, body.expected_plan_sha256, body.business_key, body.expected_selection_generation)


@router.post("/jobs/{job_id}/cancel")
def cancel(job_id: str, request: Request):
    value = runtime(request)
    job = value.hub.get(job_id)
    if job["state"] not in ("prepared", "running"): raise DataError("operation_already_published")
    return value.hub.update_job(job_id, job["revision"], state="cancelled", stage="cancel_requested")


class RetryInput(Input):
    confirm:bool


@router.post('/jobs/{job_id}/retry-cleanup')
async def retry_cleanup(job_id:str,body:RetryInput,request:Request):
    value=runtime(request)
    if not body.confirm:raise DataError('invalid_input',400)
    if value.deletions is None:raise DataError('data_readonly')
    return await value.deletions.retry_cleanup(job_id)


@router.post("/materials/{source_id}/deletion-preview")
async def deletion_preview(source_id: str, body: PreviewInput, request: Request):
    value = runtime(request)
    if value.deletions is None: raise DataError("data_readonly")
    return await run_in_threadpool(value.deletions.preview, source_id, body.expected_revision)


@router.post("/materials/{source_id}/deletions")
async def deletion(source_id: str, body: DeleteInput, request: Request):
    value = runtime(request)
    if value.deletions is None: raise DataError("data_readonly")
    if not body.confirm: raise DataError("invalid_input", 400)
    return await value.deletions.confirm(source_id, body.expected_revision, body.impact_sha256, body.business_key)
