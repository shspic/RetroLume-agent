# review-08 原始证据核对后完整裁定（读三批离线原始 meta/stdout/stderr、三检查入口、walkthrough、083 结果置顶11后）

本页不覆盖 code-prelog-assessment.md 的代码层初判；以下为证据覆盖定分、逐项关闭结论与运行准备裁定。

## 一、离线证据覆盖定分（任务卡审查点6）

三批 16/5/2 项、exit0、2.7286574+0.7178588+0.9456941=4.3922103 秒，与卡面及 083 置顶表格一致；三批 meta/stdout/stderr 独立保存，无覆盖；unittest Ran/OK 摘要在 stderr，stdout 另有 OFFLINE_RESULT 行，二者互证。

修正时点链（由三批 compile hash 定分）：
- 批01 运行于中间版：fixture=959e17b1、test_d3_runner_control=409eae4d、runner=425a54f2；repository/session/test_d3_recovery/controlled_child/contracts 已是最终版。
- 批02 运行于中间版：fixture=8ed90093、runner=a2c7c787；test_d3_runner_control=fc157323（最终）、controlled_child/contracts 最终。
- 批03 运行于全部最终版（八文件 compile hash 与 final-hashes 逐字节一致），批03 后无再修正；final-hashes.txt、incremental.diff、runner-old-to-new.diff 由批03 脚本生成并当场核 UNCHANGED 五项。

最终 hash 对应的已执行方法（分明清单）：
1. 对八文件最终版实际运行：仅批03 两项——test_runner_import_does_not_touch_resources、test_optimization_guard；另有 F1 second/upper 调用形态、F2 errors.CheckViolation、lock-barrier 两次 observe_source_lock_wait 的 AST 结构核对（脚本明示 preparation only; no PG transaction proof）。
2. 依赖面全为最终/未变文件、结论直接有效的 14 项：批01 的 D3RecoveryGuards 8 项+D3ClockOrder 2 项+ProtocolUnitTests 2 项（依赖 repository/session/windows_job/test_d3_recovery/test_worker_session，批01 时全部最终或 UNCHANGED）；批02 的 test_close_failure_marks_cleanup_unknown、test_exact_results_and_deadlines（依赖 controller/controlled_child/contracts 均最终，不触 runner/fixture 运行时）。
3. 仅对中间版运行、最终版未重跑的 3 项：test_pre_resume_failures、test_deadline_and_query_unknown（controller 409eae4d 中间版；受测主体 ControlledChild 批01 已最终版字节）、test_unknown_cleanup_and_windows_start_block_retry（runner a2c7c787 中间版；retry_allowed 纯函数逻辑已按最终版 26ECB423 静态审读）。批间 diff 未保存，无法字节证明这三项的测试断言在中间版与最终版间未变——如实按"行为证据绑定中间版、最终版仅静态"分级，不冒充最终 hash 行为证据。
4. 独立测试方法共 19 个（8+2+2+7）；16+5+2=23 为运行次数和，含 exact_results×2、optimization_guard×3、import×2 的重复计数。083 置顶按批如实报告 16/5/2，未把求和冒充 23 个独立用例——该声明核对属实。
5. fixture 场景运行时行为（migration/ledger/windows 九场景）从未运行，本轮也只 compile+AST——与冻结边界一致，无虚报。

## 二、逐项结论（关闭/仍阻断/证据不足）

**P1 关闭（代码层）**。claim（repository.py:366-433）与 inspect（:441-461）均为"来源锁→活动行 FOR UPDATE→fetchone→datetime.now(timezone.utc)"采样；事务起点口径已删。002 迁移 deadline_at TIMESTAMPTZ NOT NULL 排除 NULL 比较异常；lease_expires_at 两侧显式处理。新增/既有 FOR UPDATE 不改变来源→活动锁序，异常经事务回滚释放；产品调用方持活动互斥，inspect 短事务无死锁面。D3ClockOrder 两项替身测试证采样顺序（依赖文件批01 已最终版）。ledger_lock_barrier 夹具具有真实辨别力：claim 的 DB 事务在锁等待前建立，若实现仍用事务起点时间，越界后 claim 会"成功"并触发 `claim crossed deadline` 断言失败；锁后采样则正确拒绝——该屏障能区分新旧实现。观察不到 pg_stat_activity 锁等待即 AssertionError，失败方向安全。真实 PG 事务证据仍待实跑（见第四节）。

**P2 关闭（代码层）**。run_once（session.py:130-358）逐路径核对：五类拒接与 Open 5/87/未知 → failed_closed+cleanup_incomplete=True+账目三值 None（:179 初始 0 不再冒充旧账）；仅 ERROR_FILE_NOT_FOUND 进对象不存在分支并记 old_tree_confirmed=True；旧树 terminate/wait false/query/close 失败四路均不 claim 不 spawn 不退款、树/句柄未知如实（:194-212）；claim 回执丢失 → budget_exhausted+账目 None（折叠已提交但金额未读，:225-229）；新窗成功后 settled=0/reserved=pending_fold=window 语义与 Result 注释一致；结算失败重试一次、settlement_unconfirmed/结算已发异常账目置 None；已结算遇清理异常 → settled_cleanup_error；active_processes_at_end 仅实测树零报 0（:348）。launcher.py:310-317 异常路径自构造 None+cleanup_incomplete=True，supervisor_main.py:68-73 asdict JSON 透传，均无算术使用——"无需消费者改动"直接核对成立。

**F1/F2/F3 关闭（静态闭合）**。同 SID0 接续：first claim owner=0（fixture:155）→ second SID=0+expected_previous_generation=first.G（:175）与 repository:374-379 检查闭合，(R,S,owner)=(6,6,0)+dispatch_closed=False 断言成立；DWORD 上界在独立 pending 活动初领 4294967295 并查持久值（:191-196），跨 SID 拒绝不再误写成合法成功。旧 G/C 三拒绝+状态不变；exhausted 折叠断言 ("pending",0,6,None,True) 与仓储折叠耗尽分支一致。F2 errors.CheckViolation（:113）、F3 全 parts 白名单+重复选择拒绝+complete.parts 固定顺序保留，未为迁就失败削弱断言。批03 AST 对最终版核了 second/upper 调用形态、F2 类名、屏障观察点两处。场景本体从未运行（真实 PG 冻结），本轮唯一可得证据即静态闭合。

**R1 关闭（代码层，含一项定性）**。悬停 CreateProcess→GetProcessTimes 身份→Assign→active()==1→Resume 顺序成立；create/identity/assign 失败以精确句柄收尾（未 assigned 用 TerminateProcess+Wait 确认，assigned 用 TerminateJobObject+ActiveProcesses==0 轮询）；query 失败/超时 → OwnershipUnknown 且 cleanup_confirmed 保持 False；close 三句柄任一失败 → cleanup_confirmed=False；不持业务 Job 句柄，无观察者效应；runner 轮询退出条件=子进程退出+外层树零双正证。猝死窗口定性（卡面指定须区分两种保证）：Assign 前毫秒窗口内 runner 猝死 → 残留挂起孤儿，"不会执行 SUP"成立（挂起态无人 Resume 不运行）、"清理完整"不成立；Assign 成功起 runner 死亡由 KILL_ON_JOB_CLOSE 内核收尾。定性为可管理的已知停止边界（最窄处置=按记录 PID 手动 TerminateProcess），非阻断，不要求再造无限看门层，也不得把潜在孤儿算已清理——walkthrough 已按此口径如实声明 unknown。嵌套 Job 关系 09 场景已实测可行；本轮验证位置=windows_recovery 实跑时 fixture 在外层 Job 内创建业务 Job 树。

**R2/R3 关闭（代码层）**。validate_records：scenario_start/结果严格配对、starts/completed 恰等于期望序、complete 恰一次+all_pass is True+parts 精确匹配、exit0、timed_out/cleanup 未确认拒绝——缺项/重复/未知/部分 complete 均 FAIL，4 类坏样本+exit1+cleanup False+timeout 测试覆盖。error/cleanup_error 分栏、attempt 独立目录+as-run 字节/hash、runner 自身+controller+contracts 进 run_dir 快照、verdict NOT_RUN/BLOCKED/FAILED_*/PASS 区分未运行与失败、顶层吞 BaseException 后 `0 if PASS and stopped and not cleanup_incomplete else 1` 不假 exit0。stderr 不作唯一依据、原文保留+leaked 扫描 redact。R3：remaining/deadline_left ≤0 即抛、无 max(1,…) 复活；batch=min(total,started+600)、command=min(batch-60,started+60)、启动前 reserve=5、场景 30s 主动截止、reader join/go 等待共享额度并 reserve；PYTHONOPTIMIZE=0+-B+require_assertions 双保险，runner 关键判断为显式 if/raise 不受优化影响。口令路径：token_hex 内存生成→docker stdin（不入 argv）→子进程 env/内存→输出落盘前 replace+leaked 检查（出现即 FAIL）→meta/state 不含口令。retry 允许规则（retry_allowed）行为测试绑定中间版 runner（见第一节.3），最终版静态审读为保守停批 4 条件，失败方向安全。

## 三、资源复用路径与启用入口（审查点7）

静态核通过：inspect 以 14 字段 --format 投影明确排除 Config.Env（旧口令不入 CLI 输出）；valid_identity 全量校验 CID/NAME/IMAGE/标签(run=20260925-195448,phase=d3-10,retrolume-task=083)/唯一匿名卷/127.0.0.1:55439/1CPU/512MiB/pids128/restart=no/bridge/无 binds；启动前 docker ps --filter label=retrolume-task=083 须空+loopback 端口 bind 预检；容器内 local 认证是官方镜像既有事实，runner 仅尝试测试角色 task083_d3 本地认证（current_user/current_database 双核验）→stdin ALTER ROLE 自改密→loopback 新凭据三重身份核验（inet_server_port 返回容器内 5432，与 09 经验一致）；任一步失败 → RuntimeError → finally stop_exact_container 同 CID 收尾（stop 前后双 inspect+valid_identity，stop 失败升级 kill，running=false 必须）。不读旧 secret、不关认证、不换账号、不创建容器、不动首容器 1086a37d。本地认证/改密权限可用性未证，只能未来一次有界试验——runner 首步 identity 探测即该试验，失败即收尾，不构成复用路径本身的不安全。

给编排的启用入口与停止规则：
- 命令：`backend/.venv/Scripts/python.exe -B Ndocu/evidence/task-083/d3-repair-11/runner.py --authorized-reuse --total-seconds <120..1200>`（旗标记录授权决定，不代替人的授权）。
- 前置：编排明确资源授权；CID 85242648b70dc11839a93de29a51bc7e492390d8ad479036c141f37b26f4f6a7 停止且身份/配置/卷/端口/限制匹配；无其他 task=083 活动容器；55439 空闲。
- 场景与结果 ID：attempt-1 固定全量 migration,ledger,windows = migration_empty/old/rollback、ledger_active_lease_rejected/new_g/exhausted/lock_barrier、windows_recovery（contracts.SCENARIOS）；attempt-2 仅在同 runner 存活期间放置 attempt-02.go（parts 文本）触发。
- 停止规则：失败且 windows_started 或 cleanup 不明或树未零 → FAILED_STOP；PG-only 且树零且清理确认 → FAILED_WAITING_CORRECTION 等 go 文件；总 deadline 耗尽 → 收尾落盘；verdict/state.json 在 run_dir。
- 预算：剩余 2 批/2 PG/12 Windows 账面；30 分钟总账不重置（含 7.859s+首次收尾未知+81.765s），由编排设保守 --total-seconds。

## 四、静态运行门裁定与剩余待真实证据

**静态门满足：可在编排授权的精确资源和预算内进入受控真实验证。** 修复11 的 P1/P2/F1/F2/F3/R1/R2/R3 八项在代码与控制层全部关闭，无确定阻断，无需新修正轮。PG/Windows 实际通过仍待真实证据，不能以其未跑否决准备成果。

只能由受控真实验证取得的事实（本审计不预签）：
- PG：006 完整迁移/旧行/回滚、claim 折叠/耗尽/上界持久值、ledger_lock_barrier 真实来源锁等待与锁后判定、旧 G/C 不污染新窗。
- Windows：windows_recovery 旧 Job 精确销毁/Open2/固定 SUP 生产路径/新 G 真实账本结算、外层树收尾正证。
- ControlledChild 新控制路径的真实进程行为（身份/归属/树零）与嵌套 Job 实跑。
- 本地认证与改密权限可用性。

## 五、非阻断观察（不升级为门槛）

1. lock_barrier 的 0.9s 固定观察窗在慢环境可能超时失败——失败方向安全（不假 PASS）；若实跑因观察窗超时失败，attempt-02.go 是现成处置通道（有依据修正），无需预先改代码。
2. pre_resume_failures、deadline_and_query_unknown、unknown_cleanup 三项行为测试绑定中间版（受测主体 ControlledChild 为最终版字节、retry_allowed 最终版已静态审读）；真实运行时这些路径由真实控制门再证。
3. stop_exact_container 的 60s 收尾窗独立于 total_deadline 计算，预算极端紧张时以 cleanup_incomplete=True 安全失败收场；编排设 --total-seconds 时留出该余量即可。

## 六、边界重申

本轮只读：动态额度 0，未运行 compile/测试/旧检查，未启动/查询任何容器/PG/Job/进程，未读容器 Env/完整 DSN/口令/实现聊天；写入仅本目录与结果文件置顶段。不签 D3 动态验收、M-1/STEP008、产品 one_call 或安全最终通过；执行者身份 GLM-5.3-Flash（新隔离 Session，未参与 083 实现，review-07 同窗结论按未变方法/依赖复用）。
