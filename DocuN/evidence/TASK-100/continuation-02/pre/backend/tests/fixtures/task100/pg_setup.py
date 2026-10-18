"""TASK-100 合成 PG 初始化：建库建角色并按序应用 001—009。

只用本卡固定镜像的超级用户连接串（RETROLUME_TASK100_PG_SUPER_DSN），
不回退任何用户 DSN；DSN 不回显，输出一律为对象计数与布尔事实。

两个库：
  main  —— 正常升级路径，001—009 顺序全量应用。
  fault —— 只到 008，用于 009 的前置缺失/约束被篡改/重复执行拒绝场景。

角色（密码取自环境变量，不落盘）：
  retrolume_task100_admin   —— 迁移执行者，本卡产品连接身份
  retrolume_task100_app     —— 应用连接身份，仅授 DML 所需
  retrolume_task100_denied  —— 故意不授 teaching 三表任何权限

本文件永不进入产品导入链。
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import psycopg

BACKEND = Path(__file__).resolve().parents[3]
_SAFE_ROLE = re.compile(r"^[a-z_][a-z0-9_]{0,62}$")
MIGRATIONS = [
    "001_materials.sql",
    "002_activities.sql",
    "003_pdf_review.sql",
    "004_activities_time_budget.sql",
    "005_activities_dispatch_closed.sql",
    "006_activities_running_owner_session.sql",
    "007_activity_operation_results.sql",
    "008_activity_tool_budget.sql",
]
TEACHING_MIGRATION = "009_teaching.sql"

ADMIN_ROLE = "retrolume_task100_admin"
APP_ROLE = "retrolume_task100_app"
DENIED_ROLE = "retrolume_task100_denied"

TEACHING_TABLES = ("teaching_heads", "teaching_commands", "teaching_records")


def _require(env_name: str) -> str:
    value = os.environ.get(env_name, "")
    if not value:
        print(f"{env_name} 缺失", file=sys.stderr)
        raise SystemExit(2)
    return value


def _sanitize(dsn: str) -> str:
    """仅用于打印身份，绝不打印口令。"""
    head = dsn.split("?", 1)[0]
    return head.rsplit("/", 1)[-1]


def create_roles(admin_dsn: str) -> None:
    passwords = {
        ADMIN_ROLE: _require("RETROLUME_TASK100_PW_ADMIN"),
        APP_ROLE: _require("RETROLUME_TASK100_PW_APP"),
        DENIED_ROLE: _require("RETROLUME_TASK100_PW_DENIED"),
    }
    with psycopg.connect(admin_dsn, autocommit=True) as connection:
        for role, password in passwords.items():
            # 角色名/口令是本卡固定字面量常量，不含引号；仍用标识符引号防注入。
            if not _SAFE_ROLE.match(role):
                print(f"非法角色名: {role}", file=sys.stderr)
                return 1
            connection.execute(
                f"DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{role}') "
                f"THEN EXECUTE format('CREATE ROLE %I LOGIN PASSWORD %L', '{role}', "
                f"'{password}'); END IF; END $$;"
            )
        # 应用身份需要建表/建索引/建触发器权限以跑迁移；不授 SUPERUSER。
        connection.execute(f"GRANT ALL ON SCHEMA public TO {ADMIN_ROLE}")
        print("roles ready: " + ", ".join(sorted(passwords)))


def grant_table_privileges(admin_dsn: str) -> None:
    """教学三表建成后授应用身份最小权限（099 第 4 节批准口径）。

    records：仅 SELECT/INSERT——不可变事实无 UPDATE/DELETE。
    heads/commands：SELECT/INSERT + 状态机列白名单 UPDATE（列级授权）。
    commands 身份列（request_body/slot/父引用/retry_of/created_at 等）
    不在白名单，数据库层面直接拒绝改写。
    denied 角色刻意不授任何教学表权限。
    app 角色需要产品运行期真实写入的旧表 DML，但不给 DDL/SUPERUSER/CREATE。
    """
    runtime_tables = [
        "activities", "activity_scope_sources", "activity_allowed_models",
        "activity_operations", "activity_operation_results",
        "material_sources", "material_versions",
        "pdf_review_candidates", "pdf_extracted_pages", "pdf_review_pages",
        "pdf_user_supplements",
    ]
    HEAD_UPDATE_COLS = (
        "revision, goal_version, last_seq, phase, goal_record_id, path_record_id, "
        "node_id, exercise_record_id, answer_record_id, feedback_record_id, "
        "reason_record_id, pending_business_key, projection, updated_at"
    )
    COMMAND_UPDATE_COLS = (
        "status, launch_claimed_at, obsolete_at, abandoned_at, result_record_id, "
        "error_code, operation_id, updated_at"
    )
    with psycopg.connect(admin_dsn, autocommit=True) as connection:
        present = connection.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_name LIKE 'teaching%%' ORDER BY table_name"
        ).fetchall()
        teaching_names = [r[0] for r in present]
        for table in teaching_names:
            connection.execute(f"GRANT SELECT, INSERT ON {table} TO {APP_ROLE}")
        if "teaching_heads" in teaching_names:
            connection.execute(
                f"GRANT UPDATE ({HEAD_UPDATE_COLS}) ON teaching_heads TO {APP_ROLE}")
        if "teaching_commands" in teaching_names:
            connection.execute(
                f"GRANT UPDATE ({COMMAND_UPDATE_COLS}) ON teaching_commands TO {APP_ROLE}")
        for table in runtime_tables:
            connection.execute(
                f"GRANT SELECT, INSERT, UPDATE, DELETE ON {table} TO {APP_ROLE}")
        # PUBLIC 对教学三表无任何访问（009 REVOKE 后不得再放大）。
        connection.execute(
            "REVOKE ALL ON teaching_heads, teaching_commands, teaching_records FROM PUBLIC")
        print("teaching granted (records=select,insert): " + ",".join(sorted(teaching_names)))
        print("runtime granted: " + ",".join(runtime_tables))
        # denied 角色对教学三表必须无任何权限（权限不足场景的真实前提）。
        leaked = connection.execute(
            "SELECT count(*) FROM information_schema.role_table_grants "
            "WHERE table_schema = 'public' AND table_name LIKE 'teaching%%' "
            "AND grantee = %s", (DENIED_ROLE,)
        ).fetchone()[0]
        print(f"denied_role_teaching_grants={leaked}")
        # records 不得有任何 UPDATE/DELETE 授权（含列级）。
        records_writable = connection.execute(
            "SELECT count(*) FROM information_schema.role_table_grants "
            "WHERE table_schema='public' AND table_name='teaching_records' "
            "AND grantee=%s AND privilege_type IN ('UPDATE','DELETE')", (APP_ROLE,)
        ).fetchone()[0]
        print(f"app_records_writable_privileges={records_writable}")
        return 1 if (leaked != 0 or records_writable != 0) else 0


def create_database(super_dsn: str, name: str) -> None:
    with psycopg.connect(super_dsn, autocommit=True) as connection:
        exists = connection.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (name,)
        ).fetchone()
        if exists:
            print(f"database {name} already exists (reused)")
            return
        # 库 owner=admin：PG17 的 public schema 权限随 owner 走，迁移必须以
        # admin 身份真实执行，不靠超级权限旁路。
        connection.execute(
            f'CREATE DATABASE "{name}" OWNER retrolume_task100_admin')
        print(f"database {name} created (owner=retrolume_task100_admin)")


def apply_migrations(admin_dsn: str, upto: str | None) -> None:
    with psycopg.connect(admin_dsn, autocommit=True) as connection:
        row = connection.execute(
            "SELECT current_database(), current_user, inet_server_port()"
        ).fetchone()
        print(f"identity database={row[0]} user={row[1]} port={row[2]}")
        for name in MIGRATIONS:
            connection.execute((BACKEND / "migrations" / name).read_text(encoding="utf-8"))
            print(f"applied {name}")
        if upto == TEACHING_MIGRATION:
            connection.execute((BACKEND / "migrations" / TEACHING_MIGRATION).read_text(encoding="utf-8"))
            print(f"applied {TEACHING_MIGRATION}")
        tables = connection.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_name LIKE 'teaching%%' ORDER BY table_name"
        ).fetchall()
        present = [r[0] for r in tables]
        print("teaching tables=" + (",".join(present) if present else "(none)"))
        if upto == TEACHING_MIGRATION and sorted(present) != sorted(TEACHING_TABLES):
            print("teaching migration incomplete", file=sys.stderr)
            return 1
        return 0


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "roles":
        return create_roles(_require("RETROLUME_TASK100_PG_SUPER_DSN"))
    if mode == "create":
        name = _require("RETROLUME_TASK100_DB_NAME")
        return create_database(_require("RETROLUME_TASK100_PG_SUPER_DSN"), name)
    if mode == "migrate":
        upto = sys.argv[2] if len(sys.argv) > 2 else None
        return apply_migrations(_require("RETROLUME_TASK100_ADMIN_DSN"), upto)
    if mode == "grant":
        return grant_table_privileges(_require("RETROLUME_TASK100_ADMIN_DSN"))
    print("usage: pg_setup.py roles|create|migrate [009_teaching.sql]|grant", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
