"""主控有限证据核证及同号合并修复合同保存，无产品导入/业务运行。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import time

start = time.monotonic()
ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
E = ROOT / 'DocuN/evidence/TASK-120/execution'
C = E / 'continuation-02'
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
rule_checks = []
for row in rules:
    assert sha(Path(row['absolute_path']).read_bytes()) == row['sha256'], row['relative_path']
    rule_checks.append({'path': row['absolute_path'], 'sha256': row['sha256'], 'match': True})
b = load(E / 'budget.json')
assert b['counts']['roots'] == b['caps']['roots'] == 16
assert b['active_root'] is None and b['active_command'] is None
assert b['counts']['provider_calls'] == b['counts']['actual_fee_microunits'] == 0
assert b['calendar_deadline_utc'] == '2026-10-22T08:41:08.5687758Z'
assert len(b['failures']) == 57
identities = load(C / 'final-file-identities.json')
assert identities['product_delta_this_scope'] == 0
current = {x['path']: x['sha256'] for x in identities['all_current_paths']}
previous_doc = load(E / 'continuation-01/final-file-identities.json')
previous = {x['path']: x['sha256'] for x in previous_doc['current_files'] + previous_doc['new_files']}
products = [p for p in current if p.startswith(('backend/app/', 'frontend/src/', 'frontend/dist/'))]
assert all(p in previous and current[p] == previous[p] for p in products)
selected = set(products)
selected.update(x['path'] for x in identities['changed'] + identities['new'])
checks = []
for path in sorted(selected):
    expected = current[path]
    actual = sha((ROOT / path).read_bytes()) if (ROOT / path).is_file() else None
    assert actual == expected, path
    checks.append({'path': path, 'sha256': actual, 'match': True})
report = ROOT / 'DocuN/results/TASK-120-result.md'
raw_report = report.read_bytes()
marker = '# TASK-120 / R-114 — 续作01结果与接续断点'.encode()
assert sha(raw_report[raw_report.index(marker):]) == '6a6256bcc313a630845d6a29c7c8245a71f03420f4aa3b90293708f7ec2b236c'
stop = load(C / 'final-stop-proof.json')
assert stop['all_fresh_stop_dimensions_confirmed'] is True
assert stop['docker_realtime']['Id'] == 'b89522070d4b64fc67efed810852ccc21948058f154bf4fa1889f4d8d69a102f'
assert stop['docker_realtime']['state']['Running'] is False and stop['docker_realtime']['state']['Pid'] == 0
receipts = []
for n in (39, 40, 41):
    path = C / f'command-{n:03d}.receipt.json'
    value = load(path)
    assert value['exit_code'] == 0 and value['tree_empty'] is True
    receipts.append({'path': path.relative_to(ROOT).as_posix(), 'exit_code': 0,
                     'tree_empty': True, 'end_utc': value['end_utc']})
core = load(E / 'root-16-c02-core-result.json')
assert core['outcomes'] == {'teaching_A3': 'FAIL', 'interview': 'FAIL', 'HTML': 'FAIL'}
for mode in ('teaching', 'interview', 'legacy_html'):
    proof = load(E / f'root-16-batch-06-ui-{mode}-proof.json')
    assert proof['status'] == 'FAIL'
    assert proof['assets'] and all(x['response_sha256'] == x['file_sha256'] for x in proof['assets'])

input_paths = [report, E / 'budget.json', E / 'events.jsonl', C / 'final-file-identities.json',
               C / 'final-review-index.json', C / 'final-stop-proof.json', C / 'retained-unknown-witness.json',
               E / 'root-16-c02-core-result.json', E / 'root-16-batch-03-http-timeline.json',
               E / 'root-16-batch-02-failure.json', C / 'fixture.diff', C / 'source.diff',
               C / 'root15-diagnosis.json',
               ROOT / 'backend/app/learning/teaching_adapter.py',
               ROOT / 'backend/app/activities/teaching_repository.py',
               ROOT / 'backend/app/activities/interview_repository.py',
               ROOT / 'backend/app/activities/repository.py',
               ROOT / 'backend/app/data_exit/q_store.py',
               ROOT / 'backend/app/capabilities/q_gateway.py',
               ROOT / 'backend/app/preview/repository.py', ROOT / 'backend/app/learning/service.py']
inputs = [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p.read_bytes()), 'bytes': p.stat().st_size}
          for p in input_paths]
for name in ('budget.json', 'events.jsonl'):
    write(HERE / 'returned-snapshot' / (name + '.bytes'), (E / name).read_bytes(), True)
save(HERE / 'input-verification.json', {
    'time': now, 'task': 'TASK-120', 'R': 'R-114', 'rules': rule_checks,
    'product_paths_unchanged_from_continuation01': len(products), 'file_checks': checks,
    'inputs': inputs, 'report_prior_suffix_byte_exact': True, 'receipts': receipts,
    'stop_proof_is_prior_2026_10_19_055410_UTC_not_new_live_observation': True,
    'three_browser_cases_FAIL_with_asset_identity_subfacts_only': True,
    'classification_finding_grade': 'B: source path deterministic; original inner exception not captured',
    'no_main_product_import_compile_tests_Docker_PG_API_Job_Browser_provider_fee_Git': True,
})
old_caps = dict(b['caps'])
new_caps = dict(old_caps)
new_caps.update(roots=20, pg_starts=20, api_starts=20)
permit = {
    'id': 'TASK-120-Q-PREP-REPAIR-03-20261019', 'issued_at': now,
    'task': 'TASK-120', 'R': 'R-114', 'parent_permit': b['current_permit_id'],
    'kind': 'prospective_TESTONLY_same_scope_cause_first_repair_not_Q_activation',
    'old_counts_at_return': b['counts'], 'old_caps': old_caps, 'new_cumulative_caps': new_caps,
    'additional_cap_allowances': {k: new_caps[k] - old_caps[k] for k in old_caps},
    'old_command_wall_cap_seconds': 21600, 'command_wall_cap_seconds': 25200,
    'old_conservative_command_wall_seconds_retained': b['command_wall_conservative_upper_seconds'],
    'runtime_holding_union_cap_seconds_unchanged': 14400,
    'old_holding_seconds_retained': b['runtime_holding_union_seconds'],
    'actual_first_tool_utc_unchanged': b['actual_first_tool_utc'],
    'calendar_deadline_utc_unchanged': b['calendar_deadline_utc'],
    'save_only_last_seconds': 1800, 'new_root_ids_begin_at': 17,
    'read_only_diagnostic_roots_at_most': 1, 'diagnostic_root_seconds_including_cleanup': 420,
    'diagnostic_cleanup_reserve_seconds': 120, 'normal_root_seconds_including_cleanup': 1800,
    'business_runtime_requires_cause_and_fix_gate_in_contract': True,
    'normal_business_root_cleanup_reserve_seconds': 120,
    'old_failures_retained': 57, 'TASK117_old_failures_retained': 81,
    'container_id': stop['docker_realtime']['Id'],
    'container_name': 'retrolume-task120-qprep-pg1',
    'image_id': 'sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f',
    'volume': 'retrolume-task120-qprep-data', 'ports': {'pg': 55480, 'api': 18120},
    'database_allowlist': ['retrolume_task120_flow', 'retrolume_task120_budget_01', 'retrolume_task120_budget_02'],
    'no_new_container_volume_database_or_activity_ids': True,
    'resource_labels_keep_original_permit_id': True,
    'grant_and_activity_expiry_not_extended': True,
    'memory_and_flow_TESTONLY_expiry_no_later_than': '2026-10-19T12:19:22.457756Z',
    'memory_minimum_MiB': {'PG_API': 512, 'browser': 768, 'stop_below_two_samples': 256},
    'real_Q': 'FROZEN', 'provider_fee_preview_Git_new_budget': 0,
    'main_did_not_mutate_engineering_ledger': True,
    'executor_append_only_adoption_after_actual_receipt_only': True,
}
save(HERE / 'permit.json', permit)
findings = '''# 主控源级诊断（B级，不是独立审计或产品修复）

发送共享policy→gateway._call_original→validate_teaching_request(v2/v3)→read_teaching_command→_teaching_read_snapshot.<locals>.operation→_transaction。

method_name从该闭包实际qualname取到_teaching_read_snapshot；is_read_method既不匹配该名称也不列精确例外。_transaction因此申请exclusive，async_policy继承shared时抛q_policy_upgrade_forbidden；adapter广义except返回teaching_validation_unavailable。存在确定冲突路径，但原日志未捕获内部异常，不冒称唯一动态根因。

面试accepted在全历史model UNKNOWN存在时拒绝interview_pending，不受obsolete排除；local goal不能自动解除。abandon是现有显式业务操作，仅整理已停止实验命令，不恢复Q claim/金融额度/旧槽。主控上一“新goal足够”的判断遗漏此门，现纠正。

observer替身安装、terminal检索缓存、UTF-8均有明确夹具事实。HTML/legacy 409内部拒绝仍未知，须保留安全code和父kind/资格原件，不猜测修生产守卫。

上述诊断只支持定向合并修复，不支持宣布工程已完成或跳过真实PG/SUP及最终独审。
'''
write(HERE / 'source-findings.md', findings, True)

state_path = ROOT / 'DocuS/执行动态文档.MD'
arch_path = ROOT / 'DocuS/架构动态文档.MD'
card_path = ROOT / 'DocuN/tasks/TASK-120.md'
decision_path = ROOT / 'DocuN/results/TASK-120-work-decision.md'
changes_path = ROOT / 'DocuS/文档变更记录.MD'
old = {p: p.read_bytes() for p in (state_path, arch_path, card_path, decision_path, changes_path)}
assert '文档v2.76' in old[state_path].decode('utf-8-sig')[:150]
assert '文档v1.48' in old[arch_path].decode('utf-8-sig')[:150]
assert 'CHG-1531' in old[changes_path].decode('utf-8-sig')[-4000:]
for path, raw in old.items():
    write(HERE / 'before' / (path.name + '.bytes'), raw, True)

decision = f'''# TASK-120 / R-114 主控集中修复03裁定（当前有效）

{now}。断点纠正02已真实返回；整体仍部分通过，未到稳定集中独审点。审批已恢复，039—041实际exit0/树零；平台容量不再是当前阻塞。原根16/16用满，主控本次不执行任何根，只前向签发有根因/修复前置的同号合并许可。

主控核7锁定规则、产品相对续作01零增量及变化/新夹具、4正式bundle、旧报告后缀、3预检回执和041停机原件。三浏览器均FAIL，正式JS/CSS加载身份子事实通过，不能替代业务闭环；A3真实head/查询有限事实收存。C12共同100/25、旧learning first和EOL修补不重跑。

源级确定冲突链为q_gateway共享policy内调用教学v2/v3复核，再经read_teaching_command→_teaching_read_snapshot。私有read方法被is_read_method漏列，_transaction误申请exclusive；async_policy抛q_policy_upgrade_forbidden，随后统一码teaching_validation_unavailable。该B级路径可解释本次症状，尚未动态采到唯一内部异常，不能自签根因已实证。修复必须是精确读分类，禁止放开所有事务或共享锁升级。

面试全历史UNKNOWN门也未被上一主控“只建新goal”处理；现明确允许对精确停止的A2/A3实验命令经原本地abandon整理业务pending，原Q claim/operation/未知费用/槽保留，绝不二发/SQL清账。旧A1永不重发。observer替身安装、合法terminal缓存与UTF-8夹具问题一次合并；HTML/legacy409需先获得准确安全拒绝码/父资格，禁止猜测放宽守卫。

当前16根/PGstart15/API11/Browser3/build4/Native13/HTTP240、57失败记录、wall保守17789.126332/21600、持有1258.061295/14400全保留。新许可REPAIR-03将累计cap根20、PGstart20、API20、wall25200；其余原cap不变，无create/provider/实际费用/preview/Git新增。至多一只读诊断根420秒，真正正常业务根必须先完成合同根因/修复/有限前置门；不是再开UI猜内部错误。原首点/96h、所有更早grant/活动期限均不延长，测试库/活动固定，不用换库刷新权益。

原A+工程窗口单一执行者继续，同号完整合同待人工转交；不占TASK121，不派独审，主控没有改产品、结果、budget/events。Q及STEP018整体/019/020/M1/项目不放行，旧S有限验收保留。主控验收仅有限子事实收存。完整合同与许可见同号TASK-120.md及本轮orchestration-repair03-20261019。

---

# 以下旧裁定原字节保留

'''
state = f'''# 执行动态文档

文档v2.77，2026-10-19，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.49、task_model/07。以下v2.76原字节保留。

## TASK120断点02已返回；合并根因修复03待转交

{now}。真实根15/16均结束，产品增量0、三浏览器业务例FAIL、ACK/K2等依赖未跑；当前候选不通过完整工程验收，不到稳定独审点。有限收存A3新head/新查询与正式JS/CSS响应hash；旧C12共同100门、legacy first/EOL等充分项继承，不重跑。主控核7规则、未变产品/变化夹具、旧结果后缀、039—041回执与041停止身份，非业务复跑或独审。

当前根16/16、PGstart15/16、API11/16、Browser3/8、build4/6、Native13/48、HTTP240/5000、57失败记录，active_root/command空；wall保守17789.126332/21600、持有1258.061295/14400及旧未知预留/117全部旧账保留。审批服务已恢复，不再列旧容量阻塞；本轮最低内存835289088且无压力，失败不归因于内存。041在2026-10-19T05:54:10Z核120 PID/birth、58 Job、原CID stopped/Pid0及两端口，041自身另有tree_empty/exit0；这是原停止时点，不是主控当前Docker查询。

新源级冲突：Q共享发送锁内教学v2/v3验证读取_teaching_read_snapshot，被is_read_method漏列而误申请排他，触发禁止升级并被adapter统一包装。路径B级确定，原运行内异常未采到，不称唯一动态根因。主控上一面试“新goal即足够”也漏全历史UNKNOWN门；本次改为先精确已停实验命令的正常本地abandon/状态回读，领取/未知/槽/财务不清不退。合并observer装配、缓存终态/UTF-8夹具修正与HTML/legacy真实拒绝诊断。

签发前向附条件REPAIR-03：累计根20/PGstart20/API20/wall25200，其余cap原值，新增create/provider/实际费用/preview/Git0。至多一只读诊断根420秒，其余正常链须先过根因/修复/全链前置门；不直接开UI复制worker失败。固定唯一CID/卷/三库/roster，原首点/截止与更早grant/活动期限不延长；按原实际余量和最短门执行。

同号TASK120/R114原A+工程窗一个完整成果连续修复/验证/清场，完整卡已保存待人工转交，未虚记已收到/开始；无新TASK121，无子Agent。Q冻结，STEP018整体/019/020/M1/项目未通过，原S有限验收不重开。主控未改工程账/产品/结果或执行业务。许可/有限核证/旧共享快照在orchestration-repair03-20261019；CHG1532—1536，下一1537。

## 以下为v2.76及更早历史

'''
arch = f'''# 架构动态文档

文档v1.49，2026-10-19，Asia/Shanghai。需求v1.4、执行动态v2.77、task_model/07；以下v1.48原字节保留。

## Q v2完整工程仍未闭合，定位教学读分类冲突

{now}。TASK120断点02产品未变；原正式bundle实际浏览器加载hash匹配，但三业务模式均FAIL，不签最终UI。A3新head/查询有限事实成立，面试全历史UNKNOWN门未解除，HTML/legacy409仍缺准确内部原因，budget02部分初始化后创建时记忆未完成。C12等旧充分证据沿用，架构需求/模型不降低。

主控从实际源码定位：发送shared policy→教学v2/v3 validator→_teaching_read_snapshot，被Q读方法识别遗漏；原_transaction因此误取exclusive并触发禁止升级，错误被包装。这是确定冲突路径的静态证据，不冒称已捕获原运行唯一内部异常。后续修复只准精确只读分类及直接影响，保留写事务排他policy与K2顺序；暂未落产品修复。新goal不清历史UNKNOWN的事实一并纳入测试合法状态准备，不扩生产金融/权限模型。

剩余真实PG/SUP提交、权限/ACK/K2和最终UI均待根因合并修复后验证；未到集中独审点。Q/STEP018整体/019/020/M1/项目不通过，旧S有限验收保持，主控无产品运行。

## 以下为v1.48及更早历史

'''
for row in inputs:
    assert sha((ROOT / row['path']).read_bytes()) == row['sha256'], row['path']
write(decision_path, decision.encode() + old[decision_path])
write(arch_path, arch.encode() + old[arch_path])
write(state_path, state.encode() + old[state_path])
write(card_path, (HERE / 'contract-03.md').read_bytes() + old[card_path])
entries = [
    (1532, 'DocuN/results/TASK-120-work-decision.md', '置顶集中修复03裁定，保留失败与有限事实，锁分类/UNKNOWN/夹具/409合并处理'),
    (1533, 'DocuS/架构动态文档.MD', 'v1.49登记教学Q读分类静态冲突及真实矩阵未闭合，未将修复计划当已实现'),
    (1534, 'DocuS/执行动态文档.MD', 'v2.77登记断点02已返回/部分通过、实际累计和附条件前向资源许可'),
    (1535, 'DocuN/tasks/TASK-120.md', '置顶完整同号集中修复03，先根因/修复再运行，原窗口单一负责人，旧合同原字节保留'),
    (1536, 'DocuN/evidence/TASK-120/orchestration-repair03-20261019', '只读证据核证/源级因果/精确前向permit/旧共享与返回账快照/保存读回；主控无工程运行'),
]
addition = '\n\n' + '\n\n'.join(f'- CHG-{n:04d}，{now}，Codex编排Agent，{path}。{note}。' for n, path, note in entries) + '\n'
write(changes_path, old[changes_path] + addition.encode())
for path in (state_path, arch_path, card_path, decision_path):
    assert path.read_bytes().endswith(old[path]), path
for row in inputs:
    assert sha((ROOT / row['path']).read_bytes()) == row['sha256'], row['path']
save(HERE / 'save-proof.json', {
    'saved_at': now, 'read_back': True, 'old_document_suffixes_exact': True,
    'engineering_inputs_unchanged': True, 'main_metadata_seconds': round(time.monotonic() - start, 6),
    'files': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p.read_bytes()), 'bytes': p.stat().st_size}
              for p in (decision_path, arch_path, state_path, card_path, changes_path)],
})
print(json.dumps({'saved': True, 'rules': len(rule_checks), 'products_unchanged': len(products),
                  'source_identity_checks': len(checks), 'new_permit': permit['id'],
                  'engineering_ledger_unchanged': True, 'next_CHG': 1537}, ensure_ascii=False))
