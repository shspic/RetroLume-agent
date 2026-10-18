# TASK-068 G-1 旧代次未决操作发现与收敛 — 结果

任务：TASK-068 / R-062；类型：开发；STEP-008 局部；父 TASK-060；关联 TASK-058/051/055/062、NFR-002/003、SEC-002、FLOW-005、MOD-003/008、DATA-007。
日期：2026-09-21（Asia/Shanghai）。项目根：D:/shspic/project_NO3_RetroLume-agent。
基线：需求 v1.1、架构 v0.20、执行状态 v1.12；沿 STEP-008 既有开发授权，无真实模型费用。
执行者：Codex Sol，C 档（涉及事务、执行代次与终态竞争，按卡采用强档口径）；本卡不是独立审计。
建议状态：完成（实现候选 + 静态验证）；Astra 验收留空。真实 PG 用例未运行，G-1 不宣告全部关闭。

## 1. 结论摘要

1. 按卡实现两个内部仓储方法：`list_unresolved_operations`（只读有界发现）与 `recover_obsolete_operations`（旧代次未决项事务内收敛）。真实查询实现，非空方法。
2. 旧代次判据只用代次差（`operation.execution_generation < activity.execution_generation`），不使用墙钟；未触碰 M-1 时钟问题，未宣称解决时钟或完整 worker 恢复。
3. 现有 `recover_unknown` 语义零改动：对 repository.py 的 diff 为纯新增 102 行、0 删除（证据 repository.diff）；无 DDL、无索引/字段变化，复用 002 既有部分索引 `activity_operations_recovery`。
4. 新增 `backend/tests/test_activity_recovery.py`：5 组真实 PG 用例，默认无专用 DSN 即整体 skip，不回退用户 DSN。本卡未运行（按卡不启动数据库），标记"真实 PG 未验证"。

## 2. 实际变更与接口

- backend/app/activities/repository.py（修改，纯新增）：
  - 新增 frozen dataclass `UnresolvedOperation(operation_id, admission_id, executor_id, execution_generation, scope_revision, reserved_at, dispatch_started_at)`。
  - `async list_unresolved_operations(activity_id, *, limit=100, after_operation_id=None) -> tuple[UnresolvedOperation, ...]`：仅返回本活动 state IN ('reserved','dispatched')；按 operation_id 稳定升序、排他游标（`operation_id > after_operation_id`）；limit 限整数 1—200（bool/非 int/越界均 ValueError），after_operation_id 非空时按受限字符集校验；复用部分索引；不加行锁；只读观察，不是后续写授权。走既有 `_transaction`（超时设置、psycopg 错误统一 AdmissionUnavailable）。
  - `async recover_obsolete_operations(activity_id, *, error_code="executor_lost") -> int`：锁序保持 来源→活动→操作；锁活动行后以当前 generation 重判；先按 operation_id 升序 SELECT…FOR UPDATE 锁候选行（与 recover_unknown 同锁序），UPDATE 重复代次+状态保护条件，`RETURNING operation_id` 返回实际改动数；仅改 `execution_generation < 当前 generation` 且 state IN ('reserved','dispatched') 的操作为 state='unknown'/disposition='unknown'/recorded_at=CURRENT_TIMESTAMP/受限 error_code。未知活动 → ActivityLedgerConflict("活动不存在")，非法 error_code → ValueError（沿现有语义）。
- backend/app/activities/__init__.py（修改）：导出 `UnresolvedOperation`。
- backend/tests/test_activity_recovery.py（新增，351 行）：DSN 取 `RETROLUME_TASK_068_DATABASE_URL`，skipUnless 保护；每例全新合成活动/来源 ID，asyncTearDown 只按本例 ID 定向删除，无全表 DELETE；全部调用真实仓储方法，无 mock、无复制 SQL。测试文件 sha256=c7450f088235945281c0c25bdf4a57337bd671d34ea10e3de258fb36220896e2。

## 3. 锁序、终态与竞争说明

- 锁序：`_source_rows` → `_lock_sources` → activities FOR UPDATE → activity_operations 按 operation_id 升序 FOR UPDATE，与 recover_unknown/admit/record_outcome 的既有锁序一致；短事务、事务内无网络调用。
- 终态纪律：既有 received/not_sent/unknown 不在新 UPDATE 谓词内，绝不覆盖；当前代次与未来（异常）代次操作被 `<` 条件排除；计数与费用预留零改动（无任何 activities 计数更新）；无发送、无重新调度副作用；重复调用返回 0。
- 与旧 permit 结果记账竞争：双方都先锁活动行再锁操作行，先成终态者保留；晚到 RECEIVED/不同元数据 UNKNOWN 被既有 record_outcome 终态规则拒绝（未放宽幂等）；与收敛结果完全相同的 UNKNOWN（unknown/executor_lost/其余空）按既有幂等规则 no-op，两条路径终态一致（060 §5 口径），不把元数据不同的 unknown 宣称幂等成功。
- recover_unknown 的取消/租约/时钟判据原样保留；新方法只服务旧代次路径，本卡未接 worker、未做自动调用；"新代次建立→旧项收敛→新动作"的调用顺序留给后续监督器卡。

## 4. 验证与证据（C 档自查）

实际执行（唯一运行项）：对 3 个修改/新增文件做不写 pyc 的语法编译检查（读取源码后 compile），0.01 秒，全部 OK。命令与结果原文存 Ndocu/evidence/task-068/compile-check-and-hashes.txt。

hash 记录：
- repository.py：pre 6228b35b…77b4a763 → post cc7fddd4…e6dcc7（diff 纯新增 102 行/0 删除）
- activities/__init__.py：pre 6a1831c1…2209c63 → post 31d0b60c…f19f1d2a
- test_activity_recovery.py（新增）：c7450f08…20896e2
- 原文件副本：Ndocu/evidence/task-068/repository.py.pre-task068、__init__.py.pre-task068；差异：repository.diff、init.diff；改动前 hash：pre-change-hashes.txt。

静态一致性核对：契约（字段/类型/校验/异常）与卡面一致；锁序与既有方法一致；测试用例覆盖卡面全部 5 个要求方向（混合发现与当前代次保护、重复收敛、终态保留与预留不退、跨活动隔离与分页游标、旧 permit 晚到不覆盖 unknown）。

未运行：5 组 PG 用例及任何数据库/应用/旧测试组。**实现候选 / 真实 PG 未验证**；静态通过不等于运行通过，不以本卡自查替代后续真实 PG 证据与独立审计。

## 5. 风险与 M-1 限制

- 收敛正确性依赖"先锁活动行"与并发 record_outcome 的锁竞争；psycopg RETURNING/rowcount 行为在真实 PG 上未动态验证。
- 列表方法为只读观察，无行锁；观察结果与后续写入之间无快照隔离，监督器必须以"列出→收敛→再动作"顺序自行闭环（060 §5）。
- M-1（墙钟/单调监督/跨重启预算）仍未解决：本卡判据不使用时间，仅覆盖"新代次已建立"的旧项收敛；无有效租约且代次未变的场景仍归 recover_unknown 原语义，不因本卡宣称完整 worker 恢复。
- 测试中用 SQL 把旧租约拨快 1 分钟以领取新代次，属合成前提；真实时钟/重启行为归后续运行卡。

## 6. 文档建议（交 Astra，本卡未改正式 docu）

1. 架构 R-061 段可在 TASK-068 验收后补记实现落点与"列表非写授权、收敛非重发"边界。
2. 执行状态 TASK-068 行待 Astra 核对本结果与证据后裁定；建议在下一运行卡中一并回归 055 受影响用例（新方法未触既有路径，可按风险裁量）。

## 7. 必须人工操作与下一步

- 无本卡范围内的人工操作；未运行数据库，未触碰用户数据/Git。
- 下一步（Astra 裁定）：另开真实 PG 运行卡执行 test_activity_recovery.py（专用 DSN 授权）+ 独立审计；监督器卡接入"列出→收敛→新动作"顺序；M-1 另卡。
