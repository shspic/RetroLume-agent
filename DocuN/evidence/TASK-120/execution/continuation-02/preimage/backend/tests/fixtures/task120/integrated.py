"""Closed finite stages share one normal API, never an interactive PG wait."""
import os,time,traceback
from . import resources as r
from .api_runtime import application
from .control_job import NamedJob
from .merged import members,await_members

def integrated(mode):
    if mode not in ('core','ui'):raise RuntimeError('closed_integrated_mode')
    number=r.state()['active_root'];slot=r.state()['roots'][-1]
    job=NamedJob.open_existing(slot['identity'],1)
    try:baseline=members(job)
    finally:job.close()
    outcomes={};receipts=[]
    with application('flow') as client:
        from .flow import run_flow
        from .ui import run_ui
        from .pg_boundaries import probe_approved,run_ack_and_gap
        client.after_approval=lambda rows:probe_approved(client,rows)
        if mode=='core':
            stages=[('interview',(),lambda:run_flow('interview_repaired',client)),
                    ('legacy_html',(),lambda:run_flow('legacy_html',client)),
                    ('ack_and_K2',('interview',),lambda:run_ack_and_gap(client))]
        else:
            import json
            from app.capabilities.q_protocol import ROSTER
            progress=json.loads((r.PRIVATE/'flow/flow-progress.json').read_text())
            # Inherit only an actual original-key COMMIT receipt, with a new
            # readonly PG/API check. Failed core exit is never rewritten to 0.
            for name,key,aid,domain in [('interview','c01-interview-question-after-catalog-fix',ROSTER[1],'interview'),('legacy_html','html',ROSTER[2],'html')]:
                if key+'.done' not in progress:outcomes[name]='MISSING_COMMIT';continue
                original=progress[key];value=client.request('GET',f'/api/activities/{aid}/{domain}/commands/{original["business_key"]}')
                good=value['status']=='committed' if domain=='interview' else value['status']=='terminal' and value['terminal_disposition']=='succeeded'
                outcomes[name]='PASS' if good else 'NOT_COMMITTED'
                receipts.append({'name':name,'inherited_actual_readonly_receipt':value,'not_a_rerun':True})
            stages=[('UI_interview',('interview',),lambda:run_ui(client,'interview')),('UI_legacy_html',('legacy_html',),lambda:run_ui(client,'legacy_html'))]
        for name,dependencies,action in stages:
            if any(outcomes.get(d)!='PASS' for d in dependencies):
                outcomes[name]='SKIPPED_DEPENDENCY';receipts.append({'name':name,'depends_on':dependencies,'status':'SKIPPED_DEPENDENCY'});continue
            if time.monotonic_ns()+30_000_000_000>=slot['business_deadline_ns']:raise RuntimeError('integrated_deadline_margin')
            start=time.monotonic();receipt={'name':name,'started_utc':r.utc()}
            try:action()
            except BaseException as exc:
                outcomes[name]='FAIL';receipt.update(status='FAIL',error_type=type(exc).__name__,safe_code=str(exc) if type(exc) is RuntimeError else None,
                    frames=[{'file':str(x.filename).replace(str(r.ROOT),'PROJECT'),'line':x.lineno,'function':x.name} for x in traceback.extract_tb(exc.__traceback__)])
                r.update(lambda state:state['failures'].append({'root':number,'internal_stage':name,'receipt':f'root-{number:02d}-integrated-{mode}-result.json'}))
            else:outcomes[name]='PASS';receipt['status']='PASS'
            finally:
                job=NamedJob.open_existing(slot['identity'],1)
                try:await_members(job,baseline)
                finally:job.close()
                receipt['wall_seconds']=time.monotonic()-start;receipts.append(receipt)
                r.write(r.EVIDENCE/f'root-{number:02d}-integrated-{mode}-result.json',{'outcomes':outcomes,'receipts':receipts,'shared_normal_API':True,'provider_calls':0,'preview_creates':0,'preview_starts':0})
    if any(x!='PASS' for x in outcomes.values()):raise RuntimeError('integrated_some_finite_stages_not_passed')
