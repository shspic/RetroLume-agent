"""S06 R01 final browser only; reuse the passed seven-category HTTP and seal evidence."""
from batch_runtime import *
from frozen_http import FrozenFlow
from profiles_batch import factory_profile,Hooks
from app.data_exit.control import ControlHub
from app.data_exit.restore import TargetFactory
def main():
    preflight('S06-R01-final-reader')
    with Batch(23,'S06-R01-final-browser') as batch:
        hub=ControlHub(EXEC/'synthetic/source-control');before=hub.state()
        factory=TargetFactory(hub,EXEC/'synthetic/source-restore',factory_profile());factory.hooks=Hooks(batch.run,factory)
        target=factory.target('05abc665-bbf9-4d41-abf0-7fc607049bf8');credentials=factory.readonly_credentials(target.target_id)
        batch.run.register('sealed-R01-target',lambda:factory.stop(target),priority=0)
        batch.run.register('source-hub-lock',hub.lock.close,priority=1);batch.run.register('source-operation-lock',hub.operation_lock.close,priority=1)
        factory.start(target);factory._wait_pg(credentials['readonly_dsn']);batch.start_reader_api(target,credentials['readonly_dsn']);credentials.clear()
        proof=batch.start_browser('reader');batch.close_browser();c.count('http',proof['observed_requests']);c.event('browser_HTTP_reconciled',attempt=batch.browser_attempt,count=proof['observed_requests'])
        assert hub.state()['selection']==before['selection'] is None and hub.state()['fence']==before['fence'] is None
        c.write(C01/'R01-final-browser-verified.json',{'sample':c.sample(),'target_id':target.target_id,'cid':target.cid,'browser_proof':'browser-'+str(batch.browser_attempt)+'/proof.json','source_selector_fence_unchanged':True,'prior_seal_HTTP':'continuation-04/R01-reader-verified.json','readonly_child_no_source_writer_loader_provider_preview_config':True})
if __name__=='__main__':main()
