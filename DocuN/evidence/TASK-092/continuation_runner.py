"""TASK-092 续作01独立入口：一次real-04批（upgrade收尾子批 + Windows六方向）。

依据：TASK-092卡置顶续作01“唯一真实批与运行许可”——累计上限从3增4批次/启动，
不重置历史；本批业务运行最多300秒，加收尾最多120秒，入口总截止420秒；
Windows本轮最多6会话。本入口只调度 upgrade_child.py 与 win_chain.py，
不调度 pg_retry/离线全量；一次调用立即记第4次尝试，预检失败也占槽。

Docker检查按原卡要求使用完整 inspect JSON 在内存解析白名单字段；只输出
白名单，不保存/打印 Env；缺安全字段失败关闭。旧 batch_runner.py 不改动。
用法：python continuation_runner.py
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

BUSINESS_SECONDS = 300
CLEANUP_SECONDS = 120
TOTAL_SECONDS = BUSINESS_SECONDS + CLEANUP_SECONDS
CONTINUATION_AUTHORIZATION = (
    "TASK-092续作01置顶：追加real-04一批及原容器一次启动，累计上限3→4，不重置历史；"
    "业务300秒+收尾120秒，入口总截止420秒；Windows本轮至多6会话；费用仍0。"
)
CHILDREN = [("upgrade_child.py", "upgrade_child"), ("win_chain.py", "windows_child")]


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
    if len(prior) != 3 or any(x.get("state") != "finished" for x in prior):
        raise RuntimeError("continuation entry requires the three historical batches finished")
    if budget["active_processes"]:
        raise RuntimeError("active processes recorded; recover first")
    if budget.get("continuation_01_used"):
        raise RuntimeError("continuation entry already used; no fifth batch")
    if budget["container_starts"] >= 4 or budget["real_used_seconds"] + TOTAL_SECONDS > 3600:
        raise RuntimeError("cumulative real budget unavailable")
    folder = EVIDENCE / "real-04"
    if folder.exists():
        raise RuntimeError("real-04 already exists")
    attempt = 4
    start = time.monotonic()
    total_deadline = start + TOTAL_SECONDS
    business_deadline = start + BUSINESS_SECONDS
    scenarios = json.loads((EVIDENCE / "scenario-manifest.json").read_text(encoding="utf-8"))
    cumulative_before = {"real_used_seconds": budget["real_used_seconds"],
                         "real_attempts": len(prior), "container_starts": budget["container_starts"],
                         "windows_sessions": budget["windows_sessions"],
                         "offline_used_seconds": budget["offline_used_seconds"]}
    # 一次调用立即记第4次，即使预检失败也占槽。
    folder.mkdir(exist_ok=False)
    budget["continuation_01_used"] = True
    budget["real_attempts"].append({"attempt": attempt, "phase": "continuation_01",
                                    "path": folder.relative_to(ROOT).as_posix(), "state": "preflight"})
    write(budget_file, budget)
    state = {"attempt": attempt, "phase": "continuation_01",
             "utc": datetime.now(timezone.utc).isoformat(), "cid": CID,
             "continuation_authorization": CONTINUATION_AUTHORIZATION,
             "cumulative_before": cumulative_before,
             "business_seconds_budget": BUSINESS_SECONDS, "cleanup_seconds_budget": CLEANUP_SECONDS,
             "total_seconds_budget": TOTAL_SECONDS,
             "scenarios_frozen": scenarios["continuation_01"],
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
        # 原卡要求：完整JSON在内存解析白名单；只输出白名单，不保存Env。
        parsed = json.loads(docker(["inspect", cid], cleanup=cleanup))[0]
        host = parsed.get("HostConfig") or {}
        mounts_raw = parsed.get("Mounts")
        mounts = None if mounts_raw is None else [
            {k: m.get(k) for k in ("Type", "Name", "Destination", "RW")} for m in mounts_raw]
        return {
            "Id": parsed.get("Id"),
            "Name": parsed.get("Name"),
            "Image": parsed.get("Image"),
            "State": {k: (parsed.get("State") or {}).get(k) for k in ("Running", "Pid", "StartedAt")},
            "HostConfig": {k: host.get(k) for k in ("NanoCpus", "Memory", "PidsLimit", "Privileged", "PortBindings")},
            "RestartPolicyName": (host.get("RestartPolicy") or {}).get("Name"),
            "Mounts": mounts,
        }

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
        """单次树停止/句柄关闭/日志收集；重复调用返回已记录的clean判定。"""
        if label in finalized:
            return state["child_finalized"][label]["clean"]
        clean = True
        try:
            try:
                child.stop(total_deadline)
            except TimeoutError:
                # 总截止已到也需要有界终止自有树；额外最多30秒且不跑新场景。
                child.stop(time.monotonic() + 30)
            # 未assign或已close的子进程其自有树已在子控制层确认，不重复查询已关闭句柄。
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
                 f"'upgrade_owner',(SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname='{UPGRADE_DB}'),"
                 f"'role',(SELECT json_build_array(rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls,rolinherit) FROM pg_roles WHERE rolname='{ROLE}'),"
                 f"'sessions',(SELECT count(*) FROM pg_stat_activity WHERE datname IN ('{TOOLS_DB}','{UPGRADE_DB}') OR usename='{ROLE}'),"
                 f"'memberships',(SELECT count(*) FROM pg_auth_members WHERE member=(SELECT oid FROM pg_roles WHERE rolname='{ROLE}')));")
        identity = json.loads(docker(psql, input_text=probe))
        state["database_preflight"] = identity
        expected_role = [True, False, False, False, False, False, False]
        if (identity["tools_owner"] != ROLE or identity["upgrade_owner"] != ROLE
                or identity["role"] != expected_role or identity["sessions"] != 0 or identity["memberships"] != 0):
            raise RuntimeError("existing target ownership or privilege mismatch")
        docker(psql, input_text=f"ALTER ROLE {ROLE} PASSWORD '{password}';")
        state["credential_rotated_once"] = True
        from psycopg.conninfo import make_conninfo
        common = dict(host="127.0.0.1", port=55441, user=ROLE, password=password, connect_timeout=2,
                      options="-c statement_timeout=15000 -c lock_timeout=10000")
        env = {k: v for k, v in os.environ.items()
               if not (k.startswith("RETROLUME_") and ("DSN" in k or "DATABASE" in k))}
        env["RETROLUME_TOOL_TEST_DATABASE_URL"] = make_conninfo(dbname=TOOLS_DB, **common)
        env["RETROLUME_TOOL_UPGRADE_TEST_DATABASE_URL"] = make_conninfo(dbname=UPGRADE_DB, **common)
        env["TASK092_EVIDENCE"] = str(folder)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        state["children"] = []
        state["exit"] = 0
        for child_name, label in CHILDREN:
            child = ControlledChild()
            children.append((label, child))
            state["process"] = child.start(
                [sys.executable, "-B", str(HERE / child_name), "--child", str(folder)],
                cwd=BACKEND, env=env, deadline=business_deadline)
            budget["active_processes"] = [state["process"]]
            write(budget_file, budget)
            write(folder / "manifest.json", state)
            exit_code = child.wait_empty(business_deadline)
            child_clean = finalize_child(label, child)
            state["children"].append({"label": label, "script": child_name, "exit": exit_code,
                                      "cleanup_confirmed": child_clean,
                                      "process": state["process"]})
            if exit_code != 0 and state["exit"] == 0:
                state["exit"] = exit_code
            if not child_clean:
                state["child_stopped_batch"] = label
                break
            if exit_code != 0 and label == "upgrade_child":
                # upgrade失败但库隔离且清理已确认：继续独立Windows方向。
                state["continue_after_upgrade_failure"] = True
            write(folder / "manifest.json", state)
    except BaseException as exc:
        state["error_type"] = type(exc).__name__
        if type(exc) in (RuntimeError, TimeoutError):
            state["error"] = str(exc)
    finally:
        for label, child in children:
            finalize_child(label, child)
            state.setdefault("process_events", []).extend(child.events)
        state["windows_sessions"] = sum('"windows_session_attempt"' in line for line in all_stdout)
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
            "attempt": attempt, "phase": "continuation_01",
            "path": folder.relative_to(ROOT).as_posix(),
            "command": f"{Path(sys.executable).name} -B continuation_runner.py",
            "start_utc": state["utc"], "end_utc": state["end_utc"], "seconds": state["seconds"],
            "deadline_seconds": TOTAL_SECONDS, "exit": state["exit"],
            "windows_sessions": state["windows_sessions"],
            "scenarios": scenarios["continuation_01"], "source_changed": state.get("source_changed_during_batch", False),
            "continuation": {"authorization": CONTINUATION_AUTHORIZATION,
                             "cumulative_before": cumulative_before,
                             "cumulative_after": state["cumulative_after"]},
            "cleanup": {"container_stopped": state.get("container_stopped"),
                        "cleanup_incomplete": state["cleanup_incomplete"]}})
        write(ledger_file, ledger)
    print(json.dumps({k: state.get(k) for k in ("exit", "error_type", "error", "seconds", "outer_tree_zero",
                    "container_stopped", "cleanup_incomplete", "windows_sessions")}))
    return 0 if state["exit"] == 0 and state.get("container_stopped") and not state["cleanup_incomplete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
