"""记录低内存分时调度，采OS只读内存；不导入/运行产品或修改执行层。"""
from pathlib import Path
from datetime import datetime, timedelta, timezone
import ctypes
import hashlib
import json
import re

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent').resolve()
OUT = Path(__file__).resolve().parent
CARD = ROOT / 'DocuN/tasks/TASK-117.md'
WORK = ROOT / 'DocuN/results/TASK-117-work-decision.md'
STATE = ROOT / 'DocuS/执行动态文档.MD'
CHANGES = ROOT / 'DocuS/文档变更记录.MD'
EX = ROOT / 'DocuN/evidence/TASK-117/execution'

def load(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def ident(p):
    raw = p.read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

def save(name, value):
    p = OUT / name
    assert p.resolve().is_relative_to(ROOT) and not p.exists()
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    assert load(p) == value

def prefix(p, text, original):
    assert p.resolve().is_relative_to(ROOT)
    assert '*' not in text and not re.search(r'^\|', text, re.MULTILINE)
    p.write_bytes(text.replace('\n', '\r\n').encode('utf-8') + original)
    assert p.read_bytes().endswith(original)

assert OUT.is_relative_to(ROOT) and not (OUT / 'memory-profile.json').exists()
for p in (CARD, WORK, STATE, CHANGES):
    assert p.resolve().is_relative_to(ROOT)
before = {p: p.read_bytes() for p in (CARD, WORK, STATE, CHANGES)}
assert '文档v2.60' in before[STATE].decode('utf-8-sig').splitlines()[2]
numbers = [int(x) for x in re.findall(r'^- CHG-(\d+)', before[CHANGES].decode('utf-8-sig'), re.MULTILINE)]
assert numbers[-1] == 1420
notice = (OUT / 'notice.md').read_bytes()
assert '*' not in notice.decode('utf-8')
rules = load(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
for row in rules:
    assert ident(Path(row['absolute_path']))['sha256'] == row['sha256']
budget = load(EX / 'budget.json')
receipt = load(EX / 'continuation-01/receipt.json')
assert budget['active_segment'] == receipt['permit'] == 'TASK-117-STEP018-INTEGRATION-S02-20261015'
protected = {name: ident(ROOT / name) for name in (
    'AGENTS.md', 'DocuS/原始需求文档.MD', 'DocuS/最终需求文档.MD', 'DocuS/架构动态文档.MD',
    'backend/app/preview/docker_control.py', 'backend/app/preview/host_policy.py',
    'DocuN/results/TASK-112-result.md', 'DocuN/results/TASK-115-result.md')}
at = datetime.now(timezone(timedelta(hours=8))).isoformat()

class MemoryStatus(ctypes.Structure):
    _fields_ = [('length', ctypes.c_ulong), ('load', ctypes.c_ulong),
                ('total_phys', ctypes.c_ulonglong), ('avail_phys', ctypes.c_ulonglong),
                ('total_page', ctypes.c_ulonglong), ('avail_page', ctypes.c_ulonglong),
                ('total_virt', ctypes.c_ulonglong), ('avail_virt', ctypes.c_ulonglong),
                ('extended', ctypes.c_ulonglong)]

memory = MemoryStatus()
memory.length = ctypes.sizeof(memory)
ok = bool(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory)))
memory_observation = {'sample_at': at, 'api': 'GlobalMemoryStatusEx', 'success': ok,
                      'Docker_warm_basis': '用户/原执行窗报告，主控不启动或查询Docker',
                      'is_executor_startup_gate_sample': False}
if ok:
    memory_observation.update(total_physical_bytes=memory.total_phys,
                              available_physical_bytes=memory.avail_phys,
                              available_physical_GiB=memory.avail_phys / 1024**3,
                              api_avail_pagefile_field_bytes=memory.avail_page)
save('memory-observation.json', memory_observation)

backup = OUT / 'before-documents'
backup.mkdir(exist_ok=False)
for p, raw in before.items():
    (backup / p.name).write_bytes(raw)
profile = {
    'schema': 'TASK117.low-memory-profile.v1', 'issued_at': at,
    'TASK': 'TASK-117', 'R': 'R-111', 'permit': receipt['permit'],
    'profile': 'TASK117-S02-LOW-MEMORY-20261015',
    'user_basis': '所有自有PG/API已停、暖机可用约1.66GiB；用户明确没更多内存并要求现有条件继续',
    'supersedes': '原统一2GiB测试夹具预检与本次根分时调度项，其余S02许可不变',
    'minimum_available_physical_MiB_before_start': {
        'base_preflight': 512, 'first_PG': 512, 'API': 512,
        'host_UI_browser': 768, 'second_PG': 768, 'fixed_preview': 1024},
    'second_PG_precondition': '实际恢复/校验依赖两库，且API/host browser/preview均停',
    'default_simultaneous_PG': 1, 'maximum_short_restore_PG': 2,
    'pressure_monitor': {'sample_period_seconds': 2, 'available_physical_low_MiB': 256,
                         'consecutive_low_samples_to_cleanup': 2,
                         'action': '拒新动作并沿原有界闭包精确结束自有消费者/API/PG，不动他人'},
    'container_isolation_limits_unchanged': {'PG_memory_MiB': 512, 'preview_memory_MiB': 1024,
        'preview_memory_swap_MiB': 1024, 'PG_pids': 128, 'preview_pids': 256,
        'network_sandbox_readonly_Job_StopProof': 'unchanged'},
    'remaining_roots_from_actual_adoption_max': 3, 'S_total_roots_max': 11,
    'TASK_total_including_one_reserved_Q_root_max': 12,
    'time_money_starts_builds_objects_windows_caps': '原S02全部保持，无重置或延时；只增加用于内存分时的根调度门',
    'counts_observed_not_final': budget['counts'],
    'S02_start_unchanged': receipt['start'],
    'clock_domain_note': receipt['clock_discontinuity'],
    'gate_values_are_trial_scheduling_not_capacity_guarantee': True,
    'main_product_execution_Docker_or_private_read': 0,
    'old_execution_budget_or_fixture_written_by_main': False,
    'notice_sha256': ident(OUT / 'notice.md')['sha256']
}
save('memory-profile.json', profile)

CARD.write_bytes(notice + b'\r\n' + before[CARD])
assert CARD.read_bytes().endswith(before[CARD])
work_text = f'''# TASK117/R111 S02 — 按用户现有内存采用分时测试profile

{at}。用户报告自有PG/API已停、Docker暖机后可用约1.66GiB，并明确没有更多内存。主控读当前fixture，确认2GiB是测试统一硬编码，没有产品最低容量测定；允许低内存分阶段继续，避免重复要求用户释放内存。不是免测或保证全部场景一定能跑。

主控允许执行者修本任务memory_gate及必要调用方：基础/单PG/API启动512MiB、host Browser/必要第二PG768MiB、固定preview1024MiB，启动前各实采；默认PG1，恢复确需PG2时API/Browser/preview先停。build/离线与所有运行资源分开，L10实际宿主与一般UI分段但必需T/U门不减。原有界控制器约2秒采样，连续两次低于256MiB则拒新动作并按原精确清场；未知采样/原停止不明不冒通过。PG512MiB/preview1GiB及swap/pids/网络/只读/验签/Job/StopProof全部不降，不改用户系统/WSL/应用。

原S02已经实际接收，回执首点2026-10-15T02:24:00.722344Z、原QPC域切换/首采回推和保守5秒照留。当前账观测root8/PGstart11/API7/Browser2/build4/Native31/HTTP164，active_root为空；是中途记录，不核销或签最终合规。为减少并发使余缺可分时，从收到本补充起最多3新S目标根/S累计11/TASK总12且Q保留1，原根/失败不减计。活动/持有/离线/日历/启动/build/物理对象/窗口/费用原剩额不加、原首点不移，门到则仍停。

完整卡置顶本补充并保留原卡全文，原窗口读后记录新profile/hash再前向修fixture/单账；主控不改execution代码/budget/events、不生成新运行资源。独立的PDF422失败不是内存门解除即通过，仍按原根因处理；实际固定preview如放不下仅其依赖受限，其余S收口继续。Q真实provider/费用0、既有80次20元条件性授权不重问或激活，新数据/安全验收不降低。

准确补充、试行阈值/OS只读观测/原共享备份和保存证明在DocuN/evidence/TASK-117/orchestration-low-memory-20261015。主控本轮仅读代码/元数据/OS内存和维护共享文档，产品/测试/Docker/API/Browser/网络/费用/Git写0。

## 以下为原S02/S01裁定历史

'''
prefix(WORK, work_text, before[WORK])
state_text = f'''# 执行动态文档

文档v2.61，2026-10-15，Asia/Shanghai。唯一总状态账；需求v1.3、架构v1.35、task_model/07。以下v2.60历史原字节保留；产品架构/验收不变。

## TASK117 S02实施中，采用低内存分时测试调度

{at}。实际execution/continuation-01/receipt证明S02已接收/实施，首点2026-10-15T02:24:00.722344Z、mono4278922854000，首工具漏同步点/回推保守5秒与S02新host QPC域披露保留，不与旧S01跨域直接相减。当前唯一账观测root8、PGcreate/object/volume3/start11、API7/Browser2/build4/Native预记31/HTTP164/preview0/provider0/fee0，active_root为空；尚未统一交回，不签S02成果验收。

用户反馈所有自有PG/API已停、Docker暖机仍约1.66GiB且无更多内存。原2GiB是夹具统一预检值，主控改为LOW-MEMORY profile：默认一PG分时，恢复确需两PG时先停API/host Browser/preview；基础/单PG/API门512MiB，Browser/第二PG768MiB，固定preview1024MiB，逐启动实采。约2秒监测、连续两次低于256MiB触发原自有资源清场，采样不明拒启动。真实运行/验收仍必要，试行值不冒容量保证，不再让用户为统一2GiB反复腾内存。

固定PG512MiB/preview1024MiB等swap/pids/隔离/验签/Job/EOF/StopProof与用户进程/系统全局配置都保持。build/离线停运行资源后做，UI与实际L10宿主按依赖分段，不用静态图或mock换掉必需实证。某段实测不足仅阻塞对应承诺，其它工作继续；既有PDF422是独立未闭问题，不能因放行memory门写已修。

为支持余缺内存分时，从本补充实际接收起最多3新S目标根、S累计11/TASK12且Q另保1；原root/失败不清。S02活动28800/48h/持有10800/offline3600及累计门、PGstart20/API10/Browser8/build5/Native160/preview12/HTTP3000/对象卷等均不扩、不重置首点或退等待时间。低内存补充置顶原TASK117完整卡，仍原A+工程窗、同TASK/R，无新S03/118或子Agent。

主控只读当前fixture/回执/账与OS物理内存，未重启/实查Docker或API，用户所报停止不冒主控当前现场核查。证据和补充在DocuN/evidence/TASK-117/orchestration-low-memory-20261015；原execution单账/源/结果/私密不由主控修改。Q/20元80次/独审后启用门、旧S01超额/全部失败/全项目历史与原Must保留，STEP018/019/020/M1/项目未通过。CHG1421—1427，下一1428。

## 以下为v2.60及更早历史

'''
prefix(STATE, state_text, before[STATE])
entries = [
    ('memory-profile.json', '依用户资源限制采用低内存分阶段试行门，容器隔离不变，原时间费用不加。'),
    ('notice.md', '同原工程窗读后继续分时安排、启动门/压力退出/局部受限与根调度，不再等统一2GiB。'),
    ('DocuN/tasks/TASK-117.md', '当前低内存补充置顶，原S02/S01全文保留，未清历史失败。'),
    ('DocuN/results/TASK-117-work-decision.md', '原S02在途事实/用户低内存选择与调整范围，未验收工程或解除Q。'),
    ('DocuS/执行动态文档.MD', 'v2.61真实S02实施中、当前计数观测和分时调度，无主控产品运行。'),
    ('before-documents', '原卡/Work/状态/变更原字节备份，原执行账和产品不写。'),
    ('save-proof.json', '保存复读/原后缀保护/规则身份及0秘密读取/0产品运行。')
]
tail = ''.join(f'\r\n- CHG-{1421+i}，{at}，Codex编排Agent，'
               f'{name if "/" in name else "DocuN/evidence/TASK-117/orchestration-low-memory-20261015/"+name}。{detail}\r\n'
               for i, (name, detail) in enumerate(entries))
CHANGES.write_bytes(before[CHANGES] + tail.encode('utf-8'))
assert CHANGES.read_bytes().startswith(before[CHANGES])
assert [int(x) for x in re.findall(r'^- CHG-(\d+)', CHANGES.read_text(encoding='utf-8-sig'), re.MULTILINE)] == numbers + list(range(1421, 1428))
for name, expected in protected.items():
    assert ident(ROOT / name) == expected, name
for row in rules:
    assert ident(Path(row['absolute_path']))['sha256'] == row['sha256']
save('save-proof.json', {
    'saved_at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
    'files': [{'path': str(p), **ident(p)} for p in (CARD, WORK, STATE, CHANGES, OUT / 'notice.md', OUT / 'memory-profile.json')],
    'old_card_and_histories_preserved': True, 'protected_unchanged': len(protected),
    'execution_code_budget_events_or_private_written': False,
    'read_physical_memory_only_not_startup_validation': True,
    'new_runtime_resources_or_product_runs': 0, 'Q_active': False,
    'CHG': list(range(1421, 1428))
})
print(json.dumps({'status': 'SAVED_AND_READABLE', 'notice': str(OUT / 'notice.md'),
                  'card': str(CARD), 'execution': 'v2.61', 'last_CHG': 1427,
                  'available_physical_GiB_observed': memory_observation.get('available_physical_GiB'),
                  'runtime_or_product_execution': 0}, ensure_ascii=False))
