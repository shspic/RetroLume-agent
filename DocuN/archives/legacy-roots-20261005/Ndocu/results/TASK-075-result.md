# TASK-075 M-1 时钟/持久预算与 worker 首段接线 — 最小实现方案（结果）

任务：TASK-075 / R-069；类型：定向诊断与接线方案；STEP-008；父 TASK-060；关联 058/068/071/072/074、NFR-002/003、SEC-002、FLOW-005、MOD-003/008、DATA-007。
日期：2026-09-21（Asia/Shanghai）。项目根：D:/shspic/project_NO3_RetroLume-agent。
基线：LATER_REQUIREMENTS.MD v1.1；PROJECT_ARCHITECTURE.MD v0.25；执行状态 v1.18（R-054/R-068 裁定）。
状态：方案收敛完成（一次只读核对，未运行任何测试/应用/容器）；Astra 验收留空。本卡不实施、不修改产品代码，不宣告 M-1/STEP-008 完成。

## 0. 结论摘要

1. M-1 拆为四个互不替代的缺口：墙钟判定、活跃进程单调监督、持久剩余时间额度、租约代次。前三个均未实现或未持久化；第四个（代次）已实现且判据不用墙钟，天然免疫回拨，可继续作为恢复骨架。
2. 唯一推荐方案：**时间额度持久计数器预扣制**——认领租约的同一短事务内预扣整个执行窗口的时间额度；窗口内由单调时钟（进程内看门 + 外层 Windows Job 监督）强制终止；未确认窗口保守不退（崩溃时折叠为已消耗）；结算仅由持有当前代次的 worker 以单调实测耗时写入。回拨不得增加剩余时间、重启不得重置额度，均由计数器（而非时间戳比较）保证。
3. 备选方案（有实质差异）：按操作预扣（每次准入预扣该次调用超时上限，永不结算退回）。更简单、崩溃损失上界更小，但只记上界不记实际执行时间，预算被保守超扣，与 FLOW-005"活动执行时间累计持久化"的字面要求契合度低。
4. 072/074 的仓储切片证据继续适用；本方案不触碰其实现。主要数据模型变更（activities 加 3 列 + CHECK）仅提案，待 Astra 及必要用户确认后由实现卡执行。

## 1. 缺口逐项对应实际代码（不混为一项修复）

| # | 缺口 | 实际位置/缺失 | 现状判定 |
| --- | --- | --- | --- |
| G-a 墙钟判定 | 租约/期限比较全部使用墙钟 | repository.py L285/L293（claim_lease 写读）、L341（recover_unknown）、L536→L509-525（admit 判定）、L621（_operation_is_current）；SQL 端 CURRENT_TIMESTAMP 均为事务开始墙钟 | 回拨可扩大单租约判定窗口；R-054 已裁定单换 now/clock_timestamp/monotonic 均不足 |
| G-b 活跃进程单调监督 | activities/worker 无任何单调计时 | 全库仅 pdf_import/_windows_job.py L113/L168 使用 time.monotonic()（限本子进程超时）。backend/app/worker/ 目录不存在（FILE-009 计划中）；rg 证实 claim_lease/admit 无产品调用方；main.py 不导入 activities/capabilities | 未实现 |
| G-c 持久剩余时间额度 | 无累计执行时间持久化 | 002_activities.sql L4-32：仅有 deadline_at（绝对期限）与 requests/cost 两类计数器；无时间额度字段。FLOW-005 要求"活动执行时间累计与单次截止分别持久化，重启不能重置剩余额度" | 未实现（DB 字段缺失） |
| G-d 租约代次 | execution_generation 递增 + 旧代次收敛 | 002 L8/L57；claim_lease L292、cancel L317；recover_obsolete_operations L415-474 判据仅用代次差、不用墙钟；074 六例真实 PG 已验证该切片 | 已实现并验证（072/074 证据继承），作为恢复骨架复用，不需修改 |

结论：G-a/G-b/G-c 三者必须组合实现（060 §4.1 四层区分成立），任一单改都不是 M-1 修复；G-d 无缺口。

## 2. 唯一推荐方案（A：窗口级预扣 + 单调监督 + 失败关闭）

### 2.1 机制

1. **持久预扣**：认领租约（claim_lease）的同一短事务内，把本执行窗口 W（= min(配置窗口, 剩余额度)，秒）预扣进持久计数器：`running_reserved_seconds += W`，受 CHECK `running_reserved_seconds + running_settled_seconds <= max_running_seconds` 约束。剩余时间额度从此是**计数器差值，不是时间戳比较**——DB 墙钟回拨/前跳不可能增加它，重启不可能重置它。
2. **单调监督活跃窗口**：worker 认领成功后记录 `time.monotonic()` 起点，窗口截止 = 起点 + W；三层强制：进程内看门线程（到期停止发起新动作并取消在途 asyncio 任务）、外层监督进程持有同一 W + 宽限、Windows Job Object（复用 _windows_job.py 模式：KILL_ON_JOB_CLOSE + TerminateJobObject）。墙钟不参与活跃窗口的强制终止。
3. **未确认窗口保守不退**：崩溃/监督强杀/结算写失败时，预扣的 W 不退回。下次认领或取消时把遗留预扣**折叠为已消耗**（`settled += reserved; reserved = 0`），保证 reserved 只反映当前存活窗口。崩溃损失上界 = 一个窗口 W（建议默认 ≤600s，配置项）。
4. **正常结算**：worker 在窗口结束前（W−ε）以单调实测耗时 E=min(实际, W) 写结算事务：校验活动 running + executor + 当前代次匹配后 `reserved -= W; settled += E`，释放 (W−E)。人工等待期间无租约、无预扣、无结算——天然不计运行。
5. **DB 墙钟仅作辅助判定**：claim/admit/recover 的租约与期限比较改为**取得行锁之后**读取 `clock_timestamp()` 作判定与写入依据（语句时点墙钟，锁等待计入判定）；这收紧 G-a 的锁等待缺口，但不宣称单换即修复。回拨残余：单租约判定窗口仍可能被拉长，上限 = 单租约 ≤3600s 与 deadline_at 已写入值封顶；**后果被预扣计数器封顶**——拉长的窗口内每次新认领仍须从固定计数器预扣，总执行时间不可能超预算。此残余明确保留，不引入新时间服务（沿 R-054 边界）。
6. **跨重启恢复（失败关闭）**：不承诺持久单调时钟（不存在）。重启后旧内存窗口作废；新认领须等旧租约按墙钟自然过期（首段不加抢占）；代次 +1 后先用已验证的 recover_obsolete_operations 分批收敛旧代次未决操作（072/074 切片），再开始新动作；旧代次的结算/结果写入一律被代次检查拒绝。

### 2.2 正常停止/人工等待/崩溃的结算与取舍

- 正常停止：窗口尾或任务完成 → 结算事务（§2.1-4）→ worker 退出或重新认领（剩余额度 > 0 才允许）。
- 人工等待：活动转入等待即释放租约（结算后无 running 状态/租约），等待期不消耗时间额度；deadline_at 绝对期限独立防挂起。
- 崩溃：W 保守损失，折叠机制保证不残留脏 reserved。用户视角：预算显示口径 = 已确认消耗 + 在途预扣。
- UX 取舍：窗口越小预算会计越准、崩溃损失越小，但认领/结算事务越频繁；推荐默认 300–600s，数值属第 13 节最迟确认门。

### 2.3 备选方案（B：按操作预扣，有实质差异）

每次 admit 的同一短事务预扣该次调用超时上限（gateway timeout_seconds ≤120s）进 `time_reserved_seconds`，永不结算退回。
- 优点：只加 1 列、无结算事务与晚到结算规则、崩溃损失上界 = 单次调用超时（≤120s）。
- 缺点：只持久化消耗上界而非实际执行时间，预算按保守超扣快速耗尽（如 30 次调用 ×120s 预扣 3600s 而实际用 90s）；与 FLOW-005"活动执行时间累计持久化"字面要求契合度低；预算可视口径失真。
- 判定：不推荐；仅当 Astra 否决窗口结算复杂度时作为退路。

## 3. 失败场景责任表（谁拒绝/谁停止/额度不增）

| 场景 | 谁拒绝新动作 | 谁停止自有执行 | 剩余时间额度 |
| --- | --- | --- | --- |
| DB 墙钟回拨 | 计数器 CHECK 拒绝超额预扣；deadline/lease 比较可能被拉长但只放宽"能否再认领"，不放宽预算 | 活跃窗口由单调时钟终止，不受回拨影响 | 计数器差值，回拨不可能增加（G-a 残余仅拉长单租约判定窗口，后果被预扣封顶） |
| DB 墙钟前跳 | lease/deadline 判定提前失效 → admit/claim 拒绝（保守方向） | worker 感知租约失效后停发新动作，窗口内自行收尾 | 不增加（前跳只会更早拒绝） |
| 等待行锁期间过期 | 判定改用取锁后 clock_timestamp()：锁等待计入判定，等待中到期即拒；lock_timeout 2s 限制等待漂移 | worker 发起准入前自查单调窗口，窗口不足不再 admit | 预扣在 claim 时点已定，与锁等待无关 |
| 监督丢失（监督进程死） | 无监督即无新认领：worker 只由启动器在 Job 内启动；Job 句柄随监督者关闭 → KILL_ON_JOB_CLOSE 连带终止 worker | Job 机制强制 | 该窗口预扣不退，下次认领折叠 |
| 子进程/worker 挂死 | — | 外层监督 monotonic 到 W+宽限 → TerminateJobObject | 预扣不退，折叠 |
| 进程/机器重启 | 旧租约按墙钟到期前拒绝新认领（不加抢占，最长等 W）；新认领预扣自持久计数器 | 旧内存窗口作废；明确声明：跨重启持久单调计时不存在，靠预扣+失败关闭保守恢复 | 计数器持久，重启不重置；旧代次晚到 settle/record 被代次检查拒绝 |
| DB 不可用 | admit → AdmissionUnavailable 不发送（现状保持）；claim/结算失败即无下一窗口 | worker 单调窗口照常到点终止自有执行 | 不增加（无新预扣；未结算窗口保守消耗） |

绕过监督的原入口：当前 gateway/ledger 均无产品调用方（main.py 未接线）。首段接线把 claim/admit/settle 的组合根**唯一**放在 worker 启动路径；应用 HTTP 层不暴露（API-006 内部语义保持）；启动器只以 Job 方式启动 worker，worker 启动时以 IsProcessInJob 自检，不在 Job 内则拒绝认领（候选细节）。同进程内代码属既有信任边界（架构 §8：不承诺抵御同账户恶意程序），不新增安全标准。

## 4. 最小事件顺序（含事务边界/可信调用方/代次与晚到检查）

1. **启动**（无 DB 事务；可信调用方=受信启动器）：启动器创建 Job（KILL_ON_JOB_CLOSE、内存/进程上限，复用 _windows_job 模式）→ Job 内启动 worker → worker 自检在 Job 内 + DB 健康检查，不可用即退出，不认领。
2. **认领**（短事务[来源→活动锁序]；调用方=worker）：校验来源快照/状态/期限 → 折叠旧代次遗留预扣 → 预扣 W → 代次 G=旧+1、租约写入（clock_timestamp 取锁后值）→ 提交。
3. **建立受监督窗口**（无事务）：worker 记 monotonic 起点，臂上三层监督（§2.1-2）；配置约束：gateway 单次超时 ≤ W。
4. **旧项分批收敛/复查**（每批一短事务；072/074 已验证方法）：循环 recover_obsolete_operations（limit≤200、有界次数/总期限）至返回 0 → list_unresolved_operations 复查；当前代次项不动；窗口耗尽即停止、不 admit。
5. **准入/发送**（每操作三个短事务+事务外网络）：admit[来源→活动→操作锁：代次/租约/范围/计数全检] → mark_dispatch_started（不可逆出站边界）→ 事务外网络调用（asyncio.timeout）→ record_outcome。
6. **结果或 unknown**：record_outcome 幂等；失效/过期执行仅可登记 unknown；预留不退不重发（gateway 既有语义不变，本卡不改）。
7. **正常停止**（一短事务）：单调实测 E → settle（校验 running+executor+当前代次，无时钟比较：释放性写入只会减少消耗，上界 W）→ 退出或回到 2（剩余额度不足则不再认领）。
8. **崩溃/恢复**：Job 连带终止 → 预扣残留 → 重启后重复 1-2（旧租约墙钟到期后），新代次触发 4 收敛旧代次；旧代次一切晚到写入（record_outcome/settle）被 L610-631 同构的代次检查拒绝。

## 5. 持久字段/约束/接口候选变更（仅提案，不实施）

- **activities 表 +3 列 + 1 约束**（建议新迁移 004，不动已冻结 hash 的 002）：`max_running_seconds INT NOT NULL CHECK(>0)`、`running_reserved_seconds INT NOT NULL DEFAULT 0 CHECK(>=0)`、`running_settled_seconds INT NOT NULL DEFAULT 0 CHECK(>=0)`，CHECK `running_reserved_seconds + running_settled_seconds <= max_running_seconds`。002 仅在合成库执行过且 074 后六表清零、用户库未迁移，空表加列可行；若有历史行需回填策略，属实现卡细节。
- **接口候选**：ActivitySpec 增加 max_running_seconds（必填正整数）；claim_lease 签名不变（lease_seconds 语义扩为窗口预扣，内部先折叠再预扣）；新增内部方法 `settle_execution_window(activity_id, executor_id, execution_generation, elapsed_seconds)`（短事务、同锁序、只做代次/executor 校验的释放性写入，E 夹紧 ≤ 当前 reserved）；cancel_activity 折叠在途预扣。activity_operations/HTTP/CallContext/公开契约零变化。
- **已有字段足够部分的依据**：deadline_at 保留为独立"活动绝对期限"轴（防挂起，与时间预算并存不混用）；requests/cost 计数器、execution_generation、lease 语义全部不变；recover_obsolete_operations/recover_unknown/list_unresolved_operations 不改。
- 兼容影响：create_activity 调用方（现有测试夹具）需补新必填字段；合成库需重迁移；属实现卡范围。新增执行时间持久化是 NFR-003/FLOW-005 既有要求的实现，不作为新产品需求；但主要数据模型变更仍待 Astra 及必要用户确认后才实施。

## 6. 下一张最小实现卡边界（建议）

- **允许文件**：backend/app/activities/repository.py（+__init__.py 导出）、backend/migrations/004_activities_time_budget.sql（候选 DDL，合成库专用）、backend/app/worker/（新：runner、监督、IsProcessInJob 自检，复用 _windows_job 模式）、backend/tests/ 定向补充；不改 main.py/HTTP/网关语义/锁序。
- **前置契约**：§2 机制全部条目（折叠、预扣、结算夹紧、clock_timestamp 取锁后判定、gateway 超时 ≤ W 配置校验、Job 自检拒认领）。
- **行为验收（本卡静态/离线部分）**：预扣与 CHECK 拒绝、折叠不退、结算释放、代次晚到 settle/record 拒绝、语法检查、前后 hash 纪律。
- **后续最少动态反例（真实 PG/运行卡，获授权后）**：① 预扣后 DB 墙钟回拨 → 剩余额度不变；② 活跃窗口单调到期 → 进程被强制终止且预留不退；③ 崩溃重启 → 新认领折叠旧预扣、旧代次晚到写入被拒；④ 监督进程死亡 → Job 连带终止 worker。不得以静态断言冒充（R-054 口径）；不默认回归 074 六例，仅当实现改动触碰其夹具路径时回归受影响用例。
- **明确不在卡内**：业务学习/面试角色、G-3 业务结果提交闭环、HTTP 接线、用户库迁移、Redis、可观测性全家桶、租约抢占、新时间服务。

## 7. 真正待决事项（仅影响范围/数据/接口/成本/安全标准者）

1. activities 表 +3 列的 DDL 批准（004 新迁移 vs 002 修订、历史行回填口径）——主要数据模型变更，须 Astra + 必要用户确认。
2. 窗口/预算默认数值——第 13 节最迟确认门（STEP-008 实际调用前）；机制不依赖具体数值。
3. 崩溃后不抢占租约的可用性代价（最长等一个窗口 W 才能续跑）是否接受——推荐接受；如需抢占另出卡，不在首段内加。

其余（结算夹紧、折叠时机、Job 自检、宽限大小等）均为实现细节，已给推荐，不需用户裁决。

## 8. 未验证与风险

- 本卡全部结论基于只读源码与 072/074/060/R-054 既有证据；未运行任何测试，未动态验证时钟、监督或重启行为。
- 残余风险（明确保留）：DB 墙钟回拨在"写租约后、判定前"仍可拉长单租约判定窗口，上界 3600s+deadline 封顶，总后果被预扣计数器封顶；彻底消除需单调持久时钟（新服务/新依赖），未获授权不引入。
- gateway 超时与窗口的配置耦合若实现遗漏，单次调用可能超出窗口尾——实现卡以配置校验收口。

## 9. 文档建议（交 Astra，本卡不改正式 docu）

1. FLOW-005 补一段裁定：时间预算=持久计数器预扣/折叠/结算，非时间戳比较；DB 墙钟仅辅助判定，回拨残余由计数器封顶；跨重启无持久单调时钟，以预扣 + 失败关闭保守恢复；不得把时钟源替换单独记为 M-1 修复。
2. 执行状态登记 TASK-075 行；架构按验收结论更新 R-068 段预留表述。
3. docu/CHANGE.MD 登记本结果与证据文件（Astra 职责）。

## 10. 证据

- Ndocu/results/TASK-075-result.md（本文件）
- Ndocu/evidence/task-075/read-scope.md（读取范围与只读声明）
- Ndocu/evidence/task-075/read-hashes.txt（18 个读取文件 SHA-256；repository.py 与 R-065 登记一致）
