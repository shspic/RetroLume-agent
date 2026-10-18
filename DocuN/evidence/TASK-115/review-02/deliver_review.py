"""Deliver only the new TASK115 prefix and metadata. Never modify old bytes."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import re
import stat
import time

ROOT=Path('D:/shspic/project_NO3_RetroLume-agent')
OUT=ROOT/'DocuN/evidence/TASK-115/review-02'
RESULT=ROOT/'DocuN/results/TASK-115-result.md'
OLD_BYTES=61253
OLD_HASH='3d6a4ce4e30284f6799f61462e84c419a9fdd7226ef1f1e73dc468815b04a0f2'
OLD_ACTIVE=8617.261566
START=dt.datetime.fromisoformat('2026-10-14T01:15:19+00:00')
LIMIT=5400
DEADLINE=dt.datetime.fromisoformat('2026-10-15T06:16:24.914938+00:00')

def sample():return {'utc':dt.datetime.now(dt.timezone.utc).isoformat(),'mono_ns':time.monotonic_ns()}
def seconds(s):return (dt.datetime.fromisoformat(s['utc'])-START).total_seconds()
def safe(p):
    p=Path(str(p).replace('\\\\','/').replace('\\','/'))
    for part in [p,*p.parents]:
        if part.exists() and getattr(part.lstat(),'st_file_attributes',0)&stat.FILE_ATTRIBUTE_REPARSE_POINT:raise RuntimeError('reparse refused '+str(part))
    return p
def identity(p):
    p=safe(p);row={'path':str(p),'exists':p.is_file()}
    if row['exists']:
        b=p.read_bytes();row.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
    return row
def write_json(name,value):(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

begin=sample()
assert seconds(begin)<LIMIT-300 and dt.datetime.fromisoformat(begin['utc'])<DEADLINE
old=safe(OUT/'prior-result.md').read_bytes()
assert len(old)==OLD_BYTES and hashlib.sha256(old).hexdigest()==OLD_HASH
assert safe(RESULT).read_bytes()==old
protected=json.loads((OUT/'protected-before.json').read_text(encoding='utf-8'))
mismatches=[]
for expected in protected:
    actual=identity(expected['path'])
    if actual!=expected:mismatches.append({'expected':expected,'actual':actual})
write_json('protected-final-check.json',{'observed':sample(),'checked':len(protected),'mismatches':mismatches})
assert not mismatches

prefix=(OUT/'review-prefix.md').read_text(encoding='utf-8')
observed=sample()
elapsed=seconds(observed)
assert elapsed<LIMIT and dt.datetime.fromisoformat(observed['utc'])<DEADLINE
activity=f"UTC {observed['utc']}，本轮从保守起点连续计{elapsed:.6f}秒，旧累计加回为{OLD_ACTIVE+elapsed:.6f}秒/21600"
assert prefix.count('{{ACTIVITY_OBSERVATION}}')==1
prefix=prefix.replace('{{ACTIVITY_OBSERVATION}}',activity)
assert '\ufffd' not in prefix
(OUT/'review-prefix-rendered.md').write_text(prefix,encoding='utf-8')
content=prefix.encode('utf-8')+old
safe(RESULT).write_bytes(content)
readback=safe(RESULT).read_bytes()
assert readback==content
assert readback[-OLD_BYTES:]==old
assert hashlib.sha256(readback[-OLD_BYTES:]).hexdigest()==OLD_HASH
assert readback.decode('utf-8')

# delivery.json is the one planned evidence link; write it before link/readback QA.
provisional={'status':'report_saved_qa_in_progress','sample':sample(),'report':str(RESULT),'sha256':hashlib.sha256(readback).hexdigest()}
write_json('delivery.json',provisional)
broken=[]
for target in re.findall(r'\]\(([^)]+)\)',prefix):
    path=re.sub(r':\d+$','',target.strip('<>'))
    if re.match(r'^[A-Za-z]:/',path) and not safe(path).exists():broken.append(target)
assert not broken
post_mismatches=[]
for expected in protected:
    if safe(expected['path'])==RESULT:continue
    actual=identity(expected['path'])
    if actual!=expected:post_mismatches.append({'expected':expected,'actual':actual})
assert not post_mismatches
end=sample()
conservative_seconds=seconds(end)+2
assert conservative_seconds<LIMIT and dt.datetime.fromisoformat(end['utc'])<DEADLINE
delivery={
    'task':'TASK-115/R-109/review-02/STEP017',
    'permit':'TASK-115-STEP017-REVIEW02-20261014',
    'status':'delivered_independent_incremental_review',
    'result':str(RESULT),'bytes':len(readback),'sha256':hashlib.sha256(readback).hexdigest(),
    'prefix_bytes':len(prefix.encode('utf-8')),
    'prior_suffix_bytes':OLD_BYTES,'prior_suffix_sha256':OLD_HASH,'prior_suffix_exact':True,
    'save_begin':begin,'report_readback_and_protected_check_end':end,
    'conservative_start_utc':START.isoformat(),'first_tool_mono_missing':True,'first_tool_missing_point_deduction_seconds':300,
    'actual_end_observation_elapsed_seconds':seconds(end),
    'final_metadata_save_readback_reserve_seconds':2,
    'review_activity_seconds_conservative':conservative_seconds,
    'old_active_cumulative_seconds':OLD_ACTIVE,
    'active_cumulative_seconds_conservative':OLD_ACTIVE+conservative_seconds,
    'review_activity_limit_seconds':LIMIT,'original_activity_limit_seconds':21600,
    'calendar_deadline_utc':DEADLINE.isoformat(),
    'new_business_usage':{k:0 for k in ['real_roots','PG','SQL','Docker','API','Vite','Browser','compile','tests','build','Native','preview','provider','fees','public_network']},
    'old_usage_retained':{'roots':3,'API':3,'Browser':2,'offline_seconds':125.610,'holding_seconds_conservative':14.874},
    'protected_checks':len(protected),'protected_before_write_mismatches':mismatches,'protected_after_write_mismatches':post_mismatches,
    'new_prefix_broken_local_links':broken,'complete_UTF8_readback':True,
    'recommendations':{'DEF035_F02':'具备关闭条件','DEF036_F03':'具备关闭条件','finite_STEP017':'建议主控据既有有效主链和两项关闭裁定关闭'},
    'no_master_status_edited':True,
    'scope':'zero new business run; no new physical PG/selector or broader acceptance',
}
write_json('delivery.json',delivery)
assert json.loads((OUT/'delivery.json').read_text(encoding='utf-8'))==delivery
assert safe(RESULT).read_bytes()==readback
assert seconds(sample())<=conservative_seconds
print(json.dumps(delivery,ensure_ascii=True,indent=2))
