"""Transparent native observers and exact pauses; no authority mock."""
import asyncio,json,os,sys,threading,time
from uuid import uuid4
from .control import EVIDENCE,PERMIT,event,reserve,atomic_json
from .model import response_value

async def barrier(stage,context):
    op=context.get('operation_id','')
    if not op.startswith('int10m.'):return
    from uuid import UUID
    key=str(UUID(op[7:]));plan=EVIDENCE/'barriers'/key/'plan.json'
    if not plan.exists() or stage not in json.loads(plan.read_text()).get('stages',[]):return
    folder=EVIDENCE/'barriers'/key/stage;atomic_json(folder/'entered.json',dict(stage=stage,context=context,pid=os.getpid(),at_ns=time.perf_counter_ns()))
    until=time.perf_counter()+10
    while not (folder/'release.json').exists():
        if time.perf_counter()>until:raise RuntimeError('C01 exact barrier expired')
        await asyncio.sleep(.02)

def profile(frame,kind,arg):
    path=frame.f_code.co_filename.replace('\\','/');name=frame.f_code.co_name
    if kind=='call' and name in ('run_one_call','run_one_tool') and '/app/worker/' in path:reserve('SUP_attempt',dict(method=name,pid=os.getpid()))
    elif kind=='return' and name in ('run_one_call','run_one_tool') and '/app/worker/' in path and arg is not None:
        event('native-session',{k:getattr(arg,k,None) for k in ('state','activity_id','generation','job_name','pid','active_processes_at_end','settled_seconds','reserved_seconds','cleanup_incomplete')})
    elif kind=='return' and frame.f_code.co_qualname=='_SuspendedSupervisor.create' and '/app/worker/launcher.py' in path and arg is not None:
        event('native-sup',dict(pid=arg.pid,created_100ns=arg.creation_time_100ns()))

async def send(self,*,endpoint,api_key,payload,timeout_seconds,max_response_bytes):
    from app.capabilities.transport import TransportResponse
    from app.interview.contracts import canonical,sha
    reserve('transport_send',dict(model=payload['model'],synthetic=True))
    content=next(m['content'] for m in reversed(payload['messages']) if m['role']=='user');data=json.loads(content)
    if data.get('schema')=='interview.context.v1':
        case=json.loads((EVIDENCE/'scenarios'/data['business_key']).read_text()) if (EVIDENCE/'scenarios'/data['business_key']).exists() else {}
        value=response_value(data,case.get('scenario','normal'))
        event('provider',dict(context=data,context_sha256=sha(canonical(data)),value=value,usage=dict(prompt_tokens=128,completion_tokens=64,total_tokens=192),synthetic=True))
    elif 'goal' in data and 'evidence' in data and 'task' not in data:
        value=dict(kind='answer',message='C01旧学习入口小回归，仅给定算法。',segments=[dict(text='给定算法串行值110；现实表现未知。',citations=[data['evidence'][0]['id']])],questions=[])
    elif data.get('task',{}).get('kind')=='plan':
        value=dict(result_type='path',message='C01旧教学入口小回归。',nodes=[dict(title='给定算法',objective='说明串行与覆盖',prerequisites=[],rationale='只按给定资料',citations=[data['evidence'][0]['id']],completion_dimensions=[dict(dimension='concept',required_point='给定串行值110')])])
    else:raise ValueError('C01 fixture unexpected old profile; no generic fallback')
    raw=canonical(dict(id='task106-c01-'+uuid4().hex,model=payload['model'],choices=[dict(index=0,message=dict(role='assistant',content=canonical(value)),finish_reason='stop')],usage=dict(prompt_tokens=128,completion_tokens=64,total_tokens=192))).encode('utf-8')
    return TransportResponse(200,raw,len(raw))

def install():
    if os.environ.get('RETROLUME_TASK106_C01_FIXTURE')!=PERMIT:raise RuntimeError('C01 permit missing')
    from app.capabilities.transport import HttpxModelTransport
    HttpxModelTransport.send=send
    from app.activities.repository import PostgresAdmissionLedger
    original_admit=PostgresAdmissionLedger.admit;original_mark=PostgresAdmissionLedger.mark_dispatch_started;original_record=PostgresAdmissionLedger.record_outcome
    original_finish=PostgresAdmissionLedger.finish_interview_supervision
    async def admit(self,intent):
        await barrier('before_admit',dict(operation_id=intent.context.operation_id));return await original_admit(self,intent)
    async def mark(self,permit):
        await barrier('before_mark',dict(operation_id=permit.operation_id));value=await original_mark(self,permit)
        await barrier('after_mark',dict(operation_id=permit.operation_id));return value
    async def record(self,permit,outcome):
        if outcome.payload is not None:await barrier('before_result',dict(operation_id=permit.operation_id))
        result=await original_record(self,permit,outcome)
        if outcome.payload is not None:await barrier('after_result',dict(operation_id=permit.operation_id))
        return result
    async def finish(self,aid,key,facts):
        await barrier('before_finish',dict(operation_id='int10m.'+key.replace('-',''),facts=facts))
        return await original_finish(self,aid,key,facts)
    PostgresAdmissionLedger.admit=admit;PostgresAdmissionLedger.mark_dispatch_started=mark;PostgresAdmissionLedger.record_outcome=record;PostgresAdmissionLedger.finish_interview_supervision=finish
    sys.setprofile(profile);threading.setprofile(profile)
