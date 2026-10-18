"""续作许可/累计资源上界；不重置初轮事实。"""
import json, hashlib, os, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
E=ROOT/'DocuN/evidence/TASK-097'; C=E/'continuation-01'
sys.path.insert(0,str(E))
from artifacts import write, digest, files, stamp, append_event, PY

def permit():
    p=json.loads((C/'permit.json').read_text(encoding='utf-8'))
    assert p['permit']=='continuation-01' and p['task']=='TASK-097'
    assert digest(ROOT/'DocuN/tasks/TASK-097.md')==p['card_sha256'],'当前许可已变化'
    assert time.time()-p['active_started_epoch']<10800,'续作主动3小时已达上限'
    assert p['baseline']['active_seconds']+time.time()-p['active_started_epoch']<28800
    return p

def ledger(): return json.loads((E/'attempt-ledger.json').read_text(encoding='utf-8'))
def added(category): return [x for x in ledger() if x.get('permit')=='continuation-01' and x.get('category')==category]
def events(category): return [x for x in ledger() if x.get('category')==category]
def event(v): append_event({'permit':'continuation-01',**v})

def start_guard(kind):
    permit()
    ends=events('integration_end')
    assert all(x['cleanup_ok'] for x in ends),'旧或新清理失败，停止新启动'
    if kind=='entry': assert len(events('integration_entry'))<12 and len(added('integration_entry'))<4
    if kind=='start': assert len(events('container_start'))<12 and len(added('container_start'))<4
    assert sum(x.get('business_seconds',0) for x in added('integration_end'))<1200
    assert sum(x.get('business_seconds',0) for x in ends)<3600
    assert sum(x.get('cleanup_seconds',0) for x in added('integration_end'))<240
    assert sum(x.get('cleanup_seconds',0) for x in ends)<600

def launch_guard(kind):
    permit()
    pattern={'sup':'sup-launch-*.json','driver':'browser-launch.json','browser':'browser-actual-start.json'}[kind]
    paths=list(E.glob('integration-*/'+pattern))
    new=[p for p in paths if json.loads(p.read_text(encoding='utf-8')).get('permit')=='continuation-01']
    totalmax={'sup':23,'driver':7,'browser':6}[kind];addmax={'sup':8,'driver':3,'browser':3}[kind]
    assert len(paths)<totalmax and len(new)<addmax,(kind,len(paths),len(new))
    return len(paths)+1

def freeze(label,command,expected):
    import shutil
    target=C/'as-run'/label
    assert not target.exists(),'不可覆盖as-run'
    rows=[]
    for src in files():
        rel=src.relative_to(ROOT);dst=target/'files'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
        rows.append({'path':rel.as_posix(),'sha256':digest(src),'bytes':src.stat().st_size})
    write(target/'manifest.json',{'at':stamp(),'command':command,'expected':expected,'files':rows})
    return target

def offline(label,cmd):
    permit()
    used=sum(x.get('seconds',0) for x in added('offline'))
    assert used<600
    out=freeze(label,cmd,'定向离线：无PG/监督/浏览器启动；单批<=60秒')
    start=time.monotonic();code=1;error=None
    try:
        r=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=min(60,600-used),env={**os.environ,'PYTHONIOENCODING':'utf-8','RETROLUME_TASK097_PREFLIGHT':'1'})
        (out/'stdout.bin').write_bytes(r.stdout);(out/'stderr.bin').write_bytes(r.stderr);code=r.returncode
        print(r.stdout.decode('utf-8','replace'));print(r.stderr.decode('utf-8','replace'))
    except subprocess.TimeoutExpired as exc:
        error='TimeoutExpired';(out/'stdout.bin').write_bytes(exc.stdout or b'');(out/'stderr.bin').write_bytes(exc.stderr or b'')
    finally:
        elapsed=time.monotonic()-start
        fact={'category':'offline','label':label,'seconds':elapsed,'exit_code':code,'error':error}
        write(out/'run.json',{**fact,'post_hashes':{p.relative_to(ROOT).as_posix():digest(p) for p in files()}});event(fact)
        print(json.dumps(fact))
    return code

if __name__=='__main__':raise SystemExit(offline(sys.argv[1],sys.argv[2:]))
