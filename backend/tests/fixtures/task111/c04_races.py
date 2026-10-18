"""仅补未验证的记忆与cancel真实缓存竞态。"""
from .c03_matrix import *
from .control import registry_root
async def races(resource,built,folder):
    h=Harness(resource,built,folder,registry_dir=registry_root().resolve());results=[]
    try:
        await h.controller.recover();assert not h.controller.blocked
        for kind in ("memory","cancel"):
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
                    await service.submit_command(MemoryCommandInput(business_key=str(uuid4()),memory_id=mid,expected_revision=0,action="save",body={"kind":"self_report","title":"C04 合成记忆","text":"按机械能公式核对参数"}))
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
                await service.submit_command(MemoryCommandInput(business_key=str(uuid4()),memory_id=mid,expected_revision=view["revision"],action="revise",body={"kind":"self_report","title":"C04 新记忆版本","text":"改为核对另一条合成约束","base_body_sha256":view["body_sha256"],"impact_token":impact["impact_token"]}))
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
