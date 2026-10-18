"""接收118增量审计、关闭有限S工程成果、登记119设计卡。仅标准库。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
REV = ROOT / 'DocuN/evidence/TASK-118/audit/review-01'
E = ROOT / 'DocuN/evidence/TASK-117/execution'
assert ROOT == Path('D:/shspic/project_NO3_RetroLume-agent').resolve()
assert not (HERE / 'save-proof.json').exists(), '已发布，不重复操作'


def h(raw):
    return hashlib.sha256(raw).hexdigest()


def load(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def identity(p):
    if not p.is_file():
        return {'exists': False, 'bytes': 0, 'sha256': None}
    b = p.read_bytes()
    return {'exists': True, 'bytes': len(b), 'sha256': h(b)}


def write(p, raw, new=False):
    assert p.resolve().is_relative_to(ROOT), str(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('xb' if new else 'wb') as f:
        f.write(raw)
    assert p.read_bytes() == raw
    raw.decode('utf-8-sig')


def save_json(name, value):
    write(HERE / name, (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8'), True)


now = datetime.now(timezone(timedelta(hours=8))).isoformat()
rules = load(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
for row in rules:
    assert h(Path(row['absolute_path']).read_bytes()) == row['sha256'], row['absolute_path']
freeze = load(REV / 'freeze-final.json')
assert len(freeze['checks']) == 208 and freeze['mismatches'] == []
for row in freeze['checks']:
    assert identity(Path(row['path'])) == row['actual'], row['path']

audit_report = ROOT / 'DocuN/results/TASK-118-result.md'
receipt = load(REV / 'review-execution-receipt.json')
assert identity(audit_report)['bytes'] == 65525 and identity(audit_report)['sha256'] == '8f4569489faef05fe212e943f6c33a1e4a94bdcaae6da4fac3958f425e654af6'
assert identity(audit_report)['sha256'] == receipt['report']['sha256']
old = (REV / 'original-TASK118-result.bytes').read_bytes()
assert len(old) == 41590 and audit_report.read_bytes().endswith(old)
assert receipt['product_tests_build_compile_Node_PG_SQL_Docker_business_Job_API_Browser_network_provider_Git_writes'] == 0
assert receipt['new_agents'] == 0
engineering_report = ROOT / 'DocuN/results/TASK-117-result.md'
assert identity(engineering_report)['sha256'] == '90b4ebc77c34cf7886f5e4bb624a9912c14df9b5a7b53ac2528826487bd771e2'
budget = load(E / 'budget.json')
assert budget['active_root'] is None and budget['phase'] == 'S08_returned_engineering_candidate'
assert budget['counts']['roots'] == 25 and budget['counts']['provider_calls'] == 0 and budget['counts']['actual_fee_microunits'] == 0
assert len(budget['failures']) == 81
adoption = ROOT / 'DocuN/evidence/TASK-117/orchestration-20261014/adoption-receipt.json'
adopted = load(adoption)
package = ROOT / adopted['package_path']
assert identity(package)['sha256'] == adopted['package_sha256'] == '84cb852946220a09873225f8bde7b7138aa7366e137297638bb2aab01dbc1c84'

state = ROOT / 'DocuS/执行动态文档.MD'
arch = ROOT / 'DocuS/架构动态文档.MD'
change = ROOT / 'DocuS/文档变更记录.MD'
work117 = ROOT / 'DocuN/results/TASK-117-work-decision.md'
work118 = ROOT / 'DocuN/results/TASK-118-work-decision.md'
card = ROOT / 'DocuN/tasks/TASK-119.md'
assert not card.exists(), '119已存在，先核对编号归属'
assert '文档v2.70' in state.read_text(encoding='utf-8-sig').splitlines()[2]
assert '文档v1.43' in arch.read_text(encoding='utf-8-sig').splitlines()[2]
assert max(map(int, re.findall(r'CHG-(\d+)', change.read_text(encoding='utf-8-sig')))) == 1494
before = {p: p.read_bytes() for p in [state, arch, change, work117, work118]}
for p in before:
    assert p.resolve().is_relative_to(ROOT), str(p)
contract = (HERE / 'task-contract.md').read_bytes()
t = contract.decode('utf-8')
assert '*' not in t
for token in ['TASK-119 / R-113', '## A ', '## B ', '## C ', '## D ', '不实施', '最多8次搜索查询', '16个实际有效文档页', '模型API调用', '80次/20元', '48小时']:
    if token == '不实施':
        assert '不是代码实施' in t
    else:
        assert token in t, token

source_paths = [
    'backend/app/capabilities/embedding.py', 'backend/app/capabilities/gateway.py',
    'backend/app/activities/api.py', 'backend/app/activities/repository.py',
    'backend/app/retrieval/repository.py', 'backend/app/retrieval/service.py', 'backend/app/service_config.py',
    'backend/app/worker/one_call.py', 'backend/app/learning/teaching_service.py', 'backend/app/interview/service.py',
    'backend/app/data_exit/control.py', 'backend/app/data_exit/operations.py',
    'DocuN/evidence/TASK-116/design/adoption-package.md', 'DocuN/evidence/TASK-116/design/integration-contract.md',
    'DocuN/evidence/TASK-116/design/acceptance-contract.md', 'DocuN/evidence/TASK-116/design/sample-inputs.json',
]
for rel in source_paths:
    assert (ROOT / rel).is_file(), rel
protected_paths = {Path(row['path']) for row in freeze['checks']}
protected_paths.update([audit_report, engineering_report, REV / 'review-execution-receipt.json',
                        ROOT / 'DocuN/tasks/TASK-117.md', ROOT / 'DocuN/tasks/TASK-118.md',
                        E / 'budget.json', E / 'events.jsonl', E / 'case-index.json', adoption])
protected_paths.update(ROOT / rel for rel in source_paths)
protected_paths.difference_update(before)
protected = {p: identity(p) for p in protected_paths}

backup = HERE / 'before-documents'
backup.mkdir(exist_ok=False)
for p, b in before.items():
    write(backup / p.name, b, True)

received = {
    'at': now, 'task': 'TASK-118', 'R': 'R-112', 'round': 'review-01',
    'report': {'path': str(audit_report), **identity(audit_report)},
    'receipt': {'path': str(REV / 'review-execution-receipt.json'), **identity(REV / 'review-execution-receipt.json')},
    'frozen208_verified_now': True, 'freeze_mismatches': [], 'original41590_exact_suffix': True,
    'TASK118_review_delivery_acceptance': '通过，限集中独审及四项增量合同交付',
    'D01_D02_D03_D04': '主控依据独立复核与身份绑定全部关闭；D02仅关闭原安全缺陷，不签Q多步可执行',
    'finite_S_engineering_and_valid_evidence': '验收通过并关闭该有限交付，停止S续作',
    'TASK117_acceptance_axes': {'functional_delivery_S': '通过/有限关闭', 'evidence_for_S': '充分',
                                 'historical_execution_control': '不通过，S01-S07与未知原账保持',
                                 'TASK117_overall': '部分通过，不签全过程合规、Q或父STEP全部通过'},
    'Q_enabled': False, 'STEP018_whole_passed': False, 'project_passed': False,
    'next_work': 'TASK119/R113只读收敛完整请求批准/官方事实/费用矩阵/最小实施包，沿原117工程归属',
    'budget_metadata_read_only': {'path': str(E / 'budget.json'), **identity(E / 'budget.json'), 'phase': budget['phase'], 'counts': budget['counts'], 'failures': 81},
    'main_product_execution_or_tests_or_runtime_or_Git_writes': 0,
    'stop_scope': '只继承118已核原时点/归属停止证据，主控未新查Docker/PG/进程',
}
save_json('received-review01.json', received)
save_json('input-manifest.json', {
    'at': now, 'task': 'TASK-119', 'R': 'R-113', 'rules': rules,
    'sources': [{'path': str(ROOT / rel), **identity(ROOT / rel)} for rel in source_paths],
    'audit_report': {'path': str(audit_report), **identity(audit_report)},
    'adoption_receipt': {'path': str(adoption), **identity(adoption)},
    'source_freeze_reference': {'path': str(REV / 'freeze-final.json'), **identity(REV / 'freeze-final.json'), 'verified': 208},
    'current_engineering_counts': budget['counts'],
    'contract': {'path': str(HERE / 'task-contract.md'), **identity(HERE / 'task-contract.md')},
})
save_json('scope-index.json', {
    'at': now, 'task': 'TASK-119', 'R': 'R-113', 'parent': 'TASK-117/R111', 'dependent_audit': 'TASK-118/R112 review-01',
    'goal': '唯一可实施Q多步请求批准合同及官方事实、价额矩阵、最小采用/实施/审计门',
    'S_reopened': False, 'D02_reopened': False,
    'allowed_outputs': ['DocuN/results/TASK-119-result.md', 'DocuN/evidence/TASK-119/design/'],
    'not_authorized_now': ['implementation', 'provider API', 'activation', 'private config/key', 'product runtime', 'DB/container', 'Git publication'],
    'manual_route': 'A+原TASK117 S08工程窗口，不是原118独审窗口',
})
save_json('design-permit.json', {
    'id': 'TASK-119-Q-PRECONDITIONS-DESIGN-20261018', 'issued_at': now, 'task': 'TASK-119', 'R': 'R-113',
    'actual_receipt_or_start': False, 'calendar_hours_from_actual_first_tool': 48, 'save_only_last_calendar_seconds': 1200,
    'metadata_command_wall_cap_seconds': 1200, 'single_metadata_command_seconds': 60,
    'public_official_search_queries_cap': 8, 'public_effective_official_pages_cap': 16,
    'network_scope': '仅DeepSeek/智谱主体官方文档/价目/服务与隐私条款及其明确官方同主体链接；非API调用/非账号登录',
    'product_import_tests_compile_build_PG_SQL_Docker_Job_API_Browser_provider_fee_Git_writes': 0,
    'engineering_or_audit_unused_root_budget_inherited': False,
    'current_Q_financial_cap': {'requests': 80, 'CNY': 20, 'activated': False, 'new_spend_now': 0},
    'historical_failures_or_spend_reset': False,
})

prefix118 = f'''# TASK118/R112 — review-01验收，四项缺陷全部关闭

{now}，Codex编排Agent。65525字节/8f456948…654af6与完整复读回执一致，原41590字节审计体精确后缀保留；208组冻结身份重新核对零漂移。独立执行上下文延续且未承接117实现聊天/自评，审计交付与增量合同验收通过，主控接受D01—D04关闭。

D01写身份、D02完整消息安全批准、D03同activity原身份晚到、D04供应商告知的代码/证据闭合，原D01批TIMEOUT只继承已完成12方法、D02无I/O夹具及分批方法绑定、D03原生IDB屏障、D04正式bundle合成HTTP均按原准确层采用，不重跑。D02安全关闭不代表后续未知请求已有批准，也不把本轮当真实PG或外部语义通过。

有限S合成工程功能及有效证据主控验收通过并关闭，TASK117全过程执行控制仍不通过；S01—S07超额/未知/失败照留，不追认。S08按其前向许可核未见已记录新超额，真实持续工作仍unknown。Q/STEP018整体/STEP019/020/M1/项目未通过。

下一TASK119/R113沿原117工程窗只读收敛不可变grant下的多步请求批准、有限官方事实/价额矩阵及实施采用边界；不重新打开已关闭四项，不启用费用或产品运行。原118上下文仅在实际新变化/后续语义和剩余证明稳定后作必要增量，当前无新审计运行许可。

本轮主控只读核证/共享维护，源/报告/工程账/独审原件不改，未现场查Docker/PG/进程，未实施/测试/运行或Git写。证据在DocuN/evidence/TASK-119/orchestration-20261018。

## 以下为原裁定历史

'''
write(work118, prefix118.encode('utf-8') + before[work118])

prefix117 = f'''# TASK117/R111 — 有限S工程成果验收关闭，Q保持冻结

{now}。主控接收118 review-01独立结论65525字节/8f456948…654af6并复核208冻结身份、报告回执及原审计后缀。D01—D04全部关闭，S08与首轮有效原件组合足以支撑有限S功能及工程证据。该有限成果验收通过、停止S续作；TASK117总验收记部分通过，明确不签全过程执行合规、Q或父STEP全部通过。

代码/当前有限证据通过不改变历史控制不通过。S01—S07全部原超额/首点/mono域/metadata unknown、81条失败/UNKNOWN/旧预留留史。S08按实际前向48h/命令wall/持有/次数门核；根25/Browser19/build8/server3/HTTP2486和其它冻结计数不变，所有provider费用0。唯一工程budget维持原returned候选事实，主控验收写在本裁定与唯一执行动态账，不倒改工程账。

Q当前缺口为不可变grant/manifest下，未知上一模型产物及新ID等使下一完整payload不能事前列入固定hash；不能自动加白、重绑活动/新grant/新库清零，也不能降低原语义目标。下一新TASK119/R113为这个独立设计/事实核查成果，优先同一原工程窗，只读交付完整合同/当前官方事实/最坏80次20元矩阵/最小采用边界，产品和付费0。

原80次20元用户条件批准有效，不重问/不激活；官方/配置/持久PG组合/新normal合成资源/72h及启用回执仍后续明确。原S source frozen/selector永久readonly不解除，旧六CID/包/失败对象不动，GitHub仅已有origin，无commit/push许可。本轮无需用户执行命令或交凭据。

TASK119卡保存待人工转交，不冒已接收或开始，无新工程根/源写入。原118独审只等必要的新变化/后续语义稳定再增量，不全量重审已闭四项。STEP018整体/STEP019/020/M1/项目仍未通过。主控没有代做执行层；本轮证据/许可/旧共享/保存证明在DocuN/evidence/TASK-119/orchestration-20261018。

## 以下为原裁定历史

'''
write(work117, prefix117.encode('utf-8') + before[work117])

arch_prefix = f'''# 架构动态文档

文档v1.44，2026-10-18，Asia/Shanghai。需求v1.3、执行动态v2.71、task_model/07。以下v1.43原字节保留，116已批准的数据/费用边界不扩大。

## 有限S合成工程关闭，Q请求批准仍待合同收敛

{now}。基于118 review-01与208冻结身份核证，ControlHub三写入口hub身份、模型完整payload/request双摘要安全批准、教学原owner/view/head/scope/namespace晚到围栏、三处实际provider/model告知及缺字段门均完成独立复核，D01—D04关闭。正式bundle8 bc2768fd…a3c0c1及合成HTTP/真实文件锁/实际gateway最低替身等原件按准确层采用；有限S工程功能与有效证据主控验收关闭，不把mock扩为真实PG/供方。

历史执行控制不通过保留，不追认旧超额/未知；该事实不重新打开已确认安全功能。旧S source/selector已frozen/permanent readonly，恢复包和六CID原状保持；Q不能往旧根写或借新根清零真实费用。

现Q仍缺未知上轮模型输出/服务生成ID/父链等后继完整请求的可执行批准机制。固定model_requests安全关闭任意正文外发，却不能提前批准所有未来hash；活动grant/roster不可重绑及总80次20元保持。新TASK119仅设计唯一最小机制及官方事实/价额/实施路线，必要主要模型/接口/权限影响给具体采用包，未采用/实施/启用任何新协议。

真实PG roster SUM/两provider共同持久预扣组合证、当前官方能力/价目/条款/正常配置、新normal资源/72h及主控Q回执仍前置；不改变原Must语义目标，不要求此刻新增Linux/Nginx/公网发布。STEP018整体与后续项目交付尚未通过，GitHub仍只有origin关联无新提交/上传。

## 以下为v1.43及更早历史

'''
write(arch, arch_prefix.encode('utf-8') + before[arch])

state_prefix = f'''# 执行动态文档

文档v2.71，2026-10-18，Asia/Shanghai。唯一总状态账；需求v1.3、架构v1.44、task_model/07。以下v2.70原字节保留。

## 118增量已返回并验收，有限S关闭，TASK119/R113前置合同{{status}}

{now}。用户真实带回118 review-01，65525字节/8f456948…654af6与保存回执一致，208组身份零漂移、原41590字节后缀完整。TASK118调度已返回、验收通过限独审/增量合同交付，主控接受D01—D04关闭；有限S合成工程功能及有效证据验收通过并关闭该交付，停止S修正循环。TASK117调度已返回、总验收部分通过，历史全过程控制不通过照留，不签STEP018整体/Q/M1/项目通过。

独审支持D01锁内三写围栏、D02完整消息范围、D03同activity原身份IDB晚到门、D04配置告知。分批方法/原TIMEOUT、no-I/O loop和正式bundle8合成HTTP各按实际对象继承，不把整个失败批改绿、不重跑已足旧七族/两域/恢复/PDF/预览。Q仍未具备启用条件，多步请求批准问题没有因D02安全关闭而自动解决。

原工程账phase=S08_returned_engineering_candidate、active_root空，root25/Browser19/build8/fixture server3/HTTP2486；PGcreate对象卷6/PGstart46/产品API33/Native140/preview各2/provider费用0不变，原81失败/全部旧超额/unknown保持。S08按当时前向许可核已记录部分未见新超额，真实持续活动unknown；只继承原时点自有停止证据，主控未实时查Docker/PG/进程。源、工程账和审计原件均未写。

新TASK119/R113已占号，A+原117工程窗承接一个只读完整成果：不可变grant/固定roster下的有限分阶段/派生请求批准协议、当前官方能力/价费/条款、80次20元最坏动作矩阵、最小实施/真实PG组合证/必要审计和采用边界。旧S已关闭不再派修；本卡不实施、不import产品/测试/build/PG/SQL/Docker/API/Job/Browser/provider或费用/Git写。只读官方检索最多8查询/16有效页、metadata1200/单批60、实际接收48h/最后1200保存；写自身结果与design，公共/产品/原证据/私配不动。先登记再保存，未有真实转交/接收/执行证据。

若真正需改变主要模型/公开接口/权限等，只交具体最小采用包；普通已授权实现细节不机械请求用户再批准。80次20元原AP2条件批准不重问、不启用，旧13元不复活，未知后继payload不可自动加白或用新grant/活动/库借余额。需当期官方与正常配置/新normal合成资源/真实PG SUM+锁+共同预扣+COMMIT/72h/主控回执后才Q，source永久readonly/frozen不解除。TASK119设计完成本身不代表采用或实现。

STEP018执行仍进行中、验证部分，STEP019适用安全原件可继承但整体未验收，STEP020前置未齐，项目/M1未通过。GitHub既有shspic/RetroLume-agent origin保持，后续精确公开范围与发布执行仍未进行，不commit/push旧原件。本轮主控只读核证/共享维护，真实运行与费用0。证据/许可/旧共享/保存证明在DocuN/evidence/TASK-119/orchestration-20261018。CHG1495—1503，下一1504。

## 以下为v2.70及更早历史

'''
write(state, state_prefix.replace('{status}', '已登记待保存').encode('utf-8') + before[state])
save_json('dispatch-registration.json', {'at': now, 'task': 'TASK-119', 'R': 'R-113', 'state': 'registered_before_card_save', 'manual_transfer': True, 'actual_dispatch_receipt_execution': False})
write(card, contract, True)
write(state, state_prefix.replace('{status}', '待人工转交').encode('utf-8') + before[state])

rows = [
    ('1495', 'DocuN/evidence/TASK-119/orchestration-20261018/received-review01.json', '核118 review01/208冻结/回执与旧后缀，接受四项关闭与有限S工程成果。'),
    ('1496', 'DocuN/results/TASK-118-work-decision.md', '增量独审交付验收、四项关闭、Q多步合同缺口分层，原历史保留。'),
    ('1497', 'DocuN/results/TASK-117-work-decision.md', '有限S工程交付关闭，总验收部分通过/历史控制失败保持，停止S续作。'),
    ('1498', 'DocuN/tasks/TASK-119.md', '新119/R113完整只读设计/有限官方核实卡，原117工程窗，Q/产品/费用0。'),
    ('1499', 'DocuS/执行动态文档.MD', 'v2.71先占119号再保存卡转待人工，S关闭/父STEP未过/Q冻结不混同。'),
    ('1500', 'DocuS/架构动态文档.MD', 'v1.44登记独审修正已接受和未知后继请求/不可重绑grant矛盾，未采用新机制。'),
    ('1501', 'DocuN/evidence/TASK-119/orchestration-20261018', '输入/只读官方检索与metadata许可/设计范围存证，原AP2费用未激活。'),
    ('1502', 'DocuN/evidence/TASK-119/orchestration-20261018/before-documents', '五份旧共享完整原字节保留，未改工程/审计报告账/源/资产。'),
    ('1503', 'DocuN/evidence/TASK-119/orchestration-20261018/save-proof.json', '新卡与共享读回，受保护输入/规则/历史原件不变，无真实派发执行。'),
]
append = '\n' + '\n\n'.join(f'- CHG-{n}，{now}，Codex编排Agent，{p}。{s}' for n, p, s in rows) + '\n'
write(change, before[change] + append.encode('utf-8'))

for p, expected in protected.items():
    assert identity(p) == expected, str(p)
for row in rules:
    assert h(Path(row['absolute_path']).read_bytes()) == row['sha256']
for p in [state, arch, work117, work118]:
    assert p.read_bytes().endswith(before[p]), str(p)
assert change.read_bytes().startswith(before[change]) and card.read_bytes() == contract
proof = {
    'saved_at': datetime.now(timezone(timedelta(hours=8))).isoformat(), 'result': 'SAVED_AND_READ_BACK',
    'task': 'TASK-119 / R-113', 'versions': {'state': 'v2.71', 'architecture': 'v1.44', 'last_CHG': 1503},
    'documents': [{'path': str(p), **identity(p)} for p in [state, arch, work117, work118, card, change]],
    'audit_frozen208_reverified': True, 'protected_inputs': len(protected), 'protected_mismatches': [],
    'old_shared_raw_suffixes_preserved': True, 'engineering_audit_reports_ledger_products_unchanged': True,
    'rules7_MATCH': True, 'finite_S_accepted_and_closed': True, 'D01_D04_closed': True,
    'historical_execution_control_failed_retained': True, 'Q_enabled': False, 'project_passed': False,
    'actual_dispatch_receipt_execution': False, 'main_product_runtime_Git_or_network_calls': 0,
}
save_json('save-proof.json', proof)
print(json.dumps({'result': proof['result'], 'task': proof['task'], 'protected': len(protected), 'S_finite_closed': True,
                  'state': 'v2.71', 'architecture': 'v1.44', 'last_CHG': 1503, 'manual_transfer_pending': True, 'Q_enabled': False}, ensure_ascii=False))
