"""Finite TASK106 accounting, shared by its runners and transparent observers."""
from __future__ import annotations
import contextlib,hashlib,json,os,time,traceback
from pathlib import Path
import msvcrt

ROOT=Path(__file__).resolve().parents[4]
EVIDENCE=ROOT/'DocuN'/'evidence'/'TASK-106'
PERMIT='TASK-106-G10-20261008'
SESSION=EVIDENCE/'session.json'


def atomic_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+f'.{os.getpid()}.tmp')
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    os.replace(temp,path)


@contextlib.contextmanager
def locked():
    EVIDENCE.mkdir(parents=True,exist_ok=True)
    with (EVIDENCE/'session.lock').open('a+b') as f:
        if f.tell()==0:f.write(b'0');f.flush()
        f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_LOCK,1)
        try:
            state=json.loads(SESSION.read_text(encoding='utf-8'))
            if state['permit']!=PERMIT or Path.cwd().resolve()!=ROOT and ROOT not in Path.cwd().resolve().parents:
                raise RuntimeError('TASK106 permit/root mismatch')
            yield state
            atomic_json(SESSION,state)
        finally:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)


def reserve(kind,detail=None,n=1):
    with locked() as s:
        if time.perf_counter_ns()>=s['deadline_ns']:raise RuntimeError('TASK106 active deadline')
        if s['counts'][kind]+n>s['limits_counts'][kind]:raise RuntimeError('TASK106 count exhausted: '+kind)
        s['counts'][kind]+=n
        s['events'].append(dict(kind=kind,at_ns=time.perf_counter_ns(),pid=os.getpid(),detail=detail))


def charge(kind,seconds,detail=None):
    with locked() as s:
        s['used_seconds'][kind]+=seconds
        s['events'].append(dict(kind='time',category=kind,seconds=seconds,detail=detail))
        if s['used_seconds'][kind]>s['limits_seconds'][kind]:
            s['failures'].append(dict(kind='budget_overrun',category=kind,seconds=s['used_seconds'][kind]))


def source_manifest():
    spec=json.loads((EVIDENCE/'implementation-map.json').read_text(encoding='utf-8'))
    files=spec['new_backend']+spec['new_frontend']+spec['modified']
    files += [p.relative_to(ROOT).as_posix() for p in (ROOT/'backend/tests/fixtures/task106').rglob('*.py')]
    files += [p.relative_to(ROOT).as_posix() for p in (ROOT/'backend/tests').glob('test_interview_*.py')]
    files += ['frontend/tests/task106-interview.mjs']
    files += [p.relative_to(ROOT).as_posix() for p in (ROOT/'frontend/dist').rglob('*') if p.is_file()]
    return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(set(files)) if (ROOT/p).is_file()}


@contextlib.contextmanager
def batch(name,category='real',count='root',maximum=900):
    with locked() as s:
        if s['deadline_ns']-time.perf_counter_ns()<900_000_000_000:raise RuntimeError('cleanup reserve unavailable')
        if s['limits_seconds'][category]-s['used_seconds'][category]<maximum:raise RuntimeError('category reserve unavailable')
    reserve(count,dict(name=name,maximum=maximum))
    start=time.perf_counter();folder=EVIDENCE/'runs'/name
    folder.mkdir(parents=True,exist_ok=False);atomic_json(folder/'pre-source.json',source_manifest())
    import shutil
    for relative in source_manifest():
        target=folder/'as-run'/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/relative,target)
    record=dict(name=name,category=category,pid=os.getpid(),start_ns=time.perf_counter_ns(),permit=PERMIT,status='running')
    atomic_json(folder/'run.json',record)
    try:
        yield folder
        record['status']='PASS'
    except BaseException as exc:
        record['status']='FAIL';record['exception_type']=type(exc).__name__;record['message']=str(exc)
        # DSNs/passwords never passed as exception text by this controller.
        (folder/'failure-stack.txt').write_text(traceback.format_exc(),encoding='utf-8')
        with locked() as s:s['failures'].append(dict(kind='batch',name=name,type=type(exc).__name__,message=str(exc)))
        raise
    finally:
        elapsed=time.perf_counter()-start;record['elapsed_seconds']=elapsed;record['end_ns']=time.perf_counter_ns()
        if elapsed>maximum:record['status']='FAIL';record['overrun']=True
        atomic_json(folder/'run.json',record);atomic_json(folder/'post-source.json',source_manifest());charge(category,elapsed,name)


def event(name,value):
    atomic_json(EVIDENCE/'observations'/f'{time.time_ns()}-{os.getpid()}-{name}.json',dict(kind=name,pid=os.getpid(),value=value))
