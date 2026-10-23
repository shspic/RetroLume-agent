"""补足动态角色、差异标签及证据交叉绑定；不执行任何产品或测试。"""
import ast
import datetime
import hashlib
import json
import os
from pathlib import Path
import re

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
OUT = ROOT / 'DocuN/evidence/TASK-126/audit'
EX = 'DocuN/evidence/TASK-125/execution/'


def read(relative):
    path = ROOT / relative
    for item in (*reversed(path.parents), path):
        info = item.lstat()
        if getattr(info, 'st_file_attributes', 0) & 0x400:
            raise ValueError('reparse boundary: ' + str(item))
    return path.read_bytes()


def load(relative):
    return json.loads(read(relative).decode('utf-8-sig'))


first = load('DocuN/evidence/TASK-126/audit/static-analysis.json')
installer_tree = ast.parse(read('deploy/initialize_normal.py').decode('utf-8-sig'))
literal_globals = {}
for node in installer_tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        if node.targets[0].id in ('GLOBAL_ROLES', 'STAGES', 'BUSINESS_GROUPS'):
            try:
                literal_globals[node.targets[0].id] = ast.literal_eval(node.value)
            except ValueError:
                pass

sql012 = read('backend/migrations/012_html_explanations.sql').decode('utf-8-sig')
dynamic = re.search(r"FOREACH name IN ARRAY ARRAY\[([^\]]+)\] LOOP", sql012)
dynamic_roles = re.findall(r"'([a-z_]+)'", dynamic.group(1))
all_roles = first['global_roles_from_sql'] + dynamic_roles
old = read(EX + 'pre/README.md').splitlines(keepends=True)
new = read('README.md').splitlines(keepends=True)
patch = read(EX + 'changes.patch').decode('utf-8-sig').splitlines()
index = patch.index('--- a/README.md')
independent = read('DocuN/evidence/TASK-126/audit/readme-independent.diff').decode('utf-8-sig').splitlines()

tested01 = {r['path']: r for r in load(EX + 'tested-before-batch-01.json')}
tested02 = {r['path']: r for r in load(EX + 'tested-before-batch-02.json')}
post = {r['path']: r for r in load(EX + 'post-snapshot.json')['products']}
products = []
for rel, row in tested02.items():
    current = read(rel)
    copy = read(EX + 'post/' + rel)
    products.append({'path': rel, 'bytes': len(current), 'sha256': hashlib.sha256(current).hexdigest(),
                     'batch02_and_post_metadata_and_copy_match': len(current) == row['bytes'] == post[rel]['bytes'] and
                     hashlib.sha256(current).hexdigest() == row['sha256'] == post[rel]['sha256'] == hashlib.sha256(copy).hexdigest(),
                     'batch01_same_identity': tested01[rel]['sha256'] == row['sha256']})

tree = ast.parse(read('backend/tests/test_normal_install.py').decode('utf-8-sig'))
methods = sorted(n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith('test_'))
prefix_literals = []
for node in ast.walk(tree):
    if isinstance(node, ast.Constant) and isinstance(node.value, str) and '??' in node.value:
        prefix_literals.append({'line': node.lineno, 'repr': repr(node.value), 'codepoints': list(map(ord, node.value))})

batches = []
permit125 = load('DocuN/evidence/TASK-125/orchestration-20261022/permit.json')
for number in (1, 2):
    stem = EX + f'batch-{number:02d}'
    command = load(stem + '-command.json')
    summary = load(stem + '-summary.json')
    output = read(stem + '-output.txt').decode('utf-8-sig')
    lines = output.splitlines()
    tests = [line for line in lines if re.match(r'^test_\d\d_', line)]
    started = datetime.datetime.fromisoformat(command['started_utc'])
    finished = started + datetime.timedelta(seconds=command['elapsed_seconds'])
    batches.append({'batch': number, 'output_test_count': len(tests), 'ok_lines': sum(line.endswith(' ... ok') for line in tests),
                    'fail_lines': sum(line.endswith(' ... FAIL') for line in tests), 'exit_code': command['exit_code'],
                    'summary_counts': {k: summary[k] for k in ('tests_run', 'failures', 'errors', 'skipped')},
                    'output_method_names_match_AST': sorted(line.split(' ')[0] for line in tests) == methods,
                    'summary_method_names_match_AST': sorted(r['test'].rsplit('.', 1)[-1] for r in summary['records']) == methods,
                    'started': started.isoformat(), 'finished': finished.isoformat(),
                    'within_calendar': datetime.datetime.fromisoformat(permit125['issued_at']) <= started <= finished <= datetime.datetime.fromisoformat(permit125['deadline']),
                    'process_elapsed_seconds': command['elapsed_seconds'], 'process_within_600': command['elapsed_seconds'] < 600,
                    'harness_elapsed_seconds': summary['elapsed_seconds'], 'denied_effect_attempts': summary['denied_effect_attempts']})

pre = load(EX + 'pre-snapshot.json')
preservation = load(EX + 'source-preservation.json')
pre_sources = {r['path']: r for r in pre['sources']}
preservation_rows = [{'path': row['path'], 'allowed_change': row['allowed_change'],
                      'metadata_matches_pre': row['sha256'] == pre_sources[row['path']]['sha256'],
                      'author_matches_pre_flag': row['matches_pre']} for row in preservation]
driver = []
for name in ('connection.py', '_connection_base.py', '_conninfo_attempts.py', '_conninfo_utils.py'):
    rel = 'backend/.venv/Lib/site-packages/psycopg/' + name
    raw = read(rel)
    driver.append({'path': rel, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})

aliases = []
for row in first['ntfs_alias_metadata']:
    if not row['short_name_available']:
        continue
    path = Path(row['short_path'])
    attrs = [{'path': str(p), 'reparse': bool(p.lstat().st_file_attributes & 0x400)} for p in (*reversed(path.parents), path)]
    aliases.append({**row, 'ancestors': attrs, 'hypothetical_output_exists': Path(row['hypothetical_new_output']).exists()})

link = ROOT / (EX + 'scratch/junction-fixture/link')
link_info = link.lstat()
junction = {'path': str(link), 'reparse': bool(link_info.st_file_attributes & 0x400), 'target_from_readlink': os.readlink(link),
            'followed_or_created_or_deleted': False}

data = {'analysis_kind': '只读 AST/JSON/文件元数据与差异核对，无产品导入或运行',
        'corrected_initial_analyzer_limitations': {
            'global_roles_initial_false': '初次正则仅捕获字面 CREATE ROLE，未计012原 SQL中 FOREACH/format 创建的两个 HTML 组；不属于产品缺陷',
            'readme_patch_initial_false': '初次比较包含 a/b 与 pre 标签差异；改为独立比较相同 hunk，未发现正文差异'},
        'dynamic_roles_012': dynamic_roles, 'global_roles_match_complete_original_sql': set(all_roles) == set(literal_globals['GLOBAL_ROLES']) and len(all_roles) == len(literal_globals['GLOBAL_ROLES']),
        'readme_patch_hunk_matches': patch[index+2:] == independent[2:],
        'readme_other_original_bytes_preserved': old[:32] == new[:32] and old[33:] == new[33:],
        'products': products, 'methods_from_AST': methods, 'batches': batches, 'pre_products': pre['pre'],
        'source_preservation_metadata': preservation_rows, 'native_junction_prefix_literals': prefix_literals,
        'junction': junction, 'ntfs_aliases': aliases, 'installed_driver_readonly_sources': driver,
        'budget125': load(EX + 'command-ledger.json')['budget'], 'observed_at': datetime.datetime.now().astimezone().isoformat()}
(OUT / 'static-analysis-02.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'global_roles_match': data['global_roles_match_complete_original_sql'], 'readme_hunk_matches': data['readme_patch_hunk_matches'],
                  'readme_other_bytes_preserved': data['readme_other_original_bytes_preserved'], 'products': products,
                  'batches': batches, 'source_preservation_count': len(preservation_rows),
                  'source_preservation_changes': [r for r in preservation_rows if not r['metadata_matches_pre']],
                  'junction_prefix': prefix_literals, 'junction': junction}, ensure_ascii=False, indent=2))
