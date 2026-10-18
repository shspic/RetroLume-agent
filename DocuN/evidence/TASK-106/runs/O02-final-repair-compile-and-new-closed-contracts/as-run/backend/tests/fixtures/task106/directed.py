"""Bounded second normal direction, self-report/probe, local concurrency and repair."""
from __future__ import annotations
import asyncio,json,secrets,sys
from uuid import uuid4
from .control import batch,atomic_json
from .resources import start,stop,runtime
from .core import Harness
from .samples import H1_NAME,H2_NAME,CV_NAME,T_NAME,SPRING_NAME
from app.interview.contracts import InterviewCommandInput,InterviewRefusal


async def start_goal(h,names,target,roles):
    aid=await h.activity(names)
    receipt,_=await h.command(aid,'start',{'goal':{'target':target,'material_roles':[dict(source_id=h.saved[n]['id'],role=r) for n,r in roles.items()]}})
    assert receipt['effect_applied'],receipt
    return aid


async def detail_for(h,aid,receipt):
    assert receipt['status']=='committed',receipt
    return await h.ledger.read_interview_record(aid,receipt['record_ids'][0])


async def verify(h):
    for name in (H1_NAME,H2_NAME,CV_NAME,T_NAME,SPRING_NAME):h.material(name)
    # H: actual conflict references, explicit next, finish without fabricated feedback.
    aid=await start_goal(h,[H1_NAME,H2_NAME],'策展：并列史料活动X年份及未知依据',{H1_NAME:'reference',H2_NAME:'reference'})
    q,_=await h.command(aid,'ask',{'mode':'first'});view=await h.ledger.read_interview_workspace(aid)
    await h.command(aid,'answer',{'question_record_id':view['head']['current_question_id'],'text':'史料A记2012，史料B记2013，两者冲突；缺原始档案和同期记录，年份保持未知。'})
    view=await h.ledger.read_interview_workspace(aid);f,_=await h.command(aid,'review',{'question_record_id':view['head']['current_question_id'],'answer_record_id':view['head']['current_answer_id']})
    feedback=await detail_for(h,aid,f);conflict=feedback['body']['value']['conflicts'][0]
    assert len(set(conflict['reference_ids']))==2 and '2012' in conflict['text'] and '2013' in conflict['text'],conflict
    chosen=[c for c in feedback['body']['catalog'] if c['citation_id'] in conflict['reference_ids']]
    assert len({c['source_id'] for c in chosen})==2,chosen
    await h.command(aid,'ask',{'mode':'next','parent_feedback_id':f['record_ids'][0]});await h.command(aid,'finish',{})
    atomic_json(h.out/'H-conflict.json',dict(feedback=feedback,state=h.snapshot(aid)))
    # CV: same low-trust provider text becomes application-owned self-report wording.
    cv=await start_goal(h,[CV_NAME],'减少重复查询，性能快60%的测量依据',{CV_NAME:'resume'})
    await h.command(cv,'ask',{'mode':'first'});v=await h.ledger.read_interview_workspace(cv)
    await h.command(cv,'answer',{'question_record_id':v['head']['current_question_id'],'text':'我减少重复查询后性能快60%。'})
    v=await h.ledger.read_interview_workspace(cv);p,_=await h.command(cv,'review',{'question_record_id':v['head']['current_question_id'],'answer_record_id':v['head']['current_answer_id']})
    probe=await detail_for(h,cv,p);value=probe['body']['value']
    assert value['type']=='probe' and value['recognitions'][0]['verification_kind']=='user_statement' and '尚未独立核实' in value['recognitions'][0]['explanation'],value
    assert all(s in value['text'] for s in ('基线','口径','样本','环境','记录')),value
    v=await h.ledger.read_interview_workspace(cv)
    await h.command(cv,'answer',{'question_record_id':v['head']['current_question_id'],'text':'目前没有记录，不能把自报60%当验证结果；需要补基线100、样本30、环境及口径。这些数值也只是补充自报。'})
    v=await h.ledger.read_interview_workspace(cv);f,_=await h.command(cv,'review',{'question_record_id':v['head']['current_question_id'],'answer_record_id':v['head']['current_answer_id']})
    final=await detail_for(h,cv,f);assert final['body']['value']['type']=='feedback'
    assert final['body']['value']['recognitions'][0]['verification_kind']=='user_statement'
    await h.command(cv,'finish',{});atomic_json(h.out/'CV-self-report.json',dict(probe=probe,feedback=final,state=h.snapshot(cv)))
    # Missing goal and no matching material: zero SUP, local clarification / feedback.
    local=await h.activity([T_NAME]);await h.command(local,'start',{'goal':None})
    try:await h.command(local,'ask',{'mode':'first'})
    except InterviewRefusal as exc:assert exc.code=='interview_phase_conflict',exc.code
    else:raise AssertionError('missing goal invoked an ask')
    await h.command(local,'goal',{'goal':{'target':'xxxxxxxxunknownunmatchedzzzz'}})
    q,cmd=await h.command(local,'ask',{'mode':'first'});assert q['execution_kind']=='local'
    v=await h.ledger.read_interview_workspace(local);qid=v['head']['current_question_id']
    base=dict(schema='interview.command.v1',action='answer',expected_head_revision=v['head']['revision'],expected_goal_version=v['head']['goal_version'],expected_scope_revision=v['head']['scope_revision'],body={'question_record_id':qid,'text':'补充具体范围仍缺资料。'})
    c1=InterviewCommandInput.model_validate(dict(base,business_key=str(uuid4())));c2=InterviewCommandInput.model_validate(dict(base,business_key=str(uuid4())))
    receipts=await asyncio.gather(*(h.service.submit_command(local,c,h.config,run_tag='task106-race-'+secrets.token_hex(4)) for c in (c1,c2)))
    assert sum(r['effect_applied'] for r in receipts)==1 and any(r['duplicate_of'] for r in receipts),receipts
    conflicting=InterviewCommandInput.model_validate({**c1.model_dump(),'body':{'question_record_id':qid,'text':'不同正文'},'business_key':str(uuid4())})
    try:await h.service.submit_command(local,conflicting,h.config,run_tag='task106-conflict')
    except InterviewRefusal as exc:assert exc.code=='interview_slot_conflict',exc.code
    else:raise AssertionError('different body same slot accepted')
    v=await h.ledger.read_interview_workspace(local)
    f,_=await h.command(local,'review',{'question_record_id':v['head']['current_question_id'],'answer_record_id':v['head']['current_answer_id']})
    assert f['execution_kind']=='local' and h.snapshot(local)['activity']['requests_reserved']==0,f
    await h.command(local,'finish',{});atomic_json(h.out/'local-concurrency.json',dict(receipts=receipts,state=h.snapshot(local)))
    # Actual same-name clarification and Unicode text; no assumed direction.
    spring=await start_goal(h,[SPRING_NAME],'Spring',{SPRING_NAME:'reference'})
    q,_=await h.command(spring,'ask',{'mode':'first'});d=await detail_for(h,spring,q)
    assert d['body']['value']['purpose']=='clarification' and '软件框架' in d['body']['value']['text'] and '季节' in d['body']['value']['text'],d
    await h.command(spring,'goal',{'goal':{'target':'Spring季节相关概念','focus':'不是软件框架'}})
    after=await h.ledger.read_interview_record(spring,q['record_ids'][0]);assert after['body'] is None,after
    atomic_json(h.out/'ambiguity-goal-change.json',dict(before=d,after=after,state=h.snapshot(spring)))
    # Current same-goal answer correction invalidates old derived feedback, keeps v1.
    correct=await start_goal(h,[T_NAME],'余额算法串行覆盖',{T_NAME:'reference'})
    await h.command(correct,'ask',{'mode':'first'});v=await h.ledger.read_interview_workspace(correct)
    a,_=await h.command(correct,'answer',{'question_record_id':v['head']['current_question_id'],'text':'🧭串行得到110；两个均先读100存在覆盖风险。'})
    v=await h.ledger.read_interview_workspace(correct);f,_=await h.command(correct,'review',{'question_record_id':v['head']['current_question_id'],'answer_record_id':v['head']['current_answer_id']})
    await h.command(correct,'correct_answer',{'answer_record_id':a['record_ids'][0],'expected_answer_version':1,'text':'🧭串行100+20-10=110，最后写90可能覆盖前次120写回；不推断现实隔离级别。'})
    old=await h.ledger.read_interview_record(correct,f['record_ids'][0]);answer=await h.ledger.read_interview_record(correct,a['record_ids'][0])
    assert old['body'] is None and answer['body']['value']['answer_version']==1,(old,answer)
    atomic_json(h.out/'answer-correction.json',dict(old_feedback=old,old_answer=answer,state=h.snapshot(correct)))
    print(json.dumps(dict(H=True,CV=True,probe=True,zero_model_clarification=True,same_slot_concurrency=True,ambiguity=True,correction=True)))


def main():
    if sys.platform=='win32':asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    with batch('P04-directions-probe-local-concurrency-correction') as out:
        try:
            admin=start(1);app,denied=runtime(admin);h=Harness(admin,app,out)
            asyncio.run(verify(h))
        finally:stop(1)


if __name__=='__main__':main()
