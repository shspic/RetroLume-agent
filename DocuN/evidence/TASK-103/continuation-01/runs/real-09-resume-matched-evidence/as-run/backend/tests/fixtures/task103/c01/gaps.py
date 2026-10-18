"""最终受影响后继、实际闭包约束与缺M6残迹；只使用新合成负例。"""
from __future__ import annotations
import io,json,os,sys,time
from uuid import uuid4
import psycopg
from psycopg import sql
from psycopg.rows import dict_row,tuple_row
from .common import owned_start,configure,app_client,ar,MATERIAL,snapshot,digest
from .control import Control,EVIDENCE,atomic_json,redact

class SampleRollback(Exception):pass

def snap(conn):
 previous=conn.row_factory
 try:conn.row_factory=tuple_row;return snapshot(conn)
 finally:conn.row_factory=previous

def insert(conn,table,row):
 conn.execute(sql.SQL('INSERT INTO public.{} ({}) VALUES ({})').format(sql.Identifier(table),
  sql.SQL(',').join(map(sql.Identifier,row)),sql.SQL(',').join(sql.Placeholder() for _ in row)),tuple(row.values()))

def run():
 control=Control();docker=None;resource=None;run_name=os.environ['RETROLUME_TASK103_C01_RUN']
 resume='--resume' in sys.argv
 report={'status':'FAIL','executed':True,'cases':[],'objects':{},'synthetic_sql_negative_only':True}
 if resume:
  previous=json.loads((EVIDENCE/'gaps-result.json').read_text(encoding='utf-8'))
  report['objects']=previous['objects'];report['resumed_from']='real-08-feedback-closure-residuals';report['prior_status']=previous['status']
 def passed(name,**data):
  report['cases'].append({'name':name,'status':'PASS','executed':True,**data});atomic_json(EVIDENCE/'gaps-checkpoint.json',report)
 try:
  docker,resource,admin=owned_start(1);dsn,cfg=configure(admin,resource,'gaps');app,client=app_client();ledger=app.state.activities_ledger
  from app.learning.contracts import canonical,sha
  from app.memory.contracts import order_dependencies,dependencies_digest
  from app.materials.repository import PostgresMaterials
  with client:
   headers={'x-retrolume-session':app.state.session_token,'origin':'http://testserver'}
   def req(path,body=None,status=200):
    r=client.get(path,headers=headers) if body is None else client.post(path,json=body,headers=headers)
    assert r.status_code==status,(path,r.status_code,r.json());return r.json()
   def ws(aid):return req(f'/api/activities/{aid}/teaching/workspace')
   def detail(mid):return req('/api/memories/'+mid)
   def submit(aid,action,body):
    view=ws(aid);command={'business_key':str(uuid4()),'expected_revision':view['head']['revision'],
     'expected_goal_version':view['head']['goal_version'],'expected_scope_revision':1,'action':action,'body':body}
    receipt=req(f'/api/activities/{aid}/teaching/commands',command)
    atomic_json(EVIDENCE/'receipts'/(command['business_key']+'.json'),receipt);return receipt
   def activity(source,mids=()):
    aid=str(uuid4());body={'activity_id':aid,'source_ids':[source['id']]}
    if mids:body['memory_selection']={'confirmed':True,'entries':[{k:detail(mid)[k] for k in ['memory_id','version','revision','body_sha256']} for mid in mids]}
    req('/api/activities',body);return aid
   def save(title):
    mid=str(uuid4());req('/api/memories/commands',{'business_key':str(uuid4()),'memory_id':mid,'expected_revision':0,'action':'save',
     'body':{'kind':'preference','title':title,'text':'先核对资料中的米和秒'}});return mid
   def capture(aid,title):
    pid=ws(aid)['head']['reason_record_id'];preview=req(f'/api/activities/{aid}/teaching/records/{pid}/memory-preview');mid=str(uuid4())
    req('/api/memories/commands',{'business_key':str(uuid4()),'memory_id':mid,'expected_revision':0,'action':'save',
     'body':{'kind':'learning_observation','title':title,'text':'最终批的有限观察','capture':preview['capture']}});return mid,preview['capture']
   def evaluate(aid,eid,answer,correction=None):
    receipt=submit(aid,'evaluate',{'confirmed':True,'exercise_record_id':eid,'answer_record_id':answer,'correction_record_id':correction,'retry_of':None})
    assert receipt['status']=='committed',receipt
    assert ws(aid)['budgets']['running_reserved_seconds']==0
    return receipt['record_ids'][0]['record_id']
   def initial(aid):
    submit(aid,'goal',{'goal':'平均速度与单位','self_report':None,'domain':None,'seed_operation_id':None,'seed_payload_sha256':None})
    assert submit(aid,'plan',{'confirmed':True,'correction_record_id':None,'retry_of':None})['status']=='committed'
    submit(aid,'accept_path',{'proposal_record_id':ws(aid)['proposal']['record_id']})
    assert submit(aid,'exercise',{'confirmed':True,'path_record_id':ws(aid)['head']['path_record_id'],'node_id':'n1',
     'purpose':'initial','parent_feedback_record_id':None,'retry_of':None})['status']=='committed'
    eid=ws(aid)['head']['exercise_record_id'];answer=submit(aid,'answer',{'exercise_record_id':eid,'kind':'initial','text':'1m/s','supersedes_answer_record_id':None})['record_ids'][0]['record_id']
    return eid,answer,evaluate(aid,eid,answer)
   materials=PostgresMaterials(dsn);original=app.state.originals.put(io.BytesIO(MATERIAL.encode()),max_bytes=5242880)
   if resume:source=report['objects']['source'];pref=report['objects']['pref'];aid=report['objects']['activity']
   else:
    source=materials.save(source_id=None,expected_version=None,filename='task103-c01-gaps.md',format='md',sha256=original.sha256,size=original.size)
    pref=save('C01最终后继偏好');aid=activity(source,[pref]);report['objects'].update(source=source,activity=aid,pref=pref)
   before_sup=control.load()['counts']['sup'];eid,answer,feedback1=initial(aid);first,_=capture(aid,'C01最终同答观察一')
   unrelated=activity(source);submit(unrelated,'goal',{'goal':'无关本地事件','self_report':None,'domain':None,'seed_operation_id':None,'seed_payload_sha256':None})
   assert detail(first)['qualification']=='current'
   correction1=submit(aid,'correct',{'target_record_id':feedback1,'text':'核对本次反馈','disputed_dimensions':['value']})['record_ids'][0]['record_id']
   feedback2=evaluate(aid,eid,answer,correction1);assert feedback2!=feedback1 and detail(first)['body'] is None
   second,_=capture(aid,'C01最终同答观察二')
   correction2=submit(aid,'correct',{'target_record_id':feedback1,'text':'追加早前反馈的注记','disputed_dimensions':['value']})['record_ids'][0]['record_id']
   assert detail(second)['qualification']=='current'
   feedback3=evaluate(aid,eid,answer,correction2);assert feedback3 not in (feedback1,feedback2) and detail(second)['body'] is None
   parent,_=capture(aid,'C01最终闭包上游');assert detail(parent)['qualification']=='current'
   passed('V07 同answer新feedback使关联观察失效，无关活动与旧feedback注记不误伤',activity=aid,answer=answer,
    feedback_ids=[feedback1,feedback2,feedback3],memory_ids=[first,second,parent],unrelated=unrelated,sup_delta=control.load()['counts']['sup']-before_sup)
   child_aid=activity(source,[parent]);initial(child_aid);child,valid_capture=capture(child_aid,'C01最终闭包下游')
   assert detail(child)['qualification']=='current'
   report['objects'].update(parent=parent,child=child,child_activity=child_aid,unrelated=unrelated)
   passed('V08 最终三函数下真实两层闭包和v2上下文可用',parent=parent,child=child,child_activity=child_aid)
   forged=save('C01未选上游负例')
   with psycopg.connect(admin,autocommit=True,row_factory=dict_row) as conn:
    conn.execute("SET statement_timeout='15s'");conn.execute("SET lock_timeout='3s'")
    template={t:conn.execute(sql.SQL('SELECT * FROM public.{} WHERE memory_id=%s').format(sql.Identifier(t)),(child,)).fetchall() for t in
     ['learning_memories','learning_memory_commands','learning_memory_revisions','learning_memory_bodies','learning_memory_dependencies']}
    deps=template['learning_memory_dependencies'];assert any(str(d['origin_activity_id'])==aid for d in deps if d['dependency_kind']=='event')
    def clone_base(mid,items):
     key=str(uuid4());items=order_dependencies(items)
     for table in ['learning_memories','learning_memory_commands','learning_memory_revisions','learning_memory_bodies']:
      row=dict(template[table][0]);row['memory_id']=mid
      if table=='learning_memory_commands':row.update(business_key=key,slot_sha256=sha('save|'+mid))
      if table=='learning_memory_revisions':row.update(created_by_key=key,dependency_count=len(items),dependencies_sha256=dependencies_digest(items))
      insert(conn,table,row)
     return [{**d,'memory_id':mid,'version':1,'ordinal':i+1} for i,d in enumerate(items)]
    def reject(name,action,expected):
     baseline=snap(conn);state=None;reason=None
     try:
      with conn.transaction():action();conn.execute('SET CONSTRAINTS ALL IMMEDIATE')
     except psycopg.Error as exc:state=exc.sqlstate;reason=exc.diag.message_primary
     assert state is not None and expected in reason,(name,state,reason)
     assert snap(conn)==baseline
     passed(name,sqlstate=state,reason=reason,before_sha=digest(baseline),after_sha=digest(snap(conn)),negative_sample_rolled_back=True)
    def one(items):
     for d in clone_base(str(uuid4()),items):insert(conn,'learning_memory_dependencies',d)
    omitted=[dict(d) for d in deps if not(d['dependency_kind']=='event' and str(d['origin_activity_id'])==aid and d['record_kind']=='progress')]
    reject('V08 伪造漏闭包被最终SQL拒绝',lambda:one(omitted),'完整闭包')
    unselected=[dict(d) for d in deps];up=next(d for d in unselected if d['dependency_kind']=='memory');up.update(upstream_memory_id=forged,upstream_version=1,upstream_body_sha256=detail(forged)['body_sha256'])
    reject('V08 无选用事实的上游被最终SQL拒绝',lambda:one(unselected),'选用事实')
    def self_reference():
     mid=str(uuid4());items=[dict(d) for d in deps];up=next(d for d in items if d['dependency_kind']=='memory');up['upstream_memory_id']=mid
     for d in clone_base(mid,items):insert(conn,'learning_memory_dependencies',d)
    reject('V08 自引用CHECK拒绝',self_reference,'check')
    def cycle():
     mids=[str(uuid4()),str(uuid4())];rows=[]
     for index,mid in enumerate(mids):
      items=[dict(d) for d in deps];up=next(d for d in items if d['dependency_kind']=='memory');up.update(upstream_memory_id=mids[1-index],upstream_version=1,upstream_body_sha256=template['learning_memory_revisions'][0]['body_sha256'])
      rows.extend(clone_base(mid,items))
     for row in rows:insert(conn,'learning_memory_dependencies',row)
    reject('V08 两节点循环无合法固定选用事实，提交拒绝',cycle,'选用事实')
    source_deps=[]
    for index in range(11):
     new=materials.save(source_id=None,expected_version=None,filename=f'task103-c01-limit-{index}.md',format='md',sha256=original.sha256,size=original.size)
     source_deps.append({'dependency_kind':'source','source_id':new['id'],'source_version_id':new['version_id'],'source_revision':new['revision'],'original_sha256':original.sha256})
    reject('V08 单类来源11超过10，最终SQL拒绝',lambda:one([d for d in deps if d['dependency_kind']!='source']+source_deps),'种类容量')
    def ordinal33():
     rows=clone_base(str(uuid4()),deps);row=rows[0];row['ordinal']=33;insert(conn,'learning_memory_dependencies',row)
    reject('V08 ordinal33超总界，CHECK拒绝',ordinal33,'check')
    before=snap(conn)
    for label,change,status in [('跨活动capture',{'activity_id':unrelated},404),('伪record哈希',{'record_sha256':'0'*64},409),('伪视图token',{'view_token':'0'*64},409)]:
     bad={**valid_capture,**change};response=req('/api/memories/commands',{'business_key':str(uuid4()),'memory_id':str(uuid4()),'expected_revision':0,'action':'save',
      'body':{'kind':'learning_observation','title':'C01伪身份','text':'拒绝项','capture':bad}},status)
     passed('V08 HTTP '+label+'拒绝且0效果',http_status=status,error=response)
    req('/api/memories/commands',{'business_key':str(uuid4()),'memory_id':str(uuid4()),'expected_revision':0,'action':'save',
     'body':{'kind':'learning_observation','title':'C01伪依赖','text':'拒绝项','capture':valid_capture,'dependencies':[]}},422)
    assert snap(conn)==before;passed('V08 客户端手写dependencies不被接纳',http_status=422,before_sha=digest(before),after_sha=digest(snap(conn)))
    op=conn.execute("SELECT o.* FROM activity_operations o JOIN activity_operation_results r USING(activity_id,operation_id) WHERE o.activity_id=%s AND r.payload_format='json' AND r.payload::jsonb->'value'->>'profile'='teaching.v2' ORDER BY o.operation_id LIMIT 1",(child_aid,)).fetchone()
    assert op;result=conn.execute('SELECT * FROM activity_operation_results WHERE activity_id=%s AND operation_id=%s',(child_aid,op['operation_id'])).fetchone()
    command=conn.execute("SELECT * FROM teaching_commands WHERE activity_id=%s AND context_body::jsonb->>'schema'='teaching.context.v2' ORDER BY created_at LIMIT 1",(child_aid,)).fetchone()
    assert command;residual_templates={'operation':op,'result':result,'command':command};atomic_json(EVIDENCE/'v2-residual-templates.json',residual_templates)
    for kind in ['result','accepted_context']:
     baseline=snap(conn);operation='c01-ready-residual-'+uuid4().hex
     try:
      with conn.transaction():
       if kind=='result':
        admission=str(uuid4());row=dict(op);row.update(activity_id=unrelated,operation_id=operation,admission_id=admission);insert(conn,'activity_operations',row)
        row=dict(result);row.update(activity_id=unrelated,operation_id=operation,admission_id=admission);insert(conn,'activity_operation_results',row)
       else:
        row=dict(command);row.update(activity_id=unrelated,business_key=str(uuid4()),operation_id=operation,status='accepted',launch_claimed_at=None,result_record_id=None,parent_record_id=None,retry_of=None,slot_sha256=sha(operation));insert(conn,'teaching_commands',row)
       assert not conn.execute('SELECT public.activity_memory_eligible(%s) AS eligible',(unrelated,)).fetchone()['eligible']
       raise SampleRollback()
     except SampleRollback:pass
     assert snap(conn)==baseline;passed('V10 ready但M6无绑定行且'+kind+'残迹失败关闭',activity=unrelated,rolled_back=True,before_sha=digest(baseline),after_sha=digest(snap(conn)))
   atomic_json(EVIDENCE/'gaps-pg1-complete.json',report)
  clean=time.monotonic();report['pg1_stop']=docker.stop(resource);control.charge('cleanup',time.monotonic()-clean,{'name':'gaps-pg1'})
  docker,resource,admin=owned_start(2);dsn,cfg=configure(admin,resource,'gaps-absent');app,client=app_client();ledger=app.state.activities_ledger
  with client,psycopg.connect(admin,autocommit=True,row_factory=dict_row) as conn:
   before=snap(conn);assert not conn.execute("SELECT to_regclass('public.activity_memory_bindings') AS m").fetchone()['m']
   legacy=conn.execute("SELECT activity_id,operation_id FROM activity_operation_results WHERE payload_format='json' ORDER BY committed_at LIMIT 1").fetchone();assert legacy
   target=str(legacy['activity_id']);assert ar(ledger.read_memory_selection(target))['eligible']
   old=ar(ledger.read_committed_result(target,legacy['operation_id']));assert old.payload is not None
   def residual_sample(kind):
    operation='c01-residual-'+uuid4().hex
    try:
     with conn.transaction():
      if kind=='result':
       op=dict(residual_templates['operation']);op.update(activity_id=target,operation_id=operation,admission_id=str(uuid4()));insert(conn,'activity_operations',op)
       result=dict(residual_templates['result']);result.update(activity_id=target,operation_id=operation,admission_id=op['admission_id']);insert(conn,'activity_operation_results',result)
      else:
       command=dict(residual_templates['command']);command.update(activity_id=target,business_key=str(uuid4()),operation_id=operation,
        status='accepted',launch_claimed_at=None,result_record_id=None,parent_record_id=None,retry_of=None,slot_sha256=sha(operation))
       insert(conn,'teaching_commands',command)
      # 另一连接不可见未提交样本；直接用同事务的真实SQL守卫，不手写ready。
      async def check():
       from psycopg import AsyncConnection
       from psycopg.rows import dict_row as async_dict
       # 当前事务负例只用实际仓储生成守卫，随后在同事务执行。
       async with await AsyncConnection.connect(dsn,row_factory=async_dict) as ac:
        assert await ledger._memory_schema_info(ac)=='absent'
        return await ledger._memory_sql_guard(ac,"'"+target+"'::uuid")
      guard=ar(check());eligible=conn.execute(sql.SQL('SELECT '+guard+' AS eligible')).fetchone()['eligible'];assert not eligible
      report['cases'].append({'name':'V10 缺M6且'+kind+'真实v2残迹，最终仓储SQL拒绝','status':'PASS','executed':True,'eligible':eligible,'synthetic_restore_negative_only':True,'rolled_back':True})
      raise SampleRollback()
    except SampleRollback:pass
    assert snap(conn)==before
   residual_sample('result');residual_sample('accepted_context')
   assert ar(ledger.read_memory_selection(target))['eligible'] and ar(ledger.read_committed_result(target,legacy['operation_id'])).payload is not None
   passed('V10 实际absent 010升级库，旧007/v1正文和原全部行保留',activity=target,before_sha=digest(before),after_sha=digest(snap(conn)))
   report['status']='PASS'
 except BaseException as exc:
  report.update(error_type=type(exc).__name__,message=redact(str(exc)));(EVIDENCE/('gaps-error-'+run_name+'.txt')).write_bytes(redact(__import__('traceback').format_exc()).encode())
 finally:
  clean=time.monotonic()
  if docker and resource:
   try:report['cleanup']=docker.stop(resource)
   except BaseException as exc:report['cleanup_unconfirmed']=type(exc).__name__;report['status']='FAIL'
  control.charge('cleanup',time.monotonic()-clean,{'name':'gaps'});atomic_json(EVIDENCE/('gaps-result-'+run_name+'.json'),report);atomic_json(EVIDENCE/'gaps-result.json',report)
 print(json.dumps({'status':report['status'],'cases':len(report['cases']),'error':report.get('message')},ensure_ascii=False));return 0 if report['status']=='PASS' else 1
if __name__=='__main__':sys.exit(run())
