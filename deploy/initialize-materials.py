"""只在明确批准的新数据库执行；启动应用不会自动迁移。"""
import os
from pathlib import Path

if __name__ == "__main__":
    dsn = os.environ.get("RETROLUME_DATABASE_URL")
    if not dsn:
        raise SystemExit("请在本地设置RETROLUME_DATABASE_URL，不要把连接凭据发送到对话")
    try:
        import psycopg
    except ImportError:
        raise SystemExit("尚未安装获批的psycopg驱动") from None
    migration = Path(__file__).resolve().parents[1] / "backend/migrations/001_materials.sql"
    try:
        with psycopg.connect(dsn, connect_timeout=3, autocommit=True) as connection:
            connection.execute(migration.read_text(encoding="utf-8"))
    except psycopg.Error:
        raise SystemExit("初始化未完成；请在本机检查数据库及迁移状态，不自动重试或输出凭据") from None
    print("资料表初始化完成")
