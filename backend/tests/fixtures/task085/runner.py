"""TASK085单批控制者；专用容器/独立外层Job/总期限/精确收尾。"""
from pathlib import Path
import json
import os
import queue
import secrets
import socket
import subprocess
import sys
import time
from datetime import datetime,timezone

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
BACKEND=ROOT/"backend"
sys.path.insert(0,str(BACKEND))
from controlled_child import ControlledChild
from run_offline import hashes
from app.worker.supervisor_ipc import NamedMapping
from psycopg.conninfo import make_conninfo

IMAGE="sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f"
EVID=ROOT/"Ndocu/evidence/task-085"

def write(path,data): path.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding="utf-8")

def main():
    start=time.monotonic();deadline=start+480
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")+"-"+secrets.token_hex(3)
    folder=EVID/stamp;folder.mkdir()
    state={"start_utc":datetime.now(timezone.utc).isoformat(),"attempt":1,"image":IMAGE,
           "name":"retrolume-task-085-onecall-"+stamp.lower(),"volume":"retrolume-task-085-"+stamp.lower(),
           "port":"127.0.0.1:55440","cpu":1,"memory":536870912,"pids":128,"restart":"no",
           "commands":[],"cleanup_incomplete":False,"cid":None}
    write(folder/"manifest.json",state)
    before=hashes();write(folder/"as-run-hashes.json",before)
    child=None;mapping=None;exit_code=1;container_stopped=False
    password=secrets.token_urlsafe(36)
    role="task085_"+secrets.token_hex(4)
    env=os.environ.copy();env["POSTGRES_PASSWORD"]=password
    def docker(args,*,timeout=20,required=True):
        began=time.monotonic()
        result=subprocess.run(["docker",*args],env=env,capture_output=True,timeout=min(timeout,max(.1,deadline-time.monotonic())))
        state["commands"].append({"args":args,"exit":result.returncode,"seconds":time.monotonic()-began})
        write(folder/"manifest.json",state)
        # 不保存原始Docker错误，避免环境变量/连接串意外回显。
        if required and result.returncode: raise RuntimeError("docker command failed: "+args[0])
        return result.stdout.decode().strip(),result.returncode
    try:
        found,_=docker(["image","inspect",IMAGE,"--format","{{.Id}}"])
        if found!=IMAGE: raise RuntimeError("required local image absent")
        with socket.socket() as check:
            check.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1)
            check.bind(("127.0.0.1",55440))
        cid,_=docker(["create","--name",state["name"],"--cpus","1","--memory","512m","--pids-limit","128",
            "--restart","no","--security-opt","no-new-privileges","--publish","127.0.0.1:55440:5432",
            "--mount","type=volume,source="+state["volume"]+",target=/var/lib/postgresql/data",
            "--env","POSTGRES_PASSWORD","--env","POSTGRES_USER="+role,
            "--env","POSTGRES_DB=retrolume_task085_onecall",IMAGE])
        if len(cid)!=64 or any(c not in "0123456789abcdef" for c in cid): raise RuntimeError("unknown created container")
        state["cid"]=cid;write(folder/"manifest.json",state)
        inspect,_=docker(["inspect",cid,"--format",'{{json .Id}}|{{json .Image}}|{{json .HostConfig.NanoCpus}}|{{json .HostConfig.Memory}}|{{json .HostConfig.PidsLimit}}|{{json .HostConfig.Privileged}}|{{json .HostConfig.RestartPolicy.Name}}|{{json .HostConfig.PortBindings}}|{{json .Mounts}}'])
        values=[json.loads(x) for x in inspect.split("|")]
        if values[:7]!=[cid,IMAGE,1000000000,536870912,128,False,"no"]: raise RuntimeError("resource limits mismatch")
        if values[7]!={"5432/tcp":[{"HostIp":"127.0.0.1","HostPort":"55440"}]}: raise RuntimeError("port mismatch")
        if len(values[8])!=1 or values[8][0]["Type"]!="volume" or values[8][0]["Name"]!=state["volume"]: raise RuntimeError("volume mismatch")
        state["inspect"]=values;write(folder/"manifest.json",state)
        docker(["start",cid])
        ready_deadline=time.monotonic()+30
        while True:
            _,code=docker(["exec",cid,"pg_isready","-U",role,"-d","retrolume_task085_onecall"],required=False)
            if code==0:break
            if time.monotonic()>ready_deadline:raise TimeoutError("database readiness")
            time.sleep(.3)
        dsn=make_conninfo(host="127.0.0.1",port=55440,dbname="retrolume_task085_onecall",user=role,password=password,
                         connect_timeout=2,options="-c statement_timeout=3000 -c lock_timeout=1000")
        mapping=NamedMapping.create("Local\\RetroLume.SUP."+secrets.token_hex(16))
        mapping.write_request({"dsn":dsn,"role":role})
        child=ControlledChild()
        child_env=os.environ.copy();child_env["PYTHONDONTWRITEBYTECODE"]="1"
        # 环境中不加入DSN/key，合成凭据仅经内存映射交被测进程。
        state["process"]=child.start([sys.executable,"-B",str(HERE/"real_cases.py"),mapping.name],
            cwd=BACKEND,env=child_env,deadline=deadline-120)
        write(folder/"manifest.json",state)
        exit_code=child.wait_empty(deadline-120)
        state["batch_exit"]=exit_code
        state["outer_tree_zero"]=child.active()==0
    except BaseException as exc:
        state["error_type"]=type(exc).__name__
        # 仅本控制者自定义稳定错误标签。
        if type(exc) in (RuntimeError,TimeoutError): state["error"]=str(exc).replace(password,"[redacted]")
    finally:
        if child is not None:
            try:
                child.stop(deadline-30)
                state["outer_tree_zero"]=child.active()==0
                child.close()
                state["outer_handles_closed"]=True
            except BaseException as exc:
                state["cleanup_incomplete"]=True;state["child_cleanup_error"]=type(exc).__name__
            for thread in child.readers: thread.join(timeout=1)
            logs={"stdout":[],"stderr":[]}
            while True:
                try: label,line=child.lines.get_nowait()
                except queue.Empty:break
                if line is not None: logs[label].append(line.replace(password,"[redacted]"))
            for label,lines in logs.items(): (folder/f"{label}.log").write_text("".join(lines),encoding="utf-8")
            state["process_events"]=child.events
        if mapping is not None:
            try:mapping.close();state["mapping_closed"]=True
            except BaseException as exc:state["cleanup_incomplete"]=True;state["mapping_error"]=type(exc).__name__
        if state["cid"]:
            try:
                docker(["stop","--time","10",state["cid"]],timeout=20)
                running,_=docker(["inspect",state["cid"],"--format","{{.State.Running}}"])
                container_stopped=running=="false"
                if not container_stopped:state["cleanup_incomplete"]=True
            except BaseException as exc:state["cleanup_incomplete"]=True;state["container_cleanup_error"]=type(exc).__name__
        state["container_stopped"]=container_stopped
        state["seconds"]=time.monotonic()-start
        state["end_utc"]=datetime.now(timezone.utc).isoformat()
        after=hashes();write(folder/"post-hashes.json",after)
        state["source_unchanged"]=before==after
        write(folder/"manifest.json",state)
        print(json.dumps({k:state.get(k) for k in ("batch_exit","error_type","error","seconds","cleanup_incomplete","container_stopped","source_unchanged")}))
        print(str(folder))
    return 0 if exit_code==0 and container_stopped and not state["cleanup_incomplete"] and before==after else 1

if __name__=="__main__": raise SystemExit(main())
