from pathlib import Path
import ast, difflib, hashlib, time
root = Path(r'D:\shspic\project_NO3_RetroLume-agent')
ev = root / 'Ndocu/evidence/task-083/focused-repair-03'
paths = [
    'backend/app/worker/launcher.py',
    'backend/app/worker/supervisor_ipc.py',
    'backend/app/worker/supervisor_main.py',
    'backend/app/worker/session.py',
    'backend/tests/fixtures/task083/job_control.py',
    'backend/tests/fixtures/task083/offline_unit.py',
    'backend/tests/fixtures/task083/focused_unit.py',
]
start = time.monotonic()
lines = []
diff = []
for rel in paths:
    path = root / rel
    data = path.read_bytes()
    ast.parse(data.decode('utf-8-sig'), filename=str(path))
    sha = hashlib.sha256(data).hexdigest()
    lines.append(f'{rel} {sha}')
    old_path = ev / 'pre' / rel.replace('/', '__')
    old = old_path.read_bytes() if old_path.exists() else b''
    lines.append(f'  old_sha256={hashlib.sha256(old).hexdigest() if old_path.exists() else "NEW"}')
    diff.extend(difflib.unified_diff(old.decode('utf-8-sig').splitlines(keepends=True),
        data.decode('utf-8-sig').splitlines(keepends=True),
        fromfile='a/'+rel, tofile='b/'+rel))
for rel, expected in [
    ('backend/app/activities/repository.py', '929320baf55d625e897324aa76ebe543bda86e73a4bf1c4766c7e552721c5b20'),
    ('backend/migrations/005_activities_dispatch_closed.sql', '26b71a836355fa9620401f6bbb76e9a42668a1ce52077aa91ecb2f61ebeb50eb'),
]:
    actual = hashlib.sha256((root/rel).read_bytes()).hexdigest()
    if actual != expected: raise AssertionError(f'FROZEN_DRIFT {rel} {actual}')
    lines.append(f'FROZEN_OK {rel} {actual}')
(ev/'incremental.diff').write_text(''.join(diff), encoding='utf-8')
(ev/'final-hashes.txt').write_text('\n'.join(lines)+'\n', encoding='utf-8')
print(f'AST_OK {len(paths)} paths; FROZEN_OK repository,005; elapsed_seconds={time.monotonic()-start:.6f}')
print('\n'.join(lines))
