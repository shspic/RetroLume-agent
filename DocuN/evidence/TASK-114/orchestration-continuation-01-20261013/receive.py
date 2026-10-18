"""只读核证114实施断点的文件与普通证据，禁止产品import和运行。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
OUT = Path(__file__).resolve().parent
CLOSURE = ROOT / 'DocuN/evidence/TASK-114/implementation/closure-20261013'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def identity(path):
    raw = path.read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


source = load(CLOSURE / 'final-source-manifest.json')
bundle = load(CLOSURE / 'final-bundle-manifest.json')
checked = []
for category, manifest, saved_folder in (('source', source, 'final-source'), ('bundle', bundle, 'final-bundle')):
    for row in manifest['files']:
        expected = {'bytes': row['bytes'], 'sha256': row['sha256']}
        live = ROOT / row['path']
        saved = CLOSURE / saved_folder / row['path']
        assert identity(live) == expected, 'current drift: ' + row['path']
        assert identity(saved) == expected, 'saved drift: ' + str(saved)
        checked.append({'kind': category, 'path': row['path'], **expected})
packages = load(CLOSURE / 'package-identities.json')
for row in packages:
    assert identity(ROOT / row['path']) == {'bytes': row['bytes'], 'sha256': row['sha256']}
rules = load(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
for rule in rules:
    assert identity(Path(rule['absolute_path']))['sha256'] == rule['sha256'], rule['absolute_path']
change_index = load(CLOSURE / 'change-index.json')
control = ROOT / 'DocuN/evidence/TASK-114/implementation/control'
receipt = load(control / 'receipt.json')
note = load(CLOSURE / 'budget-reconciliation-note.json')
assert len(source['files']) == 197 and len(bundle['files']) == 4
assert note['pg_resource_batch_count'] == 8 and note['separate_windows_lock_batch'] == 1
record = {
    'at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
    'TASK': 'TASK-114', 'R': 'R-108', 'continuation': '01',
    'result': {'path': str(ROOT / 'DocuN/results/TASK-114-result.md'), **identity(ROOT / 'DocuN/results/TASK-114-result.md')},
    'current_matches_saved_source': True, 'current_matches_saved_bundle': True,
    'sources': len(source['files']), 'bundles': len(bundle['files']),
    'identities': checked, 'package_identities': packages,
    'rules_matched': len(rules),
    'change_summary': {k: len(change_index[k]) if isinstance(change_index.get(k), list) else change_index.get(k) for k in ('baseline_files', 'final_files', 'modified', 'added', 'unchanged')},
    'old_receipt_identity': identity(control / 'receipt.json'),
    'old_events_identity': identity(control / 'events.jsonl'),
    'old_receipt_counts': receipt['counts'],
    'old_offline_seconds': receipt['offline_seconds'],
    'old_real_holding_seconds': receipt['real_holding_seconds'],
    'root_reconciliation': {'raw_legacy_directory_counter': 7, 'evidenced_pg_batches': 8, 'evidenced_windows_batch': 1, 'evidenced_resource_roots': 9, 'pre_create_restore_attempts_separate': 1, 'conservative_forward_debit': 10, 'old_record_not_rewritten': True},
    'evidence_files': [{'path': str(path), **identity(path)} for path in sorted(CLOSURE.glob('*.json'))],
    'product_runs': 0,
    'conclusion': '部分成果身份确认；非完整动态验收。保持原失败/not_run，续作沿原TASK和窗口。',
}
(OUT / 'received.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'source_matches': len(source['files']), 'bundle_matches': len(bundle['files']), 'rules': len(rules), 'packages': len(packages), 'result': record['result'], 'product_runs': 0}, ensure_ascii=False))
