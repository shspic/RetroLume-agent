"""TASK-092 真实批次外层 runner：精确容器、两个专用合成库、单批预算与收尾。

用法：python batch_runner.py --phase pg|upgrade|windows
只访问白名单容器属性；只创建/接续本卡 manifest 已登记的合成对象；批内不重试。
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib.machinery
import json
import os
from pathlib import Path
import queue
import secrets
import shutil
import socket
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BACKEND = ROOT / "backend"
EVIDENCE = HERE
sys.path.insert(0, str(BACKEND))

loaded_bytes = {}
_original_get_code = importlib.machinery.SourceFileLoader.get_code


def _capture_code(self, fullname):
    if fullname == "app" or fullname.startswith("app."):
        path = Path(self.get_filename(fullname)).resolve()
        raw = self.get_data(str(path))
        loaded_bytes[path.relative_to(ROOT).as_posix()] = hashlib.sha256(raw).hexdigest()
        return self.source_to_code(raw, str(path))
    return _original_get_code(self, fullname)


importlib.machinery.SourceFileLoader.get_code = _capture_code

from child_control import ControlledChild  # noqa: E402

CID = "e49d3acc3c1be13d670af68bca2b082fea4faeeb9b9babe69df7f1d3941696a4"
IMAGE = "sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f"
NAME = "retrolume-task-088-g3-w1"
VOLUME = NAME + "-data"
TOOLS_DB = "retrolume_task092_tools"
UPGRADE_DB = "retrolume_task092_upgrade"
ROLE = "retrolume_task092_synth"
ADMIN = "retrolume_task088_synth"

KEYS = ("Id", "Name", "Image", "Mounts", "HostConfig.PortBindings", "HostConfig.NanoCpus",
        "HostConfig.Memory", "HostConfig.PidsLimit", "HostConfig.RestartPolicy.Name",
        "HostConfig.Privileged", "State.Running", "State.Pid", "State.StartedAt")
FORMAT = "|".join("{{json ." + key + "}}" for key in KEYS)

PHASES = {
    "pg": {"budget": 600, "children": [("tool_pg_child.py", "pg_child")]},
    "retry_upgrade": {"budget": 700, "children": [("tool_pg_child.py", "pg_retry_child"),
                                                  ("upgrade_child.py", "upgrade_child")]},
    "upgrade": {"budget": 480, "children": [("upgrade_child.py", "upgrade_child")]},
    "windows": {"budget": 600, "children": [("win_chain.py", "windows_child")]},
    "final": {"budget": 1100, "children": [("tool_pg_child.py", "pg_retry_child"),
                                           ("upgrade_child.py", "upgrade_child"),
                                           ("win_chain.py", "windows_child")]},
}
RETRY_TARGETS = [
    "tests.test_activity_tools.ToolPostgresTests.test_c7_executed_but_record_uncommitted_stays_unknown_no_overwrite",
    "tests.test_activity_tools.ToolPostgresTests.test_c9_scope_cas_variants_and_mark_gate",
]


def write(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def hashes() -> dict:
    paths = list((BACKEND / "app").rglob("*.py"))
    paths += list((BACKEND / "migrations").glob("*.sql"))
    paths += [BACKEND / "tests" / name for name in (
        "test_activity_tools.py", "test_worker_one_tool.py", "test_activity_results.py",
        "test_activity_continuation.py", "test_capabilities.py", "test_worker_session.py",
        "test_worker_one_call.py", "test_activity_time_budget.py")]
    paths += list(HERE.glob("*.py"))
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths)}


def main(phase: str) -> int:
    if phase not in PHASES:
        raise SystemExit(2)
    child_budget = PHASES[phase]["budget"]
    budget_file = EVIDENCE / "budget-manifest.json"
    budget = json.loads(budget_file.read_text(encoding="utf-8-sig"))
    if len(budget["real_attempts"]) >= 3 or budget["real_used_seconds"] + child_budget > 3600:
        raise RuntimeError("real budget unavailable")
    if budget["container_starts"] >= 3:
        raise RuntimeError("container start budget exhausted")
    folder = EVIDENCE / ("real-" + str(len(budget["real_attempts"]) + 1).zfill(2))
    folder.mkdir(exist_ok=False)
    attempt = len(budget["real_attempts"]) + 1
    start = time.monotonic()
    deadline = start + child_budget
    scenarios = json.loads((EVIDENCE / "scenario-manifest.json").read_text(encoding="utf-8"))
    state = {"attempt": attempt, "phase": phase, "utc": datetime.now(timezone.utc).isoformat(), "cid": CID,
             "commands": [], "cleanup_incomplete": False, "exit": None,
             "batch_seconds_budget": child_budget, "deadline_monotonic": deadline,
             "scenarios_frozen": scenarios[phase], "new_containers": 0, "new_volumes": 0,
             "windows_sessions": 0,
             "credential_lifecycle": "task role password rotated per batch via psql stdin; never argv/log; no old Env read"}
    before = hashes()
    write(folder / "as-run-hashes.json", {"before": before})
    budget["real_attempts"].append({"attempt": attempt, "phase": phase,
                                    "path": folder.relative_to(ROOT).as_posix(), "state": "preflight"})
    write(budget_file, budget)
    children = []
    started_owned = False
    password = secrets.token_hex(24)
    docker_path = shutil.which("docker") or "docker"

    def docker(args, *, input_text=None, cleanup=False, timeout=20, allow_failure=False):
        allowed_until = deadline if cleanup else deadline - 180
        remaining = allowed_until - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("batch cleanup reserve reached")
        began = time.monotonic()
        entry = {"args": args, "started_utc": datetime.now(timezone.utc).isoformat()}
        state["commands"].append(entry)
        write(folder / "manifest.json", state)
        try:
            result = subprocess.run([docker_path, *args], input=input_text, text=True, encoding="utf-8",
                                    capture_output=True, timeout=min(timeout, remaining),
                                    creationflags=subprocess.CREATE_NO_WINDOW)
            entry["exit"] = result.returncode
            if result.returncode and not allow_failure:
                raise RuntimeError("docker step failed: " + args[0])
            return result.returncode if allow_failure else result.stdout.strip()
        finally:
            entry["seconds"] = time.monotonic() - began
            write(folder / "manifest.json", state)

    def inspect(cid, cleanup=False):
        raw = docker(["inspect", cid, "--format", FORMAT], cleanup=cleanup)
        return dict(zip(KEYS, [json.loads(x) for x in raw.split("|")], strict=True))

    try:
        current = inspect(CID)
        state["preflight"] = current
        expected = {"Id": CID, "Name": "/" + NAME, "Image": IMAGE,
                    "HostConfig.PortBindings": {"5432/tcp": [{"HostIp": "127.0.0.1", "HostPort": "55441"}]},
                    "HostConfig.NanoCpus": 1000000000, "HostConfig.Memory": 536870912,
                    "HostConfig.PidsLimit": 128, "HostConfig.RestartPolicy.Name": "no",
                    "HostConfig.Privileged": False, "State.Running": False, "State.Pid": 0}
        if any(current.get(key) != value for key, value in expected.items()):
            raise RuntimeError("exact resource safety configuration mismatch")
        mounts = current["Mounts"]
        if len(mounts) != 1 or any(mounts[0].get(key) != value for key, value in {
                "Type": "volume", "Name": VOLUME, "Destination": "/var/lib/postgresql/data", "RW": True}.items()):
            raise RuntimeError("exact mount safety configuration mismatch")
        with socket.socket() as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            sock.bind(("127.0.0.1", 55441))
        started_owned = True
        budget["container_starts"] += 1
        write(budget_file, budget)
        docker(["start", CID])
        state["started"] = inspect(CID)
        ready_until = min(deadline - 180, time.monotonic() + 25)
        while docker(["exec", CID, "pg_isready", "-U", ADMIN, "-d", "postgres"], allow_failure=True, timeout=5):
            if time.monotonic() >= ready_until:
                raise TimeoutError("database readiness")
            time.sleep(.25)
        psql = ["exec", "-i", "-e", "PGOPTIONS=-c statement_timeout=10000 -c lock_timeout=2000",
                CID, "psql", "-X", "-q", "-v", "ON_ERROR_STOP=1", "-U", ADMIN, "-d", "postgres", "-t", "-A"]
        probe = ("SELECT json_build_object("
                 f"'tools_owner',(SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname='{TOOLS_DB}'),"
                 f"'upgrade_owner',(SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname='{UPGRADE_DB}'),"
                 f"'role',(SELECT json_build_array(rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls,rolinherit) FROM pg_roles WHERE rolname='{ROLE}'),"
                 f"'sessions',(SELECT count(*) FROM pg_stat_activity WHERE datname IN ('{TOOLS_DB}','{UPGRADE_DB}') OR usename='{ROLE}'),"
                 f"'memberships',(SELECT count(*) FROM pg_auth_members WHERE member=(SELECT oid FROM pg_roles WHERE rolname='{ROLE}')));")
        identity = json.loads(docker(psql, input_text=probe))
        state["database_preflight"] = identity
        prior_states = []
        for prior in budget["real_attempts"][:-1]:
            record = ROOT / prior["path"]
            if record.is_dir():
                prior_states.append(json.loads((record / "manifest.json").read_text(encoding="utf-8")))
        prior_owned_dbs = set()
        for x in prior_states:
            value = x.get("new_database")
            if isinstance(value, list):
                prior_owned_dbs.update(value)
            elif isinstance(value, str):
                prior_owned_dbs.add(value)
        prior_intent = any(x.get("setup_ddl_intent") for x in prior_states)
        existing_dbs = [name for name, owner in ((TOOLS_DB, identity["tools_owner"]), (UPGRADE_DB, identity["upgrade_owner"]))
                        if owner is not None]
        if identity["role"] is None and not existing_dbs and not prior_intent:
            state["setup_ddl_intent"] = {"databases": [TOOLS_DB, UPGRADE_DB], "role": ROLE}
            write(folder / "manifest.json", state)
            docker(psql, input_text=(
                f"CREATE ROLE {ROLE} LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD '{password}';\n"
                f"CREATE DATABASE {TOOLS_DB} OWNER {ROLE};\n"
                f"CREATE DATABASE {UPGRADE_DB} OWNER {ROLE};"))
            state["new_database"] = [TOOLS_DB, UPGRADE_DB]
            state["new_role"] = ROLE
        else:
            owned = all(name in prior_owned_dbs for name in existing_dbs) and identity["role"] is not None
            expected_role = [True, False, False, False, False, False, False]
            if not owned or identity["role"] != expected_role or identity["sessions"] != 0 or identity["memberships"] != 0:
                raise RuntimeError("existing target ownership or privilege mismatch")
            docker(psql, input_text=f"ALTER ROLE {ROLE} PASSWORD '{password}';")
        state["credential_initialized_or_rotated_once"] = True
        from psycopg.conninfo import make_conninfo
        common = dict(host="127.0.0.1", port=55441, user=ROLE, password=password, connect_timeout=2,
                      options="-c statement_timeout=15000 -c lock_timeout=10000")
        dsn_tools = make_conninfo(dbname=TOOLS_DB, **common)
        dsn_upgrade = make_conninfo(dbname=UPGRADE_DB, **common)
        env = {k: v for k, v in os.environ.items()
               if not (k.startswith("RETROLUME_") and ("DSN" in k or "DATABASE" in k))}
        env["RETROLUME_TOOL_TEST_DATABASE_URL"] = dsn_tools
        env["RETROLUME_TOOL_UPGRADE_TEST_DATABASE_URL"] = dsn_upgrade
        if phase == "pg":
            # 受影响的旧模型路径定向回归映射到同一工具库，不读取任何用户连接。
            env["RETROLUME_ACTIVITY_RESULTS_TEST_DATABASE_URL"] = dsn_tools
            env["RETROLUME_TIME_BUDGET_TEST_DATABASE_URL"] = dsn_tools
        env["TASK092_EVIDENCE"] = str(folder)
        env["TASK092_NEW_DB"] = "1" if state.get("new_database") else "0"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        if phase in ("retry_upgrade", "final"):
            env["TASK092_PG_TARGETS"] = json.dumps(RETRY_TARGETS)
        state["children"] = []
        state["exit"] = 0
        for child_name, label in PHASES[phase]["children"]:
            child = ControlledChild()
            children.append((label, child))
            state["process"] = child.start(
                [sys.executable, "-B", str(HERE / child_name), "--child", str(folder)],
                cwd=BACKEND, env=env, deadline=deadline - 180)
            budget["active_processes"] = [state["process"]]
            write(budget_file, budget)
            write(folder / "manifest.json", state)
            exit_code = child.wait_empty(deadline - 180)
            state["children"].append({"label": label, "script": child_name, "exit": exit_code,
                                      "process": state["process"]})
            if exit_code != 0 and state["exit"] == 0:
                # 冻结场景清单连续运行：失败不清空后续场景，但不重试失败子批。
                state["exit"] = exit_code
            write(folder / "manifest.json", state)
    except BaseException as exc:
        state["error_type"] = type(exc).__name__
        if type(exc) in (RuntimeError, TimeoutError):
            state["error"] = str(exc)
    finally:
        all_stdout = []
        for label, child in children:
            try:
                child.stop(deadline - 30)
                tree_zero = child.active() == 0
                child.close()
                state.setdefault("outer_tree_zero", True)
                state["outer_tree_zero"] = state["outer_tree_zero"] and tree_zero
                state.setdefault("outer_handles_closed", True)
            except BaseException as exc:
                state["cleanup_incomplete"] = True
                state["child_cleanup_error"] = type(exc).__name__
            for reader in child.readers:
                reader.join(timeout=1)
            logs = {"stdout": [], "stderr": []}
            while True:
                try:
                    stream, line = child.lines.get_nowait()
                except queue.Empty:
                    break
                if line is not None:
                    logs[stream].append(line.replace(password, "[redacted]"))
            for stream, lines in logs.items():
                (folder / (label + "-" + stream + ".log")).write_text("".join(lines), encoding="utf-8")
            all_stdout.extend(logs["stdout"])
            state.setdefault("process_events", []).extend(child.events)
        state["windows_sessions"] = sum('"windows_session_attempt"' in line for line in all_stdout)
        if started_owned:
            try:
                docker(["stop", "--time", "10", CID], cleanup=True, timeout=25)
                state["final_resource"] = inspect(CID, cleanup=True)
                state["container_stopped"] = (state["final_resource"]["State.Running"] is False
                                              and state["final_resource"]["State.Pid"] == 0)
                if not state["container_stopped"]:
                    state["cleanup_incomplete"] = True
            except BaseException as exc:
                state["cleanup_incomplete"] = True
                state["container_cleanup_error"] = type(exc).__name__
        else:
            state["container_started_by_task"] = False
        after = hashes()
        write(folder / "post-hashes.json", {"after": after})
        write(folder / "parent-loaded-source.json", loaded_bytes)
        if before != after:
            state["source_changed_during_batch"] = True
        state["seconds"] = time.monotonic() - start
        state["end_utc"] = datetime.now(timezone.utc).isoformat()
        write(folder / "manifest.json", state)
        budget["real_used_seconds"] += state["seconds"]
        budget["windows_sessions"] += state["windows_sessions"]
        budget["real_attempts"][-1].update(state="finished", seconds=state["seconds"], exit=state["exit"],
                                           cleanup_incomplete=state["cleanup_incomplete"])
        if not state["cleanup_incomplete"]:
            budget["active_processes"] = []
        write(budget_file, budget)
        ledger_file = EVIDENCE / "attempt-ledger.json"
        ledger = json.loads(ledger_file.read_text(encoding="utf-8-sig"))
        ledger["entries"].append({
            "attempt": attempt, "phase": phase, "path": folder.relative_to(ROOT).as_posix(),
            "command": f"{Path(sys.executable).name} -B batch_runner.py --phase {phase}",
            "start_utc": state["utc"], "end_utc": state["end_utc"], "seconds": state["seconds"],
            "deadline_seconds": child_budget, "exit": state["exit"],
            "windows_sessions": state["windows_sessions"],
            "scenarios": scenarios[phase], "source_changed": state.get("source_changed_during_batch", False),
            "fault_injection": scenarios[phase].get("fault_injection"),
            "cleanup": {"container_stopped": state.get("container_stopped"),
                        "cleanup_incomplete": state["cleanup_incomplete"]},
        })
        write(ledger_file, ledger)
    print(json.dumps({k: state.get(k) for k in ("exit", "error_type", "error", "seconds", "outer_tree_zero",
                    "outer_handles_closed", "container_stopped", "cleanup_incomplete", "windows_sessions")}))
    return 0 if state["exit"] == 0 and state.get("container_stopped") and not state["cleanup_incomplete"] else 1


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] != "--phase":
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[2]))
