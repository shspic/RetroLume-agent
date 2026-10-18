"""C02实际TCP API/PG方法：同一根，准确PID/birth，秘密仅在内存扫描。"""
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from dataclasses import replace
from uuid import uuid4
from unittest.mock import patch
from budget import ROOT,EVIDENCE,Budget
from c02_common import Evidence,environment,reference,start_source,stop_source,memory_guard
from c02_pg_run import runtime,FIXTURE
from freeze import freeze
sys.path.insert(0,str(ROOT/'backend'))
from app.preview.process import birth
from app.data_exit.contracts import DataJobCommand,DataError,canonical,digest


class Api:
    def __init__(self,budget,evidence):self.budget,self.evidence=budget,evidence;self.process=None;self.identity=None
    def __enter__(self):
        if not memory_guard()['ready']:raise RuntimeError('API启动内存门')
        with socket.socket() as probe:probe.bind(('127.0.0.1',18114))
        self.budget.reserve('api_start');self.log=(self.evidence.path/'api.log').open('xb')
        self.process=subprocess.Popen([str(ROOT/'backend/.venv/Scripts/python.exe'),'-B','-X','utf8',str(ROOT/'backend/tests/fixtures/task114/c02_api.py')],cwd=ROOT,
          env=dict(os.environ),stdout=self.log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        info=birth(self.process.pid);assert info['state']=='running';self.identity=f"api:{self.process.pid}:{info['birth']}"
        self.budget.created(self.identity,'api',{'pid':self.process.pid,'birth':info['birth'],'port':18114});self.budget.begin(self.identity)
        import httpx
        self.client=httpx.Client(base_url='http://127.0.0.1:18114',timeout=5)
        until=time.monotonic()+20
        while True:
            try:
                if self.client.get('/health').status_code==200:break
            except httpx.TransportError:pass
            if self.process.poll() is not None or time.monotonic()>until:self.__exit__(None,None,None);raise RuntimeError('API未就绪')
            time.sleep(.05)
        token=self.client.get('/api/session').json()['token'];self.evidence.needles.append(token)
        self.headers={'X-RetroLume-Session':token}
        return self
    def __exit__(self,*args):
        if getattr(self,'client',None):self.client.close()
        if self.process:
            if self.process.poll() is None:self.process.terminate()
            self.process.wait(timeout=10)
            if self.identity:self.budget.end(self.identity,{'pid':self.process.pid,'process_ended':True,'exit_code':self.process.returncode})
        if getattr(self,'log',None):self.log.close()


def projection(api,fixture,evidence,restored=False):
    caps=api.client.get('/api/data/capabilities',headers=api.headers).json();ctx={n:caps[n] for n in ('control_id','selection_generation','dataset_id','instance_id','current_mode','read_only')}
    headers={**api.headers,'X-RetroLume-Data-Context':canonical(ctx)};responses={}
    for category in ('memories','learning','teaching','interview'):
        response=api.client.get('/api/data/saved-records',params={'category':category},headers=headers);assert response.status_code==200
        value=response.json();assert value['data_context']==ctx;responses[category]=value
    memories=responses['memories']['items'];mid=fixture['memories']['delete']['memory_id'];masked=next(i for i in memories if i['record']['memory_id']==mid)
    assert masked['availability']=='source_deleted' and masked['record']['body'] is None
    valid=next(i for i in memories if i['record']['memory_id']==fixture['memories']['valid']['memory_id']);assert valid['availability']=='present' and valid['record']['body'] is not None
    assert responses['learning']['items'] and all(i['record']['payload'] is None and i['availability']=='source_deleted' for i in responses['learning']['items'])
    assert responses['interview']['items'] and all(i['record']['local_body'] is None and i['availability']=='source_deleted' for i in responses['interview']['items'])
    assert any(i['record']['body'] is not None for i in responses['teaching']['items'])
    if not restored:
        for name in ('replace','event','downstream'):
            item=next(i for i in memories if i['record']['memory_id']==fixture['memories'][name]['memory_id']);assert item['record']['body'] is None and item['availability']=='dependency_invalid'
    evidence.save('HTTP-projections',{'layer':'actual 127.0.0.1 TCP / new actual PG / Selector loop, no mocks','restored':restored,'caps':caps,'responses':responses})
    return caps,headers


def source_http(budget,evidence,source,credentials,fixture):
    start_source(budget,source);rt=runtime(credentials,budget)
    # 真PG capture后完整链只有一个2秒D；延迟精确在publication调用前。
    from app.data_exit import packages
    limits=replace(rt.limits,operation_seconds=2);service=packages.DataPackageService(rt.hub,rt.packages.snapshot,rt.settings.backup_dir,limits)
    job=rt.hub.create_or_get_job(DataJobCommand('restore_checkpoint','c02-real-pg-deadline-'+str(uuid4()),{'mode':'all'}),rt.context())
    link=packages.publish
    def late(*args,**kwargs):time.sleep(2.1);return link(*args,**kwargs)
    before=time.monotonic()
    with patch.object(packages,'publish',late):
        try:service.capture_and_publish(job['job_id'],{'mode':'all'})
        except DataError as error:assert error.code=='operation_timeout'
        else:raise AssertionError('真实PG后段期限未拒绝')
    facts=rt.hub.state()['jobs'][job['job_id']];assert facts['execution']['deadline_ns']-facts['execution']['started_ns']==2000000000
    assert not service.path(job['job_id']).exists();evidence.save('real-PG-whole-deadline',{'job':rt.hub.get(job['job_id']),'elapsed':time.monotonic()-before,'one_D_seconds':2,'no_publication':True,'layer':'actual new PG snapshot/real files; publication delay controlled'})
    marker='C02_PRIVATE_CHECK_'+uuid4().hex
    private=rt.hub.create_or_get_job(DataJobCommand('portable_export','c02-private-marker-'+str(uuid4()),{'mode':'all'}),rt.context())
    rt.hub.update_job(private['job_id'],private['revision'],expected_states=('prepared',),state='failed',stage='failed',private_test_marker=marker)
    evidence.needles.append(marker)
    with Api(budget,evidence) as api:
        caps,headers=projection(api,fixture,evidence)
        public=[]
        for key in (fixture['package_key'],private['business_key']):
            response=api.client.get('/api/data/jobs/by-key/'+key,headers=api.headers);assert response.status_code==200;public.append(response.content)
        invalid=api.client.post('/api/data/jobs',headers={**headers,'Origin':'http://127.0.0.1:18114'},json={'kind':'portable_export','business_key':'c02-invalid','confirm':True,'private_input':marker})
        assert invalid.status_code==422 and invalid.json()['code']=='invalid_input';public.append(invalid.content)
        # 实际HTTP hash conflict，同键不创建新consumer。
        conflict=api.client.post('/api/data/jobs',headers=headers,json={'kind':'portable_export','business_key':fixture['package_key'],'scope':{'mode':'all'},'confirm':True})
        assert conflict.status_code==409 and conflict.json()['code']=='request_conflict';public.append(conflict.content)
        # 实际TCP上传中断，不是受控ASGI回包；待准确worker失败后GET原键。
        token=api.headers['X-RetroLume-Session'];key='c02-TCP-disconnect-'+str(uuid4());uid=str(uuid4());url='/api/data/uploads?business_key='+key+'&upload_id='+uid+'&expected_sha256='+('a'*64)+'&expected_bytes=1024'
        with socket.create_connection(('127.0.0.1',18114),timeout=3) as sock:
            data=(f'POST {url} HTTP/1.1\r\nHost: 127.0.0.1:18114\r\nX-RetroLume-Session: {token}\r\nContent-Length: 1024\r\nConnection: close\r\n\r\n').encode()+b'partial only'
            sock.sendall(data)
        until=time.monotonic()+5;uploaded=None
        while time.monotonic()<until:
            response=api.client.get('/api/data/jobs/by-key/'+key,headers=api.headers)
            if response.status_code==200 and response.json()['state'] not in ('prepared','running'):uploaded=response.json();break
            time.sleep(.05)
        assert uploaded is not None and uploaded['state'] not in ('received','published');assert not (rt.incoming/(uid+'.rldata')).exists()
        evidence.save('TCP-upload-disconnect',{'job':uploaded,'received_file':False,'layer':'actual TCP Content-Length mismatch/client close, actual API handler'})
        public.append(json.dumps(uploaded).encode())
        needles=[n.encode() for n in evidence.needles if n]
        assert all(not any(n in content for n in needles) for content in public)
        evidence.save('HTTP-secret-and-conflict',{'malformed_status':invalid.status_code,'malformed_body':invalid.json(),'hash_conflict':conflict.json(),'private_fields_absent':True,'ordinary_DTO_needles_absent':True,'session_endpoint_token':'explicit auth bootstrap exempt only named token'})
    log=(evidence.path/'api.log').read_bytes();assert not any(n.encode() in log for n in evidence.needles if n)
    evidence.save('ordinary-log-scan',{'actual_API_log_bytes':len(log),'needle_count':len(evidence.needles),'matches':0,'raw_needle_values_not_output':True})


def main():
    budget=Budget();budget.check();source,credentials=reference();fixture=json.loads(FIXTURE.read_bytes());label='c02-http-source-'+str(time.monotonic_ns());evidence=Evidence(label,credentials)
    budget.root('c02-pg-group');freeze(label)
    try:source_http(budget,evidence,source,credentials,fixture);evidence.save('result',{'state':'passed'});return 0
    except BaseException as error:evidence.fail(error);return 1
    finally:stop_source(budget,source)


if __name__=='__main__':raise SystemExit(main())
