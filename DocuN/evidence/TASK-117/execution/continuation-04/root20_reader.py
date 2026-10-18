"""Real sealed R01, standalone read-only host, no source activation or writer secrets."""
from batch_runtime import *
from frozen_http import FrozenFlow
from profiles_batch import factory_profile,Hooks
from app.data_exit.control import ControlHub
from app.data_exit.restore import TargetFactory

def main():
    preflight('S05-R01-reader')
    with Batch(20,'S05-R01-isolated-reader') as batch:
        hub=ControlHub(EXEC/'synthetic/source-control');before=hub.state()
        factory=TargetFactory(hub,EXEC/'synthetic/source-restore',factory_profile())
        target=factory.target('05abc665-bbf9-4d41-abf0-7fc607049bf8')
        assert target.schema_profile=='data_exit.v1.r01'
        credentials=factory.readonly_credentials(target.target_id)
        factory.hooks=Hooks(batch.run,factory)
        batch.run.register('sealed-R01-target',lambda:factory.stop(target),priority=0)
        batch.run.register('source-hub-lock',hub.lock.close,priority=1)
        batch.run.register('source-operation-lock',hub.operation_lock.close,priority=1)
        factory.start(target);factory._wait_pg(credentials['readonly_dsn'])
        batch.start_reader_api(target,credentials['readonly_dsn']);credentials.clear()
        flow=FrozenFlow('R01-readonly-HTTP')
        try:
            caps=flow.call('GET','/api/data/capabilities');assert caps['binding_kind']=='isolated_sealed_reader'
            assert caps['read_only'] and not caps['restore_executor_configured'] and not caps['backup_available']
            records={name:flow.call('GET','/api/data/saved-records?category='+name) for name in ('activities','learning','teaching','interview','memories','preview_history','versions')}
            assert records['activities']['items']
            refused=[]
            for path,body in (('/api/activities',{}),('/api/memories/commands',{}),('/api/materials?filename=forbidden.md',{}),('/api/data/jobs',{'kind':'restore_checkpoint','business_key':str(time.time_ns()),'scope':{'mode':'all'},'confirm':True})):
                value=flow.call('POST',path,body,expected=409);assert 'data_readonly' in str(value);refused.append({'path':path,'value':value})
            assert hub.state()['selection']==before['selection'] is None and hub.state()['fence']==before['fence'] is None
            c.write(C01/'R01-reader-verified.json',{'sample':c.sample(),'target_id':target.target_id,'cid':target.cid,'caps':caps,'records':records,'writes_refused':refused,'source_selector_and_fence_unchanged':True,'formal_activation':False,'only_reader_credentials_in_host':True})
            if rc.available_memory_bytes()>=768*1024**2:
                proof=batch.start_browser('reader');batch.close_browser()
                c.count('http',proof['observed_requests']);c.event('browser_HTTP_reconciled',attempt=batch.browser_attempt,count=proof['observed_requests'])
            else:c.write(C01/'R01-UI-memory-gate.json',{'sample':c.sample(),'available':rc.available_memory_bytes(),'minimum':768*1024**2,'browser_started':False})
        finally:flow.close()

if __name__=='__main__':main()
