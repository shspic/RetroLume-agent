"""TASK-095 批次1：真实合成 PG 准备 + 定向读取/API 契约测试。

仅使用精确旧合成容器（白名单核对后启动）；只创建 retrolume_task095_g6
与 retrolume_task095_synth，不触碰旧库与用户库。凭据随机、经 stdin 传递，
不进入 argv 或日志。批末停止容器并核对 Running=false/Pid=0。
"""
from __future__ import annotations

import json
import secrets
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common  # noqa: E402

BATCH = "1-pg-http"
OUT = HERE / "batch1"
OUT.mkdir(exist_ok=True)
MIGRATIONS = common.ROOT / "backend" / "migrations"
ADMIN = "retrolume_task088_synth"  # 原合成管理通道（088/092 沿用）


def run_psql(sql: str, *, database: str, user: str, label: str,
             tuples_only: bool = False) -> subprocess.CompletedProcess:
    extra = ["-t", "-A"] if tuples_only else []
    result = subprocess.run(
        ["docker", "exec", "-i", "-e",
         "PGOPTIONS=-c statement_timeout=10000 -c lock_timeout=2000",
         common.NAME, "psql", "-X", "-q", "-v", "ON_ERROR_STOP=1", *extra,
         "-U", user, "-d", database],
        input=sql, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
    )
    (OUT / f"{label}.out.txt").write_text(
        f"returncode={result.returncode}\n---stdout---\n{result.stdout}\n---stderr---\n{result.stderr}",
        encoding="utf-8",
    )
    return result


def main() -> int:
    started = time.monotonic()
    try:
        facts = common.inspect_guard()
        assert facts["state_running"] is False, f"container unexpectedly running: {facts}"
    except BaseException as exc:
        common.append_attempt({
            "batch": BATCH, "phase": "guard-failed", "container_starts": 0,
            "error": f"{type(exc).__name__}: {exc}"[:200],
        })
        raise
    common.append_attempt({
        "batch": BATCH, "phase": "start", "guard": facts,
        "note": "pre-batch container state verified stopped before start",
    })
    business_start = time.monotonic()
    common.start_container()

    probe = run_psql(
        "SELECT json_build_object("
        "'role_exists',(SELECT count(*) FROM pg_roles WHERE rolname='retrolume_task095_synth'),"
        "'db_exists',(SELECT count(*) FROM pg_database WHERE datname='retrolume_task095_g6'),"
        "'sessions',(SELECT count(*) FROM pg_stat_activity WHERE usename='retrolume_task095_synth'))",
        database="postgres", user=ADMIN, label="preflight-probe", tuples_only=True,
    )
    existing = json.loads(probe.stdout.strip())
    adopted = False
    migration_outputs = []
    if existing == {"role_exists": 0, "db_exists": 0, "sessions": 0}:
        password = secrets.token_urlsafe(24)
        sql = (
            "DO $$ BEGIN\n"
            "  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname='retrolume_task095_synth')\n"
            "     OR EXISTS (SELECT 1 FROM pg_database WHERE datname='retrolume_task095_g6') THEN\n"
            "    RAISE EXCEPTION 'task095 objects already exist';\n"
            "  END IF;\n"
            "END $$;\n"
            f"CREATE ROLE retrolume_task095_synth LOGIN PASSWORD '{password}'"
            " NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;\n"
            "CREATE DATABASE retrolume_task095_g6 OWNER retrolume_task095_synth;\n"
        )
        created = run_psql(sql, database="postgres", user=ADMIN, label="create-role-db")
        if created.returncode != 0:
            print("ROLE/DB CREATE FAILED")
            stopped = common.stop_container()
            common.append_attempt({
                "batch": BATCH, "phase": "abort", "container_starts": 1,
                "reason": "create role/db failed", "container_after": stopped,
            })
            return 1
        for name in ("001_materials.sql", "002_activities.sql", "003_pdf_review.sql",
                     "004_activities_time_budget.sql", "005_activities_dispatch_closed.sql",
                     "006_activities_running_owner_session.sql", "007_activity_operation_results.sql",
                     "008_activity_tool_budget.sql"):
            text = (MIGRATIONS / name).read_text(encoding="utf-8")
            result = run_psql(text, database=common.DB, user=common.ROLE, label=f"migration-{name}")
            migration_outputs.append({"migration": name, "returncode": result.returncode})
            if result.returncode != 0:
                print(f"MIGRATION FAILED: {name}")
                stopped = common.stop_container()
                common.append_attempt({
                    "batch": BATCH, "phase": "abort", "container_starts": 1,
                    "reason": f"migration {name} failed", "container_after": stopped,
                })
                return 1
        dsn = f"postgresql://{common.ROLE}:{password}@127.0.0.1:55441/{common.DB}"
        (common.RUNTIME / "dsn.json").write_text(
            json.dumps({"dsn": dsn, "note": "TASK-095 synthetic only; removed at final cleanup"}, ensure_ascii=False),
            encoding="utf-8",
        )
    else:
        # 本卡自建对象的复用：需本卡证据（attempt-ledger 创建记录 + dsn.json）与身份/权限/模式核对。
        own_evidence = (common.RUNTIME / "dsn.json").is_file()
        identity = json.loads(run_psql(
            "SELECT json_build_object("
            "'owner',(SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname='retrolume_task095_g6'),"
            "'role',(SELECT json_build_array(rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls,rolinherit) FROM pg_roles WHERE rolname='retrolume_task095_synth'),"
            "'memberships',(SELECT count(*) FROM pg_auth_members WHERE member=(SELECT oid FROM pg_roles WHERE rolname='retrolume_task095_synth')),"
            "'sessions',(SELECT count(*) FROM pg_stat_activity WHERE usename='retrolume_task095_synth'))",
            database="postgres", user=ADMIN, label="adopt-identity", tuples_only=True,
        ).stdout.strip())
        schema = json.loads(run_psql(
            "SELECT json_build_object("
            "'tables',(SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
            "WHERE n.nspname='public' AND c.relname IN ('material_sources','material_versions','pdf_review_candidates',"
            "'activities','activity_scope_sources','activity_operations','activity_operation_results')),"
            "'tool_budget',(SELECT count(*) FROM information_schema.columns WHERE table_name='activities' "
            "AND column_name IN ('max_tool_calls','tools_reserved')),"
            "'kind',(SELECT count(*) FROM information_schema.columns WHERE table_name='activity_operations' "
            "AND column_name IN ('kind','arguments_sha256','tool_call_id')))",
            database=common.DB, user=common.ROLE, label="adopt-schema", tuples_only=True,
        ).stdout.strip())
        ok_identity = (
            existing == {"role_exists": 1, "db_exists": 1, "sessions": 0}
            and own_evidence
            and identity["owner"] == common.ROLE
            and identity["role"] == [True, False, False, False, False, False, False]
            and identity["memberships"] == 0
            and identity["sessions"] == 0
            and schema == {"tables": 7, "tool_budget": 2, "kind": 3}
        )
        if not ok_identity:
            stopped = common.stop_container()
            common.append_attempt({
                "batch": BATCH, "phase": "abort", "container_starts": 1,
                "reason": "task095 objects exist but adoption checks failed",
                "preflight": existing, "identity": identity, "schema": schema,
                "own_evidence": own_evidence, "container_after": stopped,
            })
            print("PREFLIGHT OBJECT CONFLICT")
            return 1
        adopted = True
        migration_outputs = [{"adopted": True, "reused_existing_schema": True}]
        dsn = common.read_dsn()
    config = {
        "model_identity": {"provider": "deepseek_chat_completions", "model": "synthetic-model-095"},
        "activity_defaults": {
            "deadline_hours": 24, "max_requests": 8, "max_cost_microunits": 800_000,
            "reserve_cost_microunits": 100_000, "max_request_bytes": 65536,
            "max_output_tokens": 256, "max_running_seconds": 600,
            "allowed_tools": [], "max_tool_calls": None,
        },
        "service": {
            "base_url": "https://api.deepseek.com", "thinking": "disabled",
            "timeout_seconds": 10, "max_output_tokens_limit": 8192,
            "max_request_bytes": 65536, "max_response_bytes": 65536,
        },
        "api_key_env": "RETROLUME_TEST095_KEY",
    }
    (common.RUNTIME / "activity.local.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )

    env = common.os.environ.copy()
    env["RETROLUME_WORKSPACE_TEST_DATABASE_URL"] = dsn
    env.pop("RETROLUME_DATABASE_URL", None)
    env.pop("RETROLUME_DATA_DIR", None)
    env.pop("RETROLUME_BACKUP_DIR", None)
    tests = subprocess.run(
        [str(common.PY), "-m", "unittest", "-v",
         "tests.test_activity_workspace_reads", "tests.test_activity_workspace_api"],
        cwd=common.ROOT / "backend", env=env,
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900,
    )
    (OUT / "unittest.out.txt").write_text(
        f"returncode={tests.returncode}\n---stdout---\n{tests.stdout}\n---stderr---\n{tests.stderr}",
        encoding="utf-8",
    )
    tail = (tests.stdout + tests.stderr).strip().splitlines()[-3:]
    ok = tests.returncode == 0 and "OK" in " ".join(tail)
    skipped = "skipped" in " ".join(tail)
    business_seconds = round(time.monotonic() - business_start, 3)

    cleanup_start = time.monotonic()
    stopped = common.stop_container()
    cleanup_seconds = round(time.monotonic() - cleanup_start, 3)
    common.append_attempt({
        "batch": BATCH, "phase": "end", "adopted_existing": adopted,
        "container_starts": 1, "pg_batches": 1, "windows_sessions": 0,
        "business_seconds": business_seconds, "cleanup_seconds": cleanup_seconds,
        "migrations": migration_outputs,
        "tests": {"returncode": tests.returncode, "tail": tail, "skipped_present": skipped},
        "container_after": stopped,
        "result": "pass" if (ok and not skipped) else "fail",
    })
    print(json.dumps({
        "batch": BATCH, "ok": ok, "skipped": skipped, "tail": tail,
        "business_seconds": business_seconds, "cleanup_seconds": cleanup_seconds,
        "container_after": stopped,
    }, ensure_ascii=False))
    return 0 if ok and not skipped else 1


if __name__ == "__main__":
    raise SystemExit(main())
