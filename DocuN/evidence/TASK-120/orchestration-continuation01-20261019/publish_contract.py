"""主控保存同号完整续作合同及前向许可；不修改工程账或产品。"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
E = ROOT / 'DocuN/evidence/TASK-120/execution'
assert ROOT == Path('D:/shspic/project_NO3_RetroLume-agent').resolve()
assert not (HERE / 'save-proof.json').exists(), '已保存，先核断点'
proof = json.loads((HERE / 'input-verification.json').read_text(encoding='utf-8'))
assert all(x['matches'] for x in proof['rules'] + proof['sources'] + proof['changed_preimages'] + proof['bundle'])
assert proof['package_matches'] and proof['source_count'] == 642
for row in proof['inputs']:
    assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
now = datetime.now(timezone(timedelta(hours=8))).isoformat()
permit_id = 'TASK-120-Q-PREP-CONTINUATION-01-20261019'
state_path = ROOT / 'DocuS/执行动态文档.MD'
arch_path = ROOT / 'DocuS/架构动态文档.MD'
change_path = ROOT / 'DocuS/文档变更记录.MD'
card_path = ROOT / 'DocuN/tasks/TASK-120.md'
decision_path = ROOT / 'DocuN/results/TASK-120-work-decision.md'
old = {p: p.read_bytes() for p in [state_path, arch_path, change_path, card_path]}
assert '文档v2.74' in old[state_path].decode('utf-8-sig')[:180]
assert '文档v1.46' in old[arch_path].decode('utf-8-sig')[:160]
assert not decision_path.exists()


def write(path, raw, new=False):
    if isinstance(raw, str):
        raw = raw.encode('utf-8')
    assert path.resolve().is_relative_to(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb' if new else 'wb') as stream:
        stream.write(raw)
    assert path.read_bytes() == raw


def save_json(path, data):
    write(path, json.dumps(data, ensure_ascii=False, indent=2) + '\n', True)


for path, raw in old.items():
    write(HERE / 'before' / (path.name + '.bytes'), raw, True)
for name in ['budget.json', 'events.jsonl', 'case-index.json', 'remaining-readiness.json']:
    write(HERE / 'returned-snapshot' / (name + '.bytes'), (E / name).read_bytes(), True)

new_caps = dict(proof['budget']['caps'])
new_caps.update(roots=16, pg_starts=16, api_starts=16, frontend_builds=6,
                native_business_sessions=48, http=5000)
permit = {
    'id': permit_id, 'issued_at': now, 'task': 'TASK-120', 'R': 'R-114',
    'kind': 'prospective_TESTONLY_same_scope_continuation_not_Q_activation',
    'parent_permit': 'TASK-120-Q-PREP-IMPLEMENTATION-20261018',
    'authorization': '用户已采用119完整包；主控在原实施/零外发目标内续发资源许可，不新增真实付费或权限模型',
    'old_counts_at_return': proof['budget']['counts'], 'old_caps': proof['budget']['caps'], 'new_cumulative_caps': new_caps,
    'additional_allowances': {k: new_caps[k] - proof['budget']['caps'][k] for k in new_caps},
    'actual_first_tool_utc_unchanged': proof['budget']['actual_first_tool_utc'],
    'calendar_deadline_utc_unchanged': proof['budget']['calendar_deadline_utc'],
    'save_only_last_seconds': 1800, 'command_wall_cap_seconds': 21600,
    'runtime_holding_union_cap_seconds': 14400, 'old_command_wall_upper_seconds_retained': proof['budget']['command_wall_upper_seconds'],
    'old_holding_union_seconds_retained': proof['budget']['holding_union_seconds'],
    'metadata_command_cap_seconds': 60, 'test_build_subbatch_cap_seconds': 300,
    'real_root_cap_seconds': 1800, 'root_cleanup_reserve_seconds': 120,
    'root_ids_begin_at': 9, 'old_failures_retained': 25, 'TASK117_old_failures_retained': 81,
    'no_new_container_or_volume_create': True, 'no_recreation_if_exact_CID_missing': True,
    'resource_labels_keep_original_permit_id': True,
    'container_id': 'b89522070d4b64fc67efed810852ccc21948058f154bf4fa1889f4d8d69a102f',
    'image_id': 'sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f',
    'container_name': 'retrolume-task120-qprep-pg1', 'volume': 'retrolume-task120-qprep-data',
    'ports': {'pg': 55480, 'api': 18120},
    'database_allowlist': ['retrolume_task120_flow', 'retrolume_task120_budget_01', 'retrolume_task120_budget_02'],
    'memory_minimum_MiB': {'PG_API': 512, 'browser': 768, 'stop_below_two_samples': 256},
    'old_financials_UNKNOWN_and_immutable_roots_retained': True,
    'TESTONLY_grant_and_activity_expiry_not_extended': True,
    'scope_addition_real_provider_fee_preview_Git': [0, 0, 0, 0],
    'only_executor_applies_after_actual_receipt_with_append_only_permit_history': True,
    'main_did_not_mutate_engineering_budget': True,
}

state_intro = f'''# 执行动态文档

文档v2.75，2026-10-19，Asia/Shanghai。唯一总状态账；需求v1.4、架构v1.47、task_model/07。以下v2.74原字节保留。

## TASK120/R114工程结果已返回且部分通过，合并续作01前向许可

{now}。用户带回真实TASK120结果，调度已返回；主控核7锁定规则、642源/文件身份、修改前副本、4最终bundle及6MB交付包一致。源相对root08-batch01只变flow/budget两夹具，batch02与当前被测集一致；已有19/2离线、typecheck/build和3条embedding提交按其原对象收存，不冒充教学model、共同100门或浏览器通过。工程总验收部分通过，完整候选未完成，不到集中独审稳定点。

原账8/8根、PGstart7/8、API5/8、Browser0/8、build4/4、Native4/32、HTTP31/3000；25登记失败含根/子批重复引用，非25独立产品缺陷。命令wall保守9538.921332/14400（含1840.326332上界及7200未知预留）、持有267.641/10800保留，手工阅读/编辑unknown不改0；原117的81失败与全部旧累计不动。原active_root/command空，2026-10-18T23:49:19Z停止证据核8 Job/23 PID-birth及精确CID Running=false/Pid0、55480/18120不监听；这不是主控现时Docker查询，旧六对象未重采。

已确认接续依据：UNKNOWN旧教学键与semantic slot不能靠abandon或同目标无效果保存释放；C12旧300秒运行预留只能生产折叠，命令应先accepted/准备批准再claim执行；root08的60秒外部子批等待使budget指令晚于退出，未执行。续作应一次检查全部父槽/retain/checkpoint依赖，冻结有限内部队列后自动串行，普通修正卡内完成，不用换key、重绑、SQL清账、外部迟到指令或新增grant刷旧未知。

本段只登记同号续作，未占TASK121。原A+工程窗口继续；新的前向累计上限根16、PGstart16、API16、Browser8、build6、Native48、HTTP5000，命令wall21600/持有14400；新增create/provider/费用/preview/Git均0。唯一CID b8952207…102f及卷/三逻辑库/55480/18120保持，失踪不重建；TESTONLY root/活动有效期不延长。原首点2026-10-18T08:41:08.5687758Z、原截止2026-10-22T08:41:08.5687758Z与最后1800保存不变，root从9、命令从29续号，旧失败/未知预留不清。PG/API512、Browser768MiB/两次<256精确收尾，不要求用户再释放内存。

Q仍冻结，真实100/25只是既有条件采用而非本次新费用；正常账号/价格税币/token-framing-reasoning/returned identity/集中独审/主控首次启用仍缺。旧S有限验收、永久readonly/source冻结不重开，STEP018整体/STEP019/020/M1/项目未通过。新卡不会提前派独审，稳定完整后原118独立归属核新增边界。

主控仅只读源/证据/元数据核证与共享维护，无产品import/compile/测试/build/SQL/Docker/API/Browser/Job/模型/费用/Git写；工程账和原报告未改。GitHub非忽略范围授权与既有main6302b0c保留，Git快照不是120最终证据，执行者Git预算仍0。完整采用/断点裁定DocuN/results/TASK-120-work-decision.md，许可及核证DocuN/evidence/TASK-120/orchestration-continuation01-20261019，完整合同DocuN/tasks/TASK-120.md。CHG1522—1526，下一1527。

'''
write(state_path, state_intro + '续作01调度：已登记，完整合同正在保存；尚无真实转交/接收证据。\n\n## 以下为v2.74及更早历史\n\n' + old[state_path].decode('utf-8'), False)

decision = f'''# TASK-120 / R-114 主控核证与续作01裁定

{now}。调度已返回；总验收**部分通过，仅收存工程候选和明确已满足证据，完整目标未完成**。不签稳定包、不启动独审、不启Q；同号续作01由原A+窗口一个完整成果接续。

7锁定规则、616既有文件+26新增=642身份、全部已改源preimage、4最终bundle、6,018,061字节ZIP实核匹配；ZIP SHA256 462f0c57bda62dfdbbb946d9af497f951b0e295c3c0aa8e8d6c7516781a07ffe。command025/026/027/028各exit0、树零；19和2项按原隔离/功能对象分级，typecheck和构建不替代UI。root08-batch01当前差异仅flow.py/budget.py，产品无差；batch02当前全表一致。三条embedding真实提交按原请求/代次/007/领域结果留证继承，不签停止后SUM重新回读。

报告、原账、失败、停止证据的读入指纹见本段input-verification.json；主控未跑任何产品/PG/Docker/浏览器或重做独审。8精确Job、23 PID/birth、CID停/Pid0及端口不监听，只核证2026-10-18T23:49:19Z原件，不虚称新实时清场。

C09：旧claimed UNKNOWN键永久保留；同目标body在teaching_repository.py625—637明确no-op，canonical_request_body含expected revision/goal version，semantic_slot绑定实际父记录。新的合法父场景须用生产local命令形成真实不同父记录并回读，再准备新意图；本地中间目标不发送。已有两错误路径留存，新增依据是函数级事实和完整上下游槽对账，不是清零失败再撞同一槽。

C12：旧running R300不能直接refund/置零；只按生产过期折叠/真实新窗结算处理。最终修正尚未运行，99基线及两backend竞争不成立；续作必须逐笔真实准入积累47/28/24、99/24750000，同A1合法租约两provider争最后slot，最终新连接100/25000000，两provider达限拒绝及同库重开。

控制器：merged.py等待外部下一文件仅60秒，原budget指令晚于root08清场9.240832秒，无child/receipt不得算已执行。续作调整为启动前有限冻结计划/依赖图并内部自动串行，逐阶段留as-run/真实exit，不在有PG持有时依赖聊天再投下一批。失败不改绿，不以固定previous_exit=0跳失败，独立子目标可在原根期限内继续。

前向许可为{permit_id}；累计根8→16、PG/API上限各8→16、build4→6、Native32→48、HTTP3000→5000，Browser8不变；命令wall14400→21600，持有10800→14400。旧9538.921332保守wall/267.641持有、25登记失败、原117历史全保留，原96h截止不变；资源仅原唯一精确CID/卷/三TESTONLY库，新增create/真实provider/费用/preview/Git0。执行者真实收到后才向原budget.json追加permit_history和上限，主控没有代改工程账，不追认过去动作。

未改变需求/持久模型/公开权限/金融规则，不需用户重复批准100/25、密钥或释放内存。任务完整后集中增强独审另卡，原118只接受目标/约束/最终差异/原始证据，不接收实现完整聊天/思考。其余官方账号/真实启用门单列，不阻塞零外发工程。详细合同见同号TASK-120.md置顶续作01。
'''
write(decision_path, decision, True)
save_json(HERE / 'permit.json', permit)

contract = f'''# TASK-120 / R-114 — 续作01：Q v2完整工程与剩余PG/UI合并闭环（当前有效）

## 目标、接收窗口与完成终点

接收Agent：**A+增强工程，继续刚返回TASK120的原TASK119/117工程窗口**。这是同一未验收成果的完整接续，不新占TASK、不启动独审、不重新设计。真实客户端/可知模型如实记；不因标签追问已完工作。不自动委派子Agent、不并行第二实施者；只有原窗口确不可用，才允许同等胜任A+新窗独占接续，原窗停止。

一次完成剩余教学/面试query→已批准model→007及领域COMMIT、旧learning/HTML等待与原键继续、权限/丢确认/K2并发、真实PG共同100门和最终正式bundle UI。范围内普通实现/夹具修正、定向验证、精确清场连续做完，达到完整稳定可审包再统一返回。已有足够证据直接复用，不把本卡拆成修一个fixture/补一项的小卡。

你只交事实与工程候选，主控裁定。**Q继续冻结，真实provider/费用/preview/Git新增均0**。未来100次/25元是用户已采用的条件上限，不是本卡可花费用，不需用户重批/给key/释放内存。真实账号、计量、返回身份及正常启用门UNKNOWN不阻塞零外发工程，但不能伪填为ready。

## 项目、规则、优先级与输入

根D:/shspic/project_NO3_RetroLume-agent；入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。task_model，锁定V4.0/公共AGENTS CHG-0003，七指纹仍全部匹配；公共只读根D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，DocuS/AGENTS.MD、WORK.MD第2/5/6/8/9章、task_model/prompts/07_开发执行循环.md与TASK_TEMPLATE。原窗已读同版内容复用，仅补变更。

本次口径需求v1.4、架构v1.47、执行动态v2.75，STEP018关联原TASK120全部需求/架构/父项。采用仍为用户2026-10-18对119完整包的批准。**本置顶续作01及本段permit优先于下面原卡相应运行额度/调度/Git公开范围旧描述；其余原A—D、完整最小矩阵、产品允许/禁止文件继续有效**，不是重授未列权限。

按序读下列真实文件，已读且未变不重读全部：

1. 根入口、锁定规则及DocuS/执行动态文档.MD置顶、架构动态文档.MD置顶。
2. D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-120-work-decision.md及同目录TASK-120-result.md，后者是本次交回原件，不能覆盖历史。
3. D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/orchestration-continuation01-20261019/input-verification.json、permit.json。本次642文件/修改前副本、4 bundle、ZIP全匹配；它们就是接续基线，不用GitHub6302b0c覆盖本地新成果。
4. D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/execution/下budget.json、events.jsonl、case-index.json、remaining-readiness.json、final-stop-proof.json、root08-next-batch-timing.json、root08-unexecuted-next-batch.json、flow-committed-receipts.json、final-file-identities.json、source.diff和final-bundle-identities.json。只读旧失败原件，不执行旧晚到指令。
5. 下面原卡完整A—D/原许可及TASK119采用K1/K2原件；同窗未变直接继承。原TASK116 sample-inputs冻结文字和实际finite/provenance仍有效，不自行扩大文字白名单。HTML TESTONLY许可沿本次html-testonly-adoption.json/command021正常host身份，不准启preview。
6. 当前backend/tests/fixtures/task120/flow.py、budget.py、merged.py、ui.py、run.py、resources.py，DocuN/evidence/TASK-120/execution/runtime_control.py及command_control.py只读作旧控制依据；实际teaching_repository.py的local goal/no-op、semantic_slot与claim/结果路径，q_context/q_store/主进程与worker锁路径。只补直接依赖，不重审整仓。

## 已收存、真实断点与必须先修的同链问题

本轮原报告是**未完成**。19项定向、2项正常配置与typecheck/build有原exit0；多为隔离证明，非真实PG currentness。3条embedding实链（一次source_index/两次query）有原HTTP/Windows/PG/007/领域提交；root08-batch01仅flow/budget夹具后来改变、产品无差，batch02与最终被测表一致。这些事实保留，不为补model再次重跑原成功三条，除非新差异确影响其路径。

原账8/8根、PGstart7/8、API5/8、Browser0/8、build4/4、Native4/32、HTTP31/3000；25条失败登记含根/子批重复引用，不等于25独立缺陷。旧UNKNOWN键1f5c659f-4a5a-4fee-bfbe-3f245eb5bc7e已claim，不能再发，原PG只读观察时operation/请求费用预留0不等于现在可放行/可清账。旧budget运行R300的原耗时未知，不能当0或退款。

先一次修正整条fixture和调度链，不能只把第一处错误改到下一处再停：

- **合法新父槽（C09及后续C11/UI共同前提）**：abandon UNKNOWN不释放其语义槽；teaching_repository.py625—637相同goal body确为no-op，换business_key不能改变父。可在原固定A1/原grant内，通过两个明确、合法、冻结文字的本地goal动作形成真正不同父，例如仅本地先切到已有concept_goal，再明确回到numeric_goal；中间不发送概念模型、不改N资料范围。canonical request含实际expected revision/goal version，semantic slot绑定真实父；每步回读确认record/revision/goal_version确变化，最终仍是数字目标/N来源，再准备新的独立意图。该例是已授权fixture细节，不能改业务no-op规则、改semantic_slot、重绑活动或SQL清UNKNOWN。若实际原资格/版本不允许，不硬做，不换grant重试。
- 所有旧retain键、旧冻结body、失败命令和UNKNOWN保持；不要把已缓存expected_revision=1的请求就地改成新body。新场景名/新意图只在真实新父成立后生成，旧未claim原键只有完整冻结体和当前资格都合格才原键显式继续。预先对账正常plan/exercise、release-gap plan、UI后继的全部父槽；不能修好首次plan后又在同父重复plan。
- **预算顺序（C12）**：先accepted/准备/真实operator批准及launch资格，再claim lease执行；按真实monotonic在窗关闭后settle，下一笔再accepted。未结算的旧R300先核旧身份/过期及原StopProof，只有生产原过期折叠或既定保守取消规则可核销；不伪造过去elapsed，不手改活动/operation金融行。已有budget.py修正是候选不是已跑证明，必须读实际生产函数对账全循环、最后竞争与post100探针。
- **消除60秒外部投批依赖**：原merged.py等外部写下一文件60秒后退出，root08 budget文件晚到退出9.240832秒，没有child/receipt。续作在启动前固定有限阶段列表、前置/依赖、单批上限和失败分支，由根内控制入口自动串行执行；不启动PG后再等下一次聊天/工具提交文件，不沿旧root08恢复。每阶段保留真实previous exit/独立as-run，不能硬设0跳失败；某链失败只阻其真实依赖，预算/已满足前提的UI等独立目标可在同根原期限内继续。新故障需修正时先确认该阶段子树已净；原根deadline不延长。

旧两条失败路径不清零。此次继续的依据是上述函数级事实、真实父槽计划和有限自动队列；若新路径仍落回同一unknown_slot且无新的可核解释，立即停该相关链，不继续换键撞槽。新问题两次有依据修正仍失败的停止规则继续。

## 一张卡内的剩余完整成果与证据标准

继续完成原卡全部未满足矩阵，不能只跑下面摘要后称整卡通过。用实际case ID/方法/场景写出已有覆盖、这次补证和仍UNKNOWN：

1. **五入口正常链与恢复**：教学、面试各至少一条实际query已提交→model pending→GET不写→operator逐请求精确批准→原冻结key显式POST→真实Windows SUP/worker→生产admit/mark→007与领域COMMIT。旧learning与HTML description各一条等待/GET恢复/原键继续；同key异体409、未批准零发送、claim/UNKNOWN不重发、准备ACK/claim ACK/COMMIT ACK分别只读对账。既有3 embedding成功引用旧原件，仅新必需query新增。全部供方实际网络由最低transport替身封闭，真实供应商/费用0。
2. **有限来源和新权限反例**：已选memory正常model至少一例；未批准answer/history/memory/标题、foreign parent/实例副本、artifact缺/日志换身及相关readonly/恢复拒绝按原最小矩阵补足。完整request/provider对象/实际规范发送bytes及parent资格都核；不可把隔离字符串检查或旧S08当新v2 PG通过。原wire3/v1充分原件继承，原wire4只补新传播实际影响，不默认全仓回归。
3. **K2实际竞争**：正常model结果必须可落地；source/memory/scope/head/revoke按受影响边界给真实锁/屏障窗口，分开临界前拒绝、已准入NOT_SENT、可能已送UNKNOWN。尤其共享发送锁释放后排他变更先完成，007不可变结果及费用保留、head不误推进；两端线程/PG connection身份与时序可辨别，不能外层串行冒并发。main.selection_guard Q短锁、launcher父data permit释放、owned_service Q注册缩短要证明直接传播，不借改非Q生命周期/恢复规则解死锁。
4. **真实共同100门**：优先原budget-01，不清其历史。逐笔生产真实准入47/28/24→SUM99/24750000，两provider在同A1合法lease争最后slot，真实两backend/同固定全局advisory锁/原SUM/同事务预扣COMMIT，最多一个成功；新独立连接最终100/25000000，输方零发送，达100后两provider拒绝、账不变。UNKNOWN/超时/已准入确定NOT_SENT都保留费用。实际停止再同库重开核权利不复活。原budget-02只在第一有具体修正且确需隔离复证时按原许可初始化，旧库保留，不是新收费余额。不可伪造99但两个活动都余一slot、或99次已25元等不可达前提。
5. **最终UI与正式字节**：源未变的最终JS 7cd5ed25…456b07、CSS6f02da29…9e8b94及index/PDF worker哈希可复用正式build；不要为恢复对话重build。若实际frontend变化，受新build额度约束重建，绑定真实Browser响应JS/CSS hash。教学/面试等待批准后显式继续、检索批等待、legacy/HTML恢复入口、刷新/重开仅GET、draft保留，旧owner/view/head/scope/DataContext/namespace迟到不推进/不额外POST。请求时间线锚定显式动作，避免把显式POST本身计作“之后自动POST”的旧夹具错误。仅description，不启动固定preview。
6. 最终实际SUM新连接回读、case-index/readiness、原/新差异及pre/post/as-run、最终包和StopProof齐备；成功按子项实际字节分级，任何旧失败批不改绿。正式最终稳定点后才交主控安排一次独立增强审计；不在本卡自签，不提前让独审窗口参与修实现。

## 允许修改、所有权与禁止

下面原卡允许的产品/前端/测试/配置示例/README/deploy说明范围保持，仅新协议和直接影响的必要修正；修前preimage/hash，差异能追溯A—D。现代码/最终bundle是候选，不以“只是验证”拒绝卡内必要普通产品修复，也不借机改业务提示/推进标准。

现行backend/tests/fixtures/task120可改，保存本轮preimage和fixture.diff；前端夹具仅task120-*.mjs。主控本段orchestration只读。旧roots01—08、command001—028、旧source.diff/ZIP/receipts原件不覆盖；旧runtime_control.py/command_control.py如需改控制，先封存其hash和原字节，再在D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/execution/continuation-01/保存明确新控制副本和计划，纠正文件层级ROOT/manifest路径，不跑旧晚到指令。产品不能import这些临时控制；唯一实际账仍为原execution/budget.json及events.jsonl，新的permit_history追加，不平行第二本活动账。

原始需求、DocuS/共享CHG、公共库、001—014/金融模型/角色profile、旧source与恢复selector、固定renderer/host/Job/时钟主体、依赖锁/安装/联网模型保持禁止。新的公开权限、主要模型、DDL或持久金融语义变更须停依赖并报具体最小差异。原非Q锁/兼容不顺手改写。禁止直接SQL改请求/费用/预留、清日志、revoke冒独立delete、手动重绑grant或用新实例刷余额。

Git项目范围已由用户2026-10-18更新为除.gitignore外均可公开，主控已同步main；这覆盖下面原卡“不上传DocuN”的旧全局表述，但**不把Git执行授权移给本卡，Git写额度仍0**。源码可能比公开快照新；不得checkout/reset用Git旧版覆盖候选，也不得上传私有目录或输出凭据。

## 前向追加资源许可与原账继承（必须精确执行）

许可ID：{permit_id}，完整机读文件D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/orchestration-continuation01-20261019/permit.json。主控已批准本表的零外发续作，不再向用户索要同一预算批准；收到后先核原账与原停止证明、实际资源身份，再把许可ID/时间/原cap/新cap追加到原budget的permit_history，保持counts/roots/events/failures全部旧前缀和首点。主控未代改工程账，不追认此前超限或未执行动作。

| 项目 | 本次返回已用 | 旧上限 | 新累计上限 |
|---|---:|---:|---:|
| 真实运行根 | 8 | 8 | **16**（新根从9） |
| PG starts | 7 | 8 | **16** |
| API starts | 5 | 8 | **16** |
| Browser starts | 0 | 8 | **8**（不追加） |
| 正式build | 4 | 4 | **6**（仅确实需要时） |
| 真实业务SUP/worker会话 | 4 | 32 | **48** |
| HTTP | 31 | 3000 | **5000** |
| 命令wall保守累计秒 | 9538.921332 | 14400 | **21600** |
| 自有资源持有并集秒 | 267.641 | 10800 | **14400** |

新增create/实际容器/卷/preview/provider/实际费用/Git均0；旧create未用余量在本续作也不用于重建。8根是余量上限，不是必须用满的计划：尽量将可共用PG生命周期的有限阶段合并，新增根只因明确需要/修正/阶段隔离，充分即停。

唯一CID b89522070d4b64fc67efed810852ccc21948058f154bf4fa1889f4d8d69a102f，retrolume-task120-qprep-pg1；卷retrolume-task120-qprep-data；image sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f，原label含retrolume.permit=TASK-120-Q-PREP-IMPLEMENTATION-20261018保持（新许可不会逼你改标签/重建）。固定PG127.0.0.1:55480/API18120、1CPU/512MiB/pids128/restart=no/无host bind；逻辑库仅原flow/budget-01及有条件budget-02，CID/卷/金融行/unknown/journal保留。精确对象丢失/身份不符就停依赖，不建替补，不查改旧六资源。

原首工具2026-10-18T08:41:08.5687758Z，**原截止2026-10-22T08:41:08.5687758Z不延长**，最后1800秒仅保存/清场。已有TESTONLY不可变grant及活动deadline可能更短，先核自己fixture有效期，不延长、不重绑；到期不能刷有效期或另换库恢复权利。每根最多1800秒、末120精确清场；离线元数据单批60秒/测试build子批300秒，各层按剩余日历/命令/持有/计数/fixture权限最短截止，不拿跨中断日历差当CPU。

旧1840.326332上界、7200未聚合元数据不确定性预留继续占账，9538.921332不是精确投入，不冲销；手工阅读编辑unknown不能记0。新的runtime控制副本要将原硬编码10800持有门改为明确读取本许可14400上限并受原账约束，不能改成无限/default免费；记录实际源diff。命令从29续号，新证据加continuation01或新root前缀，旧失败25条及TASK117原81条保留，不拿新轮次清次数。

PG/API最低512MiB，Browser768MiB；约每2秒采样，连续两次低于256MiB停止新增、精确停自有Browser/API/业务Job/PG。内存/系统端口门不满足只停相应层，不反复要求用户释放内存，不改系统保留端口/杀占用进程/重启Docker；没有实际运行不假造通过。每次启动尝试包括未ready计数；离线只读/hash/edit不是运行根，任何实际runtime都从有界入口计根，不借裸命令绕账。

## 整卡顺序、停止、集中审计与回传

先保存本次fixture完整修正和有限计划，做必要小范围离线控制/槽身份/字节检查，再用当前实际可执行入口串行跑PG/HTTP/Windows/最终UI和budget，独立子目标不被无关单个失败全挡。启动计划必须已经齐全，不持PG等待外部工具再投下一批；先算完整阶段时长能否装入原根剩余，装不下准确收尾后用真实余根，不能超时外塞指令。运行不可能由静态检查保证首遍成功，未知按事实处理；不是再写准备提案后停。

完整充分即停。相同问题已有失败/修正次数跨轮保留；无新依据不再机械重试；两次有据修正仍失败、根因不稳、主要前提/新权限模型变化或硬门到达，停受影响部分并完成可独立工作后统一回报。平台审批拒绝记录并停止该动作，不换壳/提权绕过。任何StopProof不完整先处置精确本卡资源，不再开根。

末次先停本卡Browser/API/业务树，后停精确CID；核PID/birth/命名Job、容器Running=false/Pid=0、55480/18120不监听。保留数据/原件，不prune/drop/truncate/批删。主控只继承原停止时点，不声称替你实时清场；你在本次重开和最终停线必须更新真实证据。

完整结果仍为D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-120-result.md，置顶“续作01”，**本次返回正文完整原字节保留**。新证据DocuN/evidence/TASK-120/execution/continuation-01及原唯一账；旧原件只引用。给最终源/构建/fixture差异和as-run、C01—C15及原最小矩阵逐项映射、正确SUM回读、失败/投入/余量/偏差、精确StopProof、工程与真实Q readiness分开、独审输入索引。

稳定完整后由主控另卡集中独审，优先原TASK118独立归属，未占新号、不在本卡自签；旧充分证据不全量重做。README/部署说明/架构建议如实列，DocuS及CHG由主控维护。没有必要用户密钥/SQL/内存操作；用户仅人工转交本卡。完成保存并复读后只回一句结论与可点击完整绝对结果路径，不贴完整长报告，不宣告STEP018/019/020、M1、项目或收费Q通过。

---

# 以下原TASK-120合同原字节保留；与上文冲突处以上文明确续作/用户授权为准

'''
assert card_path.read_bytes() == old[card_path]
write(card_path, contract.encode('utf-8') + old[card_path])
arch = f'''# 架构动态文档

文档v1.47，2026-10-19，Asia/Shanghai。需求v1.4、执行动态v2.75、task_model/07；以下v1.46原字节保留。

## Q v2工程候选已落地，PG/model/UI尚未完整验证

{now}。TASK120/R114已真实返回；协议q_protocol/q_context/q_gateway、私有q_store/q_kernel和本机operator、教学/面试/检索/legacy learning/HTML五入口的准备/等待/GET/原键继续及配置/UI实现候选已保存。零DDL、原001—014及金融主模型未改，候选deepseek-flash与embedding-3/512、共同100/25和固定48/28/24采用范围保持，未启真实收费。

主控642身份/修改前原件/4正式资产及ZIP核对一致；19+2定向及build有实际原件，三条embedding经真实HTTP/Windows/PG/007/领域提交；这不证明教学model/面试/legacy/HTML完整链、source-memory-head/revoke并发、同库99→100共同门或UI通过。Browser0。最终正式文件hash固定而非浏览器加载实证，架构验证状态为部分验证。

K2候选实现涉及main.selection_guard Q分支缩短锁并在返回前核身份、worker.launcher Q交接后等待前释放父data permit、owned_service Q注册段缩短。仅按实际diff登记，非Q/原恢复生命周期不得改写；正常model落地、间隔失效保留007与费用而不推进head，必须定向组合验证并在完整稳定点由独立增强审计核新权限及传播，不据注释/隔离测试通过。

本次断点为UNKNOWN旧父槽/相同goal no-op、旧预算R300及未跑的逐笔顺序、外部60秒子批窗口导致晚到指令。合法真实新父/生产fold与close/完整冻结内部队列由同号续作01一次处理；不改语义槽、时间账/金融规则、批准权限模型或持久结构，不将测试排程问题升级为新架构平台。原有限S已关闭，旧充分审计不重开。

新前向资源许可只在原唯一TESTONLY CID/卷/三库零外发内追加，详见120-work-decision与permit；不延长原96h或不可变grant/活动deadline，不重置旧账。源码候选未形成完整放行，Q/STEP018整体/STEP019/020/M1/项目仍未通过；正常启用仍缺适用独审/账号计量/严格身份/主控首次回执。主控未实现或运行产品。

## 以下为v1.46及更早历史

'''
assert arch_path.read_bytes() == old[arch_path]
write(arch_path, arch.encode('utf-8') + old[arch_path])
write(state_path, state_intro + '续作01调度：待转交，完整合同及许可已保存可读；尚无真实转交/接收/开始证据。\n\n## 以下为v2.74及更早历史\n\n' + old[state_path].decode('utf-8'))
entries = [
    ('1522', 'DocuN/results/TASK-120-work-decision.md', 'R114实际核证：工程候选部分通过、完整目标未达；明确可继承证据/缺口/新运行许可，不启Q。'),
    ('1523', 'DocuS/架构动态文档.MD', 'v1.47登记Q v2真实候选模块/五入口及K2短锁/父permit风险、部分动态和剩余集中验证门。'),
    ('1524', 'DocuS/执行动态文档.MD', 'v2.75将120登记已返回/部分通过、同号续作01待转交，真实旧账/停止时点与前向累计上限分层。'),
    ('1525', 'DocuN/tasks/TASK-120.md', '置顶一个完整续作01：合法父槽/逐笔预算/有限自动队列与剩余PG/UI一次闭环，原合同后缀保留。'),
    ('1526', 'DocuN/evidence/TASK-120/orchestration-continuation01-20261019', '642源及7规则/构建包/回执只读核证、原共享与工程账快照、精确追加许可和完整保存读回。'),
]
addition = ''.join(f'\n- CHG-{n}，{now}，Codex编排Agent，{p}。{d}\n' for n,p,d in entries)
assert change_path.read_bytes() == old[change_path]
write(change_path, old[change_path] + addition.encode('utf-8'))

assert card_path.read_bytes().endswith(old[card_path]) and state_path.read_bytes().endswith(old[state_path])
assert arch_path.read_bytes().endswith(old[arch_path])
for row in proof['inputs']:
    if row['path'] == 'DocuN/tasks/TASK-120.md':
        continue
    assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
assert len(contract) > 9000 and all(p.exists() for p in [state_path, arch_path, decision_path, card_path])
save_json(HERE / 'save-proof.json', {
    'at': now, 'task': 'TASK-120', 'R': 'R-114', 'dispatch': '待转交', 'acceptance': '部分通过',
    'Q': 'FROZEN', 'old_state_arch_card_suffix_original_bytes_preserved': True,
    'engineering_report_budget_events_and_products_not_mutated': True,
    'new_TASK_or_R_allocated': False, 'main_product_runtime': False,
    'files': [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size,
               'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
              for p in [state_path, arch_path, change_path, decision_path, card_path, HERE / 'permit.json']],
    'card_complete_readback': True, 'CHG': '1522-1526', 'next_CHG': 1527,
    'next_step': '人工转交原A+工程窗口完整续作01，稳定后一次集中独审',
})
print(json.dumps({'saved': True, 'state': 'v2.75', 'architecture': 'v1.47', 'dispatch': '待转交',
                  'task': 'TASK-120', 'card_bytes': card_path.stat().st_size,
                  'result_received_sha256': next(x['sha256'] for x in proof['inputs'] if x['path'].endswith('TASK-120-result.md')),
                  'new_caps': new_caps, 'engineering_budget_unchanged': True}, ensure_ascii=False))
