"""最后一个获准PG start只用于已sealed目标只读，完成实际bundle/TCP闭包。"""
import json
import os
import subprocess
import time
from budget import ROOT,EVIDENCE,Budget
from c02_common import Evidence,reference,environment,memory_guard
from c02_pg_run import runtime,FIXTURE
from c02_http import Api,projection
from freeze import freeze
from app.preview.process import birth
from app.data_exit.contracts import canonical


def browser(budget,evidence):
    if not memory_guard()['ready']:raise RuntimeError('Browser内存门')
    budget.reserve('browser_start');profile=EVIDENCE/'synthetic/browser-root'/evidence.path.name;profile.mkdir(parents=True)
    ids=[];process=None;closed=False
    try:
        with (evidence.path/'browser-stderr.log').open('xb') as log:
            process=subprocess.Popen(['node',str(ROOT/'frontend/tests/task114-c02-selected.mjs'),str(evidence.path),str(profile),str(FIXTURE)],cwd=ROOT,
              stdout=subprocess.PIPE,stderr=log,text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
            info=birth(process.pid);identity=f"browser-controller:{process.pid}:{info['birth']}";ids.append((identity,process.pid,info['birth']))
            budget.created(identity,'browser-controller',{'pid':process.pid,'birth':info['birth'],'profile':str(profile)});budget.begin(identity)
            for line in process.stdout:
                with (evidence.path/'browser-events.jsonl').open('a',encoding='utf-8') as f:f.write(line)
                event=json.loads(line)
                if event['event']=='browser_spawn':
                    info=birth(event['pid']);identity=f"browser:{event['pid']}:{info['birth']}";ids.append((identity,event['pid'],info['birth']))
                    budget.created(identity,'browser',{'pid':event['pid'],'birth':info['birth'],'profile':str(profile),'parent_pid':process.pid});budget.begin(identity)
                elif event['event']=='browser_closed':closed=event['confirmed']
            code=process.wait(timeout=10);assert code==0 and closed
    finally:
        if process and process.poll() is None:process.terminate();process.wait(timeout=10)
        for identity,pid,stamp in reversed(ids):
            observed=birth(pid);assert observed['state']=='exited' or observed['state']=='running' and observed['birth']!=stamp
            budget.end(identity,{'pid':pid,'birth':stamp,'process_ended':True,'actual_browser_close':closed})


def main():
    budget=Budget();budget.check();source,credentials=reference();fixture=json.loads(FIXTURE.read_bytes());label='c02-final-http-'+str(time.monotonic_ns());evidence=Evidence(label,credentials);target=None;rt=None
    budget.root('c02-pg-group');freeze(label)
    try:
        rt=runtime(credentials,budget);target=rt.factory.target(rt.hub.state()['selection']['target_id']);rt.factory.start(target)
        rt.factory._wait_pg(rt.factory.readonly_credentials(target.target_id)['readonly_dsn'])
        environment(credentials)
        with Api(budget,evidence) as api:
            caps,headers=projection(api,fixture,evidence,restored=True)
            old={**{k:caps[k] for k in ('control_id','selection_generation','dataset_id','instance_id','current_mode','read_only')},
                'selection_generation':0,'dataset_id':source.dataset_id,'instance_id':source.instance_id,'current_mode':'normal','read_only':False}
            stale={**api.headers,'X-RetroLume-Data-Context':canonical(old)}
            bad=api.client.get('/api/data/saved-records?category=memories',headers=stale);assert bad.status_code==409 and bad.json()['code']=='selection_changed'
            good=api.client.get('/api/data/jobs/by-key/'+fixture['package_key'],headers=stale);assert good.status_code==200
            evidence.save('context-dependent-vs-stable-Hub',{'stale_records':bad.json(),'stale_records_status':bad.status_code,'old_key_status':good.status_code,'old_key_job_id':good.json()['job_id']})
            browser(budget,evidence)
        evidence.save('result',{'state':'passed','last_PG_start_for_readonly_only':True,'Source_start':0,'new_Normal_authority':0});return 0
    except BaseException as error:evidence.fail(error);return 1
    finally:
        if rt and target:rt.factory.stop(target)


if __name__=='__main__':raise SystemExit(main())
