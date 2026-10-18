"""pg3最终函数下精确新目标的物理缺正文与不可读数据库清理负例。"""
from __future__ import annotations
import json,os,sys,time
from uuid import uuid4
import psycopg
from .common import owned_start,forward,configure,app_client,ar,snapshot,digest
from .control import Control,EVIDENCE,atomic_json,redact

class SampleRollback(Exception):pass

def run():
 control=Control();docker=None;resource=None;name=os.environ['RETROLUME_TASK103_C01_RUN']
 report={'status':'FAIL','executed':True,'cases':[],'objects':{}}
 def passed(title,**values):
  report['cases'].append({'name':title,'status':'PASS','executed':True,**values});atomic_json(EVIDENCE/'cleanup-gaps-checkpoint.json',report)
 try:
  docker,resource,admin=owned_start(3)
  with psycopg.connect(admin,autocommit=True) as conn:forward(conn,'pg3')
  dsn,cfg=configure(admin,resource,'cleanup-gaps');app,client=app_client();ledger=app.state.activities_ledger
  from app.memory.contracts import MemoryCommandInput
  from app.memory.service import MemoryService
  mid=str(uuid4());save=MemoryCommandInput(business_key=str(uuid4()),memory_id=mid,expected_revision=0,action='save',
   body={'kind':'self_report','title':'C01物理缺正文与断库目标','text':'只属于本轮合成目标的待清理正文'})
  ar(MemoryService(ledger).submit_command(save));view=ar(ledger.read_memory_snapshot(mid));impact=ar(ledger.preview_memory_change(mid,1,'revoke'))
  rev=MemoryCommandInput(business_key=str(uuid4()),memory_id=mid,expected_revision=1,action='revoke',
   body={'impact_token':impact['impact_token'],'confirm_revoke':True,'purge_memory_content':True})
  receipt=ar(ledger.apply_memory_command(rev));assert receipt['purge_state_now']=='pending'
  purge=MemoryCommandInput(business_key=str(uuid4()),memory_id=mid,expected_revision=2,action='purge',
   body={'revocation_key':rev.business_key,'manifest_sha256':receipt['manifest_sha256'],'confirm_memory_cleanup':True})
  report['objects'].update(memory_id=mid,save_key=save.business_key,revoke_key=rev.business_key,manifest_sha256=receipt['manifest_sha256'],purge_key=purge.business_key,
   body_target={'memory_id':mid,'version':1,'body_sha256':view['body_sha256']})
  with psycopg.connect(admin,autocommit=True) as conn:
   baseline=snapshot(conn);catalog_before=__import__('tests.fixtures.task103.migration_cleanup',fromlist=['catalog']).catalog(conn)
   state=None;reason=None
   try:
    with conn.transaction():
     # 只有新UUID/version/hash目标；触发器禁用/物理删除/重新启用全在同一回滚样本内。
     conn.execute('ALTER TABLE public.learning_memory_bodies DISABLE TRIGGER memory_body_integrity')
     deleted=conn.execute("DELETE FROM public.learning_memory_bodies b USING public.learning_memory_revisions r WHERE b.memory_id=%s AND b.version=1 AND r.memory_id=b.memory_id AND r.version=b.version AND r.body_sha256=%s AND encode(sha256(convert_to(b.body,'UTF8')),'hex')=%s RETURNING b.memory_id,b.version",(mid,view['body_sha256'],view['body_sha256'])).fetchall()
     assert len(deleted)==1
     conn.execute('ALTER TABLE public.learning_memory_bodies ENABLE TRIGGER memory_body_integrity')
     conn.execute('SET LOCAL ROLE retrolume_task103_app')
     assert conn.execute('SELECT current_user').fetchone()[0]=='retrolume_task103_app'
     try:
      with conn.transaction():conn.execute('SELECT public.purge_learning_memory(%s,%s,%s,%s)',(rev.business_key,receipt['manifest_sha256'],purge.business_key,purge.request_sha()))
     except psycopg.Error as exc:state=exc.sqlstate;reason=exc.diag.message_primary
     assert state and '清理集合不符' in reason,(state,reason)
     assert conn.execute('SELECT state,purge_state FROM learning_memories WHERE memory_id=%s',(mid,)).fetchone()==('revoked','pending')
     assert conn.execute('SELECT count(*) FROM learning_memory_commands WHERE business_key=%s',(purge.business_key,)).fetchone()[0]==0
     raise SampleRollback()
   except SampleRollback:pass
   assert snapshot(conn)==baseline and __import__('tests.fixtures.task103.migration_cleanup',fromlist=['catalog']).catalog(conn)==catalog_before
   passed('V18 普通app调用最终清理函数，物理缺正文拒绝/墓碑pending/0新收据',sqlstate=state,reason=reason,
    target=report['objects']['body_target'],exact_delete_count=1,before_sha=digest(baseline),after_sha=digest(snapshot(conn)),triggers_and_rows_restored=True)
   atomic_json(EVIDENCE/'cleanup-gaps-before-disconnect.json',{'rows_sha256':digest(baseline),'catalog_sha256':digest(catalog_before),'target':report['objects']})
  # 不可读是真实停止本卡pg3；不改客户端资格或伪造数据库错误。
  clean=time.monotonic();report['fault_stop']=docker.stop(resource);control.charge('cleanup',time.monotonic()-clean,{'name':'cleanup-gaps-fault-stop'})
  failure=None
  try:ar(MemoryService(ledger).submit_command(purge))
  except BaseException as exc:failure={'type':type(exc).__name__,'message':redact(str(exc))}
  assert failure and failure['type']=='AdmissionUnavailable',failure
  docker,resource,admin=owned_start(3)
  with psycopg.connect(admin,autocommit=True) as conn:
   assert snapshot(conn)==baseline and __import__('tests.fixtures.task103.migration_cleanup',fromlist=['catalog']).catalog(conn)==catalog_before
   assert conn.execute('SELECT state,purge_state FROM learning_memories WHERE memory_id=%s',(mid,)).fetchone()==('revoked','pending')
   assert conn.execute('SELECT count(*) FROM learning_memory_commands WHERE business_key=%s',(purge.business_key,)).fetchone()[0]==0
   assert conn.execute('SELECT count(*) FROM learning_memory_bodies WHERE memory_id=%s AND version=1',(mid,)).fetchone()[0]==1
   assert ar(ledger.read_memory_snapshot(mid))['body'] is None
   passed('V18 实际DB不可读，清理未确认；重启只读核墓碑/正文/旧收据保留',failure=failure,pending=True,
    before_sha=digest(baseline),after_sha=digest(snapshot(conn)),no_auto_retry=True,no_new_receipt=True,revoked_body_suppressed=True)
  report['status']='PASS'
 except BaseException as exc:
  report.update(error_type=type(exc).__name__,message=redact(str(exc)));(EVIDENCE/('cleanup-gaps-error-'+name+'.txt')).write_bytes(redact(__import__('traceback').format_exc()).encode())
 finally:
  clean=time.monotonic()
  if docker and resource:
   try:report['cleanup']=docker.stop(resource)
   except BaseException as exc:report['cleanup_unconfirmed']=type(exc).__name__;report['status']='FAIL'
  control.charge('cleanup',time.monotonic()-clean,{'name':'cleanup-gaps'});atomic_json(EVIDENCE/('cleanup-gaps-result-'+name+'.json'),report);atomic_json(EVIDENCE/'cleanup-gaps-result.json',report)
 print(json.dumps({'status':report['status'],'cases':len(report['cases']),'error':report.get('message')},ensure_ascii=False));return 0 if report['status']=='PASS' else 1
if __name__=='__main__':sys.exit(run())
