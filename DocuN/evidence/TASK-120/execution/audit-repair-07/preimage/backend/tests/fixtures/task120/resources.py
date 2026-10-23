"""Exact TASK-120 resources, counters and cleanup; no legacy runner imports."""
from __future__ import annotations
import ctypes
from ctypes import wintypes
from contextlib import contextmanager
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import socket
import subprocess
import time
from uuid import uuid4
from app.data_exit.files import RootLease,private_file
from app.preview.process import birth
from .control_job import NamedJob

ROOT=Path(__file__).resolve().parents[4]
EVIDENCE=ROOT/'DocuN/evidence/TASK-120/execution'
PRIVATE=ROOT/'.runtime/TASK-120'
if os.environ.get('RETROLUME_TASK120_CONTINUATION')=='TASK-120-Q-PREP-CONTINUATION-06-20261020':
    PRIVATE=PRIVATE/'continuation-06'
BUDGET=EVIDENCE/'budget.json'
NAME='retrolume-task120-qprep-pg1'
VOLUME='retrolume-task120-qprep-data'
IMAGE='pgvector/pgvector@sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f'
LABELS={'retrolume.task':'TASK-120','retrolume.scope':'q-prep-testonly','retrolume.permit':'TASK-120-Q-PREP-IMPLEMENTATION-20261018'}


def utc():return datetime.now(timezone.utc).isoformat()


def write(path,value,private=False):
    path=Path(path);temp=path.with_suffix('.new')
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    if private:private_file(temp)
    # Concurrent readonly watchdog snapshots can briefly deny DELETE sharing
    # on Windows. Retry only the atomic rename, retaining the same bytes and
    # the caller's finite metadata lock; persistent ACL errors still fail.
    until=time.monotonic()+1
    while True:
        try:os.replace(temp,path);break
        except PermissionError:
            if time.monotonic()>=until:raise
            time.sleep(.01)


def state():return json.loads(BUDGET.read_text(encoding='utf-8-sig'))


def update(function):
    lock=RootLease(EVIDENCE,'.operation.lock')
    try:
        with lock.acquire(True,timeout=2):
            value=state();result=function(value);write(BUDGET,value);return result
    finally:lock.close()


def count(name):
    def reserve(value):
        if value['counts'][name]>=value['caps'][name]:raise RuntimeError('task120_count_exhausted_'+name)
        value['counts'][name]+=1
        return value['counts'][name]
    return update(reserve)


def event(kind,**details):
    with (EVIDENCE/'events.jsonl').open('a',encoding='utf-8') as stream:
        stream.write(json.dumps({'utc':utc(),'mono_ns':time.monotonic_ns(),'kind':kind,**details})+'\n')


class Memory(ctypes.Structure):
    _fields_=[('length',wintypes.DWORD),('load',wintypes.DWORD)]+[(name,ctypes.c_ulonglong) for name in ('total_phys','avail_phys','total_page','avail_page','total_virtual','avail_virtual','avail_extended')]


def available_memory():
    sample=Memory();sample.length=ctypes.sizeof(sample)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(sample)):raise ctypes.WinError()
    return int(sample.avail_phys)


def memory_gate(kind):
    amount=available_memory()
    prospective=state().get('current_permit_id') in ('TASK-120-Q-PREP-VALIDATION-04-20261019','TASK-120-Q-PREP-FINALIZATION-05-20261019','TASK-120-Q-PREP-CONTINUATION-06-20261020')
    minimum=(512 if prospective or kind!='browser' else 768)*1024**2
    event('memory_gate',stage=kind,available_bytes=amount,minimum_bytes=minimum)
    if amount<minimum:raise RuntimeError('task120_low_memory_'+kind)


def settled_memory_gate(kind,seconds=12):
    if state().get('current_permit_id') in ('TASK-120-Q-PREP-VALIDATION-04-20261019','TASK-120-Q-PREP-FINALIZATION-05-20261019','TASK-120-Q-PREP-CONTINUATION-06-20261020'):return memory_gate(kind)
    # Docker warmup can briefly reclaim pages. This finite internal stage does
    # not start the next layer until its unchanged real threshold is met.
    until=time.monotonic()+seconds
    while True:
        try:return memory_gate(kind)
        except RuntimeError:
            if time.monotonic()>=until:raise
            time.sleep(min(2,max(0,until-time.monotonic())))


def docker(args,*,timeout=25):
    executable=shutil.which('docker')
    if not executable:raise RuntimeError('docker_missing')
    result=subprocess.run([executable,*args],capture_output=True,timeout=timeout)
    if result.returncode:raise RuntimeError('docker_command_failed_'+str(result.returncode))
    return result.stdout.decode('utf-8').strip()


def container():
    # Full inspect remains only in memory. Env/command/config are never recorded.
    raw=json.loads(docker(['container','inspect',NAME]))[0]
    value={key:raw.get(key) for key in ('Id','Name','Image')}
    value.update(labels=raw['Config'].get('Labels',{}),state={k:raw['State'].get(k) for k in ('Running','Pid','Status')},
        ports=raw['HostConfig'].get('PortBindings'),mounts=[{k:m.get(k) for k in ('Type','Name','Destination')} for m in raw['Mounts']],
        limits={k:raw['HostConfig'].get(k) for k in ('Memory','NanoCpus','PidsLimit','RestartPolicy','Privileged','CapAdd','NetworkMode')})
    return value


def owned(value,registry=None):
    if any(value['labels'].get(k)!=v for k,v in LABELS.items()):raise RuntimeError('foreign_container_labels')
    if registry and (value['Id']!=registry['Id'] or value['Image']!=registry['Image']):raise RuntimeError('container_identity_changed')
    if not any(x['Type']=='volume' and x['Name']==VOLUME and x['Destination']=='/var/lib/postgresql/data' for x in value['mounts']):raise RuntimeError('container_mount_changed')
    return value


def choose_ports():
    saved=state().get('ports')
    if saved:return saved
    result=subprocess.run(['netsh','interface','ipv4','show','excludedportrange','protocol=tcp'],capture_output=True,timeout=10)
    if result.returncode:raise RuntimeError('port_exclusion_unknown')
    ranges=[]
    for line in result.stdout.decode('utf-8',errors='replace').splitlines():
        match=re.fullmatch(r'\s*(\d+)\s+(\d+)\s*\*?\s*',line)
        if match:ranges.append(tuple(map(int,match.groups())))
    choices={};checks=[]
    for kind,candidates in (('pg',range(55480,55484)),('api',range(18120,18124))):
        for port in candidates:
            if any(a<=port<=b for a,b in ranges):checks.append({'port':port,'excluded':True});continue
            try:
                with socket.socket() as probe:
                    probe.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1)
                    probe.bind(('127.0.0.1',port))
            except OSError as exc:checks.append({'port':port,'bind':False,'errno':exc.errno});continue
            choices[kind]=port;checks.append({'port':port,'bind':True});break
        if kind not in choices:raise RuntimeError('task120_no_authorized_port_'+kind)
    update(lambda value:value.update(ports=choices))
    write(EVIDENCE/'ports.json',{'selected':choices,'excluded_ranges':ranges,'actual_bind':checks,'utc':utc()})
    return choices


def ensure_pg():
    images=json.loads(docker(['image','inspect',IMAGE]))
    if len(images)!=1 or IMAGE not in images[0].get('RepoDigests',[]):raise RuntimeError('cached_image_digest_missing')
    image_id=images[0]['Id']
    write(EVIDENCE/'image.json',{'reference':IMAGE,'Id':image_id,'RepoDigests':images[0]['RepoDigests']})
    registry=state().get('pg_registry')
    if registry:
        return owned(container(),registry)
    existing=docker(['container','ls','-a','--filter','name=^/'+NAME+'$','--format','{{.ID}}'])
    if existing:
        value=owned(container())
        if value['Image']!=image_id:raise RuntimeError('existing_image_mismatch')
        update(lambda state:state.update(pg_registry=value))
        return value
    PRIVATE.mkdir(parents=True,exist_ok=True);private_file(PRIVATE,directory=True)
    credentials=PRIVATE/'cluster.json'
    if not credentials.exists():write(credentials,{'password':secrets.token_urlsafe(32)},private=True)
    password=json.loads(credentials.read_text(encoding='utf-8'))['password']
    env_file=PRIVATE/'pg.env'
    env_file.write_text('POSTGRES_USER=postgres\nPOSTGRES_DB=postgres\nPOSTGRES_PASSWORD='+password+'\n',encoding='utf-8')
    private_file(env_file)
    volumes=docker(['volume','ls','--filter','name=^'+VOLUME+'$','--format','{{.Name}}'])
    if not volumes:
        count('volume_create_attempts')
        docker(['volume','create',*[x for k,v in LABELS.items() for x in ('--label',k+'='+v)],VOLUME])
        count('volumes')
    volume=json.loads(docker(['volume','inspect',VOLUME]))[0]
    if any(volume.get('Labels',{}).get(k)!=v for k,v in LABELS.items()):raise RuntimeError('foreign_volume')
    ports=state()['ports'];count('pg_create_attempts')
    docker(['container','create','--pull=never','--name',NAME,'--cpus','1','--memory','512m','--pids-limit','128','--restart','no',
        *[x for k,v in LABELS.items() for x in ('--label',k+'='+v)],'--label','com.docker.compose.project=retrolume-task120-qprep',
        '--publish','127.0.0.1:'+str(ports['pg'])+':5432','--mount','type=volume,source='+VOLUME+',target=/var/lib/postgresql/data','--env-file',str(env_file),IMAGE])
    value=owned(container());count('pg_objects')
    if value['Image']!=image_id:raise RuntimeError('created_image_mismatch')
    update(lambda state:state.update(pg_registry=value))
    return value


def start_pg():
    registry=ensure_pg();value=owned(container(),registry)
    if value['state']['Running']:raise RuntimeError('previous_pg_still_running')
    memory_gate('pg');count('pg_starts')
    update(lambda state:state['roots'][-1].update(holding_started_ns=time.monotonic_ns()))
    docker(['container','start',registry['Id']])
    event('pg_started',Id=registry['Id'])


def stop_pg():
    registry=state().get('pg_registry')
    if registry is None:return {'created':False}
    value=owned(container(),registry)
    if value['state']['Running']:docker(['container','stop','--time','5',registry['Id']],timeout=15)
    value=owned(container(),registry)
    if value['state']['Running'] or value['state']['Pid']!=0:raise RuntimeError('pg_stop_unknown')
    return value


def public_environment():
    # Read only the finite OS variables needed to run local test processes.
    return {name:value for name in ('SYSTEMROOT','WINDIR','PATH','TEMP','TMP','USERPROFILE','LOCALAPPDATA','APPDATA','COMSPEC') if (value:=os.environ.get(name)) is not None}


def root_job(identity):
    # A test-controller Job is separate from the unchanged <=4-process native
    # business Job. Chromium needs more processes; no breakaway is allowed.
    from .control_job import _EXTENDED_LIMIT,JOB_OBJECT_EXTENDED_LIMIT_INFORMATION_CLASS,JOB_OBJECT_LIMIT_ACTIVE_PROCESS,JOB_OBJECT_LIMIT_JOB_MEMORY,JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    job=NamedJob.create(identity,1)
    limits=_EXTENDED_LIMIT();limits.BasicLimitInformation.LimitFlags=JOB_OBJECT_LIMIT_ACTIVE_PROCESS|JOB_OBJECT_LIMIT_JOB_MEMORY|JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    limits.BasicLimitInformation.ActiveProcessLimit=32;limits.JobMemoryLimit=1024**3
    if not job.api.SetInformationJobObject(job.handle,JOB_OBJECT_EXTENDED_LIMIT_INFORMATION_CLASS,ctypes.byref(limits),ctypes.sizeof(limits)):
        job.close();raise ctypes.WinError()
    return job
