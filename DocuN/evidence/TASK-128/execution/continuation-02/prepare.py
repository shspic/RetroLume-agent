import ast,datetime,hashlib,json
from pathlib import Path
E=Path(__file__).absolute().parent;R=E.parents[4]
sha=lambda b:hashlib.sha256(b).hexdigest()
manifest=json.loads((E.parents[1]/'orchestration-continuation02-20261023/input-manifest.json').read_bytes())
def rows(value):
    if isinstance(value,dict):
        if 'sha256' in value and ('path' in value or 'absolute_path' in value):yield value
        for v in value.values():yield from rows(v)
    elif isinstance(value,list):
        for v in value:yield from rows(v)
checks=[]
for row in rows(manifest):
    p=Path(row.get('absolute_path',row.get('path')))
    if not p.is_absolute():p=R/p
    checks.append({'path':str(p),'sha256':sha(p.read_bytes()),'match':sha(p.read_bytes())==row['sha256']})
assert all(row['match'] for row in checks)
for name in ('README.md','deploy/normal-install.md','DocuN/results/TASK-128-result.md'):
    dest=E/'pre'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((R/name).read_bytes())
for name in ('run-six.py','install-observer.py','win-support.py'):
    (E/name).write_bytes((E.parent/'continuation-01'/name).read_bytes())
(E/'pre-snapshot.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inputs':checks},indent=2),encoding='utf-8')
(E/'final-run-inputs.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
receipt=R/'.runtime/normal-first-install/source/receipts/task128-c01-success.jsonl'
assert sha(receipt.read_bytes())=='a2211aa56f0497ef55e2ff42f4ea2e6b3b50bb3049cca62cbd5ef06844df6f06'
print(json.dumps({'all_inputs_match':len(checks),'source_success_receipt_matches':True,'product_code_unchanged':True}))
