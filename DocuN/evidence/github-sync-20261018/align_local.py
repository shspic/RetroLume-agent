"""远端完整根提交已核实后整理本地main；旧私有历史保存在非推送命名空间。"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import subprocess

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
proof = json.loads((HERE / 'full-commit.json').read_text(encoding='utf-8'))
remote = json.loads((HERE / 'remote-main-verification.json').read_text(encoding='utf-8'))
assert remote['verified'] and remote['remote_main'] == proof['commit']
assert not (HERE / 'local-alignment.json').exists()
env = dict(os.environ)
env.pop('GIT_INDEX_FILE', None)
env.update(GIT_OPTIONAL_LOCKS='0', GIT_TERMINAL_PROMPT='0')


def git(*args):
    result = subprocess.run(['git', '-c', 'core.longpaths=true', *args], cwd=ROOT, env=env,
                            capture_output=True, timeout=60)
    assert result.returncode == 0, (args[0], result.returncode, result.stderr.decode('utf-8', 'replace')[:1000])
    return result.stdout.decode('utf-8', 'replace').strip()


old = proof['old_local_commit_preserved']
new = proof['commit']
assert git('symbolic-ref', 'HEAD') == 'refs/heads/main'
assert git('rev-parse', 'HEAD') == old
assert not git('diff', '--cached', '--name-only'), '原暂存区已变，先保留不整理'
assert git('remote', 'get-url', 'origin') == 'https://github.com/shspic/RetroLume-agent.git'
archive_ref = 'refs/private/local-history-20260923'
assert not git('for-each-ref', '--format=%(refname)', archive_ref)
backup = ROOT / '.runtime/github-sync-20261018'
backup.mkdir(parents=True, exist_ok=True)
with (backup / 'original.index').open('xb') as stream:
    stream.write((ROOT / '.git/index').read_bytes())
original_index_sha = hashlib.sha256((ROOT / '.git/index').read_bytes()).hexdigest()
git('update-ref', archive_ref, old, '0' * 40)
assert git('rev-parse', archive_ref) == old
git('update-ref', 'refs/heads/main', new, old)
git('read-tree', new)  # 不使用-u；只更新Git索引，不检出、不删除或覆盖工作树。
git('update-ref', 'refs/remotes/origin/main', new)
git('config', '--local', 'branch.main.remote', 'origin')
git('config', '--local', 'branch.main.merge', 'refs/heads/main')
git('config', '--local', 'core.longpaths', 'true')
assert git('rev-parse', 'HEAD') == new
assert git('write-tree') == proof['tree']
assert git('rev-parse', archive_ref) == old
assert git('rev-parse', '@{upstream}') == new
record = {'at': datetime.now(timezone.utc).isoformat(), 'local_main': new, 'upstream': 'origin/main',
          'old_private_history_preserved_at': archive_ref, 'old_private_commit': old,
          'private_history_is_not_under_refs_heads_and_not_sent_by_push_all': True,
          'previous_staging_was_empty': True, 'original_index_sha256': original_index_sha,
          'original_index_backup_ignored': '.runtime/github-sync-20261018/original.index',
          'worktree_check_out_delete_or_overwrite': False, 'core_autocrlf_retained_false': True}
with (HERE / 'local-alignment.json').open('x', encoding='utf-8') as stream:
    json.dump(record, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps(record, ensure_ascii=False), flush=True)
