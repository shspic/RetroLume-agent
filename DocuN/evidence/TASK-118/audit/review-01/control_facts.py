"""Numeric original command receipts, segment clocks and exact root deadlines only."""
import datetime as dt,hashlib,json,sys,time
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8');R=Path('D:/shspic/project_NO3_RetroLume-agent');C=R/'DocuN/evidence/TASK-117/execution/continuation-07';O=R/'DocuN/evidence/TASK-118/audit/review-01';T=time.perf_counter();access=[]
def raw(p):
 b=p.read_bytes();access.append({'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()});return b
def load(p):return json.loads(raw(p).decode('utf-8-sig'))
receipts={}
for name in ('tool-receipts-at-seal.json','tool-receipts-complete.json'):
 v=load(C/name);rows=[{k:r.get(k) for k in ('label','chunk_id','wall_time_seconds','exit_code')} for r in v['commands']]
 receipts[name]={'first_batches_upper_seconds':v['first_batches_upper_seconds'],'recorded_total':v['command_wall_upper_seconds'],
    'recomputed':v['first_batches_upper_seconds']+sum(r['wall_time_seconds'] for r in rows),'commands':rows}
roots=[]
for rel in ('root-25','root-25/attempt-02','root-25/attempt-03'):
 spec=load(C/rel/'spec.json');stop=load(C/rel/'stop.json');r=spec['root']
 roots.append({'path':rel,'id':r['id'],'attempt':r.get('attempt_number'),'business_deadline_utc':r['business_deadline_utc'],'business_deadline_mono_ns':r['business_deadline_mono_ns'],
 'stop_utc':stop['sample']['utc'],'stop_before_business_deadline':dt.datetime.fromisoformat(stop['sample']['utc'])<dt.datetime.fromisoformat(r['business_deadline_utc']),
 'child_exit_code':stop['child_exit_code'],'holding_upper':stop['holding_union_upper_seconds'],'same_birth_alive':stop['same_birth_alive'],'port_no_listener':stop['18119_no_listener']})
s07=load(C.parent/'continuation-06/final-timing.json');s08=load(C/'final-timing.json')
f=s07['first_tool'];s=s07['sample'];stop=s07['final_save_sample']
result={'at':dt.datetime.now(dt.timezone.utc).isoformat(),'receipt_facts':receipts,'root_attempts':roots,'root_deadlines_equal':len({r['business_deadline_mono_ns'] for r in roots})==1 and len({r['business_deadline_utc'] for r in roots})==1,
 'S07_timing':s07,'S08_wall_recomputed':s08['offline_child_measured_seconds']+s08['through_readback_external_tool_wall_upper_seconds']+s08['final_wrapper_wall_reserved_upper_seconds'],
 'S08_boot_epoch_spread_seconds':abs(s08['clock_anchor']['boot_epoch_seconds']-s08['final_readback_sample']['boot_epoch_seconds']),
 'S08_refuse_clock_back_source_guard':{'mono_ns':True,'boot_epoch_tolerance_seconds':2,'UTC_backward_tolerance_seconds':2,'new_live_clock_check_by_auditor':False},
 'accesses':access,'elapsed_seconds':time.perf_counter()-T}
(O/'control-facts.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'receipt_totals':{k:{x:y for x,y in v.items() if x!='commands'} for k,v in receipts.items()},'root_attempts':roots,'root_deadlines_equal':result['root_deadlines_equal'],'S07_timing':s07,'S08_wall_recomputed':result['S08_wall_recomputed'],'S08_boot_epoch_spread_seconds':result['S08_boot_epoch_spread_seconds'],'seconds':result['elapsed_seconds']},ensure_ascii=False,indent=2))
