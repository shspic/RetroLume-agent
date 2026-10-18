"""从S07初版保存本段preimage链与原bundle，不修改产品。"""
import json
from control import N,E,ROOT,pre,sha,write
old=json.loads((E/'continuation-06/changes.json').read_text(encoding='utf-8'))
for path,row in old.items():pre(path,row['D'])
for path,defect in [('frontend/tests/step018-s08.mjs','D03,D04'),('backend/tests/test_step018_embedding_contracts.py','D02'),('config/integration.example.json','D02'),('frontend/src/activities/teachingDrafts.ts','D03')]:pre(path,defect)
rows=[]
for path in (ROOT/'frontend/dist').rglob('*'):
    if path.is_file():
        relative=path.relative_to(ROOT/'frontend/dist');target=N/'bundle-7-before'/relative;target.parent.mkdir(parents=True,exist_ok=True);raw=path.read_bytes();target.write_bytes(raw)
        rows.append({'path':str(path.relative_to(ROOT)),'backup':str(target),'bytes':len(raw),'sha256':sha(raw)})
write(N/'bundle-7-before.json',{'files':rows})
print('已保存S08 preimage与bundle7',len(rows))
