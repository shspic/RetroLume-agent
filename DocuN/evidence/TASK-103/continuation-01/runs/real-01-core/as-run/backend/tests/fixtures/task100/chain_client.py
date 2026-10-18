"""真实本地 HTTP 调用与合成事实观察；固定 localhost，不回显会话 token。"""
from __future__ import annotations
import json
import os
import time
import urllib.request
import urllib.error
from pathlib import Path
from uuid import uuid4
from .control import atomic_json,utc

class Client:
    def __init__(self):
        self.base=os.environ['RETROLUME_TEACHING_HTTP_BASE'];self.timeline=[]
        if self.base!='http://127.0.0.1:18100': raise ValueError('http_resource_not_allowed')
        with urllib.request.urlopen(self.base+'/api/session',timeout=self.timeout(5)) as r: self.token=json.loads(r.read())['token']
    def timeout(self,stage):
        remaining=float(os.environ['RETROLUME_TASK100_DEADLINE'])-time.monotonic()
        if remaining<=0: raise TimeoutError('batch_deadline')
        return min(stage,remaining)
    def request(self,path,body=None,expected=200):
        headers={'X-RetroLume-Session':self.token}
        raw=None
        if body is not None: headers['Content-Type']='application/json';raw=json.dumps(body,ensure_ascii=False).encode()
        began=utc();start=time.monotonic()
        request=urllib.request.Request(self.base+path,data=raw,headers=headers)
        try:
            with urllib.request.urlopen(request,timeout=self.timeout(110)) as response:
                status=response.status;value=json.loads(response.read()); cache=response.headers.get('Cache-Control')
        except urllib.error.HTTPError as exc:
            status=exc.code;value=json.loads(exc.read());cache=exc.headers.get('Cache-Control')
        self.timeline.append({'path':path,'method':'POST' if body is not None else 'GET','body':body,'status':status,'response':value,'started_at':began,'elapsed':time.monotonic()-start,'cache_control':cache})
        if status!=expected: raise AssertionError(f'{path} expected {expected}, actual {status}: '+json.dumps(value,ensure_ascii=False))
        return value
    def workspace(self,aid): return self.request(f'/api/activities/{aid}/teaching/workspace')
    def submit(self,aid,action,body,key=None,view=None,expected=200):
        head=(view or self.workspace(aid))['head']
        cmd={'business_key':key or str(uuid4()),'expected_revision':head['revision'],'expected_goal_version':head['goal_version'],
             'expected_scope_revision':1,'action':action,'body':body}
        return self.request(f'/api/activities/{aid}/teaching/commands',cmd,expected),cmd
    def save(self,path): atomic_json(path,self.timeline)

def wait_provider(directory,marker,deadline):
    while True:
        for file in Path(directory).glob('*provider_started.json'):
            value=json.loads(file.read_text(encoding='utf-8'))
            if value['value']['marker']==marker: return value
        if time.monotonic()>=deadline: raise TimeoutError('provider_start_not_observed')
        time.sleep(.03)
