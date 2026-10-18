# TASK-090 / R-084 — 范围修订与持久成果受控续接

完成结论：范围修订与持久父成果受控续接已实现、验证及精确收尾，原隔离增强审计者第一轮增量终审通过，A1/A2/E1关闭，TASK090/R084批准切片可供编排验收；不代改正式共享状态或宣告整个STEP006/008、真实provider及发布完成。

## 范围、环境与实际改动

根D:/shspic/project_NO3_RetroLume-agent，HEAD基础45951501d2741630a229762d6b2d3f4b34d7f702；保留全部原有未提交差异。需求v1.1、架构v0.56、执行状态v1.77。实现及首次审计采用根入口与公共AGENTS V3版本2026-09-28T14:08:37.3969855+08:00；增量收尾期间用户明确更新入口为V4，已补读公共DocuS/AGENTS.MD V4.0 CHG-0003，仅对剩余收尾生效，详见rule-update.json。保留此前适用版本事实及既有Ndocu路径，不移动或双写。本卡是执行，不接管WORK编排。原G3正式验收TASK-088-089-final-acceptance作为前置，不继承旧运行余量。

9项既有文件变动：activities/repository.py、__init__.py；capabilities/contracts.py、gateway.py、__init__.py；worker/one_call.py、launcher.py、supervisor_main.py、session.py。新增service.py、test_activity_scope.py、test_activity_continuation.py，以及task090专用support/offline/real_batch/controlled_child/bootstrap/win_chain六个夹具。001—007、旧fixtures/证据、materials权威主体、gate/windows_job/supervisor_ipc/transport、main/HTTP/UI/runtime/依赖锁、正式docu/公共库未改；正式建议交编排登记。无安装、提交、推送、真实provider、用户库或发布操作。

源码实际差异：[diff目录](../evidence/task-090/diff/)；[pre-hashes](../evidence/task-090/pre-hashes.json)及pre/保留原58项与正式文档基线；[最终hash](../evidence/task-090/final-hashes.json)不覆盖旧清单。[加载与适用性](../evidence/task-090/final-applicability.json)绑定最终真实批与实际编译源码，hash明细以JSON为权威。

## 接口、状态与权限

`ActivityService(ledger)`是受信内部应用接口，没有HTTP路由或常驻服务：

| 方法 | 结果与纪律 |
|---|---|
| async read_result(activity_id, operation_id) / resume_result(...) | ReadOutcome(status,snapshot)，只读同键，不claim、不轮询、不生成新ID、不发送。数据库不可读/read_unavailable、完整性错误/integrity_error、非法输入/invalid_input分开。 |
| async read_scope(activity_id) | 委托仓储inspect_scope，一条SQL快照返回ScopeSnapshot(activity_id,scope_revision,sources)；None明确not_found，不虚构revision。 |
| async revise_scope(activity_id,expected_scope_revision,sources) | 完整来源集合CAS；返回ScopeSnapshot。ScopeConflict("scope_conflict")、source_invalid、cancelled、activity_expired、scope_revision_limit等稳定异常分开，不盲重试。 |
| async continue_from_result(activity_id,parent_operation_id,new_operation_id,followup,service,config,executor_id,run_tag) | 返回ContinuationOutcome，business/监督SessionOutcome/SettlementFacts分别表示事实；同活动父新键不同。已有新键只查事实，不重发；父必须COMMITTED_CURRENT，取消历史仅可读。最多一次新one_call。 |

来源类型严格、UUID规范化、revision整数0..2147483647、来源去重且最多128；新集合按来源UUID排序，空集合允许表示全部移除。create保留原新建锁序和非空纪律，并复用该严格有限来源规范化。范围revision正整数、最大2147483647，CAS匹配且集合不变无写返回原revision；达到上界时变化拒绝，不绕回。

revise_scope锁序：读旧集合提示→旧新source_id并集按UUID锁→活动锁→重读旧集合并按完整source/version/revision规范集合比较→核CAS/活动状态/新来源当前版本revision→原子替换集合并revision+1。旧源过时不阻止移除/刷新，只校验新集合有效。pending/running可修订，cancelled/过期拒绝。范围变更不写status/G/executor/lease/dispatch_closed/deadline/M/R/S/次数/费用，也不强杀或代结算；不能承诺撤回已越过最后资格提交的请求。

统一_verify_scope_hint覆盖claim_lease、inspect_window、begin_window_close、settle_execution_window、cancel_activity、recover_unknown、recover_obsolete_operations、admit、_locked_operation。活动锁后集合变了整事务回滚为scope_conflict，不在活动锁下补来源锁。收尾方法只复核集合稳定，不新增“来源必须有效”门；空范围/旧源过时仍能按原身份规则取消、关门、结算或收敛旧操作。claim空范围异常拒绝；None仍只表示时间余额耗尽。G3只读保持单SQL资格/投影，无新增长锁。

ResultConsumptionRef(activity_id,operation_id,scope_revision,payload_sha256)为严格纯数据内部引用；ModelCallRequest.input_result默认None，AdmissionIntent传同一引用。gateway显式payload投影不包含引用；父/SUP/worker各跳严格编码、字节和同活动检查，SUP/直调监督在claim之前拒绝跨活动引用。内回执3、外帧2不变；旧无引用请求省略该新字段，新版接受旧请求，旧严格schema拒绝新字段，不作降级混用。

admit先来源锁→活动锁与集合复核，父/新操作按operation_id稳定顺序定位锁；核同活动、当前scope/context、非空有效来源、父received终态、结果admission/G/scope绑定及规范正文实际hash，之后才占新键并预留次数/费用。失败无新键/新模型预留；已准入后的scope变更拒dispatch/旧scope新正文，旧预留不退款。没有持久父子图，引用不声称能对抗恶意同用户进程。

服务将父正文放assistant低信任历史，followup放user；JSON取已验证封套value的规范编码，不升级为system指令。allowed_tools为空，不执行TOOL_PLAN；内部request UTF8<=65536及原provider/活动上界保持，超限明确input_too_large，不截断或摘要；非法配置/输入为invalid_input。异步调用以一次有界监督线程运行，shield并等待线程结束后才传播调用方取消；不把线程仍运行说成已停止。未知或丢响应先resume/read同键，NO_OPERATION/无正文终态不触发自动新请求，范围/重启/取消不复活预算。

## V1—V6证据矩阵

| 项 | 实际用例与原始证据 |
|---|---|
| V1 | ScopePostgresTests.test_v1_replace_cas_noop_empty_budget；test_v1_upper_bound_missing_and_response_loss：真实完整替换/CAS/noop xmin不变/空范围claim拒绝/上界与丢响应只读核对。 |
| V2 | test_v2_change_commits_before_old_disjoint_hint；test_v2_old_transaction_locks_before_revision；test_v2_source_version_race_uses_authority_and_lock_barrier；另外source_invalid、空/过时来源close/settle/cancel测试。两连接事件及pg_blocking_pids真实屏障，旧新集合不重叠，不靠sleep猜顺序；source版本变化通过既有materials.save权威实现。 |
| V3 | ContinuationPostgresTests.test_v3_current_parent_child_and_same_key_race（真实PG+两个gateway并发、synthetic transport恰1）；scope/source读后变化无预留、跨活动/伪hash/无正文/绑定损坏/正文损坏拒绝。 |
| V4 | test_v4_revise_after_admit_or_dispatch_no_refund_no_body，真实revise_scope引起dispatch拒绝与旧scope正文不写，次数/费用不退款；不直接SQL伪造范围接口。 |
| V5 | test_v5_resume_cancelled_unknown_no_send_or_rebudget；budget_exhausted_history_remains_readable；lost_commit_resume_no_resend；time_exhausted_resume_and_scope_never_refill。真实PG+调用计数/不调用断言，已持久/取消历史/未知/请求与时间耗尽/丢提交响应按持久事实恢复。DB不可读零发送和异步取消线程等待在离线覆盖。 |
| V6 | real-03固定SUP→worker→gateway→真实专用PG：真实仓储准备父P、显式内部service新Q、read；worker断言assistant/user内容、provider无引用、发送1，回执/DB/read hash一致，SUP实际204条顺序轨迹、树零/句柄/关门/结算。引用类型、64KiB、新旧schema及每跳跨活动claim前拒绝在离线覆盖。 |

真实PG22项=18项新行为＋4项必要旧回归（G3原子record幂等、旧操作收敛、正常settle幂等及旧R折叠claim），全发现/执行22，通过22、skip0、失败/错误0。Windows1例实际通过。原G3未变正文封套/读取故障矩阵和D3机制按明确未变依赖复用，没有全仓discover或整套重复。

离线01 35执行通过、02 8受影响通过、03 17受影响IPC/SUP通过、04 3受影响类型/服务通过、05 11受影响服务/引用通过，均skip0/失败与错误0。74为历史执行实例、43为唯一离线test ID，不冒称全部历史实例运行最终版本。旧索引曾漏掉诊断后换行才打印ok的dispatch测试并重复方法后缀，已从原始日志修正；首次审计所核40唯一项加本轮3新反例等于43。E1的历史测试源码缺口由offline05重新绑定全部相关方法，未补造历史原始源码。[唯一离线索引](../evidence/task-090/offline-unique-index.json)及[PG22索引](../evidence/task-090/pg-case-index.json)记录ID和最后适用证据。后续修改均有具体类型/IPC/错误出口原因，未重复无关已通过功能。

## 原始日志、命令与资源

真实原件：[real-03](../evidence/task-090/real-03/)的stdout/stderr、manifest、case-summary、as-run/post、parent-loaded-source、loaded-source-bytes、bootstrap-sup/worker。PG/测试实际加载15项、父进程16项、SUP/worker各18项，从首次产品导入前捕获实际源码编译字节，不只事后读磁盘。real-03加载hash与该批post及首次冻结匹配；最终service新增两处分类修正、测试仅新增离线方法，真实PG类AST及所有仓储/IPC/runner未变，按增量独立审计限定复用，不能声称该批加载修正后service。受保护产品及正式docu未漂移，AGENTS外部变化单独登记；SUP顺序在真实SUP记录，不用父trace冒充。

模型父P摘要06c52726e31608d49740696b459c4f257363917b4a83a1211cd0407e226a641a，Q回执/DB/read摘要07642a332cbe8328edcfca6161c69da2b15b76fa5e7a02183b7a3845c548ca7b。Q G3，结束活动G4；两次模型准入（P合成持久准备＋Q一次transport），requests_reserved2，R0/S2（P合成结算1＋Q实际0.75秒向上取整1）。P准备不启动Windows/provider，不冒称第二个实际模型发送。

命令记录：

- `python.exe -B backend/tests/fixtures/task090/offline.py offline-01 ...`及02/03/04/05：完整argv在各manifest；每命令独立有界外层Job，<=60秒。
- 首真实入口 `python.exe -B backend/tests/fixtures/task090/real_batch.py --phase all`：精确inspect失败，owner0.25秒、runner退出1，未进入case/未创建库角色或启动容器；manifest.exit=null是未启动子case，不等于runner成功。
- 第2独立只读入口：`docker inspect`精确CID，仅Id/Running/Pid；Docker Linux引擎管道不存在。保守记第2attempt及2秒，摘要是工具输出转录，不伪造成旧历史原件。已向用户请求启动引擎，用户明确“已就绪”后才执行末批。
- 第3入口同一real_batch --phase all：原始PG22通过、Windows1通过，runner/case exit0，内部实测13.171秒，外层Job树零/自有句柄关闭、精确容器stop并inspect确认Running=false/Pid0，cleanup_incomplete=false。

精确CID e49d3acc3c1be13d670af68bca2b082fea4faeeb9b9babe69df7f1d3941696a4；旧名retrolume-task-088-g3-w1、指定镜像/唯一named volume/127.0.0.1:55441/1CPU/512MiB/pids128/restart=no/无特权。manifest实际Mounts Type/Name/Destination/RW、端口HostIp/Port、安全字段齐全。只创建专用retrolume_task090_scope库及retrolume_task090_synth LOGIN NOINHERIT/无超级或其它创建权限角色，并在新库首次应用001—007；没有改旧库、旧角色、管理口令或pg_hba。若后续本卡剩余入口可用才允许先核归属再轮换该新role，本次实际只有创建初始化，没有第二次轮换。

DSN只在owner内存/stdin/受控子进程env，未进argv/日志；RETROLUME_SCOPE_TEST_DATABASE_URL专用新库。为选取旧回归，RETROLUME_ACTIVITY_RESULTS_TEST_DATABASE_URL、RETROLUME_TASK_068_DATABASE_URL、RETROLUME_TIME_BUDGET_TEST_DATABASE_URL仅映射同一090库，不读取用户连接。测试只按注册随机ID定向FK清理；库/角色/容器/卷均保留，其他四旧资源未操作。当前无本卡在途进程或可复用明文凭据，最后停止结论仅覆盖manifest记录时点。

[预算单账](../evidence/task-090/budget-manifest.json)：3/3入口（保守含独立只读诊断）、Windows1/6、新容器/卷0，真实累计20.421/2400秒（13.171＋0.25实测、诊断保守2、启动预扣5），离线14.826/1800秒（内部运行/失败入口/静态＋五次启动预扣5；offline05实测0.968秒）。余秒不是再运行许可；启动次数已满，完成即停。

## 中间偏差与收尾

新offline runner首次复用时证据根映射漏掉连字符，触及旧目录exist_ok=false检查后退出，未写旧证据/未启动子测试；修正新目录后正常运行，入口耗时保守2秒入新离线账。原Docker阻塞与独立诊断保留，不换分母或抹除。普通静态复核补齐来源严格类型、完整性错误码、IPC claim前绑定以及服务非法输入/字节上界区分，实际修改后仅复验影响项。

[断点](../evidence/task-090/checkpoint.md)保存已生效操作和下一动作；[审计输入](../evidence/task-090/audit-index.md)提供原目标/设计、冻结差异/原始证据。全新task090_audit以fork_turns=none创建，明确请求gpt-6-astra/ultra，只可写本人独立报告/审计证据，未继承主聊天/记忆、未实现/修复/运行资源。初审由其本人保存为TASK-090-independent-audit.md，披露独立只读辅助evidence_read。主执行第一轮合并修复后冻结incremental-01，只交实际增量及offline05原始证据；其本人现已在原报告G节追加增量最终结论，初审A—F保留。主执行只引用，不修改审计报告。

正式文档建议：编排在验收后登记G4范围修订与G3内部消费切片实装/已验、范围变更逻辑撤销边界、只读恢复与新请求分离、内部service及可选引用版本兼容；保持G5工具计数/公开HTTP/完整STEP006/008/真实供应商/发布开放。无新增持久表/008迁移/主要模型或公开接口决定待用户；真实审批及后续全局任务由编排掌握。

增量收尾01

独立初审A1为父P读取后SUP明确取消却返回supervision_unknown；现保留cancelled，同时业务no_operation、监督对象和结算事实继续分别返回。A2为合法类型但timeout跨配置冲突在one_call执行前抛错，被服务误归未知；现于监督线程/launcher之前明确invalid_input，不把运行中真正异常改为无执行结论。新增测试分别覆盖取消确认、两种配置冲突前拒绝，以及未知异常仅调用一次、resume零重发。测试使用服务边界替身，不能替代真实SUP/PG取消证明，原真实V5及V6证据按未变路径复用。

offline05运行当前ContinuationOfflineTests全部11项，发现/实际执行/通过11，skip/失败/错误均0，退出0，source_unchanged=true，外层树零及句柄关闭。旧E1相关严格引用、异步取消等待、大小拒绝方法均实际运行最终源码。incremental-01/final保存service及测试源码，与loaded-source-bytes和最终hash一致；pre-hashes保留第一次审计快照，两项最小diff记录实际接续。只修改两文件，没有继续真实资源操作。

根AGENTS在增量冻结时发现外部V4变更，非本卡写入，写入者未由本卡确认。随后用户明确替换旧入口，主执行补读新公共规则，原审计者同步通知；先前未读V4不追认已生效。新规则不增加授权且允许保留历史路径，继续原TASK090交付，不接管全局维护。V4新追加文字不新增表格/星号，已有合同和审计历史格式保留。

最后冻结复核

backend范围67项最终指纹核对一致，单列final-product-hashes.json，避免把外部文档变化混为产品漂移。final-hashes.json保留增量冻结时71项完整清单，其中架构导航随后有外部编码/换行字节变化，与pre规范文本完全一致；记录external-navigation-change.json及前后hash，本卡未写正式架构、未修改合同或共享状态。规则入口变化及用户明确采用V4另外登记，不把冻结清单当成共享文档实时监控。

真实03的停止原件为Running=false、Pid=0、outer_tree_zero/outer_handles_closed/container_stopped均true、cleanup_incomplete=false。offline05也tree_zero及handles_closed均true，预算active_processes为空；恢复时另核未发现本卡专用Python运行进程。没有为确认现状追加Docker入口，停止结论覆盖各manifest记录时点，不承诺他人此后未启动容器。

当前service.py SHA256 977f14c73f8c5533eebb7d34bba82de55a14ee5e9e314f903c2a0697cf5cbe32；test_activity_continuation.py SHA256 472eb7a9cf2deb848fdc1029ec01ce12dc501791545b54ee8ed0ff8268d6c9c9。仓储、引用、IPC等完整最终hash见final-product-hashes.json。

独立最终结论及交付终点

原隔离审计者task090_audit本人签发的[TASK-090-independent-audit.md](D:/shspic/project_NO3_RetroLume-agent/Ndocu/results/TASK-090-independent-audit.md)G节结论为通过。初审A—F历史完整保留，只有一轮合并修正及增量确认；开放确定缺陷0、阻断证据不足0。独立复算记录audit/incremental-01-source-evidence-check.json，审计本人未写产品/测试或运行资源，未读取本结果自评。

四维最终结论分别为产品合同通过、动态证据适用通过、执行合规通过及资源最终记录通过。最终11项离线受影响方法绑定当前源码；PG22方法及仓储/IPC/runner未变，真实Windows成功样本model timeout 0.5秒和session timeout 2秒不触发新增配置拒绝，committed_current不进入新增取消分支，故原成功路径仍适用。这是独立确认的精确影响分析，不声称真实03加载修正后的整份service文件。

原始离线01—05合计74个历史执行实例、43个唯一test ID，另真实PG22，共96个unittest历史实例及65个唯一ID；Windows另列1场景，各实际case均0skip/失败/错误。第一次入口及独立诊断失败仍完整保留，与case成功统计分开。3/3真实入口已用尽、Windows1/6、新容器/卷0、离线14.826/1800秒及真实20.421/2400秒；资源停止边界和保留对象按原始manifest记录，不追加现场探测。

本卡全部约定成果达到可交回条件，主执行停止产品写入、测试和资源动作。当前无需要用户夜间处理的缺口。下一步仅由编排核阅本结果及独立报告、裁定正式TASK090验收并登记正式文档建议；本卡不派下一TASK、不实施G5或公开入口、不接管共享状态。
