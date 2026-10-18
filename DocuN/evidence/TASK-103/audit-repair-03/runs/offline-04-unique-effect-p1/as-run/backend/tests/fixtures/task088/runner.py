"""TASK-088 真实 PG 定向批 runner：精确资源、单容器、一次批次。

职责（顺序执行，失败即停并如实记录）：
1. 启动本卡唯一合成 PG 容器（固定镜像 sha256，1CPU/512MiB/pids128，
   restart=no，无特权，无宿主 bind，仅 127.0.0.1:55441，独占新卷，
   独立合成角色与新随机口令）。口令仅运行期经 docker env 注入，不写
   版本化文件/日志；本镜像的口令注入路径就是环境变量，如实披露。
2. 等待就绪；按序应用 001—006 与 007 迁移到本卡合成库 public schema。
3. 运行 tests.test_activity_results（DSN 经环境变量注入子进程）。
4. 停止精确 CID 并只读确认 Running=false；容器/卷保留不删。
5. 写 manifest（CID/imageID/卷/端口/资源配置/PID/创建时间/search_path/
   归属/口令注入路径披露）与原始日志；DSN 写证据时口令脱敏。

外层总时限独立于业务阻塞；子进程精确控制（Popen + 有界 wait + 进程树
终止兜底仅限本 runner 直接子进程）。用法：

    backend/.venv/Scripts/python.exe -B -m fixtures.task088.runner --batch-tag <tag>

cwd 必须是 backend/tests（与 unittest 发现一致）。产物写入
Ndocu/evidence/task-088/pg-run-<batch-tag>/。
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import secrets
import subprocess
import sys
import time

BACKEND = Path(__file__).resolve().parents[3]
TESTS = BACKEND / "tests"
PROJECT = BACKEND.parent
PYTHON = BACKEND / ".venv" / "Scripts" / "python.exe"
EVIDENCE = PROJECT / "Ndocu" / "evidence" / "task-088"
IMAGE = "sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f"
PORT = 55441
DB_NAME = "retrolume_task088_g3"
DB_USER = "retrolume_task088_synth"
MIGRATIONS = [
    "001_materials.sql",
    "002_activities.sql",
    "003_pdf_review.sql",
    "004_activities_time_budget.sql",
    "005_activities_dispatch_closed.sql",
    "006_activities_running_owner_session.sql",
    "007_activity_operation_results.sql",
]
OUTER_DEADLINE_SECONDS = 600


def run(cmd, *, timeout, env=None, capture=True):
    """有界子进程；返回 (returncode, stdout, stderr)。不泄漏 env。"""
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        text=True,
        env=env,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )
    try:
        out, err = proc.communicate(timeout=timeout)
        return proc.returncode, out or "", err or ""
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate()
        return -9, out or "", (err or "") + "\n<timeout>"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-tag", required=True)
    parser.add_argument("--tests", default="tests.test_activity_results",
                        help="unittest 目标（模块或空格分隔的用例名）；修正批只复验受影响/未跑项")
    args = parser.parse_args()
    tag = args.batch_tag
    if not tag.replace("-", "").replace("_", "").isalnum() or len(tag) > 48:
        print("invalid batch tag", file=sys.stderr)
        return 2
    out_dir = EVIDENCE / f"pg-run-{tag}"
    out_dir.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + OUTER_DEADLINE_SECONDS
    manifest = {
        "batch_tag": tag,
        "purpose": "TASK-088 G3 真实合成 PG 定向批",
        "unittest_target": args.tests,
        "outer_deadline_seconds": OUTER_DEADLINE_SECONDS,
        "container_name": f"retrolume-task-088-g3-{tag}",
        "image": IMAGE,
        "db_name": DB_NAME,
        "db_user": DB_USER,
        "search_path": "public",
        "port": f"127.0.0.1:{PORT}",
        "resources": {"cpus": 1, "memory": "512MiB", "pids_limit": 128, "restart": "no", "privileged": False, "host_binds": 0},
        "credential_path": "POSTGRES_PASSWORD 经 docker run 环境变量注入（pgvector 镜像既定路径）；不写版本化文件/日志/argv 之外的证据；DSN 证据脱敏",
        "steps": [],
    }
    log_lines = []

    def log(line):
        log_lines.append(line)
        print(line, flush=True)

    def remaining():
        return max(1.0, deadline - time.monotonic())

    password = secrets.token_hex(16)
    name = manifest["container_name"]
    volume = f"retrolume-task-088-g3-{tag}-data"
    cid = None
    try:
        rc, out, err = run(
            [
                "docker", "run", "-d",
                "--name", name,
                "--hostname", "retrolume-task-088",
                "-e", f"POSTGRES_DB={DB_NAME}",
                "-e", f"POSTGRES_USER={DB_USER}",
                "-e", f"POSTGRES_PASSWORD={password}",
                "-v", f"{volume}:/var/lib/postgresql/data",
                "-p", f"127.0.0.1:{PORT}:5432",
                "--cpus", "1",
                "--memory", "512MiB",
                "--pids-limit", "128",
                "--restart", "no",
                "--security-opt", "no-new-privileges",
                IMAGE,
            ],
            timeout=min(60, remaining()),
        )
        log(f"docker run rc={rc}")
        if rc != 0:
            log(f"stderr: {err.strip()[:500]}")
            manifest["steps"].append({"step": "docker_run", "rc": rc, "error": err.strip()[:500]})
            return 1
        cid = out.strip()
        manifest["cid"] = cid
        manifest["volume"] = volume

        # 就绪等待（pg_isready 探针，计入批次预算）。
        ready = False
        probe_deadline = min(deadline, time.monotonic() + 60)
        while time.monotonic() < probe_deadline:
            rc, out, err = run(["docker", "exec", cid, "pg_isready", "-U", DB_USER, "-d", DB_NAME], timeout=10)
            if rc == 0:
                ready = True
                break
            time.sleep(1)
        log(f"pg_isready ready={ready}")
        if not ready:
            manifest["steps"].append({"step": "wait_ready", "rc": 1})
            return 1
        manifest["steps"].append({"step": "wait_ready", "rc": 0})

        # 容器检查（完整 JSON 解析，不用 --format 投影；不输出 Env）。
        rc, out, err = run(["docker", "inspect", cid], timeout=15)
        if rc == 0:
            info = json.loads(out)[0]
            state = info.get("State") or {}
            host_config = info.get("HostConfig") or {}
            manifest["inspect"] = {
                "image_id": info.get("Image"),
                "created": info.get("Created"),
                "state_pid": state.get("Pid"),
                "state_started_at": state.get("StartedAt"),
                "state_running": state.get("Running"),
                "nano_cpus": host_config.get("NanoCpus"),
                "memory_bytes": host_config.get("Memory"),
                "pids_limit": host_config.get("PidsLimit"),
                "restart_policy": (host_config.get("RestartPolicy") or {}).get("Name"),
                "privileged": host_config.get("Privileged"),
                "binds": host_config.get("Binds"),
                "port_bindings": list(((host_config.get("PortBindings") or {}).keys())),
                "mounts_unknown": "Mounts" not in host_config,
            }

        # 迁移 001—006 → 007（同步 psycopg，autocommit，逐文件）。
        import os
        dsn = f"postgresql://{DB_USER}:{password}@127.0.0.1:{PORT}/{DB_NAME}"
        dsn_redacted = f"postgresql://{DB_USER}:***@127.0.0.1:{PORT}/{DB_NAME}"
        manifest["dsn_redacted"] = dsn_redacted
        child_env = dict(os.environ)
        migration_script = BACKEND / "tests" / "fixtures" / "task088" / "apply_migrations.py"
        child_env["RETROLUME_TASK088_DSN"] = dsn
        rc, out, err = run(
            [str(PYTHON), "-B", str(migration_script)],
            timeout=min(120, remaining()),
            env=child_env,
        )
        log(f"migrations rc={rc}")
        log(out.strip()[:2000])
        if err.strip():
            log(f"migrations stderr: {err.strip()[:500]}")
        manifest["steps"].append({"step": "migrations", "rc": rc})
        if rc != 0:
            return 1

        # 定向测试批。
        child_env["RETROLUME_ACTIVITY_RESULTS_TEST_DATABASE_URL"] = dsn
        rc, out, err = run(
            [str(PYTHON), "-B", "-m", "unittest", *args.tests.split(), "-v"],
            timeout=min(480, remaining()),
            env=child_env,
        )
        (out_dir / "unittest-stdout.log").write_text(out, encoding="utf-8")
        (out_dir / "unittest-stderr.log").write_text(err, encoding="utf-8")
        log(f"unittest rc={rc}")
        tail = "\n".join((err or out).strip().splitlines()[-15:])
        log(f"unittest tail:\n{tail}")
        manifest["steps"].append({"step": "unittest", "rc": rc})
        return rc
    finally:
        if cid:
            rc, out, err = run(["docker", "stop", cid], timeout=60)
            log(f"docker stop rc={rc}")
            rc3, out3, err3 = run(["docker", "inspect", cid], timeout=15)
            running = "unknown"
            if rc3 == 0:
                running = str((json.loads(out3)[0].get("State") or {}).get("Running"))
            log(f"final Running={running}")
            manifest["final_running"] = running
            manifest["steps"].append({"step": "stop", "rc": rc, "running_after": running})
        manifest["wall_seconds"] = round(600 - remaining(), 3)
        (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
        (out_dir / "runner.log").write_text("\n".join(log_lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
