"""Reuse exact windows and atomics; finish refusals/retry, source and memory guards."""
import asyncio,io,json,os,sys
from uuid import uuid4
from datetime import datetime,timedelta,timezone
from .control import EVIDENCE,batch,atomic_json
from .resources import start,stop,runtime
from .core import Harness
from .directed import start_goal
from .samples import T_NAME,SAMPLES
from app.interview.contracts import InterviewRefusal
from app.activities import ActivitySpec,SourceSnapshot
from app.memory.contracts import MemoryCommandInput,MemorySelectionInput


async def verify(h,old):
    aid=old[-1]['aid'];key=old[-1]['command']['business_key'];before=h.snapshot(aid)
    try:await h.command(aid,'ask',{'mode':'first','retry_of':key})
    except InterviewRefusal as exc:
        assert exc.code=='interview_slot_conflict',exc.code
        atomic_json(h.out/'actual-unknown-retry-refusal.json',dict(code=exc.code,before=before))
    else:raise AssertionError('unknown retry admitted')
    await h.command(aid,'abandon',{'pending_key':key})
    try:await h.command(aid,'ask',{'mode':'first'})
    except InterviewRefusal as exc:assert exc.code=='window_unavailable',exc.code
    else:raise AssertionError('abandon granted unknown resend')
    after=h.snapshot(aid);assert after['activity']['requests_reserved']==before['activity']['requests_reserved'] and after['results']==before['results']
    atomic_json(h.out/'unknown-retained.json',after)
    h.material(T_NAME)
    valid=await start_goal(h,[T_NAME],'余额算法结构校验',{T_NAME:'reference'})
    os.environ['RETROLUME_TASK106_SCENARIO']='invalid_output'
    try:failed,failed_command=await h.command(valid,'ask',{'mode':'first'})
    finally:os.environ.pop('RETROLUME_TASK106_SCENARIO',None)
    assert failed['status']=='failed' and not failed['effect_applied'],failed
    retry,_=await h.command(valid,'ask',{'mode':'first','retry_of':failed_command.business_key})
    assert retry['status']=='committed',retry
    state=h.snapshot(valid);assert state['activity']['requests_reserved']==2 and len(state['results'])==1,state
    atomic_json(h.out/'received-invalid-explicit-retry.json',dict(failed=failed,retry=retry,state=state))
    # Replace own material, then adopt exact current source hash/version in one local transaction.
    source=h.saved[T_NAME];newtext=SAMPLES[T_NAME]+'\n明确合成补充：请保留测量和现实数据库表现未知。\n'
    original=h.originals.put(io.BytesIO(newtext.encode('utf-8')),max_bytes=5242880)
    replacement=h.materials.save(source_id=source['id'],expected_version=source['version_id'],filename=T_NAME,format='md',sha256=original.sha256,size=original.size)
    detail=await h.ledger.read_interview_record(valid,retry['record_ids'][0]);assert detail['body'] is None,detail
    new=[dict(source_id=replacement['id'],version_id=replacement['version_id'],source_revision=replacement['revision'],original_sha256=replacement['sha256'])]
    bound,_=await h.command(valid,'bind_scope',{'sources':new,'material_roles':[{'source_id':source['id'],'role':'reference'}]})
    view=await h.ledger.read_interview_workspace(valid)
    assert bound['effect_applied'] and view['head']['scope_revision']==2 and view['head']['goal_version']==2 and view['head']['phase']=='ready',view
    assert view['head']['revision']==3,view
    atomic_json(h.out/'source-replacement-and-adoption.json',dict(old_detail=detail,bound=bound,view=view,state=h.snapshot(valid)))
    # Actual fixed G9 selection; first version refuses instead of clearing/downgrading it.
    mid=str(uuid4());mem=MemoryCommandInput.model_validate(dict(schema='memory.command.v1',business_key=str(uuid4()),memory_id=mid,
        expected_revision=0,action='save',body=dict(title='TASK106虚构偏好',text='偏好文字题，明确自报',kind='preference',capture=None)))
    receipt=await h.ledger.apply_memory_command(mem)
    snapshot=await h.ledger.read_memory_snapshot(mid)
    # Read exact revision identity from the ordinary account without importing old runners.
    import psycopg
    from psycopg.rows import dict_row
    with psycopg.connect(h.dsn,row_factory=dict_row) as conn:
        m=conn.execute('SELECT h.revision,h.current_version,r.body_sha256 FROM learning_memories h JOIN learning_memory_revisions r ON r.memory_id=h.memory_id AND r.version=h.current_version WHERE h.memory_id=%s',(mid,)).fetchone()
    selection=MemorySelectionInput.model_validate({'confirmed':True,'entries':[dict(memory_id=mid,version=m['current_version'],revision=m['revision'],body_sha256=m['body_sha256'])]})
    selected_aid=str(uuid4())
    await h.ledger.create_activity(ActivitySpec(activity_id=selected_aid,sources=(SourceSnapshot(replacement['id'],replacement['version_id'],replacement['revision']),),
        deadline_at=datetime.now(timezone.utc)+timedelta(hours=3),max_requests=10,max_cost_microunits=100000,reserve_cost_microunits=100,
        max_request_bytes=65536,max_output_tokens=1024,max_running_seconds=3600,allowed_models=(('deepseek_chat_completions','task106-synthetic'),),max_tool_calls=0),memory_selection=selection)
    try:await h.command(selected_aid,'start',{'goal':None})
    except InterviewRefusal as exc:assert exc.code=='interview_memory_not_supported',exc.code
    else:raise AssertionError('selected memory activity entered interview')
    view=await h.ledger.read_interview_workspace(selected_aid);assert view['head'] is None and view['suppression_reason']=='interview_memory_not_supported',view
    atomic_json(h.out/'actual-memory-selection-refusal.json',dict(memory_id=mid,selection=selection.model_dump(),view=view,receipt=receipt))
    print(json.dumps(dict(unknown_refusal=True,abandon_not_authority=True,received_invalid_retry=True,source_adoption_atomic=True,actual_memory_selection_refused=True)))


def main():
    if sys.platform=='win32':asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    old=json.loads((EVIDENCE/'runs/P06-resume-late-diagnostic-atomic-and-retry/effects.json').read_text(encoding='utf-8'))
    with batch('P07-tail-retry-source-selection') as out:
        try:
            admin=start(1);app,denied=runtime(admin);h=Harness(admin,app,out)
            asyncio.run(verify(h,old))
        finally:stop(1)


if __name__=='__main__':main()
