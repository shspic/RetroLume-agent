"""TASK-083 D3-10 one-container bounded runner; password remains in this process only."""
from __future__ import annotations
import ctypes
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import time
from ctypes import wintypes

import psycopg

ROOT=Path(r"D:/shspic/project_NO3_RetroLume-agent")
EVID=ROOT/"Ndocu/evidence/task-083/d3-implementation-10"
PY=ROOT/"backend/.venv/Scripts/python.exe"
TEST=ROOT/"backend/tests/fixtures/task083/d3_pg_windows.py"
IMAGE="sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f"
TAG=datetime.now().strftime("%Y%m%d-%H%M%S")
NAME=f"retrolume-task-083-d3-{TAG}"
RUN_EVID=EVID/f"replacement-{TAG}"
RUN_EVID.mkdir(exist_ok=False)
DB="retrolume_task083_d3"
USER="task083_d3"
PORT=55439
T0=time.monotonic()
DEADLINE=T0+1680  # replacement remaining resource+real-run budget: 28 minutes
password=None
cid=None
run_attempted=False
state={"tag":TAG,"name":NAME,"attempts":[],"container_id":None,"cleanup_incomplete":False}
active_proc=None
active_created=None
runner_bytes=Path(__file__).read_bytes()
(RUN_EVID/"runner-as-run.py").write_bytes(runner_bytes)
(RUN_EVID/"runner-as-run.sha256").write_text(hashlib.sha256(runner_bytes).hexdigest()+"  runner_replacement.py\n",encoding="utf-8")

def left():
    return DEADLINE-time.monotonic()

def log(msg):
    line=f"[{time.monotonic()-T0:.3f}s] {msg}"
    print(line,flush=True)
    with (RUN_EVID/"runner-log.txt").open("a",encoding="utf-8") as f: f.write(line+"\n")

def save():
    (RUN_EVID/"runner-state.json").write_text(json.dumps(state,indent=2,ensure_ascii=False,default=str),encoding="utf-8")

def docker(args, timeout=30, *, cleanup=False):
    reserve=0 if cleanup else 60
    r=subprocess.run(["docker",*args],capture_output=True,text=True,
                     timeout=min(timeout,max(1,left()-reserve)))
    return r

def select_inspect(container, *, cleanup=False):
    r=docker(["inspect",container],30,cleanup=cleanup)
    if r.returncode!=0: raise RuntimeError(f"inspect exit={r.returncode}")
    obj=json.loads(r.stdout)[0]
    hc=obj["HostConfig"]
    selected={
        "id":obj["Id"],"name":obj["Name"],"image":obj["Image"],
        "labels":obj["Config"]["Labels"],"running":obj["State"]["Running"],
        "nano_cpus":hc["NanoCpus"],"memory":hc["Memory"],"pids_limit":hc["PidsLimit"],
        "restart":hc["RestartPolicy"]["Name"],"network":hc["NetworkMode"],
        "port_bindings":hc["PortBindings"],"binds":hc["Binds"],
        "configured_mounts":hc.get("Mounts"),"mounts":obj["Mounts"],
    }
    return selected

def identity_ok(obj):
    labels=obj["labels"] or {}
    return (obj["id"]==cid and obj["name"]=="/"+NAME and obj["image"]==IMAGE
            and labels.get("retrolume-task")=="083"
            and labels.get("phase")=="d3-10" and labels.get("run")==TAG)

def config_ok(obj):
    binding=(obj["port_bindings"] or {}).get("5432/tcp") or []
    mounts=obj["mounts"] or []
    return (obj["nano_cpus"]==1000000000 and obj["memory"]==536870912
            and obj["pids_limit"]==128 and obj["restart"]=="no"
            and obj["network"]=="bridge" and obj["binds"] is None
            and obj["configured_mounts"] in (None,[])
            and len(mounts)==1 and mounts[0]["Type"]=="volume"
            and mounts[0]["Destination"]=="/var/lib/postgresql/data"
            and binding==[{"HostIp":"127.0.0.1","HostPort":str(PORT)}])

def process_created(handle):
    class FileTime(ctypes.Structure):
        _fields_=[("low",wintypes.DWORD),("high",wintypes.DWORD)]
    api=ctypes.WinDLL("kernel32",use_last_error=True)
    api.GetProcessTimes.argtypes=[wintypes.HANDLE,*([ctypes.POINTER(FileTime)]*4)]
    api.GetProcessTimes.restype=wintypes.BOOL
    values=[FileTime() for _ in range(4)]
    if not api.GetProcessTimes(handle,*(ctypes.byref(x) for x in values)):
        raise RuntimeError(f"GetProcessTimes error={ctypes.get_last_error()}")
    return (int(values[0].high)<<32)|int(values[0].low)

def batch(parts,number,dsn):
    global active_proc,active_created
    attempt=RUN_EVID/f"attempt-{number:02d}"
    attempt.mkdir(exist_ok=False)
    script_bytes=TEST.read_bytes()
    import hashlib
    (attempt/"as-run.sha256").write_text(hashlib.sha256(script_bytes).hexdigest()+"  backend/tests/fixtures/task083/d3_pg_windows.py\n",encoding="utf-8")
    (attempt/"as-run.py").write_bytes(script_bytes)
    env=os.environ.copy()
    env.pop("RETROLUME_TASK_083_DATABASE_URL",None)
    env["RETROLUME_TASK_083_D3_DATABASE_URL"]=dsn
    env["D3_PARTS"]=parts
    cmd=[str(PY),"-B",str(TEST)]
    log(f"batch {number} start parts={parts} timeout=60s")
    started=time.monotonic()
    proc=subprocess.Popen(cmd,cwd=str(ROOT/"backend/tests"),env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    active_proc=proc
    created=process_created(proc._handle)
    active_created=created
    killed=False
    try:
        out,err=proc.communicate(timeout=min(60,max(1,left()-65)))
    except subprocess.TimeoutExpired:
        killed=True
        if process_created(proc._handle)!=created:
            state["cleanup_incomplete"]=True
            raise RuntimeError("batch PID creation time changed; ownership unknown")
        tk=subprocess.run(["taskkill","/PID",str(proc.pid),"/T","/F"],capture_output=True,text=True,timeout=15)
        (attempt/"timeout-kill.json").write_text(json.dumps({"pid":proc.pid,"created_100ns":created,"exit":tk.returncode,
            "stdout":tk.stdout,"stderr":tk.stderr},ensure_ascii=False),encoding="utf-8")
        out,err=proc.communicate(timeout=10)
    text_out=out.decode("utf-8",errors="replace").replace(password,"***")
    text_err=err.decode("utf-8",errors="replace").replace(password,"***")
    (attempt/"stdout.log").write_text(text_out,encoding="utf-8")
    (attempt/"stderr.log").write_text(text_err,encoding="utf-8")
    records=[]
    for line in text_out.splitlines():
        try:
            parsed=json.loads(line)
            if isinstance(parsed,dict): records.append(parsed)
        except json.JSONDecodeError: pass
    phases=[record.get("phase") for record in records]
    windows_started=any(record.get("label")=="windows" and record.get("phase")=="schema" for record in records)
    meta={"parts":parts,"pid":proc.pid,"created_100ns":created,"exit":proc.returncode,
          "elapsed_seconds":time.monotonic()-started,"timeout_killed":killed,
          "phases":phases,"windows_started":windows_started}
    (attempt/"meta.json").write_text(json.dumps(meta,indent=2),encoding="utf-8")
    state["attempts"].append(meta);save()
    active_proc=None
    active_created=None
    ok=proc.returncode==0 and not killed and "complete" in phases and text_err.strip()==""
    log(f"batch {number} exit={proc.returncode} elapsed={meta['elapsed_seconds']:.2f}s phases={phases} pass={ok}")
    # A failed Windows phase has no positive whole-tree cleanup proof; stop, never retry.
    return ok, (not killed and not windows_started)

try:
    log("precheck start: one attempt, no pull/start/port change")
    r=docker(["info","--format","{{.ServerVersion}}"],30)
    state["precheck_docker_info"]={"exit":r.returncode,"server":r.stdout.strip(),"error":r.stderr.strip()[:200]}
    if r.returncode!=0: raise RuntimeError("Docker engine unavailable")
    r=docker(["image","inspect",IMAGE,"--format","{{.Id}}"],30)
    state["precheck_image"]={"exit":r.returncode,"id":r.stdout.strip(),"error":r.stderr.strip()[:200]}
    if r.returncode!=0 or r.stdout.strip()!=IMAGE: raise RuntimeError("fixed local image unavailable")
    r=docker(["image","inspect",IMAGE,"--format","{{json .Config.Volumes}}"],30)
    image_volumes=json.loads(r.stdout) if r.returncode==0 else None
    state["precheck_image_volumes"]=image_volumes
    if image_volumes!={"/var/lib/postgresql/data":{}}:
        raise RuntimeError("image-declared anonymous PG volume differs")
    with socket.socket() as sock:
        sock.bind(("127.0.0.1",PORT))
    state["precheck_port"]="127.0.0.1:55439 free"
    save()
    log("precheck passed")
    password=secrets.token_urlsafe(24)
    dsn=f"postgresql://{USER}:{password}@127.0.0.1:{PORT}/{DB}"
    run_started=datetime.now(timezone.utc)
    run_attempted=True
    r=docker(["run","-d","--name",NAME,
              "--label","retrolume-task=083","--label","phase=d3-10","--label",f"run={TAG}",
              "--cpus","1","--memory","512m","--pids-limit","128","--restart","no","--network","bridge",
              "-p",f"127.0.0.1:{PORT}:5432","-e",f"POSTGRES_USER={USER}",
              "-e",f"POSTGRES_PASSWORD={password}","-e",f"POSTGRES_DB={DB}",IMAGE],30)
    if r.returncode!=0:
        state["create_error"]={"exit":r.returncode,"stderr":r.stderr.replace(password,"***")[:500]}
        raise RuntimeError("container create failed")
    cid=r.stdout.strip();state["container_id"]=cid;save();log(f"created id={cid}")
    obj=select_inspect(cid)
    (RUN_EVID/"container-created.json").write_text(json.dumps(obj,indent=2),encoding="utf-8")
    if not identity_ok(obj): raise RuntimeError("created container identity mismatch")
    if not config_ok(obj) or not obj["running"]:
        raise RuntimeError("created resource config mismatch")
    volume_name=obj["mounts"][0]["Name"]
    r=docker(["volume","inspect",volume_name],30)
    if r.returncode!=0: raise RuntimeError("anonymous volume inspect failed")
    volume=json.loads(r.stdout)[0]
    created_at=datetime.fromisoformat(volume["CreatedAt"].replace("Z","+00:00"))
    volume_ok=(volume["Name"]==volume_name and volume["Scope"]=="local"
               and volume["Mountpoint"]==obj["mounts"][0]["Source"]
               and run_started-timedelta(minutes=2)<=created_at<=datetime.now(timezone.utc)+timedelta(minutes=2))
    state["anonymous_volume"]={"name":volume_name,"created_at":str(created_at),
                               "new_this_run":volume_ok}
    save()
    if not volume_ok: raise RuntimeError("volume origin not confirmed new")
    ready_until=time.monotonic()+30
    while time.monotonic()<ready_until and left()>90:
        try:
            with psycopg.connect(dsn,connect_timeout=3) as conn:
                identity=conn.execute("SELECT current_database(),current_user,inet_server_port()").fetchone()
            if identity!=(DB,USER,5432): raise RuntimeError(f"PG identity mismatch {identity}")
            state["pg_identity"]={"database":identity[0],"user":identity[1],"internal_port":identity[2]}
            save();break
        except psycopg.OperationalError:
            time.sleep(1)
    else: raise RuntimeError("PG readiness timeout")
    log("PG ready and identity verified")
    for number in range(1,4):
        if left()<125: raise RuntimeError("budget reserve reached")
        parts="migration,ledger,windows" if number==1 else None
        if number>1:
            go=RUN_EVID/f"attempt-{number:02d}.go"
            until=min(time.monotonic()+240,DEADLINE-125)
            log(f"waiting for grounded correction signal {go.name}")
            while time.monotonic()<until and not go.exists(): time.sleep(.5)
            if not go.exists(): break
            parts=go.read_text(encoding="utf-8").strip()
            if parts not in ("migration","ledger","windows","migration,ledger","ledger,windows","migration,windows"):
                raise RuntimeError("invalid correction selection")
        passed,safe_retry=batch(parts,number,dsn)
        if passed:
            state["verdict"]="PASS";break
        if not safe_retry:
            state["verdict"]=f"ATTEMPT_{number}_FAILED_STOP"
            save()
            break
        state["verdict"]=f"ATTEMPT_{number}_FAILED";save()
    else:
        state["verdict"]="THREE_ATTEMPTS_FAILED"
    if state.get("verdict")!="PASS": log(f"verification stopped verdict={state.get('verdict')}")
except BaseException as exc:
    state["verdict"]=state.get("verdict") or "BLOCKED"
    state["error_type"]=type(exc).__name__
    state["error_message"]=str(exc).replace(password,"***") if password else str(exc)
    log(f"blocked {type(exc).__name__}: {state['error_message']}")
finally:
    if run_attempted and cid is None:
        # Docker may create the named container before reporting a run error.
        try:
            r=docker(["inspect",NAME],30,cleanup=True)
            if r.returncode==0:
                candidate=json.loads(r.stdout)[0]
                labels=candidate["Config"]["Labels"] or {}
                if (candidate["Name"]=="/"+NAME and candidate["Image"]==IMAGE
                    and labels.get("retrolume-task")=="083"
                    and labels.get("phase")=="d3-10" and labels.get("run")==TAG):
                    cid=candidate["Id"]
                    state["container_id"]=cid
                    log(f"partial run resource found id={cid}")
                else:
                    state["cleanup_incomplete"]=True
                    state["partial_run_owner"]="mismatch"
        except BaseException as exc:
            state["cleanup_incomplete"]=True
            state["partial_run_owner"]=f"{type(exc).__name__}: {exc}"
    if active_proc is not None and active_proc.poll() is None:
        try:
            if active_created is not None and process_created(active_proc._handle)==active_created:
                r=subprocess.run(["taskkill","/PID",str(active_proc.pid),"/T","/F"],
                                 capture_output=True,text=True,timeout=min(15,max(1,left()-30)))
                state["batch_final_kill"]={"pid":active_proc.pid,"created_100ns":active_created,
                                           "exit":r.returncode,"stdout":r.stdout,"stderr":r.stderr}
                active_proc.wait(timeout=min(10,max(1,left()-20)))
            else:
                # Exact Popen handle, but descendant ownership is unconfirmed.
                active_proc.kill()
                active_proc.wait(timeout=min(10,max(1,left()-20)))
                state["cleanup_incomplete"]=True
                state["batch_cleanup_error"]="creation time unavailable"
        except BaseException as exc:
            state["cleanup_incomplete"]=True
            state["batch_cleanup_error"]=f"{type(exc).__name__}: {exc}"
    if cid is not None:
        try:
            obj=select_inspect(cid,cleanup=True)
            if not identity_ok(obj): raise RuntimeError("cleanup owner mismatch")
            log(f"cleanup owner verified id={cid}")
            r=docker(["stop","--timeout","10",cid],20,cleanup=True)
            state["stop"]={"exit":r.returncode,"stderr":r.stderr[:200]}
            if r.returncode!=0:
                r=docker(["kill",cid],15,cleanup=True)
                state["kill"]={"exit":r.returncode,"stderr":r.stderr[:200]}
            final=select_inspect(cid,cleanup=True)
            (RUN_EVID/"container-final.json").write_text(json.dumps(final,indent=2),encoding="utf-8")
            if not identity_ok(final) or final["running"]:
                state["cleanup_incomplete"]=True
                log("cleanup_incomplete")
            else: log("container stopped and retained")
        except BaseException as exc:
            state["cleanup_incomplete"]=True
            state["cleanup_error"]=f"{type(exc).__name__}: {exc}"
            log("cleanup_incomplete")
    state["elapsed_seconds"]=time.monotonic()-T0
    save()
    log(f"final verdict={state.get('verdict')} elapsed={state['elapsed_seconds']:.2f}s cleanup_incomplete={state['cleanup_incomplete']}")
