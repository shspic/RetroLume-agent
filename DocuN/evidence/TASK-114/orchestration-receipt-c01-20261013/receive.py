"""读取C01身份与原件索引；不导入产品、不执行测试或数据库。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
OUT = Path(__file__).resolve().parent
FINAL = ROOT / 'DocuN/evidence/TASK-114/implementation/continuation-01/final'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def identity(path):
    raw = path.read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


rows = load(FINAL / 'manifest.json')
checked, removed = [], []
for row in rows:
    path = ROOT / row['path']
    if row['change'] == 'deleted_build_output':
        assert not path.exists(), str(path)
        removed.append(row)
        continue
    expected = {'bytes': row['bytes'], 'sha256': row['sha256']}
    assert identity(path) == expected, 'current drift: ' + row['path']
    assert identity(FINAL / 'source' / row['path']) == expected, 'saved drift: ' + row['path']
    checked.append(row)
bundle = load(FINAL / 'bundle.json')
for row in bundle:
    assert identity(ROOT / row['path']) == {'bytes': row['bytes'], 'sha256': row['sha256']}
indices = []
for filename in ('batch-result-index.json', 'failure-index.json'):
    entries = load(FINAL / filename)
    for entry in entries:
        assert identity(ROOT / entry['path'])['sha256'] == entry['sha256'], entry['path']
    indices.append({'index': filename, 'entries': len(entries), 'hash_matches': True})
report = ROOT / 'DocuN/results/TASK-114-result.md'
report_bytes = report.read_bytes()
old_bytes = (ROOT / 'DocuN/evidence/TASK-114/implementation/closure-20261013' / 'final-source-manifest.json').read_bytes()
# 原报告后缀只核已交回的固定身份，绝不从HEAD重建。
assert hashlib.sha256(report_bytes[-34931:]).hexdigest() == 'c655556d7b783a871e34c5a50c40cb9d477504d0b8d389f028e14f68b091d1af'
rules = load(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
for rule in rules:
    assert identity(Path(rule['absolute_path']))['sha256'] == rule['sha256'], rule['absolute_path']
freeze = load(FINAL / 'budget-at-freeze.json')
resources = load(FINAL / 'resources.json')
assert freeze['counts']['real_roots'] == freeze['limits']['real_roots'] == 18
assert all(not resource['running'] and resource['pid'] == 0 for resource in resources)
record = {
    'at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
    'TASK': 'TASK-114', 'R': 'R-108', 'continuation': '01',
    'result': {'path': str(report), **identity(report)},
    'old_report_byte_exact_suffix_preserved': True,
    'current_and_saved_files': checked, 'deleted_build_outputs': removed,
    'current_matches_saved': True,
    'current_source_files': len(checked) - len(bundle), 'current_bundle_files': len(bundle),
    'index_checks': indices, 'rules_matched': len(rules),
    'budget_at_freeze': freeze, 'resources_at_freeze': resources,
    'claim_level': '文件及已存原始证据身份核证，主要闭环候选，非完整29项或独立审计通过',
    'product_runs': 0,
}
(OUT / 'received.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'current_and_saved': len(checked), 'source': len(checked)-len(bundle), 'bundle': len(bundle), 'removed': len(removed), 'indices': indices, 'rules': len(rules), 'result': record['result'], 'product_runs': 0}, ensure_ascii=False))
