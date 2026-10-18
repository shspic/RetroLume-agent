# TASK-065 结果（R-059，父TASK-064，关联063/061/054、045/047/050/052/055、FR-001、DR-001/003、NFR-002）

- 执行者：Work Buddy / GLM（GLM-5.3-Flash），B档，新会话，与卡内路由一致。
- 日期：2026-09-21（本机 GMT+8）。
- 建议状态：**失败（夹具缺陷阻塞；5/7场景标识真实通过，s4未到达断言、s6未运行）**。整体无通过候选。

## 1. 唯一执行记录

- 冻结脚本 `node tests/task054_pdf_materials_integration.mjs` **实际执行一次**（runTag=rakv12g），exit=1，失败即停，未修码、未重试。
- 运行窗口：01:39:41.992Z → 01:40:33.608Z（51.6秒，远未触及600秒总窗口与120秒浏览器上限）；监督未触发（fired=false）、无超时。
- 启动器说明（不影响"主脚本最多一次"额度）：第一次启动尝试因 PowerShell 5.1 Start-Process 遇环境变量大小写重复键（HTTPS_PROXY/https_proxy）抛 ArgumentException，node 进程未创建、无任何脚本产物（证据 attempt1-launcher-failure/）；改用 Git Bash 字节级重定向后完成唯一一次执行。

## 2. 环境与快照

- Docker server 29.7.2；镜像 sha256:cf134a76…（当次 image inspect 核对）；运行前 55434/8000 空闲（当次 Get-NetTCPConnection 核对）；Node v24.15.0（系统）；backend/.venv 与 frontend/node_modules/playwright 存在。
- 冻结 hash 运行前核对 5/5 MATCH（precheck-frozen-hash.txt）：task054=1e2e86e6…、task064纯函数=2c050cbc…、task057_watchdog=13512a70…、task059_proc_tree=4523063a…、task059_proc.ps1=281aa07c…。
- 脚本内置 task057-source-hashes.txt 覆盖主脚本/看门狗/进程树/迁移/后端源码/前端dist 共23文件；**该内置清单不含 task064_candidate_constraints.mjs（脚本冻结不可改）**，新纯函数 hash 以运行前 precheck-frozen-hash.txt（2c050cbc…MATCH）纳入运行证据，满足卡内"纯函数也纳入hash"要求。
- 062/052 范围源码与 dist hash 与前证衔接（清单内一致），未重建。

## 3. 六类场景结果（脚本7个场景标识，逐项）

| 场景 | 状态 | 说明 |
|---|---|---|
| s1a TXT原换行摘录精确 | **passed**（1.5s） | 六类-1 前半 |
| s2 两页PDF实际绘制并截图 | **passed**（3.0s） | 六类-2：canvas-stats page1 nonWhite=1458/161色、page2 nonWhite=1790/179色；3张截图落证 |
| s3 缺页/重复/越界/陈旧拒绝及补充身份 | **passed**（0.4s） | 六类-3 |
| s1b 重复选择与受控晚到不污染 | **passed**（5.4s） | 六类-1 后半 |
| s5 混合坏文件隔离 | **passed**（2.3s） | 六类-5（截图 task057-mixed-batch.png） |
| s4 替换/跳过/失败保留旧版与并发CAS | **failed** | 错误：`pdfBuffer is not defined`——冻结夹具自身作用域引用错误，s4 第一行即抛出，**该场景全部断言未执行**（非被测应用失败、非产品缺陷证据） |
| s6 真实重启持久状态 | **not_run** | 因 s4 FATAL 未到达 |

- 六类映射：类1=s1a+s1b 通过；类2=s2 通过；类3=s3 通过；类5=s5 通过；**类4=s4 失败（夹具错误）**；**类6=s6 not_run**。

## 4. 收尾与残留（全部确认）

- 监督最终记录 task057-supervision-state.json：finished=true、cleanup_incomplete=false、release_reason=fatal-complete、supervision_released_at=01:40:33.653Z；看门狗按 finished=true 自行退出 exit=0（heartbeat seq=25）。
- 容器 retrolume-task-054-pg-rakv12g（完整ID 2340202877caabce67cd390090be72f13b6abfa908fae3503e4463432d0940a2，标签 retrolume-run=rakv12g）：docker stop --time 5 exit 0 → stopped-confirmed；运行后独立复核 Exited(0)（post-run-container-status.txt）。**按卡保留不删**（含匿名卷，占磁盘）。
- 应用（launcher pid 31944 + uvicorn pid 28792，spawn-direct-query 归属）：sigterm-confirmed，port_clean；运行后独立复核 55434/8000 监听者=0（post-run-port-status.txt）。
- 浏览器（系统Edge独立profile，7个msedge进程+3个取证powershell）：树确认后无存活（killed=0/still_alive=0，进程已自然退出），stop_confirmed=true。
- 外来进程：无未确认项（unresolved=[]、unverified=[]、pid_reused_left_alone=[]、unclaimed_port_listeners=[]）。

## 5. 失败/未验证/风险

- **s4 夹具缺陷**：`pdfBuffer is not defined` 为测试脚本变量作用域错误（07脚本经057/059/061/064多轮修改后引入），属 fixture ReferenceError，非应用/迁移/数据库失败；s4 的替换保留旧版、失败/跳过保留、真实PG CAS 冲突等断言**未获得任何证据**，不得推断通过或失败。
- **s6 未运行**：重启持久性无证据。
- 064 修正谓词在真实组合中得到第一次运行验证：本次全新库 001/002/003 各应用一次后迁移结构核对**通过**（063 的误报未再出现）。
- stdout-raw.log 0字节（脚本FATAL路径无stdout输出，stderr 仅1行 FAIL 摘要）；权威记录为 summary/run-notes/supervision JSON，已全部落证，未为转码重跑。
- 风险：s4/s6 阻塞 STEP-004/005 完整验收；不阻塞其他无关任务卡。

## 6. 命令与退出码汇总

```
预检：Get-FileHash×5（5/5 MATCH）；docker version → server=29.7.2 exit 0；docker image inspect → exit 0；Get-NetTCPConnection 55434/8000 → free
启动尝试1（PowerShell Start-Process）：ArgumentException，未创建进程（attempt1-launcher-failure/）
唯一执行（Git Bash，cwd=项目根）：
  RETROLUME_TASK_EVIDENCE="Ndocu/evidence/task-065/task065-run1-20260921T0136Z" node tests/task054_pdf_materials_integration.mjs
  → BASH_EXIT=1；脚本内部 exit=1（FATAL: pdfBuffer is not defined）
后核：docker ps -a（rakv12g Exited(0)）；Get-NetTCPConnection → listening_count=0
```

## 7. 文档建议 / 必须人工操作 / 下一步

- 建议 Astra 登记 TASK-065"已返回/失败（夹具s4缺陷）"；另出夹具修正卡（定位 s4 块 `pdfBuffer` 未定义引用，参照064模式：修改前存副本+hash核对、只改该作用域、离线静态核对+node --check，禁止改六场景断言语义），修后由 Astra 另派新运行卡（063/065 各一次运行均已用尽）。
- 必须人工操作：无（容器/卷保留占磁盘，如需释放请人工决定删除 rakv12g 容器及其匿名卷）。
- 不宣告 STEP-004/005 或 08 完成；不填 Astra 验收结论。
