"""Owned serial roots; hard child deadlines and exact finally cleanup."""
import json,os,subprocess,sys,time
from pathlib import Path
from .control import ROOT,EVIDENCE,PERMIT,batch,atomic_json,reserve
from .resources import start,stop,runtime,inspect,public
from .http import birth,Server,environment

def cleanup_children(out):
    for path in out.glob('owned-api-*.json'):
        x=json.loads(path.read_text(encoding='utf-8'))
        try:same=birth(x['pid'])==x['birth_100ns']
        except RuntimeError:same=False
        if same:
            query="Get-CimInstance Win32_Process -Filter 'ProcessId="+str(x['pid'])+"' | Where-Object { $_.CommandLine.Contains('tests.fixtures.task106.c01.server') } | Select-Object -ExpandProperty ProcessId"
            p=subprocess.run(['powershell','-NoProfile','-Command',query],capture_output=True,text=True,timeout=10,creationflags=subprocess.CREATE_NO_WINDOW)
            if p.stdout.strip()==str(x['pid']):
                subprocess.run(['powershell','-NoProfile','-Command','Stop-Process -Id '+str(x['pid'])+' -Force'],timeout=10,creationflags=subprocess.CREATE_NO_WINDOW)

def child(module,admin,app,out):
    env=environment(app,out);env.update(C01_OUT=str(out),C01_ADMIN_DSN=admin,C01_APP_DSN=app)
    with (out/'driver.log').open('w',encoding='utf-8') as stream:
        p=subprocess.Popen([sys.executable,'-m','tests.fixtures.task106.c01.'+module],cwd=ROOT/'backend',env=env,stdout=stream,stderr=stream,creationflags=subprocess.CREATE_NO_WINDOW)
        identity=dict(pid=p.pid,birth_100ns=birth(p.pid),command='tests.fixtures.task106.c01.'+module);atomic_json(out/'owned-root-child.json',identity)
        try:
            code=p.wait(timeout=530)
            if code:print((out/'driver.log').read_text(encoding='utf-8')[-6500:]);raise RuntimeError('C01 real '+module+' failed; original log/effects retained')
        except subprocess.TimeoutExpired:
            assert identity['birth_100ns']==birth(p.pid);p.terminate();p.wait(timeout=10);raise RuntimeError('C01 root hard deadline')
        finally:
            if p.poll() is None:
                assert identity['birth_100ns']==birth(p.pid);p.terminate();p.wait(timeout=10)
            cleanup_children(out);atomic_json(out/'root-child-stop.json',dict(identity=identity,exit_code=p.returncode,stopped=p.poll() is not None))

def browser(app,out,seed_path):
    with Server(app,out) as server:
        reserve('driver',dict(script='task106-continuation01.mjs'));reserve('browser',dict(engine='cached chromium'))
        env=server.env.copy();env.update(C01_BROWSER_OUTPUT=str(out),C01_BROWSER_SEED=str(seed_path))
        with (out/'browser-driver.log').open('w',encoding='utf-8') as stream:
            p=subprocess.Popen(['node',str(ROOT/'frontend/tests/task106-continuation01.mjs')],cwd=ROOT/'frontend',env=env,stdout=stream,stderr=stream,creationflags=subprocess.CREATE_NO_WINDOW)
            identity=dict(pid=p.pid,birth_100ns=birth(p.pid),command='frontend/tests/task106-continuation01.mjs');atomic_json(out/'owned-browser-driver.json',identity)
            try:
                code=p.wait(timeout=480)
                if code:print((out/'browser-driver.log').read_text(encoding='utf-8')[-6000:]);raise RuntimeError('C01 actual browser failed; DOM/network saved')
            finally:
                if p.poll() is None:
                    assert identity['birth_100ns']==birth(p.pid);p.terminate();p.wait(timeout=10)
        assert json.loads((out/'browser-result.json').read_text(encoding='utf-8'))['passed']

def main():
    app1=None
    with batch('P01-core-remaining-PG-HTTP-native') as out:
        try:admin=start(1);app1=runtime(admin,1);child('core',admin,app1,out)
        finally:stop(1)
    with batch('P02-M6-unreliable-ordinary-refusal') as out:
        try:admin=start(3);app3=runtime(admin,3);child('fault',admin,app3,out)
        finally:stop(3)
    with batch('P03-final-browser-history-reconcile-response') as out:
        try:
            start(1);browser(app1,out,EVIDENCE/'runs/P01-core-remaining-PG-HTTP-native/browser-seed.json')
        finally:stop(1)
    print('C01 core, fault and browser groups completed; owned PG stopped')

if __name__=='__main__':main()
