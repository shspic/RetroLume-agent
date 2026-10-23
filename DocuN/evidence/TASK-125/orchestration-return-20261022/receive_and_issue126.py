"""主控文件核证、回收和出卡；不运行产品、测试或服务。"""
from pathlib import Path
from datetime import datetime, timedelta, timezone
import difflib
import hashlib
import json
import re

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent').resolve()
RETURN = 'DocuN/evidence/TASK-125/orchestration-return-20261022/'
AUDIT = 'DocuN/evidence/TASK-126/orchestration-20261022/'
EXEC = 'DocuN/evidence/TASK-125/execution/'
TZ = timezone(timedelta(hours=8))


def p(relative):
    value = (ROOT / relative).resolve()
    value.relative_to(ROOT)
    return value


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(relative):
    return p(relative).read_bytes()


def load(relative):
    return json.loads(read(relative).decode('utf-8-sig'))


def put(relative, data):
    dest = p(relative)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data.encode('utf-8') if isinstance(data, str) else data)
    return dest


def dump(relative, value):
    return put(relative, json.dumps(value, ensure_ascii=False, indent=2) + '\n')


CARD = r'''# TASK-126 / R-120 正常首次安装工具链集中独立审查

## 目标与完整交付

你担任独立审计执行者，只读审查TASK125稳定的完整安装工具工程和原始离线证据。一次回答首次真实apply前的安装代码/角色权限门是否具备通过条件，给出确切缺陷或通过边界，以及后续最小真实安装验证清单。不是实现卡、运行卡或新的计量调研。

范围是六个最终文件及其直接依赖、相对pre的实际差异、两批原始日志/实际受测hash和执行控制事实。原TASK123/124的readiness、准确理由及13方法，原120/121未变业务/迁移/profile/权限结论按其适用范围继承，不重审全仓或重复原安全矩阵。

交付为D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-126-result.md，原始核证只写D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-126/audit/。报告分代码、证据、执行控制三轴，独立给出确定缺陷、条件风险、未知及适用范围。报告写完不等于主控最终验收。

## 项目、规则和接收安排

根目录D:/shspic/project_NO3_RetroLume-agent；入口同根AGENTS.md。模式task_model，阶段07，V4.0/公共AGENTS CHG-0003，锁定清单为DocuN/evidence/v4-migration-20260930/rules-snapshot.json。公共根D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4。

接收A+增强独立资源，优先继续原TASK124独审窗口，前提是没有参与125实现、普通修复或测试设计。原窗不满足真实隔离时改用新隔离审计窗口，不改变TASK126/R120编号，不要求为模型标签重审旧成果。实际客户端/模型如实登记；无法证实的后端变体写未知，不伪称身份。不能使用原TASK125工程窗口自审。

关联STEP-018、STEP-020的部署交接和未来STEP-019适用安全证据，父TASK125/R119，需求v1.4、架构v1.66、执行动态v2.94。原因是安装器将来执行固定迁移及创建角色，属于原TASK125已规定的首次真实apply前必需独审；稳定候选现已返回，不按每个文件分别审。

授权终点是当前冻结代码、已有证据与有限文件核证，运行和真实资源额度全0。本卡尚待人工转交，主控未通过工具派发；接收后登记实际时间及独立性。工程候选已返回并冻结，原窗口停止写入，不与本审计并行修改。

## 独立输入与读取顺序

1. 根入口、同版公共AGENTS，以及公共WORK第6节结果、第8节独立接续、第9节分轴结论。已读且指纹不变的规则复用。不得采用后来公共版本或读其它模式替换合同。
2. 本卡配套DocuN/evidence/TASK-126/orchestration-20261022/input-manifest.json、raw-evidence-index.json和permit.json。先独立核六文件及关键直接依赖身份，漂移只停止相应对象并报告具体path/hash，不能对旧快照签当前结论。
3. DocuN/tasks/TASK-125.md原始完整合同，包含正常首次空库、固定001—015、关闭配置、角色分工、非原子整包、提交未知不重试及本地离线边界。本卡不改变其目标或增加新的产品Must。
4. 六份最终文件全文、execution/changes.patch及pre/README.md；其余五文件原为不存在。先以原合同和源码形成独立判断，再查看测试和执行记录，不以工程自评替代判断。
5. backend/migrations/001—015，按清单逐项核原字节hash与当前schema_profiles；原SQL未改，不重审已验SQL全部逻辑。重点读安装依赖所需013控制行/R01、014/R02、015/R03与角色/guard，和backend/app/data_exit/schema_profiles.py、schema_checks.py、q_roles.py、files.py、config.py的直接相关职责。必要时只读现有schema.py/contracts.py等直接依赖。
6. 固定关闭模板config/activity.example.json、integration.example.json、q-approval.example.json、preview.example.json及data-exit.example.json，原deploy/start_local.py、initialize-materials.py、compose.local.yml。只核新工具与正常启动/原profile的接口相容和真实副作用边界，不另做预览镜像或Compose部署审计。
7. 原始18方法、harness/runner、两批command/output/summary、tested-before-batch-01/02、post/pre-snapshot及source-preservation。再读command-ledger、junction-diagnostic和correction-01中的实际操作/错误/修正/预算事实；作者推断只作待核事实，不当结论。

不读DocuN/results/TASK-125-result.md、实现聊天、完整思考、自评及主控对工程优劣的结论。可读取本卡列明的原始日志、差异和身份元数据。若偶然接触，披露内容、时点及对独立性的影响，不伪称从未接触。旧124窗口若已读同一已验源码，仅补真实新差异，不重复旧13方法或原业务审计。

## 当前冻结对象

以下是主控当前重算并与批2受测及post副本相符的对象身份，仅表示身份，不预设代码结论。

- deploy/initialize_normal.py，28872字节，e112ce498f73371e6d788ed834c4c0414f3c8728579ec1ddc9df6c4942ffce5d。
- deploy/normal_install_manifest.json，4325字节，f2ed126daa1c5a982b490a9343d6c17053c0f385e7a2f55676ecf4132dd2abf0。
- deploy/normal-install.md，10496字节，dc46e05bb8e01873c5ce359a9d2665d57e27e4c9a5d89c11ade18fd4128c61cc。
- config/normal-install.example.json，869字节，95c97092a95fd39b116fe4e85fd4d5d4c7bb6757fc45efe76cc600863b55df3b。
- backend/tests/test_normal_install.py，26021字节，ca2fb5fa09776a73e6e8983dd2a47f9be399dcc141ea196f31ec8a6cf69e4633。
- README.md，27130字节，7ebb7d680949ce10c9c63f2e31b26f318145eba3309ab42e1891783526602db8。

README的pre为0410c7573027f7f6e75635c3a8d050e2be375d98ab0a4b503ddf3e076104d938。其余原迁移/运行入口/产品app/原模板/依赖锁不在125写入范围。

## 一次集中审查标准

### A 默认关闭、本地输入及计划

默认/help/坏参数/plan是否确实不会连接PG、启动进程、读取真实凭据、装载app/ControlHub/QAuthority或写安装结果。确认plan的结构通过、输入不完整、真实目标未观察和安装/资格未验证可区分，不把示例/null/字节长度误当实际ready。

校验原始15份固定白名单/顺序/hash与正式profile，不glob并吸纳未来SQL；固定清单不是由调用者可替换的信任根。考察配置严格类型、对象标识、目标身份冲突和文件路径/junction/NTFS别名/输出冲突边界；按实际威胁和原合同判断，不要求能抵御拥有操作系统管理员权限的人篡改整个产品。路径TOCTOU只在可触达且影响原边界时定级，不机械把任意理论竞态当P1。

### B 身份和空库预检

显式apply在DDL/DCL/业务写之前是否核精确loopback连接、实际数据库名/OID/system_identifier/安装身份/PG版本、全新空库与独占集群、vector适用性及全局角色碰撞。主机映射地址与PG服务端实际地址应正确区分，不错误要求两端同端口，也不因允许容器NAT绕开真实身份核对。

不得静默采用旧用户/TESTONLY/共享角色或重置其密码。确切输入缺失、目标不符、非空/碰撞时应零数据库写。安装意图收据的本地记录不等于DDL或账本写入，按真实副作用区分。

### C 迁移顺序和中断语义

逐项对账完整001—015固定原SQL、013后normal/R01控制行、014/R02和015/R03以及最终schema/role检查，核现有模型/函数/guard实际所需字段和顺序。不得替换CREATE ROLE、去掉010/011碰撞guard、规范化SQL以伪造hash或从tests/DocuN读取实现。

各文件原BEGIN/COMMIT须保留，不承诺整包一个原子事务。检查多语句结果集/COMMIT确认、局部阶段、响应丢失、最后核验失败、收据写入失败和重复apply的实际路径。已确认与提交未知不能混淆，不能误记整体installed、自动重放/清空或使verify写入。收据仅部署元数据，不是新的授权或金融账。

### D 角色及真实可用性

检查登录创建、业务/快照职责组、INHERIT/SET/ADMIN选项、CONNECT/对象权限、安装管理员与业务进程的隔离。确认新工具真正复用当前schema_checks/q_roles的实际能力检查，包括传递SET/INHERIT/ADMIN及owner路径，而非仅直接membership。

重点找会导致未来合法首次安装必败、最终业务连接不可用或snapshot越权的确定代码问题，不只复述18个替身用例。也不把首次安装没有覆盖就地升级判为本范围缺陷；其明确只支持独立新集群空库。PG语法/实际ACL尚未运行需分清静态可判与动态未知，不凭Mock称真实成功。

### E 凭据、关闭配置和启动兼容

凭据只按显式未来安全通道读取，不能进入argv、说明、错误/日志/计划/安装收据；未知异常内容不外泄。维护摘要按既有模型只应写DB，不成为公开安装收据内容。示例和原原生模板保持关闭，不构造grant、operator批准、T0或真实Q根。不新增旧loader不支持字段来冒充关闭。

新工具不能暗改start_local重开、旧001初始化或原source/readonly恢复资格。README和说明里的参数必须对应最终真实入口，无不存在参数，准确说明未来独审/精确许可与目前未运行边界。不要把外部token/账号仍缺变成此离线工程必须重复研究的门槛。

### F 测试、字节绑定及执行控制

独立核批2的18方法、0失败/错误/skip、exit0及实际受测六文件与最终字节一致。读harness/runner，判断隔离、调用记录器、审计钩子和纯角色样本真实能证明什么；禁止将0计数字段本身当全系统无副作用的独立证明。核批1的junction夹具失败原文、后续实际junction断言与NAT修正是否对应实际增量，不能篡改首批为通过。

审两批上限、单批600秒、许可24h、工具10800含900收尾的事实。工程精确工具总wall为unknown、保守列支3600/10800；检查可恢复记录/封存时间能否支持，不能把两个进程实测之和当总投入。脚本预算/结果保存的缺失和偏差据实分级，未知不伪成精确合规或已违规。旧120/117历史失败与原123/124封存账均不清零。

本地NTFS junction夹具留在125的execution/scratch，允许只读核实际reparse目标与原记录的范围，不能为审计重新创建或删除。读任何嵌套目录前查reparse边界，不递归跟随junction扫描。

### G 后续最小真实验证清单

按真实新风险给一份可直接编排的有限清单，精确指到安装入口/观察项、适用状态和现存缺口。至少包括新正常空库完整001—015/R03及业务/快照实际角色与连接、关闭配置下正常启动/同库重开/停止、身份/空库/碰撞零写拒绝、一次安装中断或提交未知保留与无自动重放、成功收据verify只读。安全失败可用单个有界事务/只读比较或预先构造状态完成的，不默认各建一套容器或重跑全项目。

需要补的用例说明真实观察与最少资源，不在本卡编写/运行。不会因本卡动态额度0就判代码自动失败，也不将后续PG未跑写成当前动态通过。不得要求已可静态确定的夹具错误等到未来再耗真实额度。

## 范围、资源及停止

只读上述冻结对象及必要直接依赖。只写TASK126/audit证据和TASK126-result.md，不改源码、测试、SQL、配置、README、dist、旧证据、原结果、主控orchestration、DocuS或公共库。不读实际local/private配置、.runtime、凭据库、账号后台、用户资料/库或旧封存数据库。

允许PowerShell/标准库作有界文件读取、hash、JSON、文本diff及AST分析。禁止导入/运行产品、安装器CLI（含help/plan）、compile/unittest、PG/Docker/Compose/端口/应用/浏览器/Job/预览/模型/Embedding/网络、依赖安装和Git写入；真实资源与费用额度全0。不得用不可信源文件作为可执行脚本加载；不创建子Agent或发外部消息。

本卡新工具wall上限3600秒，含480秒保存，单命令通常60秒，日历permit签发至24h，先到停止。足够一次覆盖即停；不为用尽预算扩审。旧TASK124余量和125未用第三批不是本卡许可。根因/对象不稳定、需业务修改、新重大决定或预算到门时，停止相应审查，完成不受阻部分后带精确缺口回传。

确定缺陷按P0—P3，给来源、触发、影响及最小修正，修复归原125工程窗口。本卡不得直接修复；发现明确数据破坏/凭据泄露先留证回报，其余完成一次全范围审查后统一交回。非阻塞观察不自动升级新硬门槛，审计范围外增强不作为本次关闭条件。

## 回传

结果先给三轴结论和可否进入未来精确首次安装运行门，列独立性、六文件及直接依赖hash、审查范围、逐项事实定位、确定问题/条件/未知、原18方法证据适用性、失败和执行账、后续最小真实验证清单、需主控同步文档与最少人工。保存完整报告并复读，历史补证按轮次追加不改旧结论。

不能填写主控最终验收或签Q、真实安装/权限/语义、STEP018/019/020、M1或项目通过。无须用户提供key、开服务、释放内存或删除文件。完成后只回复一句话结论及可点击的D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-126-result.md绝对路径，用户带回主控。
'''


def main():
    now = datetime.now(TZ)
    timestamp = now.isoformat()
    state_rel = 'DocuS/执行动态文档.MD'
    arch_rel = 'DocuS/架构动态文档.MD'
    changes_rel = 'DocuS/文档变更记录.MD'
    before = {name: read(name) for name in (state_rel, arch_rel, changes_rel)}
    assert '文档v2.93' in before[state_rel].decode('utf-8-sig')[:120]
    assert '文档v1.65' in before[arch_rel].decode('utf-8-sig')[:120]
    assert max(map(int, re.findall(r'CHG-(\d+)', before[changes_rel].decode('utf-8-sig')))) == 1632
    assert not p('DocuN/tasks/TASK-126.md').exists()
    assert not p('DocuN/results/TASK-126-result.md').exists()
    assert not p('DocuN/results/TASK-125-work-decision.md').exists()
    rows = []

    def check(relative, expected, group, byte_count=None):
        source = p(relative)
        raw = source.read_bytes()
        actual = sha(raw)
        assert actual == expected, (relative, group, actual, expected)
        assert byte_count is None or len(raw) == byte_count, relative
        rows.append({'path': relative, 'absolute_path': str(source), 'group': group,
                     'bytes': len(raw), 'sha256': actual, 'matched': True})

    receipt = load(EXEC + 'closing-receipt.json')
    result_row = receipt['result']
    report = 'DocuN/results/TASK-125-result.md'
    check(report, result_row['sha256'], 'returned_report', result_row['bytes'])
    post = load(EXEC + 'post-snapshot.json')
    tested = load(EXEC + 'tested-before-batch-02.json')
    assert post['products'] == tested
    for item in post['products']:
        check(item['path'], item['sha256'], 'final_product', item['bytes'])
        check(EXEC + 'post/' + item['path'], item['sha256'], 'post_copy', item['bytes'])
        check(item['path'], item['sha256'], 'batch02_tested_binding', item['bytes'])
    current_readme = next(r for r in post['products'] if r['path'] == 'README.md')
    initial = load('DocuN/evidence/TASK-125/orchestration-20261022/input-manifest.json')
    for item in initial['sources']:
        source = Path(item['absolute_path'])
        raw = source.read_bytes()
        expected = current_readme['sha256'] if item['path'] == 'README.md' else item['sha256']
        actual = sha(raw)
        assert actual == expected, (item['path'], 'initial_source_drift')
        rows.append({'path': item['path'], 'absolute_path': str(source), 'group': 'initial_source_preservation',
                     'bytes': len(raw), 'sha256': actual, 'matched': True,
                     'allowed_changed_readme': item['path'] == 'README.md'})
    for item in receipt['artifacts']:
        check(item['path'], item['sha256'], 'raw_artifact', item['bytes'])
    check(EXEC + 'pre/README.md', '0410c7573027f7f6e75635c3a8d050e2be375d98ab0a4b503ddf3e076104d938', 'readme_pre')
    old_lines = read(EXEC + 'pre/README.md').splitlines(keepends=True)
    new_lines = read('README.md').splitlines(keepends=True)
    assert len(old_lines) == len(new_lines)
    changed_lines = [i + 1 for i, (a, b) in enumerate(zip(old_lines, new_lines)) if a != b]
    assert changed_lines == [33], changed_lines
    migration_manifest = load('deploy/normal_install_manifest.json')
    for item in migration_manifest['migrations']:
        check(item['path'], item['sha256'], 'installer_migration_manifest', item['bytes'])
    for item in migration_manifest['closed_templates']:
        check(item['path'], item['sha256'], 'installer_template_manifest')
    summary = load(EXEC + 'batch-02-summary.json')
    command = load(EXEC + 'batch-02-command.json')
    raw = read(EXEC + 'batch-02-output.txt').decode('utf-8')
    assert (summary['tests_run'], summary['failures'], summary['errors'], summary['skipped'], command['exit_code']) == (18, 0, 0, 0, 0)
    assert len(summary['records']) == 18
    assert not summary['denied_effect_attempts']
    assert raw.count(' ... ok') == 18 and 'Ran 18 tests' in raw and raw.rstrip().endswith('OK')
    first = load(EXEC + 'batch-01-summary.json')
    first_command = load(EXEC + 'batch-01-command.json')
    assert (first['tests_run'], first['failures'], first['errors'], first['skipped'], first_command['exit_code']) == (18, 1, 0, 0, 1)
    assert 'junction_create_failed' in read(EXEC + 'batch-01-output.txt').decode('utf-8')
    ledger = load(EXEC + 'command-ledger.json')
    assert ledger['budget']['used_test_batches'] == 2
    assert ledger['budget']['exact_total_tool_wall_seconds'] is None
    assert ledger['budget']['conservative_charge_seconds'] == 3600
    old_permit = load('DocuN/evidence/TASK-125/orchestration-20261022/permit.json')
    assert datetime.fromisoformat(receipt['observed_utc']) < datetime.fromisoformat(old_permit['issued_at']) + timedelta(seconds=3600)
    assert '*' not in CARD and '〈' not in CARD and '| ---' not in CARD
    evidence_files = [entry['path'] for entry in receipt['artifacts']]
    extra_sources = [
        'DocuN/tasks/TASK-125.md', 'DocuN/evidence/TASK-125/orchestration-20261022/permit.json',
        'AGENTS.md', 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json',
        'backend/app/data_exit/schema_profiles.py', 'backend/app/data_exit/schema_checks.py',
        'backend/app/data_exit/q_roles.py', 'backend/app/data_exit/files.py', 'backend/app/data_exit/config.py',
        'backend/app/data_exit/schema.py', 'backend/app/data_exit/contracts.py',
        'deploy/start_local.py', 'deploy/initialize-materials.py', 'deploy/compose.local.yml',
        'config/data-exit.example.json', 'DocuS/最终需求文档.MD',
    ]
    for relative in extra_sources:
        assert p(relative).is_file(), relative
    for name, old in before.items():
        put(RETURN + 'before/' + Path(name).name, old)
    result = {
        'TASK': 'TASK-125', 'R': 'R-119', 'checked_at': timestamp, 'identity_reference_checks': len(rows),
        'mismatches': 0, 'rows': rows, 'readme_changed_byte_lines': changed_lines,
        'batch02': {'tests': 18, 'failures': 0, 'errors': 0, 'skips': 0, 'exit_code': 0,
                    'process_seconds': command['elapsed_seconds'], 'unittest_seconds': summary['elapsed_seconds']},
        'batch01_failure_preserved': True, 'original_product_tests_rerun_by_orchestrator': False,
        'exact_total_engineering_wall': None, 'conservative_charge': 3600,
        'scope': '文件身份/差异/已有证据回收，非独立代码审计或PG动态验证',
    }
    dump(RETURN + 'return-check.json', result)
    decision = f'''# TASK125/R119工程候选已回收，待首次安装前集中独审

{timestamp}，Asia/Shanghai。主控读取实际结果、六文件差异导航与原始批次/受测身份；核{len(rows)}条身份引用零漂移。候选工程交付已返回、离线定向证据有效范围已确认，任务最终验收留空，等待原合同规定的安装迁移/角色权限独立审查。不是签首次安装或正常部署成功。

六份当前产品与第二批受测及post副本逐字节相符；README除第33行外包括原换行均不变，五项新文件pre为不存在。61输入除许可README外按原hash不变，15迁移和四关闭原生模板与新清单相符。完整统一diff只涉及本卡六文件，不把旧Git差异算本轮新成果。

第二批18方法0失败/error/skip、原日志OK/命令exit0成立，进程1.0162982000038028秒与测试器0.4948959000175819秒是不同计时不相加。第一批18中1个junction创建夹具失败、WinError5诊断、实际空目录junction的有界修正及NAT普通自查修正保留。记录器/纯角色样本只证明本地流程/输入方案，不证明真实PG/事务/ACL。

工程精确总工具wall为unknown；3600/10800为许可签发至首小时封存的保守包络，不冒充逐命令实测。两批2/3及余7200秒封存，不恢复执行，旧各任务失败/未知/预算保持。原工程窗口停止写入产品与证据以供审查。主控没有重跑测试、产品导入、PG、Docker、服务或资源探针；不把旧停止证明称现在实时核验。

TASK126/R120一次集中独审已登记待转交，优先原TASK124独立A+窗口，未参与125否则新隔离窗口。只审本组六文件与直接影响、18方法字节证据及控制；运行全0。稳定成果首次apply前的原必需门照留，不增加逐文件审计，不重审原123/124和120/121未变代码。

Q仍冻结，T0为空、provider/费用0；外部token/模板/Embedding容量/本人账号和真实normal部署前置没有新增。现安装器是待审工程，不具备执行本卡真实apply的权限。通过后真实资源与最小运行清单仍须另行精确许可，不用旧封存runner或合成库代替。STEP018/019/020、M1/项目未放行。

结果文件当前hash为{result_row['sha256']}，{result_row['bytes']}字节。有限核证位于DocuN/evidence/TASK-125/orchestration-return-20261022。最终验收由主控在独审返回后裁定。
'''
    put('DocuN/results/TASK-125-work-decision.md', decision)
    registered = f'''# 执行动态文档

文档v2.94，2026-10-22，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.66、task_model/07。以下v2.93原字节保留。

## TASK125已返回；TASK126/R120集中独审已登记

{timestamp}。主控已核工程返回与{len(rows)}条身份引用无漂移。TASK125候选冻结待审，最终验收留空；TASK126完整卡生成核读中，尚未转交。

'''
    put(state_rel, registered.encode('utf-8') + before[state_rel])
    card_path = put('DocuN/tasks/TASK-126.md', CARD)
    assert card_path.read_text(encoding='utf-8') == CARD
    state_prefix = f'''# 执行动态文档

文档v2.94，2026-10-22，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.66、task_model/07。以下v2.93原字节保留。

## TASK125工程候选已回收冻结；TASK126/R120首次安装前集中独审待人工转交

{timestamp}。用户已带回TASK125/R119实际结果，调度已返回，工程候选及离线证据按范围核收，最终验收留空待原必需独审。报告{result_row['bytes']}字节/hash{result_row['sha256']}；主控核{len(rows)}条身份引用零漂移，六当前文件与批2实际受测/post字节一致，README仅第33行变化，61输入按允许差异、15SQL与四关闭模板均相符。不能据报告存在或记录器通过签真实安装。

批2原日志18方法0失败/error/skip、exit0，父进程1.0162982秒、测试器0.4948959秒分别记录不相加；批1的junction夹具失败1项及后续真实夹具断言/NAT普通自查修正原件保留。没有重跑18方法或旧123的13方法。总工具精确unknown，首小时封存保守3600/10800及批2/3采纳为有限账，余7200秒和第三批封存不再自动可用；原120/117/123/124失败/unknown与预算保持。原工程窗口停止写入稳定对象。

TASK126/R120完整只读集中合同DocuN/tasks/TASK-126.md已保存核读，待用户人工转交，未宣称接收/启动。A+优先原TASK124独审窗口，须未参与125，否则新隔离窗。范围为本组六文件/直接依赖、两批原始18方法证据及控制，工具3600秒含480保存/24h、单命令60s、业务/compile/测试/PG/Docker/联网/Git全0。独审检查角色/迁移/提交未知等首次apply风险，并给后续最小真实验证清单；不重审未变旧业务，不立即派真实运行卡。

当前安装工具和清单/关闭模板只是已实现候选、离线定向验证，真实profile/角色/安装/正常启动未验证。Q继续冻结、T0/72h为空，真实provider/费用0，正常资源和外部计量/版本模板/Embedding容量/本人账号门未新增。100/25固定分额、28Must/89动作/24片6索引不变。STEP018进行中/部分验证，019/020/M1/项目/发布未放行；主控只有文件核证，无实时服务探针。

回收与裁定在DocuN/evidence/TASK-125/orchestration-return-20261022和TASK-125-work-decision.md；独立输入/许可在DocuN/evidence/TASK-126/orchestration-20261022。CHG1633—1638，下一1639。

## 以下为v2.93及更早历史

'''
    put(state_rel, state_prefix.encode('utf-8') + before[state_rel])
    arch_prefix = f'''# 架构动态文档

文档v1.66，2026-10-22，Asia/Shanghai。需求v1.4、执行动态v2.94、task_model/07。以下v1.65原字节保留。

## 正常首次安装工具候选落地，实际运行待原必需风险审查

{timestamp}。TASK125/R119返回deploy/initialize_normal.py、固定001—015清单、关闭安装示例、新说明/18方法测试及README最小修改。入口有默认帮助/本地plan、未来显式apply及完整收据verify；目标独立新PG17空库/R03。原SQL/profile和业务app/原启动链未变。此为已实现候选及离线控制流证据，真实PG/事务/ACL/profile/正常启动仍未验证。

安装清单和输出身份是工具元数据，不新增业务模型、授权平台或迁移账表；原业务/快照职责组及直接/传递能力检查保持。首次实际apply前的迁移/角色/凭据/未知提交风险由TASK126集中独审当前稳定六文件与原始证据，未获独审通过或运行权。正常资源、真正loader/绑定及Q外部计量/账号/首次启用门保持，100/25和原Must/两provider不变。

原readiness/progress理由以及120/121未变成果按范围继承，不进行重复整仓审查。本轮未运行产品或创建资源。

## 以下为v1.65及更早历史

'''
    put(arch_rel, arch_prefix.encode('utf-8') + before[arch_rel])
    descriptions = [
        (1633, 'DocuN/results/TASK-125-work-decision.md', '登记工程候选已返回、已有18方法/身份核收、最终验收待原独审；原失败与精确计时unknown保留。'),
        (1634, 'DocuN/tasks/TASK-126.md', '新建R120一次只读集中独审完整卡，原独审A+窗口优先，保存核读后待人工转交，不运行真实资源。'),
        (1635, arch_rel, 'v1.66登记首次安装工具已实现候选/离线证据和真实PG/权限仍未验证，不变模型/业务/Q门。'),
        (1636, state_rel, 'v2.94登记125已返回冻结和126待转交、两批原件/封存账及未放行门。'),
        (1637, 'DocuN/evidence/TASK-125/orchestration-return-20261022', '保存有限身份/README原字节/原始证据核对、旧共享及收口导航，主控产品运行0。'),
        (1638, 'DocuN/evidence/TASK-126/orchestration-20261022', '保存独立输入/六文件冻结/原始证据导航、只读许可和读回，不传工程自评或实现聊天。'),
    ]
    addition = '\n\n' + '\n\n'.join(f'- CHG-{number}，{timestamp}，Codex编排Agent，{name}。{description}'
        for number, name, description in descriptions) + '\n'
    put(changes_rel, before[changes_rel] + addition.encode('utf-8'))
    audit_sources = [item['path'] for item in post['products']] + evidence_files + extra_sources
    audit_sources += [item['path'] for item in migration_manifest['migrations']]
    audit_sources += [item['path'] for item in migration_manifest['closed_templates']]
    audit_sources += [EXEC + 'pre/README.md', state_rel, arch_rel]
    audit_sources = list(dict.fromkeys(audit_sources))
    identities = []
    for relative in audit_sources:
        content = read(relative)
        identities.append({'path': relative, 'absolute_path': str(p(relative)), 'bytes': len(content), 'sha256': sha(content)})
    rules = load('DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
    for row in rules:
        raw_rule = Path(row['absolute_path']).read_bytes()
        assert sha(raw_rule) == row['sha256']
        identities.append({'path': row['relative_path'], 'absolute_path': row['absolute_path'],
                           'bytes': len(raw_rule), 'sha256': sha(raw_rule), 'public_readonly': True})
    input_manifest = dump(AUDIT + 'input-manifest.json', {
        'TASK': 'TASK-126', 'R': 'R-120', 'issued_at': timestamp, 'products': post['products'],
        'sources': identities, 'source_count': len(identities),
        'explicitly_excluded': ['DocuN/results/TASK-125-result.md', '实现聊天/完整思考/自评',
                                '私有配置/.runtime/用户库/凭据/历史数据库'],
        'main_verification_scope': '身份/原始日志/实际差异，非产品独审预结论',
    })
    index = dump(AUDIT + 'raw-evidence-index.json', {
        'TASK': 'TASK-126', 'R': 'R-120', 'upstream_contract': 'DocuN/tasks/TASK-125.md',
        'six_frozen_products': post['products'], 'raw_artifacts': receipt['artifacts'],
        'pre_readme': EXEC + 'pre/README.md', 'post_copy_root': EXEC + 'post/',
        'prior_rule_snapshot': 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json',
        'boundaries': ['元数据不替代当前重算', '记录器/纯样本不证明PG事务/ACL',
                       '工程结果自评及完整聊天不属独立输入', '没有后继运行许可'],
    })
    permit = dump(AUDIT + 'permit.json', {
        'schema': 'retrolume.task-scope.v1', 'TASK': 'TASK-126', 'R': 'R-120',
        'execution_class': 'READONLY_INDEPENDENT_FIRST_INSTALL_AUDIT',
        'issued_at': timestamp, 'deadline': (now + timedelta(hours=24)).isoformat(),
        'contract_sha256': sha(card_path.read_bytes()), 'input_manifest_sha256': sha(input_manifest.read_bytes()),
        'raw_evidence_index_sha256': sha(index.read_bytes()), 'dispatch_status': '待人工转交', 'acceptance': None,
        'recipient': 'A+原TASK124独审窗口，未参与125；否则新隔离审计窗口',
        'tool_wall_cap_seconds': 3600, 'reserved_close_seconds': 480, 'per_command_seconds': 60,
        'allowed_writes': ['DocuN/evidence/TASK-126/audit/', 'DocuN/results/TASK-126-result.md'],
        'caps': {name: 0 for name in ('product_import', 'installer_cli', 'compile', 'test', 'pg', 'docker',
                'service', 'browser', 'job', 'preview', 'provider', 'embedding', 'network', 'git_write',
                'fee_cny', 'delegation', 'product_write')},
        'historical_budgets_reopened': False, 'Q': 'FROZEN', 'T0': None,
    })
    for row in identities:
        assert sha(Path(row['absolute_path']).read_bytes()) == row['sha256'], row['path']
    for name in (state_rel, arch_rel):
        assert read(name).endswith(before[name])
    assert read(changes_rel).startswith(before[changes_rel])
    assert not p('DocuN/results/TASK-126-result.md').exists()
    assert sha(read(report)) == result_row['sha256']
    for item in post['products']:
        assert sha(read(item['path'])) == item['sha256']
    proof = {
        'TASK': 'TASK-126', 'R': 'R-120', 'issued_at': timestamp, 'checked_at': datetime.now(TZ).isoformat(),
        'status': '待人工转交', 'input_identities': len(identities), 'upstream_identity_reference_checks': len(rows),
        'mismatches': 0, 'contract_bytes': card_path.stat().st_size, 'contract_sha256': sha(card_path.read_bytes()),
        'input_manifest_sha256': sha(input_manifest.read_bytes()), 'permit_sha256': sha(permit.read_bytes()),
        'shared_state_version': '2.94', 'architecture_version': '1.66', 'next_CHG': 1639,
        'historical_shared_bytes_preserved': True, 'product_runtime': 0, 'new_test_runs': 0,
        'TASK125_acceptance': '未裁定，待必需独审', 'Q': 'FROZEN', 'T0': None,
    }
    dump(AUDIT + 'save-proof.json', proof)
    dump(RETURN + 'return-receipt.json', {
        'TASK': 'TASK-125', 'R': 'R-119', 'checked_at': timestamp, 'dispatch': '已返回',
        'acceptance': None, 'candidate_received': True, 'evidence_verified_scope': result['scope'],
        'report_sha256': result_row['sha256'], 'verification_sha256': sha(read(RETURN + 'return-check.json')),
        'next_task': 'TASK-126', 'next_dispatch': '待人工转交', 'product_tests_rerun': False,
        'engineering_budget_sealed': True, 'Q': 'FROZEN',
    })
    print(json.dumps({k: proof[k] for k in ('TASK', 'R', 'status', 'upstream_identity_reference_checks',
        'input_identities', 'mismatches', 'contract_bytes', 'new_test_runs', 'next_CHG', 'Q')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
