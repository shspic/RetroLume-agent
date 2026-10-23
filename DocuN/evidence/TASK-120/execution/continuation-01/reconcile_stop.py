"""Cleanup only: settle an already-returned startup, exact existing objects."""
import json,socket,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5];sys.path.insert(0,str(ROOT/'backend'))
from tests.fixtures.task120 import resources as r
from app.preview.process import birth
from app.worker.windows_job import NamedJob,JobOpenError
b=r.state();root=b['active_root']
if root is None:raise SystemExit('no unreconciled root')
slot=next(x for x in b['roots'] if x['id']==root);observed=birth(slot['owner']['pid'])
if observed.get('state')=='running' and observed.get('birth')==slot['owner']['birth']:raise SystemExit('root owner still active')
try:job=NamedJob.open_existing(slot['identity'],1)
except JobOpenError as exc:
    if exc.code!=2:raise
    job_proof={'absent':True}
else:
    try:
        job.terminate();assert job.wait_empty_until(time.monotonic_ns()+5_000_000_000)
        job_proof={'active_processes':job.active_processes()}
    finally:job.close()
pg=r.stop_pg();ports={};until=time.monotonic()+10
while True:
    for name,port in b['ports'].items():
        with socket.socket() as probe:
            probe.settimeout(.2);ports[name]={'port':port,'listening':probe.connect_ex(('127.0.0.1',port))==0}
    if not any(x['listening'] for x in ports.values()) or time.monotonic()>=until:break
    time.sleep(.2)
confirmed=not any(x['listening'] for x in ports.values()) and pg['state']['Running'] is False and pg['state']['Pid']==0
proof={'utc':r.utc(),'root':root,'cleanup_only':True,'job':job_proof,'container':pg,'ports':ports,'all_confirmed':confirmed,'memory_available_bytes':r.available_memory()}
r.write(r.EVIDENCE/'continuation-01'/f'root-{root:02d}-stop-reconciliation.json',proof)
if confirmed:
    def reconcile(value):
        assert value['active_root']==root
        value['active_root']=None;value['needs_reconcile']=False
        value['roots'][-1]['stop_reconciliation']=f'continuation-01/root-{root:02d}-stop-reconciliation.json'
    r.update(reconcile)
print(json.dumps({'all_confirmed':confirmed,'ports':ports,'available_memory_bytes':proof['memory_available_bytes']}))
if not confirmed:raise SystemExit(1)
