"""只核C07交回文件、一次账调整和精确资源metadata，不运行产品。"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
from decimal import Decimal
import hashlib,json,subprocess,shutil
ROOT=Path('D:/shspic/project_NO3_RetroLume-agent')
OUT=Path(__file__).resolve().parent
C07=ROOT/'DocuN/evidence/TASK-111/execution/continuation-07'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def info(p):
    b=p.read_bytes();return dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
at=datetime.now(timezone(timedelta(hours=8))).isoformat()
receipt=load(C07/'delivery/result-delivery-proof.json')
report=ROOT/'DocuN/results/TASK-111-result.md';assert info(report)==dict(bytes=receipt['bytes'],sha256=receipt['sha256'])
suffix=report.read_bytes()[-receipt['original_suffix_bytes']:]
assert hashlib.sha256(suffix).hexdigest()==receipt['original_suffix_sha256']=='fcee65ac816c59e364f26c23d0feaec023b28a97b170e78785d16af19d4be5f4'
sources=load(C07/'final/source-identity.json')
for r in sources:assert info(ROOT/r['path'])==dict(bytes=r['bytes'],sha256=r['sha256']),r['path']
rules=[]
for r in load(ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json'):
    assert info(Path(r['absolute_path']))['sha256']==r['sha256'];rules.append(dict(path=r['absolute_path'],sha256=r['sha256']))
manifest=load(C07/'final/evidence-manifest.json')['entries']
for r in manifest:assert info(Path(r['path']))==dict(bytes=r['bytes'],sha256=r['sha256']),r['path']
budget=load(ROOT/'DocuN/evidence/TASK-111/execution/budget.json');assert budget['active_batch'] is None
events=[json.loads(x) for x in (ROOT/'DocuN/evidence/TASK-111/execution/events.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
adjustment=load(C07/'E112-01-adjustment.json')
adjust_events=[e for e in events if e.get('data',{}).get('adjustment',{}).get('issue')=='E112-01' and ('adjust' in e.get('kind',''))]
assert len(adjust_events)==1
assert adjust_events[0]['data']['adjustment']==adjustment
stored_adjustments=budget['execution_time_adjustments']
stored=list(stored_adjustments.values()) if isinstance(stored_adjustments,dict) else stored_adjustments
assert len([x for x in stored if isinstance(x,dict) and x.get('issue')=='E112-01'])==1
assert Decimal(str(adjustment['added_real_seconds']))==Decimal('2279.703') and Decimal(str(adjustment['real_seconds_after']))==Decimal('16826.566')
cases=load(C07/'final/case-index.json')['selected'];assert len(cases)==6 and all(r['status'].startswith('PASS_') and r['exit']==0 for r in cases)
for r in cases:assert load(Path(r['folder'])/'scenario-result.json')==r
stops=load(C07/'final/stop-index.json');assert len(stops)==7 and all(r['state']=='stopped' for r in stops)
changes=load(C07/'final/change-index.json')['changes'];assert len(changes)==5
save('received.json',dict(at=at,result=receipt,source_count=len(sources),sources=sources,rules=rules,evidence_count=len(manifest),evidence_byte_matches=True,old_suffix_preserved=True,
    selected_cases=cases,new_stop_count=len(stops),counts=budget['counts'],time_seconds=budget['time_seconds'],adjustment_events=len(adjust_events),E112_01=adjustment,changes=changes,
    audit112_report_unchanged=info(ROOT/'DocuN/results/TASK-112-result.md'),main_business_runs=0))
objects=[]
for r in load(C07/'final/exact-resources-final.json')['objects']:
    cid=r.get('id') or r.get('cid');p=subprocess.run([shutil.which('docker'),'container','inspect',cid],capture_output=True,timeout=10,creationflags=subprocess.CREATE_NO_WINDOW)
    assert p.returncode==0,'精确metadata不可读'
    v=json.loads(p.stdout)[0];assert v['Id']==cid and v['Image']==r['image'] and not v['State']['Running'] and v['State']['Pid']==0 and v['RestartCount']==0
    objects.append(dict(id=cid,name=v['Name'],image=v['Image'],running=False,pid=0,restart_count=0))
save('resource-recheck.json',dict(at=at,objects=objects,read_only=True,only_registered=True,not_full_stop_proof_for_old_UNKNOWN=True))
print(json.dumps(dict(result_match=True,sources=len(sources),rules=len(rules),evidence_files=len(manifest),selected_cases=len(cases),new_stopped_rows=len(stops),E112_01_events=len(adjust_events),resources_stopped=len(objects),active_batch=None),ensure_ascii=False))
