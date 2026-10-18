"""TASK-095 批次3（最终合并入口）：PG API 复验 + Windows 监督链 + 全量浏览器检查。

在批次2已修复（bootstrap95 参数、事件循环策略、同键用例构造）后一次完成：
  A. PG API 契约文件复验（全绿门）；
  B. 真实 launcher/SUP/worker/Job 链：正常继续、同键复查、并发同键、预检查后
     竞争失败再显式同键重试；受控替身传输，外网 0；
  C. 浏览器：继续动作端到端 + 工作区完整流（能力分层、界面新建、响应丢失恢复、
     409 核验、显式同键重试、取消、损坏台账闸门、原资料与 PDF 分支回归）。
"""
from __future__ import annotations

import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "backend"))
import common  # noqa: E402

BATCH = "3-pg-win-browser-final"
OUT = HERE / "batch3"
OUT.mkdir(exist_ok=True)
ADMIN = "retrolume_task088_synth"
APP_URL = f"http://127.0.0.1:{common.APP_PORT}"
WIN_TITLE = "TASK095-WIN"
WS_TITLE = "TASK095-WS"


def log_step(steps: list, name: str, ok: bool, **extra) -> None:
    steps.append({"step": name, "ok": ok, **extra})
    (OUT / "steps.json").write_text(json.dumps(steps, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[{name}] {'ok' if ok else 'FAIL'}")


def docker_psql(sql: str, *, database: str, user: str, label: str, tuples_only: bool = False):
    extra = ["-t", "-A"] if tuples_only else []
    result = subprocess.run(
        ["docker", "exec", "-i", "-e", "PGOPTIONS=-c statement_timeout=10000 -c lock_timeout=2000",
         common.NAME, "psql", "-X", "-q", "-v", "ON_ERROR_STOP=1", *extra, "-U", user, "-d", database],
        input=sql, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60,
    )
    (OUT / f"{label}.out.txt").write_text(
        f"returncode={result.returncode}\n---stdout---\n{result.stdout}\n---stderr---\n{result.stderr}",
        encoding="utf-8",
    )
    return result


def q(dsn: str, sql: str, params=()):
    import psycopg
    from psycopg.rows import dict_row
    with psycopg.connect(dsn, row_factory=dict_row) as connection:
        return connection.execute(sql, params).fetchall()


def exec_sql(dsn: str, sql: str, params=()) -> None:
    import psycopg
    with psycopg.connect(dsn) as connection:
        connection.execute(sql, params)


def http(url: str, *, token=None, method="GET", payload=None, timeout=120.0):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, method=method)
    if token:
        request.add_header("X-RetroLume-Session", token)
    if payload is not None:
        request.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", "replace")
        try:
            return error.code, json.loads(body)
        except json.JSONDecodeError:
            return error.code, {"raw": body[:300]}


def send_captures() -> list:
    return sorted(HERE.glob("transport-send-*.json"))


def terminate_process(pid: int) -> bool:
    subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True, timeout=20)
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        with socket.socket() as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            try:
                probe.bind(("127.0.0.1", common.APP_PORT))
                return True
            except OSError:
                time.sleep(0.4)
    return False


def seed_parent(dsn: str, activity_id: str, key: str) -> None:
    import asyncio
    from app.activities import PostgresAdmissionLedger
    from app.capabilities import AdmissionIntent, CallContext, LedgerDisposition, LedgerOutcome, Provider, build_business_payload
    from app.runtime import psycopg_compatible_loop_factory

    async def run():
        ledger = PostgresAdmissionLedger(dsn)
        lease = await ledger.claim_lease(activity_id, "seed095", lease_seconds=120, window_seconds=30)
        intent = AdmissionIntent(
            CallContext(activity_id=activity_id, operation_id=key, executor_id=lease.executor_id,
                        execution_generation=lease.execution_generation,
                        scope_revision=lease.scope_revision),
            Provider.DEEPSEEK_CHAT_COMPLETIONS, "synthetic-model-095", 4096, 40, (),
        )
        permit = await ledger.admit(intent)
        await ledger.mark_dispatch_started(permit)
        fmt, payload, sha = build_business_payload(json_object={"reply": "synthetic-parent-095"})
        await ledger.record_outcome(permit, LedgerOutcome(
            LedgerDisposition.RECEIVED, payload_format=fmt, payload=payload, payload_sha256=sha))
        await ledger.begin_window_close(activity_id, lease.executor_id, lease.execution_generation)
        await ledger.settle_execution_window(
            activity_id, lease.executor_id, lease.execution_generation,
            window_seconds=30, elapsed_seconds=1.0,
        )

    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:
        runner.run(run())


def main() -> int:
    steps: list = []
    business_start = time.monotonic()
    try:
        facts = common.inspect_guard()
        assert facts["state_running"] is False, f"container unexpectedly running: {facts}"
    except BaseException as exc:
        common.append_attempt({"batch": BATCH, "phase": "guard-failed", "container_starts": 0,
                               "error": f"{type(exc).__name__}: {exc}"[:200]})
        raise
    common.start_container()
    dsn = common.read_dsn()

    identity = json.loads(docker_psql(
        "SELECT json_build_object("
        "'owner',(SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname='retrolume_task095_g6'),"
        "'role',(SELECT json_build_array(rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls,rolinherit) FROM pg_roles WHERE rolname='retrolume_task095_synth'),"
        "'sessions',(SELECT count(*) FROM pg_stat_activity WHERE usename='retrolume_task095_synth'))",
        database="postgres", user=ADMIN, label="identity", tuples_only=True).stdout.strip())
    log_step(steps, "resource-identity", identity["owner"] == common.ROLE
             and identity["role"] == [True, False, False, False, False, False, False], identity=identity)

    # A. PG API 契约文件复验。
    env = os.environ.copy()
    env["RETROLUME_WORKSPACE_TEST_DATABASE_URL"] = dsn
    env.pop("RETROLUME_DATABASE_URL", None)
    tests = subprocess.run(
        [str(common.PY), "-m", "unittest", "tests.test_activity_workspace_api"],
        cwd=common.ROOT / "backend", env=env,
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600,
    )
    (OUT / "api-unittest.out.txt").write_text(
        f"returncode={tests.returncode}\n---stdout---\n{tests.stdout}\n---stderr---\n{tests.stderr}",
        encoding="utf-8")
    tail = (tests.stdout + tests.stderr).strip().splitlines()[-1] if (tests.stdout + tests.stderr).strip() else ""
    log_step(steps, "pg-api-retest", tests.returncode == 0 and "OK" in tail,
             returncode=tests.returncode, tail=tail)

    # B. 受控 Windows 链。
    plan = {"model": "synthetic-model-095",
            "content": json.dumps({"reply": "synthetic-continue-095"}),
            "prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8, "delay_seconds": 5}
    (HERE / "transport-plan.json").write_text(json.dumps(plan), encoding="utf-8")
    for stale in send_captures():
        stale.unlink()
    for sub in ("data", "backup"):
        (common.RUNTIME / sub).mkdir(exist_ok=True)
    port_deadline = time.monotonic() + 60
    port_free = False
    while time.monotonic() < port_deadline and not port_free:
        with socket.socket() as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            try:
                probe.bind(("127.0.0.1", common.APP_PORT))
                port_free = True
            except OSError:
                time.sleep(1.0)
    if not port_free:
        log_step(steps, "port-free", False, reason="port busy; not touching other processes")
        stopped = common.stop_container()
        common.append_attempt({"batch": BATCH, "phase": "abort", "container_starts": 1,
                               "reason": "port busy", "container_after": stopped, "steps": steps})
        return 1

    app_env = os.environ.copy()
    app_env.update({
        "RETROLUME_DATA_DIR": str(common.RUNTIME / "data"),
        "RETROLUME_BACKUP_DIR": str(common.RUNTIME / "backup"),
        "RETROLUME_DATABASE_URL": dsn,
        "RETROLUME_ACTIVITY_CONFIG": str(common.RUNTIME / "activity.local.json"),
        "RETROLUME_TEST095_KEY": "synthetic-placeholder-key",
        "RETROLUME_TEST_NETWORK_GUARD": "1",
        "RETROLUME_TEST_WIN_CHAIN": "1",
        "RETROLUME_TEST_WIN_EVIDENCE": str(HERE),
        "PYTHONPATH": f"{common.ROOT / 'backend'};{HERE / 'inject'}",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONIOENCODING": "utf-8",
    })
    app_env.pop("RETROLUME_WORKSPACE_TEST_DATABASE_URL", None)
    app_log = open(common.RUNTIME / "app-batch3.log", "w", encoding="utf-8")
    app = None
    app = subprocess.Popen(
        [str(common.PY), "-m", "uvicorn", "app.main:create_app", "--factory",
         "--loop", "app.runtime:psycopg_compatible_loop_factory",
         "--host", "127.0.0.1", "--port", str(common.APP_PORT)],
        cwd=common.ROOT / "backend", env=app_env,
        stdout=app_log, stderr=subprocess.STDOUT, creationflags=0x08000000,
    )
    result = "fail"
    try:
        for _ in range(80):
            try:
                status, _body = http(f"{APP_URL}/health", timeout=2)
                if status == 200:
                    break
            except Exception:
                pass
            time.sleep(0.5)
        else:
            raise RuntimeError("app not ready")
        _status, session = http(f"{APP_URL}/api/session")
        token = session["token"]
        log_step(steps, "app-ready", True, pid=app.pid)

        import uuid as _uuid
        source, version = str(_uuid.uuid4()), str(_uuid.uuid4())
        exec_sql(dsn, "INSERT INTO material_sources(id,title,revision) VALUES (%s,%s,0)", (source, WIN_TITLE))
        exec_sql(dsn, "INSERT INTO material_versions(id,source_id,filename,format,sha256,size)"
                      " VALUES (%s,%s,'win.md','md',%s,2)", (version, source, "9" * 64))
        exec_sql(dsn, "UPDATE material_sources SET current_version=%s,revision=1 WHERE id=%s", (version, source))
        ws_source, ws_version = str(_uuid.uuid4()), str(_uuid.uuid4())
        exec_sql(dsn, "INSERT INTO material_sources(id,title,revision) VALUES (%s,%s,0)", (ws_source, WS_TITLE))
        exec_sql(dsn, "INSERT INTO material_versions(id,source_id,filename,format,sha256,size)"
                      " VALUES (%s,%s,'ws.md','md',%s,2)", (ws_version, ws_source, "7" * 64))
        exec_sql(dsn, "UPDATE material_sources SET current_version=%s,revision=1 WHERE id=%s", (ws_version, ws_source))

        activity = str(_uuid.uuid4())
        status, created = http(f"{APP_URL}/api/activities", token=token, method="POST",
                               payload={"activity_id": activity, "source_ids": [source]})
        log_step(steps, "create-via-http", status == 200 and created["activity"]["status"] == "pending", status=status)
        seed_parent(dsn, activity, "P")
        (OUT / "activity.json").write_text(json.dumps({"activity": activity, "source": source}), encoding="utf-8")

        status, cont = http(f"{APP_URL}/api/activities/{activity}/continuations", token=token, method="POST",
                            payload={"parent_operation_id": "P", "new_operation_id": "ui-cont-b2-1",
                                     "followup": "请基于已有成果继续"})
        (OUT / "continue-1.json").write_text(json.dumps(cont, ensure_ascii=False, indent=2), encoding="utf-8")
        supervision = cont.get("supervision") or {}
        ok1 = (status == 200 and cont.get("status") == "committed_current"
               and supervision.get("state") == "settled"
               and supervision.get("reserved_seconds") == 0
               and supervision.get("cleanup_incomplete") is False
               and 1 <= (supervision.get("settled_seconds") or 0) <= 30)
        log_step(steps, "continue-chain", bool(ok1), status=status,
                 supervision=supervision, business=cont.get("business"))
        captures = send_captures()
        roles = json.loads(captures[0].read_text(encoding="utf-8")).get("message_roles") if captures else None
        log_step(steps, "transport-single-send", len(captures) == 1 and roles == ["assistant", "user"],
                 sends=len(captures), roles=roles)

        rows = q(dsn, "SELECT state, disposition FROM activity_operations"
                      " WHERE activity_id=%s AND operation_id='ui-cont-b2-1'", (activity,))
        result_rows = q(dsn, "SELECT payload FROM activity_operation_results"
                             " WHERE activity_id=%s AND operation_id='ui-cont-b2-1'", (activity,))
        account = q(dsn, "SELECT requests_reserved, cost_reserved_microunits, running_reserved_seconds,"
                         " dispatch_closed, status, last_settled_generation, running_settled_seconds"
                         " FROM activities WHERE id=%s", (activity,))[0]
        payload_value = json.loads(result_rows[0]["payload"])["value"] if result_rows else None
        ok2 = (rows and rows[0]["state"] == "received" and rows[0]["disposition"] == "received"
               and payload_value == {"reply": "synthetic-continue-095"}
               and account["requests_reserved"] == 2 and account["cost_reserved_microunits"] == 200_000
               and account["running_reserved_seconds"] == 0 and account["dispatch_closed"] is True
               and account["status"] == "pending" and account["last_settled_generation"] is not None)
        log_step(steps, "pg-facts-after-chain", bool(ok2), operations=rows, account=account,
                 payload_value=payload_value)

        from app.worker.windows_job import NamedJob, JobOpenError, ERROR_FILE_NOT_FOUND, job_name
        generation = account["last_settled_generation"]
        job_gone = False
        try:
            job = NamedJob.open_existing(activity, generation)
            job.close()
        except JobOpenError as exc:
            job_gone = exc.code == ERROR_FILE_NOT_FOUND
        log_step(steps, "job-gone-after-settle", job_gone, generation=generation)

        status, replay = http(f"{APP_URL}/api/activities/{activity}/continuations", token=token, method="POST",
                              payload={"parent_operation_id": "P", "new_operation_id": "ui-cont-b2-1",
                                       "followup": "同键复查"})
        log_step(steps, "same-key-replay", status == 200 and replay.get("status") == "committed_current"
                 and replay.get("supervision") is None and len(send_captures()) == 1,
                 status=status, supervision=replay.get("supervision"))

        race_results: list = []
        barrier = threading.Barrier(2)

        def race_worker():
            barrier.wait()
            race_results.append(http(f"{APP_URL}/api/activities/{activity}/continuations", token=token, method="POST",
                                     payload={"parent_operation_id": "P", "new_operation_id": "ui-race-1",
                                              "followup": "并发竞争"}, timeout=180))

        threads = [threading.Thread(target=race_worker) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        (OUT / "race-responses.json").write_text(
            json.dumps([{"status": r[0], "body": r[1]} for r in race_results], ensure_ascii=False, indent=2),
            encoding="utf-8")
        race_rows = q(dsn, "SELECT count(*) AS n FROM activity_operations"
                           " WHERE activity_id=%s AND operation_id='ui-race-1'", (activity,))[0]["n"]
        race_account = q(dsn, "SELECT requests_reserved, cost_reserved_microunits FROM activities WHERE id=%s",
                         (activity,))[0]
        ok3 = (race_rows == 1 and len(send_captures()) == 2
               and race_account["requests_reserved"] == 3
               and race_account["cost_reserved_microunits"] == 300_000)
        log_step(steps, "same-key-race-unique", bool(ok3), rows=race_rows,
                 sends=len(send_captures()), account=race_account, responses=[r[0] for r in race_results])

        slow_result: list = []
        slow_thread = threading.Thread(
            target=lambda: slow_result.append(http(
                f"{APP_URL}/api/activities/{activity}/continuations", token=token, method="POST",
                payload={"parent_operation_id": "P", "new_operation_id": "ui-slow-1",
                         "followup": "慢速窗口"}, timeout=180)),
        )
        slow_thread.start()
        time.sleep(1.2)
        sends_before_fail = len(send_captures())
        status, fail_body = http(f"{APP_URL}/api/activities/{activity}/continuations", token=token, method="POST",
                                 payload={"parent_operation_id": "P", "new_operation_id": "ui-fail-1",
                                          "followup": "竞争失败观察"}, timeout=60)
        fail_rows = q(dsn, "SELECT count(*) AS n FROM activity_operations"
                           " WHERE activity_id=%s AND operation_id='ui-fail-1'", (activity,))[0]["n"]
        (OUT / "fail-first-attempt.json").write_text(
            json.dumps({"status": status, "body": fail_body}, ensure_ascii=False, indent=2), encoding="utf-8")
        log_step(steps, "pre-admit-fail-no-row", fail_rows == 0 and len(send_captures()) == sends_before_fail,
                 status=status, rows=fail_rows, body_status=fail_body.get("status"),
                 supervision=(fail_body.get("supervision") or {}).get("state"))
        slow_thread.join()
        (OUT / "slow-result.json").write_text(
            json.dumps({"status": slow_result[0][0], "body": slow_result[0][1]}, ensure_ascii=False, indent=2),
            encoding="utf-8")
        status, retry_body = http(f"{APP_URL}/api/activities/{activity}/continuations", token=token, method="POST",
                                  payload={"parent_operation_id": "P", "new_operation_id": "ui-fail-1",
                                           "followup": "竞争失败观察"}, timeout=180)
        retry_rows = q(dsn, "SELECT state FROM activity_operations"
                            " WHERE activity_id=%s AND operation_id='ui-fail-1'", (activity,))
        (OUT / "fail-retry.json").write_text(
            json.dumps({"status": status, "body": retry_body}, ensure_ascii=False, indent=2), encoding="utf-8")
        ok4 = (status == 200 and retry_body.get("status") == "committed_current"
               and retry_rows and retry_rows[0]["state"] == "received"
               and len(send_captures()) == 4)
        log_step(steps, "same-key-retry-after-fail", bool(ok4), status=status,
                 sends=len(send_captures()), rows=retry_rows)

        # C1 浏览器继续。
        shots = OUT / "shots"
        shots.mkdir(exist_ok=True)
        browser_env = os.environ.copy()
        browser_env.update({"APP_URL": APP_URL, "ACTIVITY_ID": activity, "OP_ID": "ui-cont-b2-1",
                            "TITLE_MATCH": WIN_TITLE, "SHOT_DIR": str(shots)})
        browser = subprocess.run(
            ["node", "tests/task095-browser-continue.mjs"],
            cwd=common.ROOT / "frontend", env=browser_env,
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300,
        )
        (OUT / "browser-continue.out.txt").write_text(
            f"returncode={browser.returncode}\n---stdout---\n{browser.stdout}\n---stderr---\n{browser.stderr}",
            encoding="utf-8")
        try:
            summary = json.loads(browser.stdout.strip().splitlines()[-1])
        except Exception:
            summary = {"ok": False, "raw": browser.stdout[-400:]}
        log_step(steps, "browser-continue", browser.returncode == 0 and summary.get("ok") is True
                 and len(send_captures()) == 5, summary=summary)

        # C2 浏览器工作区完整流。
        upload_md = common.RUNTIME / "task095-upload.md"
        upload_md.write_text("回归正文内容-095\n", encoding="utf-8")
        upload_pdf = common.RUNTIME / "task095-bad.pdf"
        upload_pdf.write_bytes(b"%PDF-1.4 synthetic-broken")
        ws_env = os.environ.copy()
        ws_env.update({"APP_URL": APP_URL, "SHOT_DIR": str(shots), "WS_TITLE": WS_TITLE,
                       "UPLOAD_MD": str(upload_md), "UPLOAD_BAD_PDF": str(upload_pdf)})
        workspace = subprocess.run(
            ["node", "tests/task095-browser-workspace.mjs"],
            cwd=common.ROOT / "frontend", env=ws_env,
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=420,
        )
        (OUT / "browser-workspace.out.txt").write_text(
            f"returncode={workspace.returncode}\n---stdout---\n{workspace.stdout}\n---stderr---\n{workspace.stderr}",
            encoding="utf-8")
        try:
            ws_summary = json.loads(workspace.stdout.strip().splitlines()[-1])
        except Exception:
            ws_summary = {"ok": False, "raw": workspace.stdout[-500:]}
        log_step(steps, "browser-workspace", workspace.returncode == 0 and ws_summary.get("ok") is True,
                 summary=ws_summary)
        result = "pass" if all(step["ok"] for step in steps) else "fail"
    except BaseException as exc:
        log_step(steps, "fatal", False, error=f"{type(exc).__name__}: {exc}"[:300])
    finally:
        if app is not None and app.poll() is None:
            terminated = terminate_process(app.pid)
        else:
            terminated = True
        app_log.close()
        log_step(steps, "app-terminated", terminated, pid=app.pid if app else None)
        business_seconds = round(time.monotonic() - business_start, 3)
        cleanup_start = time.monotonic()
        stopped = common.stop_container()
        cleanup_seconds = round(time.monotonic() - cleanup_start, 3)
        result = "pass" if all(step["ok"] for step in steps) else "fail"
        common.append_attempt({
            "batch": BATCH, "phase": "end", "container_starts": 1, "pg_batches": 1,
            "windows_sessions": 7,
            "windows_sessions_note": "保守计 SUP 启动上限；实际 claim 窗口 5 个",
            "browser_sessions": 2,
            "business_seconds": business_seconds, "cleanup_seconds": cleanup_seconds,
            "container_after": stopped, "result": result, "steps": steps,
        })
        print(json.dumps({"batch": BATCH, "result": result,
                          "failed": [s["step"] for s in steps if not s["ok"]],
                          "business_seconds": business_seconds,
                          "cleanup_seconds": cleanup_seconds,
                          "container_after": stopped}, ensure_ascii=False))
    return 0 if result == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
