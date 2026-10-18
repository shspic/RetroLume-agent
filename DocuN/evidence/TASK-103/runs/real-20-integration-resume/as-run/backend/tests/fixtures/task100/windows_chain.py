"""原 Windows SUP/worker/Job 的真实 H1 与有限异常，provider 仅合成返回。"""
from __future__ import annotations
import asyncio
import json
import os
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4
from app.runtime import psycopg_compatible_loop_factory
from .control import Ledger,ROOT,BACKEND,Deadline,atomic_json,run_process,utc
from .chain_client import Client,wait_provider
from .support import Fixture,DSN
from .seed_helpers import ready_answer
from .synthetic_content import MATERIAL,GOAL

def run_async(coro):
    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as loop:return loop.run(coro)

class Context:
    def __init__(self):
        self.batch=Path(os.environ['RETROLUME_TASK100_BATCH_DIR']);self.client=Client()
        self.fixture=Fixture(DSN,Path(os.environ['RETROLUME_TASK100_ORIGINALS_DIR']))
        self.facts=[];self.observations=Path(os.environ['RETROLUME_TASK100_OBSERVATIONS'])
    def rows(self,aid):
        return self.fixture.rows('SELECT status,execution_generation,requests_reserved,cost_reserved_microunits,tools_reserved,running_reserved_seconds,running_settled_seconds FROM activities WHERE id=%s',(aid,))[0]
    def seed(self):
        value=run_async(ready_answer(self.fixture))
        self.facts.append({'kind':'synthetic_database_precondition','activity_id':value[0],'sup_created':False,'provider_sent':False})
        return value
    def evaluate_body(self,eid,answer):
        return {'confirmed':True,'exercise_record_id':eid,'answer_record_id':answer,'correction_record_id':None,'retry_of':None}
    def mode(self,name,action='evaluate',marker=None):
        marker=marker or uuid4().hex
        release=self.batch/('release-'+marker)
        # 本卡进程继承的释放路径是固定文件名；以新文件名无须删除旧证据。
        atomic_json(Path(os.environ['RETROLUME_TASK100_MODE']),{'mode':name,'action':action,'marker':marker,'release':str(release)})
        return marker,release
    def check_settled(self,aid,before,expected_q=1):
        after=self.rows(aid)
        assert after['requests_reserved']==before['requests_reserved']+expected_q,(before,after)
        assert after['cost_reserved_microunits']==before['cost_reserved_microunits']+100000*expected_q
        assert after['running_reserved_seconds']==0,after
        assert after['running_settled_seconds']>=before['running_settled_seconds']
        return after
    def snapshot(self,name,aid,before,after,**values):
        fact={'name':name,'activity_id':aid,'before':before,'after':after,**values};self.facts.append(fact)
        print('WINDOW',json.dumps(fact,ensure_ascii=False,default=str),flush=True)

def normal_h1(ctx):
    source=ctx.fixture.text(MATERIAL,'task100-h1-'+uuid4().hex[:8]+'.md')
    aid=str(uuid4());ctx.client.request('/api/activities',{'activity_id':aid,'source_ids':[source['id']]})
    before=ctx.rows(aid)
    atomic_json(ctx.batch/'browser-input.json',{'activity_id':aid,'title':source['title'],'goal':GOAL,'batch_dir':str(ctx.batch)})
    Ledger().consume('driver',{'entry':'frontend/tests/task100-browser.cjs','mode':'main'})
    deadline=Deadline(ctx.client.timeout(600))
    result=run_process(['node',str(ROOT/'frontend/tests/task100-browser.cjs'),'--main'],deadline,600,ctx.batch/'browser-main-raw',cwd=ROOT/'frontend',env=dict(os.environ))
    assert result['status']=='pass',result
    view=ctx.client.workspace(aid);after=ctx.rows(aid)
    assert after['requests_reserved']==8 and after['cost_reserved_microunits']==800000 and after['tools_reserved']==1,after
    assert after['running_reserved_seconds']==0
    assert view['head']['node_id']=='n2' and view['head']['phase']=='ready',view['head']
    assert view['nodes']['n1']['status']=='evidence_sufficient' and len(view['nodes']['n1']['independent_answers'])==2
    records=ctx.fixture.rows('SELECT kind,business_key,ordinal,applied_revision,state_after FROM teaching_records WHERE activity_id=%s ORDER BY seq',(aid,))
    assert sum(r['kind']=='feedback' for r in records)==4 and sum(r['kind']=='progress' for r in records)==4
    effect=[r['applied_revision'] for r in records if r['applied_revision'] is not None]
    assert len(set(effect))==len(effect)
    assert all((r['applied_revision'] is None)==(r['state_after'] is None) for r in records)
    ctx.snapshot('H1_actual_browser_8_model_1_tool',aid,before,after,head=view['head'],nodes=view['nodes'],record_count=len(records),immutable_effects_unique=True)
    return aid

def late(ctx,kind):
    aid,source,eid,answer=ctx.seed();before=ctx.rows(aid);marker,release=ctx.mode('delay')
    old_view=ctx.client.workspace(aid)
    with ThreadPoolExecutor(max_workers=1) as executor:
        future=executor.submit(ctx.client.submit,aid,'evaluate',ctx.evaluate_body(eid,answer),None,old_view)
        try:
            wait_provider(ctx.observations,marker,time.monotonic()+ctx.client.timeout(12))
            if kind=='goal':
                ctx.client.submit(aid,'goal',{'goal':'新目标：解释原子性','self_report':None,'domain':None,'seed_operation_id':None,'seed_payload_sha256':None})
            elif kind=='answer':
                ctx.client.submit(aid,'answer',{'exercise_record_id':eid,'kind':'revision','text':'1m/s，2分钟=120秒，数量级合理','supersedes_answer_record_id':answer})
            elif kind=='source':
                import io
                raw=ctx.fixture.originals.put(io.BytesIO((MATERIAL+'新版本。').encode()),max_bytes=5242880)
                ctx.fixture.materials.save(source_id=source['id'],expected_version=source['version_id'],filename='updated-task100.md',format='md',sha256=raw.sha256,size=raw.size)
            else:ctx.client.request(f'/api/activities/{aid}/cancel',{})
        finally: release.write_text('released',encoding='utf-8')
        receipt,cmd=future.result(timeout=ctx.client.timeout(120))
    view=ctx.client.workspace(aid);after=ctx.rows(aid)
    assert after['requests_reserved']==before['requests_reserved']+1 and after['cost_reserved_microunits']==before['cost_reserved_microunits']+100000
    assert after['running_reserved_seconds']==0
    rows=ctx.fixture.rows('SELECT kind,applied_revision FROM teaching_records WHERE activity_id=%s AND business_key=%s ORDER BY ordinal',(aid,cmd['business_key']))
    if kind in ('goal','answer'):
        assert receipt['status']=='history',(receipt,rows)
        assert [r['kind'] for r in rows]==['feedback','exposure'] and all(r['applied_revision'] is None for r in rows),rows
        detail=ctx.client.request(f"/api/activities/{aid}/teaching/records/{receipt['record_ids'][0]['record_id']}")
        assert detail['public_body'] is not None
    else:
        assert rows==[],rows
        if kind=='source': assert view['overlay']['source_invalid'] and view['answer']['text']=='120÷2=60m/s' and view['exercise']['qualification']=='source_invalid'
        else: assert view['overlay']['cancelled']
    ctx.snapshot('late_'+kind,aid,before,after,receipt=receipt,head=view['head'],facts=rows)
    ctx.mode('normal')

def late_goal(ctx):late(ctx,'goal')
def late_answer(ctx):late(ctx,'answer')
def late_source(ctx):late(ctx,'source')
def late_cancel(ctx):late(ctx,'cancel')

def unknown_and_abandon(ctx):
    aid,source,eid,answer=ctx.seed();before=ctx.rows(aid);ctx.mode('unknown')
    receipt,cmd=ctx.client.submit(aid,'evaluate',ctx.evaluate_body(eid,answer))
    assert receipt['status']=='unknown',receipt
    after=ctx.check_settled(aid,before)
    q=after['requests_reserved'];sup=Ledger().load()['counts']['sup_creates']
    ctx.client.request(f"/api/activities/{aid}/teaching/commands/{cmd['business_key']}")
    duplicate=ctx.client.request(f'/api/activities/{aid}/teaching/commands',cmd)
    assert duplicate['status']=='unknown'
    ctx.client.submit(aid,'abandon',{'target_business_key':cmd['business_key']})
    retry_body=ctx.evaluate_body(eid,answer);retry_body['retry_of']=cmd['business_key']
    ctx.client.submit(aid,'evaluate',retry_body,expected=409)
    assert Ledger().load()['counts']['sup_creates']==sup and ctx.rows(aid)['requests_reserved']==q
    ctx.snapshot('unknown_read_only_abandon_keeps_slot',aid,before,ctx.rows(aid),receipt=receipt)
    ctx.mode('normal')

def invalid_and_explicit_retry(ctx):
    aid,source,eid,answer=ctx.seed();before=ctx.rows(aid);ctx.mode('invalid')
    receipt,cmd=ctx.client.submit(aid,'evaluate',ctx.evaluate_body(eid,answer))
    assert receipt['status']=='failed',receipt
    assert ctx.client.workspace(aid)['head']['pending_business_key'] is None
    assert ctx.fixture.rows('SELECT record_id FROM teaching_records WHERE activity_id=%s AND business_key=%s',(aid,cmd['business_key']))==[]
    ctx.mode('normal');body=ctx.evaluate_body(eid,answer);body['retry_of']=cmd['business_key']
    retried,newcmd=ctx.client.submit(aid,'evaluate',body)
    assert retried['status']=='committed',retried
    after=ctx.check_settled(aid,before,2)
    ctx.snapshot('invalid_output_then_explicit_new_key_retry',aid,before,after,failed=receipt,retried=retried)

def hard_stop(ctx):
    aid,source,eid,answer=ctx.seed();before=ctx.rows(aid);marker,_=ctx.mode('hard_stop')
    receipt,cmd=ctx.client.submit(aid,'evaluate',ctx.evaluate_body(eid,answer))
    view=ctx.client.workspace(aid);after=ctx.rows(aid)
    assert receipt['status']=='unknown',receipt
    assert view['answer']['text']=='120÷2=60m/s'
    assert after['requests_reserved']==before['requests_reserved']+1
    outcomes=[json.loads(p.read_text(encoding='utf-8'))['value'] for p in ctx.observations.glob('*session_outcome.json')]
    matching=[o for o in outcomes if o['activity_id']==aid]
    assert matching and matching[-1]['active_processes_at_end']==0 and not matching[-1]['cleanup_incomplete'],matching
    assert matching[-1]['elapsed_seconds']>=80 and matching[-1]['model_receipt'] is None,matching[-1]
    assert any(json.loads(p.read_text(encoding='utf-8'))['value']['job_name']==matching[-1]['job_name']
        for p in ctx.observations.glob('*job_terminate.json'))
    ctx.snapshot('real_hard_stop_preserves_answer',aid,before,after,receipt=receipt,outcome=matching[-1])
    ctx.mode('normal')

def main():
    ctx=Context();results=[]
    cases=[normal_h1,late_goal,late_answer,late_source,late_cancel,unknown_and_abandon,invalid_and_explicit_retry,hard_stop]
    failed=False
    try:
        for fn in cases:
            if failed: results.append({'name':fn.__name__,'status':'not_run','reason':'previous_failure'});continue
            start=time.monotonic()
            try: fn(ctx);status='pass'
            except BaseException:
                traceback.print_exc();status='fail';failed=True
            results.append({'name':fn.__name__,'status':status,'elapsed':time.monotonic()-start})
        outcomes=[json.loads(p.read_text(encoding='utf-8'))['value'] for p in ctx.observations.glob('*session_outcome.json')]
        if not failed:
            assert len(outcomes)==17,len(outcomes)
            assert all(o['manager_pid'] and o['manager_created_100ns'] and o['worker_created_100ns'] and o['job_name'] for o in outcomes)
            assert all(o['active_processes_at_end']==0 and not o['cleanup_incomplete'] for o in outcomes),outcomes
        atomic_json(ctx.batch/'windows-facts.json',{'cases':results,'facts':ctx.facts,'session_outcomes':outcomes,'provider_real':False,'user_program_executed':False})
        return 1 if failed else 0
    finally:
        ctx.client.save(ctx.batch/'windows-http-timeline.json');ctx.fixture.preserve()
if __name__=='__main__':raise SystemExit(main())
