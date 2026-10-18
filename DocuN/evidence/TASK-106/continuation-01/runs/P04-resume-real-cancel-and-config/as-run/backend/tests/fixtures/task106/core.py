"""Normal real PG/domain/native SUP group; lower transport alone is fictional."""
from __future__ import annotations
import asyncio,io,json,os,secrets,sys
from datetime import datetime,timedelta,timezone
from uuid import uuid4
import psycopg
from psycopg.rows import dict_row
from pydantic import SecretStr
from .control import ROOT,EVIDENCE,batch,atomic_json,event
from .resources import start,stop,runtime
from .samples import SAMPLES,HASHES,ORACLE,T_NAME,CV_NAME,H1_NAME,H2_NAME
from app.storage.originals import OriginalStore
from app.materials.repository import PostgresMaterials
from app.activities import PostgresAdmissionLedger,ActivitySpec,SourceSnapshot
from app.capabilities.contracts import ModelServiceConfig
from app.service_config import ActivityConfig,LayerState
from app.worker.session import SessionConfig
from app.interview.contracts import InterviewCommandInput,InterviewRefusal
from app.interview.service import InterviewService


class Harness:
    def __init__(self,admin,dsn,out):
        self.admin,self.dsn,self.out=admin,dsn,out
        self.ledger=PostgresAdmissionLedger(dsn,statement_timeout_ms=10000,lock_timeout_ms=5000)
        self.materials=PostgresMaterials(dsn)
        self.data=EVIDENCE/'synthetic'/'main'/'data';self.data.mkdir(parents=True,exist_ok=True)
        original=self.data/'originals';original.mkdir(exist_ok=True);self.originals=OriginalStore(original)
        self.session=SessionConfig(window_seconds=20,request_timeout_seconds=2.0,stop_grace_seconds=2.0)
        model=ModelServiceConfig(provider='deepseek_chat_completions',base_url='https://api.deepseek.com',model='task106-synthetic',
            api_key=SecretStr(secrets.token_urlsafe(24)),timeout_seconds=1.0,max_request_bytes=65536,max_response_bytes=65536,max_output_tokens_limit=1024)
        self.config=ActivityConfig(provider='deepseek_chat_completions',model='task106-synthetic',quota_preview=None,model_service=model,
            create_layer=LayerState(True),continue_layer=LayerState(True),interview_model_layer=LayerState(True),interview_output_tokens=512,interview_followups=2)
        self.service=InterviewService(self.ledger,self.materials,self.originals,session_config=self.session)
        self.saved={};self.observations=[]

    def material(self,name):
        raw=SAMPLES[name].encode('utf-8');original=self.originals.put(io.BytesIO(raw),max_bytes=5242880)
        assert original.sha256==HASHES[name]
        row=self.materials.save(source_id=None,expected_version=None,filename=name,format='md',sha256=original.sha256,size=original.size)
        self.saved[name]=row;return row

    async def activity(self,names,requests=20):
        aid=str(uuid4());sources=tuple(SourceSnapshot(self.saved[n]['id'],self.saved[n]['version_id'],self.saved[n]['revision']) for n in names)
        await self.ledger.create_activity(ActivitySpec(activity_id=aid,sources=sources,deadline_at=datetime.now(timezone.utc)+timedelta(hours=3),
            max_requests=requests,max_cost_microunits=100000,reserve_cost_microunits=100,max_request_bytes=65536,max_output_tokens=1024,
            max_running_seconds=3600,allowed_models=(('deepseek_chat_completions','task106-synthetic'),),max_tool_calls=0))
        return aid

    async def command(self,aid,action,body,*,key=None,override=None):
        view=await self.ledger.read_interview_workspace(aid);h=view['head'] or {}
        data=dict(schema='interview.command.v1',business_key=key or str(uuid4()),action=action,expected_head_revision=h.get('revision',0),
            expected_goal_version=h.get('goal_version',0),expected_scope_revision=view['sources'][0]['source_revision'] if not view['head'] else h['scope_revision'],body=body)
        # Public scope revision is activity scope, not a source revision.
        if not view['head']:
            data['expected_scope_revision']=(await self.ledger.inspect_scope(aid)).scope_revision
        if override:data.update(override)
        command=InterviewCommandInput.model_validate(data)
        receipt=await self.service.submit_command(aid,command,self.config,run_tag='task106-'+secrets.token_hex(12))
        self.observations.append(dict(aid=aid,command=command.model_dump(),receipt=receipt))
        atomic_json(self.out/'effects.json',self.observations)
        if receipt['status'] in ('failed','unknown','started','accepted'):event('unexpected-command-status',receipt)
        return receipt,command

    def snapshot(self,aid):
        with psycopg.connect(self.dsn,row_factory=dict_row) as conn:
            return dict(activity=dict(conn.execute('SELECT id::text,status,execution_generation,requests_reserved,cost_reserved_microunits,running_reserved_seconds,running_settled_seconds,scope_revision,dispatch_closed FROM activities WHERE id=%s',(aid,)).fetchone()),
                records=[dict(r) for r in conn.execute('SELECT record_id::text,seq,kind,origin,goal_version,scope_revision,answer_version,body_sha256,operation_id FROM interview_records WHERE activity_id=%s ORDER BY seq',(aid,)).fetchall()],
                operations=[dict(r) for r in conn.execute('SELECT operation_id,state,disposition,scope_revision,error_code FROM activity_operations WHERE activity_id=%s ORDER BY operation_id',(aid,)).fetchall()],
                results=[dict(r) for r in conn.execute('SELECT operation_id,payload_sha256 FROM activity_operation_results WHERE activity_id=%s ORDER BY operation_id',(aid,)).fetchall()])


async def verify(h):
    s1=await h.ledger._transaction(h.ledger._interview_schema_info);m6=await h.ledger._transaction(h.ledger._memory_schema_info)
    assert s1=='ready' and m6=='ready',(s1,m6)
    atomic_json(h.out/'schema-ready.json',dict(S1=s1,G9=m6,connection_role='ordinary app'))
    for name in SAMPLES:h.material(name)
    atomic_json(h.out/'samples.json',dict(materials=h.saved,hashes=HASHES,oracle=ORACLE,texts=SAMPLES))
    aid=await h.activity([T_NAME]);start,_=await h.command(aid,'start',{'goal':{'target':'余额算法覆盖与串行结果','material_roles':[{'source_id':h.saved[T_NAME]['id'],'role':'reference'}]}})
    assert start['status']=='committed' and start['effect_applied'],start
    q,_=await h.command(aid,'ask',{'mode':'first'});assert q['status']=='committed',q
    view=await h.ledger.read_interview_workspace(aid);question=view['head']['current_question_id']
    a,_=await h.command(aid,'answer',{'question_record_id':question,'text':'串行100加20减10得到110；都先读100时写120再写90会覆盖一次更新。'})
    assert a['status']=='committed'
    v=await h.ledger.read_interview_workspace(aid)
    f,_=await h.command(aid,'review',{'question_record_id':v['head']['current_question_id'],'answer_record_id':v['head']['current_answer_id']})
    assert f['status']=='committed',f
    detail=await h.ledger.read_interview_record(aid,f['record_ids'][0])
    assert detail['body']['value']['type']=='feedback' and detail['body']['value']['recognitions'][0]['verification_kind']=='source_interpretation'
    assert detail['body']['catalog'] and detail['body']['value']['recognitions'][0]['answer_excerpt'].startswith('串行100')
    citation=await h.service.read_citation(aid,f['record_ids'][0],detail['body']['catalog'][0]['citation_id'],detail['view_token'])
    c=citation['citation']
    assert citation['position_verified'] and c['text']==SAMPLES[T_NAME][c['start_offset']:c['end_offset']], ('citation source slice mismatch',c)
    history=await h.ledger.read_interview_history(aid)
    assert all(not any(k in r for k in ('payload','local_body','catalog','text')) for r in history['records'])
    ended,_=await h.command(aid,'finish',{});assert ended['status']=='committed'
    state=h.snapshot(aid);assert state['activity']['requests_reserved']==2 and len(state['results'])==2 and state['activity']['running_reserved_seconds']==0
    atomic_json(h.out/'technical-final.json',state)
    atomic_json(h.out/'technical-feedback.json',detail);atomic_json(h.out/'technical-citation.json',citation)
    print(json.dumps(dict(normal_technical=True,activity_id=aid,model_calls=2,history_metadata=True)))


def main():
    if sys.platform=='win32':asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    with batch('P02-ordinary-core-first-native') as out:
        try:
            admin=start(1);app,denied=runtime(admin);h=Harness(admin,app,out)
            asyncio.run(verify(h))
        finally:stop(1)


if __name__=='__main__':main()
