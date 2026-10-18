"""第一组合真实批：真实PG/镜像/Windows OneCall/远端交互和停止，统一回收。"""
from __future__ import annotations
import asyncio
from datetime import datetime,timedelta,timezone
import io
import json
import os
from pathlib import Path
import secrets
import sys
import time
from uuid import uuid4
import psycopg
from psycopg.rows import dict_row
from pydantic import SecretStr
from .control import ROOT,EVIDENCE,PERMIT,batch,reserve,event,atomic,source_snapshot
from . import resources


def install_environment():
    if os.environ.get("RETROLUME_TASK111_FIXTURE")!=PERMIT:raise RuntimeError("exact synthetic permit missing")
    from .runtime import install
    install()


class Harness:
    def __init__(self,resource,built,folder):
        from app.activities.repository import PostgresAdmissionLedger
        from app.materials.repository import PostgresMaterials
        from app.storage.originals import OriginalStore
        from app.capabilities.contracts import ModelServiceConfig
        from app.service_config import ActivityConfig,LayerState
        from app.preview.host_policy import HostPolicy
        from app.preview.production_supervisor import PreviewController
        self.resource,self.folder=resource,folder
        self.ledger=PostgresAdmissionLedger(resource["app"]);self.materials=PostgresMaterials(resource["app"])
        self.data=EVIDENCE/"synthetic/data";self.data.mkdir(parents=True,exist_ok=True)
        (self.data/"originals").mkdir(exist_ok=True);self.originals=OriginalStore(self.data/"originals")
        self.policy=HostPolicy(image_id=built["image"]["id"],load_manifest_sha256=built["load_manifest_sha256"],renderer_sha256=built["renderer_sha256"],
          kernel_release=resource["platform"]["kernel"],docker=resources.DOCKER,registry_dir=(EVIDENCE/"synthetic/control").resolve(),authorization=PERMIT,
          owner_name="Local\\RetroLumePreviewV2Task111")
        def name(pid,generation):
            count=reserve("preview_creates",{"preview_id":pid});return "retrolume-task-111-g11-preview-"+str(count).zfill(2)
        def observer(kind,data):
            if kind=="start_attempt":reserve("preview_starts",data)
            event("preview_"+kind,data)
        self.controller=PreviewController(self.ledger,self.policy,name_supplier=name,event_sink=observer)
        self.config=ActivityConfig(provider="deepseek_chat_completions",model="task111-synthetic",quota_preview=None,
          model_service=ModelServiceConfig(provider="deepseek_chat_completions",base_url="https://api.deepseek.com",model="task111-synthetic",
          api_key=SecretStr(secrets.token_urlsafe(32)),timeout_seconds=1.0,max_request_bytes=65536,max_response_bytes=65536,max_output_tokens_limit=4096),
          create_layer=LayerState(True),continue_layer=LayerState(True),html_generation_layer=LayerState(True),html_output_tokens=4096)

    async def parent(self,kind):
        from app.activities import ActivitySpec,SourceSnapshot
        from app.capabilities.contracts import AdmissionIntent,CallContext,Provider,LedgerOutcome,LedgerDisposition,build_business_payload
        from app.learning.contracts import LearningProfile,request_fingerprint,normalize_result,parse_output
        from app.learning.evidence import validate_snapshot,load_units,assemble_catalog
        text="机械能的合成材料。E=mgh，g=9.8，m和h范围0到10。m=2,h=3得到58.8 J，零因子为0。" if kind=="energy" else "二项概率的合成材料。P(X=k)=C(n,k)p^k(1-p)^(n-k)，n整数1到5，k在0到n，p在0到1。n3,k2,p0.5为0.375。"
        original=self.originals.put(io.BytesIO(text.encode("utf-8")),max_bytes=5242880)
        material=self.materials.save(source_id=None,expected_version=None,filename=kind+".md",format="md",sha256=original.sha256,size=original.size)
        aid=str(uuid4());await self.ledger.create_activity(ActivitySpec(activity_id=aid,sources=(SourceSnapshot(material["id"],material["version_id"],material["revision"]),),
          deadline_at=datetime.now(timezone.utc)+timedelta(hours=3),max_requests=8,max_cost_microunits=10000,reserve_cost_microunits=100,
          max_request_bytes=65536,max_output_tokens=4096,max_running_seconds=1800,allowed_models=(("deepseek_chat_completions","task111-synthetic"),),max_tool_calls=0))
        snapshot=await self.ledger.read_learning_snapshot(aid);sources=validate_snapshot(snapshot)
        identity={"action":"first","activity_id":aid,"goal":text,"question":None,"scope_revision":snapshot["scope_revision"],
         "sources":[s.model_dump() for s in sources],"parent_operation_id":None,"parent_payload_sha256":None,"max_output_tokens":256}
        fingerprint=request_fingerprint(**identity);catalog=assemble_catalog("机械能" if kind=="energy" else "二项概率",load_units(snapshot,self.materials,self.originals),fingerprint)
        profile=LearningProfile(**identity,request_sha256=fingerprint,catalog=catalog,history=None)
        output=parse_output(json.dumps({"kind":"answer","message":"冻结合成父事实；不是新的真实provider验证。","segments":[{"text":text,"citations":[catalog[0].citation_id]}],"questions":[]},ensure_ascii=False))
        stored=normalize_result(profile,output);opid="learn-first-v1."+fingerprint
        lease=await self.ledger.claim_lease(aid,"fixture-parent",lease_seconds=20,window_seconds=30)
        assert lease is not None
        permit=await self.ledger.admit(AdmissionIntent(context=CallContext(activity_id=aid,operation_id=opid,executor_id="fixture-parent",execution_generation=lease.execution_generation,scope_revision=lease.scope_revision),
          provider=Provider.DEEPSEEK_CHAT_COMPLETIONS,configured_model="task111-synthetic",request_bytes=100,max_output_tokens=256,tool_names=()))
        await self.ledger.mark_dispatch_started(permit);fmt,body,bodysha=build_business_payload(json_object=stored)
        await self.ledger.record_outcome(permit,LedgerOutcome(disposition=LedgerDisposition.RECEIVED,payload_format=fmt,payload=body,payload_sha256=bodysha,
                                                           remote_request_id="task111-fixture-parent",returned_model="task111-synthetic",finish_reason="stop",prompt_tokens=0,completion_tokens=0,response_bytes=len(body.encode())))
        await self.ledger.begin_window_close(aid,"fixture-parent",lease.execution_generation)
        await self.ledger.settle_execution_window(aid,"fixture-parent",lease.execution_generation,window_seconds=30,elapsed_seconds=0)
        event("seed_parent",{"activity_id":aid,"operation_id":opid,"payload_sha256":bodysha,"material":material,"classification":"synthetic baseline fixture; not provider or native SUP proof"})
        return aid,{"kind":"learning","operation_id":opid,"payload_sha256":bodysha,"segment_index":0}

    async def generate(self,aid,parent,focus):
        from app.preview.business_contracts import HtmlCommand
        from app.preview.generation import HtmlGenerationService
        command=HtmlCommand.model_validate({"business_key":str(uuid4()),"parent":parent,"focus":focus,"expected_config_sha256":self.controller.config_sha256,"confirmed":True})
        result=await HtmlGenerationService(self.ledger,self.controller).generate(aid,command,self.config,run_tag="task111-"+secrets.token_hex(12))
        event("generation",{"aid":aid,"command":command.model_dump(),"result":result});return result,command

    async def preview(self,aid,artifact_id,events,expected):
        from app.preview.business_contracts import OpenPreview,PreviewInput
        from app.preview.description import digest
        artifact=await self.ledger.read_html_artifact(aid,artifact_id);owner=secrets.token_hex(32)
        command=OpenPreview(start_key=str(uuid4()),expected_artifact_sha256=artifact["artifact_sha256"],input_owner_key=owner,confirmed=True)
        opened=await self.controller.open(aid,artifact_id,command);pid=opened["preview_id"];until=time.monotonic()+8
        while True:
            value=await self.controller.status(aid,pid)
            if value["state"]=="ready":break
            if value["state"] in ("cleanup_unconfirmed","failed_unstarted","stopped") or time.monotonic()>until:raise AssertionError("normal preview did not become ready: "+value["state"])
            await asyncio.sleep(.1)
        observations=[]
        for sequence,(action,oracle) in enumerate(zip(events,expected),1):
            reserve("internal_inputs",{"case":"normal","seq":sequence})
            response=await self.controller.input(aid,pid,PreviewInput.model_validate({"preview_generation":value["generation"],"seq":sequence,"payload_sha256":digest(action),"event":action}),owner)
            if oracle is None:assert response["accepted"] is False,response
            else:
                assert response["accepted"] is True,response
                assert abs(float(response["readouts"][0]["value"])-oracle)<=1e-9,(response,oracle)
            packet=await self.controller.frame(aid,pid,value["generation"],0,owner)
            if packet is not None:(self.folder/("normal-"+pid+"-"+str(sequence)+".png")).write_bytes(packet[1])
            observations.append({"event":action,"expected":oracle,"ack":response});await asyncio.sleep(2)
        await self.controller.stop(aid,pid,value["generation"])
        until=time.monotonic()+15
        while True:
            result=await self.controller.status(aid,pid)
            if result["state"] in ("stopped","cleanup_unconfirmed"):break
            if time.monotonic()>until:raise AssertionError("normal stop timeout")
            await asyncio.sleep(.1)
        assert result["state"]=="stopped",result
        atomic(self.folder/("interaction-"+pid+".json"),{"events":observations,"final":result})
        return result


async def verify(resource,built,folder):
    from app.preview.description import digest
    h=Harness(resource,built,folder)
    try:
        aid,parent=await h.parent("energy");energy_result,energy_command=await h.generate(aid,parent,"机械能计算与柱形图")
        assert energy_result["terminal_disposition"]=="succeeded",energy_result
        second,parent2=await h.parent("binomial");probability_result,_=await h.generate(second,parent2,"二项概率与分布图")
        assert probability_result["terminal_disposition"]=="succeeded",probability_result
        invalid,_=await h.generate(aid,parent,"INVALID 机械能输出含非法HTML")
        assert invalid["terminal_disposition"]=="invalid_output" and invalid["artifact_id"] is None,invalid
        unknown,_=await h.generate(second,parent2,"UNKNOWN 二项概率传输失联")
        assert unknown["terminal_disposition"]=="unknown" and unknown["artifact_id"] is None,unknown
        same=await h.ledger.read_html_command(aid,energy_command.business_key);assert same["artifact_id"]==energy_result["artifact_id"]
        action=lambda control,value:{"type":"set_number","control_id":"hctl_"+control,"value":value}
        await h.preview(aid,energy_result["artifact_id"],[action("h","3"),action("h","0"),action("m","0"),action("h","3")],[58.8,0,0,0])
        await h.preview(second,probability_result["artifact_id"],[action("p","0.5"),action("k","0"),action("p","0"),action("p","1"),action("k","3"),action("k","2")],[.375,.125,1,0,1,0])
        with psycopg.connect(resource["app"],row_factory=dict_row) as conn:
            joined=conn.execute("""SELECT c.status,c.terminal_disposition,a.artifact_id::text,o.state,r.payload_sha256,a.body_sha256 FROM html_commands c
                JOIN activity_operations o ON o.activity_id=c.activity_id AND o.operation_id=c.operation_id
                LEFT JOIN html_artifacts a ON a.activity_id=c.activity_id AND a.business_key=c.business_key
                LEFT JOIN activity_operation_results r ON r.activity_id=c.activity_id AND r.operation_id=c.operation_id ORDER BY c.created_at""").fetchall()
            atomic(folder/"commits.json",[dict(row) for row in joined])
        atomic(folder/"baseline.json",{"energy":energy_result,"probability":probability_result,"invalid":invalid,"unknown":unknown,"normal_remote":True,"complete_g11":False})
    finally:await h.controller.close()


def main():
    install_environment();folder=EVIDENCE/"real-01";folder.mkdir(exist_ok=True);resource=None
    with batch("real","v2-PG-image-native-normal-stop",3600):
        source_snapshot(folder)
        try:
            resource=resources.pg_start(folder);resources.migrate_baseline(resource,folder)
            built=resources.build_renderer(folder)
            from app.runtime import psycopg_compatible_loop_factory
            with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:
                runner.run(resources.install_html(resource,folder));(folder/"bound").mkdir(exist_ok=True);source_snapshot(folder/"bound")
                runner.run(verify(resource,built,folder))
        finally:
            if resource is not None:resources.stop_pg(folder)


if __name__=="__main__":main()
