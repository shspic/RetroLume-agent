"""核设计交付及实际源身份；只读文件，无产品运行。"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
ROOT=Path('D:/shspic/project_NO3_RetroLume-agent')
OUT=Path(__file__).resolve().parent
D=ROOT/'DocuN/evidence/TASK-113/design'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def info(p):
    b=p.read_bytes();return dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
at=datetime.now(timezone(timedelta(hours=8))).isoformat();delivery=load(D/'delivery.json')
report=ROOT/'DocuN/results/TASK-113-result.md';assert info(report)==dict(bytes=delivery['bytes'],sha256=delivery['sha256'])
identity=load(D/'input-identity.json');rows=identity['files']
for r in rows:assert info(Path(r['path']))==dict(bytes=r['bytes'],sha256=r['sha256'])
extra=load(D/'additional-source-identity.json')
for r in extra:assert info(Path(r['path']))==dict(bytes=r['bytes'],sha256=r['sha256'])
rules=[]
for r in load(ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json'):
    assert info(Path(r['absolute_path']))['sha256']==r['sha256'];rules.append(dict(path=r['absolute_path'],sha256=r['sha256']))
evidence=load(D/'evidence-manifest.json')['entries']
for r in evidence:assert info(Path(r['path']))==dict(bytes=r['bytes'],sha256=r['sha256'])
review_basis=[]
for p in ['backend/app/storage/originals.py','backend/app/materials/api.py','backend/app/materials/repository.py','backend/app/main.py','backend/migrations/010_learning_memory.sql']:
    review_basis.append(dict(path=str(ROOT/p),**info(ROOT/p)))
save('received.json',dict(at=at,delivery=delivery,input_count=len(rows),inputs=rows,additional_sources=extra,rules=rules,evidence_count=len(evidence),evidence_byte_matches=True,review_basis=review_basis,main_product_runs=0))
print(json.dumps(dict(report_match=True,inputs=len(rows),extra_sources=len(extra),rules=len(rules),evidence=len(evidence),current_source_unchanged=True),ensure_ascii=False))
