"""将用户授权的全部非忽略文件建立为公开根提交；保持当前工作树和暂存区。"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
assert ROOT == Path('D:/shspic/project_NO3_RetroLume-agent').resolve()
assert not (HERE / 'full-commit.json').exists(), '先检查已保存提交，不重复执行'
manifest_raw = (HERE / 'full-manifest.json').read_bytes()
manifest = json.loads(manifest_raw)
assert not manifest['critical_product_findings'] and not manifest['oversized_remaining']
assert manifest['payload_authorization_is_explicit'] and manifest['count'] == len(manifest['files'])
assert hashlib.sha256((ROOT / '.gitignore').read_bytes()).hexdigest() == manifest['gitignore_sha256']
index_path = HERE / 'full-public.index'
assert not index_path.exists(), '独立index已存在，先核断点'
branch = 'codex/github-sync-full-20261018'
original_index = (ROOT / '.git/index').read_bytes()
original_head = (ROOT / '.git/HEAD').read_bytes()
env = dict(os.environ)
env.update({'GIT_INDEX_FILE': str(index_path), 'GIT_OPTIONAL_LOCKS': '0', 'GIT_TERMINAL_PROMPT': '0',
            'GIT_AUTHOR_NAME': 'shspic', 'GIT_COMMITTER_NAME': 'shspic',
            'GIT_AUTHOR_EMAIL': '276894097+shspic@users.noreply.github.com',
            'GIT_COMMITTER_EMAIL': '276894097+shspic@users.noreply.github.com'})
commands = []


def git(*args, input=None, timeout=120):
    cmd = ['git', '-c', 'core.longpaths=true', *args]
    start = time.monotonic()
    result = subprocess.run(cmd, cwd=ROOT, env=env, input=input, capture_output=True, timeout=timeout)
    commands.append({'args': cmd, 'exit': result.returncode, 'wall_seconds': time.monotonic() - start,
                     'stdout_bytes': len(result.stdout), 'stderr': result.stderr.decode('utf-8', 'replace')[:2000]})
    if result.returncode and not (args[0] == 'check-ignore' and result.returncode == 1):
        (HERE / 'full-git-error.json').write_text(json.dumps(commands, ensure_ascii=False, indent=2), encoding='utf-8')
        raise RuntimeError('Git命令失败: ' + args[0])
    return result.stdout


original_commit = git('rev-parse', 'HEAD').decode().strip()
assert original_commit == '45951501d2741630a229762d6b2d3f4b34d7f702'
assert not git('for-each-ref', '--format=%(refname)', 'refs/heads/' + branch).strip()
original_env = dict(env)
original_env.pop('GIT_INDEX_FILE', None)
staged = subprocess.run(['git', 'diff', '--cached', '--name-only'], cwd=ROOT, env=original_env,
                        capture_output=True, timeout=30)
assert staged.returncode == 0 and not staged.stdout.strip(), '已有暂存变动时不得干扰'
ignored = git('check-ignore', '--no-index', '--stdin', '-z',
              input=b'\0'.join(row['path'].encode('utf-8') for row in manifest['files']) + b'\0')
assert not ignored, '清单包含忽略文件'
expected = {}
drift = []
for offset in range(0, len(manifest['files']), 3000):
    batch = manifest['files'][offset:offset + 3000]
    paths = []
    for row in batch:
        name = row['path']
        assert not name.startswith(('.git/', '.runtime/')) and '\r' not in name and '\n' not in name
        path = ROOT / name
        assert path.resolve().is_relative_to(ROOT)
        paths.append(json.dumps(path.resolve().as_posix(), ensure_ascii=False))
    object_ids = git('hash-object', '-w', '--no-filters', '--stdin-paths',
                     input=('\n'.join(paths) + '\n').encode('utf-8')).decode().splitlines()
    assert len(object_ids) == len(batch)
    for row, oid in zip(batch, object_ids):
        if oid != row['blob_sha1']:
            drift.append({'path': row['path'], 'manifest_blob': row['blob_sha1'], 'current_blob': oid})
        expected[row['path']] = (row['mode'], row['blob_sha1'])
    print(json.dumps({'phase': 'hash_to_git', 'done': offset + len(batch), 'total': manifest['count'],
                      'changed_after_scan': len(drift)}), flush=True)
if drift:
    with (HERE / 'full-drift.json').open('x', encoding='utf-8') as stream:
        json.dump(drift, stream, ensure_ascii=False, indent=2)
    raise SystemExit('只需复核上述变动文件；未创建提交或覆盖原暂存区')
git('read-tree', '--empty')
entries = b''.join(mode.encode() + b' ' + oid.encode() + b'\t' + name.encode('utf-8') + b'\0'
                   for name, (mode, oid) in expected.items())
git('update-index', '-z', '--index-info', input=entries)
tree = git('write-tree').decode().strip()
actual = {}
for entry in git('ls-tree', '-r', '-z', tree).split(b'\0'):
    if not entry:
        continue
    header, name = entry.split(b'\t', 1)
    mode, kind, oid = header.decode().split()
    assert kind == 'blob'
    actual[name.decode('utf-8')] = (mode, oid)
assert actual == expected, '全文件Git树与授权清单不一致'
message = ('chore: synchronize all nonignored RetroLume project files\n\n'
           'User authorized this public repository snapshot including source, project documents, task cards, results and retained evidence.\n'
           'Apply .gitignore to credentials, private runtime data, browser profiles and generated oversized image caches.\n'
           'Start public history at the reviewed current snapshot; preserve previous local-only history separately.\n'
           'Development snapshot only; no product-release or paid-service activation.\n')
commit = git('commit-tree', tree, input=message.encode('utf-8')).decode().strip()
assert not any(line.startswith(b'parent ') for line in git('cat-file', '-p', commit).split(b'\n\n', 1)[0].splitlines())
assert git('rev-list', '--count', commit).strip() == b'1'
assert (ROOT / '.git/index').read_bytes() == original_index
assert (ROOT / '.git/HEAD').read_bytes() == original_head
assert git('rev-parse', 'HEAD').decode().strip() == original_commit
git('update-ref', 'refs/heads/' + branch, commit, '0' * 40)
proof = {'at': datetime.now(timezone.utc).isoformat(), 'repository': 'shspic/RetroLume-agent',
         'local_public_branch': branch, 'commit': commit, 'tree': tree, 'parents': [],
         'files': manifest['count'], 'bytes': manifest['bytes'], 'all_tree_modes_and_blob_hashes_match': True,
         'full_manifest_sha256': hashlib.sha256(manifest_raw).hexdigest(),
         'gitignore_sha256': manifest['gitignore_sha256'], 'all_nonignored_project_files_scope': True,
         'user_explicitly_authorized_public_full_scope': True,
         'local_private_HEAD_and_index_unchanged': True, 'old_local_commit_preserved': original_commit,
         'author_email_kind': 'GitHub noreply', 'remote_written': False, 'commands': commands}
with (HERE / 'full-commit.json').open('x', encoding='utf-8') as stream:
    json.dump(proof, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps({key: proof[key] for key in ['local_public_branch', 'commit', 'tree', 'files', 'bytes',
      'parents', 'local_private_HEAD_and_index_unchanged', 'remote_written']}, ensure_ascii=False), flush=True)
