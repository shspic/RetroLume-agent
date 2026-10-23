"""登记已确认采用包，保存人工任务卡和共享文档；不导入或运行产品。"""
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
PUBLIC = Path('D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4')
OUT = ROOT / 'DocuN/evidence/TASK-127/orchestration-20261022'
CARD = ROOT / 'DocuN/tasks/TASK-127.md'
STATE = ROOT / 'DocuS/执行动态文档.MD'
ARCH = ROOT / 'DocuS/架构动态文档.MD'
CHANGE = ROOT / 'DocuS/文档变更记录.MD'
PRIOR = ROOT / 'DocuN/evidence/TASK-125/orchestration-closure-20261022'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def describe(path):
    data = path.read_bytes()
    try:
        relative = path.relative_to(ROOT).as_posix()
    except ValueError:
        relative = path.as_posix()
    return {'path': relative, 'absolute_path': path.as_posix(), 'bytes': len(data), 'sha256': digest(data)}


def save_json(path, value):
    data = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    with path.open('xb') as stream:
        stream.write(data)
    assert path.read_bytes() == data


def safe_parent(path):
    for current in [path, *path.parents]:
        if current.exists():
            stat = current.lstat()
            if current.is_symlink() or getattr(stat, 'st_file_attributes', 0) & 0x400:
                raise RuntimeError('输出路径存在重解析边界')
        if current == ROOT:
            return
    raise RuntimeError('输出路径越出项目')


def main():
    for path in (OUT, CARD, STATE, ARCH, CHANGE):
        safe_parent(path)
    if CARD.exists() or (OUT / 'adoption-receipt.json').exists():
        raise RuntimeError('本次任务已登记或存在部分写入，须核断点而非重发')
    state_old, arch_old, change_old = STATE.read_bytes(), ARCH.read_bytes(), CHANGE.read_bytes()
    assert '文档v2.97' in state_old.decode('utf-8-sig').splitlines()[2]
    assert '文档v1.69' in arch_old.decode('utf-8-sig').splitlines()[2]
    assert 'CHG-1658' in change_old.decode('utf-8-sig')[-2200:]
    assert 'CHG-1659' not in change_old.decode('utf-8-sig')
    proposal = PRIOR / 'approval-proposal.md'
    draft_path = PRIOR / 'proposed-scope.json'
    assert digest(proposal.read_bytes()) == '543cff441295f519e1e10081b5efaf5273ed367836ddbd30cc9bc73a38775908'
    assert digest(draft_path.read_bytes()) == '2228579489ec5a52d35d6271f94a76ee9ff61f554d20fc6641e371a4bd7ff381'
    draft = json.loads(draft_path.read_bytes())
    assert draft['adopted'] is False and draft['executable'] is False
    rule_snapshot = json.loads((ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json').read_bytes())
    needed_rules = {'DocuS/AGENTS.MD', 'DocuS/WORK.MD', 'task_model/TASK_TEMPLATE.md', 'task_model/prompts/07_开发执行循环.md'}
    rules = []
    for entry in rule_snapshot:
        relative = entry['relative_path'].replace('\\', '/')
        if relative in needed_rules:
            item = describe(PUBLIC / relative)
            assert item['sha256'] == entry['sha256'], relative
            rules.append(item)
    assert len(rules) == 4
    frozen = {
        'deploy/initialize_normal.py': '68d7b71fc7296111e894df4cba21a4ed7830f9cff069c1fc500dfbd7734c0a09',
        'backend/tests/test_normal_install.py': '93dabd4887760641884fc7ca5d5c83e520522563ea2d44be4dc2e72db320c3b7',
        'deploy/normal-install.md': 'fb553199dafb11be8608a3608ff2f18778f07acbff265badb2994855c0fd6ddb',
        'deploy/normal_install_manifest.json': 'f2ed126daa1c5a982b490a9343d6c17053c0f385e7a2f55676ecf4132dd2abf0',
        'config/normal-install.example.json': '95c97092a95fd39b116fe4e85fd4d5d4c7bb6757fc45efe76cc600863b55df3b',
        'README.md': '7ebb7d680949ce10c9c63f2e31b26f318145eba3309ab42e1891783526602db8',
    }
    bundle = json.loads((ROOT / 'deploy/normal_install_manifest.json').read_bytes())
    for entry in bundle['migrations'] + bundle['closed_templates']:
        frozen[entry['path']] = entry['sha256']
    # 复用原独审已核的产品直接依赖，不引入旧执行器为产品依赖。
    prior_inputs = json.loads((ROOT / 'DocuN/evidence/TASK-126/orchestration-review01-20261022/input-manifest.json').read_bytes())
    for entry in prior_inputs['sources']:
        relative = entry['path'].replace('\\', '/')
        if relative.startswith(('backend/', 'deploy/', 'config/')) or relative == 'README.md':
            old_hash = frozen.setdefault(relative, entry['sha256'])
            assert old_hash == entry['sha256'], relative
    direct = [
        'deploy/compose.local.yml', 'deploy/start_local.py', 'backend/app/main.py',
        'backend/app/runtime.py', 'backend/app/service_config.py', 'backend/app/q_readiness.py',
        'backend/app/data_exit/config.py', 'backend/app/data_exit/control.py',
        'backend/app/data_exit/files.py', 'backend/app/data_exit/repository.py',
        'backend/app/data_exit/schema.py', 'backend/app/data_exit/schema_checks.py',
        'backend/app/data_exit/schema_profiles.py', 'backend/app/data_exit/q_roles.py',
        'config/data-exit.example.json', '.gitignore',
    ]
    for relative in direct:
        frozen.setdefault(relative, digest((ROOT / relative).read_bytes()))
    sources = []
    for relative, expected in sorted(frozen.items()):
        item = describe(ROOT / relative)
        assert item['sha256'] == expected, relative
        sources.append(item)
    previous_reports = {
        'DocuN/results/TASK-125-result.md': '694cf89b93b7f0c32f7c0a21513520de9d93aeba9c1175443fb725399f7ad084',
        'DocuN/results/TASK-126-result.md': '97f250fa74b5d95ee9e8b749745df88c1a1823a9e9f2ad78d807303c15918318',
    }
    for relative, expected in previous_reports.items():
        assert digest((ROOT / relative).read_bytes()) == expected, relative
    issued = datetime.now(timezone(timedelta(hours=8)))
    until = issued + timedelta(hours=24)
    stamp, deadline = issued.isoformat(), until.isoformat()
    OUT.mkdir(parents=True, exist_ok=True)
    before = OUT / 'before'
    before.mkdir(exist_ok=False)
    for path, data in [(STATE, state_old), (ARCH, arch_old), (CHANGE, change_old)]:
        (before / path.name).write_bytes(data)
    approval = {
        'proposal_id': draft['proposal_id'], 'TASK': 'TASK-127', 'R': 'R-121',
        'recorded_at': stamp, 'timezone': 'Asia/Shanghai',
        'user_message_exact': '确认', 'approval_message_exact_timestamp': None,
        'basis': '用户确认上一轮已展示并落盘的AP-125-NORMAL-INSTALL-01合并操作包',
        'proposal': describe(proposal), 'draft_scope': describe(draft_path),
        'adopted': True, 'old_drafts_unchanged': True,
        'runtime_by_orchestrator': 0, 'human_transfer_required': True,
    }
    save_json(OUT / 'adoption-receipt.json', approval)
    scope = dict(draft)
    scope.update(adopted=True, executable=True, next_task_assigned=True,
                 TASK='TASK-127', R='R-121', issued_at=stamp, valid_until=deadline,
                 execution_requires='人工转交后由唯一指定工程窗口按TASK127/permit执行；平台权限继续适用')
    scope['roles'] = {
        'source': {'business': 'retrolume_normal_app', 'snapshot': 'retrolume_normal_snapshot'},
        'interrupted': {'business': 'retrolume_interrupt_app', 'snapshot': 'retrolume_interrupt_snapshot'},
    }
    scope['approved_exact_temporary_objects'] = ['source:public.retrolume_install_probe_nonempty', 'source:retrolume_data_app/NOLOGIN']
    scope['one_expected_unknown_commit'] = 'interrupted/002实际COMMIT后的确认隐藏；不得重放或续装'
    save_json(OUT / 'adopted-scope.json', scope)
    inputs = {
        'TASK': 'TASK-127', 'R': 'R-121', 'issued_at': stamp,
        'requirements_version': '1.4', 'architecture_version': '1.70', 'state_version': '2.98',
        'sources': sources, 'rules': rules,
        'adoption': describe(OUT / 'adoption-receipt.json'),
        'scope': describe(OUT / 'adopted-scope.json'),
        'root_entry': describe(ROOT / 'AGENTS.md'),
        'prior_reports': [describe(ROOT / relative) for relative in previous_reports],
        'prior_closure': describe(PRIOR / 'closure-receipt.json'),
        'runtime_observed_by_orchestrator': False,
    }
    save_json(OUT / 'input-manifest.json', inputs)

    task = '''# TASK-127 / R-121 关闭外发的首次正常安装与六项真实部署验证

## 目标与交付

你是本卡A+工程执行者，继续原TASK-125安装工程窗口，不接管主控或独立审计。将已独审的首次安装器用于两个新隔离PG槽位，在一张卡内连续交付六项真实检查、原生关闭配置启动/同库重开/停止和完整证据。目标是消除真实安装、权限与启动的具体缺口，Q不启用。

完整交付包括实际资源身份、源成功安装收据、独立中断保留收据、真实权限及两次原生API生命期、只读verify、预算与精确停止证明。报告保存到D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-127-result.md。证据及本卡验证辅助脚本只写D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-127/execution/。不为正常子步骤回传，不重跑已充分验证的18/9项离线检查。

六项全部符合、无新增确定阻断、最终对象可核、资源停止且账目完整才可建议本卡完成；任一未执行或失败均保留实际状态，不以文档或记录器结果冒充真实通过。本卡不裁定STEP018/019/020、M1、项目或发布通过。

## 项目、规则与接收安排

项目根D:/shspic/project_NO3_RetroLume-agent，根入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。模式task_model；锁定V4.0、公共AGENTS CHG-0003，不自动采用后来版本。

公共根D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4。读取该根DocuS/AGENTS.MD；WORK.MD第二、四至九章仅取执行合同/资源/结果和停止条款。锁定指纹在项目DocuN/evidence/v4-migration-20260930/rules-snapshot.json。本卡按同版task_model/TASK_TEMPLATE.md制定；共享状态维护、编号和最终裁定只归主控。

接收为A+增强执行，优先原TASK125工程窗口。理由是事务提交未知、原始迁移与权限、Windows根绑定和真实生命周期需连续强推理。实际客户端/模型如实登记，不以标签冒充型号；原TASK126独审窗口不承担本卡执行。没有并行工程或审计安排，本卡产品/配置读取对象冻结。

关联TASK125/R119有限工程与TASK126/R120独审，STEP018部署前置、STEP019适用权限证据、STEP020本机交付，NFR-004/CON-002/DR-002及原角色隔离约束。需求v1.4、架构v1.70、执行动态v2.98。

授权是用户本轮原话“确认”采用AP-125-NORMAL-INSTALL-01。原草案approval-proposal.md SHA256=543cff441295f519e1e10081b5efaf5273ed367836ddbd30cc9bc73a38775908，proposed-scope.json SHA256=2228579489ec5a52d35d6271f94a76ee9ff61f554d20fc6641e371a4bd7ff381，均在DocuN/evidence/TASK-125/orchestration-closure-20261022/并原字节保留。新采用回执、adopted-scope.json、input-manifest.json及permit.json在D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-127/orchestration-20261022/。草案的adopted=false是采用前历史，以新回执和本卡许可为当前依据。

本卡是已验收安装工具之后的新真实验证单元，不复活125/126旧许可。125原工具精确unknown/保守4200秒/10800秒与3/4批、126精确unknown/保守2400秒/3600秒和未用额度封存；120根64/64及149失败、117旧81等历史账照留，不移入本卡假装清零。本卡新增真实尝试在签发时尚为0，实际运行前必须检查残留而非依据主控未探测推断已清场。

签发@ISSUED@；日历截止@DEADLINE@，Asia/Shanghai。没有人工转交/接收事实时调度仅待转交，不据卡文件存在标执行中。

## 背景与最小充分输入

125工具及126 review-01代码门已验收结束，F126-01显式loopback hostaddr与F126-02物理长路径保护已关闭。合法容器NAT语义、原SQL/职责组与提交未知禁止重放的结论继续有效。已有18方法与新9方法按实际影响复用，不称最终21全量重跑。真实PG/ACL/正常启动尚无本卡证据。

按顺序只补读当前缺失内容。

1. 根入口、上述公共AGENTS、执行所需WORK条款和本卡全文。原窗口同版本未变规则不反复通读。
2. 本项目执行动态v2.98顶部、架构v1.70顶部；上述采用回执/范围/输入清单/permit。原采用包阅读全文一次，尤其精确资源与低内存条款。
3. deploy/initialize_normal.py、deploy/normal_install_manifest.json、config/normal-install.example.json、deploy/normal-install.md及README安装段。原始001—015按固定清单读实际实施所需内容，不改写SQL或guard。
4. TASK126-result.md置顶review-01和首轮“后续最小真实验证清单”、两work-decision及TASK125实际必要证据；只复用已核代码/离线范围，不重新开展审计。无需实现聊天或思考记录。
5. 原生deploy/compose.local.yml、deploy/start_local.py、backend/app/data_exit/config.py、control.py、files.py、repository.py、schema.py、schema_checks.py、schema_profiles.py、q_roles.py，以及app/main.py、runtime.py、service_config.py、q_readiness.py和对应关闭配置模板。已有直接依赖指纹逐项见input-manifest.json，不全仓重读。

全部相对路径以真实项目根为准，产物路径须绝对记录。输入不可访问先报告具体缺失并继续不受影响部分。读入/开始/结束核冻结清单。安装器冻结29403字节，SHA256=68d7b71fc7296111e894df4cba21a4ed7830f9cff069c1fc500dfbd7734c0a09；固定安装清单SHA256=f2ed126daa1c5a982b490a9343d6c17053c0f385e7a2f55676ecf4132dd2abf0。其余以本卡input-manifest的逐项原字节hash为准；未知漂移先查归属，不覆盖用户成果。

## 允许写入、禁止范围与自主决定

允许编写本卡execution内验证控制器/用例/观察包装器及原始输出、写本卡结果；只在下述两新私有根创建实际安装/原生配置、根绑定和本地收据。需要用户说明同步时，完成真实验证后才最小更新README.md与deploy/normal-install.md，保存pre/post、diff、依据和未验证限制。其他产品文件一律只读冻结，尤其安装器、001—015、角色/profile/Grant、全部backend业务、原启动器与正式Compose；不修改依赖锁、公共库、正式DocuS、旧卡/报告/证据或用户原始需求。

可自主安排六项内部顺序、普通夹具实现与有据修正、只读观察方式和最小正常配置字段，须始终使用原生接口。验证辅助层不能成为产品运行依赖；启动/安装实际走正式入口，不能套旧TESTONLY runner、旧授权/凭据/角色修改或既有合成库。不引入平台、依赖、下载、构建、浏览器、renderer、真实业务Job、网络模型/Embedding/计量或Git写操作。

Q维持FROZEN，T0/72h为空；没有账号/token/模板/Embedding容量外部事实新增，不变更两provider，不创造grant或QAuthority.bind/InstanceBinding，不建立三固定业务活动、索引、查询、生成或付费账。原100次25元及48/28/24分额保持，真实调用与费用0。外部缺口不妨碍本卡关闭外发的正常安装验证，但本卡通过也不替代启用门。

## 精确资源及身份绑定

只用本机已缓存pgvector/pgvector@sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f，PG17、vector0.8.6。预检实际不符则带回差异；不能拉镜像、构建、升级或换资源试跑。

两个槽位串行，最多一个PG活跃。

- source容器retrolume-q-first-normal，卷retrolume-q-first-normal-data，数据库retrolume_q_first_normal，Compose项目retrolume-first-install-source；PG候选端口按55482、55484、55486顺序。
- interrupted容器retrolume-install-interrupted，卷retrolume-install-interrupted-data，数据库retrolume_install_interrupted，Compose项目retrolume-first-install-interrupted；PG候选按55483、55485、55487顺序。它只保留部分安装事实，绝不切为正常源。
- 本机API候选按18122、18124、18126顺序。先只读查归属和短时bind探可用，每槽位/用途一次选定并写身份账；后续失败不换端口绕计数。全不可用则停相应段，不改Windows排除范围、网络服务或他人进程。

每槽位最多一次容器创建尝试、一个新专有卷；最多两个对应Compose bridge网络。若指定名字已有非本次对象或归属不明即停槽位，不删除/接管/换名。创建后同卡恢复仅复用已记录完全相同的对象，不再次create。使用正式compose.local.yml的pg服务和固定-p项目，CPU1、内存512MiB、pids128、restart=no、127.0.0.1映射、无host网络/host bind、pull never。不要执行整栈up或renderer-build profile。Compose插值需要的未激活renderer变量仅填明确无副作用的本机占位；不加载旧私有预览配置。

新私有根仅D:/shspic/project_NO3_RetroLume-agent/.runtime/normal-first-install/source和D:/shspic/project_NO3_RetroLume-agent/.runtime/normal-first-install/interrupted。新任务首次创建前根须不存在，检查父链reparse/物理边界；同卡后续只复用自己身份记录的根。source内data、backup、control、restore四根独立，另置私有配置/收据。interrupted使用自己的对应根/安装身份。不得重叠、越界、转向旧TESTONLY路径。已有.gitignore的/.runtime/排除保持，不将私有配置或连接串放入证据。

创建前登记批准的槽位计划，创建后在第一次使用或后续写入前记录实际CID、镜像实际ID、卷/网络创建身份、选定端口、DB名/OID/system_identifier、PG/vector版本、当前Windows SID及根device/file-id和权属。不伪造预知CID/OID；三个安装UUID从新受信根/来源绑定一次确定并记录，控制行、配置、ControlHub一致，不把Q identity当普通安装身份。容器名、路径或端口都不能单独代替不可混淆身份核验。

只对两个新隔离集群配置短时bootstrap管理员。source新登录retrolume_normal_app、retrolume_normal_snapshot；interrupted预定retrolume_interrupt_app、retrolume_interrupt_snapshot。13个NOLOGIN职责组由原001—015产生，权限保持已审分工。禁止修改旧集群角色或重置任何已存在角色密码。生成彼此分离的16—1024字节随机秘密，按正式环境引用经安全stdin/子进程环境注入；不在argv、JSON、终端、异常、证据、报告或Git中放真实值，应用绝不继承安装管理员DSN。

Docker inspect用完整JSON在内存取必要白名单字段，日志只存脱敏投影；不打印Env、完整展开Compose或含密码连接串。不再套旧HostConfig.Mounts的14字段格式模板或旧白名单。子进程从明确最小环境构造，清除旧TESTONLY/preview/Q/provider及无关PG环境，loopback与正式显式hostaddr保护保持。不用清理宿主全局环境或绕连接核验。Windows async走原生启动器已有兼容loop_factory，不在新控制器猜用默认Proactor。

## 一次卡内六项真实检查

先离线读清入口与配置，准备完整控制器、身份核验、串行状态/预算/压力退出、原始日志及阶段检查点，再打开真实资源。控制器检查点只记录本卡事实，不造新迁移账本或平台。证据保存失败及时停相应操作，不能丢失失败后接着假称可重放。

1. 空库预检拒绝的辨别力。

同一source新空库，对错误DB OID、错误system_identifier分别用独立本地配置/拒绝收据，真实调用原apply并核确切原因及无安装器写入；合法NAT服务端地址/端口可与客户端loopback映射不同。另建精确public.retrolume_install_probe_nonempty表和retrolume_data_app NOLOGIN碰撞组来分别命中非空/职责组碰撞。先证原本不存在、记录本卡创建OID；只可按完整限定名及相同OID撤销这两个本卡对象，使source回到已核空态。该两对象的精确DROP TABLE/ROLE已随采用包获准，不允许循环/通配清库或触碰其他对象。碰撞组不能与正式安装后的同名职责组混淆，成功安装后不再清理它。每次反例独立观察，关闭旁观连接，不能都被other_clients挡住便标通过。

2. source原SQL完整真实安装。

用真实受信根/实际目标写启用安装配置，runtime_configs四项仍null。实际调用deploy/initialize_normal.py apply --config 私有绝对路径 --receipt 新私有收据。001—015逐份按原文/原事务执行，观察013后的normal/R01控制行、014/R02、015/R03，原schema_checks与q_roles通过；37条成功收据的17个submitted/confirmed及最终complete均实际对应。仅可包观察连接/提交边界来读取真实阶段，不能Recorder代替驱动、改SQL、删guard或patch验证函数。记录真实连向127.0.0.1、精确库/身份与允许的容器NAT。无业务伪造数据，不调用旧initialize-materials.py，不在重开/复验时重放已成功DDL。

3. 实际两个登录与权限。

分别用新业务和快照登录建立真实连接。复用原ROLE_CAPABILITIES/MEMBERSHIPS和原校验，再实际读取必要最小控制/只读事实。查询直接和传递SET/INHERIT/ADMIN、owner和管理标志；快照不得业务写、读maintenance秘密或SET业务/owner，业务不得超级/建角色/建库/复制/bypassrls或经传递路径取得owner/管理能力。可作少量有界回滚拒绝事务或等价真实权限查询，不扩建旧安全全套，不为了测试制造持久业务记录。记录是否确实由对应login执行，管理员观察不冒充登录能力。

4. 原生关闭配置正常启动、停止、同库重开。

用正式normal loader和data_exit结构建立新source与ControlHub真实绑定。data_exit在原loader需要时可启用正常源配置，但model/integration/Q/preview必须原生失败关闭；不要虚构模板不支持的enabled字段，也不启用只读恢复选择/新restore目标。factory不用则按真实loader允许的关闭形态，不引用旧目标或创建第三槽位。保持新业务DSN、快照引用、maintenance引用各自用途；四根/SID/file-id/控制行身份一致。

真正执行deploy/start_local.py --container retrolume-q-first-normal --port 已选API端口 --shutdown-stdin，接口参数以实读入口为准。读取实际本机capabilities/readiness与必要正常源状态，确认外发关闭、连接使用新业务login、没有安装管理员或旧源回退。预期Q readiness可能因既存外部门关闭，须区分“关闭符合预期”与本地schema/来源不可用，不能把任何503都算通过。无需页面、浏览器、活动或provider。

通过当前stdin拥有链正常关闭，核API树/端口结束；由精确归属停止source。随后同一CID/DB OID/systemid/四根/三个UUID/控制身份原生重开一次，再读同一状态，核没有自动迁移、换实例、重置或新增业务记录，正常停止。API进程、PG是否由launcher启动分别记归属；launcher不停止外层已启动PG时由本卡控制器按CID收尾，不伪称已停。不要为单次GET另开服务。

5. 独立interrupted真实提交未知保留。

source停后才启动interrupted。事前固定唯一注入在原002迁移已经由真实驱动执行、全部结果耗尽且COMMIT成功之后，隐藏一次提交确认。使用测试连接包装器即可，生产代码和SQL不改；只注入这一处，严禁跳过真实COMMIT或用记录器模拟。观察001已confirmed、002仅submitted/unknown、无003/complete/自动重放；用独立连接只读验证002实际提交事实并关闭。测试预定未知不是产品安装成功。

同一部分收据再次apply与verify须本地拒绝；一个新收据对这个部分库须真实预检拒绝且零新安装写入。不得自动继续003、补签确认、换库/名、清卷、退款或重建槽位。保留部分数据库/卷与原始收据。第五项这一次预定注入属于验收场景，允许观察/拒绝/收尾；其他非预期未知提交均按停止门处理，不能用本项豁免反复重试。

6. 回到source只读verify。

interrupted停后回source同一成功库，用原完整成功收据执行正式verify --config 与 --receipt；子进程仅注入管理员密码引用，不提供另三份秘密及业务/快照DSN。观察真实READ ONLY、schema/roles/身份和收据原字节不变；无DDL/DCL/业务写。另一个错误收据绑定输入在连接前拒绝，连接记录器仅可观察拒绝前连接数为0，不替代正常verify的真实连接。对成功收据前后hash及实际DB事实交叉核验。完成后精确停止source。

## 工具、日历与资源预算

本卡总工具wall最多10800秒，其中预留900秒保存/清场；日历24h按本卡签发起算，permit同值。工具投入不能只报测试秒数，非并行持有和父/子重叠分层记，不重复累加但不能漏掉筹备/夹具修正。精确不可得即标unknown并记录可证下界/保守占用，不编数字。

PG累计实际持有最多1800秒，API累计最多900秒。source PG start最多4次，interrupted最多2次，API start最多3次；所有尝试均留账。正常中间步骤不增加单方法根额度，文件读取、未执行审批拦截不算实际启动。最多一个合并初验入口加两次有原始依据、只接失败/未完成段的定向续验，共3入口；入口/准备失败仍记账，不重置历史。不要因控制器重开重复完整成功安装或六项全跑。

每次Docker已可用后，启动PG或API前可用物理内存至少512MiB；全程约2秒采样，连续两次低于256MiB就停止新增动作，并在已有归属下有界停本任务API/PG保存事实。此为本次明确采用的低内存串行门，不重复要求2GiB，不让用户反复释放内存。最多一个PG和一个API，无浏览器/renderer；空闲或离线修夹具期间停止数据库，避免耗尽持有预算。

所有子命令有界并可保持用户更新。等待服务ready/停止要用已知真实机制，原生关闭应预留其150秒优雅退出及父等待/终止的已有上界，不能自造更短停止超时导致误杀成功进程。启动前剩余预算须覆盖本段、失败保存和清场。总上限/日历到门只做必要自有收尾；未用预算在交回后封存，不自行跨日历恢复。

平台权限仍适用。审批未执行、容量或工具阻断只记精确动作和未执行事实，不能改shell/拆命令/换客户端绕过；先完成不依赖该动作的工作。既定许可已覆盖本卡对象时无需重复让用户批普通步骤。

## 复用、原始证据与审计关系

126已完成安装器/原SQL/权限边界的必需独立审计，两发现也独立关闭。新卡代码冻结，完成后主控核六项动态原件，不默认再派同源码全量独审。若确有新产品/安全差异则停相应部分，保留稳定范围，交主控判断必要增量审计；本工程自查不冒充独立审计。原有限代码通过不能代替本卡真实结果。

execution内最少留以下实际材料，可按阶段合并而非重复复制。

- 接收/当前规则和原输入核验、pre/post hash与允许文档diff；实际安装器/迁移/配置结构/包装器运行前后hash，验证辅助代码的实际as-run副本或不可变清单。
- 脱敏资源身份账、根实体身份/归属及端口选定依据、每次start/stop和PG/API持有区间、实际命令结构/退出码/时间、压力采样/退出。
- 六项逐条件事实到原始输出/收据的导航，真实DB错误码和固定拒绝原因，R01/R02/R03、37条完整源收据与中断未知收据的无敏感证据引用。原始收据含仅非敏感元数据时可在execution放一份副本并与私有原件hash绑定；不复制任何秘密或私有DSN。
- 跨重启身份/数据/收据比较、实际两个登录能力、verify只读与拒绝前连接数、原生两个API周期/关闭状态、原始全部失败及夹具修正依据/diff/复验选择。
- 真实provider/费用0、Q冻结及T0为空的配置/调用边界依据；不能用一个自报0代替整机零调用证明，也不扩大到全平台声明。
- 最终停止核验只读投影，精确CID Running=false/Pid=0、API自有PID/树不活跃与选定端口释放；失败卷/库保留事实，未掌握的宿主其他资源不宣称已清空。

持久容器/卷/网络及成功/失败库全部保留。只允许按本卡不可混淆身份停止自有PG和API树；不docker prune、compose down -v、DROP DATABASE、批量/递归删除、清理旧scratch或旧资料。不要删除主控采用包、原证据和失败原件。

## 停止、回传与必要人工

完成六项即停，不追加“更放心”的全套测试。普通夹具故障先按实际报错定界，可在本卡范围/预算内有据修正并只补受影响未完成段；同根因两次有据修正仍失败、根因不稳、需要扩大权限/改产品或SQL/增加槽位/依赖/新平台时停止受影响段，继续不受阻项并一次回传。source出现非预期未知提交立即停这个安装，不凭DB已提交事实补签成功或续装。第五项既定一次注入按上述特殊验收收尾。

报告先给一句真实结论、完成/未完成、实际差异及作用和六项原始证据导航，再列TASK127/R121/STEP关系、真实客户端/模型、接收与截止、对象配置/身份、检查预期与实际、继承范围、失败与修正、工具/持有/启动/入口全部累计账、风险/偏差/停止依据。明确区分本机安装事实与仍未核Q外部条件。

后续同边界补证沿用本TASK/R及结果置顶新轮，旧正文/失败保留；执行者不填主控最终验收，不改共享编号、架构/执行动态或公共库。不凭完成安装声明实际付费或整个NO3完成。需同步README/安装说明与DocuS的事实逐文件给主控，历史限制不抹除。

当前必要用户动作仅人工把本卡交给原125工程窗口，完成带回结果路径；不要求密钥、账单、截图、手工建库、释放内存或删对象。真实关键缺口才集中指出最少问题。保存D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-127-result.md并确认可读后，只回复一句结论与可点击绝对路径。
'''.replace('@ISSUED@', stamp).replace('@DEADLINE@', deadline)
    assert '*' not in task and '\n|' not in task
    for must in ['六项真实', 'R-121', '10800', '1800', '900', '512MiB', '256MiB', '37条', 'FROZEN', '同一部分收据', 'receipt', '冻结']:
        assert must in task, must
    # 编号先在唯一总账登记，再保存完整卡，最后更为待转交。
    registered = f'''# 执行动态文档\n\n文档v2.98，2026-10-22，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.70、task_model/07。以下v2.97原字节保留。\n\n## TASK127/R121已登记，完整卡保存核读中\n\n{stamp}。用户原话“确认”采用AP-125-NORMAL-INSTALL-01，已在唯一总账占TASK127/R121；完整卡保存核读后再改待转交，未发生转交、接收或开始。\n\n## 以下为v2.97及更早历史\n\n'''.encode('utf-8')
    STATE.write_bytes(registered + state_old)
    with CARD.open('xb') as stream:
        stream.write(task.encode('utf-8'))
    assert CARD.read_text(encoding='utf-8') == task
    permit = {
        'TASK': 'TASK-127', 'R': 'R-121', 'issued_at': stamp, 'valid_until': deadline,
        'task_card': describe(CARD), 'input_manifest': describe(OUT / 'input-manifest.json'),
        'adopted_scope': describe(OUT / 'adopted-scope.json'),
        'receiver': 'A+，原TASK125工程窗口；人工转卡', 'status': '待人工转交',
        'actual_dispatch': False, 'acceptance': None,
        'budgets': {'tool_wall_seconds': 10800, 'reserved_save_cleanup_seconds': 900,
                    'pg_holding_seconds': 1800, 'api_holding_seconds': 900,
                    'source_pg_starts': 4, 'interrupted_pg_starts': 2, 'api_starts': 3,
                    'combined_entries': 3, 'container_create_attempts_per_slot': 1,
                    'container_cap': 2, 'volume_cap': 2, 'compose_network_cap': 2,
                    'fees_cny': 0, 'real_provider': 0},
        'used_at_issue': {'real_entries': 0, 'pg_starts': 0, 'api_starts': 0,
                          'containers_created': 0, 'provider': 0, 'fees_cny': 0},
        'historical_budgets_reset': False, 'products_mutable': False,
        'Q': 'FROZEN', 'T0': None, 'expected_single_commit_unknown': 'interrupted/002',
        'unobserved_runtime_identities': True, 'platform_permissions_still_apply': True,
    }
    save_json(OUT / 'permit.json', permit)
    arch_prefix = f'''# 架构动态文档

文档v1.70，2026-10-22，Asia/Shanghai。需求v1.4、执行动态v2.98、task_model/07。以下v1.69原字节保留。

## 关闭外发的真实首次安装采用包已生效，部署事实待验证

{stamp}。用户原话“确认”采用AP-125-NORMAL-INSTALL-01，授权既有已审安装器/原001—015在两个新隔离PG槽位上完成原六项真实检查，现登记TASK127/R121。source未来正常源与interrupted仅中断保留分开，固定Compose服务/缓存镜像/每槽位独立卷、最多一PG活跃、原生关闭配置启动/同库重开/停止，真实角色权限和提交未知不重放均须实际取证。

本次只落实原架构安装验证，不新增业务模型、权限分工、接口或平台。低内存512MiB启动/256MiB连续两次压力退出门限为本包明确采用，普通2GiB与旧卡许可不混用。已通过126的未变安装器及离线范围继承，不重新全审；新产品风险/差异仍须对应停止与审查。主控没有启动资源，真实CID/OID/根绑定尚未观察，不把采用或出卡写成已部署/通过。

Q冻结、T0/72h空、provider/费用0，外部计量/账号/版本模板/Embedding容量与首次启用门不变；关闭式本机安装独立推进并不消除这些门。STEP018部分验证，019/020/M1/项目/发布未放行。

## 以下为v1.69及更早历史

'''.encode('utf-8')
    ARCH.write_bytes(arch_prefix + arch_old)
    state_prefix = f'''# 执行动态文档

文档v2.98，2026-10-22，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.70、task_model/07。以下v2.97原字节保留。

## 用户已采用关闭式真实安装包，TASK127/R121完整卡待人工转交

{stamp}。用户原话“确认”对应AP-125-NORMAL-INSTALL-01合并操作包，采用回执、active scope、输入/许可保存在DocuN/evidence/TASK-127/orchestration-20261022/；原草案原字节及采用前未授权历史照留。主控已登记TASK127/R121、保存并核读完整卡DocuN/tasks/TASK-127.md，调度待转交、验收留空，没有真实转交/接收/开始或在途证据。接收A+原TASK125工程窗口，不交原126独审执行。

目标是一个完整真实验证成果，原六项含空库拒绝反例、原001—015及37条成功收据、真实角色权限、原生关闭启动/同库重开/停止、独立002真实COMMIT后一次未知保留、仅管理员秘密的只读verify。两个精确PG/卷/Compose项目及私有根按已采用包限定，最多一PG和一API串行；旧资源/用户数据不动，成功/失败卷保留。当前只是目标计划，实际CID/systemid/OID/Windows根实体身份均由执行者创建后如实绑定，主控本轮未作实时Docker/端口/内存探针或产品运行。

新卡工具10800秒含900保存/清场，日历至{deadline}；PG持有1800秒/API900秒，source start≤4/interrupted≤2/API≤3，至多初验及两次有据未完成段续验；每槽位一次create/一个卷、网络≤2，低内存512MiB启动和256MiB连续两次自动退出。资源实际用量尚未发生于本卡，不能据主控无运行推断宿主无残留。平台审批继续适用，未执行拦截如实记，不能绕限。第五项预定一次未知与其他非预期未知停止规则明确区分。

125/R119和126/R120已通过的有限工程/审计结束保持，未变18/9离线方法和原独审结论按范围继承，旧保守4200/10800/3批和2400/3600/精确unknown及未用额度封存。旧120根64/64/149与117旧81等全部失败/投入不重置。本卡不修改已审产品或SQL，只准备/执行验证，必要README与安装说明按真实事实最小更新；稳定旧代码不再机械全审，实际新安全差异才决定增量审查。

Q继续FROZEN、T0/72h空、真实provider/费用0；100/25与48/28/24、28Must/89动作/24片6索引不变。外部计量/账号/token/模板/Embedding容量和首次启用门仍未齐。STEP018进行中/部分验证，019/020/M1/项目/发布未验。下一动作由用户转交本卡，工程一次连续交付六项或明确停止事实；不再按普通子步拆卡。CHG1659—1662，下一1663。

## 以下为v2.97及更早历史

'''.encode('utf-8')
    STATE.write_bytes(state_prefix + state_old)
    changes = f'''
- CHG-1659，{stamp}，Codex编排Agent，DocuN/tasks/TASK-127.md。按用户确认的AP-125-NORMAL-INSTALL-01登记TASK127/R121并保存完整六项真实验证合同，A+原125工程窗口待人工转交，付费与Q关闭。

- CHG-1660，{stamp}，Codex编排Agent，DocuS/架构动态文档.MD。v1.70登记关闭式真实安装采用范围和待验证边界，沿用原SQL/角色/原生启动及已审代码，不冒部署事实。

- CHG-1661，{stamp}，Codex编排Agent，DocuS/执行动态文档.MD。v2.98登记采用依据、新卡待转交、精确资源/低内存/预算、旧账封存和剩余Q门，保留v2.97全部原字节。

- CHG-1662，{stamp}，Codex编排Agent，DocuN/evidence/TASK-127/orchestration-20261022/。保存采用回执、原草案身份、实际输入冻结、新scope/24h许可、旧共享快照与保存读回，主控产品运行0，原草案/产品未改。
'''.encode('utf-8')
    CHANGE.write_bytes(change_old + changes)
    assert STATE.read_bytes().endswith(state_old)
    assert ARCH.read_bytes().endswith(arch_old)
    assert CHANGE.read_bytes().startswith(change_old)
    assert proposal.read_bytes() and digest(proposal.read_bytes()) == approval['proposal']['sha256']
    assert digest(draft_path.read_bytes()) == approval['draft_scope']['sha256']
    for entry in sources:
        assert digest((ROOT / entry['path']).read_bytes()) == entry['sha256'], entry['path']
    assert STATE.read_text(encoding='utf-8').startswith(state_prefix.decode('utf-8'))
    for path in [CARD, STATE, ARCH, CHANGE, OUT / 'adoption-receipt.json', OUT / 'adopted-scope.json', OUT / 'input-manifest.json', OUT / 'permit.json']:
        assert path.read_text(encoding='utf-8')
    proof = {
        'saved_at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
        'TASK': 'TASK-127', 'R': 'R-121', 'status': '待人工转交', 'acceptance': None,
        'files': [describe(path) for path in [CARD, STATE, ARCH, CHANGE, OUT / 'adoption-receipt.json', OUT / 'adopted-scope.json', OUT / 'input-manifest.json', OUT / 'permit.json']],
        'checked_product_files': len(sources), 'product_drift': 0, 'rules_checked': len(rules),
        'old_proposal_draft_bytes_preserved': True, 'old_shared_bytes_preserved': True,
        'task_registered_before_card_written': True, 'card_complete_utf8_readback': True,
        'product_runtime': 0, 'product_import': 0, 'test_runs': 0,
        'resource_probes': 0, 'new_runtime_resources': 0,
        'calendar_expiry': deadline, 'next_CHG': 1663,
    }
    save_json(OUT / 'save-proof.json', proof)
    print(json.dumps({'saved': True, 'TASK': 'TASK-127', 'R': 'R-121',
                      'card_bytes': CARD.stat().st_size, 'card_sha256': digest(CARD.read_bytes()),
                      'product_files_checked': len(sources), 'product_drift': 0,
                      'valid_until': deadline, 'status': '待人工转交'}, ensure_ascii=True))


if __name__ == '__main__':
    main()
