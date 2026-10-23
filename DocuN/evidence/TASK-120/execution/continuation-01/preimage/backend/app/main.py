"""仅提供本地工程就绪检查；不连接业务服务。"""
import os
import secrets
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, field_validator
from fastapi.staticfiles import StaticFiles
from app.storage.originals import OriginalStore
from app.materials.api import router
from app.pdf_review.api import router as pdf_review_router
from app.materials.repository import PostgresMaterials
from app.activities import PostgresAdmissionLedger
from app.activities.api import router as activities_router
from app.learning.api import router as learning_router
from app.learning.teaching_api import router as teaching_router
from app.retrieval.api import router as retrieval_router
from app.retrieval.service import load_integration_config
from app.memory.api import router as memory_router
from app.interview.api import router as interview_router
from app.service_config import load_activity_config
from app.preview.api import router as preview_router
from app.preview.host_policy import load_host_policy
from app.preview.production_supervisor import PreviewController
from app.data_exit.api import router as data_router
from app.data_exit.contracts import DataError, canonical
from contextlib import asynccontextmanager

class Settings(BaseModel):
    data_dir: Path
    backup_dir: Path

    @field_validator("data_dir", "backup_dir")
    @classmethod
    def existing_directory(cls, value: Path) -> Path:
        if not value.is_absolute() or not value.is_dir():
            raise ValueError("必须是已存在的绝对目录")
        return value.resolve()

def load_settings() -> Settings:
    values = {}
    for field, env in (("data_dir", "RETROLUME_DATA_DIR"), ("backup_dir", "RETROLUME_BACKUP_DIR")):
        value = os.environ.get(env)
        if not value:
            raise RuntimeError(f"缺少本地配置：{env}")
        values[field] = value
        if os.environ.get('RETROLUME_DATA_EXIT_CONFIG'):
            from app.data_exit.files import safe_root
            safe_root(Path(value))
    settings = Settings(**values)
    a, b = settings.data_dir, settings.backup_dir
    if a == b or a in b.parents or b in a.parents:
        raise ValueError("资料与备份目录必须独立")
    return settings

def create_app(materials=None) -> FastAPI:
    settings = load_settings()
    @asynccontextmanager
    async def lifespan(application):
        control=application.state.preview_controller
        data=application.state.data_exit
        if control is not None and (data is None or data.context().mode=='normal'):await control.recover()
        try:yield
        finally:
            if control is not None:await control.close()
    app = FastAPI(title="RetroLume development", docs_url=None, redoc_url=None, openapi_url=None,lifespan=lifespan)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "testserver"])

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "mode": "development"}

    originals_root = settings.data_dir / "originals"
    originals_root.mkdir(exist_ok=True)
    app.state.originals = OriginalStore(originals_root)
    app.state.session_token = secrets.token_urlsafe(32)
    dsn = os.environ.get("RETROLUME_DATABASE_URL")
    app.state.materials = materials if materials is not None else (PostgresMaterials(dsn) if dsn else None)
    # G6 活动账本独立失败关闭：DSN 缺失或非法只让活动面不可用，不影响资料入口。
    ledger = None
    if dsn:
        try:
            ledger = PostgresAdmissionLedger(dsn)
        except ValueError:
            ledger = None
    app.state.activities_ledger = ledger
    config_path = os.environ.get("RETROLUME_ACTIVITY_CONFIG") or str(
        Path(__file__).resolve().parents[2] / "config" / "activity.local.json"
    )
    app.state.activity_config = load_activity_config(Path(config_path))
    app.state.integration_config=load_integration_config(os.environ.get('RETROLUME_INTEGRATION_CONFIG'))
    from dataclasses import replace
    from app.service_config import LayerState
    from app.capabilities.transport import HttpxModelTransport
    activity_config=app.state.activity_config
    embedding_service=app.state.integration_config.service
    grant=embedding_service.outbound_grant if embedding_service else None
    if grant and activity_config.model_service:
        app.state.activity_config=replace(activity_config,model_service=activity_config.model_service.model_copy(update={'outbound_grant':grant,'outbound_source_manifest':embedding_service.outbound_source_manifest}))
    elif HttpxModelTransport.is_external:
        closed=LayerState(False,'outbound_not_authorized')
        app.state.activity_config=replace(activity_config,continue_layer=closed,learning_layer=closed,teaching_layer=closed,interview_model_layer=closed,html_generation_layer=closed)
    preview_path=os.environ.get("RETROLUME_PREVIEW_CONFIG")
    policy=load_host_policy(preview_path,settings.data_dir/"preview-control") if preview_path else None
    app.state.preview_policy=policy
    app.state.preview_controller=PreviewController(ledger,policy) if policy is not None and ledger is not None and not os.environ.get('RETROLUME_DATA_EXIT_CONFIG') else None
    app.state.data_exit=None
    app.state.data_exit_error=None
    try:
        from app.data_exit.config import load_profile, DataRuntime
        profile=load_profile()
        if profile is not None:
            app.state.data_exit=DataRuntime(app,settings,profile)
        elif app.state.preview_controller is None and policy is not None and ledger is not None:
            app.state.preview_controller=PreviewController(ledger,policy)
    except (DataError,OSError,ValueError) as error:
        app.state.data_exit_error=error.code if isinstance(error,DataError) else 'storage_unavailable'
        # 选择或私有凭据不明时不可回退旧源。
        app.state.materials=None
        app.state.activities_ledger=None
        app.state.preview_controller=None

    app.state.q_readiness={'available':False,'reason':'q_disabled','real_outbound_authorized':False}
    if grant and grant.get('schema')=='retrolume.outbound-grant.v2':
        try:
            from app.operator.q_request import configure_application
            q_path=os.environ.get('RETROLUME_Q_APPROVAL_CONFIG')
            if not q_path:raise DataError('q_control_missing')
            app.state.q_readiness=configure_application(app,q_path)
        except (DataError,OSError,ValueError) as error:
            closed=LayerState(False,'q_readiness_unknown')
            app.state.activity_config=replace(app.state.activity_config,continue_layer=closed,learning_layer=closed,
                teaching_layer=closed,interview_model_layer=closed,html_generation_layer=closed)
            app.state.integration_config=replace(app.state.integration_config,reason='q_readiness_unknown')
            app.state.q_readiness={'available':False,'reason':'q_readiness_unknown','real_outbound_authorized':False}

    async def data_error(request,error):
        from fastapi.responses import JSONResponse
        messages={'data_readonly':'当前数据仅供只读查看，不能继续调用或修改',
                  'selection_changed':'当前数据已切换，请刷新后核对',
                  'request_conflict':'同一操作编号已绑定不同内容',
                  'snapshot_changed':'资料版本或删除影响已改变，请重新核对后确认',
                  'maintenance_unconfirmed':'原工作收尾尚未确认，当前数据未切换',
                  'source_deleted':'此资料及全部版本的回查内容已删除',
                  'package_incomplete':'备份内容不完整，不能用于完整恢复',
                  'integrity_failed':'内容损坏或完整性核对失败',
                  'restore_executor_missing':'隔离恢复尚未配置',
                  'deletion_history_unknown':'无法核对最新删除历史，请明确按备份时点只读验证',
                  'capacity_exceeded':'本次内容超过明确的数据操作限额',
                  'invalid_input':'输入无效', 'not_found':'记录不存在'}
        return JSONResponse({'detail':messages.get(error.code,'本次操作未完成，请核对操作记录；已有数据保留'),'code':error.code},status_code=error.status)
    app.add_exception_handler(DataError,data_error)

    @app.middleware('http')
    async def selection_guard(request,call_next):
        data=app.state.data_exit
        original_context=None
        try:
            if data is not None:
                original_context=data.context()
                if request.url.path.startswith('/api/') and not request.url.path.startswith('/api/data/') and request.method not in ('GET','HEAD','OPTIONS'):
                    from app.local_session import local_session
                    local_session(request,allow_own_origin=True)
                    expected=canonical(original_context.public())
                    if request.headers.get('x-retrolume-data-context')!=expected:
                        raise DataError('selection_changed')
                    if 'q' in data.hub.state():
                        # Q takes policy at domain/PG boundaries; an HTTP permit
                        # carried across SUP would block its own lease and result.
                        with data.gate.acquire(expected=original_context):pass
                        response=await call_next(request)
                        if data.context()!=original_context:raise DataError('selection_changed')
                    else:
                        with data.gate.acquire(expected=original_context):
                            response=await call_next(request)
                else:response=await call_next(request)
            elif app.state.data_exit_error and request.url.path.startswith('/api/') and not request.url.path.startswith('/api/data/') and request.url.path!='/api/session':
                raise DataError('mode_unknown',503)
            else:response=await call_next(request)
            if original_context is not None:
                response.headers['X-RetroLume-Data-Context']=canonical(original_context.public())
            return response
        except DataError as error:return await data_error(request,error)
        except HTTPException as error:
            from fastapi.responses import JSONResponse
            return JSONResponse({'detail':error.detail},status_code=error.status_code)
    @app.middleware("http")
    async def no_store_api(request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    app.include_router(router)
    app.include_router(pdf_review_router)
    app.include_router(activities_router)
    app.include_router(learning_router)
    app.include_router(teaching_router)
    app.include_router(retrieval_router)
    app.include_router(memory_router)
    app.include_router(interview_router)
    app.include_router(preview_router)
    app.include_router(data_router)
    dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if dist.is_dir():
        app.mount("/", StaticFiles(directory=dist, html=True), name="frontend")
    return app
