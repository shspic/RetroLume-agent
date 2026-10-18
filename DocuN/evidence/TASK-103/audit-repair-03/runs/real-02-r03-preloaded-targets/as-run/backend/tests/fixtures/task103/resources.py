"""本卡专属Docker/端口身份，不读取旧实例或输出Env。"""
from __future__ import annotations
import json
import os
import re
import secrets
import socket
import subprocess
import time
from .control import Control,BudgetDenied,SECRET_VALUES,PERMIT

IMAGE="sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f"
SPECS={
 1:("retrolume-task-103-g9-pg1","retrolume-task-103-g9-pg1-data",55443,"retrolume_task103_g9_main"),
 2:("retrolume-task-103-g9-pg2","retrolume-task-103-g9-pg2-data",55444,"retrolume_task103_g9_upgrade"),
 3:("retrolume-task-103-g9-pg3","retrolume-task-103-g9-pg3-data",55445,"retrolume_task103_g9_fault")}


def owned_witness(data, expected):
    if type(data) is not dict or type(expected) is not dict:
        raise BudgetDenied("invalid ownership witness")
    labels=(data.get("Config") or {}).get("Labels") or {}
    if (data.get("Id")!=expected.get("cid") or data.get("Image")!=IMAGE
        or data.get("Name")!="/"+expected.get("name","")
        or labels.get("retrolume.task")!="TASK-103" or labels.get("retrolume.permit")!=PERMIT
        or labels.get("retrolume.synthetic")!="true"):
        raise BudgetDenied("unowned container")
    mounts=data.get("Mounts")
    if type(mounts) is not list or len(mounts)!=1:
        raise BudgetDenied("unexpected mounts")
    mount=mounts[0]
    if mount.get("Type")!="volume" or mount.get("Name")!=expected.get("volume") or mount.get("Destination")!="/var/lib/postgresql/data":
        raise BudgetDenied("unowned mount")
    config=data.get("HostConfig") or {}
    if config.get("Privileged") or config.get("NetworkMode")=="host" or config.get("Binds") not in (None,[],[expected["volume"]+":/var/lib/postgresql/data"]):
        raise BudgetDenied("unexpected privilege/bind")
    state=data.get("State") or {}
    if type(state.get("Running")) is not bool or type(state.get("Pid")) is not int:
        raise BudgetDenied("unknown state")
    return {"cid":data["Id"],"image":data["Image"],"name":expected["name"],"volume":expected["volume"],
            "running":state["Running"],"pid":state["Pid"],"exit_code":state.get("ExitCode")}


def port_available(port):
    if type(port) is not int or port not in (55443,55444,55445,18103,18104):
        raise BudgetDenied("unapproved port")
    with socket.socket() as sock:
        try:sock.bind(("127.0.0.1",port))
        except OSError:return False
    return True


class OwnedDocker:
    def __init__(self,control=None):
        self.control=control or Control()

    def cli(self,args,env=None,allowed=30,check=True):
        timeout=self.control.remaining("real",allowed)
        result=subprocess.run(["docker",*args],env=env,capture_output=True,timeout=timeout,
                              creationflags=subprocess.CREATE_NO_WINDOW)
        if check and result.returncode:
            raise RuntimeError("owned Docker operation failed: "+str(result.returncode))
        return result

    def record(self,value):
        with self.control.locked():
            data=self.control.load()
            if any(r.get("name")==value["name"] for r in data["resources"]):
                raise BudgetDenied("identity already registered")
            data["resources"].append(value)
            from .control import atomic_json
            atomic_json(self.control.path,data)

    def inspect(self,resource):
        result=self.cli(["container","inspect",resource["cid"]])
        data=json.loads(result.stdout)[0]
        return owned_witness(data,resource)

    def create(self,slot):
        if type(slot) is not int or slot not in SPECS:raise BudgetDenied("unknown resource slot")
        name,volume,port,database=SPECS[slot]
        if not port_available(port):raise BudgetDenied("approved port occupied")
        collision=self.cli(["container","inspect",name],check=False)
        if collision.returncode==0:raise BudgetDenied("container name occupied")
        collision=self.cli(["volume","inspect",volume],check=False)
        if collision.returncode==0:raise BudgetDenied("volume name occupied")
        image=json.loads(self.cli(["image","inspect",IMAGE]).stdout)[0]
        if image.get("Id")!=IMAGE:raise BudgetDenied("cached image mismatch")
        self.control.reserve("volume_create",{"name":volume})
        self.cli(["volume","create","--label","retrolume.task=TASK-103","--label","retrolume.permit="+PERMIT,
                  "--label","retrolume.synthetic=true",volume])
        secret=secrets.token_urlsafe(32);SECRET_VALUES.add(secret)
        env=os.environ.copy();env["POSTGRES_PASSWORD"]=secret
        self.control.reserve("container_create",{"name":name})
        cid=self.cli(["create","--pull=never","--name",name,"--label","retrolume.task=TASK-103",
           "--label","retrolume.permit="+PERMIT,"--label","retrolume.synthetic=true",
           "--cpus","1","--memory","512m","--pids-limit","128","--restart=no",
           "-p",f"127.0.0.1:{port}:5432","-v",volume+":/var/lib/postgresql/data",
           "-e","POSTGRES_PASSWORD","-e","POSTGRES_DB="+database,IMAGE],env=env).stdout.decode().strip()
        if not re.fullmatch("[0-9a-f]{64}",cid):raise BudgetDenied("invalid created CID")
        resource={"slot":slot,"name":name,"volume":volume,"port":port,"database":database,"cid":cid}
        self.record(resource);self.inspect(resource)
        return resource

    def start(self,resource):
        for other in self.control.load()["resources"]:
            state=self.inspect(other)
            if other["cid"]!=resource["cid"] and state["running"]:
                raise BudgetDenied("another TASK103 PG still running")
        self.inspect(resource)
        self.control.reserve("container_start",{"cid":resource["cid"]})
        self.cli(["start",resource["cid"]])
        return self.inspect(resource)

    def admin_dsn(self,resource):
        # 只有已登记、标签/CID/镜像/挂载核定的本卡容器才可单项取回口令。
        raw=json.loads(self.cli(["container","inspect",resource["cid"]]).stdout)[0]
        owned_witness(raw,resource)
        values=[x.split("=",1)[1] for x in raw["Config"].get("Env",[]) if x.startswith("POSTGRES_PASSWORD=")]
        if len(values)!=1:raise BudgetDenied("bootstrap credential unavailable")
        secret=values[0];SECRET_VALUES.add(secret)
        from urllib.parse import quote
        return f"postgresql://postgres:{quote(secret,safe='')}@127.0.0.1:{resource['port']}/{resource['database']}"

    def stop(self,resource):
        self.inspect(resource)
        # 数据、容器和卷全部保留，不remove。
        result=subprocess.run(["docker","stop","--time","10",resource["cid"]],capture_output=True,timeout=30,
                              creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode:raise RuntimeError("owned container stop unconfirmed")
        raw=json.loads(subprocess.run(["docker","container","inspect",resource["cid"]],capture_output=True,
             timeout=30,check=True,creationflags=subprocess.CREATE_NO_WINDOW).stdout)[0]
        state=owned_witness(raw,resource)
        if state["running"] or state["pid"]!=0:raise BudgetDenied("owned container still running")
        self.control.record({"cleanup_container":state})
        return state

