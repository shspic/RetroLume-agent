"""复用原步骤循环的单PG持有者，真实根固定；各子步骤全新加载。"""
import json,os,subprocess,sys,time,traceback
from pathlib import Path
from .control import ROOT,EVIDENCE,CONTINUE_ROOT,PERMIT,atomic,batch,phase,state,read_state,event,source_snapshot
from .resources import pg_resume,shell_env,DOCKER,PG_IMAGE
from app.preview.process import birth

CID="1791a2d086228c618bf043b0565e215828ff0ccfe5a858486488f1329a16ef51"


def main():
    if os.environ.get("RETROLUME_TASK111_FIXTURE")!=PERMIT:raise RuntimeError("fixture permit")
    phase("real");holder_start=time.monotonic_ns();remaining=14400-read_state()["time_seconds"]["real"]
    hold_deadline=min(state()["business_deadline_ns"],holder_start+int(remaining*1e9))
    owner=birth(os.getpid());lease={"cid":CID,"parent_pid":os.getpid(),"parent_birth":owner["birth"],"deadline_ns":hold_deadline,"completed":False}
    lease_path=CONTINUE_ROOT/"pg-lease.json";atomic(lease_path,lease);guardian=None;resource=None;matrix=None;step=0;finish=False
    built=json.loads((EVIDENCE/"real-01/production-build.json").read_text());native_path=None
    def subprocess_step(action,out):
        env=shell_env();env.update(RETROLUME_TASK111_FIXTURE=PERMIT,RETROLUME_TASK111_RESOURCE=json.dumps(resource),PYTHONPATH=str(ROOT/"backend/tests/fixtures/task111/bootstrap")+os.pathsep+str(ROOT/"backend"))
        with (out/"step.stdout.bin").open("wb") as stdout,(out/"step.stderr.bin").open("wb") as stderr:
            child=subprocess.Popen([sys.executable,"-B","-m","tests.fixtures.task111.c02_step",action,str(out)],cwd=ROOT/"backend",env=env,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
            atomic(out/"step-owner.json",{"pid":child.pid,"birth":birth(child.pid)})
            try:child.wait(timeout=min(240,(state()["active_batch"]["deadline_ns"]-time.monotonic_ns())/1e9))
            except subprocess.TimeoutExpired:child.terminate();child.wait(5);raise RuntimeError("fixed child step deadline")
            if child.returncode:raise RuntimeError("step failed: "+action)
    try:
        for root_number in (7,8,9):
            if finish:break
            folder=CONTINUE_ROOT/("root-"+str(root_number).zfill(2));folder.mkdir(exist_ok=False)
            with batch("real","c02-normal-then-missing-matrix",maximum=3500):
                root_deadline=min(state()["active_batch"]["deadline_ns"],hold_deadline)
                if resource is None:
                    guardian=subprocess.Popen([sys.executable,"-B","-m","tests.fixtures.task111.c01_guardian",str(lease_path)],cwd=ROOT/"backend",env=shell_env(),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
                    until=time.monotonic()+3
                    while not (CONTINUE_ROOT/"guardian-ready.json").exists():
                        if guardian.poll() is not None or time.monotonic()>until:raise RuntimeError("guardian ready")
                        time.sleep(.02)
                    resource=pg_resume(folder)
                atomic(CONTINUE_ROOT/"coordinator-ready.json",{"pid":os.getpid(),"birth":owner,"root":root_number,"root_deadline_ns":root_deadline,"hold_deadline_ns":hold_deadline})
                while time.monotonic_ns()<root_deadline:
                    command_path=CONTINUE_ROOT/("step-"+str(step+1).zfill(2)+".json")
                    if step==0:command={"action":"native"}
                    elif command_path.exists():command=json.loads(command_path.read_text())
                    else:
                        intent_path=CONTINUE_ROOT/"work-intent.json"
                        if not intent_path.exists() or time.time()-intent_path.stat().st_mtime>300:finish=True;break
                        time.sleep(.1);continue
                    step+=1;action=command["action"]
                    if action=="stop":finish=True;break
                    if action=="next_root":break
                    out=folder/("attempt-"+str(step).zfill(2));out.mkdir(exist_ok=False);source_snapshot(out)
                    try:
                        if action in ("native","pg","diagnostic"):
                            if matrix is not None:raise RuntimeError("stop API consumer before data-helper owns mutex")
                            subprocess_step(action,out)
                            if action=="native":native_path=out/"native-final-template.json"
                        elif action=="normal":
                            from .http_matrix import HttpMatrix
                            from .c02_normal import cases,verify_after_browser
                            if matrix is None:matrix=HttpMatrix(resource,built,out);matrix.start()
                            matrix.folder=out;matrix.browser(cases(json.loads(Path(command.get("native_results",native_path)).read_text())))
                            verify_after_browser(matrix,out)
                        elif action=="close_api":
                            if matrix is not None:matrix.close();matrix=None
                        elif action=="faults":
                            from .c02_faults import verify
                            if matrix is None:
                                from .http_matrix import HttpMatrix
                                matrix=HttpMatrix(resource,built,out);matrix.start()
                            matrix.folder=out;verify(resource,built,out,matrix,command)
                        else:raise RuntimeError("bounded action")
                        atomic(out/"coordinator-step-result.json",{"status":"PASS_STEP_ONLY","action":action})
                    except Exception:
                        (out/"coordinator-failure.txt").write_text(traceback.format_exc(),encoding="utf-8")
                        atomic(out/"coordinator-step-result.json",{"status":"FAIL","action":action})
                    atomic(CONTINUE_ROOT/"step-complete.json",{"step":step,"action":action,"folder":str(out),"API_pid":matrix.process.pid if matrix else None})
    finally:
        if matrix is not None:
            try:matrix.close()
            except Exception:pass
        # 这里直接精确inspect/stop，与业务state/phase/event无依赖。
        started=time.monotonic_ns();receipt={"cid":CID,"confirmed":False}
        fmt='{"id":{{json .Id}},"image":{{json .Image}},"name":{{json .Name}},"running":{{json .State.Running}},"pid":{{json .State.Pid}}}'
        try:
            before=subprocess.run([DOCKER,"inspect","--format",fmt,CID],capture_output=True,timeout=5,env=shell_env(),creationflags=subprocess.CREATE_NO_WINDOW)
            actual=json.loads(before.stdout)
            if before.returncode or actual["id"]!=CID or actual["image"]!=PG_IMAGE.split("@")[1] or actual["name"]!="/retrolume-task-111-g11-v2-pg1":raise RuntimeError("cleanup binding")
            if actual["running"]:subprocess.run([DOCKER,"stop","--time","5",CID],capture_output=True,timeout=15,env=shell_env(),creationflags=subprocess.CREATE_NO_WINDOW)
            after=subprocess.run([DOCKER,"inspect","--format",fmt,CID],capture_output=True,timeout=5,env=shell_env(),creationflags=subprocess.CREATE_NO_WINDOW)
            receipt["after"]=json.loads(after.stdout);receipt["confirmed"]=after.returncode==0 and not receipt["after"]["running"] and receipt["after"]["pid"]==0
        except Exception as error:receipt["error"]=type(error).__name__
        if receipt["confirmed"]:lease["completed"]=True;atomic(lease_path,lease)
        if guardian:
            try:guardian.wait(3)
            except subprocess.TimeoutExpired:guardian.terminate();guardian.wait(3)
        receipt["seconds"]=(time.monotonic_ns()-started)/1e9;atomic(CONTINUE_ROOT/"coordinator-cleanup.json",receipt)
        # 精确清场已执行后才记分类，不允许记账调用挡住资源收尾。
        try:phase("cleanup")
        except Exception:pass
        with __import__('tests.fixtures.task111.control',fromlist=['locked']).locked():
            current=read_state();current["time_seconds"]["cleanup"]+=receipt["seconds"];atomic(EVIDENCE/"budget.json",current)
        atomic(CONTINUE_ROOT/"resource-span.json",{"start_ns":holder_start,"end_ns":started,"seconds":(started-holder_start)/1e9,"PG_hold_includes_between_roots":True,"charged_in_root_spans":True,"held_after_return":False})
        event("c02_coordinator_cleanup",receipt,cleanup=True);phase("complete")


if __name__=="__main__":main()
