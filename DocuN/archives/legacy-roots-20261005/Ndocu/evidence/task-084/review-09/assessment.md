# review-09 D3完整成果最终独立验收（TASK-084 / R-078）

只读终审。执行者 GLM-5.3（本新隔离 Session；083 完整收尾14 实现窗为 Codex/GPT-6，见 read-index.md 如实登记；本窗未参与任何 083 实现、运行或整理）。review-08 结论按未变方法/依赖复用；本轮不重审 review-08 已关闭项、未变产品与旧动态证据。动态额度 0：未运行任何脚本/测试/编译/AST 工具、未启动或查询 Docker/PG/Job/进程、未读容器 Env/完整 DSN/口令/stdin 内容；仅只读文件读取、有限 hash 计算（托管 Python hashlib）与原文比对。写入仅本目录与 TASK-084-result.md 置顶段。

阅读顺序按卡面：合同与已批准 D3 决定 → review-08 三份材料 → pre/incremental.diff/review08-current-hashes 与实际 runner/controller/fixture → 三个新增离线入口 → continuation 原始 state/meta/stdout/stderr/resource-commands → 根证据目录 → **最后** 才读 TASK-083-result.md 置顶14（待核声明）。独立结论在接触自评前已形成；自评与原始证据逐项核对后无修正。

## 0. 冻结与哈希链（详见本目录 hashes.txt）

- 卡面三变化文件 MATCH：runner 7137664E…、controlled_child 0494AF00…、d3_pg_windows 19B6F78C…；未变关键四项 MATCH（repository BCA82833…、session EB514B5F…、contracts A344AC5F…、006 F791F22D…）；其余 review-08 冻结/UNCHANGED 项全部 MATCH，零未知漂移。
- pre 链：pre 副本三项分别 = review-08 记录的 repair-11 最终版（26ECB423/14E20FCB/A1E419F3），证明增量 diff 基线真实。
- as-run 链：runner/controlled_child/contracts/fixture 四个 as-run 与当前文件逐字节相等，sidecar 一致；attempt-01/sources 43 文件快照 hash 与 final-hashes 一致，其中 repository/session/006/windows_job 与当前冻结值相等——运行时依赖即最终版。
- pre/TASK-083-result.md（54F559F1）与 review-08 记录（DB656509）的差异 = 12 轮 BLOCKED 置顶写入（review-08 读到置顶11 版），已登记历史演进，非漂移。
- 定稿后无漂移：当前 TASK-083-result.md = 2d246fc8… = evidence-hashes.txt:88 = delivery-check.result_sha256。

## 一、块A：三文件实际增量裁定

**1. runner.py（26ECB423→7137664E）**
- inspect 第14字段改为 `{{json (index .HostConfig "Mounts")}}`：index 对缺失 map 键返回零值→json 渲染 "null"→None，缺键安全；保持完整14字段、不含 Config.Env（离线断言模板14字段+index表达式+无Env，offline-01 实跑 ok）。configured_mounts 非空（bind 挂载）仍被 valid_identity 拒绝（离线行为验证+实际4次 inspect 使用）；顶层 Mounts 仍单独严格核唯一匿名卷。12 轮定界的 Docker 29.7.2 缺键失败由此关闭，且 preflight 为该模板首次真实实测（exit0，"null" 渲染）。
- parse_inspect 严格化：字段数恰14、running 字面值限 true/false、labels 必 dict、mounts 必 list[dict]、port_bindings 必 dict、binds/configured_mounts 只许 None/list——类型/解析异常一律 RuntimeError 失败关闭；valid_identity 新增端口键集合恰为 {"5432/tcp"}。离线 test_projection_fails_closed 以 9 类坏样本逐项验证（offline-01 实跑 ok）。
- 就绪与认证分离：pg_isready 返回 1/2 才在 min(总期限-60, now+30s) 内有界等待（deadline_left ≤0 即 TimeoutError 自然终止）；其他退出码立即失败；认证身份由 psql `SELECT current_user,current_database()` 独立核验、失败即停——"确定认证失败不绕过"成立（就绪 exit1 属歧义码，保守等待到期限后仍停，方向安全）。实际运行首检 exit0、身份核验/单次轮换/loopback 三重核验（user/db/容器内5432）全部成功，rotation_count=1。
- 资源命令审计：docker() 每命令记录 argv/UTC起止/timeout/exit/stdout/stderr 到 resource-commands.jsonl，stdin 一律 "omitted"（口令不入日志）；REDACTIONS 对 ALTER ROLE 后所有输出脱敏；口令仅内存与子进程 env（RETROLUME_TASK_083_D3_DATABASE_URL），不入 argv/meta/state——两份命令日志与 attempt 日志均无口令痕迹。
- 复验聚合修复：reusable_parts 要求 exit_code 恰为1、complete_count==0、completed/starts 为期望序列前缀、contract.errors ⊆ 允许集、分部场景 ⊆ completed——不把首批非零/缺 complete 倒写 PASS；attempt-02 要求 `set(parts)|set(reused)==set(SCENARIOS)`（运算优先级核实：`|` 高于 `!=`，语义正确），漏未运行后继即 RuntimeError。**有限缺口（分层记录，非阻断）**：source_fingerprints 依赖集 = backend/app/**.py + backend/migrations/*.sql，不含 backend/tests/**——windows_case 以 spawn 方式使用的 fixture.py 不参与指纹；若未来走 attempt-02 且 windows 分部被复用而 fixture.py 已变，指纹不会失效。本轮未走复验通道（静态/离线结论限定，按卡不强制新建真实失败实验）；每 attempt 的 sources 快照逐字节记录 fixture.py，事后审计可查；未来若再授权复验通道，将该目录并入依赖一行即可关闭。
- windows_started 判定：队列检测 + raw_out 原文扫描 + contract.started 三通道聚合，场景事件排空后仍能正确禁止 Windows 后重试——准确。
- 其余：EVID 移至 d3-completion-14；as-run 快照改用 `Path(__file__).with_name(...)` 同目录定位（正确，不受 EVID 变更影响）；总限收紧 120..600（授权面收窄，合规）；state 增加 start/end_utc、authorized、resource_wall_seconds 等时间事实。

**2. controlled_child.py（14E20FCB→0494AF00）**
纯观察增量：`events` 列表 + `record()` 在 suspended_identity（pid+created_100ns）、assigned_outer_job（active=1）、resumed、control_handles_closed（记录当下 cleanup_confirmed 真值，失败路径记 false）四处留痕。`import time` 原已存在；已审安全顺序（CreateJobObjectW→SetInfo→CreateProcessW(SUSPENDED)→GetProcessTimes→Assign→active()==1→Resume）逐行核对未变；句柄/最后 Job 语义未弱化；不持业务 Job 句柄。异常管道/EOF/exit：run_batch finally 在 close 前读 exit_code、join readers、存活即 OwnershipUnknown；原始错误保留为 cleanup_error。**微小观察（非阻断）**：finally 内多个子块连续失败时 cleanup_error 后赋值覆盖前者消息——失败事实与 pass=False 均保留，仅首错消息细节可能丢失。

**3. d3_pg_windows.py（A1E419F3→19B6F78C）**
emit 为每条记录加 event_utc/event_monotonic（证据增强，不改断言）；ledger_new_g 增加声明字段——`old_retry_branches` 三项与 fixture:182-190 实际触达的三个不匹配拒绝一一对应、`recent_settled_gc_idempotency_exercised:false` 如实登记未触达；windows_recovery 增加 `handles_closed`（仅 close() 成功后置位）与**更强**断言（active_processes_at_end==0 且无 cleanup 错误）。无任何断言削弱；场景逻辑与 review-08 已审版本（A1E419F3）一致。

**4. 授权范围**：三文件均为 14 卡授权对象（runner/辅助测试控制/task083 fixtures）；产品 repository/session/windows_job/001—006 零改动（hash 独立核）；git status pre/post 逐字节相同（tracked 零变化，三改动文件均在未跟踪目录）；未虚构生产变化——全部增量属实测试/控制/证据侧。

## 二、块B：八场景真实链（按原始 stdout 逐项）

| 精确ID | 原始证据（stdout.log 行号） | 裁定 |
| --- | --- | --- |
| migration_empty | 行3：added=["running_owner_session_id"]、valid=[0,4294967295]、invalid=[-1,4294967296]；代码断言 NULL 默认、CHECK 拒绝、旧值保留 | **证明**：006 仅增列、域校验真实拒绝（fixture:96-119 硬断言，记录存在即断言成立） |
| migration_old | 行6：row=["running",6,null] | **证明**：旧 running/R6 行 NULL 保留无回填 |
| migration_rollback | 行9：column_count=0 | **证明**：注入位置（事务内无效约束）的完整回滚、无部分006 DDL；合成故障位置明确，不外推所有迁移故障 |
| ledger_active_lease_rejected | 行12：row 不变（G1/R6/S0/SID0）；另 fixture:153-156 五类非法 SID 值域拒绝 | **证明**：有效租约不抢占 |
| ledger_new_g | 行14：old(G1/R6/S0)→new(G2/R6/S6/SID0/dispatch_closed=false)；upper_pending_claim SID=4294967295 | **证明**：同SID0 全额旧R入S、新G/关门、DWORD 上界独立持久；三次旧G/C 为**三种不匹配拒绝**（fixture:182-190 实际执行+行不变断言），非 ALREADY_SETTLED 重测——声明如实；最近已结算幂等按旧证据范围（review-08/PG08）复用，不因未重测自动新门 |
| ledger_exhausted | 行17：after=(pending,2,0,6,null,true)；fixture:210 断言 claim 返回 None | **证明**：折叠已提交、None、关门/清身份 |
| ledger_lock_barrier | 行20：claim_wait_at 09:55:09.815874 < deadline 09:55:11.084425；inspect_wait_at 09:55:11.524253 < expiry 09:55:12.832620；claim_before==claim_after；snapshot_recoverable=true | **证明**：pg_stat_activity 真实来源锁等待先于边界（application_name+wait_event_type='Lock'+material_sources 查询特征），持锁越界后释放→claim 拒绝且行不变、inspect 恢复。辨别力成立：事务起点口径会使 claim "穿越"deadline 成功并触发 `claim crossed deadline` 断言失败，实际为 Conflict 拒绝——锁后 UTC 口径得真实证明。非单纯 sleep 屏障 |
| windows_recovery | 行23：old(G1/SID1/PID17752/created…31727313/树0/handles_closed/open_error_code=2)→pre(running/G1/R6/S0/SID1)→new_outcome(settled/G2/PID37356/manager 32896/active_processes_at_end=0/cleanup干净)→final(pending/G3/R0/S7/SID null/last_settled G2,1) | **证明**：确切旧Job+PID+创建时间、树0/close/Open2（ERROR_FILE_NOT_FOUND）→生产固定 run_supervised_window 以自身 SID1 认领 G2 真实结算→PG 最终账目与卡面逐项一致；增强断言（树0/无cleanup错误）实跑通过。观察句柄不保活业务Job（ControlledChild 不持业务 Job 句柄；fixture 在 Open2 前已 close 旧Job 三类句柄） |

逐个记录"确实证明/未证明"：已证明如上；未证明（如实分层，均已在自评与本文不当作已证）：全部崩溃分支（Assign 前孤儿、权限拒绝、Open 未知、句柄失败）、真实 second-attempt、认证失败收尾、stop 失败 kill 分支、最近已结算 G/C 幂等动态、跨机/注销/重启/全部响应丢失/退款异常。八场景完整成功不扩大到上述范围。

## 三、块C：进程与资源证据

- 外层夹具主进程 PID4936/创建 134349765079104187；控制事件序（meta.control_events）：suspended_identity→assigned_outer_job(active=1)→resumed→control_handles_closed(tree_zero_confirmed=true)，与卡面要求逐字对应。exit_code=0、readers 双流 EOF（stdout 24行完整 JSON、stderr 空）、outer_tree_zero=true、handles_closed=true（cleanup_error null 且 job/hProcess/hThread 三句柄均无）。实际 exit0/管道EOF/树0/句柄完成共同支持该链。
- 旧worker 17752（created …31727313）、SUP 32896（created …35467746）、新worker 37356（created …40558339）均以 PID+创建时间+Job 名归属，无裸 PID 认定。互斥释放顺序按未变源码（session.py EB514B5F）与旧单元事件证据解释，未伪造本轮动态 mutex 事件。Assign 前猝死悬停孤儿为已知停止边界，本轮成功链未消除亦未掩盖（自评如实声明）。
- 容器 CID 85242648…（完整）：4 次完整身份核（pre/start后/stop前/stop后）逐项一致（name/三标签/固定镜像/唯一匿名卷→/var/lib/postgresql/data/1CPU/512MiB/pids128/restart=no/bridge/127.0.0.1:55439/binds null/configured_mounts null）。资源命令账（两份 jsonl 合计12条）：仅 start 1/轮换 1/stop 1，无 run/rm/第三容器/旧secret读取/Env读取/提权。末次 stop exit0、stop_post Running=false 且身份再核——支持记录时点停止，接受已有收尾，不要求重启或实时 inspect。

## 四、块D：版本、期限与纪律

- 执行字节链：当批实际执行字节（as-run 四文件+sources 43 依赖快照）= 最终 hash = 真实 sources 链，三链独立闭合（本目录 hashes.txt）。三批旧离线 review-08 分级保留未倒签；本轮 10 项新离线（offline-01：CompletionChecks 3 + ControllerTests 7，Ran 10 tests / OK / exit0 / 1.938s）独立计数不混算历史覆盖——其中 ControllerTests 7 项在最终版 runner（7137664E）上重跑，正好关闭 review-08 对三项"绑定中间版"的分级缺口；测试摘要在 stderr.log（stdout 为空），与既往"unittest 摘要写 stderr"经验一致。
- 真实唯一批：8 唯一 start/result、complete_count=1、all_pass=true、parts=[migration,ledger,windows] 完整、exit0+cleanup 共同成立（contract.started==completed==expected==8 项，errors=[]）。**字段名核准**：scenario-index.json 每场景 "exit" 字段系 finalize_evidence.py 从 meta 批级 exit_code 投影（生成代码核实），原始 stdout 无逐场景独立 exit——逐场景证明 = 记录存在 + contract 校验，不得把投影字段当独立证据；索引其余字段（start_utc/result_utc/seconds/fixture_sha256/outer_tree_zero/handles_closed）均直接源自原始记录，无 null 误读。
- 时间账：preflight 5.609s + 外层 runner 进程 10.133438s = 15.742438s；内部 9.390s 已含不重复计；原保守 900+240 为占账声明（非实耗）；总 1155.742438/1800、余 644.257562s。场景最大 3.515s（lock_barrier）、批 6.844s，均 ≤30s/≤60s 期限，无超限。批次 2/3（历史1+本轮1）、PG 夹具命令 2、Windows 1/12、容器 2（本轮新增0）、start/轮换/stop 各1、无第二批——与 budget-final.json 及卡面逐项一致。发现无非实质文案误差需单列影响。
- 在途核查三快照空；git status pre/post 同 hash（tracked 零变化）；公共规则只读（read-index 登记 mtime+SHA）；GBK 整理失败确认为 diff 生成阶段、13 hash 与并发核查先于其完成、UTF-8 重生成未覆盖任何运行记录——有限核查接受，不影响真实证据字节。
- delivery-check.json 各声明独立复核：tracked_diff_unchanged（pre=post 同 hash）、result_sha256（当前一致）、as_run_dependency_files_unchanged 43（final-hashes 核对）、credential_url_pattern_absent（两份命令日志+attempt 日志+state 无口令痕迹）、real_resources_reexecuted=false（与动态0一致）。其生成命令未保存为脚本——辅助整理声明而非运行证据，非阻断。

## 五、块E：最终判定

1. **实际增量代码：通过。** 三文件增量全部在 14 卡普通完整修复授权内；inspect 修复保持旧控制合同（14字段/严格类型/非空拒绝/不读Env）；就绪等待有界且认证失败关闭；控制器事件纯观察；复验聚合不倒写 PASS 且防漏后继（唯一分层缺口为指纹依赖不含 backend/tests/**，见块A，未触发通道）；产品零改/迁移未改/边界未扩。
2. **八场景动态：通过。** 八项均有真实 PG/Windows 证据与有辨别力的断言；lock_barrier 提供锁后 UTC 口径的真实因果证明；windows_recovery 走生产固定 launcher/SUP 路径真实认领结算；边界声明如实。
3. **资源/执行控制：通过。** 精确身份四次核、最小资源消耗、唯一 start/轮换/stop、精确 CID 收尾且 Running=false 复核、卷/schema 保留、口令全程内存+env+脱敏、预算账自洽。
4. **批准的 D3 切片整体：达到实现/验证交付条件，可由编排验收关闭 TASK-083 的 D3 部分成果（14 轮）。**

适用边界（不据此关闭、不自动扩成新门）：单机/单交互会话部署前提（numeric SID 不证跨主机/boot 唯一性，跨机/迁库在自动恢复契约之外）；单一成功恢复路径不覆盖全部崩溃分支（Assign 前悬停孤儿、权限拒绝、Open 未知、真实 second-attempt、认证失败收尾、stop 失败 kill 分支均未触发）；最近已结算 G/C 幂等未新增实跑（按旧证据范围复用）；006 仍唯一新增列、旧行 NULL 不回填；不签 M-1/STEP008/one_call/整个项目完成。

**最少必要后续**：无阻断性补项。供编排的文档建议（不代改正式状态）：① 执行状态登记"D3 批准切片实现与真实验证 8/8 通过，review-09 独立验收通过，资源停止保留"；② CHANGE.MD 登记本结果与 read-index/d3-completion-14 证据目录；③ 若未来重新授权 attempt-02 复验通道，先把 backend/tests 依赖（至少 fixture.py）并入 source_fingerprints 一行再启用。

## 非阻断观察汇总（分层记录，均不构成验收阻断）

1. 复用指纹依赖集不含 backend/tests/**（fixture.py 为 windows_case 的 spawn 依赖）——仅影响从未触发的 attempt-02 windows 复用路径；sources 快照逐字节留痕可事后核查。
2. run_batch finally 多子块连续失败时 cleanup_error 消息后者覆盖前者——失败事实与判定保留。
3. scenario-index 每场景 "exit" 为批级投影字段，非独立逐场景 exit 证据。
4. delivery-check.json 生成命令未保存为脚本（声明已独立复核为真）。
5. pg_isready exit1（歧义码）在有界期限内重试而非立即硬停——保守方向（期限到即 TimeoutError 失败关闭），实际认证门由 psql 身份核验独立承担，未发生"确定认证失败被绕过"。

## 边界重申

本轮只读，动态 0；写入仅 Ndocu/evidence/task-084/review-09/（hashes.txt、assessment.md）与 Ndocu/results/TASK-084-result.md 置顶 review-09 段；全部历史保留。独立结论形成于读取 083 自评之前，阅读顺序与接触时点如实披露。不替编排改正式状态；不宣布 M-1/STEP008/one_call/项目完成。
