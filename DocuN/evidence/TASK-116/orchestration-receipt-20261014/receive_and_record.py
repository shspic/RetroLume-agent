"""只核设计原件/源码身份并串行登记主控裁定，不导入或执行产品。"""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import hashlib
import json
import re

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent').resolve()
OUT = Path(__file__).resolve().parent
DESIGN = ROOT / 'DocuN/evidence/TASK-116/design'
WORK = ROOT / 'DocuN/results/TASK-116-work-decision.md'
ARCH = ROOT / 'DocuS/架构动态文档.MD'
STATE = ROOT / 'DocuS/执行动态文档.MD'
CHANGES = ROOT / 'DocuS/文档变更记录.MD'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def identity(path):
    raw = path.read_bytes()
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def save_json(path, value):
    assert not path.exists(), str(path)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    assert load(path) == value


def prefix(path, value, before):
    assert '*' not in value and not re.search(r'^\|', value, re.MULTILINE)
    path.write_bytes(value.replace('\n', '\r\n').encode('utf-8') + before)
    assert path.read_bytes().endswith(before)


assert OUT.is_relative_to(ROOT)
for path in (OUT, WORK.parent, ARCH.parent):
    assert path.resolve().is_relative_to(ROOT)
assert not (OUT / 'received.json').exists(), '已有回收不得重新覆盖'
before = {p: p.read_bytes() for p in (WORK, ARCH, STATE, CHANGES)}
assert '文档v1.32' in before[ARCH].decode('utf-8-sig').splitlines()[2]
assert '文档v2.56' in before[STATE].decode('utf-8-sig').splitlines()[2]
numbers = [int(x) for x in re.findall(r'^- CHG-(\d+)', before[CHANGES].decode('utf-8-sig'), re.MULTILINE)]
assert numbers[-1] == 1384 and 1385 not in numbers

at = datetime.now(timezone(timedelta(hours=8))).isoformat()
delivery = load(DESIGN / 'delivery.json')
artifact_checks = []
for row in delivery['artifacts']:
    path = ROOT / row['path']
    actual = identity(path)
    assert actual == {k: row[k] for k in ('bytes', 'sha256')}, str(path)
    artifact_checks.append({'path': row['path'], **actual, 'matches_delivery': True})

source_checks = []
sources = load(DESIGN / 'source-identities.json')
assert sources['count'] == len(sources['records']) == 66
for row in sources['records']:
    path = Path(row['path'])
    if not path.is_absolute():
        path = ROOT / path
    actual = identity(path)
    assert actual == {k: row[k] for k in ('bytes', 'sha256')}, str(path)
    source_checks.append({'path': row['path'], **actual, 'matches_read_identity': True})

rules = load(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
rule_checks = []
for row in rules:
    actual = identity(Path(row['absolute_path']))
    assert actual['sha256'] == row['sha256'], row['absolute_path']
    rule_checks.append({'path': row['absolute_path'], **actual, 'matches_locked': True})

receipt = load(DESIGN / 'receipt.json')
assert receipt['permit'] == 'TASK-116-STEP018-DESIGN-20261014'
assert receipt['status'] == 'design_completed'
assert receipt['conservative_active_seconds'] <= receipt['active_limit_seconds']
assert receipt['new_runtime_resources'] == 0
assert receipt['current_product_test_runtime_network_fee_git_write'] == 0
consistency = load(DESIGN / 'consistency.json')
assert consistency['status'] == 'CONFORMING'
assert consistency['full_consistency_runs'] == 1
assert consistency['targeted_corrections'] == 1

protected = {}
for name in ('AGENTS.md', 'DocuS/原始需求文档.MD', 'DocuS/最终需求文档.MD',
             'DocuN/tasks/TASK-116.md', 'DocuN/results/TASK-114-result.md',
             'DocuN/results/TASK-115-result.md', 'DocuN/results/TASK-116-result.md'):
    protected[name] = identity(ROOT / name)
for p in DESIGN.rglob('*'):
    if p.is_file():
        assert p.resolve().is_relative_to(ROOT)
        protected[p.relative_to(ROOT).as_posix()] = identity(p)

backup = OUT / 'before-documents'
backup.mkdir(exist_ok=False)
for path, raw in before.items():
    target = backup / path.name
    target.write_bytes(raw)
    assert target.read_bytes() == raw

findings = {
    'TASK': 'TASK-116', 'R': 'R-110', 'STEP': '018', 'received_at': at,
    'received_basis': '用户返回设计结果路径，随后明确继续；原报告及落盘原件实际可读',
    'task_dispatch_state': 'received_and_returned',
    'design_acceptance': 'passed_document_delivery_B_level',
    'implementation_adoption': 'pending_AP1',
    'paid_egress_adoption': 'pending_AP2',
    'product_implementation_and_validation': 'not_run',
    'evidence_note': '原一致性检查及其一次有据修正直接复用；主控核对A—D、关键原始源码与身份，不重跑作者脚本或产品测试',
    'artifacts': artifact_checks, 'sources': source_checks, 'rules': rule_checks,
    'executor_control': {
        'permit': receipt['permit'],
        'conservative_active_seconds': receipt['conservative_active_seconds'],
        'active_limit_seconds': receipt['active_limit_seconds'],
        'remaining_seconds_sealed_not_runtime_permission': receipt['remaining_active_seconds'],
        'first_clock_gap': '首工具缺同步点，原QPC/UTC前保守扣120秒，不追认精确首点',
        'full_document_consistency_runs': 1, 'targeted_document_corrections': 1,
        'product_test_service_network_fee_git_write': 0,
        'assessment': '原始文件支持设计按期交付；未复演会话或声称文件hash能证明全部执行行为'
    },
    'reviewed_direct_code': [
        'backend/migrations/008_activity_tool_budget.sql model/tool shape',
        'backend/migrations/013_data_exit.sql profile and role/write guards',
        'backend/app/activities/repository.py record_outcome invalid-generation/closed gate',
        'backend/app/memory/repository.py _memory_require_call',
        'backend/app/activities/interview_repository.py _interview_domain/_interview_require_call/_interview_gate',
        'backend/app/retrieval/evidence.py existing fragment/terms carrier'
    ],
    'implementation_clarifications_not_new_authority': [
        '晚到事实沿现有UNKNOWN纪律；失效后不得新增received业务正文/向量。此前已COMMIT事实可回查但抑制当前资格，不将设计007事实表述解释成放宽record_outcome。',
        '向量hash应定义于实际存储且可恢复的规范数值表示；pgvector浮点量化/序列化必须在实现中收敛，PG读取、007、R02恢复逐项核对，不拿供方原double文本hash假冒存储roundtrip。',
        '新grant仅受信create绑定、不可重绑；新model/embedding共核该grant所有活动预留，旧UNKNOWN/费用不释放，tool零费用分支保留。',
        '候选provider/model/512维及价格条款均未实时核；本次不作当前能力或报价承诺，未核前真实网络/费用为0。'
    ],
    'main_product_execution': 0, 'main_new_runtime_resources': 0,
    'no_independent_implementation_audit_claim': True,
    'protected': protected,
    'remaining': 'AP1/AP2需对应决定；TASK117未占号/未派发；STEP018实施、019集中安全验收、020本人自用交接未完成。'
}
save_json(OUT / 'received.json', findings)

work_text = f'''# TASK116/R110 — STEP018集成合同设计交付验收

{at}，Codex编排Agent。用户已返回TASK116结果并要求接续；本轮核对原合同A—D、实际调用图、28个有限场景、完整未编号实施草案和两个具体采用包。十二交付身份、66个读入文件及七条锁定规则逐项匹配；不重算整仓243项，不重跑设计检查/产品。原结果与全部设计材料、原114/115和需求原字节保留。

任务交付验收通过，仅B级文档成果。调度改为真实接收/执行/返回、设计成果已验收；TASK116不是未完成实现，也不需要为阶段设计另加一次独立代码审计。原一致性十三项、首次三个函数归属标注不符及一次定向修正已留原件，最终原件可复用；首mono缺同步点/保守120秒与活动5133.7887266/7200及剩2066.2112734封存，未用余额不转执行权。产品/服务/PG/SQL/API/Windows/Browser/build/provider/网络/费用/Git写0是本卡边界及执行者原始登记；主控只作身份、文档/源码核证，不声称hash独自证明全部会话行为。

## 设计结论与采用状态

推荐方案在既有PG权威、原007原子正文、领域命令/CAS/四账、Windows监督和固定G11宿主上集成两链。向量能力仍未实现，terms.v1已有；旧面试v1明确禁止记忆，新v2是新增采用范围。新主要模型/公开接口/权限和费用不能由设计完成、重复推荐或本次一般继续自动生效。

AP1待用户采用。主要增量为014、三检索表及activities可空grant摘要、新embedding kind/typed gateway/wire v4且兼容v3、精确cosine加词项RRF、learning.v2/teaching.v3/interview.v2及可选低信任记忆、R02精确权限/快照/删除/恢复；原001—013与R01旧包不改。新model/embedding沿原持久次数/费用/运行时长，新收费grant不可重绑并跨固定活动合计，不建第四张通用预算表。旧tool的NULL token/request列及零费用不被统一正值约束破坏。

同一正常持久库重开后GET事实再明确继续才算连续性；R01/R02恢复副本均永久只读，不借集成开放执行。本机仍Windows API/SUP、Compose PG、动态预览；无新Agent框架/SDK/常驻renderer、无Web Docker socket，未来Linux/Nginx公开部署不增为首版门。前置有限切片通过仍有效，不重新开发或重审。

AP2待用户明确范围，建议和AP1一次决定，实际启用晚于新边界稳定独审及官方现行能力/价目/条款核实。仅冻结合成资料必要片段，候选DeepSeek chat和智谱embedding-3/512，固定三个新活动共享最多80次、最多人民币20元新总额，含失败/超时/UNKNOWN；单次预留0.25元且最坏费用经现行依据核算不超预留，无隐式重试，不借旧13元或换活动清账。72小时应由未来已批准grant实际生效时起算，不能将本次询问日当收费起点。无真实履历/学习原件/用户库或生产迁移权限；本人真实数据外发须另有对应数据范围。候选不满足必需能力时关闭相关部分并交准确变更，不静换供应商/维度或延时限。

## 后续实施的必要解释

晚到事实严格沿原record_outcome纪律。当前资格已失效只能UNKNOWN诊断，不能新增received正文/向量；此前已COMMIT的结果可按持久事实回查并抑制当前展示/投影。设计中007事实的概述不解释为放宽资格。

向量规范hash应对应实际存储数值表示，实现须处理pgvector浮点量化与序列化；007、数据库回读、R02恢复不能用不同数值文本互相冒认。具体编码是工程细节，纳入既有P01/P03与向量身份验证，不另造前置研究卡或增加新服务。

旧model/tool/domain profile/hash及R01可读分支保持，新类型绝不作为领域/HTML父。grant在受信create绑定后不可变，预留总量核门与每活动准入共同执行；全部新入口继续session/DataContext/mutation gate，GET不出站。原失败与未知不改写。

## 下一步与门槛

AP1采用后直接给原A+工程窗口一个完整实施成果卡，沿草案涵盖两链、014/R02、检索、正常同库续作、本机启动文档、有限验证与普通修复，不拆准备/单跑/修夹具卡。AP2未就绪只冻结真实出站，合成实现可以进行；已授权常规接线无须再次审批，但本阶段共同依赖新profile时不为躲采用而另做平行替代。

稳定完整候选后集中独审新类型/权限/账本/R02和最终bundle，足够原证据复用；原工程窗在AP2成立后补真实合成语义，原独审窗只增量复核。STEP018全Must适用证据齐备再裁定，随后STEP019集中余项安全/一致性、STEP020本人本机自用交接。没有承诺固定剩余卡数，也不把文档完成写项目完成。

当前TASK117/R111未占号，未派发/未执行。真正关键缺口仅AP1采用与AP2新增合成外发/费用决定，不索取密钥、不要求清内存或启动Docker。主控无在途运行，原窗已交回，旧运行许可/预算不恢复。只读证据和正式变更在DocuN/evidence/TASK-116/orchestration-receipt-20261014。

## 以下为原只读设计许可历史

'''
prefix(WORK, work_text, before[WORK])

arch_text = f'''# 架构动态文档

文档v1.33，2026-10-14，Asia/Shanghai。需求v1.2、执行动态v2.57、task_model/07；以下v1.32历史原字节保留。

## STEP018集成设计已验收，主要模型与外发采用包待决

{at}。TASK116/R110完整A—D只读成果已核证，十二交付身份、66读入身份、七锁定规则相符。现有terms.v1、领域命令/007/CAS/四账/Windows监督/固定G11/013精确R01已按源码与原验收边界辨明；设计交付通过不等于新实现、真实服务或完整STEP018通过。

推荐AP1为014三检索表及活动可空grant摘要、受控embedding kind和wire v4/v3兼容、同space精确cosine与词项RRF、learning.v2/teaching.v3/interview.v2低信任可选记忆、R02增量快照/清理/永久只读恢复。旧001—013、model/tool行及R01原包不改；旧tool零费用/NULL形状必须保留，grant不可重绑，新model/embedding共核跨活动累计。AP1待用户采用，当前没有任何新增模型/权限已经生效。

AP2是最多20元/80次、只发送冻结合成必要片段的未来许可建议，非当前授权或现行报价。候选现行能力/价目/条款尚未核，新边界集中独审未完成前真实收费关闭；不含个人资料或用户库。0.25元仅安全预留提案，最坏成本核不过就拒发送；旧13元/失败/UNKNOWN不折回。

实施时晚到结果仍遵原失效仅UNKNOWN、关门不新增正文纪律；向量身份按实际存储规范数值与R02往返一致收敛。正常同库重开和永久只读恢复继续分开，Windows/Compose/动态预览复用，无新平台/常驻服务或公开Linux-Nginx交付承诺。原114/115有限STEP017关闭及全部历史有效，完整NFR005/STEP018—020/M1/项目仍未通过。

## 以下为v1.32及更早历史

'''
prefix(ARCH, arch_text, before[ARCH])

state_text = f'''# 执行动态文档

文档v2.57，2026-10-14，Asia/Shanghai。唯一总状态账；需求v1.2、架构v1.33、task_model/07。以下v2.56历史原字节保留。

## TASK116设计已真实返回并验收，实施采用与合成付费待决定

{at}。TASK116/R110已经原A+工程窗接收/执行/返回；报告10764字节/1a0da889b0636437bf6652669b35d4911fefcbdbb77213a53c41b641b0b1949a。主控实读A—D、地图/样本/采用包/卡草案与关键原源码，核十二交付身份、66读入身份、七公共规则相符；设计文档B级交付验收通过。不是仅凭回传自述，也未重跑产品或作者一致性脚本。

一次文档检查十三项最终符合，三个函数标注的初始失败与一次定向修正原件保留；首mono缺同步点，原120秒保守扣时与5133.7887266/7200活动、剩2066.2112734封存。新产品/测试/PG/SQL/API/Windows/Browser/容器/build/provider/联网/费用/Git写登记0、无新资源；主控核证不冒完整会话取证。TASK116调度已返回/设计验收通过，执行窗无待回结果，旧剩额不变产品执行权。

STEP018状态为完整集成合同已完成，实施尚未开始/未验证。AP1主要数据/公开接口/权限包待用户采用，含014/三检索表+活动grant摘要、embedding/v4与旧v3兼容、hybrid、新领域profile及面试可选低信任记忆、R02保R01。AP2仅冻结合成必要片段最多80次/人民币20元新余额，待明确许可、现行服务/条款/价额核对及新增边界稳定独审，未开启真实费用/外发；不含本人资料/用户库。两个决定可一次答复，不为常规实现重索授权。

采用后下一原A+工程窗一张完整实施卡，普通实现/测试/修复在卡内连续完成，再集中独审高风险稳定成果。真实合成语义在相应许可和审计门就绪后补，原独审窗口只审增量；STEP019整体安全与一致性、STEP020本人自用交接仍依前置推进。TASK117/R111未占号/未保存/未派发，不虚报已启动；未确定采用前不生成可执行后续卡。

原114/115有限STEP017已验收/四DEF关闭维持；正常同库继续与R01/R02永久只读恢复不混称。所有原失败、旧根/启动/PG/Windows/API/Browser/build/时间、G11/25/UNKNOWN/R60/count1/13元/626.566及所有Must仍保留，不因设计关闭清零。旧资源停止按既有精确原件继承，本轮未重启或借旧runner/额度，未宣完整阶段/项目完成。

主控仅文档/字节/源码核证及共享维护，产品运行0。裁定为DocuN/results/TASK-116-work-decision.md，回收/源码和规则身份/旧文档/保存证明在DocuN/evidence/TASK-116/orchestration-receipt-20261014。CHG1385—1390，下一1391。原始/最终需求、执行者结果、原证据、公共库与产品未改。

## 以下为v2.56及更早历史

'''
prefix(STATE, state_text, before[STATE])

entries = [
    ('DocuN/evidence/TASK-116/orchestration-receipt-20261014/received.json', '十二交付/66读入/七规则与关键源码核证，设计交付通过，运行和实际采用分别保留。'),
    ('DocuN/results/TASK-116-work-decision.md', '主控设计验收、AP1/AP2最少具体待决和晚到/存储身份解释，原许可历史保留。'),
    ('DocuS/架构动态文档.MD', 'v1.33登记推荐集成增量尚未采用，新旧profile/权限及真实付费边界，不签实现。'),
    ('DocuS/执行动态文档.MD', 'v2.57真实返回/设计通过、实施及费用采用待决，旧预算/成果/未知保留，117未占号。'),
    ('DocuN/evidence/TASK-116/orchestration-receipt-20261014/before-documents', '原Work/架构/执行/变更原字节保留，用户需求和原证据不改。'),
    ('DocuN/evidence/TASK-116/orchestration-receipt-20261014/save-proof.json', '保存复读与旧后缀/源/规则/报告保护、CHG连续核对，不触产品运行。'),
]
tail = ''.join(f'\r\n- CHG-{1385+i}，{at}，Codex编排Agent，{path}。{detail}\r\n'
               for i, (path, detail) in enumerate(entries))
CHANGES.write_bytes(before[CHANGES] + tail.encode('utf-8'))
assert CHANGES.read_bytes().startswith(before[CHANGES])
new_numbers = [int(x) for x in re.findall(r'^- CHG-(\d+)', CHANGES.read_text(encoding='utf-8-sig'), re.MULTILINE)]
assert new_numbers == numbers + list(range(1385, 1391))

for name, expected in protected.items():
    assert identity(ROOT / name) == expected, name
for row in rule_checks:
    assert identity(Path(row['path'])) == {k: row[k] for k in ('bytes', 'sha256')}
assert not (ROOT / 'DocuN/tasks/TASK-117.md').exists(), '不抢占下一未授权卡'
save_json(OUT / 'save-proof.json', {
    'utc': datetime.now(timezone(timedelta(hours=8))).isoformat(),
    'status': 'saved_readable_document_acceptance_pending_adoption',
    'files': [{'path': str(p), **identity(p)} for p in (WORK, ARCH, STATE, CHANGES, OUT / 'received.json')],
    'history_bytes_preserved': True, 'protected_unchanged_count': len(protected),
    'source_read_identity_match_count': len(source_checks),
    'locked_rules_match_count': len(rule_checks),
    'changes': list(range(1385, 1391)),
    'TASK117_exists': False, 'main_product_runtime': 0,
    'AP1_adopted': False, 'AP2_authorized': False,
    'original_requirements_results_evidence_rules_products_unchanged': True
})
print(json.dumps({'result': 'SAVED_AND_READABLE', 'work': str(WORK),
                  'artifact_checks': len(artifact_checks), 'source_checks': len(source_checks),
                  'rules': len(rule_checks), 'protected': len(protected),
                  'architecture': 'v1.33', 'execution': 'v2.57',
                  'last_CHG': 1390, 'pending': ['AP1', 'AP2'], 'product_runtime': 0}, ensure_ascii=False))
