# TASK-058 持久准入账本独立只读审计接续 — 结果

任务：TASK-058 / R-052；类型：独立审计（STEP-006/008 局部）；接续 TASK-056，关联 TASK-046/051/055。
日期：2026-09-20（Asia/Shanghai）。项目根：D:/shspic/project_NO3_RetroLume-agent。
需求基线 LATER_REQUIREMENTS.MD v1.1（目标 v1.0）；架构 PROJECT_ARCHITECTURE.MD v0.16。
状态：本卡审计工作完成（覆盖充分即停）；不填写 Astra 最终验收结论。

## 1. 结论摘要

在**有限范围**（capabilities 受控模型入口 + activities/002 持久准入账本 + 正式 Windows 启动循环接线）内，代码与契约、原始证据三者一致；未发现导致越权、二次发送、半次预留、把取消/失联/旧代次误记为业务成功、或把未知结果当成功的缺陷。审计标准 1～4 成立，标准 5 为部分成立（应用组合未接入账本）。

发现 1 项中等问题（时钟来源）、3 项低severity问题、3 项观察；1 项恢复能力缺口列后续门槛。无阻塞项。建议：**有限范围通过**，附加条件——真实应用组合接线、002 落到用户库、worker/业务提交接入之前，先处理 M-1 与 G-1，L-1～L-3 可同批处理。

TASK-056 截至本卡检查仍无结果文件（Ndocu/results/ 仅到 TASK-057），本卡不继承其结论、不补记其通过；056 的覆盖对象由本卡重新独立判断。

## 2. 独立性声明

- 本卡在未参与本实现的新会话中执行；未读取任何实现 Agent 的自评报告/结果文件/执行聊天，判断仅基于标准（LATER_REQUIREMENTS、架构 FLOW-005 及数据/安全边界）、被审源码、合同卡原文和 051/055/046 原始证据（stdout、退出码、环境、命令、hash、停止记录）。
- 全程只读：未运行测试、Docker、应用、模型、安装；未读真实配置；未改实现/测试/锁/正式 docu/既有证据；未提交 Git。
- 与 TASK-057 无写冲突：未读取其正在变动的 tests/task054_pdf_materials_integration.mjs、task057_watchdog.mjs 及 Ndocu/evidence/task-057/。
- 读取范围明细见 Ndocu/evidence/task-058/read-scope.md。

## 3. 被审快照（自行只读复算，非引用他人结论）

复算文件与证据记录一致，说明"证据所测对象 == 当前实现快照"：

| 文件 | 本卡复算 SHA-256 | 与既有证据比对 |
| --- | --- | --- |
| backend/app/activities/repository.py | 6228b35b…4a763 | 与 051、055 source-hashes 完全一致 |
| backend/migrations/002_activities.sql | 3a9c5855…2dda6 | 与 051、055 完全一致 |
| backend/app/runtime.py | 067021e1…80f6b | 与 055 完全一致 |
| deploy/start_local.py | 60c73569…509e7 | 与 055 完全一致 |
| deploy/start-backend.ps1 | e577096e…247fc | 与 055 完全一致 |
| backend/tests/test_activity_ledger.py | 0eb878cb…30c9e | 与 055 一致（051 为 4186ddb1，即 055 的夹具清理修正） |
| tests/run_ledger_check.py | 63a05016…92b7 | 与 055 完全一致 |
| backend/app/capabilities/contracts.py | 43b6bd2b…06c84 | 与 046 证据一致 |
| backend/app/capabilities/gateway.py | c7778589…31a | 与 046 一致 |
| backend/app/capabilities/tools.py | bb94408f…a5838 | 与 046 一致 |
| backend/app/capabilities/transport.py | 1d80347e…5b656 | 与 046 一致 |
| backend/app/capabilities/__init__.py | 9e38cf88…857ee | 与 046 一致 |
| backend/migrations/001_materials.sql | 767f47c3…07a8d | 本卡记录（无对照证据，只读确认内容） |
| backend/tests/test_capabilities.py | 4b2df693…6717 | 与 046 一致 |

时间线一致性（本卡记录见 audited-mtimes.txt）：capabilities 最后写入 2026-09-14 04:34–04:38，046 取证 04:39；activities/002 最后写入 04:47–04:48；runtime/deploy/run_ledger_check/test_activity_ledger 最后写入 2026-09-14 18:40:21，055 主运行 18:41:26–18:41:32。无证据之后的新改动。

覆盖链说明（精确边界）：051 的 test_01 通过时使用旧测试文件（4186ddb1），当前为 0eb878cb；两者之间的差异按 055 记录仅为 asyncSetUp 清理顺序（当前文件 L51 已有 `current_version = NULL`）。**被审账本与迁移 hash 在两次之间未变**，test_01 的断言意图（received 状态、prompt_tokens=10、requests_reserved=1、cost=100）与当前文件 L119-138 一致，故 test_01 结论对当前快照仍成立；但 4186ddb1 原件未归档，无法逐字节 diff，此项按"间接一致"记录。

## 4. 覆盖矩阵（审计标准 → 代码位置 → 证据 → 状态）

标准1 锁序与边界核对：repository.py L199-217（_lock_sources，按 source_id 排序逐个 FOR UPDATE 并核对 current_version/revision）、L219-259（create_activity 先来源后活动）、L388-405（_activity_allows 核对 running/executor/代次/scope_revision/租约/期限/字节/输出/tools/次数/费用）、L407-464（admit 同事务唯一占用）、L466-497（_locked_operation 复核凭证、来源、活动、操作绑定）、L499-511（_operation_is_current）、L513-525（mark_dispatch_started 一次性 CAS）。证据：051 test_01（真实 PG）、055 test_04/05（来源替换撤销、取消递增代次）；materials/repository.py L54-68/L183-237 只用 material_sources FOR UPDATE，与账本不构成反向锁序。状态：成立（限定范围）。

标准2 限额、唯一 operation、短事务、回滚：repository.py L156-171（正数限额、reserve ≤ max_cost）、L172-175 校验、L94-123（每阶段独立短事务、statement/lock/idle 超时）、L426-431（operation 键占用即拒）、L433-461（同事务预留+写操作）、gateway.py L117-142（网络调用在准入事务之外）。证据：055 test_02/03/06/07/08 全部 ok、exit-code 0。状态：成立（费用为本地保守预留机制，见 O-1）。

标准3 取消/失联/超时/旧代次不得记成功、unknown 不退款不重发、幂等且不覆盖：repository.py L578-602（终态幂等比较 L562-576；不同终态拒绝覆盖 L583-586；失效/过期只能登记 unknown L587-589；尚未越过边界不得登记非 unknown L590-591）、L317-354（recover_unknown 只在活动非当前时收敛，未知保留预留）、L292-315（cancel 递增代次并清空执行者/租约）；gateway.py L126-140（RequestNotSent→NOT_SENT；Timeout/DeliveryUnknown/其他→UNKNOWN；CancelledError 先记 unknown 再上抛 L129-131）。证据：051 test_01（received 保留预留）、055 test_05/06/07。全库无任何减少 cost_reserved_microunits 的语句（只读确认）。状态：成立（限定范围）。

标准4 契约吻合、默认拒绝、固定 URL、工具白名单、总期限、无隐藏重试、日志脱敏：contracts.py L21-23（固定允许 URL）、L26-55（SecretStr + repr=False，校验失败不泄密）、L119-128（CallContext 自述"不是授权"）、L168-179（Ledger 协议语义）、L190-203（RejectingAdmissionLedger 默认拒绝，gateway.py L85 作为默认注入）；tools.py L77-98（闭集工具目录 + 精确 schema，execute 不由模型入口自动调用）；transport.py L40-92（单次 POST、follow_redirects=False、trust_env=False、无 SDK 重试）；gateway.py L118（asyncio.timeout 覆盖整段发送+读取，L98/L97 请求体上限）。证据：046 verification.md（12 项 + 定向 2/4 项，均 OK，对应当前 capabilities hash）；055 static-check.txt（无全局 event loop 策略改动）。状态：成立（真实供应商返回结构未验证，见 §6）。

标准5 Windows 启动 loop 与异步 psycopg：runtime.py L9-14（win32→SelectorEventLoop）；start_local.py L44-60 与 start-backend.ps1 L14 均以 `--loop app.runtime:psycopg_compatible_loop_factory` 启动 uvicorn。证据：055 ledger-check.stdout.log 第13行 `uvicorn_loop_factory=app.runtime:psycopg_compatible_loop_factory loop=asyncio.windows_events._WindowsSelectorEventLoop`，且 7 类真实异步 psycopg 测试在该 factory 生成的循环内跑通；哈希一致。缺口：应用组合未接入账本（全库仅测试引用 PostgresAdmissionLedger，main.py L52 只注入同步 PostgresMaterials），故"以正式启动器真正跑起应用并让账本异步连接运行"尚无证据。状态：部分成立。

标准6 缺陷/证据/缺口/后续责任区分：见 §5、§6。

## 5. 发现（文件·位置·触发·影响·证据·最小修正）

### M-1（中，条件触发）：期限与租约判定使用应用进程时钟，违反 FLOW-005 "时钟回拨不得增加剩余时间"

- 位置：backend/app/activities/repository.py L499-511（_operation_is_current）、L388-405（_activity_allows，经 L416 传入）、L272-280（claim_lease 用 now 计算并在 L277 比较）、L328-334（recover_unknown 的 recoverable 判定）；now 全部取自 L272/L328/L416/L501 的 `datetime.now(timezone.utc)`。
- 触发：主机时钟回拨或 NTP 大幅跳变，幅度大于租约剩余时间（或 deadline 与当前时间之差）。租约到期时间本身也由同一应用时钟计算并写入（L280）。
- 影响：过期租约/已过期的活动截止可能被判为"仍有效"，陈旧执行者获得额外准入与发送窗口。不会造成二次发送（operation 键唯一，L426-431）、不会突破次数/费用上限（计数在 DB 内累加，与时钟无关），因此影响限于"陈旧代次的准入门槛被时钟异常放宽"。
- 证据：代码只读确认（5 处 datetime.now 全部为进程时钟）；同一文件的其他时间字段（updated_at/cancelled_at/recorded_at/dispatch_started_at）用 CURRENT_TIMESTAMP，说明 DB 时钟可用但未用于判定。055 test_04/05/07 与 051 test_01 均未覆盖时钟异常，属未测分支。
- 最小修正：把期限/租约比较改为数据库时间（例如在 _lock_sources/活动查询中带上 `AND lease_expires_at > CURRENT_TIMESTAMP AND deadline_at > CURRENT_TIMESTAMP`，或在同事务内 `SELECT now()` 后统一使用该值计算与比较）。不影响现有接口。
- 本卡未动态验证（只读卡禁止运行），建议并入下一次真实组合运行卡顺手覆盖（时钟回拨可用事务内伪造 now 或直接 SQL 断言验证）。

### L-1（低）：CallContext 与账本实现存在未文档化的字段格式约束

- 位置：backend/app/capabilities/contracts.py L124-128（activity_id/operation_id/executor_id 仅限长度 1～128，无字符集约束）对 backend/app/activities/repository.py L356-386（activity_id 必须是 UUID；operation_id/executor_id 必须匹配 `^[A-Za-z0-9._:/-]+$`）。
- 触发：调用方使用含空格、中文或超范围字符的 operation_id/executor_id，或非 UUID 的 activity_id。
- 影响：fail-closed（只可能被拒，不会越权），但合法外观的 id 会被静默归入 `admission_denied`，集成时难以定位；文档未写明该字符集要求。
- 证据：代码只读比对；test_capabilities.py 使用 "activity-1"/"operation-1"/"worker-1"，恰好落在允许字符集内，故 046 离线证据不会暴露该差异。
- 最小修正：在 CallContext 上加同构 pattern（或在校验失败时返回可辨原因），使契约与实现一致。

### L-2（低）：请求体大小判定用紧凑序列化，与线上实际体积有系统性小偏差

- 位置：backend/app/capabilities/gateway.py L94（`json.dumps(..., separators=(",", ":"))` 后取 len）与 L97 判定，实际发送由 transport.py L59-67 `json=payload` 完成（httpx 用默认 `", "`/`": "` 分隔）。
- 触发：任何请求；差异约等于键值对数 × 2 字节。
- 影响：受检的 request_bytes 略小于线上真实体积，"请求上限"判定不严格对应实际发送体。默认 256 KiB 上限下可忽略，不构成资源风险。
- 证据：代码只读；046 test 只断言上限拒绝路径，不校验线上体积。
- 最小修正：以同一序列化结果作为发送体（transport 接收 bytes），或按分隔符作保守放大估算。

### L-3（低）：准入阶段的意外异常被统一折叠为不可区分的拒绝，且无任何日志

- 位置：backend/app/capabilities/gateway.py L114（`except (AdmissionUnavailable, Exception)` → REJECTED/"admission_unavailable"）、L384-398（_result）。
- 触发：账本实现与协议不匹配、编程错误等非预期异常（此时 permit 可能已占用）。
- 影响：不发送、fail-closed 正确；但"未准入"与"内部错误"在返回码上不可区分，且 backend/app 全目录无 logging（只读 grep 确认），集成期缺陷会表现为统一拒绝而无诊断线索。
- 证据：只读代码 + 全目录 grep（logging/logger/print/traceback 均无命中）。
- 最小修正：保持不发送，但为意外异常使用独立稳定 error_code（如 internal_error）并留下脱敏诊断标识；不改变安全语义。

### O-1（观察，不需要修正）：预留不退还政策与"本地保守额度"定位

NOT_SENT/UNKNOWN/RECEIVED 三种终态都不减少 cost_reserved_microunits（只读确认全库无递减语句），符合"未知/已发送保守保留预留"，属预期行为。副作用是：即使连接建立前即失败（RequestNotSent），也占用一次请求额度与全额预留，可用调用次数少于 max_requests 名义值；且 reserve 是按活动配置的固定值（L459），不随请求的输出/上下文规模变化。这不是供应商账单硬上限，任何文档/界面表述都不得写成"费用已被硬性封顶"。

### O-2（观察）：准入后未能越过发送边界的操作会停留在 reserved

gateway.py L109-115：admit 成功（已预留、已写入 reserved 操作行）后，若 mark_dispatch_started 抛错、或 L110 `_validate_permit` 失败，网关返回 REJECTED 且不再写任何结果（只读确认无其他补偿调用）。该操作会保持 `state='reserved'`、`dispatch_started_at IS NULL`——语义上是"确定未发出"，比写 unknown 更如实，但会长期占用一次额度与预留，需要监督侧收敛（见 G-1）。不建议改成自动退款或自动改记 unknown。

### O-3（观察）：每次准入阶段各建一条新 PG 连接

repository.py L94-123 每个方法各自 `AsyncConnection.connect`，一次模型调用的准入链（admit/mark/record）需要 3 次连接。与"短事务、网络调用不持事务"一致，本地单用户可接受；接入真实 worker 时需评估连接开销与池化，不属当前缺陷。

## 6. 缺失证据、未验证与后续门槛

未验证（本卡只读，不能声称通过）：

1. 崩溃/进程被杀/监督器失联：账本侧无 crash 测试。051/055 原始记录已明确未覆盖"进程崩溃、监督器失联、worker 终止"，与本卡判断一致。
2. 真实应用组合：账本未接入应用（仅测试引用）；002 迁移未对任何用户库执行（"候选迁移，不由启动器自动执行"）。因此"正式启动器跑起应用 + 账本异步连接 + 真实资料库"无证据。
3. 真实供应商调用与返回结构兼容：无真实模型请求（046 明确不写"模型兼容已验证"）。gateway.py L261-292 对返回 model/choices/usage/finish_reason 的校验较严（model 需匹配 `[A-Za-z0-9._:/-]{1,128}`，usage 三字段必须齐全），且请求带 `thinking`（L151）与 `response_format`（L153-154）；对真实服务是否全部接受、是否有字段形态差异，需在获授权的真实调用卡验证（本卡不授权、不执行）。
4. 时钟异常（M-1）未测。
5. 真实并发压力：test_02 只有两路并发；更高并发下 lock_timeout（2s，L87-92）导致的 AdmissionUnavailable 概率未测。
6. 晚到结果对账：未知为终态且不可覆盖（L583-586），不存在"远端稍后成功再修正"的路径；NFR-002 "晚到输出不污染当前状态"满足，但"恢复后先对账"（FLOW-005）尚未实现。

后续门槛（未实现，不构成本卡通过或失败；接入前必须满足）：

- G-1 未决操作发现接口缺失：recover_unknown（L317-354）只在活动已取消/过期/无租约/租约过期时收敛；一旦新执行者已领取租约（claim_lease 递增代次，L279-288），旧代次的 reserved/dispatched 操作既不能被 recover_unknown 收敛，也没有列出未决操作的领域方法（002 的 `activity_operations_recovery` 索引 L84-86 已建但当前无读取方）。可终结它们的路径只有"持有原 permit 并调用 record_outcome 记 unknown"（L587-589 允许），但缺少发现途径。建议最小补充：新增只读方法 list_unresolved_operations(activity_id)（复用现有索引），并明确其契约；该项属 worker 监督范畴，可在监督器实现卡内一并处理。
- G-2 worker 监督器：租约过期/取消/期限到达时实际终止自有执行单元、停止顺序（先拒新任务→停自有执行→标未知）全部未实现。
- G-3 业务提交：预留→已发送→收到结果→"提交成功"链中最后一环未实现（无业务提交状态与幂等写入），FR-010 复测/路径更新依赖它；"已完成操作可重放持久结果"也未实现（账本只存 token/模型/finish_reason 等有限事实，不存正文）。
- G-4 范围修订写入方：activities.scope_revision 目前无任何更新路径（全库只读确认），因此只能验证"不匹配即拒"，不能验证范围新增/移除后的撤销流程（FLOW-005 补充"并发源新增/移除改变范围修订号"）。
- G-5 工具调用/内部步骤独立计数：活动有 allowed_tools 白名单与请求次数上限，但没有独立的工具调用数/步骤数计数器；当前可接受的原因是网关不自动循环调用工具（每次续接都是新的 operation 并计入 max_requests），需在引入自动工具往返时重新评估。
- G-6 可观测性：架构第8节要求记录状态转换/预留/用量/追踪 ID，当前两个模块完全没有日志；接入真实 worker 时需补齐（同时保持不含正文/密钥）。
- G-7 剩余范围（本卡明确排除，不得据此判定本卡已覆盖）：完整学习链、真实模型效果、HTML/宿主、STEP-008 整体与项目整体完成。

## 7. 需求/架构偏差

1. FLOW-005"系统时钟回拨不得增加剩余时间"未在当前实现中落实（M-1）。属于实现与架构条文的实际偏差，需修正或由 Astra 明确降级并记录理由（本卡不建议降级）。
2. FLOW-005 补充"结果校验与成功写入在同一事务内完成，不能被撤销穿插"：账本自身的终态写入与其校验（来源/活动/代次/状态）确实在同一事务（L578-602）；但"成功写入"指业务结果，属 G-3，未实现，不算偏差。
3. FLOW-005"活动执行时间累计与每次绝对截止分别持久化"：截止（deadline_at）已持久化；执行时间累计未持久化，属未实现的后续项（当前由截止与租约覆盖）。
4. 未发现与 SEC-002/NFR-002/NFR-003/DR-003 相反的实现行为；DR-003"重复作答不重复计分"对应的业务计分尚不存在，非偏差。
5. 文档表述风险（非代码偏差）：现有材料若把本地预留描述为"费用上限已生效/供应商账单硬上限"，应改写为"本地保守预留"。本卡未发现该措辞出现在被审源码中，属提醒。

## 8. 文档建议（交 Astra 决定，本卡不改正式 docu）

1. MOD-003/MOD-008/DATA-004/DATA-007 的状态可从"计划中"细化为"部分实现（准入/发送/结果账本）"，并在条目内注明：应用未接入、002 未落库、无崩溃/时钟/真实供应商证据。
2. 建议在架构或执行状态中登记 G-1～G-6 门槛清单，作为 STEP-008 后续卡的检查项，避免"账本局部通过"被误读为 STEP-008 完成。
3. PROJECT_EXECUTE_STATE 的 TASK-056 行保留"验收留空 + 无结果文件"事实，并在 TASK-058 验收后注明其覆盖对象已由 058 独立复核（不含继承结论）。
4. 建议在 CALL 契约文档中补齐 CallContext 的字符集/UUID 约束（L-1），并明确 request_bytes 的口径（L-2）。

## 9. 下一步（建议，非授权）

1. Astra 按本卡发现裁定：M-1、G-1 是否必须在"真实应用组合接线卡"之前修正；L-1～L-3 是否并入同一批最小修正。
2. 下一次真实组合运行卡（055 记录的下一步）建议覆盖：正式启动器实际启动应用 + 账本接入后的异步 psycopg 真实连接、002 迁移在副本库执行、时钟异常与崩溃反例（可与 G-1 的未决操作发现一起验证）。这些均需新的运行授权与 Docker 恢复，本卡不执行。
3. 本卡不宣告 STEP-006/008 或项目完成；不填写 Astra 最终验收结论。

## 10. 证据清单（本卡新增，只读产物）

- Ndocu/results/TASK-058-result.md（本文件）
- Ndocu/evidence/task-058/audited-hashes.sha256（16 个被审文件复算 hash）
- Ndocu/evidence/task-058/audited-mtimes.txt（被审文件最后修改时间）
- Ndocu/evidence/task-058/read-scope.md（读取范围与独立性记录）
