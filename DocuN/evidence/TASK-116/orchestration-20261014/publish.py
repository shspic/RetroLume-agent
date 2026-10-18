"""关闭已通过的有限STEP017并登记/保存STEP018只读集成合同卡，不执行产品。"""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import hashlib
import json
import re

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
OUT = Path(__file__).resolve().parent
RECEIVED = ROOT / 'DocuN/evidence/TASK-115/orchestration-final-receipt-20261014/received.json'
CARD = ROOT / 'DocuN/tasks/TASK-116.md'
WORK114 = ROOT / 'DocuN/results/TASK-114-work-decision.md'
WORK115 = ROOT / 'DocuN/results/TASK-115-work-decision.md'
WORK116 = ROOT / 'DocuN/results/TASK-116-work-decision.md'
ARCH = ROOT / 'DocuS/架构动态文档.MD'
STATE = ROOT / 'DocuS/执行动态文档.MD'
CHANGES = ROOT / 'DocuS/文档变更记录.MD'


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


def prefix(path, text, original):
    path.write_bytes(text.replace('\n', '\r\n').encode('utf-8') + original)
    assert path.read_bytes().endswith(original)


at = datetime.now(timezone(timedelta(hours=8))).isoformat()
day = '2026-10-14'
received = load(RECEIVED)
assert not CARD.exists() and not WORK116.exists(), '新号已占用时不覆盖'
old = {path: path.read_bytes() for path in (WORK114, WORK115, ARCH, STATE, CHANGES)}
assert '文档v1.31' in old[ARCH].decode('utf-8-sig').splitlines()[2]
assert '文档v2.55' in old[STATE].decode('utf-8-sig').splitlines()[2]
numbers = [int(value) for value in re.findall(r'^- CHG-(\d+)', old[CHANGES].decode('utf-8-sig'), re.MULTILINE)]
assert numbers[-1] == 1372 and 1373 not in numbers
contract = (OUT / 'effective-contract.md').read_bytes()
text = contract.decode('utf-8-sig')
assert '*' not in text and not re.search(r'^\|', text, re.MULTILINE)
for required in ('目标与交付', '项目、规则、授权与窗口', '当前事实与最小充分上下文',
                 'A —', 'B —', 'C —', 'D —', '允许、禁止与本卡资源', '完成、停止与回传',
                 'TASK116/R110/STEP018', '7200秒', '本卡零产品/服务/测试/实验运行'):
    assert required in text, required

protected = {}
for row in received['current']:
    path = ROOT / row['path']
    if row['exists']:
        expected = {key: row[key] for key in ('bytes', 'sha256')}
        assert identity(path) == expected, str(path)
        protected[str(path)] = expected
    else:
        assert not path.exists()
for row in received['audit_evidence']:
    path = Path(row['path'])
    assert identity(path) == {key: row[key] for key in ('bytes', 'sha256')}
    protected[str(path)] = identity(path)
for row in received['rules']:
    path = Path(row['absolute_path'])
    assert identity(path)['sha256'] == row['sha256']
    protected[str(path)] = identity(path)
for path in (ROOT / 'AGENTS.md', ROOT / 'DocuS/原始需求文档.MD', ROOT / 'DocuS/最终需求文档.MD',
             ROOT / 'DocuN/results/TASK-114-result.md', ROOT / 'DocuN/results/TASK-115-result.md',
             ROOT / 'DocuN/tasks/TASK-114.md', ROOT / 'DocuN/tasks/TASK-115.md',
             ROOT / 'DocuN/evidence/TASK-114/implementation/control/receipt.json',
             ROOT / 'DocuN/evidence/TASK-114/implementation/control/events.jsonl',
             ROOT / 'DocuN/evidence/TASK-113/design/revision-01/current-contract.md'):
    protected[str(path)] = identity(path)
assert identity(ROOT / 'DocuN/results/TASK-115-result.md') == {key: received['report'][key] for key in ('bytes', 'sha256')}
backup = OUT / 'before-documents'
backup.mkdir(exist_ok=False)
for path, raw in old.items():
    (backup / path.name).write_bytes(raw)

permit = {
    'TASK': 'TASK-116', 'R': 'R-110', 'STEP': '018',
    'permit': 'TASK-116-STEP018-DESIGN-20261014', 'issued_at': at,
    'authorization': '用户已采用自有应用路线并持续要求推进；017有限闭环通过后，收敛下一完整集成实施合同',
    'deliverable': 'A—D完整唯一推荐合同、实际接线差异、有限验收与下一实施卡草案、最少真实待决',
    'design_only': True, 'dispatch_confirmed': False, 'execution_started': False,
    'new_activity_seconds_max': 7200, 'save_reserve_seconds': 600,
    'calendar_seconds_from_actual_receipt': 172800,
    'first_tool_clock': '接收者实采UTC/mono，缺失保守说明，签发时间不冒接收',
    'new_limits': dict.fromkeys(['product_run', 'tests', 'experiments', 'PG', 'SQL', 'Redis', 'Docker',
                                'Compose', 'API', 'Browser', 'Native', 'preview', 'compile', 'typecheck',
                                'build', 'Embedding', 'provider', 'fees', 'public_network', 'Git_write'], 0),
    'read_only_metadata_allowed': '文件hash/JSON/有限AST/只读Git元数据，不import产品；不读私配/秘密',
    'write': [str(ROOT / 'DocuN/results/TASK-116-result.md'),
              str(ROOT / 'DocuN/evidence/TASK-116/design')],
    'prior_tasks_not_reauthorized': ['TASK114', 'TASK115', 'G3—G11及所有旧runtime/runner'],
    'prior_budget_facts': {'engineering_counts': received['engineering_counts'],
                            'audit_active_cumulative_seconds': received['audit_delivery']['active_cumulative_seconds_conservative'],
                            'old_experiment_fee_reserve_yuan': 13, 'old_fee_reserve_exhausted': True},
    'key_scope_limit': '设计不重开已验收模块，不给只读恢复副本开写，不赋真实账号/外发/付费权限',
    'required_future_audit': '完整集成稳定后的适用集中独审/STEP019，不每个接口重复审计',
}
save('design-permit.json', permit)
save('window-assignment.json', {
    'created_at': at, 'TASK': 'TASK-116', 'R': 'R-110', 'grade': 'A+',
    'window': '优先原TASK114工程窗口（上一续作03），新完整成果转只读STEP018设计',
    'previous_actual_identity': 'Codex desktop / GPT-6，实际接收者如实登记',
    'reason': '跨业务主链/检索/外部能力/预算/连续性与本机集成，需要增强推理；复用同窗未变上下文',
    'no_transfer_of_old_runtime_permission': True, 'not_independent_audit': True,
    'manual_transfer': True, 'dispatch_confirmed': False, 'no_subagents_or_parallel_writers': True,
})

work115 = f'''# TASK115独立终审验收通过，有限STEP017-P1关闭

{at}，Codex编排Agent。review-02报告85761字节/1d30787020b0958215539109724fe2ec948ae4157c4be9146855294a51a872ca，原61253字节后缀完整；主控核1199保护登记、29审计原件、243 current和七锁定规则相符。原窗口独立性带主控摘要附带暴露披露接受，实际源码/原始方法支撑通过，不用摘要证明。

代码/证据/本轮增量控制合格，DEF035/F02同D pin传参与结果资格、DEF036/F03输入版本/计划/范围动作两根因关闭；DEF034/037前轮关闭有效。TASK115/R109调度已返回，验收通过，原集中审查与两次增量完成；不再派重复终审或恢复旧额度。

review-02只读1456.537288秒含最后保守2秒，累计10073.798854/21600，首工具mono缺点/保守300秒扣时与历史失败/超限/UNKNOWN全部保留。新增业务全0，原root3/API3/Browser2/offline125.610/hold14.874不变；旧时间和资源余额不自动续。

结合原有效恢复/引用/权限主链和四P1闭合，主控有限STEP017-P1验收通过。仅数据退出/一致备份/隔离恢复验证/永久只读查看与对应删除一致性；受控PG参数/route UI不冒新增物理PG或真实selector，旧两秒PG只证reading超时。完整NFR005连续执行、STEP018—020和项目/发布未验收，后续新集成另明确合同。

## 以下为原独审历史原字节

'''
prefix(WORK115, work115, old[WORK115])
work114 = f'''# TASK114已验收通过，有限STEP017-P1完整成果关闭

{at}，Codex编排Agent。原115集中独审与review-02终审通过且当前243文件/原件匹配，工程报告90515字节/12985d98…bfdf5原字节保留。TASK114/R108已返回/通过，DEF034—037全部关闭，已采用有限STEP017-P1已完成/已验证，不再开续作04或重跑已充分方法。

通过范围为可读导出、一致备份、隔离副本恢复核对/永久只读查看、删除覆盖/引用与对应控制纪律。正常PG/31域/RootLease/停止主链与最终两项受控参数和route交互按其实际层共同成立；不宣物理驱动挂死、恢复副本重新执行或全产品质量。原source frozen/selector/failed对象、全部报告/失败/数据/卷不改。

工程累计root23/24、Browser7/9且C03门7、build6/7、PG create9/12/success9/9/start37/37、Windows11/12、API8/11、offline205.959/hold487.876、C03活动4495.4211376/C02+C03为13684.1412486，以及C01 9739.953/旧55525.796净unknown保留。自有消费者准确结束，唯一账31资源stopped；余额和runner可读不恢复执行权。

接下来新TASK116/R110优先同工程窗，仅形成STEP018两条完整主链集成实施合同，零产品运行，不继承旧许可、不占旧根、不改产品。原115保持独立并结束，不派新审计。正式总状态与DEF由主控同步；旧G11/25/UNKNOWN/R60/count1/13元/626.566保留，STEP018—020/M-1/项目未通过。

## 以下为原工程历史原字节

'''
prefix(WORK114, work114, old[WORK114])
work116 = f'''# TASK116/R110 — STEP018完整学习与面试集成合同只读设计许可

{at}，Codex编排Agent。用户持续要求推进，有限STEP017-P1已验收关闭，原已确认目标和既有模块继续有效。下一完整成果是两条主链剩余接线、真实能力/持久连续性、本机Compose和验收的唯一最小实施合同A—D；不是重新开发已关闭模块或前置产品实验。

许可TASK-116-STEP018-DESIGN-20261014，A+优先原TASK114工程窗，新TASK/R但不带旧运行权，人工转卡待接收。活动7200含600保存/复读、接收后48h，首工具实际UTC/mono记录；全部产品/测试/服务/SQL/容器/构建/provider/费用/公网/Git写新增0。主控只准备卡，不实际派发或启动。

设计先读真实现状，前置有限切片不冒全部Must已经完成；RAG/Embedding/预算/引用/重开连续性与UI接线按实际函数收敛。已有Compose不重写成从未采用；Windows目标/动态预览/未来Linux/Nginx边界保留，不给永久只读副本开写。真实新模型/接口/依赖/费用/外发或用户数据缺授权才形成最少具体决定包，已有授权不重复审批；即使待决也先完整交付A—D和可转实施草案。

只写DocuN/results/TASK-116-result.md与DocuN/evidence/TASK-116/design，做一次文档覆盖/冲突/路径/追踪检查，不import产品或开前置实验。正式文档/编号/状态/CHG由主控维护。当前完整卡DocuN/tasks/TASK-116.md保存复读后才标待转交，结果尚不存在，不虚报完成或验证。

'''
WORK116.write_bytes(work116.replace('\n', '\r\n').encode('utf-8'))

arch = f'''# 架构动态文档

文档v1.32，{day}，Asia/Shanghai。需求v1.2、执行动态v2.56、task_model/07；以下v1.31历史原字节保留。

## 有限STEP017已验收，进入完整用户流程集成合同

{at}。主控核原115 review-02报告/原件/当前字节与独立性，关闭DEF035/F02、DEF036/F03；DEF034/037前轮关闭有效。TASK114/115完整成果通过，已采用STEP017-P1在数据退出/一致备份/隔离副本核对/永久只读及删除引用范围已完成、已验证。原31域/两FK/两锁序/真实停止闭包和最终pin/输入绑定方法按适用层成立；受控连接不冒物理PG等待，route不冒真实selector，旧PG两秒只证读取阶段过D。

原件/范围/记忆/历史状态/预算/未知保留及私有控制执行权不混入包；源frozen和只读selector不回退，不因任务关闭给副本开写或清旧账。恢复后的持续业务、完整语义/真实provider、STEP018—020/M-1/发布均未通过。

TASK116在既有方向内收敛STEP018完整学习与面试集成合同，识别剩余实际接线和Must、复用G3—G11及数据退出，不先选新平台。检索/Embedding/外发与预算、重开连续性、现有Compose本地集成和Windows/未来Linux-Nginx边界需明确，真正模型/接口/依赖/费用缺授权才提交具体采用包。此为只读设计，架构未采用新实现或新增持久/权限/运行许可。

## 以下为v1.31及更早历史

'''
prefix(ARCH, arch, old[ARCH])

state = f'''# 执行动态文档

文档v2.56，{day}，Asia/Shanghai。唯一总状态账；需求v1.2、架构v1.32、task_model/07。以下v2.55历史原字节保留。

## TASK114/115已验收，有限STEP017关闭；TASK116已登记

{at}。原115 review-02已真实接收/执行/返回，报告85761字节/1d30787020b0958215539109724fe2ec948ae4157c4be9146855294a51a872ca，原61253字节后缀保留。主控核1199保护登记、29本轮审计原件、243 current和七规则相符；原与本轮附带主控摘要暴露已披露、不作通过依据，受限独立性接受。代码/证据/本轮增量执行控制通过，未发现本次具体阻断。

DEF035/F02同Operation加载pin与返回后资格、DEF036/F03策略/文件/计划/范围输入生命周期两P1由主控关闭；DEF034/F01、DEF037/F04前轮关闭有效。本切片无开放P0/P1，TASK114/R108、TASK115/R109调度已返回/验收通过。有限STEP017-P1已完成/已验证，范围为可读数据退出、一致备份、隔离恢复副本核对/永久只读查看及对应删除/引用一致性，不宣恢复副本执行权或完整NFR005/项目通过。

原有效恢复/31域/权限/两FK/RootLease/停止主链与最终三组受控pin、十二Browser route方法按实际层共同支撑。旧2秒PG只抵reading过D、未到发布延迟；新route/连接参数不签真实selector/物理驱动挂死，全部原FAIL/unknown与历史超限保留，不为收尾补全量绿跑。原source frozen/target07 generation1、新C02 target01只读/failed对象和全部卷/记录保持。

审计review-02只读1456.537288（含最后2秒保守余量），累计10073.798854/21600，首mono缺点/保守300扣时和原root3/API3/Browser2/offline125.610/hold14.874保留，新业务全0。工程root23/24、Browser7/9且C03门7、build6/7、PG create9/12/success9/9/start37/37、Windows11/12、API8/11、offline205.959/hold487.876、C03活动4495.4211376/C02+C03合13684.1412486、原C01 9739.953/旧55525.796净unknown全部封存。原31资源账stopped、准确消费者关闭原件保留，本轮无新现场运行；旧余额/卡/runner可读不恢复许可。G11/25/UNKNOWN/R60/count1/13元/626.566继续保历史。

下一TASK116/R110已登记，完整卡保存阶段进行，未派发/接收，验收未裁定。STEP018当前为集成合同准备，实施未开始/未验证；前置有限切片不冒所有Must已过，设计核对实际剩余。A+优先原114工程窗，新完整只读成果A—D，不承担独立审计，不派子Agent，TASK117未占。7200活动含600落盘/接收后48h；产品/测试/PG/API/Browser/容器/构建/provider/费用/公网/Git写全0，不重置原投入或借旧资源。

TASK116应一次给两条主链实际调用图与差异、唯一最小实施合同、有限语义/故障验收、可转交实施草案及最少真实待决。已有授权自主范围不再审批，真实新模型/公开接口/依赖/外发/费用/用户数据才提交具体包。现有Compose/Windows监督与未来Linux/Nginx边界保留，不为技术词扩平台、不在设计前开实验；稳定完整集成的适用集中独审/STEP019与自用交接STEP020仍在后续。

主控仅读原材料/身份和共享维护，产品执行0。回收关闭证据在TASK115/orchestration-final-receipt-20261014；新卡/许可/输入/窗口/旧文档/保存证明在TASK116/orchestration-20261014，正式需求/原结果/原证据/公共库不改。CHG1373—1384，下一1385。

## 以下为v2.55及更早历史

'''
prefix(STATE, state, old[STATE])
CARD.write_bytes(contract)
assert CARD.read_bytes() == contract
final_state = state.replace('TASK116已登记', 'TASK116待人工转交')
final_state = final_state.replace('完整卡保存阶段进行，未派发/接收', '完整卡已保存复读待人工转交，未派发/接收')
prefix(STATE, final_state, old[STATE])
entries = [
    ('DocuN/evidence/TASK-115/orchestration-final-receipt-20261014/received.json', '1199保护登记/29原件/243 current和旧后缀核证；两P1及有限STEP017关闭依据。'),
    ('DocuN/results/TASK-115-work-decision.md', '原集中及两轮增量独审验收通过、计时/独立性/层级和历史限制保留。'),
    ('DocuN/results/TASK-114-work-decision.md', '原完整数据退出与有限只读恢复成果验收关闭，旧额度和数据不复活。'),
    ('DocuN/results/TASK-116-work-decision.md', '新完整集成合同设计许可、最少待决、零运行和原窗人工安排。'),
    ('DocuN/evidence/TASK-116/orchestration-20261014/effective-contract.md；DocuN/tasks/TASK-116.md', '按真实现状交A—D、接线/语义/连续性/Compose与下一实施草案，一次文档核对。'),
    ('DocuN/evidence/TASK-116/orchestration-20261014/design-permit.json', '7200只读设计/48h与零产品服务/外发费用，旧全项目投入不清。'),
    ('DocuN/evidence/TASK-116/orchestration-20261014/input-manifest.json', '当前243文件与正式上下文/原终审、最小必要实际输入，不复制全库。'),
    ('DocuN/evidence/TASK-116/orchestration-20261014/window-assignment.json', 'A+优先原114窗口，新设计成果不继承旧执行许可，无子Agent/并行。'),
    ('DocuS/架构动态文档.MD', 'v1.32有限STEP017通过/四DEF关闭及完整集成尚未实现的边界。'),
    ('DocuS/执行动态文档.MD', 'v2.56唯一实际状态，114/115通过、116待转交/018合同准备与旧账封存。'),
    ('DocuN/evidence/TASK-116/orchestration-20261014/before-documents', '旧共享正式和Work原字节留档，用户原始/最终需求不改。'),
    ('DocuN/evidence/TASK-116/orchestration-20261014/delivery-proof.json', '完整卡/许可/输入/编号/状态/源报告旧账保护与保存复读，CHG连续。'),
]
addition = '\r\n' + ''.join(f'- CHG-{1373 + index}，{at}，Codex编排Agent，{path}。{reason}\r\n\r\n'
                             for index, (path, reason) in enumerate(entries))
CHANGES.write_bytes(old[CHANGES] + addition.encode('utf-8'))
assert CHANGES.read_bytes().startswith(old[CHANGES])
after = [int(value) for value in re.findall(r'^- CHG-(\d+)', CHANGES.read_text(encoding='utf-8-sig'), re.MULTILINE)]
assert after == numbers + list(range(1373, 1385))
public_inputs = [ROOT / name for name in ('AGENTS.md', 'DocuS/原始需求文档.MD', 'DocuS/最终需求文档.MD',
                 'DocuS/架构动态文档.MD', 'DocuS/执行动态文档.MD', 'DocuS/文档变更记录.MD',
                 'README.md', 'backend/requirements.txt', 'backend/requirements.lock',
                 'frontend/package.json', 'frontend/package-lock.json', 'config/activity.example.json',
                 'config/preview.example.json', 'config/data-exit.example.json', 'deploy/compose.local.yml',
                 'deploy/start_local.py', 'deploy/start-backend.ps1')]
assert all(path.is_file() for path in public_inputs)
save('input-manifest.json', {
    'created_at': at, 'purpose': '完整集成设计真实当前输入，不代表STEP018实现/验证通过',
    'current': received['current'], 'current_identity_basis': record(RECEIVED),
    'rules': received['rules'], 'formal_and_public_inputs': [record(path) for path in public_inputs],
    'task_license': record(WORK116), 'independent_final_report': received['report'],
    'independent_final_evidence': received['audit_evidence'],
    'engineering_final_report': received['engineering_report'],
    'finite_STEP017_scope': received['scope'], 'closure': received['closure'],
    'evidence_limits_retained': received['evidence_limits_retained'],
    'do_not_read': ['私有/local配置', '环境变量值/DSN/密钥/DPAPI密文', '真实用户库或个人资料'],
    'architecture_versions': {'requirements': 'v1.2', 'architecture': 'v1.32', 'execution': 'v2.56'},
    'known_missing_old_outputs': [row['path'] for row in received['current'] if not row['exists']],
    'legacy_path_rule': '旧docu/evidence/Ndocu/spikes仅以根前缀映射DocuN/archives/legacy-roots-20261005，余下路径不变',
    'read_strategy': '刚核243登记和同窗未变材料复用，只记录真正参与本设计的关键输入身份，缺口定向读取',
})

for path_text, expected in protected.items():
    assert identity(Path(path_text)) == expected, path_text
for row in received['current']:
    if not row['exists']:
        assert not (ROOT / row['path']).exists()
for path in (WORK114, WORK115, ARCH, STATE):
    assert path.read_bytes().endswith(old[path])
assert not (ROOT / 'DocuN/results/TASK-116-result.md').exists()
save('delivery-proof.json', {
    'created_at': at, 'client_date': day, 'state': 'saved_readback_complete_pending_manual_transfer',
    'TASK': 'TASK-116', 'R': 'R-110', 'card': record(CARD), 'contract_equal': CARD.read_bytes() == contract,
    'permit': record(OUT / 'design-permit.json'), 'input': record(OUT / 'input-manifest.json'),
    'window': record(OUT / 'window-assignment.json'),
    'shared_documents': [record(path) for path in (WORK114, WORK115, WORK116, ARCH, STATE, CHANGES)],
    'closed': ['TASK114有限通过', 'TASK115通过', 'DEF035', 'DEF036', '有限STEP017-P1'],
    'previous_closed_retained': ['DEF034', 'DEF037'],
    'full_project_or_NFR005_passed': False, 'STEP018_implementation_started': False,
    'TASK116_dispatch_confirmed': False, 'TASK116_result_exists': False, 'TASK117_allocated': False,
    'protected_file_count': len(protected), 'protected_changes': [],
    'shared_old_bytes_preserved': True, 'product_execution_by_orchestrator': 0,
    'CHG_added': list(range(1373, 1385)), 'next_CHG': 1385,
})
print(json.dumps({'state': 'closed_and_next_contract_saved', 'finite_STEP017': '通过',
                  'card': record(CARD), 'window': 'A+原TASK114工程窗转只读STEP018合同',
                  'architecture': 'v1.32', 'execution': 'v2.56', 'CHG': '1373—1384',
                  'dispatch': '待人工转交', 'product_runs': 0}, ensure_ascii=False))
