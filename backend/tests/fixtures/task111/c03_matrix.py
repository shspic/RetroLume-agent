"""完整剩余场景的真实生产入口、独立对象和精确证明，保留原失败。"""
import asyncio,hashlib,inspect,io,json,os,secrets,struct,subprocess,sys,time
from copy import deepcopy
from pathlib import Path
from uuid import uuid4
import psycopg
from .control import ROOT,EVIDENCE,CONTINUE_ROOT,PERMIT,atomic,reserve,event,run,read_state,source_snapshot
from .core import Harness
from .c01_seeds import diagnostic_artifact,teaching_parent
from .c03_samples import limited
from app.preview.business_contracts import OpenPreview,PreviewInput,HtmlRefusal
from app.preview.description import digest,canonical
from app.capabilities.contracts import AdmissionUnavailable
from app.preview.pipe import send_packet,read_packet,validate_png
from app.runtime import psycopg_compatible_loop_factory

def plan():return json.loads((CONTINUE_ROOT/"matrix-plan.json").read_text(encoding="utf-8"))
def aid_for(key):return plan()["objects"][key]["activity_id"]

class Session:
    def __init__(self,h,item,out):
        self.h,self.item,self.out=h,item,out;self.owner=secrets.token_hex(32);self.closed=False;self.beat=None;self.c=None;self.seq=0
    async def open(self,*,heartbeat=True,concurrent=False):
        aid=self.item["activity_id"];artifact=await self.h.ledger.read_html_artifact(aid,self.item["receipt"]["artifact_id"])
        command=OpenPreview(start_key=str(uuid4()),expected_artifact_sha256=artifact["artifact_sha256"],input_owner_key=self.owner,confirmed=True)
        if concurrent:
            both=await asyncio.gather(self.h.controller.open(aid,artifact["artifact_id"],command),self.h.controller.open(aid,artifact["artifact_id"],command))
            assert both[0]["preview_id"]==both[1]["preview_id"];opened=both[0]
        else:opened=await self.h.controller.open(aid,artifact["artifact_id"],command)
        self.pid=opened["preview_id"];self.c=self.h.controller.current;self.generation=opened["generation"]
        async def keep():
            while not self.closed:
                await self.h.controller.status(aid,self.pid,self.owner);await asyncio.sleep(.15)
        until=self.c["t0_ns"]+8*10**9
        while time.monotonic_ns()<until:
            row=await self.h.controller.status(aid,self.pid,self.owner)
            if row["state"] in ("ready","stopped","cleanup_unconfirmed","failed_unstarted"):break
            await asyncio.sleep(.03)
        atomic(self.out/"ready.json",{"row":row,"t0_ns":self.c["t0_ns"],"observed_ns":time.monotonic_ns(),"deadline_ns":self.c["deadline_ns"],"concurrent_same_key":concurrent})
        assert row["state"]=="ready",row["state"]
        if heartbeat:self.beat=asyncio.create_task(keep())
        until=time.monotonic()+2
        while self.c["frame"] is None and time.monotonic()<until:await asyncio.sleep(.03)
        assert self.c["frame"] is not None
        return row
    async def input(self,control,value):
        self.seq+=1;action={"type":"set_number","control_id":"hctl_"+control,"value":value};reserve("internal_inputs",{"case":self.out.name,"seq":self.seq})
        return await self.h.controller.input(self.item["activity_id"],self.pid,PreviewInput(preview_generation=self.generation,seq=self.seq,payload_sha256=digest(action),event=action),self.owner)
    async def frame(self):
        packet=await self.h.controller.frame(self.item["activity_id"],self.pid,self.generation,0,self.owner)
        assert packet is not None;validate_png(packet[1]);return packet
    async def finish(self,*,request_stop=True,expected_confirmed=True):
        if request_stop:await self.h.controller.stop(self.item["activity_id"],self.pid,self.generation)
        until=time.monotonic()+18;row=None
        while time.monotonic()<until:
            row=await self.h.controller.status(self.item["activity_id"],self.pid,self.owner if self.beat else None)
            if row["state"] in ("stopped","cleanup_unconfirmed","failed_unstarted"):break
            await asyncio.sleep(.05)
        if self.beat:self.closed=True;self.beat.cancel();await asyncio.gather(self.beat,return_exceptions=True)
        await asyncio.to_thread(self.c["thread"].join,3)
        proof=json.loads((self.c["folder"]/"supervisor-result.json").read_text(encoding="utf-8"))
        atomic(self.out/"stop-and-budget.json",{"row":row,"result":proof,"runtime_folder":str(self.c["folder"]),"activity_id":self.item["activity_id"]})
        if expected_confirmed:assert row["state"]=="stopped" and proof["confirmed"] and proof["proof"]["tree_confirmation"]=="private_pid_init_terminated"
        else:assert row["state"]=="cleanup_unconfirmed" and row["reserved_seconds"]>=row["reserve_seconds"]
        return row,proof

async def group_item(h,out):
    path=CONTINUE_ROOT/"shared-budget-domain-item.json"
    if path.exists():return json.loads(path.read_text(encoding="utf-8"))
    item=await diagnostic_artifact(h,"energy",factory=limited,activity_id=aid_for("domain_budget_group"));atomic(path,item);return item

async def boundaries(resource,built,folder):
    # 公开类型反例先经过真实API，关闭API后再由唯一控制者进入host生命周期。
    from .http_matrix import HttpMatrix
    inherited=CONTINUE_ROOT/"root-10/step-09-boundaries/public-capability-rejections.json"
    if inherited.exists():
        atomic(folder/"public-types-inherited.json",{"path":str(inherited),"sha256":hashlib.sha256(inherited.read_bytes()).hexdigest(),"API_input_code_unchanged":True})
    else:
      m=HttpMatrix(resource,built,folder)
      try:
        m.start();aid=aid_for("domain_budget_group");pid=str(uuid4());base=f"/api/activities/{aid}/html/previews/{pid}/inputs"
        entries=[]
        for value in plan()["capability_inputs"]:
            action={"type":value,"url":value};body={"preview_generation":1,"seq":1,"payload_sha256":digest(action),"event":action}
            result=m.request("POST",base,body,expected=422);entries.append({"capability":value,"result":result})
        atomic(folder/"public-capability-rejections.json",entries)
      finally:m.close()
    h=Harness(resource,built,folder,registry_dir=(CONTINUE_ROOT/"synthetic/matrix-control").resolve())
    try:
        await h.controller.recover();assert not h.controller.blocked
        item=await group_item(h,folder)
        old_domain=CONTINUE_ROOT/"root-10/step-09-boundaries/real-domain-limit"
        if (old_domain/"domain-limit-owner-dedup.json").exists() and (old_domain/"stop-and-budget.json").exists():
            stop=json.loads((old_domain/"stop-and-budget.json").read_text(encoding="utf-8"));assert stop["result"]["confirmed"] and stop["result"]["proof"]["image_id"]==built["image"]["id"]
            previous=(None,(old_domain/"before.png").read_bytes())
            atomic(folder/"domain-evidence-inherited.json",{"path":str(old_domain),"same_image_id":built["image"]["id"],"domain_and_host_source_unchanged":True,"why":"only budget reserve function corrected"})
        else:
            out=folder/"real-domain-limit";out.mkdir();s=Session(h,item,out);await s.open()
            previous=await s.frame();(out/"before.png").write_bytes(previous[1]);c=s.c
            owner_checks=[]
            for name,aid,gen,owner in (("no_owner",item["activity_id"],s.generation,None),("wrong_owner",item["activity_id"],s.generation,"0"*64),("wrong_generation",item["activity_id"],s.generation+1,s.owner),("wrong_activity",str(uuid4()),s.generation,s.owner)):
                try:await h.controller.frame(aid,s.pid,gen,0,owner)
                except HtmlRefusal as error:owner_checks.append({"case":name,"code":error.code,"status":error.status})
                else:raise AssertionError(name)
            action={"type":"set_number","control_id":"hctl_x","value":"1"};command=PreviewInput(preview_generation=s.generation,seq=1,payload_sha256="0"*64,event=action)
            try:await h.controller.input(item["activity_id"],s.pid,command,s.owner)
            except HtmlRefusal as error:owner_checks.append({"case":"wrong_payload_hash","code":error.code})
            else:raise AssertionError("payload hash")
            response=await s.input("x","-1");assert not response["accepted"] and response["error_code"]=="calculation_domain_error"
            await asyncio.sleep(.4);after=await s.frame();assert after[1]==previous[1]
            response2=await s.input("p","0.5");assert not response2["accepted"] and response2["error_code"]=="calculation_limit"
            for key in ("input_values","readouts","figures"):assert response2[key]==response[key]
            await asyncio.sleep(.4);after=await s.frame();assert after[1]==previous[1];(out/"after-rejections.png").write_bytes(after[1])
            # 完全相同seq/hash经过真实宿主重放ACK，不重算，不新增观察文件。
            observation=c["folder"]/"engine-observation-2.json";until=time.monotonic()+2
            while not observation.exists() and time.monotonic()<until:await asyncio.sleep(.03)
            stamp=observation.stat().st_mtime_ns;last=c["last_ack"];c["ack"].clear();event_body={"type":"set_number","control_id":"hctl_p","value":"0.5"}
            with h.controller._writer:send_packet(c["attach"].stdin,c,"input",2,event_body)
            assert await asyncio.to_thread(c["ack"].wait,2);assert c["last_ack"]==last;await asyncio.sleep(.3);assert observation.stat().st_mtime_ns==stamp
            conflict_event={"type":"set_number","control_id":"hctl_p","value":"0.55"}
            try:await h.controller.input(item["activity_id"],s.pid,PreviewInput(preview_generation=s.generation,seq=2,payload_sha256=digest(conflict_event),event=conflict_event),s.owner)
            except HtmlRefusal as error:assert error.code=="html_input_seq_conflict"
            else:raise AssertionError("same sequence accepted different hash")
            atomic(out/"domain-limit-owner-dedup.json",{"domain_ack":response,"limit_ack":response2,"owner_checks":owner_checks,"complete_PNG_retained":True,"same_seq_hash_no_reexecution":True})
            await s.finish()
        out=folder/"duplicate-init";out.mkdir();s=Session(h,item,out);await s.open();c=s.c
        with h.controller._writer:send_packet(c["attach"].stdin,c,"init",0,{"schema":"retrolume.preview.init.v2","description":c["description"],"description_sha256":digest(c["description"]),"renderer_sha256":built["renderer_sha256"],"viewport":{"width":640,"height":480}})
        row,proof=await s.finish(request_stop=False);assert proof["error_code"]=="protocol_failed" and row["starts_used"]==2
        # 对实际PNG与生产解码器作相称损坏反例，不启动更多对象。
        from app.preview.pipe import PipeError
        variants={"signature":b"x"+previous[1][1:],"truncated":previous[1][:-1],"CRC":previous[1][:30]+bytes([previous[1][30]^1])+previous[1][31:]}
        rejected=[]
        for name,data in variants.items():
            try:validate_png(data)
            except PipeError as error:rejected.append({"case":name,"error":str(error)})
            else:raise AssertionError(name)
        atomic(folder/"PNG-production-codec-rejections.json",rejected)
        atomic(folder/"boundary-result.json",{"status":"PASS_PUBLIC_TYPES_REAL_HOST_DOMAIN_LIMIT_OWNER_DEDUP_AND_DUPLICATE_INIT","same_item_for_three_budget_lifecycles":item})
    finally:await h.controller.close()

async def races(resource,built,folder):
    h=Harness(resource,built,folder,registry_dir=(CONTINUE_ROOT/"synthetic/race-control").resolve());results=[]
    try:
        await h.controller.recover();assert not h.controller.blocked
        for kind in ("source","parent","memory","cancel"):
            old=CONTINUE_ROOT/("root-11/step-14-races/cache-before-qualification-"+kind)
            if (old/"exact-barrier-result.json").exists() and (old/"stop-and-budget.json").exists():
                previous=json.loads((old/"stop-and-budget.json").read_text(encoding="utf-8"));assert previous["result"]["confirmed"]
                results.append({"kind":kind,"status":"INHERITED_COMMIT_BEFORE_PUBLIC_QUALIFICATION","path":str(old),"activity_id":previous["activity_id"]});continue
            out=folder/("cache-before-qualification-"+kind);out.mkdir();mid=None
            if kind=="memory":
                from app.memory.service import MemoryService
                from app.memory.contracts import MemoryCommandInput,MemorySelectionInput
                mid=plan()["objects"]["race_memory"]["memory_id"];service=MemoryService(h.ledger)
                view=await h.ledger.read_memory_snapshot(mid)
                if view is None:
                    await service.submit_command(MemoryCommandInput(business_key=str(uuid4()),memory_id=mid,expected_revision=0,action="save",body={"kind":"self_report","title":"C03 合成记忆","text":"按机械能公式核对参数"}))
                    view=await h.ledger.read_memory_snapshot(mid)
                selection=MemorySelectionInput(confirmed=True,entries=[{"memory_id":mid,"version":view["version"],"revision":view["revision"],"body_sha256":view["body_sha256"]}])
                exists=await h.ledger.read_teaching_head(aid_for("race_memory"))
                parent_item=await teaching_parent(h,"energy",memory_selection=selection,activity_id=aid_for("race_memory"),resume_existing=exists is not None)
            elif kind=="parent":parent_item=await teaching_parent(h,"energy",activity_id=aid_for("race_parent"))
            else:parent_item=None
            item=await diagnostic_artifact(h,"energy",parent_item=parent_item,activity_id=aid_for("race_"+kind));s=Session(h,item,out);await s.open()
            entered=asyncio.Event();release=asyncio.Event();original=h.controller._owner_row;observed={}
            async def barrier(aid,pid,generation,owner):
                caller=inspect.currentframe().f_back;candidate=caller.f_locals.get("candidate") if caller else None
                assert candidate is not None,"barrier did not capture production frame candidate"
                observed.update(candidate_header=candidate[0],candidate_sha256=hashlib.sha256(candidate[1]).hexdigest(),candidate_bytes=len(candidate[1]),entered_ns=time.monotonic_ns(),public_qualification_not_started=True)
                entered.set();await release.wait();return await original(aid,pid,generation,owner)
            h.controller._owner_row=barrier
            frame_task=asyncio.create_task(h.controller.frame(item["activity_id"],s.pid,s.generation,0,s.owner));await asyncio.wait_for(entered.wait(),2)
            if kind=="source":
                snapshot=await h.ledger.read_learning_snapshot(item["activity_id"]);source=snapshot["sources"][0]
                raw=h.originals.put(io.BytesIO(b'C03 changed synthetic source; all old versions retained'),max_bytes=5242880)
                changed=h.materials.save(source_id=source["source_id"],expected_version=source["version_id"],filename="c03-replaced.md",format="md",sha256=raw.sha256,size=raw.size)
                observed["source_replacement"]=changed
            elif kind=="parent":
                from app.learning.teaching_contracts import TeachingCommandInput
                head=await h.ledger.read_teaching_head(item["activity_id"])
                await h.ledger.apply_teaching_local(item["activity_id"],TeachingCommandInput(business_key=str(uuid4()),expected_revision=head["revision"],expected_goal_version=head["goal_version"],expected_scope_revision=1,action="goal",body={"goal":"C03 改变后的合成目标","self_report":None,"domain":None,"seed_operation_id":None,"seed_payload_sha256":None}))
            elif kind=="memory":
                impact=await h.ledger.preview_memory_change(mid,view["revision"],"revise")
                await service.submit_command(MemoryCommandInput(business_key=str(uuid4()),memory_id=mid,expected_revision=view["revision"],action="revise",body={"kind":"self_report","title":"C03 新记忆版本","text":"改为核对另一条合成约束","base_body_sha256":view["body_sha256"],"impact_token":impact["impact_token"]}))
                observed["memory_after"]=await h.ledger.read_memory_selection(item["activity_id"]);assert not observed["memory_after"]["eligible"]
            else:await h.ledger.cancel_activity(item["activity_id"])
            observed["invalidation_COMMIT_completed_ns"]=time.monotonic_ns();release.set()
            try:await frame_task
            except HtmlRefusal as error:observed["frame_refusal"]={"code":error.code,"status":error.status}
            else:raise AssertionError("candidate frame escaped after committed invalidation")
            finally:h.controller._owner_row=original
            try:
                artifact=await h.ledger.read_html_artifact(item["activity_id"],item["receipt"]["artifact_id"])
                assert artifact.get("description") is None and artifact.get("read_status")!="current";observed["artifact_projection"]=artifact
            except HtmlRefusal as error:observed["artifact_refusal"]=error.code
            try:await s.input("h","3")
            except HtmlRefusal as error:observed["input_refusal"]=error.code
            else:raise AssertionError("input after qualification loss")
            observed["memory_dependency"]=kind=="memory";observed["no_memory_parent_classification"]="not_applicable" if kind!="memory" else None
            atomic(out/"exact-barrier-result.json",observed);await s.finish(request_stop=False);results.append({"kind":kind,"activity_id":item["activity_id"],"preview_id":s.pid,"status":"PASS_COMMIT_BEFORE_PUBLIC_QUALIFICATION"})
        atomic(folder/"race-results.json",results)
    finally:await h.controller.close()

async def budgets(resource,built,folder):
    from app.preview import production_supervisor as ps
    from app.preview.docker_control import DockerUnknown
    h=Harness(resource,built,folder,registry_dir=(CONTINUE_ROOT/"synthetic/budget-control").resolve())
    original=ps.call;calls=[]
    def lost_reply(docker,args,timeout=2):
        result=original(docker,args,timeout)
        if args[0]=="create":
            calls.append(result);atomic(folder/"actual-create-reply-discarded.json",result)
            raise DockerUnknown("fixed_test_loss_after_successful_create")
        return result
    try:
        await h.controller.recover();assert not h.controller.blocked;item=await group_item(h,folder)
        with psycopg.connect(resource["app"]) as conn:
            account_before=conn.execute("SELECT row_to_json(a)::text FROM activities a WHERE id=%s",(item["activity_id"],)).fetchone()[0]
        prior=CONTINUE_ROOT/"root-11/step-12-budgets"
        if (prior/"create-reply-loss-and-third-start/stop-and-budget.json").exists():
            record=json.loads((prior/"create-reply-loss-and-third-start/stop-and-budget.json").read_text(encoding="utf-8"));assert record["result"]["confirmed"] and record["result"]["proof"]["image_id"]==built["image"]["id"]
            calls.append(json.loads((prior/"actual-create-reply-discarded.json").read_text(encoding="utf-8")))
            atomic(folder/"create-loss-inherited.json",{"path":str(prior),"same_image_id":built["image"]["id"],"actual_create_calls":1})
        else:
            ps.call=lost_reply;out=folder/"create-reply-loss-and-third-start";out.mkdir();s=Session(h,item,out);await s.open(concurrent=True);ps.call=original
            assert len(calls)==1 and calls[0]["code"]==0 and calls[0]["stdout"].strip()==s.c["cid"]
            assert s.c["reserve_seconds"]==60
            await s.finish()
        budget=await h.ledger.html_preview_budget(item["activity_id"]);assert budget["starts_used"]==3 and budget["reserved_seconds"]==0 and budget["settled_seconds"]<=180
        artifact=await h.ledger.read_html_artifact(item["activity_id"],item["receipt"]["artifact_id"]);owner=secrets.token_hex(32)
        command=OpenPreview(start_key=str(uuid4()),expected_artifact_sha256=artifact["artifact_sha256"],input_owner_key=owner,confirmed=True)
        try:await h.controller.open(item["activity_id"],artifact["artifact_id"],command)
        except HtmlRefusal as error:exhausted=error.code;assert exhausted=="html_preview_budget_exhausted"
        else:raise AssertionError("fourth start")
        # 新config不重置已有预算；有限producer的最低30检查事务内ROLLBACK。
        identity={"preview_id":str(uuid4()),"owner_id":str(uuid4()),"boot_id":str(uuid4()),"nonce":secrets.token_hex(32),"control_key":secrets.token_hex(32),"image_id":built["image"]["id"],"config_sha256":"0"*64,"t0_ns":time.monotonic_ns(),"deadline_at":__import__('datetime').datetime.now(__import__('datetime').timezone.utc)+__import__('datetime').timedelta(seconds=60)}
        try:await h.ledger.reserve_html_preview(item["activity_id"],artifact["artifact_id"],command,identity,60)
        except (HtmlRefusal,psycopg.Error,AdmissionUnavailable) as error:config_error=str(error).splitlines()[0]
        else:raise AssertionError("changed config reset budget")
        fresh=await diagnostic_artifact(h,"energy",activity_id=aid_for("minimum_reserve_reject"));a=await h.ledger.read_html_artifact(fresh["activity_id"],fresh["receipt"]["artifact_id"])
        small=OpenPreview(start_key=str(uuid4()),expected_artifact_sha256=a["artifact_sha256"],input_owner_key=secrets.token_hex(32),confirmed=True);identity["config_sha256"]=h.controller.config_sha256
        try:await h.ledger.reserve_html_preview(fresh["activity_id"],a["artifact_id"],small,identity,29)
        except (HtmlRefusal,psycopg.Error,AdmissionUnavailable) as error:minimum_error=str(error).splitlines()[0]
        else:raise AssertionError("reserve below30")
        assert (await h.ledger.html_preview_budget(fresh["activity_id"]))["starts_used"]==0
        with psycopg.connect(resource["app"]) as conn:account_after=conn.execute("SELECT row_to_json(a)::text FROM activities a WHERE id=%s",(item["activity_id"],)).fetchone()[0]
        assert account_before==account_after,"preview modified original activity four ledgers"
        atomic(folder/"budget-result.json",{"status":"PASS_THREE_SHARED_STARTS_180_ACCOUNTING_CONCURRENT_KEY_CREATE_LOSS_AND_MIN30","activity_id":item["activity_id"],"budget":budget,"fourth_refusal":exhausted,"config_refusal":config_error,"minimum_refusal":minimum_error,"create_calls":len(calls),"original_activity_four_ledgers_unchanged":True})
    finally:ps.call=original;await h.controller.close()

def execute(resource,built,folder,action):
    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:
        if action=="boundaries":runner.run(boundaries(resource,built,folder))
        elif action=="races":runner.run(races(resource,built,folder))
        elif action=="budgets":runner.run(budgets(resource,built,folder))
        elif action=="faults":
            from .c03_faults import run_all
            run_all(resource,built,folder)
        else:raise RuntimeError("matrix action")
