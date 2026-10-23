"""只解析既有源码、差异和日志，不导入产品或执行测试。"""
import ast
import copy
import datetime
import difflib
import hashlib
import json
import os
from pathlib import Path
import re

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
OUT = ROOT / 'DocuN/evidence/TASK-126/audit/review-01'
EX = 'DocuN/evidence/TASK-125/execution/repair-01/'


def read(relative):
    path = ROOT / relative
    for item in (*reversed(path.parents), path):
        if getattr(item.lstat(), 'st_file_attributes', 0) & 0x400:
            raise ValueError('reparse boundary: ' + str(item))
    return path.read_bytes()


def load(relative):
    return json.loads(read(relative).decode('utf-8-sig'))


def dump(node):
    return ast.dump(node, include_attributes=False)


def methods(tree):
    return {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}


current_manifest = load('DocuN/evidence/TASK-126/orchestration-review01-20261022/input-manifest.json')
original = load('DocuN/evidence/TASK-126/audit/closure.json')
old_rows = {row['path']: row for row in original['final_input_checks']}
products = ['deploy/initialize_normal.py', 'backend/tests/test_normal_install.py', 'deploy/normal-install.md']
tested = load(EX + 'tested-before-batch-03.json')
post = load(EX + 'post-snapshot.json')
post_rows = {row['path']: row for row in post['tested_and_final_bytes']}
tested_rows = {row['path']: row for row in tested}
product_rows, independent_patch = [], []
for rel in products:
    old, current, saved = read(EX + 'pre/' + rel), read(rel), read(EX + 'post/' + rel)
    expected = tested_rows[rel]
    actual = hashlib.sha256(current).hexdigest()
    product_rows.append({'path': rel, 'bytes': len(current), 'sha256': actual,
                         'pre_matches_original_audited_bytes': hashlib.sha256(old).hexdigest() == old_rows[rel]['sha256'] and len(old) == old_rows[rel]['bytes'],
                         'current_matches_batch03_and_post': actual == expected['sha256'] == post_rows[rel]['sha256'] == post_rows[rel]['actual_post_sha256'] and len(current) == expected['bytes'],
                         'post_copy_exact': current == saved})
    independent_patch.extend(difflib.unified_diff(old.decode('utf-8-sig').splitlines(), current.decode('utf-8-sig').splitlines(),
                             fromfile='pre/' + rel, tofile='post/' + rel, lineterm=''))
patch_matches = independent_patch == read(EX + 'changes.patch').decode('utf-8-sig').splitlines()
(OUT / 'independent-changes.patch').write_text('\n'.join(independent_patch) + '\n', encoding='utf-8')

old_tree = ast.parse(read(EX + 'pre/deploy/initialize_normal.py').decode('utf-8-sig'))
new_tree = ast.parse(read('deploy/initialize_normal.py').decode('utf-8-sig'))
old_functions = {n.name: n for n in old_tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
new_functions = {n.name: n for n in new_tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
changed = [name for name in old_functions if dump(old_functions[name]) != dump(new_functions[name])]
old_rest = [n for n in old_tree.body if not isinstance(n, (ast.FunctionDef, ast.ClassDef))]
new_rest = [n for n in new_tree.body if not isinstance(n, (ast.FunctionDef, ast.ClassDef))]
old_tests = ast.parse(read(EX + 'pre/backend/tests/test_normal_install.py').decode('utf-8-sig'))
new_tests = ast.parse(read('backend/tests/test_normal_install.py').decode('utf-8-sig'))
old_methods, new_methods = methods(old_tests), methods(new_tests)
method_rows = [{'method': name, 'AST_unchanged': dump(node) == dump(new_methods[name])} for name, node in old_methods.items()]
new_names = sorted(set(new_methods) - set(old_methods))
stripped = copy.deepcopy(new_tests)
stripped.body = [n for n in stripped.body if not (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'REPAIR_OBSERVATIONS' for t in n.targets))]
for cls in [n for n in stripped.body if isinstance(n, ast.ClassDef)]:
    cls.body = [n for n in cls.body if not (isinstance(n, ast.FunctionDef) and n.name in new_names)]

selection = load(EX + 'batch-03-selection.json')
start = load(EX + 'batch-03-start.json')
command = load(EX + 'batch-03-command.json')
summary = load(EX + 'batch-03-summary.json')
output = read(EX + 'batch-03-output.txt').decode('utf-8-sig')
lines = [line for line in output.splitlines() if re.match(r'^test_\d\d_', line)]
names = [line.split(' ', 1)[0] for line in lines]
selected = selection['selected_methods']
bindings = [{'path': row['path'], 'sha256': hashlib.sha256(read(row['path'])).hexdigest(),
             'matches': hashlib.sha256(read(row['path'])).hexdigest() == row['sha256'] and len(read(row['path'])) == row['bytes']} for row in tested]

unchanged_dependencies = []
for rel, row in old_rows.items():
    if rel.startswith(('backend/migrations/', 'backend/app/data_exit/')) or rel in (
            'deploy/start_local.py', 'deploy/initialize-materials.py', 'deploy/compose.local.yml',
            'config/activity.example.json', 'config/integration.example.json', 'config/q-approval.example.json',
            'config/preview.example.json', 'config/data-exit.example.json'):
        raw = read(rel)
        unchanged_dependencies.append({'path': rel, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
                                       'same_as_original_audit': hashlib.sha256(raw).hexdigest() == row['sha256'] and len(raw) == row['bytes']})

fixture = load(EX + 'junction-before.json')
link = Path(fixture['path'])
for parent in reversed(link.parents):
    if getattr(parent.lstat(), 'st_file_attributes', 0) & 0x400:
        raise ValueError('reparse before fixture')
info = link.lstat()
fixture_now = {'path': str(link), 'device': info.st_dev, 'inode': info.st_ino, 'mtime_ns': info.st_mtime_ns,
               'reparse': bool(info.st_file_attributes & 0x400), 'readlink': os.readlink(link)}
fixture_now['matches_before'] = (info.st_dev, info.st_ino, info.st_mtime_ns, os.readlink(link)) == (
    fixture['link_device'], fixture['link_inode'], fixture['link_mtime_ns'], fixture['target_from_readlink'])
fixture_now['recursive_follow_create_delete'] = False

new_directories = []
allowed_scratch = ROOT / 'DocuN/evidence/TASK-125/execution/scratch'
for value in summary['new_directories']:
    path = Path(value)
    if not path.is_relative_to(allowed_scratch):
        raise ValueError('new case outside scratch')
    for item in (*reversed(path.parents), path):
        if getattr(item.lstat(), 'st_file_attributes', 0) & 0x400:
            raise ValueError('new case reparse')
    new_directories.append({'path': str(path), 'directory': path.is_dir()})

permit125 = load('DocuN/evidence/TASK-125/orchestration-repair01-20261022/permit.json')
started = datetime.datetime.fromisoformat(command['started_utc'])
finished = started + datetime.timedelta(seconds=command['elapsed_seconds'])
data = {'analysis_kind': '源码与日志只读核对, 不导入产品/驱动, 不运行测试', 'observed_at': datetime.datetime.now().astimezone().isoformat(),
        'product_bindings': product_rows, 'independent_patch_matches': patch_matches,
        'changed_product_functions': changed, 'unchanged_other_module_AST': [dump(n) for n in old_rest] == [dump(n) for n in new_rest],
        'original_methods': method_rows, 'new_methods': new_names, 'remaining_test_module_AST_unchanged': dump(old_tests) == dump(stripped),
        'batch03': {'selected_count': len(selected), 'actual_output_count': len(lines), 'all_ok': all(line.endswith(' ... ok') for line in lines),
                    'ordered_names_match': names == selected == summary['selected_methods'] == [r['test'].rsplit('.', 1)[-1] for r in summary['records']],
                    'summary_counts': {k: summary[k] for k in ('tests_run', 'failures', 'errors', 'skipped')}, 'exit_code': command['exit_code'],
                    'start_record_matches_command': all(command[k] == v for k, v in start.items()),
                    'selection_precedes_start': datetime.datetime.fromisoformat(selection['frozen_before_execution_utc']) < started,
                    'process_seconds': command['elapsed_seconds'], 'harness_seconds': summary['elapsed_seconds'],
                    'within_permit_and_600': datetime.datetime.fromisoformat(permit125['issued_at']) <= started <= finished <= datetime.datetime.fromisoformat(permit125['deadline']) and command['elapsed_seconds'] < 600,
                    'inherited_count': len(selection['inherited_without_rerun']),
                    'unique_total_current_methods': len(new_methods), 'tested_artifacts': bindings,
                    'observations': summary['observations']},
        'unchanged_dependency_hashes': unchanged_dependencies, 'fixture_lstat_readlink': fixture_now,
        'new_directory_metadata': new_directories,
        'engineering_budget_and_scope_notes': {k: load(EX + 'command-ledger.json')[k] for k in ('budget', 'tests', 'known_execution_note', 'historical_unknowns_retained')}}
(OUT / 'static-review.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'products': product_rows, 'patch_matches': patch_matches, 'changed_functions': changed,
                  'original_methods_unchanged': sum(r['AST_unchanged'] for r in method_rows), 'test_module_unchanged_except_additions': data['remaining_test_module_AST_unchanged'],
                  'new_methods': new_names, 'batch03': {k: v for k, v in data['batch03'].items() if k not in ('observations', 'tested_artifacts')},
                  'dependencies_unchanged': len(unchanged_dependencies) == sum(r['same_as_original_audit'] for r in unchanged_dependencies),
                  'dependency_count': len(unchanged_dependencies), 'fixture_unchanged': fixture_now['matches_before'], 'listed_directories': len(new_directories)}, ensure_ascii=False, indent=2))
