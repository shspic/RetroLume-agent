"""Only exact registered PID/Job queries and loopback probes. Never starts/stops a service."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,socket,struct,sys
ROOT=Path(__file__).resolve().parents[5];sys.path.insert(0,str(ROOT/'backend'))
from tests.fixtures.task120.control_job import NamedJob,JobOpenError
from app.preview.process import birth
HERE=Path(__file__).resolve().parent;EX=HERE.parent
budget=json.loads((EX/'budget.json').read_text(encoding='utf-8'))
registered={};job_names={};problems=[]
pattern=re.compile(r'Local\\RetroLume\.Activity\.([0-9a-f]{32})\.G([1-9][0-9]*)\Z')
def collect(value,source):
    if isinstance(value,dict):
        for key,bkeys in [('pid',('birth','birth_100ns','created_100ns')),('manager_pid',('manager_created_100ns',)),('worker_pid',('worker_created_100ns',))]:
            pid=value.get(key);stamp=next((value.get(k) for k in bkeys if value.get(k)),None)
            if type(pid) is int and pid>0 and isinstance(stamp,(int,str)):
                registered[(pid,int(stamp))]=source
        for item in value.values():collect(item,source)
    elif isinstance(value,list):
        for item in value:collect(item,source)
    elif isinstance(value,str) and pattern.fullmatch(value):job_names[value]=source
collect(budget['roots'],'sole-runtime-ledger')
for path in [*EX.glob('command-*.receipt.json'),*(EX/'continuation-01').glob('command-*.receipt.json'),*HERE.glob('command-*.receipt.json')]:
    collect(json.loads(path.read_text(encoding='utf-8')),path.relative_to(EX).as_posix())
for line in (EX/'events.jsonl').read_text(encoding='utf-8').splitlines():
    if line.strip():collect(json.loads(line),'sole-events-log')
# Read only these two registered private control files. The committed frame
# checksum and chain are checked for metadata extraction, never as a new Q root.
canonical=lambda value:json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
for slot in ('flow','budget-01','budget-02'):
    path=ROOT/'.runtime/TASK-120'/slot/'control/journal.bin'
    if not path.exists():continue
    previous='0'*64;seq=0
    with path.open('rb') as stream:
        while header:=stream.read(4):
            if len(header)!=4:problems.append(slot+':incomplete_header');break
            size=struct.unpack('!I',header)[0]
            if not 1<=size<=65536:problems.append(slot+':frame_length');break
            raw=stream.read(size);tail=stream.read(73)
            if len(raw)!=size or tail!=b'\nCOMMIT:'+hashlib.sha256(raw).hexdigest().encode()+b'\n':problems.append(slot+':frame_commit');break
            event=json.loads(raw);seq+=1
            if event['seq']!=seq or event['prev_hash']!=previous or event['body_hash']!=hashlib.sha256(canonical(event['payload']).encode()).hexdigest():problems.append(slot+':frame_chain');break
            previous=hashlib.sha256(raw).hexdigest()
            if event['kind'] in ('owned.begin','owned.end'):collect(event['payload'],slot+':committed-owned-metadata')
pids=[]
for (pid,stamp),source in sorted(registered.items()):
    observed=birth(pid);same=observed.get('state')=='running' and int(observed.get('birth',0))==stamp
    pids.append({'pid':pid,'registered_birth':stamp,'same_identity_running':same,'observation':observed,'source':source})
jobs=[]
for name,source in sorted(job_names.items()):
    match=pattern.fullmatch(name);identity=match[1];identity='-'.join((identity[:8],identity[8:12],identity[12:16],identity[16:20],identity[20:]))
    try:job=NamedJob.open_existing(identity,int(match[2]))
    except JobOpenError as exc:
        if exc.code==2:jobs.append({'job':name,'absent':True,'active_processes':0,'source':source})
        else:jobs.append({'job':name,'unknown':True,'Windows_error':exc.code,'source':source})
    else:
        try:jobs.append({'job':name,'active_processes':job.active_processes(),'source':source})
        finally:job.close()
ports={}
for kind,port in budget['ports'].items():
    with socket.socket() as probe:
        probe.settimeout(.3);ports[kind]={'port':port,'listening':probe.connect_ex(('127.0.0.1',port))==0}
from tests.fixtures.task120 import resources as r
actual=r.owned(r.container(),budget['pg_registry'])
assert actual['Id']=='b89522070d4b64fc67efed810852ccc21948058f154bf4fa1889f4d8d69a102f'
assert actual['Image']=='sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f'
assert actual['limits']['Memory']==536870912 and actual['limits']['NanoCpus']==1000000000 and actual['limits']['PidsLimit']==128
assert actual['limits']['RestartPolicy']['Name']=='no' and len(actual['mounts'])==1
assert actual['ports']=={'5432/tcp':[{'HostIp':'127.0.0.1','HostPort':'55480'}]}
stopped=not problems and not any(x['same_identity_running'] for x in pids) and not any(x.get('unknown') or x.get('active_processes',0) for x in jobs) and not any(x['listening'] for x in ports.values())
complete=stopped and not actual['state']['Running'] and actual['state']['Pid']==0
proof={'utc':datetime.now(timezone.utc).isoformat(),'kind':'normal_channel_readonly_exact_stop_inspection','registered_processes':pids,'registered_jobs':jobs,'ports':ports,'metadata_read_problems':problems,'processes_jobs_ports_stopped':stopped,'docker_realtime':actual,'all_fresh_stop_dimensions_confirmed':complete,'root_count':budget['counts']['roots'],'old_command038_not_executed':not (EX/'continuation-01/command-038.receipt.json').exists()}
(HERE/'entry-stop-proof.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
if not complete:raise RuntimeError('exact_stop_or_identity_not_confirmed')
print(json.dumps({'PID_births':len(pids),'Jobs':len(jobs),'all_fresh_stop_dimensions_confirmed':complete}))
