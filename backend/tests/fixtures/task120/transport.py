"""Only the lowest provider transport is replaced. PG/SUP/Job stay real."""
import asyncio
import hashlib
import json
import os
from pathlib import Path
import socket
import time


def install():
    if os.environ.get('RETROLUME_TASK120_TESTONLY')!='TASK-120-Q-PREP-IMPLEMENTATION-20261018':return False
    from . import resources as r
    if str(r.state().get('active_root'))!=os.environ.get('RETROLUME_TASK120_ROOT_ID'):raise RuntimeError('task120_fixture_without_root')
    from app.capabilities.transport import HttpxModelTransport,TransportResponse,DeliveryUnknown,RequestNotSent
    if getattr(HttpxModelTransport,'_task120_installed',False):return True
    async def forbid_legacy(self,**kwargs):raise RequestNotSent('TESTONLY_legacy_path_not_permitted')
    async def frozen(self,*,endpoint,api_key,payload_bytes,timeout_seconds,max_response_bytes):
        from app.capabilities.q_gateway import CURRENT
        current=CURRENT.get()
        if current is None:raise RuntimeError('test_transport_without_actual_q_lease')
        p=current.prepared;payload=json.loads(payload_bytes)
        root=r.PRIVATE/os.environ['RETROLUME_TASK120_SLOT']
        faults=json.loads((root/'faults.json').read_text(encoding='utf-8')) if (root/'faults.json').exists() else {}
        mode=faults.get(p['operation_id'],'normal')
        r.event('synthetic_provider_transport',pid=os.getpid(),operation_id=p['operation_id'],prepared_id=p['prepared_id'],
            provider=p['provider'],payload_bytes_sha256=hashlib.sha256(payload_bytes).hexdigest(),external=False,actual_fee_microunits=0,mode=mode)
        if mode=='unknown':raise DeliveryUnknown('TESTONLY_delivery_unknown')
        if mode=='not_sent':raise RequestNotSent('TESTONLY_connection_not_sent')
        if mode=='block':
            ready=root/'transport-ready.json'
            r.write(ready,{'operation_id':p['operation_id'],'pid':os.getpid()},private=True)
            deadline=time.monotonic()+5
            while not (root/'transport-release').exists():
                if time.monotonic()>deadline:raise DeliveryUnknown('TESTONLY_gate_timeout')
                await asyncio.sleep(.01)
        if p['provider']=='zhipu_embeddings':
            if endpoint!='https://open.bigmodel.cn/api/paas/v4/embeddings':raise RuntimeError('fixture_endpoint')
            rows=[]
            for index,text in enumerate(payload['input']):
                vector=[0.0]*512;vector[0]=1.0;vector[1+hashlib.sha256(text.encode()).digest()[0]]=1.0
                rows.append({'index':index,'embedding':vector})
            value={'model':'embedding-3','data':rows,'usage':{'prompt_tokens':sum(len(x) for x in payload['input'])}}
        else:
            if endpoint!='https://api.deepseek.com/chat/completions' or payload['model']!='deepseek-flash':raise RuntimeError('fixture_endpoint')
            from .synthetic_replies import reply
            user=json.loads(next(m['content'] for m in reversed(payload['messages']) if m['role']=='user'))
            if 'evidence' in user and 'task' not in user:
                business={'kind':'answer','message':'合成受控结果；不代表真实服务语义验收','segments':[{'text':user['evidence'][0]['text'][:200],'citations':[user['evidence'][0]['id']]}],'questions':[]}
            else:business=reply(payload)
            value={'id':'TESTONLY.task120','model':'unknown-test-alias' if mode=='unknown_alias' else 'deepseek-flash',
                'choices':[{'index':0,'message':{'role':'assistant','content':json.dumps(business,ensure_ascii=False)},'finish_reason':'stop'}],
                'usage':{'prompt_tokens':100,'completion_tokens':100,'total_tokens':200}}
        body=json.dumps(value,ensure_ascii=False,separators=(',',':')).encode('utf-8')
        return TransportResponse(200,body,len(body))
    HttpxModelTransport.send=forbid_legacy
    HttpxModelTransport.send_frozen=frozen
    HttpxModelTransport.is_external=False
    HttpxModelTransport._task120_installed=True
    original=socket.socket.connect
    def local_only(self,address):
        if isinstance(address,tuple) and address[0] not in ('127.0.0.1','::1','localhost'):
            r.event('external_socket_attempt_denied',pid=os.getpid())
            raise OSError('TASK120_nonloopback_connection_forbidden')
        return original(self,address)
    socket.socket.connect=local_only
    return True
