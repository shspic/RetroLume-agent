"""回收独立终审并核当前/历史字节，形成有限切片关闭依据；不执行产品。"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import stat

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
OUT = Path(__file__).resolve().parent
AUDIT = ROOT / 'DocuN/evidence/TASK-115/review-02'


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


def record(path):
    return {'path': str(path), **identity(path)}


report = ROOT / 'DocuN/results/TASK-115-result.md'
delivery = load(AUDIT / 'delivery.json')
assert identity(report) == {key: delivery[key] for key in ('bytes', 'sha256')}
prior = AUDIT / 'prior-result.md'
assert identity(prior) == {'bytes': 61253, 'sha256': '3d6a4ce4e30284f6799f61462e84c419a9fdd7226ef1f1e73dc468815b04a0f2'}
assert report.read_bytes().endswith(prior.read_bytes())
assert len(report.read_bytes()) - len(prior.read_bytes()) == delivery['prefix_bytes']
assert all(value == 0 for value in delivery['new_business_usage'].values())
assert delivery['protected_before_write_mismatches'] == delivery['protected_after_write_mismatches'] == []

protected_data = load(AUDIT / 'protected-before.json')
protected_rows = protected_data['files'] if isinstance(protected_data, dict) else protected_data
protected_checks = []
for row in protected_rows:
    path = Path(row['path'])
    if path == report:
        protected_checks.append({'path': str(path), 'basis': '唯一获准报告前缀，原61253字节后缀已核'})
        continue
    if row.get('exists') is False:
        ordinary(path)
        assert not path.exists(), str(path)
        protected_checks.append({'path': str(path), 'exists': False})
        continue
    assert identity(path)['sha256'] == row['sha256'], str(path)
    protected_checks.append(record(path))

previous = load(ROOT / 'DocuN/evidence/TASK-114/orchestration-c03-receipt-20261014/received.json')
current = previous['current']
for row in current:
    path = ROOT / row['path']
    ordinary(path)
    if row['exists']:
        assert identity(path) == {key: row[key] for key in ('bytes', 'sha256')}
    else:
        assert not path.exists()
rules = load(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
for row in rules:
    assert identity(Path(row['absolute_path']))['sha256'] == row['sha256']
evidence = []
for path in sorted(AUDIT.iterdir()):
    ordinary(path)
    assert path.is_file(), str(path)
    evidence.append(record(path))
assert load(AUDIT / 'protected-final-check.json')['mismatches'] == []

engineering_report = ROOT / 'DocuN/results/TASK-114-result.md'
assert identity(engineering_report) == {'bytes': 90515, 'sha256': '12985d9837c18333acb9b4113db178993e2c45c710da3193112529a6856bfdf5'}
control_path = ROOT / 'DocuN/evidence/TASK-114/implementation/control/receipt.json'
control = load(control_path)
assert all(row['state'] == 'stopped' for row in control['resources'])
findings = load(AUDIT / 'findings.json')
assert findings['DEF035_F02']['new_blocking_gap'] is None
assert findings['DEF036_F03']['new_blocking_gap'] is None
proof = {
    'received_at': datetime.now(timezone.utc).isoformat(),
    'purpose': '原115 review-02独立终审验收与原有限STEP017-P1关闭核证，不运行产品',
    'metadata_check_correction': '首检将protected中exists=false的旧移除bundle误作现存文件读hash，FileNotFoundError退出1；按原字段核缺失后继续。无产品动作，也未曾保存错误的通过结论。',
    'report': record(report), 'prior_report': record(prior), 'prior_suffix_exact': True,
    'protected_checks': protected_checks, 'protected_entry_count': len(protected_checks),
    'audit_evidence': evidence, 'audit_evidence_count': len(evidence),
    'current': current, 'current_present_count': sum(row['exists'] for row in current),
    'rules': rules, 'audit_delivery': delivery, 'audit_findings': findings,
    'engineering_report': record(engineering_report), 'engineering_control': record(control_path),
    'engineering_counts': control['counts'], 'engineering_limits': control['limits'],
    'stopped_resource_intervals': len(control['resources']),
    'closure': {
        'TASK-114/R-108': '通过，已采用有限STEP017-P1完整实现及适用验证',
        'TASK-115/R-109': '通过，原集中独审及两轮增量结论/证据/控制合格',
        'DEF-035/F02': '关闭原loading pin未贯通同D根因',
        'DEF-036/F03': '关闭原policy/file/plan/scope输入生命周期根因',
        'DEF-034/F01_and_DEF-037/F04': '前轮已关闭，不重开、不抹历史',
        'STEP017-P1': '已完成/已验证/有限范围通过',
    },
    'scope': '数据可读退出、备份、隔离副本恢复验证、永久只读查看及相应删除/引用一致性',
    'not_granted': ['真实用户库迁移/切换/删除', '恢复副本重新授执行权', '新真实provider/费用',
                    '完整NFR005或STEP018—020通过', 'M-1/项目/发布通过'],
    'evidence_limits_retained': ['受控连接参数不冒物理PG等待上界/驱动强停',
                                 'route UI不冒真实selector', '旧2秒PG只证reading超时',
                                 '旧FAIL/未知/时钟配对与保守扣时/历史超限不抹去'],
    'independence': '原115隔离窗未参与实现；原及本轮附带主控摘要暴露已披露，不作通过依据，接受受限独立性',
    'resource_basis': '终审零新增业务，工程准确关闭原件和唯一账均保留；未重启Docker或重复现场证明',
    'product_execution_by_orchestrator': 0,
}
target = OUT / 'received.json'
assert not target.exists()
target.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
assert load(target)['report'] == proof['report']
print(json.dumps({'state': 'accepted_finite_closure', 'report': proof['report'],
                  'protected_entries': len(protected_checks), 'audit_evidence': len(evidence),
                  'current_files': proof['current_present_count'], 'closure': proof['closure'],
                  'path': str(target)}, ensure_ascii=False))
