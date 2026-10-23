"""主控只读核证：文件身份、现有回执和账目；不导入或运行产品。"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import time

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
E = ROOT / 'DocuN/evidence/TASK-120/execution'
assert ROOT == Path('D:/shspic/project_NO3_RetroLume-agent').resolve()
assert not (HERE / 'input-verification.json').exists(), '已有核证，先读断点，不重复'
start = time.monotonic()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


rules = []
for row in read_json(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json'):
    actual = sha(Path(row['absolute_path']))
    rules.append({'path': row['absolute_path'], 'sha256': actual, 'matches': actual == row['sha256']})
identities = read_json(E / 'final-file-identities.json')
sources = []
for row in identities['existing_files'] + identities['new_files']:
    path = ROOT / row['path']
    actual = sha(path) if path.is_file() else None
    sources.append({'path': row['path'], 'expected_sha256': row['after_sha256'], 'actual_sha256': actual,
                    'matches': actual == row['after_sha256']})
preimages = []
for row in identities['existing_files']:
    if row['changed'] and row.get('preimage'):
        path = E / row['preimage']
        actual = sha(path) if path.is_file() else None
        preimages.append({'path': row['path'], 'matches': actual == row['before_sha256'], 'sha256': actual})
bundle = []
for row in read_json(E / 'final-bundle-identities.json')['assets']:
    actual = sha(ROOT / row['path'])
    bundle.append({'path': row['path'], 'sha256': actual, 'matches': actual == row['sha256']})
package = read_json(E / 'final-review-files-identity.json')
package_actual = sha(E / package['path'])
receipts = []
for name in ['command-025.receipt.json', 'command-026.receipt.json', 'command-027.receipt.json', 'command-028.receipt.json']:
    value = read_json(E / name)
    receipts.append({'path': name, 'sha256': sha(E / name), 'exit_code': value['exit_code'],
                     'wall_seconds': value['wall_seconds'], 'tree_empty': value['tree_empty']})
budget = read_json(E / 'budget.json')
stop = read_json(E / 'final-stop-proof.json')
wall = sum(budget.get(key, 0) for key in ['pre_controller_wall_upper_seconds', 'controlled_command_wall_seconds',
                                        'runtime_command_wall_seconds', 'unwrapped_metadata_wall_reserved_seconds'])
assert budget['counts']['roots'] == budget['caps']['roots'] == 8
assert budget['counts']['frontend_builds'] == budget['caps']['frontend_builds'] == 4
assert budget['active_root'] is None and budget['active_command'] is None
assert stop['all_confirmed'] and not stop['container']['state']['Running'] and stop['container']['state']['Pid'] == 0
assert len(stop['jobs']) == 8 and all(x['active_processes'] == 0 for x in stop['jobs'])
assert len(stop['registered_processes']) == 23 and not any(x['same_birth_running'] for x in stop['registered_processes'])
assert not any(x['listening'] for x in stop['ports'].values())
old_paths = ['budget.json', 'events.jsonl', 'case-index.json', 'final-stop-proof.json', 'final-file-identities.json',
             'final-bundle-identities.json', 'source.diff', 'remaining-readiness.json',
             'root08-next-batch-timing.json', 'root08-unexecuted-next-batch.json', 'flow-committed-receipts.json']
input_paths = [ROOT / 'AGENTS.md', ROOT / 'DocuN/results/TASK-120-result.md', ROOT / 'DocuN/tasks/TASK-120.md',
               ROOT / 'DocuN/results/TASK-119-result.md', ROOT / 'DocuN/evidence/TASK-119/orchestration-acceptance-20261018/adoption-proposal.md']
input_paths += [E / name for name in old_paths]
manifest = [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p), 'bytes': p.stat().st_size} for p in input_paths]
evidence_class = []
for name in ['root-08-batch-01-as-run.json', 'root-08-batch-02-as-run.json']:
    rows = read_json(E / name)['files']
    differences = [row['path'] for row in rows if (ROOT / row['path']).is_file() and sha(ROOT / row['path']) != row['sha256']]
    evidence_class.append({'path': name, 'current_differences': differences,
                           'product_differences': [p for p in differences if p.startswith(('backend/app/', 'frontend/src/'))]})
result = {'at': datetime.now(timezone.utc).isoformat(), 'task': 'TASK-120', 'R': 'R-114',
          'rules': rules, 'source_count': len(sources), 'sources': sources, 'changed_preimages': preimages,
          'bundle': bundle, 'package_matches': package_actual == package['sha256'],
          'package_sha256': package_actual, 'receipts': receipts, 'inputs': manifest,
          'budget': {'counts': budget['counts'], 'caps': budget['caps'], 'failures': len(budget['failures']),
                     'actual_first_tool_utc': budget['actual_first_tool_utc'], 'calendar_deadline_utc': budget['calendar_deadline_utc'],
                     'command_wall_upper_seconds': wall, 'holding_union_seconds': budget['runtime_holding_union_seconds'],
                     'active_root': None, 'active_command': None},
          'stop_evidence_at': stop['utc'], 'old_six_realtime_observation': 'not_claimed',
          'stop_is_historical_not_a_new_Docker_query': True, 'root08_as_run': evidence_class,
          'main_product_import_compile_test_build_SQL_Docker_API_browser_model_Git_mutations': 0,
          'wall_seconds': time.monotonic() - start}
with (HERE / 'input-verification.json').open('x', encoding='utf-8') as stream:
    json.dump(result, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps({'rules': len(rules), 'rules_match': all(x['matches'] for x in rules),
                  'source_count': len(sources), 'source_drift': [x['path'] for x in sources if not x['matches']],
                  'preimage_drift': [x['path'] for x in preimages if not x['matches']],
                  'bundle_match': all(x['matches'] for x in bundle), 'package_match': result['package_matches'],
                  'budget': result['budget'], 'as_run': evidence_class, 'wall_seconds': result['wall_seconds']}, ensure_ascii=False))
assert all(x['matches'] for x in rules + sources + preimages + bundle) and result['package_matches']
