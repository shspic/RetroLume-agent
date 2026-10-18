"""复用已写入的全部Git对象，只审扫描期间变化的八项，封存该时点完整公开树。"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
assert not (HERE / 'full-commit.json').exists()
original_raw = (HERE / 'full-manifest.json').read_bytes()
manifest = json.loads(original_raw)
drift = json.loads((HERE / 'full-drift.json').read_text(encoding='utf-8'))
assert len(drift) == 8 and not manifest['critical_product_findings'] and not manifest['oversized_remaining']
assert hashlib.sha256((ROOT / '.gitignore').read_bytes()).hexdigest() == manifest['gitignore_sha256']
index_path = HERE / 'full-public.index'
assert not index_path.exists()
env = dict(os.environ)
env.update(GIT_INDEX_FILE=str(index_path), GIT_OPTIONAL_LOCKS='0', GIT_TERMINAL_PROMPT='0',
           GIT_AUTHOR_NAME='shspic', GIT_COMMITTER_NAME='shspic',
           GIT_AUTHOR_EMAIL='276894097+shspic@users.noreply.github.com',
           GIT_COMMITTER_EMAIL='276894097+shspic@users.noreply.github.com')


def git(*args, input=None, original_index=False):
    git_env = dict(env)
    if original_index:
        git_env.pop('GIT_INDEX_FILE', None)
    result = subprocess.run(['git', '-c', 'core.longpaths=true', *args], cwd=ROOT, env=git_env,
                            input=input, capture_output=True, timeout=120)
    assert result.returncode == 0 or (args[0] == 'check-ignore' and result.returncode == 1), (args[0], result.returncode)
    return result.stdout


old_commit = git('rev-parse', 'HEAD').decode().strip()
assert old_commit == '45951501d2741630a229762d6b2d3f4b34d7f702'
assert not git('diff', '--cached', '--name-only', original_index=True).strip()
original_index_hash = hashlib.sha256((ROOT / '.git/index').read_bytes()).hexdigest()
assert not git('for-each-ref', '--format=%(refname)', 'refs/heads/codex/github-sync-full-20261018').strip()
rows = {row['path']: row for row in manifest['files']}
patterns = [
    re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
    re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{35,})\b'),
    re.compile(rb'\bsk-[A-Za-z0-9_-]{24,}\b'),
    re.compile(rb'\bAKIA[0-9A-Z]{16}\b'),
    re.compile(rb'(?:postgres(?:ql)?|mysql|mariadb)://[^\s\"\x27<>/@:]+:([^\s\"\x27<>/@]+)@', re.I),
    re.compile(rb'''(?i)authorization[\"\x27]?\s*[:=]\s*[\"\x27](?:Bearer|Basic)\s+([A-Za-z0-9+/=_-]{16,})'''),
]
secret_field = re.compile(rb'''(?i)[\"\x27](?:api_key|secret_key|access_token|review_key|hmac_key|control_key|password|passwd|pwd)[\"\x27]\s*:\s*[\"\x27]([^\"\x27\r\n]{6,})[\"\x27]''')
for item in drift:
    row = rows[item['path']]
    assert row['blob_sha1'] == item['manifest_blob']
    raw = git('cat-file', 'blob', item['current_blob'])
    assert hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == item['current_blob']
    checks = patterns + ([secret_field] if item['path'].endswith(('.json', '.jsonl')) else [])
    assert not any(pattern.search(raw) for pattern in checks), '变化文件存在待核私有字段，仅停止对应发布，不输出值'
    row.update(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(), blob_sha1=item['current_blob'])
previous_review = json.loads((HERE / 'full-reviewed-manifest.json').read_text(encoding='utf-8')) if (HERE / 'full-reviewed-manifest.json').exists() else None
manifest.update(prepared_at=previous_review['prepared_at'] if previous_review else datetime.now(timezone.utc).isoformat(),
                bytes=sum(row['bytes'] for row in manifest['files']),
                original_manifest_sha256=hashlib.sha256(original_raw).hexdigest(),
                ongoing_engineering_snapshot=True, changed_during_scan_frozen_from_git_objects=drift,
                changed_object_private_findings=0,
                snapshot_claim='扫描时已有文件集合；8个在途改动按Git读取时原字节固定，不追赶之后的活动写入')
reviewed_raw = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
if previous_review:
    assert (HERE / 'full-reviewed-manifest.json').read_bytes() == reviewed_raw
else:
    with (HERE / 'full-reviewed-manifest.json').open('xb') as stream:
        stream.write(reviewed_raw)
# 前一批hash-object -w已逐项确认实际存储的全部OID；本轮8项已从Git对象读回并重算。
# 不重复进行66000对象的批量header查询；该冗余查询在Windows上120秒超时，未动index/ref。
print(json.dumps({'phase': 'reuse_verified_object_hashes', 'files': manifest['count'], 'changed_blobs_rechecked': 8}), flush=True)
assert not git('check-ignore', '--no-index', '--stdin', '-z', input=b'\0'.join(row['path'].encode('utf-8') for row in manifest['files']) + b'\0')
git('read-tree', '--empty')
git('update-index', '-z', '--index-info', input=b''.join(row['mode'].encode() + b' ' + row['blob_sha1'].encode() + b'\t' + row['path'].encode('utf-8') + b'\0' for row in manifest['files']))
tree = git('write-tree').decode().strip()
expected = {row['path']: (row['mode'], row['blob_sha1']) for row in manifest['files']}
actual = {}
for item in git('ls-tree', '-r', '-z', tree).split(b'\0'):
    if not item:
        continue
    header, name = item.split(b'\t', 1)
    mode, kind, oid = header.decode().split()
    assert kind == 'blob'
    actual[name.decode('utf-8')] = (mode, oid)
assert actual == expected
commit = git('commit-tree', tree, input=b'chore: synchronize all nonignored RetroLume project files\n\nPublic project snapshot explicitly authorized by user. Preserve private history locally; apply .gitignore to credentials and runtime data.\nDevelopment snapshot while TASK-120 is active, not a release.\n').decode().strip()
assert not any(line.startswith(b'parent ') for line in git('cat-file', '-p', commit).split(b'\n\n', 1)[0].splitlines())
assert git('rev-list', '--count', commit).strip() == b'1'
assert hashlib.sha256((ROOT / '.git/index').read_bytes()).hexdigest() == original_index_hash
assert git('rev-parse', 'HEAD').decode().strip() == old_commit
git('update-ref', 'refs/heads/codex/github-sync-full-20261018', commit, '0' * 40)
record = {'at': datetime.now(timezone.utc).isoformat(), 'repository': 'shspic/RetroLume-agent',
          'local_public_branch': 'codex/github-sync-full-20261018', 'commit': commit, 'tree': tree, 'parents': [],
          'files': manifest['count'], 'bytes': manifest['bytes'], 'all_tree_modes_and_blob_hashes_match': True,
          'full_manifest_sha256': hashlib.sha256(reviewed_raw).hexdigest(),
          'manifest_path': 'DocuN/evidence/github-sync-20261018/full-reviewed-manifest.json',
          'gitignore_sha256': manifest['gitignore_sha256'], 'all_nonignored_project_files_scope': True,
          'user_explicitly_authorized_public_full_scope': True, 'local_private_HEAD_and_index_unchanged': True,
          'old_local_commit_preserved': old_commit, 'snapshot_frozen_while_engineering_active': True,
          'eight_changed_files_sealed_from_already_captured_objects': True, 'remote_written': False}
with (HERE / 'full-commit.json').open('x', encoding='utf-8') as stream:
    json.dump(record, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps(record, ensure_ascii=False), flush=True)
