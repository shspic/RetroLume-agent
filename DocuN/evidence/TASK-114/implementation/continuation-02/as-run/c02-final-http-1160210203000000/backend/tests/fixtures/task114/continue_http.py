"""真实18114认证/旧键/下载与现有bundle浏览器，不伪造selector。"""
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from uuid import uuid4
from budget import ROOT,EVIDENCE,Budget
from setup_source import reference,memory_guard,IMAGE
from matrix_pg import environment
from freeze import freeze
from continue_run import Evidence
from app.preview.process import birth
from app.data_exit.restore import inspect_target
from app.data_exit.contracts import canonical

def main():
    budget=Budget();budget.check()
    if not memory_guard()['ready']:return 78
    source,credentials=reference()
    if inspect_target(source,IMAGE)['running']:raise RuntimeError('不可用状态方法要求source准确停止')
    label='c01-http-unavailable-'+str(time.monotonic_ns());evidence=Evidence(label,credentials)
    budget.root('c01-http-unavailable-group');freeze(label);environment(credentials)
    with socket.socket() as sock:sock.bind(('127.0.0.1',18114))
    process=None;identity=None;browser=None;browser_identity=None
    budget.reserve('api_start');budget.reserve('windows_start')
    try:
        with (evidence.path/'api.log').open('xb') as log:
            process=subprocess.Popen([str(ROOT/'backend/.venv/Scripts/python.exe'),'-X','utf8',str(ROOT/'backend/tests/fixtures/task114/api_boot.py')],env=dict(os.environ),cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            actual=birth(process.pid);identity='api:'+str(process.pid)+':'+str(actual['birth'])
            budget.created(identity,'api',{'pid':process.pid,'birth':actual['birth'],'port':18114});budget.begin(identity)
            import httpx
            with httpx.Client(base_url='http://127.0.0.1:18114',timeout=5) as client:
                until=time.monotonic()+20
                while True:
                    try:
                        if client.get('/health').status_code==200:break
                    except httpx.TransportError:pass
                    if process.poll() is not None or time.monotonic()>until:raise RuntimeError('API未就绪')
                    time.sleep(.1)
                token=client.get('/api/session').json()['token'];headers={'X-RetroLume-Session':token}
                caps=client.get('/api/data/capabilities',headers=headers).json()
                if caps['current_mode']!='unavailable' or caps['read_only'] is not True:raise RuntimeError('source不可用写门未关闭')
                evidence.observe('01-caps',caps)
                from app.data_exit.control import ControlHub
                hub=ControlHub(ROOT/'DocuN/evidence/TASK-114/synthetic/control-root');before=hub.path.read_bytes()
                jobs=list(hub.state()['jobs'].values());results=[]
                for job in jobs:
                    response=client.get('/api/data/jobs/by-key/'+job['business_key'],headers=headers)
                    if response.status_code!=200 or response.json()['job_id']!=job['job_id']:raise RuntimeError('原键只读核对失败')
                    results.append({'job_id':job['job_id'],'state':response.json()['state'],'status':response.status_code})
                response=client.get('/api/data/packages/737bf7ba-18c2-436c-a011-3aabbc1a8b2b/content',headers=headers)
                if response.status_code!=200 or hashlib.sha256(response.content).hexdigest()!='45177d58ea58fcaa704bfdd48641aceade7ca6e6f4fe5d6759b3a46bf2671665':raise RuntimeError('真实HTTP旧包下载失败')
                context={k:caps[k] for k in ('control_id','selection_generation','dataset_id','instance_id','current_mode','read_only')}
                postheaders={**headers,'Origin':'http://127.0.0.1:18114','X-RetroLume-Data-Context':canonical(context)}
                negatives=[]
                for route in ('/api/materials?filename=c01.txt','/api/activities','/api/activities/'+str(uuid4())+'/cancel'):
                    response=client.post(route,content=b'x',headers=postheaders)
                    negatives.append({'path':route,'status':response.status_code,'code':response.json().get('code')})
                    if response.status_code!=409 or response.json().get('code')!='data_readonly':raise RuntimeError('恶意POST未拒绝')
                if before!=hub.path.read_bytes():raise RuntimeError('GET/被拒动作改写Hub')
                if client.get('/api/data/packages').status_code!=403:raise RuntimeError('未认证GET未拒绝')
                evidence.observe('02-http-truth',{'old_jobs':results,'negatives':negatives,'package_sha256_verified':True,'unauthenticated_rejected':True,'journal_unchanged':True,'source_stopped':True})
                if not memory_guard()['ready']:raise RuntimeError('浏览器启动内存门不足；HTTP结果已经保存')
                output=evidence.path/'browser';output.mkdir()
                profile=ROOT/'DocuN/evidence/TASK-114/synthetic/scratch'/('c01-browser-'+str(uuid4()));profile.mkdir()
                budget.reserve('browser_start');budget.reserve('windows_start')
                args=[str(Path('C:/Program Files/nodejs/node.exe')),str(ROOT/'frontend/tests/task114-c01-browser.mjs'),str(output),str(profile),next(j['business_key'] for j in jobs if j['job_id']=='737bf7ba-18c2-436c-a011-3aabbc1a8b2b')]
                browser=subprocess.Popen(args,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
                actual=birth(browser.pid);browser_identity='browser:'+str(browser.pid)+':'+str(actual['birth'])
                budget.created(browser_identity,'browser',{'pid':browser.pid,'birth':actual['birth'],'profile':str(profile)});budget.begin(browser_identity)
                stdout,stderr=browser.communicate(timeout=60)
                evidence.observe('03-browser-process',{'arguments':args,'exit_code':browser.returncode,'stdout':stdout,'stderr':stderr,'process_ended':True})
                if browser.returncode:raise RuntimeError('真实浏览器方法失败，已保存原进程日志')
                if hashlib.sha256((output/'downloaded.rldata').read_bytes()).hexdigest()!='45177d58ea58fcaa704bfdd48641aceade7ca6e6f4fe5d6759b3a46bf2671665':raise RuntimeError('浏览器下载字节不同')
                evidence.observe('result',{'state':'passed','http':'actual_tcp','browser':'actual_existing_chromium','scope':'source unavailable + old keys/package + disabled backup + unsubmitted draft + GET-only refresh; no selector activation'})
                budget.close_root('c01-http-unavailable-group');return 0
    except BaseException as error:evidence.fail(error);return 1
    finally:
        for child,ident in ((browser,browser_identity),(process,identity)):
            if child is None:continue
            if child.poll() is None:child.terminate()
            child.wait(timeout=10)
            if birth(child.pid)['state']=='running':raise RuntimeError('精确子进程结束未知')
            if ident is not None:budget.end(ident,{'pid':child.pid,'process_ended':True,'exit_code':child.returncode})
        evidence.observe('99-source-still-stopped',inspect_target(source,IMAGE))

if __name__=='__main__':raise SystemExit(main())
