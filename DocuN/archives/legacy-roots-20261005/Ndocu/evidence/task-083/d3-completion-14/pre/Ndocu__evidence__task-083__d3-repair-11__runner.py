"""Future-only D3 continuation; requires separate resource authorization. Never creates a container."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import queue
import secrets
import socket
import subprocess
import sys
import time
from uuid import uuid4
import psycopg
ROOT=Path(r"D:/shspic/project_NO3_RetroLume-agent")
sys.path.insert(0,str(ROOT/"backend"))
from contracts import deadline_left, parse_parts, validate_records
from controlled_child import ControlledChild, OwnershipUnknown
EVID=ROOT/"Ndocu/evidence/task-083/d3-repair-11"
PY=ROOT/"backend/.venv/Scripts/python.exe"
FIXTURE=ROOT/"backend/tests/fixtures/task083/d3_pg_windows.py"
CID="85242648b70dc11839a93de29a51bc7e492390d8ad479036c141f37b26f4f6a7"
IMAGE="sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f"
VOLUME="11140b6c41401e2cef58ef2743357938db543c5891a3a8d68fce87a60cb85e07"
NAME="/retrolume-task-083-d3-20260925-195448"
DB="retrolume_task083_d3"
USER="task083_d3"
PORT=55439


def docker(args, deadlines, *, input_text=None, reserve=60, limit=30):
    timeout=min(float(limit),deadline_left(*deadlines,reserve=reserve))
    return subprocess.run(["docker",*args],input=input_text,capture_output=True,text=True,timeout=timeout,check=False)


def inspect(deadlines, *, reserve=60, limit=30):
    # A formatted projection keeps Config.Env (and the old password) out of the CLI output.
    fields=("{{.Id}}","{{.Name}}","{{.Image}}","{{json .Config.Labels}}",
            "{{.State.Running}}","{{json .Mounts}}","{{.HostConfig.NanoCpus}}",
            "{{.HostConfig.Memory}}","{{.HostConfig.PidsLimit}}",
            "{{.HostConfig.RestartPolicy.Name}}","{{.HostConfig.NetworkMode}}",
            "{{json .HostConfig.PortBindings}}","{{json .HostConfig.Binds}}",
            "{{json .HostConfig.Mounts}}")
    result=docker(["inspect","--format","|".join(fields),CID],deadlines,reserve=reserve,limit=limit)
    if result.returncode!=0: raise RuntimeError(f"inspect exit={result.returncode}")
    pieces=result.stdout.strip().split("|")
    if len(pieces)!=len(fields): raise RuntimeError("selected inspect cardinality unknown")
    return {"id":pieces[0],"name":pieces[1],"image":pieces[2],
            "labels":json.loads(pieces[3]),"running":pieces[4]=="true",
            "mounts":json.loads(pieces[5]),"nano_cpus":int(pieces[6]),"memory":int(pieces[7]),
            "pids":int(pieces[8]),"restart":pieces[9],"network":pieces[10],
            "port_bindings":json.loads(pieces[11]),"binds":json.loads(pieces[12]),
            "configured_mounts":json.loads(pieces[13])}

def valid_identity(value):
    labels=value["labels"] or {}; mounts=value["mounts"] or []
    bindings=(value["port_bindings"] or {}).get("5432/tcp") or []
    return (value["id"]==CID and value["name"]==NAME and value["image"]==IMAGE
            and labels.get("retrolume-task")=="083" and labels.get("phase")=="d3-10"
            and labels.get("run")=="20260925-195448"
            and len(mounts)==1 and mounts[0].get("Type")=="volume" and mounts[0].get("Name")==VOLUME
            and mounts[0].get("Destination")=="/var/lib/postgresql/data"
            and value["nano_cpus"]==1_000_000_000 and value["memory"]==536_870_912
            and value["pids"]==128 and value["restart"]=="no" and value["network"]=="bridge"
            and value["binds"] is None and value["configured_mounts"] in (None,[])
            and bindings==[{"HostIp":"127.0.0.1","HostPort":str(PORT)}])


def local_auth_and_rotate(deadlines):
    base=["exec","-i","--user","postgres",CID,"psql","-X","-qAt",
          "-v","ON_ERROR_STOP=1","-U",USER,"-d",DB]
    identity=docker(base,deadlines,input_text="SELECT current_user,current_database();\n")
    if identity.returncode!=0 or identity.stdout.strip()!=f"{USER}|{DB}":
        raise RuntimeError("local test-role auth or identity unavailable")
    password=secrets.token_hex(32)
    result=docker(base,deadlines,input_text=f"ALTER ROLE {USER} PASSWORD '{password}';\n")
    if result.returncode!=0: raise RuntimeError("local test-role password rotation failed")
    dsn=f"postgresql://{USER}:{password}@127.0.0.1:{PORT}/{DB}"
    timeout=min(3,int(deadline_left(*deadlines,reserve=60)))
    if timeout<1: raise TimeoutError("loopback auth deadline")
    try:
        with psycopg.connect(dsn,connect_timeout=timeout) as conn:
            row=conn.execute("SELECT current_user,current_database(),inet_server_port()").fetchone()
    except BaseException:
        raise RuntimeError("loopback new-credential authentication failed") from None
    if row!=(USER,DB,5432): raise RuntimeError("loopback new-credential identity mismatch")
    return dsn,password,{"database":row[1],"user":row[0],"internal_port":row[2]}

def run_batch(parts,number,dsn,password,run_dir,deadlines):
    attempt=run_dir/f"attempt-{number:02d}"
    attempt.mkdir(exist_ok=False)
    script=FIXTURE.read_bytes()
    (attempt/"as-run.py").write_bytes(script)
    (attempt/"as-run.sha256").write_text(hashlib.sha256(script).hexdigest()+"  d3_pg_windows.py\n",encoding="utf-8")
    started=time.monotonic()
    batch_deadline=min(*deadlines,started+600)
    command_deadline=min(batch_deadline-60,started+60)
    deadline_left(command_deadline,reserve=5)
    env=os.environ.copy()
    env.pop("RETROLUME_TASK_083_DATABASE_URL",None)
    env["RETROLUME_TASK_083_D3_DATABASE_URL"]=dsn
    env["D3_PARTS"]=",".join(parts)
    env["PYTHONOPTIMIZE"]="0"
    env["PYTHONDONTWRITEBYTECODE"]="1"
    child=ControlledChild()
    streams={"stdout":[],"stderr":[]}
    active_scene=None; scene_deadline=None; timed_out=False; windows_started=False
    error=None; cleanup_error=None; identity=None; exit_code=None
    try:
        identity=child.start([str(PY),"-B",str(FIXTURE)],cwd=ROOT/"backend/tests",
                             env=env,deadline=command_deadline-5)
        while True:
            limit=min(command_deadline-5,scene_deadline or command_deadline)
            if time.monotonic()>=limit:
                timed_out=True
                raise TimeoutError("command or 30-second scenario deadline")
            try:
                label,line=child.lines.get(timeout=min(.05,deadline_left(limit)))
                if line is not None:
                    streams[label].append(line)
                    if label=="stdout":
                        try: event=json.loads(line)
                        except json.JSONDecodeError: event=None
                        if isinstance(event,dict):
                            phase=event.get("phase")
                            if phase=="scenario_start":
                                if active_scene is not None: raise RuntimeError("overlapping scenarios")
                                active_scene=event.get("scenario")
                                if active_scene=="windows_recovery": windows_started=True
                                scene_deadline=time.monotonic()+30
                            elif phase==active_scene:
                                active_scene=None; scene_deadline=None
            except queue.Empty: pass
            exit_code=child.exit_code()
            if exit_code is not None and child.active()==0:
                child.cleanup_confirmed=True
                break
        for reader in child.readers:
            reader.join(timeout=deadline_left(command_deadline,reserve=1))
            if reader.is_alive(): raise OwnershipUnknown("output pipe did not reach EOF")
    except BaseException as exc:
        error=f"{type(exc).__name__}: {exc}"
        try:
            if not child.cleanup_confirmed: child.stop(command_deadline)
        except BaseException as cleanup_exc:
            cleanup_error=f"{type(cleanup_exc).__name__}: {cleanup_exc}"
    finally:
        try: child.close()
        except BaseException as cleanup_exc:
            cleanup_error=f"{type(cleanup_exc).__name__}: {cleanup_exc}"
    while not child.lines.empty():
        label,line=child.lines.get_nowait()
        if line is not None: streams[label].append(line)
    raw_out,raw_err="".join(streams["stdout"]),"".join(streams["stderr"])
    leaked=password in raw_out or password in raw_err
    (attempt/"stdout.log").write_text(raw_out.replace(password,"[REDACTED]"),encoding="utf-8")
    (attempt/"stderr.log").write_text(raw_err.replace(password,"[REDACTED]"),encoding="utf-8")
    contract=validate_records(raw_out,parts,exit_code if exit_code is not None else -1,
                              cleanup_confirmed=child.cleanup_confirmed and cleanup_error is None,
                              timed_out=timed_out)
    if leaked:
        contract["pass"]=False
        contract["errors"].append("credential appeared in child output and was redacted")
    if error or cleanup_error: contract["pass"]=False
    meta={"parts":list(parts),"identity":identity,"exit_code":exit_code,
          "seconds":time.monotonic()-started,"timeout":timed_out,"windows_started":windows_started,
          "error":error,"cleanup_error":cleanup_error,
          "outer_tree_zero":child.cleanup_confirmed,"contract":contract}
    (attempt/"meta.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
    return meta


def retry_allowed(meta):
    return (not meta["contract"]["pass"] and meta["outer_tree_zero"]
            and meta["cleanup_error"] is None and not meta["windows_started"])


def stop_exact_container(deadlines,state):
    try:
        cleanup_deadline=min(*deadlines,time.monotonic()+60)
        before=inspect((cleanup_deadline,),reserve=0,limit=10)
        if not valid_identity(before): raise RuntimeError("stop refused: exact identity/config mismatch")
        state["stop_pre_identity"]=before
        if before["running"]:
            result=docker(["stop","--timeout","10",CID],(cleanup_deadline,),reserve=0,limit=20)
            state["stop_exit"]=result.returncode
            if result.returncode!=0:
                result=docker(["kill",CID],(cleanup_deadline,),reserve=0,limit=10)
                state["kill_exit"]=result.returncode
        after=inspect((cleanup_deadline,),reserve=0,limit=10)
        state["stop_post_identity"]=after
        if not valid_identity(after) or after["running"]:
            raise RuntimeError("container stop not confirmed")
        state["container_stopped"]=True
    except BaseException as exc:
        state["cleanup_incomplete"]=True
        state["cleanup_error"]=f"{type(exc).__name__}: {exc}"

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--authorized-reuse",action="store_true",help="future separate resource approval required")
    parser.add_argument("--total-seconds",type=int,default=900)
    args=parser.parse_args()
    if not args.authorized_reuse or not 120<=args.total_seconds<=1200:
        raise SystemExit("separate reuse authorization and bounded remaining total required")
    run_dir=EVID/("continuation-"+datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")+"-"+uuid4().hex[:8])
    run_dir.mkdir(exist_ok=False)
    for source in (Path(__file__),EVID/"controlled_child.py",EVID/"contracts.py"):
        data=source.read_bytes()
        (run_dir/(source.stem+"-as-run.py")).write_bytes(data)
        (run_dir/(source.stem+".sha256")).write_text(hashlib.sha256(data).hexdigest()+"\n",encoding="utf-8")
    total_deadline=time.monotonic()+args.total_seconds
    state={"resource_id":CID,"attempts":[],"cleanup_incomplete":False,
           "container_stopped":False,"verdict":"NOT_RUN"}
    password=None; touched=False
    try:
        before=inspect((total_deadline,))
        if not valid_identity(before) or before["running"]:
            raise RuntimeError("stopped exact reuse resource not confirmed")
        state["pre_identity"]=before
        with socket.socket() as sock: sock.bind(("127.0.0.1",PORT))
        others=docker(["ps","--filter","label=retrolume-task=083","--format","{{.ID}}"],(total_deadline,))
        if others.returncode!=0 or others.stdout.strip():
            raise RuntimeError("other active task resource or task ownership unavailable")
        touched=True
        started=docker(["start",CID],(total_deadline,))
        if started.returncode!=0: raise RuntimeError("exact container start failed")
        after=inspect((total_deadline,))
        if not valid_identity(after) or not after["running"]:
            raise RuntimeError("started resource identity mismatch")
        dsn,password,state["new_pg_identity"]=local_auth_and_rotate((total_deadline,))
        for number in (1,2):  # original attempt 1 consumed; two remaining maximum
            parts=parse_parts("migration,ledger,windows") if number==1 else None
            if number==2:
                go=run_dir/"attempt-02.go"
                while not go.exists():
                    time.sleep(min(.2,deadline_left(total_deadline,reserve=120)))
                parts=parse_parts(go.read_text(encoding="utf-8").strip())
            meta=run_batch(parts,number,dsn,password,run_dir,(total_deadline,))
            state["attempts"].append(meta)
            (run_dir/"state.json").write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
            if meta["contract"]["pass"]:
                state["verdict"]="PASS"; break
            if not retry_allowed(meta):
                state["verdict"]="FAILED_STOP"; break
            state["verdict"]="FAILED_WAITING_CORRECTION"
    except BaseException as exc:
        if not state["attempts"]: state["verdict"]="BLOCKED"
        message=f"{type(exc).__name__}: {exc}"
        state["error"]=message.replace(password,"[REDACTED]") if password else message
    finally:
        if touched: stop_exact_container((total_deadline,),state)
        (run_dir/"state.json").write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
    return 0 if state["verdict"]=="PASS" and state["container_stopped"] and not state["cleanup_incomplete"] else 1


if __name__=="__main__":
    sys.exit(main())