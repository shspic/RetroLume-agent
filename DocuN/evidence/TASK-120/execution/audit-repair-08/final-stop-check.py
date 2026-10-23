"""08 exact owned objects; unknown remains unknown, with explicit Job alternatives."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,re,socket,sys,hashlib
ROOT=Path(__file__).resolve().parents[5];HERE=Path(__file__).resolve().parent;EX=HERE.parent
os.environ['RETROLUME_TASK120_CONTINUATION']='TASK-120-Q-PREP-TARGETED-REPAIR-08-20261021'
sys.path.insert(0,str(ROOT/'backend'))
from tests.fixtures.task120 import resources as r
from tests.fixtures.task120.control_job import NamedJob,JobOpenError
from tests.fixtures.task120.restore06 import identity as target_identity
from app.preview.process import birth
b=json.loads((EX/'budget.json').read_text(encoding='utf-8'));prior=json.loads((HERE/'budget.json.before.bytes').read_text(encoding='utf-8'))
registered={};names={};command_jobs={};membership={}
pattern=re.compile(r'Local\\RetroLume\.Activity\.([0-9a-f]{32})\.G([1-9][0-9]*)\Z')
def collect(v,source):
    if isinstance(v,dict):
        pid=v.get('pid');stamp=next((v[k] for k in ('birth','birth_100ns','created_100ns') if v.get(k)),None)
        if isinstance(stamp,dict):stamp=stamp.get('birth')
        if type(pid) is int and isinstance(stamp,(int,str)):registered[(pid,int(stamp))]=source
        for x in v.values():collect(x,source)
    elif isinstance(v,list):
        for x in v:collect(x,source)
    elif isinstance(v,str) and pattern.fullmatch(v):names[v]=source
for root in b['roots'][len(prior['roots']):]:collect(root,'08 sole root ledger')
prefix=(HERE/'events.jsonl.before.bytes').read_bytes();events=(EX/'events.jsonl').read_bytes();assert events.startswith(prefix)
for line in events[len(prefix):].decode('utf-8').splitlines():
    if line:collect(json.loads(line),'08 appended events')
for p in HERE.glob('command-*.receipt.json'):
    row=json.loads(p.read_text(encoding='utf-8'));collect(row,p.name)
    if row.get('tree_empty'):command_jobs[(row['pid'],int(row['birth_100ns']))]=row['job']
for p in HERE.glob('root-*-memory-samples.jsonl'):
    for line in p.read_text(encoding='utf-8').splitlines():
        row=json.loads(line);collect(row,p.name)
        # These are exact members of the registered root's named Job,
        # sampled through merged.members; the root itself holds the Job ID.
        root_number=int(p.name.split('-')[1]);root=next(x for x in b['roots'] if x['id']==root_number)
        job_name='Local\\RetroLume.Activity.'+root['identity'].replace('-','')+'.G1'
        for member in row.get('owned_processes',[]):
            if member.get('pid') and isinstance(member.get('birth'),(int,str)):
                membership[(member['pid'],int(member['birth']))]=job_name;names[job_name]=p.name
jobs={}
for name,source in names.items():
    match=pattern.fullmatch(name);raw=match[1];identity='-'.join((raw[:8],raw[8:12],raw[12:16],raw[16:20],raw[20:]))
    try:job=NamedJob.open_existing(identity,int(match[2]))
    except JobOpenError as exc:
        jobs[name]={'job':name,'absent':exc.code==2,'unknown':exc.code!=2,'Windows_error':exc.code,'source':source}
    else:
        try:jobs[name]={'job':name,'active_processes':job.active_processes(),'source':source}
        finally:job.close()
pids=[];unresolved=[]
for (pid,stamp),source in sorted(registered.items()):
    observed=birth(pid);proof=None
    if observed.get('state')=='exited':proof='fresh explicit exited'
    elif observed.get('state')=='running' and int(observed.get('birth',0))!=stamp:proof='fresh different birth; old identity cannot revive'
    elif observed.get('state')=='unknown':
        job_name=command_jobs.get((pid,stamp)) or membership.get((pid,stamp));job=jobs.get(job_name,{})
        if job.get('absent') or job.get('active_processes')==0:proof='exact recorded Job membership plus fresh absent/empty named Job'
    item={'pid':pid,'registered_birth':stamp,'observation':observed,'proof':proof,'source':source}
    pids.append(item)
    if proof is None:unresolved.append(item)
ports={}
for name,port in b['ports'].items():
    with socket.socket() as probe:probe.settimeout(.3);ports[name]={'port':port,'listening':probe.connect_ex(('127.0.0.1',port))==0}
source=r.owned(r.container(),b['pg_registry']);target=target_identity(b['continuation06_restore_target'])
assert source['Id']=='b89522070d4b64fc67efed810852ccc21948058f154bf4fa1889f4d8d69a102f'
assert source['Image']=='sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f'
assert source['limits']['Memory']==536870912 and source['limits']['NanoCpus']==1000000000 and source['limits']['PidsLimit']==128
assert source['limits']['RestartPolicy']['Name']=='no'
complete=(not unresolved and not any(x.get('unknown') or x.get('active_processes',0) for x in jobs.values())
    and not any(x['listening'] for x in ports.values()) and not source['state']['Running'] and source['state']['Pid']==0
    and not target['running'] and target['Pid']==0)
historical=[]
for name in ('stop-history-resolution.json','stop-root22-job-resolution.json'):
    p=ROOT/'DocuN/evidence/TASK-121/audit/review-01'/name
    historical.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
proof={'utc':datetime.now(timezone.utc).isoformat(),'scope':'08 registered objects only; previous705 are not freshly reclassified',
    'registered_processes':pids,'registered_jobs':list(jobs.values()),'unresolved':unresolved,'ports':ports,
    'source_container':source,'restore_target':target,'08_stop_dimensions_confirmed':complete,
    'old079_unknown20_retained_with_review01_accepted_alternatives':historical,
    'current_metadata_command_own_receipt':'External close/tree_empty proof after this helper exits'}
(HERE/'final-stop-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'PID_births':len(pids),'Jobs':len(jobs),'unresolved':len(unresolved),'08_stop_dimensions_confirmed':complete}))
if not complete:raise RuntimeError('08 stop contains unresolved dimensions; retained explicitly')
