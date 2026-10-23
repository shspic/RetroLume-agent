"""Exact read-only resume proof, then prospective append to the sole ledger."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,socket,sys,time
ROOT=Path(__file__).resolve().parents[5]
sys.path.insert(0,str(ROOT/'backend'))
from tests.fixtures.task120 import resources as r
from app.preview.process import birth
from app.worker.windows_job import NamedJob,JobOpenError

OUT=Path(__file__).resolve().parent
permit_path=ROOT/'DocuN/evidence/TASK-120/orchestration-continuation01-20261019/permit.json'
permit=json.loads(permit_path.read_text(encoding='utf-8'))
b=r.state()
assert b['active_root'] is None and b['active_command'] is None
assert b['counts']==permit['old_counts_at_return'] and b['caps']==permit['old_caps']
assert len(b['failures'])==25 and not any(x.get('id')==permit['id'] for x in b.get('permit_history',[]))
assert b['actual_first_tool_utc']==permit['actual_first_tool_utc_unchanged']
assert b['calendar_deadline_utc']==permit['calendar_deadline_utc_unchanged']
assert datetime.now(timezone.utc).timestamp()<datetime.fromisoformat(b['calendar_deadline_utc'].replace('Z','+00:00')).timestamp()-1800
container=r.owned(r.container(),b['pg_registry'])
assert container['Id']==permit['container_id'] and container['Image']==permit['image_id']
assert container['state']['Running'] is False and container['state']['Pid']==0
jobs=[]
for root in b['roots']:
    try:job=NamedJob.open_existing(root['identity'],1)
    except JobOpenError as exc:
        if exc.code!=2:raise
        count=0
    else:
        try:count=job.active_processes()
        finally:job.close()
    owner=root['owner'];actual=birth(owner['pid'])
    assert count==0 and not (actual.get('state')=='running' and actual.get('birth')==owner['birth'])
    jobs.append({'root':root['id'],'active_processes':count,'owner_identity_stopped':True})
ports={}
for name,port in b['ports'].items():
    with socket.socket() as probe:
        probe.settimeout(.3);listening=probe.connect_ex(('127.0.0.1',port))==0
    assert not listening;ports[name]={'port':port,'listening':listening}
grants=[]
for slot in ('flow','budget-01'):
    config=json.loads((r.PRIVATE/slot/'q-config.json').read_text(encoding='utf-8'))
    bundle_path=Path(config['root_file']);assert bundle_path.is_relative_to(r.PRIVATE)
    bundle=json.loads(bundle_path.read_text(encoding='utf-8'));grant=bundle['grant']
    assert datetime.fromisoformat(grant['valid_until_utc'])>datetime.now(timezone.utc)
    grants.append({'slot':slot,'execution_class':bundle['execution_class'],'root_sha256':hashlib.sha256(bundle_path.read_bytes()).hexdigest(),'valid_until_utc':grant['valid_until_utc']})
proof={'utc':r.utc(),'mono_ns':time.monotonic_ns(),'all_confirmed':True,'container':container,'jobs':jobs,'ports':ports,'TESTONLY_grants':grants,'old_six_realtime_observation':'not_claimed'}
r.write(OUT/'resume-stop-proof.json',proof)
def adopt(value):
    assert value==b
    value.setdefault('permit_history',[]).append({'id':permit['id'],'received_and_adopted_utc':proof['utc'],'sampled_mono_ns':proof['mono_ns'],
        'permit_sha256':hashlib.sha256(permit_path.read_bytes()).hexdigest(),'previous_caps':value['caps'].copy(),'new_caps':permit['new_cumulative_caps'],
        'counts_retained':value['counts'].copy(),'failures_retained':len(value['failures']),'original_first_point_and_deadline_retained':True})
    value['caps']=permit['new_cumulative_caps']
    value['command_wall_cap_seconds']=permit['command_wall_cap_seconds']
    value['runtime_holding_union_cap_seconds']=permit['runtime_holding_union_cap_seconds']
    value['current_permit_id']=permit['id'];value['no_new_container_or_volume_create']=True
    value['engineering_status']='CONTINUATION_01_IN_PROGRESS';value['runtime_resume_requires_new_explicit_permit']=False
r.update(adopt)
r.event('continuation_permit_adopted',permit_id=permit['id'],old_counts=permit['old_counts_at_return'],new_caps=permit['new_cumulative_caps'])
print(json.dumps({'permit_adopted':permit['id'],'all_own_resources_stopped':True,'counts_preserved':True,'next_root':9,'Q':'FROZEN'}))
