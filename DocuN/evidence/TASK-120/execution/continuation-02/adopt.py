"""Filesystem-only scope adoption; no candidate import, test or runtime."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,time
HERE=Path(__file__).resolve().parent;EX=HERE.parent;ROOT=HERE.parents[4]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
scope=ROOT/'DocuN/evidence/TASK-120/orchestration-recovery-20261019/scope-clarification.json'
verification=read(scope.with_name('input-verification.json'))
checked=[]
for row in verification['inputs']+verification['incremental_file_checks']+verification['rules']:
    p=Path(row['path']);p=p if p.is_absolute() else ROOT/p
    assert sha(p)==row['sha256'],str(p)
    checked.append({'path':str(p),'sha256':sha(p)})
b=read(EX/'budget.json');assert b['active_root'] is None and b['active_command'] is None and not b['needs_reconcile']
assert b['counts']['roots']==14 and len(b['failures'])==44
for folder in ('prior','preimage'):(HERE/folder).mkdir(exist_ok=True)
for name in ('budget.json','events.jsonl','case-index.json','remaining-readiness.json'):
    target=HERE/'prior'/name;assert not target.exists();shutil.copy2(EX/name,target)
shutil.copy2(ROOT/'DocuN/results/TASK-120-result.md',HERE/'prior/TASK-120-result.md')
shutil.copy2(ROOT/'DocuN/tasks/TASK-120.md',HERE/'TASK-120-card.md')
files=[*sorted((ROOT/'backend/tests/fixtures/task120').glob('*.py')),*sorted((ROOT/'backend/tests').glob('test_task120*.py')),*sorted((ROOT/'frontend/tests').glob('task120-*.mjs')),
 ROOT/'backend/app/capabilities/q_context.py',ROOT/'backend/app/capabilities/q_protocol.py']
pre=[]
for p in files:
    rel=p.relative_to(ROOT);dst=HERE/'preimage'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
    pre.append({'path':rel.as_posix(),'sha256':sha(p)})
for name in ('runtime_control.py','command_control.py'):
    body=(EX/'continuation-01'/name).read_text(encoding='utf-8-sig').replace('continuation-01/','continuation-02/')
    body=body.replace("+before.get('continuation_metadata_uncertainty_reserved_seconds',0))","+before.get('continuation_metadata_uncertainty_reserved_seconds',0)+before.get('continuation02_unwrapped_command_wall_upper_seconds',0))")
    body=body.replace("+budget.get('continuation_metadata_uncertainty_reserved_seconds',0))","+budget.get('continuation_metadata_uncertainty_reserved_seconds',0)+budget.get('continuation02_unwrapped_command_wall_upper_seconds',0))")
    (HERE/name).write_text(body,encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
adoption={'id':read(scope)['id'],'utc':now,'scope_sha256':sha(scope),'resource_permit_unchanged':b['current_permit_id'],'counts_unchanged':b['counts'].copy(),'caps_unchanged':b['caps'].copy(),'failures_retained':44,'old_command038_still_not_executed':True,'new_budget':False}
b.setdefault('scope_clarification_history',[]).append(adoption)
b['continuation02_unwrapped_command_wall_upper_seconds']=90
b['continuation02_metadata_time_note']='Separate 90s conservative command-wall reservation for this resumed segment filesystem/read/edit tool calls, reconciled at return; old two 7200s reservations retained. Manual thinking/editing total UNKNOWN_NOT_ZERO, not fabricated CPU; cross-interruption calendar gaps not charged.'
b['engineering_status']='CONTINUATION_02_OFFLINE_PREPARATION'
write(EX/'budget.json',b)
with (EX/'events.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps({'kind':'scope_clarification_02_adopted','utc':now,'mono_ns':time.monotonic_ns(),**adoption})+'\n')
write(HERE/'adoption.json',{'adoption':adoption,'verified_inputs':checked,'preimages':pre,'prior_result_sha256':sha(HERE/'prior/TASK-120-result.md')})
print(json.dumps({'scope_adopted':adoption['id'],'preimages':len(pre),'roots':b['counts']['roots'],'no_runtime':True}))
