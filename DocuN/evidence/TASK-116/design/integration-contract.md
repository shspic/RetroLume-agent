# STEP018 唯一最小集成实施合同（TASK-116 / R-110）

本合同完成设计，尚未实施、运行或验收STEP018。采用当前PG权威库、领域命令/记录、007原子正文和Windows原生监督链；把现有入口串成两条完整流程，增量补受控Embedding、精确向量与词项融合、同库重开连续性及本机交付。没有重建通用Agent、计分或记忆平台。规范性样本见[验收合同](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-116/design/acceptance-contract.md)，前向实施范围见[实施卡草案](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-116/design/implementation-card-draft.md)，实际采用决定见[采用包](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-116/design/adoption-package.md)。同一规定不另存平行副本。

## A. 当前调用链与缺口归属

“存在”以下仅指本次源码静态核对；“继承”指原任务已裁定的有限证据，不是TASK116重跑。证据层分别为S源码、P协议/合成、T真实本机事务或监督、U真实浏览器/公开入口、Q真实服务的语义验收。原115终审只关闭有限STEP017，G11只关闭已采用安全宿主的有限切片；Q和完整重开链仍须新证。

| 地图行/唯一增量归属 | 现在的真实入口及函数 | 当前承载/事实 | 证据及剩余工作 |
|---|---|---|---|
| M01 导入到范围 | `frontend/src/main.tsx:App.upload/activateMaterial`、`PdfReviewPanel` → `materials.api.upload/read_material`、`pdf_review.api.confirm_candidate` →资料/版本/逐页核对表 | TXT/MD逐文件导入；PDF原页与提取预览、确认/跳过、用户补充；活动只能选当前ready版本 | S，旧资料/PDF有限P/T/U继承。缺明确“用此资料开始学习/面试”交接；只把已核ID/版本传到范围草稿，再由服务器重新核当前版本。失败项留在导入页，其他成功项继续。 |
| M02 创建与范围 | `ActivityWorkspace.createActivity` → `activities.api.create_activity` → `ActivityService.list_scope_source_versions`、`PostgresAdmissionLedger.create_activity/revise_scope` | 服务器冻结source/version/revision、预算和允许模型；已有显式记忆选择及防重复创建意图 | S及旧活动有限证据继承。新增版本期望检查、检索能力/外发摘要；不能只由前端选中状态授权执行。范围变化沿原修订，不另建活动状态机。 |
| M03 意图/目标/澄清 | `ActivityWorkspace`首轮/追问 → `LearningService.execute` → `assemble_catalog` → `ModelCallRequest.learning_profile` → `run_one_call`；`getTeachingSeed/onUseGoal` → `TeachingWorkspace.submit('goal')` | 首轮已有answer/clarification/no_evidence/conflict与持久正文；teaching目标零费用保存；G7不接受选记忆活动 | S及旧G7有限P/T/U继承。主入口显式选择学习/面试；学习无记忆可复用已持久G7目标seed，选记忆直接保存teaching目标并由plan作必要澄清。澄清答复修订目标，不从缺信息自动推能力。 |
| M04 检索 | `learning.evidence.load_units/assemble_catalog`、`teaching_evidence.assemble_teaching_catalog`、`interview.evidence` → `retrieval.evidence.build_fragments/rank_term_candidates/verify_fragment` | 已有原件回查、lossless片段、词项排序及范围过滤；不是完全没有RAG。当前`terms.v1`，没有Embedding适配器、向量记录或pgvector查询接线 | S；旧词项与定位证据继承。唯一新增归属R：受控显式索引/查询Embedding和`hybrid.v1`。沿架构已定pgvector精确cosine+词项融合，不把词项局部成功签为向量或语义通过。 |
| M05 路径/题/回答/反馈 | `TeachingWorkspace.submit` → `teaching_api.submit_teaching_command/read_teaching_workspace/read_teaching_command` → `TeachingService._submit_model/_freeze_model_context/_load_teaching_entities` → `accept_teaching_command/claim_teaching_launch` →Native；`apply_teaching_local`保存目标/接受路径/作答 | teaching_commands/records/heads已有goal、plan、accept_path、exercise、answer、evaluate、correction等；freeze绑定真实父记录及hash、CAS；模型007正文与领域投影同事务 | S及旧教学有限P/T/U继承。改检索提供器与完整流程导航，补有据开放反馈/针对练习真实语义；不重新实现上述实体。模型输出schema成立不等于参考答案正确。 |
| M06 复测/理由 | `TeachingWorkspace`初题、retest、continuation、反馈/理由展示 → `teaching_policy.derive_support_checks/derive_progress`、teaching_progress/仓储事务 | 现有有限Decimal检查、单位换算、不执行程序题；两份不同且未暴露答案的独立合格作答才达到`evidence_sufficient`；保存progress理由/节点变化，重复答不重复计分 | S及旧有限P/T证据继承。补完整用户链传播与语义反例。现有单位自动核算限m/s、m/min、m、s、min；其余单位保留unchecked，不能自称通用计算或长期掌握。 |
| M07 解释/工具 | `_submit_tool` →受限`finite_calculate`工具账；`openHtml` →`HtmlExplanationPanel` →`HtmlGenerationService.generate` →Native描述生成/编译 →`PreviewController` →外部SUP/Docker attach | `interactive_description.v1`由固定程序生成真正交互HTML；命令父记录/hash与宿主身份、预览3次/180s及每窗≤60s已有控制；未知清场不新开 | S，G11有限T/U及独审继承。仅验证本次题/反馈到解释的关联和计算，不改runtime/自由HTMLJS/权限。缺签票或不可用时显示原因、保留题/答案，不称FR009已通过。 |
| M08 学习记忆 | `MemoryWorkspace`及teaching捕获预览 →`memory.api` →`MemoryLedgerMethods`；`memory.context.make_recipe/materialize_recipe/check_capacity` →teaching.v2 | 记忆原文、版本、依赖、用户修正/撤销及显式选取已存；≤4条/4096bytes背景低信任；撤销抑制失效正文，不改证据 | S及原记忆有限P/T/U继承。补同库重开后的资格与失效传播。对面试的现有明确禁止在M09收口，不能声称已贯穿。 |
| M09 文字面试/记忆 | `ActivityWorkspace` interview变体 →`InterviewWorkspace` →`interview.api.submit` →`InterviewService.submit_command/_frozen/read_citation` →`InterviewLedgerMethods.accept_interview_command/claim_interview_launch/_write_interview_outcome` | 当前真实start/goal/ask/answer/correct_answer/review/bind_scope/finish及有限probe、认可/缺口、历史回查均存在。当前`interview.v1`明确拒选记忆，start还要求fresh unselected activity | S及原面试有限P/T/U继承。新增`interview.v2`可选低信任学习记忆背景，保留v1禁记忆；主链完整语义及必要追问新证，禁止把自报当履历或收益事实。不是重新造面试模块。 |
| M10 预算/监督/未知 | `capabilities.ControlledModelGateway` →`ledger.admit/mark_dispatched/record_outcome` →`OneCallInput/run_one_call` →`launcher.run_supervised_window`、外部SUP/worker →007 | 真实httpx transport已实现；默认无SDK重试；一次窗口90s、请求10s、总管理120s；收到事实与当前资格分开；旧未知不退款或自动重发 | S，旧RootLease/Windows Job/StopProof/UNKNOWN的有限T继承。仅为新embedding kind及新profile扩类型绑定与同一四账，新故障传播补证。真实provider当前配置/能力/语义未核。 |
| M11 同库重开 | 活动列表/GET历史/各意图台账 →持久领域heads/records、operation结果；`SessionConfig.single_host_single_session_recovery` | 已能重新读取持久活动；意图正文在IndexedDB、owner/view/CAS防晚到；自动恢复声明默认False。读历史、重启容器都不足以证明完整继续 | S及旧恢复边界继承。新增正常库owner准入/显式继续步骤及跨服务重启主链测试；不复制旧lease/generation，不自动重放费用调用。 |
| M12 退出/隔离恢复传播 | `data_exit.config.DataRuntime`装配、DataWorkspace →`data_exit.api.jobs/plans/restore_jobs/activate/deletion` →snapshot/包/删除/恢复；`LocalRestoreFactory._initialize/seal_readonly`、`ReferenceRootCoordinator` | 001—013/R01、28业务表+3控制导出视图的精确profile；十三版loader白名单/角色/原件fence/恢复永久只读均已有限验收 | S，原114/115有限T/U及独审继承。新持久检索与新profile需R02增量快照/删除/恢复传播；不重开已关闭原验收，不将恢复副本开放写入。 |
| M13 本机交付 | `create_app`路由/Selector loop、`deploy/start_local.py`、`start-backend.ps1`、`compose.local.yml` | FastAPI/React已装配；Compose已有缓存PG/pgvector服务及renderer-build入口；本地脚本已有PG启动、hidden uvicorn、停止自己启动的PG/子进程 | S及旧组件运行事实继承。缺正常库迁移/精确profile就绪/端口全状态与owner接续收口；补示例teaching配置和README过时文案。不是“未用Docker”。 |

### Must对照（缺口只归一处）

差异分类：M01/02/03/05/06/07/08/10/11/13的跨模块主链/运行不足为既有Must实现不足；M04的向量能力是已采用检索方向尚未实现的承载，不是从零选型；M12为新表导致的必需前向传播。M09已有FR011主模块，完整语义是Must未证；面试可选学习记忆v2是本合同新建议（原FR011未单独规定），采用包中明确增量。provider/账户/价目/真实语义及当前Docker缓存/扩展版本是未知，在相应采用/运行时核，不把未知记成当前失败或增加无关硬门。

| 已确认需求 | 主归属 | 已有充分部分与STEP018还需完成 |
|---|---|---|
| FR001、DR001/003 | M01/M02 | 继承逐文件/PDF/version；新增资料到两链、替换后不混上下文并保留草稿。 |
| FR002/003/012 | M03（面试M09）、M11 | 继承目标/范围/文字；新增完整入口、澄清后继续与同库重开。 |
| FR004、NFR001、INT002 | M04 | 继承定位验证；新增融合检索、跨链证据装配、逐结论语义支持/真实服务质量。 |
| FR006/007/008 | M05 | 继承领域事务；新增完整链及数值、概念、程序正反例，不用字符串评分。 |
| FR009、SEC003 | M07 | 继承G11固定宿主安全切片；新增当前练习/反馈真实交互关联与失败保持。 |
| FR010 | M06 | 继承保守推进和理由；新增复测反馈到保存/后续路径使用。 |
| FR011 | M09 | 继承文字场次/追问纪律；新增完整链、真实有据认可与缺证具体补充。 |
| NFR002/003、SEC001/002 | M10 | 继承限额/监督/脱敏；新kind/profile不可绕过，provider和费用采用门另列。 |
| NFR005 | M08/M11（面试背景M09） | 继承记忆查看修正撤销；同库续作及面试背景是实际不足，不以只读恢复替代。 |
| DR002 | M12 | 继承R01可读退出；新增R02包括检索调用事实，不复制执行资格。 |
| NFR004 | 验收合同 | 冻结有限样本、分层逐例保存。未运行，全部新验收待证。 |
| CON002 | M13 | 使用现有核心/Compose/许可；Redis可重建缓存、MCP/框架、Linux/Nginx未来条件不新升首版门。 |

## B. 正常/失败时序与实施细节

### B1. 两条流程只接现有领域命令

学习：导入并核对 →明确选ready版本/用途/上限 →创建同一活动 →目标保存（可复用合格G7 seed；有选记忆走teaching）→一次显式“准备本活动检索” →必要澄清并修订目标 →plan →用户accept_path →exercise(initial) →answer零费用原文保存 →evaluate →正确部分认可/实际错误/未知归因分别展示 →用户选针对练习(exercise continuation，绑定当前feedback/纠错) →有需要时有限计算或固定交互解释 →retest →evaluate同事务保存progress及保留/推进理由 →显式继续下一节点。缺目标/同名歧义时保持该阶段，不用额外无限Agent循环。首题参考答案默认隐藏，用户显式查看记录exposure；后续不能抹除exposure来凑独立作答。

面试：同样的资料/当前范围 →新interview域活动（不把已教学活动改域）→start/goal及resume/experience/measurement/reference角色 →显式检索准备 →ask →answer原文零费用保存 →review；确有材料/回答缺口时输出probe，用户回答后再次review →相应认可/证据不足具体补充/可追溯反馈 →finish保留历史。probe不为凑次数，最多2层（兼容现有1—4可配范围）；没有测量不能编造百分比。v2可在创建时显式选≤4条记忆作背景，不当简历/测量引用；对已启动场次不偷偷重选。

通用单次时序：读取当前源/记忆/head资格 →构造冻结请求及hash →短事务accept（同键不同正文409；同键同正文GET原事实）→一次launch claim →RootLease/执行generation →短事务admit并持久预留次数/费用/运行时长 →dispatch前复核 →单次外部HTTP →worker校验合法返回 →`received + 007正文 + 新向量/领域投影`同一COMMIT →SUP停止证明及现有结算 →GET回查当前资格 →UI显示。HTTP/模型/Docker不放进事务。

超时、cancel、坏schema、响应丢失及服务中断复用现有分类：确未发送才not_sent；发出后不确定是UNKNOWN并保留预留，绝不自动重试/退次数。结构不合法可能已收费，保存脱敏错误和收到事实但不授领域资格。COMMIT后响应丢失先GET同键/operation，不能以UI报错再次创建收费调用。cancel后晚到可保存事实，必须抑制当前正文/向量与进度投影。源、scope、goal/head、记忆修订或epoch变动均使旧冻结命令失效；用户文字草稿和历史元数据保留。

### B2. 受控检索的具体边界

新增`embedding.v1`；供应商候选固定为智谱开放平台`embedding-3`、请求`dimensions=512`，HTTP POST候选`https://open.bigmodel.cn/api/paas/v4/embeddings`。这三个字符串来自项目旧候选，仅作为待核采用对象，不宣称2026-10-14仍有该能力或价目。采用前必须核官方当前接口、固定模型身份、维度/批量/限额、币种计价、账户与条款。若不成立，Embedding关闭并回主控变更，不能降维/换模型/换供应商自动放行。聊天继续现有DeepSeek受控适配器；精确模型/能力见采用包。

空间键`space_id=SHA256(canonical({provider,configured_model,dimensions:512,normalization:'l2.v1',chunk_recipe:'lossless-line-2048cp.v1'}))`。返回模型、请求id、usage另记事实；返回模型不满足已核别名白名单拒绝。正文规范化只沿原片段换行/原文规则；不把用户补充改为原文。复用`build_fragments`的evidence_id，附source_id、source_version_id、source_revision、physical_page/origin、start/end codepoint、text_sha256。vector只在同space比较；NaN/Inf、零范数、长度≠512、索引不唯一/缺项、超body限拒绝。L2归一化采用一次确定程序，输入/原向量hash与结果hash留在007，不读真实资料做实验。

显式准备范围最多10源；本合同合成验收每活动≤8片段/最多2批，单批≤4片段、每片段≤2048codepoints。产品有限目录沿现有上限≤512候选片段，单准备命令最多128批；面向正常用户的“准备”先列实际片段数/必要bytes/预期调用数，超过本活动余量或目录限制时拒绝并请缩范围，不自动对整库索引。不能把合成样本8片段偷改成TXT/MD单文件输入新上限；大源是否在声明有限目录内必须明确呈现，超限不声称完整覆盖。按source/version/chunk逐条复用合法已存向量，命中不外发、不虚增收费操作；没有当前能力/费用许可不索引。新范围/替换不后台自动外发，用户重新确认。学习/面试每次需要检索的明确模型动作最多一次query embedding（query≤1024chars/4096bytes，本最小方案不新增跨命令query缓存）；HTML使用既有合格父上下文，无额外Embedding。

`build_retrieval_query`只从当前目标、节点/题干或面试问题构成必要查询；不把记忆正文或作答默认送Embedding，不拼整份简历。索引Embedding只送当前已确认source片段。两个用途都在admit/result核活动的当前memory eligibility和冻结selection/dependency身份；`_memory_require_call/_interview_require_call`新增严格typed EmbeddingBinding分支（purpose/command/scope/domain/selection hash），不凭emb前缀一般绕门、不假扮teach8m/int10m。记忆不进入Embedding input，但其撤销使该活动尚未完成命令失效；已经合格源向量是同space/source/version的派生缓存，不把旧活动的执行权限授给使用它的新活动。新活动仍独立核范围/预算/当前记忆/域资格。

`retrieve(activity_id, query, retrieval_command_ref, expected_scope_revision) -> CatalogEnvelope`：先由PG当前scope/currentready/删除tombstone及记忆资格过滤，再分别获取同space精确cosine候选≤32和原词项候选≤32；RRF(k=60)为`sum(1/(60+rank))`，用evidence_id稳定破同分；无ANN/重排外部服务。取≤8片段、沿现有≤12000chars/24000bytes总目录，重新从原件`verify_fragment`，PDF仍物理页/用户补充双身份。每个结论最终引用再回查当前版本/位置；排序分数不证明语义支持。向量索引不可用时显式`retrieval_degraded:terms.v1`且留原因，可读/已授权词项功能保留，但不能签hybrid验收。Embedding UNKNOWN不得暗中改用新query再次收费；需用户查原事实后明确改范围/新动作，旧预留不还。

### B3. 协议、函数与UI精确变更

以下新增名称为本合同规定，尚不存在。旧名称见M表和读取身份；同名函数实现变更应以实际span定位。

| 产品位置 | 规定的最小变更/签名和返回语义 |
|---|---|
| `capabilities/contracts.py` +新增`embedding.py` | `EmbeddingRequest(profile='embedding.v1', purpose:'source_index'|'query', inputs:tuple[EmbeddingInput,1..4], dimensions:Literal[512], space_id, activity_id, business_key, request_sha256, scope_revision)`；每input含ordinal、identity/hash、text。`EmbeddingServiceConfig`只允许候选固定base/path、环境变量名与已核模型/返回别名；工具集空、output_tokens=0。`EmbeddingOutcome`独立结构，含vector/usage/returned_model/remote_request_id与received/not_sent/unknown事实，不伪装成ChatMessage/TeachingOutput。 |
| `capabilities/gateway.py`、`transport.py` | 保留聊天实现；新增`ControlledEmbeddingGateway.call(context, request)`，共用Httpx的无redirect/trust_env=False/无隐式retry/1次POST语义；服务timeout≤10s、request/response≤65536bytes，不记录key/input原文。超限在调用前拒绝，响应超限按可能发出事实处理。 |
| `worker/one_call.py`、`worker_main.py`、`launcher.py`、`session.py` | 新wire v4封闭`capability_kind=model|embedding` union。v3聊天继续旧解析，不更改旧字节；父/worker均核类型与profile。新增`EmbeddingOneCallInput`、`run_one_embedding(ledger, session, activity_id, executor_id, operation_id, request, config, *, run_tag)`，继续同SUP/Job窗口/RootLease。禁止任意命令/自由网络/SDK二次调用。 |
| `activities/repository.py` +新增`retrieval/repository.py` | `admit_embedding(context, operation_id, intent, binding)`、`record_embedding_outcome(credential, outcome)`：同一锁序、generation、取消、预算、current source检查；kind=embedding，显式无输出tokens且不扣tools；次数/费用/时间照扣。received的007正文与相应chunk向量及命令进度同COMMIT，同键重复逐byte等效；普通`record_outcome`仍只认model，工具/领域/preview parent API必须拒embedding。 |
| 新增`retrieval/service.py/contracts.py/api.py` | `prepare_index(aid, command)`、`prepare_query(aid, command)`、`read_command(aid,key)`、`retrieve(...)`；HTTP `POST /api/activities/{aid}/retrieval/commands`、`GET .../retrieval/commands/{key}`、`GET .../retrieval/status`。命令严格`business_key, action,index/query input, expected_scope_revision, expected_domain_revision, confirmed:true`；服务器冻结源/当前领域父记录、space/profile与输入hash。返回accepted/launch_claimed/terminal元数据、每批operation ID和未知原因；向量及原文不返回浏览器。 |
| `activities/api.py/service.py`、`service_config.py` | capabilities增加`retrieval`、provider+用途/bytes/估计次数、v2 profile readiness；create增加可选`expected_sources`（ID/version/revision），服务重新核；只从受信配置加入chat和embedding允许pair。旧create缺该字段仍按旧机制，不能由请求填任意provider/price/工具/外发权限。Embedding能力配置缺失时默认关闭；修正teaching profile展示与真实memory.v2选择，不改变旧协议语义。 |
| `learning/contracts.py/service.py/evidence.py` | 保留learning.v1 terms存量；新增learning.v2/hybrid目录标识及检索命令引用。无选记忆的G7可用；有选记忆不放开旧learning.v1门，入口转teaching。所有继承引用ID仍可原位验证，不更改旧请求hash。 |
| `teaching_contracts.py/teaching_service.py/teaching_evidence.py`、`activities/teaching_repository.py` | 新`teaching.v3`在现v2 memory recipe上增加`retrieval_ref={business_key,query_sha256,space_id,result_sha256}`，在freeze/admit/result均校验其当前资格；v1/v2旧读取与hash原样保留。`_submit_model`使用检索目录而不现场绕账发Embedding。原领域记录/CAS/进度策略不复制；必要澄清仍由已有Output与用户goal修订承载。 |
| `interview/contracts.py/service.py`、`activities/interview_repository.py`、`memory/repository.py` | 新`interview.v2`同时加retrieval_ref及可空`memory_recipe/selection_sha256/dependency_sha256`。复用现≤4条、版本/hash重查、低信任材料化容量规则，记忆不得进入source_refs/recognition已证栏。start准入仅允许新v2、fresh、零操作/无teaching且合法显式memory binding；旧v1仍要求unselected。`_memory_require_call/_interview_require_call/_interview_domain/_interview_verify_frozen/_interview_result_sql`按严格profile绑定扩分支，不能凭operation前缀绕过；既有source→memory→activity→domain→operation相对锁序不变。收费新grant先取其advisory lock，详见采用包；没有反向取grant的嵌套路径。新增v2使用独立`int18m.`前缀，旧`int10m.`结果原样可读。 |
| `frontend/src/main.tsx`、`activities/ActivityWorkspace.tsx` | `onStartFromMaterials({sources:[{id,version_id,revision}],domain})`只填范围草稿；显式域/目标/预算/必要外发确认。新增`initialScopeDraft`prop，刷新重核，保留旧选择/文字。activity详情以既有domain/head显示当前步骤及下一合格动作；“重开/继续”先GET，不自动POST。 |
| 新增`frontend/src/activities/RetrievalPanel.tsx`与接口 | 在活动内显示必要资料范围、用途、供应商、预计次数/费用及余量。`submitWithRetrieval(action,input)`在一次明确确认中冻结查询key和领域key，顺序完成最多一次query及一次原领域动作；仅当前owner/view/上下文仍有效且前一步确已COMMIT时继续，失败/卸载/响应未知立即停此链。重开先GET，再由用户明确继续未发送的原键；不得重放unknown。首次准备索引告知实际有限批数（本合成许可最多2批），后台不得自行续剩余批。技术space/chunk/SQL不进产品主流程；命令状态与domain/head、DataContext共同绑定。 |
| Teaching/InterviewWorkspace、`MemoryWorkspace.tsx`及其api/types/意图台账 | 重用已有IndexedDB/owner/view/CAS，新增profile字面值/检索引用/场次记忆选择；参数/旧回答草稿本地保留。显示clarification/conflict/no_evidence下一可行修正、针对练习/复测/理由，并区分模型建议/确定核算/自报。route/只读壳和C03最终bundle guard保持；v2记忆资格失效时禁止请求并抑制旧正文，不吞旧意图。 |

采用新增schema/profile只能作为新非空迁移的一部分，不能在独立“准备”卡里先打开provider或未知接口。所有新API仍过现session token、localhost、DataContext与mutation gate；restored_readonly只允许status/GET合格元数据，POST一律拒。GET不得触发索引/模型/SUP。

### B4. 014迁移的持久定义、旧行及权限

推荐只有一份前向`backend/migrations/014_step018_retrieval.sql`。001—013原字节不变；新DDL在新的**正常合成库**测试，通过后再提供正常本人库明确迁移命令，TASK116不迁移任何库。以下为规范DDL字段，不是已执行SQL；uuid/text/bigint/jsonb/check/FK名称可由实现规范化，但含义与空值兼容不能删。

```sql
CREATE EXTENSION IF NOT EXISTS vector; -- 须实核已缓存PG镜像中的版本/许可和可用性
CREATE TABLE retrieval_spaces (
 space_id text PRIMARY KEY CHECK(space_id ~ '^[0-9a-f]{64}$'),
 provider text NOT NULL, configured_model text NOT NULL,
 dimensions smallint NOT NULL CHECK(dimensions=512),
 normalization text NOT NULL CHECK(normalization='l2.v1'),
 chunk_recipe text NOT NULL CHECK(chunk_recipe='lossless-line-2048cp.v1'),
 created_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE(provider,configured_model,dimensions,normalization,chunk_recipe)
);
CREATE TABLE retrieval_commands (
 activity_id uuid NOT NULL REFERENCES activities(id), business_key uuid NOT NULL,
 action text NOT NULL CHECK(action IN('source_index','query')),
 space_id text NOT NULL REFERENCES retrieval_spaces(space_id),
 scope_revision integer NOT NULL CHECK(scope_revision>0),
 domain text NOT NULL CHECK(domain IN('learning','interview')),
 domain_revision integer NOT NULL CHECK(domain_revision>=0),
 request_body text, request_sha256 text NOT NULL CHECK(request_sha256 ~ '^[0-9a-f]{64}$'),
 source_refs jsonb NOT NULL, parent_refs jsonb NOT NULL,
 query_sha256 text, manifest_sha256 text NOT NULL,
 batch_count smallint NOT NULL CHECK(batch_count BETWEEN 0 AND 128),
 status text NOT NULL CHECK(status IN('accepted','launch_claimed','terminal')),
 terminal_disposition text CHECK(terminal_disposition IN('received','not_sent','unknown','invalidated','partial','cache_ready')),
 result_sha256 text, error_code text,
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(activity_id,business_key),
 CHECK(request_body IS NULL OR octet_length(request_body) BETWEEN 1 AND 65536),
 CHECK(jsonb_typeof(source_refs)='array' AND jsonb_array_length(source_refs)<=10),
 CHECK(jsonb_typeof(parent_refs)='array' AND jsonb_array_length(parent_refs)<=12),
 CHECK((action='query' AND batch_count=1 AND query_sha256 IS NOT NULL
        AND query_sha256 ~ '^[0-9a-f]{64}$')
       OR (action='source_index' AND query_sha256 IS NULL)),
 CHECK(batch_count<>0 OR (action='source_index' AND status='terminal'
                         AND terminal_disposition IS NOT NULL
                         AND terminal_disposition='cache_ready'))
);
CREATE TABLE retrieval_chunks (
 space_id text NOT NULL REFERENCES retrieval_spaces(space_id),
 evidence_id text NOT NULL, source_id uuid NOT NULL REFERENCES material_sources(id),
 source_version_id uuid NOT NULL REFERENCES material_versions(id),
 source_revision integer NOT NULL CHECK(source_revision>0),
 origin text NOT NULL CHECK(origin IN('original','user_supplement')),
 physical_page integer CHECK(physical_page>0),
 start_codepoint integer NOT NULL CHECK(start_codepoint>=0),
 end_codepoint integer NOT NULL CHECK(end_codepoint>start_codepoint),
 text_sha256 text NOT NULL CHECK(text_sha256 ~ '^[0-9a-f]{64}$'),
 vector_value vector(512), vector_sha256 text,
 committed_activity_id uuid NOT NULL, committed_operation_id text NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(space_id,evidence_id),
 FOREIGN KEY(committed_activity_id,committed_operation_id)
  REFERENCES activity_operations(activity_id,operation_id),
 CHECK((vector_value IS NULL)=(vector_sha256 IS NULL)),
 CHECK(vector_sha256 IS NULL OR vector_sha256 ~ '^[0-9a-f]{64}$')
);
```

索引准备的request_body只存请求**身份清单**/目录hash/批清单，不存重复原件文本；query正文为用户明确该动作必要文字。批固定operation id `emb18i.{business_key}.{ordinal}`（0..127，本合成许可仅0/1），query为`emb18q.{business_key}.0`，命令读取按这组确定ID回查operations及007；不需第四张批表。全部源向量合法命中时batch_count=0，短事务直接保存terminal/cache_ready及当前manifest/result hash，零operation/外发/收费，不伪造received传输。有新批时整个命令只claim一次，正常同窗口按已确认有限manifest顺序处理；中断不后台重开。全部批received且当前资格一致才complete，任何可能发送未知为unknown；已收到部分且余批确未发送为partial，逐批事实分别呈现，不能假写整命令not_sent或索引全ready。原已COMMIT向量保留，后续显式准备只处理仍需的片段并对旧unknown告知可能重复费用、保原预留。查询向量在007合格结果中，源向量落chunks。request_body可被删除事务清成NULL，仅保hash/元数据，不能以NULL重新提交；immutability trigger仅允许受信purge lane执行这一动作。source_refs/parent_refs须有封闭JSON schema、无用户任意SQL；端点输入只允许服务器重新构造该冻结体。结果正文≤131072bytes沿007，单Embedding响应≤65536bytes；解析和序列化须同时计wire/007限额。

Embedding的007值固定`{profile:'embedding.v1',purpose,space_id,request_sha256,manifest_sha256,inputs:[{ordinal,identity_sha256,vector:[512 finite numbers],vector_sha256}],usage}`，外层继续007 format/json及当前admission/scope/generation归属；source_index/query不能互认，不把此值放进聊天messages或学习结果接口。endpoint body上限65536、UTF8/codepoint上限均前拒；query/index冻结体另含domain/head/selection/dependency身份，来源text由worker前重取校验，不由浏览器指定。GET返回command/meta、逐batch operation事实、current eligibility和目录coverage，不返回向量/secret。置信语义不从vectors/距离或schema推定。

014同时精确扩`activity_operations.kind`检查为model/tool/embedding；保留008现有model分支（request_bytes/max_output_tokens/预留费用正数）及tool分支（前两列NULL、费用0、arguments/tool_call身份要求）原含义，增加embedding分支（provider/configured_model非空、request_bytes正数、max_output_tokens=0、预留费用正数、tool_names空、arguments_sha256/tool_call_id为空且存在检索绑定），不能用“所有非embedding都tokens>0/费用>0”破坏非空旧tool行。旧model/tool行不回填、不重算费用。014另增加activities可空outbound_grant_sha256，旧行NULL；新收费准入由受信grant固定roster/global PG预留合计核20元/80次，详见采用包，不加第四张通用账表。新embedding插入/结果触发器核绑定prefix/command/源版本/space/完整input manifest/credential/generation；任何embedding的007正文禁止被learning/teaching/interview/html当父。新增检索事实写入不伪造执行权限，cache资格每次实时核。

新增`retrolume_retrieval_owner` NOLOGIN无super/bypass；`retrolume_retrieval_app` NOLOGIN只授精确SELECT、必要INSERT/UPDATE列，不授DROP/任意DDL、DELETE；应用正常登录通过现role映射获得需要的两种角色。不可变identity/hash/FK及结果guard固定search_path，purge限定SECURITY DEFINER函数由现维护lane调用，PUBLIC execute撤销。三表每张都有R02 data_runtime_write_guard，snapshot只SELECT受控列，loader仅loading期插入，seal撤销loader/应用写。授原data_state/data_loading_allowed必要EXECUTE到新owner，禁止因新表给snapshot/runtime超级权限。旧memory/interview/teaching函数profile变化的精确指纹同时更新R02注册；R01检测留原字节投影，不把未知DDL宽松认作兼容。

### B5. R02退出/删除/恢复增量

新profile `data_exit.v1.r02`包含001—014可信链、31业务表（R01的28+上述3）及原3控制导出视图。013 schema_profile固定CHECK不能原地编辑：014替换为R01/R02允许集合，并仅在正常、无活动执行/预览未清/数据操作未清且maintenance fence持有时将本次新正常库改R02。新包schema_profile/链hash/表shape/角色/函数/trigger和向量空间写明；旧R01包不改、不假装存在新表。采用前核本地vector扩展版本纳入profile身份，未知版本拒绝，不能用模块版本猜。

`data_exit/schema_profiles.py`注册R01/R02两份精确常量；`schema_checks`按当前注册profile核对，不全局替换28→31放宽；`ReferenceRootCoordinator`/control/reference pin核profile与dataset/instance/root/epoch同步，继续TASK114的live pin/deadline。`snapshot`、`codec`、`packages`、`readability`、`restore._initialize/_load/_components/seal_readonly`增量用该registry：R01仅1..13链，R02仅1..14链；vector按512个有限十进制数编码、逐项和hash校验，restore无需联网/重嵌入。快照必须包含retrieval_commands和embedding operations/007真实unknown及预留，不因“索引可重建”丢收费事实。向量缓存允许丢失后显式重建，但旧受控调用事实不可丢。

删除源版本/源/记忆沿原tombstone+维护fence/关联闭包：受影响chunk.vector_value/hash清空或由受限purge物理删除；受影响source_index/query的007向量正文通过固定`purge_retrieval_payloads`删除，保operation/命令元数据、请求hash、费用与unknown。该函数仅维护fence/鉴权lane可执行，只删kind=embedding的result行，不改旧model/tool结果保护；新增NOLOGIN owner仅因固定函数取得必要DELETE，PUBLIC/运行登录不能直接删除结果。源索引请求体不存原文，受影响命令正文可NULL且终态不可重交；独立用户query/作答按既有用户记录保留/抑制政策，不假称物理删除全部用户文字。不得让007或cache成为被删源正文/向量的旁路。重建必须新显式许可且仍计累计预算。记忆变动不重嵌入资料，却使绑定它的query/模型命令资格失效。删除前影响展示增加检索对象计数与必要清理范围；旧备份不自动删除，恢复沿现覆盖tombstone策略，deleted-source向量不加载，历史收费元数据仍保留。

R01恢复仍新隔离副本、永久restored_readonly；R02也一样，严禁把恢复copy变正常、继承lease/SUP/CID/私密或自动索引。R01应用重开只用R01可信链/读取兼容分支；没有014时hybrid/新写门关闭，正常历史GET不凭未识别DDL失败后回退另库。R02装载只在新loader角色loading，逐表/007/向量/hash/空间/权限核对后seal；verification失败保留隔离failed对象，不激活。原R01证据继续有效，新证只覆盖014/profile/新表/跨链传播。

### B6. 同库重开与一次本机启动

本人Windows、127.0.0.1绑定、PG为Compose服务，API在Windows原生进程内保留Windows Job监督，预览由外部SUP动态拥有容器。没有把应用放Linux容器、把Docker socket给Web应用或新增常驻renderer。Redis目前没有客户端/业务依赖；PG为权威、轮询/GET足够首版，Redis只保留既定可重建缓存方向，采用前核版本/许可。MCP不是有限计算的运行依赖；沿现有限工具gateway，不新起MCP服务或LangChain/LlamaIndex/第三框架。新Embedding用httpx+现psycopg原生SQL，无新增SDK依赖。Nginx/完整Linux和公开发布为后续条件交付，不以renderer Linux运行冒全应用兼容。

最小修改`deploy/start_local.py`，增加受信`--profile <operator profile absolute path>`及`--initialize`/`--migrate`显式动作；默认仍本人normal配置，草案合成profile精确资源见实施卡。就绪报告只给mode/schema/profile/能力/理由、端口/秘密是否就绪，不打印值。配置示例使用环境变量名字：既有RETROLUME_ACTIVITY_CONFIG/MODEL_API_KEY、PREVIEW_CONFIG/PREVIEW_REVIEW_KEY、DATA_SNAPSHOT_URL/DATA_MAINTENANCE_KEY；新增RETROLUME_EMBEDDING_API_KEY和受信retrieval配置字段。private文件由用户/operator正常安全配置，设计不读取、不向用户索key；安全脱敏沿当前logger/导出政策。

启动顺序：校准UTC/mono与资源profile →仅查精确缓存image/卷/CID/labels →Docker已唤醒后可用内存≥2GiB，采于每个新PG/浏览器/预览前（同窗上次不替代实采）→检查所有实际待绑定端口：无listener且bind probe成功方准；同名应用listener仅可身份匹配后复用；其他listener、排除范围WinError10013、只bind失败、未知owner一律明确冲突、不kill用户进程/换端口绕计数 →读取服务器安全配置、验证模型/预算/签票/profile门 →新库显式initialize或正常库显式migrate（预先R01可读备份）→PG readiness核配置实际user/db，不硬编码retrolume →创建hidden uvicorn且记录PID+birth/控制handle →session/capabilities/前端同源就绪 →显示缺能力而非偷偷切库。PG/迁移不可用时留错误与资源ID，不启动业务模型；未完整配置时只读现有成果保留。

一次停止：先拒新mutations，等待/取消属于本launch的窗口并取得既有StopProof，预览按精确CID/nonce/两Job/EOF核证；没有确认标unknown不假写stopped。API对该PID/birth发CTRL_BREAK并保留现有有界20/5/3秒退出流程；仅停本launch启动的精确PG，启动前已由用户运行的不擅自停。卷/数据库/镜像/失败对象保留不自动销毁。Docker daemon和用户进程不在停止范围。

同normal库再次启动：selector、dataset/instance/root必须当前一致，确认旧session/SUP不在途，取得同一全局owner与持久generation。受信profile明确single-host/single-session并允许现session recovery；缺声明/旧birth/停止不确认证据只关闭执行门，GET保留。先GET原意图/命令/operation/heads/预算，UI显示“原调用未知，只读核对；余量未重置”。已COMMIT结果可直接继续下一明确动作；未发送且未claim可显式重交同键，已claim/unknown不可自动POST或重新付费，取消活动不授新旧资格。达到deadline/次数/费用不能重新打开同活动；用户另建活动仍保项目总费用/失败账，不借新号清尝试。选择restored_readonly只重开查看，永不与normal续作混称。

### B7. 基线、许可和产品文档修改

本次只读Git HEAD为`45951501d2741630a229762d6b2d3f4b34d7f702`，porcelain633行含既有删除/未提交源码，原件见design/git-status-before.txt及git-baseline.json。不能把这些改动认成TASK116，不能reset/stash/整仓格式化。关键实际源身份在source-identities.json；编排前只补本卡真正变更文件的冲突核对，不重hash243件。

复用PG缓存image `sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f`、G11 v2-08 renderer `sha256:ec3c70c7a8a8894c647a69b08b0c296727bb052f639e487567e9cd4624766789`、load `8a047050ffe584dffa6e85222c16c8f400c0ab4db82f72a32812c2befd082b3f`及renderer `6cc300164a6cb364d9bd0bae4897f06d3f6a65cf5d4272477d2bccde67312597`。这是原111/112已核事实，TASK116未查Docker缓存/启动；后续启动核现cache，不存在则停该能力，不pull或复活旧对象。签票由原独审既有结果的正常operator部署程序提供，工程不得自己伪签；新embedding/profile审计不重签未改的固定runtime。

现锁定fastapi0.141.1/pydantic2.13.5/psycopg3.3.5/httpx0.28.1/uvicorn0.52.4/pypdf6.17.0、React19.3.0/TS7.0.2/Vite8.3.0/PW1.62.1保持；使用repo内锁与许可原件，不从公共提示词库/DocuN runner或外部参考路径供产品运行。新vector扩展身份及新服务条款由采用包核，历史许可材料不是今日条款。产品新增代码必须backend/frontend/deploy，样本/证据可在新任务DocuN，不能把测试实现变产品依赖。

后续精确文档修订：README资料footer/学习入口“后续接入”改实际流程；词项限定保留为fallback，加入hybrid readiness及费用提示；补teaching配置示例；记忆候选与“完整退出未授权”按已裁定有限STEP017改写限定事实；deploy/preview README旧v2-01/候选/待审文案改v2-08实际签票与有限范围；本机启动/迁移/重开、normal与readonly差别、采用前provider/费用/资料条款、端口与内存收尾说明写入README。原任务失败/报告、用户需求/公共规则不修改；本卡不修改上述产品文档，主控维护正式DocuS时不签未实现的Must。
