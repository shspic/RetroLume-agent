"""仅观察原 SUP/Job 及替代 provider transport；不改监督权威。"""
from __future__ import annotations
import asyncio
import json
import os
import sys
import time
import uuid
from dataclasses import asdict
from pathlib import Path
from .control import Ledger,PERMIT,atomic_json,utc

INSTALLED=False

def event(kind,value):
    directory=Path(os.environ['RETROLUME_TASK100_OBSERVATIONS'])
    directory.mkdir(parents=True,exist_ok=True)
    atomic_json(directory/(f'{time.time_ns()}-{os.getpid()}-{uuid.uuid4().hex}-{kind}.json'),
                {'at':utc(),'pid':os.getpid(),'kind':kind,'value':value})

def observe(kind,value):
    try: event(kind,value)
    except BaseException as exc:
        # 观察失败不能阻止原 terminate/close。该异常单独留在完整 stderr。
        sys.stderr.write('TASK100_OBSERVATION_FAILED '+kind+' '+type(exc).__name__+'\n')

async def synthetic_send(self,*,endpoint,api_key,payload,timeout_seconds,max_response_bytes):
    from app.capabilities.transport import TransportResponse,DeliveryUnknown
    from .synthetic_content import output_for
    document=json.loads(next(m['content'] for m in reversed(payload['messages']) if m['role']=='user'))
    mode_path=Path(os.environ['RETROLUME_TASK100_MODE'])
    mode=json.loads(mode_path.read_text(encoding='utf-8')) if mode_path.exists() else {}
    selected=mode.get('mode','normal') if mode.get('action',document['task']['kind'])==document['task']['kind'] else 'normal'
    marker=mode.get('marker','normal')
    event('provider_started',{'marker':marker,'mode':selected,'payload':payload,'timeout_seconds':timeout_seconds})
    if selected=='unknown': raise DeliveryUnknown('合成返回状态未知')
    if selected=='hard_stop': time.sleep(180)
    if selected=='delay':
        release=Path(mode.get('release',os.environ['RETROLUME_TASK100_RELEASE']))
        end=min(time.monotonic()+8,float(os.environ['RETROLUME_TASK100_DEADLINE']))
        while not release.exists():
            if time.monotonic()>=end: raise DeliveryUnknown('合成延迟未释放')
            await asyncio.sleep(.02)
    content=output_for(document)
    if selected=='false_met' and content.get('result_type')=='feedback':
        for observation in content['dimension_observations']: observation['observation']='met'
        content.update(errors=[],evidence_gaps=[],cause_hypotheses=[])
    if selected=='invalid': content['passed']=True
    raw=json.dumps({'id':'task100-'+uuid.uuid4().hex,'object':'chat.completion','model':'synthetic-model-100',
        'choices':[{'index':0,'message':{'role':'assistant','content':json.dumps(content,ensure_ascii=False)},'finish_reason':'stop'}],
        'usage':{'prompt_tokens':128,'completion_tokens':256,'total_tokens':384}},ensure_ascii=False,separators=(',',':')).encode()
    event('provider_returned',{'marker':marker,'content':content,'response_sha256':__import__('hashlib').sha256(raw).hexdigest()})
    return TransportResponse(200,raw,len(raw),'task100-synthetic')

def install():
    global INSTALLED
    if INSTALLED: return
    if os.environ.get('RETROLUME_TASK100_FIXTURE')!=PERMIT: raise RuntimeError('fixture_not_authorized')
    Ledger().load()
    if time.monotonic()>=float(os.environ['RETROLUME_TASK100_DEADLINE']): raise RuntimeError('fixture_deadline')
    from app.capabilities.transport import HttpxModelTransport
    HttpxModelTransport.send=synthetic_send
    from app.worker import launcher
    original_create=launcher._SuspendedSupervisor.create.__func__
    def create(cls,mapping_name):
        if time.monotonic()>=float(os.environ['RETROLUME_TASK100_DEADLINE']): raise RuntimeError('fixture_deadline')
        Ledger().consume('sup_creates',{'mapping_name':mapping_name,'caller_pid':os.getpid()})
        result=original_create(cls,mapping_name)
        try: event('sup_created',{'pid':result.pid,'created_100ns':result.creation_time_100ns(),'mapping_name':mapping_name})
        except BaseException: raise launcher.ProcessCreationError(0,result) from None
        return result
    launcher._SuspendedSupervisor.create=classmethod(create)
    from app.worker import windows_job
    original_job_create=windows_job.NamedJob.create.__func__
    def job_create(cls,activity_id,generation,**kwargs):
        result=original_job_create(cls,activity_id,generation,**kwargs)
        try: event('job_created',{'activity_id':activity_id,'generation':generation,'job_name':result.name})
        except BaseException:
            try: result.terminate()
            finally: result.close()
            raise
        return result
    windows_job.NamedJob.create=classmethod(job_create)
    for name in ('spawn_suspended','resume','terminate','wait_empty_until','close'):
        original=getattr(windows_job.NamedJob,name)
        def wrapper(self,*args,_name=name,_original=original,**kwargs):
            try: return _original(self,*args,**kwargs)
            finally: observe('job_'+_name,{'job_name':self.name,'worker_pid':int(self.process.dwProcessId)})
        setattr(windows_job.NamedJob,name,wrapper)
    from app.learning import teaching_service
    original_model=teaching_service.run_one_call
    def model(*args,**kwargs):
        outcome=original_model(*args,**kwargs)
        observe('session_outcome',asdict(outcome)); return outcome
    teaching_service.run_one_call=model
    from app.worker import one_tool
    original_tool=one_tool.run_one_tool
    def tool(*args,**kwargs):
        outcome=original_tool(*args,**kwargs)
        observe('session_outcome',asdict(outcome)); return outcome
    one_tool.run_one_tool=tool
    # 原短事务行为不变；仅把被产品统一收敛的 SQL 原因保存到本卡证据。
    import psycopg
    original_execute=psycopg.AsyncConnection.execute
    async def execute(self,query,*args,**kwargs):
        try: return await original_execute(self,query,*args,**kwargs)
        except psycopg.Error as exc:
            observe('pg_error',{'sql':str(query),'sqlstate':exc.sqlstate,'message':exc.diag.message_primary}); raise
    psycopg.AsyncConnection.execute=execute
    # Observe lengths at the actual HTTP stream reader; never retain body/auth bytes.
    from app.learning import teaching_api
    original_read=teaching_api._read_bounded_body
    async def bounded_read(request):
        lengths=[]
        class ObservedRequest:
            async def stream(self):
                async for chunk in request.stream():
                    lengths.append(len(chunk));yield chunk
        status=200
        try: return await original_read(ObservedRequest())
        except BaseException as exc:
            status=getattr(exc,'status_code',500);raise
        finally: observe('http_body_stream',{'chunk_lengths':lengths,'bytes_seen':sum(lengths),'status':status,'url_path':request.url.path})
    teaching_api._read_bounded_body=bounded_read
    INSTALLED=True
    import hashlib
    modules={}
    for name in ('app.activities.teaching_repository','app.learning.teaching_service','app.learning.teaching_views',
                 'app.learning.teaching_policy','app.learning.teaching_progress','app.learning.teaching_contracts',
                 'app.learning.teaching_api','tests.fixtures.task100.synthetic_content'):
        module=__import__(name,fromlist=['__file__']);file=Path(module.__file__)
        modules[name]={'path':str(file),'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
    event('fixture_ready',{'argv':sys.argv,'external_network_blocked':True,'transport_only':True,'loaded_modules':modules,
                          'injections':['provider_return','supervisor_job_observation','sql_error_observation','http_stream_lengths']})
