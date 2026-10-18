"""最终仓储字节的恢复、传播、快照与真实监督失效窗口组合。"""
from __future__ import annotations
import asyncio,io,json,os,secrets,sys,time,threading
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote
from uuid import uuid4
import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from .control import Control,EVIDENCE,ROOT,atomic_json,redact,SECRET_VALUES
from .resources import OwnedDocker
from .windows_normal import config,MATERIAL

def run():
 control=Control();control.reserve('entry',{'name':'integration-remaining'});start=time.monotonic()
 docker=OwnedDocker(control);resource=next(r for r in control.load()['resources'] if r['slot']==1)
 report={'status':'FAIL','executed':True,'cases':[]}
 def passed(name,**values):
  report['cases'].append({'name':name,'status':'PASS','executed':True,**values});atomic_json(EVIDENCE/'integration-remaining-checkpoint.json',report)
 try:
  docker.start(resource);admin=docker.admin_dsn(resource);password=secrets.token_urlsafe(32);SECRET_VALUES.add(password)
  with psycopg.connect(admin,autocommit=True) as conn:conn.execute(sql.SQL('ALTER ROLE retrolume_task103_app PASSWORD {}').format(sql.Literal(password)))
  dsn=f"postgresql://retrolume_task103_app:{quote(password,safe='')}@127.0.0.1:{resource['port']}/{resource['database']}"
  data=EVIDENCE/'workspace/data';backup=EVIDENCE/'workspace/backup';cfg=EVIDENCE/'workspace/remaining-config.json';atomic_json(cfg,config())
  key=secrets.token_urlsafe(24);SECRET_VALUES.add(key)
  os.environ.update(RETROLUME_DATA_DIR=str(data),RETROLUME_BACKUP_DIR=str(backup),RETROLUME_DATABASE_URL=dsn,RETROLUME_ACTIVITY_CONFIG=str(cfg),RETROLUME_TASK103_SYNTHETIC_KEY=key)
  from app.main import create_app
  from app.runtime import psycopg_compatible_loop_factory
  from app.worker.session import SessionConfig
  from app.materials.repository import PostgresMaterials
  from app.memory.contracts import MemoryCommandInput
  from app.memory.service import MemoryService
  from app.learning.teaching_service import TeachingService
  from app.learning.teaching_contracts import TeachingCommandInput,TeachingRefusal
  from app.learning.contracts import canonical,sha
  from fastapi.testclient import TestClient
  app=create_app();app.state.teaching_session_config=SessionConfig(window_seconds=20,request_timeout_seconds=2,stop_grace_seconds=2)
  SECRET_VALUES.add(app.state.session_token);ledger=app.state.activities_ledger;memory=MemoryService(ledger)
  teaching=TeachingService(ledger,app.state.materials,app.state.originals,session_config=app.state.teaching_session_config)
  def ar(value):
   with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:return runner.run(value)
  original=app.state.originals.put(io.BytesIO(MATERIAL.encode()),max_bytes=5242880)
  materials=PostgresMaterials(dsn);source=materials.save(source_id=None,expected_version=None,filename='task103-final-integration.md',format='md',sha256=original.sha256,size=original.size)
  with TestClient(app,backend_options={'loop_factory':psycopg_compatible_loop_factory}) as client:
   headers={'x-retrolume-session':app.state.session_token,'origin':'http://testserver'}
   def req(path,body=None,status=200):
    r=client.get(path,headers=headers) if body is None else client.post(path,json=body,headers=headers)
    assert r.status_code==status,(path,r.status_code,r.json());return r.json()
   def detail(mid):return req('/api/memories/'+mid)
   def save(text='我仍容易把分钟当秒',kind='self_report'):
    mid=str(uuid4());body={'business_key':str(uuid4()),'memory_id':mid,'expected_revision':0,'action':'save','body':{'kind':kind,'title':'最终合成背景','text':text}}
    return mid,req('/api/memories/commands',body)
   def revise(mid,text):
    row=detail(mid);imp=req(f"/api/memories/{mid}/impact?expected_revision={row['revision']}&action=revise")
    return req('/api/memories/commands',{'business_key':str(uuid4()),'memory_id':mid,'expected_revision':row['revision'],'action':'revise',
      'body':{'kind':row['claim_kind'],'title':'最终修订背景','text':text,'base_body_sha256':row['body_sha256'],'impact_token':imp['impact_token']}})
   def activity(mids=(),entries=None,aid=None):
    aid=aid or str(uuid4());body={'activity_id':aid,'source_ids':[source['id']]}
    if mids or entries:
     entries=entries or [{k:detail(mid)[k] for k in ['memory_id','version','revision','body_sha256']} for mid in mids]
     body['memory_selection']={'confirmed':True,'entries':entries}
    req('/api/activities',body);return aid
   def workspace(aid):return req(f'/api/activities/{aid}/teaching/workspace')
   def command(aid,action,body):
    view=workspace(aid);return {'business_key':str(uuid4()),'expected_revision':view['head']['revision'],'expected_goal_version':view['head']['goal_version'],
     'expected_scope_revision':1,'action':action,'body':body}
   def submit(aid,action,body):return req(f'/api/activities/{aid}/teaching/commands',command(aid,action,body))
   def goal(aid):submit(aid,'goal',{'goal':'平均速度独立表现','self_report':None,'domain':None,'seed_operation_id':None,'seed_payload_sha256':None})
   def budget(aid):
    with psycopg.connect(dsn) as c:return c.execute('SELECT requests_reserved,cost_reserved_microunits,tools_reserved,running_reserved_seconds,running_settled_seconds FROM activities WHERE id=%s',(aid,)).fetchone()
   endpoint='/api/memories/commands'
   for same_key in [True,False]:
    mid=str(uuid4());key=str(uuid4());body={'business_key':key,'memory_id':mid,'expected_revision':0,'action':'save','body':{'kind':'self_report','title':'并发首次保存','text':'相同语义只产生一次效果'}}
    bodies=[body,{**body,'business_key':key if same_key else str(uuid4())}]
    with ThreadPoolExecutor(max_workers=2) as pool:responses=list(pool.map(lambda b:client.post(endpoint,json=b,headers=headers),bodies))
    assert [r.status_code for r in responses]==[200,200],[r.json() for r in responses]
    with psycopg.connect(dsn) as c:
     n=c.execute('SELECT count(*),count(*) FILTER(WHERE effect_applied) FROM learning_memory_commands WHERE memory_id=%s',(mid,)).fetchone()
     assert n==(1 if same_key else 2,1),n
    for b in bodies:assert req('/api/memories/commands/'+b['business_key'])['request_sha256']==responses[0].json()['request_sha256']
    passed('V10 同时首次保存'+('同键' if same_key else '不同键同槽')+'唯一效果与持久收据',memory_id=mid,statuses=[r.status_code for r in responses],commands=n[0],effects=n[1])
   m1,_=save();m2,_=save('我偏好先统一米和秒','preference');aid=activity([m1,m2]);goal(aid)
   invalid_entry={k:detail(m1)[k] for k in ['memory_id','version','revision','body_sha256']};invalid_entry['body_sha256']='f'*64
   bad=str(uuid4());r=client.post('/api/activities',json={'activity_id':bad,'source_ids':[source['id']],'memory_selection':{'confirmed':True,'entries':[invalid_entry]}},headers=headers);assert r.status_code==409
   with psycopg.connect(dsn) as c:assert c.execute('SELECT count(*) FROM activities WHERE id=%s',(bad,)).fetchone()[0]==0
   passed('V03 坏选择原子零创建',activity_id=bad,status=409)
   cmd=TeachingCommandInput.model_validate(command(aid,'plan',{'confirmed':True,'correction_record_id':None,'retry_of':None}))
   frozen,_=ar(teaching._freeze_model_context(aid,cmd,app.state.activity_config));accepted=ar(ledger.accept_teaching_command(aid,cmd,frozen));assert accepted.status=='accepted'
   with psycopg.connect(dsn) as c:context_before=c.execute('SELECT context_body FROM teaching_commands WHERE activity_id=%s AND business_key=%s',(aid,cmd.business_key)).fetchone()[0]
   sup=control.load()['counts']['sup'];plan=req(f'/api/activities/{aid}/teaching/commands',cmd.model_dump());assert plan['status']=='committed'
   replay=req(f'/api/activities/{aid}/teaching/commands',cmd.model_dump());assert replay['status']=='committed' and control.load()['counts']['sup']==sup+1
   with psycopg.connect(dsn) as c:assert c.execute('SELECT context_body FROM teaching_commands WHERE activity_id=%s AND business_key=%s',(aid,cmd.business_key)).fetchone()[0]==context_before
   assert 'messages' not in json.loads(context_before) and '我仍容易把分钟当秒' not in context_before
   passed('V04/V13 两种低信任背景，持久recipe有效恢复恰一SUP',activity_id=aid,sup_delta=1,frozen_sha=sha(context_before),selected=2,context_plaintext=False)
   view=workspace(aid);proposal=view['proposal']['record_id'];submit(aid,'accept_path',{'proposal_record_id':proposal})
   view=workspace(aid);exercise=submit(aid,'exercise',{'confirmed':True,'path_record_id':view['head']['path_record_id'],'node_id':'n1','purpose':'initial','parent_feedback_record_id':None,'retry_of':None})
   eid=workspace(aid)['head']['exercise_record_id'];answer=submit(aid,'answer',{'exercise_record_id':eid,'kind':'initial','text':'1m/s','supersedes_answer_record_id':None})
   evaluation=submit(aid,'evaluate',{'confirmed':True,'exercise_record_id':eid,'answer_record_id':answer['record_ids'][0]['record_id'],'correction_record_id':None,'retry_of':None})
   assert evaluation['status']=='committed';view=workspace(aid);pid=view['head']['reason_record_id'];preview=req(f'/api/activities/{aid}/teaching/records/{pid}/memory-preview')
   observed=str(uuid4());req(endpoint,{'business_key':str(uuid4()),'memory_id':observed,'expected_revision':0,'action':'save','body':{'kind':'learning_observation','title':'来源与上游有限观察','text':'仅一次独立答文','capture':preview['capture']}})
   obs=detail(observed);deps=obs['dependencies'];assert len([d for d in deps if d['dependency_kind']=='memory'])==2 and len([d for d in deps if d['dependency_kind']=='event'])>=4
   target=activity([observed]);goal(target);target_plan=submit(target,'plan',{'confirmed':True,'correction_record_id':None,'retry_of':None});assert target_plan['status']=='committed'
   passed('V01/V08 真实教学观察带来源/事件/已选上游闭包',memory_id=observed,origin_activity=aid,target_activity=target,dependencies=len(deps),kinds=[d['dependency_kind'] for d in deps])
   # 实际引用位置和原文支持分开核，不把背景当引用。
   with psycopg.connect(dsn,row_factory=dict_row) as c:
    row=c.execute("SELECT r.record_id,r.body_sha256,o.payload FROM teaching_records r JOIN activity_operation_results o USING(activity_id,operation_id) WHERE r.activity_id=%s AND r.kind='exercise'",(aid,)).fetchone()
   result=json.loads(row['payload'])['value']['result'];cid=result['reference_points'][0]['citations'][0]
   citation=req(f'/api/activities/{aid}/teaching/records/{eid}/citations/{cid}')
   assert '平均速度' in json.dumps(citation,ensure_ascii=False) and '120' in json.dumps(citation,ensure_ascii=False)
   oracle={'source_id':source['id'],'version_id':source['version_id'],'original_sha256':original.sha256,'citation_id':cid,'exercise_record_id':eid,
    'reference_value':'1m/s','position':citation,'judgment':'原文120米/120秒与题目/参考1米每秒一致；用户记忆无lc引用权。有限样本，不推供应商质量。'}
   atomic_json(EVIDENCE/'content-oracle-final.json',oracle);passed('V22 真实位置回查与冻结原文数值支持分别核',citation_id=cid,source_sha=original.sha256)
   # 保存观察后另一条用户答案后继使其失效，故意all-met不能修复旧观察。
   revised_answer=submit(aid,'answer',{'exercise_record_id':eid,'kind':'revision','text':'我不知道结果，尚不确定','supersedes_answer_record_id':answer['record_ids'][0]['record_id']})
   assert detail(observed)['body'] is None and workspace(target)['memory_invalid']
   negative=submit(aid,'evaluate',{'confirmed':True,'exercise_record_id':eid,'answer_record_id':revised_answer['record_ids'][0]['record_id'],'correction_record_id':None,'retry_of':None});assert negative['status']=='committed'
   view=workspace(aid);reason=view['reason']['body'];assert reason['support_checks'] and all(check.get('answer_status')!='matched' for check in reason['support_checks']),reason
   passed('V07/V22 答案后继失效；模型all-met与unknown答文不能作独立支持',origin_activity=aid,target_activity=target,support_checks=reason['support_checks'])
   # 容量与缺配置均须接受前失败；GET/旧v1不被偷偷变成模型背景。
   big1,_=save('a'*1024);big2,_=save('b'*1024);limited=activity([big1,big2]);goal(limited)
   cmd_big=command(limited,'plan',{'confirmed':True,'correction_record_id':None,'retry_of':None});sup_before=control.load()['counts']['sup']
   response=client.post(f'/api/activities/{limited}/teaching/commands',json=cmd_big,headers=headers);assert response.status_code in (409,413),response.json()
   with psycopg.connect(dsn) as c:assert c.execute("SELECT count(*) FROM teaching_commands WHERE activity_id=%s AND action='plan'",(limited,)).fetchone()[0]==0
   cfg_none=config();cfg_none['memory_context']=None;atomic_json(cfg,cfg_none)
   config_off=__import__('app.service_config',fromlist=['load_activity_config']).load_activity_config(cfg)
   plain_cmd=TeachingCommandInput.model_validate(command(limited,'plan',{'confirmed':True,'correction_record_id':None,'retry_of':None}))
   try:ar(teaching.submit_command(limited,plain_cmd,config_off));raise AssertionError('missing memory config accepted')
   except TeachingRefusal as exc:assert exc.code=='memory_not_configured',exc.code
   atomic_json(cfg,config());assert control.load()['counts']['sup']==sup_before
   passed('V04/V21 超记忆容量与缺配置均零accept/零SUP',activity_id=limited,sup_delta=0,capacity_error=response.json())
   # 同一SQL快照含资格和正文；透明profile只记录SQL，不保存参数。
   for tag,path in [('memory-detail','/api/memories/'+m1),('memory-list','/api/memories?limit=50'),('selection',f'/api/activities/{aid}/memory-selection'),
    ('workspace',f'/api/activities/{aid}/teaching/workspace'),('history',f'/api/activities/{aid}/teaching/history')]:
    os.environ['RETROLUME_TASK103_READ_TAG']=tag;req(path);os.environ.pop('RETROLUME_TASK103_READ_TAG',None)
   def read_snapshot(_):
    row=detail(m1)
    if row['body'] is not None:assert sha(canonical(row['body']))==row['body_sha256']
    return {'revision':row['revision'],'qualification':row['qualification'],'body_present':row['body'] is not None}
   with ThreadPoolExecutor(max_workers=3) as pool:
    futures=[pool.submit(read_snapshot,i) for i in range(8)];changed=revise(m1,'明确修订，旧选择不换版');reads=[f.result() for f in futures]
   assert all(r['revision'] in (1,2) for r in reads)
   passed('V09 并发修订读取完整前或后状态，正文hash同快照',memory_id=m1,reads=reads)
   budgets_before=budget(aid);immutable_before=None
   with psycopg.connect(dsn) as c:immutable_before=c.execute('SELECT record_id,body_sha256 FROM teaching_records WHERE activity_id=%s ORDER BY seq',(aid,)).fetchall()
   op=plan['operation_id'];assert workspace(aid)['memory_invalid']
   assert req(f'/api/activities/{aid}/teaching/records/{eid}')['public_body'] is None
   assert req(f'/api/activities/{aid}/teaching/commands/{cmd.business_key}')['qualification']=='memory_invalid'
   raw=ar(ledger.read_committed_result(aid,op));assert raw.payload is None
   operations=ar(ledger.list_operations(aid,limit=50));assert all(not r.payload_available for r in operations)
   seed=client.get(f'/api/activities/{aid}/teaching/seeds/{op}',headers=headers);assert seed.status_code in (404,409)
   cite_invalid=client.get(f'/api/activities/{aid}/teaching/records/{eid}/citations/{cid}',headers=headers);assert cite_invalid.status_code==409
   answer_raw=req(f'/api/activities/{aid}/teaching/records/{revised_answer["record_ids"][0]["record_id"]}');assert answer_raw['public_body']['text']=='我不知道结果，尚不确定'
   passed('V06/V16 全公开派生读面停用，用户原答仍能读',activity_id=aid,operations=len(operations),seed_status=seed.status_code,citation_status=cite_invalid.status_code,budget_before=list(budgets_before))
   # 旧终态确认仍可核；不消费或返还失效背景的调用预留。
   from app.capabilities.contracts import AdmissionPermit,LedgerOutcome,LedgerDisposition,RecordOutcome
   with psycopg.connect(dsn,row_factory=dict_row) as c:
    row=c.execute('SELECT o.*,r.payload,r.payload_format,r.payload_sha256 FROM activity_operations o JOIN activity_operation_results r USING(activity_id,operation_id) WHERE o.activity_id=%s AND o.operation_id=%s',(aid,op)).fetchone()
   permit=AdmissionPermit(str(row['admission_id']),op,row['executor_id'])
   outcome=LedgerOutcome(disposition=LedgerDisposition(row['disposition']),**{k:row[k] for k in ['error_code','remote_request_id','returned_model','finish_reason','prompt_tokens','completion_tokens','response_bytes','payload','payload_format','payload_sha256']})
   assert ar(ledger.record_outcome(permit,outcome)) is RecordOutcome.ALREADY_PRESENT
   assert budget(aid)==budgets_before
   passed('V14 失效后相同终态只确认，旧预算不改',activity_id=aid,confirmation='already_present')
   # 三个状态的进度重建门，清空的只是明确可重建投影。
   for stage in ['dependency_invalid','revoked_body_retained','purged']:
    if stage=='revoked_body_retained':
     row=detail(m1);imp=req(f"/api/memories/{m1}/impact?expected_revision={row['revision']}&action=revoke")
     rev=MemoryCommandInput(business_key=str(uuid4()),memory_id=m1,expected_revision=row['revision'],action='revoke',body={'impact_token':imp['impact_token'],'confirm_revoke':True,'purge_memory_content':True})
     rev_receipt=ar(ledger.apply_memory_command(rev));assert rev_receipt['purge_state_now']=='pending'
    if stage=='purged':ar(ledger.apply_memory_command(MemoryCommandInput(business_key=str(uuid4()),memory_id=m1,expected_revision=rev_receipt['revision_after'],action='purge',body={'revocation_key':rev.business_key,'manifest_sha256':rev_receipt['manifest_sha256'],'confirm_memory_cleanup':True})))
    with psycopg.connect(admin,autocommit=True) as c:c.execute("UPDATE teaching_heads SET projection='{}' WHERE activity_id=%s",(aid,))
    async def rebuild():
     async def action(c):
      head=(await (await c.execute('SELECT * FROM teaching_heads WHERE activity_id=%s',(aid,))).fetchone())
      return await ledger._teaching_rebuild_progress(c,aid,head)
     return await ledger._transaction(action)
    try:ar(rebuild());raise AssertionError('invalid rebuild resurrected')
    except TeachingRefusal as exc:assert exc.code=='memory_dependency_invalid'
    assert not workspace(aid)['nodes']
    passed('V17 '+stage+'重建拒绝、不复活',activity_id=aid,memory_id=m1)
   with psycopg.connect(dsn) as c:assert c.execute('SELECT record_id,body_sha256 FROM teaching_records WHERE activity_id=%s ORDER BY seq',(aid,)).fetchall()==immutable_before
   # 实际after-admit及已mark/response前两个窗口，不替换任何权威函数。
   for phase in ['after_admit','before_result']:
    bg,_=save('受控在途背景');race_aid=activity([bg]);goal(race_aid)
    race_cmd=command(race_aid,'plan',{'confirmed':True,'correction_record_id':None,'retry_of':None})
    marker=EVIDENCE/('workspace/races/'+phase+'-'+uuid4().hex);marker.parent.mkdir(exist_ok=True)
    os.environ['RETROLUME_TASK103_RACE']=json.dumps({'phase':phase,'activity_id':race_aid,'path':str(marker)})
    actor_result={}
    def actor():
     try:
      end=time.monotonic()+12
      while not marker.with_suffix('.ready.json').exists():
       if time.monotonic()>end:raise RuntimeError('race ready absent')
       time.sleep(.01)
      view=ar(ledger.read_memory_snapshot(bg));imp=ar(ledger.preview_memory_change(bg,view['revision'],'revise'))
      ar(memory.submit_command(MemoryCommandInput(business_key=str(uuid4()),memory_id=bg,expected_revision=view['revision'],action='revise',body={'kind':'self_report','title':'在途修订','text':'旧在途背景停用','base_body_sha256':view['body_sha256'],'impact_token':imp['impact_token']})))
      actor_result['changed']=True
     except BaseException as exc:actor_result['error']=redact(str(exc))
     finally:atomic_json(marker.with_suffix('.release.json'),actor_result)
    thread=threading.Thread(target=actor);thread.start();sup_before=control.load()['counts']['sup']
    response=req(f'/api/activities/{race_aid}/teaching/commands',race_cmd);thread.join(timeout=15);os.environ.pop('RETROLUME_TASK103_RACE',None)
    assert not thread.is_alive() and actor_result.get('changed'),actor_result
    with psycopg.connect(dsn,row_factory=dict_row) as c:
     op_row=c.execute('SELECT state,dispatch_started_at FROM activity_operations WHERE activity_id=%s',(race_aid,)).fetchone()
     counts=c.execute("SELECT (SELECT count(*) FROM activity_operation_results WHERE activity_id=%s) AS results,(SELECT count(*) FROM teaching_records WHERE activity_id=%s AND kind<>'goal') AS derived",(race_aid,race_aid)).fetchone()
    assert list(counts.values())==[0,0],counts
    if phase=='after_admit':assert op_row['dispatch_started_at'] is None
    else:assert op_row['dispatch_started_at'] is not None and op_row['state']=='unknown',op_row
    b=budget(race_aid);assert b[0]==1 and b[1]==1000 and b[2]==0 and b[3]==0,b
    reads_before=control.load()['counts']['sup'];workspace(race_aid);req(f'/api/activities/{race_aid}/teaching/commands/{race_cmd["business_key"]}');assert control.load()['counts']['sup']==reads_before
    passed('V14 真实'+phase+'失效窗口',activity_id=race_aid,actor=actor_result,status=response['status'],operation=op_row,new_payload=0,new_derived_facts=0,budget=list(b),sup_delta=control.load()['counts']['sup']-sup_before)
   # 当前墓碑表不可读/新结构残迹时失败关闭；恢复同一在线原表后仍保留墓碑。
   with psycopg.connect(admin,autocommit=True) as c:c.execute('ALTER TABLE public.learning_memories RENAME TO task103_unavailable_memories')
   try:
    disabled=workspace(aid);assert disabled['memory_invalid'] and not disabled['nodes']
    response=client.get('/api/memories/'+m1,headers=headers);assert response.status_code==503
   finally:
    with psycopg.connect(admin,autocommit=True) as c:c.execute('ALTER TABLE public.task103_unavailable_memories RENAME TO learning_memories')
   assert detail(m1)['state']=='revoked' and detail(m1)['body'] is None
   passed('V23 当前墓碑权威不可用隔离、在线重开后仍撤销',memory_id=m1,unavailable_status=503)
  report['status']='PASS'
 except BaseException as exc:
  report.update(error_type=type(exc).__name__,message=redact(str(exc)));(EVIDENCE/'integration-remaining-error.txt').write_bytes(redact(__import__('traceback').format_exc()).encode())
 finally:
  os.environ.pop('RETROLUME_TASK103_RACE',None);os.environ.pop('RETROLUME_TASK103_READ_TAG',None)
  control.charge('real',time.monotonic()-start,{'name':'integration-remaining'});clean=time.monotonic()
  try:report['cleanup']=docker.stop(resource)
  except BaseException as exc:report['cleanup_unconfirmed']=type(exc).__name__;report['status']='FAIL'
  control.charge('cleanup',time.monotonic()-clean,{'name':'integration-remaining'});atomic_json(EVIDENCE/'integration-remaining-result.json',report)
 print(json.dumps({'status':report['status'],'cases':len(report['cases']),'error':report.get('message')},ensure_ascii=False))
 return 0 if report['status']=='PASS' else 1
if __name__=='__main__':sys.exit(run())
