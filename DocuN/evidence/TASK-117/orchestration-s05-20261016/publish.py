"""Document maintenance and read-only file identities; no product/runtime imports."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
OUT = Path(__file__).resolve().parent
EXEC = ROOT / 'DocuN/evidence/TASK-117/execution'
C = EXEC / 'continuation-03'
CARD = ROOT / 'DocuN/tasks/TASK-117.md'
WORK = ROOT / 'DocuN/results/TASK-117-work-decision.md'
ARCH = ROOT / 'DocuS/架构动态文档.MD'
STATE = ROOT / 'DocuS/执行动态文档.MD'
CHANGE = ROOT / 'DocuS/文档变更记录.MD'
AT = datetime.now(timezone(timedelta(hours=8))).isoformat()


def ident(p):
    if not p.is_file():
        return {'exists': False, 'bytes': 0, 'sha256': None}
    raw = p.read_bytes()
    return {'exists': True, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def save(name, value):
    path = OUT / name
    assert not path.exists(), str(path)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


managed = (CARD, WORK, ARCH, STATE, CHANGE)
before = {p: p.read_bytes() for p in managed}
assert STATE.read_text(encoding='utf-8-sig').splitlines()[2].startswith('文档v2.64，')
assert ARCH.read_text(encoding='utf-8-sig').splitlines()[2].startswith('文档v1.37，')
numbers = [int(v) for v in re.findall(r'^- CHG-(\d+)', CHANGE.read_text(encoding='utf-8-sig'), re.M)]
assert numbers[-1] == 1447
rules = read(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
assert len(rules) == 7
for entry in rules:
    assert ident(Path(entry['absolute_path']))['sha256'] == entry['sha256']
result = ROOT / 'DocuN/results/TASK-117-result.md'
assert ident(result) == {'exists': True, 'bytes': 48950,
    'sha256': '67f3656fb1f0a602957ac0a8274205d1c51127e1028d9925c05ea8af31f15bc4'}
assert hashlib.sha256(result.read_bytes()[-40682:]).hexdigest() == '4347b1e249f2d405ecc7ef39c66c78253ebc5c971266781e1a17c8205e59d473'
manifest = read(C / 'final-source-manifest.json')
assert len(manifest['entries']) == 155
for entry in manifest['entries']:
    assert ident(ROOT / entry['path']) == entry['post'], entry['path']
binding = read(C / 'final-binding.json')
for name, key in (('final-source-manifest.json', 'source_manifest_sha256'),
                  ('final-case-index.json', 'case_index_sha256')):
    assert ident(C / name)['sha256'] == binding[key]
assert ident(EXEC / 'budget.json')['sha256'] == binding['budget_sha256']
stop_path = Path(binding['stop']['path'])
assert ident(stop_path)['sha256'] == binding['stop']['sha256']
stop = read(stop_path)
assert stop['all_stopped'] and len(stop['pg']) == 6 and not stop['listeners']
assert all(not row['running'] and row['pid'] == 0 for row in stop['pg'])
budget = read(EXEC / 'budget.json')
assert budget['phase'] == 'S04_returned_partial' and budget['active_root'] is None
expected_counts = {'roots': 18, 'pg_create_attempts': 6, 'pg_objects': 6, 'volumes': 6,
                   'pg_starts': 33, 'api_starts': 22, 'browser_starts': 11,
                   'frontend_builds': 7, 'native_windows': 136, 'preview_creates': 1,
                   'preview_starts': 1, 'http': 2068, 'provider_calls': 0, 'actual_fee_microunits': 0}
assert budget['counts'] == expected_counts
bundle = read(C / 'bundle-7.json')
assert len(bundle['files']) == 4
for entry in bundle['files']:
    assert ident(ROOT / entry['path'])['sha256'] == entry['sha256']
restore = read(C / 'P03-S04-verified.json')
assert restore['receipt']['state'] == 'verified' and restore['target']['state'] == 'sealed'
assert restore['receipt']['root_sha256'] == 'b040841394dfa82a14c2b180e60393b3b7f0d222b11016b468a81d6f17c3a347'
assert restore['target']['target_id'] == '634aa034-51f6-4510-b075-38cb005481d8'
assert len(restore['proof']['actual_rows']) == 31 and restore['proof']['execution_authority'] is False
assert restore['target']['readonly_probe']['writes_rejected'] == ['42501', '42501', '42501']
ui = read(C / 'final-UI-passed.json')
assert ui['bundle_identity'] == '58a87abf5ff4b02b33aab5dc3735507f4f097791e021aeb4ddfbf0b62ac115e8'
assert not ui['proof']['errors'] and ui['proof']['browser_closed']
assert [(x['kind'], x['HTTP']) for x in ui['proof']['dropped']] == [('answer', 200), ('query', 200), ('feedback', 200)]
observed = read(C / 'final-budget-observed.json')
preview_dir = EXEC / 'synthetic/source-data/preview-control/5c508dc7-2ac6-44fb-922b-8e8de4b9f006'
failure = read(preview_dir / 'failure.json')
registry = read(preview_dir / 'registry.json')
assert failure['code'] == 'reaper_not_ready' and failure['stage'] == 'reaper_start'
failure_from_t0 = (failure['at_ns'] - (registry['deadline_ns'] - 60_000_000_000)) / 1e9
assert abs(failure_from_t0 - 3.515) < .001
assert read(preview_dir / 'supervisor-result.json')['proof'] is None

protected_paths = list(dict.fromkeys([ROOT / entry['path'] for entry in manifest['entries']] + [
    result, EXEC / 'budget.json', EXEC / 'events.jsonl', EXEC / 'case-index.json',
    C / 'final-source-manifest.json', C / 'final-binding.json', C / 'final-case-index.json',
    C / 'result-save-receipt.json', C / 'final-readback.json', C / 'final-budget-observed.json',
    C / 'final-resource-stop-binding.json', stop_path, C / 'P03-S04-verified.json',
    C / 'final-UI-passed.json', C / 'bundle-7.json', C / 'source-changes.diff',
    C / 'preview-late-current-absence.json', C / 'restore-cost-final-diagnosis.json',
    C / 'snapshot-profile.txt', C / 'reason-sufficient-no-successor-persistent.json',
    ROOT / 'backend/app/preview/production_supervisor.py', ROOT / 'backend/app/preview/production_reaper.py',
    ROOT / 'backend/app/data_exit/control.py', ROOT / 'backend/app/data_exit/maintenance.py',
    ROOT / 'backend/app/data_exit/restore.py', ROOT / 'AGENTS.md', ROOT / '.gitignore',
    ROOT / '.git/HEAD', ROOT / '.git/config', ROOT / '.git/index',
    preview_dir / 'failure.json', preview_dir / 'reaper-ready.json',
    preview_dir / 'registry.json', preview_dir / 'supervisor-result.json',
]))
assert not any(path in managed for path in protected_paths)
protected = {str(path.relative_to(ROOT)): ident(path) for path in protected_paths}
backup = OUT / 'before-documents'
backup.mkdir(exist_ok=False)
for path in managed:
    (backup / path.name).write_bytes(before[path])

save('received.json', {
    'at': AT, 'TASK': 'TASK-117', 'R': 'R-111', 'received_stage': 'S04',
    'result': ident(result), 'old_S03_40682_byte_suffix_unchanged': True,
    'A_behavior': {'R02_same_package_verified_sealed_seconds': restore['verify_seconds'],
        'rows': 617, 'canonical_tables': 31, 'readonly_writes_rejected': ['42501'] * 3,
        'new_target_id': restore['target']['target_id'],
        'X08_original_key_GET_after_three_COMMIT_body_losses': True,
        'final_bundle_7_actually_loaded': True, 'browser_11_closed': True,
        'two_independent_instances_with_no_successor_reason_persisted': True},
    'B_identity': {'source_entries': 155, 'bundle_assets': 4, 'seven_locked_rules_match': True,
        'binding_hashes_match': True, 'raw_report_history_preserved': True},
    'preview': {'id': registry['preview_id'], 'failure': 'reaper_not_ready',
        'failure_seconds_from_reserve_t0': failure_from_t0,
        'ready_file_mtime_after_failure_seconds': round((preview_dir / 'reaper-ready.json').stat().st_mtime - (preview_dir / 'failure.json').stat().st_mtime, 6),
        'specific_slow_subcall_not_yet_established': True, 'first_StopProof': 'UNCONFIRMED',
        'current_absence_evidence_not_retroactive_stop_proof': True},
    'stop_evidence': {'path': str(stop_path), **ident(stop_path), 'sample': stop['sample'],
        'six_pg_nonrunning_pid_zero': True, 'listeners': [], 'live_main_runtime_probe': False},
    'implementation_axis': 'partial_candidate_with_valid_completed_layers',
    'evidence_axis': 'partial_reuse_by_version_scope_and_layer',
    'execution_control_axis': 'S04_offline_overrun_preserved_not_passed',
    'budget_observed': observed, 'stable_S_accepted': False,
    'independent_audit_started': False, 'Q_enabled': False,
    'main_product_runtime_or_tests_or_git_writes': 0,
})
permit = {
    'at': AT, 'permit': 'TASK-117-STEP018-INTEGRATION-S05-20261016',
    'TASK': 'TASK-117', 'R': 'R-111', 'basis': 'same approved AP1, targeted remaining integration; user-specified GitHub repository',
    'dispatch_confirmed': False, 'actual_received_at': None, 'execution_started': False,
    'activity_added_seconds': 21600, 'calendar_hours_from_receipt': 48,
    'no_expand_after_seconds': 16200, 'save_only_after_seconds': 20400, 'save_reserve_seconds': 1200,
    'runtime_holding_added_seconds': 7200, 'offline_added_seconds': 10800,
    'offline_no_new_repairs_after_seconds': 9000, 'cumulative_offline_forward_cap': 19812,
    'old_offline_caps_7200_9000_and_overruns_preserved': True,
    'prior_actual_observed': observed['cumulative'], 'baseline_counts': expected_counts,
    'new_real_roots_max': 4, 'S_total_roots_cap': 22, 'TASK_total_roots_cap': 23, 'Q_reserved_roots': 1,
    'root_business_seconds': 2100, 'root_cleanup_seconds': 300,
    'new_counts_caps': {'roots': 4, 'pg_starts': 8, 'api_starts': 6, 'browser_starts': 3,
        'frontend_builds': 2, 'preview_creates': 2, 'preview_starts': 2,
        'pg_create_attempts': 1, 'pg_objects': 1, 'volumes': 1},
    'cumulative_counts_caps': {**expected_counts, 'roots': 22, 'pg_starts': 41, 'api_starts': 28,
        'browser_starts': 14, 'frontend_builds': 9, 'native_windows': 160, 'http': 3000,
        'preview_creates': 3, 'preview_starts': 3, 'pg_create_attempts': 7, 'pg_objects': 7, 'volumes': 7},
    'conditional_only_target': {'slot': 'r02-success-02', 'name': 'retrolume-step018-syn-r02-success-02',
        'volume': 'retrolume-step018-syn-r02-success-02-data', 'host': '127.0.0.1', 'port': 15487,
        'database': 'step018_r02_success_02',
        'gate': 'required new normal tombstones absent from original sealed plan; only one same-package current-overlay derivative, no retry pool'},
    'reuse_successful_restore_without_repeat_for_confirmation': True,
    'preview_diagnosis_max_seconds': 900, 'PDF_diagnosis_max_seconds': 600,
    'low_memory_stages_MiB': {'base': 512, 'pg': 512, 'api': 512, 'browser': 768, 'second_pg': 768, 'preview': 1024},
    'pressure_MiB': 256, 'pressure_consecutive': 2, 'pressure_sampling_seconds': 2,
    'production_preview_equivalent_hotspot_changes_only': True, 'preview_deadlines_and_security_unchanged': True,
    'git_write_exception': 'local origin remote configuration only, exact approved URL; no index/HEAD/commit/push/upload',
    'remote_url': 'https://github.com/shspic/RetroLume-agent.git',
    'Q_enabled': False, 'provider_calls_cap': 0, 'actual_fee_microunits_cap': 0,
}
save('continuation-permit.json', permit)
save('repository-state.json', {
    'at': AT, 'source': 'this-turn GitHub get_repo and branches GET; local read-only Git calls',
    'repository_url': 'https://github.com/shspic/RetroLume-agent', 'id': '1421491262',
    'owner': 'shspic', 'visibility': 'public', 'default_branch': 'main', 'branches': [],
    'local_branch': 'main', 'local_HEAD': '45951501d2741630a229762d6b2d3f4b34d7f702',
    'local_last_commit_date': '2026-09-23 20:53:42 +0800', 'remotes': [],
    'porcelain_summary_entries': 648, 'porcelain_status_counts': {' M': 23, ' D': 527, '??': 98},
    'untracked_entries_are_summary_paths_not_full_recursive_file_count': True,
    'main_git_or_remote_mutations': 0, 'execution_remote_configuration_is_future_not_done': True,
    'public_upload_permission_in_this_card': False,
})
save('input-manifest.json', {
    'at': AT, 'rules': rules,
    'protected_read_inputs': [{'path': str(ROOT / rel), **value} for rel, value in protected.items()],
    'shared_inputs_before_maintenance': [{'path': str(path), **ident(backup / path.name),
        'raw_preserved_at': str(backup / path.name)} for path in managed],
    'scope': 'read/hash/JSON/source-path review only; no product code import, compile, DB, Docker, HTTP server or browser execution',
})

work = f'''# TASK117/R111 — S04部分回收与S05剩余集成许可

{AT}。实际S04报告48950字节/67f3656f…15bc4、155源身份和4bundle、账/索引/停止绑定匹配；原40682字节S03后缀保持。主控分层采纳同包R02恢复成功、最终bundle7真实加载、三种COMMIT丢回包后原键GET及合法无后继理由，不重做两域/重开或为确认性能再恢复。实现仍为部分候选，证据分层有效；完整S/STEP018不通过，稳定点前不提前全面独审。

同617行原包在完整控制根上22.454秒verified/sealed，target634aa034-51f6-4510-b075-38cb005481d8，31表codec/512维/007/预留/删除覆盖、只读拒写和撤loader有真实层证据。新ControlHub同身份+完整字节摘要复用投影为候选，不冒取消/完整性已独审。后续normal新删除可能确定性使原plan_changed；S05只在真实新tombstone差异下准一次success-02当前overlay派生，不是重复确认恢复或失败重试池。

原preview首次reaper_not_ready，t0后3.515秒失败、ready文件约晚0.992秒；代码显示3秒门包含reserve/登记/gate等待。具体慢调用未证，先测明因果，再原合同内等价修补，不增加3/4.5/8秒门或总D。旧首次StopProof不确认与新正常恢复/当前不存在分层；原正常恢复器核齐never_started和owned才能解除相关阻断，不手清账/selector。

剩余为Java单范围、独立delete/current/late与最终U部分、PDF实际HTTP、固定preview ACK/PNG/停止、新reader R01/R02应用查看及README。单source控制根不能先readonly再回normal/换目标；R01定位为真实旧库+当前只读reader兼容实例，R02为源控制根唯一正常activate；不得捏造selector。若构造或安全合同需实质扩大，停依赖部分交具体差异，其它完整推进。

原停止原件e55654b0…fcf45支持2026-10-16 08:50时点六CID非运行/Pid0、已登记birth/进程清单/端口；不是主控现场实时监控。S04离线2782.296/2400超382.296，累计offline9011.637117/9000超11.637117，旧所有超额/漏采留存，执行控制不通过。root18/active_root空；PGcreate/object/volume6、PGstart33/API22/Browser11/build7/Native136/HTTP2068、preview1/provider0/fee0。

同号S05原A+完整卡已保存待人工转交，未登记新执行，不创建TASK118。新增活动21600/48h含1200收尾、持有7200/offline10800及累计前向19812，离线9000后留1800保存；新完整根4/S累计22/TASK23保Q1，PG新增8至41/API6至28/Browser3至14/build2至9，Native160/HTTP3000保持，preview新增各2至3。最多一个条件success-02，PGcreate/对象/卷最多7；没有新删除覆盖差异就保持6。低内存/原隔离/凭据/模板和费用门不放松。

用户指定GitHub仓库已通过只读接口确认公开、空branches，owner shspic/ID1421491262/default main；本地尚无remote，HEAD仍45951501…7f702。S05给唯一Git写例外是关联精确origin和生成公开候选清单，不改index/HEAD、不commit/push或上传证据/私密。此为用户新明确目标的接入安排，不能声称主控已关联或已同步。

证据/前向许可/输入/旧共享备份及保存证明位于DocuN/evidence/TASK-117/orchestration-s05-20261016。原执行账、报告、产品和原件由工程保护。Q仍0，未来80次/20元条件许可不消费，STEP019/020/M1/全项目未通过。主控只读核证/共享文档维护，产品/测试/build/SQL/Docker/Browser/供应商/费用/Git写0。

## 以下为原裁定历史

'''
arch = f'''# 架构动态文档

文档v1.38，2026-10-16，Asia/Shanghai。需求v1.3、执行动态v2.65、task_model/07。以下v1.37历史原字节保留，116采用包不变。

## STEP018当前候选恢复、最终界面与预览阻断

{AT}。117/S04同617行R02包已实际verified/sealed，31表逐列codec回读、512维float32/007/预留/删除覆盖及真实只读角色成立，原目标634aa034…481d8保留；新ControlHub读取等价缓存仍候选，旧数据/取消/CAS/64MiB/组件30秒不变，未独审。正常新增删除若令既有plan覆盖过时，必须按当前overlay处理，不能将旧sealed视为新历史的已验证副本。

bundle7主JS58a87abf…115e8已实际加载；输入身份就绪门、面试持久目标门、三种COMMIT丢回包后的原键GET及两独立实例无后继理由有定向证据。旧两域和同normal应用重开证据继承，不冒全部最终U或真实Q语义。

真实HTML父成果/artifact已生成，首次preview救援就绪失败，原StopProof未确认；3秒门从预扣前起算并包含前序成本。S05只准有据等价性能/owned恢复接线，保持t0/各deadline/StopProof/renderer/签票/Job/EOF/隔离，变化候选最终集中独审。新的当前物理不存在不退款或回写首次成功。

P02/P03当前只读reader应用层仍待补；同一source控制根一旦restored_readonly不能回normal或切第二target，先完成normal，再R01兼容reader与唯一R02正式切换。GitHub公开仓库shspic/RetroLume-agent现纳版本交付目标；本轮仅准备精确origin关联与公开范围，未同步外部。完整S/Q/发布未通过。

## 以下为v1.37及更早历史

'''
state = f'''# 执行动态文档

文档v2.65，2026-10-16，Asia/Shanghai。唯一总状态账；需求v1.3、架构v1.38、task_model/07。以下v2.64历史原字节保留。

## TASK117 S04部分已核证，S05剩余收口与GitHub接入待人工转交

{AT}。用户真实带回117/R111/S04，报告48950字节/67f3656f…15bc4、155源及4bundle和账/索引/停止身份匹配，旧S03后缀完整。同包R02恢复22.454秒verified/sealed、31表/readonly角色、最终bundle7三类回包丢失原键GET和目标就绪/无后继理由分层采纳，不重复已足两链/重开/恢复确认；完整S仍未完成。

当前真实预算phase S04_returned_partial、active_root为空；roots18，PGcreate/object/volume6、PGstart33/API22/Browser11/build7/Native136/HTTP2068、preview create/start1、provider/fee0。累计活动90806.1720744/持有24821.501/offline9011.637117，S04离线超382.296、累计旧9000超11.637117和旧全部失败/漏采/超限不追认。S04段旧status active不改变已交回事实，由工程追加新段和分层纠正，不清旧账。

停止原件e55654b0…fcf45绑定08:50时点六CID/Pid0、进程birth/清单及端口，不冒主控实时现场。原preview reaper_not_ready/首次StopProof不确认仍在；实际t0后3.515秒失败，ready文件晚约0.992秒，源代码3秒门包含预扣/登记/gate成本，具体慢调用待定量。先正常恢复旧未确认owned，再最小等价性能修补，不能延长固定deadline或清registry绕过。

同号S05完整卡已保存待人工转交原A+工程窗，未登记接收或执行，无TASK118。合并Java单范围、独立delete/current/late、剩余最终U/PDF/preview/两profile只读查看/README；未变证据直接继承，稳定S才集中隔离审计。normal新删除可能使旧R02 plan_changed，只有真实差异才准一次success-02派生；否则复用success-01。单selector只做一次正常R02切换，R01隔离真实只读reader兼容，不回normal或伪造selector。

S05新增活动21600/48h含1200收尾、持有7200/offline10800，累计offline前向19812且旧cap/超额留史；离线9000后只留收口，定期计时不等根尾。新完整根4/S总22/TASK23保Q1；PG新增8/41、API6/28、Browser3/14、build2/9，Native160/HTTP3000不加，preview新增各2/总3，条件PGcreate/对象/卷各最多7。低内存512/768/1024MiB和两次低于256自动自有清场/其它安全边界不变。

用户新增指定GitHub https://github.com/shspic/RetroLume-agent，已只读确认公开/空branches/默认main；本地remote空、HEAD45951501…7f702、23修改/527删除/98未跟踪汇总。原批准归档不恢复。当前卡仅授权精确origin关联与可公开文件范围准备，不commit/push/上传证据和私密；不能称仓库已经同步。版本发布后续仍需绑定实际审计候选和具体范围。

本轮主控产品/测试/build/SQL/Docker/API/Browser/真实模型/费用/Git写0，只读GitHub及本地Git核对完成。输入/许可/备份/保存证明在DocuN/evidence/TASK-117/orchestration-s05-20261016。Q/80次20元条件门仍未启，STEP018/019/020/M1/项目未验收。CHG1448—1454，下一1455。

## 以下为v2.64及更早历史

'''
outputs = {
    CARD: (OUT / 'continuation.md').read_bytes(),
    WORK: work.encode('utf-8') + before[WORK],
    ARCH: arch.encode('utf-8') + before[ARCH],
    STATE: state.encode('utf-8') + before[STATE],
}
assert b'\xef\xbf\xbd' not in outputs[CARD]
for prefix in (work, arch, state):
    assert '*' not in prefix and '|' not in prefix
entries = [
    ('DocuN/evidence/TASK-117/orchestration-s05-20261016/received.json', 'S04真实成果分层核证、155源与4bundle/旧报告后缀、六CID旧停止及原预览未确认边界。'),
    ('DocuN/tasks/TASK-117.md', '同号S05完整合并合同，因果诊断/正常恢复/剩余集成/只读路线及精确Git origin例外。'),
    ('DocuN/results/TASK-117-work-decision.md', '部分采纳、S05前向预算和条件删除覆盖派生，不重做已足证据，不签完整S。'),
    ('DocuS/架构动态文档.MD', 'v1.38登记真实R02成功、最终bundle7/理由、预览时序与只读切换边界及仓库目标。'),
    ('DocuS/执行动态文档.MD', 'v2.65唯一状态账，S04回收/S05待转交、旧超额、实际仓库状态及未启用Q。'),
    ('DocuN/evidence/TASK-117/orchestration-s05-20261016/before-documents', '旧五份共享文件原字节、输入/许可及GitHub只读身份保存。'),
    ('DocuN/evidence/TASK-117/orchestration-s05-20261016/save-proof.json', '保存复读/历史/源与执行账保护；主控没有产品或Git写入。'),
]
tail = ''.join(f'\r\n- CHG-{1448+i}，{AT}，Codex编排Agent，{path}。{detail}\r\n'
               for i, (path, detail) in enumerate(entries))
outputs[CHANGE] = before[CHANGE] + tail.encode('utf-8')
for path in managed:
    assert path.read_bytes() == before[path]
for path, raw in outputs.items():
    path.write_bytes(raw)
assert CARD.read_bytes() == (OUT / 'continuation.md').read_bytes()
for path in (WORK, ARCH, STATE):
    assert path.read_bytes().endswith(before[path])
assert CHANGE.read_bytes().startswith(before[CHANGE])
assert [int(v) for v in re.findall(r'^- CHG-(\d+)', CHANGE.read_text(encoding='utf-8-sig'), re.M)] == numbers + list(range(1448, 1455))
for path in managed:
    assert (backup / path.name).read_bytes() == before[path]
    assert '\ufffd' not in path.read_text(encoding='utf-8-sig')
for rel, value in protected.items():
    assert ident(ROOT / rel) == value, rel
for entry in rules:
    assert ident(Path(entry['absolute_path']))['sha256'] == entry['sha256']
save('save-proof.json', {
    'at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
    'documents': [{'path': str(path), **ident(path)} for path in (*managed, OUT / 'continuation.md')],
    'before_documents_raw_preserved': True, 'old_history_suffixes_unchanged': True,
    'source_entries_match': 155, 'bundle_assets_match': 4, 'locked_rules_match': 7,
    'protected_identities_unchanged': len(protected), 'CHG': list(range(1448, 1455)),
    'product_or_execution_ledger_or_result_or_git_written_by_main': False,
    'main_runtime_resources_created_started_stopped': 0, 'dispatch_confirmed': False,
    'Q_enabled': False, 'remote_configuration_already_done': False,
})
print(json.dumps({'status': 'SAVED_AND_READ_BACK', 'TASK': '117', 'R': '111',
    'permit': 'S05', 'card': str(CARD), 'state': 'v2.65', 'architecture': 'v1.38',
    'last_CHG': 1454, 'source_matches': 155, 'product_execution': 0,
    'GitHub_recorded_origin_execution_pending': True}, ensure_ascii=False))
