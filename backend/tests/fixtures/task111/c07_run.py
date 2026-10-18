"""本地build/load与真实PG/生产控制合并根；PG持有和清场全计区间并集。"""
import asyncio,hashlib,json,os,subprocess,sys,time,traceback
from pathlib import Path
import psycopg
from psycopg.rows import dict_row
from .control import ROOT,CONTINUE_ROOT,CONTINUATION,PERMIT,EVIDENCE,atomic,batch,phase,read_state,source_snapshot,locked,event,registry_root
from .resources import build_renderer,pg_resume,shell_env
from .c03_resources import guardian,cleanup
from .c05_faults import PassiveWitness
from .core import Harness
from app.preview.process import birth,terminate_owned
from app.preview.repository import plain
from app.runtime import psycopg_compatible_loop_factory

CASES=('normal_bom_header','late_ready','stderr_overflow','null_init','bom_body','stderr_no_eof')

async def recover_no_eof(resource,built,out,witness):
    observed=witness.drain(out);h=Harness(resource,built,out)
    try:
        trigger=json.loads((out/'trigger.json').read_text(encoding='utf-8'));before=await h.ledger.read_html_preview(trigger['activity_id'],trigger['preview_id'])
        assert before['state']=='cleanup_unconfirmed' and before['elapsed_seconds'] is None
        await h.controller.recover(recovery_observation=observed);assert not h.controller.blocked,'缺EOF反例同根完整恢复失败'
        after=await h.ledger.read_html_preview(trigger['activity_id'],trigger['preview_id']);assert after['state']=='stopped' and after['elapsed_seconds']==60 and after['reserved_seconds']==0
        proof=json.loads((Path(trigger['runtime_folder'])/'recovery-proof.json').read_text(encoding='utf-8'))
        atomic(out/'same-root-persistent-recovery.json',dict(before=before,after=after,proof=proof,actual_EOF_observation=observed,full_R_consumed=True,
            no_unknown_refund=True,same_root=str(registry_root()),physical_external_kill_used=False))
    finally:await h.controller.close()

def actor(resource,built,out,name,active):
    env=shell_env();env.update(RETROLUME_TASK111_FIXTURE=PERMIT,RETROLUME_TASK111_RESOURCE=json.dumps(resource))
    witness=None
    with (out/'actor.stdout.bin').open('wb') as stdout,(out/'actor.stderr.bin').open('wb') as stderr:
        child=subprocess.Popen([sys.executable,'-B','-m','tests.fixtures.task111.c07_actor',name,str(out)],cwd=ROOT/'backend',env=env,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
        atomic(out/'launcher.json',dict(pid=child.pid,birth=birth(child.pid)))
        try:
            if name=='stderr_no_eof':
                until=min(active['deadline_ns']-30*10**9,time.monotonic_ns()+15*10**9)
                while not (out/'pretrigger.json').exists():
                    if child.poll() is not None or time.monotonic_ns()>=until:raise RuntimeError('缺EOF反例未到准确READY绑定')
                    time.sleep(.02)
                witness=PassiveWitness(json.loads((out/'pretrigger.json').read_text(encoding='utf-8')))
                atomic(out/'witness-bound.json',dict(observer=witness.observer,no_extra_Job_handles=True,actual_read_handles_duplicated=True,actual_sync_handles=True))
            child.wait(timeout=max(.1,(active['deadline_ns']-time.monotonic_ns())/1e9-30))
            if witness:
                with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(recover_no_eof(resource,built,out,witness))
            result=dict(scenario=name,exit=child.returncode,folder=str(out),completed_ns=time.monotonic_ns())
            if child.returncode==0:
                report=json.loads((out/'actor-result.json').read_text(encoding='utf-8'));result['status']=report['status'];result['preview_id']=report['row']['preview_id']
            else:
                result['status']='FAIL_RETAINED'
                # 普通方法失败只有准确完整的本对象停止事实才允许继续余项。
                pointer=json.loads((registry_root()/'current.json').read_text(encoding='utf-8'))
                if not pointer.get('complete'):raise RuntimeError('失败对象未完整确认；暂停依赖，不换根')
            atomic(out/'scenario-result.json',result);event('C07_case_completed',result);return result
        finally:
            if child.poll() is None:
                owned=json.loads((out/'actor-owner.json').read_text(encoding='utf-8'));terminate_owned(owned['pid'],owned['birth']);child.wait(5)
            if witness:witness.close()

def data(resource,out):
    start=json.loads((CONTINUE_ROOT/'accepted.json').read_text(encoding='utf-8'))['first_clock_utc']
    with psycopg.connect(resource['app'],row_factory=dict_row) as conn:
        rows=conn.execute("SELECT preview_id::text,activity_id::text,state,reserve_seconds,elapsed_seconds,confirmation_receipt,first_stop_receipt,deadline_at,image_id FROM html_preview_sessions WHERE created_at>=%s ORDER BY created_at",(start,)).fetchall()
        old=conn.execute("SELECT preview_id::text,state,reserve_seconds,elapsed_seconds FROM html_preview_sessions WHERE preview_id='542b0750-6e02-418a-b216-5dfbd3b93047'").fetchone()
    assert old['state']=='cleanup_unconfirmed' and old['reserve_seconds']==60 and old['elapsed_seconds'] is None
    atomic(out/'sessions-final.json',plain(rows));atomic(out/'old-unknown-kept.json',plain(old))

def main():
    assert CONTINUATION=='TASK-111-G11-C07-20261012'
    prior=read_state();number=prior['counts']['real_batches']+1;assert number in (19,20)
    names=CASES if len(sys.argv)==1 else tuple(sys.argv[1:]);assert all(x in CASES for x in names)
    root=CONTINUE_ROOT/('root-'+str(number));root.mkdir(exist_ok=False);guard=None;resource=None;results=[];phase('real')
    try:
        with batch('real','C07 new image and targeted actual pipe/PG cases',maximum=1800) as active:
            source_snapshot(root);atomic(root/'owner.json',dict(pid=os.getpid(),birth=birth(os.getpid()),deadline_ns=active['deadline_ns']))
            built_path=CONTINUE_ROOT/'active-build.json'
            if not built_path.exists():
                (root/'build').mkdir()
                built=build_renderer(root/'build');atomic(built_path,built)
                prior_build=json.loads((EVIDENCE/'continuation-06/active-build.json').read_text(encoding='utf-8'))
                assert built['renderer_sha256']==prior_build['renderer_sha256'] and built['image']['id']!=prior_build['image']['id'] and built['load_manifest_sha256']!=prior_build['load_manifest_sha256']
            else:
                built=json.loads(built_path.read_text(encoding='utf-8'))
                assert built['source_files']['renderer-protocol.cjs']==hashlib.sha256((ROOT/'deploy/preview/renderer-protocol.cjs').read_bytes()).hexdigest()
            try:
                guard=guardian(root,active['deadline_ns']-15*10**9);resource=pg_resume(root)
                for name in names:
                    if time.monotonic_ns()>=active['deadline_ns']-90*10**9:raise RuntimeError('真实根余时不足，保清场')
                    out=root/name;out.mkdir();results.append(actor(resource,built,out,name,active));atomic(root/'case-results.json',results)
                    print(json.dumps(results[-1],ensure_ascii=False),flush=True)
                data(resource,root)
            finally:
                receipt=cleanup(root,guard)
                assert receipt['confirmed']
                # 清场在本根内，已被外层real区间包含；从cleanup分类扣回以防双计。
                with locked():
                    b=read_state();b['time_seconds']['cleanup']-=receipt['seconds'];atomic(EVIDENCE/'budget.json',b)
                atomic(root/'interval-accounting.json',dict(real_union_start_ns=active['start_ns'],real_union_end_ns=time.monotonic_ns(),
                    includes=['本地build/load','PG启动/持有','case与修正等待','PG停止确认外围'],cleanup_seconds_reclassified=receipt['seconds'],
                    resource_held_after_root=False,overlap_added_seconds=0))
                event('C07_cleanup_inside_real_union',dict(root=number,receipt=receipt),cleanup=True)
            atomic(root/'result.json',dict(status='PASS_ALL_SELECTED_TARGETED_REAL_CASES' if all(r['exit']==0 for r in results) else 'RETAINED_ORDINARY_FAILURES',cases=results))
    except Exception:
        text=traceback.format_exc()
        if resource:
            for secret in [resource.get(k,'') for k in ('admin','app','denied')]+list(resource.get('passwords',[])):
                if secret:text=text.replace(secret,'[redacted-task-secret]')
        (root/'root-failure.txt').write_text(text,encoding='utf-8');raise
    finally:phase('implementation_offline')

if __name__=='__main__':main()
