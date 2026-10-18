"""结果保存/可读/路径核对；不运行产品或验收方法。"""
from control import ROOT,HERE,state,write,sha,event,sample
from pathlib import Path
import re,json,time
path=ROOT/'DocuN/results/TASK-117-result.md'
raw=path.read_bytes();text=raw.decode('utf-8','strict')
targets=re.findall(r'\]\((D:/[^)]+)\)',text)
missing=[p for p in targets if not Path(p).exists()]
if missing:raise RuntimeError('saved_result_has_missing_links:'+repr(missing))
cases=json.loads((HERE/'case-index.json').read_text(encoding='utf-8'))
assert len(cases['cases'])==28 and cases['passed_frozen_scenarios']==0
rules=json.loads((HERE/'final-rules-identity.json').read_text(encoding='utf-8'))
assert all(r['unchanged'] for r in rules['rules'])
resources=json.loads((HERE/'final-resource-stop.json').read_text(encoding='utf-8'))
assert all(not r['running'] and r['pid']==0 for r in resources['pg'])
value=state();assert value['active_root'] is None
value['phase']='hard_stopped_partial_result_saved'
value['stop_disposition']={'sample':sample(),'result':str(path),'result_sha256':sha(raw),'S_complete':False,'Q_enabled':False,'activity_remaining_seconds':0,'continuation_requires_master_card':True,'all_original_counters_and_failures_retained':True}
write(HERE/'budget.json',value)
proof={'sample':sample(),'path':str(path),'sha256':sha(raw),'bytes':len(raw),'utf8_strict_readback':True,'existing_local_links':len(targets),'missing_links':[],'case_count':28,'S_complete':False,'Q_enabled':False,'activity_elapsed_at_save_seconds':(time.monotonic_ns()-value['start_mono_ns'])/1e9,'counts':value['counts'],'all_owned_resources_stopped':True,'new_product_runs_after_budget_stop':0}
write(HERE/'result-save-receipt.json',proof)
event('result_saved_readback_verified',path=str(path),sha256=sha(raw),bytes=len(raw),status='partial_hard_budget_stop')
print(json.dumps(proof,ensure_ascii=False))
