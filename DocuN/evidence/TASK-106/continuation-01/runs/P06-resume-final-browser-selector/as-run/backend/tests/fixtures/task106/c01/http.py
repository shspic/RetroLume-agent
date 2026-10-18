"""Owned ordinary real server; one config and explicit C01 environment."""
import ctypes,json,os,secrets,subprocess,sys,time
import httpx
from .control import ROOT,EVIDENCE,PERMIT,reserve,atomic_json
from .harness import DATA,MODEL

def birth(pid):
    from ctypes import wintypes
    k=ctypes.WinDLL('kernel32',use_last_error=True);k.OpenProcess.restype=wintypes.HANDLE;handle=k.OpenProcess(0x1000,False,pid)
    if not handle:raise RuntimeError('C01 process no longer alive')
    a=wintypes.FILETIME();b=wintypes.FILETIME();c=wintypes.FILETIME();d=wintypes.FILETIME()
    try:
        if not k.GetProcessTimes(handle,ctypes.byref(a),ctypes.byref(b),ctypes.byref(c),ctypes.byref(d)):raise RuntimeError('C01 birth unavailable')
        return (a.dwHighDateTime<<32)|a.dwLowDateTime
    finally:k.CloseHandle(handle)

def config_value(mode='normal'):
    return dict(model_identity=dict(provider='deepseek_chat_completions',model='task106-c01-forbidden' if mode=='illegal_model' else MODEL),
        activity_defaults=dict(deadline_hours=3,max_requests=24,max_cost_microunits=100000,reserve_cost_microunits=100,max_request_bytes=65536,max_output_tokens=1024,max_running_seconds=3600,allowed_tools=[],max_tool_calls=0),
        service=dict(base_url='https://api.deepseek.com',thinking='disabled',timeout_seconds=1,max_output_tokens_limit=1024,max_request_bytes=131072 if mode=='onecall_limit' else 65536,max_response_bytes=65536),
        api_key_env='RETROLUME_C01_MODEL_KEY',interview=dict(profile='interview.v1',max_output_tokens=512,max_followups_per_round=2),learning=dict(profile='learning.v1',max_output_tokens=256))

def environment(dsn,out,mode='normal'):
    config=EVIDENCE/'synthetic'/('activity-'+mode+'.json');atomic_json(config,config_value(mode));backup=EVIDENCE/'synthetic/backup';backup.mkdir(parents=True,exist_ok=True)
    env=os.environ.copy();env.pop('RETROLUME_TASK106_FIXTURE',None)
    env.update(RETROLUME_DATABASE_URL=dsn,RETROLUME_DATA_DIR=str(DATA),RETROLUME_BACKUP_DIR=str(backup),RETROLUME_ACTIVITY_CONFIG=str(config),
        RETROLUME_C01_MODEL_KEY=secrets.token_urlsafe(24),RETROLUME_TASK106_C01_FIXTURE=PERMIT,PYTHONDONTWRITEBYTECODE='1',PYTHONIOENCODING='utf-8',
        PYTHONPATH=str(ROOT/'backend/tests/fixtures/task106/c01/bootstrap')+';'+str(ROOT/'backend'))
    return env

class Server:
    def __init__(self,dsn,out,mode='normal'):self.dsn,self.out,self.mode=dsn,out,mode;self.process=None
    def __enter__(self):
        self.env=environment(self.dsn,self.out,self.mode);reserve('listener_start',dict(port=18106,mode=self.mode));self.stream=(self.out/('api-'+self.mode+'.log')).open('w',encoding='utf-8')
        self.process=subprocess.Popen([sys.executable,'-m','tests.fixtures.task106.c01.server'],cwd=ROOT/'backend',env=self.env,stdout=self.stream,stderr=self.stream,creationflags=subprocess.CREATE_NO_WINDOW)
        self.identity=dict(pid=self.process.pid,birth_100ns=birth(self.process.pid),command='tests.fixtures.task106.c01.server',port=18106);atomic_json(self.out/('owned-api-'+self.mode+'.json'),self.identity)
        try:
            until=time.perf_counter()+20
            while True:
                try:
                    with httpx.Client(trust_env=False,timeout=1) as c:
                        if c.get('http://127.0.0.1:18106/health').status_code==200:break
                except httpx.HTTPError:pass
                if self.process.poll() is not None or time.perf_counter()>until:raise RuntimeError('C01 owned API startup failed; complete log saved')
                time.sleep(.1)
            return self
        except BaseException:self.__exit__(None,None,None);raise
    def __exit__(self,*args):
        if self.process and self.process.poll() is None:
            assert self.identity['birth_100ns']==birth(self.process.pid);self.process.terminate();self.process.wait(timeout=10)
        self.stream.close();atomic_json(self.out/('api-stop-'+self.mode+'.json'),dict(identity=self.identity,exit_code=self.process.returncode,stopped=self.process.poll() is not None))

class HTTP:
    def __init__(self,out):
        self.out=out;self.items=[];self.client=httpx.Client(base_url='http://127.0.0.1:18106',trust_env=False,timeout=60)
        r=self.client.get('/api/session');assert r.status_code==200;self.headers={'X-RetroLume-Session':r.json()['token'],'Origin':'http://127.0.0.1:18106'}
    def request(self,method,path,**kwargs):
        r=self.client.request(method,path,headers=kwargs.pop('headers',self.headers),**kwargs)
        self.items.append(dict(method=method,path=path,status=r.status_code,body=r.json()));atomic_json(self.out/'http.json',self.items);return r
    def ok(self,method,path,**kwargs):
        r=self.request(method,path,**kwargs);assert r.status_code in (200,201,202),dict(status=r.status_code,body=r.json(),path=path);return r.json()
