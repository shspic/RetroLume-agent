"""Finite no-resource S06 parsing checks; synthetic state never writes production ledger."""
import sys,json,time,copy
from pathlib import Path
N=Path(__file__).resolve().parent;sys.path.insert(0,str(N.parent))
import control as c
v=c.state();s=next(x for x in v['segments'] if x['permit']==v['active_segment'])
now=time.monotonic_ns();checks=[]
def run(name,change,expected=None):
    value=copy.deepcopy(v);segment=next(x for x in value['segments'] if x['permit']==value['active_segment'])
    change(value,segment)
    try:c.guard_s06(value,segment);actual=None
    except RuntimeError as error:actual=str(error)
    assert actual==expected,(name,actual,expected)
    checks.append({'name':name,'expected':expected,'actual':actual,'passed':True})
run('null_is_unbounded_offresource_with_old_overruns',lambda v,s:None)
run('null_not_zero',lambda v,s:s.update(offline_cap_seconds=0),'S06_offline_policy_mismatch')
run('activity_still_enforced',lambda v,s:s.update(start_mono_ns=now-13201*10**9),'S06_save_only_activity_gate')
run('process_runtime_still_enforced',lambda v,s:s.update(offline_process_run_seconds=1801),'S06_offline_process_hard_gate')
run('holding_still_enforced',lambda v,s:v['runtime_intervals'].append({'segment':s['permit'],'seconds':5401}),'S06_runtime_hard_gate')
run('suspended_no_legacy_fallback',lambda v,s:s.update(status='suspended'),'S06_permit_suspended_or_returned')
run('returned_no_legacy_fallback',lambda v,s:s.update(status='returned_partial'),'S06_permit_suspended_or_returned')
oldstate,oldwrite,oldevent=c.state,c.write,c.event
try:
    c.state=lambda:copy.deepcopy(v);c.write=lambda *a:None;c.event=lambda *a,**k:None
    c.reserve_offline(30)
    for counter in ('roots','pg_starts','api_starts','browser_starts','preview_starts','http'):
        trial=copy.deepcopy(v);trial['counts'][counter]=next(x for x in trial['segments'] if x['permit']==trial['active_segment'])['baseline_counts'][counter]
        c.state=lambda trial=trial:copy.deepcopy(trial)
        c.count(counter);checks.append({'name':'S06_counter_'+counter,'passed':True,'production_mutated':False})
    c.state=lambda:copy.deepcopy(v)
    for counter in ('pg_create_attempts','pg_objects','volumes'):
        try:c.count(counter)
        except RuntimeError as error:assert '次数门关闭' in str(error)
        else:raise AssertionError('conditional seventh object accepted without actual overlay evidence')
        checks.append({'name':'S06_default_no_conditional_'+counter,'passed':True,'production_mutated':False})
finally:c.state,c.write,c.event=oldstate,oldwrite,oldevent
c.write(N/'controller-boundaries.json',{'sample':c.sample(),'checks':checks,'passed':True,'no_runtime_resources_started':True,'source_sha256':c.sha((N.parent/'control.py').read_bytes())})
print(json.dumps({'passed':True,'checks':len(checks)}))
