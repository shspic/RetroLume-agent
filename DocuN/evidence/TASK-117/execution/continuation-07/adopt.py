"""核对S08明确采用输入，追加新许可；保留S07及更早全部历史。"""
from datetime import datetime,timedelta,timezone
from pathlib import Path
import json
import uuid
from control import N,E,ROOT,PERMIT,sample,sha,write,event

assert not (N/'receipt.json').exists(),'已有接收点，不重置'
P=ROOT/'DocuN/evidence/TASK-117/orchestration-s08-20261017'
manifest=json.loads((P/'input-manifest.json').read_text(encoding='utf-8'))
permit=json.loads((P/'continuation-permit.json').read_text(encoding='utf-8'))
assert permit['id']==PERMIT and permit['Q_enabled'] is False
verified=[]
def walk(value):
    if isinstance(value,dict):
        path=value.get('path',value.get('absolute_path'))
        if path and 'sha256' in value:
            p=Path(path);exists=p.exists();actual=sha(p.read_bytes()) if exists else None
            assert exists==value.get('exists',True) and actual==value['sha256'],path
            verified.append({'path':str(p),'sha256':actual,'exists':exists})
        else:
            for child in value.values():walk(child)
    elif isinstance(value,list):
        for child in value:walk(child)
walk(manifest)
b=json.loads((E/'budget.json').read_text(encoding='utf-8'))
assert b['active_root'] is None and b['counts']==permit['baseline_counts']
assert b['phase']=='S07_returned_incomplete_activity_limit'
for filename in ('budget.json','events.jsonl','case-index.json'):(N/('before-'+filename)).write_bytes((E/filename).read_bytes())
old=(ROOT/'DocuN/results/TASK-117-result.md').read_bytes()
assert len(old)==88265 and sha(old)=='fc600e1381e44542fc933bdd294e471e2e1a5d4b70b979a5a2be708878993aab'
(N/'before-result.md').write_bytes(old)
anchor=sample();first=datetime.fromisoformat('2026-10-18T01:30:39.4377167Z')
s={'permit':PERMIT,'stage':'S08','status':'active','first_tool_utc':first.isoformat(),
   'first_tool_qpc':806993274664,'first_tool_qpc_frequency':10000000,
   'calendar_deadline_utc':(first+timedelta(hours=48)).isoformat(),'activity_cap_seconds':None,
   'policy':'UTC跨中断差仅上界；日历48小时、真实命令wall3600与运行持有3600分别守门；不追改旧段',
   'clock_anchor':anchor,'last_clock':anchor,'clock_reanchors':[],
   'baseline_counts':b['counts'].copy(),'cumulative_caps':permit['cumulative_caps'],
   'offline_process_run_seconds':0,'offline_process_run_active':None,'holding_start_mono_ns':None,
   'tool_wall_account':'外层工具命令真实wall另记tool-receipts.json；嵌套计费保守保留',
   'observed_work_intervals':[],'unknown_gaps':[],'evidence_directory':str(N)}
b['segments'].append(s);b['active_segment']=PERMIT;b['phase']='S08_control_preparation';write(E/'budget.json',b)
write(N/'receipt.json',{'permit':PERMIT,'first_tool_utc':first.isoformat(),'qpc':806993274664,'frequency':10000000,
   'anchor':anchor,'verified_inputs':verified,'baseline_counts':b['counts'],'Q':'FROZEN',
   'runtime_started':False,'resume_observation':'Get-Process node/chrome/python no rows; TCP18119 no rows at receipt commands; no S07 roots/PIDs registered',
   'old_report_bytes':len(old),'old_report_sha256':sha(old),'actual_model':'Codex desktop / GPT-6；A+资源标签，具体变体未知'})
write(N/'tool-receipts.json',{'command_wall_upper_seconds':10.7,'first_three_batches_upper_seconds':10.7,'receipt_policy':'三次并行调用的工具wall分别1.9/1.2/1.3秒乘命令数3/2/2，保守上界；不是精确CPU','commands':[]})
event('S08_received',verified=len(verified),Q='FROZEN')
print(json.dumps({'verified':len(verified),'permit':PERMIT,'calendar_deadline_utc':s['calendar_deadline_utc']},ensure_ascii=False))
