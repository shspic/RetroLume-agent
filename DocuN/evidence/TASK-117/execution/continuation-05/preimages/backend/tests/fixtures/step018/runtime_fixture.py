"""TASK117明确的最低合成传输；不替换ledger、时钟、SUP、Job或数据库。"""
import hashlib
import json
import os
from pathlib import Path
import time
import sys
import threading


def install():
    if os.environ.get('RETROLUME_TASK117_SYNTHETIC') not in (
        'TASK-117-STEP018-INTEGRATION-S01-20261014',
        'TASK-117-STEP018-INTEGRATION-S02-20261015','TASK-117-STEP018-INTEGRATION-S03-20261015','TASK-117-STEP018-INTEGRATION-S04-20261016','TASK-117-STEP018-INTEGRATION-S05-20261016',
    ):return False
    from app.capabilities.transport import HttpxModelTransport,TransportResponse
    async def send(self,*,endpoint,api_key,payload,timeout_seconds,max_response_bytes):
        if endpoint=='https://api.deepseek.com/chat/completions' and payload.get('model')=='deepseek-chat':
            from synthetic_replies import reply
            value=reply(payload)
            response={'id':'syn18.model','model':'deepseek-chat','choices':[{'index':0,'message':{'role':'assistant','content':json.dumps(value,ensure_ascii=False)},'finish_reason':'stop'}],'usage':{'prompt_tokens':100,'completion_tokens':100,'total_tokens':200}}
            body=json.dumps(response,ensure_ascii=False,separators=(',',':')).encode('utf-8')
            path=os.environ.get('RETROLUME_TASK117_TRANSPORT_LOG')
            if path:
                with Path(path).open('a',encoding='utf-8') as stream:stream.write(json.dumps({'kind':'synthetic_transport','pid':os.getpid(),'mono_ns':time.monotonic_ns(),'capability':'model','request_sha256':hashlib.sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),'response_bytes':len(body),'real_http':False,'actual_fee':0})+'\n')
            return TransportResponse(200,body,len(body))
        if endpoint!='https://open.bigmodel.cn/api/paas/v4/embeddings' or payload.get('model')!='embedding-3':
            raise RuntimeError('synthetic_capability_not_implemented')
        if payload.get('input')==['S02合成超时']:
            # 仅受本卡fixture许可的最低传输故障，准入/dispatch/UNKNOWN仍走正式链。
            raise TimeoutError('synthetic_delivery_timeout')
        if payload.get('input')==['S02晚到记忆']:
            # Dispatch has already been admitted by the real ledger/worker. Only transport waits.
            import asyncio
            folder=Path(os.environ['RETROLUME_TASK117_LATE_GATE']);folder.mkdir(exist_ok=True)
            (folder/'ready.json').write_text(json.dumps({'pid':os.getpid(),'mono_ns':time.monotonic_ns(),'input_sha256':hashlib.sha256(payload['input'][0].encode()).hexdigest()}),encoding='utf-8')
            until=time.monotonic()+8
            while not(folder/'release').exists():
                if time.monotonic()>=until:raise TimeoutError('synthetic_late_release_timeout')
                await asyncio.sleep(.02)
        inputs=payload['input'];rows=[]
        for index,text in enumerate(inputs):
            raw=hashlib.sha256(text.encode('utf-8')).digest();vector=[0.0]*512
            vector[0]=1.0;vector[1+int.from_bytes(raw[:2],'little')%511]=float(1+raw[2]%3)
            rows.append({'index':index,'embedding':vector})
        reply={'id':'syn18.embedding','model':'embedding-3','data':rows,'usage':{'prompt_tokens':sum(len(x) for x in inputs)}}
        body=json.dumps(reply,separators=(',',':')).encode('utf-8')
        path=os.environ.get('RETROLUME_TASK117_TRANSPORT_LOG')
        if path:
            value={'kind':'synthetic_transport','pid':os.getpid(),'mono_ns':time.monotonic_ns(),'capability':'embedding',
                   'inputs_sha256':[hashlib.sha256(x.encode('utf-8')).hexdigest() for x in inputs],'response_bytes':len(body),
                   'real_http':False,'actual_fee':0}
            with Path(path).open('a',encoding='utf-8') as stream:stream.write(json.dumps(value)+'\n')
        return TransportResponse(200,body,len(body))
    HttpxModelTransport.is_external=False
    HttpxModelTransport.send=send
    def local_trace(frame,event,arg):
        if event=='exception' and arg[0] not in (StopIteration,StopAsyncIteration):
            error=arg[1];diag=getattr(error,'diag',None)
            value={'kind':'pg_admission_exception','pid':os.getpid(),'function':frame.f_code.co_name,'line':frame.f_lineno,
                   'exception_type':type(error).__name__,'sqlstate':getattr(error,'sqlstate',None),
                   'message_primary':getattr(diag,'message_primary',None),'constraint':getattr(diag,'constraint_name',None)}
            if '/pdf_import/' in frame.f_code.co_filename.replace('\\','/').lower():
                value.update(kind='pdf_original_exception',code=getattr(error,'code',None),safe_message=str(error)[:300] if type(error).__module__=='app.pdf_import.errors' else None)
            path=os.environ.get('RETROLUME_TASK117_TRANSPORT_LOG')
            if path:
                with Path(path).open('a',encoding='utf-8') as stream:stream.write(json.dumps(value)+'\n')
        return local_trace
    def global_trace(frame,event,arg):
        name=frame.f_code.co_filename.replace('\\','/').lower()
        if name.endswith(('/app/retrieval/repository.py','/app/activities/repository.py','/app/activities/interview_repository.py','/app/pdf_import/supervisor.py')):return local_trace
        return None
    if os.environ.get('RETROLUME_TASK117_TRACE_PG')=='1':
        sys.settrace(global_trace);threading.settrace(global_trace)
    return True
