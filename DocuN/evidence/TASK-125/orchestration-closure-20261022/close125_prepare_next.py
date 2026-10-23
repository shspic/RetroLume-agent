"""主控仅核回传原件、关闭工程及准备待采用的后续范围；不运行产品。"""
from pathlib import Path
from datetime import datetime, timedelta, timezone
import hashlib
import json
import re

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent').resolve()
OUT = 'DocuN/evidence/TASK-125/orchestration-closure-20261022/'
TZ = timezone(timedelta(hours=8))


def p(relative):
    dest = (ROOT / relative).resolve()
    dest.relative_to(ROOT)
    return dest


def read(relative):
    return p(relative).read_bytes()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(relative):
    return json.loads(read(relative).decode('utf-8-sig'))


def put(relative, raw):
    dest = p(relative)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw.encode('utf-8') if isinstance(raw, str) else raw)
    return dest


def dump(relative, value):
    return put(relative, json.dumps(value, ensure_ascii=False, indent=2) + '\n')


PROPOSAL = r'''# AP-125-NORMAL-INSTALL-01 关闭外发的本地真实安装验证采用包

状态为待用户采用，不可执行。本包只提前把后续新资源、写入及验证边界列完整，不占新的TASK/R，不创建资源或恢复旧运行许可。当前TASK125离线工程与TASK126代码门已由主控关闭；真实安装和Q从未因此获得执行权。

## 本次需要的一项决定

是否采用下述一个合并包，授权新建至多两个彼此隔离的本地PG容器及独立数据卷，使用已独审的正式安装器执行新空库001—015和角色创建，完成首轮独审规定的六项真实检查，以及主正常库的关闭配置启动、同库重开和停止。全部合成、零外网模型/Embedding/费用，不涉及旧库、用户资料或用户库。只有此一项决定，无新的模型/供应商/业务或费用取舍。

之所以需要确认，是原125/126执行合同的PG、容器、角色和实际apply均明确为0；公共AGENTS第2节还要求权限调整等高影响动作有覆盖对象和范围的明确授权。代码门通过不是新资源或DDL/DCL授权。批准后主控才按本包登记下一正式任务卡并给执行许可，不让工程者凭本草案开工。

## 固定对象及资源上限

只使用本机已缓存并核对的pgvector/pgvector@sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f，不拉取/构建/升级。目标PG17、vector0.8.6；首次预检不匹配就带回实际差异，不能换镜像碰运气。

两个槽位串行运行，任何时刻最多一个PG容器活跃。

- source槽位，容器retrolume-q-first-normal，卷retrolume-q-first-normal-data，逻辑库retrolume_q_first_normal；Compose项目retrolume-first-install-source。它是未来正常源的持久安装候选，先保持所有外发关闭，不重建或换库重置任何未来预算。
- interrupted槽位，容器retrolume-install-interrupted，卷retrolume-install-interrupted-data，逻辑库retrolume_install_interrupted；Compose项目retrolume-first-install-interrupted。只作真实SQL一次提交未知/中断保留验证，不作为可运行正常源，不自动续装或清空。

每槽位至多一次容器创建尝试和一个专有新卷；若名字已有对象，先只读核归属，非本次对象就停止该槽位，不覆盖/删除/接管或静默换名。最多两个Compose专属bridge网络，不使用host网络或host bind。CPU1、内存512MiB、pids128、restart=no、仅127.0.0.1映射、pull_policy=never。使用既有deploy/compose.local.yml的pg服务，两个项目隔离；不启用renderer-build profile、不构建或启动预览。未启用预览变量如需Compose插值，使用明确无激活作用的本机占位，不读取旧私有预览配置。

source的PG端口按顺序在55482、55484、55486中只读检查并短时bind核可用后一次选定，interrupted在55483、55485、55487中选定；本地API在18122、18124、18126中选定。只选择已批准候选，选定即写本任务身份账，不因后续失败轮换端口绕计数。没有可用项则停止相关段，不改Windows排除范围、不重启宿主网络或Docker服务、不结束他人进程。

新私有根仅D:/shspic/project_NO3_RetroLume-agent/.runtime/normal-first-install/source及interrupted。source内分别建立独立data/backup/control/restore、私有安装/原生关闭配置和新收据目录；根须原先不存在，拒绝已有归属不明、junction、重叠和越界。既有.gitignore已排除/.runtime/，不将凭据或实际私有配置写进可公开证据。

实际CID、卷/网络ID、选定端口、system_identifier、数据库OID、当前Windows SID和根device/file-id只在获准创建后读取并绑定；未发生时为空，不能在本草案伪造。三个安装UUID由受信新根绑定产生并一次记录；应用身份与正常控制行保持同一来源，不造Q InstanceBinding或grant。

仅新集群bootstrap管理员用于短时安装；source登录固定为retrolume_normal_app与retrolume_normal_snapshot，interrupted预定retrolume_interrupt_app与retrolume_interrupt_snapshot。两个新集群的13个NOLOGIN职责组由原001—015按原文创建，登录通过已审权限分工创建，不给业务管理员权限，不复用或修改任何旧集群角色。随机密码/维护秘密只经安全stdin或进程环境注入，无值进入argv、日志、证据或报告。禁止输出docker inspect Env或Compose展开后的凭据配置。

## 六项合并检查

1. 同一source新空库的精确错误OID/system_identifier拒绝，以及非空/职责组碰撞拒绝。允许在这个本次新空库建立并精确撤销public.retrolume_install_probe_nonempty表和retrolume_data_app NOLOGIN碰撞组，先记录它们原本不存在及创建OID，只撤销本轮同身份对象，不清空库、不碰别的对象。反例每次用独立拒绝收据，确认真实入口命中对应原因和零安装器数据库写；先关闭旁观元数据连接，不能所有反例只命中other_clients就冒充覆盖。
2. source空库用正式deploy/initialize_normal.py真实apply，原样执行001—015，观察013后R01、014/R02、015/R03、原schema/role验证及37条完整成功收据。可用测试连接包装器观察真实COMMIT后的阶段，不替代SQL或核验函数。安装器代码冻结为29403字节/hash68d7b71fc7296111e894df4cba21a4ed7830f9cff069c1fc500dfbd7734c0a09。
3. 同库分别用新业务/快照真实登录，核权限、控制行和实际可读性；用真实权限查询或有界事务拒绝检查，确认snapshot不能业务写、读维护秘密或SET到业务/owner，业务无管理/owner/传递SET/INHERIT/ADMIN越权。不重跑旧全安全矩阵，不给应用安装管理员连接。
4. 使用现有start_local.py的--container、--port、--shutdown-stdin和原生配置，关闭model/integration/Q/preview，建立真正normal源绑定与ControlHub，仅启动一个本机API。读取实际capabilities/readiness，正常停止后用同一库/根再开一次，核无自动迁移/新身份/重置和原记录不变，再正常停止。无需浏览器、业务worker、模型、索引、活动或付费账。关闭配置的真实部署可在账号/token等待期间独立验证，但不冒称Q外部门通过。
5. interrupted槽位真实执行同一原SQL，在事先固定的002提交应答边界制造一次提交未知。包装器必须先真实执行并提交该SQL才隐藏一次确认；记录真实DB状态与001已确认、002 submitted/unknown、无003/complete/自动重放。原收据重用和verify在本地拒绝，新收据对部分库也应零写拒绝。保留部分库和卷，不续装、清空或退款。
6. 回source成功库真实verify，仅注入安装管理员密码引用、不提供另三秘密；核READ ONLY、schema/roles/身份和收据不变。错误收据绑定在连接前拒绝。各步骤共享身份和检查点，一次合并回传。

## 资源、失败与停止

低内存明确采用本包的串行门，不恢复一般2GiB要求。Docker已可用后，每次启动PG或API前可用物理内存至少512MiB；约2秒采样，连续两次低于256MiB时停止新动作并有界关闭本任务自有API/PG。不要求用户反复释放内存，不启用浏览器/renderer/第二活跃PG。

总工具最多10800秒含900秒保存/收尾，获准正式签发后日历24h；PG累计持有最多1800秒，API累计持有最多900秒。PG source启动最多4次，interrupted最多2次，API最多3次，其中source安装/正常开/同库重开为既定需要，其余只能针对具体有据修正。至多一个合并初验入口及两次只恢复失败/未完成段的有据续验；不会为文件读取、未执行的审批拒绝或单方法拆根次数。准备和入口失败如实留账，不把失败清零。

新建容器/卷/网络/库和反例对象的授权仅覆盖上述固定范围。所有成功对象和失败卷保留，收尾只有精确CID/创建ID核对后的停止和本卡API树关闭，不docker prune、不compose down -v、不DROP DATABASE或清理旧资料。本包不允许重复创建同槽位、换名重试、重置角色密码、扩内存、拉镜像或改系统。已完成阶段用原始检查点/受测版本证据继承，不能因重开runner重放DDL。

先离线准备完整runner和身份/预算/原始日志控制，再一次进入真实段；不因切到下一正常步骤就回传。若纯测试夹具明确出错，保留失败并仅修本卡验证夹具，在预算内定向复检后继续余段。若发现产品确定缺陷、安装器未知提交、同根因两次有据修正仍失败、需要扩大权限/改SQL/新平台或限额到门，则停止受影响段，完成不受阻项后一次回传。不承诺未运行必过，也不再用大量小续卡机械重试。

## 绝不包含的授权

Q仍关闭，T0/72h为空，不创建三固定业务活动或grant，不绑定QAuthority，不索引/查询/生成，不访问真实provider或Embedding/计量接口；100次25元及分额原封不动。无网络下载/依赖安装/镜像构建/浏览器/业务Job/HTML预览/用户资料或用户库操作，Git写入为0。现有两个provider与计量/账号/token/模板/容量外部缺口继续保留，不以真实安装成功代替。

不修改已审安装器、001—015、业务app/角色/profile/Grant/现启动入口或正式Compose。实现/验证辅助脚本只属本任务证据，产品运行继续走正式工具。可按真实已验证结果最小更新README和normal-install.md的用户说明，不预写通过。独审已通过的未变代码不再审一遍；主控核最终真实原件，新增安全差异才决定相应集中审查。

批准本包只使上述关闭式验证具备授权依据。主控仍需登记正式任务及启用范围后，用户再转交原TASK125工程窗口；本草案本身不执行。完成不等于STEP018/019/020、M1或项目通过。
'''


def main():
    now = datetime.now(TZ)
    stamp = now.isoformat()
    state_rel = 'DocuS/执行动态文档.MD'
    arch_rel = 'DocuS/架构动态文档.MD'
    changes_rel = 'DocuS/文档变更记录.MD'
    d125 = 'DocuN/results/TASK-125-work-decision.md'
    d126 = 'DocuN/results/TASK-126-work-decision.md'
    t125 = 'DocuN/tasks/TASK-125.md'
    t126 = 'DocuN/tasks/TASK-126.md'
    originals = {name: read(name) for name in (state_rel, arch_rel, changes_rel, d125, d126, t125, t126)}
    assert '文档v2.96' in originals[state_rel].decode('utf-8-sig')[:120]
    assert '文档v1.68' in originals[arch_rel].decode('utf-8-sig')[:120]
    assert max(map(int, re.findall(r'CHG-(\d+)', originals[changes_rel].decode('utf-8-sig')))) == 1650
    assert not p('DocuN/tasks/TASK-127.md').exists()
    assert '*' not in PROPOSAL and '〈' not in PROPOSAL and '| ---' not in PROPOSAL
    audit_closure = load('DocuN/evidence/TASK-126/audit/review-01/closure.json')
    manifest = load('DocuN/evidence/TASK-126/orchestration-review01-20261022/input-manifest.json')
    checks = []

    def verify(source, expected, group, count=None, relative=None):
        source = Path(source)
        raw = source.read_bytes()
        actual = sha(raw)
        assert actual == expected, (str(source), expected, actual)
        assert count is None or len(raw) == count, str(source)
        checks.append({'path': relative or str(source), 'absolute_path': str(source), 'bytes': len(raw),
                       'sha256': actual, 'group': group, 'match': True})

    report_rel = 'DocuN/results/TASK-126-result.md'
    current_report = audit_closure['new_report']
    verify(p(report_rel), current_report['sha256'], 'audit_current_report', current_report['bytes'], report_rel)
    for row in manifest['sources']:
        if row['path'] == report_rel:
            continue
        verify(row['absolute_path'], row['sha256'], 'review_frozen_input', row['bytes'], row['path'])
    report = read(report_rel)
    old_hash = 'b1f52e0284e37b5e67f28ef1a1c2dee7d1c7d255a3e090d1478bc5747d72b1d3'
    assert sha(report[-33379:]) == old_hash
    assert report[:16706] == read('DocuN/evidence/TASK-126/audit/review-01/review-01-addition.md')
    for row in audit_closure['artifacts_before_closure']:
        relative = 'DocuN/evidence/TASK-126/audit/review-01/' + row['name']
        verify(p(relative), row['sha256'], 'review_artifact', row['bytes'], relative)
    reception = load('DocuN/evidence/TASK-126/audit/review-01/reception-identity.json')
    for row in reception['bindings']:
        verify(p(row['path']), row['sha256'], 'review_permit_binding', relative=row['path'])
    static = load('DocuN/evidence/TASK-126/audit/review-01/static-review.json')
    for row in static['unchanged_dependency_hashes']:
        source = row.get('absolute_path') or str(p(row['path']))
        verify(source, row['sha256'], 'inherited_original_dependency', row.get('bytes'), row['path'])
    tested = load('DocuN/evidence/TASK-125/execution/repair-01/tested-before-batch-03.json')
    for row in tested:
        verify(p(row['path']), row['sha256'], 'batch03_current_binding', row['bytes'], row['path'])
    engineer_closure = load('DocuN/evidence/TASK-125/execution/repair-01/closing-receipt.json')
    verify(p('DocuN/results/TASK-125-result.md'), engineer_closure['result']['sha256'], 'engineer_current_report',
           engineer_closure['result']['bytes'], 'DocuN/results/TASK-125-result.md')
    assert sha(read('DocuN/results/TASK-125-result.md')[-15686:]) == '78a80de9633ad13b703262850782ddbcbef3d4ef50632b255e319147a3715404'
    assert audit_closure['independent_static_review']['batch03'] == {'tests_run': 9, 'failures': 0, 'errors': 0, 'skipped': 0}
    assert audit_closure['budget']['cumulative_conservative_seconds'] == 2400
    assert engineer_closure['cumulative_conservative_seconds'] == 4200
    assert all(value == 0 for value in audit_closure['real_operations'].values())
    for name, raw in originals.items():
        put(OUT + 'before/' + Path(name).name, raw)
    dump(OUT + 'closure-check.json', {
        'checked_at': stamp, 'identity_reference_checks': len(checks), 'mismatches': 0, 'checks': checks,
        'audit_historical_suffix_preserved': True, 'engineer_historical_suffix_preserved': True,
        'new_product_runtime': 0, 'new_test_runs': 0,
        'scope': '主控核当前原件和独审证据，未替代独审、未补做PG/安装动态验证',
    })
    adoption = put(OUT + 'approval-proposal.md', PROPOSAL)
    scope = dump(OUT + 'proposed-scope.json', {
        'proposal_id': 'AP-125-NORMAL-INSTALL-01', 'created_at': stamp, 'adopted': False, 'executable': False,
        'proposal_sha256': sha(adoption.read_bytes()), 'next_task_assigned': False,
        'scope': '关闭外发的首次真实安装与六项验证',
        'container_slots': [
            {'slot': 'source', 'name': 'retrolume-q-first-normal', 'volume': 'retrolume-q-first-normal-data',
             'database': 'retrolume_q_first_normal', 'compose_project': 'retrolume-first-install-source',
             'pg_port_candidates': [55482, 55484, 55486], 'cid': None, 'system_identifier': None, 'database_oid': None},
            {'slot': 'interrupted', 'name': 'retrolume-install-interrupted', 'volume': 'retrolume-install-interrupted-data',
             'database': 'retrolume_install_interrupted', 'compose_project': 'retrolume-first-install-interrupted',
             'pg_port_candidates': [55483, 55485, 55487], 'cid': None, 'system_identifier': None, 'database_oid': None},
        ],
        'image': 'pgvector/pgvector@sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f',
        'api_port_candidates': [18122, 18124, 18126],
        'new_private_roots': ['.runtime/normal-first-install/source', '.runtime/normal-first-install/interrupted'],
        'container_cap': 2, 'volume_cap': 2, 'compose_network_cap': 2, 'max_active_pg': 1,
        'per_pg_limits': {'cpus': 1, 'memory_mib': 512, 'pids': 128, 'restart': 'no', 'host_bind': False},
        'startup_available_memory_mib': 512, 'pressure_floor_mib': 256, 'pressure_samples': 2,
        'requested_tool_wall_cap_seconds': 10800, 'requested_reserved_close_seconds': 900,
        'requested_calendar_hours': 24, 'requested_pg_holding_seconds': 1800, 'requested_api_holding_seconds': 900,
        'requested_combined_attempts': 3, 'requested_pg_source_starts': 4,
        'requested_pg_interrupted_starts': 2, 'requested_api_starts': 3,
        'real_provider': 0, 'fees_cny': 0, 'Q': 'FROZEN', 'T0': None,
        'user_database_or_existing_resources': False,
        'cleanup': '仅明确自有进程/容器停止；卷及成功/失败数据保留，无prune/down-v/DROP DATABASE',
    })
    decision125 = f'''# TASK125有限安装工具工程验收通过并关闭

{stamp}，Asia/Shanghai。主控已核{len(checks)}条当前身份引用无漂移，回收TASK126 review-01，接受F126-01 P1和F126-02 P2在当前冻结版本的独立关闭结论。TASK125/R119约定的首次安装工具、固定原SQL清单、关闭示例/说明及离线验证交付通过并结束；不是首次真实安装、PG/ACL/正常启动或Q验收。

当前安装器29403字节/hash68d7b71fc7296111e894df4cba21a4ed7830f9cff069c1fc500dfbd7734c0a09，测试32786/93dabd4887760641884fc7ca5d5c83e520522563ea2d44be4dc2e72db320c3b7，说明10845/fb553199dafb11be8608a3608ff2f18778f07acbff265badb2994855c0fd6ddb。接受hostaddr固定、先拒绝原路径reparse再严格物理父/root归一及归一失败关闭，无新增直接阻断。原6旧/3新共9方法原始证据和12方法按实际影响继承，不重跑9/18、不宣称21全跑。原角色/SQL/启动/配置未变结论继承。

执行控制保持部分可核、完整精确unknown；工程原3600加本轮600=保守4200/10800、3/4批和所有旧失败/缺失原件/只读枚举范围偏差保留，不升级为精确控制全通过。未用工具与batch04封存不恢复许可。受信父目录的并发替换条件风险、server_major类型观察留作非阻塞适用限制，未要求新平台或对手试验。

原126报告现在50085字节/hash{current_report['sha256']}，原33379字节失败报告完整后缀保留；工程报告26676/hash{engineer_closure['result']['sha256']}及其15686原文后缀也不变。主控仅核原件与独审适用性，没有运行产品/测试/服务，不将静态缺陷关闭冒充真实行为证明。

本处不再派重复修复/独审。下一步六项真实安装/角色/启动/中断/verify可合并成一个关闭外发的本地验证单元，但新持久容器/卷及实际DDL/角色写未在125/126授权内。已准备AP-125-NORMAL-INSTALL-01具体采用包，待用户一次决定，当前不可执行、没有新TASK/R或资源。外部计量/账号/模板/Embedding容量门不阻塞该包的准备，也不因未来安装通过自行关闭。

Q冻结，T0/72h空、provider/费用0；STEP018整体、019/020/M1/项目仍未验。下方为原主控裁定原字节，保留当时失败和待审结论。

'''
    put(d125, decision125.encode('utf-8') + originals[d125])
    decision126 = f'''# TASK126 review-01通过并结束，两项发现由主控关闭

{stamp}，Asia/Shanghai。主控接受原独立窗口review-01交付和两项关闭依据，F126-01/F126-02关闭，当前首次安装前代码门通过；原首轮不通过和控制部分unknown保持其历史真实范围。审计交付已通过并结束，原工程/审计未用预算不自动恢复。

核{len(checks)}条当前原件引用无漂移，当前50输入扣除有意追加的报告后其余49项保持，原30依赖hash/实际batch03/原报告后缀链均相符。接受真实共享连接地址固定、Windows严格归一和9方法/12继承的限定证据；不是实际PG、网络认证、ACL、正常安装或启用。

本轮审计保守600加原1800=2400/3600，完整精确unknown；零产品/测试/PG等动态操作声明按原源码和日志的可核范围采纳，不把零字段本身作全平台证明。首轮最小六步真实清单直接沿用，只绑定修后版本，无新验证设计或新审计补项。

主控已关闭125有限工程，真实资源/DDL/角色操作另有采用包待决。本次不签运行或Q，STEP和项目门保持。下方保留原裁定原字节。

'''
    put(d126, decision126.encode('utf-8') + originals[d126])
    stop125 = f'''# TASK125有限工程已验收关闭 本卡运行许可结束

{stamp}。F126-01/F126-02经原126独立增量确认并由主控关闭。安装工具/关闭配置/离线证据交付通过，本卡已结束，不得使用未用工具或batch04继续。真实PG安装、正常资源或付费Q不在本卡。后续具体采用包尚待用户决定，以下完整合同仅保留历史，不恢复执行权。

'''
    stop126 = f'''# TASK126 review-01已回收验收结束 本卡只读许可封存

{stamp}。两项发现及当前代码门由主控接受关闭，原审计/增量交付结束。未用工具和原时间窗不自动恢复，原历史控制unknown与首轮报告不改。没有新独审或真实运行任务，以下完整合同保留历史。

'''
    put(t125, stop125.encode('utf-8') + originals[t125])
    put(t126, stop126.encode('utf-8') + originals[t126])
    state = f'''# 执行动态文档

文档v2.97，2026-10-22，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.69、task_model/07。以下v2.96原字节保留。

## 125有限工程关闭、126增量验收结束；关闭式真实安装采用包待决定

{stamp}。用户带回126 review-01，主控核{len(checks)}条身份引用零漂移，接受F126-01 P1/F126-02 P2关闭和当前代码门通过。125/R119约定的正式首次安装工具、清单/关闭示例说明及离线证据交付通过并结束；126/R120首轮与增量审计交付验收结束。代码门不再阻断，本处不派重复修复或审查。原首轮不通过/历史控制unknown和失败原件照留。

当前报告126为50085字节/hash{current_report['sha256']}，原33379字节后缀完整；125报告26676/hash{engineer_closure['result']['sha256']}与原15686后缀保留。三修后文件/受测六项及原30依赖保持。原18与batch03九方法证据按实际影响继承，不称21全跑，主控未重跑任何产品或测试。工程保守4200/10800/3批及审计2400/3600、完整精确unknown和未用额度全部封存，不恢复旧卡许可。

当前无在途或待转交工程/审计卡，未占TASK127/R121。下一必要单元为原独审六步真实安装验证，可先关闭外发完成，不必重复计量研究。新建持久容器/卷及实际权限/DDL超出125/126零运行范围，主控已把AP-125-NORMAL-INSTALL-01准备到具体对象/上限/反例/失败收尾，保存于TASK125/orchestration-closure-20261022/approval-proposal.md和proposed-scope.json，状态待用户采用、不可执行，尚未创建normal或签新运行许可。

提案只请求两个精确本机PG/独立卷/有限Compose网络、一个原生API串行、完整001—015/新角色、关闭配置启动/同库重开/停止、一次提交未知和成功verify。原旧库/用户数据不碰，真实provider/费用/索引/活动/Grant/预览/浏览器全0；低内存512MiB串行门作为本次待采用项明示，不擅用一般2GiB或旧特许。批准后才登记正式任务并给原125工程窗，普通中间步骤不再拆卡。

Q继续冻结、T0/72h空，账号/token/模板/Embedding容量/真实normal绑定和首次启用仍待后续。100/25及分额/28Must/89动作不变。STEP018进行中/部分验证，019/020/M1/项目/发布未放行。主控本轮只核文件，未实时探测Docker/端口/内存或启动资源。CHG1651—1658，下一1659。

## 以下为v2.96及更早历史

'''
    put(state_rel, state.encode('utf-8') + originals[state_rel])
    arch = f'''# 架构动态文档

文档v1.69，2026-10-22，Asia/Shanghai。需求v1.4、执行动态v2.97、task_model/07。以下v1.68原字节保留。

## 正常首次安装工具有限工程验收，实际安装仍待新权限与证据

{stamp}。原126独立增量关闭连接hostaddr和NTFS短别名两发现，主控接受代码门/离线证据并关闭125有限安装工具工程。原001—015、职责组和能力核验、控制行R01/R02/R03顺序及提交未知不重放等未变结论继承，原18和新9按适用方法复用，不表示真实PG/ACL/认证/正常启动已成功。

后续原六步动态检查准备为一个关闭外发验证采用包，拟新建主正常源与中断槽位、独立卷和现Compose PG服务，数据/权限仅新空状态。该包未获采用，所有对象身份尚未创建，不是架构已部署事实；Q/真实账号与计量前置不变，原预算/失败/控制unknown留档。未新增业务模型、接口、收费协议或平台。

## 以下为v1.68及更早历史

'''
    put(arch_rel, arch.encode('utf-8') + originals[arch_rel])
    changes = [
        (1651, d125, '接受两发现独立关闭，125有限工程验收通过并结束，动态安装及控制unknown不扩大。'),
        (1652, d126, '接受review-01及当前代码门，原失败历史保持，审计结束/剩余许可封存。'),
        (1653, t125, '置顶工程验收结束通知，旧完整合同原字节保留，不恢复batch04或真实安装权。'),
        (1654, t126, '置顶独审回收结束通知，旧合同与原报告保持，不签新运行。'),
        (1655, arch_rel, 'v1.69登记有限安装工程已验和真实安装未验证，关闭式采用包只作待决。'),
        (1656, state_rel, 'v2.97登记两任务收口/无在途卡和下一单元采用前置，旧投入与Q门保持。'),
        (1657, OUT + 'approval-proposal.md', '保存一次可审阅的精确关闭式真实安装采用包，含两持久槽位/原六步/预算和停止，未授权执行。'),
        (1658, OUT, '保存当前身份/原报告后缀核证、旧共享、采用草案JSON和工程关闭回执，主控产品运行0。'),
    ]
    addition = '\n\n' + '\n\n'.join(f'- CHG-{number}，{stamp}，Codex编排Agent，{name}。{description}' for number, name, description in changes) + '\n'
    put(changes_rel, originals[changes_rel] + addition.encode('utf-8'))
    for name, old in originals.items():
        if name == changes_rel:
            assert read(name).startswith(old)
        else:
            assert read(name).endswith(old)
    assert sha(read(report_rel)) == current_report['sha256']
    assert sha(read('DocuN/results/TASK-125-result.md')) == engineer_closure['result']['sha256']
    assert not p('DocuN/tasks/TASK-127.md').exists()
    receipt = {
        'checked_at': stamp, 'TASK125': 'PASS_ENGINEERING_SCOPE_AND_CLOSED',
        'TASK126': 'AUDIT_DELIVERY_ACCEPTED_AND_CLOSED',
        'findings': {'F126-01': 'CLOSED', 'F126-02': 'CLOSED'},
        'code_gate': 'PASS_SCOPE_ONLY', 'evidence_axis': '有限离线证据通过', 'control_axis': '部分可核，完整精确unknown照留',
        'identity_reference_checks': len(checks), 'mismatches': 0,
        'new_product_runtime': 0, 'new_test_runs': 0,
        'normal_install_dynamic_verified': False, 'Q': 'FROZEN', 'T0': None,
        'next_proposal': 'AP-125-NORMAL-INSTALL-01', 'next_proposal_adopted': False,
        'next_proposal_sha256': sha(adoption.read_bytes()), 'scope_sha256': sha(scope.read_bytes()),
        'next_task_assigned': False, 'shared_state_version': '2.97', 'architecture_version': '1.69', 'next_CHG': 1659,
    }
    dump(OUT + 'closure-receipt.json', receipt)
    proof = dict(receipt, verified_at=datetime.now(TZ).isoformat(),
        original_reports_and_shared_history_preserved=True,
        closure_check_sha256=sha(read(OUT + 'closure-check.json')),
        closure_receipt_sha256=sha(read(OUT + 'closure-receipt.json')))
    dump(OUT + 'save-proof.json', proof)
    print(json.dumps({key: receipt[key] for key in ('TASK125', 'TASK126', 'identity_reference_checks', 'mismatches',
        'new_product_runtime', 'next_proposal_adopted', 'next_task_assigned', 'next_CHG', 'Q')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
