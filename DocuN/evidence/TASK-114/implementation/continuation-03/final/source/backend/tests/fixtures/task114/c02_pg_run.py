"""C02同一PG根分段入口；每段关闭准确消费者，已完成fixture只读复用。"""
import argparse
import asyncio
import json
import shutil
import sys
import time
from pathlib import Path
from uuid import uuid4
from unittest.mock import patch
from budget import ROOT,EVIDENCE,Budget,FactoryHooks
from c02_common import reference,environment,Evidence,start_source,stop_source,SYNTHETIC,IMAGE,memory_guard
from freeze import freeze
sys.path.insert(0,str(ROOT/'backend'))
from app.data_exit.contracts import DataJobCommand,DataError,canonical,digest
from app.data_exit.operations import Operation,request_cancel
from app.data_exit.restore import TargetRef,inspect_target
from app.data_exit.readability import memory_projection,history_qualification
from app.runtime import psycopg_compatible_loop_factory

FIXTURE=EVIDENCE/'fixture.json'


def runtime(credentials,budget):
    environment(credentials)
    from app.main import create_app
    app=create_app();rt=app.state.data_exit
    if rt is None:raise RuntimeError('C02入口失败: '+str(app.state.data_exit_error))
    rt.factory.hooks=FactoryHooks(budget)
    return rt


def check_memories(rt,fixture):
    result={}
    with rt.source.connection(readonly=True,repeatable=True) as conn:
        for name,memory in fixture['memories'].items():
            body,reason=memory_projection(conn,memory['memory_id'],memory['version'])
            head=conn.execute('SELECT state,revision,current_version,purge_state FROM public.learning_memories WHERE memory_id=%s',(memory['memory_id'],)).fetchone()
            retained=conn.execute('SELECT body FROM public.learning_memory_bodies WHERE memory_id=%s AND version=%s',(memory['memory_id'],memory['version'])).fetchone()
            result[name]={'reason':reason,'body_exposed':body is not None,'body_sha256':digest(body) if body else None,'head':head,
              'stored_original_body_sha256':digest(retained['body']) if retained else None}
    return result


async def source_phase(rt,evidence,resume=False):
    from c02_seed import seed,material,invalidate_event
    if FIXTURE.exists():raise RuntimeError('seed阶段已有完成原件，不重复已完成源工作')
    with rt.source.connection(readonly=True) as conn:
        n=conn.execute('SELECT count(*) AS n FROM public.material_sources').fetchone()['n']
        if n and not resume:
            raise RuntimeError('未封口fixture已有提交前缀，需准确核对后接续')
        if resume:assert n==3
    fixture=await seed(rt,resume=resume);evidence.save('01-fixture',fixture)
    FIXTURE.write_text(json.dumps(fixture,ensure_ascii=False,indent=2),encoding='utf-8')
    before=check_memories(rt,fixture);assert all(r['reason']=='present' and r['body_exposed'] for r in before.values());evidence.save('02-all-dependencies-valid',before)
    # 合法备份取在任何失效之前，之后默认删除覆盖必须抑制相应正文。
    key='c02-valid-snapshot-'+str(uuid4());job=rt.hub.create_or_get_job(DataJobCommand('restore_checkpoint',key,{'mode':'all'}),rt.context())
    package=rt.packages.capture_and_publish(job['job_id'],{'mode':'all'});assert package['state']=='published';evidence.save('03-published',package)
    upload_id=str(uuid4());incoming=rt.incoming/(upload_id+'.rldata');shutil.copyfile(rt.packages.path(job['job_id']),incoming)
    fixture['package_job_id']=job['job_id'];fixture['package_key']=key;fixture['upload_id']=upload_id
    fixture['package_sha256']=digest(incoming.read_bytes())
    material(rt,'C02-replace-new','C02 replacement different bytes',fixture['sources']['replace'])
    from app.memory.contracts import MemoryCommandInput
    ledger=rt.app.state.activities_ledger;mid=fixture['memories']['upstream']['memory_id']
    current=await ledger.read_memory_snapshot(mid);impact=await ledger.preview_memory_change(mid,1,'revise')
    await ledger.apply_memory_command(MemoryCommandInput(business_key=str(uuid4()),memory_id=mid,expected_revision=1,action='revise',body={'kind':'preference','title':'C02-upstream-new','text':'changed upstream','base_body_sha256':current['body_sha256'],'impact_token':impact['impact_token']}))
    middle=check_memories(rt,fixture);assert middle['replace']['reason']=='dependency_invalid';assert middle['downstream']['reason']=='dependency_invalid';assert middle['event']['reason']=='present';evidence.save('04-pointer-revision-hash-and-upstream',middle)
    invalidate_event(rt,fixture);after_event=check_memories(rt,fixture);assert after_event['event']['reason']=='dependency_invalid';evidence.save('05-event-correction',after_event)
    # cancel-first实际经过source仓储入口但不进入墓碑；通用CAS替身只控制边界。
    source=fixture['sources']['delete'];impact=rt.deletions.preview(source['id'],source['revision']);cancel_key='c02-delete-cancel-'+str(uuid4())
    def cancel_started(*args,**kwargs):
        op=Operation(*args,**kwargs);request_cancel(op.hub,op.job_id);return op
    with patch('app.data_exit.deletions.Operation',side_effect=cancel_started):
        try:await rt.deletions.confirm(source['id'],source['revision'],impact['impact_sha256'],cancel_key)
        except DataError as error:assert error.code=='operation_cancelled'
        else:raise AssertionError('source取消未停止')
    assert rt.hub.get_by_key(cancel_key)['state']=='cancelled'
    with rt.source.connection(readonly=True) as conn:assert not conn.execute("SELECT 1 FROM public.data_tombstones WHERE entity_kind='source' AND entity_id=%s",(source['id'],)).fetchone()
    evidence.save('06-delete-cancel-first',{'job':rt.hub.get_by_key(cancel_key),'tombstone_absent':True,'layer':'real PG/repository; Operation-start cancellation injected'})
    admit=Operation.admit;rejected=[]
    def cancel_admitted(op,phase):
        value=admit(op,phase)
        if phase=='source_tombstone_commit':
            try:request_cancel(op.hub,op.job_id)
            except DataError as error:rejected.append(error.code)
        return value
    with patch.object(Operation,'admit',cancel_admitted):
        deleted=await rt.deletions.confirm(source['id'],source['revision'],impact['impact_sha256'],'c02-delete-'+str(uuid4()))
    assert rejected==['operation_not_cancelable'];assert deleted['state']=='deleted';fixture['deletion_job_id']=deleted['job_id'];evidence.save('07-delete-admit-first',{'job':deleted,'cancel_rejected':rejected})
    after=check_memories(rt,fixture);assert after['delete']['reason']=='source_deleted';assert after['delete']['head']['state']=='active';assert after['delete']['stored_original_body_sha256']==fixture['memories']['delete']['body_sha256'];assert after['valid']['reason']=='present';evidence.save('08-source-deleted-body-masked-head-retained',after)
    # 正常在线九guard：mode/权限/真实命中与函数context由独立方法记录。
    from c02_guards import guards
    guards(rt,fixture,evidence)
    plan=rt.restore.prepare(upload_id,'respect_current_deletions',rt.context());assert plan['latest_status']=='known' and plan['overlay_count']>=1
    fixture['plan']=plan;evidence.save('10-default-deletion-plan',plan)
    FIXTURE.write_text(json.dumps(fixture,ensure_ascii=False,indent=2),encoding='utf-8')
    return {'state':'source_phase_passed','fixture':str(FIXTURE)}


def restore_phase(rt,fixture,evidence,cancel):
    plan=fixture['plan'];job=rt.hub.create_or_get_job(DataJobCommand('restore','c02-restore-'+('cancel-' if cancel else 'normal-')+str(uuid4()),{'plan_id':plan['plan_id'],'plan_sha256':plan['plan_sha256']}),rt.context())
    if not memory_guard()['ready']:raise RuntimeError('目标job消费前内存门；不创建目标')
    loader=rt.restore._load;abandon=rt.factory.abandon
    def loaded(*args):
        proof=loader(*args);evidence.save('01-actual-loaded',proof)
        if cancel:request_cancel(rt.hub,job['job_id'])
        return proof
    def abandoned(target):
        import psycopg
        credentials=rt.factory._ephemeral[target.target_id]
        with psycopg.connect(credentials['admin_dsn'],connect_timeout=3) as conn:
            revoked=abandon(target)
            roles=conn.execute("SELECT rolname,rolcanlogin,rolpassword IS NULL FROM pg_authid WHERE rolname IN('retrolume_c02_loader','retrolume_c02_admin') ORDER BY rolname").fetchall()
            evidence.save('02-actual-revoked-before-stop',{'revoked':revoked,'roles':roles});assert revoked and all(not r[1] and r[2] for r in roles)
        return revoked
    rt.restore._load=loaded
    if cancel:rt.factory.abandon=abandoned
    if cancel:
        try:rt.restore.verify(job['job_id'],plan['plan_sha256'])
        except DataError as error:assert error.code=='operation_cancelled'
        else:raise AssertionError('load后取消仍验证')
        final=rt.hub.get(job['job_id']);assert final['state']=='cancelled'
        target=rt.hub.state()['targets'][final['target_id']];assert target['state']=='failed' and target['temporary_credentials_revoked']
        evidence.save('03-cancelled-stopped',{'job':final,'target':target,'role_and_stop':'actual'});fixture['cancel_restore_job_id']=job['job_id']
    else:
        final=rt.restore.verify(job['job_id'],plan['plan_sha256']);assert final['state']=='verified';fixture['normal_restore_job_id']=job['job_id'];evidence.save('03-verified-sealed-stopped',final)
    FIXTURE.write_text(json.dumps(fixture,ensure_ascii=False,indent=2),encoding='utf-8')
    return {'state':'cancelled_target_failed' if cancel else 'verified_target_sealed','job_id':job['job_id']}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['source','source-resume','cancel','normal']);args=parser.parse_args()
    budget=Budget();budget.check();source,credentials=reference();label='c02-pg-'+args.phase+'-'+str(time.monotonic_ns());evidence=Evidence(label,credentials)
    budget.root('c02-pg-group');freeze(label);rt=None
    try:
        if args.phase in ('source','source-resume'):
            start_source(budget,source);rt=runtime(credentials,budget)
            with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:result=runner.run(source_phase(rt,evidence,args.phase=='source-resume'))
        else:
            fixture=json.loads(FIXTURE.read_bytes());rt=runtime(credentials,budget);result=restore_phase(rt,fixture,evidence,args.phase=='cancel')
        evidence.save('result',result);return 0
    except BaseException as error:evidence.fail(error);return 1
    finally:
        stop_source(budget,source)
        if rt:
            for value in rt.hub.state()['targets'].values():
                if value.get('cid'):
                    target=TargetRef(value['target_id'],value['job_id'],value['profile_id'],value['cid'],value['name'],value['volume'],value['port'],value['dataset_id'],value['instance_id'],value['root_id'],rt.factory.root/value['job_id'])
                    rt.factory.stop(target)


if __name__=='__main__':raise SystemExit(main())
