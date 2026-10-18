"""交付文档复读与冻结/预算证明，只读原对象，不启动消费者。"""
import datetime as dt
import json
from pathlib import Path
import re
import time
from bootstrap import ROOT,AUDIT,digest,save,verify

def main():
    now=dt.datetime.now(dt.timezone.utc);mono=time.monotonic_ns()
    receipt=json.loads((AUDIT/'control/receipt.json').read_text(encoding='utf-8'))
    bound=dt.datetime.fromisoformat(receipt['conservative_start_utc'])
    utc_upper=(now-bound).total_seconds()
    mono_upper=(mono-receipt['observed_monotonic_ns'])/1e9+receipt['pre_receipt_charge_seconds']
    receipt['final_observed_utc']=now.isoformat();receipt['final_observed_mono_ns']=mono
    receipt['active_seconds_conservative']=max(utc_upper,mono_upper)
    receipt['calendar_seconds_conservative']=utc_upper
    receipt['active_remaining_conservative_seconds']=max(0,21600-receipt['active_seconds_conservative'])
    receipt['status']='returned_at_scope_stop_no_new_consumers'
    receipt['model_provider_fees_user_data_operations']=0
    save('control/receipt.json',receipt)
    before=json.loads((AUDIT/'protected-before.json').read_text(encoding='utf-8'))
    protected=[{'path':r['path'],'before_sha256':r['sha256'],'after_sha256':digest(Path(r['path'])) if Path(r['path']).is_file() else None} for r in before]
    changes=[r for r in protected if r['before_sha256']!=r['after_sha256']]
    save('protected-after.json',protected)
    inputs=json.loads((ROOT/'DocuN/evidence/TASK-115/orchestration-20261013/input-manifest.json').read_text(encoding='utf-8-sig'))
    current=verify(inputs['frozen_files'],True)
    rules=json.loads((ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json').read_text(encoding='utf-8-sig'))
    rules=verify(rules)
    missing_removed=[r['path'] for r in inputs['removed'] if (ROOT/r['path']).exists()]
    report=ROOT/'DocuN/results/TASK-115-result.md';raw=report.read_text(encoding='utf-8')
    ids=re.findall(r'^- (V\d\d)。',raw,re.M)
    expected=[f'V{i:02}' for i in range(1,30)]
    links=re.findall(r'\]\((D:/[^)]+)\)',raw)
    missing_links=[p for p in links if not Path(p).exists()]
    checks={'matrix_exact_29':ids==expected,'no_asterisk':not '*' in raw,'missing_links':missing_links,
       'current_frozen_mismatches':[r['path'] for r in current if not r['match']],
       'rule_mismatches':[r['path'] for r in rules if not r['match']],
       'protected_changes':changes,'removed_file_reappeared':missing_removed,
       'control_counts_within_limits':all(receipt['new_counts'][name]<=receipt['limits'][name] for name in ('roots','api','browser','source_start','target07_start','create_attempts','pg_success')),
       'active_bound_within_limit':receipt['active_seconds_conservative']<=21600,
       'holding_within_limit':receipt['new_counts']['holding_seconds']<=2100,
       'offline_tests_within_limit':receipt['new_counts']['offline_test_seconds']<=3600}
    evidence=[]
    for p in sorted(AUDIT.rglob('*')):
        if p.is_file() and 'browser-root' not in p.parts and p.name!='delivery.json':
            evidence.append({'path':str(p),'bytes':p.stat().st_size,'sha256':digest(p)})
    value={'utc':now.isoformat(),'report':{'path':str(report),'bytes':report.stat().st_size,'sha256':digest(report),
       'lines':len(raw.splitlines()),'readback_complete':True},'checks':checks,
       'protected_file_count':len(protected),'current_file_count':len(current),
       'active_seconds_conservative':receipt['active_seconds_conservative'],
       'active_remaining_conservative_seconds':receipt['active_remaining_conservative_seconds'],
       'new_counts':receipt['new_counts'],'evidence':evidence,
       'result':'independent audit report returned; candidate not accepted; no final master acceptance'}
    save('delivery.json',value)
    print(json.dumps({k:value[k] for k in ('utc','report','checks','protected_file_count','current_file_count','active_seconds_conservative','active_remaining_conservative_seconds','new_counts')},ensure_ascii=False))
    assert checks['matrix_exact_29'] and checks['no_asterisk'] and not any(checks[k] for k in ('missing_links','current_frozen_mismatches','rule_mismatches','protected_changes','removed_file_reappeared'))
    assert all(checks[k] for k in ('control_counts_within_limits','active_bound_within_limit','holding_within_limit','offline_tests_within_limit'))

if __name__=='__main__':main()
