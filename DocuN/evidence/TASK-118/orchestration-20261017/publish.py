"""Verify frozen file/evidence identities and publish an independent-audit contract."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re

R = Path('D:/shspic/project_NO3_RetroLume-agent')
O = Path(__file__).resolve().parent
E = R / 'DocuN/evidence/TASK-117/execution'
C = E / 'continuation-05'
CARD = R / 'DocuN/tasks/TASK-118.md'
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


assert not CARD.exists()
managed = (WORK, ARCH, STATE, CHANGE)
before = {p: p.read_bytes() for p in managed}
assert STATE.read_text(encoding='utf-8-sig').splitlines()[2].startswith('文档v2.66，')
assert ARCH.read_text(encoding='utf-8-sig').splitlines()[2].startswith('文档v1.39，')
numbers = [int(x) for x in re.findall(r'^- CHG-(\d+)', CHANGE.read_text(encoding='utf-8-sig'), re.M)]
assert numbers[-1] == 1462
rules = read(R / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
assert len(rules) == 7
for x in rules:
    assert ident(Path(x['absolute_path']))['sha256'] == x['sha256']
result = R / 'DocuN/results/TASK-117-result.md'
result_identity = {'exists': True, 'bytes': 79709,
                   'sha256': 'b596ab87ae3facc605dab65acbf9c708c784c11b1f8581b75ddc6611ad802ac9'}
assert ident(result) == result_identity
assert hashlib.sha256(result.read_bytes()[-63687:]).hexdigest() == '4ba3402549f8d7a9c5a9cb4c6e26825ae174aae5bbdcd5740294e95ed73bbe00'
manifest = read(C / 'final-source-manifest.json')
assert len(manifest['entries']) == 163
for x in manifest['entries']:
    assert ident(R / x['path']) == x['post'], x['path']
binding = read(C / 'final-binding.json')
assert len(binding['entries']) == 27
for x in binding['entries']:
    assert ident(Path(x['path']))['sha256'] == x['sha256'], x['path']
assert ident(C / 'final-binding.json')['sha256'] == read(C / 'final-readback.json')['binding_sha256']
bundle = read(C / 'final-bundle-7-binding.json')
assert len(bundle['files']) == 4
for x in bundle['files']:
    assert ident(R / x['path']) == {'exists': True, 'bytes': x['bytes'], 'sha256': x['sha256']}
assert ident(R / 'backend/app/data_exit/config.py')['sha256'] == 'f3582c2bca0db6dadc8fd5cfb3dfb9caa25b951848eb046861f04a21a856e38f'
budget = read(E / 'budget.json')
assert budget['phase'] == 'S06_returned_engineering_candidate' and budget['active_root'] is None
counts = {'roots': 24, 'pg_create_attempts': 6, 'pg_objects': 6, 'volumes': 6,
          'pg_starts': 46, 'api_starts': 33, 'browser_starts': 16, 'frontend_builds': 7,
          'native_windows': 140, 'preview_creates': 2, 'preview_starts': 2, 'http': 2324,
          'provider_calls': 0, 'actual_fee_microunits': 0}
assert budget['counts'] == counts
stop_binding = read(C / 'final-resource-stop-binding.json')
stop_path = Path(stop_binding['path'])
assert ident(stop_path)['sha256'] == stop_binding['sha256']
stop = read(stop_path)
assert stop['all_stopped'] and len(stop['pg']) == 6 and not stop['listeners']
assert all(not p['running'] and p['pid'] == 0 for p in stop['pg'])
preview = read(C / 'L10/supervisor-result.json')
proof = preview['proof']
assert preview['confirmed'] and proof['tree_confirmation'] == 'private_pid_init_terminated'
assert proof['pipe_observation']['stdout_eof'] and proof['pipe_observation']['stderr_eof']
assert proof['owned_reaper_ended']
assert proof['reaper_windows_job']['ActiveProcesses'] == 0
assert proof['supervisor_cli_windows_job']['ActiveProcesses'] == 0
settled = read(C / 'L10/settled-status.json')
assert settled['elapsed_seconds'] == 11 and settled['reserved_seconds'] == 0
assert settled['settled_seconds'] == 71 and settled['starts_used'] == 2
pdf = read(C / 'PDF-HTTP-bounded-probe.json')
assert pdf['parse_entered'] and pdf['result'] == 'success' and pdf['physical_pages'] == 2
assert pdf['input_sha256'] == 'ca68cb54cfdb651e6a2d4048128a1aa5d3613a83a3192bb1321df5f2ddb8fcc4'
assert pdf['job_result']['exit_code'] == 0
pdf_confirm = read(C / 'PDF-two-page-confirmed.json')
assert pdf_confirm['content_GET']['review_status'] == 'confirmed' and pdf_confirm['content_GET']['query_ready']
deleted = read(C / 'X02-current-physical-deletion.json')
assert deleted['SQL']['body_rows'] == [[0]] and deleted['all_revision_bodies_removed']
assert deleted['exact_manifest_hash_verified'] and deleted['immutable_versions_choices_dependencies_retained']
readonly = read(C / 'R02-formal-readonly-reopen.json')
assert readonly['selector']['target_id'] == '634aa034-51f6-4510-b075-38cb005481d8'
assert readonly['selector']['generation'] == 1 and readonly['fence']['state'] == 'frozen'
assert readonly['source_PG_stopped'] and readonly['normal_config_reopen_no_source_fallback']
assert readonly['same_original_control_root'] and not readonly['new_restore_or_target']
assert readonly['caps']['format'] == 'data_exit.v1.r02'
shared = read(C / 'shared-global-budget-PG-lock.json')
assert shared['read_only_transactions'] and shared['target_SQL_writes'] == 0
assert shared['Q_roster_rows_created'] == 0 and shared['real_provider_calls'] == 0
assert shared['budget'] == {'requests': 80, 'cost': 20000000}
assert sum(x['admitted'] for x in shared['results']) == 1
assert len({x['backend_pid'] for x in shared['locks']}) == 2
observed = read(C / 'final-budget-observed.json')

contract_paths = [R / 'AGENTS.md', R / 'DocuS/最终需求文档.MD',
    R / 'DocuN/evidence/TASK-116/design/integration-contract.md',
    R / 'DocuN/evidence/TASK-116/design/acceptance-contract.md',
    R / 'DocuN/evidence/TASK-116/design/sample-inputs.json',
    R / 'DocuN/evidence/TASK-116/design/adoption-package.md',
    R / 'DocuN/evidence/TASK-117/orchestration-20261014/adoption-receipt.json',
    R / 'DocuN/evidence/TASK-117/orchestration-20261014/resource-profile.json',
    R / 'DocuN/evidence/TASK-117/orchestration-s06-20261016/X02-contract-correction.md',
    R / 'DocuN/evidence/TASK-117/orchestration-s06-20261016/X02-source-basis.json',
    R / 'DocuN/tasks/TASK-117.md']
task117_area = R / 'DocuN/evidence/TASK-117'
contract_paths += sorted(task117_area.glob('orchestration*/continuation-permit.json'))
contract_paths += sorted(task117_area.glob('orchestration*/before-documents/TASK-117.md'))
contract_paths = list(dict.fromkeys(contract_paths))
assert all(p.is_file() for p in contract_paths)
diff_paths = [E / 'changes.json', E / 'final-changes-limited.diff']
for stage in ['continuation-01', 'continuation-02', 'continuation-03', 'continuation-04', 'continuation-05']:
    for name in ['changes.json', 'source-changes.diff']:
        p = E / stage / name
        if p.is_file(): diff_paths.append(p)
raw_paths = [C / name for name in [
    'L10/input-acks.json', 'L10/actual-frame.png', 'L10/supervisor-result.json', 'L10/stage-times.json',
    'L10/settled-status.json', 'PDF-diagnostic-admission.json', 'pdf_probe.py', 'PDF-HTTP-bounded-probe.json',
    'PDF-two-page-confirmed.json', 'X02-current-physical-deletion.json', 'semantic-slot-race.json',
    'inflight-goal-invalidation.json', 'R02-selector-increment.json', 'R02-current-overlay-and-owned.json',
    'R02-one-PG-switch-stage.json', 'R02-formal-readonly-reopen.json', 'R01-final-browser-verified.json',
    'reader-host-proof.json', 'shared-global-budget-concurrency.json', 'shared-global-budget-PG-lock.json',
    'shared_gate_check.py', 'root24_global_gate.py', 'S-case-closure.json', 'final-binding.json', 'final-readback.json',
    'final-resource-stop-binding.json', 'final-fixture-manifest.json', 'final-budget-observed.json',
    'historical-ledger-preservation.json']]
assert all(p.is_file() for p in raw_paths)
extra = [result, E / 'budget.json', E / 'events.jsonl', E / 'case-index.json', stop_path,
    R / '.git/HEAD', R / '.git/config', R / '.git/index',
    R / 'backend/app/pdf_import/supervisor.py', R / 'backend/app/pdf_import/worker.py',
    R / 'backend/app/pdf_import/_windows_job.py', R / 'backend/app/preview/production_supervisor.py',
    R / 'backend/app/preview/production_reaper.py', R / 'backend/app/data_exit/control.py']
protected_paths = list(dict.fromkeys([R / x['path'] for x in manifest['entries']] + contract_paths + diff_paths + raw_paths + extra + [Path(x['path']) for x in binding['entries']]))
assert not any(p in managed or p == CARD for p in protected_paths)
protected = {str(p.relative_to(R)): ident(p) for p in protected_paths}
backup = O / 'before-documents'
backup.mkdir(exist_ok=False)
for p in managed:
    (backup / p.name).write_bytes(before[p])

save('received-117-s06.json', {
    'at': AT, 'TASK': 'TASK-117', 'R': 'R-111', 'received_stage': 'S06',
    'result': result_identity, 'old_63687_raw_suffix_preserved': True,
    'source_entries_match': 163, 'bundle_assets_match': 4, 'bound_evidence_entries_match': 27,
    'seven_locked_rules_match': True,
    'behavior_evidence_verified': {
        'preview_new_StopProof_confirmed': True, 'preview_CID': proof['cid'],
        'private_PID_init_stopped': True, 'dual_EOF': True, 'SUP_REAP_ActiveProcesses': [0, 0],
        'new_window_elapsed_seconds': 11, 'total_settled_seconds_including_old_failure': 71, 'reserved_seconds': 0,
        'same_frozen_PDF_HTTP_and_two_page_confirmation': True, 'memory_bodies': 0,
        'R01_actual_final_browser': True, 'R02_same_sealed_target_normal_activation_and_reopen': True,
        'selector_generation': 1, 'source_frozen_stopped': True,
        'shared_budget_scope': 'real PG advisory locks; in-memory synthetic manifest/grant/sum/budget; not actual outbound admission'},
    'implementation_axis': 'engineering_closeout_candidate_received',
    'evidence_axis': 'ready_for_concentrated_independent_review_with_explicit_layer_limits',
    'execution_control_axis': 'S06_current_limits_observed; historical overruns/unknowns preserved for independent assessment',
    'budget_observed': observed,
    'stop_binding': {'path': str(stop_path), **ident(stop_path), 'sample': stop['sample'],
        'six_pg_nonrunning_pid_zero': True, 'listeners': [], 'main_live_runtime_probe': False},
    'independent_acceptance_or_Q_or_STEP018_complete': False,
    'main_product_execution_or_Git_mutations': 0,
})
save('contract-index.json', {
    'at': AT, 'purpose': 'original scope/authority/permissions; implementation evaluations are not audit evidence',
    'entries': [{'path': str(p), **ident(p)} for p in contract_paths],
    'read_original_contract_sections_only_in_old_cards': True,
    'implementation_result_path': str(result), 'implementation_result_read_rule': 'hash bytes only; do not read self-evaluation or chat',
})
save('audit-inputs.json', {
    'at': AT, 'TASK': 'TASK-118', 'R': 'R-112', 'rules': rules,
    'frozen_source_manifest': {'path': str(C / 'final-source-manifest.json'), **ident(C / 'final-source-manifest.json')},
    'frozen_sources': manifest['entries'],
    'bundle': bundle['files'],
    'baseline_and_stage_diff_index': [{'path': str(p), **ident(p)} for p in diff_paths],
    'critical_raw_evidence': [{'path': str(p), **ident(p)} for p in raw_paths],
    'protected_inputs': [{'path': str(R / rel), **value} for rel, value in protected.items()],
    'implementation_report_is_hash_only': str(result),
    'main_product_or_test_execution': 0, 'live_runtime_approved_for_audit': False,
})
save('audit-permit.json', {
    'at': AT, 'permit': 'TASK-118-STEP018-INDEPENDENT-AUDIT-20261017', 'TASK': 'TASK-118', 'R': 'R-112',
    'parent_TASK': 'TASK-117', 'resource': 'A+', 'window': 'new isolated independent audit conversation',
    'dispatch_confirmed': False, 'actual_received_at': None, 'execution_started': False,
    'activity_seconds': 14400, 'calendar_hours_from_actual_receipt': 48,
    'no_new_audit_family_after_seconds': 10800, 'save_only_after_seconds': 13200, 'save_reserve_seconds': 1200,
    'metadata_script_single_batch_seconds': 60, 'metadata_script_cumulative_process_seconds': 1800,
    'runtime_roots': 0, 'SQL_PG_Docker_WindowsJob_API_Browser_compile_unittest_provider_or_product_execution': 0,
    'network_requests': 0, 'actual_fee_microunits': 0, 'Git_mutations': 0,
    'allowed_writes': [str(R / 'DocuN/evidence/TASK-118/audit'), str(R / 'DocuN/results/TASK-118-result.md')],
    'TASK117_runtime_permission_returned_not_inherited': True,
    'TASK117_baseline_counts': counts, 'historical_failures_budgets_overruns_not_reset': True,
    'Q_enabled': False, 'source_currently_permanently_readonly': True,
})

work = f'''# TASK117/R111 — S06工程候选接收，交TASK118集中独审

{AT}。用户带回S06候选79709字节/b596ab87…802ac9，163源/4bundle/27项绑定与63687旧后缀匹配。接收工程收口候选及可审原件，不自代独审或STEP018通过；原117运行权已交回，未用根/次数不恢复。下一新TASK118/R112为隔离A+集中审计，待人工转交。

原X02更正按三个效果核：真实清单hash/版本1和2 hash及bytes、body_rows0/GET null、版本和6旧选择身份保留，未新增delete或墓碑。L10新真实ACK及seq2对应.5的PNG、原private PID/init结束、双EOF/SUP与REAP Job0、owned收敛和正常StopProof confirmed；新窗11秒/R0、含旧失败60的累计71/starts2。旧首次UNCONFIRMED与后续never_started恢复保留，不能回写首次成功。

同942字节PDF原hash的有限诊断直接HTTP成功，真实Job/worker exit0、2物理页/人工确认/content回读成立；没有为原两次422追造唯一旧因。semantic-slot/goal失效、R01最终U及R02唯一正式切换/正常只读重开取得新证。原success01/617行包复用无新装载/目标，selector generation1/activation55e4e1dc…870e，source frozen/stopped，不能再用于正常Q写入。共享总门证据仅真实PG advisory锁+内存manifest/grant/sum/预算，不是实际写账准入通过，待独审和Q前置分别界定。

产品最终config.py f3582c2b…6e38f仅修复已验证target profile在caps.format的R02只读重开投影，API33和真实Browser16绑定；前端bundle7四项原字节不变，R01在该小修前的适用性按实际差异审。完整117实际变化含014/embedding/检索/两域/预算/恢复codec/日志缓存/owned/reader，不只审最后一行或只看S06摘要。

S06实际roots22/23/24，累计roots24/PGcreate对象卷6/PGstart46/API33/Browser16/build7/Native140/HTTP2324/preview各2/provider费用0，active_root空、phase已交回。活动12244.341136/14400、持有139.233/5400、离线进程保守257.6443102/1800；旧连续无资源/中断保守上界及S01—S05失败/超额/漏采保持。停止hash44f5f77d…a3a6f支持2026-10-16T15:45:05Z六CID非运行/Pid0和端口/birth；本轮主控未实时查询Docker。

原工程窗保持停止/源与证据只读冻结。TASK118只在自身audit/及结果写入，14400/48h含1200保存、标准库metadata进程1800/单批60秒，产品/PG/Docker/Job/API/Browser/真实外发/费用/Git写均0。审计输入先原始目标/合同/实际diff/源，再原件，禁止实施者结果/聊天/推理作为独立判断；三轴各自结论，缺陷合并回原117而不是逐小改审。

Q80次/20元条件批准仍未启，官方当期条件/正常本地账号配置/实际总账组合证/新正常合成运行环境及主控回执是后续Q前置，不把已readonly源开写。GitHub origin已关联但无新commit/push，原公开候选不等于可发布。STEP018/019/020/M1/项目未通过；S审计充分后主控再安排Q及整体交付，不预发依赖未满足的卡。

证据、输入、许可、旧共享和保存证明在DocuN/evidence/TASK-118/orchestration-20261017。主控只读核证/维护共享文档，没有产品/测试/build/SQL/Docker/API/Browser/provider/费用/Git写，没有代做独审。

## 以下为原裁定历史

'''
arch = f'''# 架构动态文档

文档v1.40，2026-10-17，Asia/Shanghai。需求v1.3、执行动态v2.67、task_model/07。以下v1.39历史原字节保留，116采用包不扩大。

## STEP018完整合成候选形成，集中独审前的实际边界

{AT}。117/S06补齐新固定预览ACK/PNG/原StopProof、private PID/init/双EOF/双Job0与11秒正常结算；t0/3/4.5/8/D未改，reaper约1.484秒/ready约6.047秒。原失败恢复/60秒保守计账与首次UNCONFIRMED保持。相同PDF经原受限HTTP/worker/人工两页确认及回读，原422旧因未追溯，不写已证旧根因。

记忆X02按已有revise/revoke/purge三个效果完成实际正文0行/GET null/精确清单/历史身份保留核证；无新动作/模型/迁移。原R01 sealed-reader最终U已走到；原R02 sealed success01复用，normal源经真实drain/freeze、停止source、启target、唯一selector generation1并正常只读重开，保永久只读/无fallback。最终config.py f3582c2b…6e38f的target schema_profile投影由API33/Browser16绑定，bundle7未改。

新semantic-slot/goal/selector晚到证据补足，旧两域/重开/当前UI按实际变更合并继承。跨provider共享总门本轮只证明真实PG advisory锁串行化+内存合成预算，不冒实际持久总预扣的端到端证；真实供应商及Q配置仍关闭。新Q运行不能直接复用已frozen的源写身份，需要后续明确正常合成环境和许可。

当前是可集中独审的完整S工程候选，未签S最终、Q或STEP。TASK118/R112对117全实际差异及受影响边界独立审计，既有G模块充分未变证据继续复用。Windows/Compose与隔离readonly为本切片边界，不外推Linux全应用/Nginx/公开发布。GitHub已关联、未提交上传，源/原件冻结。

## 以下为v1.39及更早历史

'''
state = f'''# 执行动态文档

文档v2.67，2026-10-17，Asia/Shanghai。唯一总状态账；需求v1.3、架构v1.40、task_model/07。以下v2.66历史原字节保留。

## TASK117 S06工程候选已接收，TASK118/R112集中独审待人工转交

{AT}。S06报告79709字节/b596ab87…802ac9，163源/4bundle/27绑定及63687原后缀匹配。接收完整S工程候选，原117已返回并停止，未签独审/STEP018/Q。X02实际body0/GET null/精确清单和历史身份、固定预览真实ACK/seq2 PNG/private PID/init/双EOF/双Job0/正常StopProof、同PDF真实HTTP两页人工确认、semantic-slot/goal/selector晚到、R01最终U和原R02正常唯一只读切换/重开有原件支持，已有两域/重开/回包GET不重做。

原success01/617行包直接复用，无新对象或success02，原source现frozen且永久readonly选择generation1/activation55e4e1dc…870e。最后config.py f3582c2b…6e38f的目标profile显示修补由API33/Browser16绑定，bundle7原字节不变。共享总门只有真实PG advisory锁+合成内存预算，不能当实际持久全局预扣已验；Q前置单列待审，不把无真实provider费用写成安全放行。

工程累计roots24/PGcreate对象卷6/PGstart46/API33/Browser16/build7/Native140/HTTP2324/preview各2/provider与费用0；S06 phase返回候选、active_root空。活动12244.341136/14400，持有139.233/5400，离线进程保守257.6443102/1800；旧所有连续无资源/中断unknown、失败/超额/漏采照留。停止hash44f5f77d…a3a6f绑定2026-10-16T15:45:05Z六CID stopped/Pid0、端口和原birth；主控未做现场Docker监控。新正常StopProof不回填旧首次失败或旧Job error2为历史0。

新TASK118/R112已正式占号并保存完整卡待人工转交A+新隔离审计窗，未登记接收或执行。原117源/证据/资产和账冻结，旧余根/次数不授权审计。集中审117 S01—S06实际变化、原始证据和执行控制，输入只原始合同/源/diff/原件，不实施者完整聊天/自评。产品动态/PG/Job/Docker/API/Browser/compile/unittest/模型/网络/费用/Git写额度0；新metadata进程1800/单批60、活动14400/48h含1200保存。待三轴独立结论再主控裁定；不逐小修改另做全面审计。

Q80次/20元原条件许可未启，官方当期条件、配置/共享账实证、正常合成Q环境和主控回执后续安排；不能把已冻结源重新开写。GitHub origin已关联但无新commit/push，候选公开清单仍待实际范围/敏感审查。STEP018/019/020/M1/项目未通过。输入/许可/旧共享/保存证明在DocuN/evidence/TASK-118/orchestration-20261017，主控产品/运行/测试/费用/Git写0。CHG1463—1470，下一1471。

## 以下为v2.66及更早历史

'''
for prefix in (work, arch, state):
    assert '*' not in prefix and '|' not in prefix
changes = [
    ('DocuN/evidence/TASK-118/orchestration-20261017/received-117-s06.json', 'S06工程候选/163源/4bundle/27绑定与关键真实层、预算停止核证，不代独审。'),
    ('DocuN/tasks/TASK-118.md', '新R112隔离A+集中独审完整合同，117全实际增量/三轴/Q门，零产品运行。'),
    ('DocuN/results/TASK-117-work-decision.md', '接收工程候选并冻结原窗/原运行权，交集中独审，旧失败和Q条件保持。'),
    ('DocuS/架构动态文档.MD', 'v1.40真实固定预览/PDF/readonly收口、目标profile补丁和共享总门证据边界。'),
    ('DocuS/执行动态文档.MD', 'v2.67唯一总账先占TASK118/R112，再保存卡转待人工，Q/项目不冒通过。'),
    ('DocuN/evidence/TASK-118/orchestration-20261017/audit-inputs.json', '原始合同index/冻结源与diff原件/独立读取约束/审计许可保存。'),
    ('DocuN/evidence/TASK-118/orchestration-20261017/before-documents', '四原共享完整字节备份，不覆工程报告/账/规则/产品。'),
    ('DocuN/evidence/TASK-118/orchestration-20261017/save-proof.json', '新卡/登记/读回/历史与全部受保护输入一致，未真实派发执行。'),
]
tail = ''.join(f'\r\n- CHG-{1463+i}，{AT}，Codex编排Agent，{path}。{detail}\r\n'
               for i, (path, detail) in enumerate(changes))
assert all(p.read_bytes() == before[p] for p in managed)
reservation = f'# 执行动态文档\n\n文档v2.67（登记处理中），2026-10-17，Asia/Shanghai。\n\n{AT}：正式占TASK118/R112，原117候选已回，审计卡尚待保存，未派发/执行。\n\n## 以下为v2.66原历史\n\n'.encode('utf-8') + before[STATE]
STATE.write_bytes(reservation)
assert STATE.read_bytes() == reservation and not CARD.exists()
registered_at = datetime.now(timezone(timedelta(hours=8))).isoformat()
CARD.write_bytes((O / 'task-contract.md').read_bytes())
WORK.write_bytes(work.encode('utf-8') + before[WORK])
ARCH.write_bytes(arch.encode('utf-8') + before[ARCH])
CHANGE.write_bytes(before[CHANGE] + tail.encode('utf-8'))
STATE.write_bytes(state.encode('utf-8') + before[STATE])
save('dispatch-registration.json', {'reserved_at': registered_at, 'TASK': 'TASK-118', 'R': 'R-112',
    'state_reservation_before_card_saved': True, 'card_saved': True, 'card_identity': ident(CARD),
    'current_scheduling_state': 'awaiting_manual_transfer', 'dispatch_confirmed': False, 'execution_started': False})
assert CARD.read_bytes() == (O / 'task-contract.md').read_bytes()
for p in (WORK, ARCH, STATE):
    assert p.read_bytes().endswith(before[p])
assert CHANGE.read_bytes().startswith(before[CHANGE])
assert [int(x) for x in re.findall(r'^- CHG-(\d+)', CHANGE.read_text(encoding='utf-8-sig'), re.M)] == numbers + list(range(1463, 1471))
for p in managed:
    assert (backup / p.name).read_bytes() == before[p]
for p in (*managed, CARD):
    assert '\ufffd' not in p.read_text(encoding='utf-8-sig')
for rel, expected in protected.items():
    assert ident(R / rel) == expected, rel
for x in rules:
    assert ident(Path(x['absolute_path']))['sha256'] == x['sha256']
save('save-proof.json', {
    'at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
    'documents': [{'path': str(p), **ident(p)} for p in (*managed, CARD, O / 'task-contract.md')],
    'old_shared_raw_suffixes_preserved': True, 'old_backups_exact': True,
    'source_entries_match': 163, 'bundle_assets_match': 4, 'bound_entries_match': 27,
    'rules_match': 7, 'protected_identities_unchanged': len(protected),
    'state_reserved_before_card_saved': True, 'scheduling_state': 'awaiting_manual_transfer',
    'dispatch_confirmed': False, 'Q_enabled': False, 'CHG': list(range(1463, 1471)),
    'main_product_or_tests_or_runtime_or_Git_writes': 0,
})
print(json.dumps({'status': 'SAVED_AND_READ_BACK', 'candidate_TASK': '117', 'audit_TASK': '118', 'R': '112',
    'card': str(CARD), 'state': 'v2.67', 'architecture': 'v1.40', 'last_CHG': 1470,
    'source_matches': 163, 'audit_runtime_authorized': 0, 'manual_transfer_pending': True}, ensure_ascii=False))
