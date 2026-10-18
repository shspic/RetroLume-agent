"""Pure read/hash ledger reconciliation; no controller/product execution."""
import datetime as dt,hashlib,json,sys,time
from collections import Counter
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8');R=Path('D:/shspic/project_NO3_RetroLume-agent');E=R/'DocuN/evidence/TASK-117/execution';C=E/'continuation-07';O=R/'DocuN/evidence/TASK-118/audit/review-01';T=time.perf_counter();access=[]
def raw(p):
 b=p.read_bytes();access.append({'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()});return b
def load(p):return json.loads(raw(p).decode('utf-8-sig'))
cur=load(E/'budget.json');before=load(C/'before-budget.json');s07before=load(E/'continuation-06/before-budget.json')
ev=raw(E/'events.jsonl');old=raw(C/'before-events.jsonl');events=[json.loads(x) for x in ev.decode('utf-8-sig').splitlines()]
permit=load(R/'DocuN/evidence/TASK-117/orchestration-s08-20261017/continuation-permit.json');timing=load(C/'final-timing.json');p=permit['id'];segment=next(s for s in cur['segments'] if s['permit']==p)
s07=next(s for s in before['segments'] if 'S07' in s['permit']);oldseg={s['permit']:s for s in before['segments']}
skip={'return_disposition','scheduling_amendments'}
def scalars(v):return {k:x for k,x in v.items() if k not in skip and not isinstance(x,(dict,list))}
steps=[x for x in events if x.get('kind')=='S08_offline_process_end'];held=[x for x in cur['runtime_intervals'] if x.get('segment')==p]
failures=cur['failures'][len(before['failures']):]
stops=load(C/'final-resource-stop.json');stopchecks=[]
for row in stops['attempt_stops']:
 b=raw(Path(row['path']));stopchecks.append({'path':row['path'],'hash_match':hashlib.sha256(b).hexdigest()==row['sha256'],'embedded_matches':json.loads(b.decode('utf-8-sig'))==row['stop']})
first=dt.datetime.fromisoformat(timing['first_tool_utc']);last=dt.datetime.fromisoformat(timing['final_readback_sample']['utc'])
report=raw(R/'DocuN/results/TASK-117-result.md');oldreport=raw(C/'before-result.md')
result={'at':dt.datetime.now(dt.timezone.utc).isoformat(),'counts':cur['counts'],'delta_counts':{k:v-permit['baseline_counts'].get(k,0) for k,v in cur['counts'].items()},
 'counts_within_S08_caps':{k:cur['counts'][k]<=v for k,v in permit['cumulative_caps'].items()},'active_root':cur.get('active_root'),'phase':cur.get('phase'),
 'S07_before_fields':scalars(s07),'S08_fields':scalars(segment),'old_segments_exactly_preserved':all(next(s for s in cur['segments'] if s['permit']==k)==v for k,v in oldseg.items()),
 'old_roots_exactly_preserved':cur['roots'][:len(before['roots'])]==before['roots'],'old_failures_exact_prefix':cur['failures'][:len(before['failures'])]==before['failures'],
 'failure_count_before':len(before['failures']),'failure_count_current':len(cur['failures']),'new_failure_count':len(failures),'new_failure_rows':failures,
 'events_old_bytes':len(old),'events_old_sha256':hashlib.sha256(old).hexdigest(),'events_exact_prefix':ev.startswith(old),'S08_offline_end_events':steps,
 'S08_offline_end_seconds_sum':sum(x['seconds'] for x in steps),'S08_holding_intervals':held,'S08_holding_union_upper_sum':sum(x['seconds'] for x in held),
 'final_timing_initial_upper_UTC_seconds':timing['UTC_span_upper_seconds'],'through_readback_UTC_upper_recomputed_seconds':(last-first).total_seconds(),
 'conservative_wall_through_readback':timing['through_readback_conservative_command_wall_seconds'],'conservative_components':{'offline':timing['offline_child_measured_seconds'],'external':timing['through_readback_external_tool_wall_upper_seconds'],'wrapper_reserve':timing['final_wrapper_wall_reserved_upper_seconds']},
 'attempt_stop_checks':stopchecks,'implementation_report':{'bytes':len(report),'sha256':hashlib.sha256(report).hexdigest(),'before_bytes':len(oldreport),'before_sha256':hashlib.sha256(oldreport).hexdigest(),'old_body_exact_suffix':report.endswith(oldreport),'decoded':False},
 'accesses':access,'elapsed_seconds':time.perf_counter()-T}
(O/'ledger-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ('accesses','S08_offline_end_events','S08_holding_intervals')},ensure_ascii=False,indent=2))
