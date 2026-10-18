TASK-078 / R-072 review-03 增量独立复核结果（本轮有效，置顶）

TASK-078 / R-072；独立只读增量复核（非全面重审）；STEP-008 局部；父 TASK-077，关联 076/072/074、NFR-002/003、SEC-002、FLOW-005、DATA-007。
执行窗口：承接 review-02 原 Work Buddy 独立审计窗口；本窗口自报标识 DeepSeek-V4.1-Flash（review-02 自报 GLM-5.3-Flash，按用户 2026-09-23 指示如实记录、不因此重审）。
日期：2026-09-23。口径：需求 v1.1、架构 v0.29、执行状态 v1.30。
证据目录：Ndocu/evidence/task-078/review-03/（hash_current.txt、review-03-scope-and-findings.md）。
范围界定：本轮只作答 N1 修复增量、hash 适用性、代码层结论更新与 PG 清单差异四问；不重跑 review-02 已完成的八项审查，不重复采集未变证据。

总结论（代码层）：有条件通过。
唯一条件：定向 PG 动态验证尚未执行（清单见第五节）。review-02 的唯一阻断缺陷 N1 已在当前快照关闭。

一、N1 结论：已关闭（静态确认，非动态通过）

1. 定义：backend/app/activities/repository.py 第 70–77 行，@dataclass(frozen=True) 保留，window_seconds: int 位于 lease_expires_at 之后（第 77 行），无默认值（必填）；字段序列与合同一致。
2. 增量边界：revision-02 diff 全文仅一个 hunk（@@ -74,6 +74,7 @@），+1 行 / −0 行，仅字段新增，无 SQL、无事务边界、无其他文件改动。
3. 位置一致性：全仓 *.py 中 ActivityLease 构造点唯一（repository.py 第 383–390 行，六位置实参：activity_id、executor_id、generation、row["scope_revision"]、lease_expires_at、effective_window），与六字段顺序逐位对应；第 6 实参即 W_eff = min(window_seconds, available)。N1 的"多余位置参数"触发条件消除，未引入新错配。
4. 构造日志（复用，未重跑）：check_activitylease_contract.py 真实导入产品数据类并自算被测 hash；construct_check.log 的 [hash_under_test] 与 [hash_under_test_after] 均为 045a3cf8…2534（= 当前冻结值，运行期未变），exit_code=0，pycache 未写，[RESULT] PASS；断言覆盖字段顺序、注解 int、frozen=True、无默认值、六位置参数构造、window_seconds==79、前五字段逐一相等、FrozenInstanceError、调用点第 5/6 实参名称。
5. 适用范围界定：上述 1–4 只证明构造契约与修复增量形态，**不证明** PG 可用性、锁行为或真实认领成功，不构成动态通过。

二、当前快照与原证据适用范围

1. 本轮独立重算（托管 Python SHA-256，见 hash_current.txt）：六文件与卡面冻结值逐项一致，无漂移。repository.py = 045a3cf8b1c81d7a1336c3bd2e90e891e4e53934027c9fea9727fafde7202534（已轮换，修复后）；其余五文件 hash 与 review-02 时相同。
2. 链证：revision-02/pre__repository.py 的 hash = 33b733e6…ffa57e，与 review-02 记录的被审快照值一致 → 修复增量确实落在 review-02 所审基线之上。
3. 适用性结论：未变五文件（__init__.py、004 迁移、time_budget/ledger/recovery 测试）沿用 review-02 的结论与证据，不重复采集；repository.py 的相关结论中，凡不依赖 N1 的部分（分支逻辑、折叠算术、锁序、settle/cancel、调用路径影响）继续有效，凡以 N1 为唯一不通过理由的标准 3 判定按第三节更新。
4. 首轮（轮次 01）与 review-02 的证据目录与结论原文全部保留，未删除、未改写。

三、原代码层结论如何更新

1. 标准 3（claim 分支）：由"不通过——仅因 N1"更新为"符合（静态）"。依据：review-02 已独立复核的分支逻辑未受影响（本轮 diff 证实无逻辑改动），其唯一不通过理由已消除。
2. 标准 1、2、4、5、6、7：结论不变，维持 review-02 判定（标准 1/2/4/5/6 符合；标准 7 符合，含修正后 D1/D2 已满足原合同的确认）。
3. 已确认项继续有效：D1（recovery test_04 补 max_running_seconds 与 window_seconds 并断言非 None）、D2（time_budget test_08 改名与 79 结算算术）、O1（004 last_settled_generation 非负 CHECK 落地）三处修正均维持"满足原合同"。
4. 综合：由"不通过（当前代码层）"更新为"有条件通过（当前代码层）"，条件仅为 PG 动态验证缺口。不宣称 PG、迁移、M-1 或 STEP-008 通过。

四、独立性与实际身份

1. 本窗口未参与 TASK-077 修正轮02：本轮与 review-02 轮对本项目源码均为只读，无写入痕迹。
2. 已披露的间接接触面：本项目记忆文件 .workbuddy/memory/MEMORY.md 载有修正轮02 的执行记录（N1 修复位置、hash 轮换、偏差 D-R02-1）；该记录来自项目记忆文件而非本窗口执行。本窗口未读取 TASK-077 结果文档、自评或实现聊天。
3. 残余不确定性：无法从文件层完全排除"同一客户端多会话"的可能；就机制而言，本窗口未持有实现过程推理上下文，本轮判断仅由只读证据支撑。
4. 判定：独立性成立（附受限披露），签发代码层结论；不签发动态通过。
5. 型号登记：本轮 DeepSeek-V4.1-Flash；review-02 GLM-5.3-Flash。按用户指示如实记录，不作为重审理由，亦不据此重复审查已完成的合规工作。

五、最小 PG 验证清单（review-03 版，相对 review-02 的差异）

1. 前置门：由"N1 待修 + hash 待轮换"更新为**已满足**（repository.py = 045a3cf8…2534）；运行卡无 N1 前置障碍。
2. 迁移项改为逐项列级/表级清点（不再采用"五列+四条约束"的合并口径）：CHECK 共 8 条——列级 5（max_running_seconds 上界下界、R 非负、S 非负、last_settled_generation 非负、last_settled_seconds 非负）、表级 3（balance、running_shape、last_settled_pair）；另有 NOT NULL 3 条、DEFAULT 0 两条。此为清点粒度细化，不改变 review-02 对任一约束的静态判断。
3. 迁移负例逐条覆盖：M=0 与 M=2147483648；R=−1；S=−1；last_settled_generation=−1（seconds 非空同写）；last_settled_seconds=−1；balance 反例 R>M−S；running_shape 两向反例（非 running 且 R>0；running 且 R=0）；pair 单列 NULL。正例：NULL/NULL 与 0/0 合法。另含空库成功、非空 activities 拒绝并全回滚、无部分 DDL。
4. 用例项保持 review-02 原样，不改名、不扩围：time_budget test_01–test_08（test_08 现名 test_08_ceiling_rounding_zero_and_fold_reclaim_partial_window）；ledger 8 例；recovery 6 例（test_04 经 D1 修正）。
5. 不要求项保持：并发压力、时钟回拨、崩溃恢复、worker、EXPLAIN、mock/通用框架扩建。

六、未验证与剩余门

1. 全部动态行为仍未验证：PG 执行、004 迁移真实运行、CHECK 实际拒绝、锁等待与并发；迁移未运行。静态正确不等于真实通过。
2. 未执行 compile / unittest / 构造脚本重跑 / Docker / 应用启动 / 联调；构造结论取自现成日志（已核对 hash 绑定与断言覆盖）。
3. 本卡 PG 额度 0，未申请任何运行；旧尝试与 13 元费用预算未重置。
4. 不得以本结论宣称 PG、迁移、M-1 或 STEP-008 通过；本轮不填写编排最终验收。

七、下一步

1. 按第五节清单出定向 PG 运行卡（迁移项按 8 条 CHECK 逐项验证）。
2. 编排据本结论更新架构/执行状态中的 078 条目与 DATA-007 状态。

---

# 历史轮次 02（review-02，2026-09-22；原文保留，其"本轮"均指该轮）

TASK-078 / R-072 补审轮 review-02 独立代码审计结果（本轮有效，置顶）

TASK-078 / R-072 补审轮；独立只读代码审计；STEP-008 局部；父 TASK-077，关联 076/072/074、NFR-002/003、SEC-002、FLOW-005、DATA-007。
审计者：Work Buddy 执行 Agent（模型自报标识 GLM-5.3-Flash；未配置/未使用 API 密钥）。全新隔离会话，未参与 077 实现，未使用 077 实现窗口。
日期：2026-09-22。口径：需求 v1.1、架构 v0.27、执行状态 v1.27。
证据目录：Ndocu/evidence/task-078/review-02/（hash_current.txt、hash_migrations_001_003.txt、review-02-scope-and-findings.md）。
原轮有效发现与证据全部保留（见下方历史轮次）；本轮为补齐强档资格与修正快照的新增审计轮，不重审未受影响模块，未重复采集未变证据。

总结论（代码层）：不通过（当前代码层）。
原因：新发现一个产品代码确定缺陷 N1——ActivityLease 数据类缺 window_seconds 字段，而 claim_lease 成功路径以 6 个位置参数构造该类，任何成功认领运行时必抛 TypeError，违反合同"ActivityLease 增加 window_seconds 字段"的返回契约（审查标准 3 不满足）。N1 为静态可定位的一行修复：在数据类 lease_expires_at 之后新增字段 window_seconds: int（与第 382–389 行返回参数顺序一致），修复后本轮其余各项可达"有条件通过"并进入定向 PG。原轮 D1/D2/O1 三个修正确认全部满足原合同。本结论不宣告任何动态通过：迁移未运行、真实 PG 未验证、CHECK 未实测；不宣告 M-1 解决或 STEP-008 完成。
冻结 hash：六文件与卡面一致，无漂移；revision-01 差异 post-hash 与当前逐项一致，旧差异证据适用；001/002/003 本轮补算全量 hash 前缀与首轮记录一致（旁证补强）。

一、三个修正的增量确认（均满足原合同）

1. D1（recovery test_04）：第二 ActivitySpec 已补 max_running_seconds=3600（现第 293 行）；other_lease 调用已补 window_seconds=300 并在传给 intent 前 assertIsNotNone（现第 302–305 行）。创建前 extra_activity_ids 登记、FK 清理、隔离/分页业务断言全部保留。同文件 build_activity/reclaim_next_generation 的构造/claim 调用均符合合同，无扩大业务修改。
2. D2（time_budget test_08）：已改名 test_08_ceiling_rounding_zero_and_fold_reclaim_partial_window。算术独立复核：M200；20.2→C21（S=21）；零秒结算 C0（last=0、S=21）；第三窗 R100 过期折叠→S121，A=200−121=79，新租约 W_eff=79 且 assertIsNotNone；断言 M=200、S=121、R=79、可用余额 M−S−R=0、status=running、代次/执行者与 DB 投影一致且不硬编码 generation。原前序向上取整/零秒/有效租约冲突检查与末尾未知活动冲突检查保留；真实耗尽 None 及关闭已提交仍由 test_04 覆盖。实现未被迁就修改。
3. O1（004 generation CHECK）：last_settled_generation 增加 CHECK（IS NULL 或 >=0，现第 27–28 行）；NULL/NULL 与 0/0 合法（成对约束+非负 CHECK）、−1/0 非法（gen CHECK 拒绝）。仍为五列、ACCESS EXCLUSIVE 锁内判空、同事务非空拒绝、无回填。首轮 O1 观察闭合。

二、逐项标准结论（标准 1—6 本轮独立判断；7 围绕修正；8 更新清单）

标准 1（五列 DDL 与 Python 域一致）：符合。逐列复核：M BIGINT CHECK (0<M<=2147483647) 与 _validate_spec 一致；R/S BIGINT 非负默认 0；余额约束 R<=M−S（减法写法，BIGINT 域内无求值溢出）；running 形状 (status='running')=(R>0) 与全部写路径（create/claim 成功/折叠耗尽/settle/cancel）逐一核对一致；最近结算两列成对 NULL 且 seconds/generation 均 NULL 或非负（O1 修正后）。nullable 表达"未结算"保留，非法已结算值被 DB 拒绝。Python 侧 S 增量（折叠 R、结算 C<=W<=3600）受 DB CHECK 兜底，无溢出路径。
标准 2（004 事务与边界）：符合（静态）。BEGIN→LOCK TABLE activities IN ACCESS EXCLUSIVE→DO 块判空→非空 RAISE 使整个事务含 DDL 全回滚；无回填、无用户库写。001/002/003 旁证见证据记录。不据静态 DDL 宣称迁移已运行。
标准 3（claim 分支）：不通过——仅因 N1。分支逻辑本身独立复核符合合同：锁序来源→活动不变；取消/过期/有效租约冲突保留；folds_residual 仅 status='running' 且 R>0（已结算 pending/R0 不折叠）；折叠与新租约同一 UPDATE 原子、每路径代次恰 +1；折叠耗尽提交关闭（pending、executor/lease 清空、R=0、S=折叠值，由不变量 S+R=M 保证 balance 约束等式成立）后返回 None，无异常回滚；pending 且 A=0 不写行不递增；W_eff=min(window, A)；None 与冲突异常可区分。
标准 4（settle）：符合。事务外校验完整（bool/NaN/无穷/负数/C>W 拒绝不钳制）；锁内先判受限幂等再判运行态（关闭后重试不被状态先拒）；相同 G 异 C 拒绝、更旧/未知 G 拒绝且不改账；UPDATE 原子 S+=C、R 整窗清零（R==W 已验证）、代次 +1、写最近 G/C；S+C<=M 由 C<=W 与旧不变量保证，CHECK 不误伤；NULL last_settled_generation 不会与整数代次误配。
标准 5（幂等与取消竞争）：符合。cancel 在 FOR UPDATE 锁内幂等；UPDATE 的 S=S+R、R=0 取旧值语义恰好转出一次；重复取消返回同代次不改账；次数/费用预留与 UNKNOWN 纪律未动；五列不保存历史 executor/W 为已批准契约。
标准 6（未顺手改写与调用路径影响）：符合。首轮 diff 与 revision-01 diff 合并核对，生产改动仅限合同范围；list/recover/admit/mark/record 主体零变化。claim/cancel 的代次递增使旧代次操作自然落入 recover_obsolete_operations 既有收敛路径；admit 判定不引用新列。传导影响：N1 使一切成功认领在运行时失败，属标准 3 缺陷的传导，非本标准回归。
标准 7（测试准备）：符合（修正后）。三文件均真实调用仓储；专用 DSN 缺失明确 skip、不回退用户 DSN；定向 FK 清理正确且失败如实抛出；budget_row 九列投影覆盖全部断言字段；revision-01 对三文件改动仅必要参数/None 检查。新八例对关键分支（正常/幂等/不折叠/折叠/耗尽/取消/晚到/参数/取整零秒部分窗口）覆盖完整。非阻塞观察（不升级为门槛）：test_08 第三次 claim 未显式 assertIsNotNone，由其后"有效租约冲突"断言间接覆盖。
标准 8（最小 PG 验证清单）：见下节（含 N1 前置修复门）。

三、N1 缺陷详情（确定缺陷，产品代码，严重度高）

位置：backend/app/activities/repository.py 第 70–77 行（ActivityLease 定义 5 字段）与第 382–389 行（成功路径 6 位置参数构造）。
触发：任何成功返回租约的 claim_lease 调用（普通认领、折叠后部分窗口认领）。
影响：运行时 TypeError；_transaction 不转换该异常，原样抛出。即使截断构造参数，合同与测试（lease.window_seconds）仍要求该属性。依赖成功认领的全部 PG 用例在修复前必然失败；折叠耗尽 None 路径不受影响。
最小修复：数据类新增字段 window_seconds: int（置于 lease_expires_at 之后，与返回语句参数顺序一致），一行改动，不改其他逻辑。属产品代码改动，超出本卡写入授权，由编排另派修复窗口执行（注意 repository.py 冻结轮换与 hash 更新）。
与首轮报告的冲突披露：首轮报告标准 3 称"ActivityLease 新增 window_seconds 字段"、标准 6 称"ActivitySpec/ActivityLease 各一字段"，与其自产 diff-repository.txt（无该 hunk）矛盾，属首轮报告事实错误并漏检本缺陷。本轮判断在读取首轮报告之前已独立形成并留证（Grep+全文读取双确认），未受其影响。

四、最小 PG 验证清单（review-02 更新版）

前置门：先修 N1 并更新冻结 hash，否则本清单所有成功认领用例必 TypeError 失败，运行卡不得启动。
A. time_budget 八例（test_activity_time_budget.py，专用 RETROLUME_TIME_BUDGET_TEST_DATABASE_URL）：test_01 至 test_08 全部运行（test_08 为修正后名称）。
B. 004 迁移（真实运行，均为缺口）：
1. 空库执行成功，五列与四条约束（balance、running_shape、last_settled_pair、last_settled_generation 非负 CHECK）存在。
2. 非空 activities 执行拒绝且全回滚、无部分 DDL。
3. CHECK 负例至少各一：balance（R>M−S）、running_shape、pair（单列 NULL）、last_settled_seconds 负值、M=0 或超 2147483647、generation=−1 且 seconds=0；正例：NULL/NULL 与 0/0 合法（修正轮合同新增两例）。
C. 既有用例（依赖驱动，非机械全跑）：
1. test_activity_ledger.py 全部 8 例：均经 activity() 夹具依赖新 claim 签名与必填 M；test_05 直接覆盖修改后的 cancel（代次+1 与 R 折叠）。
2. test_activity_recovery.py 全部 6 例：均经 build_activity/reclaim_next_generation 夹具依赖新签名；test_04 为 D1 修复目标。说明：两文件全部用例确实均依赖修改后的夹具，属依赖驱动全覆盖，已按卡要求说明而非默认全跑。
D. 明确不要求：并发压力、时钟回拨、崩溃恢复、worker、EXPLAIN、mock/通用框架扩建。

五、未验证与剩余门

1. 全部动态行为未验证：PG 执行、004 迁移、CHECK 实际拒绝、锁等待、并发。静态正确不等于真实通过。
2. N1 未修复（本卡无产品代码写入授权）；修复窗口与 hash 轮换由编排安排。
3. PG 运行额度 0，原 13 元费用额度已尽，本卡未申请任何运行。
4. 不能以本代码结论宣称 PG/迁移、M-1 或 STEP-008 通过。

六、读取范围与独立性披露

按卡序读取：根入口（注入）、公共 AGENTS.MD、本卡全文（含末尾八项原始标准）、TASK-077.md 原合同与修正轮 01、六份被审文件全文、revision-01 三个 pre 快照存在性及 diff（post-hash 已核对适用）、首轮四份 diff 与 scope-and-hashes.txt。未读：TASK-077 结果文档、完整执行状态、交接聊天、实现者自评。原 078 结果在判断形成并留证后读取，仅用于续写保留历史与披露冲突，其结论未作为本轮证明。意外暴露：无。
命令仅 PowerShell New-Item/Get-FileHash；未运行 compile/unittest/PG/Docker/EXPLAIN/应用/模型调用，未联网安装、未读真实配置、未 Git 提交；写入仅限 review-02/ 证据与本结果文档置顶段。

七、下一步

1. 编排裁决：N1 一行修复窗口（产品代码，注意冻结轮换）→ 复核 hash → 按第四节清单出定向 PG 运行卡。
2. 本轮不填写 Astra 最终验收，不宣告时间监督或 STEP-008 完成。

---

# 历史轮次 01（首轮，2026-09-22，Work Buddy 其他模型执行；结论已被 review-02 部分修正）

TASK-078 / R-072 独立代码审计结果

TASK-078 / R-072；独立只读代码审计；STEP-008 局部；父 TASK-077，关联 076/072/074、NFR-002/003、SEC-002、FLOW-005、DATA-007。
审计者：独立审计 Agent（Work Buddy），全新隔离会话，未参与 077 实现，未读 077 结果、自评与执行聊天。
日期：2026-09-22。口径：需求 v1.1、架构 v0.27、执行状态 v1.23。
证据目录：Ndocu/evidence/task-078/（scope-and-hashes.txt、diff-repository.txt、diff-init.txt、diff-ledger.txt、diff-recovery.txt）。

总结论（代码层）：有条件通过。
产品代码三文件（backend/app/activities/repository.py、backend/app/activities/__init__.py、backend/migrations/004_activities_time_budget.sql）按八项标准逐项静态审查，未发现确定缺陷。存在两处测试准备确定缺陷（D1、D2，均不涉产品代码）：不修正则定向 PG 运行卡将出现一例夹具 TypeError 与一例必然误报失败。修正 D1/D2 后即可进入定向 PG 验证。本结论不宣告任何动态通过：迁移未运行、真实 PG 未验证、CHECK 约束未实测；不宣告 M-1 解决或 STEP-008 完成。
冻结 hash 六文件全部与卡面一致，无漂移，未触发停止条款。

一、逐项标准结论

标准 1（五列 DDL 与 Python 域一致）：符合。
事实定位：004_activities_time_budget.sql 第 20–49 行；repository.py 第 29–33、200–205、260–267 行。
逐列核对：max_running_seconds BIGINT NOT NULL，CHECK 大于 0 且不超过 2147483647，与 Python 侧 _validate_spec 的 0 < M <= _MAX_RUNNING_SECONDS（含 bool/非整数拒绝）完全一致；running_reserved_seconds、running_settled_seconds 均 BIGINT NOT NULL DEFAULT 0 且 CHECK 非负；余额约束 running_reserved_seconds <= max_running_seconds - running_settled_seconds 等价于 R + S <= M，采用减法写法防溢出（M 上界 2^31-1、S 非负，M - S 下界仍在 BIGINT 范围），不依赖加法回绕；running 形状约束（status='running') = (R>0) 与所有写路径一致（create 写 R=0 状态 pending、claim 成功 R=W_eff>0 状态 running、折叠耗尽/结算/取消均 R=0 且状态非 running）；last_settled_generation/last_settled_seconds 成对 NULL 约束，seconds 列 CHECK 为 NULL 或非负。nullable 表达"未结算"保留，非法已结算值（负秒数、单列出现）被 DB 约束拒绝。create_activity 写 M 及零计数（R=0、S=0 显式插入），无无限预算或自动免费默认。
观察 O1（非缺陷，记录边界）：last_settled_generation 列无非负 CHECK。Python 侧 settle 校验 execution_generation >= 0 且为唯一写入路径，DB 层不阻止绕过应用的负值直写。与合同"历史数值非负"对照：seconds 列有 CHECK，generation 列靠应用校验。不要求本批修改，是否加固由后续迁移修订决定。

标准 2（004 事务与边界）：符合（静态）。
事实定位：004 第 5–16 行。BEGIN 后先 LOCK TABLE activities IN ACCESS EXCLUSIVE MODE，再在 DO 块判空，非空 RAISE EXCEPTION 使整个事务中止，DDL 在同一事务内，不存在无锁判空窗口或部分 DDL 残留。无回填、无用户库写。001/002/003 mtime 为 09-12/09-14，未改动（见证据记录）。不据静态 DDL 宣称迁移已运行。

标准 3（claim 三分支）：符合。
事实定位：repository.py 第 296–391 行；diff-repository.txt 对应段。
锁序保持来源快照 → 活动 FOR UPDATE。准入冲突校验（未知活动/来源失效、已取消或过期、有效租约）先于预算计算。folds_residual 条件为 status='running' 且 R>0：仅残留 R 折叠，已结算 pending/R0 窗口不折叠。耗尽分支：折叠后 A<=0 时提交关闭 UPDATE（status=pending、代次 +1、executor/lease 清空、R=0、S=折叠值）后返回 None，无异常回滚；活动已 pending 且 A=0 时直接返回 None，不写行、不递增代次。成功分支：W_eff=min(window_seconds, A)，折叠与新租约在同一 UPDATE 原子完成，代次每条路径恰递增一次，ActivityLease 新增 window_seconds 字段返回实际预扣，与返回契约一致。代次递增规则已写入 docstring 两路径说明，无硬编码测试代次。时间预算耗尽 None 与未知活动/有效租约冲突异常可区分。
余额守恒复核：折叠耗尽时由旧不变量 S_old+R_old<=M 且 A<=0 可推出折叠后 S 恰等于 M，balance CHECK 不会误伤；Python 侧整型运算无溢出问题。

标准 4（settle）：符合。
事实定位：repository.py 第 393–477 行。
参数校验在事务外：bool/NaN/无穷/负数拒绝，C=ceil(elapsed_seconds) 向上取整，C>W 直接 ValueError 拒绝不静默钳制；执行代次/window 格式校验完整。事务内锁序与 claim 一致。正常路径要求 running、executor 匹配、代次匹配、R 等于实际 W，UPDATE 原子完成 S+=C、R 清零（等价 R-=W）、代次 +1、executor/lease 清空、写最近结算 G 与 C。受限幂等在 FOR UPDATE 锁内判断且先于运行态检查：相同最近 G 且相同 C 返回 ALREADY_SETTLED 不改账；相同 G 不同 C 拒绝；更旧或未知 G 落入运行态不匹配拒绝；关闭后重试不被状态先拒。提交响应丢失按持久事实重试即得 ALREADY_SETTLED，不重复折叠或退款。极端输入（超大有限 float、C 恰等于 W、C=0 真实零耗时）均符合拒绝/接受契约，错误传播 ValueError/ActivityLedgerConflict/AdmissionUnavailable 分层明确。S_new=S+C<=M 由 C<=W=R 与旧不变量保证，DB CHECK 为兜底不误伤。
观察 O2（非缺陷）：settle 与既有 cancel 一致地忽略 _lock_sources 返回值（来源替换不阻断结算/取消记账），属既有取消语义的自然延续，不属本卡范围。

标准 5（幂等与取消竞争）：符合。
事实定位：settle 第 443–475 行；cancel_activity 第 479–509 行。
受限幂等在锁内判断；关闭后重试不改账；冲突/更旧拒绝且不改账。cancel 沿既有锁序，FOR UPDATE 串行化竞争；重复取消命中 cancelled 终态直接返回当前代次；UPDATE 中 running_settled_seconds = running_settled_seconds + running_reserved_seconds 按 PostgreSQL SET 取旧值语义恰好转出一次在途 R，不重复扣费。模型次数/费用预留字段未动，旧操作不重发，record_outcome 的 UNKNOWN 纪律保持。五列不保存历史 executor/W 的限制为已批准内部契约，未要求扩成全历史回放。

标准 6（未顺手改写与调用路径影响）：符合。
diff-repository.txt 全量核对：变化仅限常量两行、SettleResult 枚举、ActivitySpec/ActivityLease 各一字段、_validate_spec 增校验、create_activity INSERT 列清单、claim_lease 主体、新增 settle_execution_window、cancel_activity UPDATE 增两行与两个 docstring；list_unresolved_operations、recover_unknown、recover_obsolete_operations、admit、mark_dispatch_started、record_outcome 主体零变化。
调用路径影响分析：admit/_activity_allows 不引用新列，行为不变；settle/cancel/折叠均递增代次并清空 executor/lease，使旧代次未决操作自然落入既有 recover_obsolete_operations 收敛路径，与 071/074 已验证机制一致，无新缺口；budget 耗尽 None 仅影响测试调用方（backend/app 内无生产调用点，全仓 grep 证实）。claim/cancel 的状态与代次变化不会绕过 _operation_is_current 的代次/租约判定。未发现回归迹象（静态）。

标准 7（测试准备）：两处确定缺陷，其余符合。
符合项：新用例全部真实调用仓储；专用 RETROLUME_TIME_BUDGET_TEST_DATABASE_URL 缺失时 skipUnless 明确跳过，不回退用户 DSN；teardown 定向 FK 清理顺序与 068 一致且失败如实抛出；budget_row 九列投影覆盖全部断言字段，test_01/test_04 整行断言；三个旧测试文件 diff 证实夹具修改仅必要参数（max_running_seconds、window_seconds）与 None 检查，业务断言与 069 定向 FK 清理保留。
缺陷 D1（确定缺陷，测试夹具，严重度中）：backend/tests/test_activity_recovery.py 第 284–296 行，test_04 的隔离对照活动 other = ActivitySpec(...) 缺少必填字段 max_running_seconds（该字段无默认值）。运行时构造即抛 TypeError，test_04 必然失败，浪费运行卡。触发条件：运行 test_04。影响：仅该用例，不涉产品代码。最小修正：在该构造中补 max_running_seconds=3600，与同文件其他夹具一致。
缺陷 D2（确定缺陷，测试场景算术，严重度中）：backend/tests/test_activity_time_budget.py test_08 末段（第 343–345 行）断言预算耗尽返回 None，但场景算术不支持：M=200，第一窗 W100 结算 20.2 得 C21（S=21），第二窗 W50 结算 0（S 仍 21），第三窗 W100 过期后折叠 R100 入 S 得 S=121，A=200-121=79 大于 0，按合同与当前实现应返回 W_eff=79 的新租约，assertIsNone 必然失败。实现行为符合合同，属测试场景标注与算术错误。触发条件：运行 test_08。影响：仅该用例误报，不涉产品代码。最小修正方向（二选一，由修复卡裁决）：将该断言改为成功认领且 window_seconds 等于 79 并补齐后续断言；或重构用例数字使折叠后真实耗尽（例如第一窗以 elapsed_seconds=100 全额结算后再折叠满窗）。本卡不执行修复。

标准 8（最小 PG 验证清单）：见下节。

二、后续最小 PG 验证清单（逐项标识或缺口）

A. 新增八例（backend/tests/test_activity_time_budget.py，专用 DSN）：
1. test_01_settle_normal_path_and_idempotent_retry——现有，直接运行（正常结算、幂等重试、同 G 异 C 冲突）。
2. test_02_new_claim_after_settle_does_not_fold——现有，直接运行。
3. test_03_stale_residual_fully_folded_on_reclaim——现有，直接运行。
4. test_04_fold_exhaustion_returns_none_and_closure_committed——现有，直接运行。
5. test_05_cancel_folds_and_repeat_is_idempotent——现有，直接运行。
6. test_06_late_settlement_for_old_generation_rejected——现有，直接运行。
7. test_07_parameter_validation_rejects_invalid_input——现有，直接运行。
8. test_08_ceiling_rounding_zero_and_budget_exhaustion——现有但含 D2，须先修正场景再运行，否则误报。

B. 004 迁移（合同明确留真实运行验证，均为缺口）：
1. 空库执行成功：五列与三条约束（balance、running_shape、last_settled_pair）存在——缺口。
2. 非空 activities 执行拒绝：预置一行合成活动后执行 004 须异常且全回滚、无部分 DDL——缺口。
3. CHECK 反例至少各一：balance 反例（R 超出 M-S）、running_shape 反例（非 running 且 R>0，或 running 且 R=0）、last_settled_pair 反例（单列 NULL/单列非 NULL）、last_settled_seconds 负值、M 为 0 或超 2147483647——缺口。

C. 既有用例按依赖选择（不默认三文件全跑，但以下全部经夹具依赖新签名，均受影响，应运行）：
1. backend/tests/test_activity_ledger.py 全部 8 例（test_01 至 test_08）：均经 activity() 夹具使用新 claim 签名与 ActivitySpec 必填 M。
2. backend/tests/test_activity_recovery.py test_01 至 test_06：均经 build_activity/reclaim_next_generation 依赖新签名；test_04 须先修 D1，否则 TypeError。

D. 明确不要求：并发压力、时钟回拨、崩溃恢复、worker、EXPLAIN、mock/通用测试框架扩建。

三、未验证与风险
1. 全部动态行为未验证：PG 执行、004 迁移运行、CHECK 实际拒绝行为、锁等待与超时、并发。静态正确不等于真实通过。
2. running_shape 与 balance 约束在真实 PG 的行为未观测；标准 2 的结论限定静态。
3. O1：last_settled_generation 无 DB 层非负 CHECK，依赖应用校验，为已记录边界。
4. O2：settle/cancel 忽略来源锁校验结果，与既有取消语义一致，若未来来源撤销需阻断记账则为契约修订项。
5. 本卡未修复 D1/D2；未运行 compile/unittest/PG/Docker；未读 077 结果文档，其报告中声称的 compile 通过等事项未复核。

四、文档建议
1. 架构 v0.27 后续可记录：078 代码层有条件通过，条件为修正 D1/D2；DATA-007 基础切片维持"已实现，尚未验证"。
2. 建议将 O1、O2 登记为非阻塞观察，不升级为硬门槛。

五、必要人工操作
1. 裁决 D2 修复方向（改断言为 W_eff=79，或重构用例数字真实耗尽）。
2. 安排 D1/D2 修复小卡（仅限两个测试文件，本卡不修复），随后按第二节清单出定向 PG 运行卡。

六、下一步
Astra 验收本卡；出修复卡；修复后按最小 PG 清单执行验证卡。本卡不填写 Astra 最终验收，不宣告时间监督或 STEP-008 完成。
