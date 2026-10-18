"""修复回归与引用的唯一新根，真正API/PG，模型及教学0。"""
import hashlib,json,os,secrets,subprocess,sys,time,urllib.request,urllib.error
from urllib.parse import quote
import psycopg
from psycopg import sql
from .control import Control,EVIDENCE,ROOT,atomic_json,redact,SECRET_VALUES,require_entry
from .resources import OwnedDocker,port_available
from ..processes import process_state,stop_owned
from ..migration_cleanup import snapshot,catalog,digest
from ..windows_normal import config
def run():
 c=Control();require_entry();name=os.environ['RETROLUME_TASK103_R03_RUN'];out=EVIDENCE/'groups'/name;out.mkdir(parents=True)
 docker=OwnedDocker(c);resource=next(r for r in c.load()['resources'] if r['slot']==1);server=None;sw=None;node=None;nw=None;report={'status':'FAIL','executed':True}
 try:
  assert port_available(18103) and port_available(55443);assert all(not docker.inspect(r)['running'] for r in c.load()['resources'])
  docker.start(resource);admin=docker.admin_dsn(resource);end=time.monotonic()+20
  while True:
   try:
    with psycopg.connect(admin,connect_timeout=2) as conn:conn.execute('SELECT 1')
    break
   except psycopg.Error:
    if time.monotonic()>end:raise
    time.sleep(.05)
  password=secrets.token_urlsafe(32);SECRET_VALUES.add(password);c.reserve('password_reset',{'role':'retrolume_task103_app','old_services_stopped':True})
  with psycopg.connect(admin,autocommit=True) as conn:
   before=snapshot(conn);initial=catalog(conn);atomic_json(out/'pg-before.json',before);atomic_json(out/'catalog-before.json',initial)
   conn.execute(sql.SQL('ALTER ROLE retrolume_task103_app PASSWORD {}').format(sql.Literal(password)))
  dsn=f"postgresql://retrolume_task103_app:{quote(password,safe='')}@127.0.0.1:55443/{resource['database']}"
  work=EVIDENCE/'workspace'/name;originals=work/'data/originals';originals.mkdir(parents=True);backup=work/'backup';backup.mkdir()
  copied=[]
  for file in (EVIDENCE.parent/'continuation-01/workspace/data/originals').iterdir():
   if file.is_file():
    raw=file.read_bytes();assert hashlib.sha256(raw).hexdigest()==file.name;(originals/file.name).write_bytes(raw);copied.append({'sha256':file.name,'bytes':len(raw)})
  atomic_json(out/'original-copy-readonly.json',copied);cfg=work/'activity-config.json';atomic_json(cfg,config());key=secrets.token_urlsafe(24);SECRET_VALUES.add(key)
  os.environ.update(RETROLUME_DATA_DIR=str(work/'data'),RETROLUME_BACKUP_DIR=str(backup),RETROLUME_DATABASE_URL=dsn,RETROLUME_ACTIVITY_CONFIG=str(cfg),RETROLUME_TASK103_SYNTHETIC_KEY=key,RETROLUME_TASK103_R03_GROUP=name)
  c.reserve('listener_start',{'module':'tests.fixtures.task103.r03.server','port':18103});server=subprocess.Popen([sys.executable,'-X','utf8','-B','-m','tests.fixtures.task103.r03.server'],cwd=ROOT/'backend',env=os.environ.copy(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
  sw={**process_state(server.pid),'module':'tests.fixtures.task103.r03.server'};report['server_witness']=sw;end=time.monotonic()+20
  while True:
   try:
    with urllib.request.urlopen('http://127.0.0.1:18103/health',timeout=1) as r:
     if r.status==200:break
   except Exception:
    if time.monotonic()>end:raise
    time.sleep(.05)
  # Native bootstrap不附Origin；实际受保护请求使用同源Origin及会话。
  with urllib.request.urlopen('http://127.0.0.1:18103/api/session',timeout=3) as r:token=json.load(r)['token'];SECRET_VALUES.add(token)
  def get(path):
   req=urllib.request.Request('http://127.0.0.1:18103'+path,headers={'X-RetroLume-Session':token,'Origin':'http://127.0.0.1:18103'})
   try:
    with urllib.request.urlopen(req,timeout=10) as r:return r.status,json.load(r)
   except urllib.error.HTTPError as exc:return exc.code,json.load(exc)
  target=json.loads((EVIDENCE.parent/'continuation-02/browser-target.json').read_text('utf-8'))
  status,cite=get(target['citation_path']);ws_status,view=get(f"/api/activities/{target['activity_id']}/teaching/workspace")
  atomic_json(out/'current-target-get.json',{'status':status,'body':cite,'workspace_status':ws_status,'workspace':view,'SUP':0})
  assert status==200 and cite['citation']['text'] and ws_status==200 and not view.get('memory_invalid'),(status,cite)
  target['workspace']=view;target['citation']=cite;atomic_json(out/'browser-target.json',target)
  c.reserve('driver',{'script':'frontend/tests/task103-r03-ui.cjs'});c.reserve('browser',{'profile':str(work/'browser-profile')})
  script=ROOT/'frontend/tests/task103-r03-ui.cjs';node=subprocess.Popen(['node',str(script)],cwd=ROOT/'frontend',env=os.environ.copy(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
  nw={**process_state(node.pid),'module':str(script)};report['driver_witness']=nw
  stdout,stderr=node.communicate(timeout=c.remaining('real',240));(out/'node-stdout.txt').write_bytes(redact(stdout.decode('utf-8','replace')).encode());(out/'node-stderr.txt').write_bytes(redact(stderr.decode('utf-8','replace')).encode())
  browser=json.loads((out/'browser/result.json').read_text('utf-8'));report['browser']=browser;report['driver_exit_code']=node.returncode
  with psycopg.connect(admin,autocommit=True) as conn:
   after=snapshot(conn);atomic_json(out/'pg-after.json',after);assert catalog(conn)==initial
   assert all(row in after[t] for t,rows in before.items() for row in rows),'旧行发生修改'
   ids=c.load().get('synthetic_memory_ids',[]);assert conn.execute('SELECT count(*) FROM activity_memory_choices WHERE memory_id=ANY(%s::uuid[])',(ids,)).fetchone()[0]==0
   writes=[x['payload'] for x in browser['network'] if x['event']=='request' and x['method']=='POST'];proof=[]
   for payload in writes:
    receipt=conn.execute('SELECT effect_applied,request_sha256,after_revision,after_version FROM learning_memory_commands WHERE business_key=%s',(payload['business_key'],)).fetchone()
    assert receipt and receipt[0];proof.append({'request':payload,'persisted':receipt})
   assert len(writes)==c.load()['counts']['memory_post']
   atomic_json(out/'persistent-command-proof.json',{'commands':proof,'all_own_ids_not_selected_by_old_activities':True,'all_old_rows_unchanged':True,'no_delete':True})
   protected=[t for t in before if t not in ['learning_memories','learning_memory_commands','learning_memory_revisions','learning_memory_bodies']]
   assert all(before[t]==after[t] for t in protected)
  assert node.returncode==0 and browser['status']=='PASS',browser.get('error');assert c.load()['counts']['sup']==0;report['status']='PASS'
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
  report['ports_released']={str(p):port_available(p) for p in [18103,55443]};c.charge('cleanup',time.monotonic()-start,{'name':name});atomic_json(out/'result.json',report)
 print(json.dumps({'status':report['status'],'error':report.get('message'),'cases':len(report.get('browser',{}).get('cases',[]))},ensure_ascii=False));return 0 if report['status']=='PASS' else 1
if __name__=='__main__':sys.exit(run())
