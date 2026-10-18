# TASK-051 有限真实 PostgreSQL 验证记录

状态：验证未闭合。真实 PostgreSQL 已确认第 1 类通过；另 7 类被测试夹具清理顺序阻断，修正后遵守停止条件未再运行。

## 范围和环境

- 父任务映射：`TASK-048` 接续为 `TASK-051 / R-045`。
- 只使用合成来源、合成活动、合成模型响应和合成数据库；没有模型请求、外网资料发送、费用、真实配置读取或已有用户数据库写入。
- 项目环境：Windows，Python 3.12.10，psycopg 3.3.5。
- 数据库：PostgreSQL 17.11；执行 `001_materials.sql` 和 `002_activities.sql` 到新建的合成库。
- 专用容器：`retrolume-task-048-pg`，镜像 ID `sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f`，只绑定 `127.0.0.1:55433`，CPU 1、内存 512 MiB、PID 128、`restart=no`、无宿主挂载。
- 凭据只属于该合成容器；`command.txt` 中已脱敏。

完整环境和最终源码 SHA-256 分别见 `environment.txt`、`source-hashes.sha256`。

## 命令和原始证据

共同命令和脱敏环境见 `command.txt`。三次进程调用均使用同一专用容器，修正后只重启该已核对身份的容器，没有重建、覆盖或删除：

1. `ledger-check.stdout.log` / `ledger-check.exit-code.txt`：退出码 1。`001`、`002` 已成功应用；测试发现器因 `backend/tests` 不是包而在加载用例前退出。修正 `tests/run_ledger_check.py` 的发现根目录。
2. `ledger-check-rerun.stdout.log` / `ledger-check-rerun.exit-code.txt`：退出码 1。8 类均在建连前被 Windows Proactor 事件循环阻断，未触及账本事务。修正专用启动器，在 Windows 使用 psycopg 支持的 Selector 事件循环。
3. `ledger-check-final.stdout.log` / `ledger-check-final.exit-code.txt`：退出码 1。第 1 类“合法一次准入、一次性发送边界、收到结果并保留预留”通过。第 2 至 8 类在各自测试开始前被清理夹具阻断：`material_sources.current_version` 仍引用 `material_versions`，直接删除版本违反 `material_current_version_source` 外键。

已把夹具清理改为先将合成来源的 `current_version` 置空，再删版本和来源。按卡内“连续两次有依据的修正仍失败则停止”边界，没有第四次数据库运行，因此该修正及第 2 至 8 类均未形成通过证据。

## 已确认和未确认

真实 PostgreSQL 已确认：

- 新库可按顺序执行 001 和 002 迁移。
- 合法活动可创建、领取租约、原子预留一次请求和费用、一次性越过发送边界，并幂等记录一份 received 事实。
- 第 1 类检查后活动账上保留 `requests_reserved=1` 和 `cost_reserved_microunits=100`。

真实 PostgreSQL 尚未确认：

- 重复并发操作只有一个发送资格。
- 次数/费用限额拒绝。
- 来源版本替换撤销准入。
- 取消或过期代次拒绝，以及在途 unknown 诊断。
- unknown 跨新连接保留且预算不返还。
- 相同结果幂等、不同终态禁止覆盖。
- 插入失败时活动预留和操作写入整笔回滚。
- 进程崩溃、监督器失联、真实 worker 终止、业务提交和真实应用组合。

## 资源关闭

每次数据库进程结束或异常后均由外层监督使用记录的唯一容器 ID 停止容器并检查状态。最终状态见 `container-final-verification.txt`：`exited|false`，`stopped_confirmed=True`。容器及其纯合成存储按任务卡要求停止保留，没有删除数据；宿主端口不再监听。

## 集成风险

当前项目的 Uvicorn 0.52.4 在 Windows 单进程默认选择 Proactor，而异步 psycopg 3.3.5 要求兼容的 Selector 事件循环。专用测试入口已局部处理；正式接入 `PostgresAdmissionLedger` 前，需要在应用启动组合中显式满足该要求并另行验证。本卡没有越界修改部署启动文件。
