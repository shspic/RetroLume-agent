# TASK-078 / R-072 review-03 增量独立复核证据记录

日期：2026-09-23。
任务性质：既定单行修复（N1）与现成客观证据的**增量独立复核**，不重审未受影响模块，不重跑有效验证。
执行窗口：承接 TASK-078 review-02 原 Work Buddy 独立审计窗口（保留其结论与证据上下文）。
型号标识（如实记录）：本轮窗口自报 DeepSeek-V4.1-Flash；review-02 轮自报 GLM-5.3-Flash。按用户 2026-09-23 指示"型号如实记录即可，不以模型名称不一致为理由重审"，该差异不作为本轮重审理由，仅作身份登记。

## 一、独立性披露

1. 本窗口未参与 TASK-077 修正轮02 的实现：本轮与 review-02 轮对本项目源码均为只读，未对 backend/app/activities/repository.py 或任何被审文件执行写入。
2. 已披露的间接接触面：项目工作记忆文件 .workbuddy/memory/MEMORY.md 载有 TASK-077 修正轮02 的执行记录（含 N1 修复位置、hash 轮换、偏差 D-R02-1）。该记录来源为本项目的记忆文件，不是本窗口的执行痕迹；本窗口未读取 TASK-077 的结果文档、自评或实现聊天。
3. 残余不确定性：无法从文件层完全排除"同一客户端多会话"的可能。就机制而言，本窗口未持有实现过程的推理上下文，N1 关闭判断仅由本轮的只读证据（当前源码 + diff + 构造日志 + hash）支撑。
4. 判定：独立性成立（附上述受限披露），可签发代码层结论；不签发任何动态（PG）通过。

## 二、冻结 hash 重算（本轮独立）

见同目录 hash_current.txt。六文件与卡面冻结值逐项一致，无漂移。repository.py 为唯一变更文件。
链证：revision-02/pre__repository.py 的 hash = 33b733e6…ffa57e，与 review-02 的 hash_current.txt 中 repository.py 记录值一致 → 修复 diff 的 pre 快照即 review-02 所审快照；修复增量确实落在被我方审过的基线之上。

## 三、N1 关闭的四项事实核对（第 1、2 项）

### 3.1 定义与位置（当前源码实测）

backend/app/activities/repository.py 第 70–77 行：
- 第 70 行 @dataclass(frozen=True) 保留；
- 字段序列 activity_id / executor_id / execution_generation / scope_revision / lease_expires_at / window_seconds；
- window_seconds: int 位于 lease_expires_at 之后（第 76→77 行），无默认值（必填）。

### 3.2 diff 增量边界

Ndocu/evidence/task-077/revision-02/diff_revision02_repository.txt 全文仅一个 hunk：
@@ -74,6 +74,7 @@ ，内容为 "+    window_seconds: int"。
- 增量 = +1 行 / −0 行；
- 无 SQL 语句改动、无事务边界改动、无其他文件改动（post_hashes 显示其余五文件 UNCHANGED，本轮 hash 重算复现该结论）。
- pre 版本构造点位于第 382 行，post 版本位于 383 行（+1 行后移），与构造日志 [call_site_line] 383 一致。

### 3.3 构造点唯一性与位置一致性（本轮独立 Grep + 读取）

全仓 *.py 检索 "ActivityLease(" → 命中仅 backend/app/activities/repository.py:383 一处（测试文件中的 claim(...) 是测试自有 helper，不构造 ActivityLease）。
当前第 383–390 行六位置实参：
1 activity_id ／ 2 executor_id ／ 3 generation ／ 4 row["scope_revision"] ／ 5 lease_expires_at ／ 6 effective_window。
与第 72–77 行字段顺序（第 5 = lease_expires_at，第 6 = window_seconds）逐位对应；第 6 实参 effective_window 即 claim 成功路径的 W_eff = min(window_seconds, available)（第 372 行），满足合同"返回实际预扣 W_eff"。
→ N1 的触发条件（frozen dataclass 收到多余位置参数）已消除，且未引入新的位置错配。

### 3.4 构造脚本与日志的绑定（复用，未重跑）

Ndocu/evidence/task-077/revision-02/check_activitylease_contract.py（全文已读）：
- 真实导入 app.activities.repository.ActivityLease，不复制、不 mock；脚本自身计算并打印被测文件 hash；
- 断言覆盖：字段顺序 expected_order 六项、window_seconds 注解 'int'、frozen=True、无类属性默认值、六位置参数真实构造、window_seconds == 79、前五字段按位置逐一相等断言、frozen 赋值抛 FrozenInstanceError、调用点实参个数 6、第 5 实参 lease_expires_at、第 6 实参 effective_window。

construct_check.log：
- [hash_under_test] 045a3cf8…2534 = 当前冻结值；[hash_under_test_after] 同值（运行期文件未变）；
- exit_code: 0；elapsed_seconds: 0.53；pycache_unchanged: True（files=2）；
- [RESULT] PASS window_seconds==79 positional_contract_ok；[call_args] 六项与 3.3 独立读取一致。

适用范围界定：该日志与脚本**只证明构造契约**（字段存在性/顺序/类型/frozen/位置参数一致性），**不证明 PG 可用性、不证明运行时真实认领成功、不构成动态通过**。

## 四、未变五文件的 hash 适用性（第 3 项）

__init__.py、004 迁移、测试 time_budget/ledger/recovery 五文件本轮重算 hash 与卡面一致，与 review-02 时值相同。因此 review-02 对这五文件形成的结论与证据适用性保持不变（不重新采集、不重新审查）。__init__.py 第 3–21 行 re-export 与 __all__ 含 ActivityLease，字段增删不改变该模块行为，无需复核变更。

## 五、迁移约束逐项清点（第 4 项，列级/表级，不作合计口径）

004_activities_time_budget.sql 实际约束清点（不采用"五列+四条约束"的合并口径）：
CHECK 共 8 条：
- 列级 5：activities_max_running_seconds_check（>0 AND <=2147483647，第 21–22 行）；
  activities_running_reserved_seconds_check（>=0，第 23–24 行）；
  activities_running_settled_seconds_check（>=0，第 25–26 行）；
  activities_last_settled_generation_check（IS NULL OR >=0，第 27–28 行）；
  activities_last_settled_seconds_check（IS NULL OR >=0，第 29–30 行）。
- 表级命名 3：activities_time_budget_balance（R <= M − S，第 35–38 行）；
  activities_time_budget_running_shape（(status='running') = (R>0)，第 41–44 行）；
  activities_time_budget_last_settled_pair（(gen IS NULL) = (sec IS NULL)，第 47–50 行）。
非 CHECK 约束：NOT NULL 3 条（max_running_seconds、running_reserved_seconds、running_settled_seconds）；DEFAULT 0 两条（R、S）。
新增列 5：max_running_seconds、running_reserved_seconds、running_settled_seconds、last_settled_generation、last_settled_seconds。

## 六、命令与边界记录

本轮执行：只读读取（Read/Grep）、托管 Python hashlib 计算 8 个文件 SHA-256、创建 Ndocu/evidence/task-078/review-03/ 目录、写入本目录 2 个证据文件与 Ndocu/results/TASK-078-result.md 置顶段落。
未执行：PG、Docker、迁移、compile、unittest、构造脚本重跑、应用启动、联网安装、真实模型调用、密钥/配置读取、Git 操作。
写入范围：仅 Ndocu/evidence/task-078/review-03/ 与 Ndocu/results/TASK-078-result.md；正式 docu/、公共库、源码、测试、迁移、旧证据均未改动。
