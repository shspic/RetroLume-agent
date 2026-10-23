"""Prospective validation04 adoption; no runtime or business action."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,shutil,time
HERE=Path(__file__).resolve().parent;EX=HERE.parent;ROOT=HERE.parents[4]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
pp=ROOT/'DocuN/evidence/TASK-120/orchestration-validation04-20261019/permit.json'
p=read(pp);v=read(pp.with_name('input-verification.json'))
assert not (HERE/'adoption.json').exists()
checked=[]
rules=read(ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
rule_rows=[{'path':x['absolute_path'],'sha256':x['sha256']} for x in rules]
for row in v['inputs']+v['file_checks']+rule_rows:
    f=Path(row['path']);f=f if f.is_absolute() else ROOT/f
    assert (not f.exists()) if row['sha256'] is None else sha(f)==row['sha256'],str(f)
    checked.append(row)
b=read(EX/'budget.json')
assert b['active_root'] is None and b['active_command'] is None and not b['needs_reconcile']
assert b['counts']==p['old_counts_at_return'] and b['caps']==p['old_caps'] and len(b['failures'])==77
(HERE/'prior').mkdir();(HERE/'preimage').mkdir()
for name in ('budget.json','events.jsonl','case-index.json','remaining-readiness.json'):
    shutil.copy2(EX/name,HERE/'prior'/name)
shutil.copy2(ROOT/'DocuN/results/TASK-120-result.md',HERE/'prior/TASK-120-result.md')
shutil.copy2(ROOT/'DocuN/tasks/TASK-120.md',HERE/'TASK-120-card.md')
pre=[]
for row in v['file_checks']:
    f=Path(row['path']);f=f if f.is_absolute() else ROOT/f
    if row['sha256'] is None:continue
    rel=f.relative_to(ROOT);dst=HERE/'preimage'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dst)
    pre.append({'path':rel.as_posix(),'sha256':sha(f)})
for name in ('command_control.py','runtime_control.py'):
    body=(EX/'repair-03'/name).read_text(encoding='utf-8-sig').replace('repair-03/','validation-04/')
    body=body.replace("+budget.get('repair03_unwrapped_command_wall_upper_seconds',0))","+budget.get('repair03_unwrapped_command_wall_upper_seconds',0)+budget.get('validation04_unwrapped_command_wall_upper_seconds',0))")
    body=body.replace("+before.get('repair03_unwrapped_command_wall_upper_seconds',0))","+before.get('repair03_unwrapped_command_wall_upper_seconds',0)+before.get('validation04_unwrapped_command_wall_upper_seconds',0))")
    if name=='runtime_control.py':body=body.replace('every=2,minimum=','every=1,minimum=')
    (HERE/name).write_text(body,encoding='utf-8')
body=(EX/'repair-03/final-stop-check.py').read_text(encoding='utf-8-sig').replace("*HERE.glob('command-*.receipt.json')","*(EX/'repair-03').glob('command-*.receipt.json'),*HERE.glob('command-*.receipt.json')")
(HERE/'final-stop-check.py').write_text(body,encoding='utf-8')
(HERE/'entry-stop-check.py').write_text(body.replace("'final-stop-proof.json'","'entry-stop-proof.json'"),encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
ad={'id':p['id'],'received_and_adopted_utc':now,'monotonic_ns':time.monotonic_ns(),'permit_sha256':sha(pp),'counts_retained':b['counts'],'failures_retained':77,'previous_caps':b['caps'],'new_caps':p['new_cumulative_caps']}
b.setdefault('permit_history',[]).append(ad);b['caps']=p['new_cumulative_caps'];b['command_wall_cap_seconds']=p['command_wall_cap_seconds'];b['current_permit_id']=p['id'];b['remaining_roots']=4
b['runtime_resume_requires_new_explicit_permit']=False;b['engineering_status']='VALIDATION_04_OFFLINE_PREPARATION'
b['validation04_unwrapped_command_wall_upper_seconds']=300
b['validation04_timing']={'entry_utc':'2026-10-19T11:01:53+00:00','note':'Current active interval only; provisional 300s reconciled at save, excluding measured commands/runtime. No interruption reset.'}
b['failures'].append({'case':'validation04-adoption-first-attempt','error_type':'KeyError','reason':'New input verifier references locked rules snapshot instead of embedding a rules array. First attempt stopped before any ledger/runtime mutation; correction verifies all seven snapshot hashes.'})
write(EX/'budget.json',b)
with (EX/'events.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps({'kind':'validation04_permit_adopted','utc':now,**ad})+'\n')
write(HERE/'adoption.json',{'adoption':ad,'verified_inputs':checked,'preimages':pre,'prior_result_sha256':sha(HERE/'prior/TASK-120-result.md')})
print(json.dumps({'adopted':p['id'],'verified':len(checked),'preimages':len(pre),'runtime_started':False}))
