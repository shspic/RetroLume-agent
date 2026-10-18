"""冻结S余项，只调用真实API/PG；输入与结果保存，合成回复不冒Q语义。"""
from batch_runtime import *
from frozen_http import SAMPLES
from uuid import uuid4
from datetime import datetime,timedelta,timezone
from concurrent.futures import ThreadPoolExecutor
import traceback

def case(name,operation,*,layer='real_HTTP_PG_Windows_with_lowest_synthetic_transport'):
    c.guard()
    try:
        value=operation();c.write(C01/(name+'.json'),{'sample':c.sample(),'status':'passed_at_stated_layer','layer':layer,'Q':'NOT_RUN','result':value});return value
    except Exception as exc:
        c.failure('S02-'+name,type(exc).__name__+':'+str(exc)[:250],effect='保存实际输入/回执；停止该受影响例，不重发已提交步骤')
        (C01/(name+'-error.txt')).write_text(traceback.format_exc(),encoding='utf-8');return None

def evaluate(flow,aid):
    h=flow.call('GET',f'/api/activities/{aid}/teaching/workspace')['head']
    return flow.teaching(aid,'evaluate',{'confirmed':True,'exercise_record_id':h['exercise_record_id'],'answer_record_id':h['answer_record_id']})

def interview_before(flow,mapping,memory,aid=None):
    marker=C01/'interview-before-normal-reopen.json'
    if marker.exists():return json.loads(marker.read_text())['activity_id']
    if aid is None:aid=flow.create([mapping['R'],mapping['M']],memory)
    w=flow.call('GET',f'/api/activities/{aid}/interview/workspace')
    if not w.get('head'):w=flow.interview(aid,'start',{'goal':{'target':SAMPLES['inputs']['interview_goal'],'focus':None,'clarifications':[],'material_roles':[{'source_id':mapping['R']['id'],'role':'resume'},{'source_id':mapping['M']['id'],'role':'measurement'}]}})
    flow.index(aid)
    if w['head']['phase']=='ready':w=flow.interview(aid,'ask',{'mode':'first'})
    if w['head']['phase']=='question_ready' and w['head']['probe_depth']==0:w=flow.interview(aid,'answer',{'question_record_id':w['head']['current_question_id'],'text':SAMPLES['inputs']['interview_incomplete_answer']})
    if w['head']['phase']=='answer_ready' and w['head']['probe_depth']==0:w=flow.interview(aid,'review',{'question_record_id':w['head']['current_question_id'],'answer_record_id':w['head']['current_answer_id']})
    assert w['head']['probe_depth']<=2
    if w['head']['phase']=='question_ready':w=flow.interview(aid,'answer',{'question_record_id':w['head']['current_question_id'],'text':SAMPLES['inputs']['interview_supported_answer']})
    c.write(marker,{'activity_id':aid,'workspace':w,'memory_id':memory['memory_id']});return aid

def interview_after(flow,aid):
    w=flow.call('GET',f'/api/activities/{aid}/interview/workspace')
    w=flow.interview(aid,'review',{'question_record_id':w['head']['current_question_id'],'answer_record_id':w['head']['current_answer_id']})
    w=flow.interview(aid,'finish',{})
    assert w['head']['phase']=='ended';return w

def setup_teaching(flow,sources,goal):
    aid=flow.create(sources);flow.index(aid)
    w=flow.teaching(aid,'goal',{'goal':goal});w=flow.teaching(aid,'plan',{'confirmed':True},query=goal)
    return aid,w

def variants(flow,mapping,alias,goal,answers):
    aid,w=setup_teaching(flow,[mapping[alias]],goal)
    w=flow.teaching(aid,'accept_path',{'proposal_record_id':w['proposal']['record_id']})
    w=flow.teaching(aid,'select_node',{'path_record_id':w['head']['path_record_id'],'node_id':'n1'})
    w=flow.teaching(aid,'exercise',{'confirmed':True,'path_record_id':w['head']['path_record_id'],'node_id':'n1','purpose':'initial'},query=goal)
    results=[]
    for answer in answers:
        h=w['head'];body={'exercise_record_id':h['exercise_record_id'],'kind':'initial' if not results else 'revision','text':answer}
        if results:body['supersedes_answer_record_id']=h['answer_record_id']
        w=flow.teaching(aid,'answer',body);w=evaluate(flow,aid)
        assert w['feedback']['qualification']=='current'
        results.append({'answer':answer,'answer_id':w['head']['answer_record_id'],'feedback':w['feedback'],'reason':w.get('reason')})
    return {'activity_id':aid,'alias':alias,'answers':results,'open_semantics':'Q_NOT_RUN','program_execution':False}

def neutral(flow,mapping,aliases,goal,expected):
    aid,w=setup_teaching(flow,[mapping[a] for a in aliases],goal)
    assert w['proposal']['result_type']==expected,w['proposal']
    return {'activity_id':aid,'workspace':w,'expected':expected}

def raw_post(flow,path,body):
    c.count('http');r=flow.client.post(path,json=body);value=r.json()
    c.write(flow.folder/(str(time.time_ns())+'.json'),{'method':'POST','path':path,'request':body,'status':r.status_code,'response':value})
    return r.status_code,value

def budget_and_keys(flow,mapping):
    import asyncio,psycopg
    from psycopg.rows import dict_row
    from app.activities.repository import ActivitySpec,SourceSnapshot,PostgresAdmissionLedger
    from app.runtime import psycopg_compatible_loop_factory
    from app.retrieval.contracts import space_identity
    aid=str(uuid4());source=mapping['N'];metadata_grant=c.sha(b'TASK117 S02 non-executable grant metadata; Q never enabled')
    spec=ActivitySpec(activity_id=aid,sources=(SourceSnapshot(source['id'],source['version_id'],source['revision']),),deadline_at=datetime.now(timezone.utc)+timedelta(hours=2),max_requests=1,max_cost_microunits=250000,reserve_cost_microunits=250000,max_request_bytes=65536,max_output_tokens=2048,max_running_seconds=3600,allowed_models=(('deepseek_chat_completions','deepseek-chat'),),outbound_grant_sha256=metadata_grant)
    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(PostgresAdmissionLedger(rc.dsn('source')).create_activity(spec))
    # A second isolated space is metadata only, never configured as an external capability.
    with psycopg.connect(rc.dsn('source'),row_factory=dict_row) as db:
        second=space_identity('zhipu_embeddings','S02-unused-metadata')
        db.execute("INSERT INTO retrieval_spaces(space_id,provider,configured_model,dimensions,normalization,chunk_recipe) VALUES(%s,'zhipu_embeddings','S02-unused-metadata',512,'l2.v1','lossless-line-2048cp.v1') ON CONFLICT DO NOTHING",(second,))
    path=f'/api/activities/{aid}/teaching/commands';body={'business_key':str(uuid4()),'expected_revision':0,'expected_goal_version':0,'expected_scope_revision':1,'action':'goal','body':{'goal':'平均速度的分钟换秒'}}
    c.count('http',2)
    def post():
        r=flow.client.post(path,json=body);return {'status':r.status_code,'body':r.json()}
    with ThreadPoolExecutor(max_workers=2) as pool:concurrent=list(pool.map(lambda _:post(),range(2)))
    assert all(r['status']==200 and r['body']['status']=='committed' for r in concurrent),concurrent
    code,conflict=raw_post(flow,path,{**body,'body':{'goal':'同键异文应拒绝'}});assert code==409
    status=flow.call('GET',f'/api/activities/{aid}/retrieval/status');flow.index(aid)
    code,refusal=raw_post(flow,f'/api/activities/{aid}/retrieval/commands',{'business_key':str(uuid4()),'action':'query','expected_scope_revision':1,'expected_domain_revision':status['domain_revision'],'query':'平均速度','confirmed':True});assert code==409 and 'retrieval_workflow_budget_insufficient' in str(refusal)
    with psycopg.connect(rc.dsn('source'),row_factory=dict_row) as db:
        row=db.execute('SELECT requests_reserved,cost_reserved_microunits,outbound_grant_sha256 FROM activities WHERE id=%s',(aid,)).fetchone()
        assert row['requests_reserved']==row['cost_reserved_microunits']==0
        assert db.execute("SELECT count(*) AS n FROM retrieval_commands WHERE activity_id=%s AND action='query'",(aid,)).fetchone()['n']==0
        assert db.execute("SELECT count(*) AS n FROM teaching_records WHERE activity_id=%s AND kind='goal'",(aid,)).fetchone()['n']==1
    return {'activity_id':aid,'same_key_concurrent':concurrent,'different_body':conflict,'query_then_model_refusal':refusal,'budget_after':row,'second_space_id':second,'grant_metadata_only':True,'Q_roster_created':0}

def late_memory(flow,mapping,memory,learning_aid):
    mid=memory['memory_id'];gates=C01/'late-transport';gates.mkdir(exist_ok=True);results=[]
    for action in ('revise','revoke'):
        current=flow.call('GET','/api/memories/'+mid)
        if action=='revise':aid=learning_aid
        else:
            aid=flow.create([mapping['R'],mapping['M']],current)
            flow.interview(aid,'start',{'goal':{'target':SAMPLES['inputs']['interview_goal'],'material_roles':[{'source_id':mapping['R']['id'],'role':'resume'},{'source_id':mapping['M']['id'],'role':'measurement'}]}})
            flow.index(aid)
        status=flow.call('GET',f'/api/activities/{aid}/retrieval/status')
        for path in (gates/'ready.json',gates/'release'):path.unlink(missing_ok=True)
        command={'business_key':str(uuid4()),'action':'query','expected_scope_revision':status['scope_revision'],'expected_domain_revision':status['domain_revision'],'query':'S02晚到记忆','confirmed':True}
        c.count('http');c.count('native_windows')
        with ThreadPoolExecutor(max_workers=1) as pool:
            future=pool.submit(flow.client.post,f'/api/activities/{aid}/retrieval/commands',json=command)
            try:
                end=time.monotonic()+28
                while not(gates/'ready.json').exists():
                    if future.done() or time.monotonic()>=end:raise RuntimeError('late_transport_did_not_reach_dispatch')
                    time.sleep(.05)
                impact=flow.call('GET',f"/api/memories/{mid}/impact?expected_revision={current['revision']}&action={action}")
                body={'title':'S02偏好','kind':'preference','text':SAMPLES['inputs']['memory_revised_body'],'base_body_sha256':current['body_sha256'],'impact_token':impact['impact_token']} if action=='revise' else {'impact_token':impact['impact_token'],'confirm_revoke':True,'purge_memory_content':True}
                changed=flow.call('POST','/api/memories/commands',{'business_key':str(uuid4()),'memory_id':mid,'expected_revision':current['revision'],'action':action,'body':body})
            finally:(gates/'release').write_text('release',encoding='ascii')
            r=future.result(timeout=105);response=r.json()
        assert not response.get('current'),response
        selection=flow.call('GET',f'/api/activities/{aid}/memory-selection');assert not selection['eligible']
        after=flow.call('GET','/api/memories/'+mid)
        if action=='revoke':assert after['body'] is None and after['purge_state']=='done'
        results.append({'action':action,'activity_id':aid,'query':command,'HTTP':r.status_code,'late_receipt':response,'change':changed,'selection':selection,'memory_after':after})
        c.write(C01/'X02-late-memory-progress.json',results)
    return results

def delete_auxiliary(flow):
    import psycopg
    from psycopg.rows import dict_row
    unknown=json.loads((C01/'unknown-before-normal-reopen.json').read_text());sid=unknown['source_id']
    material=next(x for x in flow.call('GET','/api/materials')['items'] if x['id']==sid)
    impact=flow.call('POST',f'/api/data/materials/{sid}/deletion-preview',{'expected_revision':material['revision']})
    deleted=flow.call('POST',f'/api/data/materials/{sid}/deletions',{'expected_revision':material['revision'],'impact_sha256':impact['impact_sha256'],'business_key':str(uuid4()),'confirm':True})
    with psycopg.connect(rc.dsn('source'),row_factory=dict_row) as db:
        chunks=db.execute('SELECT count(*) AS n FROM retrieval_chunks WHERE source_id=%s',(sid,)).fetchone()['n']
        bodies=db.execute("SELECT count(*) AS n FROM activity_operation_results r JOIN activity_operations o USING(activity_id,operation_id) WHERE o.kind='embedding' AND o.activity_id=%s",(unknown['activity_id'],)).fetchone()['n']
        tombstones=db.execute('SELECT count(*) AS n FROM data_tombstones WHERE entity_kind=\'source\' AND entity_id=%s',(sid,)).fetchone()['n']
        assert chunks==bodies==0 and tombstones>=1
    return {'source_id':sid,'impact':impact,'receipt':deleted,'remaining_chunks':chunks,'remaining_embedding_007':bodies,'tombstones':tombstones,'unknown_and_reserved_metadata_retained':True}
