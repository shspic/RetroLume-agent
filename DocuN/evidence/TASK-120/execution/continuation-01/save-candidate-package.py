"""Filesystem-only report/evidence packaging. Does not import or test the candidate."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import copy,difflib,hashlib,json,time,zipfile
HERE=Path(__file__).resolve().parent;EX=HERE.parent;ROOT=HERE.parents[4]
started=time.monotonic()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def write(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
now=datetime.now(timezone.utc);budget=read(EX/'budget.json');prior=read(HERE/'prior/budget.json')
assert budget['active_root'] is None and budget['active_command'] is None and budget['counts']['roots']==14
assert budget['roots'][:len(prior['roots'])]==prior['roots']
assert budget['failures'][:len(prior['failures'])]==prior['failures']
assert (EX/'events.jsonl').read_bytes().startswith((HERE/'prior/events.jsonl').read_bytes())
assert not (HERE/'command-038.receipt.json').exists()
for entry in [
 {'case':'continuation-01-filesystem-package-first-attempt','classification':'metadata_packaging_failure_not_product_or_runtime','receipt':'continuation-01/packaging-attempt-01.json'},
 {'case':'continuation-01-platform-review-capacity','classification':'platform_action_not_executed','receipt':'continuation-01/automatic-review-block.json'},
 {'case':'continuation-01-final-readonly-Docker-inspect','classification':'metadata_permission_denied_not_runtime','receipt':'continuation-01/final-stop-proof.json'},
 {'case':'continuation-01-unwrapped-metadata-lookup-diagnostics','classification':'five_lookup_failures_not_independent_product_defects','items':[
   {'tool_chunk':'0df17c','error':'four frontend component paths absent; later found via rg --files'},
   {'tool_chunk':'bd441d','error':'guessed test filename absent; later found via rg --files'},
   {'tool_chunk':'d1445e','error':'Windows literal migration wildcard path; later used rg glob'},
   {'tool_chunk':'884975','error':'guessed frontend dataContext path absent; resolved to data/context.tsx'},
   {'tool_chunk':'3ecdb7','error':'whole legacy_html result file absent because HTML failed; use actual HTTP timeline and PG observation'}]}]:
    if not any(x.get('case')==entry['case'] for x in budget['failures']):budget['failures'].append(entry)
budget.update(continuation_metadata_uncertainty_reserved_seconds=7200,
 continuation_manual_read_edit_time='UNKNOWN_NOT_ZERO; conservative additional metadata uncertainty reservation 7200s, not measured CPU/calendar gap',
 engineering_status='CONTINUATION_01_PARTIAL_STOPPED_PLATFORM_REVIEW_CAPACITY',real_Q='FROZEN',
 final_stop_proof='continuation-01/final-stop-proof.json',final_case_index='case-index.json',
 runtime_resume_requires_new_explicit_permit=False,
 resume_requires_fresh_Docker_identity_status_and_functional_approval_service=True,
 unexecuted_plan='continuation-01/plan-root-15.json',unexecuted_command='continuation-01/command-038.json')
budget['command_wall_conservative_upper_seconds']=sum(budget.get(k,0) for k in ('pre_controller_wall_upper_seconds','controlled_command_wall_seconds','runtime_command_wall_seconds','unwrapped_metadata_wall_reserved_seconds','continuation_metadata_uncertainty_reserved_seconds'))
assert budget['command_wall_conservative_upper_seconds']<budget['command_wall_cap_seconds']
write(EX/'budget.json',budget)
events=(EX/'events.jsonl').read_text(encoding='utf-8')
if 'continuation01_package_stop_platform_capacity' not in events:
    with (EX/'events.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps({'utc':now.isoformat(),'mono_ns':time.monotonic_ns(),'kind':'continuation01_package_stop_platform_capacity','root15_started':False,'command038_executed':False,'real_Q':'FROZEN','precise_metadata_time':'UNKNOWN_NOT_ZERO','additional_metadata_reserve_seconds':7200})+'\n')

assessment={
 'C01':('PASS_ISOLATED','B','K1/approval finite checks inherited and targeted regression passed; full PG ACK matrix remains pending',['command-025.log','continuation-01/command-036.log']),
 'C02':('PARTIAL_PG_AND_ISOLATED','A/B','Listed real embedding/legacy chains; unapproved whole-request PG negative matrix not run',['root-11-batch-03-http-timeline.json','root-11-batch-04-http-timeline.json','continuation-01/command-036.log']),
 'C03':('PASS_FOR_LISTED_COMPATIBILITY_CHECKS','B','Old wire3/v1 limits and v4 private reference roundtrip retained; no blanket wire4 regression claim',['command-025.log','continuation-01/command-036.log']),
 'C04':('PARTIAL','B','Existing isolated artifact/hub/frozen checks inherited; new actual-PG copies/tail/delete/readonly matrix saved not run',['command-025.log','continuation-01/command-036.log']),
 'C05':('PASS_FOR_INERT_NORMAL_EXAMPLES','B','Original normal loader/configuration checks reused; real enabling facts UNKNOWN',['command-028.log','command-028.receipt.json']),
 'C06':('PASS_ORIGINAL_TESTONLY_IDENTITIES','A','Original two databases/CID/volume/roster reused; no budget02 or replacement resource',['continuation-01/resume-stop-proof.json','root-14-instance-observation.json']),
 'C07':('PARTIAL','A','Original teaching pending/GET/approval preserved; original UNKNOWN never resent',['root-06-batch-01-http-timeline.json','root-11-batch-02-http-timeline.json']),
 'C08':('PASS_FOR_LISTED_EMBEDDING_CHAINS','A','Inherited N index/two query plus R/M two index batches and one query; not a model-domain pass',['flow-committed-receipts.json','root-11-batch-03-http-timeline.json']),
 'C09':('BLOCKED_BY_COMMITTED_NOOP_GOAL_SLOT','A','Actual revision1 no-op goal occupies goal slot; no semantic/no-op rule changed; A3 supplemental question unanswered',['root-12-readonly-diagnosis.json','root-11-batch-02-failure.json']),
 'C10':('PARTIAL_LEGACY_PASS_INTERVIEW_HTML_PENDING','A/B','Legacy first committed_current; Interview claim UNKNOWN retained; typed-context/catalog repairs checked offline only; HTML exact EOL patch passed, description not run',['root-11-batch-04-http-timeline.json','root-12-batch-03-http-timeline.json','continuation-01/retained-interview-q-witness.json','continuation-01/command-036.log','root-14-html-eol-applied.json']),
 'C11':('PARTIAL_REMAINING_MODEL_K2_NOT_RUN','A/B','Inherited real embedding commits and isolated lock checks; new model ACK/release-gap/source-memory-scope races unrun',['flow-committed-receipts.json','command-025.log','continuation-01/automatic-review-block.json']),
 'C12':('PASS_ACTUAL_COMMON_PG_100_AND_REOPEN','A','Actual 47/28/24 baseline99, two backends3923/3925 last slot, 100/25000000, post100 both deny, stopped/reopened original DB remains exhausted',['budget-99-baseline.json','budget-last-slot-race.json','root-12-budget-reopen.json','root-14-budget-reopen.json']),
 'C13':('FORMAL_DIST_INHERITED_BROWSER_NOT_RUN','B/C','Four build byte identities unchanged; browser0; new UI fixture saved unverified',['final-bundle-identities.json','continuation-01/automatic-review-block.json']),
 'C14':('PARTIAL_FINAL_DOCKER_REALTIME_UNKNOWN','A','Root9 late stop reconciled; Root10-14 stopped at recorded times; new106 PID/53 Job/ports checks pass, Docker live inspect denied',['continuation-01/root-09-stop-reconciliation.json','root-14-stop.json','continuation-01/final-stop-proof.json']),
 'C15':('IDENTITY_AND_SAVED_CANDIDATE_NOT_ACCEPTANCE','B','Baseline642/preimages/history prefixes and final hashes/diffs retained; blocked preflight/new fixtures not asserted passed',['continuation-01/receipt-baseline.json','continuation-01/final-file-identities.json','continuation-01/final-rules-check.json'])}
case=read(HERE/'prior/case-index.json');old_cases=copy.deepcopy(case['cases'])
case.update(status=budget['engineering_status'],stable_audit_package_ready=False,real_Q='FROZEN',prior_case_index_sha256=sha(HERE/'prior/case-index.json'),case_history_at_return=old_cases)
case['cases']=[{'id':key,'status':value[0],'grade':value[1],'facts':value[2],'evidence':value[3]} for key,value in assessment.items()]
case['continuation_01']={'permit_id':budget['current_permit_id'],'counts':budget['counts'],'failures_entries':len(budget['failures']),'old_root_and_command_receipts_unchanged':True,'plans_are_not_runs':True}
write(EX/'case-index.json',case)
ready=read(HERE/'prior/remaining-readiness.json')
ready.update(engineering_stable=False,activated=False,real_Q='FROZEN',engineering_completed_increment=['Actual original budget01 100/25000000 last-slot race and both-provider denial, stop/reopen','One original legacy-learning first chain','User-approved exact nine HTML function EOL correction and ordinary-role fingerprint check'],
 engineering_required=['Resolve original A1 committed no-op goal-slot contract without changing semantic/no-op rules; A3 question unanswered','Resolve selected-memory positive at creation without rebinding old activities; conditional budget02 question unanswered','Run corrected Interview/Teaching query-to-model-to-007-domain chains, HTML description, ACK and actual K2 remainder','Complete unapproved whole-request/foreign-parent/source-memory-copy-artifact-journal-readonly PG matrix','Run final-dist five-entry UI and all applicable late identity fences; Browser is 0','Final syntax/JS fixture preflight command038 was not executed; candidate fixtures remain unverified'],
 resource_block={'roots_used':14,'roots_cap':16,'pg_starts':13,'api_starts':9,'browser_starts':0,'frontend_builds':4,'native_sessions':9,'http':54,'platform':'automatic review selected model at capacity; action not executed','fresh_Docker_inspection':'permission denied; last actual stopped Root14 2026-10-19T01:47:08.980403Z','no_budget_reset':True},
 user_keys_or_memory_release_requested=False,independent_audit_started=False,current_case_index='DocuN/evidence/TASK-120/execution/case-index.json')
write(EX/'remaining-readiness.json',ready)

baseline=read(HERE/'receipt-baseline.json');identities={}
for value in baseline.values():
    if isinstance(value,list):
        for row in value:
            if isinstance(row,dict) and 'path' in row and 'sha256' in row:identities[row['path']]=row['sha256']
assert len(identities)==642
changed=[];current=[];missing=[];expected_absent=[];unexpected_present=[]
for relative,old in sorted(identities.items()):
    path=ROOT/relative
    if old is None:
        if path.exists():unexpected_present.append(relative)
        else:expected_absent.append(relative)
        current.append({'path':relative,'sha256':sha(path) if path.is_file() else None,'expected_absent':True,'exists':path.exists()})
        continue
    if not path.is_file():missing.append(relative);continue
    actual=sha(path);current.append({'path':relative,'sha256':actual})
    if actual!=old:changed.append({'path':relative,'before_sha256':old,'after_sha256':actual})
new_files=[]
allowed=[ROOT/'backend/tests/test_task120_continuation.py',ROOT/'backend/tests/test_task120_outbound_api.py',*sorted((ROOT/'backend/tests/fixtures/task120').glob('*.py')),*sorted((ROOT/'frontend/tests').glob('task120-*.mjs'))]
for path in allowed:
    relative=path.relative_to(ROOT).as_posix()
    if relative not in identities:new_files.append({'path':relative,'sha256':sha(path)})
write(HERE/'final-file-identities.json',{'utc':now.isoformat(),'baseline_unique_paths':642,'baseline_existing_files':len(identities)-len(expected_absent),'current_files':current,'changed':changed,'missing':missing,'expected_absent':expected_absent,'unexpected_present':unexpected_present,'new_files':new_files,'execution_not_implied':True})
assert not missing and not unexpected_present
product_diff=[];fixture_diff=[]
for row in [*changed,*new_files]:
    relative=row['path'];path=ROOT/relative;pre=HERE/'preimage'/relative
    if relative in identities:
        if not pre.is_file():raise RuntimeError('missing_preimage_'+relative)
        assert sha(pre)==identities[relative]
    before=pre.read_text(encoding='utf-8-sig').splitlines(keepends=True) if pre.is_file() else []
    after=path.read_text(encoding='utf-8-sig').splitlines(keepends=True)
    target=product_diff if relative.startswith('backend/app/') else fixture_diff
    target.extend(difflib.unified_diff(before,after,fromfile='before/'+relative if pre.is_file() else '/dev/null',tofile='after/'+relative))
(HERE/'source.diff').write_text(''.join(product_diff),encoding='utf-8',newline='\n')
(HERE/'fixture.diff').write_text(''.join(fixture_diff),encoding='utf-8',newline='\n')
rules=[]
for row in read(ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json'):
    path=Path(row['absolute_path']);actual=sha(path)
    rules.append({'path':row['absolute_path'],'expected':row['sha256'],'actual':actual,'matches':actual==row['sha256']})
write(HERE/'final-rules-check.json',{'locked_version':'V4.0/CHG-0003','all_match':all(x['matches'] for x in rules),'rules':rules})
bundle=read(EX/'final-bundle-identities.json')
for row in bundle['assets']:assert sha(ROOT/row['path'])==row['sha256']
old_zip=read(EX/'final-review-files-identity.json');assert sha(EX/old_zip['path'])==old_zip['sha256']
original=(HERE/'prior/TASK-120-result.md').read_bytes()
assert hashlib.sha256(original).hexdigest()==baseline['result_sha256']
prefix=(HERE/'result-prefix.md').read_text(encoding='utf-8').replace('@@SAVED@@',now.astimezone(timezone(timedelta(hours=8))).isoformat()).replace('@@FAILURES@@',str(len(budget['failures'])))
report=ROOT/'DocuN/results/TASK-120-result.md'
report.write_bytes(prefix.encode('utf-8')+original)
assert report.read_bytes().endswith(original)
write(HERE/'result-preservation.json',{'old_body_sha256':hashlib.sha256(original).hexdigest(),'old_body_bytes':len(original),'unchanged_original_is_final_suffix':True,'new_report_sha256':sha(report)})
index={'task':'TASK-120','permit_id':budget['current_permit_id'],'status':budget['engineering_status'],'engineering_complete':False,'stable_for_independent_audit':False,'real_Q':'FROZEN',
 'report':str(report),'case_index':str(EX/'case-index.json'),'readiness':str(EX/'remaining-readiness.json'),
 'entry':'read original task card continuation01, current result prefix, automatic review block, final stop proof, sole budget; do not run old roots/batches',
 'verified_budget_evidence':['budget-99-baseline.json','budget-last-slot-race.json','root-12-budget-reopen.json','root-14-budget-reopen.json'],
 'verified_HTML_patch_evidence':['continuation-01/proposed-html-eol-repair.sql','continuation-01/html-eol-user-permission.json','root-14-html-eol-applied.json'],
 'source_diff':'continuation-01/source.diff','fixture_diff':'continuation-01/fixture.diff','file_identities':'continuation-01/final-file-identities.json','rules':'continuation-01/final-rules-check.json',
 'actual_as_run_roots':list(range(9,15)),'unexecuted':['continuation-01/command-038.json','continuation-01/plan-root-15.json','new integrated/PG-boundary/UI fixtures'],
 'continuation_controls_unexecuted_last_delta':'Both new controllers include the added metadata uncertainty reservation; do not treat prior control tests as validating this final delta',
 'original_report_and_logs_preserved':True,'old_ZIP_identity':old_zip,'new_package':'continuation-01/final-review-candidate.zip','excludes_private_runtime':True,
 'remaining_roots':2,'future_grant_validity_must_be_observed_not_extended':True,'latest_stop_is_partial_Docker_live_unknown':True}
write(HERE/'final-review-index.json',index)
pack=set()
for row in [*changed,*new_files]:pack.add(ROOT/row['path'])
pack.update((report,EX/'budget.json',EX/'events.jsonl',EX/'case-index.json',EX/'remaining-readiness.json'))
for path in HERE.rglob('*'):
    if path.is_file() and '__pycache__' not in path.parts and path.suffix not in ('.zip','.pyc') and path.name!='candidate-package-identity.json':pack.add(path)
# Explicit new runtime roots only; preserve/refer old raw archive separately.
for number in range(9,15):pack.update(path for path in EX.glob(f'root-{number:02d}*') if path.is_file())
for name in ('budget-99-baseline.json','budget-last-slot-race.json','final-bundle-identities.json'):pack.add(EX/name)
target=HERE/'final-review-candidate.zip'
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as archive:
    for path in sorted(pack):
        if time.monotonic()-started>55:raise RuntimeError('bounded_packaging_deadline')
        relative=path.relative_to(ROOT).as_posix()
        if relative.startswith('.runtime/') or '.git/' in relative:raise RuntimeError('private_path_in_review_package')
        archive.write(path,relative)
with zipfile.ZipFile(target) as archive:assert archive.testzip() is None
receipt={'path':target.relative_to(ROOT).as_posix(),'sha256':sha(target),'bytes':target.stat().st_size,'files':len(pack),'includes_private_configuration':False,'includes_usable_Q_authority':False,'candidate_only_not_verified_fixture_execution':True,'old_ZIP_unchanged':True}
write(HERE/'candidate-package-identity.json',receipt)
write(HERE/'save-consistency.json',{'utc':datetime.now(timezone.utc).isoformat(),'report_saved':True,'original_report_suffix_unchanged':True,'old_root_failure_event_prefixes_retained':True,'old_ZIP_unchanged':True,'dist_all_four_unchanged':True,'all_seven_pinned_rules_match':all(x['matches'] for x in rules),'candidate_archive_CRC_ok':True,'blocked_command038_not_executed':True,'new_root15_not_started':True,'wall_seconds_filesystem_packaging':time.monotonic()-started,'source_files_changed':len(changed),'new_source_fixture_files':len(new_files),'failures_entries':len(budget['failures'])})
print(json.dumps({'report':str(report),'package':receipt,'old_original_suffix_preserved':True,'metadata_reservation':budget['continuation_metadata_uncertainty_reserved_seconds'],'wall_upper':budget['command_wall_conservative_upper_seconds'],'roots':budget['counts']['roots'],'failures_entries':len(budget['failures'])}))
