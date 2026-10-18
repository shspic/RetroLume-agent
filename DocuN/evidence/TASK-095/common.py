"""TASK-095 批次公共：容器白名单核对、尝试账、合成 DSN 与产品哈希。

仅用于证据侧运行控制；产品不依赖本目录。Docker inspect 的完整 JSON 只在
内存解析白名单字段，不输出 Env。
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.request

ROOT = Path(r"D:/shspic/project_NO3_RetroLume-agent")
EVIDENCE = ROOT / "DocuN" / "evidence" / "TASK-095"
RUNTIME = EVIDENCE / "runtime"
PY = ROOT / "backend" / ".venv" / "Scripts" / "python.exe"

CID = "e49d3acc3c1be13d670af68bca2b082fea4faeeb9b9babe69df7f1d3941696a4"
NAME = "retrolume-task-088-g3-w1"
IMAGE = "sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f"
VOLUME = "retrolume-task-088-g3-w1-data"
DB = "retrolume_task095_g6"
ROLE = "retrolume_task095_synth"
APP_PORT = 18095

PRODUCT_FILES = [
    "backend/app/local_session.py",
    "backend/app/service_config.py",
    "backend/app/activities/api.py",
    "backend/app/activities/repository.py",
    "backend/app/activities/service.py",
    "backend/app/main.py",
    "backend/app/materials/api.py",
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
]


def docker(*args: str, timeout: int = 40) -> tuple[int, str, str]:
    result = subprocess.run(
        ["docker", *args], capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=timeout,
    )
    return result.returncode, result.stdout, result.stderr


def inspect_guard() -> dict:
    """核对精确归属：CID/镜像/卷/端口/资源限制/无 host bind；返回白名单事实。"""
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
    # 只允许精确命名卷绑定；任何主机路径绑定都视为归属不符。
    for bind in binds:
        source = bind.split(":", 2)[0]
        assert source == VOLUME and "/" not in source and "\\" not in source, "unexpected host bind"
    ports = host.get("PortBindings") or {}
    mapping = ports.get("5432/tcp") or []
    assert len(mapping) == 1
    assert mapping[0]["HostIp"] in ("127.0.0.1",) and mapping[0]["HostPort"] == "55441", "port mapping mismatch"
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


def write_dsn() -> str:
    path = RUNTIME / "dsn.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["dsn"]


def read_dsn() -> str:
    return json.loads((RUNTIME / "dsn.json").read_text(encoding="utf-8"))["dsn"]


def append_attempt(entry: dict) -> None:
    path = EVIDENCE / "attempt-ledger.json"
    entries = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else []
    entries.append({"at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), **entry})
    path.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def product_hashes() -> dict:
    result = {}
    for relative in PRODUCT_FILES:
        path = ROOT / relative
        if path.is_file():
            result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        else:
            result[relative] = None
    return result


def http_json(url: str, *, token: str | None = None, method: str = "GET",
              payload: dict | None = None, timeout: float = 30.0) -> tuple[int, dict]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, method=method)
    if token is not None:
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
            return error.code, {"raw": body[:200]}


def wait_app(token: str, port: int = APP_PORT) -> None:
    deadline = time.monotonic() + 40
    while True:
        try:
            status, body = http_json(f"http://127.0.0.1:{port}/health", timeout=2)
            if status == 200:
                status, _ = http_json(f"http://127.0.0.1:{port}/api/session", timeout=2)
                if status == 200:
                    return
        except Exception:
            pass
        if time.monotonic() >= deadline:
            raise SystemExit("app not ready")
        time.sleep(0.4)
