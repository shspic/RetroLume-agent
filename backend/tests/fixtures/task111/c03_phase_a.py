"""先取得最小生产renderer闭环，不启动主UI或再次发送模型。"""
import asyncio,hashlib,json,os,secrets,time,traceback
from uuid import uuid4
from .control import ROOT,EVIDENCE,PERMIT,CONTINUE_ROOT,batch,phase,atomic,source_snapshot,reserve
from .resources import build_renderer,pg_resume
from .c03_resources import guardian,cleanup
from .core import Harness
from .c01_seeds import diagnostic_artifact
from app.preview.business_contracts import OpenPreview,PreviewInput
from app.preview.description import digest
from app.preview.pipe import send_packet,validate_png
from app.runtime import psycopg_compatible_loop_factory

async def probe(resource,built,folder):
    h=Harness(resource,built,folder);closed=False;heartbeat=None;c=None
    try:
        await h.controller.recover()
        if h.controller.blocked:raise RuntimeError("preexisting owner unconfirmed")
        item=await diagnostic_artifact(h,"energy");atomic(folder/"synthetic-producer-prerequisite.json",item)
        artifact=await h.ledger.read_html_artifact(item["activity_id"],item["receipt"]["artifact_id"])
        owner=secrets.token_hex(32)
        opened=await h.controller.open(item["activity_id"],artifact["artifact_id"],OpenPreview(start_key=str(uuid4()),expected_artifact_sha256=artifact["artifact_sha256"],input_owner_key=owner,confirmed=True))
        pid=opened["preview_id"];c=h.controller.current
        async def keep():
            while not closed:
                await h.controller.status(item["activity_id"],pid,owner);await asyncio.sleep(.2)
        heartbeat=asyncio.create_task(keep());until=c["t0_ns"]+8*10**9;last=opened
        while time.monotonic_ns()<until:
            last=await h.controller.status(item["activity_id"],pid,owner)
            if last["state"] in ("ready","stopped","cleanup_unconfirmed","failed_unstarted"):break
            await asyncio.sleep(.03)
        atomic(folder/"ready-observation.json",{"row":last,"t0_ns":c["t0_ns"],"observed_ns":time.monotonic_ns(),"deadline_ns":c["deadline_ns"]})
        if last["state"]!="ready":raise RuntimeError("production renderer did not ready: "+last["state"])
        rows=[];pngs=[]
        for seq,(control,value,oracle) in enumerate((("h","3",58.8),("h","0",0),("m","0",0)),1):
            action={"type":"set_number","control_id":"hctl_"+control,"value":value};reserve("internal_inputs",{"case":"minimal-core","seq":seq})
            ack=await h.controller.input(item["activity_id"],pid,PreviewInput(preview_generation=last["generation"],seq=seq,payload_sha256=digest(action),event=action),owner)
            assert ack["accepted"] and abs(float(ack["readouts"][0]["value"])-oracle)<=1e-9
            await asyncio.sleep(.45);packet=await h.controller.frame(item["activity_id"],pid,last["generation"],0,owner)
            assert packet is not None;validate_png(packet[1]);name="remote-"+str(seq)+".png";(folder/name).write_bytes(packet[1])
            pngs.append({"path":name,"sha256":hashlib.sha256(packet[1]).hexdigest(),"head":packet[0]});rows.append({"event":action,"oracle":oracle,"ack":ack})
            atomic(folder/"remote-acks.json",rows)
        assert pngs[0]["sha256"]!=pngs[1]["sha256"],"zero boundary did not change actual PNG"
        previous=c["last_ack"];action={"type":"set_number","control_id":"hctl_h","value":"-1"};reserve("internal_inputs",{"case":"host-domain-refusal"})
        c["input_seq"]+=1;c["ack"].clear();c["last_payload_sha256"]=digest(action)
        with h.controller._writer:send_packet(c["attach"].stdin,c,"input",c["input_seq"],action)
        assert await asyncio.to_thread(c["ack"].wait,2)
        refusal=c["last_ack"];assert not refusal["accepted"]
        for key in ("readouts","figures","input_values"):assert refusal[key]==previous[key],key
        atomic(folder/"host-domain-refusal.json",{"method":"bounded internal v2 input to actual fixed host","ack":refusal,"complete_snapshot_retained":True})
        await asyncio.sleep(.4);packet=await h.controller.frame(item["activity_id"],pid,last["generation"],0,owner)
        if packet:(folder/"rejected-frame.png").write_bytes(packet[1])
        assert packet and hashlib.sha256(packet[1]).hexdigest()==pngs[-1]["sha256"]
        atomic(folder/"png-identities.json",pngs)
        await h.controller.stop(item["activity_id"],pid,last["generation"])
        until=time.monotonic()+15
        while time.monotonic()<until:
            final=await h.controller.status(item["activity_id"],pid,owner)
            if final["state"] in ("stopped","cleanup_unconfirmed"):break
            await asyncio.sleep(.05)
        assert final["state"]=="stopped",final["state"]
        await asyncio.to_thread(c["thread"].join,3)
        proof=json.loads((c["folder"]/"supervisor-result.json").read_text(encoding="utf-8"))
        assert proof["confirmed"] and proof["proof"]["tree_confirmation"]=="private_pid_init_terminated"
        atomic(folder/"phase-a-result.json",{"status":"PASS_REAL_RUNTIME_CORE","item":item,"preview_id":pid,"runtime_folder":str(c["folder"]),"image_id":built["image"]["id"],
          "load_manifest_sha256":built["load_manifest_sha256"],"remote_acks":rows,"pngs":pngs,"stop_proof":proof,"final":final,"Native_or_main_UI_chain":False})
    finally:
        closed=True
        if heartbeat:heartbeat.cancel();await asyncio.gather(heartbeat,return_exceptions=True)
        await h.controller.close()

def main():
    if os.environ.get("RETROLUME_TASK111_FIXTURE")!=PERMIT:raise RuntimeError("fixture permit")
    folder=CONTINUE_ROOT/"phase-a-root09";folder.mkdir(exist_ok=False);guard=None;resource=None
    phase("real")
    try:
        with batch("real","C03-build-and-minimal-renderer",maximum=1800) as active:
            source_snapshot(folder);guard=guardian(folder,active["deadline_ns"])
            built=build_renderer(folder);atomic(CONTINUE_ROOT/"active-build.json",built)
            resource=pg_resume(folder)
            with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(probe(resource,built,folder))
    except Exception:
        failure=traceback.format_exc()
        if resource:
            for key in ("admin","app","denied"):
                failure=failure.replace(resource[key],"[redacted-task-dsn]")
        (folder/"failure.txt").write_text(failure,encoding="utf-8");atomic(folder/"phase-a-failure.json",{"status":"FAIL"})
    finally:
        phase("cleanup");cleanup(folder,guard);phase("implementation_offline")
    path=folder/"phase-a-result.json";print(path.read_text(encoding="utf-8")[:180] if path.exists() else "FAIL; see phase-a-root09/failure.txt")

if __name__=="__main__":main()
