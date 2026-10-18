# TASK-086 / R-080 — 受控one_call接线独立增强审计结果

审计完成时间：2026-09-28。审计者：独立增强审计Agent（全新隔离会话，未参与085实现）。

## 0. 一句结论

**085实际新增接线在批准的内部切片内具备编排验收条件：无阻断项**；发现1个非阻断低危缺陷（N1：SessionConfig.request_timeout_seconds无上限与worker侧≤120秒解码上限构成配置死区，失败关闭）与若干观察项；建议编排验收关闭085，本审计不签编排最终验收。

## 1. 独立性、实际身份、接触范围、冻结稳定性

- **独立性**：全新隔离会话执行本卡；未读TASK-085-result.md、delivery-check.json、085实现聊天/自评、完整共享状态与客户端项目记忆。全部结论由当前源码与Ndocu/evidence/task-085/原始证据独立形成。
- **意外接触披露**：读取PROJECT_ARCHITECTURE.MD文件头部时接触到顶部v0.49"one_call候选回收与独立审计"编排条目（编排验收状态摘要，非实现自评）；除此之外零接触禁读材料；结论未采信该条目任何断言。
- **实际执行身份**：本会话由当前客户端最强可用模型执行（GLM-5.3，会话内最高可用推理档）；按卡面要求如实记录，未因标签重新审查已完工作。
- **接触范围**：只读根AGENTS.md、公共docu/AGENTS.MD、TASK-085.md原合同（含其顶部2026-09-28执行回传状态注记）、架构FLOW-005原文与批准边界、卡面指定源码/测试/夹具/原始证据；未运行任何测试、未启动任何资源、未import/compile被审代码（compile除外——未执行，仅静态阅读）、未做Git操作；仅写Ndocu/evidence/task-086/与本结果文件。
- **冻结稳定性（证据见本卡证据目录freeze-verification.json）**：
  - 卡面4项冻结输入SHA256全部重算MATCH（post-hashes/pre-hashes/task085.diff/真实批manifest）。
  - post清单52项逐条独立重算与当前实际文件比对：0不符。
  - pre清单59项独立重算：仅7个worker文件相对pre变化且全部登记于post，无未登记暗改；全部只读依赖（gate.py、windows_job.py、activities/repository.py、capabilities六文件、runtime.py、001—006迁移、test_worker_session.py、test_capabilities.py、main.py、AGENTS.md等）当前hash=pre。
  - git status pre/post逐行一致，仅新增两处卡面允许路径（Ndocu/evidence/task-085/、backend/tests/test_worker_one_call.py）；既有未提交tracked差异未被085触碰。
  - 完整差异由pre副本+当前源码+新增文件组成（independent-diff-pre-vs-current.txt），不以git空diff证明无变化；worker此前未跟踪这一事实已按卡处理。
  - 冻结输入漂移为0，本卡对"当前内容"签发结论成立。

## 2. 与085原合同逐项对应结论

| # | 原合同（TASK-085 §3/§5） | 独立结论 | 关键证据 |
|---|---|---|---|
| A1 | 类型化one_call入口，activity/executor/runTag严格校验，G/scope派生自claim | 通过。run_one_call只收activity/executor/operation/request/service/config；G/scope/W_eff全部来自claim返回的ActivityLease（session.py:249-254用lease字段构造context；worker_request由lease派生），调用者无任何代次/窗口输入通道 | one_call.py:168-183、session.py:268-275 |
| A2 | 固定解释器/模块/cwd/有限任务枚举；无任意exe/argv/模块/路径 | 通过。argv=固定解释器+`-B -m app.worker.worker_main`+任务枚举+校验过的映射名（command.py:28-35）；SUP同构（launcher.py:100）；消息层为纯数据，无模块/路径/代码加载点 | command.py、supervisor_main.py:24-65 |
| A3 | claim None/旧租约/来源失效/取消/输入非法不得启动有出站资格的worker；idle保留；缺数据明确失败 | 通过。六个拒绝节点全部位于spawn之前且账目保守（见§4动态行）；idle全链保留（worker入口返回0、SUP idle不携带one_call数据、argv拒绝映射名）；缺数据在launcher/_request、SUP _validated_request、session.run_once、worker argv四层显式失败，不静默降级为idle | 各场景原始行 |
| B1 | 配置/请求经固定启动链交worker，有界回传，容量/schema/完整性/所有权/关闭时机记录 | 通过。双层映射：launcher→SUP（SUP请求，协议2）与SUP→worker（exchange，协议2）；1MiB映射=两个512KiB槽；36字节帧头（长度+SHA-256）；写序零长度→体→长度（提交标记）；请求先于Resume写入、结果仅在子进程退出后读取；DACL显式（见B3）；句柄不继承；拥有者close先memset整映射再Unmap再CloseHandle | supervisor_ipc.py全文 |
| B2 | 写前限长，与ModelServiceConfig协调，内部限额更小时明确拒绝不截断；未知字段拒绝；校验和不等于身份认证 | 通过。两层显式拒绝：服务配置max_request/response_bytes>64KiB在to_wire抛错（one_call.py:57-58，非截断）；载荷128KiB合同上限在bounded()以序列化后长度度量（转义膨胀已计入）；exact()全层严格set相等拒绝未知/缺失字段；帧校验和仅完整性。生产可用替换通道不存在：无任何transport/command选择器进入产品 | one_call.py:22-44、各decode |
| B3 | DSN/key/正文不进argv/日志/证据/Git；受控短生命周期通道；测试用新合成凭据 | 通过。DSN仅经映射（worker_request携带self.ledger._dsn）；api_key仅进映射帧；argv无秘密（离线断言+静态核验）；worker/SUP异常路径零输出（BaseException→静默exit）；gateway日志仅事件码+异常类型名；repr=False覆盖request/service/model_receipt/正文；真实批口令运行期生成、经env与映射传递、日志脱敏；本审计对085全部证据文件做口令/DSN/api_key模式扫描零命中 | worker_main.py:78-80、supervisor_main.py:86-88、gateway.py:34-36、证据扫描 |
| B4 | Windows DACL/所有权/非继承/权限/零化顺序/失败路径；不声称抵御同用户恶意进程 | 通过。create用SDDL `D:P(A;;GA;;;OW)(A;;GA;;;SY)`（保护DACL不继承、仅所有者与SYSTEM全权）；bInheritHandle=False；ERROR_ALREADY_EXISTS视为冲突失败关闭（防名字蹲点劫持）；随机名128位熵+校验和不作认证（代码注释如实声明同用户受信边界，符合D3单机前提） | supervisor_ipc.py:105-154 |
| C1 | 真实gateway/账本，ClosingCallGate，一次调用，TOOL_PLAN只返计划 | 通过。worker实际构造PostgresAdmissionLedger（映射DSN）与ControlledModelGateway（默认HttpxModelTransport），gate.call包含admit→mark→send→record；每one_call每进程恰好一次（SUP每窗恰好spawn一个worker，无重生）；TOOL_PLAN仅构造计划（gateway无自动执行路径，测试中execute被禁仍通过证明不执行） | worker_main.py:53-62、gateway.py:96-162 |
| C2 | PG兼容循环；超时/余量与W_eff及不可后移单调截止相容；短窗拒绝不扩窗；先预扣后启动 | 通过。worker/SUP/launcher均psycopg_compatible_loop_factory；t0在claim前固定；stop_ns=min(deadline−grace, manager−cleanup)claim后固定不可后移；配置交叉校验W>startup+timeout+grace；worker实际运行预算=min(request_timeout, 距stop_ns−0.25)；短窗partial_window_too_small全额预扣不退款不扩窗 | session.py:233-262、worker_main.py:57-60 |
| C3 | admit→mark→网络→record保持；UNKNOWN不降格不换operation重发；取消/失效不转授权成功 | 通过。gateway（冻结未变）语义完整复用；record_outcome对失效操作仅收UNKNOWN诊断；unknown_repeat场景实证：同operation二次admit被拒（REJECTED），操作行保持unknown态、requests_reserved不增、零重发 | repository.py:995-1019、真实批unknown/unknown_repeat行 |
| C4 | 门关闭阻止新调用，树零/句柄关闭先于begin_window_close/settle；worker不代SUP结算 | 通过。新回执读取/IPC关闭插入在树零+退出码+elapsed校验之后、job.close()之前，begin_window_close→settle顺序原样保持（session.py:305-339）；结算重试同G/W/C一次；worker_main无任何结算调用 | session.py、worker_main.py |
| C5 | 杀进程/缺回执/解析失败不误退款不伪成功 | 通过。worker非零退出→worker_failed_full_reservation全额预扣；回执缺失（one_call+settled无receipt）在launcher层抛错；解析失败→failed_closed且R=W、S=0、无回执、DB窗口留待保守折叠 | session.py:343-352、launcher.py:297-298 |
| D1 | 结果与监督状态分开；回执绑定全部身份；缺失/畸形/超限/旧回执失败关闭 | 通过。receipt绑定protocol/context(含G/scope)/run_tag/business_commit=not_committed/result；SUP用lease重建context并要求逐字段相等；launcher再对outcome.generation+provider/model复核；离线篡改矩阵（错G/错scope/错executor/布尔G/多余字段/缺字段/超限文本/超限载荷）全部失败关闭 | one_call.py:116-165、launcher.py:286-296 |
| D2 | SUCCEEDED仅为模型返回；not_committed非业务写入授权；G3未实现为批准边界 | 通过。docstring与回执字段显式声明；SUCCEEDED语义=模型返回且账本record(RECEIVED)已提交；未新增结果表、未声称重启可取正文；晚到结果按原账本纪律（record_outcome失效仅UNKNOWN）不发布为有效成果 | one_call.py:170-174、repository.py:1000-1008 |
| E1 | 兼容：协议2明确收发，idle与原导出保留，调用位置不遗漏 | 通过。协议2在四处decode显式校验（protocol=1被拒）；__init__原导出全保留（run_controlled_worker惰性代理防循环导入）；run_supervised_window全部既有调用位置（task083夹具idle路径）签名向后兼容；无产品模块（main/HTTP）接入worker——one_call未接HTTP/用户库/真实provider/工具循环 | 各文件、调用点全量grep |
| V1-V6 | 六组验证要求映射到实际test ID/场景 | 通过（映射见§4）；测试辨别力合格：成功链替身=合同允许条件且披露替换边；固定生产入口场景证明真实argv链数据传递+失败关闭 | §4映射表 |

## 3. 三个切片结论（按卡面要求分别签发）

- **当前切片代码结论：通过。** 逐行审查one_call.py全文、worker 7文件pre→当前完整差异及全部当前源码、只读直接依赖（gate/windows_job/repository关键方法/capabilities六文件/runtime）；未发现任何确定性高危缺陷；发现1个非阻断低危配置死区缺陷（N1）与若干观察项（§5）。静态正确性针对纯函数路径由动态证据与源码逻辑双重支撑；两处仅静态核验点已在证据分级中如实标注（N2）。
- **动态证据适用结论：通过。** 真实批运行源码=最终产品源码（hash链逐字节证实，仅3个测试/夹具文件批后有变且不进产品链）；12场景start/result/complete、批exit=0、外层Job树零、容器停止保留均由原始日志/manifest独立复核；离线03失败已定位为纯测试缺陷（tuple/list序列化语义），04修复不弱化实质内容/身份断言。证据分级细节见evidence-grading.json。
- **资源控制结论：通过。** 单批35.5s（≤600s/批、≤1800s累计、留足收尾）；离线累计5.47s（≤900s，单命令≤60s）；专用容器1个：固定镜像sha256:cf134a…、loopback 55440、1CPU/512MiB/pids128/no-new-privileges/restart=no、专用卷，inspect七字段+端口+卷逐项验证（投影用顶层{{json .Mounts}}，正确吸收D3-repair-11经验）；精确PID 27412+创建时间；外层Job（test-only ControlledChild，KILL_ON_JOB_CLOSE）树零ActiveProcesses=0、句柄关闭；容器stop后Running=false核验、卷保留不删；合成DSN/口令不进env/argv/日志。控制代码对硬超时/异常退出的收尾能力存在且有界；未触发分支（外层兜底kill）未虚称动态覆盖。

**是否可由编排验收关闭085：可以。** 本审计不签编排最终验收。

## 4. 六组验证要求→实际test/场景映射（原始日志逐行核对）

| 组 | 原合同要求 | 实际绑定 | 原始证据要点 |
|---|---|---|---|
| 1 正常one_call | 真实gateway逻辑，恰好一次发送/返回，G/scope来自claim | 真实批success/json/tool场景 + 离线test_real_gateway_single_send | events=[admit,mark,send,received]、transport.calls=1、ops=1且G=1=claim代次、scope一致、requests_reserved=1、dispatch_closed、R=0/S=1 |
| 2 拒绝无发送 | 无余额/取消/来源失效/身份错配无发送；UNKNOWN不重发 | 真实批no_balance/cancelled/source_invalid/unknown_repeat + 离线unknown/timeout/denied | 五场景零spawn零操作行；unknown_repeat同operation重试被admit拒绝、操作行保持unknown零重发 |
| 3 失败/超时/关门 | UNKNOWN/TOOL_PLAN不执行/关门拒绝/窗口不足不扩时 | 真实批unknown/tool/hard/short + 离线tool_plan_never_executes | unknown记录disposition=unknown；tool为TOOL_PLAN计划态且execute被禁仍通过；hard在硬截止杀树、R=10/S=0、op停dispatched；short全额预扣1秒不扩窗 |
| 4 载荷边界/秘密 | 载荷/畸形/身份/旧G回执拒绝；秘密不泄漏；idle回归 | 离线receipt_wrong_identity/frame_limits/mapping_owned/input_bounds + 真实批12场景全链decode + idle断言 | 篡改矩阵全拒；重复键/NaN/未知字段/超限全拒；argv/日志/repr无秘密；idle入口返回0且SUP侧idle拒绝携带业务数据 |
| 5 PG+Windows完整链 | 固定入口→SUP认领→worker→账本→结果→树零/句柄→关门结算 | 真实批production_rejected（全真argv链）+ success等11场景（bootstrap SUP） | 12组manager_pid/worker PID+创建时间；success场景结算后业务Job名open返回FILE_NOT_FOUND证明SUP先释放全部句柄；R/S/G/操作状态与模型结果分列断言 |
| 6 在途失败收尾 | 合成延迟至硬截止，局部树停止/保守R/无伪成功 | 真实批hard场景 | transport阻塞30秒→SUP于stop_ns杀树确认ActiveProcesses=0→stopped_at_deadline、无回执、R=10保守、op保持dispatched无终态 |

**生产固定入口与测试成功链的区分（卡面要求单列）**：production_rejected场景在未打任何patch的真实链（launcher真实spawn `-m app.worker.supervisor_main`→SUP→真实spawn `-m app.worker.worker_main`）上完成，证明固定生产入口的数据传递（双层映射/协议2/argv/回执）与失败关闭（未授权模型在admit被拒、零操作行、零发送），**不证明生产入口的成功发送**；11个成功/失败组合场景经bootstrap自举（替换两处argv模块路径与进程内transport.send），SUP子进程仍运行真实supervisor_main/session/claim/Job/IPC全部产品逻辑，worker子进程仍运行真实worker_main/decode/gateway/ledger，唯一行为替换边=transport.send替身（合同允许且逐项披露），产品无任何对应选择器。真实供应商0费用/0连通验证保持为已知边界。

## 5. 问题清单（无阻断；确定缺陷与观察分列）

### 确定缺陷

**N1（非阻断，低危，确定）**：`SessionConfig.request_timeout_seconds`无上界，与worker解码上限构成配置死区。
- 定位：backend/app/worker/session.py:44（SessionConfig字段）、one_call.py:109（decode_worker_request要求0<call_seconds≤120）、session.py:275（SUP把config.request_timeout_seconds原样作为call_seconds下发）。
- 触发：构造SessionConfig(request_timeout_seconds=121)（__post_init__仅要求有限正数，与window_seconds≤3600交叉下可构造）+ one_call调用。
- 影响：worker解码必然ValueError→exit 1→worker_failed_full_reservation，全额预扣不退款——失败关闭、不 unsafe，但功能上该配置区间one_call恒不可用，且launcher/SUP各层无早期拦截（各层只查service.timeout≤request_timeout）。
- 确定性：确定（代码路径静态必然）。
- 最小修正：SessionConfig.__post_init__给request_timeout_seconds加上界≤120（一行校验），或one_call三处入口统一加`config.request_timeout_seconds<=120`预检。
- 必需验证：一条离线断言（request_timeout=121构造被拒/或one_call在launcher前拒绝），约1秒。

### 非阻断观察（有现实触发/影响才列，无理论无限防护项）

**N2（证据分级，非阻断）**：最终版test_worker_one_call.py从未整体执行；10用例中6个（unknown_timeout/tool_plan/missing_data/frame_limits/input_bounds/sup_protocol）最后执行于offline-01、针对精化前源码，4+1个分别在02/04/05版本执行。逐行为分级（见evidence-grading.json）：这些用例的目标行为均另有12真实场景在最终产品源码上的动态覆盖，gateway/transport/tools/worker_main自offline-01起未变（hash链证实），唯两点仅静态审查支撑——(a) to_wire对配置>64KiB的显式拒绝（one_call.py:57-58）、(b) pack_frame槽边界在最终常量上的边界断言。可选最小补验：**一次离线完整跑最终tests.test_worker_one_call全套（约3秒）**；不构成阻断，不要求重跑12场景或D3。

**N3（观察，无需动作）**：idle worker从"跑一次gate空调用"改为立即exit 0（worker_main.py:68-69）；SUP计时/observed语义不受影响（ceil≥1s），offline-05已断言；083以来的SUP idle合同未变。

**N4（观察，同进程受信边界内）**：decode_receipt对回执tool_plans仅做finite_calculate结构校验，allowed_tools与request的匹配只由gateway在发送侧强制；被审进程为自有代码，无现实越权触发，不设为本切片门槛。

**N5（观察，标准共享内存卫生）**：exchange映射仅SUP（创建者）在close时memset清零；worker端unmap不清零自身视图（OS在对象销毁后回收页面）。秘密生命周期受限于同用户受信边界内，代码注释如实声明，符合合同"短生命周期通道"要求。

**阻断项：无。**

## 6. 边界保持（未验证不冒充通过）

- 真实供应商连通/费用：0调用0验证；成功链为transport替身，属085合同允许条件，未称真实连通。
- G3业务结果原子持久提交/重启幂等读取：未实现，未新增表，未用临时回执替代。
- M-1/STEP008整体、UI/HTTP接入、生产调用：未完成，本卡不宣告。
- 单机/单交互会话部署前提（D3批准范围）不变：映射随机名/DACL/校验和不作跨用户或同用户恶意进程防护声明；本次session/IPC新增不继承D3跨用户结论，仅复用未受影响的windows_job/claim-close-settle骨架（hash证实未变）。
- 外层控制未触发分支（子进程挂死时的外层Job兜底kill）仅有控制能力、无动态覆盖，如实记录不虚称。
- 085返回后的余量（批12/12 Windows会话、容器已停保留）不因本审计产生任何续跑授权；本卡零额度消耗、零容器接触、零源码写入。

## 7. 补验（如需，仅此一项，逐项精确）

| 项 | 精确缺口 | 补验动作 | 成本 | 必要性 |
|---|---|---|---|---|
| P1 | 最终测试文件整体执行证据；to_wire>64KiB拒绝与pack_frame边界两点在最终源码上无动态记录 | 单次离线：`cd backend && python -B -m unittest -v tests.test_worker_one_call`，留存exit/耗时/前后hash | ~3秒，离线预算内 | 可选（N2分级已证其余行为有动态替代证据）；若跑则一次通过即可，不重跑12场景/D3 |

除P1外无其他补验项。不默认重跑12场景、不重开D3、不做全仓审计。

## 8. 证据导航

- 本卡证据：`Ndocu/evidence/task-086/freeze-verification.json`（冻结核验+接触范围+意外接触披露）、`evidence-grading.json`（时间线/hash链/测试执行分级/账目分层事实）、`independent-diff-pre-vs-current.txt`（worker 7文件pre→当前独立diff）。
- 085原始证据引用（只读）：`Ndocu/evidence/task-085/`（pre/、pre-hashes.json、task085.diff、post-hashes.json、offline-01..05、20260928T001119Z-77ba1b/）。

**建议状态：有条件通过（条件仅为可选P1补验与N1最小修正建议，均不阻断编排验收）。**
