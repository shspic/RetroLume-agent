"""Real session/Origin HTTP and final built frontend; no server/UI mocks."""
from __future__ import annotations
import asyncio,ctypes,json,os,secrets,subprocess,sys,time
from pathlib import Path
from uuid import uuid4
import httpx
from .control import ROOT,EVIDENCE,PERMIT,batch,reserve,atomic_json
from .resources import start,stop,runtime
from .samples import SAMPLES,T_NAME,H1_NAME,H2_NAME,CV_NAME,ORACLE,HASHES


def process_birth(pid):
    from ctypes import wintypes
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.OpenProcess.restype=wintypes.HANDLE
    handle=kernel.OpenProcess(0x1000,False,pid)
    if not handle:raise RuntimeError('own process identity unavailable')
    a=wintypes.FILETIME();b=wintypes.FILETIME();c=wintypes.FILETIME();d=wintypes.FILETIME()
    try:
        if not kernel.GetProcessTimes(handle,ctypes.byref(a),ctypes.byref(b),ctypes.byref(c),ctypes.byref(d)):raise RuntimeError('own birth unavailable')
        return (a.dwHighDateTime<<32)|a.dwLowDateTime
    finally:kernel.CloseHandle(handle)


def app_environment(app_dsn,folder):
    data=EVIDENCE/'synthetic/http/data';backup=EVIDENCE/'synthetic/http/backup'
    data.mkdir(parents=True,exist_ok=True);backup.mkdir(parents=True,exist_ok=True)
    config=dict(model_identity=dict(provider='deepseek_chat_completions',model='task106-synthetic'),
        activity_defaults=dict(deadline_hours=3,max_requests=20,max_cost_microunits=100000,reserve_cost_microunits=100,max_request_bytes=65536,max_output_tokens=1024,max_running_seconds=3600,allowed_tools=[],max_tool_calls=0),
        service=dict(base_url='https://api.deepseek.com',thinking='disabled',timeout_seconds=1.0,max_output_tokens_limit=1024,max_request_bytes=65536,max_response_bytes=65536),
        api_key_env='RETROLUME_TASK106_MODEL_KEY',interview=dict(profile='interview.v1',max_output_tokens=512,max_followups_per_round=2))
    path=EVIDENCE/'synthetic/http/activity.synthetic.json';atomic_json(path,config)
    env=os.environ.copy();env.update(RETROLUME_DATA_DIR=str(data),RETROLUME_BACKUP_DIR=str(backup),RETROLUME_DATABASE_URL=app_dsn,
        RETROLUME_ACTIVITY_CONFIG=str(path),RETROLUME_TASK106_MODEL_KEY=secrets.token_urlsafe(24),RETROLUME_TASK106_FIXTURE=PERMIT,
        PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(ROOT/'backend/tests/fixtures/task106/bootstrap')+';'+str(ROOT/'backend'))
    return env


class HTTP:
    def __init__(self,folder):
        self.folder=folder;self.observations=[]
        self.client=httpx.Client(base_url='http://127.0.0.1:18106',timeout=65,trust_env=False)
        session=self.client.get('/api/session')  # Native bootstrap deliberately has no Origin.
        assert session.status_code==200,dict(status=session.status_code,body=session.text)
        self.token=session.json()['token'];self.headers={'X-RetroLume-Session':self.token,'Origin':'http://127.0.0.1:18106'}
    def request(self,method,path,**kwargs):
        response=self.client.request(method,path,headers=kwargs.pop('headers',self.headers),**kwargs)
        try:body=response.json()
        except ValueError:body={'non_json':response.text[:1000]}
        # No cookie/session token or password is saved in observations.
        self.observations.append(dict(method=method,path=path,status=response.status_code,body=body))
        atomic_json(self.folder/'http.json',self.observations)
        return response
    def ok(self,method,path,**kwargs):
        r=self.request(method,path,**kwargs);assert r.status_code in (200,201,202),dict(status=r.status_code,body=r.text[:5000],path=path)
        return r.json()
    def command(self,aid,action,body,*,key=None):
        v=self.ok('GET',f'/api/activities/{aid}/interview/workspace');h=v['head'] or {}
        request=dict(schema='interview.command.v1',business_key=key or str(uuid4()),action=action,expected_head_revision=h.get('revision',0),expected_goal_version=h.get('goal_version',0),expected_scope_revision=h.get('scope_revision',1),body=body)
        return self.ok('POST',f'/api/activities/{aid}/interview/commands',json=request),request


def verify(http,folder):
    unauthorized=http.request('GET','/api/activities',headers={});assert unauthorized.status_code==403,unauthorized.text
    foreign=http.request('GET','/api/activities',headers={'X-RetroLume-Session':http.token,'Origin':'https://foreign.invalid'});assert foreign.status_code==403,foreign.text
    materials={}
    for name in (T_NAME,H1_NAME,H2_NAME,CV_NAME):
        value=http.ok('POST','/api/materials',params={'filename':name},content=SAMPLES[name].encode('utf-8'),headers={**http.headers,'Origin':'http://127.0.0.1:5173','Content-Type':'application/octet-stream'})
        materials[name]=value['material'];assert materials[name]['sha256']==HASHES[name]
    aid=str(uuid4());http.ok('POST','/api/activities',json={'activity_id':aid,'source_ids':[materials[T_NAME]['id']]})
    receipt,request=http.command(aid,'start',{'goal':{'target':'余额算法串行与覆盖','material_roles':[{'source_id':materials[T_NAME]['id'],'role':'reference'}]}})
    assert receipt['effect_applied']
    # Schema/input errors and closed public authority are real HTTP, not only contract constructors.
    bad={**request,'business_key':str(uuid4()),'budget':0}
    response=http.request('POST',f'/api/activities/{aid}/interview/commands',json=bad);assert response.status_code==422,response.text
    unknown=http.request('POST',f'/api/activities/{aid}/interview/commands',content=b'{"schema":"x","schema":"y"}',headers={**http.headers,'Content-Type':'application/json'});assert unknown.status_code==422,unknown.text
    q,ask_request=http.command(aid,'ask',{'mode':'first'});assert q['status']=='committed',q
    # Simulate the already-lost response by retaining only original key; subsequent GET/POST are actual HTTP.
    stored=http.ok('GET',f'/api/activities/{aid}/interview/commands/{q["business_key"]}')
    assert stored['record_ids']==q['record_ids']
    replay=http.ok('POST',f'/api/activities/{aid}/interview/commands',json=ask_request);assert replay['record_ids']==q['record_ids']
    v=http.ok('GET',f'/api/activities/{aid}/interview/workspace')
    a,_=http.command(aid,'answer',{'question_record_id':v['head']['current_question_id'],'text':'🧭串行得到110；两个都先读100时可能覆盖写回。这只针对给定算法。'})
    v=http.ok('GET',f'/api/activities/{aid}/interview/workspace')
    f,_=http.command(aid,'review',{'question_record_id':v['head']['current_question_id'],'answer_record_id':v['head']['current_answer_id']});assert f['status']=='committed',f
    d=http.ok('GET',f'/api/activities/{aid}/interview/records/{f["record_ids"][0]}')
    assert d['body']['value']['recognitions'][0]['verification_kind']=='source_interpretation',d
    catalog=d['body']['catalog'];c=http.ok('GET',f'/api/activities/{aid}/interview/records/{f["record_ids"][0]}/citations/{catalog[0]["citation_id"]}',params={'view_token':d['view_token']})
    assert c['position_verified']
    hist=http.ok('GET',f'/api/activities/{aid}/interview/history');assert all('payload' not in r and 'local_body' not in r for r in hist['records'])
    wrong=http.request('GET',f'/api/activities/{aid}/interview/records/{q["record_ids"][0]}',params={'view_token':'0'*64});assert wrong.status_code==409 and wrong.json()['code']=='interview_view_changed',wrong.text
    # Generic profile consumption and local teaching head are refused for this domain.
    cont=http.request('POST',f'/api/activities/{aid}/continuations',json={'parent_operation_id':q.get('operation_id') or stored['operation_id'],'new_operation_id':'task106-forbidden','followup':'继续'});assert cont.status_code==409,cont.text
    http.command(aid,'finish',{})
    final=http.ok('GET',f'/api/activities/{aid}/interview/workspace');assert final['head']['phase']=='ended'
    atomic_json(folder/'http-summary.json',dict(aid=aid,materials=materials,final=final,oracle=ORACLE))
    return materials


def main():
    with batch(os.environ.get('RETROLUME_TASK106_HTTP_GROUP','P09-real-http-final-dist-chain')) as folder:
        process=None;stream=None;identity=None
        try:
            admin=start(1);app,denied=runtime(admin);env=app_environment(app,folder)
            reserve('listener_start',{'port':18106,'kind':'synthetic-api'})
            stream=(folder/'api-log.txt').open('w',encoding='utf-8')
            process=subprocess.Popen([sys.executable,'-m','tests.fixtures.task106.server'],cwd=ROOT/'backend',env=env,stdout=stream,stderr=stream,creationflags=subprocess.CREATE_NO_WINDOW)
            identity=dict(pid=process.pid,birth_100ns=process_birth(process.pid),command='tests.fixtures.task106.server',port=18106)
            atomic_json(folder/'owned-api.json',identity)
            until=time.perf_counter()+20
            while True:
                try:
                    with httpx.Client(trust_env=False,timeout=1) as client:r=client.get('http://127.0.0.1:18106/health')
                    if r.status_code==200:break
                except httpx.HTTPError:pass
                if process.poll() is not None or time.perf_counter()>until:raise RuntimeError('owned API startup failed; saved complete nonsecret log')
                time.sleep(.15)
            http=HTTP(folder)
            try:materials=verify(http,folder)
            finally:http.client.close()
            print(json.dumps(dict(http=True,ordinary_runtime=True,session_origin=True,complete_chain=True,dist=True)))
        finally:
            if process and process.poll() is None:
                assert identity['birth_100ns']==process_birth(process.pid);process.terminate();process.wait(timeout=10)
            if stream:stream.close()
            if process:atomic_json(folder/'api-stop.json',dict(identity=identity,exit_code=process.returncode,stopped=process.poll() is not None))
            stop(1)


if __name__=='__main__':main()
