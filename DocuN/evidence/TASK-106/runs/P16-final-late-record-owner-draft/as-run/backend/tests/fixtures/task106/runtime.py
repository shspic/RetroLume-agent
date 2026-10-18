"""Only lowest transport is synthetic; native SUP/DB/Job/outcomes stay real."""
from __future__ import annotations
import asyncio,json,os,sys,threading,time
from uuid import uuid4
from .control import reserve,event,PERMIT
INSTALLED=False


async def barrier(stage,context):
    if os.environ.get('RETROLUME_TASK106_BARRIER')!=stage:return
    from pathlib import Path
    from .control import ROOT,atomic_json
    folder=ROOT/'backend/tests/fixtures/task106/barriers'/os.environ['RETROLUME_TASK106_BARRIER_KEY']
    folder.mkdir(parents=True,exist_ok=True)
    atomic_json(folder/'entered.json',dict(stage=stage,pid=os.getpid(),context=context,at_ns=time.perf_counter_ns()))
    until=time.perf_counter()+8
    while not (folder/'release.json').exists():
        if time.perf_counter()>until:raise RuntimeError('TASK106 exact barrier expired')
        await asyncio.sleep(.03)


def profile(frame,kind,arg):
    path=frame.f_code.co_filename.replace('\\','/');name=frame.f_code.co_name
    if kind=='call' and name in ('run_one_call','run_one_tool') and '/app/worker/' in path:
        reserve('SUP_attempt',dict(method=name,pid=os.getpid()))
    elif kind=='return' and name in ('run_one_call','run_one_tool') and '/app/worker/' in path and arg is not None:
        keys=('state','activity_id','generation','job_name','pid','active_processes_at_end','settled_seconds','reserved_seconds','cleanup_incomplete','manager_pid','manager_created_100ns','worker_created_100ns')
        event('native-session',{k:getattr(arg,k,None) for k in keys})
    elif kind=='return' and frame.f_code.co_qualname=='_SuspendedSupervisor.create' and '/app/worker/launcher.py' in path and arg is not None:
        event('native-sup',dict(pid=arg.pid,created_100ns=arg.creation_time_100ns()))


async def synthetic_send(self,*,endpoint,api_key,payload,timeout_seconds,max_response_bytes):
    from app.capabilities.transport import TransportResponse,RequestNotSent,DeliveryUnknown
    from app.interview.contracts import canonical,sha
    reserve('transport_send',dict(configured_model=payload['model'],synthetic=True))
    content=next(m['content'] for m in reversed(payload['messages']) if m['role']=='user')
    try:frozen=json.loads(content)
    except (ValueError,TypeError):frozen={}
    scenario=os.environ.get('RETROLUME_TASK106_SCENARIO','normal')
    if scenario=='not_sent':raise RequestNotSent('declared synthetic pre-send failure')
    if scenario=='unknown':raise DeliveryUnknown('declared synthetic delivery unknown')
    if frozen.get('schema')!='interview.context.v1':
        if 'goal' in frozen and 'evidence' in frozen and 'task' not in frozen:
            result=dict(kind='answer',message='合成旧学习回归，仅对照给定算法。',segments=[dict(text='给定算法串行初值100加20减10等于110，不推断现实数据库隔离。',citations=[frozen['evidence'][0]['id']])],questions=[])
        elif frozen.get('task',{}).get('kind')=='plan':
            result=dict(result_type='path',message='合成旧教学路径回归。',nodes=[dict(title='给定余额算法',objective='说明串行值与覆盖风险',prerequisites=[],rationale='按给定资料，不写掌握事实',citations=[frozen['evidence'][0]['id']],completion_dimensions=[dict(dimension='concept',required_point='给定串行值110')])])
        else:result={'message':'TASK106明确合成的旧通用继续结果'}
    else:
        ids=[c['citation_id'] for c in frozen['catalog']]
        goal=frozen['goal_body']['target'];is_history=any(s in goal for s in ('史料','策展','活动X'))
        if is_history:
            per_source={}
            for entry in frozen['catalog']:per_source.setdefault(entry['source_id'],entry['citation_id'])
            ids=list(per_source.values())
        if frozen['action']=='ask':
            if goal.strip().casefold()=='spring':
                result=dict(type='question',purpose='clarification',reason='ambiguous_target',text='资料中Spring含软件框架与季节两种解释，请说明实际领域和具体概念。',reference_ids=ids[:2])
            else:result=dict(type='question',purpose='interview',reason='topic',text='请并列说明两份史料对活动X年份的记载、冲突和需要补充的依据。' if is_history else '请解释给定先读余额再写回算法：100加20减10的串行结果与两个均先读100时的覆盖风险。',reference_ids=ids[:2])
        else:
            answers=[r for r in frozen['parent_record_refs'] if r['kind']=='answer'];last=answers[-1];text=last['body']['value']['text'];aid=last['record_id']
            claims=('60%' in text or '60％' in text) and not any(x in text for x in ('基线100','样本30','口径'))
            recognition=dict(answer_record_id=aid,start_offset=0,end_offset=min(180,len(text)),answer_excerpt=text[:180],reference_ids=ids[:1],semantic_support='supports',explanation='对照冻结资料中的实际算法或用户声明；仅是语义建议。')
            if claims and frozen['probe_depth']<frozen['limits']['max_followups_per_round']:
                result=dict(type='probe',reason='missing_claim_evidence',text='请补充60%主张的基线、统计口径、样本、环境、时间窗口和可核查测量记录。',recognitions=[recognition],gaps=[dict(answer_record_id=aid,text='自报性能收益没有基线和测量依据。',reference_ids=[])],reference_ids=ids[:1])
            else:
                result=dict(type='feedback',summary='对照给定虚构算法，正确部分与缺依据分开；不推断真实PG隔离级别或业绩。' if not is_history else '两份虚构史料分别记2012和2013，年份保持未知，需并列出处。',
                    recognitions=[recognition],gaps=[],conflicts=[dict(text='2012与2013冲突，请补原始档案或同期记录，不能择一当事实。',reference_ids=ids[:2])] if is_history else [],next_steps=['确认是否继续下一题；方向与题数由你选择。'])
        if scenario=='invalid_output':result['authority']=True
        event('synthetic-provider',dict(action=frozen['action'],key=frozen['business_key'],messages_sha256=sha(canonical(payload['messages'])),result=result,
            catalog_ids=ids,usage={'prompt_tokens':128,'completion_tokens':64,'total_tokens':192},oracle='explicit fictional samples; not model self-assessment'))
    response=dict(id='task106-'+uuid4().hex,model=payload['model'],choices=[dict(index=0,message=dict(role='assistant',content=canonical(result)),finish_reason='stop')],
        usage=dict(prompt_tokens=128,completion_tokens=64,total_tokens=192))
    body=canonical(response).encode('utf-8')
    return TransportResponse(200,body,len(body),remote_request_id=response['id'])


def install():
    global INSTALLED
    if INSTALLED:return
    if os.environ.get('RETROLUME_TASK106_FIXTURE')!=PERMIT:raise RuntimeError('TASK106 fixture permit mismatch')
    from app.capabilities.transport import HttpxModelTransport
    HttpxModelTransport.send=synthetic_send
    import psycopg
    original_execute=psycopg.AsyncConnection.execute
    async def observed_execute(self,query,*args,**kwargs):
        try:return await original_execute(self,query,*args,**kwargs)
        except psycopg.Error as exc:
            # SQL text has placeholders; values/DSNs/credentials never copied.
            event('pg-error',dict(sqlstate=exc.sqlstate,message=exc.diag.message_primary,
                constraint=exc.diag.constraint_name,table=exc.diag.table_name,query=str(query)[:3000]))
            raise
    psycopg.AsyncConnection.execute=observed_execute
    from app.activities.repository import PostgresAdmissionLedger
    original_admit=PostgresAdmissionLedger.admit
    original_mark=PostgresAdmissionLedger.mark_dispatch_started
    original_record=PostgresAdmissionLedger.record_outcome
    original_hook=PostgresAdmissionLedger._write_interview_outcome
    async def observed_admit(self,intent):
        if intent.context.operation_id.startswith('int10m.'):
            await barrier('accepted_before_admit',dict(activity_id=intent.context.activity_id,operation_id=intent.context.operation_id))
        return await original_admit(self,intent)
    async def observed_mark(self,permit):
        if permit.operation_id.startswith('int10m.'):
            await barrier('admitted_before_mark',dict(operation_id=permit.operation_id,admission_id=permit.admission_id))
        return await original_mark(self,permit)
    async def observed_record(self,permit,outcome):
        payload=outcome.payload is not None
        if payload and permit.operation_id.startswith('int10m.'):
            await barrier('marked_before_result',dict(operation_id=permit.operation_id,admission_id=permit.admission_id))
        result=await original_record(self,permit,outcome)
        if payload and permit.operation_id.startswith('int10m.'):
            await barrier('committed_before_repair',dict(operation_id=permit.operation_id,admission_id=permit.admission_id))
        return result
    async def observed_hook(self,connection,activity,call,outcome,payload):
        await original_hook(self,connection,activity,call,outcome,payload)
        if payload is not None and os.environ.get('RETROLUME_TASK106_SCENARIO')=='atomic_fail':
            raise RuntimeError('declared fault inside actual native transaction after domain writes before COMMIT')
    PostgresAdmissionLedger.admit=observed_admit
    PostgresAdmissionLedger.mark_dispatch_started=observed_mark
    PostgresAdmissionLedger.record_outcome=observed_record
    PostgresAdmissionLedger._write_interview_outcome=observed_hook
    sys.setprofile(profile);threading.setprofile(profile);INSTALLED=True
