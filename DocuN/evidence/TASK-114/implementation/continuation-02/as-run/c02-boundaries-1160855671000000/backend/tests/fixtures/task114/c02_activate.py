"""最后正常选择：先cancel-first/实际selector拒绝，冻结保持；后明确新确认选择。

不重复source写/播种、不借旧selector，所有不可逆事实及未确认job保留。
"""
import asyncio
import json
import time
from uuid import uuid4
from unittest.mock import patch
from budget import Budget,ROOT,EVIDENCE
from c02_common import reference,start_source,stop_source,Evidence,IMAGE,environment
from c02_pg_run import runtime,FIXTURE
from c02_http import Api,projection
from freeze import freeze
from app.data_exit.operations import Operation,request_cancel
from app.data_exit.contracts import DataError
from app.data_exit.restore import inspect_target
from app.runtime import psycopg_compatible_loop_factory


async def activate(rt,fixture,evidence):
    rid=fixture['normal_restore_job_id'];sha=fixture['plan']['plan_sha256'];key='c02-activate-cancel-'+str(uuid4())
    before=rt.hub.state();assert before['selection'] is None and before['fence'] is None
    def cancelled(*args,**kwargs):
        op=Operation(*args,**kwargs);request_cancel(op.hub,op.job_id);return op
    with patch('app.data_exit.restore.Operation',side_effect=cancelled):
        try:await rt.restore.activate_readonly(rid,sha,key,0)
        except DataError as error:assert error.code=='operation_cancelled'
        else:raise AssertionError('取消仍进入维护')
    after=rt.hub.state();assert after['selection'] is None and after['fence'] is None;assert after['jobs'][rt.hub.get_by_key(key)['job_id']]['state']=='cancelled'
    evidence.save('01-activate-cancel-first',{'job':rt.hub.get_by_key(key),'fence':None,'selector':None,'layer':'actual new source/control, injected cancel before irreversible admission'})
    commit=rt.hub.commit;reject_key='c02-selector-reject-'+str(uuid4())
    def rejected(kind,payload,**kwargs):
        if kind=='selector_commit':raise DataError('control_unavailable',503)
        return commit(kind,payload,**kwargs)
    with patch.object(rt.hub,'commit',rejected):
        try:await rt.restore.activate_readonly(rid,sha,reject_key,0)
        except DataError as error:assert error.code=='control_unavailable'
        else:raise AssertionError('selector拒绝未执行')
    state=rt.hub.state();assert state['selection'] is None and state['fence']['state']=='frozen';assert rt.source.state()['mode']=='frozen'
    target=rt.factory.target(state['jobs'][rid]['target_id']);assert not inspect_target(target,IMAGE)['running']
    evidence.save('02-actual-maintenance-selector-rejection',{'job':rt.hub.get_by_key(reject_key),'fence':state['fence'],'selection':None,
      'source_mode_actual':'frozen','target_running':False,'layer':'actual source freeze/target probe; exact journal selector rejection controlled; no COMMIT claimed'})
    admit=Operation.admit;refused=[];key='c02-activate-normal-'+str(uuid4())
    def admitted(op,phase):
        value=admit(op,phase)
        if phase=='readonly_maintenance_selector':
            try:request_cancel(op.hub,op.job_id)
            except DataError as error:refused.append(error.code)
        return value
    with patch.object(Operation,'admit',admitted):result=await rt.restore.activate_readonly(rid,sha,key,0)
    assert result['state']=='active_readonly' and refused==['operation_not_cancelable'];assert rt.hub.state()['selection']['generation']==1
    evidence.save('03-normal-readonly-selection',{'job':result,'cancel_rejected':refused,'selected':rt.hub.state()['selection'],'source_mode_actual':rt.source.state()['mode']})
    fixture['activation_key']=key;fixture['activation_job_id']=result['job_id'];FIXTURE.write_text(json.dumps(fixture,ensure_ascii=False,indent=2),encoding='utf-8')
    return target


def main():
    budget=Budget();budget.check();source,credentials=reference();fixture=json.loads(FIXTURE.read_bytes());label='c02-activate-'+str(time.monotonic_ns());evidence=Evidence(label,credentials);rt=None;target=None
    budget.root('c02-pg-group');freeze(label)
    try:
        start_source(budget,source);rt=runtime(credentials,budget)
        with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:target=runner.run(activate(rt,fixture,evidence))
        # 当前副本HTTP、旧业务键、旧包都从同Hub只读核对；source不回源。
        environment(credentials)
        with Api(budget,evidence) as api:
            caps,headers=projection(api,fixture,evidence,restored=True);assert caps['selection_generation']==1 and caps['read_only']
            readonly=rt.factory.readonly_credentials(target.target_id)
            import psycopg
            before=rt.hub.path.read_bytes();reads=[]
            for job in rt.hub.state()['jobs'].values():
                response=api.client.get('/api/data/jobs/by-key/'+job['business_key'],headers=api.headers);assert response.status_code==200 and response.json()['job_id']==job['job_id'];reads.append(job['job_id'])
            response=api.client.get('/api/data/packages/'+fixture['package_job_id']+'/content',headers=api.headers);assert response.status_code==200 and __import__('hashlib').sha256(response.content).hexdigest()==fixture['package_sha256']
            assert rt.hub.path.read_bytes()==before
            bad=api.client.post('/api/materials?filename=should-not-write.md',headers=headers,content=b'not written');assert bad.status_code==409 and bad.json()['code']=='data_readonly'
            evidence.save('04-selected-HTTP-old-Hub',{'old_jobs':reads,'old_package_sha256':fixture['package_sha256'],'GET_journal_unchanged':True,'business_write_rejected':bad.json()})
            with psycopg.connect(readonly['readonly_dsn'],connect_timeout=3) as conn:
                roles=conn.execute("SELECT rolname,rolcanlogin,pg_has_role(rolname,'retrolume_data_restore_loader','MEMBER') FROM pg_roles WHERE rolname IN('retrolume_c02_loader','retrolume_c02_admin') ORDER BY rolname").fetchall();assert all(not r[1] and not r[2] for r in roles if r[0].endswith('loader'))
                evidence.save('05-selected-target-role-facts',{'roles':roles,'source_id':source.dataset_id,'target_dataset_id':target.dataset_id,'target_instance_id':target.instance_id})
        evidence.save('result',{'state':'passed','normal_selection_generation':1,'old_selector_touched':False});return 0
    except BaseException as error:evidence.fail(error);return 1
    finally:
        if target is not None and rt is not None:rt.factory.stop(target)
        elif rt is not None:
            for value in rt.hub.state()['targets'].values():
                if value.get('state')=='sealed':rt.factory.stop(rt.factory.target(value['target_id']))
        stop_source(budget,source)


if __name__=='__main__':raise SystemExit(main())
