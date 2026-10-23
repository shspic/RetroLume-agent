import ast,datetime,hashlib,json
from pathlib import Path
E=Path(__file__).absolute().parent;R=E.parents[4]
sha=lambda b:hashlib.sha256(b).hexdigest()
m=json.loads((E.parents[1]/'orchestration-continuation01-20261023/input-manifest.json').read_bytes())
def rows(x):
    if isinstance(x,dict):
        if 'sha256' in x and ('path' in x or 'absolute_path' in x):yield x
        for v in x.values():yield from rows(v)
    elif isinstance(x,list):
        for v in x:yield from rows(v)
checks=[]
for row in rows(m):
    p=Path(row.get('absolute_path',row.get('path')))
    if not p.is_absolute():p=R/p
    assert p.is_file(),str(p)
    checks.append({'path':str(p),'sha256':sha(p.read_bytes()),'match':sha(p.read_bytes())==row['sha256']})
assert all(row['match'] for row in checks)
for name in ('deploy/initialize_normal.py','backend/tests/test_normal_install.py','README.md','deploy/normal-install.md','DocuN/results/TASK-128-result.md'):
    target=E/'pre'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((R/name).read_bytes())
(E/'pre-snapshot.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inputs':checks},indent=2),encoding='utf-8')
for name in ('run-six.py','install-observer.py','win-support.py'):
    source=E.parent/name
    s=source.read_text(encoding='utf-8').replace('.parents[4]','.parents[5]')
    (E/name).write_text(s,encoding='utf-8')
print(json.dumps({'pre_inputs':len(checks),'match':True}))
