"""核增量终审交付与当前候选身份/账/精确停止metadata；不执行产品。"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,subprocess,shutil
ROOT=Path('D:/shspic/project_NO3_RetroLume-agent')
OUT=Path(__file__).resolve().parent
REVIEW=ROOT/'DocuN/evidence/TASK-112/review-01-20261012'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def info(p):
    b=p.read_bytes();return dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
at=datetime.now(timezone(timedelta(hours=8))).isoformat()
receipt=load(REVIEW/'delivery-receipt.json');p=ROOT/'DocuN/results/TASK-112-result.md'
assert info(p)==dict(bytes=receipt['report']['bytes'],sha256=receipt['report']['sha256'])
old=p.read_bytes()[-receipt['original_report']['bytes']:]
assert hashlib.sha256(old).hexdigest()==receipt['original_report']['sha256']=='ea51e0f49f556fd6f07aea11741d26099a534550850c0c68dfa49a9ab4c3b522'
assert all(receipt['conclusion'][k]=='关闭' for k in ('DEF_031','DEF_032','DEF_033')) and receipt['business_operations']==0
end=load(REVIEW/'frozen-end.json');assert len(end)==379 and all(r['match'] for r in end)
checked=[]
for r in receipt['checked_evidence']:
    assert info(Path(r['path']))==dict(bytes=r['bytes'],sha256=r['sha256']);checked.append(r)
sources=load(ROOT/'DocuN/evidence/TASK-111/execution/continuation-07/final/source-identity.json')
for r in sources:assert info(ROOT/r['path'])==dict(bytes=r['bytes'],sha256=r['sha256'])
rules=[]
for r in load(ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json'):
    assert info(Path(r['absolute_path']))['sha256']==r['sha256'];rules.append(dict(path=r['absolute_path'],sha256=r['sha256']))
b=load(ROOT/'DocuN/evidence/TASK-111/execution/budget.json');assert b['active_batch'] is None
save('received.json',dict(at=at,audit_receipt=receipt,sources=sources,rules=rules,review_end_objects=379,review_checked_evidence=checked,old_audit_suffix_preserved=True,
    engineering_report=info(ROOT/'DocuN/results/TASK-111-result.md'),current_counts=b['counts'],current_time_seconds=b['time_seconds'],budget_identity=info(ROOT/'DocuN/evidence/TASK-111/execution/budget.json'),main_business_operations=0))
objects=[]
for r in load(ROOT/'DocuN/evidence/TASK-111/execution/continuation-07/final/exact-resources-final.json')['objects']:
    cid=r.get('id') or r.get('cid');q=subprocess.run([shutil.which('docker'),'container','inspect',cid],capture_output=True,timeout=10,creationflags=subprocess.CREATE_NO_WINDOW)
    assert q.returncode==0,'精确metadata不可读'
    v=json.loads(q.stdout)[0];assert v['Id']==cid and v['Image']==r['image'] and not v['State']['Running'] and v['State']['Pid']==0 and v['RestartCount']==0
    objects.append(dict(id=cid,name=v['Name'],image=v['Image'],running=False,pid=0,restart_count=0))
save('resource-recheck.json',dict(at=at,objects=objects,read_only=True,only_registered=True,not_old_UNKNOWN_full_proof=True))
print(json.dumps(dict(audit_report_match=True,old_suffix_preserved=True,review_end_objects=379,checked_evidence=len(checked),source_match=len(sources),rules_match=len(rules),resources_stopped=len(objects),DEF_close_candidates=['031','032','033'],active_batch=None),ensure_ascii=False))
