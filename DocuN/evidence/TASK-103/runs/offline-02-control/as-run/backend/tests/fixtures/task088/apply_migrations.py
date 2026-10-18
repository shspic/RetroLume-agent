"""TASK-088 迁移应用步骤：按序应用 001—006 与 007 到本卡合成库 public schema。

DSN 仅经 RETROLUME_TASK088_DSN 环境变量注入；不回退任何用户库。
输出仅对象计数，不回显口令。重复执行会报 duplicate 并失败（007 无 IF NOT EXISTS），
本步骤只在全新合成库上运行一次。
"""

from __future__ import annotations

import os
from pathlib import Path
import sys

import psycopg

BACKEND = Path(__file__).resolve().parents[3]
MIGRATIONS = [
    "001_materials.sql",
    "002_activities.sql",
    "003_pdf_review.sql",
    "004_activities_time_budget.sql",
    "005_activities_dispatch_closed.sql",
    "006_activities_running_owner_session.sql",
    "007_activity_operation_results.sql",
]


def main() -> int:
    dsn = os.environ.get("RETROLUME_TASK088_DSN", "")
    if not dsn:
        print("RETROLUME_TASK088_DSN 缺失", file=sys.stderr)
        return 2
    with psycopg.connect(dsn, autocommit=True) as connection:
        row = connection.execute("SELECT current_database(), current_user, current_setting('search_path')").fetchone()
        print(f"identity database={row[0]} user={row[1]} search_path={row[2]}")
        for name in MIGRATIONS:
            connection.execute((BACKEND / "migrations" / name).read_text(encoding="utf-8"))
            print(f"applied {name}")
        count = connection.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'"
        ).fetchone()[0]
        results = connection.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'activity_operation_results'"
        ).fetchone()[0]
        print(f"public tables={count} activity_operation_results={results}")
        return 0 if results == 1 else 1


if __name__ == "__main__":
    raise SystemExit(main())
