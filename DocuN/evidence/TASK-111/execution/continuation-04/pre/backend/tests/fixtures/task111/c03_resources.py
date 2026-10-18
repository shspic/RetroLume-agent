"""本卡PG外部清场与租约，独立于已到期的业务预算入口。"""
import json,os,subprocess,sys,time
from .control import ROOT,CONTINUE_ROOT,EVIDENCE,atomic,locked,read_state,event
from .resources import DOCKER,PG_IMAGE,shell_env
from app.preview.process import birth

CID="1791a2d086228c618bf043b0565e215828ff0ccfe5a858486488f1329a16ef51"

def guardian(folder,deadline):
    parent=birth(os.getpid())
    if parent["state"]!="running":raise RuntimeError("coordinator ownership unknown")
    lease={"cid":CID,"parent_pid":os.getpid(),"parent_birth":parent["birth"],"deadline_ns":deadline,"completed":False}
    path=folder/"pg-lease.json";atomic(path,lease)
    child=subprocess.Popen([sys.executable,"-B","-m","tests.fixtures.task111.c01_guardian",str(path)],cwd=ROOT/"backend",env=shell_env(),
       stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
    until=time.monotonic()+3
    while not (folder/"guardian-ready.json").exists():
        if child.poll() is not None or time.monotonic()>until:raise RuntimeError("PG guardian did not ready")
        time.sleep(.02)
    atomic(folder/"guardian-launcher.json",{"pid":child.pid,"birth":birth(child.pid)})
    return child,path,lease

def cleanup(folder,guard=None):
    started=time.monotonic_ns();receipt={"cid":CID,"confirmed":False}
    fmt='{"id":{{json .Id}},"image":{{json .Image}},"name":{{json .Name}},"running":{{json .State.Running}},"pid":{{json .State.Pid}},"restart_count":{{json .RestartCount}}}'
    try:
        before=subprocess.run([DOCKER,"inspect","--format",fmt,CID],capture_output=True,timeout=5,env=shell_env(),creationflags=subprocess.CREATE_NO_WINDOW)
        current=json.loads(before.stdout)
        if before.returncode or current["id"]!=CID or current["image"]!=PG_IMAGE.split("@")[1] or current["name"]!="/retrolume-task-111-g11-v2-pg1":raise RuntimeError("PG cleanup identity")
        receipt["before"]=current
        if current["running"]:
            stop=subprocess.run([DOCKER,"stop","--time","5",CID],capture_output=True,timeout=15,env=shell_env(),creationflags=subprocess.CREATE_NO_WINDOW);receipt["stop_code"]=stop.returncode
        after=subprocess.run([DOCKER,"inspect","--format",fmt,CID],capture_output=True,timeout=5,env=shell_env(),creationflags=subprocess.CREATE_NO_WINDOW)
        receipt["after"]=json.loads(after.stdout);receipt["confirmed"]=after.returncode==0 and not receipt["after"]["running"] and receipt["after"]["pid"]==0
    except Exception as error:receipt["error_type"]=type(error).__name__
    if guard:
        child,path,lease=guard
        if receipt["confirmed"]:lease["completed"]=True;atomic(path,lease)
        try:child.wait(3)
        except subprocess.TimeoutExpired:child.terminate();child.wait(3)
        receipt["guardian_exit"]=child.returncode
    receipt["seconds"]=(time.monotonic_ns()-started)/1e9;atomic(folder/"pg-cleanup.json",receipt)
    with locked():
        current=read_state();current["time_seconds"]["cleanup"]+=receipt["seconds"];atomic(EVIDENCE/"budget.json",current)
    event("c03_exact_pg_cleanup",receipt,cleanup=True)
    return receipt
