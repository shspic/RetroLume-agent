"""续作03接收、字节基线及唯一旧账前向追加；不访问PG或旧业务控制。"""
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = ROOT / 'DocuN/evidence/TASK-114/implementation/continuation-03'
CONTROL = ROOT / 'DocuN/evidence/TASK-114/implementation/control'
INPUT = ROOT / 'DocuN/evidence/TASK-114/orchestration-repair-c03-20261014'


def identity(path):
    raw = path.read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def main():
    if EVIDENCE.exists():
        raise RuntimeError('续作03目录已经存在，必须核对断点，不能重复接收')
    manifest = json.loads((INPUT / 'input-manifest.json').read_text(encoding='utf-8-sig'))
    permit = json.loads((INPUT / 'continuation-permit.json').read_text(encoding='utf-8-sig'))
    mismatch = []
    for item in manifest['current']:
        path = ROOT / item['path']
        actual = identity(path) if path.is_file() else None
        if bool(actual) != item['exists'] or actual and any(actual[k] != item[k] for k in ('bytes', 'sha256')):
            mismatch.append({'path': item['path'], 'actual': actual, 'expected': item})
    locked = json.loads((ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json').read_text(encoding='utf-8-sig'))
    assert {i['relative_path']: i['sha256'] for i in locked} == {i['relative_path']: i['sha256'] for i in manifest['rules']}
    for item in locked:
        path = Path(item['absolute_path'])
        actual = identity(path)
        if actual['sha256'] != item['sha256']: mismatch.append({'path': str(path), 'actual': actual})
    for key in ('root_entry', 'adopted_contract', 'audit_report', 'engineering_report_before',
                'engineering_control_before', 'engineering_events_before', 'C02_final_manifest'):
        item = manifest[key]
        actual = identity(Path(item['path']))
        if any(actual[k] != item[k] for k in ('bytes', 'sha256')): mismatch.append({'key': key, 'actual': actual})
    for path in manifest['known_missing_old_outputs']:
        if (ROOT / path).exists(): mismatch.append({'unexpected_exists': path})
    if mismatch:
        print(json.dumps({'input_drift': mismatch}, ensure_ascii=False)); return 2
    old = json.loads((CONTROL / 'receipt.json').read_text(encoding='utf-8'))
    assert old['counts'] == permit['previous_counts']
    assert old['continuation']['status'] == 'delivered_candidate_for_TASK115_review01'
    assert all(r['state'] == 'stopped' and r['end_ns'] is not None for r in old['resources'])
    assert all(r['end_ns'] is not None for r in old['continuation']['real_batches'])
    EVIDENCE.mkdir(parents=True)
    pre = EVIDENCE / 'pre'; pre.mkdir()
    for item in manifest['current']:
        if not item['exists']: continue
        target = pre / item['path']; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / item['path'], target)
    for key, name in (('engineering_report_before', 'TASK-114-result.md'),
                      ('engineering_control_before', 'receipt.json'), ('engineering_events_before', 'events.jsonl')):
        shutil.copyfile(manifest[key]['path'], pre / name)
    (EVIDENCE / 'pre-manifest.json').write_text(json.dumps(manifest['current'], ensure_ascii=False, indent=2), encoding='utf-8')
    shutil.copyfile(INPUT / 'input-manifest.json', EVIDENCE / 'input-manifest.json')
    shutil.copyfile(INPUT / 'continuation-permit.json', EVIDENCE / 'continuation-permit.json')
    sampled_utc = datetime.fromisoformat('2026-10-13T23:49:44.0046548+00:00')
    sampled_ns = 1206845296862400
    begin_utc, begin_ns = sampled_utc - timedelta(seconds=300), sampled_ns - 300_000_000_000
    deadline = min(begin_utc + timedelta(hours=24), datetime.fromisoformat('2026-10-15T08:54:00+00:00'))
    current_ns = time.monotonic_ns()
    assert current_ns > sampled_ns and datetime.now(timezone.utc) < deadline
    old['continuation_history'].append(old['continuation'])
    old['limits']['frontend_build'] = 7
    old['continuation'] = {
        'permit': permit['permit'], 'received_utc': begin_utc.isoformat(), 'received_monotonic_ns': begin_ns,
        'anchor_basis': '首工具没有同步mono；首次同步.NET QPC/UTC采样前保守扣300秒，包含全部前置读取和首条无副作用路径错误；不追认精确首点',
        'first_synchronous_sample': {'utc': sampled_utc.isoformat(), 'mono_ns': sampled_ns},
        'active_limit_seconds': 10800, 'calendar_limit_seconds': (deadline - begin_utc).total_seconds(),
        'calendar_hard_deadline_utc': deadline.isoformat(), 'previous_C02_active_seconds': 9188.720111,
        'active_segments': [{'begin_utc': begin_utc.isoformat(), 'begin_ns': begin_ns, 'end_ns': None,
                             'reason': 'C03接收读取、实现、验证、等待、报告连续计时'}],
        'real_batches': [], 'pause': None, 'status': 'accepted_implementation',
        'model': 'Codex desktop / GPT-6；具体后端子型号未披露；A+为资源标签',
        'baseline_counts': dict(old['counts']), 'baseline_offline_seconds': old['offline_seconds'],
        'baseline_holding_seconds': old['real_holding_seconds'], 'max_post_counts': permit['max_post_counts_this_round'],
        'offline_round_max': 1800, 'holding_round_max': 600, 'holding_business_round_max': 480,
        'old_stopped_basis': 'C02 closure/final delivery与主控/115保存的metadata；本轮未启动Docker，也未冒称今天重查容器',
        'new_PG_SQL_API_Vite_Native_preview_provider_fees_public_network': 0,
    }
    from budget import Budget
    budget = Budget(); budget.save(old)
    accepted = {'utc': datetime.now(timezone.utc).isoformat(), 'mono_ns': current_ns,
                'input_verified': len(manifest['current']), 'rules_verified': len(manifest['rules']),
                'permit': permit['permit'], 'consumer_new_started': 0,
                'preflight_failures': [{'kind': 'command_path', 'argv': '.venv/Scripts/python.exe -c clock sample',
                                       'exit': 1, 'effect': '路径不存在，未执行python或任何测试/消费者'},
                                      {'kind': 'bootstrap_manifest_shape', 'exit': 1, 'error': "KeyError: path",
                                       'effect': '规则对象使用relative_path/absolute_path；失败发生在目录/账写入前；改为核锁定snapshot绝对路径与同SHA相对映射'}],
                'rule_path_resolution': '规则对象使用absolute_path而不是path，核同relative_path/SHA的锁定七绝对路径；input绝对路径本身正常，先前终端乱码来自Python stdout编码显示',
                'anchor': old['continuation'], 'prior_events': identity(pre / 'events.jsonl')}
    (EVIDENCE / 'accepted.json').write_text(json.dumps(accepted, ensure_ascii=False, indent=2), encoding='utf-8')
    budget.event('c03.accepted', accepted)
    print(json.dumps({'accepted': permit['permit'], 'current_entries': len(manifest['current']), 'new_consumers': 0}))
    return 0


if __name__ == '__main__': sys.exit(main())
