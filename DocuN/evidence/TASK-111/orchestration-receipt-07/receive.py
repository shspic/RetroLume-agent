"""回收现成C06候选与五方法原件，核身份和精确停止metadata；不运行产品。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib, json, subprocess, shutil

ROOT=Path('D:/shspic/project_NO3_RetroLume-agent')
OUT=Path(__file__).resolve().parent
C06=ROOT/'DocuN/evidence/TASK-111/execution/continuation-06'

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def info(p):
    b=p.read_bytes()
    return dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

at=datetime.now(timezone(timedelta(hours=8))).isoformat()
delivery=load(C06/'final/result-delivery-receipt.json')
report=ROOT/'DocuN/results/TASK-111-result.md'
assert info(report)==dict(bytes=delivery['result_bytes'],sha256=delivery['result_sha256'])
old=report.read_bytes()[-delivery['old_suffix_bytes']:]
prior=load(ROOT/'DocuN/evidence/TASK-111/orchestration-receipt-06/received.json')['result']
assert len(old)==prior['result_bytes']==delivery['old_suffix_bytes']
assert hashlib.sha256(old).hexdigest()==prior['result_sha256']==delivery['old_suffix_sha256']
sources=load(C06/'final/source-identity.json')
for r in sources:assert info(ROOT/r['path'])==dict(bytes=r['bytes'],sha256=r['sha256']),r['path']
rules=[]
for r in load(ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json'):
    actual=info(Path(r['absolute_path']))
    assert actual['sha256']==r['sha256']
    rules.append(dict(path=r['absolute_path'],sha256=actual['sha256']))
receipt=load(C06/'final/execution-receipt.json')
budget=load(ROOT/'DocuN/evidence/TASK-111/execution/budget.json')
assert budget['active_batch'] is None and budget['counts']==receipt['counts'] and budget['time_seconds']==receipt['time_seconds']
originals=load(C06/'final/runtime-originals-index.json')
for r in originals:
    assert info(Path(r['evidence_copy']))==dict(bytes=r['bytes'],sha256=r['sha256'])
    assert info(Path(r['runtime_source']))==info(Path(r['evidence_copy']))
five=load(C06/'final/five-methods-final.json')
methods=[]
for name,r in five['client'].items():
    p=Path(r['path']);actual=load(p)
    assert actual==r['row']
    methods.append(dict(method=name,path=str(p),**info(p),status=actual.get('status'),keys=list(actual.keys())))
stops=five['stops']
stop_rows=stops if isinstance(stops,list) else list(stops.values())
for r in stop_rows:
    if isinstance(r,dict) and 'path' in r:
        p=Path(r['path']);actual=load(p)
        if 'row' in r:assert actual==r['row']
        methods.append(dict(method=actual.get('scenario',r.get('method')),path=str(p),**info(p),status=actual.get('status'),keys=list(actual.keys())))
refresh=load(C06/'final/active-refresh-complete-HTTP.json')
all_http=refresh['all_routes_http']
rows=all_http if isinstance(all_http,list) else all_http.get('rows',all_http.get('requests',[]))
http_methods=[r.get('method') or r.get('data',{}).get('detail',{}).get('method') for r in rows]
assert rows and all(method=='GET' for method in http_methods)
assert refresh['same_deadline'] and refresh['same_starts'] and refresh['owner_after_reload'] is None
save('received.json',dict(at=at,result=delivery,source_count=len(sources),sources=sources,rules=rules,old_report_suffix_preserved=True,runtime_originals_count=len(originals),runtime_original_bytes_verified=True,counts=receipt['counts'],time_seconds=receipt['time_seconds'],methods=methods,refresh_checks=dict(actual_GET_count=len(rows),owner_none=True,deadline_and_starts_unchanged=True),as_run=load(C06/'final/as-run-bindings.json'),main_product_executions=0))
actual_objects=[]
for r in load(C06/'final/exact-resources-final.json')['objects']:
    cid=r.get('id') or r.get('cid')
    p=subprocess.run([shutil.which('docker'),'container','inspect',cid],capture_output=True,timeout=10,creationflags=subprocess.CREATE_NO_WINDOW)
    assert p.returncode==0,'精确资源metadata不可读'
    item=json.loads(p.stdout)[0];s=item['State']
    assert item['Id']==cid and item['Image']==r['image'] and item['Name']==r['name']
    assert not s['Running'] and s['Pid']==0 and item['RestartCount']==0
    actual_objects.append(dict(id=cid,name=item['Name'],image=item['Image'],running=False,pid=0,restart_count=0))
save('resource-recheck.json',dict(at=at,objects=actual_objects,only_registered=True,read_only=True,not_full_stop_proof_for_old_UNKNOWN=True))
print(json.dumps(dict(result_match=True,source_count=len(sources),rules_count=len(rules),runtime_originals_verified=len(originals),GETs=len(rows),method_links=methods,resources_stopped=len(actual_objects),active_batch=None),ensure_ascii=False))
