"""One original-source drain/fence/selector, same sealed target, then normal read-only reopen."""
from batch_runtime import *
from frozen_http import FrozenFlow
from profiles_batch import factory_profile,Hooks
from app.data_exit.control import ControlHub
from app.data_exit.repository import DataRepository
from app.data_exit.restore import TargetFactory
def main():
    preflight('S06-R02-original-selector')
    with Batch(24,'S06-R02-formal-selector-and-reopen') as batch:
        hub=ControlHub(EXEC/'synthetic/source-control');state=hub.state();assert state['selection'] is None and state['fence'] is None
        factory=TargetFactory(hub,EXEC/'synthetic/source-restore',factory_profile());factory.hooks=Hooks(batch.run,factory)
        target=factory.target('634aa034-51f6-4510-b075-38cb005481d8')
        batch.run.register('sealed-original-success01',lambda:factory.stop(target),priority=0)
        batch.run.register('source-hub-lock',hub.lock.close,priority=1);batch.run.register('source-operation-lock',hub.operation_lock.close,priority=1)
        rc.start_pg('source')
        job=state['jobs']['55957ddd-20dc-498b-972f-66f3805679cb'];plan=json.loads(hub.read_artifact('plans',job['scope']['plan_id'],job['scope']['plan_sha256']))
        latest=DataRepository(rc.dsn('source')).latest();covered={(r['entity_kind'],r['entity_id'],r['effective_revision']) for r in plan['overlay']}
        missing=[r for r in latest['tombstones'] if (r['entity_kind'],r['entity_id'],r['effective_revision']) not in covered]
        outstanding=[r for r in hub.state()['owned'].values() if r['state']!='ended']
        c.write(C01/'R02-current-overlay-and-owned.json',{'sample':c.sample(),'current_tombstones':latest['tombstones'],'current_missing':missing,'outstanding_owned':outstanding,'target_id':target.target_id,'original_job':job['job_id'],'plan_sha256':job['scope']['plan_sha256'],'same_617_row_sealed_package':True,'success02_created':False})
        assert latest['status']=='known' and not missing and not outstanding
        batch.start_api(read_only_factory=True)
        proof=batch.start_browser('selector');batch.close_browser();c.count('http',proof['observed_requests']);c.event('browser_HTTP_reconciled',attempt=batch.browser_attempt,count=proof['observed_requests'])
        selected=hub.state();assert selected['selection']['target_id']==target.target_id and selected['selection']['generation']==1 and selected['fence']['state']=='frozen'
        assert not rc.metadata(next(r['cid'] for r in c.state()['resources'] if r.get('id')=='pg-source'))['running']
        batch.close_api();reopen=batch.fresh_api_handle();reopen.start_api(read_only_factory=True)
        flow=FrozenFlow('R02-normal-readonly-reopen')
        try:
            caps=flow.call('GET','/api/data/capabilities');assert caps['read_only'] and caps['selection_generation']==1 and caps['format']=='data_exit.v1.r02'
            records=flow.call('GET','/api/data/saved-records?category=activities');assert records['items']
            denied=flow.call('POST','/api/activities',{},expected=409);assert 'data_readonly' in str(denied)
            assert hub.state()['selection']==selected['selection']
            c.write(C01/'R02-formal-readonly-reopen.json',{'sample':c.sample(),'selector':selected['selection'],'fence':selected['fence'],'caps':caps,'records':records,'write_refusal':denied,'source_PG_stopped':True,'normal_config_reopen_no_source_fallback':True,'same_original_control_root':True,'new_restore_or_target':False,'product_config_sha256':c.sha((ROOT/'backend/app/data_exit/config.py').read_bytes()),'final_browser_proof':'browser-'+str(batch.browser_attempt)+'/proof.json'})
        finally:flow.close();reopen.close_api()
if __name__=='__main__':main()
