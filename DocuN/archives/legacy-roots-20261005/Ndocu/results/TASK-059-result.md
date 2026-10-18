# TASK-059 结果：修正057剩余监督与资源接管缺口（定向修复，不运行）

- 任务：TASK-059 / R-053 / STEP-004-005 / 父TASK-057（关联054、FR-001、DR-003、NFR-002）；类型：定向修复（只读产品 + 改两个测试脚本 + 新增必要辅助脚本）。
- 执行时间：2026-09-20 +08:00。
- 结论：**完成（候选交付，静态）**。六项已核对缺口逐项落地并有明确失败路径；六场景与成功标准未删减（断言对比：旧45条全部保留，新增2条只加强 s6 的"真正停止"）。唯一实际检查为一次 `node --check` 批次（3个.mjs，均 exit 0）与一次 PowerShell 纯解析（未执行脚本内容，exit 0）。**未运行脚本主体、未执行 Docker、未启动应用/浏览器，因此六场景仍一律按未验证对待；静态正确不等于真实通过。**

## 实际变更

| 文件 | 动作 | 修改前 SHA-256 | 修改后 SHA-256 |
| --- | --- | --- | --- |
| `tests/task054_pdf_materials_integration.mjs` | 定向修改（+802/-149 行） | `4898f2321e7d7211da8549b4d030625ecdbe2b64207798b8d7f2a2df3a4a2e62` | `682e1804123913d9b37186817cadba1b4e25e5615d5939e9da75b723c626062c` |
| `tests/task057_watchdog.mjs` | 重写（+254/-34 行） | `f792372570a958e35cee610df65328d3f984682e093073269220b9d7a31aaa2f` | `1f3dc9086e8b2d3e9e2813b60f13a33e62f5b38933a35886ca30cfffa866e52d` |
| `tests/task059_proc_tree.mjs` | 新增（122行） | — | `a1eb75b9488b429ac208395c432ae72cef21630361e848ff2b3a89bf719c4203` |
| `tests/task059_proc.ps1` | 新增（91行，只读进程查询） | — | `281aa07cdc9ef9f722244a2482f64c18cd4065c2612684a996768085a0c711e3` |

本卡证据（新增，不覆盖旧日志）：`Ndocu/evidence/task-059/` 下 `task054-pre-059-script-copy.mjs`、`task057-pre-059-watchdog-copy.mjs`（修改前字节级副本）、`task059-pre-change-sha256.txt`、`task059-fix-mapping.md`（六项逐项落点/失败路径/证据设计）、`task059-node-check.log`、`task059-powershell-parse.log`、`task059-final-sha256.txt`。

未改业务源码、迁移、依赖/锁、正式 docu、旧结果、旧日志；无 Docker 命令、无应用/浏览器启动、无安装下载、无模型请求、无删除、无 Git 操作。项目无 Git 基线，未声称干净工作树。

## 六项修正逐项证据（完整落点见 `task059-fix-mapping.md`）

1. **监督先行与异常窗口**：`main()` 第一件事就是 `startSupervision()`（主脚本:955/283）——等看门狗 ready 文件（PID 必须等于本进程子进程、工具自检 `helper_ok:true`），未就绪或提前退出即抛错，此时尚未创建任何资源；容器创建前先登记预期名称+本次运行标签 `retrolume-run=<runTag>`，ID 一取得即登记；应用 spawn 后同步登记 pid 并立即补写 (pid,创建时间)；浏览器在 launch 前先登记本次唯一 profile 目录。监督失联（进程退出或心跳停滞>10秒）由 500ms 看门狗实际触发应急停止，不继续跑。状态与心跳一律"临时文件+改名"原子写，看门狗读失败时沿用最后有效状态（不丢所有权与截止）。
2. **期限**：`remainingMs = min(预算−单调耗时, 绝对截止−挂钟)`（主脚本:53-58；系统回拨不延长，向前跳只会更早停）；`runCmd` 超时受剩余预算约束（:169）；浏览器阶段不再只做阶段检查——500ms 看门狗在浏览器超限/总期限到/监督失联时**实际触发停止**（:323、:341）；看门狗采纳期限也用"挂钟与预算取小"并转单调截止（看门狗:85），拿不到可用期限 30 秒即退出，原"状态坏了可等 45 分钟"的路径已删除（看门狗:44）。总 10 分钟与浏览器 120 秒常量未动，浏览器上限只可能因总预算不足而下调（min(120s, 剩余−15s)）：正常收尾留 30 秒余量（`STEP_RESERVE_MS`）。超限应急清理仍可继续安全停止，但结果记为 `emergency-stopped/emergency-cleanup-incomplete` + `overtime:true`，且应急/看门狗触发过时一律不打印 PASS。
3. **进程与浏览器收束**：新增 `task059_proc_tree.mjs` 统一身份规则——(PID,创建时间) 一致才算本卡资源；PID 被复用→不动，缺创建时间→只登记不停且不计入"已停止"。应用记录来源=自有启动器 + 其当前后代 + 8000 端口监听者（名称必须 python，且只在本次自有应用运行期内首见）；`stopApp`（:511）SIGTERM 有界 8 秒→对仍存活的自有记录逐个核验后 `taskkill /T /F`→复核全部消失；测试浏览器按本次唯一 `--user-data-dir` 标记 + 本进程后代定位并确认停止（:561/:579）。不按端口杀未知进程、不按裸 PID 杀、不按名称杀。
4. **失败收尾**：`runCleanup`（:374）单步（浏览器关闭15秒/浏览器树/应用/容器）与总体（90秒）都有上限，每步结果都进摘要；任一必要步骤未确认→写 `cleanup_incomplete:true, finished:false`，`finally` 保留看门狗继续值守（:1325-1330，不再 kill）；只有全部自有资源确认停止才写 `finished:true` 并正常退出看门狗（:312）。catch 不吞错：失败原因 + 每步停止结果 + 非零退出码（:1303-1323）。只处理本卡资源。
5. **容器复用**：除镜像 ID 外逐项核对名称、`Config.Image`（不一致时要求解析回同一镜像 ID）、`restart=no`、CPU1/512MiB/PID128、无宿主挂载、非 host 网络、`127.0.0.1:55434` 绑定、State 非 running/paused/restarting（:606/:657）；仅 `No such object/container` 视为不存在，Docker 连接/权限错误一律阻塞不转为创建（:637），创建前另做 `docker info` 预检（:648）；启动后复核运行状态+实际端口绑定+宿主侧可连（:697）；此后所有 exec/stop/inspect 均用已核实容器 ID（:215/:709）。
6. **迁移与证据目录**：期望清单=10张表+各表关键列+5个关键索引（:744-761）；一次 SQL 取回 tables/columns/constraints/indexes 原始清单落盘（:763），核对主键、外键（含 `material_current_version_source`）、唯一约束、检查约束（format 必须已含 `'pdf'` 即 003 已应用，同时保留 `'txt'/'md'`）、5个索引（:779）；10张表全缺才按序执行 001/002/003 一次并**再次取清单复核**；表缺失但非全缺、或结构核对不过→阻塞，不重迁移、不删库、不重建（:827）。证据目录每次唯一：默认 `Ndocu/evidence/task057-runs/<UTC时间>-<runTag>/`（:63-68），不覆盖 057 的旧摘要/日志。

## 唯一实际检查与退出码

```
node --check tests/task054_pdf_materials_integration.mjs  -> exit 0（无输出）
node --check tests/task057_watchdog.mjs                   -> exit 0（无输出）
node --check tests/task059_proc_tree.mjs                  -> exit 0（无输出）
批次 batch_exit_code: 0；node v24.15.0
powershell Parser::ParseFile tests/task059_proc.ps1（纯解析，未执行）-> exit 0，输出 parse-ok
断言对照检查：旧脚本45条 assert 全部保留，新脚本47条（新增2条，只加强 s6 停止确认）
```

日志：`Ndocu/evidence/task-059/task059-node-check.log`、`task059-powershell-parse.log`。

## 未运行与风险

- 六场景、Docker、应用、浏览器、迁移均未运行；本卡不做任何真实环境验证判定。
- `tests/task059_proc.ps1` 只经语法解析，未在真实环境执行过；主脚本启动时若工具不可用会**阻塞**（不静默降级），看门狗自检失败同样阻塞。
- 迁移文件改用 `docker exec -i ... psql -f -`（原057为把整个迁移文件塞进 `-c` 参数）；两种方式都未被真实执行过，本卡选了不依赖 argv 长度的写法，并在迁移后复核结构以在失败时暴露。
- 新增运行期依赖：系统需在 PATH 中提供 `powershell.exe`（Windows 自带）——运行卡需要写进环境前提；这属于新增环境要求，不是依赖安装。
- 遗留风险（低）：若一次运行以"停止未确认"结束，看门狗会在期限+5分钟硬上限内继续重试；若期间有人启动新一轮并复用同一个（已停止的）容器，旧看门狗可能把它停掉。缓解：本轮正常收尾确认后会写 `finished:true` 让看门狗立即退出；未确认停止时下一轮会因容器运行中而按卡阻塞。
- 浏览器阶段若总预算已接近耗尽，其实际上限会低于120秒（只下调不上调）；本卡未抬高任何原卡上限。

## 需求或架构偏差

无需求/架构/业务改动。实现层面的三点显式偏差（建议运行卡与后续审计知悉）：

1. 创建容器时新增两个身份标签 `retrolume-task=054`、`retrolume-run=<runTag>`（名称/端口/CPU/内存/PID/restart/镜像/挂载均未变），用于关闭"已创建但ID未登记"的异常窗口；复用历史容器（无标签）时不依赖标签，改用已核实 ID。
2. s6 新增两条断言（`stopHow.confirmed`、`finalStop.confirmed`）——只加强"真正停止"的成功标准，未删除或放宽任何原断言。
3. 默认证据目录由 `Ndocu/evidence/task-057` 改为每次唯一的 `Ndocu/evidence/task057-runs/<时间>-<runTag>`（满足第6点防覆盖）；`RETROLUME_TASK_EVIDENCE` 仍可覆盖（此时唯一性由调用方负责）。

## 文档建议与下一入口

- 建议 Astra 登记 `CHG-XXXX`（本卡按分工不改 `docu/CHANGE.MD`），并确认 057 结果中"证据目录默认 `Ndocu/evidence/task-057`"的口径已被本卡第6点取代。
- 下一入口为**运行卡**（真实启动），本卡不自行开启。运行卡需在此基础上补充：①Docker 可用、55434/8000 空闲、`powershell.exe` 可用；②前端 dist 为当前构建（hash 清单已含新增的两个测试辅助脚本）；③命令 `node tests/task054_pdf_materials_integration.mjs`；④总期限10分钟、浏览器120秒不抬高，正常收尾留至少30秒；⑤证据落本次唯一目录（默认即可）；⑥首次失败即停该流程并保留证据，六场景结果以实际证据为准。
- 与 TASK-060 无写入冲突：本卡只改上述测试脚本与辅助脚本，未触碰账本与正式 docu。
