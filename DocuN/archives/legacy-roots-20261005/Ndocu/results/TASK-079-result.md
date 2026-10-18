TASK-079 / R-073 时间账本定向真实 PG 验证结果（置顶，2026-09-23 续跑完成）

TASK-079 / R-073；定向真实 PG 验证；STEP008 局部；父 TASK-077；审计关联 TASK-078 review-02+03；NFR002/003、SEC002、FLOW005、DATA007。需求 v1.1、架构 v0.30、执行状态 v1.31。
执行窗口：Work Buddy 执行 Agent（模型自报标识 DeepSeek-V4.1-Flash，如实登记；与 077 修正轮02 同窗口延续，型号不一致不作重做理由）。
runTag：20260923T1508-wbC2（一个批次、一个容器、unittest 仅一次启动，预算未超）。
证据目录：Ndocu/evidence/task-079/20260923T1508-wbC2/。
历史：环境阻塞轮 runTag 20260923T1456-wbC1（Docker daemon 未运行，零消耗，证据 Ndocu/evidence/task-079/20260923T1456-wbC1/precheck-blocked.log），用户启动 Docker Desktop 后授权续跑。

总结论：通过（本卡验证范围）。
22 例真实 PostgreSQL unittest 全部 ok（0 失败/0 错误/0 skip）；004 迁移三库真实运行；目录约束逐项命中；reject 库非空拒绝且无部分 DDL；18 项约束反例/正例全部按预期 SQLSTATE+约束名命中；budget 库业务测试后六表清零。本结论不证明 worker 并发、M-1 解决、STEP008 完成或整项目完成。

一、证据导航

- 运行控制：run_task079.py（part1，FAIL:reject_004 于 12.0s 停止）、run_task079_part2.py（part2 补做，PASS，16.8s）。
- 运行结果：run-result.json（part1）、run-result-part2.json（part2，口令已脱敏）；run-log.txt / run-log-part2.txt。
- 容器：docker-run-stdout/stderr.txt、container-inspect-created-sanitized.json（Env 脱敏）、container-logs-tail.txt；停止后 Running=false 记录于 run-result-part2.json cleanup。
- 迁移：migration-<库>__<迁移>-stdout/stderr.txt（8 份成功）+ part2-reject-004-stdout/stderr.txt（预期失败）。
- 目录核对：catalog-budget.json、catalog-ledger.json、catalog-reject-snapshot.json。
- 反例批次：part2-counterexample-batch.json。
- unittest：test-raw-output.bin（原字节）、test-output-utf8.txt。
- hash：run-result.json frozen_hashes（开始前）、hashes-post-run.json（结束后，_ALL_OK=true）。

二、版本与资源记录

- Docker server 29.7.2；固定镜像 sha256:cf134a76…60f8e6f 在位（未拉取/构建）。
- PostgreSQL 17.11 (Debian 17.11-1.pgdg12+2)；backend/.venv Python 3.12.10；psycopg 3.3.5。
- 容器 retrolume-task-079-pg-20260923T1508-wbC2，id c854db7cf1723d5b1d192a00834c216560b54aa07bfdf900114bb6d0f6eec9eb；标签 retrolume-task=079 / retrolume-run=20260923T1508-wbC2；1 CPU、512MiB、pids 128、restart=no、无宿主挂载、bridge 网络、仅 127.0.0.1:55436→5432。
- 三专用库：retrolume_task079_budget / retrolume_task079_ledger / retrolume_task079_reject；合成账号 retrolume_t079；口令全程未写入任何证据文件。

三、冻结 hash（开始前核对 + 结束后绑定，8 文件全部相符，无漂移）

repository.py 045a3cf8…2534、__init__.py 6bdb9609…a46dd、001 767f47c3…7a8d、002 3a9c5855…dda6、004 8f04f57c…97cc、time_budget 63a19d1f…1a86、ledger fb174d4c…de63da、recovery 0e5d9c89…bf7a。

四、迁移与目录约束核对（可观察标准第 3 项）

1. 三库各应用 001/002 一次（psql stdin，ON_ERROR_STOP=1，原 SQL 全文，rc=0）；budget/ledger 在 activities 空表上应用 004 各一次（rc=0）。003 未运行（无本卡依赖），不宣称完整用户库升级通过。
2. budget/ledger 目录实测：五新列类型（bigint/bigint/bigint/integer/bigint）、3 NOT NULL、2 DEFAULT 0、004 新增 8 个 CHECK（列级 5 + 表级 3）逐项命中；全表 CHECK 总数 20（含 002 既有 12 条），按卡不作"全表仅 8 条"断言；核对按 pg_catalog 逻辑匹配（名称+关键谓词），未用脆弱整串相等。

五、reject 库非空拒绝（第 4 项）

1. 仅 001/002；插入一行旧模式合成 activities（pending、id 7f1e5f64-7b62-4a3f-8b1d-02090923a079、有效必填限额、无来源依赖），DDL 前快照已存。
2. 004 尝试一次：psql rc=3（非零），stderr 含 RAISE EXCEPTION "activities 非空：004 仅允许在空 activities 合成库执行，本事务已回滚"，非连接/权限/语法错误。
3. 新连接核对：样本行保留、五新列均不存在、约束名与列结构与快照完全一致、无部分 DDL。样本保留未清空，004 未重跑。

六、约束反例/正例批次（第 5 项，budget 库，18 项全部命中）

反例（各独立事务，SQLSTATE 23514 + 实际 constraint_name 确认命中）：M=0、M=2147483648 → activities_max_running_seconds_check；R=−1 → activities_running_reserved_seconds_check；S=−1 → activities_running_settled_seconds_check；gen=−1/sec=0 → activities_last_settled_generation_check；sec=−1/gen=0 → activities_last_settled_seconds_check；running 样本（executor+lease 齐）R=300>M−S → activities_time_budget_balance；pending 且 R=50、running 且 R=0（executor+lease 齐）→ activities_time_budget_running_shape 两向；gen 有值/sec NULL 与反向 → activities_time_budget_last_settled_pair。
NOT NULL：M/R/S 各设 NULL → 23502（PG 17 列 NOT NULL 无约束名，constraint_name=None，按 SQLSTATE 判定命中）。
正例（验证后回滚）：NULL/NULL 合法；0/0 合法；省略 R/S 读回 0/0；M 上界 2147483647 合法。
批次结束 budget 六业务表全 0，方进入 unittest。

七、unittest（第 6 项，唯一一次启动）

命令：backend cwd 下 ./.venv/Scripts/python.exe -B -m unittest -f -v tests.test_activity_time_budget tests.test_activity_recovery tests.test_activity_ledger。
环境：RETROLUME_TIME_BUDGET_TEST_DATABASE_URL 与 RETROLUME_TASK_068_DATABASE_URL → budget 库；RETROLUME_TASK_048_DATABASE_URL → ledger 库；缺变量即 skip 的保护未触发（DSN 全部注入）。项目既有 Selector loop（psycopg_compatible_loop_factory）未改动。
结果：Ran 22 tests in 9.758s，OK；exit 0；无超时（实际 11.8s）；逐项状态 22/22 ok，0 失败/0 错误/0 skip。time test_08 使用现名 test_08_ceiling_rounding_zero_and_fold_reclaim_partial_window（window_seconds=79 断言通过）；recovery test_06 的 2/2/1/0 分批收敛断言通过（verbose 输出因名称过长换行，ok 在续行，已核对原字节）；ledger test_02 并发重复准入为既定用例，未额外加压。

八、三库行数（第 7 项）

- budget：六表全 0（新测试/recovery 定向 tearDown 生效）。
- ledger：material_sources 1、material_versions 1、activities 1、activity_scope_sources 1、activity_allowed_models 1、activity_operations 0——ledger 套件仅 setUp 全清、末例遗留合成行，按卡不判失败、不手工删除凑 0，如实记录并保留。
- reject：activities 1（第 4 项样本），其余 0。

九、收尾（第 8 项）

unittest 子进程自然退出（exit 0）；对核实 ID+标签停止容器（docker stop rc=0），inspect Running=false；容器/三库/卷全部保留未删除；docker logs 尾部已存。

十、偏差与风险（如实登记）

- D-079-1：part1 运行器自身缺陷——reject 库"尝试 004 一次"步骤漏实现，流程在 reject_004 阶段按停止条款退出（verdict=FAIL:reject_004，12.0s，12 秒消耗）。part2 于同一容器补做缺失步骤（reject 004、反例批次、unittest、行数、停止），未新开容器/批次；unittest 首次启动发生在 part2，"最多一次"预算未突破；运行窗口径自 part2 起计，part1 运行窗已超时如实登记。
- D-079-2：part1 合成口令按脱敏设计仅存进程内存，未持久化；part2 经容器内本地通道重置本卡合成账号口令一次（新口令仍不写明文证据）。
- 期间无产品/测试/迁移修改；part1 失败分类为夹具/运行器缺陷，非产品缺陷。
- 遗留观察：ledger 库末例遗留 5 行合成数据（见第八节），属现成测试行为，如需清理由后续卡裁决。

十一、未验证边界

1. 不证明 worker 并发消费、M-1 解决、STEP008 完成、整项目完成；不证明 003 及完整用户库升级。
2. 未做并发压力、时钟回拨、崩溃恢复、EXPLAIN、锁竞争加压（按卡不要求）。
3. PG 运行额度：本卡新增批次已按预算使用一次（part1+part2 同批次延续）；历史 073/074 额度未挪用、未重置。
4. 本卡不填写编排最终验收；正式状态与 CHANGE 由编排维护。
