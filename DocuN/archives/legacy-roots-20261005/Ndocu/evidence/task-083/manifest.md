# TASK-083 有限验证清单（首次运行前冻结）

范围：仅本卡改动的activities关闭门与新worker内部组件；不运行PG/Docker/模型/应用/真实网络。Windows Job场景串行，至多5个场景，单场景≤30秒，单批首个进程起≤10分钟、每条命令≤60秒、最后预留60秒清理。每场景的测试控制者先持精确Job/进程句柄和截止，才Resume。若归属或清理失败即停止后续Job。

1. 静态：`backend\.venv\Scripts\python.exe -B Ndocu\evidence\task-083\static_check.py`（项目根），检查允许文件AST、004/仓储pre hash、禁止明显真实外发调用、输出证据。另查 `git diff --check` 与精确差异。
2. 离线门/仓储接口：`..\.venv\Scripts\python.exe -B tests\test_activity_dispatch_close.py CloseGateRepositoryTests`（backend根；实际命令用 `.venv\Scripts\python.exe -B tests\test_activity_dispatch_close.py CloseGateRepositoryTests`）。3个明确方法：test_01_close_current_is_idempotent_old_identity_cannot_touch_new_window、test_02_settle_requires_close_but_old_same_g_c_remains_idempotent、test_03_admit_denied_when_db_gate_closed。
3. 离线本地门与启动顺序：`.venv\Scripts\python.exe -B tests\test_worker_session.py GateTests ProtocolUnitTests`（backend根）。4个方法：test_gate_closure_waits_for_marked_before_send_and_never_reopens、test_gate_close_timeout_keeps_closed、test_claim_response_lost_and_partial_window_never_spawn、test_unknown_old_job_fails_before_claim。
4. Windows本机合成Job：`.venv\Scripts\python.exe -B tests\test_worker_session.py WindowsJobTests`（backend根）。5个场景：test_01_normal_job_empty_precedes_close_and_refund、test_02_hung_job_is_killed_and_not_refunded、test_03_main_exits_before_descendant、test_04_supervisor_death_closes_last_job_handle、test_05_same_name_collision_fails_closed。每个活动UUID/Job唯一，包含准确PID和对象查询事实；未包含真实模型。
5. PG准备、**not_run**：005空表成功/非空全回滚；close与admit/mark并发；settle关门前拒绝、关门后成功、旧G/C幂等不影响新窗；取消/恢复结果纪律。使用独立专用DSN，缺失明确skip，未来单独授权。已有test_activity_time_budget.py中01/02/06/08依赖settle关门前置；test_activity_ledger.py中01/05/06/07和test_activity_recovery.py中01/03/05依赖admit/mark/record门变更，未来只选受影响用例与新PG场景，不机械重跑079全部22例。

预算：最多一次初始批；明确范围内缺陷一次修正并仅失败/受影响复检，复检总Job启动数与初批合计≤16；连续第二次失败、根因不明或cleanup_incomplete立即停。测试命令记录退出码和原始输出；手工逻辑检查不得称动态通过。
