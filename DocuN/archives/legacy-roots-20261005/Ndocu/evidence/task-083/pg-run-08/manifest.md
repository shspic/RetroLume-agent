# TASK-083 / R-077 pg-run-08 运行前 manifest

- 卡号：TASK-083 / R-077（005及关闭门六例真实PG验证08）
- runTag：`20260925-1455`
- 容器名：`retrolume-task-083-pg08-20260925-1455`
- 镜像：`sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f`（固定本机已用镜像，先查在位，不拉取/构建/安装）
- 专用库：`retrolume_task083_pg08`（单一专用库，POSTGRES_DB 初始化时创建）
- 合成账号：`task083_pg08`，口令随机生成（secrets.token_urlsafe(24)），仅注入本次 docker run 与 unittest 子进程环境，所有输出经口令过滤，不记录完整含口令 DSN
- 端口：仅 `127.0.0.1:55437 → 5432`；占用即停，不杀占用者、不换端口

## 冻结四文件（预检 hash 复核）

| 文件 | 期望 SHA-256 | 预检 |
| --- | --- | --- |
| backend/tests/fixtures/task083/pg_migration.py | 85d27efd9d73ed4c7736b0a0a0268c8dd852b19e29334173426a15c862a105ac | MATCH |
| backend/tests/fixtures/task083/pg_close.py | 00b58fe7d091a6ef40c1406c81faf211c83da50b79a432e205d8c2677f130970 | MATCH |
| backend/app/activities/repository.py | 929320baf55d625e897324aa76ebe543bda86e73a4bf1c4766c7e552721c5b20 | MATCH |
| backend/migrations/005_activities_dispatch_closed.sql | 26b71a836355fa9620401f6bbb76e9a42668a1ce52077aa91ecb2f61ebeb50eb | MATCH |

其余直接依赖/001—004 沿已审冻结记录（084 review-05 复核零漂移），本卡不重采全仓；若运行中发现新漂移即停对应运行。

## 版本（预检实测）

- 项目 venv：Python 3.12.10（backend/.venv/Scripts/python.exe）
- psycopg：3.3.5（venv 内）
- PG 版本：运行时就绪检查 `SELECT version()` 实测，写入 runner-state.json
- Docker/镜像：首次预检 daemon 不可达（环境阻塞）；用户手动启动 Docker Desktop 后重跑预检一次，结果见 precheck-output.txt

## 资源限制（容器）

`--cpus 1 --memory 512m --pids-limit 128 --restart no`，bridge 网络（非 host），无宿主 bind 挂载（postgres 镜像匿名卷除外，保留不删），端口绑定仅 127.0.0.1:55437。创建成功后立即脱敏 inspect（container-inspect-created.json：名称/标签/镜像/限制/绑定/无bind挂载）。

## 唯一批次命令

工作目录 `backend/tests`，单次 unittest 进程、failfast：

```
backend/.venv/Scripts/python.exe -B -m unittest -v -f \
  fixtures.task083.pg_migration.PGMigrationTests.test_pg_migration_01_empty_table_adds_only_closed_column \
  fixtures.task083.pg_migration.PGMigrationTests.test_pg_migration_02_nonempty_table_rolls_back_whole_005 \
  fixtures.task083.pg_close.PGCloseTests.test_pg01_close_settle_and_old_gc_does_not_touch_new_window \
  fixtures.task083.pg_close.PGCloseTests.test_pg02_closed_gate_rejects_admit_mark_but_records_outcomes \
  fixtures.task083.pg_close.PGCloseTests.test_pg03_close_commits_before_concurrent_admit_and_mark \
  fixtures.task083.pg_close.PGCloseTests.test_pg04_cancel_closes_gate_and_old_dispatched_unknown_converges
```

子进程环境仅设：PATH、SYSTEMROOT、COMSPEC、TEMP、TMP（OS 必需）+ `RETROLUME_TASK_083_DATABASE_URL`（指向本新库，值不记录）。夹具既有兼容 loop_factory 不动。

预期：6 实际运行、0 失败/错误/skip（DSN 已设，skipUnless 不触发）；failfast；任一失败/超时/skip/身份或清理未知立即停批，无修正重跑、无第二容器、第二 unittest 进程。

## 超时与预算

| 阶段 | 预算 |
| --- | --- |
| 总正常窗（runner 内） | 560s（卡面 600s 自创建起，runner 预留工具层余量） |
| 容器创建 | ≤30s，到期即停 |
| 就绪等待+身份核对 | ≤30s（自创建起），身份错配立即停 |
| 单 docker 检查命令 | ≤15—30s |
| unittest | 硬超时 120s，超时按精确 PID `taskkill /T /F`（仅本次进程句柄后代） |
| finally 收尾 | 各阶段预算截断 remaining()−65，保底 ≥65s；stop 应急 ≤60s |

## finally 停止办法

1. 确认测试子进程退出（proc.poll / 补杀+wait）。
2. 核对容器 ID（run 输出的准确 ID）+ 标签（retrolume-task=083 / retrolume-phase=pg08 / retrolume-run=20260925-1455），核对失败不 stop 不 kill，记 cleanup_incomplete。
3. `docker stop -t 10 <ID>` → `docker inspect` 确认 Running=false；stop 失败仅对同一核实 ID 一次 `docker kill` 再 inspect，应急 ≤60s 如实记录。
4. 停止后保留容器、库、schema、失败数据（不 DROP schema/database、不删容器/卷）；仅夹具成功路径按合成 UUID/FK 清理行数据（夹具自带）。
5. 无法确认则 cleanup_incomplete，不签整体通过。

## 证据文件清单（本目录）

- precheck.py / precheck-output.txt：一次只读预检（冻结hash/venv/Docker/镜像/端口）
- runner.py / runner-log.txt / runner-state.json：有限超时 runner 及其输出
- container-inspect-created.json / container-final-inspect.json：创建后与停止后脱敏 inspect
- unittest-stdout.txt / unittest-stderr.txt / unittest-meta.txt：唯一批次原始输出与元数据
- schemas.txt：夹具创建的 schema 清单（全部保留）

## 批次一（runTag 20260925-1455，容器 8b2b63497f9a…）：就绪超时停批

- 结果：容器创建成功、标签核对 OK，就绪/身份核对 30s 超时 → BLOCKED_READY_TIMEOUT；unittest 未启动（六例 not_run）；finally 干净（stop 成功、Running=False、cleanup_ok=True）。容器与匿名卷保留。
- 根因（容器日志+runner-state.json ready_last_error 证实）：runner 就绪检查 SQL 将 PG 裸关键字 `current_user` 误写为 `current_user()`，服务器持续报 `syntax error at or near "(" at character 40`；连接/认证/库创建全程正常。属本轮证据目录内检查脚本自身缺陷，非环境/夹具/被测对象缺陷。
- runner 缺陷修正（留档于本 runner.py 当前版本）：修正01 就绪 SQL `current_user` 裸关键字；修正02 `proc = None` 预初始化消除 finally 早期路径 NameError；新增 SyntaxError/ProgrammingError 立即停分类（BLOCKED_CHECK_SQL_DEFECT）。
- **例外授权（用户 2026-09-25 15:10+08:00 明确回复"授权例外重跑"）**：允许用修正版 runner + 新 runTag `20260925-1509` 再创建一次容器完成六例；批次一容器保留作证据，不删除、不重启。批次二为最终运行，仍受全部卡面预算/停批纪律约束。

## 批次二（runTag 20260925-1509，容器 10faef609560…）：身份核对缺陷停批

- 结果：容器创建成功、标签核对 OK，连接 1.62s 即成功，但身份核对判 `port=5432 ≠ 55437` → BLOCKED_IDENTITY_MISMATCH；unittest 未启动；finally 干净（Running=False、cleanup_ok=True）。容器保留。
- 根因：runner 第二处检查缺陷——`inet_server_port()` 返回 PG 在**容器内**监听的端口（5432），非宿主映射端口；db/user 核对全部正确，宿主 55437 绑定归属由 inspect port_bindings 证实。仍属检查脚本语义错误，非环境/夹具/被测对象缺陷。
- 修正03：身份核对改为 db/user/容器内端口 5432 三核对；宿主 55437→5432 归属在创建后 inspect 阶段以 port_bindings 显式核对（HostIp=127.0.0.1、HostPort=55437）。
- **批次三授权（用户 2026-09-25 15:15+08:00 明确回复"授权批次三"）**：runTag `20260925-1515`，最终运行，全程受卡面预算/停批纪律约束；批次一/二容器保留作证据。

## 批次三（runTag 20260925-1515，容器 b8b7982f85ff…）：六例全部通过

- 流水：创建 0.41s → inspect 标签 OK + 宿主端口绑定核对 OK（127.0.0.1:55437→5432）→ PG 17.11 就绪+身份三核对一致（1.64s）→ unittest 单进程 failfast 六方法 exit=0、包装墙钟 2.78s（unittest 自报 Ran 6 tests in 1.897s）→ finally 核对 ID/标签后 stop 成功 → Running=false、cleanup_ok=true（总耗时 5.49s）。
- **六例逐项：全部 ok，0 失败/0 错误/0 skip，failfast 未触发**（unittest-stderr.txt 原始行）：pg_migration_01 空表仅增 dispatch_closed；pg_migration_02 非空整体回滚；pg01 关门结算+旧G幂等不碰新窗；pg02 关门拒 admit/mark 且记 outcome；pg03 关门先提交先于并发 admit/mark（真实来源锁+屏障）；pg04 取消关门+旧 dispatched UNKNOWN 收敛。
- schema 清单（全部保留，无失败保留行=夹具成功路径 FK 清理行数据）：task083_migration_91f93dae…、task083_migration_b0bae76d…、task083_close_cdef47ba…、task083_close_8fed9a16…、task083_close_6d1cda74…、task083_close_97643930…（全量见 schemas.txt / unittest-stdout.txt）。
- 版本：Python 3.12.10（项目 venv）、psycopg 3.3.5、PostgreSQL 17.11 (Debian 17.11-1.pgdg12+2)、Docker server 29.7.2、镜像 pgvector/pgvector:0.8.6-pg17-bookworm（sha256:cf134a…）。
- 运行后核验（post-run-hash-check.txt）：四冻结文件 hash 全 MATCH 零漂移；git status backend/ 仅含 083 既有实现差异（与卡面既有差异保护一致，非本批写入）；本批写入仅限本证据目录与 Ndocu/results/TASK-083-result.md 置顶段。
- **verdict 更正**：runner-state.json 显示 verdict=TESTS_FAILED 系 runner 第三处缺陷（结果解析只查 stdout，而 unittest 的 Ran/OK 摘要写 stderr）所致误标；**批次三最终裁定以 unittest-stderr.txt 原始输出（六行 ok + Ran 6 tests in 1.897s + OK）+ 退出码 0 为准 = 全部通过**。runner 解析层已修正（修正04）并留档；批次三实际运行脚本字节副本 runner-batch3-as-run.py（sha256=52ba7c4486f74a057ce12e0994e2d263fa9f2d110625a60bd07da32940c74933）与 state 原样保留，不覆盖。
- 三个批次容器（8b2b6349… / 10faef60… / b8b7982f…）全部保留（含各自匿名卷、库 retrolume_task083_pg08 两实例——批次一二为同名库各自卷内实例、批次三含 6 schema），均 Running=false，未删除任何容器/卷/schema/database。
