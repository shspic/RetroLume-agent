# review-08 代码/控制初判（读原始三批日志与自评前）

只读初判；读取范围=任务卡冻结八项+UNCHANGED五项 hash 核对、incremental.diff、runner-old-to-new.diff、repository.py(340-500)、session.py(130-358)、d3_pg_windows.py(95-275) 最终版、test_d3_recovery.py/test_d3_runner_control.py/contracts.py/controlled_child.py/runner.py diff 全文（新文件）。未读实现聊天、未读三批原始 meta/stdout/stderr、未读 runner-walkthrough.md 与 083 结果置顶（待核声明按卡顺序后置）。

## 一、冻结与基线核对（现场计算 SHA256）

- 卡面八项全部 MATCH（repository BCA82833…/session EB514B5F…/test_d3_recovery D5A5389D…/d3_pg_windows A1E419F3…/test_d3_runner_control FC157323…/controlled_child 14E20FCB…/contracts A344AC5F…/runner 26ECB423…）。
- final-hashes UNCHANGED_REVIEW07 五项全部 MATCH（006 迁移/windows_job/test_worker_session/offline_unit/runner_replacement），review-07 基线适用性成立。
- TASK-083-result.md=DB656509…、runner-walkthrough.md=FF43AAFD…、incremental.diff=2FF42BCF…、runner-old-to-new.diff=892FC12C… 与 final-hashes 一致。
- 结论：无未知漂移，review-07 对未变文件的结论可按原方法复用。

## 二、P1（repository.py claim/inspect）

1. claim（:366-433）：来源锁 `_lock_sources` → 活动 `SELECT * … FOR UPDATE` → fetchone → `now=datetime.now(timezone.utc)`（:371）。已删除事务起点 `CURRENT_TIMESTAMP AS database_now` 口径。锁序与 begin_window_close/close 路径一致（来源→活动），新增或既有 FOR UPDATE 均不引入反向锁序。
2. inspect（:441-461）：SELECT 列投影改为原始列并加 `FOR UPDATE`，`lease_recoverable` 从 SQL 表达式改为锁后 Python 比较 `(lease_expires_at is None or <= now) and deadline_at > now`，与 claim 同口径。新增 FOR UPDATE 的直接影响：与并发 claim 的行锁竞争被序列化；产品调用方持活动互斥（run_once :172），inspect/claim 不会同进程并发；跨进程由命名互斥先行序列化；异常（ActivityLedgerConflict）→ 事务回滚释放行锁，无异常路径遗漏。inspect 持锁窗口为短事务，manager deadline 有包装。
3. NULL 风险：002 迁移 `deadline_at TIMESTAMPTZ NOT NULL`，`row["deadline_at"] > now` 不会遇 None；`lease_expires_at` 可空且两侧均显式处理。语义与原 SQL 等价（NULL→False）。
4. D3ClockOrder（test_d3_recovery.py 新增）：以 `patch("app.activities.repository.datetime", Clock)` 断言采样点事件序 `source_lock → activity_select → activity_fetch → clock`，claim 与 inspect 双路径覆盖。Clock 断言用 events[:3] 前缀比较，单次采样场景成立。这是纯替身顺序证据，仅证明采样顺序，不证明真实 PG 锁等待——与合同"P1 用定向逻辑/采样顺序检查，核心跨锁证据仅准备真实PG用例"一致。

## 三、ledger_lock_barrier 夹具（真实 PG 屏障，本卡只审准备质量）

1. 结构：holder 连接（默认事务化）持 material_sources 行锁 → 线程池内 claim/inspect → observe_source_lock_wait 以 0.9s 窗轮询 pg_stat_activity（application_name 精确匹配 + wait_event_type='Lock' + query LIKE '%material_sources%'）→ 观察时刻必须早于边界（claim_wait_at<deadline / inspect_wait_at<expiry）→ future 未完成证明阻塞 → 持锁越过边界 0.2s → commit 释放。
2. 辨别力（关键）：claim 的 DB 事务与连接在锁等待前已建立；若实现仍采事务起点时间（CURRENT_TIMESTAMP），其值早于 deadline，资格判断会通过 → future 返回 lease → `else raise AssertionError("claim crossed deadline…")` 触发失败；修复后锁后采样 now>deadline_at → ActivityLedgerConflict。inspect 侧对称（旧口径 → lease_recoverable=False → 断言失败）。即该屏障能区分"事务起点"与"锁后采样"两种实现，具有真实辨别力，不是采样顺序自证。
3. 释放后断言：claim 抛 Conflict 且 after==before（行无变化）；inspect 返回 recoverable=True。两侧均有正反断言。
4. 运行性风险（非阻断）：0.9s 固定观察窗需覆盖线程启动+loopback 连接建立；环境抖动时 observe 超时 → AssertionError → 场景失败。失败方向安全（不会假 PASS），但真实运行存在 FLAKY 失败可能；不要求本审计运行验证，计入"未来受控运行可能需一次重试"的有限风险，不构成准备不足。

## 四、P2（session.py run_once）

逐路径核对（对照合同与 review-07 缺陷清单）：
1. 初始账目 (0,0,0) 仅适用于 pending 新窗；旧 running 即置 None（:179）——初始 0 不再冒充旧账事实。
2. 五类拒接（未配置前提/SID None/异号/来源或租约不可恢复，test 覆盖 5 变体）→ failed_closed + cleanup_incomplete=True + 账目 None。有效租约有意拒接同样保守上报"本次未清理"，外层不会误认全活动干净（review-07 要求的最小语义，方向保守正确）。
3. Open 错误：仅 ERROR_FILE_NOT_FOUND 置 old_tree_confirmed=True（对象不存在分支，符合 D3 决策"明确不存在才可进入"）；ACCESS_DENIED(5)/87/JobUnknown → 直接 raise，old_tree_confirmed=False → cleanup_incomplete=True。
4. 旧树核查（:194-212）：terminate/wait_empty_until(False→JobUnknown)/close 任一失败 → old_failure raise → old_tree_confirmed=False；close 失败在 terminate/wait 已失败时并入 cleanup_errors。四类失败（terminate_error/wait_error/wait_result=False/close_error）测试断言 cleanup_incomplete=True+账目 None+无 claim/create+mutex_release 收尾。
5. claim 响应丢失（lease None）→ budget_exhausted + 账目 None（:225-229 注释明确"折叠已提交但未读取提交后S/R"）；old_tree_confirmed 已 True 时 incomplete=False，state 如实保留。
6. 新窗成功后 settled_seconds=0 语义=“本次新窗已确认结算（S 从 0 起算）”，与 Result 注释一致；旧 G 折叠不入此字段。
7. 结算失败重试一次（:289-294）；settlement_unconfirmed/结算已发异常时账目置 None（:310-313）；已结算遇清理异常 → settled_cleanup_error（不伪装未结算）。
8. 树零正证：active_processes_at_end 仅在 created_job and tree_empty 时报 0，否则 None（:348）——未证树零不冒充已清理。
9. finally 清理：terminate/query/close/owner_close/local_owner_release 分项入 cleanup_errors；incomplete 三因子合成（old_running 未确认 ∨ created_job 未树零 ∨ cleanup_errors）。
10. launcher/supervisor 消费者：SessionOutcome 字段未改名未增删（settled/reserved/pending 语义注释收窄），run_supervised_window 透传结构不变，无需适配（与合同"只有必要直接适配才改"一致）。

## 五、F1/F2/F3（d3_pg_windows.py）

1. F1 同 SID0 接续：ledger_active_lease_rejected 段 first claim owner=0（:155），ledger_new_g second claim SID=0+expected_previous_generation=first.G（:175）→ repository :374-379 要求 row.owner==0==参数，静态闭合；(R,S,owner)=(6,6,0) 且 dispatch_closed=False 断言成立（旧 6 折叠入 S、新预留 6）。
2. DWORD 上界分离：另一 pending 活动 initial claim SID=4294967295，持久值断言（:191-196）——跨 SID 拒绝不再被误写成合法成功（review-07 确定缺陷已按最小修复闭合）。
3. 旧 G 三拒绝（late claim/begin_window_close/settle 旧 G）+ 状态不变断言（:189-190）。
4. exhausted：owner=7 接续折叠 → ("pending",0,6,None,True) 断言与 repository 折叠耗尽分支（:397-410）一致。
5. F2 errors.CheckViolation（:113）保留；F3 全 parts 白名单+新增重复选择拒绝+complete.parts 固定顺序，未为迁就失败削弱断言。
6. 场景配对事件：全部 9 场景前置 scenario_start，为 contracts.validate_records 提供逐场景闭合。

## 六、R1（controlled_child.py）

1. 顺序：CreateJobObjectW（未命名、非继承、KILL_ON_JOB_CLOSE）→ SetInformationJobObject → CreateProcessW(CREATE_SUSPENDED) → GetProcessTimes 身份（pid+created_100ns）→ AssignProcessToJobObject → active()==1 核验 → ResumeThread。身份/归属建成先于 Resume，符合合同。
2. 出口：create/identity/assign 失败 → OwnershipUnknown；异常统一 stop(deadline)+close() 后 raise。stop 对未 assigned 悬停进程 TerminateProcess+Wait 确认退出；对 assigned 树 TerminateJobObject+active()==0 轮询；query 失败/超时 → OwnershipUnknown，cleanup_confirmed 保持 False（测试覆盖 query_fail 与 deadline 两路）。
3. close() 三句柄逐一关闭，任一失败 → cleanup_confirmed=False + OwnershipUnknown（测试覆盖）。
4. 观察者效应：ControlledChild 不持有业务 Job 句柄；外层 Job 独立对象，KILL_ON_JOB_CLOSE 作用于外层树（fixture 及其创建的 launcher/SUP/worker 全树），不保活业务 Job。
5. 猝死窗口（任务卡指定须明确区分两种保证的声明）：CreateProcessW 成功至 AssignProcessToJobObject 成功之间的毫秒级窗口内 runner 猝死 → 悬停进程游离于外层 Job 之外，KILL_ON_JOB_CLOSE 不覆盖。此窗口内："不会执行 SUP"成立（进程挂起态，无人 Resume 不运行）；"清理完整"不成立（残留一个挂起孤儿，占 PID/少量内存）。窗口之后（Assign 成功起）runner 死亡 → 控制者进程句柄由内核关闭 → 外层 Job 无引用 → 整树终止，清理保证成立。最窄处置：按记录 PID 手动 TerminateProcess（挂起进程可杀），无需再造无限看门层。定性：可管理的已知停止边界，非阻断；真实受控运行中该窗口仅存在于 fixture 进程启动瞬间，与本次待验证的 D3 语义无交集。
6. 嵌套 Job：外层 Job 含业务 Job 的嵌套关系在 09 场景 A/B/C 已实测可行；本次新路径为 CREATE_SUSPENDED+assign+resume，嵌套本身非新语义。受控运行中的验证位置=windows_recovery 场景（fixture 进程在外层 Job 内创建业务 Job 树）。

## 七、R2/R3（contracts.py+runner.py）

1. validate_records：scenario_start/结果严格配对（未知/重复/交叠拒绝）、starts/completed 恰等于期望序列、complete 恰一次且 all_pass is True 且 parts 匹配、exit==0、timed_out 拒绝、cleanup_confirmed 必须 True。缺项/重复/未知/部分 complete 均 FAIL；测试覆盖 4 类坏样本+exit1+cleanup False+timeout。
2. 顶层吞 BaseException 后 verdict/exit 分离：main 返回 `0 if PASS and container_stopped and not cleanup_incomplete else 1`——控制失败不会 exit0 假通过；verdict NOT_RUN/BLOCKED/FAILED_*/PASS 与 attempts 空判别区分"未运行"与"失败"。
3. stderr 不作唯一依据（validate 只看 stdout 事件合同；stderr 原文保留）。
4. deadline 体系：remaining/deadline_left 均 ≤0 抛 TimeoutError，无 max(1,…) 复活；run_batch batch_deadline=min(total,started+600)、command_deadline=min(batch-60,started+60)、启动前 deadline_left(reserve=5)；场景 30s 由 runner 主动截止（scene_deadline，超时 stop 树）；reader join 有 deadline；attempt-02 go 等待 deadline_left(reserve=120)。全部等待共享剩余额度。
5. PYTHONOPTIMIZE：run_batch env 显式 "0"+PYTHONDONTWRITEBYTECODE=1；fixture require_assertions(sys.flags.optimize) 双保险（测试覆盖 optimize=1 → RuntimeError）。runner 自身关键判断为显式 if/raise，不依赖 assert，不受优化影响。
6. 口令路径：secrets.token_hex 内存生成 → docker stdin（不在 argv）→ dsn 仅入子进程 env 与内存 → stdout/stderr 落盘前 replace redact + leaked 检查（出现即 contract FAIL）→ meta.json 无口令字段 → state.json error 字段 replace。合同"不进 argv/日志/文件"静态满足。
7. 资源复用静态核：inspect 用 14 字段 --format 投影（注释明确排除 Config.Env，旧口令不入 CLI 输出）；valid_identity 校验 CID/NAME/IMAGE/三标签/唯一卷/端口绑定(127.0.0.1:55439)/1CPU/512MiB/pids128/restart=no/bridge/无 binds；启动前 docker ps --filter label=retrolume-task=083 须空 + loopback 端口 bind 预检；local_auth_and_rotate：容器内 --user postgres 以测试角色 local 认证（identity 双字段核验）→ ALTER ROLE 自改密（stdin）→ loopback 新凭据 psycopg 连接 + current_user/current_database/inet_server_port 三重核验（inet_server_port 返回容器内 5432，与 09 经验一致）。失败任一步 → RuntimeError → finally stop_exact_container 同 CID 收尾（stop 前后双 inspect+valid_identity，stop 失败升级 kill，最终 running=False 必须）。
8. 认证可用性：容器内 local trust 是官方镜像既有事实，runner 失败即停，不降认证、不扩大权限、不创建容器、不读旧 secret。静态层面未发现使复用不安全的原因；"本地认证/改密权限可用"本身只能未来有界试验取得（runner 首步 identity 探测即是该试验）。

## 八、初判结论（待原始日志核对后修正）

P1/P2/F1/F2/F3/R1/R2/R3 八项在代码与控制层均未见确定阻断；lock-barrier 与 offline 证据的"最终 hash 对应哪些已执行方法"须以三批原始 meta/stdout/stderr 定分（批间修正时点），留待下一页。0.9s 固定观察窗的 FLAKY 失败方向安全。猝死窗口定性为可管理边界。
