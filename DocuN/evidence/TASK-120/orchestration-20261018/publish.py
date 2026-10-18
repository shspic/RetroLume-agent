"""登记已批准增量与新完整工程卡。仅文档、标准库hash/JSON，不运行产品。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
assert ROOT == Path('D:/shspic/project_NO3_RetroLume-agent').resolve()
assert not (HERE / 'save-proof.json').exists(), '已有保存证明，不重复发布'


def h(raw):
    return hashlib.sha256(raw).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def ident(path):
    if not path.is_file():
        return {'exists': False, 'bytes': 0, 'sha256': None}
    raw = path.read_bytes()
    return {'exists': True, 'bytes': len(raw), 'sha256': h(raw)}


def write(path, content, new=False):
    assert path.resolve().is_relative_to(ROOT), str(path)
    raw = content.encode('utf-8') if isinstance(content, str) else content
    raw.decode('utf-8-sig')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb' if new else 'wb') as stream:
        stream.write(raw)
    assert path.read_bytes() == raw


def save_json(name, content):
    write(HERE / name, json.dumps(content, ensure_ascii=False, indent=2) + '\n', True)


now = datetime.now(timezone(timedelta(hours=8))).isoformat()
proposal = ROOT / 'DocuN/evidence/TASK-119/orchestration-acceptance-20261018/adoption-proposal.md'
report = ROOT / 'DocuN/results/TASK-119-result.md'
assert ident(proposal)['sha256'] == '394dfae437dd416770104425aefc5386a95420edd4a3ef07dfa029bcd330db8f'
assert ident(report)['sha256'] == '2d10d08bf2d16ff136258b122d93d12747b659744a4ae5c6036d348806096346'
rules = load(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
for row in rules:
    assert ident(Path(row['absolute_path']))['sha256'] == row['sha256'], row['absolute_path']
for row in load(ROOT / 'DocuN/evidence/TASK-119/design/input-identities.json')['inputs']:
    path = Path(row['path'])
    if row.get('exists') is False:
        assert not path.exists(), str(path)
    else:
        assert ident(path)['bytes'] == row['bytes'] and ident(path)['sha256'] == row['sha256'], str(path)

state = ROOT / 'DocuS/执行动态文档.MD'
arch = ROOT / 'DocuS/架构动态文档.MD'
requirements = ROOT / 'DocuS/最终需求文档.MD'
changes = ROOT / 'DocuS/文档变更记录.MD'
work119 = ROOT / 'DocuN/results/TASK-119-work-decision.md'
card = ROOT / 'DocuN/tasks/TASK-120.md'
draft = HERE / 'task-contract.md'
assert not card.exists(), '120已存在，先核对真实归属'
assert '文档v2.72' in state.read_text(encoding='utf-8-sig').splitlines()[2]
assert '文档v1.45' in arch.read_text(encoding='utf-8-sig').splitlines()[2]
assert 'v1.3' in requirements.read_text(encoding='utf-8-sig').splitlines()[2]
assert max(map(int, re.findall(r'CHG-(\d+)', changes.read_text(encoding='utf-8-sig')))) == 1508
before = {p: p.read_bytes() for p in [state, arch, requirements, changes, work119]}
text = draft.read_text(encoding='utf-8')
for token in ['TASK-120 / R-114', '零外发', 'K1', 'K2', '96小时', '14400', '10800',
              '48次', '28次', '24次', '99临界', '47／28／24', '根入口8', 'Browser start8',
              '512MiB', '768MiB', '独立增强审计', '停止', 'TASK-120-result.md']:
    assert token in text, token
assert '*' not in text and not any(line.lstrip().startswith('|') for line in text.splitlines())
contract = draft.read_bytes()

product_paths = set()
for rel in ['backend/app', 'backend/tests']:
    product_paths.update(p for p in (ROOT / rel).rglob('*.py') if p.is_file())
for rel in ['frontend/src', 'frontend/tests']:
    product_paths.update(p for p in (ROOT / rel).rglob('*') if p.is_file() and p.suffix in {'.ts', '.tsx', '.js', '.mjs', '.css', '.html'})
product_paths.update((ROOT / 'backend/migrations').glob('*.sql'))
product_paths.update((ROOT / 'config').glob('*.example.json'))
product_paths.update((ROOT / 'deploy').glob('*.py'))
product_paths.update((ROOT / 'deploy').glob('*.ps1'))
for rel in ['AGENTS.md', 'README.md', '.gitignore', 'start-local.cmd', 'deploy/compose.local.yml',
            'backend/requirements.txt', 'backend/requirements.lock', 'frontend/package.json', 'frontend/package-lock.json']:
    path = ROOT / rel
    if path.is_file(): product_paths.add(path)
dist = ROOT / 'frontend/dist'
if dist.is_dir():
    product_paths.update(p for p in dist.rglob('*') if p.is_file())
for path in product_paths:
    assert path.resolve().is_relative_to(ROOT), str(path)
product_baseline = [{'relative_path': str(p.relative_to(ROOT)).replace('\\', '/'), 'path': str(p), **ident(p)}
                    for p in sorted(product_paths, key=str)]

protected_paths = set(product_paths)
protected_paths.update((ROOT / 'DocuN/evidence/TASK-119/design').iterdir())
protected_paths.update([proposal, report, ROOT / 'DocuN/tasks/TASK-119.md',
                        ROOT / 'DocuN/results/TASK-117-result.md', ROOT / 'DocuN/results/TASK-118-result.md',
                        ROOT / 'DocuN/evidence/TASK-117/execution/budget.json',
                        ROOT / 'DocuN/evidence/TASK-117/execution/events.jsonl',
                        ROOT / 'DocuS/原始需求文档.MD'])
protected_paths.difference_update(before)
protected = {p: ident(p) for p in protected_paths}
old_budget = load(ROOT / 'DocuN/evidence/TASK-117/execution/budget.json')
assert old_budget['active_root'] is None and old_budget['phase'] == 'S08_returned_engineering_candidate'
assert old_budget['counts']['roots'] == 25 and len(old_budget['failures']) == 81
assert old_budget['counts']['provider_calls'] == 0 and old_budget['counts']['actual_fee_microunits'] == 0

backup = HERE / 'before-documents'
backup.mkdir(exist_ok=False)
for path, raw in before.items():
    write(backup / path.name, raw, True)

roster = [
    {'activity_id': '01800000-0000-4000-8000-000000000001', 'role': 'learning', 'max_requests': 48, 'max_cost_microunits': 12000000},
    {'activity_id': '01800000-0000-4000-8000-000000000002', 'role': 'interview', 'max_requests': 28, 'max_cost_microunits': 7000000},
    {'activity_id': '01800000-0000-4000-8000-000000000003', 'role': 'supplement', 'max_requests': 24, 'max_cost_microunits': 6000000},
]
assert sum(x['max_requests'] for x in roster) == 100
assert sum(x['max_cost_microunits'] for x in roster) == 25000000
adoption = {
    'recorded_at': now, 'source': '当前主控聊天，用户在完整三项增量提案后明确回复“批准”',
    'user_exact_text': '批准', 'proposal_path': str(proposal), 'proposal_sha256': ident(proposal)['sha256'],
    'design_path': str(report), 'design_sha256': ident(report)['sha256'],
    'adopted': ['zero_DDL_Q_v2_exact_local_operator_approval_and_original_key_continue',
                'candidate_deepseek_flash_thinking_disabled_same_endpoint_and_caps',
                'one_future_conditional_Q_100_requests_25_CNY_roster_48_28_24'],
    'clarifications': ['K1_non_self_referential_approval_id', 'K2_shared_policy_release_before_result_write'],
    'global_max_requests': 100, 'global_max_cost_microunits': 25000000, 'reserve_per_request_microunits': 250000,
    'roster': roster, 'old_80_20_superseded_before_first_activation_not_added': True,
    'Q_activated': False, 'valid_from_utc': None, 'valid_until_utc': None, 'activation_receipt': False,
    'candidate_adoption_is_not_capability_or_account_or_price_verification': True,
    'TASK120_provider_calls_cap': 0, 'TASK120_actual_fee_microunits_cap': 0,
    'original_S_closed_and_historical_control_failures_preserved': True,
    'user_original_or_private_data_or_user_DB_or_Git_publication_authorized': False,
}
save_json('adoption-receipt.json', adoption)
save_json('product-baseline.json', {'at': now, 'scope': '只读源／测试／锁／迁移／最终dist身份，不扩写入范围',
                                   'count': len(product_baseline), 'files': product_baseline})
save_json('input-manifest.json', {
    'at': now, 'rules': rules, 'design_report': {'path': str(report), **ident(report)},
    'adopted_proposal': {'path': str(proposal), **ident(proposal)},
    'adoption_receipt': {'path': str(HERE / 'adoption-receipt.json'), **ident(HERE / 'adoption-receipt.json')},
    'prior_119_input_identities': {'path': str(ROOT / 'DocuN/evidence/TASK-119/design/input-identities.json'),
                                    **ident(ROOT / 'DocuN/evidence/TASK-119/design/input-identities.json')},
    'old_engineering_budget': {'path': str(ROOT / 'DocuN/evidence/TASK-117/execution/budget.json'),
                               **ident(ROOT / 'DocuN/evidence/TASK-117/execution/budget.json'),
                               'phase': old_budget['phase'], 'counts': old_budget['counts'], 'failures': 81},
    'draft': {'path': str(draft), **ident(draft)}, 'current_product_count': len(product_baseline),
})
save_json('scope-index.json', {
    'task': 'TASK-120', 'R': 'R-114', 'STEP': 'STEP-018', 'design_parent': 'TASK-119/R113',
    'route': 'A+原TASK119／TASK117 S08工程窗口', 'manual_transfer': True, 'actual_receipt_or_start': False,
    'whole_outcome': 'Q_v2_implementation_all_five_entrypoints_PG_zero_outbound_combination_final_bundle_and_cleanup',
    'allowed_product_scope': '完整卡允许文件段为唯一权限，product-baseline仅身份',
    'product_DDL_changes': 0, 'new_schema_or_role_profile': False, 'independent_audit_required_after_stability': True,
    'audit_route': '主控另卡，优先原TASK118独立窗口；不预占号，不接收工程完整聊天／自评',
    'result_path': str(ROOT / 'DocuN/results/TASK-120-result.md'),
    'execution_evidence_path': str(ROOT / 'DocuN/evidence/TASK-120/execution'),
    'already_accepted_S_not_reopened': True, 'public_source_research_cap_this_card': 0,
})
permit = {
    'id': 'TASK-120-Q-PREP-IMPLEMENTATION-20261018', 'issued_at': now,
    'actual_first_tool': None, 'calendar_hours_from_actual_first_tool': 96, 'save_only_last_seconds': 1800,
    'command_wall_total_cap_seconds': 14400, 'runtime_holding_union_cap_seconds': 10800,
    'metadata_command_cap_seconds': 60, 'test_build_subbatch_cap_seconds': 300,
    'real_root_cap_seconds': 1800, 'root_cleanup_reserve_seconds': 120,
    'new_caps': {'roots': 8, 'pg_create_attempts': 2, 'pg_objects': 1, 'volume_create_attempts': 2, 'volumes': 1,
                 'pg_starts': 8, 'api_starts': 8, 'browser_starts': 8, 'frontend_builds': 4,
                 'native_business_sessions': 32, 'http': 3000, 'preview_creates': 0, 'preview_starts': 0,
                 'provider_calls': 0, 'actual_fee_microunits': 0, 'Git_writes': 0},
    'new_counts_not_yet_consumed': True, 'old_budget_reset_or_rewritten': False,
    'historical_counts_read_only_reference': old_budget['counts'], 'historical_failures': 81,
    'memory_free_MiB': {'PG_API_start': 512, 'browser_start': 768, 'pressure_stop_below': 256,
                        'pressure_consecutive_samples': 2, 'sampling_interval_seconds': 2},
    'cross_interruption_elapsed_is_not_continuous_activity_hard_gate': True,
    'Q_activation_and_real_provider_API': False,
}
save_json('permit.json', permit)
save_json('resource-policy.json', {
    'permit_id': permit['id'], 'kind': 'TESTONLY_zero_external', 'container': 'retrolume-task120-qprep-pg1',
    'volume': 'retrolume-task120-qprep-data', 'compose_project': 'retrolume-task120-qprep',
    'image_reference': 'pgvector/pgvector@sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f',
    'image_cached_now_verified_by_main': False, 'pull_build_install_allowed': False,
    'labels': {'retrolume.task': 'TASK-120', 'retrolume.scope': 'q-prep-testonly', 'retrolume.permit': permit['id']},
    'limits': {'CPU': 1, 'memory_MiB': 512, 'pids': 128, 'restart': 'no', 'host_bind': False, 'privileged': False},
    'loopback_PG_port_candidates': [55480, 55481, 55482, 55483], 'loopback_API_port_candidates': [18120, 18121, 18122, 18123],
    'selection': '首真实根前实际bind等预检后取首可用并固定，不改系统保留段／不杀占用者',
    'logical_DBs': ['retrolume_task120_flow', 'retrolume_task120_budget_01', 'retrolume_task120_budget_02'],
    'budget02_condition': '首库有具体修正且需重新证明时；首库原件保留，不是真收费重置',
    'private_root': str(ROOT / '.runtime/TASK-120'), 'old_six_resources_allowed': False,
    'live_fee_Q_DB_creation_allowed': False, 'retention': '准确停止但保留CID／卷／库／journal／失败',
    'new_external_network_requests_allowed': 0, 'real_provider_calls_allowed': 0,
})

work_prefix = f'''# TASK119采用包已获用户批准，移交完整工程TASK120

{now}。用户对主控完整三项提案明确回复“批准”。主控以394dfae4…db8f的具体提案及其K1/K2登记采用，完整receipt在DocuN/evidence/TASK-120/orchestration-20261018/adoption-receipt.json；原设计交付验收通过、原119报告和本裁定历史原字节保留。

生效采用范围为零DDL的Q v2本机精确逐请求批准／原键等待与显式继续、候选deepseek-flash且原两provider／thinking disabled／10秒／字节输出限不放宽、同固定三个UUID的未来100次／25元条件许可（48／28／24次，12／7／6元）。替换尚未激活的原80／20，不叠加，不恢复旧13元，不重绑已建活动或换根借账。

Q尚未激活，valid_from/valid_until空。原S有限关闭、历史控制不通过与81失败照留。新的实现／零外发PG组合／最终UI及必要独审、真实官方/账号/计量/币种税/返回身份/矩阵/readiness/启用回执均未因此自动通过。本轮不对本人资料／用户库／Git远程写入或发布授权。

新TASK120/R114沿原119工程窗一个完整候选成果，当前仅登记保存待人工转交，不冒已接收。96h自实际首工具、命令wall14400、持有10800、精确新TESTONLY资源及低内存512/768门，所有provider/费用0，旧对象不动。卡面允许普通实现与修复连续完成，稳定后主控另卡集中独审，原118独立归属优先。不再反复请求用户批准同一包／释放内存／交key。证据与旧共享在本轮orchestration目录。

## 以下为采用前原验收裁定

'''
write(work119, work_prefix.encode('utf-8') + before[work119])
requirement_prefix = f'''# 最终需求文档

需求与实现验收基线v1.4，2026-10-18，Asia/Shanghai。用户对TASK119主控具体增量包明确“批准”，补充已采用的STEP018实现及条件外发边界；原31项编号／Must／质量标准和v1.3以下原字节完整保留，用户原始需求不改。

## 已采用的有限请求批准及条件额度增量

采用零DDL的Q v2：固定根／有限合成输入／固定实例和三活动不变，未来每个完整请求由受信本机operator精确审查批准，客户端原键显式继续、GET只读恢复，未批准／失效／unknown不外发。新私有批准不成为第二金融账，不自动批准未来任意模型内容，不修改永久只读恢复权或旧v1兼容。K1摘要排除自身和K2共享发送临界段释放后再写结果的规范见已采用提案；产品实现仍需真实证据和必需独审。

Chat候选配置名改为deepseek-flash，provider仍deepseek_chat_completions，保留原endpoint／thinking disabled／输出字节及10秒限；embedding仍zhipu_embeddings／embedding-3／512，不新增其它供应商。此处采用候选不是官方能力／账号／返回身份／计量／税费已核通过。

尚未激活的一份未来真实Q总上限调整为100次、人民币25元，含失败／超时／UNKNOWN及已准入未送预留；每笔仍250000 microunits，1元=1000000。固定学习01800000-0000-4000-8000-000000000001为48次／12元；面试01800000-0000-4000-8000-000000000002为28次／7元；补证01800000-0000-4000-8000-000000000003为24次／6元。替换原80／20，只增加20次与5元上限，不另发25元，不恢复旧13元，不跨活动挪款或换grant／库重置。

启用仍待完整新协议实现、真实PG共同锁/SUM/预扣COMMIT、必要独审、现行官方与账号条款／严格返回身份／token-framing-reasoning／含税币种、每笔最坏≤0.25且至少25%裕量、完整合法剩余Must矩阵、正常配置及主控首次启用回执。72小时只从未来真实T0起；每活动24小时／3600秒、finite_calculate≤8及预览3次180秒等原边界不放宽。当前provider费用0，TASK120只做零外发合成前置，不使用本次条件额启动付费。

采用来源DocuN/evidence/TASK-120/orchestration-20261018/adoption-receipt.json及其固定提案hash。原S有限成果关闭／历史控制不通过均保留；不包含本人资料／用户库或Git发布。STEP018整体／STEP019／STEP020／M1及项目通过仍需各自实际证据。

## 以下为v1.3及更早批准原文

'''
write(requirements, requirement_prefix.encode('utf-8') + before[requirements])
arch_prefix = f'''# 架构动态文档

文档v1.46，2026-10-18，Asia/Shanghai。需求v1.4、执行动态v2.73、task_model/07；以下v1.45原字节保留。

## Q v2具体增量已采用，TASK120完整实现尚未开始

{now}。用户对119主控394dfae4…db8f提案明确批准。采用固定v2根／实例／finite来源和本机operator逐请求精确批准，原accepted未claim等待、原键显式继续、v1／协议3及原4兼容，原PG仍唯一金融权威；零DDL、不新增profile或R03、不解除readonly／source冻结。q事件／私有artifact／authority与等待投影的具体边界按119 A—D及K1/K2实施，无通用HTTP批准或auto-approve平台。

approval hash排除自身、原日志锁内固定seq；共享policy发送临界段必须在会改head的结果事务前释放，写结果再先取排他policy与MutationGate／PG，原currentness处理间隔变更，禁止升级共享锁／PG反向等私有锁。该规范仍待实际实现和有界并发／正常落地证明，不宣称静态说明已证行为。

候选deepseek-flash、原deepseek_chat_completions／thinking disabled及原limits不变，embedding-3／512不变。未来同三个固定UUID改48／28／24次及12／7／6元，总100／25、单笔0.25替换未激活80／20；不因尚未知价格／账号／返回别名或计量把候选说成ready。真实Q的正常绑定／PG组合／独审／官方及账号事实／合法矩阵／主控启用门保留。

TASK120为一个完整A+工程成果：协议＋五入口等待／显式继续＋真实PG零外发共同预扣＋最终bundle传播＋精确清场。只用一新TESTONLY PG／卷与固定端口候选、低内存串行门，旧六对象不动，真实provider／费用／preview／Git写0。实现后的稳定新边界集中独审，原S关闭／D01—D04充分原件不重审。当前卡只保存待人工转交，未收到执行证据，STEP018整体和项目未通过。

## 以下为v1.45及更早历史

'''
write(arch, arch_prefix.encode('utf-8') + before[arch])
state_prefix = f'''# 执行动态文档

文档v2.73，2026-10-18，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.46、task_model/07。以下v2.72原字节保留。

## 用户批准119增量，TASK120/R114完整工程{{status}}

{now}。用户明确“批准”，对应主控完整提案394dfae4…db8f和119设计58870字节／2d10d08b…096346。TASK119设计已返回且验收通过；新增Q v2本机精确批准／原键显式继续、deepseek-flash候选及未来100次／25元（48／28／24，12／7／6元）采用生效，K1/K2规范同采用。替换原未启80／20而非叠加或新25元余额，旧13元不恢复。

Q仍冻结，72h/T0未起、valid_from/valid_until空；本轮不读取key／用户库／私配，不发外网或真实供应商，不形成可用grant。原S有限工程／证据关闭、原117总体部分通过／历史控制失败照留；原81失败、root25／PGcreate对象卷6／PGstart46／API33／Browser19／build8／Native140／HTTP2486／preview各2／fixture_server3/provider费用0原账未改。当前只继承原停止时点，不宣称主控实时查旧六资源。

新TASK120/R114先登记占号、A+原119/117工程窗负责一个完整实现候选，内容含新授权协议、五入口等待／恢复／原键继续、真实PG双provider同锁/SUM/预扣COMMIT及100门并发、最终正式bundle与低内存精确清场，必要普通修复卡内连续完成。验收未判断／未自签独审，{{dispatch}}。正式卡DocuN/tasks/TASK-120.md；未来新增独审只在稳定后另卡登记，优先原118独立归属，不预占121，不传工程完整聊天／自评。

新许可从实际首工具96h、最后1800保存、命令wall14400秒／运行持有10800秒；每真实根1800／末120清场。delta根8／PGstart8／APIstart8／Browser8／build4／真实业务监督32／HTTP3000，create尝试2但新PG/卷各只1；PG端口55480—55483／API18120—18123首根预检后各固定一个，三TESTONLY逻辑库只在新CID。PG/API最低512MiB、Browser768MiB／连续两次<256精确停止，不再要求2GiB或用户释放内存。provider费用／preview／Git新额度0，旧资源／源／readonly保持。

这张卡不保证第一次就成功，但合并预检／实现／必要测试与普通修正，保留所有失败、计数及as-run，不用极少根预算把已知夹具修正逐一转卡；同问题两次修正仍失败／主要方案不稳／硬门仍按规则停止受影响部分。内存／镜像／平台门只阻相应真实验证，剩余离线成果继续。真实Q启用仍需实际新边界独审、当前官方／账号／计量／严格返回身份／合法剩余矩阵／正常配置及主控启用回执，不能把此卡pure synthetic成功签真实语义。

主控本轮只读源/证据hash与共享维护，没有实现／compile／测试／PG／Docker／API／Browser／业务Job／模型／费用或Git写。原GitHub origin shspic/RetroLume-agent保持，发布和公开范围仍后续。STEP018整体、STEP019/020、M1与项目未通过。采用／baseline／精确许可／旧共享／保存证明在DocuN/evidence/TASK-120/orchestration-20261018。CHG1509—1516，下一1517。

## 以下为v2.72及更早历史

'''
write(state, state_prefix.replace('{status}', '已登记待保存').replace('{dispatch}', '未有人工转交／接收／执行证据').encode('utf-8') + before[state])
save_json('dispatch-registration.json', {'at': now, 'task': 'TASK-120', 'R': 'R-114', 'state': 'registered_before_card_save',
                                          'actual_dispatch_receipt_execution': False, 'manual_transfer': True})
write(card, contract, True)
write(state, state_prefix.replace('{status}', '待人工转交').replace('{dispatch}', '完整卡已保存待人工转交，未有真实接收／执行证据').encode('utf-8') + before[state])
entries = [
    (1509, 'DocuN/evidence/TASK-120/orchestration-20261018/adoption-receipt.json', '记录用户对119三项增量明确批准，条件许可100/25，不启用Q。'),
    (1510, 'DocuN/results/TASK-119-work-decision.md', '置顶采用决定／移交完整工程与保留启用门，原裁定原字节保留。'),
    (1511, 'DocuS/最终需求文档.MD', 'v1.4固化Q v2及候选／条件额度采用，原31项Must和原文不改。'),
    (1512, 'DocuS/架构动态文档.MD', 'v1.46记录已采用授权及K1/K2、零DDL及新前置工程仍未实现。'),
    (1513, 'DocuS/执行动态文档.MD', 'v2.73先登记120/R114再保存转待人工，新许可与原累计分层，未虚记派发。'),
    (1514, 'DocuN/tasks/TASK-120.md', '一张完整A+实施／零外发PG／最终UI／必要修复和清场卡，沿原工程窗。'),
    (1515, 'DocuN/evidence/TASK-120/orchestration-20261018', '输入／产品baseline／scope／低内存精确资源和96h等前向许可，旧账只读。'),
    (1516, 'DocuN/evidence/TASK-120/orchestration-20261018/save-proof.json', '共享／新卡完整读回与原输入未漂移，未启动产品或付费。'),
]
append = '\n' + '\n\n'.join(f'- CHG-{n}，{now}，Codex编排Agent，{path}。{reason}' for n, path, reason in entries) + '\n'
write(changes, before[changes] + append.encode('utf-8'))

for path, expected in protected.items():
    assert ident(path) == expected, str(path)
for row in rules:
    assert ident(Path(row['absolute_path']))['sha256'] == row['sha256']
for path in [state, arch, requirements, work119]:
    assert path.read_bytes().endswith(before[path]), str(path)
assert changes.read_bytes().startswith(before[changes])
assert card.read_bytes() == contract
assert not (ROOT / 'DocuN/results/TASK-120-result.md').exists(), '不得虚建执行结果'
save_json('save-proof.json', {
    'saved_at': datetime.now(timezone(timedelta(hours=8))).isoformat(), 'result': 'SAVED_AND_READ_BACK',
    'task': 'TASK-120/R114', 'versions': {'requirements': 'v1.4', 'architecture': 'v1.46', 'state': 'v2.73', 'last_CHG': 1516},
    'documents': [{'path': str(p), **ident(p)} for p in [card, state, arch, requirements, work119, changes]],
    'product_baseline_files': len(product_baseline), 'protected_count': len(protected), 'protected_mismatches': [],
    'rules7_match': True, 'prior_shared_suffixes_and_change_prefix_preserved': True,
    'new_adoption_approved': True, 'actual_dispatch_receipt_execution': False,
    'Q_activated': False, 'provider_calls': 0, 'actual_fee_microunits': 0,
    'orchestration_document_precheck_failure_preserved': 'precheck-failure-01.json及原draft bytes；未写共享或运行产品',
    'main_product_runtime_tests_or_Git_writes': 0,
})
print(json.dumps({'result': 'SAVED_AND_READ_BACK', 'task': 'TASK-120/R114', 'product_baseline': len(product_baseline),
                  'protected': len(protected), 'requirements': 'v1.4', 'architecture': 'v1.46', 'state': 'v2.73',
                  'last_CHG': 1516, 'manual_transfer_pending': True, 'Q_activated': False}, ensure_ascii=False))
