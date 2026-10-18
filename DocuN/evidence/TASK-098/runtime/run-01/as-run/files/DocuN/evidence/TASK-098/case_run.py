"""一个不同目标并发案例；只在098精确托管入口内运行。"""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import io
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import threading
import time
from uuid import uuid4

from probe_support import ROOT, HERE, RUN, CID, DB, ROLE, ADMIN, docker, event, free, identity, inspect_guard, load, publish, stop_exact

sys.path.insert(0, str(ROOT / "backend"))


def psql(sql, database, secret=False):
    result = docker("exec", "-i", "-e", "PGOPTIONS=-c statement_timeout=10000 -c lock_timeout=2000", CID,
                    "psql", "-X", "-q", "-A", "-t", "-v", "ON_ERROR_STOP=1", "-U", ADMIN, "-d", database, input=sql)
    event("psql", {"database": database, "admin": ADMIN, "exit_code": result.returncode, "secret_stdin": secret})
    if result.returncode:
        raise RuntimeError("098_psql_failed")
    return result.stdout.strip()


def prepare_role():
    owner = load(ROOT / "DocuN/evidence/TASK-097/resource-ownership.json")
    assert owner["task"] == "TASK-097" and owner["container"] == CID
    assert owner["created_db"] == DB and owner["created_role"] == ROLE and owner["schema_initialized"] is True
    facts = json.loads(psql("SELECT json_build_object('db',current_database(),'db_owner',"
        "(SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname=current_database()),"
        "'role',rolname,'login',rolcanlogin,'super',rolsuper,'create_db',rolcreatedb,'create_role',rolcreaterole,"
        "'replication',rolreplication,'bypass_rls',rolbypassrls,'members',(SELECT count(*) FROM pg_auth_members WHERE member=r.oid),"
        "'sessions',(SELECT count(*) FROM pg_stat_activity WHERE usename=r.rolname),"
        "'schema_create',has_schema_privilege(r.rolname,'public','CREATE'),"
        "'table_count',(SELECT count(*) FROM pg_tables WHERE schemaname='public'),"
        "'rw_tables',(SELECT count(*) FROM pg_tables t WHERE schemaname='public' AND "
        "has_table_privilege(r.rolname,quote_ident(t.schemaname)||'.'||quote_ident(t.tablename),'SELECT') AND "
        "has_table_privilege(r.rolname,quote_ident(t.schemaname)||'.'||quote_ident(t.tablename),'INSERT') AND "
        "has_table_privilege(r.rolname,quote_ident(t.schemaname)||'.'||quote_ident(t.tablename),'UPDATE') AND "
        "has_table_privilege(r.rolname,quote_ident(t.schemaname)||'.'||quote_ident(t.tablename),'DELETE'))) "
        "FROM pg_roles r WHERE rolname='" + ROLE + "';", DB))
    assert facts["db"] == DB and facts["db_owner"] == ADMIN and facts["role"] == ROLE and facts["login"]
    assert all(not facts[k] for k in ("super", "create_db", "create_role", "replication", "bypass_rls", "members", "sessions", "schema_create"))
    assert facts["table_count"] == facts["rw_tables"] and facts["table_count"] > 0
    publish("role-db-identity.json", facts)
    password = secrets.token_urlsafe(32)
    psql("ALTER ROLE " + ROLE + " PASSWORD '" + password + "';", "postgres", secret=True)
    return f"host=127.0.0.1 port=55441 dbname={DB} user={ROLE} password={password} connect_timeout=3"


def config():
    return {"model_identity": {"provider": "deepseek_chat_completions", "model": "synthetic-model-098"},
            "activity_defaults": {"deadline_hours": 1, "max_requests": 2, "max_cost_microunits": 200000,
                "reserve_cost_microunits": 100000, "max_request_bytes": 65536, "max_output_tokens": 256,
                "max_running_seconds": 300, "allowed_tools": [], "max_tool_calls": None},
            "service": {"base_url": "https://api.deepseek.com", "thinking": "disabled", "timeout_seconds": 10,
                "max_output_tokens_limit": 256, "max_request_bytes": 65536, "max_response_bytes": 65536},
            "api_key_env": "RETROLUME_TASK098_SYNTH_KEY", "learning": {"profile": "learning.v1", "max_output_tokens": 256}}


def main():
    assert os.environ.get("RETROLUME_TASK098_PERMIT") == "g7-audit-01"
    started = time.monotonic()
    phase = "precheck"
    source = None
    dsn = None
    app = None
    client = None
    app_identity = None
    cleanup_errors = []
    baseline = None
    exit_code = 1
    spec = load(RUN / "case-spec.json")
    try:
        before = inspect_guard()
        assert not before["running"] and before["pid"] == 0
        publish("container-before.json", before)
        for port in (18098, 55441):
            free(port)
        phase = "container_start"
        publish("container-start-attempt-01.json", {"at": time.time(), "id": CID, "permit": "g7-audit-01"})
        result = docker("start", CID)
        if result.returncode:
            raise RuntimeError("098_container_start_failed")
        until = time.monotonic() + 15
        while docker("exec", CID, "pg_isready", "-U", ADMIN, "-d", DB, timeout=4).returncode:
            if time.monotonic() >= until:
                raise TimeoutError("098_pg_not_ready")
            time.sleep(0.2)
        publish("container-running.json", inspect_guard())
        phase = "role_identity_rotation"
        dsn = prepare_role()
        from probe_bootstrap import install_imports
        install_imports()
        import psycopg
        from psycopg.rows import dict_row
        from app.materials.repository import PostgresMaterials
        from app.storage.originals import OriginalStore

        def rows(sql, params=()):
            with psycopg.connect(dsn, row_factory=dict_row, options="-c statement_timeout=10000 -c lock_timeout=2000") as connection:
                cursor = connection.execute(sql, params)
                return cursor.fetchall() if cursor.description else []

        def old_facts():
            facts = {}
            for table in ("activities", "activity_allowed_models", "activity_scope_sources",
                          "activity_operations", "activity_operation_results", "material_sources", "material_versions"):
                values = rows(f"SELECT to_jsonb(t)::text AS body FROM {table} t ORDER BY to_jsonb(t)::text")
                raw = "\n".join(x["body"] for x in values).encode()
                facts[table] = {"rows": len(values), "sha256": hashlib.sha256(raw).hexdigest()}
            return facts

        identity_fact = rows("SELECT current_database() AS db,current_user AS role")[0]
        assert identity_fact == {"db": DB, "role": ROLE}
        publish("business-role-identity.json", identity_fact)
        baseline = old_facts()
        publish("old-business-baseline.json", baseline)
        phase = "synthetic_source"
        original_root = HERE / "runtime/data/originals"
        original_root.mkdir(parents=True, exist_ok=True)
        (HERE / "runtime/backup").mkdir(exist_ok=True)
        raw = ("098 new synthetic activity only.\r\n"
               "Atomicity means all transaction changes commit together or none commit.\r\n"
               "事务原子性表示一起提交或全部不提交。\n").encode()
        original = OriginalStore(original_root).put(io.BytesIO(raw), max_bytes=5242880)
        materials = PostgresMaterials(dsn)
        source = materials.save(source_id=None, expected_version=None,
                                filename="TASK098 " + spec["activity_id"] + ".md", format="md",
                                sha256=original.sha256, size=original.size)
        publish("source-created.json", {"source": source, "original": as_original(original), "root": str(original_root)})
        cfg = HERE / "runtime/synthetic-config.json"
        with cfg.open("x", encoding="utf-8") as stream:
            json.dump(config(), stream, ensure_ascii=False)
        env = {k: v for k, v in os.environ.items() if not k.upper().startswith("RETROLUME_")}
        env.update({"RETROLUME_TASK098_PERMIT": "g7-audit-01", "RETROLUME_DATABASE_URL": dsn,
                    "RETROLUME_DATA_DIR": str(HERE / "runtime/data"), "RETROLUME_BACKUP_DIR": str(HERE / "runtime/backup"),
                    "RETROLUME_ACTIVITY_CONFIG": str(cfg), "RETROLUME_TASK098_SYNTH_KEY": "synthetic-098-only",
                    "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"})
        phase = "http_app_start"
        app = subprocess.Popen([str(ROOT / "backend/.venv/Scripts/python.exe"), "-B", str(HERE / "probe_bootstrap.py"), "app"],
                               cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            app_identity = identity(app.pid)
            assert app_identity is not None
            publish("owned-app.json", {**app_identity, "kind": "app"})
        except BaseException:
            # Popen本身持有真实句柄，记录失败时仍可精确终止，不能按陌生PID猜。
            app.kill()
            app.wait(timeout=10)
            raise
        import httpx
        client = httpx.Client(base_url="http://127.0.0.1:18098", trust_env=False, timeout=160)
        until = time.monotonic() + 25
        while True:
            if app.poll() is not None:
                raise RuntimeError("098_app_early_exit")
            try:
                response = client.get("/api/session", timeout=2)
                if response.status_code == 200:
                    break
            except httpx.TransportError:
                pass
            if time.monotonic() >= until:
                raise TimeoutError("098_app_not_ready")
            time.sleep(0.1)
        client.headers["X-RetroLume-Session"] = response.json()["token"]
        client.headers["Origin"] = "http://127.0.0.1:18098"

        def req(method, path, body=None):
            event("http-request", {"at": time.time(), "method": method, "path": path, "body": body})
            response = client.request(method, path, json=body)
            data = response.json()
            event("http-response", {"at": time.time(), "method": method, "path": path, "status": response.status_code, "body": data})
            return response.status_code, data

        phase = "zero_cost_activity"
        code, created = req("POST", "/api/activities", {"activity_id": spec["activity_id"], "source_ids": [source["id"]]})
        assert code == 200 and created["activity"]["activity_id"] == spec["activity_id"]
        code, initial = req("GET", "/api/activities/" + spec["activity_id"])
        assert code == 200 and initial["activity"]["requests_reserved"] == 0
        publish("activity-before.json", initial)
        phase = "concurrent_first"
        start_gate = threading.Barrier(2)

        def contender(index):
            body = {"business_key": spec["business_keys"][index], "goal": spec["goals"][index], "confirmed": True}
            start_gate.wait(timeout=5)
            return req("POST", "/api/activities/" + spec["activity_id"] + "/learning/first", body)

        with ThreadPoolExecutor(max_workers=2) as pool:
            replies = list(pool.map(contender, (0, 1)))
        publish("competition-http.json", {"goals": spec["goals"], "business_keys": spec["business_keys"], "responses": replies})
        phase = "persistent_readback"
        records = rows("SELECT o.operation_id,o.state,o.disposition,o.error_code,o.execution_generation,"
                       "o.xmin::text AS operation_xmin,r.xmin::text AS result_xmin,r.payload,r.payload_sha256 "
                       "FROM activity_operations o LEFT JOIN activity_operation_results r "
                       "ON r.activity_id=o.activity_id AND r.operation_id=o.operation_id WHERE o.activity_id=%s", (spec["activity_id"],))
        publish("pg-persistent-slot.json", {"rows": records})
        assert len(records) == 1 and records[0]["state"] == "received" and records[0]["disposition"] == "received"
        row = records[0]
        assert row["operation_xmin"] == row["result_xmin"]
        assert hashlib.sha256(row["payload"].encode()).hexdigest() == row["payload_sha256"]
        body = json.loads(row["payload"])["value"]
        winner = spec["goals"].index(body["goal"])
        loser = 1 - winner
        assert replies[winner][0] == 200 and replies[winner][1]["business"]["read_status"] == "committed_current"
        assert replies[loser][0] == 409 or (replies[loser][0] == 200 and replies[loser][1]["business"]["read_status"] != "committed_current")
        assert replies[loser][1].get("operation_id") != row["operation_id"]
        sends = [load(p) for p in RUN.glob("transport-*.json")]
        prepared = [load(p) for p in RUN.glob("candidate-prepared-*.json")]
        sessions = [load(p) for p in RUN.glob("session-*.json")]
        attempts = [load(p) for p in RUN.glob("sup-attempt-*.json")]
        created_sup = [load(p) for p in RUN.glob("sup-created-*.json")]
        resumes = [load(p) for p in RUN.glob("sup-resumed-*.json")]
        assert len(sends) == 1 and len(prepared) == 2 and len(attempts) == 2 and len(created_sup) == len(resumes) == 2
        assert {x["goal"] for x in prepared} == set(spec["goals"])
        assert len(sessions) == 2 and all(not x["cleanup_incomplete"] for x in sessions)
        winner_session = next(x for x in sessions if x["model_receipt"] and x["model_receipt"]["business_commit"] == "committed")
        loser_session = next(x for x in sessions if x is not winner_session)
        assert winner_session["active_processes_at_end"] == 0
        if loser_session["generation"] is not None:
            assert loser_session["active_processes_at_end"] == 0
            receipt = loser_session["model_receipt"]
            assert receipt and receipt["result"]["status"] == "rejected" and receipt["result"]["error_code"] == "learning_input_conflict"
        else:
            assert loser_session["state"] in {"local_owner_busy", "owner_busy", "mutex_busy", "failed_closed"}
            assert loser_session["error_type"] not in {"PermissionError", "JSONDecodeError"}
        fact = req("GET", "/api/activities/" + spec["activity_id"])[1]
        assert fact["activity"]["requests_reserved"] == 1 and fact["activity"]["cost_reserved_microunits"] == 100000
        assert fact["activity"]["running_reserved_seconds"] == 0
        reads = []
        for key in spec["business_keys"]:
            reads.append(req("GET", f"/api/activities/{spec['activity_id']}/learning/intents/{key}?action=first"))
        assert all(x[0] == 200 and x[1]["operation"]["operation_id"] == row["operation_id"] for x in reads)
        from app.worker.windows_job import NamedJob, JobOpenError, ERROR_FILE_NOT_FOUND
        job_reads = []
        for session in sessions:
            if session["generation"] is None:
                continue
            try:
                job = NamedJob.open_existing(spec["activity_id"], session["generation"])
            except JobOpenError as exc:
                assert exc.code == ERROR_FILE_NOT_FOUND
                job_reads.append({"generation": session["generation"], "error": exc.code, "exists": False})
            else:
                try:
                    active = job.active_processes()
                    assert active == 0
                    job_reads.append({"generation": session["generation"], "exists": True, "active": active})
                finally:
                    job.close()
        publish("job-readback.json", job_reads)
        publish("competition-checks.json", {"status": "PASS", "activity": spec["activity_id"], "winner_goal": body["goal"],
                "winner_operation": row["operation_id"], "winner_index": winner, "loser_index": loser,
                "send_count": len(sends), "prepared_count": len(prepared), "sup_attempts": len(attempts),
                "actual_created": len(created_sup), "actual_resumed": len(resumes), "sessions": sessions,
                "activity_after": fact, "atomic_xmin": row["operation_xmin"], "payload_sha256": row["payload_sha256"],
                "zero_external_transport": True, "real_cost": 0})
        exit_code = 0
    except BaseException as exc:
        event("case-failure", {"phase": phase, "type": type(exc).__name__, "at": time.time()})
    finally:
        business_seconds = time.monotonic() - started
        cleanup_started = time.monotonic()
        if client is not None:
            try:
                client.close()
            except BaseException as exc:
                cleanup_errors.append("http_client:" + type(exc).__name__)
        if app is not None:
            try:
                if app_identity is not None:
                    stopped = stop_exact(app_identity)
                    publish("app-stop.json", stopped)
                    assert stopped["zero"]
                else:
                    app.kill()
                app.wait(timeout=10)
            except BaseException as exc:
                cleanup_errors.append("app:" + type(exc).__name__)
        if dsn is not None:
            try:
                import psycopg
                with psycopg.connect(dsn, options="-c statement_timeout=10000 -c lock_timeout=2000") as connection:
                    for table in ("activity_operation_results", "activity_operations", "activity_allowed_models", "activity_scope_sources"):
                        connection.execute(f"DELETE FROM {table} WHERE activity_id=%s", (spec["activity_id"],))
                    connection.execute("DELETE FROM activities WHERE id=%s", (spec["activity_id"],))
                    if source is not None:
                        connection.execute("UPDATE material_sources SET current_version=NULL WHERE id=%s", (source["id"],))
                        connection.execute("DELETE FROM material_versions WHERE source_id=%s", (source["id"],))
                        connection.execute("DELETE FROM material_sources WHERE id=%s", (source["id"],))
                    remaining = connection.execute("SELECT count(*) FROM activities WHERE id=%s", (spec["activity_id"],)).fetchone()[0]
                    assert remaining == 0
                publish("fk-cleanup.json", {"activity_id": spec["activity_id"], "source_id": None if source is None else source["id"],
                                          "transaction_committed": True, "remaining_activity_rows": remaining, "originals_retained": True})
                if baseline is not None:
                    after = old_facts()
                    same = after == baseline
                    publish("old-business-after.json", {"facts": after, "matches_baseline": same})
                    assert same
            except BaseException as exc:
                cleanup_errors.append("fk:" + type(exc).__name__)
        publish("case-run-result.json", {"exit_code": exit_code, "phase": phase, "business_seconds": business_seconds,
                "cleanup_seconds": time.monotonic() - cleanup_started, "cleanup_errors": cleanup_errors,
                "cleanup_ok": not cleanup_errors})
        if cleanup_errors:
            exit_code = 1
    return exit_code


def as_original(original):
    return {"sha256": original.sha256, "size": original.size}


if __name__ == "__main__":
    raise SystemExit(main())
