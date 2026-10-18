"""只读核证C03当前字节、原始方法和收尾账，不运行产品。"""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import ast
import hashlib
import json
import stat

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
OUT = Path(__file__).resolve().parent
BASE = ROOT / 'DocuN/evidence/TASK-114/implementation/continuation-03'


def ordinary(path):
    for item in (path, *path.parents):
        if not item.exists():
            continue
        info = item.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise RuntimeError(f'不穿过重解析点 {item}')


def load(path):
    ordinary(path)
    return json.loads(path.read_text(encoding='utf-8-sig'))


def identity(path):
    ordinary(path)
    data = path.read_bytes()
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def record(path):
    return {'path': str(path), **identity(path)}


def verify(rows, base):
    result = []
    for row in rows:
        path = base / row['path']
        ordinary(path)
        expected_exists = row.get('exists', bool(row.get('sha256')))
        assert path.is_file() == expected_exists, str(path)
        if expected_exists:
            assert identity(path)['sha256'] == row['sha256'], str(path)
            result.append({'path': row['path'], 'exists': True, **identity(path)})
        else:
            assert not path.exists()
            result.append({'path': row['path'], 'exists': False})
    return result


manifest = load(BASE / 'final/manifest.json')['files']
current = verify(manifest, ROOT)
snapshot = verify(manifest, BASE / 'final/source')
before = load(BASE / 'pre-manifest.json')
pre = verify(before, BASE / 'pre')
report = ROOT / 'DocuN/results/TASK-114-result.md'
delivery = load(BASE / 'final/delivery.json')
assert identity(report) == {key: delivery[key] for key in ('bytes', 'sha256')}
old_report = BASE / 'pre/TASK-114-result.md'
assert identity(old_report) == delivery['old_suffix_identity']
assert identity(old_report) == {'bytes': 69598, 'sha256': 'e457d13159c439da8c56814b4f9c860973c0ff5d8622793ab4663584ffe5ad11'}
assert report.read_bytes().endswith(old_report.read_bytes())
assert report.read_bytes() == (BASE / 'report-prefix.md').read_bytes() + old_report.read_bytes()

audit_report = ROOT / 'DocuN/results/TASK-115-result.md'
assert identity(audit_report) == {'bytes': 61253, 'sha256': '3d6a4ce4e30284f6799f61462e84c419a9fdd7226ef1f1e73dc468815b04a0f2'}
audit_files = []
for path in sorted((ROOT / 'DocuN/evidence/TASK-115/review-01').iterdir()):
    assert path.is_file()
    audit_files.append(record(path))
prior_received = load(ROOT / 'DocuN/evidence/TASK-115/orchestration-review01-receipt-20261014/received.json')
for row in prior_received['review_evidence']:
    assert identity(Path(row['path'])) == {key: row[key] for key in ('bytes', 'sha256')}

rules = load(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
for row in rules:
    assert identity(Path(row['absolute_path']))['sha256'] == row['sha256']
index = load(BASE / 'final/method-index.json')
assert len(index['methods']) == 13
assert len(index['offline_exact']) == 11 and len(index['browser_exact']) == 2
methods = []
for row in index['methods']:
    folder = ROOT / row['as_run']
    as_run_path = folder / 'manifest.json'
    data = load(as_run_path)
    entries = data['files'] if isinstance(data, dict) else data
    verify(entries, folder)
    tested = []
    for binding in row['tested_file_bindings']:
        rel = binding['path']
        assert identity(folder / rel)['sha256'] == binding['as_run_sha256'], rel
        actual_final = identity(ROOT / rel)['sha256']
        assert actual_final == binding['final_sha256'], rel
        assert (binding['as_run_sha256'] == actual_final) == binding['same_final_bytes']
        tested.append(binding)
    methods.append({'label': row['label'], 'exit_code': row['exit_code'], 'seconds': row['seconds'],
                    'argv': row['argv'], 'cwd': row['cwd'], 'as_run_manifest': record(as_run_path),
                    'tested_bindings': tested, 'final_binding': row['final_binding']})

loading = next(row for row in methods if row['label'] == 'loading-pin-1207676843000000')
browser = next(row for row in methods if row['label'] == 'c03-browser-1210447187000000')
assert loading['exit_code'] == browser['exit_code'] == 0
assert all(row['same_final_bytes'] for row in loading['tested_bindings'])
assert all(row['same_final_bytes'] for row in browser['tested_bindings'])
browser_result_path = BASE / 'batches/c03-browser-1210447187000000/result.json'
browser_result = load(browser_result_path)
assert len(browser_result['cases']) == 12 and browser_result['state'] == 'passed'
assert browser_result['errors'] == [] and browser_result['automatic_action_POST'] == 0
for row in browser_result['finalIdentity']:
    assert identity(ROOT / row['path'])['sha256'] == row['sha256']

control_path = ROOT / 'DocuN/evidence/TASK-114/implementation/control/receipt.json'
events_path = ROOT / 'DocuN/evidence/TASK-114/implementation/control/events.jsonl'
control = load(control_path)
assert control['counts'] == delivery['counts']
assert all(row['state'] == 'stopped' for row in control['resources'])
assert all(row['end_ns'] is not None for row in delivery['roots'])
assert all(row['state'] == 'stopped' and row['last_stop']['process_ended']
           and row['last_stop']['actual_browser_close'] for row in delivery['new_resource_closure'])
old_events = BASE / 'pre/events.jsonl'
assert events_path.read_bytes().startswith(old_events.read_bytes())

changed = [row for row in manifest if row['status'] != 'unchanged']
app_changed = [row['path'] for row in changed if row['path'].startswith(('backend/app/', 'frontend/src/'))]
assert sorted(app_changed) == ['backend/app/data_exit/reference.py', 'backend/app/data_exit/restore.py', 'frontend/src/data/DataWorkspace.tsx']
def class_digest(path):
    tree = ast.parse(path.read_text(encoding='utf-8-sig'))
    node = next(item for item in tree.body if isinstance(item, ast.ClassDef) and item.name == 'ReferencePin')
    return hashlib.sha256(ast.dump(node, include_attributes=False).encode()).hexdigest()
assert class_digest(ROOT / 'backend/app/data_exit/reference.py') == class_digest(BASE / 'pre/backend/app/data_exit/reference.py')
raw_navigation = []
for folder in (BASE / 'final', BASE / 'methods', BASE / 'batches', BASE / 'offline', BASE / 'observations'):
    for path in sorted(folder.rglob('*')):
        ordinary(path)
        if path.is_file() and not path.is_relative_to(BASE / 'final/source'):
            raw_navigation.append(record(path))

proof = {
    'observed_at': datetime.now(timezone.utc).isoformat(),
    'purpose': 'C03候选回收与原115两项增量复核输入，不是独审或产品动态验收',
    'metadata_check_correction': '首检沿用C02的pre路径猜测，FileNotFoundError退出1；实读C03 pre及c03_deliver后改为实际pre/TASK-114-result.md、pre/events.jsonl。未运行或修改产品，未保存失败的核证通过结论。',
    'report': record(report), 'old_suffix': record(old_report), 'old_suffix_exact': True,
    'unchanged_independent_report': record(audit_report), 'unchanged_review01_evidence': audit_files,
    'current': current, 'final_source': snapshot, 'pre': pre,
    'manifest': record(BASE / 'final/manifest.json'), 'status_counts': dict(Counter(row['status'] for row in manifest)),
    'changed': changed, 'actual_product_source_changed': app_changed,
    'methods': methods, 'method_index': record(BASE / 'final/method-index.json'),
    'raw_evidence_navigation': raw_navigation,
    'loading_pin_case_files': [record(path) for path in sorted((BASE / 'offline/cases/loading-pin-1207676843000000').iterdir())],
    'browser_result': record(browser_result_path), 'browser_cases': [row['case'] for row in browser_result['cases']],
    'normal_ReferencePin_class_AST_unchanged': True,
    'rules': rules, 'counts': control['counts'], 'limits': control['limits'],
    'control': record(control_path), 'events': record(events_path), 'old_events_prefix_unchanged': True,
    'delivery': delivery, 'inheritance': load(BASE / 'final/inheritance.json'),
    'stopped_resource_intervals': len(control['resources']),
    'old_owned_PG_basis': '本轮无新增PG；旧Stopped继承已有精确原件，不冒今天Docker现场观察',
    'decision': '实现与定向补证候选已回收；DEF035/036仍开放待原115 review-02，F01/F04已关闭不重审',
    'product_execution_by_orchestrator': 0,
}
target = OUT / 'received.json'
assert not target.exists()
target.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
assert load(target)['report'] == proof['report']
print(json.dumps({'state': 'received_byte_verified', 'report': proof['report'],
                  'current_files': sum(row['exists'] for row in current), 'manifest_entries': len(manifest),
                  'changed_product_source': app_changed, 'methods': len(methods), 'browser_cases': len(browser_result['cases']),
                  'all_resources_ledger_stopped': True, 'receipt': str(target)}, ensure_ascii=False))
