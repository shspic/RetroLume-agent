"""TASK-095 续作02 唯一合并入口：分页单方法真实 PG + 浏览器 s0—s8 + 收尾。

按卡：一次真实 runner 入口；容器 start 最多 1、浏览器 start 最多 1。
26 个已通过方法不重跑（as-run 字节证据 reuse-binding.json 继承）。
PG 段仅运行 ReadProjectionTests.test_activity_list_pagination_cursor（修正后
冻结字节 ed32fe37…）；身份核验的 schema 查询连接 task095 库本身。
浏览器段运行当前 task095-continuation01-browser.mjs（修正后 5e541e22…），
真最终 dist、全合成 API 回放；summary.ok 已收紧为 checks 全 true 且无
failures/blocked。PG 断言失败可继续隔离的浏览器段，总批 FAIL；
资源/清理异常则停止后续。
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
OUT = HERE / "final-run"
OUT.mkdir(exist_ok=True)
PY = ROOT / "backend" / ".venv" / "Scripts" / "python.exe"

CID = "e49d3acc3c1be13d670af68bca2b082fea4faeeb9b9babe69df7f1d3941696a4"
NAME = "retrolume-task-088-g3-w1"
IMAGE = "sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f"
VOLUME = "retrolume-task-088-g3-w1-data"
DB = "retrolume_task095_g6"
ROLE = "retrolume_task095_synth"
ADMIN = "retrolume_task088_synth"  # 继承已核正确管理身份（095 创建证据）
APP_PORT = 18095

LEDGER = HERE / "attempt-ledger-continuation02.json"

# 产品冻结六项（以续作01 post-hashes.json 为准）+ 两夹具冻结期望。
FROZEN = {
    "backend/app/materials/api.py": "e463ed5d90a656527b33fa3829f74d0716d99635e9a27683d1e82155affb3d79",
    "frontend/src/activities/ActivityWorkspace.tsx": "b6a339d0847699caa3aa998c6f063997d9f7d236035f2d13070fb728c95348b5",
    "backend/app/activities/repository.py": "ac55739c9f35596f62b610069dd6f1ca558cc98bf666bcc814533ee257e7670c",
    "backend/tests/test_activity_workspace_reads.py": "ed32fe37004bde9af37a33066cb8c79755754aa6fcdff7cd24f51ee06fbae268",
    "backend/tests/test_activity_workspace_api.py": "a5c95c794e8e8f91ff71ba3427e964dd177ee4be413c6966750bb7ec31885a4f",
    "frontend/tests/task095-continuation01-browser.mjs": "5e541e22e60b3d69e2e9f334ce52abd3248c2bb0fe01622f8a38aad9dbc124a3",
}
DIST_FILES = ["index.html", "assets/index-CiaiBKAO.js", "assets/index-PXrCNFBs.css", "assets/pdf.worker.min-Dswkl-cV.mjs"]


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
    entries = json.loads(LEDGER.read_text(encoding="utf-8")) if LEDGER.is_file() else []
    entries.append({"at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), **entry})
    LEDGER.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def snapshot() -> dict:
    result = {rel: sha(ROOT / rel) for rel in FROZEN}
    result.update({f"dist/{name}": sha(ROOT / "frontend" / "dist" / name) for name in DIST_FILES})
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
    pre = snapshot()
    (OUT / "hashes-pre.json").write_text(
        json.dumps({"phase": "pre", "files": pre}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    drift = {rel: {"expect": expect, "actual": pre.get(rel)} for rel, expect in FROZEN.items() if pre.get(rel) != expect}
    if drift:
        append_attempt({"batch": "c02-merged", "phase": "frozen-drift", "drift": drift})
        print("FROZEN DRIFT", json.dumps(drift, ensure_ascii=False))
        return 1
    append_attempt({
        "batch": "c02-merged", "phase": "new-permission",
        "identity": "WorkBuddy（GLM-5.3-Flash）续作01 同一实际修复窗口延续，非 096 审计窗口，如实登记",
        "plan": "PG: ReadProjectionTests.test_activity_list_pagination_cursor only; Browser: task095-continuation01-browser.mjs s0—s8; fixture browser script 5e541e22 with pre/diff/post in continuation-02",
        "budget": {"entries": 1, "container_starts": 1, "browser_starts": 1,
                   "business_seconds": 300, "cleanup_seconds": 120, "pg_target_seconds": 60},
    })
    try:
        facts = inspect_guard()
        assert facts["state_running"] is False, f"container unexpectedly running: {facts}"
    except BaseException as exc:
        append_attempt({"batch": "c02-merged", "phase": "guard-failed",
                        "error": f"{type(exc).__name__}: {exc}"[:200]})
        raise
    append_attempt({"batch": "c02-merged", "phase": "start", "guard": facts,
                    "note": "single real entry; prior 9 entries/8 starts preserved"})

    resource_ok = True
    pg_ok = False
    browser_ok = False
    browser_ran = False
    stopped: dict = {}
    container_starts = 0
    pg_seconds = browser_seconds = cleanup_seconds = 0.0
    business_start = time.monotonic()
    try:
        start_container()
        container_starts += 1

        identity = json.loads(run_psql(
            "SELECT json_build_object("
            "'owner',(SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname='retrolume_task095_g6'),"
            "'role',(SELECT json_build_array(rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls,rolinherit) FROM pg_roles WHERE rolname='retrolume_task095_synth'),"
            "'memberships',(SELECT count(*) FROM pg_auth_members WHERE member=(SELECT oid FROM pg_roles WHERE rolname='retrolume_task095_synth')),"
            "'sessions',(SELECT count(*) FROM pg_stat_activity WHERE usename='retrolume_task095_synth'))",
            database="postgres", user=ADMIN, label="identity-admin",
        ).stdout.strip())
        schema = json.loads(run_psql(
            "SELECT json_build_object("
            "'tables',(SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
            "WHERE n.nspname='public' AND c.relname IN ('material_sources','material_versions','pdf_review_candidates',"
            "'activities','activity_scope_sources','activity_operations','activity_operation_results')))",
            database=DB, user=ROLE, label="identity-schema-in-task095-db",
        ).stdout.strip())
        ok_identity = (
            identity["owner"] == ROLE
            and identity["role"] == [True, False, False, False, False, False, False]
            and identity["memberships"] == 0
            and identity["sessions"] == 0
            and schema["tables"] == 7
        )
        if not ok_identity:
            (OUT / "pg-segment.json").write_text(
                json.dumps({"ok": False, "reason": "identity checks failed",
                            "identity": identity, "schema": schema}, ensure_ascii=False) + "\n", encoding="utf-8")
        else:
            password = secrets.token_urlsafe(24)
            alter = run_psql(
                f"ALTER ROLE retrolume_task095_synth PASSWORD '{password}';",
                database="postgres", user=ADMIN, label="reset-role-password",
            )
            if alter.returncode != 0:
                (OUT / "pg-segment.json").write_text(
                    json.dumps({"ok": False, "reason": "role password reset failed"}, ensure_ascii=False) + "\n",
                    encoding="utf-8")
            else:
                dsn = f"postgresql://{ROLE}:{password}@127.0.0.1:55441/{DB}"
                (OUT / "hashes-import.json").write_text(
                    json.dumps({"phase": "import", "files": snapshot()}, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")
                env = dict(os.environ)
                env["RETROLUME_WORKSPACE_TEST_DATABASE_URL"] = dsn
                env.pop("RETROLUME_DATABASE_URL", None)
                env.pop("RETROLUME_DATA_DIR", None)
                env.pop("RETROLUME_BACKUP_DIR", None)
                tests = subprocess.run(
                    [str(PY), "-m", "unittest", "-v",
                     "tests.test_activity_workspace_reads.ReadProjectionTests.test_activity_list_pagination_cursor"],
                    cwd=ROOT / "backend", env=env,
                    capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
                )
                (OUT / "unittest-pagination.out.txt").write_text(
                    f"returncode={tests.returncode}\n---stdout---\n{tests.stdout}\n---stderr---\n{tests.stderr}",
                    encoding="utf-8")
                tail = (tests.stdout + tests.stderr).strip().splitlines()[-3:]
                pg_ok = tests.returncode == 0 and "OK" in " ".join(tail) and "skipped" not in " ".join(tail)
                (OUT / "pg-segment.json").write_text(
                    json.dumps({"ok": pg_ok, "returncode": tests.returncode, "tail": tail,
                                "skipped_present": "skipped" in " ".join(tail),
                                "note": "single method only; 26 prior OK methods inherited via reuse-binding.json"},
                               ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        pg_seconds = round(time.monotonic() - business_start, 3)
    except BaseException as exc:
        resource_ok = False
        append_attempt({"batch": "c02-merged", "phase": "resource-exception",
                        "error": f"{type(exc).__name__}: {exc}"[:300]})
    finally:
        if container_starts == 1:
            stopped = stop_container()
            if stopped != {"running": False, "pid": 0}:
                resource_ok = False
    cleanup_seconds = round(time.monotonic() - business_start - pg_seconds, 3)

    # 浏览器段：PG 段断言失败仍可跑（完全隔离）；资源/清理异常则停。
    if resource_ok:
        browser_start = time.monotonic()

        def port_free(port: int) -> bool:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                return sock.connect_ex(("127.0.0.1", port)) != 0

        if port_free(APP_PORT):
            browser_ran = True
            browser = subprocess.run(
                ["node", "tests/task095-continuation01-browser.mjs"],
                cwd=ROOT / "frontend",
                env={**os.environ,
                     "APP_PORT": str(APP_PORT),
                     "SHOT_DIR": str(OUT / "shots"),
                     "REPORT_PATH": str(OUT / "browser-report.json"),
                     "DIST_DIR": str(ROOT / "frontend" / "dist")},
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180,
            )
            (OUT / "browser.out.txt").write_text(
                f"returncode={browser.returncode}\n---stdout---\n{browser.stdout}\n---stderr---\n{browser.stderr}",
                encoding="utf-8")
            try:
                report = json.loads((OUT / "browser-report.json").read_text(encoding="utf-8"))
                browser_ok = bool(report.get("ok")) and browser.returncode == 0
                (OUT / "browser-segment.json").write_text(json.dumps({
                    "ok": browser_ok, "returncode": browser.returncode,
                    "checks": report.get("checks"), "failures": report.get("failures"),
                    "blocked": report.get("blocked"), "post_total": report.get("post_total"),
                    "steps": report.get("steps"), "console_errors": report.get("console_errors"),
                    "page_errors": report.get("page_errors"),
                }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            except Exception as error:  # noqa: 报告缺失按失败记录
                browser_ok = False
                (OUT / "browser-report-error.txt").write_text(str(error), encoding="utf-8")
            port_released = port_free(APP_PORT)
            if not port_released:
                resource_ok = False
        else:
            (OUT / "browser.out.txt").write_text(
                "returncode=-1\n---stderr---\nport 18095 not free before start", encoding="utf-8")
            browser_ran = False
            resource_ok = False
        browser_seconds = round(time.monotonic() - browser_start, 3)

    (OUT / "hashes-final.json").write_text(
        json.dumps({"phase": "final", "files": snapshot()}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    total_seconds = round(time.monotonic() - started, 3)
    append_attempt({
        "batch": "c02-merged", "phase": "end",
        "container_starts": container_starts, "browser_started": browser_ran,
        "pg_ok": pg_ok, "browser_ok": browser_ok, "resource_ok": resource_ok,
        "pg_seconds": pg_seconds, "browser_seconds": browser_seconds,
        "cleanup_seconds": cleanup_seconds, "total_seconds": total_seconds,
        "container_after": stopped,
        "result": "pass" if (pg_ok and browser_ok and resource_ok) else "fail",
    })
    print(json.dumps({
        "batch": "c02-merged", "pg_ok": pg_ok, "browser_ok": browser_ok, "browser_ran": browser_ran,
        "resource_ok": resource_ok, "container_starts": container_starts,
        "pg_seconds": pg_seconds, "browser_seconds": browser_seconds,
        "total_seconds": total_seconds, "container_after": stopped,
    }, ensure_ascii=False))
    return 0 if (pg_ok and browser_ok and resource_ok) else 1


if __name__ == "__main__":
    raise SystemExit(main())
