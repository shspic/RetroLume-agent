from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[5];HERE=Path(__file__).resolve().parent;EX=HERE.parent
files=['backend/tests/fixtures/task120/'+x for x in ('setup.py','resources.py','run.py','queued.py','validation_memory.py','api_runtime.py','transport.py')]+['backend/app/activities/interview_repository.py','frontend/tests/task120-ui-continuation.mjs']
for name in files:
    target=HERE/'preimage'/name;target.parent.mkdir(parents=True,exist_ok=True)
    if not target.exists():shutil.copy2(ROOT/name,target)
def edit(name,old,new):
    p=ROOT/name;body=p.read_text(encoding='utf-8');assert body.count(old)==1,(name,old[:60],body.count(old));p.write_text(body.replace(old,new),encoding='utf-8',newline='')
edit('backend/tests/fixtures/task120/resources.py',"prospective=state().get('current_permit_id')=='TASK-120-Q-PREP-VALIDATION-04-20261019'","prospective=state().get('current_permit_id') in ('TASK-120-Q-PREP-VALIDATION-04-20261019','TASK-120-Q-PREP-FINALIZATION-05-20261019')")
edit('backend/tests/fixtures/task120/resources.py',"if state().get('current_permit_id')=='TASK-120-Q-PREP-VALIDATION-04-20261019':return memory_gate(kind)","if state().get('current_permit_id') in ('TASK-120-Q-PREP-VALIDATION-04-20261019','TASK-120-Q-PREP-FINALIZATION-05-20261019'):return memory_gate(kind)")
edit('backend/tests/fixtures/task120/validation_memory.py',"path=r.EVIDENCE/'validation-04'/f'root-{root:02d}-memory-samples.jsonl'","path=r.EVIDENCE/('finalization-05' if r.state().get('current_permit_id')=='TASK-120-Q-PREP-FINALIZATION-05-20261019' else 'validation-04')/f'root-{root:02d}-memory-samples.jsonl'")
edit('backend/tests/fixtures/task120/setup.py',"if slot not in ('flow','budget-01','budget-02'):","if slot not in ('flow','budget-01','budget-02','matrix-final'):")
edit('backend/tests/fixtures/task120/setup.py',"    if slot=='budget-02':\n        activity['memory_context']", "    if slot in ('budget-02','matrix-final'):\n        activity['memory_context']")
edit('backend/tests/fixtures/task120/setup.py',"        r.write(identity,value,private=True)\n    activity=", "        if slot=='matrix-final':\n            old=info('flow')\n            value.update(app_user=old['app_user'],app_password=old['app_password'],snapshot_user=old['snapshot_user'],snapshot_password=old['snapshot_password'])\n        r.write(identity,value,private=True)\n    activity=")
edit('backend/tests/fixtures/task120/setup.py',"            connection.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(value['database'])))", "            if slot=='matrix-final':\n                def reserve(s):\n                    if s.get('matrix_database_create_attempts',0)>=1:raise RuntimeError('matrix_create_attempt_cap')\n                    s['matrix_database_create_attempts']=1\n                r.update(reserve)\n            connection.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(value['database'])))")
edit('backend/tests/fixtures/task120/setup.py',"            if slot=='budget-02':body=body.replace('\\r\\n','\\n')", "            if slot in ('budget-02','matrix-final'):body=body.replace('\\r\\n','\\n')")
edit('backend/tests/fixtures/task120/setup.py',"            if slot in ('budget-01','budget-02'):","            if slot in ('budget-01','budget-02','matrix-final'):")
p=ROOT/'backend/tests/fixtures/task120/setup.py';body=p.read_text(encoding='utf-8')
start=body.index("        connection.execute(sql.SQL('CREATE ROLE {} LOGIN")
end=body.index("        admin=connection.execute",start)
old=body[start:end]
body=body[:start]+"        if slot!='matrix-final':\n"+''.join('    '+line+'\n' for line in old.splitlines())+"        else:\n            # 复用已经核证的同簇应用及快照角色，不新增登录或修改旧角色。\n            for role in (value['app_user'],value['snapshot_user']):\n                flags=connection.execute('SELECT rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls FROM pg_roles WHERE rolname=%s',(role,)).fetchone()\n                if flags is None or any(flags):raise RuntimeError('matrix_reused_role_drift')\n"+body[end:]
p.write_text(body,encoding='utf-8',newline='')
edit('backend/tests/fixtures/task120/setup.py',"    if slot=='budget-02':\n        expiry=", "    if slot=='matrix-final':\n        expiry=r.state()['finalization05']['finish_deadline_utc']\n        if now>=datetime.fromisoformat(expiry):raise RuntimeError('matrix_new_window_expired')\n        grant['valid_until_utc']=expiry\n    if slot=='budget-02':\n        expiry=")
edit('backend/tests/fixtures/task120/setup.py',"        if slot=='budget-02' and index==1:","        if slot in ('budget-02','matrix-final') and index==1:")
edit('backend/tests/fixtures/task120/setup.py',"r.EVIDENCE/'budget-02-creation-memory-proof.json'","r.EVIDENCE/(slot+'-creation-memory-proof.json')")
edit('backend/tests/fixtures/task120/run.py',"        elif phase.startswith('v04_'):","        elif phase.startswith('f05_'):\n            from .final05 import execute\n            execute(phase.removeprefix('f05_'))\n        elif phase.startswith('v04_'):")
edit('backend/tests/fixtures/task120/queued.py',"VALIDATION_PERMIT='TASK-120-Q-PREP-VALIDATION-04-20261019'","FINAL_PERMIT='TASK-120-Q-PREP-FINALIZATION-05-20261019'\nPHASES=PHASES|frozenset(('f05_reconcile','f05_bootstrap','f05_permissions','f05_ack','f05_head','f05_scope','f05_source','f05_memory','f05_ui','f05_delete','f05_readonly','f05_financials','f05_scope_diagnose'))\nVALIDATION_PERMIT='TASK-120-Q-PREP-VALIDATION-04-20261019'")
edit('backend/tests/fixtures/task120/queued.py',"(PERMIT,REPAIR_PERMIT,VALIDATION_PERMIT)","(PERMIT,REPAIR_PERMIT,VALIDATION_PERMIT,FINAL_PERMIT)")
edit('backend/tests/fixtures/task120/queued.py',"low,high=(21,24) if", "low,high=(25,64) if value['permit_id']==FINAL_PERMIT else (21,24) if")
edit('backend/tests/fixtures/task120/queued.py',"    if type(value['root_id']) is not int", "    if value['permit_id']==FINAL_PERMIT and any(not s.get('phase','').startswith('f05_') for s in value['stages']):raise ValueError('final05_closed_phase')\n    if type(value['root_id']) is not int")
body=(EX/'validation-04/runtime_control.py').read_text(encoding='utf-8')
body=body.replace("expiry=datetime.fromisoformat('2026-10-19T12:19:22.457756+00:00')", "expiry=datetime.fromisoformat(before['finalization05']['finish_deadline_utc'])")
body=body.replace("+before.get('validation04_unwrapped_command_wall_upper_seconds',0))", "+before.get('validation04_unwrapped_command_wall_upper_seconds',0)+before.get('finalization05_unwrapped_command_wall_upper_seconds',0))")
(HERE/'runtime_control.py').write_text(body,encoding='utf-8',newline='')
body=(EX/'validation-04/command_control.py').read_text(encoding='utf-8')
body=body.replace("deadline = datetime.fromisoformat(budget['calendar_deadline_utc'].replace('Z','+00:00'))", "deadline = min(datetime.fromisoformat(budget['calendar_deadline_utc'].replace('Z','+00:00')),datetime.fromisoformat(budget['finalization05']['finish_deadline_utc']))")
(HERE/'command_control.py').write_text(body,encoding='utf-8',newline='')
plan={'schema':'task120.finite-plan.v1','permit_id':'TASK-120-Q-PREP-FINALIZATION-05-20261019','root_id':25,'stages':[{'id':'old_scope_facts','phase':'f05_reconcile','seconds':60,'depends_on':[]}]}
(HERE/'plan-25.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
print(json.dumps({'preimages':len(files),'new_controller':'finalization-05/runtime_control.py','new_database_not_created':True}))
