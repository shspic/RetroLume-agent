"""主控核断点、追加前向续作许可并保存完整现行卡；不执行产品。"""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import hashlib
import json
import re

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
OUT = Path(__file__).resolve().parent
TASK = ROOT / 'DocuN/tasks/TASK-114.md'
WORK = ROOT / 'DocuN/results/TASK-114-work-decision.md'
ARCH = ROOT / 'DocuS/架构动态文档.MD'
STATE = ROOT / 'DocuS/执行动态文档.MD'
CHANGES = ROOT / 'DocuS/文档变更记录.MD'
RESULT = ROOT / 'DocuN/results/TASK-114-result.md'
CONTROL = ROOT / 'DocuN/evidence/TASK-114/implementation/control'
CLOSURE = ROOT / 'DocuN/evidence/TASK-114/implementation/closure-20261013'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def identity(path):
    raw = path.read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def save_json(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


at = datetime.now(timezone(timedelta(hours=8))).isoformat()
received = load(OUT / 'received.json')
assert identity(RESULT) == {k: received['result'][k] for k in ('bytes', 'sha256')}
for row in received['identities']:
    assert identity(ROOT / row['path']) == {k: row[k] for k in ('bytes', 'sha256')}, row['path']
old = {path: path.read_bytes() for path in (TASK, WORK, ARCH, STATE, CHANGES)}
assert '文档v1.25' in old[ARCH].decode('utf-8-sig').splitlines()[2]
assert '文档v2.47' in old[STATE].decode('utf-8-sig').splitlines()[2]
assert 'CHG-1308' in old[CHANGES].decode('utf-8-sig')
assert 'CHG-1309' not in old[CHANGES].decode('utf-8-sig')
backup = OUT / 'before-documents'
backup.mkdir(exist_ok=False)
for path, raw in old.items():
    (backup / path.name).write_bytes(raw)
(OUT / 'receipt-before-continuation.json').write_bytes((CONTROL / 'receipt.json').read_bytes())

permit = {
    'permit': 'TASK-114-STEP017-C01-20261013', 'TASK': 'TASK-114', 'R': 'R-108',
    'created_at': at, 'status': '待人工转交；尚未实际接收或开始',
    'authorization': '原STEP017-P1明确采用，用户继续请求及此次请求主控追加续作；相同成果/资源种类/零真实费用',
    'original_anchor_utc': '2026-10-12T08:31:24.422001+00:00',
    'original_anchor_ns': 1065347750000000,
    'original_window_seconds': 28800,
    'elapsed_at_closure_seconds': 55525.796,
    'old_net_active_work': 'unknown，不以原墙时当净工时',
    'new_active_work_seconds': 21600,
    'calendar_horizon_seconds': 172800,
    'activation': '实际接收首工具记录UTC/mono；首个非只读续作开始活动段；内存不满足时无消费者、只读检查不激活活动段',
    'suspension': '仅真实外部等待/用户中断，所有本卡资源准确停止且无子进程并记录UTC/mono/原因/断点才可暂停；无记录间隔保守计入；普通修码计活动',
    'cleanup_seconds_reserved_in_active_work': 1200,
    'original_root_limit': 12, 'additional_root_quota': 6, 'cumulative_root_limit': 18,
    'conservative_root_baseline': 10, 'remaining_roots': 8,
    'root_facts': received['root_reconciliation'],
    'old_counts': received['old_receipt_counts'],
    'unchanged_limits': {'offline_seconds': 7200, 'holding_seconds': 10800, 'holding_business_seconds': 9600, 'pg_create': 12, 'pg_success': 9, 'pg_start': 32, 'preview_create': 2, 'preview_start': 2, 'api_start': 8, 'vite_start': 8, 'browser_start': 6, 'windows_start': 12, 'frontend_build': 6, 'running_containers': 2, 'fees': 0, 'provider_calls': 0},
    'remaining_unchanged': {'offline_seconds': 7155.948, 'holding_seconds': 10731.345, 'holding_business_seconds': 9531.345, 'pg_create': 11, 'pg_success': 8, 'pg_start': 25, 'preview_create': 2, 'preview_start': 2, 'api_start': 8, 'vite_start': 8, 'browser_start': 6, 'windows_start': 11, 'frontend_build': 4},
    'source_reuse': {'cid': '2659f71b56015c0de1be5a3d5790a47e0362139bbbaae45ad3a45bf562706c22', 'name': 'retrolume-task-114-data-source', 'volume': 'retrolume-task-114-data-source-data', 'port': 55461, 'image': 'sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f'},
    'used_logical_target_slots_not_released': ['target01', 'target02'],
    'new_target_slots_allowed': ['target03', 'target04', 'target05', 'target06', 'target07', 'target08'],
    'same_resource_roots_and_namespace': True,
    'new_product_or_provider_permission': False,
    'memory_gate_bytes': 2147483648,
    'memory_latest_checked': {'at': '2026-10-13T08:51:35.5579175+08:00', 'available_gib': 2.35, 'gate_met_at_sample': True, 'must_recheck_at_real_start': True},
    'audit': '完整稳定后隔离A+集中终审另卡；TASK115未占号',
}
save_json('continuation-permit.json', permit)

text = old[TASK].decode('utf-8-sig')
sections = re.split(r'(?m)^## ', text)
parts = {part.split('\n', 1)[0].strip(): part for part in sections[1:]}
assert len(parts) == 9
goal = '''目标与交付

你沿TASK114/R108原A+工程窗口接续，完成同一个已采用STEP017-P1成果。候选主体已写入，直接从未闭合的真实恢复、竞态、删除、维护/只读选择及HTTP/浏览器接续；保留当前197份源码、source数据、现存完整包和全部失败，不重新搭建或重复已充分且未变的验证。

授权终点仍是完整可携导出、备份、隔离永久只读恢复、准确资料删除与用户工作区的稳定候选和相关真实证据。普通实现/夹具修复和实际影响复验卡内连续，整卡完成或真实停止门才回传。本卡不是独立审计，最终裁定仍主控。

结果仍保存 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-114-result.md，置顶续作01，当前34931字节/SHA-256 c655556d7b783a871e34c5a50c40cb9d477504d0b8d389f028e14f68b091d1af全文原字节保留。新证据只入 DocuN/evidence/TASK-114/implementation/continuation-01/，原control/events和闭环证据保留，不并行第二套总资源账。
'''

rules = parts['项目、规则与接收安排'].replace('架构v1.25、执行动态v2.47', '架构v1.26、执行动态v2.48')
rules = rules.replace('本任务实际执行尚未开始；新额度是前向授权，旧投入仍在历史账，不追认既往偏差。', 'TASK114已实际返回未完成候选，原时间许可已结束。现以主控续作01许可前向接续，旧投入/失败/锚点/资源不清零，历史原窗口超时不追认。')
rules += '''
此次主控许可 TASK-114-STEP017-C01-20261013，具体预算/口径/资源绑定见 DocuN/evidence/TASK-114/orchestration-continuation-01-20261013/continuation-permit.json。用户原技术采用无需再批。本卡优先原TASK114工程窗口；原窗口确实不可用才同等A+新窗按断点恢复，不让其他窗口同时改文件。
'''

context = parts['背景与最小充分上下文'] + '''
当前最先补读 TASK-114-result.md的断点/第六至十一节，implementation/closure-20261013的change-index、final-source-manifest、final-bundle-manifest、as-run-to-final、budget-reconciliation-note、hub-readonly-observation，以及本次主控received.json。197源码/4bundle/现存包与封存逐字节匹配；38既有文件修改/52新增/107未变只是身份事实，不是完整验收。

最终013为64872字节/SHA-256 15074997652bae1e66e2f7237a7e68d98e2164f5e148460d900adfe374520e4f，schema.py为43592字节/cb1d30a26154402775cf50f24dead1e89d26b590219c79d96b3c0e09cfb35fd5，preview指纹11265108b26ef6242012c8d03841c74d736ef0099bd7c40e4696f1d470aa250d。它们是本轮pre基线，必要修正留pre/diff/post，不覆盖原副本。

已发布checkpoint 737bf7ba-18c2-436c-a011-3aabbc1a8b2b，306945字节，文件45177d58ea58fcaa704bfdd48641aceade7ca6e6f4fe5d6759b3a46bf2671665，root312e673b22e0957217c74d116ed3de6d1b068a1124b1fc2939b11385f8be8d10。现存计划271e9dd7-e982-4daa-9854-4beffac445a1须重核准确plan hash/删除旁证；不能取任意latest plan或因上次FAIL重新打包。source实际28非空fixture完整，最末source前缀绑定最终产品；source-forward整批仍FAIL，权限SQLSTATE/行值没有独立原始落盘的子项须定向补证，不补造旧日志。

最后target-saved在create前内存失败，未有target DDL/load/seal；两个target01/02意图仍allocating无CID，restore job已failed，原Hub19完整frame/六jobs无selector_commit/维护fence。不把stopped容器当source业务frozen，不从失败job复活owner或自动reset为prepared。
'''

required = parts['必须形成的完整产品成果']
required += '''
续作实际顺序：先离线修正本卡计数/分段许可和日志，再用现存包、source保持Stopped完成target03的最终001—013/九guard/两FK/全关系原件加载/真实撤权readonly回查。成功后按剩余矩阵合并补source准确权限/字段观测、真实T与最后检查/unlink竞态、共享删除/内存和旧包覆盖、四账/历史反例、ControlHub/维护fence/selector；最后同最终字节接HTTP和浏览器。失败先留精确SQLSTATE/阶段/原件并据实修复，不再只在整批成功时输出此前通过子项。

已有fixture的deadline可能因隔夜而过期：历史值及包不改，需要正向live资格时用正常仓储新增准确合成ID；不改系统/DB时钟、不更新旧行deadline或重复seed。013 source已前向补四函数，source数据/迁移前后值保持；不重跑初始化。新空target必须真实一次安装最终001—013。013新增FK/role/ACL/guard的schema指纹兼容须核精确对象，不以泛过滤所有type=t约束通过，坏定义/缺约束应拒绝。
'''

allowed = parts['允许文件和独占范围']
resources = parts['精确新资源与凭据']
resources = resources.replace('TASK-114-STEP017-IMPLEMENT-20261012', 'TASK-114-STEP017-C01-20261013')
resources += '''
续作覆盖：source不是新建，唯一可复用CID为2659f71b56015c0de1be5a3d5790a47e0362139bbbaae45ad3a45bf562706c22，准确label为retrolume.task=TASK-114、profile=TASK-114-PG17、job=f934ac64-4dce-4f8c-8442-15b283f2d48d；卷/端口/image固定如上，当前Stopped/Pid0。只允许准确重启和继续合法同库操作，不recreate/DROP/reinstall，凭据由原DPAPI受限引用获取，不reset来绕过。

target01/02已由真实工厂意图占逻辑slot，即使物理create=0也不回收；两个失败意图/业务键原样保留，下一目标固定target03，之后仅04—08。不得改profile名字/端口/新根绕过slot。两次空内存失败不继续机械尝试；入口在调用verify/allocate和写新job/intent之前先核当前内存，达到原2GiB门才进新目标路径，hook可再核但不足时精确收尾，不再不断生成新failed job。

用户已释放内存，主控2026-10-13T08:51:35+08:00实核可用2.35GiB达到原门。该采样不保证之后每步；第一恢复阶段只启动一个target、source保持Stopped，降低组合压力；后续source+target/Browser开跑前再核。暂不足时停止/封存全部本卡消费者，仅推进不依赖真实资源的准备，不能降低2GiB门或停止用户软件/daemon。
'''

budget = '''预算、连续批次和异常处理

旧许可记录/原首锚点1065347750000000ns及2026-10-12T08:31:24.422001Z保留；旧28800秒已结束，封存观测elapsed55525.796秒，净活跃投入unknown。不是把旧墙时清零或追认已过期运行。此次新许可只前向授权21600秒活动工时，实际接收记录UTC/mono和本许可hash；首个非只读续作/修码开始活动段，并另记接收到首段的准备时长。

每段start/end/原因有日志。普通阅读/实现/修码/测试均计活动工时；只有真实外部等待或用户中断、全部本卡资源准确Stopped且无子消费者、已保存完整断点并登记暂停UTC/mono时才可暂停新活动计时。无暂停记录的间隔保守计入，不能自己称空闲剔除。最多接受后48小时日历窗，不让前向许可无限有效；活动工时最后1200秒只清场。此为执行预算，不改变生产窗口/租约/ready/D/停止证明或任何账。

真实批次口径核正：原raw real_roots=7是七目录计数错误，原receipt/events/closure原件保存。已证实8个PG资源批+1个Windows锁批=9，target-saved创建前失败单列；前向预算保守扣10，不把其当10个已实际创建/运行根，不返还目录错计。原根上限12追加6至累计18，按保守基线10剩8个真实根；本次新量不是清零旧失败。一个真实根是预先登记的合并业务入口，内含有限多个既定方法/准确启停，不逐方法或每target都多占根；FactoryHooks只登记对象create/start，不重复新根。纯目录/静态parse/metadata不占真实根，第一次真实create/start/SQL/HTTP/Browser/真实OS child前才begin_root。同根普通修正也记失败，不换根重试清计数。

其他总上限完全沿原卡，不加容器/镜像/端口/费用：offline7200已44.052，剩7155.948；真实持有10800已68.655，剩10731.345，业务门9600剩9531.345、最后1200只清场。PG create已1/12、成功物理对象1/9、start7/32；preview create/start0/2、API/Vite0/8、Browser0/6、Windows1/12、build2/6。原控制账的各数原样保留，余额不是新的额外一套上限。

所有容器/API/Browser/Job持有仍按实际连续经过时间累计，暂停活动工时不能暂停其Running/持有。原current receipt是唯一实时计数/资源账：先在本轮留完整old receipt及events身份，追加本许可和legacy/canonical roots/计时分段、保持原锚点/原计数事实，执行adapter按该许可而非旧已结束墙窗校验。不得直接把old received_monotonic_ns替成现在、删除事件或重跑bootstrap归零。closure旧原件保持不改。

离线先修budget.py/source与factory hooks的根语义、活动许可和finally/渐进证据落盘，做最少无资源自检；不扩建平台。每个方法立即保存as-run/argv脱敏/exit/耗时、期待/实际/SQLSTATE或真实回执，后续失败不丢前缀。原失败栈缺SQLSTATE与首dist pre不存在如实保留；新补证是现在的新运行，不回填旧证据。

两次有证据修正同因仍失败、超任一累计上限/48小时日历窗、新高风险/超权限或资格未知停受影响消费者并交回；普通可定位修复按本卡连续。已成立且未变的字节/包/正常source值/前缀直接复用，实际改变处才复验。完整通过即停，不用满所有slot/工时。
'''

verification = parts['验证、证据与审计关系']
verification += '''
续作优先关闭报告中的V06/V08/V09目标真值、V04/V14准确竞态、V22/V28/V29维护/权威、V24/V25真实用户流，并合并其余29项子分支，不把“部分观察”改称完整PASS。对初始8单测/中间离线结果以as-run-to-final核实际路径是否未变，不能无条件继承早期字节。故意断尾的旧offline-control不重跑不清除，需要复验相关分支用本轮新scratch准确子目录。

最终source/bundle发生修改须新pre/as-run/post及真实层复验；未改最终bundle可直接用于真实Browser，不为标签重build。原全部V项不完整，不能先发完整终审；待剩余实现/运行及准确收尾完结再由主控另卡隔离集中独审。
'''
stop = parts['精确清场、停止与回传']
stop += '''
当前旧报告34931字节全文保留作后缀，续作结果置顶同一文件。新增签名/产品改动和根补账/计时修正给主控同步，不自写DocuS/CHG/公共库。此次所需人工仅转同一窗口，内存已实核达到门，无须重新采用技术包。若资源再不足，给准确采样与暂停证明，不机械开启目标或改旧计数。
'''

updated = '# TASK-114 / R-108 续作01 — 保留候选，完成真实恢复与剩余完整链\n\n' + '\n\n'.join('## ' + part.strip() for part in (goal, rules, context, required, allowed, resources, budget, verification, stop)) + '\n'
assert len(re.findall(r'^## ', updated, re.MULTILINE)) == 9
assert '*' not in updated and '|' not in updated
(OUT / 'effective-contract.md').write_text(updated, encoding='utf-8')

work_prefix = f'''# TASK114/R108续作01前向许可（当前有效）

{at}，Codex编排Agent。用户继续原任务且交回114未完成/请求主控追加续作额度；原STEP017-P1采用不变。本主控核证197源码/4bundle/现存完整包逐字节匹配、source准确Stopped/无业务端口，接受为部分候选，不签完整实现/动态通过。结果34931字节/c655556d…d1af原件不改，当前source/28表和全部失败保留，真正待关闭为恢复/权限、竞态/删除、停线/选择及HTTP/UI。

前向许可TASK-114-STEP017-C01-20261013：追加21600秒有证据分段活动工时，只有外部等待/用户中断且全部资源准确停妥才可暂停；普通实现修码计时，未记录间隔保守计。接受后48小时日历门，活动最后1200只清场。旧28800秒/锚点、55525.796 elapsed及净活动unknown保历史，不以暂停新预算追认旧超时。生产monotonic窗口/ready/D/账面计时不改。

根口径核正为已证实9资源批次+独立创建前失败1项，前向保守扣10；原七目录错计不删不返。原根12加6至累计18，剩8根。其余offline/持有/create/start/Browser/Windows/build/费用上限不加：旧44.052和68.655、PG1create/7start、Windows1/build2继续累计。先修runner与渐进日志，不自己把旧receipt锚点换成现在；current唯一账升级带legacy及本许可，原close/events原文保存。

只复用准确source CID2659f71b56015c0de1be5a3d5790a47e0362139bbbaae45ad3a45bf562706c22。target01/02意图占slot即使无CID也保留；新目标03—08，其他资源/role/端口/目录与原卡不变。第一恢复source保持Stopped用现存包，按原2GiB内存门启动target。主控用户释放后08:51:35实核2.35GiB满足，但执行仍按实时门。没有新付费/user库/扩大执行恢复资格。

原A+114工程窗口独占继续，完整现行任务卡已经重写，不让执行者拼接冲突预算；普通修复卡内收口，完整稳定后隔离集中独审。TASK115仍计划未派/未占；原G11和旧25等不重开。此轮主控只核文件和元数据/维护文档，产品运行0。

## 以下为原实施许可历史原字节

'''
WORK.write_bytes(work_prefix.replace('\n', '\r\n').encode('utf-8') + old[WORK])

arch_prefix = f'''# 架构动态文档

文档v1.26，2026-10-13，Asia/Shanghai。需求v1.2、执行动态v2.48、task_model/07；以下v1.25历史原字节保留。

## STEP017候选主体已形成，真实恢复与完整链待续作

{at}。TASK114已返回未完成实施候选：17个data_exit生产模块、013/配置/CLI/前端工作区和跨域围栏接线已写入，38既有改动/52新增/107不变，封存197源码与4bundle相符。source合法非空001—012→当时013及四函数前向修正保旧业务值，最终31安全域完整checkpoint已发布；这是部分真实前缀，不把整批FAIL或build当完整产品通过。

新隔离target仍未创建，最终001—013/加载/撤权、准确新引用-unlink迟到竞态、删除覆盖、source停线/selector/只读绑定与真实HTTP/UI尚未验证。source准确Stopped不等于业务frozen；两个allocating无CID意图和失败job保留，无selector/fence事件。013/schema/preview指纹候选涉及历史加载和ACL，仍须最终版真实验证及集中独审。

续作01采用原方案/权限/资源，优先现存完整包单target恢复；只新增执行工时和有账根额度，生产monotonic窗口/账守恒/权限模型不因计时停顿变化。永久只读不完成全部NFR005持续使用，原Must/G11有限关闭、旧unknown/历史预算和STEP018—020维持。尚不放行用户库/真实资料/费用或生产能力。

## 以下为v1.25及更早历史

'''
ARCH.write_bytes(arch_prefix.replace('\n', '\r\n').encode('utf-8') + old[ARCH])
TASK.write_text(updated, encoding='utf-8')

state_prefix = f'''# 执行动态文档

文档v2.48，2026-10-13，Asia/Shanghai。唯一总状态账；需求v1.2、架构v1.26、task_model/07。以下v2.47历史原字节保留。

## TASK114未完成候选已回收，续作01待人工转交

{at}。TASK114/R108实际接收/执行/返回已经发生，当前结果34931字节/c655556d7b783a871e34c5a50c40cb9d477504d0b8d389f028e14f68b091d1af。197当前源码/4bundle与原封存逐字节匹配，38改/52新/107未变；001—012/公共七规则未漂移，完整checkpoint306945字节/45177d58…1665存在。成果验收为部分，所有V01—29仍部分观察/not_run，不能直接派完整终审。主体实现候选/部分source升级与包，target恢复/竞态/删除/维护/HTTP/UI待。

source准确CID2659f71b56015c0de1be5a3d5790a47e0362139bbbaae45ad3a45bf562706c22 exited/Running=false/Pid0，固定image/卷/label/资源/55461匹配；本卡业务端口无监听、无在途API/Browser/目标。target01/02两失败意图allocating无CID保留，后续slot03—08；源业务normal不以Stopped冒frozen，现存Hub无selector/fence。

原实施接收锚点2026-10-12T08:31:24.422001Z/1065347750000000ns、28800秒窗已结束，封存elapsed55525.796、净活动unknown。原raw roots7为七目录错计，实据8PG批+1锁批=9，另target-saved创建前失败独立；前向保守扣10，原日志/错计不删/不返。old offline44.052/7200、hold68.655/10800，PG create1/12/成功1/9/start7/32、Windows1/12、build2/6、API/Vite/Browser/preview0及旧商业费用全保留。

用户继续请求及此次未完成交回支持同边界前向续作，技术采用不需重批。新许可TASK-114-STEP017-C01-20261013：21600秒分段活動工时，接受后48小时日历门，最后1200只清场；只有外部等待/用户中断且所有资源准确停妥/无消费者/暂停时间原因断点登记才可暂停活动，未记录间隔保守计。生产期限不改，真实资源持有永远连续计。根上限12加6至累计18，保守基线10剩8；其他资源种类/数量/子预算一律不加，旧source准确复用，不清root/slot/job。

续作原TASK/R/原A+工程窗口，完整卡DocuN/tasks/TASK-114.md已保存复读待人工转交；本续作实际派发/接收/新运行尚0，无子Agent/并行。先runner补账与渐进日志，现存包单target真实恢复，再合并其余矩阵和最终HTTP/UI，普通修正卡内连续；稳定后另隔离A+一次集中独审，TASK115/R109仅计划未占号。

内存曾不足2GiB阻目标；主控问后用户释放，2026-10-13T08:51:35+08:00实核可用2.35GiB达到原门，真实开跑再核；不以内存等待反复写新target意图。原源码/事件/包/失败、G11/旧25/R60/count1/13元/626.566全部保留。永久只读不签完整NFR005/STEP018—020/M1/发布/项目，真实用户库/数据/私配/费用不许可。

主控只做文档/身份/元数据核对，产品运行0。核证/预算/窗口/完整卡及原卡/旧共享字节在DocuN/evidence/TASK-114/orchestration-continuation-01-20261013，current控制总账仍implementation/control，不另维护第二实时账。CHG1309—1317，下一1318。

## 以下为v2.47及更早历史

'''
STATE.write_bytes(state_prefix.replace('\n', '\r\n').encode('utf-8') + old[STATE])
save_json('window-assignment.json', {'TASK': 'TASK-114', 'R': 'R-108', 'continuation': '01', 'recipient': '原TASK114工程窗口', 'execution': 'A+', 'reported_client': 'Codex工程窗口', 'exact_model_and_window_id': '不可核，不要求已完成工作因型号重做', 'manual_transfer': True, 'dispatch_confirmed': False, 'new_execution_started': False, 'parallel': False, 'subagent': False, 'audit_window_kept_separate': True})
entries = [
    (1309, 'DocuN/evidence/TASK-114/orchestration-continuation-01-20261013/received.json', '实核197源码/4bundle/包/七规则，部分成果不冒动态验收。'),
    (1310, 'DocuN/evidence/TASK-114/orchestration-continuation-01-20261013/continuation-permit.json', '前向活动工时与48小时/精确暂停条件，root补账保守基线10/上限18，子预算/资源不扩。'),
    (1311, 'DocuN/results/TASK-114-work-decision.md', '原TASK/R续作01许可、原窗口与准确source/slot、保旧时钟/失败/未验证。'),
    (1312, 'DocuN/evidence/TASK-114/orchestration-continuation-01-20261013/effective-contract.md', '完整现行卡一次重写，直补真实恢复/剩余矩阵，不让执行者拼旧预算。'),
    (1313, 'DocuN/tasks/TASK-114.md', '续作01完整卡保存复读，原首轮任务卡原字节保留，待人工转交。'),
    (1314, 'DocuS/架构动态文档.MD', 'v1.26主体候选/部分source包及实际未验证，权限/只读需求边界不变。'),
    (1315, 'DocuS/执行动态文档.MD', 'v2.48唯一账，旧真实执行已返回/续作未派/内存门已采样满足/原预算缺口保留。'),
    (1316, 'DocuN/evidence/TASK-114/orchestration-continuation-01-20261013/window-assignment.json', '原A+工程窗接续，人工闭环、隔离审计待稳定。'),
    (1317, 'DocuN/evidence/TASK-114/orchestration-continuation-01-20261013/delivery-proof.json', '一次完整卡/许可/源及原结果保护/共享历史与CHG核对。'),
]
addition = ''.join(f'\r\n- CHG-{number}，{at}，Codex编排Agent，{path}。{note}\r\n' for number, path, note in entries)
CHANGES.write_bytes(old[CHANGES] + addition.encode('utf-8'))

assert identity(RESULT) == {k: received['result'][k] for k in ('bytes', 'sha256')}
for row in received['identities']:
    assert identity(ROOT / row['path']) == {k: row[k] for k in ('bytes', 'sha256')}, row['path']
for path in (WORK, ARCH, STATE):
    assert path.read_bytes().endswith(old[path])
assert CHANGES.read_bytes().startswith(old[CHANGES])
assert (CONTROL / 'receipt.json').read_bytes() == (OUT / 'receipt-before-continuation.json').read_bytes()
assert identity(CONTROL / 'events.jsonl') == received['old_events_identity']
assert TASK.read_bytes() == (OUT / 'effective-contract.md').read_bytes()
assert '本卡真实资源持有时间合计10800秒，其中最后1200秒' not in updated
assert '28800秒；实施/阅读/文档在此总窗内' not in updated
assert '本任务实际执行尚未开始' not in updated
assert not (ROOT / 'DocuN/tasks/TASK-115.md').exists()
for number, _, _ in entries:
    assert CHANGES.read_text(encoding='utf-8-sig').count(f'CHG-{number}，') == 1
save_json('delivery-proof.json', {'at': at, 'TASK': 'TASK-114', 'R': 'R-108', 'continuation': '01', 'task': {'path': str(TASK), **identity(TASK)}, 'status': '待人工转交，未冒已派发', 'source_bundle_and_result_unchanged': True, 'old_receipt_events_preserved': True, 'prior_shared_documents_byte_exact': True, 'old_task_preserved': identity(backup / TASK.name), 'product_runs': 0, 'resources_started': 0, 'CHG_range': [1309, 1317], 'next_CHG': 1318, 'scope': '同一已采用成果，前向工时/root追加，实际生产预算与资源数量不扩', 'consistency': '一次合同与许可/状态/资源/暂停条件/余额/历史保护检查'})
print(json.dumps({'task': str(TASK), **identity(TASK), 'status': '待人工转交', 'execution': 'A+原TASK114窗口', 'architecture': 'v1.26', 'state': 'v2.48', 'CHG': [1309, 1317], 'product_runs': 0, 'source_and_result_preserved': True}, ensure_ascii=False))
