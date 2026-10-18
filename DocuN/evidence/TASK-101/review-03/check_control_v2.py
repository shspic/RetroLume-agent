from audit_io import *
from collections import Counter
raw=ROOT/'DocuN/evidence/TASK-100/answer-support-repair-04'
ledger=load(raw/'session-accounting.json'); execution=load(raw/'batch-01/execution.json')
index=load(ROOT/'DocuN/evidence/TASK-101/review-03-input.json')
final=load(raw/'final-identities.json'); pre=load(raw/'pre-identities.json')
receipt_dir=ROOT/'DocuN/evidence/TASK-100/orchestration-receipt-07'
assert ledger['offline_batches_used']==len(ledger['offline_batches'])==1 and ledger['offline_batches_limit']==3
assert ledger['offline_batches'][0]==execution
assert execution['number']==1 and execution['started_monotonic']<execution['started_process_monotonic']<execution['ended_monotonic']
assert abs(execution['ended_monotonic']-execution['started_monotonic']-execution['elapsed_seconds'])<0.0001
assert execution['timeout_seconds']==55 and execution['process_elapsed_seconds']<55
assert execution['outer_shell_tool_elapsed_seconds']==execution['offline_charged_seconds']==ledger['offline_charged_seconds']==1.6463436
assert execution['offline_charged_seconds']<60 and ledger['offline_charged_seconds']<ledger['offline_limit_seconds']==600
assert abs(ledger['end_monotonic']-ledger['start_monotonic']-ledger['active_measured_through_final_package_seconds'])<0.0001
components=ledger['active_charge_components']
assert abs(sum(components.values())-ledger['active_charged_upper_seconds'])<0.0001
assert components['initial_unknown_charged_seconds']==180 and components['final_recording_tool_return_and_reply_unknown_charged_seconds']==15
assert abs(ledger['active_charged_upper_seconds']-1779.265)<0.0001 and ledger['active_charged_upper_seconds']<ledger['active_limit_seconds']==3600
assert abs(ledger['active_charged_upper_seconds']-ledger['report_upper_checkpoint_seconds']-ledger['report_to_final_package_seconds'])<0.0001
assert abs(ledger['report_to_final_package_seconds']-2.515)<0.0001
assert all(value==0 for value in ledger['resource_counts'].values())
assert 'stopped' in ledger['status'] and ledger['metadata_failures'][0]['exit_code']==1
for x in ledger['source_freeze'].items(): assert sha(ROOT/x[0])==x[1]
changes={x['path'] for x in index['changes'] if x['changed']}
records=[]
for before,after in zip(pre['records'],final['records']):
    assert before['path']==after['path'] and before['actual']==after['pre_sha256']
    path=Path(after['path'])
    if path == ROOT/'DocuN/results/TASK-100-result.md':
        records.append({'path':str(path),'group':after['group'],'binding':'excluded-author-report-content','changed_from_pre':after['changed_from_pre']})
        continue
    current_sha=sha(path)
    historical_target=receipt_dir/'before'/path.relative_to(ROOT) if path.is_relative_to(ROOT) else None
    if current_sha==after['actual_final_sha256']:
        binding='current'
    elif historical_target is not None and historical_target.is_file() and sha(historical_target)==after['actual_final_sha256']:
        binding='orchestration-receipt-07/before'
    else:
        raise ValueError('unexplained original snapshot drift: '+str(path))
    rel=str(path.relative_to(ROOT)).replace('\\','/') if path.is_relative_to(ROOT) else None
    assert not after['changed_from_pre'] or rel in changes
    records.append({'path':str(path),'group':after['group'],'binding':binding,'expected_sha256':after['actual_final_sha256'],'current_sha256':current_sha,'changed_from_pre':after['changed_from_pre']})
assert len(records)==178
notes=load(raw/'method-applicability.json')
summary={'at':stamp(),'ledger_math_and_execution_pairing':True,'batches_used':1,'batch_limit':3,'methods':18,'subtest_callbacks':81,'offline_charged_seconds':ledger['offline_charged_seconds'],'active_charged_upper_seconds':ledger['active_charged_upper_seconds'],'active_components':components,'report_checkpoint_to_final_seconds':ledger['report_to_final_package_seconds'],'resource_counts':ledger['resource_counts'],'counter_timestamp_before_child':True,'recorded_child_timeout_seconds':55,'actual_outer_elapsed_under_60':True,'failed_metadata_search_retained':ledger['metadata_failures'],'final_snapshot_rows':records,'final_snapshot_current_vs_historical':dict(Counter(x['binding'] for x in records)),'metadata_notes_shape':list(notes) if isinstance(notes,dict) else len(notes),'grade_limit':'historical invocation/receipt and arithmetic; no fresh timeout fault test, resource inspection, product import or execution'}
save('execution-control-check.json',summary)
finish('execution-control-and-historical-bindings', {k:v for k,v in summary.items() if k not in ('final_snapshot_rows','metadata_notes_shape')})

