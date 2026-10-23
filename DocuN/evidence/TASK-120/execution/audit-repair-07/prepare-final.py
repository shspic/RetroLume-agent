"""Filesystem-only07 review materials. No DB, API, worker or business starts."""
from pathlib import Path
from datetime import datetime,timezone
import ast,difflib,hashlib,json,os

HERE=Path(__file__).resolve().parent
EX=HERE.parent
ROOT=HERE.parents[4]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return Path(p).relative_to(ROOT).as_posix()
def write(name,data):
    p=HERE/name
    assert not p.exists(),name
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

b=read(EX/'budget.json');prior=read(HERE/'budget.json.before.bytes')
assert b['active_root'] is None
assert b['roots'][:len(prior['roots'])]==prior['roots']
assert b['failures'][:len(prior['failures'])]==prior['failures']
assert (EX/'events.jsonl').read_bytes().startswith((HERE/'events.jsonl.before.bytes').read_bytes())
assert (ROOT/'DocuN/results/TASK-120-result.md').read_bytes()==(HERE/'result.before.bytes').read_bytes()
assert len(prior['roots'])==51 and len(prior['failures'])==125
assert b['counts']['roots']==60 and b['counts']['pg_starts']==61
assert all(b['counts'][k]==0 for k in ('provider_calls','actual_fee_microunits','preview_creates','preview_starts','Git_writes'))
assert read(HERE/'final-stop-proof.json')['all_fresh_stop_dimensions_confirmed']
assert read(HERE/'command-079.receipt.json')['tree_empty']
registry=read(HERE/'change-registry.json')['paths']
allowed={str((ROOT/x['path']).resolve()).casefold() for x in registry}
mutable={str((EX/x).resolve()).casefold() for x in ('budget.json','events.jsonl')}
baseline=[]
for x in read(HERE/'baseline-identities.json')['checked']:
    p=Path(x['path']);actual=sha(p) if p.is_file() else None
    status='UNCHANGED' if actual==x['expected'] else 'REGISTERED07_CHANGE' if str(p.resolve()).casefold() in allowed else 'SOLE_LEDGER_UPDATED' if str(p.resolve()).casefold() in mutable else 'UNEXPECTED_DRIFT'
    assert status!='UNEXPECTED_DRIFT',str(p)
    baseline.append({'path':str(p),'before_sha256':x['expected'],'sha256':actual,'status':status})
rules=read(ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
for x in rules:assert sha(x['absolute_path'])==x['sha256']
rows=[];changes=[];product=[];source=[];fixtures=[]
for x in registry:
    p=ROOT/x['path'];assert p.is_file(),str(p)
    data=p.read_bytes();actual=hashlib.sha256(data).hexdigest()
    if p.suffix=='.py':ast.parse(data.decode('utf-8-sig'))
    rows.append({'path':x['path'],'sha256':actual,'bytes':len(data)})
    if actual==x['before_sha256']:continue
    pre=HERE/'preimage'/x['path']
    if x['existed']:assert pre.is_file() and sha(pre)==x['before_sha256'],x['path']
    else:assert not pre.exists(),x['path']
    changes.append({'path':x['path'],'before_sha256':x['before_sha256'],'after_sha256':actual,'reason':x['reason']})
    delta=difflib.unified_diff(pre.read_text(encoding='utf-8-sig').splitlines(True) if pre.exists() else [],
        data.decode('utf-8-sig').splitlines(True),fromfile='before/'+x['path'] if pre.exists() else '/dev/null',tofile='after/'+x['path'])
    if x['path'].startswith(('backend/app/','backend/migrations/')):
        source.extend(delta);product.append(x['path'])
    else:
        assert x['path'].startswith('backend/tests/'),x['path'];fixtures.extend(delta)
(HERE/'source.diff').write_text(''.join(source),encoding='utf-8')
(HERE/'fixture.diff').write_text(''.join(fixtures),encoding='utf-8')
write('final-file-identities.json',{'baseline_audit_references':baseline,'registered_current_files':rows,'changes':changes,
    'product_paths_changed':product,'source_diff':'source.diff','fixture_diff':'fixture.diff',
    'all_other_audit322_references_unchanged_except_sole_ledger':True,'seven_locked_rules_unchanged':True,
    'frontend_source_dist_dependencies_unmodified':True,'report_replacement_deferred_until_exact_old_suffix_append':True})
asrun=[]
for p in sorted(HERE.glob('root-*-batch-*-as-run.json')):
    mismatches=[];checked=0
    for x in read(p)['files']:
        if not x['path'].startswith(('backend/app/','backend/migrations/')):continue
        checked+=1;actual=sha(ROOT/x['path'])
        if actual!=x['sha256']:
            assert str((ROOT/x['path']).resolve()).casefold() in allowed
            mismatches.append({'path':x['path'],'as_run_sha256':x['sha256'],'final_sha256':actual})
    asrun.append({'path':p.name,'sha256':sha(p),'product_files_checked':checked,'final_differences':mismatches})
assert all(not x['final_differences'] for x in asrun if x['path'].startswith('root-60-'))
assert read(HERE/'q_roles-root054-reconstruction.json')['matches_original_as_run_identity']
write('as-run-final-mapping.json',{'roots':asrun,'final_root60_product_mismatches':0,
    'F01_earlier_missing_privilege_checks':'Root52 used first revised015, saved exactly as migration015-first-revised-failed.sql. Pre-GRANT predicates identical to final; only normal R02 CHECK transition subsequently fixed. Root54 applies final015 once.',
    'F02_prior_eight_cases':'Exact root54 q_roles source reconstructed and hash matched. Final adds control/schema/database and predefined management denial; existing graph/privilege/purpose logic byte-identical. Delta negatives and legal/snapshot cases run57; final normal schema check run60.',
    'F03_final_delta':'control.py and deletions.py root059 exact preimages saved. Only cleanup-attempt/retry/completion receipt changes after59; original Operation source unchanged. Final normal HTTP retry/denial/readbacks run60; bounded authority negatives command078.',
    'F04_F05_reuse':'Clock/projection/worker logic from55/57 unchanged. control.py later change confined to source-delete completion receipt. All final root60 product hashes match.',
    'full_earlier_fixture_bytes_not_claimed':'Original as-run hashes and raw failure receipts preserved. Available exact preimages/reconstruction attached; unretained intermediate fixture bytes are not represented as final files.'})
old_packages=read(EX/'continuation-06/old-packages-preserved.json')['seven_prior_packages']+[read(EX/'continuation-06/candidate-package-identity.json')]
assert len(old_packages)==8
for x in old_packages:assert sha(ROOT/x['path'])==x['sha256'],x['path']
write('old-packages-preserved.json',{'eight_prior_packages':old_packages,'old_zip_bytes_unchanged':True,'nested_old_ZIPs_in_new_package':0})

groups={
 'TASK-121-F01':['F01-select-only-PASS.json','F01-missing-insert-PASS.json','F01-missing-update-PASS.json','F01-normal-R03-install-PASS.json','F01-exact-codec-compatibility-PASS.json'],
 'TASK-121-F02':[p.name for p in sorted(HERE.glob('F02-*-PASS.json'))],
 'TASK-121-F03':['F03-normal-memory-revoke-purge-PASS.json','F03-source-cleanup-failure-closed-PASS.json','F03-exact-cleanup-replay-and-retry-PASS.json','F03-root58-successful-substeps-reconciled.json','command-078.receipt.json'],
 'TASK-121-F04':['F04-clock-authorization-PASS.json','F04-real-API-operator-worker-normal-combination-PASS.json','command-073.receipt.json','command-075.receipt.json'],
 'TASK-121-F05':['F05-PG-claimed-before-Q-claim-PASS.json']}
for names in groups.values():
    for name in names:
        d=read(HERE/name)
        if name.endswith('-PASS.json'):assert d['status']=='PASS',name
        if '.receipt.' in name:assert d['exit_code']==0 and d['tree_empty'],name
write('impact-matrix.json',{'engineering_checks':{k:{'status':'PASS_TARGETED_ENGINEERING','evidence':v} for k,v in groups.items()},
    'independent_audit':'PENDING_ORIGINAL_TASK121_INCREMENTAL_REVIEW','real_Q':'FROZEN',
    'no_claim_unknown_defect_count_is_zero':True,'no_full_business_replay_or_new_frontend_build':True})
write('inherited-evidence.json',{'authority':'DocuN/results/TASK-121-result.md sections4/5/6 unchanged',
    'audit_report_sha256':sha(ROOT/'DocuN/results/TASK-121-result.md'),
    'inherit_only_original_scoped_facts':['C01 ACK accepted/launch/result committed facts','C02 listed11 provenance negatives','C03 original v3/v4 wire and v1/v2 budgets','C05 original frozen TESTONLY scope','C06 exact old source and restore object','C07 old zero-resend UNKNOWN/reservation facts','C08 listed retrieval/model wiring','C09 limited original exercise/memory display','C10 limited UI cases and their as-run bundles','C11 K2 scoped late head consistency','C12 real PG common99-to100 evidence','C13 two late context UI and readonly lists','C14 historical stop instant'],
    'affected_boundaries_replaced_only_by_new_scoped_evidence':{'C02':'F04 joint clocks','C04':'F02 roles and F03 body cleanup','C06':'F01 final015 on new07 main DB only','C07':'F05 actual PG consumption projection','C14':'new exact stop proof plus filesystem command receipts'},
    'C15':'Await original TASK121 incremental audit and master disposition; no engineering self-acceptance',
    'memory_K2_limit_retained':'Root35 lacked immediate before-financial snapshot; no reconstruction of missing snapshot or broad financial-difference claim.'})
finance=read(HERE/'final-new-instances-separated-PASS.json')['facts']
assert finance['audit07-r02']['financials']['requests']==0
assert finance['audit07-main']['financials']['requests']==5 and finance['audit07-main']['financials']['cost']==1250000
retired=read(HERE/'new-only-approvals-explicitly-retired.json')
assert retired['all_existing_new_decisions_revoked'] and len(retired['prepared_ids'])==8
manifest=read(HERE/'F03-exact-new-deletion-manifest.json')
assert len(manifest['files'])==6
for x in manifest['files']:
    p=Path(x['path']).resolve();assert p.is_relative_to(ROOT/'.runtime/task120-audit07') and not os.path.lexists(p),str(p)
write('financial-summary.json',{'new_instances':finance,'new_actual_admissions':5,'launch_reservations':b['audit_repair07_synthetic_admission_launch_reservations'],
    'new_budget_cap':16,'sum_of_instances_is_not_balance_or_new_credit':True,
    'old_instances':'Historical per-instance06 readbacks retained unchanged; no old DB business query or mutation07.',
    'old_financial_evidence':['DocuN/evidence/TASK-120/execution/continuation-06/financial-summary.json','DocuN/evidence/TASK-120/execution/continuation-06/final-fresh-financials-separated.json','DocuN/evidence/TASK-120/execution/continuation-06/restore-target-final-after-readonly-UI.json'],
    'old_UNKNOWN_and_reservations':'Original entire event prefix and old roots/failures unchanged; no reissue or refund.',
    'all_eight_new_approvals_retired':True,'exact_synthetic_delete_paths_absent':6,'actual_provider_calls':0,'actual_fee_microunits':0})
write('remaining-gaps.json',{'engineering_F01_F05':'Targeted checks complete; unknown defects not certified absent.',
    'independent_acceptance':'Original TASK121 delta review and master decision pending.',
    'real_Q_readiness':'Accounts/official applicability/readiness, first activation decision and72h start remain outside this task.',
    'compatibility':['Only exact old59b2 and new874d 015 identities accepted; failed intermediate1fbe never compatibility identity.','Old applied databases not rerun, backfilled or represented as passing revised prerequisites.','No new actual PG full restore; original factory/readonly proof inherited with final initializer-chain reader check.','Legacy approvals without clock close; unsupported/unknown boot clock closes. Windows boot GUID native query is platform-specific; local3.12 GetTickCount64 verified, not an unconditional cross-platform guarantee.','Monotonic cert bounds900s with1s UTC drift sampling tolerance; a time check is not a claim to detect arbitrarily small wall adjustments.','F03 gateway refusal invokes actual ControlledModelGateway before admission, no redundant full native worker; real positive API/operator/native/SUP/PG path is separate root55 evidence.','Intermediate as-run fixture bytes not all retained; exact hashes, original receipts, available preimages and reconstruction mapping disclosed.'],
    'historical_control_failures_retained':['Prior05/06 bootstrap/control rejection facts not repaired retroactively.','07 actual human receipt unknown; conservative issue time used. Two readonly batches preceded persisted bootstrap, explicitly not claimed pre-tool.'],
    'manual_total':'UNKNOWN_NOT_ZERO','STEP018_019_020_M1_project_release':'NOT_SIGNED','further_runtime_from_unused_caps':'NOT_AUTHORIZED_AFTER_RETURN'})
write('preparation-check.json',{'utc':datetime.now(timezone.utc).isoformat(),'audit_reference_rows':len(baseline),'registered_paths':len(rows),
    'changed_product_paths':len(product),'changed_fixture_paths':len(changes)-len(product),'old_events_prefix_exact':True,
    'old_51_roots_125_failure_records_exact':True,'old_report91351bytes_unchanged':True,'old_eight_ZIPs_unchanged':True,
    'seven_rules_unchanged':True,'final60_products_match_asrun':True,'six_manifest_files_absent':True,'engineering_targeted_checks_complete':True})
print(json.dumps({'prepared':True,'products':len(product),'fixtures':len(changes)-len(product),'old_packages':8,'old_references':len(baseline)}))
