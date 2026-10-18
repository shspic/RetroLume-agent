"""One combined remaining PG/HTTP/native group. No old effects repeated."""
import asyncio,io,json,os,secrets,sys,time
from dataclasses import replace
from pathlib import Path
from uuid import uuid4
import httpx,psycopg
from psycopg.rows import dict_row
from .control import EVIDENCE,atomic_json
from .harness import Harness,MODEL
from .http import Server,HTTP
from .resources import start,stop
from .samples import *
from app.interview.contracts import InterviewRefusal,profile_for,operation_id
from app.capabilities.contracts import CallContext,ModelCallRequest,ToolCallPlan
from app.capabilities.gateway import ControlledModelGateway
from app.activities.service import ActivityService
from app.learning.service import LearningService
from app.learning.evidence import LearningRefusal
from app.learning.teaching_service import TeachingService
from app.learning.teaching_contracts import TeachingCommandInput,TeachingRefusal
from app.memory.contracts import MemoryCommandInput,MemorySelectionInput
from app.activities import ActivitySpec,SourceSnapshot

async def reject(fn,allowed):
    try:await fn()
    except (InterviewRefusal,TeachingRefusal,LearningRefusal) as exc:
        code=getattr(exc,'code',str(exc));assert code in allowed,(code,allowed);return code
    raise AssertionError('Expected refusal missing')

async def answer(h,aid,text):
    v=await h.ledger.read_interview_workspace(aid);return await h.command(aid,'answer',dict(question_record_id=v['head']['current_question_id'],text=text))

async def review(h,aid):
    v=await h.ledger.read_interview_workspace(aid);return await h.command(aid,'review',dict(question_record_id=v['head']['current_question_id'],answer_record_id=v['head']['current_answer_id']))

async def check_support(h,aid,r,kind):
    assert r['status']=='committed',r;detail=await h.ledger.read_interview_record(aid,r['record_ids'][0]);value=detail['body']['value']
    ids=value['recognitions'][0]['reference_ids'];picked=[x for x in detail['body']['catalog'] if x['citation_id'] in ids]
    needles=(SERIAL,TRACE) if kind=='T' else (YEAR_A,YEAR_B)
    assert all(any(n in c['text'] for c in picked) for n in needles),dict(kind=kind,picked=picked)
    if kind=='H':assert len({c['source_id'] for c in picked})==2 and value['conflicts'] and '未知' in value['conflicts'][0]['text']
    quotes=[]
    for c in picked:
        actual=await h.service.read_citation(aid,r['record_ids'][0],c['citation_id'],detail['view_token'])
        name=next(n for n,s in h.saved.items() if s['id']==c['source_id']);original=SAMPLES[name]
        assert c['text']==original[c['start_offset']:c['end_offset']] and actual['position_verified'] and h.saved[name]['sha256']==HASHES[name]
        quotes.append(actual)
    assert value['recognitions'][0]['verification_kind']=='source_interpretation'
    return dict(detail=detail,quotes=quotes,source_support=True,oracle='frozen fictional sentences and scalar offsets, independently checked')

async def positives(h):
    for name in SAMPLES:h.material(name)
    atomic_json(h.out/'samples-oracle.json',dict(texts=SAMPLES,hashes=HASHES,oracle=ORACLE,materials=h.saved))
    results={}
    for kind,names,target,text in (('T',[T_NAME],'余额算法串行覆盖',T_ANSWER),('H',[H1_NAME,H2_NAME],'史料活动X年份策展',H_ANSWER)):
        aid=await h.start(names,target);await h.command(aid,'ask',{'mode':'first'});a,_=await answer(h,aid,text);f,_=await review(h,aid)
        first=await check_support(h,aid,f,kind);nextq,_=await h.command(aid,'ask',{'mode':'next','parent_feedback_id':f['record_ids'][0]});await answer(h,aid,text);nextf,_=await review(h,aid)
        second=await check_support(h,aid,nextf,kind)
        if kind=='T':
            chosen=await h.ledger.read_interview_record(aid,a['record_ids'][0]);assert chosen['record']['can_correct_answer']
            repaired,_=await h.command(aid,'correct_answer',dict(answer_record_id=a['record_ids'][0],expected_answer_version=1,text=T_ANSWER+' 这是明确另存的早期回答v2。'))
            oldanswer=await h.ledger.read_interview_record(aid,a['record_ids'][0]);oldfb=await h.ledger.read_interview_record(aid,f['record_ids'][0]);oldq=await h.ledger.read_interview_record(aid,nextq['record_ids'][0])
            assert oldanswer['body'] and not oldanswer['record']['can_correct_answer'] and oldfb['body'] is None and oldq['body'] is None
            now=await h.ledger.read_interview_workspace(aid);assert now['head']['round_index']==1 and now['head']['current_answer_id']==repaired['record_ids'][0]
            newf,_=await review(h,aid);correct=await check_support(h,aid,newf,kind)
            atomic_json(h.out/'historical-recursive-correction.json',dict(aid=aid,before_answer=chosen,old_answer=oldanswer,old_feedback=oldfb,old_successor_question=oldq,corrected=repaired,workspace=now,new_feedback=correct))
        await h.command(aid,'finish',{});closed=await h.ledger.read_interview_workspace(aid);hist=await h.ledger.read_interview_history(aid)
        assert closed['head']['phase']=='ended' and all('payload' not in x and 'local_body' not in x for x in hist['records'])
        results[kind]=dict(aid=aid,first=first,explicit_next=second,closed=closed,history=hist)
        atomic_json(h.out/'positive-two-directions.json',results)
    # Independent UI purpose, no model calls yet.
    ui=await h.start([T_NAME],'余额算法UI历史修订')
    return results,ui

async def small_remaining(h):
    spring=await h.start([SPRING_NAME],'Spring');q,_=await h.command(spring,'ask',{'mode':'first'});d=await h.ledger.read_interview_record(spring,q['record_ids'][0]);assert d['body']['value']['purpose']=='clarification'
    await h.command(spring,'goal',{'goal':{'target':'Spring季节含义'}});newq,_=await h.command(spring,'ask',{'mode':'first'});assert newq['status']=='committed';await h.command(spring,'finish',{})
    missing=await h.start([H1_NAME],'余额算法串行覆盖');local,_=await h.command(missing,'ask',{'mode':'first'});assert local['execution_kind']=='local'
    source=h.saved[T_NAME];bound,_=await h.command(missing,'bind_scope',dict(sources=[dict(source_id=source['id'],version_id=source['version_id'],source_revision=source['revision'],original_sha256=source['sha256'])],material_roles=[dict(source_id=source['id'],role='reference')]))
    actual,_=await h.command(missing,'ask',{'mode':'first'});detail=await h.ledger.read_interview_record(missing,actual['record_ids'][0]);assert detail['record']['scope_revision']==2 and detail['body']['scope_revision']==2
    atomic_json(h.out/'clarification-and-adopted-new-scope-native.json',dict(spring=d,new_spring_question=newq,local_missing=local,bound=bound,current=detail))
    cv=await h.start([CV_NAME],'自报性能快60%基线口径',{CV_NAME:'resume'});await h.command(cv,'ask',{'mode':'first'});probes=[]
    for depth in range(3):
        await answer(h,cv,'我自报性能快60%，暂无测量记录。');c=await h.make(cv,'review',dict(question_record_id=(await h.ledger.read_interview_workspace(cv))['head']['current_question_id'],answer_record_id=(await h.ledger.read_interview_workspace(cv))['head']['current_answer_id']))
        if depth==2:atomic_json(EVIDENCE/'scenarios'/c.business_key,dict(scenario='force_probe'))
        r=await h.service.submit_command(cv,c,h.config,run_tag='c01-probe-'+str(depth))
        if depth<2:
            d=await h.ledger.read_interview_record(cv,r['record_ids'][0]);assert d['body']['value']['type']=='probe' and d['body']['value']['recognitions'][0]['verification_kind']=='user_statement';probes.append(d)
        else:assert r['status']=='failed' and not r['effect_applied'];invalid=r
    state=h.snapshot(cv);assert state['activity']['requests_reserved']==4 and len(state['results'])==3 and state['head']['probe_depth']==2
    atomic_json(h.out/'native-probe-depth-received-invalid.json',dict(probes=probes,invalid=invalid,state=state))
    await h.command(cv,'finish',{})

async def cross_and_legacy(h,parent):
    service=ActivityService(h.ledger);learning=LearningService(h.ledger,h.materials,h.originals);codes={};before=h.snapshot(parent)
    op=before['results'][0]['operation_id'];legacy=await h.activity([T_NAME]);tool=ToolCallPlan('c01-tool','finite_calculate',{'expression':'1+1'})
    codes['continue_domain']=(await service.continue_from_result(parent,op,'c01-invalid1','继续',h.config.model_service,h.session,'local-ui','c01-refusal')).status
    codes['continue_parent']=(await service.continue_from_result(legacy,op,'c01-invalid2','继续',h.config.model_service,h.session,'local-ui','c01-refusal2')).status
    codes['tool_domain']=(await service.execute_tool_action(parent,'c01-tool',tool,h.session,'local-ui','c01-tool-refusal')).status
    codes['learning_domain']=await reject(lambda:learning.execute(parent,str(uuid4()),'余额算法',h.config,run_tag='c01-l-refusal'),{'interview_domain_conflict'})
    codes['learning_parent']=await reject(lambda:learning.execute(legacy,str(uuid4()),'余额算法',h.config,parent_operation_id=op,run_tag='c01-l-parent'),{'interview_parent_forbidden'})
    tc=TeachingCommandInput.model_validate(dict(business_key=str(uuid4()),action='goal',expected_revision=0,expected_goal_version=0,expected_scope_revision=1,body={'goal':'不得跨域'}))
    codes['teaching_head']=await reject(lambda:h.ledger.apply_teaching_local(parent,tc),{'stage_conflict'})
    assert codes['continue_domain']==codes['tool_domain']=='interview_domain_conflict' and codes['continue_parent']=='interview_parent_forbidden' and h.snapshot(parent)==before,codes
    # Fully valid frozen carrier; wrong activity/op or absent profile must reject.
    ready=await h.start([T_NAME],'余额算法wrong-binding');command=await h.make(ready,'ask',{'mode':'first'});frozen=await h.service._frozen(ready,command,h.config)
    from app.interview.prompt import messages
    req=ModelCallRequest(interview_profile=profile_for(frozen),messages=messages(frozen),max_output_tokens=512);gateway=ControlledModelGateway(h.config.model_service,ledger=h.ledger)
    for name,aid,operation,request in (('missing',ready,operation_id(command.business_key),ModelCallRequest(messages=[dict(role='user',content='ordinary')],max_output_tokens=128)),('wrong_op',ready,'c01-normal',req),('wrong_activity',legacy,operation_id(command.business_key),req)):
        r=await gateway.call(CallContext(activity_id=aid,operation_id=operation,executor_id='local-ui',execution_generation=1,scope_revision=1),request);assert r.status.value=='rejected';codes[name]=r.error_code
    import app.learning.service as learning_module
    original=learning_module.SessionConfig;learning_module.SessionConfig=lambda:h.session
    try:learned=await learning.execute(legacy,str(uuid4()),'余额算法串行110',h.config,run_tag='c01-upgraded-learning')
    finally:learning_module.SessionConfig=original
    teach=await h.activity([T_NAME]);ts=TeachingService(h.ledger,h.materials,h.originals,session_config=h.session)
    goal=TeachingCommandInput.model_validate(dict(business_key=str(uuid4()),action='goal',expected_revision=0,expected_goal_version=0,expected_scope_revision=1,body={'goal':'余额算法'}))
    await ts.submit_command(teach,goal,h.config,run_tag='c01-upgraded-goal');v=await h.ledger.read_teaching_workspace(teach)
    plan=TeachingCommandInput.model_validate(dict(business_key=str(uuid4()),action='plan',expected_revision=v['head']['revision'],expected_goal_version=v['head']['goal_version'],expected_scope_revision=1,body={'confirmed':True}))
    taught=await ts.submit_command(teach,plan,h.config,run_tag='c01-upgraded-plan');assert taught.status=='committed'
    with psycopg.connect(h.dsn,row_factory=dict_row) as conn:
        bodies=[dict(x) for x in conn.execute('SELECT r.activity_id::text,r.operation_id,r.payload::jsonb AS payload FROM activity_operation_results r WHERE r.activity_id=ANY(%s::uuid[])',([legacy,teach],))]
    assert len(bodies)==2 and {x['payload']['value']['profile'] for x in bodies}=={'learning.v1','teaching.v1'}
    atomic_json(h.out/'cross-consumption-and-upgraded-legacy.json',dict(refusals=codes,legacy_bodies=bodies,learning_return=str(learned),old_interview_unchanged=h.snapshot(parent)==before))

async def memory_invalid(h):
    mid=str(uuid4());save=MemoryCommandInput.model_validate(dict(schema='memory.command.v1',business_key=str(uuid4()),memory_id=mid,expected_revision=0,action='save',body=dict(title='C01虚构偏好',text='偏好文字说明，明确自报',kind='preference',capture=None)))
    await h.ledger.apply_memory_command(save)
    with psycopg.connect(h.dsn,row_factory=dict_row) as conn:m=conn.execute('SELECT h.revision,h.current_version,r.body_sha256 FROM learning_memories h JOIN learning_memory_revisions r ON r.memory_id=h.memory_id AND r.version=h.current_version WHERE h.memory_id=%s',(mid,)).fetchone()
    source=h.saved[T_NAME];aid=str(uuid4());from datetime import datetime,timedelta,timezone
    selection=MemorySelectionInput.model_validate(dict(confirmed=True,entries=[dict(memory_id=mid,version=m['current_version'],revision=m['revision'],body_sha256=m['body_sha256'])]))
    await h.ledger.create_activity(ActivitySpec(activity_id=aid,sources=(SourceSnapshot(source['id'],source['version_id'],source['revision']),),deadline_at=datetime.now(timezone.utc)+timedelta(hours=2),max_requests=10,max_cost_microunits=10000,reserve_cost_microunits=100,max_request_bytes=65536,max_output_tokens=1024,max_running_seconds=3600,allowed_models=(('deepseek_chat_completions',MODEL),),max_tool_calls=0),memory_selection=selection)
    preview=await h.ledger.preview_memory_change(mid,m['revision'],'revise')
    revised=MemoryCommandInput.model_validate(dict(schema='memory.command.v1',business_key=str(uuid4()),memory_id=mid,expected_revision=m['revision'],action='revise',body=dict(title='C01虚构偏好',text='明确修改后的文字偏好',kind='preference',base_body_sha256=m['body_sha256'],impact_token=preview['impact_token'])))
    await h.ledger.apply_memory_command(revised)
    before=await h.ledger.read_memory_selection(aid);code=await reject(lambda:h.command(aid,'start',{'goal':None}),{'interview_memory_dependency_invalid'});v=await h.ledger.read_interview_workspace(aid)
    assert v['head'] is None and v['suppression_reason']=='interview_memory_dependency_invalid' and before['selected'] and not before['eligible']
    atomic_json(h.out/'actual-invalid-memory-selection.json',dict(mid=mid,selection=selection.model_dump(),before=before,after=await h.ledger.read_memory_selection(aid),code=code,view=v))

async def large_history(h):
    names=list(SAMPLES)
    for n in range(5):name=f'TASK106-C01-bound-{n}.md';h.material(name,T);names.append(name)
    aid=await h.start(names,'xxxxxxxxunknownunmatchedzzzz');q,_=await h.command(aid,'ask',{'mode':'first'});assert q['execution_kind']=='local'
    a,_=await answer(h,aid,'本机第1版。');rid=a['record_ids'][0]
    for n in range(2,51):r,_=await h.command(aid,'correct_answer',dict(answer_record_id=rid,expected_answer_version=n-1,text=f'本机第{n}版。'));rid=r['record_ids'][0]
    assert h.snapshot(aid)['activity']['requests_reserved']==0
    return aid

def marker(key,stage):return EVIDENCE/'barriers'/key/stage
async def wait_file(path,timeout=10):
    until=time.perf_counter()+timeout
    while not path.exists():
        if time.perf_counter()>until:raise RuntimeError('C01 actual barrier did not enter: '+path.name)
        await asyncio.sleep(.02)
    return json.loads(path.read_text(encoding='utf-8'))

async def cancellation_cases(h,http):
    proofs=[]
    for name,stage in (('caller_marked_goal','before_result'),('caller_after_commit','after_result'),('cancel_before_mark','before_mark'),('cancel_after_mark','after_mark'),('caller_db_unreadable','before_result')):
        aid=await h.start([T_NAME],'余额算法取消窗'+name);command=await h.make(aid,'ask',{'mode':'first'});key=command.business_key
        stages=[stage]+(['before_finish'] if name in ('caller_marked_goal','caller_db_unreadable') else [])
        atomic_json(EVIDENCE/'barriers'/key/'plan.json',dict(stages=stages));before=h.snapshot(aid)
        headers={**http.headers,**({'X-C01-Cancel-Key':key} if name.startswith('caller') else {})}
        async def request():
            async with httpx.AsyncClient(trust_env=False,timeout=45) as client:
                r=await client.post('http://127.0.0.1:18106/api/activities/'+aid+'/interview/commands',headers=headers,json=command.model_dump());return dict(status=r.status_code,body=r.text[:5000])
        pending=asyncio.create_task(request());entered=await wait_file(marker(key,stage)/'entered.json');during=h.snapshot(aid)
        try:
            if name in ('caller_marked_goal','caller_db_unreadable'):
                await h.command(aid,'goal',{'goal':{'target':'余额算法已修正目标'}});atomic_json(EVIDENCE/'barriers'/key/'cancel.json',dict(at_ns=time.perf_counter_ns()))
            elif name.startswith('cancel_'):await h.ledger.cancel_activity(aid)
            elif name=='caller_after_commit':atomic_json(EVIDENCE/'barriers'/key/'cancel.json',dict(at_ns=time.perf_counter_ns()))
            atomic_json(marker(key,stage)/'release.json',dict(at_ns=time.perf_counter_ns()))
            if 'before_finish' in stages:
                finish_entered=await wait_file(marker(key,'before_finish')/'entered.json')
                atomic_json(EVIDENCE/'barriers'/key/'cancel2.json',dict(at_ns=time.perf_counter_ns()))
                await asyncio.sleep(.06)
                if name=='caller_db_unreadable':stop(1)
                atomic_json(marker(key,'before_finish')/'release.json',dict(at_ns=time.perf_counter_ns()))
            response=await pending
            if name.startswith('caller'):await wait_file(EVIDENCE/'barriers'/key/'route-cancelled.json')
            if name=='caller_db_unreadable':
                admin=start(1)
                unconfirmed=h.snapshot(aid);assert not unconfirmed['results'] and unconfirmed['operations'][0]['state'] in ('dispatched','unknown')
                await h.ledger.finish_interview_supervision(aid,key,finish_entered['context']['facts'])
            after=h.snapshot(aid);receipt=await h.ledger.read_interview_command(aid,key)
            if name=='caller_after_commit':assert len(after['results'])==1 and receipt['status']=='committed' and during['results']==after['results']
            else:
                assert not after['results'] and after['operations'][0]['state']=='unknown' and receipt['status']=='unknown',after
                assert after['activity']['requests_reserved']==1 and after['activity']['cost_reserved_microunits']==100 and after['activity']['running_reserved_seconds']==0,after
            if name.startswith('cancel_'):
                view=await h.service.read_workspace(aid,h.config);assert not view['capabilities']['model'] and view['capabilities']['model_reason']=='cancelled'
            frozen_after=h.snapshot(aid);again=await h.ledger.read_interview_command(aid,key);assert frozen_after==h.snapshot(aid)
            proof=dict(name=name,aid=aid,key=key,entered=entered,before=before,during=during,after=after,receipt=receipt,GET=again,response=response,
                cancellation_is_not_stop_proof=True,unknown_never_refunded=True)
            if name=='caller_db_unreadable':proof.update(unconfirmed_before_diagnostic=unconfirmed,actual_stop_facts=finish_entered['context']['facts'])
            proofs.append(proof);atomic_json(h.out/'exact-cancellation-cases.json',proofs)
        finally:
            for st in stages:atomic_json(marker(key,st)/'release.json',dict(finally_release=True))
            if not pending.done():await pending
    # Scope is a distinct representative before native admit, no new remote send.
    aid=await h.start([T_NAME],'余额算法scope窗');c=await h.make(aid,'ask',{'mode':'first'});atomic_json(EVIDENCE/'barriers'/c.business_key/'plan.json',dict(stages=['before_admit']))
    task=asyncio.create_task(h.service.submit_command(aid,c,h.config,run_tag='c01-scope-window'));entered=await wait_file(marker(c.business_key,'before_admit')/'entered.json')
    try:
        s=h.saved[H1_NAME];bound,_=await h.command(aid,'bind_scope',dict(sources=[dict(source_id=s['id'],version_id=s['version_id'],source_revision=s['revision'],original_sha256=s['sha256'])],material_roles=[dict(source_id=s['id'],role='reference')]))
        atomic_json(marker(c.business_key,'before_admit')/'release.json',dict(at_ns=time.perf_counter_ns()));receipt=await task;after=h.snapshot(aid);assert not after['operations'] and not after['results'] and after['activity']['requests_reserved']==0
        atomic_json(h.out/'scope-before-admit.json',dict(aid=aid,entered=entered,bound=bound,receipt=receipt,after=after))
    finally:
        atomic_json(marker(c.business_key,'before_admit')/'release.json',dict(finally_release=True))
        if not task.done():await task

async def run(h):
    positives_result,ui=await positives(h);await small_remaining(h);await cross_and_legacy(h,positives_result['T']['aid']);await memory_invalid(h);large=await large_history(h)
    # Native accepted/unclaimed fixture for explicit original-key UI replay.
    accepted_aid=await h.start([T_NAME],'余额算法accepted原意图');accepted_cmd=await h.make(accepted_aid,'ask',{'mode':'first'});frozen=await h.service._frozen(accepted_aid,accepted_cmd,h.config)
    receipt=await h.ledger.accept_interview_command(accepted_aid,accepted_cmd,frozen);assert not receipt['launch_claimed']
    lost=await h.start([T_NAME],'余额算法浏览器丢响应')
    with Server(h.dsn,h.out) as server:
        http=HTTP(h.out)
        before=h.snapshot(large);r=http.request('GET',f'/api/activities/{large}/interview/history?limit=50');assert r.status_code==413 and r.json()['code']=='interview_snapshot_limit';assert h.snapshot(large)==before
        invalid=http.request('GET',f'/api/activities/{large}/interview/history?before_seq=0');assert invalid.status_code==422
        raw=http.request('POST',f'/api/activities/{ui}/interview/commands',content=b' '*32769,headers={**http.headers,'Content-Type':'application/json'});assert raw.status_code==413
        atomic_json(h.out/'actual-http-capacity-refusals.json',dict(large_activity=large,history=r.json(),cursor_status=invalid.status_code,command_status=raw.status_code,no_effect=True))
        await cancellation_cases(h,http);http.client.close()
    # Real cached config startup variants, same ordinary DB, never UI supplied.
    negative=await h.start([T_NAME],'余额算法非法配置');before=h.snapshot(negative)
    for mode,code in (('illegal_model','interview_binding_invalid'),('onecall_limit','interview_context_too_large')):
        with Server(h.dsn,h.out,mode):
            http=HTTP(h.out);c=await h.make(negative,'ask',{'mode':'first'});r=http.request('POST',f'/api/activities/{negative}/interview/commands',json=c.model_dump());assert r.status_code in (409,422) and r.json()['code']==code,dict(mode=mode,status=r.status_code,body=r.json());http.client.close()
        assert h.snapshot(negative)==before
    seed=dict(technical=ui,lost=lost,accepted=accepted_aid,acceptedCommand=accepted_cmd.model_dump(),acceptedReceipt=receipt,technicalTitle=h.saved[T_NAME]['title'],materials=h.saved,Tanswer=T_ANSWER,Hanswer=H_ANSWER)
    atomic_json(h.out/'browser-seed.json',seed);atomic_json(h.out/'core-summary.json',dict(positive=positives_result,browser_seed=seed,all_remaining_methods_completed=True))

def main():
    if sys.platform=='win32':asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    out=Path(os.environ['C01_OUT']);h=Harness(os.environ['C01_ADMIN_DSN'],os.environ['C01_APP_DSN'],out);asyncio.run(run(h));print('C01 core actual methods completed')

if __name__=='__main__':main()
