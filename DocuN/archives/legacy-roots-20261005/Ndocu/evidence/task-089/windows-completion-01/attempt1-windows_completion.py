"""TASK089 Windows-only completion; exact existing target, one authorized role rotation, outer Job."""
from pathlib import Path
from datetime import datetime, timezone
import json
import os
import queue
import secrets
import shutil
import socket
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))
from controlled_child import ControlledChild
from offline import hashes, write

EVIDENCE = ROOT / "Ndocu/evidence/task-089"
CID = "e49d3acc3c1be13d670af68bca2b082fea4faeeb9b9babe69df7f1d3941696a4"
IMAGE = "sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f"
NAME = "retrolume-task-088-g3-w1"
VOLUME = NAME + "-data"
DB = "retrolume_task089_g3"
ROLE = "retrolume_task089_synth"
ADMIN = "retrolume_task088_synth"
KEYS = ("Id", "Name", "Image", "Mounts", "HostConfig.PortBindings", "HostConfig.NanoCpus",
        "HostConfig.Memory", "HostConfig.PidsLimit", "HostConfig.RestartPolicy.Name",
        "HostConfig.Privileged", "State.Running", "State.Pid", "State.StartedAt")
FORMAT = "|".join("{{json ." + key + "}}" for key in KEYS)


def cases(folder):
    import psycopg
    os.environ["TASK089_EVIDENCE"] = str(folder)
    before = hashes()
    write(folder / "as-run-hashes.json", before)
    with psycopg.connect(os.environ["RETROLUME_ACTIVITY_RESULTS_TEST_DATABASE_URL"]) as conn:
        assert conn.execute("SELECT current_database(),current_user").fetchone() == (DB, ROLE)
        for table in ("material_sources","material_versions","activities","activity_operations","activity_operation_results"):
            assert conn.execute("SELECT to_regclass(%s)",(table,)).fetchone()[0]
        conn.execute("SELECT payload_sha256,admission_id,execution_generation,scope_revision FROM activity_operation_results LIMIT 0")
    print(json.dumps({"event":"windows_session_attempt","count":1}),flush=True)
    import importlib.machinery, hashlib
    loaded_bytes={}
    original_get_code=importlib.machinery.SourceFileLoader.get_code
    def capture_code(self, fullname):
        if fullname == "app" or fullname.startswith("app."):
            path=Path(self.get_filename(fullname)).resolve()
            raw=self.get_data(str(path))
            loaded_bytes[path.relative_to(ROOT).as_posix()]=hashlib.sha256(raw).hexdigest()
            return self.source_to_code(raw,str(path))
        return original_get_code(self,fullname)
    importlib.machinery.SourceFileLoader.get_code=capture_code
    import win_chain
    # Passive trace records executed product lines without replacing methods or outcomes.
    trace=[]
    def observe(frame,event,arg):
        path=Path(frame.f_code.co_filename)
        if event == "line" and path.name == "session.py" and "app" in path.parts:
            trace.append({"line":frame.f_lineno,"time_ns":time.monotonic_ns()})
        return observe
    sys.settrace(observe)
    try:
        code=win_chain.main()
    finally:
        sys.settrace(None)
        write(folder / "parent-loaded-source.json",loaded_bytes)
        write(folder / "session-line-trace.json",trace)
        write(folder / "post-hashes.json",hashes())
    assert before == hashes(), "source drift"
    records=[json.loads(p.read_text()) for p in folder.glob("bootstrap-*.json")]
    assert len(records)==2 and {x["mode"] for x in records}=={"sup","worker"}
    for record in records:
        assert record["source_unchanged"]
        assert record["loaded_source_bytes"]
        for name,digest in record["loaded_source_bytes"].items():
            assert before[name]==digest
        if record["mode"]=="worker": assert record["transport_sends"]==1
    return code


def main():
    budget_file = EVIDENCE / "budget-manifest.json"
    budget = json.loads(budget_file.read_text(encoding="utf-8-sig"))
    if len(budget["real_attempts"]) >= 3 or budget["real_used_seconds"] + 300 > 2400:
        raise RuntimeError("real budget unavailable")
    completion_attempts=[x for x in budget["real_attempts"] if "windows-completion-01" in x["path"]]
    if len(completion_attempts)>=2 or sum(x.get("seconds",300) for x in completion_attempts)+300>600:
        raise RuntimeError("completion segment budget unavailable")
    folder = EVIDENCE / "windows-completion-01" / ("attempt-"+str(len(completion_attempts)+1))
    folder.mkdir(exist_ok=False)
    attempt=len(budget["real_attempts"])+1
    start = time.monotonic()
    deadline = start + 300
    state = {"attempt": attempt, "utc": datetime.now(timezone.utc).isoformat(), "cid": CID,
             "commands": [], "cleanup_incomplete": False, "exit": None,
             "new_containers": 0, "new_volumes": 0, "windows_sessions": 0,
             "credential_lifecycle": "explicitly authorized task role password rotation only owner memory, psql stdin and controlled child env; never argv/log; no old Env read"}
    budget["credential_stop_gate_superseded_by"]="2026-09-29 Windows completion 01 explicit task role rotation authorization"
    budget["real_attempts"].append({"attempt": attempt, "path": folder.relative_to(ROOT).as_posix(), "state": "preflight"})
    write(budget_file, budget)
    child = None
    started_owned = False
    password = secrets.token_hex(24)
    docker_path = shutil.which("docker")
    if not docker_path:
        docker_path = "docker"

    def docker(args, *, input_text=None, cleanup=False, timeout=20, allow_failure=False):
        allowed_until = deadline if cleanup else deadline - 60
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
                # 不写psql错误文本/输入，避免角色DDL中的新口令进入证据。
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
        # 标记先于启动，启动响应丢失也只对已核停止且获准CID作收尾。
        started_owned = True
        docker(["start", CID])
        state["started"] = inspect(CID)
        ready_until = min(deadline - 60, time.monotonic() + 25)
        while docker(["exec", CID, "pg_isready", "-U", ADMIN, "-d", "postgres"], allow_failure=True, timeout=5):
            if time.monotonic() >= ready_until: raise TimeoutError("database readiness")
            time.sleep(.25)
        psql = ["exec", "-i", "-e", "PGOPTIONS=-c statement_timeout=10000 -c lock_timeout=2000",
                CID, "psql", "-X", "-q", "-v", "ON_ERROR_STOP=1", "-U", ADMIN, "-d", "postgres"]
        psql += ["-t", "-A"]
        identity_sql = "SELECT json_build_object('owner',(SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname='retrolume_task089_g3'),'role',(SELECT json_build_array(rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls) FROM pg_roles WHERE rolname='retrolume_task089_synth'),'sessions',(SELECT count(*) FROM pg_stat_activity WHERE datname='retrolume_task089_g3' OR usename='retrolume_task089_synth'),'memberships',(SELECT count(*) FROM pg_auth_members WHERE member=(SELECT oid FROM pg_roles WHERE rolname='retrolume_task089_synth')));"
        identity=json.loads(docker(psql,input_text=identity_sql))
        state["database_preflight"]=identity
        if identity != {"owner":ROLE,"role":[True,False,False,False,False,False],"sessions":0,"memberships":0}:
            raise RuntimeError("existing target ownership or privilege mismatch")
        docker(psql,input_text=f"ALTER ROLE {ROLE} PASSWORD '{password}';")
        state["credential_rotated_once"]=True
        from psycopg.conninfo import make_conninfo
        dsn = make_conninfo(host="127.0.0.1", port=55441, dbname=DB, user=ROLE, password=password,
                           connect_timeout=2, options="-c statement_timeout=15000 -c lock_timeout=10000")
        env = {k: v for k, v in os.environ.items()
               if not (k.startswith("RETROLUME_") and ("DSN" in k or "DATABASE" in k))}
        env["RETROLUME_ACTIVITY_RESULTS_TEST_DATABASE_URL"] = dsn
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        child = ControlledChild()
        state["process"] = child.start([sys.executable, "-B", str(Path(__file__).resolve()), "--cases", str(folder)],
                                       cwd=BACKEND, env=env, deadline=deadline - 60)
        budget["active_processes"] = [state["process"]]
        write(budget_file, budget)
        write(folder / "manifest.json", state)
        state["exit"] = child.wait_empty(deadline - 60)
    except BaseException as exc:
        state["error_type"] = type(exc).__name__
        if type(exc) in (RuntimeError, TimeoutError): state["error"] = str(exc)
    finally:
        if child is not None:
            try:
                child.stop(deadline - 30)
                state["outer_tree_zero"] = child.active() == 0
                child.close()
                state["outer_handles_closed"] = True
            except BaseException as exc:
                state["cleanup_incomplete"] = True
                state["child_cleanup_error"] = type(exc).__name__
            for reader in child.readers: reader.join(timeout=1)
            logs = {"stdout": [], "stderr": []}
            while True:
                try: label, line = child.lines.get_nowait()
                except queue.Empty: break
                if line is not None: logs[label].append(line.replace(password, "[redacted]"))
            for label, lines in logs.items():
                (folder / (label + ".log")).write_text("".join(lines), encoding="utf-8")
            state["windows_sessions"] = sum('"windows_session_attempt"' in line for line in logs["stdout"])
            state["process_events"] = child.events
        if started_owned:
            try:
                docker(["stop", "--time", "10", CID], cleanup=True, timeout=25)
                state["final_resource"] = inspect(CID, cleanup=True)
                state["container_stopped"] = state["final_resource"]["State.Running"] is False and state["final_resource"]["State.Pid"] == 0
                if not state["container_stopped"]: state["cleanup_incomplete"] = True
            except BaseException as exc:
                state["cleanup_incomplete"] = True
                state["container_cleanup_error"] = type(exc).__name__
        else:
            state["container_started_by_task"] = False
        state["seconds"] = time.monotonic() - start
        state["end_utc"] = datetime.now(timezone.utc).isoformat()
        write(folder / "manifest.json", state)
        budget["real_used_seconds"] += state["seconds"]
        budget["windows_sessions"] += state["windows_sessions"]
        budget["real_attempts"][-1].update(state="finished", seconds=state["seconds"], exit=state["exit"],
                                            cleanup_incomplete=state["cleanup_incomplete"])
        if not state["cleanup_incomplete"]: budget["active_processes"] = []
        write(budget_file, budget)
    print(json.dumps({k: state.get(k) for k in ("exit", "error_type", "error", "seconds", "outer_tree_zero",
                    "outer_handles_closed", "container_stopped", "cleanup_incomplete", "windows_sessions")}))
    return 0 if state["exit"] == 0 and state.get("container_stopped") and not state["cleanup_incomplete"] else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cases":
        try: code=cases(Path(sys.argv[2]))
        except BaseException as exc:
            print(json.dumps({"event":"case_error","type":type(exc).__name__,"label":str(exc) if type(exc) is AssertionError else None}),flush=True)
            code=1
        raise SystemExit(code)
    raise SystemExit(main())
