"""唯一PG持有者，真实根和总账硬门自动检测，普通修正沿本窗加载。"""
import hashlib,json,os,subprocess,sys,time,traceback
from .control import ROOT,EVIDENCE,CONTINUE_ROOT,CONTINUATION,PERMIT,atomic,batch,phase,state,read_state,event,source_snapshot,reserve,run,CAPS
from .resources import pg_resume,build_renderer,shell_env
from .c03_resources import guardian,cleanup
from app.preview.process import birth,terminate_owned

def main():
    if os.environ.get("RETROLUME_TASK111_FIXTURE")!=PERMIT or CONTINUATION!="TASK-111-G11-C03-20261011":raise RuntimeError("C03 permit")
    resource=None;guard=None;stop=False;step=0
    timing=json.loads((CONTINUE_ROOT/"timing.json").read_text(encoding="utf-8"));current=read_state()
    remaining=min(14400-current["time_seconds"]["real"],7200-(current["time_seconds"]["real"]-timing["prior_time_seconds"]["real"]))
    hold_deadline=min(current["business_deadline_ns"],time.monotonic_ns()+int(remaining*1e9));phase("real")
    lease_folder=CONTINUE_ROOT/"integrated-holder";lease_folder.mkdir(exist_ok=False)
    atomic(lease_folder/"owner.json",{"pid":os.getpid(),"birth":birth(os.getpid()),"deadline_ns":hold_deadline})
    try:
        for root_no in range(current["counts"]["real_batches"]+1,CAPS["real_batches"]+1):
            if stop:break
            folder=CONTINUE_ROOT/("root-"+str(root_no).zfill(2));folder.mkdir(exist_ok=False)
            with batch("real","C03-final-production-business-and-matrix",maximum=1800) as active:
                source_snapshot(folder)
                if resource is None:
                    guard=guardian(lease_folder,hold_deadline);resource=pg_resume(folder)
                    built=build_renderer(folder);atomic(CONTINUE_ROOT/"active-build.json",built)
                    reserve("frontend_typecheck_build_batches",{"purpose":"C03 final affected UI"})
                    run(["cmd.exe","/c","npm.cmd","run","build"],folder,cwd=ROOT/"frontend",maximum=180,name="frontend-build")
                    atomic(CONTINUE_ROOT/"frontend-bundle.json",[{"path":p.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in (ROOT/"frontend/dist").rglob("*") if p.is_file()])
                    command={"action":"probe"}
                else:command=None
                atomic(CONTINUE_ROOT/"coordinator-ready.json",{"pid":os.getpid(),"birth":birth(os.getpid()),"root":root_no,"root_deadline_ns":active["deadline_ns"],"hold_deadline_ns":hold_deadline})
                while time.monotonic_ns()<min(active["deadline_ns"],hold_deadline):
                    path=CONTINUE_ROOT/("command-"+str(step+1).zfill(2)+".json")
                    if command is None:
                        if not path.exists():time.sleep(.1);continue
                        command=json.loads(path.read_text(encoding="utf-8"))
                    step+=1;action=command["action"];command=None
                    if action=="stop":stop=True;break
                    if action=="next_root":break
                    out=folder/("step-"+str(step).zfill(2)+"-"+action);out.mkdir(exist_ok=False)
                    try:
                        if action=="build":
                            built=build_renderer(out);atomic(CONTINUE_ROOT/"active-build.json",built)
                        elif action=="fault_build":
                            from .c03_variant import build
                            build(out)
                        elif action=="frontend_build":
                            reserve("frontend_typecheck_build_batches",{"purpose":"C03 evidenced UI correction"})
                            run(["cmd.exe","/c","npm.cmd","run","build"],out,cwd=ROOT/"frontend",maximum=180,name="frontend-build")
                            atomic(CONTINUE_ROOT/"frontend-bundle.json",[{"path":p.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in (ROOT/"frontend/dist").rglob("*") if p.is_file()])
                        else:
                            env=shell_env();env.update(RETROLUME_TASK111_FIXTURE=PERMIT,RETROLUME_TASK111_RESOURCE=json.dumps(resource),PYTHONPATH=str(ROOT/"backend/tests/fixtures/task111/bootstrap")+os.pathsep+str(ROOT/"backend"))
                            with (out/"stdout.bin").open("wb") as stdout,(out/"stderr.bin").open("wb") as stderr:
                                child=subprocess.Popen([sys.executable,"-B","-m","tests.fixtures.task111.c03_step",action,str(out)],cwd=ROOT/"backend",env=env,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
                                atomic(out/"launcher.json",{"pid":child.pid,"birth":birth(child.pid)})
                                try:child.wait(timeout=min(900,max(.1,(active["deadline_ns"]-time.monotonic_ns())/1e9)))
                                except subprocess.TimeoutExpired:
                                    owner=json.loads((out/"actual-step-owner.json").read_text(encoding="utf-8"));terminate_owned(owner["pid"],owner["birth"]);child.wait(5);raise RuntimeError("C03 fixed child deadline")
                                if child.returncode:raise RuntimeError("C03 step failed: "+action)
                        atomic(out/"coordinator-result.json",{"status":"PASS_STEP_ONLY","action":action})
                    except Exception:
                        (out/"coordinator-failure.txt").write_text(traceback.format_exc(),encoding="utf-8");atomic(out/"coordinator-result.json",{"status":"FAIL","action":action})
                    atomic(CONTINUE_ROOT/"step-complete.json",{"step":step,"action":action,"folder":str(out)})
    finally:
        phase("cleanup");cleanup(lease_folder,guard);phase("implementation_offline")

if __name__=="__main__":main()
