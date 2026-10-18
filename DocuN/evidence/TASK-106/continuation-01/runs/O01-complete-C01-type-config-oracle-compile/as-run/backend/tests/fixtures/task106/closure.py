"""Remaining new-domain boundaries on real ordinary PG/native/HTTP.

No authority replacement: barriers wrap actual methods; bulk capacity preparation
creates only declared011 synthetic rows under its real checks and triggers.
"""
import asyncio,io,json,os,secrets,subprocess,sys,time
from dataclasses import replace
from datetime import datetime,timedelta,timezone
from uuid import uuid4
import httpx,psycopg
from psycopg import sql
from psycopg.rows import dict_row
from .control import ROOT,EVIDENCE,batch,reserve,atomic_json
from .resources import start,stop,runtime
from .core import Harness
from .samples import T_NAME,SAMPLES
from .directed import start_goal
from .windows import wait_marker
from .http_group import app_environment,process_birth,HTTP
from app.activities import ActivitySpec,SourceSnapshot
from app.interview.contracts import InterviewCommandInput,InterviewRefusal,canonical,sha,profile_for,operation_id
from app.interview.prompt import messages
from app.interview.views import plain
from app.capabilities.contracts import AdmissionDenied,AdmissionPermit,LedgerOutcome,LedgerDisposition,RecordOutcome,ModelCallRequest,CallContext,build_business_payload
from app.capabilities.gateway import ControlledModelGateway
from app.learning.teaching_contracts import TeachingRefusal,TeachingCommandInput


async def refused(fn,codes):
    try:await fn()
    except (InterviewRefusal,AdmissionDenied,TeachingRefusal) as exc:
        code=getattr(exc,'code',str(exc));assert code in codes,(code,codes);return code
    raise AssertionError('Expected concrete refusal did not occur')


async def command(h,aid,action,body,key=None):
    v=await h.ledger.read_interview_workspace(aid);head=v['head'] or {}
    return InterviewCommandInput.model_validate(dict(schema='interview.command.v1',business_key=key or str(uuid4()),action=action,
        expected_head_revision=head.get('revision',0),expected_goal_version=head.get('goal_version',0),expected_scope_revision=head.get('scope_revision',1),body=body))


def native_outcome(h,aid,op):
    with psycopg.connect(h.dsn,row_factory=dict_row) as conn:
        row=conn.execute('SELECT o.*,r.payload_format,r.payload,r.payload_sha256 FROM activity_operations o LEFT JOIN activity_operation_results r USING(activity_id,operation_id) WHERE o.activity_id=%s AND o.operation_id=%s',(aid,op)).fetchone()
    permit=AdmissionPermit(str(row['admission_id']),row['operation_id'],row['executor_id'])
    fields=('error_code','remote_request_id','returned_model','finish_reason','prompt_tokens','completion_tokens','response_bytes','payload_format','payload','payload_sha256')
    outcome=LedgerOutcome(LedgerDisposition(row['disposition']),**{k:row[k] for k in fields})
    return permit,outcome


async def concurrency(h):
    h.material(T_NAME);aid=await start_goal(h,[T_NAME],'余额算法并发确认',{T_NAME:'reference'})
    c=await command(h,aid,'ask',{'mode':'first'});frozen=await h.service._frozen(aid,c,h.config)
    accepted=await h.ledger.accept_interview_command(aid,c,frozen)
    before=h.snapshot(aid);assert accepted['status']=='accepted' and not accepted['launch_claimed'] and not before['operations']
    # Real GET cannot claim a previously committed acceptance.
    read=await h.ledger.read_interview_command(aid,c.business_key);assert not read['launch_claimed'] and h.snapshot(aid)==before
    alias=InterviewCommandInput.model_validate({**c.model_dump(),'business_key':str(uuid4())})
    barrier_key=uuid4().hex;folder=ROOT/'backend/tests/fixtures/task106/barriers'/barrier_key
    os.environ['RETROLUME_TASK106_BARRIER']='accepted_before_admit';os.environ['RETROLUME_TASK106_BARRIER_KEY']=barrier_key
    first=asyncio.create_task(h.service.submit_command(aid,c,h.config,run_tag='task106-explicit-claim'))
    try:
        entered=await wait_marker(folder)
        other=await asyncio.gather(*(h.service.submit_command(aid,x,h.config,run_tag='task106-overlap-'+secrets.token_hex(4)) for x in (c,alias)))
        during=h.snapshot(aid);assert not during['operations']
        assert sum(x['launch_claimed'] and not x['duplicate_of'] for x in other)==1 and any(x['duplicate_of'] for x in other),other
        atomic_json(folder/'release.json',dict(at_ns=time.perf_counter_ns()))
        committed=await first;after=h.snapshot(aid)
    finally:
        atomic_json(folder/'release.json',dict(finally_release=True));os.environ.pop('RETROLUME_TASK106_BARRIER',None);os.environ.pop('RETROLUME_TASK106_BARRIER_KEY',None)
        if not first.done():await first
    assert committed['status']=='committed' and len(after['operations'])==len(after['results'])==1 and after['activity']['requests_reserved']==1,after
    changed=InterviewCommandInput.model_validate({**c.model_dump(),'body':{'mode':'first','parent_feedback_id':None,'retry_of':str(uuid4())}})
    key_code=await refused(lambda:h.service.submit_command(aid,changed,h.config,run_tag='task106-key-conflict'),{'interview_key_conflict'})
    slot_code=await refused(lambda:h.service.submit_command(aid,InterviewCommandInput.model_validate({**changed.model_dump(),'business_key':str(uuid4())}),h.config,run_tag='task106-slot-conflict'),{'interview_slot_conflict'})
    assert h.snapshot(aid)==after
    atomic_json(h.out/'model-concurrency-explicit-claim.json',dict(aid=aid,command=c.model_dump(),accepted=accepted,GET=read,before=before,entered=entered,concurrent=other,committed=committed,after=after,key_conflict=key_code,slot_conflict=slot_code))
    permit,outcome=native_outcome(h,aid,operation_id(c.business_key));equal=await h.ledger.record_outcome(permit,outcome)
    assert equal==RecordOutcome.ALREADY_PRESENT and h.snapshot(aid)==after
    value=json.loads(outcome.payload)['value'];value['value']['text']+=' 异文'
    fmt,body,digest=build_business_payload(json_object=value)
    altered=replace(outcome,payload_format=fmt,payload=body,payload_sha256=digest)
    conflict=await refused(lambda:h.ledger.record_outcome(permit,altered),{'已终结正文与提交不一致'})
    # An actual received-invalid operation has no007; equal diagnostic remains readonly.
    with psycopg.connect(h.dsn,row_factory=dict_row) as conn:
        old=conn.execute("SELECT o.activity_id::text,o.operation_id FROM activity_operations o LEFT JOIN activity_operation_results r USING(activity_id,operation_id) WHERE left(o.operation_id,7)='int10m.' AND o.state='received' AND r.operation_id IS NULL ORDER BY o.recorded_at LIMIT 1").fetchone()
    assert old
    oldp,oldout=native_outcome(h,old['activity_id'],old['operation_id']);oldbefore=h.snapshot(old['activity_id'])
    assert await h.ledger.record_outcome(oldp,oldout)==RecordOutcome.ALREADY_PRESENT
    nobod=await refused(lambda:h.ledger.record_outcome(oldp,replace(oldout,payload_format=fmt,payload=body,payload_sha256=digest)),{'已终结无正文状态不能补写正文'})
    assert h.snapshot(old['activity_id'])==oldbefore
    atomic_json(h.out/'strict-terminal-equal-different-and-no-body.json',dict(equal=equal,different=conflict,old_no_body=nobod,original=after,unchanged=h.snapshot(aid),old_before=oldbefore,old_after=h.snapshot(old['activity_id'])))
    # Authentic gateway rejects wrong profile/op and wrong activity before admission.
    req=ModelCallRequest(interview_profile=profile_for(frozen),messages=messages(frozen),max_output_tokens=frozen.limits.max_output_tokens)
    gw=ControlledModelGateway(h.config.model_service,ledger=h.ledger);codes=[]
    for context,r in (
        (CallContext(activity_id=aid,operation_id=operation_id(c.business_key),executor_id='task106',execution_generation=1,scope_revision=1),ModelCallRequest(messages=[dict(role='user',content='generic')],max_output_tokens=128)),
        (CallContext(activity_id=aid,operation_id='task106-generic',executor_id='task106',execution_generation=1,scope_revision=1),req),
        (CallContext(activity_id=str(uuid4()),operation_id=operation_id(c.business_key),executor_id='task106',execution_generation=1,scope_revision=1),req),
    ):
        result=await gw.call(context,r);assert result.status.value=='rejected';codes.append(result.error_code)
    from app.learning.teaching_contracts import TeachingCommandInput
    teaching=TeachingCommandInput.model_validate(dict(business_key=str(uuid4()),action='goal',expected_revision=0,expected_goal_version=0,expected_scope_revision=1,body={'goal':'不得跨域'}))
    code=await refused(lambda:h.ledger.apply_teaching_local(aid,teaching),{'stage_conflict'})
    atomic_json(h.out/'native-profile-and-cross-domain.json',dict(gateway_codes=codes,teaching_head=code,state_unchanged=h.snapshot(aid)==after))
    return aid,committed


def replacement(h):
    source=h.saved[T_NAME];raw=(SAMPLES[T_NAME]+'\nTASK106明确合成来源修订，保持现实表现未知。').encode('utf-8')
    original=h.originals.put(io.BytesIO(raw),max_bytes=5242880)
    return h.materials.save(source_id=source['id'],expected_version=source['version_id'],filename=T_NAME,format='md',sha256=original.sha256,size=original.size)


async def citation_cutoffs(h,aid,receipt):
    proofs=[]
    for before_sql in (True,False):
        if not before_sql:
            h.material(T_NAME);aid=await start_goal(h,[T_NAME],'余额算法引用截止后',{T_NAME:'reference'});receipt,_=await h.command(aid,'ask',{'mode':'first'})
        rid=receipt['record_ids'][0];detail=await h.ledger.read_interview_record(aid,rid);entry=detail['body']['catalog'][0]
        original=h.ledger.read_interview_record;entered=asyncio.Event();release=asyncio.Event();calls=0;timing={}
        async def observed(*args,**kwargs):
            nonlocal calls
            calls+=1
            if calls==2 and before_sql:
                timing['before_last_sql_ns']=time.perf_counter_ns();entered.set();await release.wait()
            result=await original(*args,**kwargs)
            if calls==2:
                timing['last_sql_return_ns']=time.perf_counter_ns()
                if not before_sql:entered.set();await release.wait()
            return result
        h.ledger.read_interview_record=observed
        task=asyncio.create_task(h.service.read_citation(aid,rid,entry['citation_id'],detail['view_token']))
        try:
            await asyncio.wait_for(entered.wait(),5);changed=await asyncio.to_thread(replacement,h);timing['source_commit_observed_ns']=time.perf_counter_ns();release.set()
            if before_sql:
                try:await task
                except InterviewRefusal as exc:assert exc.code in ('interview_view_changed','source_invalid');result=dict(refused=exc.code,old_text_returned=False)
                else:raise AssertionError('old quote crossed changed-source final predicate')
            else:
                actual=await task;assert actual['citation']['text']==entry['text'];result=dict(in_flight_after_cutoff=True,body=actual)
        finally:
            release.set();h.ledger.read_interview_record=original
            if not task.done():await task
        workspace=await h.ledger.read_interview_workspace(aid);history=await h.ledger.read_interview_history(aid)
        direct=await h.ledger.read_interview_record(aid,rid);generic=await h.ledger.read_committed_result(aid,receipt['operation_id'])
        assert direct['body'] is None and generic.payload is None and workspace['suppression_reason']=='source_invalid'
        assert all('payload' not in x and 'body' not in x for x in history['records'])
        proof=dict(before_final_sql=before_sql,aid=aid,rid=rid,source=changed,cutoff=timing,result=result,workspace=workspace,history=history,detail=direct,generic_status=generic.read_status.value)
        atomic_json(h.out/('citation-before-final-sql.json' if before_sql else 'citation-after-final-sql.json'),proof);proofs.append(proof)
    return proofs


async def limited_activity(h,**limits):
    aid=str(uuid4());source=h.saved[T_NAME]
    data=dict(activity_id=aid,sources=(SourceSnapshot(source['id'],source['version_id'],source['revision']),),deadline_at=datetime.now(timezone.utc)+timedelta(hours=1),
        max_requests=20,max_cost_microunits=100000,reserve_cost_microunits=100,max_request_bytes=65536,max_output_tokens=1024,max_running_seconds=3600,allowed_models=(('deepseek_chat_completions','task106-synthetic'),),max_tool_calls=0)
    data.update(limits);await h.ledger.create_activity(ActivitySpec(**data));await h.command(aid,'start',{'goal':{'target':'余额算法边界','material_roles':[dict(source_id=source['id'],role='reference')]}})
    return aid


async def budgets_retry_capacity(h):
    h.material(T_NAME);proofs=[]
    for kind in ('request','cost','running','cancelled','expired'):
        limit={'request':dict(max_requests=1),'cost':dict(max_cost_microunits=100),'running':dict(max_running_seconds=1),'cancelled':{},'expired':dict(deadline_at=datetime.now(timezone.utc)+timedelta(seconds=1.2))}[kind]
        aid=await limited_activity(h,**limit)
        if kind in ('request','cost'):
            first,_=await h.command(aid,'ask',{'mode':'first'});assert first['status']=='committed',first
            await h.command(aid,'goal',{'goal':{'target':'余额算法修正后的边界'}})
        elif kind=='cancelled':await h.ledger.cancel_activity(aid)
        elif kind=='expired':await asyncio.sleep(1.3)
        before=h.snapshot(aid)
        if kind=='running':
            receipt,_=await h.command(aid,'ask',{'mode':'first'});assert receipt['status']=='not_sent' and not h.snapshot(aid)['operations'],receipt;code=receipt['status']
        else:code=await refused(lambda:h.command(aid,'ask',{'mode':'first'}),{'interview_budget_exhausted','budget_exhausted','cancelled','activity_expired'})
        after=h.snapshot(aid);assert before['activity']['requests_reserved']==after['activity']['requests_reserved'] and before['activity']['cost_reserved_microunits']==after['activity']['cost_reserved_microunits']
        assert before['results']==after['results'];proofs.append(dict(kind=kind,aid=aid,refusal=code,before=before,after=after))
        atomic_json(h.out/'finite-budgets-cancel-expire.json',proofs)
    aid=await limited_activity(h);os.environ['RETROLUME_TASK106_SCENARIO']='not_sent'
    try:failed,c=await h.command(aid,'ask',{'mode':'first'})
    finally:os.environ.pop('RETROLUME_TASK106_SCENARIO',None)
    assert failed['status']=='not_sent',failed
    again,_=await h.command(aid,'ask',{'mode':'first','retry_of':c.business_key});assert again['status']=='committed'
    snap=h.snapshot(aid);assert snap['activity']['requests_reserved']==2 and len(snap['results'])==1
    atomic_json(h.out/'explicit-not-sent-retry.json',dict(first=failed,retry=again,state=snap))
    # Actual32 goal versions and256 answer versions, local only.
    versions=await limited_activity(h)
    for n in range(2,33):await h.command(versions,'goal',{'goal':{'target':f'xxxxxxxxunmatched{n}'}})
    before=h.snapshot(versions);code=await refused(lambda:h.command(versions,'goal',{'goal':{'target':'第33个目标'}}),{'interview_version_limit'});assert before==h.snapshot(versions)
    q,_=await h.command(versions,'ask',{'mode':'first'});assert q['execution_kind']=='local'
    v=await h.ledger.read_interview_workspace(versions);answer,_=await h.command(versions,'answer',{'question_record_id':v['head']['current_question_id'],'text':'第1版本机原文🧭'})
    rid=answer['record_ids'][0]
    for n in range(2,257):
        answer,_=await h.command(versions,'correct_answer',{'answer_record_id':rid,'expected_answer_version':n-1,'text':f'第{n}版本机原文🧭'});rid=answer['record_ids'][0]
    before=h.snapshot(versions);limitcode=await refused(lambda:h.command(versions,'correct_answer',{'answer_record_id':rid,'expected_answer_version':256,'text':'第257版'}),{'interview_version_limit'});assert before==h.snapshot(versions)
    atomic_json(h.out/'goal-answer-version-real-boundaries.json',dict(aid=versions,goal_limit=code,answer_limit=limitcode,state=before,model_requests=before['activity']['requests_reserved']))
    # Controlled physical011 preparation to actual4096 rows, not public effect proof.
    capacity=await limited_activity(h);view=await h.ledger.read_interview_workspace(capacity);head=view['head'].copy();sources=[{k:s[k] for k in ('source_id','version_id','source_revision','original_sha256')} for s in view['sources']]
    async def prepare(connection):
        for n in range(4094):
            c=InterviewCommandInput.model_validate(dict(schema='interview.command.v1',business_key=str(uuid4()),action='goal',expected_head_revision=head['revision'],expected_goal_version=head['goal_version'],expected_scope_revision=head['scope_revision'],body={'goal':{'target':f'TASK106 physical capacity preparation {n}'}}))
            await h.ledger._interview_insert_command(connection,capacity,c,sha('capacity-'+str(n)),'local')
            await h.ledger._interview_insert_record(connection,capacity,c.business_key,head,'goal',{'goal':c.body['goal'],'copied_from_goal_id':None},sources)
            await connection.execute("UPDATE interview_commands SET status='committed' WHERE activity_id=%s AND business_key=%s",(capacity,c.business_key))
        old=head['revision'];head['revision']=old+1;await h.ledger._interview_put_head(connection,capacity,head,old)
    await h.ledger._transaction(prepare)
    before=h.snapshot(capacity);assert len(before['records'])==4096
    recordcode=await refused(lambda:h.command(capacity,'finish',{}),{'interview_record_limit'});assert before==h.snapshot(capacity)
    # One last declared local metadata command reaches4096; next public action refuses.
    c=await command(h,capacity,'goal',{'goal':{'target':'capacity final command'}})
    async def last(connection):await h.ledger._interview_insert_command(connection,capacity,c,sha('capacity-final'),'local')
    await h.ledger._transaction(last)
    commandcode=await refused(lambda:h.command(capacity,'finish',{}),{'interview_record_limit'})
    atomic_json(h.out/'physical-record-command-capacity.json',dict(aid=capacity,prepared_scope='new011 synthetic rows only; no native/admission/old fact changes; not a public business flow',records=4096,commands=4096,record_refusal=recordcode,command_refusal=commandcode))


async def normal(h):
    if os.environ.get('RETROLUME_TASK106_CLOSURE_RESUME'):
        proof=json.loads((EVIDENCE/'runs/P13-closure-concurrency-cutoff-budget-terminal-schema/model-concurrency-explicit-claim.json').read_text(encoding='utf-8'))
        aid=proof['aid'];q=proof['committed']
        with psycopg.connect(h.dsn,row_factory=dict_row) as conn:
            row=conn.execute('SELECT m.id::text,s.version_id::text,s.source_revision AS revision,v.sha256 FROM activity_scope_sources s JOIN material_sources m ON m.id=s.source_id JOIN material_versions v ON v.id=s.version_id WHERE s.activity_id=%s',(aid,)).fetchone()
        h.saved[T_NAME]=row
        teaching=TeachingCommandInput.model_validate(dict(business_key=str(uuid4()),action='goal',expected_revision=0,expected_goal_version=0,expected_scope_revision=1,body={'goal':'不得跨域'}))
        before=h.snapshot(aid);code=await refused(lambda:h.ledger.apply_teaching_local(aid,teaching),{'stage_conflict'});assert h.snapshot(aid)==before
        atomic_json(h.out/'cross-domain-refusal-resumed.json',dict(aid=aid,code=code,before=before,after=h.snapshot(aid),inherited='P13 model same-key/slot concurrency and strict terminal actual PASS subcases; no new effect'))
        # P14 source change actually committed before a fixture DTO-field typo;
        # retain it, and use one fresh identity for the missing cutoff timestamps.
        h.material(T_NAME);aid=await start_goal(h,[T_NAME],'余额算法最后资格前',{T_NAME:'reference'});q,_=await h.command(aid,'ask',{'mode':'first'})
    else:aid,q=await concurrency(h)
    await citation_cutoffs(h,aid,q);await budgets_retry_capacity(h)


def http_cut(app,folder):
    env=app_environment(app,folder);reserve('listener_start',dict(port=18106,kind='real-response-cut'))
    process=None;identity=None
    with (folder/'api-log.txt').open('w',encoding='utf-8') as stream:
        try:
            process=subprocess.Popen([sys.executable,'-m','tests.fixtures.task106.server'],cwd=ROOT/'backend',env=env,stdout=stream,stderr=stream,creationflags=subprocess.CREATE_NO_WINDOW)
            identity=dict(pid=process.pid,birth_100ns=process_birth(process.pid),command='tests.fixtures.task106.server',port=18106);atomic_json(folder/'owned-api.json',identity)
            until=time.perf_counter()+20
            while True:
                try:
                    with httpx.Client(trust_env=False,timeout=1) as client:
                        if client.get('http://127.0.0.1:18106/health').status_code==200:break
                except httpx.HTTPError:pass
                if process.poll() is not None or time.perf_counter()>until:raise RuntimeError('owned cut API startup failed')
                time.sleep(.1)
            http=HTTP(folder);old=json.loads((EVIDENCE/'runs/P10-http-origin-correct-complete-chain/http-summary.json').read_text(encoding='utf-8'));aid=str(uuid4())
            http.ok('POST','/api/activities',json={'activity_id':aid,'source_ids':[old['materials'][T_NAME]['id']]});http.command(aid,'start',{'goal':None})
            c=dict(schema='interview.command.v1',business_key=str(uuid4()),action='finish',expected_head_revision=1,expected_goal_version=0,expected_scope_revision=1,body={})
            try:http.request('POST',f'/api/activities/{aid}/interview/commands',json=c,headers={**http.headers,'X-TASK106-Cut-After-Commit':'yes'})
            except httpx.RemoteProtocolError as exc:cut=dict(type=type(exc).__name__,message='real incomplete HTTP response after route commit')
            else:raise AssertionError('real HTTP response did not disconnect')
            receipt=http.ok('GET',f'/api/activities/{aid}/interview/commands/{c["business_key"]}');assert receipt['status']=='committed' and receipt['effect_applied']
            replay=http.ok('POST',f'/api/activities/{aid}/interview/commands',json=c);assert replay['record_ids']==receipt['record_ids']
            v=http.ok('GET',f'/api/activities/{aid}/interview/workspace');assert v['head']['phase']=='ended' and v['head']['revision']==2 and v['budget']['requests_reserved']==0
            atomic_json(folder/'actual-http-commit-response-cut.json',dict(activity_id=aid,command=c,cut=cut,GET=receipt,replay=replay,view=v));http.client.close()
        finally:
            if process and process.poll() is None:
                assert identity['birth_100ns']==process_birth(process.pid);process.terminate();process.wait(timeout=10)
            if process:atomic_json(folder/'api-stop.json',dict(identity=identity,exit_code=process.returncode,stopped=process.poll() is not None))


async def fault(h):
    h.material(T_NAME);aid=await start_goal(h,[T_NAME],'余额算法缺失领域引用',{T_NAME:'reference'});q,_=await h.command(aid,'ask',{'mode':'first'})
    permit,outcome=native_outcome(h,aid,q['operation_id']);before=h.snapshot(aid)
    # Save immutable table intact, expose an empty model-reference view as a fault.
    with psycopg.connect(h.admin,autocommit=True) as conn:
        conn.execute('ALTER TABLE interview_records RENAME TO task106_preserved_records')
        conn.execute("CREATE VIEW interview_records AS SELECT * FROM task106_preserved_records WHERE origin<>'model'")
        conn.execute('GRANT SELECT ON interview_records TO retrolume_task106_app')
    try:
        code=await refused(lambda:h.ledger.record_outcome(permit,outcome),{'interview_binding_invalid'})
        atomic_json(h.out/'strict-terminal-missing-domain-ref.json',dict(aid=aid,error_code=code,old007_and_records_retained=True,fault='namespace view excludes model rows; original immutable table intact'))
    finally:
        with psycopg.connect(h.admin,autocommit=True) as conn:
            conn.execute('ALTER VIEW interview_records RENAME TO task106_fault_empty_model_projection')
            conn.execute('ALTER TABLE task106_preserved_records RENAME TO interview_records')
    assert h.snapshot(aid)==before and await h.ledger._transaction(h.ledger._interview_schema_info)=='ready'
    tables=('interview_heads','interview_commands','interview_records')
    with psycopg.connect(h.admin,row_factory=dict_row) as conn:
        funcs=conn.execute("SELECT proname,pg_get_function_identity_arguments(oid) AS args FROM pg_proc WHERE pronamespace='public'::regnamespace AND left(proname,10)='interview_' ORDER BY proname").fetchall()
    renamed=[]
    try:
        with psycopg.connect(h.admin,autocommit=True) as conn:
            for name in tables:conn.execute(sql.SQL('ALTER TABLE {} RENAME TO {}').format(sql.Identifier(name),sql.Identifier('task106_absent_'+name)));renamed.append(('table',name,None))
            for f in funcs:
                conn.execute(sql.SQL('ALTER FUNCTION public.{}({}) RENAME TO {}').format(sql.Identifier(f['proname']),sql.SQL(f['args']),sql.Identifier('task106_absent_'+f['proname'])));renamed.append(('function',f['proname'],f['args']))
            for name in ('retrolume_interview_owner','retrolume_interview_app'):
                conn.execute(sql.SQL('ALTER ROLE {} RENAME TO {}').format(sql.Identifier(name),sql.Identifier('task106_absent_'+name)));renamed.append(('role',name,None))
        schema=await h.ledger._transaction(h.ledger._interview_schema_info);assert schema=='absent',schema
        generic=await h.ledger.read_committed_result(aid,q['operation_id']);assert generic.payload is None,generic.read_status
        facts=await h.ledger.read_activity_facts(aid);assert facts.business_domain=='unknown'
        code=await refused(lambda:h.ledger.require_non_interview(aid),{'interview_schema_not_ready'})
        atomic_json(h.out/'absent-schema-with-int10m-residue.json',dict(schema=schema,activity_id=aid,generic_status=generic.read_status.value,payload_available=False,business_domain=facts.business_domain,write_refusal=code,renamed=renamed,no_drop_or_delete=True))
    finally:
        with psycopg.connect(h.admin,autocommit=True) as conn:
            for kind,name,args in reversed(renamed):
                if kind=='table':query=sql.SQL('ALTER TABLE {} RENAME TO {}').format(sql.Identifier('task106_absent_'+name),sql.Identifier(name))
                elif kind=='role':query=sql.SQL('ALTER ROLE {} RENAME TO {}').format(sql.Identifier('task106_absent_'+name),sql.Identifier(name))
                else:query=sql.SQL('ALTER FUNCTION public.{}({}) RENAME TO {}').format(sql.Identifier('task106_absent_'+name),sql.SQL(args),sql.Identifier(name))
                conn.execute(query)
    assert await h.ledger._transaction(h.ledger._interview_schema_info)=='ready' and h.snapshot(aid)==before
    atomic_json(h.out/'closure-fault-restored.json',dict(S1='ready',old007_and011_unchanged=True,state=before))


def main():
    if sys.platform=='win32':asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    with batch(os.environ.get('RETROLUME_TASK106_CLOSURE_GROUP','P13-closure-concurrency-cutoff-budget-terminal-schema')) as out:
        try:
            admin=start(1);app,denied=runtime(admin);h=Harness(admin,app,out);asyncio.run(normal(h));http_cut(app,out)
        finally:stop(1)
        try:
            admin=start(3);app,denied=runtime(admin);h=Harness(admin,app,out);asyncio.run(fault(h))
        finally:stop(3)
        print('Remaining actual boundaries passed; no old platform changes or refunds')

if __name__=='__main__':main()
