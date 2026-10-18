# TASK-072 结果：TASK-071 差异独立审计（R-066 / STEP-008 局部）

- TASK/R/STEP：TASK-072 / R-066 / STEP-008 局部；父 TASK-071，关联 068/069/070、NFR-002/003、SEC-002、FLOW-005、DATA-007
- 审计类型：独立只读差异审计（仅审 071 新增差异，不重审整仓）；真实 PG 未运行，本卡不运行、不以语法证据判动态通过
- 建议结论：**代码层有条件通过**（无确定缺陷；条件仅为 Astra 既有安排中的真实 PG 运行六个用例，本审计未新增条件）。本结论不是 G-1 完成、不是 STEP-008 完成。

## 独立性声明

全新隔离会话执行，未参与 TASK-071 实现。读取范围限：根 AGENTS.md、docu/AGENTS.MD、TASK-071 原合同、LATER_REQUIREMENTS 的 NFR-002/003 与 SEC-002、PROJECT_ARCHITECTURE 的 FLOW-005 与 R-064/R-065 内部恢复信任边界（跳过执行者评价与 Work 验收段）、两对文件 pre/current、002 迁移。未读取 TASK-071 结果/自评、执行聊天、make-diffs-run 或其推理说明；未接触自评内容，无披露事项。审计中仅运行 hash 计算与 `git diff --no-index`（只读），未运行 compile/unittest/Docker/PG/EXPLAIN，未安装、未联网、未读凭据，未做 Git 提交，未改任何生产/测试/迁移/正式文档文件。

## 读取快照与 hash（Ndocu/evidence/task-072/）

- input_hashes.txt：四项实测 hash 与卡面完全一致（repository pre cc7fddd4…6dcc7 / current 50ec537b…cfce6；test pre 7bf924cd…6804f4 / current ef705113…575d246），无快照漂移
- diff_repository.patch、diff_test.patch：`git diff --no-index -U40` 原始差异
- read_scope.md：读取范围、独立性声明、关键原始摘录

差异范围确认：repository.py 仅 `recover_obsolete_operations` 签名/校验/候选 SELECT/UPDATE 改动（415—474）；测试仅新增 `test_06`（380 起），test_01—05 与 069 定向清理未改动（差异中无任何删除/修改行）。

## 逐项标准与证据

1. **limit 校验与返回语义：成立。** 校验在 434—435，位于 `_transaction`（474）调用之前，非法输入不建连接；bool/非 int/1—200 以外统一 ValueError，不静默截断。默认 100（420）。返回值 = UPDATE RETURNING 行数（471—472），即本批实际改动数。单次事务一 SELECT 一 UPDATE，无内部循环、无隐式重试。
2. **锁序与候选限定：成立。** 锁序保持 来源（_lock_sources，202—230，按 source_id 排序）→ 活动（440 FOR UPDATE）→ 操作（445—453），与 recover_unknown 及全部写入方一致。当前代次在活动锁后读取（444）。候选 SELECT 严格限本活动、reserved/dispatched、`execution_generation < 当前代次`，ORDER BY operation_id + LIMIT + FOR UPDATE（445—453）；排序口径与既有方法一致，不引入跨方法锁序倒置。
3. **UPDATE 精确集合：成立。** UPDATE 只对 `operation_id = ANY(locked_ids)`（467），locked_ids 全部来自本次实际加锁的 SELECT 结果（457）；同时重复 activity/state/旧代次谓词（464—466）。空集合在 UPDATE 前返回 0（458—459）。无重新宽更新、无另选候选集合。同事务内活动行已锁定，当前代次不可能变化，重复谓词为纵深防御且无害。
4. **终态与旧 permit 竞争：成立。** 当前/未来代次被 `< 当前代次` 排除，既有终态（not_sent/received/unknown）被 state 谓词排除，均不可能被本批改写；UPDATE 不触碰 requests_reserved/cost_reserved_microunits，预留不退、无重发。旧 permit 提交 UNKNOWN 的竞争按锁序与终态保护分析（非凭代次互斥）：record_outcome 经 _locked_operation（586—617）以相同 来源→活动→操作 锁序加锁，无倒置；(a) record_outcome 先提交则行变终态，recover 候选 SELECT 在 READ COMMITTED 新快照下不再选中该行，不会覆盖；(b) recover 先提交则 record_outcome 随后看到终态 unknown，元数据完全相同才幂等返回，否则 AdmissionDenied「已终结调用不能覆盖为不同结果」（703—706），不可能覆盖 recover 写入。
5. **test_06 可观察性与清理边界：成立。** 类内实际 6 个 test 方法（test_01—06），基类 PsycopgLoopIsolatedAsyncioTestCase 无用例。test_06 观察：limit=2 四批返回 2/2/1/0；每批后逐行 state 映射证明仅对应已选项变化（未选项保持 reserved）；每批断言 execution_generation=2、requests_reserved=6、cost_reserved=600 不变；末批断言终态字段 state/disposition/error_code/recorded_at 及 cur-op-1 完全未动；bool/0/201/"2" 均 ValueError。069 定向外键清理（asyncTearDown，60—84，按 FK 顺序仅删本例合成行）原样保留。DSN 缺失经类级 `@unittest.skipUnless(DSN, …)`（49）记为 skip，不回退用户 DSN，不把 skip 当成功。
6. **边界诚实性：成立。** docstring（430）明示 limit 只约束加锁与改写行数，不约束扫描/排序输入、不消除锁等待；返回 0/<limit 不被表述为永久无未决项证明。455—456 注释含「Limit 位于 LockRows 之上」计划形状说明——与 PostgreSQL 对该语句形态的既知计划一致，但本卡无 EXPLAIN，未当证据引用。
7. **范围不扩张：成立。** 差异仅涉及该方法与新增用例；无 DDL/索引/HTTP/列表投影/worker/时钟/持久预算/依赖改动。内部调用方须有活动写权限的门槛未动（当前仍无调用方）；已知 M-1、worker、真实 PG 未运行项未用于重复否决本差异。

## 发现及严重度

- **确定缺陷：无。**
- F-1（条件风险，低）：`operation_id = ANY(%s)` 依赖 psycopg3 的 Python list→数组适配。与本文件既有 `allowed_tools` 数组插入（257）同一适配模式，代码层一致；实际绑定行为待真实 PG 确认。若异常只会运行时报错并整批回滚（失败关闭），不构成越权或误改终态。最小建议：无需改动，test_06 四次调用均走该路径，真实 PG 运行即覆盖。
- F-2（未验证，信息级）：455—456 注释的执行计划形状声称无 EXPLAIN 证据。无需行动；后续真实 PG 卡如需可 EXPLAIN 确认，本卡不要求。
- F-3（适用边界，信息级）：并发下单批可能因锁等待/超时（lock_timeout 2s、statement_timeout 3s）整批回滚为 AdmissionUnavailable，或因 EvalPlanQual 重判使实际加锁数小于 limit；返回值如实计实际改动。批次调度纪律属于未来调用方接线卡，本差异已如实声明。

## 未验证 / 限制

全部动态行为未验证：六个真实 PG 用例未运行；数组适配、锁竞争、EvalPlanQual 行为、执行计划形状均为代码层推断。本审计为单次差异审查，覆盖七项标准即停；不重审 070 整仓结论（其未变部分证据继续适用），不新增性能或动态任务。

## 需求与架构影响

R-065 增量与架构 v0.23 R-065 段描述一致（默认 100、非 bool 整数 1—200、锁序不变、精确 ID 集合、返回本批数、无内部循环）；本次审计支持维持「已实现、未验证」状态不变，不改变 FLOW-005 与 SEC-002 门槛。NFR-002（晚到结果不污染）、NFR-003（预留不退、不自动重发）在差异范围内保持。

## 待同步文档（由 Astra 执行，本卡禁写正式 docu）

- docu/PROJECT_EXECUTE_STATE.MD：登记 TASK-072 差异审计结论与建议状态
- docu/CHANGE.MD：登记 Ndocu/evidence/task-072/ 四个文件与 Ndocu/results/TASK-072-result.md
- docu/PROJECT_ARCHITECTURE.MD：如需，可在 R-065 段补一句「072 差异审计代码层有条件通过，动态证据仍缺」

## 必须人工操作与下一步

1. 用户将本结果块带回 Astra；Astra 验收本卡并登记文档。
2. Astra 按既有安排运行真实 PG 六用例（含 test_06）；通过后 071 切片的验证条件方可关闭。
3. M-1、worker 闭环、内部调用方权限接线保持开放，不随本卡关闭；不宣告 G-1 或 STEP-008 完成。
