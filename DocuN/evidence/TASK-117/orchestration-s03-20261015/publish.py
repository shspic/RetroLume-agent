"""Read metadata and maintain orchestration documents only; no product imports or runtime calls."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re
import copy

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
OUT = Path(__file__).resolve().parent
EXEC = ROOT / 'DocuN/evidence/TASK-117/execution'
C = EXEC / 'continuation-01'
CARD = ROOT / 'DocuN/tasks/TASK-117.md'
WORK = ROOT / 'DocuN/results/TASK-117-work-decision.md'
STATE = ROOT / 'DocuS/执行动态文档.MD'
ARCH = ROOT / 'DocuS/架构动态文档.MD'
CHANGE = ROOT / 'DocuS/文档变更记录.MD'
at = datetime.now(timezone(timedelta(hours=8))).isoformat()


def ident(path):
    if not path.is_file():
        return {'exists': False, 'bytes': 0, 'sha256': None}
    raw = path.read_bytes()
    return {'exists': True, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def save(name, value):
    path = OUT / name
    assert not path.exists(), path
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


managed = (CARD, WORK, STATE, ARCH, CHANGE)
before = {p: p.read_bytes() for p in managed}
assert STATE.read_text(encoding='utf-8-sig').splitlines()[2].startswith('文档v2.62，')
assert ARCH.read_text(encoding='utf-8-sig').splitlines()[2].startswith('文档v1.35，')
numbers = [int(x) for x in re.findall(r'^- CHG-(\d+)', CHANGE.read_text(encoding='utf-8-sig'), re.M)]
assert numbers[-1] == 1433
rules = read(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
for row in rules:
    assert ident(Path(row['absolute_path']))['sha256'] == row['sha256']
receipt = read(C / 'result-save-receipt.json')
result = ROOT / 'DocuN/results/TASK-117-result.md'
assert ident(result)['sha256'] == receipt['sha256'] == '5f2e0a19f893dcd6634345b86149d9a35de41354cb50f2694f76a024ba1c0c8d'
assert hashlib.sha256(result.read_bytes()[-21405:]).hexdigest() == 'db9dd539274c9b77db237410de31a6c9cc75595bae3b758d6e6c2d5573351b53'
manifest = read(C / 'final-source-manifest.json')
assert len(manifest['entries']) == 113
for row in manifest['entries']:
    assert ident(ROOT / row['path']) == row['post'], row['path']
binding = read(C / 'final-binding.json')
for row in binding['bundle5']['files']:
    assert ident(ROOT / row['path'])['sha256'] == row['sha256']
budget = read(EXEC / 'budget.json')
assert budget['counts']['roots'] == 13 and budget['active_root'] is None
assert budget['phase'] == 'S02_returned_partial'
assert budget['counts']['api_starts'] == 11 and budget['counts']['frontend_builds'] == 5
stop_binding = read(C / 'final-resource-stop-binding.json')
stop_path = Path(stop_binding['path'])
assert ident(stop_path)['sha256'] == stop_binding['sha256']
stop = read(stop_path)
assert stop['all_stopped'] is True and not stop['listeners']
assert len(stop['pg']) == 3 and all(not x['running'] and x['pid'] == 0 for x in stop['pg'])
adoption = read(C / 'ordinary-db-fixes/adoption.json')
assert ident(ROOT / 'backend/migrations/014_step018_retrieval.sql')['sha256'] == adoption['new_migration_014_sha256']
derived = read(C / 'ordinary-db-fixes/derived-shape.json')
normalized_shape = copy.deepcopy(derived['shape'])
# Identity comparison follows the declared snapshot format in schema_profiles.py:83-94.
# The raw JSON file digest is distinct from this owner/grantor-normalized catalog identity.
for row in normalized_shape.get('columns', []):
    if row['relname'] == 'activities' and row['attname'] == 'outbound_grant_sha256' and row.get('owner_super') is True:
        row['owner'] = 'bootstrap_owner'
for section in ('columns', 'table_acl', 'functions'):
    for row in normalized_shape.get(section, []):
        if row.get('acl'):
            row['acl'] = re.sub(r'/[^,}]+', '/trusted_owner', row['acl'])
derived_digest = hashlib.sha256(json.dumps(normalized_shape, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
assert derived_digest == derived['sha256'] == adoption['new_shape_sha256']
legacy = read(C / 'ordinary-db-fixes/iteration01-adoption.json')['old_R01_chain']
for filename, expected in legacy.items():
    assert ident(ROOT / 'backend/migrations' / filename)['sha256'] == expected
function_pattern = r'CREATE(?: OR REPLACE)? FUNCTION public\.retrieval_chunk_guard\(\).*?AS \$([^$]+)\$(.*?)\$\1\$;'
functions = {}
for label, path in [('migration014', ROOT / 'backend/migrations/014_step018_retrieval.sql'), ('pending_sql', C / 'ordinary-db-fixes/pending-forward-repair.sql')]:
    body = re.search(function_pattern, path.read_text(encoding='utf-8-sig'), re.S).group(2)
    functions[label] = hashlib.sha256(re.sub(r'\s', '', body).encode()).hexdigest()
assert functions['migration014'] == functions['pending_sql'] == adoption['new_chunk_function_sha256']
protected_paths = list(dict.fromkeys([ROOT / x['path'] for x in manifest['entries']] + [
    result, EXEC / 'budget.json', EXEC / 'events.jsonl', EXEC / 'case-index.json',
    C / 'final-source-manifest.json', C / 'final-binding.json', C / 'result-save-receipt.json',
    C / 'final-budget-observed.json', C / 'final-resource-stop-binding.json', stop_path,
    C / 'ordinary-db-fixes/pending-forward-repair.sql', C / 'ordinary-db-fixes/adoption.json',
    C / 'ordinary-db-fixes/derived-shape.json', C / 'X03-X07-real-PG-only.json',
    C / 'source-closure-check.json', C / 'root12-cleanup-1792045254766060400.json'
]))
assert not any(p in managed for p in protected_paths)
protected = {str(p.relative_to(ROOT)): ident(p) for p in protected_paths}
save('input-manifest.json', {'at': at, 'protected': protected, 'rules': rules,
                             'private_storage_or_credentials_read': False})
received = {
    'at': at, 'TASK': 'TASK-117', 'R': 'R-111', 'STEP': '018',
    'actual_execution_result': ident(result), 'source_entries_verified': 113,
    'bundle_files_verified': 4, 'legacy_migration_files_verified': len(legacy),
    'S01_raw_suffix_preserved': True,
    'S02_axes': {'implementation': 'partial_candidate', 'evidence': 'partial_valid_by_actual_layer_and_version',
                'execution_control': 'S02_root_cap_stop_and_cleanup_evidence_confirmed; all_historical_deviations_retained'},
    'S_complete': False, 'S_acceptance': False, 'new_independent_audit_dispatched': False,
    'SQL_static_scope': {'SELECT_only_role': 'retrolume_interview_owner',
                         'tables': adoption['read_only_dependencies_added'],
                         'chunk_body_hashes': functions, 'expected_shape_derived_not_live_adopted': derived_digest,
                         'apply_and_PG_retest': 'NOT_RUN'},
    'confirmed_blockers': ['missing transitive SELECT', 'ambiguous DELETE alias',
                            '007 CancelledError / UNKNOWN cause not established',
                            'actual low-memory pressure', 'remaining frozen S matrix'],
    'root12_pressure_minimum_bytes': 97435648,
    'stop_at_evidence_time': {'at': stop['sample'], 'sha256': stop_binding['sha256'],
                             'all_stopped': True, 'PG_count': 3,
                             'no_main_live_Docker_or_process_observation_this_turn': True},
    'counts': budget['counts'], 'observed_time': read(C / 'final-budget-observed.json'),
    'client_Sol_quota_not_equated_with_business_or_SQL_failures': True,
    'main_product_runtime_build_test_SQL_or_provider_actions': 0,
    'orchestration_metadata_correction': 'First publication preflight compared raw shape JSON instead of declared owner/grantor-normalized identity; failed before writes; corrected after reading schema_profiles.py:83-98. No product or test was run.',
}
save('received.json', received)
permit = {
    'at': at, 'TASK': 'TASK-117', 'R': 'R-111', 'STEP': '018',
    'permit': 'TASK-117-STEP018-INTEGRATION-S03-20261015',
    'authorization': 'same user-approved TASK116 AP1 implementation; bounded forward continuation by orchestrator',
    'actual_received_at': None, 'dispatch_confirmed': False, 'execution_started': False,
    'start': 'first actual tool operation, UTC and monotonic sampled together; not issuance time',
    'activity_added_seconds': 21600, 'calendar_from_receipt_hours': 48,
    'no_expansion_after_seconds': 18000, 'save_only_after_seconds': 19800, 'save_reserve_seconds': 1800,
    'runtime_holding_added_seconds': 10800, 'offline_added_seconds': 3000, 'offline_all_task_cap_seconds': 7200,
    'prior_observation': {'S01_activity': 37651.0027854, 'S02_activity_at_return': 17303.702146,
                          'cumulative_activity': 54954.7049314, 'cumulative_runtime_conservative': 21921.454,
                          'cumulative_offline': 2546.561},
    'forward_totals_from_return_basis': {'activity': 76554.7049314, 'runtime_conservative': 32721.454, 'offline': 5546.561},
    'unrecorded_actual_prior_work_if_found': 'append honestly; no increase of added limits',
    'new_complete_real_target_roots_max': 4, 'S_total_roots_cap': 17, 'TASK_total_roots_cap': 18, 'Q_reserved_roots': 1,
    'root_business_seconds': 2100, 'root_cleanup_seconds': 300,
    'new_counts_caps': {'roots': 4, 'pg_starts': 12, 'api_starts': 8, 'frontend_builds': 2, 'browser_starts': 4},
    'cumulative_counts_caps': {'roots': 17, 'pg_starts': 28, 'api_starts': 19, 'frontend_builds': 7,
                               'browser_starts': 8, 'pg_create_attempts': 8, 'pg_objects': 5, 'volumes': 5,
                               'native_windows': 160, 'preview_creates': 12, 'preview_starts': 12, 'http': 3000,
                               'provider_calls': 0, 'actual_fee_microunits': 0},
    'counts_baseline_at_issuance': budget['counts'],
    'old_caps_failures_times_counter_history_preserved': True,
    'memory_stage_MiB': {'base_first_PG_API': 512, 'host_browser_second_PG': 768, 'fixed_preview': 1024},
    'pressure_cleanup': {'period_seconds': 2, 'below_MiB': 256, 'consecutive': 2, 'same_combo_retries_without_changed_environment': False},
    'normal_SQL_targets': ['source', 'compat'], 'R01_SQL_upgrade_allowed': False,
    'approved_SQL_identity': ident(C / 'ordinary-db-fixes/pending-forward-repair.sql'),
    'Q_active': False, 'AP2_80_requests_20_CNY_not_reapproved_or_consumed': True,
    'first_dependent_gates': ['exact resources and current old catalog', 'forward SQL and trusted new catalog',
                              'minimal actual normal embedding commit before dependent long chains'],
}
save('continuation-permit.json', permit)
backup = OUT / 'before-documents'
backup.mkdir(exist_ok=False)
for path, raw in before.items():
    (backup / path.name).write_bytes(raw)

def prefix(path, text):
    path.write_bytes(text.encode('utf-8') + before[path])
    assert path.read_bytes().endswith(before[path]), path

prefix(WORK, f'''# TASK117/R111 — S02部分成果核证，S03同号合并续作许可

{at}。用户返回S02部分结果，实际31949字节/5f2e0a19f893dcd6634345b86149d9a35de41354cb50f2694f76a024ba1c0c8d；113项最终身份和4项bundle、13个旧迁移均匹配，原S01后缀21405字节保留。分层成果部分采纳，不验收完整S；root13/13用满，active_root空、业务已交回。主控仅读源/差异/原始证据/元数据，不执行产品或重跑测试。

两项SQL根因与014/pre实际差异相符：invoker记忆资格传递需既有NOLOGIN interview_owner读取五表，DELETE局部变量c与别名冲突；修补只SELECT和purge_command别名，新函数摘要2b8801…31bab与014/前向SQL相同，新shape5b7dc68…dc12由受信旧目录及精确增量推导。允许在精确source/compat合成库先核旧目录、事务应用、核新目录/无写权并真实回归，不改R01目标或001—013；不签DB已修好。007 CancelledError/UNKNOWN真实根因仍未闭，trace成本对照不当最终结论。

当前S02压力最低约93MiB且自动清场实证有效。最终停止原件cd9292dd…2512绑定三CID stopped/Pid0、原birth退出/完整进程清单和端口，按其时点继承，不冒主控当前现场。最终build5 JS ff79970b…43af尚未加载；Browser3已提交学习动作保留，末answer/revision16未终评；R01装载seal有效但应用查看、R02往返和多项S仍缺。SQL修补源码未应用是直接前置，不能再原样整体重跑旧runner。

同AP1新增前向S03许可TASK-117-STEP018-INTEGRATION-S03-20261015，A+原工程窗口，当前卡待人工转交；原窗无额度则一个A+接续窗独占。首次实际工具同次UTC/QPC新首点，活动21600含1800收尾/48h，持有10800/offline3000且总offline7200；新完整真实目标根4/S累计17/TASK18保Q1，根2100+300，PGstart新增12至28/API新增8至19/build新增2至7，Browser仅原余4至8。其它create/对象/卷/Native/preview/HTTP/费用门保持。所有旧账/原超额/失败保留，新许可不追认S01/S02旧合规。

纯离线不另占真实根，根内有据普通修正按原截止连续复检，避免几十秒失败就换根。内存512/768/1024MiB/两次低于256MiB清场及原隔离不变；同组合再次压力退出则冻结对应段，不机械加入口。按SQL/最小提交、两链同库重开、只读恢复、预览与传播合并收口；PDF需新根因依据才准复验。仍不能解释的UNKNOWN只停依赖链，独立部分继续，不把源码或模板成功冒全部真实通过。

当前TASK117全文整理为单份有效合同，旧完整卡原字节放本次before-documents，产品116合同/历史失败/有效证据不变。完整S稳定才集中独审，Q未启用/真实provider与费用0，原80次20元条件许可不重问或消费；STEP018/019/020/M1/项目未通过。正式状态/编号仍主控维护，不改工程execution账/结果/私密。

核证、许可、身份、旧共享文档及保存证明在DocuN/evidence/TASK-117/orchestration-s03-20261015。

## 以下为原裁定历史

''')
prefix(ARCH, f'''# 架构动态文档

文档v1.36，2026-10-15，Asia/Shanghai。需求v1.3、执行动态v2.63、task_model/07；以下v1.35历史原字节保留，116采用包未扩大。

## STEP018候选SQL修补与当前动态边界

{at}。117/S02部分回收，113项候选身份已核。014当前3a919b2562ded5765de132519b841c1d1439c65c001795cfbd608cbc03586e78，R02预期shape5b7dc68a94101307bcbd63a16607c5b2ee79906b5f32669d764853a55172dc12；source/compat仍旧4aa808…/a3c9…，待准确前向事务与目录核证。增量仅interview_owner对memory invoker五项传递表SELECT及retrieval_chunk_guard删除分支别名更正；没有新表/字段/写权。001—013保持，R01永久只读目标不升级。

compat旧model/tool/NULL tokens/预算对账及R01物理seal/42501已有证据；不冒应用只读查看或R02往返。新整步query+model门、源白名单/共享grant实现和部分PG边界已有证据，Q未启用；真实跨活动外发及语义仍按其独审和启用门。007写期CancelledError尚未定因，UNKNOWN不重发不退款。bundle5构建可用、未实际加载；旧build4成功不追认为新字节通过。

真实低内存退出及当前有界清场有效，硬件压力不可用追加入口消除。S03在同AP1内先修SQL/最小正常提交，再按当前真实缺口连续收口；固定preview/Job/StopProof、正常库与只读恢复分离、原权限/退款主体不降。独审仍在完整稳定点集中安排，STEP018与项目未放行。

## 以下为v1.35及更早历史

''')
prefix(STATE, f'''# 执行动态文档

文档v2.63，2026-10-15，Asia/Shanghai。唯一总状态账；需求v1.3、架构v1.36、task_model/07。以下v2.62历史原字节保留。

## TASK117 S02部分交回已核证，S03同号合并卡待人工转交

{at}。TASK117/R111/S02已真实返回部分结果31949字节/5f2e0a19…c0c8d；113项对象含缺失标记、4bundle及13旧迁移与当前一致。实现轴部分候选、证据轴分层有效；完整S未完成，不安排提前全面独审。原S01后缀21405字节、root09停止不明/晚核与旧超额全部保留。S02返回时root13/13/active_root空，精确最终停止原件绑定三CID/Pid0、进程birth/清单及端口，按该时点核证，不冒主控实时监控。

当前累计PGcreate/object/volume3/PGstart16/API11/Browser4/build5/Native预记53/HTTP304，preview/provider/fee0。保存时S02活动17303.702146/持有5702.094/offline821.686；与S01累计54954.7049314/21921.454/2546.561。旧root10内存门拒、root11导航夹具及007 UNKNOWN、root12真实压力503、root13权限/触发器失败均保留，原root13 completed只指根收尾，不代表内部场景通过。

直接阻断为尚未应用的两项已定位SQL修补、007监督UNKNOWN根因未闭和真实低内存；完整两域/记忆/同库重开、最终bundle加载、R01应用查看/R02往返、L10及矩阵余项未完成。主控已核新014/前向SQL相同函数体与五表只读依赖，准在原source/compat先事务修补及目录核证；新shape为预期派生，不能从实测任意采信。正式014和新shape/实现候选状态见架构v1.36。

同号S03前向许可已保存待人工转交A+原工程窗；未登记已接收/执行，不建TASK118。新活动21600/48h含1800收尾、持有10800/offline3000且全任务7200，四个完整真实根/S累计17/TASK18保Q1；PG新增12/累计28、API新增8/19、build新增2/7，Browser原余4/8，其它资源/费用门不变。新增与累计同时核，旧cap/计数/失败/超额不改，不自动退旧时间或移用Q。接收首点实际记录，不使用签发时间假称执行已开始。

当前卡改为单份有效合同，旧完整卡原字节备份引用；纯离线不每脚本占真实根，普通修正在根原截止内连续，稳定S才集中独审。低内存阶段门和压力清场/隔离不变，同组合压力再现则停对应段，不反复要求用户释放内存或同根因盲试。Q未启用/原80次20元未消费，STEP018/019/020/M1/项目均未验收。

本轮主控只读核证和共享维护，无产品/测试/build/SQL/Docker/API/Browser/真实模型/费用/Git写。证据、许可、旧共享及保存证明在DocuN/evidence/TASK-117/orchestration-s03-20261015。CHG1434—1440，下一1441。

## 以下为v2.62及更早历史

''')
CARD.write_bytes((OUT / 'continuation.md').read_bytes())
assert CARD.read_bytes() == (OUT / 'continuation.md').read_bytes()
entries = [
    ('DocuN/evidence/TASK-117/orchestration-s03-20261015/received.json', 'S02部分成果、113身份/4bundle/13旧迁移、实际失败与精确停止按原时点核证。'),
    ('DocuN/tasks/TASK-117.md', '同号S03完整当前合同；新前向许可、合并根内修正，旧完整卡原字节备份，待人工转交。'),
    ('DocuN/results/TASK-117-work-decision.md', '两项SQL范围核证及真实执行前置，未签S完成，Q保持关闭。'),
    ('DocuS/架构动态文档.MD', 'v1.36候选014/预期新shape与旧实库不同、真实低内存及UNKNOWN边界。'),
    ('DocuS/执行动态文档.MD', 'v2.63唯一总账登记部分回收与S03待转交，旧失败/超限/计数保留。'),
    ('DocuN/evidence/TASK-117/orchestration-s03-20261015/before-documents', '五份原共享完整字节备份；input-manifest/continuation-permit绑定输入与前向上限。'),
    ('DocuN/evidence/TASK-117/orchestration-s03-20261015/save-proof.json', '保存复读与历史后缀保护，执行账/产品/旧报告/规则未被主控修改。'),
]
tail = ''.join(f'\r\n- CHG-{1434+i}，{at}，Codex编排Agent，{path}。{detail}\r\n'
               for i, (path, detail) in enumerate(entries))
CHANGE.write_bytes(before[CHANGE] + tail.encode('utf-8'))
assert CHANGE.read_bytes().startswith(before[CHANGE])
assert [int(x) for x in re.findall(r'^- CHG-(\d+)', CHANGE.read_text(encoding='utf-8-sig'), re.M)] == numbers + list(range(1434, 1441))
for rel, expected in protected.items():
    assert ident(ROOT / rel) == expected, rel
for row in rules:
    assert ident(Path(row['absolute_path']))['sha256'] == row['sha256']
for path in managed:
    assert '\ufffd' not in path.read_text(encoding='utf-8-sig')
    assert (backup / path.name).read_bytes() == before[path]
save('save-proof.json', {
    'at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
    'documents': [{'path': str(p), **ident(p)} for p in (*managed, OUT / 'continuation.md')],
    'old_full_card_raw_preserved_at': str(backup / CARD.name),
    'old_shared_history_suffixes_preserved': True, 'protected_identities_unchanged': len(protected),
    'rules_7_unchanged': True, 'source_113_identities_match': True,
    'product_execution_SQL_or_runtime_changes_by_main': 0,
    'execution_budget_events_or_old_results_written_by_main': False,
    'dispatch_confirmed': False, 'Q_active': False, 'CHG': list(range(1434, 1441)),
})
print(json.dumps({'status': 'SAVED_AND_READ_BACK', 'TASK': '117', 'R': '111', 'permit': 'S03',
                  'card': str(CARD), 'state': 'v2.63', 'architecture': 'v1.36',
                  'last_CHG': 1440, 'source_identity_matches': 113, 'product_execution': 0}, ensure_ascii=False))
