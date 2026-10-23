"""主控有限文件与封存记录核对，不导入产品或执行测试。"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib
import json
import zipfile

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
AUDIT=ROOT/'DocuN/evidence/TASK-121/orchestration-review01-20261021'
E=ROOT/'DocuN/evidence/TASK-120/execution'
B=E/'audit-repair-07'
NOW=datetime.now(timezone(timedelta(hours=8))).isoformat()

def sha(data):return hashlib.sha256(data).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def putj(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    assert not p.exists(),p
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def item(p):
    return {'path':str(p.relative_to(ROOT)).replace('\\','/') if p.is_relative_to(ROOT) else str(p),
            'sha256':sha(p.read_bytes()) if p.is_file() else None,
            'bytes':p.stat().st_size if p.is_file() else None}

assert not (OUT/'bounded-review.json').exists()
ids=load(B/'final-file-identities.json')
rules=load(ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
for r in rules:assert sha(Path(r['absolute_path']).read_bytes())==r['sha256']
current={}
for r in ids['baseline_audit_references']:
    p=Path(r['path'])
    if r['status']=='SOLE_LEDGER_UPDATED':continue
    if p==ROOT/'DocuN/results/TASK-120-result.md':
        # 最终统一报告在文件身份清单之后置顶发布，单独核新hash及旧后缀。
        assert r['sha256']=='3d044a788f7354e9a3b1fec0f75bab100f182469dea42613d3112078cda67b03'
        continue
    actual=sha(p.read_bytes()) if p.is_file() else None
    assert actual==r['sha256'],str(p)
    current[str(p).lower()]=item(p)
for r in ids['registered_current_files']:
    p=ROOT/r['path']
    assert sha(p.read_bytes())==r['sha256'],r['path']
    current[str(p).lower()]=item(p)
for r in ids['changes']:
    assert sha((ROOT/r['path']).read_bytes())==r['after_sha256'],r['path']
assert len(ids['product_paths_changed'])==15
assert len(ids['registered_current_files'])==31 and len(ids['changes'])==30
budget=load(E/'budget.json')
assert budget['active_root'] is None and budget['active_command'] is None
assert budget['engineering_status']=='AUDIT_REPAIR07_COMPLETE_STOPPED_READY_FOR_TASK121_DELTA_REVIEW'
assert budget['counts']['roots']==60 and len(budget['failures'])==141
assert budget['counts']['pg_starts']==61 and budget['counts']['browser_starts']==14
assert budget['command_wall_cap_seconds']==72000
assert abs(budget['command_wall_conservative_upper_seconds']-64525.559426)<.001
prior=load(ROOT/'DocuN/evidence/TASK-120/orchestration-adopted07-20261021/returned-ledger/budget.json')
assert budget['roots'][:len(prior['roots'])]==prior['roots']
assert budget['failures'][:len(prior['failures'])]==prior['failures']
report=ROOT/'DocuN/results/TASK-120-result.md'
saved=load(B/'save-consistency.json')
raw=report.read_bytes()
assert sha(raw)==saved['new_report_sha256']
assert sha(raw[-91351:])=='3d044a788f7354e9a3b1fec0f75bab100f182469dea42613d3112078cda67b03'
receipts={}
for n in ('078','079','080','999'):
    r=load(B/f'command-{n}.receipt.json')
    assert r['tree_empty'] and r['exit_code']==0
    receipts[n]={k:r[k] for k in ('start_utc','end_utc','wall_seconds','exit_code','tree_empty')}
summary=load(B/'budget-summary.json')
assert abs(summary['current_wall_upper_with_final999_60second_reserve']-60+receipts['999']['wall_seconds']-budget['command_wall_conservative_upper_seconds'])<.001
stop=load(B/'final-stop-proof.json')
assert stop['all_fresh_stop_dimensions_confirmed']
assert not stop['metadata_read_problems']
assert stop['docker_realtime']['state']['Running'] is False and stop['docker_realtime']['state']['Pid']==0
assert stop['restore_target_realtime']['running'] is False and stop['restore_target_realtime']['Pid']==0
assert all(not r['listening'] for r in stop['ports'].values())
assert all(not r['same_identity_running'] for r in stop['registered_processes'])
assert all(r.get('absent') or r.get('active_processes')==0 for r in stop['registered_jobs'])
package=load(B/'candidate-package-identity.json')
zp=ROOT/package['path']
assert sha(zp.read_bytes())==package['sha256'] and zp.stat().st_size==package['bytes']
with zipfile.ZipFile(zp) as z:
    names=z.namelist()
    assert len(names)==275==package['files']
    assert not any(n.lower().endswith('.zip') for n in names)
old_packages=load(B/'old-packages-preserved.json')

raw_entries=[item(p) for p in sorted(B.rglob('*')) if p.is_file()]
authorities=[item(E/'budget.json'),item(E/'events.jsonl')]
old_audit=ROOT/'DocuN/results/TASK-121-result.md'
assert sha(old_audit.read_bytes())=='c4c30439cd6a2d7b63b12254a76550013ae8da93b50c9cf2d6836451588314d8'
audit_receipt=load(ROOT/'DocuN/evidence/TASK-121/audit/audit-session-receipt.json')
putj(AUDIT/'audit-inputs.json',{
    'frozen_at':NOW,'rules':rules,'current_frozen_files':list(current.values()),
    'registered_current_files':ids['registered_current_files'],
    'change_identity_source':item(B/'final-file-identities.json'),
    'raw_engineering_evidence':raw_entries,'unique_latest_engineering_ledger':authorities,
    'prior_audit_result':item(old_audit),'prior_audit_receipt':item(ROOT/'DocuN/evidence/TASK-121/audit/audit-session-receipt.json'),
    'opaque_engineering_result':item(report),
    'candidate_archive':item(zp),'candidate_entries':275,
    'original_adopted_contract':item(ROOT/'DocuN/evidence/TASK-120/orchestration-adopted07-20261021/contract.md'),
    'adoption_receipt':item(ROOT/'DocuN/evidence/TASK-120/orchestration-adopted07-20261021/adoption-receipt.json'),
    'adopted_engineering_permit':item(ROOT/'DocuN/evidence/TASK-120/orchestration-adopted07-20261021/permit.json')})
putj(AUDIT/'scope-index.json',{
    'scope':'Original TASK121 findings F01-F05; all actual07 changes and direct effects, not a full repeat audit',
    'product_paths_changed':ids['product_paths_changed'],'changes':ids['changes'],
    'source_diff':str((B/'source.diff').relative_to(ROOT)),
    'fixture_diff':str((B/'fixture.diff').relative_to(ROOT)),
    'preimage_directory':str((B/'preimage').relative_to(ROOT)),
    'as_run_mapping':item(B/'as-run-final-mapping.json'),
    'exact_intermediate_source_directories':[str((B/'asrun-root054').relative_to(ROOT)),str((B/'asrun-root059').relative_to(ROOT))],
    'evidence_groups':load(B/'impact-matrix.json')['engineering_checks'],
    'evidence_group_status_is_navigation_not_audit_conclusion':True,
    'additional_direct_effect_scope':['control.py journal clock witness and source_delete cleanup completion authority',
        'deletions.py private bounded CAS cleanup retry after old Operation domain changes',
        'packages.py exact legacy/current migration identities in normal reader and codec',
        'memory repository/service normal revoke-purge wiring','q_context/operator PG-consumed gating versus legal worker path'],
    'all_other_scope_inherit_prior_audit_if_unaffected':True})
putj(OUT/'bounded-review.json',{
    'checked_at':NOW,'rule_matches':len(rules),'baseline_reference_rows_checked':322,
    'current_unique_identity_count':len(current),'registered_current_files':31,'registered_changes':30,
    'changed_product_files':15,'main_runtime':0,'independent_audit_performed':False,
    'report_identity':item(report),'report_old_91351byte_suffix_hash_matches':True,
    'old_roots_and_failures_prefix_exact':True,'budget_counts':budget['counts'],'budget_caps':budget['caps'],
    'budget_failures':141,'TASK117_failure_history':81,
    'conservative_wall_seconds_latest':budget['command_wall_conservative_upper_seconds'],
    'wall_cap':72000,'holding_seconds':budget['runtime_holding_union_seconds'],'holding_cap':21600,
    'summary_wall_correction':'64583.418426 - final999 reserve60 + measured2.141 = latest64525.559426; separate post-save60 retained, older unknowns retained',
    'active_root':None,'active_command':None,'engineering_status':budget['engineering_status'],
    'stop_record_original_utc':stop['utc'],'stop_process_identity_count':len(stop['registered_processes']),
    'stop_job_count':len(stop['registered_jobs']),'selected_receipts':receipts,
    'live_Docker_process_port_probe':False,'archive':item(zp),'archive_entries':275,
    'code_and_evidence_closure':'Pending original TASK121 incremental independent review; no main pass claimed',
    'prior_audit_charged_tool_seconds':audit_receipt['conservative_charged_tool_seconds']})
print(json.dumps({'state':'FROZEN_INPUTS_AND_BOUNDED_REVIEW_SAVED','unique_current_files':len(current),
    'product_changes':15,'raw_evidence_files':len(raw_entries),'latest_wall':budget['command_wall_conservative_upper_seconds'],
    'archive_entries':275,'runtime':0},ensure_ascii=False))
