"""只读取证据和串行维护编排文档，不导入或执行产品。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
assert ROOT == Path('D:/shspic/project_NO3_RetroLume-agent').resolve()
assert not (HERE / 'save-proof.json').exists(), '本批已保存，不重复发布'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def stamp(path):
    if not path.exists():
        return {'exists': False, 'bytes': 0, 'sha256': None}
    raw = path.read_bytes()
    return {'exists': True, 'bytes': len(raw), 'sha256': sha(raw)}


def json_new(name, value):
    target = HERE / name
    raw = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    with target.open('xb') as stream:
        stream.write(raw)
    assert target.read_bytes() == raw


def write_checked(path, raw):
    path.write_bytes(raw)
    assert path.read_bytes() == raw
    raw.decode('utf-8-sig')


now = datetime.now(timezone(timedelta(hours=8))).isoformat()
rules = load(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
for rule in rules:
    assert sha(Path(rule['absolute_path']).read_bytes()) == rule['sha256'], rule['absolute_path']

audit_freeze_path = ROOT / 'DocuN/evidence/TASK-118/audit/final-freeze.json'
freeze = load(audit_freeze_path)['result']['checks']
for entry in freeze:
    actual = stamp(Path(entry['path']))
    expected = entry['actual']
    assert actual['exists'] == expected['exists'], entry['path']
    if actual['exists']:
        assert actual['bytes'] == expected['bytes'] and actual['sha256'] == expected['sha256'], entry['path']

report = ROOT / 'DocuN/results/TASK-118-result.md'
receipt_path = ROOT / 'DocuN/evidence/TASK-118/audit/audit-execution-receipt.json'
receipt = load(receipt_path)
assert stamp(report)['sha256'] == receipt['report']['sha256'] == 'dd0a5f1d2ddb2ffcd9a168496e4cca5b8292b7221977c76b8ff417f9ff0f21f1'
original_report = ROOT / 'DocuN/results/TASK-117-result.md'
assert stamp(original_report)['sha256'] == 'b596ab87ae3facc605dab65acbf9c708c784c11b1f8581b75ddc6611ad802ac9'
budget_path = ROOT / 'DocuN/evidence/TASK-117/execution/budget.json'
budget = load(budget_path)
assert budget['active_root'] is None and budget['phase'] == 'S06_returned_engineering_candidate'
assert budget['counts']['roots'] == 24 and budget['counts']['provider_calls'] == 0

state = ROOT / 'DocuS/执行动态文档.MD'
arch = ROOT / 'DocuS/架构动态文档.MD'
change = ROOT / 'DocuS/文档变更记录.MD'
work117 = ROOT / 'DocuN/results/TASK-117-work-decision.md'
card = ROOT / 'DocuN/tasks/TASK-117.md'
work118 = ROOT / 'DocuN/results/TASK-118-work-decision.md'
assert not work118.exists(), '已有主控裁定，先核对，不覆盖'
assert '文档v2.67' in state.read_text(encoding='utf-8-sig').splitlines()[2]
assert '文档v1.40' in arch.read_text(encoding='utf-8-sig').splitlines()[2]
assert max(map(int, re.findall(r'CHG-(\d+)', change.read_text(encoding='utf-8-sig')))) == 1470

before_paths = [state, arch, change, work117, card]
before = {p: p.read_bytes() for p in before_paths}
backup = HERE / 'before-documents'
backup.mkdir(exist_ok=True)
for path, raw in before.items():
    saved = backup / path.name
    if saved.exists():
        assert saved.read_bytes() == raw, str(saved)
    else:
        with saved.open('xb') as stream:
            stream.write(raw)
    assert (backup / path.name).read_bytes() == raw

contract = (HERE / 'task-contract.md').read_bytes()
text = contract.decode('utf-8')
for required in ['D01 / P1', 'D02 / P1', 'D03 / P2', 'D04 / P2', 'S07', 'continuation-06/', '21600', '768MiB', 'PG/SQL/Docker/产品API/Windows业务监督/真实provider/费用']:
    assert required in text, required
assert '*' not in text

allowed_products = [
    'backend/app/data_exit/control.py', 'backend/app/capabilities/embedding.py',
    'backend/app/capabilities/gateway.py', 'backend/app/retrieval/service.py',
    'backend/app/service_config.py', 'frontend/src/activities/TeachingWorkspace.tsx',
    'frontend/src/activities/InterviewWorkspace.tsx', 'frontend/src/activities/RetrievalPanel.tsx',
    'frontend/src/activities/retrieval-api.ts', 'frontend/src/activities/ActivityWorkspace.tsx',
    'frontend/src/activities/teachingIntents.ts', 'frontend/src/activities/teachingDrafts.ts',
    'frontend/src/activities/teachingApi.ts', 'frontend/src/data/context.tsx',
    'backend/tests/test_step018_control_snapshot.py', 'backend/tests/test_step018_flows.py',
    'backend/tests/test_step018_embedding_contracts.py', 'README.md', 'config/integration.example.json',
]
for rel in allowed_products:
    assert (ROOT / rel).is_file(), rel

received = {
    'at': now, 'task': 'TASK-118', 'R': 'R-112', 'sourced_from': '用户回传原结果绝对路径',
    'report': {'path': str(report), **stamp(report)}, 'receipt': {'path': str(receipt_path), **stamp(receipt_path)},
    'audit_delivery_acceptance': '通过，限集中独审合同交付，不等于所审产品通过',
    'candidate_code': '不通过', 'candidate_evidence': '部分满足', 'historical_execution_control': '不通过',
    'findings': [{'id': 'D01', 'severity': 'P1', 'scope': 'S 控制日志写身份'},
                 {'id': 'D02', 'severity': 'P1', 'scope': '仅未来 Q 完整合成消息外发'},
                 {'id': 'D03', 'severity': 'P2', 'scope': '教学同 activity owner/view 晚到'},
                 {'id': 'D04', 'severity': 'P2', 'scope': '索引及两域供应商告知'}],
    'independence_basis': '实际fork_turns=none独立上下文，未承接实现聊天/自评；不是另一个桌面客户端，精确模型未确认',
    'independence_disclosure': 'DocuN/evidence/TASK-118/audit/isolation-dispatch.json',
    'audit_freeze_verified_now': len(freeze), 'audit_freeze_mismatches': [],
    'main_verification': '只读报告/原始身份和四项关键源码，不执行产品或重复独审',
    'actual_engineering_budget_before': {'path': str(budget_path), **stamp(budget_path), 'phase': budget['phase'], 'active_root': budget['active_root'], 'counts': budget['counts']},
    'historical_stop_reference_only': '2026-10-16T15:45:05Z 原六CID停止记录，本轮未查询现场Docker或进程',
    'main_product_tests_build_SQL_Docker_API_browser_provider_Git_mutations': 0,
    'main_read_failures': '三次错误Windows通配路径、一个猜测不存在的teaching-editor.ts只读定位失败；后按rg实际路径读取。文档发布预检误写context.ts，正式写入前断言失败，查明实际tsx路径后修正；原脚本与失败记录保留在本目录，未触发产品或运行重试。',
    'S_acceptance': '当前不通过，四项合并修正回TASK117，Q仍不得启用',
}
json_new('received-audit.json', received)
inputs = {
    'at': now, 'task': 'TASK-117', 'R': 'R-111', 'stage': 'S07', 'rules': rules,
    'audit_frozen_input': {'path': str(audit_freeze_path), **stamp(audit_freeze_path), 'checked': len(freeze)},
    'reports': [{'path': str(p), **stamp(p)} for p in [report, original_report]],
    'sources': [{'path': str(ROOT / p), **stamp(ROOT / p)} for p in allowed_products],
    'baseline_manifest': str(ROOT / 'DocuN/evidence/TASK-117/execution/continuation-05/final-source-manifest.json'),
    'contract': {'path': str(HERE / 'task-contract.md'), **stamp(HERE / 'task-contract.md')},
}
json_new('input-manifest.json', inputs)
permit = {
    'id': 'TASK-117-STEP018-AUDIT-REPAIR-S07-20261017', 'issued_at': now,
    'task': 'TASK-117', 'R': 'R-111', 'purpose': 'TASK118 D01-D04合并修正与定向验证',
    'status': 'saved_pending_manual_transfer', 'starts_on': 'actual first tool after receipt; not issuance',
    'activity_seconds': 21600, 'no_new_family_after_seconds': 20400, 'save_reserve_seconds': 1200,
    'calendar_hours': 48, 'offline_child_process_wall_seconds': 3600, 'runtime_holding_union_seconds': 3600,
    'new_roots': 3, 'cumulative_roots_cap': 27, 'root_check_seconds': 1500, 'root_cleanup_seconds': 300,
    'baseline_counts': budget['counts'],
    'new_counts': {'browser_starts': 3, 'frontend_builds': 2, 'fixture_server_starts': 3, 'http': 600,
                   'pg_create_attempts': 0, 'pg_objects': 0, 'volumes': 0, 'pg_starts': 0,
                   'api_starts': 0, 'native_windows': 0, 'preview_creates': 0, 'preview_starts': 0,
                   'provider_calls': 0, 'actual_fee_microunits': 0},
    'cumulative_caps': {**budget['counts'], 'roots': 27, 'browser_starts': 19, 'frontend_builds': 9, 'http': 2924},
    'fixture_binding': '127.0.0.1:18119, no PG/API product runtime, synthetic HTTP only',
    'memory_gates_mib': {'fixture_server': 512, 'browser': 768, 'pressure_exit_two_samples': 256, 'sample_interval_seconds': 2},
    'Q_enabled': False, 'financial_history_reset': False, 'historical_overruns_waived': False,
    'runtime_now_started_by_main': False,
}
json_new('continuation-permit.json', permit)

audit_decision = f'''# TASK-118 / R-112 集中独审交付核证与合并修正裁定

{now}，Codex编排Agent。报告41590字节/dd0a5f1d…0f21f1与保存回执一致，256组被审身份独立重算零漂移。四项直接源码定位成立；原始运行事实按TASK118列明层级继承，不重跑旧充分验证。

TASK118调度为已返回，验收通过仅指集中独审合同交付。实际隔离机制为内置fork_turns=none上下文、未继承实现聊天/自评，不冒新外部桌面客户端或确定模型。该机制有可读披露且满足本轮判断所需独立性，本轮不因资源标签重审。

所审TASK117/S的代码轴不通过、证据轴部分满足、历史执行控制轴不通过。D01/P1控制日志写身份阻断S；D02/P1只阻断未来Q完整synthetic-only，不称S已真实泄露；D03/D04为必须修正的P2，未被用户接受为交付限制。S未关闭，Q不得启用，STEP018/019/020/M1/项目未通过。

四项统一归原TASK117/R111 S07原A+工程窗，在同卡连续修正和定向验证。采用隔离本地文件锁、实际网关合成ledger/最低transport、正式dist合成HTTP浏览器。新增PG/SQL/Docker/产品API/业务Job/provider/费用0，不启动已冻结source或六个旧CID，不重跑恢复/PDF/完整两链。共享总门真实PG组合缺证留未来Q前置，本卡mock不冒通过。

历史活动/持有/离线超额和首点缺口完整保留；前向许可不追认旧合规。当前只接收旧时点清场原件，主控未查询实时Docker/进程。原工程账不由主控改写。稳定修正后回原118独审上下文一次增量复核，复用本次其它有效判断。

80次/20元原条件批准不重问、不激活；后续需官方当期能力/价率/条款、正常本地配置、新normal合成资源、持久共享总门证据和明确Q启用回执。GitHub保持既有origin、无提交/推送许可。

本轮证据与许可在D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/orchestration-s07-20261017。主控仅做规则/报告/原件身份与源码核证、出卡和共享文档维护，无产品实施、测试、build、SQL、Docker、API、Browser、真实模型或Git写入。
'''
write_checked(work118, audit_decision.encode('utf-8'))

work_prefix = f'''# TASK117/R111 — TASK118四项缺陷已核证，S07合并修正许可

{now}。集中独审交付已接收，报告41590字节/dd0a5f1d…0f21f1、256组冻结身份匹配。TASK118合同交付通过，所审S代码不通过/证据部分满足/历史执行控制不通过；不是S、Q或项目通过。D01/P1控制日志全部写入口的hub身份，D02/P1仅未来Q完整合成消息范围，D03/P2同activity owner/view晚到，D04/P2新入口供应商告知，一并归原117/R111工程修正。

本次同号S07完整卡待人工转交原A+工程窗，未接收/未新执行，无TASK119。三类最小验证足以针对本次改动：真实隔离FileLock、实际gateway合成ledger/transport、正式bundle合成HTTP浏览器。PG/SQL/Docker/产品API/业务Job/preview/外网/真实provider/费用/Git写新增0，原source frozen/readonly和六CID不动；持久共享总门真实PG组合缺证仍归Q前置。

S07前向活动21600/48h含1200保存、20400后不启新族，离线子进程3600/运行资源并集3600；新增完整根3至27、Browser3至19/build2至9/fixture server3/HTTP600至2924，唯一127.0.0.1:18119。512/768MiB启动门、两次低于256自动准确自有清场，禁外网。所有旧活动/持有/离线超额/漏采/失败不清零、不追认。收到后先采真实UTC/单调钟、校验本段控制器及截止清场后运行。

工程当前账roots24/PGcreate对象卷6/PGstart46/产品API33/Browser16/build7/Native140/HTTP2324/preview各2/provider费用0、active_root空。旧79709字节工程报告保护；新产物continuation-06，原execution账只能追加。原六CID停止仅2026-10-16T15:45:05Z原件，不冒实时监控。

稳定后回原118独立上下文一次增量复核，不逐小改重开全面审计。Q80次20元原条件许可未激活，真实PG全局准入/官方当期条件/正常配置/新normal资源/72h与启用回执仍待；STEP018/019/020/M1/项目未通过。主控没有代做产品。

## 以下为原裁定历史

'''
write_checked(work117, work_prefix.encode('utf-8') + before[work117])

arch_prefix = f'''# 架构动态文档

文档v1.41，2026-10-17，Asia/Shanghai。需求v1.3、执行动态v2.68、task_model/07。以下v1.40原字节保留，116采用包不扩大。

## STEP018集中独审确认的当前缺口与修正边界

{now}。TASK118已完成集中独审。当前ControlHub快照读校验当前完整字节/文件身份/首control_id，但commit/create_or_get_job/change_job写入口未共享该围栏，构成D01/P1；原包/readonly/实际日志读证据不能替代写身份完整性。S未验收。

OutboundSourceManifest仅检查source/catalog，实际模型目标/回答/历史/selected memory自由正文没有完整合成范围批准，D02/P1只阻断尚未启用Q，无真实泄露证据。修复限定原受信manifest/实际gateway全消息边界及必要loader兼容，不新增持久列/公开接口或启用Q。

教学query→domain最后比较可变owner且缺view/scope/head绑定，D03/P2；索引和两领域入口未展示受信实际provider/model，D04/P2。批准原contract内修正并定向验证；本段尚未实施，不写已修或已验证。未变两域/恢复/PDF/预览和旧G模块有效证据按对象继承。

修正使用本地文件锁、网关合成调用、正式dist合成HTTP浏览器，无新PG/API/业务Job或真实供方。原S source永久readonly/frozen不解除；Q新normal资源、真实PG共享总门组合证、官方当期条件及原80次20元启用门后续处理。历史执行控制失败不由新成功赦免，不升级Linux/Nginx/公开部署为本S门。

## 以下为v1.40及更早历史

'''
write_checked(arch, arch_prefix.encode('utf-8') + before[arch])

state_prefix = f'''# 执行动态文档

文档v2.68，2026-10-17，Asia/Shanghai。唯一总状态账；需求v1.3、架构v1.41、task_model/07。以下v2.67历史原字节保留。

## TASK118/R112已返回，TASK117/R111 S07四项合并修正{{status}}

{now}。用户带回TASK118集中独审结果41590字节/dd0a5f1d…0f21f1，主控核256组身份零漂移、保存回执与四项关键源码。TASK118调度已返回、验收通过限独审合同交付；独立机制fork_turns=none如实披露，不因标签再审。被审S代码不通过/证据部分满足/历史执行控制不通过，S、Q及STEP018/019/020/M1/项目均未放行。

D01/P1日志三类写入口未核当前hub身份，D02/P1仅未来Q模型自由正文未受完整合成清单约束，D03/P2教学同activity owner/view晚到门，D04/P2实际供应商告知。四项归原TASK117/R111 S07原A+窗口一次修正、验证、收口，不拆卡，不新占119。必要独审回原118上下文做一次实际增量确认，其余有效证据继承。

当前工程唯一账仍S06_returned_engineering_candidate、active_root空、roots24，PGcreate对象卷6/PGstart46/产品API33/Browser16/build7/Native140/HTTP2324/preview各2/provider费用0。全部原活动/持有/离线超额/63条failure/漏采/unknown保留，不改旧段/初许可。原六CID停止只采旧2026-10-16T15:45:05Z原件，主控未实查现场。

S07新前向许可仅四项修复：活动21600/48h含1200保存、20400后不启新族，离线子进程3600/运行持有并集3600；完整合成验证根最多3至27，Browser新增3至19/build2至9/loopback fixture server3/HTTP600至2924。所有PG/SQL/Docker/产品API/业务Job/preview/provider/外网/费用/Git写新增0。正式bundle+合成HTTP检查D03/D04，实际gateway+合成ledger/transport检查D02，真实隔离FileLock检查D01，不冒PG/付费集成通过。低内存512/768MiB/连续两次<256自动自有清场保持，无需2GiB/Docker暖机。

原source frozen/正式selector永久readonly、六CID/包/旧日志/原79709字节报告保持。新产物continuation-06、原执行账只追加。Q未启用，80次/20元原批准不重问但仍需官方当期条件、正常配置、新normal库/控制根、真实持久全局准入组合证、72h与启用回执；S替身不能代Q。GitHub仅已关联origin，未commit/push。

本轮输入/许可/旧共享与保存证明在DocuN/evidence/TASK-117/orchestration-s07-20261017。主控只读核证和共享维护，产品/测试/build/SQL/Docker/Job/API/Browser/provider/Git写0，未代做工程或重做独审。CHG1471—1478，下一1479。

## 以下为v2.67及更早历史

'''

# 先在唯一状态账登记接续，再保存合同；不得把保存当作真实派发。
write_checked(state, state_prefix.replace('{status}', '已登记待保存').encode('utf-8') + before[state])
json_new('dispatch-registration.json', {'at': now, 'task': 'TASK-117', 'R': 'R-111', 'stage': 'S07', 'state': 'registered_before_card_save', 'new_TASK_or_R': False, 'manual_transfer': True, 'actual_dispatch_or_receipt': False})
write_checked(card, contract)
write_checked(state, state_prefix.replace('{status}', '待人工转交').encode('utf-8') + before[state])

changes = [
    ('1471', 'DocuN/evidence/TASK-117/orchestration-s07-20261017/received-audit.json', '接收118报告及256组身份，四缺陷源码核证、三轴及旧控制偏差分层。'),
    ('1472', 'DocuN/results/TASK-118-work-decision.md', '集中独审交付通过与所审S不通过分开，四项归117，Q冻结。'),
    ('1473', 'DocuN/results/TASK-117-work-decision.md', '置顶S07合并修正许可，旧完整裁定保留，原工程窗接续。'),
    ('1474', 'DocuS/执行动态文档.MD', 'v2.68先登记同号S07再保存转待人工，118已返回；无119、无真实派发。'),
    ('1475', 'DocuN/tasks/TASK-117.md', '完整S07合同替换有效卡，旧S06卡原字节备份，四项连续修正和定向验证。'),
    ('1476', 'DocuS/架构动态文档.MD', 'v1.41登记实际四缺口及修正边界，未冒实施或放行。'),
    ('1477', 'DocuN/evidence/TASK-117/orchestration-s07-20261017', '保存输入hash/前向许可/旧五文档原字节及出卡脚本；PG/费用等新增0。'),
    ('1478', 'DocuN/evidence/TASK-117/orchestration-s07-20261017/save-proof.json', '保存复读合同和共享文档、规则/受保护对象/历史原件不变，待人工转交。'),
]
append = '\n' + '\n\n'.join(f'- CHG-{number}，{now}，Codex编排Agent，{path}。{description}' for number, path, description in changes) + '\n'
write_checked(change, before[change] + append.encode('utf-8'))

managed = {p.resolve() for p in before_paths}
protected = []
for entry in freeze:
    p = Path(entry['path'])
    if p.resolve() in managed:
        continue
    current = stamp(p)
    expected = entry['actual']
    assert current['exists'] == expected['exists'], str(p)
    if current['exists']:
        assert current['bytes'] == expected['bytes'] and current['sha256'] == expected['sha256'], str(p)
    protected.append({'path': str(p), 'match': True})
for p in [state, arch, work117]:
    assert p.read_bytes().endswith(before[p]), str(p)
assert change.read_bytes().startswith(before[change])
assert stamp(report)['sha256'] == receipt['report']['sha256']
assert stamp(budget_path)['sha256'] == received['actual_engineering_budget_before']['sha256']
assert card.read_bytes() == contract
for p in [state, arch, work117, work118, card, change]:
    p.read_bytes().decode('utf-8-sig')
proof = {
    'saved_at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
    'result': 'SAVED_AND_READ_BACK', 'task': 'TASK-117', 'R': 'R-111', 'stage': 'S07',
    'documents': [{'path': str(p), **stamp(p)} for p in [state, arch, work117, work118, card, change]],
    'versions': {'state': 'v2.68', 'architecture': 'v1.41', 'last_CHG': 1478},
    'protected_count': len(protected), 'protected_mismatches': [], 'audit_received_freeze_count': len(freeze),
    'old_shared_bytes_preserved': True, 'original_117_and_118_reports_unchanged': True,
    'engineering_budget_unchanged': True, 'rules_7_MATCH': True,
    'actual_dispatch_or_receipt': False, 'actual_runtime_started': False,
    'main_product_execution_or_Git_mutations': 0,
    'checks': ['完整卡D01-D04/规则/绝对根/窗口/输入/范围/预算/停止/回传齐全', '同号接续不占新TASK/R', '旧产品/证据/报告/预算受保护', '正式文档已登记再保存完整卡', '新状态为待人工转交不是派发', '用户原始需求/公共库未写'],
}
json_new('save-proof.json', proof)
print(json.dumps({'result': proof['result'], 'task': 'TASK-117 / R-111 S07', 'audit_TASK118_delivery': 'accepted', 'S_code': 'failed', 'Q_enabled': False, 'protected': len(protected), 'state': 'v2.68', 'architecture': 'v1.41', 'last_CHG': 1478, 'manual_transfer_pending': True}, ensure_ascii=False))
