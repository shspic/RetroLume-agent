"""TASK120 original-instance PG observations, never financial fixture UPDATEs."""
from . import resources as r,setup
from .api_runtime import run,financials


def run_budget():
    import asyncio,json,os,time
    from uuid import uuid4
    import psycopg
    from psycopg.rows import dict_row
    from app.capabilities.q_protocol import ROSTER
    from app.capabilities.contracts import ModelCallRequest,CallContext,CallStatus,AdmissionIntent,AdmissionDenied
    from app.capabilities.gateway import ControlledModelGateway
    from app.capabilities.embedding import ControlledEmbeddingGateway,EmbeddingRequest,EmbeddingAdmissionIntent
    from app.capabilities.q_context import claim_approved,prepare
    from app.data_exit.q_store import authority_for
    from app.operator.q_request import inspect_request,approve_request
    from app.learning.teaching_service import TeachingService
    from app.learning.teaching_contracts import TeachingCommandInput
    from app.retrieval.service import RetrievalService
    from app.retrieval.contracts import RetrievalCommandInput
    setup.environment('budget-01',include_admin=False)
    from .transport import install
    install()
    from app.main import create_app
    app=create_app();ledger=app.state.activities_ledger;config=app.state.activity_config
    if not app.state.q_readiness['available']:raise RuntimeError('budget_actual_loader_not_ready')
    service=TeachingService(ledger,app.state.materials,app.state.originals)
    root=authority_for(ledger);base=r.PRIVATE/'budget-01'
    progress_file=base/'baseline-progress.json'
    progress=json.loads(progress_file.read_text(encoding='utf-8')) if progress_file.exists() else {'completed':{},'commands':{}}
    async def local(aid,action,body):
        view=await ledger.read_teaching_workspace(aid);h=view['head'] or {}
        command=TeachingCommandInput(business_key=str(uuid4()),action=action,expected_revision=h.get('revision',0),expected_goal_version=h.get('goal_version',0),expected_scope_revision=1,body=body)
        return await ledger.apply_teaching_local(aid,command)
    async def approve(row):
        inspected=await inspect_request(ledger,row['prepared_id'])
        if not inspected['request_available']:raise RuntimeError('budget_inspection_invalidated')
        await approve_request(ledger,row['prepared_id'],inspected['prepared_sha256'])
    async def pending(aid,name):
        view=await ledger.read_teaching_workspace(aid);h=view['head']
        body=progress['commands'].get(name)
        if body is None:
            body={'business_key':str(uuid4()),'action':'plan','expected_revision':h['revision'],'expected_goal_version':h['goal_version'],'expected_scope_revision':1,'body':{'confirmed':True}}
            progress['commands'][name]=body;r.write(progress_file,progress,private=True)
        command=TeachingCommandInput.model_validate(body)
        result=await service.submit_command(aid,command,config,run_tag='budget-freeze')
        if result.status!='accepted':raise RuntimeError('budget_pending_original_requires_reconciliation')
        row=root.by_operation(aid,command.operation_id(aid));await approve(row)
        actual=ModelCallRequest.model_validate_json(json.dumps(root.artifact(row)['request']))
        configured=config.model_service.model_copy(update={'outbound_authorization':root.reference(root.request(row['prepared_id']))})
        decision=await claim_approved(ledger,configured,lambda:ledger.claim_teaching_launch(aid,command.business_key,result.request_sha256))
        if not decision['launch_allowed']:raise RuntimeError('budget_launch_not_allowed')
        return command,actual,configured
    async def go():
        leases={};started={}
        async def finish(aid,lease,begin):
            await ledger.begin_window_close(aid,'task120-budget',lease.execution_generation)
            await ledger.settle_execution_window(aid,'task120-budget',lease.execution_generation,window_seconds=lease.window_seconds,elapsed_seconds=time.monotonic()-begin)
        for aid,target in zip(ROSTER,(47,28,24)):
            # A prior stopped fixture may have left its running-time reserve.
            # Only the production expired-lease fold may conservatively charge
            # it. No fabricated elapsed measurement or financial UPDATE.
            with psycopg.connect(setup.dsn('budget-01'),row_factory=dict_row) as connection:
                old=connection.execute('SELECT status,executor_id,lease_expires_at,CURRENT_TIMESTAMP AS observed_at FROM activities WHERE id=%s',(aid,)).fetchone()
            if old['status']=='running':
                if old['executor_id']!='task120-budget' or old['lease_expires_at']>old['observed_at']:raise RuntimeError('prior_budget_lease_not_expired')
                begin=time.monotonic();lease=await ledger.claim_lease(aid,'task120-budget',lease_seconds=90,window_seconds=90)
                if lease is None:raise RuntimeError('budget_running_reserve_exhausted')
                await finish(aid,lease,begin)
                r.event('actual_expired_budget_window_folded',activity_id=aid,old_elapsed_unknown=True,old_reserve_not_refunded=True)
            view=await ledger.read_teaching_workspace(aid)
            if view['head'] is None:await local(aid,'goal',{'goal':setup.SAMPLES['inputs']['numeric_goal']})
            for ordinal in range(progress['completed'].get(aid,0),target):
                command,request,configured=await pending(aid,aid+'.'+str(ordinal))
                operation=command.operation_id(aid)
                begin=time.monotonic();lease=await ledger.claim_lease(aid,'task120-budget',lease_seconds=90,window_seconds=90)
                if lease is None:raise RuntimeError('budget_lease_unavailable')
                # Determinately NOT_SENT keeps the real financial reservation
                # while permitting a fresh explicit business intent in this
                # parent slot. UNKNOWN is retained by the final race winner;
                # it must never be reused to build this baseline.
                mode='not_sent'
                r.write(base/'faults.json',{operation:mode},private=True)
                context=CallContext(activity_id=aid,operation_id=operation,executor_id='task120-budget',execution_generation=lease.execution_generation,scope_revision=1)
                try:result=await ControlledModelGateway(configured,ledger=ledger).call(context,request)
                finally:await finish(aid,lease,begin)
                expected=CallStatus.NOT_SENT if mode=='not_sent' else CallStatus.UNKNOWN
                if result.status is not expected:raise RuntimeError('budget_baseline_actual_gateway_'+str(result.error_code))
                await local(aid,'abandon',{'target_business_key':command.business_key})
                progress['completed'][aid]=ordinal+1;r.write(progress_file,progress,private=True)
        baseline=financials('budget-01')
        if [row['requests_reserved'] for row in baseline['activities']]!=[47,28,24] or (baseline['requests'],baseline['cost'])!=(99,24750000):raise RuntimeError('actual_99_baseline_mismatch')
        r.write(r.EVIDENCE/'budget-99-baseline.json',baseline)
        aid=ROSTER[0];view=await ledger.read_teaching_workspace(aid);h=view['head']
        command=TeachingCommandInput(business_key=str(uuid4()),action='plan',expected_revision=h['revision'],expected_goal_version=h['goal_version'],expected_scope_revision=1,body={'confirmed':True})
        frozen,identity=await service._freeze_model_context(aid,command,config)
        await ledger.accept_teaching_command(aid,command,frozen)
        retrieval=RetrievalService(ledger,app.state.materials,app.state.originals)
        status=await retrieval.status(aid,app.state.integration_config)
        emb_command=RetrievalCommandInput(business_key=str(uuid4()),action='source_index',expected_scope_revision=1,expected_domain_revision=status['domain_revision'],confirmed=True)
        receipt=await retrieval.submit(aid,emb_command,app.state.integration_config)
        profile=service._build_profile(aid,command,frozen,identity)
        request=ModelCallRequest(messages=[{'role':m['role'],'content':m['content']} for m in frozen.messages],max_output_tokens=frozen.max_output_tokens,allowed_tools=frozenset(),teaching_profile=profile)
        _,configured=await prepare(ledger,aid,command.business_key,command.operation_id(aid),request,config.model_service,ControlledModelGateway(config.model_service)._build_payload(request),domain='teaching',action='plan')
        model_row=root.by_operation(aid,command.operation_id(aid));emb_row=next(row for row in root.hub.state()['q']['requests'].values() if row['prepared']['business_key']==emb_command.business_key)
        await approve(model_row);await approve(emb_row)
        configured=config.model_service.model_copy(update={'outbound_authorization':root.reference(root.request(model_row['prepared_id']))})
        embedded=app.state.integration_config.service.model_copy(update={'outbound_authorization':root.reference(root.request(emb_row['prepared_id']))})
        emb_request=EmbeddingRequest.model_validate_json(json.dumps(root.artifact(emb_row)['request']))
        await claim_approved(ledger,configured,lambda:ledger.claim_teaching_launch(aid,command.business_key,command.request_sha256(aid)))
        await claim_approved(ledger,embedded,lambda:ledger.retrieval_claim(aid,emb_command.business_key,emb_row['prepared']['command_request_sha256']))
        started[aid]=time.monotonic();lease=await ledger.claim_lease(aid,'task120-budget',lease_seconds=90,window_seconds=90)
        if lease is None:raise RuntimeError('budget_race_lease_unavailable')
        leases[aid]=lease
        mc=CallContext(activity_id=aid,operation_id=model_row['prepared']['operation_id'],executor_id='task120-budget',execution_generation=lease.execution_generation,scope_revision=1)
        ec=CallContext(activity_id=aid,operation_id=emb_row['prepared']['operation_id'],executor_id='task120-budget',execution_generation=lease.execution_generation,scope_revision=1)
        r.write(base/'faults.json',{mc.operation_id:'unknown',ec.operation_id:'unknown'},private=True)
        # A genuine administrative session holds the same production advisory
        # key while two independent production connections enter their SUM gate.
        with psycopg.connect(setup.dsn('budget-01',True),autocommit=True,row_factory=dict_row) as barrier:
            barrier.execute("SELECT pg_advisory_lock(hashtextextended('retrolume.outbound-roster.v1',0))")
            tasks=[asyncio.create_task(ControlledModelGateway(configured,ledger=ledger).call(mc,request)),asyncio.create_task(ControlledEmbeddingGateway(embedded,ledger=ledger).call(ec,emb_request))]
            until=time.monotonic()+1.7;waiting=[]
            try:
                while time.monotonic()<until:
                    waiting=barrier.execute("SELECT pid,wait_event_type,wait_event FROM pg_stat_activity WHERE datname=current_database() AND pid<>pg_backend_pid() AND wait_event='advisory' ORDER BY pid").fetchall()
                    if len(waiting)>=2:break
                    await asyncio.sleep(.01)
            finally:barrier.execute("SELECT pg_advisory_unlock(hashtextextended('retrolume.outbound-roster.v1',0))")
            results=await asyncio.gather(*tasks)
            if len(waiting)!=2 or waiting[0]['pid']==waiting[1]['pid']:raise RuntimeError('two_actual_backend_lock_window_not_observed')
        final=financials('budget-01')
        if (final['requests'],final['cost'])!=(100,25000000):raise RuntimeError('actual_100_final_mismatch')
        statuses=[result.status.value for result in results]
        if statuses.count('unknown')!=1 or statuses.count('rejected')!=1:raise RuntimeError('last_slot_outcomes_invalid')
        from app.capabilities.contracts import Provider
        negative=[]
        async with root.async_policy(shared=True):
            intents=[AdmissionIntent(mc,Provider(configured.provider),configured.model,model_row['prepared']['payload_bytes_count'],request.max_output_tokens,(),outbound_grant=configured.outbound_grant,outbound_source_manifest=configured.outbound_source_manifest),
                EmbeddingAdmissionIntent(ec,embedded.model,emb_row['prepared']['payload_bytes_count'],emb_request.binding,emb_request,embedded.outbound_grant,embedded.outbound_source_manifest)]
            for method,intent in zip((ledger.admit,ledger.admit_embedding),intents):
                try:await method(intent)
                except AdmissionDenied as exc:
                    if str(exc)!='outbound_grant_exhausted':raise
                    negative.append({'provider':str(intent.provider),'denial':str(exc),'stage':'actual_production_global_SUM_before_later_Q_proof'})
                else:raise RuntimeError('post100_admitted')
        if financials('budget-01')!=final:raise RuntimeError('post100_negative_changed_financials')
        r.write(r.EVIDENCE/'budget-last-slot-race.json',{'waiting_backends':waiting,'baseline':{'requests':99,'cost':24750000},'final':final,'model_status':statuses[0],'embedding_status':statuses[1],
            'post100_both_providers':negative,'real_production_connections':True,'same_eligible_lease':{'activity_id':aid,'generation':lease.execution_generation},'provider_calls':0,'fee':0})
        for current,lease in leases.items():
            await ledger.begin_window_close(current,'task120-budget',lease.execution_generation)
            elapsed=time.monotonic()-started[current]
            await ledger.settle_execution_window(current,'task120-budget',lease.execution_generation,window_seconds=lease.window_seconds,elapsed_seconds=elapsed)
    run(go())


def run_reopen():
    import json,os
    setup.environment('flow',include_admin=False)
    from .transport import install
    install()
    from app.main import create_app
    app=create_app();ledger=app.state.activities_ledger
    state=json.loads((r.PRIVATE/'flow/flow-progress.json').read_text(encoding='utf-8'))
    commands=[]
    for name,body in state.items():
        if name.endswith('.done') or not name.startswith('teaching-'):continue
        value=run(ledger.read_teaching_command('01800000-0000-4000-8000-000000000001',body['business_key']))
        if value:
            row=value['command'];commands.append({'name':name,**{key:row.get(key) for key in ('business_key','status','operation_id','error_code','launch_claimed_at','obsolete_at','abandoned_at')}})
    from app.data_exit.codec import plain
    r.write(r.EVIDENCE/f"root-{r.state()['active_root']:02d}-batch-{int(os.environ.get('RETROLUME_TASK120_BATCH','0')):02d}-original-pg-observation.json",plain({'commands':commands,'financials':financials('flow'),'q_readiness':app.state.q_readiness}))
    if (r.EVIDENCE/'budget-last-slot-race.json').exists():
        final=financials('budget-01')
        if (final['requests'],final['cost'])!=(100,25000000):raise RuntimeError('budget_reopen_changed_SUM')
        r.write(r.EVIDENCE/f"root-{r.state()['active_root']:02d}-budget-reopen.json",{'same_database':True,'requests':final['requests'],'cost':final['cost'],'financials':final,'execution_authority_restored':False})
