"""用独立index建立公开根提交，不切换HEAD、不覆盖工程或原暂存区、不推送。"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SNAPSHOT = HERE / 'public-tree'
assert ROOT == Path('D:/shspic/project_NO3_RetroLume-agent').resolve()
assert not (HERE / 'commit.json').exists(), '已有提交证明，先核对，不重复提交'
manifest_raw = (HERE / 'reviewed-manifest.json').read_bytes()
manifest = json.loads(manifest_raw)
assert manifest['critical_findings'] == 0 and manifest['source_drift_after_copy'] == []
assert manifest['count'] == len(manifest['files']) and manifest['count'] > 1000
branch = 'codex/github-sync-20261018'
index_path = HERE / 'public.index'
assert not index_path.exists()
original_index = (ROOT / '.git/index').read_bytes()
original_head = (ROOT / '.git/HEAD').read_bytes()
original_ref = (ROOT / '.git/refs/heads/main').read_bytes()
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
                     'stdout_bytes': len(result.stdout), 'stderr': result.stderr.decode('utf-8', 'replace')[:3000]})
    if result.returncode:
        (HERE / 'git-error.json').write_text(json.dumps(commands, ensure_ascii=False, indent=2), encoding='utf-8')
        raise RuntimeError(f'Git命令失败 exit={result.returncode}: {args[0]}')
    return result.stdout


assert git('rev-parse', 'HEAD').decode().strip() == '45951501d2741630a229762d6b2d3f4b34d7f702'
refs = git('for-each-ref', '--format=%(refname)', 'refs/heads/' + branch).decode().strip()
assert not refs, '公开分支已存在，禁止覆盖'
expected = {}
path_lines = []
for row in manifest['files']:
    relative = row['path']
    assert not relative.startswith(('DocuN/', 'DocuS/', 'Ndocu/', 'docu/', 'evidence/', 'spikes/', '.runtime/'))
    assert '\n' not in relative and '\r' not in relative
    path = SNAPSHOT / relative
    assert path.resolve().is_relative_to(SNAPSHOT.resolve())
    raw = path.read_bytes()
    assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], relative
    object_id = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    expected[relative] = (row['mode'], object_id)
    path_lines.append(json.dumps(path.resolve().as_posix(), ensure_ascii=False))
blob_ids = git('hash-object', '-w', '--no-filters', '--stdin-paths',
               input=('\n'.join(path_lines) + '\n').encode('utf-8')).decode().splitlines()
assert len(blob_ids) == manifest['count']
for row, object_id in zip(manifest['files'], blob_ids):
    assert expected[row['path']][1] == object_id, row['path']
git('read-tree', '--empty')
entries = b''.join(mode.encode() + b' ' + oid.encode() + b'\t' + name.encode('utf-8') + b'\0'
                   for name, (mode, oid) in expected.items())
git('update-index', '-z', '--index-info', input=entries)
tree = git('write-tree').decode().strip()
actual = {}
for entry in git('ls-tree', '-r', '-z', tree).split(b'\0'):
    if not entry: continue
    head, name = entry.split(b'\t', 1)
    mode, kind, oid = head.decode().split()
    assert kind == 'blob'
    actual[name.decode('utf-8')] = (mode, oid)
assert actual == expected, '公开树与已审清单不一致'
message = ("chore: publish RetroLume development source snapshot\n\n"
           "Include application sources, migrations, lockfiles, portable tests, configuration examples and third-party notices.\n"
           "Exclude local credentials, user data, internal orchestration evidence, build caches and private history.\n"
           "This is a development snapshot, not a production release or paid-service activation.\n")
commit = git('commit-tree', tree, input=message.encode('utf-8')).decode().strip()
header = git('cat-file', '-p', commit).split(b'\n\n', 1)[0]
assert not any(line.startswith(b'parent ') for line in header.splitlines()), '不得带本地私有父历史'
assert git('rev-list', '--count', commit).decode().strip() == '1'
assert (ROOT / '.git/index').read_bytes() == original_index
assert (ROOT / '.git/HEAD').read_bytes() == original_head
assert (ROOT / '.git/refs/heads/main').read_bytes() == original_ref
git('update-ref', 'refs/heads/' + branch, commit, '0' * 40)
assert (ROOT / '.git/index').read_bytes() == original_index
assert (ROOT / '.git/HEAD').read_bytes() == original_head
assert (ROOT / '.git/refs/heads/main').read_bytes() == original_ref
proof = {'at': datetime.now(timezone.utc).isoformat(), 'repository': 'shspic/RetroLume-agent',
         'local_public_branch': branch, 'commit': commit, 'tree': tree, 'parents': [],
         'files': manifest['count'], 'bytes': manifest['bytes'], 'all_tree_modes_and_blob_hashes_match': True,
         'reviewed_manifest_sha256': hashlib.sha256(manifest_raw).hexdigest(),
         'local_private_HEAD_main_and_index_unchanged': True, 'old_local_commit_preserved': '45951501d2741630a229762d6b2d3f4b34d7f702',
         'author_email_kind': 'GitHub noreply, no private email', 'remote_written': False, 'commands': commands}
with (HERE / 'commit.json').open('x', encoding='utf-8') as stream:
    json.dump(proof, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps({key: proof[key] for key in ['local_public_branch', 'commit', 'tree', 'files', 'bytes',
      'parents', 'local_private_HEAD_main_and_index_unchanged', 'remote_written']}, ensure_ascii=False))
