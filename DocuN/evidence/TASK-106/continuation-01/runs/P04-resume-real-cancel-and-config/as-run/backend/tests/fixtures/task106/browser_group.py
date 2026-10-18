"""One exact final build/ordinary HTTP/native/Chromium root; bounded cleanup."""
import json,os,subprocess,sys,time
from .control import ROOT,EVIDENCE,batch,reserve,atomic_json
from .resources import start,stop,runtime
from .http_group import app_environment,process_birth,HTTP
from .samples import T_NAME,H1_NAME,H2_NAME
import httpx
from uuid import uuid4


def main():
    with batch(os.environ.get('RETROLUME_TASK106_BROWSER_GROUP','P11-final-real-browser-lifecycle')) as folder:
        process=None;stream=None;node=None;identity=None
        try:
            admin=start(1);app,denied=runtime(admin);env=app_environment(app,folder)
            reserve('listener_start',{'port':18106,'kind':'final-browser-api'})
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
                if process.poll() is not None or time.perf_counter()>until:raise RuntimeError('owned browser API startup failure')
                time.sleep(.15)
            http=HTTP(folder)
            previous=json.loads((EVIDENCE/'runs/P10-http-origin-correct-complete-chain/http-summary.json').read_text(encoding='utf-8'))
            materials=previous['materials'];other=str(uuid4())
            resume=os.environ.get('RETROLUME_TASK106_BROWSER_RESUME')
            if resume:
                technical=json.loads((EVIDENCE/'runs/P11-final-real-browser-lifecycle/browser-seed.json').read_text(encoding='utf-8'))['technical']
            else:
                technical=str(uuid4())
                http.ok('POST','/api/activities',json={'activity_id':technical,'source_ids':[materials[T_NAME]['id']]})
            http.ok('POST','/api/activities',json={'activity_id':other,'source_ids':[materials[H1_NAME]['id'],materials[H2_NAME]['id']]})
            seed=dict(technical=technical,other=other,technicalTitle=materials[T_NAME]['title'],materialIds={k:v['id'] for k,v in materials.items()},resumeOnly=bool(resume),closureOnly=bool(os.environ.get('RETROLUME_TASK106_BROWSER_CLOSURE')))
            seedpath=folder/'browser-seed.json';atomic_json(seedpath,seed)
            http.client.close()
            reserve('driver',{'runner':'frontend/tests/task106-interview.mjs'});reserve('browser',{'engine':'cached chromium','headless':True})
            nodeenv=env.copy();nodeenv['RETROLUME_TASK106_BROWSER_OUTPUT']=str(folder);nodeenv['RETROLUME_TASK106_BROWSER_SEED']=str(seedpath)
            with (folder/'driver-log.txt').open('w',encoding='utf-8') as driver:
                node=subprocess.Popen(['node',str(ROOT/'frontend/tests/task106-interview.mjs')],cwd=ROOT/'frontend',env=nodeenv,stdout=driver,stderr=driver,creationflags=subprocess.CREATE_NO_WINDOW)
                nodeidentity=dict(pid=node.pid,birth_100ns=process_birth(node.pid),command='frontend/tests/task106-interview.mjs')
                atomic_json(folder/'owned-driver.json',nodeidentity)
                time.sleep(1)
                profile=str(folder/'chrome-profile').replace("'","''")
                query="Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'chrome.exe' -and $_.CommandLine.Contains('"+profile+"') } | Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 3"
                captured=subprocess.run(['powershell','-NoProfile','-Command',query],capture_output=True,text=True,timeout=15,creationflags=subprocess.CREATE_NO_WINDOW)
                if captured.returncode==0:
                    owned=json.loads(captured.stdout or '[]');owned=owned if isinstance(owned,list) else [owned]
                    for row in owned:row['birth_100ns']=process_birth(row['ProcessId'])
                    atomic_json(folder/'owned-chromium.json',owned)
                try:code=node.wait(timeout=240)
                except subprocess.TimeoutExpired:
                    assert nodeidentity['birth_100ns']==process_birth(node.pid);node.terminate();node.wait(timeout=10);raise RuntimeError('bounded browser driver timeout')
            if code:
                print((folder/'driver-log.txt').read_text(encoding='utf-8')[-7000:]);raise RuntimeError('real browser failed; exact DOM/network/stack saved')
            result=json.loads((folder/'browser-result.json').read_text(encoding='utf-8'));assert result['passed']
            print(json.dumps(dict(browser=True,source_build_http_identity=True,lifecycle=True,root='final-browser')))
        finally:
            if node and node.poll() is None:node.terminate();node.wait(timeout=10)
            if process and process.poll() is None:
                assert identity['birth_100ns']==process_birth(process.pid);process.terminate();process.wait(timeout=10)
            if stream:stream.close()
            if process:atomic_json(folder/'api-stop.json',dict(identity=identity,exit_code=process.returncode,stopped=process.poll() is not None))
            stop(1)


if __name__=='__main__':main()
