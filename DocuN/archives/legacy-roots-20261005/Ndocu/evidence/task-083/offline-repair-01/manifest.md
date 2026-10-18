# TASK-083 离线补足轮01验证清单（运行前冻结）

旧083 Job 初批5场景、一次修正及第04场景超时/归属偏差原样保留；本轮真实Job复检机会冻结，**Job启动数=0**。本轮不运行 PG/Docker/模型/应用/网络，不查询或操作旧进程。

## 一次静态核对

项目根目录命令：`backend\.venv\Scripts\python.exe -B Ndocu\evidence\task-083\offline-repair-01\static_check.py`，仅 AST、hash、冻结范围与选择清单核对。紧接只对本卡允许且已跟踪的文件运行 `git diff --check -- backend/app/worker/__init__.py backend/app/worker/gate.py backend/app/worker/session.py backend/app/worker/windows_job.py backend/tests/test_worker_session.py backend/tests/fixtures/task083/fixture.py`；新文件另由 AST 覆盖。静态及差异检查同属一次准备核对，记录退出码与原始日志。

## 一次纯单元批次

项目 backend 目录唯一命令：`.venv\Scripts\python.exe -B tests\fixtures\task083\run_offline.py`。单命令≤60秒，整个离线验证墙钟≤180秒；脚本只加载下列精确ID，不做发现式运行、无OS子进程或数据库连接。失败只允许一次修正与失败/受影响 ID 复检，两次累计≤360秒；再次失败或根因不稳停止。

1. `OfflineRepairTests.test_01_command_data_rejects_callable_and_expired_manager_never_spawns`
2. `OfflineRepairTests.test_02_partial_window_early_exit_reports_cleanup_failure_and_full_reservation`
3. `OfflineRepairTests.test_03_cancellation_preserves_diagnostic_and_cleans_owner`
4. `OfflineRepairTests.test_04_claim_response_lost_has_no_job_and_no_false_charge`
5. `OfflineRepairTests.test_05_early_success_uses_tree_zero_close_then_same_g_settle_retry`
6. `OfflineRepairTests.test_06_timeout_or_cleanup_failure_never_refunds`
7. `OfflineRepairTests.test_07_controlled_worker_gateway_chain_drains_marked_call`
8. `LauncherUnitTests.test_08_fake_process_timeout_terminates_exact_owner_without_charge_claim`
9. `ProtocolUnitTests.test_claim_response_lost_and_partial_window_never_spawn`（受命令接口修改影响）
10. `ProtocolUnitTests.test_unknown_old_job_fails_before_claim`（受命令接口修改影响）

以上替身仅证明调用序和状态出口，不声称 Windows Job、PG、跨进程管道或真实供应商通过。原7项中未受影响的 GateTests 和仓储替身不重跑。

## 后续候选，当前 not_run

真实Job最小受影响清单：原失败01正常早停退款、原失败04 SUP死亡/最后句柄；修订 session 终止/收尾路径影响02挂死全额预扣，新增创建时间/精确身份日志与Job关闭路径影响03主退后代仍存活。05同名碰撞旧局部行为有效但身份未完整记录，独立审计先评估是否再给该项运行预算，不能用旧PASS替代身份验收。下一次真实运行需编排在独立只读审查后明确恢复范围与预算。

专用PG运行准备（not_run）：`backend/tests/fixtures/task083/pg_migration.py` 的 `PGMigrationTests.test_pg_migration_01_empty_table_adds_only_closed_column`、`test_pg_migration_02_nonempty_table_rolls_back_whole_005`；`pg_close.py` 的 `PGCloseTests.test_pg01_close_settle_and_old_gc_does_not_touch_new_window`、`test_pg02_closed_gate_rejects_admit_mark_but_records_outcomes`、`test_pg03_close_commits_before_concurrent_admit_and_mark`、`test_pg04_cancel_closes_gate_and_old_dispatched_unknown_converges`。仅环境变量 `RETROLUME_TASK_083_DATABASE_URL` 明确指向专用合成库时运行，缺失skip，不回退任何用户或应用DSN。001—005迁移仅在测试自己的随机 schema 中执行，仓储用例按本例UUID及FK顺序清理。既有受影响ID：time-budget 01/02/06/08；ledger 01/05/06/07；recovery 01/03/05；按各自新门行为挑选，不机械全跑。
