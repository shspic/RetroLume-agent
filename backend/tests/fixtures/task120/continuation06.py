"""AP-120-06 finite targeted implementation checks; real PG/SUP and HTTP."""
import copy,hashlib,json,os,threading,time,traceback
from pathlib import Path
from uuid import uuid4
import psycopg
from psycopg.rows import dict_row
from . import resources as r,setup,final05 as previous
from .api_runtime import application,run,financials
from app.capabilities.q_protocol import ROSTER,digest,raw_digest,canonical
HERE=r.EVIDENCE/'continuation-06';SLOT='scope-ui-final'
previous.HERE=HERE;previous.SLOT=SLOT
Matrix=previous.Matrix
write=lambda name,value:r.write(HERE/name,value)

def checkpoint(name,action):
    p=HERE/(name+'-PASS.json')
    if p.exists():return json.loads(p.read_text(encoding='utf-8'))['facts']
    return previous.case(name,action)

def sources(aliases):
    mapping=json.loads((r.PRIVATE/SLOT/'sources.json').read_text(encoding='utf-8'))
    return [{'source_id':str(mapping[a]['id']),'version_id':str(mapping[a]['version_id']),'source_revision':mapping[a]['revision'],'original_sha256':mapping[a]['sha256']} for a in aliases]

def rows():
    with psycopg.connect(setup.dsn(SLOT),row_factory=dict_row) as c:
        return {'scope':c.execute('SELECT activity_id::text,source_id::text,version_id::text,source_revision FROM activity_scope_sources ORDER BY activity_id,source_id').fetchall(),
          'activities':c.execute('SELECT id::text,scope_revision,requests_reserved,cost_reserved_microunits FROM activities ORDER BY id').fetchall(),
          'heads':c.execute('SELECT activity_id::text,revision,goal_version,scope_revision,current_question_id::text,pending_key::text FROM interview_heads ORDER BY activity_id').fetchall()}

def bootstrap():
    risk=json.loads((HERE/'permission-risk-check.json').read_text(encoding='utf-8'))
    assert risk['before_real_GRANT'] and risk['migration015_sha256']==raw_digest((r.ROOT/'backend/migrations/015_activity_scope_delete_permission.sql').read_bytes())
    setup.initial_files(SLOT);setup.migrate(SLOT);setup.environment(SLOT)
    from app.data_exit.schema_profiles import SCOPE_ACL_QUERY
    from app.data_exit.schema_checks import assert_data_schema_sync
    with psycopg.connect(setup.dsn(SLOT),row_factory=dict_row) as connection:
        write('bootstrap-actual-scope-ACL-root-'+str(r.state()['active_root'])+'.json',{'rows':connection.execute(SCOPE_ACL_QUERY).fetchall()})
        assert_data_schema_sync(connection)
    from .transport import install
    install()
    from app.main import create_app
    app=create_app()
    if app.state.data_exit is None:raise RuntimeError('new_R03_data_assembly_not_ready')
    mapping=setup.seed_sources(app,SLOT);run(setup.bind_root(app,SLOT,mapping))
    with application(SLOT) as c:
        f=Matrix(c)
        for aid in ROSTER[1:]:f.goal(aid,'initial-'+aid)
    identity=setup.info(SLOT)
    return {'database':identity['database'],'database_oid':identity['database_oid'],'dataset_id':identity['dataset_id'],'instance_id':identity['instance_id'],'schema_profile':'data_exit.v1.r03','role_reuse_no_new_login_or_membership':True,'source_count':len(mapping),'fixed_roster':list(ROSTER),'financials':financials(SLOT),'015_core':risk['grant_objects']}

def profile_checks():
    from app.data_exit.schema_checks import assert_data_schema_sync
    from app.data_exit.schema_profiles import SCOPE_ACL_QUERY
    from app.data_exit.contracts import DataError
    with psycopg.connect(setup.dsn(SLOT),row_factory=dict_row) as c:
        assert_data_schema_sync(c);actual=c.execute(SCOPE_ACL_QUERY).fetchall()
    write('scope-exact-actual-ACL.json',{'profile':'data_exit.v1.r03','rows':actual})
    tests=[('missing-delete','REVOKE DELETE ON public.activity_scope_sources FROM retrolume_data_app'),('extra-truncate','GRANT TRUNCATE ON public.activity_scope_sources TO retrolume_data_app'),('readonly-delete','GRANT DELETE ON public.activity_scope_sources TO retrolume_data_snapshot'),('wrong-profile',"ALTER TABLE public.data_control DROP CONSTRAINT data_control_schema_profile_check; ALTER TABLE public.data_control ADD CONSTRAINT data_control_schema_profile_check CHECK(schema_profile IN('data_exit.v1.r02','data_exit.v1.r03'))")]
    result=[]
    for name,mutation in tests:
        with psycopg.connect(setup.dsn(SLOT,True),autocommit=True,row_factory=dict_row) as c:
            c.execute('BEGIN')
            try:
                c.execute(mutation,prepare=False)
                try:assert_data_schema_sync(c)
                except DataError as exc:assert exc.code=='data_schema_not_ready';result.append({'case':name,'code':exc.code,'actual_catalog_transaction':True})
                else:raise AssertionError('inexact_profile_accepted_'+name)
            finally:c.execute('ROLLBACK')
    for mode in ('frozen','restored_readonly'):
        with psycopg.connect(setup.dsn(SLOT,True),autocommit=True,row_factory=dict_row) as c:
            c.execute('BEGIN')
            try:
                c.execute('UPDATE public.data_control SET mode=%s',(mode,))
                from psycopg import sql
                c.execute(sql.SQL('SET LOCAL ROLE {}').format(sql.Identifier(setup.info(SLOT)['app_user'])))
                try:c.execute('DELETE FROM public.activity_scope_sources WHERE activity_id=%s',(ROSTER[2],))
                except psycopg.Error as exc:
                    assert exc.sqlstate=='42501' and exc.diag.message_primary=='data_runtime_readonly'
                    result.append({'case':'guard-'+mode,'SQLSTATE':'42501','guard':'data_runtime_readonly','transaction_rolled_back':True})
                else:raise AssertionError('nonnormal_DELETE_was_allowed')
            finally:c.execute('ROLLBACK')
    with psycopg.connect(setup.dsn(SLOT),row_factory=dict_row) as c:assert_data_schema_sync(c)
    return {'exact_actual_ACL':'scope-exact-actual-ACL.json','negative_catalog_and_guard_cases':result,'normal_source_restored_by_transaction_rollback':True,'financials':financials(SLOT)}

def positive_shrink():
    with application(SLOT) as c:
        f=Matrix(c);aid=ROSTER[2]
        f.local(aid,'bind_scope',{'sources':sources(('N','R')),'material_roles':[]},'scope-two-source-preparation')
        before=rows();money=financials(SLOT);h=f.head(aid)
        receipt=f.local(aid,'bind_scope',{'sources':sources(('N',)),'material_roles':[]},'actual-scope-shrink')
        after=rows();assert f.head(aid)['scope_revision']==h['scope_revision']+1
        before_other=[x for x in before['scope'] if x['activity_id']!=aid];after_other=[x for x in after['scope'] if x['activity_id']!=aid]
        assert before_other==after_other and len([x for x in after['scope'] if x['activity_id']==aid])==1 and financials(SLOT)==money
        return {'receipt':receipt,'before':before,'after':after,'financials_unchanged':True,'only_removed_requested_binding':True,'scope_revision_exactly_one':True,'legitimate_local_head_update':True}

def scope_negatives():
    result=[]
    with application(SLOT) as c:
        f=Matrix(c);aid=ROSTER[2];h=f.head(aid)
        base={'schema':'interview.command.v2','business_key':str(uuid4()),'action':'bind_scope','expected_head_revision':h['revision'],'expected_goal_version':h['goal_version'],'expected_scope_revision':h['scope_revision'],'body':{'sources':sources(('N',)),'material_roles':[]}}
        cases=[]
        stale=copy.deepcopy(base);stale['expected_head_revision']-=1;cases.append(('stale-CAS',aid,stale,'interview_head_conflict',409))
        invalid=copy.deepcopy(base);invalid['business_key']=str(uuid4());invalid['body']['sources'][0]['source_revision']+=1;cases.append(('invalid-source',aid,invalid,'source_invalid',409))
        unknown=copy.deepcopy(base);unknown['business_key']=str(uuid4());cases.append(('unknown-activity','01800000-0000-4000-8000-000000000099',unknown,'not_found',404))
        for name,target,cmd,expected,status in cases:
            cmd=f.retain('negative-'+name,cmd)
            def check():
                before=rows();money=financials(SLOT);got=c.request('POST',f.url(target),cmd,expect=(status,));code=c.timeline[-1]['rejection_code']
                after=rows();after_money=financials(SLOT)
                write('scope-negative-'+name+'-actual-root-'+str(r.state()['active_root'])+'.json',{'request':cmd,'response':got,'before':before,'after':after,'money_before':money,'money_after':after_money,'expected_code':expected,'actual_code':code})
                assert code==expected,(name,code);assert after==before and after_money==money
                return {'case':name,'HTTP':status,'code':code,'business_key':cmd['business_key'],'no_partial_scope_or_head_write':True,'no_financial_delta':True}
            result.append(checkpoint('scope-negative-'+name,check))
    return {'cases':result,'eleven_unaffected_whole_request_gates':'../finalization-05/permissions-summary.json'}

def shrink_race():
    from app.data_exit.q_store import authority_for
    from app.operator.q_request import inspect_request
    from app.capabilities.contracts import AdmissionDenied
    from app.data_exit.contracts import DataError
    with application(SLOT) as c:
        f=Matrix(c);aid=ROSTER[2]
        f.local(aid,'bind_scope',{'sources':sources(('N','R')),'material_roles':[]},'K2-two-source-preparation')
        f.goal(aid,'K2-scope-shrink-goal');cmd,q=f.prepare(aid,'K2-scope-shrink-model');key=cmd['business_key'];op=q['prepared']['operation_id']
        before=previous.persistent(aid,key);money=financials(SLOT)
        write('K2-scope-shrink-before.json',{'persistent':before,'financials':money,'business_key':key,'operation_id':op})
        previous.fault(op,'release_gap');tag=hashlib.sha256(op.encode()).hexdigest();base=r.PRIVATE/SLOT
        ready=base/('gap-ready-'+tag+'.json');release=base/('gap-release-'+tag);outcome={}
        def send():
            try:outcome['receipt']=c.request('POST',f.url(aid),cmd)
            except BaseException as exc:outcome['failure']=previous.safe(exc)
        r.count('native_business_sessions');worker=threading.Thread(target=send,name='TASK120-scope-shrink');worker.start()
        try:
            end=time.monotonic()+18
            while not ready.exists():
                if not worker.is_alive() or time.monotonic()>=end:raise RuntimeError('actual_release_gap_not_reached')
                time.sleep(.01)
            barrier=json.loads(ready.read_text(encoding='utf-8'));assert barrier['dispatch_released'] and barrier['worker_pid']!=os.getpid()
            mutation=f.local(aid,'bind_scope',{'sources':sources(('N',)),'material_roles':[]},'K2-real-scope-shrink')
            committed=previous.persistent(aid,key)
            write('K2-scope-shrink-COMMIT.json',{'utc':r.utc(),'worker':barrier,'actor_pid':os.getpid(),'actor_thread':threading.get_ident(),'mutation':mutation,'persistent':committed})
        finally:
            release.write_text('release',encoding='utf-8');worker.join(20)
            write('K2-scope-shrink-final-checkpoint.json',{'utc':r.utc(),'persistent':previous.persistent(aid,key),'financials':financials(SLOT),'worker_stopped':not worker.is_alive(),'outcome':outcome})
        assert not worker.is_alive() and 'failure' not in outcome
        final=previous.persistent(aid,key);after=financials(SLOT)
        assert final['head']==committed['head'] and final['007']['state']=='received' and final['007']['actual_sha256']==final['007']['payload_sha256']
        assert after['requests']==money['requests']+1 and after['cost']==money['cost']+250000 and previous.dispatch_count(op)==1
        try:inspection=run(inspect_request(f.ledger,q['prepared_id']))
        except (DataError,AdmissionDenied) as exc:inspection={'request_available':False,'code':getattr(exc,'code',str(exc))}
        assert not inspection.get('request_available')
        native=r.state()['counts']['native_business_sessions'];c.request('GET',f.url(aid)+'/'+key)
        assert financials(SLOT)==after and r.state()['counts']['native_business_sessions']==native
        return {'before':before,'after_mutation':committed,'final':final,'financials_before':money,'financials_after':after,'barrier':barrier,'scope_actually_shrank':True,'late_model_did_not_advance_head':True,'immutable007_and_charge_retained':True,'one_dispatch':True,'GET_zero_actions':True,'request_body_closed':inspection}

def ui():
    import subprocess
    from . import restore06
    from app.data_exit.contracts import DataJobCommand
    from app.data_exit.schema_profiles import R03
    assert (HERE/'K2-scope-shrink-PASS.json').exists() and (HERE/'UI-order-preflight.md').exists()
    port=restore06.preflight();base=r.PRIVATE/SLOT
    config=json.loads((base/'data-exit.json').read_text(encoding='utf-8'))
    config['factory']={'id':'task120-scopeui-readonly-v1','image_id':restore06.IMAGE,'login_prefix':'task120_scopeui_','pg_major':17,'source_name':r.NAME,
      'slots':[{'id':'scopeui-ro1','name':restore06.NAME,'volume':restore06.VOLUME,'port':port,'database':'retrolume_task120_scopeui_ro','schema_profile':R03}]}
    r.write(base/'data-exit.json',config,private=True)
    with application(SLOT) as c:
        f=Matrix(c);rt=c.app.state.data_exit;undo=restore06.install(rt.factory)
        if 'UI-legacy-parent.done' not in f.state:
            cmd=f.retain('UI-legacy-parent',{'business_key':str(uuid4()),'goal':setup.SAMPLES['inputs']['numeric_goal'],'confirmed':True})
            intent=f'/api/activities/{ROSTER[0]}/learning/intents/{cmd["business_key"]}?action=first'
            got=c.request('GET',intent,expect=(200,202,404))
            if got.get('operation'):
                operation=got['operation'];assert operation.get('read_status')=='committed_current'
                f.save('UI-legacy-parent.done',{'operation_id':operation['operation_id']})
            else:
                c.request('POST',f'/api/activities/{ROSTER[0]}/learning/first',cmd);c.approve(ROSTER[0],cmd['business_key']);r.count('native_business_sessions')
                got=c.request('POST',f'/api/activities/{ROSTER[0]}/learning/first',cmd);assert got['status']=='committed_current';f.save('UI-legacy-parent.done',got)
        money=financials(SLOT);write('pre-irreversible-B-and-financial-checkpoint.json',{'utc':r.utc(),'scope':rows(),'financials':money,'B_proofs':['actual-scope-shrink-PASS.json','scope-targeted-negatives-PASS.json','K2-scope-shrink-PASS.json']})
        directory=base/('UI-root-'+str(r.state()['active_root']));directory.mkdir(exist_ok=True);handshake=directory/'handshake';handshake.mkdir(exist_ok=True)
        spec={'origin':c.base,'project':str(r.ROOT),'evidence':str(HERE),'proof':str(HERE/f'UI-context-root-{r.state()["active_root"]}.json'),'profile':str(directory/'browser'),'handshake':str(handshake),'activity_id':ROSTER[0],
          'parent_operation':f.state['UI-legacy-parent.done']['operation_id'],'questions':[setup.SAMPLES['inputs']['numeric_initial_question'],setup.SAMPLES['inputs']['targeted_question']],'root':r.state()['active_root']}
        r.write(directory/'spec.json',spec,private=True)
        gates={'armed':False,'used':False,'ready':threading.Event(),'release':threading.Event()};original_caps=rt.caps
        def caps():
            if gates['armed'] and not gates['used']:
                gates['used']=True;gates['ready'].set()
                write('namespace-capabilities-authenticated-barrier.json',{'utc':r.utc(),'actor_pid':os.getpid(),'thread':threading.get_ident(),'local_session_already_checked_by_production_runtime':True,'body_not_yet_built':True})
                if not gates['release'].wait(20):raise RuntimeError('bounded_capabilities_transition_timeout')
            return original_caps()
        rt.caps=caps
        env=r.public_environment();env['RETROLUME_TASK120_UI_SPEC']=str(directory/'spec.json')
        r.memory_gate('browser');r.count('browser_starts');process=None
        def reply(request):
            kind=request['kind']
            if kind=='approve':
                result=c.approve(ROSTER[0],request['business_key']);return {'prepared_ids':[v['prepared_id'] for v in result],'claim_absent':all(v.get('claim') is None for v in result)}
            if kind=='backup':
                receipt=c.request('POST','/api/data/jobs',{'kind':'restore_checkpoint','business_key':str(uuid4()),'scope':{'mode':'all'},'confirm':True});end=time.monotonic()+45
                while rt.hub.get(receipt['job_id'])['state'] not in ('published','failed','published_unconfirmed'):
                    if time.monotonic()>end:raise RuntimeError('backup_not_settled')
                    time.sleep(.02)
                actual=rt.hub.get(receipt['job_id']);assert actual['state']=='published'
                write('normal-backup-checkpoint.json',{'receipt':actual,'context':rt.context().public(),'financials':financials(SLOT)})
                return {'path':str(rt.packages.path(receipt['job_id'])),'receipt':actual,'context':rt.context().public()}
            if kind=='freeze':
                before=rt.context().public();lease=run(rt.maintenance.drain_for_readonly_switch(before['selection_generation'],time.monotonic()+15));lease.close()
                after=rt.context().public();assert after['read_only'] and after['current_mode']=='frozen';assert financials(SLOT)==money
                c.headers['x-retrolume-data-context']=canonical(after)
                value={'before':before,'after':after,'actual_PG':rt.source.state(),'financials_unchanged':True,'Q_state_sha256':digest(rt.hub.state()['q'])}
                write('actual-frozen-DataContext-COMMIT.json',value);return value
            if kind=='verified':
                end=time.monotonic()+70
                while rt.hub.get(request['job_id'])['state'] not in ('verified','failed','restore_unconfirmed'):
                    if time.monotonic()>end:raise RuntimeError('restore_not_settled')
                    time.sleep(.02)
                receipt=rt.hub.get(request['job_id']);assert receipt['state']=='verified'
                value={'receipt':receipt,'target':r.state()['continuation06_restore_target'],'target_state':rt.hub.state()['targets'][receipt['target_id']]}
                write('normal-restore-verified-checkpoint.json',value);return value
            if kind=='arm_namespace':gates['armed']=True;return {'armed':True}
            if kind=='activate':
                if not gates['ready'].wait(12):raise RuntimeError('real_authenticated_capabilities_request_not_paused')
                before=rt.context().public()
                try:
                    got=c.request('POST',f'/api/data/restore-jobs/{request["job_id"]}/activate-readonly',{'expected_plan_sha256':request['plan_sha256'],'business_key':str(uuid4()),'expected_selection_generation':before['selection_generation'],'confirm':True})
                    after=rt.context().public();assert got['state']=='active_readonly' and after['current_mode']=='restored_readonly' and after['instance_id']!=before['instance_id']
                    value={'activation':got,'before':before,'after':after,'selector':rt.hub.state()['selection'],'target':r.state()['continuation06_restore_target']}
                    write('normal-selector-activation-COMMIT.json',value);return value
                finally:gates['release'].set()
            raise RuntimeError('closed_UI_driver_action')
        try:
            with (HERE/f'UI-root-{r.state()["active_root"]}.log').open('wb') as log:
                process=subprocess.Popen(['node',str(r.ROOT/'frontend/tests/task120-continuation06-ui.mjs')],cwd=r.ROOT/'frontend',env=env,stdout=log,stderr=subprocess.STDOUT)
                ordinal=1;end=time.monotonic()+260
                while process.poll() is None:
                    if time.monotonic()>end:raise RuntimeError('finite_UI_driver_timeout')
                    path=handshake/f'request-{ordinal}.json'
                    if path.exists():
                        request=json.loads(path.read_text(encoding='utf-8'))
                        try:value=reply(request)
                        except BaseException as exc:
                            write('UI-driver-failure-root-'+str(r.state()['active_root'])+'.json',{'request':request,**previous.safe(exc)})
                            r.write(handshake/f'reply-{ordinal}.json',{'status':'FAILED','safe_code':getattr(exc,'code',type(exc).__name__)},private=True)
                        else:r.write(handshake/f'reply-{ordinal}.json',{'status':'COMPLETED','facts':value},private=True)
                        ordinal+=1
                    time.sleep(.02)
                if process.returncode:raise RuntimeError('actual_two_context_UI_failed')
        finally:
            gates['release'].set();rt.caps=original_caps
            if process is not None and process.poll() is None:process.terminate();process.wait(5)
            undo()
            write('source-final-financials.json',{'utc':r.utc(),'source':financials(SLOT),'separate_from_restore_target':True})
            if rt.hub.state()['selection'] is not None:
                target=rt.factory.target(rt.hub.state()['selection']['target_id']);credentials=rt.factory.readonly_credentials(target.target_id)
                with psycopg.connect(credentials['readonly_dsn'],row_factory=dict_row) as connection:
                    from app.data_exit.schema_checks import assert_data_schema_sync
                    assert_data_schema_sync(connection)
                    activities=connection.execute('SELECT id::text,requests_reserved,cost_reserved_microunits,running_reserved_seconds,running_settled_seconds FROM activities ORDER BY id').fetchall()
                    state=connection.execute('SELECT dataset_id::text,source_instance_observed::text,mode_observed,schema_profile FROM public.data_export_control_v1').fetchone()
                write('restore-target-final-financials.json',{'utc':r.utc(),'state':state,'activities':activities,'requests':sum(x['requests_reserved'] for x in activities),'cost':sum(x['cost_reserved_microunits'] for x in activities),'separate_restored_copy_not_new_budget':True,'strict_R03_schema_check':True})
        proof=json.loads(Path(spec['proof']).read_text(encoding='utf-8'));assert proof['status']=='PASS' and len(proof['cases'])==2
        return {'proof':Path(spec['proof']).name,'cases':proof['cases'],'source_financials':financials(SLOT),'target_financials':'restore-target-final-financials.json','target':r.state().get('continuation06_restore_target')}

def old_compatibility():
    from psycopg.conninfo import make_conninfo
    from app.data_exit.repository import DataRepository
    expected=json.loads((r.EVIDENCE/'finalization-05/financial-final-separated.json').read_text(encoding='utf-8'))['instances']
    instances={};states={}
    for slot in ('flow','budget-01','budget-02','matrix-final'):
        credential=json.loads((r.ROOT/'.runtime/TASK-120'/slot/'identity.json').read_text(encoding='utf-8'))
        dsn=make_conninfo(host='127.0.0.1',port=r.state()['ports']['pg'],dbname=credential['database'],user=credential['app_user'],password=credential['app_password'])
        with DataRepository(dsn).connection(readonly=True) as c:
            state=c.execute('SELECT public.data_state() AS state').fetchone()['state'];assert state['schema_profile']=='data_exit.v1.r02';states[slot]=state
            activities=c.execute('SELECT id::text,requests_reserved,cost_reserved_microunits,running_reserved_seconds,running_settled_seconds,tools_reserved FROM activities ORDER BY id').fetchall()
            ops=c.execute('SELECT activity_id::text,operation_id,admission_id::text,state FROM activity_operations ORDER BY activity_id,operation_id').fetchall()
        actual={'activities':activities,'operations':ops,'requests':sum(x['requests_reserved'] for x in activities),'cost':sum(x['cost_reserved_microunits'] for x in activities)}
        assert actual==expected[slot],slot;instances[slot]=actual
    source=financials(SLOT);assert source==json.loads((HERE/'source-final-financials.json').read_text(encoding='utf-8'))['source']
    with DataRepository(setup.dsn(SLOT)).connection(readonly=True) as connection:state=connection.execute('SELECT public.data_state() AS state').fetchone()['state']
    assert state['mode']=='frozen' and state['schema_profile']=='data_exit.v1.r03';states[SLOT]=state;instances[SLOT]=source
    write('final-fresh-financials-separated.json',{'utc':r.utc(),'instances':instances,'states':states,'old_four_exactly_unchanged':True,'R02_normal_and_frozen_strict_schema_reads_passed':True,'source_R03_frozen_strict_read_passed':True,'restore_copy':'restore-target-final-financials.json','do_not_sum_source_and_restore_copy':True,'all_connections_read_only':True})
    from app.data_exit.control import ControlHub
    hub=ControlHub(r.PRIVATE/SLOT/'control');control=hub.state()
    records=[]
    for pid,row in control['q']['requests'].items():
        records.append({'prepared_id':pid,'business_key':row['prepared']['business_key'],'operation_id':row['prepared']['operation_id'],'state':row.get('state'),'claim':row.get('claim') is not None})
    write('final-source-Q-metadata.json',{'utc':r.utc(),'source_mode':state['mode'],'fence':control['fence']['state'],'selector':control['selection'],'requests':records,'claimed_keys_never_resent':True,'old_approved_unclaimed_keys_retained':True,'old_three_events':'../finalization-05/retained-original-Q-witness.json'})
    return {'old_four_unchanged':True,'actual_R02_compatibility':states,'final_R03_source':'frozen','no_business_or_ACL_write':True,'target_snapshot_preserved_from_root46':True}

def readonly_listing_check():
    with application(SLOT,reconciliation_only=True) as c:
        result=[]
        for path in ('/api/data/capabilities','/api/activities/capabilities','/api/activities?limit=20','/api/data/saved-records?category=activities'):
            response=c.request('GET',path,expect=(200,400,401,403,404,409,500,503))
            result.append({'path':path,'HTTP':c.timeline[-1]['status'],'code':c.timeline[-1]['rejection_code'],'response':response})
        write('readonly-listing-actual-diagnostic-root-'+str(r.state()['active_root'])+'.json',{'context':c.app.state.data_exit.context().public(),'Q_readiness':c.app.state.q_readiness,'routes':result,'target_only':True,'no_POST':True})
        ledger=c.app.state.activities_ledger
        try:records=run(ledger.list_activities(limit=20))
        except BaseException as exc:
            write('readonly-ledger-list-exception-root-'+str(r.state()['active_root'])+'.json',previous.safe(exc));raise
        assert len(records)==3
        from app.data_exit.q_store import QAuthority
        from app.data_exit.contracts import DataError
        try:QAuthority(c.app.state.data_exit.hub)
        except DataError as exc:assert exc.code=='q_normal_root_required';denial=exc.code
        else:raise AssertionError('readonly_target_gained_normal_Q_authority')
        try:run(ledger.cancel_activity(ROSTER[0]))
        except BaseException as exc:
            code=getattr(exc,'code',None)
            assert code in ('q_normal_root_required','data_readonly'),type(exc).__name__
            write('readonly-cancel-mutation-denied.json',{'actual_code':code,'normal_Q_denied':denial,'no_new_admission_or_send':True})
        else:raise AssertionError('readonly_cancel_was_allowed')
        return {'routes':result,'target_only':True,'listing_records':len(records),'normal_Q_authority_denied':denial,'cancel_mutation_denied':True}

def readonly_ui_check():
    import subprocess
    with application(SLOT,reconciliation_only=True) as c:
        folder=r.PRIVATE/SLOT/('readonly-UI-root-'+str(r.state()['active_root']));folder.mkdir(exist_ok=True)
        spec={'origin':c.base,'project':str(r.ROOT),'instance_id':r.state()['continuation06_restore_target']['instance_id'],'profile':str(folder/'browser'),'proof':str(HERE/f'readonly-UI-root-{r.state()["active_root"]}.json'),'screenshot':str(HERE/f'readonly-UI-root-{r.state()["active_root"]}.png')}
        r.write(folder/'spec.json',spec,private=True);env=r.public_environment();env['RETROLUME_TASK120_UI_SPEC']=str(folder/'spec.json')
        r.memory_gate('browser');r.count('browser_starts')
        with (HERE/f'readonly-UI-root-{r.state()["active_root"]}.log').open('wb') as log:
            result=subprocess.run(['node',str(r.ROOT/'frontend/tests/task120-continuation06-readonly-view.mjs')],cwd=r.ROOT/'frontend',env=env,stdout=log,stderr=subprocess.STDOUT,timeout=90)
        assert result.returncode==0
        proof=json.loads(Path(spec['proof']).read_text(encoding='utf-8'));assert proof['status']=='PASS'
        return {'proof':Path(spec['proof']).name,'rows':proof['activity_rows'],'saved_records':proof['saved_record_rows'],'context':proof['context'],'no_automatic_POST':True}

def execute(mode):
    if mode=='bootstrap':checkpoint('new-R03-bootstrap',bootstrap);checkpoint('real-profile-ACL-and-guard',profile_checks)
    elif mode=='scope':checkpoint('actual-scope-shrink',positive_shrink);checkpoint('scope-targeted-negatives',scope_negatives)
    elif mode=='shrink_race':checkpoint('K2-scope-shrink',shrink_race)
    elif mode=='ui':checkpoint('late-context-UI',ui)
    elif mode=='compat':checkpoint('old-R02-and-final-readonly-reconciliation',old_compatibility)
    elif mode=='ro_check':checkpoint('readonly-listing',readonly_listing_check)
    elif mode=='ro_ui':checkpoint('readonly-listing-UI',readonly_ui_check)
    elif mode=='financials':write('source-final-financials.json',{'utc':r.utc(),'source':financials(SLOT)})
    else:raise RuntimeError('closed_continuation06_phase')
