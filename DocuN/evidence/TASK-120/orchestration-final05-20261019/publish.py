"""主控核证及一次完整收尾合同；仅标准库文件操作，不运行产品。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import time

START = time.monotonic()
ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
E = ROOT / 'DocuN/evidence/TASK-120/execution'
C = E / 'validation-04'
assert ROOT == Path('D:/shspic/project_NO3_RetroLume-agent').resolve()
assert not (HERE / 'save-proof.json').exists(), '已保存，不重复发布'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path, raw, new=False):
    if isinstance(raw, str):
        raw = raw.encode('utf-8')
    assert path.resolve().is_relative_to(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb' if new else 'wb') as handle:
        handle.write(raw)
    assert path.read_bytes() == raw


def save(path, value):
    write(path, json.dumps(value, ensure_ascii=False, indent=2) + '\n', True)


now = datetime.now(timezone(timedelta(hours=8))).isoformat()
rules = load(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
for row in rules:
    assert sha(Path(row['absolute_path']).read_bytes()) == row['sha256'], row['relative_path']
b = load(E / 'budget.json')
assert b['counts']['roots'] == b['caps']['roots'] == 24
assert b['counts']['api_starts'] == b['caps']['api_starts'] == 24
assert b['active_root'] is None and b['active_command'] is None
assert len(b['failures']) == 88
assert b['counts']['provider_calls'] == b['counts']['actual_fee_microunits'] == 0
identity = load(C / 'final-file-identities.json')
assert identity['product_changed_files'] == 1
assert identity['final_product_matches_root24_as_run'] is True
mapping = {x['path']: x['sha256'] for x in identity['all_current_paths']}
mapping.update({x['path']: x['after_sha256'] for x in identity['new']})
checks = []
for path, expected in sorted(mapping.items()):
    actual = sha((ROOT / path).read_bytes()) if (ROOT / path).is_file() else None
    assert actual == expected, path
    checks.append({'path': path, 'sha256': actual, 'match': True})
report = ROOT / 'DocuN/results/TASK-120-result.md'
raw = report.read_bytes()
marker = '# TASK-120 / R-114 — 集中修复03增量结果（未完整，Q继续冻结）'.encode()
suffix = raw[raw.index(marker):]
assert len(suffix) == 53732
assert sha(suffix) == '199325438bc74bba2e08de02525ed70f77f62fd59c9e0679740a6be90919af9c'
stop = load(C / 'final-stop-proof.json')
assert stop['all_fresh_stop_dimensions_confirmed'] is True and stop['root_count'] == 24
receipt = load(C / 'command-055.receipt.json')
assert receipt['exit_code'] == 0 and receipt['tree_empty'] is True
exercise = load(C / 'original-exercise-positive.json')
assert exercise['status'] == 'PASS' and exercise['receipt']['status'] == 'committed'
assert exercise['007']['read_status'] == 'committed_current'
ui_cases = []
ui_paths = [E / 'root-23-batch-01-ui-all-proof.json', E / 'root-24-batch-01-ui-remaining-proof.json']
for path in ui_paths:
    proof = load(path)
    assert proof['status'] == 'PARTIAL_FOR_LISTED_CHAINS'
    assert proof['real_PG'] and proof['real_Windows_SUP']
    assert all(row['response_sha256'] == row['file_sha256'] for row in proof['assets'])
    assert not proof['external_attempts']
    ui_cases.extend(proof['cases'])
assert len(ui_cases) == 4 and all(x['status'] == 'PASS' for x in ui_cases)
input_paths = [report, E / 'budget.json', E / 'events.jsonl', C / 'final-review-index.json',
               C / 'final-file-identities.json', C / 'final-stop-proof.json', C / 'command-055.receipt.json',
               C / 'original-exercise-positive.json', C / 'financial-summary.json',
               C / 'source.diff', C / 'fixture.diff', C / 'remaining-gaps.json',
               C / 'copied-control-reconciliation.json', C / 'memory-display-PG.json',
               ROOT / 'backend/tests/fixtures/task120/pg_boundaries.py',
               ROOT / 'backend/tests/fixtures/task120/recovery_races.py'] + ui_paths
inputs = [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p.read_bytes()), 'bytes': p.stat().st_size}
          for p in input_paths]
for name in ('budget.json', 'events.jsonl'):
    write(HERE / 'returned-snapshot' / (name + '.bytes'), (E / name).read_bytes(), True)
save(HERE / 'input-verification.json', {
    'time': now, 'task': 'TASK-120', 'R': 'R-114', 'rules_match': len(rules),
    'file_checks': checks, 'inputs': inputs, 'old_report_suffix_exact': True,
    'exercise_committed_fact': exercise['007'], 'four_limited_normal_UI_cases': ui_cases,
    'UI_whole_reports_still_PARTIAL': True, 'late_fences_not_passed': True,
    'scope_503_COMMIT_state_unconfirmed': True,
    'old_stop_observation_2026_10_19_114050_UTC_not_main_live_query': True,
    'resource_holding_minutes': round(b['runtime_holding_union_seconds'] / 60, 3),
    'no_main_product_import_compile_tests_PG_Docker_API_Job_Browser_provider_Git': True,
})
old_caps = dict(b['caps'])
caps = dict(old_caps)
caps.update(roots=64, pg_starts=64, api_starts=96, browser_starts=16,
            frontend_builds=8, native_business_sessions=128, http=10000)
permit = {
    'id': 'TASK-120-Q-PREP-FINALIZATION-05-20261019', 'issued_at': now,
    'task': 'TASK-120', 'R': 'R-114', 'parent_permit': b['current_permit_id'],
    'kind': 'prospective_TESTONLY_complete_remaining_matrix_not_Q_activation',
    'receiver': 'A_special_strongest_available_new_exclusive_engineering_window',
    'old_Aplus_window_must_remain_stopped': True,
    'old_counts_at_return': b['counts'], 'old_caps': old_caps, 'new_cumulative_caps': caps,
    'additional_cap_allowances': {k: caps[k] - old_caps[k] for k in old_caps},
    'old_command_wall_cap_seconds': 28800, 'command_wall_cap_seconds': 57600,
    'old_conservative_command_wall_seconds_retained': b['command_wall_conservative_upper_seconds'],
    'old_holding_union_cap_seconds': 14400, 'runtime_holding_union_cap_seconds': 21600,
    'old_holding_seconds_retained': b['runtime_holding_union_seconds'],
    'actual_first_tool_utc_unchanged': b['actual_first_tool_utc'],
    'calendar_deadline_utc_unchanged': b['calendar_deadline_utc'],
    'complete_finish_window_seconds_from_actual_receipt': 86400,
    'new_matrix_grant_until': 'min(actual_receipt_plus_24h, original_calendar_deadline_minus_1800s)',
    'old_grants_and_activity_expiries_not_extended_or_rebound': True,
    'save_only_last_seconds': 1800, 'root_ids_begin_at': 25,
    'real_root_cap_seconds': 1800, 'root_cleanup_reserve_seconds': 120,
    'old_failures_retained': 88, 'TASK117_old_failures_retained': 81,
    'container_id': 'b89522070d4b64fc67efed810852ccc21948058f154bf4fa1889f4d8d69a102f',
    'container_name': 'retrolume-task120-qprep-pg1', 'volume': 'retrolume-task120-qprep-data',
    'image_id': 'sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f',
    'ports': {'pg': 55480, 'api': 18120},
    'old_databases_readonly_reconciliation_no_new_dispatch': ['retrolume_task120_flow', 'retrolume_task120_budget_01', 'retrolume_task120_budget_02'],
    'new_independent_TESTONLY_database': 'retrolume_task120_matrix_final',
    'new_database_fixture_slot': 'matrix-final',
    'new_database_create_attempt_cap': 1, 'new_database_objects_cap': 1,
    'new_application_role_if_needed': 'retrolume_task120_matrix_app',
    'no_new_container_or_volume_or_activity_UUIDs': True,
    'old_PG_financials_unknowns_and_immutable_roots_retained': True,
    'new_TESTONLY_fixture_not_revival_of_old_budget_or_real_grant': True,
    'fixed_roster_48_28_24_global_100_25_same_in_new_fixture': True,
    'resource_labels_keep_original_permit_id': True,
    'memory_minimum_MiB': {'PG_API': 512, 'browser_single_headless_page': 512, 'stop_below_two_samples': 256},
    'memory_poll_seconds': 1, 'do_not_disable_browser_sandbox_or_other_security': True,
    'main_did_not_mutate_engineering_ledger': True,
    'executor_append_only_adoption_after_actual_receipt_only': True,
    'real_Q': 'FROZEN', 'real_provider_fee_preview_Git_new_budget': 0,
}
save(HERE / 'permit.json', permit)

state_path = ROOT / 'DocuS/执行动态文档.MD'
arch_path = ROOT / 'DocuS/架构动态文档.MD'
card_path = ROOT / 'DocuN/tasks/TASK-120.md'
decision_path = ROOT / 'DocuN/results/TASK-120-work-decision.md'
changes_path = ROOT / 'DocuS/文档变更记录.MD'
old = {p: p.read_bytes() for p in (state_path, arch_path, card_path, decision_path, changes_path)}
assert '文档v2.78' in old[state_path].decode('utf-8-sig')[:150]
assert '文档v1.50' in old[arch_path].decode('utf-8-sig')[:150]
assert 'CHG-1541' in old[changes_path].decode('utf-8-sig')[-4000:]
for path, content in old.items():
    write(HERE / 'before' / (path.name + '.bytes'), content, True)

decision = f'''# TASK-120 / R-114 主控完整收尾05裁定（当前有效）

{now}。用户带回续验04并明确“下一次必须完成”。主控核7规则、199最终身份/最后单产品diff、055退出/停机、原练习及四个有限UI成功case、金融原件和旧结果后缀。整体仍部分通过，未到稳定终审点；原报告PARTIAL/FAIL不改绿。练习和有限五入口正常UI证据按原对象收存，权限/ACK/K2/晚到未过，不自签全部通过。

反复停线的原因分三层：早期真实Q读锁/finite字段/记忆显示等代码缺陷；后期夹具错误（合法cache/错误码、回执字段、页面刷新）和一次失败前未逐例保存证据；编排每次仅4个启动余量且依赖串联过度，使普通修正反复转卡。24根已用满是任务卡次数，不是GPT账号/真实API费用。实际自有资源持有1875.827295秒约31.2638分钟；保守wall含未知预留，不是CPU精确投入。主控承认该资源/依赖组织不当，现改变方法，不再机械加4次。

A特殊指派最强可用工程新窗独占接续，原A+保持停止；同TASK120/R114，不占121，不冒称独审。先只读核旧budget02 scope503的真实COMMIT/head/scope与模型received事实，不重放不猜回滚；修逐例checkpoint/精确错误码/独立失败隔离，再完整做剩余矩阵和晚到。普通修复/定向复检在同窗持续完成，真实停止条件保留，不保证未知缺陷为零或允许假通过。

旧flow/budget02今晚20:19:22+08批准将到期，不改旧grant/root/活动/账，不赶倒计时。主控明确准许同CID/卷新增一个独立TESTONLY矩阵库retrolume_task120_matrix_final，原001—014/profile及同fixed roster/100-25合成上限，正常生产初始化/选择接口。新样本以实际新身份和冻结文字建立独立不可变TESTONLY root，终点=min实际接收+24h/原96h减保存期；不复制旧批准或旧结果为新权利，不给真实Q/费用，旧三库只读核证。此为验证fixture资源扩展，不是产品权限/金融模型变更。

一次完整收尾窗至多实际接收24h且受原96h/末1800门，累计兜底caps根64/PG64/API96/Browser16/build8/Native128/HTTP10000、wall57600/持有21600；原24/23/24/6/4/36/800、88失败、旧117历史与所有旧投入未知预留保留。次数照记但不为每4次普通修正另转卡；无新容器/卷/活动UUID，真实provider/费用/preview/Git0。512MiB单页低内存/连续两低于256清场不变，不绕审批/安全/系统资源。

完整卡/permit已保存待人工转交新A窗，尚未实际接收或执行；主控未改工程账/产品/结果或运行PG/Browser。高风险稳定后仍需原118独立归属集中终审，Q冻结，旧S不重开，STEP018整体/019/020/M1/项目未放行。

---

# 以下旧裁定原字节保留

'''
state = f'''# 执行动态文档

文档v2.79，2026-10-19，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.51、task_model/07。以下v2.78原字节保留。

## TASK120续验04返回；有限正常链收存，A新窗一次完整收尾05待转交

{now}。主控核7规则、199当前身份/最后读取显示diff、055退出/停机、练习committed/007和根23/24四个有限UI PASS case、原金融快照及旧结果后缀，未跑业务/独审。整体部分通过，权限/ACK/K2/晚到围栏未闭合，不到稳定终审点；旧PARTIAL/FAIL照留，正常链不重建证明。

原根24/24、PG23/24、API24/24、Browser6/8、build4/6、Native36/48、HTTP800/5000、88失败记录，active_root/command空；wall保守24382.005564/28800、持有1875.827295/14400约31.264分钟，旧unknown预留/117历史保持。055在2026-10-19T11:40:50Z核193 PID/birth/89 Job/精确CID stopped/Pid0/两端口，自身另有tree_empty/exit0，仅原时点不是主控现时Docker查验。

正常教学练习/五入口有限UI已成；余项卡在正确tail_unconfirmed码误报、先前checkpoint不足、head列表未刷新及scope503未核COMMIT。反复4根续批与依赖串联是主控组织问题，启动次数不是GPT帐号/真实API费用。新A最强可用工程窗独占接续、原A+停止，先核旧503再逐例保存/隔离失败/卡内修复，优先原有效证据，不重复C12等。

前向FINALIZATION-05：实际接收至多24h且受原96h/末1800门；累计兜底caps根64/PG64/API96/Browser16/build8/Native128/HTTP10000/wall57600/持有21600，历史全部保留。无新容器/卷，仅同原CID/卷新增确切独立TESTONLY逻辑库matrix_final及必要最小角色，原三库只读核证/旧root和期限不延长。新root以真实新实例/冻结数据/固定roster建立，截止不晚于收尾窗，不恢复旧预算/批准，不授真实Q。

同TASK120/R114，未占121；完整合同/permit已保存待转交，未虚记新窗收到/开始。Q/provider实际费用/preview/Git仍0，旧S有限关闭不重开，STEP018整体/019/020/M1/项目不签通过。主控未改产品/工程结果/账或执行资源操作。orchestration-final05-20261019保存核证/许可/旧共享快照，CHG1542—1546，下一1547。

## 以下为v2.78及更早历史

'''
arch = f'''# 架构动态文档

文档v1.51，2026-10-19，Asia/Shanghai。需求v1.4、执行动态v2.79、task_model/07；以下v1.50原字节保留。

## Q v2正常教学练习及有限五入口UI已有证据，安全余项未闭合

{now}。续验04仅teaching_repository读取显示投影新增：明确null-memory teaching.v3显示为未选，实际binding/v2/未知上下文继续保守；资格/正文守卫、memory仓储、DDL/schema/SUP/时钟不改。该修补与最终产品字节已在根24真实PG/UI绑定。原练习/007及正常教学/面试/检索/legacy/HTML有限UI成立，owner/view按列明范围继承；不称head/scope/namespace/DataContext已过。

权限回调在正确control_tail_unconfirmed码处误报、ACK未装载，旧scope变更503的COMMIT/head/scope未知且模型007 received/费用保留。最后错误码/checkpoint/刷新/安全SQLSTATE诊断为夹具离线增量，不当运行成功；必须核持久事实后修真实原因。后续新矩阵样本仅独立TESTONLY fixture，不改原产品根不可变/实例隔离/金融上限/来源与记忆资格，不延长旧root权利。

多数正常主链与C12既有证据不重跑；完整安全/晚到矩阵和稳定集中独审仍待。Q/STEP018整体/019/020/M1/项目未放行，主控无产品实现运行。

## 以下为v1.50及更早历史

'''
for row in inputs:
    assert sha((ROOT / row['path']).read_bytes()) == row['sha256'], row['path']
write(decision_path, decision.encode() + old[decision_path])
write(arch_path, arch.encode() + old[arch_path])
write(state_path, state.encode() + old[state_path])
write(card_path, (HERE / 'contract-05.md').read_bytes() + old[card_path])
entries = [
    (1542, 'DocuN/results/TASK-120-work-decision.md', '置顶完整收尾05裁定，明确反复停线原因/有限成功/旧503先核/一次收尾新独立测试样本'),
    (1543, 'DocuS/架构动态文档.MD', 'v1.51登记最后memory显示投影和有限正常UI/练习实证，安全余项未闭合'),
    (1544, 'DocuS/执行动态文档.MD', 'v2.79登记续验04返回/部分通过、真实累计/停止时点、A新窗完整收尾待转交'),
    (1545, 'DocuN/tasks/TASK-120.md', '置顶完整收尾05，24h有限收尾/逐例checkpoint/普通修复卡内/独立TESTONLY矩阵库，旧合同原字节保留'),
    (1546, 'DocuN/evidence/TASK-120/orchestration-final05-20261019', '证据核证/精确前向permit/旧共享与返回账快照/保存读回；主控没有改工程账或运行产品'),
]
addition = '\n\n' + '\n\n'.join(f'- CHG-{n:04d}，{now}，Codex编排Agent，{path}。{note}。' for n, path, note in entries) + '\n'
write(changes_path, old[changes_path] + addition.encode())
for path in (state_path, arch_path, card_path, decision_path):
    assert path.read_bytes().endswith(old[path]), path
for row in inputs:
    assert sha((ROOT / row['path']).read_bytes()) == row['sha256'], row['path']
save(HERE / 'save-proof.json', {
    'saved_at': now, 'read_back': True, 'old_suffixes_byte_exact': True, 'engineering_inputs_unchanged': True,
    'main_metadata_seconds': round(time.monotonic() - START, 6),
    'files': [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p.read_bytes())}
              for p in (decision_path, state_path, arch_path, card_path, changes_path)],
})
print(json.dumps({'saved': True, 'rules': len(rules), 'identities': len(checks), 'engineering_inputs_unchanged': True,
                  'new_permit': permit['id'], 'next_CHG': 1547}, ensure_ascii=False))
