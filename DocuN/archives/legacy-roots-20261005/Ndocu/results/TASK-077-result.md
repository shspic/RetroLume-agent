# TASK-077 / R-071 修正轮02（2026-09-23，当前有效，置顶）

执行者：WorkBuddy 执行 Agent（实际客户端/模型如实登记见第一节，**非** Codex Sol）。未续用原实现窗口（本机不可达原窗口）；未重做首轮实现，未重做修正轮01，非独立审计。
口径：需求 v1.1、架构 v0.28、执行状态 v1.28；STEP-008 仍进行中/部分验证；关联 076、078/review-02 N1、NFR-002/003、SEC-002、FLOW-005、DATA-007。

结论：N1 修正完成并通过本轮最小验证。`ActivityLease` 在 `lease_expires_at` 之后新增必填 `window_seconds: int`，与 claim 成功路径六位置参数顺序一致；一次真实数据类构造检查通过（exit=0，0.53s），确认 `window_seconds==79`、前五字段按位置保留、`frozen=True` 与必填语义仍生效。repository.py 新 hash `045a3cf8…2534`；其余五文件 hash 与冻结值逐项一致，未改动。D1/D2/O1 按其 revision-01 快照原样保留。

## 一、实际执行身份（如实登记，偏差披露）

- 实际客户端/窗口：WorkBuddy（CodeBuddy）桌面客户端执行 Agent 会话；**未**续用 TASK-077 原实现窗口（原窗口在本机不可达，无可用续接证据）。
- 实际底层模型：DeepSeek-V4.1-Flash（本会话运行时自报底座）。
- **偏差 D-R02-1**：与卡面指定（Codex Sol，C 强档）不一致。本轮不以 Sol 身份签发任何结论，不冒用指定模型身份；C 档在本轮仅体现为"限域单字段改动 + 一次最小构造验证"，**是否满足原强档要求由编排裁决**。如需 Sol 强档窗口复核或重做，由编排另派窗口。
- 审计侧限制继续有效：TASK-078 review-02 实际模型为 GLM-5.3-Flash，与指定 Sol 不一致，其有效发现保留，但本实现窗口**不**补签任何强档独立审计结论。
- 本轮无并发写入、无 EBUSY、无不明漂移：六文件改前 hash 与卡面冻结值逐项相符。

## 二、N1 修正范围（唯一必要改动）

1. `backend/app/activities/repository.py` 第 76 行之后新增一行 `window_seconds: int`（位于 `lease_expires_at: datetime` 之后），与第 383—390 行 `return ActivityLease(activity_id, executor_id, generation, row["scope_revision"], lease_expires_at, effective_window)` 的六个位置参数一一对应，调用方可读取实际预扣 `W_eff`。
2. 保留 `frozen=True`；未加默认值（字段仍必填）；未截断成功路径实参；未改事务、锁序、分支、SQL、迁移、`__init__.py` 导出；未新增第 6 列。
3. 未发现仍须改动其他产品逻辑的情形，未顺手扩围。
4. D1/D2/O1 保留证明：`test_activity_time_budget.py`、`test_activity_recovery.py`、`004_activities_time_budget.sql` 三文件本轮 hash 与冻结值完全相同（UNCHANGED）。

## 三、命令与客观证据（Ndocu/evidence/task-077/revision-02/）

1. **改前冻结核对**：六文件 SHA-256 与卡面冻结值逐项一致，无漂移 → `pre/pre_hashes.json`、`pre__repository.py`（42957 字节 / 904 行）。
2. **运行前导入副作用静态确认**：`app/__init__.py` 为空；`repository.py` 仅在 `_transaction` 内惰性 `import psycopg`；repository.py 与 `app.capabilities` 依赖模块顶层无 `connect` / `getenv` / `environ` / `open` 调用 → 判定直接导入路径无连接副作用，脚本以**实际导入**执行（未改业务、未绕过）。
3. **真实构造检查**（本轮新增增量额度，单批 0.53s，未达 60s 上限）：
   - 命令：`cd D:/shspic/project_NO3_RetroLume-agent/backend && .venv/Scripts/python.exe -B ../Ndocu/evidence/task-077/revision-02/check_activitylease_contract.py`（`PYTHONPATH=backend`、`PYTHONDONTWRITEBYTECODE=1`）
   - `exit_code=0`，`elapsed=0.53s`，被测 hash `045a3cf8…2534`，stderr 为空，`__pycache__` 前后一致（未写 pyc）
   - 关键输出：
     - `[fields] ['activity_id','executor_id','execution_generation','scope_revision','lease_expires_at','window_seconds']`
     - `[annotation] window_seconds -> 'int'`；`[frozen] True`；`[frozen_enforced] FrozenInstanceError raised as expected`（且无类属性默认值 → 必填）
     - `[constructed] ActivityLease(..., window_seconds=79)`
     - `[call_site_line] 383`；`[call_args] ['activity_id','executor_id','generation','row["scope_revision"]','lease_expires_at','effective_window']`
     - `[RESULT] PASS window_seconds==79 positional_contract_ok`
   - 证据：`construct_check.log`；脚本 `check_activitylease_contract.py`（仅导入产品数据类，未复制、未 mock、未实例化仓储、未连 DB、未读配置/密钥）
   - 首次执行即通过，**未使用**"至多一次复检"额度。
4. **六文件改后 hash 与差异**：`post_hashes.txt` / `post_hashes.json` / `diff_revision02_repository.txt`
   - repository.py：`33b733e66fcabb7a86edf9c6080051c55ecb1294042d60b6afa176a13dffa57e` → `045a3cf8b1c81d7a1336c3bd2e90e891e4e53934027c9fea9727fafde7202534`（单 hunk，+1 行 / −0 行）
   - `__init__.py` = `6bdb9609…46dd`、`004_activities_time_budget.sql` = `8f04f57c…97cc`、`test_activity_time_budget.py` = `63a19d1f…1a86`、`test_activity_ledger.py` = `fb174d4c…63da`、`test_activity_recovery.py` = `0e5d9c89…bf7a`：post 与 pre 逐项相同 → UNCHANGED
   - 证据导航：`revision-02-scope-and-evidence.md`

## 四、未验证项（not_run）与限制

1. 本轮构造成功**只关闭 N1 构造缺口**：不证明 claim 事务、SQL、锁序、余额不变量或任何数据库行为；不得据此宣称"claim 通过"或"真实 PG 通过"。
2. 未运行：PG/数据库、004 迁移、unittest 套件、time_budget 八例、ledger/recovery 旧用例、Docker、应用服务、真实模型、EXPLAIN、并发与时钟回拨实验；未安装、未联网、未读 DSN 或环境密钥、未 Git 操作（本仓非 Git 仓库，未初始化未提交）。
3. N1 的两个运行时触发路径（普通认领、折叠后部分窗口认领）仍未在真实 PG 上执行；`_transaction` 不转换该异常的判断同样未动态验证。
4. **冻结轮换**：repository.py 新 hash `045a3cf8…2534` 取代卡面冻结值，后续改动卡/审计卡须以新值起算；078/review-02 PG 清单的"前置门"仅解除**代码层**缺口，PG 运行额度仍为 0、原 13 元费用额度仍耗尽。
5. 本轮结果不构成 M-1、STEP-008 或时间监督完成；不填编排最终验收。

## 五、风险与文档建议

1. 风险（继承，未新增）：新增字段在 `lease_expires_at` 之后，外部若按位置解包 5 个字段将受影响；已静态确认本仓仅 repository.py 一处构造点、无测试构造该类型，风险限于仓外未知调用方。
2. 文档建议：在架构/执行状态中把"ActivityLease 返回字段清单"与 004 五列并列登记为受控返回契约，并注明 `window_seconds` = 实际预扣 `W_eff`（既非请求值、也非墙钟测量）；执行状态记录 repository.py 冻结 hash 已轮换至 `045a3cf8…2534`。
3. 文档建议：TASK-078/review-02 的 N1 条目标记"代码层已修复，待独立复核 + 定向 PG"，避免下游把缺口状态读成仍开放。

## 六、下一步（交编排，不由本窗口执行）

1. 裁决身份偏差 D-R02-1（指定 Codex Sol 不可用）：是否需强档窗口复核本轮一行改动。
2. 按 078/review-02 第四节清单出定向 PG 运行卡；代码层前置门已满足，运行额度需另行批准。

---

# TASK-077 / R-071 执行结果（回传 Astra）

执行者：Codex Sol（C档强档，新会话）；日期 2026-09-22；父 TASK-076，关联 075/071/072/074、NFR-002/003、SEC-002、FLOW-005、DATA-007。
建议状态：候选，待 Astra 验收。不宣告 M-1 或 STEP-008 完成；真实 PG/迁移验证未执行。

---

# 修正轮01（2026-09-22，接续原实现窗口）

执行者：Codex Sol（C档强档）；原窗口续用，未新开任务、未重做首轮实现、未重复消费首轮检查预算。客户端/模型标签：Codex Sol C 强档（与本轮任务卡口径一致）。本轮无在途并发任务冲突，无 EBUSY/漂移事件。

## 结论

TASK-077 / R-071 / 修正轮01 完成。D1、D2、O1 三项修正及同点遗漏适配全部落实；三份冻结文件（repository.py、__init__.py、test_activity_ledger.py）与 001/002/003、正式 docu、公共库、旧证据均未改动；两份修改的 Python 测试文件 compile 通过；004 候选 DDL 未执行。004 与真实八例及受影响旧测试仍标未运行（not_run）。

## 本轮三文件实际差异

1. D1（test_activity_recovery.py，test_04）：
   - 第二个 ActivitySpec（`other`，原 284 行起）补 `max_running_seconds=3600`，与 build_activity 口径一致。
   - `other_lease` 的 claim_lease 调用（原 301 行）补必填 `window_seconds=300`，并在传给 intent 前新增 `self.assertIsNotNone(other_lease)`（原调用确实会因缺参数 TypeError，未只修构造）。
   - 静态确认：本文件全部 5 处相关调用（2 处 ActivitySpec 构造、3 处 claim_lease）均符合既有合同；创建前登记 extra_activity_ids、FK 清理顺序、原业务断言全部保留，未扩大业务修改。
2. D2（test_activity_time_budget.py，test_08）：
   - 用例改名：`test_08_ceiling_rounding_zero_and_budget_exhaustion` → `test_08_ceiling_rounding_zero_and_fold_reclaim_partial_window`（新旧行为映射：原"过期折叠后预算耗尽返回 None"断言按 TASK-078 审计算术更正为"折叠后仍可取得部分窗口租约"）。
   - 保留原数字与前序检查：M=200、向上取整 20.2→C21、C=0、有效租约不被抢占冲突检查、未知活动冲突检查全部不动。
   - 过期折叠后改为断言成功取得租约：window_seconds=79 且非 None；S=121、R=79、M=200、可用余额 M-S-R=0、status=running；租约身份/代次与行一致（execution_generation、executor_id 与返回 lease 相等），未硬编码 generation 数字。
   - 未改实现迎合错误预期；真实耗尽 None 及关闭已提交路径仍由 test_04 完整覆盖（第 217/233 行 None 断言未删除未降低）。
3. O1（004_activities_time_budget.sql）：
   - `last_settled_generation` 增加 CHECK (IS NULL OR >= 0)，保持 INTEGER 类型；五列、成对 NULL 约束、余额/running 形状约束、锁内判空、事务结构、非空拒绝均未动；无第六列，未以应用验证替代 DB 域约束。仅改候选 DDL，未执行。

## 本轮证据导航（Ndocu/evidence/task-077/revision-01/）

- pre_hashes.txt：改前六文件 SHA256，与任务卡六项冻结/目标 hash 全部一致，无漂移。
- pre__004_activities_time_budget.sql / pre__test_activity_recovery.py / pre__test_activity_time_budget.py：三文件改前快照（不覆盖首轮 pre）。
- diff_revision01.txt：三文件统一 diff（含改后 SHA256）。
- compile_post.txt：两份修改的 Python 测试文件 compile 证据。
- post_hashes.txt：改后六文件 SHA256；三份冻结文件与改前完全一致。

## 本轮实际执行的命令

1. 冻结核对：backend/.venv/Scripts/python.exe 内联 hashlib 脚本计算六文件 SHA256 → 与卡内一致，exit=0。
2. compile 检查：同一解释器读取源码后 compile(src, rel, 'exec')，不 import、不写 pyc，单批两文件、耗时 <0.001s，输出 COMPILE_OK×2，exit=0（一次性通过，未复检）。
3. diff 生成与六文件改后复核：difflib 统一 diff + 改后 SHA256 复核，exit=0。

## 本轮检查及未运行项（not_run）

- 已做：三文件差异/参数/断言/DDL 域一致性一次检查；recovery 文件全部构造/claim 调用点静态确认（5/5 合规）。
- 未运行：004 迁移未执行；unittest/PG/迁移/Docker 未运行；未复现已知 TypeError（按卡禁止）；未重测 055/074、未重跑首轮 compile 与旧 074 PG 证据；无新增 mock/SQL 字符串匹配测试；无 DSN skip 冒充通过。

## 本轮风险与文档建议

- 风险：D2 修正后的折叠部分窗口路径（W_eff=min(W,A)=79）与 D1 适配仍未经真实 PG 行为确认，与首轮同属候选状态；语法通过不宣称用例或 SQL 通过。
- PG 验证建议（并入后续真实 PG 卡）：对 004 增加反例/正例——`last_settled_generation=-1 且 last_settled_seconds=0` 必须被 CHECK 拒绝；`NULL/NULL` 与 `0/0` 必须合法入库。无需为此新建运行框架。
- 编排侧：修正回收后另行安排必要独立复核及 PG；本窗口未补签审计，TASK-078 资格不受影响，不能据此关 M-1 或 STEP-008。

---

# 以下为首轮合同执行结果（历史保留，仅供追溯）

## 一、文件差异（新旧 SHA-256）

修改：
- backend/app/activities/repository.py  50ec537b07533c68194651b008d275176430effeb67126391ef43b96155cfce6 → 33b733e66fcabb7a86edf9c6080051c55ecb1294042d60b6afa176a13dffa57e
- backend/app/activities/__init__.py  31d0b60cfc644c797a04fb31e9c3a4da242969abbe0e5b54648b1d18f19f1d2a → 6bdb960912ea3fc7ddd8730f37a44e580b73768e1067d23facc9983ca04a46dd
- backend/tests/test_activity_ledger.py  0eb878cbe2fe282257e76b73b7a930163e18877c9bfe9fa4e58255d204730c9e → fb174d4c29355bb0e57ac013d4e8555ef9ac342e9be804e0edbf732112de63da
- backend/tests/test_activity_recovery.py  7839af04e3043a173f8caaeefd5085ff72e138891207a0e882d8b2ef585d15e4（冻结核对一致）→ 93ab4e2c5a481dc7b880ef7c8e696b9ac4981e7e52938b095f12a8fb8ebd3cba

新增：
- backend/migrations/004_activities_time_budget.sql  1501e1f1dd38770eceaf26430882a62e9bac8fdfec41d6303c8531ef0654db6b
- backend/tests/test_activity_time_budget.py  a4e3070eb2137da8feb28a67161f391bd9568264189410cf97c52f966bea5ab4

证据：Ndocu/evidence/task-077/（pre/ 四文件副本+hashes-pre.txt；compile_check_077.py；compile-check.txt；hashes-post.txt）。001/002/003、gateway/transport/HTTP/main/runtime、依赖锁、正式 docu、旧证据均未动。

## 二、字段/签名/返回语义实际清单

### 004 迁移（只写未执行）
- activities 五列：max_running_seconds BIGINT NOT NULL CHECK(>0 AND <=2147483647)；running_reserved_seconds BIGINT NOT NULL DEFAULT 0 CHECK(>=0)；running_settled_seconds BIGINT NOT NULL DEFAULT 0 CHECK(>=0)；last_settled_generation INTEGER 可空；last_settled_seconds BIGINT 可空 CHECK(>=0 或 NULL)。
- 表级约束三条：activities_time_budget_balance（R <= M - S，减法写法，BIGINT 非负域内不可溢出）；activities_time_budget_running_shape（(status='running') = (R>0)，即 running 当且仅当 R>0）；activities_time_budget_last_settled_pair（两最近结算列成对 NULL/成对非 NULL）。
- 流程：BEGIN → LOCK TABLE activities IN ACCESS EXCLUSIVE MODE（先锁后判空，无并发写入窗口）→ DO 块内 PERFORM 判空，非空 RAISE EXCEPTION 整笔回滚 → ALTER TABLE ADD COLUMN/CONSTRAINT → COMMIT。002 不变；仅空 activities 合成库；无自动免费默认、无无限预算。

### repository.py
- ActivitySpec：新增必填 max_running_seconds: int（dataclass 必填字段，缺失在构造时 TypeError）；_validate_spec 拒绝 bool/非 int/<=0/>2147483647，ValueError。create_activity INSERT 显式写 M 及 R=S=0。
- ActivityLease：新增必填 window_seconds: int = 实际预扣 W_eff；docstring 明示 W_eff/租约长度/墙钟不构成实际单调耗时保证。
- 新增 SettleResult 枚举（SETTLED / ALREADY_SETTLED），已从 app.activities 导出。
- claim_lease(activity_id, executor_id, *, lease_seconds, window_seconds) -> ActivityLease | None：
  - lease_seconds 原限制保留（1—3600）；window_seconds 必填，bool/非 int/1—3600 外 ValueError。
  - None 唯一含义＝"未获得新租约：时间预算耗尽"；未知活动/来源失效/已取消或过期/有效租约冲突仍为 ActivityLedgerConflict，可区分。
  - 原准入条件先校验；A=M-S-R，W_eff=min(window_seconds,A)；过期 running 租约接续时先全额折叠 R→S、清零、关闭旧代次资格；已结算 pending/R0 窗口不折叠。
  - 代次递增三路径（各一次，无硬编码示例值）：成功认领（含折叠）+1，折叠与新租约同一 UPDATE 原子；折叠后 A=0 → 提交关闭（pending、executor/lease 清空、代次失效）+1 并返回 None，不以事务内异常回滚；已是 pending 且 A=0 → 不写行、不递增，直接 None。
- settle_execution_window(activity_id, executor_id, execution_generation, *, window_seconds, elapsed_seconds) -> SettleResult：
  - 参数校验：activity UUID/executor 格式；execution_generation 非负 int（拒 bool）；window_seconds 1—3600（拒 bool）；elapsed_seconds 有限非负数（拒 bool/NaN/±inf/负）；C=ceil(elapsed_seconds)，0 仅真实零耗时；C>W 拒绝（ValueError），不钳制。
  - 正常路径：running + executor/代次匹配 + R==W（运行态预扣等于所报窗口）；原子 S+=C、R=0、generation+1、pending、executor/lease 清空、写 last_settled_generation/seconds；返回 SETTLED。
  - 幂等（受限确认，先于运行态检查，已关闭状态不拒绝合法重试）：最近已结算 G 相同且 C 相同 → ALREADY_SETTLED 不改账；相同 G 不同 C → 冲突拒绝不改账；更旧/未知 G → 冲突拒绝不改账。确认分支的 executor/W 仅格式校验，不回放历史、不授予执行资格。响应丢失按持久事实重试即 ALREADY_SETTLED，不重新折叠/退款。
  - 无外部路由；不提供停止证明、不等于准许生产退款；生产组合保持未接线。
- cancel_activity：按既有锁序/幂等；真实在途 R 全额转 S、R=0、取消终态及代次失效；重复取消直接返回当前代次不重复扣账；模型次数/费用预留不动，旧操作不重发。
- 未修改：list/recover/admit/mark/record 主体、时钟、恢复器（074 复用）。

### 测试适配与新增
- test_activity_ledger.py / test_activity_recovery.py：仅适配 ActivitySpec 必填（max_running_seconds=3600）、claim 增 window_seconds=300、认领结果 isNotNone 检查；业务断言与 069 定向 FK 清理原样保留。
- test_activity_time_budget.py（新增，未运行）：DSN 取 RETROLUME_TIME_BUDGET_TEST_DATABASE_URL，缺失明确 skip，绝不回退用户 DSN；每例合成 ID 定向清理；租约过期样本用合成行 lease_expires_at 数据值，不改系统时间、不称真实回拨实验。八个用例覆盖：M200/W100/C20→S20/R0 及幂等/冲突重试；已结算后新认领不折叠；过期残留全额折叠；折叠耗尽返回 None 且关闭已提交（含二次 None 不写行）；取消/重复取消；旧代次晚到与执行者不匹配拒绝及当代幂等；参数非法（spec M/claim W/settle elapsed·window·代次/C>W）与未知活动冲突；向上取整 20.2→21、C=0、有效租约不被抢占、耗尽 None 与冲突可区分。

## 三、事务/接口/边界

- 锁序不变：来源 UUID 排序→活动→操作；claim/settle/cancel 均单短事务；网络调用不入事务。
- settle 幂等分支置于运行态检查之前，已关闭（pending/cancelled）状态不拒绝合法重试；判断与事务锁一致（FOR UPDATE 后读行）。
- 折叠耗尽路径提交关闭后返回 None，无"回滚后虚称已关闭"。
- 无第 6 列、无额外服务、无 worker/HTTP/模型接线、无主要模型变化；未出现迫使其他接口改变的不变量冲突。

## 四、实际执行的命令与结果

1. 冻结 hash 核对（PowerShell Get-FileHash，改动前）：repository.py=50ec537b…cfce6、recovery 测试=7839af04…d15e4，均与卡内一致。
2. compile 检查：backend/.venv/Scripts/python.exe Ndocu/evidence/task-077/compile_check_077.py → 输出 COMPILE_OK 5，exit=0。compile() 内建函数逐文件编译，不写 pyc。
   - 首次尝试经 PowerShell -c 内联传参，因 PS 5.1 原生参数内嵌双引号截断而 SyntaxError（非代码问题）；改脚本文件方式后通过。
3. 一次一致性检查：重读全部改动区段，核对调用位置（claim/settle 调用方仅测试文件，无产品接线）、不变量（R+S<=M 在 claim/settle/cancel 三路径均保持；running iff R>0；代次三路径递增规则）、锁序。通过。

执行事件（如实记录）：claim_lease/settle 大段编辑首次应用成功后，因文件锁竞争（EBUSY）该区段被旧内容覆盖丢失；发现后依据 grep 证据重做该编辑，并按卡内"有明确修正依据最多一次复检"重跑 compile（COMPILE_OK 5，exit=0）与通读核验。其余编辑未受影响。

## 五、未验证风险（not_run）

- 004 迁移未执行；非空拒绝与三条 CHECK 的数据库端真实行为未验证（按卡留给真实运行验证）。
- 三个测试文件均未运行（无真实 PG；unittest 未执行）；无 SQL 字符串断言/mock 冒充事务验证。
- 旧两测试文件（048/068 DSN）未来真实运行需在已应用 004 的合成库上执行（claim 现写 R/S 列）。
- 幂等/折叠/取消语义仅有静态一致性核对，未经真实 PG 行为确认。
- 不宣称 M-1、监督、跨重启实际运行时长受控。

## 六、文档建议（Astra 维护）

- 架构批准增量（v0.26 时间账本基础切片）对应实现已落地为候选；可在执行状态登记本卡结果与后续验证缺口。
- 后续建议两卡：① 真实 PG 验证卡（004 迁移执行 + RETROLUME_TIME_BUDGET_TEST_DATABASE_URL 专用合成库 + 三测试文件运行，含旧两文件回归）；② 独立强档审计卡（仅覆盖实际影响：五列、claim/settle/cancel 事务与幂等语义、004 DDL）。
- 代码内 docstring 已完整记录两路径代次递增规则与受限幂等边界，无需另建文档。

## 七、必要人工操作

无。本卡不需要用户执行操作；真实 PG/迁移由 Astra 另卡编排。

## 八、下一步

交回 Astra 验收本结果；通过后安排上述真实 PG 验证卡与独立审计卡。不填 Astra 最终验收，不宣告 STEP-008 完成。
