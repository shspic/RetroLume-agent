"""Filesystem-only result, ledger and review package; no business execution."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import copy,difflib,hashlib,json,struct,time,zipfile
HERE=Path(__file__).resolve().parent;EX=HERE.parent;ROOT=HERE.parents[4];started=time.monotonic()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc);b=read(EX/'budget.json');prior=read(HERE/'prior/budget.json')
assert b['active_root'] is None and b['active_command'] is None and not b['needs_reconcile']
assert b['counts']['roots']==16 and b['caps']['roots']==16
assert b['roots'][:len(prior['roots'])]==prior['roots'] and b['failures'][:len(prior['failures'])]==prior['failures']
assert (EX/'events.jsonl').read_bytes().startswith((HERE/'prior/events.jsonl').read_bytes())
assert not (EX/'continuation-01/command-038.receipt.json').exists()
entry={'case':'continuation-02-metadata-edit-and-lookup-diagnostics','classification':'metadata_only_not_independent_product_defects','items':[
 {'action':'apply_patch anchor mismatch','effect':'no files changed by rejected patch; exact replacements then applied by filesystem script'},
 {'action':'readonly guessed activities/config.py, materials/store.py and capabilities/authorization.py paths','effect':'absent; actual modules found by rg'},
 {'action':'Windows literal test*teaching* path search','effect':'invalid wildcard argument; replaced by rg glob; no test run'}]}
if not any(x.get('case')==entry['case'] for x in b['failures']):b['failures'].append(entry)
b.update(continuation02_unwrapped_command_wall_upper_seconds=120,
 continuation02_metadata_time_note='Initial 90s raised forward to 120s conservative aggregate allowance for current filesystem/read/edit commands and final packaging; not another 7200s reservation. Manual total UNKNOWN_NOT_ZERO. Review wait and interruption gaps are not measured CPU.',
 engineering_status='CONTINUATION_02_PARTIAL_STOPPED_ROOT_CAP_16',real_Q='FROZEN',
 final_stop_proof='continuation-02/final-stop-proof.json',current_review_index='continuation-02/final-review-index.json',
 runtime_resume_requires_new_explicit_permit=True,remaining_roots=0,
 scope02_questions_resolved=['flow A3 authorized','budget02 creation-time memory authorized'],
 database02_status='Created and migrated, root bound, roster only partially created before UTF8 fixture failure; memory save/A2 selection not executed; retain partial state, do not recreate')
b['command_wall_conservative_upper_seconds']=sum(b.get(k,0) for k in ('pre_controller_wall_upper_seconds','controlled_command_wall_seconds','runtime_command_wall_seconds','unwrapped_metadata_wall_reserved_seconds','continuation_metadata_uncertainty_reserved_seconds','continuation02_unwrapped_command_wall_upper_seconds'))
assert b['command_wall_conservative_upper_seconds']<b['command_wall_cap_seconds']
write(EX/'budget.json',b)
with (EX/'events.jsonl').open('a',encoding='utf-8') as stream:
    stream.write(json.dumps({'kind':'scope02_final_return_root_cap','utc':now.isoformat(),'mono_ns':time.monotonic_ns(),'roots_used':16,'roots_cap':16,'resource_create_delta':0,'real_Q':'FROZEN','manual_total':'UNKNOWN_NOT_ZERO','new_metadata_command_upper_seconds':120})+'\n')

# Decode committed frames for a narrow immutable UNKNOWN witness, never use
# journal state as a financial authority and never export private request bodies.
unknown_keys={'1f5c659f-4a5a-4fee-bfbe-3f245eb5bc7e','430a4e36-08e1-411f-a73e-097506a6278b','3b561488-07b7-4d6d-8b98-05e793c96749'}
qrows={};journal=ROOT/'.runtime/TASK-120/flow/control/journal.bin';previous='0'*64;seq=0
canonical=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
with journal.open('rb') as stream:
    while header:=stream.read(4):
        assert len(header)==4;size=struct.unpack('!I',header)[0];raw=stream.read(size);tail=stream.read(73)
        assert tail==b'\nCOMMIT:'+hashlib.sha256(raw).hexdigest().encode()+b'\n'
        event=json.loads(raw);seq+=1;assert event['seq']==seq and event['prev_hash']==previous
        assert event['body_hash']==hashlib.sha256(canonical(event['payload']).encode()).hexdigest();previous=hashlib.sha256(raw).hexdigest()
        payload=event['payload'];kind=event['kind']
        if kind=='q.prepared':
            prepared=payload['prepared']
            if prepared['business_key'] in unknown_keys:
                qrows[payload['prepared_id']]={'business_key':prepared['business_key'],'prepared_id':payload['prepared_id'],'domain':prepared['domain'],'operation_id':prepared['operation_id'],'events':[]}
        if isinstance(payload,dict) and payload.get('prepared_id') in qrows:
            row=qrows[payload['prepared_id']];row['events'].append({'kind':kind,'seq':seq})
            if kind in ('q.claim','q.launch_claim','q.admission_intent','q.admission_observed','q.admission_closed'):row[kind]=True
write(HERE/'retained-unknown-witness.json',{'committed_frame_chain_verified':True,'requests':list(qrows.values()),'never_resent':True,'journal_is_not_financial_authority':True,'current_PG_balances_not_claimed':True})

case=read(HERE/'prior/case-index.json');case.setdefault('history',[]).append({'at_return':'continuation-01','cases':copy.deepcopy(case['cases'])})
updates={
 'C01':('PARTIAL_INHERITED_ISOLATED_NEW_WAIT_APPROVAL_ONLY','New teaching prepare/GET/approval/claim observed, model rejected; ACK matrix not executed'),
 'C02':('PARTIAL_REAL_QUERY_NEW_MEMORY_NOT_RUN','Three new actual queries received; selected memory initialization failed before save; full new PG negative probes not reached'),
 'C03':('INHERITED_UNCHANGED_PRODUCT_CHECKS','q_context/q_protocol and original wire compatibility byte identities unchanged; no blanket new PG pass'),
 'C04':('PARTIAL_INHERITED_ONLY','New full-request negative/copy/readonly/cleanup matrix did not execute; old isolated results retained'),
 'C05':('PASS_INHERITED_INERT_CONFIGURATION','No normal Q configuration/authority changed; real activation UNKNOWN'),
 'C06':('PASS_RETAINED_INSTANCES_PARTIAL_THIRD_DATABASE','Original CID/ports identities verified; budget02 created and migrated but roster/memory not complete'),
 'C07':('PARTIAL_REAL_TEACHING_UI_WAIT_GET_APPROVE','A3 fresh local goal, query and pending/GET/approval; original UNKNOWN keys preserved'),
 'C08':('PASS_FOR_LISTED_QUERY_CHAINS','Original chains inherited; actual new A2 query and A3/A2 UI queries received, no model acceptance inferred'),
 'C09':('PARTIAL_A3_NEW_HEAD_MODEL_UNKNOWN','A3 precondition/local goal passed; core index hit valid terminal cache and fixture asserted missing approval; UI new model rejected teaching_validation_unavailable and retained UNKNOWN'),
 'C10':('PARTIAL_INTERVIEW_PENDING_HTML_409','New goal did not close global old UNKNOWN gate; core/UI ask409; HTML409 and legacy followup409; original legacy first/EOL pass inherited'),
 'C11':('NOT_RUN_REMAINING_ACK_K2_RACES','Core ACK depended on successful Interview and memory races on memory creation; both skipped'),
 'C12':('PASS_INHERITED_ACTUAL_COMMON_PG_100_AND_REOPEN','Root11/12/14 retained unchanged; no repetition/refund/new balance claim'),
 'C13':('PARTIAL_ACTUAL_FINAL_DIST_LOADED_THREE_FAILED_FLOWS','All three real browser modes loaded exact final JS/CSS; teaching query/reopen/owner/view assertions reached; final business assertions failed. Remaining head/scope/namespace/DataContext matrix unverified'),
 'C14':('PASS_FRESH_EXACT_STOP_AND_COMMAND_JOB_EXIT','Final041 confirms120 PID/birth,58 Jobs,CID stopped/Pid0,ports released; own command Job tree_empty/exit0'),
 'C15':('PASS_SAVED_IDENTITIES_NOT_ACCEPTANCE','Old result/ZIPs/as-run retained; final post-root16 fixtures syntax/UTF8 checked only; engineering incomplete')}
for row in case['cases']:
    status,facts=updates[row['id']];row.update(status=status,scope02_facts=facts,scope02_evidence='continuation-02/final-review-index.json')
case.update(status=b['engineering_status'],stable_audit_package_ready=False,real_Q='FROZEN',scope02_counts=b['counts'],scope02_failures_entries=len(b['failures']))
write(EX/'case-index.json',case)
ready=read(HERE/'prior/remaining-readiness.json')
ready.update(engineering_stable=False,activated=False,real_Q='FROZEN',scope02_contract_questions_resolved=True,
 current_block='Running root hard cap16/16; service review has recovered, not the present blocker',
 engineering_required=['Resume partial budget02 without recreate/reset, execute creation-time frozen memory save/bind and model positive','Normal Interview local abandon of retained UNKNOWN may be needed before new goal; source accept gate checks all historical unknown commands. Do not resend old claimed key or change global gate','Diagnose actual teaching_validation_unavailable from original worker validation and reconcile new A3 UNKNOWN readonly; never resend','Diagnose preserved HTML/legacy409 with exact safe error code; do not infer or weaken parent/role/config checks','Finish full actual PG permission/ACK/K2/source-memory-scope/read-only-copy matrix','Finish five-entry successful final-dist flows and all required head/scope/namespace/DataContext fences'],
 resource_block={'roots_used':16,'roots_cap':16,'current_counts':b['counts'],'new_runtime_permit_required':True,'platform_capacity_recovered_command039':True},
 source_post_root16_delta='UTF8/cached-index/safe-error fixture repairs saved and syntax checked; not rerun against PG/UI',
 final_stop_proof='DocuN/evidence/TASK-120/execution/continuation-02/final-stop-proof.json',user_keys_or_memory_release_requested=False,independent_audit_started=False)
write(EX/'remaining-readiness.json',ready)

baseline=read(EX/'continuation-01/final-file-identities.json');identities={row['path']:row['sha256'] for row in baseline['current_files']+baseline['new_files']}
for path in (ROOT/'backend/tests/fixtures/task120').glob('*.py'):
    identities.setdefault(path.relative_to(ROOT).as_posix(),None)
pre=read(HERE/'adoption.json')['preimages'];preimages={x['path']:x['sha256'] for x in pre}
current=[];changes=[];new=[];fixture_diff=[]
for rel,old in sorted(identities.items()):
    path=ROOT/rel;actual=sha(path) if path.is_file() else None;current.append({'path':rel,'sha256':actual})
    if rel=='frontend/dist/assets/index-BuUoTjO5.js':assert old is None and actual is None;continue
    assert actual is not None,rel
    if actual!=old:
        assert rel.startswith('backend/tests/fixtures/task120/') or rel.startswith('frontend/tests/task120-'),rel
        row={'path':rel,'before_sha256':old,'after_sha256':actual};(new if old is None else changes).append(row)
        before=HERE/'preimage'/rel
        if old is not None:assert before.is_file() and sha(before)==old
        lines=before.read_text(encoding='utf-8-sig').splitlines(keepends=True) if before.exists() else []
        fixture_diff.extend(difflib.unified_diff(lines,path.read_text(encoding='utf-8-sig').splitlines(keepends=True),fromfile='before/'+rel if before.exists() else '/dev/null',tofile='after/'+rel))
write(HERE/'final-file-identities.json',{'baseline':'continuation-01 final identities','all_current_paths':current,'changed':changes,'new':new,'product_delta_this_scope':0,'final_JS_CSS_dist_unchanged':True,'candidate_is_not_runtime_pass':True})
(HERE/'fixture.diff').write_text(''.join(fixture_diff),encoding='utf-8',newline='\n')
(HERE/'source.diff').write_text('',encoding='utf-8')
rules=[]
for row in read(ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json'):
    actual=sha(row['absolute_path']);rules.append({'path':row['absolute_path'],'expected':row['sha256'],'actual':actual,'matches':actual==row['sha256']})
assert all(x['matches'] for x in rules);write(HERE/'final-rules-check.json',{'all_seven_match':True,'rules':rules})
for asset in read(EX/'final-bundle-identities.json')['assets']:assert sha(ROOT/asset['path'])==asset['sha256']
old_packages=[(EX/'final-review-files.zip',read(EX/'final-review-files-identity.json')['sha256']),(EX/'continuation-01/final-review-candidate.zip',read(EX/'continuation-01/candidate-package-identity.json')['sha256'])]
for path,expected in old_packages:assert sha(path)==expected
old=(HERE/'prior/TASK-120-result.md').read_bytes();assert hashlib.sha256(old).hexdigest()==read(HERE/'adoption.json')['prior_result_sha256']
prefix=(HERE/'result-prefix.md').read_text(encoding='utf-8').replace('@@SAVED@@',now.astimezone(timezone(timedelta(hours=8))).isoformat()).replace('@@FAILURES@@',str(len(b['failures']))).replace('@@WALL@@',f"{b['command_wall_conservative_upper_seconds']:.6f}")
report=ROOT/'DocuN/results/TASK-120-result.md';report.write_bytes(prefix.encode()+old);assert report.read_bytes().endswith(old)
write(HERE/'result-preservation.json',{'old_report_sha256':hashlib.sha256(old).hexdigest(),'old_report_bytes':len(old),'unchanged_original_suffix':True,'new_report_sha256':sha(report)})
index={'task':'TASK-120','scope':'断点纠正02','resource_permit_unchanged':b['current_permit_id'],'status':b['engineering_status'],'engineering_complete':False,'stable_for_independent_audit':False,'real_Q':'FROZEN',
 'report':str(report),'case_index':'../case-index.json','readiness':'../remaining-readiness.json','actual_roots':[15,16],
 'preflights':['command-039.receipt.json','command-040.receipt.json','command-041.receipt.json'],
 'stop':['final-stop-proof.json','command-041.receipt.json'],'as_run':['../root-15-as-run.json','../root-16-batch-03-as-run.json','../root-16-batch-06-as-run.json'],
 'actual_failures':['../root-15-batch-01-failure.json','../root-16-batch-02-failure.json','../root-16-c02-core-result.json','../root-16-c02-ui-result.json'],
 'browser_raw_proofs':[f'../root-16-batch-06-ui-{mode}-proof.json' for mode in ('teaching','interview','legacy_html')],
 'inherited_C12':'../budget-last-slot-race.json and ../root-14-budget-reopen.json; not rerun','inherited_HTML_patch':'../root-14-html-eol-applied.json; not reapplied',
 'diagnostics':['root15-diagnosis.json','retained-unknown-witness.json','post-root16-preimage/'],
 'candidate_only_after_root16':['UTF8 private JSON reads','terminal cached index reconciliation','safe API error extraction'],
 'remaining_roots':0,'runtime_requires_new_explicit_permit':True,'old_packages_unchanged':[{'path':str(p.relative_to(ROOT)),'sha256':h} for p,h in old_packages],
 'fixture_diff':'fixture.diff','file_identities':'final-file-identities.json','rules':'final-rules-check.json','new_package':'final-review-candidate.zip','no_private_runtime_or_usable_Q_material':True}
write(HERE/'final-review-index.json',index)
pack={report,EX/'budget.json',EX/'events.jsonl',EX/'case-index.json',EX/'remaining-readiness.json',EX/'budget-02-bootstrap.json',EX/'budget-02-source-identities.json',EX/'final-bundle-identities.json'}
for path,h in old_packages:pack.add(path)
for row in changes+new:pack.add(ROOT/row['path'])
for path in HERE.rglob('*'):
    if path.is_file() and '__pycache__' not in path.parts and path.suffix not in ('.zip','.pyc') and path.name not in ('candidate-package-identity.json','save-consistency.json'):pack.add(path)
for number in (15,16):pack.update(path for path in EX.glob(f'root-{number:02d}*') if path.is_file())
target=HERE/'final-review-candidate.zip'
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as archive:
    for path in sorted(pack):
        if time.monotonic()-started>55:raise RuntimeError('metadata_packaging_time_limit')
        rel=path.relative_to(ROOT).as_posix();assert not rel.startswith(('.runtime/','.git/'));archive.write(path,rel)
with zipfile.ZipFile(target) as archive:assert archive.testzip() is None
receipt={'path':target.relative_to(ROOT).as_posix(),'bytes':target.stat().st_size,'sha256':sha(target),'files':len(pack),'includes_private_configuration':False,'includes_usable_Q_authority':False,'engineering_complete':False,'real_Q':'FROZEN'}
write(HERE/'candidate-package-identity.json',receipt)
write(HERE/'save-consistency.json',{'utc':datetime.now(timezone.utc).isoformat(),'old_report_suffix_preserved':True,'old_root_failure_event_prefixes_preserved':True,'old_two_ZIPs_unchanged':True,'dist_four_files_unchanged':True,'all_seven_rules_match':True,'archive_CRC_ok':True,'root15_and16_not_restarted':True,'blocked038_never_executed':True,'current_root_cap':b['counts']['roots'],'failures_entries':len(b['failures']),'wall_upper':b['command_wall_conservative_upper_seconds'],'metadata_packaging_seconds':time.monotonic()-started})
print(json.dumps({'report':str(report),'archive':receipt,'failures':len(b['failures']),'roots':b['counts']['roots'],'command_wall_upper':b['command_wall_conservative_upper_seconds']}))
