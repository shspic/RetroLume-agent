"""Read existing C03 raw JSON/log/code; do not execute original methods."""
from pathlib import Path
import datetime as dt
import difflib
import hashlib
import json
import re
import time

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
C03 = ROOT / 'DocuN/evidence/TASK-114/implementation/continuation-03'
OUT = ROOT / 'DocuN/evidence/TASK-115/review-02'

def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def write(name,data): (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def normalized(path): return Path(str(path).replace('\\\\','/').replace('\\','/'))
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

run1='c03-browser-1210213609000000'
run2='c03-browser-1210447187000000'
batch1=C03/'batches'/run1
batch2=C03/'batches'/run2
result=read(batch2/'result.json')
failure=read(batch1/'failure.json')
requests=result['requests']
phases=list(dict.fromkeys(r['phase'] for r in requests))
summary={
    'source':str(batch2/'result.json'),
    'state':result['state'],'layer':result['layer'],
    'request_count':len(requests),
    'case_count':len(result['cases']),
    'cases':result['cases'],
    'errors':result['errors'],
    'sequence':result['sequence'],
    'consumer_action_counts':{k:result[k] for k in ['explicit_restore_POST','explicit_export_POST','explicit_activate_POST','automatic_action_POST']},
    'all_requests':requests,
    'per_phase':[{'phase':p,'post_requests':[r for r in requests if r['phase']==p and r['method']=='POST'],'reads':sum(r['phase']==p and r['method']=='GET' for r in requests)} for p in phases],
    'final_identity_actual':[{'path':e['path'],'expected':e['sha256'],'actual':digest(ROOT/e['path']),'matches':digest(ROOT/e['path'])==e['sha256']} for e in result['finalIdentity']],
    'first_failure':{'source':str(batch1/'failure.json'),'type':failure.get('type'),'message':failure.get('message'),'phase_request_counts':{p:sum(r['phase']==p for r in failure['requests']) for p in dict.fromkeys(r['phase'] for r in failure['requests'])},'matrix_cases':failure.get('cases'),'page_errors':failure.get('errors'),'has_failure_dom':(batch1/'failure-dom.txt').exists(),'has_failure_png':(batch1/'failure.png').exists()},
    'own_metadata_read_failure':{'command_exit':1,'path':str(C03/'methods'/f'{run2}.json'),'cause':'Browser method lives under batches/<run>/method.json; guessed methods path absent; corrected by actual directory listing','product_runs':0},
}
for run in [run1,run2]:
    batch=C03/'batches'/run
    summary[run]={'method':read(batch/'method.json'),'begin':read(batch/'method-begin.json'),'events':[json.loads(l) for l in (batch/'events.jsonl').read_text(encoding='utf-8-sig').splitlines() if l.strip()],'stderr':(batch/'stderr.log').read_text(encoding='utf-8-sig')}

identities=read(OUT/'as-run-identity.json')
def as_original(run,relative):
    row=next(r for r in identities if r['label']==run)
    binding=next(b for b in row['actual_bindings'] if b['path']==relative)
    assert binding['as_run_matches']
    return normalized(binding['actual']['path'])
as1=as_original(run1,'frontend/tests/task114-c03-inputs.mjs')
as2=as_original(run2,'frontend/tests/task114-c03-inputs.mjs')
(OUT/'browser-fixture-first-to-final.diff').write_text(''.join(difflib.unified_diff(as1.read_text(encoding='utf-8').splitlines(keepends=True),as2.read_text(encoding='utf-8').splitlines(keepends=True),fromfile=run1+'/fixture',tofile=run2+'/fixture')),encoding='utf-8')
write('browser-raw-analysis.json',summary)

pin_method=read(C03/'methods/loading-pin-1207676843000000.json')
pin_cases=[read(C03/'offline/cases/loading-pin-1207676843000000'/name) for name in ['01-same-operation.json','02-no-connect.json','03-actual-load.json']]
write('pin-raw-analysis.json',{'method':pin_method,'cases':pin_cases,'log':(C03/'offline/loading-pin-1207676843000000.log').read_text(encoding='utf-8-sig'),'product_call_sites':[{'path':'backend/app/data_exit/restore.py','line':445,'operation_keyword_required':True}], 'current_reference_sha256':digest(ROOT/'backend/app/data_exit/reference.py'),'current_restore_sha256':digest(ROOT/'backend/app/data_exit/restore.py')})

receipt=read(ROOT/'DocuN/evidence/TASK-114/implementation/control/receipt.json')
pre_receipt=read(C03/'pre/receipt.json')
pre_events=(C03/'pre/events.jsonl').read_bytes()
events=(ROOT/'DocuN/evidence/TASK-114/implementation/control/events.jsonl').read_bytes()
control={'receipt_keys':list(receipt),'pre_receipt_keys':list(pre_receipt),'old_events_exact_prefix':events.startswith(pre_events),'pre_events_bytes':len(pre_events),'current_events_bytes':len(events),'new_events':[json.loads(l) for l in events[len(pre_events):].decode('utf-8').splitlines() if l.strip()],'final_delivery':read(C03/'final/delivery.json'),'inheritance_navigation':read(C03/'final/inheritance.json')}
for key in receipt:
    if key in ['counts','limits','resources','continuation_history','active_continuation','continuation','roots','used','hard_deadline_utc','calendar_deadline','status'] or 'continu' in key or 'activity' in key or 'offline' in key or 'holding' in key:
        control[key]=receipt[key]
for key in ['resources','continuation_history']:
    if key in pre_receipt:
        if isinstance(pre_receipt[key],dict): control[key+'_old_exact']=all(receipt.get(key,{}).get(k)==v for k,v in pre_receipt[key].items())
        elif isinstance(pre_receipt[key],list): control[key+'_old_exact']=receipt.get(key,[])[:len(pre_receipt[key])]==pre_receipt[key]
write('control-original-analysis.json',control)

index=read(C03/'final/method-index.json')['methods']
method_compact=[{k:m.get(k) for k in ['label','argv','cwd','start','end','exit_code','seconds','log','as_run']}|{'not_final_tested_files':[f['path'] for f in m.get('tested_file_bindings',[]) if not f.get('same_final_bytes',False)]} for m in index]
write('method-navigation.json',method_compact)
print(json.dumps({'browser_requests':len(requests),'cases':[c['case'] for c in result['cases']],'phase_posts':[{'phase':p,'posts':[{'seq':r['seq'],'path':r['path'],'body':r['body']} for r in requests if r['phase']==p and r['method']=='POST']} for p in phases],'held_released': [{'event':e['event'],'kind':e['kind'],'phase':e['phase'],'result':e.get('result')} for e in result['sequence']],'binding_mismatches':[e['path'] for e in summary['final_identity_actual'] if not e['matches']],'first_failure':summary['first_failure'],'control_keys':list(receipt),'old_events_prefix':control['old_events_exact_prefix'],'new_event_count':len(control['new_events']),'methods':method_compact},ensure_ascii=False,indent=2))
