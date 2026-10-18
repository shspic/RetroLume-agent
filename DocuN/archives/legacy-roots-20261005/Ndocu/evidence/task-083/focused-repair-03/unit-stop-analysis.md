# 最终批次停止记录

`unit-final-01.log` 原样保留。第一命令 10 个精确替身用例运行 0.7465334 秒，退出码 1；9 通过、1 失败。失败是 `LauncherTests.test_d1_deadline_before_resume_terminates_exact_owner`：替身 `_remaining` 前三次均返回 5.0，第四次才返回 0.0。实现的前三次检查分别发生在映射创建前、请求写入后、精确 SUP 句柄/创建时间取得后；第三次允许 Resume，第四次发生在已 Resume 的 `wait` 参数处，所以实际返回 `manager_timeout_unconfirmed`，与夹具期待的 `manager_startup_deadline_unconfirmed` 不符。该用例没有有效验证“Resume 前截止”分支；不得凭其他用例推断已覆盖。其余九例虽显示 ok，整个命令仍失败，不能作为最终批通过。

按本卡最终批次失败即停，未修改夹具/产品，未复检，预列第二命令 `FixedEntryTests.test_12_fixed_command_and_injected_gateway_pass_through_gate` 为 not_run。05 单次诊断先前已完成且不能重试。真实 Job、PG 均 0 启动。后续独立审计须看到此失败并由编排另定额度；本窗口不自放行 D1。
