"""独立PG租约清场闸；父死亡/固定截止，只核并停止精确已登记CID。"""
import json,os,subprocess,sys,time
from pathlib import Path
from app.preview.process import birth,atomic_json
from .resources import DOCKER,PG,PG_IMAGE,shell_env


def main():
    path=Path(sys.argv[1]);value=json.loads(path.read_text());own=birth(os.getpid())
    if own["state"]!="running":raise RuntimeError("guardian birth")
    atomic_json(path.with_name("guardian-ready.json"),{"pid":os.getpid(),"birth":own["birth"],"deadline_ns":value["deadline_ns"]})
    while True:
        try:current=json.loads(path.read_text())
        except (OSError,ValueError):current=value
        if current.get("completed"):return
        parent=birth(value["parent_pid"])
        if parent["state"]!="running" or parent.get("birth")!=value["parent_birth"] or time.monotonic_ns()>=value["deadline_ns"]:break
        time.sleep(.1)
    fmt='{"id":{{json .Id}},"image":{{json .Image}},"name":{{json .Name}},"running":{{json .State.Running}},"pid":{{json .State.Pid}}}'
    receipt={"guardian_pid":os.getpid(),"expected_cid":value["cid"],"confirmed":False}
    try:
        before=subprocess.run([DOCKER,"inspect","--format",fmt,value["cid"]],capture_output=True,timeout=5,env=shell_env(),creationflags=subprocess.CREATE_NO_WINDOW)
        actual=json.loads(before.stdout)
        if before.returncode or actual["id"]!=value["cid"] or actual["image"]!=PG_IMAGE.split("@")[1] or actual["name"]!="/"+PG:raise RuntimeError("PG guardian ownership")
        if actual["running"]:subprocess.run([DOCKER,"stop","--time","5",value["cid"]],capture_output=True,timeout=15,env=shell_env(),creationflags=subprocess.CREATE_NO_WINDOW)
        after=subprocess.run([DOCKER,"inspect","--format",fmt,value["cid"]],capture_output=True,timeout=5,env=shell_env(),creationflags=subprocess.CREATE_NO_WINDOW)
        receipt["after"]=json.loads(after.stdout);receipt["confirmed"]=after.returncode==0 and not receipt["after"]["running"] and receipt["after"]["pid"]==0
    except Exception as error:receipt["error"]=type(error).__name__
    receipt["at_ns"]=time.monotonic_ns();atomic_json(path.with_name("guardian-result.json"),receipt)


if __name__=="__main__":main()
