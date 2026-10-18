"""沿root19真实持久断点，仅补失效窗剩余断言与尚未执行的窗口。"""
from __future__ import annotations
import asyncio,json,os,secrets,sys,time,threading
from uuid import uuid4
from urllib.parse import quote
import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from .control import Control,EVIDENCE,atomic_json,redact,SECRET_VALUES
from .resources import OwnedDocker
from .windows_normal import config

def run():
 control=Control();control.reserve('entry',{'name':'integration-resume'});start=time.monotonic();docker=OwnedDocker(control)
 resource=next(r for r in control.load()['resources'] if r['slot']==1)
 existing='--existing-only' in sys.argv
 prior=json.loads((EVIDENCE/('failures/root20-integration-resume-result.json' if existing else 'failures/root19-integration-remaining-result.json')).read_text(encoding='utf-8'))
 report={'status':'FAIL','executed':True,'cases':prior['cases'],'inherited_root19_cases':len(prior['cases'])}
 def passed(name,**values):
  report['cases'].append({'name':name,'status':'PASS','executed':True,**values});atomic_json(EVIDENCE/'integration-resume-checkpoint.json',report)
 try:
  docker.start(resource);admin=docker.admin_dsn(resource);password=secrets.token_urlsafe(32);SECRET_VALUES.add(password)
  with psycopg.connect(admin,autocommit=True) as c:c.execute(sql.SQL('ALTER ROLE retrolume_task103_app PASSWORD {}').format(sql.Literal(password)))
  dsn=f"postgresql://retrolume_task103_app:{quote(password,safe='')}@127.0.0.1:{resource['port']}/{resource['database']}"
  cfg=EVIDENCE/'workspace/remaining-config.json';atomic_json(cfg,config());key=secrets.token_urlsafe(24);SECRET_VALUES.add(key)
  os.environ.update(RETROLUME_DATA_DIR=str(EVIDENCE/'workspace/data'),RETROLUME_BACKUP_DIR=str(EVIDENCE/'workspace/backup'),RETROLUME_DATABASE_URL=dsn,RETROLUME_ACTIVITY_CONFIG=str(cfg),RETROLUME_TASK103_SYNTHETIC_KEY=key)
  from app.main import create_app
  from app.runtime import psycopg_compatible_loop_factory
  from app.worker.session import SessionConfig
  from app.memory.contracts import MemoryCommandInput
  from app.memory.service import MemoryService
  from fastapi.testclient import TestClient
  app=create_app();app.state.teaching_session_config=SessionConfig(window_seconds=20,request_timeout_seconds=2,stop_grace_seconds=2)
  SECRET_VALUES.add(app.state.session_token);ledger=app.state.activities_ledger;memory=MemoryService(ledger)
  def ar(coro):
   with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:return runner.run(coro)
  with TestClient(app,backend_options={'loop_factory':psycopg_compatible_loop_factory}) as client:
   headers={'x-retrolume-session':app.state.session_token,'origin':'http://testserver'}
   def req(path,body=None,status=200):
    r=client.get(path,headers=headers) if body is None else client.post(path,json=body,headers=headers);assert r.status_code==status,(path,r.status_code,r.json());return r.json()
   def workspace(aid):return req(f'/api/activities/{aid}/teaching/workspace')
   def cmd(aid,action,body):
    v=workspace(aid);return {'business_key':str(uuid4()),'action':action,'expected_revision':v['head']['revision'],'expected_goal_version':v['head']['goal_version'],'expected_scope_revision':1,'body':body}
   def check(aid,phase):
    with psycopg.connect(dsn,row_factory=dict_row) as c:
     row=c.execute('SELECT state,dispatch_started_at FROM activity_operations WHERE activity_id=%s',(aid,)).fetchone()
     n=c.execute("SELECT (SELECT count(*) FROM activity_operation_results WHERE activity_id=%s) AS results,(SELECT count(*) FROM teaching_records WHERE activity_id=%s AND kind<>'goal') AS derived",(aid,aid)).fetchone()
     budget=c.execute('SELECT requests_reserved,cost_reserved_microunits,tools_reserved,running_reserved_seconds,running_settled_seconds FROM activities WHERE id=%s',(aid,)).fetchone()
    assert n=={'results':0,'derived':0},n
    assert row['dispatch_started_at'] is None if phase=='after_admit' else row['dispatch_started_at'] is not None and row['state']=='unknown',row
    b=list(budget.values());assert b[:4]==[1,1000,0,0],b
    passed('V14 真实'+phase+'窗断言完成',activity_id=aid,operation=row,results=n,budgets=b)
   if existing:
    from app.capabilities.contracts import AdmissionPermit,LedgerOutcome,LedgerDisposition,RecordOutcome
    ready=max((EVIDENCE/'workspace/races').glob('before_result-*.ready.json'),key=lambda f:f.stat().st_mtime_ns)
    race_aid=json.loads(ready.read_text(encoding='utf-8'))['activity_id']
    with psycopg.connect(dsn,row_factory=dict_row) as c:
     op=c.execute('SELECT admission_id,operation_id,executor_id,state FROM activity_operations WHERE activity_id=%s',(race_aid,)).fetchone()
    assert op['state']=='dispatched',op
    permit=AdmissionPermit(str(op['admission_id']),op['operation_id'],op['executor_id'])
    assert ar(ledger.record_outcome(permit,LedgerOutcome(LedgerDisposition.UNKNOWN,error_code='memory_dependency_invalid'))) is RecordOutcome.RECORDED
    check(race_aid,'before_result');sup=control.load()['counts']['sup'];workspace(race_aid)
    receipt=req(f"/api/activities/{race_aid}/teaching/commands/{op['operation_id'].split('.')[1]}")
    assert receipt['status']=='unknown' and receipt['retry_policy']=='read_only' and control.load()['counts']['sup']==sup
    passed('V14 失效后显式UNKNOWN诊断可写，GET不重发，预留不退',activity_id=race_aid,status=receipt['status'],sup_delta=0,previous_sup_root='real-20-integration-resume')
   else:
    ready=max((EVIDENCE/'workspace/races').glob('after_admit-*.ready.json'),key=lambda f:f.stat().st_mtime_ns)
    aid=json.loads(ready.read_text(encoding='utf-8'))['activity_id'];check(aid,'after_admit')
    with psycopg.connect(dsn) as c:source=str(c.execute('SELECT source_id FROM activity_scope_sources WHERE activity_id=%s',(aid,)).fetchone()[0])
    bg=str(uuid4());req('/api/memories/commands',{'business_key':str(uuid4()),'memory_id':bg,'expected_revision':0,'action':'save','body':{'kind':'self_report','title':'mark后失效背景','text':'受控合成，旧请求不得新写'}})
    view=req('/api/memories/'+bg);race_aid=str(uuid4());req('/api/activities',{'activity_id':race_aid,'source_ids':[source],'memory_selection':{'confirmed':True,'entries':[{k:view[k] for k in ['memory_id','revision','version','body_sha256']}]}})
    req(f'/api/activities/{race_aid}/teaching/commands',cmd(race_aid,'goal',{'goal':'速度平均值','self_report':None,'domain':None,'seed_operation_id':None,'seed_payload_sha256':None}))
    plan=cmd(race_aid,'plan',{'confirmed':True,'correction_record_id':None,'retry_of':None})
    marker=EVIDENCE/('workspace/races/before_result-'+uuid4().hex)
    os.environ['RETROLUME_TASK103_RACE']=json.dumps({'phase':'before_result','activity_id':race_aid,'path':str(marker)})
    actor_result={}
    def actor():
     try:
      end=time.monotonic()+12
      while not marker.with_suffix('.ready.json').exists():
       if time.monotonic()>end:raise RuntimeError('race ready absent')
       time.sleep(.01)
      row=ar(ledger.read_memory_snapshot(bg));imp=ar(ledger.preview_memory_change(bg,row['revision'],'revise'))
      ar(memory.submit_command(MemoryCommandInput(business_key=str(uuid4()),memory_id=bg,expected_revision=row['revision'],action='revise',body={'kind':'self_report','title':'在途变化','text':'已经mark，拒新正文','base_body_sha256':row['body_sha256'],'impact_token':imp['impact_token']})))
      actor_result['changed']=True
     except BaseException as exc:actor_result['error']=redact(str(exc))
     finally:atomic_json(marker.with_suffix('.release.json'),actor_result)
    thread=threading.Thread(target=actor);thread.start();sup=control.load()['counts']['sup'];outcome=req(f'/api/activities/{race_aid}/teaching/commands',plan);thread.join(timeout=15);os.environ.pop('RETROLUME_TASK103_RACE',None)
    assert not thread.is_alive() and actor_result.get('changed'),actor_result
    assert control.load()['counts']['sup']==sup+1
    check(race_aid,'before_result');reads_sup=control.load()['counts']['sup'];workspace(race_aid);req(f'/api/activities/{race_aid}/teaching/commands/{plan["business_key"]}');assert control.load()['counts']['sup']==reads_sup
    passed('V14 已mark不声称撤回，UNKNOWN后GET零重发',activity_id=race_aid,status=outcome['status'],sup_delta=1,actor=actor_result)
   old_case=next(x for x in report['cases'] if x['name']=='V17 purged重建拒绝、不复活');m1=old_case['memory_id'];old_aid=old_case['activity_id']
   with psycopg.connect(admin,autocommit=True) as c:c.execute('ALTER TABLE public.learning_memories RENAME TO task103_unavailable_memories')
   try:
    unavailable=workspace(old_aid);assert unavailable['memory_invalid'] and not unavailable['nodes']
    req('/api/memories/'+m1,status=503)
   finally:
    with psycopg.connect(admin,autocommit=True) as c:c.execute('ALTER TABLE public.task103_unavailable_memories RENAME TO learning_memories')
   detail=req('/api/memories/'+m1);assert detail['state']=='revoked' and detail['body'] is None
   passed('V23 当前墓碑权威缺失失败关闭，在线重开不复活',activity_id=old_aid,memory_id=m1,missing_status=503)
  report['status']='PASS'
 except BaseException as exc:
  report.update(error_type=type(exc).__name__,message=redact(str(exc)));(EVIDENCE/'integration-resume-error.txt').write_bytes(redact(__import__('traceback').format_exc()).encode())
 finally:
  os.environ.pop('RETROLUME_TASK103_RACE',None);control.charge('real',time.monotonic()-start,{'name':'integration-resume'});clean=time.monotonic()
  try:report['cleanup']=docker.stop(resource)
  except BaseException as exc:report['cleanup_unconfirmed']=type(exc).__name__;report['status']='FAIL'
  control.charge('cleanup',time.monotonic()-clean,{'name':'integration-resume'});atomic_json(EVIDENCE/'integration-resume-result.json',report)
 print(json.dumps({'status':report['status'],'cases':len(report['cases']),'error':report.get('message')},ensure_ascii=False))
 return 0 if report['status']=='PASS' else 1
if __name__=='__main__':sys.exit(run())
