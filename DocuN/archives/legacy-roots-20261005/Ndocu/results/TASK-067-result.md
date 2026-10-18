# TASK-067 结果（R-061，父TASK-066，关联065/064/061、FR-001、DR-001/003、NFR-002）

- 执行者：Work Buddy / GLM（GLM-5.3-Flash），B档，新会话，与卡内路由一致。
- 日期：2026-09-21（本机 GMT+8）。
- 建议状态：**完成——剩余场景通过候选（s4/s6 实际 passed 且收尾全部确认）**。整体判定由 Astra 合并 065 历史证据（s1a/s2/s3/s1b/s5 passed）后作出；本轮其余五个标识保持 not_run/not_selected，未伪写 passed。

## 1. 唯一执行记录

- 冻结脚本 `node tests/task054_pdf_materials_integration.mjs --remaining-s4-s6` **实际执行一次**（runTag=ram8p8h），**BASH_EXIT=0 / 脚本 exit 0**，失败即停规则未触发，未重试、未转全套模式。
- 时间：started_at=2026-09-21T02:18:19.457Z，finished_at=02:19:28.180Z；单调耗时 68721ms、墙钟 68723ms（两者一致）；总窗口 600000ms 仅用约 11.5%，无超时（on_time=true，overtime=false，watchdog fired=false）。
- 启动方式复用 065 已验证的 Git Bash 字节级重定向（PowerShell Start-Process 的大小写重复环境键问题未再触碰，未删改任何系统环境变量/代理）。

## 2. 环境 / 冻结 hash

- 只读预检（当次核对，precheck-env.txt）：Docker server 29.7.2 exit 0；镜像 sha256:cf134a76… 在机 exit 0；55434/8000 运行前空闲；Node v24.15.0；backend/.venv 与 powershell.exe 存在。
- 冻结 hash 一次性核对 5/5 MATCH（precheck-frozen-hash.txt）：task054=130a5bc9…、task064纯函数=2c050cbc…（新增纯函数 hash 已一并保存）、task057_watchdog=13512a70…、task059_proc_tree=4523063a…、task059_proc.ps1=281aa07c…。
- 复用 065 已有环境/源码/构建证据，未变部分未重跑；前端未重建（剩余模式不依赖浏览器）。

## 3. 准备与 s4/s6 实际结果

- **准备（真实API，失败关闭）**：上传同一合成两页PDF → 逐页确认（第2页 supplement"第二页用户补充"）→ 核对响应（资料列表、query_ready、pages=2、supplements 恰1条 identity=user_supplement/physical_page=2）后进入 s4/s6。pdfRow=8f0c6017-d08e-4fba-bd18-de4935eaa804，candidate=aae8963e-6f8b-4069-b0a1-b8912740d79e。未直写数据库、未用旧库预置；准备不计作重验 s2/s3。
- **s4 PASSED**（4869ms）：待核对替换期间旧版可读；陈旧候选确认 CAS 409 拒绝；跳过路径、坏PDF失败路径均保留更新后的 TXT；断言未降低。
- **s6 PASSED**（22400ms）：真实停止本次自有应用（sigterm-confirmed、port_clean）→ 重启（app ready）→ 核对数据库计数一致、确认PDF版本/两页文字/第2页用户补充身份、更新TXT正文、pending 候选保留 → 最终应用停止确认（sigterm-confirmed）。
- **未选场景**：s1a/s2/s3/s1b/s5 = not_run（not_selected，未选择）；浏览器 started=false（summary browser.note："剩余模式未启动浏览器（准确记录，非异常/遗留）"），无截图、未触碰个人浏览器。

## 4. 命令 / 退出码 / 证据

```
预检：Get-FileHash×5 = 5/5 MATCH；docker version exit 0；docker image inspect exit 0；Get-NetTCPConnection 55434/8000 = free
唯一执行（Git Bash，cwd=项目根）：
  RETROLUME_TASK_EVIDENCE="Ndocu/evidence/task-067/task067-run1-20260921T0218Z" node tests/task054_pdf_materials_integration.mjs --remaining-s4-s6
  → BASH_EXIT=0（脚本 exit 0；console: TASK-054/057 REMAINING PASS (s4/s6 only; overall verdict by Astra)）
后核（独立复核）：docker ps -a → ram8p8h Exited(0)（post-run-container-status.txt）；55434/8000 监听者=0（post-run-port-status.txt）
```

- 摘要 task057-summary.json：outcome=passed-remaining-s4-s6；mode=remaining-s4-s6；selected=[s4,s6]；not_selected=[s1a,s2,s3,s1b,s5]；scenario_failures=[]；migration_mode=applied-fresh-verified；cleanup.incomplete=false、timed_out=false。
- 监督最终记录 task057-supervision-state.json 与 summary 一致：supervision released=true、release_reason=normal-complete；看门狗按 finished=true 自行退出 exit=0（heartbeat seq=33）。
- 原始输出：stdout-raw.log / stderr-raw.log 字节级保留（065 同款 shim dirname 警告为启动器外壳输出，与被测脚本无关）。

## 5. 自有残留及收尾

- 容器 retrolume-task-054-pg-ram8p8h（完整ID a9913fcfe8300f3e58d39a92afb07affb01bf647d1a805cab279503e45964366，标签 retrolume-run=ram8p8h）：docker stop --time 5 exit 0 → stopped-confirmed；运行后独立复核 Exited(0)。**按卡保留不删**（含匿名卷，占磁盘）。
- 应用两次运行实例（首启 launcher 37332/uvicorn 38464；重启后 launcher 8880/uvicorn 25264，均为 spawn-direct-query 归属）：s6 前停止 sigterm-confirmed；s6 内最终停止 sigterm-confirmed；收尾 normal 停止记录 sigterm-timeout 但 confirmed=true、still_alive=0、unverified=0、unresolved=0、port_clean=true（如实记录，未影响确认结论）；双端口独立复核 0 监听。
- 浏览器：未启动（records=[]，note 如实）；无外来进程（unresolved/unverified/unclaimed 均空）。
- 旧容器：065 容器 2340202877ca…（rakv12g）及历史保留容器均未接管、未启动、未删除。

## 6. 未验证 / 风险

- 本轮不覆盖 s1a/s2/s3/s1b/s5（not_run/not_selected）；其结论依赖 065 证据（当时通过），本轮未重测。
- 收尾 normal stop 的 sigterm-timeout（launcher pid 8880 SIGTERM 后未在单步窗口内退出确认，随后 still_alive=0、port_clean 确认）如实记录；如 Astra 认为需关注应用优雅退出时长，可另立观察项，不阻塞本卡结论。
- 整体六类通过与否须由 Astra 合并 065 与本轮证据判定；本轮仅报剩余场景通过候选。

## 7. 文档建议 / 必须人工操作 / 下一步

- 建议 Astra 在 PROJECT_EXECUTE_STATE 登记 TASK-067"已返回/通过候选（s4/s6）"，合并 065+067 证据判定 STEP-004/005 六类场景整体状态，并视结果解除夹具阻塞线。
- 必须人工操作：无（如需释放磁盘可人工删除 ram8p8h / rakv12g 容器及其匿名卷）。
- 下一步：由 Astra 决定是否进入后续验收/整体验证流程；本卡不宣告 STEP/项目/08 完成。
