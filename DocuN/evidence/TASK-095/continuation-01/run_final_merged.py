"""TASK-095 续作01 最终合并批（入口 #2：PG 段 + 零 PG 浏览器段）。

修正说明（同根因第一次修正）：首版 run_pg_batch.py 预检的 schema_tables
子查询在 postgres 库执行（pg_class 按库隔离，永远为 0），属 runner 夹具
错误；本版把 schema 核对改到目标库执行。失败原件保留不覆盖。

PG 段：仅使用精确旧合成容器（白名单核对后启动）；只核验/复用
retrolume_task095_g6 与 retrolume_task095_synth，不创建新对象、不触碰旧库
与用户库。原 dsn.json 已删，按卡面许可重置本专用 role 为随机口令（经
stdin，不进 argv/日志/报告），DSN 仅经子进程环境注入。
浏览器段：正式 dist 静态服务 127.0.0.1:18095 + 全合成 API 回放，零 PG。
批前/导入后/批末三重记录被测字节哈希；批末停止容器并核对 Running=false/Pid=0。
"""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(r"D:/shspic/project_NO3_RetroLume-agent")
OUT = HERE / "final-merged"
OUT.mkdir(exist_ok=True)
PY = ROOT / "backend" / ".venv" / "Scripts" / "python.exe"

CID = "e49d3acc3c1be13d670af68bca2b082fea4faeeb9b9babe69df7f1d3941696a4"
NAME = "retrolume-task-088-g3-w1"
IMAGE = "sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f"
VOLUME = "retrolume-task-088-g3-w1-data"
DB = "retrolume_task095_g6"
ROLE = "retrolume_task095_synth"
ADMIN = "retrolume_task088_synth"  # 原合成管理通道（088/092/095 沿用，据 095 创建证据）
APP_PORT = 18095

LEDGER = HERE / "attempt-ledger-continuation01.json"

PRODUCT_FILES = [
    "backend/app/local_session.py",
    "backend/app/service_config.py",
    "backend/app/activities/api.py",
    "backend/app/activities/repository.py",
    "backend/app/activities/service.py",
    "backend/app/main.py",
    "backend/app/materials/api.py",
    "backend/app/pdf_review/api.py",
    "config/activity.example.json",
    ".gitignore",
    "frontend/src/main.tsx",
    "frontend/src/activities/pendingIntents.ts",
    "frontend/src/activities/ActivityWorkspace.tsx",
    "frontend/src/activities/activity-workspace.css",
    "backend/tests/test_activity_workspace_config.py",
    "backend/tests/test_activity_workspace_reads.py",
    "backend/tests/test_activity_workspace_api.py",
    "backend/tests/test_materials.py",
    "backend/tests/test_d3_recovery.py",
    "frontend/tests/task095-browser-continue.mjs",
    "frontend/tests/task095-browser-workspace.mjs",
    "frontend/tests/task095-continuation01-browser.mjs",
]
DIST_FILES = [
    "index.html",
    "assets/index-CiaiBKAO.js",
    "assets/index-PXrCNFBs.css",
    "assets/pdf.worker.min-Dswkl-cV.mjs",
]


def docker(*args: str, timeout: int = 40) -> tuple[int, str, str]:
    result = subprocess.run(
        ["docker", *args], capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=timeout,
    )
    return result.returncode, result.stdout, result.stderr


def inspect_guard() -> dict:
    code, out, err = docker("inspect", NAME)
    if code != 0:
        raise SystemExit(f"container inspect failed: {err.strip()[:200]}")
    data = json.loads(out)[0]
    assert data["Id"] == CID, "container identity mismatch"
    assert data["Config"]["Image"] == IMAGE, "image mismatch"
    assert data["Name"].lstrip("/") == NAME
    host = data["HostConfig"]
    assert host.get("RestartPolicy", {}).get("Name") in ("no", ""), "restart policy mismatch"
    assert not host.get("Privileged"), "privileged container"
    assert host.get("Memory", 0) == 512 * 1024 * 1024, "memory limit mismatch"
    assert host.get("NanoCpus", 0) == 1_000_000_000, "cpu limit mismatch"
    assert host.get("PidsLimit", 0) == 128, "pids limit mismatch"
    binds = host.get("Binds") or []
    for bind in binds:
        source = bind.split(":", 2)[0]
        assert source == VOLUME and "/" not in source and "\\" not in source, "unexpected host bind"
    ports = host.get("PortBindings") or {}
    mapping = ports.get("5432/tcp") or []
    assert len(mapping) == 1
    assert mapping[0]["HostIp"] == "127.0.0.1" and mapping[0]["HostPort"] == "55441", "port mapping mismatch"
    mounts = data.get("Mounts") or []
    assert any(item.get("Name") == VOLUME for item in mounts), "volume mismatch"
    return {
        "id": data["Id"], "image": data["Config"]["Image"],
        "state_running": data["State"]["Running"], "pid": data["State"].get("Pid"),
        "port": "127.0.0.1:55441", "volume": VOLUME,
    }


def start_container() -> None:
    code, _out, err = docker("start", NAME)
    if code != 0:
        raise SystemExit(f"container start failed: {err.strip()[:200]}")
    deadline = time.monotonic() + 30
    while True:
        code, _out, _err = docker("exec", NAME, "pg_isready", "-U", "retrolume", "-d", "retrolume", timeout=10)
        if code == 0:
            return
        if time.monotonic() >= deadline:
            raise SystemExit("pg not ready in time")
        time.sleep(0.4)


def stop_container() -> dict:
    docker("stop", "--time", "5", NAME, timeout=60)
    deadline = time.monotonic() + 20
    while True:
        code, out, _err = docker("inspect", "--format", "{{.State.Running}} {{.State.Pid}}", NAME)
        if code == 0 and out.strip().lower() == "false 0":
            return {"running": False, "pid": 0}
        if time.monotonic() >= deadline:
            return {"running": out.strip(), "pid": None}
        time.sleep(0.5)


def append_attempt(entry: dict) -> None:
    entries = json.loads(LEDGER.read_text(encoding="utf-8"))
    entries.append({"at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), **entry})
    LEDGER.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def product_hashes() -> dict:
    result = {}
    for relative in PRODUCT_FILES:
        path = ROOT / relative
        result[relative] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    dist = {f"dist/{name}": hashlib.sha256((ROOT / "frontend" / "dist" / name).read_bytes()).hexdigest()
            for name in DIST_FILES if (ROOT / "frontend" / "dist" / name).is_file()}
    result.update(dist)
    return result


def run_psql(sql: str, *, database: str, user: str, label: str) -> subprocess.CompletedProcess:
    result = subprocess.run(
        ["docker", "exec", "-i", "-e",
         "PGOPTIONS=-c statement_timeout=10000 -c lock_timeout=2000",
         NAME, "psql", "-X", "-q", "-v", "ON_ERROR_STOP=1", "-t", "-A",
         "-U", user, "-d", database],
        input=sql, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
    )
    # 只落盘 stdout/stderr；含口令的输入 SQL 不写入任何输出文件。
    (OUT / f"{label}.out.txt").write_text(
        f"returncode={result.returncode}\n---stdout---\n{result.stdout}\n---stderr---\n{result.stderr}",
        encoding="utf-8",
    )
    return result


def main() -> int:
    started = time.monotonic()
    (OUT / "hashes-pre.json").write_text(
        json.dumps({"phase": "pre", "files": product_hashes()}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    pg_ok = False
    browser_ok = False
    container_starts = 0
    stopped: dict = {}
    try:
        facts = inspect_guard()
        assert facts["state_running"] is False, f"container unexpectedly running: {facts}"
    except BaseException as exc:
        append_attempt({
            "batch": "c01-merged", "phase": "guard-failed", "container_starts": 0,
            "error": f"{type(exc).__name__}: {exc}"[:200],
        })
        raise

    append_attempt({
        "batch": "c01-merged", "phase": "start", "guard": facts,
        "note": "entry #2 of 2 (merged PG + browser segments); prior entry #1 aborted on runner fixture bug (schema probe in wrong database), failure original preserved",
    })
    business_start = time.monotonic()
    start_container()
    container_starts += 1

    # ---- PG 段：身份核验 + 口令重置 + 最终字节测试 ----
    probe = run_psql(
        "SELECT json_build_object("
        "'role_exists',(SELECT count(*) FROM pg_roles WHERE rolname='retrolume_task095_synth'),"
        "'db_exists',(SELECT count(*) FROM pg_database WHERE datname='retrolume_task095_g6'),"
        "'sessions',(SELECT count(*) FROM pg_stat_activity WHERE usename='retrolume_task095_synth'))",
        database="postgres", user=ADMIN, label="preflight-probe",
    )
    existing = json.loads(probe.stdout.strip())
    identity = json.loads(run_psql(
        "SELECT json_build_object("
        "'owner',(SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname='retrolume_task095_g6'),"
        "'role',(SELECT json_build_array(rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls,rolinherit) FROM pg_roles WHERE rolname='retrolume_task095_synth'),"
        "'memberships',(SELECT count(*) FROM pg_auth_members WHERE member=(SELECT oid FROM pg_roles WHERE rolname='retrolume_task095_synth')))",
        database="postgres", user=ADMIN, label="adopt-identity",
    ).stdout.strip())
    schema = json.loads(run_psql(
        "SELECT json_build_object("
        "'tables',(SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
        "WHERE n.nspname='public' AND c.relname IN ('material_sources','material_versions','pdf_review_candidates',"
        "'activities','activity_scope_sources','activity_operations','activity_operation_results')))",
        database=DB, user=ROLE, label="adopt-schema",
    ).stdout.strip())
    ok_identity = (
        existing == {"role_exists": 1, "db_exists": 1, "sessions": 0}
        and identity["owner"] == ROLE
        and identity["role"] == [True, False, False, False, False, False, False]
        and identity["memberships"] == 0
        and schema["tables"] == 7
    )
    if ok_identity:
        password = secrets.token_urlsafe(24)
        alter = run_psql(
            f"ALTER ROLE retrolume_task095_synth PASSWORD '{password}';",
            database="postgres", user=ADMIN, label="reset-role-password",
        )
        if alter.returncode == 0:
            dsn = f"postgresql://{ROLE}:{password}@127.0.0.1:55441/{DB}"
            (OUT / "hashes-import.json").write_text(
                json.dumps({"phase": "import", "files": product_hashes()}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            env = dict(os.environ)
            env["RETROLUME_WORKSPACE_TEST_DATABASE_URL"] = dsn
            env["RETROLUME_TEST095_KEY"] = "synthetic-placeholder-key"
            env.pop("RETROLUME_DATABASE_URL", None)
            env.pop("RETROLUME_DATA_DIR", None)
            env.pop("RETROLUME_BACKUP_DIR", None)
            tests = subprocess.run(
                [str(PY), "-m", "unittest", "-v",
                 "tests.test_activity_workspace_reads", "tests.test_activity_workspace_api"],
                cwd=ROOT / "backend", env=env,
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900,
            )
            (OUT / "unittest.out.txt").write_text(
                f"returncode={tests.returncode}\n---stdout---\n{tests.stdout}\n---stderr---\n{tests.stderr}",
                encoding="utf-8",
            )
            tail = (tests.stdout + tests.stderr).strip().splitlines()[-3:]
            pg_ok = tests.returncode == 0 and "OK" in " ".join(tail) and "skipped" not in " ".join(tail)
            (OUT / "pg-segment.json").write_text(
                json.dumps({"returncode": tests.returncode, "tail": tail, "ok": pg_ok,
                            "skipped_present": "skipped" in " ".join(tail)}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        else:
            (OUT / "pg-segment.json").write_text(
                json.dumps({"ok": False, "reason": "role password reset failed"}, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
    else:
        (OUT / "pg-segment.json").write_text(
            json.dumps({"ok": False, "reason": "identity checks failed", "preflight": existing,
                        "identity": identity, "schema": schema}, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    (OUT / "hashes-final.json").write_text(
        json.dumps({"phase": "final", "files": product_hashes()}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    cleanup_start = time.monotonic()
    stopped = stop_container()
    cleanup_seconds = round(time.monotonic() - cleanup_start, 3)
    pg_seconds = round(time.monotonic() - business_start, 3)

    # ---- 浏览器段（零 PG）：端口核空闲 → node 合成回放批 → 端口释放核 ----
    browser_start = time.monotonic()

    def port_free(port: int) -> bool:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            return sock.connect_ex(("127.0.0.1", port)) != 0

    port_was_free = port_free(APP_PORT)
    if port_was_free:
        browser = subprocess.run(
            ["node", "tests/task095-continuation01-browser.mjs"],
            cwd=ROOT / "frontend",
            env={**os.environ,
                 "APP_PORT": str(APP_PORT),
                 "SHOT_DIR": str(OUT / "shots"),
                 "REPORT_PATH": str(OUT / "browser-report.json"),
                 "DIST_DIR": str(ROOT / "frontend" / "dist")},
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=240,
        )
        (OUT / "browser.out.txt").write_text(
            f"returncode={browser.returncode}\n---stdout---\n{browser.stdout}\n---stderr---\n{browser.stderr}",
            encoding="utf-8",
        )
        try:
            report = json.loads((OUT / "browser-report.json").read_text(encoding="utf-8"))
            browser_ok = bool(report.get("ok")) and browser.returncode == 0
        except Exception as error:  # noqa: 报告缺失也按失败记录
            browser_ok = False
            (OUT / "browser-report-error.txt").write_text(str(error), encoding="utf-8")
        port_released = port_free(APP_PORT)
    else:
        browser = None
        port_released = None
        (OUT / "browser.out.txt").write_text("returncode=-1\n---stderr---\nport 18095 not free before start", encoding="utf-8")
    browser_seconds = round(time.monotonic() - browser_start, 3)

    total_seconds = round(time.monotonic() - started, 3)
    append_attempt({
        "batch": "c01-merged", "phase": "end",
        "container_starts": container_starts,
        "pg_seconds": pg_seconds, "browser_seconds": browser_seconds,
        "cleanup_seconds": cleanup_seconds, "total_seconds": total_seconds,
        "pg_ok": pg_ok, "browser_ok": browser_ok,
        "port_was_free": port_was_free, "port_released": port_released,
        "container_after": stopped,
        "result": "pass" if (pg_ok and browser_ok and stopped == {"running": False, "pid": 0}) else "fail",
    })
    print(json.dumps({
        "batch": "c01-merged", "pg_ok": pg_ok, "browser_ok": browser_ok,
        "container_starts": container_starts, "pg_seconds": pg_seconds,
        "browser_seconds": browser_seconds, "cleanup_seconds": cleanup_seconds,
        "container_after": stopped, "port_released": port_released,
    }, ensure_ascii=False))
    return 0 if pg_ok and browser_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
