# TASK-059 六项定向修正：代码落点 / 失败路径 / 所有权与停止证据设计

- 对象：`tests/task054_pdf_materials_integration.mjs`（行号指本卡提交版本）、`tests/task057_watchdog.mjs`、新增 `tests/task059_proc_tree.mjs` 与 `tests/task059_proc.ps1`。
- 本卡只做静态/控制流检查：未运行脚本主体、未执行 Docker、未启动应用或浏览器、未安装、未做模型请求。行号为交付版本实测。

## 1. 监督先行 + 异常窗口 + 半写JSON

| 落点 | 内容 |
| --- | --- |
| 主脚本:955 `await startSupervision();` | main() 的第一件事。Edge/venv 检查、docker 预检、容器、迁移、应用、浏览器全在其后。 |
| 主脚本:283 `startSupervision()` | spawn 看门狗后等就绪文件（PID 必须等于本进程子进程 PID、`helper_ok===true`）；看门狗提前退出或 30 秒未就绪即抛错——此时尚未创建任何资源。 |
| 看门狗:204 `main()` 前段 | 先自检 `tests/task059_proc.ps1`（缺失/自检失败→写 `helper_ok:false` 的 ready 文件并退出码 3），再采纳期限后写 ready 文件。 |
| 主脚本:128 `writeJsonAtomic` / 看门狗:48 | 全部状态/心跳/报告写入都是"临时文件+改名"。 |
| 看门狗:74 `readState()` | 文件缺失或半写 JSON 时返回 `lastValidState`，不丢最后有效的所有权与截止信息。 |
| 主脚本:152 `writeSupervision` | 合并式写入，且显式拒绝丢失 `started_at/deadline_at/budget_ms`。 |
| 异常窗口-容器 | `ensureContainer()` 入口先写 `container.expect=true`；`docker run` 带 `--label retrolume-run=<runTag>`；返回 ID 立即写状态。看门狗按"ID 优先，无 ID 时名称+运行标签匹配"判定归属。 |
| 异常窗口-应用 | `spawnApp()`：spawn 后同步写 pid，随即查询并写 (pid, 创建时间)；`recordAppTree()` 在就绪后补登后代与 8000 端口监听者。 |
| 异常窗口-浏览器 | `launchPersistentContext` 之前把本次唯一 `profile_dir` 写入状态。 |
| 监督失联不能继续跑 | 每个阶段/场景入口 `assertSupervisionAlive()`（主脚本:276）；同时 500ms 看门狗（主脚本:323）检测心跳停滞>10 秒即触发应急停止。 |

失败路径：看门狗未就绪→主脚本在 0 资源状态下失败退出；看门狗中途死亡→主进程 500ms 内检测并应急停止，退出码 2，不打印 PASS；状态半写→双方都退回最后有效状态继续判定。

## 2. 单调耗时 + 绝对截止；浏览器挂起实际停止；超限只记应急

| 落点 | 内容 |
| --- | --- |
| 主脚本:53-58 | `monoMs()`（`process.hrtime.bigint`）与 `deadlineAt`（挂钟绝对）共同限制：`remainingMs = min(budget-单调, deadline-挂钟)`，回拨不延长，向前跳只会更早停。 |
| 主脚本:162 `checkBudget` | 阶段/场景入口要求剩余 > 30 秒收尾余量（`STEP_RESERVE_MS`），正常收尾留在预算内。 |
| 主脚本:169 `runCmd` | 超时 `min(请求值, 剩余预算)`；预算不足直接拒绝执行；`budgetExempt` 只给收尾/应急步骤并单独限时。 |
| 主脚本:323-339 | 500ms 看门狗：浏览器阶段超 `cap_ms`、总期限到、监督失联 → `fireGuillotine()`，不再依赖阶段边界检查。 |
| 主脚本:1007 | 浏览器上限 `min(120秒, 剩余总预算-15秒)`，原卡 120 秒不抬高。 |
| 看门狗:85 `adoptDeadline` | 采纳 `min(挂钟剩余, 预算-已用挂钟)` 后转成本进程单调截止；回拨不延长。看门狗:44 无可用期限 30 秒即退出（原 45 分钟空等路径已删除）。 |
| 应急与正常分离 | `fireGuillotine` 写 `task057-guillotine-fired.json` 与 `outcome: emergency-stopped/emergency-cleanup-incomplete`、`overtime:true`；主流程正常结束也要求 `onTimeNow()` 才写 `outcome:"passed"`；看门狗触发过（`task057-watchdog-fired.json`）或应急已触发时一律不打印 PASS。 |

失败路径：浏览器挂起→超时看门狗实际触发收尾（关闭浏览器有界 15 秒，超时转由进程树收束）；应急清理允许超过总期限继续安全停止，但结果标记 overtime，绝不记准时通过。

## 3. 可靠收束自有进程树与测试浏览器

| 落点 | 内容 |
| --- | --- |
| 新增 `tests/task059_proc_tree.mjs` | 身份 = (PID, 创建时间)；`killVerified()` 停止前重新查询并比对创建时间，不符则"不视为本卡资源"、不停止；`classifyRecords()` 区分 alive/gone/reused（PID被复用视为已退出）/unverified（缺身份依据，不停止也不据此确认）。 |
| 新增 `tests/task059_proc.ps1` | 只读查询（query/descendants/find/portowner）。不杀进程、不写文件。 |
| 主脚本:418 `recordAppTree` | 自有应用记录来源：启动器 spawn 记录、启动器的当前后代、8000 端口监听者（名称必须为 python，且首见时仍在本次自有应用运行期内）。启动器退出后子进程被重挂仍可由端口监听者记录收束。 |
| 主脚本:511 `stopApp` | SIGTERM 自有启动器（8 秒有界）→ 对仍存活的自有记录逐个 `taskkill /T /F`（先核验身份）→ 复核全部记录消失；外来的 8000 监听者只报告不停止、也不据此判定未确认。 |
| 主脚本:561/579 `recordBrowserTree`/`killBrowserTree` | 测试浏览器按"命令行含本次唯一 `--user-data-dir` profile 目录" + 本进程后代定位；确认 stop 后 `task057-*.png` 截图仍在同一证据目录。 |
| 看门狗:97 `stopRegisteredResources` | 超期时同样按状态中已核验身份的记录停止应用/浏览器，容器按 ID（或名称+本次运行标签）停止并复核。 |

失败路径：PID 被复用→不动并记录 `skip-pid-reused`；缺创建时间→`left_alone` 记录且不计入"已停止"；端口有外来监听者→只报告。

## 4. 失败收尾不吞错、不误报成功、清理有界

| 落点 | 内容 |
| --- | --- |
| 主脚本:374 `runCleanup` | 单步：浏览器关闭 15 秒、浏览器树、应用、容器各有上限；总体上限 90 秒；每步结果（含失败/超时）都进 `steps`。 |
| 主脚本:400 | 任一必要步骤未确认→写 `cleanup_incomplete:true, finished:false`，看门狗保留值守。 |
| 主脚本:312 `releaseSupervision` | 只有全部自有资源确认停止才写 `finished:true` 并等看门狗自行退出（6 秒兜底）。 |
| 主脚本:1325-1330 finally | 未解除监督时**不** kill 看门狗；只记录"监督保留运行"。 |
| 主脚本:1303-1323 catch | 失败原因、每步停止结果、`outcome: failed/failed-cleanup-incomplete`、`overtime` 全部写进摘要；非零退出码。 |

失败路径：应用杀不掉→不写 finished、不解除监督、不打印 PASS，看门狗在期限/硬上限内继续重试；清理超 90 秒→按未确认处理。

## 5. 容器复用必须完整身份核对，Docker 错误不当"不存在"

| 落点 | 内容 |
| --- | --- |
| 主脚本:657 `ensureContainer` | 复用前逐项核对：名称、镜像 ID、`Config.Image` 引用（不一致时要求解析回同一镜像 ID）、`restart=no`、NanoCpus=1e9、Memory=512MiB、PidsLimit=128、无 Binds/Mounts、非 host 网络、`HostConfig.PortBindings["5432/tcp"]=127.0.0.1:55434`、State 非 running/paused/restarting。 |
| 主脚本:637 `dockerInspectClassified` | 仅 `No such object/container` 视为不存在；其余（连接/权限/守护进程错误）返回 error → 阻塞，不转入创建。 |
| 主脚本:629 `dockerPreflight` | 创建前先 `docker info`；失败即阻塞。 |
| 主脚本:697 | 启动后复核运行状态 + 完整配置 + 实际 `NetworkSettings.Ports` 绑定 + 宿主侧 TCP 可连，然后才 `pg_isready`。 |
| 主脚本:215 `psql` / 709 `stopContainerConfirmed` | 之后所有容器操作（exec/stop/inspect）都用已核实的容器 ID；停止后按 ID 复核 `State.Running=false`。 |

失败路径：同名容器任一属性不符→阻塞并列出全部问题；Docker 不可用→阻塞；运行中的同名容器→拒绝接管。

## 6. 迁移完整性核对与唯一证据目录

| 落点 | 内容 |
| --- | --- |
| 主脚本:744-761 | 期望清单：10 张表 + 各表关键列 + 5 个关键索引。 |
| 主脚本:763 `fetchSchemaInventory` | 一次 SQL 取回 tables/columns/constraints/indexes 原始清单并落盘（`task057-db-schema-inventory.json`）。 |
| 主脚本:779 `verifyMigrationStructure` | 核对：主键（全表）、外键（含 `material_current_version_source`、pdf/activity 各表）、唯一约束（`material_versions(source_id,id)`、`pdf_review_candidates(version_id)`、`(id,version_id)`）、检查约束（format 必须已含 `'pdf'` 且保留 `'txt'/'md'`，即 003 已应用；sha256/size/revision/status/预留额度/disposition/decided_at/warnings/identity/octet_length）、关键索引。 |
| 主脚本:827 `ensureMigrations` | 10 张表全缺→按序执行 001/002/003 各一次（`psql -f -`，事务在脚本内）→再次取清单并复核，不一致即阻塞；表缺失但非全缺→阻塞；全存在但结构核对不过→阻塞。不重迁移、不删库、不重建。 |
| 主脚本:63-68 | 证据目录每次唯一：默认 `Ndocu/evidence/task057-runs/<UTC时间>-<runTag>/`，可用 `RETROLUME_TASK_EVIDENCE` 指定（此时唯一性由调用方负责）。 |

失败路径：结构读取失败→阻塞并给出 psql 退出码与 stderr；混合/不完整→列出缺失项后阻塞；迁移后复核不过→阻塞。
