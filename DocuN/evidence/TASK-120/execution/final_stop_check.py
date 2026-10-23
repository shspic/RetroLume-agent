"""Read-only exact identity stop check; never starts a service or creates a Job."""
from pathlib import Path
import json,socket,sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'backend'))
from tests.fixtures.task120 import resources as r
from app.preview.process import birth
from app.worker.windows_job import NamedJob,JobOpenError

b=r.state();jobs=[];processes=[]
for root in b['roots']:
    try:job=NamedJob.open_existing(root['identity'],1)
    except JobOpenError as exc:
        if exc.code!=2:raise
        jobs.append({'root':root['id'],'state':'named_job_absent','active_processes':0})
    else:
        try:jobs.append({'root':root['id'],'state':'observed','active_processes':job.active_processes()})
        finally:job.close()
    owner=root['owner'];observed=birth(owner['pid'])
    processes.append({'kind':'root_owner','root':root['id'],'pid':owner['pid'],'expected_birth':owner['birth'],
        'observed':observed,'same_birth_running':observed.get('state')=='running' and observed.get('birth')==owner['birth']})

for event in (r.EVIDENCE/'events.jsonl').read_text(encoding='utf-8').splitlines():
    value=json.loads(event)
    if value.get('kind')=='root_child_started':
        pid=value['pid'];expected=value['birth_100ns']
    elif value.get('kind')=='watchdog_started':
        pid=value['watchdog']['pid'];expected=value['watchdog']['birth']
    else:continue
    observed=birth(pid)
    processes.append({'kind':value['kind'],'root':value['root'],'pid':pid,'expected_birth':expected,'observed':observed,
        'same_birth_running':observed.get('state')=='running' and observed.get('birth')==expected})

container=r.owned(r.container(),b['pg_registry'])
ports={}
for name,port in b['ports'].items():
    with socket.socket() as probe:
        probe.settimeout(.3);ports[name]={'port':port,'listening':probe.connect_ex(('127.0.0.1',port))==0}
confirmed=(b['active_root'] is None and b['active_command'] is None and not container['state']['Running'] and container['state']['Pid']==0
    and all(x['active_processes']==0 for x in jobs) and not any(x['same_birth_running'] for x in processes) and not any(x['listening'] for x in ports.values()))
r.write(r.EVIDENCE/'final-stop-proof.json',{'utc':r.utc(),'read_only_recheck':True,'active_root':b['active_root'],'active_command':b['active_command'],
    'jobs':jobs,'registered_processes':processes,'container':container,'ports':ports,'all_confirmed':confirmed,
    'container_volume_databases_retained':True,'old_six_realtime_observation':'not_claimed','provider_calls':b['counts']['provider_calls']})
print(json.dumps({'all_confirmed':confirmed,'roots_observed':len(jobs),'process_identities_observed':len(processes),'pg_state':container['state'],'ports':ports}))
if not confirmed:raise SystemExit(1)
