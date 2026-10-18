"""仅核对已有字节、证据导航和收尾账，不导入或运行产品。"""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
OUT = Path(__file__).resolve().parent
BASE = ROOT / 'DocuN/evidence/TASK-114/implementation/continuation-02'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def identity(path):
    raw = path.read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def subset_identity(row):
    return {key: row[key] for key in ('bytes', 'sha256')}


def check_tree(rows, directory, allowed_absent):
    checked = []
    for row in rows:
        path = directory / row['path']
        if row['path'] in allowed_absent:
            assert not path.exists(), str(path)
            checked.append({'path': row['path'], 'exists': False, 'basis': allowed_absent[row['path']]})
        else:
            assert identity(path) == subset_identity(row), str(path)
            checked.append({'path': row['path'], 'exists': True, **identity(path)})
    return checked


rules = load(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
rule_checks = []
for row in rules:
    actual = identity(Path(row['absolute_path']))
    assert actual['sha256'] == row['sha256'], row['absolute_path']
    rule_checks.append({'path': row['absolute_path'], **actual})

final = load(BASE / 'final/manifest.json')
absent = {
    'frontend/dist/assets/index-CJ8Yp7JQ.js': '本轮构建移除的旧输出，manifest 标记 deleted',
    'frontend/dist/assets/index-DcQS7jxH.js': 'C01 已移除输出，C02 manifest 仍登记 unchanged；旧缺失不恢复',
}
checks = check_tree(final, ROOT, absent)
snapshot_checks = check_tree(final, BASE / 'final/source', absent)
before = load(BASE / 'pre-manifest.json')
pre_checks = check_tree(before, BASE / 'pre', {
    'frontend/dist/assets/index-DcQS7jxH.js': '原 C01 已移除旧构建输出',
})
report = ROOT / 'DocuN/results/TASK-114-result.md'
old_report = BASE / 'pre/DocuN/results/TASK-114-result.md'
assert identity(old_report) == {
    'bytes': 53842,
    'sha256': 'c0f970d48ac57d1081e79afa90bcab5822d4c6058e60ed7f9fb6f9b0cd770e2e',
}
assert report.read_bytes().endswith(old_report.read_bytes())
assert identity(report) == subset_identity(load(BASE / 'final/delivery.json'))

audit = load(ROOT / 'DocuN/evidence/TASK-115/audit/delivery.json')
audit_report = ROOT / 'DocuN/results/TASK-115-result.md'
assert identity(audit_report) == subset_identity(audit['report'])
for row in audit['evidence']:
    path = Path(row['path'])
    assert path.is_relative_to(ROOT / 'DocuN/evidence/TASK-115/audit')
    assert identity(path) == subset_identity(row), str(path)

bindings = []
for path in sorted((BASE / 'as-run').glob('*/manifest.json')):
    data = load(path)
    rows = data['files']
    if isinstance(rows, dict):
        rows = [{'path': key, **value} for key, value in rows.items()]
    mismatches = []
    present_final = {row['path']: row for row in final if row['path'] not in absent}
    for row in rows:
        name = row['path']
        if name in present_final and row['sha256'] != present_final[name]['sha256']:
            mismatches.append({'path': name, 'as_run_sha256': row['sha256'],
                               'final_sha256': present_final[name]['sha256']})
    bindings.append({'path': str(path), 'label': data.get('label'), 'utc': data.get('utc'),
                     'file_count': len(rows), 'different_from_final': mismatches,
                     'meaning': '字节差异导航，不代替独立的行为继承判定'})

raw_navigation = []
for folder in sorted((BASE / 'batches').iterdir()):
    if not folder.is_dir():
        continue
    files = [{'path': str(path), **identity(path)} for path in sorted(folder.iterdir())
             if path.is_file() and path.suffix.lower() in ('.json', '.log', '.txt')]
    raw_navigation.append({'batch': folder.name, 'files': files})

closure = load(BASE / 'closure.json')
assert len(closure['containers']) == 9
assert all(row['running'] is False and row['pid'] == 0 for row in closure['containers'])
assert all(row['original_process_ended'] is True for row in closure['processes'])
assert closure['task_owned_active_TCP'] == []
assert closure['all_owned_consumers_stopped'] is True
control = load(ROOT / 'DocuN/evidence/TASK-114/implementation/control/receipt.json')
assert control['counts'] == closure['counts']
assert all(row['state'] == 'stopped' for row in control['resources'])

proof = {
    'observed_at': datetime.now(timezone.utc).isoformat(),
    'purpose': 'TASK114 C02 实际回收及原115增量复核输入身份；不是产品独审或运行通过',
    'report': {'path': str(report), **identity(report)},
    'old_report_suffix': {'path': str(old_report), **identity(old_report), 'preserved': True},
    'unchanged_audit_report': {'path': str(audit_report), **identity(audit_report)},
    'old_audit_evidence_verified': len(audit['evidence']),
    'manifest': {'path': str(BASE / 'final/manifest.json'), **identity(BASE / 'final/manifest.json'),
                 'entries': len(final), 'current_files': len(checks) - len(absent),
                 'change_counts': dict(Counter(row['change'] for row in final)),
                 'known_absent_outputs': absent},
    'current': checks, 'final_source_snapshot': snapshot_checks, 'pre': pre_checks,
    'rules': rule_checks,
    'as_run_bindings': bindings,
    'raw_batch_navigation': raw_navigation,
    'offline_method_index_limitation': '原 final/method-index.json 的 offline_exact 为空；须由原始日志、cases、as-run、events 重建，不据索引声称完整方法/退出码同点采样',
    'resource_closure': {'path': str(BASE / 'closure.json'), **identity(BASE / 'closure.json'),
                         'stopped_container_count': len(closure['containers']),
                         'ended_original_consumer_count': len(closure['processes']),
                         'stopped_resource_intervals': len(control['resources']),
                         'basis': '原件交叉一致；当前只读元数据核查另存，不代替停止证据'},
    'counts': control['counts'], 'limits': control['limits'],
    'offline_seconds': control['offline_seconds'],
    'holding_seconds': control['real_holding_seconds'],
    'engineering_continuation': control['continuation'],
    'audit_active_previous_conservative': audit['active_seconds_conservative'],
    'audit_active_remaining_conservative': audit['active_remaining_conservative_seconds'],
    'decision': '实现与定向补证候选已返回；DEF034—037保留开放待原115独立增量复核，未关闭STEP017',
    'product_execution_by_orchestrator': 0,
}
target = OUT / 'received.json'
assert not target.exists(), '不覆盖已有回收原件'
target.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
assert load(target)['report'] == proof['report']
print(json.dumps({'state': 'received_and_byte_verified', 'report': proof['report'],
                  'current_files': proof['manifest']['current_files'], 'pre_rows': len(pre_checks),
                  'old_audit_evidence': len(audit['evidence']), 'as_run_batches': len(bindings),
                  'counts': proof['counts'], 'path': str(target)}, ensure_ascii=False))
