"""重建首次可得preimage到当前文件的只读差异，不执行产品。"""
import ast
import datetime as dt
import difflib
import hashlib
import json
from pathlib import Path
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
start = time.perf_counter()
root = Path('D:/shspic/project_NO3_RetroLume-agent')
out = root / 'DocuN/evidence/TASK-118/audit'
exe = root / 'DocuN/evidence/TASK-117/execution'
rounds = [exe] + [exe / f'continuation-{n:02}' for n in range(1, 6)]
first = {}
history = {}
checks = []
for folder in rounds:
    path = folder / 'changes.json'
    data = json.loads(path.read_text(encoding='utf-8-sig'))
    for rel, record in data.items():
        first.setdefault(rel, (folder.name, record))
        history.setdefault(rel, []).append(folder.name)
        if record.get('exists') and record.get('backup'):
            p = root / record['backup']
            b = p.read_bytes() if p.is_file() else None
            checks.append({'path': str(p), 'expected': record.get('sha256'), 'actual': None if b is None else hashlib.sha256(b).hexdigest(), 'match': b is not None and hashlib.sha256(b).hexdigest() == record.get('sha256')})
manifest = json.loads((exe / 'continuation-05/final-source-manifest.json').read_text(encoding='utf-8-sig'))
for entry in manifest['entries']:
    first.setdefault(entry['path'], ('manifest-only', {'exists': None}))
inventory = []
diffdir = out / 'diffs'
diffdir.mkdir(exist_ok=True)
for rel, (roundname, pre) in sorted(first.items()):
    if not rel.startswith(('backend/app/', 'backend/migrations/', 'backend/tests/', 'frontend/', 'deploy/', 'config/')) and rel != 'README.md':
        continue
    current = root / rel
    b = current.read_bytes() if current.is_file() else b''
    oldpath = root / pre['backup'] if pre.get('backup') else None
    before = oldpath.read_bytes() if oldpath and oldpath.is_file() else b''
    item = {'path': rel, 'first_round': roundname, 'pre_exists': pre.get('exists'), 'pre_sha256': pre.get('sha256'), 'post_exists': current.is_file(), 'post_sha256': hashlib.sha256(b).hexdigest() if current.is_file() else None, 'rounds': history.get(rel, []), 'preimage': str(oldpath) if oldpath else None, 'lines': b.count(b'\n')}
    if before != b and current.suffix in ('.py', '.sql', '.ts', '.tsx', '.json', '.md', '.ps1', '.yml', '.mjs', '.html', '.css') and not rel.startswith('frontend/dist/'):
        diff = ''.join(difflib.unified_diff(before.decode('utf-8-sig').splitlines(True), b.decode('utf-8-sig').splitlines(True), fromfile='first-pre/' + rel, tofile='current/' + rel, n=3))
        dest = diffdir / (rel.replace('/', '__') + '.diff')
        dest.write_text(diff, encoding='utf-8')
        item['diff'] = str(dest)
        item['added'] = sum(line.startswith('+') and not line.startswith('+++') for line in diff.splitlines())
        item['removed'] = sum(line.startswith('-') and not line.startswith('---') for line in diff.splitlines())
    if current.suffix == '.py' and current.is_file():
        try:
            tree = ast.parse(b.decode('utf-8-sig'))
            item['definitions'] = [{'name': n.name, 'line': n.lineno, 'end': n.end_lineno} for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
        except SyntaxError as exc:
            item['ast_error'] = str(exc)
    inventory.append(item)
result = {'at': dt.datetime.now(dt.timezone.utc).isoformat(), 'backup_checks': checks, 'backup_mismatches': [x for x in checks if not x['match']], 'inventory': inventory, 'elapsed_seconds': time.perf_counter() - start}
(out / 'delta-inventory.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
for item in inventory:
    print(f"{item['path']} first={item['first_round']} pre={item['pre_exists']} lines={item['lines']} +{item.get('added',0)} -{item.get('removed',0)}")
print('backup_checks=' + str(len(checks)) + ' mismatches=' + str(len(result['backup_mismatches'])) + ' seconds=' + str(result['elapsed_seconds']))
