"""续作具体配置、既有精确资源与函数前向维护。"""
import asyncio,hashlib,io,json,os,re,secrets,subprocess,time
from pathlib import Path
from urllib.parse import quote
import psycopg
from psycopg import sql
from .control import Control,EVIDENCE,ROOT,atomic_json,SECRET_VALUES,require_entry
from .resources import OwnedDocker,port_available
from ..windows_normal import config,MATERIAL
from ..migration_cleanup import snapshot,catalog,digest
FUNCTIONS={'activity_memory_eligible':'uuid','purge_learning_memory':'uuid,text,uuid,text','memory_final_shape_guard':''}
def ar(coro):
 from app.runtime import psycopg_compatible_loop_factory
 with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:return runner.run(coro)
def owned_start(slot):
 require_entry();control=Control();docker=OwnedDocker(control);resource=next(r for r in control.load()['resources'] if r['slot']==slot)
 docker.start(resource);admin=docker.admin_dsn(resource);end=time.monotonic()+20
 while True:
  try:
   with psycopg.connect(admin,connect_timeout=2) as c:c.execute('SELECT 1')
   break
  except psycopg.Error:
   if time.monotonic()>end:raise
   time.sleep(.05)
 return docker,resource,admin
def forward(conn,label):
 from app.memory.repository import FUNCTION_FINGERPRINTS
 old=json.loads((EVIDENCE.parent/'upgrade-010-catalog.json').read_text(encoding='utf-8'))
 old_rows={r[0]:r for r in old['functions']};migration=(ROOT/'backend/migrations/010_learning_memory.sql').read_text(encoding='utf-8')
 before=snapshot(conn);records=[]
 with conn.transaction():
  for name,args in FUNCTIONS.items():
   signature='public.'+name+'('+args+')'
   row=conn.execute("SELECT pg_get_functiondef(p.oid),p.prosrc,p.provolatile,p.prosecdef,p.proconfig,r.rolname,p.proacl::text FROM pg_proc p JOIN pg_roles r ON r.oid=p.proowner WHERE p.oid=%s::regprocedure",(signature,)).fetchone()
   previous=old_rows[name];body_hash=hashlib.sha256(re.sub(r'\s+','',row[1]).encode()).hexdigest();expected_old=hashlib.sha256(re.sub(r'\s+','',previous[2]).encode()).hexdigest()
   assert body_hash in (expected_old,FUNCTION_FINGERPRINTS[name]),'未知函数源码漂移 '+name
   assert list(row[2:])==previous[3:],'未知函数安全属性漂移 '+name
   (EVIDENCE/'sql').mkdir(exist_ok=True)
   (EVIDENCE/'sql'/(label+'-'+name+'-before.sql')).write_bytes(row[0].encode())
   start=migration.index('CREATE FUNCTION public.'+name+'(');end=migration.index('$f$;',start)+4
   statement=migration[start:end].replace('CREATE FUNCTION','CREATE OR REPLACE FUNCTION',1)
   if body_hash!=FUNCTION_FINGERPRINTS[name]:conn.execute(statement,prepare=False)
   after=conn.execute("SELECT pg_get_functiondef(p.oid),p.prosrc,p.provolatile,p.prosecdef,p.proconfig,r.rolname,p.proacl::text FROM pg_proc p JOIN pg_roles r ON r.oid=p.proowner WHERE p.oid=%s::regprocedure",(signature,)).fetchone()
   assert row[2:]==after[2:] and hashlib.sha256(re.sub(r'\s+','',after[1]).encode()).hexdigest()==FUNCTION_FINGERPRINTS[name]
   (EVIDENCE/'sql'/(label+'-'+name+'-after.sql')).write_bytes(after[0].encode())
   records.append({'function':signature,'before_body_sha':body_hash,'after_body_sha':FUNCTION_FINGERPRINTS[name],'safety_unchanged':True})
 assert snapshot(conn)==before
 atomic_json(EVIDENCE/'sql'/(label+'-forward-proof.json'),{'functions':records,'rows_before_sha':digest(before),'rows_after_sha':digest(snapshot(conn)),'tables':list(before),'rows':sum(map(len,before.values()))})
 atomic_json(EVIDENCE/'sql'/(label+'-catalog-after.json'),catalog(conn))
def configure(admin,resource,name='core',memory_enabled=True):
 # 只在自有服务/worker均已结束的根入口中重置本卡app；真实凭据仅RAM。
 if not port_available(18103) or not port_available(18104):raise RuntimeError('任务端口被占用，未重置角色')
 password=secrets.token_urlsafe(32);SECRET_VALUES.add(password)
 with psycopg.connect(admin,autocommit=True) as c:c.execute(sql.SQL('ALTER ROLE retrolume_task103_app PASSWORD {}').format(sql.Literal(password)))
 dsn=f"postgresql://retrolume_task103_app:{quote(password,safe='')}@127.0.0.1:{resource['port']}/{resource['database']}"
 data=EVIDENCE/'workspace/data';backup=EVIDENCE/'workspace/backup';originals=data/'originals'
 data.mkdir(parents=True,exist_ok=True);backup.mkdir(parents=True,exist_ok=True);originals.mkdir(exist_ok=True)
 copied=[]
 for file in (EVIDENCE.parent/'workspace/data/originals').iterdir():
  if not file.is_file():continue
  body=file.read_bytes();assert hashlib.sha256(body).hexdigest()==file.name
  target=originals/file.name
  if target.exists():assert target.read_bytes()==body
  else:target.write_bytes(body)
  copied.append({'sha256':file.name,'bytes':len(body)})
 atomic_json(EVIDENCE/'originals-copied-readonly.json',copied)
 cfg=EVIDENCE/('workspace/'+name+'-config.json');value=config()
 if not memory_enabled:value['memory_context']=None
 atomic_json(cfg,value);key=secrets.token_urlsafe(24);SECRET_VALUES.add(key)
 os.environ.update(RETROLUME_DATA_DIR=str(data),RETROLUME_BACKUP_DIR=str(backup),RETROLUME_DATABASE_URL=dsn,
  RETROLUME_ACTIVITY_CONFIG=str(cfg),RETROLUME_TASK103_SYNTHETIC_KEY=key)
 return dsn,cfg
def app_client():
 from app.main import create_app
 from app.worker.session import SessionConfig
 from app.runtime import psycopg_compatible_loop_factory
 from fastapi.testclient import TestClient
 app=create_app();app.state.teaching_session_config=SessionConfig(window_seconds=20,request_timeout_seconds=2,stop_grace_seconds=2,
  startup_limit_seconds=5,manager_db_timeout_seconds=5,cleanup_seconds=5,mutex_wait_seconds=3,manager_overhead_seconds=30,single_host_single_session_recovery=False)
 SECRET_VALUES.add(app.state.session_token)
 return app,TestClient(app,backend_options={'loop_factory':psycopg_compatible_loop_factory})
