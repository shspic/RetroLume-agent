# TASK-060 058审计事实更正与时钟/恢复门槛定向诊断 — 结果

任务：TASK-060 / R-054；类型：只读诊断（更正与方案，不是新的独立安全审计）；父 TASK-058；关联 TASK-046/051/055/056、NFR-002/003、SEC-002、FLOW-005；STEP-006/008 局部。
日期：2026-09-20（Asia/Shanghai）。项目根：D:/shspic/project_NO3_RetroLume-agent。
基线：LATER_REQUIREMENTS.MD v1.1；PROJECT_ARCHITECTURE.MD v0.16。
状态：本卡诊断完成（一次源码/证据/方案一致性核对，未运行任何测试）；Astra 验收结论留空。

## 1. 结论摘要

1. 058 的"有限范围通过、无阻塞"在划清边界后仍成立；锁序、唯一操作、预算/回滚、终态纪律四类证据不推翻。四项发现中：L-2 不成立（事实前提错误），L-1、L-3 保持成立，M-1 缺口真实但 058 给出的最小修正（换成数据库时间）不充分，不能照抄进实现卡。
2. 关键时钟事实：PostgreSQL 的 CURRENT_TIMESTAMP/now() 固定于事务开始且仍是墙钟；clock_timestamp 同为墙钟仅粒度不同。"统一时钟源"与"单调期限"是两个机制，任何单一时钟替换（datetime.now→DB 时间、→clock_timestamp、→monotonic）都不能单独满足 FLOW-005 的回拨/锁等待/跨重启三条要求。
3. G-1 最小方案：只读列出旧代次未决操作 + 按代次差保守收敛为 unknown；不自动退款、不自动重发、不补空壳方法名。
4. 建议下一实现卡同批：M-1 时钟同源化（repository.py）+ L-1（contracts.py）+ L-3（gateway.py）；G-1 并入 worker 监督器卡；002 用户库迁移/应用接线/时钟与重启反例归真实组合运行卡。

## 2. 范围与独立性声明

- 全程只读：未运行测试、Docker、应用、模型、安装；未读真实配置；未修改产品、迁移、锁、正式 docu、旧审计报告；未 Git 提交。
- 未读取 TASK-059 的变动脚本（与 059 并行约束遵守）。
- 读取范围明细：Ndocu/evidence/task-060/read-scope.md。
- 本卡不是独立审计，不重复 058 的完整覆盖，只做事实更正与定向方案。

## 3. 事实更正表（058 → 实际）

| # | 058 原表述 | 实际证据（本卡只读核对） | 裁定 | 影响 |
| --- | --- | --- | --- | --- |
| F-1 | L-2：gateway 用紧凑序列化取 len，httpx 用默认 ", "/" 分隔，request_bytes 有系统性小偏差 | backend/.venv/Lib/site-packages/httpx/_content.py L176-183：encode_json 使用 ensure_ascii=False、separators=(",", ":")、allow_nan=False；transport.py L66 以 json=payload 发送，走 encode_json；gateway.py L94 计算参数与之一字不差。同一 payload dict 两次 json.dumps（同参数、dict 保序、float repr 确定）字节一致 | 不成立 | request_bytes 与实际发送体一致；不改 transport、不扩大 request_bytes 预留、不为不存在的问题做保守放大 |
| F-2 | §8.1 简写"002 未落库"（正文 §6.2 已写"未对任何用户库执行"） | 001/002 已在专用合成 PG（容器 retrolume_task_048_synthetic，055 stdout L14-15 可见 PG 17.11 与库名；051 执行七类/01-08 测试即依赖该库已建表）执行并有 051/055 原始运行证据；002 未在用户库执行、未接入应用启动流程（051 结果明示） | 部分成立（表述需更正） | 准确口径："001/002 已在专用合成库迁移并验证，未在用户库迁移、尚未接入真实应用"。文档状态不得据此写成"已落库/已接入" |
| F-3 | L-1：CallContext 与账本实现的字段格式约束未文档化 | contracts.py L124-128 仅限长度 1-128 无字符集约束；repository.py L356-362 activity_id 必须 UUID，L134/L364-365 operation_id/executor_id 必须匹配 ^[A-Za-z0-9._:/-]+$；046 离线测试用 "activity-1"（非 UUID）通过，因其走离线假账本 | 成立（保持） | 字符集符合不等于满足完整 ID 契约；046 离线证据不能延伸为"ID 契约已验证"。修法沿 058 建议：CallContext 加同构 pattern，或拒绝时返回可辨原因 |
| F-4 | M-1 最小修正："把期限/租约比较改为数据库时间（CURRENT_TIMESTAMP 或 SELECT now()）" | PG CURRENT_TIMESTAMP/now() 固定于事务开始、仍是墙钟；clock_timestamp 亦为墙钟；DB 时钟同样受 NTP 跳变影响。仅换时钟源不能证明回拨不延长剩余时间、锁等待后过期、跨重启不延长 | 部分成立（缺口真实、方案不充分） | 换 DB 时钟是合理第一步（消除应用进程时钟单点、写读同源），但不得单独把"换成数据库时间"当作 M-1 修复完成的证据；完整方案见 §4 |
| F-5 | （隐含混用）"统一时钟源"与"单调期限" | FLOW-005 L124 并列要求三件事：系统时钟回拨不得增加剩余时间；活跃进程用单调时钟监督；跨重启以持久预算/截止保守恢复 | 更正 | 三者是不同层次的机制，须组合实现（§4），不得在文档或实现卡中互相替代 |

### 3.1 标准1—4 中哪些结论受时钟缺口限制

- 标准1（锁序与边界）：锁顺序、代次递增、唯一占用的结论不变；其中"租约/期限有效性判定正确"的子结论适用边界缩小为"未覆盖主机时钟异常"。
- 标准2（限额、唯一 operation、短事务、回滚）：判定依据是 DB 内计数与事务约束，与时钟无关，结论不变。
- 标准3（终态纪律）：状态机、幂等、不可覆盖、未知保留预留的结论不变；"失效或过期执行只能登记 unknown"中的"过期"判定（recoverable，L328-334）受时钟异常影响。
- 标准4（契约吻合）：固定 URL、白名单、无隐藏重试、超时覆盖等不变；"总期限"断言（deadline_at 比较）在时钟回拨场景不成立。
- 不否认：055 七类（test_02—08）与 051 test_01 的锁序/唯一操作/预算/回滚证据仍然有效；O-1/O-2/O-3 观察不变。

## 4. M-1 推荐最小方案（供 Astra 形成实现卡；本卡不实施）

### 4.1 四层区分（FLOW-005 对应）

1. 活动持久剩余时间（跨重启权威）：deadline_at 已持久化。FLOW-005 还要求"执行时间累计"分别持久化，当前未实现——只列影响：若补齐需新增字段（如 accumulated_running_seconds、last_resume_at）并与活动状态机联动，属数据模型范围变化，交 Astra 裁定；当前由绝对截止 + 租约覆盖，不构成本卡前置。
2. 单次运行/租约：lease_expires_at 持久化，claim_lease 一次一片（1—3600s），封顶 deadline。
3. 进程内单调监督：worker 活跃期间用 time.monotonic() 从领取租约时刻起倒计时监督剩余窗口；单调时钟不受墙钟跳变影响。Windows Selector 循环不支持 asyncio 子进程（055 结论），监督逻辑保持在同步受监督子进程边界内。
4. 跨重启恢复：进程内单调时钟不可跨进程延续——重启后不得凭任何内存时钟认为旧租约仍有效；重新 claim_lease 取新代次；旧代次未决操作按 §5 收敛；无法可靠判断时失败关闭。

### 4.2 最小代码改动（repository.py 内，不改公开接口、不加字段）

- a) 写读同源：claim_lease 中 lease_expires_at 改由事务内 DB 时间计算（先 SELECT now() 取得 db_now，写 least(deadline_at, db_now + lease)，比较也用同一 db_now），消除"应用时钟写、应用时钟读"的双进程时钟混用（当前 L280 写、L277/L397/L509 读均用 datetime.now）。
- b) 判定下沉：_activity_allows、_operation_is_current 的租约/期限比较改为使用同事务 DB 时钟值（SQL 内比较或传入 db_now），不再用 datetime.now（L272/L328/L416/L501 共 5 处）。
- c) 失败关闭（行为保持）：DB 不可用 → AdmissionUnavailable 不发送（现状）；重启后未重新领租约 → 不准入；无法判断是否过期 → 按未决操作保守记 unknown，不得推断"未发出"而重发。
- d) 锁等待后判定：admit/mark 获取行锁后基于同事务时钟值重新判定（逻辑保留，仅时钟值来源同源化）；lock_timeout（2s）超时即 AdmissionUnavailable，保持不变。等待时间自然计入判定，等待期间租约到期即拒绝。

### 4.3 三个场景的明确回答

- 锁等待后判定：判定使用锁获取后的同事务 DB 时钟值，等待计入窗口；到期即拒。
- 主机/DB 回拨或前跳：活跃进程内由单调时钟倒计时，回拨不延长本地监督窗口；持久判定以 deadline/lease 与 DB 时间比较，已写入的 lease_expires_at 不因回拨变化。残余风险：若 DB 墙钟回拨发生在"写入 lease 之后、判定之前"，该次比较窗口被拉长，上限受单租约 ≤3600s 与 deadline 绝对封顶约束。彻底消除需单调持久时钟（新服务或新字段），本卡不建议引入，未获授权不扩范围。
- 重启后无法可靠判断：失败关闭——不恢复旧租约、不准入旧代次；旧代次未决操作只能保守记 unknown（§5），业务重试必须形成新操作并重新检查剩余额度（FLOW-005）。

不引入新时间服务、不放宽原标准；除 §4.1 第 1 项仅列影响的累计字段外无数据/接口变化。

## 5. G-1 未决操作发现与收敛（最小方案）

- 发现什么：活动内 state IN ('reserved','dispatched') 的操作，重点是 execution_generation 低于当前活动 execution_generation 的旧代次操作（新租约领取后它们既不能被 recover_unknown 收敛，也无读取方；002 的 activity_operations_recovery 部分索引 L84-86 已建但无人使用）。
- 最小接口：新增只读方法 list_unresolved_operations(activity_id)，复用该索引，返回 operation_id、admission_id、executor_id、execution_generation、scope_revision、reserved_at、dispatch_started_at。必须带契约实现与查询，不得只补方法名。
- 何时恢复/收敛职责：worker 监督器（G-2 卡）在活动取消、租约过期、期限到达或进程重启后调用；顺序为"先列出 → 保守收敛 → 再开始新动作"（对应 FLOW-005"恢复后未知项先对账"）。
- 避免新租约遮蔽：收敛条件 = 操作 execution_generation < 当前活动 execution_generation，或活动已取消/已过期限/无有效租约（保持 recover_unknown 现有 recoverable 语义）；当前代次仍持有效租约的操作不得动。这样旧代次操作以代次差被发现，不被"新租约有效"挡住。
- 幂等边界：收敛即置 state='unknown'（终态，重复收敛 no-op）；不自动退款（全库无减少 cost_reserved_microunits 的路径，保持）；不自动重发；重发必须形成新操作并重新检查剩余额度。持原 permit 的执行者仍可按 L587-589 自行记 unknown，两条路径结果一致。

## 6. G-2～G-6 映射与真正放行时机

| 门槛 | 归属 STEP/卡 | 真正放行时机 |
| --- | --- | --- |
| G-2 worker 监督器（实际终止自有执行单元） | STEP-008 监督器实现卡（G-1 随同卡） | 真实 worker 开始执行任何活动之前 |
| G-3 业务提交（预留→发送→提交成功闭环、可重放持久结果） | STEP-008 业务提交卡；FR-010 复测/路径更新依赖它 | 任何"提交成功"闭环宣称完成之前 |
| G-4 scope_revision 更新路径 | 来源/范围管理卡（FLOW-005 范围修订） | 范围新增/移除功能实现之前；当前"不匹配即拒"的既有验证不受影响 |
| G-5 工具/步骤独立计数 | 引入自动工具往返时重评 | 不是当前任何卡的前置（网关不自动循环工具，每次续接是新 operation 计入 max_requests） |
| G-6 可观测性（脱敏日志、状态转换记录） | 真实 worker 接入卡 | 应用接入账本/worker 之前补齐；不阻塞资料/PDF 离线工作 |

以上均不构成 STEP-004/005（资料/PDF 离线线）的前置。STEP-006 剩余前置：L-1/L-3（可同批修复）与真实供应商返回兼容验证（需授权的真实调用卡，非本卡范围）。

## 7. 下一实现卡建议（最小文件范围、验证清单、上限）

同批可做（一张实现卡，建议强档 C/Sol，涉时钟与锁语义）：

- backend/app/activities/repository.py：M-1 时钟同源化（§4.2 a/b/d，5 处 datetime.now 收敛为事务内 DB 时钟值）。
- backend/app/capabilities/contracts.py：CallContext 补 activity_id UUID 语义与 operation_id/executor_id 字符集约束或可辨拒绝原因（L-1）。
- backend/app/capabilities/gateway.py：意外异常独立 error_code（如 internal_error）+ 脱敏诊断（L-3，保持不发送与 fail-closed）。
- 对应测试文件的定向补充（backend/tests/test_activity_ledger.py、test_capabilities.py）。
- G-1 的 list_unresolved_operations 可选同卡，或随监督器卡（Astra 定）。

后续单独处理（不并入上卡）：G-1 若不同批则归监督器卡；002 用户库迁移 + 应用接线 + 真实组合运行卡（含时钟异常与重启反例）；执行时间累计持久化（范围变化待裁定）。

验证清单（写入实现卡）：

1. 改动前后源码 hash 记录（沿 058 证据纪律）。
2. 静态检查 + 离线契约测试（L-1/L-3 无 PG 依赖可离线验证）。
3. M-1 判定路径的定向反例须在下次获授权的真实 PG 运行卡执行；不得以"已替换 datetime.now"或静态 SQL 断言充当跨重启时钟行为证据；跨重启只能以实际重启反例证明。
4. 已通过七类（055）与 051 test_01 不单独重跑；但 M-1 改动触及 admit/claim_lease/record_outcome 判定路径，下次运行卡应一并回归受影响用例（属"相关变化使受影响证据失效"，不是重复放心检查）。

投入上限：单会话一次完成；两次有据修正仍失败即停止交回 Astra。

L-1/L-3 处理归属：两者均可与 M-1 同批（低风险、离线可验）；无必须拆分的理由。

## 8. 未验证与风险

- 本卡未运行任何测试，全部结论基于只读源码与既有 046/051/055/058 证据；未动态验证时钟行为。
- M-1 残余风险：即使按 §4 实施，DB 墙钟回拨仍可能在"写入 lease 之后、判定之前"的窗口拉长单租约判定窗口；上限受单租约 ≤3600s 与 deadline 封顶。彻底消除需单调持久时钟（新依赖/新字段），未获授权不引入。
- F-1 判定基于本机 venv 的 httpx 版本实现；将来升级 httpx 须复核该事实（升级依赖须另行授权）。
- TASK-056 无结果文件的事实保持不变；本卡不继承、不补记其结论。
- 超范围/待 Astra 裁定项：执行时间累计字段口径；G-1 收敛触发方式（定时轮询 vs 事件驱动）；L-1 修法在"契约加 pattern"与"拒绝返回可辨原因"之间的取舍（两者可并用）。

## 9. 文档建议（交 Astra，本卡不改正式 docu）

1. FLOW-005 或执行状态可补一句取舍记录：统一 DB 时钟源为第一步，进程内单调监督与失败关闭为必配，跨重启行为以实际重启反例为必需证据；不得把时钟源替换单独记为"已修复时钟回拨"。
2. CALL 契约文档补 CallContext 的 UUID/字符集约束（L-1）与 request_bytes 口径说明（= 实际发送体，F-1 更正后无需放大）。
3. 执行状态 TASK-060 行验收留空，待 Astra 核对本结果与证据后裁定。

## 10. 证据清单（本卡新增，只读产物）

- Ndocu/results/TASK-060-result.md（本文件）
- Ndocu/evidence/task-060/read-scope.md（读取范围与只读声明）
