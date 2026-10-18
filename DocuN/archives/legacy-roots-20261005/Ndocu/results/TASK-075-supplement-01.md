# TASK-075 补充01：六项决策缺口修订（结果）

任务：TASK-075 / R-069 定向修订补充（沿原卡，不占新 TASK/R）；父 TASK-060；STEP-008。
日期：2026-09-21（Asia/Shanghai）。根：D:/shspic/project_NO3_RetroLume-agent。
基线：需求 v1.1；架构 v0.25；执行状态 v1.19。
状态：本补充为**未实施方案**（未实施任何代码/DDL/接口变更，未动态验证）。原 075 结果与证据不覆盖；原方案中"缺口定位、预扣计数器方向、单调监督方向、代次恢复骨架"保留，以下仅修订六项决策缺口。每节先写修订前→修订后差异。

## 修订1：删除不成立的真实时间上界（安全性与可用性分开）

**修订前（原075 §2.1-6/§3/§7）**："崩溃后最长等一个窗口 W""残余回拨窗口 ≤3600s+deadline 封顶"——均为无依据表述，删除。
**修订后**：

- **安全性（方案可保证，不依赖墙钟）**：① 预算账不超发——由持久计数器 + CHECK 保证，回拨/前跳/重启均无法增加额度账；② 活跃自有执行有界——由 worker 进程单调看门 + 外层 Job 强终止保证，与 DB 时钟无关。DB 墙钟回拨只影响租约/deadline 的**墙钟判定**（谁能取得新认领/准入），不产生任何无预算的执行。
- **可用性（方案不保证上界，诚实声明）**：崩溃/重启后新认领须等旧租约按 DB 墙钟判定过期；若回拨 Δ，等待至少延长 Δ，**Δ 无上界 → 恢复等待时长无真实时间上界**。deadline_at 同为墙钟，不提供封顶（原表述删除）。预扣计数器约束的是"额度账"，不自动约束等待的实际时长。
- **当前方案内的确定性恢复出口**：cancel_activity（repository.py L305-328）判据是状态/代次而非时钟，人工取消可立即解除等待并触发旧代次收敛——这是无界等待下唯一不依赖墙钟的确定性手段，写入使用说明。
- **抢占推荐：暂不引入**（不扩范围）。重评条件：实际观察到回拨/前跳事件，或可用性要求"恢复等待有界"成为硬性标准时，另出"受监督抢占（取消+收敛+新代次）"卡。
- **不降低标准**：NFR-003 的"时间上限"由预算账 + 单调监督承载（新动作可拒绝、活跃执行可终止）；**恢复等待时长不在该保证内**，此边界如实写入文档建议，不以用户接受风险将其标为已满足。

## 修订2：时间轴精确定义与闭合

**修订前**：仅"timeout≤W""各层 W+宽限"——不闭合。**修订后**：

- **顺序与截止不可延后**：外层监督 ready（Job 已建+配置+句柄唯一持有+armed 握手，见修订4）→ 才允许认领 → **认领事务提交时点即固定窗口单调截止 T = t_claim_mono + W**；此后任何阶段不得重置/续满 W（删除"认领完成后重新起满 W"的可能）；全链唯一宽限 = 外层 kill 截止 T+grace（单一、显式配置），不再各层另加宽限。
- **各耗时归属（逐项）**：
  | 阶段 | 是否计入窗口 W | 说明 |
  | 认领事务自身（含其行锁等待） | 否 | 提交前无副作用；失败即无窗口。lock_timeout 2s 限制其时长 |
  | 启动自检/DB 健康检查 | 否 | 认领前、只读 |
  | 旧项分批收敛（每批短事务含锁等待） | 是 | 每批前查单调剩余，不足即停 |
  | admit/mark/record 各短事务（含锁等待） | 是 | 每事务 lock_timeout 2s |
  | 网络往返 | 是 | asyncio.timeout |
  | 结算事务 | 是 | 受 settle_margin 保护（下条） |
- **发送门槛（取代"timeout≤W"）**：发起 admit 前自查单调剩余 R，要求 **R ≥ request_timeout + settle_margin**（两项均显式配置、缺省拒绝启动）；不满足则本窗口不再发新请求，转入停止/结算。
- **额度计费、停止请求、确认停止三分**：
  - 额度计费 C = min(E_stop_req, W)——钳制**仅用于账**（预扣为 W，最大计费 W）；不得用钳制把实际超时改写成"准时"。
  - t_stop_req（看门到点或正常收尾决定停止新动作）与 t_stop_confirmed（进程退出/Job 终止确认，WaitForSingleObject 实测）分开记录。
  - **超窗判定**：t_stop_confirmed > T+grace 或需要外层 TerminateJobObject → 窗口结果记 overrun 失败（error_code=window_overrun，含实际耗时与清理耗时），计费全额 W（释放 0）；清理耗时（kill 后 5000ms 等待等）记入诊断，不隐去。
- **明示缺口（不作绝对实时调度承诺）**：结算事务遇 DB 延迟尖峰可能耗尽剩余时间 → 外层 kill → 该窗口按崩溃折叠（全额计费）；settle_margin 降低但不消除此概率。预扣 W 覆盖"计入执行的全部阶段 + 结算余量"，覆盖失败时以保守计费收场，不承诺精确实时。

## 修订3：结算与停止新动作闭合（窗口=代次）

**修订前**：settle 仅"running+executor+generation 校验 + reserved/settled 调整"，且"旧代次一切晚到写入被拒"——不闭合：退款后同代次仍可 admit/mark；幂等/竞争未定义；旧 permit UNKNOWN 语义被错误归入"拒绝"。**修订后**：

### 3.1 原子窗口关闭/结算规则

settle_execution_window(activity_id, executor_id, execution_generation, window_seconds, charged_seconds) 单短事务（来源→活动锁序）：

1. 校验链：status='running' ∧ executor 匹配 ∧ generation=请求值 ∧ running_reserved_seconds == window_seconds ∧ 0 ≤ charged_seconds ≤ window_seconds。
2. 效果：settled += C；reserved −= (W−C)；**execution_generation += 1；status='pending'；executor_id=NULL；lease_expires_at=NULL**；记录 last_settled_generation/last_settled_seconds（幂等确认用）。
3. 闭合性质：**退款后同代次不可能再 admit/mark**（代次已失效，_activity_allows L514 代次等值检查拒绝）；租约同时消失，发送资格关闭。

释放前置条件（两侧分保证）：
- **账本侧**：上述校验链（代次/执行者/状态/预扣额一致）。账本看不见网络，"无可继续出站路径"不由账本证明。
- **worker 侧协议**：停止新动作（t_stop_req）→ 本窗口全部已 admit 操作到达账本终态或已尽力记 unknown（gateway 既有 CancelledError best-effort 路径）→ 才调 settle。违约晚到的 record_outcome 按既有语义处理（见 3.3），不产生预算洞。

### 3.2 结算前后各自能力

| 时点 | worker 可做 | 监督者可做 |
| 结算前（窗口存活） | admit/mark/record（受 R−margin 门槛）；t_stop_req 后停新动作 | kill 截止 T+grace 到点强杀 |
| 结算后（本代次失效） | 不再 admit/mark；record 仅剩 UNKNOWN 诊断路径；可退出或新认领（新代次，重新折叠+预扣） | kill 截止继续有效至 worker 退出或新窗口握手更新；无新窗口且静默 → 按截止处理 |

### 3.3 幂等/竞争结果表（依据=设计校验逻辑推演+既有同型机制定位；未实施未验证）

| 场景 | 结果 | 依据来源 |
| 重复相同结算（事务成功但响应丢失后重试，同 C） | last_settled_generation 命中且 C 相同 → 返回 already_settled 确认，账面不变 | 新增幂等列比对 |
| 冲突 E（同代次两个不同 C） | 命中代次但 C 不同 → distinct conflict 拒绝（缺陷信号，记脱敏诊断） | 同上 |
| 结算成功但响应丢失、worker 崩溃未重试 | 无重试 → 下次认领折叠全额 W（保守计费，无泄漏） | claim 折叠规则 |
| 正常关闭与 cancel 竞争 | 活动行锁串行：先提交者生效；cancel 先 → settle 见代次不匹配拒绝且 W 已被 cancel 折叠全额；settle 先 → cancel 走既有取消路径 | repository.py 锁序 L311/L337/L440 同型 |
| 下一代认领后旧 settle 晚到 | 代次不匹配拒绝；旧 W 已在认领折叠时全额计费，不退款 | claim 折叠规则 |
| 结算窗口内在途操作晚到 record_outcome | 非 UNKNOWN → 拒绝；UNKNOWN → 保守记账（诊断终态） | 既有 L707-709 语义，本方案不改 |

### 3.4 字段候选修订

3 列 → **5 列**：原 max_running_seconds / running_reserved_seconds / running_settled_seconds + CHECK(reserved+settled≤max)，新增 **last_settled_generation INT NOT NULL DEFAULT 0**、**last_settled_seconds INT NOT NULL DEFAULT 0**（仅服务幂等确认/冲突检测，为闭合协议真正所需的最小状态）。不加窗口 outcome 列：超窗失败记录入脱敏日志（§8 日志规则：事件码+时长）+ 全额计费可观察；若未来需要 DB 可查询的窗口历史，须单开 per-window 表，非最小，现在不做。
claim 语义扩展（签名不变）：折叠旧预扣 → 预扣 W → 代次+1。cancel 语义扩展：取消时折叠在途预扣（全额保守）。**不假定当前 002 DDL 已支持任何等待/关闭状态**——closed 状态复用 pending+代次失效表达，不新增 status 枚举值。

## 修订4：监督边界可实施化

**修订前**：IsProcessInJob 自检被表述为"候选细节"但未界定证明力；"三层监督"未给信任链。**修订后**：

- **IsProcessInJob 定位**：仅隶属检查（排除"不在任何 Job"的明显错配），**不能证明**：本监督者创建、限制设置正确、句柄唯一持有、监督丢失会关闭最后句柄。权威信任链由启动器自证：
- **最小顺序（复用 _windows_job.py 既有模式；源码行号定位，未运行验证）**：
  1. 受信启动器（未来 deploy 新入口或 start_local 扩展，非通用监督平台）先 CreateJobObjectW + SetInformationJobObject（KILL_ON_JOB_CLOSE、内存/进程上限；L106-130）。
  2. CREATE_SUSPENDED 创建 worker（L135-147，bInheritHandles=False L141）→ AssignProcessToJobObject（L150）→ ResumeThread（L153）。挂起-关联-恢复为既有已验证模式（052 PDF 线），依据=源码定位，非本卡运行证据。
  3. Job 句柄仅启动器/监督者持有；不继承/复制给 worker。监督者死亡 → OS 关闭最后句柄 → KILL_ON_JOB_CLOSE 终止 worker。若任何第三方另持该 Job 句柄则此保证失效——以设计禁令+启动器私有承载，不做运行时验证承诺。
  4. worker 自检（IsProcessInJob 隶属 + DB 健康）→ 受控管道发 ready → 监督者回 armed → worker 才进入认领路径（armed 之前认领代码不可达）。
  5. 认领成功 → worker 上报（W、单调起点）→ 监督者设 kill 截止 T+grace（唯一宽限）。
- **失联 vs 挂死**：失联（管道关闭/监督者退出）→ worker 停止认领并自行退出，Job kill 随后兜底；挂死（管道在但无响应）→ worker 失败关闭、不发起新认领。**诚实缺口**：监督者挂死（存活但持有句柄不执行）+ worker 进程整体挂死（阻塞型不耗 CPU）的组合无自动终止手段——进程内看门线程**不能覆盖进程自身挂死**（修订前表述降级：它只是及时停止新动作的第一层）；Job CPU 时间限制（现有结构体字段 L77 未用）只覆盖空转型，不覆盖阻塞型。处置=启动器级重启策略（未来配置项），本方案不解决、不承诺。
- **杀伤范围**：Job 仅含本次 worker（ActiveProcessLimit 2 兼容 venv launcher，既有 L122），不全局杀进程，符合 SEC-002"停止只处理自有工作"。

## 修订5：迁移与兼容影响

**修订前**："002 仅合成库执行过且 074 后六表清零，空表加列可行"——外推不当。**修订后**：

- **074 清零事实范围**：仅证明 074 当次新建合成库为空，不外推到任何其他库（用户库、其他合成库、含历史行的任何库）。
- **004 候选迁移保守规则**：仅当 activities 表为空时执行；**非空 → 拒绝自动迁移并退出**，要求明确回填决策（逐活动设定时间预算，或先迁移后建活动）；不默认无限/免费时间，不编造回填默认值。002 保持冻结不动，004 为独立候选文件。
- **ActivitySpec 新必填字段的实际调用位置**（rg 核实）：backend/tests/test_activity_ledger.py L95、L154；backend/tests/test_activity_recovery.py L112、L276。产品代码零构造点（main.py 不导入 activities）。受影响范围 = 这两个测试文件 + 未来全部调用方。
- **证据影响（诚实版，替代原075"旧证据绝对不受影响"表述）**：实现卡修改 repository.py 后，其 hash 不再匹配 072/074 的审计/验证输入；设计结论（锁序、终态纪律）仍可参考，但按"相关变化使受影响证据失效"规则，动态证据须在实现卡获授权运行时重跑：claim/cancel/settle 相关用例（test_activity_ledger，051/055 范围）必然受影响；recover/list 切片方法本身不改，但同文件变更 + 夹具需补新必填字段 → 074 六例也一并回归。现在不重跑任何测试。

## 修订6：收敛为可决策材料

### 6.1 唯一推荐（修订后方案 A：窗口=代次预扣制）

- **账本保证**：预算账不超发（计数器+CHECK，DB 层失败关闭）；发送资格一次性（唯一操作键）；代次失效即关闭 admit/mark；结算幂等（last_settled_* 比对）与保守折叠（不退不泄漏）；DB 不可用拒绝一切有副作用事务（既有 AdmissionUnavailable）。
- **监督保证**：armed 之前无认领路径；活跃进程在 T+grace 内被 Job 强制终止；监督失联 worker 自杀。
- **分工边界（不互相冒充）**：账本不保证实际执行时长（只保证账）；监督不保证预算（只保证终止）。实际执行时长 = min(单调监督截止, 预算账拒绝点)，两者叠加构成安全线。
- **配置策略**：窗口长度 W、grace、settle_margin、request timeout **全部显式必填、缺省拒绝启动**（失败关闭）；合法范围：W∈[1,3600] 且运行时钳制 ≤ 剩余额度；grace/margin>0 且上界由配置校验；**不编造 300–600s 产品默认值**（原075 §2.2 该建议删除），数值留第 13 节确认门。

### 6.2 事件/状态表（完整最小序列）

| 步 | 执行者 | DB 事务 | 状态/账面变化 | 前置 | 失败行为 |
|---|---|---|---|---|---|
| 0 启动器建 Job→挂起创建→关联→恢复→ready/armed 握手 | 监督者/worker | 无 | — | 受信启动 | 握手失败→不进入认领，退出 |
| 1 DB 健康检查 | worker | 只读 | — | armed | 不可用→退出 |
| 2 认领：折叠+预扣 W+代次 G+1 | worker | 短事务 | pending→running；reserved=W；gen=G+1 | 旧租约墙钟已过期/无租约（或人工已 cancel）；来源/期限通过 | 冲突/不可用→无窗口；等待时长无上界（修订1），人工 cancel 为确定性出口 |
| 3 上报窗口→监督者设 T+grace | worker→监督者 | 无 | — | — | 上报失败→不 admit，自行结算退出 |
| 4 旧项分批收敛/复查 | worker | 每批一短事务 | 旧代次→unknown（072/074 方法） | 每批前查剩余 | 窗口耗尽→停止，转 6/7 |
| 5 准入/发送/结果（循环） | worker | admit/mark/record 三短事务+事务外网络 | requests/cost 计数、操作终态 | R≥timeout+margin | 拒绝→不发送；unknown→不重发（既有） |
| 6 停止新动作 | 看门线程 | 无 | 记 t_stop_req | — | — |
| 7 结算 settle（原子关闭） | worker | 短事务 | running→pending；settled+=C；reserved−=(W−C)；gen+1；last_settled_* | 3.1 校验链+worker 侧顺序 | 重试幂等；崩溃→下次认领折叠全额 |
| 8 退出或回 2 | worker | — | — | 剩余额度>0 | — |
| X 超窗/崩溃 | 监督者/Job | — | reserved 残留 W；结果记 overrun（日志）| — | 下次认领折叠全额；旧代次晚到写入按 3.3 |
| Y 人工取消 | API/人工 | 短事务 | cancelled；折叠全额；gen+1 | — | 幂等（已取消返回当代次） |

### 6.3 集中待批准清单（主要数据模型/接口变更，含原因/代价/失败处理）

| # | 待批准项 | 原因 | 代价 | 失败处理 |
| 1 | 004 候选 DDL：activities +5 列 + CHECK；claim/cancel/settle 语义变更（窗口=代次） | NFR-003 时间上限的持久实现 + 结算闭合协议所需最小状态 | 两测试文件夹具更新；repository hash 变化→相关动态证据重跑；实现复杂度高于纯时钟方案 | 迁移仅空表执行，非空拒绝并要求回填决策；CHECK 拒绝超额预扣即失败关闭 |
| 2 | 受影响证据重跑范围确认（051/055 范围必跑；074 六例随实现回归） | repository.py 变更使原 hash 证据失效 | 一次真实 PG 运行卡额度 | 按既有运行卡流程 |
| 3 | 可用性取舍：不抢占租约 + 回拨后恢复等待无界（人工 cancel 为确定性出口） | 避免引入不可靠的时钟型抢占 | 极端回拨下恢复延迟不定 | 重评条件见修订1；触发时另出抢占卡 |

未闭合的技术正确性（修订2 的实时调度缺口、修订4 的双挂死缺口）**不交用户投票**，作为明示缺口保留在方案边界内，由保守计费/失败关闭兜底；只有上表三项需批准。

### 6.4 后续最小实现边界与验证（全部未执行）

- **允许文件**：repository.py(+__init__)、migrations/004（候选）、backend/app/worker/（runner/监督/握手/看门）、backend/tests 定向补充（含 ActivitySpec 夹具更新）；不改 main.py/HTTP/网关语义/锁序/002。
- **静态验收**：5 列 CHECK 行为、折叠/预扣/结算/幂等/冲突/代次失效的单元级断言、配置缺省拒绝、语法、hash 纪律。
- **动态反例（获授权运行卡）**：①回拨后额度账不变且等待无上界如实呈现（可用性项不判失败）；②T+grace 强杀→预留全额折叠+overrun 记录；③崩溃重启折叠+旧代次晚到 settle/record 结果符合 3.3；④监督失联→worker 自杀+Job 兜底；⑤幂等重试/冲突 E/cancel 竞争三例（3.3 表落码）；⑥armed 前认领路径不可达。
- **不在卡内**：业务角色、G-3 业务结果提交、HTTP、用户库迁移、Redis、可观测性全家桶、抢占、通用监督平台。

## 保留风险与真正待决（汇总）

1. 待决三项见 6.3（DDL+语义、证据重跑范围、可用性取舍）。
2. 明示缺口（不承诺）：实时调度精确性（修订2）、双挂死自动终止（修订4）、回拨下恢复等待无界（修订1）。
3. 全部内容为未实施方案；072/074 仓储证据在其原 hash 范围内继续有效，repository.py 实际变更后按修订5 规则重跑。

## 证据

- Ndocu/results/TASK-075-supplement-01.md（本文件）
- Ndocu/evidence/task-075/supplement-01/read-scope.md（补充读取范围与只读声明）
- Ndocu/evidence/task-075/supplement-01/read-hashes.txt（3 个新增读取文件 SHA-256）
