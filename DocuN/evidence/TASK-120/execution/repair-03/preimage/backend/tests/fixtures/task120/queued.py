"""Finite, prewritten TASK120 continuation stages. No external投批 or retry."""
import hashlib,json,os,subprocess,sys,time
from pathlib import Path
from . import resources as r
from .merged import members,await_members
from .control_job import NamedJob

PHASES=frozenset(('observe','diagnose','html_eol','integrated_core','integrated_ui','teaching','interview','interview_repaired','legacy_html','gap','budget','budget_a2','budget_a3','budget_race','boundaries','ui','reopen'))
PERMIT='TASK-120-Q-PREP-CONTINUATION-01-20261019'
PHASES=PHASES|frozenset(('c02_observe','c02_bootstrap_memory','c02_core','c02_memory','c02_ui','c02_races'))

def read_plan(path):
    value=json.loads(Path(path).read_text(encoding='utf-8'))
    if set(value)!={'schema','permit_id','root_id','stages'} or value['schema']!='task120.finite-plan.v1' or value['permit_id']!=PERMIT:raise ValueError('closed_plan')
    if type(value['root_id']) is not int or not 9<=value['root_id']<=16 or not isinstance(value['stages'],list) or not 1<=len(value['stages'])<=12:raise ValueError('plan_limit')
    seen=set()
    for stage in value['stages']:
        if (set(stage)!={'id','phase','seconds','depends_on'} or stage['phase'] not in PHASES or type(stage['seconds']) is not int or not 1<=stage['seconds']<=300
            or not isinstance(stage['id'],str) or not stage['id'].isidentifier() or stage['id'] in seen or not isinstance(stage['depends_on'],list)
            or any(x not in seen for x in stage['depends_on']) or len(set(stage['depends_on']))!=len(stage['depends_on'])):raise ValueError('invalid_stage')
        seen.add(stage['id'])
    if sum(s['seconds'] for s in value['stages'])>1680:raise ValueError('plan_root_deadline')
    return value

def runnable(stage,outcomes):return all(outcomes.get(x)=='PASS' for x in stage['depends_on'])

def run_plan():
    path=Path(os.environ['RETROLUME_TASK120_PLAN']);plan=read_plan(path)
    root=r.state()['active_root'];slot=next(x for x in r.state()['roots'] if x['id']==root)
    if plan['root_id']!=root or slot['permit_id']!=PERMIT or hashlib.sha256(path.read_bytes()).hexdigest()!=slot['plan_sha256']:raise RuntimeError('plan_identity')
    job=NamedJob.open_existing(slot['identity'],1)
    try:baseline=members(job)
    finally:job.close()
    outcomes={};previous=None;receipts=[]
    for ordinal,stage in enumerate(plan['stages'],1):
        stem=f'root-{root:02d}-batch-{ordinal:02d}'
        if not runnable(stage,outcomes):
            outcomes[stage['id']]='SKIPPED_DEPENDENCY'
            r.write(r.EVIDENCE/(stem+'-receipt.json'),{'stage':stage,'state':'SKIPPED_DEPENDENCY','previous_actual_exit':previous,'depends_on':{x:outcomes.get(x) for x in stage['depends_on']}})
            continue
        remaining=slot['business_deadline_ns']/1e9-time.monotonic()-5
        if remaining<stage['seconds']:raise RuntimeError('remaining_root_cannot_fit_next_frozen_stage')
        env=r.public_environment()
        for name in ('PYTHONPATH','PYTHONIOENCODING','RETROLUME_TASK120_ROOT_ID','RETROLUME_TASK120_TESTONLY','RETROLUME_TASK120_CONTINUATION','RETROLUME_TASK120_PLAN'):env[name]=os.environ[name]
        env['RETROLUME_TASK120_BATCH']=str(ordinal)
        files=[]
        for directory in ('backend/app','backend/tests/fixtures/task120','frontend/src','frontend/dist'):
            for file in sorted((r.ROOT/directory).rglob('*')):
                if file.is_file() and '__pycache__' not in file.parts:files.append({'path':file.relative_to(r.ROOT).as_posix(),'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
        r.write(r.EVIDENCE/(stem+'-as-run.json'),{'files':files,'utc':r.utc(),'stage':stage,'previous_actual_exit':previous,'plan_sha256':slot['plan_sha256']})
        r.event('finite_stage_started',root=root,ordinal=ordinal,phase=stage['phase'],previous_actual_exit=previous)
        start=time.monotonic()
        # Timeout or unconfirmed descendants abort the owning root; no stage
        # may continue while the previous business subtree is unknown.
        result=subprocess.run([sys.executable,'-m','tests.fixtures.task120.run',stage['phase']],cwd=r.ROOT/'backend',env=env,timeout=stage['seconds'])
        job=NamedJob.open_existing(slot['identity'],1)
        try:await_members(job,baseline)
        finally:job.close()
        receipt={'stage':stage,'exit_code':result.returncode,'previous_actual_exit':previous,'wall_seconds':time.monotonic()-start,'descendants_stopped':True,'utc':r.utc()}
        previous=result.returncode;outcomes[stage['id']]='PASS' if previous==0 else 'FAIL';receipts.append(receipt)
        r.write(r.EVIDENCE/(stem+'-receipt.json'),receipt)
        if previous:r.update(lambda state:state['failures'].append({'root':root,'batch':ordinal,'phase':stage['phase'],'receipt':stem+'-receipt.json'}))
    r.write(r.EVIDENCE/f'root-{root:02d}-queue-result.json',{'outcomes':outcomes,'receipts':receipts,'automatic_finite_serial_plan':True,'external_request_wait':False})
    return 0 if all(x=='PASS' for x in outcomes.values()) else 1
