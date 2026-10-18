"""续作01集中PG/HTTP/真实Windows工具、后继与降级组合。"""
from __future__ import annotations
import io,json,os,sys,time,threading
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from .common import owned_start,forward,configure,app_client,ar,MATERIAL,snapshot,digest
from .control import Control,EVIDENCE,atomic_json,redact

def run():
 c=Control();docker=None;resource=None;start=time.monotonic();report={'status':'FAIL','executed':True,'cases':[],'objects':{}}
 def passed(name,**values):
  report['cases'].append({'name':name,'status':'PASS','executed':True,**values});atomic_json(EVIDENCE/'core-checkpoint.json',report)
 try:
  docker,resource,admin=owned_start(1)
  with psycopg.connect(admin,autocommit=True) as conn:
   conn.execute("SET statement_timeout='15s'");forward(conn,'pg1')
  dsn,cfg=configure(admin,resource);app,client=app_client();ledger=app.state.activities_ledger
  from app.memory.contracts import MemoryCommandInput,MemoryRefusal
  from app.capabilities.contracts import ToolCallPlan,AdmissionIntent,CallContext,Provider,LedgerOutcome,LedgerDisposition,build_business_payload
  from app.activities.service import ActivityService
  from app.materials.repository import PostgresMaterials
  from app.learning.contracts import canonical,sha
  from app.learning.teaching_contracts import TeachingCommandInput
  with client:
   headers={'x-retrolume-session':app.state.session_token,'origin':'http://testserver'}
   def req(path,body=None,status=200):
    r=client.get(path,headers=headers) if body is None else client.post(path,json=body,headers=headers)
    assert r.status_code==status,(path,r.status_code,r.json());return r.json()
   def save(title='C01合成记忆',text='我仍容易把分钟当秒',kind='self_report'):
    mid=str(uuid4());key=str(uuid4());receipt=req('/api/memories/commands',{'business_key':key,'memory_id':mid,'expected_revision':0,'action':'save','body':{'kind':kind,'title':title,'text':text}})
    return mid,key,receipt
   def detail(mid):return req('/api/memories/'+mid)
   def activity(source,mids=()):
    aid=str(uuid4());body={'activity_id':aid,'source_ids':[source['id']]}
    if mids:body['memory_selection']={'confirmed':True,'entries':[{k:detail(mid)[k] for k in ['memory_id','version','revision','body_sha256']} for mid in mids]}
    req('/api/activities',body);return aid
   def ws(aid):return req(f'/api/activities/{aid}/teaching/workspace')
   def command(aid,action,body):
    view=ws(aid);return {'business_key':str(uuid4()),'expected_revision':view['head']['revision'],'expected_goal_version':view['head']['goal_version'],'expected_scope_revision':1,'action':action,'body':body}
   def submit(aid,action,body):return req(f'/api/activities/{aid}/teaching/commands',command(aid,action,body))
   def goal(aid):return submit(aid,'goal',{'goal':'平均速度独立理解','self_report':None,'domain':None,'seed_operation_id':None,'seed_payload_sha256':None})
   def plan(aid):return submit(aid,'plan',{'confirmed':True,'correction_record_id':None,'retry_of':None})
   def exercise(aid):
    view=ws(aid);return submit(aid,'exercise',{'confirmed':True,'path_record_id':view['head']['path_record_id'],'node_id':'n1','purpose':'initial','parent_feedback_record_id':None,'retry_of':None})
   def evaluate(aid,eid,answer,correction=None):return submit(aid,'evaluate',{'confirmed':True,'exercise_record_id':eid,'answer_record_id':answer,'correction_record_id':correction,'retry_of':None})
   def capture(aid,pid,title):
    value=req(f'/api/activities/{aid}/teaching/records/{pid}/memory-preview');mid=str(uuid4())
    req('/api/memories/commands',{'business_key':str(uuid4()),'memory_id':mid,'expected_revision':0,'action':'save','body':{'kind':'learning_observation','title':title,'text':'当时有限观察','capture':value['capture']}});return mid
   def phase1(mid):
    row=detail(mid);impact=req(f"/api/memories/{mid}/impact?expected_revision={row['revision']}&action=revoke")
    cmd=MemoryCommandInput(business_key=str(uuid4()),memory_id=mid,expected_revision=row['revision'],action='revoke',body={'impact_token':impact['impact_token'],'confirm_revoke':True,'purge_memory_content':True})
    return cmd,ar(ledger.apply_memory_command(cmd))
   assert req('/api/activities/capabilities')['memory_model']['available']
   with psycopg.connect(dsn) as conn:
    unknown=conn.execute("SELECT activity_id,operation_id,state FROM activity_operations WHERE error_code='memory_dependency_invalid' AND state='unknown' ORDER BY recorded_at DESC LIMIT 1").fetchone()
    assert unknown and unknown[2]=='unknown'
    old=conn.execute("SELECT business_key,request_sha256,result_meta FROM learning_memory_commands WHERE action='purge' ORDER BY committed_at LIMIT 1").fetchone()
    assert old;old_meta=old[2]
   receipt=req('/api/memories/commands/'+str(old[0]));assert receipt['business_key']==str(old[0]) and receipt['request_sha256']==old[1]
   passed('末尾三函数前向、原行/权限不改、旧UNKNOWN与收据只读确认',unknown_activity=str(unknown[0]),old_key=str(old[0]),old_meta_sha=sha(old_meta),legacy_meta_unchanged=True)
   # 新清理实际标准字节，原清理故障和权限证据按未改分支继承。
   purge_mid,_,_=save('C01标准收据','本轮精确正文');rev,receipt=phase1(purge_mid)
   purge_key=str(uuid4());done=req('/api/memories/commands',{'business_key':purge_key,'memory_id':purge_mid,'expected_revision':receipt['revision_after'],'action':'purge',
     'body':{'revocation_key':rev.business_key,'manifest_sha256':receipt['manifest_sha256'],'confirm_memory_cleanup':True}})
   assert done['purge_state_now']=='done'
   with psycopg.connect(dsn) as conn:
    text=conn.execute('SELECT result_meta FROM learning_memory_commands WHERE business_key=%s',(purge_key,)).fetchone()[0]
    assert text==canonical(json.loads(text));assert conn.execute('SELECT count(*) FROM learning_memory_bodies WHERE memory_id=%s',(purge_mid,)).fetchone()[0]==0
   passed('V18 最终purge收据canonical实际字节与精确M3清理',memory_id=purge_mid,key=purge_key,result_meta=text)
   originals=app.state.originals;original=originals.put(io.BytesIO(MATERIAL.encode()),max_bytes=5242880);materials=PostgresMaterials(dsn)
   source=materials.save(source_id=None,expected_version=None,filename='task103-c01-core.md',format='md',sha256=original.sha256,size=original.size)
   bg,_,_=save('C01低信任偏好');pref,_,_=save('C01第二背景','先统一米秒','preference');aid=activity(source,[bg,pref]);goal(aid)
   report['objects'].update(source=source,activity_id=aid,bg=bg,pref=pref);atomic_json(EVIDENCE/'core-checkpoint.json',report)
   sup=c.load()['counts']['sup'];budget_before=ws(aid)['budgets']
   denied=req(f'/api/activities/{aid}/continuations',{'parent_operation_id':'task103-parent','new_operation_id':'c01-denied-'+uuid4().hex,'followup':'继续'},409)
   assert denied['detail']['code']=='memory_profile_required' and '教学工作区' in denied['detail']['message']
   generic=ar(ActivityService(ledger).execute_tool_action(aid,'c01-generic-tool',ToolCallPlan('c1','finite_calculate',{'operation':'divide','left':120,'right':120}),app.state.teaching_session_config,'c01-generic','c01-generic'))
   assert generic.status=='memory_profile_required' and c.load()['counts']['sup']==sup
   assert ws(aid)['budgets']==budget_before
   passed('DEF020 普通continue409/中文和通用tool拒绝，零SUP/零预算变化',activity_id=aid,continue_error=denied['detail'],generic_status=generic.status)
   proposal=plan(aid);assert proposal['status']=='committed';submit(aid,'accept_path',{'proposal_record_id':ws(aid)['proposal']['record_id']});exercise(aid)
   eid=ws(aid)['head']['exercise_record_id'];answer=submit(aid,'answer',{'exercise_record_id':eid,'kind':'initial','text':'我不知道结果，尚不确定','supersedes_answer_record_id':None});answer_id=answer['record_ids'][0]['record_id']
   submit(aid,'expose',{'exercise_record_id':eid,'part':'reference'})
   tool=submit(aid,'calculate',{'confirmed':True,'exercise_record_id':eid,'answer_record_id':answer_id,'reference_point_id':'p1','retry_of':None});assert tool['status']=='committed',tool
   with psycopg.connect(dsn) as conn:
    op=conn.execute('SELECT kind,provider,request_bytes,reserved_cost_microunits FROM activity_operations WHERE activity_id=%s AND operation_id=%s',(aid,tool['operation_id'])).fetchone()
    assert op==('tool',None,None,0),op
   feedback=evaluate(aid,eid,answer_id);assert feedback['status']=='committed'
   view=ws(aid);support=view['reason']['body']['support_checks'];assert support and all(x['answer_status']=='unchecked' for x in support)
   assert not view['reason']['body']['advance'];assert all(n.get('status')!='evidence_sufficient' for n in view['nodes'].values()) if isinstance(view['nodes'],dict) else True
   budget=view['budgets'];assert [budget[k] for k in ['requests_reserved','cost_reserved_microunits','tools_reserved','running_reserved_seconds']]==[3,3000,1,0]
   observed=capture(aid,view['head']['reason_record_id'],'C01有限观察一');assert detail(observed)['qualification']=='current'
   report['objects'].update(exercise_id=eid,answer_id=answer_id,feedback1=feedback['record_ids'][0]['record_id'],observed=observed,tool=tool['operation_id'])
   passed('V04/V21/V22 选记忆合法calc真实工具账，all-met/unknown不推进',activity_id=aid,sup_delta=c.load()['counts']['sup']-sup,tool_operation=tool['operation_id'],kind=list(op),support_checks=support,budgets=budget)
   unrelated=activity(source);goal(unrelated);assert detail(observed)['qualification']=='current'
   first_feedback=report['objects']['feedback1'];correction1=submit(aid,'correct',{'target_record_id':first_feedback,'text':'请核对这次反馈的单位支持','disputed_dimensions':['value']})
   evaluate(aid,eid,answer_id,correction1['record_ids'][0]['record_id']);second=capture(aid,ws(aid)['head']['reason_record_id'],'C01有限观察二')
   correction2=submit(aid,'correct',{'target_record_id':first_feedback,'text':'再次补充早前反馈的注记','disputed_dimensions':['value']})
   assert detail(second)['qualification']=='current','旧feedback注记不应替代针对关联的资格'
   evaluate(aid,eid,answer_id,correction2['record_ids'][0]['record_id']);assert detail(second)['body'] is None
   passed('V07 相同answer新feedback独立失效，无关活动/旧feedback注记不误伤',memory_id=second,origin_activity=aid,answer_id=answer_id,unrelated_activity=unrelated)
   current_obs=capture(aid,ws(aid)['head']['reason_record_id'],'C01 PDF前观察')
   from app.pdf_import.contracts import PdfImportResult,PdfPage
   from app.pdf_review.contracts import ReviewPage
   from pypdf import PdfWriter
   writer=PdfWriter();writer.add_blank_page(width=300,height=300);stream=io.BytesIO();writer.write(stream);raw=originals.put(io.BytesIO(stream.getvalue()),max_bytes=5242880)
   candidate=materials.create_pdf_candidate(source_id=source['id'],expected_version=source['version_id'],expected_revision=source['revision'],filename='task103-c01-candidate.pdf',sha256=raw.sha256,size=raw.size,
    extraction=PdfImportResult(1,(PdfPage(1,MATERIAL,()),),(),extraction_method='task103-c01-synthetic-extracted-page'))
   assert detail(current_obs)['qualification']=='current' and materials.get(source['id'])['version_id']==source['version_id']
   confirmed=materials.confirm_pdf_candidate(candidate_id=candidate['candidate_id'],version_id=candidate['version_id'],pages=(ReviewPage(1,True,None),))
   assert detail(current_obs)['body'] is None
   pdf_source=materials.get(source['id']);pdf_aid=activity(pdf_source,[pref]);goal(pdf_aid);plan(pdf_aid);submit(pdf_aid,'accept_path',{'proposal_record_id':ws(pdf_aid)['proposal']['record_id']});exercise(pdf_aid)
   pdf_eid=ws(pdf_aid)['head']['exercise_record_id'];pdf_answer=submit(pdf_aid,'answer',{'exercise_record_id':pdf_eid,'kind':'initial','text':'1m/s','supersedes_answer_record_id':None});evaluate(pdf_aid,pdf_eid,pdf_answer['record_ids'][0]['record_id'])
   pdf_mem=capture(pdf_aid,ws(pdf_aid)['head']['reason_record_id'],'C01已确认PDF观察');assert detail(pdf_mem)['qualification']=='current'
   passed('V05 候选未切换不失效，逐页确认后旧观察失效，确认PDF新记忆可用',source_id=source['id'],candidate_id=candidate['candidate_id'],old_memory=current_obs,pdf_activity=pdf_aid,pdf_memory=pdf_mem,parser_run=False)
   # 真实来源切换竞争，读取自身body/hash/资格是完整同一SELECT。
   gate=threading.Event()
   def reader():
    gate.wait();values=[]
    for _ in range(5):
     row=detail(pdf_mem)
     if row['body'] is not None:assert sha(canonical(row['body']))==row['body_sha256'] and row['qualification']=='current'
     else:assert row['qualification']=='memory_dependency_invalid'
     values.append({'body':row['body'] is not None,'qualification':row['qualification']})
    return values
   new_raw=originals.put(io.BytesIO((MATERIAL+'本轮版本更新。\n').encode()),max_bytes=5242880)
   with ThreadPoolExecutor(max_workers=2) as pool:
    tasks=[pool.submit(reader) for _ in range(2)];gate.set();replacement=materials.save(source_id=source['id'],expected_version=pdf_source['version_id'],filename='task103-c01-replaced.md',format='md',sha256=new_raw.sha256,size=new_raw.size);reads=[f.result() for f in tasks]
   assert detail(pdf_mem)['body'] is None
   passed('V09 来源切换并发完整前/后资格与正文，最终失效',memory_id=pdf_mem,reads=reads,new_source=replacement)
   # 独立可辨legacy使用真实007结果；结构damaged下不借旧v2数据。
   legacy_source=replacement;legacy=activity(legacy_source)
   from app.worker.one_call import run_one_call
   from app.capabilities.contracts import ModelCallRequest
   legacy_call=run_one_call(ledger,app.state.teaching_session_config,legacy,'c01-seed','c01-seed-result',
     ModelCallRequest(messages=[{'role':'user','content':'受控legacy父正文'}],max_output_tokens=128),app.state.activity_config.model_service,run_tag='c01-seed')
   assert legacy_call.active_processes_at_end==0 and legacy_call.reserved_seconds==0
   assert ar(ledger.read_committed_result(legacy,'c01-seed-result')).payload is not None
   with psycopg.connect(admin,autocommit=True) as conn:conn.execute('ALTER TABLE public.learning_memory_bodies RENAME TO c01_unavailable_bodies')
   try:
    selected=ar(ledger.read_memory_selection(aid));clean=ar(ledger.read_memory_selection(legacy));assert not selected['eligible'] and clean['eligible'] and not clean['selected']
    assert ar(ledger.read_committed_result(legacy,'c01-seed-result')).payload is not None
    assert ws(aid)['memory_invalid'] and not ws(legacy)['memory_invalid']
    assert not req('/api/activities/capabilities')['memory_model']['available']
    # API旧默认管理总120大于本轮50；直接用同入口的service和合法本轮配置完成旧使用。
    continued=ar(ActivityService(ledger).continue_from_result(legacy,'c01-seed-result','c01-legacy-continue','继续平均速度',app.state.activity_config.model_service,app.state.teaching_session_config,'c01-legacy','c01-legacy'))
    assert continued.business and continued.business.snapshot and continued.business.snapshot.payload is not None,continued.status
   finally:
    with psycopg.connect(admin,autocommit=True) as conn:conn.execute('ALTER TABLE public.c01_unavailable_bodies RENAME TO learning_memory_bodies')
   with psycopg.connect(admin,autocommit=True) as conn:conn.execute('ALTER TABLE public.activity_memory_bindings RENAME TO c01_unavailable_bindings')
   try:assert not ar(ledger.read_memory_selection(legacy))['eligible'] and not ar(ledger.read_memory_selection(aid))['eligible']
   finally:
    with psycopg.connect(admin,autocommit=True) as conn:conn.execute('ALTER TABLE public.c01_unavailable_bindings RENAME TO activity_memory_bindings')
   passed('DEF021 damaged但M6可靠无绑定legacy读/真实继续可用；已选/缺M6关闭',legacy_activity=legacy,selected_activity=aid,continued_status=continued.status)
   report['objects'].update(pdf_source=pdf_source,pdf_mem=pdf_mem,pdf_activity=pdf_aid,legacy_activity=legacy,new_source=replacement)
   report['status']='PASS'
 except BaseException as exc:
  report.update(error_type=type(exc).__name__,message=redact(str(exc)));(EVIDENCE/'core-error.txt').write_bytes(redact(__import__('traceback').format_exc()).encode())
 finally:
  # 实际根只由外壳收费，避免再重复借回或制造新额。
  clean=time.monotonic()
  if docker and resource:
   try:report['cleanup']=docker.stop(resource)
   except BaseException as exc:report['cleanup_unconfirmed']=type(exc).__name__;report['status']='FAIL'
  c.charge('cleanup',time.monotonic()-clean,{'name':'core'});atomic_json(EVIDENCE/'core-result.json',report)
 print(json.dumps({'status':report['status'],'cases':len(report['cases']),'error':report.get('message')},ensure_ascii=False))
 return 0 if report['status']=='PASS' else 1
if __name__=='__main__':sys.exit(run())
