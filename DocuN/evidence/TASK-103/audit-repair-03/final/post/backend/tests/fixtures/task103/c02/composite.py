"""同一真实pg1/API/浏览器根补最后四项，现有事实只读选目标。"""
from __future__ import annotations
import asyncio,hashlib,json,os,secrets,subprocess,sys,time,urllib.request,urllib.error
from pathlib import Path
from urllib.parse import quote
from uuid import uuid4
import psycopg
from psycopg import sql
from .control import Control,EVIDENCE,ROOT,atomic_json,redact,SECRET_VALUES,require_entry
from .resources import OwnedDocker,port_available
from ..processes import process_state,stop_owned
from ..migration_cleanup import snapshot,catalog,digest
from ..windows_normal import config

def run():
 c=Control();require_entry();docker=OwnedDocker(c);resource=next(r for r in c.load()['resources'] if r['slot']==1)
 server=None;server_witness=None;node=None;node_witness=None;report={'status':'FAIL','executed':True,'cases':[]};run_name=os.environ['RETROLUME_TASK103_C02_RUN']
 def passed(name,**data):
  report['cases'].append({'name':name,'status':'PASS','executed':True,**data});atomic_json(EVIDENCE/'checkpoint.json',report)
 try:
  assert port_available(18103) and port_available(55443)
  before_resources=[docker.inspect(r) for r in c.load()['resources']];assert all(not r['running'] and r['pid']==0 for r in before_resources)
  atomic_json(EVIDENCE/'resources-before.json',before_resources)
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
   before=snapshot(conn);initial_catalog=catalog(conn);atomic_json(EVIDENCE/'pg-before.json',before);atomic_json(EVIDENCE/'catalog-before.json',initial_catalog)
   conn.execute(sql.SQL('ALTER ROLE retrolume_task103_app PASSWORD {}').format(sql.Literal(password)))
  atomic_json(EVIDENCE/'role-password-action.json',{'role':'retrolume_task103_app','action':'仅自有角色随机密码重置','old_services_stopped':True,
   'ports18103_55443_checked_before_start':True,'credential_memory_only':True,'role_create':0,'attributes_acl_changes':False})
  dsn=f"postgresql://retrolume_task103_app:{quote(password,safe='')}@127.0.0.1:55443/{resource['database']}"
  data=EVIDENCE/'workspace/data';originals=data/'originals';backup=EVIDENCE/'workspace/backup';originals.mkdir(parents=True);backup.mkdir(parents=True)
  copies=[]
  for file in (EVIDENCE.parent/'continuation-01/workspace/data/originals').iterdir():
   if file.is_file():
    content=file.read_bytes();assert hashlib.sha256(content).hexdigest()==file.name;(originals/file.name).write_bytes(content)
    copies.append({'sha256':file.name,'bytes':len(content),'source_readonly':True})
  atomic_json(EVIDENCE/'original-copy.json',copies);cfg=EVIDENCE/'workspace/activity-config.json';atomic_json(cfg,config())
  synthetic=secrets.token_urlsafe(24);SECRET_VALUES.add(synthetic)
  os.environ.update(RETROLUME_DATA_DIR=str(data),RETROLUME_BACKUP_DIR=str(backup),RETROLUME_DATABASE_URL=dsn,RETROLUME_ACTIVITY_CONFIG=str(cfg),RETROLUME_TASK103_SYNTHETIC_KEY=synthetic)
  c.reserve('listener_start',{'module':'tests.fixtures.task103.c02.server','port':18103})
  server=subprocess.Popen([sys.executable,'-X','utf8','-B','-m','tests.fixtures.task103.c02.server'],cwd=ROOT/'backend',env=os.environ.copy(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
  server_witness={**process_state(server.pid),'module':'tests.fixtures.task103.c02.server'};report['server_witness']=server_witness
  limit=time.monotonic()+20
  while True:
   try:
    with urllib.request.urlopen('http://127.0.0.1:18103/health',timeout=1) as response:
     if response.status==200:break
   except Exception:
    if time.monotonic()>limit:raise
    time.sleep(.05)
  with urllib.request.urlopen('http://127.0.0.1:18103/api/session',timeout=3) as response:session=json.load(response)
  token=session['token'];SECRET_VALUES.add(token)
  def request(path,body=None):
   headers={'X-RetroLume-Session':token,'Origin':'http://127.0.0.1:18103'}
   raw=None if body is None else json.dumps(body,ensure_ascii=False).encode()
   if raw is not None:headers['Content-Type']='application/json'
   try:
    with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:18103'+path,data=raw,headers=headers),timeout=55) as response:return response.status,json.load(response)
   except urllib.error.HTTPError as exc:return exc.code,json.load(exc)
  def get(path):
   status,value=request(path);assert status==200,(path,status,value);return value
  def post(path,body):
   status,value=request(path,body);assert status==200,(path,status,value);return value
  objects=json.loads((EVIDENCE.parent/'continuation-01/gaps-result.json').read_text('utf-8'))['objects']
  aid=str(uuid4());post('/api/activities',{'activity_id':aid,'source_ids':[objects['source']['id']]});view=get(f'/api/activities/{aid}/teaching/workspace')
  goal={'business_key':str(uuid4()),'expected_revision':view['head']['revision'],'expected_goal_version':view['head']['goal_version'],'expected_scope_revision':1,
   'action':'goal','body':{'goal':'铱铂同位素测定','self_report':None,'domain':None,'seed_operation_id':None,'seed_payload_sha256':None}}
  post(f'/api/activities/{aid}/teaching/commands',goal);view=get(f'/api/activities/{aid}/teaching/workspace');key=str(uuid4())
  command={'business_key':key,'expected_revision':view['head']['revision'],'expected_goal_version':view['head']['goal_version'],'expected_scope_revision':1,
   'action':'plan','body':{'confirmed':True,'correction_record_id':None,'retry_of':None}}
  def target_snapshot(conn):
   names=['activities','teaching_heads','teaching_commands','teaching_records','activity_operations','activity_operation_results'];result={}
   for table in names:
    column='id' if table=='activities' else 'activity_id'
    result[table]=conn.execute(sql.SQL('SELECT COALESCE(jsonb_agg(to_jsonb(t)),\'[]\'::jsonb) FROM public.{} t WHERE {}=%s').format(sql.Identifier(table),sql.Identifier(column)),(aid,)).fetchone()[0]
   return result
  with psycopg.connect(admin,autocommit=True) as conn:pre=target_snapshot(conn)
  sup_before=c.load()['counts']['sup'];provider_before=list((EVIDENCE/'observations').glob('*-provider.json')) if (EVIDENCE/'observations').exists() else []
  status,result=request(f'/api/activities/{aid}/teaching/commands',command)
  with psycopg.connect(admin,autocommit=True) as conn:after=target_snapshot(conn)
  assert status==409 and result['detail']['code']=='no_evidence' and '没有找到相关证据' in result['detail']['message'],(status,result)
  assert pre==after and c.load()['counts']['sup']==sup_before==0
  providers=list((EVIDENCE/'observations').glob('*-provider.json')) if (EVIDENCE/'observations').exists() else [];assert not providers and not provider_before
  atomic_json(EVIDENCE/'no-evidence-http.json',{'activity_id':aid,'business_key':key,'request':command,'response_status':status,'response':result,'before':pre,'after':after,
   'rows_equal':True,'new_accepted_commands':0,'new_operations':0,'provider_sends':0,'sup':0,'budgets_before':view['budgets'],'budgets_after':get(f'/api/activities/{aid}/teaching/workspace')['budgets']})
  report['objects']={'no_evidence_activity':aid,'no_evidence_key':key};passed('DEF022 真实鉴权HTTP/PG no_evidence409及六表/四账零副作用',activity_id=aid,business_key=key,sql_before_sha=digest(pre),sql_after_sha=digest(after),sup=0,provider=0)
  def citation_ids(value):
   ids=[]
   def walk(item):
    if isinstance(item,dict):
     if isinstance(item.get('citations'),list):ids.extend(x for x in item['citations'] if isinstance(x,str))
     for v in item.values():walk(v)
    elif isinstance(item,list):
     for v in item:walk(v)
   walk(value);return list(dict.fromkeys(ids))
  targets=[];candidate_checks=[]
  candidate_ids=[objects['child_activity'],objects['activity']]
  with psycopg.connect(admin,autocommit=True) as conn:
   candidate_ids.extend(str(row[0]) for row in conn.execute("SELECT activity_id FROM teaching_heads h WHERE h.path_record_id IS NOT NULL OR EXISTS(SELECT 1 FROM teaching_records r WHERE r.activity_id=h.activity_id AND r.kind='path_proposal') ORDER BY updated_at DESC"))
  for candidate in dict.fromkeys(candidate_ids):
   view_status,workspace=request(f'/api/activities/{candidate}/teaching/workspace');entry={'activity_id':candidate,'workspace_status':view_status}
   if view_status==200:
    path=workspace.get('proposal') or workspace.get('path');ids=citation_ids(path)
    if path and ids and not workspace.get('memory_invalid'):
     record_id=path['record_id'];uri=f'/api/activities/{candidate}/teaching/records/{record_id}/citations/{ids[0]}'
     cite_status,cite=request(uri);entry.update(record_id=record_id,citation_id=ids[0],citation_status=cite_status)
     if cite_status==200:
      targets.append({'activity_id':candidate,'record_id':record_id,'citation_id':ids[0],'citation_path':uri,'workspace':workspace,'citation':cite})
   candidate_checks.append(entry)
   if targets:break
  atomic_json(EVIDENCE/'target-selection.json',{'candidates':candidate_checks,'targets':targets,'sup_prepared':0,'synthetic_or_qualification_patched':False})
  prepared_sup=0
  if not targets:
   # 已实际穷读全部现有路径候选才使用卡内附条件准备；负例此前已经完成且SUP0。
   with c.locked():
    state=c.load();assert state['counts']['sup']==0;state['allow_sup_preparation']=True;state['sup_preparation_basis']=str(EVIDENCE/'target-selection.json');atomic_json(c.path,state)
   fresh=str(uuid4());post('/api/activities',{'activity_id':fresh,'source_ids':[objects['source']['id']]})
   view=get(f'/api/activities/{fresh}/teaching/workspace');post(f'/api/activities/{fresh}/teaching/commands',{'business_key':str(uuid4()),'expected_revision':view['head']['revision'],
    'expected_goal_version':view['head']['goal_version'],'expected_scope_revision':1,'action':'goal','body':{'goal':'平均速度与单位','self_report':None,'domain':None,'seed_operation_id':None,'seed_payload_sha256':None}})
   view=get(f'/api/activities/{fresh}/teaching/workspace');receipt=post(f'/api/activities/{fresh}/teaching/commands',{'business_key':str(uuid4()),'expected_revision':view['head']['revision'],
    'expected_goal_version':view['head']['goal_version'],'expected_scope_revision':1,'action':'plan','body':{'confirmed':True,'correction_record_id':None,'retry_of':None}})
   assert receipt['status']=='committed',receipt;workspace=get(f'/api/activities/{fresh}/teaching/workspace');proposal=workspace['proposal'];ids=citation_ids(proposal)
   uri=f"/api/activities/{fresh}/teaching/records/{proposal['record_id']}/citations/{ids[0]}";cite=get(uri)
   targets=[{'activity_id':fresh,'record_id':proposal['record_id'],'citation_id':ids[0],'citation_path':uri,'workspace':workspace,'citation':cite}];prepared_sup=c.load()['counts']['sup'];assert 0<prepared_sup<=2
   atomic_json(EVIDENCE/'conditional-reference-preparation.json',{'basis':str(EVIDENCE/'target-selection.json'),'activity_id':fresh,'receipt':receipt,'targets':targets,'sup':prepared_sup,'no_evidence_earlier_sup':0})
  target=targets[0];target['switch_activity_id']=aid;atomic_json(EVIDENCE/'browser-target.json',target)
  c.reserve('driver',{'script':'frontend/tests/task103-c02-browser.cjs'});c.reserve('browser',{'profile':'workspace/browser-profile'})
  script=ROOT/'frontend/tests/task103-c02-browser.cjs';node=subprocess.Popen(['node',str(script)],cwd=ROOT/'frontend',env=os.environ.copy(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
  node_witness={**process_state(node.pid),'module':str(script)};report['driver_witness']=node_witness
  stdout,stderr=node.communicate(timeout=c.remaining('real',450));(EVIDENCE/'browser-stdout.txt').write_bytes(redact(stdout.decode('utf-8','replace')).encode());(EVIDENCE/'browser-stderr.txt').write_bytes(redact(stderr.decode('utf-8','replace')).encode())
  browser=json.loads((EVIDENCE/'browser/result.json').read_text('utf-8'));report['browser']=browser;report['driver_exit_code']=node.returncode
  assert node.returncode==0 and browser['status']=='PASS',browser.get('error')
  with psycopg.connect(admin,autocommit=True) as conn:
   final_rows=snapshot(conn);atomic_json(EVIDENCE/'pg-after.json',final_rows);assert catalog(conn)==initial_catalog
   for case in browser['cases']:
    if 'memory_id' not in case:continue
    mid=case['memory_id'];head=conn.execute('SELECT revision,current_version,state FROM learning_memories WHERE memory_id=%s',(mid,)).fetchone();rows=conn.execute('SELECT business_key,effect_applied,request_sha256,action FROM learning_memory_commands WHERE memory_id=%s ORDER BY committed_at',(mid,)).fetchall()
    expected=2 if case['name']=='V15 双页真实陈旧POST' else 1
    assert head==(expected,expected,'active') and sum(1 for r in rows if r[1])==expected
    if case.get('stale_key'):assert not any(str(r[0])==case['stale_key'] for r in rows)
    atomic_json(EVIDENCE/('memory-db-'+mid+'.json'),{'head':list(head),'receipts':rows,'effect_count':expected})
   # 所有旧表行逐身份保留，只允许本轮新行及新合成记忆的追加revision。
   assert all(row in final_rows[name] for name,rows in before.items() for row in rows),'旧事实发生改变'
  assert c.load()['counts']['sup']==prepared_sup;report['sup_prepared']=prepared_sup;report['status']='PASS'
 except BaseException as exc:
  report.update(error_type=type(exc).__name__,message=redact(str(exc)));(EVIDENCE/('error-'+run_name+'.txt')).write_bytes(redact(__import__('traceback').format_exc()).encode())
 finally:
  clean=time.monotonic()
  for proc,witness,label in [(node,node_witness,'driver'),(server,server_witness,'server')]:
   if proc and witness:
    try:
     report[label+'_stop']=stop_owned(proc,witness)
     out,err=proc.communicate(timeout=5)
     if label=='server':(EVIDENCE/'server-stdout.txt').write_bytes(redact(out.decode('utf-8','replace')).encode());(EVIDENCE/'server-stderr.txt').write_bytes(redact(err.decode('utf-8','replace')).encode())
    except BaseException as exc:report[label+'_stop_unconfirmed']=type(exc).__name__;report['status']='FAIL'
  try:report['container_stop']=docker.stop(resource)
  except BaseException as exc:report['container_stop_unconfirmed']=type(exc).__name__;report['status']='FAIL'
  report['ports_released']={str(p):port_available(p) for p in [18103,55443]};c.charge('cleanup',time.monotonic()-clean,{'name':run_name})
  atomic_json(EVIDENCE/('result-'+run_name+'.json'),report);atomic_json(EVIDENCE/'result.json',report)
 print(json.dumps({'status':report['status'],'cases':len(report['cases'])+len(report.get('browser',{}).get('cases',[])),'error':report.get('message')},ensure_ascii=False));return 0 if report['status']=='PASS' else 1
if __name__=='__main__':sys.exit(run())
