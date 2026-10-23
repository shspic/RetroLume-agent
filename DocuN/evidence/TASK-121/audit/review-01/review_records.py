"""Saved-record comparison for TASK121 review01; stdlib only."""
import collections, datetime, hashlib, json
from pathlib import Path
ROOT=Path(r'D:\shspic\project_NO3_RetroLume-agent')
E=ROOT/'DocuN/evidence/TASK-120/execution/audit-repair-07'
O=ROOT/'DocuN/evidence/TASK-121/audit/review-01'
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(b):return hashlib.sha256(b).hexdigest()
def facts(n):
 d=load(E/n);return d.get('facts',d),d.get('root')
migration=[]
for n in ['F01-missing-insert-PASS.json','F01-missing-update-PASS.json','F01-select-only-PASS.json']:
 f,r=facts(n);migration.append(dict(file=n,root=r,preconditions=f['actual_preconditions'],error=f['error'],
 endpoint=f['endpoint'],before_after_equal=f['before']==f['after'],new_connection_equal=f['new_connection_equal']))
role=[]
for p in sorted(E.glob('F02-*.json')):
 f,r=facts(p.name);row=dict(file=p.name,root=r)
 for k in ('name','endpoint','subject','exact_uncommitted_statements','actual_PG_capability','actual_management_capability',
 'actual_snapshot_login','actual_DELETE_false_rows','schema_check_error','ROLLBACK_confirmed','new_connection_graph_exact',
 'temporary_bridges_retained','actual_login','normal_configuration_passed','write_error'):
  if k in f:row[k]=f[k]
 role.append(row)
cleanup=[]
for n in ['F03-normal-memory-revoke-purge-PASS.json','F03-source-cleanup-failure-closed-PASS.json','F03-exact-cleanup-replay-and-retry-PASS.json']:
 f,r=facts(n);before,after=f['before'],f['after']
 row=dict(file=n,root=r,witness_equal={k:before[k]==after[k] for k in before},requests_before=before['financials']['requests'],
 cost_before=before['financials']['cost'],before_operation_count=len(before['operations']),before_007=before['007_hashes'])
 for k in ('normal_HTTP_receipt','normal_source_HTTP_receipt','memory','Q_bodies','receipt','all_target_Q_body_paths_absent',
 'same_pending_job','replayed_before_retry','after_retry','normal_Q_GET_projection','normal_content_GET_error','normal_continue_POST_error'):
  if k in f:row[k]=f[k]
 cleanup.append(row)
manifest=load(E/'F03-exact-new-deletion-manifest.json')
claim,claimroot=facts('F05-PG-claimed-before-Q-claim-PASS.json')
claim_result=dict(root=claimroot,PG_fact=claim['actual_PG_COMMIT'],Q_claim_absent=claim['Q_claim_absent'],
 snapshot_unchanged=claim['frozen_snapshot_unchanged'],immediate=claim['immediate_GET_projection'],
 repeated=claim['repeated_GET_projection'],errors=claim['operator_immediate_and_after_15min_errors'],
 financials_equal=claim['financials_before']==claim['financials_after'],new_approvals=claim['new_approval_events'],
 dispatches=claim['worker_dispatches_for_claimed_operation'])
clock=load(E/'F04-clock-authorization-PASS.json')
clock_records=[json.loads(x)for x in (E/'F04-API-worker-clock-samples.jsonl').read_text(encoding='utf-8-sig').splitlines()]
positive,positiveroot=facts('F04-real-API-operator-worker-normal-combination-PASS.json')
financial=load(E/'financial-summary.json')
record_result=dict(F01=migration,F02=role,F03=cleanup,F04=dict(cases=clock['cases'],positive_root=positiveroot,
 sample_count=len(clock_records),process_ids=sorted({x['pid']for x in clock_records}),domains=sorted({x['domain']for x in clock_records}),
 offsets=sorted({x['offset_seconds']for x in clock_records}),positive=positive),F05=claim_result,
 exact_cleanup_manifest=dict(count=len(manifest['files']),cap=manifest['maximum'],root=manifest['root'],files=manifest['files']),
 final_financial=financial,limitations=['All are saved original observations; auditor executed no PG/API/worker/filesystem deletion.',
 'F02 composite ADMIN-to-SET and F03 memory-failure GET are static residual findings; not covered by these passing records.'])
save('evidence-comparison.json',record_result)
b=load(E.parent/'budget.json');old=load(E/'budget.json.before.bytes')
raw_events=(E.parent/'events.jsonl').read_bytes();old_events=(E/'events.jsonl.before.bytes').read_bytes()
events=[json.loads(x) for x in raw_events.decode('utf-8-sig').splitlines()]
old_event_rows=[json.loads(x) for x in old_events.decode('utf-8-sig').splitlines()]
new=events[len(old_event_rows):]
rootrows=[]
for r in b['roots'][51:]:
 result=r['result']
 rootrows.append(dict(id=r['id'],start_utc=r['start_utc'],permit_id=r['permit_id'],entry_counts=r['counts_at_entry'],
  elapsed=result['root_elapsed_seconds'],exit_code=result['exit_code'],end_utc=result['utc'],
  cleanup_all_confirmed=result['cleanup']['all_confirmed'],holding=result['runtime_holding_union_seconds'],
  minimum_available_bytes=result['cleanup']['physical_memory']['minimum_bytes'],
  pressure_events=result['cleanup']['physical_memory']['pressure_events']))
commands=[]
for n in [str(i).zfill(3) for i in range(72,81)]+['999']:
 f=load(E/('command-'+n+'.receipt.json'))
 commands.append(f)
component_keys=['pre_controller_wall_upper_seconds','controlled_command_wall_seconds','runtime_command_wall_seconds',
'unwrapped_metadata_wall_reserved_seconds','continuation_metadata_uncertainty_reserved_seconds',
'continuation02_unwrapped_command_wall_upper_seconds','repair03_unwrapped_command_wall_upper_seconds',
'validation04_unwrapped_command_wall_upper_seconds','finalization05_unwrapped_command_wall_upper_seconds',
'continuation06_unwrapped_command_wall_upper_seconds','audit_repair07_unwrapped_command_wall_upper_seconds']
components={k:b[k]for k in component_keys}
stop=load(E/'final-stop-proof.json')
stop_result={k:v for k,v in stop.items()if k not in ('registered_processes','registered_jobs')}
stop_result.update(process_count=len(stop['registered_processes']),job_count=len(stop['registered_jobs']),
 same_identity_running=[x for x in stop['registered_processes'] if x.get('same_identity_running') is not False],
 unknown_processes=[x for x in stop['registered_processes'] if x.get('observation',{}).get('state')=='unknown'],
 nonempty_or_unknown_jobs=[x for x in stop['registered_jobs']if x.get('active_processes')!=0])
retained_keys=['unwrapped_metadata_wall_reserved_seconds','continuation_metadata_uncertainty_reserved_seconds',
'continuation02_unwrapped_command_wall_upper_seconds','repair03_unwrapped_command_wall_upper_seconds',
'validation04_unwrapped_command_wall_upper_seconds','finalization05_unwrapped_command_wall_upper_seconds',
'continuation06_unwrapped_command_wall_upper_seconds','holding_uncertainty']
control=dict(events_total=len(events),old_events=len(old_event_rows),events_prefix_exact=raw_events.startswith(old_events),
 old_roots_exact=b['roots'][:len(old['roots'])]==old['roots'],old_failures_prefix_exact=b['failures'][:len(old['failures'])]==old['failures'],
 old_unknowns_retained={k:b.get(k)==old.get(k) for k in retained_keys},new_event_kinds=dict(collections.Counter(x.get('kind',x.get('event'))for x in new)),
 new_synthetic_transport=[x for x in new if x.get('kind')=='synthetic_provider_transport'],counts=b['counts'],caps=b['caps'],
 delta_counts={k:b['counts'][k]-old['counts'][k]for k in b['counts']},old_failures=len(old['failures']),current_failures=len(b['failures']),
 new_failures=b['failures'][len(old['failures']):],roots=rootrows,commands=commands,wall_components=components,
 wall_component_sum=sum(components.values()),wall_reported=b['command_wall_conservative_upper_seconds'],
 holding=b['runtime_holding_union_seconds'],new_holding=sum(x['holding']for x in rootrows),holding_old=old['runtime_holding_union_seconds'],
 logical_databases=b['audit_repair07_logical_databases'],admissions=b['audit_repair07_synthetic_admissions'],
 admission_cap=b['audit_repair07_synthetic_admission_cap'],current_active_root=b['active_root'],current_active_command=b['active_command'],
 adoption=load(E/'adoption.json'),stop=stop_result,sole_ledger_sha256=sha((E.parent/'budget.json').read_bytes()),
 sole_events_sha256=sha(raw_events),original96h_deadline=b['calendar_deadline_utc'],fresh_runtime_probe_by_auditor=False)
save('control-reconstruction.json',control)
print(json.dumps(dict(F01_negative_rows=len(migration),F02_records=len(role),cleanup_rows=len(cleanup),
 cleanup_witness_all_equal=all(all(r['witness_equal'].values())for r in cleanup),
 clock_pids=record_result['F04']['process_ids'],claim_financial_equal=claim_result['financials_equal'],
 exact_manifest_files=len(manifest['files']),event_prefix_exact=control['events_prefix_exact'],
 old_roots_exact=control['old_roots_exact'],old_failures_prefix_exact=control['old_failures_prefix_exact'],
 wall_sum=control['wall_component_sum'],wall_reported=control['wall_reported'],new_holding=control['new_holding'],
 new_synthetic_dispatches=len(control['new_synthetic_transport']),stop_processes=stop_result['process_count'],
 stop_jobs=stop_result['job_count'],stop_running=len(stop_result['same_identity_running']),
 stop_unknown=len(stop_result['unknown_processes'])+len(stop_result['nonempty_or_unknown_jobs'])),ensure_ascii=False))

