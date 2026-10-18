"""Read source/evidence identities and maintain orchestration documents only."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re

R = Path('D:/shspic/project_NO3_RetroLume-agent')
O = Path(__file__).resolve().parent
E = R / 'DocuN/evidence/TASK-117/execution'
C = E / 'continuation-04'
CARD = R / 'DocuN/tasks/TASK-117.md'
WORK = R / 'DocuN/results/TASK-117-work-decision.md'
ARCH = R / 'DocuS/架构动态文档.MD'
STATE = R / 'DocuS/执行动态文档.MD'
CHANGE = R / 'DocuS/文档变更记录.MD'
AT = datetime.now(timezone(timedelta(hours=8))).isoformat()


def ident(p):
    if not p.is_file():
        return {'exists': False, 'bytes': 0, 'sha256': None}
    raw = p.read_bytes()
    return {'exists': True, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def save(name, value):
    p = O / name
    assert not p.exists(), str(p)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


managed = (CARD, WORK, ARCH, STATE, CHANGE)
before = {p: p.read_bytes() for p in managed}
assert STATE.read_text(encoding='utf-8-sig').splitlines()[2].startswith('文档v2.65，')
assert ARCH.read_text(encoding='utf-8-sig').splitlines()[2].startswith('文档v1.38，')
numbers = [int(x) for x in re.findall(r'^- CHG-(\d+)', CHANGE.read_text(encoding='utf-8-sig'), re.M)]
assert numbers[-1] == 1454
rules = read(R / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
for item in rules:
    assert ident(Path(item['absolute_path']))['sha256'] == item['sha256']
result = R / 'DocuN/results/TASK-117-result.md'
expected_result = {'exists': True, 'bytes': 63687,
                   'sha256': '4ba3402549f8d7a9c5a9cb4c6e26825ae174aae5bbdcd5740294e95ed73bbe00'}
assert ident(result) == expected_result
assert hashlib.sha256(result.read_bytes()[-48950:]).hexdigest() == '67f3656fb1f0a602957ac0a8274205d1c51127e1028d9925c05ea8af31f15bc4'
manifest = read(C / 'final-source-manifest.json')
assert len(manifest['entries']) == 163
for item in manifest['entries']:
    assert ident(R / item['path']) == item['post'], item['path']
binding = read(C / 'final-binding.json')
assert binding['result']['sha256'] == expected_result['sha256']
for item in binding['files']:
    assert ident(Path(item['path']))['sha256'] == item['sha256'], item['path']
for name, key in [('budget.json', 'canonical_budget_sha256'), ('events.jsonl', 'canonical_events_sha256'),
                  ('case-index.json', 'canonical_case_index_sha256')]:
    assert ident(E / name)['sha256'] == binding[key], name
bundle = read(C / 'final-bundle-7-binding.json')
assert len(bundle['files']) == 4
for item in bundle['files']:
    assert ident(R / item['path']) == {'exists': True, 'bytes': item['bytes'], 'sha256': item['sha256']}
stop_binding = read(C / 'final-resource-stop-binding.json')
stop_path = Path(stop_binding['path'])
assert ident(stop_path)['sha256'] == stop_binding['sha256']
stop = read(stop_path)
assert stop['all_stopped'] and len(stop['pg']) == 6 and not stop['listeners']
assert all(not p['running'] and p['pid'] == 0 for p in stop['pg'])
budget = read(E / 'budget.json')
assert budget['phase'] == 'S05_returned_partial_save_only' and budget['active_root'] is None
counts = {'roots': 21, 'pg_create_attempts': 6, 'pg_objects': 6, 'volumes': 6,
          'pg_starts': 39, 'api_starts': 28, 'browser_starts': 13, 'frontend_builds': 7,
          'native_windows': 138, 'preview_creates': 1, 'preview_starts': 1, 'http': 2209,
          'provider_calls': 0, 'actual_fee_microunits': 0}
assert budget['counts'] == counts
observed = read(C / 'final-budget-observed.json')
recovery = read(C / 'old-preview-recovery.json')
assert recovery['status']['state'] == 'failed_unstarted'
assert recovery['status']['reserved_seconds'] == 0 and recovery['status']['settled_seconds'] == 60
assert recovery['proof']['tree_confirmation'] == 'never_started' and not recovery['outstanding']
assert recovery['old_first_attempt']['confirmed'] is False and recovery['old_first_attempt']['proof'] is None
reader = read(C / 'R01-reader-verified.json')
assert reader['caps']['current_mode'] == 'restored_readonly' and reader['formal_activation'] is False
assert len(reader['records']) == 7 and len(reader['writes_refused']) == 4
assert reader['source_selector_and_fence_unchanged']
for browser in ('browser-12', 'browser-13'):
    proof = read(C / browser / 'proof.json')
    assert proof['status'] == 'passed' and proof['browser_closed']
overlay = read(C / 'R02-overlay-dependency-preflight.json')
assert not overlay['current_missing'] and overlay['selector'] is None and overlay['fence'] is None
repo = read(C / 'repository-final.json')
assert repo['HEAD'] == '45951501d2741630a229762d6b2d3f4b34d7f702'
for p in repo['protected']:
    assert ident(R / '.git' / p['file'])['sha256'] == p['sha256']
assert ident(R / '.git/config')['sha256'] == repo['config_sha256']
config = (R / '.git/config').read_text()
assert '[remote "origin"]' in config and 'https://github.com/shspic/RetroLume-agent.git' in config
for name, amount in [('snapshot-final-tests.log', 8), ('recovery-adapter-tests.log', 2), ('reader-config-tests-02.log', 3)]:
    raw = (C / name).read_text()
    assert f'Ran {amount} tests' in raw and raw.rstrip().endswith('OK')

extra = [result, E / 'budget.json', E / 'events.jsonl', E / 'case-index.json',
         C / 'final-binding.json', C / 'final-source-manifest.json', C / 'source-changes.diff',
         C / 'final-bundle-7-binding.json', C / 'final-resource-stop-binding.json', stop_path,
         C / 'old-preview-recovery.json', C / 'R01-reader-verified.json', C / 'R02-overlay-dependency-preflight.json',
         C / 'preview-stage-cost-final.json', C / 'PDF-bounded-diagnosis.json',
         C / 'browser-12/proof.json', C / 'browser-13/proof.json',
         C / 'snapshot-final-tests.log', C / 'recovery-adapter-tests.log', C / 'reader-config-tests-02.log',
         R / 'backend/app/memory/contracts.py', R / 'backend/app/memory/service.py',
         R / 'backend/migrations/010_learning_memory.sql', R / 'DocuN/results/TASK-102-result.md',
         R / 'DocuN/evidence/TASK-116/design/acceptance-contract.md',
         R / 'DocuN/evidence/TASK-116/design/integration-contract.md',
         R / 'DocuS/最终需求文档.MD', R / 'AGENTS.md', R / '.git/HEAD', R / '.git/config', R / '.git/index']
extra += [Path(x['path']) for x in binding['files']]
protected_paths = list(dict.fromkeys([R / x['path'] for x in manifest['entries']] + extra))
assert not any(p in managed for p in protected_paths)
protected = {str(p.relative_to(R)): ident(p) for p in protected_paths}
backup = O / 'before-documents'
backup.mkdir(exist_ok=False)
for p in managed:
    (backup / p.name).write_bytes(before[p])

save('received.json', {
    'at': AT, 'TASK': 'TASK-117', 'R': 'R-111', 'received_stage': 'S05',
    'result': expected_result, 'raw_48950_suffix_unchanged': True,
    'source_entries_match': 163, 'bundle_assets_match': 4, 'bound_evidence_files_match': 16,
    'seven_locked_rules_match': True,
    'A_behavior': {'old_preview_new_normal_recovery': 'never_started', 'old_first_StopProof': 'UNCONFIRMED',
        'old_preview_settled_seconds': 60, 'old_preview_reserved_seconds': 0, 'outstanding_owned': [],
        'JCODE_only_scope': 'real HTTP/PG/Native, synthetic transport',
        'final_bundle_U': ['same key and different body', 'late view', 'copied owner', 'four ledgers', 'whole step refusal', 'refresh GET only'],
        'R01_reader_real_HTTP_kinds': 7, 'R01_reader_real_POST_refusals': 4,
        'R01_real_activate': False, 'R01_final_browser_U': 'not_run', 'final_focused_tests': 13},
    'current_stop_evidence': {'path': str(stop_path), **ident(stop_path), 'sample': stop['sample'],
        'six_pg_nonrunning_pid_zero': True, 'listeners': [], 'main_live_runtime_probe': False},
    'execution_control': {'S05_offline_overrun_preserved': True, 'unknown_gap_seconds': 12557.422,
        'unknown_gap_not_claimed_CPU_or_complete_active_work': True, 'observed_final_budget': observed},
    'remaining': ['PDF HTTP causal layer and two-page review', 'fixed preview ready/ACK/PNG/normal StopProof',
        'R01 final UI', 'R02 normal readonly activation/HTTP/UI', 'affected new matrix assertions and Q later'],
    'X02': 'controller corrects command mapping; physical deletion and invalidation evidence still required',
    'repo': {'origin_configured_and_read_back': True, 'URL': 'https://github.com/shspic/RetroLume-agent.git',
        'HEAD_unchanged': True, 'index_unchanged': True, 'remote_live_refs': 'unverified connection reset',
        'commits_pushes_uploads': 0},
    'implementation_axis': 'partial_candidate', 'evidence_axis': 'valid_by_scope_and_bytes',
    'control_axis': 'not_passed_due_to_preserved_overrun_and_missing_first_sample',
    'stable_S_accepted': False, 'Q_enabled': False, 'main_product_runtime_or_tests_or_Git_writes': 0,
})
permit = {
    'at': AT, 'permit': 'TASK-117-STEP018-INTEGRATION-S06-20261016', 'TASK': 'TASK-117', 'R': 'R-111',
    'basis': 'same approved AP1; controller corrects X02 testing/command mismatch; no new deletion model',
    'dispatch_confirmed': False, 'actual_received_at': None, 'execution_started': False,
    'activity_added_seconds': 14400, 'calendar_hours_from_receipt': 48,
    'no_expand_after_seconds': 10800, 'save_only_after_seconds': 13200, 'save_reserve_seconds': 1200,
    'runtime_holding_added_seconds': 5400,
    'offline_cap_seconds': None, 'cumulative_offline_forward_cap': None,
    'offline_stop_policy': 'S06 has no second cross-interruption rolling offline cap; preserve all old caps and overruns; activity and resource hard gates remain',
    'offline_process_run_cap_seconds': 1800,
    'pause_policy': 'explicit no-resource/no-inflight suspension sample before external wait; unexpected gaps remain unknown and require stop/account review, no historical refunds',
    'baseline_observed': observed, 'baseline_counts': counts,
    'new_real_roots_max': 4, 'S_total_roots_cap': 25, 'TASK_total_roots_cap': 26, 'Q_reserved_roots': 1,
    'root_business_seconds': 2100, 'root_cleanup_seconds': 300,
    'new_counts_caps': {'roots': 4, 'pg_starts': 8, 'api_starts': 6, 'browser_starts': 3,
        'frontend_builds': 2, 'preview_creates': 2, 'preview_starts': 2,
        'pg_create_attempts': 1, 'pg_objects': 1, 'volumes': 1},
    'cumulative_counts_caps': {**counts, 'roots': 25, 'pg_starts': 47, 'api_starts': 34, 'browser_starts': 16,
        'frontend_builds': 9, 'preview_creates': 3, 'preview_starts': 3, 'native_windows': 160,
        'http': 3000, 'pg_create_attempts': 7, 'pg_objects': 7, 'volumes': 7},
    'conditional_only_target': {'slot': 'r02-success-02', 'name': 'retrolume-step018-syn-r02-success-02',
        'volume': 'retrolume-step018-syn-r02-success-02-data', 'host': '127.0.0.1', 'port': 15487,
        'database': 'step018_r02_success_02', 'gate': 'only actual newly required tombstones absent from old plan; default reuse sealed success01'},
    'new_independent_delete_action_allowed': False, 'X02_contract_correction': str(O / 'X02-contract-correction.md'),
    'PDF_diagnostic_HTTP_max': 1, 'PDF_causal_fix_HTTP_recheck_max': 1, 'PDF_total_analysis_implementation_seconds': 1800,
    'low_memory_stages_MiB': {'base': 512, 'pg': 512, 'api': 512, 'browser': 768, 'second_pg': 768, 'preview': 1024},
    'pressure_MiB': 256, 'pressure_consecutive': 2, 'pressure_sampling_seconds': 2,
    'isolation_permissions_deadlines_and_stopping_semantics_unchanged': True,
    'Git_writes': 0, 'Q_enabled': False, 'provider_calls_cap': 0, 'actual_fee_microunits_cap': 0,
}
save('continuation-permit.json', permit)
save('input-manifest.json', {
    'at': AT, 'rules': rules,
    'protected_inputs': [{'path': str(R / rel), **value} for rel, value in protected.items()],
    'old_shared_inputs': [{'path': str(p), **ident(backup / p.name), 'raw_preserved_at': str(backup / p.name)} for p in managed],
    'main_actions': 'standard library read/hash/JSON/source inspection, read-only OS memory and Git metadata, shared document maintenance',
    'main_product_tests_compile_build_SQL_Docker_API_Browser_provider_or_Git_mutation': 0,
})
save('X02-source-basis.json', {
    'at': AT, 'correction': ident(O / 'X02-contract-correction.md'),
    'files': [{'path': str(p), **ident(p)} for p in extra if p in [R / 'backend/app/memory/contracts.py',
        R / 'backend/app/memory/service.py', R / 'backend/migrations/010_learning_memory.sql',
        R / 'DocuN/results/TASK-102-result.md', R / 'DocuN/evidence/TASK-116/design/acceptance-contract.md', R / 'DocuS/最终需求文档.MD']],
    'facts': ['MemoryCommandInput has save/revise/revoke/purge only', 'revoke explicitly requires purge_memory_content confirmation',
        'MemoryService commits revocation then submits deterministic purge', 'purge requires original tombstone and exact immutable manifest',
        'purge removes each targeted version body while retaining metadata', 'NFR005/DR002 require observable deletion, not literal independent delete action'],
    'requires_new_adoption_package': False, 'product_physical_delete_not_accepted_from_source_alone': True,
})

work = f'''# TASK117/R111 — S05分层回收、X02纠正与S06收口许可

{AT}。真实S05结果63687字节/4ba34025…bbe00，163项身份、4bundle、16绑定与原48950后缀匹配。原预览正常恢复never_started/60秒全额结算/R0/精确owned结束、J-CODE单范围、最终bundle7同键/晚view/复制owner/四账/整步拒绝、R01七类HTTP与四种POST拒写、13项定向检查和实际origin关联分层采纳。原首次StopProof仍UNCONFIRMED，不把正常恢复或当前不存在回写成首次成功；完整S仍部分候选。

X02-source-basis及X02-contract-correction已落盘。主控纠正原卡把三个可观察效果误写为三个独立持久动作：批准G9/010/API只有save/revise/revoke/purge，删除正文由明确撤销后的精确purge承载。原116字面与S04/S05错误保留，用户“主控补合同”据此处理；没有新delete接口/迁移/权限，不降低正文确实清掉及依赖失效Must。旧有效修订/撤销/清理/晚到证据复用，缺项只读核实际对象；解除等待新增delete持久模型这一虚构前置，R02仍须真实normal工作结束/无未知owned/overlay相符才能切换。

原6tombstone tuple在success01 overlay、current_missing为空；默认复用sealed target634aa034…481d8，只做必要正式只读切换，不再恢复。R01兼容HTTP已闭、最终缓存身份guard与API27适用性分层；最后U待补。PDF旧两次HTTP422和孤立成功有区别，S05诊断没有覆盖实际拒绝层，S06授一个有限带阶段观察的HTTP诊断及仅因果修补后的最多一次复检；不是无差异裸试。

S05新预览两次门均在预扣/启动前拒绝，最终可用1016.121MiB低于1024；R01 Browser631.410低于768。没有新增preview尝试，局部gate0.891→0.125秒不冒完整启动修复。S06优先preview分时再低内存部分，门/隔离/t0/3/4.5/8/D/StopProof保持，仍不足仅停物理依赖，不让用户反复腾内存。原17:36停止hash5d35ff02…507c支持六CID/Pid0和端口/出生实例，仅其时点，不冒主控实时Docker核查。

当前roots21/PGcreate对象卷6/PGstart39/API28/Browser13/build7/Native138/HTTP2209/preview1/provider费用0，active_root空、phase已交回。S05最终活动16611.729874、持有159.953、offline16451.527874/10800超5651.527874；累计107417.9019484/24981.454/25463.164991，旧offline19812超5651.164991。12557.422秒中断缺连续采样按原保守上界照留，不声称实际CPU/全部活动，也不归0或追认合规。

S06同号原A+完整卡已保存待人工转交。新活动14400/48h含1200收尾、持有5400、离线进程1800；不再设置第二个跨中断滚动offline硬门，旧连续口径和超额留史，所有离线分类仍记录，activity/resource门不断。新4根/S25/TASK26保Q1，根2100+300；PG新增8/47、API6/34、Browser3/16、build2/9，Native160/HTTP3000保持，preview新增各2/总3；仅有实际新删除差异才准success02各create/对象/卷最多7。明确阶段结算与外部等待挂起，意外未知不伪造暂停；控制器须识别新段而非fallback旧amendment/API/offline门。

GitHub origin已实际为https://github.com/shspic/RetroLume-agent.git，本地HEAD/index未变；原远端refs查询连接重置，当前远端内容不冒已核。1318项是公开候选未通过敏感/上传裁定。本卡Git写0/不push，使用说明和来源范围继续维护。稳定S后集中隔离A+审计，Q/80次20元条件门仍关闭，STEP018/019/020/M1/项目未通过。

本轮主控只读核证、一次只读OS内存/本地Git元数据及共享文档维护，产品/测试/build/SQL/Docker/API/Browser/供应商/费用/Git写0。输入/许可/原共享备份/纠正及保存证明在DocuN/evidence/TASK-117/orchestration-s06-20261016；未替工程改报告/账/旧证据。

## 以下为原裁定历史

'''
arch = f'''# 架构动态文档

文档v1.39，2026-10-16，Asia/Shanghai。需求v1.3、执行动态v2.66、task_model/07。以下v1.38历史原字节保留，116主要采用包不扩大。

## STEP018当前恢复、sealed-reader及删除验收映射

{AT}。117/S05原precreate失败preview经真实正常恢复never_started、60秒保守结算及精确data_owned闭环；首次StopProof不确认仍保留。当前完整字节/身份缓存新增writable尾帧拒绝和control_id换hub围栏；局部gate profile0.891→0.125秒，阶段时钟已加但真实新preview因启动前内存门未运行，不宣称就绪/ACK/PNG/正常StopProof。变更候选待集中独审，不放宽计时、锁/取消/CAS/owned或停止主体。

新增隔离sealed-reader配置经正常产品构造，只持目标只读凭据、真实R01 profile/目标/权限核对，七类HTTP历史可读、四类POST拒绝；不具source写/loader/维护/provider/preview执行配置，不改原selector/fence，不冒正式activate。API27证据与后续缓存防换hub增量按身份区分，R01最终U仍缺。bundle7及原两域业务未变，S05补真实同键/视图/owner/账门，未重建bundle。

X02主控补充纠正测试组织：可修订、逻辑撤销、精确删除正文三个效果映射既有revise/revoke/purge，取消不存在第三种独立delete命令的要求，不新增模型或迁移、不降低实际清理/失效/历史保留Must。旧批准矩阵文字与错误卡面留史，当前证据仍逐效果核对。若无新tombstone，已sealed成功R02覆盖保持，可在normal收口后沿原单向选择器正常切换，无需再装载。

PDF原HTTP路径仍未定界；S06只准有限观察实际parse/Job/输出层的诊断和有据普通修补，保持原样本/限额/隔离。公开GitHub origin已实际关联，本地HEAD/index未变，尚无新提交/上传，公开候选范围不是发布通过。完整S/Q/STEP/全项目仍未验收。

## 以下为v1.38及更早历史

'''
state = f'''# 执行动态文档

文档v2.66，2026-10-16，Asia/Shanghai。唯一总状态账；需求v1.3、架构v1.39、task_model/07。以下v2.65历史原字节保留。

## TASK117 S05部分已核证，X02合同已纠正，S06收口待人工转交

{AT}。S05报告63687字节/4ba34025…bbe00、163源/4bundle/16绑定与48950旧后缀匹配。旧preview正常never_started恢复、60秒全额结算和精确owned闭环，J-CODE、bundle7同键/晚view/复制owner/四账/整步预算U、R01七类HTTP和四类拒POST、13定向检查、README和origin实际关联分层采纳。完整S未稳定，Q仍0，不重做原两域/重开/同包恢复。

当前phase S05_returned_partial_save_only/active_root空；roots21、PGcreate/对象/卷6、PGstart39/API28/Browser13/build7/Native138/HTTP2209、preview1/provider费用0。S05最终活动16611.729874/持有159.953/offline16451.527874，离线超5651.527874；累计活动107417.9019484/持有24981.454/offline25463.164991，旧前向19812超5651.164991。约12557.422秒无连续采样中断为原保守上界，不能称全部实际执行；原所有失败、漏首点与超额不追改。原17:36停止hash5d35ff02…507c支持六CID/Pid0/端口/原birth，仅其时点；主控没有现场Docker启停。

X02误要求独立delete是主控验收组织问题，已在orchestration-s06-20261016/X02-contract-correction.md纠正：既有revise/revoke/purge分别证明修订、墓碑失效、精确正文清理；无新delete action/endpoint/迁移/权限。原用户保留/设计字面和旧卡原件保持，现解除“等待新增持久删除合同”的前置，物理清理和失效实证仍必须。原success01当前overlay涵盖全部六tuple，无新删除默认不建success02，normal余项后再单向只读activate。

实际余缺为PDF真实HTTP/两页确认、固定preview正常ready/ACK/PNG/StopProof、R01最终U/R02正式只读链及新增实际矩阵。预览和R01 Browser上轮均因内存门启动前拒绝，不算新preview尝试；局部优化不能冒完整启动成功。S06优先preview按真实资源分时，PDF先准备有限阶段观察再一次诊断，有确定原因才一次复检；已足证据和Q未启用不制造重复全链前置。

S06完整同号原A+卡已保存待人工转交，未登记接收/新执行，不建TASK118。新活动14400/48h含1200收尾、持有5400、离线进程1800；取消本新段第二个跨中断offline累计停止门，旧账和旧cap不改，分类/未知继续记录，activity/resource硬门保持。新4根/S25/TASK26保Q1、根2100+300，PG新增8/47/API6/34/Browser3/16/build2/9，Native160/HTTP3000不加、preview新增各2/总3；条件success02仅实际新tombstone差异才各create/对象/卷加1至7。512/768/1024MiB和<256两次压力清场、安全隔离/费用门不变，控制器需显式认本段许可。

GitHub origin现已真实关联shspic/RetroLume-agent，HEAD45951501…7f702/index未改，远端实时refs因连接重置仍未核。1318候选不冒公开敏感审查或上传通过；当前Git写0、不push。完整S稳定再集中隔离独审，Q/80次20元门未启，STEP018/019/020/M1/项目未通过。主控仅只读/共享维护，没有产品/测试/build/SQL/Docker/API/Browser/provider/费用/Git写。输入/纠正/许可/备份/保存证明在orchestration-s06-20261016。CHG1455—1462，下一1463。

## 以下为v2.65及更早历史

'''
for prefix in (work, arch, state):
    assert '*' not in prefix and '|' not in prefix
outputs = {CARD: (O / 'continuation.md').read_bytes(), WORK: work.encode('utf-8') + before[WORK],
           ARCH: arch.encode('utf-8') + before[ARCH], STATE: state.encode('utf-8') + before[STATE]}
changes = [
    ('DocuN/evidence/TASK-117/orchestration-s06-20261016/received.json', 'S05真实增量/163源/4bundle/16绑定和旧报告核证，保留停止/超额/未知边界。'),
    ('DocuN/evidence/TASK-117/orchestration-s06-20261016/X02-contract-correction.md', '纠正三效果与三持久动作混淆，保持删除实效Must及原设计历史，不新增模型。'),
    ('DocuN/tasks/TASK-117.md', 'S06完整合并卡，优先预览、PDF可区分诊断、真实只读链和前向计量许可。'),
    ('DocuN/results/TASK-117-work-decision.md', 'S05分层采纳、解除错误delete前置、明确S06授权和原账保留。'),
    ('DocuS/架构动态文档.MD', 'v1.39记录真实恢复/缓存/reader候选、删除映射与尚未验证层。'),
    ('DocuS/执行动态文档.MD', 'v2.66唯一总账，S05返回/S06待转交、当前计数/未知超额/GitHub已关联。'),
    ('DocuN/evidence/TASK-117/orchestration-s06-20261016/before-documents', '原五共享原字节、输入/许可/删除依据保存，不修改工程源/执行账。'),
    ('DocuN/evidence/TASK-117/orchestration-s06-20261016/save-proof.json', '保存复读/历史与受保护源、报告、Git、规则身份一致证明。'),
]
tail = ''.join(f'\r\n- CHG-{1455+i}，{AT}，Codex编排Agent，{path}。{detail}\r\n'
               for i, (path, detail) in enumerate(changes))
outputs[CHANGE] = before[CHANGE] + tail.encode('utf-8')
for p in managed:
    assert p.read_bytes() == before[p]
for p, raw in outputs.items():
    p.write_bytes(raw)
assert CARD.read_bytes() == (O / 'continuation.md').read_bytes()
for p in (WORK, ARCH, STATE):
    assert p.read_bytes().endswith(before[p])
assert CHANGE.read_bytes().startswith(before[CHANGE])
assert [int(x) for x in re.findall(r'^- CHG-(\d+)', CHANGE.read_text(encoding='utf-8-sig'), re.M)] == numbers + list(range(1455, 1463))
for p in managed:
    assert (backup / p.name).read_bytes() == before[p]
    assert '\ufffd' not in p.read_text(encoding='utf-8-sig')
for rel, expected in protected.items():
    assert ident(R / rel) == expected, rel
for item in rules:
    assert ident(Path(item['absolute_path']))['sha256'] == item['sha256']
save('save-proof.json', {
    'at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
    'documents': [{'path': str(p), **ident(p)} for p in (*managed, O / 'continuation.md', O / 'X02-contract-correction.md')],
    'before_documents_raw_preserved': True, 'old_history_suffixes_unchanged': True,
    'source_entries_match': 163, 'bundle_assets_match': 4, 'bound_evidence_files_match': 16,
    'locked_rules_match': 7, 'protected_identities_unchanged': len(protected), 'CHG': list(range(1455, 1463)),
    'product_execution_ledger_result_or_Git_written_by_main': False,
    'main_runtime_resources_created_started_stopped': 0, 'dispatch_confirmed': False, 'Q_enabled': False,
})
print(json.dumps({'status': 'SAVED_AND_READ_BACK', 'TASK': '117', 'R': '111', 'permit': 'S06',
    'card': str(CARD), 'state': 'v2.66', 'architecture': 'v1.39', 'last_CHG': 1462,
    'source_matches': 163, 'X02_contract_correction_saved': True, 'product_execution': 0}, ensure_ascii=False))
