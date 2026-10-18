"""最小正常源：合法源/记忆/事件/上游/三类历史，约束全部真实COMMIT。

只使用C02新ID和普通生产仓储/有界合成SQL，不发模型请求或启动preview。
"""
from datetime import datetime,timedelta,timezone
import io
from uuid import uuid4
from app.activities import ActivitySpec,SourceSnapshot
from app.capabilities.contracts import AdmissionIntent,CallContext,Provider,LedgerOutcome,LedgerDisposition,build_business_payload
from app.memory.contracts import MemoryCommandInput,MemorySelectionInput
from app.learning.teaching_contracts import TeachingCommandInput
from app.interview.contracts import InterviewCommandInput
from app.data_exit.contracts import canonical,digest
from app.data_exit.codec import plain


def material(rt,name,text,previous=None):
    raw=text.encode('utf-8');prepared=rt.references.prepare_reference(digest(raw),len(raw),source_id=previous['id'] if previous else None)
    with rt.references.acquire_shared(prepared) as pin:
        original=rt.app.state.originals.put(io.BytesIO(raw),max_bytes=4096,reference_pin=pin)
        return rt.app.state.materials.save(source_id=previous['id'] if previous else None,expected_version=previous['version_id'] if previous else None,
          filename=name+'.md',format='md',sha256=original.sha256,size=original.size,reference_pin=pin,prepared_ids=prepared)


def memory(rt,title,deps=(),kind='self_report'):
    mid,key=str(uuid4()),str(uuid4());uncertainty='limited' if kind=='learning_observation' else 'self_reported'
    body=canonical({'schema':'memory.body.v1','kind':kind,'uncertainty':uncertainty,'title':title,'text':'C02 saved '+title})
    columns={'source':('source_id','source_version_id','source_revision','original_sha256'),
      'event':('origin_activity_id','record_id','record_kind','record_sha256','origin_scope_revision','origin_goal_version'),
      'memory':('upstream_memory_id','upstream_version','upstream_body_sha256')}
    def dep_line(d):
        order={'source':('source_id','source_version_id','source_revision','original_sha256'),
          'event':('origin_activity_id','record_id','record_kind','origin_scope_revision','origin_goal_version','record_sha256'),
          'memory':columns['memory']}[d['dependency_kind']]
        return '|'.join([d['dependency_kind']]+[str(d[k]) for k in order])
    from psycopg import sql
    with rt.gate.acquire(),rt.source.connection() as conn:
        conn.execute("INSERT INTO public.learning_memories(memory_id,revision,current_version,state) VALUES(%s,1,1,'active')",(mid,))
        conn.execute("INSERT INTO public.learning_memory_commands(business_key,action,memory_id,request_sha256,slot_sha256,effect_applied,before_revision,after_revision,after_version,result_meta) VALUES(%s,'save',%s,%s,%s,true,0,1,1,'{}')",(key,mid,digest(key),digest('slot'+key)))
        conn.execute("INSERT INTO public.learning_memory_revisions(memory_id,version,claim_kind,uncertainty,policy_version,body_sha256,body_bytes,dependencies_sha256,dependency_count,created_by_key) VALUES(%s,1,%s,%s,%s,%s,%s,%s,%s,%s)",
          (mid,kind,uncertainty,'memory.observation.v1' if kind=='learning_observation' else 'memory.user.v1',digest(body),len(body.encode()),digest('\n'.join(dep_line(d) for d in deps)),len(deps),key))
        for ordinal,dep in enumerate(deps,1):
            names=['memory_id','version','ordinal','dependency_kind',*columns[dep['dependency_kind']]]
            values=[mid,1,ordinal,dep['dependency_kind'],*[dep[n] for n in names[4:]]]
            conn.execute(sql.SQL('INSERT INTO public.learning_memory_dependencies ({}) VALUES({})').format(sql.SQL(',').join(map(sql.Identifier,names)),sql.SQL(',').join(sql.Placeholder() for _ in names)),values)
        conn.execute('INSERT INTO public.learning_memory_bodies(memory_id,version,body) VALUES(%s,1,%s)',(mid,body))
    return {'memory_id':mid,'version':1,'body_sha256':digest(body),'body':body}


def source_dependency(source):
    return {'dependency_kind':'source','source_id':source['id'],'source_version_id':source['version_id'],'source_revision':source['revision'],'original_sha256':source['sha256']}


async def seed(rt):
    ledger=rt.app.state.activities_ledger
    sources={name:material(rt,'C02-'+name,'C02 '+name+' original\r\n') for name in ('valid','delete','replace')}
    memories={name:memory(rt,'C02-'+name,[source_dependency(source)]) for name,source in sources.items()}
    upstream=memory(rt,'C02-upstream',kind='preference');memories['upstream']=upstream
    async def activity(source,selected=False):
        aid=str(uuid4());selection=MemorySelectionInput(confirmed=True,entries=[{'memory_id':upstream['memory_id'],'version':1,'revision':1,'body_sha256':upstream['body_sha256']}]) if selected else None
        await ledger.create_activity(ActivitySpec(activity_id=aid,sources=(SourceSnapshot(source['id'],source['version_id'],source['revision']),),
          deadline_at=datetime.now(timezone.utc)+timedelta(hours=4),max_requests=8,max_cost_microunits=10000,reserve_cost_microunits=100,
          max_request_bytes=65536,max_output_tokens=256,max_running_seconds=180,allowed_models=(('deepseek_chat_completions','c02-synthetic'),),allowed_tools=(),max_tool_calls=0),memory_selection=selection)
        return aid
    aid=await activity(sources['valid'],True)
    await ledger.apply_teaching_local(aid,TeachingCommandInput(business_key=str(uuid4()),expected_revision=0,expected_goal_version=0,expected_scope_revision=1,action='goal',body={'goal':'C02 synthetic goal'}))
    # 只保存合成传输收据。无provider，model标签只是原记录形状。
    lease=await ledger.claim_lease(aid,'c02-synthetic',lease_seconds=60,window_seconds=60)
    op='c02.synthetic.exercise'
    permit=await ledger.admit(AdmissionIntent(CallContext(activity_id=aid,executor_id='c02-synthetic',operation_id=op,execution_generation=lease.execution_generation,scope_revision=1),Provider.DEEPSEEK_CHAT_COMPLETIONS,'c02-synthetic',32,128,()))
    await ledger.mark_dispatch_started(permit)
    fmt,payload,payload_sha=build_business_payload(json_object={'fixture':'C02 saved exercise','sources':[{'source_id':sources['valid']['id'],'version_id':sources['valid']['version_id'],'source_revision':1,'original_sha256':sources['valid']['sha256']}]})
    await ledger.record_outcome(permit,LedgerOutcome(LedgerDisposition.RECEIVED,prompt_tokens=1,completion_tokens=1,response_bytes=len(payload.encode()),payload_format=fmt,payload=payload,payload_sha256=payload_sha))
    with rt.gate.acquire(),rt.source.connection() as conn:
        goal=conn.execute("SELECT record_id FROM public.teaching_records WHERE activity_id=%s AND kind='goal'",(aid,)).fetchone()['record_id']
        refs=canonical([{'source_id':sources['valid']['id'],'version_id':sources['valid']['version_id'],'source_revision':1,'original_sha256':sources['valid']['sha256']}])
        rid,answer=str(uuid4()),str(uuid4());answer_body=canonical({'text':'C02 original answer'})
        for seq,kind,record,body,operation,exercise in ((2,'exercise',rid,None,op,None),(3,'answer',answer,answer_body,None,rid)):
            key=str(uuid4());raw=canonical({'fixture':kind})
            conn.execute("INSERT INTO public.teaching_commands(activity_id,business_key,action,request_sha256,request_body,slot_sha256,expected_revision,goal_version,scope_revision,status) VALUES(%s,%s,%s,%s,%s,%s,1,1,1,'history')",(aid,key,kind,digest(raw),raw,digest(key)))
            conn.execute("INSERT INTO public.teaching_records(activity_id,record_id,seq,kind,business_key,ordinal,goal_version,scope_revision,goal_record_id,exercise_record_id,operation_id,body,body_sha256,source_refs) VALUES(%s,%s,%s,%s,%s,1,1,1,%s,%s,%s,%s,%s,%s)",
              (aid,record,seq,kind,key,goal,exercise,operation,body,payload_sha if body is None else digest(body),refs))
    event={'dependency_kind':'event','origin_activity_id':aid,'record_id':answer,'record_kind':'answer','record_sha256':digest(answer_body),'origin_scope_revision':1,'origin_goal_version':1}
    memories['event']=memory(rt,'C02-event',[source_dependency(sources['valid']),event],kind='learning_observation')
    memories['downstream']=memory(rt,'C02-downstream',[source_dependency(sources['valid']),event,{'dependency_kind':'memory','upstream_memory_id':upstream['memory_id'],'upstream_version':1,'upstream_body_sha256':upstream['body_sha256']}],kind='learning_observation')
    interview=await activity(sources['delete'])
    await ledger.apply_interview_local(interview,InterviewCommandInput(business_key=str(uuid4()),action='start',expected_head_revision=0,expected_goal_version=0,expected_scope_revision=1,body={'goal':{'target':'C02 interview'}}))
    await ledger.apply_interview_local(interview,InterviewCommandInput(business_key=str(uuid4()),action='ask',expected_head_revision=1,expected_goal_version=1,expected_scope_revision=1,body={'mode':'first'}),application_value={'type':'question','text':'C02 question','purpose':'bounded fixture','reason':'saved history'})
    head=(await ledger.read_interview_workspace(interview))['head']
    await ledger.apply_interview_local(interview,InterviewCommandInput(business_key=str(uuid4()),action='answer',expected_head_revision=2,expected_goal_version=1,expected_scope_revision=1,body={'question_record_id':head['current_question_id'],'text':'C02 historical answer'}))
    return plain({'sources':sources,'memories':memories,'teaching_activity_id':aid,'interview_activity_id':interview,'answer_id':answer,'goal_id':goal,'exercise_id':rid,
        'source_fixture_type':'new normal PG actual constrained synthetic rows; controlled transport receipts; no provider/native/preview'})


def invalidate_event(rt,fixture):
    aid=fixture['teaching_activity_id'];key,rid=str(uuid4()),str(uuid4());body=canonical({'text':'C02 corrected answer'})
    source=fixture['sources']['valid'];refs=canonical([{'source_id':source['id'],'version_id':source['version_id'],'source_revision':source['revision'],'original_sha256':source['sha256']}])
    with rt.gate.acquire(),rt.source.connection() as conn:
        raw=canonical({'fixture':'correction'})
        conn.execute("INSERT INTO public.teaching_commands(activity_id,business_key,action,request_sha256,request_body,slot_sha256,expected_revision,goal_version,scope_revision,status) VALUES(%s,%s,'correct',%s,%s,%s,1,1,1,'history')",(aid,key,digest(raw),raw,digest(key)))
        conn.execute("INSERT INTO public.teaching_records(activity_id,record_id,seq,kind,business_key,ordinal,goal_version,scope_revision,goal_record_id,parent_record_id,body,body_sha256,source_refs) VALUES(%s,%s,4,'correction',%s,1,1,1,%s,%s,%s,%s,%s)",
          (aid,rid,key,fixture['goal_id'],fixture['answer_id'],body,digest(body),refs))
