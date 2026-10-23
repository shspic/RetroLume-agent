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
        repair=r.PRIVATE/'flow/r03-progress.json'
        repair_progress=json.loads(repair.read_text(encoding='utf-8')) if repair.exists() else {}
        spec={'permit':'TASK-120-Q-PREP-IMPLEMENTATION-20261018','project':str(r.ROOT),'origin':client.base,
            'activities':list(ROSTER),'interview_goal':setup.SAMPLES['inputs']['interview_goal'],
            'mode':mode,'numeric_goal':setup.SAMPLES['inputs']['numeric_goal'],'concept_goal':setup.SAMPLES['inputs']['concept_goal'],'numeric_question':setup.SAMPLES['inputs']['numeric_initial_question'],
            'scope_remove_title':next(s['filename'] for s in setup.SAMPLES['sources'] if s['alias']=='M'),
            'legacy_operation':repair_progress.get('legacy-followup.done',progress.get('legacy-first.done',{})).get('operation_id'),
            'profile':str(folder/'browser'),'handshake':str(folder),'proof':str(r.EVIDENCE/(stem+'-proof.json')),
            'screenshotTeaching':str(r.EVIDENCE/(stem+'-teaching.png')),'screenshotInterview':str(r.EVIDENCE/(stem+'-interview.png'))}
        r.write(folder/'spec.json',spec,private=True)
        if mode=='fences' and r.state().get('current_permit_id')=='TASK-120-Q-PREP-VALIDATION-04-20261019':raise RuntimeError('validation04_single_page_fences_required')
        r.settled_memory_gate('browser');r.count('browser_starts')
        env=os.environ.copy();env['RETROLUME_TASK120_UI_SPEC']=str(folder/'spec.json')
        with (r.EVIDENCE/(stem+'-node.log')).open('wb') as log:
            process=subprocess.Popen([shutil.which('node'),str(r.ROOT/'frontend/tests/task120-ui-continuation.mjs')],cwd=r.ROOT/'frontend',env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            from app.preview.process import birth
            r.event('ui_node_started',pid=process.pid,birth=birth(process.pid),root=number)
            deadline=time.monotonic()+(280 if mode=='remaining' else 240 if mode=='all' else 90);ordinal=1
            try:
                while process.poll() is None:
                    if time.monotonic()>=deadline:raise RuntimeError('task120_ui_timeout')
                    request=folder/f'request-{ordinal}.json'
                    if request.exists():
                        value=json.loads(request.read_text(encoding='utf-8'))
                        if set(value)!={'ordinal','kind','activity_id','business_key'} or value['ordinal']!=ordinal or value['activity_id'] not in ROSTER:raise RuntimeError('closed_ui_operator_request')
                        if value['kind']!='approve':
                            if mode!='remaining' or value['kind'] not in ('boundaries','head','scope','freeze','native_attempt'):raise RuntimeError('closed_ui_driver_request')
                            try:
                                if value['kind']=='native_attempt':r.count('native_business_sessions')
                                elif value['kind']=='boundaries':client.validation04_boundaries()
                                else:driver_mutation(client,value)
                            except Exception as exc:
                                import traceback
                                diagnostic={'kind':value['kind'],'error_type':type(exc).__name__,'safe_code':str(exc) if type(exc) is RuntimeError else None,'frames':[{'function':f.name,'line':f.lineno,'file':str(f.filename).replace(str(r.ROOT),'PROJECT')} for f in traceback.extract_tb(exc.__traceback__)]}
                                r.write(r.EVIDENCE/'validation-04'/('driver-'+value['kind']+'-failure.json'),diagnostic)
                                r.update(lambda b:b['failures'].append({'root':number,'case':'validation04-driver-'+value['kind'],'diagnostic':diagnostic}))
                                answer={'status':'FAILED','error_type':type(exc).__name__}
                            else:answer={'status':'COMPLETED'}
                            r.write(folder/f'reply-{ordinal}.json',answer,private=True);ordinal+=1;continue
                        before=financials('flow');rows=client.approve(value['activity_id'],value['business_key'])
                        if financials('flow')!=before:raise RuntimeError('ui_approval_changed_financials')
                        # Reserve an attempt before the explicitly requested UI
                        # continuation. A fenced late attempt is conservative.
                        if mode!='remaining':
                            for row in rows:r.count('native_business_sessions')
                        r.write(folder/f'reply-{ordinal}.json',{'status':'APPROVED'},private=True);ordinal+=1
                    time.sleep(.04)
            finally:
                if process.poll() is None:process.terminate()
                process.wait(timeout=8)
        if process.returncode:raise RuntimeError('task120_browser_assertion_failed')

def driver_mutation(c,value):
    from .api_runtime import run
    from .repair03 import Flow
    from app.capabilities.q_protocol import canonical
    aid=value['activity_id'];kind=value['kind'];f=Flow(c,'flow')
    if kind=='head':
        f.local(aid,'interview','goal',{'goal':{'target':setup.SAMPLES['inputs']['interview_goal'],'material_roles':[]}},'v04-UI-head-mutation')
    elif kind=='scope':
        sources=json.loads((r.PRIVATE/'flow/sources.json').read_text(encoding='utf-8'))
        item=sources['R'];entries=[{'source_id':str(item['id']),'version_id':str(item['version_id']),'source_revision':item['revision'],'original_sha256':item['sha256']}]
        f.local(aid,'interview','bind_scope',{'sources':entries,'material_roles':[]},'v04-UI-scope-mutation')
    elif kind=='freeze':
        from app.data_exit.q_store import authority_for
        from app.operator.q_request import inspect_request
        from app.capabilities.q_context import snapshot,check_instance
        from app.capabilities.contracts import AdmissionDenied
        from app.data_exit.contracts import DataError
        ledger=c.app.state.activities_ledger;authority=authority_for(ledger)
        row=next(x for x in authority.hub.state()['q']['requests'].values() if x['prepared']['business_key']==value['business_key'])
        if row.get('claim'):raise RuntimeError('v04_readonly_case_already_claimed')
        before=financials('flow');context=c.app.state.data_exit.context()
        with authority.policy():
            lease=run(c.app.state.data_exit.maintenance.drain_for_readonly_switch(context.generation,time.monotonic()+20))
            lease.close()
        actual=c.app.state.data_exit.context().public();state,_,_=run(snapshot(ledger,aid))
        try:check_instance(authority,ledger,state)
        except AdmissionDenied as exc:denial=str(exc)
        else:raise RuntimeError('v04_frozen_actual_PG_instance_allowed')
        try:inspection=run(inspect_request(ledger,row['prepared_id']))
        except (DataError,AdmissionDenied) as exc:inspection={'request_available':False,'denial':getattr(exc,'code',str(exc))}
        if inspection.get('request_available') or authority.request(row['prepared_id']).get('claim') or financials('flow')!=before:raise RuntimeError('v04_frozen_body_claim_financial_failure')
        r.write(r.EVIDENCE/'validation-04'/'actual-readonly-body-closed.json',{'status':'PASS','prepared_id':row['prepared_id'],'business_key':value['business_key'],'before_context':context.public(),'after_context':actual,'actual_PG_mode':state['control']['state']['mode'],'Q_denial':denial,'request_body_closed':True,'claim_not_created':True,'financials_unchanged':True,'never_unfreeze':True})
