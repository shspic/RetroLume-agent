"""每种独立故障的专用生产控制进程，注入方法固定，无公开fault入口。"""
import asyncio,json,msvcrt,os,signal,sys,time,traceback
from pathlib import Path
from .control import CONTINUE_ROOT,PERMIT,atomic,source_snapshot
from .core import Harness
from .c01_seeds import diagnostic_artifact
from .c03_matrix import Session
from app.preview import production_supervisor as ps,docker_control as dc
from app.preview.process import birth,terminate_owned
from app.preview.description import digest
from app.runtime import psycopg_compatible_loop_factory

async def scenario(resource,built,out,command):
    name=command["scenario"];registry=Path(command["registry"]).resolve()
    h=Harness(resource,built,out,registry_dir=registry);s=None;creation=ps.creation_args;old_call=dc.call;old_ps_call=ps.call;old_popen=ps.subprocess.Popen
    mode="renderer_busy" if name=="renderer_busy" else "node_busy" if name=="node_busy" else "fake_console" if name=="reaper_death" else "none"
    def fixed_creation(intent,seccomp):
        args=creation(intent,seccomp);args[-1:-1]=["--env","RETROLUME_TASK111_FAULT_MODE="+mode];return args
    ps.creation_args=fixed_creation
    if name=="control_path_lost":
        def reaper_wrapper(args,*a,**kw):
            args=list(args)
            if "app.preview.production_reaper" in args:args[args.index("app.preview.production_reaper")]="tests.fixtures.task111.c03_reaper_unreachable"
            return old_popen(args,*a,**kw)
        ps.subprocess.Popen=reaper_wrapper
    try:
        await h.controller.recover();assert not h.controller.blocked
        item=await diagnostic_artifact(h,"energy",activity_id=command["activity_id"]);atomic(out/"fixture-item.json",item)
        s=Session(h,item,out);await s.open(heartbeat=name!="owner_control_lost");c=s.c
        trigger={"scenario":name,"activity_id":item["activity_id"],"preview_id":s.pid,"cid":c["cid"],"nonce":c["nonce"],"image_id":built["image"]["id"],"runtime_folder":str(c["folder"]),"t0_ns":c["t0_ns"],"deadline_ns":c["deadline_ns"],"at_ns":time.monotonic_ns(),"actor_pid":os.getpid(),"actor_birth":birth(os.getpid())["birth"]}
        before=dc.inspect_owned(h.policy.docker,c["cid"],c["intent"])
        atomic(out/"pretrigger.json",{**trigger,"before":before,"kernel":c["kernel_ready"],"reaper_owner":c["reaper_owner"],"job_names":[c["host_job"].name,c["reaper_job"].name],"pipe_handles":[msvcrt.get_osfhandle(c["attach"].stdout.fileno()),msvcrt.get_osfhandle(c["attach"].stderr.fileno())]})
        witness_deadline=time.monotonic()+5
        while not (out/"witness-bound.json").is_file():
            if time.monotonic()>witness_deadline:raise RuntimeError("independent witness missing")
            await asyncio.sleep(.02)
        if name in ("renderer_busy","node_busy"):
            trigger["method"]="frozen variant beforeInput executes fixed busy loop in "+("actual sandbox renderer" if name=="renderer_busy" else "actual Node host")
            atomic(out/"trigger.json",trigger)
            try:await s.input("h","3")
            except Exception as error:trigger["input_error_type"]=type(error).__name__
            else:raise AssertionError("busy input unexpectedly ACKed")
        elif name=="browser_busy":
            rows=c["kernel_ready"]["processes"]["rows"];target=None
            for row in rows:
                if row.get("Name")!="chrome":continue
                result=dc.call(h.policy.docker,["exec",c["cid"],"/bin/cat","/proc/"+str(row["pid"])+"/cmdline"])
                cmd=result["stdout"]
                if result["code"]==0 and "--type=" not in cmd:target=row;trigger["browser_command_receipt"]=result;break
            assert target is not None,"actual browser root PID unconfirmed"
            stat=dc.call(h.policy.docker,["exec",c["cid"],"/bin/cat","/proc/"+str(target["pid"])+"/stat"])
            assert stat["stdout"].split(') ',1)[1].split()[19]==target["birth_ticks"]
            trigger["target"]=target;trigger["signal"]=dc.call(h.policy.docker,["exec",c["cid"],"/bin/kill","-STOP",str(target["pid"])])
            assert trigger["signal"]["code"]==0;trigger["method"]="SIGSTOP to exact actual browser root, distinct from renderer and Node"
            atomic(out/"trigger.json",trigger)
            try:await s.input("h","3")
            except Exception as error:trigger["input_error_type"]=type(error).__name__
            else:raise AssertionError("suspended browser unexpectedly ACKed")
        elif name=="reaper_death":
            before=c["deadline_ns"];ack=await s.input("h","3");assert ack["accepted"] and ack["seq"]==1 and c["deadline_ns"]==before
            trigger["fake_console_postMessage"]=True;trigger["valid_ack"]=ack;trigger["unchanged_deadline_ns"]=before
            owner=c["reaper_owner"];trigger["reaper_terminated"]=terminate_owned(owner["pid"],owner["birth"]);assert trigger["reaper_terminated"]
            trigger["method"]="actual exact Reaper process termination; live Supervisor must rescue"
        elif name in ("supervisor_death","both_supervisors_death"):
            if name=="both_supervisors_death":
                owner=c["reaper_owner"];trigger["reaper_terminated"]=terminate_owned(owner["pid"],owner["birth"]);assert trigger["reaper_terminated"]
            trigger["method"]="actual controlling process exits; "+("Reaper remains independent" if name=="supervisor_death" else "both production supervisors have ended")
            atomic(out/"trigger.json",trigger);os._exit(71 if name=="supervisor_death" else 72)
        elif name=="control_path_lost":
            marker=c["folder"]/"control-unreachable.flag";marker.write_text("fixed TASK111 control-path test",encoding="ascii")
            def unavailable(docker,args,timeout=2):
                if marker.exists():raise dc.DockerUnknown("fixed_test_control_path_unavailable")
                return old_call(docker,args,timeout)
            dc.call=unavailable;ps.call=unavailable;trigger["method"]="both actual control processes reject Docker operations after immutable CID binding; daemon remains running"
            c["stop"].set()
        elif name=="pipe_corrupt":
            with h.controller._writer:c["attach"].stdin.write(b'\0\0\x08\x01bad');c["attach"].stdin.flush()
            trigger["method"]="actual anonymous pipe header length2049 exceeds2048"
        elif name=="hard_deadline":
            original=h.controller._db
            def frozen(awaitable):
                time.sleep(max(0,(c["deadline_ns"]+10**9-time.monotonic_ns())/1e9));return original(awaitable)
            h.controller._db=frozen;trigger["method"]="freeze actual Supervisor observation; independent production Reaper retains original D"
        elif name=="owner_control_lost":trigger["method"]="owner heartbeat withheld; only ownerless persistent reads remain"
        else:raise RuntimeError("fixed independent fault")
        atomic(out/"trigger.json",trigger)
        if name=="hard_deadline":
            until=c["deadline_ns"]+12*10**9
            while time.monotonic_ns()<until and not (c["folder"]/"supervisor-result.json").exists():await asyncio.sleep(.1)
            assert (c["folder"]/"reaper-receipt.json").exists(),"no independent Reaper deadline receipt"
            row,proof=await s.finish(request_stop=False,expected_confirmed=False)
        elif name=="control_path_lost":
            row,proof=await s.finish(request_stop=False,expected_confirmed=False)
            try:await h.controller.open(item["activity_id"],item["receipt"]["artifact_id"],__import__('app.preview.business_contracts',fromlist=['OpenPreview']).OpenPreview(start_key=str(__import__('uuid').uuid4()),expected_artifact_sha256=item["receipt"]["artifact_sha256"],input_owner_key="1"*64,confirmed=True))
            except Exception as error:trigger["new_start_refused_type"]=type(error).__name__
            else:raise AssertionError("unknown allowed start")
            atomic(out/"trigger.json",trigger)
        else:
            row,proof=await s.finish(request_stop=False)
            if name=="owner_control_lost":assert proof["error_code"]=="control_lost"
        atomic(out/"actor-result.json",{"status":"PASS_EXPECTED_UNKNOWN" if name in ("hard_deadline","control_path_lost") else "PASS_CONFIRMED_PRODUCTION_STOP","scenario":name,"row":row,"stop":proof})
    finally:
        ps.creation_args=creation;dc.call=old_call;ps.call=old_ps_call;ps.subprocess.Popen=old_popen
        if s and s.beat:s.closed=True;s.beat.cancel();await asyncio.gather(s.beat,return_exceptions=True)
        await h.controller.close()

def main():
    if os.environ.get("RETROLUME_TASK111_FIXTURE")!=PERMIT:raise RuntimeError("fault permit")
    command=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"));out=Path(command["out"]).resolve()
    if not out.is_relative_to(CONTINUE_ROOT.resolve()):raise RuntimeError("fault output scope")
    resource=json.loads(os.environ["RETROLUME_TASK111_RESOURCE"]);built=json.loads((CONTINUE_ROOT/"fault-build.json").read_text(encoding="utf-8"));source_snapshot(out)
    atomic(out/"actor-owner.json",{"pid":os.getpid(),"birth":birth(os.getpid())["birth"]})
    try:
        with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(scenario(resource,built,out,command))
    except Exception:
        text=traceback.format_exc()
        for secret in [resource.get(k,"") for k in ("admin","app","denied")]+list(resource.get("passwords",[])):
            if secret:text=text.replace(secret,"[redacted-task-secret]")
        (out/"actor-failure.txt").write_text(text,encoding="utf-8");raise SystemExit(1)

if __name__=="__main__":main()
