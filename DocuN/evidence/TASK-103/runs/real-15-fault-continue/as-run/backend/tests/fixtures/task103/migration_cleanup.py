"""两个获准独立cluster的具体升级、坏前置和精确清理检查。"""
from __future__ import annotations
import asyncio,hashlib,io,json,os,secrets,sys,time
from datetime import datetime,timedelta,timezone
from urllib.parse import quote
from uuid import uuid4
import psycopg
from psycopg import sql
from .control import Control,EVIDENCE,ROOT,atomic_json,redact,SECRET_VALUES
from .resources import OwnedDocker
from .windows_normal import config,MATERIAL

TABLES=['learning_memories','learning_memory_commands','learning_memory_revisions','learning_memory_bodies',
 'learning_memory_dependencies','activity_memory_bindings','activity_memory_choices']
FUNCTIONS=['memory_dependency_line(public.learning_memory_dependencies)','memory_dependency_digest(uuid,integer)',
 'memory_scope_digest(uuid)','memory_choice_digest(uuid)','memory_revision_readable(uuid,integer)',
 'memory_revision_eligible(uuid,integer)','activity_memory_eligible(uuid)','memory_immutable_guard()',
 'memory_head_guard()','memory_body_guard()','memory_final_shape_guard()','purge_learning_memory(uuid,text,uuid,text)']
ROLES=['retrolume_memory_owner','retrolume_memory_app','retrolume_memory_purger']

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),default=str).encode()).hexdigest()
def snapshot(conn,names=None):
 if names is None:names=[r[0] for r in conn.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")]
 rows={}
 for name in names:
  rows[name]=conn.execute(sql.SQL("SELECT COALESCE(jsonb_agg(j),'[]'::jsonb) FROM (SELECT to_jsonb(t) AS j FROM public.{} t ORDER BY to_jsonb(t)::text) x").format(sql.Identifier(name))).fetchone()[0]
 return rows
def catalog(conn):
 return {'tables':conn.execute("SELECT c.relname,a.attname,format_type(a.atttypid,a.atttypmod),a.attnotnull FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_attribute a ON a.attrelid=c.oid WHERE n.nspname='public' AND c.relkind='r' AND a.attnum>0 AND NOT a.attisdropped ORDER BY c.relname,a.attnum").fetchall(),
  'constraints':conn.execute("SELECT c.relname,k.conname,pg_get_constraintdef(k.oid),k.convalidated FROM pg_constraint k JOIN pg_class c ON c.oid=k.conrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' ORDER BY c.relname,k.conname").fetchall(),
  'functions':conn.execute("SELECT p.proname,pg_get_function_identity_arguments(p.oid),p.prosrc,p.provolatile,p.prosecdef,p.proconfig,r.rolname,p.proacl::text FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace JOIN pg_roles r ON r.oid=p.proowner WHERE n.nspname='public' ORDER BY p.proname,p.oid").fetchall(),
  'triggers':conn.execute("SELECT c.relname,t.tgname,t.tgenabled,pg_get_triggerdef(t.oid) FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND NOT t.tgisinternal ORDER BY c.relname,t.tgname").fetchall(),
  'roles':conn.execute("SELECT rolname,rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls FROM pg_roles WHERE rolname LIKE 'retrolume_%' ORDER BY rolname").fetchall()}
def apply010(conn,inside=False):
 source=(ROOT/'backend/migrations/010_learning_memory.sql').read_text(encoding='utf-8')
 if inside:
  source=source.replace('BEGIN;','',1);source=source.rsplit('COMMIT;',1)[0]
 conn.execute(source,prepare=False)
def grants(conn,password,denied):
 conn.execute(sql.SQL('CREATE ROLE retrolume_task103_app LOGIN PASSWORD {}').format(sql.Literal(password)))
 conn.execute(sql.SQL('CREATE ROLE retrolume_task103_denied LOGIN PASSWORD {}').format(sql.Literal(denied)))
 for name in ['material_sources','material_versions','activities','activity_scope_sources','activity_allowed_models','activity_operations',
  'activity_operation_results','teaching_heads','teaching_commands','teaching_records','pdf_review_candidates','pdf_extracted_pages','pdf_review_pages','pdf_user_supplements']:
  conn.execute(sql.SQL('GRANT SELECT,INSERT,UPDATE ON public.{} TO retrolume_task103_app').format(sql.Identifier(name)))
 conn.execute('GRANT DELETE ON public.activity_scope_sources TO retrolume_task103_app')
def reset_env(dsn,name):
 data=EVIDENCE/'workspace/data';backup=EVIDENCE/'workspace/backup'
 data.mkdir(parents=True,exist_ok=True);backup.mkdir(parents=True,exist_ok=True)
 cfg=EVIDENCE/('workspace/'+name+'-config.json');value=config();value['memory_context']=None;atomic_json(cfg,value)
 key=secrets.token_urlsafe(24);SECRET_VALUES.add(key)
 os.environ.update(RETROLUME_DATA_DIR=str(data),RETROLUME_BACKUP_DIR=str(backup),RETROLUME_DATABASE_URL=dsn,
  RETROLUME_ACTIVITY_CONFIG=str(cfg),RETROLUME_TASK103_SYNTHETIC_KEY=key)
class RollbackSample(Exception):pass

def upgrade(conn,dsn,report,passed):
 from app.main import create_app
 from app.materials.repository import PostgresMaterials
 from app.runtime import psycopg_compatible_loop_factory
 from app.worker.session import SessionConfig
 from fastapi.testclient import TestClient
 reset_env(dsn,'upgrade');app=create_app();app.state.teaching_session_config=SessionConfig(window_seconds=20,request_timeout_seconds=2,stop_grace_seconds=2)
 SECRET_VALUES.add(app.state.session_token)
 original=app.state.originals.put(io.BytesIO(MATERIAL.encode()),max_bytes=5242880)
 source=PostgresMaterials(dsn).save(source_id=None,expected_version=None,filename='task103-upgrade-legacy.md',format='md',sha256=original.sha256,size=original.size)
 def ar(coro):
  with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:return runner.run(coro)
 with TestClient(app,backend_options={'loop_factory':psycopg_compatible_loop_factory}) as client:
  headers={'x-retrolume-session':app.state.session_token,'origin':'http://testserver'}
  def req(path,body=None):
   response=client.get(path,headers=headers) if body is None else client.post(path,headers=headers,json=body)
   assert response.status_code==200,(path,response.status_code,response.json());return response.json()
  aid=str(uuid4());req('/api/activities',{'activity_id':aid,'source_ids':[source['id']]})
  def submit(action,body):
   view=req(f'/api/activities/{aid}/teaching/workspace')
   return req(f'/api/activities/{aid}/teaching/commands',{'business_key':str(uuid4()),'expected_revision':view['head']['revision'],
    'expected_goal_version':view['head']['goal_version'],'expected_scope_revision':1,'action':action,'body':body})
  submit('goal',{'goal':'平均速度旧v1升级事实','self_report':None,'domain':None,'seed_operation_id':None,'seed_payload_sha256':None})
  plan=submit('plan',{'confirmed':True,'correction_record_id':None,'retry_of':None});assert plan['status']=='committed'
  view=req(f'/api/activities/{aid}/teaching/workspace');submit('accept_path',{'proposal_record_id':view['proposal']['record_id']})
  view=req(f'/api/activities/{aid}/teaching/workspace')
  submit('exercise',{'confirmed':True,'path_record_id':view['head']['path_record_id'],'node_id':'n1','purpose':'initial','parent_feedback_record_id':None,'retry_of':None})
  view=req(f'/api/activities/{aid}/teaching/workspace');eid=view['head']['exercise_record_id']
  answer=submit('answer',{'exercise_record_id':eid,'kind':'initial','text':'1m/s','supersedes_answer_record_id':None})
  submit('evaluate',{'confirmed':True,'exercise_record_id':eid,'answer_record_id':answer['record_ids'][0]['record_id'],'correction_record_id':None,'retry_of':None})
  # 旧通用账本真实准入、mark和正文/UNKNOWN，不伪造远端或监督见证。
  from app.capabilities.contracts import AdmissionIntent,LedgerOutcome,LedgerDisposition,CallContext,Provider
  from app.capabilities import build_business_payload
  ledger=app.state.activities_ledger
  old=str(uuid4());req('/api/activities',{'activity_id':old,'source_ids':[source['id']]})
  lease=ar(ledger.claim_lease(old,'task103-upgrade',lease_seconds=60,window_seconds=20))
  for op,unknown in [('task103-g7-seed',False),('task103-g7-unknown',True)]:
   permit=ar(ledger.admit(AdmissionIntent(context=CallContext(activity_id=old,operation_id=op,executor_id='task103-upgrade',execution_generation=lease.execution_generation,scope_revision=1),
    provider=Provider.DEEPSEEK_CHAT_COMPLETIONS,configured_model='deepseek-v4-flash',request_bytes=200,max_output_tokens=128,tool_names=())))
   ar(ledger.mark_dispatch_started(permit))
   if unknown:outcome=LedgerOutcome(disposition=LedgerDisposition.UNKNOWN,error_code='delivery_unknown')
   else:
    fmt,body,sha=build_business_payload(text='旧007合成正文，不是provider质量证据')
    outcome=LedgerOutcome(disposition=LedgerDisposition.RECEIVED,returned_model='deepseek-v4-flash',finish_reason='stop',prompt_tokens=128,completion_tokens=64,response_bytes=256,payload=body,payload_format=fmt,payload_sha256=sha)
   ar(ledger.record_outcome(permit,outcome))
  finish_upgrade(conn,req,aid,old,report,passed)

def finish_upgrade(conn,req,aid,old,report,passed):
 before=snapshot(conn);old_names=list(before);old_catalog=catalog(conn)
 atomic_json(EVIDENCE/'upgrade-old-before.json',before)
 apply010(conn);conn.execute('GRANT retrolume_memory_app TO retrolume_task103_app')
 after=snapshot(conn,old_names);assert before==after
 atomic_json(EVIDENCE/'upgrade-old-after.json',after);atomic_json(EVIDENCE/'upgrade-010-catalog.json',catalog(conn))
 workspace=req(f'/api/activities/{aid}/teaching/workspace');assert workspace['feedback'] and not workspace.get('memory_invalid',False)
 passed('V20 非空v1/007/UNKNOWN升级旧行逐字段不变',before_sha=digest(before),after_sha=digest(after),tables=len(old_names),rows=sum(map(len,before.values())),activity_ids=[aid,old])
 assert all(conn.execute(sql.SQL('SELECT count(*) FROM public.{}').format(sql.Identifier(t))).fetchone()[0]==0 for t in TABLES)
 external=conn.execute("SELECT count(*) FROM pg_constraint WHERE confrelid=ANY(SELECT oid FROM pg_class WHERE relname=ANY(%s)) AND conrelid<>ALL(SELECT oid FROM pg_class WHERE relname=ANY(%s))",(TABLES,TABLES)).fetchone()[0]
 assert external==0
 triggers=conn.execute('SELECT c.relname,t.tgname FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid WHERE c.relname=ANY(%s) AND NOT t.tgisinternal ORDER BY c.relname,t.tgname',(TABLES,)).fetchall()
 reverse=[f'DROP TRIGGER {tr} ON public.{table};' for table,tr in triggers]+[f'DROP FUNCTION public.{f};' for f in FUNCTIONS]
 reverse+=['ALTER TABLE public.learning_memories DROP CONSTRAINT memory_current_version;','ALTER TABLE public.learning_memories DROP CONSTRAINT memory_revoke_command;']
 reverse += [f'DROP TABLE public.{t};' for t in ['activity_memory_choices','activity_memory_bindings','learning_memory_dependencies','learning_memory_bodies','learning_memory_revisions','learning_memory_commands','learning_memories']]
 reverse+=['REVOKE retrolume_memory_app FROM retrolume_task103_app;']+[f'REVOKE USAGE ON SCHEMA public FROM {r};' for r in ROLES]+[f'DROP ROLE {r};' for r in ROLES]
 atomic_json(EVIDENCE/'upgrade-empty-reverse-pre.json',{'all_new_rows':0,'external_fk':external,'objects':catalog(conn),'statements':reverse})
 (EVIDENCE/'upgrade-empty-reverse.sql').write_bytes(('BEGIN;\n'+'\n'.join(reverse)+'\nCOMMIT;\n').encode())
 with conn.transaction():
  for statement in reverse:conn.execute(statement)
 assert snapshot(conn,old_names)==before
 assert conn.execute('SELECT count(*) FROM pg_roles WHERE rolname=ANY(%s)',(ROLES,)).fetchone()[0]==0
 assert req(f'/api/activities/{aid}/teaching/workspace')['feedback']
 passed('V20 空010精确反向DDL，无CASCADE，旧数据与v1读取保留',new_rows=0,external_fk=0,statements=len(reverse),old_before_sha=digest(before),old_after_sha=digest(snapshot(conn,old_names)))
 report['legacy_catalog_before']=old_catalog;report['catalog_after_reverse']=catalog(conn)

def resume_upgrade(conn,dsn,report,passed):
 from app.main import create_app
 from app.runtime import psycopg_compatible_loop_factory
 from fastapi.testclient import TestClient
 from app.activities import PostgresAdmissionLedger
 from app.capabilities.contracts import AdmissionIntent,LedgerOutcome,LedgerDisposition,CallContext,Provider
 from app.capabilities import build_business_payload
 reset_env(dsn,'upgrade');app=create_app();SECRET_VALUES.add(app.state.session_token)
 aid=str(conn.execute("SELECT activity_id FROM teaching_heads WHERE feedback_record_id IS NOT NULL ORDER BY activity_id LIMIT 1").fetchone()[0])
 old=str(conn.execute("SELECT id FROM activities WHERE executor_id='task103-upgrade' ORDER BY id LIMIT 1").fetchone()[0])
 ledger=PostgresAdmissionLedger(dsn)
 def ar(coro):
  with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:return runner.run(coro)
 lease=ar(ledger.claim_lease(old,'task103-upgrade',lease_seconds=60,window_seconds=20))
 for op,unknown in [('task103-g7-seed',False),('task103-g7-unknown',True)]:
  if conn.execute('SELECT 1 FROM activity_operations WHERE activity_id=%s AND operation_id=%s',(old,op)).fetchone():continue
  permit=ar(ledger.admit(AdmissionIntent(context=CallContext(activity_id=old,operation_id=op,executor_id='task103-upgrade',execution_generation=lease.execution_generation,scope_revision=1),provider=Provider.DEEPSEEK_CHAT_COMPLETIONS,configured_model='deepseek-v4-flash',request_bytes=200,max_output_tokens=128,tool_names=())))
  ar(ledger.mark_dispatch_started(permit))
  if unknown:outcome=LedgerOutcome(disposition=LedgerDisposition.UNKNOWN,error_code='delivery_unknown')
  else:
   fmt,body,sha=build_business_payload(text='旧007合成正文，不是provider质量证据')
   outcome=LedgerOutcome(disposition=LedgerDisposition.RECEIVED,returned_model='deepseek-v4-flash',finish_reason='stop',prompt_tokens=128,completion_tokens=64,response_bytes=256,payload=body,payload_format=fmt,payload_sha256=sha)
  ar(ledger.record_outcome(permit,outcome))
 with TestClient(app,backend_options={'loop_factory':psycopg_compatible_loop_factory}) as client:
  def req(path):
   r=client.get(path,headers={'x-retrolume-session':app.state.session_token,'origin':'http://testserver'})
   assert r.status_code==200,(r.status_code,r.json());return r.json()
  finish_upgrade(conn,req,aid,old,report,passed)

def fault(conn,dsn,denied_dsn,report,passed):
 faults=[('同名kind CHECK被弱化',"ALTER TABLE public.activity_operations DROP CONSTRAINT activity_operations_kind_domain; ALTER TABLE public.activity_operations ADD CONSTRAINT activity_operations_kind_domain CHECK(kind IN ('model','tool','unsafe'))"),
  ('007 payload列类型错',"ALTER TABLE public.activity_operation_results ALTER COLUMN payload TYPE varchar USING payload::varchar"),
  ('009触发器身份缺失',"ALTER TRIGGER teaching_records_immutable ON public.teaching_records RENAME TO task103_wrong_trigger"),
  ('新表残迹',"CREATE TABLE public.learning_memories(x integer)"),
  ('新角色残迹',"CREATE ROLE retrolume_memory_app LOGIN")]
 baseline=catalog(conn)
 completed={x['name'] for x in report['cases']}
 for name,change in faults:
  if 'V20 '+name+'迁移失败且全回滚' in completed:continue
  try:
   with conn.transaction():
    conn.execute(change,prepare=False);pre=catalog(conn)
    try:
     with conn.transaction():apply010(conn,inside=True)
     raise AssertionError('bad migration accepted')
    except psycopg.Error as exc:state=exc.sqlstate;reason=exc.diag.message_primary
    assert catalog(conn)==pre
    passed('V20 '+name+'迁移失败且全回滚',sqlstate=state,reason=reason,pre_sha=digest(pre),post_sha=digest(catalog(conn)))
    raise RollbackSample()
  except RollbackSample:pass
  assert catalog(conn)==baseline
 apply010(conn);conn.execute('GRANT retrolume_memory_app TO retrolume_task103_app')
 atomic_json(EVIDENCE/'fault-010-catalog.json',catalog(conn))
 from app.activities import PostgresAdmissionLedger
 from app.memory.service import MemoryService
 from app.memory.contracts import MemoryCommandInput
 from app.runtime import psycopg_compatible_loop_factory
 ledger=PostgresAdmissionLedger(dsn);service=MemoryService(ledger)
 def ar(coro):
  with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:return runner.run(coro)
 mid=str(uuid4())
 first=MemoryCommandInput(business_key=str(uuid4()),memory_id=mid,expected_revision=0,action='save',body={'kind':'self_report','title':'清理故障目标','text':'仅合成正文第一版'})
 ar(service.submit_command(first))
 view=ar(ledger.read_memory_snapshot(mid));impact=ar(ledger.preview_memory_change(mid,1,'revise'))
 ar(service.submit_command(MemoryCommandInput(business_key=str(uuid4()),memory_id=mid,expected_revision=1,action='revise',
  body={'kind':'self_report','title':'清理故障目标','text':'仅合成正文第二版','base_body_sha256':view['body_sha256'],'impact_token':impact['impact_token']})))
 imp=ar(ledger.preview_memory_change(mid,2,'revoke'));rev=MemoryCommandInput(business_key=str(uuid4()),memory_id=mid,expected_revision=2,action='revoke',body={'impact_token':imp['impact_token'],'confirm_revoke':True,'purge_memory_content':True})
 receipt=ar(ledger.apply_memory_command(rev));assert receipt['purge_state_now']=='pending'
 purge=MemoryCommandInput(business_key=str(uuid4()),memory_id=mid,expected_revision=3,action='purge',body={'revocation_key':rev.business_key,'manifest_sha256':receipt['manifest_sha256'],'confirm_memory_cleanup':True})
 before=snapshot(conn);body_pre=before['learning_memory_bodies']
 # 在已提交的新故障trigger中，第二次DELETE后抛错，观察真实普通login事务回滚。
 fail_body=f"BEGIN IF OLD.memory_id='{mid}'::uuid AND OLD.version=2 THEN RAISE EXCEPTION 'task103 midway synthetic fault'; END IF; RETURN OLD; END"
 conn.execute(sql.SQL('CREATE FUNCTION public.task103_midway_fault() RETURNS trigger LANGUAGE plpgsql SECURITY INVOKER AS {}').format(sql.Literal(fail_body)))
 conn.execute('REVOKE ALL ON FUNCTION public.task103_midway_fault() FROM PUBLIC')
 conn.execute('CREATE TRIGGER task103_midway_fault AFTER DELETE ON public.learning_memory_bodies FOR EACH ROW EXECUTE FUNCTION public.task103_midway_fault()')
 try:ar(ledger.apply_memory_command(purge));raise AssertionError('midway fault ignored')
 except Exception as exc:
  from app.capabilities import AdmissionUnavailable
  assert isinstance(exc,AdmissionUnavailable),type(exc).__name__
 assert snapshot(conn)==before and conn.execute('SELECT state,purge_state FROM learning_memories WHERE memory_id=%s',(mid,)).fetchone()==('revoked','pending')
 passed('V19 第二版删除中途故障整笔回滚，墓碑保留',memory_id=mid,bodies_before=2,bodies_after=2,rows_sha_before=digest(before),rows_sha_after=digest(snapshot(conn)))
 conn.execute("CREATE OR REPLACE FUNCTION public.task103_midway_fault() RETURNS trigger LANGUAGE plpgsql SECURITY INVOKER AS 'BEGIN RETURN OLD; END'")
 (EVIDENCE/'purge-fault-function-before.sql').write_bytes(fail_body.encode())
 # 坏正文、缺项/额外清单仅在明确事务内制造，全部回滚；009与旧表未关闭触发器。
 for name,kind in [('正文hash不符','body'),('清单缺版本','missing_manifest'),('清单额外版本','extra_manifest')]:
  try:
   with conn.transaction():
    if kind=='body':
     conn.execute('ALTER TABLE public.learning_memory_bodies DISABLE TRIGGER memory_body_integrity')
     conn.execute('UPDATE public.learning_memory_bodies SET body=body||%s WHERE memory_id=%s AND version=2',(' ',mid))
     conn.execute('ALTER TABLE public.learning_memory_bodies ENABLE TRIGGER memory_body_integrity')
    else:
     row=conn.execute('SELECT cleanup_manifest FROM learning_memory_commands WHERE business_key=%s',(rev.business_key,)).fetchone()[0];doc=json.loads(row)
     if kind=='missing_manifest':doc['targets']=doc['targets'][:1]
     else:doc['targets'].append({**doc['targets'][0],'version':32})
     text=json.dumps(doc,ensure_ascii=False,sort_keys=True,separators=(',',':'));manifest_hash=hashlib.sha256(text.encode()).hexdigest()
     conn.execute('ALTER TABLE public.learning_memory_commands DISABLE TRIGGER memory_command_immutable')
     conn.execute('UPDATE learning_memory_commands SET cleanup_manifest=%s,manifest_sha256=%s WHERE business_key=%s',(text,manifest_hash,rev.business_key))
     conn.execute('ALTER TABLE public.learning_memory_commands ENABLE TRIGGER memory_command_immutable')
    pre=snapshot(conn)
    try:
     with conn.transaction():
      conn.execute('SET LOCAL ROLE retrolume_task103_app')
      conn.execute('SELECT public.purge_learning_memory(%s,%s,%s,%s)',(rev.business_key,receipt['manifest_sha256'] if kind=='body' else manifest_hash,str(uuid4()),'c'*64))
     raise AssertionError('bad purge accepted')
    except psycopg.Error as exc:state=exc.sqlstate;reason=exc.diag.message_primary
    assert snapshot(conn)==pre
    passed('V19 '+name+'拒绝且零效果',sqlstate=state,reason=reason,pre_sha=digest(pre),post_sha=digest(snapshot(conn)))
    raise RollbackSample()
  except RollbackSample:pass
  assert snapshot(conn)==before
 with psycopg.connect(dsn) as app:
  app.execute("SELECT set_config('retrolume.purge_authorized','true',true)")
  for statement in ['DELETE FROM learning_memory_bodies WHERE memory_id=%s','TRUNCATE learning_memory_bodies','SET ROLE retrolume_memory_purger',
   'ALTER TABLE learning_memory_bodies DISABLE TRIGGER memory_body_integrity','DROP FUNCTION public.purge_learning_memory(uuid,text,uuid,text)','UPDATE teaching_records SET body=body']:
   try:
    with app.transaction():app.execute(statement,(mid,) if '%s' in statement else None)
    raise AssertionError('app privilege bypass accepted')
   except psycopg.Error as exc:assert exc.sqlstate in ('42501','P0001'),exc.sqlstate
 with psycopg.connect(denied_dsn) as denied:
  try:
   with denied.transaction():denied.execute('SELECT public.purge_learning_memory(%s,%s,%s,%s)',(rev.business_key,receipt['manifest_sha256'],str(uuid4()),'c'*64))
   raise AssertionError('PUBLIC execute accepted')
  except psycopg.errors.InsufficientPrivilege:pass
 passed('V12/V19 普通app/GUC/角色切换/DDL与PUBLIC清理权限拒绝',app_role='retrolume_task103_app',denied_role='retrolume_task103_denied')
 with psycopg.connect(dsn) as app:
  app.execute('CREATE TEMP TABLE learning_memories(x integer)');app.execute('CREATE TEMP TABLE learning_memory_bodies(x integer)')
  app.execute('CREATE TEMP TABLE learning_memory_commands(x integer)');app.commit()
  outcome=app.execute('SELECT public.purge_learning_memory(%s,%s,%s,%s)',(rev.business_key,receipt['manifest_sha256'],purge.business_key,purge.request_sha())).fetchone()[0];app.commit()
  assert json.loads(outcome)['purge_state_now']=='done'
  again=app.execute('SELECT public.purge_learning_memory(%s,%s,%s,%s)',(rev.business_key,receipt['manifest_sha256'],purge.business_key,purge.request_sha())).fetchone()[0];assert again==outcome;app.commit()
 after=snapshot(conn)
 assert not after['learning_memory_bodies'] and len(after['learning_memory_revisions'])==2
 for t in before:
  if t not in ('learning_memories','learning_memory_bodies','learning_memory_commands'):assert before[t]==after[t],t
 passed('V18/V19 临时同名对象不改目标，精确清理与同键回放一次效果',memory_id=mid,bodies_before=2,bodies_after=0,versions_retained=2,cleanup_receipts=conn.execute("SELECT count(*) FROM learning_memory_commands WHERE action='purge'").fetchone()[0])
 report['core_sha_missing_branch']={'status':'NOT_RUN','executed':False,'reason':'真实PG17核心sha256已存在；不删除pg_catalog伪造缺失环境'}
 report['new_objects_catalog']=catalog(conn)

def run(mode):
 control=Control();control.reserve('entry',{'name':'migration-'+mode});start=time.monotonic();docker=OwnedDocker(control);resource=None
 report={'status':'FAIL','executed':True,'mode':mode,'cases':[]}
 def passed(name,**details):
  report['cases'].append({'name':name,'status':'PASS','executed':True,**details});atomic_json(EVIDENCE/('migration-'+mode+'-checkpoint.json'),report)
 try:
  slot=2 if mode.startswith('upgrade') else 3;matches=[r for r in control.load()['resources'] if r['slot']==slot]
  if mode.endswith('-resume'):
   if len(matches)!=1:raise RuntimeError('续作资源缺失')
   resource=matches[0]
  else:
   if matches:raise RuntimeError('该根只可首次运行；续作必须明确使用持久断点，不能重建')
   resource=docker.create(slot)
  if mode=='fault-resume':
   prior=max([json.loads(f.read_text(encoding='utf-8')) for f in EVIDENCE.glob('migration-fault*-result.json')],key=lambda x:len(x['cases']))
   report['cases']=prior['cases'];report['inherited_root13_cases']=len(prior['cases'])
  docker.start(resource);admin=docker.admin_dsn(resource)
  end=time.monotonic()+30
  while True:
   try:conn=psycopg.connect(admin,autocommit=True,connect_timeout=2);break
   except psycopg.Error:
    if time.monotonic()>end:raise
    time.sleep(.1)
  with conn:
   conn.execute("SET statement_timeout='15s'");conn.execute("SET lock_timeout='3s'")
   report['server']=conn.execute("SELECT version(),current_setting('server_encoding'),encode(sha256(convert_to('abc','UTF8')),'hex')").fetchone()
   if not mode.endswith('-resume'):
    for migration in sorted((ROOT/'backend/migrations').glob('*.sql')):
     if not migration.name.startswith('010'):conn.execute(migration.read_text(encoding='utf-8-sig'),prepare=False)
   password=secrets.token_urlsafe(32);denied=secrets.token_urlsafe(32);SECRET_VALUES.update([password,denied])
   if mode.endswith('-resume'):
    conn.execute(sql.SQL('ALTER ROLE retrolume_task103_app PASSWORD {}').format(sql.Literal(password)))
    conn.execute(sql.SQL('ALTER ROLE retrolume_task103_denied PASSWORD {}').format(sql.Literal(denied)))
   else:grants(conn,password,denied)
   dsn=f"postgresql://retrolume_task103_app:{quote(password,safe='')}@127.0.0.1:{resource['port']}/{resource['database']}"
   denied_dsn=f"postgresql://retrolume_task103_denied:{quote(denied,safe='')}@127.0.0.1:{resource['port']}/{resource['database']}"
   if mode=='upgrade':upgrade(conn,dsn,report,passed)
   elif mode=='upgrade-resume':resume_upgrade(conn,dsn,report,passed)
   else:fault(conn,dsn,denied_dsn,report,passed)
   report['status']='PASS'
 except BaseException as exc:
  report.update(error_type=type(exc).__name__,message=redact(str(exc)),sqlstate=getattr(exc,'sqlstate',None))
  (EVIDENCE/('migration-'+mode+'-error.txt')).write_bytes(redact(__import__('traceback').format_exc()).encode())
 finally:
  control.charge('real',time.monotonic()-start,{'name':'migration-'+mode});clean=time.monotonic()
  if resource:
   try:report['cleanup']=docker.stop(resource)
   except BaseException as exc:report['cleanup_unconfirmed']=type(exc).__name__;report['status']='FAIL'
  control.charge('cleanup',time.monotonic()-clean,{'name':'migration-'+mode});atomic_json(EVIDENCE/('migration-'+mode+'-result.json'),report)
 print(json.dumps({'status':report['status'],'cases':len(report['cases']),'error':report.get('message')},ensure_ascii=False))
 return 0 if report['status']=='PASS' else 1
if __name__=='__main__':sys.exit(run(sys.argv[1]))
