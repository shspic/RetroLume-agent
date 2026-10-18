"""只核证设计与维护共享文档，不导入或运行产品。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
DESIGN = ROOT / 'DocuN/evidence/TASK-119/design'
assert ROOT == Path('D:/shspic/project_NO3_RetroLume-agent').resolve()
assert not (HERE / 'save-proof.json').exists(), '已有保存证明，禁止重复发布'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def identity(path):
    return {'path': str(path), 'exists': path.is_file(), 'bytes': path.stat().st_size if path.is_file() else 0,
            'sha256': digest(path) if path.is_file() else None}


def write(path, content, new=False):
    assert path.resolve().is_relative_to(ROOT), str(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = content.encode('utf-8') if isinstance(content, str) else content
    with path.open('xb' if new else 'wb') as stream:
        stream.write(raw)
    assert path.read_bytes() == raw
    raw.decode('utf-8-sig')


def save_json(name, content):
    write(HERE / name, json.dumps(content, ensure_ascii=False, indent=2) + '\n', True)


now = datetime.now(timezone(timedelta(hours=8))).isoformat()
rules = load(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
inputs = load(DESIGN / 'input-identities.json')
check = load(DESIGN / 'document-consistency.json')
receipt = load(DESIGN / 'execution-receipt.json')
matrix = load(DESIGN / 'call-matrix.json')
verified = []
for row in rules:
    path = Path(row['absolute_path'])
    assert digest(path) == row['sha256'], str(path)
    verified.append({'kind': 'rule', **identity(path), 'match': True})
for row in inputs['inputs']:
    path = Path(row['path'])
    if row.get('exists') is False:
        assert not path.exists(), str(path)
    else:
        assert path.is_file() and path.stat().st_size == row['bytes'] and digest(path) == row['sha256'], str(path)
    verified.append({'kind': 'input', **identity(path), 'match': True})
for row in check['artifacts']:
    path = Path(row['path'])
    assert path.stat().st_size == row['bytes'] and digest(path) == row['sha256'], str(path)
    verified.append({'kind': 'artifact', **identity(path), 'match': True})
report = Path(receipt['result']['path'])
assert report.stat().st_size == 58870 and digest(report) == receipt['result']['sha256'] == '2d10d08bf2d16ff136258b122d93d12747b659744a4ae5c6036d348806096346'
verified.append({'kind': 'report_receipt', **identity(report), 'match': True})
assert len(verified) == 54
assert receipt['status'] == 'design_complete_Q_frozen'
assert all(value == 0 for value in receipt['runtime_new_counts'].values())
assert receipt['network']['search_queries'] <= 8 and receipt['network']['effective_responses'] <= 16
assert receipt['metadata_wall_conservative_charged_seconds'] <= 1200
totals = {key: sum(row.get(key, 0) for row in matrix['rows']) for key in
          ['model_calls', 'query_calls', 'index_calls', 'html_calls', 'requests', 'reserve_microunits']}
assert totals == {'model_calls': 39, 'query_calls': 39, 'index_calls': 2, 'html_calls': 1,
                  'requests': 81, 'reserve_microunits': 20250000}
by_role = {role: sum(row['requests'] for row in matrix['rows'] if row['activity'] == role)
           for role in ['learning', 'interview', 'supplement']}
assert by_role == {'learning': 39, 'interview': 24, 'supplement': 18}

state = ROOT / 'DocuS/执行动态文档.MD'
arch = ROOT / 'DocuS/架构动态文档.MD'
changes = ROOT / 'DocuS/文档变更记录.MD'
work = ROOT / 'DocuN/results/TASK-119-work-decision.md'
proposal = HERE / 'adoption-proposal.md'
assert not work.exists() and not proposal.exists()
assert not (ROOT / 'DocuN/tasks/TASK-120.md').exists(), '下卡已存在，须核对归属'
assert '文档v2.71' in state.read_text(encoding='utf-8-sig').splitlines()[2]
assert '文档v1.44' in arch.read_text(encoding='utf-8-sig').splitlines()[2]
assert max(map(int, re.findall(r'CHG-(\d+)', changes.read_text(encoding='utf-8-sig')))) == 1503
before = {path: path.read_bytes() for path in [state, arch, changes]}
protected_paths = {Path(row['path']) for row in verified}
protected_paths.update(DESIGN.iterdir())
protected_paths.update([ROOT / 'DocuN/evidence/TASK-117/execution/budget.json',
                        ROOT / 'DocuN/evidence/TASK-117/execution/events.jsonl',
                        ROOT / 'DocuN/results/TASK-117-result.md',
                        ROOT / 'DocuN/results/TASK-118-result.md',
                        ROOT / 'DocuS/最终需求文档.MD', ROOT / 'DocuS/原始需求文档.MD'])
protected_paths.difference_update(before)
protected = {path: identity(path) for path in protected_paths}
backup = HERE / 'before-documents'
backup.mkdir(exist_ok=False)
for path, raw in before.items():
    write(backup / path.name, raw, True)

proposal_text = f'''# TASK119增量采用提案，待用户决定

{now}，Codex编排Agent。依据TASK119/R113设计包及原116 AP1/AP2，现只保存具体提案；没有新增可用授权、费用、grant、活动、库或资源。Q继续冻结。

## 一次合并待采用内容

1. 采用零DDL的Q v2批准协议。新normal合成根只绑定一次不可变grant、原三个活动UUID、有限原文、模板和instance。每个未来完整请求由受信本机operator审查实际typed request和实际外发bytes并精确批准；客户端只读等待、用原键显式继续。没有网页通用批准接口、任意正文白名单、自动批准全部后继或第二套金融账。协议3／原协议4、v1精确清单、R01／R02只读恢复及旧业务接口兼容保留。私有ControlHub封闭q事件、artifact、operator权限与等待响应是本次需明确采用的新边界；不能仅凭设计报告自行视为用户已授权。完整规范为DocuN/results/TASK-119-result.md的A—D及本提案的实施澄清。

2. 候选Chat模型由deepseek-chat替换为deepseek-flash，保留deepseek_chat_completions适配器、原base/ChatCompletions、thinking disabled及原输出／字节／10秒限制。embedding-3／512及原两供应商范围不变，不增加Pro、第三家、工具收费服务或本人资料。主控已有限抽核DeepSeek官方公告、更新日志、价目三个公开页；公告淘汰旧名、当前使用deepseek-flash可以支持候选更换，不证明账号、返回别名和最终计费就绪。来源为https://api-docs.deepseek.com/news/news260424/、https://api-docs.deepseek.com/updates/、https://api-docs.deepseek.com/zh-cn/quick_start/pricing/。

3. 将尚未激活的这一份真实Q许可总上限由80次／20元调整为100次／25元，增加的是20次和5元上限，不是再发一份25元或恢复旧13元。固定三个UUID不变，单笔仍250000 microunits、1元=1000000 microunits。学习01800000-0000-4000-8000-000000000001改为48次／12元；面试01800000-0000-4000-8000-000000000002改为28次／7元；补证01800000-0000-4000-8000-000000000003改为24次／6元。三分额准确相加为100／25，不可跨活动借款。

现设计基线39／24／18合计81次、20250000预留，原补证16次分额必不足；只提高全局到81也不能解决它。新分额的19次余量分别为学习9、面试4、补证6；学习若确需L05额外4次则仍余5。它们只供保持Must的实际必要步骤及明确失败，不产生隐式重试许可。实际片段数、合法缓存及全部Must矩阵仍在启用前准确计算；若不能容纳就不启用，不能删Must或另库清账。25元是含全部失败／超时／UNKNOWN的总付费及预留上限，不是报价或成功保证，实际仅在严格最坏成本不超过原0.25且含至少25%裕量时准入。

## 实施合同必须明确的两处规范

K1，approval_id的规范摘要只计算不含approval_id自身的DecisionBody；event_seq在原日志锁内固定后纳入body，生成ID再附入完整回执。重复批准同一未过期prepared返回原决定；过期续批只能在原launch确未领取且资格未变的情况下显式生成新决定并保留旧事件。不采用要求自身hash参与自身计算的对象。

K2，Q共享policy lease仅覆盖当前请求资格核定、准入／mark和有限transport完成／异常退出这一临界段。它必须在进入会改变head的record_outcome／领域结果提交前释放；之后按同一Q写规则先取排他policy lease，再取MutationGate及原PG锁，使用原CAS／currentness核定，不升级仍持有的共享锁，不在已持PG锁时反向等policy锁。间隔中若scope／head／source／memory改变，保留原operation/007不可变事实及预留，只按现有失效规则抑制消费，不再发或退款。operator revoke只报告排他锁真实取得后的本地阻断；不能把可能已在途的请求说成已撤回。受影响路径需在下一完整工程成果中补一个有界并发反例和一条正常结果落地，不为本澄清另开实验卡。

这两处为主控对设计歧义的实施收敛，尚无产品代码或运行证明。文件ACL、同OS principal信任范围和worker读写能力必须如实区分；逻辑方法限制不能冒充独立OS隔离，未实现的权限检查不签ready。

## 采用之后的推进和仍关闭的操作

若用户一并采用，主控先发一个完整A+工程卡，沿原TASK117／119工程窗口一次完成全部前置实现、普通修复、真实PG零外发组合及最终bundle传播，再交原TASK118独审归属仅核新增边界。不给执行者“先实现后倒补授权”的权利；没有本次采用，当前只读设计已交付，依赖新协议的实施暂停。

下一PG边界fixture按实际采用上限派生，不能把旧80门的79样本照搬作新100门。新99临界的可达三活动计数为47／28／24，两provider竞争A1最后一个合法slot，实际生产同一PG总锁／SUM／预扣COMMIT决定输赢；纯TESTONLY库与未来收费normal根分离，前者不得冒充真实支出或耗尽后清零作付费库。原80配置兼容证据在其原身份层复用。

采用只使上述开发与条件预算上限生效，不立即付费。真实Q仍待新协议独审、实际正常实例与固定三活动、现行官方能力／严格返回身份、token／framing／reasoning／含税币种／账号条款、合法完整剩余矩阵和服务器secret loader非敏感readiness全部核齐，由主控另写首次启用回执；72小时只从未来真实启用T0起。每活动24小时／3600秒、finite_calculate≤8、预览3次／180秒等原限制不放宽。所有收费失败和旧历史照留，无借新grant／数据库重置许可。

原S有限成果及D01—D04仍关闭，旧source frozen／selector永久readonly、六旧对象保持。用户库／本人资料外发、Git提交／推送／发布、依赖安装均未由此获得授权。仓库origin沿用户指定的https://github.com/shspic/RetroLume-agent，公开范围与发布另按实际门槛处理。

本次需确认来自公共AGENTS第二章关于改变公开接口、主要模型／服务、权限及重大费用要有对应决定的要求，也来自本项目锁定模式的既有AP2两候选与80／20边界。原80／20不重问；只对这份新增差异作一次决定。必要输入、成本和代价已具体列明，无需用户发送密钥或数据库凭据。
'''
assert '*' not in proposal_text
write(proposal, proposal_text, True)

work_text = f'''# TASK119/R113主控验收，设计交付通过，采用包待用户决定

{now}，Codex编排Agent。真实结果58870字节／2d10d08b…096346与执行回执一致；主控重新核7规则、36输入、10产物及回执报告共54组身份，零漂移。A—D、协议索引、四条未执行推演、有限公开官方事实、逐动作矩阵和采用包均已保存。按本卡只读设计合同验收通过，不把设计视为已实现／行为通过。

调度已真实返回。运行记录产品import／tests／compile／build／PG／SQL／Docker／业务Job／API／Browser／provider／费用／Git写均0；metadata保守85.6420866秒／1200，官方查询8／8、有效响应15／16，22读取尝试含7失败，原读取错误／截断保留。原工程81失败和旧账没有改动，也未实时检查六旧对象状态。本轮审阅不是新增独审或产品取证。

核心取舍为固定授权根下的本机逐请求精确批准＋accepted未领取等待＋原键显式继续。原PG仍为唯一费用权威、零DDL／v1兼容／R01和R02永久只读。完整typed／payload实际bytes与派生来源、失效、COMMIT丢确认、unknown留账都有明确合同。approval_id排除自身摘要、共享policy lease释放后再取写锁落结果两处按adoption-proposal.md澄清，下一实施须真正验证，不能只补文字冒PASS。

主控独立逐行加总为39模型＋39query＋2索引＋1HTML＝81次／20250000预留，学习39、面试24、补证18；原80／20和补证16／4不可容纳。官方当前更新确认旧deepseek-chat已公告淘汰、现候选deepseek-flash，不代表实际账号可用。token／framing／reasoning／税／账号及严格返回身份未知继续关门，不能以条件价格反算冒已核报价。

原报告称主控可自行采用新operator／wire／等待等协议不作为扩大权限的依据。按锁定AGENTS/WORK实际影响，本次新增批准权限／协议响应、新模型及预算调整一次交用户决定。具体候选为零DDL完整Q v2、deepseek-flash及保留原thinking/字节/10秒、原固定三个UUID下100次／25元（48／28／24，12／7／6元）。只比原条件许可新增20次和5元上限；未采用、未激活、未创建新付费根。不用恰好81且零失败余量的上限制造下一轮必停；实际路径超限仍停止。

唯一提案在DocuN/evidence/TASK-119/orchestration-acceptance-20261018/adoption-proposal.md，未经确认不将其写成有效最终需求或可用grant。批准后一次完整工程，再同一独审归属集中增量；未批准时暂停依赖新边界的实施，保留S关闭、Q冻结。无新TASK占号／派发，无需此刻用户运行命令、发key或释放内存。STEP018整体／STEP019／STEP020／M1／项目未通过。原报告、design产物及旧裁定均不改，本轮只写主控核证／共享文档。
'''
assert '*' not in work_text
write(work, work_text, True)

arch_prefix = f'''# 架构动态文档

文档v1.45，2026-10-18，Asia/Shanghai。需求v1.3、执行动态v2.72、task_model/07。以下v1.44原字节保留；本轮不采用新权限／模型／费用。

## Q前置设计已交付，具体增量采用仍待决定

{now}。TASK119/R113完成只读A—D合同并经主控54组身份／逐动作算术核证，设计交付通过。拟采用固定v2根、精确本机operator逐请求批准、原accepted未领取等待及原键显式继续，零DDL，原PG锁内roster SUM和预扣COMMIT保持金融唯一权威。v1及协议3／原4、永久只读恢复和S有限成果沿用，不重新打开原四项缺陷。

候选新增ControlHub q事件／私有artifact／operator权限与wire等待投影，属尚待用户明确采用的新边界；approval摘要无自引用，发送共享policy临界段先释放、结果按现资格和写锁提交，禁止锁升级死等，具体见TASK119主控提案。当前没有实现／新配置／新grant／新库／新资源。

DeepSeek官方公告／更新可支持将已淘汰deepseek-chat改候选deepseek-flash，embedding-3／512不变；公开模型/价格事实不等于账号/计量/税/返回身份验证。矩阵81次／20.25元预留且补证18次超16，原80／20无法完整覆盖；新建议100／25、固定分额48／28／24（12／7／6元）只是待批准提案，不新增可花余额。各项启用门／72h未来T0／未知不发仍在。

Q及STEP018整体未通过，有限S关闭和历史控制不通过并存。旧source frozen／selector永久readonly／旧六对象不变，用户库、真实个人资料外发与Git远程写入／发布仍未授权。本轮主控只读核证、有限公开官方来源抽核及文档维护，未做产品运行或测试。

## 以下为v1.44及更早历史

'''
state_prefix = f'''# 执行动态文档

文档v2.72，2026-10-18，Asia/Shanghai。唯一总状态账；需求v1.3、架构v1.45、task_model/07。以下v2.71原字节保留。

## TASK119/R113已返回并通过设计验收，新增采用包待用户决定

{now}。用户已带回119设计包；真实结果58870字节／2d10d08b…096346与保存回执一致，7规则／36输入／10产物／报告回执共54组重新核证零漂移。TASK119调度已返回，验收通过限A—D只读设计／公开事实及矩阵交付；未实现、未验证产品，Q冻结。S有限功能／工程证据验收关闭不重开，TASK117总体部分通过、旧执行控制不通过及81失败照留。

119本轮metadata保守85.6420866／1200秒、官方查询8／8、有效文档15／16，22尝试含7抓取失败；产品import/test/compile/build/PG/SQL/Docker/Job/API/Browser/provider/费用/Git写全0，无新持有产品资源，未查询旧六对象实时状态。原117账及所有原件保持，主控本轮没有接管实现或新独审，只做核证与有限官方三页抽核。

完整请求后继未知问题收敛为零DDL的固定v2根＋本机operator逐请求批准＋原键显式继续；主控明确无自引用摘要及发送共享锁／结果写锁时序。私有批准权限、wire／等待响应为新边界，需要对应采用，不因报告自述自动生效。原PG费用权威和固定锁／roster保留，unknown／未送预留不退，不借换根／活动／库清账。

原模型候选已被官方公告淘汰，现建议deepseek-flash；矩阵独立合计81次／20.25元预留，补证18次超过原16分额。因此保存一个合并待批准提案：Q v2实施＋候选更换＋总上限100次／25元及固定三活动48／28／24次、12／7／6元。比原80／20只增加20次和5元上限，非再发25元；旧13元耗尽不恢复。提案见DocuN/evidence/TASK-119/orchestration-acceptance-20261018/adoption-proposal.md。用户尚未决定，正式需求v1.3不变；不发依赖许可尚缺的工程卡，不预占120/R114，不虚记已转交／开始。

采用后沿原117/119 A+工程窗口一个完整成果实现／零外发PG组合／最终bundle，稳定后原118独审归属只核实际新增权限及传播，不全量重做旧审。当前公开事实／真实账号／token/framing/reasoning/税／严格返回身份／完整合法剩余矩阵及PG组合证均未替代实际启用门；未来主控启用回执前provider费用仍0、72h未起。若不采用新额度，原80／20条件批准仍有效但本矩阵不能启用，不擅自降Must。

STEP018整体／STEP019／STEP020／M1／项目未通过，source frozen／selector永久readonly及旧六对象保持。GitHub沿既有origin，没有commit/push/发布执行。主控证据、提案、旧共享原字节及读回证明在DocuN/evidence/TASK-119/orchestration-acceptance-20261018。CHG1504—1508，下一1509。当前仅待这一份新增差异决定，不重问原80／20或已完成S。

## 以下为v2.71及更早历史

'''
assert '*' not in arch_prefix and '*' not in state_prefix
write(arch, arch_prefix.encode('utf-8') + before[arch])
write(state, state_prefix.encode('utf-8') + before[state])
entries = [
    (1504, 'DocuN/results/TASK-119-work-decision.md', '核证设计交付通过，54身份及81/分额实算，采用与启用分层。'),
    (1505, 'DocuN/evidence/TASK-119/orchestration-acceptance-20261018/adoption-proposal.md', '具体一次增量决定：Q v2权限／模型候选／100次25元建议，保留原边界与两处实施澄清。'),
    (1506, 'DocuS/架构动态文档.MD', 'v1.45登记设计成果与尚未采用的新授权／候选／额度，不修改产品或正式需求。'),
    (1507, 'DocuS/执行动态文档.MD', 'v2.72将119登记已返回／设计验收通过，待具体采用，未预占或派发下卡。'),
    (1508, 'DocuN/evidence/TASK-119/orchestration-acceptance-20261018', '核证记录、共享旧原字节、提案及保存读回复核，原工程／设计证据保持。'),
]
addition = '\n' + '\n\n'.join(f'- CHG-{n}，{now}，Codex编排Agent，{path}。{reason}' for n, path, reason in entries) + '\n'
write(changes, before[changes] + addition.encode('utf-8'))
save_json('verification.json', {
    'at': now, 'task': 'TASK-119', 'R': 'R-113', 'checks': verified, 'count': len(verified), 'mismatches': [],
    'totals_recomputed': totals, 'by_activity_recomputed': by_role,
    'original_roster': matrix['roster'], 'design_delivery_accepted': True,
    'new_adoption_approved': False, 'Q_activated': False, 'new_task_registered': False,
    'main_runtime_or_product_test_or_Git_write': 0,
    'public_source_spot_check': {'tool': 'web open', 'requests': 3,
        'urls': ['https://api-docs.deepseek.com/news/news260424/', 'https://api-docs.deepseek.com/updates/',
                 'https://api-docs.deepseek.com/zh-cn/quick_start/pricing/'],
        'confirmed_scope': '官方公告淘汰旧候选及更新使用deepseek-flash；不证明账号、严格返回身份和完整计费边界',
        'API_or_account_or_provider_calls': 0},
    'unverified_shared_lock_lifetime': '实施澄清K2非运行结论，必须在新成果验证',
    'operator_OS_and_logical_authority': '部署信任边界明确，不冒充已证隔离',
})
for path, expected in protected.items():
    assert identity(path) == expected, str(path)
for path in [state, arch]:
    assert path.read_bytes().endswith(before[path]), str(path)
assert changes.read_bytes().startswith(before[changes])
assert not (ROOT / 'DocuN/tasks/TASK-120.md').exists()
save_json('save-proof.json', {
    'saved_at': datetime.now(timezone(timedelta(hours=8))).isoformat(), 'result': 'SAVED_AND_READ_BACK',
    'versions': {'state': 'v2.72', 'architecture': 'v1.45', 'last_CHG': 1508},
    'documents': [identity(path) for path in [work, proposal, arch, state, changes]],
    'original_shared_suffixes_and_change_prefix_preserved': True, 'protected_count': len(protected),
    'protected_mismatches': [], 'accepted_scope': 'TASK119 design delivery only',
    'Q_enabled': False, 'proposed_adoption_approved': False, 'task120_registered': False,
    'engineer_original_inputs_reports_ledgers_and_design_artifacts_unchanged': True,
})
print(json.dumps({'result': 'SAVED_AND_READ_BACK', 'design_acceptance': '通过', 'new_package': '待用户决定',
                  'Q_enabled': False, 'protected': len(protected), 'state': 'v2.72', 'architecture': 'v1.45',
                  'last_CHG': 1508, 'new_task_dispatched': False}, ensure_ascii=False))
