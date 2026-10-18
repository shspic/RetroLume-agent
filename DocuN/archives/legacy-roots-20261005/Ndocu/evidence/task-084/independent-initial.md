# TASK-084 源码初判（读取083运行日志前留存）

2026-09-24；独立审计新窗口。只读批准合同、需求、原合同、离线边界和当前源码/夹具；未读 TASK-083-result.md 或实现聊天，尚未读本卡指定的083原始日志。19个冻结文件独立 SHA256 复算均匹配。未执行产品代码、测试、Job或PG。

- 仓储/005：先锁后判空、claim新代次开门、close身份校验、admit/mark关门、结果收敛及settle旧G/C受限确认在静态路径上基本符合合同；真实事务尚未验证。
- `launcher.py:63-75,81-83,90-108`：deadline虽然在`Process`创建前固定，`Process.start()`和`receive.recv()`均无由剩余预算约束的独立终止机制，超时后的两次`join(config.cleanup_seconds)`还能越过总期限；失败处理和finally内操作也可能覆盖原异常。当前场景/命令硬截止不充分。
- `session.py:161-181,273-306`：任何已claim却未settle的正常失败，在本次清理关闭Job句柄后仍留running/R；重启时`open_existing`失败即拒绝claim，无法进入原保守折叠，形成可重复的永久不可恢复路径。失败关闭安全，但可用性未满足完整恢复目标。
- `command.py:15-27`、`launcher.py:34,47`、`worker_main.py:15-26`：任意既有绝对可执行文件加参数可成为受监督命令；没有强制命令进入`run_controlled_worker`的绑定。门控包装器本身有效，但整个当前入口不能静态证明所有任务经门控gateway调用。真实供应商/HTTP接线本来未授权。
- `pg_close.py:24,35-56`：使用专用变量但未建随机schema，也未把`search_path`传给仓储或清理连接；不会按本卡要求隔离。`pg_close.py:124-148`仅sleep(0)后释放来源锁，未保证close事务在admit/mark前提交，所称并发顺序不确定。`pg_migration.py:26-37`失败时无条件DROP临时schema，不保留失败现场。
- `offline_unit.py:145-152`与`session.py:264-271`静态矛盾：claim抛`CancelledError`时结果账字段被设为`None`，测试却断言`(0,0)`，最终快照该用例预期会失败；需读原始日志和修改时序后作最终裁定。
- `job_control.py:18-105`的04控制器在Resume前获取创建时间、确切Job和自身截止，且于退出事件前关闭观察Job句柄；但`fixture.py:51-58`的事件/管道时序以及SUP死后树退出证据仍需真实复检。其他Job场景的旧证据适用性等读原日志判断。

以上为源码初判，不是运行证据或最终结论。后续逐项核查原始失败、修改前后差异与冻结适用性。
