# TASK-081 / R-075 结果：时间窗口监督与停止结算协议收敛（修正轮01 置顶）

- TASK-081 / R-075 修正轮01；STEP-008 局部；父 TASK-076；关联 077—079、NFR-002/003、SEC-002、FLOW-005、DATA-007。
- 基线：需求 v1.1、架构 v0.34、执行状态 v1.37；Git 基础提交 45951501d2741630a229762d6b2d3f4b34d7f702 及既有未提交文档差异已保护（本卡零代码改动）。
- 执行者：沿 081 原 Work Buddy 增强执行窗口（实际 GLM-5.3，如实登记）；本轮为定向设计纠正，非独立审计，不新增 TASK。
- 状态：**只读设计纠正**。未实施任何代码/DDL/接口变更；未运行任何测试/compile/PG/Docker/应用/模型/网络/安装；未读凭据；运行/费用预算 0。不填写编排最终验收，不宣告 M-1 或 STEP-008 完成。
- 首轮裁定接受：首轮设计不通过实施门槛；有限截止、失败保守处理、已提交事实不撤销等可用段落保留（未列修正处以首轮为准，首轮全文见本文件下半部分"首轮历史"）。撤回首轮"SWP-081 已收敛""五列零变更足以支撑完整协议""接受无上界作为推荐方案""SUP 不触账本是 SEC-002 要求"等表述。原任务卡归档 Ndocu/archives/TASK-081-before-revision01-20260924.md 只作追溯。
- 一句话结论：修正轮01 交付修订协议 SWP-081/R1（每会话单窗 + 上报 ack 确认门 + 窗口关闭条件 WCC + 持久会话预算候选 + 两级进程树终止确认）；F1/F4/F5/F6 设计级闭合，F2 的闭合以用户批准持久会话预算（005 候选两列+新内部方法）为条件——不批准则存在单一决定性缺口"跨恢复墙钟无不可重置上界"，F3 的闭合依赖单一待核 Windows API 事实（Job 对象 signaled / NumberOfActiveProcesses 归零语义）。

---

## 0. 闭合状态总表

| 缺陷 | 结论 | 残余条件 |
|---|---|---|
| F1 退款前关闭证明 | 已闭合（设计级）：WCC-1..4 可观察、不可重开 | WRK 诚实性为账本既有信任假设（与 elapsed_seconds 同级）；WCC 代码路径为实现后独立增强审计对象 |
| F2 跨恢复累计 | 条件闭合：持久会话预算候选给出不变量推导与反例处置 | 属主要模型变更，须用户批准（005 候选+ActivitySpec 必填）；不批准=单一决定性缺口，明示与 NFR-003 时间维差距，不冒充正确性方案 |
| F3 证据范围 | 条件闭合：两级终止确认 | 单一待核事实：Windows Job 对象 signaled/NumberOfActiveProcesses 归零语义（实现卡一次官方文档核对+最小探针；本轮无网络研究/探针） |
| F4 协议一致性 | 已闭合（设计级）：每会话单窗 + ack 门 + 顺序统一 + 全部上界条件化 | 多窗模式已否决（记录理由，不并行推荐） |
| F5 数值与恢复 | 已闭合：两路径分开、全部行 S+R+A=M、T4 具体值、F7 折叠/启动分离 | 无 |
| F6 不制造约束 | 已闭合：SEC-002 表述纠正、两层监督链承认、有限故障模型修订 | 三层同时不动作不覆盖（明示） |

## 1. F1—F6 逐项纠正

### F1 退款前关闭证明（替换首轮 INV3 与 S5/S6 前置）

**首轮缺陷（承认）**：S5 允许"unknown 后由存活 WRK 结算"，INV3 以资格失效替代停止证明——generation 变化只关闭后续仓储判定，不能撤回已越过发送门的动作，也不证明并发本地任务/子进程不再执行；"存活 worker 是唯一结算者"是主体声明，不是证明。

**修订：窗口关闭条件 WCC（Window Closure Condition）**，全部可观察、满足后不可重开：

- **WCC-1（本地任务终态）**：WRK 维护本窗口 in-flight 操作表：条目在 admit 成功时创建（绑定 admission_id/operation_id/generation，均经 LED 持久），在 record_outcome 提交成功或 RequestNotSent 确定未发送返回时移除。WCC-1 = 表空。绑定活动/代次由 admit 入库天然承载；表空时该窗口全部本地操作已到持久终态（含 UNKNOWN 诊断终态——如实：UNKNOWN 是账面终态，不是远端停止证明）。
- **WCC-2（新发送的结构性阻止）**：发送门槛=窗口剩余（WRK 单调自查）≥ request_timeout+settle_margin。若存在未终态在途操作，其收敛至少还需其剩余 request_timeout 时间，而此时窗口剩余不足以通过门槛——**"仍有在途 ⇒ 新发送不可能通过门槛"是结构性质，不依赖代码纪律**。
- **WCC-3（DB 级新 admit 阻止）**：协议约定 claim 时 `lease_seconds = window_seconds`（请求 W）。W_eff=W（无余额截断）时，窗口满期即 lease 到期，此后 `_activity_allows` 的 `lease_expires_at > now` 失败（repository.py L698-699）→ DB 层拒绝一切新 admit。**覆盖边界如实声明**：W_eff=min(W,A)<W（余额截断）时 lease（=W）晚于窗口满期，DB 级阻止不完整，该情形依赖 WCC-2+审计。零代码变更（claim 既有参数，调用方约定）。
- **WCC-4（无遗留执行载体）**：当前协议范围内 WRK 不拥有子进程；transport 每请求独立 AsyncClient、无持久连接池（transport.py L54-88），无待关闭通道。若未来 WRK 引入子进程/持久通道，WCC 必须扩展为逐项终止确认——协议预留该条目，不虚构当前已覆盖。

**确认主体与信任声明**：WRK 是唯一能观察 WCC-1 的主体。WRK 诚实性是账本**既有信任假设**（settle 的 elapsed_seconds、admit 调用本就依赖可信内部调用方；076 裁定"settle 仅为可信内部基础接口"），不是本协议新增信任；WCC 相关代码路径（表维护、门槛、lease 约定）列为实现后独立增强审计对象。

**退款规则（修订后）**：部分退款（S+=C、A 恢复 W_eff−C）**仅**发生在 WRK 的 settle 提交成功且其前置序列满足 WCC-1..4 时。不可重开性：settle 提交即 pending+G+1，本窗口资格永久关闭，in-flight 表随窗口销毁。一切其他路径（kill/崩溃/取消/代次外/监督者动作）折叠全额、退款为零。**不存在先退款后等待退出的路径**：退款时点=结算事务提交，与进程退出顺序无关。

**诚实边界**：WCC 证明"本地不再执行/发送"，不证明"远端已停止"——远端已接收请求不可撤销（首轮 §1.5 保留）；部分退款释放的是本地受控时间预算，远端维度由次数/费用账承载，两者不相混。若审计发现 WCC 实现缺陷，缺陷期间退款不可信，处置=修正+重新审计，不以"接受风险"替代。

### F2 跨恢复累计（替换首轮裁决项 1 及 §1.6 NFR-003 行、§6 配套明示）

**首轮缺陷（承认）**：τ_total 每会话独立，会话数由启动器重启策略（可重置配置）决定，不构成不可重置事实；"接受无上界"不可作为推荐正确性方案。

**四类时间口径（区分，不把一切墙钟误当 CPU 时间，也不缩小为仅账面守恒）**：

| 类 | 定义 | 计入 M | 有限总量由哪个不可重置事实控制 |
|---|---|---|---|
| T1 业务执行 | 窗口内 t0→settle 发起（含排空） | 是（C≤W_eff） | 持久 M |
| T2 窗级开销 | 上报时延+grace+kill 等待+结算事务 | 否 | ≤（δ_report+grace+kw+settle_margin）每窗；窗数≤M（每窗 W_eff≥1）→总量≤M×常数，由持久 M 控制 |
| T3 会话级开销 | 启动/自检/armed/ack/退出（含零窗口会话） | 否 | 每会话≤τ_total+kw；会话数须由**持久会话预算**封顶（下文） |
| T4 远端执行/用户等待 | 不可本地观测 | 否（次数/费用账承载） | 无本地墙钟声明（如实） |

**持久会话预算候选（主要模型变更，须用户批准）**：
- 005 候选迁移：activities 新增 `sessions_opened BIGINT NOT NULL DEFAULT 0`（CHECK ≥0）与 `max_sessions BIGINT NOT NULL`（创建时固化，CHECK 1≤max_sessions≤2147483647）及 `sessions_opened <= max_sessions` CHECK；仅空 activities 合成库模式（沿 004 纪律）。
- repository 新增内部方法 `open_execution_session(activity_id, executor_id) -> int`：锁序/超时同 claim（来源→活动行锁），原子 sessions_opened+1，已达 max_sessions 抛 ActivityLedgerConflict。调用主体=**LAUNCHER**（受信启动器，未来接线卡承载；本设计只定调用契约）——理由：LAUNCHER 是会话的最早发起者且必然存活于会话开始（spawn SUP 前调用），保证"凡有进程存在的会话必已计数"（WRK 秒死/挂死不漏计）；SUP 保持零账本（见 F6）；WRK 保持执行期唯一账本调用方。LAUNCHER 账本权限仅此一个方法（最小权限，审计点）。
- 协议顺序：open_execution_session 成功是 SUP 获得 armed 权的前置；失败（DB 不可用/超限）→会话失败关闭，无窗口、无执行。

**不变量推导（跨恢复墙钟上界）**：
- 前提1（持久）：sessions_opened≤max_sessions（DB CHECK+原子递增，回拨无效——计数不是墙钟函数；重启不重置——DB 持久）。
- 前提2（协议）：任何会话（含零窗口）必经 open_execution_session 计数后才 armed。
- 前提3（单会话，条件性）：在"SUP 获得调度执行，或 SUP 死亡触发 OS 关闭 Job 私有句柄"假设下，受控区间≤τ_total+kw（kw=kill 有界等待上界）。
- **推论：T_wall(活动) = Σ会话受控区间 ≤ max_sessions×(τ_total+kw) + M×(δ_report+grace+kw+settle_margin)**。右端全部由持久不可重置事实（max_sessions、M）与固定配置常数构成；重启策略/退避配置只能减少实际会话数，不能突破封顶（open_execution_session 是唯一递增入口）。

**跨重启反例处置**：
- 反例A（无限零窗口会话刷墙钟）：被前提2封顶（每会话必计数）。
- 反例B（时钟回拨重置）：计数/M 均非墙钟函数，无效。
- 反例C（DB 不可用绕过登记）：失败关闭，无 armed、无执行（可用性代价如实）。
- 反例D（open_session 提交响应丢失→重试重复递增）：多计会话→预算提前耗尽，保守方向，无免费墙钟；如实记录为可用性损失。

**若不批准**：跨恢复墙钟上界**不可闭合**——此为单一决定性缺口；M 仅保证账面（授权窗口预扣/结算/折叠）守恒，不冒充受控时间上界；推荐降级表述为"账面上界+每会话有界（会话数无上界）"，并明示与 NFR-003"跨恢复不重置"时间维的差距，**不将该降级写成正确性方案**。

### F3 证据范围（替换首轮 INV6 及 S7/F 行的"进程树终止确认"表述）

**首轮缺陷（承认）**：INV6 只 WaitForSingleObject(主进程句柄)——现有源码（_windows_job.py L156-161）仅支持"主进程退出确认"；主进程退出≠Job 内全部进程退出；"所需 API 全部明确"式表述撤回。

**修订（两级终止确认）**：
- 级1（现行可证）：主进程句柄有界等待 WAIT_OBJECT_0=主进程退出。
- 级2（完整树确认，拟实现）：TerminateJobObject 后等待 **Job 对象句柄 signaled**，或轮询 QueryInformationJobObject(JobObjectBasicAccountingInformation) 的 NumberOfActiveProcesses==0。
- **单一待核事实（显式，不臆测）**：Windows Job 对象 signaled 语义与 NumberOfActiveProcesses 对终止中进程的计数归零时机，未在本项目内验证；需实现卡一次官方文档核对+最小探针。本轮无网络研究/探针。
- 无法确认时处理：有界等待后仍疑有活动进程→记 unconfirmed-tree 诊断；Job 句柄保持打开至会话退出（KILL_ON_JOB_CLOSE 兜底）；该窗口账面折叠全额（保守）；且**不满足新会话启动门槛（见 F7）**——失败关闭，不宣称树已终止。

### F4 协议一致性（替换首轮 §2 时序框架与 S1/S3/S6）

**首轮缺陷（承认）**：S3 缺 SUP 接受上报后的确认门（flush/写成功≠SUP 已接受）；S6 多窗但 D_report 与一次性 accept_report 的换窗/旧消息隔离/旧截止撤换未定义；S1 自检先后含糊；一处承认调度暂停、一处写无条件绝对上界。

**修订——唯一模式：每会话单窗**：
- 每会话=恰好一个窗口；新窗口必须新会话（新进程、新 t_resume、新 τ_total、新 open_execution_session 计数）。**多窗模式否决**（已考虑替代，不并行推荐）：换窗截止撤换、D_report 复用、旧上报消息隔离需新增状态机，非最小；单窗代价=每窗进程启动开销（入 T3 会话开销，由 max_sessions 封顶），收益=无换窗状态机。
- **S3' ack 确认门**：WRK claim 成功→写上报行（stdout，W_eff 与 t0）→**阻塞等待 SUP ack 行（stdin）**；SUP 读到上报→一次性固化 D_kill=t0+W_eff+grace→写 ack；WRK 读到 ack→才允许首个 admit。flush 成功≠SUP 已接受的空档由 ack 门关闭；ack 不达（SUP 死）→Job 关闭杀 WRK（F3），无执行或执行被终止。
- **S1 顺序统一**：t_resume（SUP 固化 D_ready/D_total）→LAUNCHER open_execution_session 成功→SUP 固化 D_report=t_armed+τ_report 并下发 armed→WRK 自检（IsProcessInJob 隶属+LED 只读健康）→WRK 收 armed 才可 claim。armed 授予的是 claim 权，**不是出站资格**；出站资格仍唯一由 admit 时的 DB running+租约授予（INV1 不变）。顺序保证：任何 admit 发生前 D_ready/D_report/D_total 已固化、D_kill 已设（ack 门先于首个 admit）——"不得先授予出站再等监督安装截止"由顺序闭合。
- **上界声明统一（消除矛盾）**：本文件全部"有界/≤"声明均为**条件性**，共同前提="SUP 获得调度执行，或 SUP 死亡触发 OS 关闭 Job 私有句柄"；系统级调度饥饿、整机无限挂起不在模型内；休眠期无 CPU 执行（休眠影响计费偏差方向，时钟待核点保留）。首轮 INV4/INV5 的"≤"全部追加此前提注记，不存在无条件绝对上界表述。

### F5 数值与恢复（修正首轮 T2/T4/F7）

- **T2 修正**：首轮步4"折叠关闭后 S=100/R=0/A=0"错误（漏加第二次折叠）。分开两路径，全部行 S+R+A=M=200（M=200，窗1 W=100 残留折叠前）：
  - 路径A（成功占满余额，非 None）：残留折叠后 claim W'=100：S=100（折叠）、R=0→再预扣 W_eff=min(100, A=100)=100→**S=100, R=100, A=0**（成功认领，G+1，running）。此窗若正常 settle(C=30)：S=130, R=0, A=70。
  - 路径B（后续残留再次折叠耗尽）：若路径A 的窗口又崩溃（R=100 残留），第三次 claim：折叠 S=100+100=200、R=0，A=0≤0→**折叠耗尽分支**：提交折叠与关闭（pending、G+1）并返回 None→终态 **S=200, R=0, A=0**。守恒：200 ✓。
- **T4 修正（具体 G/R/S/A，旧幂等重试不改新窗 R）**：M=200。窗1：claim W=100→R=100, G=1；settle(E,1,100,20) **提交成功**（响应丢失）→S=20, R=0, A=180, LSG=1, LSs=20, G=2(pending)。重启新会话：open_session(#2)+claim W'=80→W_eff=min(80,180)=80→**S=20, R=80, A=100, G=3, running**。旧 settle(E,1,100,20) 晚到重试：LSG=1==请求 G 且 LSs=20==C→ALREADY_SETTLED，**账面不变（S=20, R=80, A=100）**，新窗口 R 不被改 0。若新窗口已先 settle（LSG=3）：旧请求 LSG=3≠1→进入运行态校验→代次不匹配→ActivityLedgerConflict 拒绝不改账。
- **F7 修正（撤回"两况皆安全"）**：区分两个动作——
  - **折叠（账面动作）**：任意时刻安全（折叠只重分类残留 R，与旧执行者死活无关）。
  - **新会话执行启动**：前置门槛=**旧会话进程树终止确认**（F3 级2；级2 实现前=级1+Job 句柄关闭确认）。旧 WRK 若仍活：其旧 admit 虽被 DB 拒（代次失效），但其**已越过发送门的在途请求不可撤回、其进程内本地计算仍耗真实墙钟**——与并行的新代次执行构成真实双重执行。故旧树未确认终止→不 armed 新会话（失败关闭，等待重试/人工介入，可用性代价如实）；确认终止→安全启动。剩余缺口：树确认依赖 F3 待核 API；确认失败且不人工介入→活动卡住（正确性优先于可用性），不以并行执行换可用性。

### F6 不制造约束（纠正首轮角色表述与监督层声明）

- **SEC-002 纠正**：撤回"SUP 不触账本是 SEC-002 要求"。SEC-002 实际要求=工具仅执行获准范围、参数非法/越权拒绝并记录、停止只处理本应用自有工作、跨恢复状态和预算须完整产品测试及风险对应独立审计；**并未规定监督者不能调用账本**。SUP 不触账本改为**方案选择**，理由：(a) SUP 无法观察 WCC-1（in-flight 表在 WRK 进程内），SUP 代结算会制造无证明的部分退款路径；(b) C 的正确口径（计至 settle 发起）只有 WRK 能取；(c) 双写主体增加账面竞争。备选（SUP 代结算）已评估并否决，理由如上。影响：实施与首轮相同，表述与审计验证点不变（SUP 不 import activities 为审计对象之一，但作为设计选择验证）。
- **两层监督链承认**：本方案监督结构=LAUNCHER（心跳健康检查+按持久会话预算重启 SUP）→SUP（Job 监督 WRK）两层，是**新增的监督责任**，不再称"未增加监督层"。上界：LAUNCHER 自身死亡→无自动重启（明示不覆盖，人工启动）；已计数会话不受 LAUNCHER 死亡影响（预算已持久）。双挂死处置修订：LAUNCHER 心跳可检测"SUP 存活但不动作"并重启 SUP（重启=杀旧 SUP→Job 句柄关闭→杀 WRK），把该场景暴露窗口降为检测周期+重启时长（有界，前提 LAUNCHER 存活）；**三层（LAUNCHER+SUP+WRK）同时不动作不在任何模型内**，不宣称解决。
- **正常路径与故障路径分离声明**：正常路径（无故障）每窗/每会话上界不依赖上述故障处置成立；故障路径的保守收场（折叠全额、失败关闭、活动卡住待人工）均为正确性优先，不以绝对保证掩盖正常路径缺口。

## 2. 唯一修订时序表（SWP-081/R1，每会话单窗）

角色：LAUNCHER（受信启动器，接线卡承载）/ SUP（拟新增 job_session+session_supervisor）/ WRK（拟新增 worker_main）/ LED（既有仓储）/ Job。单调截止 D_ready=t_resume+τ_ready、D_report=t_armed+τ_report、D_total=t_resume+τ_total、D_kill=t0+W_eff+grace，全部固化后不可后移、不读 DB 墙钟；lease_seconds=window_seconds（WCC-3，覆盖边界见 F1）。

| 步 | 事件 | 所有者动作 | 出站执行许可 | 持久态（提交后） | 允许下一动作（所有者） | 禁止 |
|---|---|---|---|---|---|---|
| S0 | 会话启动 | LAUNCHER 调 open_execution_session(E)（成功才继续）→SUP 建 Job、CREATE_SUSPENDED 创建 WRK→Assign→Resume；记 t_resume，固化 D_ready/D_total | 无 | sessions_opened+1（≤max_sessions） | S1（SUP→WRK） | 登记失败→会话失败关闭（无进程或进程即回收）；SUP 不触账本（设计选择，F6） |
| S1 | armed | SUP 固化 D_report 并下发 armed；WRK 自检（进程隶属+LED 只读健康）→ready | 无 | 只读 | S2（WRK） | τ 未配置→拒绝启动会话；armed 前认领代码不可达 |
| S2 | 认领 | WRK claim_lease(E, W, lease_seconds=W, window_seconds=W)；LED 原子：过期残留折叠（S+=R_old）→预扣 W_eff=min(W,A≥1) | 无 | running；R=W_eff；G+=1；lease=min(deadline, now+W) | S3（WRK） | 不得抢占有效租约；A≤0→LED 提交折叠关闭并返回 None→会话收尾（单窗，无回 S2） |
| S3 | 上报+ack 门 | WRK 记 t0（claim 响应后单调读数）、读 lease.window_seconds=W_eff→写上报(W_eff,t0)→**阻塞等 ack**；SUP 读到→一次性固化 D_kill→写 ack；WRK 收 ack | 无（首个 admit 待 ack） | 不变 | S4（WRK） | **ack 前禁止首个 admit**（顺序硬规则）；重复上报拒绝；flush≠SUP 已接受由 ack 门闭合 |
| S4 | 窗口执行 | WRK 循环 admit→mark_dispatch→出站（事务外网络）→record；门槛：窗口剩余≥request_timeout+settle_margin | **有**（DB running∧exec=E∧G∧租约；此时刻起 D_kill 已设） | 次数/费用账独立入账 | S5（WRK）/故障行 | 过 D_kill/D_total→SUP 必须 kill；窗口外 admit 被 DB 拒 |
| S5 | 停止与 WCC | 停止点（窗口剩余<门槛/终止信号/业务完成）→不再 admit→in-flight 表清空（WCC-1：全部到持久终态或确定 not_sent） | 递减至零（WCC-2 结构性阻止新发送） | 不变 | S6（WRK） | unknown=账面终态≠远端停止证明；WCC-1 未满足禁止 settle 发起 |
| S6 | 结算 | WRK settle(E,G,W_eff,C=ceil(t_settle发起−t0))（前置=WCC-1..4） | **提交即失去**（pending、G+1） | pending；R=0；S+=C；LSG=G；LSs=C；A 恢复 W_eff−C | S7（WRK 退出；单窗无新窗） | C>W_eff 拒绝不钳制；退款仅此路径；任何主体不得代结算 |
| S7 | 退出确认 | WRK 自行退出（有界）；SUP 级1 等待（主句柄，≤5000ms）+级2 树确认（待核 API 后实现）；关 Job；诊断（含 t_stop_req/确认/开销分列） | 无 | 不变 | 会话结束 | 级2 未实现期间只称"主进程退出+Job 句柄关闭"，不称"进程树终止确认" |
| F1 | 认领提交后响应丢失/上报前挂死 | 无上报至 D_report→SUP kill+级1/级2 确认 | 从未实际取得或已被终止 | 残留 running∧R=W_eff（会话已计数） | 下次会话 claim 折叠 或 cancel | 无人代结算；折叠只针对 running∧R>0 |
| F2 | 窗口挂死/超窗 | 过 D_kill（或 D_total）→TerminateJobObject+两级确认 | 被 kill 终止；在途远端请求不可撤销 | 残留同 F1 | 下次会话折叠（其启动门槛=本会话树终止确认）/cancel | 超窗部分不退款；overrun 只入诊断，不钳制 C 冒称无超额 |
| F3 | SUP 死亡 | OS 关闭 Job 最后私有句柄→KILL_ON_JOB_CLOSE 杀 WRK | 终止 | 残留同 F1 | 下次会话（门槛同 F2）/cancel；LAUNCHER 心跳按预算重启 | 无人代结算；不假设句柄外泄 |
| F4 | DB 阻塞 | admit→REJECTED(admission_unavailable) 不发送；settle 有界重试至 D_kill 仍败→WRK 死亡 | 无新增出站 | 残留同 F1→下次折叠 | 同 F1 | 不以 DB 墙钟延后 D_*；不用事务内异常回滚已提交的折叠关闭 |
| F5 | settle 提交响应丢失 | WRK 重试 settle→ALREADY_SETTLED（LSG=G∧LSs=C） | 已失（提交时点） | 已 pending∧R=0（持久事实） | S7 | 不按未结算折叠；跨会话更旧代次拒绝不改账（受限幂等，076 行5b 保留） |
| F6 | 取消（cancel_activity） | LED 单事务折叠 R 全额入 S、cancelled 终态、G+=1；WRK 下次 admit 被拒→跳过 settle 自行退出；SUP 两级确认收尾 | 立即失去（DB 级） | cancelled；R=0；S+=R；G+=1 | 无（终态） | 不退款；取消≠撤回远端；SUP 收尾不读账本 |
| F7 | 监督重启发现残留 | 折叠：任意时刻账面安全；**新会话启动**：门槛=旧树终止确认（F3 级2）+open_execution_session 预算 | 旧代次已被 G+1 失效 | 折叠后新代次 running | S2（新会话） | 旧树未确认终止→不启动新会话（正确性优先）；旧在途本地工作与新代次的并行被门槛排除 |

## 3. 手工事件轨迹（≤4，修订数值；方案级推演，非测试）

M=200；统一不使用 DB 墙钟计时（各角色 time.monotonic()，同机同源）。

**R1 正常单窗（C<W）**：open_session(#1)→claim(W=100)：S=0,R=100,A=100,G=1→ack→执行 20s（含停止排空，WCC-1 满足）→settle(E,1,100,20)：S=20,R=0,A=180,G=2→退出两级确认。免费 grace 规避：armed 前无资格；ack 前无首个 admit；排空计入 C；settle 后无资格且本地动作受 D_kill/D_total 封顶；跨恢复不重置（A=180 持久，会话计数持久）。

**R2 认领响应丢失→kill→折叠→两路径**（F5 修正数值）：claim 提交（R=100,G=1）响应丢失→D_report kill→残留折叠（会话#1 已计数）→会话#2 claim W'=100：路径A S=100,R=100,A=0（成功占满，非 None）→正常 settle(30)：S=130,R=0,A=70；路径B（A 窗又崩）→会话#3 claim：折叠 S=200,R=0，A=0→None+折叠关闭提交，终态 S=200,R=0,A=0。全程 S+R+A=200；无退款；无限零窗口会话被 max_sessions 封顶（前提：005 获批）。

**R3 挂死保守收费**：窗1 W=100 第 15s 挂死→D_kill=t0+100+grace 时 kill+级1 确认（级2 待核）→残留折叠 S+=100（下次会话，其门槛=本会话树确认）。真实墙钟≈100+grace+kw；账面恰 100；超窗部分（grace+kw+上报时延）**不可记账**（每窗账面封顶 W_eff；C>W_eff 被 settle 拒绝），只记 overrun 诊断——无法保证处如实声明为机制边界（裁决项 2），不钳制 C 冒称无超额。

**R4 settle 提交响应丢失→重启→旧重试不改新窗**（F5/T4 修正数值）：见 §1 F5 T4 修正段：新窗 S=20,R=80,A=100,G=3；旧 settle(E,1,100,20) 重试→ALREADY_SETTLED 账面不变；新窗先 settle（LSG=3）后旧请求→代次不匹配拒绝不改账。

## 4. 最小实施提案（修订）

**零变更（沿用首轮 §4.1）**：repository 既有方法签名与语义（claim/settle/cancel/admit/mark/record/recover 全部）、004 迁移、gateway/transport、pdf_import 两文件。首轮回撤"五列零变更足以支撑完整协议"表述：五列承载 T1/T2 的账面，T3 会话级开销的跨恢复封顶**需要新增持久字段**（下），两级树确认需要新增监督代码。

**拟新增/变更（相对首轮的修订）**：

| 项 | 内容 | 原→新 | 需用户裁决 |
|---|---|---|---|
| 005 候选迁移 | sessions_opened/max_sessions 两列+3 CHECK | 新增（首轮无） | **是**（主要模型变更） |
| repository.open_execution_session | 单事务原子递增+超限拒绝（LAUNCHER 调用契约，约 40 行） | 新增（首轮无） | 同上 |
| ActivitySpec.max_sessions | 新必填字段 | 新增 | 同上（调用方/夹具影响同 077 模式） |
| backend/app/worker/{__init__,job_session,session_supervisor,worker_main}.py | 单窗模式+ack 门+WCC in-flight 表+两级终止确认（级2 待核后实现）+发送门槛 | 修订首轮四文件设计（多窗→单窗、加 ack、加 WCC） | 否（模块内部） |
| claim 调用约定 | lease_seconds=window_seconds（WCC-3） | 新增约定，零代码 | 否（审计点） |

**撤回**：首轮裁决项 1 的"方案 A：接受无上界+启动器退避"作为推荐——退避上限不是重启次数上限、进程内计数不能跨恢复保存，均已在 F2 论证中否定；推荐方案改为持久会话预算。

## 5. 验证矩阵（修订；替身只能证协议调用次序，不能证真实 DB/OS 停止事实——每项标注证据类型）

| # | 真实新行为 | 可观察证据（类型） | 合成故障注入 |
|---|---|---|---|
| V1 | open_session 先于 armed 且预算封顶 | 替身 ledger 调用次序+超限拒绝（替身）；005 迁移/约束（真实 PG 定向，不重跑 079） | 替身 open_session 失败/超限 |
| V2 | armed 前认领不可达、ack 前无首个 admit | 替身 ledger/gateway 调用序断言（替身次序） | 替身 |
| V3 | WCC：in-flight 表空先于 settle、门槛阻止新发送 | 替身调用序+门槛边界用例（替身次序+静态审计） | 在途未终态时尝试 admit/settle |
| V4 | lease=window_seconds 约定与 WCC-3 覆盖边界 | claim 参数断言+满期后 admit 拒绝（替身次序；真实 PG 仅 005 变更需要时） | 窗口满期 inject admit |
| V5 | 正常单窗结算退款+退出两级确认 | DB 断言+级1 等待日志（替身 ledger+本机真实 spawn） | 无（正常路径） |
| V6 | 认领响应丢失→D_report kill→折叠两路径（R2 数值） | kill 确认+S/R/A 断言（替身+spawn） | 替身丢 claim 响应 |
| V7 | 窗口挂死→D_kill kill→折叠+overrun 诊断（R3） | kill 确认+overrun 事件+S+=W_eff 断言（spawn） | worker hang 模式 |
| V8 | settle 提交响应丢失→ALREADY_SETTLED 不改新窗（R4 数值） | S/R/A 逐行断言（替身） | 替身提交后丢响应 |
| V9 | 取消→admit 拒绝→WRK 自行退出→全额折叠无退款 | cancelled 断言+退出确认（替身+spawn） | 窗口中途 cancel |
| V10 | SUP 被杀→Job 关闭杀 WRK | WRK 进程退出观察+DB 残留（spawn） | taskkill SUP |
| V11 | 树终止确认（级2） | 探针+官方文档核对结论（待核事实关闭后设计用例） | Job 内多进程终止 |
| V12 | DB 阻塞→REJECTED 不发送→settle 重试失败→死亡→折叠 | gateway REJECTED+DB 残留断言（替身） | 替身 ledger 阻塞 |

- **独立增强审计（实现后必要，独立新会话）**：WCC 代码纪律（in-flight 表/门槛/lease 约定）、停止/退款权限边界（无 SUP/LAUNCHER（除 open_session）/API 路径写 running_* 或调 settle）、SUP 零账本 import 边界（设计选择验证）、两级终止确认实现与待核事实的一致性。
- 079 有效证据不重跑；真实 PG 仅补 005 变更及新接线定向需要。

## 6. 待用户裁决项（修订后；真正语义差异）

1. **持久会话预算（005+open_execution_session+ActivitySpec.max_sessions）**：批准→F2 闭合（T_wall 上界=max_sessions×(τ_total+kw)+M×常数，全部持久事实控制）；不批准→单一决定性缺口"跨恢复墙钟无不可重置上界"，NFR-003 时间维明示差距，不以降级方案冒充闭合。
2. **超窗 overrun 不入账**（维持首轮推荐+明示）：每窗账面封顶 W_eff，超窗只诊断；备选（C>W 超额记账）须改 settle"拒绝不钳制"合同+CHECK，不推荐。
3. **双挂死处置**：LAUNCHER 心跳检测"SUP 不动作"并按持久预算重启（承认两层监督链与 LAUNCHER 健康检查为新增监督责任）；三层同时不动作不覆盖（人工介入）。
4. **数值配置确认门**：τ_ready/τ_report/τ_total/grace/settle_margin/W/lease_seconds/max_sessions 缺省拒绝启动。

## 7. 未实施/未验证/待核（修正轮01）

- 本轮全部为设计级纠正；未实施任何代码/DDL/接口变更；未运行任何测试/静态检查/PG/Docker/应用；§3 为手工推演非程序测试。
- 待核事实（单一）：Windows Job 对象 signaled/NumberOfActiveProcesses 归零语义（F3，实现卡核对+探针）。首轮待核点 1/2/3（monotonic 底层时钟与睡眠、stdout 通道有界性、ActiveProcessLimit 取值）保留。
- WRK 诚实性为账本既有信任假设（非新增）；WCC 实现正确性由实现后独立增强审计承载，本轮不能宣称已证明。
- 077—079 已验证行为按原证据范围引用，未重测；首轮归档原文与首轮历史见下；本卡不填编排最终验收，不宣告 M-1/STEP-008 完成。

## 8. 修正轮01 读取范围与身份

- 身份：沿 081 原 Work Buddy 增强执行窗口（实际 GLM-5.3，如实登记）；本轮定向设计纠正，非独立审计。
- 读取：首轮结果全文（本窗口自写）；以下本窗口首轮已读且 hash 复算未变、未重复展开——TASK-076-work-decision.md、LATER_REQUIREMENTS.MD（NFR-003/SEC-002）、repository.py（claim/settle/admit/mark，hash 045a3cf8…2534 无漂移）、_windows_job.py（终止/等待段，hash 797f445f…36425 无漂移）。未读其他完整历史报告（卡面豁免）。
- 证据：Ndocu/evidence/task-081/revision-01/drift-check.md（漂移核对+归档核对）；首轮 read-scope.md/read-hashes.txt 继续有效。
- 写入：本结果文件 + revision-01/drift-check.md。未改源码/迁移/正式 docu/旧证据/公共库/Git。

---
---

# 首轮历史（2026-09-24 上午；已被修正轮01 部分取代）

> 编排裁定：首轮设计不通过实施门槛（F1—F6 见上文）；有限截止、失败保守处理、已提交事实不撤销等段落保留，未列修正处以本部分为准继续有效；已撤回表述以修正轮01 为准（SWP-081"已收敛"、"五列零变更足以支撑完整协议"、裁决项 1 方案 A 推荐、"SUP 不触账本是 SEC-002 要求"）。原任务卡归档：Ndocu/archives/TASK-081-before-revision01-20260924.md。

# TASK-081 / R-075 结果：时间窗口监督与停止结算协议收敛（设计与实施提案）【首轮原文】

- TASK-081 / R-075；STEP-008 局部；父 TASK-076；关联已完成 077/078/079、NFR-002/003、SEC-002、FLOW-005、DATA-007。
- 基线：需求 v1.1、架构 v0.34、执行状态 v1.36；Git 基础提交 45951501d2741630a229762d6b2d3f4b34d7f702，本卡零代码改动，无差异产生。
- 执行者：Work Buddy 新窗口（系统标识 GLM-5.3，增强执行）。076 原方案窗口（Codex Sol）不可续；未沿用 080 普通 Git 窗口承接本设计。
- 状态：**只读设计交付**。未实施任何代码/DDL/接口变更；未运行任何测试、compile、PG、Docker、应用、模型、网络；未读取私有配置或凭据。本卡不是独立审计，不填写编排最终验收，不宣告 M-1 或 STEP-008 完成。
- 一句话结论【已由修正轮01 撤回】：已收敛为一个 Windows 内部单窗口监督协议（下称 SWP-081）：出站资格唯一由账本窗口承载、墙钟封顶唯一由监督者单调截止承载、退款唯一由存活 worker 的 settle 提交承载；五列账本零变更即可支撑该协议，决定性缺口为"双挂死无第三方强制终止"与"跨会话墙钟无全局上界"，各配最小替代并列为裁决项。

---

## 1. 时间定义、可观察不变量与故障模型（交付 1）【首轮】

### 1.1 角色与记号

| 记号 | 角色 | 边界 |
|---|---|---|
| LAUNCHER | 受信启动器（未来接线卡承载，本卡不接线） | 决定会话启动/重启策略；不触账本 |
| SUP | 监督者（拟新增模块进程内角色，持有 Job 私有句柄） | 只管进程树终止与诊断；**不 import activities、不触账本**（SEC-002）【注：SEC-002 归属表述已由修正轮01 F6 纠正为方案选择】 |
| WRK | worker（拟新增模块入口进程） | 唯一账本调用方；唯一结算主体 |
| LED | 仓储（backend/app/activities/repository.py 既有） | 唯一资格/账面权威 |
| Job | Windows Job Object（KILL_ON_JOB_CLOSE + 进程数/内存限制，复用 _windows_job.py L115-130 模式） | 仅含本会话 WRK 进程树；句柄私有不继承 |

单调时钟：SUP 与 WRK 同机各用 Python `time.monotonic()`（同一时钟源，跨进程可比性由同源承载；底层时钟与睡眠行为见待核点 1）。**禁止以 DB 墙钟（now/CURRENT_TIMESTAMP）参与任何单调截止或耗时测量**；DB 墙钟仅用于既有冲突判定（lease/deadline，claim L343-346）。

截止（全部单调、固化后**不可后移**）：
- `D_ready = t_resume + τ_ready`（t_resume=SUP 恢复 WRK 主线程时读数；WRK 未 ready 即 kill）。
- `D_report = t_armed + τ_report`（t_armed=SUP 下发 armed 时读数；覆盖自检+单次 claim 事务+上报通道）。
- `D_total = t_resume + τ_total`（**锚点为进程恢复时点而非 armed**，覆盖含 armed 前全部进程存活期；不可延后总截止）。
- `D_kill = t0 + W_eff + grace`（收到上报时一次性固化；t0=WRK 在 claim 响应后立即取得的单调读数；**W_eff 取自 ActivityLease.window_seconds（实际预扣），不是请求 W**；grace 为唯一窗口级宽限）。t_commit（claim 事务提交）≤ t0，客户端不可精确取得，不用于账面。

τ_ready/τ_report/τ_total/grace/settle_margin/W 请求/lease_seconds 全部留配置确认门：缺失或非法→拒绝启动会话（失败关闭，076 剩余问题 2 口径）。

### 1.2 受控区间与各段计入口径

受控区间 = [t_resume, 进程树退出确认（或 Job 句柄关闭兜底）]。段划分与计入：

| 段 | 区间 | 是否计入 C（账面） | 墙钟封顶 |
|---|---|---|---|
| 启动/自检/armed | t_resume → t_armed | 否 | D_ready/D_total |
| 认领 | claim 事务（提交=账面窗口名义起点 t_commit）→ 响应送达 WRK（t0） | 否（t_commit→t0 差额未计 C，由 grace 宽松量覆盖并记录，不宣称 C 从提交起精确） | D_report；claim 事务自身有界（connect 3s / lock 2s / statement 3s，repository `_transaction` 默认） |
| 窗口执行+停止排空 | t0 → settle 发起 | **全部计入**：C = ceil(t_settle发起 − t0)；停止请求、排空（已 admit 操作到终态/unknown）都发生在 settle 发起之前，因此**排空耗时在 C 内**（回应 076 裁定"C 在 settle 发起时计算不包含其后实际执行"：其后仅剩结算事务与退出，见下两行） | D_kill/D_total |
| 结算事务 | settle 发起 → 提交 | 否（C 已定格）；由发送门槛（窗口剩余 ≥ request_timeout+settle_margin）保证其在 W_eff 内完成的空间，超时失败走 F4 | D_kill/D_total |
| settle 提交后 → 退出确认 | 提交 → 进程树退出 | 否，且**无出站资格**（提交即 pending、G+1） | D_kill（该窗口）/D_total |
| 监督开销 | kill 等待、清理、Job 关闭 | 否（不入 M） | kill 等待有界（≤5000ms 模式，_windows_job.py L159-161） |

监督开销与逐窗实际墙钟超出账面部分（上报时延+grace+kill 等待）**分开记录为诊断事件码+实际时长**，由 D_total 封顶总量，不并入 M，不宣称钳制后无超额（076 裁定口径保留）。

### 1.3 可观察不变量【INV3/INV4/INV5/INV6 已由修正轮01 修订，见修正轮 §1；INV1/INV2 保留】

- **INV1（资格唯一来源）**：出站执行许可 = LED 中 `status='running' ∧ executor_id=E ∧ generation=G ∧ 租约有效`（`_activity_allows`，repository L691-707）。窗口外、代次外任何 admit 必被拒；armed 前、settle 后、cancel 后均无资格。
- **INV2（账面守恒）**：S+R+A=M 恒成立（004 CHECK + 079 真实 PG 已验证）；A=0 时 claim 返回 None，无新窗口。
- INV3（退款唯一入口）【已被修正轮01 F1 的 WCC 修订取代】。
- INV4（单会话墙钟上界）【修正轮01 F4 条件化：前提=SUP 获得调度执行或其死亡触发 Job 关闭】。
- INV5（每窗口真实墙钟上界）【修正轮01 F4 条件化，同上】。
- INV6（停止证明唯一主体）【已被修正轮01 F3 两级终止确认取代】。

### 1.4 故障模型（明示覆盖与不覆盖）【修正轮01 F6 已修订双挂死处置与监督链表述】

覆盖：
1. SUP 被杀/崩溃 → OS 关闭 Job 最后私有句柄 → KILL_ON_JOB_CLOSE 终止 WRK（信任链=句柄私有性，设计禁令承载）。
2. WRK 崩溃/挂死/空转 → D_ready/D_report/D_kill/D_total 逐级 kill；Job 内存/进程数限制兜底空转型。
3. DB 阻塞/不可用 → admit 返回 REJECTED(admission_unavailable) 不发送；settle 有界重试至 D_kill 仍败 → WRK 死亡 → 残留折叠（保守收场）。
4. 系统休眠/调度暂停 → 睡眠期无 CPU 执行发生；时钟口径差异只造成记账偏差（多计=保守方向，少计部分与无执行期对应），不做绝对声明（待核点 1）。
5. WRK 失联（上报通道关闭）→ SUP 按 D_report/D_total kill，Job 兜底。

**不覆盖（决定性缺口，见 §6）**：SUP 存活但不动作 ∧ WRK 阻塞型挂死（双挂死）——当前故障模型内无第三方能在有限时间内强制终止，不承诺任意双挂死下绝对实时终止，不为此叠加看门层。【修正轮01 F6：LAUNCHER 心跳可检测该场景并按持久预算重启，把暴露窗口降为检测周期+重启时长；三层同时不动作不覆盖】

### 1.5 远端不可撤销边界【保留，修正轮01 F1 引用】

`mark_dispatch_started` 提交后，请求可能已在途或已被远端处理；取消、超时、kill、代次失效**均不能撤销已出站请求**。本地能做的只有：终止自有进程树（INV6→修正轮 F3 两级确认）+ 保守记账（旧代次 record 仅 UNKNOWN 诊断，repository L890-891；transport 无重试，transport.py L41-92）。gateway 的取消协程（asyncio.CancelledError → best-effort unknown，gateway.py L149-151）**不是网络终止证明**。取消/超时的用户可见表述必须如实（NFR-002：远端可能继续时如实显示）。

### 1.6 需求-机制不一致（明示，不悄悄降级）【NFR-003 跨恢复行已由修正轮01 F2 取代】

| 要求 | 当前机制可达 | 不一致点（如实） |
|---|---|---|
| NFR-003"达限实际停止本地自有工作"（时间维） | 账面达限（A=0）⇒ 无新出站资格 + 残留全额折叠；单会话内 SUP 截止提供有界终止 | 双挂死时无实时终止（§6 缺口）；"实际停止"只能承诺到"有监督动作时有界终止" |
| NFR-003"跨恢复不重置"（时间维）【修正轮01 F2 取代：闭合以持久会话预算批准为条件】 | 账面 M 跨恢复累计（079 已验证行为沿用，不重测） | **真实墙钟无跨会话总量上界**：每会话 τ_total 独立，会话数由 LAUNCHER 重启策略决定（裁决项 1）。不把账面 M 冒充墙钟保证 |
| SEC-002"停止只处理自有工作" | Job 仅含本会话 WRK 进程树 | 无不一致【修正轮01 F6：SUP 零账本为方案选择，非本条要求】 |
| NFR-003"实际调用含隐藏重试计入" | transport 无重试；每出站经 admit 计数 | 无不一致 |

---

## 2. 唯一推荐协议：时序与状态转换表（交付 2）【已被修正轮01 §2 单窗修订版整体取代】

<details>
<summary>首轮时序表（历史保留，展开）</summary>

| 步 | 事件/条件 | 所有者动作 | 出站执行许可 | 持久态（事务提交后） | 允许下一动作（所有者） | 禁止 |
|---|---|---|---|---|---|---|
| S0 | 会话启动 | LAUNCHER→SUP；SUP 建 Job，CREATE_SUSPENDED 创建 WRK→Assign→Resume（_windows_job.py L132-153 模式）；记 t_resume | 无 | 不读不写 | S1（WRK） | SUP 不触 LED；armed 前 WRK 认领代码不可达（入口门，见 S1） |
| S1 | ready→armed | WRK 自检（IsProcessInJob 隶属，仅排错配不作权威证明；LED 只读健康）→发 ready；SUP 固化 D_ready/D_report/D_total 并下发 armed | 无 | 只读 | S2（WRK） | D_* 固化后不可后移；τ 未配置→SUP 拒绝启动会话（WRK 未获 armed 永不 claim） |
| S2 | 认领 | WRK `claim_lease(E, W, lease_seconds, window_seconds)`；LED 原子完成：过期残留折叠（S+=R_old、R=0）→ 预扣 W_eff=min(W, A≥1) | 无（claim 非出站） | running；R=W_eff；G+=1；exec=E；lease 设置 | S3 上报（WRK） | 不得抢占有效租约（LED 冲突）；A≤0→LED 提交折叠关闭并返回 None（不回滚、不虚称未关闭）→会话收尾 |
| S3 | 上报 | WRK 上报 (W_eff=lease.window_seconds, t0)；SUP 固化 D_kill=t0+W_eff+grace（一次性，重复上报拒绝） | 窗口开启（首个 admit 待上报完成） | 不变 | S4（WRK） | **上报前禁止首个 admit**（WRK 代码纪律，非 DB 强制；D_report 兜底 kill）【修正轮01 F4：已升级为 ack 门硬规则】 |
| S4 | 窗口执行 | WRK 循环 admit→mark_dispatch→出站（事务外网络）→record；发送门槛：窗口剩余（按 WRK 单调自查）≥ request_timeout+settle_margin；看门线程记 t_stop_req | **有**（INV1） | 不变 | S5（WRK）/ F1-F4 故障 | 过 D_kill 或 D_total → SUP 必须 kill；窗口外 admit 被 LED 拒绝 |
| S5 | 停止与排空 | WRK 不再 admit；已 admit 操作全部到终态或尽力记 unknown（有界：门槛保证在途请求窗口内超时收敛） | 递减至零 | 不变 | S6（WRK） | unknown 标记≠底层停止证明，仅诊断（076 裁定保留）【修正轮01 F1：已由 WCC-1..4 取代"尽力 unknown 即可结算"】 |
| S6 | 结算 | WRK `settle_execution_window(E, G, W_eff, C)`，C=ceil(t_settle发起−t0)（含 S5 排空） | **提交即失去**（pending、G+=1） | pending；R=0；S+=C；LSG=G；LSs=C；A 恢复 W_eff−C | S7 退出 或 回 S2 新窗口（D_total 不变，D_kill 重设）【修正轮01 F4：多窗已否决】 | C>W_eff 拒绝不钳制；退款仅此步、仅存活 WRK；不得代结算 |
| S7 | 退出确认 | WRK 自行退出（有界）；SUP 对主句柄 WaitForSingleObject(≤5000ms) 确认，关 Job | 无 | 不变 | 会话结束（SUP） | SUP 不代结算、不代退款、不写任何账面【修正轮01 F3：两级确认修订】 |
| F1-F7 | （故障行） | — | — | — | — | 【整体由修正轮01 §2 取代：F7 新增"新会话启动=旧树终止确认"门槛】 |

</details>

## 3. 手工事件轨迹（首轮）【T2/T4 数值错误已由修正轮01 §1 F5 修正；T1/T3 结论沿用、以修正轮 R1/R3 为准】

<details>
<summary>首轮轨迹（历史保留，展开；T2 步4 与 T4 表格数值有误，以修正轮01 为准）</summary>

统一口径：M=200；请求 W=100；gen 初始 0。

T1 正常小于 W 停止：claim W_eff=100→执行 20s→settle(E,1,100,20)：S=20,R=0,A=180,G=2→退出确认。免费 grace 规避与跨窗口不重置论证见修正轮 R1（沿用）。

T2 认领响应丢失：claim 提交（R=100,G=1）响应丢失→D_report kill→残留折叠→下次 claim 两路径。【步4"S=100,R=0,A=0"错误；正确两路径见修正轮01 §1 F5 与 R2】

T3 停止或监督故障保守收费：挂死→D_kill kill→折叠 S+=100；SUP 被杀→Job 关→折叠同。退款为零、无免费账面时间；超窗部分不可记账只入 overrun 诊断（沿用，修正轮 R3）。

T4 结算提交成功后重启：settle 提交（S=20,R=0,LSG=1,LSs=20）响应丢失→双死→新会话 claim 普通认领（不折叠）→旧 settle 重试 ALREADY_SETTLED 不改账。【表格"R=0/…"数值含糊；具体值见修正轮01 §1 F5 T4 与 R4】

</details>

## 4. 最小实施提案（首轮）【已由修正轮01 §4 取代；以下保留原始记录】

<details>
<summary>首轮提案（历史保留，展开）</summary>

零变更：repository 全部方法、004、gateway/transport、pdf_import 两文件（该结论中"五列零变更足以支撑该协议"的表述已由修正轮01 撤回）。

拟新增：backend/app/worker/{__init__,job_session,session_supervisor,worker_main}.py 四文件。job_session：start/arm/accept_report/poll/terminate_and_confirm/close；session_supervisor：会话循环+脱敏诊断；worker_main：armed 门→自检→claim→上报→窗口循环（gateway+PostgresAdmissionLedger）→排空→settle→退出。

时间定义修订（相对 076 §C）：D_total 锚 t_resume；D_kill 基于 W_eff；上报前禁首 admit。裁决项：跨会话墙钟无全局上界（方案 A 接受+启动器退避【已撤回推荐】）；超窗 overrun 不入账；双挂死缺口；数值配置确认门。

验证矩阵 V1-V10（首轮版）+独立增强审计（停止/退款权限边界）+一次有界实现/验证批次建议。

</details>

## 5. 下一实现卡最小验证矩阵（首轮）【已由修正轮01 §5 取代，证据类型标注为修正轮新增】

首轮 V1-V10 清单见修正轮01 §5 对照（V2/V4/V6/V8/V10 与首轮同名项对应并修订；V1/V3/V11/V12 为修正轮新增）。

## 6. 决定性缺口与最小替代（首轮）【已由修正轮01 §1 F2/F3/F6 修订】

双挂死缺口与最小替代（受信启动器健康检查+有限重启策略）：保留缺口定位；修正轮01 F2/F6 修订——重启次数必须由持久会话预算封顶（不可重置事实），LAUNCHER 健康检查被承认为新增监督责任（两层监督链），"接受无上界"不再作为推荐正确性方案。配套明示（跨会话墙钟无全局上界、超窗 overrun 不可记账）：前者已改为条件闭合（持久会话预算候选）；后者维持明示边界（裁决项 2）。

## 7. 未验证风险与待核点（首轮）

1. Python `time.monotonic()` 底层时钟（Windows 上 GetTickCount64 vs QPC）与睡眠期行为：实现卡一次静态+最小探针确认。同机同源→跨进程可比性不受影响；差异只影响睡眠期计费方向（多计=保守）。【保留】
2. stdout 单行 JSON 通道在 CREATE_NO_WINDOW+管道下的缓冲与时延上界：实现卡确认 flush 纪律与有界性。【保留】
3. Job ActiveProcessLimit 取值：venv python.exe 转发器假设沿 _windows_job.py L121-122；活动 worker 若需更多子进程须复核限额。【保留】
4. WRK 纪律位（上报前禁 admit、margin 门槛、排空到终态）为代码纪律非 DB 强制——已列为独立审计覆盖点。【修正轮01 F1：WCC-2/WCC-3 已将其中两项升级为结构性/DB 级】
5. 本卡全部为设计：§3 为手工推演非程序测试；未运行任何测试/静态检查/PG/Docker/应用；077-079 已验证行为按原证据范围引用，未重测。【保留】
6. API 语义不确定且无本地原始资料佐证之处：无（本卡所需 API 全部来自实读源码，hash 已冻结核对）。【修正轮01 F3：新增单一待核 Windows API 事实，首轮该表述限定为"仓储/传输 API"，Job 树确认 API 不在其中】

## 8. 实际读取范围（首轮）

- 规则：根 AGENTS.md（注入上下文）+ 公共 docu/AGENTS.MD。
- 项目文件 12 份：TASK-076-work-decision.md、TASK-076-result.md（监督部分及未闭合项，未继承其被否定结论）、LATER_REQUIREMENTS.MD（NFR-002/003/SEC-002）、PROJECT_ARCHITECTURE.MD（FLOW-005/DATA-007/Windows 监督与部署边界）、PROJECT_EXECUTE_STATE.MD（顶部最新裁定）、activities/repository.py、pdf_import/_windows_job.py、pdf_import/supervisor.py、capabilities/gateway.py、capabilities/transport.py、migrations/004_activities_time_budget.sql、TASK-079-result.md。
- Hash 清单（14 项，含入口）：`Ndocu/evidence/task-081/read-hashes.txt`。冻结核对：repository.py=045a3cf8b1c81d7a1336c3bd2e90e891e4e53934027c9fea9727fafde7202534 ✓、004=8f04f57c743c260f5081e0c6f232860301b30c7b03fef69498d7c0704c0a97cc ✓，无漂移。072/074 恢复证据未引用（无直接依赖），未重审。
- 写入文件：首轮结果 + `Ndocu/evidence/task-081/read-scope.md`、`read-hashes.txt`、`make_read_hashes.py`（清单生成脚本）。所有源码、迁移、正式 docu、旧证据与 Git 只读。

## 9. 停止声明（首轮）

已达到本卡唯一成果目标；达到目标即停，未做全仓重复研究，未实际执行任何验证。不填写编排最终验收，不宣告 M-1 或 STEP-008 完成；实现后的独立增强审计（停止/退款权限边界）保留。【修正轮01 同口径：一次有限设计纠正已完成，未闭合项（F2 裁决、F3 待核事实）已明示，不启动新一轮自行试错】
