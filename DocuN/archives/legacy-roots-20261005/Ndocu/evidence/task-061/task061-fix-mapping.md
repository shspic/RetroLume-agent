# TASK-061 资源归属链修正：逐项差异、停止权限来源与静态分支证据

对象（行号=本卡交付版本实测）：
- `tests/task059_proc_tree.mjs`（身份/代次规则）
- `tests/task054_pdf_materials_integration.mjs`（夹具主脚本）
- `tests/task057_watchdog.mjs`（独立看门狗）
- `tests/task059_proc.ps1`（未修改：281aa07c…）

本卡只做修改差异与控制流核对 + 一次 node --check 批次；**下表全部是静态证据**，不代表真实运行通过。
未运行脚本主体、未执行 Docker、未启动应用/浏览器、未做真实进程查询或停止。

## 一、逐项差异与停止权限来源

| 约束 | 修改点（落点） | 停止权限来源 | 失败路径 |
| --- | --- | --- | --- |
| 1 端口观察不产生owned | 删除 `recordAppTree` 里的端口认领分支；新增 `observeAppPort()`（主脚本:456）只写 `app.port_observations` 诊断；`recordAppTree()`（:439）只登记"本次直接 spawn"与"自有启动器仍存活时的后代链" | 归属只有两条：本次 `spawn()`（主脚本:496）与自有父进程后代链（:444）。已登记后代在父退出后仍按 (PID,创建时间) 可核验 | 不能证明归属的监听者只旁观、不停止；`stopApp` 把它记入 `unresolved` 并置 `confirmed=false`（:600-605）→ `cleanup_incomplete` |
| 2 创建时间无容差 | `normalizeCreated()`（proc_tree:61）只做无损语法统一（空格→T、逗号→点、尾部z→Z、去空白，不删数字位）；`createdMatches()`（:72）改为精确相等，**删除 ±1000ms 容差**；`recordKey()`（:90）按 (PID, 规范化创建时间) 分代，`mergeRecords()`（:95）不再按PID合并、也**删除了"补齐创建时间"的补造逻辑** | `killVerified()`（proc_tree:129）停止前重新查询并精确比对创建时间，不符即"不视为本卡资源" | 时间不符 → 记为 `reused`：视为本卡进程已退出，不动该PID（主脚本:582、看门狗:120）；创建时间未知 → `unverified` → 不停止 + `unresolved` |
| 3 容器不跨运行复用 | `containerBase`（:54，仅保留/诊断）与 `containerName = base-runTag`（:90）；`ensureContainer()`（:711）删除复用/`docker start` 分支，同唯一名已存在即阻塞并写 `container.collision`；`docker run` 带 `--label retrolume-run=<runTag>`；创建后核对含标签（:741）；`stopContainerConfirmed()`（:761）停止前必须同时通过"本次运行标签+本次运行容器名+已核实ID"（:766-773） | 停止权限=本次运行自己创建并由状态登记的容器 | 名冲突→阻塞（不接管）；标签/ID核对不过→不停止；有已核实ID但核对不过→`unresolved`+未确认（主脚本:792 / 看门狗:188）；无ID且标签不符→`not_ours`（只旁观，不阻塞收尾，主脚本:789 / 看门狗:185） |
| 4 未知不得转成已确认 | 主脚本 `stopApp`：`unverified` → `unresolved` + `confirmed=false`（:584-587、:605）；看门狗 `stopRegisteredResources`：`unverified` 从 `leftAlone` 改到 **`unresolved`**（:115-117），端口未认领监听者同样进 `unresolved`（:128-136） | 只对"已认领且身份精确一致"的记录拥有停止权限 | 未确认 → `cleanup_incomplete:true, finished:false`，看门狗保留并在硬上限内重试；`fire()` 只在 `unresolved` 为空时正常收束（:212 起） |
| 5 上限不变 | `deadlineMs=600000`、`browserBudgetMs=120000`、`STEP_RESERVE_MS=30000`、`CLEANUP_TOTAL_CAP_MS=90000` 均未改动（:60-63）；应急路径仍单独记 `emergency-*`+`overtime`，不打印 PASS | — | 超限只记超时/应急 |

同时保留：六场景与 47 条断言逐条未变（含浏览器四场景块与 s4/s6 块逐字节一致）、迁移完整性核对（10表/关键列/主外键/唯一/检查约束/5索引 + 全缺才迁移）、证据目录每次唯一、期限与心跳监督、看门狗有界自保。

附加修正（同属"停止状态是否可确认"，非新增范围）：本次**从未启动**过应用且无任何自有记录时，`stopApp` 返回 `confirmed:true`（主脚本:563-564 注释与实现）。059 原实现此处返回 `confirmed:false`，会把"什么都没启动就失败"的收尾误标为清理未完成。

## 二、四个静态分支证据表（分支→代码路径→结论）

| 分支 | 对应代码路径 | 静态结论 |
| --- | --- | --- |
| **外来python占8000端口** | `observeAppPort()` 记录 `claimed_by_this_run`；`stopApp` 的未认领监听者 → `unresolved`(`unclaimed-listener-not-stopped`) 且 `confirmed=false`（:589-603）；看门狗同规则（:126-135）。全脚本对进程调用 `killVerified` 共四处：主脚本:578（应用）、主脚本:645（浏览器）、看门狗:112（应用）、看门狗:154（浏览器），入参都来自 `ownedRecords()`/`appRecords`/浏览器记录——只含已认领记录；端口观察从不写入 `tree` | 外来python**永远不会被停止**（端口巧合不触发停止）；但它会让本次收尾记"未确认"，不打印 PASS |
| **PID复用 / 创建时间近似（<1s）** | `createdMatches` 精确比对（proc_tree:72）；`classifyRecords` 的 `reused` 分支（proc_tree:112 起）；`recordKey` 分代（:90）；s6 重启时两代启动器同PID不同创建时间会各存一条 | 创建时间只要不精确相同就**不停止**；059 的 ±1s 容差逻辑已不存在（`createdMatches` 内无容差比较，全文残留的 `1_000` 只是 sleep 时长与 NanoCpus=1e9 检查） |
| **未知身份（无创建时间）** | `captureSpawnIdentity()` 3次×2条来源仍失败→`created:null`（主脚本:481-494）；`classifyRecords` 的 `unverified`；主脚本 `stopApp` :581-586、看门狗 :115-117。全脚本无任何"后来观察补齐创建时间"的代码（059 的补造分支已删） | 身份未知**不停止**，且必定进入 `unresolved`/`cleanup_incomplete`，不会被记成"已停止/收尾完成" |
| **旧看门狗遇新运行容器** | 新容器名 `retrolume-task-054-pg-<runTag>`（:90）+ 标签 `retrolume-run=<runTag>`；旧（059版）看门狗只用**它自己状态文件里的**ID或固定名 `retrolume-task-054-pg` 去 `docker inspect` | 旧看门狗按ID→新容器ID不同→`No such object`→不动；按固定名→新容器名带 runTag→同样不存在→不动。新运行也不接管旧容器，故**不存在**"旧看门狗停掉新运行容器"的路径 |

验证方式（静态）：读取上述落点源代码 + 差异核对 + 一次 `node --check` 批次（见 task061-node-check.log）。
以上不构成运行验证；运行行为留后续单次运行卡。
