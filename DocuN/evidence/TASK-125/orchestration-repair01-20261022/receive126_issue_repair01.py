"""主控核原始审计身份并维护修复合同；不运行产品或测试。"""
from pathlib import Path
from datetime import datetime, timedelta, timezone
import hashlib
import json
import re

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent').resolve()
OUT = 'DocuN/evidence/TASK-125/orchestration-repair01-20261022/'
AUDIT_RETURN = 'DocuN/evidence/TASK-126/orchestration-return-20261022/'
TZ = timezone(timedelta(hours=8))


def p(relative):
    target = (ROOT / relative).resolve()
    target.relative_to(ROOT)
    return target


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(relative):
    return p(relative).read_bytes()


def load(relative):
    return json.loads(read(relative).decode('utf-8-sig'))


def put(relative, content):
    dest = p(relative)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(content.encode('utf-8') if isinstance(content, str) else content)
    return dest


def dump(relative, value):
    return put(relative, json.dumps(value, ensure_ascii=False, indent=2) + '\n')


REPAIR = r'''# TASK-125 / R-119 审计修复01 当前有效完整合同

## 目标与交付

你担任原TASK125工程执行者，继续原窗口，一次合并修正F126-01 P1及F126-02 P2，完成必要定向离线验证与普通修复，保存完整候选供原TASK126增量复核。不是重新实现安装器，不执行真实PG或安装器apply，不重做18方法全量验证和旧业务审计。

本轮仍属TASK125/R119、STEP-018首次正常部署安装工具工程，关联STEP-020及原TASK126/R120。原候选尚未验收，沿同一卡和结果，不占新TASK/R；原全合同保留在本卡后半部，本置顶修复合同在本轮范围/许可上优先。原结果、两批、post副本、失败和审计报告不得覆盖。

产物仅为修正后的deploy/initialize_normal.py、backend/tests/test_normal_install.py，必要时更新deploy/normal-install.md中的相关准确说明；新证据保存到D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/repair-01/。统一结果仍为D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-125-result.md，按修复01置顶追加，原15686字节正文完整保留。

完成标准是两条已确定缺陷触发路径消除、新离线证据绑定实际最终字节、直接影响回归通过、无原迁移/角色/业务/Q边界变化。只交修复候选，不自签独审、首次安装门或项目通过。

## 根、规则、接收与真实状态

根目录D:/shspic/project_NO3_RetroLume-agent，入口同根AGENTS.md。模式task_model，V4.0，公共AGENTS CHG-0003。公共根D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，按项目DocuN/evidence/v4-migration-20260930/rules-snapshot.json锁定，不自动采用后来版本。同窗规则hash不变复用，只补读缺失与本次变更。

需求v1.4，发本轮后架构v1.67、执行动态v2.95。读取公共AGENTS及WORK的task_model、结果/接续/状态相关条款。接收A+，继续刚完成TASK125的原工程窗口，不使用126独审窗口自修。本轮不因具体模型标签换窗或重审；真实客户端/模型如实登记。若原窗不可用，交同等胜任工程窗口接续本轮，仍同TASK/R且只能一个写入者。

授权是已批准开发范围内的原合同缺陷修复，不增加新能力、依赖、资源或费用。当前修复待人工转交，主控没有代做产品或工具派发。TASK126审计已返回并结束；该审计交付通过，代码门不通过，证据轴限定通过，执行控制部分可核/完整精确unknown；不是由审计者自行签最终验收。原125验收失败待修，不是已经放行。

## 最小输入与已证根因

依次读取以下内容，已有同窗不变材料复用。

1. 根入口、本完整修复合同、DocuS/执行动态文档.MD置顶和本轮input-manifest.json、permit.json，确认新许可与保护边界。主控文件在DocuN/evidence/TASK-125/orchestration-repair01-20261022，只读不可写。
2. DocuN/results/TASK-126-result.md的F126-01/F126-02及证据/执行控制分级，和DocuN/evidence/TASK-126/audit/static-analysis-02.json中ntfs_aliases与junction元数据、closure.json中的当前身份。没有必要重读审计完整背景、旧全仓或原聊天。
3. 当前deploy/initialize_normal.py的safe_path/new_output/connect/plan/apply/verify及直接调用，现有test_normal_install.py相关方法。原六文件和15SQLhash见本轮manifest，改动前保存本轮pre。
4. 当前安装的psycopg 3.3.5中connection.py、_connection_base.py、_conninfo_utils.py和_conninfo_attempts.py的直接相关片段，仅读源码；它们的hash已被原审计记录。不要改驱动、升级依赖或借此联网查新API。
5. 原batch-02-command/summary/output、tested-before-batch-02、post-snapshot，以及原run-offline-batch-02.py/harness的环境隔离方式。原18方法有效证据直接继承，只补实际影响和新缺口。原runner/harness和日志不得原地重跑或覆盖，复制必要测试启动方式到repair-01后只产生本轮新日志。

F126-01是确定P1，非已发生泄露。当前connect仅给host=127.0.0.1而未给hostaddr；当前驱动对未显式项使用PGHOSTADDR，非loopback环境可在数据库身份预检前改变管理员认证的实际网络目的地。预检后的system_identifier/OID/身份核对不能撤回认证。原18方法没有覆盖这个参数路径。

F126-02是确定P2，非覆盖或数据破坏。safe_path已逐级拒绝reparse，但new_output只将原拼写与ROOT下受保护目录做字面包含检查。本机原审计只读GetShortPathNameW/GetLongPathNameW已证D:/shspic/PROJEC~3是当前项目根的实际8.3别名；通过其backend/deploy/config拼写可绕过保护，排他新建仍阻止覆盖已有文件。原审计没有创建假设输出或运行安装器。

原中间版批1正文未另存完整副本、平台junction审批原回执缺失、精确总wall未知均保持事实；不为收口补造原件或把unknown判为已违规/已核合规。原审计指出server_major对17.0的非阻塞类型观察及受信父目录下的TOCTOU条件风险，不自动扩成本轮硬门槛或另一个平台重构。

## 唯一合并修正

### F126-01 固定真正连接目的地

connect在传给psycopg的参数里同时显式固定host和hostaddr为已经由原配置校验允许的127.0.0.1；保留精确port/dbname/安装登录及真实DB身份检查。apply与verify共享connect，须共同受保护。

不修改全局os.environ作为产品纠偏，不读取/回显原PGHOSTADDR，不移除身份检查，不把PG服务端地址强制为127.0.0.1或映射端口。原合法容器NAT的服务端172.18.0.2:5432与客户端127.0.0.1:55464等语义保持。不通过真实外连或另建PG证明此修复。

增加零网络驱动参数记录测试，使用本轮进程内的合成非loopback PGHOSTADDR、PGHOST及必要合成安装凭据，并在任何连接前替换/阻断驱动入口。观察实际connect提交的kwargs，hostaddr/host必须固定loopback，port及其余已限定参数正确，不能由环境覆盖。覆盖apply/verify共享路径的可观察关系，至少直接测试真实产品connect；不是只assert源码里出现hostaddr字符串。不要读取当前真实PG环境再脱敏，也不把调用记录器冒称实际TCP或认证已验证。

### F126-02 按物理目录身份保护输出

保留对用户原拼写逐级lstat拒绝reparse/junction、UNC、ADS、设备/尾点等逻辑；在此检查之后，将现存父目录及受保护根归一到可核的实际长路径或文件对象身份，再判包含关系，并保留末级排他新建。不可先resolve隐藏junction后再假称原路径安全；归一失败要失败关闭，不能回退未保护的字面比较。

修正同时覆盖plan输出、apply收据及Journal共用new_output路径，不改变verify仅读完整既有收据的合同。保持产品外正常受信输出可用和已有文件不能覆盖，不新加通用路径授权平台。实现细节可自主选择现有标准库/本机Win32只读文件元数据API，不能引入依赖或改系统/卷8.3设置。

使用原审计已证明存在的真实短别名，按当前元数据确认仍指同一目录后，测试backend/deploy/config等原受保护目录拒绝。不得用假的lstat/伪造字符串等价替代唯一短路径证据。可用共享new_output加实际plan/收据入口的阻断写入探针，保证即便回归也不在受保护产品目录落盘；不为演示漏洞真的创建新产品文件。

继续验证正常允许输出、已有输出冲突和原真实junction拒绝。不要重建原夹具：原execution/scratch/junction-fixture/link指向同目录target，允许只读复用与元数据核对。本轮测试临时case可在原execution/scratch下创建新的随机子目录，以兼容现有test08的范围断言；必须登记新增目录，不写/删任何旧case、link或target，不递归遍历或清理scratch。如夹具意外漂移，停止其用例并报告具体身份，不重做已失败的DeviceIoControl路径。

## 文件与资源边界

只允许改deploy/initialize_normal.py、backend/tests/test_normal_install.py及相关准确说明所必需的deploy/normal-install.md。所有路径以项目根为准。允许在execution/repair-01写本轮pre/diff/post、子进程启动器/纯离线harness/测试数据和命令/账；上述原scratch仅允许新增本轮随机case目录和只读复用旧junction。

保持README、normal_install_manifest.json、normal-install.example.json、001—015及其原hash、backend/app、原runtime/loader/roles/profile/业务/账本/Grant/worker、前端/dist、依赖/锁、真实local/private配置和原运行入口不变。不改DocuS、公共库、主控文件、审计原件或旧125证据。不创建新TASK/全局DEF编号，不自行写外部经验库。

本卡仍无真实PG连接/查询/DDL/DCL、Docker/Compose/容器/数据库/卷/角色创建、应用/HTTP服务/端口/浏览器/Job/预览、provider/Embedding/计量服务/网络/安装依赖/Git写入或真实费用权限。不要运行安装器CLI apply或读取.runtime/用户库/凭据。离线参数记录器调用内部函数仅观察本地边界，不等于实际安装。

两个供应商、100次25元固定分额、28Must/89动作/24片6索引不变，Q继续冻结、T0为空。计量/账号外部缺口不因本轮修复关闭，也不要求本轮重复搜索或提问。

## 验证、复用和预算

修改前对三允许文件存pre副本及hash，原四个不可变产品和所有SQL/原证据作为冻结对象。以本轮pre生成准确diff，不把原Git差异并入。结果置顶保留原报告完整后缀，原post/两批及原审计内容一字不改。

完成两项修正后集中运行新增hostaddr/实际短别名测试，以及实际直接受影响的原方法。通常包括test07输出/冲突、test08真实junction、test11/12/13的收据/关闭/重复行为和test17错误边界；名单按真实diff确认并在运行前固定，若需要增加说明具体影响。原迁移清单/纯角色/未变配置方法按最终字节和不受影响依据继承，不机械全跑18方法，不宣称所有18在新字节上重新运行。

使用现有backend/.venv/Scripts/python.exe，-I -S -B和显式现有依赖目录的白名单环境方式可复用原批2。新日志/harness/summary必须在repair-01，不覆盖原batch文件；冻结本批harness、测试文件、安装器和实际说明字节，测后相符才绑定。socket/PG/进程/运行时构造的观察阻断保持，不能仅据硬编码零字段冒称全平台证据。测试不继承真实provider key、DSN、旧PYTHONPATH或sitecustomize，只传必要系统名及本轮合成PGHOSTADDR等占位。

原工程工具精确总wall仍unknown，保守已列3600/10800；原2/3批以及所有失败保持。本轮主控明确从原封存剩余7200秒中恢复最多2400秒工具投入，含360秒保存/收尾，原10800总cap不变。累计保守记账须为原3600加本轮真实或如实保守投入，不从0重建。不得把回传等待当工具实测，缺调用记录写unknown及有据包络。

原24h截止2026-10-23T09:12:14.276888+08:00保持，不重置日历。本轮至多两批集中离线验证，第一批为累计batch03，若有明确修正依据可一次batch04；原总批上限由3前向调整为4，仅增加一批以覆盖新增审计路径及必要修正，原已用2批不删。每批至多600秒，不按方法拆根额度，不为用尽预算多跑。全部通过即停止；同一问题两次有据修正仍失败或工具/日历先到门时停依赖部分，不自行开batch05。

范围内普通修复连续完成，不逐行向用户请批。必须改变原SQL/主要角色或公开业务/安全模型、新真实资源、安装器真实运行、范围扩大、根因不稳或额度到门时，完成不受阻部分后带最小具体差异回主控，不增加服务或对手模型来追理论完美。

## 独审关系与回传

本轮是工程普通修复，不能自签两项缺陷关闭。稳定后由原TASK126独立窗口只确认F126-01/F126-02修正、最终hash及直接影响/新原始证据，其余已接受结论继承。原独审已结束，其剩余预算不自动恢复；主控在收到修复候选后再签增量复核合同，不现在让两窗口并行写/审同一变化对象。

修复结果包括两项原触发和对应最小变化、字段/CLI兼容、pre/post/diff及未变文件保护、实际所选测试方法/子场景、日志/退出/时长/受测身份、未运行项、旧失败/unknown和累计账、待主控同步项。真实PG/认证/路径对手竞态/正常启动尚未运行，不能扩大离线结论。

不需要用户提供key、开服务、释放内存、删除文件或重新批准已有开发。完成后保存并复读原结果D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-125-result.md，回复一句话结论和可点击完整绝对路径即可。最终验收由主控裁定，Q及STEP018/019/020、M1/项目不放行。

## 以下为原TASK125完整合同 原字节保留

'''


def main():
    current = datetime.now(TZ)
    timestamp = current.isoformat()
    state_rel = 'DocuS/执行动态文档.MD'
    arch_rel = 'DocuS/架构动态文档.MD'
    changes_rel = 'DocuS/文档变更记录.MD'
    task_rel = 'DocuN/tasks/TASK-125.md'
    old_decision_rel = 'DocuN/results/TASK-125-work-decision.md'
    original_paths = (state_rel, arch_rel, changes_rel, task_rel, old_decision_rel)
    before = {name: read(name) for name in original_paths}
    assert '文档v2.94' in before[state_rel].decode('utf-8-sig')[:100]
    assert '文档v1.66' in before[arch_rel].decode('utf-8-sig')[:100]
    assert max(map(int, re.findall(r'CHG-(\d+)', before[changes_rel].decode('utf-8-sig')))) == 1638
    assert sha(before[task_rel]) == '10a1ce45367f50045faca8393d67fe32aacfc5df1653b97e2fa377c4b0e3e0a5'
    assert not p('DocuN/results/TASK-126-work-decision.md').exists()
    assert not p('DocuN/tasks/TASK-127.md').exists()
    old_permit = load('DocuN/evidence/TASK-125/orchestration-20261022/permit.json')
    assert current < datetime.fromisoformat(old_permit['deadline'])
    assert '*' not in REPAIR and '〈' not in REPAIR and '| ---' not in REPAIR
    closure = load('DocuN/evidence/TASK-126/audit/closure.json')
    audit_inputs = load('DocuN/evidence/TASK-126/orchestration-20261022/input-manifest.json')
    checks = []

    def verify(source, expected, group, byte_count=None, relative=None):
        source = Path(source)
        raw = source.read_bytes()
        actual = sha(raw)
        assert actual == expected, (str(source), actual, expected)
        assert byte_count is None or len(raw) == byte_count, str(source)
        checks.append({'path': relative or str(source), 'absolute_path': str(source), 'group': group,
                       'bytes': len(raw), 'sha256': actual, 'match': True})

    for row in audit_inputs['sources']:
        verify(row['absolute_path'], row['sha256'], 'audit_frozen_inputs', row['bytes'], row['path'])
    for row in closure['additional_dependencies']:
        verify(row['path'], row['sha256'], 'audit_additional_dependency', row['bytes'])
    report_rel = 'DocuN/results/TASK-126-result.md'
    verify(p(report_rel), closure['report']['sha256'], 'audit_report', closure['report']['bytes'], report_rel)
    for row in closure['audit_artifacts_before_closure']:
        relative = 'DocuN/evidence/TASK-126/audit/' + row['name']
        verify(p(relative), row['sha256'], 'audit_raw_artifact', row['bytes'], relative)
    reception = load('DocuN/evidence/TASK-126/audit/reception-identity.json')
    for row in reception['bindings']:
        verify(p(row['path']), row['sha256'], 'audit_contract_binding', relative=row['path'])
    assert closure['budget']['conservative_charge_seconds'] == 1800
    assert closure['budget']['exact_total_tool_wall_seconds'] is None
    assert all(value == 0 for value in closure['real_operations'].values())
    original_engineer_report = read('DocuN/results/TASK-125-result.md')
    assert sha(original_engineer_report) == '78a80de9633ad13b703262850782ddbcbef3d4ef50632b255e319147a3715404'
    supplement = load('DocuN/evidence/TASK-126/audit/static-analysis-02.json')
    assert any(row['short_name_available'] and row['long_path'].replace('\\', '/') == str(ROOT).replace('\\', '/')
               for row in supplement['ntfs_aliases'])
    for relative, raw in before.items():
        put(OUT + 'before/' + Path(relative).name, raw)
    dump(AUDIT_RETURN + 'return-check.json', {
        'TASK': 'TASK-126', 'R': 'R-120', 'checked_at': timestamp,
        'identity_reference_checks': len(checks), 'mismatches': 0, 'checks': checks,
        'product_runtime': 0, 'product_tests_rerun': False,
        'root_cause_review': {
            'F126-01': '原connect未显式hostaddr，与已安装驱动get_param/resolve_hostaddr的环境回退事实相符',
            'F126-02': '原new_output字面包含判断，与原审计只读实际8.3长短路径元数据相符；未创建漏洞输出',
        },
        'main_scope': '有限原件/代码定位核证，非重新独立审计',
    })
    audit_decision = f'''# TASK126/R120独审交付通过，TASK125首次安装门不通过

{timestamp}，Asia/Shanghai。主控已回收实际审计报告及原件，核{len(checks)}条身份引用零漂移，包括71冻结输入、7额外直接依赖、报告/6原件及许可绑定。审计交付验收通过并结束；采纳代码轴不通过、证据轴原离线范围通过、控制轴部分可核/完整精确unknown，不把报告交付通过写成安装门或控制全通过。

采纳F126-01 P1。现connect缺hostaddr，当前psycopg3.3.5源码对未显式项回退PGHOSTADDR，管理员认证可能先于身份查询到错误地址。没有真实外连或泄露证据，不夸大为已发生事故。原apply/verify共享连接需显式固定loopback hostaddr，保留身份及合法NAT语义。

采纳F126-02 P2。new_output仅字面比较受保护目录，原审计已取本机实际8.3长短路径元数据，别名可绕过新输出位置保护；排他新建仍挡覆盖，未发生写入或数据破坏。修复在拒绝原路径链接后核实际父目录长路径/身份，保留正常输出和排他创建。

原18方法证据与六文件最终身份、无改原SQL/角色/业务的有效结论保持，记录器/硬编码零及首批中间版未归档、平台原回执缺失等限制照留。精确总工具wall unknown，1800/3600只为保守列支，原失败/分析器局限和格式/元数据退出原文不改，不追加新运行。

唯一修复线沿原TASK125/R119、原A+工程窗口，两个发现合并在一次离线修复01。只改安装器/测试/必要说明，稳定后回原126增量核两项和实际直接影响，不重审全套。126本轮已结束，余量不自动恢复；修复候选返回后主控才另签增量复核许可。

Q保持冻结，真实apply/PG/运行/账号前置未获新增许可，STEP018/019/020及项目不放行。原审计报告SHA256 {closure['report']['sha256']}，{closure['report']['bytes']}字节，原文保留。主控本轮无产品运行或测试。
'''
    put('DocuN/results/TASK-126-work-decision.md', audit_decision)
    engineer_decision = f'''# TASK125首次安装候选验收失败，F126-01/F126-02沿原窗修复01

{timestamp}，Asia/Shanghai。TASK126独审交付已由主控接受，125候选代码门失败。F126-01 P1为缺显式hostaddr导致环境可影响认证目的地；F126-02 P2为实际NTFS短别名绕过输出位置保护。两项均有被冻结源码/当前驱动和原始文件名元数据依据；尚未发生错误连接或漏洞输出，原18方法证据按原范围有效，不推翻未变业务。

同号完整修复01合同已保存，待人工转交原A+工程窗口；尚未接收/启动。只改initialize_normal.py、test_normal_install.py及必要normal-install.md，新证据进execution/repair-01，原报告/两批/post/审计原文保留。

从原封存7200余量明确恢复最多2400秒工具含360保存，原保守3600/10800不重置，总cap及原截止2026-10-23T09:12:14.276888+08:00保持。原已用2批，本轮最多batch03/04，累计批上限前向3改4，原失败不删，无真实资源额度。两项普通修正后只验直接影响和新增路径，旧充分方法按范围继承。

修复完成仍为候选，待原126限定增量确认，不由工程自签关闭。不新增模型/API/SQL/角色/真实资源或费用。Q冻结/外部依据及原阶段门不变。下方为原主控裁定原字节，保留当时待审状态。

'''
    put(old_decision_rel, engineer_decision.encode('utf-8') + before[old_decision_rel])
    put(task_rel, REPAIR.encode('utf-8') + before[task_rel])
    assert read(task_rel).endswith(before[task_rel])
    assert read(task_rel)[:len(REPAIR.encode('utf-8'))].decode('utf-8') == REPAIR
    state_prefix = f'''# 执行动态文档

文档v2.95，2026-10-22，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.67、task_model/07。以下v2.94原字节保留。

## TASK126独审已回收，TASK125同号双缺陷修复01待人工转交

{timestamp}。用户回传126，主控核{len(checks)}条身份引用零漂移；审计交付通过并结束，125首次安装候选代码门不通过，证据轴既有离线范围通过，控制轴部分可核/精确总wall未知。报告33379字节/hash{closure['report']['sha256']}及原始失败/分析器修正/缺失原回执和中间版限制保留；主控无重新测试或独审。

采纳F126-01 P1：缺显式hostaddr，可被PGHOSTADDR在身份核验前影响认证目的地；F126-02 P2：实际8.3别名可绕过new_output字面目录保护。原源码/驱动片段及原审计真实文件名元数据支持，未发生真实错误连接、文件写入或数据破坏。现有原18方法不覆盖这两个触发路径，其余有效结论仍继承。

同TASK125/R119、原A+工程窗口唯一修复路线；完整修复01置顶DocuN/tasks/TASK-125.md，原合同原字节留后，状态待转交，未声明接收/开始。只准安装器、定向测试及必要安装说明，固定SQL/角色模型/业务/README/清单/示例不变。新产物execution/repair-01，原结果置顶保后缀和全部原证据。修复稳定后回原126只核双缺陷/最终hash/直接影响，不重复全审；126余量已封存不自动续审。

从125原封存7200秒中显式恢复本轮最多2400秒含360保存，原保守3600/10800/精确unknown及原24h截止不重置；原2批留账，本轮至多batch03及有据batch04，累计批上限由3前向4，单批600秒，无按子方法拆根额度。原149/117旧81、123/124账及126保守1800/3600/精确unknown原样保持。

全部真实PG/apply/Docker/角色/容器/卷/服务/浏览器/网络/provider/费用/Git额度0；Q冻结、T0/72h空，账号/token/模板/Embedding容量/真实normal绑定和启用门未新增。STEP018仍进行中/部分验证，019/020/M1/项目未验。不以本次离线修复重复搜索或预签真实运行。

回收裁定DocuN/results/TASK-126-work-decision.md、TASK-125-work-decision.md；身份原件在TASK126/orchestration-return-20261022，修复合同/许可在TASK125/orchestration-repair01-20261022。CHG1639—1644，下一1645。

## 以下为v2.94及更早历史

'''
    put(state_rel, state_prefix.encode('utf-8') + before[state_rel])
    arch_prefix = f'''# 架构动态文档

文档v1.67，2026-10-22，Asia/Shanghai。需求v1.4、执行动态v2.95、task_model/07。以下v1.66原字节保留。

## 首次安装候选双缺陷修复计划，真实安装门继续关闭

{timestamp}。TASK126独审发现连接实际目的地未显式hostaddr固定和Windows实际短别名绕输出目录保护。主控接受P1/P2，125候选不通过，双缺陷沿原工程同号修复01。计划只加强原有loopback连接和受保护目录约束，保留合法NAT、原路径reparse拒绝、排他新建及既有权限/迁移模型，不改SQL或业务协议。

原完整迁移顺序/角色分工等未见新确定问题和18方法限定证据继续适用，但不能据此放行当前代码。修正尚未实施，实际PG/ACL/认证/正常启动和外部Q仍未验证/启用。稳定后原独审限定增量复核，不重复未变整仓。旧unknown及历史控制限制保持。

## 以下为v1.66及更早历史

'''
    put(arch_rel, arch_prefix.encode('utf-8') + before[arch_rel])
    entries = [
        (1639, 'DocuN/results/TASK-126-work-decision.md', '接受独审交付/三轴结论，采纳F126-01 P1和F126-02 P2，首次安装门不通过，原审计及控制unknown保留。'),
        (1640, old_decision_rel, '置顶125候选验收失败和唯一同号修复路线，原待审裁定原字节保留。'),
        (1641, task_rel, '置顶完整修复01合同，合并双缺陷定向离线验证，从原余量明确恢复部分工具/前向批上限，不授真实资源。'),
        (1642, arch_rel, 'v1.67登记双缺陷与加强原连接/路径边界的计划，尚未修复，无业务/SQL/角色变更。'),
        (1643, state_rel, 'v2.95登记126已返回/审计交付结束、125失败/修复待转交及原账/剩余范围。'),
        (1644, 'DocuN/evidence/TASK-126/orchestration-return-20261022及TASK-125/orchestration-repair01-20261022', '保存有限原件/根因定位、旧共享和原卡、修复输入/许可/读回证明，主控产品运行0。'),
    ]
    addition = '\n\n' + '\n\n'.join(f'- CHG-{n}，{timestamp}，Codex编排Agent，{name}。{text}' for n, name, text in entries) + '\n'
    put(changes_rel, before[changes_rel] + addition.encode('utf-8'))
    allowed = ('deploy/initialize_normal.py', 'backend/tests/test_normal_install.py', 'deploy/normal-install.md')
    source_paths = [
        'AGENTS.md', state_rel, arch_rel, 'DocuS/最终需求文档.MD', task_rel,
        'DocuN/results/TASK-126-result.md', 'DocuN/evidence/TASK-126/audit/closure.json',
        'DocuN/evidence/TASK-126/audit/static-analysis-02.json',
        'deploy/initialize_normal.py', 'backend/tests/test_normal_install.py', 'deploy/normal-install.md',
        'deploy/normal_install_manifest.json', 'config/normal-install.example.json', 'README.md',
        'DocuN/evidence/TASK-125/execution/closing-receipt.json',
        'DocuN/evidence/TASK-125/execution/post-snapshot.json',
        'DocuN/evidence/TASK-125/execution/batch-02-command.json',
        'DocuN/evidence/TASK-125/execution/batch-02-output.txt',
        'DocuN/evidence/TASK-125/execution/batch-02-summary.json',
        'DocuN/evidence/TASK-125/execution/tested-before-batch-02.json',
        'DocuN/evidence/TASK-125/execution/run-offline-batch-02.py',
        'DocuN/evidence/TASK-125/execution/offline-harness-02.py',
        'DocuN/evidence/TASK-125/orchestration-20261022/permit.json',
        'DocuN/evidence/v4-migration-20260930/rules-snapshot.json',
    ]
    source_paths += [row['path'] for row in load('deploy/normal_install_manifest.json')['migrations']]
    rows = []
    for relative in source_paths:
        raw = read(relative)
        rows.append({'path': relative, 'absolute_path': str(p(relative)), 'bytes': len(raw),
                     'sha256': sha(raw), 'write_allowed': relative in allowed})
    for row in closure['additional_dependencies']:
        raw = Path(row['path']).read_bytes()
        rows.append({'path': row['path'], 'absolute_path': row['path'], 'bytes': len(raw), 'sha256': sha(raw), 'write_allowed': False})
    for row in load('DocuN/evidence/v4-migration-20260930/rules-snapshot.json'):
        raw = Path(row['absolute_path']).read_bytes()
        assert sha(raw) == row['sha256']
        rows.append({'path': row['relative_path'], 'absolute_path': row['absolute_path'], 'bytes': len(raw),
                     'sha256': sha(raw), 'write_allowed': False, 'public_readonly': True})
    manifest = dump(OUT + 'input-manifest.json', {
        'TASK': 'TASK-125', 'R': 'R-119', 'continuation': 'audit-repair-01', 'issued_at': timestamp,
        'sources': rows, 'source_count': len(rows), 'allowed_product_writes': list(allowed),
        'report_original': {'path': 'DocuN/results/TASK-125-result.md', 'bytes': len(original_engineer_report), 'sha256': sha(original_engineer_report)},
        'original_contract': {'path': OUT + 'before/TASK-125.md', 'sha256': sha(before[task_rel])},
        'known_real_junction': supplement['junction'],
        'original_ntfs_alias_observations': supplement['ntfs_aliases'],
        'source_of_aliases': '原126只读文件名元数据；本主控未重做或写入探针',
        'all_prior_raw_evidence_preserved': True,
    })
    permit = dump(OUT + 'permit.json', {
        'schema': 'retrolume.task-scope.v1', 'TASK': 'TASK-125', 'R': 'R-119',
        'continuation': 'audit-repair-01', 'issued_at': timestamp, 'deadline': old_permit['deadline'],
        'full_current_card_sha256': sha(read(task_rel)), 'effective_contract_prefix_sha256': sha(REPAIR.encode('utf-8')),
        'historical_contract_sha256': sha(before[task_rel]), 'input_manifest_sha256': sha(manifest.read_bytes()),
        'dispatch_status': '待人工转交', 'acceptance': '失败，待F126-01/F126-02修复及独审确认',
        'recipient': 'A+原TASK125工程窗口，不能由126独审窗口自修',
        'historical_tool_charge_seconds': 3600, 'historical_exact_tool_total': None,
        'historical_tool_cap_seconds': 10800, 'unsealed_tool_extra_cap_seconds': 2400,
        'reserved_close_seconds': 360, 'historical_test_batches_used': 2,
        'previous_test_batch_cap': 3, 'forward_test_batch_cap': 4, 'continuation_batch_cap': 2,
        'next_batch': 'batch03', 'per_batch_seconds': 600,
        'scope': '只修既有连接和路径约束；不是新安装/计量/部署运行许可',
        'real_caps': {name: 0 for name in ('pg', 'installer_cli_apply', 'docker', 'database', 'role_mutation',
            'container', 'volume', 'service', 'browser', 'job', 'preview', 'provider', 'embedding',
            'metering_api', 'network', 'dependency_install', 'git_write', 'fee_cny', 'delegation')},
        'Q': 'FROZEN', 'T0': None,
    })
    for row in rows:
        assert sha(Path(row['absolute_path']).read_bytes()) == row['sha256'], row['path']
    for relative in (state_rel, arch_rel, old_decision_rel, task_rel):
        assert read(relative).endswith(before[relative])
    assert read(changes_rel).startswith(before[changes_rel])
    assert sha(read('DocuN/results/TASK-125-result.md')) == sha(original_engineer_report)
    assert sha(read(report_rel)) == closure['report']['sha256']
    assert read(task_rel).startswith(REPAIR.encode('utf-8'))
    proof = {
        'TASK': 'TASK-125', 'R': 'R-119', 'continuation': 'audit-repair-01',
        'issued_at': timestamp, 'checked_at': datetime.now(TZ).isoformat(), 'status': '待人工转交',
        'audit_return_identity_checks': len(checks), 'source_identities': len(rows), 'mismatches': 0,
        'full_current_card_bytes': len(read(task_rel)), 'full_current_card_sha256': sha(read(task_rel)),
        'effective_contract_prefix_bytes': len(REPAIR.encode('utf-8')), 'permit_sha256': sha(permit.read_bytes()),
        'input_manifest_sha256': sha(manifest.read_bytes()), 'shared_state_version': '2.95',
        'architecture_version': '1.67', 'next_CHG': 1645, 'product_runtime': 0, 'new_test_runs': 0,
        'original_card_and_decision_bytes_preserved': True, 'original_reports_unchanged': True,
        'F126-01': 'OPEN P1', 'F126-02': 'OPEN P2', 'Q': 'FROZEN', 'T0': None,
    }
    dump(OUT + 'save-proof.json', proof)
    dump(AUDIT_RETURN + 'return-receipt.json', {
        'TASK': 'TASK-126', 'R': 'R-120', 'checked_at': timestamp, 'dispatch': '已返回',
        'audit_delivery_acceptance': '通过', 'TASK125_code_gate': '不通过',
        'evidence_axis': closure['evidence_axis'], 'execution_axis': closure['execution_axis'],
        'audit_report_sha256': closure['report']['sha256'], 'historical_budget_sealed': True,
        'fix_route': 'TASK125/R119审计修复01，待人工转交原工程窗口', 'new_product_runs': 0, 'Q': 'FROZEN',
    })
    print(json.dumps({k: proof[k] for k in ('TASK', 'R', 'continuation', 'status', 'audit_return_identity_checks',
        'source_identities', 'mismatches', 'full_current_card_bytes', 'effective_contract_prefix_bytes',
        'next_CHG', 'product_runtime', 'Q')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
