"""每步新加载本次源；尾链使用真实仓储producer，零新Native/模型发送。"""
import asyncio,hashlib,json,os,sys,time,traceback
from pathlib import Path
from uuid import uuid4
import psycopg
from psycopg.rows import dict_row
from .control import ROOT,CONTINUE_ROOT,PERMIT,atomic,source_snapshot,reserve,run,read_state
from .resources import shell_env
from .core import Harness
from .c01_seeds import teaching_parent,diagnostic_artifact
from app.runtime import psycopg_compatible_loop_factory
from app.preview.repository import plain

async def seeds(resource,built,out):
    saved=CONTINUE_ROOT/'tail-items.json'
    if saved.exists():return json.loads(saved.read_text(encoding='utf-8'))
    h=Harness(resource,built,out);rows=[]
    try:
        await h.controller.recover();assert not h.controller.blocked,'同一C04根前提未恢复'
        for _ in range(3):
            parent=await teaching_parent(h,'energy');aid,parent_ref=parent
            from app.learning.teaching_contracts import TeachingCommandInput
            head=await h.ledger.read_teaching_head(aid)
            await h.ledger.apply_teaching_local(aid,TeachingCommandInput(business_key=str(uuid4()),expected_revision=head['revision'],expected_goal_version=head['goal_version'],expected_scope_revision=1,action='expose',body=dict(exercise_record_id=parent_ref['record_id'],part='reference')))
            item=await diagnostic_artifact(h,'energy',parent_item=parent)
            rows.append(dict(kind='energy',activity_id=aid,parent=parent_ref,receipt=item['receipt'],classification='真实合成prerequisite/producer；无transport/OneCall，不冒新Native'))
        atomic(saved,rows);return rows
    finally:await h.controller.close()

def tail(resource,built,out):
    from .http_matrix import HttpMatrix,BASE
    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:rows=runner.run(seeds(resource,built,out))
    matrix=HttpMatrix(resource,built,out)
    try:
        matrix.start();reserve('main_browser_starts',dict(purpose='C05 dedicated real tail and visibility'))
        payload=dict(base=BASE,items=rows,out=str(out),remaining_ms=max(1,int((read_state()['active_batch']['deadline_ns']-time.monotonic_ns())/1e6)-20000));atomic(out/'browser-input.json',payload)
        env=shell_env();env['RETROLUME_TASK111_BROWSER_SESSION']=matrix.token
        run(['node',str(ROOT/'frontend/tests/task111/c05_browser_host.cjs'),str(out/'browser-input.json')],out,cwd=ROOT,env=env,maximum=650,name='tail-browser')
        result=json.loads((out/'tail-result.json').read_text(encoding='utf-8'));assert result['status']=='PASS_REAL_CLIENT_TAIL_FIVE_LIFECYCLES'
    finally:
        if matrix.actual_owner and matrix.process and matrix.process.poll() is None:
            with psycopg.connect(resource['app']) as conn:sessions=conn.execute("SELECT activity_id::text,preview_id::text,generation FROM html_preview_sessions WHERE activity_id=ANY(%s::uuid[]) AND state NOT IN ('stopped','failed_unstarted')",([r['activity_id'] for r in rows],)).fetchall()
            for aid,pid,generation in sessions:
                matrix.request('POST',f'/api/activities/{aid}/html/previews/{pid}/stop',dict(generation=generation,stop_key=str(uuid4()),reason='user'))
                until=time.monotonic()+15
                while time.monotonic()<until:
                    row=matrix.request('GET',f'/api/activities/{aid}/html/previews/{pid}')
                    if row['state'] in ('stopped','cleanup_unconfirmed'):break
                    time.sleep(.05)
        if matrix.process:matrix.close()

def data(resource,out):
    with psycopg.connect(resource['app'],row_factory=dict_row) as conn:
        rows=conn.execute("SELECT preview_id::text,activity_id::text,state,reserve_seconds,elapsed_seconds,confirmation_receipt,first_stop_receipt,deadline_at,image_id FROM html_preview_sessions WHERE created_at>=%s ORDER BY created_at",(json.loads((CONTINUE_ROOT/'timing.json').read_text(encoding='utf-8'))['accepted_utc'],)).fetchall()
        old=conn.execute("SELECT preview_id::text,state,reserve_seconds,elapsed_seconds FROM html_preview_sessions WHERE preview_id='542b0750-6e02-418a-b216-5dfbd3b93047'").fetchone()
    assert old['state']=='cleanup_unconfirmed' and old['reserve_seconds']==60 and old['elapsed_seconds'] is None
    atomic(out/'sessions-final.json',plain(rows));atomic(out/'old-unknown-kept.json',plain(old))

def main():
    action=sys.argv[1];out=Path(sys.argv[2]).resolve();assert out.is_relative_to(CONTINUE_ROOT.resolve())
    resource=json.loads(os.environ.get('RETROLUME_TASK111_RESOURCE','{}'));built=json.loads((CONTINUE_ROOT/'active-build.json').read_text(encoding='utf-8'))
    from app.preview.process import birth
    atomic(out/'actual-step-owner.json',dict(pid=os.getpid(),birth=birth(os.getpid())['birth']));source_snapshot(out)
    try:
        if action=='job_probe':
            from .c05_job_probe import run as probe
            probe(out)
        elif action=='tail':tail(resource,built,out)
        elif action in ('faults','faults_remaining'):
            from .c05_faults import run_all
            if action=='faults_remaining':
                from . import c05_faults
                c05_faults.NAMES=('control_path_lost','hard_deadline')
            run_all(resource,built,out)
        elif action=='final_data':data(resource,out)
        else:raise RuntimeError('fixed C05 step')
        atomic(out/'step-result.json',dict(status='PASS_STEP_ONLY',action=action))
    except Exception:
        failure=traceback.format_exc()
        for secret in [resource.get(k,'') for k in ('admin','app','denied')]+list(resource.get('passwords',[])):
            if secret:failure=failure.replace(secret,'[redacted-task-secret]')
        (out/'failure.txt').write_text(failure,encoding='utf-8');atomic(out/'step-result.json',dict(status='FAIL',action=action));raise SystemExit(1)

if __name__=='__main__':main()
