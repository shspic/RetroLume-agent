# TASK-090 / R-084 独立增强审计

## A. 初审结论（2026-09-30，Asia/Shanghai）

**本次暂不签署 TASK090 切片通过。** 范围事务、父成果重新准入、IPC及成功链没有发现阻断安全缺陷；新增服务的两条确定失败分类路径不符合任务卡3D，另有新离线用例的历史源码绑定缺口。下列发现已一次合并，修正后只确认这些增量；不重审未变G3/D3、不重跑已充分的22项PG和1例Windows。

| 最终结论维度 | 初审判断 |
|---|---|
| 产品合同 | 部分确定通过；A1、A2须修正，故尚不满足整张090卡 |
| 动态证据适用 | real-03最终冻结版本的PG22和Windows1成立；早期离线须按下文限定，E1待补充 |
| 执行合规 | 在所给原始记录及runner范围内通过；3/3真实入口已用尽，不得再启动真实资源 |
| 资源最终记录 | 最后记录Running=false、Pid=0、外层树零/句柄关闭，业务树零、cleanup_incomplete=false；这是批次结束时记录，不是本次实时探测 |

### 独立性及输入

审计者：`/root/task090_audit`，全新隔离会话，未参与090实现。只接收原目标、卡/设计/前置批准边界、冻结源码及差异、原始证据；未读取主执行聊天、思考、自评或记忆，也未读取TASK-090-result.md。报告由本审计者本人判断、写入；不修改产品、测试、runner和正式docu。

只读辅助：`/root/task090_audit/evidence_read`，同样以隔离上下文创建，仅核对任务卡5/6节、原始manifest/log/hash及相应runner的计数、资源、加载和收尾记录；未运行测试、未写文件，不签独立报告。主审自行审查产品合同、实际测试断言、核心原始日志、资源manifest及来源指纹，未以辅助摘要替代产品审查。

已读根AGENTS.md及公共规则 `D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD`（本卡采用2026-09-28 14:08:37.3969855 +08:00版本）。执行者角色不加载编排全阶段规则。原用户附件与 `Ndocu/tasks/TASK-090.md` 规范换行后全文一致。设计为TASK-089-next-contract；既有G3只接受TASK-088-089-final-acceptance的明确批准边界。

本次只进行文件读取、SHA256及内存文本比较，没有执行产品/测试、连接数据库、调用Docker或启动受测资源。普通工具因sandbox helper权限故障未能启动，随后走平台require_escalated审批执行所授权的只读及审计报告写入，无绕审批。

## B. 确定缺陷（合并一次交回）

### A1 / P2：已确认取消被服务误报为监督未知

位置：`backend/app/activities/service.py:123-131`；直接传播：`backend/app/worker/session.py:196-199`及`395-409`。

可确定的顺序：服务先读父P为COMMITTED_CURRENT，随后另一调用取消活动；SUP的inspect_window读到cancelled，明确返回 `SessionOutcome.state="cancelled"`、无模型回执、新Q未生成。服务读Q得到no_operation，128行只特判budget_exhausted，遂返回 `ContinuationOutcome.status="supervision_unknown"`，丢掉已经确定的取消分类。

这不是数据库或旧树未知；底层仍停止新执行、未发现多发或退款。缺陷在新增业务返回合同，违反3D要求区分cancelled与supervision_unknown，并使调用方无法按顶层状态识别确定的停止原因。现有V5用例在服务读取父P之前已经取消，因此只覆盖服务早退，不覆盖此真实竞争窗口。

关闭标准：保留business/supervision/settlement三个事实的独立含义，同时正确传递已确认取消；对“父已读、SUP才确认取消”的服务分支有有辨别力的离线证据，确认Q不重发。无需增加PG/Windows启动。

### A2 / P2：可提前确定的配置冲突被服务归为监督未知

位置：`backend/app/activities/service.py:106-116`；直接传播：`backend/app/worker/one_call.py:230-234`。

`continue_from_result`只核config/service的类型及OneCallInput编码，未覆盖one_call执行前的跨配置限制。例如合法SessionConfig的request_timeout_seconds=10，与合法ModelServiceConfig的timeout_seconds=30（其他字段满足内部64KiB限制）组合时，run_one_call在调用launcher之前确定抛ValueError；request_timeout_seconds>120也是同类。服务把这些已知无监督副作用的输入错误统一捕获为supervision_unknown。

该路径不会启动SUP或发模型，但违反3D中invalid_input与supervision_unknown的区分。不能把这类配置错误描述为“执行状态可能未知”。这与真正监督/数据库异常返回unknown的保守策略不同，后者应继续保持。

关闭标准：已知配置前置条件在正确边界明确拒绝，返回invalid_input或任务合同认可的确定配置错误；用离线断言证明在监督入口之前拒绝，同时保留真正监督异常的unknown且不重发语义。不提供实现补丁，技术修法交主执行。

## C. 证据不足

### E1：新离线用例的历史测试源码缺少可核对的快照

四批离线各自有运行日志及加载SHA256，均能证明所记录快照的测试通过；但不能把63次历史执行整体写成“最终版本63项通过”。offline-01/02存在多个产品文件后续变化；offline-03的contracts.py、service.py仍为旧hash；offline-04产品加载hash已全部等于最终版，但其 `backend/tests/test_activity_continuation.py` 实际加载hash为 `24d3007e63a006b0ef352fc7554544bdb2dca4057823b3b9d00f7560f53a6c14`，最终文件是 `3f65aea12b3c35b5b94ad4b13fcf0ab170fcbd4ff0cd13b02f880e10e7537633`。

原始loaded-source-bytes.json保存的是hash，不是源码字节；目前提供的pre/也没有新增文件的中间版本。因而主审能确认offline-04运行了最终产品代码及列名的3个方法，但不能独立确认最终所见测试断言与当时执行的3个方法完全一致。该限制尤其影响新增严格引用校验、异步取消等待及超长早拒分支的精确适用性，不反向否定已有G3批准，也不否定real-03最终源码上的新PG/Windows证据。

最小关闭方式：提供能匹配原hash的历史源码，使审计者比较实际选中方法/公共夹具；或在A1/A2必要离线验证中合并运行受影响的新服务/引用用例并绑定最终源码。无需因整文件hash变化重跑无关旧测试，更不能重启真实资源。旧轮原始文件保留，不能改写成最终hash。

## D. 确定通过及依据

| 合同项 | 源码判断与原始证据 |
|---|---|
| G4完整替换/CAS/空集合/上界 | repository.py的_normalize_scope、inspect_scope、revise_scope：严格快照项、128项/去重、规范集合；旧新来源并集UUID排序加锁→活动锁→复读提示→CAS/状态/新来源校验；同集合无UPDATE，变更原子+1，上界失败。real-03的V1两例验证xmin无写、预算列不变、空范围拒claim、响应丢失后read_scope不重复推进 |
| 锁后复核 | _verify_scope_hint比较source/version/revision完整集合；claim、inspect_window、begin_window_close、settle、cancel、两类recover、admit和_locked_operation均在活动锁后调用；变化明确scope_conflict、事务回滚，没有活动锁后补来源锁。V2不相交集合先提交例及旧事务先锁例有实际两连接屏障，stdout含pg_blocking_pids观察；资料save竞争沿真实权威方法 |
| 取消/必要收尾不受来源有效性阻断 | begin_window_close、settle、cancel、recover_unknown/recover_obsolete仅获取来源锁，不以_lock_sources返回的有效性为收尾门槛。V2空集合关门/结算、过期来源取消一次折叠、重复取消及cancel后settle拒绝覆盖直接风险；旧事务范围冲突按显式冲突失败，不改变总期限 |
| 重新准入及原子预算 | admit在来源/活动及范围复核后按operation_id锁父/新键；父须received、本活动、本scope、结果admission/G/scope完整绑定、规范payload/hash与引用一致，非空来源及当前租约/门/预算仍有效；所有校验先于预留与INSERT，事务原子。V3包含假hash、跨活动、无正文、损坏绑定/实际payload、读后scope/source变化；实际双gateway同Q仅一次发送，requests_reserved包含P后为2 |
| 准入后的范围变化 | mark_dispatch_started及record_outcome沿_locked_operation重新核资格。V4通过真正revise_scope清空范围，Q拒dispatch、已在途旧scope拒新正文，预留不退，unknown诊断仍可收敛 |
| 只读恢复/预算纪律 | service read/resume不调用监督；同新键有任何已知记录或不可读结果均不调用第二次；取消历史只读，父失效不消费。V5真实PG涵盖取消历史/unknown、提交丢响应后重启同键读取、次数与时间耗尽仍读历史且不复活账本 |
| 引用与IPC | ResultConsumptionRef严格UUID/操作键/正revision/小写64hex；旧无引用to_wire排除None，旧extra=forbid schema拒新字段；launcher、SUP、session、worker发送/解码逐跳活动绑定。gateway显式投影不含引用，工具为空；引用不是恶意同用户进程能力凭证 |
| 低信任正文和有界异步边界 | service将规范父value置assistant、followup置user，没有system提升、截断或自动摘要。唯一to_thread监督调用由shield等待，调用方取消先等线程自身有界结束才传播；此源码分支成立，动态精确断言适用受E1限制 |
| 最小真实成功链 | real-03单Windows场景经真实PG/launcher/SUP/worker主体，transport唯一合成；worker原件记录transport_sends=1、parent_low_trust_verified=true、reference_excluded_verified=true。内协议3，receipt/database/read的hash均为07642a33…5ca7b；外帧2由真实launcher严格_decode_outcome成功解码，未改协议主体 |
| 收尾顺序 | SUP12036原始trace由SUP采集，树等待及成功出口后经过job.close、begin_window_close、settle；原始业务outcome树零、R=0、S加1、door=true、无cleanup错误；win_chain还检查业务Job名不可打开。外层Job/截止独立于受测逻辑 |

运行原始计数：offline-01=35、02=8、03=17、04=3，共63次执行、40个唯一test ID；均0 skip/failure/error。real-03为22个PG方法（18个090新方法+4个直接受影响回归），0 skip/failure/error，退出0；另1个Windows场景退出0，不混入unittest数量。总计85次unittest执行、62个唯一test ID，另Windows1。这是执行计数，不冒充所有历史离线均绑定最终版本。

已审查新测试的断言具有实际区分力：事务no-op看xmin；并发不是sleep猜序；父/新键竞态看transport次数及账本；损坏payload重算校验；Windowstransport断言实际provider请求中的角色/内容和内部引用排除，未替换生产准入、持久提交或监督结果函数。

## E. 证据冻结与执行合规

主审自行复算 `final-hashes.json` 71项全部匹配当前；`pre-hashes.json` 62项全部匹配pre原件。已有文件实际变化仅9个许可产品文件，另新增service及任务090测试/夹具；001—007、材料权威主体、gate/windows_job/supervisor_ipc/transport、旧测试/夹具与正式docu快照未变。只读复算记录为 `Ndocu/evidence/task-090/audit/initial-source-check.json`。real-03的before/post 60项及实际PG/parent/SUP/worker加载hash与当前相符。未根据final-applicability主评直接签字。

真实入口1为精确CID inspect失败（manifest错误保留、未启动）；入口2为独立只读诊断（引擎命名管道缺失、未启动，保守计2秒）；入口3才启动获准CID并完成PG+Windows。账本没有把第二独立入口藏进已结束的第一owner。按原件算术，真实20.421秒（含5秒启动保守扣账）、离线12.858秒（含前提失败/静态检查/四次启动保守扣账），均低于卡内时限，但真实次数3/3已用尽；Windows1/6。首失败exit=null/inspect exit1与末批exit0分开保留。

唯一CID `e49d3acc3c1be13d670af68bca2b082fea4faeeb9b9babe69df7f1d3941696a4`、名称、镜像、1 CPU/512MiB/pids128/restart=no/privileged=false符合卡；Mounts仅指定named volume（Type/Name/Destination/RW齐全），5432绑定127.0.0.1:55441。末批专用库/角色初始均不存在且sessions/memberships=0；runner只创建090专用库/角色，口令经stdin和owner/受控进程环境，不读旧Env，不把密码/DSN写argv/日志。新容器/卷为0，没有替代资源证据。

末批manifest的外层PID31584及创建时间、挂Job→Resume→控制句柄关闭记录齐全；final_resource明确Running=false/Pid0。保留数据库/角色/容器/卷，无删除。审计期间不再次核Docker现状，不以记录时状态保证后续环境无人改变。

## F. 非阻断观察与边界

- 服务read_scope以None明确表示缺活动，并以脱敏异常区分暂不可读；没有伪造revision。本报告按语义视为not-found，未把返回类型拼写差异制造为阻断。
- 范围变化没有即时杀在途请求的承诺；最后资格提交后可能已在途，旧scope新正文受拒。引用保持内部受信边界，没有宣称可抗恶意同用户进程。
- Windows bootstrap实际Python PID与监督主启动PID不同，不能把二者当同一个身份；当前入口固定.venv解释器且整Job树受约束，树零/Job销毁证据不依赖PID相等。未据此重开未变Windows机制审计。
- 未验证真实provider、用户库、公开HTTP/UI、G5、STEP008整体或发布；这些本就不在090切片。已有G3/D3批准不被本轮服务分类缺陷反向否定。

本报告及审计记录的CHANGE登记交编排按其权限完成。后续仅在本文件追加增量结论，保留A节初审历史和原始证据；主执行不得代写签字。A1/A2/E1关闭前，不能以本报告宣布090完成。

## G. 第一轮合并修正增量终审

2026-09-30，Asia/Shanghai。由原审计者 `/root/task090_audit` 本人接续，未更换审计身份、重置预算或增加修复轮次。A至F为真实初审历史，原样保留；当前结论以本节为准。

结论为通过。A1、A2已关闭，E1已由最终版本上的定向离线证据关闭。本次没有发现新增阻断项，TASK090/R084批准切片可供编排验收；本审计不代改正式任务状态，也不代表G5、STEP006/008整体、真实provider或发布通过。

### G1. 增量对象及规则阶段

只审查incremental-01中两项差异、匹配的pre/final源码、offline-05原始记录及它们对已审路径的直接影响。主审自行复算全部67项backend冻结指纹，与当前文件完全一致；相对初审仅service.py及test_activity_continuation.py变化。两份保存diff与从pre/final源码实际生成的差异完全相同，快照hash与real-03的前版本衔接成立。PG测试类的AST完整不变，repository、IPC、runner和其他后端文件未变。

最终service.py SHA256为 `977f14c73f8c5533eebb7d34bba82de55a14ee5e9e314f903c2a0697cf5cbe32`；最终test_activity_continuation.py为 `472eb7a9cf2deb848fdc1029ec01ce12dc501791545b54ee8ed0ff8268d6c9c9`。独立复算、实际diff及原始计数记录保存在 `Ndocu/evidence/task-090/audit/incremental-01-source-evidence-check.json`。

用户在接续时明确替换入口为V4 task_model。主审已实际补读公共 `项目开发提示词V4/DocuS/AGENTS.MD`，版本V4.0 CHG-0003，hash为 `e7e6b1a806d80a19294c5d6b95f93c7a004dc254029c7c01256910df479d4514`。本轮剩余收尾适用此版本；此前实现、验证和初审仍依当时有效V3合同，不追认当时已读V4。新规则不扩大产品/资源授权，不要求强制搬迁历史材料，故沿用原Ndocu报告和证据位置。本次不承担全局编排或项目最终裁定，未另加载WORK/全部阶段。

AGENTS.md当前hash为 `1e3fb2f1dfb7404260c81e8bc6931fa704d88375a78f6826da4cc8f0c70ee1b2`，确与初审冻结入口不同。文件改写者无法由本任务确定；用户后续明确规则替换已提供当前采用依据。docu/PROJECT_ARCHITECTURE.MD也有外部字节漂移，主审复算旧hash `048b8fc8…bf0c10a9c`、当前hash `1c79dbeb…7e0a48a33`，按UTF-8去BOM及通用换行读取后的文本完全相同。该变化不包含架构文字变化，写入者未知。两项外部变化均保留，不作为090产品改动，不回滚，不改写旧冻结清单来掩盖差异。

初次增量读取曾被平台自动审批额度错误拦截，动作未执行；本次恢复后同一require_escalated审批路径已成功。未绕过审批，也未以新窗口重置限制。审计自身只做文件、hash、AST和日志核对，没有运行测试或接触Docker/数据库资源。

### G2. 三项发现关闭依据

A1确定通过。service只在business为no_operation/unresolved时，把已确定的supervision.state cancelled或budget_exhausted保留下来，其余监督未知仍返回supervision_unknown。新增 `test_cancel_after_parent_read_preserves_confirmed_supervision` 明确断言调用顺序先读Q/P、SUP返回取消后只再读Q，监督只调用一次，顶层cancelled且business仍no_operation，并保留同一个supervision对象与原settlement字段。该测试定位新增服务适配边界，不冒充新的PG取消测试；真实取消纪律仍复用已通过证据。

A2确定通过。service在启动监督线程前显式拒绝request_timeout_seconds大于120及service.timeout_seconds大于监督请求时限。新增 `test_known_timeout_conflicts_reject_before_supervision` 对这两种合法类型但组合无效的参数分别断言invalid_input、监督未调用、无虚构监督/结算事实。新增 `test_unexpected_supervision_error_remains_unknown_no_resend` 用真正来自监督调用的ValueError反例，证明异常没有被一概重分类为输入错误，仍unknown、只调用一次，之后resume也不重发。

E1确定关闭。offline-05执行当前完整ContinuationOfflineTests共11个方法，原始stderr逐项ok且统计11/0skip/0failure/0error，manifest退出0。它覆盖初审E1提及的严格引用类型、异步取消等待线程结束、超长早拒三个方法，以及活动绑定、旧请求兼容/旧端拒新字段、provider投影、工具拒绝、只读失败和本轮三项新反例。as-run与post相等，实际加载的23项源码hash全部与当前文件一致；两份final源码同时匹配实际加载hash，现已能核查实际执行断言，不再依赖缺失的中间源码。

offline-05原始监督记录包含PID26216、创建时间134352069582715588、先挂外层Job后Resume、tree_zero=true、handles_closed=true，单批0.968秒。本审计没有重跑这些用例。

### G3. 已有动态证据为何仍适用

real-03的PG22方法保留适用。其仓储与所有直接依赖未变；ContinuationPostgresTests整体AST与实际执行版本相同。测试文件只新增离线方法和离线helper，没有修改PG方法、夹具或运行控制。

real-03的一例Windows成功接线保留适用。实际成功样本service.timeout_seconds为0.5、SessionConfig.request_timeout_seconds为2，新前置条件均为假；成功业务返回committed_current，不进入修改的no_operation/unresolved状态分类分支。因此本轮两个service改动均不改变该成功样本的执行路径；请求组装、引用、监督线程等待、仓储、IPC、transport替身及收尾主体均未变。该判断建立在已保存的真实成功证据与精确最小差异上，不声称重新运行过新hash的Windows场景，也不为追求整文件hash相同再次启动资源。

主审从原始stderr逐方法块提取test ID和终止ok，兼容诊断日志插入后另行输出ok的情况。offline-01至05分别为35、8、17、3、11次，共74个历史执行实例、43个唯一方法；real-03为22个PG方法，因此共96个unittest历史执行实例、65个唯一test ID，Windows另列1场景。各批均无skip/failure/error。这里的96是历史实例总数，不是96项互异最终版本测试；早批适用性继续服从初审和本节的具体边界。汇总索引先前的解析漏项没有改变原始日志或case结果。

### G4. 四维最终结论与停止边界

产品合同通过。范围CAS/锁序、取消及收尾、父成果重新准入/原子预算、IPC内部引用、低信任输入、未知不重发及异步线程收尾沿初审确定通过项复用；A1/A2两项服务分类缺陷经本轮修正及反例证据关闭，没有新发现。

动态证据适用通过。最终离线11方法绑定当前完整源码，关闭E1；PG22和Windows1按上节精确影响分析继续适用。未验证真实外部provider、用户数据库、公开HTTP/UI或整体发布，均在本卡范围之外。

执行合规通过。真实账仍为3/3入口、累计20.421秒、Windows1/6，增量没有追加真实启动、probe或替代资源。离线累计14.826秒，包含本轮0.968秒及1秒启动保守扣账；原先失败和诊断记录继续保留。预算没有因窗口恢复、规则更新或修正而清零。不得再依本卡启动真实资源。

资源最终记录通过。仍引用real-03最后记录的精确CID Running=false/Pid0、外层树零及句柄关闭、业务树零及cleanup_incomplete=false；没有新资源动作，所以不制造新的现场探测记录，也不把历史记录表述成实时环境保证。容器/卷/专用库/角色保留，没有删除。

当前分类为确定通过；开放确定缺陷0，阻断证据不足0。非阻断观察仍为内部受信消费引用边界、已越过最后资格事务的在途请求不能撤回、资源状态仅限记录时点，以及上述受保护文件的外部变化。当前切片达到本次审计终点，停止追加检查。正式状态裁定及本报告CHANGE登记交编排完成，主执行不得代改审计结论。
