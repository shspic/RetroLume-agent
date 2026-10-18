"""Orchestration documents and read-only evidence identities; no product imports or execution."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re
import time

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
OUT = Path(__file__).resolve().parent
EXEC = ROOT / 'DocuN/evidence/TASK-117/execution'
C01 = EXEC / 'continuation-01'
CARD = ROOT / 'DocuN/tasks/TASK-117.md'
WORK = ROOT / 'DocuN/results/TASK-117-work-decision.md'
STATE = ROOT / 'DocuS/执行动态文档.MD'
CHANGE = ROOT / 'DocuS/文档变更记录.MD'
at = datetime.now(timezone(timedelta(hours=8))).isoformat()


def ident(p):
    raw = p.read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def save(name, obj):
    path = OUT / name
    assert not path.exists(), str(path)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


before = {p: p.read_bytes() for p in (CARD, WORK, STATE, CHANGE)}
assert STATE.read_text(encoding='utf-8-sig').splitlines()[2].startswith('文档v2.61，')
old_numbers = [int(x) for x in re.findall(r'^- CHG-(\d+)', CHANGE.read_text(encoding='utf-8-sig'), re.M)]
assert old_numbers[-1] == 1427
rules = read(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
for row in rules:
    assert ident(Path(row['absolute_path']))['sha256'] == row['sha256']
as_run_path = C01 / 'root09-as-run-1792038022321090500.json'
as_run = read(as_run_path)
for rel, expected in as_run['files'].items():
    assert ident(ROOT / rel)['sha256'] == expected, rel
assert len(as_run['files']) == 84
protected_paths = list(dict.fromkeys(
    [ROOT / rel for rel in as_run['files']]
    + [EXEC / 'budget.json', EXEC / 'events.jsonl',
       ROOT / 'DocuN/results/TASK-117-result.md',
       C01 / 'browser-3/proof.json', C01 / 'root09-error-1792038493721512900.txt',
       C01 / 'root09-cleanup-1792038022321090500.json',
       C01 / 'root09-stop-1792038022321090500.json', as_run_path]
))
assert not any(p in before for p in protected_paths)
protected = {str(p.relative_to(ROOT)): ident(p) for p in protected_paths}
budget = read(EXEC / 'budget.json')
assert budget['counts']['roots'] == 9 and budget['active_root'] == 9
segment = next(s for s in budget['segments'] if s['permit'] == budget['active_segment'])
root9 = next(r for r in budget['roots'] if r['id'] == 9)
assert root9['end'] is None
browser = read(C01 / 'browser-3/proof.json')
cleanup = read(C01 / 'root09-cleanup-1792038022321090500.json')
assert browser['status'] == 'failed' and cleanup['all_confirmed'] is False
assert budget['counts']['api_starts'] == 8
now_mono = time.monotonic_ns()
observation = {
    'schema': 'TASK117.orchestration-recovery-inspection.v1', 'observed_at': at,
    'TASK': 'TASK-117', 'R': 'R-111', 'STEP': '018',
    'user_clarification': 'GPT账号Sol模型配额耗尽，不是本卡预算或审批服务额度',
    'client_quota_not_a_new_business_failure': True,
    'budget_identity': ident(EXEC / 'budget.json'), 'events_identity': ident(EXEC / 'events.jsonl'),
    'active_segment': budget['active_segment'], 'counts': budget['counts'],
    'segment_start_utc': segment['start_utc'], 'segment_start_mono_ns': segment['start_mono_ns'],
    'observation_mono_ns': now_mono,
    'same_current_QPC_domain_elapsed_observed': (now_mono - segment['start_mono_ns']) / 1e9,
    'not_a_final_time_or_holding_settlement': True,
    'segment_intervals_sum': {name: sum(x['seconds'] for x in budget.get(name, [])
                                      if x.get('segment') == segment['permit'])
                              for name in ('runtime_intervals', 'offline_intervals')},
    'root9': root9, 'root9_current_business_deadline_already_past': now_mono >= root9['business_deadline_mono_ns'],
    'browser_observed': {
        'status': browser['status'], 'browser_closed': browser.get('browser_closed'),
        'teaching_activity_id': browser.get('teaching_activity_id'),
        'new_committed_receipts': sum(x.get('value', {}).get('status') == 'committed' for x in browser['receipts']),
        'last_command': {k: browser['receipts'][-1].get('value', {}).get(k)
                         for k in ('activity_id', 'action', 'business_key', 'applied_revision', 'status')},
        'failure': browser.get('failure'), 'assets': browser['assets']},
    'root9_as_run_binding': {'path': str(as_run_path), **ident(as_run_path),
                            'files': len(as_run['files']), 'all_match': True,
                            'node_script_sha256': as_run['node_script_sha256']},
    'resource_observation_limits': {
        'historical_root09_stop_all_stopped': False,
        'historical_API8_owned_handle_exit': 0,
        'historical_source_PG_running': False, 'historical_source_PG_pid': 0,
        'live_CIM': 'restricted client could not access CIM resource',
        'live_GetProcess_selected_PIDs': 'no rows; not used to infer complete browser tree closure',
        'live_Docker_read_only_inspect': 'permission denied to dockerDesktopLinuxEngine pipe; no state confirmed',
        'main_no_starts_or_stops': True},
    'forward_scheduling_authorization': {'S_total_roots_cap': 13, 'TASK_total_with_Q_reserved': 14,
                                       'new_S_roots_from_receipt_max': 4, 'API_total_cap': 14,
                                       'old_counts_failures_and_caps_preserved_in_history': True,
                                       'new_time_money_and_other_resource_caps': 0},
    'rules_7_match_locked': True, 'protected_identities': protected,
    'private_or_browser_storage_contents_read': False,
    'main_product_test_build_SQL_provider_actions': 0,
    'new_runtime_resources': 0, 'Q_active': False,
}
save('inspection.json', observation)
backup = OUT / 'before-documents'
backup.mkdir(exist_ok=False)
for p, raw in before.items():
    (backup / p.name).write_bytes(raw)

notice = (OUT / 'continuation.md').read_bytes()
CARD.write_bytes(notice + b'\r\n\r\n' + before[CARD])
work_prefix = f'''# TASK117/R111 S02 — Sol账号配额中断后恢复补充

{at}。用户明确中断为其GPT账号Sol模型用量耗尽，不是任务预算用完或审批服务拒绝；可用A+资源接续，优先原窗可用资源，否则一个接续窗独占，原窗保持停止。本次是恢复补充待人工转交，未声称已接收或已重新执行。

主控核root09原始错误、cleanup/stop、Browser3回执/DOM、当前fixture及84项as-run身份，84/84无漂移。教学活动b7f32142-b5b3-4a5c-b561-f927bcbe1b6d的14笔新增committed保留，最后answer/revision16；不等于最后评价或独立复测完成。记忆教学bbe0617f-0417-4490-8a8f-354ab0e10ae3为另一活动。Browser3实际在面试记忆checkbox未改状态失败，response.json关闭后未捕获异常，browser_closed缺失；API原句柄退出0、source原时点PG停/Pid0，但all_stopped=false，active_root9/end空。原业务/清场截止已过，不得恢复root9业务或倒填历史PASS。

新卡先当前精确停止核查/必要自有清理及晚核证，前向关闭root9保守计时，再按GET原key/head/四账从未提交处完成S余项；禁止整体重跑root09。主控当前只读Docker inspect遭管道拒绝，CIM不可访问，不能签当前整树已停；工程恢复时自行按真实权限核证。本轮未申请或遭自动审批审查拒绝，不把管道访问失败冒为审批结论。

当前观测root9/PGstart12/API8/Browser3/build4/Native51/HTTP278，PG对象卷各3、preview/provider/fee0；S02已结束runtime小计430.752/offline812.968，root9及持有另算。原首点02:24:00.722344Z、S02活动28800/持有10800/offline3600和48h及旧S01超额不改。因同库重开和两种恢复应用查看至少还需API启动，本次明确前向调度覆盖为收到后最多4新S根/S总13/TASK14保Q1、API累计14；其余时间/启动/物理/费用限额不加、不重置、不要求耗满。旧根11/API10门保留历史，新段由执行者读入后前向追加覆盖和guard，不由主控写执行账。

低内存512/768/1024MiB分阶段及两次低于256MiB自动精确清场继续，容器隔离与验签不降。Q未启用/真实费用0，PDF旧两次失败独立保留，不授权盲目第三次重试。普通修复/补证仍同卡连续完成，稳定S后才集中独审；STEP018/019/020/M1/项目均未通过。

完整合同与核证证据在DocuN/evidence/TASK-117/orchestration-quota-recovery-20261015；结果仍由工程追加TASK-117-result.md，主控未改历史报告/产品/主账/旧证据/私密。

## 以下为原低内存、S02/S01裁定历史

'''
WORK.write_bytes(work_prefix.encode('utf-8') + before[WORK])
state_prefix = f'''# 执行动态文档

文档v2.62，2026-10-15，Asia/Shanghai。唯一总状态账；需求v1.3、架构v1.35、task_model/07。以下v2.61历史原字节保留；未改变产品采用包或通过结论。

## TASK117 S02账号Sol配额中断，已核root09并签发同号恢复补充

{at}。用户明确是GPT账号Sol配额耗尽；不记为任务额度清零或审批服务拒绝。仍A+同TASK117/R111，优先原工程窗可用资源，否则一个接续窗独占/原窗保持停止；恢复补充已保存待人工转交，不登记已经重新接收或运行。

主控84/84 as-run字节核对一致；Browser3教学14笔新增committed有效保留，末笔answer/revision16，最后评价/独立次数与I01未完成。Browser3实际在面试记忆checkbox失败，随后异步response.json关闭异常、browser_closed缺失，cleanup/stop未通过。root09仍active/end空且原截止已过；先精确当前停止核证和晚核证前向结账，保留原FAIL/超时，再新根GET持久事实接续，禁止整批重跑或倒填成功。

当前计数观测root9/PGstart12/API8/Browser3/build4/Native51/HTTP278，PG对象卷各3、preview/provider/fee0；两类已结束区间小计runtime430.752/offline812.968不是全部投入。主控只读Docker管道访问失败/CIM受限，未确认当前完整整树停止，也未启动停止任何资源。工程结果文件仍旧S01，不能由文件存在冒S02完成。

当前前向调度补充：收到后最多4新S目标根、S累计13/TASK14且Q保留1、API累计14。原根/计数/失败和旧cap历史保留；原S02首点02:24:00.722344Z、活动28800/持有10800/offline3600/48h及其它资源/费用上限不加。低内存分阶段512/768/1024MiB与压力256MiB两次自动清场、原隔离/验签全部保持；S02硬门先到仍停，不把新窗口变新时间。Q仍未激活，不能把S补证冒真实付费语义通过。

本次合同/核证/旧共享备份/保存证明位于DocuN/evidence/TASK-117/orchestration-quota-recovery-20261015。继续剩余同库重开、两域/记忆、P02/P03只读查看、L10等实际缺口，不重复已足证据；PDF原失败单列，稳定S后集中独审。产品/执行账/旧证据/原报告由原分工保护，主控没有接管产品执行。CHG1428—1433，下一1434。

## 以下为v2.61及更早历史

'''
STATE.write_bytes(state_prefix.encode('utf-8') + before[STATE])
entries = [
    ('DocuN/evidence/TASK-117/orchestration-quota-recovery-20261015/continuation.md', '核实Sol账号配额与root09真实故障分开；完整断点接续与明确前向调度许可。'),
    ('DocuN/tasks/TASK-117.md', '恢复补充置顶，旧完整卡原字节保留，同TASK/R/A+且单写者。'),
    ('DocuN/results/TASK-117-work-decision.md', '84项字节/14回执与停止缺口核证，未签S02完成，未重置原账。'),
    ('DocuS/执行动态文档.MD', 'v2.62唯一状态登记当前root9及恢复待转交，旧S01/S02历史保留。'),
    ('DocuN/evidence/TASK-117/orchestration-quota-recovery-20261015/before-documents', '共享四文件原字节备份；inspection保存原执行身份与读取限制。'),
    ('DocuN/evidence/TASK-117/orchestration-quota-recovery-20261015/save-proof.json', '保存复读和原后缀保护，规则/84绑定对象/主账/旧报告未被主控改写。'),
]
tail = ''.join(f'\r\n- CHG-{1428+i}，{at}，Codex编排Agent，{name}。{detail}\r\n'
               for i, (name, detail) in enumerate(entries))
CHANGE.write_bytes(before[CHANGE] + tail.encode('utf-8'))
for p in (CARD, WORK, STATE):
    assert p.read_bytes().endswith(before[p]), str(p)
assert CHANGE.read_bytes().startswith(before[CHANGE])
assert [int(x) for x in re.findall(r'^- CHG-(\d+)', CHANGE.read_text(encoding='utf-8-sig'), re.M)] == old_numbers + list(range(1428, 1434))
for rel, expected in protected.items():
    assert ident(ROOT / rel) == expected, rel
for row in rules:
    assert ident(Path(row['absolute_path']))['sha256'] == row['sha256']
for p in (CARD, WORK, STATE, CHANGE):
    assert '\ufffd' not in p.read_text(encoding='utf-8-sig')
save('save-proof.json', {
    'saved_at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
    'files': [{'path': str(p), **ident(p)} for p in (CARD, WORK, STATE, CHANGE, OUT / 'continuation.md', OUT / 'inspection.json')],
    'old_documents_raw_preserved': True, 'protected_identities_unchanged': len(protected),
    'as_run_84_unchanged': True, 'rules_7_unchanged': True,
    'execution_budget_events_products_or_old_results_written_by_main': False,
    'product_build_test_SQL_provider_actions': 0, 'runtime_resources_started_or_stopped': 0,
    'dispatch_confirmed': False, 'Q_active': False, 'CHG': list(range(1428, 1434)),
})
print(json.dumps({'status': 'SAVED_AND_READ_BACK', 'card': str(CARD), 'state': 'v2.62',
                  'last_CHG': 1433, 'product_execution': 0, 'old_documents_preserved': True}, ensure_ascii=False))
