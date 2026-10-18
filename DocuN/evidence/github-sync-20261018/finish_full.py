"""仅在完整快照远端核证和本地主分支整理成功后写入共享结果。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
commit = json.loads((HERE / 'full-commit.json').read_text(encoding='utf-8'))
manifest = json.loads((ROOT / commit['manifest_path']).read_text(encoding='utf-8'))
remote = json.loads((HERE / 'remote-main-verification.json').read_text(encoding='utf-8'))
local = json.loads((HERE / 'local-alignment.json').read_text(encoding='utf-8'))
assert remote['verified'] and remote['remote_main'] == local['local_main'] == commit['commit']
assert not (HERE / 'management-save-proof.json').exists()
now = datetime.now(timezone(timedelta(hours=8))).isoformat()
old_reason = '该命令会把约47MB、1227个文件的代码快照公开推送到公共GitHub主分支；虽用户授权了同步仓库，但未明确授权这份具体完整载荷公开外发，且无法仅凭当前证据排除其中含敏感信息。'


def write(path, value, new=True):
    if isinstance(value, str):
        value = value.encode('utf-8')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb' if new else 'wb') as stream:
        stream.write(value)
    assert path.read_bytes() == value


def save_json(path, data):
    write(path, json.dumps(data, ensure_ascii=False, indent=2) + '\n')


save_json(HERE / 'explicit-publication-authorization.json', {
    'at': now, 'user_authorization_verbatim': '"D:\\shspic\\project_NO3_RetroLume-agent"这个文件夹下，除了"D:\\shspic\\project_NO3_RetroLume-agent\\.gitignore"中的文件不跟踪、上传、同步到GitHub之外，其他文件均可跟踪、上传、同步到GitHub',
    'destination': 'https://github.com/shspic/RetroLume-agent', 'visibility_verified': 'public',
    'new_authorization_after_prior_review_rejection': True,
    'prior_rejected_source_only_commit': '6a6bd79f9e6cfb09b2fa46efa87c38433c0dbb1c',
    'prior_rejection_verbatim': old_reason, 'prior_rejected_command_had_no_process_or_remote_write': True,
    'scope': 'all actual nonignored project files including DocuN and DocuS',
    'current_full_commit': commit['commit'], 'manifest_sha256': commit['full_manifest_sha256'],
    'matched_secret_values_printed_or_saved': False, 'old_source_only_scope_restriction_superseded': True})

state_path = ROOT / 'DocuS/执行动态文档.MD'
readme_path = ROOT / 'README.md'
change_path = ROOT / 'DocuS/文档变更记录.MD'
before = {p: p.read_bytes() for p in [state_path, readme_path, change_path]}
assert '文档v2.73' in before[state_path].decode('utf-8-sig')[:200]
for path, raw in before.items():
    write(HERE / 'shared-before' / (path.name + '.bytes'), raw)
readme = before[readme_path].decode('utf-8')
old_line = next(line for line in readme.splitlines() if line.startswith('公开仓库为 '))
new_line = ('公开仓库为 [shspic/RetroLume-agent](https://github.com/shspic/RetroLume-agent)，默认分支为 `main`。'
            '用户于 2026-10-18 明确授权同步项目目录中除 `.gitignore` 排除项外的全部文件，包含源码、DocuS、任务卡、结果及可公开证据。'
            '已按此范围建立公开历史；本机凭据、私有运行数据、浏览器存储、依赖环境和大型生成缓存由 `.gitignore` 排除并原样保留本机。'
            '旧本地提交保存在 `refs/private/local-history-20260923`，不随公开分支上传。仓库同步不代表产品验收、部署发布或真实供应商调用已获启用。')
assert readme.count(old_line) == 1
write(readme_path, readme.replace(old_line, new_line), False)
prefix = f'''# 执行动态文档

文档v2.74，2026-10-18，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.46、task_model/07。以下v2.73原字节保留。

## 用户授权全部非忽略项目文件公开同步，完整快照已核实到达GitHub

{now}。用户明确项目根内除.gitignore规则外其余均可跟踪／上传／同步至公开仓库shspic/RetroLume-agent。本轮由主控直接办理用户单独指派的Git同步；这替代先前仅源码白名单，不是TASK120工程卡的Git运行许可。DocuS／DocuN任务卡／结果／可公开证据实际纳入，未整体忽略。

完整快照起点{manifest['cutoff_utc']}，{manifest['count']}文件／{manifest['bytes']}字节，清单SHA256为{commit['full_manifest_sha256']}。实际根.gitignore在保留原规则后追加私有凭据／浏览器profile／运行数据和生成镜像缓存忽略，84份逐文件待核敏感材料原件仅本机保留；无产品核心秘密发现、无剩余>100MiB文件。未删除数据、未改旧报告或归档原件。

公开根提交{commit['commit']}，tree {commit['tree']}；完整树逐项mode／blob与清单一致，无旧parent。远端main通过真实Git读取核证，明确的上传动作已成功。原本地main45951501…f702已保存在refs/private/local-history-20260923（非heads，普通push --all不带出），本地main／origin/main已接新公开根、原暂存为空才整理，未检出或覆盖工程工作树。README旧源码限制说明按本次用户授权更新。后续同步使用正常增量提交／普通push，.gitignore不能自动从未来新提交中移除曾已跟踪的秘密，仍须保持这一排除边界。

先前47MB源码方案曾在启动push前被自动审批拒绝，用户随后明确上述全部非忽略文件公开范围；新完整载荷按该授权另建根提交并通过正常Git路径推送，没有经连接器或间接接口绕过拒绝。源代码-only分支本地保留，未推旧私有历史。

TASK120/R114目录和产品的八项持续写入已观察，已出现执行活动；正式成果仍未回传、验收仍未完成，不补造接收起点或运行计数，已保存卡／许可／原累计预算不变。Q冻结、主控provider／费用0、72h未起，STEP018整体／STEP019／STEP020／M1／项目均未签通过。主控本轮仅Git对象／远端同步／忽略规则和共享维护，无产品实现／compile／测试／PG／Docker／API／Browser／业务Job／模型／付费。八份扫描期在途变化已只核对应对象并冻结，不重复全量扫描、不打断工程；当前快照包含开发候选字节，工程后续编辑需另按同一规则增量同步。

完整结果DocuN/results/GITHUB-SYNC-20261018-result.md；原清单／本地树／远端核证／规则与共享旧字节均在DocuN/evidence/github-sync-20261018。Git metadata预检错误（独立index误用于原暂存判断、check-ignore正常退出1）及冗余对象header批量查询120秒超时均保留，未推送或改工程；全部实际hash-object写入证明复用，只读回变化八项，不重复全扫，不计作产品测试。CHG1517—1521，下一1522。

## 以下为v2.73及更早历史

'''
assert state_path.read_bytes() == before[state_path]
write(state_path, prefix.encode('utf-8') + before[state_path], False)
result_path = ROOT / 'DocuN/results/GITHUB-SYNC-20261018-result.md'
result = f'''# 项目全范围GitHub同步结果

{now}。完整快照已真实推送并核证到用户指定的公开仓库[shspic/RetroLume-agent](https://github.com/shspic/RetroLume-agent)，main。范围为根目录内全部非忽略现存文件，包括DocuS／DocuN，并非仅源码。

- 根提交：[{commit['commit']}](https://github.com/shspic/RetroLume-agent/commit/{commit['commit']})；无私有父提交，tree `{commit['tree']}`。
- 快照：{manifest['cutoff_utc']}起读，{manifest['count']}文件、{manifest['bytes']}字节。全文件mode／blob与[最终清单](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/github-sync-20261018/full-reviewed-manifest.json)逐一一致；八份扫描期在途变化单独复核并从已捕获Git对象固定，不追赶后续编辑，不将开发快照冒充稳定发行版。
- 排除：实际根.gitignore保留原规则并追加凭据、私有浏览器profile、运行数据／导出和大型镜像缓存；84份文件级敏感发现已精确忽略。私密值不打印、不写证据，不删本地原件；产品核心待核发现0、剩余超GitHub100MiB文件0。
- 本地：main及origin/main接入新的公开历史；旧45951501d2741630a229762d6b2d3f4b34d7f702保存在refs/private/local-history-20260923，原空暂存区才整理，仅read-tree不带-u，无检出、删除或覆盖工作树。原index备份在忽略的.runtime/github-sync-20261018。
- 控制：先前仅源码提交在push进程创建前被自动审批拒绝、远端零写入；随后用户明确授权整个非忽略目录，按新范围另行核清单及正常Git推送。本地metadata前置错误及冗余批量对象查询超时均保留，后续直接复用已写入对象，不重复全量扫描；非产品运行，不占TASK120资源预算。
- 证据：full-scope-policy.json／full-manifest.json／full-commit.json／remote-main-verification.json／local-alignment.json；原方案、失败和全部私有／工程证据未改写。

README与执行动态v2.74按用户新规则更新，原v2.73整段字节保留。Git同步仅交付开发快照，不签TASK120、Q启用、产品验收或发布；产品测试／PG／Docker／API／Browser／模型／费用新增0。当前未收到TASK120正式成果，继续沿原A+窗口及原许可，不因同步换卡、清账或重复验证。
'''
write(result_path, result)
entries = [
    ('1517', '.gitignore', '追加必要私有／运行／生成缓存排除，原本机文件与旧规则保留；按用户全部非忽略范围授权。'),
    ('1518', 'README.md', '替换旧仅源码与未上传说明，记录全部非忽略范围和实际GitHub公开同步事实。'),
    ('1519', 'DocuN/results/GITHUB-SYNC-20261018-result.md', '完整快照实际上传及根树／远端／本地历史保留证明；不签产品通过。'),
    ('1520', 'DocuS/执行动态文档.MD', 'v2.74登记用户明确全范围公开授权与同步，TASK120仍待回传、Q冻结与原预算保持。'),
    ('1521', 'DocuN/evidence/github-sync-20261018', '全范围逐文件清单、秘密排除、独立Git树、远端核证、本地历史／原暂存保存和共享读回。'),
]
addition = ''.join(f'\n- CHG-{number}，{now}，Codex编排Agent，{name}。{description}\n' for number, name, description in entries)
assert change_path.read_bytes() == before[change_path]
write(change_path, before[change_path] + addition.encode('utf-8'), False)
assert state_path.read_bytes().endswith(before[state_path])
save_json(HERE / 'management-save-proof.json', {
    'at': now, 'full_root_commit': commit['commit'], 'remote_root_verified': True,
    'old_state_original_suffix_preserved': True, 'product_or_old_evidence_rewritten': False,
    'files': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size}
              for p in [state_path, readme_path, change_path, result_path]], 'next_CHG': 1522})
print(json.dumps({'saved': True, 'state': 'v2.74', 'CHG': '1517-1521', 'result': str(result_path)}, ensure_ascii=False))
