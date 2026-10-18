"""只读工作源码，准备经筛选的公开快照；不修改工程文件或Git。"""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SNAPSHOT = HERE / 'public-tree'
assert ROOT == Path('D:/shspic/project_NO3_RetroLume-agent').resolve()
assert not (HERE / 'manifest.json').exists(), '已有快照，先核对，不盲目重做'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def save(name, value):
    path = HERE / name
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


paths = set()
for directory in ['backend/app', 'backend/migrations', 'backend/tests', 'frontend/src', 'frontend/tests', 'tests']:
    base = ROOT / directory
    for path in base.rglob('*'):
        if not path.is_file(): continue
        rel = path.relative_to(base)
        if any(part in {'__pycache__', '.cache', '.venv', 'node_modules', 'dist'} for part in rel.parts): continue
        if path.suffix.lower() in {'.py', '.sql', '.ts', '.tsx', '.css', '.js', '.mjs', '.cjs', '.ps1'}:
            paths.add(path)
        elif 'THIRD_PARTY_LICENSES' in path.parts:
            paths.add(path)
        elif str(path.relative_to(ROOT)).replace('\\', '/') == 'backend/app/preview/schema-fingerprint.json':
            paths.add(path)
for rel in ['backend/requirements.txt', 'backend/requirements.lock', 'frontend/package.json',
            'frontend/package-lock.json', 'frontend/index.html', 'frontend/tsconfig.json',
            'frontend/vite.config.js', 'start-local.cmd']:
    path = ROOT / rel
    assert path.is_file(), rel
    paths.add(path)
paths.update((ROOT / 'config').glob('*.example.json'))
paths.add(ROOT / 'config/local.env.example')
for path in (ROOT / 'deploy').iterdir():
    if path.is_file() and path.suffix in {'.py', '.ps1', '.yml'}:
        paths.add(path)
preview = ROOT / 'deploy/preview'
for path in preview.iterdir():
    if path.is_file() and path.name != 'README.md': paths.add(path)
for directory in ['vendor/playwright-core', 'licenses/base-c091b21d-c02-resolved-02']:
    base = preview / directory
    assert base.is_dir(), str(base)
    paths.update(path for path in base.rglob('*') if path.is_file() and '__pycache__' not in path.parts)

patterns = [
    ('private_key', re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----')),
    ('github_token', re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{35,})\b')),
    ('provider_secret', re.compile(rb'\bsk-[A-Za-z0-9_-]{24,}\b')),
    ('AWS_access_key', re.compile(rb'\bAKIA[0-9A-Z]{16}\b')),
    ('credential_in_database_url', re.compile(rb'(?:postgres(?:ql)?|mysql|mariadb)://[^\s\"\x27<>/@:]+:[^\s\"\x27<>/@]+@', re.I)),
    ('actual_user_home_path', re.compile(rb'(?:C:[/\\]{1,2}Users[/\\]{1,2}(?:28432)|D:[/\\]{1,2}spiritice)', re.I)),
]
literal_secret = re.compile(rb'''(?i)(?:api_key|secret_key|access_token|review_key|password|passwd|pwd)[\"\x27]?\s*[:=]\s*[\"\x27]([^\"\x27\r\n]{8,})[\"\x27]''')
findings = []
withheld = []
selected = []
critical_findings = []
SNAPSHOT.mkdir(exist_ok=False)
for path in sorted(paths, key=str):
    assert path.resolve().is_relative_to(ROOT), str(path)
    relative = path.relative_to(ROOT).as_posix()
    raw = path.read_bytes()
    found = []
    for kind, pattern in patterns:
        for match in pattern.finditer(raw):
            value = match.group()
            if b'EXAMPLE' in value.upper() or b'PLACEHOLDER' in value.upper(): continue
            # 只豁免可见测试占位，不把历史合成容器真实口令当成占位。
            if kind == 'credential_in_database_url' and any(x in value.lower() for x in [b'user:password@', b'user:pass@', b'example:example@', b'test:test@']): continue
            found.append({'kind': kind, 'line': raw.count(b'\n', 0, match.start()) + 1})
    if not relative.startswith(('deploy/preview/vendor/', 'deploy/preview/licenses/')):
        for match in literal_secret.finditer(raw):
            value = match.group(1)
            if any(marker in value.lower() for marker in [b'example', b'placeholder', b'synthetic', b'unused', b'test-', b'test_', b'fake', b'dummy', b'not-a-', b'no-real', b'key_env', b'${']): continue
            if value.startswith((b'env:', b'{', b'postgresql:', b'http', b'RETROLUME_')): continue
            found.append({'kind': 'literal_secret_review', 'line': raw.count(b'\n', 0, match.start()) + 1})
    if len(raw) > 50 * 1024 * 1024:
        found.append({'kind': 'oversized_file', 'line': None})
    if found:
        entry = {'path': relative, 'findings': found, 'bytes': len(raw), 'sha256': digest(raw)}
        findings.append(entry)
        if relative.startswith(('backend/tests/', 'frontend/tests/', 'tests/')):
            withheld.append(entry)
            continue
        critical_findings.append(entry)
        continue
    target = SNAPSHOT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    mode = '100755' if path.suffix == '.sh' else '100644'
    selected.append({'path': relative, 'source_path': str(path), 'bytes': len(raw), 'sha256': digest(raw),
                     'mode': mode, 'variant': False})

public_ignore = '''# 本地运行环境、依赖和构建产物
.venv/
node_modules/
dist/
__pycache__/
*.pyc
.cache/
*.log
.env
.env.*
!.env.example

# 本机私有配置、资料、备份、会话与工程编排证据
/config/*.local.json
/config/*.env
/config/local.env
/.runtime/
/data-exit-control/
/synthetic-runtime/
/.workbuddy/
/.codex/
/DocuN/
/DocuS/
/Ndocu/
/docu/
/evidence/
/spikes/
/backend/Ndocu/
/AGENTS.md

# 已准备镜像与临时构建上下文不进入源码仓库
/deploy/preview/build-contexts/
/deploy/preview/task109-c01-cache/
/deploy/preview/task109-c04-context/
/deploy/preview/task109-h0-context/
'''
public_readme = '''# RetroLume / 溯光教育 Agent

RetroLume 是以本地资料为依据的学习与文字面试应用，包含资料与 PDF 核对、学习路径和练习反馈、低信任学习记忆、受控工具、混合检索及有限交互解释。

本仓库保存2026-10-18的开发源码快照，包含仍在开发的接线模块。源码同步不代表整体验收或生产发布；真实模型与向量服务、固定预览均默认关闭。未知调用只读取已有事实，不自动重发；恢复副本保持只读。

## 目录

- backend/app 为后端业务、持久仓储、能力准入和 Windows 监督实现。
- backend/migrations 为版本化 PostgreSQL 迁移。应用不会自动迁移用户数据库。
- backend/tests、frontend/tests、tests 为适用测试与通用夹具。历史专机执行器或含本机配置的夹具不随快照公开。
- frontend/src 为 React 工作区、草稿和原键恢复界面。
- config 只提供无真实凭据的示例配置。
- deploy 为本地启动和固定预览构建源码，包含必要第三方许可材料。

本机配置、密钥、资料、备份、浏览器状态、原始日志、内部任务卡／报告／证据、依赖目录和镜像缓存不在本仓库。

## 环境与依赖

项目当前使用 Python 3.12、Node 24、npm 11、PostgreSQL 与 pgvector。后端原生进程监督采用 Windows Job Object；不能据此认为整套业务已支持 Linux 服务端部署。

在 backend 下创建 .venv，然后按锁文件恢复：

```powershell
python -m venv backend/.venv
backend/.venv/Scripts/python.exe -m pip install --only-binary=:all: -r backend/requirements.lock
cd frontend
npm.cmd ci --ignore-scripts --no-audit --no-fund
npm.cmd run build
```

这些命令供操作者在目标环境明确执行，本次源码同步没有安装依赖、运行迁移、构建或启动业务。不要用旧集成夹具直接操作现有用户数据库。

## 本地配置与启动

设置已存在且互相独立的 RETROLUME_DATA_DIR 与 RETROLUME_BACKUP_DIR。需要数据库时通过 RETROLUME_DATABASE_URL 或私有 config/database.local.json 提供本机连接。参考 config/local.env.example，真实连接串和密码不得提交。

从项目根运行 deploy/start-backend.ps1 可使用现有后端入口，健康检查地址为 http://127.0.0.1:8000/health。start-local.cmd 使用 deploy/start_local.py 管理明确配置的本地资源；只有实际创建或登记的自有资源才允许停止。前端正式构建由后端同源提供，开发时可在 frontend 运行 npm.cmd run dev。

资料导入和保存不是模型调用授权。活动／集成／只读恢复的配置分别参考 config 中对应 example 文件；占位值有意不可激活。模型密钥只能通过服务器配置声明的环境变量注入，不填入目标、资料、浏览器或仓库。

## 行为与安全边界

学习支持路径、练习、作答、反馈、参考、纠错和有限独立复测；文字面试保留每个回答版本与来源引用。记忆只是低信任偏好，不作为履历或能力事实。模型返回仍须通过本地结构、来源及当前资格核定。

页面先持久保存意图，再发送显式动作；刷新、重开和结果未确认时只读取原键事实。来源、记忆、目标或视图身份改变时，迟到结果不能推进新状态。取消／超时只能停止本地后续工作，不能撤回已发送到远端的请求。

次数、费用、工具与运行时间由持久账本及受控监督约束；UNKNOWN 保留原预留。Q 的逐请求批准协议还需完整实现、独立复核和正常部署启用条件，当前快照不提供可用授权文件、真实激活时间、审核密钥或付费运行资格。配置缺失或事实无法核对时保持关闭。

## 固定交互预览

预览只接收有限描述数据，固定项目程序在隔离容器中生成画面并处理有限输入；不执行模型自由 HTML 或 JavaScript。详见 deploy/preview/README.md。

仓库保留正式 renderer／vendor 源码和所需许可文字，不包含浏览器镜像、OCI层、临时构建上下文或部署审核票据。准备环境和启用预览是独立的操作者动作，不能直接把源码快照当成已配置的预览运行包。

## 仓库

项目仓库为 https://github.com/shspic/RetroLume-agent 。本次公开分支从筛选后的源码树建立，不包含本地旧提交里的内部历史与执行证据；本地原工程及旧历史继续保留。
'''
preview_readme = '''# 固定交互预览源码与部署材料

预览默认关闭。模型只提供有限 interactive_description 数据，固定 runtime.cjs／runtime.css／runtime.html 和 renderer-host.cjs／renderer-bootstrap.cjs 在隔离容器执行。主页面仅发送有限参数或reset并读取PNG，不执行自由模型HTML／JavaScript。

## 构建材料

正式构建入口是 Dockerfile.production 和 build_renderer.py。源码需要 vendor/playwright-core 1.62.1、licenses/base-c091b21d-c02-resolved-02、明确提供的受信本地OCI基础材料。准备函数核固定base manifest、逐文件许可SHA及源文件生成load-manifest，再由构建入口使用network none／pull false。仓库不包含OCI层、base-image.tar、浏览器二进制或历史build-contexts；不会在构建时联网补装。

正式源码与第三方许可一起保留，vendor自带LICENSE／NOTICE／ThirdPartyNotices，基础系统与浏览器许可索引位于上述licenses目录。历史诊断Dockerfile等不是正式生产构建入口。

## 配置与启动边界

config/preview.example.json只有惰性占位。RETROLUME_PREVIEW_CONFIG指定的私有operator配置必须具有实际image_id、load_manifest_sha256、renderer_sha256、kernel_release、审核票据和服务器环境中的验证密钥。审核票据需绑定适用独立复核结果和完整身份；源码中的公开hash不是有效票据，普通调用者不能自行绕验证。

容器使用UID/GID10001、network none、read-only、cap-drop ALL、no-new-privileges、固定seccomp、private IPC／PID、init、restart no、CPU和内存及进程数限制。不得通过Compose启动常驻renderer或挂载Docker socket、资料、凭据及任意host目录。

每活动原限额3次／180秒，每次预扣30至60秒，准备和启动计入固定单调截止。关闭／失联会请求停止；缺少物理停止组合证明时保留预扣并关闭新预览。SQL状态、HTTP回包或单个Pid0不等于完整停止证明，远端模型请求也不因本地停止而撤回。

## 故障与数据

会话密钥和input owner不进日志／argv／资料正文；持久控制收据按现实现保护。重开先核原parent birth、精确CID／image／nonce及独占归属，不能抢占存活或未知旧owner。只停止自己登记的进程树和容器，不运行全局prune或删除卷来处理故障。

该目录是源码与许可材料，不是已就绪运行包。迁移用户库、准备镜像、配置真实密钥、独立审核及正式启用均需各自实际条件；源码同步没有执行这些动作。
'''
for relative, content in {'.gitignore': public_ignore, 'README.md': public_readme, 'deploy/preview/README.md': preview_readme}.items():
    raw = content.encode('utf-8')
    target = SNAPSHOT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    selected.append({'path': relative, 'source_path': None, 'bytes': len(raw), 'sha256': digest(raw),
                     'mode': '100644', 'variant': 'public_documentation_only_original_workspace_unchanged'})

source_drift = []
for row in selected:
    if row['source_path'] is None: continue
    path = Path(row['source_path'])
    if not path.is_file() or digest(path.read_bytes()) != row['sha256']:
        source_drift.append(row['path'])
selected.sort(key=lambda x: x['path'])
save('privacy-findings.json', {'findings': findings, 'withheld_test_files': withheld, 'critical_product_findings': critical_findings,
                               'matched_values_recorded': False, 'policy': '仅路径/类别/行号，不记录命中秘密值'})
manifest = {'prepared_at': datetime.now(timezone.utc).isoformat(), 'repository': 'shspic/RetroLume-agent',
            'visibility_verified': 'public', 'remote_empty_verified': True,
            'scope': 'source_snapshot_only_no_internal_history_no_deployment',
            'files': selected, 'count': len(selected), 'bytes': sum(x['bytes'] for x in selected),
            'by_root': dict(Counter(x['path'].split('/')[0] for x in selected)),
            'source_drift_after_copy': source_drift, 'critical_findings': len(critical_findings),
            'withheld_environment_test_files': len(withheld), 'old_local_history_will_be_parent': False,
            'local_HEAD_index_and_source_modified': False,
            'excluded': ['DocuN', 'DocuS', 'Ndocu', 'docu', 'evidence', 'spikes', 'AGENTS.md', '.runtime',
                         'private_configs_credentials_user_data_backups_browser_storage_logs', '.venv', 'node_modules', 'dist',
                         'preview_OCI_cache_build_contexts_duplicate_license_materials', 'historical_test_data_and_withheld_environment_runners']}
save('manifest.json', manifest)
print(json.dumps({'count': manifest['count'], 'bytes': manifest['bytes'], 'by_root': manifest['by_root'],
                  'critical_product_findings': critical_findings, 'withheld_tests': [{'path':x['path'],'findings':x['findings']} for x in withheld],
                  'source_drift': source_drift}, ensure_ascii=False))
if critical_findings or source_drift:
    raise SystemExit(2)
