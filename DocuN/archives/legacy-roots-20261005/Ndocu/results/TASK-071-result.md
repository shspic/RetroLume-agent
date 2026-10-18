# TASK-071 结果 —— 旧代次收敛改为有界单批（TASK-068 切片，TASK-070 F-1 最小修正）

任务：TASK-071 / R-065；开发；STEP-008 局部；父 TASK-068，关联 TASK-069/070、NFR-002/003、SEC-002、FLOW-005、DATA-007。
执行者：Codex Sol（C 档，因事务批次、锁定集合与 UPDATE 一致性风险高按强档执行；非独立审计）。
日期：2026-09-21（Asia/Shanghai）。根目录：D:/shspic/project_NO3_RetroLume-agent。
需求 v1.1、架构 v0.22、执行状态 v1.14。原开发授权；内部仓储无调用方，Astra 裁定补单批上限。

---

## 0. 结论摘要

**建议状态：代码层「有条件通过」（候选补丁，待 Astra 验收）。** `recover_obsolete_operations` 已改为单批有界收敛：新增仅关键字参数 `limit`（默认 100，非 bool 整数 1—200，非法 ValueError，不静默截断），加锁 SELECT 与 UPDATE 收敛到同一确切锁定 ID 集合。语义边界（当前/未来代次、终态、预留/费用、准入与发送事实、recover_unknown 时间语义）全部保持不变。测试新增 test_06 有界单批用例并保留 069 清理与 5 组原用例。**本卡仅做了 compile 语法检查，未运行任何 PG/unittest；静态正确不等于真实通过。**

## 1. 接口与实际差异

### 1.1 接口变化（backend/app/activities/repository.py）

- 旧：`recover_obsolete_operations(activity_id, *, error_code="executor_lost") -> int`
- 新：`recover_obsolete_operations(activity_id, *, error_code="executor_lost", limit=100) -> int`
- `limit` 校验在事务开启前：`isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 200` → `ValueError("limit 必须是 1 到 200 之间的整数")`。与 `list_unresolved_operations` 的既有校验同款。
- 旧位置参数调用不受影响（无调用方；测试用例全部以默认 limit 运行仍得原结果）。
- **返回值语义变化已在 docstring 写明**：返回值是本批实际改动数，不代表整个活动已恢复完毕。

### 1.2 事务内逻辑（差异实质，+24/−6 行，全部落在该方法内）

1. 锁序不变：来源（`_lock_sources`，UUID 升序）→ 活动（`FOR UPDATE`）→ 操作；`current_generation` 仍在活动锁取得之后读取。
2. 加锁 SELECT 新增 `LIMIT %s`，保留 activity_id / state IN ('reserved','dispatched') / execution_generation < 当前代次三重过滤与 `ORDER BY operation_id`。PostgreSQL 计划中 Limit 节点位于 LockRows 之上（拉取式执行器，行锁随实际取出行生效，SKIP LOCKED 队列模式同源），故仅锁定本批候选。
3. 收集 `locked_ids = [row["operation_id"] ...]`；空集合直接 `return 0`，不执行 UPDATE。
4. UPDATE 限定为 `operation_id = ANY(%s)`（即锁定集合）**并重复** activity_id / state / 旧代次三重条件，`RETURNING operation_id` 计实际改动数。未重新按宽谓词扫全部旧项，未用另一个 LIMIT 子查询代替锁定集合。
5. 单次事务、无内部循环、无重试、无调度。调用方未来按有界次数/总期限调用至 0 并复查（本次不实现）。

### 1.3 明确未改（对照 TASK-070 第 3/5 节逐项保持）

`recover_unknown`（含取消/租约/时钟语义）、`record_outcome`（含终态纪律与元数据幂等判等）、`admit`、`claim_lease`、`cancel_activity`、`_locked_operation`、列表投影（`list_unresolved_operations`）逐字未变；无 DDL/索引/依赖/锁参数变更；未接 worker；未处理 M-1；无循环恢复器。终态竞争保护（旧 permit 仍可记 unknown）保留。

## 2. 批次与终态边界（如实说明）

- `limit` 只约束**加锁与改写行数**；不约束扫描/排序输入规模（谓词 `state IN (...)` 跨部分索引两值、排序键为第三列，取批仍可能产生 Sort 节点，见 070 F-5），也不彻底消除锁等待（来源锁与活动锁仍整事务持有）。
- 返回值小于 `limit` 或 0 仅表示本批无更多匹配，不解释为活动永久无未决项；调用方须复查。
- 070 F-1 所述"语句超时→整批回滚→跨活动阻塞"的触发面被压缩为单批行数（≤200），但未实测耗时，风险定性仍属推断（070 亦明示为风险推断、非已发生事故）。
- 070 F-2/F-3/F-4/F-5 均不在本卡范围，状态不变。

## 3. 测试（backend/tests/test_activity_recovery.py，+100/−0 行）

- **保留**：069 定向外键顺序清理（asyncTearDown）、test_01—test_05 全部 5 组原业务断言，逐字未改（默认 limit=100 覆盖其候选规模 1/1/1/7/1）。
- **新增 test_06_bounded_single_batch_converges_incrementally**：5 个旧未决项（old-op-00…04，代次 1）+ 当前代次对照（cur-op-1，代次 2）；`limit=2` 连续收敛返回 2/2/1/0；逐批断言仅对应已选项变 unknown、其余仍 reserved；每批后断言 `execution_generation=2`、`requests_reserved=6`、`cost_reserved_microunits=600` 不变；终态断言 error_code/disposition/recorded_at 与当前代次操作不受影响；末尾补 limit 的 `0/201/True/"2"` 拒绝。
- 专用 DSN（`RETROLUME_TASK_068_DATABASE_URL`）缺失即类级 skip，不回退用户 DSN，不全表清理——均沿用原文件机制。
- **测试只编写，本卡未运行**；未运行用例清单见 `Ndocu/evidence/task-071/unrun-tests.txt`。

## 4. 命令、证据与哈希

冻结输入核对（`Ndocu/evidence/task-071/pre-hashes.txt`）：

| 对象 | 卡内冻结值 | 实测（改动前） | 判定 |
|---|---|---|---|
| backend/app/activities/repository.py | cc7fddd4e685e1d3af859c7b402d0734354cef5675ed72f2f8acb83c92e6dcc7 | 同左 | 一致 |
| backend/tests/test_activity_recovery.py | 7bf924cded794b94bdc213d255177253af2b3948ad844f302d7bd987ae6804f4 | 同左 | 一致 |

改动后哈希（`Ndocu/evidence/task-071/hashes-and-diffs.txt`，含权威 unified diff）：

| 对象 | post sha256 | diff 统计 |
|---|---|---|
| backend/app/activities/repository.py | 50ec537b07533c68194651b008d275176430effeb67126391ef43b96155cfce6 | removed=6 added=24 |
| backend/tests/test_activity_recovery.py | ef705113fbf6af83a0a29e99b40dfdb68109282c0ae8b724790e1d440575d246 | removed=0 added=100 |

语法检查（`Ndocu/evidence/task-071/compile-check.txt`）：用 `backend/.venv/Scripts/python.exe` 对两文件 `compile(source, path, "exec")`，不写 pyc，结果 `compile OK` ×2，elapsed 0.02 秒（限时 60 秒内）。第一次尝试因 PowerShell 5.1 传递多行 `-c` 参数吞换行而失败（`SyntaxError: '(' was never closed`，报错在 `<string>` 第 1 行，与源文件无关），有据修正为脚本文件方式后复检一次通过；完整命令记录见 `commands-run.md`。

证据目录 `Ndocu/evidence/task-071/`：pre-hashes.txt、repository.py.pre-task071、test_activity_recovery.py.pre-task071、compile_check.py、compile-check.txt、make_diffs.py、make-diffs-run.txt、hashes-and-diffs.txt、unrun-tests.txt、commands-run.md。

## 5. 未验证项与风险

1. **未运行任何测试**（含新增 test_06）：无 PG 环境执行，本卡禁令遵守。`LIMIT %s` 参数化、`operation_id = ANY(列表)` 在 psycopg 3.3.5 + PG 17.11 的实际类型适配、LockRows/Limit 行为、批次耗时与锁等待均为静态论证，需真实 PG 验证。
2. **静态正确 ≠ 真实通过**；068/071 定向审计复核与真实 PG 验证由 Astra 后续安排（卡内明示）。
3. 070 F-4（collation 前提）对新加锁 SELECT 同样成立：`ORDER BY operation_id` 与 `ANY` 集合匹配不受 collation 影响（等值比较），排序选择批次在确定性 collation 下稳定；未改索引，未跑 EXPLAIN。
4. 批次上限不消除扫描/排序输入代价（070 F-5），未做性能基准。
5. 无调用方（内部仓储未接 HTTP/worker），返回值语义变化不产生现网影响。

## 6. 文档建议（供 Astra，本卡不改正式 docu）

- 执行状态登记 R-065/TASK-071 结果与本结果文件路径；CHANGE.MD 由 Astra 追加 CHG 条目（本卡未写）。
- G-1 相关描述如提及"recover_obsolete_operations 一次收敛全部旧项"，应更新为"有界单批、调用方循环至 0"。

## 7. 必须人工操作 / 下一步（供 Astra 决定）

1. Astra 验收本差异（冻结哈希 → 新哈希比对、差异边界核对）。
2. 安排 068/071 定向审计复核（新哈希为审计对象）。
3. 安排真实 PG 验证卡：运行 test_activity_recovery.py 全部 6 例（含 test_06），覆盖 2/2/1/0、代次/预算不变、终态/预留不退、limit 拒绝；可顺带 EXPLAIN 定性 070 F-4/F-5。
4. 后续接线卡决定调用方循环策略（有界次数/总期限 + 复查）与 F-2 信任边界。

## 8. 产物清单

- `backend/app/activities/repository.py`（修改）
- `backend/tests/test_activity_recovery.py`（修改）
- `Ndocu/evidence/task-071/`（10 个证据文件，见第 4 节）
- `Ndocu/results/TASK-071-result.md`（本文件）

不填 Astra 验收，不宣告 G-1 或 STEP-008 完成。
