"""Adopt the received prospective repair permit; filesystem only."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil, time
HERE=Path(__file__).resolve().parent; EX=HERE.parent; ROOT=HERE.parents[4]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
permit_path=ROOT/'DocuN/evidence/TASK-120/orchestration-repair03-20261019/permit.json'
permit=read(permit_path); verification=read(permit_path.with_name('input-verification.json'))
assert not (HERE/'adoption.json').exists(), 'already adopted; inspect instead'
checked=[]
for row in verification['inputs']+verification['file_checks']+verification['rules']:
    p=Path(row['path']);p=p if p.is_absolute() else ROOT/p
    assert (not p.exists()) if row['sha256'] is None else sha(p)==row['sha256'],str(p)
    checked.append({'path':str(p),'sha256':row['sha256']})
b=read(EX/'budget.json')
assert b['active_root'] is None and b['active_command'] is None and not b['needs_reconcile']
assert b['counts']==permit['old_counts_at_return'] and b['caps']==permit['old_caps'] and len(b['failures'])==57
(HERE/'prior').mkdir();(HERE/'preimage').mkdir()
for name in ('budget.json','events.jsonl','case-index.json','remaining-readiness.json'):
    shutil.copy2(EX/name,HERE/'prior'/name)
shutil.copy2(ROOT/'DocuN/results/TASK-120-result.md',HERE/'prior/TASK-120-result.md')
shutil.copy2(ROOT/'DocuN/tasks/TASK-120.md',HERE/'TASK-120-card.md')
pre=[]
for row in verification['file_checks']:
    p=Path(row['path']);p=p if p.is_absolute() else ROOT/p
    if row['sha256'] is None:continue
    rel=p.relative_to(ROOT);dst=HERE/'preimage'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
    pre.append({'path':rel.as_posix(),'sha256':sha(p)})
for name in ('command_control.py','runtime_control.py'):
    body=(EX/'continuation-02'/name).read_text(encoding='utf-8-sig').replace('continuation-02/','repair-03/')
    body=body.replace("+before.get('continuation02_unwrapped_command_wall_upper_seconds',0))","+before.get('continuation02_unwrapped_command_wall_upper_seconds',0)+before.get('repair03_unwrapped_command_wall_upper_seconds',0))")
    body=body.replace("+budget.get('continuation02_unwrapped_command_wall_upper_seconds',0))","+budget.get('continuation02_unwrapped_command_wall_upper_seconds',0)+budget.get('repair03_unwrapped_command_wall_upper_seconds',0))")
    (HERE/name).write_text(body,encoding='utf-8')
body=(EX/'continuation-02/final-stop-check.py').read_text(encoding='utf-8-sig')
body=body.replace("*HERE.glob('command-*.receipt.json')", "*(EX/'continuation-02').glob('command-*.receipt.json'),*HERE.glob('command-*.receipt.json')")
(HERE/'final-stop-check.py').write_text(body,encoding='utf-8')
(HERE/'entry-stop-check.py').write_text(body.replace("'final-stop-proof.json'","'entry-stop-proof.json'"),encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
adoption={'id':permit['id'],'received_and_adopted_utc':now,'sampled_mono_ns':time.monotonic_ns(),'permit_sha256':sha(permit_path),'previous_caps':b['caps'].copy(),'new_caps':permit['new_cumulative_caps'],'counts_retained':b['counts'].copy(),'failures_retained':len(b['failures']),'original_first_point_and_deadline_retained':True}
b.setdefault('permit_history',[]).append(adoption)
b['caps']=permit['new_cumulative_caps'];b['command_wall_cap_seconds']=permit['command_wall_cap_seconds'];b['current_permit_id']=permit['id']
b['runtime_resume_requires_new_explicit_permit']=False;b['remaining_roots']=4;b['engineering_status']='REPAIR_03_OFFLINE_PREPARATION'
b['repair03_unwrapped_command_wall_upper_seconds']=300
b['repair03_metadata_time_note']='Prospective bounded allowance for unwrapped filesystem/read/edit commands; reconcile at final save. Previous failures and both 7200 reservations retained. Manual time UNKNOWN_NOT_ZERO; interruption gaps not CPU.'
b['failures'].append({'case':'repair03-filesystem-adoption-first-attempt','error_type':'FileNotFoundError','reason':'Verifier represents intentionally absent historical dist asset with sha256=null; first script treated it as an existing file. No ledger/runtime mutation took effect. Exact absence checked on correction.'})
write(EX/'budget.json',b)
with (EX/'events.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps({'kind':'repair03_permit_adopted','utc':now,**adoption})+'\n')
write(HERE/'adoption.json',{'adoption':adoption,'verified_inputs':checked,'preimages':pre,'prior_result_sha256':sha(HERE/'prior/TASK-120-result.md')})
print(json.dumps({'adopted':permit['id'],'verified':len(checked),'preimages':len(pre),'roots':b['counts']['roots'],'failures':len(b['failures']),'runtime_started':False}))
