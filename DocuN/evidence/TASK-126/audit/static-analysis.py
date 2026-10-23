"""TASK-126 自编只读分析器。只解析文本与文件元数据，不导入产品。"""
import ast
import ctypes
import difflib
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
OUT = ROOT / 'DocuN/evidence/TASK-126/audit'


def read(relative):
    path = ROOT / relative
    for parent in (*reversed(path.parents), path):
        info = parent.lstat()
        if info.st_file_attributes & 0x400:
            raise ValueError('reparse boundary: ' + str(parent))
    return path.read_bytes()


def constants(relative, names):
    tree = ast.parse(read(relative).decode('utf-8-sig'), filename=relative)
    found = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in names:
                    found[target.id] = ast.literal_eval(node.value)
    return found


manifest = json.loads(read('deploy/normal_install_manifest.json'))
entry = constants('deploy/initialize_normal.py', {'MIGRATIONS', 'GLOBAL_ROLES', 'BUSINESS_GROUPS', 'SNAPSHOT_GROUPS', 'PROFILE', 'MANIFEST_SHA256'})
schema = constants('backend/app/data_exit/schema.py', {'MIGRATIONS', 'MIGRATION_013'})
profiles = constants('backend/app/data_exit/schema_profiles.py', {'MIGRATION_014', 'MIGRATION_015', 'VECTOR_EXTENSION_VERSION'})
chain = {**schema['MIGRATIONS'], '013_data_exit.sql': schema['MIGRATION_013'],
         '014_step018_retrieval.sql': profiles['MIGRATION_014'], '015_activity_scope_delete_permission.sql': profiles['MIGRATION_015']}
import re
rows = []
roles = []
for row in manifest['migrations']:
    raw = read(row['path'])
    body = raw.decode('utf-8-sig')
    names = re.findall(r'\bCREATE\s+ROLE\s+(\w+)', body, re.I)
    roles.extend(names)
    code_lines = [line.strip() for line in body.splitlines() if line.strip() and not line.lstrip().startswith('--')]
    rows.append({'path': row['path'], 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
                 'manifest_match': hashlib.sha256(raw).hexdigest() == row['sha256'] and len(raw) == row['bytes'],
                 'profile_match': chain.get(Path(row['path']).name) == row['sha256'],
                 'first_code_line': code_lines[0], 'last_code_line': code_lines[-1],
                 'created_roles': names, 'utf8_bom': raw.startswith(b'\xef\xbb\xbf')})

old = read('DocuN/evidence/TASK-125/execution/pre/README.md').decode('utf-8-sig').splitlines()
new = read('README.md').decode('utf-8-sig').splitlines()
readme_diff = '\n'.join(difflib.unified_diff(old, new, fromfile='pre/README.md', tofile='README.md', lineterm='')) + '\n'
(OUT / 'readme-independent.diff').write_text(readme_diff, encoding='utf-8')

patch_lines = read('DocuN/evidence/TASK-125/execution/changes.patch').decode('utf-8-sig').splitlines()
patch_rows = []
pos = 0
while pos < len(patch_lines):
    if not patch_lines[pos].startswith('--- '):
        pos += 1
        continue
    before_name = patch_lines[pos][4:]
    after_name = patch_lines[pos + 1][6:]
    end = pos + 2
    while end < len(patch_lines) and not patch_lines[end].startswith('--- '):
        end += 1
    block = patch_lines[pos + 2:end]
    if before_name == '/dev/null':
        added = [line[1:] for line in block if line.startswith('+')]
        current = read(after_name).decode('utf-8-sig').splitlines()
        patch_rows.append({'path': after_name, 'pre_existed': False, 'patch_text_matches_current': added == current, 'lines': len(current)})
    else:
        patch_rows.append({'path': after_name, 'pre_existed': True,
                           'patch_text_matches_independent_diff': patch_lines[pos:end] == readme_diff.splitlines()})
    pos = end

aliases = []
if os.name == 'nt':
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    for name in ('GetShortPathNameW', 'GetLongPathNameW'):
        func = getattr(kernel, name)
        func.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint]
        func.restype = ctypes.c_uint
    for relative in ('', 'backend', 'deploy', 'config'):
        full = str(ROOT / relative)
        short_buffer = ctypes.create_unicode_buffer(32768)
        long_buffer = ctypes.create_unicode_buffer(32768)
        length = kernel.GetShortPathNameW(full, short_buffer, len(short_buffer))
        long_length = kernel.GetLongPathNameW(short_buffer.value, long_buffer, len(long_buffer)) if length else 0
        hypothetical = PureWindowsPath(short_buffer.value) / 'audit-hypothetical-not-created.json'
        protected = [PureWindowsPath(str(ROOT / part)) for part in ('backend', 'deploy', 'config', '.git', '.agents', '.codex')]
        aliases.append({'path': full, 'short_path': short_buffer.value if length else None,
                        'long_path': long_buffer.value if long_length else None,
                        'short_name_available': bool(length), 'hypothetical_new_output': str(hypothetical),
                        'lexically_inside_protected': any(hypothetical.is_relative_to(p) for p in protected),
                        'file_created': False})

data = {'analysis_kind': 'AST literals, exact bytes and text diff; no product execution',
        'migrations': rows, 'manifest_order_matches_entry': [Path(r['path']).name for r in rows] == list(entry['MIGRATIONS']),
        'manifest_hash_matches_entry': hashlib.sha256(read('deploy/normal_install_manifest.json')).hexdigest() == entry['MANIFEST_SHA256'],
        'global_roles_match_original_sql': set(roles) == set(entry['GLOBAL_ROLES']) and len(roles) == len(entry['GLOBAL_ROLES']),
        'global_roles_from_sql': roles, 'patch_files': patch_rows, 'ntfs_alias_metadata': aliases,
        'readme_pre_sha256': hashlib.sha256(read('DocuN/evidence/TASK-125/execution/pre/README.md')).hexdigest()}
(OUT / 'static-analysis.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: data[k] for k in ('manifest_order_matches_entry', 'manifest_hash_matches_entry', 'global_roles_match_original_sql', 'patch_files', 'ntfs_alias_metadata')}, ensure_ascii=False, indent=2))
