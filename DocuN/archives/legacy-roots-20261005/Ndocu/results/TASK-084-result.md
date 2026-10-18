# TASK-084 / R-078 — review-09 D3完整成果最终独立验收：通过，可由编排验收关闭（2026-09-27，当前有效）

**结论：083 完整收尾14 的实际三文件增量、八场景真实动态证据、资源/执行控制全部通过独立验收——批准的单机 D3 切片已达到实现/验证交付条件，可由编排验收关闭；无阻断性补项。** 冻结链独立闭合：三变化文件（runner 7137664E…、controlled_child 0494AF00…、fixture 19B6F78C…）与卡面一致，pre 副本=review-08 基线（26ECB423/14E20FCB/A1E419F3），as-run 四文件与当前逐字节相等，repository/session/contracts/006 等未变项全部 MATCH 零漂移，定稿后结果文件无再变。inspect 修复（`{{json (index .HostConfig "Mounts")}}` 缺键安全+parse_inspect 严格类型失败关闭+端口键集合校验）关闭 12 轮 Docker 29.7.2 根因，经离线行为验证（9类坏样本）+preflight 首次真实实测+主运行4次使用；就绪/认证分离有界、失败关闭；控制器事件纯观察不弱化已审顺序与句柄语义；复验聚合不倒写 PASS 且防漏后继。八场景原始 stdout 逐项核实：migration 三例（仅增列/旧NULL保留/回滚无部分DDL）、ledger 四例（有效租约拒绝/同SID0全额折叠+DWORD上界/耗尽None关门/真实pg_stat_activity锁屏障先于边界、释放后拒绝且行不变、锁后UTC口径得证）、windows_recovery（旧Job PID17752树0/Open2→生产SUP32896自读SID认领G2真实结算→worker37356→PG最终G3/R0/S7/SID NULL）。进程树（外层4936四事件链、exit0/EOF/树0/句柄完成）与容器（完整CID四次身份核、start1/轮换1/stop1、stop exit0+Running=false复核、无Env/旧secret读取、口令仅内存+env+脱敏）均支持。预算账自洽：5.609+10.133438=15.742438s，总1155.742438/1800，批2/3、PG命令2、Windows 1/12、容器2（本轮0新增）；本轮10项新离线（exit0）独立计数，ControllerTests 7 项绑定最终版重跑关闭 review-08 中间版分级缺口。**适用边界**：单机/单交互会话前提；单一成功恢复路径不覆盖全部崩溃分支（Assign前孤儿、权限拒绝、Open未知、second-attempt、认证失败收尾、stop失败kill分支未触发）；最近已结算G/C幂等未新增实跑按旧证据范围复用；不签 M-1/STEP008/one_call/项目完成。非阻断分层记录：①复用指纹依赖集不含 backend/tests/**（fixture.py），仅影响从未触发的 attempt-02 windows 复用路径，sources 快照可事后核查；②scenario-index 每场景"exit"为批级投影；③run_batch finally 连续失败时 cleanup_error 消息覆盖（事实保留）；④delivery-check 生成命令未存脚本（声明已独立复核）；⑤pg_isready exit1 有界重试属保守方向。执行者 GLM-5.3（新隔离 Session，未参与 083 实现/运行；14 实现窗为 Codex/GPT-6 如实登记）；独立结论形成于读 083 自评之前，阅读顺序按卡面（原始证据先、置顶14 最后），接触时点如实披露。本轮只读动态 0，写入仅 `Ndocu/evidence/task-084/review-09/`（hashes.txt、assessment.md）与本置顶段。文档建议供编排：执行状态登记 D3 切片"实现与真实验证 8/8 通过、review-09 独立验收通过、资源停止保留"；CHANGE.MD 登记；未来若再授权 attempt-02 复验通道，先把 backend/tests 依赖并入指纹再启用。证据：`Ndocu/evidence/task-084/review-09/`（完整五块裁定见 assessment.md）。

---

# TASK-084 / R-078 — review-08 修复11独立增量复核与真实运行门裁定（2026-09-26）

**结论：P1/P2/F1/F2/F3/R1/R2/R3 八项全部关闭，无确定阻断，无新增修正需求；完整剩余PG/Windows链的静态运行条件具备——可在编排授权的精确资源和预算内进入受控真实验证。** 冻结八项+UNCHANGED五项 SHA-256 现场计算全部 MATCH，零漂移。离线三批16/5/2、exit0、合计4.3922103秒核实无误，且按批次 compile hash 完成修正时点定分：对八文件最终版实际运行的测试仅批03 两项+AST结构核对；批01 12项（Guards 8+Clock 2+Protocol 2）与批02 两项因依赖面均为最终/未变文件而直接有效；pre_resume_failures、deadline_and_query_unknown、unknown_cleanup 三项行为测试绑定中间版（受测主体 ControlledChild 为最终版字节、retry_allowed 最终版已静态审读），如实分级不冒充。083 置顶未把 23 求和冒充独立用例（实为19个独立方法）——核对属实。ledger_lock_barrier 屏障经静态论证具有真实辨别力（事务起点口径会"穿越"deadline 导致断言失败，锁后采样正确拒绝），0.9s 固定观察窗存在失败方向安全的 FLAKY 风险，若实跑超时失败走 attempt-02.go 通道即可。猝死窗口定性：Assign 前毫秒窗口残留挂起孤儿（不会执行SUP成立、清理完整不成立，最窄处置=按PID手动终止，可管理边界非阻断），Assign 起 KILL_ON_JOB_CLOSE 内核收尾；walkthrough 已如实声明。资源复用路径静态核通过：14字段投影排除Config.Env、全量身份/卷/端口/限制校验、local trust 既有事实+stdin自改密+loopback三重核验、失败同CID收尾；本地认证/改密可用性未证，只能未来一次有界试验。启用入口 `backend/.venv/Scripts/python.exe -B Ndocu/evidence/task-083/d3-repair-11/runner.py --authorized-reuse --total-seconds <120..1200>`，前置=编排授权+容器停止且身份匹配+无其他083容器+55439空闲；场景9个ID，attempt-2需同runner存活期间放置attempt-02.go；停止规则=windows_started/cleanup不明/树未零即FAILED_STOP；剩余2批/2PG/12Windows账面、30分钟不重置。剩余待真实证据：006完整迁移/折叠/锁屏障、windows_recovery恢复链、ControlledChild真实进程行为与嵌套Job、认证可用性。PG/Windows实际通过仍待真实证据，不以其未跑否决准备成果。实际身份GLM-5.3-Flash（新隔离Session，未参与083实现；review-07同窗结论按未变方法/依赖复用）。本轮只读，动态0，未启动任何容器/PG/Job/进程，未读Env/DSN/口令；写入仅`Ndocu/evidence/task-084/review-08/`（code-prelog-assessment.md、postlog-assessment.md、hashes.txt）与本置顶段。不签D3动态验收、M-1/STEP008、产品one_call或安全最终通过。证据：`Ndocu/evidence/task-084/review-08/`。

---

# TASK-084 / R-078 / STEP008 — review-07 D3候选与完整验证链独立审计（2026-09-25）

**结论：D3核心的同机同会话旧G全额保守折叠，在批准的受信部署前提下具备静态实现骨架；当前仍有两项产品确定缺陷、PG夹具一项必然失败的错误，以及runner运行控制和证据协议缺口。代码层不通过，PG与Windows运行门均未打开。** 006空表执行及负SID CHECK拒绝仅有局部真实证据；真实claim、完整迁移、旧G Windows恢复均未到达。两容器额度已用且仅有记录时点的停止证据，本审计未启动资源或批准重启、轮换凭据、第三容器。旧Job07、PG08、09、084 review-06按未变方法/依赖及各自证据范围复用；不签M-1/STEP008或产品接线完成。

## 身份、顺序、快照

当前为原084独立审计上下文；实际客户端Codex desktop，本轮可见模型标识GPT-6（无更细后缀可核），未参与083代码/测试/runner编写或运行，不接管实施编排。根及公共AGENTS沿同窗已读未变复用。先读082批准的D3决定、当前TASK-083合同/停止前缀及自己review-06三条件；再审006/repository/session/windows_job、launcher/supervisor出口和真实pre副本，保存`product-prelog-assessment.md`；之后审四项测试、runner各as-run版与差异，保存`fixture-runner-prelog-assessment.md`；最后才看原始offline/PG/资源日志、fix记录和083结果置顶两段（待评陈述）。未读实现聊天、容器Env、真实配置、任何口令或完整DSN；未作新网页查询，review-06官方Windows语义按原限定复用。

九个指定冻结文件本轮SHA-256全部MATCH，逐项见`review-07/hashes.txt`。直接出口`activities/__init__.py`、`worker/launcher.py`、`worker/supervisor_main.py`与本轮pre副本哈希相同。首runner as-run `6B796C00…`、首修正`E21B41B6…`、替补as-run `56E698A7…`、当前候选`39E5917E…`分开归属；替补夹具as-run `7C650F78…`，当前`5F256503…`只改异常类第111行。083包内未找到卡面泛称的`incremental.diff`，故从真实pre和当前产品生成`review-07/product-pre-current.diff`。两次宽泛读取请求被自动审批审查拒绝，理由是可能输出密码/DSN；之后仅用非凭据源码行、选取JSON字段及排除凭据行的日志完成审查，没有绕读秘密。本轮仅文本/hash/只读diff；未import、AST、compile、单元、Job、spawn、PG、Docker、网络、安装、模型或诊断脚本，动态额度0。

## 产品逐项结论

| 条款 | 当前静态判断 | 限制 |
| --- | --- | --- |
| 006与身份域 | **代码通过**。`006_activities_running_owner_session.sql:1-8`仅增BIGINT NULL默认列、CHECK 0..4294967295、BEGIN/COMMIT；`repository.py:356-364`精确int拒bool/负/溢出，0有效；旧行不回填。 | 完整回滚、上界/超界、旧行NULL真实PG未验。 |
| claim、折叠与清理 | **主体静态成立，时钟缺陷阻断整体**。`repository.py:366-435`保留来源→活动锁，旧running G/SID在同事务重检；R→S全额，耗尽时提交pending/关门/清SID后返回None；新G/R/SID同UPDATE；`settle:558-586`最近G/C先判、成功清SID，`cancel:598-622`全额折叠并清SID。旧record/admit语义未改。 | `:369-413`截止时钟失真，见P1；新SID原子写尚无真实PG证据。 |
| 可信恢复入口 | **有条件成立，报告缺陷阻断**。`session.py:142,170-219`SUP自身读SessionId；running必须显式配置单机单交互会话、旧SID非NULL且相同、来源有效、租约/截止可接续；在ActivityMutex内Open精确旧G，只有JobOpenError.code=2可作为对象不存在候选；存在则terminate→ActiveProcesses0→close，随后claim CAS。`windows_job.py:162-168,260-267`保留Windows错误码，5/87拒绝；claim响应丢失不spawn/重认领，互斥至DB返回和收尾后才释放。 | 布尔开关是受信部署声明，不自证同主机；多主机共享库/迁库/异会话须由部署约束禁用。旧Job未证收尾可报clean，见P2。 |
| 并发与迟到 | **受限模型内静态可守**。同机同会话所有SUP守同一Local互斥时，活旧SUP挡新SUP；旧SUP死后无迟到Resume主体，旧Job的KILL_ON_JOB_CLOSE/无breakaway沿review-06官方语义。claim重验G/SID/租约，取消/来源变化在事务中重新拒绝。 | inspect快照至claim可变；中间取消或来源变更可先停旧树后由claim冲突，属保守停止而非退款。非守互斥的低层调用、多主机不在批准生产模型。 |

**P1｜事务起点时钟可在活动截止后授予新窗，确定产品缺陷。** `repository.py:139-164`事务在来源锁前启动，`:250-268`可等待来源锁；`:369-413`以PG`CURRENT_TIMESTAMP`为now，它固定于事务开始；`inspect_window:441-460`同样。最短交错：deadline剩不到2秒时启动claim，另一事务持来源锁至deadline后，当前claim获锁；`:380`仍以锁前时间判未过期，`:413-433`可写入已到期lease并提交running/G+1/R/SID，SUP管理期限内仍可建Job/Resume。2秒锁超时足以出现此交错。旧租约在锁等待期间的判定则偏保守，不能据此断言提前抢占；主要风险是过期活动获新窗。**最小修复**：恢复原claim在完成锁后采主机UTC墙钟的口径，并让inspect在锁后同口径判租约/截止；若选PG`clock_timestamp()`，须明确时钟契约变化并以锁屏障PG证据证明。不能把`CURRENT_TIMESTAMP`挪到同事务另一SQL假装修复，也不承诺任意内核阻塞下绝对硬实时。

**P2｜旧Job失败出口会把未知树/句柄报作清理完整，确定产品缺陷。** `session.py:190-208`旧Job terminate/等待false/查询异常或close失败只设old_failure并抛；`:301-304,331-344`因created_job=False且cleanup_errors通常空，可返回`failed_closed, cleanup_incomplete=False`。最短触发是同号旧Job打开后wait_empty_until返回False、close成功：最后句柄是否由他者持有未知，树零未证，却显示clean。Open5/87或SID不符等旧running在claim前拒绝还可能输出账目`(0,0,0)`，而快照R>0。未见误退款或新spawn，但外层若凭结果续批会误判。**最小修复**：跟踪旧树/句柄未确认，旧Job停止/查询/close失败或存在性无法确认时`cleanup_incomplete=True`；running旧账在无已确认新claim/折叠结果时用`None`表达未知，或严格定义并要求消费者识别“仅本次新窗”的字段语义。有效租约有意拒接旧树可另列状态，不能当全活动已清理。补定向纯替身断言，不改账本事务。

## 夹具与runner完整路径

| 项 | 最短触发、影响、最小修复 |
| --- | --- |
| F1 确定阻断 `d3_pg_windows.py:150,164-170` | 旧G SID=0，合法接续却传4294967295和expected_previous_generation；`repository.py:374-379`必因SID不同拒绝。合法接续改0；上界在另一pending活动初领并查持久值。 |
| F2 已修未验 `d3_pg_windows.py:108-115` | as-run误捕获`psycopg.CheckViolation`导致AttributeError；当前改`psycopg.errors.CheckViolation`，未运行。 |
| F3 已修未验 `runner_replacement.py:219-228` | 替补as-run遗漏合法`migration,ledger,windows`白名单；当前已补，未运行。 |
| R1 Windows控制阻断 `runner_replacement.py:116-154,264-280` | Popen先运行后取PID创建时间；读取失败时子进程已可建SUP/Job，finally仅杀父句柄。超时taskkill返回码只记录，未取确切SUP/Job树零；active_proc置None后不再收尾，Windows失败仍可cleanup_incomplete=False。runner死亡无独立收尾。需悬停创建、精确归属与独立deadline、控制建成后Resume、失败整树正证；无证则unknown停批。观察句柄不得保活被测最后句柄。 |
| R2 证据协议阻断 `runner_replacement.py:136-154,239-303` | ok只查子进程exit0、stderr空、任意complete相位，不核所选各场景与all_pass/parts；顶层吞BaseException后仍进程exit0。必须核逐项唯一完整结果及clean，任何失败非零退出，保留原始证据。 |
| R3 期限/断言 `runner_replacement.py:52-55,109-128,204-228` | `max(1,left()-reserve)`允许deadline/预留耗尽后再启动一步；Popen与taskkill+二次communicate未共用≤60s；Windows场景只结束后assert≤30s。按绝对截止控制每步/每场景、预留收尾。继承父环境未排除PYTHONOPTIMIZE，大量assert可被优化关闭；固定优化关闭并核子进程标志或显式raise。实际环境未知，不能说本次触发。 |

夹具已有的正确结构：`d3_pg_windows.py:43-52`每子例随机schema，按001—005/006顺序；`:64-90`限定search_path传仓储、行查询、expire；`:93-140`意图覆盖空表/旧running NULL、0/上界、负/超界和失败事务回滚；`:143-193`意图覆盖有效租约、新G、全额折叠、耗尽；`:196-241`真实建旧Job、取PID和创建时间/树零、close后Open错误2，再走固定run_supervised_window到新G/真实PG结算。此为生产路径合成前提，未替换被证明的恢复函数。`windows_case:240`写死的mutex_release文本不是真实互斥释放观察；顺序现由源码和纯单元事件支持，未来Windows单场景不得凭该字段声称实测。失败/成功schema都保留，无DROP。替补资源核准CID/标签/镜像/限制/loopback端口/镜像声明匿名卷与CreatedAt；所存selected inspect不含Env。资源检查通过不抵消R1—R3。

## 原始事实与预算

| 事件 | 已证 | 不可推出 |
| --- | --- | --- |
| 首资源1086a37d… | 首as-run以`mounts==[]`误拒镜像自动匿名卷；runner verdict BLOCKED、7.859s、PG/Windows测试0、原状态cleanup_incomplete=true；事后`cleanup-after-identity-check.txt`同ID/标签stop exit0、Running=false。 | 不倒改原先未知，也不是迁移测试。 |
| 替补85242648… attempt-01 | meta：PG测试PID31624/创建时间134348108976985801、exit1、0.891s，phases仅schema；stdout仅empty schema；stderr先是负SID的PG CheckViolation，再是错误捕获AttributeError。 | 只证明006空表执行与-1拒绝；0/上界/超界、旧行/回滚、claim/Windows均未运行。 |
| 替补go与收尾 | go为`migration,ledger,windows`；runner-log在第2 Popen前报invalid correction selection；attempt总数1，Windows启动0。最终所选身份/资源字段匹配CID、镜像、标签、loopback55439、唯一匿名卷；stop exit0、Running=false、cleanup_incomplete=false，81.765s。 | runner退出0不是测试PASS；停止仅日志时点，本窗未查Docker；当前未运行修正不能倒签历史。 |

累计离线3批；真实PG测试进程/批1、Windows0。原上限3批/3PG/12Windows账面余**2批/2PG/12Windows**，但容器已达2上限，不能自动继续。总时至少**7.859s+首次事后收尾耗时（无完整可合并数字）+81.765s**，原30min总限不重置。离线最终D3六项、受影响旧Protocol两项和offline05 PASS；offline05诊断绑定session `DFD342…`/fixture `BB301…`、Δ400ms/C1/W6，仅证明替身。Job07 create/碰撞/最后句柄、PG08 005/关门/最近G-C原语义、09固定launcher四场景沿未变方法和原始证据复用；新增SID、时钟、恢复分支的动态证明不在那些PASS中。

## 唯一下一路径与最小验证矩阵（供编排另卡，不构成本轮授权）

1. **先一次合并离线修正**P1/P2、F1、R1/R2/R3；保留已正确但未运行的F2/F3，冻结新hash与有限diff。P1回到锁后原UTC口径最窄；P2明确旧树unknown与账目None。纯单元只补旧Job终止false/查询失败/close失败/异号和Open5结果字段，以及同号/0/上界判别；现有D3六项中仅方法受改者定向复核，未变的open错误码、offline05和旧门控断言不机械重跑。纯单元不充PG锁/Windows证据。修后原084只审实际增量。
2. **资源先裁决，当前无续跑许可。** 最窄优选是编排另行明确授权评估已停替补的**同一完整CID 85242648b70dc11839a93de29a51bc7e492390d8ad479036c141f37b26f4f6a7**：重核完整CID/标签/固定镜像/唯一匿名卷、loopback55439可用和无其它工作；按确切对象启动后，只尝试批准的容器内本地认证路径，以当前测试角色/库身份连接；同一连续runner内存生成新随机凭据，经标准输入轮换测试角色口令，随后从loopback以新凭据核库/用户/容器内5432。旧secret全程不读Env/日志/argv，不关认证、不开放端口、不删旧库/schema。**现有证据未证明该容器本地socket认证或轮换权限可用**；认证不通即停并按精确CID收尾，不改用旧secret。runner成功轮换后必须持续持有新凭据到剩余批结束，子进程仅得专用环境变量；异常时精确CID/标签停止并复核，失败保留卷/schema。此评估、重启、轮换本卡一概未执行，须编排另给具体批准及期限。
3. 若本地认证路径经批准后仍不可用，当前证据下**不能在不读旧secret的约束内证明安全复用**。唯一资源备选是编排申请**额外第3个全新合成容器的明确例外**：新增1容器与新随机凭据，旧两容器仍停止，原批/PG/Windows次数和30min总账不归零；未获批准不得创建。旧容器Env不得成为默认凭据来源。
4. 资源可用且runner控制经独立增量审查后，**一次**选择`migration,ledger,windows`按顺序跑完整剩余链：`migration_empty`（NULL/0/上界/负/超界）、`migration_old`、`migration_rollback`；`ledger_active_lease_rejected`、修正后`ledger_new_g`（同SID、旧R全折、新G/SID）、`ledger_exhausted`，并补一个真实来源行锁屏障跨deadline/旧租约边界及最近旧G/C不污染新SID的定向断言；最后`windows_recovery`一次真实旧Job销毁→Open2→固定SUP新G/PG结算。PG失败即failfast不进入Windows；Windows无精确树停止正证即cleanup unknown并停全部，不因还有额度重试。只有确切原因且归属/收尾全证，才可用剩余**1批**按parts定向复验。每场景≤30s、命令≤60s、批≤10min含60s收尾、累计原30min持续计时；单一runner用不可覆盖attempt目录、stdout/stderr/exit/逐项phase证据。
5. 真实证据到手后原084只对**实际修正差异和新增动态证据**增量复核；不全量重测Job01—05/PG08六例/09四场景。当前**产品代码不通过，PG夹具不具完整执行条件，Windows runner不具安全运行控制，动态恢复not_run**。编排可在执行状态记录分层结论和两容器/凭据停止门；本卡不改正式docu或用户库。

证据：`Ndocu/evidence/task-084/review-07/`的hashes、product-pre-current.diff、product-prelog-assessment、fixture-runner-prelog-assessment、postlog-assessment。完整review-06及更早历史原文保留如下。

---

## 历史：TASK-084 review-06 及更早结果原文

# TASK-084 / R-078 / STEP008 — review-06 09完整成果独立增量终审（当前有效）

**裁定：09 四场景（A/B/C1/C2）的真实验证代码路径、证据链、账目与偏差登记全部独立核实成立，最终代码未发现新确定缺陷；各场景确定PASS、只能局部证明、缺证之处已分层列明；D3"一列 running_owner_session_id + 同号全额保守折叠/异号失败关闭"方案核心论证成立，补入两项显式条件后可提交用户批准。** 原084独立增强审计窗口接续（review-06），实际身份 GLM-5.3-Flash，未参与083代码/测试实施，不接管实现或编排；沿原独立上下文，已验Job07/PG08/纯单元与review-05静态结论按未变范围复用，未重审全仓、未重跑任何实现脚本。

## 输入、冻结与独立性

接触顺序（review-06/prelog-assessment.md 披露）：TASK-083 09合同 → **先读原始源码独立判断**（launcher_control.py、launcher_scenario.py 全文 + launcher.py/supervisor_main.py/windows_job.py 直接依赖全文）→ 09证据（results.json、batch-meta、runner、runner-log、manifest、post-run-check、两轮p-evidence/p-stderr、batch-stdout）→ **后读待评声明**（083结果置顶段、084 review-03/05边界、d3-sources-and-decision.md、082批准段）→ hash独立复算（第1—3块初判在读实现者自述前成形）→ D3支柱官方页3页抽查（S3/S1/S4，决定性原文逐句核对；S2/S5未重开、如实标注）。未读实现聊天；未运行AST/import/compile/单元/Job/spawn/PG/Docker/安装/模型/私有配置；官方网页读取为唯一网络范围；实际运行额度0。

冻结复核（review-06/hashes.txt，托管Python hashlib只读12文件）：launcher_control.py=142a5699…09af5、launcher_scenario.py=17f1bc8a…2cc8d（均=卡面给定值）；launcher/supervisor_main/supervisor_ipc/windows_job/session/command/worker_main/gate 七文件=JOB07_REFERENCES 一致；repository/005 抽查=084首轮冻结值一致——**零漂移**。本证明仅覆盖"当前文件=09记录快照"，不将本轮pre/post相等外推为历史未改证明。其余19文件清单沿Job07/PG08/09真实快照复用，未知漂移停对应结论（本轮未发现漂移信号）。

## 1. 四场景覆盖裁定（完整审查第1块）

| 场景 | 裁定 | 真正证明什么 | 只能局部证明/缺证 |
| --- | --- | --- | --- |
| A 正常完整入口 | **确定PASS** | 真实 run_supervised_window→固定SUP→idle worker→真实PG 全链成立：命令/venv（batch-meta：backend/.venv python -B -m fixtures.task083.launcher_control，cwd=backend/tests）、PG 17.11（runner-log就绪行）、身份链（SUP PID 31612+created_100ns、Job名精确匹配job_name(activity,G1)、outcome.pid 28612=venv launcher与watcher在飞记录从PID 31580自动入Job双进程——与官方S3"子进程默认入Job"及windows_job无breakaway互证）、计时（timing_diagnostic t1>t0、observed=1、W=6、settled=1=elapsed 0.75s上取整）、关门（dispatch_closed=true）、结算账（S=1/R=0/pending=0、DB last_settled G1/G2）、收尾（active_end=0正查询、SUP与worker事后OpenProcess 87如实）。 | 仅覆盖idle worker立即完成的成功路径。"worker挂死→SUP到截止终止"未在launcher链复现——Job07场景02（同SUP代码、hash冻结）已验stopped_at_deadline，属局部延续的组合推论，非同链联合实证。 |
| B 父级管理截止 | **确定PASS（按卡面B验证目标）** | 注入不绕过真实链：trigger条件（DB status=running+精确命名业务Job在管）是SUP真实claim/spawn的产物；injected_wait仅把launcher主等待（真实wait调用、resume后）的返回时点确定性提前，wait(0)探测保持真实语义；其后launcher走**真实**管理截止路径（terminate SUP→close→None账目），manifest已披露"真实16s截止下SUP结构上必然先完成，非注入无法确定性命中"——符合卡面"确定性控制点注入"授权。账目结论（state=manager_timeout_unconfirmed、R/S/pending全None、cleanup_incomplete=true、SUP PID 13284有终止）与DB保守保留（running/G1/R=6/S=0/closed=false/租约在、零退款）独立成立。 | 不证明"SUP在真实16s超时下超时"（注入提前触发，同代码路径但时点不同）；不证明生产"SUP死亡且无其他句柄"情形的行为——SUP死时Job内2进程仍活是**控制者持最后句柄的观察者效应**，B既不证明也不证伪该情形下KILL_ON_JOB_CLOSE（由S3官方语义推论，未单独实测）。不能据B宣称生产KILL_ON_JOB_CLOSE失效或有效。 |
| C1 父死前（Resume前） | **确定PASS** | 屏障精确在resume调用边界（held_resume替换点=launcher.py:267真实ResumeThread前，记录SUP精确身份+映射名后挂起，go永不置位→无任何真实ResumeThread调用者）；"悬停SUP不迟到Resume/不迟到认领"的根因是**结构性保证**（CREATE_SUSPENDED+唯一resume入口被替身拦断），2秒负观察仅证明观测窗（结果文档"2秒有界负观察无变化"措辞如实，未上升永久命题）；DB恒pending/R=0/closed=false、G0/G1对象均不存在、P被杀即最后映射句柄关闭→映射销毁核验；控制者按精确PID+创建时间终止悬停SUP。 | 2秒观察窗本身不证明"永远不迟到"——但本场景不依赖它（结构保证足够）。C1的SUP悬停时未open映射（挂起主线程未执行任何代码），映射生命周期仅覆盖"创建者死亡后销毁"路径。 |
| C2 父死后（Resume后） | **确定PASS** | 双屏障（pre_resume在recorded_resume内、at_wait在barriered_wait主等待入口）+控制者等待的全部是真实可观察事实（DB running→Job open→active>0即worker已spawn，毫秒级间隙有界轮询）；P双进程（venv launcher 19252+真实python 15660）精确终止确认；SUP存活核验→25秒内自退出（self_exit=true、兜底终止未触发）→DB收敛（pending/G2/R0/S1/closed=true/last_settled G1）→Job对象与SUP映射open如实失败（销毁）→两worker PID复核消亡（created_matches=False即PID复用不计残留的口径正确）。控制者Job句柄close先于kill P（launcher_control.py:734-744行序核实），未保活污染SUP收尾。 | C2是**正常早退**路径：证明"父死后SUP独立完成正常窗口直到结算与对象销毁"；不凭短运行证明"到截止时SUP一定终止"——该分句由Job07-02局部延续（结果文档"独立完成自身截止"措辞应按此理解，本审查予以明确）。 |

2秒负观察与C2早退的卡面提醒核实结果：结果文档未把负观察写成永久命题、未以C2早退宣称截止终止（该限定由本审查补充明确）；C1"不迟到Resume"有结构性根因支撑，成立。

## 2. 观察者效应与停止权限（完整审查第2块）

控制者句柄逐项清单（取得/释放时点以源码行序核实）：

| 场景 | 控制者持有 | 取得→释放 | 物理停止归属 |
| --- | --- | --- | --- |
| A | watcher线程短暂持业务Job句柄；批进程主线程不持 | running后open_existing→记录→close（观察窗内，SUP收尾前早已释放） | 自然完成：worker退出→SUP结算退出→对象销毁；树空=active_end=0正查询+事后Open 87 |
| B | DeadlineTrigger持业务Job句柄 | 触发时open_existing→记录+terminate+wait_empty后close；异常路径_emergency_job_cleanup兜底不留活对象 | SUP由被测系统terminate（launcher finally）；Job树由**控制者**terminate+wait_empty=0（真实物理停止，控制者执行） |
| C1 | P双进程句柄+SUP句柄+2事件句柄 | 屏障后open→kill确认dead→close；SUP悬停核验后精确终止（pid+created匹配）；事件close于PProcess.close | 悬停SUP物理停止=控制者TerminateProcess；P=控制者精确树杀（先真实python后venv launcher） |
| C2 | P双进程句柄+Job句柄（观察）+SUP句柄 | mid_flight观察后**close先于kill P**；kill P确认；SUP句柄等25s自退出（兜底terminate备而未触发）；事后open核验销毁 | SUP自行完成（结算+杀树+关句柄→对象销毁）；控制者仅观察与事后核验 |

- 卡面"外层控制者必须能确切收束本次对象，否则停真实运行"：B/C1/C2全部满足，无"未执行就算已清理"。
- **B中"SUP死而worker仍活"确因控制者保持最后Job句柄**（open_existing时起对象归属移交控制者，launcher_control.py:316-318注释已如实声明）；受测行为被观察者改变的部分已被083结果以"控制者持精确句柄实测"限定，未宣称生产KILL_ON_JOB_CLOSE失效或有效——处理正确。
- **B结果独立成立保留**：state/None账目/cleanup_incomplete/DB R=6保守保留（不退款）不依赖"worker存活"解释；"SUP退出≠树空"的准确表述应为"存在其他句柄持有者时SUP退出≠树空"——生产唯一持有者情形由S3官方语义覆盖（推论），09未单独实测。全批不作废。
- 生产语义证据分层：09实测覆盖"主动close最后句柄→树灭对象销毁"（C2）与"控制者持句柄时SUP死亡→对象存活"（B）；"SUP死亡且无其他句柄→KILL_ON_JOB_CLOSE杀树"是S3官方语义的直接推论（句柄关闭原因不重要），未单独实测——D3折叠论证应建立在S3官方语义上（其文档已如此处理）。

## 3. 尝试与证据账（完整审查第3块）

| 卡面口径 | 实际 | 判定 |
| --- | --- | --- |
| 一个新专用PG容器 | 4容器（1652/1653/1655/1658），全部Exited(0)、stop保留、标签完整、未删除 | **执行合规偏差（已登记）**。结构性根因：随机口令仅注入当次docker run进程环境、不可恢复，前置缺陷轮修复后无法复用旧容器；1652/1653均0场景启动。处置权留编排。 |
| 真实批≤3 | 2真实批（1655首验/1658复验）+2前置拦截轮（0场景） | 合规 |
| 场景启动≤12 | 8（1655四场景+1658四场景） | 合规 |
| 每批≤10分钟（预留收尾60秒） | 批进程自身deadline=540s（BATCH_DEADLINE_NS），实际8.8s | 合规 |
| 每测试命令≤60秒 | runner级8.797s | 合规 |
| 准备/纯离线检查≤5分钟、≤3命令批 | 预检1次+静态3次（前2次为检查脚本自身缺陷） | 恰在上限内 |
| 累计真实运行与资源操作≤30分钟 | 约5分钟 | 合规 |

- **TOTAL_WINDOW=660是runner级总窗**（容器操作+批+收尾，含批前检查75s），不是批超时；不得将配置660自动等同实际超时（实际批11.5s、runner全程约1.5分钟）。1652首启的560s算术缺陷正是此口径混淆所致，修正后660与卡面各项一致。
- **首批1655批级日志被1658同名覆盖**（runner固定文件名缺陷）：A/B/C1通过状态与C2失败细节的原始批日志缺失，仅剩runTag维度p-evidence/p-stderr（四组，与最终批results.json交叉一致）+执行会话实时观察；manifest/post-run-check已如实登记、未补跑。**最终PASS由1658完整独立批次支撑，不依赖被覆盖日志**——功能证据不受损；1655信息残值仅剩尝试账层面。
- **复验全批重跑vs"核心失败只复验受影响场景"**：runner不支持场景参数，1658实际全批重跑A/B/C1/C2——方向保守（多验证非少验证），场景启动8/12仍在上限；已登记，不构成证据缺陷。
- **最后全部停容器的正证据强弱**：1658=强（runner-log含inspect-before-stop身份核对OK→stop exit=0→inspect-final Running=False全过程）；1652/1653/1655=中等（各轮runner日志同被覆盖，但post-run-check.json 17:05 docker ps -a标签过滤提供四容器Exited(0)事后快照核验+端口55438 FREE）——状态在案、过程日志部分缺失，如实分层。
- 功能证据与执行合规已区分；未以最终exit=0抹去偏差（四项偏差均逐条在案）；"无法恢复的日志明确缺失，禁止为补美观重跑"的纪律已遵守。

## 4. D3一列方案终审（完整审查第4块）

**官方抽查**（3页，≤6上限内；决定性原文与D3摘录逐句一致）：
- S3 job-objects页确认："The job is destroyed when its last handle has been closed and all associated processes have been terminated. However, if the job has the JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE flag specified, **closing the last job object handle terminates all associated processes and then destroys the job object itself**"；另确认"After a process is associated with a job, by default any child processes it creates using CreateProcess are also associated with the job"及breakaway仅当设JOB_OBJECT_LIMIT_BREAKAWAY_OK/SILENT_BREAKAWAY_OK——与windows_job.py:222-226（仅ACTIVE_PROCESS|JOB_MEMORY|KILL_ON_JOB_CLOSE）及09双进程观察互证。
- S1 kernel-object-namespaces页确认："each session has a separate namespace"（对象清单含job objects）、"client processes can use the 'Local\' prefix to explicitly create an object in their session namespace"、"The first user to log on uses session one, the next user to log on uses session two, and so on"。
- S4 ProcessIdToSessionId页确认：取指定进程所属RDS会话号；"Callers must hold the PROCESS_QUERY_INFORMATION access right"——对自身进程天然满足，自证无需特权。
- S2/S5未重开（如实登记）：S2内容（job与event/mutex同命名空间）已被S1页第一句对象清单直接覆盖；S5仅辅助说明注销灭进程，**核心论证不依赖它**（互斥+对象存在性兜底）。

**充分性判定：核心论证链成立**——同号（单机内）⇒同Local命名空间（S1）⇒"对象FILE_NOT_FOUND+互斥在手+租约过期"⇒旧树必灭（旧SUP活着⇒必持互斥或持Job句柄，互斥地被排除；已死⇒其句柄随进程死亡关闭⇒S3语义杀树销毁；从未建Job⇒无树）⇒全额保守折叠W安全、不双跑不漏杀不误退。逐路径核对：

| 情形 | 裁决 | 依据 |
| --- | --- | --- |
| 同boot同会话、旧SUP活着 | 对象存在（走精确terminate/整树确认）或互斥不可得（等待/失败关闭） | 互斥+对象存在性 |
| 同会话、旧SUP已死 | FILE_NOT_FOUND→折叠安全 | S3官方语义推论（09实测的是主动close路径，本情形未单独实测——D3文档已按S3语义论证，处理正确） |
| 注销后同号复用 | 折叠安全 | 注销灭该会话全部进程（S5辅助）；即使注销语义不完备，活着必持互斥/句柄被排除 |
| 跨boot/快速启动同号 | 折叠安全 | 旧进程随boot终结全灭；提案不依赖boot GUID——逻辑正确 |
| 休眠/会话断开（同会话恢复） | 对象路径或失败关闭 | 会话延续、对象/互斥可查 |
| **同号异机（共享DB多主机）** | **不安全——恢复主机B上FILE_NOT_FOUND但旧树在主机A仍活** | S1命名空间按主机×会话划分；numeric会话号跨主机重发 |
| 异号/缺值（含迁移旧行NULL） | 失败关闭、保留R人工处置 | 提案明确 |
| claim响应丢失/旧SUP晚到/取消 | 沿原G/C/CAS裁决 | review-02已核路径复用 |
| 互斥取得含WAIT_ABANDONED | 语义正确（=旧持有者死亡） | windows_job.py:169+官方语义 |

**唯一逻辑缺口**：同号裁决行未显式写死单机前提（部署限制段有"跨会话/跨机"字样但主表同号路径未限定）。**两项实施前置**：①单机前提显式化（部署文档+恢复代码前置检查）；②windows_job.py open_existing当前:240-243合并所有失败为JobUnknown、**无法区分ERROR_FILE_NOT_FOUND**——D3方案第2步的"严格区分"须先改造此函数并配定向纯单元。另：③"DB收敛先于互斥释放"的时序在run_once收尾须显式断言（沿084已审session.py 502a3743结构，实施卡加测试覆盖）。
**措辞修正**："无需官方并不存在的用户态boot GUID"应为"方案不依赖boot GUID；此前调查未找到官方用户态boot GUID来源"——"官方不存在"是对"未找到"的过度升级（不影响方案逻辑，方案确实不需要）。
**合规性**：全额折叠非部分退款、无t1记账，符合082批准的保守模型；新增持久字段确属082边界外（082-work-decision:19"新增字段/公开接口…先交回，不自行扩展"），D3文档已正确保留用户批准门、本卡未实施。

**推荐（供编排提交用户裁定）**：D3方案**可提交批准**，批准内容=006迁移一列（NULL默认）+claim接口SUP自证会话号原子写入+"同号自动折叠/异号失败关闭"语义+**单机单交互会话部署限制**；实施合同最小必含上述①②③与定向PG三例（同号折叠/异号拒/缺值拒）+恢复纯单元，不重跑079/PG08。替代解（不批字段：单交互会话+异号全人工runbook折叠）同样成立。不自行批准或实施006。

## 统一结论

- **D1四场景有效范围**：A=真实完整链正常结算；B=管理截止代码路径（注入触发时点、真实前提）；C1=Resume前父死（结构性悬停保证）；C2=Resume后父死（SUP独立完成正常窗口结算与销毁）。局部未覆盖且已明确分级：launcher链内"worker挂死→SUP截止终止"（Job07-02局部延续）、"SUP死亡无其他句柄→KILL_ON_JOB_CLOSE"（S3官方语义推论）。**最终代码未发现新确定缺陷**。
- **最少补项**：无阻断项；D3实施验证属其自身批准后另卡。允许推进后续，不制造新硬门槛。
- **旧证据复用**：Job07/PG08/纯单元/review-05静态结论按未变范围复用成立（hash零漂移佐证）；不重审全仓不重跑。
- **偏差与验收影响**：4容器（口令不可恢复的结构性根因+runner前置缺陷）、首批批级日志覆盖（最终批完整独立、runTag维度留存）、复验全批重跑（runner无场景参数）、TOTAL_WINDOW=660口径——均执行合规层面、已逐条在案，不损害最终PASS证据力，不构成验收阻断。
- **不签**：全项目M-1/STEP008、未验证one_call业务链、旧G动态恢复通过、生产KILL_ON_JOB_CLOSE的"SUP死亡无其他句柄"实测——均维持not_run/未实测登记。
- **下一步必要用户决定**：①D3方案（含单机部署限制）批准与否（或选纯人工替代解）；②四容器处置（保留/删除）——留编排。

证据：Ndocu/evidence/task-084/review-06/{prelog-assessment.md, hashes.txt}；被评证据 Ndocu/evidence/task-083/launcher-complete-09/（26文件）。历史review-05及更早原文完整保留于下方。

---

## 历史：TASK-084 review-05 及更早结果原文
# TASK-084 / R-078 / STEP008 — review-05 三处替身修正最终增量确认（当前有效）

**裁定：review-04 最小修正清单三处缺陷（①回执硬编码身份 ②open_existing 硬编码/恒真断言 ③starter/kernel 句柄撞号）已按最终 diff 全部关闭，本轮独立确认零未闭合项——六项 hash 零漂移；独立 difflib 证实改动全部限定 StartLifecycleTests 区段、区段外字节级相等；派生索引 args[4]/[5]/[6] 与 job_control.py:82-84 实参逐位核对一致；无 patch uuid4、身份校验零削弱；focused_unit 无运行链引用、新差异零传导。三例（生命周期两例 + 05）均项目 venv 实跑通过（exit 0，2.478s/0.883s），05 诊断行运行时 hash 与冻结一致、C1/W6 断言适用；旧 D1/碰撞 PASS 沿局部不变性延续成立。夹具侧对现有 Job01—05 准备的确定阻断全部解除；Job/PG 冻结维持，真实 OS/PG 验证仍为 0。不签真实 OS/PG 通过或 M-1/STEP008 最终验收。** 原084独立增强审计窗口接续（review-05），实际身份 GLM-5.3（本窗系统标注，无更细可核实后缀；如实登记，不因模型标签重审有效工作）；未参与083任何修改，不接管实现或编排。

## 输入、冻结与独立性

冻结三文件与 pre/ 三副本共六项独立复算（托管 Python hashlib 只读）：focused_unit.py=dfaaf814…5259（卡冻结 MATCH）、job_control.py=5bc35bf1…（未变）、offline_unit.py=3029a709…（未变）、pre__focused_unit.py=4a633aff…（=review-04 轮终值，pre→post 连续性成立）、pre__job_control/pre__offline=当前一致值——六项全 MATCH 零漂移（review-05/hashes.txt）。其余 13 个直接依赖沿 fixture-completion-06/final-hashes 与 review-04 证据复用，未全仓重采，未知漂移停对应结论。

接触顺序（prelog 纪律，review-05/prelog-assessment.md 披露）：公共规则 → review-04 自身基线 → 六项 hash 复算 → pre/final-hashes、incremental.diff → focused_unit 全文 + job_control 全文 + offline_unit test_05 区段 → 独立 difflib 比对 → **独立初判落笔（读日志前成形）** → manifest-final.txt、unit-lifecycle-06.log/meta、offline-05-06.log/meta、static-check.txt → 083 结果当前段（待评陈述，最后读取）→ 082 批准决定（原批准边界核对，无变化）。未读实现聊天。本卡运行额度 0：未运行 AST/import/compile/单元/Job/spawn/PG/Docker/网络/模型/安装/真实配置，未运行任何实现者脚本（static_check_06.py/run_batch_06.py 只读文本与输出）；唯一执行的两条命令为自写只读取证（hashlib 哈希复算、difflib 文本比对），零写入。

## 1. 三缺陷逐项关闭确认（独立差异级审查）

| 缺陷（review-04 编号） | 独立确认依据 | 结论 |
| --- | --- | --- |
| ① 回执硬编码身份 vs 控制器随机身份 | `_identity_lines` 整体删除；fake_spawn 从真实 spawn 实参派生：args[4]=activity_id（str，控制器 :34 `str(uuid4())`）、`int(args[5])`=7（int，:36 固定）、args[6]=run_tag（str），与 job_control.py:82-84 实参顺序（base_executable, "-B", fixture, "controller", activity_id, str(generation), run_tag, start_name）逐位一致；job_name 用真实导入函数+派生身份构造，与 :97-100 expected 五元组逐字段同型同值（JSON 往返 int 7→7→int、str→str）；pid/created_100ns/active_processes 与 GetProcessTimes 替身全零、:133 resumed 校验对齐（沿 review-04 已核结论）。patch 面仍仅三处 OS 边界（focused_unit.py:207-209），uuid4 未被 patch；job_control.py hash 未变 → 身份校验零削弱。实施即 review-04 裁定的方案 A（实参派生），优于 patch uuid4。 | **关闭** |
| ② open_existing 断言硬编码/负断言恒真 | 成功例 :233-234 与分支 B :258 均改用派生 `identity["activity_id"]` + 字面量 7（FakeNamedJob 记录控制器随机 activity + int 7，job_control.py:116 → 元组必然匹配）；分支 B spawn 成功 → identity 已派生 → 负断言可发现任何真实 open_existing 调用，**不再恒真**；分支 A 显式断言 `identity == {}` 且后续断言不引用 identity 字段——失败分支不靠错误元组恒真。 | **关闭** |
| ③ starter/kernel 句柄基址撞号 | Kernel 接收 base；fake_windll 按实例序号给 100（starter，:48 首次 WinDLL）与 100100（kernel，:57 二次），分配面 [100,101) 与 [100100,100103) 互不相交；**原断言全保留**：set_event(start)/close_handle(start) 恰一次、readline<close_handle(start)<open_process<open_existing 四条次序断言语义不变；kernel.CloseHandle(worker_handle)（:171）与 starter.CloseHandle(start_event)（:104）不再混入同一计数。 | **关闭** |

**范围与传导**：独立 difflib 比对 +51/−30 行全部落在 StartLifecycleTests 区段（pre 57-240 / cur 57-261），区段外 head/tail 字节级相等（EventControlTests 碰撞两例、LauncherTests D1 期限用例方法体未动）；incremental.diff 与独立比对逐块一致。focused_unit.py 仅被 Ndocu 取证脚本引用，job_batch.py 只 import 未变的 job_control——**新差异零传导到 Job 运行链**，review-04 已核的控制器句柄合同与 05 静态流程结论无需重审。成功例全流程替身值推演（初判于读日志前落笔）与实际运行吻合。

## 2. 证据适用性确认

- **两生命周期例**：unit-lifecycle-06.log 两例 ok、Ran 2 tests、OK；meta exit_code=0、2.478s（≤60s）、项目 venv（backend/.venv/Scripts/python.exe -B）、cwd=项目根、failfast 未触发跳过。PASS 绑定 dfaaf814：final-hashes 先冻后跑 + static-check post hash + 本轮当前文件独立复算零漂移，三点闭合。
- **05 例**：offline-05-06.log test_05 ok、Ran 1 test、OK；meta exit_code=0、0.883s。诊断行：t1>t0（1.0004e12>1e12）、delta_ns=400000000、observed=1、window=6、state=settled、job_events=[spawn_suspended, resume, query, close_job]；**imports 运行时 hash 绑定**：session.py=502a3743…f16c、offline_unit.py=3029a709…4c5c，与冻结值一致 → 运行快照=最终源码，C1/W6 断言适用。
- **性质边界**：三例为真实控制函数（verify_last_handle / run_once）+ OS 全替身/测试局部确定性时钟，**不是 Windows 实测**；不构成真实 Start/Arm/Exit 事件、真实 Job 对象、真实子进程、最后句柄行为证据。
- **旧 PASS 延续**：碰撞两例、D1 期限一例按 review-04 局部不变性延续（区段外字节级相等+直接依赖冻结），成立；第 12 项及其余 9 项沿 084 口径复用，无重跑。旧 05 原始失败根因仍未唯一证实（确定性时钟通过不回溯解释旧失败；卡面不要求循环复现，维持）。
- **静态偏差记录**：static_check_06.py 本轮以托管 3.13.12 而非卡定项目 venv 执行（083 如实登记）——文本/AST/hash 三层结构检查、不 import 不写 pyc，解释器差异不改变其检查域；该纯工具偏差**不构成产品测试重跑门槛**，项目 venv 实跑三例不因此失效。其 34 项 ALL_PASS 与本轮独立 difflib/手工跨文件核对互为印证（本窗未运行该脚本）。

## 3. 运行门结论（限增量）

| 门 | 增量结论 |
| --- | --- |
| 纯单元/夹具层 | review-04"下一最小批"前置（修正①②③ + 三例定向复验）已完成，**纯单元层无剩余确定阻断**；三例 PASS 绑定 dfaaf814。 |
| 现有 Job01—05 准备 | **夹具侧确定阻断全部解除**（04 控制器 verify_last_handle 控制流经替身全路径验证；job_control.py 未变，01/02/03/05 由 verify_scenario 控制且本轮零改动）。剩余门=编排授权解冻 Job + 真实 OS 预算（每场景≤30s、命令≤60s、批≤10 分钟、精确身份/创建时间/独立 deadline、未知即停）。真实 OS 证据仍为 0。 |
| 新 D1 固定 launcher 真实入口 | **仍未准备**：需独立外层控制+精确 SUP/Job 身份+限时+未知停批的场景设计先审；若需正常结算配专用合成 PG；不给产品入口加任意命令开关。此为新增场景，非现有 Job01—05 阻断。 |
| PG 六例 | 沿 review-03 精确清单（PGMigration 两例 + PGClose 四例）：专用 DSN、每例随机 schema、失败保留；当前连接 0、冻结维持；正常结算若需 PG 保持单独准备；与 D3 来源研究可独立安排。 |
| D3 旧 G 恢复 | 决定性缺口不变：旧 G 所处 Local 命名空间化身来源（跨冷启动/快速启动可辨识取值与生命周期）。仅阻断旧 G 恢复场景与整体交付，**不阻断干净新活动/隔离 Job 场景/独立 PG 六例**——不泛化为永久前置。 |

**最小路由（建议，非本卡授权）**：R1 受控真实 Job 批（Job01—05，含真实 OS 版 verify_last_handle 场景 04）——前置仅剩编排授权与预算核定；R2 新 D1 固定 launcher 入口场景设计审查卡（先审后跑；正常结算需 PG 则与 R3 联动）；R3 PG 六例准备卡（专用 DSN，可与 R1 并行）；R4 D3 化身来源只读事实决策卡（独立）。均沿 review-03 最小验证矩阵与停止条件，不新造压力/时钟/全仓回归。

## 4. 未验证风险与文档建议

未验证（如实登记）：真实 OS 全部维度（真实事件/Job/子进程/最后句柄/父死场景）、真实 PG 事务、D3 恢复、新 D1 固定入口——均 not_run，替身通过不升级。风险备注：① 派生方案依赖 job_control.py:82-84 实参顺序，控制器 argv 若再变更须同步核对夹具索引（本轮已核对一致）；② 05 确定性时钟结论依赖 session.py 当前形态（502a3743 冻结），session 再变更即失效；③ 旧 D1/碰撞 PASS 绑定方法级局部不变性，后续改动越出 StartLifecycleTests 即须复跑。

文档建议：编排可在执行状态记录"生命周期替身三缺陷已关闭并经 review-05 独立增量确认、三例纯单元 PASS 绑定 dfaaf814、Job/PG 冻结维持、真实 OS/PG 验证仍为 0"；docu/CHANGE.MD 沿惯例由编排补记（本卡禁改正式 docu）；不填 M-1/STEP008 最终验收。

证据：Ndocu/evidence/task-084/review-05/{prelog-assessment.md, hashes.txt}；被评证据 Ndocu/evidence/task-083/fixture-completion-06/（14 文件）。历史 review-04 及更早原文完整保留于下方。

---

## 历史：TASK-084 review-04 及更早结果原文
# TASK-084 / R-078 / STEP008 — review-04 夹具完整流程增量诊断（当前有效）

**裁定：运行首例"Job/G/runTag身份不匹配"的确定根因在替身而非控制器——verify_last_handle 自生成随机身份（job_control.py:34-35），夹具回执硬编码固定身份（focused_unit.py:68-77），job_control.py:97-100 校验结构性必然失败；另静态发现两处替身缺陷（open_existing 断言用硬编码身份、starter/kernel 替身句柄空间撞号）会在修完身份后相继卡住成功例。04 控制器候选满足句柄合同，无阻塞缺陷；05 时钟替身静态可运行。给出一次可合并实施的最小完整修正清单（只涉 focused_unit.py），三个剩余方法的验证范围与停止条件已列。本卡只读，运行额度 0；Job/PG 冻结不解除；生命周期与 05 的运行验证仍为 0，不宣告动态通过。** 原084独立审计窗口接续，实际客户端/模型标签 GLM-5.3-Flash（如实登记，不因已完成任务模型标签重审有效证据）；未参与083实施，不接管编排或修复。

## 输入、冻结与独立性

冻结三文件独立复算（托管 Python hashlib 只读）与卡面逐一 MATCH（review-04/hashes.txt）；其余直接依赖沿两轮 final-hashes 复用，13 文件两轮一致零漂移，未展开全仓。接触顺序（review-04/prelog-assessment.md 披露）：冻结复核 → 两轮 pre/final-hashes 与 incremental.diff → 三源文件全文 + session.py run_once 全路径（必要直接依赖；windows_job.py 未重读，沿 FROZEN_OK 登记）→ **独立初判落笔** → 两轮运行日志/meta、05 轮静态三尝试日志、两份 manifest → 最后 083 结果置顶两段（待评陈述）、084 review-03、082 批准记录、归档卡。未读实现聊天；未运行 AST/import/compile/单元/Job/spawn/PG/任何脚本；源码/测试/迁移/正式docu/公共库/Git 零写入。初判核心结论（根因与两处新缺陷）在读运行日志前已成形，日志仅作证实。

## 四项结论

### 1. 生命周期夹具完整核对：三处确定缺陷，一次可整体修好

替身值逐步映射（成功路径）：uuid4 随机身份（:34-35）→ spawn 实参 args[4]/[5]/[6] 完整携带（:82-84）→ 夹具回执硬编码（:68-77）→ :97-100 校验必败。**缺陷一（运行时已证）**：随机身份 vs 固定回执，activity_id/run_tag/job_name 三字段必不匹配；phase/generation/pid/created_100ns/resumed.pid 夹具均已对齐。**缺陷二（静态新发现）**：focused_unit.py:215 `log.index(("open_existing", activity, 7))` 用硬编码 activity 查 log，而 FakeNamedJob 记录控制器内部随机 activity（job_control.py:116）→ 修完缺陷一后此处必 ValueError；:237 分支 B 的 assertNotIn 因 open_existing 未被调用而侥幸恒真，语义同错。**缺陷三（静态新发现）**：starter/kernel 是两次独立 fake_windll，两个 Kernel 各自 `_next=100` 起编号，start_event=100 与 worker_handle=100 撞号——成功例 finally 中 kernel.CloseHandle(worker_handle=100)（job_control.py:171）与 starter.CloseHandle(start_event=100)（:104）混入同一 log，`count(("close_handle", start_handle))==1`（focused_unit.py:210）必败为 2。**缺陷二、三不修，修完缺陷一的成功例仍会相继失败**——这正是本轮要求"不只报告当前首错"的静态收获。

已排除的疑点（避免误报）：partial 8 API 与 job_control.py:49-71 赋值面/调用面闭合；_new_event_or_reject 的 set_last_error(0) 先行使 get_last_error() 确定性返 0，183 误判不存在；GetProcessTimes 替身不动 byref _FILETIME 与 created_100ns=0 对齐；asyncio.wait_for 用循环内建时钟不受 patch 影响；patch 作用域 with 内恢复无越界。失败分支 A（spawn 异常）/B（空回执）在当前替身下静态自洽（A 不触身份校验、B 的 count 恰 1），不受缺陷三影响（worker_handle 未取得）。

**最小完整修正清单（全部只涉 focused_unit.py 的 StartLifecycleTests，不取消任何身份校验）：**
- ① 身份派生：fake_spawn 从 spawn 实参 args[4]/args[5]/args[6] 派生 activity_id/generation/run_tag，动态构造 created 行（job_name 用已导入的真实函数、pid=123、created_100ns=0 不变）与 resumed 行（pid=123 不变）。与真实协议数据流一致（SUP 子进程从 argv 接收身份并回执），不耦合源码 uuid4 调用次数——优于 083 置顶段提议的 patch uuid4 方案（其需 side_effect 序列同时供 str 值与 .hex 属性，源码改单次调用即碎；两者均保留全部校验，编排可择一）。
- ② _run 返回派生身份（activity, generation, run_tag），测试断言 :215/:237 改用派生值（generation 字面量 7 不变，job_control.py:36 固定 int 7 与 FakeNamedJob 记录类型一致）。
- ③ 句柄基址分离：fake_windll 按实例序号分配不相交基址（如首例 100 起、次例 100000 起），Kernel.__init__ 接收 base；count/次序断言即可按原语义成立（starter 句柄 100、kernel 句柄 100000+，log 记录互不混淆）。

### 2. 04 真实控制器增量：候选满足句柄合同，产品源码零新缺陷

verify_last_handle（job_control.py:33-181）资源纪律逐项核过：Start 父句柄持有至子 Open 并回执悬停身份、身份校验通过后才释放（:103-105，102 行注释的竞态语义与 review-03 裁定一致）；主流程释放与 finally 补释放由 start_released 标志互补，所有异常出口**恰一次**释放；收尾保留原 deadline（:163 用 deadline_ns 计算剩余）与精确身份（kill 用 proc 对象、Terminate 用精确 worker 句柄）；观察 Job 释放时点：成功路径父观察句柄先关、parent_job=None 后才 SetEvent Exit（:135-137），最后句柄场景不被破坏，finally 仅对非 None 兜底无二次 close。**产品式控制器缺陷：无。纯替身缺陷：三处（见上）。** 两条备注（非阻塞、真实不可触发或低概率）：start_event 创建于 :56 而 try 起于 :80，:57-71 确定性 ctypes 属性赋值段若抛异常则 start_event 无 finally 覆盖（结构备注）；:88-92 except 内 proc.kill()/wait 无独立保护，kill 失败会覆盖原异常（低概率备注）。**不因新测试失败判控制器有错**：运行首错根因在替身回执固定身份，控制器"自生成身份→spawn 传参→校验回执"的协议语义正确（真实场景 SUP 子进程正是从 argv 拿身份回执）。不以意向代码签通过：生命周期运行验证仍为 0。

### 3. 05 最终时钟替身静态可运行性：成立（仅静态，not_run 不升级）

patch 面：app.worker.session.time 与 offline_unit 模块 time（脚本直跑 __main__.time）→ _TestClock；run_once test_05 路径全部 time.* 引用为 monotonic_ns（session.py:103/133/187/208/217/231，:170/:285 在 pending 分支不执行），**无 time.sleep**，clock 无 sleep 方法不构成缺口；offline_unit 侧 test_05 路径仅 run_fake:153 一处。FakeJob.wait_empty_until 注入 clock 时显式 advance 0.4s 无真实睡眠；finally 中 job 已 None 不再 wait_empty_until，清理等待可终止。asyncio 不被误伤：patch 为模块属性替换，loop 内建时钟不受影响，_db 的 wait_for timeout=min(0.5,20)s 真实时钟而协程瞬时；其他用例串行且在 patch 外。断言真连实际流程（静态推演全程）：t0=1e12（claim 前 :187）→ wait_empty advance 0.4e9 → t1=1.0004e12（:231）→ delta=400_000_000 ✓ observed=(4e8+999_999_999)//1e9=1（:233 公式）✓ window=lease.window_seconds=6 ✓；job_closed（:243 job.close→FakeJob 外部事件）先于 close_db（:245）✓；settle#1 TimeoutError→:252 except Exception→settle#2 同 G（:248/:254 同 lease.execution_generation）→ALREADY_SETTLED ✓；(settled,reserved,pending)=(1,0,0)（:263-266）✓ active_processes_at_end=0（:311）✓ ledger.events=[inspect,claim,job_closed,close_db,settle,settle] ✓。纯测试注入不改生产 C0/C>W 契约：session.py 502a3743… 冻结未动，:238 `1<=observed<=window` 原样。

### 4. 证据适用性与下一最小批

- **D1 期限/碰撞**：直接依赖 13 文件两轮 FROZEN_OK + 本轮三冻结复核一致；LauncherTests/EventControlTests 测试方法与替身 AST 未变（04 轮 diff 仅动 d1_deadline 一例的值序列与断言增强 + 新增 StartLifecycleTests；05 轮 diff 仅动 StartLifecycleTests 内部）。→ 04 轮运行批碰撞两例 PASS 与 D1 deadline PASS 按**局部不变性适用**（绑定 focused_unit 4a633aff 的方法级状态），review-03 的 D1 静态有条件通过继续有效；不按全文件 hash 轮换机械全部失效。下一卡若修正只涉 StartLifecycleTests 内部，D1 与碰撞方法 AST 仍不变，可继续延续，是否并入复跑由编排择定。
- **05 轮静态三尝试**：attempt-01 检查脚本 ast.AsyncFunctionDef 漏扫（assigned=[] 假空）+ docstring 误判 FAIL，源码中间态 144335c4（44 diff 行）；attempt-02 修复漏扫但 docstring 判定仍 FAIL、同一中间态；attempt-03 ALL_PASS、最终 4a633aff（40 diff 行）。中间态未运行未交付、日志原样存档——属检查脚本缺陷与临时编辑问题，**不丢弃最终证据**（ALL_PASS + hash 与冻结一致成立）。原卡一次运行额度已用于 unit-lifecycle-01（生命周期两例定向、failfast）：首例 FAIL 即停、第二例 not_run、offline05 未在本轮命令内 not_run；旧 05 根因仍未证，不循环追复现。本卡运行额度 0，未占用任何新额度。
- **下一最小批（建议新修正卡，一次运行额度、两条命令）**：前置实施上述修正①②③（仅 focused_unit.py StartLifecycleTests）；Command 1 = `focused_unit.py --failfast StartLifecycleTests` 两例，预期 2 ok；Command 2（仅 Command 1 过）= `offline_unit.py OfflineRepairTests.test_05_…` 单例，预期 ok。**停止条件**：身份校验再失败（派生遗漏字段）即停；断言 ValueError（句柄/身份记录遗漏）即停；任一替身边界内非断言性异常即停不扩跑。修后 focused_unit.py hash 轮换，本轮三缺陷对应断言即其验证范围；Job01-05 真实验证、新 D1 固定 launcher 真实入口仍另卡，本清单不构成运行门放行。

## 分类结论与未验证风险

| 层 | 结论 |
| --- | --- |
| 产品代码 | 本轮零缺陷零改动；13 依赖文件冻结一致；D1 旧用户态无界路径 review-03 静态结论维持，D3 恢复未闭合（本轮不追加来源研究/OS探针/持久模型） |
| 测试替身 | 三处确定缺陷（身份固定回执、open_existing 硬编码断言、句柄撞号）+ 两条非阻塞备注；最小修正全部只涉 focused_unit.py；05 时钟替身静态自洽 |
| 真实 OS | 验证仍为 0：生命周期两例、05 时钟注入、Start/Arm/Exit 真实事件、最后句柄行为均 not_run；静态自洽≠动态通过 |
| PG | not_run，冻结维持；repository/005 结论沿 review-02/03 复用 |

**未验证风险**：① 修正①②③实施后的实际运行行为未知（本轮静态推演不替代运行）；② 方案 A 与方案 B 均未实施，若实施中引入新替身状态（如派生解析对 args 索引的假设）需静态复核 spawn 实参顺序仍为 job_control.py:82-84 所列；③ D1 碰撞/期限旧 PASS 绑定方法级局部不变性，若下一卡改动越出 StartLifecycleTests 范围即须复跑；④ 05 静态结论依赖 run_once 无 time.sleep 的当前源码形态，session.py 再变更即失效。

**文档建议**：编排维持 083"部分/冻结"与 084"诊断通过、实施待新卡"；可在执行状态记录"生命周期替身三缺陷已定位、修正清单已审、运行额度 0"。不填编排最终验收，不宣告 M-1/STEP008 完成。

证据：Ndocu/evidence/task-084/review-04/{prelog-assessment.md, hashes.txt}。历史 review-03/review-02/首轮原文完整保留于下方。

---

## 历史：TASK-084 review-03 及更早结果原文
# TASK-084 / R-078 / STEP008 — review-03 定向独立复核（当前有效）

**裁定：D1 旧 `Process.start`/Pipe 无界用户态路径已由固定悬停 SUP 与有界映射替换，属代码层有条件通过；04 的碰撞拒绝已修，但 Start 事件生命周期仍有确定可运行性竞态。最终纯单元期限用例是夹具错排，05 旧失败根因仍未证。D3 恢复可用性未闭合；Job/PG 本卡仍冻结。** 原084独立审计窗口继续执行，实际客户端为 Codex desktop、可见模型标签 GPT-6（无可核实的 Sol 等后缀）；未参与083代码修改，不接管实施或编排，不签产品动态安全通过。

## 输入、冻结与独立性

先复读本结果 review-02，核 `focused-repair-03/pre/` 实际副本、`pre-hashes.txt`、`incremental.diff`、`final-hashes.txt` 与七份最终源码；在读取运行日志前写下 `Ndocu/evidence/task-084/review-03/prelog-assessment.md`。之后才读 `05-diagnostic.log/meta`、`unit-final-01.log/meta`、`unit-stop-analysis.md`、两份 manifest、`static-final.log`；最后读实现方 `official-facts.md` 六页摘要与 `TASK-083-result.md` 当前置顶段（含四项实现者陈述、历史开头），仅作待评材料，未读实现聊天或打开新网页。`review-03/hashes.txt` 独立复算七份最终源码及 repository/005：九项全匹配；另核未变 `scenario_child.py`、`job_batch.py`、`fixture.py` 的旧哈希。`session.py` 的大量空行差异未当成重写：实质新增诊断/父进程身份字段及计时观测，原 C 限制、结算与恢复分支未改。实现方 AST_OK 属其自有日志，本窗口没有运行 AST、import、compile、单元、Job、PG 或配置。

## 四项增量结论

| 项 | 独立代码判断与定位 | 证据边界/运行门 |
| --- | --- | --- |
| D1 启动与IPC | **有条件通过旧缺陷的静态修复。** `launcher.py:93-116,234-273` 用显式 base Python 和固定 `app.worker.supervisor_main` 创建悬停进程、禁继承，记录精确PID/创建时间，第三次运行窗检查后才Resume；`supervisor_main.py:23-73` 在子端检查同一 `deadline_ns` 并传给 `run_once`。`supervisor_ipc.py:19-64,96-145` 两个8KiB槽、限长/校验/完整性、创建183拒碰撞；父只在确切SUP退出后读结果，`launcher.py:196-211` 校验runTag/activity/字段形状。进程死亡不被解释为业务Job零进程。 | 消除了旧 `Process.start`/Pipe `send/recv` 阻塞点；CreateProcessW返回前无可握句柄、Win32内核无限阻塞仍不承诺硬实时。真实固定入口、venv转发、父死亡及终止耗时未运行；运行门未开。 |
| 04 控制器 | **碰撞缺陷关闭，另有确定旧竞态。** `job_control.py:21-30,55-56,222-224` 对 Start/Arm 的失败或183拒绝，碰撞只关闭本次返回句柄，不SetEvent；纯替身两例PASS。可是04在 `:59-71` SetEvent(Start)后立刻关闭其唯一父句柄，`fixture.py:20-42` 子端可能尚未OpenEvent：对象销毁，子报10而不是产生可审证据。该生命周期竞态在改前代码已存在，本轮碰撞修复没有解决。 | 04不可作为稳定可运行用例；最小修复为持有父Start句柄至子已打开且发出悬停身份回执，失败则在最终精确清理时关闭。04的最后句柄观察者释放时点仍按review-02，真实验证未做。 |
| 最终期限失败/05 | **期限用例为确定夹具错排；05旧根因仍不足证。** `focused_unit.py:215-222` 给 `_remaining` `(5,5,5,0,0)`；`launcher.py:249-268` Resume前只有三次检查，第三次仍为5，第四次已是Resume后wait参数，故必得 `manager_timeout_unconfirmed` 而非预期的 `manager_startup_deadline_unconfirmed`。最终日志正如此。05仅在 `offline_unit.py:78-93,166-187` 加观测，`session.py:231-239` 保持 `1≤C≤W`；本次Δ=15ms、C=1/W=6、settled PASS，只证本次快照路径。 | 最终10例9过1败，exit1；第12项因停批not_run。旧05失败未记录旧t0/t1；本次PASS不能宣称旧故障消失。 |
| D3 恢复 | **安全失败关闭延续，自动恢复可用性仍开放。** `session.py:165-185` 与 `windows_job.py:237-244` 对旧running Job Open失败仍拒新工；repository/005未变。`official-facts.md` 的六页摘要支持 `Local` 按会话隔离、numeric session ID与uptime不是唯一化身、快速启动/休眠不能凭墙钟猜测的保守结论，但这些是实现方摘要，本窗口未重新打开原页。 | “本轮未找到来源”不等于Windows没有可行机制；两列的具体值/化身语义尚无可靠来源，不能批准迁移，也不能把任意Open失败算0。D3阻断恢复场景与整体完成，不自动阻断满足隔离前提的干净新活动定向验证。 |

D2固定worker门、D5 reserved→UNKNOWN、D6取消及D7 PG夹具隔离沿review-02有条件结论复用，不重审未变仓储或旧079。D8在新路径仍保守：`launcher.py:276-325` 无可解码SUP结果时 R/S/pending均None且 `cleanup_incomplete=True`；中断重抛附未知结果。若已有可信子结果但父句柄/映射关闭失败，则标不完整；`supervisor_main.py:72-84` 结果写入或close失败使子非零，父不把其当clean。真实父终止后业务Job能否及时整树退出仍需确切Job事实；父未证SUP退出时会报告未知并停批，不能把 `TerminateProcess` 返回或SUP退出当退款证明。若终止等待耗尽，`launcher.py:280-298` 最终关闭精确进程句柄，留下未证停止的SUP；该出口只有在调用方遵守 `cleanup_incomplete` 后停止后续工作时才安全，不能用于自动重试/恢复。

## D1 安全边界与最短动态证据

命名映射采用随机128位名、16KiB pagefile对象、默认token DACL；帧SHA-256只检损坏，**不是同权限恶意进程认证**。DSN经请求槽传给受信SUP，错误只报类型/Windows码，不打印DSN；环境块复制父环境，故本地同权限非受信进程或过宽ACL不在当前已证明范围。`bInheritHandles=False`，结果只在SUP确切退出后取，避免半帧误判；创建、映射/进程句柄失败路径返回未知而不启动业务。当前安全判断限批准的受信本地模型，不借无限看门层应对任意内核挂死。

父死在Resume前：当前父代码没有后台线程可迟到Resume，悬停SUP可能遗留为资源对象，但其线程不会由本代码运行，更不会claim/建Job；父死在Resume后且子尚未Open映射时，父最后映射句柄消失使子失败；若子已打开，则子持映射和本窗Job监督职责继续运行。父主动终止已运行SUP时，业务Job由SUP持句柄及 KILL_ON_JOB_CLOSE 约束，但最后句柄和后代退出必须真实查询/受控证据；父返回未知不退款。`supervisor_main.py:66-73` 将同一绝对截止交给 `session.py:102-115,160-223`，其DB await、claim前置和Job停止窗继续受限。唯一仍需实测的是固定解释器启动、窗口交接、父死/子存、最后句柄、主动终止与实际耗时；现有纯替身不能证明这些。

**现有Job01—05不覆盖新父launcher。** 未变 `scenario_child.py:69-75` 的01/02直接调用 `SingleWindowSupervisor.run_once`，03/05直接创建Job；`job_batch.py:24-35` 只调用这些控制器。它们可验证原Job/树/碰撞协议，但不能被称为D1固定SUP真实OS验证；未来须另列一个受控的固定launcher入口场景（若要求到正常结算，则用专用合成PG；不允许为测试给产品入口加任意命令开关）。先具备独立父控制、精确SUP/Job身份、限时和未知即停，才可申请运行额度。

## 两次失败的证据限度与最小修正

期限用例最小只改 `focused_unit.py:217` 第三次返回0，保留前两次5及后续清理预算；验证同一用例必见 `create_suspended→identity`、**无Resume**、精确SUP terminate/exit确认、未知账字段，且无结果读取或claim。不能把期望字符串改成 `manager_timeout_unconfirmed` 来掩盖没有覆盖Resume前截止。真实 `launcher.py:263-268` 的判定分支无需因此修改。现有9个PASS只覆盖各自替身；首命令整体exit1，`unit-final-01-meta.txt`记0.6060814秒，而 `unit-stop-analysis.md`记0.7465334秒，记录口径不一致但均低于60秒，不影响失败裁定；第12项 `FixedEntryTests.test_12_fixed_command_and_injected_gateway_pass_through_gate` 是not_run。

05诊断日志固定 `t0=1172500000000`、`t1=1172515000000`、sleep前后正好为这两值、Δ=15000000ns、C=1/W=6，导入源哈希为当时session `9956e442…`、offline_unit `6941dbc9…`；最终hash分别 `502a3743…`、`3e79ce97…`，改前与最终源码对照可确认C公式、`time.monotonic_ns`调用及2ms sleep在这两个冻结端点未变；但诊断时的两个中间源码哈希与最终不同，未保存其字节副本，不能仅凭实现者描述断言中间→最终只改输出字段，也不能把诊断PASS登记为最终快照PASS。该正例与review-02的05 `elapsed_violation_full_reservation` 可同时成立：2ms sleep可能跨过或未跨过更粗的时钟刻度，日志的15ms跳变使此解释**合理但未证实**；旧失败没有Δ/睡眠读数/导入hash，不能唯一确定旧环境或C=0。下一卡只需把05纯替身的正耗时改成可证明的有界单调推进/显式时钟注入，并断言 `t1>t0`、C=1、Job0后settle；一次定向验证足够，无需无穷复现旧故障，不得放宽生产 C0 拒退款。

## D3 最窄决定与唯一下一路径

review-02提出的 `running_owner_boot_id` + numeric `running_owner_session_id` **目前不充分**：后者可复用，前者尚无经官方支持、可跨冷启动/快速启动/休眠辨识的取值与生命周期；即使持活动互斥，跨登录会话同名 `Local` 对象仍可能错判。决定性缺口是能在claim事务可信持久化、恢复时可比较的**旧G所处Local命名空间化身**，以及对不同化身旧受控进程是否已灭的可核事实。可以另卡定向查这个来源及API语义；当前资料未找到不构成“不存在”的证明。若取得来源，再提交具体原→新claim字段/事务、缺值失败关闭、同化身精确Open/明确FILE_NOT_FOUND+无迟到创建、异化身旧树退出的窄方案供批准；不引入未证必要的常驻见证服务/逐阶段表，不追溯死亡窗部分退款。当前旧G Job消失仍可能永久挂R、无法新claim；安全失败关闭不等于满足恢复目标。

**唯一下一执行路径由编排开一张窄离线修正卡**：只修04 Start句柄持有时点与 `focused_unit` 的第三检查值/断言，05替身改成有界确定正耗时；静态重冻后在新增额度内精确复验 04碰撞两例、D1 Resume前截止一例、05一例及已预列而未运行的第12项（若门控源码未变，12可按已有review-02最终PASS复用，由编排选择）；其余本轮9项按受影响关系复用。独立窗口再核差异与原日志。D3化身来源另作**只读事实决策**，不先批准两列。随后编排可分别申请受控Job与PG运行，不能由本报告自动解冻：干净新活动、无旧running G且精确所有权/期限/未知停批时，Job01—05可验证各自Job行为，另补新D1固定launcher真实入口；D3仍只阻断旧G恢复及整体交付。PG仍按review-02六个精确ID在专用DSN/随机schema/失败保留条件下验证005与关门事务，和D3来源研究可独立安排；若将来新增持久字段，再单列迁移/claim/恢复PG，不机械重跑079。

### 最小验证矩阵（均非本卡运行授权）

| 范围 | 现有标识/最小新增项 | 前置与可复用证据 |
| --- | --- | --- |
| 纯单元 | `EventControlTests.test_04_start_collision_closes_only_returned_handle`、`test_04_start_creation_error_and_new_handle` 已PASS；修04句柄生命周期后只补其持有至身份回执断言。`LauncherTests.test_d1_deadline_before_resume_terminates_exact_owner` 修第三次检查后定向复验；`OfflineRepairTests.test_05_early_success_uses_tree_zero_close_then_same_g_settle_retry` 仅在正耗时确定化后定向复验。 | 新额度、最终hash；本轮其他9例按未受影响路径复用。`FixedEntryTests.test_12_fixed_command_and_injected_gateway_pass_through_gate` 本轮not_run，因 command/worker_main/gate 未变，可复用review-02对同一直接依赖的PASS；若新卡更改这些依赖才重跑12。 |
| Job | 现有 `job_batch.py` mode01早停退款、02挂死全额、03主退后代存、04最后句柄、05同名碰撞；另须新增且先审的真实 `run_supervised_window` 固定SUP入口场景。 | 修04 Start生命周期、D1纯单元缺口；每场景精确对象/创建时间、≤30秒，单命令≤60秒，批≤10分钟并留收尾，未知停批。01—05旧批证据不覆盖新控制器；新D1入口需独立外层控制，正常结算需专用合成PG。D3不阻断无旧running G的隔离场景，但旧G恢复不可测为通过。 |
| PG | `PGMigrationTests.test_pg_migration_01_empty_table_adds_only_closed_column`、`test_pg_migration_02_nonempty_table_rolls_back_whole_005`；`PGCloseTests.test_pg01_close_settle_and_old_gc_does_not_touch_new_window`、`test_pg02_closed_gate_rejects_admit_mark_but_records_outcomes`、`test_pg03_close_commits_before_concurrent_admit_and_mark`、`test_pg04_cancel_closes_gate_and_old_dispatched_unknown_converges`。 | 新PG额度、专用DSN、每例随机schema及同一search_path、失败保留；repository/005静态hash及旧079未改结论复用。若D3日后增持久字段，再单列迁移/claim/恢复PG，不混作本批。 |
文档建议：编排维持083“部分/冻结”，记录04生命周期竞态、期限夹具错排、05旧因未证、D1真实OS not_run、D3化身事实不足；待独立增量复核与新预算后才判断局部Job/PG运行，绝不填M-1/STEP008最终验收。本窗口只有哈希/文本只读取证与上述授权两处写入，Job/PG本轮0、005未执行；没有修改源码、测试、迁移、正式docu、公共库、Git或旧证据，没有网络、安装、模型、真实配置或进程操作。

---

## 历史：TASK-084 review-02 及首轮结果原文
# TASK-084 / R-078 — review-02 增量独立复核（当前有效）

**裁定：代码与 Job 运行门仍不通过；PG 夹具静态隔离条件已改善，但 PG 运行仍冻结。** D1 的父级启动/IPC 可控上界、D3 的跨恢复证明未闭合；最终纯单元 05 失败且根因未证。不得接线、启动 Job/PG，亦不宣告 STEP008/M-1 完成。本轮是原 084 独立审计窗口，实际模型标识为 GPT-6（可见界面未给可核实后缀）；未参与 083 修改。下文仅审修复轮02增量，首轮原文完整保留在后。

## 快照、接触与证据

先复读本窗口首轮结果、独立初判和哈希，再读 `audit-fix-02/static-final.log`、`incremental.diff`、`pre/`及最终源码，先将判断写入 `Ndocu/evidence/task-084/review-02/prelog-assessment.md`，之后才读 `unit-initial.log`、`unit-recheck.log`、两份 meta 与 manifest。另读取 `TASK-083-result.md` 置顶前60行（含实现者D1—D8状态表、D1/D3提案及历史标题），只评其中D1/D3提案，没有以“已修”自评作为证明；pre/ 的旧结果副本也只用于差异定位。核对 `TASK-082-result.md:38-43` 已留的官方事实摘要，未重新联网。`review-02/hashes.txt` 独立复算13个新哈希及 session/windows_job/gate/repository/005 五个未变哈希，全部匹配。实现静态日志的 AST_OK 属实现方执行，本窗口**未运行 AST、import 或测试**。`fixture.py` 在084基线已存在（旧 D511DCEA…、新 C9970B8D…），改前字节副本遗漏；只审完整当前文件与首轮定位，不把 diff 对空当成精确增量证明。仓储和005的首轮静态结论沿用，未重审其全体。

## D1—D8 增量裁定

| 项 | 代码层状态与最短定位 | 运行含义 |
| --- | --- | --- |
| D1 父级截止 | **开放。** `launcher.py:66-96` 已先定绝对deadline并留清理窗，但 `process.start()`、子 `_supervisor_target` 的 `pipe.send` (`:20-31`)、父 `receive.recv()` 仍可能阻塞在调用内；`finally:103-135` 只能在这些调用返回后管理精确对象。部分 start 异常仅在获得 PID/对象后可清理。 | 纯替身09—11不能证明 Windows 启动、pickle、IPC 的期限；Job运行阻断。 |
| D2 固定门控入口 | **本切片代码层关闭，有条件。** `command.py:15-30` 仅允许 idle/one_call，argv 固定项目 venv 与 `app.worker.worker_main`；`worker_main.py:25-49` 实际入口调用 `run_internal_task→run_controlled_worker→ClosingCallGate`。任意 exe、`-c`、脚本不再由产品参数进入；危险合成任务在仅供测试的 `scenario_child.py:46-75` 以 monkeypatch 注入，产品未依赖。 | 真供应商/HTTP 未接；one_call 的现有 CLI 网关会明确失败，不能称业务链已验证。 |
| D3 恢复 | **开放。** 未变 `session.py:161-181` 遇 running 必须 `open_existing`；未变 `windows_job.py:237-244` 合并所有 Open 失败。已认领而 Job 已销毁仍可永久留 R/拒新工。 | 当前保守拒绝是安全停止，不能算完成恢复；最小模型见下。 |
| D4 Job 控制 | **大幅改善，仍有一处确定夹具缺口。** `job_control.py:165-263` 为01/02/03/05建立 Start/Arm、身份、创建时间、确切Job/独立25秒截止并在未知时停批；`job_batch.py:19-43` 55秒总限、失败即停。04在 `job_control.py:18-132` 于 Exit 前关观察Job句柄，`fixture.py:20-67` 限单进程；但04的 `CreateEventW(Start)` (`job_control.py:36-48`) **未检查 ERROR_ALREADY_EXISTS**，命名碰撞时现有已触发事件可令子进程在身份控制建立前创建Job。最小修复同其他场景拒绝碰撞。 | 04关闭后的Job计数不可查询，单进程限额+精确worker句柄退出仅是待本机证明的替代证据。旧Job五例不可复用为新控制器验证。 |
| D5 PG02 | **静态关闭。** `pg_close.py:122-132` 对 reserved 使用仓储既有合法 UNKNOWN，并预期两个 UNKNOWN；repository 未改。 | PG02 not_run。 |
| D6 取消 | **静态关闭。** `offline_unit.py:145-152` 对 claim 回应未知断言账字段 None、保留取消重抛和清理检查。 | 初批该项 PASS；最终解释器路径改动不触及其命令执行分支，证据限纯替身。 |
| D7 PG 隔离/并发 | **静态有条件关闭，未发现新的必然失败。** `pg_close.py:36-51` 每例独立 schema、001—005顺序、同一 `scoped_dsn` 传仓储/查询/清理；`:139-175` 用实际来源锁持有及请求屏障后放行close；`pg_migration.py:26-71` 专用DSN、随机schema、失败保留、不DROP。 | PG02/03及两迁移仍需真实事务验证；测试替身/字符串检查不可替代。失败时未完成的并发任务属失败现场与运行卡清理要求，不计静态通过。 |
| D8 未知树输出 | **返回值静态关闭，受D1约束。** `launcher.py:142-156` 无SUP结果的超时/丢失/异常均给 `cleanup_incomplete=True` 和 R/S/pending=None；有结果而外层清理出错则标不完整。`KeyboardInterrupt/SystemExit` 重抛，调用者须按无确认处理。 | 不能因父级SUP退出推断业务Job为0；真实故障路径 not_run。 |

04碰撞是本轮新发现的**确定夹具缺陷**，不是对产品已存在漏洞的推断。D1、D3为产品运行阻断；D4需在未来Job运行前修。首轮DB门、预扣/整树后结算、gate、Windows Job等未变源码的有条件静态结论继续有效，不提升为动态通过。

## 最终纯单元05：能够确定的边界

`unit-initial.log` 为14/14 PASS、exit 0、meta 0.8901296秒，发生在固定 venv 解释器路径修正之前；仅未受该修正影响的断言可作局部旧证据。最终 `unit-recheck.log` 为05/06/12中2过、exit 1、meta 0.6154191秒；05实际状态 `elapsed_violation_full_reservation`，最终快照**不通过**。`session.py:227-235` 表明该状态只由 `observed=(t1-t0+999999999)//1e9` 不在 `1..window` 触发；`offline_unit.py:67-88,116-123,160-168` 显示本例 FakeJob 默认非hang/非terminated，在查询时 `time.sleep(0.002)`，假账本返回 W=6，命令固定 idle。源码无本例的 monotonic monkeypatch，也不经真实Job。按通常同一单调钟和该sleep正常执行，C应为1；仅凭现成失败日志不能唯一认定时钟分辨率、未进入sleep、加载代码差异或其他原因。总命令不到1秒使 C>6 在正常同钟下不成立，但日志未记原始 t0/t1、window、job.events，不能反推确定C=0。

下一实现卡只需一次**定向、限额**诊断：在05失败断言时记录实际 `t0_ns,t1_ns,delta_ns,observed,window,job.events`、实际导入文件/hash及本例sleep前后单调值，再根据事实作一次修正/验证；勿改弱真实SUP的 `1≤C≤W`。06/12最终 PASS只证明自身替身路径；初批其余未受argv改动项按调用范围复用，不将14 PASS宣称为最终全过。

## D1 唯一最小控制结构建议

在**既有父 launcher 与 SUP 两层**内替换父级 `multiprocessing.Process/Pipe`：父方用固定解释器/固定SUP模块的 `CreateProcessW(CREATE_SUSPENDED)` 取得精确进程/线程句柄，确认受限配置、期限与必要所有权后才 Resume；结果采用长度上限、单向、可取消/可按剩余deadline完成的协议（例如 overlapped Win32 管道，父读与子写均有退出条件），所有等待、终止、确认与句柄释放共享一个绝对deadline和清理预留。父方活着时到期凭句柄终止并等待精确SUP；无法确认则未知、停止新工。`CreateProcessW` 本身的内核无限不返回不承诺硬实时；不能用后台线程包住start留下迟到创建者。**无需默认增加管理Job或第三常驻看门层**：082已批准故障模型允许父 launcher 死而 SUP 继续监督；管理Job若使worker继承后再加入业务Job，还涉及嵌套Job/句柄语义，必要性未证。父在SUP悬停且尚无Job时死亡，不得有其他主体能Resume；SUP已Resume后应自行持业务Job并完成有限停止。

实施前只核所用Windows版本的 suspended CreateProcess失败/句柄交付、父死亡时悬停进程的不可继续性、 overlapped I/O取消与进程退出关系、业务Job进程继承/最后句柄语义；如确需管理Job，再核嵌套分配限制。可观察验收为：启动前/后失败、父子IPC半帧/堵塞、父死亡、取消、期限到达均记录精确SUP身份与零迟到Resume/创建，父返回前或失败停批时给出受限剩余收尾和未知账本字段；有界模型内命令≤60秒、单Job场景≤30秒。此建议不是API实证或动态通过。

## D3 最小恢复提案与不足

**先只争取安全全额折叠W，不追溯死亡窗口的部分退款。** 同一 `(activity UUID,G)` 下，持有活动命名互斥，阻断并等旧SUP所有可创建Job的主体退出；重读DB running/G及租约，严格区分 `OpenJobObjectW` 的 `ERROR_FILE_NOT_FOUND` 与权限/其他失败。若已证明与旧窗同一 `Local` 命名空间、无迟到创建、业务Job不可breakaway/无继承额外句柄，则沿 `TASK-082-result.md:38-43` 已核的官方语义，对明确对象不存在推断其最后句柄/关联进程已终止；等旧租约到期后调用现有 `claim_lease`，由原来源→活动锁/CAS折叠R全额为S再建立新G。Open成功时仍须精确Job的 `ActiveProcesses=0`；Open其他失败一律失败关闭。claim提交丢响应后不spawn，新持锁者读回G/R再判断；取消/旧SUP晚到由原status/G/C与互斥约束，不能让旧动作改新窗。缺 t1 的旧窗只收W，不能据“对象不在”补退款。已有成功settle的响应丢失仍按原G/C幂等确认。

实现者提出的每G持久CLAIMED→ASSIGNED→ARMED→TREE_EMPTY witness、另一个owner epoch、独立长期持句柄者，**对上述全额折叠并非逐项必要，也并非自动充分**：G已是持久代次；阶段写入与Job创建不能原子跨DB/OS，见证者也会死，丢失见证时仍须上述OS对象/创建者证明；TREE_EMPTY跨重启不携带可信t1。若要在SUP死亡后仍给部分退款，才需可信、持久、与G/W/C和树空时刻绑定的证据及更强时钟/提交协议，已越批准范围，本卡不建议启动。

**尚未闭合的决定性事实是旧G的命名空间/启动纪元来源。** 当前仅有DB中的G，`Local` 名与互斥在不同登录会话可同名异物；新进程即使收到 FILE_NOT_FOUND，也不能证明旧窗原在这个会话。父/SUP尚可能迟到的D1亦须先闭合。全应用同会话重启只有在旧G同会话来源可证明时可用上段安全路径；跨登录会话失败关闭。若编排要求跨整机重启自动恢复，须先证可靠的OS启动纪元标识与“前次启动的所有受控进程已灭”事实，不能用不可靠墙钟猜测。

可供编排审阅的**最小模型扩展候选**：原 `activities` running 行只存G/R/租约 → 增 `running_owner_boot_id` 与 `running_owner_session_id` 两个随G原子写入的字段；`claim_lease` 由受信SUP提供经OS核实的启动纪元与Windows会话ID，并在同一事务内写入，下一G覆盖，G本身兼作owner epoch。旧行两字段缺失则失败关闭，绝不推定可恢复。恢复时同纪元同会话按精确Job/明确不存在判定；可信纪元已变化且经OS证实旧进程全灭，则只折叠W；同纪元异会话、标识缺失/损坏或证明提交不明均失败关闭。取消和旧SUP结算仍以原status/G/C/CAS裁决。它不增加逐阶段witness或常驻服务，也不追溯部分退款。代价是两列/claim接口/迁移及定向PG与Windows验证；082/083批准仅005一列，**此扩展尚未经批准**。关键未决是找到可靠、有官方依据且跨整机重启可比较的启动纪元来源，并证实上述Job销毁、命名空间与迟到创建条件；未核实前方案不充分，不建议直接批准具体迁移。可先实施不改模型的Open错误码区分和D1所有权补正，再由编排审此窄扩展。

## 后续最小受影响矩阵与停止

1. **先修静态阻断**：D1固定悬停SUP及双向有界IPC/总deadline，D4 04 Start事件碰撞拒绝；D3先落实同命名空间/无迟到创建的证明或提交上述窄模型变更审批，不把失败关闭宣称恢复完成。纯单元05仅先取一次最少诊断值，按观察修正。旧仓储/005无漂移，无理由全量重审。
2. **纯单元限额另卡**：05诊断/修正后精确复验05；D1新控制段的部分启动失败、半帧/发送异常、父取消/死亡、deadline及最后清理、D8未知结果；D2固定命令12若接口再改才复验。06、原取消03、claim响应丢失04及未受改动协议单元可按快照复用，变动所及再纳入。不得以旧14 PASS覆盖最终05 FAIL。
3. **Job另卡再定额度，当前启动0**：01正常早停退款、02挂死全额、03主进程先退/后代存、05同名碰撞均因统一控制器与固定入口变化需重取对象事实；04旧观察条件及控制事件变化需重验，原count0不能复用。每例≤30秒、命令≤60秒、批≤10分钟含收尾，先有精确身份/创建时间/Job/独立deadline再Resume；任一归属或清理未知即停批。现脚本04碰撞缺口未修，且D1/D3未闭合，**当前不能启动**。
4. **PG另卡再定额度，当前连接0**：只执行 `PGMigrationTests.test_pg_migration_01_empty_table_adds_only_closed_column`、`test_pg_migration_02_nonempty_table_rolls_back_whole_005`、`PGCloseTests.test_pg01_close_settle_and_old_gc_does_not_touch_new_window`、`test_pg02_closed_gate_rejects_admit_mark_but_records_outcomes`、`test_pg03_close_commits_before_concurrent_admit_and_mark`、`test_pg04_cancel_closes_gate_and_old_dispatched_unknown_converges`；专用DSN缺失skip、成功按UUID/FK清理、schema删除另卡授权、失败保留定位。受新门影响的旧测试只按首轮矩阵选取；若D3新增持久模型，则迁移/claim/恢复再另列定向PG，不混入此冻结批。

本轮只读产品、测试、迁移和旧证据；只写本结果置顶及 `Ndocu/evidence/task-084/review-02/` 初判/哈希。未运行代码、AST、compile、import、测试、Job、PG、Docker、网络、安装或模型；未读真实配置。Job/PG可运行门均**不通过**，上述清单是编排后续卡的最小范围，非本窗口运行授权。

---

## 历史：TASK-084 首轮独立审计原文
# TASK-084 / R-078 — 独立代码与运行控制审查结果

**结论：不通过进入定向Windows Job运行门；PG夹具目前也不具备按本卡隔离要求执行的条件。** 005和仓储关闭门的主要静态事务路径可进入修正后的定向PG验证；但启动器硬截止、内部命令到受控worker的绑定、失败后恢复及测试控制器存在确定缺口。本文是最终候选的限定代码审计，不是动态通过、M-1或STEP008验收。编排应先处理下列确定缺陷，再按最小矩阵另卡给运行预算；本审计没有恢复083冻结额度。

## 身份、范围与快照

本次是新隔离审计窗口；本会话可见身份为Codex/GPT-6，具体Sol后缀不可核实，未参与082诊断转083实现或083离线补足，未读实现聊天及`Ndocu/results/TASK-083-result.md`。按指定顺序先读根`AGENTS.md`、公共`docu/AGENTS.MD`、082批准合同末尾用户“批准”、需求v1.1的NFR-002/003与SEC-002原文、083原完整合同及当前离线停止边界；再读七个worker文件、仓储/导出、005、三份指定测试、task083全部六个实际Python夹具及必要gateway/runtime/001—004片段。源码初判先写入`Ndocu/evidence/task-084/independent-initial.md`，此后才读指定原始日志、清理记录、静态日志及两个时期哈希清单。另接触了项目记忆注册表中一条**规划阶段避免过度验证的偏好**，未用它判断083实现，也未读历史实现摘要。没有意外读取实现自评。

`Ndocu/evidence/task-083/offline-repair-01/final-hashes.txt`所列16文件，加任务卡补充的`activities/__init__.py`、`test_activity_time_budget.py`、`test_activity_dispatch_close.py`，现场逐文件SHA256复算19/19一致；实际值见`Ndocu/evidence/task-084/hashes.txt`。仓储`929320…5B20`、005`26B71A…BEB`与冻结相同。新文件经实际文件枚举纳入，没有依赖Git差异列出未跟踪文件。有限差异及证据时序见`Ndocu/evidence/task-084/diff-scope.md`。本轮没有运行代码（含AST/compile/import/单元）、进程、Job、PG、Docker、网络或真实配置，也没有修改产品、测试、迁移、正式文档、公共规则、旧证据或Git。

## 八项判定

| 项 | 代码层判定 | 依据与边界 |
| --- | --- | --- |
| 1 DB门/结算 | **有条件通过** | `005:2-16`先ACCESS EXCLUSIVE锁、判空、ALTER同一事务；默认false并不单独授资格。`repository.py:348-407,429-462,763-904`显示claim新代次唯一开门，close身份/代次校验、同代次幂等，admit/mark拒关门；`957-981`及`585-729`未因共用helper误挡原合法结果/UNKNOWN收敛。`514-550`首次settle要求closed，最近旧G/C确认先于当前状态检查且不改新窗。cancel/过期折叠无部分退款。真实PG与事务并发未运行；PG02测试自身有静态错误，见D5。 |
| 2 本地发送门 | **不通过当前整条内部路径保证** | `gate.py:35-60`单个令牌覆盖`gateway.call`全部await，先置closed再排空且不可重开；`gateway.py:115-162,375-401`确有admit→mark→send→record调用链。`worker_main.py:15-26`只对被注入的受控任务有效；`command.py:9-27`及`launcher.py:29-59`允许任意存在的绝对可执行文件/参数，SUP只执行命令，未验证它必走`run_controlled_worker`。合成01换成controlled_fast不代表所有被允许命令均受门控。未来真实供应商/HTTP未授权接线不在本结论中。 |
| 3 预扣/时间/退款 | **有条件通过** | `session.py:183-259`把t0置于claim前，拿到`lease.window_seconds`才建Job；partial/不明确claim不spawn，t1在`wait_empty_until`为真后，成功且`1≤ceil≤W_eff`才关门/settle，失败或超窗保留R，结果字段区分S/R/待折叠。`launcher.py:52-53`管理期限另计；不应解释为任意挂死下硬实时。清理/响应丢失的实际安全性仍依赖D1、D3和动态证据。 |
| 4 启动器硬截止 | **不通过** | 截止在创建前固定，但`launcher.py:63`的`Process.start()`没有独立预算约束；`67-75,90-108`超时后两次固定cleanup join及异常/finally操作可越过同一deadline；`81-83`的管道poll/recv无剩余预算封顶。SUP内同步Win32在专用进程而非应用事件循环，DB的`wait_for`有限，但父级不能保证自身命令硬截止。 |
| 5 Windows归属/恢复 | **不通过完整恢复；保守停止有条件通过** | `windows_job.py:152-244,246-335`按活动UUID/G命名、碰撞拒绝、悬停Assign后Resume、禁止句柄继承/未开breakaway、确切Job查询ActiveProcesses；Open失败被拒绝而非算0。`session.py:152-181`本地锁加命名互斥并拒未知旧树。可是已claim未settle而Job句柄在清理后消失时，DB仍running/R；下次必走`open_existing`失败，无法到claim原保守折叠，见D3。默认DACL/Local会话边界、最后句柄及旧SUP竞态尚需有控制的Windows实证，不能把旧count0当证明。 |
| 6 收尾/结果 | **不通过完整结果语义** | `session.py:262-313`在finally后构造结果，逐项捕获Job终止、查询、句柄、互斥释放异常；未证树空不退款，`cleanup_incomplete`不会报clean，取消附诊断后重新抛出。成功结算前先关Job句柄；若结算后互斥释放失败，状态明确`settled_cleanup_error`。但外层launcher在未证Job树退出时可返回cleanup_incomplete=False，见D8；冻结后纯单元取消断言与源码不符，见D6。 |
| 7 Job控制器 | **不通过可运行门** | 新04控制器`job_control.py:18-105`在Resume前取得独立20秒截止、Job/G/runTag、进程句柄/创建时间；`95-98`在SUP退出前释放观察Job句柄，未用夹具保活掩盖最后句柄。`fixture.py:30-58`以base解释器和venv环境转发，事件双向等待有界。其余01/02/03/05仍由`WindowsJobTests`直接运行，缺少同等独立控制者；默认unittest在归属/清理失败后仍继续后续场景。`test_worker_session.py:150-196`五场景合并命令也没有≤60秒命令总截止。 |
| 8 PG夹具/回归 | **不通过可运行门** | `pg_migration.py:15-37`用专用DSN、随机schema及001—005顺序，缺DSN skip；但`pg_close.py:24-56`只用原DSN，没有随机schema或传给仓储/清理连接的`search_path`，并假设表已存在。PG02在预留态记录NOT_SENT与现有仓储契约冲突；PG03未精确控制提交顺序；两夹具失败时都删除现场。见D5/D7。替身只证流程，不作PG/OS结论。 |

## 确定缺陷及最小修复

**D1｜运行控制阻断。** 子端管道send、父端poll/recv及异常/finally也未统一绑定剩余预算；Process.start若在创建OS子进程后抛错，started仍为False，现有清理分支会跳过该子进程。`backend/app/worker/launcher.py:52-108`：调用`Process.start()`卡在spawn/pickle/解释器启动时，deadline虽已固定却没有持对象句柄的上层控制者；即使正常返回后超时，`terminate→join(cleanup_seconds)→kill→join(cleanup_seconds)`也能在总截止后再增加两段等待。异常时`is_alive`/finally亦无收尾界限。影响是场景/命令可超过硬截止，父进程可能无法按时诊断或停止。最小修复为在启动前建立独立、可限时控制的精确SUP进程归属和外层截止，所有父级等待/清理使用同一剩余预算，并在无法确证停止时报告unknown且中止后续场景；需覆盖启动/发送/接收异常，而非再转移一个无限回调。

**D2｜受控入口可绕门。** `backend/app/worker/command.py:9-27`、`launcher.py:29-59`与`worker_main.py:15-26`：传入已有绝对路径如普通Python和任意`-c`参数即能在已认领Job里运行未调用门的程序；路径/长度校验不证明经过`run_controlled_worker`。影响是本切片对该入口的受控发送门不能覆盖任意受信调用者误用；并非声称模型目前能传此参数。最小修复是固定内部worker入口/受限命令协议并把获准任务注入绑定到门控gateway；合成场景另用显式测试专用入口。若架构只把调用者当完全可信，也须在接口中落实可检验的边界，不以注释代替。

**D3｜正常失败后不可恢复。** `backend/app/worker/session.py:161-181,193-215,230-239,272-306`配合`windows_job.py:236-244`：claim已提交后遇partial窗口、worker非零退出或结算前DB失败，最终清理关闭Job句柄而DB仍`running`、R>0；下一次`inspect_window`看到running，`OpenJobObjectW`因对象已消失失败，代码不走`claim_lease`，同一活动每次重启都失败关闭。影响是保守预扣可永久挂住，不能称跨恢复完成；当前保守拒新工作是安全的一面。最小修复应区分“无法证旧树”与“有可信的整树结束证据但Job对象已消失”，设计可持久/可验证的恢复证明及有限折叠路径；不得把Open失败、主进程退出或count0筛选直接当证据。此修复可能触及原合同授权边界，须由编排裁定。

**D4｜Job测试控制不足。** `backend/tests/test_worker_session.py:142-196`：01/02的SUP直接在`IsolatedAsyncioTestCase`中做阻塞Win32调用，03/05无独立控制者；unittest失败后继续下例。初批命令实际141.328秒，超过原每命令60秒，01/04失败后05仍执行。04新控制器仅覆盖04。最小修复是每个要复验的Job场景先由独立控制器握确切对象/创建时间/截止，再Resume；每例单独硬截止，失败归属/清理不明即停止批次，保留≤60秒命令和≤30秒场景预算。先静态核对再另卡批准运行。

**D5｜PG02按现有合同必失败。** `backend/tests/fixtures/task083/pg_close.py:106-122`在close后对仍为`reserved`的`reserved`凭证调用`record_outcome(...NOT_SENT)`；`backend/app/activities/repository.py:966-970`对reserved只允许UNKNOWN，故即使PG已准备好也会在118行抛`AdmissionDenied`，到不了三状态断言。最小修复是按既有合法收敛规则把该凭证记UNKNOWN并调整断言，或若确要改变原结果语义则另走批准；本卡不重审旧079行为。

**D6｜最终纯单元取消断言与源码矛盾。** `backend/tests/fixtures/task083/offline_unit.py:145-152`把claim抛`CancelledError`后的`(reserved_seconds, settled_seconds)`断言为`(0,0)`；`backend/app/worker/session.py:264-271`在`claim_attempted and lease is None`时明确设二者为`None`，这是正确保守未知。该最终快照用例静态必失败。最小修复为断言`(None,None)`并保留取消重新抛出、清理完整性检查；补最终快照单项运行。

**D7｜PG隔离与并发夹具不能提供声称证据。** `backend/tests/fixtures/task083/pg_close.py:24-56,124-148`未创建随机schema，原DSN直接用于仓储、读行和FK清理；迁移夹具自己的schema运行完立即DROP，不能为close夹具准备表。PG03在来源锁内发出admit/mark后只`await asyncio.sleep(0)`即release，不能保证close提交先于两者获得锁，故期望拒绝有竞态。`pg_close.py:41-49`及`pg_migration.py:26-37`在失败时照样清理/删除合成现场，无法保留失败证据。最小修复：每个PG close用例自建随机schema、迁移到005，明确把schema限定`search_path`传给仓储及所有辅助连接；失败保留schema/合成ID供定向复核，成功才FK顺序清理；并发用barrier/锁观测/提交确认控制顺序，至少覆盖close先提交及admit/mark先取得资格的交错。

**D8｜父启动器把未知树报成清理完整。** `backend/app/worker/launcher.py:68-102`：deadline到时终止SUP，代码明言父方不能证明旧Job树为空，但只要SUP进程不再存活，`manager_timeout_unconfirmed`的`cleanup_incomplete`即为False；SUP丢失分支也沿用默认False。依赖该字段的测试控制器会误以为收尾完成。最小修复：没有确切Job整树零正证据时设`cleanup_incomplete=True`并停止批次；SUP退出码不能代替树证据。

## 条件风险与动态缺证

- `windows_job.py:213,240-244,254-269,297-335`用默认DACL、`Local`命名、`bInheritHandles=False`和无breakaway标志，静态上符合本地会话设计；默认DACL实际访问、venv转发器子进程归属、Assign失败时`TerminateProcess`返回未检查及最后句柄行为需要OS证据。没有据此认定当前会影响其他进程；Open失败的安全处理是保守拒绝。
- `session.py:105-112,240-252`用`wait_for`包DB事务；提交响应丢失可同G/W/C重试一次，但取消与数据库提交的实际先后仍需PG取证。未知不spawn/不退款的静态路径成立。
- `gate.py:47-60`覆盖await的gateway调用；可信业务回调若私自保留原gateway或创建不经门的任务，不受此包装器约束。此边界应随D2固定内部入口验证，不能拿离线手写事件字符串当真实gateway或供应商证据。
- Windows Job总计5例原始日志仅有02/03/05局部通过；02/03/05的源码/身份日志/命令接口后来改变，旧记录只可作旧实现行为线索。旧04失败以及`owned_python_process_count=0`均不构成新04或旧树空的正证据。`static.log`和05单项复检也发生在后续源码变动前，适用范围见`diff-scope.md`。

## 后续最小验证矩阵（建议，非本卡运行授权）

1. **先修D1、D2、D4—D8；D3交编排确认恢复证明是否触及批准模型，再定最小修复。** 修完再冻结新哈希。当前Job场景及命令硬截止/收尾可控性**不足**；不得沿旧083额度启动Job。PG运行准备**不足**；不可按当前`pg_close.py`运行。005未在本审计执行。
2. **最终快照纯单元**：至少`OfflineRepairTests.test_03_cancellation_preserves_diagnostic_and_cleans_owner`（D6），`test_05_early_success_uses_tree_zero_close_then_same_g_settle_retry`（旧复检后session改动），`LauncherUnitTests.test_08_fake_process_timeout_terminates_exact_owner_without_charge_claim`及新增start卡住/recv异常/截止后清理用例（D1），`ProtocolUnitTests.test_claim_response_lost_and_partial_window_never_spawn`、`test_unknown_old_job_fails_before_claim`（D2/D3），`GateTests.test_gate_closure_waits_for_marked_before_send_and_never_reopens`与`OfflineRepairTests.test_07_controlled_worker_gateway_chain_drains_marked_call`（D2改动时）。仓储替身`CloseGateRepositoryTests`01—03及time-budget 01/02/06/08只在相应仓储/门代码改动时定向复检；替身不替代PG。
3. **Job01—05逐项**：01原失败且改变受控命令/结算，必须重验；02旧PASS只保留“旧实现杀挂死且未退款”线索，session清理及launcher变动影响最终状态，定向重验；03旧PASS只保留主退后代存在的旧API线索，身份/截止与控制器变动要求重验；04原失败且新控制器未运行，必须重验，尤其观察Job句柄须在退出事件前关闭；05旧PASS可复用同名碰撞拒绝的旧局部事实，但最终身份日志/安全停止批次未验证，如D2/D4改动影响Job创建控制，再定向重验，否则不机械重复。每个实际运行场景先握独立对象/截止，单场景≤30秒、命令≤60秒、批总窗≤10分钟并预留≤60秒收尾；一例清理/归属不明立即停。编排另卡核预算和实际命令，不能从本文推定已批准复跑全部。
4. **PG测试ID**：修后`PGMigrationTests.test_pg_migration_01_empty_table_adds_only_closed_column`、`test_pg_migration_02_nonempty_table_rolls_back_whole_005`；`PGCloseTests.test_pg01_close_settle_and_old_gc_does_not_touch_new_window`、`test_pg02_closed_gate_rejects_admit_mark_but_records_outcomes`、`test_pg03_close_commits_before_concurrent_admit_and_mark`、`test_pg04_cancel_closes_gate_and_old_dispatched_unknown_converges`。D3若改仓储恢复，增加针对有正证据旧树与身份不明旧树的实际事务用例。旧受影响选择：`ActivityTimeBudgetPostgresTests`的01/02/06/08（settle前置与新窗/折叠）、`ActivityLedgerPostgresTests`的01/05/06/07及`ActivityRecoveryPostgresTests`的01/03/05（admit/mark/取消/UNKNOWN），只在实际修改触达其断言时运行对应ID，不把079原22例全部重测。专用DSN缺失应明确skip；不得指向用户库或凭替身宣称PG通过。

当前独立安全结论仅为**已审静态切片不能放行运行控制**。官方Windows事实未在本卡新取网络证据；若修复依赖新的API语义，应沿082原官方链接核对精确对象、访问权与最后句柄行为，并将需要的新OS取证列入后续定向Job卡。所有运行、真实PG与产品接线均为`not_run`。

