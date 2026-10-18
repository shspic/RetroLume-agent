# TASK-083 / R-077 / STEP008 执行结果：review-02 后定向接续（当前有效）

**状态：部分完成，按本卡最终批次失败即停。Job/PG 运行门仍冻结，D1、D3 未闭合，05 旧失败未查明；不得接线或宣告 STEP008/M-1 完成。** 执行身份为原 083 实现窗口 GPT-6，本窗口自本卡起是实现者而非独立审计者。原 5 个 Job、旧 04 缺证与全部历史修正/失败不清零；本轮真实 Job/PG 启动数均为 0，005 未执行。

## 四项结论

| 项 | 本轮结果 | 定位及限制 |
| --- | --- | --- |
| 04 Start 事件 | **代码候选已修。** `CreateEventW` 返回已有对象（183）或失败即关闭本次句柄并拒绝；01—05 控制链 Start/Arm 共用检查，不触发外来事件。纯替身碰撞/失败/新建 2 项显示 ok。 | `backend/tests/fixtures/task083/job_control.py:21,56`；`unit-final-01.log`。无真实事件/Job 验证，旧 04 证据无法追补。改前真实 `fixture.py` 字节副本已保存在 `focused-repair-03/pre/`，本轮未改它。 |
| 05 计时 | **根因未证，未改 1≤C≤W。** 按预列 ID 仅诊断一次，退出 0；本次 `t0=1172500000000ns`、`t1=1172515000000ns`、`delta=15000000ns`、`C=1`、`W=6`，sleep 前后读数分别等于这两个时间，Job 替身事件为 `spawn_suspended,resume,query,close_job`，状态 settled。导入的 session/test 哈希随原始 JSON 记录。 | `05-diagnostic.log`、`05-diagnostic-meta.txt`；诊断时 session 哈希 9956e442…，最终版本另有 D1 输出字段。单次 PASS 未复现 review-02 的 `elapsed_violation_full_reservation`，不能解释旧失败，也不能据此关闭。05 不在最终批次重复。 |
| D1 父 launcher/SUP | **固定悬停控制候选已写，验证未通过。** `run_supervised_window` 仅接真实仓储、受限 `SessionConfig`、`WorkerCommand`；请求经限长 16 KiB 命名映射提交，父以显式 base Python 与固定 `app.worker.supervisor_main` 创建悬停进程，禁句柄继承，取得精确进程/主线程句柄与创建时间后才 Resume。子端固定入口验证请求，执行 `SingleWindowSupervisor.run_once`，结果只在确切 SUP 退出后读取并校验帧、身份和形状。启动、运行、终止等待共享绝对 `deadline` 与预留清理窗；无 SUP 结果时 S/R/待折叠均 None、`cleanup_incomplete=True`。 | `launcher.py:93,170,196,215`；`supervisor_ipc.py:41,50,88`；`supervisor_main.py:23,58`；`session.py:66`。最终批次 10 项中 9 ok、1 fail，整批退出 1；失败项的替身把第四次检查设为截止，此时实现已 Resume，故实际 `manager_timeout_unconfirmed`，期待的 Resume 前状态不成立。该分支无有效验证；旧第12项因停批 not_run。Win32 固定入口/venv 转发、父死亡悬停对象及真实超时/句柄收尾均 not_run。CreateProcessW 内核永久阻塞不在硬墙钟承诺内；同权限恶意旁路未证明排除。 |
| D3 旧 G 恢复 | **事实调查完成，提案待裁决。** 只讨论旧 W 全额折叠，不追溯部分退款，不改模型。Microsoft Learn 支持 Local 命名空间按登录会话分隔，`ProcessIdToSessionId` 只给 numeric ID，`GetTickCount64` 是 uptime 而非唯一启动 ID；快速启动属于 S4，不能以墙钟或数值相同证明命名空间化身。六页官方取证链接、适用范围和未证部分见 `official-facts.md`。 | 两列 `running_owner_boot_id/session_id` 只有在先获得可信且持久的启动/登录会话化身来源后才可能充分；本轮未获得该唯一决定性事实，不能提交具体迁移为安全方案。现行旧 Job Open 失败保持拒新工，不放行恢复。 |

## D1 控制时序与故障出口

父在创建 SUP 前写入受限映射请求及绝对截止；`CreateProcessW(CREATE_SUSPENDED)` 成功后先取 PID、创建时间和主线程句柄，再检查剩余运行窗，才 Resume。子仅读固定映射、按固定模块进入单窗监督；本地业务 Job 的 claim→Job→worker Resume→整树确认→关门/结算仍由未变 `session.py` 协议管理。父等确切 SUP 退出，再读一次完整结果帧；半帧/校验错、子失败、父取消、启动部分失败或总期限到期均走精确句柄有限终止/等待，未知时字段保持 None。父在 Resume 前死亡时，本代码没有后台线程或迟到回调去 Resume；该结论限受信本地进程模型，未把任意外部同权限操纵视为已排除。父取得的非继承句柄与映射关闭、实际 Windows 父死后悬停生命周期须由后续 Job 运行和独立审查核实。

D1 最终替身失败的具体调用次序是：检查 1 映射前、检查 2 写请求后、检查 3 取得精确身份后、检查 4 Resume 后进入 wait。夹具给前三次 5 秒、第四次 0 秒，因此失败反映夹具场景排程不符其断言，不说明 Resume 前截止被验证。按“失败即停”未修夹具、未复检；实现也未签通过。`unit-stop-analysis.md` 保留原始定位。

## D3 最窄批准边界

候选仅需旧 G 满租后按原 W 全额折叠：若将来有可信启动/登录会话化身标识，可由受信 SUP 在 claim 的活动锁事务随 G 原子写入并读回；claim 响应丢失不得造 Job。持同一活动互斥时，同化身同会话须对确切 Job 得到零进程，或得到明确 `ERROR_FILE_NOT_FOUND` 且能排除迟到创建/错误命名空间，才能全额折叠；不同可信启动化身还须证明旧受控进程全灭；不同会话、旧行无字段、标识异常、权限/其他 Open 错误、提交不明均失败关闭。旧 SUP 迟到提交仍由原 status/G/C/CAS 裁决。拟由 running 行增加 `running_owner_boot_id`、`running_owner_session_id` 两列并改 claim/恢复接口，超出已批准 005 单列及本卡权限；**当前这两列仍不充分**，因官方支持的唯一命名空间化身事实未取得，不能请求仅按列名实施。未运行系统身份探针，也未把 `GetTickCount64` 或 session ID 复用风险猜成已解决。

## 验证、差异与后续门

- 改前所有相关文件（含实际已有 fixture.py）的字节副本/哈希见 `focused-repair-03/pre/`、`pre-hashes.txt`。最终 7 文件 AST、仓储/005 冻结哈希、逐文件旧新 SHA256 见 `static-final.log`、`final-hashes.txt`，增量正文见 `incremental.diff`。最终静态命令 `backend/.venv/Scripts/python.exe -B Ndocu/evidence/task-083/focused-repair-03/static-final.py`，退出 0、0.1614772 秒；AST 不等于运行通过。仓储 `929320baf55d625e897324aa76ebe543bda86e73a4bf1c4766c7e552721c5b20` 与 005 `26b71a836355fa9620401f6bbb76e9a42668a1ce52077aa91ecb2f61ebeb50eb` 未漂移。
- 05 唯一诊断命令：`backend/.venv/Scripts/python.exe -B backend/tests/fixtures/task083/offline_unit.py OfflineRepairTests.test_05_early_success_uses_tree_zero_close_then_same_g_settle_retry`，退出 0、1.5256558 秒。最终批次精确 ID/源码 hash 见 `manifest-final.txt`、`manifest-source-hashes.txt`；首命令 10 例退出 1、0.6060814 秒，原日志 `unit-final-01.log`；第二命令 `FixedEntryTests.test_12_fixed_command_and_injected_gateway_pass_through_gate` **not_run**。无第二次修正或复检。两项实际测试时长未超各自 60 秒，批次总窗未超 180 秒。
- D2/D5/D6 复用前轮静态/离线证据，未重新验证；D7 PG 隔离准备和 D8 未知结果仍仅为原条件结论，D1 变化不使它们自动升级。未改 repository、001—005、HTTP/gateway/PDF/runtime/锁/配置；未联网业务、安装、模型、应用、Docker、PG、真实 Job/事件/子进程。官方页面只读不算本机动态验证。
- 后续先由原 084 独立窗口增量复核本轮源码、D1 失败与 D3 证据边界；不得以本实现者自评代替审计。经编排另定额度后，最小 Job 仍含 01 正常早停、02 挂死、03 主退后代存、04 最后句柄/碰撞、05 同名碰撞，并补固定 SUP 的创建/父死亡/IPC 异常/期限受影响事实；任一归属或清理未知即停。PG 仍仅 review-02 定向 005 两例与 close 四例，真实连接 not_run；若 D3 获得审批，另列迁移/claim/恢复实际事务验证，不复用原 PG 证据。

以下保留前轮结果原文字节，作为历史记录；以上当前状态优先。

---
