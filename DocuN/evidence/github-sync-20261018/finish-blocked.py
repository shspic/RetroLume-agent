"""保存公开同步的真实停止点与范围，不重试被拒推送。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import json
import hashlib
import re

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
assert ROOT == Path('D:/shspic/project_NO3_RetroLume-agent').resolve()
assert not (HERE / 'blocked-save-proof.json').exists()
now = datetime.now(timezone(timedelta(hours=8))).isoformat()
manifest = json.loads((HERE / 'reviewed-manifest.json').read_text(encoding='utf-8'))
commit = json.loads((HERE / 'commit.json').read_text(encoding='utf-8'))
assert commit['commit'] == '6a6bd79f9e6cfb09b2fa46efa87c38433c0dbb1c'
assert commit['files'] == 1227 and commit['parents'] == []
assert hashlib.sha256((HERE / 'reviewed-manifest.json').read_bytes()).hexdigest() == commit['reviewed_manifest_sha256']


def write(path, raw, new=False):
    assert path.resolve().is_relative_to(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(raw, str): raw = raw.encode('utf-8')
    with path.open('xb' if new else 'wb') as stream: stream.write(raw)
    assert path.read_bytes() == raw
    raw.decode('utf-8-sig')


def save_json(path, value):
    write(path, json.dumps(value, ensure_ascii=False, indent=2) + '\n', True)


reason = '该命令会把约47MB、1227个文件的代码快照公开推送到公共GitHub主分支；虽用户授权了同步仓库，但未明确授权这份具体完整载荷公开外发，且无法仅凭当前证据排除其中含敏感信息。'
save_json(HERE / 'push-blocked.json', {
    'at': now, 'operation': 'git push --porcelain origin 6a6bd79f9e6cfb09b2fa46efa87c38433c0dbb1c:refs/heads/main',
    'state': 'auto_review_rejected_before_process_launch', 'process_exit_code': None,
    'remote_write_performed': False, 'reason_verbatim': reason,
    'post_rejection_remote_branch_read': {'tool': 'GitHub search_branches', 'branches': []},
    'workaround_or_indirect_upload_attempted': False,
    'remaining_action': '用户明确确认本份已冻结清单可以公开后，原提交普通推送并核远端；不重做源扫描或提交',
})
approval = f'''# GitHub公开同步的具体范围，等待确认

{now}。目标是用户指定的公开仓库https://github.com/shspic/RetroLume-agent，远端main。用户已授权同步；平台自动审批另外要求确认下面这份具体公开载荷。

本次精确提交6a6bd79f9e6cfb09b2fa46efa87c38433c0dbb1c，tree为299f8bde146defcb7cdf34192f9316fcf04a7f82。共1227文件、47647036字节，约47.6MB；逐文件路径／字节／SHA256及公开文档变体见[已审清单](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/github-sync-20261018/reviewed-manifest.json)，清单SHA256={commit['reviewed_manifest_sha256']}。

公开内容为后端业务与迁移、前端源码、依赖锁、通用测试、配置样例、本地部署源码及所需第三方许可。文件按根分为backend448、frontend93、deploy670、config7、tests6，以及.gitignore／README／start-local各1。deploy较大的文字来自固定浏览器／系统第三方许可，不含浏览器镜像或OCI层。

不公开DocuN／DocuS／Ndocu／docu／evidence／spikes、AGENTS内部规则、任务卡／报告／原始证据、用户资料／备份／配置／密钥／连接信息／浏览器存储、依赖环境／dist／镜像缓存或旧私有提交。发现的本机专用敏感／路径夹具及其直接环境依赖未纳入。源码白名单和模式扫描没有发现待公开产品文件的确定秘密，但扫描不是对任意敏感信息的绝对保证。

为使公开克隆可读，本次仅公开副本的README／预览README／.gitignore使用去内部路径的说明；工程里的这些原文件未改。快照包含开发中文件，不是完整验收、部署发布或真实Q启用；快照形成后的新增编辑仍保留本地。

本地原main仍为45951501d2741630a229762d6b2d3f4b34d7f702，原暂存区未改，全部旧记录／证据／数据保留。新公开提交单独位于codex/github-sync-20261018，无parent，推送不会带入旧私有历史。目标远端刚核仍为空；只作普通非强制推送，不覆盖已有提交，不修改仓库可见性。

需要的确认只有一项：同意把上述精确提交／清单公开推送到该仓库main。确认不改变真实模型、个人资料外发、用户库或部署权限，也不授权上传以后新增或其它未审文件。

平台停止原因原文为“{reason}”动作在CreateProcess阶段被拒，未启动push进程、没有远端写入。没有经连接器／分批／其它仓库绕过；将等待本份范围的明确确认后继续。
'''
write(HERE / 'publication-review.md', approval, True)

result_path = ROOT / 'DocuN/results/GITHUB-SYNC-20261018-result.md'
result = f'''# GitHub同步结果，公开推送被自动审批拦截

{now}。用户明确要求主控帮助同步项目到GitHub，本次是task_model下用户对具体Git动作的直接指派，主控亲自执行例外仅限本同步，不接管TASK120业务实现或放宽其Git0许可。

已完成真实远端metadata／分支核对（公开、push权限、空main）、受控源码白名单／隐私筛选、1227文件冻结副本、独立index／根提交和逐tree/blob身份核对。公开分支codex/github-sync-20261018，commit6a6bd79f9e6cfb09b2fa46efa87c38433c0dbb1c；原本地main45951501…f702、HEAD与原暂存区保留。已审字节47647036，范围与排除详见[具体公开范围](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/github-sync-20261018/publication-review.md)。源码、配置、数据与原旧记录未由本同步修改，README等只有公开副本变体。

推送未完成。普通非强制push在进程创建前被平台auto_review拒绝，无真实exit code／无远端写入；随后GitHub只读分支核对仍空。不能把本地提交称GitHub已同步。原始停止事实在push-blocked.json，候选／清单／排除理由及本地提交核证在本证据目录。没有用API、拆分或其它路径绕过。

第一轮Git ls-remote在默认沙箱报getaddrinfo thread failed；经正规权限审查的同一只读查询成功，未取得或输出凭据值。GitHub get_repo首轮错用参数repo_name，随后按已公开schema改repository_full_name成功；均为读取／连接准备，不是产品验证失败。所有真实产品测试／build／PG／Docker／业务Job／Browser／provider／费用0，本次没有借Git同步宣称功能或发布通过。

剩余只有对具体公开载荷作一次必要确认，再复用本根提交普通推送并核远端ref／tree，不重建或重复测试。此确认由平台自动审批拒绝触发，不是项目开发阶段重新索权；原因是“{reason}”。用户无需发送密码／token、执行Git命令或改工程文件。

Q继续冻结，STEP018整体／STEP019／STEP020／M1及项目不因源码同步通过，TASK120工程沿原许可继续且未被本操作接管。仓库https://github.com/shspic/RetroLume-agent保持公开，可见性没有更改。
'''
write(result_path, result, True)

state = ROOT / 'DocuS/执行动态文档.MD'
arch = ROOT / 'DocuS/架构动态文档.MD'
change = ROOT / 'DocuS/文档变更记录.MD'
assert '文档v2.73' in state.read_text(encoding='utf-8-sig').splitlines()[2]
assert '文档v1.46' in arch.read_text(encoding='utf-8-sig').splitlines()[2]
assert max(map(int, re.findall(r'CHG-(\d+)', change.read_text(encoding='utf-8-sig')))) == 1516
old = {p: p.read_bytes() for p in [state, arch, change]}
backup = HERE / 'before-shared-documents'
backup.mkdir(exist_ok=False)
for path, raw in old.items(): write(backup / path.name, raw, True)
state_prefix = f'''# 执行动态文档

文档v2.74，2026-10-18，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.47、task_model/07。以下v2.73原字节保留。

## 用户具体指派主控同步GitHub，本地公开提交完成，push被平台拦截

{now}。用户明确“能帮我把这个项目同步到GitHub吗”，本次由主控亲自执行该项Git操作，未转卡／未新占TASK，不改变TASK120分工或费用／运行许可。GitHub官方工具核shspic/RetroLume-agent为公开空仓库、具有push权限。筛选后的1227文件／47647036字节已形成不带本地旧父历史的公开根提交6a6bd79f9e6cfb09b2fa46efa87c38433c0dbb1c，tree299f8bde…7f82，保存在codex/github-sync-20261018；原main45951501…f702／HEAD／暂存区保持。

源码／迁移／锁／通用夹具／惰性样例／部署源码和必要第三方许可可审，DocuN/DocuS／旧内部根／真实配置与数据／证据／浏览器／依赖及镜像缓存不在公开树。9项初筛环境夹具及相关93文件和1个直接依赖被排除；三个公开文档变体只在快照，未改工程原件。工作源码出现的在途开发增量只按冻结时点保存，不宣告稳定或任务完成，不反向覆盖工程窗。

普通push在CreateProcess之前被auto_review拒绝，远端写0；其理由为具体约47MB/1227文件公开载荷尚缺明确确认、现证据不足以排除敏感。随后只读分支仍空。当前待用户对publication-review.md精确载荷一次确认，不拆分／API绕过，不重复构建或做无关测试。结果DocuN/results/GITHUB-SYNC-20261018-result.md；证据DocuN/evidence/github-sync-20261018。不是已上传或发布通过。

主控本轮产品测试／build／PG／Docker／业务Job／Browser／provider／费用0。Q和72h仍未启，S有限关闭及历史控制失败不变，原119/120完整采用／卡／预算均不改，STEP018整体/019/020/M1/项目仍未过。开发可按原卡继续，源和旧账未由同步改写。CHG1517—1523，下一1524。

## 以下为v2.73及更早历史

'''
arch_prefix = f'''# 架构动态文档

文档v1.47，2026-10-18，Asia/Shanghai。需求v1.4、执行动态v2.74；以下v1.46原字节保留。

## 实际Git拓扑与公开边界

{now}。按用户具体指派，主控准备公开源码同步。原本地main／私有历史和index不改，新增codex/github-sync-20261018公开根提交6a6bd79f…bb1c（无parent），其树1227项仅为冻结源码／迁移／锁／通用测试／样例和必要许可，排除内部编排／证据／配置／数据／运行产物。公开README与ignore仅在快照变体；工程无覆盖，无功能／部署／真实Q声明。

origin仍为用户指定公开GitHub仓库。普通非强制push尚未执行：被auto_review在进程创建前拒绝，远端再次核空，等待具体载荷公开确认。不重写远端，不通过API绕过，不以本地分支存在声称已同步。以后继续必须用本公开分支／已审树，不能直接push带旧内部历史的本地main。私有旧提交留在原机，其历史保存不代表允许公开。

本轮没有产品改动／测试／运行、仓库可见性调整或真实数据外发。Q v2与条件100/25采用、TASK120开发许可和独审门保持，未触用户库或原六资源。具体范围与证明见DocuN/evidence/github-sync-20261018/publication-review.md及commit.json。

## 以下为v1.46及更早历史

'''
write(state, state_prefix.encode('utf-8') + old[state])
write(arch, arch_prefix.encode('utf-8') + old[arch])
entries = [
 (1517, 'DocuN/evidence/github-sync-20261018', '用户具体指派Git同步，冻结清单／公开副本／本地根提交证明，未覆盖工程或原私有历史。'),
 (1518, 'DocuN/evidence/github-sync-20261018/publication-review.md', '列明需公开的1227文件精确提交／清单与排除，等待平台要求的具体范围确认。'),
 (1519, 'DocuN/results/GITHUB-SYNC-20261018-result.md', '记录已完成准备与被拒push，复用断点、不冒已同步，主控例外边界明确。'),
 (1520, 'DocuS/架构动态文档.MD', 'v1.47记录私有main与独立公开根提交拓扑，远端仍空，Q不启。'),
 (1521, 'DocuS/执行动态文档.MD', 'v2.74登记真实同步与自动审批阻断，TASK120和业务预算保持。'),
 (1522, 'DocuN/evidence/github-sync-20261018/push-blocked.json', '完整保留自动审批拒绝原因，process未启动／exit未知，不通过替代写入绕过。'),
 (1523, 'DocuN/evidence/github-sync-20261018/blocked-save-proof.json', '共享旧原字节／结果／范围完整保存与读回，不声称远端成功。'),
]
tail = '\n' + '\n\n'.join(f'- CHG-{n}，{now}，Codex编排Agent，{path}。{reason}' for n,path,reason in entries) + '\n'
write(change, old[change] + tail.encode('utf-8'))
assert state.read_bytes().endswith(old[state]) and arch.read_bytes().endswith(old[arch])
assert change.read_bytes().startswith(old[change])
save_json(HERE / 'blocked-save-proof.json', {
 'at': now, 'result': 'SAVED_AND_READ_BACK_PUSH_NOT_RUN', 'state': 'v2.74', 'architecture': 'v1.47', 'last_CHG': 1523,
 'commit': commit['commit'], 'remote_written': False, 'pending': 'specific_public_payload_confirmation',
 'documents': [{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
               for p in [state,arch,change,result_path,HERE/'publication-review.md']],
 'prior_shared_raw_bytes_preserved':True, 'no_product_tests_or_runtime_or_provider_spend':True,
})
print(json.dumps({'result':'SAVED_AND_READ_BACK_PUSH_NOT_RUN','commit':commit['commit'],'files':1227,
                  'publication_scope':str(HERE/'publication-review.md'),'result_file':str(result_path),
                  'state':'v2.74','architecture':'v1.47','last_CHG':1523},ensure_ascii=False))
