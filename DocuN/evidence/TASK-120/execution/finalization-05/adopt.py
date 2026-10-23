from pathlib import Path
from datetime import datetime,timedelta,timezone
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[5]
sys.path.insert(0,str(ROOT/'backend'))
from tests.fixtures.task120 import resources as r
HERE=Path(__file__).resolve().parent
permit=json.loads((r.EVIDENCE.parent/'orchestration-final05-20261019/permit.json').read_text(encoding='utf-8'))
before=r.state()
if before.get('active_root') is not None or before.get('active_command') is not None:raise RuntimeError('unreconciled_owner')
if before.get('current_permit_id')==permit['id']:raise RuntimeError('already_adopted_read_saved_receipt')
assert before['counts']==permit['old_counts_at_return']
assert len(before['failures'])==88
rules=json.loads((r.EVIDENCE.parent.parent/'v4-migration-20260930/rules-snapshot.json').read_text(encoding='utf-8-sig'))
for row in rules:
    assert hashlib.sha256(Path(row['absolute_path']).read_bytes()).hexdigest()==row['sha256'],row['relative_path']
paths=['DocuN/results/TASK-120-result.md','DocuN/evidence/TASK-120/execution/budget.json','DocuN/evidence/TASK-120/execution/events.jsonl']
identities=json.loads((r.EVIDENCE/'validation-04/final-file-identities.json').read_text(encoding='utf-8'))
r.write(HERE/'input-identities.json',{'utc':r.utc(),'identities_document_sha256':hashlib.sha256((r.EVIDENCE/'validation-04/final-file-identities.json').read_bytes()).hexdigest(),'inputs':[{'path':p,'bytes':(ROOT/p).stat().st_size,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in paths],'rules_verified':rules})
now=datetime.now(timezone.utc)
# 首次接收工具未同步UTC，采用签发时刻作保守下界，不借换窗或恢复延长24小时。
conservative_deadline=min(datetime.fromisoformat(permit['issued_at'])+timedelta(hours=24),datetime.fromisoformat(before['calendar_deadline_utc'].replace('Z','+00:00'))-timedelta(seconds=1800))
assert now<conservative_deadline
entry={'permit_id':permit['id'],'adopted_at_utc':now.isoformat(),'receipt_exact_UTC_not_recorded_before_interruption':True,'conservative_receipt_lower_bound':permit['issued_at'],'finish_deadline_utc':conservative_deadline.isoformat(),'client':'Codex desktop','actual_precise_model_variant':'not exposed; no official variant invented','role':'A exclusive implementation; old A+ remains stopped','old_counts':before['counts'].copy(),'old_failure_count':88,'no_history_reset':True}
def adopt(value):
    value.setdefault('permit_history',[]).append(entry)
    value['current_permit_id']=permit['id'];value['caps'].update(permit['new_cumulative_caps'])
    value['command_wall_cap_seconds']=permit['command_wall_cap_seconds'];value['runtime_holding_union_cap_seconds']=permit['runtime_holding_union_cap_seconds']
    value['finalization05']=entry;value['runtime_resume_requires_new_explicit_permit']=False
    value['remaining_roots']=value['caps']['roots']-value['counts']['roots']
r.update(adopt);r.event('finalization05_adopted',**entry);r.write(HERE/'adoption.json',entry)
print(json.dumps({'adopted':permit['id'],'finish_deadline_utc':entry['finish_deadline_utc'],'old_roots':24,'old_failures':88}))
