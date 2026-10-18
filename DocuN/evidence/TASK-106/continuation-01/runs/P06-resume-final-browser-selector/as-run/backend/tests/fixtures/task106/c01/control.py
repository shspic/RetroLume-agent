"""Independent bounded C01 counters; historical106 ledger is read-only."""
import contextlib,hashlib,json,msvcrt,os,shutil,time,traceback
from pathlib import Path

ROOT=Path(__file__).resolve().parents[5]
EVIDENCE=ROOT/'DocuN/evidence/TASK-106/continuation-01'
PERMIT='TASK-106-G10-C01-20261008'
SESSION=EVIDENCE/'session.json'
INPUT=ROOT/'DocuN/evidence/TASK-106/continuation-01-input.json'

def atomic_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+f'.{os.getpid()}.tmp');tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(tmp,path)

@contextlib.contextmanager
def locked():
    with (EVIDENCE/'session.lock').open('a+b') as f:
        if f.tell()==0:f.write(b'0');f.flush()
        f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_LOCK,1)
        try:
            s=json.loads(SESSION.read_text(encoding='utf-8'));assert s['permit']==PERMIT
            assert Path.cwd().resolve()==ROOT or ROOT in Path.cwd().resolve().parents
            yield s;atomic_json(SESSION,s)
        finally:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)

def reserve(kind,detail=None):
    with locked() as s:
        if time.perf_counter_ns()>=s['deadline_ns']:raise RuntimeError('C01 active deadline exhausted')
        if s['counts'][kind]>=s['count_limits'][kind]:raise RuntimeError('C01 counter exhausted: '+kind)
        s['counts'][kind]+=1;s['events'].append(dict(kind=kind,pid=os.getpid(),at_ns=time.perf_counter_ns(),detail=detail))

def charge(category,seconds,detail):
    with locked() as s:
        s['seconds'][category]+=seconds;s['events'].append(dict(kind='time',category=category,seconds=seconds,detail=detail))
        if s['seconds'][category]>s['second_limits'][category]:raise RuntimeError('C01 category exceeded: '+category)

def event(name,value):atomic_json(EVIDENCE/'observations'/f'{time.time_ns()}-{os.getpid()}-{name}.json',dict(kind=name,pid=os.getpid(),value=value))

def manifest():
    paths=set(json.loads(INPUT.read_text(encoding='utf-8'))['current_files'])
    paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'backend/tests/fixtures/task106/c01').rglob('*.py'))
    paths.add('frontend/tests/task106-continuation01.mjs')
    paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'frontend/dist').rglob('*') if p.is_file())
    return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(paths) if (ROOT/p).is_file()}

@contextlib.contextmanager
def batch(name,category='real',count='root',maximum=600):
    with locked() as s:
        if s['deadline_ns']-time.perf_counter_ns()<600_000_000_000:raise RuntimeError('C01 cleanup reserve unavailable')
        if s['second_limits'][category]-s['seconds'][category]<maximum:raise RuntimeError('C01 category reserve unavailable')
    reserve(count,dict(name=name,maximum=maximum));begun=time.perf_counter();out=EVIDENCE/'runs'/name;out.mkdir(parents=True,exist_ok=False)
    before=manifest();atomic_json(out/'pre-source.json',before)
    for rel in before:
        target=out/'as-run'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,target)
    record=dict(name=name,category=category,status='running',start_ns=time.perf_counter_ns(),pid=os.getpid(),permit=PERMIT,maximum=maximum)
    atomic_json(out/'run.json',record)
    try:yield out;record['status']='PASS'
    except BaseException as exc:
        record.update(status='FAIL',type=type(exc).__name__,message=str(exc));(out/'failure-stack.txt').write_text(traceback.format_exc(),encoding='utf-8')
        with locked() as s:s['failures'].append(dict(name=name,type=type(exc).__name__,message=str(exc)))
        raise
    finally:
        elapsed=time.perf_counter()-begun;record.update(elapsed_seconds=elapsed,end_ns=time.perf_counter_ns())
        if elapsed>maximum:record.update(status='FAIL',overrun=True)
        atomic_json(out/'run.json',record);atomic_json(out/'post-source.json',manifest());charge(category,elapsed,name)
