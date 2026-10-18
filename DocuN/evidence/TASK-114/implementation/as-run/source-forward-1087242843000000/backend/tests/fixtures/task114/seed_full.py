"""本卡全域合成数据。只在新 source 已核身份后调用，不发 provider 请求。"""
from datetime import datetime,timedelta,timezone
import io
import json
import secrets
import time
from uuid import uuid4

from app.activities import ActivitySpec,SourceSnapshot
from app.capabilities.contracts import AdmissionIntent,CallContext,Provider,LedgerOutcome,LedgerDisposition,build_business_payload
from app.data_exit.contracts import canonical,digest
from app.data_exit.codec import plain
from app.data_exit.reference import PreparedReference
from app.memory.contracts import MemoryCommandInput,MemorySelectionInput
from app.interview.contracts import InterviewCommandInput
from app.pdf_import.contracts import PdfImportResult,PdfPage
from app.pdf_review.contracts import ReviewPage
from app.preview.compiler import runtime_identity,compile_description
from app.preview.business_contracts import HtmlCommand,HtmlCallBinding,OpenPreview,operation_id
from app.learning.contracts import LearningProfile,request_fingerprint,normalize_result,FIRST_PREFIX
from app.learning.evidence import validate_snapshot,load_units,assemble_catalog


async def seed(runtime):
    app=runtime.app;ledger=app.state.activities_ledger;materials=app.state.materials;store=app.state.originals
    sources=materials.list()
    source=next(row for row in sources if row['filename']=='当前资料.md')
    identities={'source':source}
    async def activity(selection=None):
        aid=str(uuid4())
        await ledger.create_activity(ActivitySpec(activity_id=aid,sources=(SourceSnapshot(source['id'],source['version_id'],source['revision']),),
            deadline_at=datetime.now(timezone.utc)+timedelta(hours=4),max_requests=16,max_cost_microunits=100000,reserve_cost_microunits=100,
            max_request_bytes=65536,max_output_tokens=2048,max_running_seconds=300,
            allowed_models=(('deepseek_chat_completions','task114-synthetic'),),allowed_tools=('finite_calculate',),max_tool_calls=4),memory_selection=selection)
        return aid

    # 有效普通 PDF 原件，三个候选各保原资格；不把直接夹具当原解析监督证明。
    from pypdf import PdfWriter
    writer=PdfWriter();writer.add_blank_page(width=100,height=100);writer.add_blank_page(width=100,height=100)
    stream=io.BytesIO();writer.write(stream);pdf=stream.getvalue()
    pdfs=[]
    for status in ('pending','confirmed','skipped'):
        with runtime.source.connection(readonly=True) as connection:
            found=connection.execute('SELECT c.id AS candidate_id,c.source_id,c.version_id,c.status,v.sha256,v.size FROM public.pdf_review_candidates c JOIN public.material_versions v ON v.id=c.version_id WHERE v.filename=%s',('合成-'+status+'.pdf',)).fetchall()
        if len(found)>1:raise RuntimeError('夹具候选重复，停止查因')
        if found:
            candidate=plain(found[0])
            prepared=PreparedReference(candidate['source_id'],candidate['version_id'],candidate['candidate_id'],candidate['sha256'],candidate['size'])
            from app.storage.originals import Original
            original=Original(candidate['sha256'],candidate['size'])
        else:
            prepared=runtime.references.prepare_reference(digest(pdf),len(pdf),pdf=True)
            with runtime.references.acquire_shared(prepared) as pin:
                original=store.put(io.BytesIO(pdf),max_bytes=5*1024**2,reference_pin=pin)
                candidate=materials.create_pdf_candidate(source_id=None,expected_version=None,expected_revision=0,
                    filename='合成-'+status+'.pdf',sha256=original.sha256,size=original.size,
                    extraction=PdfImportResult(2,(PdfPage(1,'',('no_text',)),PdfPage(2,'',('no_text',))),('no_text',)),
                    reference_pin=pin,prepared_ids=prepared)
        if status=='confirmed' and candidate['status']=='pending':
            with runtime.references.acquire_shared(prepared) as pin:
                materials.confirm_pdf_candidate(candidate_id=candidate['candidate_id'],version_id=candidate['version_id'],
                    pages=[ReviewPage(1,True,'用户明确补充第一页'),ReviewPage(2,True,'第二页独立补充')],reference_pin=pin)
        elif status=='skipped' and candidate['status']=='pending':materials.skip_pdf_candidate(candidate['candidate_id'])
        pdfs.append({'id':candidate['candidate_id'],'source_id':candidate['source_id'],'version_id':candidate['version_id'],'status':status,'sha256':original.sha256})
    identities['pdf']=pdfs

    # 一条合法 SQL 存储样本带资料依赖，声明为用户自报而非掌握结论。
    mid,key=str(uuid4()),str(uuid4())
    body=canonical({'schema':'memory.body.v1','kind':'self_report','uncertainty':'self_reported','title':'合成背景','text':'用户自报背景，不是正确性证明'})
    line='source|'+source['id']+'|'+source['version_id']+'|'+str(source['revision'])+'|'+source['sha256']
    with runtime.gate.acquire(),runtime.source.connection() as connection:
        connection.execute("INSERT INTO public.learning_memories(memory_id,revision,current_version,state) VALUES(%s,1,1,'active')",(mid,))
        connection.execute("INSERT INTO public.learning_memory_commands(business_key,action,memory_id,request_sha256,slot_sha256,effect_applied,before_revision,after_revision,after_version,result_meta) VALUES(%s,'save',%s,%s,%s,true,0,1,1,'{}')",(key,mid,digest(key),digest('slot'+key)))
        connection.execute("INSERT INTO public.learning_memory_revisions(memory_id,version,claim_kind,uncertainty,policy_version,body_sha256,body_bytes,dependencies_sha256,dependency_count,created_by_key) VALUES(%s,1,'self_report','self_reported','memory.user.v1',%s,%s,%s,1,%s)",(mid,digest(body),len(body.encode()),digest(line),key))
        connection.execute("INSERT INTO public.learning_memory_dependencies(memory_id,version,ordinal,dependency_kind,source_id,source_version_id,source_revision,original_sha256) VALUES(%s,1,1,'source',%s,%s,%s,%s)",(mid,source['id'],source['version_id'],source['revision'],source['sha256']))
        connection.execute('INSERT INTO public.learning_memory_bodies(memory_id,version,body) VALUES(%s,1,%s)',(mid,body))
    current=await ledger.read_memory_snapshot(mid)
    impact=await ledger.preview_memory_change(mid,1,'revise')
    await ledger.apply_memory_command(MemoryCommandInput(business_key=str(uuid4()),memory_id=mid,expected_revision=1,action='revise',
        body={'kind':'self_report','title':'合成背景','text':'第二版用户自报背景','base_body_sha256':current['body_sha256'],'impact_token':impact['impact_token']}))
    current=await ledger.read_memory_snapshot(mid)
    selected=await activity(MemorySelectionInput(confirmed=True,entries=[{'memory_id':mid,'version':2,'revision':2,'body_sha256':current['body_sha256']}]))
    identities.update(memory_id=mid,memory_activity_id=selected)
    revoked=str(uuid4())
    await ledger.apply_memory_command(MemoryCommandInput(business_key=str(uuid4()),memory_id=revoked,expected_revision=0,action='save',body={'kind':'preference','title':'待撤销背景','text':'合成偏好'}))
    impact=await ledger.preview_memory_change(revoked,1,'revoke')
    pending=await ledger.apply_memory_command(MemoryCommandInput(business_key=str(uuid4()),memory_id=revoked,expected_revision=1,action='revoke',
        body={'impact_token':impact['impact_token'],'confirm_revoke':True,'purge_memory_content':True}))
    identities.update(revoked_memory_id=revoked,pending_memory_receipt=pending)

    # 面试目标、应用问题、用户答案及修正全部来自原同事务 producer。
    aid=await activity()
    async def interview(action,body,revision,goal):
        return await ledger.apply_interview_local(aid,InterviewCommandInput(business_key=str(uuid4()),action=action,
            expected_head_revision=revision,expected_goal_version=goal,expected_scope_revision=1,body=body),
            application_value={'type':'question','text':'说明当前资料','purpose':'合成核对','reason':'仅作已保存样本'} if action=='ask' else None)
    await interview('start',{'goal':{'target':'旧目标'}},0,0)
    await interview('goal',{'goal':{'target':'当前目标'}},1,1)
    await interview('ask',{'mode':'first'},2,2)
    head=(await ledger.read_interview_workspace(aid))['head'];qid=head['current_question_id']
    await interview('answer',{'question_record_id':qid,'text':'第一次回答'},3,2)
    head=(await ledger.read_interview_workspace(aid))['head']
    await interview('correct_answer',{'answer_record_id':head['current_answer_id'],'expected_answer_version':1,'text':'修正后的回答'},4,2)
    identities['interview_activity_id']=aid

    # 只写合成传输的标准模型收据，原预算和未知预留按原仓储保留。
    aid=await activity();lease=await ledger.claim_lease(aid,'task114-fixture',lease_seconds=120,window_seconds=120)
    snapshot=await ledger.read_learning_snapshot(aid);source_ids=validate_snapshot(snapshot)
    identity=dict(action='first',activity_id=aid,goal='当前资料',question=None,scope_revision=1,sources=[s.model_dump() for s in source_ids],
                  parent_operation_id=None,parent_payload_sha256=None,max_output_tokens=256)
    request_sha=request_fingerprint(**identity)
    profile=LearningProfile(**identity,request_sha256=request_sha,catalog=assemble_catalog('当前资料',load_units(snapshot,materials,store),request_sha))
    model=normalize_result(profile,{'kind':'answer','message':'合成传输结果','segments':[{'text':'当前资料的合成解释','citations':[profile.catalog[0].citation_id]}],'questions':[]})
    async def result(op,value,html_binding=None):
        permit=await ledger.admit(AdmissionIntent(CallContext(activity_id=aid,executor_id='task114-fixture',operation_id=op,
            execution_generation=lease.execution_generation,scope_revision=1),Provider.DEEPSEEK,'task114-synthetic',100,256,(),html_binding=html_binding))
        await ledger.mark_dispatch_started(permit)
        fmt,payload,sha=build_business_payload(json_object=value)
        await ledger.record_outcome(permit,LedgerOutcome(LedgerDisposition.RECEIVED,prompt_tokens=1,completion_tokens=1,response_bytes=len(payload.encode()),payload_format=fmt,payload=payload,payload_sha256=sha))
        return sha
    parent_op=FIRST_PREFIX+request_sha;parent_sha=await result(parent_op,model)
    cfg=digest('task114-synthetic-configuration');key=str(uuid4());renderer=runtime_identity()['renderer_sha256']
    command=await ledger.accept_html_command(aid,HtmlCommand(business_key=key,parent={'kind':'learning','operation_id':parent_op,'payload_sha256':parent_sha,'segment_index':0},
        focus='合成解释',expected_config_sha256=cfg,confirmed=True),renderer,cfg)
    assert await ledger.claim_html_command(aid,key)
    cid=profile.catalog[0].citation_id
    description={'schema':'interactive_description.v1','title':'有限倍数','concept':'数值倍增的合成解释',
        'inputs':[{'id':'hctl_x','kind':'number','label':'输入','description':'有限输入','min':'0','max':'10','step':'1','default':'2'}],
        'calculations':[{'id':'hcalc_double','expression':{'op':'mul','args':[{'op':'input','id':'hctl_x'},{'op':'const','value':'2'}]}}],
        'views':[{'id':'hout_double','kind':'readout','label':'两倍','calculation':'hcalc_double','unit':''}], 'actions':[],
        'calculation_notes':[{'formula':'x*2','domain':'0至10','error':'无舍入保证','samples':[{'input':'0','expected':'0'},{'input':'2','expected':'4'}],'citations':[cid]}],
        'citations':[cid],'limitations':['仅合成数据，不评价真实模型']}
    package=compile_description(description,[cid])
    binding=HtmlCallBinding(business_key=key,request_sha256=command['request_sha256'],context_sha256=command['context_sha256'],renderer_sha256=renderer)
    await result(operation_id(key),{'profile':'html_explanation.v2','activity_id':aid,'business_key':key,'request_sha256':command['request_sha256'],
        'context_sha256':command['context_sha256'],'package':package},binding)
    artifact=await ledger.read_html_command(aid,key);artifact_id=artifact['artifact_id']
    # 仅数据库历史样本，不创建 Docker preview、不制造物理停止证明。
    for index,state in enumerate(('failed_unstarted','failed_unstarted','cleanup_unconfirmed')):
        owner=secrets.token_hex(32);control=secrets.token_hex(32);t0=time.monotonic_ns()
        identity={'preview_id':str(uuid4()),'owner_id':str(uuid4()),'control_key':control,'boot_id':str(uuid4()),'nonce':secrets.token_hex(32),
            'image_id':'sha256:ec3c70c7a8a8894c647a69b08b0c296727bb052f639e487567e9cd4624766789','t0_ns':t0,'deadline_at':datetime.now(timezone.utc)+timedelta(seconds=60),'config_sha256':cfg}
        row,_=await ledger.reserve_html_preview(aid,artifact_id,OpenPreview(start_key=str(uuid4()),expected_artifact_sha256=package['artifact_sha256'],input_owner_key=owner,confirmed=True),identity,60)
        if state=='cleanup_unconfirmed':await ledger.update_html_preview(row['preview_id'],control,state)
        else:
            # 明确标归档夹具观察；receipt 仅满足旧存储形状，不作为新树证明。
            await ledger.update_html_preview(row['preview_id'],control,'failed_unstarted',confirmation={'tree_confirmation':'never_started','fixture_observation':True},elapsed=0)
    unknown_op='task114-unknown'
    permit=await ledger.admit(AdmissionIntent(CallContext(activity_id=aid,executor_id='task114-fixture',operation_id=unknown_op,execution_generation=lease.execution_generation,scope_revision=1),Provider.DEEPSEEK,'task114-synthetic',100,256,()))
    await ledger.mark_dispatch_started(permit);await ledger.record_outcome(permit,LedgerOutcome(LedgerDisposition.UNKNOWN,error_code='fixture_unknown'))
    identities.update(model_activity_id=aid,model_operation_id=parent_op,html_artifact_id=artifact_id,unknown_operation_id=unknown_op)
    return plain(identities)
