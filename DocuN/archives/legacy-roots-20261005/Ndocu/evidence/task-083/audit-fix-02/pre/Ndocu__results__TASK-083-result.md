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

# TASK-083 / R-077 / STEP008 执行结果

**状态：部分完成，停止本卡运行并交回编排。** 本窗口实际模型标签为 GPT-6；沿 TASK-082 独立诊断窗口转为本卡实现者，082 历史诊断独立性不变，本窗口不担任 083 后续独立安全审计。未宣告 M-1、STEP008 或项目完成。根目录 `D:\shspic\project_NO3_RetroLume-agent`。基线 `45951501d2741630a229762d6b2d3f4b34d7f702`；既有正式文档和其他未提交差异原样保护。

## 输入与边界

按本卡读取根 `AGENTS.md`、公共 `docu/AGENTS.MD`（本窗口已读未变，复用）、`TASK-083.md`、`TASK-082-work-decision.md` 全部批准条款、`TASK-082-result.md`、需求 NFR002/003、SEC002、第13节、架构 FLOW005/DATA007，必要的 activities/repository、001—004、gateway/transport、PDF Windows Job 与直接相关测试。没有加载全部历史执行聊天或重做 077—079 PG。082 的官方依据仅用于本卡既定设计；本卡未新增联网取证。

用户 2026-09-24 批准的是内部单窗监督切片与合成验证。005 **未执行**；未运行 PG、Docker、模型、应用服务或真实外发。未改 gateway/transport 主体、PDF 监督器、HTTP/runtime/前端、001—004、锁文件、正式 docu/公共库或旧证据；未 Git 提交/推送/reset/clean。

## 已写入的增量与职责

| 路径 | 增量与职责 | 状态 |
| --- | --- | --- |
| `backend/migrations/005_activities_dispatch_closed.sql` | 事务内 ACCESS EXCLUSIVE 锁 activities，非空抛错回滚，仅增加 `dispatch_closed BOOLEAN NOT NULL DEFAULT FALSE`。 | 静态核对，not_run |
| `backend/app/activities/repository.py`、`__init__.py` | claim 同事务只给新代次开门；折叠耗尽/cancel/settle 关门；`begin_window_close` 同来源→活动锁序、当前 G/执行者匹配、仅 false→true 幂等；admit/mark 检查门；record 仍允许关门后合法收敛；settle 首次需已关门，最近 G/C 幂等先行；`inspect_window` 供恢复只读核对。 | 离线替身局部通过，PG not_run |
| `backend/app/worker/gate.py`、`worker_main.py` | 不可重开的本地共享调用令牌，覆盖包装器 `gateway.call` 的全程；关闭先设 closed 再等活跃调用退出。只向注入工作函数提供包装器。 | 离线 2 项通过；未接真实 gateway |
| `backend/app/worker/windows_job.py` | 活动命名互斥、UUID+G 精确命名 Job，默认当前用户 DACL、非继承句柄、无 breakaway，4 进程/256 MiB 限额、KILL_ON_JOB_CLOSE；悬停创建→Assign→Resume；查询 BasicAccounting.ActiveProcesses，有限终止等待。 | 合成初批部分通过；归属测试未闭合 |
| `backend/app/worker/session.py`、`__init__.py` | 活动互斥覆盖恢复核对、claim、Job 创建及交接；t0 在 claim 前，响应丢失不 spawn；partial W 拒绝启动；整树 0 且主进程成功才取 t1/关 DB 门/按真实 C 结算；失败保留全额预扣并失败关闭。 | 内部骨架，尚不能签完整监督协议 |
| `backend/tests/test_activity_time_budget.py` | 原 PG 合成 helper 在当前合法代次 settle 前调用 close；保留旧业务断言；未运行 PG。 | not_run |
| `backend/tests/test_activity_dispatch_close.py`、`test_worker_session.py`、`fixtures/task083/fixture.py` | 限定离线替身与 Windows 合成场景；初批发现夹具缺陷后作唯一一次精确修正，未再次运行 Job。 | 7 离线通过、Job 3/5 初批通过 |

原件 hash 及副本：`Ndocu/evidence/task-083/pre/`。冻结 repository `045A3CF8B1C81D7A1336C3BD2E90E891E4E53934027C9FEA9727FAFDE7202534`、004 `8F04F57C743C260F5081E0C6F232860301B30C7B03FEF69498D7C0704C0A97CC` 均与预期相同。最终 repository `929320BAF55D625E897324AA76EBE543BDA86E73A4BF1C4766C7E552721C5B20`，activities `__init__` `0C5EA723C270EFAE0BAC9F5AA9517628D1EBC88844A3C4E41829188B52F2BE78`，time-budget test `CB5A51960B830825350F5E30F9430DE6B04C939489D8FE8CAC0C76172C2E1245`，005 `26B71A836355FA9620401F6BBB76E9A42668A1CE52077AA91ECB2F61EBEB50EB`。全部新 Python 文件最终 hash 见 `Ndocu/evidence/task-083/static-final.log`；前副本 hash 在同文件。已跟踪源码增量 `+92/-1` 行；新增文件不在 Git numstat 中，审计须直接查看。

## 合同与当前实现限制

默认工程参数 W=90s、启动上限 s=5s、请求超时=10s、停止预留 g=5s、Job 查询步长 q≤0.05s；要求 `W > s + request_timeout + g`，实际 `W_eff` 不满足也拒绝开工，截止固定为 t0+W_eff，终止开始不晚于 t0+W_eff-g。SUP 的 claim、旧树核对、DB 及清理均有有限代码等待；不声称 Windows 硬实时。C0 只保留仓储原合同，真实 SUP 仅在 `1≤ceil(t1-t0)≤W_eff` 路径请求退款；越界/失败不伪造 C0 或钳制 C，残留由原过期认领规则保守折叠，不擅自取消活动。提交响应丢失只用同 G/W/C 有限重试；整机重启不比较旧 t0，旧 Job 打不开或身份未知就拒绝新 claim。

**仍有实现级缺口**：`command_for_lease` 是同步注入回调，代码没有对其执行时长的独立强制上限；当前 SUP 用阻塞 Win32 轮询，必须专用线程/进程运行，但外部启动器的有限管理生命周期未形成可验证产品接口。内部 worker 门仅由注入回调路径使用，尚未与真实供应商 gateway 连接，不能证明未来业务代码不会持原始 gateway 绕开门。真实 Job 身份/恢复与 SUP 死亡场景未通过本批验证。因此这不是可供产品接线的完整已验收监督协议。

## 有限验证与真实预算账

首次运行前清单：`Ndocu/evidence/task-083/manifest.md`。静态命令（项目根）`backend\.venv\Scripts\python.exe -B Ndocu\evidence\task-083\static_check.py`：初次及修正后各 exit 0；最终原始输出 `static-final.log`。本卡限定 `git diff --check -- backend/app/activities/repository.py backend/app/activities/__init__.py backend/tests/test_activity_time_budget.py` exit 0。全仓 `git diff --check` exit 1，只报本卡开始前已存在的正式 docu 尾随空白，不触碰这些文件。静态检查是 AST、hash 与明显真实外发标记检查，不是动态无外发证明。

| 批次 | 真实命令（工作目录 backend） | exit | 原始事实 |
| --- | --- | ---: | --- |
| 离线仓储替身 | `.venv\Scripts\python.exe -B tests\test_activity_dispatch_close.py CloseGateRepositoryTests` | 0 | 3/3 通过，`unit-close.log`；仅调用序/内存替身，不证明 PG 锁或约束。 |
| 离线 worker | `.venv\Scripts\python.exe -B tests\test_worker_session.py GateTests ProtocolUnitTests` | 0 | 4/4 通过，`unit-worker.log`；claim 响应丢失、partial W、旧 Job 未知均不 spawn。 |
| 初始 Job 批次 | `.venv\Scripts\python.exe -B tests\test_worker_session.py WindowsJobTests` | 1 | 5 个场景，3 通过、2 失败，`job-initial.log`。日志 10:32:19—10:34:40，本批总墙钟约141.3秒；第4场景和整条命令突破单场景30秒/命令60秒上限。没有第二 Job 批次，修正后 Job 结果 **not_run**。 |

Job 初批逐项：01 正常早停在 Job 查询 0 后未结算，合成 FakeLedger 错把真实 0.313 秒当作必须≥1，SUP 返回 `failed_closed`；日志保留活动 `d0876c04-4b37-4247-bbd4-60c5d181acdd`、G1、精确 Job 名、PID 35116、`ActiveProcesses=0`。02 挂死路径在约5秒停止并观测 0，全窗收费，未调用 settle。03 主进程先退时 ActiveProcesses 仍>0，随后查询为 0。04 SUP 死亡路径未取得稳定 worker 句柄：虚拟环境解释器为转发器，读取到的 PID 随转发退出，`OpenProcess` 返回空；测试控制器/管道等待突破期限，不能主张“最后句柄关闭后整树退出”已验证。05 同名 Job 创建拒绝，原 Job 查询 0。第02/03/05 的精确 UUID/PID 未写入原始日志，因此只作为局部行为证据，不作完整归属审计证据。

初批曾以精确命令行与父链定位测试进程 13512/32900、夹具控制者 7300/35500，活动 UUID `11dd3767-7f74-41eb-baa4-aba83a852dfc`；对仍存活且归属已核对的 PID 35500 作有限应急停止，随后批次进程收束。`cleanup-process-check.txt` 的只读筛选为本卡 Python 夹具/测试控制者 count=0；这**不是**该 Job 的 ActiveProcesses=0 正证据，04 仍按归属/整树证据不足记录。未按进程名/端口批量杀进程，没有继续启动 Job。启动 Job 场景数为 5，少于8；初批总窗少于10分钟，但场景/命令子上限违反，作为执行偏差保留。

一次范围内修正由 `edit_after_initial.py` 精确修改 FakeLedger 的 `ceil(C)` 断言，并使合成场景使用 `sys._base_executable` 绕开已确认的虚拟环境转发器，未扩大进程数。修正后仅 AST/hash 通过；因 04 的归属正证据和时间边界失守，按本卡停止规则**未启动复检**，不可称修复已通过。无第二次修正或第二 Job 批次。测试输出中的 unittest `FAIL` 原样保留，不以文字 PASS 代替。

## 后续矩阵与交接

| 层级 | 下一步具体范围 | 当前证据 |
| --- | --- | --- |
| 实现补足 | 为生成 worker 命令及 SUP/启动器建立有限上限；让测试控制者在 Resume 前取得稳定精确进程/Job 身份和截止，并为每场景记录 runTag、UUID/G/Job/PID/查询结果；修正 04 的管道等待期限；只在获新卡预算后重测失败/受影响场景。 | 缺口未闭合；本卡不再运行。 |
| 独立增强审计（新窗口） | 审查关闭门与 admit/mark/send/退款交错、DB 锁序与旧 G/C 幂等、Job 归属/跨进程重启/未知退出、t0/W/失败预算不重置；审计最终源码与本卡原始失败日志。 | 本实现者不签安全通过。 |
| 专用真实 PG 与组合验证（另卡） | `Ndocu/evidence/task-083/pg-plan.md` 的 PG-01—06，专用 DSN 缺失 skip；仅选择真正受影响的既有 ledger/recovery/time-budget 用例。 | **not_run**；079 旧证据不覆盖 005/新门。 |
| 产品外接 | 在审计与专用 PG 后明确 gateway 注入和 worker 生命周期；若需改 gateway 主体或持久字段，先提交具体差异再审批。 | 本卡未接线。 |

原始导航：`Ndocu/evidence/task-083/manifest.md`、`static-final.log`、`unit-close.log`、`unit-worker.log`、`job-initial.log`、`cleanup-process-check.txt`、`pg-plan.md`、`pre/`。源码/测试原件均在上述允许路径；旧文档差异保持。建议编排将 083 标记“部分/停止”，围绕确定缺口派下一张有限修正与验证卡，再交独立增强审计；不要把本结果登记为最终验收。
补充实现风险：`run_once` 多个提前返回在 `finally` 清理前构造 `SessionOutcome`，若清理随后失败，返回值的 `cleanup_incomplete` 可能失真；下一卡须先修正并以故障注入验证，不能依赖该字段判定安全收尾。
