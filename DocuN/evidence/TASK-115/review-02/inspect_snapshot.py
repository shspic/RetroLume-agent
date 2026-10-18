"""TASK115 review-02: standard-library file/JSON/AST metadata only.

No product import, compilation, execution, network, process inventory or DB call.
All output is restricted to this review evidence directory.
"""
from pathlib import Path
import ast
import datetime as dt
import difflib
import hashlib
import json
import stat
import time

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
OUT = ROOT / 'DocuN/evidence/TASK-115/review-02'
C03 = ROOT / 'DocuN/evidence/TASK-114/implementation/continuation-03'
NAV = ROOT / 'DocuN/evidence/TASK-115/orchestration-review02-20261014/input-manifest.json'
OLD_SIZE = 61253
OLD_HASH = '3d6a4ce4e30284f6799f61462e84c419a9fdd7226ef1f1e73dc468815b04a0f2'

def stamp():
    return {'utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'mono_ns': time.monotonic_ns()}

def safe(path):
    path = Path(str(path).replace('\\\\', '/').replace('\\', '/'))
    if not path.is_absolute(): path = ROOT / path
    for part in (path, *path.parents):
        if part.exists() and getattr(part.lstat(), 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise RuntimeError('reparse input refused: ' + str(part))
    return path

def info(path):
    path = safe(path)
    result = {'path': str(path), 'exists': path.is_file()}
    if result['exists']:
        data = path.read_bytes()
        result.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
    return result

def read(path):
    return json.loads(safe(path).read_text(encoding='utf-8-sig'))

def write(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

nav = read(NAV)
start = stamp()
receipt = {
    'task': 'TASK-115/R-109/review-02/STEP017',
    'permit': 'TASK-115-STEP017-REVIEW02-20261014',
    'environment': 'Codex desktop / system GPT-6; A+ is resource label',
    'independent_window_continued': True,
    'prior_controller_summary_exposure_retained': True,
    'excluded': nav['reading_exclusions'],
    'first_tool_clock_return_utc': '2026-10-14T01:20:19Z',
    'first_tool_mono_missing': True,
    'next_actual_sample': {'utc': '2026-10-14T01:20:37.9530199+00:00', 'monotonic_ticks': 12122991647744, 'monotonic_frequency': 10000000},
    'conservative_start_utc': '2026-10-14T01:15:19Z',
    'conservative_missing_point_deduction_seconds': 300,
    'record_sample': start,
    'review_activity_cap_seconds': 5400,
    'save_reserve_seconds': 300,
    'old_active_cumulative_seconds': 8617.261566,
    'calendar_deadline_utc': '2026-10-15T06:16:24.914938Z',
    'old_usage': {'roots': 3, 'api': 3, 'browser': 2, 'offline_seconds': 125.610, 'holding_seconds_conservative': 14.874},
    'new_business_usage_all_zero': True,
    'allowed': 'read/hash/JSON/AST/diff only; do not import or run product or original method',
}
write('receipt.json', receipt)
old = safe(ROOT / 'DocuN/results/TASK-115-result.md').read_bytes()
assert len(old) == OLD_SIZE and hashlib.sha256(old).hexdigest() == OLD_HASH
assert not (OUT / 'prior-result.md').exists()
(OUT / 'prior-result.md').write_bytes(old)

protected = {}
checks = []
def verify(group, entry, base=None):
    raw = entry.get('absolute_path', entry.get('path'))
    p = safe((base / raw) if base is not None else raw)
    actual = info(p)
    expected_exists = entry.get('exists', True)
    ok = actual['exists'] == expected_exists
    if expected_exists:
        ok = ok and actual.get('sha256') == entry.get('sha256')
        if 'bytes' in entry: ok = ok and actual.get('bytes') == entry['bytes']
    checks.append({'group': group, 'relative': raw, 'expected': entry, 'actual': actual, 'matches': ok})
    protected[str(p)] = actual

for group, base in [('current', ROOT), ('final_source', C03 / 'final/source'), ('pre', C03 / 'pre')]:
    for entry in nav[group]: verify(group, entry, base)
for entry in nav['rules']: verify('rule', entry)
for key in ['root_entry','adopted_contract','engineering_card','original_independent_report','current_final_manifest','method_index','engineering_control','engineering_events']:
    verify(key, nav[key])
for key in ['original_review01_evidence', 'raw_evidence_navigation', 'loading_pin_cases']:
    for entry in nav[key]: verify(key, entry)
verify('browser_result', nav['browser_result'])
for p in [NAV, ROOT/'DocuN/tasks/TASK-115.md',ROOT/'DocuN/results/TASK-115-work-decision.md',ROOT/'DocuN/evidence/v4-migration-20260930/rules-snapshot.json',ROOT/'DocuS/架构动态文档.MD',ROOT/'DocuS/执行动态文档.MD',ROOT/'DocuS/最终需求文档.MD']:
    protected[str(p)] = info(p)

manifest = read(C03 / 'final/manifest.json')
assert manifest['files'] == [dict(e, status=next(f['status'] for f in manifest['files'] if f['path']==e['path']), before=next(f.get('before') for f in manifest['files'] if f['path']==e['path'])) for e in nav['current']] or all(all(e.get(k)==f.get(k) for k in ['exists','bytes','sha256']) for e in nav['current'] for f in manifest['files'] if f['path']==e['path'])
changes = [f for f in manifest['files'] if f['status'] != 'unchanged']
write('identity-before.json', {'captured': start,'checks': checks,'mismatches': [c for c in checks if not c['matches']]})
write('protected-before.json', list(protected.values()))
write('current-deltas.json', {'changes': changes,'current_present': sum(e['exists'] for e in nav['current']),'current_absent': [e['path'] for e in nav['current'] if not e['exists']]})

methods = read(C03 / 'final/method-index.json')['methods']
rows = []
key_paths = ['backend/app/data_exit/reference.py','backend/app/data_exit/restore.py','backend/app/data_exit/operations.py','backend/app/data_exit/files.py','backend/app/storage/originals.py','backend/tests/test_data_exit_c03.py','frontend/src/data/DataWorkspace.tsx','frontend/src/data/context.tsx','frontend/src/data/dataApi.ts','frontend/src/main.tsx','frontend/tests/task114-c03-inputs.mjs','frontend/dist/index.html','frontend/dist/assets/index-DZduJTtr.js']
final_map = {e['path']: e for e in nav['current']}
for method in methods:
    as_root = safe(method['as_run'])
    as_manifest_path = as_root / 'manifest.json'
    as_manifest = read(as_manifest_path)
    protected[str(as_manifest_path)] = info(as_manifest_path)
    entries = as_manifest.get('files', []) if isinstance(as_manifest, dict) else as_manifest
    as_map = {e['path']:e for e in entries}
    row = {k:method.get(k) for k in ['label','argv','cwd','start','end','exit_code','seconds','root','layer','log','outcome','cases_exercised','case_count']}
    row['recorded_tested_file_bindings'] = method.get('tested_file_bindings', [])
    row['actual_bindings'] = []
    for rel in key_paths:
        if rel not in as_map: continue
        actual = info(as_root / 'source' / rel)
        if not actual['exists']: actual = info(as_root / rel)
        expected = as_map[rel]
        match = actual['exists']==expected.get('exists',True) and (not actual['exists'] or (actual['sha256']==expected.get('sha256') and actual['bytes']==expected.get('bytes')))
        row['actual_bindings'].append({'path':rel,'actual':actual,'as_run_matches':match,'same_final_bytes':actual.get('sha256')==final_map.get(rel,{}).get('sha256') and actual['exists']==final_map.get(rel,{}).get('exists')})
        protected[actual['path']] = actual
    rows.append(row)
write('as-run-identity.json', rows)
write('protected-before.json', list(protected.values()))

before = ast.parse(safe(C03/'pre/backend/app/data_exit/reference.py').read_text(encoding='utf-8-sig'))
after = ast.parse(safe(ROOT/'backend/app/data_exit/reference.py').read_text(encoding='utf-8-sig'))
ordinary = ['PreparedReference','ReferencePin','OriginalReferenceCoordinator']
ordinary_equal = {name:ast.dump(next(n for n in before.body if isinstance(n,ast.ClassDef) and n.name==name))==ast.dump(next(n for n in after.body if isinstance(n,ast.ClassDef) and n.name==name)) for name in ordinary}
write('ordinary-reference-ast.json', {'ordinary_classes_unchanged': ordinary_equal})
for rel in nav['actual_product_source_changed']:
    b = safe(C03/'pre'/rel).read_text(encoding='utf-8-sig').splitlines(keepends=True)
    a = safe(ROOT/rel).read_text(encoding='utf-8-sig').splitlines(keepends=True)
    name = Path(rel).name + '.diff'
    (OUT/name).write_text(''.join(difflib.unified_diff(b,a,fromfile='C03-pre/'+rel,tofile='current/'+rel)), encoding='utf-8')
summary = {'checks':len(checks),'mismatches':len([c for c in checks if not c['matches']]),'present':sum(e['exists'] for e in nav['current']),'absent':[e['path'] for e in nav['current'] if not e['exists']],'changes': [{'path':f['path'],'status':f['status']} for f in changes],'ordinary_classes_unchanged':ordinary_equal,'method_count':len(rows),'methods': [{'label':r['label'],'exit':r['exit_code'],'seconds':r['seconds'],'binding_mismatches':[b['path'] for b in r['actual_bindings'] if not b['as_run_matches']],'final_differences':[b['path'] for b in r['actual_bindings'] if not b['same_final_bytes']]} for r in rows]}
write('inspection-summary.json', summary)
print(json.dumps(summary,ensure_ascii=False,indent=2))
