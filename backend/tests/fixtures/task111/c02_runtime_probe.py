"""固定有限合成前提的真实启动诊断；不冒最后Native/UI全链成功。"""
import asyncio,json,secrets,time
from uuid import uuid4
from .control import CONTINUE_ROOT,atomic
from .resources import build_renderer
from .core import Harness
from .c01_seeds import diagnostic_artifact
from app.preview.business_contracts import OpenPreview,PreviewInput
from app.preview.description import digest
from app.runtime import psycopg_compatible_loop_factory


def verify(resource,folder):
    built=build_renderer(folder);atomic(CONTINUE_ROOT/"active-build.json",built)
    async def run():
        h=Harness(resource,built,folder);heartbeat=None;closed=False
        try:
            await h.controller.recover()
            if h.controller.blocked:raise RuntimeError("runtime probe recovery unknown")
            item=await diagnostic_artifact(h,"energy");atomic(folder/"diagnostic-prerequisite.json",item)
            artifact=await h.ledger.read_html_artifact(item["activity_id"],item["receipt"]["artifact_id"]);owner=secrets.token_hex(32)
            opened=await h.controller.open(item["activity_id"],artifact["artifact_id"],OpenPreview(start_key=str(uuid4()),expected_artifact_sha256=artifact["artifact_sha256"],input_owner_key=owner,confirmed=True))
            pid=opened["preview_id"]
            async def keep():
                while not closed:
                    await h.controller.status(item["activity_id"],pid,owner);await asyncio.sleep(.2)
            heartbeat=asyncio.create_task(keep());until=time.monotonic()+8;last=opened
            while time.monotonic()<until:
                last=await h.controller.status(item["activity_id"],pid,owner)
                if last["state"]=="ready":break
                if last["state"] in ("stopped","cleanup_unconfirmed","failed_unstarted"):break
                await asyncio.sleep(.05)
            atomic(folder/"runtime-ready-observation.json",last)
            if last["state"]!="ready":raise RuntimeError("runtime did not ready: "+last["state"])
            results=[]
            for seq,(control,value,expected) in enumerate((("h","3",58.8),("h","0",0),("m","0",0)),1):
                event={"type":"set_number","control_id":"hctl_"+control,"value":value}
                body=await h.controller.input(item["activity_id"],pid,PreviewInput(preview_generation=last["generation"],seq=seq,payload_sha256=digest(event),event=event),owner)
                if body.get("accepted") is not True or abs(float(body["readouts"][0]["value"])-expected)>1e-9:raise RuntimeError("remote oracle")
                packet=await h.controller.frame(item["activity_id"],pid,last["generation"],0,owner)
                if packet is not None:(folder/("remote-"+str(seq)+".png")).write_bytes(packet[1])
                results.append({"expected":expected,"ack":body});atomic(folder/"remote-results.json",results)
            await h.controller.stop(item["activity_id"],pid,last["generation"])
            until=time.monotonic()+15
            while time.monotonic()<until:
                last=await h.controller.status(item["activity_id"],pid,owner)
                if last["state"] in ("stopped","cleanup_unconfirmed"):break
                await asyncio.sleep(.1)
            atomic(folder/"runtime-probe-result.json",{"status":"PASS_RUNTIME_CORE_ONLY" if last["state"]=="stopped" else "FAIL","final":last,"main_UI_or_Native_parent_chain":False})
            if last["state"]!="stopped":raise RuntimeError("runtime stop unknown")
        finally:
            closed=True
            if heartbeat:heartbeat.cancel();await asyncio.gather(heartbeat,return_exceptions=True)
            await h.controller.close()
    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(run())
