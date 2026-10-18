"""核对独立增量结果、封存字节与原件；不导入产品或执行测试。"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import stat

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
OUT = Path(__file__).resolve().parent
AUDIT = ROOT / 'DocuN/evidence/TASK-115/review-01'


def ordinary(path):
    for item in (path, *path.parents):
        if not item.exists():
            continue
        metadata = item.lstat()
        if stat.S_ISLNK(metadata.st_mode) or getattr(metadata, 'st_file_attributes', 0) & 0x400:
            raise RuntimeError(f'不穿过重解析点 {item}')


def load(path):
    ordinary(path)
    return json.loads(path.read_text(encoding='utf-8-sig'))


def identity(path):
    ordinary(path)
    raw = path.read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


report = ROOT / 'DocuN/results/TASK-115-result.md'
delivery = load(AUDIT / 'delivery.json')
assert identity(report) == {key: delivery[key] for key in ('bytes', 'sha256')}
prior = AUDIT / 'prior-result.md'
assert identity(prior) == {'bytes': 37767, 'sha256': '7d34ec7e7f433effe3bf51367c68229a566dc525361a30c4b2c496702f4ca67a'}
assert report.read_bytes().endswith(prior.read_bytes())
assert report.read_bytes() == (AUDIT / 'review-prefix.md').read_bytes() + prior.read_bytes()
assert all(value == 0 for value in delivery['new_business_counts'].values())

manifest = load(ROOT / 'DocuN/evidence/TASK-114/implementation/continuation-02/final/manifest.json')
absent = {'frontend/dist/assets/index-CJ8Yp7JQ.js', 'frontend/dist/assets/index-DcQS7jxH.js'}
current = []
for row in manifest:
    path = ROOT / row['path']
    ordinary(path)
    if row['path'] in absent:
        assert not path.exists()
        current.append({'path': row['path'], 'exists': False})
    else:
        assert identity(path) == {key: row[key] for key in ('bytes', 'sha256')}
        current.append({'path': row['path'], 'exists': True, **identity(path)})

protected = load(AUDIT / 'protected-before.json')['files']
checked = []
for row in protected:
    path = Path(row['path'])
    if path == report:
        checked.append({'path': str(path), 'basis': '仅获准新增review前缀，原报告后缀已单独核对'})
        continue
    assert identity(path)['sha256'] == row['sha256'], str(path)
    checked.append({'path': str(path), **identity(path)})
rules = load(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
for row in rules:
    assert identity(Path(row['absolute_path']))['sha256'] == row['sha256']

evidence = []
for path in sorted(AUDIT.iterdir()):
    ordinary(path)
    assert path.is_file(), str(path)
    evidence.append({'path': str(path), **identity(path)})

control_path = ROOT / 'DocuN/evidence/TASK-114/implementation/control/receipt.json'
control = load(control_path)
assert control['counts'] == {'real_roots': 21, 'frontend_build': 5, 'windows_start': 11,
                            'pg_create': 9, 'pg_success': 9, 'pg_start': 37,
                            'api_start': 8, 'browser_start': 5}
assert all(row['state'] == 'stopped' for row in control['resources'])
proof = {
    'received_at': datetime.now(timezone.utc).isoformat(),
    'purpose': '回收原115独立review-01；核对象及原件后裁定两个关闭、两个原P1继续同工程修复',
    'report': {'path': str(report), **identity(report)},
    'old_suffix': {'path': str(prior), **identity(prior), 'preserved': True},
    'current': current, 'current_present_count': sum(row['exists'] for row in current),
    'protected_checks': checked, 'protected_entry_count': len(checked),
    'review_evidence': evidence, 'review_evidence_count': len(evidence),
    'rules': rules, 'audit_delivery': delivery,
    'findings': load(AUDIT / 'findings.json'),
    'deadline_original_progress': {'path': str(AUDIT / 'deadline-original-progress.json'),
                                   **identity(AUDIT / 'deadline-original-progress.json')},
    'engineering_report': {'path': str(ROOT / 'DocuN/results/TASK-114-result.md'),
                           **identity(ROOT / 'DocuN/results/TASK-114-result.md')},
    'engineering_card_before': {'path': str(ROOT / 'DocuN/tasks/TASK-114.md'),
                               **identity(ROOT / 'DocuN/tasks/TASK-114.md')},
    'engineering_control': {'path': str(control_path), **identity(control_path)},
    'engineering_counts': control['counts'], 'engineering_limits': control['limits'],
    'engineering_continuation_before': control['continuation'],
    'resource_basis': 'review-01零新增消费者；原control全部stopped，沿用2026-10-13准确owned metadata，不冒今日再实查',
    'decision': {'DEF-034/F01': '关闭原取消覆盖根因，范围限已批准切片',
                 'DEF-037/F04': '关闭原正文依赖投影根因，保原头及历史',
                 'DEF-035/F02': 'P1开放：LoadingReferencePin未传同Operation',
                 'DEF-036/F03': 'P1开放：删除policy/范围输入生命周期与迟到计划'},
    'evidence_correction': '真实PG 2秒deadline只抵达reading后失败，不称capture后发布延迟；文件层后段方法仍有效',
    'independence': '接受原独审窗连续性和旧暴露披露；本轮无实现上下文、零产品写入',
    'product_execution_by_orchestrator': 0,
}
target = OUT / 'received.json'
assert not target.exists()
target.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
assert load(target)['report'] == proof['report']
print(json.dumps({'state': 'received', 'report': proof['report'], 'current_present': proof['current_present_count'],
                  'protected_entries': len(checked), 'review_evidence_files': len(evidence),
                  'decision': proof['decision'], 'engineering_card': proof['engineering_card_before']}, ensure_ascii=False))
