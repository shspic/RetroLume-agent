# TASK-055 Windows 运行循环与账本剩余验证记录

状态：本卡定向验证通过；这不是独立审计，也不代表 STEP-008 整体完成。

## 范围与环境

- 只使用父任务保留的专用合成 PostgreSQL 容器 `retrolume-task-048-pg`，容器 ID `2eca04213acaad642a7df879b457d86c596df11d9699555567e07f0e956b9106`。
- 启动前核对镜像 `sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f`、`127.0.0.1:55433`、CPU 1、内存 512 MiB、PID 128、`restart=no`、无宿主绑定，未重建或覆盖容器。
- 只使用合成来源、活动、模型响应和容器自有凭据；未读取真实配置、用户数据库或资料，未调用模型，未安装或升级依赖。
- 运行版本：Windows、Python 3.12.10、Uvicorn 0.52.4、psycopg 3.3.5、PostgreSQL 17.11。

## 循环选择

两个正式启动器均传入 `--loop app.runtime:psycopg_compatible_loop_factory`。本次不是仅检查字符串：`tests/run_ledger_check.py` 使用 Uvicorn `Config.get_loop_factory()` 实际解析同一入口，结果为 `app.runtime:psycopg_compatible_loop_factory`，其 Windows 实例类型为 `asyncio.windows_events._WindowsSelectorEventLoop`。

七个真实 PostgreSQL 测试通过自定义 `IsolatedAsyncioTestCase` 基类，把同一正式 factory 交给 Python 3.12 `asyncio.Runner`；因此异步 psycopg 连接和账本事务实际运行在该 factory 生成的循环中。没有修改全局事件循环策略。Linux 分支继续使用 `asyncio.new_event_loop()`，遵循平台默认循环。

Windows Selector 循环不支持 asyncio 异步子进程。现有 `deploy/start_local.py` 使用同步受监督的 `subprocess.Popen` 启动 Uvicorn，不受此限制；后续异步 worker 若需创建子进程，必须另行遵循该边界。

## 七类定向结果

唯一一次主运行仅选择父卡未闭合的测试 02—08，7/7 成功：

1. 相同操作并发准入仅产生一个 `AdmissionPermit`，另一个被拒绝，预算只预留一次。
2. 非正数活动限制拒绝创建；额度耗尽后第二次准入拒绝。
3. 来源版本替换后旧快照准入被撤销。
4. 取消递增执行代次，旧 permit 不能发送；在途项只能记录 unknown。
5. unknown 跨新连接保留，预算不返还，不能自动再发。
6. 相同终态幂等，不同终态不能覆盖既有 received 事实。
7. 合成插入失败时，活动预留和操作写入整笔回滚。

原始输出见 `ledger-check.stdout.log`，退出码见 `ledger-check.exit-code.txt`。父任务已通过的测试 01 没有重跑。没有自动重试、退款或越权路径。

## 资源关闭

主运行结束后由外层监督按唯一容器 ID 执行停止。`container-after.txt` 确认最终为 `status=exited`、`running=False`；容器和纯合成数据按卡片要求停止保留，未删除。

## 完成边界

本卡关闭 Windows 正式 Uvicorn 启动循环接线和七类账本剩余反例。进程崩溃、监督器失联、worker 终止、取消远端、业务提交、真实应用组合与独立强模型审计仍不在本卡验证范围。
