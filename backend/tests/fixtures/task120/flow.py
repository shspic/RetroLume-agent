"""Finite actual API chains; checkpoints resume original commands, never reset."""
from uuid import uuid4
from . import resources as r,setup
from .api_runtime import application,run,financials
from app.capabilities.q_protocol import ROSTER,digest


def run_flow(lane=None,client=None,slot='flow'):
    if not (r.EVIDENCE/'bootstrap-result.json').exists():raise RuntimeError('completed_bootstrap_required')
    state_file=r.PRIVATE/slot/'flow-progress.json'
    import json
    state=json.loads(state_file.read_text(encoding='utf-8')) if state_file.exists() else {}
    def retain(name,body):
        if name not in state:state[name]=body;r.write(state_file,state,private=True)
        return state[name]
    from contextlib import nullcontext
    with (application(slot) if client is None else nullcontext(client)) as c:
        a1,a2,a3=ROSTER
        if lane=='teaching_a3':a1=a3
        plan_name='teaching-plan'
        if lane is None and 'teaching-plan' in state and 'teaching-plan.done' not in state:
            prior=run(c.app.state.activities_ledger.read_teaching_command(a1,state['teaching-plan']['business_key']))
            if prior and prior['command']['launch_claimed_at'] is not None:
                # The retained Root06 StopProof ends that original tree. Its
                # claimed key is never resent. Explicitly abandon locally, then
                # use a new finite business intent after the launcher repair.
                if 'teaching-plan-abandoned.done' not in state:
                    v=c.request('GET',f'/api/activities/{a1}/teaching/workspace');h=v['head']
                    command=retain('teaching-plan-abandoned',{'business_key':str(uuid4()),'action':'abandon','expected_revision':h['revision'],'expected_goal_version':h['goal_version'],'expected_scope_revision':1,'body':{'target_business_key':state['teaching-plan']['business_key']}})
                    state['teaching-plan-abandoned.done']=c.request('POST',f'/api/activities/{a1}/teaching/commands',command);r.write(state_file,state,private=True)
                plan_name='teaching-plan-after-launcher-repair'
        def retrieve(aid,action,name,query=None):
            if name+'.done' in state:return state[name+'.done']
            domain=c.request('GET',f'/api/activities/{aid}/retrieval/status')
            command=retain(name,{'business_key':str(uuid4()),'action':action,'expected_scope_revision':1,'expected_domain_revision':domain['domain_revision'],
                'confirmed':True,**({'query':query} if query is not None else {})})
            path=f'/api/activities/{aid}/retrieval/commands'
            # Reconcile the immutable original key first. A fully cached index
            # is a real terminal receipt and needs no new approval or send.
            value=c.request('GET',path+'/'+command['business_key'],expect=(200,202,404))
            if not value.get('status'):value=c.request('POST',path,command)
            if value.get('status')=='terminal':
                if value.get('terminal_disposition')!='received':raise RuntimeError('retained_retrieval_terminal_not_received')
                state[name+'.done']=value;r.write(state_file,state,private=True);return value
            if value.get('launch_claimed') or value.get('launch_claimed_at') or value.get('status')=='launch_claimed':raise RuntimeError('retained_retrieval_claim_never_resent')
            if not value.get('outbound_approval'):value=c.request('POST',path,command)
            assert value['outbound_approval'] and not value['outbound_approval']['can_continue']
            baseline=financials(slot)
            c.request('GET',path+'/'+command['business_key'])
            rows=c.approve(aid,command['business_key'])
            assert financials(slot)==baseline
            for row in rows:r.count('native_business_sessions')
            value=c.request('POST',path,command)
            assert value['terminal_disposition']=='received',value.get('error_code')
            state[name+'.done']=value;r.write(state_file,state,private=True)
            return value
        def index(aid):return retrieve(aid,'source_index','index-'+aid)
        def teach(action,body,name):
            if name+'.done' in state:return state[name+'.done']
            ref=None
            if action=='plan' and name not in state:
                index(a1)
                ref=retrieve(a1,'query',name+'-query',setup.SAMPLES['inputs']['numeric_goal'])['retrieval_ref']
            view=c.request('GET',f'/api/activities/{a1}/teaching/workspace');h=view['head'] or {}
            command=retain(name,{'business_key':str(uuid4()),'action':action,'expected_revision':h.get('revision',0),'expected_goal_version':h.get('goal_version',0),'expected_scope_revision':1,'body':body,
                **({'retrieval_ref':ref} if ref else {})})
            path=f'/api/activities/{a1}/teaching/commands'
            value=c.request('POST',path,command)
            if action in ('plan','exercise'):
                assert value['status']=='accepted' and value['outbound_approval']['state']=='pending'
                baseline=financials(slot);sup=r.state()['counts']['native_business_sessions']
                receipt=c.request('GET',path+'/'+command['business_key']);assert receipt['outbound_approval']['state']=='pending'
                assert financials(slot)==baseline and r.state()['counts']['native_business_sessions']==sup
                c.approve(a1,command['business_key'])
                receipt=c.request('GET',path+'/'+command['business_key']);assert receipt['outbound_approval']['can_continue']
                assert financials(slot)==baseline
                r.count('native_business_sessions');value=c.request('POST',path,command)
                assert value['status']=='committed',value.get('error_code')
                op=run(c.app.state.activities_ledger.read_committed_result(a1,value['operation_id']))
                assert op.read_status.value=='committed_current' and op.payload
            state[name+'.done']=value;r.write(state_file,state,private=True)
            return value
        def change_goal(name,text):
            if name+'.done' in state:
                if name+'.parent-proof' not in state:raise RuntimeError('local_goal_ack_requires_parent_reconciliation')
                return state[name+'.done']
            before=c.request('GET',f'/api/activities/{a1}/teaching/workspace')['head'] or {'revision':0,'goal_version':0,'goal_record_id':None}
            result=teach('goal',{'goal':text},name)
            after=c.request('GET',f'/api/activities/{a1}/teaching/workspace')['head']
            if (not result['record_ids'] or after['goal_record_id']==before['goal_record_id']
                or after['revision']!=before['revision']+1 or after['goal_version']!=before['goal_version']+1):
                raise RuntimeError('explicit_local_goal_did_not_create_new_parent')
            state[name+'.parent-proof']={'before':before,'after':after,'model_called':False}
            r.write(state_file,state,private=True)
            return result
        if lane=='teaching_a3':
            if 'c02-a3-goal.done' not in state:
                import psycopg
                with psycopg.connect(setup.dsn(slot)) as db:
                    heads=db.execute('SELECT (SELECT count(*) FROM teaching_heads WHERE activity_id=%s),(SELECT count(*) FROM interview_heads WHERE activity_id=%s)',(a1,a1)).fetchone()
                    activity=db.execute('SELECT deadline_at>CURRENT_TIMESTAMP,requests_reserved<max_requests,cost_reserved_microunits+250000<=max_cost_microunits FROM activities WHERE id=%s',(a1,)).fetchone()
                if heads!=(0,0) or not activity or not all(activity):raise RuntimeError('original_A3_not_a_legal_fresh_teaching_start')
                r.write(r.EVIDENCE/'flow-A3-fresh-head-precondition.json',{'activity_id':a1,'heads':list(heads),'deadline_and_funds_valid':True,'old_A1_untouched':True})
            change_goal('c02-a3-goal',setup.SAMPLES['inputs']['numeric_goal'])
            plan=teach('plan',{'confirmed':True},'c02-a3-plan')
            proposal=next(row['record_id'] for row in plan['record_ids'] if row['kind']=='path_proposal')
            teach('accept_path',{'proposal_record_id':proposal},'c02-a3-accept-path')
            head=c.request('GET',f'/api/activities/{a1}/teaching/workspace')['head']
            teach('exercise',{'confirmed':True,'path_record_id':head['path_record_id'],'node_id':head['node_id'],'purpose':'initial'},'c02-a3-exercise')
        if lane in (None,'teaching'):
            # Explicitly authorized local-only intermediate goal. Neither this
            # intermediate text nor the old UNKNOWN intent is sent.
            change_goal('c01-goal-concept',setup.SAMPLES['inputs']['concept_goal'])
            change_goal('c01-goal-numeric',setup.SAMPLES['inputs']['numeric_goal'])
            plan=teach('plan',{'confirmed':True},'c01-teaching-plan')
            proposal=next(row['record_id'] for row in plan['record_ids'] if row['kind']=='path_proposal')
            teach('accept_path',{'proposal_record_id':proposal},'c01-teaching-accept-path')
            view=c.request('GET',f'/api/activities/{a1}/teaching/workspace');head=view['head']
            teach('exercise',{'confirmed':True,'path_record_id':head['path_record_id'],'node_id':head['node_id'],'purpose':'initial'},'c01-teaching-exercise')
        def interview(action,body,name):
            if name+'.done' in state:return state[name+'.done']
            ref=None
            if action=='ask' and name not in state:
                ref=retrieve(a2,'query',name+'-query',setup.SAMPLES['inputs']['interview_goal'])['retrieval_ref']
            view=c.request('GET',f'/api/activities/{a2}/interview/workspace');h=view['head'] or {}
            command=retain(name,{'schema':'interview.command.v2','business_key':str(uuid4()),'action':action,'expected_head_revision':h.get('revision',0),'expected_goal_version':h.get('goal_version',0),'expected_scope_revision':1,'body':body,
                **({'retrieval_ref':ref} if ref else {})})
            path=f'/api/activities/{a2}/interview/commands';value=c.request('POST',path,command)
            if action in ('ask','review'):
                assert value['status']=='accepted' and value['outbound_approval']['state']=='pending'
                before=financials(slot);c.request('GET',path+'/'+command['business_key']);c.approve(a2,command['business_key']);assert financials(slot)==before
                r.count('native_business_sessions');value=c.request('POST',path,command);assert value['status']=='committed',value.get('error_code')
            state[name+'.done']=value;r.write(state_file,state,private=True);return value
        if lane in (None,'interview','interview_repaired'):
            interview('start',{'goal':{'target':setup.SAMPLES['inputs']['interview_goal'],'material_roles':[]}},'c01-interview-start')
            index(a2)
            if lane=='interview_repaired':
                interview('goal',{'goal':{'target':setup.SAMPLES['inputs']['interview_goal'],'material_roles':[]}},'c01-interview-goal-after-catalog-fix')
            interview('ask',{'mode':'first'},'c01-interview-question-after-catalog-fix' if lane=='interview_repaired' else 'c01-interview-question')
        if lane in (None,'legacy_html'):
            # Legacy learning keeps its first slot, private intent and original key.
            command=retain('legacy-first',{'business_key':str(uuid4()),'goal':setup.SAMPLES['inputs']['numeric_goal'],'confirmed':True})
            path=f'/api/activities/{a3}/learning/first'
            if 'legacy-first.done' not in state:
                value=c.request('POST',path,command);assert value['outbound_approval']['state']=='pending'
                before=financials(slot);c.request('GET',f'/api/activities/{a3}/learning/intents/{command["business_key"]}?action=first');c.approve(a3,command['business_key']);assert financials(slot)==before
                r.count('native_business_sessions');value=c.request('POST',path,command)
                assert value['status']=='committed_current',value.get('status')
                state['legacy-first.done']=value;r.write(state_file,state,private=True)
            if 'html.done' not in state:
                result=state['legacy-first.done'];parent=run(c.app.state.activities_ledger.read_committed_result(a3,result['operation_id']))
                caps=c.request('GET',f'/api/activities/{a3}/html/capabilities');assert caps['available']
                command=retain('html',{'business_key':str(uuid4()),'parent':{'kind':'learning','operation_id':result['operation_id'],'payload_sha256':parent.payload_sha256,'segment_index':0},
                    'focus':setup.SAMPLES['inputs']['numeric_goal'],'expected_config_sha256':caps['config_sha256'],'confirmed':True})
                path=f'/api/activities/{a3}/html/commands';value=c.request('POST',path,command);assert value['outbound_approval']['state']=='pending'
                before=financials(slot);c.request('GET',path+'/'+command['business_key']);c.approve(a3,command['business_key']);assert financials(slot)==before
                r.count('native_business_sessions');value=c.request('POST',path,command)
                assert value['status']=='terminal' and value['terminal_disposition']=='succeeded' and value['read_status']=='current',value.get('error_code')
                state['html.done']=value;r.write(state_file,state,private=True)
        if lane in (None,'gap') and 'release-gap.done' not in state:
            change_goal('c01-gap-goal-concept',setup.SAMPLES['inputs']['concept_goal'])
            change_goal('c01-gap-goal-numeric',setup.SAMPLES['inputs']['numeric_goal'])
            import hashlib,threading,time
            from app.data_exit.q_store import authority_for
            from app.operator.q_request import principal_id
            before=c.request('GET',f'/api/activities/{a1}/teaching/workspace');h=before['head']
            command=retain('release-gap',{'business_key':str(uuid4()),'action':'plan','expected_revision':h['revision'],'expected_goal_version':h['goal_version'],'expected_scope_revision':1,'body':{'confirmed':True}})
            path=f'/api/activities/{a1}/teaching/commands';pending=c.request('POST',path,command)
            assert pending['outbound_approval']['state']=='pending'
            row=c.approve(a1,command['business_key'])[0];operation=row['prepared']['operation_id'];base=r.PRIVATE/'flow'
            r.write(base/'faults.json',{operation:'release_gap'},private=True)
            tag=hashlib.sha256(operation.encode()).hexdigest();outcome={}
            def dispatch():
                try:outcome['receipt']=c.request('POST',path,command)
                except BaseException as exc:outcome['error_type']=type(exc).__name__
            r.count('native_business_sessions');thread=threading.Thread(target=dispatch,name='TASK120-gap-HTTP');thread.start()
            until=time.monotonic()+18
            while not (base/('gap-ready-'+tag+'.json')).exists():
                if not thread.is_alive() or time.monotonic()>=until:raise RuntimeError('actual_release_gap_not_observed')
                time.sleep(.01)
            blocking=authority_for(c.app.state.activities_ledger).revoke(row['prepared_id'],principal_id())
            assert blocking['state']=='revoked'
            r.event('release_gap_exclusive_revoke_completed',prepared_id=row['prepared_id'])
            (base/('gap-release-'+tag)).write_text('explicit fixture response release',encoding='utf-8')
            thread.join(20)
            if thread.is_alive() or outcome.get('error_type'):raise RuntimeError('release_gap_result_unconfirmed')
            after=c.request('GET',f'/api/activities/{a1}/teaching/workspace')
            assert all(after['head'][k]==before['head'][k] for k in ('revision','goal_version','goal_record_id','path_record_id','node_id','exercise_record_id','answer_record_id','feedback_record_id')),'revoked response advanced head'
            fact=run(c.app.state.activities_ledger.read_committed_result(a1,operation))
            assert fact.payload and fact.payload_sha256
            state['release-gap.done']={'prepared_id':row['prepared_id'],'operation_id':operation,'payload_sha256':fact.payload_sha256,
                'read_status':fact.read_status.value,'head_unchanged':True,'exclusive_revoke_before_result':True,'fee_not_refunded':True}
            r.write(state_file,state,private=True);r.write(r.EVIDENCE/'release-gap-result.json',state['release-gap.done'])
            command=retain('release-gap-abandon',{'business_key':str(uuid4()),'action':'abandon','expected_revision':h['revision'],'expected_goal_version':h['goal_version'],'expected_scope_revision':1,'body':{'target_business_key':command['business_key']}})
            c.request('POST',path,command)
        r.write(r.EVIDENCE/f"root-{r.state()['active_root']:02d}-{slot}-{lane or 'all'}-flow-result.json",{'execution_class':'TESTONLY','status':'PASS-for-listed-chains','chains':[key for key in state if key.endswith('.done')],
            'financials':financials(slot),'zero_provider_calls':True,'preview_created_started':[0,0]})
