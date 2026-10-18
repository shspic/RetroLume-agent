"""续作04已准备的单步消费者；停止后修正，下一步载入新字节。"""
import asyncio,hashlib,json,os,sys,time,traceback
from pathlib import Path
import psycopg
from psycopg.rows import dict_row
from .control import ROOT,CONTINUE_ROOT,C03_ROOT,PERMIT,atomic,source_snapshot,reserve,run,read_state
from app.runtime import psycopg_compatible_loop_factory
from app.preview.repository import plain

async def parents(resource,built,out):
    from .core import Harness
    from .c01_seeds import teaching_parent
    saved=CONTINUE_ROOT/'normal-parents.json'
    if saved.exists():return json.loads(saved.read_text(encoding='utf-8'))['parents']
    h=Harness(resource,built,out)
    try:
        await h.controller.recover();assert not h.controller.blocked
        old=json.loads((C03_ROOT/'normal-parents.json').read_text(encoding='utf-8'))
        effects=[]
        for item in old['parents']:
            with psycopg.connect(resource['app'],row_factory=dict_row) as conn:
                rows=conn.execute("SELECT c.activity_id::text,c.business_key::text,c.context_body,a.artifact_id::text,a.artifact_sha256,a.body,a.renderer_sha256,public.html_artifact_eligible(a.activity_id,a.artifact_id) AS eligible,x.deadline_at,(SELECT count(*) FROM html_preview_budgets b WHERE b.activity_id=c.activity_id) AS budget_rows FROM html_commands c JOIN html_artifacts a USING(activity_id,business_key) JOIN activities x ON x.id=c.activity_id WHERE c.activity_id=%s",(item['activity_id'],)).fetchall()
            for row in rows:
                from app.preview.compiler import verify_package
                # 包验证和资格分别核证，不能把镜像更新误写为包失效。
                try:
                    artifact=await h.ledger.read_html_artifact(item['activity_id'],row['artifact_id']);package_verified=artifact.get('description') is not None
                except Exception:package_verified=False
                effects.append(plain(dict(activity_id=row['activity_id'],artifact_id=row['artifact_id'],eligible=row['eligible'],deadline_at=row['deadline_at'],budget_rows=row['budget_rows'],readable_package=package_verified,generation_image=old['image_id'],preview_image=built['image']['id'],decision='保留旧行；实际资格不成立时新建活动生成')))
        atomic(out/'prior-Native-reuse-check.json',effects)
        rows=[]
        for kind,feedback in (('energy',False),('binomial',True)):
            aid,parent=await teaching_parent(h,kind,feedback);rows.append(dict(kind=kind,activity_id=aid,parent=parent))
        atomic(saved,dict(image_id=built['image']['id'],parents=rows));return rows
    finally:await h.controller.close()

def ui(resource,built,out):
    from .http_matrix import HttpMatrix,BASE
    from .resources import shell_env
    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:rows=runner.run(parents(resource,built,out))
    matrix=HttpMatrix(resource,built,out)
    try:
        matrix.start();reserve('main_browser_starts',dict(purpose='C04 two actual Native/UI and late guards'))
        payload=dict(base=BASE,parents=rows,out=str(out),remaining_ms=max(1,int((read_state()['active_batch']['deadline_ns']-time.monotonic_ns())/1e6)-15000));atomic(out/'browser-input.json',payload)
        env=shell_env();env['RETROLUME_TASK111_BROWSER_SESSION']=matrix.token
        run(['node',str(ROOT/'frontend/tests/task111/c04_browser_host.cjs'),str(out/'browser-input.json')],out,cwd=ROOT,env=env,maximum=600,name='real-main-ui')
        result=json.loads((out/'ui-result.json').read_text(encoding='utf-8'));atomic(CONTINUE_ROOT/'native-progress.json',result['bindings'])
        with psycopg.connect(resource['app'],row_factory=dict_row) as conn:
            values=conn.execute("SELECT c.activity_id::text,c.business_key::text,c.operation_id,c.status,c.terminal_disposition,c.config_sha256,c.request_sha256,a.artifact_id::text,a.artifact_sha256,a.body_sha256,a.renderer_sha256,o.state,r.payload_sha256 FROM html_commands c JOIN activity_operations o ON o.activity_id=c.activity_id AND o.operation_id=c.operation_id LEFT JOIN html_artifacts a ON a.activity_id=c.activity_id AND a.business_key=c.business_key LEFT JOIN activity_operation_results r ON r.activity_id=c.activity_id AND r.operation_id=c.operation_id WHERE c.activity_id=ANY(%s::uuid[])",([r['activity_id'] for r in rows],)).fetchall()
        assert len(values)==2 and all(v['terminal_disposition']=='succeeded' and v['state']=='received' for v in values);atomic(out/'same-object-commits.json',plain(values))
    finally:
        if matrix.actual_owner and matrix.process and matrix.process.poll() is None:
            from uuid import uuid4
            with psycopg.connect(resource['app']) as conn:sessions=conn.execute("SELECT activity_id::text,preview_id::text,generation FROM html_preview_sessions WHERE activity_id=ANY(%s::uuid[]) AND state NOT IN ('stopped','failed_unstarted')",([r['activity_id'] for r in rows],)).fetchall()
            for aid,pid,generation in sessions:
                matrix.request('POST',f'/api/activities/{aid}/html/previews/{pid}/stop',dict(generation=generation,stop_key=str(uuid4()),reason='user'))
                until=time.monotonic()+15
                while time.monotonic()<until:
                    row=matrix.request('GET',f'/api/activities/{aid}/html/previews/{pid}')
                    if row['state'] in ('stopped','cleanup_unconfirmed'):break
                    time.sleep(.1)
        if matrix.process:matrix.close()

def final_data(resource,out):
    with psycopg.connect(resource['app'],row_factory=dict_row) as conn:
        old=conn.execute("SELECT preview_id::text,state,reserve_seconds,elapsed_seconds FROM html_preview_sessions WHERE preview_id='542b0750-6e02-418a-b216-5dfbd3b93047'").fetchone();assert old['state']=='cleanup_unconfirmed' and old['reserve_seconds']==60 and old['elapsed_seconds'] is None
        rows=conn.execute("SELECT preview_id::text,activity_id::text,state,reserve_seconds,elapsed_seconds,confirmation_receipt FROM html_preview_sessions WHERE created_at>=%s ORDER BY created_at",(json.loads((CONTINUE_ROOT/'timing.json').read_text(encoding='utf-8'))['first_read_lower_bound_utc'],)).fetchall()
        atomic(out/'sessions-final.json',plain(rows));atomic(out/'old-unknown-kept.json',plain(old))

def main():
    if os.environ.get('RETROLUME_TASK111_FIXTURE')!=PERMIT:raise RuntimeError('fixture permit')
    action=sys.argv[1];out=Path(sys.argv[2]).resolve();assert out.is_relative_to(CONTINUE_ROOT.resolve())
    resource=json.loads(os.environ['RETROLUME_TASK111_RESOURCE']);built=json.loads((CONTINUE_ROOT/'active-build.json').read_text(encoding='utf-8'))
    from app.preview.process import birth
    atomic(out/'actual-step-owner.json',dict(pid=os.getpid(),birth=birth(os.getpid())['birth']));source_snapshot(out)
    try:
        if action=='qualify':
            from .c04_qualify import apply
            apply(resource,out)
        elif action=='pdf_verify':
            from .c04_qualify import pdf_cases
            pdf_cases(resource,out)
        elif action=='ui':ui(resource,built,out)
        elif action=='faults':
            from .c04_faults import run_all
            run_all(resource,built,out)
        elif action=='final_data':final_data(resource,out)
        else:
            with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:
                if action=='startup':
                    from .c04_startup import execute
                    runner.run(execute(resource,built,out))
                elif action=='races':
                    from .c04_races import races
                    runner.run(races(resource,built,out))
                else:raise RuntimeError('fixed C04 action')
        atomic(out/'step-result.json',dict(status='PASS_STEP_ONLY',action=action))
    except Exception:
        failure=traceback.format_exc()
        for secret in [resource.get(k,'') for k in ('admin','app','denied')]+list(resource.get('passwords',[])):
            if secret:failure=failure.replace(secret,'[redacted-task-secret]')
        (out/'failure.txt').write_text(failure,encoding='utf-8');atomic(out/'step-result.json',dict(status='FAIL',action=action));raise SystemExit(1)

if __name__=='__main__':main()
