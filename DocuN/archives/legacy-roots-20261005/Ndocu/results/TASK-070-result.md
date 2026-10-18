# TASK-070 结果 —— G-1 旧代次未决操作发现与收敛（TASK-068 切片）独立只读代码审计

任务：TASK-070 / R-064；独立只读代码审计；STEP-008 局部；关联 TASK-068、NFR-002/003、SEC-002、FLOW-005、MOD-003/008、DATA-007。
审计者：独立审计 Agent（隔离新会话，未参与 TASK-068 实现或修正）。
日期：2026-09-21（Asia/Shanghai）。根目录：D:/shspic/project_NO3_RetroLume-agent。
需求 v1.1、架构 v0.21、执行状态 v1.13。

---

## 0. 结论摘要

**建议状态：代码层「有条件通过」。** 未发现阻塞级（正确性 / 并发 / 数据边界）缺陷；冻结对象的哈希与卡内值逐字节一致，原始差异完备且为纯新增（删除行 0），既有 `recover_unknown` 与原有终态纪律逐字未变。发现 1 项 MEDIUM 标准缺口（收敛路径无批次上界）与 4 项 LOW 事项（授权边界说明、未知活动语义不对称、collation 环境前提、排序代价未经测量）。**本审计仅为静态代码层结论，不构成真实 PG 运行通过，不得据此写入 Astra 最终验收或关闭 G-1 动态门槛。**

关键正面结论（详见第 4.4 节）：收敛候选集 `generation < 当前代次` 与写授权集 `generation == 当前代次` 在结构上互斥，且 `execution_generation` 插入后无任何语句可改写，因此「晚到成功结果」与「旧代次收敛」不可能作用于同一操作，两者并发无需额外仲裁。

---

## 1. 独立性

- 未参与 TASK-068 实现或任何修正；未继承该执行会话的聊天、思考或自评。
- 未打开 Ndocu/results/TASK-068-result.md、未读取 069 结果报告、未读取 backend/tests/test_activity_recovery.py（卡内明示不读）。
- **披露一次无意暴露**：以 `grep` 全库定位新方法引用（目的在于确认有无调用方/worker 接线）时，输出带出了 TASK-068-result.md 的 4 行、TASK-058/060-result.md 的若干行、.workbuddy/memory/2026-09-20.md 的 1 行。这些内容均为任务要求或历史背景的复述，未被用作证据、未据此形成任何结论；所有结论均来自第 2 节清单中的原始生产对象、原始 diff 与迁移 DDL。记录于此供 Astra 复核独立性判定。
- 本次未使用 Git、未联网、未安装、未读取凭据或真实配置、未运行测试/Docker/数据库/应用/模型。

读取清单与未执行操作详见 `Ndocu/evidence/task-070/audit-manifest.md`。

---

## 2. 冻结对象实测哈希与差异边界

### 2.1 哈希核对（`Ndocu/evidence/task-070/hashes-and-diff-boundary.txt`）

| 对象 | 卡内冻结值 | 实测值 | 判定 |
|---|---|---|---|
| backend/app/activities/repository.py | cc7fddd4e685e1d3af859c7b402d0734354cef5675ed72f2f8acb83c92e6dcc7 | 同左 | 一致 |
| backend/app/activities/__init__.py | 31d0b60cfc644c797a04fb31e9c3a4da242969abbe0e5b54648b1d18f19f1d2a | 同左 | 一致 |

命令：

```bash
sha256sum backend/app/activities/repository.py backend/app/activities/__init__.py
```

两项均一致，未触发卡内「不符停止审计受影响快照」条件。

附带核对：`backend/migrations/002_activities.sql` 实测 `3a9c5855aa9ddc54a03666327267ff3b7cb81eafa931a9f260c5637922b2dda6`，与 051/055 证据 `source-hashes.sha256` 记录的同名基线逐字节一致 → DDL 自 051 以来未变。

### 2.2 差异完备性反重建（`Ndocu/evidence/task-070/diff-reconstruction-check.txt`）

方法：取 068 的 pre 副本，用提供的原始 diff 反向重建，比对哈希。

```bash
cp Ndocu/evidence/task-068/repository.py.pre-task068 /tmp/audit070/f.py
patch f.py < Ndocu/evidence/task-068/repository.diff
sha256sum f.py
```

结果：重建产物 = `cc7fddd4e685e1d3af859c7b402d0734354cef5675ed72f2f8acb83c92e6dcc7`，与生产对象逐字节一致；`init.diff` 同理得到 `31d0b60c…`。**结论：原始差异完备、未隐藏改动。**

权威 `diff -u`（pre 副本 → 生产对象）统计：删除行 **0**、新增行 **92**、hunk 2 个。即本次变更**纯粹新增**，仓库中任何既有语句均未被改写。提供的 repository.diff 首个 hunk 起始行标注为 `-61` 而权威值为 `-63`，属上下文窗口截取差异；因反重建哈希一致，已排除实质差异。

编译证据链：`Ndocu/evidence/task-068/compile-check-and-hashes.txt` 记录两文件 `compile OK`，且其 post-change sha256 与本卡实测冻结值一致，故该编译结论绑定到当前字节。**本卡未重跑编译**（限量要求「无新增动态检查」）。

### 2.3 变更落点

- `UnresolvedOperation` frozen dataclass：生产文件 66-76 行。
- `list_unresolved_operations`：368-413 行。
- `recover_obsolete_operations`：415-456 行。
- `__init__.py`：导入与 `__all__` 各增 `UnresolvedOperation`。

---

## 3. 逐项标准符合性核对

| 原始标准 | 结论 | 依据（生产文件行号） |
|---|---|---|
| 有界发现本活动 reserved/dispatched | 符合 | 382（state 谓词硬编码）、377-378（limit 1—200） |
| 按 operation_id 稳定排序 | 符合（含 collation 前提，见 F-4） | 396 `ORDER BY operation_id`；活动内 operation_id 由主键 (activity_id, operation_id) 保证唯一，故序为全序 |
| 排他游标 | 符合 | 384-386 `operation_id > %s`，游标取自上一页真实 operation_id，故严格排他 |
| limit 整数 1—200 | 符合 | 377-378：显式拒绝 bool、非 int、越界 |
| 返回定位及代次/时间事实 | 符合 | 391-392 选取 operation_id/admission_id/executor_id/execution_generation/scope_revision/reserved_at/dispatch_started_at，与 002 表列名逐一对应 |
| 列表不是写授权 | 语义成立，机制依赖信任边界（见 F-2） | 68 文档串；390 无 FOR UPDATE |
| 收敛仅 gen < 当前 activity.generation 且仍未决 | 符合 | 437、448 `execution_generation < %s`；436、448 `state IN ('reserved','dispatched')` |
| 来源→活动→操作锁序 | 符合 | 426-428（来源 FOR UPDATE → 活动 FOR UPDATE）；433-441（操作 FOR UPDATE） |
| 活动锁后重新判定 | 符合 | 428 取活动锁，432 才读 `current_generation` |
| 操作排序锁定 | 符合 | 438 `ORDER BY operation_id`；PostgreSQL 中 `LockRows` 位于 `Sort` 之上，故按排序序加锁 |
| UPDATE 重复条件 | 符合 | 443-450 重复 activity_id + state + generation 三重条件 |
| 返回实际数量 | 符合 | 443-453 `RETURNING operation_id` → 454 `len(changed)` |
| 当前/未来代次与终态不改 | 符合 | 严格 `<` 排除当前与未来代次；state 谓词排除 not_sent/received/unknown |
| 费用次数不退 | 符合 | 444-447 仅改 state/disposition/error_code/recorded_at；未触碰 activities.requests_reserved、activities.cost_reserved_microunits、activity_operations.reserved_cost_microunits |
| 无网络/重发 | 符合 | 两方法仅发 SQL；无 DELETE、无网络、无调度；admit 527-533 仍拒绝已占用的 operation_id |
| 晚到结果不覆盖 unknown | 符合 | 685-688 终态分支：状态属 {not_sent,received,unknown} 且结果不同 → AdmissionDenied；结果相同 → 幂等返回 |
| 重复收敛无副作用 | 符合 | 第二次调用匹配 0 行，UPDATE 不改写任何行，返回 0 |
| 保持原 recover_unknown 与 M-1 时钟边界 | 符合 | 权威 diff 删除行 0，recover_unknown（330-366）逐字未变；recover_obsolete_operations 全文无墙钟调用 |
| 未接 worker、不能宣称完整恢复 | 符合 | 全库仅 `__init__.py` 导出，无调用方；main.py 61-62 只挂 materials/pdf_review 路由，账本未接入 HTTP |

补充核实（活动隔离与写入面收敛）：全库 `activity_operations` 的读写**仅存在于 repository.py**（已 grep 全 backend/app 证实）；所有写路径均在取得活动行锁之后才触碰操作行（admit 515→527、mark_dispatch_started/record_outcome 经 `_locked_operation` 585→587、recover_unknown 337→350、cancel_activity 311）。来源锁顺序亦全局一致：`_source_rows` 的 `ORDER BY source_id`（UUID 字节序）与 `_validate_spec` 按 `UUID(...).int` 排序（158-170）为同一序。

---

## 4. 发现清单

### F-1【MEDIUM / 标准缺口】收敛路径无批次上界，与语句/锁超时组合后可能永久不可执行，并跨活动阻塞同来源写入

- **原始位置**：`backend/app/activities/repository.py:433-441`（加锁 SELECT 无 LIMIT）、`443-453`（UPDATE 无 LIMIT）。
- **触发条件**：单个活动累积较多 `generation < 当前代次` 且仍为 reserved/dispatched 的旧项时，一次 `recover_obsolete_operations` 在同一事务内锁定并改写全部匹配行。可累积量受 `activities.max_requests` 约束，而 `_validate_spec`（185-186）只校验正整数值域、**不设上界**；每次 admit 恰好产生一行操作。
- **影响**：
  1. 批次耗时超过 `statement_timeout = 3000ms`（107-132 事务包装内的设置）即触发 QueryCanceled，被 `except psycopg.Error` 归一为 `AdmissionUnavailable` 并整事务回滚。相同输入每次重试都会再次超时 → 该活动的旧代次收敛在实现层面**不可完成**（失败关闭，非数据损坏、非部分提交）。
  2. 事务期间持有全部 `material_sources` 行锁与活动行锁，超过 `lock_timeout = 2000ms` 后，**其他活动**的 admit/claim_lease/create_activity（若共享任一来源）与同活动的 admit 会以 `AdmissionUnavailable` 失败 → 影响范围跨活动，且发生在 G-1 恢复路径本应消除故障的时刻。
- **对照**：标准已要求发现侧有界（列表 limit ≤ 200，377-378），但未对收敛侧规定上界；本项属**当前标准缺口**而非实现偏离。
- **最小修正（位置同上两处）**：为 `recover_obsolete_operations` 增加批次参数（沿用列表的校验规则与量级），把加锁 SELECT 与 UPDATE 收敛到同一批次，例如
  `SELECT operation_id FROM activity_operations WHERE <原谓词> AND operation_id IN (SELECT operation_id FROM activity_operations WHERE <原谓词> ORDER BY operation_id LIMIT %s) ORDER BY operation_id FOR UPDATE`，
  UPDATE 侧使用同一子查询形式，保留 `RETURNING` 计数。调用方以「返回数量 < 批次」或返回 0 作为收敛完成条件。**保持锁序、不退款、不重发、不改语义。**
- **说明**：当前未接 worker，该方法无实际调用方，故为潜力缺口而非现网故障；但一旦监督器按活动循环调用即成真实约束，建议在接线卡前决定（或明确接受当前规模并记录）。

### F-2【LOW / 授权边界说明，非本差异缺陷】列表投影恰等于 `record_outcome` 的授权三元组

- **原始位置**：`repository.py:391-392`（返回 admission_id）、`568-599`（`_locked_operation` 的身份核对）、`contracts.py:156-162`（`AdmissionPermit` 仅含 admission_id/operation_id/executor_id）。
- **事实**：`_locked_operation` 对写入方的身份核对只用「admission_id 定位 + operation_id 与 executor_id 相等」这三项；`AdmissionPermit` 本身也只有这三项。即这三项在现行契约中**就是写授权本身**，而 `UnresolvedOperation` 恰好原样返回它们。
- **影响**：任何能调用 `list_unresolved_operations` 的代码，都获得了对所列操作调用 `record_outcome` 的凭据（含对当前代次已 dispatched 操作提交 received）。故「列表不是写授权」在语义/文档层面成立，在机制层面依赖信任边界而非能力分离。
- **已核实的抑制因素（使风险显著降级）**：
  1. 终态纪律阻断陈旧观察覆盖：685-688 使 state ∈ {not_sent,received,unknown} 时不同结果一律拒绝，686-687 使元数据不同的「都是 unknown」不被当作幂等成功 → 与标准第 5 条一致。
  2. **收敛路径不接受任何列表输入**：`recover_obsolete_operations` 只接收 activity_id（415），候选集在活动锁下重新推导 → 陈旧观察在结构上无法驱动收敛，此即标准「列表观察后陈旧不构成授权」的真正落点，已成立。
  3. 账本未接入任何 HTTP 路由（main.py 61-62），无不可信调用方。
- **最小修正（接线时）**：在监督器/worker 接线卡中显式限定 `list_unresolved_operations` 的调用者限于已被授权写该活动结果的组件；若需机制化，再评估把写授权改为不可由观察推导的凭证（超出本卡标准，需 Astra 决定）。
- **明确**：标准要求返回这 7 个字段，故本项**不是**本差异的实现缺陷，仅记录边界。

### F-3【LOW / 语义不对称，标准未规定】未知活动在列表侧静默返回空

- **原始位置**：`repository.py:368-413`（无活动存在性判断，缺失时返回空元组）；对照 `415-431`、`330-340`、`305-314` 均抛 `ActivityLedgerConflict("活动不存在")`。
- **影响**：调用方无法区分「活动不存在（含 ID 拼写错误）」与「活动当前无未决项」。因列表不构成写授权、收敛侧另有硬校验，无直接数据风险；风险仅在调用方把空列表误当作对某 activity_id 的确认。
- **最小修正（可选）**：若后续监督器需要该区分，在列表前置一次存在性读取并在缺失时抛 `ActivityLedgerConflict`；也可保持现状、在接线契约中写明「空结果不代表活动存在」。标准未规定，本项为建议。

### F-4【LOW / 环境前提 + 证据缺口】排序与游标依赖数据库默认 collation

- **原始位置**：`repository.py:396`（`ORDER BY operation_id`）、`385`（`operation_id > %s`）均未指定 `COLLATE`；`002_activities.sql:54` 列 `operation_id VARCHAR(128)`、`84-86` 部分索引同样未带 collation 限定。
- **事实**：051/055 证据记录 PG 17.11 官方 Debian 镜像（`17.11-1.pgdg12+2`）与合成库，但**未记录容器创建参数或 initdb locale**；仓库内未见 collation 固化。
- **影响**：在确定性 collation 下（含 glibc `en_US.utf8`，即官方镜像默认）`ORDER BY` 与 `>` 同源同序，且游标取自上一页真实值、活动内 operation_id 唯一 → 排序稳定、分页不跳行，逻辑正确。触发条件为非确定性 collation（如 ICU `deterministic=false`）：与游标在该 collation 下「相等」的不同字符串会被 `>` 排除，可能跳行。
- **最小修正**：若要得到与库无关的稳定序，在 `ORDER BY` 与游标比较上显式 `COLLATE "C"`；**注意现有部分索引不带该 collation，改后需重建索引才能保持索引序** —— 属后续卡，本卡标准明示「不加索引/字段」，故不改。
- **静态推断，未运行 EXPLAIN/真实 PG**：现部署下判定为非缺陷，记录为环境前提。

### F-5【LOW / 静态推断 + 证据缺口】列表排序代价不受 LIMIT 约束

- **原始位置**：`repository.py:390-398`，谓词 `state IN ('reserved','dispatched')` 跨部分索引 `activity_operations_recovery(activity_id, state, operation_id)`（002:84-86）第二列的两个取值，而排序键是第三列。
- **影响**：单一索引无法跨两个区间直接提供全局有序，静态推断计划中会出现 `Sort` 节点；`LIMIT 200` 只约束返回行数、不约束排序输入，故取一页的代价随该活动未决项总数增长（仍为只读、无锁、无写入）。单活动未决项通常受在途请求数约束，实际规模可能很小。
- **最小修正（若实测证实代价）：评估索引形态或改为按 state 两段有序取再归并 —— 属后续卡，本卡不改。**
- **需真实 PG EXPLAIN 才能定性**，本项为静态推断，不计入阻塞。

---

## 5. 无发现项边界（已核实正确，附限定）

1. **参数校验与活动隔离**：activity_id 始终经 `_uuid` 规范化（376、422）并作为硬过滤条件（382、434、447），游标不跨活动；limit 拒绝 bool/非 int/越界（377-378）；`after_operation_id` 以与写入端完全相同的字符集与 128 长度上限校验（380 对 146-149、466），与 `VARCHAR(128)` 一致。
2. **SQL 参数化**：所有取值经 `%s` 传参；f-string 仅拼接静态字面片段（382-387），无注入面。该拼接模式在扩展时较脆弱（若将来引入动态片段需复核），不构成本次缺陷。
3. **锁顺序与并发写入不可绕过**：全路径遵循「来源（UUID 升序）→ 活动 → 操作」，且活动锁先于操作行锁；`execution_generation` 仅由 claim_lease（292-300）、cancel_activity（317-325）在持有活动锁时递增，单调不减 → 收敛读取的 `current_generation` 在事务内稳定，任何并发写路径都无法绕过该重判。`_locked_operation` 首条为**不加锁**读（575-578）用于定位活动，不持有乱序锁，随后按序补锁，无锁序倒置。
4. **代次分离（关键安全性质）**：收敛集 `{gen < current}` 与写授权集 `{gen == current}`（`_operation_is_current` 608）互斥；且 `execution_generation` 插入后无任何语句改写（已逐一核对全部 UPDATE 语句）→ 两类并发不可能作用于同一操作，故无需额外仲裁即满足「晚到不得覆盖 unknown」「先成终态者保留」。
5. **终态竞合与幂等**：收敛写入 state='unknown'/disposition='unknown'/recorded_at 非空，满足 002 的三条 CHECK（79-81），不会因约束失败回滚；重复调用匹配 0 行返回 0 且无写入副作用；`_stored_outcome`（664-678）与 `_outcome_values`（629-662）字段与顺序一一对应，元数据不同即不判等。
6. **预算不变量**：收敛不减少 `requests_reserved`、`cost_reserved_microunits`，亦不改 `reserved_cost_microunits` → 预留跨代次保留，后续 admit 的额度检查（504-506）仍将旧预留计入，符合 FLOW-005「预留保留、不自动退还」。
7. **无网络/无重发/无删除**：两方法只发 SQL；无网络调用、无 DELETE、无重新调度；admit 对已存在 operation_id 仍拒绝（527-533），收敛不删行 → 同一操作键不可能重发。
8. **适用范围（不扩大解读）**：收敛仅限单一活动内、仅在先发生租约重领或取消使代次递增之后生效；不扫描活动集合（无全局查询）、不处理「租约过期未重领」（属 recover_unknown）、不涉及 M-1 时钟问题。**且未接 worker（无调用方），故不得宣称完整恢复。**
9. **既有语句未变**：权威 diff 删除行为 0，`recover_unknown`（330-366）、`record_outcome`（680-704）、`admit`、`claim_lease`、`cancel_activity` 逐字未变。
10. **契约与导出一致**：`__init__.py` 导入与 `__all__` 同步导出 `UnresolvedOperation`；`AdmissionLedger` Protocol（contracts.py:183-194）未增加方法，新方法为内部仓储扩展，`RejectingAdmissionLedger` 不受影响。

---

## 6. 证据缺口（明确声明）

本卡结论**仅到代码层**。未运行任何测试 / Docker / 数据库 / 应用 / 模型，未做 EXPLAIN，未做并发实测。真实 PG 上未验证：

1. `LIMIT %s` 及 uuid/text 参数在 psycopg3 3.3.5 + PG 17.11 下的实际类型适配与计划形状；
2. 列表 ORDER BY 在真实 collation 下的跨页行序（F-4）与是否出现 Sort（F-5）；
3. 收敛批次的真实耗时、语句超时行为与锁等待对同来源其他活动的影响（F-1）；
4. 002 三条 CHECK 在实际 UPDATE 下的通过（本次为静态推导满足）；
5. 并发崩溃/终态竞争的实测行为（本次为锁与谓词的静态论证）。

**静态审计不得当作运行通过。** 后续真实 PG 证据回来后，按具体需要复核上述 1-5 项，本卡不预填通过。

---

## 7. 建议状态与边界

- **代码层建议：有条件通过。** 无阻塞级发现；F-1 需在 worker/监督器接线前决定（补批次上界，或明确接受当前规模并记录），F-4/F-5 需真实 PG 证据定性，F-2/F-3 为边界说明与可选建议。
- **本卡不写 Astra 最终验收，不关闭 G-1 动态门槛，不宣告 STEP-008 完成。**
- 未修改实现 / 测试 / 迁移 / 正式 docu / 旧证据；未使用 Git；未运行测试与数据库。

## 8. 产物

- `Ndocu/results/TASK-070-result.md`（本文件）
- `Ndocu/evidence/task-070/audit-manifest.md`（独立性、读取清单、未执行操作、写入清单）
- `Ndocu/evidence/task-070/hashes-and-diff-boundary.txt`（哈希与差异边界原始输出）
- `Ndocu/evidence/task-070/diff-reconstruction-check.txt`（差异反向重建核验）

**CHANGE.MD 登记：** 依 docu/AGENTS.MD 第 6 节，CHANGE.MD 由 Astra 统一登记；本卡禁止写正式 docu，故以上 4 个文件**尚未登记**，待 Astra 追加 `CHG-XXXX`。

## 9. 下一步（供 Astra 决定，不自行推进）

1. 按 F-1 决定收敛侧批次上界：或立最小修正卡，或明确记录当前规模假设并接受。
2. 路由真实 PG 证据卡：覆盖旧 reserved/dispatched + 当前未决混合、重复收敛、终态与预留不退、跨活动隔离/分页、旧 permit 晚到不能覆盖 unknown，并补 EXPLAIN 以定性 F-4/F-5。
3. F-2 在监督器接线卡中固化信任边界。
