"""固定Docker参数数组、精确归属与privatePID/init组合停止证明。"""
from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess
import time
import hashlib
import secrets
from uuid import uuid4
from .host_job import HostJob,JobChild,current_job,job_name
from .description import canonical

SAFE_ENV=("SystemRoot","WINDIR","PATH","TEMP","TMP","LOCALAPPDATA","USERPROFILE","PROGRAMFILES","PROGRAMFILES(X86)")
INSPECT='{ "id":{{json .Id}},"image":{{json .Image}},"labels":{{json .Config.Labels}},"user":{{json .Config.User}},"state":{{json .State}},"host":{{json .HostConfig}},"mounts":{{json .Mounts}},"ports":{{json .NetworkSettings.Ports}} }'


class DockerUnknown(RuntimeError):pass


def clean_env():return {key:os.environ[key] for key in SAFE_ENV if key in os.environ}


def call(docker,args,timeout=2):
    started=time.monotonic_ns()
    job=current_job();owned=job is None;child=None
    if owned:job=HostJob(job_name(str(uuid4()),secrets.token_hex(32),"CALL"))
    try:
        child=JobChild([docker,*args],job,env=clean_env())
        stdout,stderr=child.communicate(timeout=timeout);code=child.poll()
        # 这些固定调用不接密码/DSN或Config.Env；输出仍有硬上界。
        if len(stdout)>65536 or len(stderr)>8192:raise DockerUnknown("docker_output_limit")
        proof=job.finish() if owned else {"name":job.name,"primary_exit":code,"primary_pid":child.pid,"birth":child.birth["birth"]}
        return {"args":args,"code":code,"stdout":stdout.decode("utf-8","replace"),
                "stderr":stderr.decode("utf-8","replace"),"start_ns":started,"end_ns":time.monotonic_ns(),"windows_job":proof}
    except (OSError,subprocess.TimeoutExpired):raise DockerUnknown("docker_control_unavailable") from None
    finally:
        if child:
            if child.poll() is None:child.terminate();child.wait(2)
            child.close()
        if owned:job.close()


def inspect_owned(docker,cid,intent):
    if len(cid)!=64 or any(ch not in "0123456789abcdef" for ch in cid):raise DockerUnknown("cid_unconfirmed")
    response=call(docker,["inspect","--format",INSPECT,cid])
    if response["code"]:raise DockerUnknown("inspect_unavailable")
    value=json.loads(response["stdout"]);labels=value["labels"] or {}
    if value["id"]!=cid or value["image"]!=intent["image_id"] or any(labels.get(key)!=expected for key,expected in intent["labels"].items()):
        raise DockerUnknown("ownership_mismatch")
    host=value["host"]
    if (host["Privileged"] or host["ReadonlyRootfs"] is not True or host["NetworkMode"]!="none" or host["Init"] is not True
        or host["PidMode"]!="" or host["IpcMode"]!="private" or host["RestartPolicy"]["Name"]!="no"
        or host["Binds"] or host["PortBindings"] or value["ports"] or value["user"]!="10001:10001"
        or host["CapAdd"] or host["CapDrop"]!=["ALL"] or host["PidsLimit"]!=256
        or host["Memory"]!=1073741824 or host["MemorySwap"]!=1073741824 or host["NanoCpus"]!=1000000000
        or host["ShmSize"]!=67108864 or not any(str(x).startswith("no-new-privileges") for x in host["SecurityOpt"])):
        raise DockerUnknown("container_boundary_mismatch")
    if any(m["Type"]!="tmpfs" for m in value["mounts"]):raise DockerUnknown("mount_boundary_mismatch")
    seccomp=[option[len("seccomp="):] for option in host["SecurityOpt"] if option.startswith("seccomp=")]
    if len(seccomp)!=1 or hashlib.sha256(canonical(json.loads(seccomp[0])).encode("utf-8")).hexdigest()!=intent["seccomp_sha256"]:
        raise DockerUnknown("seccomp_identity_mismatch")
    value["host"]={key:host[key] for key in ("Privileged","ReadonlyRootfs","NetworkMode","Init","PidMode","IpcMode","RestartPolicy","PidsLimit","Memory","MemorySwap","NanoCpus","ShmSize","CapAdd","CapDrop","Tmpfs")}
    value["host"]["SecurityOpt"]={"no_new_privileges":True,"seccomp_sha256":intent["seccomp_sha256"]}
    return value


def find_intent(docker,intent):
    result=call(docker,["ps","-a","--no-trunc","--filter","name=^/"+intent["name"]+"$","--filter","label=retrolume.nonce="+intent["nonce"],"--format","{{.ID}}"])
    if result["code"]:raise DockerUnknown("intent_lookup_unavailable")
    ids=result["stdout"].split()
    if len(ids)>1:raise DockerUnknown("intent_multiple_objects")
    if not ids:return None
    inspect_owned(docker,ids[0],intent);return ids[0]


def creation_args(intent,seccomp):
    # 不传--pid即独立namespace；Docker的--pid仅支持host或container，private不是合法值。
    args=["create","--name",intent["name"],"--user","10001:10001","--network","none","--read-only","--cap-drop","ALL",
      "--security-opt","no-new-privileges","--security-opt","seccomp="+str(seccomp),"--ipc","private","--init",
      "--restart","no","--cpus","1","--memory","1024m","--memory-swap","1024m","--pids-limit","256","--shm-size","64m",
      "--tmpfs","/tmp:rw,size=128m,uid=10001,gid=10001,mode=0700,nosuid,nodev,noexec",
      "--tmpfs","/home/preview:rw,size=32m,uid=10001,gid=10001,mode=0700,nosuid,nodev,noexec","-i"]
    for key,value in sorted(intent["labels"].items()):args.extend(["--label",key+"="+value])
    args.append(intent["image_id"]);return args


def local_create_rejection(result,intent,seccomp):
    """只识别已保存的CLI参数解析失败。普通非零、无CID或空lookup仍是未知。"""
    expected=creation_args(intent,seccomp)
    index=expected.index("--ipc");expected[index:index]=["--pid","private"]
    return (type(result) is dict and result.get("args")==expected and result.get("code")==125
        and result.get("stdout")=="" and result.get("stderr","").replace("\r\n","\n")==
        "docker: --pid: invalid PID mode\n\nRun 'docker create --help' for more information\n"
        and type(result.get("start_ns")) is int and type(result.get("end_ns")) is int
        and 0<result["start_ns"]<=result["end_ns"])


def namespace_premises(ready,intent):
    facts=ready.get("processes",{});rows=facts.get("rows",[])
    init=next((r for r in rows if r.get("pid")==1),None)
    own=next((r for r in rows if r.get("pid")==facts.get("own_pid")),None)
    errors=facts.get("errors",[])
    if (facts.get("kernel")!=intent["kernel_release"] or facts.get("own_uid")!=10001 or facts.get("own_gid")!=10001
        or not isinstance(facts.get("own_namespace"),str) or not facts["own_namespace"].startswith("pid:[") or not facts["own_namespace"].endswith("]")
        or not facts["own_namespace"][5:-1].isdigit() or facts.get("own_namespace")!=facts.get("init_namespace") or not init or not own
        or init.get("NSpid")!="1" or not init.get("birth_ticks") or own.get("NoNewPrivs")!="1"
        or own.get("CapEff")!="0000000000000000" or any(e.get("code")!="ENOENT" for e in errors)):
        return False
    # 消失的/proc项保留errno；不把未读取的任务计作0。内核init证明对整个本namespace及子树适用。
    return (init.get("pid_namespace")==facts["init_namespace"] and own.get("pid_namespace")==facts["own_namespace"]
        and all(row.get("NSpid") and row["NSpid"].split()[0]==str(row["pid"]) and row.get("birth_ticks") and row.get("pid_namespace") for row in rows))


def stop_owned(docker,cid,intent,ready,*,attach_ended=False,diagnostic_deadline_ns=None):
    receipt={"cid":cid,"image_id":intent["image_id"],"nonce":intent["nonce"],"tree_confirmation":"unconfirmed",
             "mechanism":"private_pid_namespace_init_end","start_ns":time.monotonic_ns()}
    if ready is not None:
        receipt["kernel_premises_sha256"]=hashlib.sha256(canonical(ready).encode("utf-8")).hexdigest()
        receipt["kernel_release"]=ready.get("processes",{}).get("kernel")
    try:
        before=inspect_owned(docker,cid,intent);receipt["before"]=before
        if before["state"]["Running"]:receipt["kill"]=call(docker,["kill",cid])
        wait=call(docker,["wait",cid],timeout=2);receipt["wait"]=wait
        after=inspect_owned(docker,cid,intent);receipt["after"]=after
        if wait["code"] or after["state"]["Running"] or after["state"]["Pid"]!=0 or after["state"]["Restarting"]:
            raise DockerUnknown("termination_unconfirmed")
        until=int(time.time())+1
        events=call(docker,["events","--since",intent["created_unix"],"--until",str(until),"--filter","container="+cid,
                           "--filter","event=die","--format","{{json .}}"],timeout=2)
        receipt["events"]=events
        rows=[json.loads(line) for line in events["stdout"].splitlines() if line.strip()]
        dies=[event for event in rows if event.get("Actor",{}).get("ID")==cid and event.get("Action")=="die"]
        if not dies:raise DockerUnknown("init_exit_event_missing")
        if ready is not None and namespace_premises(ready,intent) and attach_ended:
            receipt["tree_confirmation"]="private_pid_init_terminated"
        receipt["attach_eof_confirmed"]=attach_ended;receipt["end_ns"]=time.monotonic_ns()
        receipt["claims"]="自有工作任务树，非cgroup目录删除或内存完全释放"
    except (DockerUnknown,ValueError,KeyError):receipt["error_code"]="cleanup_unconfirmed";receipt["end_ns"]=time.monotonic_ns()
    if diagnostic_deadline_ns is not None and receipt["end_ns"]>diagnostic_deadline_ns:
        receipt["tree_confirmation"]="unconfirmed";receipt["error_code"]="stop_diagnostic_deadline"
    return receipt
