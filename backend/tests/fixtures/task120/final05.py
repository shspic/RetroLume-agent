"""剩余独立矩阵，逐例落盘；旧批准仅只读核证。"""
import hashlib,json,os,time,traceback
from pathlib import Path
from uuid import uuid4
from . import resources as r,setup
from .api_runtime import run,financials,application
from app.capabilities.q_protocol import ROSTER,canonical,digest,raw_digest
HERE=r.EVIDENCE/'finalization-05';SLOT='matrix-final'

def write(name,value):r.write(HERE/name,value)

def safe(exc):
    from .api_runtime import transaction_failure_metadata
    return {'exception_chain':transaction_failure_metadata(exc),'safe_code':str(exc) if type(exc) is RuntimeError else getattr(exc,'code',None),'frames':[{'file':str(Path(x.filename).relative_to(r.ROOT)) if Path(x.filename).is_relative_to(r.ROOT) else 'external','function':x.name,'line':x.lineno} for x in traceback.extract_tb(exc.__traceback__)]}

def case(name,action):
    start=r.utc()
    try:value=action()
    except Exception as exc:
        write(name+'-FAIL-root-'+str(r.state()['active_root'])+'.json',{'case':name,'status':'FAIL','started':start,'ended':r.utc(),**safe(exc)})
        raise
    write(name+'-PASS.json',{'case':name,'status':'PASS','started':start,'ended':r.utc(),'facts':value})
    return value

class Matrix:
    def __init__(self,c):
        self.c=c;self.ledger=c.app.state.activities_ledger;self.file=r.PRIVATE/SLOT/'matrix-progress.json'
        self.state=json.loads(self.file.read_text(encoding='utf-8')) if self.file.exists() else {}
    def save(self,name,value):self.state[name]=value;r.write(self.file,self.state,private=True);return value
    def retain(self,name,value):return self.state[name] if name in self.state else self.save(name,value)
    def head(self,aid):return self.c.request('GET',f'/api/activities/{aid}/interview/workspace')['head']
    def url(self,aid):return f'/api/activities/{aid}/interview/commands'
    def local(self,aid,action,body,name):
        if name+'.done' in self.state:return self.state[name+'.done']
        h=self.head(aid) or {}
        cmd=self.retain(name,{'schema':'interview.command.v2','business_key':str(uuid4()),'action':action,'expected_head_revision':h.get('revision',0),'expected_goal_version':h.get('goal_version',0),'expected_scope_revision':h.get('scope_revision',1),'body':body})
        known=self.c.request('GET',self.url(aid)+'/'+cmd['business_key'],expect=(200,202,404))
        if known.get('status')=='committed':return self.save(name+'.done',known)
        receipt=self.c.request('POST',self.url(aid),cmd)
        if receipt['status']!='committed':raise RuntimeError('matrix_local_not_committed_'+name)
        return self.save(name+'.done',receipt)
    def goal(self,aid,name):return self.local(aid,'start' if not self.head(aid) else 'goal',{'goal':{'target':setup.SAMPLES['inputs']['interview_goal'],'material_roles':[]}},name)
    def retrieve(self,aid,action,name):
        if name+'.done' in self.state:return self.state[name+'.done']
        status=self.c.request('GET',f'/api/activities/{aid}/retrieval/status');h=self.head(aid)
        cmd=self.retain(name,{'business_key':str(uuid4()),'action':action,'expected_scope_revision':h['scope_revision'],'expected_domain_revision':status['domain_revision'],'confirmed':True,**({'query':setup.SAMPLES['inputs']['interview_goal']} if action=='query' else {})})
        url=f'/api/activities/{aid}/retrieval/commands'
        receipt=self.c.request('GET',url+'/'+cmd['business_key'],expect=(200,202,404))
        if not receipt.get('status'):receipt=self.c.request('POST',url,cmd)
        if receipt.get('status')=='terminal':
            from .repair03 import terminal_retrieval
            current=self.c.request('GET',f'/api/activities/{aid}/retrieval/status')
            if not terminal_retrieval(action,receipt,current):raise RuntimeError('matrix_retrieval_unqualified_'+name)
            return self.save(name+'.done',receipt)
        if receipt.get('launch_claimed'):raise RuntimeError('matrix_claimed_query_never_resent')
        rows=self.c.approve(aid,cmd['business_key'])
        for row in rows:r.count('native_business_sessions')
        receipt=self.c.request('POST',url,cmd)
        if receipt.get('terminal_disposition')!='received':raise RuntimeError('matrix_retrieval_failed_'+name+'_'+str(receipt.get('error_code')))
        return self.save(name+'.done',receipt)
    def command(self,aid,name):
        if name in self.state:return self.state[name]
        self.retrieve(aid,'source_index',name+'-index')
        query=self.retrieve(aid,'query',name+'-query');h=self.head(aid)
        return self.retain(name,{'schema':'interview.command.v2','business_key':str(uuid4()),'action':'ask','expected_head_revision':h['revision'],'expected_goal_version':h['goal_version'],'expected_scope_revision':h['scope_revision'],'body':{'mode':'first'},'retrieval_ref':query['retrieval_ref']})
    def prepare(self,aid,name):
        cmd=self.command(aid,name);url=self.url(aid);known=self.c.request('GET',url+'/'+cmd['business_key'],expect=(200,202,404))
        if known.get('launch_claimed') or known.get('status') in ('started','unknown'):raise RuntimeError('matrix_original_claim_never_resent_'+name)
        receipt=self.c.request('POST',url,cmd)
        if receipt['status']!='accepted' or not receipt.get('outbound_approval'):raise RuntimeError('matrix_prepare_not_pending_'+name)
        rows=self.c.approve(aid,cmd['business_key']);return cmd,rows[0]

def bootstrap():
    setup.initial_files(SLOT);setup.migrate(SLOT);setup.environment(SLOT)
    from .transport import install
    install()
    from app.main import create_app
    app=create_app()
    if app.state.data_exit is None:raise RuntimeError('matrix_data_not_ready')
    mapping=setup.seed_sources(app,SLOT);run(setup.bind_root(app,SLOT,mapping))
    with application(SLOT) as c:
        f=Matrix(c)
        for aid in (ROSTER[1],ROSTER[2]):f.goal(aid,'initial-'+aid)
        selection=run(c.app.state.activities_ledger.read_memory_selection(ROSTER[1],include_bodies=False))
        assert selection['selected']
    identity=setup.info(SLOT)
    return {'database':identity['database'],'database_oid':identity['database_oid'],'dataset_id':identity['dataset_id'],'instance_id':identity['instance_id'],'reuse_existing_app_and_snapshot_roles_no_role_mutation':True,'source_count':len(mapping),'fixed_roster':list(ROSTER),'A2_memory_selected':True,'new_container_or_volume':0,'financials':financials(SLOT)}

def scope_diagnose():
    with application(SLOT) as c:
        f=Matrix(c);aid=ROSTER[2];sources=json.loads((r.PRIVATE/SLOT/'sources.json').read_text(encoding='utf-8'))
        entries=[{'source_id':str(sources[a]['id']),'version_id':str(sources[a]['version_id']),'source_revision':sources[a]['revision'],'original_sha256':sources[a]['sha256']} for a in ('N','R')]
        before=f.head(aid);money=financials(SLOT)
        try:changed=f.local(aid,'bind_scope',{'sources':entries,'material_roles':[]},'scope-diagnostic-local')
        finally:
            after=f.head(aid)
            write('scope-diagnostic-persistent-after-root-'+str(r.state()['active_root'])+'.json',{'before':before,'after':after,'financials_before':money,'financials_after':financials(SLOT),'business_key':f.state['scope-diagnostic-local']['business_key']})
        assert after['scope_revision']==before['scope_revision']+1 and money==financials(SLOT)
        return {'before':before,'after':after,'receipt':changed,'real_PG_COMMIT':True,'financials_unchanged':True}

def legacy_parent(f):
    aid=ROSTER[0];name='legacy-first'
    if name+'.done' not in f.state:
        cmd=f.retain(name,{'business_key':str(uuid4()),'goal':setup.SAMPLES['inputs']['numeric_goal'],'confirmed':True})
        url=f'/api/activities/{aid}/learning/first'
        known=f.c.request('GET',f'/api/activities/{aid}/learning/intents/{cmd["business_key"]}?action=first',expect=(200,202,404))
        if known.get('launch_claimed'):raise RuntimeError('legacy_claim_must_be_reconciled')
        pending=f.c.request('POST',url,cmd);f.c.approve(aid,cmd['business_key']);r.count('native_business_sessions')
        got=f.c.request('POST',url,cmd)
        if got['status']!='committed_current':raise RuntimeError('matrix_legacy_parent_not_current')
        f.save(name+'.done',got)
    parent=f.state[name+'.done'];name='legacy-followup'
    if name+'.done' not in f.state:
        cmd=f.retain(name,{'business_key':str(uuid4()),'parent_operation_id':parent['operation_id'],'question':setup.SAMPLES['inputs']['numeric_initial_question'],'confirmed':True})
        url=f'/api/activities/{aid}/learning/followups'
        pending=f.c.request('POST',url,cmd)
        if pending['status']!='awaiting_approval':raise RuntimeError('matrix_followup_not_waiting')
        rows=f.c.approve(aid,cmd['business_key']);f.save(name+'.prepared_id',rows[0]['prepared_id'])
        r.count('native_business_sessions');got=f.c.request('POST',url,cmd)
        if got['status']!='committed_current':raise RuntimeError('matrix_legacy_followup_not_current')
        f.save(name+'.done',got)
    return f.state[name+'.prepared_id']

def permissions():
    import copy,logging
    from app.capabilities.q_context import snapshot,check_instance,validate_provenance
    from app.capabilities.contracts import ModelCallRequest,CallContext,CallStatus,AdmissionDenied
    from app.capabilities.gateway import ControlledModelGateway
    from app.data_exit.q_store import authority_for
    from app.operator.q_request import inspect_request,approve_request
    with application(SLOT) as c:
        f=Matrix(c);legacy_id=legacy_parent(f);aid=ROSTER[1]
        cmd,row=f.prepare(aid,'permissions-model')
        authority=authority_for(f.ledger);row=authority.request(row['prepared_id']);p=row['prepared'];artifact=authority.artifact(row)
        state,ids,derived=run(snapshot(f.ledger,aid));check_instance(authority,f.ledger,state)
        provenance=validate_provenance(authority,artifact['request'],artifact['payload'],state,ids,derived,p['action'],p)
        request=ModelCallRequest.model_validate_json(canonical(artifact['request']))
        service=c.app.state.activity_config.model_service.model_copy(update={'outbound_authorization':authority.reference(row)})
        money=financials(SLOT);qbefore=digest(authority.hub.state()['q'])
        def checkpoint(name,expected,action):
            path=HERE/('permission-'+name+'-PASS.json')
            if path.exists():
                saved=json.loads(path.read_text(encoding='utf-8'))
                if saved['facts']['prepared_id']==p['prepared_id']:return saved['facts']
                raise RuntimeError('permission_saved_identity_changed')
            def perform():
                facts=action()
                assert facts['actual_code']==expected,(name,facts['actual_code'],expected)
                after=financials(SLOT);current=authority.request(p['prepared_id'])
                assert money==after and not current.get('claim') and not current.get('admission') and digest(authority.hub.state()['q'])==qbefore
                return {'prepared_id':p['prepared_id'],'input_request_sha256':p['typed_request_sha256'],'snapshot_sha256':digest(state),'expected_code':expected,**facts,'financials_before':money,'financials_after':after,'claim':current.get('claim'),'admission':current.get('admission'),'Q_state_unchanged':True,'dispatches':0}
            return case('permission-'+name,perform)
        def denied(changed,req_state=state,req_ids=ids,req_derived=derived,binding=p,action=p['action']):
            payload=ControlledModelGateway(service)._build_payload(changed)
            try:validate_provenance(authority,changed.model_dump(mode='json'),payload,req_state,req_ids,req_derived,action,binding)
            except AdmissionDenied as exc:return {'actual_code':str(exc),'boundary':'actual_PG_snapshot_whole_request_provenance','field':getattr(exc,'q_path',None),'changed_request_sha256':digest(changed.model_dump(mode='json')),'provider_bytes_sha256':raw_digest(canonical(payload))}
            raise RuntimeError('unapproved_full_request_allowed')
        for label in ('answer','goal','memory','title'):
            value=json.loads(request.messages[1].content)
            if label=='memory':value['learning_background'][0]['text']='UNAPPROVED_MEMORY'
            elif label=='title':value['context']['catalog'][0]['title']='UNAPPROVED_TITLE'
            elif label=='goal':value['context']['goal_body']['target']='UNAPPROVED_GOAL'
            else:
                actual=next(x for x in state['parents'] if x['record_id']==value['context']['goal_record_id'])
                value['context']['parent_record_refs'].append({'record_id':actual['record_id'],'kind':'answer','body_sha256':actual['body_sha256'],'body':{'text':'UNAPPROVED_ANSWER'}})
            changed=request.model_copy(update={'messages':(request.messages[0],request.messages[1].model_copy(update={'content':canonical(value)}))})
            checkpoint('unapproved-'+label,'q_unapproved_text',lambda changed=changed:denied(changed))
        legacy=authority.request(legacy_id);a=authority.artifact(legacy)
        legacy_request=ModelCallRequest.model_validate_json(canonical(a['request']))
        s,i,d=run(snapshot(f.ledger,ROSTER[0]));v=json.loads(legacy_request.messages[1].content);v['previous_result']+=' UNAPPROVED_HISTORY'
        changed=legacy_request.model_copy(update={'messages':(legacy_request.messages[0],legacy_request.messages[1].model_copy(update={'content':canonical(v)}))})
        checkpoint('unapproved-history','q_unapproved_text',lambda:denied(changed,s,i,d,legacy['prepared'],'followup'))
        checkpoint('foreign-activity-parent','q_parent_unqualified',lambda:denied(legacy_request,state,ids,derived,legacy['prepared'],'followup'))
        from app.activities.repository import PostgresAdmissionLedger
        foreign=PostgresAdmissionLedger(setup.dsn('flow'));foreign_state,_,_=run(snapshot(foreign,ROSTER[0]))
        def other_instance():
            try:check_instance(authority,foreign,foreign_state)
            except AdmissionDenied as exc:return {'actual_code':str(exc),'boundary':'instance_binding','actual_foreign_database_oid':foreign_state['control']['database_oid']}
            raise RuntimeError('foreign_PG_identity_allowed')
        checkpoint('other-existing-instance','q_instance_mismatch',other_instance)
        context=CallContext(activity_id=aid,operation_id=p['operation_id'],executor_id='local-ui',execution_generation=1,scope_revision=p['snapshot']['activity']['scope_revision'])
        class Codes(logging.Handler):
            def __init__(self):super().__init__();self.codes=[]
            def emit(self,record):
                if record.msg=='q_dispatch_rejected code=%s field=%s value_sha256=%s':self.codes.append(record.args[0])
        for label,config,req in [('exact-bytes',service,request.model_copy(update={'messages':(request.messages[0],request.messages[1].model_copy(update={'content':request.messages[1].content+' '}))})),('endpoint',service.model_copy(update={'base_url':'https://api.deepseek.com/not-approved'}),request)]:
            def check(config=config,req=req):
                handler=Codes();logger=logging.getLogger('app.capabilities.q_gateway');logger.addHandler(handler)
                try:result=run(ControlledModelGateway(config,ledger=f.ledger).call(context,req))
                finally:logger.removeHandler(handler)
                assert result.status is CallStatus.REJECTED and result.error_code=='q_authorization_denied' and handler.codes==['q_prepared_changed']
                return {'actual_code':handler.codes[0],'public_code':result.error_code,'boundary':'immutable_prepared_request_before_claim'}
            checkpoint(label,'q_prepared_changed',check)
        def missing():
            path=authority.hub.artifact_path('q-prepared',p['prepared_id']);held=path.with_suffix('.final05-held')
            with authority.policy():
                path.rename(held)
                try:
                    try:run(inspect_request(f.ledger,p['prepared_id']))
                    except FileNotFoundError as exc:
                        assert exc.errno==2
                        return {'actual_code':'FileNotFoundError.2','boundary':'original_artifact_read_after_valid_snapshot','request_returned':False}
                    raise RuntimeError('missing_original_returned_body')
                finally:held.rename(path)
        checkpoint('missing-original','FileNotFoundError.2',missing)
        def duplicate():
            decision=run(approve_request(f.ledger,p['prepared_id'],row['prepared_sha256']));assert decision==row['approval']
            return {'actual_code':'SAME_DECISION_SAME_EVENT_SEQ','event_seq':decision['body']['event_seq'],'approval_id':decision['approval_id']}
        checkpoint('duplicate-approval','SAME_DECISION_SAME_EVENT_SEQ',duplicate)
        write('permissions-summary.json',{'status':'PASS_FOR_LISTED_LIVE_PG_GATES','prepared_id':p['prepared_id'],'live_gates':11,'copied_identity_and_tail_reused':'../validation-04/copied-control-reconciliation.json','readonly_and_deleted_body':'later_final_cases','positive_whole_request_valid':True,'new_real_provider_calls':0})
        return {'prepared_id':p['prepared_id'],'selected_memory_in_actual_request':True,'whole_request':p['typed_request_sha256'],'fees_unchanged':True}

def persistent(aid,key):
    import psycopg
    from psycopg.rows import dict_row
    with psycopg.connect(setup.dsn(SLOT),row_factory=dict_row) as db:
        db.execute('BEGIN READ ONLY')
        command=db.execute('SELECT business_key::text,request_sha256,context_sha256,operation_id,status,launch_claimed,obsolete,effect_applied,before_revision,after_revision FROM interview_commands WHERE activity_id=%s AND business_key=%s',(aid,key)).fetchone()
        head=db.execute('SELECT revision,goal_version,scope_revision,goal_record_id::text,current_question_id::text,current_answer_id::text,current_feedback_id::text,pending_key::text FROM interview_heads WHERE activity_id=%s',(aid,)).fetchone()
        result=None
        if command:
            result=db.execute("SELECT o.state,o.operation_id,o.admission_id::text,r.payload_sha256,encode(sha256(convert_to(r.payload,'UTF8')),'hex') AS actual_sha256 FROM activity_operations o LEFT JOIN activity_operation_results r USING(activity_id,operation_id) WHERE o.activity_id=%s AND o.operation_id=%s",(aid,command['operation_id'])).fetchone()
        return {'command':command,'head':head,'007':result,'backend_pid':db.info.backend_pid}

def fault(operation,mode):
    path=r.PRIVATE/SLOT/'faults.json';value=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    value[operation]=mode;r.write(path,value,private=True)

def dispatch_count(operation):
    return sum(1 for line in (r.EVIDENCE/'events.jsonl').read_text(encoding='utf-8').splitlines() if (x:=json.loads(line)).get('kind')=='synthetic_provider_transport' and x.get('operation_id')==operation)

def ack():
    from app.capabilities.contracts import AdmissionUnavailable
    from app.data_exit.q_store import authority_for
    with application(SLOT) as c:
        f=Matrix(c);authority=authority_for(f.ledger);aid=ROSTER[2]
        cmd=f.command(aid,'ack-accept-claim-model');url=f.url(aid);key=cmd['business_key']
        if not (HERE/'ACK-accepted-COMMIT-PASS.json').exists():
            def accept_test():
                before=financials(SLOT);qbefore=digest(authority.hub.state()['q']);original=f.ledger.accept_interview_command;lost=[]
                async def lose(*args,**kwargs):
                    got=await original(*args,**kwargs)
                    if not lost:
                        lost.append(True);r.event('final05_actual_accept_COMMIT_ACK_lost',business_key=key)
                        raise AdmissionUnavailable('TESTONLY_actual_accept_COMMIT_ACK_lost')
                    return got
                f.ledger.accept_interview_command=lose
                try:response=c.request('POST',url,cmd,expect=(503,))
                finally:f.ledger.accept_interview_command=original
                facts=persistent(aid,key);one=c.request('GET',url+'/'+key);two=c.request('GET',url+'/'+key)
                assert lost==[True] and facts['command']['status']=='accepted' and not facts['command']['launch_claimed'] and facts['007'] is None
                assert one['status']==two['status']=='accepted' and financials(SLOT)==before and digest(authority.hub.state()['q'])==qbefore
                f.save('ACK.accepted',facts)
                return {'business_key':key,'request_sha256':facts['command']['request_sha256'],'persistent':facts,'GETs':2,'GET_zero_actions':True,'financials_before':before,'financials_after':financials(SLOT),'HTTP_status':503,'dispatches':0,'Q_state_unchanged':True}
            case('ACK-accepted-COMMIT',accept_test)
        if not (HERE/'ACK-launch-claim-COMMIT-PASS.json').exists():
            def claim_test():
                before=financials(SLOT);pending=c.request('POST',url,cmd);assert pending['outbound_approval']['state']=='pending'
                row=c.approve(aid,key)[0];original=f.ledger.claim_interview_launch;lost=[]
                async def lose(*args,**kwargs):
                    got=await original(*args,**kwargs)
                    if not lost:
                        lost.append(True);r.event('final05_actual_claim_COMMIT_ACK_lost',business_key=key)
                        raise AdmissionUnavailable('TESTONLY_actual_claim_COMMIT_ACK_lost')
                    return got
                f.ledger.claim_interview_launch=lose
                try:response=c.request('POST',url,cmd,expect=(503,))
                finally:f.ledger.claim_interview_launch=original
                facts=persistent(aid,key);native=r.state()['counts']['native_business_sessions'];qbefore=digest(authority.hub.state()['q'])
                one=c.request('GET',url+'/'+key);two=c.request('GET',url+'/'+key)
                assert lost==[True] and facts['command']['launch_claimed'] and facts['command']['status']=='started' and facts['007'] is None
                assert one['launch_claimed'] and two['launch_claimed'] and one['status']==two['status']=='started'
                assert financials(SLOT)==before and r.state()['counts']['native_business_sessions']==native and digest(authority.hub.state()['q'])==qbefore
                f.save('ACK.claimed',facts)
                return {'business_key':key,'prepared_id':row['prepared_id'],'persistent':facts,'GETs':2,'financials_before':before,'financials_after':financials(SLOT),'native_launches':0,'dispatches':0,'never_POST_again_after_claim':True}
            case('ACK-launch-claim-COMMIT',claim_test)
        # 精确本地放弃已证明无worker的测试pending；不动Q/费用或原claim。
        if 'ack-local-abandon.done' not in f.state:
            before=financials(SLOT);qbefore=digest(authority.hub.state()['q'])
            f.local(aid,'abandon',{'pending_key':key},'ack-local-abandon')
            assert before==financials(SLOT) and qbefore==digest(authority.hub.state()['q'])
        aid=ROSTER[1];cmd=f.state['permissions-model'];key=cmd['business_key'];url=f.url(aid)
        if not (HERE/'ACK-result-COMMIT-PASS.json').exists():
            def result_test():
                row=next(x for x in authority.hub.state()['q']['requests'].values() if x['prepared']['business_key']==key)
                facts=persistent(aid,key);before=financials(SLOT)
                if facts['command']['launch_claimed']:raise RuntimeError('result_ACK_claimed_key_requires_readonly_reconciliation')
                fault(row['prepared']['operation_id'],'commit_ack_lost');r.count('native_business_sessions')
                try:response=c.request('POST',url,cmd)
                finally:write('ACK-result-COMMIT-persistent-root-'+str(r.state()['active_root'])+'.json',{'utc':r.utc(),'business_key':key,'facts':persistent(aid,key),'financials':financials(SLOT)})
                facts=persistent(aid,key);after=financials(SLOT);qbefore=digest(authority.hub.state()['q']);native=r.state()['counts']['native_business_sessions']
                one=c.request('GET',url+'/'+key);two=c.request('GET',url+'/'+key)
                assert facts['command']['launch_claimed'] and facts['command']['status']=='committed' and facts['command']['effect_applied']
                assert facts['007']['state']=='received' and facts['007']['actual_sha256']==facts['007']['payload_sha256']
                assert one['status']==two['status']=='committed' and financials(SLOT)==after and native==r.state()['counts']['native_business_sessions'] and digest(authority.hub.state()['q'])==qbefore
                count=dispatch_count(row['prepared']['operation_id']);assert count==1
                assert after['requests']==before['requests']+1 and after['cost']==before['cost']+250000
                f.save('ACK.result',facts)
                return {'business_key':key,'prepared_id':row['prepared_id'],'persistent':facts,'HTTP_receipt_status':response['status'],'result_COMMIT_ack_lost_after_real_record_outcome':True,'dispatches':count,'GETs':2,'GET_zero_actions':True,'financials_before':before,'financials_after':after,'never_resent':True}
            case('ACK-result-COMMIT',result_test)
        return {'three_separate_checkpoints':True,'keys':[f.state['ack-accept-claim-model']['business_key'],f.state['permissions-model']['business_key']]}

def race(name):
    import threading
    from app.data_exit.q_store import authority_for
    from app.operator.q_request import principal_id,inspect_request
    from app.capabilities.contracts import AdmissionDenied
    from app.data_exit.contracts import DataError
    with application(SLOT) as c:
        f=Matrix(c);aid=ROSTER[1] if name=='memory' else ROSTER[2];base=r.PRIVATE/SLOT
        f.goal(aid,'race-'+name+'-goal')
        cmd,row=f.prepare(aid,'race-'+name+'-model');key=cmd['business_key'];operation=row['prepared']['operation_id'];authority=authority_for(f.ledger)
        before=persistent(aid,key);money=financials(SLOT);fault(operation,'release_gap');tag=hashlib.sha256(operation.encode()).hexdigest()
        ready=base/('gap-ready-'+tag+'.json');release=base/('gap-release-'+tag);outcome={}
        def send():
            try:outcome['receipt']=c.request('POST',f.url(aid),cmd)
            except BaseException as exc:outcome['failure']=safe(exc)
        r.count('native_business_sessions');worker=threading.Thread(target=send,name='TASK120-final05-'+name);worker.start()
        mutation=None;after_mutation=None;mutation_error=None;window=None
        try:
            until=time.monotonic()+18
            while not ready.exists():
                if not worker.is_alive() or time.monotonic()>=until:raise RuntimeError('actual_'+name+'_release_gap_not_observed')
                time.sleep(.01)
            window=json.loads(ready.read_text(encoding='utf-8'));assert window['dispatch_released'] and window['worker_pid']!=os.getpid()
            mutation_started=r.utc()
            if name=='head':mutation=f.goal(aid,'race-head-exclusive-new-goal')
            elif name=='revoke':mutation=authority.revoke(row['prepared_id'],principal_id());assert mutation['state']=='revoked'
            elif name=='scope':
                sources=json.loads((base/'sources.json').read_text(encoding='utf-8'))
                aliases=('N','R','M');entries=[{'source_id':str(sources[a]['id']),'version_id':str(sources[a]['version_id']),'source_revision':sources[a]['revision'],'original_sha256':sources[a]['sha256']} for a in aliases]
                mutation=f.local(aid,'bind_scope',{'sources':entries,'material_roles':[]},'race-scope-exclusive')
            elif name=='source':
                import io
                sources=json.loads((base/'sources.json').read_text(encoding='utf-8'));old=sources['R'];sample=next(x for x in setup.SAMPLES['sources'] if x['alias']=='R');raw=sample['text'].encode('utf-8')
                refs=c.app.state.data_exit.references;prepared=refs.prepare_reference(raw_digest(raw),len(raw),source_id=str(old['id']))
                with refs.acquire_shared(prepared) as pin:
                    original=c.app.state.originals.put(io.BytesIO(raw),max_bytes=5*1024**2,reference_pin=pin)
                    changed=c.app.state.materials.save(source_id=str(old['id']),expected_version=str(old['version_id']),filename=sample['filename'],format=sample['filename'].rsplit('.',1)[1],sha256=original.sha256,size=original.size,reference_pin=pin,prepared_ids=prepared)
                assert changed['revision']==old['revision']+1
                mutation={'before':old,'after':changed,'same_frozen_bytes':True}
            elif name=='memory':
                from app.memory.contracts import MemoryCommandInput
                from app.memory.service import MemoryService
                selected=run(f.ledger.read_memory_selection(aid,include_bodies=False))['entries'][0]
                preview=run(f.ledger.preview_memory_change(selected['memory_id'],selected['revision'],'revoke'))
                value=f.retain('race-memory-exclusive',{'business_key':str(uuid4()),'memory_id':selected['memory_id'],'expected_revision':selected['revision'],'action':'revoke','body':{'impact_token':preview['impact_token'],'confirm_revoke':True,'purge_memory_content':True}})
                mutation=run(MemoryService(f.ledger).submit_command(MemoryCommandInput.model_validate(value)))
            else:raise RuntimeError('closed_race_name')
            after_mutation=persistent(aid,key)
            write('race-'+name+'-mutation-COMMIT-root-'+str(r.state()['active_root'])+'.json',{'utc':r.utc(),'started':mutation_started,'actor_pid':os.getpid(),'actor_thread':threading.get_ident(),'worker':window,'before':before,'after_mutation':after_mutation,'mutation':mutation})
        except BaseException as exc:
            mutation_error=exc
            write('race-'+name+'-mutation-ERROR-persistent-root-'+str(r.state()['active_root'])+'.json',{'utc':r.utc(),'failure':safe(exc),'persistent':persistent(aid,key),'financials':financials(SLOT)})
        finally:
            release.write_text('释放本次合成响应',encoding='utf-8');worker.join(20)
            write('race-'+name+'-final-persistent-root-'+str(r.state()['active_root'])+'.json',{'utc':r.utc(),'facts':persistent(aid,key),'financials':financials(SLOT),'worker_stopped':not worker.is_alive(),'HTTP_outcome':outcome})
        if worker.is_alive():raise RuntimeError('race_worker_not_stopped')
        if mutation_error is not None:raise mutation_error
        if 'failure' in outcome:raise RuntimeError('race_HTTP_outcome_failure_'+name)
        facts=persistent(aid,key);after=financials(SLOT);native=r.state()['counts']['native_business_sessions']
        assert facts['007']['state']=='received' and facts['007']['actual_sha256']==facts['007']['payload_sha256']
        assert facts['head']==after_mutation['head'],'late_result_advanced_invalidated_head'
        assert after['requests']==money['requests']+1 and after['cost']==money['cost']+250000 and dispatch_count(operation)==1
        try:inspection=run(inspect_request(f.ledger,row['prepared_id']))
        except (DataError,AdmissionDenied) as exc:inspection={'request_available':False,'denial':getattr(exc,'code',str(exc))}
        assert not inspection.get('request_available')
        one=c.request('GET',f.url(aid)+'/'+key);assert financials(SLOT)==after and r.state()['counts']['native_business_sessions']==native
        proof={'activity_id':aid,'business_key':key,'operation_id':operation,'prepared_id':row['prepared_id'],'barrier':window,'mutation':mutation,'mutation_actor_pid':os.getpid(),'mutation_actor_thread':threading.get_ident(),'persistent_before':before,'persistent_after_mutation':after_mutation,'persistent_final':facts,'late_head_unchanged':True,'financials_before':money,'financials_after':after,'007_preserved':True,'one_dispatch':True,'request_body_closed':True,'GET_zero_actions':True,'worker_stopped':True,'inspection':inspection}
        # 只清理本例业务pending。Q claim、不可变007和费用仍保留。
        if facts['command']['status']=='unknown' and name!='memory':
            qbefore=digest(authority.hub.state()['q'])
            f.local(aid,'abandon',{'pending_key':key},'race-'+name+'-explicit-local-abandon')
            assert financials(SLOT)==after and digest(authority.hub.state()['q'])==qbefore
            proof['local_abandon_receipt']=f.state['race-'+name+'-explicit-local-abandon.done']
        f.save('race-'+name+'.done',proof)
        return proof

def memory_reconcile():
    import psycopg
    from psycopg.rows import dict_row
    from app.data_exit.q_store import authority_for
    from app.operator.q_request import inspect_request
    from app.capabilities.contracts import AdmissionDenied
    mutation=json.loads((HERE/'race-memory-mutation-COMMIT-root-35.json').read_text(encoding='utf-8'))
    final=json.loads((HERE/'race-memory-final-persistent-root-35.json').read_text(encoding='utf-8'))
    with application(SLOT) as c:
        f=Matrix(c);cmd=f.state['race-memory-model'];aid=ROSTER[1];key=cmd['business_key'];facts=persistent(aid,key);money=financials(SLOT)
        assert mutation['mutation']['status']=='committed' and mutation['mutation']['purge_state_now']=='done' and final['worker_stopped']
        assert mutation['worker']['dispatch_released'] and mutation['worker']['worker_pid']!=mutation['actor_pid']
        assert final['facts']['head']==mutation['after_mutation']['head']==facts['head']
        assert final['facts']['007']==facts['007'] and facts['007']['state']=='received' and facts['007']['payload_sha256']==facts['007']['actual_sha256']
        assert facts['command']['status']=='unknown' and facts['command']['launch_claimed'] and dispatch_count(facts['command']['operation_id'])==1
        authority=authority_for(f.ledger);row=next(x for x in authority.hub.state()['q']['requests'].values() if x['prepared']['business_key']==key)
        try:run(inspect_request(f.ledger,row['prepared_id']))
        except AdmissionDenied as exc:denial=str(exc)
        else:raise RuntimeError('revoked_memory_request_body_returned')
        assert denial=='q_activity_or_memory_mismatch'
        with psycopg.connect(setup.dsn(SLOT),row_factory=dict_row) as db:
            db.execute('BEGIN READ ONLY')
            memory=db.execute('SELECT state,revision,purge_state,purged_at IS NOT NULL AS purged,(SELECT count(*) FROM learning_memory_bodies b WHERE b.memory_id=h.memory_id) AS body_rows FROM learning_memories h WHERE memory_id=%s',(mutation['mutation']['memory_id'],)).fetchone()
            costs=db.execute('SELECT count(*) AS operations,COALESCE(sum(reserved_cost_microunits),0) AS reserved_cost FROM activity_operations WHERE activity_id=%s',(aid,)).fetchone()
        assert memory['state']=='revoked' and memory['purge_state']=='done' and memory['purged'] and memory['body_rows']==0
        current=next(x for x in money['activities'] if x['id']==aid);at35=next(x for x in final['financials']['activities'] if x['id']==aid)
        assert current['requests_reserved']==at35['requests_reserved']==costs['operations'] and current['cost_reserved_microunits']==at35['cost_reserved_microunits']==costs['reserved_cost']
        before=digest(authority.hub.state()['q']);native=r.state()['counts']['native_business_sessions'];one=c.request('GET',f.url(aid)+'/'+key)
        assert one['status']=='unknown' and financials(SLOT)==money and digest(authority.hub.state()['q'])==before and native==r.state()['counts']['native_business_sessions']
        return {'original_barrier_and_COMMIT':'race-memory-mutation-COMMIT-root-35.json','original_result':'race-memory-final-persistent-root-35.json','persistent':facts,'memory':memory,'operator_denial':denial,'fees_retained':costs,'GET_zero_actions':True,'dispatches':1,'no_resend':True,'business_UNKNOWN_retained':True,'local_abandon_denied_due_revoked_dependency_expected_no_requalification':True,'root35_FAIL_retained':True,'no_fresh_live_financial_before_snapshot_was_saved_in_root35':True,'immutable_operation_reservations_reconciled_instead':True}

def deleted_body():
    from app.data_exit.q_store import authority_for
    from app.operator.q_request import inspect_request
    from app.capabilities.contracts import AdmissionDenied
    with application(SLOT) as c:
        f=Matrix(c);sources=json.loads((r.PRIVATE/SLOT/'sources.json').read_text(encoding='utf-8'));sid=str(sources['R']['id']);current=c.app.state.materials.get(sid);before=financials(SLOT)
        preview=c.request('POST',f'/api/data/materials/{sid}/deletion-preview',{'expected_revision':current['revision']})
        cmd=f.retain('final-R-deletion',{'business_key':str(uuid4()),'expected_revision':current['revision'],'impact_sha256':preview['impact_sha256'],'confirm':True})
        receipt=c.request('POST',f'/api/data/materials/{sid}/deletions',cmd)
        denied=c.request('GET',f'/api/materials/{sid}/content',expect=(404,409,410))
        assert next(x['text'] for x in setup.SAMPLES['sources'] if x['alias']=='R') not in canonical(denied) and financials(SLOT)==before
        command=f.state['race-source-model'];authority=authority_for(f.ledger);row=next(x for x in authority.hub.state()['q']['requests'].values() if x['prepared']['business_key']==command['business_key'])
        try:run(inspect_request(f.ledger,row['prepared_id']))
        except AdmissionDenied as exc:code=str(exc)
        else:raise RuntimeError('deleted_source_private_artifact_returned')
        assert code=='q_source_invalid'
        return {'source_id':sid,'request':cmd,'receipt':receipt,'content_GET_denied':True,'operator_request_body_denial':code,'private_prepared_id':row['prepared_id'],'financials_before':before,'financials_after':financials(SLOT),'physical_cleanup_not_overclaimed':receipt.get('state')}

def freeze(c,key):
    from app.data_exit.q_store import authority_for
    from app.capabilities.q_context import snapshot,check_instance
    from app.capabilities.contracts import AdmissionDenied
    from app.operator.q_request import inspect_request
    from app.data_exit.contracts import DataError
    f=Matrix(c);authority=authority_for(f.ledger);row=next(x for x in authority.hub.state()['q']['requests'].values() if x['prepared']['business_key']==key)
    inspection=run(inspect_request(f.ledger,row['prepared_id']));assert inspection['request_available'] and not row.get('claim')
    before=financials(SLOT);context=c.app.state.data_exit.context()
    with authority.policy():
        lease=run(c.app.state.data_exit.maintenance.drain_for_readonly_switch(context.generation,time.monotonic()+20));lease.close()
    state,_,_=run(snapshot(f.ledger,ROSTER[0]))
    try:check_instance(authority,f.ledger,state)
    except AdmissionDenied as exc:code=str(exc)
    else:raise RuntimeError('readonly_instance_allowed')
    try:run(inspect_request(f.ledger,row['prepared_id']))
    except (AdmissionDenied,DataError) as exc:body_code=getattr(exc,'code',str(exc))
    else:raise RuntimeError('readonly_request_body_returned')
    after=c.app.state.data_exit.context().public()
    assert code=='q_instance_mismatch' and body_code=='q_instance_mismatch' and after['read_only'] and not authority.request(row['prepared_id']).get('claim') and financials(SLOT)==before
    proof={'status':'PASS','before_context':context.public(),'after_context':after,'before_request_available':True,'prepared_id':row['prepared_id'],'business_key':key,'actual_PG_mode':state['control']['state']['mode'],'instance_denial':code,'request_body_denial':body_code,'claim':None,'financials_before':before,'financials_after':financials(SLOT),'permanent_readonly_not_reopened':True}
    write('readonly-actual-PG-body-closed.json',proof);return proof

def readonly_ui():
    import shutil,subprocess
    from app.preview.process import birth
    number=r.state()['active_root'];folder=r.PRIVATE/SLOT/('readonly-UI-'+str(number));folder.mkdir(exist_ok=False)
    with application(SLOT) as c:
        f=Matrix(c);parent=f.state['legacy-followup.done']['operation_id'];fact=run(f.ledger.read_committed_result(ROSTER[0],parent));assert fact.read_status.value=='committed_current'
        spec={'project':str(r.ROOT),'origin':c.base,'activity_id':ROSTER[0],'parent_operation':parent,'question':setup.SAMPLES['inputs']['numeric_initial_question'],'profile':str(folder/'browser'),'handshake':str(folder),'proof':str(HERE/('UI-readonly-root-'+str(number)+'.json'))}
        r.write(folder/'spec.json',spec,private=True);r.memory_gate('browser');r.count('browser_starts');env=os.environ.copy();env['RETROLUME_TASK120_UI_SPEC']=str(folder/'spec.json')
        with (HERE/('UI-readonly-root-'+str(number)+'.log')).open('wb') as log:
            proc=subprocess.Popen([shutil.which('node'),str(r.ROOT/'frontend/tests/task120-final05-readonly.mjs')],cwd=r.ROOT/'frontend',env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            r.event('final05_browser_node_started',pid=proc.pid,birth=birth(proc.pid));ordinal=1;until=time.monotonic()+260
            try:
                while proc.poll() is None:
                    if time.monotonic()>=until:raise RuntimeError('readonly_UI_deadline')
                    path=folder/f'request-{ordinal}.json'
                    if path.exists():
                        v=json.loads(path.read_text(encoding='utf-8'));assert set(v)=={'ordinal','kind','activity_id','business_key'} and v['ordinal']==ordinal and v['activity_id']==ROSTER[0]
                        try:
                            if v['kind']=='approve':c.approve(ROSTER[0],v['business_key']);answer={'status':'APPROVED'}
                            elif v['kind']=='freeze':answer={'status':'COMPLETED','facts':freeze(c,v['business_key'])}
                            else:raise RuntimeError('closed_readonly_UI_request')
                        except Exception as exc:answer={'status':'FAILED',**safe(exc)};write('readonly-UI-driver-failure.json',answer)
                        r.write(folder/f'reply-{ordinal}.json',answer,private=True);ordinal+=1
                    time.sleep(.02)
            finally:
                if proc.poll() is None:proc.terminate()
                proc.wait(timeout=8)
        if proc.returncode:raise RuntimeError('readonly_UI_assertion_failed')
        return {'proof':Path(spec['proof']).name,'actual_readonly':'readonly-actual-PG-body-closed.json','scope':'DataContext plus real view switch; isolated namespace and DataContext guards not claimed'}

def final_financials():
    before=json.loads((HERE/'old-financial-readonly-baseline.json').read_text(encoding='utf-8'))['instances']
    now={slot:financials(slot) for slot in ('flow','budget-01','budget-02',SLOT)}
    assert all(now[s]==before[s] for s in before)
    write('financial-final-separated.json',{'utc':r.utc(),'instances':now,'old_three_exactly_unchanged':True,'separate_instances_not_summed':True,'real_provider_calls':0,'actual_fee_microunits':0})
    return {'old_three_exactly_unchanged':True,'matrix':{'requests':now[SLOT]['requests'],'cost':now[SLOT]['cost']}}

def reconcile_final():
    import psycopg
    from psycopg.rows import dict_row
    from app.data_exit.control import ControlHub
    from app.data_exit.q_store import QAuthority
    from app.data_exit.contracts import DataError
    base=r.PRIVATE/SLOT;progress=json.loads((base/'matrix-progress.json').read_text(encoding='utf-8'));hub=ControlHub(base/'control');control=hub.state();q=control['q']
    sources=json.loads((base/'sources.json').read_text(encoding='utf-8'));sid=str(sources['R']['id']);memory_key=progress['race-memory-model']['business_key'];memory_mutation=json.loads((HERE/'race-memory-mutation-COMMIT-root-35.json').read_text(encoding='utf-8'));mid=memory_mutation['mutation']['memory_id']
    with psycopg.connect(setup.dsn(SLOT),row_factory=dict_row) as db:
        db.execute('BEGIN READ ONLY')
        mode=db.execute('SELECT public.data_state() AS state').fetchone()['state']
        source=db.execute('SELECT id::text,current_version::text,revision FROM material_sources WHERE id=%s',(sid,)).fetchone()
        tombstones=db.execute("SELECT count(*) AS n FROM data_tombstones WHERE entity_kind='source' AND entity_id=%s",(sid,)).fetchone()['n']
        memory=db.execute('SELECT state,revision,purge_state,purged_at IS NOT NULL AS purged,(SELECT count(*) FROM learning_memory_bodies b WHERE b.memory_id=h.memory_id) AS body_rows FROM learning_memories h WHERE memory_id=%s',(mid,)).fetchone()
        costs=db.execute('SELECT count(*) AS operations,COALESCE(sum(reserved_cost_microunits),0)::bigint AS reserved_cost FROM activity_operations WHERE activity_id=%s',(ROSTER[1],)).fetchone()
    assert mode['mode']=='frozen' and control['fence']['state']=='frozen'
    assert tombstones==1 and source['current_version'] is None
    assert memory['state']=='revoked' and memory['purge_state']=='done' and memory['purged'] and memory['body_rows']==0
    facts=persistent(ROSTER[1],memory_key);original=json.loads((HERE/'race-memory-final-persistent-root-35.json').read_text(encoding='utf-8'));mutation=memory_mutation
    assert facts['head']==original['facts']['head']==mutation['after_mutation']['head'] and facts['007']==original['facts']['007']
    assert facts['007']['state']=='received' and facts['007']['actual_sha256']==facts['007']['payload_sha256'] and dispatch_count(facts['command']['operation_id'])==1
    current=next(x for x in financials(SLOT)['activities'] if x['id']==ROSTER[1]);at35=next(x for x in original['financials']['activities'] if x['id']==ROSTER[1])
    assert current['requests_reserved']==at35['requests_reserved']==costs['operations'] and current['cost_reserved_microunits']==at35['cost_reserved_microunits']==costs['reserved_cost']
    write('K2-memory-persistent-reconciled.json',{'status':'PASS_FOR_ORIGINAL_K2_AND_PURGE_FACTS','original_COMMIT':'race-memory-mutation-COMMIT-root-35.json','original_result':'race-memory-final-persistent-root-35.json','root35_failed_only_at_unnecessary_abandon_after_invariants':True,'original_facts':facts,'memory':memory,'fees_retained':costs,'worker_and_actor':{'worker':mutation['worker'],'actor_pid':mutation['actor_pid'],'actor_thread':mutation['actor_thread']},'immutable_007_and_head_preserved':True,'one_dispatch_no_resend':True,'original_UNKNOWN_retained':True,'original_live_before_financial_not_saved':True,'limits':'current direct PG reconciliation plus original trace proves prior invariants; no new delivery or requalification claimed'})
    jobs=[{k:v.get(k) for k in ('job_id','kind','state','revision','error_code','business_key','counts')} for v in control['jobs'].values() if v.get('kind')=='source_delete']
    try:QAuthority(hub)
    except DataError as exc:code=exc.code
    else:raise RuntimeError('frozen_Q_root_reopened')
    write('readonly-new-authority-denial.json',{'actual_code':code,'expected_code':'q_normal_root_required','boundary':'new_QAuthority_rejects_frozen_normal_root','PG_mode':mode['mode'],'hub_fence_state':control['fence']['state']})
    assert code=='q_normal_root_required'
    before=financials(SLOT)
    with application(SLOT,reconciliation_only=True) as c:
        denied=c.request('GET',f'/api/materials/{sid}/content',expect=(404,409,410),browser_read=True)
        assert next(x['text'] for x in setup.SAMPLES['sources'] if x['alias']=='R') not in canonical(denied)
        capabilities=c.request('GET','/api/data/capabilities',browser_read=True)
        assert capabilities['read_only']
    assert before==financials(SLOT)
    write('deleted-source-body-GET-checkpoint.json',{'status':'PASS_FOR_THIS_GET','source':source,'tombstone_count':tombstones,'response':denied,'fees_unchanged':True,'read_only':capabilities['read_only']})
    readonly_ui=json.loads((HERE/'UI-readonly-root-36.json').read_text(encoding='utf-8'));delayed=readonly_ui['delayed'];key=str(__import__('uuid').UUID(delayed['path'].rsplit('/',1)[-1]))
    assert delayed['receipt']['outbound_approval']['can_continue']
    row=next(x for x in q['requests'].values() if x['prepared']['business_key']==key);assert not row.get('claim') and not row.get('admission')
    write('readonly-actual-PG-body-closed-reconciled.json',{'status':'PASS_PERSISTENT_READONLY_BOUNDARY','PG':mode,'hub_fence':control['fence'],'pre_freeze_actual_approved_GET':'UI-readonly-root-36.json','prepared_id':row['prepared_id'],'business_key':key,'actual_QAuthority_denial':code,'claim':None,'admission':None,'read_only_capability':capabilities['read_only'],'financials_unchanged':True,'no_second_freeze_or_thaw':True,'root36_followup_snapshot_failed_at_correct_root_guard_not_freeze_COMMIT':True,'UI_late_guard_NOT_PASSED':True})
    write('deleted-source-body-reconciled.json',{'status':'PASS_PERSISTENT_TOMBSTONE_AND_BODY_CLOSURE','source':source,'tombstone_count':tombstones,'original_actual_DELETE_HTTP_200':'../root-36-batch-02-http-timeline.json','content_GET_with_normal_browser_auth_and_no_nonbrowser_Origin':denied,'jobs':jobs,'request_body_closes_at_frozen_Q_root':code,'fees_unchanged':True,'no_repeated_deletion':True,'root36_FAIL_retained':True})
    return {'memory_purge_confirmed':True,'source_tombstone_confirmed':True,'frozen_mode_confirmed':True,'Q_root_denied':code,'never_replayed_business':True}

def scope_removal():
    import psycopg
    from psycopg.rows import dict_row
    with application(SLOT) as c:
        f=Matrix(c);aid=ROSTER[2];before=f.head(aid);money=financials(SLOT)
        sources=json.loads((r.PRIVATE/SLOT/'sources.json').read_text(encoding='utf-8'))
        entries=[{'source_id':str(sources[a]['id']),'version_id':str(sources[a]['version_id']),'source_revision':sources[a]['revision'],'original_sha256':sources[a]['sha256']} for a in ('N','R')]
        with psycopg.connect(setup.dsn(SLOT),row_factory=dict_row) as db:
            db.execute('BEGIN READ ONLY')
            rights=db.execute("SELECT current_user,has_table_privilege(current_user,'public.activity_scope_sources','DELETE') AS delete_allowed").fetchone()
            old_scope=db.execute('SELECT source_id::text,version_id::text,source_revision FROM activity_scope_sources WHERE activity_id=%s ORDER BY source_id',(aid,)).fetchall()
        assert not rights['delete_allowed']
        h=f.head(aid)
        cmd=f.retain('scope-removal-not-authorized-fix',{'schema':'interview.command.v2','business_key':str(uuid4()),'action':'bind_scope','expected_head_revision':h['revision'],'expected_goal_version':h['goal_version'],'expected_scope_revision':h['scope_revision'],'body':{'sources':entries,'material_roles':[]}})
        c.request('POST',f.url(aid),cmd,expect=(503,))
        fact=persistent(aid,cmd['business_key'])
        with psycopg.connect(setup.dsn(SLOT),row_factory=dict_row) as db:
            db.execute('BEGIN READ ONLY')
            new_scope=db.execute('SELECT source_id::text,version_id::text,source_revision FROM activity_scope_sources WHERE activity_id=%s ORDER BY source_id',(aid,)).fetchall()
        assert fact['command'] is None and old_scope==new_scope and before==f.head(aid) and money==financials(SLOT)
        write('scope-removal-blocker.json',{'status':'BLOCKED_REQUIRES_PERSISTENT_PERMISSION_CHANGE','original_requirement_not_passed':True,'sqlstate':'42501','table':'public.activity_scope_sources','statement':'DELETE WHERE activity_id AND source_id','application_role':rights,'business_key':cmd['business_key'],'persistent_command':fact['command'],'before_scope':old_scope,'after_scope':new_scope,'head_unchanged':True,'fees_unchanged':True,'grant_or_DDL_not_changed':True,'addition_and_version_update_verified_separately':'scope-diagnostic-PASS.json','required_adoption':'least privilege scope deletion or trusted scoped replacement function plus schema/profile review; outside current permission boundary'})

def ui_driver(c,value):
    from app.data_exit.q_store import authority_for
    kind=value['kind'];aid=value['activity_id'];f=Matrix(c)
    if kind=='native_attempt':r.count('native_business_sessions');return {'status':'COMPLETED'}
    if kind=='head':
        before=f.head(aid);result=f.goal(aid,'UI-head-'+value['business_key']);after=f.head(aid)
    elif kind=='scope':
        sources=json.loads((r.PRIVATE/SLOT/'sources.json').read_text(encoding='utf-8'))
        h=f.head(aid);current=c.request('GET',f'/api/activities/{aid}/interview/workspace')['sources'];present={x['source_id'] for x in current}
        new=next(x for x in sources.values() if str(x['id']) not in present)
        entries=[{k:x[k] for k in ('source_id','version_id','source_revision','original_sha256')} for x in current]+[{'source_id':str(new['id']),'version_id':str(new['version_id']),'source_revision':new['revision'],'original_sha256':new['sha256']}]
        before=h;result=f.local(aid,'bind_scope',{'sources':entries,'material_roles':[]},'UI-scope-'+value['business_key']);after=f.head(aid)
    else:raise RuntimeError('final05_closed_UI_driver')
    money=financials(SLOT)
    row=next(x for x in authority_for(f.ledger).hub.state()['q']['requests'].values() if x['prepared']['business_key']==value['business_key'])
    assert not row.get('claim')
    facts={'status':'COMPLETED','before_head':before,'after_head':after,'receipt':result,'financials':money,'original_prepared_id':row['prepared_id'],'original_claim':row.get('claim')}
    write('UI-'+kind+'-mutation-'+value['business_key']+'.json',facts)
    return facts

def ui():
    import shutil,subprocess
    from app.preview.process import birth
    number=r.state()['active_root'];folder=r.PRIVATE/SLOT/('UI-'+str(number));folder.mkdir(exist_ok=False)
    with application(SLOT) as c:
        f=Matrix(c);f.retrieve(ROSTER[2],'source_index','UI-final-scope-index')
        identity=setup.info(SLOT)
        passed=HERE/'UI-head-scope-root-33.json'
        kinds=['scope'] if passed.exists() and any(x['name']=='actual-head-late-approved-GET' and x['status']=='PASS' for x in json.loads(passed.read_text(encoding='utf-8')).get('cases',[])) else ['head','scope']
        spec={'project':str(r.ROOT),'origin':c.base,'activity_id':ROSTER[2],'goal':setup.SAMPLES['inputs']['interview_goal'],'namespace':identity['dataset_id']+'.'+identity['instance_id']+'.0','kinds':kinds,'profile':str(folder/'browser'),'handshake':str(folder),'proof':str(HERE/('UI-head-scope-root-'+str(number)+'.json')),'screenshot':str(HERE/('UI-head-scope-root-'+str(number)+'.png'))}
        r.write(folder/'spec.json',spec,private=True);r.memory_gate('browser');r.count('browser_starts')
        env=os.environ.copy();env['RETROLUME_TASK120_UI_SPEC']=str(folder/'spec.json')
        with (HERE/('UI-root-'+str(number)+'.log')).open('wb') as log:
            proc=subprocess.Popen([shutil.which('node'),str(r.ROOT/'frontend/tests/task120-final05-ui.mjs')],cwd=r.ROOT/'frontend',env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            r.event('final05_browser_node_started',pid=proc.pid,birth=birth(proc.pid));ordinal=1;until=time.monotonic()+270
            try:
                while proc.poll() is None:
                    if time.monotonic()>=until:raise RuntimeError('final05_UI_deadline')
                    path=folder/f'request-{ordinal}.json'
                    if path.exists():
                        v=json.loads(path.read_text(encoding='utf-8'))
                        assert set(v)=={'ordinal','kind','activity_id','business_key'} and v['ordinal']==ordinal and v['activity_id']==ROSTER[2]
                        before=financials(SLOT)
                        try:
                            if v['kind']=='approve':c.approve(v['activity_id'],v['business_key']);assert before==financials(SLOT);answer={'status':'APPROVED'}
                            else:answer=ui_driver(c,v)
                        except Exception as exc:answer={'status':'FAILED',**safe(exc)};write('UI-driver-failure-root-'+str(number)+'.json',answer)
                        r.write(folder/f'reply-{ordinal}.json',answer,private=True);ordinal+=1
                    time.sleep(.02)
            finally:
                if proc.poll() is None:proc.terminate()
                proc.wait(timeout=8)
        if proc.returncode:raise RuntimeError('final05_UI_assertion_failed')
        proof=json.loads(Path(spec['proof']).read_text(encoding='utf-8'));assert proof['status']=='PASS'
        return {'proof':Path(spec['proof']).name,'cases':proof['cases'],'formal_dist_unchanged':True,'assets':proof['assets']}

def reconcile():
    import psycopg
    from psycopg.rows import dict_row
    base=r.PRIVATE/'budget-02'
    prior=json.loads((base/'c02-races.json').read_text(encoding='utf-8'))
    mutation=prior['scope-mutation'];model=prior['scope-model'];aid=ROSTER[2]
    until=time.monotonic()+25
    while True:
        try:db=psycopg.connect(setup.dsn('budget-02'),row_factory=dict_row,connect_timeout=2);break
        except psycopg.Error:
            if time.monotonic()>=until:raise
            time.sleep(.2)
    with db:
        db.execute('BEGIN READ ONLY')
        row=db.execute('SELECT activity_id::text,business_key::text,action,request_sha256,status,launch_claimed,effect_applied,before_revision,after_revision,goal_version,scope_revision,operation_id,error_code FROM interview_commands WHERE activity_id=%s AND business_key=%s',(aid,mutation['business_key'])).fetchone()
        head=db.execute('SELECT revision,goal_version,scope_revision,goal_record_id::text,current_question_id::text,pending_key::text FROM interview_heads WHERE activity_id=%s',(aid,)).fetchone()
        scope=db.execute('SELECT source_id::text,version_id::text,source_revision FROM activity_scope_sources WHERE activity_id=%s ORDER BY source_id',(aid,)).fetchall()
        activity=db.execute('SELECT scope_revision,requests_reserved,cost_reserved_microunits FROM activities WHERE id=%s',(aid,)).fetchone()
        command=db.execute('SELECT business_key::text,status,launch_claimed,obsolete,effect_applied,operation_id,request_sha256 FROM interview_commands WHERE activity_id=%s AND business_key=%s',(aid,model['business_key'])).fetchone()
        result=db.execute('SELECT o.state,o.operation_id,r.payload_sha256,encode(sha256(convert_to(r.payload,\'UTF8\')),\'hex\') AS actual_sha256 FROM activity_operations o LEFT JOIN activity_operation_results r USING(activity_id,operation_id) WHERE o.activity_id=%s AND o.operation_id=%s',(aid,command['operation_id'])).fetchone()
    expected_before={k:mutation[k] for k in ('expected_head_revision','expected_goal_version','expected_scope_revision')}
    no_commit=row is None and head['scope_revision']==mutation['expected_scope_revision'] and activity['scope_revision']==mutation['expected_scope_revision']
    committed=row is not None and row['status']=='committed' and row['request_sha256']==digest(mutation)
    assert command['launch_claimed'] and result['state']=='received' and result['actual_sha256']==result['payload_sha256']
    write('old-scope-503-reconciliation.json',{'utc':r.utc(),'database':'retrolume_task120_budget_02','application_role_only':True,'READ_ONLY_transaction':True,'business_key':mutation['business_key'],'request_sha256':digest(mutation),'expected_before':expected_before,'mutation_command':row,'head':head,'activity':activity,'scope':scope,'model_command':command,'007':result,'conclusion':'NOT_COMMITTED' if no_commit else 'COMMITTED' if committed else 'INSUFFICIENT_EVIDENCE','basis':'exact command absent plus original scope revision retained' if no_commit else 'exact command/status/request hash','no_resend':True,'no_old_grant_extension':True})
    assert no_commit or committed
    # 仅元数据读取两个旧未领取意图，不创建QAuthority或更新旧journal。
    from app.data_exit.control import ControlHub
    q=ControlHub(r.PRIVATE/'flow/control').state()['q']
    keys=('9d478f34-cfef-4753-8b73-fb8a4d5f7631','fa4d574c-e47b-4db6-832b-56ae55289582')
    write('old-unclaimed-keys.json',{'utc':r.utc(),'old_grant_expired':True,'new_POST':0,'keys':[{'business_key':key,'requests':[{'prepared_id':x['prepared_id'],'claim':x.get('claim'),'admission':x.get('admission'),'state':x.get('state'),'expires_at':x.get('approval',{}).get('expires_at')} for x in q['requests'].values() if x['prepared']['business_key']==key]} for key in keys]})
    write('old-financial-readonly-baseline.json',{'utc':r.utc(),'instances':{s:financials(s) for s in ('flow','budget-01','budget-02')},'no_new_outbound':True})

def execute(mode):
    if mode=='reconcile':return reconcile()
    if mode=='bootstrap':return case('matrix-bootstrap',bootstrap)
    if mode=='scope_diagnose':return case('scope-diagnostic',scope_diagnose)
    if mode=='permissions':return case('permissions',permissions)
    if mode=='ack':return case('ACK-matrix',ack)
    if mode in ('head','revoke','scope','source','memory'):return case('K2-'+mode,lambda:race(mode))
    if mode=='scope_removal':return scope_removal()
    if mode=='ui':return case('UI-head-scope',ui)
    if mode=='memory_reconcile':return case('K2-memory-reconciled',memory_reconcile)
    if mode=='delete':return case('deleted-source-body',deleted_body)
    if mode=='readonly':return case('readonly-UI',readonly_ui)
    if mode=='financials':return case('final-financials',final_financials)
    if mode=='reconcile_final':return case('final-persistent-reconciliation',reconcile_final)
    raise RuntimeError('final05_mode_not_implemented_'+mode)
