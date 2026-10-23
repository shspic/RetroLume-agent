"""Finite actual PG/source/memory/scope races at the real released dispatch gap."""
import hashlib,json,threading,time
from uuid import uuid4
from . import resources as r,setup
from .api_runtime import application,run,financials
from app.capabilities.q_protocol import ROSTER,raw_digest

def run_races():
    slot='budget-02';base=r.PRIVATE/slot;file=base/'c02-races.json'
    state=json.loads(file.read_text(encoding='utf-8')) if file.exists() else {}
    def retain(name,value):
        if name not in state:state[name]=value;r.write(file,state,private=True)
        return state[name]
    def remember(name,value):state[name]=value;r.write(file,state,private=True);return value
    with application(slot) as c:
        import psycopg
        from psycopg.rows import dict_row
        from app.data_exit.q_store import authority_for
        authority=authority_for(c.app.state.activities_ledger)
        sources=json.loads((base/'sources.json').read_text(encoding='utf-8'))
        def head(aid):
            with psycopg.connect(setup.dsn(slot),row_factory=dict_row) as db:
                row=db.execute('SELECT revision,goal_version,scope_revision,goal_record_id::text,current_question_id::text,current_answer_id::text,current_feedback_id::text FROM interview_heads WHERE activity_id=%s',(aid,)).fetchone()
            return row
        def local_goal(aid,name):
            before=head(aid);path=f'/api/activities/{aid}/interview/commands'
            body=retain(name,{'schema':'interview.command.v2','business_key':str(uuid4()),'action':'goal' if before else 'start','expected_head_revision':before['revision'] if before else 0,'expected_goal_version':before['goal_version'] if before else 0,'expected_scope_revision':1,'body':{'goal':{'target':setup.SAMPLES['inputs']['interview_goal'],'material_roles':[]}}})
            if name+'.done' not in state:remember(name+'.done',c.request('POST',path,body))
        def retrieval(aid,name,action):
            if name+'.done' in state:return state[name+'.done']
            current=c.request('GET',f'/api/activities/{aid}/retrieval/status')
            body=retain(name,{'business_key':str(uuid4()),'action':action,'expected_scope_revision':1,'expected_domain_revision':current['domain_revision'],'confirmed':True,**({'query':setup.SAMPLES['inputs']['interview_goal']} if action=='query' else {})})
            url=f'/api/activities/{aid}/retrieval/commands';pending=c.request('POST',url,body)
            if pending['terminal_disposition']=='received':return remember(name+'.done',pending)
            if action=='source_index' and pending['terminal_disposition']=='cache_ready':
                status=c.request('GET',f'/api/activities/{aid}/retrieval/status')
                if not status['ready'] or status['cached_fragments']!=status['fragments'] or not status['fragments']:raise RuntimeError('race_cache_not_complete')
                return remember(name+'.done',pending)
            rows=c.approve(aid,body['business_key'])
            for row in rows:r.count('native_business_sessions')
            value=c.request('POST',url,body)
            if value['terminal_disposition']!='received':raise RuntimeError('race_prerequisite_query_failed')
            return remember(name+'.done',value)
        proofs=[]
        # Source and scope use the other two original fixed activities; the
        # memory-selected A2 remains valid until its final memory race.
        for name,aid in [('scope',ROSTER[2]),('source',ROSTER[0]),('memory',ROSTER[1])]:
            if name+'.done' in state:proofs.append(state[name+'.done']);continue
            local_goal(aid,name+'-goal')
            if name!='memory':retrieval(aid,name+'-index','source_index')
            query=retrieval(aid,name+'-query','query');h=head(aid);url=f'/api/activities/{aid}/interview/commands'
            body=retain(name+'-model',{'schema':'interview.command.v2','business_key':str(uuid4()),'action':'ask','expected_head_revision':h['revision'],'expected_goal_version':h['goal_version'],'expected_scope_revision':h['scope_revision'],'body':{'mode':'first'},'retrieval_ref':query['retrieval_ref']})
            pending=c.request('POST',url,body)
            if pending.get('launch_claimed'):raise RuntimeError('retained_race_claim_must_not_be_resent')
            row=c.approve(aid,body['business_key'])[0];operation=row['prepared']['operation_id'];before=financials(slot)
            faults_file=base/'faults.json';faults=json.loads(faults_file.read_text(encoding='utf-8')) if faults_file.exists() else {};faults[operation]='release_gap';r.write(faults_file,faults,private=True)
            tag=hashlib.sha256(operation.encode()).hexdigest();ready=base/('gap-ready-'+tag+'.json');outcome={}
            def send():
                try:outcome['receipt']=c.request('POST',url,body)
                except BaseException as exc:outcome['error_type']=type(exc).__name__
            r.count('native_business_sessions');worker=threading.Thread(target=send,name='TASK120-c02-'+name);worker.start()
            until=time.monotonic()+18
            try:
                while not ready.exists():
                    if not worker.is_alive() or time.monotonic()>=until:raise RuntimeError('actual_'+name+'_released_gap_not_observed')
                    time.sleep(.01)
                window=json.loads(ready.read_text(encoding='utf-8'));assert window['dispatch_released']
                mutation_started=r.utc()
                if name=='scope':
                    entries=[{'source_id':str(sources[a]['id']),'version_id':str(sources[a]['version_id']),'source_revision':sources[a]['revision'],'original_sha256':sources[a]['sha256']} for a in ('N','R')]
                    mutation=retain('scope-mutation',{'schema':'interview.command.v2','business_key':str(uuid4()),'action':'bind_scope','expected_head_revision':h['revision'],'expected_goal_version':h['goal_version'],'expected_scope_revision':h['scope_revision'],'body':{'sources':entries,'material_roles':[]}})
                    changed=c.request('POST',url,mutation)
                elif name=='source':
                    # A real production material version, same frozen bytes;
                    # no SQL mutation and no expansion of allowed input text.
                    sample=next(x for x in setup.SAMPLES['sources'] if x['alias']=='N');old=sources['N'];raw=sample['text'].encode()
                    refs=c.app.state.data_exit.references;prepared=refs.prepare_reference(raw_digest(raw),len(raw),source_id=str(old['id']))
                    with refs.acquire_shared(prepared) as pin:
                        import io
                        original=c.app.state.originals.put(io.BytesIO(raw),max_bytes=5*1024**2,reference_pin=pin)
                        changed=c.app.state.materials.save(source_id=str(old['id']),expected_version=str(old['version_id']),filename=sample['filename'],format=sample['filename'].rsplit('.',1)[1],sha256=original.sha256,size=original.size,reference_pin=pin,prepared_ids=prepared)
                    if changed['revision']!=old['revision']+1:raise RuntimeError('source_race_version_not_changed')
                else:
                    from app.memory.contracts import MemoryCommandInput
                    from app.memory.service import MemoryService
                    selected=run(c.app.state.activities_ledger.read_memory_selection(aid,include_bodies=False))['entries'][0]
                    preview=run(c.app.state.activities_ledger.preview_memory_change(selected['memory_id'],selected['revision'],'revoke'))
                    mutation=retain('memory-mutation',{'business_key':str(uuid4()),'memory_id':selected['memory_id'],'expected_revision':selected['revision'],'action':'revoke','body':{'impact_token':preview['impact_token'],'confirm_revoke':True,'purge_memory_content':True}})
                    changed=run(MemoryService(c.app.state.activities_ledger).submit_command(MemoryCommandInput.model_validate(mutation)))
                after_mutation=head(aid)
                r.event('actual_c02_exclusive_mutation_completed',case=name,operation_id=operation,actor_pid=__import__('os').getpid(),actor_thread=threading.get_ident(),worker_pid=window['worker_pid'])
            finally:(base/('gap-release-'+tag)).write_text('explicit synthetic response release',encoding='utf-8')
            worker.join(20)
            if worker.is_alive() or outcome.get('error_type'):raise RuntimeError('actual_'+name+'_result_not_reconciled')
            with psycopg.connect(setup.dsn(slot),row_factory=dict_row) as db:
                fact=db.execute('SELECT o.state,r.payload,r.payload_sha256 FROM activity_operations o JOIN activity_operation_results r USING(activity_id,operation_id) WHERE o.activity_id=%s AND o.operation_id=%s',(aid,operation)).fetchone()
            if not fact or fact['state']!='received' or raw_digest(fact['payload'])!=fact['payload_sha256']:raise RuntimeError('race_immutable_007_not_retained_'+name)
            if head(aid)!=after_mutation:raise RuntimeError('late_result_advanced_invalidated_head_'+name)
            after=financials(slot)
            if after['requests']!=before['requests']+1 or after['cost']!=before['cost']+250000:raise RuntimeError('race_fee_not_retained_'+name)
            from app.operator.q_request import inspect_request
            from app.capabilities.contracts import AdmissionDenied
            from app.data_exit.contracts import DataError
            try:inspection=run(inspect_request(c.app.state.activities_ledger,row['prepared_id']))
            except (AdmissionDenied,DataError) as exc:inspection={'request_available':False,'denial':getattr(exc,'code',str(exc))}
            if inspection.get('request_available'):raise RuntimeError('invalidated_request_body_returned_'+name)
            proof=remember(name+'.done',{'case':name,'activity_id':aid,'operation_id':operation,'prepared_id':row['prepared_id'],'007_payload_sha256':fact['payload_sha256'],'window':window,'mutation_started':mutation_started,'head_after_mutation':after_mutation,'late_result_head_unchanged':True,'fees_retained':True,'invalidated_inspection_returns_no_body':True,'never_resent_after_claim':True})
            proofs.append(proof);r.write(r.EVIDENCE/f"root-{r.state()['active_root']:02d}-c02-mutation-races.json",{'status':'PASS_FOR_COMPLETED_CASES','cases':proofs,'real_PG':True,'provider_calls':0})
