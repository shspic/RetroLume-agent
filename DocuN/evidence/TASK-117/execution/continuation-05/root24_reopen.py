"""Continue root24 original deadline; permanent selected R02 only, no source start or activation retry."""
from batch_runtime import *
from frozen_http import FrozenFlow
from profiles_batch import factory_profile,Hooks
from app.data_exit.control import ControlHub
from app.data_exit.restore import TargetFactory
def main():
    preflight('S06-R02-permanent-readonly-reopen')
    with Batch(24,'S06-R02-formal-selector-and-reopen') as batch:
        hub=ControlHub(EXEC/'synthetic/source-control');state=hub.state();selection=state['selection'];assert selection['target_id']=='634aa034-51f6-4510-b075-38cb005481d8' and selection['generation']==1
        assert state['fence']['state']=='frozen'
        factory=TargetFactory(hub,EXEC/'synthetic/source-restore',factory_profile());factory.hooks=Hooks(batch.run,factory);target=factory.target(selection['target_id'])
        batch.run.register('same-selected-R02-target',lambda:factory.stop(target),priority=0)
        batch.run.register('source-hub-lock',hub.lock.close,priority=1);batch.run.register('source-operation-lock',hub.operation_lock.close,priority=1)
        factory.start(target);credentials=factory.readonly_credentials(target.target_id);factory._wait_pg(credentials['readonly_dsn']);credentials.clear()
        batch.start_api(read_only_factory=True);flow=FrozenFlow('R02-normal-readonly-reopen')
        try:
            caps=flow.call('GET','/api/data/capabilities');assert caps['read_only'] and caps['selection_generation']==1 and caps['format']=='data_exit.v1.r02'
            records=flow.call('GET','/api/data/saved-records?category=activities');assert records['items']
            denied=flow.call('POST','/api/activities',{},expected=409);assert 'data_readonly' in str(denied)
            proof=batch.start_browser('selected-reader');batch.close_browser();c.count('http',proof['observed_requests']);c.event('browser_HTTP_reconciled',attempt=batch.browser_attempt,count=proof['observed_requests'])
            assert hub.state()['selection']==selection
            source=rc.metadata(next(r['cid'] for r in c.state()['resources'] if r.get('id')=='pg-source'));assert not source['running'] and source['pid']==0
            c.write(C01/'R02-formal-readonly-reopen.json',{'sample':c.sample(),'selector':selection,'fence':state['fence'],'caps':caps,'records':records,'write_refusal':denied,'source_PG_stopped':True,'normal_config_reopen_no_source_fallback':True,'same_original_control_root':True,'new_restore_or_target':False,'product_config_sha256':c.sha((ROOT/'backend/app/data_exit/config.py').read_bytes()),'final_browser_proof':'browser-'+str(batch.browser_attempt)+'/proof.json','activation_original':'browser-15/proof.json','late_response_subset':'R02-selector-increment.json'})
        finally:flow.close()
if __name__=='__main__':main()
