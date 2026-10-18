"""编排只读回收；核文件与原日志，不执行产品、测试或资源变更。"""
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
BASE = ROOT / 'DocuN/evidence/TASK-100/continuation-02'
OUT = Path(__file__).parent


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def save(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


identity = load(BASE / 'final-file-identity.json')
sources = [{'path': rel, 'expected_sha256': expected, 'sha256': digest(ROOT / rel)}
           for mapping in (identity['source_files'], identity['dist']) for rel, expected in mapping.items()]
inventory = load(BASE / 'evidence-inventory.json')
evidence = []
for item in inventory['files']:
    path = BASE / item['path']
    evidence.append({'path': path.relative_to(ROOT).as_posix(), 'expected_sha256': item['sha256'],
                     'sha256': digest(path), 'bytes': path.stat().st_size if path.is_file() else None})
rules = [{'path': item['absolute_path'], 'expected_sha256': item['sha256'],
          'sha256': digest(Path(item['absolute_path']))}
         for item in load(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')]
verify = load(BASE / 'verification-index.json')
methods = []
for field in ('pg_distinct_passed_methods', 'http_methods'):
    for item in verify[field]:
        log = BASE / item['raw']
        text = log.read_text(encoding='utf-8', errors='replace')
        parts = item['method'].split('.')
        short = parts[-1]
        complete = '.'.join(parts[:-1]) + '.' + short
        all_lines = text.splitlines()
        lines = []
        blocks = []
        for index, line in enumerate(all_lines):
            if not (line.startswith(short + ' ') and complete in line):
                continue
            lines.append(line)
            block = [line]
            for successor in all_lines[index + 1:]:
                if successor.startswith('test_') or successor.startswith('-----'):
                    break
                block.append(successor)
            blocks.extend(block)
        methods.append({'method': item['method'], 'raw': log.relative_to(ROOT).as_posix(),
                        'ok_found': any(re.search(r'\.\.\. ok\s*$', line) for line in blocks),
                        'line_count': len(lines), 'log_sha256': digest(log)})
offline = BASE / verify['offline']['batch']
offline_summary = load(offline / 'summary.json')
offline_log = (offline / 'offline-raw/stderr.txt').read_text(encoding='utf-8', errors='replace')
batches = []
for directory in sorted(BASE.iterdir()):
    if not directory.is_dir() or not directory.name.endswith(('main-combo', 'preflight-refusal')):
        continue
    summary_path = directory / 'summary.json'
    cleanup_path = directory / 'cleanup.json'
    batches.append({'batch': directory.name, 'summary_exists': summary_path.is_file(),
                    'status': load(summary_path).get('status') if summary_path.is_file() else 'preflight_refusal',
                    'cleanup_exists': cleanup_path.is_file()})
artifacts = load(BASE / 'browser-final-artifact-verification.json')
artifact_checks = [{'path': rel, 'match': digest(BASE / rel) == expected}
                   for rel, expected in artifacts['sources'].items()]
permits = []
for name in verify['permits']:
    value = load(BASE / name)
    before_ledger = value.get('baseline_ledger_sha256')
    before_candidates = sorted(BASE.glob('attempt-ledger-before-*.json'))
    permits.append({'path': name, 'sha256': digest(BASE / name), 'additional_counts': value.get('additional_counts'),
                    'registered_at': value.get('registered_at'),
                    'baseline_ledger_bound': any(digest(p) == before_ledger for p in before_candidates),
                    'approval_text_has_replacement_characters': '\ufffd' in value.get('approval', ''),
                    'authority_scope': '执行者许可登记；不等同独立可读的用户原生批准全文'})
previous_path = OUT / 'receipt.json'
previous = load(previous_path) if previous_path.exists() else None
if previous is not None and not (OUT / 'receipt-initial-parser.json').exists():
    (OUT / 'receipt-initial-parser.json').write_bytes(previous_path.read_bytes())
resource = previous['live_resource'] if previous else {'operation': '只读inspect精确ID的State；未启动/停止/更新资源、连接数据库或应用'}
try:
    if previous is not None:
        raise StopIteration
    result = subprocess.run(['docker', 'inspect', '--format', '{{json .State}}',
                             '80ae914138fa42a9ae72acf898d13f7e740b759ff09fc248470abb6df0c15d4d'],
                            capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=15)
    resource['exit_code'] = result.returncode
    if result.returncode == 0:
        resource['state'] = json.loads(result.stdout)
    else:
        resource['state'] = '实时不可确认'
        resource['error'] = result.stderr[:700]
except StopIteration:
    pass
except Exception as exc:
    resource.update(state='实时不可确认', error_type=type(exc).__name__)
snapshot = {
    'at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
    'role': '编排普通回收核证；非独立审计，未执行产品验证',
    'sources': sources, 'evidence': evidence, 'rules': rules, 'raw_methods': methods,
    'offline_summary': offline_summary,
    'offline_log_has_58_tests_and_ok': bool(re.search(r'Ran 58 tests', offline_log) and re.search(r'^OK\s*$', offline_log, re.M)),
    'raw_batch_statuses': batches, 'artifact_checks': artifact_checks,
    'limits': verify['effective_limits'], 'counts': verify['counts'], 'seconds': verify['seconds'],
    'supplementary_permits': permits, 'live_resource': resource,
    'claimed_limits_not_removed': verify['not_run'] + verify['not_captured'],
    'conclusion': '候选回收，完整成果集中独立审计待执行；未重启main-combo或补写PASS',
    'result_sha256': digest(ROOT / 'DocuN/results/TASK-100-result.md'),
}
save('receipt.json', snapshot)
save('evidence-identity.json', {'files': evidence})
print(json.dumps({'sources': len(sources), 'source_mismatch': [x['path'] for x in sources if x['sha256'] != x['expected_sha256']],
                  'evidence': len(evidence), 'evidence_mismatch': [x['path'] for x in evidence if x['sha256'] != x['expected_sha256']],
                  'rules_match': all(x['sha256'] == x['expected_sha256'] for x in rules),
                  'method_checks': len(methods), 'methods_without_matching_ok': [x['method'] for x in methods if not x['ok_found']],
                  'offline_58_ok': snapshot['offline_log_has_58_tests_and_ok'],
                  'all_saved_browser_artifact_hashes_match': all(x['match'] for x in artifact_checks),
                  'supplementary_permit_baselines_bound': all(x['baseline_ledger_bound'] for x in permits),
                  'supplementary_approval_text_garbled': any(x['approval_text_has_replacement_characters'] for x in permits),
                  'live_container_running': resource.get('state', {}).get('Running') if isinstance(resource.get('state'), dict) else None,
                  'readiness': '回收事实已保存；逐方法或hash差异如有须先定界'}, ensure_ascii=False))
