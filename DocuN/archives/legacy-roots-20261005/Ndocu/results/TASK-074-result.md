# TASK-074 结果（R-068 / STEP-008 局部 / 父TASK-073）

- 执行者：Work Buddy / GLM-5.3-Flash，B档（沿 073 会话接续）
- 执行时间：2026-09-21 13:19—13:21（Asia/Shanghai）；runTag=20260921T1319-wbB1
- 建议结果：**通过（限定本卡范围）**——测试夹具定向修复＋同卡真实 PG 验证完成；六例实际运行 0 失败/错误/skip，六表清零，收尾确认。不代表完整 G-1/STEP-008/项目完成。

## 一、预检（全部通过）

- Docker server 29.7.2；镜像在位 `sha256:cf134a76…f8e6f`（pgvector/pgvector:0.8.6-pg17-bookworm）；55435 空闲；项目 venv 可用。
- 修改前冻结 hash 四文件与 073 冻结值全部一致（test ef705113… / repository 50ec537b… / 001 767f47c3… / 002 3a9c5855…），无不明快照。
- 其余导入文件 hash：activities/__init__ 31d0b60c…、capabilities/__init__ 9e38cf88…、runtime 067021e1…。
- 版本：Python 3.12.10、psycopg 3.3.5、PostgreSQL 17.11 (Debian 17.11-1.pgdg12+2)。

## 二、唯一改动（夹具定向修复）

- 文件：backend/tests/test_activity_recovery.py，test_01 内读取操作结果的 SELECT 投影增加 execution_generation 列（一行查询拆为两行字符串拼接，语义仅补该字段）；全部断言、其余五用例、清理顺序、生产代码、DDL 均未动。
- hash：修改前 ef705113fbf6af83a0a29e99b40dfdb68109282c0ae8b724790e1d440575d246 → 修改后 **7839af04e3043a173f8caaeefd5085ff72e138891207a0e882d8b2ef585d15e4**。
- 证据：test_activity_recovery.py.before（修改前副本）、test-fix.diff（unified diff，仅此一处）、fix-hash-compile.json。
- compile 检查：内置 compile 通过，0.015 秒，未写 pyc。未复现旧 KeyError，未扩大修复范围。

## 三、容器与迁移

- 唯一容器 `retrolume-task-074-pg-20260921T1319-wbB1`，ID `7ef8f17e0ded014832ead684ddc5cf224fe91f0a4b38e953e2b6a467c7a4b3cc`，标签 retrolume-task=074 / retrolume-run=20260921T1319-wbB1；1CPU/512MiB/pids128/restart=no/无宿主挂载（自动卷 /var/lib/postgresql/data）/仅 127.0.0.1:55435→5432。同名冲突检查通过。
- 旧 073 容器 da18c806…2a62 仅只读确认（保留、exited、未触碰）；未操作任何历史容器/用户库。
- 库 retrolume_task074_synthetic、专用合成账号（口令仅存证据 run-result.json，不在本文件复述）。PG 就绪约 1.5 秒。
- 迁移 001、002 各一次，stdin 传 `psql -v ON_ERROR_STOP=1 -f -`，均 rc=0。未执行 003、未调用 run_ledger_check.py。

## 四、测试运行（唯一一次，failfast）

命令（cwd=backend，项目 venv，仅本次子进程环境设 RETROLUME_TASK_068_DATABASE_URL 指向新库）：

    ./.venv/Scripts/python.exe -B -m unittest -f -v tests.test_activity_recovery

- exit_code=0；`Ran 6 tests in 3.630s`；**OK**。耗时 5.5 秒，未超时；实际启动次数 1，无重试。
- 逐例状态（原始输出 test-output-utf8.txt / test-raw-output.bin）：
  - test_01_valid_lease_does_not_block_finding_and_converging_old_generation：ok（含原 195 行 execution_generation 断言）
  - test_02_repeat_converge_is_noop_and_invalid_input_rejected：ok
  - test_03_existing_terminals_kept_and_reservation_not_refunded：ok
  - test_04_listing_is_bounded_paginated_and_isolated_per_activity：ok
  - test_05_late_permit_cannot_overwrite_recovered_unknown：ok
  - test_06_bounded_single_batch_converges_incrementally：ok（卡内验收的分批 2/2/1/0、不变量与 limit 校验为该例内部断言，随例通过）
- 0 skip。

## 五、六表清零核对（只读）

    material_sources=0, material_versions=0, activities=0,
    activity_scope_sources=0, activity_allowed_models=0, activity_operations=0  → all_zero=True

## 六、收尾与资源保留

- 测试子进程（pid 39864）自行退出。finally 按核实 ID+标签（identity_verified=true）docker stop -t 10 成功；复验 Running=false / Status=exited / ExitCode=0 / FinishedAt 2026-09-21T05:21:36Z。未用 kill，无 cleanup_incomplete。
- 容器与数据卷保留未删（restart=no 不自启）；容器日志尾部已存证据。总耗时 16.1 秒，远小于 10 分钟窗口，无应急。

## 七、证据路径（均在 Ndocu/evidence/task-074/20260921T1319-wbB1/）

precheck.py / precheck.json / precheck-stdout.txt（旧 hash 核对、版本、端口）
test_activity_recovery.py.before（修改前副本）；test-fix.diff；fix-hash-compile.json（新 hash + compile）
run_task074.py（限时监督控制脚本，复用 073 结构仅换标识）/ run-log.txt / run-stdout.txt / run-result.json（含合成口令，勿外传）
docker-run-stdout/stderr.txt；container-inspect-created.json
migration-001_materials-stdout/stderr.txt；migration-002_activities-stdout/stderr.txt
test-raw-output.bin（字节级原始）/ test-output-utf8.txt
container-logs-tail.txt；verify_cleanup.py / cleanup-verify.txt（停止后非敏感 inspect + 073 旧容器状态）
结果文件：Ndocu/results/TASK-074-result.md

## 八、限制与未验证

- 无独立并发/时钟/性能验证；不外推任何相应保证。本次仅为限定真实 PG 合成验证，不证明 M-1、完整 worker 接线。
- 修复仅触及测试投影，产品代码未变（repository 仍 50ec537b…），072 审计结论继续适用，不要求重跑。
- run-result.json 含本容器专用合成口令，本地合成凭据，仅证据绑定用。

## 九、文档建议 / 下一步（交 Astra）

1. 建议 Astra 将 test_activity_recovery.py 新冻结 hash 7839af04… 登记入执行状态/架构对应条目，合并 068/069/070/071/072/073/074 证据链，复核真实 PG 条件是否关闭。
2. 本卡变更（测试夹具一行投影）建议在 docu/CHANGE.MD 登记一条 CHG（按独占边界本卡未写 docu/，登记由 Astra 完成）。
3. 073 的 FAIL:test_run 状态可由本次结果取代；其容器 da18c806…2a62 及本卡容器 7ef8f17e…0b3cc 均保留，是否清理由 Astra/用户决定（需授权删除）。
4. 后续真实 PG 条件关闭后，M-1、worker 接线与完整 STEP-008/G-1 仍按既有门槛另行验证；本卡不宣告。

## 十、必要人工操作

- 无必需项。两个保留容器（073/074）如需删除，须人工或新卡授权。
