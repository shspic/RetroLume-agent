"""保留式当前父与故障前提。前提走真实producer；不冒原生模型发送事实。"""
from dataclasses import replace
from datetime import datetime,timezone
import io,json
from uuid import uuid4
from .control import atomic,event
from .core import Harness


async def teaching_parent(h,kind,feedback=False):
    from app.activities import ActivitySpec,SourceSnapshot
    from app.learning.teaching_contracts import TeachingCommandInput,TeachingCallBinding,stored_teaching_result,parse_teaching_output
    from app.learning.teaching_service import TeachingService
    from app.service_config import LayerState
    from app.capabilities.contracts import AdmissionIntent,CallContext,Provider,LedgerOutcome,LedgerDisposition,build_business_payload,Message
    from app.learning.contracts import canonical
    title="机械能" if kind=="energy" else "二项概率"
    source="机械能合成资料：E=mgh，g=9.8，m和h均为0到10。m=2,h=3为58.8J，零因子为0。" if kind=="energy" else "二项概率合成资料：P(X=k)=C(n,k)p^k(1-p)^(n-k)，n为0到20整数，k为0到n整数，p为0到1。n3,k2,p0.5为0.375；n0/k0概率1，n20最多21柱。"
    original=h.originals.put(io.BytesIO(source.encode()),max_bytes=5242880)
    material=h.materials.save(source_id=None,expected_version=None,filename="c01-"+kind+".md",format="md",sha256=original.sha256,size=original.size)
    aid=str(uuid4());await h.ledger.create_activity(ActivitySpec(activity_id=aid,sources=(SourceSnapshot(material["id"],material["version_id"],material["revision"]),),
        deadline_at=datetime(2026,10,10,14,35,tzinfo=timezone.utc),max_requests=8,max_cost_microunits=10000,reserve_cost_microunits=100,
        max_request_bytes=65536,max_output_tokens=4096,max_running_seconds=1800,allowed_models=(("deepseek_chat_completions","task111-synthetic"),),max_tool_calls=0))
    config=replace(h.config,teaching_layer=LayerState(True),teaching_output_tokens=2048)
    service=TeachingService(h.ledger,h.materials,h.originals)
    async def command(action,body):
        head=await h.ledger.read_teaching_head(aid)
        return TeachingCommandInput(business_key=str(uuid4()),expected_revision=0 if head is None else head["revision"],expected_goal_version=0 if head is None else head["goal_version"],expected_scope_revision=1,action=action,body=body)
    await h.ledger.apply_teaching_local(aid,await command("goal",{"goal":title,"self_report":None,"domain":None,"seed_operation_id":None,"seed_payload_sha256":None}))
    async def record(action,body):
        cmd=await command(action,body);frozen,identity=await service._freeze_model_context(aid,cmd,config);profile=service._build_profile(aid,cmd,frozen,identity)
        cid=frozen.catalog[0].citation_id
        if action=="plan":output={"result_type":"path","message":"冻结合成教学前提","nodes":[{"title":title,"objective":"解释公式和边界","prerequisites":[],"rationale":"按本卡合成资料核对参数与结果","citations":[cid],"completion_dimensions":[{"dimension":"value","required_point":"数值与定义域一致"}]}]}
        elif action=="exercise":output={"result_type":"exercise","message":"冻结当前练习","exercise_type":"calculation","difficulty":2,"stem":"质量2，高度3，计算机械能。" if kind=="energy" else "二项概率：n3 k2 p0.5。",
            "reference_points":[{"point_id":"p1","text":"58.8J" if kind=="energy" else "0.375，n0概率1","citations":[cid],"numeric":None}],
            "reference_explanation":"按资料公式核对，不宣长期掌握","dimensions":[{"id":"value","point_ids":["p1"],"description":"核对数值与边界"}],"hint":"先列参数和定义域",
            "variant":{"purpose":"initial","parent_exercise_record_id":None,"parent_feedback_record_id":None,"instance_data":{"kind":"calculation","quantities":[{"name":"n" if kind=="binomial" else "m","value_decimal":"3" if kind=="binomial" else "2","unit":"次" if kind=="binomial" else "kg"}]}}}
        else:output={"result_type":"feedback","message":"二项概率的合成反馈，n0..20有限边界","correct_parts":[{"answer_excerpt":"0.375","explanation":"n3/k2/p0.5符合资料","point_ids":["p1"],"citations":[cid]}],"errors":[],"evidence_gaps":[],"cause_hypotheses":[],
            "dimension_observations":[{"id":"value","observation":"met","reason":"仅本次冻结合成观察","point_ids":["p1"]}],"next_focus":{"focus_dimension":"value","reason":"再核端点，不推长期能力","suggested_mode":"retest"}}
        normalized=parse_teaching_output(canonical(output),action);stored=stored_teaching_result(profile,normalized,[Message.model_validate(m) for m in frozen.messages])
        receipt=await h.ledger.accept_teaching_command(aid,cmd,frozen);assert receipt.status=="accepted"
        decision=await h.ledger.claim_teaching_launch(aid,cmd.business_key,receipt.request_sha256);assert decision["launch_allowed"]
        lease=await h.ledger.claim_lease(aid,"task111-c01-parent-seed",lease_seconds=20,window_seconds=30);assert lease
        binding=TeachingCallBinding(command_key=cmd.business_key,request_sha256=profile.request_sha256,context_sha256=profile.context_sha256,expected_revision=profile.expected_revision,goal_version=profile.goal_version)
        permit=await h.ledger.admit(AdmissionIntent(context=CallContext(activity_id=aid,operation_id=cmd.operation_id(aid),executor_id="task111-c01-parent-seed",execution_generation=lease.execution_generation,scope_revision=lease.scope_revision),
             provider=Provider.DEEPSEEK_CHAT_COMPLETIONS,configured_model="task111-synthetic",request_bytes=100,max_output_tokens=2048,tool_names=(),teaching_binding=binding))
        await h.ledger.mark_dispatch_started(permit);fmt,payload,sha=build_business_payload(json_object=stored)
        await h.ledger.record_outcome(permit,LedgerOutcome(disposition=LedgerDisposition.RECEIVED,payload_format=fmt,payload=payload,payload_sha256=sha,
            remote_request_id="task111-c01-synthetic-parent-seed",returned_model="task111-synthetic",finish_reason="stop",prompt_tokens=0,completion_tokens=0,response_bytes=len(payload.encode())))
        await h.ledger.begin_window_close(aid,"task111-c01-parent-seed",lease.execution_generation)
        await h.ledger.settle_execution_window(aid,"task111-c01-parent-seed",lease.execution_generation,window_seconds=30,elapsed_seconds=0)
        view=await h.ledger.read_teaching_command(aid,cmd.business_key);assert view["command"]["status"]=="committed"
        rows=view["records"];row=next(r for r in rows if r["kind"]==("path_proposal" if action=="plan" else "exercise" if action=="exercise" else "feedback"))
        event("c01_parent_seed",{"aid":aid,"action":action,"record_id":str(row["record_id"]),"classification":"synthetic prerequisite through real ledger, no transport/SUP verdict"})
        return str(row["record_id"]),row["body_sha256"]
    proposal,_=await record("plan",{"confirmed":True,"correction_record_id":None,"retry_of":None})
    await h.ledger.apply_teaching_local(aid,await command("accept_path",{"proposal_record_id":proposal}))
    head=await h.ledger.read_teaching_head(aid)
    eid,sha=await record("exercise",{"confirmed":True,"path_record_id":str(head["path_record_id"]),"node_id":"n1","purpose":"initial","parent_feedback_record_id":None,"retry_of":None})
    if feedback:
        answer=await h.ledger.apply_teaching_local(aid,await command("answer",{"exercise_record_id":eid,"kind":"initial","text":"0.375","supersedes_answer_record_id":None}))
        aid_record=answer.record_ids[0].record_id
        eid,sha=await record("evaluate",{"confirmed":True,"exercise_record_id":eid,"answer_record_id":aid_record,"retry_of":None})
    return aid,{"kind":"teaching","record_id":eid,"body_sha256":sha,"point_id":None}


async def diagnostic_artifact(h,kind):
    """故障前提经真实v2准入/同COMMIT producer保存；零transport，不称模型/SUP证据。"""
    import secrets
    from .samples import energy,binomial
    from app.preview.business_contracts import HtmlCommand,HtmlProfile,HtmlCallBinding
    from app.preview.compiler import runtime_identity
    from app.preview.model_policy import stored_result
    from app.preview.description import canonical,load_json
    from app.capabilities.contracts import AdmissionIntent,CallContext,Provider,LedgerOutcome,LedgerDisposition,build_business_payload
    aid,parent=await h.parent(kind)
    command=HtmlCommand(business_key=str(uuid4()),parent=parent,focus="冻结故障前提 "+kind,expected_config_sha256=h.controller.config_sha256,confirmed=True)
    row=await h.ledger.accept_html_command(aid,command,runtime_identity()["renderer_sha256"],h.controller.config_sha256)
    profile=HtmlProfile(activity_id=aid,business_key=command.business_key,request_sha256=row["request_sha256"],context_sha256=row["context_sha256"],context_json=row["context_body"],renderer_sha256=row["renderer_sha256"],max_output_tokens=4096)
    assert await h.ledger.claim_html_command(aid,command.business_key)
    context=load_json(profile.context_json);citation=context["catalog"][0]["citation_id"]
    descriptor=binomial(citation) if kind=="binomial" else energy(citation)
    stored=stored_result(canonical(descriptor),profile);fmt,payload,sha=build_business_payload(json_object=stored)
    lease=await h.ledger.claim_lease(aid,"task111-c01-diag-seed",lease_seconds=20,window_seconds=30);assert lease
    binding=HtmlCallBinding(business_key=profile.business_key,request_sha256=profile.request_sha256,context_sha256=profile.context_sha256,renderer_sha256=profile.renderer_sha256)
    permit=await h.ledger.admit(AdmissionIntent(context=CallContext(activity_id=aid,operation_id=row["operation_id"],executor_id="task111-c01-diag-seed",execution_generation=lease.execution_generation,scope_revision=lease.scope_revision),provider=Provider.DEEPSEEK_CHAT_COMPLETIONS,configured_model="task111-synthetic",request_bytes=100,max_output_tokens=4096,tool_names=(),html_binding=binding))
    await h.ledger.mark_dispatch_started(permit)
    await h.ledger.record_outcome(permit,LedgerOutcome(disposition=LedgerDisposition.RECEIVED,payload_format=fmt,payload=payload,payload_sha256=sha,remote_request_id="synthetic-diagnostic-baseline-no-transport",returned_model="task111-synthetic",finish_reason="stop",prompt_tokens=0,completion_tokens=0,response_bytes=len(payload.encode())))
    await h.ledger.begin_window_close(aid,"task111-c01-diag-seed",lease.execution_generation)
    await h.ledger.settle_execution_window(aid,"task111-c01-diag-seed",lease.execution_generation,window_seconds=30,elapsed_seconds=0)
    receipt=await h.ledger.read_html_command(aid,command.business_key);assert receipt["artifact_id"]
    event("c01_diagnostic_artifact_seed",{"activity_id":aid,"artifact_id":receipt["artifact_id"],"classification":"real PG producer synthetic fixture prerequisite; not a transport/OneCall sample; no model quality claim"})
    return {"activity_id":aid,"parent":parent,"receipt":receipt,"command":command.model_dump()}
