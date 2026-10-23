"""核收独审并合并剩余功能验证合同；不执行产品、资源或测试。"""
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
PUBLIC = Path('D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4')
OUT = ROOT / 'DocuN/evidence/TASK-128/orchestration-continuation02-20261023'
AUDIT = ROOT / 'DocuN/evidence/TASK-129/audit'
AORCH = ROOT / 'DocuN/evidence/TASK-129/orchestration-20261023'
PREV = ROOT / 'DocuN/evidence/TASK-128/orchestration-continuation01-20261023'
E1 = ROOT / 'DocuN/evidence/TASK-128/execution/continuation-01'
CARD = ROOT / 'DocuN/tasks/TASK-128.md'
DEC128 = ROOT / 'DocuN/results/TASK-128-work-decision.md'
DEC129 = ROOT / 'DocuN/results/TASK-129-work-decision.md'
STATE = ROOT / 'DocuS/执行动态文档.MD'
ARCH = ROOT / 'DocuS/架构动态文档.MD'
CHANGE = ROOT / 'DocuS/文档变更记录.MD'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def js(path):
    return json.loads(path.read_bytes())


def item(path):
    raw = path.read_bytes()
    return {'path': path.as_posix(), 'bytes': len(raw), 'sha256': sha(raw)}


def save_json(path, value):
    raw = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    with path.open('xb') as output:
        output.write(raw)
    assert path.read_bytes() == raw


def main():
    for path in (OUT, CARD, DEC128, DEC129, STATE, ARCH, CHANGE):
        for parent in [path, *path.parents]:
            if parent.exists():
                stat = parent.lstat()
                assert not parent.is_symlink() and not getattr(stat, 'st_file_attributes', 0) & 0x400, str(parent)
            if parent == ROOT:
                break
        else:
            raise RuntimeError('输出越界')
    assert not DEC129.exists() and not (OUT / 'permit.json').exists(), '已有接续登记，先核断点'
    old_state, old_arch, old_change = STATE.read_bytes(), ARCH.read_bytes(), CHANGE.read_bytes()
    old_card, old_dec128 = CARD.read_bytes(), DEC128.read_bytes()
    assert '文档v3.01' in old_state.decode('utf-8-sig').splitlines()[2]
    assert '文档v1.73' in old_arch.decode('utf-8-sig').splitlines()[2]
    assert 'CHG-1677' in old_change.decode('utf-8-sig')[-1700:] and 'CHG-1678' not in old_change.decode('utf-8-sig')
    now = datetime.now(timezone(timedelta(hours=8)))
    stamp = now.isoformat()
    deadline = js(PREV / 'permit.json')['valid_until']
    assert now < datetime.fromisoformat(deadline), '旧日历已到期，不暗中延长'
    ap = js(AORCH / 'permit.json')
    manifest = js(AORCH / 'input-manifest.json')
    raw_index = js(AORCH / 'raw-evidence-index.json')
    checks = []

    def verify(path, expected, size=None, category='input'):
        path = Path(path)
        row = item(path)
        assert row['sha256'] == expected, str(path)
        if size is not None:
            assert row['bytes'] == size, str(path)
        checks.append({**row, 'category': category, 'match': True})

    for key in ('task_card', 'input_manifest', 'raw_evidence_index'):
        ref = ap[key]
        verify(ref['path'], ref['sha256'], ref['bytes'], 'audit_permit_binding')
    for row in manifest['products'] + manifest['before_sources'] + manifest['original_contracts'] + raw_index['sources']:
        verify(row['path'], row['sha256'], row['bytes'])
    closure = js(AUDIT / 'closure.json')
    audit_report = item(ROOT / 'DocuN/results/TASK-129-result.md')
    assert audit_report['sha256'] == closure['result']['sha256'] == 'a95f3ac087dcafbf9d74c0e6aa36961d3fcb67e18d77854dc046a16aa1bc39db'
    assert audit_report['bytes'] == closure['result']['bytes'] == 25406
    assert all(closure['checks'].values())
    assert closure['conclusions']['functional_security_new_defects'] == []
    assert closure['conclusions']['dynamic_remainder'] == [4, 5, 6]
    static = js(AUDIT / 'static-crosschecks-02.json')
    assert all(row['satisfied'] for row in static['checks'])
    audit_objects = []
    for path in sorted(AUDIT.iterdir()):
        if path.is_file():
            audit_objects.append(item(path))
    rules = js(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
    for row in rules:
        verify(PUBLIC / row['relative_path'].replace('\\', '/'), row['sha256'], category='locked_rule')
    checkpoint = js(E1 / 'checkpoint.json')
    assert checkpoint['entries'] == 6 and checkpoint['slots']['source']['starts'] == 4
    assert checkpoint['slots']['interrupted']['starts'] == 1 and checkpoint['api_starts'] == 0
    r128 = item(ROOT / 'DocuN/results/TASK-128-result.md')
    assert r128['sha256'] == '472882152a5283bf0ff36d72ff1b73b7a9822e1cfff4dda5c0afa942950efc55'
    success = E1 / 'entry-06/source-success-receipt.jsonl'
    assert sha(success.read_bytes()) == 'a2211aa56f0497ef55e2ff42f4ea2e6b3b50bb3049cca62cbd5ef06844df6f06'
    OUT.mkdir(parents=True, exist_ok=True)
    before = OUT / 'before'
    before.mkdir(exist_ok=False)
    for path, raw in [(STATE, old_state), (ARCH, old_arch), (CHANGE, old_change), (CARD, old_card), (DEC128, old_dec128)]:
        (before / path.name).write_bytes(raw)
    verification = {'checked_at': stamp, 'TASK129': 'R-123', 'audit_report': audit_report,
                    'identity_reference_checks': len(checks), 'mismatches': 0, 'checks': checks,
                    'audit_artifacts': audit_objects, 'accepted_code_scope': ['connect', 'observe_identity'],
                    'accepted_dynamic_scope': [1, 2, 3], 'dynamic_not_run': [4, 5, 6],
                    'P3': {'id': 'F129-01', 'status': 'DEFERRED_NONBLOCKING', 'reason': '用户明确要求不处理不影响功能的细节'},
                    'orchestrator_runtime': 0, 'orchestrator_live_resource_probe': 0}
    save_json(OUT / 'acceptance-check.json', verification)
    dec129 = f'''# TASK-129 / R-123 主控验收

{stamp}，Asia/Shanghai。用户带回独立报告并要求加快收口、不处理不影响功能的细节。主控核{len(checks)}条引用零漂移，报告25406字节/hasha95f3ac087dcafbf9d74c0e6aa36961d3fcb67e18d77854dc046a16aa1bc39db，实际独立差异/127输入身份及81项静态原件可核；不重跑产品。

验收通过，审计任务结束，未用保守1500/2400余量封存。接受connect服务隔离及observe_identity完整主机格式当前代码门、前三项真实证据的限定结论；其余四/五/六仍未验证，不签128、STEP019、Q或项目通过。元数据仅读hash暴露和初次分析失败已披露，保留原件，不据此重复审查。

F129-01是两行英文注释P3，按用户明确要求登记非阻断暂缓，不开修复卡、不改产品hash、不追加功能测试或审计。旧非阻断观察亦不升级为新硬门。

后续相同代码仅补后三项动态并核原件；没有新安全变更不重新审两函数或旧SQL/角色。真实启动权限由128续作02集中给出，不由审计交付自动恢复。Q冻结、T0空、费用0。
'''
    DEC129.write_text(dec129, encoding='utf-8', newline='\n')
    dec128 = f'''# TASK-128 / R-122 续作02集中收尾决定

{stamp}，Asia/Shanghai。129独审已验收结束，接受两函数代码及前三项真实证据；前三项不再重跑，成功source及37行收据不得重放/重建。任务128仍部分通过，余4/5/6待真实运行。P3注释按用户要求暂缓，不成为工作项。

同号128续作02恢复原采用包未用2400工具秒，含900保存/清场，连续保守8400/10800/精确unknown及全部失败不重置；原截止{deadline}不延。主控把同资源source cap5前向7（当前4，覆盖两必需启动及一个有据余量），interrupted cap2前向3（当前1，实际002注入仍仅一次），API cap3保持（当前0）；entry07为本次完整主批，entry08仅一次有据未完成段备用，累计cap7前向8。所有新create/卷/网络仍0，总工具/持有/费用不加。

启动次数只作为明确边界，不再按每个查询拆根；全部已完成事实直接继承。新控制器先离线核路径/许可和完整余段，串行独立中断保护、成功source的verify及两原生API周期；正常顺序可按独立性调整，不削弱两个API跨真实PG停/开。停止/启动间允许最多90秒等待内存恢复达到既有512MiB门，全部计时/持有照计，不能把瞬时波动立即变成新卡，也不降低运行压力两次256门。

若本机持续达不到最小运行容量，先收可独立完成项并统一交明确环境缺口，不机械加同样试跑、不反复索要释放内存。代码冻结，P3不修；无新功能/安全风险不另派审计。Q保持冻结、provider/费用0。本决定只支持既有正常部署余项，不宣整个项目已完工。

以下保留续作01及首轮主控裁定原字节。

'''.encode('utf-8')
    DEC128.write_bytes(dec128 + old_dec128)
    scope = {'TASK': 'TASK-128', 'R': 'R-122', 'round': '续作02', 'issued_at': stamp, 'valid_until': deadline,
             'approval_basis': 'AP-125-NORMAL-INSTALL-01及用户加快功能收口要求；主控同资源前向调度',
             'used': {'tool_conservative_seconds': 8400, 'tool_exact_seconds': None, 'entries': 6,
                      'source_starts': 4, 'interrupted_starts': 1, 'api_starts': 0,
                      'pg_holding_seconds': 34.1386296749115, 'api_holding_seconds': 0},
             'caps': {'tool_total_seconds': 10800, 'restored_seconds': 2400, 'save_cleanup_reserve': 900,
                      'entries': 8, 'source_starts': 7, 'interrupted_starts': 3, 'api_starts': 3,
                      'pg_holding_seconds': 1800, 'api_holding_seconds': 900,
                      'new_container': 0, 'new_volume': 0, 'new_network': 0},
             'memory': {'startup_min_mib': 512, 'runtime_floor_mib': 256, 'floor_samples': 2,
                        'sample_seconds': 2, 'max_capacity_wait_seconds_per_phase': 90},
             'identity_checkpoint': item(E1 / 'checkpoint.json'), 'source_success_receipt': item(success),
             'objects': checkpoint['slots'], 'product_code_frozen': True, 'P3_deferred': True,
             'already_accepted_checks': [1, 2, 3], 'remaining_checks': [4, 5, 6],
             'Q': 'FROZEN', 'T0': None, 'provider': 0, 'fees_cny': 0}
    save_json(OUT / 'scope.json', scope)
    input_manifest = {'TASK': 'TASK-128', 'R': 'R-122', 'round': '续作02', 'issued_at': stamp,
                      'products': manifest['products'], 'root_entry': item(ROOT / 'AGENTS.md'),
                      'rules': manifest['rules'], 'scope': item(OUT / 'scope.json'),
                      'audit_result': audit_report, 'audit_closure': item(AUDIT / 'closure.json'),
                      'checkpoint': item(E1 / 'checkpoint.json'), 'source_receipt': item(success),
                      'result128': r128, 'old_contract': item(before / CARD.name),
                      'helper_baseline': [item(E1 / name) for name in ('run-six.py', 'install-observer.py', 'win-support.py')]}
    save_json(OUT / 'input-manifest.json', input_manifest)
    contract = '''# TASK-128 / R-122 续作02 剩余三项功能验证集中收口

本段为当前有效完整合同，后文旧卡原字节保留为历史，不叠加已封存许可。原前三项及两产品修复已获独立审查采纳，本轮只补4/5/6；不处理非阻断P3注释、不重装、不重跑旧测试、不新开设计/研究卡。

## 接收、目标和产物

接收A+，继续刚完成128续作01的原125/127/128工程窗口，不使用129独审窗口。真实模型/客户端如实登记，不开并行Agent。复杂性在原生生命期、真实提交未知和安全配置，不能为省步骤降低身份/权限检查。

一次卡内完成原生API两周期及真实PG停/开、中断槽位002提交后唯一丢确认、成功收据只读verify，全部原始证据和精确停止一次交回。真实未跑保持未验证；工程不自签主控最终验收/项目/Q。新辅助/输出只写D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-02/；结果在D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-128-result.md置顶续作02并保当前25623字节完整后缀。

## 项目、规则和依据

项目根D:/shspic/project_NO3_RetroLume-agent，入口该根AGENTS.md；task_model V4.0、公共AGENTS CHG-0003。公共根D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4；读其DocuS/AGENTS.MD及必要WORK执行/停止条款，同窗同版未变内容复用。锁定指纹为项目DocuN/evidence/v4-migration-20260930/rules-snapshot.json。公共库、DocuS和原始需求只读。

需求v1.4、架构v1.74、执行动态v3.02，关联128/R122、129/R123、127/125/126及STEP018/019/020原部署前置。用户已确认AP-125-NORMAL-INSTALL-01并要求加快功能收口，主控据此恢复同一对象范围内余项和明确次数；没有新资源/付费/数据模型或外发授权。

本轮scope/input-manifest/permit在D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/orchestration-continuation02-20261023/。签发@STAMP@，截止仍@DEADLINE@，Asia/Shanghai，不重置24h。只有人工转交/实际接收后才执行。

先读本卡、scope/permit/新输入与129结论的适用范围；复用原127六项及128续作01正确辅助。当前checkpoint来自continuation-01/checkpoint.json，不能从旧127或128首轮checkpoint回退。成功source的37行/17阶段收据hasha2211aa56f0497ef55e2ff42f4ea2e6b3b50bb3049cca62cbd5ef06844df6f06必须保留；已成功001—015、normal/R03和两登录权限不可重放或重建。

## 冻结产品和现有资源

当前安装器29865字节/hash7cd62b4f3526510c6f38de2a033a01d6ae36bcd661e90dbaca6b551db8141ba8，测试35468字节/hash2357a7031d2da858224d75b56ee0173a3166b0ca68c6905994009b7e64e6b3c3；完整产品41项以input-manifest为准。代码门与前三项已独审，不重新跑19/22/23或旧18/9。P3两行英文注释暂不修，不因它改变hash、加测试或复审。

允许修本轮验证辅助、已采用正常关闭私有配置的必要填写，以及README/normal-install.md按实际结果最小更新。安装器、测试、001—015、业务/角色/profile/权限模型、原生start_local、Compose、依赖锁等产品代码冻结；不得为通过跳过检查、改身份/时钟、开Q或换原始SQL。真遇功能/安全阻断缺陷，先留能定位的证据和最小影响再交回；普通夹具/配置填充问题在卡内有据修正，不为注释/格式/日志排版停线。

source仅CID db709b67cc8af398edf1735b0ac6fe365898264326466b2566f904784bfef48d，名称retrolume-q-first-normal，卷retrolume-q-first-normal-data，项目retrolume-first-install-source，bridge Id2f79fb05977e79f3fa89791f4a97553334be384ba6df89ecd0dc650c2018adb2；127.0.0.1:55482，库retrolume_q_first_normal/OID16384/systemid7699647093882925094。已安装，禁止再次apply或初始化001。

interrupted仅CID549f36f11827babea930f0338149aa3542e8ea4d3d7cceb67b54b79e25dca8e8，名称retrolume-install-interrupted，卷retrolume-install-interrupted-data，项目retrolume-first-install-interrupted，bridge Idc333276027ca367edf8086eec15763185fe2800f66c820792e7ad96cb842d610；127.0.0.1:55483，库retrolume_install_interrupted/OID16384/systemid7699647123872251942。尚未实际注入002，原失败收据不是已提交未知。

镜像仍缓存sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f，PG17/vector0.8.6，CPU1/512MiB/pids128/restart=no/loopback/无host bind。新create/卷/网络0，最多一PG活跃；只按精确CID/原创建身份/挂载/网络/根核验后start/stop，不拉取、构建、换名/端口/镜像或改宿主服务。

原.runtime/normal-first-install/source与interrupted四根/originals、三个UUID、SID/device/file-id和控制行身份全部复用checkpoint，不新建替代根或生成新身份。秘密只复用当前用户DPAPI在内存解密，环境引用/安全stdin注入，不重置密码、不输出明文/密文/DSN/Env/完整Compose或异常敏感内容。应用只用retrolume_normal_app，快照retrolume_normal_snapshot；管理员不交应用。API尚未选定，只在18122/18124/18126按序核可用后一次固定。

## 先准备完整余段，再串行运行

新辅助使用明确ROOT/E/PERMIT路径，先核旧helper复制后的根目录、许可日期、输入hash允许差异、entry命名和checkpoint指向。预演阶段只读状态分支，不导向check1/2/3或成功源apply。旧辅助的checks字典、api_completed和successful_receipt必须从实际最新checkpoint及已核收据导入，不能仅依据旧failed字段把前三项重跑。新as-run在真实执行前保存，原helper/日志不原地覆盖。

不启浏览器、renderer、前端dev server、TestClient或旧测试suite。只保留一个有界控制器及当前PG/官方API进程，关闭本卡已完成的诊断连接/子进程，避免无用同时占用。只读元数据足够，不为报表全表加载大结果。禁止结束用户或别的Agent进程。

容量门不变：Docker暖机后每次启动PG/API前实际可用物理内存>=512MiB；全程约2秒采样，连续两次<256MiB停止新动作并有界停自有资源。一次瞬时不足时允许在同一卡内最多90秒等待回收/平稳后再采样，达到原门即继续；PG存活期间等待要计持有，不新增服务。停止PG后也给系统有界回收时间，不在stop返回瞬间就用旧样本否决独立下一段。等待不改宿主、不开第二PG，不反复要求用户释放内存。

三项可按相互独立的条件调度，优先把单PG即可完成的中断保护和成功verify闭合，再做API周期；不要求为了编号顺序停线。全部需真实证据，顺序调整不削弱两API跨真实PG停/开的要求。具体可行次序为interrupted唯一场景并停；source首周期合并verify与首次API并停；source第二周期开API复测并停。verify在成功源第一次或第二次周期执行都可，但必须原成功收据/正确身份/真实只读；不可用旧apply后置核验替代。

## 三项必须完成的可观察行为

第五项，中断保护。仅对原interrupted，先只读核同一目标/无意外已提交阶段，然后正式原SQL001、002真实执行，002全部结果耗尽且COMMIT成功后唯一隐藏确认。原观察包装器可复用，不能Recorder代替驱动、删guard/SQL或模拟COMMIT。核001 confirmed、002 submitted/unknown、无003/complete/自动重放，独立只读连接核真实提交事实并关闭。原收据再次apply/verify本地拒绝，新收据对部分库预检零写拒绝。保留部分库/卷，不续装/清空/补签/退款。预定一次未知按场景收尾，其他非预期未知须停；实际唯一注入一旦发生，不能用备用次数再注入一遍。

第六项，只读复核。原source同一CID/OID/systemid/四根/三UUID和37行成功收据，正式verify CLI只提供管理员密码环境引用，不提供其他三秘密及业务/快照DSN；真实READ ONLY/schema/roles/身份相符、收据原字节不变，无DDL/DCL/业务写。坏绑定输入须连接前0调用拒绝，正常verify须真实连接。不要复制旧private配置到证据，不修完整收据以迎合新观察。

第四项，正常API跨PG重开。按原native data_exit结构建立正常源/ControlHub及原根绑定，model/integration/Q/preview保持原生关闭，不虚构loader字段，不切只读副本或旧TESTONLY。实际启动deploy/start_local.py --container retrolume-q-first-normal --port 固定端口 --shutdown-stdin，真实读取会话/capabilities/readiness和正常源事实，观察用新业务login而无管理员继承；区分预期Q关闭与本地source/schema失败。

首次原生API正常结束、树/端口释放后，实际停止source PG；再以同一CID/库/根/控制身份开启PG和第二个原生API周期，读取相同身份/数据，无自动迁移、预算重置、新实例或业务记录写入，然后正常停API/PG。不能用两个GET或同一PG存活期冒充跨PG重开。原生优雅停150秒及父等待已有上界要留足；实际无后台任务时可正常尽早结束，不人为睡满。无需模型、活动、索引、预览或浏览器。

某独立项暂时达不到启动门时，先完成容量允许的其他未完成项；不要把全部退回已通过部分，也不反复盲启。若90秒后仍无法容纳最小PG/API组合，统一记录“持续容量不足、哪些真实功能未跑”和实际样本后收尾，不能宣称通过或无限等；不会据此再开同样一轮猜测。

## 一次配足的连续预算

工程保守已用8400/10800、精确unknown，本轮仅恢复未用2400工具秒，含900秒保存/清场；原日历至@DEADLINE@不延长。所有筹备/夹具修正/等待/实际操作/收尾纳入，父子重叠分层不双算，不能只报SQL秒数。审计129保守900/2400及余1500已经封存，不挪作工程额度。

主控现在前向明确source累计上限5→7（当前4，两个必要周期加一个有据余量），interrupted2→3（当前1，唯一注入仍一次，额外只处理注入前有据普通失败）；API累计3保持（当前0）。入口累计7→8，当前6，entry07本次完整主批，entry08仅一次有据未完成段备用；取消旧entry07仅夹具这一过窄条件，容量恢复后也可依当前许可进入，但同一次未执行内存拒绝不消耗实际start。每个真实控制器/PG/API实际启动照记，不能循环藏次数或重置旧账。成功即停，备用不用就封存。

PG累计持有仍1800秒、已34.1386296749115；API仍900秒、已0；新资源0/费用0。余量不够完整相应段和停止储备就不启动该段，先收不受影响项。同根因两次有据修正仍失败、真实新功能/安全阻断、新权限/模型、非预期未知提交、任一时间/容量/累计硬门到限，停相关操作并一次交回。非阻断注释/格式/记录粒度不作为新增停止门。

## 原件、收尾与回传

保存三个检查点/真实驱动原件/实际SQL提交与收据/两API生命期和跨PG区间、真实身份/业务login/权限关闭状态、前后hash及数据对照；保存所有普通失败和修正/复用依据。每次启动门实际值、等待区间与压力样本尽量直接记录，已有足够证据不补跑，只在新增操作就地落盘。日志只保存脱敏白名单/限长实际异常，不原样输出kwargs、DSN或完整Docker Env。平台审批仍适用，拦截记未执行，不换工具/拆动作绕过。

收尾核两精确CID Running=false/Pid=0、自有API PID+birth/树结束、端口释放，成功/未知库及卷/网络/全部旧原件保留。无prune、down-v、DROP DATABASE、递归删除或旧scratch清理。可按实际验证事实最小更新README/安装说明；P3注释原样保留。

两代码与前三项已有独审，不再审一遍；本轮产品代码不变时主控只核新增三项动态原件和资源账，不安排重复全审。若确有新的安全/功能变更再决定其必要增量审查。Q FROZEN、T0/72h空，provider/Embedding/计量/付费、索引/查询/生成、三活动/grant/QAuthority.bind/InstanceBinding、浏览器/预览/业务Job、依赖安装与Git写全0，100/25及分额与外部门不变。

结果置顶续作02保当前25623字节完整后缀。先一句完成/具体功能阻断、4/5/6逐项结果与原始证据，再给实际模型、TASK/R/STEP、变化/复用、连续工具/持有/入口/启动/容量账、失败与偏差、精确停止/保留、未验证和待同步信息。没有新功能阻断不列新的零碎改进清单。主控统一维护DocuS与最终验收；工程不宣STEP、Q或NO3已通过。保存复读后仅回一句真实结论和D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-128-result.md的可点击绝对路径。

## 以下为续作01及首轮旧合同历史，不能叠加旧许可

'''.replace('@STAMP@', stamp).replace('@DEADLINE@', deadline)
    assert '*' not in contract and '\n|' not in contract
    registered = f'# 执行动态文档\n\n文档v3.02，2026-10-23，Asia/Shanghai。需求v1.4、架构v1.74。\n\n{stamp}。129已核收、128续作02同号登记，完整卡保存核读中，未派发。\n\n'.encode('utf-8')
    STATE.write_bytes(registered + old_state)
    CARD.write_bytes(contract.encode('utf-8') + old_card)
    assert CARD.read_bytes().endswith(old_card) and CARD.read_text(encoding='utf-8').startswith(contract)
    permit = {'TASK': 'TASK-128', 'R': 'R-122', 'round': '续作02', 'issued_at': stamp, 'valid_until': deadline,
              'status': '待人工转交', 'actual_dispatch': False, 'acceptance': None,
              'receiver': 'A+，刚执行128续作01的原工程窗口', 'task_card': item(CARD),
              'input_manifest': item(OUT / 'input-manifest.json'), 'scope': item(OUT / 'scope.json'),
              'restored_tool_seconds': 2400, 'save_reserve_seconds': 900, 'cumulative_tool_cap': 10800,
              'source_cap': 7, 'interrupted_cap': 3, 'api_cap': 3, 'entry_cap': 8,
              'original_success_install_no_replay': True, 'new_resources': 0, 'Q': 'FROZEN', 'fees_cny': 0,
              'P3_deferred_by_user': True, 'unchanged_code_no_repeat_audit': True}
    save_json(OUT / 'permit.json', permit)
    arch_prefix = f'''# 架构动态文档

文档v1.74，2026-10-23，Asia/Shanghai。需求v1.4、执行动态v3.02、task_model/07。以下v1.73原字节保留。

## 两安装修复独审已核收，剩余三项动态集中收口

{stamp}。129独立审查当前connect服务隔离及observe_identity主机格式通过功能/安全增量范围，前三项原件可采纳。主控接受独审并结束，未变代码不重复审；F129-01仅两行注释语言P3，按用户明确要求暂缓，不改hash、不加测试或新卡。

128整体尚未关闭，API跨PG重开、002唯一提交未知、成功收据verify仍not_run。同号续作02只补这三项、成功source/37行收据不可重放，代码冻结。原两个CID/卷/根复用，source/interrupted启动cap前向7/3、API3和入口8只为既定功能余项提供有限有据余量，原总工具/持有/日历不加。阶段间有界等待内存恢复，既定512/两次256门保持，不凭细节停线也不伪造运行。

无模型/权限/SQL/业务或平台变更。Q冻结、T0空、费用0及外部启用前置保留，主控未现场运行或探资源。后续只核新增动态事实，无新变更不重审当前代码；STEP/项目最终验收未签。

## 以下为v1.73及更早历史

'''.encode('utf-8')
    ARCH.write_bytes(arch_prefix + old_arch)
    state_prefix = f'''# 执行动态文档

文档v3.02，2026-10-23，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.74、task_model/07。以下v3.01原字节保留。

## 129独审验收结束，128续作02仅剩三项集中验证待转交

{stamp}。用户带回129并明确要求加快功能收口、不处理不影响功能细节。主控核{len(checks)}条引用零漂移，报告25406字节/hasha95f3ac087dcafbf9d74c0e6aa36961d3fcb67e18d77854dc046a16aa1bc39db，三轴限定结论与原件相符。129实际已返回，审计交付通过并结束，保守900/2400/精确unknown及余1500封存；未恢复工程额度。只hash未解码主控文档的披露和首方法失败保留，不再因此重复审。

接收两函数代码门及前三项真实拒绝/完整安装/登录权限。F129-01非阻断P3注释按用户最新明确要求暂缓，保留记录、不另修/测/审。第四API跨PG重开、第五002实际提交未知、第六成功收据verify仍not_run；128任务仍部分通过，未最终关闭。源已成功001—015且收据37行，禁止重放或重建；代码冻结，后续只核新增动态原件，无新安全差异不全审当前代码。

TASK128/R122续作02完整卡已置顶保存核读，保旧合同原字节，待人工转交A+刚执行128续作01的原工程窗口，未据保存宣称接收/启动，无并行工作。恢复原余2400工具秒含900保存/清场，连续保守8400/10800/精确unknown与原截止{deadline}不变。source current4/cap5前向cap7，中断current1/cap2前向cap3，API0/cap3保持，入口current6/cap7前向cap8；entry07合并主批、entry08仅一次有据未完成段备用。全部旧失败/unknown连续、不换号清零，新容器/卷/网络0。

PG持有已34.1386296749115/1800、API0/900，上限不增。原两CID/身份/四根和秘密复用，先离线修辅助路径/许可与checkpoint指向，前三项只继承不再跑。先处理单PG独立中断/verify，再两原生API跨实际PG停/开；非必要编号顺序不制造回传。每阶段512内存门不足可同卡等最多90秒恢复，约2秒采样、连续两次低256有界停自有资源，既定安全门不降低，不重复要求用户释放内存。持续容量不足则一次交回具体环境缺口，不机械重复试跑。

新范围/许可/核收原件在TASK128/orchestration-continuation02-20261023及129-work-decision。主控本轮只文件核证和共享维护，产品/测试/PG/Docker/API/实时内存探针均0。原125/126/120/117旧账均保留；Q FROZEN、T0/72h空、provider/费用0，100/25及分额/28Must/89动作不变，外部计量/账号/token/模板/Embedding容量门仍待。STEP018进行中/部分验证，019/020/M1/项目/发布未通过。CHG1678—1683，下一1684。

## 以下为v3.01及更早历史

'''.encode('utf-8')
    STATE.write_bytes(state_prefix + old_state)
    updates = [
        ('DocuN/results/TASK-129-work-decision.md', '验收结束独立增量审计，接受代码门/前三原件，P3按用户要求暂缓，余三仍未验。'),
        ('DocuN/results/TASK-128-work-decision.md', '置顶集中收尾决定、原余额恢复/同资源前向次数和有界容量等待，旧原文保留。'),
        ('DocuN/tasks/TASK-128.md', '同号置顶续作02完整合同，只补4/5/6、不动P3、不重审未变代码，原工程待转交。'),
        ('DocuS/架构动态文档.MD', 'v1.74登记两修独审已采纳和余三动态范围，原架构/SQL/权限/Q不变。'),
        ('DocuS/执行动态文档.MD', 'v3.02登记129已返回结束、128续作02待转交及连续预算，保留全部历史。'),
        ('DocuN/evidence/TASK-128/orchestration-continuation02-20261023/', '保存独审原件/身份核证、旧共享/旧卡、新范围/输入/许可与保存复读，主控运行0。')]
    text = '\n' + '\n\n'.join(f'- CHG-{1678+i}，{stamp}，Codex编排Agent，{path}。{note}' for i, (path, note) in enumerate(updates)) + '\n'
    CHANGE.write_bytes(old_change + text.encode('utf-8'))
    assert STATE.read_bytes().endswith(old_state) and ARCH.read_bytes().endswith(old_arch)
    assert DEC128.read_bytes().endswith(old_dec128) and CHANGE.read_bytes().startswith(old_change)
    assert item(ROOT / 'DocuN/results/TASK-129-result.md') == audit_report
    assert item(ROOT / 'DocuN/results/TASK-128-result.md') == r128
    for row in manifest['products']:
        assert item(Path(row['path']))['sha256'] == row['sha256']
    proof = {'saved_at': datetime.now(timezone(timedelta(hours=8))).isoformat(), 'TASK': 'TASK-128', 'R': 'R-122', 'round': '续作02',
             'files': [item(path) for path in [CARD, DEC128, DEC129, STATE, ARCH, CHANGE, OUT / 'permit.json', OUT / 'scope.json', OUT / 'input-manifest.json']],
             'identity_reference_checks': len(checks), 'mismatches': 0, 'status': '待人工转交', 'actual_dispatch': False,
             'old_card_and_shared_bytes_preserved': True, 'reports_unchanged': True, 'P3_deferred': True,
             'product_runtime': 0, 'live_resource_probes': 0, 'next_CHG': 1684}
    for row in proof['files']:
        Path(row['path']).read_text(encoding='utf-8')
    save_json(OUT / 'save-proof.json', proof)
    print(json.dumps({'saved': True, 'TASK': 'TASK-128', 'round': 'continuation-02', 'checks': len(checks),
                      'mismatches': 0, 'P3': 'deferred', 'restored_seconds': 2400,
                      'card_bytes': CARD.stat().st_size, 'runtime': 0}, ensure_ascii=True))


if __name__ == '__main__':
    main()
