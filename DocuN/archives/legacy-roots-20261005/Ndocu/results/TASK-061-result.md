# TASK-061 结果：测试夹具资源归属修正（只改归属链，不运行）

- 任务：TASK-061 / R-055 / STEP-004-005 / 父 TASK-059（关联 057/054、FR-001、DR-003、NFR-002）；类型：开发（测试夹具资源归属修正）。
- 执行时间：2026-09-21 +08:00。
- 结论：**完成（候选交付，静态）**。059 的四个疑点逐项落地：端口观察不再产生归属、创建时间比对无容差并按代次保存、容器不再跨运行复用且所有停止路径核对本次标签与ID、已认领但身份/停止状态未知一律进入 `unresolved`/`cleanup_incomplete`。六业务场景与 **47 条断言逐条未变**（浏览器四场景块与 s4/s6 块逐字节一致）。唯一实际检查为一次 `node --check` 批次（3 个改动的 .mjs，均 exit 0）；`task059_proc.ps1` 未修改故按卡未做解析检查。**未运行脚本主体、未执行 Docker、未启动应用/浏览器、未做真实进程查询或停止**，因此这不是运行验证。

## 实际变更

| 文件 | 动作 | 修改前 SHA-256 | 修改后 SHA-256 |
| --- | --- | --- | --- |
| `tests/task054_pdf_materials_integration.mjs` | 定向修改（+188/-113 行） | `682e1804123913d9b37186817cadba1b4e25e5615d5939e9da75b723c626062c` | `12888be4d3faa2b8c583308301e0e2f370ee964c63a048314b4b58c9df5eb493` |
| `tests/task057_watchdog.mjs` | 定向修改（+50/-20 行） | `1f3dc9086e8b2d3e9e2813b60f13a33e62f5b38933a35886ca30cfffa866e52d` | `13512a7054a38769f178e6bd70267b35b8d65a7ced680cdfdfdbd0dff8efcfe9` |
| `tests/task059_proc_tree.mjs` | 定向修改（+37/-14 行） | `a1eb75b9488b429ac208395c432ae72cef21630361e848ff2b3a89bf719c4203` | `4523063ae0f72641dd5acb5db8a7a86b03808c7883671427d13d2ef9006e53b7` |
| `tests/task059_proc.ps1` | 未修改 | `281aa07cdc9ef9f722244a2482f64c18cd4065c2612684a996768085a0c711e3` | 同左（未改） |

证据（新增，不覆盖旧证据）：`Ndocu/evidence/task-061/` 下四个变更前字节级副本、`task061-pre-change-sha256.txt`、`task061-final-sha256.txt`、`task061-node-check.log`、`task061-fix-mapping.md`（逐项差异/停止权限来源/**四分支静态证据表**）。

未改业务源码、迁移、依赖/锁、正式 docu、旧结果/日志；无 Docker 命令、无应用/浏览器启动、无真实进程查询或停止、无安装/联网/模型/凭据、无 Git 操作。

## 逐项差异与停止权限来源（完整落点见 task061-fix-mapping.md）

1. **端口观察不产生 owned**：删除 `recordAppTree` 的端口认领分支，新增 `observeAppPort()`（主脚本:456）只写 `app.port_observations` 诊断。归属只来自两条：本次直接 `spawn()`（:496，含 `captureSpawnIdentity` 3次×2来源补身份）与自有启动器存活时的后代链（:444）；已登记后代在父退出后仍按 (PID,创建时间) 核验。不能证明归属者不停止，记 `unresolved`。
2. **创建时间无容差、按代次保存**：`createdMatches` 改为无损规范化后精确相等（proc_tree:72），删除 ±1000ms 容差；`recordKey`/`mergeRecords`（:90/:95）按 (PID, 规范化创建时间) 分代，不再按PID合并，并删除"后来补齐创建时间"的补造逻辑。
3. **容器不跨运行复用**：新容器名 `retrolume-task-054-pg-<runTag>`（:90）+ 标签 `retrolume-run=<runTag>`；`ensureContainer()`（:711）删除复用/`docker start` 分支，同名碰撞即阻塞并写 `container.collision`；创建后核对含本次标签（:741）；`stopContainerConfirmed()`（:761）停止前必须同时通过"本次运行标签+本次运行容器名+已核实ID"（:766-773）。历史容器仅保留、不停止、不删除。
4. **未知不得转成已确认**：主脚本 `stopApp` 把 `unverified` 记入 `unresolved` 并置 `confirmed=false`（:584-587、:605）；看门狗把 `unverified` 从 `leftAlone` 改为 **`unresolved`**（:115-117），端口未认领监听者同样进 `unresolved`（:128-136）。`runCleanup` 据此写 `cleanup_incomplete:true, finished:false` 并保留看门狗；`fire()` 只在 `unresolved` 为空时收束。
5. **上限不变**：`deadlineMs=600000`、`browserBudgetMs=120000`、`STEP_RESERVE_MS=30000`、`CLEANUP_TOTAL_CAP_MS=90000` 均未改；应急收尾仍单独记 `emergency-*`+`overtime`，不打印 PASS。

附加修正（同属"停止状态是否可确认"）：本次从未 spawn 过应用且无任何自有记录时，`stopApp` 现在返回 `confirmed:true`（:563-564）。059 此处返回 `confirmed:false`，会把"什么都没启动就失败"的收尾误标为清理未完成。

## 四分支静态证据表（分支→代码路径→结论；全部为静态证据）

| 分支 | 代码路径 | 静态结论 |
| --- | --- | --- |
| 外来 python 占 8000 端口 | `observeAppPort` 的 `claimed_by_this_run`；`stopApp` 未认领监听者 → `unresolved`+`confirmed=false`（:591-605）；看门狗同规则（:128-136）。全文 `killVerified` 仅四处（主脚本:578/:645、看门狗:112/:154），入参均来自已认领记录 | 端口巧合**不触发停止**；只会让收尾记"未确认"，不打印 PASS |
| PID 复用 / 创建时间近似（<1s） | `createdMatches` 精确比对（proc_tree:72）；`classifyRecords` 的 `reused` 归类；`recordKey` 分代 | 创建时间不精确相同即**不停止**；059 的 ±1s 容差路径已不存在（残留 `1_000` 只是 sleep 与 NanoCpus 检查） |
| 未知身份 | `captureSpawnIdentity` 失败→`created:null`（:481-494）→`unverified`；主脚本 :584-587、看门狗 :115-117；无任何"后来补齐身份"的代码 | 身份未知**不停止**，且必进 `unresolved`/`cleanup_incomplete`，不会被记成已停止 |
| 旧看门狗遇新运行容器 | 新容器名带 `<runTag>` + 标签；旧（059版）看门狗只按**它自己状态里的**ID或固定名 `retrolume-task-054-pg` 做 `docker inspect` | 按ID→新容器ID不同→`No such object`→不动；按固定名→新名带 runTag→不存在→不动。新运行也不接管旧容器 → 不存在"旧看门狗停掉新运行"的路径 |

## 唯一实际检查与退出码

```
node --check tests/task054_pdf_materials_integration.mjs  -> exit 0（无输出）
node --check tests/task057_watchdog.mjs                   -> exit 0（无输出）
node --check tests/task059_proc_tree.mjs                  -> exit 0（无输出）
批次 batch_exit_code: 0；node v24.15.0
tests/task059_proc.ps1 未修改（hash 与059一致）→ 按卡不做 Parser::ParseFile
控制流核对：断言 47→47（逐条比对无增删）；浏览器四场景块、s4/s6 块逐字节一致；7个 scenario 调用点齐全
```

日志：`Ndocu/evidence/task-061/task061-node-check.log`。

## 未运行与风险

- 六场景、Docker、应用、浏览器、迁移、真实进程查询/停止均未运行；本卡不做真实环境结论。
- 新容器每次运行都会**新增一个保留容器及其匿名数据卷**（占磁盘；本卡不创建、不测量、不清理）。历史 `retrolume-task-054-pg` 与既往运行容器一律保留，清理需另行授权。
- 端口规则比 059 更严：若我方应用停止后恰有外来进程占住 8000，本次收尾会记 `cleanup_incomplete`（不停止该进程、也不宣布收尾完成）。这是按卡"不能证明归属则不停止、记未确认"的有意取舍。
- 看门狗在 `unresolved` 非空时会在硬上限（期限+5分钟）内重试，属有界行为；重试不会去动未认领进程。
- `captureSpawnIdentity` 在查询失败时最多增加约 1 秒同步等待（3 次尝试）；仅异常路径触发，仍在总预算内。
- PowerShell 辅助脚本、`docker --name` 唯一名、标签语义等均只经静态核对，未在真实环境执行。

## 是否偏离边界

未偏离。只写了允许的 4 个脚本（其中 1 个未改动）+ `Ndocu/evidence/task-061/` + 本结果文件；未触碰业务源码/迁移/依赖/正式 docu/其他 TASK 文件（062 的 capabilities/gateway 无重叠）。按卡要求**放弃了跨运行容器复用**，因此容器名由固定名改为本次 runTag 唯一名——这是卡内明确要求的方案收缩，不是自行扩大范围。

## 文档建议与下一步

- 建议 Astra 登记 `CHG-XXXX`，并在执行状态中记录：061 采用"本次唯一容器、不跨运行复用"的口径，取代 054/057 卡中的固定容器名与复用规则；原 `retrolume-task-054-pg` 保留不接管。
- 可交运行卡的准备结论（**不是运行通过**）：三个改动脚本语法批次通过、归属链与停止权限路径有静态落点与失败路径；运行前需确认 Docker 可用、`127.0.0.1:55434` 与 `8000` 空闲、`powershell.exe` 可用、前端 dist 为当前构建；运行后需接受"新增保留容器占磁盘、清理另行授权"和"未确认停止时看门狗继续值守"两条行为。
- 运行行为留后续单次运行卡；本卡交付即停，不申请运行、不扩建模拟器。
