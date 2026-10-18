"""按用户新指示同步全部非忽略文件，仅追加实际私有/生成物忽略规则。"""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import subprocess
import hashlib
import json
import os

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
env = dict(os.environ)
env['GIT_OPTIONAL_LOCKS'] = '0'
assert not (HERE / 'full-scope-policy.json').exists()
ignore = ROOT / '.gitignore'
old = ignore.read_bytes()
assert b'GitHub-full-sync-20261018' not in old
out = subprocess.run(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=ROOT,
                     env=env, capture_output=True, timeout=60)
assert out.returncode == 0
names = sorted(set(x.decode('utf-8') for x in out.stdout.split(b'\0') if x))
existing = [name for name in names if (ROOT / name).is_file()]
profile_roots = set()
for name in existing:
    if '/Default/Network/Cookies' in name:
        profile_roots.add(name.split('/Default/Network/Cookies', 1)[0])
rules = [
    ('/deploy/preview/task109-c01-cache/', '本机OCI层和949MB镜像归档，实际超过GitHub100MiB限制'),
    ('/deploy/preview/task109-c04-context/', '历史生成构建上下文'),
    ('/deploy/preview/task109-h0-context/', '历史生成构建上下文'),
    ('/deploy/preview/build-contexts/', '正式源码可重建的生成构建上下文'),
    ('/.runtime/', '本机私有运行配置/凭据/数据，不只排除TASK120'),
    ('*.log', '运行日志可能含环境或请求数据，本地原件保留'),
    ('*.har', '网络录制可能含会话/Authorization'),
    ('**/trace.zip', '浏览器运行录制，不是源码'),
    ('*.rldata', '数据导出/备份包，可能含业务资料'),
    ('**/credentials-*.bin', '私有持久凭据'),
    ('**/credentials-*.pending', '私有凭据临时发布'),
    ('*.dpapi', '私有凭据密文'),
    ('**/dsn.json', '本机连接信息'),
    ('**/credentials.json', '本机凭据配置'),
    ('**/pg-before.json', '原始数据库行快照，不是实现或迁移'),
    ('**/pg-after.json', '原始数据库行快照，不是实现或迁移'),
    ('/DocuN/evidence/github-sync-20261018/public-tree/', '本同步生成的重复快照，不递归同步自身'),
    ('/DocuN/evidence/github-sync-20261018/full-public-tree/', '本同步生成的重复快照，不递归同步自身'),
    ('/DocuN/evidence/github-sync-20261018/*.index', 'Git临时index，不是源码'),
]
rules += [('/' + name + '/', '实际发现Cookies的浏览器私有profile') for name in sorted(profile_roots)]
with (HERE / 'gitignore-before-full-sync.bytes').open('xb') as stream: stream.write(old)
addition = '\n# GitHub-full-sync-20261018：只排除凭据、运行资料和生成缓存，文档/卡/报告继续纳管\n'
for pattern, reason in rules:
    addition += '# ' + reason + '\n' + pattern + '\n'
assert ignore.read_bytes() == old
with ignore.open('ab') as stream: stream.write(addition.encode('utf-8'))
assert ignore.read_bytes().startswith(old)
policy = {
    'at': datetime.now(timezone.utc).isoformat(),
    'user_exact_authorization': 'D:/shspic/project_NO3_RetroLume-agent下除.gitignore中的文件外，其他文件均可跟踪、上传、同步到GitHub',
    'public_repository': 'https://github.com/shspic/RetroLume-agent',
    'scope_changed_from_source_only_to_all_nonignored': True,
    'prior_push_rejection_preserved_and_not_bypassed': True,
    'previous_public_source_commit_not_pushed': '6a6bd79f9e6cfb09b2fa46efa87c38433c0dbb1c',
    'gitignore_before_sha256': hashlib.sha256(old).hexdigest(),
    'gitignore_after_sha256': hashlib.sha256(ignore.read_bytes()).hexdigest(),
    'original_ignore_bytes_preserved_prefix': True,
    'new_patterns': [{'pattern': pattern, 'reason': reason} for pattern, reason in rules],
    'actual_browser_profile_roots': len(profile_roots),
    'DocuN_DocuS_tasks_results_handoffs_archives_ignored_as_a_whole': False,
    'files_deleted_or_old_reports_rewritten': False,
}
with (HERE / 'full-scope-policy.json').open('x', encoding='utf-8') as stream:
    json.dump(policy, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps({'new_ignore_rules': len(rules), 'actual_browser_profiles': len(profile_roots),
                  'gitignore_after': policy['gitignore_after_sha256'], 'scope': 'all actual nonignored files, including DocuN and DocuS'}, ensure_ascii=False))
