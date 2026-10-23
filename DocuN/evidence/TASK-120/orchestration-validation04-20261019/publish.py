"""主控只读核证/前向剩余验证合同；不导入产品或运行资源。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import time

START = time.monotonic()
ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
E = ROOT / 'DocuN/evidence/TASK-120/execution'
C = E / 'repair-03'
assert ROOT == Path('D:/shspic/project_NO3_RetroLume-agent').resolve()
assert not (HERE / 'save-proof.json').exists(), '已保存，先核断点'


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
assert b['counts']['roots'] == b['caps']['roots'] == 20
assert b['active_root'] is None and b['active_command'] is None
assert len(b['failures']) == 77
assert b['counts']['provider_calls'] == b['counts']['actual_fee_microunits'] == 0
identity = load(C / 'final-file-identities.json')
mapping = {x['path']: x['sha256'] for x in identity['all_current_paths']}
mapping.update({x['path']: x['after_sha256'] for x in identity['new']})
checks = []
for path, expected in sorted(mapping.items()):
    actual = sha((ROOT / path).read_bytes()) if (ROOT / path).is_file() else None
    assert actual == expected, path
    checks.append({'path': path, 'sha256': actual, 'match': True})
report = ROOT / 'DocuN/results/TASK-120-result.md'
raw = report.read_bytes()
marker = '# TASK-120 / R-114 — 断点纠正02结果（当前事实优先）'.encode()
suffix = raw[raw.index(marker):]
assert len(suffix) == 43266
assert sha(suffix) == '14ffc493339ce321c6fb41bacf020d8cc76932770319b71f320222f5fa043443'
stop = load(C / 'final-stop-proof.json')
assert stop['all_fresh_stop_dimensions_confirmed'] is True
assert stop['root_count'] == 20
receipt = load(C / 'command-050.receipt.json')
assert receipt['exit_code'] == 0 and receipt['tree_empty'] is True
tests = load(C / 'repair-tests-050.json')
assert tests['tests'] == 11 and tests['failures'] == tests['errors'] == 0 and tests['new_PG'] is False
diagnosis = load(C / 'readonly-diagnosis.json')
assert diagnosis['checks']['teaching_before']['returned_code'] == 'teaching_validation_unavailable'
assert diagnosis['checks']['teaching_after']['returned_code'] is None
assert diagnosis['checks']['teaching_read_fix_verified'] is True
positives = {}
for name in ('teaching-plan-reconciled-positive.json', 'flow-interview-reconciled-positive.json',
             'budget-02-interview-reconciled-positive.json', 'legacy-html-positive.json'):
    value = load(C / name)
    assert value['status'].startswith('PASS'), name
    positives[name] = value
    if 'model' in value:
        assert value['model']['read_status'] == 'committed_current', name
input_paths = [report, E / 'budget.json', E / 'events.jsonl', C / 'final-review-index.json',
               C / 'final-file-identities.json', C / 'final-stop-proof.json', C / 'source.diff', C / 'fixture.diff',
               C / 'readonly-diagnosis.json', C / 'repair-tests-050.json', C / 'command-050.receipt.json',
               C / 'remaining-gaps.json', C / 'retained-original-Q-witness.json',
               ROOT / 'backend/tests/fixtures/task120/repair03.py']
input_paths += [C / name for name in positives]
inputs = [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p.read_bytes()), 'bytes': p.stat().st_size}
          for p in input_paths]
for name in ('budget.json', 'events.jsonl'):
    write(HERE / 'returned-snapshot' / (name + '.bytes'), (E / name).read_bytes(), True)
save(HERE / 'input-verification.json', {
    'time': now, 'task': 'TASK-120', 'R': 'R-114', 'rules_match': len(rules), 'file_checks': checks,
    'inputs': inputs, 'old_report_suffix_exact': True, 'final_11_tests_are_offline_only': True,
    'read_diagnosis_before_after_checked': True, 'limited_positive_receipts': positives,
    'positive_currentness_at_original_PG_read_only': True,
    'later_final_q_context_PathNode_delta_not_PG_verified': True,
    'old_file_gate_present': (C / 'flow-interview-positive.json').exists(),
    'reconciled_actual_positive_present': True,
    'stop_proof_time_is_2026_10_19_103953_UTC_not_main_live_observation': True,
    'main_product_import_compile_tests_PG_Docker_API_Job_Browser_provider_Git': 0,
})
old_caps = dict(b['caps'])
caps = dict(old_caps)
caps.update(roots=24, pg_starts=24, api_starts=24)
permit = {
    'id': 'TASK-120-Q-PREP-VALIDATION-04-20261019', 'issued_at': now,
    'task': 'TASK-120', 'R': 'R-114', 'parent_permit': b['current_permit_id'],
    'kind': 'prospective_TESTONLY_remaining_validation_same_scope_not_Q_activation',
    'old_counts_at_return': b['counts'], 'old_caps': old_caps, 'new_cumulative_caps': caps,
    'additional_cap_allowances': {k: caps[k] - old_caps[k] for k in old_caps},
    'old_command_wall_cap_seconds': 25200, 'command_wall_cap_seconds': 28800,
    'old_conservative_command_wall_seconds_retained': b['command_wall_conservative_upper_seconds'],
    'runtime_holding_union_cap_seconds_unchanged': 14400,
    'old_holding_seconds_retained': b['runtime_holding_union_seconds'],
    'actual_first_tool_utc_unchanged': b['actual_first_tool_utc'],
    'calendar_deadline_utc_unchanged': b['calendar_deadline_utc'],
    'save_only_last_seconds': 1800, 'root_ids_begin_at': 21,
    'real_root_cap_seconds': 1800, 'root_cleanup_reserve_seconds': 120,
    'old_failures_retained': 77, 'TASK117_old_failures_retained': 81,
    'container_id': 'b89522070d4b64fc67efed810852ccc21948058f154bf4fa1889f4d8d69a102f',
    'container_name': 'retrolume-task120-qprep-pg1', 'volume': 'retrolume-task120-qprep-data',
    'image_id': 'sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f',
    'ports': {'pg': 55480, 'api': 18120},
    'database_allowlist': ['retrolume_task120_flow', 'retrolume_task120_budget_01', 'retrolume_task120_budget_02'],
    'no_new_container_volume_database_or_activity_ids': True,
    'resource_labels_keep_original_permit_id': True,
    'grant_and_activity_expiry_not_extended': True,
    'flow_memory_expiry_no_later_than': '2026-10-19T12:19:22.457756Z',
    'memory_minimum_MiB': {'PG_API': 512, 'browser_single_headless_page': 512, 'stop_below_two_samples': 256},
    'browser_old_gate_768MiB_not_retroactively_changed': True,
    'browser_single_process_group_one_context_one_page_no_extra_workers': True,
    'memory_poll_seconds': 1, 'do_not_disable_browser_sandbox_or_other_security': True,
    'normal_positive_and_UI_before_destructive_mutation_cases': True,
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
assert '文档v2.77' in old[state_path].decode('utf-8-sig')[:150]
assert '文档v1.49' in old[arch_path].decode('utf-8-sig')[:150]
assert 'CHG-1536' in old[changes_path].decode('utf-8-sig')[-4000:]
for path, content in old.items():
    write(HERE / 'before' / (path.name + '.bytes'), content, True)

decision = f'''# TASK-120 / R-114 主控续验04裁定（当前有效）

{now}。集中修复03已返回，总验收仍部分通过，完整候选未达稳定终审点。主控核7规则、最终产品/夹具身份、五产品diff、锁诊断前后、11项最终离线/050回执、四有限成功记录及旧报告原字节后缀。未执行业务或独立审计；不将最终PathNode补丁的离线证明当练习PG通过。

真实增量支持收存：根17确认锁分类根因/修后读；flow面试、已选记忆面试、legacy续问、HTML description及教学plan均按原as-run和PG/SUP/007子事实保留。原汇总KeyError/FAIL不改绿，但不因其失败重发已提交原键。C12等旧充分项不重跑。

实际余项为accepted/unclaimed教学练习的最后字段修补复验、权限/ACK/K2/source-scope-memory矩阵、最终UI及金融快照。现后续gate仍以旧positive文件存在判断，而真实成功另存reconciled文件，必须按业务键/operation/query摘要与原件核证映射修消费者，不造PASS文件。正常业务/UI必须先于破坏来源/范围/记忆/head的测试，避免自毁前置。

当前20/20根已满，PG19/API18/Browser3/build4/Native25/HTTP353、77失败记录、wall保守21629.019209/25200、持有1593.890295/14400及所有旧unknown预留保留。前向许可VALIDATION-04累计cap根24/PG24/API24/wall28800，其余cap不变，无新create/库/活动/provider/实际费用/preview/Git。原截止及flow/budget02当日20:19:22+08更早期限不延长。

用户低内存串行要求内，唯一headless单context单页Browser门前向改512MiB，PG/API512保持、1秒采样连续两次<256精确清场；不并行/不关sandbox，不追认根20原768门未过为已启动。真实内存仍不足则只停该层，不要求用户腾内存，不持PG循环等门。

同号原A+工程窗只补剩余验证，完整卡保存待人工转交；原报告/工程budget/events未改。源码高风险完整稳定后仍须原118独立归属集中终审。Q冻结，旧S有限验收不重开，STEP018整体/019/020/M1/项目不签通过。主控没有接管执行。

---

# 以下旧裁定原字节保留

'''
state = f'''# 执行动态文档

文档v2.78，2026-10-19，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.50、task_model/07。以下v2.77原字节保留。

## TASK120修复03已返回；多数正常模型链已成，续验04待转交

{now}。主控核7规则/最终产品与fixture身份/五产品diff、锁诊断前后、050离线11项及退出/停机原件、4有限成功记录和旧结果后缀，未执行业务/独审。总验收部分通过，未到完整稳定终审点；不把原汇总FAIL改绿，也不因KeyError重发已COMMIT原键。

根17已确认并修复教学/面试/HTML只读闭包误取排他；真实flow面试、创建时已选记忆面试、legacy续问、HTML description及教学plan/007有限成果收存，原UNKNOWN/Q序列/费用不清不退。最终PathNode字段补丁仅离线通过，教学练习原accepted/unclaimed、权限/ACK/K2/失效竞态、最终UI及金融快照仍待补。C12等充分旧证据直接继承。后续旧文件gate须改读核证业务事实，正常UI先于破坏性失效测试。

累计根20/20、PGstart19/20、API18/20、Browser3/8、build4/6、Native25/48、HTTP353/5000、77记录失败；wall保守21629.019209/25200、持有1593.890295/14400、所有旧预留/117历史保持，active_root/command空。050在2026-10-19T10:39:53Z实核160 PID/birth/76 Job/原CID Running=false/Pid0/两端口并自身tree_empty/exit0；主控只继承该原时点，没有现时Docker查询。

前向VALIDATION-04累计根24/PG24/API24/wall28800，其余cap保持，新增create/provider/实际费用/preview/Git0；固定CID/卷/三库/roster/原截止不变，flow/budget02当日20:19:22+08更早期限不延长。唯一headless单context单页Browser启动门前向512MiB，约1秒采样连续两次<256精确清场，不关sandbox/不要求用户腾内存，旧768门未过不追认为启动。

原A+工程窗单一执行者，同号完整续验04已保存待人工转交，未记已收到/开始；不占新TASK121，不提前派独审。主控未改产品、结果或工程账。Q冻结，旧S有限验收不重开，STEP018整体/019/020/M1/项目未通过。证据及新permit在orchestration-validation04-20261019；CHG1537—1541，下一1542。

## 以下为v2.77及更早历史

'''
arch = f'''# 架构动态文档

文档v1.50，2026-10-19，Asia/Shanghai。需求v1.4、执行动态v2.78、task_model/07；以下v1.49原字节保留。

## Q v2锁读分类修复及多数模型链已验证，权限/最终UI未闭合

{now}。TASK120五产品变化：q_store精确列教学快照/面试验证/HTML验证只读闭包；interview policy/repository允许精确obsolete UNKNOWN在无其他pending时正常本地abandon；q_context接纳已接受命令配置摘要及已核同活动父规范history，并将PathNode字段限到task.path_nodes整数项；q_gateway仅记安全拒绝码/路径/摘要。金融/权限主模型及001—014文件不变。

真实根17前后证实锁升级冲突消失；flow面试、已选记忆面试、legacy followup、HTML description及教学plan/007成立。最终PathNode/rationale补丁仅离线11项，练习尚无修后PG；原三浏览器FAIL加载子事实沿用，修复03新增Browser0因原门不足，最终UI未过。模型成功按原as-run继承，不把最后增量冒充所有链已跑最终字节。

剩余权限/ACK/K2/source-scope-memory竞态和完整UI仍待当前正常前提下验证，旧C12共同100门不重跑。恢复修正证据消费者与测试顺序，不增持久结构/新平台。整体工程未完成，稳定后仍集中增强终审；Q/STEP018整体/019/020/M1/项目未放行，主控无产品运行。

## 以下为v1.49及更早历史

'''
for row in inputs:
    assert sha((ROOT / row['path']).read_bytes()) == row['sha256'], row['path']
write(decision_path, decision.encode() + old[decision_path])
write(arch_path, arch.encode() + old[arch_path])
write(state_path, state.encode() + old[state_path])
write(card_path, (HERE / 'contract-04.md').read_bytes() + old[card_path])
entries = [
    (1537, 'DocuN/results/TASK-120-work-decision.md', '置顶续验04裁定，有限收存多数真实模型链，按事实修复gate/排序，保留余项'),
    (1538, 'DocuS/架构动态文档.MD', 'v1.50登记五产品变化/根17确认/真实模型链与最终字段补丁仅离线边界'),
    (1539, 'DocuS/执行动态文档.MD', 'v2.78登记修复03返回/部分通过/真实累计/停止时点及前向剩余验证许可'),
    (1540, 'DocuN/tasks/TASK-120.md', '置顶同号续验04，正常UI先于失效矩阵/只补余项/单页低内存，旧合同保留'),
    (1541, 'DocuN/evidence/TASK-120/orchestration-validation04-20261019', '有限证据核证/精确permit/旧共享和返回账快照/保存证明；主控未改工程账或执行业务'),
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
                  'new_permit': permit['id'], 'next_CHG': 1542}, ensure_ascii=False))
