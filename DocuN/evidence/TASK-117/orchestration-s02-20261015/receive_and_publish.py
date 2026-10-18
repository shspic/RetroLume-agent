"""原卡部分回收、原件身份核证与前向续作许可，只维护文档/元数据。"""
from pathlib import Path
from datetime import datetime, timedelta, timezone
import hashlib
import json
import re

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent').resolve()
OUT = Path(__file__).resolve().parent
EX = ROOT / 'DocuN/evidence/TASK-117/execution'
REPORT = ROOT / 'DocuN/results/TASK-117-result.md'
CARD = ROOT / 'DocuN/tasks/TASK-117.md'
WORK = ROOT / 'DocuN/results/TASK-117-work-decision.md'
ARCH = ROOT / 'DocuS/架构动态文档.MD'
STATE = ROOT / 'DocuS/执行动态文档.MD'
CHANGES = ROOT / 'DocuS/文档变更记录.MD'

def load(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def ident(p):
    raw = p.read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

def save(name, obj):
    p = OUT / name
    assert p.resolve().is_relative_to(ROOT) and not p.exists(), str(p)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    assert load(p) == obj

def prefix(p, text, raw):
    assert p.resolve().is_relative_to(ROOT)
    assert '*' not in text and not re.search(r'^\|', text, re.MULTILINE)
    p.write_bytes(text.replace('\n', '\r\n').encode('utf-8') + raw)
    assert p.read_bytes().endswith(raw)

assert OUT.resolve().is_relative_to(ROOT)
assert not (OUT / 'received.json').exists()
assert ident(REPORT) == {'bytes': 21405, 'sha256': 'db9dd539274c9b77db237410de31a6c9cc75595bae3b758d6e6c2d5573351b53'}
assert ident(EX / 'final-source-manifest.json')['sha256'] == 'a5610ca9591cefd9e20a58c06a2416196179feb84c8b1247df64f9c8cfc2c210'
before = {p: p.read_bytes() for p in (CARD, WORK, ARCH, STATE, CHANGES)}
assert '文档v1.34' in before[ARCH].decode('utf-8-sig').splitlines()[2]
assert '文档v2.59' in before[STATE].decode('utf-8-sig').splitlines()[2]
nums = [int(x) for x in re.findall(r'^- CHG-(\d+)', before[CHANGES].decode('utf-8-sig'), re.MULTILINE)]
assert nums[-1] == 1411 and 1412 not in nums
continuation = (OUT / 'effective-continuation.md').read_bytes()
txt = continuation.decode('utf-8')
assert '*' not in txt and not re.search(r'^\|', txt, re.MULTILINE)
for token in ('TASK-117 / R-111', 'S02', '28800', '37651.0027854', '66451.0027854',
              '16219.360', '27019.360', '3600', 'X07', 'source_manifest_sha256',
              '不把超额追认为合规', '审批', 'R01/R02', '最后1800', '结果仍'):
    assert token in txt, token

sources = load(EX / 'final-source-manifest.json')['entries']
assert len(sources) == 77
current = []
for row in sources:
    p = ROOT / row['path']
    expected = row['post']
    if expected['exists']:
        actual = ident(p)
        assert actual == {k: expected[k] for k in ('bytes', 'sha256')}, str(p)
        current.append({'path': row['path'], 'exists': True, **actual})
    else:
        assert not p.exists(), str(p)
        current.append({'path': row['path'], 'exists': False})
binding = load(EX / 'final-binding.json')
for name, expected in binding['bundle'].items():
    assert ident(ROOT / name) == expected, name
assert ident(ROOT / 'backend/migrations/014_step018_retrieval.sql')['sha256'] == binding['migration_014_actual_sha256']
saved = load(EX / 'result-save-receipt.json')
assert ident(REPORT) == {k: saved[k] for k in ('bytes', 'sha256')}
budget = load(EX / 'budget.json')
stop = load(EX / 'final-resource-stop.json')
observed = load(EX / 'final-budget-observed.json')
assert budget['phase'] == 'hard_stopped_partial_result_saved' and budget['active_root'] is None
assert saved['S_complete'] is False and saved['Q_enabled'] is False
assert saved['all_owned_resources_stopped'] is True
assert budget['counts'] == saved['counts'] == observed['counts']
assert budget['counts']['roots'] == 4 and budget['counts']['provider_calls'] == 0
assert all(not p['running'] and p['pid'] == 0 for p in stop['pg'])
assert {p['cid'] for p in stop['pg']} == {
    '1df68961975a43929fa06f63314a0da6e4e5cea113e3c403fc1ffd90d7c0fa5f',
    '0741d770fe07cc145660929044c471ef73fee11bb58e3ee6593e9a47adaa67c8'}
cases = load(EX / 'case-index.json')
assert len(cases['cases']) == 28 and not any(x['frozen_scenario_passed'] for x in cases['cases'])
rules = load(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
for row in rules:
    assert ident(Path(row['absolute_path']))['sha256'] == row['sha256']

# 只冻结非私密原始材料；不打开本TASK凭据、operator认证文件或合成控制密文。
raw_evidence = []
for p in sorted(EX.rglob('*')):
    if not p.is_file():
        continue
    relative = p.relative_to(EX)
    if any(part.lower() in ('synthetic', 'private', 'operator', '__pycache__') for part in relative.parts):
        continue
    assert p.resolve().is_relative_to(ROOT)
    raw_evidence.append({'path': p.relative_to(ROOT).as_posix(), **ident(p)})
protected = {}
for name in ('AGENTS.md', 'DocuS/原始需求文档.MD', 'DocuS/最终需求文档.MD',
             'DocuN/results/TASK-116-result.md', 'DocuN/results/TASK-112-result.md',
             'DocuN/results/TASK-115-result.md', 'DocuN/results/TASK-117-result.md'):
    protected[name] = ident(ROOT / name)
for row in current:
    if row['exists']:
        protected[row['path']] = {k: row[k] for k in ('bytes', 'sha256')}
for row in raw_evidence:
    protected[row['path']] = {k: row[k] for k in ('bytes', 'sha256')}

at = datetime.now(timezone(timedelta(hours=8))).isoformat()
backup = OUT / 'before-documents'
backup.mkdir(exist_ok=False)
for p, raw in before.items():
    (backup / p.name).write_bytes(raw)

received = {
    'received_at': at, 'TASK': 'TASK-117', 'R': 'R-111', 'STEP': '018',
    'report': {'path': str(REPORT), **ident(REPORT)},
    'result_axes': {
        'implementation': 'partial_engineering_increment_not_complete_S',
        'evidence': 'partial_valid_typed_PG_HTTP_and_bundle_progress_with_as_run_limits',
        'execution_control': 'not_passed_S01_hard_limits_exceeded_cleanup_controller_defect',
        'final_acceptance': 'not_accepted_as_complete_S_or_STEP018', 'independent_audit': 'not_run'
    },
    'current': current, 'raw_evidence': raw_evidence, 'rules': rules,
    'binding': binding,
    'S01_sealed': {
        'original_start_utc': budget['start_utc'], 'original_start_mono_ns': budget['start_mono_ns'],
        'activity_at_stop': observed['activity_elapsed_seconds'],
        'activity_at_last_result_save': saved['activity_elapsed_at_save_seconds'],
        'original_activity_cap': 28800,
        'activity_over_at_last_save': saved['activity_elapsed_at_save_seconds'] - 28800,
        'conservative_runtime_holding': observed['runtime_holding_conservative_seconds'],
        'actual_CID_union_runtime_holding': load(EX / 'final-holding-union.json')['seconds'],
        'original_runtime_cap': 14400, 'offline_seconds': observed['offline_seconds'],
        'counts': budget['counts'], 'original_caps': budget['caps'],
        'cleanup_original_record': stop,
        'resource_state_scope': '原件时点精确停止，本轮主控不运行Docker重新查询或连库',
        'no_budget_reset_or_retroactive_approval': True
    },
    'reuse': {
        'ROOT01': '初版12方法及4新合同断言的实际版本有效，v4/null后最终影响仍须定向复检',
        'ROOT02': '真实普通PG/Windows索引query/cache及float32/SQL摘要部分有效，不冒全部冻结场景',
        'ROOT04': '真实普通角色HTTP教学/面试状态链和正常loader就绪部分有效，N替身不冒L01/I01/Q',
        'browser': '最终bundle第二次到接受路径，选择n1修正未跑；第三次审批服务用量拦截未执行',
        'profiles': 'P01仅早期非空/R01包，compat缺最终只读ACL，P02/P03未跑'
    },
    'root_cause': 'source独立由root04_start启动，API控制器有截止但PG不在同一自动清场闭包；审批/聊天中断使PG继续持有',
    'continuation_precondition': '先修原fixture有界清场，不依赖下一工具审批；再开剩余真实链',
    'open_original_Must': ['X07整步预算前拒', 'X12实际source外发采用闭包', '28场景剩余S层', 'P01最终ACL/P02/P03', 'L10', 'X09', '启动文档'],
    'Q': '未启用/费用0；已有候选差异及官方访问缺口待核，不静换模型，不再索20元授权',
    'main_product_execution': 0,
    'protected': protected
}
save('received.json', received)

permit = {
    'TASK': 'TASK-117', 'R': 'R-111', 'STEP': '018', 'issued_at': at,
    'permit': 'TASK-117-STEP018-INTEGRATION-S02-20261015',
    'basis': '用户已批准AP1/AP2并返回部分成果；主控按既有开发边界对同号追加完整前向合成实施段',
    'current_phase': 'S02_synthetic_complete_candidate', 'Q_active': False,
    'actual_received_at': None, 'execution_started': False, 'dispatch_confirmed': False,
    'activity_new_max': 28800, 'calendar_from_actual_receipt_hours': 48,
    'save_cleanup_reserve': 1800, 'no_expand_after': 25200, 'cleanup_only_after': 27000,
    'sealed_S01_activity': 37651.0027854, 'activity_forward_total_limit': 66451.0027854,
    'holding_new_max': 10800, 'sealed_S01_holding_conservative': 16219.36,
    'holding_forward_total_limit': 27019.36, 'offline_new_max': 3600, 'original_offline_total_max': 7200,
    'root_business_seconds_max': 2100, 'root_cleanup_seconds': 300, 'root_total_seconds_max': 2400,
    'new_complete_target_roots_max': 5, 'S_total_roots_max': 9, 'TASK_total_roots_with_Q_reserved': 10,
    'build_new_max': 2, 'build_total_max': 5, 'API_start_new_max': 5, 'API_start_total_max': 10,
    'Browser_start_new_max': 6, 'Browser_original_total_max': 8,
    'PG_starts_new_max': 17, 'PG_original_starts_total_max': 20,
    'unchanged_limits': {'PG_create': 8, 'PG_objects': 5, 'volumes': 5, 'Native': 160,
                         'preview_create': 12, 'preview_start': 12, 'HTTP': 3000,
                         'memory_min_GiB': 2, 'PG_concurrent': 2, 'API_concurrent': 1,
                         'Browser_concurrent': 1, 'preview_concurrent': 1},
    'official_document_new_targets_max': 8, 'official_document_total_targets_max': 18,
    'current_provider_calls_fee': 0, 'AP2_80_requests_20_CNY_unchanged_not_active': True,
    'existing_resource_profile': 'DocuN/evidence/TASK-117/orchestration-20261014/resource-profile.json',
    'old_resource_S01_labels_preserved': True,
    'first_gate': '修现有controller，证明无新工具批准亦能到D精确收尾所有自有资源，之后再启真实PG/API/Browser',
    'original_S01_caps_and_overruns': '全部原字段/原报告保留；新限额不追认旧超限',
    'approval_service': '额度限制不是本卡可改变的平台权限；仍拦截则停止依赖/自动清场不机械重试',
    'used_new_at_issuance': 0
}
save('continuation-permit.json', permit)
save('window-assignment.json', {
    'TASK': 'TASK-117', 'R': 'R-111', 'grade': 'A+',
    'window': 'continue original TASK117/116/114 engineering',
    'manual_handoff': True, 'transferred': False, 'received': False,
    'reason': '77项候选和原私有合成状态/失败留在原窗，范围内修复及余缺完整收口，避免重新开发',
    'independent_auditor': False, 'subagents': False,
    'future_audit': 'S完整稳定后另隔离窗口集中，当前不预占118',
    'platform_usage_limit_note': '许可不恢复平台审批配额；需要真实能力可用，不能绕审批'
})

work_text = f'''# TASK117/R111 — S01部分回收与S02完整续作01许可

{at}。用户返回真实S01结果21405字节/db9dd539274c9b77db237410de31a6c9cc75595bae3b758d6e6c2d5573351b53。主控核77登记源/删除标记、4最终bundle、014绑定、28场景账、原typed/检索/HTTP/Browser/控制器及准确停机原件和七规则。实现轴部分、证据轴部分有效、执行控制轴S01不通过；不能验收完整S/STEP018，也不是仅差浏览器一例。原已成功层和全部失败有效保留，不重跑足够原件。

已交付typed embedding/float32/RRF/014/R02代码、普通角色PG/Windows检索、N教学和面试状态链及最终bundle到路径接受，均按实际as-run范围继承。compat缺最终只读授权、P02/P03物理恢复未跑、X07整步门与实际source采用闭包未完成、原8源/PDF/记忆/故障与L10/X09/本机文档未收口；没有冻结场景整体通过。源码已写不等于全验证，普通同边界修复继续原卡，不提前插全面独审。

S01最严重控制缺口是API有截止但source PG脱离其自动清场闭包；审批服务拦截/聊天中断后持续持有，并非只因token/额度不足。停机活动36673.4247854，最后保存37651.0027854/28800、超8851.0027854；保守持有16219.360/14400、实际CID并集16216.391，离线1724.875、root4、create/object/volume2、PGstart3/API5/Browser2/build3/Native保守28/HTTP146/preview0/provider0均封存。原两个CID准确停止/Pid0、原API句柄退出/Browser两进程已结束据原时点记录继承，本轮主控未实查Docker，不冒当前现场。第三次Browser因自动审批服务用量限制未执行，计数仍2，不当安全不通过。

在既有AP1开发授权内追加S02许可TASK-117-STEP018-INTEGRATION-S02-20261015，A+原工程窗。先修本卡控制器完整有界清场，再连续完成全部S余缺；不借产品SUP主体修夹具，不清旧账。新活动28800/48h含1800收尾、持有10800/offline3600且总offline7200，单真实根2100业务+300收尾，最多5新根/S总9/Q保留1；build新增2累计5，API新增5累计10，其余原物理/窗口/HTTP等总门保持，Browser可用余6/总8。旧S01许可结束/超额原FAIL不被新门追认，resource labels保持S01并登记S02复用权。

完整任务卡以S02段置顶、原卡全文原字节保留，待人工转交，未派发/未接收新段。新增执行量0，不重建原source/compat、不开用户数据/真实provider/费用。正常operator rekey授权继续，当前候选仍未集中独审；后续Q必须核候选差异与现行条款/价额/账户及新边界审计和主控启用，已批准80次/20元不重新问或扩大。官方页面新8/累计18只作有限输入，不把Q未知当S完成借口。

如自动审批服务仍受限，先由已设置的控制器精确结束自有资源，停止受影响段，避免相同命令重试/PG空耗；本许可无法恢复平台配额，不绕审批。必要时交回具体平台阻塞，原卡/账不清。原结果/77源/旧证据/公共规则/需求/全项目旧13元/626.566/25-UNKNOWN-R60等不写。STEP018/019/020/M1/项目未通过，稳定S后才集中独审。

回收和续作证据、原共享备份、许可/输入/窗口/保存证明位于DocuN/evidence/TASK-117/orchestration-s02-20261015；新执行产物continuation-01归原execution，唯一主账仍由执行者前向追加。主控产品执行0。原结果全文保留，续作结果仍同TASK117-result.md。

## 以下为S01原许可及交接历史

'''
prefix(WORK, work_text, before[WORK])
arch_text = f'''# 架构动态文档

文档v1.35，2026-10-15，Asia/Shanghai。需求v1.3、执行动态v2.60、task_model/07；以下v1.34历史原字节保留。采用包不变，记录实际候选与未完成项。

## STEP018候选增量已落地，完整S尚未完成

{at}。TASK117/R111 S01真实返回，77项受影响登记与最终bundle/014实际身份核对相符。新typed Embedding、float32向量摘要/RRF、014三表/grant/新kind、wire v4及领域profile/R02 registry已部分落地；普通角色PG/Windows检索和N教学/面试HTTP状态链有实际层证据，不冒冻结L01/I01及真实语义。现014 hash4aa808fd80845e8abb1f09d5547a5c63694fea2f781a69200ec6a992ea8247b0，vector0.8.6实测按工程原件，source extra shape a3c9bc08f104ad5f6dfc03c3902ad720ea871f6ff94fab299210cd68befaedbb；compat最后invoker只读ACL未同步，不能写最终profile均已一致。

明确未闭为X07 query+model整步预算前拒、真实source采用闭包与grant正反、选记忆两域/冻结7源与PDF及故障传播、正常同库重开、R01/R02物理恢复、L10实际预览、最终启动与文档。固定宿主正常部署loader已接受不代表产生本轮artifact/ACK/PNG/StopProof；Q未启用，新kind/权限/预算/R02尚未独审。不能从代码存在或模板通过签完整Must。

S01控制器只关API而PG留存导致硬门超额，属于执行夹具闭包缺口，不改产品SUP/Job/停止退款权。原窗S02在同采用边界内先修自动完整收尾，再合并实现/验证余缺；旧失败/源/状态/费用保留，原frozen/readonly/UNKNOWN不解封。R01/R02永只读与正常同库继续仍分开。

AP1/AP2采用不重批；20元/80次条件性额度未启用，执行者记录的候选/官方访问差异需后续核实，不静换模型或把安全/条款门省掉。Windows/Compose/固定v2-08动态预览继续，无新平台/生产发布/用户数据。STEP018—020及项目未通过，S稳定后适用集中独审。

## 以下为v1.34及更早历史

'''
prefix(ARCH, arch_text, before[ARCH])
state_text = f'''# 执行动态文档

文档v2.60，2026-10-15，Asia/Shanghai。唯一总状态账；需求v1.3、架构v1.35、task_model/07。以下v2.59历史原字节保留。

## TASK117 S01部分停止已回收，S02完整续作01待人工转交

{at}。用户真实带回S01报告21405字节/db9dd539274c9b77db237410de31a6c9cc75595bae3b758d6e6c2d5573351b53，已接收/执行/返回。主控核77源登记含删除标记、4最终bundle、014/28case、原成功/失败/停止/单账与七锁定规则；实现部分、证据部分有效、执行控制S01不通过，完整S/STEP018未验收。无冻结场景整体通过不等于没有局部成果；检索/HTTP等按实际版本和层继承，未做产品复跑或提前全面独审。

主要余缺为完整冻结两链/7源PDF/选记忆与故障矩阵、X07整步门/实际source采用闭包、compat最终ACL及P02/P03恢复、正常同库重开/L10/本机文档。第三Browser被自动审批服务用量限制拦截未执行、计数2保留；API控制器截止只关API而source未纳同自动清场导致等待期间越活动与持有门，不能全部归审批故障或追加额度了事。

S01封存活动停机36673.4247854、最后保存37651.0027854/28800（超8851.0027854）；保守持有16219.360/14400、实际CID并集16216.391，offline1724.875、root4、PGcreate/object/volume2/start3、API5/Browser2/build3/Native保守28/HTTP146/preview0/provider0/fee0，原失败/缺birth/pre/90秒未知原件保留。原source 1df68961975a43929fa06f63314a0da6e4e5cea113e3c403fc1ffd90d7c0fa5f与compat0741d770fe07cc145660929044c471ef73fee11bb58e3ee6593e9a47adaa67c8据原精确清场均stopped/Pid0，API/Browser已结束；本轮没有实查Docker或连接DB，旧时点不冒新现场。

同TASK117/R111 S02完整卡已置顶保存复读，待人工转交原A+工程窗口，未派发/未接收/新执行0，无新TASK118。许可TASK-117-STEP018-INTEGRATION-S02-20261015先修本卡完整自动收尾再开真实资源，合并余缺实现/有限验证/普通修复；不新增平台或改产品停止主体。原卡/旧报告/失败/账/CID/标签原字节保留，源/公共规则/需求不动。

本段活动新28800/48h含1800清场，累计前向门66451.0027854；holding新10800/累计27019.360，offline新3600且原总7200。真实根2100业务+300清场/本段5，S累计9/Q保留1；正式build加2至5，API加5至10；Browser余6累计8、PGstart余17累计20及原create8/对象5/卷5/Native160/preview12/HTTP3000/内存2GiB/并发门不变。原超额和原cap不改，不因新额度追认旧合规；S01结束到S02接收停线间隔不追称执行。旧所有全项目账继续保持。

当前仍仅S，Q真实API/费用0，原80次/20元条件性批准不重问、不启用。官方新8页/累计18用于准确Q准备，候选差异及账户条款/价格未知后续核，不静换供应商/模型/维度，不把Q缺口替代S未完成。平台审批额度不由本卡恢复，仍受阻则已有控制器清场后停依赖，不重复同命令空耗。稳定完整S才安排独立集中审计，STEP018/019/020/M1/项目未通过。

主控只读原件/身份、预算核算和共享维护，产品/测试/SQL/Docker/API/Browser/模型/外网/费用/Git写全0。回收/原始保护/新许可/窗口/输入/旧共享/保存证明在DocuN/evidence/TASK-117/orchestration-s02-20261015。CHG1412—1420，下一1421。唯一执行主账仍原execution/budget/events，未来产物continuation-01，原结果保留全文同路径续写。

## 以下为v2.59及更早历史

'''
prefix(STATE, state_text, before[STATE])
CARD.write_bytes(continuation + before[CARD])
assert CARD.read_bytes().endswith(before[CARD])
assert CARD.read_bytes().startswith(continuation)

entry_specs = [
    ('received.json', 'S01部分成果/77源/原证据/预算与准确清场核证，控制轴超限不通过，足够原证继承。'),
    ('DocuN/results/TASK-117-work-decision.md', '同号S02前向许可，先修控制器/原Must余缺，不重置或提前全面审计。'),
    ('continuation-permit.json', '活动/持有/子次数实际基数与新增上限、独立2400秒根清场和Q关闭。'),
    ('DocuN/tasks/TASK-117.md', '完整S02续作置顶、原卡/部署补充全文保留，原A+工程窗人工接续。'),
    ('DocuS/架构动态文档.MD', 'v1.35实际typed/014/R02候选与未完成X07/采用闭包/两链恢复及宿主证据范围。'),
    ('DocuS/执行动态文档.MD', 'v2.60原S01真实返回/硬门停止及S02待转交，失败/超额/计数/旧账保留。'),
    ('input-manifest.json', '本轮实际前置/源身份/原账与精确两CID及输入，不读private或重复制整仓。'),
    ('before-documents', '原卡/Work/架构/执行/变更原字节备份，原结果/源码/执行原件不改。'),
    ('delivery-proof.json', '完整合同/许可/输入/保存复读及原保护对象/规则一致，平台配额未冒恢复。')
]
tail = ''.join(f'\r\n- CHG-{1412+i}，{at}，Codex编排Agent，'
               f'{name if "/" in name else "DocuN/evidence/TASK-117/orchestration-s02-20261015/"+name}。{detail}\r\n'
               for i, (name, detail) in enumerate(entry_specs))
CHANGES.write_bytes(before[CHANGES] + tail.encode('utf-8'))
assert CHANGES.read_bytes().startswith(before[CHANGES])
new_nums = [int(x) for x in re.findall(r'^- CHG-(\d+)', CHANGES.read_text(encoding='utf-8-sig'), re.MULTILINE)]
assert new_nums == nums + list(range(1412, 1421))

inputs = [CARD, WORK, ARCH, STATE, ROOT / 'DocuS/最终需求文档.MD', REPORT,
          EX / 'final-source-manifest.json', EX / 'final-binding.json', EX / 'result-save-receipt.json',
          EX / 'budget.json', EX / 'events.jsonl', EX / 'case-index.json',
          EX / 'final-resource-stop.json', EX / 'final-budget-observed.json',
          EX / 'official-check.json', OUT / 'continuation-permit.json', OUT / 'received.json']
save('input-manifest.json', {
    'issued_at': at, 'formal': {'requirements': 'v1.3', 'architecture': 'v1.35', 'execution': 'v2.60'},
    'inputs': [{'path': str(p), **ident(p)} for p in inputs],
    'current_registered': current, 'rules': rules,
    'no_full_repo_rehash_or_private_read': True,
    'resource_profile_unchanged_reference': 'DocuN/evidence/TASK-117/orchestration-20261014/resource-profile.json',
    'original_S01_sealed_counts': budget['counts'],
    'source_CID': '1df68961975a43929fa06f63314a0da6e4e5cea113e3c403fc1ffd90d7c0fa5f',
    'compat_CID': '0741d770fe07cc145660929044c471ef73fee11bb58e3ee6593e9a47adaa67c8',
    'runtime_current_state_check': 'not_run_by_main; executor must verify before resume'
})
for name, expected in protected.items():
    assert ident(ROOT / name) == expected, name
for row in rules:
    assert ident(Path(row['absolute_path']))['sha256'] == row['sha256']
assert not (ROOT / 'DocuN/tasks/TASK-118.md').exists()
save('delivery-proof.json', {
    'saved_at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
    'status': 'saved_readable_pending_manual_handoff_S02',
    'files': [{'path': str(p), **ident(p)} for p in (CARD, WORK, ARCH, STATE, CHANGES,
              OUT / 'continuation-permit.json', OUT / 'received.json', OUT / 'input-manifest.json')],
    'sources_registered_checked': len(current), 'nonprivate_evidence_checked': len(raw_evidence),
    'protected_unchanged': len(protected), 'old_card_and_formal_histories_preserved': True,
    'result_original_bytes_unchanged': True, 'execution_budget_events_control_private_untouched': True,
    'no_product_or_resource_execution': True, 'Q_activated': False,
    'CHG': list(range(1412, 1421)), 'new_agent_or_TASK118': False,
    'platform_approval_quota_restored': 'not_claimed'
})
print(json.dumps({'status': 'SAVED_AND_READABLE_PENDING_MANUAL_HANDOFF',
                  'card': str(CARD), **ident(CARD), 'continuation': str(OUT / 'effective-continuation.md'),
                  'source_checks': len(current), 'evidence_checks': len(raw_evidence),
                  'architecture': 'v1.35', 'execution': 'v2.60', 'last_CHG': 1420,
                  'main_product_execution': 0, 'Q': 'closed'}, ensure_ascii=False))
