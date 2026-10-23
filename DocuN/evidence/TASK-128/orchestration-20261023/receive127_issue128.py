"""主控有限文件核证和新合同登记；不导入产品，不启动资源。"""
import hashlib
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
PUBLIC = Path('D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4')
OUT = ROOT / 'DocuN/evidence/TASK-128/orchestration-20261023'
RETURN = ROOT / 'DocuN/evidence/TASK-127/orchestration-return-20261023'
EXEC = ROOT / 'DocuN/evidence/TASK-127/execution'
ORIGINAL = ROOT / 'DocuN/evidence/TASK-127/orchestration-20261022'
STATE = ROOT / 'DocuS/执行动态文档.MD'
ARCH = ROOT / 'DocuS/架构动态文档.MD'
CHANGE = ROOT / 'DocuS/文档变更记录.MD'
CARD = ROOT / 'DocuN/tasks/TASK-128.md'
DECISION = ROOT / 'DocuN/results/TASK-127-work-decision.md'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def info(path):
    raw = path.read_bytes()
    return {'path': path.as_posix(), 'bytes': len(raw), 'sha256': sha(raw)}


def js(path):
    return json.loads(path.read_bytes())


def write_json(path, value):
    raw = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    with path.open('xb') as stream:
        stream.write(raw)
    assert path.read_bytes() == raw


def main():
    for path in (OUT, RETURN, STATE, ARCH, CHANGE, CARD, DECISION):
        for parent in [path, *path.parents]:
            if parent.exists():
                stat = parent.lstat()
                assert not parent.is_symlink() and not getattr(stat, 'st_file_attributes', 0) & 0x400, str(parent)
            if parent == ROOT:
                break
        else:
            raise RuntimeError('项目输出越界')
    assert not CARD.exists() and not DECISION.exists() and not (OUT / 'permit.json').exists(), '已有登记，先核断点'
    state_old, arch_old, change_old = STATE.read_bytes(), ARCH.read_bytes(), CHANGE.read_bytes()
    assert '文档v2.98' in state_old.decode('utf-8-sig').splitlines()[2]
    assert '文档v1.70' in arch_old.decode('utf-8-sig').splitlines()[2]
    assert 'CHG-1662' in change_old.decode('utf-8-sig')[-1800:] and 'CHG-1663' not in change_old.decode('utf-8-sig')
    now = datetime.now(timezone(timedelta(hours=8)))
    stamp = now.isoformat()
    old_permit = js(ORIGINAL / 'permit.json')
    deadline = old_permit['valid_until']
    assert now < datetime.fromisoformat(deadline), '原日历已到期，不能暗延长'
    original_manifest = js(ORIGINAL / 'input-manifest.json')
    assert sha((ORIGINAL / 'input-manifest.json').read_bytes()) == old_permit['input_manifest']['sha256']
    assert sha((ROOT / 'DocuN/tasks/TASK-127.md').read_bytes()) == old_permit['task_card']['sha256']
    post, pre = js(EXEC / 'post-snapshot.json'), js(EXEC / 'pre-snapshot.json')
    result_path = ROOT / 'DocuN/results/TASK-127-result.md'
    result = info(result_path)
    readback = js(EXEC / 'result-readback.json')
    assert (result['bytes'], result['sha256']) == (readback['bytes'], readback['sha256'])
    assert not readback['missing_links']
    checks = []

    def check(path, expected, expected_bytes=None, category='evidence'):
        path = Path(path)
        if not path.is_absolute():
            path = ROOT / path
        observed = info(path)
        assert observed['sha256'] == expected, str(path)
        if expected_bytes is not None:
            assert observed['bytes'] == expected_bytes, str(path)
        checks.append({**observed, 'category': category, 'match': True})

    for entry in original_manifest['sources']:
        check(entry['absolute_path'], entry['sha256'], entry['bytes'], 'frozen_product')
    for group in ('inputs', 'evidence_inventory'):
        for entry in post[group]:
            check(entry['path'], entry['sha256'], entry.get('bytes'), group)
    for entry in post['rules']:
        check(PUBLIC / entry['path'].replace('\\', '/'), entry['sha256'], category='locked_rule')
    for entry in js(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json'):
        check(PUBLIC / entry['relative_path'].replace('\\', '/'), entry['sha256'], category='pinned_rule')
    assert len(post['inputs']) == 41 and len(post['rules']) == 7
    checkpoint = js(EXEC / 'final-checkpoint.json')
    assert sha((EXEC / 'checkpoint.json').read_bytes()) == post['checkpoint_sha256']
    assert (EXEC / 'checkpoint.json').read_bytes() == (EXEC / 'final-checkpoint.json').read_bytes()
    assert checkpoint['entries'] == post['entries'] == 3
    assert post['api_started'] == 0 and post['api_holding_seconds'] == 0
    assert abs(post['pg_holding_seconds'] - 8.117866039276123) < .000001
    expected_slots = {
        'source': {'cid': 'db709b67cc8af398edf1735b0ac6fe365898264326466b2566f904784bfef48d',
                   'port': 55482, 'system_identifier': '7699647093882925094',
                   'trace': 'source-wrong-database_oid-trace.jsonl',
                   'receipt': 'source-wrong-database_oid-receipt.jsonl', 'command': 'command-009.json'},
        'interrupted': {'cid': '549f36f11827babea930f0338149aa3542e8ea4d3d7cceb67b54b79e25dca8e8',
                        'port': 55483, 'system_identifier': '7699647123872251942',
                        'trace': 'interrupted-expected-unknown-trace.jsonl',
                        'receipt': 'interrupted-expected-unknown-receipt.jsonl', 'command': 'command-015.json'},
    }
    facts = {}
    for slot, expected in expected_slots.items():
        observed = post['objects'][slot]
        target = checkpoint['slots'][slot]
        assert observed['cid'] == target['cid'] == expected['cid']
        assert target['port'] == expected['port'] and target['starts'] == target['create_attempts'] == 1
        assert observed['state']['Running'] is False and observed['state']['Pid'] == 0
        assert target['database_identity']['system_identifier'] == expected['system_identifier']
        trace_path = EXEC / 'entry-03' / expected['trace']
        receipt_path = EXEC / 'entry-03' / expected['receipt']
        trace = [json.loads(line) for line in trace_path.read_text(encoding='utf-8').splitlines()]
        receipt = [json.loads(line) for line in receipt_path.read_text(encoding='utf-8').splitlines()]
        command = js(EXEC / 'entry-03' / expected['command'])
        kinds = [line['kind'] for line in trace]
        assert kinds.count('real_connect_requested') == 1 and 'real_connect_returned' not in kinds
        assert trace[-1]['connections'] == 1 and trace[-1]['write_requests'] == 0
        assert trace[-1]['planned_injection_exercised'] is False
        assert len(receipt) == 2 and receipt[-1] == {'event': 'stopped', 'reason': 'installation_stopped', 'confirmed_stages': [], 'unknown_stage': None}
        assert command['exit_code'] == 2 and command['stderr'] == ''
        assert json.loads(command['stdout'])['reason'] == 'installation_stopped'
        facts[slot] = {
            'cid': expected['cid'], 'port': expected['port'], 'database_identity': target['database_identity'],
            'container_state_as_of_post': observed['state'], 'network': observed['network'],
            'volume': observed['volume'], 'roots': observed['roots'], 'identities': target['identities'],
            'recorded_starts': 1, 'recorded_create_attempts': 1,
            'connect_requested': 1, 'connect_returned': 0, 'installer_write_requests_observed': 0,
            'exception_details_not_captured': True, 'planned_unknown_injection_exercised': False,
            'receipt': info(receipt_path), 'trace': info(trace_path), 'command': info(EXEC / 'entry-03' / expected['command']),
            'db_empty_currently_not_independently_verified': True,
        }
    asrun = js(EXEC / 'entry-03/as-run.json')
    for entry in asrun['helpers']:
        check(entry['path'], entry['sha256'], entry['bytes'], 'as_run_helper')
        snapshot = EXEC / 'entry-03' / Path(entry['path']).name
        check(snapshot, entry['sha256'], entry['bytes'], 'as_run_copy')
    assert post['secret_scan']['matched'] == 0
    assert post['no_listening_selected_pg_or_api_candidate_ports'] is True
    assert post['q'] == 'FROZEN' and post['T0'] is None
    observer = (EXEC / 'install-observer.py').read_text(encoding='utf-8')
    assert 'inner = real_connect(**kwargs)' in observer and 'real_connect_returned' in observer
    connect_block = (ROOT / 'deploy/initialize_normal.py').read_text(encoding='utf-8').split('def connect(config, credentials):', 1)[1].split('def read_credentials', 1)[0]
    assert 'hostaddr=target["host"]' in connect_block and 'service=""' in connect_block

    OUT.mkdir(parents=True, exist_ok=True)
    RETURN.mkdir(parents=True, exist_ok=False)
    before = OUT / 'before'
    before.mkdir(exist_ok=False)
    for path, data in [(STATE, state_old), (ARCH, arch_old), (CHANGE, change_old)]:
        (before / path.name).write_bytes(data)
    return_check = {
        'checked_at': stamp, 'TASK': 'TASK-127', 'R': 'R-121', 'result': result,
        'identity_reference_checks': len(checks), 'mismatches': 0, 'checks': checks,
        'facts': facts, 'source_count': 41, 'rules_count': 7,
        'runtime_probe_by_orchestrator': 0, 'fresh_resource_stop_not_inferred': True,
        'expected_six_passes': 0, 'known_connection_failures': 2,
        'root_cause': '尚未确定；控制器连接成功、正式connect请求后未返回，实际异常未留存',
        'candidate_difference': '正式connect另传service空串/options等；须差异诊断，不先判根因',
        'all_product_bytes_unchanged': True,
        'budget': {'old_combined_entries': 3, 'old_combined_entry_cap': 3,
                   'old_tool_exact_seconds': None, 'old_tool_conservative_seconds': 4800,
                   'original_tool_cap_seconds': 10800, 'sealed_unused_seconds': 6000,
                   'old_pg_holding_seconds': post['pg_holding_seconds'], 'old_api_starts': 0},
    }
    write_json(RETURN / 'return-check.json', return_check)
    decision = f'''# TASK-127 / R-121 主控核证与接续裁定

{stamp}，Asia/Shanghai。主控收到真实结果路径后核{len(checks)}条身份引用，零缺失零漂移；报告16765字节/hash{result['sha256']}，41产品与七规则冻结，原工具/迁移未改。

## 当前裁定

调度已返回并停止，任务验收失败。两个真实连接边界均失败，四项因前置未到未执行，六项无完整通过；不能称源成功安装或002已提交未知。报告、全部原始失败和3/3合并入口原样保留。125/126已验收的有限代码与离线/独审范围不推翻，也不代替这次真实失败。

source及interrupted在原post时点均Running=false/Pid=0，PG/API候选无监听，API启动0；这是原件可支持的停止事实，主控未现场探测当前资源。两槽位实际CID/数据库systemid/OID/根实体和创建身份已留存，不再新建/换槽位。

## 原因分层

原筹备有Docker引擎不可用/平台原生读取权限和辅助不存在门大小写缺陷；这些已有原始失败与有据修正。最后失败另发生在正式psycopg.connect：控制器真实连接已查得两个库身份，正式观察各记录一次连接请求、无返回、写请求0，CLI只剩installation_stopped。包装器没有保存脱敏异常类型/SQLSTATE，因此当前不能判产品、认证或夹具的根因。正式connect另传service空串及options是可检差异，不是已确定结论。

本次不盲重跑六项或重建环境。先取得同目标/凭据条件下的可比较连接结果与脱敏异常，再完成最小修复及六项。允许修复的范围新增为既有连接参数适配及必要测试，属于新关联TASK128/R122；不在已结束125或冻结127原件上暗改执行合同。若需改变角色/SQL/认证信任或主要配置模型则仍停止并交回。

## 预算与接续

127的3/3入口封存，工具精确unknown/保守4800/10800，PG保守8.117866039276123/1800、source与interrupted各start1、API0，两个create各1/1。未用6000秒和原持有/启动余额仅按TASK128完整合同显式恢复用于同一采用包余项，原日历截止{deadline}不延长。原入口计数从3前向最多6，新卡至多三个实际合并入口；不得把换号写成无历史失败或新增10800秒。所有旧120/117/125/126账保留。

TASK128交原A+工程窗口，包含先诊断/受限修复/六项真实闭合及同身份精确停止。产品若无变化，不重复已通过代码审计；若安装器有增量，稳定后集中独审其连接边界和实际影响，工程不自签。Q继续冻结、T0空、真实provider/费用0，STEP及项目不放行。
'''
    DECISION.write_text(decision, encoding='utf-8', newline='\n')
    restored = {
        'TASK': 'TASK-128', 'R': 'R-122', 'issued_at': stamp, 'valid_until': deadline,
        'source_approval': 'AP-125-NORMAL-INSTALL-01，用户确认',
        'reason_for_new_task': '原127失败后新增受限产品连接修复权并合并既有六项余缺，不重置历史',
        'runtime_slots': facts,
        'resource_policy': {'new_container_create': 0, 'new_volume': 0, 'new_network': 0,
                            'image_pull_build': 0, 'max_active_pg': 1, 'per_pg_memory_mib': 512,
                            'startup_memory_mib': 512, 'pressure_memory_mib': 256, 'pressure_samples': 2},
        'tool_pool': {'original_cap_seconds': 10800, 'old_conservative_used_seconds': 4800,
                      'old_exact_seconds': None, 'restored_max_seconds': 6000, 'save_cleanup_reserve_seconds': 900},
        'cumulative_caps': {'combined_entries': {'used': 3, 'cap': 6},
                            'source_pg_starts': {'used': 1, 'cap': 4},
                            'interrupted_pg_starts': {'used': 1, 'cap': 2},
                            'api_starts': {'used': 0, 'cap': 3},
                            'pg_holding_seconds': {'used': 8.117866039276123, 'cap': 1800},
                            'api_holding_seconds': {'used': 0, 'cap': 900}},
        'allowed_product_changes': ['deploy/initialize_normal.py:connect及保持原隔离的直接局部帮助',
                                    'backend/tests/test_normal_install.py:必要定向缺陷验证',
                                    'deploy/normal-install.md:实际变化与验证范围', 'README.md:最小实际用户说明'],
        'Q': 'FROZEN', 'T0': None, 'real_provider': 0, 'fees_cny': 0,
        'secrets_policy_unchanged': True, 'new_approval_requested': False,
    }
    write_json(OUT / 'restored-scope.json', restored)
    inputs = {
        'TASK': 'TASK-128', 'R': 'R-122', 'issued_at': stamp,
        'product_baseline': original_manifest['sources'], 'rules': original_manifest['rules'],
        'root_entry': info(ROOT / 'AGENTS.md'),
        'result127': result, 'readback127': info(EXEC / 'result-readback.json'),
        'return_check': info(RETURN / 'return-check.json'), 'decision': info(DECISION),
        'original_contract': info(ROOT / 'DocuN/tasks/TASK-127.md'),
        'original_permit': info(ORIGINAL / 'permit.json'),
        'post_snapshot': info(EXEC / 'post-snapshot.json'),
        'checkpoint': info(EXEC / 'final-checkpoint.json'),
        'as_run': info(EXEC / 'entry-03/as-run.json'),
        'scope': info(OUT / 'restored-scope.json'),
        'driver_readonly_diagnostic_sources': [info(ROOT / 'backend/.venv/Lib/site-packages/psycopg/connection.py'), info(ROOT / 'backend/.venv/Lib/site-packages/psycopg/conninfo.py')],
    }
    write_json(OUT / 'input-manifest.json', inputs)
    task = '''# TASK-128 / R-122 正式安装连接故障完整收敛与六项真实验证闭合

## 目标与交付

接收A+增强工程，继续刚执行TASK127的原TASK125安装工程窗口。你在同一卡内先取得真实连接失败的可比较、脱敏诊断，完成范围内最小修复，再把127未完成的六项真实部署检查连续闭合并精确停止。不是重做旧离线或盲重跑；遇真实停止条件才统一回传。工程不代签独立审计、主控验收或Q启用。

结果保存D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-128-result.md；新辅助/运行原件保存D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/。127统一报告、收据、检查点、as-run及历史原件全部只读保留。不要把127失败改写为通过；本卡六项可以用新实证补足原采用包目标，并逐条交叉引用。

完成要求是连接根因有可复核证据、必要增量最小且原隔离不减、六项各有真实目标行为证据及完整资源/预算/停止账。仅原代码/记录器通过或顶层控制器exit0不能称完成。若产品有增量，交稳定候选与集中增量独审所需证据，不自签最终通过。

## 项目、规则和安排

真实项目根D:/shspic/project_NO3_RetroLume-agent，入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。模式task_model，V4.0/AGENTS CHG-0003。公共根D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4；读DocuS/AGENTS.MD及WORK.MD合同/停止/记录有关章节，锁定指纹在项目DocuN/evidence/v4-migration-20260930/rules-snapshot.json。未变同窗材料复用，只补当前差异，不读其他模式或自动采用新版本。

需求v1.4，架构v1.71，执行动态v2.99；关联原TASK127/R121、已验收125/R119与126/R120、STEP018部署前置、STEP019适用权限证据、STEP020本机交付，NFR-004/CON-002/DR-002和既有隔离约束。新增受限连接修复权使本卡区别于127冻结版纯验证，旧失败/投入随相同资源和目标连续，不因新编号清零。

A+理由是正式连接与可用控制连接差异、libpq环境、权限和真实事务边界的故障定位；实际模型/客户端如实登记，不以档位代身份。默认原工程唯一窗口，无并行实现/审计，126独审窗口不执行本卡。没有实际接收前仅待转交，已记录主控回收127不等于你已接收128。

实际授权仍是用户确认AP-125-NORMAL-INSTALL-01的两固定PG槽位/原六项及项目范围内普通缺陷修复；主控现按本卡显式恢复同包剩余工具和资源额度，不请求用户重复批准普通步骤。读DocuN/evidence/TASK-128/orchestration-20261023/内restored-scope.json、input-manifest.json、permit.json及本卡全文。正式签发@STAMP@，截止仍为@DEADLINE@，Asia/Shanghai，不新开24h。

## 真实断点与先读材料

127报告16765字节，SHA256=e001d7892f3e11581db4731e53242cd007870165c97a7b186496ebb84b3dc73b。主控已核@CHECKS@条身份引用无漂移；41产品/七规则及三辅助as-run相符。两槽位曾真实启动且控制器连接查得PG17/vector0.8.6及OID/systemid。正式CLI的两trace各只有一次real_connect_requested、没有returned，写请求0，收据仅intent/stopped、confirmed=[]、unknown_stage=null。错误OID反例和002注入都未真正到达，六项没有一项完整通过，不能称部分迁移成功。

关键证据缺口是install-observer.py调用real_connect抛出后未保留脱敏异常；产品将其归一为installation_stopped。因此产品、环境、凭据还是夹具的根因未知。正式connect比控制器连接另带service空串和options等参数，这是待验证差异，不是已确认原因，禁止照猜测改一行就宣称修好。

已有Docker API500/version超时、原生读取受限令牌errno5、辅助No such/no such大小写误判的失败及修正保留；最后一次已证明引擎与两个PG可用，不重复拉镜像、建资源或要求用户恢复引擎。原收尾post时点两CID均Running=false/Pid=0、端口无监听；当前执行前仍核实际归属和状态，不凭历史推断实时已停。

按序读取根入口/已变共享顶部/本卡与许可；TASK127-result、TASK127-work-decision、本卡input-manifest与旧127原完整合同；127 execution的post-snapshot/final-checkpoint、entry-03/as-run、两trace/command/receipt及实际run-six.py/install-observer.py/win-support.py；正式initialize_normal.py的connect/read_credentials/apply/verify和当前psycopg/conninfo直接依赖；最后按实际需要读原001—015固定清单、原生start_local/Compose和data_exit配置/ControlHub/根绑定/权限原接口。旧126代码审计和18/9方法仅复用适用结论，不重新全审或重跑。所有相对路径以真实根为准，必要上下文同窗未变只补缺。

## 精确对象，只复用不创建

source固定CID=db709b67cc8af398edf1735b0ac6fe365898264326466b2566f904784bfef48d，容器retrolume-q-first-normal；卷retrolume-q-first-normal-data，项目retrolume-first-install-source，bridge Id=2f79fb05977e79f3fa89791f4a97553334be384ba6df89ecd0dc650c2018adb2；127.0.0.1:55482，库retrolume_q_first_normal，OID16384，system_identifier=7699647093882925094，管理员retrolume_source_bootstrap。

interrupted固定CID=549f36f11827babea930f0338149aa3542e8ea4d3d7cceb67b54b79e25dca8e8，容器retrolume-install-interrupted；卷retrolume-install-interrupted-data，项目retrolume-first-install-interrupted，bridge Id=c333276027ca367edf8086eec15763185fe2800f66c820792e7ad96cb842d610；127.0.0.1:55483，库retrolume_install_interrupted，OID16384，system_identifier=7699647123872251942，管理员retrolume_interrupted_bootstrap。

镜像仍仅缓存pgvector/pgvector@sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f，CPU1/512MiB/pids128/restart=no/loopback/无host bind，最多一个PG活跃。新容器/create尝试、卷、网络均0；不compose up/create/down、换名换端口、重置账号/密码、换镜像、拉取构建或接管别的资源。只按上述CID start/stop并核镜像/挂载/创建时刻/网络Id/映射，现有名字不足以授权。

私有根只复用D:/shspic/project_NO3_RetroLume-agent/.runtime/normal-first-install/source及interrupted。原data/backup/control/restore和originals实体file-id/owner/SID/三个UUID逐项沿用final-checkpoint及本卡scope。device=1031070048549017791；source四根file-id依次562949953906263/6264/6265/6266（后三项完整值分别562949953906264、562949953906265、562949953906266），interrupted依次562949953906295、562949953906296、562949953906297、562949953906298；完整精确实体以原JSON和本卡scope为准，不按字符串简写匹配。当前SID/owner仍须符合原记录。发现漂移停止，不再生成新的安装UUID或root身份。不存在成功控制行或ControlHub是原报告范围，不假称已核当前DB为空。

原DPAPI秘密只能通过现有本卡归属私有位置在当前用户内存解密复用，不能重新随机密码或ALTER ROLE。诊断前先在内存确认控制器与正式入口使用相同秘密字节；证据只记相等/引用名，不输出值、可猜测摘要、DSN或完整环境。安装/业务/快照/maintenance四用途继续分离；source业务/快照登录仍retrolume_normal_app/retrolume_normal_snapshot，interrupted仍retrolume_interrupt_app/retrolume_interrupt_snapshot。应用不继承安装管理员DSN。

本机API候选只从18122、18124、18126按序核可用后一次选定；原API尚未选定，不能把PG端口选定的限制错套为API无可用端口。选定后不轮换。遇系统保留端口不改Windows网络/排除范围，不结束他人进程。无用户库、旧合成库或旧TESTONLY配置。

## 诊断、允许修复与先后门

先离线把新观察/控制器/保存/预算/压力退出准备完整，原127原件不覆盖。可以复制必要辅助脚本到新execution后修改为128，但产品不依赖这些脚本。新检查点引用原final-checkpoint并继承实际数值和资源身份，不改原checkpoint/旧permit强行再跑127入口，也不绕旧3/3门。

第一步先补证据能力。观察层在real_connect外捕获异常，记录实际异常类/模块、SQLSTATE（可空）、安全类别及限长已脱敏诊断；处理所有当前秘密、连接串和参数后才落盘，禁止原样str(error)/repr(kwargs)/整个stderr/traceback泄露。保留异常原义继续抛给正式工具，外部CLI脱敏归一仍可保持。必须在无凭据合成异常里验证记录确实生效且不泄密，不能再次只有installation_stopped就盲重试。

比较必须固定同一源CID/host/hostaddr/port/database/login/秘密、驱动版本与子进程环境，只改变经过源码核实的最小参数差异。离线能经真实libpq参数解析定位的问题先离线确认，不为每个猜测start一次PG；纯记录器只用于安全/调用序检查，不能证明真实库可用。需要实际认证时，先在source本轮唯一启动中以控制器真实连接查同一身份，再用正式connect做只读连接及真实异常对照；此诊断阶段禁止apply/DDL/DCL和业务写。

定位证据须能区分环境/凭据注入错误、验证包装错误、正式连接参数/驱动适配缺陷。不得通过去掉hostaddr、放松loopback/OID/systemid/NAT核验、借助未知service配置或旧环境回退来制造成功。不读取用户PG service/passfile等未授权私配。service空串或options若证实为根因，修复必须保留原来防环境隐式改写目的地及凭据的安全目标；不能简单删掉隔离项使PGSERVICE/PGHOSTADDR重新取得效果。

允许只修新增execution辅助；如果真实根因确在产品，可修改deploy/initialize_normal.py的connect参数适配和为维持既有环境隔离所必需的直接局部帮助，backend/tests/test_normal_install.py补最小正/反例，并在README.md、deploy/normal-install.md按真实事实最小更新。必须先存pre副本/hash、最终完整diff、受影响调用分析和as-run hash。禁止修改SQL/role/profile/manifest/原配置schema/权限模型/业务代码/原native启动器/Compose/依赖锁；不得全局修改驱动或用户环境。

旧测试若断言的正是已证缺陷参数，按根因改成能区分坏行为和安全修复的新断言，保留其他安全断言与原失败；不能以删除测试/替换真实connect/跳过apply来造绿。只集中验证直接受影响方法与新根因正反例，不重新全跑旧18/9或整仓。保持F126-01显式host/hostaddr=127.0.0.1、合法NAT支持和F126-02物理路径保护、四秘密隔离、提交未知不重放、schema/权限检查。若要改变安全策略、认证信任、安装目的地、ROLE/SQL或公开接口则停相关部分交回，不能凭普通连接修复权扩范围。

根因和修复验证具备后，先完成当前source同一身份的只读核验，确认未有迁移、额外表/职责组/登录或未知提交；以实际原只读预检/目录事实与原收据交叉验证，不凭旧trace的writes=0作DB绝对空证明。只有该证据及修复安全门均满足才用新收据执行下一段。若发现真实submitted未知或非本卡对象，不清库、不补签或自动续装。

若产品未改，原126门按不变范围继承；若产品连接增量落地，工程稳定后由主控集中安排独立增量审查其连接边界、差异/直接影响与新真实原件，不重复未变SQL/角色全审。本卡工程不自签该独审或最终关闭；角色/不可逆原风险边界沿用原126已审模型，新增策略变化仍是前述硬停止条件。

## 六项合并验收，全部原目标不删减

原六项完整标准以只读TASK127.md“六项真实检查”为原合同输入，本节同步列出，不能仅凭引用跳过。原失败不重复覆盖，用本卡独立收据/trace，旧收据仍保留。

1. source空库分别错误OID/system_identifier真实拒绝、非空表和职责组碰撞各自拒绝，须命中对应原因且安装器无写，不能都命中other_clients。允许的临时对象仍仅public.retrolume_install_probe_nonempty及retrolume_data_app NOLOGIN碰撞组；只在事前证不存在并记录本次创建OID后创建，按同名同OID精确撤销，仅安装成功前完成，不触动后续正式同名职责组。不要全库清理。
2. 同一source原生正式apply完整执行原001—015，不改SQL/guard/事务，不再运行initialize-materials；实际观察013后normal/R01、014/R02、015/R03、原schema_checks/q_roles及37条完整成功收据。确认17个submitted/confirmed和complete均对应真实提交；只用观察包装，不能Recorder替代驱动或patch核验。source真实成功仅一次，后续不重放迁移。
3. 真实新业务/快照登录分别认证，核ROLE_CAPABILITIES/MEMBERSHIPS及实际最小读取。快照不能业务写/读maintenance/SET业务或owner，业务无超级/建库/建角色/复制/bypassrls/owner/传递SET/INHERIT/ADMIN越权。实际权限查询或少量有界回滚反例即可，不扩全安全矩阵、不造业务账。
4. 按原loader/data_exit结构和四根/UUID建立真正normal源与ControlHub绑定，model/integration/Q/preview关闭。正式deploy/start_local.py --container retrolume-q-first-normal --port 已选API --shutdown-stdin启动，读真实capabilities/readiness，区分预期Q外部门未齐和本地来源/schema失败。正常停止，再同一CID/库/根/身份原生重开一次、读取和正常停止；无自动迁移/换身份/重置。保持安装管理员不交应用。无需浏览器/worker/模型/预览；不得为绕正式生命期改startup源码或用旧只读恢复目标假装正常源。
5. source停止后只启interrupted，在原002真实执行、耗尽结果且COMMIT已成功之后唯一隐藏一次确认，观察001 confirmed、002 submitted/unknown、无003/complete/自动重放，另真实只读查提交事实。保留部分库/卷。原收据再次apply与verify本地拒绝，新收据对部分库真实零写拒绝；不续装/清空/补签。此前127尚未到此注入，因此本次仍只许一次实际注入，不误称重复配额。预定此例未知允许按场景观察/收尾，其他非预期未知均停。
6. interrupted停止后source同一成功收据真实verify，只提供管理员密码环境引用，不提供其他三秘密及业务/快照DSN。READ ONLY/schema/roles/身份一致、收据字节不变，无DDL/DCL/业务写；坏收据绑定在连接前拒绝。正常verify必须真实连接，拒绝前0连接可用观察器证明。最后停止source。

开始真实段前把以上六项的身份/连接/退出和预期断言核成完整计划，避免到末尾才发现控制器分支先天不能到达。可以复用127未变正确辅助和已核资源创建证据；不能继承不存在的六项PASS。原3入口与全部失败原件照留。

## 连续预算与可行顺序

原采用包工具10800秒未加总；127精确unknown、保守已占4800秒。本卡只恢复余6000秒，含900秒保存/自有收尾；新增实际投入与原4800累计不得超过10800。日历仍至@DEADLINE@，不因新卡重启24h。125/126/120/117旧账保持。

原合并入口3/3封存，本卡前向增加至累计最多6，新增至多三个显式进入受控真实段的合并入口，编号沿entry04—06留账。离线读取、控制器语法/安全自检和一次有界只读引擎前置不独立算真实入口，仍记实际失败/耗时；不能用长驻循环隐藏真实多次启动或绕平台审批。修正后只续失败/尚未执行段，不把六项全套反复跑。

资源累计硬上限不变。source start原1/4，剩最多3；interrupted原1/2，剩1；API原0/3；PG持有原8.117866039276123/1800秒，API原0/900秒。新create/卷/网络均0。预算应读原checkpoint和新连续账，不写零起点。

可行顺序是先离线定位/修辅助，source第2次启动内合并真实只读连接诊断、必要确认、拒绝反例、成功安装/权限和首个原生API周期；source第3次启动作同库重开第二周期后停；interrupted第2次启动作唯一真实注入/拒绝/停；最后source第4次启动verify/停。可在同次PG存活期间安排两个API周期以节省一次start，但不能为了省次数虚报同库重开或占用长时PG等离线改码。若实际诊断须停库修码，重新计算剩余启动能否覆盖原六项，不能暗加第五次source或第三次interrupted。

启动PG/API前现机Docker暖机后可用物理内存>=512MiB；约2秒采样，连续两次<256MiB停止新动作并精确关闭自有API/PG。不反复要求用户释放内存、不用2GiB门、不同时开两PG、不启动浏览器/renderer。PG/API持有按start请求到stop确认计，不只算SQL秒数；命令父子重叠分层不双算，不漏筹备/修码/保存。

原生start_local优雅停止150秒和父等待/终止已有上界须预留，不能自行缩短导致误判。压力退出/日历/剩余工具不足时只作有界自有收尾并保存。产品或同根因两次有据修正仍失败、根因不稳、新高风险/权限范围改变、任一累计上限到门，停受影响部分并完成不受阻项后一次交回。工具unknown如实标未知及保守占用，不编精确秒数。

## 安全、证据与最终回传

主控只恢复本卡范围内许可，平台审批仍适用；审批容量/权限拦截如实记未执行，不拆命令/换客户端或参数绕过。无SQL/权限/镜像/依赖新授权需求时不要重问用户已决定的普通步骤。

随机秘密/DPAPI密文、DSN、Env和完整Compose禁止进入公开证据。新diagnostic须有安全白名单和实际异常留存，避免两端都“泛化错误”导致无法定位；脱敏前不得写临时原日志。真实值只在内存/安全子进程环境，不重置或索取聊天密钥。Docker只输出完整JSON在内存取白名单后的投影，不用旧HostConfig.Mounts格式模板。

保存接收/规则/输入pre、每次实际as-run源码或完整指纹、产品pre/post与diff、根因反证和最小修复验证、六项原始收据/trace/DB错误码/权限及两次原生API的真实事实。停止证明按精确CID/创建身份和自有API PID/birth/句柄或进程树，最终Running=false/Pid=0/端口释放；同时保存旧成功和失败数据。无prune、compose down -v、DROP DATABASE、递归删除、第三槽位或清理旧scratch。允许精确临时反例表/组撤销的原边界不扩大。

Q保持FROZEN、T0/72h空，真实provider/Embedding/计量/费用、索引/查询/生成/三活动/grant/QAuthority.bind/InstanceBinding、浏览器/预览/业务Job、Git写均0；原100/25及分额不变。无新账号/token/模板/容量事实。本卡关闭式正常安装不能替代真实Q前置，也不自动放行STEP018/019/020、M1、项目或发布。

报告先写一句结论、连接根因证据、实际改动、六项逐项实际状态和原件导航，区分复用、实际新通过、失败/未跑；再列TASK/R/STEP、实际模型、基线/hash/配置身份、全部失败/修正与实际预算/持有/启动连续账、清场与保留、限制/风险/偏差、待同步文档、必要人工和下一步。若产品修改，给下一隔离独审的稳定差异与原始证据，不给实现聊天/思考过程，不自签独审。

本卡及结果未验收的同范围续作沿用本TASK/R和本结果置顶保留历史；不得改127原结果/原卡/原checkpoint或正式DocuS/公共库。当前唯一人工动作是把卡交原工程窗口、完成带回路径；不要求用户建库/删东西/释放内存/发送秘密。整卡完成或真实停止门到达后保存并复读结果，只回一句结论与D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-128-result.md的可点击绝对路径。
'''.replace('@STAMP@', stamp).replace('@DEADLINE@', deadline).replace('@CHECKS@', str(len(checks)))
    assert '*' not in task and '\n|' not in task
    for required in ['6000', '4800', '10800', 'entry04', '37条', 'READ ONLY', '异常类', '127.0.0.1', 'FROZEN', '002']:
        assert required in task
    registered = f'# 执行动态文档\n\n文档v2.99，2026-10-23，Asia/Shanghai。需求v1.4、架构v1.71。\n\n{stamp}。TASK127/R121已返回验收失败，TASK128/R122已登记，完整卡保存核读中；没有派发/接收事实。\n\n'.encode('utf-8')
    STATE.write_bytes(registered + state_old)
    with CARD.open('xb') as stream:
        stream.write(task.encode('utf-8'))
    assert CARD.read_text(encoding='utf-8') == task
    permit = {
        'TASK': 'TASK-128', 'R': 'R-122', 'issued_at': stamp, 'valid_until': deadline,
        'status': '待人工转交', 'actual_dispatch': False, 'acceptance': None,
        'receiver': 'A+，刚完成127的原125工程窗口',
        'task_card': info(CARD), 'input_manifest': info(OUT / 'input-manifest.json'),
        'restored_scope': info(OUT / 'restored-scope.json'),
        'original_permit_sealed': True, 'old_budget_not_reset': True,
        'tool_restored_seconds': 6000, 'cumulative_tool_cap_seconds': 10800,
        'new_real_entries_max': 3, 'cumulative_entry_cap': 6,
        'new_resources': 0, 'Q': 'FROZEN', 'T0': None, 'real_provider': 0, 'fees_cny': 0,
        'permission_change_outside_existing_approval': False,
    }
    write_json(OUT / 'permit.json', permit)
    receipt = {
        'checked_at': stamp, 'TASK': 'TASK-127', 'R': 'R-121',
        'dispatch': '已返回/停止', 'acceptance': '失败', 'result': result,
        'identity_reference_checks': len(checks), 'mismatches': 0,
        'root_cause_confirmed': False, 'exact_exception_evidence_missing': True,
        'six_complete_passes': 0, 'new_followup': 'TASK-128/R-122',
        'Q': 'FROZEN', 'T0': None, 'orchestrator_runtime': 0,
    }
    write_json(RETURN / 'return-receipt.json', receipt)
    arch_prefix = f'''# 架构动态文档

文档v1.71，2026-10-23，Asia/Shanghai。需求v1.4、执行动态v2.99、task_model/07。以下v1.70原字节保留。

## 正常安装真实连接门失败，受限根因收敛与六项验证接续

{stamp}。127真实创建两个隔离PG/卷/网络并核身份，控制器真实连接可用，正式安装器connect未返回且原异常未留证。安装器/SQL/原权限模型41输入未变；没有源成功安装、002提交未知、角色能力或原生启动通过事实，六项不通过。当前只能定位连接差异，不能把service空串/options等候选判为产品根因。

主控登记128/R122在同身份资源完成先诊断、必要最小连接适配/测试及原六项闭合，保留loopback hostaddr、原目录保护、角色/SQL和提交未知规则。只新增局部连接修复权；不改主要模型/权限/平台。稳定产品若有增量须集中独审实际影响，未变原126结论继承。两个资源不重建，原停止事实按原post时点引用；本轮主控无产品执行或现场资源探针。

原关闭外发采用包预算只显式恢复未用6000秒，原日历和PG/API启动/持有上限不变，入口前向至累计6。Q冻结、T0空、真实费用0，外部计量/账号/token/模板/Embedding容量门保持；STEP018部分验证，019/020/M1/项目/发布未放行。

## 以下为v1.70及更早历史

'''.encode('utf-8')
    ARCH.write_bytes(arch_prefix + arch_old)
    state_prefix = f'''# 执行动态文档

文档v2.99，2026-10-23，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.71、task_model/07。以下v2.98原字节保留。

## TASK127已返回失败，TASK128/R122连接收敛及原六项合并卡待人工转交

{stamp}。用户带回127原结果，主控核{len(checks)}条身份引用零缺失零漂移，报告16765字节/hashe001d7892f3e11581db4731e53242cd007870165c97a7b186496ebb84b3dc73b。127实际接收并运行后已返回/停止，验收失败，原3/3入口封存；不再维持旧待转交状态。两连接失败、四项未到，六项无完整通过，原工具/迁移/41输入及七规则未改。

控制器真实连接查询到两库PG17/vector0.8.6与身份，正式connect各有requested而无returned，写请求0，intent/stopped收据confirmed=[]/unknown_stage=null；这不是002已提交未知。关键缺口是观察层未留脱敏异常，因此正式service空串/options或环境/凭据/夹具只是候选，不先判根因。不再盲重跑、重建或恢复旧127入口。

source实际CID db709b67cc8af398edf1735b0ac6fe365898264326466b2566f904784bfef48d、127.0.0.1:55482/systemid7699647093882925094；interrupted CID 549f36f11827babea930f0338149aa3542e8ea4d3d7cceb67b54b79e25dca8e8、55483/systemid7699647123872251942，OID均16384但独立资源。原post时点两CID Running=false/Pid=0、所选PG/API候选无监听、API0；主控没有现场探针，不假称当下重新停过。卷/网络/根/秘密和失败收据保留。

127精确工具unknown、保守4800/10800秒、PG持有8.117866039276123/1800秒、source1/4/interrupted1/2/API0/3、create各1/1。主控把同采用包未用6000秒显式恢复给新128，含900保存/清场，原截止{deadline}不延长；新入口最多3、累计由3前向至6，源/中断/API启动和持有原上限不增，新容器/卷/网络0。新编号不是额外10800秒或重置失败，旧125/126unknown及120/117全部账照留。

TASK128/R122完整卡DocuN/tasks/TASK-128.md已保存核读，待人工转交A+刚执行127的原125工程窗口，未据保存宣称派发/接收或在途。范围先取得脱敏真实异常并比较同目标连接，允许确定根因后的局部connect适配/保持隔离的帮助和必要测试/说明，继而完成原六项与精确停止。原127纯验证不暗加产品写权；SQL/角色/profile/权限模型/启动器/Compose不改，产品新安全增量稳定后才集中审其直接影响。无并行工作。

Q保持FROZEN、T0/72h空、provider/费用0，100/25与分额/28Must/89动作不变，账号/计量/token/模板/Embedding容量和首次启用未新增。STEP018进行中/部分验证，019/020/M1/项目/发布未验。主控只核文件/原件、维护文档，未导入/运行产品、测试、PG/Docker/API或真实网络。核证/裁定在TASK127/orchestration-return-20261023与work-decision，128范围/输入/许可在orchestration-20261023。CHG1663—1667，下一1668。

## 以下为v2.98及更早历史

'''.encode('utf-8')
    STATE.write_bytes(state_prefix + state_old)
    changes = f'''
- CHG-1663，{stamp}，Codex编排Agent，DocuN/results/TASK-127-work-decision.md。核实际连接失败/停止原件，127验收失败及原额度封存，保留未知根因和原六项缺口，区分历史停止与当前未探测。

- CHG-1664，{stamp}，Codex编排Agent，DocuN/tasks/TASK-128.md。登记128/R122完整根因收敛、受限修复和六项真实闭合合同，A+原工程待人工转交，只恢复同采用包余额、不重置旧账。

- CHG-1665，{stamp}，Codex编排Agent，DocuS/架构动态文档.MD。v1.71登记真实连接阻断与待确认原因、局部连接修复/验证计划，原模型/SQL/权限和Q门不变。

- CHG-1666，{stamp}，Codex编排Agent，DocuS/执行动态文档.MD。v2.99登记127实际已返回/失败、两资源身份/原停止、余额/前向入口及128待转交，保留v2.98历史。

- CHG-1667，{stamp}，Codex编排Agent，DocuN/evidence/TASK-127/orchestration-return-20261023/及TASK-128/orchestration-20261023/。保存有限原件核证、回收回执、旧共享、连续资源/预算scope、输入/许可和读回；产品运行0。
'''.encode('utf-8')
    CHANGE.write_bytes(change_old + changes)
    assert STATE.read_bytes().endswith(state_old) and ARCH.read_bytes().endswith(arch_old)
    assert CHANGE.read_bytes().startswith(change_old)
    assert info(result_path) == result
    for entry in original_manifest['sources']:
        assert info(Path(entry['absolute_path']))['sha256'] == entry['sha256']
    proof = {
        'saved_at': datetime.now(timezone(timedelta(hours=8))).isoformat(), 'TASK': 'TASK-128', 'R': 'R-122',
        'files': [info(path) for path in [CARD, DECISION, STATE, ARCH, CHANGE, OUT / 'permit.json', OUT / 'input-manifest.json', OUT / 'restored-scope.json', RETURN / 'return-check.json', RETURN / 'return-receipt.json']],
        'status': '待人工转交', 'acceptance': None, 'actual_dispatch': False,
        'all_utf8_readable': True, 'old_shared_bytes_preserved': True, 'old127_result_bytes_preserved': True,
        'identity_reference_checks': len(checks), 'mismatches': 0, 'old_budget_reset': False,
        'product_runtime': 0, 'tests': 0, 'live_resource_probes': 0, 'created_resources': 0,
        'next_CHG': 1668,
    }
    for row in proof['files']:
        Path(row['path']).read_text(encoding='utf-8')
    write_json(OUT / 'save-proof.json', proof)
    print(json.dumps({'saved': True, 'TASK': 'TASK-128', 'R': 'R-122', 'checked': len(checks),
                      'mismatches': 0, 'card_bytes': CARD.stat().st_size,
                      'permit_deadline_unchanged': deadline, 'product_runtime': 0}, ensure_ascii=True))


if __name__ == '__main__':
    main()
