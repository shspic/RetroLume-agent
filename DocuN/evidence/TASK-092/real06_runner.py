"""续作03 E2专用最小入口：real-06一次——最终版11个缺证工具PG方法定向运行。

依据：TASK-092置顶续作03 E2回退条款——项目内未找到real-01旧夹具原件，哈希仲裁
逆向重建尝试（160结构化变体，完整SHA256全部不中）未果，启用授权内一次定向PG：
对最终版适用性缺证的11项ToolPostgresTests方法运行（排除已由real-03最终版真实
通过的c7/c9）；4项旧model回归文件hash与real-01一致，直接复用不跟随重跑。
总尝试上限6（本入口为第6次）、原容器第6次启动（上限6）；业务180秒+收尾120秒、
总截止300秒；只访问retrolume_task092_tools与task092_synth，不运行迁移/upgrade、
不重建schema/数据库；Windows业务会话新增0；费用0。失败即收尾交回，不暗开real07。
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
from real06_child import TARGETS  # noqa: E402

CID = "e49d3acc3c1be13d670af68bca2b082fea4faeeb9b9babe69df7f1d3941696a4"
IMAGE = "sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f"
NAME = "retrolume-task-088-g3-w1"
VOLUME = NAME + "-data"
TOOLS_DB = "retrolume_task092_tools"
ROLE = "retrolume_task092_synth"
ADMIN = "retrolume_task088_synth"

BUSINESS_SECONDS = 180
CLEANUP_SECONDS = 120
TOTAL_SECONDS = BUSINESS_SECONDS + CLEANUP_SECONDS
AUTHORIZATION = (
    "TASK-092续作03 E2回退条款：real-06一次入口+原容器一次启动；总尝试与启动上限6；"
    "业务180秒+收尾120秒、总截止300秒；仅工具库与task092_synth；Windows会话0；费用0。"
)
REASON = "real-01旧夹具原件未存档且哈希仲裁重建未果；对最终版冻结11个缺证方法定向复跑，c7/c9已由real-03最终版通过故排除；4项旧model回归文件hash一致直接复用"


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


def main() -> int:
    budget_file = EVIDENCE / "budget-manifest.json"
    budget = json.loads(budget_file.read_text(encoding="utf-8-sig"))
    prior = budget["real_attempts"]
    if len(prior) != 5 or any(x.get("state") != "finished" for x in prior):
        raise RuntimeError("continuation-03 entry requires the five historical batches finished")
    if budget["active_processes"]:
        raise RuntimeError("active processes recorded; recover first")
    if budget.get("continuation_03_e2_used"):
        raise RuntimeError("continuation-03 entry already used; no real-07")
    if budget["container_starts"] >= 6 or budget["real_used_seconds"] + TOTAL_SECONDS > 3600:
        raise RuntimeError("cumulative real budget unavailable")
    folder = EVIDENCE / "real-06"
    if folder.exists():
        raise RuntimeError("real-06 already exists")
    attempt = 6
    start = time.monotonic()
    total_deadline = start + TOTAL_SECONDS
    business_deadline = start + BUSINESS_SECONDS
    cumulative_before = {"real_used_seconds": budget["real_used_seconds"],
                         "real_attempts": len(prior), "container_starts": budget["container_starts"],
                         "windows_sessions": budget["windows_sessions"],
                         "offline_used_seconds": budget["offline_used_seconds"]}
    # 一次调用立即记第6次尝试，预检失败也占槽。
    folder.mkdir(exist_ok=False)
    budget["continuation_03_e2_used"] = True
    budget["real_attempts"].append({"attempt": attempt, "phase": "continuation_03_e2",
                                    "path": folder.relative_to(ROOT).as_posix(), "state": "preflight"})
    write(budget_file, budget)
    state = {"attempt": attempt, "phase": "continuation_03_e2",
             "utc": datetime.now(timezone.utc).isoformat(), "cid": CID,
             "authorization": AUTHORIZATION, "reason_frozen": REASON,
             "targets_frozen": TARGETS,
             "cumulative_before": cumulative_before,
             "business_seconds_budget": BUSINESS_SECONDS, "cleanup_seconds_budget": CLEANUP_SECONDS,
             "total_seconds_budget": TOTAL_SECONDS,
             "commands": [], "cleanup_incomplete": False, "exit": None,
             "new_containers": 0, "new_volumes": 0, "windows_sessions": 0,
             "credential_lifecycle": "task role password rotated via psql stdin; never argv/log; no Env read"}
    before = hashes()
    write(folder / "as-run-hashes.json", {"before": before})
    children = []
    started_owned = False
    password = secrets.token_hex(24)
    docker_path = shutil.which("docker") or "docker"

    def docker(args, *, input_text=None, cleanup=False, timeout=20, allow_failure=False):
        allowed_until = total_deadline if cleanup else business_deadline
        remaining = allowed_until - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("batch deadline reserve reached")
        began = time.monotonic()
        entry = {"args": args if args[0] != "exec" else args[:4] + ["psql(...)"],
                 "started_utc": datetime.now(timezone.utc).isoformat()}
        state["commands"].append(entry)
        write(folder / "manifest.json", state)
        try:
            result = subprocess.run([docker_path, *args], input=input_text, text=True, encoding="utf-8",
                                    capture_output=True, timeout=min(timeout, remaining),
                                    creationflags=subprocess.CREATE_NO_WINDOW)
            entry["exit"] = result.returncode
            if result.returncode and not allow_failure:
                raise RuntimeError("docker step failed: " + args[0])
            return result.returncode if allow_failure else result.stdout
        finally:
            entry["seconds"] = time.monotonic() - began
            write(folder / "manifest.json", state)

    def inspect(cid, cleanup=False):
        parsed = json.loads(docker(["inspect", cid], cleanup=cleanup))[0]
        host = parsed.get("HostConfig") or {}
        mounts_raw = parsed.get("Mounts")
        mounts = None if mounts_raw is None else [
            {k: m.get(k) for k in ("Type", "Name", "Destination", "RW")} for m in mounts_raw]
        return {"Id": parsed.get("Id"), "Name": parsed.get("Name"), "Image": parsed.get("Image"),
                "State": {k: (parsed.get("State") or {}).get(k) for k in ("Running", "Pid", "StartedAt")},
                "HostConfig": {k: host.get(k) for k in ("NanoCpus", "Memory", "PidsLimit", "Privileged", "PortBindings")},
                "RestartPolicyName": (host.get("RestartPolicy") or {}).get("Name"),
                "Mounts": mounts}

    def validate_preflight(current):
        expected = {"Id": CID, "Name": "/" + NAME, "Image": IMAGE,
                    "State.Running": False, "State.Pid": 0,
                    "HostConfig.NanoCpus": 1000000000, "HostConfig.Memory": 536870912,
                    "HostConfig.PidsLimit": 128, "HostConfig.Privileged": False,
                    "RestartPolicyName": "no",
                    "HostConfig.PortBindings": {"5432/tcp": [{"HostIp": "127.0.0.1", "HostPort": "55441"}]}}
        got = {"Id": current["Id"], "Name": current["Name"], "Image": current["Image"],
               "State.Running": current["State"]["Running"], "State.Pid": current["State"]["Pid"],
               "HostConfig.NanoCpus": current["HostConfig"]["NanoCpus"],
               "HostConfig.Memory": current["HostConfig"]["Memory"],
               "HostConfig.PidsLimit": current["HostConfig"]["PidsLimit"],
               "HostConfig.Privileged": current["HostConfig"]["Privileged"],
               "RestartPolicyName": current["RestartPolicyName"],
               "HostConfig.PortBindings": current["HostConfig"]["PortBindings"]}
        mismatches = {k: (got.get(k), v) for k, v in expected.items() if got.get(k) != v}
        if mismatches:
            raise RuntimeError("exact resource safety configuration mismatch: " + ",".join(sorted(mismatches)))
        mounts = current["Mounts"]
        if mounts is None or len(mounts) != 1 or any(mounts[0].get(key) != value for key, value in {
                "Type": "volume", "Name": VOLUME, "Destination": "/var/lib/postgresql/data", "RW": True}.items()):
            raise RuntimeError("exact mount safety configuration mismatch")

    finalized: set[str] = set()
    all_stdout: list[str] = []

    def finalize_child(label, child) -> bool:
        if label in finalized:
            return state["child_finalized"][label]["clean"]
        clean = True
        try:
            try:
                child.stop(total_deadline)
            except TimeoutError:
                child.stop(time.monotonic() + 30)
            tree_zero = (child.active() == 0) if (child.assigned and child.job) else True
            child.close()
            state.setdefault("outer_tree_zero", True)
            state["outer_tree_zero"] = state["outer_tree_zero"] and tree_zero
            state.setdefault("outer_handles_closed", True)
        except BaseException as exc:
            clean = False
            state["cleanup_incomplete"] = True
            state["outer_handles_closed"] = False
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
        state.setdefault("child_finalized", {})[label] = {"clean": clean, "stdout_lines": len(logs["stdout"])}
        finalized.add(label)
        return clean

    try:
        current = inspect(CID)
        state["preflight"] = current
        validate_preflight(current)
        with socket.socket() as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            sock.bind(("127.0.0.1", 55441))
        started_owned = True
        budget["container_starts"] += 1
        write(budget_file, budget)
        docker(["start", CID])
        state["started"] = inspect(CID)
        ready_until = min(business_deadline, time.monotonic() + 25)
        while docker(["exec", CID, "pg_isready", "-U", ADMIN, "-d", "postgres"], allow_failure=True, timeout=5):
            if time.monotonic() >= ready_until:
                raise TimeoutError("database readiness")
            time.sleep(.25)
        psql = ["exec", "-i", "-e", "PGOPTIONS=-c statement_timeout=10000 -c lock_timeout=2000",
                CID, "psql", "-X", "-q", "-v", "ON_ERROR_STOP=1", "-U", ADMIN, "-d", "postgres", "-t", "-A"]
        probe = ("SELECT json_build_object("
                 f"'tools_owner',(SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname='{TOOLS_DB}'),"
                 f"'role',(SELECT json_build_array(rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls,rolinherit) FROM pg_roles WHERE rolname='{ROLE}'),"
                 f"'sessions',(SELECT count(*) FROM pg_stat_activity WHERE datname='{TOOLS_DB}' OR usename='{ROLE}'),"
                 f"'memberships',(SELECT count(*) FROM pg_auth_members WHERE member=(SELECT oid FROM pg_roles WHERE rolname='{ROLE}')));")
        identity = json.loads(docker(psql, input_text=probe))
        state["database_preflight"] = identity
        expected_role = [True, False, False, False, False, False, False]
        if (identity["tools_owner"] != ROLE or identity["role"] != expected_role
                or identity["sessions"] != 0 or identity["memberships"] != 0):
            raise RuntimeError("existing target ownership or privilege mismatch")
        docker(psql, input_text=f"ALTER ROLE {ROLE} PASSWORD '{password}';")
        state["credential_rotated_once"] = True
        from psycopg.conninfo import make_conninfo
        env = {k: v for k, v in os.environ.items()
               if not (k.startswith("RETROLUME_") and ("DSN" in k or "DATABASE" in k))}
        env["RETROLUME_TOOL_TEST_DATABASE_URL"] = make_conninfo(
            host="127.0.0.1", port=55441, dbname=TOOLS_DB, user=ROLE, password=password,
            connect_timeout=2, options="-c statement_timeout=15000 -c lock_timeout=10000")
        env["TASK092_EVIDENCE"] = str(folder)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        state["children"] = []
        child = ControlledChild()
        children.append(("e2_child", child))
        state["process"] = child.start(
            [sys.executable, "-B", str(HERE / "real06_child.py"), "--child", str(folder)],
            cwd=BACKEND, env=env, deadline=business_deadline)
        budget["active_processes"] = [state["process"]]
        write(budget_file, budget)
        write(folder / "manifest.json", state)
        exit_code = child.wait_empty(business_deadline)
        child_clean = finalize_child("e2_child", child)
        state["children"].append({"label": "e2_child", "exit": exit_code,
                                  "cleanup_confirmed": child_clean, "process": state["process"]})
        state["exit"] = exit_code
        if not child_clean:
            state["child_stopped_batch"] = "e2_child"
    except BaseException as exc:
        state["error_type"] = type(exc).__name__
        if type(exc) in (RuntimeError, TimeoutError):
            state["error"] = str(exc)
    finally:
        for label, child in children:
            finalize_child(label, child)
            state.setdefault("process_events", []).extend(child.events)
        state["windows_sessions"] = sum('"windows_session_attempt"' in line for line in all_stdout)
        if state["windows_sessions"] != 0:
            state["windows_sessions_violation"] = True
            state["cleanup_incomplete"] = True
        if started_owned:
            try:
                docker(["stop", "--time", "10", CID], cleanup=True, timeout=25)
                state["final_resource"] = inspect(CID, cleanup=True)
                state["container_stopped"] = (state["final_resource"]["State"]["Running"] is False
                                              and state["final_resource"]["State"]["Pid"] == 0)
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
        state["cumulative_after"] = {"real_used_seconds": budget["real_used_seconds"] + state["seconds"],
                                     "real_attempts": len(budget["real_attempts"]),
                                     "container_starts": budget["container_starts"],
                                     "windows_sessions": budget["windows_sessions"] + state["windows_sessions"]}
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
            "attempt": attempt, "phase": "continuation_03_e2",
            "path": folder.relative_to(ROOT).as_posix(),
            "command": f"{Path(sys.executable).name} -B real06_runner.py",
            "start_utc": state["utc"], "end_utc": state["end_utc"], "seconds": state["seconds"],
            "deadline_seconds": TOTAL_SECONDS, "exit": state["exit"],
            "windows_sessions": state["windows_sessions"],
            "scenarios": {"frozen_targets": TARGETS, "reason": REASON},
            "source_changed": state.get("source_changed_during_batch", False),
            "continuation": {"authorization": AUTHORIZATION, "cumulative_before": cumulative_before,
                             "cumulative_after": state["cumulative_after"]},
            "cleanup": {"container_stopped": state.get("container_stopped"),
                        "cleanup_incomplete": state["cleanup_incomplete"]}})
        write(ledger_file, ledger)
    print(json.dumps({k: state.get(k) for k in ("exit", "error_type", "error", "seconds", "outer_tree_zero",
                    "container_stopped", "cleanup_incomplete", "windows_sessions")}))
    return 0 if state["exit"] == 0 and state.get("container_stopped") and not state["cleanup_incomplete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
