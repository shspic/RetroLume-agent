"""Filesystem-only frozen55 readiness; no business execution."""
import ast,json,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
reg=json.loads((HERE/'change-registry.json').read_text(encoding='utf-8'));rows=[]
for row in reg['paths']:
    p=ROOT/row['path']
    if not p.is_file():continue
    if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8-sig'))
    rows.append({'path':row['path'],'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
b=json.loads((HERE.parent/'budget.json').read_text(encoding='utf-8'))
assert b['active_root'] is None and b['counts']['roots']==54
assert all(x['objects']==1 and x['create_attempts']==1 for x in b['audit_repair07_logical_databases'].values())
for name in ('F01-missing-insert','F01-missing-update','F01-select-only','F01-normal-R03-install','F02-direct-inherit-snapshot','F02-indirect-inherit-snapshot','F02-set-only-indirect-snapshot','F02-admin-without-inherit-or-set','F02-legal-harmless-membership','F02-normal-snapshot-read-and-write-denial'):
    assert json.loads((HERE/(name+'-PASS.json')).read_text(encoding='utf-8'))['status']=='PASS'
(HERE/'frozen-next-batch-identities.json').write_text(json.dumps({'status':'PASS','files':rows,'F01_F02_checkpoints':'retained, not repeated','front_end_product_changed':False,'new_synthetic_admission_limit':16,'delete_manifest_cap':16},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'PASS','syntax_files':len(rows),'counts_before':b['counts'],'budget_logical_databases':b['audit_repair07_logical_databases']}))
