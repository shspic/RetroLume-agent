"""仅提供本地工程就绪检查；不连接业务服务。"""
import os
import secrets
from pathlib import Path
from fastapi import FastAPI
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
from app.service_config import load_activity_config

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
    settings = Settings(**values)
    a, b = settings.data_dir, settings.backup_dir
    if a == b or a in b.parents or b in a.parents:
        raise ValueError("资料与备份目录必须独立")
    return settings

def create_app(materials=None) -> FastAPI:
    settings = load_settings()
    app = FastAPI(title="RetroLume development", docs_url=None, redoc_url=None, openapi_url=None)
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
    dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if dist.is_dir():
        app.mount("/", StaticFiles(directory=dist, html=True), name="frontend")
    return app
