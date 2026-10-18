"""核证113修正轮01的文件与文档身份；不导入或运行产品。"""
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from pathlib import Path
import hashlib
import json
import re

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
OUT = Path(__file__).resolve().parent
DESIGN = ROOT / 'DocuN/evidence/TASK-113/design'
REV = DESIGN / 'revision-01'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def identity(path):
    raw = path.read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def verify(entries):
    for entry in entries:
        assert identity(Path(entry['path'])) == {
            'bytes': entry['bytes'], 'sha256': entry['sha256']
        }, entry['path']
    return len(entries)


accepted = load(REV / 'accepted.json')
delivery = load(REV / 'delivery.json')
result_path = ROOT / 'DocuN/results/TASK-113-result.md'
result = result_path.read_bytes()
assert identity(result_path) == {
    'bytes': delivery['bytes'], 'sha256': delivery['sha256']
}
assert result[:delivery['current_prefix_bytes']] == (REV / 'current-contract.md').read_bytes()
assert result[-delivery['old_suffix_bytes']:] == (REV / 'prior-result.md').read_bytes()
assert hashlib.sha256(result[-delivery['old_suffix_bytes']:]).hexdigest() == delivery['old_suffix_sha256']
assert len(result) == delivery['current_prefix_bytes'] + delivery['old_suffix_bytes']

input_count = verify(accepted['inputs'])
additional_inputs = load(DESIGN / 'additional-source-identity.json')
additional_input_count = verify(additional_inputs)
old_evidence_count = verify(load(DESIGN / 'evidence-manifest.json')['entries'])
revision_evidence_count = verify(load(REV / 'evidence-manifest.json')['entries'])
rules = load(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
for rule in rules:
    assert identity(Path(rule['absolute_path']))['sha256'] == rule['sha256'], rule['absolute_path']

new_seconds = Decimal(delivery['completed_ns'] - accepted['accepted_ns']) / Decimal(10**9)
assert new_seconds == Decimal(str(delivery['new_observed_seconds']))
assert new_seconds <= Decimal(accepted['new_window_seconds'])
total = Decimal(accepted['old_observed_seconds']) + new_seconds
assert total <= Decimal(accepted['total_observed_cap'])
assert delivery['total_official_pages'] == delivery['official_cap'] == 6
assert delivery['new_official_pages'] == 2
assert delivery['old_prepare_unknown_preserved'] is True

contract = (REV / 'current-contract.md').read_text(encoding='utf-8-sig')
methods = re.findall(r'^- (V\d{2})，', contract, re.MULTILINE)
assert methods == [f'V{n:02d}' for n in range(1, 30)], methods
for heading in ('## A ', '## B ', '## C ', '## D '):
    assert heading in contract
assert not (ROOT / 'DocuN/tasks/TASK-114.md').exists(), '下一实施卡已存在，需要核对状态'

record = {
    'at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
    'TASK': 'TASK-113', 'R': 'R-107', 'revision': '01',
    'delivery': delivery,
    'result_identity': identity(result_path),
    'result_prefix_equals_current_contract': True,
    'first_round_byte_exact_suffix_preserved': True,
    'inputs_checked': input_count,
    'additional_inputs_checked': additional_input_count,
    'inputs_before_main_publication': accepted['inputs'],
    'additional_inputs_before_main_publication': additional_inputs,
    'rules_checked': len(rules),
    'old_evidence_checked': old_evidence_count,
    'revision_evidence_checked': revision_evidence_count,
    'budget': {
        'new_observed_seconds': str(new_seconds),
        'new_cap_seconds': accepted['new_window_seconds'],
        'total_observed_seconds': str(total),
        'total_cap_seconds': accepted['total_observed_cap'],
        'old_prepare': accepted['old_prepare'],
        'remaining_is_not_new_execution_authorization': True,
    },
    'matrix': methods,
    'product_runs': 0,
    'main_review': '文档一致性与现有文件身份核证；未实施、未运行、未作产品独立审计',
}
(OUT / 'received.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({
    'report_match': True, 'history_byte_exact': True,
    'inputs': input_count, 'additional_inputs': additional_input_count, 'rules': len(rules),
    'old_evidence': old_evidence_count, 'revision_evidence': revision_evidence_count,
    'future_methods': len(methods), 'new_seconds': str(new_seconds),
    'total_seconds': str(total), 'product_runs': 0,
}, ensure_ascii=False))
