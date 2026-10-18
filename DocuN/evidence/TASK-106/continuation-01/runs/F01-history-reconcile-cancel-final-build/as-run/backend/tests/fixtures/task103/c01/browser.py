"""C01最终bundle两页真实浏览器与有限控制actor。"""
import io,json,os,subprocess,sys,time,threading,urllib.request
import psycopg
from .common import owned_start,configure,MATERIAL,config
from .control import Control,EVIDENCE,ROOT,atomic_json,redact
from .resources import port_available
from ..processes import process_state,stop_owned
def run():
 control=Control();docker=None;resource=None;server=None;witness=None;actor_thread=None;stop=threading.Event();report={'status':'FAIL','executed':True}
 attempt=os.environ.get('RETROLUME_TASK103_C01_BROWSER','01')
 try:
  docker,resource,admin=owned_start(1);dsn,cfg=configure(admin,resource,'browser')
  from app.materials.repository import PostgresMaterials
  from app.storage.originals import OriginalStore
  store=OriginalStore(EVIDENCE/'workspace/data/originals');original=store.put(io.BytesIO(MATERIAL.encode()),max_bytes=5242880)
  source=PostgresMaterials(dsn).save(source_id=None,expected_version=None,filename='task103-c01-browser.md',format='md',sha256=original.sha256,size=original.size)
  env=os.environ.copy();control.reserve('listener_start',{'module':'tests.fixtures.task103.c01.server','port':18103})
  server=subprocess.Popen([sys.executable,'-X','utf8','-B','-m','tests.fixtures.task103.c01.server'],cwd=ROOT/'backend',env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
  witness={**process_state(server.pid),'module':'tests.fixtures.task103.c01.server'};report['server_witness']=witness
  end=time.monotonic()+20
  while True:
   try:
    with urllib.request.urlopen('http://127.0.0.1:18103/health',timeout=1) as r:
     if r.status==200:break
   except Exception:
    if time.monotonic()>end:raise
    time.sleep(.05)
  folder=EVIDENCE/'workspace/browser-control';folder.mkdir(exist_ok=True);seen=set();actor_results=[]
  def actor():
   try:
    with psycopg.connect(admin,autocommit=True) as conn:
     while not stop.is_set():
      for file in folder.glob('*.request.json'):
       data=json.loads(file.read_text(encoding='utf-8'))
       if data['id'] in seen:continue
       seen.add(data['id']);value={'status':'FAIL','id':data['id'],'kind':data['kind']}
       try:
        if data['kind']=='cleanup_disable':conn.execute('REVOKE EXECUTE ON FUNCTION public.purge_learning_memory(uuid,text,uuid,text) FROM retrolume_memory_app')
        elif data['kind']=='cleanup_enable':conn.execute('GRANT EXECUTE ON FUNCTION public.purge_learning_memory(uuid,text,uuid,text) TO retrolume_memory_app')
        elif data['kind']=='memory_config_disable':
         value_config=config();value_config['memory_context']=None;atomic_json(cfg,value_config)
         atomic_json(EVIDENCE/'workspace/browser-config-reload.json',{'id':data['id']})
         limit=time.monotonic()+10
         while True:
          loaded=EVIDENCE/'workspace/browser-config-reloaded.json'
          if loaded.exists() and json.loads(loaded.read_text(encoding='utf-8')).get('id')==data['id']:break
          if time.monotonic()>limit:raise RuntimeError('config reload timeout')
          time.sleep(.05)
        else:raise RuntimeError('unknown actor request')
        value['status']='PASS'
       except BaseException as exc:value['error']=redact(str(exc))
       atomic_json(folder/(data['id']+'.done.json'),value);actor_results.append(value)
      time.sleep(.02)
   except BaseException as exc:actor_results.append({'status':'FAIL','error':redact(str(exc))})
  actor_thread=threading.Thread(target=actor);actor_thread.start()
  control.reserve('driver',{'script':'frontend/tests/task103-c01-browser.cjs'});control.reserve('browser',{'profile':'workspace/browser-profile-'+attempt})
  ran=subprocess.run(['node',str(ROOT/'frontend/tests/task103-c01-browser.cjs')],cwd=ROOT/'frontend',env=env,capture_output=True,timeout=min(650,control.remaining('real',650)),creationflags=subprocess.CREATE_NO_WINDOW)
  (EVIDENCE/('browser-'+attempt+'-node-out.txt')).write_bytes(redact(ran.stdout.decode('utf-8','replace')).encode());(EVIDENCE/('browser-'+attempt+'-node-error.txt')).write_bytes(redact(ran.stderr.decode('utf-8','replace')).encode())
  actual=json.loads((EVIDENCE/('browser-'+attempt+'/result.json')).read_text(encoding='utf-8'));report.update(browser=actual,exit_code=ran.returncode,source=source,actor=actor_results)
  assert ran.returncode==0 and actual['status']=='PASS',actual.get('error')
  report['status']='PASS'
 except BaseException as exc:
  report.update(error_type=type(exc).__name__,message=redact(str(exc)));(EVIDENCE/('browser-'+attempt+'-root-error.txt')).write_bytes(redact(__import__('traceback').format_exc()).encode())
 finally:
  start=time.monotonic();stop.set()
  if actor_thread:actor_thread.join(timeout=15)
  if server and witness:
   try:
    report['server_stop']=stop_owned(server,witness);stdout,stderr=server.communicate(timeout=5)
    (EVIDENCE/('browser-'+attempt+'-server-out.txt')).write_bytes(redact(stdout.decode('utf-8','replace')).encode());(EVIDENCE/('browser-'+attempt+'-server-error.txt')).write_bytes(redact(stderr.decode('utf-8','replace')).encode())
   except BaseException as exc:report['server_stop_unconfirmed']=type(exc).__name__;report['status']='FAIL'
  if docker and resource:
   try:
    with psycopg.connect(admin,autocommit=True) as conn:conn.execute('GRANT EXECUTE ON FUNCTION public.purge_learning_memory(uuid,text,uuid,text) TO retrolume_memory_app')
    report['container_stop']=docker.stop(resource)
   except BaseException as exc:report['cleanup_unconfirmed']=type(exc).__name__;report['status']='FAIL'
  report['port18103_available']=port_available(18103);control.charge('cleanup',time.monotonic()-start,{'name':'browser'});atomic_json(EVIDENCE/('browser-'+attempt+'-root-result.json'),report)
 print(json.dumps({'status':report['status'],'cases':len(report.get('browser',{}).get('cases',[])),'error':report.get('message')},ensure_ascii=False));return 0 if report['status']=='PASS' else 1
if __name__=='__main__':sys.exit(run())
