"""真实独立故障逐个运行；未知保R，外部精确清理后再按真实重启合同恢复。"""
import asyncio,json,os,subprocess,sys,time
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from .control import ROOT,CONTINUE_ROOT,PERMIT,atomic,read_state,source_snapshot
from .resources import shell_env
from .core import Harness
from app.preview import docker_control as dc
from app.preview.process import birth,terminate_owned
from app.preview.business_contracts import OpenPreview,HtmlRefusal
from app.runtime import psycopg_compatible_loop_factory

NAMES=("renderer_busy","browser_busy","node_busy","reaper_death","owner_control_lost","pipe_corrupt","supervisor_death","both_supervisors_death","control_path_lost","hard_deadline")

async def rescue(resource,built,out,registry,expected_unknown):
    trigger=json.loads((out/"trigger.json").read_text(encoding="utf-8"));folder=Path(trigger["runtime_folder"])
    value=json.loads((folder/"registry.json").read_text(encoding="utf-8"));facts=json.loads((folder/"kernel-premises.json").read_text(encoding="utf-8"))
    h=Harness(resource,built,out,registry_dir=registry)
    try:
        before=await h.ledger.read_html_preview(trigger["activity_id"],trigger["preview_id"]);item=json.loads((out/"fixture-item.json").read_text(encoding="utf-8"))
        if expected_unknown:
            assert before["reserved_seconds"]>=before["reserve_seconds"] and before["elapsed_seconds"] is None
            try:await h.controller.open(trigger["activity_id"],item["receipt"]["artifact_id"],OpenPreview(start_key=str(uuid4()),expected_artifact_sha256=item["receipt"]["artifact_sha256"],input_owner_key="1"*64,confirmed=True))
            except HtmlRefusal as error:assert error.code=="cleanup_unconfirmed"
            else:raise AssertionError("restart stole unknown preview")
        physical=dc.inspect_owned(h.policy.docker,value["cid"],value["intent"])
        # 本卡独立验收控制者只清精确CID。它不是生产双监督失联的自行停止能力。
        if physical["state"]["Running"]:kill=dc.call(h.policy.docker,["kill",value["cid"]]);atomic(out/"external-exact-kill.json",kill)
        attach=birth(value["attach_pid"]);attach_ended=attach["state"]=="exited"
        if not attach_ended:attach_ended=terminate_owned(value["attach_pid"],value["attach_birth"])
        proof=dc.stop_owned(h.policy.docker,value["cid"],value["intent"],facts,attach_ended=attach_ended)
        reaper=value.get("reaper_owner")
        if reaper:proof["owned_reaper_ended"]=terminate_owned(reaper["pid"],reaper["birth"])
        proof["actual_parent_ended"]=birth(value["parent"]["pid"])["state"]=="exited";proof["external_acceptance_cleanup"]=True
        atomic(out/"external-stop-proof.json",proof)
        assert proof["tree_confirmation"]=="private_pid_init_terminated" and proof["actual_parent_ended"]
        await h.controller.recover();assert not h.controller.blocked,"persistent recovery not confirmed"
        after=await h.ledger.read_html_preview(trigger["activity_id"],trigger["preview_id"]);assert after["state"]=="stopped" and after["reserved_seconds"]==0
        if expected_unknown:assert after["elapsed_seconds"]==before["reserve_seconds"],"unknown reserve was refunded"
        if trigger["scenario"]=="hard_deadline":
            finished=datetime.fromisoformat(physical["state"]["FinishedAt"].replace('Z','+00:00'));deadline=datetime.fromisoformat(before["deadline_at"])
            assert finished<=deadline,"physical container exit exceeded original D"
        atomic(out/"persistent-recovery.json",{"before":before,"after":after,"unknown_full_reserve_preserved_until_confirmed":expected_unknown,"external_controller_scope":"only exact registered CID and born owned processes"})
    finally:await h.controller.close()

def run_all(resource,production,folder):
    built=json.loads((CONTINUE_ROOT/"fault-build.json").read_text(encoding="utf-8"));plan=json.loads((CONTINUE_ROOT/"matrix-plan.json").read_text(encoding="utf-8"));results=[]
    for name in NAMES:
        out=folder/name;out.mkdir(exist_ok=False);registry=(CONTINUE_ROOT/"synthetic/fault-control"/name).resolve()
        command={"scenario":name,"activity_id":plan["objects"]["fault_"+name]["activity_id"],"registry":str(registry),"out":str(out)};atomic(out/"command.json",command)
        env=shell_env();env.update(RETROLUME_TASK111_FIXTURE=PERMIT,RETROLUME_TASK111_RESOURCE=json.dumps(resource))
        with (out/"actor.stdout.bin").open("wb") as stdout,(out/"actor.stderr.bin").open("wb") as stderr:
            child=subprocess.Popen([sys.executable,"-B","-m","tests.fixtures.task111.c03_fault_actor",str(out/"command.json")],cwd=ROOT/"backend",env=env,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
            atomic(out/"launcher.json",{"pid":child.pid,"birth":birth(child.pid)})
            try:child.wait(timeout=min(120,max(.1,(read_state()["active_batch"]["deadline_ns"]-time.monotonic_ns())/1e9)))
            except subprocess.TimeoutExpired:
                own=json.loads((out/"actor-owner.json").read_text(encoding="utf-8"));terminate_owned(own["pid"],own["birth"]);child.wait(5)
        expected_code=71 if name=="supervisor_death" else 72 if name=="both_supervisors_death" else 0
        actual=child.returncode;unknown=name in ("both_supervisors_death","control_path_lost","hard_deadline")
        # 所有死亡/未知都由独立验收控制者收精确对象，再保存真正的重启恢复。
        if name in ("supervisor_death","both_supervisors_death","control_path_lost","hard_deadline") or actual!=expected_code:
            if not (out/"trigger.json").exists():raise RuntimeError("fault failed before precise ownership: "+name)
            # 给仍独立存活的生产Reaper父死亡检测机会，不用外部kill冒它的成果。
            if name=="supervisor_death":
                trig=json.loads((out/"trigger.json").read_text(encoding="utf-8"));rpath=Path(trig["runtime_folder"])/"reaper-receipt.json";until=time.monotonic()+8
                while not rpath.exists() and time.monotonic()<until:time.sleep(.05)
                assert rpath.exists(),"independent reaper parent-loss receipt missing"
            with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(rescue(resource,built,out,registry,unknown))
        else:
            report=json.loads((out/"actor-result.json").read_text(encoding="utf-8"));assert report["stop"]["confirmed"]
        result={"scenario":name,"actor_exit":actual,"expected_exit":expected_code,"status":"PASS_EXPECTED_BEHAVIOR" if actual==expected_code else "FAIL_ACTOR_WITH_PRECISE_RESCUE","fault_variant":True,"production_navigation_pass":False};results.append(result);atomic(folder/"fault-results.json",results)
    if any(x["status"]!="PASS_EXPECTED_BEHAVIOR" for x in results):raise RuntimeError("fault actor had retained failures")
