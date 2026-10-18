"""只提交本次同步的共享说明和Git元数据，不纳入仍在执行的TASK120后续写入。"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import subprocess

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PRIVATE = ROOT / '.runtime/github-sync-20261018'
assert not (PRIVATE / 'management-commit.json').exists()
root_proof = json.loads((HERE / 'full-commit.json').read_text(encoding='utf-8'))
env = dict(os.environ)
env.pop('GIT_INDEX_FILE', None)
env.update(GIT_OPTIONAL_LOCKS='0', GIT_TERMINAL_PROMPT='0', GIT_AUTHOR_NAME='shspic', GIT_COMMITTER_NAME='shspic',
           GIT_AUTHOR_EMAIL='276894097+shspic@users.noreply.github.com', GIT_COMMITTER_EMAIL='276894097+shspic@users.noreply.github.com')


def git(*args, input=None):
    result = subprocess.run(['git', '-c', 'core.longpaths=true', '-c', 'gc.auto=0', '-c', 'maintenance.auto=false',
                             *args], cwd=ROOT, env=env, input=input, capture_output=True, timeout=120)
    assert result.returncode == 0 or (args[0] == 'check-ignore' and result.returncode == 1), (args[0], result.stderr.decode('utf-8', 'replace')[:1500])
    return result.stdout


assert git('rev-parse', 'HEAD').decode().strip() == root_proof['commit']
paths = ['.gitignore', 'README.md', 'DocuS/执行动态文档.MD', 'DocuS/文档变更记录.MD',
         'DocuN/results/GITHUB-SYNC-20261018-result.md', 'DocuN/evidence/github-sync-20261018']
already_staged = [p.decode('utf-8') for p in git('diff', '--cached', '--name-only', '-z').split(b'\0') if p]
assert all(p in paths or p.startswith('DocuN/evidence/github-sync-20261018/') for p in already_staged)
git('add', '--', *paths)
staged = [p.decode('utf-8') for p in git('diff', '--cached', '--name-only', '-z').split(b'\0') if p]
assert staged and all(p in paths or p.startswith('DocuN/evidence/github-sync-20261018/') for p in staged)
assert not any('/public-tree/' in p or '/full-public-tree/' in p or p.endswith('.index') for p in staged)
assert not git('check-ignore', '--no-index', '--stdin', '-z', input=b'\0'.join(p.encode('utf-8') for p in staged) + b'\0')
tree = git('write-tree').decode().strip()
commit = git('commit-tree', tree, '-p', root_proof['commit'],
             input=b'docs: record authorized full-project GitHub synchronization\n').decode().strip()
git('update-ref', 'refs/heads/main', commit, root_proof['commit'])
assert git('rev-parse', 'HEAD').decode().strip() == commit
assert git('rev-parse', 'HEAD^').decode().strip() == root_proof['commit']
assert git('rev-list', '--count', 'HEAD').strip() == b'2'
proof = {'at': datetime.now(timezone.utc).isoformat(), 'management_commit': commit,
         'parent_public_root': root_proof['commit'], 'staged_files': staged,
         'product_changes_staged': False, 'scope': 'this Git sync metadata and shared docs only',
         'current_state_sha256': hashlib.sha256((ROOT / 'DocuS/执行动态文档.MD').read_bytes()).hexdigest(),
         'staged_ignored_files': False, 'old_private_parent_in_public_history': False}
PRIVATE.mkdir(parents=True, exist_ok=True)
with (PRIVATE / 'management-commit.json').open('x', encoding='utf-8') as stream:
    json.dump(proof, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps({'management_commit': commit, 'files': len(staged), 'product_changes_staged': False}, ensure_ascii=False))
