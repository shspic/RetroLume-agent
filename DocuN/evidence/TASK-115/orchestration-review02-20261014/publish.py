"""回收C03候选，串行更新共享记录并保存原115增量终审卡；不执行产品。"""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import hashlib
import json
import re

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent')
OUT = Path(__file__).resolve().parent
BASE = ROOT / 'DocuN/evidence/TASK-114/implementation/continuation-03'
RECEIVED = ROOT / 'DocuN/evidence/TASK-114/orchestration-c03-receipt-20261014/received.json'
CARD = ROOT / 'DocuN/tasks/TASK-115.md'
WORK114 = ROOT / 'DocuN/results/TASK-114-work-decision.md'
WORK115 = ROOT / 'DocuN/results/TASK-115-work-decision.md'
ARCH = ROOT / 'DocuS/架构动态文档.MD'
STATE = ROOT / 'DocuS/执行动态文档.MD'
CHANGES = ROOT / 'DocuS/文档变更记录.MD'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def identity(path):
    data = path.read_bytes()
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


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
old = {path: path.read_bytes() for path in (CARD, WORK114, WORK115, ARCH, STATE, CHANGES)}
assert '文档v1.30' in old[ARCH].decode('utf-8-sig').splitlines()[2]
assert '文档v2.54' in old[STATE].decode('utf-8-sig').splitlines()[2]
numbers = [int(value) for value in re.findall(r'^- CHG-(\d+)', old[CHANGES].decode('utf-8-sig'), re.MULTILINE)]
assert numbers[-1] == 1363 and 1364 not in numbers
contract = (OUT / 'effective-contract.md').read_bytes()
text = contract.decode('utf-8-sig')
assert '*' not in text and not re.search(r'^\|', text, re.MULTILINE)
for value in ('目标与交付', '项目、规则、窗口与授权', '前置与最小充分输入',
              '必答A', '必答B', '证据绑定、失败与有限传播', '读写边界与预算',
              '顺序、停止与回传', '5400秒', '本轮产品运行新增0', 'c03-browser-1210447187000000'):
    assert value in text, value
assert len(received['current']) == 246
assert sum(row['exists'] for row in received['current']) == 243

protected = {}
for path in (ROOT / 'DocuN/results/TASK-114-result.md', ROOT / 'DocuN/results/TASK-115-result.md',
             ROOT / 'DocuN/tasks/TASK-114.md', ROOT / 'AGENTS.md',
             ROOT / 'DocuN/evidence/TASK-114/implementation/control/receipt.json',
             ROOT / 'DocuN/evidence/TASK-114/implementation/control/events.jsonl'):
    protected[str(path)] = identity(path)
for row in received['current']:
    path = ROOT / row['path']
    if row['exists']:
        expected = {key: row[key] for key in ('bytes', 'sha256')}
        assert identity(path) == expected, str(path)
        protected[str(path)] = expected
    else:
        assert not path.exists()
for row in received['raw_evidence_navigation'] + received['unchanged_review01_evidence']:
    path = Path(row['path'])
    expected = {key: row[key] for key in ('bytes', 'sha256')}
    assert identity(path) == expected, str(path)
    protected[str(path)] = expected
for row in received['rules']:
    path = Path(row['absolute_path'])
    assert identity(path)['sha256'] == row['sha256']
    protected[str(path)] = identity(path)
backup = OUT / 'before-documents'
backup.mkdir(exist_ok=False)
for path, raw in old.items():
    (backup / path.name).write_bytes(raw)

permit = {
    'TASK': 'TASK-115', 'R': 'R-109', 'round': 'review-02',
    'permit': 'TASK-115-STEP017-REVIEW02-20261014', 'issued_at': at,
    'authorization': '用户已采用STEP017-P1并要求完成；稳定C03双修后原独审窗口仅问题及实际传播增量终审',
    'dispatch_confirmed': False, 'execution_started': False,
    'focus': ['DEF-035/F02', 'DEF-036/F03'],
    'closed_inherited': ['DEF-034/F01', 'DEF-037/F04'],
    'new_active_seconds_max': 5400, 'save_reserve_seconds': 300,
    'previous_active_conservative_seconds': 8617.261566,
    'original_active_seconds_limit': 21600,
    'total_active_if_full_round_used': 14017.261566,
    'remaining_after_full_round': 7582.738434,
    'original_calendar_deadline_utc': '2026-10-15T06:16:24.914938Z',
    'actual_first_tool_UTC_and_mono': '执行者首工具同步实采；漏点如实披露并保守计，不用签发时间冒接收',
    'new_runtime_limits': dict.fromkeys(['real_roots', 'PG', 'SQL', 'Docker_mutation', 'Docker_wakeup',
                                       'API', 'Browser', 'compile', 'unittest', 'product_import',
                                       'build', 'Windows', 'preview', 'provider', 'fees', 'public_network'], 0),
    'allowed': '既存文件/hash/有限AST/JSON/diff/截图阅读及报告保存，不运行产品',
    'old_counts': {'roots': 3, 'API': 3, 'Browser': 2, 'offline_seconds': 125.610,
                   'holding_conservative_seconds': 14.874},
    'engineering_counts_not_reauthorized': received['counts'],
    'engineering_active_C03': received['delivery']['active_C03_seconds_conservative'],
    'engineering_active_C02_plus_C03': received['delivery']['active_C02_plus_C03_seconds'],
    'evidence': str(ROOT / 'DocuN/evidence/TASK-115/review-02'),
    'result': str(ROOT / 'DocuN/results/TASK-115-result.md'),
    'independence': '原115独立窗未参与工程，旧意外摘要暴露披露保留；不读114结果/聊天/自评',
}
save('continuation-permit.json', permit)
save('input-manifest.json', {
    'created_at': at, 'purpose': '原独审增量输入中性字节/真实方法导航，工程结果正文不作判断输入',
    'current': received['current'], 'final_source': received['final_source'], 'pre': received['pre'],
    'rules': received['rules'], 'root_entry': record(ROOT / 'AGENTS.md'),
    'adopted_contract': record(ROOT / 'DocuN/evidence/TASK-113/design/revision-01/current-contract.md'),
    'engineering_card': record(ROOT / 'DocuN/tasks/TASK-114.md'),
    'original_independent_report': record(ROOT / 'DocuN/results/TASK-115-result.md'),
    'original_review01_evidence': received['unchanged_review01_evidence'],
    'current_final_manifest': received['manifest'], 'method_index': received['method_index'],
    'methods': received['methods'], 'raw_evidence_navigation': received['raw_evidence_navigation'],
    'loading_pin_cases': received['loading_pin_case_files'],
    'browser_result': received['browser_result'], 'browser_case_names': received['browser_cases'],
    'actual_product_source_changed': received['actual_product_source_changed'],
    'engineering_control': received['control'], 'engineering_events': received['events'],
    'preserved_report_identity_only': received['report'],
    'report_and_control_pre_layout': {'report': 'pre/TASK-114-result.md，不读工程自评',
                                     'receipt': 'pre/receipt.json', 'events': 'pre/events.jsonl'},
    'reading_exclusions': ['TASK-114-result.md正文及pre/工程自评正文', '实现聊天/思考', '记忆中的工程结论'],
    'old_resource_basis': received['old_owned_PG_basis'],
})
save('window-assignment.json', {
    'created_at': at, 'TASK': 'TASK-115', 'R': 'R-109', 'round': 'review-02',
    'grade': 'A+', 'window': '原TASK115独立审计窗口，上一review-01',
    'previous_actual_identity': 'Codex desktop / GPT-6，当前如实登记',
    'reason': '只复核两处高风险余缺和实际传播，复用原独审与充分方法',
    'manual_transfer': True, 'dispatch_confirmed': False,
    'engineering_window': '原TASK114已返回并封存，零并行产品写入',
    'no_subagents_or_parallel_writers': True,
})

work114 = f'''# TASK114 C03稳定候选已返回，待原115两项增量终审

{at}，Codex编排Agent。实际报告90515字节/12985d9837c18333acb9b4113db178993e2c45c710da3193112529a6856bfdf5，旧69598字节后缀原字节保留。主控核243当前/final/pre、13方法原件与绑定、十二场景及旧115报告原件。只改reference.py、restore.py、DataWorkspace.tsx三个产品源，Operations/普通ReferencePin/context/dataApi与原闭环核心未改。工程调度已返回、候选部分通过，DEF035/036未由主控关闭。

loading pin的同Operation/受限连接/fetch与COMMIT后check以三组受控原始连接方法取证；最终bundle的输入版本/计划动作/范围/迟到以真实Chromium十二route场景取证。不是新PG或真实selector，通过层级不扩大。首次Browser定位FAIL保留，复验未改产品且绑定最终源码/脚本/bundle；旧真实PG只证reading过D的更正仍有效。

C03活动4495.4211376、与C02合计13684.1412486；累计root23/24、Browser7/9且本轮门7满、build6/7、offline205.959/hold487.876。PG/start/API/Native等本轮零，旧资源继承停止事实，新四准确Browser/controller资源均stopped/确认close，两个活根已结束。原工程余量不自动复活，旧账/FAIL/文件/数据/selector全保留。

下一同TASK115/R109原独立窗review-02，仅F02/F03及真实传播/证据和执行控制；新运行0，不重审F01/F04或旧主链。独审回后由主控裁定两DEF和有限STEP017，不签完整恢复继续或项目。原结果/源码/工程控制不由主控修改。

## 以下为旧工程记录原字节

'''
prefix(WORK114, work114, old[WORK114])

work115 = f'''# TASK115 review-02两项增量独立终审许可，待人工转交

{at}，Codex编排Agent。TASK114 C03实际已返回并冻结，243当前和final/pre、13方法绑定及十二route场景/准确close原件核证。原115报告61253字节/3d6a4ce4…4a0f2与23原件未改，独立性/既有暴露披露继续接受。DEF034/037已关闭；DEF035/036保留P1待本轮独立裁定，不能因工程报告自签关闭。

许可TASK-115-STEP017-REVIEW02-20261014，原A+独立审计窗，只读5400秒含最后300落盘。原审计累计8617.261566/21600全部保留，本轮全用最多14017.261566；旧日历到2026-10-15T06:16:24.914938Z不延。新增全部产品/PG/SQL/Docker/API/Browser/compile/test/build/Native/provider费用0，不借工程余额，不需RAM门/密钥/开容器。

只核loading pin同D真实传参/受控方法，以及输入revision/生命周期/计划与scope动作绑定、最终bundle十二场景及有限影响。原F01/F04、31域/正常PG/SUP/G11等未变充分证据继承；原PG两秒样本仅reading超时，既定受控参数检查不是要求新增物理PG。不读114结果自评，只读目标/源码/原件，不能直接修产品。

完整同号卡DocuN/tasks/TASK-115.md已保存复读待人工转交，未实际派发/接收。原114封存，无在途产品写入，TASK116未占。结果review-02置顶且保原61253字节后缀，主控据三轴最后裁定DEF/STEP，不预签。

## 以下为原独审许可及历史原字节

'''
prefix(WORK115, work115, old[WORK115])

arch = f'''# 架构动态文档

文档v1.31，{day}，Asia/Shanghai。需求v1.2、执行动态v2.55、task_model/07；以下v1.30历史原字节保留。

## STEP017两处余缺候选已补，独立增量终审前不关闭

{at}。TASK114 C03实际实现loading pin必需绑定原Operation/同Hub-job、受限连接与结果消费后资格检查，_load唯一构造点传同对象；普通ReferencePin与operations核心未改。前端DataWorkspace按restore/scope输入版本和dataset lifetime保护上传/策略/文件/计划/刷新/验证激活与两类范围，呈现和动作共用当前资格，旧事实仍可核对但不复活执行权。

定向原件为实际产品的三组受控原始连接检查、最终bundle真实Chromium十二route场景；不冒物理PG等待或真实selector，本轮没有新增后台主链。旧PG deadline只到reading失败的适用性更正保留。三份产品源之外的原F01/F04及SQL/ACL/普通权限/Native/停止核心按未变机制继承。

DEF035/036保持开放待原115 review-02对问题与实际传播终审；DEF034/037关闭不重审，存在具体回归仍按事实处理。永久只读范围、source frozen/旧selector保护和全部原Must不减，不宣完整NFR005/恢复继续、STEP018—020、M-1或项目发布。

## 以下为v1.30及更早历史

'''
prefix(ARCH, arch, old[ARCH])

state = f'''# 执行动态文档

文档v2.55，{day}，Asia/Shanghai。唯一总状态账；需求v1.2、架构v1.31、task_model/07。以下v2.54历史原字节保留。

## TASK114 C03已返回，TASK115 review-02已登记

{at}。工程C03已真实接收/执行/返回，报告90515字节/12985d9837c18333acb9b4113db178993e2c45c710da3193112529a6856bfdf5，原69598字节后缀完整。主控核246登记/243当前/final/pre、13方法as-run实际绑定、十二Browser场景及关闭原件和七规则无漂移；只改三产品源，工程验收为稳定候选部分通过，DEF035/036继续P1开放待独审。F01/DEF034、F04/DEF037已关闭，STEP017尚不关闭。

三组LoadingPin受控连接方法2.735秒exit0/内部1.964，最终Browser十二route场景4.984秒exit0，typecheck21.985与一次build7.578通过。首次Browser7.954秒定位FAIL/业务0到达、缺初次失败DOM保留；夹具locator与reload适配后未改产品/bundle复验。正常文件选择的upload/plan POST与显式verify/export/activate分别计，不把所有POST零当断言。没有新PG/SQL/API/Vite/监听/Native/provider/费用，不把受控层写真实后端；旧PG只证reading超时的更正沿用。

C03活动4495.4211376，C02+C03合计13684.1412486/原21600；首工具未同步mono、后同步QPC/UTC保守扣300秒，内存等待连续计。累计root23/24、Browser7/9且C03门7已满、build6/7、offline205.959（新33.642）/hold487.876（新25.829），PG create9/12/success9/9/start37/37、Windows11/12、API8/11不变。C03两根已结束，新controller+Chrome四精确PID/birth均close/ended，唯一账31资源stopped；旧九PG停止按既有精确原件继承，不冒今日现场Docker观察。工程无在途消费者/写入，子余额不恢复新许可。

原115 review-01活动3126.578112/累计8617.261566、root3/API3/Browser2/offline125.610/hold14.874及全部失败/原锚点保留；C01 9739.953/旧55525.796净unknown、G11/25/UNKNOWN/R60/count1/13元/626.566和原Must不改。

TASK115/R109 review-02已登记，完整卡保存阶段进行，未派发/接收。继续原A+独立窗口，只两项余缺/实际影响/证据和控制，原114封存，不派子Agent、不占TASK116。新只读活动5400含最后300落盘，旧审计累计加最多14017.261566仍在21600内，旧日历2026-10-15T06:16:24.914938Z不延；全部新增产品运行0，不借工程余额，不要求内存/密钥/旧容器启动。充分不变方法直接继承，不重做四问题/整仓/正常恢复。

主控仅原始材料、字节、方法和记录核证及共享维护，产品执行0；元数据首检误用C02 pre布局的FileNotFoundError按实际C03 pre修正并留注，非产品失败。回收在TASK114/orchestration-c03-receipt-20261014；许可/卡/输入/窗口/旧文档和保存证明在TASK115/orchestration-review02-20261014。CHG1364—1372，下一1373。原始/最终需求/旧结果/证据/公共库不改，不宣完整NFR005/项目发布。

## 以下为v2.54及更早历史

'''
prefix(STATE, state, old[STATE])
CARD.write_bytes(contract)
assert CARD.read_bytes() == contract
final_state = state.replace('TASK115 review-02已登记', 'TASK115 review-02待人工转交')
final_state = final_state.replace('完整卡保存阶段进行，未派发/接收', '完整卡已保存复读待人工转交，未派发/接收')
prefix(STATE, final_state, old[STATE])
entries = [
    ('DocuN/evidence/TASK-114/orchestration-c03-receipt-20261014/received.json', '243当前/final/pre/旧后缀及13方法身份、十二route与收尾原件核证，保候选和层级。'),
    ('DocuN/results/TASK-114-work-decision.md', 'C03实际回收、三个源增量/预算/失败和准确关闭，稳定交原独审。'),
    ('DocuN/results/TASK-115-work-decision.md', '同原独审review-02零新运行、两问题/传播终审，旧累计/独立性不清。'),
    ('DocuN/evidence/TASK-115/orchestration-review02-20261014/effective-contract.md；DocuN/tasks/TASK-115.md', '完整两余缺增量终审卡保存复读，原窗人工转交，充分证据继承。'),
    ('DocuN/evidence/TASK-115/orchestration-review02-20261014/continuation-permit.json；input-manifest.json；window-assignment.json', '5400只读段原累计门内/固定日历、零新产品，原件版本与独立安排。'),
    ('DocuS/架构动态文档.MD', 'v1.31记录pin和输入绑定的实际候选增量与未关闭/受控层边界。'),
    ('DocuS/执行动态文档.MD', 'v2.55唯一实际状态：C03已返回、DEF035/036待审、review-02待转交及旧预算全保。'),
    ('DocuN/evidence/TASK-115/orchestration-review02-20261014/before-documents/TASK-115.md', '原review-01完整卡和共享旧文档原字节保存，旧执行许可不复活。'),
    ('DocuN/evidence/TASK-115/orchestration-review02-20261014/delivery-proof.json', '完整卡/授权输入/当前产品原件和执行账保护、CHG连续与保存复读。'),
]
addition = '\r\n' + ''.join(f'- CHG-{1364 + index}，{at}，Codex编排Agent，{path}。{reason}\r\n\r\n'
                             for index, (path, reason) in enumerate(entries))
CHANGES.write_bytes(old[CHANGES] + addition.encode('utf-8'))
assert CHANGES.read_bytes().startswith(old[CHANGES])
after = [int(value) for value in re.findall(r'^- CHG-(\d+)', CHANGES.read_text(encoding='utf-8-sig'), re.MULTILINE)]
assert after == numbers + list(range(1364, 1373))
for path_text, expected in protected.items():
    assert identity(Path(path_text)) == expected, path_text
for row in received['current']:
    if not row['exists']:
        assert not (ROOT / row['path']).exists()
for path in (WORK114, WORK115, ARCH, STATE):
    assert path.read_bytes().endswith(old[path])
save('delivery-proof.json', {
    'created_at': at, 'client_date': day, 'state': 'saved_readback_complete_pending_manual_transfer',
    'card': record(CARD), 'contract_equal': CARD.read_bytes() == contract,
    'permit': record(OUT / 'continuation-permit.json'), 'inputs': record(OUT / 'input-manifest.json'),
    'window': record(OUT / 'window-assignment.json'),
    'shared_documents': [record(path) for path in (WORK114, WORK115, ARCH, STATE, CHANGES)],
    'original_audit_card': record(backup / CARD.name), 'shared_history_original_bytes_preserved': True,
    'protected_file_count': len(protected), 'protected_changes': [],
    'closed_inherited': ['DEF-034/F01', 'DEF-037/F04'], 'open_pending_review': ['DEF-035/F02', 'DEF-036/F03'],
    'STEP017_closed': False, 'TASK116_allocated': False, 'product_execution_by_orchestrator': 0,
    'CHG_added': list(range(1364, 1373)), 'next_CHG': 1373,
})
print(json.dumps({'state': 'published_readback_verified', 'card': record(CARD),
                  'architecture': 'v1.31', 'execution': 'v2.55', 'CHG': '1364—1372',
                  'dispatch': '待人工转交', 'new_product_runs': 0}, ensure_ascii=False))
