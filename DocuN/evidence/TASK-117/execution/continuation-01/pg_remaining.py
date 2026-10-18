"""不启动API/Browser/Native的真实普通角色PG定向余项；不冒HTTP或迟到门。"""
from profiles_batch import *
import asyncio,dataclasses
from app.activities.repository import ActivitySpec,SourceSnapshot
from app.learning.teaching_contracts import TeachingCommandInput,TeachingRefusal
from app.retrieval.contracts import RetrievalCommandInput,RetrievalRefusal,space_identity
from app.memory.contracts import MemorySelectionInput,MemoryCommandInput
from app.memory.service import MemoryService
from app.interview.contracts import parse_command
from app.runtime import psycopg_compatible_loop_factory
from datetime import datetime,timedelta,timezone

def activity(mapping,aliases,*,one=False):
    return ActivitySpec(activity_id=str(uuid4()),sources=tuple(SourceSnapshot(mapping[a]['id'],mapping[a]['version_id'],mapping[a]['revision']) for a in aliases),deadline_at=datetime.now(timezone.utc)+timedelta(hours=2),max_requests=1 if one else 80,max_cost_microunits=250000 if one else 20000000,reserve_cost_microunits=250000,max_request_bytes=65536,max_output_tokens=2048,max_running_seconds=3600,allowed_models=(('deepseek_chat_completions','deepseek-chat'),),outbound_grant_sha256=c.sha(b'S02 metadata only, never activated') if one else None)

async def budget_keys(runtime,mapping):
    ledger=runtime.app.state.activities_ledger;spec=activity(mapping,['N'],one=True)
    await ledger.create_activity(spec)
    command=TeachingCommandInput(business_key=str(uuid4()),expected_revision=0,expected_goal_version=0,expected_scope_revision=1,action='goal',body={'goal':'平均速度的分钟换秒'})
    receipts=await asyncio.gather(*(ledger.apply_teaching_local(spec.activity_id,command) for _ in range(2)))
    assert all(r.status=='committed' for r in receipts)
    try:await ledger.apply_teaching_local(spec.activity_id,command.model_copy(update={'body':{'goal':'同键异文必须拒绝'}}))
    except TeachingRefusal as exc:assert exc.code=='command_key_conflict'
    else:raise AssertionError('different body accepted')
    context=await ledger.retrieval_context(spec.activity_id)
    query=RetrievalCommandInput(business_key=str(uuid4()),action='query',expected_scope_revision=1,expected_domain_revision=context['domain_revision'],query='平均速度',confirmed=True)
    source=mapping['N'];refs=[{'source_id':source['id'],'source_version_id':source['version_id'],'source_revision':source['revision']}]
    body={k:context[k] for k in ('domain','parent_refs','memory_selection_sha256','memory_dependency_sha256')}
    try:await ledger.retrieval_freeze(spec.activity_id,query,body,{'space_id':space_identity('zhipu_embeddings','embedding-3'),'provider':'zhipu_embeddings','configured_model':'embedding-3'},[],1,refs,c.sha('平均速度'.encode()))
    except RetrievalRefusal as exc:assert exc.code=='retrieval_workflow_budget_insufficient'
    else:raise AssertionError('query then model admitted with one request')
    with psycopg.connect(rc.dsn('source'),row_factory=dict_row) as db:
        row=db.execute('SELECT requests_reserved,cost_reserved_microunits,outbound_grant_sha256 FROM activities WHERE id=%s',(spec.activity_id,)).fetchone()
        assert row['requests_reserved']==row['cost_reserved_microunits']==0
        assert db.execute("SELECT count(*) AS n FROM teaching_records WHERE activity_id=%s AND kind='goal'",(spec.activity_id,)).fetchone()['n']==1
        assert db.execute('SELECT count(*) AS n FROM retrieval_commands WHERE activity_id=%s',(spec.activity_id,)).fetchone()['n']==0
        db.execute('SELECT public.data_mutation_enter()')
        second=space_identity('zhipu_embeddings','S02-unused-metadata')
        db.execute("INSERT INTO retrieval_spaces(space_id,provider,configured_model,dimensions,normalization,chunk_recipe) VALUES(%s,'zhipu_embeddings','S02-unused-metadata',512,'l2.v1','lossless-line-2048cp.v1') ON CONFLICT DO NOTHING",(second,))
    from app.retrieval.repository import plain
    return {'activity_id':spec.activity_id,'same_key_concurrent_receipts':[plain(dataclasses.asdict(r)) if dataclasses.is_dataclass(r) else r.model_dump(mode='json') for r in receipts],'budget':row,'retrieval_commands_inserted':0,'second_space':second,'metadata_only_grant':True,'Q_roster_created':0,'Native_windows':0,'layer':'real PG, no HTTP/UI/concurrency claim for global paid roster'}

async def memory_changes(runtime,mapping):
    ledger=runtime.app.state.activities_ledger;service=MemoryService(ledger)
    mid=json.loads((C01/'frozen-memory-binding.json').read_text())['memory_id']
    learning=json.loads((C01/'memory-teaching-before-reopen.json').read_text())['activity_id'];results=[]
    for action in ('revise','revoke'):
        memory=await ledger.read_memory_snapshot(mid)
        spec=activity(mapping,['R','M'])
        selection=MemorySelectionInput(confirmed=True,entries=[{k:memory[k] for k in ('memory_id','version','revision','body_sha256')}])
        await ledger.create_activity(spec,memory_selection=selection)
        start=parse_command({'schema':'interview.command.v2','business_key':str(uuid4()),'expected_head_revision':0,'expected_goal_version':0,'expected_scope_revision':1,'action':'start','body':{'goal':{'target':'冻结合成R+M面试的本地记忆资格','material_roles':[{'source_id':mapping['R']['id'],'role':'resume'},{'source_id':mapping['M']['id'],'role':'measurement'}]}},'retrieval_ref':None})
        await ledger.apply_interview_local(spec.activity_id,start)
        assert (await ledger.retrieval_context(spec.activity_id))['current']
        impact=await ledger.preview_memory_change(mid,memory['revision'],action)
        if action=='revise':
            samples=json.loads((ROOT/'DocuN/evidence/TASK-116/design/sample-inputs.json').read_text())
            body={'kind':'preference','title':'S02偏好','text':samples['inputs']['memory_revised_body'],'base_body_sha256':memory['body_sha256'],'impact_token':impact['impact_token']}
        else:body={'impact_token':impact['impact_token'],'confirm_revoke':True,'purge_memory_content':True}
        receipt=await service.submit_command(MemoryCommandInput(business_key=str(uuid4()),memory_id=mid,expected_revision=memory['revision'],action=action,body=body))
        contexts={aid:await ledger.retrieval_context(aid) for aid in (learning,spec.activity_id)}
        assert all(not r['current'] for r in contexts.values())
        after=await ledger.read_memory_snapshot(mid)
        if action=='revoke':assert after['body'] is None and after['purge_state']=='done'
        results.append({'action':action,'memory_before':memory,'interview_id':spec.activity_id,'receipt':receipt,'contexts':contexts,'memory_after':after,'late_dispatch':'NOT_RUN; no Native launched','HTTP_browser':'NOT_RUN'})
    return results

async def delete_source(runtime):
    unknown=json.loads((C01/'unknown-before-normal-reopen.json').read_text());sid=unknown['source_id']
    with psycopg.connect(rc.dsn('source'),row_factory=dict_row) as db:revision=db.execute('SELECT revision FROM material_sources WHERE id=%s',(sid,)).fetchone()['revision']
    impact=runtime.deletions.preview(sid,revision)
    receipt=await runtime.deletions.confirm(sid,revision,impact['impact_sha256'],str(uuid4()))
    with psycopg.connect(rc.dsn('source'),row_factory=dict_row) as db:
        chunks=db.execute('SELECT count(*) AS n FROM retrieval_chunks WHERE source_id=%s',(sid,)).fetchone()['n']
        bodies=db.execute("SELECT count(*) AS n FROM activity_operation_results r JOIN activity_operations o USING(activity_id,operation_id) WHERE o.kind='embedding' AND o.activity_id=%s",(unknown['activity_id'],)).fetchone()['n']
        tombstones=db.execute("SELECT count(*) AS n FROM data_tombstones WHERE entity_kind='source' AND entity_id=%s",(sid,)).fetchone()['n']
        assert chunks==bodies==0 and tombstones>=1
    return {'source_id':sid,'impact':impact,'receipt':receipt,'remaining_chunks':chunks,'remaining_embedding_007':bodies,'tombstones':tombstones,'layer':'original product deletion service and actual PG, no HTTP/UI claim'}

def run_async(operation):
    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:return runner.run(operation)
