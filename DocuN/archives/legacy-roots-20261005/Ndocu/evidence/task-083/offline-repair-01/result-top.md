# TASK-083 / R-077 / STEP008 执行结果：离线补足轮01（当前有效）

**结论：内部监督候选实现与受控验证准备已补足；真实 Job、005/PG、产品供应商路径及独立安全审计均未通过或未运行，不可接线放行。** 本窗口实际标签 GPT-6，仍是 083 实现者而非独立审计。原初批 5 个 Job、一次修正、第04场景超时与归属缺证及旧原始日志不清零；下方保留初批结果原文。没有宣告 M-1 或 STEP008 完成。

## A—E 完成映射与接口

| 项 | 本轮可审查实现 | 限制 |
| --- | --- | --- |
| A 命令与 SUP 边界 | 新 `WorkerCommand` 只接受本地绝对可执行文件、不可变有界参数及工作目录；SUP 不再调用 `command_for_lease` 任意同步函数。新 `run_supervised_window` 是阻塞的内部入口，拒绝在运行中的应用事件循环调用；Windows `multiprocessing.spawn` 专用子进程持 Job/活动所有权，父启动器在创建前固定总管理 deadline，凭精确 `Process` 对象有限 join→terminate→kill，未知结果失败关闭。子进程使用现有 `psycopg_compatible_loop_factory`。默认 W90、启动5、请求10、停止预留5、管理额外30秒，关系由 `SessionConfig` 检查；partial W 不开工。 | 真实进程/PG组合 not_run；父启动器自身死亡时由旧树未知恢复规则失败关闭，未宣称任意系统挂死下硬实时。 |
| B 收尾与账本语义 | `SingleWindowSupervisor.run_once` 所有路径在 Job 终止/查询/close、互斥释放之后构造结果；首个异常类型保留，后续清理异常逐项记录。取消重抛并附 `session_outcome`。结果分 `settled_seconds`（本窗确认进入 S）、`reserved_seconds`（确认仍占 R）与 `pending_fold_seconds`（待原规则折叠）；claim 或 settle 提交响应不明时字段为 `None`，不再谎称 0 或已收费。只有 Job 树 0、主进程成功、C≥1且 C≤W 后才关 DB 门并按原 G/W/C 有限重试结算。 | claim 未知语义、子进程兼容循环属于纯单元之后的定向源码补正，最终动态验证 **not_run**；整树事实仍须真实 Job 验证。 |
| C 内部发送门 | `run_controlled_worker` 将唯一 `ClosingCallGate` 交给注入 work；门先原子 closed 再等活跃调用归零，令牌包住假 gateway 的 admit→mark→send→record，全链纯单元观察了已 mark 未 send 时新令牌被拒、在途收尾后退出。未来 Job01 的 `controlled_fast` 合成 worker 入口也调用真实 `run_controlled_worker`，不接供应商。 | `WorkerCommand` 是内部命令数据，不证明未来产品 worker 必然调用受控入口；产品接线需独立审查该约束，未授权修改 gateway 主体。 |
| D 可控 Job 准备 | 第04场景改成 base Python 稳定进程句柄，并按本机 Python 3.12 Windows spawn 源码设置 `__PYVENV_LAUNCHER__` 保留 venv 依赖。父测试在 Resume 前有20秒独立截止、UUID/G/runTag/Job名/PID/进程创建时间、精确 Job/进程句柄及 ActiveProcesses>0；两个唯一命名事件各限5秒握手，父控制器有限管道读/等待，最终只用自身句柄收尾并输出身份与停止事实。Job01/02/03/05 也准备身份日志。 | 这些新场景 **not_run**；旧04进程列表 count0 仍不能补成旧Job整树正证据。01 合成 venv 转发器及子进程在同Job内，<=原4进程上限；04直接 base 解释器。 |
| E PG 可执行准备 | 新 `pg_close.py` 含当前代次 close/首次 settle 前置/最近旧 G/C 不改新窗、关闭后 admit/mark 拒绝而 RECEIVED/UNKNOWN/NOT_SENT 可收敛、真实来源锁→活动锁并发次序及 cancel 残留；新 `pg_migration.py` 在随机自建 schema 上准备 001—005 空表成功/非空事务回滚。仓储用例仅以本例 UUID 和 FK 顺序清理；仅 `RETROLUME_TASK_083_DATABASE_URL`，缺失明确 skip，无应用/用户 DSN 回退。 | 005 未执行，全部 PG **not_run**；旧001—004未改。精确测试ID及既有受影响ID见本轮 `manifest.md`。 |

内部接口清单：`WorkerCommand`（纯数据）、`run_supervised_window`（产品未来唯一应接的阻塞 launcher）、`SingleWindowSupervisor.run_once`（仅子进程/替身调用）、`SessionConfig`、`SessionOutcome`、`run_controlled_worker`、`ClosingCallGate`、`NamedJob`/`ActivityMutex`。产品 HTTP/真实供应商入口仍未接线。SUP 时序是活动本地/Win32排他→旧Job确切身份与 ActiveProcesses 0→t0→claim 明确返回→唯一 Job/悬停 worker→固定 stop/deadline→Resume→整树0→关闭 Job 句柄→DB close→settle→释放所有权；kill/超窗/未知不退款且不开新工。默认 q≤50ms 轮询、g=5秒；调度和内核终止误差不作硬实时保证。`repository.py`、005 hash 未变。

## 差异、hash 与验证

改前版本与 SHA256 在 `Ndocu/evidence/task-083/offline-repair-01/pre/`、`pre-hashes.txt`；最终全部逐文件 SHA256 在同目录 `final-hashes.txt`。关键旧→新：`session.py` `8E99B12B...→D317DB76...`，`windows_job.py` `3D0B5DAB...→D05CA259...`，`gate.py` `2186C7C8...→7E7588A5...`，`test_worker_session.py` `010DD38A...→0AC732AC...`；新增 `command.py`、`launcher.py`、`job_control.py`、`offline_unit.py`、`run_offline.py`、`pg_close.py`、`pg_migration.py`。冻结 repository `929320BAF55D625E897324AA76EBE543BDA86E73A4BF1C4766C7E552721C5B20`、005 `26B71A836355FA9620401F6BBB76E9A42668A1CE52077AA91ECB2F61EBEB50EB` 均保持。所有本轮新增/改动都在原083允许源码/测试或本轮证据与结果路径；不改正式 docu/公共库/旧证据/HTTP/gateway主体/PDF/依赖锁/Git，不安装/外发。

| 验证 | 真实命令与退出码 | 事实 |
| --- | --- | --- |
| 静态一次 | 项目根 `backend\.venv\Scripts\python.exe -B Ndocu\evidence\task-083\offline-repair-01\static_check.py`，exit 0；限定 `git diff --check -- backend/app/worker/__init__.py backend/app/worker/gate.py backend/app/worker/session.py backend/app/worker/windows_job.py backend/tests/test_worker_session.py backend/tests/fixtures/task083/fixture.py`，exit 0 | `static.log`；核对当时 AST、004/005/repository hash、显式测试选择。静态后又有定向源码/夹具修正，**不能把旧静态日志称为最终版本的 AST 通过**。 |
| 纯单元初批 | backend 根 `.venv\Scripts\python.exe -B tests\fixtures\task083\run_offline.py`，exit 1 | `unit-initial.log`；10项中9过，唯一失败是即刻返回 FakeJob 使合成 C=0，生产 SUP 按合同拒绝部分退款。 |
| 唯一修正复检 | backend 根 `.venv\Scripts\python.exe -B tests\fixtures\task083\offline_unit.py OfflineRepairTests.test_05_early_success_uses_tree_zero_close_then_same_g_settle_retry`，exit 0 | `unit-recheck.log`；只修该替身正耗时与 Job close→DB close→settle 的事件观察，1/1过。没有第二批 Job、没有 PG/OS 子进程。 |

真实纯单元命令耗时分别约0.35s、0.05s，单命令均小于60s。首次静态检查约11:23、单元初批约13:43，**整段墙钟跨越180秒上限**：中间 `exec_command` 自动审批因用量限制未完成审核，明确拒绝动作是纯单元命令，理由是审批用量限制而非认定不安全；该次命令未执行、无日志或遗留进程。用户随后明确要求继续，断点核对后才执行；未借此重置083 Job预算。上述超时偏差保留。离线补足的修正次数为一次单元失败修正及仅失败项复检；其后发现 claim 响应丢失不能报 R=0、子进程事件循环兼容性和合成入口问题，已作定向源码补正，**没有追加测试额度或声称这些补正动态通过**。

## 后续审查与运行门

先由新窗口独立增强**只读审查最终源码**与 `job-initial.log`、本轮原始单元日志及 `final-hashes.txt`，重点核对 DB 门与本地发送门、退款/取消/未知交错、SUP/Job 精确归属和最后句柄、重启预算不重置、late claim/settle 响应以及本轮后补代码。实现者不签安全通过。审查后由编排另定真实 Job 预算；最小受影响场景为原失败01正常早停退款、原失败04 SUP死亡/最后句柄，以及 session 终止/清理改变牵动的02挂死全额预扣、Job身份与创建时间/主退子存牵动的03。原05同名碰撞旧局部行为通过但身份记录不足，由独立审查决定是否占新预算复检，不能把旧PASS说成身份验收。专用PG按本轮 manifest 的两个 migration 与四个仓储确切ID定向运行，随后只挑受影响旧 time-budget 01/02/06/08、ledger 01/05/06/07、recovery 01/03/05；均须编排另定预算，当前 not_run。

文档建议：编排在正式执行状态记录“083离线候选已补、Job/PG/独立审计仍阻塞产品接线”，登记静态后代码修正未复核和离线整段墙钟偏差；本执行者不改正式 docu。无需用户逐项确认工程参数。当前无新增持久字段、公共接口或服务批准请求。

---

## 历史：083 初批结果（原文保留）

