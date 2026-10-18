# TASK-073 结果（R-067 / STEP-008 局部 / 父TASK-071）

- 执行者：Work Buddy / GLM-5.3-Flash，B档，新会话
- 执行时间：2026-09-21 12:55—12:58（Asia/Shanghai）；runTag=20260921T1254-wbA1
- 建议结果：不通过（本卡验收未达成）。区分：本次失败为**测试自身代码缺陷**，非产品/repository 缺陷；产品断言在失败点之前全部通过。

## 一、预检（全部通过）

- Docker server 29.7.2 可达；镜像在位 `sha256:cf134a76…f8e6f` = pgvector/pgvector:0.8.6-pg17-bookworm；55435 空闲；项目 venv python 可用。
- 冻结 hash 四文件全部一致：repository.py 50ec537b…、test_activity_recovery.py ef705113…、001_materials.sql 767f47c3…、002_activities.sql 3a9c5855…。
- 其余实际导入文件 hash：app/activities/__init__.py 31d0b60c…、app/capabilities/__init__.py 9e38cf88…、app/runtime.py 067021e1…。
- 版本：项目 Python 3.12.10、psycopg 3.3.5；PG 实际 PostgreSQL 17.11 (Debian 17.11-1.pgdg12+2)。未做 3.13 重复测试（按卡）。

## 二、容器与迁移

- 唯一容器 `retrolume-task-073-pg-20260921T1254-wbA1`，ID `da18c806a871780500df3bdf2b612632afa7c5721e122e80437b6c248c1d2a62`，标签 retrolume-task=073 / retrolume-run=20260921T1254-wbA1；1 CPU、512MiB、pids-limit 128、restart=no、无宿主挂载（自动卷 /var/lib/postgresql/data）、仅 127.0.0.1:55435→5432。同名冲突检查通过（无历史同名）。
- 库 retrolume_task073_synthetic、专用合成账号（口令仅存本卡证据 run-result.json，不在本文件复述）。PG 就绪约 1.6 秒。
- 迁移 001、002 各一次，经 stdin 传原文件 `psql -v ON_ERROR_STOP=1 -f -`，均 rc=0，无错误输出。未执行 003、未运行 run_ledger_check.py。

## 三、测试运行（唯一一次，failfast）

命令（cwd=backend，项目 venv，仅子进程环境设置 RETROLUME_TASK_068_DATABASE_URL 指向新库）：

    ./.venv/Scripts/python.exe -B -m unittest -f -v tests.test_activity_recovery

- 结果：exit_code=1；`Ran 1 test in 0.580s`；`FAILED (errors=1)`。耗时 1.7 秒，未超时，无重试、无改码。
- 六例状态：
  - test_01_valid_lease_does_not_block_finding_and_converging_old_generation：**ERROR**
  - test_02…test_06：**not_run**（-f failfast，test_01 出错即停）

### 失败点与定性

原始错误（test-output-utf8.txt / test-raw-output.bin 原样保留）：

    File "backend/tests/test_activity_recovery.py", line 195, in test_01_…
        self.assertEqual(rows["current-2"]["execution_generation"], 2)
    KeyError: 'execution_generation'

定性依据（静态核对冻结测试文件，hash ef705113… 一致）：
- test_01 内该处 rows 来自测试自身的查询：`SELECT operation_id, state, disposition, error_code, dispatch_started_at, recorded_at FROM activity_operations …`（第 182—183 行），**SELECT 列表不含 execution_generation**，但第 195 行断言 `rows["current-2"]["execution_generation"] == 2`。行字典不可能含未查询列，属测试自身查询列缺失的代码缺陷。
- 失败点之前的**产品行为断言全部通过**（按执行顺序）：新代次 reclaim generation+1、list_unresolved_operations 三项内容/代次/dispatch_started_at/admission_id、recover_obsolete_operations 返回 2、旧 reserved→unknown、旧 dispatched→unknown+executor_lost、current-2 保持 reserved。即 KeyError 发生前没有任何产品断言失败。
- 不能据此外推：test_01 第 195 行之后的断言未评估；test_02—06 全部未运行；分批 2/2/1/0（test_06）、六表清零（步骤5）均未验证。第 5 步六表核对按卡仅在全部成功后执行，本次未执行，库现场原样保留在容器卷中。

## 四、收尾与资源保留

- 测试子进程（pid 39856）自行退出，无需终止。
- finally 按核实 ID+标签（identity_verified=true）执行 docker stop -t 10，成功；复验 State.Running=false、Status=exited、ExitCode=0、FinishedAt 2026-09-21T04:58:03Z。未使用 docker kill。
- 容器与数据卷**保留未删**（restart=no，不会自启）；容器日志尾部已存证据。未触碰任何历史容器/用户数据库/全局环境。总耗时 12.8 秒，远小于 10 分钟窗口，无应急。

## 五、证据路径（均在 Ndocu/evidence/task-073/20260921T1254-wbA1/）

precheck.py / precheck.json / precheck-stdout.txt（hash、版本、端口）
run_task073.py（最小运行控制脚本：限时、监督子进程、finally 收尾）/ run-log.txt / run-stdout.txt / run-result.json（含合成口令，勿外传）
docker-run-stdout.txt / docker-run-stderr.txt / container-inspect-created.json
migration-001_materials-stdout.txt / -stderr.txt；migration-002_activities-stdout.txt / -stderr.txt
test-raw-output.bin（字节级原始）/ test-output-utf8.txt
container-logs-tail.txt / verify_cleanup.py / cleanup-verify.txt（停止后 inspect 非敏感字段）

## 六、限制与未验证

- 无独立并发/时钟/性能验证；六例未全部运行，不外推任何相应保证。
- run-result.json 内含本容器专用合成口令，属本地合成资源凭据，仅用于证据绑定，不适用真实凭据。
- 本卡无代码改动，无需重跑 072 审计；hash 与冻结一致。

## 七、建议与下一步（交 Astra 裁决，不在本卡修）

1. 测试缺陷（本卡唯一确定发现）：test_01 第 182—183 行 SELECT 需补 `execution_generation` 列（与第 195 行断言一致）。此为测试文件改动，须新卡授权后修改并同步冻结 hash；本卡未改任何文件。
2. 修复后建议重开同类真实 PG 卡（新 runTag/容器），完整跑六例+六表清零，方可关闭 071/068 的真实 PG 条件。
3. 静态观察（非运行结论）：test_02—06 的 SELECT 列与断言列初步核对一致，未发现同类缺列；仅 test_01 存在此问题。
4. 建议人工/Astra：将本结果登记 PROJECT_EXECUTE_STATE（R-067 段）及 CHANGE.MD；本卡按独占边界未写 docu/，登记由 Astra 完成。
5. 下一步编号建议沿当前登记顺延（结果返回后由 Astra 定）；本卡不宣告 G-1、STEP-008、TASK-08 或项目完成。

## 八、必要人工操作

- 无必需人工环境操作。容器/卷保留，若 Astra 决定丢弃，需人工或新卡授权删除 `retrolume-task-073-pg-20260921T1254-wbA1` 及其匿名卷。
