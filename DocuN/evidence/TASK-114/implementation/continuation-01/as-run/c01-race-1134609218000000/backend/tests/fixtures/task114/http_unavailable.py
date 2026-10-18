"""source 明确 stopped 时实际本机 HTTP 权威与拒写；不冒恢复成功。"""
import json
import os
import socket
import subprocess
import sys
import time
from uuid import uuid4
from budget import ROOT,CONTROL,Budget
sys.path.insert(0,str(ROOT/'backend'))
from setup_source import reference,memory_guard,IMAGE
from matrix_pg import environment
from freeze import freeze
from app.preview.process import birth
from app.data_exit.restore import inspect_target
from app.data_exit.contracts import canonical


def main():
    budget=Budget();budget.check()
    if not memory_guard()['ready']:print(json.dumps({'state':'not_run','reason':'memory_start_guard'}));return 78
    target,credentials=reference()
    if inspect_target(target,IMAGE)['running']:raise RuntimeError('此批要求 source 已准确 stopped')
    with socket.socket() as probe:probe.bind(('127.0.0.1',18114))
    environment(credentials);freeze('http-source-stopped-01')
    budget.reserve('api_start');budget.reserve('windows_start')
    log=CONTROL/'http-source-stopped-01.log'
    process=None;identity=None
    try:
        with log.open('xb') as stream:
            process=subprocess.Popen([str(ROOT/'backend/.venv/Scripts/python.exe'),'-X','utf8',str(ROOT/'backend/tests/fixtures/task114/api_boot.py')],cwd=ROOT,env=dict(os.environ),stdout=stream,stderr=subprocess.STDOUT,
                                     creationflags=subprocess.CREATE_NO_WINDOW)
            native=birth(process.pid)
            if native['state']!='running':raise RuntimeError('API PID/birth 无法确认')
            identity='api:'+str(process.pid)+':'+str(native['birth'])
            budget.created(identity,'api',{'pid':process.pid,'birth':native['birth'],'port':18114});budget.begin(identity)
            import httpx
            with httpx.Client(base_url='http://127.0.0.1:18114',timeout=5) as client:
                until=time.monotonic()+20
                while True:
                    try:
                        if client.get('/health').status_code==200:break
                    except httpx.TransportError:pass
                    if process.poll() is not None or time.monotonic()>until:raise RuntimeError('API 未就绪')
                    time.sleep(.1)
                token=client.get('/api/session').json()['token'];headers={'X-RetroLume-Session':token}
                caps=client.get('/api/data/capabilities',headers=headers).json()
                if caps['current_mode']!='unavailable' or caps['read_only'] is not True:raise RuntimeError('source stopped 未关闭写入')
                from app.data_exit.control import ControlHub
                hub=ControlHub(ROOT/'DocuN/evidence/TASK-114/synthetic/control-root')
                jobs=list(hub.state()['jobs'].values());before=hub.path.read_bytes()
                reads=[]
                for job in jobs:
                    response=client.get('/api/data/jobs/by-key/'+job['business_key'],headers=headers)
                    if response.status_code!=200 or response.json()['job_id']!=job['job_id']:raise RuntimeError('原 job 不能独立读取')
                    reads.append(job['job_id'])
                if before!=hub.path.read_bytes():raise RuntimeError('GET 改写日志')
                context={key:caps[key] for key in ('control_id','selection_generation','dataset_id','instance_id','current_mode','read_only')}
                post_headers={**headers,'X-RetroLume-Data-Context':canonical(context),'Origin':'http://127.0.0.1:18114'}
                rejected=[]
                for path in ('/api/materials?filename=task114.txt','/api/activities','/api/activities/'+str(uuid4())+'/cancel'):
                    response=client.post(path,content=b'x',headers=post_headers)
                    if response.status_code!=409 or response.json()['code']!='data_readonly':raise RuntimeError('未知源公开写未拒绝')
                    rejected.append(path)
                if client.get('/api/data/packages').status_code!=403:raise RuntimeError('会话认证未生效')
                result={'state':'passed','transport':'actual_tcp_127.0.0.1_18114','source_status':'stopped','mode':caps['current_mode'],
                        'jobs_read':reads,'get_did_not_write':True,'writes_rejected':rejected,'authentication_rejected':True,'restore_verified':False}
                (CONTROL/'http-source-stopped-result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
                print(json.dumps({'state':'passed','jobs_read':len(reads),'writes_rejected':len(rejected)}));return 0
    finally:
        if process is not None:
            if process.poll() is None:process.terminate()
            process.wait(timeout=10)
            ended=birth(process.pid)
            if ended['state']=='running':raise RuntimeError('API 结束未确认')
            if identity is not None:budget.end(identity,{'pid':process.pid,'process_ended':True,'exit_code':process.returncode})


if __name__=='__main__':raise SystemExit(main())
