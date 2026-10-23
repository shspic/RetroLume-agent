"""主控断点核证与同号合同纠正；仅标准库和文件元数据，无产品导入或运行。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import time

START = time.monotonic()
ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
E = ROOT / 'DocuN/evidence/TASK-120/execution'
C = E / 'continuation-01'
assert ROOT == Path('D:/shspic/project_NO3_RetroLume-agent').resolve()
assert not (HERE / 'save-proof.json').exists(), '本次已保存，先核断点，不重复执行'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path, raw, new=False):
    if isinstance(raw, str):
        raw = raw.encode('utf-8')
    assert path.resolve().is_relative_to(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb' if new else 'wb') as handle:
        handle.write(raw)
    assert path.read_bytes() == raw


def save_json(path, value):
    write(path, json.dumps(value, ensure_ascii=False, indent=2) + '\n', new=True)


now = datetime.now(timezone(timedelta(hours=8))).isoformat()
rules = load(ROOT / 'DocuN/evidence/v4-migration-20260930/rules-snapshot.json')
rule_checks = []
for row in rules:
    actual = digest(Path(row['absolute_path']).read_bytes())
    assert actual == row['sha256'], row['relative_path']
    rule_checks.append({'path': row['absolute_path'], 'sha256': actual, 'match': True})

old_identity = load(E / 'final-file-identities.json')
new_identity = load(C / 'final-file-identities.json')
old_map = {row['path']: row['after_sha256'] for row in old_identity['existing_files'] + old_identity['new_files']}
new_map = {row['path']: row['sha256'] for row in new_identity['current_files']}
new_map.update({row['path']: row['sha256'] for row in new_identity['new_files']})
product_deltas = [p for p in old_map.keys() & new_map.keys()
                  if old_map[p] != new_map[p] and p.startswith(('backend/app/', 'frontend/src/', 'frontend/dist/'))]
assert set(product_deltas) == {'backend/app/capabilities/q_context.py', 'backend/app/capabilities/q_protocol.py'}
# 本次只核实际增量/新夹具和四bundle，不重采641项未变产品。
selected = set(product_deltas)
selected.update(p for p in new_map if old_map.get(p) != new_map[p])
for field in ('changed', 'new_files'):
    for row in new_identity[field]:
        selected.add(row['path'])
selected.update(['frontend/dist/index.html'])
selected.update(p for p in new_map if p.startswith('frontend/dist/') and new_map[p] is not None)
source_checks = []
for path in sorted(selected):
    expected = new_map.get(path)
    if expected is None:
        assert not (ROOT / path).exists(), path
        source_checks.append({'path': path, 'sha256': None, 'expected_absent': True})
    else:
        actual = digest((ROOT / path).read_bytes())
        assert actual == expected, path
        source_checks.append({'path': path, 'sha256': actual, 'match': True})

report = ROOT / 'DocuN/results/TASK-120-result.md'
raw_report = report.read_bytes()
marker = b'# TASK-120 / R-114 ' + '工程结果与停止断点'.encode()
assert digest(raw_report[raw_report.index(marker):]) == '69ce8513eeef5fed6cb72f3e13d9e4cb72c300d30a6dd5416ea90e0a6ea2da2b'
block = load(C / 'automatic-review-block.json')
assert block['executed'] is False and 'Selected model is at capacity' in block['reason']
b = load(E / 'budget.json')
assert b['active_root'] is None and b['active_command'] is None
assert b['counts']['roots'] == 14 and b['caps']['roots'] == 16
assert b['counts']['provider_calls'] == b['counts']['actual_fee_microunits'] == 0
assert b['calendar_deadline_utc'] == '2026-10-22T08:41:08.5687758Z'
race = load(E / 'budget-last-slot-race.json')
assert race['baseline'] == {'requests': 99, 'cost': 24750000}
assert len(race['waiting_backends']) == 2
assert all(x['wait_event_type'] == 'Lock' and x['wait_event'] == 'advisory' for x in race['waiting_backends'])
reopen = load(E / 'root-14-budget-reopen.json')
assert reopen['same_database'] and reopen['requests'] == 100 and reopen['cost'] == 25000000
assert [r['requests_reserved'] for r in reopen['financials']['activities']] == [48, 28, 24]
assert all(r['running_reserved_seconds'] == 0 for r in reopen['financials']['activities'])

input_paths = [report, E / 'budget.json', E / 'events.jsonl', C / 'automatic-review-block.json',
               C / 'final-stop-proof.json', C / 'final-review-index.json', C / 'final-file-identities.json',
               C / 'source.diff', C / 'fixture.diff', C / 'plan-root-15.json',
               E / 'budget-last-slot-race.json', E / 'root-14-budget-reopen.json',
               E / 'root-14-html-eol-applied.json', C / 'html-eol-user-permission.json',
               ROOT / 'backend/tests/fixtures/task120/flow.py',
               ROOT / 'backend/tests/fixtures/task120/setup.py',
               ROOT / 'backend/tests/fixtures/task120/integrated.py',
               ROOT / 'backend/tests/fixtures/task120/pg_boundaries.py',
               ROOT / 'backend/app/activities/teaching_repository.py',
               ROOT / 'backend/app/learning/teaching_contracts.py',
               ROOT / 'backend/app/activities/interview_repository.py',
               ROOT / 'backend/app/activities/repository.py',
               ROOT / 'backend/app/memory/contracts.py']
inputs = [{'path': p.relative_to(ROOT).as_posix(), 'sha256': digest(p.read_bytes()), 'bytes': p.stat().st_size}
          for p in input_paths]
for name in ('budget.json', 'events.jsonl'):
    write(HERE / 'returned-snapshot' / (name + '.bytes'), (E / name).read_bytes(), new=True)

state_path = ROOT / 'DocuS/执行动态文档.MD'
arch_path = ROOT / 'DocuS/架构动态文档.MD'
changes_path = ROOT / 'DocuS/文档变更记录.MD'
card_path = ROOT / 'DocuN/tasks/TASK-120.md'
decision_path = ROOT / 'DocuN/results/TASK-120-work-decision.md'
old = {p: p.read_bytes() for p in (state_path, arch_path, changes_path, card_path, decision_path)}
assert '文档v2.75' in old[state_path].decode('utf-8-sig')[:130]
assert '文档v1.47' in old[arch_path].decode('utf-8-sig')[:130]
assert 'CHG-1526' in old[changes_path].decode('utf-8-sig')[-5000:]
for path, raw in old.items():
    write(HERE / 'before' / (path.name + '.bytes'), raw, new=True)

save_json(HERE / 'input-verification.json', {
    'time': now, 'task': 'TASK-120', 'R': 'R-114', 'rules': rule_checks,
    'product_deltas_from_prior_return': product_deltas, 'incremental_file_checks': source_checks,
    'inputs': inputs, 'original_report_suffix_exact': True,
    'C12_raw_barrier_and_reopen_checked': True, 'preflight_block_executed': False,
    'remaining': {k: b['caps'][k] - b['counts'][k] for k in b['counts'] if k in b['caps']},
    'main_product_imports_tests_PG_Docker_API_browser_provider_Git': 0,
    'verification_is_bounded_orchestration_not_independent_audit': True,
    'current_container_state_not_freshly_observed': True,
})

decision = f'''# TASK-120 / R-114 主控断点裁定02（当前有效，无新增预算）

{now}。续作01确已返回；工程总验收仍部分通过，未到稳定独审点。主控核当前两份产品增量、变化/新夹具与4正式bundle、7锁定规则、旧报告原字节后缀、C12原始双backend barrier及root14同库重开。元数据逐项身份见本轮input-verification.json；不是重跑业务或独立代码终审。

## 为什么再次停下

1. 主控上一卡的C09指令不充分：只核goal效果/no-op，没有核apply_teaching_local在效果之前的slot_winner。原A1在revision1已提交的相同goal命令占据goal槽，因此先concept再numeric的第一步必定stage_conflict。撤销这条指令，不把责任只归工程模型，不再在A1尝试换文本/换key。
2. 已选memory正例未在活动创建前安排，旧flow/budget01三活动已创建，create_activity的选择绑定不能事后补。这是测试准备缺口，不应靠反复启动探路或改生产规则解决。
3. 最后command038因自动审批服务“Selected model is at capacity”未执行；不是不安全裁定、不是业务失败、不是根额度耗尽。现余2根、3次PGstart、7次APIstart、8次Browser和2次build。不得借换模型/shell/连接器绕过；正常审批服务恢复前不执行被拦动作。

已完成C12共同100/25、同库重开、旧learning和9函数精确EOL修补予以按实际对象收存，禁止为接续重做。当前两产品修补只有15项定向证据，不签面试真实链。总体矩阵剩余项及正式UI未完成，不提前派独审。

## 两项测试安排由主控直接明确（已采用零外发实施范围内）

- flow固定A3可用于新教学head的正常正例；这不是释放A1未知槽、清额度或换grant。沿原grant、N来源、24次/6元TESTONLY预留分额和原deadline，旧learning原COMMIT仍保持。先只读查A3确无teaching/interview互斥head且源/资格/余额满足，再一次goal→真实新head→query→准备/批准/原键model。若发现实际不同状态只停该例，不能改槽或清历史。A1原UNKNOWN永久保留，作为禁止二发反例。
- 原allowlist内尚未初始化的budget-02可改用于已选记忆的独立TESTONLY正/反例，而不是重复已过100门。仅原CID/卷内这一预留逻辑库；固定A2创建时按生产memory保存/选择接口绑定TASK116冻结memory_body（原字节），再建教学/面试协议许可的完整请求。其余两个固定UUID及48/28/24、12/7/6、100/25配置保持；创建前固定用途、scope与选择，旧库不重绑。新根/活动有效期不得晚于原flow的2026-10-19T12:19:22.457756Z，不新增正常Q权益、真实费用或延长旧grant。旧budget-01金融账100/25封存不动，不把新隔离测试库当旧额度恢复。生产DDL/迁移/权限模型均不变。该项取代旧budget-02只为预算修复备用的用途限制，新增逻辑库对象上限不变。

面试修复后用现有flow A2合法goal命令创建新版本：源码明确每个成功goal递增revision/goal_version，和教学no-op机制不同；必须先读真实槽/头，真实回读新父后再准备。保留原claimed UNKNOWN，不能重发。HTML精确EOL修补已生效，只补description，不开preview。

## 恢复方式

不发新TASK/新资源许可，不重置任何次数或工时。沿现有许可仅补正常PG/SUP、ACK/K2、有限来源/已选记忆及最终五入口UI；同窗一次合并，普通修复留卡内。现有plan-root15没有教学/已选记忆，UI只列面试/旧learning/HTML，不能冒充完整覆盖，须先补入同一有限依赖表。可以复用当前controllers，但最后未执行的改动不宣称通过。

先结束纯离线合同/夹具修正，再经原正常审批路径执行必要语法检查。平台恢复不需要用户再批钱或预算；服务仍容量受限则保留断点，不反复提交探针，不绕路。新的执行回执与原038未执行记录分开；不改写原失败。

继续前精确CID Docker身份/状态须正常读取成功；09:47停机事实和最新PID/Job/端口观察不能冒充当前Docker实时证明。低内存门保持512/768MiB，连续两次<256精确停止；不要求用户再次释放内存。若本轮受内存阻断，只阻对应层，不借关掉守卫保证“必过”。原grant/活动/日历/累计时间最短门均保持，到期不刷根续命。

当前累计14/16根、PGstart13/16、API9/16、Browser0/8、build4/6、Native9/48、HTTP54/5000、44失败记录；命令wall保守17553.845332/21600、持有1150.108295/14400。旧两笔7200未知预留不冲销；未来记录真实计时与区间归属，不因换轮机械另加同额预留、不重复累加同一已覆盖区间；新未计量部分不能冒充0。主控没有修改工程budget/events。

TASK120稳定完整后再按原安排集中独审；Q仍冻结，STEP018整体/019/020/M1/项目不签通过。原S有限验收不重开。具体完整合同在同号TASK-120.md置顶，旧采用/合同/报告全部保留。

---

# 以下为先前裁定，历史原字节保留

'''

card = f'''# TASK-120 / R-114 — 断点纠正02：补合法测试起点并完成剩余成果（无新增额度）

## 目标、窗口与当前许可

接收Agent：A+，继续TASK120原TASK119/117工程窗口；不新开实施者，不委派，不启动独审。本次纠正上一续作01两处不可行测试安排，沿已采用完整Q v2成果继续，正常实现/修复/相关验证卡内连续完成。交付仍为一个稳定、可集中独审的零外发完整工程包，不能把本次只当准备报告。

此段优先于以下历史中的A1两步切目标、budget-02用途限制及“共同100门待跑”表述；未改原A—D、Must、安全合同和允许产品文件。**没有新增预算，没有新TASK，没有新真实Q授权**。现有许可TASK-120-Q-PREP-CONTINUATION-01-20261019及原许可均在后文，保持同一budget/events、全部失败和原首点。

## 项目、规则、依据和最小输入

根D:/shspic/project_NO3_RetroLume-agent；入口同根AGENTS.md。锁定V4.0/公共AGENTS CHG-0003，公共根D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，DocuS/AGENTS.MD、WORK.MD第2/5/6/8/9章、task_model/prompts/07_开发执行循环.md和TASK_TEMPLATE；同窗未变复用。七锁定指纹在DocuN/evidence/v4-migration-20260930/rules-snapshot.json，本轮一致；不采用后来公共版本。

口径需求v1.4、架构v1.48、执行动态v2.76，STEP018及原TASK120全部关联。授权仍为用户采用119包，范围为合成/零外发实施与验证，真实provider/实际费用/preview/Git新增0，Q冻结。资源标签不冒充模型身份。无需用户密钥、SQL或释放内存。

按序只补已变部分：

1. D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-120-work-decision.md置顶02和同目录TASK-120-result.md续作01；本次主控已直接明确两个测试安排，**不要再询问是否可用A3或预留budget-02**。
2. D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/orchestration-recovery-20261019/input-verification.json、scope-clarification.json；原资源permit仍在orchestration-continuation01-20261019/permit.json。本文后附全部旧合同，可脱离聊天执行。
3. DocuN/evidence/TASK-120/execution/budget.json、events.jsonl、case-index.json、remaining-readiness.json和continuation-01/final-review-index.json、final-file-identities.json、automatic-review-block.json、final-stop-proof.json。旧as-run/未执行标记/原报告后缀保持；不要执行旧root或重写旧计划原件。
4. backend/app/activities/teaching_repository.py的apply_teaching_local槽判定在效果前、teaching_contracts.semantic_slot，repository.create_activity记忆绑定，interview_repository.apply_interview_local/_interview_replay，及已保存flow/setup/integrated/pg_boundaries/UI夹具；只补这次直接依赖，不全仓重读。

## 已通过直接继承，不重跑

真实C12：budget-01原99→100双backend同锁竞争、两provider达限拒绝、root12/14同库重开100/25000000，三活动48/28/24且R0；对应budget-last-slot-race.json和root-14-budget-reopen.json。旧R300已经生产折叠，不能再核销/退款。旧learning原键COMMIT、原embedding索引/查询、9函数EOL修补及普通角色指纹检查均按原对象继承，不再应用补丁/012或重复全套业务。

最终前端源码/dist本轮未变，继承原typecheck/build及四文件hash；这不是浏览器通过。q_context/q_protocol两产品修补仅15项定向检查通过，面试真实链仍须跑。根15/16及最后预检没有执行，不能按已通过使用。

## 一次补齐两个合法起点

**教学：采用原flow固定A3=01800000-0000-4000-8000-000000000003。** 原A1的相同goal no-op已COMMIT，占据revision1 goal槽；上一主控concept→numeric处方撤销，不再尝试该槽。A3仍沿同grant/Nscope/24次与6元合成分额/原deadline，保留其旧learning COMMIT，不清额度。先只读核A3无teaching/interview互斥head、范围/余额/时间合法，再通过原生产local goal建立真实head，固定一次新业务键，回读记录/版本后正常query→精确准备/批准→同键显式model→007/领域提交及需要的后继。旧A1 UNKNOWN键1f5c659f-4a5a-4fee-bfbe-3f245eb5bc7e及其父槽永久保留，不重发、不换文字绕槽。若A3实际有冲突则停此例交具体事实，不能暗建第四活动或改生产槽。

**已选记忆：准许原allowlist内尚未初始化的retrolume_task120_budget_02作记忆专用TESTONLY库。** 仅原CID/卷内第三库，不新容器/卷，不重建旧库/换source或readonly权利。初始化前就固定A2=...0002的scope、TASK116冻结memory_body及选择；经既有生产memory保存/选择接口，再create_activity(memory_selection=...)一次绑定。固定全roster与100/25、48/28/24分额不变；manifest只沿原冻结输入，不扩文字白名单。新TESTONLY根/活动的valid_until/deadline不得晚于原flow的2026-10-19T12:19:22.457756Z，不延长旧根，不出具真实启用物。正例证明实际选择记录/完整请求中有限memory来源及一次合法模型提交，反例沿原有限来源/撤销矩阵；不因新库独立而称旧budget-01总账恢复。不重复100门，不增加库对象上限。

**面试/HTML：** 原flow A2的旧claimed UNKNOWN430a4e36-08e1-411f-a73e-097506a6278b不重发。源码面试goal确实产生新版本，按真实当前head/槽先提交local goal并回读，再准备新ask和query；不能仅改key。HTML仅补原learning成果的description，继承已修9函数，不启preview、不改profile。

## 剩余完整交付及有限执行

先将上述教学/记忆真实父、面试、HTML、ACK/K2/有限权限反例、五入口最终UI全部落进同一有限用例—依赖—原件表，再运行。当前plan-root15仅core面试/legacy_html/ACK和两种UI，**没有教学和记忆，不能当完整计划**；保留旧未执行计划，保存修正版本与hash。不要再次以“等待主控决定测试活动”为由启动/清场/返回。

独立阶段只依赖实际需要的父，不用一个未成教学阻断整个面试/HTML/UI。共享一次正常API和PG生命周期，阶段均在根内自动执行；每个成功/失败和源as-run独立留证。父已COMMIT时GET核证后继承，不再发送；新请求保留完整原键/批准/实际费用预留/007和领域结果，不以替身或隔离断言冒PG。

最终浏览器实际加载正式bundle并核响应hash；覆盖五入口等待/GET无副作用/原键继续及本卡新v2 owner/view/head/scope/namespace/DataContext晚到围栏。同阶段普通夹具修正可在卡内处理，不弱化正确断言。源码不变不重复build；前端产品实改才用剩余build绑定新字节。只跑原矩阵实际缺项，C12/旧S闭环/原未变审计不重复。

根15优先完整正常PG/SUP及权限/记忆/ACK-K2，根16仅确有必要的未成增量及UI；允许合并，两个余根不是必须用完。启动前冻结每根有限阶段与总时长，必须装进真实剩余截止及清场预留。不依赖PG运行时聊天投批，不将未执行计划当通过；相关同问题两次有依据修正仍失败须停止该问题，保留独立成果。

## 平台、资源、预算和停止

command038的自动审批服务原文为“Selected model is at capacity”，executed=false，未占根，无receipt。**它不构成需要新增预算的理由。** 原正常审批通道恢复后才提交更新后的必要预检，保留原阻塞记录，执行回执用独立新标识；不切模型/shell/连接器绕过，不反复发命令探测服务。服务未恢复时可做授权文件编辑/保存，不能运行被拦动作或下游。

当前counts/caps：根14/16、PGstart13/16、API9/16、Browser0/8、build4/6、Native9/48、HTTP54/5000；44失败记录及原117的81条历史保留。命令wall保守17553.845332/21600、持有1150.108295/14400；原两笔7200未知预留保留，不冲销，也不因换轮机械新增同额或重复计同一覆盖区间。未来受控命令实计、新未测量投入列实际边界上界，手工总工时不冒充0。主控没有改工程账；执行者收到本明确范围修正后append-only记采纳，计数/时间cap均不改。

固定CID b89522070d4b64fc67efed810852ccc21948058f154bf4fa1889f4d8d69a102f，名称retrolume-task120-qprep-pg1，volume retrolume-task120-qprep-data，image sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f；标签沿原TASK-120-Q-PREP-IMPLEMENTATION-20261018；1CPU/512MiB/pids128/restart=no/无host bind。PG127.0.0.1:55480/API18120。缺失/不符不替补，不碰旧六资源；逻辑库仅flow/budget01/budget02。新增create/真实费用/provider/preview/Git0。

最新Docker实时inspect曾permission denied，只继承09:47原停止；最新PID/Job/两端口观察不代替当前Docker状态。任何重开前先正常完成精确身份/状态检查，无法读则不启业务。PG/API最低512MiB、Browser768MiB，约2秒采样连续两次<256精确清场；不要求用户再释放内存，不关守卫。不满足只停相关层，不宣称“下一次一定成功”。

原首点2026-10-18T08:41:08.5687758Z、原截止2026-10-22T08:41:08.5687758Z不变，末1800仅保存清场；grant/活动更早截止不延长。每根1800秒/末120清场、元数据单批60秒/测试build子批300秒上限保持，按各层最短剩余门。过期不换库刷新批准，余量不够完整步骤不开始。

允许产品/测试文件范围、禁止001—014/依赖/锁/正式DocuS/公共库/旧证据/用户配置、SUP不触账、所有出站与金融主契约，均严格沿下方原完整合同。本卡不扩大公开接口、持久模型或正常启用权。新只写执行continuation-02子目录、原唯一账及指定结果，旧原件不可覆盖。

## 收尾、审计与回传

结束精确停本任务Browser/API/业务树，再停原CID，核PID/birth/命名Job、Running=false/Pid0、55480/18120无监听，保留数据/容器/卷/失败，不批删/drop/truncate/prune。若某维不可复核就明确时点及未知，不称全清场。

完整结果仍D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-120-result.md，新轮置顶且旧续作01/首轮原字节保留。交C01—C15及原最小矩阵逐项证据/复用/未跑、最终源/构建/fixture身份、准确累计账及精确StopProof；新模板/控制器最后未跑要标清，不以保存完毕自签通过。稳定完整后主控另安排原118独立归属集中终审，不逐小项审计，不自签Q/STEP018/019/020/M1/项目。

无额外用户决定/密钥/SQL/内存操作。用户人工转交本同号完整卡即可；平台容量无法由本卡保证。保存并复读后只回一句真实结论与可点击绝对结果路径。

---

# 以下为续作01及原合同，历史原字节保留；冲突以以上明确修正为准

'''

clarification = {
    'id': 'TASK-120-SCOPE-CLARIFICATION-02-20261019', 'issued_at': now,
    'task': 'TASK-120', 'R': 'R-114', 'resource_permit_unchanged': b['current_permit_id'],
    'new_budget': False, 'new_real_Q_authority': False, 'caps_unchanged': b['caps'],
    'allow_flow_A3_fresh_teaching_head': True,
    'allow_reserved_budget_02_creation_time_frozen_memory_A2': True,
    'memory_database_purpose_replaces_prior_budget_repair_only_condition': True,
    'fixed_roster_and_financial_limits_unchanged': True,
    'new_TESTONLY_expiry_no_later_than': '2026-10-19T12:19:22.457756Z',
    'retained_old_finances_unknown_slots_and_roots': True,
    'blocking_automatic_review_not_bypassed': True,
    'old_command038_not_run': True, 'main_did_not_execute_engineering_or_mutate_ledger': True,
}
save_json(HERE / 'scope-clarification.json', clarification)

state = f'''# 执行动态文档

文档v2.76，2026-10-19，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.48、task_model/07。以下v2.75原字节保留。

## TASK120续作01已返回；C12等有限成果收存，纠正两处测试起点，无新增预算

{now}。主控核7锁定规则、两产品真实增量及变化/新夹具/4正式bundle、旧报告原字节后缀、C12双backend同锁及root14同库重开。642身份是641文件加1个原已删除旧dist，并非642个现存文件；本轮仅重核实际变化与直接依赖，不重复全树产品或独审。

C12按真实对象收存通过：原budget-01 99→100竞争、两provider达限拒绝、48/28/24合计100/25000000及同库重开R0；旧learning一条原键COMMIT、九函数获准精确EOL修补继承。整体工程仍部分通过，教学、面试修补后PG/007、HTML description、权限/ACK/K2余项、最终五入口UI未闭合，未到稳定独审点。两产品q_context/q_protocol增量只有15项定向通过，不自签动态。

主控撤销上一A1 concept→numeric处方：slot_winner先于no-op效果，旧相同goal占槽，第一步即冲突；记忆正例也应创建时绑定而非重绑现成活动。两处属编排准备缺口，现明确准许原flow固定A3新教学head和原预留budget-02的A2创建时冻结memory选择，均只在原TESTONLY/固定roster/截止内；不改生产槽/DDL/权限，不释放A1旧UNKNOWN，不洗预算100账。第三库用途由预算修复备用改为记忆正反例，最大库数/唯一CID/卷均不加，新增有效期不晚于原flow 2026-10-19T12:19:22.457756Z。

最新真实累计根14/16、PGstart13/16、API9/16、Browser0/8、build4/6、Native9/48、HTTP54/5000、44失败记录（非44独立产品缺陷）；命令wall保守17553.845332/21600、持有1150.108295/14400，两笔7200未知预留和旧117全部历史照留。active_root/command空；15/16未启动。没有新额度，不新增TASK121；原工程窗口继续，待人工转交本次纠正合同。

command038最终预检被自动审批服务Selected model is at capacity拦截，未执行无receipt/无新根，区别于业务或资源额度失败。不换模型/shell/连接器绕过，不循环探测审批。当前仅可推进非依赖文件工作；服务恢复后仍需正常审批及精确CID状态核对。最新Docker实时inspect被拒，只继承2026-10-19T01:47:08Z原停机；新106PID/53Job/端口观察不等于当前Docker Running/Pid已确认。主控本轮未查询实时Docker或执行业务。

Q保持冻结，provider/实际费用/preview/Git新增0；STEP018整体/019/020/M1/项目未通过，原S有限验收不重开。没有用户新费用/密钥/SQL/内存动作，平台门非本卡可保证。详细裁定TASK-120-work-decision.md置顶02、同号完整TASK-120.md和orchestration-recovery-20261019；主控未改产品、工程结果、budget/events或原证据。CHG1527—1531，下一1532。

## 以下为v2.75及更早历史

'''
arch = f'''# 架构动态文档

文档v1.48，2026-10-19，Asia/Shanghai。需求v1.4、执行动态v2.76、task_model/07；以下v1.47原字节保留。

## Q v2预算门已有真实组合证据，完整工程仍未闭合

{now}。TASK120续作01产品仅q_context/q_protocol两项增量：面试封闭typed JSON键与原profile/prompt配对后的catalog取证；15项定向检查通过，修后真实面试PG/SUP未跑。前端源码/4正式bundle未改，build沿用，浏览器0；不因静态检查或dist存在签五入口UI。

新增真实C12同锁双backend99→100、两provider上限拒绝、同库重开100/25000000及R0，保留原PG金融权威。旧learning一条COMMIT继承。flow库九函数按用户具体批准精确修复CRLF/LF，目录指纹恢复、owner/ACL/其他目录与金融行不变；无新表/列、001—014文件不改，不将库内修补误写为零SQL。

教学原A1槽不具备目标切换路径，主控改用同固定名单A3正常新head；已选记忆采用原预留第三逻辑库创建时绑定。均为测试场景安排纠正，不改semantic_slot/no-op/金融/监督权限模型，不回退旧未知。K2/source-memory-scope-head/revoke完整剩余动态矩阵及收费启用边界未闭合，后续稳定点集中独审。Q/STEP018整体/019/020/M1/项目仍不放行，主控未实施运行产品。

## 以下为v1.47及更早历史

'''

# 写入前确认执行者没有继续写，避免按过期返回改共享状态。
for row in inputs:
    assert digest((ROOT / row['path']).read_bytes()) == row['sha256'], row['path']
write(decision_path, decision.encode() + old[decision_path])
write(arch_path, arch.encode() + old[arch_path])
write(state_path, state.encode() + old[state_path])
write(card_path, card.encode() + old[card_path])
entries = [
    (1527, 'DocuN/results/TASK-120-work-decision.md', '置顶断点裁定02，纠正A1槽/创建记忆安排，保留C12等通过事实，平台容量阻塞不追加预算'),
    (1528, 'DocuS/架构动态文档.MD', 'v1.48登记两产品增量、真实C12及获准九函数EOL；未签完整Q工程'),
    (1529, 'DocuS/执行动态文档.MD', 'v2.76登记续作01已返回/部分通过/平台阻塞/真实余量，同号纠正待转交'),
    (1530, 'DocuN/tasks/TASK-120.md', '置顶完整断点纠正02，A3新head/第三库创建时记忆/有限剩余链，无新额度，旧合同保留'),
    (1531, 'DocuN/evidence/TASK-120/orchestration-recovery-20261019', '有限增量及原件核证、范围明确JSON、共享旧字节/返回账快照与保存证明；主控无产品运行'),
]
addition = '\n\n' + '\n\n'.join(f'- CHG-{n:04d}，{now}，Codex编排Agent，{p}。{note}。' for n, p, note in entries) + '\n'
write(changes_path, old[changes_path] + addition.encode())
for path in (state_path, arch_path, card_path, decision_path):
    assert path.read_bytes().endswith(old[path]), path
for row in inputs:
    assert digest((ROOT / row['path']).read_bytes()) == row['sha256'], row['path']
save_json(HERE / 'save-proof.json', {
    'at': now, 'saved_and_read_back': True, 'prior_document_suffixes_byte_exact': True,
    'new_resource_budget': False, 'engineering_inputs_unchanged': True,
    'main_metadata_seconds': round(time.monotonic() - START, 6),
    'files': [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size, 'sha256': digest(p.read_bytes())}
              for p in (state_path, arch_path, changes_path, card_path, decision_path)],
})
print(json.dumps({'saved': True, 'rules': len(rule_checks), 'incremental_identities': len(source_checks),
                  'C12_barrier_and_reopen_checked': True, 'resources_added': 0,
                  'old_engineering_inputs_unchanged': True, 'next_CHG': 1532}, ensure_ascii=False))
