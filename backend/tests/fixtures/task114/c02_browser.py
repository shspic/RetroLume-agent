"""仅最终bundle路由浏览器；无API，真实Chrome/PID与准确close落同总账。"""
import json
import os
import subprocess
import sys
import time
from budget import Budget,ROOT,EVIDENCE
from setup_source import memory_guard
from freeze import freeze
sys.path.insert(0,str(ROOT/'backend'))
from app.preview.process import birth


def main():
    budget=Budget();budget.check()
    if not memory_guard()['ready']:print(json.dumps({'state':'not_run','reason':'memory_gate'}));return 78
    label='c02-browser-'+str(time.monotonic_ns());out=EVIDENCE/'batches'/label;out.mkdir(parents=True)
    profile=EVIDENCE/'synthetic/browser-root'/label;profile.mkdir(parents=True)
    budget.root('c02-browser-group');freeze(label);budget.reserve('browser_start')
    process=None;identities=[];closed=False
    try:
        process=subprocess.Popen(['node',str(ROOT/'frontend/tests/task114-c02-context.mjs'),str(ROOT),str(out),str(profile)],cwd=ROOT,
          stdout=subprocess.PIPE,stderr=(out/'stderr.log').open('xb'),text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
        born=birth(process.pid);identity=f"browser-controller:{process.pid}:{born['birth']}";identities.append((identity,process.pid,born['birth']))
        budget.created(identity,'browser-controller',{'pid':process.pid,'birth':born['birth'],'profile':str(profile)});budget.begin(identity)
        for line in process.stdout:
            with (out/'events.jsonl').open('a',encoding='utf-8') as f:f.write(line)
            event=json.loads(line)
            if event['event']=='browser_spawn':
                actual=birth(event['pid']);identity=f"browser:{event['pid']}:{actual['birth']}";identities.append((identity,event['pid'],actual['birth']))
                budget.created(identity,'browser',{'pid':event['pid'],'birth':actual['birth'],'profile':str(profile),'parent_pid':process.pid});budget.begin(identity)
            elif event['event']=='browser_closed':closed=bool(event['confirmed'])
        code=process.wait(timeout=10)
        print(json.dumps({'exit_code':code,'browser_close_confirmed':closed,'evidence':str(out)}),flush=True)
        return code
    finally:
        if process and process.poll() is None:process.terminate();process.wait(timeout=10)
        for identity,pid,stamp in reversed(identities):
            observed=birth(pid)
            ended=observed['state']=='exited' or observed['state']=='running' and observed.get('birth')!=stamp
            if not ended:raise RuntimeError('准确Browser对象仍运行，不能签停止')
            budget.end(identity,{'pid':pid,'birth':stamp,'process_ended':True,'browser_close_confirmed':closed})


if __name__=='__main__':raise SystemExit(main())
