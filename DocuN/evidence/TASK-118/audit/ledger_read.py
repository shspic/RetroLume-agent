"""唯一原账的只读分段归并，保留全部失败，不反写工程账。"""
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys
import time
sys.stdout.reconfigure(encoding='utf-8')
started=time.perf_counter()
root=Path('D:/shspic/project_NO3_RetroLume-agent')
e=root/'DocuN/evidence/TASK-117/execution'
out=root/'DocuN/evidence/TASK-118/audit'
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def brief(v):
    if isinstance(v,dict):
        return {k:(brief(x) if isinstance(x,dict) and k in ('caps','baseline_counts','counts','clock','costs') else x if not isinstance(x,(dict,list)) else {'type':type(x).__name__,'length':len(x),'keys':list(x) if isinstance(x,dict) else None}) for k,x in v.items()}
    return v
b=read(e/'budget.json');old=read(e/'continuation-05/before-budget.json')
prefix=read(e/'continuation-05/before-events.jsonl-identity.json')
raw=(e/'events.jsonl').read_bytes()
def expected_identity(value):
    if isinstance(value,dict):
        if 'bytes' in value and 'sha256' in value:return value
        for x in value.values():
            found=expected_identity(x)
            if found:return found
    return None
ident=expected_identity(prefix)
events=[json.loads(line) for line in raw.splitlines() if line.strip()]
eventkinds={}
for event in events:
    key=str(event.get('event',event.get('kind',event.get('type','<none>'))))
    eventkinds[key]=eventkinds.get(key,0)+1
result={'at':dt.datetime.now(dt.timezone.utc).isoformat(),'counts':b['counts'],'caps':b['caps'],'phase':b.get('phase'),'active_root':b['active_root'],
 'segments':[brief(v) for v in b['segments']], 'S01':{k:brief(b[k]) for k in ('start_utc','start_mono_ns','activity_cap_seconds','runtime_holding_cap_seconds','offline_cap_seconds','stop_disposition')},
 'roots':[brief(v) for v in b['roots']], 'failures':b['failures'],
 'runtime_intervals':[brief(v) for v in b['runtime_intervals']],
 'offline_intervals':[brief(v) for v in b['offline_intervals']],
 'preservation':{'segments_equal':b['segments'][:len(old['segments'])]==old['segments'],'first_21_roots_equal':b['roots'][:len(old['roots'])]==old['roots'],
 'failures_exact_old_prefix':b['failures'][:len(old['failures'])]==old['failures'],'events_expected_identity':ident,
 'events_exact_old_prefix':None if ident is None else hashlib.sha256(raw[:ident['bytes']]).hexdigest()==ident['sha256']},
 'event_count':len(events),'event_kinds':eventkinds,'elapsed_seconds':time.perf_counter()-started}
(out/'ledger-facts.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:result[k] for k in ('counts','phase','active_root','segments','S01','preservation','event_count')},ensure_ascii=False,indent=2))
print('failure_count='+str(len(b['failures'])))
for f in b['failures']:print(json.dumps(brief(f),ensure_ascii=False))
