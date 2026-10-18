"""复用真实三项及已有提交，只补本轮同进程尾项与最终PG核对。"""
import hashlib,json,os,secrets,subprocess,sys,time,urllib.request
from urllib.parse import quote
import psycopg
from psycopg import sql
from .control import Control,EVIDENCE,ROOT,atomic_json,redact,SECRET_VALUES,require_entry
from .resources import OwnedDocker,port_available
from ..processes import process_state,stop_owned
from ..migration_cleanup import snapshot,catalog
from ..windows_normal import config
def run():
 c=Control();require_entry();docker=OwnedDocker(c);resource=next(r for r in c.load()['resources'] if r['slot']==1)
 out=EVIDENCE/'tail';out.mkdir();server=None;sw=None;node=None;nw=None;report={'status':'FAIL','executed':True,'inherited_root':'real-02-permit-corrected-composite'}
 try:
  assert port_available(18103) and port_available(55443);assert all(not docker.inspect(r)['running'] for r in c.load()['resources'])
  docker.start(resource);admin=docker.admin_dsn(resource);limit=time.monotonic()+20
  while True:
   try:
    with psycopg.connect(admin,connect_timeout=2) as conn:conn.execute('SELECT 1')
    break
   except psycopg.Error:
    if time.monotonic()>limit:raise
    time.sleep(.05)
  password=secrets.token_urlsafe(32);SECRET_VALUES.add(password)
  with psycopg.connect(admin,autocommit=True) as conn:
   before=snapshot(conn);cat=catalog(conn);atomic_json(out/'pg-before.json',before);atomic_json(out/'catalog-before.json',cat)
   conn.execute(sql.SQL('ALTER ROLE retrolume_task103_app PASSWORD {}').format(sql.Literal(password)))
  atomic_json(out/'role-password-action.json',{'role':'retrolume_task103_app','old_services_stopped':True,'password_ram_only':True,'create_roles':0})
  dsn=f"postgresql://retrolume_task103_app:{quote(password,safe='')}@127.0.0.1:55443/{resource['database']}"
  work=EVIDENCE/'workspace/tail';originals=work/'data/originals';originals.mkdir(parents=True);backup=work/'backup';backup.mkdir()
  for file in (EVIDENCE.parent/'continuation-01/workspace/data/originals').iterdir():
   if file.is_file():
    body=file.read_bytes();assert hashlib.sha256(body).hexdigest()==file.name;(originals/file.name).write_bytes(body)
  cfg=work/'activity-config.json';atomic_json(cfg,config());key=secrets.token_urlsafe(24);SECRET_VALUES.add(key)
  os.environ.update(RETROLUME_DATA_DIR=str(work/'data'),RETROLUME_BACKUP_DIR=str(backup),RETROLUME_DATABASE_URL=dsn,RETROLUME_ACTIVITY_CONFIG=str(cfg),RETROLUME_TASK103_SYNTHETIC_KEY=key,RETROLUME_TASK103_C02_RESUME_TAIL='true')
  c.reserve('listener_start',{'module':'tests.fixtures.task103.c02.server','port':18103});server=subprocess.Popen([sys.executable,'-X','utf8','-B','-m','tests.fixtures.task103.c02.server'],cwd=ROOT/'backend',env=os.environ.copy(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
  sw={**process_state(server.pid),'module':'tests.fixtures.task103.c02.server'};report['server_witness']=sw
  limit=time.monotonic()+20
  while True:
   try:
    with urllib.request.urlopen('http://127.0.0.1:18103/health',timeout=1) as r:
     if r.status==200:break
   except Exception:
    if time.monotonic()>limit:raise
    time.sleep(.05)
  with urllib.request.urlopen('http://127.0.0.1:18103/api/session',timeout=3) as r:token=json.load(r)['token'];SECRET_VALUES.add(token)
  def get(path):
   with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:18103'+path,headers={'X-RetroLume-Session':token,'Origin':'http://127.0.0.1:18103'}),timeout=10) as r:assert r.status==200;return json.load(r)
  target=json.loads((EVIDENCE/'browser-target.json').read_text('utf-8'));cite=get(target['citation_path']);assert cite['citation']['text']
  old=json.loads((EVIDENCE/'browser/result.json').read_text('utf-8'));assert len(old['cases'])==2
  pending=next(x['payload'] for x in old['network'] if x['event']=='request' and x.get('payload',{}).get('body',{}).get('title','').startswith('C02晚保存切换'))
  receipt=get('/api/memories/commands/'+pending['business_key']);assert receipt['status']=='committed'
  atomic_json(out/'old-pending-readonly-confirmation.json',{'request':pending,'receipt':receipt,'new_post':0,'cause':'上轮选择器失败时真实COMMIT已发生，客户端未收到；本轮仅GET，不重发'})
  noev=json.loads((EVIDENCE/'no-evidence-http.json').read_text('utf-8'))
  with psycopg.connect(admin,autocommit=True) as conn:
   for table,rows in noev['after'].items():
    column='id' if table=='activities' else 'activity_id';actual=conn.execute(sql.SQL("SELECT COALESCE(jsonb_agg(to_jsonb(t)),'[]'::jsonb) FROM public.{} t WHERE {}=%s").format(sql.Identifier(table),sql.Identifier(column)),(noev['activity_id'],)).fetchone()[0];assert actual==rows
  report['no_evidence_inherited_verified']=True;c.reserve('driver',{'script':'frontend/tests/task103-c02-browser.cjs'});c.reserve('browser',{'profile':'workspace/browser-profile-02'})
  script=ROOT/'frontend/tests/task103-c02-browser.cjs';node=subprocess.Popen(['node',str(script)],cwd=ROOT/'frontend',env=os.environ.copy(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
  nw={**process_state(node.pid),'module':str(script)};report['driver_witness']=nw;stdout,stderr=node.communicate(timeout=c.remaining('real',450))
  (out/'browser-stdout.txt').write_bytes(redact(stdout.decode('utf-8','replace')).encode());(out/'browser-stderr.txt').write_bytes(redact(stderr.decode('utf-8','replace')).encode())
  browser=json.loads((EVIDENCE/'browser-02/result.json').read_text('utf-8'));report['browser']=browser;report['driver_exit_code']=node.returncode;assert node.returncode==0 and browser['status']=='PASS',browser.get('error')
  with psycopg.connect(admin,autocommit=True) as conn:
   final=snapshot(conn);assert catalog(conn)==cat;assert all(row in final[name] for name,rows in before.items() for row in rows)
   atomic_json(out/'pg-after.json',final);proof=[]
   for case in browser['cases']:
    if 'memory_id' not in case:continue
    mid=case['memory_id'];head=conn.execute('SELECT revision,current_version,state FROM learning_memories WHERE memory_id=%s',(mid,)).fetchone()
    expected=2 if case['name']=='V15 双页真实陈旧POST' else 1;assert head==(expected,expected,'active')
    rows=conn.execute('SELECT business_key,effect_applied,request_sha256 FROM learning_memory_commands WHERE memory_id=%s ORDER BY committed_at',(mid,)).fetchall();assert sum(1 for r in rows if r[1])==expected
    if case.get('stale_key'):assert not any(str(r[0])==case['stale_key'] for r in rows)
    if case.get('business_key'):assert any(str(r[0])==case['business_key'] and r[1] and r[2]==case['receipt']['request_sha256'] for r in rows)
    proof.append({'case':case['name'],'memory_id':mid,'head':head,'receipts':rows,'effects':expected})
   assert conn.execute('SELECT count(*) FROM learning_memory_commands WHERE business_key=%s',(pending['business_key'],)).fetchone()[0]==1
  atomic_json(out/'memory-db-proof.json',proof);assert c.load()['counts']['sup']==0;report['status']='PASS'
 except BaseException as exc:
  report.update(error_type=type(exc).__name__,message=redact(str(exc)));(out/'error.txt').write_bytes(redact(__import__('traceback').format_exc()).encode())
 finally:
  start=time.monotonic()
  for proc,witness,label in [(node,nw,'driver'),(server,sw,'server')]:
   if proc and witness:
    try:
     report[label+'_stop']=stop_owned(proc,witness);a,b=proc.communicate(timeout=5)
     if label=='server':(out/'server-stdout.txt').write_bytes(redact(a.decode('utf-8','replace')).encode());(out/'server-stderr.txt').write_bytes(redact(b.decode('utf-8','replace')).encode())
    except BaseException as exc:report[label+'_stop_unconfirmed']=type(exc).__name__;report['status']='FAIL'
  try:report['container_stop']=docker.stop(resource)
  except BaseException as exc:report['container_stop_unconfirmed']=type(exc).__name__;report['status']='FAIL'
  report['ports_released']={str(p):port_available(p) for p in [18103,55443]};c.charge('cleanup',time.monotonic()-start,{'name':'tail'});atomic_json(out/'result.json',report)
 print(json.dumps({'status':report['status'],'error':report.get('message')},ensure_ascii=False));return 0 if report['status']=='PASS' else 1
if __name__=='__main__':sys.exit(run())
