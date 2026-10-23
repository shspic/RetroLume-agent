"""Actual original-PG negative gates, acknowledgement faults and K2 window."""
import copy,hashlib,json,os,shutil,threading,time
from pathlib import Path
from uuid import uuid4
from . import resources as r,setup
from .api_runtime import run,financials

def probe_approved(client,rows):
    if getattr(client,'_task120_probe_done',False):return
    row=next((x for x in rows if x['prepared']['domain']=='interview'),None)
    if row is None:return
    from app.capabilities.q_protocol import canonical,digest,raw_digest,ROSTER
    from app.capabilities.q_context import snapshot,check_instance,validate_provenance
    from app.capabilities.contracts import ModelCallRequest,CallContext,CallStatus,AdmissionDenied
    from app.capabilities.gateway import ControlledModelGateway
    from app.data_exit.q_store import authority_for,QAuthority
    from app.data_exit.control import ControlHub
    from app.data_exit.contracts import DataError
    from app.data_exit.files import private_file
    from app.operator.q_request import inspect_request,approve_request
    ledger=client.app.state.activities_ledger;authority=authority_for(ledger);row=authority.request(row['prepared_id']);p=row['prepared']
    base=financials('flow');artifact=authority.artifact(row)
    request=ModelCallRequest.model_validate_json(canonical(artifact['request']))
    service=client.app.state.activity_config.model_service.model_copy(update={'outbound_authorization':authority.reference(row)})
    state,ids,derived=run(snapshot(ledger,p['activity_id']));check_instance(authority,ledger,state)
    validate_provenance(authority,request.model_dump(mode='json'),artifact['payload'],state,ids,derived,p['action'],p)
    authority.manifest.check_model(request,artifact['payload'])
    cases=[]
    for label,text in [('answer','UNAPPROVED_ANSWER'),('history','UNAPPROVED_HISTORY'),('memory','UNAPPROVED_MEMORY'),('title','UNAPPROVED_TITLE')]:
        value=json.loads(request.messages[1].content)
        if label=='memory':value['learning_background']=[{'text':text}]
        elif label=='title':value['context']['catalog'][0]['title']=text
        else:value['context']['goal_body']['target']=text
        changed=request.model_copy(update={'messages':(request.messages[0],request.messages[1].model_copy(update={'content':canonical(value)}))})
        payload=ControlledModelGateway(service)._build_payload(changed)
        try:validate_provenance(authority,changed.model_dump(mode='json'),payload,state,ids,derived,p['action'],p)
        except AdmissionDenied as exc:
            cases.append({'case':'unapproved_'+label,'denied':str(exc),'typed_request_sha256':digest(changed.model_dump(mode='json')),'provider_bytes_sha256':raw_digest(canonical(payload))})
        else:raise RuntimeError('actual_PG_provenance_allowed_'+label)
    context=CallContext(activity_id=p['activity_id'],operation_id=p['operation_id'],executor_id='local-ui',execution_generation=1,scope_revision=1)
    changed=request.model_copy(update={'messages':(request.messages[0],request.messages[1].model_copy(update={'content':request.messages[1].content+' '}))})
    for label,configuration,body in [('exact_bytes',service,changed),('endpoint',service.model_copy(update={'base_url':'https://api.deepseek.com/not-approved'}),request)]:
        result=run(ControlledModelGateway(configuration,ledger=ledger).call(context,body))
        if result.status is not CallStatus.REJECTED:raise RuntimeError('actual_gateway_negative_not_rejected_'+label)
        if authority.request(row['prepared_id']).get('claim'):raise RuntimeError('negative_gate_consumed_original_approval')
        cases.append({'case':label,'actual_gateway_status':result.status.value,'code':result.error_code,'claim_not_created':True})
    # A different existing PG instance remains foreign even in this same CID.
    from app.activities.repository import PostgresAdmissionLedger
    foreign=PostgresAdmissionLedger(setup.dsn('budget-01'))
    foreign_state,_,_=run(snapshot(foreign,ROSTER[0]))
    try:check_instance(authority,foreign,foreign_state)
    except AdmissionDenied as exc:cases.append({'case':'actual_other_existing_PG_instance','denied':str(exc),'actual_database_oid':foreign_state['control']['database_oid']})
    else:raise RuntimeError('foreign_actual_PG_instance_allowed')
    # Full other-activity typed request, never a fabricated parent or ID string.
    foreign_row=next(x for x in authority.hub.state()['q']['requests'].values() if x['prepared']['domain']=='learning' and x['prepared']['activity_id']!=p['activity_id'])
    other=authority.artifact(foreign_row)
    try:validate_provenance(authority,other['request'],other['payload'],state,ids,derived,foreign_row['prepared']['action'],foreign_row['prepared'])
    except AdmissionDenied as exc:cases.append({'case':'actual_foreign_activity_full_request','denied':str(exc),'foreign_operation_id':foreign_row['prepared']['operation_id']})
    else:raise RuntimeError('foreign_actual_request_allowed')
    # Inspect does not fall back to a copied artifact when the original is gone.
    path=authority.hub.artifact_path('q-prepared',row['prepared_id']);held=path.with_suffix('.c01-held')
    with authority.policy():
        path.rename(held)
        try:
            try:run(inspect_request(ledger,row['prepared_id']))
            except (DataError,OSError):cases.append({'case':'original_artifact_missing','inspect_denied':True})
            else:raise RuntimeError('missing_artifact_returned_request')
        finally:held.rename(path)
    # Copies retain their old binding and cannot become authority. Damage only
    # new private copies; the live journal and root bytes remain untouched.
    for kind in ('copied_instance','journal_tail'):
        folder=r.PRIVATE/'negative-copies'/str(uuid4());folder.mkdir(parents=True);private_file(folder,directory=True)
        copied=folder/'journal.bin';shutil.copy2(authority.hub.path,copied);private_file(copied)
        q=authority.hub.state()['q'];root_artifact=authority.hub.artifact_path('q-root',q['root_id'])
        destination=folder/root_artifact.relative_to(authority.hub.root);destination.parent.mkdir(parents=True,exist_ok=True)
        private_file(destination.parent,directory=True);shutil.copy2(root_artifact,destination);private_file(destination)
        if kind=='journal_tail':
            with copied.open('ab') as stream:stream.write(b'\xff')
        try:QAuthority(ControlHub(folder))
        except DataError as exc:
            permitted={'q_instance_identity'} if kind=='copied_instance' else {'control_tail','control_corrupt'}
            if exc.code not in permitted:raise RuntimeError('copy_denied_at_unrelated_boundary_'+exc.code)
            cases.append({'case':kind,'copied_control_denied':True,'denied':exc.code,'live_original_untouched':True})
        else:raise RuntimeError('copied_or_damaged_control_allowed')
    # Repeated exact approval is a read of the same decision/event sequence.
    decision=run(approve_request(ledger,row['prepared_id'],row['prepared_sha256']))
    if decision!=row['approval']:raise RuntimeError('same_prepared_approval_was_not_idempotent')
    if financials('flow')!=base or authority.request(row['prepared_id']).get('claim'):raise RuntimeError('negative_cases_changed_finances_or_claim')
    proof={'status':'PASS_FOR_LISTED_GATES','actual_original_PG_snapshot':True,'prepared_id':row['prepared_id'],'cases':cases,'whole_request_positive':True,'fees_and_operations_unchanged':True,'provider_calls':0}
    r.write(r.EVIDENCE/f"root-{r.state()['active_root']:02d}-PG-approval-boundaries.json",proof)
    # Exactly this first new model tests a genuine result COMMIT ACK loss. It
    # stays claimed/consumed; its business transaction must be found via GET.
    path=r.PRIVATE/'flow/faults.json';faults=json.loads(path.read_text()) if path.exists() else {}
    faults[p['operation_id']]='commit_ack_lost';r.write(path,faults,private=True)
    client._task120_probe_done=True

def run_ack_and_gap(client):
    from app.capabilities.q_protocol import ROSTER
    from app.capabilities.contracts import AdmissionUnavailable
    from app.data_exit.q_store import authority_for
    from app.operator.q_request import principal_id
    import psycopg
    from psycopg.rows import dict_row
    aid=ROSTER[1];ledger=client.app.state.activities_ledger;authority=authority_for(ledger)
    base=r.PRIVATE/'flow';file=base/'c01-ack-gap-progress.json';state=json.loads(file.read_text()) if file.exists() else {}
    def retain(name,body):
        if name not in state:state[name]=body;r.write(file,state,private=True)
        return state[name]
    def persist(name,value):state[name]=value;r.write(file,state,private=True);return value
    path=f'/api/activities/{aid}/interview/commands'
    def goal(name):
        if name+'.done' in state:return state[name+'.done']
        before=client.request('GET',f'/api/activities/{aid}/interview/workspace')['head']
        body=retain(name,{'schema':'interview.command.v2','business_key':str(uuid4()),'action':'goal','expected_head_revision':before['revision'],'expected_goal_version':before['goal_version'],'expected_scope_revision':1,'body':{'goal':{'target':setup.SAMPLES['inputs']['interview_goal'],'material_roles':[]}}})
        value=client.request('POST',path,body)
        after=client.request('GET',f'/api/activities/{aid}/interview/workspace')['head']
        if value['status']!='committed' or after['revision']!=before['revision']+1 or after['goal_version']!=before['goal_version']+1:raise RuntimeError('ack_goal_did_not_create_new_parent')
        return persist(name+'.done',{'receipt':value,'before':before,'after':after})
    def command(name):
        if name in state:return state[name]
        status=client.request('GET',f'/api/activities/{aid}/retrieval/status')
        query=retain(name+'-query',{'business_key':str(uuid4()),'action':'query','expected_scope_revision':1,'expected_domain_revision':status['domain_revision'],'confirmed':True,'query':setup.SAMPLES['inputs']['interview_goal']})
        url=f'/api/activities/{aid}/retrieval/commands'
        pending=client.request('POST',url,query);client.approve(aid,query['business_key']);r.count('native_business_sessions')
        received=client.request('POST',url,query)
        if received['terminal_disposition']!='received':raise RuntimeError('ack_actual_query_not_received')
        head=client.request('GET',f'/api/activities/{aid}/interview/workspace')['head']
        return retain(name,{'schema':'interview.command.v2','business_key':str(uuid4()),'action':'ask','expected_head_revision':head['revision'],'expected_goal_version':head['goal_version'],'expected_scope_revision':1,'body':{'mode':'first'},'retrieval_ref':received['retrieval_ref']})
    if 'ACK.done' not in state:
        goal('ack-goal');body=command('ack-model');before=financials('flow');original=ledger.accept_interview_command;lost=[]
        async def accept_lost(*args,**kwargs):
            value=await original(*args,**kwargs)
            if not lost:lost.append(True);r.event('actual_PG_accept_COMMIT_ack_lost',business_key=body['business_key']);raise AdmissionUnavailable('TESTONLY_accept_ACK_lost')
            return value
        ledger.accept_interview_command=accept_lost
        try:client.request('POST',path,body,expect=(503,))
        finally:ledger.accept_interview_command=original
        known=client.request('GET',path+'/'+body['business_key']);assert known['status']=='accepted' and not known['launch_claimed']
        if financials('flow')!=before:raise RuntimeError('accepted_ack_loss_reserved_money')
        pending=client.request('POST',path,body);assert pending['outbound_approval']['state']=='pending'
        client.approve(aid,body['business_key']);original=ledger.claim_interview_launch;claimed=[]
        async def claim_lost(*args,**kwargs):
            value=await original(*args,**kwargs)
            if not claimed:claimed.append(True);r.event('actual_PG_launch_claim_COMMIT_ack_lost',business_key=body['business_key']);raise AdmissionUnavailable('TESTONLY_claim_ACK_lost')
            return value
        ledger.claim_interview_launch=claim_lost
        try:client.request('POST',path,body,expect=(503,))
        finally:ledger.claim_interview_launch=original
        native=r.state()['counts']['native_business_sessions']
        one=client.request('GET',path+'/'+body['business_key']);two=client.request('GET',path+'/'+body['business_key'])
        assert one['launch_claimed'] and two['launch_claimed'] and one['status']=='accepted'
        if financials('flow')!=before or r.state()['counts']['native_business_sessions']!=native:raise RuntimeError('claimed_ACK_GET_changed_finances_or_launched')
        persist('ACK.done',{'business_key':body['business_key'],'accept_COMMIT_real':True,'claim_COMMIT_real':True,'prepared_ACK_readonly_recovered':True,'claim_ACK_readonly_only':True,'never_resent_after_claim':True,'financials_unchanged':True})
    if 'gap.done' not in state:
        goal('gap-goal');body=command('gap-model');before=client.request('GET',f'/api/activities/{aid}/interview/workspace')['head']
        pending=client.request('POST',path,body);assert pending['outbound_approval']['state']=='pending'
        row=client.approve(aid,body['business_key'])[0];operation=row['prepared']['operation_id']
        faults_path=base/'faults.json';faults=json.loads(faults_path.read_text()) if faults_path.exists() else {};faults[operation]='release_gap';r.write(faults_path,faults,private=True)
        tag=hashlib.sha256(operation.encode()).hexdigest();outcome={};before_money=financials('flow')
        def send():
            try:outcome['receipt']=client.request('POST',path,body)
            except BaseException as exc:outcome['error_type']=type(exc).__name__
        r.count('native_business_sessions');thread=threading.Thread(target=send,name='TASK120-K2-actual-HTTP');thread.start()
        until=time.monotonic()+18;ready=base/('gap-ready-'+tag+'.json')
        while not ready.exists():
            if not thread.is_alive() or time.monotonic()>=until:raise RuntimeError('actual_interview_release_gap_not_observed')
            time.sleep(.01)
        window=json.loads(ready.read_text());assert window['dispatch_released']
        mutation=goal('gap-exclusive-goal')
        revoked=authority.revoke(row['prepared_id'],principal_id());assert revoked['state']=='revoked'
        r.event('actual_gap_exclusive_head_and_revoke_completed',operation_id=operation,prepared_id=row['prepared_id'],actor_pid=os.getpid(),actor_thread=threading.get_ident(),worker_pid=window['worker_pid'])
        (base/('gap-release-'+tag)).write_text('release only synthetic response',encoding='utf-8')
        thread.join(20)
        if thread.is_alive() or outcome.get('error_type'):raise RuntimeError('interview_gap_result_not_confirmed')
        after=client.request('GET',f'/api/activities/{aid}/interview/workspace')['head']
        fields=('revision','goal_version','goal_record_id','current_question_id','current_answer_id','current_feedback_id')
        if any(after[k]!=mutation['after'][k] for k in fields):raise RuntimeError('late_gap_result_advanced_current_head')
        with psycopg.connect(setup.dsn('flow'),row_factory=dict_row) as db:
            fact=db.execute('SELECT o.state,r.payload,r.payload_sha256 FROM activity_operations o JOIN activity_operation_results r USING(activity_id,operation_id) WHERE o.activity_id=%s AND o.operation_id=%s',(aid,operation)).fetchone()
        if not fact or fact['state']!='received' or hashlib.sha256(fact['payload'].encode()).hexdigest()!=fact['payload_sha256']:raise RuntimeError('immutable_007_not_retained_after_gap')
        after_money=financials('flow')
        if after_money['requests']!=before_money['requests']+1 or after_money['cost']!=before_money['cost']+250000:raise RuntimeError('gap_reserved_money_changed')
        persist('gap.done',{'operation_id':operation,'prepared_id':row['prepared_id'],'original_head':before,'exclusive_mutation_head':mutation['after'],'final_head':after,'007_payload_sha256':fact['payload_sha256'],'fee_not_refunded':True,'separate_HTTP_thread':True,'actual_worker_window':window,'head_and_revoke_completed_before_result':True})
    r.write(r.EVIDENCE/f"root-{r.state()['active_root']:02d}-ACK-and-K2-result.json",{'status':'PASS_FOR_LISTED_FAULTS','ACK':state['ACK.done'],'K2':state['gap.done'],'other_source_memory_scope_races':'NOT_CLAIMED'})
