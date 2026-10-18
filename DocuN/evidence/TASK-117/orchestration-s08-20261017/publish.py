"""S08编排核证和文档保存，仅用标准库，不执行产品。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import difflib
import json
import re

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
C = ROOT / 'DocuN/evidence/TASK-117/execution/continuation-06'
assert ROOT == Path('D:/shspic/project_NO3_RetroLume-agent').resolve()
assert not (HERE / 'save-proof.json').exists(), '已经保存，不重复发布'


def h(raw):
    return hashlib.sha256(raw).hexdigest()


def load(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def identity(p):
    if not p.is_file():
        return {'exists': False, 'bytes': 0, 'sha256': None}
    b = p.read_bytes()
    return {'exists': True, 'bytes': len(b), 'sha256': h(b)}


def verify(p, expected):
    actual = identity(p)
    assert actual['exists'] == expected.get('exists', True), str(p)
    if actual['exists']:
        assert actual['sha256'] == expected['sha256'], str(p)
        if 'bytes' in expected:
            assert actual['bytes'] == expected['bytes'], str(p)
    return {'path': str(p), **actual}


def put(p, raw, new=False):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('xb' if new else 'wb') as f:
        f.write(raw)
    assert p.read_bytes() == raw
    raw.decode('utf-8-sig')


def save_json(name, value):
    put(HERE / name, (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8'), True)


now = datetime.now(timezone(timedelta(hours=8))).isoformat()
rules = load(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
for rule in rules:
    assert h(Path(rule['absolute_path']).read_bytes()) == rule['sha256'], rule['absolute_path']

post = load(C / 'post-source-manifest.json')
source_checks, normalized_diff, changed = [], [], {}
for entry in post['files']:
    p = ROOT / entry['path']
    source_checks.append(verify(p, entry['post']))
    pre = entry['pre']
    if pre['exists']:
        pre_path = ROOT / pre['backup']
        verify(pre_path, pre)
    if entry['changed']:
        changed[entry['path']] = entry['post']
        a = pre_path.read_text(encoding='utf-8-sig').splitlines()
        b = p.read_text(encoding='utf-8-sig').splitlines()
        normalized_diff.extend(difflib.unified_diff(a, b, fromfile=entry['path'] + '@S07-pre', tofile=entry['path'] + '@S07-current', n=3, lineterm=''))
assert len(source_checks) == 15 and len(changed) == 6

baseline = load(ROOT / 'DocuN/evidence/TASK-117/execution/continuation-05/final-source-manifest.json')
current_sources = []
for entry in baseline['entries']:
    expected = changed.get(entry['path'], entry['post'])
    current_sources.append(verify(ROOT / entry['path'], expected))
assert len(current_sources) == 163

bundle = load(C / 'bundle-7-post.json')
bundle_checks = []
for entry in bundle['files']:
    bundle_checks.append(verify(ROOT / entry['source'], entry))
    verify(Path(entry['backup']), entry)
assert len(bundle_checks) == 4

binding = load(C / 'final-binding.json')
report = ROOT / 'DocuN/results/TASK-117-result.md'
report_check = verify(report, binding)
assert report_check['sha256'] == 'fc600e1381e44542fc933bdd294e471e2e1a5d4b70b979a5a2be708878993aab'
old_report = (C / 'before-result.md').read_bytes()
assert len(old_report) == 79709 and h(old_report) == 'b596ab87ae3facc605dab65acbf9c708c784c11b1f8581b75ddc6611ad802ac9'
assert report.read_bytes().endswith(old_report)
evidence_checks = [verify(Path(row['path']), row) for row in binding['evidence']]
audit = ROOT / 'DocuN/results/TASK-118-result.md'
verify(audit, {'sha256': 'dd0a5f1d2ddb2ffcd9a168496e4cca5b8292b7221977c76b8ff417f9ff0f21f1', 'bytes': 41590})

E = ROOT / 'DocuN/evidence/TASK-117/execution'
budget = load(E / 'budget.json')
before_budget = load(C / 'before-budget.json')
assert budget['phase'] == 'S07_returned_incomplete_activity_limit' and budget['active_root'] is None
assert budget['counts']['roots'] == 24 and budget['counts']['fixture_server_starts'] == 0
assert budget['segments'][:len(before_budget['segments'])] == before_budget['segments']
assert budget['roots'] == before_budget['roots']
assert budget['failures'][:len(before_budget['failures'])] == before_budget['failures']
old_events = (C / 'before-events.jsonl').read_bytes()
assert (E / 'events.jsonl').read_bytes().startswith(old_events)
timing = load(C / 'final-timing.json')
assert timing['activity_charged_through_full_report_readback_seconds'] == 30294.653691
assert timing['activity_overrun_through_readback_seconds'] == 8694.653691

state = ROOT / 'DocuS/执行动态文档.MD'
arch = ROOT / 'DocuS/架构动态文档.MD'
change = ROOT / 'DocuS/文档变更记录.MD'
work = ROOT / 'DocuN/results/TASK-117-work-decision.md'
card = ROOT / 'DocuN/tasks/TASK-117.md'
assert '文档v2.68' in state.read_text(encoding='utf-8-sig').splitlines()[2]
assert '文档v1.41' in arch.read_text(encoding='utf-8-sig').splitlines()[2]
assert max(map(int, re.findall(r'CHG-(\d+)', change.read_text(encoding='utf-8-sig')))) == 1478
before = {p: p.read_bytes() for p in [state, arch, change, work, card]}

old_card = before[card].decode('utf-8-sig')
requirements = old_card.split('## 四项一次修复的完成合同', 1)[1].split('## 写入范围与隔离', 1)[0]
scope = old_card.split('## 写入范围与隔离', 1)[1].split('## 新段前向预算、完整验证与自动停止', 1)[0]
scope = scope.replace('continuation-06/', 'continuation-07/').replace('79709', '88265').replace('s07_', 's08_').replace('step018-s07', 'step018-s08')
new_card = ((HERE / 'contract-head.md').read_text(encoding='utf-8') + '\n## 四项有效验收合同\n' + requirements + '\n## 写入范围与隔离\n' + scope + '\n' + (HERE / 'contract-tail.md').read_text(encoding='utf-8')).encode('utf-8')
assert '*' not in new_card.decode('utf-8')
for token in ['D01 / P1', 'D02 / P1', 'D03 / P2', 'D04 / P2', 'continuation-07/', 'S08', '不再以', '48小时', '3600']:
    assert token in new_card.decode('utf-8'), token

protected_paths = {Path(row['path']) for row in current_sources + source_checks + bundle_checks + evidence_checks}
protected_paths.update([report, audit, E / 'budget.json', E / 'events.jsonl', E / 'case-index.json',
                        C / 'post-source-manifest.json', C / 'final-binding.json', C / 'receipt.json',
                        C / 'control.py', C / 'as-run.json', C / 'before-result.md'])
protected = {p: identity(p) for p in protected_paths}

backup = HERE / 'before-documents'
backup.mkdir(exist_ok=False)
for p, raw in before.items():
    put(backup / p.name, raw, True)
put(HERE / 'task-contract.md', new_card, True)
put(HERE / 'S07-normalized-review.diff', ('\n'.join(normalized_diff) + '\n').encode('utf-8'), True)

received = {
    'at': now, 'task': 'TASK-117', 'R': 'R-111', 'stage': 'S07', 'report': report_check,
    'acceptance': '部分通过仅接收六初版及封存，不接受四项修复关闭；完整S不通过，Q冻结',
    'sources_15_match': source_checks, 'source_baseline_163_match_with_6_authorized_revisions': len(current_sources),
    'bundle_4_match_but_not_current_TSX': bundle_checks, 'binding_match': evidence_checks,
    'old_report_suffix_79709_match': True, 'old_segments_roots_failure_prefix_events_prefix_preserved': True,
    'S07_tests_typecheck_build_browser_controller_selfcheck': '全部NOT_RUN',
    'current_counts': budget['counts'], 'active_root': budget['active_root'], 'phase': budget['phase'],
    'failures': {'old': len(before_budget['failures']), 'now': len(budget['failures'])},
    'S07_activity_through_readback_seconds': 30294.653691, 'S07_activity_overrun_seconds': 8694.653691,
    'monotonic_domain': '不连续，当前mono低于保存起点，原因未知；旧UTC保守活动和metadata漏账保留',
    'S07_runtime_delta': 0, 'metadata_process_wall': 'unknown，不以受控验证0冒全部命令0',
    'stop_reference': 'S07无登记runtime，2026-10-17T09:35:07.8034845Z Get-Process/netstat18119有限观察；CIM不可用；原六CID仅沿旧时点原件',
    'main_live_product_or_process_queries': 0, 'main_tests_or_build_or_runtime': 0,
}
save_json('received-s07.json', received)
save_json('input-manifest.json', {'at': now, 'rules': rules, 'report': report_check,
                               'current_sources': current_sources, 'S07_files': source_checks,
                               'bundle': bundle_checks, 'critical_evidence': evidence_checks,
                               'old_card': {'path': str(backup / card.name), **identity(backup / card.name)},
                               'new_card': {'path': str(HERE / 'task-contract.md'), **identity(HERE / 'task-contract.md')}})
permit = {
    'id': 'TASK-117-STEP018-AUDIT-REPAIR-S08-20261017', 'issued_at': now,
    'task': 'TASK-117', 'R': 'R-111', 'stage': 'S08', 'status': 'saved_pending_manual_transfer',
    'start': 'actual receipt first tool UTC plus current host monotonic identity, not issuance',
    'calendar_hours': 48, 'save_only_calendar_remaining_seconds': 1200,
    'activity_cap_seconds': None,
    'activity_policy': '新段不以跨平台中断UTC总差作额外活动硬门；可观测段/UTC上界/未知分别留账，旧S07超额不追改',
    'offline_child_process_wall_cap_seconds': 3600, 'runtime_holding_union_cap_seconds': 3600,
    'renew_unused_S07_counts_only': True, 'new_roots': 3, 'root_business_seconds': 1500, 'root_cleanup_seconds': 300,
    'baseline_counts': budget['counts'],
    'cumulative_caps': {**budget['counts'], 'roots': 27, 'browser_starts': 19, 'frontend_builds': 9, 'fixture_server_starts': 3, 'http': 2924},
    'additional_PG_Docker_SQL_product_API_Job_preview_provider_fee_Git': 0,
    'loopback': '127.0.0.1:18119', 'minimum_memory_MiB': {'fixture_server': 512, 'browser': 768, 'pressure_exit_two_samples': 256},
    'Q_enabled': False, 'old_caps_or_activity_history_changed': False,
    'no_permission_to_start_old_source_or_CIDs': True,
}
save_json('continuation-permit.json', permit)

work_prefix = f'''# TASK117/R111 — S07初版分层接收，S08原窗完成剩余与验证

{now}。S07报告88265字节/fc600e13…93aab与封存回执匹配，15项清单、6项实际修改、旧79709字节后缀及163源的6项授权增量核对成立，bundle7四字节仍旧，不含新教学源码。接收初版与封存，未接受D01—D03修复通过，D04未实施；全部新验证not_run，完整S仍不通过、Q冻结，尚不送独审。

S07从2026-10-17T01:14:01.395492Z到09:38:56.049183Z保守活动30294.653691/21600，超8694.653691秒；mono域倒退/原因未知，未预登记pause。metadatawall漏记仍unknown，不能因受控测试0声称全部读写进程0。旧5段/24根/63条失败前缀及events794002字节前缀不变，现失败66、active_root空，运行次数全未新增。历史控制不通过不赦免。

已签同号S08前向许可待人工转交原A+窗，未登记新接收/执行，无TASK119。先修本卡计时域与清场控制、有限自检，补D04并完成D01—D03与兼容/草稿测试，收齐实现后typecheck/build和正式bundle最小合成浏览器一次闭合，不重做旧充分PG/恢复/预览/两域链。

S08改为48小时日历有效期、最后1200秒只收口，实际离线命令wall3600和运行持有并集3600硬门。跨中断UTC总差不再作为本新段额外活动硬门；观察投入/上界/unknown继续留账，旧活动门与超额不变。mono域不明禁止负差放行/续原运行截止，准确自有资源先收尾才按同段原日历余量重锚，不重置次数或首点。

仅续用未消费3根至27、Browser3至19/build2至9/fixture server3/HTTP600至2924；PG/SQL/Docker/产品API/业务Job/preview/provider费用/Git新增0。原source永久readonly/frozen和六CID不动。512/768MiB及两次低于256清场保持，单端口18119，原CIM不可用不导致升权或杀用户进程。新证据continuation-07，旧88265字节报告及唯一执行账旧段保留。

稳定后才回原118一次实际增量独审。Q80次20元原条件许可不启用、不重问，实际持久全局准入组合证、官方/配置/新normal资源/72h与启用回执仍须后续；STEP018/019/020/M1/项目未通过。主控只读核证与维护共享，未执行产品测试/build/SQL/Docker/API/Browser/模型/Git。

## 以下为原裁定历史

'''
put(work, work_prefix.encode('utf-8') + before[work])

arch_prefix = f'''# 架构动态文档

文档v1.42，2026-10-17，Asia/Shanghai。需求v1.3、执行动态v2.69、task_model/07。以下v1.41原字节保留，116采用包不扩大。

## 四项审计缺口当前只有初版，未形成已验证修复

{now}。S07已写ControlHub读写共用_validated_locked、受信model_requests完整payload/request摘要及网关快照/dispatch复核、教学不可变owner/view/head/scope/DataContext捕获和草稿/POST时序初版，六文件hash有链。均未测试/typecheck/build/实机验证，不能更新为缺陷关闭；实际供应商告知D04尚未实施。原bundle7仍是旧TSX产物，已有UI证据只对原字节和层有效。

S08按原四项合同完成必要修正与定向验证，范围仍本地文件锁、实际网关合成ledger/transport、正式bundle合成HTTP浏览器，不新增主要模型、迁移、公开写接口或真实供方权限。原source永久readonly/frozen、R01/R02/旧日志/预览安全边界保持。持久共享总门真实PG组合证仍Q前置，本轮替身不冒该项通过。

S07控制器跨宿主mono负差及未知空档计时不能作为续作余量。仅开发控制的新S08前向许可采用48小时日历+命令wall/运行持有+次数硬门，投入观察/上界/unknown另记，不影响产品时间预算、租约、停止证明或退款语义，也不追认任何历史控制违规。GitHub仅既有origin，无新提交/上传。完整S/Q/STEP/项目仍未验收。

## 以下为v1.41及更早历史

'''
put(arch, arch_prefix.encode('utf-8') + before[arch])

state_prefix = f'''# 执行动态文档

文档v2.69，2026-10-17，Asia/Shanghai。唯一总状态账；需求v1.3、架构v1.42、task_model/07。以下v2.68原字节保留。

## TASK117/R111 S07到限已返回，S08合并续作{{status}}

{now}。用户带回S07结果88265字节/fc600e13…93aab；15项封存、6源码增量、163源期望链、4旧bundle、7关键绑定和79709旧后缀匹配。工程调度已返回、验收部分通过仅收初版/封存；D01—D03未验证、D04未实现，四缺陷全开放，完整S不通过、Q冻结，未形成新的独审稳定点。

S07保守活动至复读30294.653691/21600超8694.653691，mono域倒退未知、无预记pause；metadata命令wall漏记不伪称0。原5段/24根和63条失败前缀/原events前缀保持，现66条。唯一账phase=S07_returned_incomplete_activity_limit、active_root空；root24/PGcreate对象卷6/PGstart46/产品API33/Browser16/build7/Native140/HTTP2324/fixture server0/preview各2/provider费用0不变。不是新验证失败，所有新测试/build/Browser/controller自检均not_run。

S08同号原A+继续，保留六初版和原证据，不占119、不提前再审。先有限修本卡计时域/截止与精确清场，再补D04和四项最小测试，typecheck/build成功后正式bundle合成浏览器。稳定后回原118独立上下文仅实际增量复核。原118审计及所有其它有效结论按原字节继承，不再重做全部合成链。

新前向计时采用48小时日历、最后1200秒仅保存、离线命令wall3600/运行持有并集3600和原次数硬门。跨账号/宿主中断UTC差只作投入上界与unknown记录，不再作本新段额外活动硬门；旧21600门/8694.653691超额及其它历史不改。跨域负mono不得放行、不续旧运行截止；准确资源收尾后只能在同段原日历及余量重锚。

只续用原未消费3根至27/Browser3至19/build2至9/fixture server3/HTTP600至2924，PG/SQL/Docker/产品API/业务Job/preview/provider费用/Git新增0。低内存512/768MiB/两次<256清场与18119独占保持，不再要求Docker暖机/2GiB。source frozen/永久readonly和旧六CID不动；新证据continuation-07、原88265字节报告保持，原账仅追加。主控未查实时系统；S07有限Get-Process/netstat观察与CIM不可用原件只按其时点引用，原PG只沿更早停止原件。

Q80次20元仍条件许可未启；官方当期条件/正常配置/新normal合成资源、真实PG持久总门组合证、实际清单/72h与启用回执后续处理。GitHub已有origin，无commit/push。STEP018/019/020/M1/项目未通过。本轮主控只读核证/维护共享，无产品/测试/build/SQL/Docker/API/Browser/provider/Git写。证据/许可/旧共享/保存证明在DocuN/evidence/TASK-117/orchestration-s08-20261017。CHG1479—1486，下一1487。

## 以下为v2.68及更早历史

'''
put(state, state_prefix.replace('{status}', '已登记待保存').encode('utf-8') + before[state])
save_json('dispatch-registration.json', {'at': now, 'task': 'TASK-117', 'R': 'R-111', 'stage': 'S08', 'state': 'registered_before_save', 'new_TASK_or_R': False, 'manual_transfer': True, 'actual_dispatch_or_receipt': False})
put(card, new_card)
put(state, state_prefix.replace('{status}', '待人工转交').encode('utf-8') + before[state])

rows = [
    ('1479', 'DocuN/evidence/TASK-117/orchestration-s08-20261017/received-s07.json', '核15封存/163源链/4bundle/7绑定及旧后缀、初版/未运行/时钟到限分层，旧66失败不改。'),
    ('1480', 'DocuN/results/TASK-117-work-decision.md', 'S07部分回收、四缺陷未闭，原窗S08补齐实现与验证，Q冻结。'),
    ('1481', 'DocuS/执行动态文档.MD', 'v2.69先登记同号续作再保存，待人工转交，不冒接收执行。'),
    ('1482', 'DocuN/tasks/TASK-117.md', '完整S08续作卡，旧S07原卡备份，保留六初版、不重派全部旧链。'),
    ('1483', 'DocuS/架构动态文档.MD', 'v1.42登记未验证初版和未实施D04、当前旧bundle，未冒修复通过。'),
    ('1484', 'DocuN/evidence/TASK-117/orchestration-s08-20261017', '输入/前向许可明确48h与进程/持有/次数门，旧活动超额保留，无新增PG或付费许可。'),
    ('1485', 'DocuN/evidence/TASK-117/orchestration-s08-20261017/before-documents', '五份旧共享原字节和有限normalized差异核对留存；不写源/工程账/旧原件。'),
    ('1486', 'DocuN/evidence/TASK-117/orchestration-s08-20261017/save-proof.json', '新卡/共享复读、规则与受保护输入不变，历史原体保留，主控不代执行。'),
]
append = '\n' + '\n\n'.join(f'- CHG-{n}，{now}，Codex编排Agent，{p}。{s}' for n, p, s in rows) + '\n'
put(change, before[change] + append.encode('utf-8'))

for p, expected in protected.items():
    assert identity(p) == expected, str(p)
for rule in rules:
    assert h(Path(rule['absolute_path']).read_bytes()) == rule['sha256']
for p in [work, state, arch]:
    assert p.read_bytes().endswith(before[p])
assert change.read_bytes().startswith(before[change]) and card.read_bytes() == new_card
proof = {'saved_at': datetime.now(timezone(timedelta(hours=8))).isoformat(), 'result': 'SAVED_AND_READ_BACK',
         'task': 'TASK-117 / R-111 S08', 'versions': {'state': 'v2.69', 'architecture': 'v1.42', 'last_CHG': 1486},
         'documents': [{'path': str(p), **identity(p)} for p in [state, arch, work, card, change]],
         'protected_inputs': len(protected), 'protected_mismatches': [], 'old_shared_raw_suffixes_preserved': True,
         'old_reports_budget_events_case_index_products_dist_unchanged': True, 'rules_7_match': True,
         'S07_closed_or_passed': False, 'Q_enabled': False, 'new_TASK_or_R': False,
         'actual_dispatch_or_receipt': False, 'main_product_or_runtime_execution': 0}
save_json('save-proof.json', proof)
print(json.dumps({'result': proof['result'], 'task': proof['task'], 'source163': len(current_sources),
                  'S07changed6': len(changed), 'protected': len(protected), 'state': 'v2.69', 'arch': 'v1.42',
                  'last_CHG': 1486, 'manual_transfer_pending': True, 'Q_enabled': False}, ensure_ascii=False))
