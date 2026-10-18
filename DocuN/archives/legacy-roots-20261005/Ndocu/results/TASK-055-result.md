# TASK-055 结果：Windows 运行循环兼容与账本剩余验证

状态：本卡实现与定向验证通过，可作为 `R-049` 候选证据交回 Astra；不是独立审计，不代表 STEP-008 整体完成。

关联：`TASK-055 / R-049 / STEP-008`，父任务 `TASK-051 / R-045`；对应 NFR-002/003、SEC-002、MOD-003/007/008、FLOW-005。

## 实际变更

- 新增 `backend/app/runtime.py`，提供 `psycopg_compatible_loop_factory()`：Windows 明确创建 Selector 事件循环，其他平台使用 `asyncio.new_event_loop()` 保持平台默认行为。
- `deploy/start_local.py` 与 `deploy/start-backend.ps1` 都向 Uvicorn 传入同一个 `app.runtime:psycopg_compatible_loop_factory`，没有用全局事件循环策略代替正式启动接线。
- `backend/tests/test_activity_ledger.py` 的隔离异步测试通过 Python 3.12 `asyncio.Runner(loop_factory=...)` 使用正式 factory。
- `tests/run_ledger_check.py` 通过 Uvicorn 实际解析正式 factory、检查 Windows 循环类型，并只选择父任务未执行的测试 02—08。父任务已通过的合法路径测试 01 未重跑。
- 既有账本仓储和 `002_activities.sql` 只读保留；确认测试清理顺序已是先清空 `material_sources.current_version`，再删除版本与来源。

没有修改 main、materials、PDF、前端、锁、真实配置或正式 docu，没有安装或更换依赖，没有提交 Git。

## 实际运行与结果

唯一一次主运行使用父任务停止保留的专用容器，启动前精确核对 ID、镜像、`127.0.0.1:55433`、CPU 1、内存 512 MiB、PID 128、`restart=no` 和无宿主绑定；没有重建容器。

Uvicorn 0.52.4 的 `Config.get_loop_factory()` 实际选择 `app.runtime:psycopg_compatible_loop_factory`，Windows 循环为 `_WindowsSelectorEventLoop`。真实 PostgreSQL 17.11 上测试 02—08 共 7/7 通过：并发重复操作、额度拒绝、来源版本撤销、取消代次拒绝、unknown 跨连接保留、结果幂等冲突、事务失败整笔回滚均成功。没有自动重试、自动退款或越权；没有模型调用、费用、真实资料、真实配置或用户数据库操作。

原始命令、stdout、退出码、时间、版本、源码哈希和容器前后状态统一保存在 `Ndocu/evidence/task-055/`。测试退出码为 0；最终容器状态为 `exited`、`running=False`，停止保留且未删除。

## 未运行与边界

- 没有重跑 TASK-051 已通过的合法一次准入路径。
- 没有启动真实应用、读取应用数据库配置或执行用户数据库迁移。
- 没有验证进程崩溃、监督器失联、worker 实际终止、远端取消、业务成功提交或整体 STEP-008。
- 本卡自查不能替代最终候选所需的隔离独立强模型审计。

Windows Selector 循环不支持 asyncio 异步子进程。当前 `start_local.py` 对 Uvicorn 使用同步受监督的 `subprocess.Popen`，该行为不变；后续 worker 如需异步创建子进程，必须显式遵守这一兼容边界。

## 风险、文档建议与下一步

剩余风险集中在尚未实现或验证的 worker/监督/业务集成和最终独立审计，不影响本卡两项定向结论。建议 Astra 把 R-049 登记为“实现与定向验证候选通过”，更新架构版本映射，并在最终候选形成后按既定隔离要求执行强模型独立审计；在此之前不要把 STEP-008 或功能发布写成完成。
