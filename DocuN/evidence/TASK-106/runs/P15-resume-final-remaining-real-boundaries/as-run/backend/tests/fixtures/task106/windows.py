"""Four exact native boundaries, atomic rollback and unknown/retry retention."""
from __future__ import annotations
import asyncio,json,os,secrets,sys,time
from uuid import uuid4
from .control import ROOT,batch,atomic_json
from .resources import start,stop,runtime
from .core import Harness
from .directed import start_goal
from .samples import T_NAME
from app.interview.contracts import InterviewRefusal


async def wait_marker(folder):
    until=time.perf_counter()+12
    while not (folder/'entered.json').exists():
        if time.perf_counter()>until:raise RuntimeError('exact native barrier did not enter; no substitute general cancel')
        await asyncio.sleep(.03)
    return json.loads((folder/'entered.json').read_text(encoding='utf-8'))


async def verify(h,stages=('accepted_before_admit','admitted_before_mark','marked_before_result','committed_before_repair')):
    h.material(T_NAME);proofs=[]
    for stage in stages:
        aid=await start_goal(h,[T_NAME],'余额算法串行覆盖',{T_NAME:'reference'})
        key=uuid4().hex;folder=ROOT/'backend/tests/fixtures/task106/barriers'/key
        os.environ['RETROLUME_TASK106_BARRIER']=stage;os.environ['RETROLUME_TASK106_BARRIER_KEY']=key
        task=asyncio.create_task(h.command(aid,'ask',{'mode':'first'}))
        try:
            entered=await wait_marker(folder);before=h.snapshot(aid)
            await h.command(aid,'goal',{'goal':{'target':'余额算法：明确修正后的目标','material_roles':[{'source_id':h.saved[T_NAME]['id'],'role':'reference'}]}})
            after_repair=h.snapshot(aid);atomic_json(folder/'release.json',dict(at_ns=time.perf_counter_ns()))
            receipt,command=await task;after=h.snapshot(aid)
            proof=dict(stage=stage,aid=aid,entered=entered,before=before,after_repair=after_repair,after=after,receipt=receipt)
            atomic_json(h.out/(stage+'.json'),proof);proofs.append(proof)
            if stage=='accepted_before_admit':
                assert not before['operations'] and not after['results'] and after['activity']['requests_reserved']==0,proof
            elif stage=='admitted_before_mark':
                assert before['operations'][0]['state']=='reserved' and not after['results'] and after['activity']['requests_reserved']==1,proof
            elif stage=='marked_before_result':
                assert before['operations'][0]['state']=='dispatched' and not before['results'] and not after['results'] and after['operations'][0]['state']=='unknown',proof
            else:
                assert len(before['results'])==len(after['results'])==1 and before['results']==after['results'],proof
                record=await h.ledger.read_interview_record(aid,receipt['record_ids'][0]);assert record['body'] is None,record
            assert after['activity']['scope_revision']==1 and after['activity']['running_reserved_seconds']==0,proof
        finally:
            atomic_json(folder/'release.json',dict(at_ns=time.perf_counter_ns(),finally_release=True))
            os.environ.pop('RETROLUME_TASK106_BARRIER',None);os.environ.pop('RETROLUME_TASK106_BARRIER_KEY',None)
            if not task.done():await task
    # Real failure after all domain writes, before original native transaction COMMIT.
    aid=await start_goal(h,[T_NAME],'余额算法回滚验证',{T_NAME:'reference'})
    before=h.snapshot(aid);os.environ['RETROLUME_TASK106_SCENARIO']='atomic_fail'
    try:receipt,command=await h.command(aid,'ask',{'mode':'first'})
    finally:os.environ.pop('RETROLUME_TASK106_SCENARIO',None)
    after=h.snapshot(aid);view=await h.ledger.read_interview_workspace(aid)
    atomic_json(h.out/'atomic-hook-rollback.json',dict(before=before,after=after,view=view,receipt=receipt))
    assert len(before['records'])==len(after['records']) and not after['results'] and view['head']['revision']==1,after
    assert after['activity']['requests_reserved']==1 and receipt['status']=='unknown',receipt
    # UNKNOWN must not start a fresh SUP with a changed key or retry_of.
    try:await h.command(aid,'ask',{'mode':'first','retry_of':command.business_key})
    except InterviewRefusal as exc:assert exc.code in ('interview_pending','window_unavailable','interview_retry_forbidden','interview_slot_conflict'),exc.code
    else:raise AssertionError('unknown retried')
    await h.command(aid,'abandon',{'pending_key':command.business_key})
    try:await h.command(aid,'ask',{'mode':'first'})
    except InterviewRefusal as exc:assert exc.code=='window_unavailable',exc.code
    else:raise AssertionError('abandon granted unknown resend')
    atomic_json(h.out/'unknown-abandon-retention.json',h.snapshot(aid))
    # A received-invalid response is a real terminal with no domain effect; new explicit key may retry.
    valid=await start_goal(h,[T_NAME],'余额算法结构校验',{T_NAME:'reference'})
    os.environ['RETROLUME_TASK106_SCENARIO']='invalid_output'
    try:failed,failed_command=await h.command(valid,'ask',{'mode':'first'})
    finally:os.environ.pop('RETROLUME_TASK106_SCENARIO',None)
    assert failed['status']=='failed' and not failed['effect_applied'],failed
    retry,_=await h.command(valid,'ask',{'mode':'first','retry_of':failed_command.business_key});assert retry['status']=='committed',retry
    state=h.snapshot(valid);assert state['activity']['requests_reserved']==2 and len(state['results'])==1,state
    atomic_json(h.out/'received-invalid-explicit-retry.json',dict(failed=failed,retry=retry,state=state))
    print(json.dumps(dict(exact_windows=4,atomic_rollback=True,unknown_no_retry=True,explicit_received_invalid_retry=True)))


def main():
    if sys.platform=='win32':asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    with batch('P05-exact-windows-atomic-unknown-safe-retry') as out:
        try:
            admin=start(1);app,denied=runtime(admin);h=Harness(admin,app,out)
            asyncio.run(verify(h))
        finally:stop(1)


if __name__=='__main__':main()
