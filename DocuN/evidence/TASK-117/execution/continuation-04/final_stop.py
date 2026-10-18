"""Fresh stop observation including the recovered precreate preview; no history rewritten."""
from inspect_stop import *
import ctypes,os
from app.preview.docker_control import find_intent
from app.preview.host_job import job_name
from app.worker.windows_job import _kernel,_BASIC_ACCOUNTING

main(final=True)
pid='5c508dc7-2ac6-44fb-922b-8e8de4b9f006';folder=EXEC/'synthetic/source-data/preview-control'/pid
registry=json.loads((folder/'registry.json').read_text());proof=json.loads((folder/'recovery-proof.json').read_text())
original=json.loads((folder/'supervisor-result.json').read_text())
assert original['confirmed'] is False and proof['tree_confirmation']=='never_started' and registry['complete']
owners={k:registry[k] for k in ('parent','reaper_launcher')};ready=json.loads((folder/'reaper-ready.json').read_text());owners['late_reaper']={k:ready[k] for k in ('pid','birth')}
observed={}
for name,owner in owners.items():
    actual=birth(owner['pid']);ended=actual['state']=='exited' or actual['state']=='running' and actual.get('birth')!=owner['birth']
    observed[name]={'original':owner,'current':actual,'original_instance_ended':ended};assert ended
lookup={'product_lookup':'not_attempted'}
try:
    assert find_intent(registry['intent']['docker'],registry['intent']) is None
    lookup['product_lookup']='absent'
except Exception as error:
    # A current diagnostic is not a replacement StopProof or a deadline relaxation.
    lookup['product_lookup']='unconfirmed';lookup['error_type']=type(error).__name__
    value=rc.docker(['ps','-a','--no-trunc','--filter','name=^/'+registry['intent']['name']+'$',
        '--filter','label=retrolume.nonce='+registry['intent']['nonce'],'--format','{{.ID}}'],timeout=30)
    assert not value;lookup['current_metadata_lookup']='exact_name_nonce_absent';lookup['not_a_StopProof_replacement']=True
api=_kernel();jobs=[]
for role in ('SUP','REAP'):
    name=job_name(pid,registry['intent']['nonce'],role);ctypes.set_last_error(0);handle=api.OpenJobObjectW(0x0004,False,name);error=ctypes.get_last_error()
    if handle:
        try:
            account=_BASIC_ACCOUNTING();assert api.QueryInformationJobObject(handle,1,ctypes.byref(account),ctypes.sizeof(account),None)
            jobs.append({'name':name,'current_observation':'queried','ActiveProcesses':account.ActiveProcesses});assert account.ActiveProcesses==0
        finally:api.CloseHandle(handle)
    else:
        assert error==2;jobs.append({'name':name,'current_observation':'not_found','open_error':error,'not_claimed_zero_or_historical_proof':True})
c.write(N/'final-old-preview-stop.json',{'sample':c.sample(),'preview_id':pid,'registry_sha256':c.sha((folder/'registry.json').read_bytes()),
    'recovery_proof':proof,'recovery_sha256':c.sha((folder/'recovery-proof.json').read_bytes()),'first_StopProof':'UNCONFIRMED retained',
    'first_supervisor_result_sha256':c.sha((folder/'supervisor-result.json').read_bytes()),'exact_name_nonce_container_absent':True,
    'owners':observed,'jobs':jobs,'lookup':lookup,'new_preview_create_start_attempts':0,'all_current_owned_preview_instances_stopped':True})
print('recovered original preview: exact process births ended, name/nonce absent, current Jobs observed')
