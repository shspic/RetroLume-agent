# TASK-083 / R-077 / STEP008 执行结果：固定launcher组合真实验证09与D3恢复决策（当前有效）

**状态：卡面三项成果全部交付——①新增 launcher_control.py/launcher_scenario.py 夹具并经真实 run_supervised_window→固定SUP→worker 组合在专用真实PG上完成四场景验证：A正常完整入口 settled（真实PG认领/关门/结算，G1→G2、S=1/R=0/closed=true、SUP与worker进程复核消亡、在飞观察记录worker双进程PID+创建时间）；B父级管理截止经wait真实调用边界确定性注入（claim已提交+业务Job在管两真实前提）——SUP有界终止、结果R/S/pending全None、cleanup_incomplete=true，**SUP死亡后业务Job内2个worker进程仍存活**（控制者持精确句柄实测，"SUP退出≠树空"正证据），控制者终止后归零，DB保留R=6/S=0/closed=false不退款；C1父在Resume前被精确终止——悬停SUP不迟到Resume/不迟到认领（DB恒pending、Job对象G0/G1均不存在、2秒有界负观察无变化），控制者精确收尾悬停SUP、映射销毁核验通过；C2父在Resume后（claim完成+worker在飞时）被精确终止——已运行SUP独立完成自身截止与映射生命周期（self_exit=true、DB收敛pending/G2/S=1/closed=true、Job对象与SUP映射均销毁、两个worker PID复核消亡）。②批内尝试账2真实批/8场景启动（≤3批/≤12），前置runner缺陷两轮（预算算术、loop factory）如实留档；最终批 exit=0、8.80s、all_pass=true、19文件hash零漂移、产品源码零改动。③D3给出有原始依据的最小恢复方案：claim事务随G原子新增一列 running_owner_session_id（SUP经ProcessIdToSessionId自证），同号⇒同Local命名空间（官方S1）⇒互斥+FILE_NOT_FOUND严格区分+租约过期后全额保守折叠W；异号/缺值失败关闭；跨boot同号情形下旧进程必然全灭故折叠同样安全——**无需官方并不存在的用户态boot GUID**；不新增常驻见证、不追溯部分退款；新增持久字段须用户批准门，本卡未实施。未验证/不宣告：真实one_call业务链、旧G实际恢复执行、D3方案实施均not_run/not_done；不签独立安全验收，不宣告M-1/STEP008。执行窗口实际身份GLM-5.3-Flash（接续原083实现窗口，非独立审计）。**

## 交付1：夹具与四场景事实（最终批 20260925-1658，results.json 为准）

| 场景 | 结果 | 关键正证据 |
| --- | --- | --- |
| A 正常完整入口 | 通过 | state=settled、G1、Job名精确匹配、worker主PID 28612（venv launcher）+从PID 31580 在飞记录创建时间、active_end=0、S=1（elapsed 0.75s）、R=0/pending=0、cleanup_incomplete=false、timing(t1>t0,observed=1,W=6)、SUP PID 31612+创建时间且事后Open失败(87)；DB：pending/G2/R0/S1/closed=true/last_settled G1。 |
| B 父级管理截止 | 通过 | 注入在wait真实边界触发（G1已认领）；outcome：manager_timeout_unconfirmed、R/S/pending=None、cleanup_incomplete=true、SUP PID 13284有终止；**SUP死后Job内active=2（PID 18212/32940+创建时间在案）→控制者terminate→0**；DB：running/G1/**R=6**/S=0/closed=false/租约在——保守预扣保留、零退款。 |
| C1 父死前退出 | 通过 | P屏障证据（SUP PID 31660+创建时间+映射名）；P两进程精确终止确认；SUP悬停 alive+创建时间匹配；DB恒pending、G0/G1对象均不存在；2s负观察无变化；控制者精确终止SUP；映射open失败（销毁证实）。 |
| C2 父死后退出 | 通过 | pre_resume+at_wait双屏障；父死时DB running/G1、Job内active=2（PID 11060/6388在飞在案）；P精确终止；SUP alive→**25s内自退出（self_exit=true，未用兜底终止）**；DB收敛pending/G2/R0/S1/closed=true/last_settled G1；Job对象与SUP映射查询如实失败（销毁）；worker残留复核两PID均消亡。 |

场景D（映射交接）判定不适用：A/B/C1/C2 已覆盖映射创建/打开/写入/销毁全生命周期（C1 未打开即销毁、C2 双方句柄关闭后销毁），半帧/校验路径沿既有纯单元证据复用，无新增未覆盖风险。

## 交付2：尝试账与复用范围

- 资源预检1次（Docker/镜像/端口/venv 全OK）+ 静态检查批3次（前两次为检查脚本自身缺陷，第3次ALL PASS）。runner/批尝试4次：1652 拦截轮（runner预算算术，0启动）→ 1653 预备轮（ProactorEventLoop，0启动）→ 1655 首验批（A/B/C1通过、C2时序缺陷失败，控制者安全网精确收尾无泄漏）→ 1658 复验批（**四场景全通过**）。真实批计数2/≤3，场景启动8/≤12。
- 修复均属卡内授权范围且零产品改动：①runner TOTAL_WINDOW=660/批前检查口径；②build_activity 用 psycopg_compatible_loop_factory；③c2 触发改为"claim已提交+Job含worker"真实事实的有界轮询；④results.json 序列化 default=str。
- 复用（未重跑）：Job07五场景、PG08六例、084已审静态结论、005/repository冻结、official-facts.md 六页。本卡改动文件仅 launcher_control.py/launcher_scenario.py（新增），19文件冻结（Job07参照13+PG08四文件+新2）pre/post零漂移；attempt-1655 的批级原始日志被 1658 同名覆盖（runner固定文件名缺陷，如实登记），attempt 级 p-evidence/p-stderr 全留存。
- 资源：4个专用容器（每runner一次）全部 Exited(0) stop保留、标签 task=083/phase=d1-09/run=<runTag>、旧PG08三容器未触碰、55438释放；**卡面"一个容器"与实际的4个偏差如实登记，处置权留编排**。DSN口令仅批内环境、输出全脱敏、未打印。

## 交付3：D3 恢复决策（详见 evidence d3-sources-and-decision.md）

- 新增官方事实5项（≤6）：S1 Kernel Object Namespaces（Local\=会话命名空间；会话号按登录顺序分配）、S2 Object Names（job与互斥同空间）、S3 Job Objects/KILL_ON_JOB_CLOSE（最后句柄关闭→杀树→销毁；本批C2真实实证）、S4 ProcessIdToSessionId（SUP可自证会话号，无需特权）、S5 logoff（注销终止会话全部进程）。
- **推荐方案（须用户批准，未实施）**：claim事务随G原子写 `running_owner_session_id`；恢复时同号⇒持活动互斥（无迟到创建屏障）→严格区分ERROR_FILE_NOT_FOUND→租约过期→**全额保守折叠W**（同号跨boot情形旧进程必然全灭，折叠亦安全，故无需不可得的boot GUID）；异号/缺值（含迁移旧行NULL）⇒失败关闭。不部分退款、不新增常驻见证。替代解（不批字段）：单交互会话部署+异号全人工runbook折叠。
- **唯一必要决定**：是否批准该一列持久扩展与"同号自动折叠/异号失败关闭"语义（或选择纯人工替代解）。

## 后续（沿卡）

- 本结果与最终diff一次交原084窗口独立增量终审（B/C的注入边界与安全网语义为终审重点）；docu/CHANGE.MD与执行状态沿惯例由编排补记。
- 若D3方案获批：另卡实施（006迁移+claim接口+定向PG三例+恢复纯单元），不混入本卡。

证据目录：Ndocu/evidence/task-083/launcher-complete-09/（manifest.md、results.json、d3-sources-and-decision.md、post-run-check.json、precheck、runner、static_check_09、两轮P证据、容器inspect、批输出）。

以下保留前轮结果原文字节，作为历史记录；以上当前状态优先。

---
# TASK-083 / R-077 / STEP008 执行结果：005及关闭门六例真实PG验证08（当前有效）

**状态：卡面精确六例在专用真实PG上一次全部通过——`Ran 6 tests in 1.897s / OK`、unittest exit=0、0失败/0错误/0skip、failfast未触发（stderr原始输出在案）；005空表迁移仅增dispatch_closed、非空表005整体回滚、关门后拒绝admit/mark且合法outcome收敛、关门先提交先于并发admit/mark（真实来源锁+屏障交错）、取消关门+旧dispatched UNKNOWN收敛、旧G/C幂等ALREADY_SETTLED不碰新窗，全部实际事务验证成立。三容器（批次一/二/三）均stop后Running=false、cleanup_ok=true，容器/卷/库/6个schema全保留，冻结四文件hash运行前后零漂移，源码/测试/迁移/正式docu/公共库/Git零写入。仅确认这六个当前真实PG用例：不扩成新D1真实launcher、不覆盖run_supervised_window固定SUP入口、不解决D3旧G恢复、不签M-1/STEP008或独立安全通过。执行窗口实际身份GLM-5.3-Flash（接续原083实现窗口，非独立审计，如实登记）。**

## 批次史与例外授权（如实登记）

| 批次 | runTag/容器 | 结果 | 根因与处置 |
| --- | --- | --- | --- |
| 一 | 20260925-1455 / 8b2b6349… | 就绪核对30s超时停批，六例not_run | 本卡自备runner就绪检查SQL将PG裸关键字`current_user`误写`current_user()`，服务器持续报语法错误；连接/认证/库全程正常。非环境/夹具/被测对象缺陷。 |
| 二 | 20260925-1509 / 10faef60… | 身份核对停批（连接1.62s即成功），六例not_run | runner将`inet_server_port()`（返回容器内监听端口5432）误预期为宿主映射端口55437；db/user核对全对。 |
| 三（最终） | 20260925-1515 / b8b7982f… | **六例全部通过** | 修正01—03后：标签+宿主端口绑定核对OK、PG就绪身份三核对一致（1.64s）、unittest exit=0、finally干净（5.49s总）。 |

两次停批均由用户明确授权例外后继续（15:10"授权例外重跑"、15:15"授权批次三"）；三次运行的runner/输出/inspect全部留档，批次三实际运行脚本字节副本runner-batch3-as-run.py（sha256=52ba7c44…74933）与误标verdict的runner-state.json原样保留不覆盖。runner共有三处检查/解析缺陷（current_user括号、inet_server_port语义、Ran/OK摘要解析只查stdout），均属本轮证据目录内自备脚本问题，不影响夹具/被测对象证据；verdict以原始stderr输出+退出码为准。

## 六例逐项事实（unittest-stderr.txt原始行+stdout schema行）

| 用例 | 实际 | 保留schema（全保留，无失败保留行） |
| --- | --- | --- |
| pg_migration_01_empty_table_adds_only_closed_column | ok：001—004后空activities执行005，仅新增列dispatch_closed(boolean,NO,default false) | task083_migration_91f93dae… |
| pg_migration_02_nonempty_table_rolls_back_whole_005 | ok：非空表005抛psycopg.Error、ROLLBACK后数据仍在且无dispatch_closed列，合成行FK清理 | task083_migration_b0bae76d… |
| pg01_close_settle_and_old_gc_does_not_touch_new_window | ok：关门→关门幂等→settle SETTLED→新代次claim开门→旧G settle ALREADY_SETTLED不碰新窗→过代次close拒绝 | task083_close_cdef47ba… |
| pg02_closed_gate_rejects_admit_mark_but_records_outcomes | ok：关门后admit/mark均AdmissionDenied，reserved/dispatched记UNKNOWN、received保留，not_sent=0/unknown=2/received=1 | task083_close_8fed9a16… |
| pg03_close_commits_before_concurrent_admit_and_mark | ok：真实来源锁持有+请求屏障控制交错，close先提交，并发admit/mark均拒绝 | task083_close_6d1cda74… |
| pg04_cancel_closes_gate_and_old_dispatched_unknown_converges | ok：cancel关门（closed=true、R=0、S=90整树结算），旧dispatched记UNKNOWN收敛 | task083_close_97643930… |

## 版本、资源与零写入证明

- venv Python 3.12.10、psycopg 3.3.5、PostgreSQL 17.11 (Debian 17.11-1.pgdg12+2)、Docker server 29.7.2、固定镜像pgvector/pgvector:0.8.6-pg17-bookworm（sha256:cf134a767f47…，在位未拉取）；容器1CPU/512MiB/pids128/restart=no/bridge/无宿主bind挂载/仅127.0.0.1:55437→5432；合成账号task083_pg08+随机口令仅注入本次子进程环境，全部输出经口令过滤，未记录完整含口令DSN。
- 运行前后核验：四冻结文件（pg_migration.py/pg_close.py/repository.py/005.sql）hash全MATCH零漂移（precheck两次+post-run-hash-check.txt）；git status backend/仅含083既有实现差异，与卡面"既有差异保护"一致；本卡写入仅限Ndocu/evidence/task-083/pg-run-08/与本置顶段。
- 三个容器均保留（Running=false），含各自匿名卷与库实例；未删除任何容器/卷/schema/database，未执行用户库迁移，未接管073/074/079旧资源。

## 边界与后续（沿卡，不扩）

- 本批只确认上述六个当前真实PG用例；不构成新D1固定launcher真实入口、不覆盖run_supervised_window固定SUP入口、不解决D3旧G恢复（化身来源决策仍开放）、不签M-1/STEP008完成。Job07已验局部行为未重测。
- runner三缺陷修正（01裸关键字、02 proc初始化、03端口语义、04摘要解析）已留档于runner.py供后续卡复用；错误经验应记入D:\shspic\错误记录（编排裁定）。
- docu/CHANGE.MD与执行状态沿惯例由编排补记（本卡禁改正式docu）。证据目录：Ndocu/evidence/task-083/pg-run-08/（manifest.md含批次史与授权记录、precheck、runner及批次三字节副本、container-inspect-created/final、unittest-stdout/stderr/meta、schemas.txt、runner-log/state、post-run-hash-check.txt）。

以下保留前轮结果原文字节，作为历史记录；以上当前状态优先。

---
# TASK-083 / R-077 / STEP008 执行结果：受控真实Windows Job验证07（当前有效）

**状态：编排一次解冻的现有Job01—05真实Windows合成批，五场景全部实际启动并按已审控制器裁定通过——01正常早停（settled、事件序[inspect,claim,close_db,settle]、C=1≤W=6、整树0后关门/结算）、02挂死（stopped_at_deadline、全窗6s保留不结算、真实树空0）、03主进程先退后代存（descendants_after_primary=2、确切终止至整树0）、05同名Job碰撞拒绝（collision_rejected=true、原Job精确身份在案）、04最后句柄（Start生命周期+身份回执、PID/创建时间精确核验、SUP退出前Job计数1、释放观察句柄后worker signaled、对象销毁后查询如实null）。批命令exit=0、墙钟14.122011s（单一计时源run_batch_07.py perf_counter）≤60s，未超时、无cleanup_incomplete、无归属/树未知、无句柄错配；运行前后15项冻结hash零漂移（卡面运行链4文件+9直接依赖+信息项2），精确PID残留核验与补充只读扫描均无遗留，本批对源码/夹具/迁移/正式docu/公共库/旧证据零写入。即使五例全过，也只确认这五个已审合成Job行为：不覆盖新run_supervised_window固定SUP入口（01/02直接run_once、03/05直接Job）、不覆盖真实PG/005（02账本为合成FakeLedger，不得声称PG真实退款）、不解决D3旧G恢复，不宣告M-1/STEP008完成。执行者不签独立安全结论，回传由编排裁定。执行窗口实际身份：GLM-5.3-Flash（接续原083增强实现窗口，非独立审计，如实登记）。**

## 场景逐项事实（依据实际控制器输出裁定；原始JSON逐行存证据，不事后编造）

| 场景 | 实际 | 身份正证据（runTag / UUID+G / Job名 / PID） | 关键观察与清理 |
| --- | --- | --- | --- |
| 01 正常早停 | 已启动，通过 | job-01-e815efbd；活动 81455924-4f7c-49b6-8292-6b79693b2a94，G1；Local\RetroLume.Activity.814559244f7c49b682926b79693b2a94.G1；worker PID 30240（outcome.pid） | state=settled、events=[inspect,claim,close_db,settle]（=已审预期次序）、timing_diagnostic t1>t0（Δ=750000000ns）→C=1、W=6，1≤C≤W；active_processes_before_resume=1、active_processes_at_end=0（Job整树0后关门/结算）；settled=1/reserved=0/pending_fold=0、elapsed=0.75s、cleanup_incomplete=false。账本为合成FakeLedger，不构成PG真实退款证据。 |
| 02 挂死 | 已启动，通过 | job-02-1b31fce6；活动 dc717c60-c767-4272-b069-93297ea56a8c，G1；…dc717c60c7674272b06993297ea56a8c.G1；worker PID 25304 | state=stopped_at_deadline、reserved_seconds=6、settled_seconds=0、events=[inspect,claim]（无settle）、elapsed=5.0s、pending_fold_seconds=6（交原规则保守折叠）；真实树空观察 active_processes_at_end=0、cleanup_incomplete=false——全窗保守账面、不部分退款。 |
| 03 主退后代存 | 已启动，通过 | job-03-29a56b7e；活动 4a5afcc6-6c40-4f70-a735-7f68a9f3f723，G1；…4a5afcc66c404f70a7357f68a9f3f723.G1 | 主进程退出后Job查询 descendants_after_primary=2（>0，主退不当树空；查询值如实记录，不作进一步推断）；随后确切终止/等待至 active_processes_at_end=0、cleanup_incomplete=false。控制器输出不含本场景worker PID（悬停期已由控制器以精确句柄+创建时间+active_before=1核验），如实记录、不补造。 |
| 05 同名碰撞 | 已启动，通过 | job-05-2c58bbb9；活动 a8a1440a-27ea-4a86-8462-044caba2db60，G1；…a8a1440a27ea4a868462044caba2db60.G1 | collision_rejected=true：同名 NamedJob.create 被拒（JobUnknown），原Job身份精确在案、不按模糊名字查杀；active_processes_at_end=0、cleanup_incomplete=false。控制器输出同样不含worker PID（口径同03）。 |
| 04 最后句柄 | 已启动，通过 | job-death-5cdecc24；活动 15b1838f-48aa-4415-93fb-cce26d058597，G7；…15b1838f48aa441593fbcce26d058597.G7；worker PID 27856、created_100ns=134347917200933325 | Start生命周期与身份回执：子端Open消费Start并回执悬停身份后父才释放唯一Start句柄；PID+创建时间经OpenProcess/GetProcessTimes核验；active_processes=1（悬停）与active_processes_before_supervisor_exit=1（Resume前Job计数1）；观察Job句柄先关、SUP退出码0；释放观察句柄后最后Job句柄关闭使worker_signaled_after_last_job_handle_closed=true；对象销毁后无法查询ActiveProcesses时active_processes_at_end=null如实写入（tree_evidence原文在案），不把单进程夹具推成任意整树通用证明。 |

## 命令、退出码与单一计时来源

- 唯一命令（无第二次运行）：`D:/shspic/project_NO3_RetroLume-agent/backend/.venv/Scripts/python.exe -B -m fixtures.task083.job_batch`，工作目录 `backend/tests`；run_batch_07.py 包装（Popen在OS层直录stdout/stderr，退出码取自Popen.wait()，不以工具yield当进程已结束）。
- exit_code=0；墙钟14.122011s（单一计时源 run_batch_07.py time.perf_counter；起2026-09-25T14:35:06.067+08:00，止14:35:20.189+08:00）；timed_out_at_60s=false；批内55s自身deadline与场景30s上限均未触及；stderr为空。
- 实际启动5/5，通过5/5，失败0，跳过0；场景次序01→02→03→05→04按已审脚本内置次序执行，未重排、未补跑。

## 清理确认与零写入证明

- 逐场景控制器 cleanup_incomplete=false；01/02/03/05 active_processes_at_end=0（确切整树0）；04 worker signaled（最后句柄关闭致worker退出）。
- 运行后只读精确核验（post-run-check.json）：控制器打印的 01 PID 30240、02 PID 25304、04 PID 27856 OpenProcess 均error 87（进程已不存在），无"同PID同创建时间"残留；03/05 控制器不打印PID，以整树0为清理证据；补充只读名称扫描（task083相关命令行）0条，仅作旁证、不充当树空证明。未知对象/遗留：无；旧不明进程未触碰。
- 运行前（pre-run-check.json）与运行后（post-run-check.json）各15项hash一致：卡面运行链4文件（job_batch 648e419c…、job_control 5bc35bf1…、scenario_child 98f132f2…、fixture c9970b8d…）+9直接依赖（windows_job/session/command/worker_main/launcher/supervisor_ipc/supervisor_main/gate/test_worker_session，沿stub-fix-05与084 review-02冻结记录）+信息项repository/005——本批零写入证明。

## 边界、复用与后续（沿卡，不扩）

- 本批只确认上述五个已审合成Job行为；不覆盖新 run_supervised_window 固定SUP真实入口、不覆盖真实PG/005、不解决D3旧G恢复，不宣告M-1/STEP008完成。剩余已登记路线：专用PG六例、新D1受控入口准备、D3化身事实决策，均不在本批。
- 旧5场景尝试、超时偏差与费用不重置；本批为独立一次授权运行，未复用旧04 count0筛选替代观察。
- 执行者不签独立安全结论；需要独立解释的新风险沿084窗口增量审，不默认再审全仓。docu/CHANGE.MD与正式执行状态沿惯例由编排补记（本卡禁改正式docu）。
- 证据目录 Ndocu/evidence/task-083/job-run-07/：manifest.md（运行前冻结值/命令/次序/预算/停止与精确清理办法）、prep_run07.py、pre-run-check.json、run_batch_07.py、run-batch-stdout.log（逐场景原始JSON）、run-batch-stderr.log、run-batch-meta.json、post_check_07.py、post-run-check.json。

以下保留前轮结果原文字节，作为历史记录；以上当前状态优先。

---
# TASK-083 / R-077 / STEP008 执行结果：生命周期夹具完整修正06（当前有效）

**状态：review-04定位的三处同链替身缺陷（①硬编码身份回执 ②open_existing断言硬编码身份 ③starter/kernel句柄基址撞号）已一次合并修复，静态核对34项ALL_PASS，最终定向批三例全部通过——生命周期两例首次经真实verify_last_handle完整控制流验证通过（此前三轮分别停在argtypes赋值、身份校验），05确定时钟例首次通过（t1>t0、ceil=1/W=6、树0后关门、同G结算重试）。本卡只修替身不修控制器，job_control.py语义零改动；真实Job与PG仍冻结，静态/替身通过不构成真实OS证据，不宣告M-1/STEP008完成，不填写编排最终验收。执行窗口实际身份：GLM-5.3-Flash（接续原083增强实现任务，非独立审计，如实登记）。**

## 本轮改动（唯一允许文件，三项一次完成）

backend/tests/fixtures/task083/focused_unit.py：pre_sha256=4a633aff…7a1ca（=卡冻结值，改前真实字节副本+hash见 pre/、pre-hashes.txt）→ new_sha256=dfaaf814bb6abeea0a7f82d8499b1e03915c87bad50aa4a50295fcfde3995259。全部改动限于StartLifecycleTests区段（区段外head/tail字节级不变，static-check证明；incremental.diff存档）：

1. **身份派生（修正①）**：删除硬编码`_identity_lines`（旧activity="11111111-…"、run_tag="lifecycle-unit"）；fake_spawn从真实spawn实参派生身份——args[4]=activity_id、args[5]=int(str(generation))、args[6]=run_tag，索引经job_control.py:82-84实际调用文本逐项核对（sys._base_executable, "-B", str(fixture), "controller", activity_id, str(generation), run_tag, start_name），非机械照抄报告数字；按真实job_name函数构造created/resumed回执；pid=123、created_100ns=0、active_processes=1及resumed pid=123等协议字段保持不变。不patch控制器uuid4、不固定控制器内部随机身份、不取消任何身份校验（patch面仍仅三处OS边界：job_control.ctypes.WinDLL、job_control.asyncio.create_subprocess_exec、job_control.NamedJob）。
2. **派生身份回传与断言（修正②）**：_run签名改为`(*, receipt="identity", spawn_error=None)`，返回(次序log, kernels, 派生身份, result, 异常)；三分支定义清晰——"identity"=按派生身份回执两行、"empty"=spawn成功但空回执、spawn异常=不产生身份（保持空dict）；成功例与失败分支B的open_existing正反断言改用派生身份+字面量7（job_control.py:36固定int 7与FakeNamedJob记录类型一致）；分支A新增显式断言`identity == {}`（spawn未成功不产生派生身份，防未定义身份变量）。断言能发现任何不应发生的open_existing调用：控制器内部随机activity经spawn实参派生同源，不以硬编码元组掩盖行为。
3. **句柄基址分离（修正③）**：Kernel.__init__接收base，fake_windll按实例序号分配互不相交基址（starter=100起、kernel=100100起）；Start父句柄与worker/事件句柄不再共用编号空间，`count(("close_handle", start_handle))==1`等断言按原语义成立；每类API的返回、指针输出（byref _FILETIME全0与created_100ns=0匹配）与调用记录语义不变；Start回执后关闭、恰一次释放、观察Job先释放再Exit、失败清理等次序断言原样保留，不改断言迎合错误次序。

## 静态核对（一次执行额度，34项ALL_PASS）

static_check_06.py（托管3.13.12执行，文本/AST/hash三层，不import不写pyc，0.036秒≤60秒，单次执行无重试）：① 三文件冻结复算MATCH（focused_unit pre=4a633aff…、job_control=5bc35bf1…3980d2、offline_unit=3029a709…4c5c），零漂移；② 区段限制：pre/post的head（模块docstring/导入/EventControlTests）与tail（FrameTests/ConfigFactory/LauncherTests/main）字节级相等，diff仅落StartLifecycleTests区段——碰撞两例与D1期限用例方法体未变；③ AST：_identity_lines已删、_run唯一5元组return、三方法齐备；④ 全流程文本一致性：派生索引与job_control.py:82-84实参顺序跨文件核对、open_existing传int generation、身份校验tuple原文未动（无契约弱化）、无uuid4 patch、回执字段与协议一致；⑤ 有限diff写入incremental.diff。

## 运行账（新增且仅一次定向批；先冻结后运行）

| 命令 | 退出码 | 耗时（单一计时源run_batch_06.py perf_counter） | 结果 |
| --- | --- | --- | --- |
| 1：`backend/.venv/Scripts/python.exe -B backend/tests/fixtures/task083/focused_unit.py --failfast StartLifecycleTests.test_04_start_handle_closes_after_identity_receipt StartLifecycleTests.test_04_start_handle_release_exactly_once_on_failure`（工作目录=项目根） | 0 | 2.478099秒（≤60秒） | **2 tests OK**：成功例与失败例均实际运行，failfast未触发任何跳过 |
| 2：`backend/.venv/Scripts/python.exe -B backend/tests/fixtures/task083/offline_unit.py OfflineRepairTests.test_05_early_success_uses_tree_zero_close_then_same_g_settle_retry`（命令1通过后才启动） | 0 | 0.883秒（≤60秒） | **1 test OK** |

- 成功例：真实verify_last_handle控制流全路径——fake spawn→SetEvent(100)→首次readline收到派生身份回执→job_control.py:97-100身份校验通过→CloseHandle(100)恰一次→OpenProcess/GetProcessTimes→open_existing（派生身份,int 7）→Arm→resumed回执校验→job_close先于Exit→returncode 0→最后句柄等待通过。
- 05例诊断行：t0_ns=1000000000000、t1_ns=1000400000000（t1>t0）、delta_ns=400000000、observed=1、window=6、state=settled、job_events=[spawn_suspended, resume, query, close_job]；导入hash session=502a3743…f16c、offline_unit=3029a709…4c5c与冻结一致（日志offline-05-06.log）。
- 累计3.361秒≤120秒；PASS仅绑定最终快照dfaaf814…5259；无真实事件/Job/spawn/子进程/PG/Docker/网络调用。

## PASS适用范围、复用与风险

- 保留PASS（局部不变性延续，不重跑）：EventControlTests碰撞两例、LauncherTests D1期限一例——区段外字节级不变+直接依赖冻结复算MATCH；第12项及其余9项沿084口径复用。
- 未运行/缺口（如实登记）：真实Job与PG仍冻结；生命周期两例验证的是真实verify_last_handle控制流+全替身OS边界，不构成真实Start/Arm/Exit事件、真实Job对象、真实子进程证据；旧05根因仍未证（本轮按要求不研究）；D3不研究不实现，旧G未知保持失败关闭；新D1固定launcher真实入口OS证据缺口保留。
- 后续（沿卡）：三例及差异经原084增量确认后，由编排分别安排受控真实验证；本卡未追加任何运行。docu/CHANGE.MD登记沿前几轮惯例由编排补记（卡面禁改正式docu）。
- 证据目录Ndocu/evidence/task-083/fixture-completion-06/：prep_evidence.py、pre/（三文件字节副本）、pre-hashes.txt、static_check_06.py、static-check.txt、incremental.diff、final-hashes.txt、manifest-final.txt、run_batch_06.py、unit-lifecycle-06.log、unit-lifecycle-06-meta.txt、offline-05-06.log、offline-05-06-meta.txt。

以下保留前轮结果原文字节，作为历史记录；以上当前状态优先。

---
# 历史：TASK-083 / R-077 / STEP008 执行结果：夹具替身修正05与剩余三例验证（stub-fix-05轮原文）

**状态：04轮替身兼容缺陷已修——partial包装使argtypes/restype赋值合法，静态核对ALL_PASS；但新增定向批首命令 1/2 FAIL 即停：生命周期成功例在真实verify_last_handle内推进到身份回执校验后，因夹具回执身份与控制器内部随机身份结构性不匹配（"Job/G/runTag身份不匹配"）而失败；第二例因failfast未运行，命令2（offline 05）not_run。按卡"失败即停、不再修正复跑、不开启无限修正批"，本轮到此交回原084独立窗口审视夹具与具体失败。Job/PG仍冻结；不宣告真实Job/PG通过、D3恢复解决或M-1/STEP008完成。执行窗口实际身份：GLM-5.3-Flash（接续原083增强实现任务，非独立审计）。**

## 本轮改动（唯一允许文件）

backend/tests/fixtures/task083/focused_unit.py：pre_sha256=1e58eb03…8ce08（=卡冻结值，改前真实字节副本+hash见 pre/、pre-hashes.txt）→ new_sha256=4a633aff536f833cdbf3a266be2d44de70b8e01105a204b68d7947995627a1ca。仅三处hunk（incremental.diff共40行）：① 新增标准库导入 `from functools import partial`；② StartLifecycleTests docstring追加partial包装说明（纯追加）；③ StartLifecycleTests._run局部Kernel.__init__将8个API（CreateEventW/SetEvent/CloseHandle/OpenProcess/GetProcessTimes/OpenEventW/WaitForSingleObject/TerminateProcess）以partial包装的实例闭包占位，使verify_last_handle（job_control.py:49-71）对替身API的argtypes/restype赋值合法。API调用语义、参数、返回值、事件记录与故障注入行为零改动。job_control.py（5bc35bf1…3980d2）、offline_unit.py（3029a709…4c5c）及13个冻结文件逐一复算零漂移（final-hashes.txt）。其余全部顶层节点AST与改前副本逐项一致：碰撞两例、D1期限用例的测试方法与直接依赖均未受影响，其旧PASS按"局部不变性"延续证据（不重跑）；functools导入不改变全局初始化行为。

## 静态核对（3次尝试，最终一次ALL_PASS）

stub_fix_05.py（AST/hash/diff，不import、不写pyc，以backend/.venv/Scripts/python.exe -B执行——本卡默认项目解释器，无解释器偏差）：job_control内verify_last_handle/_new_event_or_reject对starter/kernel的argtypes/restype赋值面与调用面各8个API，与Kernel partial包装集和方法集逐一闭合；15个冻结hash全FROZEN_OK。attempt-01/02失败均为检查脚本自身缺陷（ast.AsyncFunctionDef漏扫async的verify_last_handle；docstring前缀判定未先归一缩进，并由此暴露首次docstring编辑曾使62-66行降为0缩进，已恢复统一4空格缩进），非目标文件问题；两次失败日志与meta原样存档（static-attempt-01-fail.log、static-attempt-02-fail.log及对应meta），最终静态static.log+static-meta.txt（1.12秒内，≤60秒达标）。上一轮（04）静态用托管3.13.12而非卡定venv的偏差如实保留于04轮历史记录，本轮不冒称按原命令执行。

## 运行账（新增定向批，失败即停）

- **Command 1**（`backend/.venv/Scripts/python.exe -B backend/tests/fixtures/task083/focused_unit.py --failfast -v StartLifecycleTests.test_04_start_handle_closes_after_identity_receipt StartLifecycleTests.test_04_start_handle_release_exactly_once_on_failure`，工作目录=项目根D:/shspic/project_NO3_RetroLume-agent）：**exit=1，1.1161450秒**（run_cmd.py单一计时源perf_counter；unit-lifecycle-01.log/meta）。
  - FAIL（failfast，第二例未运行）：`test_04_start_handle_closes_after_identity_receipt`——`assertIsNone(exc)`失败，exc=AssertionError('Job/G/runTag身份不匹配')。**精确定位（未修）**：修正04的AttributeError已消除，流程真实推进：fake spawn→SetEvent(100)→首次readline收到_identity_lines回执→json解析→job_control.py:97-100身份校验失败。verify_last_handle内部自生成activity_id=str(uuid4())（:34）与run_tag="job-death-"+uuid4().hex[:8]（:35），而_identity_lines回执硬编码activity="11111111-1111-1111-1111-111111111111"、run_tag="lifecycle-unit"，phase/generation/pid/created_100ns匹配但activity_id/run_tag/job_name三字段必不匹配——夹具回执身份与控制器内部随机身份结构性不相容，是partial修复点之后新暴露的第二个夹具缺陷（修正04运行从未到达此路径）。修复需patch job_control.uuid4为确定性值并同步_identity_lines常量（或等价方案），属语义性替身扩展，超出本卡"只改Kernel API替身+必须标准库导入"授权，按停机纪律不修、不复跑，交原084窗口裁定。
  - `test_04_start_handle_release_exactly_once_on_failure`：**not_run**（failfast首例失败即停；其分支A spawn异常与分支B空回执路径均不触及身份校验，但本轮无运行证据）。
- **Command 2**（offline_unit.py OfflineRepairTests.test_05_early_success_uses_tree_zero_close_then_same_g_settle_retry）：**not_run**（首命令失败即停）。05确定时钟注入运行验证仍为零。

## PASS适用范围、复用与风险

- 保留PASS（局部不变性延续，不重跑）：EventControlTests碰撞两例、LauncherTests.test_d1_deadline_before_resume_terminates_exact_owner（AST逐项一致+直接依赖FROZEN_OK+导入增量functools唯一）；第12项及其余9项沿084口径复用。
- 风险/未闭合：① job_control.py生命周期修改至今无一次完整通过运行（本轮推进至身份校验即失败，04轮失败点在argtypes赋值）；② D1期限PASS原绑定focused_unit.py旧hash 1e58eb03…，本文件已轮换为4a633aff…，其PASS按"测试方法与依赖未变的局部不变性"主张，适用性由084认定；③ 05仍未运行验证；④ 新暴露夹具身份缺陷的最小修法待084审定，本卡未实施；⑤ 真实Job/PG/事件/子进程本轮零启动，D3恢复未闭合、新D1固定入口OS证据缺口保留；⑥ docu/CHANGE.MD仍未登记（卡面禁改正式docu，建议由编排补记）。
- 证据目录Ndocu/evidence/task-083/stub-fix-05/：prep_evidence.py、pre/、pre-hashes.txt、stub_fix_05.py、static.log、static-meta.txt、static-attempt-01-fail.log、static-attempt-02-fail.log及两个对应attempt meta、incremental.diff、final-hashes.txt、manifest-final.txt、run_cmd.py、unit-lifecycle-01.log、unit-lifecycle-01-meta.txt。本轮结果以上方置顶段为准，历史各轮原文字节保留于下方分隔线之后。

以下保留前轮结果原文字节，作为历史记录；以上当前状态优先。

---
# TASK-083 / R-077 / STEP008 执行结果：定向夹具修正04（当前有效）

**状态：三项夹具修正候选已写入（AST/静态一次通过、13个未改文件零漂移），最终离线批首命令 2/5 FAIL 即停：新增生命周期两例因测试替身自身 AttributeError 未执行到被测路径，D1 Resume 前截止用例修改后首次 PASS；第二命令 not_run，05 时钟注入未运行验证。按卡"失败即停、不追加修正复检"，本轮未修替身、未复跑。Job/PG 仍冻结；不宣告真实 Job/PG 通过、D3 恢复解决或 M-1/STEP008 完成。**

## 三项改动（原→新）

| 文件 | pre_sha256（与卡冻结值一致） | new_sha256 | 改动 |
| --- | --- | --- | --- |
| backend/tests/fixtures/task083/job_control.py | f76f0a4e…dcb95 | 5bc35bf1…3980d2 | `verify_last_handle` 合并为单一大 try：create_subprocess/SetEvent→readline→身份校验通过后才 `starter.CloseHandle(start_event)`（start_released 标记防重）；finally 统一精确收尾含 start_event 恰好一次释放与 proc None 防护。原"SetEvent 后立即关闭唯一父句柄"的竞态出口删除；kernel 配置段前移至 try 前（纯 argtypes 赋值，行为不变）；deadline/remaining 与观察 Job 释放时点不变，不延长总期限、不跨越最后句柄死亡测试。 |
| backend/tests/fixtures/task083/focused_unit.py | 0887adee…cff6d4 | 1e58eb03…8ce08 | D1 期限用例 `_remaining` 序列 (5,5,5,0,0)→(5,5,0,5,5)（第三次 Resume 前检查归零，finally 清理保有 5s），断言增强为精确事件序列+账字段未知+不读结果；新增 StartLifecycleTests（2 方法，调用真实 verify_last_handle，patch job_control.ctypes.WinDLL / asyncio.create_subprocess_exec / NamedJob；成功分支断言回执先于关闭、失败分支覆盖提前异常与空回执）。 |
| backend/tests/fixtures/task083/offline_unit.py | 3e79ce97…5cb04 | 3029a709…4c5c | 新增 _TestClock（读取返回固定值、仅显式 advance 0.4s）；FakeJob.wait_empty_until 注入 clock 时以确定性推进代替 2ms 真实睡眠（clock=None 旧路径保留不变，其他用例零影响）；test_05 以 patch("app.worker.session.time") 与本模块 time（脚本直跑为 __main__）注入，断言 t1>t0、Δ=400000000ns、ceil=1、W=6、job_closed 先于 close_db、settle×2 同 G、(settled,reserved,pending)=(1,0,0)。生产 session.py 未触碰，C0 拒退与 C>W 拒绝语义不变（hash 零漂移）。 |

完整有限 diff：`incremental.diff`；逐文件新旧 hash 与未改文件防漂移：`final-hashes.txt`（launcher/session/supervisor_ipc/supervisor_main/command/worker_main/gate/repository/005/fixture.py/scenario_child.py/job_batch.py 全部 FROZEN_OK；windows_job.py 登记 d05ca259…f6f6，job_name 纯字符串构造已核实）。改前真实字节副本与卡冻结值核对一致：`pre-hashes.txt`、`pre/`。上一轮卡已由编排归档 `Ndocu/archives/TASK-083-before-fixture-repair04-20260924.md`。

## 验证账与失败定位

证据目录 `Ndocu/evidence/task-083/fixture-repair-04/`：

- 静态检查一次通过（AST parse，不 import、不写 pyc）：`static_check.py` → AST_OK 3 路径 + FROZEN_OK 12 路径，0.047345 秒（托管 3.13.12 解释器执行，仅静态解析）。
- 最终离线批 manifest（6 方法限额、OS 替身覆盖确认清单）：`manifest-final.txt`；runner `run_batch.py`，单一计时来源 time.perf_counter。
- **Command 1**（`backend/.venv/Scripts/python.exe -B backend/tests/fixtures/task083/focused_unit.py` + 5 个精确 ID）：**exit=1，1.0503720 秒**（`unit-final-01.log`、`unit-final-meta.txt`）。
  - ok×3：`EventControlTests.test_04_start_collision_closes_only_returned_handle`、`test_04_start_creation_error_and_new_handle`（原碰撞两例未改）、`LauncherTests.test_d1_deadline_before_resume_terminates_exact_owner`（修改后 PASS：state=manager_startup_deadline_unconfirmed、精确序列 ["create_suspended","identity",("wait",0),"terminate",("wait",5.0),"process_close"]、无 resume、账字段 (None,None,None)、无 read_result——**Resume 前截止分支首次有效替身验证**；claim 结构上不可能发生，因 SUP 从未 resume 且 claim 仅存在于 SUP 内的 session.run_once）。
  - FAIL×2：`StartLifecycleTests.test_04_start_handle_closes_after_identity_receipt`、`test_04_start_handle_release_exactly_once_on_failure`，原因均为 `AttributeError("'method' object has no attribute 'argtypes'")`。定位：verify_last_handle 对 starter/kernel 的 API 设置 argtypes/restype（job_control.py:49-71），替身 Kernel 以普通绑定方法模拟 API 不可设属性；异常发生在任何生命周期断言与 job_control 新代码路径执行之前。**job_control.py 生命周期修改的运行验证为零。**
- **Command 2**（offline_unit.py test_05）：**not_run**（首命令失败即停）。05 确定时钟注入运行验证为零，`__main__.time` patch 方案亦未经运行检验。

## 已明确的下一步（供编排裁定，未执行）

最小修正只涉 focused_unit.py 的 StartLifecycleTests 替身：Kernel 各 API 用 functools.partial（或可设属性的可调用包装）绑定实例闭包，使 argtypes/restype 赋值合法；job_control.py 与 offline_unit.py 不动。修正后 focused_unit.py hash 轮换，本轮 command 1 的 5 例（含已 PASS 的碰撞两例与 D1）须按同一 manifest 复跑，再跑 command 2；按卡"后补代码对应测试 not_run，不能沿用通过"。生命周期两例通过后，04 生命周期修改才存在首个替身运行证据；随后由原 084 窗口只复核本三处差异与日志，受控 Job 真实验证仍另卡（新 D1 固定 launcher 真实入口仍无运行证据，Job01—05 不能替代）。

## 复用与风险

- 复用：第 12 项不重跑（command/worker_main/gate 未变，本轮 FROZEN_OK 再证）；其余 9 项按未受影响依赖沿用；旧 05 诊断不重复取证；D3 本轮不再调查，旧 G 未知继续失败关闭。
- 风险：① job_control.py 修改与 offline_unit.py 时钟注入当前只有静态证据，行为验证 not_run；② 生命周期替身修复未实施，其 PASS 行为未知；③ D1 本轮 PASS 绑定 focused_unit.py hash 1e58eb03…8ce08，同文件再改即失效；④ 真实 Start/Arm/Exit 事件、子进程、Job、最后句柄行为仍未运行（Job 冻结）；⑤ 旧 05 失败原因仍未唯一确定（如实保留），2ms 跨时钟刻度依赖已在源码层消除但待运行证明；⑥ docu/CHANGE.MD 未登记（卡面禁改正式 docu，建议由编排补记）。

以下保留前轮结果原文字节，作为历史记录；以上当前状态优先。

---
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
# TASK-083 / R-077 / STEP008 执行结果：审计修复轮02（当前有效）

**状态：部分完成并停止本轮。不得进入 Job/PG 运行门或产品接线。** 本窗口实际标签 GPT-6，是原083实现者，不承担独立安全审计。084的D1管理启动上界、D3恢复证明仍未闭合；本轮最终命令路径修正后的定向复检3项中1项失败，原因未证实，修正/复检额度已用尽。原5个Job、旧04缺证及历史失败预算不清零；005未执行，PG/Job本轮启动数均为0；不宣告STEP008或M-1完成。

## D1—D8 增量结论

| 审计项 | 本轮变更与最终定位 | 状态和限制 |
| --- | --- | --- |
| D1 启动/IPC/期限 | launcher.py:46 将管理截止分出清理预留，所有已返回的Process对象使用同一绝对截止有限join/terminate/kill；start异常后按精确对象尝试收尾，poll/recv/close异常保留未知结果。纯替身09—11覆盖这些分支。 | **未闭合、运行阻断。** multiprocessing.Process.start返回前没有独立可终止的SUP句柄；子pipe.send和父recv仍可能卡在无独立取消的调用，有限故障模型下不能证明整体期限。不得以替身通过冒充生产启动/IPC上界。最小控制结构变更见下文。 |
| D2 固定入口/门 | command.py:15,28 固定项目venv解释器与唯一 app.worker.worker_main 模块，只接受 idle/one_call受限任务数据，不能由生产参数提供exe、-c或脚本；worker_main.py:27,46 的真实模块入口调用run_internal_task→run_controlled_worker→ClosingCallGate。one_call在无供应商接线的产品入口会明确失败；假gateway纯单元12证受控调用。 | **代码候选，Job与真实供应商未验。** venv转发器可能增加Job内进程，未来控制器按确切Job整树检查；不得把初始PID当最终解释器。 |
| D3 失败后恢复 | session.py未改；旧Job打不开时仍失败关闭，claim已提交但Job已消失可永久挂R。 | **提案待编排裁定。** 不能把Open失败或单纯主进程退出当整树空；下述持久证明/所有权扩展超出已批准005单列。 |
| D4 合成Job控制 | test_worker_session.py已移除可直接执行的旧WindowsJobTests；job_control.py:18,165、scenario_child.py、job_batch.py:20准备01/02/03/05统一Start→悬停身份→精确Job/进程句柄/创建时间核验→Arm→Resume；04的fixture.py:20加入Start门和单进程Job限额，04观察句柄在Exit前释放。单场景25/20秒，批入口55秒且失败停批。 | **仅准备，全部not_run。** 04最后句柄关闭后不能再查询该Job的ActiveProcesses，结果诚实写null，仅报告关闭前count=1及该单进程夹具的精确进程退出；此证据强度须独立审计。初批04旧count0仍不足。 |
| D5 PG02 | pg_close.py:122 将预留凭证按原合法UNKNOWN收敛，统计期望unknown=2；repository.py未改。 | **静态修复，PG not_run。** |
| D6 取消 | offline_unit.py:145 对claim响应未知的取消断言改为R/S=(None,None)，保留取消重抛与收尾断言。 | **纯单元初批通过，最终此路径源码未再改。** |
| D7 PG隔离 | pg_close.py:38每例随机schema，001—005在其内准备；仓储、行查询、并发、定向FK清理均使用同一search_path DSN；pg_close.py:140以实际来源锁持有/请求屏障控制close先提交和mark先提交的正反序。pg_migration.py:26失败保留schema，本轮不DROP；仅专用环境变量RETROLUME_TASK_083_DATABASE_URL，缺失skip。 | **可执行候选，PG not_run。** 锁与迁移实际事务效果、失败保留和清理仍待定向PG验证；新schema最终删除须另卡授权。 |
| D8 未知树结果 | launcher.py:46后所有外层超时、SUP丢失、start/recv失败均返回R/S/待折叠=None和cleanup_incomplete=True，即使SUP已退出亦不声称Job树空；有SUP结果但外层清理异常时标记不完整。 | **纯替身08—11通过；真实Job未证。** D1未闭合，不能进入运行。 |

## D1与D3的具体决定边界

D1的决定性缺口是CPython Process.start和Connection.recv的调用中没有可在调用尚未返回时由当前父方握持并取消的精确SUP对象。现有代码已在返回后的故障路径保守收尾，但无法证明启动前后整体deadline。最小后续实现是替换该父级Process/Pipe控制段：父方创建悬停SUP并在Resume前握精确进程/管理Job句柄，使用有界、可取消或可由终止SUP保证结束的结果协议，所有等待共享同一截止；CreateProcess自身内核不返回的情形仍在有限故障模型之外。此项需要先核对相应Windows API事实并经084独立复核，不能继续用新线程包装阻塞start。没有请求本轮额外运行或新增服务。

D3的最小恢复闭环**提案，不是本轮实现或已获批准**：新增按(activity UUID,G)唯一的持久window witness记录及持久owner epoch/CAS接口，记录命名空间/登录会话/boot身份、Job名、worker PID与创建时间、阶段CLAIMED→ASSIGNED→ARMED→TREE_EMPTY及可信主体。claim同事务写CLAIMED；单一持有活动互斥的所有者创建悬停Job/Assign，ASSIGNED提交或同代次读回确认后才可写ARMED并Resume；Job外可信持句柄者查询确切ActiveProcesses=0后写TREE_EMPTY，再允许close/settle。旧SUP晚到须受互斥和epoch CAS拒绝；提交响应丢失只读回同G/owner阶段，不盲目再领或Resume。整应用重启由独立于应用SUP的持句柄见证者按持久记录找回；见证者或证明丢失、命名空间/权限/boot不符时失败关闭，绝不凭Job不存在退款。仅用DB标记和易失Job无法原子地区分“从未创建”与“创建后在标记前崩溃”；该空隙归UNKNOWN，未ARMED者不得曾执行受控工作，仍需互斥/进程归属证明排除迟到创建。见证者自身死亡后的正常恢复仍需经官方Job销毁语义与同命名空间实证判定，否则保持保守预扣，不把新的看门责任递归假定为永不失败。

原批准边界只有005的dispatch_closed；上述持久表/接口及独立见证者均是**需编排取得具体批准的模型/职责扩展**。现合同的失败关闭代价是旧R可能长期不能折叠、无新窗，不能作为满足恢复目标的解法；不能擅自改折叠/结算或添加字段来掩盖。

## 最终文件、差异与验证账

所有改前已保存副本在 Ndocu/evidence/task-083/audit-fix-02/pre；逐文件旧/新SHA256、AST及冻结仓储/005匹配在 static-final.log，增量文本在 incremental.diff。例外：原有 fixture.py 的改前**字节副本遗漏**，其084基线hash为D511DCEA4E7E22F5E01D91B2845479FB8DB4CF5D33405C18E0E1C6ABA7F5636E，最终hash见静态日志；diff将其误列为全新文件，不能据此声称精确增量。其余重要最终hash：command b0e91c3a…、worker_main 5d065b5e…、launcher f650d2b8…、job_control 62396193…、pg_close 00b58fe7…、pg_migration 85d27efd…。repository 929320BA…、005 26B71A83…与084冻结值相同，001—004未改；没有改正式docu、公共库、gateway主体、HTTP/runtime、PDF、配置或Git。

| 验证 | 真实命令/证据 | 结果 |
| --- | --- | --- |
| 初始纯单元 | backend/.venv/Scripts/python.exe -B backend/tests/fixtures/task083/run_audit_fix_02.py；unit-initial.log、unit-initial-meta.txt | exit 0，14/14，约0.89秒；属于修正解释器路径**之前**快照。 |
| 唯一修正复检 | backend/.venv/Scripts/python.exe -B backend/tests/fixtures/task083/run_audit_fix_02_recheck.py；unit-recheck.log、unit-recheck-meta.txt | exit 1，3项中2过；test_05_early_success_uses_tree_zero_close_then_same_g_settle_retry返回elapsed_violation_full_reservation而断言期望settled。原因未证实，最终快照**不能称通过**。约0.62秒。 |
| 最终静态 | backend/.venv/Scripts/python.exe -B - 执行一次限定AST/差异/hash脚本；static-final.log、incremental.diff | exit 0，13个改动/新增Python文件AST通过，冻结仓储/005匹配；局部无明文凭证或真实外发URL模式。它不验证行为、OS或PG。 |
| Job/PG/迁移 | 本轮未执行 | not_run；Job启动数0，PG连接数0，005未执行。 |

复检失败后没有再改源码或追加测试。初批14项只有不受最终命令argv改动的条目可作局部证据；05最终失败，不将旧PASS沿用为最终PASS。历史Job 5例及旧04缺证原样保留。没有真实出站或旧进程调查/操作。任务预算未按新脚本或中断重置。

后续最小门：先由原084独立增强窗口只读复核D1/D2/D4/D8最终控制链、D3权限提案和本次复检失败；不对未改仓储全量重审。D1/D3和05单元失败未关闭前不进入Job运行。若编排修复并另给预算，Job最小清单为01正常退款、02挂死全额预扣、03主退后代、04最后句柄/旧失败、05因统一控制器和身份入口变化需核验同名碰撞；每例按job_batch的精确对象与停止条件复审后才可执行，不承诺按当前脚本直接放行。PG定向ID为 PGMigrationTests.test_pg_migration_01_empty_table_adds_only_closed_column、test_pg_migration_02_nonempty_table_rolls_back_whole_005、PGCloseTests.test_pg01_close_settle_and_old_gc_does_not_touch_new_window、test_pg02_closed_gate_rejects_admit_mark_but_records_outcomes、test_pg03_close_commits_before_concurrent_admit_and_mark、test_pg04_cancel_closes_gate_and_old_dispatched_unknown_converges；专用DSN缺失skip，另卡授权运行/清理。文档建议由编排把083保持“部分/运行冻结”，登记D1/D3与本轮复检失败；本实现者不签安全通过。

---

## 历史：离线补足轮01原文


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
