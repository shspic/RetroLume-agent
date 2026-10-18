"""一次PG剩余启动的有限协调者；无工作立即收尾，跨根持有计整个real。"""
import asyncio,importlib,json,os,subprocess,sys,time,traceback
from pathlib import Path
from .control import ROOT,EVIDENCE,CONTINUE_ROOT,PERMIT,phase,batch,atomic,event,source_snapshot,state,locked
from .resources import pg_resume,stop_pg,shell_env
from app.preview.process import birth
from app.runtime import psycopg_compatible_loop_factory


def main():
    if os.environ.get("RETROLUME_TASK111_FIXTURE")!=PERMIT:raise RuntimeError("base fixture permit")
    phase("real");folder=CONTINUE_ROOT/"root-07";folder.mkdir(exist_ok=False);resource=None;guardian=None;lease=None;start=time.monotonic_ns()
    timing=json.loads((CONTINUE_ROOT/"timing.json").read_text());deadline=min(timing["original_deadline_ns"]-30000000000,start+10500*1000000000)
    try:
        with batch("real","c01-normal-PG-HTTP-browser-treeproof",3500):
            source_snapshot(folder)
            parent=birth(os.getpid());assert parent["state"]=="running"
            lease={"cid":"1791a2d086228c618bf043b0565e215828ff0ccfe5a858486488f1329a16ef51","parent_pid":os.getpid(),"parent_birth":parent["birth"],"deadline_ns":deadline,"completed":False}
            atomic(CONTINUE_ROOT/"pg-lease.json",lease)
            guardian=subprocess.Popen([sys.executable,"-B","-m","tests.fixtures.task111.c01_guardian",str(CONTINUE_ROOT/"pg-lease.json")],cwd=ROOT/"backend",env=shell_env(),stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
            until=time.monotonic()+2
            while not (CONTINUE_ROOT/"guardian-ready.json").is_file():
                if guardian.poll() is not None or time.monotonic()>until:raise RuntimeError("PG guardian ready")
                time.sleep(.02)
            resource=pg_resume(folder)
            built=json.loads((EVIDENCE/"real-01/production-build.json").read_text())
            from .runtime import install
            install()
            module=importlib.import_module("tests.fixtures.task111.c01_matrix")
            with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(module.verify(resource,built,folder))
    except Exception:
        (folder/"failure.txt").write_text(traceback.format_exc(),encoding="utf-8")
        event("c01_combined_failure",{"raw":str(folder/"failure.txt")})
    finally:
        # 新独立清场预留不经已经到期的业务guard；所有数据/对象保留。
        phase("cleanup")
        with batch("cleanup","c01-coordinator-exact-resource-cleanup",maximum=120):
            stop_pg(folder)
            if lease:lease["completed"]=True;atomic(CONTINUE_ROOT/"pg-lease.json",lease)
            if guardian:
                try:guardian.wait(timeout=3)
                except subprocess.TimeoutExpired:guardian.terminate();guardian.wait(timeout=3)
        atomic(CONTINUE_ROOT/"resource-span.json",{"start_ns":start,"end_ns":time.monotonic_ns(),"seconds":(time.monotonic_ns()-start)/1e9,"includes_between_roots":True,"held_after_return":False})
        phase("complete")


if __name__=="__main__":main()
