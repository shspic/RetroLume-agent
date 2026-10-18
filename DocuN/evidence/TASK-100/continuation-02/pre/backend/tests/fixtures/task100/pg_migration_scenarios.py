"""TASK-100 教学迁移真实 PG 场景（续作01 保留式修订）：非空升级、重复拒绝、
前置缺失、约束篡改、中途失败全回滚、权限不足。

资源纪律（续作01 合同）：
  * 不再 DROP/重建任何数据库；fault 库不存在时仅创建一次（限本卡容器）。
  * 反例场景使用 fault 库内显式命名 schema（最多六个），search_path 固定为
    该 schema 本身、不回退 public，防跨 schema 串读；每例数据全部保留。
  * schema 已存在时该场景记 SKIP（保留式设计的预期结果），不删除重建，
    也不假称通过。
  * DSN 全部经环境变量注入，绝不回退用户库；输出一律为布尔事实与对象
    计数，不回显口令。

场景失败即以非零退出，不吞异常：本文件是真实迁移行为的判据。
"""

from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import psycopg

BACKEND = Path(__file__).resolve().parents[3]
M009 = (BACKEND / "migrations" / "009_teaching.sql").read_text(encoding="utf-8")
BASELINE = [
    "001_materials.sql",
    "002_activities.sql",
    "003_pdf_review.sql",
    "004_activities_time_budget.sql",
    "005_activities_dispatch_closed.sql",
    "006_activities_running_owner_session.sql",
    "007_activity_operation_results.sql",
    "008_activity_tool_budget.sql",
]
TEACHING_TABLES = ("teaching_heads", "teaching_commands", "teaching_records")
FAULT_DB = "retrolume_task100_g8_fault"
# 六个显式场景 schema：名称冻结；已存在即保留复用，不清理。
SCHEMA_NAMES = {
    "nonempty": "task100_m01_nonempty",
    "duplicate": "task100_m02_duplicate",
    "missing": "task100_m03_missing",
    "tampered": "task100_m04_tampered",
    "midway": "task100_m05_midway",
    "denied": "task100_m06_denied",
}

RESULTS: list[tuple[str, str, str]] = []  # (name, PASS|FAIL|SKIP, detail)


def record(name: str, ok: bool | None, detail: str = "") -> None:
    verdict = "PASS" if ok is True else ("SKIP" if ok is None else "FAIL")
    RESULTS.append((name, verdict, detail))
    print(f"{verdict} {name} {detail}")


def admin_dsn() -> str:
    value = os.environ.get("RETROLUME_TASK100_ADMIN_DSN", "")
    if not value:
        print("RETROLUME_TASK100_ADMIN_DSN 缺失", file=sys.stderr)
        raise SystemExit(2)
    return value


def super_dsn() -> str:
    value = os.environ.get("RETROLUME_TASK100_PG_SUPER_DSN", "")
    if not value:
        print("RETROLUME_TASK100_PG_SUPER_DSN 缺失", file=sys.stderr)
        raise SystemExit(2)
    return value


def _switch_dbname(dsn: str, dbname: str) -> str:
    """在 URL 或 key-value 两种 DSN 格式下安全切换 dbname（修正#4）。

    旧实现 rpartition("/") 仅适用 URL 格式；key-value 格式（host=...）
    中无 "/"，静默切库失败导致场景跑错库。
    """
    if dsn.strip().startswith("host=") or re.search(r"(?:^|\s)dbname=", dsn):
        if re.search(r"(?:^|\s)dbname=", dsn):
            return re.sub(r"(?:^|\s)dbname=[^\s]+", f" dbname={dbname}", dsn, count=1)
        return f"{dsn} dbname={dbname}"
    head, _, _ = dsn.rpartition("/")
    return f"{head}/{dbname}"


def ensure_fault_database(super_conn_dsn: str) -> str:
    """fault 库不存在时创建一次（owner=admin）；绝不 DROP、绝不重建。

    返回 admin 身份的 fault 库连接串。已存在库核 owner 归属：非本卡
    admin 角色即停止（不触碰他人资源）。
    """
    fault_dsn = _switch_dbname(admin_dsn(), FAULT_DB)
    with psycopg.connect(super_conn_dsn, autocommit=True) as connection:
        row = connection.execute(
            "SELECT pg_get_userbyid(datdba) AS owner FROM pg_database WHERE datname = %s",
            (FAULT_DB,)).fetchone()
        if row is None:
            connection.execute(f'CREATE DATABASE "{FAULT_DB}" OWNER retrolume_task100_admin')
            print(f"fault database {FAULT_DB} created (first use)")
        elif row["owner"] != "retrolume_task100_admin":
            print(f"fault 库 owner 非本卡 admin: {row['owner']}", file=sys.stderr)
            raise SystemExit(3)
        else:
            print(f"fault database {FAULT_DB} exists (preserved)")
    return fault_dsn


def ensure_schema(super_conn_dsn: str, schema: str) -> bool:
    """场景 schema 不存在时创建（owner=admin）；已存在返回 False（保留）。"""
    with psycopg.connect(super_conn_dsn, autocommit=True) as connection:
        exists = connection.execute(
            "SELECT 1 FROM pg_namespace WHERE nspname = %s", (schema,)).fetchone()
        if exists:
            return False
        connection.execute(f'CREATE SCHEMA "{schema}" AUTHORIZATION retrolume_task100_admin')
    return True


def connect_schema(dsn: str, schema: str) -> psycopg.Connection:
    """固定 search_path 为场景 schema 本身；不回退 public，防串读。"""
    return psycopg.connect(dsn, autocommit=True, options=f"-c search_path={schema}")


def apply_baseline(schema: str, migrations: list[str]) -> None:
    with connect_schema(admin_dsn(), schema) as connection:
        for migration in migrations:
            connection.execute((BACKEND / "migrations" / migration).read_text(encoding="utf-8"))


def seed_g7_rows(schema: str) -> dict:
    """写入真实 G7 资料/活动行，验证 009 零回填、零补正文。"""
    with connect_schema(admin_dsn(), schema) as connection:
        source_id = str(uuid.uuid4())
        version_id = str(uuid.uuid4())
        connection.execute(
            "INSERT INTO material_sources (id, title, revision) VALUES (%s, %s, 1)",
            (source_id, "迁移前资料"),
        )
        connection.execute(
            "INSERT INTO material_versions (id, source_id, filename, format, sha256, size) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (version_id, source_id, "legacy.txt", "txt", "a" * 64, 12),
        )
        connection.execute(
            "UPDATE material_sources SET current_version = %s WHERE id = %s",
            (version_id, source_id),
        )
        activity_id = str(uuid.uuid4())
        connection.execute(
            "INSERT INTO activities (id, status, scope_revision, deadline_at, max_requests, "
            "max_cost_microunits, reserve_cost_microunits, max_request_bytes, max_output_tokens, "
            "max_running_seconds) "
            "VALUES (%s, %s, %s, now() + interval '1 hour', %s, %s, %s, %s, %s, %s)",
            (activity_id, "pending", 1, 10, 100000, 1000, 65536, 1024, 600),
        )
        return {"source_id": source_id, "activity_id": activity_id}


def count(schema: str, sql: str, args: tuple = ()) -> int:
    with connect_schema(admin_dsn(), schema) as connection:
        return connection.execute(sql, args).fetchone()[0]


def scenario_nonempty_upgrade(schema: str, fresh: bool) -> None:
    """M-01 非空升级：已有 G7 数据的 schema 上 009 成功，且零回填旧学习行。"""
    if not fresh:
        record("M01_nonempty_upgrade", None, "schema_exists_preserved")
        return
    apply_baseline(schema, BASELINE)
    seed_g7_rows(schema)
    before_activities = count(schema, "SELECT count(*) FROM activities")
    try:
        with connect_schema(admin_dsn(), schema) as connection:
            connection.execute(M009)
        tables = count(
            schema,
            "SELECT count(*) FROM information_schema.tables "
            "WHERE table_schema = current_schema() AND table_name = ANY(%s)",
            (list(TEACHING_TABLES),),
        )
        after_activities = count(schema, "SELECT count(*) FROM activities")
        heads_empty = count(schema, "SELECT count(*) FROM teaching_heads")
        record("M01_nonempty_upgrade_creates_tables", tables == 3, f"tables={tables}")
        record("M01_no_backfill_old_rows",
               before_activities == after_activities and heads_empty == 0,
               f"activities {before_activities}->{after_activities} heads={heads_empty}")
    except Exception as exc:  # noqa: BLE001 - 失败必须显式记录
        record("M01_nonempty_upgrade_creates_tables", False, f"error={type(exc).__name__}: {exc}")


def scenario_duplicate_rejected(schema: str, fresh: bool) -> None:
    """M-02 重复执行：第二次 009 必须整体回滚且不留残迹。"""
    if not fresh:
        record("M02_duplicate_rejected", None, "schema_exists_preserved")
        return
    apply_baseline(schema, BASELINE)
    with connect_schema(admin_dsn(), schema) as connection:
        connection.execute(M009)
    try:
        with connect_schema(admin_dsn(), schema) as connection:
            connection.execute(M009)
        record("M02_duplicate_rejected", False, "second run unexpectedly succeeded")
    except psycopg.errors.RaiseException as exc:
        message = str(exc)
        record("M02_duplicate_rejected", "009" in message, f"reason={message.splitlines()[0][:80]}")
    extra = count(
        schema,
        "SELECT count(*) FROM information_schema.tables "
        "WHERE table_schema = current_schema() AND table_name LIKE 'teaching%'",
    )
    record("M02_no_extra_objects", extra == 3, f"teaching_tables={extra}")


def scenario_missing_prerequisite(schema: str, fresh: bool) -> None:
    """M-03 前置缺失：只有 001—007（无 008）时 009 必须拒绝。"""
    if not fresh:
        record("M03_missing_prerequisite_rejected", None, "schema_exists_preserved")
        return
    apply_baseline(schema, BASELINE[:-1])
    try:
        with connect_schema(admin_dsn(), schema) as connection:
            connection.execute(M009)
        record("M03_missing_prerequisite_rejected", False, "009 accepted without 008")
    except psycopg.errors.RaiseException as exc:
        record("M03_missing_prerequisite_rejected", True, f"reason={str(exc).splitlines()[0][:70]}")
    created = count(
        schema,
        "SELECT count(*) FROM information_schema.tables "
        "WHERE table_schema = current_schema() AND table_name LIKE 'teaching%'",
    )
    record("M03_no_partial_tables", created == 0, f"teaching_tables={created}")


def scenario_tampered_constraint(schema: str, fresh: bool) -> None:
    """M-04 约束被篡改：删掉 008 的 kind 域/形状约束后 009 必须拒绝。"""
    if not fresh:
        record("M04_tampered_constraint_rejected", None, "schema_exists_preserved")
        return
    apply_baseline(schema, BASELINE)
    with connect_schema(admin_dsn(), schema) as connection:
        connection.execute(
            "ALTER TABLE activity_operations DROP CONSTRAINT activity_operations_kind_domain"
        )
    try:
        with connect_schema(admin_dsn(), schema) as connection:
            connection.execute(M009)
        record("M04_tampered_constraint_rejected", False, "009 accepted after constraint drop")
    except psycopg.errors.RaiseException as exc:
        record("M04_tampered_constraint_rejected", "约束" in str(exc) or "constraint" in str(exc).lower(),
               f"reason={str(exc).splitlines()[0][:70]}")
    created = count(
        schema,
        "SELECT count(*) FROM information_schema.tables "
        "WHERE table_schema = current_schema() AND table_name LIKE 'teaching%'",
    )
    record("M04_no_partial_tables", created == 0, f"teaching_tables={created}")


def scenario_midway_failure_rollback(schema: str, fresh: bool) -> None:
    """M-05 中途失败：009 事务中途注入异常，三表与索引必须全部不存在。"""
    if not fresh:
        record("M05_midway_failure_raised", None, "schema_exists_preserved")
        return
    apply_baseline(schema, BASELINE)
    broken = M009.replace(
        "CREATE TABLE teaching_heads (",
        "SELECT 1/0;\nCREATE TABLE teaching_heads (",
        1,
    )
    failed = False
    try:
        with connect_schema(admin_dsn(), schema) as connection:
            connection.execute(broken)
    except psycopg.Error:
        failed = True
    record("M05_midway_failure_raised", failed)
    tables = count(
        schema,
        "SELECT count(*) FROM information_schema.tables "
        "WHERE table_schema = current_schema() AND table_name LIKE 'teaching%'",
    )
    triggers = count(
        schema,
        "SELECT count(*) FROM pg_trigger WHERE NOT tgisinternal "
        "AND tgname IN ('teaching_records_immutable','teaching_command_identity_guard')",
    )
    record("M05_full_rollback", tables == 0 and triggers == 0,
           f"tables={tables} triggers={triggers}")


def scenario_privilege_denied(schema: str, fresh: bool) -> None:
    """M-06 权限不足：denied 角色对教学三表读写必须真实被拒。

    009 自身已 REVOKE ALL FROM PUBLIC；denied 角色从未被授权。本场景
    不再执行 PUBLIC 往返授权（续作01 取消 PUBLIC 临时放权）。
    """
    if not fresh:
        record("M06_denied_role_rejected", None, "schema_exists_preserved")
        return
    denied_dsn = os.environ.get("RETROLUME_TASK100_DENIED_DSN", "")
    if not denied_dsn:
        record("M06_denied_role_rejected", False, "RETROLUME_TASK100_DENIED_DSN 缺失")
        return
    apply_baseline(schema, BASELINE)
    with connect_schema(admin_dsn(), schema) as connection:
        connection.execute(M009)
    checks = []
    for statement in (
        "SELECT count(*) FROM teaching_heads",
        "SELECT count(*) FROM teaching_commands",
        "SELECT count(*) FROM teaching_records",
    ):
        try:
            with connect_schema(denied_dsn, schema) as connection:
                connection.execute(statement)
            checks.append(False)
        except psycopg.Error:
            checks.append(True)
    record("M06_denied_role_rejected", all(checks), f"denied={sum(checks)}/3")
    # denied 场景保留：denied 角色仍无权限、行数据全部保留。


def main() -> int:
    super_conn = super_dsn()
    fault = ensure_fault_database(super_conn)
    print(f"fault_dsn_database={FAULT_DB}")
    # 每个 schema 只判定一次：创建返回 True（本轮 fresh），已存在返回
    # False（保留复用，场景记 SKIP）。禁止二次判定导致首跑误记 SKIP。
    fresh_map = {key: ensure_schema(super_conn, schema) for key, schema in SCHEMA_NAMES.items()}
    for key, schema in SCHEMA_NAMES.items():
        print(f"schema {schema}: {'created' if fresh_map[key] else 'exists_preserved'}")
    scenario_nonempty_upgrade(SCHEMA_NAMES["nonempty"], fresh_map["nonempty"])
    scenario_duplicate_rejected(SCHEMA_NAMES["duplicate"], fresh_map["duplicate"])
    scenario_missing_prerequisite(SCHEMA_NAMES["missing"], fresh_map["missing"])
    scenario_tampered_constraint(SCHEMA_NAMES["tampered"], fresh_map["tampered"])
    scenario_midway_failure_rollback(SCHEMA_NAMES["midway"], fresh_map["midway"])
    scenario_privilege_denied(SCHEMA_NAMES["denied"], fresh_map["denied"])
    passed = sum(1 for _, verdict, _ in RESULTS if verdict == "PASS")
    failed = sum(1 for _, verdict, _ in RESULTS if verdict == "FAIL")
    skipped = sum(1 for _, verdict, _ in RESULTS if verdict == "SKIP")
    print(f"SUMMARY {passed}/{len(RESULTS)} passed ({failed} failed, {skipped} skipped_preserved)")
    for name, verdict, _ in RESULTS:
        if verdict == "FAIL":
            print(f"FAILED_SCENARIO {name}")
    # SKIP（schema 保留）不算失败；FAIL 才非零退出。
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
