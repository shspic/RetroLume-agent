"""Finite original-key validation. Successful old requests are read only."""
import hashlib,json
from . import resources as r,setup
from .api_runtime import application,financials,run
from .repair03 import Flow
from app.capabilities.q_protocol import ROSTER,canonical,digest
HERE=r.EVIDENCE/'validation-04'
def write(name,value):r.write(HERE/name,value)
def money(name):
    value={'utc':r.utc(),'new_PG_connections':True,'flow':financials('flow'),'budget-02':financials('budget-02')}
    write(name,value);return value

def positive_map(c,*,exercise_required=False):
    """Read exact committed operation/hash and query identity, not filename gates."""
    from app.data_exit.q_store import authority_for
    facts=[];ledger=c.app.state.activities_ledger;authority=authority_for(ledger)
    progress=json.loads((r.PRIVATE/'flow/r03-progress.json').read_text(encoding='utf-8'))
    for name,aid,domain,query in [('t-plan',ROSTER[2],'teaching','t-query'),('i-ask',ROSTER[1],'interview','i-query'),('legacy-followup',ROSTER[2],'learning',None),('html',ROSTER[2],'html',None)]+([('t-exercise',ROSTER[2],'teaching','t-exercise-query')] if exercise_required else []):
        cmd=progress[name];receipt=progress[name+'.done'];op=receipt['operation_id']
        fact=run(ledger.read_committed_result(aid,op))
        import psycopg
        with psycopg.connect(setup.dsn('flow')) as db:
            db.execute('BEGIN READ ONLY')
            raw=db.execute('SELECT payload,payload_sha256 FROM activity_operation_results WHERE activity_id=%s AND operation_id=%s',(aid,op)).fetchone()
        if raw is None or raw[1]!=hashlib.sha256(raw[0].encode()).hexdigest():raise RuntimeError('v04_original_007_integrity_'+name)
        q=next(x for x in authority.hub.state()['q']['requests'].values() if x['prepared']['business_key']==cmd['business_key'] and x['prepared']['operation_id']==op)
        if not q.get('claim') or not q.get('admission'):raise RuntimeError('v04_original_Q_claim_missing_'+name)
        a=authority.artifact(q)
        entry={'name':name,'activity_id':aid,'business_key':cmd['business_key'],'domain':domain,'operation_id':op,'payload_sha256':raw[1],'current_read_status':fact.read_status.value,'qualified_payload_available':fact.payload is not None,'prepared_id':q['prepared_id'],'prepared_sha256':q['prepared_sha256'],'artifact_request_sha256':digest(a['request']),'claim':q['claim'],'admission':q['admission'],'business_resends':0}
        if query:
            entry.update(query_business_key=progress[query]['business_key'],query_result_sha256=progress[query+'.done']['retrieval_ref']['result_sha256'])
            current=c.request('GET',f'/api/activities/{aid}/retrieval/commands/'+entry['query_business_key'])
            if current['result_sha256']!=entry['query_result_sha256']:raise RuntimeError('v04_original_query_hash_changed')
            entry['query_current']=current.get('current')
        if domain in ('teaching','interview'):
            entry['domain_receipt']=c.request('GET',f'/api/activities/{aid}/{domain}/commands/'+cmd['business_key'])
        facts.append(entry)
    write('positive-operation-map-root-'+str(r.state()['active_root'])+'.json',{'utc':r.utc(),'facts':facts,'historical_success_not_assumed_current':True,'new_send':0})
    return facts

def exercise():
    from app.capabilities.contracts import ModelCallRequest
    from app.capabilities.gateway import ControlledModelGateway
    from app.capabilities.q_context import snapshot,check_instance,validate_provenance
    from app.learning.teaching_adapter import validate_teaching_request
    from app.learning.teaching_service import TeachingService
    from app.learning.teaching_contracts import TeachingCommandInput,parse_frozen_context
    from app.data_exit.q_store import authority_for
    from app.data_exit.codec import plain
    from types import SimpleNamespace
    baseline=money('financial-baseline.json')
    with application('flow') as c:
        f=Flow(c,'flow');aid=ROSTER[2];command=TeachingCommandInput.model_validate(f.state['t-exercise']);key=command.business_key
        ledger=c.app.state.activities_ledger;authority=authority_for(ledger)
        current=run(ledger.read_teaching_command(aid,key));row=current['command'];head=current['head']
        qrows=[x for x in authority.hub.state()['q']['requests'].values() if x['prepared']['business_key']==key]
        if row['status']!='accepted' or row.get('launch_claimed_at') or row.get('launch_claimed') or any(q.get('claim') for q in qrows):raise RuntimeError('v04_original_exercise_not_unclaimed')
        if head['revision']!=command.expected_revision or head['goal_version']!=command.expected_goal_version or current['activity']['scope_revision']!=command.expected_scope_revision:raise RuntimeError('v04_original_exercise_parent_changed')
        if row['request_sha256']!=command.request_sha256(aid):raise RuntimeError('v04_original_exercise_request_changed')
        frozen=parse_frozen_context(json.loads(row['context_body']))
        if getattr(frozen,'recipe',None) is not None:raise RuntimeError('v04_unexpected_original_memory_recipe')
        identity={n:head.get(n) for n in ('goal_record_id','goal_version','path_record_id','node_id','exercise_record_id','answer_record_id')};identity['correction_record_id']=command.body.get('correction_record_id')
        service=TeachingService(ledger,c.app.state.materials,c.app.state.originals)
        profile=service._build_profile(aid,command,frozen,identity)
        req=ModelCallRequest(messages=[{'role':m['role'],'content':m['content']} for m in frozen.messages],max_output_tokens=frozen.max_output_tokens,allowed_tools=frozenset(),teaching_profile=profile,retrieval_ref=frozen.retrieval_ref)
        payload=ControlledModelGateway(c.app.state.activity_config.model_service)._build_payload(req)
        before=financials('flow');qbefore=authority.hub.state()['q']
        async def dry():
            async with authority.async_policy(shared=True):
                state,ids,derived=await snapshot(ledger,aid);check_instance(authority,ledger,state)
                validate_provenance(authority,req.model_dump(mode='json'),payload,state,ids,derived,command.action,{'operation_id':command.operation_id(aid),'business_key':key,'command_request_sha256':command.request_sha256(aid),'frozen_context_sha256':frozen.context_sha256})
                authority.manifest.check_model(req,payload)
                code=await validate_teaching_request(SimpleNamespace(activity_id=aid,scope_revision=command.expected_scope_revision,operation_id=command.operation_id(aid)),req,ledger)
                if code:raise RuntimeError('v04_original_exercise_validation_'+code)
        run(dry())
        if before!=financials('flow') or qbefore!=authority.hub.state()['q']:raise RuntimeError('v04_dry_validation_mutated_authority')
        write('original-exercise-before-send.json',{'utc':r.utc(),'business_key':key,'request_sha256':row['request_sha256'],'context_sha256':row['context_sha256'],'full_request_sha256':digest(req.model_dump(mode='json')),'original_Q_rows':plain(qrows),'accepted_unclaimed':True,'full_frozen_request_validation':'PASS','financials_before':before,'dry_claim_send':0})
        f.model(aid,'teaching','exercise',command.body,'t-exercise',command.retrieval_ref.model_dump())
        after=financials('flow')
        if after['requests']!=before['requests']+1 or after['cost']!=before['cost']+250000:raise RuntimeError('v04_exercise_financial_delta')
        write('original-exercise-positive.json',{'status':'PASS','business_key':key,'007':f.state['t-exercise.007'],'receipt':f.state['t-exercise.done'],'financials_before':before,'financials_after':after,'no_new_plan_or_key':True})
        positive_map(c,exercise_required=True)
    money('financial-after-exercise.json')

def boundary_cases(c):
    from .pg_boundaries import probe_approved,run_ack_and_gap
    positive_map(c,exercise_required=True)
    f=Flow(c,'flow');aid=ROSTER[1]
    f.goal(aid,'interview',setup.SAMPLES['inputs']['interview_goal'],'v04-b-goal')
    ref=f.retrieve(aid,'query','v04-b-query',setup.SAMPLES['inputs']['interview_goal'])['retrieval_ref']
    before=financials('flow');c.after_approval=lambda rows:probe_approved(c,rows)
    try:f.model(aid,'interview','ask',{'mode':'first'},'v04-b-result-ACK-model',ref)
    finally:c.after_approval=None
    write('result-ACK-positive.json',{'status':'PASS','007':f.state['v04-b-result-ACK-model.007'],'financials_before':before,'financials_after':financials('flow')})
    run_ack_and_gap(c)
    money('financial-after-boundaries.json')

def flow_final():
    from .ui import run_ui
    from app.activities.repository import PostgresAdmissionLedger
    with application('flow') as c:
        positive_map(c,exercise_required=True)
        before=financials('flow');view=run(c.app.state.activities_ledger.read_teaching_workspace(ROSTER[2]))
        selected=run(PostgresAdmissionLedger(setup.dsn('budget-02')).read_memory_selection(ROSTER[1],include_bodies=False))
        if view['memory_selected'] or not view['memory_qualified'] or not selected['selected']:raise RuntimeError('v04_memory_display_projection_not_proven')
        write('memory-display-PG.json',{'status':'PASS','unselected_flow_teaching_v3_memory_selected':view['memory_selected'],'memory_eligibility_unchanged':view['memory_qualified'],'budget02_actual_selected':selected['selected'],'financials_unchanged':financials('flow')==before,'only_display_projection_changed':True})
        c.validation04_boundaries=lambda:boundary_cases(c)
        run_ui(c,'remaining')

def execute(mode):
    if mode=='exercise':return exercise()
    if mode=='financials':return money('financial-final-new-connection-root-'+str(r.state()['active_root'])+'.json')
    if mode=='flow_final':return flow_final()
    if mode=='ui':
        from .ui import run_ui
        with application('flow') as c:
            positive_map(c,exercise_required=True)
            return run_ui(c,'all')
    if mode=='boundaries':
        with application('flow') as c:
            return boundary_cases(c)
    if mode=='races':
        from .recovery_races import run_races
        ui_path=r.EVIDENCE/f"root-{r.state()['active_root']:02d}-batch-01-ui-remaining-proof.json"
        ui=json.loads(ui_path.read_text(encoding='utf-8'))
        if not any(x['name'].startswith('A3-teaching-query-model') and x['status']=='PASS' for x in ui.get('cases',[])):raise RuntimeError('v04_normal_teaching_UI_required_before_final_instance_mutations')
        old=json.loads((r.PRIVATE/'budget-02/r03-progress.json').read_text(encoding='utf-8'))
        from app.activities.repository import PostgresAdmissionLedger
        from .transport import install
        setup.environment('budget-02',include_admin=False);install()
        from app.main import create_app
        app=create_app();fact=run(app.state.activities_ledger.read_committed_result(ROSTER[1],old['i2-ask.007']['operation_id']))
        if fact.read_status.value!='committed_current' or fact.payload_sha256!=old['i2-ask.007']['payload_sha256']:raise RuntimeError('v04_memory_positive_current_qualification_lost')
        write('memory-positive-fresh-before-destructive.json',{'utc':r.utc(),'operation_id':old['i2-ask.007']['operation_id'],'payload_sha256':fact.payload_sha256,'read_status':fact.read_status.value,'new_send':0})
        return run_races()
    raise ValueError('v04_closed_mode')
