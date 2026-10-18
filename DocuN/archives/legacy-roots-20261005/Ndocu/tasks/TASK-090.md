# TASK-090 关闭登记

2026-09-30 编排已核对实际产品指纹、原始批次记录和独立终审，TASK-090 / R-084 验收通过，批准切片关闭。裁定见 [编排最终验收](../../DocuN/results/TASK-090-final-acceptance.md)。原任务全部运行许可结束，预算和失败历史保留，不因余秒或规则换版续跑。

本卡及原 Ndocu 结果／证据保持原路径。正式文档已按用户要求迁入 DocuS，实际新路径见 [项目入口](../../AGENTS.md) 和 [执行动态文档](../../DocuS/执行动态文档.MD)。090 前段仍按当时 V3 合同解释，增量收尾与后续任务采用已登记 V4，不追认早期已读新版。

下一成果为另号 TASK-091 / R-085，原 090 主窗口按新卡补读 V4，不能将下文旧实现合同当成新运行授权。

## 原合同全文


# TASK-090 / R-084 — 范围修订与持久成果受控续接完整实现
你是本卡执行Agent，在一张卡内完成实现、相关测试/修复、精确收尾和阶段末独立增强审计，完成后统一保存结果供编排验收。不接管全局编排。

接收：原TASK089主执行窗口，增强执行，最强可用模型/最高可用推理档；范围可变带来锁序及权限传播，需强推理。不要继承旧审计窗口的额度阻塞，阶段末用未参与090实现的全新隔离审计子会话。
任务：TASK090/R084；STEP006/008局部；父089，复用已关闭088/089 G3、085/086、083/084。关联FLOW005、DATA007、NFR002/003、SEC002，G4范围修订与G3消费接线；G5工具计数仍不在本卡完成范围。
根D:/shspic/project_NO3_RetroLume-agent。需求v1.1、架构v0.56、执行状态v1.77；Git基础45951501d2741630a229762d6b2d3f4b34d7f702及已有有效未提交差异全部保留。
状态：待用户转交。授权：用户既定STEP006/008受控业务接线与连续开发委托；编排采用已交付TASK-089-next-contract完整设计，在现有002/007模型及内部受信接口范围内明确授权本卡实现/合成验证。不是用户库、真实provider、公开HTTP或发布授权。

## 1. 完整成果与执行节奏
交付同一活动的真实范围更新和安全消费已持久父成果的内部闭环：read/resume查持久事实→read_scope/revise_scope明确修订→continue_from_result显式新操作→既有受控one_call→读新成果。一个入口调用最多一个新的模型操作，没有自动多轮循环/工具执行。
完成标准：第3节接口/权限/锁序/失败行为落地，第5节新行为有适用证据，资源收尾明确，阶段末独立增强审计无阻断，可交编排一次验收。
先实现完整功能及必要适配，在同窗做相关测试与普通修复；不每个函数/文件设独立审计，不为每个正常中间步骤回传。全部稳定后一次集中独立审计；审计发现的问题合并修正，只增量确认，不重审未变G3/D3。完成即停，节约总返工/读取/测试成本，不以耗尽额度为目标。

## 2. 必要上下文与冻结
入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md；公共D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD（2026-09-28T14:08:37.3969855+08:00）；公共库只读。编排WORK同库docu/WORK.MD（14:27:08.2195352）、模板Ndocu/TASK_TEMPLATE.md（14:23:15.6061911）、阶段Ndocu/prompts/07_开发执行循环.md（2026-09-23T09:02:19.8381135）；执行不加载全阶段，已读未变不重读。
按序：
1. Ndocu/results/TASK-088-089-final-acceptance.md、TASK-089-next-contract.md完整推荐合同；以本卡明确细化覆盖冲突，不重做设计。
2. docu/LATER_REQUIREMENTS.MD相关NFR/SEC、PROJECT_ARCHITECTURE.MD当前G4/FLOW005/DATA007、PROJECT_EXECUTE_STATE.MD当前任务/资源，按需读。
3. activities/repository.py及导出，capabilities/contracts/gateway，worker/one_call及实际请求消费点；materials/repository.py的save/confirm权威更新只读；001—007相关schema只读。沿函数直接依赖，不全仓重审。
4. G3证据按需复用：task089/final-applicability、独立审计C、windows-completion-01/attempt-2/post-hashes.json；主窗可复用已有结论，独立审计只给正式验收边界和原始证据，不给实现聊天自评。
当前末批post清单58项经编排核无漂移；核心repository=a31e7d770b9f8746bfe66dd4fc7ea946b195eca21b029b370940810fd0a938b2，one_call=cb1bf3f2440c6727311fb2a8af27d1b9668a6abc1ef00c84e6ff4e465ce57727。实际改动前存pre/hash/diff，不覆盖旧清单。首次核有无在途/090产物，已有运行先接续；陌生差异查明不覆盖。正式docu本次更新不当产品漂移。

## 3. 功能与权限合同
### A. 内部服务
新增backend/app/activities/service.py，对受信调用方提供：
- read_result/resume_result(activity_id,operation_id)：只读G3同键事实；不claim、不生成新ID、不出站、不自动轮询。未知/暂不可读如实返回，以后显式再查。
- read_scope(activity_id)：仓储inspect_scope，同一SQL快照返回当前scope_revision与完整轻量来源集合，供CAS及提交丢响应核对。缺活动明确not_found，不伪造revision。
- revise_scope(activity_id,expected_scope_revision,sources)：完整新集合，不传正文充权威；sources项source/version/revision严格类型、去重和既有数量上界，返回新revision及元数据。
- continue_from_result(activity_id,parent_operation_id,new_operation_id,followup,service,config,executor_id,run_tag)：同一活动、父新键不同，显式新意图；父必须当前有效持久正文，放低信任assistant历史，followup放user，绝不提升到系统权限指令。json用已验规范value。请求仍受64KiB和原上下文/输出上界；超限明确拒绝，不截断/自动摘要。allowed_tools为空，不执行TOOL_PLAN。
明确同步监督与异步仓储调用边界，不在已有事件循环裸asyncio.run；不得因异步调用者取消就把仍运行的监督线程当已停止，继续履行既有有界收尾。普通技术实现由你决定，不新增常驻调度/后台worker服务。
返回业务读取、监督结果、结算事实三者分开；回执未知不据此自动再次调用。相同new_operation_id不重发、不同新键才是新请求；新键冲突不得退款或重置活动预算。

### B. 范围修订权威与锁序
沿002现有activity_scope_sources/scope_revision，不加表/字段/008迁移。
revise_scope单短事务：读旧集合提示→对旧新来源ID并集排序加锁→锁活动→重读旧集合且与提示完整比较→核CAS/活动状态/新来源实际版本revision→原子替换集合与scope_revision+1。旧源过时不阻止移除/刷新，仅新集合必须当前有效；不得在持活动锁后补锁新来源造成反序。
集合比较按source_id/version_id/revision的规范集合，不能只比数量/ID或受输入排序影响。重复source拒绝；相同集合且CAS匹配无写返回原revision；CAS不匹配明确scope_conflict，不盲重试。整数上界前拒绝，不绕回。
pending/running允许显式修订，cancelled拒绝；过期等其他已有活动终态纪律保持，未知状态不自动获权。空集合允许表示全部移除并推进revision，但此后claim/admit/正文读取必须拒绝新执行/抑制正文；None仍只表示时间预算耗尽，空范围不能伪装为耗尽。
范围变化不改status/G/executor/lease/dispatch_closed/deadline、M/R/S、次数/费用计数，不强杀/不代结算。不承诺即时撤回在途请求；旧scope后续发送/新正文提交被拒，现有监督有界收尾。
所有来源→活动→操作事务在活动锁后重新比较此前来源提示；变了整事务回滚，明确scope_conflict，不能追加反向来源锁或继续用旧集合。实际覆盖claim/inspect_window/begin_window_close/settle/cancel/recover_unknown/recover_obsolete/admit/_locked_operation；create保持新建流程。用统一小helper消除遗漏，但不顺手重构无关事务。
关键：复核“集合在加锁期间未变”和验证“来源仍有效”是不同要求。cancel/关闭/结算/必要旧操作收敛沿原合同，即使来源被删除/替换或范围为空仍要能按其权限规则收尾；不得新增来源有效性门把停止/保守记账锁死。只读G3保持单语句快照不新增长锁。来源集合竞争可在既有总期限内有限重试，重试不延长deadline或重置预算。

### C. 父成果到新操作重新准入
新增纯数据ResultConsumptionRef(activity_id,operation_id,scope_revision,payload_sha256)，严格UUID/操作键/正revision/64位小写hex；ModelCallRequest.input_result默认None、AdmissionIntent传同一引用，旧无引用请求保持原行为。
gateway provider payload显式投影排除该内部引用。IPC两侧严格类型/字节限额/同活动绑定；内回执3、外帧2不变，不用任意降级绕旧端extra字段拒绝。新旧worker混用明确拒绝；旧无引用请求在新版本正常。
服务只从G3受控read得到COMMITTED_CURRENT正文和引用；admit在来源→活动锁及集合复核后，按操作ID稳定顺序处理父/新操作锁（新键不存在由活动锁串行化）。原子核父操作/结果完整绑定、当前scope、非空有效来源、实际payload/hash与引用/context一致，才预留新操作次数/费用和占新键。任一失败无新键/预留。
父正文已读快照不是新出站资格；read后范围或来源改变必须拒绝续接。取消历史只可读不能消费；过期/余额不足/关门/租约或G失效继续失败关闭。
mark_dispatch_started保留再次校验来源、scope/G和门；admit后范围变更则禁止新dispatch，已预留按原规则不退款；越过最后资格提交的请求可能在途，不能保证撤回，旧scope结果不得新增成功正文。
合法父结果不可变，本卡不持久化父子图/消费事件；不能宣称引用可对抗恶意同用户进程。服务的组装和内部受信调用边界必须明确，未来外部身份/请求指纹另行设计，不能放开任意客户端绕正文选择。

### D. 失败与恢复
明确区分scope_conflict/source_invalid/result_invalidated、unresolved/read_unavailable、cancelled/budget_exhausted、input_too_large/invalid_input、integrity_error、supervision_unknown等；不把所有错误标成自动重试。
scope提交成功丢响应先read_scope核CAS结果，不能再次无条件+1；新操作提交/回执丢失先read同键，不重新发送。NO_OPERATION/无正文终态也不触发自动新请求。
范围/读取/重启均不复活M/R/S或次数/费用额度；cancel后不额外settle；旧树未知不得开新窗口。数据库/异常日志不泄漏正文/凭据/敏感SQL，不能把上游模型正文当系统指令。

## 4. 文件边界与协作
允许：
- activities/repository.py、__init__.py，新增service.py；
- capabilities/contracts.py、gateway.py及必要导出；worker/one_call.py、worker_main.py、session.py、launcher.py、supervisor_main.py仅实际请求引用传递/有界冲突适配，不改监督/退款权力；
- 新test_activity_scope.py、test_activity_continuation.py；test_activity_results/test_capabilities/test_worker_one_call/test_worker_session仅受影响必要适配，原断言不弱化；
- 新backend/tests/fixtures/task090/，Ndocu/evidence/task-090/，Ndocu/results/TASK-090-result.md和TASK-090-independent-audit.md。
001—007、旧task083/085/088/089夹具及证据、materials权威写入主体、gate/windows_job/supervisor_ipc/transport安全主体、main/HTTP/UI/runtime/依赖锁、正式docu/公共库只读。禁止生产数据/安装/拉镜像/付费provider/Git提交推送/部署；工具不自动执行。
本卡单一owner写产品/管资源；无并行修改/测试同一快照。阶段末审计子会话只写其报告/审计证据。确有范围外必须改动，先定位具体影响，完成不受阻部分后交回，不自行改权限/持久模型。

## 5. 定向验证与一次集中审计
按TASK-089-next-contract V1—V6，合并测试而非机械每项起批；每个实际新行为映射到test ID和原始证据：
V1 真实PG完整替换/CAS冲突/无变化无写/空集合拒新调用、scope上界及预算不变；revise响应丢失后read_scope确认不重复推进。
V2 两连接明确锁屏障证明范围变更先提交/旧事务先锁两顺序，旧新source集合不重叠样本验证锁后复核确实拒绝；来源版本替换竞争；取消/关闭/结算在过期来源/空集合下仍按原合同可收尾。等待有界，不靠sleep猜顺序。
V3 真实PG当前P→Q准入成功；读P后scope或来源变更拒Q且无预留；跨活动/伪hash/无正文/损坏绑定拒绝；双请求同新键不双发送。
V4 Q准入后真正revise_scope触发dispatch拒绝/旧scope record不得新正文，原预留不退款；不能直接SQL改scope代替新接口。
V5 服务只读resume当前/取消历史/未知/DB不可读分支均不发送；预算耗尽仍能历史读取但不能Q；取消/未知/重启不复活预算。新逻辑相关部分用真实PG/调用计数，未变G3故障矩阵不全跑。
V6 最小真实Windows内部service链：已持久合法父P→显式新Q→read；真实PG/监督主体、合成transport；证明父输入确按低信任内容进入请求、引用不发provider、发送恰一次、内3外2及hash、树零/自有句柄关闭/关门结算。父可通过真实仓储合成提交准备，不必为造P多跑一次Windows。离线测参数/字节上界/旧无引用兼容及旧端拒新字段、非法引用/工具禁用。
异步服务取消/线程边界只有实际采用时测试受影响收尾，不新增通用异步框架。类型/纯编码用离线、事务/竞态用真PG、进程接线用一例Windows，互不冒充。
旧G3 44离线/18PG/Windows、D3/085机制按实际未变依赖复用；来源helper实改相关方法就选必要回归，不能因函数名旧就免回归，也不默认全仓discover。
产品完成、验证证据充分且资源已收尾后，再创建一个增强审计隔离新Session（如fork_turns=none）：仅原目标/本卡、设计合同、最终源码/diff及原始证据，禁继承主聊天/实现自评/记忆。审计一次完整功能，重点新锁序/权限/未知/预算/协议和证据适用性；不再次全审未变G3。
审计发现问题在同卡合并修复并只确认实际增量，至多两轮有据修正，同核心两次仍败止。独立性不足明说，不能执行者自签。审计模型额度不足是能力阻塞，不否定已保存有效报告，不重做已有通过工作。
卡内按上述顺序连续完成，不在普通实现/compile/每批之间另加独立审计，也不反复向用户问是否继续。

## 6. 新任务资源与可续接运行授权
088/089已结束，不承接其剩余量。本卡新账：离线累计≤1800秒/单命令≤60秒；真实PG＋Windows合计最多3次启动、累计≤2400秒/单批≤600秒、保留180秒收尾；Windows会话≤6，仅必要新场景，成功足够即停。预检/失败/探针/等待/起停全部计入；PG/Windows不各分母，命令入口即记attempt。
复用唯一精确CID e49d3acc3c1be13d670af68bca2b082fea4faeeb9b9babe69df7f1d3941696a4，名retrolume-task-088-g3-w1，卷retrolume-task-088-g3-w1-data，镜像sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f；127.0.0.1:55441→5432，1CPU/512MiB/pids128/restart=no/无特权/仅该named volume/无宿主bind。新容器/卷0，不碰其余四旧容器。
允许在此CID用已验容器内受信管理连接retrolume_task088_synth，首次创建一个全新专用库retrolume_task090_scope及最小LOGIN角色retrolume_task090_synth。不得改变管理账户/旧088/089库或口令、pg_hba、角色继承或超级权限。若090名字已存在，先核本卡manifest/所有者/无他人占用；无法确认归属即停，不能覆盖。
明确允许本卡角色在各许可批入口核验归属/权限/无占用后轮换随机口令，经psql stdin传递，owner内存及受控子进程env持有；丢失owner内存不再成为无解门，剩余批可重新核同role再轮换，不要另建库/容器。绝不读旧Env/秘密，不在argv/日志/结果输出密码/DSN。只该090角色可轮换。
首次在新库应用001—007作为合成基线；后续核schema并复用，不对已有表重复迁移。专用RETROLUME_SCOPE_TEST_DATABASE_URL（若需要其他变量仅指向同新库，记录映射），缺失skip不能算通过，不回退用户DSN。每例随机ID定向FK清理，禁止全表DELETE和删除旧数据；不同场景隔离schema只限这个新库，不创建第二数据库。
复用089已解的运行控制到task090：PG阶段与Windows阶段可按--phase选择、有同一预算账/内存owner或许可角色轮换；一个纯测试前提失败不要求在重跑时再次执行已通过全部PG。缺口修正后只跑影响/未跑项；受安全前置阻断的Windows不能绕过。
manifest必须记录精确运行资源配置及当前状态/端口所有权；inspect核Mounts完整Type/Name/Destination/RW和HostIp/Port，不能unknown默认通过。独立外层Job/总deadline与受测业务阻塞分离，PID+创建时间、树零/句柄及异常收尾可查。
每批as-run/实际加载/post指纹从开始采集，SUP顺序证据由实际SUP采集，不放错到父进程；可复用089被动钩子，禁止改生产函数返回伪造断言。不得为记录一次成功重复跑两个相同样本。
结束stop该CID并核Running=false/Pid0，保留库/角色/容器/卷不删；失败也精确收尾，不宽泛kill/stop。资源缺失/配置不符/未知owner/收尾不明停真实部分，继续无冲突离线或文档，不建替补或拉镜像。
外部provider调用0、用户库0、端口之外服务0、安装/提交推送0。授权只有有限合成操作，不因本机工具权限大就扩大。

## 7. 交付、断点与停止
Ndocu/results/TASK-090-result.md：完整接口/签名/锁序和范围变更语义、实际文件差异及hash、V1—V6/相关回归对照、真实命令与case/skip/失败/退出码、原始证据路径、资源/时间/attempt单账、独立审计引用、未验证/偏差/正式文档建议及必要人工操作。
独立报告TASK-090-independent-audit.md由审计者本人写，原始/增量历史保留，主执行不能代签。证据Ndocu/evidence/task-090/保存pre/diff/as-run/post、原始事件/资源manifest及checkpoint；证据不逐文件复制多份或重复记账。产品实现不依赖Ndocu/外部公共库。
额度/上下文接近上限先保存已生效操作、进程/容器状态、凭据生命周期、尝试/剩余及下一入口；无在途才安全交回。换窗/模型不清零，不重复启动。
完成即停；同核心两次有据修正仍失败、需要新增持久/公开接口/权限或用户数据/费用、资源归属不明、预算到限，完成不受阻部分并带具体差异交回。普通小错不逐次退卡；不能以通过本卡宣告G5/STEP008整体/真实provider/发布完成。
确认结果已保存可读后仅回一句话结论＋绝对链接D:/shspic/project_NO3_RetroLume-agent/Ndocu/results/TASK-090-result.md，用户一次带回编排。
