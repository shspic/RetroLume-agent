"""续作03每个真实子步骤新加载，合成凭据只在限定Env和内存。"""
import asyncio,hashlib,json,os,sys,time,traceback
from pathlib import Path
from .control import ROOT,CONTINUE_ROOT,PERMIT,atomic,source_snapshot,reserve,run,read_state,synthetic_root,event
from app.runtime import psycopg_compatible_loop_factory

async def parents(resource,built,folder):
    from .core import Harness
    from .c01_seeds import teaching_parent,diagnostic_artifact
    saved=CONTINUE_ROOT/"normal-parents.json"
    if saved.exists():
        previous=json.loads(saved.read_text(encoding="utf-8"))
        if previous["image_id"]==built["image"]["id"]:return previous["parents"]
    first=CONTINUE_ROOT/"root-10/step-04-ui/new-final-deployment-parents.json"
    if first.exists() and not saved.exists():
        previous=json.loads(first.read_text(encoding="utf-8"));atomic(saved,{"image_id":built["image"]["id"],"parents":previous});return previous
    h=Harness(resource,built,folder);rows=[]
    try:
        await h.controller.recover()
        if h.controller.blocked:raise RuntimeError("owner recovery unconfirmed")
        for kind,feedback in (("energy",False),("binomial",True)):
            aid,parent=await teaching_parent(h,kind,feedback);rows.append({"kind":kind,"activity_id":aid,"parent":parent})
        atomic(folder/"new-final-deployment-parents.json",rows)
        atomic(saved,{"image_id":built["image"]["id"],"parents":rows})
    finally:await h.controller.close()
    return rows

def ui(resource,built,folder):
    from .http_matrix import HttpMatrix,BASE
    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:rows=runner.run(parents(resource,built,folder))
    matrix=HttpMatrix(resource,built,folder)
    try:
        matrix.start();reserve("main_browser_starts",{"purpose":"C03 two final Native/UI and delayed guards"})
        payload={"base":BASE,"parents":rows,"out":str(folder),"remaining_ms":max(1,int((read_state()["active_batch"]["deadline_ns"]-time.monotonic_ns())/1000000)-15000)};atomic(folder/"browser-input.json",payload)
        from .resources import shell_env
        env=shell_env();env["RETROLUME_TASK111_BROWSER_SESSION"]=matrix.token
        run(["node",str(ROOT/"frontend/tests/task111/c03_browser_host.cjs"),str(folder/"browser-input.json")],folder,cwd=ROOT,env=env,maximum=600,name="real-main-ui")
        result=json.loads((folder/"ui-result.json").read_text(encoding="utf-8"))
        atomic(CONTINUE_ROOT/"native-progress.json",result["bindings"])
        import psycopg
        from psycopg.rows import dict_row
        ids=[r["activity_id"] for r in rows]
        with psycopg.connect(resource["app"],row_factory=dict_row) as conn:
            values=conn.execute("""SELECT c.activity_id::text,c.business_key::text,c.operation_id,c.status,c.terminal_disposition,c.config_sha256,c.request_sha256,
              a.artifact_id::text,a.artifact_sha256,a.body_sha256,a.renderer_sha256,o.state,r.payload_sha256
              FROM html_commands c JOIN activity_operations o ON o.activity_id=c.activity_id AND o.operation_id=c.operation_id
              LEFT JOIN html_artifacts a ON a.activity_id=c.activity_id AND a.business_key=c.business_key
              LEFT JOIN activity_operation_results r ON r.activity_id=c.activity_id AND r.operation_id=c.operation_id WHERE c.activity_id=ANY(%s::uuid[])""",(ids,)).fetchall()
        assert len(values)==2 and all(v["terminal_disposition"]=="succeeded" and v["state"]=="received" for v in values)
        atomic(folder/"same-object-commits.json",[dict(v) for v in values])
    finally:
        # 即使主UI中途失败，先给本次精确新活动的每个会话正常停止与物理确认机会。
        if matrix.process and matrix.process.poll() is None:
            import psycopg
            with psycopg.connect(resource["app"]) as conn:
                sessions=conn.execute("SELECT activity_id::text,preview_id::text,generation FROM html_preview_sessions WHERE activity_id=ANY(%s::uuid[]) AND state NOT IN ('stopped','failed_unstarted')",([r["activity_id"] for r in rows],)).fetchall()
            for aid,pid,generation in sessions:
                from uuid import uuid4
                matrix.request("POST",f"/api/activities/{aid}/html/previews/{pid}/stop",{"generation":generation,"stop_key":str(uuid4()),"reason":"user"})
                until=time.monotonic()+15
                while time.monotonic()<until:
                    last=matrix.request("GET",f"/api/activities/{aid}/html/previews/{pid}")
                    if last["state"] in ("stopped","cleanup_unconfirmed"):break
                    time.sleep(.1)
        if matrix.process:matrix.close()

def main():
    if os.environ.get("RETROLUME_TASK111_FIXTURE")!=PERMIT:raise RuntimeError("fixture permit")
    action=sys.argv[1];folder=Path(sys.argv[2]).resolve()
    if not folder.is_relative_to(CONTINUE_ROOT.resolve()):raise RuntimeError("step scope")
    resource=json.loads(os.environ["RETROLUME_TASK111_RESOURCE"]);built=json.loads((CONTINUE_ROOT/"active-build.json").read_text(encoding="utf-8"))
    from app.preview.process import birth
    atomic(folder/"actual-step-owner.json",{"pid":os.getpid(),"birth":birth(os.getpid())["birth"]});source_snapshot(folder)
    try:
        if action=="probe":
            from .c03_phase_a import probe
            with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(probe(resource,built,folder))
        elif action=="ui":ui(resource,built,folder)
        elif action=="schema_patch":
            from .c03_schema_patch import apply
            apply(resource,folder)
        elif action=="independent":
            from .c03_independent import run as independent
            independent(resource,built,folder)
        elif action=="independent_finish":
            from .c03_independent_finish import run as finish
            finish(resource,built,folder)
        elif action in ("boundaries","races","budgets","faults"):
            from .c03_matrix import execute
            execute(resource,built,folder,action)
        else:raise RuntimeError("fixed C03 action")
        atomic(folder/"step-result.json",{"status":"PASS_STEP_ONLY","action":action})
    except Exception:
        failure=traceback.format_exc()
        for secret in [resource.get(k,"") for k in ("admin","app","denied")]+list(resource.get("passwords",[])):
            if secret:failure=failure.replace(secret,"[redacted-task-secret]")
        (folder/"failure.txt").write_text(failure,encoding="utf-8");atomic(folder/"step-result.json",{"status":"FAIL","action":action});raise SystemExit(1)

if __name__=="__main__":main()
