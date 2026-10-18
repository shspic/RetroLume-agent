"""仅精确本卡API测试进程的继承stdin控制，固定场景，不是公开路由或生产开关。"""
import asyncio,json,os,time,signal
from pathlib import Path
from .control import EVIDENCE,CONTINUE_ROOT,PERMIT,atomic,event
from app.preview.process import birth,terminate_owned
from app.preview.docker_control import call,inspect_owned
from app.runtime import psycopg_compatible_loop_factory
from .c01_faults import PLAN


def read_commands(app,stream):
    if os.environ.get("RETROLUME_TASK111_FIXTURE")!=PERMIT:raise RuntimeError("control permit")
    for line in stream:
        try:
            if len(line)>1024:raise ValueError("fixture control size")
            command=json.loads(line)
            if set(command)!={"scenario","activity_id","preview_id","generation"} or command["scenario"] not in PLAN:raise ValueError("fixture control fields")
            run(app,command)
        except Exception as error:event("c01_fault_control_error",{"type":type(error).__name__})


def run(app,command):
    controller=app.state.preview_controller;until=time.monotonic()+8;c=None
    while time.monotonic()<until:
        c=controller.current
        if c and c["preview_id"]==command["preview_id"] and c["generation"]==command["generation"] and c["state"] in ("ready","running"):break
        if c and c["state"]=="cleanup_unconfirmed":raise RuntimeError("cannot inject unknown tree")
        time.sleep(.02)
    if c is None or c["state"] not in ("ready","running"):raise RuntimeError("fault requires ready same object")
    name=command["scenario"];receipt={"scenario":name,"preview_id":c["preview_id"],"cid":c["cid"],"nonce":c["nonce"],"at_ns":time.monotonic_ns()}
    inspect_owned(controller.policy.docker,c["cid"],c["intent"])
    if name in ("renderer_busy","browser_busy"):
        rows=c["kernel_ready"]["processes"]["rows"]
        target=next(row["pid"] for row in rows if ("chrome" in row.get("Name","") and (name=="browser_busy" or row["pid"]!=1)))
        receipt["signal"]=call(controller.policy.docker,["exec",c["cid"],"/bin/kill","-STOP",str(target)])
        c["stop"].set()
    elif name=="reaper_death":
        reaper=json.loads((c["folder"]/"reaper-ready.json").read_text());receipt["owned_terminated"]=terminate_owned(reaper["pid"],reaper["birth"])
    elif name=="supervisor_death":
        atomic(CONTINUE_ROOT/("trigger-"+c["preview_id"]+".json"),{**receipt,"action":"exact supervisor process exit"})
        os._exit(71)
    elif name=="control_lost":receipt["action"]="owner heartbeat withheld by caller"
    elif name=="pipe_corrupt":
        c["attach"].stdin.write(b"\0\0\x08\x01bad");c["attach"].stdin.flush();receipt["action"]="invalid limited pipe header to same attached object"
    elif name=="hard_deadline":
        # 冻结本卡监督者的后续数据库观察；独立Reaper仍按原D停止，不延限。
        original=controller._db
        def frozen(awaitable):
            if time.monotonic_ns()<c["deadline_ns"]+1000000000:time.sleep(max(0,(c["deadline_ns"]+1000000000-time.monotonic_ns())/1e9))
            return original(awaitable)
        controller._db=frozen;receipt["action"]="test process observer frozen until original D; reaper independent"
    elif name=="cancel_refresh_budget":
        async def cancel():await app.state.activities_ledger.cancel_activity(command["activity_id"])
        with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(cancel())
        receipt["action"]="actual activity cancellation"
    elif name=="qualification_cache_barrier":
        c["stop"].set();receipt["status"]="NOT_RUN_EXACT_BARRIER";receipt["action"]="scenario requires dedicated public cache barrier; not represented by stop"
    elif name=="create_reply_lost":
        c["stop"].set();receipt["status"]="NOT_RUN_CREATE_LOSS";receipt["action"]="existing started object cannot represent pre-bind loss"
    atomic(CONTINUE_ROOT/("trigger-"+c["preview_id"]+".json"),receipt);event("c01_fault_trigger",receipt)
