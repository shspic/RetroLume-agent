"""回收原115增量结论、关闭两项根因、保存原114双修完整卡；不执行产品。"""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import hashlib
import json
import re

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
OUT = Path(__file__).resolve().parent
CARD = ROOT / 'DocuN/tasks/TASK-114.md'
WORK114 = ROOT / 'DocuN/results/TASK-114-work-decision.md'
WORK115 = ROOT / 'DocuN/results/TASK-115-work-decision.md'
ARCH = ROOT / 'DocuS/架构动态文档.MD'
STATE = ROOT / 'DocuS/执行动态文档.MD'
CHANGES = ROOT / 'DocuS/文档变更记录.MD'
AUDIT = ROOT / 'DocuN/evidence/TASK-115/review-01'
RECEIVED = ROOT / 'DocuN/evidence/TASK-115/orchestration-review01-receipt-20261014/received.json'
CONTROL = ROOT / 'DocuN/evidence/TASK-114/implementation/control'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def identity(path):
    raw = path.read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def record(path):
    return {'path': str(path), **identity(path)}


def save(name, data):
    path = OUT / name
    assert not path.exists(), str(path)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    assert load(path) == data


def prefix(path, text, old):
    path.write_bytes(text.replace('\n', '\r\n').encode('utf-8') + old)
    assert path.read_bytes().endswith(old), str(path)


now = datetime.now(timezone(timedelta(hours=8)))
at = now.isoformat()
day = '2026-10-14'
assert now < datetime(2026, 10, 15, 8, 54, tzinfo=timezone.utc), '旧日历截止已到，不发布已过期运行许可'
received = load(RECEIVED)
old = {path: path.read_bytes() for path in (CARD, WORK114, WORK115, ARCH, STATE, CHANGES)}
assert '文档v1.29' in old[ARCH].decode('utf-8-sig').splitlines()[2]
assert '文档v2.53' in old[STATE].decode('utf-8-sig').splitlines()[2]
assert identity(CARD) == {key: received['engineering_card_before'][key] for key in ('bytes', 'sha256')}
numbers = [int(value) for value in re.findall(r'^- CHG-(\d+)', old[CHANGES].decode('utf-8-sig'), re.MULTILINE)]
assert numbers[-1] == 1354 and 1355 not in numbers

backup = OUT / 'before-documents'
backup.mkdir(exist_ok=False)
for path, raw in old.items():
    (backup / path.name).write_bytes(raw)

protected = {}
for path in (ROOT / 'DocuN/results/TASK-114-result.md', ROOT / 'DocuN/results/TASK-115-result.md',
             ROOT / 'DocuN/tasks/TASK-115.md', CONTROL / 'receipt.json', CONTROL / 'events.jsonl'):
    protected[str(path)] = identity(path)
for row in received['current']:
    path = ROOT / row['path']
    if row['exists']:
        expected = {key: row[key] for key in ('bytes', 'sha256')}
        assert identity(path) == expected
        protected[str(path)] = expected
    else:
        assert not path.exists()
for row in received['review_evidence']:
    path = Path(row['path'])
    assert identity(path) == {key: row[key] for key in ('bytes', 'sha256')}
    protected[str(path)] = identity(path)
for row in received['rules']:
    path = Path(row['absolute_path'])
    assert identity(path)['sha256'] == row['sha256']
    protected[str(path)] = identity(path)
for row in load(ROOT / 'DocuN/evidence/TASK-115/audit/delivery.json')['evidence']:
    path = Path(row['path'])
    assert identity(path) == {key: row[key] for key in ('bytes', 'sha256')}
    protected[str(path)] = identity(path)

control = load(CONTROL / 'receipt.json')
assert all(row['state'] == 'stopped' for row in control['resources'])
assert control['counts'] == received['engineering_counts']
new_cumulative = dict(control['limits'])
assert new_cumulative['frontend_build'] == 6
new_cumulative['frontend_build'] = 7
permit = {
    'TASK': 'TASK-114', 'R': 'R-108', 'continuation': '03',
    'permit': 'TASK-114-STEP017-C03-20261014', 'issued_at': at,
    'authorization': '用户已采用STEP017-P1并要求完成；原115只读复核指向两处原P1余缺，原工程合并修复和定向验证',
    'dispatch_confirmed': False, 'execution_started': False,
    'closed_defects': ['DEF-034/F01', 'DEF-037/F04'],
    'open_defects': ['DEF-035/F02', 'DEF-036/F03'],
    'scope': 'loading pin同Operation及policy/plan/scope输入生命周期；受控连接检查+最终dist真实Chromium/routes，无新PG',
    'previous_counts': control['counts'],
    'original_cumulative_limits': control['limits'],
    'new_cumulative_task114_limits': new_cumulative,
    'new_counter_allowance': {'real_roots': 2, 'browser_start': 2, 'frontend_build': 2,
                              'pg_create': 0, 'pg_success': 0, 'pg_start': 0, 'api_start': 0,
                              'vite_start': 0, 'windows_start': 0, 'preview_create': 0,
                              'preview_start': 0, 'SQL': 0, 'provider_calls': 0, 'fees': 0,
                              'public_network': 0},
    'max_post_counts_this_round': {'real_roots': 23, 'browser_start': 7, 'frontend_build': 7,
                                  'pg_create': 9, 'pg_success': 9, 'pg_start': 37,
                                  'api_start': 8, 'windows_start': 11},
    'explicit_increment': {'frontend_build_cumulative_limit': {'from': 6, 'to': 7, 'delta': 1,
                                                              'reason': '两处精确修复的最终构建及一次有据修正复检余地，不重置旧5次'}},
    'new_active_seconds_max': 10800, 'active_cleanup_reserve_seconds': 1200,
    'previous_C02_active_seconds': 9188.720111,
    'original_C02_active_limit_seconds': 21600,
    'C02_plus_C03_max_seconds': 19988.720111,
    'calendar_hard_deadline_utc': '2026-10-15T08:54:00Z',
    'calendar_additional_limit': '接收后24小时与原硬截止取较早者，原锚点不改',
    'first_tool_anchor': '实际接收者实采UTC/mono；无精确点时保守说明，签发时刻不冒接收',
    'offline_seconds_this_round_max': 1800, 'offline_original_used': 172.317,
    'offline_cumulative_limit_unchanged': 7200,
    'holding_seconds_this_round_max': 600, 'holding_cleanup_reserve_seconds': 120,
    'holding_previous_used': 462.047, 'holding_post_max': 1062.047,
    'holding_cumulative_limit_unchanged': 10800,
    'business_holding_cumulative_limit_unchanged': 9600,
    'browser': {'mode': '既有Chromium+全部routes+本项目最终dist，零监听/API/Vite/PG',
                'profile_root': str(ROOT / 'DocuN/evidence/TASK-114/implementation/continuation-03/synthetic/browser-root'),
                'URL_only_not_a_listener': 'http://127.0.0.1:18114/',
                'memory_available_GiB_before_start': 2,
                'PID_birth_exact_close': True},
    'evidence_root': str(ROOT / 'DocuN/evidence/TASK-114/implementation/continuation-03'),
    'unique_control': str(CONTROL),
    'old_resources_reauthorized': False,
    'previous_115_active_seconds': 8617.261566,
    'engineering_result': str(ROOT / 'DocuN/results/TASK-114-result.md'),
    'independent_review_after_stable': '原TASK115只对两问题及实际影响，另由主控给许可，本卡不执行',
}
save('continuation-permit.json', permit)
save('input-manifest.json', {
    'created_at': at, 'current': received['current'], 'rules': received['rules'],
    'root_entry': record(ROOT / 'AGENTS.md'),
    'adopted_contract': record(ROOT / 'DocuN/evidence/TASK-113/design/revision-01/current-contract.md'),
    'original_engineering_card': record(backup / CARD.name),
    'audit_report': record(ROOT / 'DocuN/results/TASK-115-result.md'),
    'audit_review_evidence': received['review_evidence'],
    'engineering_report_before': record(ROOT / 'DocuN/results/TASK-114-result.md'),
    'engineering_control_before': record(CONTROL / 'receipt.json'),
    'engineering_events_before': record(CONTROL / 'events.jsonl'),
    'C02_final_manifest': record(ROOT / 'DocuN/evidence/TASK-114/implementation/continuation-02/final/manifest.json'),
    'decision_basis': record(RECEIVED),
    'known_missing_old_outputs': [row['path'] for row in received['current'] if not row['exists']],
    'all_history_protected': '原工程/独审证据、报告后缀、失败与已结束控制段不得改写；新轮只追加唯一执行账',
})
save('window-assignment.json', {
    'created_at': at, 'TASK': 'TASK-114', 'R': 'R-108', 'continuation': '03',
    'grade': 'A+', 'window': '原TASK114工程窗口（上一续作02）',
    'previous_actual_identity': 'Codex desktop / GPT-6，实际接收时如实登记',
    'manual_transfer': True, 'dispatch_confirmed': False,
    'reason': '原工程熟悉正确取消/时限基础，本次只两处实际漏链，避免换窗重做',
    'audit_window': '原TASK115保持独立，不参与本卡实现',
    'no_subagents_or_parallel_product_writers': True,
})

work115 = f'''# TASK115 review-01已回收：两项关闭，两项原P1待修

{at}，用户侧日期{day}，Codex编排Agent。报告61253字节/3d6a4ce4e30284f6799f61462e84c419a9fdd7226ef1f1e73dc468815b04a0f2，原37767字节后缀未改；235当前文件、1117保护登记与23本轮审计原件/旧358原件/七规则核证。原独审窗口连续性和既有暴露披露接受，独立交付验收通过；代码部分、证据部分、执行控制本轮只读范围合规，不签STEP017。

主控关闭DEF-034/F01原取消覆盖成功根因和DEF-037/F04原依赖正文投影根因，保留实际样本/角色/Hub/文件层及不变传播边界。DEF-035/F02仍P1：LoadingReferencePin独立connect固定3秒及身份查询未接原Operation；DEF-036/F03仍P1：上传/策略/旧plan和范围核对输入生命周期失效。不能用此前GET plan反序替代上传中改policy。

真实PG deadline原件只到reading后failed，未抵达2.1秒发布注入，纠正层级后继承真实读取超时和独立文件后段方法，不作废正常PG也不追认后段PG。原F01/F04不机械重审，原普通连接/loader角色和31域/SUP/G11保持有效。

review-01只读活动3126.578112，原5490.683454加累计8617.261566/21600；原首工具mono未同时采样、保守早起点保留。新增产品/业务/PG/SQL/Docker/Browser/API/compile/test/build/Native/provider/费用/公网/Git全0，原root3/API3/Browser2/offline125.610/hold14.874不清。旧日历与未用余额不自动续。

后续原114合并双修和最终bundle定向route补证，原115暂不接新执行。工程稳定后主控只给同原独审窗口两项及传播复核许可，不派TASK116，不让审计自修或重复原充分方法。原结果/本轮原件都不改。

## 以下为旧独审许可与历史原字节

'''
prefix(WORK115, work115, old[WORK115])

work114 = f'''# TASK114续作03 — 两项P1定向修复与验证前向许可

{at}，用户侧日期{day}，Codex编排Agent。原115 review-01实际已回，F01/F04由主控据独审和实际原件关闭；F02 loading pin未贯通D、F03 policy/plan/scope输入生命周期仍P1，STEP017不关闭。本轮原TASK114/R108 A+工程窗完整双修+定向验证卡，不重复四项审查或正常PG/SUP主链。

许可TASK-114-STEP017-C03-20261014。当前235文件冻结，旧报告69598字节/e457d131…5ad11保原字节后缀，既有控制和失败历史保留。pin复用原Operation受限连接、前端选择绑定与动作校验；原operations核心/SQL/ACL/业务模型/用户库不改，不回源normal、不触旧selector/failed目标。采用明确受控连接参数检查和最终dist真实Chromium/routes，零新PG/SQL/API/Vite/Native/preview/provider/费用/公网，无新TCP监听。

前向活动最多10800含最后1200清场，占原C02剩余额，旧9188.720111加最多19988.720111不超21600；原硬日历2026-10-15T08:54:00Z与接收后24h取早。新增根2/累计最多23且原上限24不变，Browser2/累计最多7且原9不变；build2，明确累计build6加1至7以保留一次有据修正复检，不清旧5。offline本轮1800/旧172.317/总7200，holding本轮600含120清场/旧462.047/总10800不扩。旧PG success9/9/start37/37不解冻，其它子余额不借。

本轮先读取/实现/夹具自检，后集中验证并允许范围内有据普通修复；不是每遇一次夹具失败就退卡。同因两次修正仍失败/根因不稳/越界/上限才停相关。最终方法绑定实际源/脚本/bundle、如实标受控层，并将旧PG两秒样本说明为只到reading的过D拒绝，不重造后段PG通过。

完整卡DocuN/tasks/TASK-114.md已保存复读待人工转交，未实际派发/接收。原115保持独立；工程稳定后只复核两余项及真实传播。所有正式共享/DEF/CHG由主控维护。原所有失败、C01 9739.953/旧55525.796净unknown、115活动8617.261566、G11/25/UNKNOWN/R60/count1/13元/626.566不改。

## 以下为旧工程许可与历史原字节

'''
prefix(WORK114, work114, old[WORK114])

arch = f'''# 架构动态文档

文档v1.30，{day}，Asia/Shanghai。需求v1.2、执行动态v2.54、task_model/07；以下v1.29历史原字节保留。

## STEP017取消和正文两根因已关闭，截止pin与输入生命周期仍阻断

{at}。主控据TASK115 review-01和原件关闭DEF-034/F01、DEF-037/F04：取消请求/准确收尾/不可逆短CAS及同RR完整正文资格机制有效，真实文件/PG撤权/HTTP与最终bundle相应证据适用。原已充分正常链、31域、角色/两FK/RootLease/原SUP与G11不重新审计。

DEF-035/F02仍P1，restore._load的LoadingReferencePin另建固定3秒PG身份连接、没有原Operation/剩余statement与lock门；其余已贯通D和晚到完成事实保持。DEF-036/F03仍P1，全局身份反序已修，但删除policy/上传/plan及scope选择更改不推进输入版本，旧结果可重填并错误确认。修复限同Operation传播和当前输入绑定/动作前校验，不扩业务模型/SQL/权限或原核心协议。

旧真实PG两秒deadline实际仅在reading阶段失败，未到capture后publication延迟点；不能据此证明后段PG，但实际读取拒绝与文件后段仍有效。C03以受控连接参数检查和最终dist的精确route交互验证这两处，不开PG/恢复主链，不将替身写真实数据库。产品未修前STEP017不关闭。

原采用永久只读范围、source frozen和旧selector保护、UNKNOWN/25/R60及费用/历史停止边界不变；完整NFR005恢复继续、STEP018—020、M-1/项目发布尚未通过。用户库/真实资料/费用/外发均无新许可。

## 以下为v1.29及更早历史

'''
prefix(ARCH, arch, old[ARCH])

state = f'''# 执行动态文档

文档v2.54，{day}，Asia/Shanghai。唯一总状态账；需求v1.2、架构v1.30、task_model/07。以下v2.53历史原字节保留。

## TASK115 review-01已返回，两DEF关闭；TASK114 C03已登记

{at}。原独立115/R109 review-01已接收/执行/返回，报告61253字节/3d6a4ce4e30284f6799f61462e84c419a9fdd7226ef1f1e73dc468815b04a0f2，原37767字节后缀完整。主控235 current、1117保护登记、23本轮/358原独审原件和七规则匹配，独立性与旧暴露披露接受；独审交付验收通过，代码/证据部分、控制本轮只读合规。

DEF-034/F01取消覆盖成功根因与DEF-037/F04依赖正文投影根因由主控关闭，只限已采用有限切片。DEF-035/F02保持P1开放：原件loading pin独立连接/查询未接同D；DEF-036/F03保持P1开放：用户policy/文件/plan、范围选择变化没有淘汰旧结果与动作资格。全局CAP反序已修，不把旧GET plan方法当上传策略竞态。STEP017仍阻塞待修/待独审，不把两个关闭扩成整阶段通过。

旧真实PG deadline实际reading后失败且未到发布延迟，按审计更正A层范围，真实读取超时、文件后段、正常PG/角色/31域/两序/原SUP/G11继续有效。review-01本轮活动3126.578112，审计累计8617.261566/21600，首工具mono缺同步采样及保守扣时保留；新增全部业务0，原审计root3/API3/Browser2/offline125.610/hold14.874不变，未用余额不自动恢复许可。

原工程C02仍封存root21/24、PG create9/12、success9/9/start37/37、Windows11/12、API8/11、Browser5/9、build5/6、offline172.317/hold462.047、C02活动9188.720111，旧C01 9739.953/旧55525.796净unknown及所有失败保留。review无新消费者，沿用已保存九容器/17消费者停止原件和2026-10-13准确metadata，不冒今天重新启动或实查。source frozen/原target07、新C02 target01 readonly/failed对象全部冻结，不借旧执行权。

C03原TASK114/R108已登记，完整卡保存阶段进行，未派发/接收。A+继续原工程窗，原115不接管修复，TASK116未占。不重批方案、不回PG：pin实际产品受控连接参数检查、前端输入绑定与最终dist route矩阵作为一个完整成果；不安装/新镜像/服务器/真实模型费用。

新许可TASK-114-STEP017-C03-20261014只激活10800活动含1200清场，旧C02加最多19988.720111仍在原21600内，原2026-10-15T08:54:00Z硬日历与接收24h取早。新增根最多2/累计23/原24，Browser最多2/累计7/原9，build最多2且累计上限6明确加1至7；offline新1800/原总7200，holding新600含最后120/原总10800。PG/SQL/create/start/API/Vite/Native/preview/provider/费用/公网全部新增0。实际接收再追加唯一control历史，主控不提前改执行账或假计新用量。

主控仅身份/原件/直接代码核证及共享维护，产品运行0。关闭两问题不删除历史，剩余两项原115稳定后仅问题及传播复核。G11/25/UNKNOWN/R60/count1/13元/626.566/Must不减，STEP018—020、项目/发布不签。回收在TASK115/orchestration-review01-receipt-20261014；卡/许可/输入/旧文档/保存证明在TASK114/orchestration-repair-c03-20261014。CHG1355—1363，下一1364。

## 以下为v2.53及更早历史

'''
prefix(STATE, state, old[STATE])
contract = (OUT / 'effective-contract.md').read_bytes()
text = contract.decode('utf-8-sig')
assert '*' not in text and not re.search(r'^\|', text, re.MULTILINE)
for value in ('目标与交付', '项目、规则与接收', '断点和最小充分输入', '实现成果A', '实现成果B',
              '允许文件与冻结边界', '验证与证据成果C', '许可、预算与资源', '停止、回传与必要人工',
              'C1 真实产品调用的受控连接检查', 'C2 最终构建的一次合并浏览器矩阵', '10800秒',
              '本轮新增Browser启动最多2次', '原操作键', '原PG deadline只证读取阶段超时'):
    assert value in text, value
CARD.write_bytes(contract)
assert CARD.read_bytes() == contract
final_state = state.replace('TASK114 C03已登记', 'TASK114 C03待人工转交')
final_state = final_state.replace('完整卡保存阶段进行，未派发/接收', '完整卡已保存复读待人工转交，未派发/接收')
prefix(STATE, final_state, old[STATE])

entries = [
    ('DocuN/evidence/TASK-115/orchestration-review01-receipt-20261014/received.json', '核235当前/1117保护登记/23原件与旧后缀，独审交付接受，关闭两原根因、两P1保留。'),
    ('DocuN/results/TASK-115-work-decision.md', 'review-01真实返回/三轴/计时保守账与两项精确传播，未派新复核。'),
    ('DocuN/results/TASK-114-work-decision.md', '同TASK/R原工程续作03，双修+定向验证，不回PG、不清旧额。'),
    ('DocuN/evidence/TASK-114/orchestration-repair-c03-20261014/effective-contract.md；DocuN/tasks/TASK-114.md', '完整pin截止和policy/plan/scope生命周期修复卡，保存复读待人工。'),
    ('DocuN/evidence/TASK-114/orchestration-repair-c03-20261014/continuation-permit.json；input-manifest.json；window-assignment.json', '旧余量内10800活动/固定日历，根2/Browser2/build2，build累计明确加1至7，其余消费0。'),
    ('DocuS/架构动态文档.MD', 'v1.30：DEF034/037关闭，035/036明确漏链和原PG deadline证据范围纠正。'),
    ('DocuS/执行动态文档.MD', 'v2.54唯一实际账，独审已回/工程新续作待转交、历史保留与无新产品操作。'),
    ('DocuN/evidence/TASK-114/orchestration-repair-c03-20261014/before-documents/TASK-114.md', '原C02完整卡/共享文档原字节封存，旧许可不恢复。'),
    ('DocuN/evidence/TASK-114/orchestration-repair-c03-20261014/delivery-proof.json', '完整合同/指纹/预算/状态与原报告产品旧账保护、CHG连续保存核对。'),
]
addition = '\r\n' + ''.join(f'- CHG-{1355 + index}，{at}，Codex编排Agent，{path}。{reason}\r\n\r\n'
                             for index, (path, reason) in enumerate(entries))
CHANGES.write_bytes(old[CHANGES] + addition.encode('utf-8'))
after = [int(value) for value in re.findall(r'^- CHG-(\d+)', CHANGES.read_text(encoding='utf-8-sig'), re.MULTILINE)]
assert after == numbers + list(range(1355, 1364))
assert CHANGES.read_bytes().startswith(old[CHANGES])
for path_text, expected in protected.items():
    assert identity(Path(path_text)) == expected, path_text
for row in received['current']:
    if not row['exists']:
        assert not (ROOT / row['path']).exists()
for path in (WORK114, WORK115, ARCH, STATE):
    assert path.read_bytes().endswith(old[path])
save('delivery-proof.json', {
    'created_at': at, 'client_date': day, 'state': 'saved_readback_complete_pending_manual_transfer',
    'card': record(CARD), 'contract_equal': CARD.read_bytes() == contract,
    'permit': record(OUT / 'continuation-permit.json'), 'inputs': record(OUT / 'input-manifest.json'),
    'window': record(OUT / 'window-assignment.json'),
    'shared_documents': [record(path) for path in (WORK114, WORK115, ARCH, STATE, CHANGES)],
    'old_card': record(backup / CARD.name), 'shared_history_original_bytes_preserved': True,
    'protected_count': len(protected), 'protected_mismatches': [],
    'known_removed_outputs_still_absent': True,
    'closed_defects': ['DEF-034/F01', 'DEF-037/F04'], 'open_P1': ['DEF-035/F02', 'DEF-036/F03'],
    'STEP017_closed': False, 'TASK116_allocated': False,
    'new_runtime_before_dispatch': 0, 'new_dispatch_confirmed': False,
    'CHG_added': list(range(1355, 1364)), 'next_CHG': 1364,
    'product_execution_by_orchestrator': 0,
})
print(json.dumps({'state': 'saved_readback_verified', 'card': record(CARD),
                  'versions': ['architecture1.30', 'execution2.54'], 'closed': ['F01', 'F04'],
                  'open': ['F02', 'F03'], 'dispatch': '待人工转交', 'CHG': '1355—1363'}, ensure_ascii=False))
