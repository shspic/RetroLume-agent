# TASK-076 结果：075 补充01 结算与监督定向纠错（结果）

任务：TASK-076 / R-070；类型：定向方案纠错；STEP-008；父 TASK-075；关联 NFR-002/003、SEC-002、FLOW-005、DATA-007。
执行者：Codex Sol C档（全新会话，不沿 075 执行会话）。
日期：2026-09-22（Asia/Shanghai）。项目根：D:/shspic/project_NO3_RetroLume-agent。
基线：需求 v1.1；架构 v0.25；执行状态 v1.20。
状态：**未实施方案**（只读纠错；无代码/DDL/接口变更；无任何测试或静态检查运行；本卡不是独立安全审计，不声称独立审计通过）。075 补充01 保留部分（缺口定位、预扣计数器方向、单调监督方向、代次恢复骨架、072/074 仓储证据）在其原 hash 范围内继续有效。

## 0. Astra 八项确认问题的处置一览

| # | 确认问题 | 本卡处置 | 依据定位 |
|---|---|---|---|
| 1 | settle 的 `settled+=C; reserved-=(W−C)` 算术错误 | 改为 `settled+=C; reserved-=W`（整窗移出预扣，仅 C 计入已结算）；给出守恒证明（§B 前置）；新增 DB CHECK 使错误公式在库层被拒绝（§A 不变量 I2） | 075补§3.1；单开放窗口不变量 |
| 2 | 提交响应丢失不能撤销已提交事实；下次 claim 不得折叠已结算的 W | settle 提交后持久状态即 `pending ∧ reserved=0`，下次 claim 是普通认领，**不折叠**；折叠只发生在 `running ∧ reserved>0`。075补§3.3 第3行"无重试→折叠全额"表述修正 | 075补§3.1/§3.3 |
| 3 | last_settled_* 仅一个历史值 | 限定为**受限幂等契约**：仅可确认最近一次已结算代次；更旧请求一律"代次不匹配"拒绝且不改账、不退款（无重复扣账、无误退款） | §A 行5b、§B2 覆盖不足 |
| 4 | armed—认领—上报间空档；截止不得后移；提交时点不可凭空取得 | 监督者在 armed 时点即固化 D_report（有限认领等待）与 D_total（进程总截止），先于任何认领存在且不后移；窗口级 D_kill 基于上报时单调读数（≥真实提交时点），如实声明测量差 | §C；075补修订4 |
| 5 | 关闭时在途操作；退款前须停止证据；settle 主体与退出后结算 | settle 主体=worker 自身且仅在存活期间；退出后**无人代为结算**，残留预扣由下次认领折叠全额（保守不退款）；部分释放（W−C）只在 settle 提交成功时发生 | §A 行3/行4、§C 步8-10 |
| 6 | 停止请求时点计费忽略后续执行；grace 免费累计 | C 计至本窗口**最后一次账本动作**（settle 发起），不以 t_stop_req 截断；停止请求/停止确认/结算开销/清理开销四项分开记录；账面钳制 W 与实际墙钟超额分别记录，由 D_total 封顶总量；不宣称钳制后无超额 | §C 步7-10、§D 计费定义 |
| 7 | cancel 是放弃出口，不是恢复 | cancel 折叠在途预扣全额、活动永久终态（既有 claim L288 拒绝再认领）；回拨下租约等待无真实时间上界，cancel 是唯一不依赖墙钟的确定性出口——保留 075补修订1 结论 | repository.py L288/L305-328 |
| 8 | 不以同文件 hash 变化作全套重测理由 | 按 claim/cancel/settle/夹具的具体依赖列受影响用例（§E）；不重复 074 有效证据 | §E |

---

## A. 最小状态转换表

### A.0 字段与记号（候选 004 列，均未实施）

activities 表现有列不变（002 L4-32），候选新增：

- `max_running_seconds INTEGER NOT NULL CHECK (>0)` —— 活动时间总预算 M（对应 NFR-003 时长上限的持久实现）。
- `running_reserved_seconds INTEGER NOT NULL DEFAULT 0` —— R，未结算窗口预扣。
- `running_settled_seconds INTEGER NOT NULL DEFAULT 0` —— S，已结算。
- `last_settled_generation INTEGER NOT NULL DEFAULT 0` —— LSG，最近一次成功结算的代次。
- `last_settled_seconds INTEGER NOT NULL DEFAULT 0` —— LSs，最近一次成功结算的 C。
- `CHECK (R>=0 AND S>=0 AND R+S<=M)`（不变量 I1/I3）。
- `CHECK ((status='running' AND R>0) OR (status<>'running' AND R=0))`（不变量 I2；**该 CHECK 使 075补 §3.1 的错误公式在库层被拒绝**：错误结算会留下 `pending ∧ R=C>0`，违反 I2）。

派生量：A（可用余额）= M − S − R ≥ 0，不落列。既有 002 CHECK（running ⇒ executor/lease 非空，L28-31）兼容保留。
状态记法：status ∈ {pending, running, cancelled}；gen=execution_generation；exec=executor_id；lease=lease_expires_at。
内部接口（无 HTTP）：`claim_lease` 语义扩展（需新增 window_seconds 参数，签名变更留实现卡）；`settle_execution_window(activity_id, executor_id, generation, window_seconds, charged_seconds)` 新增；`cancel_activity` 语义扩展（折叠在途预扣，签名不变）。admit/mark/record/recover 系列不改（代次/状态既有校验已闭合，L508-525、L698-722）。

### A.1 状态表

| 行 | 字段/状态前值 | 事件 | 事务前置（全部满足才提交） | 原子后值（单事务） | 允许下一动作 |
|---|---|---|---|---|---|
| 1 | status=pending ∧ R=0 ∧ A≥1 | claim(exec, W) | 活动存在∧来源有效∧未取消∧未过期（L288）；W_eff=min(W, A) 且 W_eff≥1 | R=W_eff；gen+=1；status=running；exec 设置；lease=min(deadline, now+lease_seconds) | admit/mark/record（窗口内）；settle；cancel；崩溃（行4） |
| 2 | status=running ∧ (lease IS NULL ∨ lease≤now) ∧ R=W_open>0 | claim(exec, W') | 同行1（折叠后 A'≥1） | **折叠：S+=W_open；R=0**；再预扣 R=min(W', M−S)；gen+=1；exec 更新；lease 重设 | 同行1 |
| 3 | status=running ∧ exec=E ∧ gen=G ∧ R=W ∧ 0≤C≤W | settle(E,G,W,C) | 账本校验链如左（代次/执行者/状态/预扣额一致）。worker 侧前置（DB 不验证）：t_stop_req 后本窗口已 admit 操作全部到账本终态或已尽力记 unknown；C 计至 settle 发起时点（非 t_stop_req 截断） | **S+=C；R−=W（整窗移出）**；gen+=1；status=pending；exec=NULL；lease=NULL；LSG=G；LSs=C | 新认领（行1）；cancel；本代次一切 admit/mark/record 凭证失效（L508-525/L707-709 既有拒绝） |
| 4 | 行1/行2 后状态（running ∧ R=W） | worker 崩溃/被 kill（无 DB 事务） | — | 持久态不变（running、R=W、gen 不变）；lease 按 DB 墙钟在未来某刻过期（回拨延长等待=可用性缺口，075补修订1 保留） | 租约过期后 claim 折叠（行2）；人工 cancel（行6）；晚到旧 record 走既有 L707-709（非 UNKNOWN 拒绝/UNKNOWN 诊断） |
| 5 | settle 已提交（=行3 后值）但响应丢失，worker 重试 settle(E,G,W,C) | LSG=G ∧ LSs=C | **无账面变化**；返回 already_settled 确认 | worker 退出或继续新认领（行1）。**修正**：075补§3.3 第3行"折叠全额"错误——此时 status=pending ∧ R=0，下次认领不折叠 |
| 5b | 行5 后新窗口已建立（gen=G+1 running，或已再 settle 使 LSG=G+1），旧 settle(G,…,C) 再到 | LSG==G ∧ LSs==C → already_settled（跨窗口仍可确认**最近一代**）；LSG==G ∧ LSs≠C → distinct-conflict 拒绝（缺陷信号，记脱敏诊断）；LSG>G → 仅"代次不匹配"拒绝 | 三种分支均**不改账、不退款** | 无；旧 worker 写路径终局拒绝 |
| 6 | status≠cancelled | cancel() | 活动存在（L311-316） | 若 R>0：S+=R、R=0（在途预扣全额折叠，不退款）；status=cancelled；gen+=1；exec=NULL；lease=NULL。幂等：已 cancelled → 返回当代次，无变化 | **无**。cancelled 永久终态（claim L288 拒绝）。cancel 是放弃等待/终止活动的出口，不是恢复正常执行的路径 |
| 7 | gen 已大于旧请求携带的 G（新 claim/settle/cancel 已递增） | 旧 admit/mark/record 到达 | — | admit/mark：_activity_allows L514 代次等值失败→拒绝，无发送资格、无账变化；record 非 UNKNOWN→拒绝（L708-709）；record UNKNOWN→诊断记账（既有） | 无恢复路径 |

不新增 status 枚举值（closed 复用 pending+代次失效表达，075补§3.4 结论保留）。

### A.2 不变量（守恒性质，DB CHECK 强制）

- I1：0≤R，0≤S，R+S≤M。
- I2：status≠running ⇒ R=0（单开放窗口不变量：预扣只在 claim 增加、只被 settle/折叠/cancel 清零，任一时刻至多一个开放窗口）。
- I3：A=M−S−R≥0（由 I1 直接得出）。
- 事件增量（对 S, R, A）：claim 折叠 (+R_old, −R_old, 0)；claim 预扣 (0, +W_eff, −W_eff)；settle (+C, −W, +(W−C))；cancel (+R, −R, 0)。每事件三增量之和为零 ⇒ **S+R+A=M 恒成立**。
- 无重复扣账：一个窗口的 W 离开 R 恰好一次（settle 的 R−=W，或折叠/cancel 的重分类），其消耗计入 S 恰好一次（settle 的 +C，或折叠/cancel 的全额 +W）；settle 与折叠对同一窗口互斥（settle 置 pending∧R=0，折叠要求 running∧R>0），两者不可能先后命中同一 W。
- 无泄漏退款：W−C 只在 settle 提交时一次性回 A；崩溃/取消路径退款为零。

---

## B. 三条数值轨迹（手工推演，非程序测试）

统一口径：M=200（max_running_seconds）；第1窗口 W=100、消耗 C=20。初始 S=0、R=0、A=200、gen=0、status=pending。

### B1 正常窗口

| 步 | 事件 | S | R | A | 其他 |
|---|---|---|---|---|---|
| 0 | 初始 | 0 | 0 | 200 | gen=0, pending |
| 1 | claim(exec,W=100)：W_eff=min(100,200)=100 | 0 | 100 | 100 | gen=1, running, lease 设置 |
| 2 | 窗口内 admit/mark/record（不动 running_* 计数），消耗 20 | 0 | 100 | 100 | — |
| 3 | settle(E,1,100,20)：S+=20, R−=100 | 20 | 0 | 180 | gen=2, pending, LSG=1, LSs=20 |

守恒验证：步3 后 S+R+A=200 ✓。预扣 100 整体退场：20 入 S（消耗一次），80 一次性回 A。对比 075补§3.1 错误公式（S+=20, R−=80 → R=20、S=20、A=160）：committed 变为 40，同一 20 秒被预扣与已结算双计，且残留 R=20 违反 I2 会被新 CHECK 拒绝——错误在库层不可提交。

### B2 同一提交响应丢失再重试

| 步 | 事件 | S | R | A | 其他 |
|---|---|---|---|---|---|
| 0-1 | 同 B1 步0-1 | 0 | 100 | 100 | gen=1, running |
| 2 | settle 事务**提交成功**，响应丢失：S+=20, R−=100 | 20 | 0 | 180 | gen=2, pending, LSG=1, LSs=20（持久事实，不因响应丢失而撤销） |
| 3 | worker 未收到确认，重试 settle(E,1,100,20) | 20 | 0 | 180 | 前置命中 LSG=1∧LSs=20 → **already_settled，账面不变** |
| 4 | （若重试携带 C=25，缺陷信号） | 20 | 0 | 180 | LSG=1∧LSs=20≠25 → distinct-conflict 拒绝，账面不变 |

**幂等覆盖不足（如实指出）**：若步3 之前 worker 已 claim 新窗口（gen=2, running, R=W2）并成功 settle（LSG=2），则旧重试 settle(G=1) 既不匹配当前代次也不匹配 LSG → 仅"代次不匹配"拒绝，不改账、不能确认也不能退款。单历史值只保证**最近一次已结算代次**的幂等确认；更旧代次一律拒绝不改账（无重复扣账、无误退款，但无确认能力）——这是受限契约的明确边界，不声称无限历史幂等。本例（G=1 仍是最近已结算代次）在覆盖内。

### B3 未结算崩溃折叠 100

| 步 | 事件 | S | R | A | 其他 |
|---|---|---|---|---|---|
| 0-1 | 同 B1 步0-1 | 0 | 100 | 100 | gen=1, running |
| 2 | worker 崩溃（无 settle 事务提交），持久态不变 | 0 | 100 | 100 | lease 按 DB 墙钟等待过期（回拨则延长，可用性缺口如实保留；人工 cancel 为确定性出口） |
| 3 | 下次 claim(exec,W'=100)：折叠 S+=100→R=0；再预扣 W_eff=min(100, 200−100)=100 | 100 | 100 | 0 | gen=2, running |

守恒验证：步3 折叠前后 S+R 均为 100（纯重分类，A 不变）；再预扣后 S+R+A=200 ✓。崩溃窗口全额 100 计入 S 恰好一次，无退款、无泄漏、无重复扣；全预算恰好耗尽（A=0），后续 claim 因 A<1 被拒。
对照修正点2：若步2 改为"settle 已提交但响应丢失且 worker 崩溃未重试"，持久态=pending∧R=0（B2 步2 状态），下次 claim 走行1 普通认领（不折叠），与 075补§3.3 第3行"无重试→折叠全额"相反——折叠只针对 `running ∧ R>0` 的真实未结算残留。

---

## C. 最小监督时序（有限故障模型）

记号：D_* 均为监督者单调时钟截止，armed 时点固化后**不后移**。kill = TerminateJobObject + 有限等待确认（≤5000ms，复用 _windows_job.py L159-161 模式）。监督者不触账本（SEC-002：停止只处理自有工作；账本写入只经仓储接口）。

| 步 | 监督者 | worker | DB |
|---|---|---|---|
| 0 | 建 Job（KILL_ON_JOB_CLOSE/进程数/内存限制，L115-130 模式）→ 挂起创建→关联→恢复（L135-153 模式）；句柄私有不继承 | — | — |
| 1 | — | 自检：IsProcessInJob 隶属（仅排除明显错配，不作权威证明）+ DB 健康只读 → 发 ready | 只读 |
| 2 | 收 ready → **回 armed 的同一时点固化两个预算并告知 worker**：D_report=t_armed+τ_report（有限认领等待：覆盖 DB 健康检查+单次 claim 事务+上报通道；claim 事务自身已有 connect 3s/lock 2s/statement 3s 上界，repository.py L91-101）；D_total=t_armed+τ_total（整个 worker 进程含任意数量窗口+结算+退出的不可延后总截止）。armed 之前认领代码不可达（075补修订4 保留） | 收 armed | — |
| 3 | — | claim → 记 t_report_mono（claim 响应后单调读数；真实提交时点 t_commit≤t_report_mono，客户端不能取得准确提交时点，**不用于账面**） | 行1/行2 事务（提交时点即账面窗口起点） |
| 4 | 收上报 (W, t_report_mono) → 设 D_kill=t_report_mono+W+grace（唯一窗口级宽限，不后移；因 t_report_mono≥t_commit，D_kill 晚于理想真截止至多上报时延，如实记录，不宣称精确 W） | — | — |
| 5 | 任何时点：上报未到且过 D_report → kill；过 D_total → kill；过 D_kill → kill | 窗口内循环：admit/mark/record 短事务+事务外网络；发送门槛 R剩余≥request_timeout+settle_margin（单调自查）；看门线程记 t_stop_req | 行3/行7 既有语义 |
| 6 | — | t_stop_req → 已 admit 操作全部到终态或尽力记 unknown（有界：门槛保证在途请求在窗口内超时收敛） | — |
| 7 | — | 发起 settle（C 计至此时点，非 t_stop_req 截断） | 行3 结算事务 |
| 8 | — | settle 失败 → 有界重试至 D_kill/D_total → 仍失败则死亡（**退出后无人代为结算**） | 未提交则持久态保持 running∧R=W |
| 9 | 过 D_kill/D_total → kill → 确认进程终止（有限等待） | （已死或被杀） | 无事务；残留 R=W 待下次认领折叠（行4/行2），**保守不退款** |
| 10 | — | settle 成功 → 退出或回到步3（新窗口；新 D_kill 覆盖，D_total 不变） | 行3/行1 |

**计费与耗时口径（一致定义，回应问题6）**：
- 账面（M 账）：窗口 W 从 claim 事务提交起算；C 覆盖窗口起点→最后一次账本动作（settle 发起）；结算事务由 settle_margin 保护在 W 内。停止请求 t_stop_req、停止确认 t_stop_confirmed、结算开销、kill 后清理开销**四项分开记入诊断**，不截断 C。
- 监督账（不进 M）：τ_report、grace、kill 等待、上报时延。逐窗实际墙钟可超账面至多（上报时延+grace+清理等待），**分别记录**（事件码+实际时长+清理耗时），由 D_total 封顶进程总量；grace 不因逐窗累计而逃逸 D_total。不钳制后宣称无超额：账面封顶 W 与实际超额（overrun 诊断）两列并存。
- 退款前置（回应问题5）：部分释放 W−C 只发生在 settle 提交成功；退款的可信"停止证据"=worker 存活并发起 settle 前已使在途操作终态/unknown（worker 侧协议）+ 门槛保证。监督者不做退款决策；崩溃/被杀一律折叠全额。

**有限故障模型（明示，不承诺绝对实时调度）**：
- DB 延迟尖峰可耗尽窗口剩余 → kill → 折叠全额（保守计费收场），settle_margin 降低但不消除该概率。
- 监督者死亡 → OS 关闭 Job 最后句柄 → KILL_ON_JOB_CLOSE 终止 worker（信任链=启动器私有句柄，设计禁令承载，075补修订4 保留）。
- worker 失联（管道关闭）→ 停止认领并自行退出，Job 兜底。
- **双挂死缺口（不闭合，不宣称强终止已保证）**：监督者存活不动作 ∧ worker 阻塞型挂死——进程内看门不能覆盖自身挂死，KILL_ON_JOB_CLOSE 只在监督者死亡时生效，Job CPU 限制只覆盖空转型。处置=受信启动器的重启策略（未来配置项），本方案不解决、不增加新看门层（避免无限叠加）。
- 回拨下租约等待无真实时间上界（可用性项）；人工 cancel 为确定性出口（075补修订1 保留）。D_report/D_total 在进程级封顶"挂住不报/挂住不退"的墙钟（kill 或重启），不改变账面语义。
- 单调时钟跨进程可比性（同机 QueryPerformanceCounter）：方案推断，实现卡需一次静态确认（见§E）。

---

## D. 最少持久字段、接口与旧库拒绝策略

**推荐（唯一）**：
1. 持久字段：§A.0 的 activities +5 列 + 两条 CHECK（R+S≤M；I2）。不加 per-window 表、不加窗口 outcome 列（超窗/overrun 入脱敏日志+全额计费可观察，075补§3.4 结论保留）。
2. 内部接口：claim_lease 语义扩展（折叠+钳制+预扣+代次+1；**需新增 window_seconds 参数**）；settle_execution_window 新增（签名见§A.0）；cancel_activity 语义扩展（折叠在途预扣）。admit/mark/record/recover 系列零改动。
3. 非空旧库拒绝：004 候选迁移仅当 activities 表为空时执行（执行器前置 SELECT 计数，>0 即拒绝迁移并退出，要求明确回填决策）；074"清零"事实不外推到任何其他库（075补修订5 保留）。002 冻结不动。
4. ActivitySpec 新必填 max_running_seconds 的实际调用位置（rg 核实沿用 075补修订5）：backend/tests/test_activity_ledger.py L95、L154；backend/tests/test_activity_recovery.py L112、L276；产品代码零构造点。

**需后续批准的主要模型变更（本卡不是批准请求）**：① activities +5 列+CHECK 与 claim/settle/cancel 语义变更（窗口=代次预扣制）；② ActivitySpec 新必填字段的调用方/夹具影响；③ 受影响动态证据重跑范围（§E）。备选方案：无（推荐方案在上述明示缺口边界内闭合，无需备选）。

---

## E. 下一实现卡最小范围与必要验证映射

**允许文件**：repository.py（+activities/__init__）、migrations/004（候选）、backend/app/worker/（runner/监督/握手/看门）、backend/tests 定向补充。不改 main.py/HTTP/网关语义/锁序/002。

**受影响用例映射（按具体依赖列，不以文件 hash 变化为由全量重测）**：
- claim 语义变化 → test_activity_ledger 中 claim/租约相关用例。
- cancel 语义变化（折叠）→ cancel 相关用例。
- settle 新方法 → 新增用例：§B1/B2/B3 三轨迹、行5b 三分支（already_settled/冲突/代次不匹配）落码。
- ActivitySpec 夹具新必填字段 → 仅 4 处构造点更新（test_activity_ledger.py L95/L154、test_activity_recovery.py L112/L276）；recover/list 切片方法零改动 → 074 六例中仅夹具依赖部分需更新，**非全量重跑**（074 既有有效证据在其原 hash 范围内保留，不重复）。
- admit/mark/record 代码路径零改动 → 其行为用例不因 hash 变化重跑。
- 静态确认项（实现卡内）：单调时钟跨进程可比性（同机）；语法/导入检查；hash 纪律。
- 动态反例（获授权运行卡才执行，本卡不运行）：回拨后账不变且等待无上界如实呈现；D_kill 强杀→折叠+overrun 记录；崩溃重启折叠+旧代次晚到 settle/record；失联自杀+Job 兜底；幂等/冲突/cancel 竞争；armed 前认领不可达。

**不默认用户接受**：回拨恢复等待无界、双挂死缺口、受限幂等契约边界均为明示可用性限制，列入待决/明示缺口，不以"用户接受风险"标记为已满足（075补修订1 口径保留）。

---

## 未实施/未验证边界

- 本卡全部内容为方案级纠错，未实施任何代码/DDL/接口变更；未运行任何测试、compile、脚本计算、Docker、PG、应用、模型。
- §B 为手工推演（方案级算术验证），非程序测试；未验证≠通过。
- 单调时钟跨进程可比性、管道上报通道时延上界为实现卡静态确认项，本卡未验证。
- 072/074 仓储代次恢复证据在其原 hash 范围内保留有效；本卡未修改任何代码，不触发证据失效。

## 实际读取范围

见 Ndocu/evidence/task-076/read-scope.md（8 个文件，含哈希清单 read-hashes.txt）。

## 剩余问题

1. claim_lease 签名需新增 window_seconds 参数，具体形态（关键字参数/新方法）留实现卡定。
2. τ_report/τ_total/W/grace/settle_margin 数值不编造，留配置确认门（缺省拒绝启动，075补§6.1 口径）。
3. 双挂死缺口、回拨恢复等待无界：明示保留，处置为未来重启策略卡/抢占重评卡，本卡不闭合也不宣称闭合。
4. last_settled_* 单历史值的受限幂等契约：仅确认最近已结算代次；更旧请求拒绝不改账。若未来要求全历史幂等确认需 per-window 表（非最小，不推荐）。
5. 受监督抢占、业务角色、HTTP、用户库迁移、Redis 均不在本卡及下一实现卡范围。

## 证据

- Ndocu/results/TASK-076-result.md（本文件）
- Ndocu/evidence/task-076/read-scope.md（读取范围与只读声明）
- Ndocu/evidence/task-076/read-hashes.txt（8 个读取文件 SHA-256）
