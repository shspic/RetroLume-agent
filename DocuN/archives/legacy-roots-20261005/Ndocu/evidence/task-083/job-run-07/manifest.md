# TASK-083 job-run-07 运行前 manifest

- 日期：2026-09-25（UTC+8）；执行窗口：接续083实现窗口（GLM-5.3-Flash），本卡为受控验证卡，非独立审计。
- 卡号：TASK-083 / R-077 — 受控真实Windows Job验证07；原卡存档 Ndocu/archives/TASK-083-before-job-run07-20260925.md。
- 授权依据：用户2026-09-24批准082内部单窗监督与合成验证；084 review-05 关闭现有Job夹具全部确定阻断；本卡为编排对现有Job01—05的一次解冻运行，PG/新D1入口/旧G恢复仍冻结。

## 冻结值核对（运行前，只读，prep_run07.py → pre-run-check.json）

卡面运行链四文件 SHA-256 全部 MATCH：

| 文件 | SHA-256 |
| --- | --- |
| backend/tests/fixtures/task083/job_batch.py | 648e419cea693aa10630326cb28176e010a82b9f2c3380c33b42169c19bdef5b |
| backend/tests/fixtures/task083/job_control.py | 5bc35bf185de71e3ce94aa1a12e3e2a1466e6fd372e5c3f5d6aca196233980d2 |
| backend/tests/fixtures/task083/scenario_child.py | 98f132f272b952c22ac887efbf8026c5b00ec618838b6d484a3deec3c73f3f36 |
| backend/tests/fixtures/task083/fixture.py | c9970b8ddc718da1a4e83c6d206a67f6bd000d715578e028c0a0964d9f53dc7f |

补充冻结复算（沿 stub-fix-05/final-hashes.txt 与 084 review-02/hashes.txt 记录，非卡面义务）：windows_job.py、session.py、command.py、worker_main.py、launcher.py、supervisor_ipc.py、supervisor_main.py、gate.py、test_worker_session.py 共 9 个直接依赖全部 MATCH 零漂移；信息项 repository.py、005 亦未漂移。任何漂移=停对应运行，不覆盖。

环境文本核对（不用 import 探针试跑）：venv 解释器 backend/.venv/Scripts/python.exe 存在；backend/tests、backend/tests/fixtures/task083、backend/app/worker 存在；fixtures 无 `__init__.py`（PEP 420 命名空间包，`-m fixtures.task083.job_batch` 以 cwd=backend/tests 解析；job_batch.py 自身把 backend 加入 sys.path，scenario_child.py 把 backend 与 backend/tests 加入 sys.path，均经文本核对）。

## 命令（一次、唯一）

- 工作目录：`D:/shspic/project_NO3_RetroLume-agent/backend/tests`
- 解释器（绝对）：`D:/shspic/project_NO3_RetroLume-agent/backend/.venv/Scripts/python.exe`
- 参数：`-B -m fixtures.task083.job_batch`
- 场景次序（已审脚本内置，不得重排/不得单独补跑）：01 → 02 → 03 → 05 → 04

## 预算

| 层 | 上限 | 执行者 |
| --- | --- | --- |
| 单场景 | ≤30s（脚本内置：scenario deadline 25s / run deadline 20s，wait_for≤28s；04 deadline 20s） | job_control.py |
| 批 deadline | 55s（脚本内置 monotonic） | job_batch.py |
| 命令墙钟 | ≤60s（本包装硬限） | run_batch_07.py |
| 总准备/执行/收尾 | ≤10 分钟，收尾预留 ≤60s | 本卡窗口 |

## 记录方式（不以工具 yield 当进程已结束）

run_batch_07.py 以 subprocess.Popen 启动上述唯一命令：stdout/stderr 在 OS 层直接重定向到 `run-batch-stdout.log` / `run-batch-stderr.log`；真实退出码取自 `Popen.wait()`；计时单一来源 `time.perf_counter`（附 epoch 起止时间戳，UTC+8）；60s 墙钟到点按超时处理。

## 停止条件（任一即停整批，不修复、不复跑、不启动余项）

首次断言失败（批内 stop_batch / 退出码 2）、超时（60s 墙钟或批内 deadline）、cleanup_incomplete、归属/树未知、句柄错配、总截止到达。旧 5 场景尝试、超时偏差与费用不重置；不追加任何场景或通用 runner/看门。

## 停止后的精确清理办法

- 仅处理本次 runTag/精确 PID+创建时间/已握句柄且归属已证的对象；不按 python 名/端口批量杀；旧不明进程一律不碰。
- 包装 60s 超时：对本包装启动的唯一批进程 PID 执行 `taskkill /PID <pid> /T /F`（归属已证=我们启动的进程树），随后按控制器已打印的精确 PID+创建时间做只读残留核验（post_check_07.py：OpenProcess+GetProcessTimes 与记录的 created_100ns 比对）。
- 残留对象仅当"同 PID 且同创建时间"才实施精确 taskkill /PID /F；归属不明则保留并报告最少人工处置需求；不以只杀批入口掩盖未收束子树。
- 清理确认以控制器输出（active_processes_at_end / cleanup_incomplete / worker signaled）为权威观察事实；补充名称扫描仅作旁证，不充当树空证明。

## 证据目录（仅本目录写 manifest/原始日志/meta/hash/只读记录）

`Ndocu/evidence/task-083/job-run-07/`：prep_run07.py、pre-run-check.json、本 manifest、run_batch_07.py、run-batch-stdout.log、run-batch-stderr.log、run-batch-meta.json、post_check_07.py、post-run-check.json。不得复制环境变量/DSN 等敏感信息入日志。结果写 Ndocu/results/TASK-083-result.md 置顶并保留历史。

## 序列化与资源边界

本批串行独占本 Job 夹具进程；无并行测试、服务操作、代码修改；无真实模型/网络/HTTP/用户数据/PG/Docker；不读私有配置或凭据；不安装；不 Git 提交/推送；不改源码/夹具/迁移/正式docu/公共库/旧证据。活动 UUID/runTag/事件名均为随机专用（每次运行 uuid4 新值，冲突由 _new_event_or_reject 显式拒绝）。
