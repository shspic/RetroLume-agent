"""Affected Windows chain, real SUP/worker/Job/PG; finite synthetic transport only.

Twelve maximum SUP attempts planned: explicit recovery model/tool, small-value
conflict, actual three-node plan + calculation initial/retest, concept and program.
"""
from __future__ import annotations
import json
import os
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
from .control import Ledger,atomic_json
from .windows_chain import Context,run_async
from .seed_helpers import command,ready_answer
from .repair_cases import unclaimed_model,unclaimed_tool,ready_node,seed_g7
from .synthetic_content import MATERIAL,GOAL
from .repair_oracle import evaluate_record,premises


def numeric_progress(ctx,aid,status):
    view=ctx.client.workspace(aid);node=view['nodes']['n1']
    assert node['status']==status,node
    if status!='evidence_sufficient':assert not node['independent_answers'],node
    row=ctx.fixture.rows("SELECT body FROM teaching_records WHERE activity_id=%s AND kind='progress' ORDER BY seq DESC LIMIT 1",(aid,))[0]
    return {'workspace':view,'progress':json.loads(row['body'])}


def recover_model_and_tool(ctx):
    source=ctx.fixture.text(MATERIAL,'repair03-ui-'+uuid4().hex[:8]+'.md')
    aid,_,eid,answer=run_async(ready_answer(ctx.fixture,source));before=ctx.rows(aid)
    cmd,frozen=run_async(unclaimed_model(ctx.fixture,aid));path=f'/api/activities/{aid}/teaching/commands'
    row=run_async(ctx.fixture.ledger.read_teaching_command(aid,cmd.business_key))['command']
    frozen_body=row['context_body'];sup_before=Ledger().load()['counts']['sup_creates']
    receipt=ctx.client.request(path+'/'+cmd.business_key)
    assert receipt['retry_policy']=='same_key_before_claim' and Ledger().load()['counts']['sup_creates']==sup_before
    ctx.mode('false_met',marker='repair-recover-false-met')
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(ctx.client.request,path,cmd.model_dump()) for _ in range(2)]
        receipts=[future.result(timeout=ctx.client.timeout(110)) for future in futures]
    assert sum(r['status']=='committed' for r in receipts)>=1,receipts
    assert Ledger().load()['counts']['sup_creates']==sup_before+1
    current=run_async(ctx.fixture.ledger.read_teaching_command(aid,cmd.business_key))['command']
    assert current['context_body']==frozen_body and current['context_sha256']==frozen.context_sha256
    after=ctx.check_settled(aid,before);numeric=numeric_progress(ctx,aid,'needs_repair')
    assert numeric['progress']['support_checks'][0]['answer_status']=='conflict'
    ctx.snapshot('accepted_commit_unclaimed_concurrent_model_recovery',aid,before,after,
        receipts=receipts,command=cmd.model_dump(),frozen_context_sha256=frozen.context_sha256,
        original_context_preserved=True,actual_sup_delta=1,model_observations_injected='all met',progress=numeric['progress'])
    readonly_before=ctx.rows(aid)
    ctx.client.request(path+'/'+cmd.business_key);ctx.client.request(path,cmd.model_dump())
    assert ctx.rows(aid)==readonly_before and Ledger().load()['counts']['sup_creates']==sup_before+1
    tool,context_sha=run_async(unclaimed_tool(ctx.fixture,aid));before=ctx.rows(aid)
    ctx.mode('normal');sup_before=Ledger().load()['counts']['sup_creates']
    accepted=ctx.client.request(path+'/'+tool.business_key);assert accepted['retry_policy']=='same_key_before_claim'
    result=ctx.client.request(path,tool.model_dump());assert result['status']=='committed',result
    after=ctx.check_settled(aid,before,0)
    assert after['tools_reserved']==before['tools_reserved']+1 and Ledger().load()['counts']['sup_creates']==sup_before+1
    row=run_async(ctx.fixture.ledger.read_teaching_command(aid,tool.business_key))['command']
    assert row['context_sha256']==context_sha
    ctx.snapshot('accepted_commit_unclaimed_tool_recovery',aid,before,after,receipt=result,
        original_context_sha256=context_sha,actual_sup_delta=1,actual_model_delta=0,actual_tool_delta=1)
    # Actual tool-kind 007 row is never a G7 seed authority.
    op=ctx.fixture.rows('SELECT payload_sha256 FROM activity_operation_results WHERE activity_id=%s AND operation_id=%s',
        (aid,tool.operation_id(aid)))[0]
    before_head=ctx.fixture.head(aid);before_commands=ctx.fixture.commands(aid)
    bad=command(before_head,'goal',{'goal':GOAL,'seed_operation_id':tool.operation_id(aid),'seed_payload_sha256':op['payload_sha256']})
    ctx.client.request(path,bad.model_dump(),expected=409)
    ctx.client.request(f'/api/activities/{aid}/teaching/seeds/{tool.operation_id(aid)}',expected=409)
    assert before_head==ctx.fixture.head(aid) and before_commands==ctx.fixture.commands(aid)
    ctx.ui={'activity_id':aid,'title':source['title'],'goal':GOAL}


def numeric_small_conflict(ctx):
    aid,source,eid,answer=run_async(ready_node(ctx.fixture,'n1','0.01m/s'))
    before=ctx.rows(aid);ctx.mode('false_met',marker='repair-small-false-met')
    receipt,cmd=ctx.client.submit(aid,'evaluate',ctx.evaluate_body(eid,answer));assert receipt['status']=='committed',receipt
    after=ctx.check_settled(aid,before);value=numeric_progress(ctx,aid,'needs_repair')
    assert value['progress']['support_checks'][0]['answer_status']=='conflict'
    ctx.snapshot('small_finite_answer_false_model_met_cannot_advance',aid,before,after,
        receipt=receipt,progress=value['progress'],model_observations_injected='all met')
    ctx.mode('normal')


def actual_exercise(ctx,aid,node,purpose='initial'):
    view=ctx.client.workspace(aid)
    body={'confirmed':True,'path_record_id':view['head']['path_record_id'],'node_id':node,'purpose':purpose,
          'parent_feedback_record_id':view['head']['feedback_record_id'] if purpose=='retest' else None,'retry_of':None}
    receipt,_=ctx.client.submit(aid,'exercise',body);assert receipt['status']=='committed',receipt
    return ctx.client.workspace(aid)['head']['exercise_record_id']


def actual_answer(ctx,aid,eid,text):
    receipt,_=ctx.client.submit(aid,'answer',{'exercise_record_id':eid,'kind':'initial','text':text,'supersedes_answer_record_id':None})
    assert receipt['status']=='committed',receipt
    return receipt['record_ids'][0]['record_id']


def grounded_three_scenarios(ctx):
    ctx.oracle=[];ctx.mode('normal',marker='repair-grounded')
    source=ctx.fixture.text(MATERIAL,'repair-three-grounded-'+uuid4().hex[:8]+'.md');aid=str(uuid4())
    ctx.client.request('/api/activities',{'activity_id':aid,'source_ids':[source['id']]})
    before=ctx.rows(aid)
    receipt,_=ctx.client.submit(aid,'goal',{'goal':GOAL,'self_report':None,'domain':None,'seed_operation_id':None,'seed_payload_sha256':None})
    proposal,_=ctx.client.submit(aid,'plan',{'confirmed':True,'correction_record_id':None,'retry_of':None})
    assert proposal['status']=='committed',proposal
    pr=ctx.client.workspace(aid)['proposal']['record_id'];ctx.oracle.append(evaluate_record(ctx.fixture,ctx.client,aid,pr,'path'))
    ctx.client.submit(aid,'accept_path',{'proposal_record_id':pr})
    eid=actual_exercise(ctx,aid,'n1');answer=actual_answer(ctx,aid,eid,'1m/s；2分钟=120秒，先统一时间单位，数量级合理。')
    receipt,_=ctx.client.submit(aid,'evaluate',ctx.evaluate_body(eid,answer));assert receipt['status']=='committed'
    view=ctx.client.workspace(aid)
    assert len(view['nodes']['n1']['independent_answers'])==1
    ctx.oracle.extend([evaluate_record(ctx.fixture,ctx.client,aid,eid,'calculation'),
                       evaluate_record(ctx.fixture,ctx.client,aid,view['head']['feedback_record_id'],'calculation')])
    first_instance=ctx.fixture.rows('SELECT payload FROM activity_operation_results WHERE activity_id=%s AND operation_id='
        '(SELECT operation_id FROM teaching_records WHERE activity_id=%s AND record_id=%s)',(aid,aid,eid))[0]['payload']
    retest=actual_exercise(ctx,aid,'n1','retest');answer=actual_answer(ctx,aid,retest,'1m/s；3分钟=180秒，先统一秒，单位与数量级合理。')
    receipt,_=ctx.client.submit(aid,'evaluate',ctx.evaluate_body(retest,answer));assert receipt['status']=='committed'
    view=ctx.client.workspace(aid);assert view['head']['node_id']=='n2' and len(view['nodes']['n1']['independent_answers'])==2
    ctx.oracle.append(evaluate_record(ctx.fixture,ctx.client,aid,retest,'calculation'))
    new_instance=ctx.fixture.rows('SELECT payload FROM activity_operation_results WHERE activity_id=%s AND operation_id='
        '(SELECT operation_id FROM teaching_records WHERE activity_id=%s AND record_id=%s)',(aid,aid,retest))[0]['payload']
    assert json.loads(first_instance)['value']['result']['variant']['instance_data']!=json.loads(new_instance)['value']['result']['variant']['instance_data']
    after=ctx.check_settled(aid,before,5)
    ctx.snapshot('actual_plan_calculation_and_new_independent_instance',aid,before,after,head=view['head'],nodes=view['nodes'])
    ctx.grounded=[]
    for node,text,kind in [('n2','A100/B50，全部成功或全部不生效；原子性不能单独保证隔离，材料未给隔离级别。','concept'),
                           ('n3','返回2，0也满足value>0并被计数','program')]:
        aid,source,_,_=run_async(ready_node(ctx.fixture,node,text,seed_exercise=False))
        before=ctx.rows(aid);eid=actual_exercise(ctx,aid,node);answer=actual_answer(ctx,aid,eid,text)
        receipt,_=ctx.client.submit(aid,'evaluate',ctx.evaluate_body(eid,answer));assert receipt['status']=='committed',receipt
        view=ctx.client.workspace(aid);feedback=view['head']['feedback_record_id']
        ctx.oracle.extend([evaluate_record(ctx.fixture,ctx.client,aid,eid,kind),evaluate_record(ctx.fixture,ctx.client,aid,feedback,kind)])
        if kind=='program':assert view['feedback']['dimension_observations'][1]['observation']=='not_met'
        else:assert all(d['observation']=='met' for d in view['feedback']['dimension_observations'])
        after=ctx.check_settled(aid,before,2)
        ctx.snapshot('actual_'+kind+'_exercise_answer_feedback',aid,before,after,receipt=receipt,exercise=view['exercise'],feedback=view['feedback'])
        ctx.grounded.append({'activity_id':aid,'source_id':source['id'],'exercise_record_id':eid,'feedback_record_id':feedback,'kind':kind})
    atomic_json(ctx.batch/'content-oracle.json',{'status':'pass','independent_premises':premises(),'actual_records':ctx.oracle,
        'synthetic_transport_only':True,'user_program_executed':False})


def prepare_browser(ctx):
    aid=ctx.ui['activity_id'];head=ctx.fixture.head(aid);feedback=str(head['feedback_record_id'])
    for index in range(23):
        run_async(ctx.fixture.ledger.apply_teaching_local(aid,command(ctx.fixture.head(aid),'correct',{
            'target_record_id':feedback,'text':f'浏览器历史分页前提 {index}','disputed_dimensions':[]})))
    head=ctx.fixture.head(aid)
    records=ctx.fixture.rows('SELECT record_id,kind,seq FROM teaching_records WHERE activity_id=%s ORDER BY seq',(aid,))
    seed=run_async(seed_g7(ctx.fixture))
    value={'ui':ctx.ui,'seed':seed,'records':[dict(r,record_id=str(r['record_id'])) for r in records],
        'head':{k:str(head[k]) if head[k] is not None and k.endswith('_id') else head[k] for k in
                ('revision','exercise_record_id','answer_record_id','feedback_record_id','path_record_id')},
        'grounded':ctx.grounded,'batch_dir':str(ctx.batch),'fixture_grade':'native PG synthetic preconditions explicitly labelled'}
    for file in ctx.batch.glob('http-test_actual_citations*.json'):
        for item in json.loads(file.read_text(encoding='utf-8')):
            if item.get('status')==409 and '/citations/' in item.get('path',''):
                value['source_invalid_read']={'path':item['path'],'response':item['response']}
    assert value.get('source_invalid_read'),'actual HTTP invalid-source response missing'
    atomic_json(ctx.batch/'repair-browser-input.json',value)
    ctx.facts.append({'kind':'browser_preconditions','activity_id':aid,'history_count':len(records),'seed':seed,
        'actual_model_requests':False,'new_sup':0,'delete_used':False})


def main():
    ctx=Context();results=[];failed=False
    try:
        for fn in (recover_model_and_tool,numeric_small_conflict,grounded_three_scenarios,prepare_browser):
            if failed:results.append({'name':fn.__name__,'status':'not_run','reason':'previous_failure'});continue
            begun=time.monotonic()
            try:fn(ctx);status='pass'
            except BaseException:traceback.print_exc();status='fail';failed=True
            results.append({'name':fn.__name__,'status':status,'elapsed':time.monotonic()-begun})
        outcomes=[json.loads(p.read_text(encoding='utf-8'))['value'] for p in ctx.observations.glob('*session_outcome.json')]
        if not failed:
            assert len(outcomes)==12,len(outcomes)
            assert all(o['manager_pid'] and o['manager_created_100ns'] and o['worker_created_100ns'] and o['job_name'] for o in outcomes)
            assert all(o['active_processes_at_end']==0 and not o['cleanup_incomplete'] for o in outcomes)
        atomic_json(ctx.batch/'repair-windows-facts.json',{'cases':results,'facts':ctx.facts,'session_outcomes':outcomes,
            'provider_real':False,'user_program_executed':False,'old_17_windows_rerun':False})
        return 1 if failed else 0
    finally:ctx.client.save(ctx.batch/'repair-windows-http.json');ctx.fixture.preserve()


if __name__=='__main__':raise SystemExit(main())
