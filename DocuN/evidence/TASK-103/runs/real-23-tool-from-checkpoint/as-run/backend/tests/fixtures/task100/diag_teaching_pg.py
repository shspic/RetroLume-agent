"""TASK-100 临时诊断：直连合成库跑一次教学本地提交，打印真实异常。

只读诊断用途：定位 _transaction 吞掉的原始错误。不改产品、不做断言。
"""
import asyncio
import os
import sys
import traceback
from pathlib import Path
from uuid import uuid4

BACKEND = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(BACKEND))

import psycopg  # noqa: E402
from psycopg.rows import dict_row  # noqa: E402

from app.learning.teaching_contracts import GoalBody, TeachingCommandInput  # noqa: E402
from tests.fixtures.task100.support import DSN, Fixture  # noqa: E402


async def main() -> int:
    fixture = Fixture(DSN, Path(os.environ.get("TEMP", ".")) / "retrolume-task100-originals")
    source = fixture.text("平均速度 = 路程 ÷ 时间。2 分钟走 120 米，120 米 ÷ 120 秒 = 1 米/秒。\n")
    # 原始错误探测：用 admin 身份（真实迁移身份）建全新 ledger 实例，
    # 定位是权限不足还是产品逻辑问题。_transaction 会把 psycopg.Error 统一
    # 收敛成 AdmissionUnavailable，所以这里直接用 psycopg 复现同一条语句。
    admin_dsn = os.environ.get("RETROLUME_TASK100_ADMIN_DSN", "")
    if not admin_dsn:
        print("DIAG_SKIP no admin dsn")
        fixture.cleanup()
        return 1
    import psycopg as _psycopg
    with _psycopg.connect(admin_dsn, autocommit=True) as connection:
        try:
            connection.execute(
                "INSERT INTO activities (id, status, scope_revision, deadline_at, max_requests, "
                "max_cost_microunits, reserve_cost_microunits, max_request_bytes, "
                "max_output_tokens, max_running_seconds) "
                "VALUES (%s, 'pending', 1, now() + interval '1 hour', 16, 1600000, 100000, "
                "65536, 2048, 900)", (str(uuid4()),))
            print("RAW_INSERT_OK admin can insert activities")
        except Exception:
            traceback.print_exc()
    with _psycopg.connect(DSN, autocommit=True) as connection:
        try:
            connection.execute(
                "INSERT INTO activities (id, status, scope_revision, deadline_at, max_requests, "
                "max_cost_microunits, reserve_cost_microunits, max_request_bytes, "
                "max_output_tokens, max_running_seconds) "
                "VALUES (%s, 'pending', 1, now() + interval '1 hour', 16, 1600000, 100000, "
                "65536, 2048, 900)", (str(uuid4()),))
            print("RAW_INSERT_OK app can insert activities")
        except Exception:
            print("APP_RAW_INSERT_FAILED")
            traceback.print_exc()
    # 逐条复刻 create_activity 内部语句，定位真实失败点。
    with _psycopg.connect(DSN, autocommit=True) as connection:
        activity_id = str(uuid4())
        try:
            connection.execute(
                """INSERT INTO activities(
                       id, status, scope_revision, execution_generation, deadline_at,
                       max_requests, max_cost_microunits, reserve_cost_microunits,
                       max_request_bytes, max_output_tokens,
                       max_running_seconds, running_reserved_seconds, running_settled_seconds,
                       allowed_tools, max_tool_calls)
                     VALUES (%s, 'pending', %s, 0, %s, %s, %s, %s, %s, %s, %s, 0, 0, %s, %s)""",
                (activity_id, 1, "2026-10-03T12:00:00+00:00", 16, 1600000, 100000,
                 65536, 2048, 900, [], None))
            print("STEP activities OK")
            connection.execute(
                "INSERT INTO activity_allowed_models(activity_id, provider, model) "
                "VALUES (%s, %s, %s)", (activity_id, "deepseek_chat_completions",
                                          "synthetic-model-100"))
            print("STEP allowed_models OK")
        except Exception:
            print("STEP_FAILED")
            traceback.print_exc()
    # 直接调 ledger._lock_sources 观察真实失败（不被 _transaction 收敛）。
    from app.activities import SourceSnapshot
    snapshot = SourceSnapshot(source["id"], source["version_id"], source["revision"])
    print("source_row", source)

    # 复刻 _transaction 的三句 SET，复现真实 psycopg.Error。
    try:
        connection = await _psycopg.AsyncConnection.connect(DSN, connect_timeout=5)
        async with connection:
            async with connection.transaction():
                await connection.execute(
                    "SELECT set_config('statement_timeout', %s, true)", ("15000ms",))
                await connection.execute(
                    "SELECT set_config('lock_timeout', %s, true)", ("3000ms",))
                await connection.execute(
                    "SET LOCAL idle_in_transaction_session_timeout = '5s'")
                ok = await fixture.ledger._lock_sources(
                    connection, [snapshot])
                print("LOCK_SOURCES", ok)
        await connection.close()
    except Exception as exc:
        print("RAW_TRANSACTION_REPLICA_FAILED", type(exc).__name__, str(exc)[:400])

    activity = await fixture.activity([source])
    print("activity", activity)
    body = GoalBody(goal="能正确换算平均速度并说明数量级", self_report=None, domain=None,
                    seed_operation_id=None, seed_payload_sha256=None)
    command = TeachingCommandInput(
        business_key=str(uuid4()), expected_revision=0, expected_goal_version=0,
        expected_scope_revision=1, action="goal", body=body.model_dump())
    async def probe(connection):
        cursor = await connection.execute("SELECT 1")
        print("probe", await cursor.fetchone())
    try:
        await fixture.ledger._transaction(probe)
        print("TRANSACTION_OK")
    except Exception:
        traceback.print_exc()
    try:
        receipt = await fixture.ledger.apply_teaching_local(activity, command)
        print("RECEIPT", receipt)
    except Exception:
        traceback.print_exc()
    with psycopg.connect(DSN, row_factory=dict_row) as connection:
        rows = connection.execute(
            "SELECT * FROM teaching_heads WHERE activity_id=%s", (activity,)).fetchall()
        print("HEAD", rows)
    fixture.cleanup()
    return 0


if __name__ == "__main__":
    # 必须用产品同款 loop_factory：Windows 默认 ProactorEventLoop 不能跑 psycopg 异步。
    import os as _os
    from app.runtime import psycopg_compatible_loop_factory
    _target = _os.environ.get("RETROLUME_TASK100_DIAG_TARGET", "ledger")
    if _target == "raw":
        import psycopg as _p
        from psycopg.rows import dict_row as _dr
        with _p.connect(DSN, row_factory=_dr) as _c:
            _row = _c.execute(
                "SELECT current_database() AS db, current_user AS role").fetchone()
            print("RAW_IDENTITY", dict(_row))
    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:
        raise SystemExit(runner.run(main()))
