"""Final bundle browser, normal local API/PG and real local operator."""
import json,os,shutil,subprocess,time
from . import resources as r,setup
from .api_runtime import application,financials
from app.capabilities.q_protocol import ROSTER


def run_ui(client=None,mode='interview'):
    from contextlib import nullcontext
    number=r.state()['active_root'];batch=int(os.environ.get('RETROLUME_TASK120_BATCH','0'))
    stem=f'root-{number:02d}-batch-{batch:02d}-ui-{mode}'
    folder=r.PRIVATE/stem;folder.mkdir(exist_ok=False)
    with (application('flow') if client is None else nullcontext(client)) as client:
        progress=json.loads((r.PRIVATE/'flow/flow-progress.json').read_text(encoding='utf-8'))
        spec={'permit':'TASK-120-Q-PREP-IMPLEMENTATION-20261018','project':str(r.ROOT),'origin':client.base,
            'activities':list(ROSTER),'interview_goal':setup.SAMPLES['inputs']['interview_goal'],
            'mode':mode,'numeric_goal':setup.SAMPLES['inputs']['numeric_goal'],'numeric_question':setup.SAMPLES['inputs']['numeric_initial_question'],
            'legacy_operation':progress.get('legacy-first.done',{}).get('operation_id'),
            'profile':str(folder/'browser'),'handshake':str(folder),'proof':str(r.EVIDENCE/(stem+'-proof.json')),
            'screenshotTeaching':str(r.EVIDENCE/(stem+'-teaching.png')),'screenshotInterview':str(r.EVIDENCE/(stem+'-interview.png'))}
        r.write(folder/'spec.json',spec,private=True)
        r.settled_memory_gate('browser');r.count('browser_starts')
        env=os.environ.copy();env['RETROLUME_TASK120_UI_SPEC']=str(folder/'spec.json')
        with (r.EVIDENCE/(stem+'-node.log')).open('wb') as log:
            process=subprocess.Popen([shutil.which('node'),str(r.ROOT/'frontend/tests/task120-ui-continuation.mjs')],cwd=r.ROOT/'frontend',env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            from app.preview.process import birth
            r.event('ui_node_started',pid=process.pid,birth=birth(process.pid),root=number)
            deadline=time.monotonic()+90;ordinal=1
            try:
                while process.poll() is None:
                    if time.monotonic()>=deadline:raise RuntimeError('task120_ui_timeout')
                    request=folder/f'request-{ordinal}.json'
                    if request.exists():
                        value=json.loads(request.read_text(encoding='utf-8'))
                        if set(value)!={'ordinal','kind','activity_id','business_key'} or value['ordinal']!=ordinal or value['kind']!='approve' or value['activity_id'] not in ROSTER:raise RuntimeError('closed_ui_operator_request')
                        before=financials('flow');rows=client.approve(value['activity_id'],value['business_key'])
                        if financials('flow')!=before:raise RuntimeError('ui_approval_changed_financials')
                        # Reserve an attempt before the explicitly requested UI
                        # continuation. A fenced late attempt is conservative.
                        for row in rows:r.count('native_business_sessions')
                        r.write(folder/f'reply-{ordinal}.json',{'status':'APPROVED'},private=True);ordinal+=1
                    time.sleep(.04)
            finally:
                if process.poll() is None:process.terminate()
                process.wait(timeout=8)
        if process.returncode:raise RuntimeError('task120_browser_assertion_failed')
