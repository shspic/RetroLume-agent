"""从C01已提交工具/反馈断点接续，保留失败窗口预留。"""
import io,json,os,sys,time,threading
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
import psycopg
from .common import owned_start,configure,app_client,ar,MATERIAL
from .control import Control,EVIDENCE,atomic_json,redact
def run():
 c=Control();docker=None;resource=None;report=json.loads((EVIDENCE/'core-result.json').read_text(encoding='utf-8'));report['status']='FAIL'
 def passed(name,**values):
  report['cases'].append({'name':name,'status':'PASS','executed':True,**values});atomic_json(EVIDENCE/'remaining-checkpoint.json',report)
 try:
  docker,resource,admin=owned_start(1);dsn,cfg=configure(admin,resource,'remaining');app,client=app_client();ledger=app.state.activities_ledger
  from app.materials.repository import PostgresMaterials
  from app.learning.contracts import canonical,sha
  with client:
   h={'x-retrolume-session':app.state.session_token,'origin':'http://testserver'}
   def req(path,body=None,status=200):
    r=client.get(path,headers=h) if body is None else client.post(path,json=body,headers=h);assert r.status_code==status,(path,r.status_code,r.json());return r.json()
   def detail(mid):return req('/api/memories/'+mid)
   def ws(aid):return req(f'/api/activities/{aid}/teaching/workspace')
   def submit(aid,action,body):
    v=ws(aid);payload={'business_key':str(uuid4()),'expected_revision':v['head']['revision'],'expected_goal_version':v['head']['goal_version'],'expected_scope_revision':1,'action':action,'body':body}
    receipt=req(f'/api/activities/{aid}/teaching/commands',payload);atomic_json(EVIDENCE/'receipts'/(payload['business_key']+'.json'),receipt)
    return receipt
   def activity(source,mids=()):
    aid=str(uuid4());b={'activity_id':aid,'source_ids':[source['id']]}
    if mids:b['memory_selection']={'confirmed':True,'entries':[{k:detail(m)[k] for k in ['memory_id','version','revision','body_sha256']} for m in mids]}
    req('/api/activities',b);return aid
   def goal(aid):submit(aid,'goal',{'goal':'平均速度与单位','self_report':None,'domain':None,'seed_operation_id':None,'seed_payload_sha256':None})
   def capture(aid,title):
    pid=ws(aid)['head']['reason_record_id'];v=req(f'/api/activities/{aid}/teaching/records/{pid}/memory-preview');mid=str(uuid4())
    req('/api/memories/commands',{'business_key':str(uuid4()),'memory_id':mid,'expected_revision':0,'action':'save','body':{'kind':'learning_observation','title':title,'text':'本轮有限观察','capture':v['capture']}});return mid
   obj=report['objects'];aid=obj['activity_id'];source=obj['source'];pref=obj['pref'];eid=obj['exercise_id'];answer=obj['answer_id'];first=obj['feedback1']
   with psycopg.connect(dsn) as conn:
    second=str(conn.execute("SELECT memory_id FROM learning_memory_bodies WHERE body::jsonb->>'title'='C01有限观察二' ORDER BY memory_id LIMIT 1").fetchone()[0])
    unknown=conn.execute("SELECT business_key,status,operation_id FROM teaching_commands WHERE activity_id=%s AND action='evaluate' ORDER BY created_at DESC LIMIT 1",(aid,)).fetchone()
   atomic_json(EVIDENCE/'failed-window-diagnostic.json',{'command_key':str(unknown[0]),'status':unknown[1],'operation_id':unknown[2],'budgets':ws(aid)['budgets']})
   assert detail(second)['qualification']=='current'
   if '--skip-blocked-window' in sys.argv:
    current=second
    passed('旧失败窗口保留R20，single_host恢复false；相关追加评价BLOCKED不重发',activity_id=aid,unknown_key=str(unknown[0]),new_effect=False)
   else:
    correction=submit(aid,'correct',{'target_record_id':first,'text':'核对早前反馈的追加说明','disputed_dimensions':['value']})
    t=time.monotonic();evaluated=submit(aid,'evaluate',{'confirmed':True,'exercise_record_id':eid,'answer_record_id':answer,'correction_record_id':correction['record_ids'][0]['record_id'],'retry_of':None})
    assert evaluated['status']=='committed',evaluated
    assert detail(second)['body'] is None
    passed('V07 新关联feedback使同answer有限观察失效，旧注记不误伤',memory_id=second,activity_id=aid,elapsed_seconds=time.monotonic()-t)
    current=capture(aid,'C01 PDF前观察')
   originals=app.state.originals;materials=PostgresMaterials(dsn)
   from app.pdf_import.contracts import PdfImportResult,PdfPage
   from app.pdf_review.contracts import ReviewPage
   from pypdf import PdfWriter
   stream=io.BytesIO();w=PdfWriter();w.add_blank_page(width=300,height=300);w.write(stream);raw=originals.put(io.BytesIO(stream.getvalue()),max_bytes=5242880)
   candidate=materials.create_pdf_candidate(source_id=source['id'],expected_version=source['version_id'],expected_revision=source['revision'],filename='task103-c01-candidate.pdf',sha256=raw.sha256,size=raw.size,
    extraction=PdfImportResult(1,(PdfPage(1,MATERIAL,()),),(),extraction_method='task103-c01-synthetic-extracted-page'))
   assert detail(current)['qualification']=='current'
   materials.confirm_pdf_candidate(candidate_id=candidate['candidate_id'],version_id=candidate['version_id'],pages=(ReviewPage(1,True,None),));assert detail(current)['body'] is None
   pdf=materials.get(source['id']);pdf_aid=activity(pdf,[pref]);goal(pdf_aid)
   plan=submit(pdf_aid,'plan',{'confirmed':True,'correction_record_id':None,'retry_of':None});assert plan['status']=='committed'
   submit(pdf_aid,'accept_path',{'proposal_record_id':ws(pdf_aid)['proposal']['record_id']});v=ws(pdf_aid)
   exercise=submit(pdf_aid,'exercise',{'confirmed':True,'path_record_id':v['head']['path_record_id'],'node_id':'n1','purpose':'initial','parent_feedback_record_id':None,'retry_of':None});assert exercise['status']=='committed'
   pe=ws(pdf_aid)['head']['exercise_record_id'];pa=submit(pdf_aid,'answer',{'exercise_record_id':pe,'kind':'initial','text':'1m/s','supersedes_answer_record_id':None})
   evaluated=submit(pdf_aid,'evaluate',{'confirmed':True,'exercise_record_id':pe,'answer_record_id':pa['record_ids'][0]['record_id'],'correction_record_id':None,'retry_of':None});assert evaluated['status']=='committed'
   pm=capture(pdf_aid,'C01已确认PDF观察');assert detail(pm)['qualification']=='current';report['objects'].update(pdf_activity=pdf_aid,pdf_memory=pm)
   passed('V05 PDF候选/确认/新观察，仅测记忆关联不冒解析质量',candidate=candidate['candidate_id'],old_memory=current,pdf_memory=pm,physical_page=1)
   gate=threading.Event()
   def reader():
    gate.wait();values=[]
    for _ in range(5):
     row=detail(pm)
     if row['body'] is not None:assert sha(canonical(row['body']))==row['body_sha256'] and row['qualification']=='current'
     else:assert row['qualification']=='memory_dependency_invalid'
     values.append({'body_present':row['body'] is not None,'qualification':row['qualification']})
    return values
   replacement_raw=originals.put(io.BytesIO((MATERIAL+'本轮来源版本更新。\n').encode()),max_bytes=5242880)
   with ThreadPoolExecutor(max_workers=2) as pool:
    jobs=[pool.submit(reader) for _ in range(2)];gate.set();replacement=materials.save(source_id=source['id'],expected_version=pdf['version_id'],filename='task103-c01-replaced.md',format='md',sha256=replacement_raw.sha256,size=replacement_raw.size);reads=[x.result() for x in jobs]
   assert detail(pm)['body'] is None
   passed('V09 来源切换并发读完整资格/正文',memory_id=pm,reads=reads,new_source=replacement)
   from app.worker.one_call import run_one_call
   from app.capabilities.contracts import ModelCallRequest
   from app.activities.service import ActivityService
   legacy=activity(replacement)
   seed=run_one_call(ledger,app.state.teaching_session_config,legacy,'c01-seed','c01-seed-result',ModelCallRequest(messages=[{'role':'user','content':'受控legacy父正文'}],max_output_tokens=128),app.state.activity_config.model_service,run_tag='c01-seed')
   assert seed.active_processes_at_end==0 and seed.reserved_seconds==0 and ar(ledger.read_committed_result(legacy,'c01-seed-result')).payload is not None
   with psycopg.connect(admin,autocommit=True) as conn:conn.execute('ALTER TABLE public.learning_memory_bodies RENAME TO c01_unavailable_bodies')
   try:
    assert ar(ledger.read_memory_selection(legacy))['eligible'] and not ar(ledger.read_memory_selection(aid))['eligible']
    assert not ws(legacy)['memory_invalid'] and ws(aid)['memory_invalid'] and not req('/api/activities/capabilities')['memory_model']['available']
    continued=ar(ActivityService(ledger).continue_from_result(legacy,'c01-seed-result','c01-legacy-continue','继续平均速度',app.state.activity_config.model_service,app.state.teaching_session_config,'c01-legacy','c01-legacy'))
    assert continued.business and continued.business.snapshot and continued.business.snapshot.payload is not None,continued.status
   finally:
    with psycopg.connect(admin,autocommit=True) as conn:conn.execute('ALTER TABLE public.c01_unavailable_bodies RENAME TO learning_memory_bodies')
   with psycopg.connect(admin,autocommit=True) as conn:conn.execute('ALTER TABLE public.activity_memory_bindings RENAME TO c01_unavailable_bindings')
   try:assert not ar(ledger.read_memory_selection(legacy))['eligible'] and not ar(ledger.read_memory_selection(aid))['eligible']
   finally:
    with psycopg.connect(admin,autocommit=True) as conn:conn.execute('ALTER TABLE public.c01_unavailable_bindings RENAME TO activity_memory_bindings')
   passed('DEF021 可靠无选择legacy读/真实继续可用；已选/无法分类关闭',legacy_activity=legacy,selected_activity=aid,continue_status=continued.status)
   report['objects'].update(legacy_activity=legacy,new_source=replacement);report['status']='PASS'
 except BaseException as exc:
  report.update(error_type=type(exc).__name__,message=redact(str(exc)));(EVIDENCE/('remaining-error-'+os.environ['RETROLUME_TASK103_C01_RUN']+'.txt')).write_bytes(redact(__import__('traceback').format_exc()).encode())
 finally:
  start=time.monotonic()
  if docker and resource:
   try:report['cleanup']=docker.stop(resource)
   except BaseException as exc:report['cleanup_unconfirmed']=type(exc).__name__;report['status']='FAIL'
  c.charge('cleanup',time.monotonic()-start,{'name':'remaining'});atomic_json(EVIDENCE/('remaining-result-'+os.environ['RETROLUME_TASK103_C01_RUN']+'.json'),report);atomic_json(EVIDENCE/'remaining-result.json',report)
 print(json.dumps({'status':report['status'],'cases':len(report['cases']),'error':report.get('message')},ensure_ascii=False));return 0 if report['status']=='PASS' else 1
if __name__=='__main__':sys.exit(run())
