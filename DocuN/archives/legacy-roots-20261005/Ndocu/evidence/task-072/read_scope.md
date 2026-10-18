# TASK-072 读取范围、独立性与关键摘录

时间：2026-09-21 12:38—12:50（GMT+8）。执行者：独立审计 Agent（全新隔离会话，未参与 TASK-071 实现）。

## 输入 hash（实测，见 input_hashes.txt）

- repository pre：cc7fddd4e685e1d3af859c7b402d0734354cef5675ed72f2f8acb83c92e6dcc7 → 与卡一致
- repository current：50ec537b07533c68194651b008d275176430effeb67126391ef43b96155cfce6 → 与卡一致
- test pre：7bf924cded794b94bdc213d255177253af2b3948ad844f302d7bd987ae6804f4 → 与卡一致
- test current：ef705113fbf6af83a0a29e99b40dfdb68109282c0ae8b724790e1d440575d246 → 与卡一致

四项全部一致，无快照漂移，审计适用于当前文件。

## 实际读取范围（全部只读）

1. AGENTS.md（根入口）、docu/AGENTS.MD（全篇）
2. Ndocu/tasks/TASK-071.md（原合同）
3. docu/LATER_REQUIREMENTS.MD：仅 NFR-002/003、SEC-002 条目及第 10/11 节相关行（按需 grep）
4. docu/PROJECT_ARCHITECTURE.MD：FLOW-005 全段（137—153）、R-064/R-065 内部恢复边界段（40—47）、SEC-002 映射行 280；未读执行者评价与 Work 验收段
5. backend/app/activities/repository.py：全篇（重点 330—366 recover_unknown 未改对照、415—474 差异方法、586—617 _locked_operation、619—631 _operation_is_current、698—723 record_outcome、107—136 _transaction、202—230 _source_rows/_lock_sources）
6. backend/tests/test_activity_recovery.py：头部与基类（1—157）、test_06（380 起）；test_01—05 经差异确认未改，未逐行重审
7. backend/migrations/002_activities.sql：全篇（operation_id VARCHAR(128)、PK、偏索引）；001 未读（定向清理保留已由差异证明，无需 001 外键细节）

## 未读取（独立性纪律）

未读：Ndocu/results/TASK-071-result.md、TASK-070-result.md 及任何执行自评、执行聊天、make-diffs-run 产物或其推理说明。审计期间未接触任何 071 自评内容，无披露事项。

## 允许的写动作

- 生成原始差异：`git diff --no-index -U40`（只读操作，不触碰仓库索引），产物 diff_repository.patch、diff_test.patch
- hash 计算：PowerShell Get-FileHash，产物 input_hashes.txt
- 未运行 compile、unittest、Docker、PG、EXPLAIN、应用、模型；未安装、未联网、未读配置凭据；未做 Git 提交

## 关键原始摘录（行号以当前文件为准）

repository.py 434—435（事务前校验）：
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 200:
        raise ValueError("limit 必须是 1 到 200 之间的整数")

repository.py 445—459（候选锁定与空集合短路）：
    SELECT operation_id FROM activity_operations
      WHERE activity_id = %s AND state IN ('reserved', 'dispatched')
        AND execution_generation < %s
      ORDER BY operation_id LIMIT %s FOR UPDATE
    locked_ids = [row["operation_id"] for row in await cursor.fetchall()]
    if not locked_ids: return 0

repository.py 460—469（UPDATE 限定确切 ID 集合并重复谓词）：
    UPDATE activity_operations SET state='unknown', disposition='unknown', error_code=%s,
        recorded_at=CURRENT_TIMESTAMP
      WHERE activity_id=%s AND state IN ('reserved','dispatched')
        AND execution_generation < %s AND operation_id = ANY(%s)
      RETURNING operation_id

repository.py 703—709（旧 permit 终态保护，未改）：
    if call["state"] in {"not_sent", "received", "unknown"}:
        if self._stored_outcome(call) == values: return
        raise AdmissionDenied("已终结调用不能覆盖为不同结果")
    ...
    if not current and outcome.disposition is not LedgerDisposition.UNKNOWN:
        raise AdmissionDenied("失效或过期执行只能登记 unknown 诊断")

migrations/002_activities.sql 54/77/84—86：
    operation_id VARCHAR(128) NOT NULL,
    PRIMARY KEY (activity_id, operation_id),
    CREATE INDEX activity_operations_recovery ON activity_operations(activity_id, state, operation_id)
        WHERE state IN ('reserved', 'dispatched');

tests 49—50（DSN skip）：
    @unittest.skipUnless(DSN, "仅在 TASK-068 专用合成 PostgreSQL 中运行")
    class ActivityRecoveryPostgresTests(PsycopgLoopIsolatedAsyncioTestCase):
