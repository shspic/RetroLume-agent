"""S07独立前向门，追加原工程账，绝不退回旧许可。"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,time,subprocess,os,sys
N=Path(__file__).resolve().parent;E=N.parent;ROOT=E.parents[3]
PERMIT='TASK-117-STEP018-AUDIT-REPAIR-S07-20261017'
def sample():return {'utc':datetime.now(timezone.utc).isoformat(),'mono_ns':time.monotonic_ns()}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def state():return json.loads((E/'budget.json').read_text(encoding='utf-8'))
def segment(b):
    if b['active_segment']!=PERMIT:raise RuntimeError('S07许可身份不符')
    return next(s for s in b['segments'] if s['permit']==PERMIT)
def guard():
    b=state();s=segment(b);now=time.monotonic_ns()
    if s['status']!='active':raise RuntimeError('S07未激活或已交回')
    if (now-s['start_mono_ns'])/1e9-s['paused_seconds']>=20400:raise RuntimeError('S07仅清场保存')
    if datetime.now(timezone.utc)>=datetime.fromisoformat(s['calendar_deadline_utc']):raise RuntimeError('S07日历门关闭')
    used=s['offline_process_run_seconds']
    if s['offline_process_run_active']:used+=(now-s['offline_process_run_active']['start_mono_ns'])/1e9
    if used>=3600:raise RuntimeError('S07离线进程门关闭')
    held=sum(x['seconds'] for x in b['runtime_intervals'] if x.get('segment')==PERMIT)
    if s.get('holding_start_mono_ns') is not None:held+=(now-s['holding_start_mono_ns'])/1e9
    if held>=3600:raise RuntimeError('S07运行持有门关闭')
    if b['active_root'] is not None:
        root=next(r for r in b['roots'] if r['id']==b['active_root'])
        if root.get('segment')!=PERMIT or now>=root['business_deadline_mono_ns']:raise RuntimeError('S07原根只允许清场')
    return b
def event(kind,**fields):
    with (E/'events.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps({'kind':kind,**sample(),**fields},ensure_ascii=False)+'\n')
def count(name,number=1):
    b=guard();s=segment(b)
    if type(number) is not int or number<1 or name not in s['cumulative_caps'] or b['counts'][name]+number>s['cumulative_caps'][name]:raise RuntimeError('S07次数门关闭 '+name)
    b['counts'][name]+=number;write(E/'budget.json',b);event('S07_attempt_reserved',counter=name,number=number,total=b['counts'][name])
def pre(relative,defect):
    guard();p=(ROOT/relative).resolve();p.relative_to(ROOT)
    if '.git' in p.parts or 'private' in p.parts:raise RuntimeError('非允许修改路径')
    index=N/'changes.json';rows=json.loads(index.read_text()) if index.exists() else {}
    if relative not in rows:
        raw=p.read_bytes() if p.exists() else b'';backup=N/'preimages'/relative;backup.parent.mkdir(parents=True,exist_ok=True)
        if p.exists():backup.write_bytes(raw)
        rows[relative]={'exists':p.exists(),'bytes':len(raw),'sha256':sha(raw) if p.exists() else None,'backup':str(backup.relative_to(ROOT)) if p.exists() else None,'D':defect,'sample':sample()};write(index,rows)
def failure(label,error):
    b=state();row={'label':label,'reason':str(error),**sample(),'segment':PERMIT};b['failures'].append(row);write(E/'budget.json',b);event('failure',**row)
def run(command,label,*,timeout=120,cwd=None):
    b=guard();s=segment(b)
    if s['offline_process_run_active'] is not None:raise RuntimeError('上一离线进程未结束')
    timeout=min(timeout,3600-s['offline_process_run_seconds'],20400-(time.monotonic_ns()-s['start_mono_ns'])/1e9)
    if timeout<=0:raise RuntimeError('离线进程无剩余额度')
    env=dict(os.environ);temp=N/'temp';temp.mkdir(exist_ok=True)
    env.update(TEMP=str(temp),TMP=str(temp),S07_EVIDENCE=str(N),PYTHONPATH=os.pathsep.join([str(ROOT/'backend'),str(ROOT/'backend/.venv/Lib/site-packages'),str(ROOT/'backend/tests')]))
    stamp=sample();s['offline_process_run_active']={'start_mono_ns':stamp['mono_ns'],'label':label,'timeout':timeout};write(E/'budget.json',b)
    try:
        result=subprocess.run(command,cwd=cwd or ROOT,env=env,capture_output=True,timeout=timeout,check=False)
        (N/(label+'.log')).write_bytes(result.stdout+result.stderr)
        if result.returncode:failure(label,'退出码'+str(result.returncode))
        return result
    except subprocess.TimeoutExpired as error:
        (N/(label+'.log')).write_bytes((error.stdout or b'')+(error.stderr or b''));failure(label,'实际进程超时');raise
    finally:
        end=sample();b=state();s=segment(b);seconds=(end['mono_ns']-stamp['mono_ns'])/1e9
        s['offline_process_run_seconds']+=seconds;s['offline_process_run_active']=None;write(E/'budget.json',b);event('S07_offline_process_end',label=label,seconds=seconds)
def py():return [sys._base_executable,'-X','utf8']
