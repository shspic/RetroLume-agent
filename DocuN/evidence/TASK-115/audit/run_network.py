"""一个真实 API/Browser 根；先准入，准确清场，逐阶段保存前缀。"""
import datetime as dt
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time
from bootstrap import ROOT,AUDIT,save
from run_offline import event
sys.path.insert(0,str(ROOT/'backend'))
from app.preview.process import birth

def memory():
    result=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',
        '$m=Get-CimInstance Win32_OperatingSystem; [pscustomobject]@{free_gib=$m.FreePhysicalMemory*1KB/1GB; utc=[DateTime]::UtcNow.ToString("o")} | ConvertTo-Json -Compress'],
        capture_output=True,text=True,timeout=10,creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:raise RuntimeError('内存核查受限，停止真实消费者')
    value=json.loads(result.stdout)
    event('memory',**value)
    if value['free_gib']<2:raise RuntimeError('内存未达到 2 GiB')
    return value

def reserve(field):
    receipt=json.loads((AUDIT/'control/receipt.json').read_text(encoding='utf-8'))
    assert receipt['new_counts'][field]<receipt['limits'][field]
    receipt['new_counts'][field]+=1
    save('control/receipt.json',receipt)

def main():
    attempt=sys.argv[1] if len(sys.argv)>1 else '01'
    memory()
    with socket.socket() as probe:probe.bind(('127.0.0.1',18115))
    if attempt=='01':reserve('roots')
    event('root.begin' if attempt=='01' else 'root.resume',label='D1-final-bundle-controlled-responses',attempt=attempt,timeout_seconds=300)
    output=AUDIT/'browser'/('attempt-'+attempt);output.mkdir(parents=True)
    profile=AUDIT/'synthetic/browser-root'/('attempt-'+attempt);profile.mkdir(parents=True)
    api=None;browser=None;identities=[];chrome=[]
    env=dict(os.environ);env['PYTHONDONTWRITEBYTECODE']='1';env['TASK115_HTTP_ATTEMPT']=attempt
    api_arguments=[str(ROOT/'backend/.venv/Scripts/python.exe'),'-B','-X','utf8',str(AUDIT/'api_fixture.py')]
    browser_arguments=[str(Path('C:/Program Files/nodejs/node.exe')),str(AUDIT/'browser_cases.mjs'),str(ROOT),str(output),str(profile)]
    code=None
    def register(process,kind,arguments):
        info={'resource_kind':kind,'pid':process.pid,'birth':birth(process.pid),'begin_mono':time.monotonic(),'arguments':arguments}
        identities.append(info);event('consumer.begin',**info)
    try:
        reserve('api')
        with (AUDIT/'control'/('api-D1-'+attempt+'.log')).open('xb') as log:
            api=subprocess.Popen(api_arguments,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            register(api,'api',api_arguments)
            import httpx
            with httpx.Client(base_url='http://127.0.0.1:18115',timeout=3) as client:
                deadline=time.monotonic()+20
                while True:
                    try:
                        if client.get('/health').status_code==200:break
                    except httpx.TransportError:pass
                    if time.monotonic()>=deadline or api.poll() is not None:raise RuntimeError('本卡 API 未有界就绪')
                    time.sleep(.05)
                save('control/http-D1-'+attempt+'-auth.json',{'missing_session_status':client.get('/api/data/capabilities').status_code})
            memory();reserve('browser')
            with (AUDIT/'control'/('browser-D1-'+attempt+'-stderr.log')).open('xb') as err:
                browser=subprocess.Popen(browser_arguments,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=err,text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
                register(browser,'browser',browser_arguments)
                lines=[]
                def read():
                    for line in browser.stdout:
                        lines.append(line)
                        try:
                            item=json.loads(line)
                            if item.get('event')=='browser_spawn':
                                item['birth']=birth(item['pid']);chrome.append(item)
                            event('browser.event',detail=item)
                        except ValueError:pass
                thread=threading.Thread(target=read);thread.start()
                code=browser.wait(timeout=120);thread.join(3)
                save('control/browser-D1-'+attempt+'-process.json',{'arguments':browser_arguments,'exit_code':code,'stdout':lines,'chromium_roots':chrome})
    finally:
        for process in (browser,api):
            if process is None:continue
            if process.poll() is None:process.terminate()
            process.wait(timeout=10)
            info=next(v for v in identities if v['pid']==process.pid)
            observed=birth(process.pid)
            if observed['state']=='running':raise RuntimeError('本卡准确进程停止未知')
            held=time.monotonic()-info['begin_mono']
            event('consumer.end',pid=process.pid,birth=info['birth'],observation=observed,seconds=held,exit_code=process.returncode)
            receipt=json.loads((AUDIT/'control/receipt.json').read_text(encoding='utf-8'))
            receipt['new_counts']['holding_seconds']+=held;save('control/receipt.json',receipt)
        for item in chrome:
            observed=birth(item['pid'])
            if observed['state']=='running' and observed.get('birth')==item['birth'].get('birth'):
                raise RuntimeError('Chromium 根停止未知，不能宣清场')
            event('chromium.stop.observed',pid=item['pid'],old_birth=item['birth'],observation=observed)
        with socket.socket() as probe:probe.bind(('127.0.0.1',18115))
        event('root.end',label='D1-final-bundle-controlled-responses',exit_code=code,port18115_bindable=True)
    print(json.dumps({'browser_exit_code':code,'artifact_root':str(output)}))
    return code or 0

if __name__=='__main__':raise SystemExit(main())
