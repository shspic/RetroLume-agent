"""串行回收C02、维护共享文档、保存原独审窗口增量复核卡；不执行产品。"""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import hashlib
import json
import re

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
OUT = Path(__file__).resolve().parent
BASE = ROOT / 'DocuN/evidence/TASK-114/implementation/continuation-02'
RECEIPT = ROOT / 'DocuN/evidence/TASK-114/orchestration-c02-receipt-20261013'
CARD = ROOT / 'DocuN/tasks/TASK-115.md'
WORK114 = ROOT / 'DocuN/results/TASK-114-work-decision.md'
WORK115 = ROOT / 'DocuN/results/TASK-115-work-decision.md'
ARCH = ROOT / 'DocuS/架构动态文档.MD'
STATE = ROOT / 'DocuS/执行动态文档.MD'
CHANGES = ROOT / 'DocuS/文档变更记录.MD'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def identity(path):
    data = path.read_bytes()
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def record(path):
    return {'path': str(path), **identity(path)}


def save(name, value):
    path = OUT / name
    assert not path.exists(), str(path)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    assert load(path) == value


def prefix(path, text, original):
    path.write_bytes(text.replace('\n', '\r\n').encode('utf-8') + original)
    assert path.read_bytes().endswith(original), str(path)


now = datetime.now(timezone(timedelta(hours=8)))
at = now.isoformat()
day = now.strftime('%Y-%m-%d')
received = load(RECEIPT / 'received.json')
metadata = load(RECEIPT / 'current-owned-metadata.json')
assert received['manifest']['current_files'] == 235
assert received['old_audit_evidence_verified'] == 358
assert metadata['all_containers_stopped'] and metadata['no_original_consumers']
assert metadata['relevant_tcp'] == []
closed = load(BASE / 'closure.json')
assert {row['cid'] for row in closed['containers']} == {row['cid'] for row in metadata['containers']}
for row in closed['containers']:
    actual = next(item for item in metadata['containers'] if item['cid'] == row['cid'])
    assert all(actual[key] == row[key] for key in ('name', 'image_id', 'running', 'pid'))

old = {path: path.read_bytes() for path in (CARD, WORK114, WORK115, ARCH, STATE, CHANGES)}
assert '文档v1.28' in old[ARCH].decode('utf-8-sig').splitlines()[2]
assert '文档v2.52' in old[STATE].decode('utf-8-sig').splitlines()[2]
assert identity(CARD)['sha256'] == '4fdf624d0e49e80e2f238b8f4a52ccbfd402ed2f19bd9c093f1e1af0b2db2204'
numbers = [int(value) for value in re.findall(r'^- CHG-(\d+)', old[CHANGES].decode('utf-8-sig'), re.MULTILINE)]
assert numbers[-1] == 1344 and 1345 not in numbers

backup = OUT / 'before-documents'
backup.mkdir(exist_ok=False)
for path, data in old.items():
    (backup / path.name).write_bytes(data)

protected = {}
for path in (ROOT / 'DocuN/results/TASK-114-result.md', ROOT / 'DocuN/results/TASK-115-result.md',
             ROOT / 'DocuN/tasks/TASK-114.md', BASE / 'final/manifest.json',
             ROOT / 'DocuN/evidence/TASK-114/implementation/control/receipt.json',
             ROOT / 'DocuN/evidence/TASK-114/implementation/control/events.jsonl'):
    protected[str(path)] = identity(path)
for row in received['current']:
    if row['exists']:
        path = ROOT / row['path']
        protected[str(path)] = {key: row[key] for key in ('bytes', 'sha256')}
        assert identity(path) == protected[str(path)]
    else:
        assert not (ROOT / row['path']).exists()
audit = load(ROOT / 'DocuN/evidence/TASK-115/audit/delivery.json')
for row in audit['evidence']:
    path = Path(row['path'])
    protected[str(path)] = {key: row[key] for key in ('bytes', 'sha256')}
    assert identity(path) == protected[str(path)]
for row in received['rules']:
    path = Path(row['path'])
    protected[str(path)] = {key: row[key] for key in ('bytes', 'sha256')}
    assert identity(path) == protected[str(path)]

permit = {
    'TASK': 'TASK-115', 'R': 'R-109', 'round': 'review-01',
    'permit': 'TASK-115-STEP017-REVIEW01-20261013', 'issued_at': at,
    'authorization': '用户已采用STEP017-P1并持续要求完成；原必需独审对合并修复和实际影响增量确认',
    'dispatch_confirmed': False, 'execution_started': False,
    'active_seconds_this_round_max': 7200, 'save_reserve_seconds': 300,
    'previous_active_conservative_seconds': 5490.683454,
    'original_active_limit_seconds': 21600,
    'total_active_upper_if_full_round_used': 12690.683454,
    'remaining_after_max_this_round_seconds': 8909.316546,
    'original_calendar_anchor_utc': '2026-10-13T06:16:24.914938Z',
    'original_calendar_deadline_utc': '2026-10-15T06:16:24.914938Z',
    'actual_first_tool_utc_and_monotonic_pair': '接收者实采；本文件签发时间不冒执行锚点',
    'new_runtime_limits': dict.fromkeys(['real_roots', 'PG', 'SQL', 'container_create', 'container_start',
                                       'API', 'Browser', 'Windows', 'preview', 'build',
                                       'product_import', 'unittest', 'provider', 'fees', 'public_network'], 0),
    'allowed_metadata': '读取既存文件/hash/有限AST/JSON/diff；仅必要时准确自有对象metadata，不唤醒或消费',
    'prior_audit_counts': audit['new_counts'],
    'engineering_counts_readonly': received['counts'],
    'engineering_limits_readonly': received['limits'],
    'engineering_resources_not_reauthorized': True,
    'separate_local_review_log': 'review-01/receipt.json及events，引用旧锚点和用量，非第二总状态账',
    'independence': '原TASK115独立窗口，未参与113/114；原暴露披露保留，不读114自评或实现聊天',
    'output': str(ROOT / 'DocuN/results/TASK-115-result.md'),
    'evidence_output': str(ROOT / 'DocuN/evidence/TASK-115/review-01'),
}
save('continuation-permit.json', permit)

input_manifest = {
    'created_at': at, 'purpose': '独立增量复核的中性字节与原始证据导航，不给工程自评作判断输入',
    'current': received['current'], 'final_source_snapshot': received['final_source_snapshot'],
    'pre': received['pre'], 'rules': received['rules'],
    'adopted_contract': record(ROOT / 'DocuN/evidence/TASK-113/design/revision-01/current-contract.md'),
    'engineering_task': record(ROOT / 'DocuN/tasks/TASK-114.md'),
    'final_manifest': record(BASE / 'final/manifest.json'),
    'method_index': record(BASE / 'final/method-index.json'),
    'offline_index_actual_limit': received['offline_method_index_limitation'],
    'as_run_delta_navigation': received['as_run_bindings'],
    'raw_batches': received['raw_batch_navigation'],
    'protected_original_audit_report': record(ROOT / 'DocuN/results/TASK-115-result.md'),
    'protected_original_audit_evidence': audit['evidence'],
    'latest_owned_metadata': record(RECEIPT / 'current-owned-metadata.json'),
    'engineering_control': record(ROOT / 'DocuN/evidence/TASK-114/implementation/control/receipt.json'),
    'engineering_events': record(ROOT / 'DocuN/evidence/TASK-114/implementation/control/events.jsonl'),
    'reading_exclusions': ['TASK-114-result.md正文及pre副本正文', '实现聊天/思考/自评', '记忆中的工程结论'],
    'old_proven_methods': '原115已独立判定的未变方法直接引用，只复核真实增量传播',
}
save('input-manifest.json', input_manifest)
save('window-assignment.json', {
    'created_at': at, 'TASK': 'TASK-115', 'R': 'R-109', 'round': 'review-01',
    'grade': 'A+', 'window': '原TASK115集中独立审计窗口',
    'previous_actual_identity': 'Codex desktop / GPT-6，当前如实登记',
    'manual_transfer': True, 'dispatch_confirmed': False,
    'engineering_window_state': '原TASK114封存，无新消费者/写入',
    'reason': '复核四项高风险修复和证据传播，原独审上下文复用，独立性保持',
    'no_subagents_or_parallel_work': True,
})

work114 = f'''# TASK114 C02合并修复与定向补证已返回，候选待原115增量复核

{at}，Codex编排Agent。实际回传69598字节，SHA256 e457d13159c439da8c56814b4f9c860973c0ff5d8622793ab4663584ffe5ad11；旧53842字节后缀原字节保留。235当前文件/最终原件/pre、21批as-run差异导航、旧358审计原件及七锁定规则核证。原四DEF-034—037保持开放待独审，工程调度已返回，验收为候选部分通过，不凭回返卡签完整验证或STEP017。

实际C02增量含取消请求/不可逆短准入、operation唯一D与晚到完成确认、前端身份/生命周期、同RR正文依赖资格；必要PG/文件/HTTP/Browser原件存在。最终六离线方法绑定最终产品，但PG/HTTP后仍有产品增量，原115必须按真实差异判继承，不能默认最终签名全链PG已跑。原method-index的offline_exact为空，方法需由原日志/as-run/events读取重建，不伪造采样。

工程累计root21/24、PG create9/12、success9/9/start37/37、Windows11/12、API8/11、Browser5/9、build5/6、offline172.317、hold462.047；本轮活动9188.720111，原C01活动9739.953/旧55525.796及unknown保留。PG成功/启动已经门满，其他余量不自动续，原工程无新许可。实际资源readonly复查九准确容器Stopped/Pid0、原17消费者结束、相关TCP0，未启DB或执行产品。旧source frozen/target07 generation1不写，新独立域另存，不回退选择或复用failed目标。

原TASK115/R109窗口review-01用7200秒只读段、原累计21600/48h日历门不清；零新PG/SQL/API/Browser/build/Windows/provider费用。主控核候选与共享维护，四缺陷最后关闭及有限STEP017由独审回后裁定；TASK116未占，原G11/25/UNKNOWN/R60/13元/626.566不外推。原114结果/源码/旧FAIL不写。

## 以下为旧工程许可与记录原字节

'''
prefix(WORK114, work114, old[WORK114])

work115 = f'''# TASK115 review-01原独立窗口增量复核许可，待人工转交

{at}，Codex编排Agent。TASK114四修和定向补证已实际返回并冻结，235当前文件/最终原件、旧报告后缀/358原审计证据匹配，准确资源Stopped，前置满足。原115独审交付及独立性带暴露披露继续有效；原四P1仍待关闭。当前新卡只核F01—F04、必要V差异与真实传播，不重做充分正常链/整仓/旧G11，不读114结果自评。

许可TASK-115-STEP017-REVIEW01-20261013，只读活动段最多7200秒含最后300落盘，原115活动5490.683454/21600累计，最多12690.683454；旧保守日历起点2026-10-13T06:16:24.914938Z加48h不延。原root3/API3/Browser2、offline125.610/保守hold14.874、全部失败/计时偏差保留。本轮新增产品/PG/SQL/container/API/Browser/build/Windows/unittest/模型费用全0，只写review-01证据与原结果置顶、原37767字节原文后缀不改。

最后纯控制/文件方法绑定最终版，较早PG/HTTP的api/control/operations等仍有hash差异，必须独立核完整D/完成确认和调用传参，不仅以SQL没改就继承，也不因字节不同自动全重跑；确切缺口一次集中交主控。原normal/权限/RootLease/SUP及已认可归约有效则直接引用。独审代码、证据、执行控制分轴，不能自修或回源normal。

完整卡DocuN/tasks/TASK-115.md已保存复读；继续原115 A+独立窗，人工转交/实际接收前调度待转交，不冒已派发。原114封存，未派子Agent，TASK116未占。用户无需密钥、释放内存或启容器；只转本完整卡并带回结果路径。

## 以下为原独审许可及结论历史原字节

'''
prefix(WORK115, work115, old[WORK115])

arch = f'''# 架构动态文档

文档v1.29，{day}，Asia/Shanghai。需求v1.2、执行动态v2.53、task_model/07；以下v1.28历史原字节保留。

## STEP017四修候选已形成，独立增量复核前不关闭

{at}。TASK114 C02实际候选增量已落盘并有定向原始证据。数据管理私有操作新增operations/readability，取消请求与安全确认分开，成功按revision/原状态/kind/准入短CAS；一次绝对D贯通文件/PG/镜像，成功帧提交回包与确认分开，迟到保留未确认事实。前端全生命周期与代次/实例新鲜性、稳定Hub GET与数据视图命名空间分别约束；只读同RR核source/event/upstream/memory及派生正文，不改历史头或purge。

新增私有execution/completion协议与clock_domain/票据不授旧执行权，不应进普通DTO或包。001—013/codec/角色ACL/业务模型/原Native和预算StopProof核心未改；可选Operation向调用者传导须独立核，不能以函数文本未变排除回归。较早PG/HTTP后仍有控制/文件增量，最终离线六方法不冒最终版完整PG链，必须按实际影响裁定证据继承。

DEF-034—037仍开放，原115窗口只对问题、必要余门和传播复核后主控关闭。正常恢复/31域/同T/两锁序/原SUP/G11已充分证据不重跑。永久只读仍不代完整恢复继续/NFR005，STEP018—020、M-1、用户库/真实资料/费用/发布均未放行；旧source/target07 frozen和readonly选择保护，新独立域不复制执行资格。

## 以下为v1.28及更早历史

'''
prefix(ARCH, arch, old[ARCH])

state = f'''# 执行动态文档

文档v2.53，{day}，Asia/Shanghai。唯一总状态账；需求v1.2、架构v1.29、task_model/07。以下v2.52历史原字节保留。

## TASK114 C02已返回，原TASK115 review-01已登记

{at}。工程C02实际已接收/执行/返回，报告69598字节/e457d13159c439da8c56814b4f9c860973c0ff5d8622793ab4663584ffe5ad11，旧53842字节后缀保留。主控235当前文件和final/pre字节、21批as-run导航、358旧独审原件与七锁定规则匹配；两已移除旧bundle输出保缺失。工程验收候选部分通过，DEF-034/F01、035/F02、036/F03、037/F04保持开放待原独审确认，STEP017不关闭，不凭实现自评签四问题通过。

累计root21/24、PG create9/12、物理success9/9/start37/37、Windows11/12、API8/11、Browser5/9、build5/6、offline172.317/hold462.047，本轮活动9188.720111/原C01活动9739.953；旧55525.796及净投入unknown、原失败/根口径/超限不清。PG成功/启动门满，工程许可已收口，其他子余额不恢复新执行权。九精确容器封存Stopped/Pid0、17原消费者ended；主控只读升级实际核九对象Stopped、原消费者不存在、相关TCP0，未遇审批拒绝，不启动或连接DB。原source frozen/target07 generation1未改，新C02 source frozen/target01 generation1为独立域。

C02六kind取消、真实文件/Hub后段D、实际PG加载取消/撤权/normal overlay/九guard、精确selector注入、实际TCP正文与最终Chromium原件已读导航。PG/HTTP之后api/control/operations等有增量，最终六离线方法才绑定最终产品；原115必须判定传参与确认传播，不能假称当前完整签名全PG已跑。method-index offline_exact为空，原始日志/as-run/events有内容，复核重建必要方法导航，不伪造同点采样。

原115/R109本轮review-01已登记，完整同号卡保存阶段进行，未派发/接收/执行。A+原集中独审窗，原114封存；仅四问题/必要V差异/真实传播，旧充分方法直接继承。新许可7200只读活动含最后300落盘、旧活动5490.683454/21600累计；旧48h日历至2026-10-15T06:16:24.914938Z不延，新增全部产品运行/PG/SQL/API/Browser/build/Native/provider费用0，不借旧根/时间。无需RAM启动门或用户密钥，不派子Agent、不建TASK116。

独审原root3/API3/Browser2/offline125.610/hold14.874及时间配对缺口/保守起点/旧夹具FAIL和两60秒unknown全保留。本轮只读复核完成后才由主控按代码/证据/执行控制三轴裁定四DEF和有限STEP017，不删未满足Must，不重审G11/25/UNKNOWN/R60/count1/13元/626.566，不宣STEP018—020或项目/发布通过。

主控本轮仅字节/原始证据/准确资源metadata核证和共享维护，产品执行0。回收在TASK114/orchestration-c02-receipt-20261013；原115卡和共享旧文档原件、输入/许可/窗口/保存证明在TASK115/orchestration-review01-20261013。CHG1345—1354，下一1355。

## 以下为v2.52及更早历史

'''
# 同号续作先登记，卡保存并复读后才登记待转交。
prefix(STATE, state, old[STATE])
contract = (OUT / 'effective-contract.md').read_bytes()
text = contract.decode('utf-8-sig')
assert '*' not in text and not re.search(r'^\|', text, re.MULTILINE)
for required in ('目标与交付', '项目、规则与窗口', '前置与最小充分输入', 'F01／DEF034',
                 'F02／DEF035', 'F03／DEF036', 'F04／DEF037', '允许、禁止、计时与资源',
                 '执行顺序、停止与回传', '7200秒', '新增真实根/PG/create/start/API/Browser/build/Windows/preview/provider/费用上限全部0'):
    assert required in text, required
CARD.write_bytes(contract)
assert CARD.read_bytes() == contract
final_state = state.replace('原TASK115 review-01已登记', '原TASK115 review-01待人工转交')
final_state = final_state.replace('完整同号卡保存阶段进行，未派发/接收/执行', '完整同号卡已保存复读待人工转交，未派发/接收/执行')
prefix(STATE, final_state, old[STATE])

entries = [
    ('DocuN/evidence/TASK-114/orchestration-c02-receipt-20261013/received.json', '235 current及final/pre/旧后缀与358原独审原件/七规则核证，候选不冒独审通过。'),
    ('DocuN/evidence/TASK-114/orchestration-c02-receipt-20261013/current-owned-metadata.json', '只读升级实查九准确对象Stopped/Pid0、原消费者结束与相关TCP0，无产品/SQL消费。'),
    ('DocuN/results/TASK-114-work-decision.md', '工程C02实际返回/累计门满/原成果保护，候选交原独审复核。'),
    ('DocuN/results/TASK-115-work-decision.md', '同TASK/R原独立窗review-01零产品运行许可，旧时间失败原件不清。'),
    ('DocuN/evidence/TASK-115/orchestration-review01-20261013/effective-contract.md；DocuN/tasks/TASK-115.md', '完整四修/真实传播/必要余证增量复核卡保存复读待人工转交，不重做充分审查。'),
    ('DocuN/evidence/TASK-115/orchestration-review01-20261013/continuation-permit.json；input-manifest.json；window-assignment.json', '7200只读段从旧累计预算内限定，所有真实消费新增0；中性输入/as-run差异与原独立安排。'),
    ('DocuS/架构动态文档.MD', 'v1.29私有操作/确认/身份/资格候选实际增量与未关闭DEF边界。'),
    ('DocuS/执行动态文档.MD', 'v2.53唯一状态：114已返回/真实门满/115增量待人工，旧超限与Must保留。'),
    ('DocuN/evidence/TASK-115/orchestration-review01-20261013/before-documents/TASK-115.md', '原集中审计完整卡和共享文档原字节留档，历史许可不复活。'),
    ('DocuN/evidence/TASK-115/orchestration-review01-20261013/delivery-proof.json', '完整卡/输入/许可/资源/源报告旧账保护与共享历史、CHG保存复读。'),
]
addition = '\r\n' + ''.join(f'- CHG-{1345 + index}，{at}，Codex编排Agent，{path}。{reason}\r\n\r\n'
                             for index, (path, reason) in enumerate(entries))
CHANGES.write_bytes(old[CHANGES] + addition.encode('utf-8'))
assert CHANGES.read_bytes().startswith(old[CHANGES])
after_numbers = [int(value) for value in re.findall(r'^- CHG-(\d+)', CHANGES.read_text(encoding='utf-8-sig'), re.MULTILINE)]
assert after_numbers == numbers + list(range(1345, 1355))
for path_text, expected in protected.items():
    assert identity(Path(path_text)) == expected, path_text
for row in received['current']:
    if not row['exists']:
        assert not (ROOT / row['path']).exists()
for path in (WORK114, WORK115, ARCH, STATE):
    assert path.read_bytes().endswith(old[path])

save('delivery-proof.json', {
    'created_at': at, 'state': 'saved_readback_complete_pending_manual_transfer',
    'TASK': 'TASK-115', 'R': 'R-109', 'round': 'review-01',
    'card': record(CARD), 'contract_equal': CARD.read_bytes() == contract,
    'permit': record(OUT / 'continuation-permit.json'),
    'input_manifest': record(OUT / 'input-manifest.json'),
    'window': record(OUT / 'window-assignment.json'),
    'new_shared_documents': [record(path) for path in (WORK114, WORK115, ARCH, STATE, CHANGES)],
    'old_doc_bytes_preserved': True, 'original_audit_card_preserved': record(backup / CARD.name),
    'protected_identity_count': len(protected), 'protected_identity_mismatches': [],
    'known_missing_old_outputs_preserved': list(received['manifest']['known_absent_outputs']),
    'required_sections_present': True, 'new_card_no_stars_or_tables': True,
    'CHG_added': list(range(1345, 1355)), 'next_CHG': 1355,
    'four_defects_state': '开放待原115独立增量复核，不自签关闭',
    'TASK114_dispatch': '已返回/工程封存', 'TASK115_review01_dispatch': '待人工转交',
    'TASK116_allocated': False, 'product_execution_by_orchestrator': 0,
})
print(json.dumps({'state': 'published_and_readback_verified', 'card': record(CARD),
                  'architecture': 'v1.29', 'execution': 'v2.53', 'CHG': '1345—1354',
                  'product_execution': 0, 'dispatch': '待人工转交'}, ensure_ascii=False))
