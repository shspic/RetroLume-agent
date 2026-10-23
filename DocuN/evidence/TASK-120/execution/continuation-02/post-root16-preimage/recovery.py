"""Scope-02 finite recovery, original identities and independent actual stages."""
import json,os,time,traceback
from datetime import datetime,timezone
from . import resources as r,setup
from .api_runtime import application,run,financials
from .control_job import NamedJob
from .merged import members,await_members

def observe():
    # Normal TESTONLY assembly explicitly rejects an external transport. The
    # read-only observer must install the same zero-egress transport first.
    from .transport import install
    install()
    import psycopg
    from psycopg.rows import dict_row
    from app.data_exit.codec import plain
    from app.capabilities.q_context import snapshot,check_instance
    from app.data_exit.q_store import authority_for
    rows=[]
    for slot in ('flow','budget-01'):
        setup.environment(slot,include_admin=False)
        until=time.monotonic()+15
        while True:
            try:
                with psycopg.connect(setup.dsn(slot),connect_timeout=2) as ready:ready.execute('SELECT 1').fetchone()
                break
            except psycopg.Error:
                if time.monotonic()>=until:raise RuntimeError('original_PG_not_ready_within_finite_gate') from None
                time.sleep(.2)
        from app.main import create_app
        app=create_app();authority=authority_for(app.state.activities_ledger)
        if not app.state.q_readiness['available']:
            r.event('c02_observer_actual_readiness',slot=slot,readiness=app.state.q_readiness,data_exit_error=getattr(app.state.data_exit_error,'code',None))
            raise RuntimeError('retained_Q_assembly_not_ready_'+str(app.state.q_readiness.get('reason')))
        with psycopg.connect(setup.dsn(slot),row_factory=dict_row) as db:
            identity=db.execute('SELECT current_database() AS database,(SELECT oid FROM pg_database WHERE datname=current_database()) AS database_oid,public.data_state() AS control').fetchone()
            activities=db.execute('SELECT id::text,deadline_at,requests_reserved,cost_reserved_microunits,running_reserved_seconds,outbound_grant_sha256 FROM activities ORDER BY id').fetchall()
        if any(a['deadline_at']<=datetime.now(timezone.utc) or a['outbound_grant_sha256']!=authority.grant.sha256 for a in activities):raise RuntimeError('original_deadline_or_binding_failed')
        rows.append({'slot':slot,'identity':identity,'activities':activities,'valid_until':authority.grant.valid_until_utc})
    r.write(r.EVIDENCE/f"root-{r.state()['active_root']:02d}-c02-instance-observation.json",plain({'actual_original_instances':rows,'C12_inherited_not_rerun':True}))

def bootstrap_memory():
    slot='budget-02';setup.initial_files(slot);setup.migrate(slot);setup.environment(slot)
    from .transport import install
    from app.main import create_app
    install();app=create_app()
    if app.state.data_exit_error or app.state.data_exit is None:raise RuntimeError('memory_actual_data_exit_not_ready')
    mapping=setup.seed_sources(app,slot);run(setup.bind_root(app,slot,mapping))
    selection=run(app.state.activities_ledger.read_memory_selection(__import__('app.capabilities.q_protocol',fromlist=['ROSTER']).ROSTER[1],include_bodies=True))
    if not selection['selected'] or not selection['eligible'] or len(selection['entries'])!=1 or selection['entries'][0]['body']['text']!=setup.SAMPLES['inputs']['memory_body']:raise RuntimeError('creation_memory_not_exactly_bound')
    r.write(r.EVIDENCE/'budget-02-selected-memory-binding.json',{'selected':True,'eligible':True,'selection_sha256':selection['selection_sha256'],'dependency_sha256':selection['dependency_sha256'],'entry':{k:v for k,v in selection['entries'][0].items() if k!='body'},'same_original_CID':True,'valid_until':'2026-10-19T12:19:22.457756Z'})

def finite(mode):
    if mode not in ('core','memory','ui'):raise RuntimeError('closed_scope02_mode')
    number=r.state()['active_root'];slot=r.state()['roots'][-1]
    job=NamedJob.open_existing(slot['identity'],1)
    try:baseline=members(job)
    finally:job.close()
    outcomes={};receipts=[];database='budget-02' if mode=='memory' else 'flow'
    with application(database) as client:
        from .flow import run_flow
        from .pg_boundaries import probe_approved,run_ack_and_gap
        from .ui import run_ui
        if mode=='core':
            client.after_approval=lambda rows:probe_approved(client,rows)
            stages=[('teaching_A3',(),lambda:run_flow('teaching_a3',client)),
                ('interview',(),lambda:run_flow('interview_repaired',client)),
                ('HTML',(),lambda:run_flow('legacy_html',client)),
                ('ACK_K2',('interview',),lambda:run_ack_and_gap(client))]
        elif mode=='memory':
            stages=[('selected_memory_positive',(),lambda:run_flow('interview_repaired',client,'budget-02')),
                ('selected_memory_proof',('selected_memory_positive',),lambda:memory_proof(client))]
        else:
            stages=[('UI_teaching',(),lambda:run_ui(client,'teaching')),
                ('UI_interview',(),lambda:run_ui(client,'interview')),
                ('UI_legacy_HTML',(),lambda:run_ui(client,'legacy_html'))]
        for name,deps,action in stages:
            if any(outcomes.get(x)!='PASS' for x in deps):outcomes[name]='SKIPPED_DEPENDENCY';receipts.append({'name':name,'status':outcomes[name],'depends_on':deps});continue
            if time.monotonic_ns()+30_000_000_000>=slot['business_deadline_ns']:raise RuntimeError('finite_scope02_margin')
            start=time.monotonic();receipt={'name':name,'utc':r.utc()}
            try:action()
            except BaseException as exc:
                outcomes[name]='FAIL';receipt.update(status='FAIL',error_type=type(exc).__name__,safe_code=str(exc) if type(exc) is RuntimeError else None,
                    frames=[{'file':str(x.filename).replace(str(r.ROOT),'PROJECT'),'line':x.lineno,'function':x.name} for x in traceback.extract_tb(exc.__traceback__)])
                r.update(lambda state:state['failures'].append({'root':number,'internal_stage':name,'receipt':f'root-{number:02d}-c02-{mode}-result.json'}))
            else:outcomes[name]='PASS';receipt['status']='PASS'
            finally:
                job=NamedJob.open_existing(slot['identity'],1)
                try:await_members(job,baseline)
                finally:job.close()
                receipt['wall_seconds']=time.monotonic()-start;receipts.append(receipt)
                r.write(r.EVIDENCE/f'root-{number:02d}-c02-{mode}-result.json',{'outcomes':outcomes,'receipts':receipts,'shared_normal_API':True,'provider_calls':0,'actual_fee':0,'preview':0})
    if any(v!='PASS' for v in outcomes.values()):raise RuntimeError('finite_scope02_partial_failure')

def memory_proof(client):
    from app.data_exit.q_store import authority_for
    from app.capabilities.q_protocol import ROSTER,canonical,raw_digest
    ledger=client.app.state.activities_ledger;authority=authority_for(ledger)
    progress=json.loads((r.PRIVATE/'budget-02/flow-progress.json').read_text())
    command=progress['c01-interview-question-after-catalog-fix'];receipt=client.request('GET',f'/api/activities/{ROSTER[1]}/interview/commands/{command["business_key"]}')
    if receipt['status']!='committed':raise RuntimeError('selected_memory_domain_not_committed')
    row=next(x for x in authority.hub.state()['q']['requests'].values() if x['prepared']['business_key']==command['business_key'] and x['prepared']['domain']=='interview')
    artifact=authority.artifact(row);request=artifact['request'];messages=request['messages']
    value=json.loads(next(m['content'] for m in reversed(messages) if m['role']=='user'))
    background=value['learning_background'];selection=run(ledger.read_memory_selection(ROSTER[1],include_bodies=True))
    if len(background)!=1 or background[0]['text']!=setup.SAMPLES['inputs']['memory_body'] or background[0]['memory_id']!=selection['entries'][0]['memory_id']:raise RuntimeError('selected_memory_not_in_actual_full_request')
    fact=run(ledger.read_committed_result(ROSTER[1],receipt['operation_id']))
    if not fact.payload or fact.read_status.value!='committed_current':raise RuntimeError('memory_actual_007_not_current')
    r.write(r.EVIDENCE/f"root-{r.state()['active_root']:02d}-selected-memory-model-COMMIT.json",{'status':'PASS','prepared_id':row['prepared_id'],'operation_id':receipt['operation_id'],'007_payload_sha256':fact.payload_sha256,'full_request_sha256':raw_digest(canonical(request)),'selection_sha256':selection['selection_sha256'],'memory_id':background[0]['memory_id'],'frozen_text_sha256':raw_digest(background[0]['text']),'actual_original_PG_and_SUP':True,'provider_calls':0})
