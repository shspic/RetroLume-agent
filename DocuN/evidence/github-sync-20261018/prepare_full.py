"""按Git忽略规则核全项目；不改原件，只对私有数据追加精确忽略。"""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import subprocess
import hashlib
import json
import os
import re

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
env = dict(os.environ)
env['GIT_OPTIONAL_LOCKS'] = '0'
assert not (HERE / 'full-manifest.json').exists(), '已保存，先核断点'


def git(*args, input=None):
    result = subprocess.run(['git', *args], cwd=ROOT, env=env, input=input, capture_output=True, timeout=90)
    assert result.returncode in (0, 1), result.stderr[:200]
    return result.stdout


def literal_rule(name):
    for char in ('\\', '[', ']', '*', '?', ' '):
        name = name.replace(char, '\\' + char)
    return '/' + name


raw_names = git('ls-files', '--cached', '--others', '--exclude-standard', '-z')
names = sorted(set(x.decode('utf-8') for x in raw_names.split(b'\0') if x))
names = [name for name in names if (ROOT / name).is_file()]
ignored = {x.decode('utf-8') for x in git('check-ignore', '--no-index', '--stdin', '-z',
           input=b'\0'.join(name.encode('utf-8') for name in names) + b'\0').split(b'\0') if x}
names = [name for name in names if name not in ignored]
extra_profiles = {name.rsplit('/Local State', 1)[0] for name in names if name.endswith('/Local State')}
extra_profiles.update(name.split('/Default/Preferences', 1)[0] for name in names if '/Default/Preferences' in name)
new_ignored = []
findings = []
records = []
oversized = []
critical = []
binary_count = 0
source_ext = {'.py', '.js', '.mjs', '.cjs', '.ts', '.tsx', '.sql', '.ps1', '.sh', '.cmd'}
text_ext = source_ext | {'.md', '.json', '.jsonl', '.txt', '.yaml', '.yml', '.csv', '.out', '.err', '.log', '.toml', '.example', '.bytes'}
high_patterns = [
    ('private_key', re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----')),
    ('github_token', re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{35,})\b')),
    ('provider_key', re.compile(rb'\bsk-[A-Za-z0-9_-]{24,}\b')),
    ('AWS_key', re.compile(rb'\bAKIA[0-9A-Z]{16}\b')),
    ('password_in_DSN', re.compile(rb'(?:postgres(?:ql)?|mysql|mariadb)://[^\s\"\x27<>/@:]+:([^\s\"\x27<>/@]+)@', re.I)),
    ('literal_authorization', re.compile(rb'''(?i)authorization[\"\x27]?\s*[:=]\s*[\"\x27](?:Bearer|Basic)\s+([A-Za-z0-9+/=_-]{16,})''')),
]
json_secret = re.compile(rb'''(?i)[\"\x27](?:api_key|secret_key|access_token|review_key|hmac_key|control_key|password|passwd|pwd)[\"\x27]\s*:\s*[\"\x27]([^\"\x27\r\n]{6,})[\"\x27]''')
placeholder = [b'example', b'placeholder', b'redacted', b'synthetic', b'dummy', b'fake', b'test-', b'test_',
               b'not-a-', b'no-real', b'${', b'<', b'{', b'user:pass@']
cutoff = datetime.now(timezone.utc).isoformat()
print(json.dumps({'phase':'full_scope_scan','files':len(names),'cutoff_utc':cutoff}), flush=True)
for index, name in enumerate(names, 1):
    path = ROOT / name
    if any(name.startswith(profile + '/') for profile in extra_profiles):
        continue
    if not path.resolve().is_relative_to(ROOT):
        new_ignored.append((literal_rule(name), '符号目标超出用户指定项目目录'))
        findings.append({'path':name,'kind':'outside_root_link'})
        continue
    try:
        size = path.stat().st_size
        if size > 100 * 1024 * 1024:
            oversized.append({'path':name,'bytes':size})
            continue
        raw = path.read_bytes()
    except FileNotFoundError:
        findings.append({'path':name,'kind':'file_removed_during_cutoff_scan','ignored':False})
        continue
    if raw.startswith(b'SQLite format 3\0'):
        new_ignored.append((literal_rule(name), '实际SQLite运行数据，不是源码'))
        findings.append({'path':name,'kind':'runtime_sqlite'})
        continue
    hits = []
    is_text = path.suffix.lower() in text_ext or b'\0' not in raw[:4096]
    if is_text:
        for kind, pattern in high_patterns:
            for match in pattern.finditer(raw):
                value = match.group(1) if match.lastindex else match.group()
                lower = value.lower()
                if any(marker in lower for marker in placeholder): continue
                if kind == 'password_in_DSN' and len(value) <= 3: continue
                # 代码中的纯测试字面值与正常文档示例不算真实平台key。
                if kind in {'provider_key','github_token'} and len(set(value.replace(b'-',b''))) <= 3: continue
                hits.append({'kind':kind,'line':raw.count(b'\n',0,match.start())+1})
        if path.suffix.lower() not in source_ext and not name.startswith(('deploy/preview/licenses/','deploy/preview/vendor/')):
            for match in json_secret.finditer(raw):
                value=match.group(1);lower=value.lower()
                if any(marker in lower for marker in placeholder) or value.startswith((b'RETROLUME_',b'env:',b'http')):continue
                hits.append({'kind':'serialized_secret_review','line':raw.count(b'\n',0,match.start())+1})
    else:
        binary_count += 1
    if hits:
        findings.append({'path':name,'findings':hits,'matched_values_saved':False})
        if name.startswith(('backend/app/','frontend/src/','backend/migrations/','config/')):
            critical.append({'path':name,'findings':hits})
        else:
            new_ignored.append((literal_rule(name), '检测到连接凭据/令牌或待核私有字段，原件仅保留本地'))
        continue
    records.append({'path':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
                    'blob_sha1':hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),
                    'mode':'100755' if path.suffix=='.sh' else '100644'})
    if index % 5000 == 0:
        print(json.dumps({'scanned':index,'total':len(names),'accepted':len(records),'private_findings':len(findings)}),flush=True)
for profile in sorted(extra_profiles):
    new_ignored.append((literal_rule(profile)+'/', '实际Local State/Preferences浏览器私有profile'))
if new_ignored:
    ignore=ROOT/'.gitignore';before=ignore.read_bytes()
    addition='\n# GitHub-full-sync-20261018：逐文件私有检查补充，原证据不改不删\n'
    for pattern, reason in sorted(set(new_ignored)):
        addition+='# '+reason+'\n'+pattern+'\n'
    assert ignore.read_bytes()==before
    with ignore.open('ab') as stream:stream.write(addition.encode('utf-8'))
    assert ignore.read_bytes().startswith(before)
    raw=ignore.read_bytes()
    for row in records:
        if row['path']=='.gitignore':
            row.update(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),blob_sha1=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest())
new_ignore_names={x.decode('utf-8') for x in git('check-ignore','--no-index','--stdin','-z',
                    input=b'\0'.join(row['path'].encode('utf-8') for row in records)+b'\0').split(b'\0') if x}
records=[row for row in records if row['path'] not in new_ignore_names]
records.sort(key=lambda row:row['path'])
result={'prepared_at':datetime.now(timezone.utc).isoformat(),'cutoff_utc':cutoff,
        'source':'用户明确指定整个项目除.gitignore外均可跟踪/上传/同步',
        'files':records,'count':len(records),'bytes':sum(row['bytes'] for row in records),
        'by_root':dict(Counter(row['path'].split('/')[0] for row in records)),
        'gitignore_sha256':hashlib.sha256((ROOT/'.gitignore').read_bytes()).hexdigest(),
        'private_findings':findings,'new_ignore_rules_count':len(set(new_ignored)),
        'critical_product_findings':critical,'oversized_remaining':oversized,'binary_files':binary_count,
        'old_history_is_parent':False,'worktree_files_deleted':False,'payload_authorization_is_explicit':True}
with (HERE/'full-manifest.json').open('x',encoding='utf-8') as stream:
    json.dump(result,stream,ensure_ascii=False,indent=2);stream.write('\n')
print(json.dumps({'phase':'full_scope_scan_complete','files':len(records),'bytes':result['bytes'],
                   'by_root':result['by_root'],'private_findings':len(findings),'new_ignore_rules':len(set(new_ignored)),
                   'critical_product_findings':critical,'oversized_remaining':oversized},ensure_ascii=False),flush=True)
if critical or oversized:raise SystemExit(2)
