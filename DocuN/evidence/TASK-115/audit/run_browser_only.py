"""API 额度到门后只消费尚获准的第二个 Browser，全部响应夹具，不启 API。"""
import json
import os
from pathlib import Path
import subprocess
import threading
import time
from bootstrap import ROOT,AUDIT,save
from run_offline import event
from run_network import memory,reserve,birth

def main():
    memory();reserve('browser')
    output=AUDIT/'browser/late-only';output.mkdir()
    profile=AUDIT/'synthetic/browser-root/late-only';profile.mkdir()
    arguments=['C:/Program Files/nodejs/node.exe',str(AUDIT/'browser_late_only.mjs'),str(ROOT),str(output),str(profile)]
    event('root.resume',label='D1-final-bundle-controlled-responses',method='browser-only',arguments=arguments,timeout_seconds=90)
    process=None;chrome=[];messages=[];started=None;code=None
    try:
        with (AUDIT/'control/browser-only-stderr.log').open('xb') as log:
            process=subprocess.Popen(arguments,cwd=ROOT,stdout=subprocess.PIPE,stderr=log,text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
            started=time.monotonic();identity=birth(process.pid)
            event('consumer.begin',resource_kind='browser',pid=process.pid,birth=identity,arguments=arguments)
            def read():
                for line in process.stdout:
                    messages.append(line)
                    try:
                        value=json.loads(line)
                        if value.get('event')=='browser_spawn':value['birth']=birth(value['pid']);chrome.append(value)
                        event('browser.event',detail=value)
                    except ValueError:pass
            thread=threading.Thread(target=read);thread.start()
            code=process.wait(timeout=90);thread.join(3)
            save('control/browser-only-process.json',{'arguments':arguments,'exit_code':code,'stdout':messages,'chromium_roots':chrome})
    finally:
        if process is not None:
            if process.poll() is None:process.terminate()
            process.wait(timeout=10)
            observed=birth(process.pid)
            if observed['state']=='running':raise RuntimeError('准确 Browser runner 停止未知')
            seconds=time.monotonic()-started
            receipt=json.loads((AUDIT/'control/receipt.json').read_text(encoding='utf-8'))
            receipt['new_counts']['holding_seconds']+=seconds;save('control/receipt.json',receipt)
            event('consumer.end',pid=process.pid,birth=identity,observation=observed,seconds=seconds,exit_code=process.returncode)
        for item in chrome:
            observed=birth(item['pid'])
            if observed['state']=='running' and observed.get('birth')==item['birth'].get('birth'):raise RuntimeError('Chromium 根停止未知')
            event('chromium.stop.observed',pid=item['pid'],old_birth=item['birth'],observation=observed)
        event('root.end',label='D1-final-bundle-controlled-responses',exit_code=code,api_started=False)
    print(json.dumps({'exit_code':code,'artifact_root':str(output)}))
    return code or 0

if __name__=='__main__':raise SystemExit(main())
