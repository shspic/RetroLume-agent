"""TASK-088 最小真实 Windows 组合批 runner：单容器 + 真实 launcher/SUP→worker→PG 链。

资源口径与 fixtures/task088/runner.py 一致（同一固定镜像/端口/限额/无特权/
无宿主bind/独占新卷/口令仅运行期 env 注入并如实披露）。成功后 stop 精确
CID 并只读确认 Running=false，容器/卷保留。用法：

    backend/.venv/Scripts/python.exe -B tests/fixtures/task088/win_runner.py --batch-tag w1

产物写入 Ndocu/evidence/task-088/windows-run-<batch-tag>/。
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import secrets
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import runner as pg  # 复用同目录 PG runner 的 run()/常量；差异仅批次目标。

BACKEND = Path(__file__).resolve().parents[3]
PROJECT = BACKEND.parent
PYTHON = BACKEND / ".venv" / "Scripts" / "python.exe"
EVIDENCE = PROJECT / "Ndocu" / "evidence" / "task-088"
OUTER_DEADLINE_SECONDS = 600


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-tag", required=True)
    args = parser.parse_args()
    tag = args.batch_tag
    if not tag.replace("-", "").replace("_", "").isalnum() or len(tag) > 48:
        print("invalid batch tag", file=sys.stderr)
        return 2
    out_dir = EVIDENCE / f"windows-run-{tag}"
    out_dir.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + OUTER_DEADLINE_SECONDS
    manifest = {
        "batch_tag": tag,
        "purpose": "TASK-088 G3 最小真实 Windows 组合批（launcher/SUP→worker→gateway→PG 成功链）",
        "outer_deadline_seconds": OUTER_DEADLINE_SECONDS,
        "container_name": f"retrolume-task-088-g3-{tag}",
        "image": pg.IMAGE,
        "db_name": pg.DB_NAME,
        "db_user": pg.DB_USER,
        "port": f"127.0.0.1:{pg.PORT}",
        "resources": {"cpus": 1, "memory": "512MiB", "pids_limit": 128, "restart": "no", "privileged": False, "host_binds": 0},
        "credential_path": "POSTGRES_PASSWORD 经 docker run 环境变量注入（镜像既定路径）；DSN 经子进程环境变量注入；不写版本化文件/日志",
        "windows_supervisor_sessions": 2,
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
        rc, out, err = pg.run(
            [
                "docker", "run", "-d",
                "--name", name,
                "--hostname", "retrolume-task-088",
                "-e", f"POSTGRES_DB={pg.DB_NAME}",
                "-e", f"POSTGRES_USER={pg.DB_USER}",
                "-e", f"POSTGRES_PASSWORD={password}",
                "-v", f"{volume}:/var/lib/postgresql/data",
                "-p", f"127.0.0.1:{pg.PORT}:5432",
                "--cpus", "1",
                "--memory", "512MiB",
                "--pids-limit", "128",
                "--restart", "no",
                "--security-opt", "no-new-privileges",
                pg.IMAGE,
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

        ready = False
        probe_deadline = min(deadline, time.monotonic() + 60)
        while time.monotonic() < probe_deadline:
            rc, out, err = pg.run(["docker", "exec", cid, "pg_isready", "-U", pg.DB_USER, "-d", pg.DB_NAME], timeout=10)
            if rc == 0:
                ready = True
                break
            time.sleep(1)
        log(f"pg_isready ready={ready}")
        if not ready:
            manifest["steps"].append({"step": "wait_ready", "rc": 1})
            return 1

        rc, out, err = pg.run(["docker", "inspect", cid], timeout=15)
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
                "port_bindings": list((host_config.get("PortBindings") or {}).keys()),
            }

        dsn = f"postgresql://{pg.DB_USER}:{password}@127.0.0.1:{pg.PORT}/{pg.DB_NAME}"
        manifest["dsn_redacted"] = f"postgresql://{pg.DB_USER}:***@127.0.0.1:{pg.PORT}/{pg.DB_NAME}"
        child_env = dict(os.environ)
        child_env["RETROLUME_TASK088_DSN"] = dsn
        rc, out, err = pg.run(
            [str(PYTHON), "-B", str(BACKEND / "tests" / "fixtures" / "task088" / "apply_migrations.py")],
            timeout=min(120, remaining()),
            env=child_env,
        )
        log(f"migrations rc={rc}")
        log(out.strip()[:1500])
        manifest["steps"].append({"step": "migrations", "rc": rc})
        if rc != 0:
            return 1

        child_env["RETROLUME_TASK088_ROLE"] = pg.DB_USER
        child_env["RETROLUME_TASK088_DB"] = pg.DB_NAME
        rc, out, err = pg.run(
            [str(PYTHON), "-B", str(BACKEND / "tests" / "fixtures" / "task088" / "win_chain.py")],
            timeout=min(300, remaining()),
            env=child_env,
        )
        (out_dir / "chain-stdout.jsonl").write_text(out, encoding="utf-8")
        (out_dir / "chain-stderr.log").write_text(err, encoding="utf-8")
        log(f"chain rc={rc}")
        log(f"chain tail:\n{chr(10).join(out.strip().splitlines()[-12:])}")
        if err.strip():
            log(f"chain stderr: {err.strip()[:500]}")
        manifest["steps"].append({"step": "windows_chain", "rc": rc})
        return rc
    finally:
        if cid:
            rc, out, err = pg.run(["docker", "stop", cid], timeout=60)
            log(f"docker stop rc={rc}")
            rc3, out3, err3 = pg.run(["docker", "inspect", cid], timeout=15)
            running = "unknown"
            if rc3 == 0:
                running = str((json.loads(out3)[0].get("State") or {}).get("Running"))
            log(f"final Running={running}")
            manifest["final_running"] = running
            manifest["steps"].append({"step": "stop", "rc": rc, "running_after": running})
        manifest["wall_seconds"] = round(OUTER_DEADLINE_SECONDS - remaining(), 3)
        (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
        (out_dir / "runner.log").write_text("\n".join(log_lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
