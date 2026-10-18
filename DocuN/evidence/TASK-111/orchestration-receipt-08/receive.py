"""回收TASK112审计并核历史PG段原件，只有文件/hash和精确metadata读取。"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
from decimal import Decimal
import hashlib,json,subprocess,shutil,re
ROOT=Path('D:/shspic/project_NO3_RetroLume-agent')
OUT=Path(__file__).resolve().parent
AUDIT=ROOT/'DocuN/evidence/TASK-112/audit-20261011'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def info(p):
    b=p.read_bytes();return dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
at=datetime.now(timezone(timedelta(hours=8))).isoformat()
delivery=load(AUDIT/'delivery-receipt.json')
assert info(ROOT/'DocuN/results/TASK-112-result.md')==dict(bytes=delivery['report']['bytes'],sha256=delivery['report']['sha256'])
frozen=load(ROOT/'DocuN/evidence/TASK-112/orchestration-20261011/frozen-inputs.json')
for r in frozen['sources']:assert info(Path(r['path']))==dict(bytes=r['bytes'],sha256=r['sha256']),r['path']
for r in frozen['rule_sources']:assert info(Path(r['path']))['sha256']==r['sha256']
end=load(AUDIT/'frozen-identity-end.json');assert len(end)==225 and all(r['match'] for r in end)
b=load(ROOT/'DocuN/evidence/TASK-111/execution/budget.json');assert b['active_batch'] is None
execution=load(AUDIT/'execution-budget-independent.json');assert b['counts']==execution['counts_from_budget']==execution['counts_from_original_events']
gap=execution['unaccounted_root6_PG_segment']
raw_before=load(Path(gap['source_before']));raw_stop=load(Path(gap['source_stop']))
# 原件不含业务执行；stdout只解析必要状态/ID，不输出Env或凭据。
before_out=json.loads((Path(gap['source_before']).parent/'pg-before.stdout.bin').read_bytes())
objects=before_out if isinstance(before_out,list) else [before_out]
target=next(r for r in objects if (r.get('Id') or r.get('id'))==gap['CID'])
state=target.get('State',target.get('state',target))
running=state.get('Running',state.get('running'));pid=state.get('Pid',state.get('pid'))
assert running is True and pid==945
assert raw_stop.get('returncode',raw_stop.get('exit_code',raw_stop.get('code')))==0
hold=Decimal(gap['stop_end_ns']-gap['root_end_ns'])/Decimal(10**9)
assert hold==Decimal('2279.703')
recorded=Decimal(str(execution['reproduced_recorded_real']))
total=recorded+hold;assert total==Decimal('16826.566')
save('PG-hold-disposition.json',dict(at=at,issue='E112-01',basis='保守完整持有至精确stop确认；物理停机瞬时未采，非精确连续观测',
    CID=gap['CID'],root6_end_ns=gap['root_end_ns'],PG_running_before_cleanup=True,PG_pid_before_cleanup=945,stop_confirmation_ns=gap['stop_end_ns'],
    raw_files=[dict(path=gap['source_before'],**info(Path(gap['source_before']))),dict(path=gap['source_stop'],**info(Path(gap['source_stop'])))],
    recorded_real_seconds=str(recorded),missing_hold_seconds=str(hold),conservative_real_seconds=str(total),historical_cap_seconds='16200',historical_excess_seconds=str(total-Decimal('16200')),
    not_retroactively_authorized=True,do_not_reset_counters=True,budget_file_not_modified=True,adjustment_to_be_appended_once_by_engineering=True))
def_numbers=[int(x) for x in re.findall(r'DEF-0*(\d+)',(ROOT/'DocuS/执行动态文档.MD').read_text(encoding='utf-8'))]
save('received.json',dict(at=at,audit_delivery=delivery,audit_report_current=info(ROOT/'DocuN/results/TASK-112-result.md'),frozen_sources=105,rules=7,auditor_frozen_checks=225,
    code='不通过',evidence='现成方法限定成立，缺陷修正证据待补',execution='历史偏差及E112-01单列保守核销',
    F112_01='P1迟到ready成功分支未复核',F112_03='P1stderr线程退出被误充EOF',F112_02='P2constraints null和BOM原字节域差异',
    current_counts=b['counts'],current_time_seconds=b['time_seconds'],current_real_caps=b['continuation_caps'],max_existing_DEF=max(def_numbers),business_operations=0))
actual=[]
for r in load(ROOT/'DocuN/evidence/TASK-111/execution/continuation-06/final/exact-resources-final.json')['objects']:
    cid=r.get('id') or r.get('cid');p=subprocess.run([shutil.which('docker'),'container','inspect',cid],capture_output=True,timeout=10,creationflags=subprocess.CREATE_NO_WINDOW)
    assert p.returncode==0,'精确metadata不可读'
    v=json.loads(p.stdout)[0];assert v['Id']==cid and v['Image']==r['image'] and not v['State']['Running'] and v['State']['Pid']==0 and v['RestartCount']==0
    actual.append(dict(id=v['Id'],name=v['Name'],image=v['Image'],running=False,pid=0,restart_count=0))
save('resource-recheck.json',dict(at=at,objects=actual,read_only=True,only_registered=True,not_new_runtime_or_old_UNKNOWN_proof=True))
print(json.dumps(dict(audit_report_match=True,source_match=105,rules_match=7,auditor_frozen_match=225,root6_gap_seconds=str(hold),conservative_real_seconds=str(total),historical_excess_seconds=str(total-Decimal('16200')),resources_stopped=len(actual),max_existing_DEF=max(def_numbers)),ensure_ascii=False))
