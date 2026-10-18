"""Read-only baseline identity and preimages for the permitted TASK-120 paths."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
baseline = json.loads((OUT.parent / 'orchestration-20261018/product-baseline.json').read_text(encoding='utf-8-sig'))
areas = ('backend/app/capabilities/', 'backend/app/operator/', 'backend/app/activities/',
         'backend/app/retrieval/', 'backend/app/learning/', 'backend/app/interview/',
         'frontend/src/activities/', 'frontend/src/explanations/')
exact = {'backend/app/data_exit/'+x+'.py' for x in ('control','files','maintenance','deletions','operations')}
exact.update({'backend/app/preview/'+x+'.py' for x in ('generation','api','business_contracts','repository')})
exact.update({'backend/app/worker/'+x+'.py' for x in ('one_call','worker_main','command','session','launcher')})
exact.update(('.gitignore','README.md','backend/app/main.py','backend/app/service_config.py',
              'config/activity.example.json','config/integration.example.json','config/data-exit.example.json'))
observations = []
for item in baseline['files']:
    name = item['relative_path'].replace('\\','/')
    path = ROOT / name
    raw = path.read_bytes() if path.is_file() else None
    actual = hashlib.sha256(raw).hexdigest() if raw is not None else None
    row = {'path':name,'sha256':actual,'bytes':len(raw) if raw is not None else None,
           'matches_baseline':actual==item.get('sha256'),'preimage':False}
    if raw is not None and (name in exact or name.startswith(areas)):
        dest=OUT/'preimage'/name
        dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists():
            if dest.read_bytes()!=raw:raise RuntimeError('preimage_already_exists_different')
        else:dest.write_bytes(raw)
        row['preimage']=True
    observations.append(row)
(OUT/'baseline-check.json').write_text(json.dumps({'utc':datetime.now(timezone.utc).isoformat(),
 'files':observations,'mismatches':[x for x in observations if not x['matches_baseline']]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'checked':len(observations),'mismatches':[x['path'] for x in observations if not x['matches_baseline']],
 'preimages':sum(x['preimage'] for x in observations)}))
