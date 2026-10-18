"""登记用户采用决定并保存完整人工转交卡，只操作文档和身份元数据。"""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import hashlib
import json
import re

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent').resolve()
OUT = Path(__file__).resolve().parent
CARD = ROOT / 'DocuN/tasks/TASK-117.md'
WORK116 = ROOT / 'DocuN/results/TASK-116-work-decision.md'
WORK117 = ROOT / 'DocuN/results/TASK-117-work-decision.md'
FINAL = ROOT / 'DocuS/最终需求文档.MD'
ARCH = ROOT / 'DocuS/架构动态文档.MD'
STATE = ROOT / 'DocuS/执行动态文档.MD'
CHANGES = ROOT / 'DocuS/文档变更记录.MD'
DESIGN = ROOT / 'DocuN/evidence/TASK-116/design'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def identity(path):
    raw = path.read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def save(path, obj):
    assert path.resolve().is_relative_to(ROOT)
    assert not path.exists(), str(path)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    assert load(path) == obj


def prefix(path, value, original):
    assert path.resolve().is_relative_to(ROOT)
    assert '*' not in value and not re.search(r'^\|', value, re.MULTILINE)
    path.write_bytes(value.replace('\n', '\r\n').encode('utf-8') + original)
    assert path.read_bytes().endswith(original)


assert OUT.is_relative_to(ROOT)
for path in (OUT, CARD.parent, WORK117.parent, FINAL.parent):
    assert path.resolve().is_relative_to(ROOT)
assert not CARD.exists() and not WORK117.exists()
assert not (ROOT / 'DocuN/results/TASK-117-result.md').exists()
assert not (OUT / 'adoption-receipt.json').exists()
old = {p: p.read_bytes() for p in (WORK116, FINAL, ARCH, STATE, CHANGES)}
assert '基线 v1.2' in old[FINAL].decode('utf-8-sig').splitlines()[2]
assert '文档v1.33' in old[ARCH].decode('utf-8-sig').splitlines()[2]
assert '文档v2.57' in old[STATE].decode('utf-8-sig').splitlines()[2]
numbers = [int(x) for x in re.findall(r'^- CHG-(\d+)', old[CHANGES].decode('utf-8-sig'), re.MULTILINE)]
assert numbers[-1] == 1390 and 1391 not in numbers
contract = (OUT / 'effective-contract.md').read_bytes()
text = contract.decode('utf-8-sig')
assert '*' not in text and not re.search(r'^\|', text, re.MULTILINE)
for value in ('TASK-117 / R-111', 'S01', '目标与交付', '项目、规则、批准与接收安排',
              '最小充分输入与对象身份', '采用后的工程合同', '允许写入', '精确资源profile',
              '时间、批次与次数上限', '验证目的、样本、证据与复用', '集中独审',
              '结果、保存复读与必要人工', '28800', '14400', '7200',
              '一并批准', '真实供应商调用/费用均0', '80次/人民币20元', '15485'):
    assert value in text, value

prior = load(ROOT / 'DocuN/evidence/TASK-116/orchestration-receipt-20261014/received.json')
prior_save = load(ROOT / 'DocuN/evidence/TASK-116/orchestration-receipt-20261014/save-proof.json')
known_main_forward = {str(Path(row['path'])): row for row in prior_save['files']}
protected = dict(prior['protected'])
for name, expected in protected.items():
    assert identity(ROOT / name) == expected, name
source_pre = []
for row in prior['sources']:
    p = Path(row['path'])
    if not p.is_absolute():
        p = ROOT / p
    actual = identity(p)
    if str(p) in known_main_forward and p in old:
        known = known_main_forward[str(p)]
        assert actual == {k: known[k] for k in ('bytes', 'sha256')}, str(p)
        source_pre.append({'path': row['path'], **actual, 'basis': '116回收后主控前向裁定/正式版本，当前身份精确匹配既有save-proof，不当产品漂移'})
        continue
    assert actual == {k: row[k] for k in ('bytes', 'sha256')}, str(p)
    source_pre.append({'path': row['path'], **actual, 'matches_design_source': True})
    if p.is_relative_to(ROOT):
        protected[p.relative_to(ROOT).as_posix()] = actual
rules = load(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
for row in rules:
    assert identity(Path(row['absolute_path']))['sha256'] == row['sha256']

at = datetime.now(timezone(timedelta(hours=8))).isoformat()
backup = OUT / 'before-documents'
backup.mkdir(exist_ok=False)
for p, raw in old.items():
    target = backup / p.name
    target.write_bytes(raw)
    assert target.read_bytes() == raw

adoption = {
    'schema': 'TASK117.user-adoption.v1', 'recorded_at': at,
    'user_statement': '一并批准',
    'binding_context': '编排展示AP1新增数据/接口/权限与AP2后续仅合成DeepSeek/智谱合计80次20元、独审及核价条款后启用，用户明确同时批准',
    'package_path': 'DocuN/evidence/TASK-116/design/adoption-package.md',
    'package_sha256': identity(DESIGN / 'adoption-package.md')['sha256'],
    'prior_main_decision': {
        'path': 'DocuN/results/TASK-116-work-decision.md',
        **identity(WORK116)
    },
    'AP1': {
        'adopted': True, 'migration': '014_step018_retrieval.sql',
        'new_tables': ['retrieval_spaces', 'retrieval_commands', 'retrieval_chunks'],
        'new_activity_column': 'outbound_grant_sha256 nullable',
        'new_kind': 'embedding', 'protocol': 'v4 typed union, old v3 retained',
        'profiles': ['learning.v2', 'teaching.v3', 'interview.v2', 'data_exit.v1.r02'],
        'R01_and_original_migrations': '001—013原字节与原包/有限验收保留',
        'restore_execution': False
    },
    'AP2': {
        'conditionally_authorized': True, 'activated': False,
        'providers': ['deepseek_chat_completions/deepseek-chat candidate', 'zhipu_embeddings/embedding-3/512 candidate'],
        'data_class': 'frozen_synthetic_necessary_fragments_only',
        'max_total_requests': 80, 'max_total_cost_CNY': 20,
        'cost_microunits_per_yuan': 1000000, 'reserve_per_call_microunits': 250000,
        'includes_failed_timeout_unknown': True, 'implicit_retries': 0,
        'activation_conditions': [
            '稳定新增kind/权限/预算/数据profile完整候选独立审计可用结论',
            '官方现行能力/模型别名/维度/计价/条款及必要账号条件核对',
            '保守最坏单次费用含必要边界/25%裕量不超预留',
            '主控Q启用回执和受信固定roster OutboundGrant'
        ],
        'validity_from_future_explicit_activation_hours': 72,
        'real_user_data_or_databases': False,
        'new_spend_or_provider_calls_now': 0,
        'old_13_CNY_reused': False
    },
    'no_repeat_permission_for': '已批准范围内实施/合成验证/普通修复及未来满足条件的20元额度',
    'not_authorized': ['个人资料外发', '用户库迁移/写入', '新供应商/维度/服务', '部署发布', '真实付费早于条件', '旧额度重置'],
    'dispatch_state': 'not_transferred_or_received'
}
save(OUT / 'adoption-receipt.json', adoption)

permit = {
    'TASK': 'TASK-117', 'R': 'R-111', 'STEP': '018',
    'permit': 'TASK-117-STEP018-INTEGRATION-S01-20261014', 'issued_at': at,
    'current_phase': 'S01_synthetic_complete_candidate', 'Q_active': False,
    'adoption_receipt_sha256': identity(OUT / 'adoption-receipt.json')['sha256'],
    'current_active_seconds_max': 28800, 'save_cleanup_reserve_seconds': 1800,
    'no_expand_after_active_seconds': 25200, 'cleanup_only_after_active_seconds': 27000,
    'calendar_from_actual_receipt_hours': 72, 'actual_received_at': None,
    'active_clock_first_tool_utc_and_mono': '接收者实采，不以签发替代；漏点保守扣时',
    'real_runtime_and_holding_seconds_max': 14400, 'offline_checks_and_build_seconds_max': 7200,
    'complete_target_roots_total_max': 8, 'S_roots_max': 7,
    'PG_successful_physical_objects_max': 5, 'PG_create_attempts_max': 8,
    'PG_volumes_max': 5, 'PG_start_attempts_max': 20,
    'API_start_attempts_max': 8, 'main_browser_lifetimes_max': 8,
    'frontend_build_max': 3, 'Windows_Native_SUP_sessions_max': 160,
    'dynamic_preview_create_attempts_max': 12, 'dynamic_preview_start_attempts_max': 12,
    'HTTP_max': 3000, 'official_document_pages_max': 10,
    'current_provider_calls_and_fee_max': 0,
    'same_time_limits': {'PG': 2, 'preview': 1, 'API': 1, 'main_browser': 1},
    'free_physical_memory_GiB_before_each_dependent_start_min': 2,
    'new_paid_authorization_preserved_not_active': {'requests_total': 80, 'CNY_total': 20},
    'used_at_issuance': 0, 'execution_started': False, 'dispatch_confirmed': False,
    'old_budgets': '原TASK/失败/费用/时间/UNKNOWN各原账保留，余额不继承执行权',
    'scope': '见完整任务卡；实施、合成各层验证和普通修复连续完成，稳定后集中独审'
}
save(OUT / 'execution-permit.json', permit)

profile = {
    'schema': 'TASK117.synthetic-resource-profile.v1', 'issued_at': at,
    'PG_image': 'sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f',
    'PG_limits': {'CPU': 1, 'memory_MiB': 512, 'pids': 128, 'restart': 'no', 'bind': '127.0.0.1', 'pull': 'never'},
    'PG_objects': [
        {'role': role, 'name': f'retrolume-step018-syn-{suffix}',
         'volume': f'retrolume-step018-syn-{suffix}-data', 'port': port,
         'database': database, 'CID': None, 'used': False}
        for role, suffix, port, database in (
            ('normal_source', 'source', 15481, 'step018_syn'),
            ('nonempty_upgrade_compat', 'compat', 15482, 'step018_compat'),
            ('permanent_readonly_R01', 'r01', 15483, 'step018_r01'),
            ('permanent_readonly_R02', 'r02', 15484, 'step018_r02'),
            ('failed_R02_target_only_if_required', 'r02-fault', 15485, 'step018_r02_fault'))
    ],
    'fifth_object_reason': '独立P03 failed对象不可复用为成功只读目标；优先预检拒绝，确需才创建，避免卡面结构性缺slot',
    'API': {'host': '127.0.0.1', 'port': 18118, 'mode': 'Windows hidden Selector uvicorn', 'PID_birth': None},
    'preview': {
        'image': 'sha256:ec3c70c7a8a8894c647a69b08b0c296727bb052f639e487567e9cd4624766789',
        'load_sha256': '8a047050ffe584dffa6e85222c16c8f400c0ab4db82f72a32812c2befd082b3f',
        'renderer_entry_sha256': '6cc300164a6cb364d9bd0bae4897f06d3f6a65cf5d4272477d2bccde67312597',
        'normal_verified_ticket_required': True, 'reuse_old_runtime_objects': False
    },
    'runtime_metadata_and_memory_ports_cache': '未由主控运行Docker/socket核查；执行者在每次实际启动前实时核门',
    'new_objects_created_by_orchestration': 0,
    'cleanup': '只精确停止本卡自有资源，保留全部卷/库/镜像/失败，用户进程和Docker daemon不动'
}
save(OUT / 'resource-profile.json', profile)

window = {
    'TASK': 'TASK-117', 'R': 'R-111', 'grade': 'A+增强执行',
    'continue_window': 'TASK116/原TASK114工程窗口',
    'last_reported_identity': 'Codex desktop / 系统GPT-6；后端子型号未披露',
    'reason': '主要持久模型/迁移/新能力/权限/R02与全栈两链集成难度高，原窗有效上下文可复用',
    'independent_auditor': False, 'sub_agents': False, 'parallel_product_writer': False,
    'manual_handoff': True, 'transferred': False, 'received': False,
    'future_independent_audit': '稳定完整S候选后新隔离增强窗口集中审新边界，主控另卡，不提前占号'
}
save(OUT / 'window-assignment.json', window)

work116 = f'''# TASK116/R110 — AP1/AP2采用决定已生效

{at}。用户对主控已展示的AP1与AP2明确回复“一并批准”。采用014/受控Embedding/hybrid/新领域profile/可选低信任面试记忆/R02保R01及新增grant归属；后续真实服务仅冻结合成必要片段，DeepSeek/智谱候选合计80次/人民币20元新总额，失败/UNKNOWN在内。原v1.3需求采用段和本回执记录范围，不追认任何实现或收费已经发生。

AP1可进入完整工程合成实施，下一TASK117/R111已正式编号。AP2是条件性许可，不再向用户重复请付费批准；实际启用仍晚于新增边界稳定独审、官方现行能力/价格/条款及最坏费用核对、账号/安全配置条件和主控Q回执。72小时从未来grant生效算；当前S01真实provider调用/费用0，不含个人资料/用户库或发布。

TASK116设计交付验收通过维持。其原结果/设计文件“待采用”历史不改，以下原裁定和预算保留；旧13元/失败/UNKNOWN不借。完整新实施卡为DocuN/tasks/TASK-117.md，原A+工程窗，人工转交未确认接收。真实采用回执及对应文件hash在DocuN/evidence/TASK-117/orchestration-20261014/adoption-receipt.json。

## 以下为原设计验收及许可历史

'''
prefix(WORK116, work116, old[WORK116])

work117 = f'''# TASK117/R111 — 完整学习与面试集成S01实施许可

{at}，Codex编排Agent。用户已同时批准116 AP1/AP2，按当前task_model/07在同一原A+工程窗口连续交一个完整S合成集成候选，包含必要官方文档核查、014/新kind/wire/profile、两链UI、R02传播、同正常库重开、本机启动文档、分层验证和普通修复。不是再次只读设计、单项准备卡或旧失败循环。

许可TASK-117-STEP018-INTEGRATION-S01-20261014，活动28800含1800清场/72h日历；runtime/holding14400、offline7200、根总8且S最多7。PG对象5/create8/volume5/start20，API8、Browser8、build3、Native160、preview create/start12、HTTP3000；每活动原preview3次180秒不变，同在PG2/API1/browser1/preview1。第五个独立fault target只在P03必需时建，解决失败对象保留与成功目标不可复用的草案slot不足，未改变产品/费用/并发门。所有上限不是要求耗满。

AP2最大80次/20元条件性许可已记录，未来Q独审/官方事实/账号条件/价格保守上界/主控启用未满足前真实API调用和费用0；官方只读核查最多10页可在本卡进行，非新增调研卡或主控接管。缺官方能力只停其依赖部分，工程普通决策自主处理，真实私密不进聊天/证据。没有用户库迁移/个人资料外发、下载安装/pull、新image/Git写或公开发布权限。

原114/115/116充分原件复用，原背景和所有失败/时间/超限/13元/UNKNOWN保留，不reset/stash覆盖历史。两项解释沿原116裁定，失效后不新增received正文/向量；向量hash须实际存储/007/R02往返一致。旧tool NULL/零费用及R01原链保护，两个恢复profile永久只读，新活动不能重绑grant清费用。

接收安排为TASK116/原TASK114工程窗，实际型号如实记录，无子Agent/并行产品写者。稳定S成果完成精确清场交回，再由新隔离增强窗口集中独审；S工程不得自签。原窗未来Q只补真实合成语义及实际影响，原独审只增量，不重新整仓验证；STEP018/019/020/M1/项目均未裁定通过。

当前完整卡保存复读后为待人工转交，不等于已派发/已接收；签发新增用量全0、无运行资源，现场缓存/内存/端口待执行者实际启动前核，不借主控签发时采样。唯一执行结果DocuN/results/TASK-117-result.md，execution子目录单账和case-index；正式DocuS/共享编号/最后验收仍主控维护。任务普通步骤/测试/修复在卡内完成，关键门或两次有据修正仍失败/投入上限才交回。
'''
WORK117.write_bytes(work117.replace('\n', '\r\n').encode('utf-8'))
assert WORK117.read_text(encoding='utf-8-sig').startswith('# TASK117/R111')

final_text = f'''# 最终需求文档

需求与实现验收基线 v1.3，2026-10-14，Asia/Shanghai。用户对STEP018 AP1/AP2明确“一并批准”，新增采用边界如下。原31项需求编号/优先级/Must及v1.2全文保留，原始需求文件不改。

## 已采用的集成与有限合成外发增量

依据TASK116完整合同及本次主控回执，采用受控Embedding/同空间精确向量与词项融合、对应新持久检索记录/调用kind/协议、R02前向profile兼容R01及旧数据。面试新v2可在创建时显式选取有限学习记忆作为低信任背景，不当履历/测量证据；旧v1有限验收与禁记忆语义保持。具体014/公开接口/角色/不可重绑grant及工程细节归架构与TASK117合同，不改原功能质量标准。

用户同时条件性允许后续仅冻结合成资料必要片段调用DeepSeek chat/智谱embedding候选，两个供应商合计最多80次、人民币20元新总额，含失败/超时/UNKNOWN。新增边界稳定独审、官方现行能力/价目/条款及最坏单次费用核对、账号和安全配置就绪、主控Q启用回执后方生效；当前真实费用0，72小时从未来grant启用起算。原13元/已用失败不折回，不向对话索密钥，不含真实履历/用户资料/用户库或发布授权。

正常同一持久库重开、先读事实再明确继续仍是集成目标；R01/R02恢复副本仍永久只读，采用新profile不授副本执行权。全部适用Must及真实服务语义、集中独审、最终自用交接仍需实际证据，不因本次采用宣告通过。采用来源DocuN/evidence/TASK-117/orchestration-20261014/adoption-receipt.json，唯一总状态仍执行动态文档。

## 以下为v1.2及更早批准原文

'''
prefix(FINAL, final_text, old[FINAL])

arch_text = f'''# 架构动态文档

文档v1.34，2026-10-14，Asia/Shanghai。需求v1.3、执行动态v2.58、task_model/07；以下v1.33历史原字节保留。

## STEP018 AP1/AP2已采用，完整工程S01待人工转交

{at}。用户明确“一并批准”。AP1为014三检索表及活动grant摘要、新embedding kind/typed gateway/OneCall v4兼容v3、同空间精确cosine和词项RRF、learning.v2/teaching.v3/interview.v2及低信任可选面试记忆、R02精确001—014/profile/角色/清理/恢复。原001—013/model/tool/旧profile/hash/R01包保持，旧tool空token/request和零费用分支不能被新约束伤及。新真实grant受信create不可重绑，model/embedding共享PG跨固定活动预留门和每活动原四账。

当前仅采用/允许实施，不冒上述机制已实现。晚到/失效严格沿原UNKNOWN与正文资格，向量hash须实际存储表示/007/数据库回读/R02恢复一致。新表owner/app/loader/snapshot/seal/purge权限按精确registry，未识别DDL不宽松容忍。正常同库重开明确继续与永久只读恢复分开，恢复不继承执行权/秘密。

AP2条件性允许仅冻结合成片段、两候选供方合计80次/20元新总额；新增边界集中独审、官方现行能力/条款/价格/账号条件及最坏费用核对和Q回执前不激活。当前S01真实供应商调用/费用0，可有限读官方页面作输入。无个人资料/用户库迁移/新供应商或公开发布权限，旧13元/UNKNOWN不清。

TASK117一张完整工程卡在原A+窗口连续完成S合成候选/普通修复，稳定后集中独审。Windows API/SUP/Job和既有Compose PG/动态v2-08预览继续，不建常驻renderer/Redis业务依赖/新框架，不给Web Docker socket；Linux/Nginx完整公开交付仍后续条件范围。前置有限STEP017/G11等验收保持，STEP018—020及M1/项目未通过。

## 以下为v1.33及更早历史

'''
prefix(ARCH, arch_text, old[ARCH])

reservation = f'''# 执行动态文档

文档v2.58，2026-10-14，Asia/Shanghai。唯一总状态账；需求v1.3、架构v1.34、task_model/07。以下v2.57历史原字节保留。

## TASK117/R111已占号，用户AP1/AP2批准已登记

{at}。主控先登记新完整集成成果TASK117/R111；许可S01，当前卡保存中，未转交/接收/执行。用户“一并批准”AP1/AP2，真实付费仍需独审/核价条款与Q启用门。完整正式状态在保存复读后填写，不将占号写已派发。旧成果/失败/预算全部保留。

## 以下为v2.57及更早历史

'''
prefix(STATE, reservation, old[STATE])
CARD.write_bytes(contract)
assert CARD.read_bytes() == contract

state_text = f'''# 执行动态文档

文档v2.58，2026-10-14，Asia/Shanghai。唯一总状态账；需求v1.3、架构v1.34、task_model/07。以下v2.57历史原字节保留。

## AP1/AP2用户已批准，TASK117完整集成S01待人工转交

{at}。用户对主控所列AP1与AP2明确“一并批准”，有效回执绑定116采用包84cb852946220a09873225f8bde7b7138aa7366e137297638bb2aab01dbc1c84。TASK116设计已验收维持；采用新014/检索表/grant列、新embedding kind/typed wire/profile/hybrid/低信任面试记忆及R02保R01。需求v1.3只新增采用边界，原31项/Must与历史不改，不冒实现完成。

TASK117/R111已先占号再保存完整卡并复读，待人工转交，未派发/接收/执行；原A+ TASK116/114工程窗口连续完成S01合成集成候选与普通修复，不派子Agent，不借独审窗。完整目标包括两条业务链、真实PG/Windows/HTTP/最终bundle/正常同库重开、R01/R02只读恢复、本机启动文档及失败传播，不拆准备/跑单项/修夹具卡。未回结果不由主控接管。

用户AP2额度是合计80次/20元、仅冻结合成必要片段的新条件性批准，含失败/UNKNOWN；不再重复问费用批准。新增边界稳定独审、官方现行能力/模型/价目/条款/账号和最坏费用核对、主控Q回执前真实provider调用和费用0。官方必要只读最多10页在本卡可做，非主控产品执行。72小时从未来grant实际生效算，不借旧13元、换活动或换grant清账；无本人资料/用户库或发布权限。

S01许可TASK-117-STEP018-INTEGRATION-S01-20261014，接收活动28800含1800清场/72h日历、runtime及持有14400/offline7200、完整根总8/S最多7。PG物理成功5/create8/卷5/start20，API8/Browser8/build3/Native160/preview create-start12/HTTP3000，同在PG2/API1/browser1/preview1，实际依赖启动前内存2GiB门。第五fault target按P03失败对象保留不可复用成功目标的需要补齐，其它技术/并发/费用门不扩；全部是新成果上限非要求跑满。签发用量0，runtime cache/端口/内存未实查，执行前核实时门。

完整S候选后精确停机/封存交主控安排新隔离集中独审，Q原工程窗只在条件就绪后接续并保本TASK原计数/剩额；候选和实际Q语义分级，未放行部分不冒通过。随后STEP018全Must、STEP019整体安全/一致性、STEP020本人自用交接按前置裁定。TASK118未占号，不预生成依赖未满足的卡。

原114/115有限STEP017、G11及其准确数据/停止/权限范围继续有效；旧31资源/全部原根、时间、失败、超限、G11/25/UNKNOWN/R60/count1/13元/626.566封存，不因新TASK清零。只读恢复副本永不开写，正常重开新执行资格另核。主控本轮仅读文件/身份和维护文档，未启动Docker/DB/Browser/API或测试、无外发/费用/Git写，旧卷和个人成果不动。

回执/许可/精确资源/窗口/输入/旧共享/完整卡及保存证明在DocuN/evidence/TASK-117/orchestration-20261014，执行结果预定DocuN/results/TASK-117-result.md尚不存在。CHG1391—1404，下一1405。原始需求、原任务结果/证据、公共库、产品未改。

## 以下为v2.57及更早历史

'''
prefix(STATE, state_text, old[STATE])

entries = [
    ('DocuN/evidence/TASK-117/orchestration-20261014/adoption-receipt.json', '用户一并批准AP1/AP2的真实范围及hash；仅合成20元条件性许可，当前未启用。'),
    ('DocuN/results/TASK-116-work-decision.md', '设计验收后记录用户采用，原待决/预算历史原字节保留。'),
    ('DocuN/results/TASK-117-work-decision.md', '完整S工程实施许可、一次集中独审与Q分界、无重复费用审批。'),
    ('DocuS/最终需求文档.MD', 'v1.3采用增量、原31项/Must与v1.2保留，不修改原始需求。'),
    ('DocuS/架构动态文档.MD', 'v1.34具体014/新类型/profile/权限及旧兼容采用，尚未实现。'),
    ('DocuS/执行动态文档.MD', 'v2.58先占号后完整卡保存复读待转交，真实执行全0、旧账保留。'),
    ('DocuN/tasks/TASK-117.md', '原A+工程窗完整S集成/分层验证/普通修复卡；不预占下一独审卡。'),
    ('DocuN/evidence/TASK-117/orchestration-20261014/execution-permit.json', 'S01时间/根/子次数和费用启用门，签发不冒接收。'),
    ('DocuN/evidence/TASK-117/orchestration-20261014/resource-profile.json', '精确五对象含必要独立fault slot、缓存/端口/限制及保留清场。'),
    ('DocuN/evidence/TASK-117/orchestration-20261014/input-manifest.json', '实际当前关键读入和正式版本，最小源身份继承，不全仓重验。'),
    ('DocuN/evidence/TASK-117/orchestration-20261014/window-assignment.json', '继续116/原114 A+工程窗、人工转卡状态与未来隔离独审。'),
    ('DocuN/evidence/TASK-117/orchestration-20261014/before-documents', '原五共享文件完整原字节留档，不改执行者结果/旧证据。'),
    ('DocuN/evidence/TASK-117/orchestration-20261014/contract-check.json', '一次卡面/前置/授权/阶段/路径/身份/预算一致性静态核对，不运行产品。'),
    ('DocuN/evidence/TASK-117/orchestration-20261014/delivery-proof.json', '完整卡和配套保存复读、CHG连续与原保护对象不变。'),
]
tail = ''.join(f'\r\n- CHG-{1391+i}，{at}，Codex编排Agent，{path}。{detail}\r\n'
               for i, (path, detail) in enumerate(entries))
CHANGES.write_bytes(old[CHANGES] + tail.encode('utf-8'))
assert CHANGES.read_bytes().startswith(old[CHANGES])
new_numbers = [int(x) for x in re.findall(r'^- CHG-(\d+)', CHANGES.read_text(encoding='utf-8-sig'), re.MULTILINE)]
assert new_numbers == numbers + list(range(1391, 1405))

inputs = [ROOT / 'AGENTS.md', FINAL, ARCH, STATE, WORK116, WORK117, CARD,
          ROOT / 'DocuN/results/TASK-116-result.md',
          ROOT / 'DocuN/results/TASK-115-result.md', ROOT / 'DocuN/results/TASK-112-result.md']
inputs.extend(DESIGN / n for n in (
    'integration-contract.md', 'acceptance-contract.md', 'sample-inputs.json',
    'adoption-package.md', 'actual-call-map.json', 'source-identities.json',
    'sample-identities.json', 'git-baseline.json', 'consistency.json'))
save(OUT / 'input-manifest.json', {
    'issued_at': at, 'purpose': '117当前有效前置、批准与源身份，非产品通过',
    'formal_versions': {'requirements': 'v1.3', 'architecture': 'v1.34', 'execution': 'v2.58'},
    'inputs': [{'path': str(p), **identity(p)} for p in inputs],
    'design_source_pre': source_pre, 'locked_rules': rules,
    'baseline_full_current_manifest_reference': 'DocuN/evidence/TASK-116/orchestration-20261014/input-manifest.json',
    'rehashed_entire_243': False,
    'allowed_write_pre': '接收者按卡面首次实际编辑文件逐个核身份/pre副本，未触及文件不全量复制',
    'old_git_HEAD': '45951501d2741630a229762d6b2d3f4b34d7f702',
    'original_dirty_status': '设计读取633行原件继承，新的共享文档差异不冒旧身份',
    'runtime_metadata': '执行者每次启动前实时核，主控未查现cache/内存/端口'
})

# 正式文档是本次明确写对象；其余读入保护必须维持。
for p in (WORK116, FINAL, ARCH, STATE, CHANGES):
    protected.pop(p.relative_to(ROOT).as_posix(), None)
for name, expected in protected.items():
    assert identity(ROOT / name) == expected, name
for row in rules:
    assert identity(Path(row['absolute_path']))['sha256'] == row['sha256']
assert not (ROOT / 'DocuN/tasks/TASK-118.md').exists()

save(OUT / 'contract-check.json', {
    'checked_at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
    'document_consistency_only': True,
    'metadata_publication_failure_preserved': 'publication-attempt-01.json；首次预检未区分116设计读入时的Work与已登记主控前向裁定，未写卡/正式文档。修正为既有save-proof精确匹配，不忽略未知漂移。',
    'one_complete_deliverable': 'S完整合成候选包含28场景适用层，Q已批准有明确独审后启用门',
    'card_exact_saved': CARD.read_bytes() == contract,
    'all_required_contract_sections_present': True,
    'new_text_no_stars_or_tables': True,
    'user_adoption_AP1_AP2_registered': True, 'Q_not_active': True,
    'rules_match': len(rules), 'current_source_pre_record_count': len(source_pre),
    'protected_unchanged': len(protected),
    'prior_histories_suffix_preserved': all(p.read_bytes().endswith(raw) for p, raw in old.items() if p != CHANGES),
    'change_history_prefix_preserved': CHANGES.read_bytes().startswith(old[CHANGES]),
    'proper_failed_target_slot': '第五独立目标只在P03必须时建立，不复用失败或sealed目标',
    'TASK_reserved_before_card_save': True, 'dispatch': 'pending_manual_handoff',
    'current_counters': 0, 'product_services_tests_network_fees_git_writes': 0,
    'actual_resource_runtime_preflight': 'not_run_by_orchestrator; future executor before each startup',
    'CHG': list(range(1391, 1405))
})
save(OUT / 'delivery-proof.json', {
    'saved_at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
    'TASK': 'TASK-117', 'R': 'R-111', 'status': 'saved_readable_pending_manual_handoff',
    'grade': 'A+', 'window': 'continue TASK116/original TASK114 engineering',
    'files': [{'path': str(p), **identity(p)} for p in (
        CARD, WORK116, WORK117, FINAL, ARCH, STATE, CHANGES,
        OUT / 'adoption-receipt.json', OUT / 'execution-permit.json',
        OUT / 'resource-profile.json', OUT / 'input-manifest.json', OUT / 'window-assignment.json',
        OUT / 'contract-check.json')],
    'histories_preserved': True, 'protected_count': len(protected),
    'source_and_evidence_unchanged': True, 'current_executions': 0,
    'AP1_adopted': True, 'AP2_conditionally_authorized': True, 'Q_activated': False,
    'last_CHG': 1404
})
print(json.dumps({'status': 'SAVED_AND_READABLE_PENDING_MANUAL_HANDOFF',
                  'card': str(CARD), **identity(CARD), 'TASK': '117', 'R': '111',
                  'requirements': 'v1.3', 'architecture': 'v1.34', 'execution': 'v2.58',
                  'last_CHG': 1404, 'AP1': 'adopted', 'AP2': 'conditional_80_requests_20_CNY',
                  'current_Q_calls_fee': 0, 'product_execution': 0}, ensure_ascii=False))
