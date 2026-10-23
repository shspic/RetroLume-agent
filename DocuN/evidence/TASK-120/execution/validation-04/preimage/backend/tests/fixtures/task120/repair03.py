"""Repair03 finite checks and normal chains; original resources only."""
import json,sys,time,re
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from . import resources as r,setup
from .api_runtime import run,financials,application
from app.capabilities.q_protocol import ROSTER,canonical,digest
HERE=r.EVIDENCE/'repair-03'
OLD_I='430a4e36-08e1-411f-a73e-097506a6278b'
OLD_T='3b561488-07b7-4d6d-8b98-05e793c96749'

def write(name,value):
    target=HERE/name
    if target.exists():
        old=target.read_bytes();new=json.dumps(value,ensure_ascii=False,indent=2).encode()
        if old!=new:
            folder=HERE/'history';folder.mkdir(exist_ok=True)
            (folder/(target.stem+'-before-root-'+str(r.state()['active_root'])+'-'+str(time.monotonic_ns())+target.suffix)).write_bytes(old)
    r.write(target,value)

def terminal_retrieval(action,receipt,status=None):
    if receipt.get('status')!='terminal':return False
    if receipt.get('terminal_disposition')=='received':return True
    return bool(action=='source_index' and receipt.get('terminal_disposition')=='cache_ready' and status
        and status.get('ready') and status.get('fragments',0)>0 and status.get('cached_fragments')==status['fragments'])
def safe_error(exc):
    code=getattr(exc,'code',None)
    return {'type':type(exc).__name__,'code':code if isinstance(code,str) and re.fullmatch(r'[a-zA-Z0-9_.-]{1,96}',code) else None,'sqlstate':getattr(exc,'sqlstate',None)}

def diagnose():
    from .transport import install
    from app.main import create_app
    from app.data_exit.q_store import authority_for
    from app.capabilities.contracts import ModelCallRequest
    from app.learning.teaching_adapter import validate_teaching_request
    from app.learning.contracts import read_document,normalize_input
    import psycopg
    from psycopg.rows import dict_row
    install();setup.environment('flow',include_admin=False)
    until=time.monotonic()+15
    while True:
        try:
            with psycopg.connect(setup.dsn('flow'),connect_timeout=2) as c:c.execute('SELECT 1').fetchone()
            break
        except psycopg.Error:
            if time.monotonic()>until:raise RuntimeError('repair03_PG_readiness_timeout') from None
            time.sleep(.2)
    app=create_app()
    ledger=app.state.activities_ledger;authority=authority_for(ledger)
    if not app.state.q_readiness['available']:raise RuntimeError('repair03_original_assembly_unavailable')
    before=financials('flow');journal_before=__import__('hashlib').sha256((r.PRIVATE/'flow/control/journal.bin').read_bytes()).hexdigest()
    result={'readonly':True,'new_business_POST':0,'SUP':0,'admit_mark_record_claim':0,'checks':{},'exceptions':[]}
    def trace(frame,event,arg):
        if event=='exception':
            filename=Path(frame.f_code.co_filename)
            if filename.is_relative_to(r.ROOT/'backend/app'):
                exc=arg[1];record={**safe_error(exc),'file':filename.relative_to(r.ROOT).as_posix(),'function':frame.f_code.co_name,'line':frame.f_lineno}
                if record not in result['exceptions']:result['exceptions'].append(record)
        return trace
    async def validate():
        row=next(x for x in authority.hub.state()['q']['requests'].values() if x['prepared']['business_key']==OLD_T)
        request=ModelCallRequest.model_validate(authority.artifact(row)['request'])
        p=row['prepared'];context=SimpleNamespace(activity_id=p['activity_id'],scope_revision=request.teaching_profile.scope_revision,operation_id=p['operation_id'])
        from app.data_exit.q_store import is_read_method
        for old in (True,False):
            with patch('app.data_exit.q_store.is_read_method',side_effect=lambda name:False if old and name=='_teaching_read_snapshot' else is_read_method(name)):
                previous=sys.gettrace();sys.settrace(trace)
                try:
                    async with authority.async_policy(shared=True):code=await validate_teaching_request(context,request,ledger)
                finally:sys.settrace(previous)
            result['checks']['teaching_before' if old else 'teaching_after']={'returned_code':code,'request_sha256':digest(request.model_dump(mode='json')),'business_key':OLD_T}
        result['checks']['teaching_read_fix_verified']=result['checks']['teaching_before']['returned_code']=='teaching_validation_unavailable' and result['checks']['teaching_after']['returned_code'] is None
    until=time.monotonic()+15
    while True:
        try:
            with psycopg.connect(setup.dsn('flow'),connect_timeout=2) as c:c.execute('SELECT 1').fetchone()
            break
        except psycopg.Error:
            if time.monotonic()>until:raise RuntimeError('repair03_PG_readiness_timeout') from None
            time.sleep(.2)
    run(validate())
    progress=json.loads((r.PRIVATE/'flow/flow-progress.json').read_text(encoding='utf-8'))
    parent_op=progress['legacy-first.done']['operation_id']
    parent=run(ledger.read_committed_result(ROSTER[2],parent_op))
    document=json.loads(parent.payload)['value'];profile,output=read_document(document,activity_id=ROSTER[2],operation_id=parent_op)
    result['checks']['legacy_parent']={'operation_id':parent_op,'kind':parent.kind,'read_status':parent.read_status.value,'output_kind':output.kind,'payload_sha256':parent.payload_sha256,'segment_count':len(output.segments),'profile':profile.profile}
    for name,text in [('followup',setup.SAMPLES['inputs']['numeric_initial_question']),('focus',setup.SAMPLES['inputs']['numeric_goal'])]:
        result['checks'][name+'_input_canonical']=normalize_input(text)==text
    async def guards():
        async with await psycopg.AsyncConnection.connect(setup.dsn('flow'),row_factory=dict_row) as c:
            await c.execute('BEGIN READ ONLY');await c.execute("SET LOCAL statement_timeout='5s'")
            a=await (await c.execute('SELECT * FROM activities WHERE id=%s',(ROSTER[2],))).fetchone()
            for name,fn in [('legacy_domain',lambda:ledger._interview_require_non_domain(c,ROSTER[2])),
                ('html_schema',lambda:ledger._html_assert_schema(c)),
                ('html_parent',lambda:ledger._html_parent_locked(c,a,{'kind':'learning','operation_id':parent_op,'payload_sha256':parent.payload_sha256,'segment_index':0}))]:
                try:
                    async with c.transaction():value=await fn()
                except Exception as exc:result['checks'][name]={'status':'REFUSED',**safe_error(exc)}
                else:result['checks'][name]={'status':'PASS','context_sha256':digest(value) if value else None}
            for table,fields in [('teaching_heads','revision,goal_version,goal_record_id::text,pending_business_key::text'),('interview_heads','revision,goal_version,goal_record_id::text,pending_key::text')]:
                result[table]=await (await c.execute(f'SELECT activity_id::text,{fields} FROM {table} ORDER BY activity_id')).fetchall()
            for table in ('teaching_commands','interview_commands'):
                result[table]=await (await c.execute(f'SELECT activity_id::text,business_key::text,action,status,operation_id FROM {table} ORDER BY created_at')).fetchall()
    run(guards())
    result['financials_unchanged']=financials('flow')==before
    result['journal_unchanged']=__import__('hashlib').sha256((r.PRIVATE/'flow/control/journal.bin').read_bytes()).hexdigest()==journal_before
    write('readonly-diagnosis.json',__import__('app.data_exit.codec',fromlist=['plain']).plain(result))
    if not result['financials_unchanged'] or not result['journal_unchanged']:raise RuntimeError('readonly_diagnostic_changed_authority')

def execute(mode):
    if mode=='diagnose':return diagnose()
    if mode=='core':return core()
    if mode=='memory':return memory()
    if mode=='ui':return flow_tail()
    if mode=='fences':
        tail=json.loads((HERE/'flow-tail-result.json').read_text(encoding='utf-8'))
        if not tail['outcomes'].get('interview',{}).get('status','').startswith('PASS'):raise RuntimeError('repair03_UI_interview_positive_required_before_head_scope_fences')
        from .ui import run_ui
        return run_ui(mode='fences')
    if mode=='races':
        if not (HERE/'selected-memory-positive.json').exists():raise RuntimeError('repair03_memory_positive_required_before_races')
        from .recovery_races import run_races
        return run_races()
    raise ValueError('repair03_closed_mode')

class Flow:
    def __init__(self,c,slot):
        self.c=c;self.slot=slot;self.path=r.PRIVATE/slot/'r03-progress.json'
        self.state=json.loads(self.path.read_text(encoding='utf-8')) if self.path.exists() else {}
    def save(self,name,value):self.state[name]=value;r.write(self.path,self.state,private=True);return value
    def retain(self,name,value):return self.state[name] if name in self.state else self.save(name,value)
    def body(self,name,value):
        from uuid import uuid4
        return self.retain(name,dict(business_key=str(uuid4()),**value))
    def head(self,aid,domain):return self.c.request('GET',f'/api/activities/{aid}/{domain}/workspace')['head']
    def local(self,aid,domain,action,body,name):
        if name+'.done' in self.state:return self.state[name+'.done']
        h=self.head(aid,domain) or {};interview=domain=='interview'
        value={'action':action,'expected_goal_version':h.get('goal_version',0),'expected_scope_revision':1,'body':body}
        value['expected_head_revision' if interview else 'expected_revision']=h.get('revision',0)
        if interview:value['schema']='interview.command.v2'
        command=self.body(name,value);receipt=self.c.request('POST',f'/api/activities/{aid}/{domain}/commands',command)
        if receipt['status']!='committed':raise RuntimeError('repair03_local_not_committed_'+name)
        return self.save(name+'.done',receipt)
    def goal(self,aid,domain,text,name):
        if name+'.parent-proof' in self.state:return self.state[name+'.parent-proof']
        before=self.head(aid,domain)
        self.local(aid,domain,'start' if domain=='interview' and not before else 'goal',
            {'goal':{'target':text,'material_roles':[]}} if domain=='interview' else {'goal':text},name)
        after=self.head(aid,domain)
        if after['revision']!=(before or {}).get('revision',0)+1 or after['goal_version']!=(before or {}).get('goal_version',0)+1 or after['goal_record_id']==(before or {}).get('goal_record_id'):raise RuntimeError('repair03_goal_no_new_parent_'+name)
        return self.save(name+'.parent-proof',{'before':before,'after':after})
    def retrieve(self,aid,action,name,query=None):
        path=f'/api/activities/{aid}/retrieval/commands'
        if name not in self.state:
            status=self.c.request('GET',f'/api/activities/{aid}/retrieval/status')
            self.body(name,{'action':action,'expected_scope_revision':1,'expected_domain_revision':status['domain_revision'],'confirmed':True,**({'query':query} if query else {})})
        command=self.state[name];receipt=self.c.request('GET',path+'/'+command['business_key'],expect=(200,202,404))
        if not receipt.get('status'):receipt=self.c.request('POST',path,command)
        if receipt.get('status')=='terminal':
            status=self.c.request('GET',f'/api/activities/{aid}/retrieval/status') if receipt.get('terminal_disposition')=='cache_ready' else None
            if not terminal_retrieval(action,receipt,status):raise RuntimeError('repair03_retained_retrieval_not_qualified')
            return self.save(name+'.done',receipt)
        if receipt.get('launch_claimed') or receipt.get('launch_claimed_at') or receipt.get('status') in ('unknown','launch_claimed'):raise RuntimeError('repair03_retained_claim_not_resent')
        approval=receipt.get('outbound_approval')
        if not approval:
            receipt=self.c.request('POST',path,command);approval=receipt.get('outbound_approval')
        if not approval:raise RuntimeError('repair03_retrieval_approval_absent')
        before=financials(self.slot);native=r.state()['counts']['native_business_sessions']
        self.c.request('GET',path+'/'+command['business_key'])
        if financials(self.slot)!=before or r.state()['counts']['native_business_sessions']!=native:raise RuntimeError('repair03_GET_side_effect')
        if not approval['can_continue']:self.c.approve(aid,command['business_key'])
        if financials(self.slot)!=before:raise RuntimeError('repair03_approval_financial_side_effect')
        r.count('native_business_sessions');receipt=self.c.request('POST',path,command)
        if receipt.get('terminal_disposition')!='received':raise RuntimeError('repair03_query_not_received_'+str(receipt.get('error_code')))
        return self.save(name+'.done',receipt)
    def model(self,aid,domain,action,body,name,ref=None):
        path=f'/api/activities/{aid}/{domain}/commands'
        if name not in self.state:
            h=self.head(aid,domain);value={'action':action,'expected_goal_version':h['goal_version'],'expected_scope_revision':1,'body':body}
            value['expected_head_revision' if domain=='interview' else 'expected_revision']=h['revision']
            if domain=='interview':value['schema']='interview.command.v2'
            if ref:value['retrieval_ref']=ref
            self.body(name,value)
        command=self.state[name]
        if name+'.done' in self.state:
            receipt=self.c.request('GET',path+'/'+command['business_key'])
            if receipt['status']!='committed':raise RuntimeError('repair03_saved_COMMIT_not_reconciled')
            return receipt
        receipt=self.c.request('GET',path+'/'+command['business_key'],expect=(200,202,404))
        if receipt.get('launch_claimed') or receipt.get('launch_claimed_at') or receipt.get('status') in ('unknown','started'):raise RuntimeError('repair03_old_model_never_resent')
        receipt=self.c.request('POST',path,command)
        if receipt['status']!='accepted' or not receipt.get('outbound_approval'):raise RuntimeError('repair03_model_prepare_not_pending')
        before=financials(self.slot);self.c.request('GET',path+'/'+command['business_key']);self.c.approve(aid,command['business_key'])
        if financials(self.slot)!=before:raise RuntimeError('repair03_model_GET_approval_financial_side_effect')
        r.count('native_business_sessions');receipt=self.c.request('POST',path,command)
        fact=run(self.c.app.state.activities_ledger.read_committed_result(aid,receipt['operation_id']))
        if receipt['status']!='committed' or fact.read_status.value!='committed_current' or not fact.payload:raise RuntimeError('repair03_model_missing_domain_007_'+domain+'_'+str(receipt.get('error_code')))
        self.save(name+'.007',{'operation_id':receipt['operation_id'],'payload_sha256':fact.payload_sha256,'read_status':fact.read_status.value})
        return self.save(name+'.done',receipt)

def abandon_originals(f):
    from app.data_exit.q_store import authority_for
    ledger=f.c.app.state.activities_ledger;authority=authority_for(ledger)
    for domain,aid,key in [('interview',ROSTER[1],OLD_I),('teaching',ROSTER[2],OLD_T)]:
        name='abandon-'+domain
        if name+'.done' in f.state:
            if domain=='teaching' and not (HERE/(name+'-witness.json')).exists():
                view=run(ledger.read_teaching_command(aid,key));row=view['command']
                if row['abandoned_at'] is None or (view['head'] or {}).get('pending_business_key') is not None:raise RuntimeError('repair03_teaching_abandon_not_effective')
                qrow=next(x for x in authority.hub.state()['q']['requests'].values() if x['prepared']['business_key']==key)
                write(name+'-witness.json',{'old_business_key':key,'original_UNKNOWN_status_retained':row['status'],'abandoned_at':str(row['abandoned_at']),'pending_cleared':True,'Q_claim_retained':qrow.get('claim'),'Q_admission_retained':qrow.get('admission'),'financials_after':financials(f.slot),'resend_count':0,'initial_assertion_failed_before_this_readonly_reconciliation':True})
            continue
        money=financials(f.slot);q=authority.hub.state()['q'];before=f.head(aid,domain)
        path=f'/api/activities/{aid}/{domain}/commands/'+key;old=f.c.request('GET',path)
        if old['status']!='unknown':raise RuntimeError('repair03_original_unknown_state_changed')
        f.local(aid,domain,'abandon',{'pending_key' if domain=='interview' else 'target_business_key':key},name)
        after=f.c.request('GET',path)
        ended=after['status']=='abandoned' if domain=='interview' else run(ledger.read_teaching_command(aid,key))['command']['abandoned_at'] is not None
        if not ended or financials(f.slot)!=money or authority.hub.state()['q']!=q:raise RuntimeError('repair03_abandon_changed_Q_or_finances')
        write(name+'-witness.json',{'old_business_key':key,'before_command':old,'after_command':after,'before_head':before,'after_head':f.head(aid,domain),'Q_claim_operation_finances_unchanged':True,'resend_count':0,'old_semantic_slot_retained':True})

def legacy_and_html(f):
    from app.learning.contracts import read_document
    aid=ROSTER[2];ledger=f.c.app.state.activities_ledger
    old=json.loads((r.PRIVATE/'flow/flow-progress.json').read_text(encoding='utf-8'))
    parent_op=old['legacy-first.done']['operation_id'];parent=run(ledger.read_committed_result(aid,parent_op))
    _,output=read_document(json.loads(parent.payload)['value'],activity_id=aid,operation_id=parent_op)
    if parent.read_status.value!='committed_current' or output.kind!='answer' or not output.segments:raise RuntimeError('repair03_legacy_parent_ineligible')
    name='legacy-followup';body=f.body(name,{'parent_operation_id':parent_op,'question':setup.SAMPLES['inputs']['numeric_initial_question'],'confirmed':True})
    if name+'.done' not in f.state:
        url=f'/api/activities/{aid}/learning/followups';value=f.c.request('POST',url,body)
        if value['status']!='awaiting_approval' or not value.get('outbound_approval'):raise RuntimeError('repair03_legacy_not_pending')
        before=financials('flow');f.c.request('GET',f'/api/activities/{aid}/learning/intents/{body["business_key"]}?action=followup');f.c.approve(aid,body['business_key'])
        if financials('flow')!=before:raise RuntimeError('repair03_legacy_approval_reserved')
        r.count('native_business_sessions');value=f.c.request('POST',url,body)
        if value['status']!='committed_current':raise RuntimeError('repair03_legacy_not_COMMIT_'+value['status'])
        f.save(name+'.done',value)
    if 'html.done' not in f.state:
        caps=f.c.request('GET',f'/api/activities/{aid}/html/capabilities')
        if not caps['available']:raise RuntimeError('repair03_original_html_host_unavailable')
        body=f.body('html',{'parent':{'kind':'learning','operation_id':parent_op,'payload_sha256':parent.payload_sha256,'segment_index':0},'focus':setup.SAMPLES['inputs']['numeric_goal'],'expected_config_sha256':caps['config_sha256'],'confirmed':True})
        url=f'/api/activities/{aid}/html/commands';value=f.c.request('POST',url,body)
        if value.get('status')!='accepted' or not value.get('outbound_approval'):raise RuntimeError('repair03_html_not_pending')
        before=financials('flow');f.c.request('GET',url+'/'+body['business_key']);f.c.approve(aid,body['business_key'])
        if financials('flow')!=before:raise RuntimeError('repair03_HTML_approval_reserved')
        r.count('native_business_sessions');value=f.c.request('POST',url,body)
        if value['status']!='terminal' or value['terminal_disposition']!='succeeded' or value['read_status']!='current':raise RuntimeError('repair03_HTML_not_COMMIT_'+str(value.get('error_code')))
        f.save('html.done',value)
    write('legacy-html-positive.json',{'status':'PASS','original_first_inherited':parent_op,'first_answer_parent_verified':True,'followup':f.state['legacy-followup.done'],'html':f.state['html.done'],'preview_creates_starts':[0,0]})

def core():
    gate=json.loads((HERE/'readonly-diagnosis.json').read_text(encoding='utf-8'))
    if not gate['checks']['teaching_read_fix_verified'] or any(gate['checks'][x]['status']!='PASS' for x in ('legacy_domain','html_schema','html_parent')):raise RuntimeError('repair03_cause_gate_not_closed')
    with application('flow') as c:
        f=Flow(c,'flow');abandon_originals(f)
        outcomes={}
        for name,action in [('teaching',lambda:teaching(f)),('interview',lambda:interview(f)),('legacy_html',lambda:legacy_and_html(f))]:
            try:action()
            except Exception as exc:
                outcomes[name]={'status':'FAIL',**safe_error(exc),'safe_code':str(exc) if type(exc) is RuntimeError else None}
                r.update(lambda b:b['failures'].append({'root':r.state()['active_root'],'case':'repair03-'+name,'receipt':'repair-03/core-result.json'}))
            else:outcomes[name]={'status':'PASS'}
            write('core-result.json',{'outcomes':outcomes,'actual_PG_HTTP_SUP':True,'provider_fee_preview_Git':0})
    if any(x['status']!='PASS' for x in outcomes.values()):raise RuntimeError('repair03_core_partial')

def teaching(f):
    aid=ROSTER[2]
    f.goal(aid,'teaching',setup.SAMPLES['inputs']['concept_goal'],'t-concept-goal')
    f.goal(aid,'teaching',setup.SAMPLES['inputs']['numeric_goal'],'t-numeric-goal')
    f.retrieve(aid,'source_index','t-index')
    ref=f.retrieve(aid,'query','t-query',setup.SAMPLES['inputs']['numeric_goal'])['retrieval_ref']
    plan=f.model(aid,'teaching','plan',{'confirmed':True},'t-plan',ref)
    proposal=next(x['record_id'] for x in plan['record_ids'] if x['kind']=='path_proposal')
    f.local(aid,'teaching','accept_path',{'proposal_record_id':proposal},'t-path')
    head=f.head(aid,'teaching')
    exercise_ref=f.retrieve(aid,'query','t-exercise-query',setup.SAMPLES['inputs']['numeric_goal'])['retrieval_ref']
    f.model(aid,'teaching','exercise',{'confirmed':True,'path_record_id':head['path_record_id'],'node_id':head['node_id'],'purpose':'initial'},'t-exercise',exercise_ref)
    write('teaching-positive.json',{'status':'PASS','activity_id':aid,'plan':f.state['t-plan.007'],'exercise':f.state['t-exercise.007'],'query_business_key':f.state['t-query']['business_key'],'query_result_sha256':f.state['t-query.done']['retrieval_ref']['result_sha256']})

def interview(f,prefix='i'):
    aid=ROSTER[1];f.goal(aid,'interview',setup.SAMPLES['inputs']['interview_goal'],prefix+'-new-goal')
    f.retrieve(aid,'source_index',prefix+'-index')
    ref=f.retrieve(aid,'query',prefix+'-query',setup.SAMPLES['inputs']['interview_goal'])['retrieval_ref']
    f.model(aid,'interview','ask',{'mode':'first'},prefix+'-ask',ref)
    write(f.slot+'-interview-positive.json',{'status':'PASS','activity_id':aid,'model':f.state[prefix+'-ask.007'],'query_business_key':f.state[prefix+'-query']['business_key'],'query_result_sha256':f.state[prefix+'-query.done']['retrieval_ref']['result_sha256']})

def memory():
    from .recovery import bootstrap_memory
    if not (r.EVIDENCE/'budget-02-selected-memory-binding.json').exists():bootstrap_memory()
    with application('budget-02') as c:
        f=Flow(c,'budget-02')
        # Original root18 stopped its worker. Its claimed key is GET-only;
        # explicitly end this local pending, then create a new real goal parent.
        if 'i-ask' in f.state and 'i-ask.done' not in f.state and 'memory-abandon-root18.done' not in f.state:
            old=f.state['i-ask']['business_key'];url=f'/api/activities/{ROSTER[1]}/interview/commands/'+old
            before=c.request('GET',url);money=financials('budget-02')
            if before['status']=='unknown':f.local(ROSTER[1],'interview','abandon',{'pending_key':old},'memory-abandon-root18')
            after=c.request('GET',url)
            if after['status']!='abandoned' or financials('budget-02')!=money:raise RuntimeError('repair03_memory_unknown_not_locally_closed')
            write('memory-unknown-root18-retained.json',{'before':before,'after':after,'never_resent':True,'finances_unchanged':True})
        interview(f,'i2')
        from app.data_exit.q_store import authority_for
        authority=authority_for(c.app.state.activities_ledger);command=f.state['i2-ask'];aid=ROSTER[1]
        row=next(x for x in authority.hub.state()['q']['requests'].values() if x['prepared']['business_key']==command['business_key'])
        request=authority.artifact(row)['request'];value=json.loads(request['messages'][1]['content'])
        background=value['learning_background'];selection=run(c.app.state.activities_ledger.read_memory_selection(aid,include_bodies=True))
        if len(background)!=1 or background[0]['text']!=setup.SAMPLES['inputs']['memory_body'] or background[0]['memory_id']!=selection['entries'][0]['memory_id']:raise RuntimeError('repair03_selected_memory_not_in_actual_request')
        write('selected-memory-positive.json',{'status':'PASS','prepared_id':row['prepared_id'],'007':f.state['i2-ask.007'],'full_request_sha256':digest(request),'memory_id':background[0]['memory_id'],'frozen_text_sha256':__import__('hashlib').sha256(background[0]['text'].encode()).hexdigest(),'real_PG_SUP':True})

def boundaries(c):
    if not (HERE/'flow-interview-positive.json').exists():raise RuntimeError('repair03_interview_positive_required_before_boundaries')
    import psycopg
    with psycopg.connect(setup.dsn('flow')) as db:
        unknown=db.execute("SELECT count(*) FROM interview_commands WHERE activity_id=%s AND status='unknown' AND execution_kind='model'",(ROSTER[1],)).fetchone()[0]
    if unknown:raise RuntimeError('repair03_new_UI_UNKNOWN_must_not_be_reissued')
    from .pg_boundaries import probe_approved,run_ack_and_gap
    f=Flow(c,'flow');aid=ROSTER[1]
    f.goal(aid,'interview',setup.SAMPLES['inputs']['interview_goal'],'b-new-goal')
    ref=f.retrieve(aid,'query','b-query',setup.SAMPLES['inputs']['interview_goal'])['retrieval_ref']
    c.after_approval=lambda rows:probe_approved(c,rows)
    try:f.model(aid,'interview','ask',{'mode':'first'},'b-result-ACK-model',ref)
    finally:c.after_approval=None
    write('result-ACK-positive.json',{'status':'PASS','007':f.state['b-result-ACK-model.007'],'real_COMMIT_ACK_loss':True,'GET_recovered':True})
    run_ack_and_gap(c)

def flow_tail():
    from .ui import run_ui
    outcomes={};gates={'teaching':'teaching-positive.json','interview':'flow-interview-positive.json','legacy_html':'legacy-html-positive.json'}
    with application('flow') as c:
        for mode,gate in gates.items():
            if not (HERE/gate).exists():outcomes[mode]={'status':'SKIPPED_NO_BACKEND_POSITIVE'};continue
            try:run_ui(c,mode)
            except Exception as exc:
                outcomes[mode]={'status':'FAIL',**safe_error(exc),'safe_code':str(exc) if type(exc) is RuntimeError else None}
                r.update(lambda b:b['failures'].append({'root':b['active_root'],'case':'repair03-UI-'+mode,'receipt':'repair-03/flow-tail-result.json'}))
            else:outcomes[mode]={'status':'PASS_FOR_LISTED_FLOW'}
            write('flow-tail-result.json',{'outcomes':outcomes,'remaining_late_fences_not_inherited_as_pass':['head','scope','namespace','DataContext']})
        try:boundaries(c)
        except Exception as exc:
            outcomes['boundaries']={'status':'FAIL',**safe_error(exc),'safe_code':str(exc) if type(exc) is RuntimeError else None}
            r.update(lambda b:b['failures'].append({'root':b['active_root'],'case':'repair03-boundaries','receipt':'repair-03/flow-tail-result.json'}))
        else:outcomes['boundaries']={'status':'PASS_FOR_LISTED_GATES_AND_ACK_K2'}
        write('flow-tail-result.json',{'outcomes':outcomes,'remaining_late_fences_not_inherited_as_pass':['head','scope','namespace','DataContext']})
    if any(not x['status'].startswith('PASS') for x in outcomes.values()):raise RuntimeError('repair03_flow_tail_partial')
