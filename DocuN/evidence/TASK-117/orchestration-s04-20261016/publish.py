"""Maintain orchestration records using file/JSON identities only; no product imports or runtime actions."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
OUT = Path(__file__).resolve().parent
EXEC = ROOT / 'DocuN/evidence/TASK-117/execution'
C = EXEC / 'continuation-02'
CARD = ROOT / 'DocuN/tasks/TASK-117.md'
WORK = ROOT / 'DocuN/results/TASK-117-work-decision.md'
ARCH = ROOT / 'DocuS/架构动态文档.MD'
STATE = ROOT / 'DocuS/执行动态文档.MD'
CHANGE = ROOT / 'DocuS/文档变更记录.MD'
at = datetime.now(timezone(timedelta(hours=8))).isoformat()


def ident(p):
    if not p.is_file():
        return {'exists': False, 'bytes': 0, 'sha256': None}
    raw = p.read_bytes()
    return {'exists': True, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def save(name, obj):
    p = OUT / name
    assert not p.exists(), p
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


managed = (CARD, WORK, ARCH, STATE, CHANGE)
before = {p: p.read_bytes() for p in managed}
assert STATE.read_text(encoding='utf-8-sig').splitlines()[2].startswith('文档v2.63，')
assert ARCH.read_text(encoding='utf-8-sig').splitlines()[2].startswith('文档v1.36，')
numbers = [int(x) for x in re.findall(r'^- CHG-(\d+)', CHANGE.read_text(encoding='utf-8-sig'), re.M)]
assert numbers[-1] == 1440
rules = read(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
for x in rules:
    assert ident(Path(x['absolute_path']))['sha256'] == x['sha256']
result = ROOT / 'DocuN/results/TASK-117-result.md'
receipt = read(C / 'result-save-receipt.json')
assert ident(result) == receipt['result_identity']
assert ident(result)['sha256'] == '4347b1e249f2d405ecc7ef39c66c78253ebc5c971266781e1a17c8205e59d473'
assert hashlib.sha256(result.read_bytes()[-31949:]).hexdigest() == '5f2e0a19f893dcd6634345b86149d9a35de41354cb50f2694f76a024ba1c0c8d'
manifest = read(C / 'final-source-manifest.json')
assert len(manifest['entries']) == 136
for x in manifest['entries']:
    assert ident(ROOT / x['path']) == x['post'], x['path']
bundle = read(C / 'bundle-6.json')
for x in bundle['files']:
    assert ident(ROOT / x['path'])['sha256'] == x['sha256']
budget = read(EXEC / 'budget.json')
assert budget['phase'] == 'S03_returned_partial' and budget['active_root'] is None
assert budget['counts']['roots'] == 16 and budget['counts']['pg_objects'] == 5
assert budget['counts']['browser_starts'] == 8
stop_binding = read(C / 'final-resource-stop-binding.json')
stop_path = Path(stop_binding['path'])
assert ident(stop_path)['sha256'] == stop_binding['sha256']
stop = read(stop_path)
assert stop['all_stopped'] is True and not stop['listeners']
assert len(stop['pg']) == 5 and all(not x['running'] and x['pid'] == 0 for x in stop['pg'])
restore = read(C / 'restore-final-disposition.json')
assert [(x['slot_id'], x['state']) for x in restore['targets']] == [('r01', 'sealed'), ('r02-fault', 'failed'), ('r02', 'failed')]
assert all(x.get('temporary_credentials_revoked') for x in restore['targets'] if x['state'] == 'failed')
protected_paths = list(dict.fromkeys([ROOT / x['path'] for x in manifest['entries']] + [
    result, EXEC / 'budget.json', EXEC / 'events.jsonl', EXEC / 'case-index.json',
    C / 'result-save-receipt.json', C / 'final-source-manifest.json', C / 'final-binding.json',
    C / 'final-budget-observed.json', C / 'final-resource-stop-binding.json', stop_path,
    C / 'restore-final-disposition.json', C / 'final-r02-valid-plan.json',
    C / 'final-r02-hash-failed.json', C / 'source-r02-final-package.json',
    C / 'metadata-corrections.json', C / 'neutral-results-readback.json',
    C / 'validation-summary.json', C / 'bundle-6.json', C / 'bundle-6-actual-HTTP.json',
    C / 'PDF-unclosed.json'
]))
assert not any(x in managed for x in protected_paths)
protected = {str(p.relative_to(ROOT)): ident(p) for p in protected_paths}
save('input-manifest.json', {'at': at, 'protected': protected, 'rules': rules,
                             'private_credentials_or_packages_opened_by_main': False})
received = {
    'at': at, 'TASK': 'TASK-117', 'R': 'R-111', 'STEP': '018',
    'result': ident(result), 'source_identity_matches': 136, 'bundle_identity_matches': len(bundle['files']),
    'old_S02_raw_suffix_preserved': True,
    'axes': {'implementation': 'substantial_partial_candidate', 'evidence': 'valid_by_actual_layer_and_as_run_binding',
             'execution_control': 'cleanup_confirmed_at_recorded_time; activity/offline_overruns_and_first_clock_capture_issue_not_passed'},
    'reuse': ['SQL applied source/compat and trusted R02 shape', 'new persistent teaching and selected-memory interview',
             'normal app restart continuity', 'memory edit/revoke late invalidation',
             'source deletion and R02 source package', 'bundle6 actual HTTP bytes', 'bad hash restore failed as expected'],
    'open': ['valid R02 component timeout', 'P02/new successful P03 application read-only viewing',
             'final bundle6 browser evidence', 'real preview never started', 'progress reason contradiction',
             'current_mode fixture error', 'remaining L08/X02/X04/X08 and PDF'],
    'static_restore_cost_fact': {'call_path': 'RestoreController._load per-row bounded -> Operation.check -> ControlHub.state -> full journal validate/replay',
                                 'status': 'candidate overhead, not yet measured root cause',
                                 'component_30_seconds_not_raised': True},
    'reason_fact': 'candidate None is used both for insufficient evidence and no successor, while progress already evidence_sufficient',
    'resource_stop': {'sample': stop['sample'], 'sha256': stop_binding['sha256'], 'PG_count': 5,
                      'all_stopped': True, 'live_main_observation': False},
    'restore_targets': [{'slot': x['slot_id'], 'target_id': x['target_id'], 'state': x['state'],
                         'cid': x['cid'], 'credentials_revoked': x.get('temporary_credentials_revoked')}
                        for x in restore['targets']],
    'counts': budget['counts'], 'S_complete': False, 'independent_audit': 'not yet stable complete S',
    'main_product_test_build_SQL_Docker_or_provider_execution': 0, 'Q_active': False,
}
save('received.json', received)
slots = [
    {'slot_id': 'r02-success-01', 'container': 'retrolume-step018-syn-r02-success-01',
     'volume': 'retrolume-step018-syn-r02-success-01-data', 'port': 15486, 'database': 'step018_r02_success_01'},
    {'slot_id': 'r02-success-02', 'container': 'retrolume-step018-syn-r02-success-02',
     'volume': 'retrolume-step018-syn-r02-success-02-data', 'port': 15487, 'database': 'step018_r02_success_02'},
]
save('continuation-permit.json', {
    'at': at, 'permit': 'TASK-117-STEP018-INTEGRATION-S04-20261016', 'TASK': 'TASK-117', 'R': 'R-111',
    'basis': 'same approved AP1; forward repair of actual remaining integration and R02 runtime blocker',
    'dispatch_confirmed': False, 'actual_received_at': None, 'execution_started': False,
    'activity_added_seconds': 14400, 'calendar_hours_from_receipt': 48,
    'no_expand_after_seconds': 10800, 'save_only_after_seconds': 13200, 'save_reserve_seconds': 1200,
    'runtime_holding_added_seconds': 7200, 'offline_added_seconds': 2400,
    'cumulative_offline_forward_cap': 9000, 'old_offline_cap_7200_and_overrun_preserved': True,
    'prior_actual_observed': read(C / 'final-budget-observed.json')['cumulative'],
    'new_real_roots_max': 3, 'S_total_roots_cap': 19, 'TASK_total_roots_cap': 20, 'Q_reserved_roots': 1,
    'root_business_seconds': 2100, 'root_cleanup_seconds': 300,
    'new_counts_caps': {'roots': 3, 'pg_starts': 9, 'api_starts': 6, 'browser_starts': 4,
                        'frontend_builds': 2, 'pg_objects': 2, 'volumes': 2},
    'cumulative_counts_caps': {'roots': 19, 'pg_starts': 36, 'api_starts': 24, 'browser_starts': 12,
                               'frontend_builds': 8, 'pg_create_attempts': 8, 'pg_objects': 7, 'volumes': 7,
                               'native_windows': 160, 'http': 3000, 'preview_creates': 12, 'preview_starts': 12,
                               'provider_calls': 0, 'actual_fee_microunits': 0},
    'counts_baseline': budget['counts'], 'new_slots': slots,
    'slot_first_gate': 'specific cause/evidence, scoped repair and discriminating offline checks before create',
    'second_slot_gate': 'new concrete difference and justified repair after first attempt, within remaining permit',
    'failed_targets_never_reused': True,
    'memory_stage_MiB': {'base_firstPG_API': 512, 'host_browser_secondPG': 768, 'fixed_preview': 1024},
    'pressure_cleanup': {'sample_period_seconds': 2, 'below_MiB': 256, 'consecutive': 2},
    'old_times_caps_counter_history_or_failures_reset': False,
    'Q_active': False, 'AP2_80_requests_20_CNY_unchanged': True,
})
backup = OUT / 'before-documents'
backup.mkdir(exist_ok=False)
for p, raw in before.items():
    (backup / p.name).write_bytes(raw)


def prefix(p, text):
    p.write_bytes(text.encode('utf-8') + before[p])
    assert p.read_bytes().endswith(before[p]), p


prefix(WORK, f'''# TASK117/R111 — S03部分回收与S04恢复装载/剩余集成许可

{at}。实际S03报告40682字节/4347b1e249f2d405ecc7ef39c66c78253ebc5c971266781e1a17c8205e59d473，136项当前对象含缺失标志、bundle6四项身份匹配，原31949字节S02后缀保持。两库SQL修补、合法新检索提交、持久两域及同normal应用重开、记忆晚到失效和删源/包事实分层采纳，不重跑；不是完整S通过。旧UNKNOWN及trace因果未知边界保留。

已核两个R02目标真实failed：hash-fault按预期integrity_failed；有效617行/3938960字节包组件30秒operation_timeout。均撤临时凭据并停止，五对象/卷已满，不能重置失败对象。代码确认每行bounded经Operation.check全日志验证/重放，系可疑重复开销，未以静态路径签实测根因。理由candidate=None混同证据不足和无后继为具体源码问题；current_mode被夹具误读mode也已证。固定preview尚未创建，bundle6 HTTP绑定有效而最终U未完成，R01/R02应用查看及PDF等仍缺。

按最终停止绑定96eff71c…10422，五CID停止/Pid0、登记birth退出及完整清单/端口在2026-10-16 05:45时点成立，本轮主控未实启停/实查Docker，不冒实时监控。S03 elapsed31724.280143/21600、offline3682.780117/3000超额与首采漏钟/保守下界保留，执行控制不签通过。报告中间中断期间资源已停，不把该间隔计作真实PG或offline，但不改原elapsed门。

同TASK117/R111新增前向S04，A+原工程窗，待人工转交。先在副本/已有原件上具体定位装载慢点并完成等价修复与定向反例，再使用新的独立成功目标；不延长组件30秒/拆事务/关检查/换小包。最多两个新slot r02-success-01/02（15486/15487、同名-data），旧5对象均留，总对象/卷7；第二次必须有新的具体差异和修正依据，不能重复赌通过。factory现有最多8slot范围内仅扩本任务正常测试配置，不改产品恢复权限。两个新目标仍失败则冻结依赖，不暗开第八对象。

前向活动14400/48h含1200收尾，持有7200/offline2400，offline全任务前向门9000，旧7200和超额留史。新真实根3/S累计19/TASK20保Q1，PG新增9至36/API新增6至24/Browser新增4至12/build新增2至8；PGcreate总8/Native160/HTTP3000/preview各12不加，其它安全/低内存分阶段512/768/1024MiB及压力清场不降。新段收到后同次UTC/QPC首点，不追造新执行；旧预算/实际/失败不清零。

当前卡为单一有效合同，旧卡原字节备份。先完成全部normal余项再不可逆只读选择，核真实selector/fence路线，禁止清空或伪造选择；应用查看两profile不回normal/不fallbacksource。最终U、预览、理由/夹具与恢复收口在卡内连续做，不重做已足两域/旧审计。完整S稳定后才集中隔离审计，Q/80次20元条件门仍关闭/未消费，STEP018/019/020/M1/项目未通过。

证据/许可/输入/旧共享备份及保存证明在DocuN/evidence/TASK-117/orchestration-s04-20261016；主控仅读源/原件与共享维护，未写产品/执行账/旧报告/私密。

## 以下为原裁定历史

''')
prefix(ARCH, f'''# 架构动态文档

文档v1.37，2026-10-16，Asia/Shanghai。需求v1.3、执行动态v2.64、task_model/07。以下v1.36历史原字节保留，116采用包不变。

## STEP018实际SQL/两域闭环与剩余恢复、界面边界

{at}。117/S03核证source/compat已实际按批准GRANT及函数别名修补，014为3a919b…86e78、R02受信shape5b7dc68…dc12，旧001—013和R01不改。新检索合成真实received有效；旧UNKNOWN不重发，trace与旧取消异常的唯一因果未证。

新学习93852e50-f648-4cb1-a2e8-5f8283975567有两个独立实例/一个受助、evidence_sufficient；单节点无后继却写不足的reason分支仍需修正，旧事实不改。选记忆面试06c8a779-a936-423d-9554-010f9ebcfb8e ended，正常应用同库重开/后续反馈、两域记忆晚到失效与删源覆盖有实际层证据，不能冒最终新bundle U或真实Q语义。

bundle6已真实HTTP绑定，Browser只加载旧bundle5。HTML资格ACL精确投影修补有真实PG证，固定preview仍无artifact/ACK/PNG/StopProof。新R02包617行/两个space/向量/007/unknown/删源事实已发布，但有效恢复目标组件30秒超时，另一hash-fault正确failed；两个目标永久保留且不激活。R01保持sealed，新reader应用查看未闭。

S04只在同协议内定位/修复恢复重复开销、理由和夹具，并补剩余实际U/预览/应用只读证。性能优化不得降低取消/CAS/日志完整性或改变组件/事务/容量合同；新成功slot仅本地合成资源配置，不新增模型或业务表。正常写与单向readonly选择顺序必须正确，不能为测试便利清空fence/回normal。完整S与新增边界集中独审仍未通过，Q未启用。

## 以下为v1.36及更早历史

''')
prefix(STATE, f'''# 执行动态文档

文档v2.64，2026-10-16，Asia/Shanghai。唯一总状态账；需求v1.3、架构v1.37、task_model/07。以下v2.63历史原字节保留。

## TASK117 S03部分回收，S04剩余集成/恢复修复待人工转交

{at}。用户真实带回117/R111/S03结果40682字节/4347b1e2…d473；136项对象及4bundle身份一致，旧S02原31949字节后缀完整。实现/证据轴为 substantial partial，已实际应用两库SQL、合法检索提交、持久两域与正常应用重开、晚到记忆失效及删源/源包，均按对象层继承。完整S未通过，不重跑已充分层，不提前全面独审。

主要剩余为有效R02装载超时、新reader R01/R02应用查看、最终bundle6 U、真实固定preview、教学理由矛盾及少量传播/PDF。617行有效包组件30秒operation_timeout，hash故障按预期failed；两个目标均撤loader/停止，五对象/卷满。主控读到每行check触发全日志验证/重放的重复路径，尚未签定量根因；拒绝仅加入口、提高30秒或复用failed对象重试。

当前root16/active_root空，PGcreate/object/volume5、PGstart27/API18/Browser8/build6/Native预记113/HTTP1207、preview/provider/fee0。五CID stopped/Pid0、所有已登记birth退出/346进程清单和端口由05:45原件绑定96eff71c…10422支持，不冒本轮主控现场观察。S03 elapsed31724.280143超10124.280143、offline3682.780117超682.780117及首采缺口照留，执行控制不通过。累计活动86678.9850744/保守持有23476.767/offline6229.341117。

同号S04完整卡已保存待人工转交原A+工程窗，未登记已接收/执行，无TASK118。新活动14400/48h含1200收尾、持有7200/offline2400；offline全任务前向门9000，旧7200和超额不改。新真实根3/S累计19/TASK20保Q1，PG新增9/累计36、API6/24、Browser4/12、build2/8；PGcreate总8、Native160/HTTP3000/preview12保持。最多两个新r02-success-01/02精确slot与卷，15486/15487，总对象/卷7；先有原因/修复/离线区别门，第二次需新具体差异/修正，不毁旧目标。其它低内存与安全边界不变。

当前卡/输入/许可/原共享备份及保存证明在DocuN/evidence/TASK-117/orchestration-s04-20261016。普通修复及剩余证据同卡合并，所有normal动作在不可逆readonly选择前完成；不伪造selector/清fence/回normal。Q仍0/20元80次条件门未启，稳定S后集中独审，STEP018/019/020/M1/项目均未通过。主控产品/测试/build/SQL/Docker/API/Browser/模型/费用/Git写0，原执行账和旧报告不写。CHG1441—1447，下一1448。

## 以下为v2.63及更早历史

''')
CARD.write_bytes((OUT / 'continuation.md').read_bytes())
entries = [
    ('DocuN/evidence/TASK-117/orchestration-s04-20261016/received.json', 'S03部分实际成果/136身份/四bundle/五CID停止与失败/超额核证。'),
    ('DocuN/tasks/TASK-117.md', 'S04单份有效合并合同，装载因果门、两个有条件新成功slot和剩余最终U/预览/只读查看。'),
    ('DocuN/results/TASK-117-work-decision.md', '部分采纳不签完整S，明确前向时间/对象/投入增量及旧失败保持。'),
    ('DocuS/架构动态文档.MD', 'v1.37实际SQL/两域/包与R02失败、bundle6 U和preview的真实适用范围。'),
    ('DocuS/执行动态文档.MD', 'v2.64唯一总账，S03已回收且S04待人工转交，无新执行或提前独审。'),
    ('DocuN/evidence/TASK-117/orchestration-s04-20261016/before-documents', '原五份共享文件字节备份，输入/许可绑定保存。'),
    ('DocuN/evidence/TASK-117/orchestration-s04-20261016/save-proof.json', '保存复读、原后缀/旧卡备份与受保护执行/产品/规则身份未改。'),
]
tail = ''.join(f'\r\n- CHG-{1441+i}，{at}，Codex编排Agent，{path}。{detail}\r\n'
               for i, (path, detail) in enumerate(entries))
CHANGE.write_bytes(before[CHANGE] + tail.encode('utf-8'))
assert CARD.read_bytes() == (OUT / 'continuation.md').read_bytes()
assert CHANGE.read_bytes().startswith(before[CHANGE])
assert [int(x) for x in re.findall(r'^- CHG-(\d+)', CHANGE.read_text(encoding='utf-8-sig'), re.M)] == numbers + list(range(1441, 1448))
for p in managed:
    assert (backup / p.name).read_bytes() == before[p]
    assert '\ufffd' not in p.read_text(encoding='utf-8-sig')
for rel, expected in protected.items():
    assert ident(ROOT / rel) == expected, rel
for x in rules:
    assert ident(Path(x['absolute_path']))['sha256'] == x['sha256']
save('save-proof.json', {
    'at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
    'documents': [{'path': str(p), **ident(p)} for p in (*managed, OUT / 'continuation.md')],
    'old_full_card_raw_backup': str(backup / CARD.name),
    'old_shared_history_suffixes_preserved': True, 'source_136_match': True,
    'protected_identities_unchanged': len(protected), 'rules_7_unchanged': True,
    'product_execution_or_execution_budget_events_or_old_results_written_by_main': False,
    'runtime_resources_created_started_or_stopped_by_main': 0,
    'dispatch_confirmed': False, 'Q_active': False, 'CHG': list(range(1441, 1448)),
})
print(json.dumps({'status': 'SAVED_AND_READ_BACK', 'TASK': '117', 'R': '111', 'permit': 'S04',
                  'card': str(CARD), 'state': 'v2.64', 'architecture': 'v1.37',
                  'last_CHG': 1447, 'source_matches': 136, 'product_execution': 0}, ensure_ascii=False))
