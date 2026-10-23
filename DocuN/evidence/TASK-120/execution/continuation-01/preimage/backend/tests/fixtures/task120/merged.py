"""Finite TASK120 subbatches inside one already-owned, bounded PG lifecycle."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from . import resources as r
from app.worker.windows_job import NamedJob


def members(job):
    import ctypes
    from ctypes import wintypes
    from app.preview.process import birth
    class Pids(ctypes.Structure):
        _fields_=[('assigned',wintypes.DWORD),('listed',wintypes.DWORD),('pids',ctypes.c_size_t*64)]
    value=Pids()
    if not job.api.QueryInformationJobObject(job.handle,3,ctypes.byref(value),ctypes.sizeof(value),None):raise ctypes.WinError()
    if value.assigned!=value.listed or value.listed>32:raise RuntimeError('subbatch_members_unknown')
    result=[]
    for pid in list(value.pids)[:value.listed]:
        identity=birth(pid)
        if identity.get('state')!='running':raise RuntimeError('subbatch_member_birth_unknown')
        result.append({'pid':pid,'birth':identity['birth']})
    return sorted(result,key=lambda row:row['pid'])


def await_members(job,baseline,seconds=2):
    until=time.monotonic()+seconds
    while True:
        current=members(job)
        if current==baseline:return current
        if time.monotonic()>=until:raise RuntimeError('subbatch_descendants_not_stopped')
        time.sleep(.02)


def validate(value,ordinal,previous):
    if (set(value)!={'ordinal','phase','seconds','previous_exit'} or value['ordinal']!=ordinal
        or value['phase'] not in ('flow','budget','ui','reopen','stop') or type(value['seconds']) is not int
        or not 1<=value['seconds']<=300 or value['previous_exit']!=previous):raise ValueError('task120_closed_subbatch')
    return value


def await_request(path,until):
    while not path.exists():
        if time.monotonic()>=until:return None
        time.sleep(min(.1,max(0,until-time.monotonic())))
    return json.loads(path.read_text(encoding='utf-8'))


def run_batches():
    root=r.state()['active_root'];slot=next(x for x in r.state()['roots'] if x['id']==root)
    previous=None
    folder=r.PRIVATE/f'root-{root:02d}';folder.mkdir(exist_ok=True)
    job=NamedJob.open_existing(slot['identity'],1)
    try:baseline=members(job)
    finally:job.close()
    r.event('merged_manager_members',root=root,members=baseline)
    for ordinal in range(1,9):
        request=folder/f'batch-{ordinal:02d}.json'
        until=min(time.monotonic()+60,slot['business_deadline_ns']/1e9-5)
        r.event('awaiting_explicit_task120_subbatch',root=root,ordinal=ordinal,until_mono=until)
        value=await_request(request,until)
        if value is None:return previous or 0
        value=validate(value,ordinal,previous)
        if value['phase']=='stop':return previous or 0
        env=r.public_environment()
        env.update({name:os.environ[name] for name in ('PYTHONPATH','PYTHONIOENCODING','RETROLUME_TASK120_ROOT_ID','RETROLUME_TASK120_TESTONLY')})
        env['RETROLUME_TASK120_BATCH']=str(ordinal)
        files=[]
        for directory in ('backend/app','backend/tests/fixtures/task120','frontend/src','frontend/dist'):
            for path in sorted((r.ROOT/directory).rglob('*')):
                if path.is_file() and '__pycache__' not in path.parts:files.append({'path':path.relative_to(r.ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        stem=f'root-{root:02d}-batch-{ordinal:02d}'
        r.write(r.EVIDENCE/(stem+'-as-run.json'),{'files':files,'utc':r.utc(),'request':value})
        start=time.monotonic()
        result=subprocess.run([sys.executable,'-m','tests.fixtures.task120.run',value['phase']],cwd=r.ROOT/'backend',env=env,
            timeout=min(value['seconds'],max(1,slot['business_deadline_ns']/1e9-time.monotonic()-3)))
        previous=result.returncode
        job=NamedJob.open_existing(slot['identity'],1)
        try:
            await_members(job,baseline)
        finally:job.close()
        r.write(r.EVIDENCE/(stem+'-receipt.json'),{'phase':value['phase'],'exit_code':previous,'wall_seconds':time.monotonic()-start,'descendants_stopped':True,'utc':r.utc()})
        if previous:r.update(lambda state:state['failures'].append({'root':root,'batch':ordinal,'phase':value['phase'],'receipt':stem+'-receipt.json'}))
    return previous or 0


if __name__=='__main__':
    job=NamedJob.open_existing(sys.argv[1],1)
    try:
        before=members(job);subprocess.run([sys.executable,'-c','pass'],check=True,timeout=3)
        after=await_members(job,before)
        print(json.dumps({'before':before,'after':after,'exact_members_restored':before==after}))
    finally:job.close()
