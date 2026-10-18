"""冻结每批实际被测源码及新文件身份，不把累计 Git 差异算成本卡。"""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys
from budget import ROOT,CONTROL,Budget,EVIDENCE


def freeze(label):
    before=json.loads((EVIDENCE/'pre-manifest.json').read_text(encoding='utf-8'))
    files={ROOT/entry['path'] for entry in before}
    for directory in ('backend/app/data_exit','frontend/src/data','backend/tests/fixtures/task114'):
        files.update(path for path in (ROOT/directory).rglob('*') if path.is_file() and '__pycache__' not in path.parts)
    for pattern in ('backend/tests/test_data_exit*.py','frontend/tests/task114*.mjs'):
        files.update(ROOT.glob(pattern))
    files.update(ROOT/name for name in ('backend/migrations/013_data_exit.sql','deploy/data_restore.py','config/data-exit.example.json'))
    destination=EVIDENCE/'as-run'/label
    destination.mkdir(parents=True)
    manifest=[]
    prior={entry['path']:entry for entry in before}
    for path in sorted(files):
        relative=path.relative_to(ROOT).as_posix();raw=path.read_bytes()
        target=destination/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
        manifest.append({'path':relative,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'before_exists':relative in prior})
    data={'label':label,'utc':datetime.now(timezone.utc).isoformat(),'files':manifest}
    (destination/'manifest.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    Budget().event('as_run',{'label':label,'manifest':str((destination/'manifest.json').relative_to(ROOT))})
    print(json.dumps({'label':label,'files':len(manifest)}))
    return destination


if __name__=='__main__':freeze(sys.argv[1])
