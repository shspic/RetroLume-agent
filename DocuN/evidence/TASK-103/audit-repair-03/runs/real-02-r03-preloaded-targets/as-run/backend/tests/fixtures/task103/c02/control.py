"""续作02固定截止与薄受控执行；原许可账只读。"""
from __future__ import annotations
import contextlib,hashlib,json,msvcrt,os,subprocess,time
from pathlib import Path
from datetime import datetime,timezone
from ..control import BudgetDenied,finite,redact,SECRET_VALUES,aggregate
ROOT=Path(__file__).resolve().parents[5]
EVIDENCE=ROOT/'DocuN/evidence/TASK-103/continuation-02'
PERMIT='TASK-103-G9-C02-20261007'
COUNTS={'offline':3,'build':1,'entry':3,'container_create':0,'volume_create':0,'role_create':0,'container_start':3,'listener_start':3,'sup':2,'browser':3,'driver':3}
LIMITS={'offline':600,'real':1200,'cleanup':300,'metadata':300}
def utc():return datetime.now(timezone.utc).isoformat()
def serial(value):
 if hasattr(value,'isoformat'):return value.isoformat()
 if type(value).__name__=='UUID':return str(value)
 raise TypeError('unserializable evidence type '+type(value).__name__)
def atomic_json(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 temporary=path.with_name(path.name+f'.{os.getpid()}.tmp')
 temporary.write_bytes(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False,default=serial).encode());os.replace(temporary,path)
class Control:
 def __init__(self):self.path=EVIDENCE/'session.json';self.receipt=EVIDENCE/'receipt.json';self.lock=self.path.with_suffix('.lock')
 @contextlib.contextmanager
 def locked(self):
  with self.lock.open('a+b') as f:
   f.seek(0,2)
   if f.tell()==0:f.write(b'\0');f.flush()
   f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_LOCK,1)
   try:yield
   finally:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
 def validate(self,data):
  receipt=json.loads(self.receipt.read_text(encoding='utf-8'))
  if data.get('permit')!=PERMIT or data.get('round')!='continuation-02':raise BudgetDenied('permit mismatch')
  for key in ['start_ns','deadline_ns']:
   if type(data.get(key)) is not int or data[key]!=receipt[key]:raise BudgetDenied('fixed clock changed')
  if data['deadline_ns']-data['start_ns']!=7200*10**9:raise BudgetDenied('active limit changed')
  if data.get('limits')!=LIMITS:raise BudgetDenied('limits changed')
  for key,maximum in COUNTS.items():
   value=data.get('counts',{}).get(key)
   if type(value) is not int or not 0<=value<=maximum:raise BudgetDenied('invalid counter')
  for key in LIMITS:finite(data.get('used_seconds',{}).get(key))
  return data
 def load(self):return self.validate(json.loads(self.path.read_text(encoding='utf-8')))
 def reserve(self,kind,detail=None):
  with self.locked():
   data=self.load()
   if data.get('closed') or time.monotonic_ns()>=data['deadline_ns']:raise BudgetDenied('permit closed/deadline')
   if kind not in COUNTS or data['counts'][kind]>=COUNTS[kind]:raise BudgetDenied('count exhausted')
   if kind=='entry' and data['used_seconds']['real']>=LIMITS['real']:raise BudgetDenied('real time exhausted')
   if kind=='sup' and not data.get('allow_sup_preparation'):raise BudgetDenied('默认SUP0，缺合法引用的条件尚未成立')
   data['counts'][kind]+=1;data['actions'].append({'kind':kind,'count':data['counts'][kind],'at':utc(),'ns':time.monotonic_ns(),'detail':detail or {}});atomic_json(self.path,data)
   return data['counts'][kind]
 def remaining(self,bucket,maximum):
  value=finite(maximum)
  if value<=0 or bucket not in LIMITS:raise BudgetDenied('invalid requested budget')
  data=self.load();deadline=data['deadline_ns']+(300*10**9 if bucket=='cleanup' else 0)
  result=min(value,LIMITS[bucket]-data['used_seconds'][bucket],(deadline-time.monotonic_ns())/1e9)
  if result<=0:raise BudgetDenied('time exhausted')
  return result
 def charge(self,bucket,seconds,detail):
  if bucket not in LIMITS:raise BudgetDenied('unknown bucket')
  value=finite(seconds)
  with self.locked():
   data=self.load();data['used_seconds'][bucket]+=value;data['actions'].append({'kind':'charge','bucket':bucket,'seconds':value,'at':utc(),'detail':detail});atomic_json(self.path,data)
 def record(self,detail):
  with self.locked():
   data=self.load();data['actions'].append({'kind':'observation','at':utc(),'detail':detail});atomic_json(self.path,data)
 def run(self,name,argv,bucket,maximum,count=None,cwd=None,env=None):
  reserved=self.reserve(count,{'name':name}) if count else None
  start=time.monotonic();folder=EVIDENCE/'runs'/name;folder.mkdir(parents=True,exist_ok=False)
  before=freeze(folder/'as-run');allowed=self.remaining(bucket,maximum)
  record={'name':name,'argv':[redact(str(x)) for x in argv],'cwd':str(cwd or ROOT),'at':utc(),'allowed_seconds':allowed,'before':before}
  if count=='entry':
   env=dict(env or os.environ);env.update(RETROLUME_TASK103_C02_ENTRY=str(reserved),RETROLUME_TASK103_C02_RUN=name)
  proc=subprocess.Popen(argv,cwd=cwd or ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
  try:stdout,stderr=proc.communicate(timeout=allowed)
  except subprocess.TimeoutExpired:
   proc.terminate();stdout,stderr=proc.communicate(timeout=10);record['timed_out']=True
  finally:self.charge(bucket,time.monotonic()-start,{'name':name})
  (folder/'stdout.txt').write_bytes(redact(stdout.decode('utf-8','replace')).encode());(folder/'stderr.txt').write_bytes(redact(stderr.decode('utf-8','replace')).encode())
  after=identities();record.update(exit_code=proc.returncode,ended_at=utc(),elapsed_seconds=time.monotonic()-start,after=after,bytes_unchanged=before==after,passed=proc.returncode==0 and not record.get('timed_out'))
  atomic_json(folder/'execution.json',record);return record
def require_entry():
 data=Control().load();name=os.environ.get('RETROLUME_TASK103_C02_RUN');number=os.environ.get('RETROLUME_TASK103_C02_ENTRY')
 if not name or number!=str(data['counts']['entry']) or not any(a['kind']=='entry' and a.get('detail',{}).get('name')==name and str(a.get('count'))==number for a in data['actions']):
  raise BudgetDenied('真实根必须经本轮driver动作前计数')
def identities():
 base=json.loads((EVIDENCE.parent/'continuation-02-input.json').read_text(encoding='utf-8'))['current_files']
 paths={ROOT/name for name in base}
 paths|=set((ROOT/'backend/tests/fixtures/task103/c02').rglob('*.py'))
 paths|=set((ROOT/'backend/tests').glob('test_task103_c02*'))
 paths|=set((ROOT/'frontend/tests').glob('task103-c02*'))
 paths|={p for p in (ROOT/'frontend/dist').rglob('*') if p.is_file()}
 result=[]
 for path in sorted(paths,key=str):
  if path.is_file():result.append({'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size})
 return result
def freeze(directory):
 rows=identities();base=json.loads((EVIDENCE.parent/'continuation-02-input.json').read_text(encoding='utf-8'))['current_files']
 for row in rows:
  if row['path'] in base and row['sha256']==base[row['path']]:
   preserved=EVIDENCE.parent/'continuation-01/final/post'/row['path']
   if not preserved.is_file() or hashlib.sha256(preserved.read_bytes()).hexdigest()!=row['sha256']:raise BudgetDenied('已存副本不匹配')
  else:
   out=Path(directory)/row['path'];out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes((ROOT/row['path']).read_bytes())
 atomic_json(Path(directory)/'identities.json',rows)
 atomic_json(Path(directory)/'inherited-post.json',{'path':str(EVIDENCE.parent/'continuation-01/final/post'),'baseline_count':len(base),'verified_current':True})
 return rows
