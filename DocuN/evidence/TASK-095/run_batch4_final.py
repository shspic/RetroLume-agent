"""TASK-095 批次4（最终验证入口）：PG API 复验 + 浏览器只读查看 + 工作区完整流。

不重跑 Windows 链（批次3已全绿），不新增任何监督会话；仅：
  A. PG API 契约文件全绿复验（修复同键用例种子后的复跑）；
  B. 浏览器只读查看既有链提交的继续成果（单操作正文补全）；
  C. 浏览器工作区完整流（能力分层、界面新建、响应丢失恢复、409 核验、显式同键
     重试、取消、损坏台账闸门、原资料与 PDF 分支回归）。
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "backend"))
import common  # noqa: E402

BATCH = "4-final-verification"
OUT = HERE / "batch4"
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


def http(url: str, *, token=None, method="GET", payload=None, timeout=60.0):
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
    app_log = open(common.RUNTIME / "app-batch4.log", "w", encoding="utf-8")
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

        shots = OUT / "shots"
        shots.mkdir(exist_ok=True)
        browser_env = os.environ.copy()
        browser_env.update({"APP_URL": APP_URL, "OP_ID": "ui-cont-b2-1",
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
        log_step(steps, "browser-continue-readonly", browser.returncode == 0 and summary.get("ok") is True,
                 summary=summary)

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
            "windows_sessions": 0, "browser_sessions": 2,
            "note": "只读查看与工作区流；不重跑 Windows 链，不新增监督会话",
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
