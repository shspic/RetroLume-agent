# TASK-099 / R-093 G8完整推荐实施合同

A—D已收敛为一张完整实施长卡的合同，推荐增加三张有限教学领域表并接入现有受控链；仅需裁定一个持久模型及接口批准包，本轮未实施、未运行，也未作独立审计或项目验收。

## 1 交付身份、事实及证据

本轮为2026-10-02，Asia/Shanghai。项目根为D:/shspic/project_NO3_RetroLume-agent，入口为D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。模式为task_model，锁定V4.0、公共AGENTS CHG-0003。有效需求v1.1、架构v0.76、执行v1.98。本文是唯一推荐合同，不是另一份项目状态账，也不是已经派发的TASK100。

实际执行者为当前Codex桌面会话，系统身份为Codex/GPT-6；未获得更细客户端模型标签和原097窗口的可核查身份，因此按恢复后的业务设计窗口记录，不假称原097窗口或098独立审计窗口。A+是接收执行档，不作为实际模型身份。没有派子Agent。

已读项目入口、用户粘贴卡、TASK099输入索引、锁定规则快照，公共AGENTS全文及WORK的task_model和4/6/8/9适用段，07执行循环、任务模板，并补读05/06适用条款。公共00仅核指纹，没有读其正文或切换阶段。当前执行账只读顶部及STEP009—013合同，未采用历史“待批准基线”撤销后续有效授权。

输入索引SHA256为d1a6da5301822003de26ce74c2cfef4602508785484f74b81cf89cb89424574f，实核相符。索引指定38项文件实核均无漂移，七份锁定规则指纹均相符。正式文档更新与产品漂移分别判断。定向源码函数、读入范围及当前SHA256见D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-099/read-manifest.json；文档对应检查及保存回读见同目录document-check.md、delivery-proof.json。未作全仓指纹。

已读需求相关FR逐项Must及第7/8/13节、架构当前增量与FLOW002—005/MOD/API/DATA；097限定验收文件及098的范围限制和旧夹具两缺陷。没有重读691输入或完整旧日志。G7有效子能力包括terms.v1有限权威目录、learning.v1首次/续问、原子正文、父消费、引用和意图恢复。它没有目标版本、教学路径、作答/反馈/复测持久闭环，不能当完整记忆。097 bootstrap和依赖runner整体禁用，identity/partial保护及close/terminate观察路径风险保留。

关联STEP009/010/011/012，DR002/NFR005的有限查看修正和版本恢复边界；FR002/004/006/007/008/010/012，NFR001—005，DR001—003，SEC001/002，MOD001/003/005/006/007/008，FLOW002/003/004/005，API002/003/005/006，DATA004/005/006/007。下文省略编号内连字符仅为阅读方便，不重新占编号。

本轮产品、测试、迁移、配置、正式DocuS、公共库、旧证据、原始需求及Git写入均为零。编译、unittest、build、PG、Docker、浏览器、Windows Job、应用、模型、联网安装均为零。只做阅读、定向hash、文档写入及一致性检查。材料中的SQL、类型与函数签名均为未实施提案。没有把手工推演称为运行或真实模型验证。

## 2 现有实现的函数级事实

F01。backend/app/learning/contracts.py的LearningProfile和StoredProfile固定learning.v1，action只接受first/followup，max_output_tokens为1..256；normalize_input限制1024字符/4096 UTF-8字节。内部profile含父hash和history，公开持久profile排除二者。CatalogEntry验证源/版本/代次、片段hash及位置；validated_output检查引用集合，不能证明语义支持。parse_output拒重复字段、非有限值及16384字节超限。

F02。learning/service.py的LearningService.execute(activity_id,business_key,text,config, parent_operation_id=None,run_tag=...)按是否有父项区分首次/续问。续问调用read_committed_result，要求committed_current、kind=model、合法learning.v1正文，再构造ResultConsumptionRef。首次稳定前缀learn-first-v1.，续问learn-next-v1.<UUID>.，指纹包括目标、问题、scope、源身份、父hash和输出上限。reconcile对首次按整个稳定槽定位，客户端业务键不是首次实体ID。

F03。LearningService.execute先读取read_learning_snapshot、配置和预算，再load_units/assemble_catalog、messages_for、ControlledModelGateway._build_payload及OneCallInput.to_wire预检，随后run_one_call。asyncio.shield保留有界监督收尾；响应正文通过ActivityService.read_result读库，不相信跨进程正文。adapter.validate_learning_request在实际worker取得租约之后复核context、消息、父成果、来源及槽位。现有槽竞争的有效证据沿G7继承；其API前查不是本合同新教学竞争的数据库保证。

F04。activities/repository.py的PostgresAdmissionLedger._transaction(operation)每次新建有限连接及短事务，设置statement_timeout、lock_timeout、idle_in_transaction_session_timeout，只有退出事务后才确认。默认隔离下，多条SELECT不自动成为同一读取快照。_source_rows按来源排序；_lock_sources锁material_sources核current_version/revision；_verify_scope_hint在锁活动后复核范围集合。revise_scope(activity_id,expected_scope_revision,sources)按旧新来源并集→活动锁及CAS更新；它不自动改教学目标，也不恢复旧正文资格。

F05。admit(AdmissionIntent)在来源→活动→排序后的当前/父operation锁内检查running、dispatch_closed、executor、G、scope、租约、截止、模型/工具授权、请求字节/输出、次数和费用；受信父引用还核received及正文hash。通过才同事务requests_reserved加1、费用预留加一次及INSERT model操作。没有零费操作kind。mark_dispatch_started再次检查并消费reserved→dispatched唯一资格。

F06。record_outcome(permit,outcome)依次执行_outcome_values/_payload_values、_locked_operation、_terminal_confirmation，随后资格/未发送/关门检查，再_write_outcome。在同一真实事务更新received及INSERT activity_operation_results。终态严格等值的无写幂等先于当前资格拒绝；旧received无正文不能补正文，UNKNOWN不能补成成功。_operation_is_current自身不含dispatch_closed，正文分支另核关门。这一顺序必须保持。

F07。admit_tool_operation(ToolIntent)、mark_tool_started(permit,call)、record_tool_outcome(permit,call,outcome)是G5专用链。kind=tool不伪造provider/token/费用，只在准入时tools_reserved加1；工具不接受not_sent终态。ControlledToolExecutor.call按admit→mark→事务外execute一次→record，同一规范参数与摘要贯穿。ToolRegistry仅finite_calculate的add/subtract/multiply/divide/power，参数2048字节、绝对值至1e12、整数幂绝对值至12、结果至1e18、Decimal精度50，不执行用户程序。

F08。read_committed_result/list_committed_results及read_operation/list_operations使用同源来源/绑定资格。_RESULT_READ_SQL区分scope_current、sources_valid、binding_consistent；取消历史可读，失效来源正文抑制。read_operation是一条SELECT；list_operations不取正文，按operation_id升序。read_learning_snapshot是一条有限元数据SELECT，至多11项用于拒绝超10来源；TXT/MD当前有效，PDF须确认且页表齐全。read_scope_source_versions只读当前身份。

F09。001—008中activities.status仍仅pending/running/cancelled，G是执行代次而不是目标版本；004有M/R/S守恒与running形状，005关门，006旧owner_session=NULL不能获得自动恢复权，007正文PK(activity_id,operation_id)且FK操作，最多131072字节，008保留旧行为model并增加有限tool域。007没有用户作答、目标修正、父阶段唯一性或零费事务入口。不能伪造model/tool行和零token/零费用以塞教学事实。

F10。worker/one_call.py的OneCallInput.to_wire检查typed request自身65536字节，配置的request/response各至65536，含服务的call数据131072字节；协议3回执只携状态/身份/hash。worker_main.execute_one_call→ClosingCallGate→gateway，WorkerCommand固定idle/one_call/one_tool。one_tool内协议4保持精确字段。SUP映射物理槽512KiB不意味着业务可用512KiB。SessionConfig默认W90秒、请求10秒、管理总120秒，HTTP默认single_host_single_session_recovery=False。服务配置实际L2还限timeout≤10秒，不能只引用ModelServiceConfig的120秒域宣称HTTP可用120秒请求。

F11。service_config.py的_ActivityDefaults目前allowed_tools长度0、max_tool_calls=None，_LearningSection仅learning.v1/256；内部G5可用不代表浏览器已启用工具。L0读/取消、L1新建、L2模型层分开，缺配置/密钥失败关闭。activity.example.json是全零占位模板。本合同新teaching层和可选核算层必须显式配置，不能静默把旧活动加额度。

F12。frontend的pendingIntents保存业务键和用户输入；compareLearningIntent比较目标/问题/父ID。ActivityWorkspace.createLearningIntent/submitLearning先本地保存再POST；read/refresh只GET。refreshDetail并读活动与操作，两个端点各有自己的快照，不能把它们当新教学一致快照。已有sequence、selectedRef、mountedRef、3秒无重叠/隐藏暂停轮询及LearningResult引用AbortController可薄复用。现有台账未给新长作答总容量保证，需新有限版本，不无界扩旧数组。

F13。activities/api.py._guard使用local_session(allow_own_origin=True)，校验应用会话及同源/跨站；不是多用户ACL。main.create_app登记活动与学习router，API已有no-store及nosniff。新增入口沿此本地权限；不暴露DSN、key、provider、executor、G、预算或目录给客户端设定。

## 3 A 唯一业务、状态与权威合同

### 3.1 入口与目标版本

没有G7首成果时，允许在已存在且范围就绪的学习活动内零费保存目标，并直接进入teaching.v1规划；不强迫再跑一次G7才可规划。G7旧first槽没有被建立就仍为空，有就永不再first。目标已明确、范围不歧义但能力未知时用未知诊断生成暂定路径，后续练习观察再修订，不能为收集自报强制填无关信息。

有有效G7时，用户点击“沿用此目标”才将StoredProfile.goal作为新goal版本的输入来源。G7答案是有引用的历史建议，可作有限上下文，不等于已观察的用户能力，更不迁成掌握分。普通问答、旧摘要、模型自述及用户自报均标低信任来源。父成果的来源失效时只保留身份/不可用说明，不复制其正文入当前目录。

目标缺失或同名歧义时，只追问目标概念/领域中实际缺的至多两项，一次显示，零模型预检优先。时间/偏好可空。诊断记录三种claim_kind，self_report为用户自报，observation必须指已保存answer/feedback版本，evidence_judgment附范围引用及不确定性。没有观察就unknown，不从目标文字推断能力。

目标版本每活动1..32。O01提交新goal记录，不改旧goal、旧learning.v1正文或历史反馈。新版本在数据库COMMIT时生效，head.revision增加1，旧path/exercise/answer/feedback成为历史；当前路径清空，回needs_plan。旧目标的在途命令标obsolete并清当前pending引用，不递增G、不清租约或四账。旧请求若尚未越过准入/mark即拒；已出站不能撤回。旧结果若G/scope/来源/门仍合法，只能存历史，不能推进新head；这些资格已失效则仅原UNKNOWN诊断，不能新存正文。第6节给真实事务实现。

范围失效时，读页置只读来源失效覆盖层，停止新模型/工具。用户本人的目标、作答可历史查看；资料派生正文及引用按失效规则抑制。合法下一步是核对/保留草稿、取消或显式新建活动选当前资料，再保存目标。没有自动搬预算、没有在旧first槽重发；完整跨活动记忆/资料物理删除不在本切片。

### 3.2 持久阶段与模型建议边界

head.phase只有needs_goal、needs_plan、path_review、ready、exercise_ready、answer_saved、feedback_ready。processing、unconfirmed、source_invalid、cancelled、expired、budget_exhausted是根据commands/操作/活动/来源读取的覆盖层，不把activities.status改成教学词。

路径为1..6节点有向无环图，前置只指本路径较早节点。服务器把模型索引映射成n1..n6，实体身份为path_record_id加node_id。每节点含目标、依据、诊断出处/unknown、建议理由、完成维度。用户接受路径后才能出练习。模型提供有限建议及逐维度判断，应用决定是否接受结构、允许何种命令和是否推进。禁止模型输出trusted goal/scope/version/permission/progress/passed/mastered字段；出现额外权威字段整项无效，不能悄悄剥掉后采用。

节点投影只有not_started、practising、needs_repair、evidence_sufficient、deferred。完成依据是同目标/路径/节点下至少两个不同练习的未暴露独立作答，至少一个purpose=retest，所有必需维度在当前非争议反馈中有据满足，支持性检查无冲突，来源有效。对开放题这是“按当前评价，本步已有有限证据可前进”，并非客观长期掌握；长期能力仍unknown。单题正确只加一次本次观察，错误重复必须needs_repair/保留理由，不能毕业。

“不同练习”不能只换UUID或改写题干。数值题须改变实例数据并保持可核算依据；程序题须改变可手推输入/分支实例；概念题须采用不同应用情境并要求解释理由。应用作结构差异和暴露检查，语义上的迁移独立性还在代表性内容核查/真实provider样本检验，不能以内容hash不同自签。结构差异不足则标assisted/insufficient_novelty，不进入两个独立观察计数。

观察以answer_record_id去重，同题续答、重复提交、对同一作答的再评价不新增独立次数。一次答案的多版评价可以更换当前观察的解释，但保留所有版本；新旧结论矛盾或用户纠错未解决时，该观察contested，计数中排除。应用不能只保存一个熟练度数字。路径调整仅允许在已接受图内保留/针对修补/进入满足前置的下一节点；大改节点或目标需O02新proposal加O03接受，不能由反馈直接另建无限路径。

练习purpose为initial、continuation、retest。continuation关联同题前答，帮助修正但不算独立复测；retest关联此前feedback/练习，生成一个有限的新实例。题型为calculation、concept、program，每题有题干、允许答案维度、难度1..3、参考要点/解释、来源、适用节点及复测理由。题目/参考答案版本不可变；改题必须新记录。一个出题动作只产生一题，待用户显式继续。

参考答案、已展示提示与反馈暴露单独记exposure。服务端先COMMIT exposure再返回参考正文；回执丢失也保守视为已暴露。作答保存时冻结本题exposure集合。先答后看参考不会追改原首次独立作答；看过答案后同题再正确只能记assisted。生成新题不自动展示参考；不能靠前端折叠隐藏已经返回浏览器的答案。

### 3.3 全部命令与可执行迁移

以下共有契约称C。输入带activity_id路径、business_key规范UUID、expected_revision整数、expected_goal_version整数、expected_scope_revision整数及action的固定body。客户端版本只作CAS前提，不能授权。每次先本地持久意图再POST。所有owner均为用户显式动作→受信TeachingService→PostgresAdmissionLedger，模型只是有限建议来源。非副作用读由API/仓储负责，预算/G/停止始终由现有活动链负责。

通用成功事实是commands的原输入摘要、返回record ID/hash及事实资格；不能用HTTP200替代COMMIT确认。同键同规范内容先核原收据并只读重放，优先于当前版本失效拒绝；同键异内容409 command_key_conflict。不同键竞争同一语义父槽，同内容返回duplicate_of及唯一获胜事实，异内容409 stage_conflict。UNKNOWN仍占父槽，不能换键重发。已确定failed/not_sent的显式再试用retry_of，新键但原父槽与累计预算仍核验。

O01 保存/修正目标。输入C加goal{text,self_report?,domain?,seed_operation_id?,seed_payload_sha256?}。首次expected_revision/goal_version为0；修正给当前版本。前提为活动存在、有效本地会话、未取消/到期；本地保存不要求模型/次数/费用余额。COMMIT产生goal事实、goal_version加1、needs_plan、清当前下游引用及pending，旧命令obsolete。来源失效时仍可保存用户文字并更新目标，但source_invalid覆盖层阻止形成当前路径；CAS中的scope版本不符仍409，不能用旧scope强行提交。下一动作O02，缺信息则编辑O01，来源失效则新建选当前资料。目标未变的同内容另键作为无效应重复，不悄悄增加目标版本。模型0、工具0。

O02 生成/重订路径。输入C加plan{correction_record_id?,retry_of?}，使用当前goal和有限真实观察。前提needs_plan，或已有路径下用户主动重新规划；没有未解决的同父UNKNOWN/当前pending，L2教学配置、有效scope及原预算。服务器保存command和冻结context，然后用户此动作最多一次模型调用。合法path产物进入path_review；clarification/no_evidence/conflict保存有限结果及理由，保留原有成功成果，仍needs_plan或保持此前路径但标提案未形成。下一动作O03或O01补实际缺口；不自动再问。原已接受路径在新proposal未接受前仍可历史/当前查看，但O02在途不同时发另一付费动作。

O03 接受路径。输入C加accept_path{proposal_record_id}。前提该proposal属于当前goal/scope、result_type=path、图与来源校验有效，且没有在途当前动作。零费COMMIT path_accept，head.path指proposal，首个前置满足节点成为当前，phase=ready；清旧题/答/反馈及候选指针，为新图建立空观察投影，不把旧图观察自动算入新图。旧路径事件不覆盖。下一O04或O11。proposal只是建议；用户不接受则保留path_review，可O01/O02。模型0、工具0。

O04 获取练习/针对续练/复测。输入C加exercise{path_record_id,node_id,purpose,parent_feedback_record_id?,retry_of?}。initial需ready或当前节点重新练习；continuation/retest需feedback_ready，父feedback为当前非失效记录；有争议的反馈可用于提出验证问题但不当正确事实。前置节点满足，scope有效，无当前未处理练习/UNKNOWN。一次模型生成一题，合法产物COMMIT不可变exercise、phase=exercise_ready。参考未暴露。no_evidence等不替换旧练习。下一O05/O06。没有自动题目循环。continuation若改题则新exercise关联父题，独立性仍assisted；同题续答直接O06，不需再出题。

O05 查看参考/提示。输入C加expose{exercise_record_id,part:hint|reference}。前提当前题可读或历史题用户主动查看，本地来源资格成立；无模型/工具，也无新执行进程。一个零费事务写exposure及必要head修订，提交后才返回可展示片段。历史题暴露不改变当前head。响应丢失时核对exposure，能同键取正文，不新记暴露。若source_invalid则拒回派生正文409，保留输入。下一O06或只读；不会把已见答案的续答算独立。

O06 保存首次作答/续答/修正版。输入C加answer{exercise_record_id,kind:initial|continuation|revision,text,supersedes_answer_record_id?}。首答不能带supersedes；后两种必须指当前本题答案，链不可分叉。允许exercise_ready/answer_saved/feedback_ready及本题评价在途，保存是零费，不要求模型配置或费用余额。事务保存不可变answer、冻结暴露信息与来源身份、head.revision加1、phase=answer_saved，旧评价obsolete，当前反馈引用清除。已取消/到期不新增业务保存，草稿保留在本机；来源失效/旧题但用户要求留稿时只存history_only作答，不改变head。下一O07可选核算或O08。保存成功评价失败仍有answer ID可恢复，绝不把保存和付费评价合为一次不可分失败。

O07 核算。输入C加calculate{exercise_record_id,answer_record_id,reference_point_id}，不接收任意表达式/程序/工具名。服务器从已保存、已确认显示的数值依据构造一项CalculationArguments；只能有限两操作数和一种运算。本切片只核已展示参考要点的固定recipe，须先O05 reference暴露，不从任意作答文字猜算式。前提当前绑定可核算、活动显式finite_calculate授权与有限工具余额，且无在途动作。一次G5工具、模型0，原工具事务保存正文并附calculation事实；只加support_check，不自行评价或推进节点。下一O08。复合推导超过一次算子用手工可核查依据，或者另一次显式核算，不暗中多次execute。无工具额度时显示未核算，不绕工具链免费算业务结果。

O08 请求评价/根据纠错再评价。输入C加evaluate{exercise_record_id,answer_record_id,correction_record_id?,retry_of?}。前提已保存当前答案，目标/路径/题目/答案版本一致，scope有效，无同父UNKNOWN/当前pending。一次模型，工具0；装配当前参考、已保存作答、必要G5核算及有限前史。输出正确部分、实际错误、缺证据、原因假设、逐维度观察与针对下一练习建议。事务存feedback；有当前资格时再写progress、按规则保留/修补/前进节点和理由，并记录反馈会暴露的本题内容。保留/修补时phase=feedback_ready；转下一节点时清当前题/答/反馈指针、phase=ready，前一反馈由progress及历史回查。下一O06续答、O04针对练习/复测、O09纠错或O11选择合法节点。没有自动评价→出题第二调用。再评价以纠错ID区分语义槽，观察仍按同一answer去重；相反评价标争议，不能叠加分数。

O09 纠正诊断/评价/路径理由。输入C加correction{target_record_id,text,disputed_dimensions[]}，目标须为本活动可读path/feedback/progress之一，0..4维度。零费新增user_correction，保留原结论。当前图内feedback/progress的对应answer观察置contested，移出前置依据，重算图；当前节点的前置因此失效时，回最早需要修补的节点，清不同节点的当前题/答/反馈并置ready，后续题仍是历史。同节点保留合法当前题/答：有当前已保存反馈为feedback_ready，有答无反馈为answer_saved，仅有题为exercise_ready。纠错针对旧答案不把它改成当前答案；当前评价在途则obsolete。当前path/proposal的理由纠错只标建议理由有争议并保存理由，不伪造某个answer错误，下一O02/O03重订。其他旧图/旧目标纠错是history_only，不改当前head。用户声明不是已验证事实。下一合法动作依实际阶段：answer_saved/feedback_ready可O08，feedback_ready可O04 continuation/retest，ready可O04 initial重新观察，或O02；没有当前题/答时不得拿历史ID冒充当前来再评价。

O10 放弃意图。输入C加abandon{target_business_key}。不承诺撤回远端，不取消活动，不退款。尚未claim_launch的accepted命令经同一锁确认后可abandoned释放；已有claim/operation、UNKNOWN或在途只记abandoned_at并清当前显示pending，原未知父槽及账面不释放。在途结果仅历史。用户也可仅清本机台账，不影响服务端。下一只读核对；只有确定未发送/确定失败才能retry_of，不确定同父不能重发。

O11 选择路径节点。输入C加select_node{path_record_id,node_id}。零费，仅接受当前图内、前置满足节点；有当前未处理练习时先显示其未处理事实并要求显式保留历史，body增加archive_current=true才能切换。该字段只归档当前引用不删内容。当前model/tool在途不允许切节点；O10只放弃显示，仍须原有效窗口完成收尾。事务写node_selection和理由、清当前题/答/反馈及未接受候选指针、更新head，phase=ready。已完成节点可复习，不重计旧效果。下一O04。

X01 沿现有POST /api/activities/{id}/cancel取消活动。它仍按来源→活动→操作序列，G加1、关门、R保守折叠至S，不动模型/费用/工具账。教学读取据activities取消状态覆盖，不要求同步遍历head。新正文禁止，原已提交事实可历史读，草稿不丢。不能把O10当真正取消。

R01 工作区快照、R02 有界历史/记录、R03 绑定引用/用户作答回查，全部只读、0模型/0工具/0新进程。失败只显示无法核对，不猜成功或补正文。第7节定义具体路径、快照及分页。

### 3.4 失败与恢复的统一语义

COMMIT后响应丢失，客户端保留key/hash，先GET command再GET workspace。已提交以事实返回，不再评分/计数；无command且可读只能说明该查询时刻没有该键，显式同键重试仍要服务器claim/CAS。数据库不可读就是unconfirmed，不能当“无记录”。

UNKNOWN或claim_launch后失联，保持占槽及预留；只有只读核对/放弃显示/取消/使用其他明确新上下文的合法动作，禁止自动重发、重新开同父键或退款。未知长期无结果不妨碍读旧成功成果及本地保存新答案，但同父不确定评价不能重发；新增答案是新观察对象，旧不确定请求必须先结束当前有效执行窗口，新评价另外显式确认并计账。

预算不足只关模型/工具，目标/作答/纠错零费仍可保存，前提活动尚可写。到期/取消页只读，本机草稿保留并允许复制到用户显式创建的新活动，不假称旧活动仍可执行。刷新/重开只GET，同步清不了的旧running显示需既有受控恢复，HTTP不启用自动旧窗口恢复。

跨标签页全部以数据库版本/父槽裁决。另一页保存新答案后本页旧评价可存历史，下一读显示“答案已更新；此反馈对应上一版”。切活动/目标/题目/答案后迟到响应不能改当前编辑器或焦点，也不能帮用户自动开始下一动作。

## 4 B 唯一最小持久模型

采用三张G8专用表，教学head为可重建投影，commands为有限用户命令和启动收据，records为不可变教学事实/用户编辑版本。模型与工具正文继续唯一存007，records只以FK及hash引用，零费用户事实存records，不把Redis/localStorage当历史。不增加通用事件总线、多Agent服务或第三种operation kind。

三表是必要最小职责分离。只扩007仍受model/tool非空/成本/发送域限制，无法可靠表达零费修正和答案；只用head会覆盖历史；只用records而没有commands不能保存出站前意图、占UNKNOWN父槽及防重复启动。新增字段不能把客户端或模型提升为权威。

命令实体为(activity_id,business_key)，事实实体为(activity_id,record_id)，记录序号只作稳定历史排序；operation_id为teach8m.<UUID>.<request_sha256>或teach8t.<UUID>.<request_sha256>，长度109，仍在128域。业务语义槽slot_sha256不同于这些实体ID，由应用按action、goal ID、path/node、练习/答案/纠错/前驱ID组成，排除business_key及文本内容，因此能拒同父异文竞争。同内容跨键只有一个业务事实和一次效果。

### 4.1 完整DDL草案

下列SQL仅在本报告内，未创建可执行迁移。未来009须在一笔事务验证001—008表、必需列/约束域与无G8残迹，任一不符RAISE后全回滚；不能依名字相同就采用篡改约束。包括旧行和旧正文身份核查，重跑009不支持，不用IF NOT EXISTS跳过冲突。非空升级只新增表/索引/FK，不回填旧学习、不改001—008、不让旧G7成为已测能力。

```sql
BEGIN;
CREATE TABLE teaching_heads (
    activity_id UUID PRIMARY KEY REFERENCES activities(id),
    revision INTEGER NOT NULL DEFAULT 0 CHECK (revision BETWEEN 0 AND 2147483647),
    goal_version INTEGER NOT NULL DEFAULT 0 CHECK (goal_version BETWEEN 0 AND 32),
    last_seq INTEGER NOT NULL DEFAULT 0 CHECK (last_seq BETWEEN 0 AND 4096),
    phase TEXT NOT NULL DEFAULT 'needs_goal' CHECK (phase IN
        ('needs_goal','needs_plan','path_review','ready','exercise_ready','answer_saved','feedback_ready')),
    goal_record_id UUID,
    path_record_id UUID,
    node_id VARCHAR(2) CHECK (node_id IS NULL OR node_id ~ '^n[1-6]$'),
    exercise_record_id UUID,
    answer_record_id UUID,
    feedback_record_id UUID,
    reason_record_id UUID,
    pending_business_key UUID,
    projection TEXT NOT NULL DEFAULT '{}' CHECK (octet_length(projection) BETWEEN 2 AND 8192),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK ((goal_version = 0 AND goal_record_id IS NULL AND phase = 'needs_goal')
        OR (goal_version > 0 AND goal_record_id IS NOT NULL AND phase <> 'needs_goal')),
    CHECK ((path_record_id IS NULL AND node_id IS NULL) OR
        (path_record_id IS NOT NULL AND node_id IS NOT NULL)),
    CHECK (answer_record_id IS NULL OR exercise_record_id IS NOT NULL),
    CHECK (feedback_record_id IS NULL OR answer_record_id IS NOT NULL)
);

CREATE TABLE teaching_commands (
    activity_id UUID NOT NULL REFERENCES activities(id),
    business_key UUID NOT NULL,
    action TEXT NOT NULL CHECK (action IN
        ('goal','plan','accept_path','exercise','expose','answer','calculate','evaluate',
         'correct','abandon','select_node')),
    request_sha256 CHAR(64) NOT NULL CHECK (request_sha256 ~ '^[0-9a-f]{64}$'),
    request_body TEXT NOT NULL CHECK (octet_length(request_body) BETWEEN 2 AND 32768),
    slot_sha256 CHAR(64) NOT NULL CHECK (slot_sha256 ~ '^[0-9a-f]{64}$'),
    expected_revision INTEGER NOT NULL CHECK (expected_revision BETWEEN 0 AND 2147483647),
    goal_version INTEGER NOT NULL CHECK (goal_version BETWEEN 0 AND 32),
    scope_revision INTEGER NOT NULL CHECK (scope_revision > 0),
    parent_record_id UUID,
    context_body TEXT CHECK (context_body IS NULL OR octet_length(context_body) BETWEEN 2 AND 49152),
    context_sha256 CHAR(64) CHECK (context_sha256 IS NULL OR context_sha256 ~ '^[0-9a-f]{64}$'),
    operation_id VARCHAR(128) CHECK (operation_id IS NULL OR
        (char_length(operation_id) BETWEEN 1 AND 128 AND operation_id !~ '[^A-Za-z0-9._:/-]')),
    retry_of UUID,
    status TEXT NOT NULL CHECK (status IN
        ('accepted','started','committed','history','not_sent','failed','unknown','abandoned')),
    launch_claimed_at TIMESTAMPTZ,
    obsolete_at TIMESTAMPTZ,
    abandoned_at TIMESTAMPTZ,
    result_record_id UUID,
    error_code VARCHAR(64) CHECK (error_code IS NULL OR error_code ~ '^[A-Za-z0-9._:/-]{1,64}$'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (activity_id,business_key),
    UNIQUE (activity_id,operation_id),
    FOREIGN KEY (activity_id,retry_of) REFERENCES teaching_commands(activity_id,business_key),
    CHECK ((context_body IS NULL) = (context_sha256 IS NULL)),
    CHECK ((action IN ('plan','exercise','evaluate','calculate') AND operation_id IS NOT NULL)
        OR (action NOT IN ('plan','exercise','evaluate','calculate') AND operation_id IS NULL)),
    CHECK (launch_claimed_at IS NULL OR action IN ('plan','exercise','evaluate','calculate')),
    CHECK (status <> 'started' OR launch_claimed_at IS NOT NULL)
);

CREATE UNIQUE INDEX teaching_command_live_slot ON teaching_commands(activity_id,action,slot_sha256)
    WHERE status IN ('accepted','started','unknown','committed','history');
CREATE INDEX teaching_commands_recent ON teaching_commands(activity_id,created_at,business_key);

CREATE TABLE teaching_records (
    activity_id UUID NOT NULL REFERENCES activities(id),
    record_id UUID NOT NULL,
    seq INTEGER NOT NULL CHECK (seq BETWEEN 1 AND 4096),
    kind TEXT NOT NULL CHECK (kind IN
        ('goal','path_proposal','path_accept','exercise','exposure','answer','calculation',
         'feedback','progress','correction','node_selection')),
    business_key UUID NOT NULL,
    ordinal SMALLINT NOT NULL CHECK (ordinal BETWEEN 1 AND 4),
    goal_version INTEGER NOT NULL CHECK (goal_version BETWEEN 1 AND 32),
    scope_revision INTEGER NOT NULL CHECK (scope_revision > 0),
    goal_record_id UUID,
    parent_record_id UUID,
    exercise_record_id UUID,
    answer_record_id UUID,
    supersedes_record_id UUID,
    operation_id VARCHAR(128),
    body TEXT CHECK (body IS NULL OR octet_length(body) BETWEEN 2 AND 32768),
    body_sha256 CHAR(64) NOT NULL CHECK (body_sha256 ~ '^[0-9a-f]{64}$'),
    source_refs TEXT NOT NULL CHECK (octet_length(source_refs) BETWEEN 2 AND 8192),
    applied_revision INTEGER CHECK (applied_revision BETWEEN 1 AND 2147483647),
    state_after TEXT CHECK (state_after IS NULL OR octet_length(state_after) BETWEEN 2 AND 8192),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (activity_id,record_id),
    UNIQUE (activity_id,seq),
    UNIQUE (activity_id,business_key,ordinal),
    FOREIGN KEY (activity_id,business_key) REFERENCES teaching_commands(activity_id,business_key),
    FOREIGN KEY (activity_id,operation_id) REFERENCES activity_operation_results(activity_id,operation_id),
    FOREIGN KEY (activity_id,goal_record_id) REFERENCES teaching_records(activity_id,record_id),
    FOREIGN KEY (activity_id,parent_record_id) REFERENCES teaching_records(activity_id,record_id),
    FOREIGN KEY (activity_id,exercise_record_id) REFERENCES teaching_records(activity_id,record_id),
    FOREIGN KEY (activity_id,answer_record_id) REFERENCES teaching_records(activity_id,record_id),
    FOREIGN KEY (activity_id,supersedes_record_id) REFERENCES teaching_records(activity_id,record_id),
    CHECK ((kind IN ('path_proposal','exercise','calculation','feedback')
            AND operation_id IS NOT NULL AND body IS NULL)
        OR (kind NOT IN ('path_proposal','exercise','calculation','feedback')
            AND operation_id IS NULL AND body IS NOT NULL)),
    CHECK ((applied_revision IS NULL) = (state_after IS NULL)),
    CHECK ((kind = 'goal' AND goal_record_id IS NULL) OR
        (kind <> 'goal' AND goal_record_id IS NOT NULL)),
    CHECK (kind NOT IN ('feedback','calculation','progress') OR answer_record_id IS NOT NULL),
    CHECK (kind NOT IN ('answer','exposure','feedback','calculation','progress') OR exercise_record_id IS NOT NULL),
    CHECK (kind <> 'progress' OR parent_record_id IS NOT NULL)
);

CREATE UNIQUE INDEX teaching_goal_version ON teaching_records(activity_id,goal_version) WHERE kind='goal';
CREATE UNIQUE INDEX teaching_operation_fact ON teaching_records(activity_id,operation_id) WHERE operation_id IS NOT NULL;
CREATE UNIQUE INDEX teaching_effect_revision ON teaching_records(activity_id,applied_revision) WHERE applied_revision IS NOT NULL;
CREATE UNIQUE INDEX teaching_feedback_effect ON teaching_records(activity_id,parent_record_id) WHERE kind='progress';
CREATE UNIQUE INDEX teaching_answer_successor ON teaching_records(activity_id,supersedes_record_id)
    WHERE kind='answer' AND supersedes_record_id IS NOT NULL;
CREATE UNIQUE INDEX teaching_initial_answer ON teaching_records(activity_id,exercise_record_id)
    WHERE kind='answer' AND supersedes_record_id IS NULL;
CREATE INDEX teaching_history ON teaching_records(activity_id,seq DESC);
CREATE INDEX teaching_answer_observations ON teaching_records(activity_id,answer_record_id,seq)
    WHERE kind IN ('feedback','progress','correction');

ALTER TABLE teaching_heads
    ADD FOREIGN KEY (activity_id,goal_record_id) REFERENCES teaching_records(activity_id,record_id),
    ADD FOREIGN KEY (activity_id,path_record_id) REFERENCES teaching_records(activity_id,record_id),
    ADD FOREIGN KEY (activity_id,exercise_record_id) REFERENCES teaching_records(activity_id,record_id),
    ADD FOREIGN KEY (activity_id,answer_record_id) REFERENCES teaching_records(activity_id,record_id),
    ADD FOREIGN KEY (activity_id,feedback_record_id) REFERENCES teaching_records(activity_id,record_id),
    ADD FOREIGN KEY (activity_id,reason_record_id) REFERENCES teaching_records(activity_id,record_id),
    ADD FOREIGN KEY (activity_id,pending_business_key) REFERENCES teaching_commands(activity_id,business_key);
ALTER TABLE teaching_commands
    ADD FOREIGN KEY (activity_id,parent_record_id) REFERENCES teaching_records(activity_id,record_id),
    ADD FOREIGN KEY (activity_id,result_record_id) REFERENCES teaching_records(activity_id,record_id);

CREATE FUNCTION teaching_records_immutable() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION '教学历史不可覆盖或直接删除';
END;
$$;
CREATE TRIGGER teaching_records_immutable BEFORE UPDATE OR DELETE ON teaching_records
    FOR EACH ROW EXECUTE FUNCTION teaching_records_immutable();
CREATE FUNCTION teaching_command_identity_guard() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF ROW(NEW.activity_id,NEW.business_key,NEW.action,NEW.request_sha256,NEW.request_body,
           NEW.slot_sha256,NEW.expected_revision,NEW.goal_version,NEW.scope_revision,
           NEW.parent_record_id,NEW.context_body,NEW.context_sha256,NEW.operation_id,
           NEW.retry_of,NEW.created_at)
       IS DISTINCT FROM
       ROW(OLD.activity_id,OLD.business_key,OLD.action,OLD.request_sha256,OLD.request_body,
           OLD.slot_sha256,OLD.expected_revision,OLD.goal_version,OLD.scope_revision,
           OLD.parent_record_id,OLD.context_body,OLD.context_sha256,OLD.operation_id,
           OLD.retry_of,OLD.created_at) THEN
        RAISE EXCEPTION '教学命令身份不可改写';
    END IF;
    IF OLD.launch_claimed_at IS NOT NULL AND
       NEW.launch_claimed_at IS DISTINCT FROM OLD.launch_claimed_at THEN
        RAISE EXCEPTION '教学启动资格不可重置';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER teaching_command_identity_guard BEFORE UPDATE ON teaching_commands
    FOR EACH ROW EXECUTE FUNCTION teaching_command_identity_guard();
REVOKE ALL ON teaching_heads,teaching_commands,teaching_records FROM PUBLIC;
COMMIT;
```

上述完整字段草案的跨行类型校验由锁内仓储承担，不谎称CHECK可验证其他行。FK保证同活动，仓储还核parent kind、goal/version、同题答案、supersedes前驱及scope身份。canonical TEXT只接受精确DTO、有限JSON、拒重复键/NUL/非有限值；body_sha256在应用重算，不假设有pgcrypto。state_after是应用生成的有界投影快照，applied_revision是唯一效果版本，不接受模型/客户端直接写。每次生效head.revision加1的事务恰有一条state_after，评价时由progress承担；其他同事务feedback/exposure等事实applied_revision=NULL。不生效历史记录也无state_after。

head首次由O01事务惰性创建，R01不存在head时只派生needs_goal，不写空壳。commands.goal_version/scope_revision记录原请求CAS前提；O01的goal事实版本是expected_goal_version加1，不能为此修改command身份。历史exposure/answer/correction事实绑定原题或目标记录的goal/scope，当前C的CAS仍须核当前活动，不把两种版本口径混合。模型/工具命令只绑定已成立的当前goal版本。goal_record_id在goal记录中NULL，其他类型绑定具体goal；path_proposal/exercise/feedback/calculation的正文仍在007，record.body=NULL且hash必须等于007规范封套hash。其余本地body的hash为排序键canonical UTF-8，不与G3不排序键的封套hash算法混用。

request_body/context_body、操作ID、slot、父引用、retry_of及创建时间一经接受不可修改；status/启动收据/obsolete/abandoned/结果/错误仅按状态机更新。草案中的identity触发器及最小列级写权限共同覆盖，launch_claimed_at非空后不可重置；不能只靠一般UPDATE接口承诺。records触发器明确禁止本轮任何无痕修正/删除；完整STEP013/017以后提供获准删除事务与依赖失效，届时须显式修改此删除边界，不宣称当前删除已实现。

不新增角色或放宽旧表权限。未来合成库沿已授权迁移/应用角色，只给新表所需SELECT/INSERT及head/commands指定列UPDATE、所需函数执行；records无UPDATE/DELETE，PUBLIC无访问。实际授权角色必须由未来卡的合成夹具清单给出并核权，不能猜用户库角色。升级前检查角色能锁/读旧权威域但不能自行DDL；不足则只停该资源许可，不现在读私有DSN。候选SQL的前置校验与权限语句须在未来实施卡中落实到固定合成对象。

回滚分两类。COMMIT前任何校验/DDL/FK/授权失败整笔回滚，旧行/hash不变。COMMIT后无G8记录时可在显式合成许可下逆序撤新FK/触发器/表/函数，旧001—008保留；已有教学事实不得DROP冒充无损回退。此时关闭teaching模型/工具入口、保留只读及记录，采用向前修正或已批准副本恢复。产品旧版本若不认识新教学操作，不能继续对新教学活动发送普通调用；需入口关闭/固定版本部署门。不能用恢复旧软件抹账。

### 4.2 事实、用户版本与可重建投影

不可变事实包括每个模型/工具规范正文、题目/参考依据、exposure、具体answer文字和暴露快照、feedback各版、retest父关系、progress的更新/保留理由与来源。goal和correction的“可编辑”是新增版本，绝不UPDATE原行。commands保存用户本次意图、服务端冻结上下文、一次启动收据及结局，关键输入不改。当前节点、各节点状态、当前有效观察、争议标记与当前理由是head.projection，可由按seq排列的state_after、当前来源资格及commands重建。

state_after为schema='teaching.state.v1'的严格对象，含revision、goal_version、phase、goal/path/node/题/答/反馈/理由ID及projection；不存在的指针为null。projection含pending_proposal_record_id、0..6节点的status和各节点最多两个当前独立answer ID、contested/assisted标识。整个state_after与独立projection分别受8192字节限制。全部引用必须是本活动已存在事实，不能携正文或长期熟练度定值。seq在锁活动/head下分配，最多4096，COMMIT前整个批量记录及head.last_seq一起写；失败无半个序号事实。history_only可增加last_seq而不增加head.revision。接受在途命令只改变pending引用及command状态，不改变教学revision；这是“教学事实版本”，不是调用状态时钟。快照另携command状态摘要，不遗漏其变化。

每活动accepted命令上限1024，goal版本32，已接受路径32，题128，答案512，纠错128，总记录4096。达到任一上限拒新的对应写入，保留旧事实，不清历史换额度；同键重放不占新额度。应用在活动锁内核数量，数据库序号/唯一性作最后屏障。普通业务容量不足可显式新建活动，不假称现有活动无限可扩。

本轮仅最小“查看及有出处纠错”。新增数据可独立解读其kind、goal/scope/题/答/父/纠错链及规范JSON版本；后续导出必须带这三表和相关007正文/源版本映射，不能只导head。删除必须清楚地区分用户记录和资料引用，依赖删源则马上抑制派生正文、当前路径和缓存；不物理删除用户作答来模拟失效。完整资料删除、记忆管理、导出/备份/恢复仍归STEP013/017。

## 5 B DTO、请求profile与有限大小

### 5.1 公共命令类型

新文件backend/app/learning/teaching_contracts.py定义所有Strict DTO，extra=forbid、frozen、strict。日期由服务端生成。规范UUID须是小写标准形式；整数拒bool，版本/索引有明确域。Canonical新命令使用UTF-8、ensure_ascii=False、sort_keys=True、紧凑分隔符、allow_nan=False；仅文本CRLF/CR统一为LF，goal及简单问题去首尾空白，answer保留缩进/空行，仅拒全空、NUL、孤立代理字符。客户端计算相同规范hash，服务端重算才有效。不能把答案的语义等价作为幂等内容等价。

request_body的精确规范对象为{activity_id,action,expected_revision,expected_goal_version,expected_scope_revision,body}，request_sha256为这些UTF-8字节的SHA256；business_key独立作实体主键，不在内容摘要中。因此不同业务键能比较相同意图，同键也能判断异文/异前提。body中的retry_of、confirmed等若适用均在内容摘要内，不隐性改变。client draft保存完整公开请求，核对时按此对象重算；context_sha不是request_sha，不能混用。

统一POST请求为TeachingCommandInput，恰有business_key、expected_revision、expected_goal_version、expected_scope_revision、action、body。action和body按O01—O11的封闭判别联合。O02/04/07/08的body额外必需confirmed=true，严格布尔；它只是用户此次显式发送意图，不增加权限。retry_of仅模型/工具动作可有，指同活动、同action/父槽、已确定failed/not_sent命令。其他动作多余字段422。expected_goal_version 0只允许首次goal，其他须1..32；expected_revision 0只在不存在head且首次goal时合法。所有新接口使用同一C，无客户端provider、catalog、权限、G、额度或“pass”字段。

O01的seed只接受有效G7 model当前成果，服务器校验operation/hash/goal，seed不是父消费凭证；seed正文不作为当前观察。O04的path/node由服务器回查批准图；O05只允许固定hint/reference。O06的supersedes须最新本题答案，initial不可重复建，continuation标辅助，revision根据暴露快照重新判独立性但仍同一题只算一次独立实例。history_only作答的C仍核当前活动head/goal/scope CAS，但answer事实的goal_record_id/goal_version/scope_revision/source_refs取原exercise绑定，不能把旧题用户文字重新贴成新目标观察；这一窄保存不要求原派生正文当前可读，不回传其参考。O07 reference_point_id须属于该题固定数值rubric，工具参数由服务器从已存数值生成，不能从用户自然语言eval。O08 correction必须为该答案/节点的有效纠错链。O09 disputed_dimensions须来自目标记录，文字是用户补充，非原文证据。O11 archive_current是严格布尔且仅有未处理题时要求true。

semantic_slot对固定对象再作canonical SHA256，所有动作都包含activity/action及scope身份。goal用前一goal ID/version和expected_revision；plan用当前goal ID和有限诊断证据ID/hash集合；accept_path用proposal ID；exercise用当前path/node/purpose及父feedback或最新path_accept/node_selection/progress理由ID；expose用exercise/part；answer用exercise和supersedes或固定initial标志，不包含正文/kind；calculate用exercise/answer/point/recipe hash；evaluate用exercise/answer/correction锚及参考hash；correct用target/expected_revision；abandon用target_business_key；select_node用path/node/expected_revision。父槽不含重试key/retry_of或答案文字，未知不能通过变这些字段解锁。无新诊断重复plan、无新父理由重复出题只返回原提案/题，不凭不同UUID新增同一效果。

跨键同槽同内容比较request_body全字节相等（含原CAS前提），才返回duplicate_of。已有exposure后直接GET已暴露参考，不用新版本请求重复expose；单纯多点一次可以重放原意图。合法新修正版/新的诊断锚/新实例上下文是新父槽，不能把陈旧CAS改成最新值伪装同一次意图。

通用响应TeachingCommandReceipt恰含activity_id、business_key、action、request_sha256、status、duplicate_of、record_ids、operation_id、payload_sha256、applied_revision、head_revision_now、qualification、error_code、model_called、tool_called、retry_policy、exposed_part。status为accepted/started/committed/history/not_sent/failed/unknown/abandoned，qualification为current/history_only/source_invalid/cancelled/integrity_error/unconfirmed。duplicate_of/operation_id/payload_sha256/applied_revision/error_code/exposed_part无对应事实时为null；called字段已知时布尔，否则null，无依据不能把unknown说成未调用。record_ids最多4项，每项{record_id,kind,seq}，其本身不夹参考答案。exposed_part只在O05对应exposure COMMIT已确认且来源可读时非空，是{part:'hint',text}或{part:'reference',reference_points,reference_explanation}的封闭联合，沿题目相同大小/字段上限；其他动作固定null。retry_policy为none|same_key_before_claim|explicit_new_key_after_confirmed_failure|read_only。正常提交200，尚在有界处理中202；资格不明时不返回参考。

错误为现有{detail:{code,message}}格式。400 invalid_input/clarification_required，403会话或跨源，404 not_found/record_not_found/citation_not_found，409 command_key_conflict/stage_conflict/version_conflict/goal_changed/answer_changed/source_invalid/activity_cancelled/activity_expired/unknown_slot/launch_already_claimed/budget_exhausted/tool_limit_unconfigured/tool_limit_exhausted/profile_required，413 input_too_large/context_limit/result_limit/history_limit，422字段/类型非法，503 database_unavailable/teaching_not_configured/teaching_config_invalid/teaching_config_incompatible。未知提交不是明确拒绝，返回unknown/unconfirmed而非可安全重试码。错误不泄露DSN/秘密/全文输入。

### 5.2 受信内部profile和低信任模型输出

TeachingProfile恰含profile='teaching.v1'、action=plan|exercise|evaluate、command_key、request_sha256、context_sha256、activity_id、expected_revision、goal_record_id、goal_version、path_record_id?、node_id?、exercise_record_id?、answer_record_id?、correction_record_id?、scope_revision、sources、catalog、messages_sha256、max_output_tokens。sources沿SourceIdentity，目录由应用生成、至多4项。profile不重复放完整作答和前史，避免profile/messages双份答案冲破one_call上限。context_sha256在freeze时对“各引用正文hash、目标/题/答案/纠错版本、目录、固定提示版本、max_output_tokens、规范messages”重算；messages_sha256是精确发给provider的规范消息数组hash。

教学目录的citation_id沿lc_加SHA256(request_sha256与evidence_id连接)前24位，先由已确定的request_sha生成目录，再计算含目录的context_sha；不以context_sha生成其自身包含的目录，避免循环指纹。所有目录正文及来源仍应用从范围装配，模型不能提供受信catalog。

消息hash按实际provider payload中的messages，即Message.model_dump(mode='json',exclude_none=True)投影的数组计算，包含规范类型默认值，不把prompt函数的简写dict与实际序列化消息混比。messages_for_teaching不把request/context/messages摘要本身拼入消息，固定提示版本和低信任内容先生成消息，再计算摘要及profile，避免另一个自引用。

ModelCallRequest增加可空teaching_profile，与learning_profile互斥，teaching必须JSON_OBJECT、allowed_tools为空。AdmissionIntent仅增加可空TeachingCallBinding{command_key,request_sha256,context_sha256,expected_revision,goal_version}，由gateway受信profile构造，不能从公开API直接构造。普通请求该字段None，旧字节/协议不变。新profile经OneCallInput.from_wire和worker/gateway再验证，不允许model_construct/copy绕过。teach8m.无profile、profile与operation不符、未知profile/action或混合learning均零发送拒绝。

StoredTeachingDocument由应用构造，含profile/action/command/request/context、实际goal/scope/相关实体、有限catalog、固定limitations及result；不公开父消费token、DSN、G执行凭证或内部全history。模型只输出result对象。目录身份、目标版本、权限、当前状态、进度均取锁内命令和实际活动。record hook对封套复核profile/context与commands冻结值，并据命令action唯一映射record.kind，不让模型选写入表或事实版本。

低信任输出是封闭联合，下列字段为完整模型契约。

- PathOutput为{result_type:'path',message,nodes}。nodes为1..6项，每项{title,objective,prerequisites,rationale,citations,completion_dimensions}；前置是0..5节点索引集合且须在当前节点之前，title至80字符、objective160、rationale240，citations1..4，completion_dimensions1..4个{dimension,required_point}，dimension64、required_point160。服务器分配节点ID并做DAG/目标相关性和证据集合验证，模型不回passed。
- ExerciseOutput为{result_type:'exercise',message,exercise_type,difficulty,stem,reference_points,reference_explanation,dimensions,hint,variant}。stem至1024字符；reference_points为1..4个{point_id,text,citations,numeric?}，point_id仅p1..p4并在服务器规范化，text240，numeric可空或{value_decimal,unit,operation,left,right}；数值字符串规范有限域，operation只能G5枚举，left/right为原有限数值；reference_explanation512，dimensions1..4个{id,point_ids,description}，description160；hint可空至240。variant恰有{purpose,parent_exercise_record_id,parent_feedback_record_id,instance_data}，purpose及父ID由应用的当前命令决定，不相信模型回报来改变绑定；输出中的对应字段必须与请求一致。instance_data为该题型封闭小对象，数值至8个命名量，概念至2个给定情境，程序为固定语言标签Python及给定代码/输入/手工预期；不含脚本入口或执行指令。模型生成的数值/程序参考是待检验建议，机械可核查的部分单独核，不能自签质量。
- FeedbackOutput为{result_type:'feedback',message,correct_parts,errors,evidence_gaps,cause_hypotheses,dimension_observations,next_focus}。四类条目各0..4；前三类每项{answer_excerpt,explanation,point_ids,citations}，excerpt至200、explanation240，必须回查实际作答位置，point_ids至4、citations至4。hypothesis每项{hypothesis,evidence_for,missing_evidence,confidence}，文字各240，confidence只tentative/unknown。dimension_observations为1..4个{id,observation:met|partial|not_met|unknown,reason,point_ids}，reason240。next_focus为{focus_dimension,reason,suggested_mode:continuation|retest|review}，不含直接状态写入；按当前合法动作映射。实际错误没有证据则转gap/unknown，不能把假设写成确定缺陷。
- ClarificationOutput为{result_type:'clarification',message,questions}，questions1..2，每项至160；NoEvidenceOutput为{result_type:'no_evidence',message,missing}，missing1..4至160；ConflictOutput为{result_type:'conflict',message,claims}，claims2..4项{text,citations}，至少两个不同资料身份或明确新旧feedback ID。通用message至256。三者不带正常产物字段，不触发通过或自动下一调用。

支持性检查SupportChecks是应用输出，分离于模型评价。可给numeric_value/unit/order_of_magnitude的确定运算对照，negation/equivalence/logical_relation只能报告在给定资料和rubric下的可核查符合/冲突/未检验，不能用关键词命中宣布开放题正确。开放题保留作答原文、逐维度理由和证据；只有精确的结构/数学确定矛盾可以收紧模型判断，其余不确定就unknown并需要后续实例。答中若单位/数值与受检参考冲突，则相关dimension至少not_met/unknown，即使模型误判met也不进入独立计数。自然语言否定/等价不是一般字符串裁判。

每条参考、作答/反馈引用要区分source、answer、feedback、calculation和user_correction。来源沿G7 position/hash；answer引用为{record_id,start_offset,end_offset,text_sha256}，按保存文本Unicode码点定位且UTF-8 hash重算；feedback/correction引用为具体记录和字段，不冒充原资料。计算引用由真实G5操作/arguments_sha/payload_sha组成，手工参考标manual_reference，不能伪造一次工具调用。

instance_data的封闭签名为calculation:{quantities:[{name,value_decimal,unit}]}，1..8项，name32、unit16；concept:{scenarios:[{label,text}]}，1..2项，label80、text512；program:{language:'Python',code,inputs:[{name,value_json}],manual_expected}，inputs0..4，name32、value_json每项1024字节、manual_expected512字符，code至32行/2048字符/6144字节。均拒额外字段、重复量名和无限嵌套。decimal采用有限规范十进制字符串，不接受NaN/Inf/科学计数注入；value绝对值≤1e18、left/right沿G5≤1e12。需要近似时numeric增加tolerance_decimal至12位小数、非负≤1，必须明确显示误差；未提供就精确对照。核算本身保留G5原精度50结果，不用浮点字符串评分开放答案。数值/单位结构来自已存参考及可核查资料，自动文本解析不足就未检验，不硬评分。

### 5.3 上限与配置依据

不抬one_call/SUP/007通道上限。G7输入/learning.v1的1..256原样。新增teaching层独立配置max_output_tokens为1..2048，推荐合成实施样本显式用2048；不能自动升级旧活动的max_output_tokens，低于所需显式配置时先拒绝。这个独立上限属于本次批准包，而非以G7配置变更免费拿预算。

依据是本合同代表性输出同时包含路径理由/前置/多个维度，或题干/参考/维度，或四类反馈及复测理由；G7只有message/segments/questions，256不适合作为新完整教学结构固定顶限。第9节给最小完整内容和实际文档字节记录。未运行tokenizer或provider，因此2048是有界建议，不宣称所有中文场景必在此额度内。未来代表性provider一次验证若在合法字节内仍截断，先缩短非必需文本/节点数量；需提高2048或扩大场景再裁定，绝不自动续写/拼接两调用。

规范输出大小材料为D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-099/model-output-examples.json，含三节点路径、一完整计算题、一四类概念反馈；字节摘要记录在document-check.md。占位lc_仅保留真实ID的固定宽度，未声称当前源存在；未来夹具绑定实际目录再验证。该测量仅文档JSON/UTF-8长度，不是调用项目序列化/测试，也不是token或模型质量测量。

新输入上限如下，字符按Unicode码点，另核UTF-8字节，任一超限拒绝。

- goal 1024字符/4096字节，self_report 512/2048，domain 80/320；answer 4096/12288，correction 1024/4096；一请求HTTP正文32768字节，教学路由在JSON解析前计流量，不能只看Content-Length或Pydantic字段上限。
- sources 1..10、原件合计5MiB、PDF50页、文本单元100、候选片段512、query词项24沿G7。新teaching目录最多4片段，总4000字符/8000字节；引用不得跨版本，单片段仍沿CatalogEntry2048字符。保留完整高优先片段，超总额先去非必需历史及尾部片段，关键依据放不下即context_limit，不截断答案或必需参考。
- 模型messages最多3项，全部纯固定system/user或受信只读历史内容，不含工具计划。传入模型的最近观察至多2条/合计2048字节；reference及当前题/已存答案按必需项装配。messages编码目标≤49152字节，profile/messages重复目录的实际ModelCallRequest编码必须≤65536，含service的call≤131072，provider请求≤min(activity.max_request_bytes,service.max_request_bytes,65536)。每个边界实际序列化检查，不能用字符和推测替代。
- 原始result≤16384字节，模型与本地规范教学正文≤32768字节；加目录/身份/limitations后的G3封套仍≤131072、深度12/节点2000。下游投影state_after/projection≤8192。超限received失败、无正文/无progress，已存答案保留。合法外层JSON转义的传输大小与解码正文上限分别核，不沿旧夹具误拒。
- 一动作plan/exercise/evaluate最多模型1、工具0；calculate最多工具1、模型0；其余0/0。SDK重试0、内部自动重试0、模型工具计划0。新生成题数1、路径节点6、单题维度4、历史摘要页默认20/最大50。费用/请求/工具/时间四账照现有admit/工具准入/claim/结算，未知不退预留。

ActivityConfig增加teaching_layer、teaching_output_tokens、teaching_calculation_layer，不改L0/L1/L2意义。新增配置段固定{profile:'teaching.v1',max_output_tokens,enable_calculation:false|true}，缺段默认关闭。enabled计算还需activity_defaults显式allowed_tools=['finite_calculate']及max_tool_calls在0..32，且新活动才复制配置；旧None/0仍拒工具。_ActivityDefaults的薄扩展只在明确合法teaching配置下容许此有限白名单，普通模型及所有teaching模型请求依然allowed_tools为空。不开任意工具或新增权限来源。capabilities增教学与核算availability、确切限制、原因及已配置输出值，不展示密钥。

SessionConfig、W/R/S/G、请求10秒HTTP限制、关门、单主机恢复声明保持既有设置。输出2048不延长超时，不保证响应必完成。用户仍可在模型失败后保留答案、读参考/手工理由；真实教学质量与真实provider授权是单独门槛。

## 6 B 原子边界、并发与恢复协议

### 6.1 固定锁序与四个边界

教学写入统一来源UUID排序→activities行→相关activity_operations键排序→teaching_heads→teaching_commands键排序→新records及head写入。前置来源hint必须在锁活动后_verify_scope_hint。同一活动行串行化其领域写入，禁止先锁head/command再反向锁活动/来源。只读定位不加锁，可在活动锁内重新读取；跨活动引用直接拒绝。原普通路径没有G8前缀就不查新表，不改变老锁序/分支顺序。

T-local是O01/03/05/06/09/11及未启动O10的短事务。TeachingService只做纯校验/有限文件读取；PostgresAdmissionLedger.apply_teaching_local(command)用_transaction一次完成同键重放或CAS/父槽、来源资格/权限、command收据、全部record、head及obsolete更新。没有模型、claim、费用或R预扣。失效来源允许用户文字目标/答案的窄保存规则，其他派生读/推进仍拒绝；活动取消/到期拒新写。权限来源为local_session和该活动事实，不是用户给定scope授权。

T-intent是付费/工具动作接受事务。accept_teaching_command(command,frozen_context)核全部当前前提，保存context/hash和accepted命令，head.pending指该键；不预扣模型/工具，教学revision不变。只允许一个当前pending，语义父槽在数据库唯一索引封闭，同父不同键先在锁内查胜者。context必须在锁前组包，再在锁内核其全部源/goal/题/答/反馈正文hash和head版本；不同即拒，不能用旧组包冻结新版本。

T-launch是claim_teaching_launch(activity_id,key,request_sha256)事务。条件accepted且launch_claimed_at=NULL、仍当前绑定/可调用、没有已存在operation；CAS置started及唯一launch时间。COMMIT已确认后才进入既有监督线程。多个重试线程只有一个能获这张启动收据；重复同key存在claim时只读，不再创建第二SUP。崩溃发生在claim后且未观察到operation也不能推定未启动，视unknown并只核对。claim前崩溃可由用户显式同键重试争取唯一claim，不自动续发。

T-admit/T-mark仍是现有G3/G5真实准入和发送/执行分界。在实际lease之后，gateway adapter再核受信profile；admit和mark的锁内再核教学command绑定/当前head/revision、obsolete/abandoned、parent事实及pending。在_model admit中TeachingCallBinding须匹配冻结context；在工具分支teach8t.以实际operation_id定位唯一command，再对原canonical arguments_sha/name/call_id核固定recipe，不新增工具协议字段。纯前查/adapter不能替代这两个数据库屏障。

T-result扩展现有record_outcome/record_tool_outcome的同一个_transaction回调，在原_terminal_confirmation与原资格/关门纪律之后，调用_write_teaching_outcome(connection,activity,call,command,outcome,payload_triple)。正文/received、对应model/tool fact、exposure及至多一个progress、head、command结局同一COMMIT。不能在LearningService收到SUCCEEDED后另开事务推进教学阶段。_write_outcome只负责旧操作/正文，不重新开事务；教学helper使用同一connection，无内部_transaction调用。

### 6.2 结果提交的准确分支

1. 先保留原_terminal_confirmation。严格相等已终态只返回ALREADY_PRESENT，检查既有教学record/command收据是否绑定完整；若G8链损坏报integrity_error，不“补记录”修旧终态。其优先级不能被新的current检查挤后。
2. 原G/scope/源/租约/活动状态或正文关门不合法，仍按原合同拒正文；只有UNKNOWN脱敏诊断可记录。不能为了展示迟到答案放松这道门。取消/换源后返回的未提交正文不会新存为教学历史。
3. 原活动资格合法，teaching goal/head/答案/纠错版本已变化或用户放弃，则received及规范正文、一个不可变历史fact和command.history可原子保存，applied_revision=NULL，不写progress或改当前pending。若是可供历史查看的feedback，须同事务另写绑定原题的exposure：反馈从COMMIT起可被读取，保守记录参考已可见，不能只因迟到就漏记暴露。该exposure同样history_only，不改当前head、不追改更早保存答案的曝光快照；之后同题新答案须纳入它。这个分支不放宽原G3成功资格，仅限制教学效果。API资格为history_only，协议3/4仍只确认正文hash，SUCCEEDED不等于当前教学节点已推进。
4. 两层资格都合法且result_type为该action的正常产物时，path/exercise结果保存当前fact及state_after；feedback保存feedback、progress、反馈暴露exposure，唯一progress.parent=feedback ID，head仅一次revision增加，reason引用progress。calculation保存计算fact及支持依据投影，一次revision增加但不推进节点。合法clarification/no_evidence/conflict仍按command action存path_proposal/exercise/feedback事实，reason指此有限结果；不激活路径、不替换原题/答案、不产生progress/观察，阶段保留原可用阶段，无原路径的plan仍needs_plan。只有reason生效的该fact携一次state_after；evaluate的中性结果因已可读也保守附exposure，不能用它给met。command可committed但业务提示“未形成可用路径/题/评价”，下一按原阶段补充O01/O06/O09或只读，不把有效中性结果冒充确定failed来盲目retry_of。record、head、007或command任一写失败整笔回滚，不可出现“正文成功、教学推进失败”但仍回成功。
5. received的远端HTTP/输出无效/截断等无正文失败，将原操作诊断和command.failed及清本键pending同事务保存，不产生练习/反馈/progress；NOT_SENT保持原模型诊断与command.not_sent；UNKNOWN保留原預留及父槽。工具不支持NOT_SENT，不造该状态。

实际方案不改LedgerOutcome正文三字段或协议回执字段。教学context从规范StoredTeachingDocument及锁内command复核；无正文失败通过teach8m./teach8t.操作定位command。传回模型的context不是权限，admit从受信绑定及DB对照。新表缺失或未知教学类型失败关闭，普通G7不要求009存在。

### 6.3 每类竞争与幂等保证

- 同key同内容。锁活动后先核request_body与request_sha严格相等，回原record/hash及当前资格。已过期/取消可以读原收据，不能再获得发送资格。零费重复无新record，模型重复无第二launch/admit；独立计数不变。
- 同key异内容。409，保留原意图/答案及输入，不能把旧成功当本次成功。正文hash不同也不覆盖。文本语义等价但字节不同属于新答案版本，需要新key及合法supersedes。
- 同父不同key。固定slot唯一索引与活动锁；同规范内容返回duplicate_of，异文stage_conflict。O06另有initial_answer和answer_successor唯一性阻止首答重复/修正版分叉。反馈效果有feedback_effect唯一索引，同answer多评价的计数由投影按answer ID去重而非把progress次数当分数。
- 迟到反馈/旧目标、题、答。admit/mark在锁内检查expected_revision及每个实体；已经出站则T-result取当前head比较，旧版只history，或原活动资格失效而仅UNKNOWN。来源替换用已有代次锁及scope hint，不修改引用到新版本。旧result为committed_current是G3来源资格术语，新教学API还须报告teaching资格，不能直接当当前路径父。
- 修正目标/零费保存答在模型在途。只增加教学revision并obsolete相关command，清当前pending；G/lease/R/S不改，不杀别的进程。SUP仍有限执行并按老监督收尾，新付费动作须等原有效窗口收尾，否则lease冲突。应用不撤远端请求、不归零失败或预算。
- 响应丢失。T-local/T-result COMMIT后任何HTTP/IPC丢失按command/record/007持久事实核；回执unconfirmed可以已提交，因此只GET。没有用缺回执否认正文，也没有用首个200补未提交事实。
- 取消/关门后返回。X01沿原G加1和关门，正文新写拒，原UNKNOWN及R保守折叠规则不变。取消前提交成功的原事实仍可history读取；取消后相同终态严格重放无效应，不重新推进。
- command accepted但没有operation。唯一launch CAS尚未claimed时允许显式同key获取一次；claimed后绝不靠“无操作行”重启。finish_teaching_supervision只能将已知确定未准入且监督已收尾的命令记failed并清pending，不能把观察失败记未启动。其COMMIT失败保守unconfirmed，GET只计算事实资格、不自动写恢复。

finish_teaching_supervision(activity_id,key,supervision)是有限监督完成后的收据整理事务，仅为尚无outcome的启动失败/租约冲突/unknown分类及pending显示，不写正文/progress、不退款。有已终态结果先读原收据，不覆盖。恢复/预算fold继续由原ActivityService/监督权威负责，不通过新读接口暗中调用recover_unknown或claim_lease。

仓储新函数的建议完整签名如下，类型均来自teaching_contracts，返回值不携权限凭证到浏览器。新增helper只能用传入connection，不能嵌套事务。

```python
async def apply_teaching_local(self, activity_id: str, command: TeachingCommandInput) -> TeachingCommandReceipt: ...
async def accept_teaching_command(self, activity_id: str, command: TeachingCommandInput,
                                  frozen: TeachingFrozenContext) -> TeachingCommandReceipt: ...
async def claim_teaching_launch(self, activity_id: str, business_key: str,
                                request_sha256: str) -> TeachingLaunchDecision: ...
async def finish_teaching_supervision(self, activity_id: str, business_key: str,
                                      supervision: TeachingSupervisionFacts) -> TeachingCommandReceipt: ...
async def read_teaching_workspace(self, activity_id: str, history_limit: int = 20) -> TeachingWorkspaceView: ...
async def read_teaching_command(self, activity_id: str, business_key: str) -> TeachingCommandReceipt | None: ...
async def read_teaching_history(self, activity_id: str, limit: int = 20,
                                cursor: TeachingHistoryCursor | None = None) -> TeachingHistoryPage: ...
async def read_teaching_record(self, activity_id: str, record_id: str) -> TeachingRecordView | None: ...
async def _locked_teaching_binding(self, connection, activity, operation_id: str,
                                   binding: TeachingCallBinding | None, phase: str) -> TeachingLockedBinding: ...
async def _write_teaching_outcome(self, connection, activity, call, command,
                                 outcome: LedgerOutcome, payload_triple) -> None: ...
```

TeachingFrozenContext是以kind判别的严格联合，共有schema='teaching.context.v1'、kind、reference_hashes、operation_id、context_sha256。kind='model'另有profile_version='teaching.v1'、prompt_version、max_output_tokens、messages、catalog；kind='tool'另有call{call_id,name,arguments_json,arguments_sha256}，没有模型消息/profile/目录。reference_hashes至12个{record_id,body_sha256}，其goal/题/答/反馈/纠错身份按命令决定，model/tool互相多出的字段拒绝。TeachingLaunchDecision为{launch_allowed,receipt}；TeachingSupervisionFacts只接原监督state/是否确定未准入/原model或tool receipt/hash、settled/reserved/pending_fold/cleanup_incomplete，不用客户端陈述恢复。phase仅admit/mark/result；其他值失败关闭。锁内helper验证身份相等、资格及父hash，返回仅内部锁定行集合，网络/ToolRegistry.execute均在事务外。

### 6.4 父消费、计算和停门兼容

TeachingService组包可对选定当前model父结果构造原ResultConsumptionRef；只消费经过teaching资格复核的当前path/exercise/feedback，父007 hash在admit原事务内核。零费answer不是007 model结果，不伪造G4 ref，依靠新增command的answer_record_id/body_sha/revision锁内绑定。需要多个教学引用时原G4只承担一个直接模型父，其他类型按新command事实hash核，不假称一个旧凭证覆盖所有域。

admit/_locked_operation的新G8分支在活动锁后从command定位所有实际model父keys，再按operation_id排序锁定，随后锁head/command；普通分支保留原行为。工具父不能作为G4 model父，计算只作为带实际tool身份的独立证据片段。普通continue_from_result、learning first/followup及公开continuations必须拒绝teach8m./teach8t.父/新键走通用继续，防绕teaching阶段；G7 first/followup本身不改正文或槽。

工具仍固定WorkerCommand('one_tool')，协议4精确输入/回执不新增字段；教学绑定只在账本按teach8t.查受信command。模型仍one_call协议3，嵌套ModelCallRequest的新可空profile由同一固定版本严格识别。旧版本收到新嵌套字段失败关闭，禁止协商降级为普通JSON调用；旧plain/G7请求去除None后字节保持。不改Command枚举/停止/回执成功含义。

## 7 B 外部接口、只读快照和实际改动清单

### 7.1 固定HTTP面

新router仍在/api/activities，均调用现有_guard。

TeachingWorkspaceView完整字段为schema='teaching.workspace.v1'、activity_id、view_token、read_at、head、overlay、goal、path、proposal、exercise、answer、feedback、reason、nodes、sources、budgets、pending、history、next_cursor、limits。head含revision/goal_version/phase及第4节所有当前实体ID，0版本只表示未建教学head；proposal可空，其ID由projection.pending_proposal_record_id和reason_record_id回查，不能用最后一条历史结果代替当前候选。其他正文区域均可空并附qualification，nodes至6、sources至10、pending至8、history至20。budgets只公开已有四账/有限上限及deadline，不公开执行凭证；overlay明确资料资格、取消/到期、当前命令处理/未知及配置禁用理由。limits固定第5.3节可审查值，不能成为客户端授权参数。

TeachingRecordView为{record_id,kind,seq,goal_version,scope_revision,parent_record_id,exercise_record_id,answer_record_id,supersedes_record_id,body_sha256,created_at,qualification,public_body}；public_body仅允许对应kind的用户可见投影，源无效则派生部分null，不带context_body/state_after/受信内部profile。TeachingHistoryPage为{activity_id,view_token,read_at,watermark_last_seq,items,next_cursor}，item为{record_id,kind,seq,goal_version,parent_record_id,created_at,label}，label最多32字符且整项≤512字节。TeachingHistoryCursor为上述固定activity/view/watermark/before，不含自由SQL/文件路径。命令回执沿第5.1节，nullable表示未确认/未形成事实，不能当默认false。

- POST /api/activities/{activity_id}/teaching/commands执行O01—O11的封闭DTO，仅上述actions，不能提供自由函数名。普通X01沿原cancel。
- GET /api/activities/{activity_id}/teaching/commands/{business_key}为同键核对，一条SELECT联命令/操作/结果/相关record/当前head/来源判资格；可返回不存在，不替代“不曾启动”证明，不自动launch或退款。
- GET /api/activities/{activity_id}/teaching/workspace为R01，一条SELECT/CTE返回一致head、当前目标/路径/题/答/反馈/理由、sources有效性、预算、当前pending/至多8条最近意图摘要和受限历史摘要20条。没有head返回needs_goal派生视图。数据库snapshot_time与view_token一起给。
- GET /api/activities/{activity_id}/teaching/history?limit=20&cursor=...为R02摘要，不取正文；GET /api/activities/{activity_id}/teaching/records/{record_id}单记录读、校验正文/hash和本活动引用。题目默认public投影；只有已记录对应exposure才允许参考投影，feedback读取也须核其同事务暴露事实，缺失即integrity_error并抑制相关正文。纯GET不能完成新的暴露。
- GET /api/activities/{activity_id}/teaching/records/{record_id}/citations/{citation_id}为R03，固定目录版本，沿read_citation位置/hash及PDF页复用，必要时适配StoredTeachingDocument，不任意读文件。GET .../answers/{answer_record_id}/references/{reference_id}只允许规范的作答offset/hash，不执行用户代码。无对应集合404，失效409，未保存/未知503或只读状态。

上述新端点是本包公开接口增量；没有新增外部互联网服务或自由工具API。旧activities/list/detail/operations、learning first/followup/intents/citations仍兼容。activities/api.py._operation_payload在teach8m./teach8t.时仅给元数据及teaching记录入口，禁止通过通用operation GET泄露尚未记录exposure的参考答案；不影响旧G7正文读取。G3内部读不抹正文，内部消费仍需实际资格。UI从新workspace恢复教学，不把两个旧GET拼成同一快照。

### 7.2 单语句快照与分页

read_teaching_workspace(activity_id,history_limit=20)用单条CTE语句联activities、scope+material_sources/PDF就绪、head、指针记录及007、有限commands/历史摘要。每项绑定/源资格/教学版本在该同一语句中判，Python再对取出的规范正文/hash/严格DTO复核；一个坏记录仅抑制对应区域并显示integrity_error，不把其他成功事实删掉，也不允许依坏进度发命令。不得循环调用read_operation拼接多版本。数据库不可用整页unconfirmed。

view_token为{head_revision,last_seq,scope_revision,source_identity_sha256,command_state_sha256}的canonical hash，来源代次与pending状态变化即不同，不只依head.updated_at。source_identity_sha含当前identity/ready有效状态，command_state_sha含返回的命令关键结局/launch/obsolete时间，不含秘密。只读时点的预算和G可以变化，不承诺响应到达后仍有效；每个POST重查。

工作区最多一goal、一path、一当前exercise、一answer、一feedback/理由及有限元数据，响应编码上限196608字节；每个教学正文上限32768确保主要指针负载可评审。超限不截掉答案/关键引用冒充完整快照，返回413 snapshot_limit并提供同一view_token的摘要及显式单记录读取入口；客户端保持上次成功页、禁依缺失区域发送下一动作。正常合同样例应在此域内。

历史默认20、最大50，每条摘要≤512字节，响应≤65536字节；seq降序稳定，cursor含activity_id、view_token、watermark_last_seq、before_seq，base64url≤1024字节。当前view_token变化返回409 snapshot_changed及新workspace入口，禁止把不同当前版本页面合并成一致当前状态。新页仍只读并复核来源；既有immutable历史可单条独立读，UI标读取时点。cursor格式非法400，跨活动404。命令核对≤65536，单记录≤65536；API no-store、纯文本呈现。

来源失效时抑制模型/工具派生正文、catalog复制文本、参考/反馈内容及当前推进资格；用户goal/answer/correction文字可显示其历史身份。当前缺证据原因给通用说明，不复制被删原文。过期或取消而来源仍有效时已提交结果只history，未显示参考的题仍需已存exposure才回参考；取消后新暴露命令拒绝。完整删除/导出后续不能绕过这层读资格。

### 7.3 拟改/新增文件与精确职责

所有以下路径均相对D:/shspic/project_NO3_RetroLume-agent，属于下一实施建议，当前未写。

1. backend/app/learning/teaching_contracts.py新增TeachingCommandInput各action body、TeachingProfile/TeachingCallBinding/StoredTeachingDocument、封闭输出类型、TeachingCommandReceipt/WorkspaceView及canonical/byte/引用校验。teaching_policy.py新增validate_transition、semantic_slot、validate_path、derive_support_checks、derive_progress、project_public_exercise、rebuild_head。纯函数不联网、不exec/eval。
2. learning/teaching_service.py新增TeachingService.submit_command(activity_id,command,config,run_tag)、reconcile、read_workspace/read_history/read_record/read_citation；先有限组包再仓储CAS，模型用run_one_call，计算调用既有ActivityService.execute_tool_action的G5链；所有零费动作调apply_teaching_local，不用模型解释保存动作。
3. learning/teaching_adapter.py新增validate_teaching_request(context,request,ledger)，复核freeze/精确消息hash/operation/profile/当前父/范围。teaching_prompt.py的messages_for_teaching(profile,frozen_context)仅固定三个专业提示，无递归、多Agent服务或后台自动复测。
4. activities/repository.py新增apply_teaching_local、accept_teaching_command、claim_teaching_launch、finish_teaching_supervision、read_teaching_workspace/command/history/record、_locked_teaching_binding、_write_teaching_outcome、_validate_teaching_fact_links。admit/mark_dispatch_started/record_outcome及G5 admit_tool_operation/mark_tool_started/record_tool_outcome只在新前缀薄扩展锁内检查/同事务提交。_terminal_confirmation/_write_outcome/_operation_is_current旧语义保持，新record hook不另开事务。_transaction复用不改隔离来掩盖多SELECT读。
5. capabilities/contracts.py新增可空teaching_profile及AdmissionIntent.teaching_binding互斥/严校验；gateway.py.call加新前缀/profile拒绝及adapter，_parse_success加教学输出解析/normalize、_finish仍只record确认。tool_execution.py不改任意执行域，工具新前缀禁止冒充模型；ToolRegistry有限算法及旧参数合同复用不改。
6. learning/evidence.py/teaching_evidence.py复用load_units/query_check和CatalogEntry/verify_fragment，新增assemble_teaching_catalog有明确4片段/8000字节域及teaching引用读适配。不改G7 assemble_catalog默认8/24000，不重写监督/PDF主体。
7. learning/teaching_api.py新增第7.1节router、教学正文stream字节守卫。main.py仅注册新router及所需路径专用大小守卫；local_session复用。activities/api.py扩capabilities并给新profile通用结果元数据投影；ActivityService.continue_from_result及旧learning入口仅加教学前缀拒绝，其他老请求照旧。
8. service_config.py新增_TeachingSection/_teaching_check、ActivityConfig新层、受控可选finite_calculate配置校验；config/activity.example.json/README.md说明新层默认关闭、推荐值不是启用付费许可。私有配置不读不写。worker/one_call.py仅随typed request接受新可空profile/新前缀身份校验，worker_main/command/one_tool协议、launcher/session/Job停止不变；需要的教学联表由固定worker内部ledger能力承担。
9. backend/migrations/009_teaching.sql在获批后实现第4节草案、完整前置/重复/旧行/失败回滚/列身份保护及角色最小权限准备；本轮没有此文件。新迁移不能依赖DocuN或公共提示词。
10. frontend/src/activities/TeachingWorkspace.tsx、TeachingExercise.tsx、TeachingFeedback.tsx、teachingApi.ts、teachingIntents.ts、teachingDrafts.ts、teachingIntentMatch.ts新增有限教学UI/IDB草稿/摘要台账，ActivityWorkspace只挂新区域及上下文切换。LearningResult/G7原呈现不重构；引用沿现有PDF薄复用。相关样式纳入已有前端CSS，不加设计框架。
11. backend/tests及frontend现有验证目录只补第11节真正新风险场景；合成受控transport/有限runner进入项目产品测试目录，不能import DocuN临时实现。旧task097/bootstrap.py及其runner禁用标识保持；采用098验证控制边界的最小新夹具须按新卡许可准备，不现在重建通用runner。

外部依赖、账号、向量服务、任意程序执行、权限来源、停止权威、G/R/S及四账模型均无新增。若未来实施发现需要这些变化，先保存已成立部分和具体差异，暂停受影响项，不自行扩卡。

## 8 C 界面、意图及恢复合同

布局和普通用户文案只存D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-099/teaching-flow.md。工作区从上至下为目标/诊断、有限路径、当前题、草稿/已保存答、分开的四类反馈、续答/复测及更新理由、历史/纠错。目标/保存答/接受路径/纠错/选择节点标“不调用模型”；plan/exercise/evaluate标“1次模型”；核算标“1次有限计算”。额度/供应商用途在显式调用前可读，普通页面不显示数据库或运行夹具细节。

按钮禁用只依当前snapshot与配置可解释事实。没有目标禁规划，没有接受路径禁出题，没有已保存答案禁评价，旧版本/失效来源/UNKNOWN同父禁重发，有效执行窗口未收尾禁新模型/工具。预算不足仍可保存用户输入。已经提交后的修正版在途可保存，明确提示旧反馈将成为历史。所有POST最后仍由服务器判资格，前端禁用不是并发授权。

teachingIntents新版本仅存16条以内摘要，每条至2048字节，总至32768，含key、action、activity、head/goal/scope、题/答/父ID、request_sha、draft_id、创建时间和状态，不含模型正文/引用正文/秘密。不迁改或清除旧retrolume.pending-intents.v1；兼容显示两种台账，不能把旧G7意图视为新G8答案。新的metadata可用独立localStorage键，完整待发body存在有限IndexedDB。

teachingDrafts用原生IndexedDB，无新依赖，最多16个草稿/总262144字节；一草稿绑定活动/goal/题/当前答案和supersedes，内容按O06限额。goal/纠错也可存在同一待发body库。容量满时让用户选择具体草稿保留/删除/复制，不自动清旧输入。服务端answer COMMIT后可以经用户确认移除对应草稿；本机草稿绝非教学历史。浏览器IDB不可用/写失败，保留编辑框且零POST，提供复制入口，不能只存hash后丢全文。

提交顺序为规范化并检查字节→IDB保存完整body及hash→localStorage保存摘要→POST一次。任一步失败不POST。核对顺序为GET command→核request_sha/实体/body身份→匹配才显示已提交/移除意图；不匹配显示冲突并保留本地输入。同key异内容不得静默更新旧body或拿别的胜者当本次输入成功。duplicate_of只在服务器和客户端都核相同规范内容时指向唯一结果。

刷新/重开只加载本机意图及GET workspace/command，绝不自动POST；跨标签页storage/IDB变化只提示/GET，不争相重试。用户可以显式同键重提accepted且未claimed动作；已claim/UNKNOWN同父只有核对/放弃显示/取消。收到明确失败可创建retry_of，但页面同时显示新一次调用和原有累计账。放弃本机意图不能释放服务端未知槽。

每个请求捕获context_key=(activity,goal_record_id,path,node,exercise,answer,head_revision)及递增sequence。活动/目标/题/答切换立即废弃旧sequence、取消GET AbortController；POST中断只停止等待，不假定服务器取消。所有迟到UI响应需mounted、sequence、当前context一致才能更新；允许按原key更新意图台账，不把旧feedback装进新答案区域。草稿切换不得覆盖另一上下文。

教学轮询使用一个workspace GET而非旧refreshDetail的两个查询拼接。至多一个在途，3秒节拍，hidden停、visible立即一次只读，unmount清timer/abort；当前command终结停止自动轮询。unconfirmed的自动观察最多120秒/40次，之后停止并给“只读核对”，不能无限等待占前端/后端执行单元。引用独立sequence/abort沿LearningResult，PDF只按受信源/物理页加载。新引用返回晚到不写当前资料页。

O02形成有效proposal时将其ID写projection.pending_proposal_record_id、reason_record_id指该proposal；O03消费候选后清此临时指针。已有当前path时提出新proposal不丢旧path引用，用户可显式O11继续原节点而保留未接受提案为历史；没有原path时只有接受/修正目标/新建议入口。head实际阶段在feedback转节点时回ready并清当前题/答/反馈，最近反馈从reason/progress链单独展示，避免把上一节点的题误作新节点当前题。

本轮不把轮询结束当监督结束。服务器每个显式动作都有原监督绝对期限，无用户等待worker。读页也不在后台auto-recover旧running。取消按钮文案为“停止本应用继续执行；已发远端请求可能继续”，观察unknown/收尾不完整如实显示。

## 9 C 三组完整可人工复核教学样例

S1—S3均是本报告给定的合成资料、手工推导和期望，未调用模型、未执行程序。下列L行是合成文本的位置定义，未来实施夹具冻结其原件字节/hash后由真实terms.v1目录分配lc_身份；本报告别名不是伪造已经存在的活动/资料ID。所有“预期反馈”是独立验收oracle，不用模型自评分当正确性标准。

### S1 可核算题、单位与数量级

资料M1为UTF-8文本，逐行给定。

```text
L1 平均速度等于路程除以所用时间。
L2 一分钟等于六十秒。
L3 使用米与秒计算时，速度单位为米每秒。
L4 换算先统一时间单位，再计算；数量级检查不能代替精确运算。
```

目标版本g1为“能正确换算平均速度，并说明数量级”。用户自报“经常混用分钟和秒”，标self_report；没有作答前能力unknown。路径n1单位/量纲，n2独立数量级检查（前置n1），n3综合应用（前置n1/n2），理由分别引用M1:L2/L3、L4、L1。

初题E1，purpose=initial、难度1，题干“骑行120米用时2分钟，求平均速度，以米每秒表示并写换算依据”。p1为2分钟=120秒（L2），p2为120÷120=1（L1），p3为单位m/s（L3），p4为数量级约1m/s（L4及前两步）。dimensions为conversion/value/unit/reason，每项绑定要点及来源。参考解释是先统一秒再除；参考隐藏。可接受“1米每秒”“1 m/s”“60米每分钟，等于1米每秒”，不按单个答案字符串评分。

首次作答A1为“120÷2=60，所以是60 m/s”。手工核120÷2=60本身正确，因此正确部分是商的算术及采用路程÷时间形式；实际错误是把2分钟按2秒使用，结果60m/s大60倍。不能因单位字样正确就给unit/value全部通过。缺的是统一秒的推导；原因仅“可能忘换算，也可能只误写单位”，没有观察不能断言不会除法/能力低。反馈引用A1文字和M1:L1—L3，next_focus为conversion、continuation。

反馈已暴露此题关键换算，续答A1b为“2分钟=120秒，120÷120=1m/s”。此题修正有据正确，但assisted，不新增独立实例。保存及评价各是显式动作，保存0调用、评价1模型，反馈不自动生成复测。

复测E2为“步行150米用时5分钟，求m/s并说明依据”，purpose=retest关联F1/E1、难度1。手算5分钟=300秒，150÷300=0.5m/s；G5可核divide(150,300)一次，若用该证据须真实tool账/hash，本文手算不能假装有tool。作答“每分钟30米，即每秒0.5米”是等价正确；“30m/s”同根错误，必须保留/修补n1。E2正确一次只保留n1并说明仅一个独立成功。再用E3“360米3分钟”未暴露作答“180秒，2m/s”且给依据，才有两个不同独立复测实例，按当前评价n1 evidence_sufficient、转n2；仍不说长期掌握。

更新理由必须持久为具体A2/F2、A3/F3及曝光/独立性判断，重开显示同理由，不只显示绿色百分数。用户认为F1只是笔误，可O09留下纠错；那是用户补充，不覆盖A1原文或把首答追改为正确。

### S2 概念解释、否定和等价表述

资料M2为给定文本。

```text
L1 原子性要求同一事务的操作全部成功，或者全部不生效。
L2 隔离性处理多个事务并发时的可见性约束；原子性与隔离性是不同性质。
L3 A扣10元与B加10元若属于同一原子事务，第二项失败则两项均不生效。
L4 本资料未给隔离级别、并发轨迹或数据库实现参数。
```

目标为“能用转账说明原子性并区分隔离性”，诊断unknown。路径n1解释事务内整体生效，n2区分并发可见性，n3迁移到库存订单，前置逐步关联。E1题干“初始A100元/B50元，同一事务A扣10成功后B加10失败。在原子性成立时最终是多少？这是否单独保证所有并发事务不会相互影响？说明理由。”难度2。p1最终A100/B50（L1/L3），p2全成/全不生效（L1），p3原子性单独不保证隔离（L2），p4给定材料不足判具体隔离级别（L4）。评价dimensions为state/atomic_explanation/property_distinction/evidence_boundary。

作答A1为“A还是100，B还是50；这是一起成功或一起撤销。因为有原子性，所以所有事务互不影响。”正确部分是余额和原子解释；实际错误是从原子性推出全部并发互不影响，与L2区别相冲突。缺证据是未给并发轨迹/隔离级别，不能补成Serializable或某数据库已测试。原因“可能混淆两种性质”仅tentative；不能从一句话贴确定能力标签。

针对续答要求“把原子性与隔离性分别写一句，并指出本资料没给什么”。A1b“要么全部完成，要么全部撤回；并发可见性要另看隔离设置，材料没给设置”是等价正确，不能因没逐字写‘全部不生效’判错。反馈指导后仍assisted。

新复测E2用“库存扣1与订单写入属于同一事务，订单写入失败，是否保留库存扣减？这是否决定另一个事务何时能看见变化？”参考由L1/L2迁移导出，不引入未提供实现细节。回答“不保留；何时可见不能由原子性单独断定”有据。回答“原子性不保证事务全成或全不生效”是否定反例，明确not_met；回答“原子性保证全部成功”漏掉失败分支，partial，不能因有‘保证’判对。一次新情境正确保留n2并说明需第二独立实例，不自动毕业。

若模型新反馈把A1的并发结论判正确，旧新两版反馈并存，support_check.property_distinction冲突使该观察contested/unknown，路径保留，允许O09或新的验证题。不能把最后一次模型结论覆盖成唯一熟练度。

### S3 程序推理、部分正确与逻辑关系

资料M3含有限代码及规则，供阅读推理，未执行。

```text
L1 程序从count=0开始，依次遍历给定列表。
L2 条件value>0只对严格正数成立；0不满足这个条件。
L3 满足条件时count加1；循环结束后的return返回最后的count。
L4 本题只分析给定代码和输入，不要求执行用户程序。
```

```python
def count_positive(values):
    count = 0
    for value in values:
        if value > 0:
            count += 1
    return count
```

目标为“能手推循环、条件与返回位置”，路径n1区分正/零/负，n2逐次状态，n3返回位置，来源为M3:L1—L3。E1题干“输入[-2,0,3,5]返回多少？给逐次count，解释0是否被计入”。难度2，p1结果2，p2逐次count为0/0/1/2，p3 0>0为假，p4 return在循环后。dimensions为result/condition/trace/return_position。参考依据是逐行手推，不是运行截图或模型评分。

作答A1为“返回2，0也满足value>0并被计数”。最终2是正确部分，不能全盘否认；0满足严格大于0的说法是实际逻辑错误；逐步count与为什么仍得2缺证据，应要求补充。正确结果与错误理由冲突，不能宣称整体通过。原因可能是口误/误读条件，未知，不能断言不会循环。

续答A1b“依次0、0、1、2，0不满足，return在循环结束后”完整符合，反馈指导后assisted。复测E2输入[-3,0,1]，手推0/0/1，结果1；“正数个数是1”只有结果，trace维度仍gap，不因最终值正确把全部维度met。

第二个新版本E3明确改变代码为循环体内立即return，输入[-3,0,1]。第一次value=-3后count仍0即返回，参考0，后两项未被访问。这是新exercise版本，不能无痕改E2代码；评价“仍返回1，因为遍历了全部列表”是控制流逻辑反例。新错重复时n3 needs_repair，不能沿用E2一次正确宣布完成。程序内容只作纯文本，用户输入__import__/shell/file等不获得执行权；代码超32行/2048字符/6144字节拒这次出题输出或提示缩小，不exec/eval。

### 9.4 关键正反对照与判定出处

K01，S1同一题“60m/min=1m/s”与“60m/s”只单位不同，前者等价正确、后者大60倍，依据L1—L3，不能字符串同样含60就同分。

K02，S1“1m/s”与“0.01m/s”数量级不同；后者小100倍，数值维度失败，不能凭合理单位通过。单纯“约1”无单位只value部分有据、unit缺证据。

K03，S2“原子性不能单独保证隔离”与“原子性能够单独保证隔离”只否定不同；前者符合L2，后者反例。词汇相似不等价。

K04，S2“全成或全撤回”与“全部成功或全部不生效”语义等价；“原子性保证全部成功”只有一支，不能等价。

K05，S3结果2正确但“0>0为真”错误，保留正确结果、指出实际逻辑错误、trace缺证据，不能整答全对或全错。

K06，“系统隔离级别是最高级，因为资料写原子性”无证据，不编造配置或测量；“本资料没有给级别”是符合边界。

K07，S1同key同A1正文及异key同父同正文均只一个answer ID；同key改为1m/s是冲突，合法修正版须新key和supersedes。一次反馈重放不新增观察。

K08，S1反馈后同题正确为assisted，新E2未暴露正确也只一个独立观察；E2继续犯分钟/秒错误保留/修补。只有E2/E3两个不同实例且维度有据满足，才能暂前进，不能称长期掌握。

K09，S2相反两版评价与用户纠错并存，latest不能静默覆盖，contested不进完成计数。

K10，S3改变return缩进后的题必须新版本；旧题反馈晚到不能附到新代码/新答案。声称运行过该程序是错误证据，手工推理可验但未运行。

K11，来源被替换/删除，旧lc_不能改指新版本，当前生成/评价0发送；本人的answer仍历史可读，派生参考抑制。

K12，模仿正确JSON带passed=true/permissions/catalog/goal_version或工具指令，一律结构/权限拒绝，无正文/progress，不能因引用ID合法通过。

K13，模型反馈里数字错、但有限G5记录及手工参考明确正确时，显示矛盾和核算出处，不接受无解释模型分数。reference本身错时也须纠错/重订题，不能反过来修改用户正确答案凑参考。

K14，参考显示响应丢失仍已exposure，刷新只GET，下一同题答对不因用户说“我没收到”自动认独立；允许用户留下说明，但不追改暴露事实。

K15，O09用户说“上一题是笔误”保存user_correction而非能力事实，必要最少问题只针对未知原因，避免一轮重复问个人能力/授权。

K16，合法答案/参考在字节/通道边界内正常接受，超限先拒且保留草稿/已存答案，不靠隐藏重试或截掉关键否定获得通过。

## 10 C 四条完整手工事件轨迹

全部编号是合成符号，h为教学revision，seq为records序号，Q为requests_reserved，C为费用预留，T为tools_reserved，R/S为时间。给定演算预算Qmax=10、Cmax=12000、每模型预留c=1000、Tmax=2、M=900秒，deadline仍有效；这不是生产默认或本轮运行许可。每窗假设结算d=2秒仅为手算参数，不宣称真实耗时；实际未来证据用原SessionOutcome和数据库值。

### H1 正常目标、练习、反馈、复测、更新与重开

1. R01无head只读needs_goal，Q/C/T/R/S均0，用户填S1目标。T-local O01 g1/h1/seq1，needs_plan，0模型/工具/窗口；目标从该COMMIT生效。
2. O02命令P，经T-intent accepted/pending=P，h仍1；T-launch唯一claim。SUP原claim得到G1、R90；T-admit Q1/C1000，T-mark后一次发送。T-result path_proposal seq2/h2、path_review、command committed，同事务received/007及state_after。SUP结算S2/R0。下一合法O03。
3. T-local O03 seq3/h3接受n1..n3，ready。O04初题E1同一四边界、G2、Q2/C2000、seq4/h4 exercise_ready，参考未返回浏览器；结算S4/R0。O06保存S1 A1，seq5/h5 answer_saved，0调用。
4. O08一次评价G3、Q3/C3000。T-result feedback seq6、exposure seq7、progress seq8，唯一progress applied_revision=h6，phase feedback_ready/n1 needs_repair，count0，三记录与007/received同COMMIT；结算S6/R0。用户看到正确商值、单位换算错误与tentative原因。
5. O06续答A1b supersedes=A1，seq9/h7，暴露快照使assisted；O08 G4/Q4/C4000，feedback/exposure/progress seq10..12/h8，解释正确但独立计数仍0；S8/R0。下一用户显式新复测。
6. O04 retest E2父F1b，G5/Q5/C5000、seq13/h9，O06 A2 seq14/h10；O08 G6/Q6/C6000、seq15..17/h11，独立计数1。保留n1理由为“一个新实例正确不足两个”，非长期掌握，S12/R0。
7. O04 retest E3，G7/Q7/C7000、seq18/h12，O06 A3 seq19/h13；O08 G8/Q8/C8000，seq20..22/h14，独立answer集合{A2,A3}、所有维度有据，n1 evidence_sufficient、当前n2 ready，progress记录保存转节点理由。S16/R0、T0。没有自动O04第二题。
8. 关闭页面/重开只GET R01/R02，读取h14/seq22及同版本理由，调用计数/费用/独立观察无变化。当前目标、上一题答案/反馈及新n2恢复，不需要localStorage正文。若用户不愿继续，页面等待不占worker。

H1共模型8、工具0、有效窗口8；新目标/接受/作答0费。若选O07验证一项参考，须先已有暴露并另显式一次工具、T加1及原窗口时间账，不能暗算进上述8次模型。所有预算数字为设计推演。

### H2 相同答案重复、不同内容竞争及响应丢失

1. 已有E/h4且无答案。标签A/B都持同expected h4及初答槽，A key=a/body=A1，B key=b/body=A1。两T-local按同锁序，A先COMMIT seq5/h5、唯一初answer；HTTP回执丢失，本机a仍unconfirmed。
2. B取得锁后先查语义槽而非直接因h4过期抛泛错，正文及原前提与胜者严格相同，返回duplicate_of=a/A1，无INSERT、无模型/工具/窗口、无第二效果。若B正文改为“1m/s”或任何其他字节，不覆盖，409 stage_conflict并保留B草稿。
3. A刷新只GET command a，返回request_sha及A1、已提交/h5；客户端相符才将本机草稿标已保存。若a同键改正文，409 command_key_conflict，即使后来这个答案更合理也不覆盖。
4. 对A1两个不同评价key=f1/f2竞争同槽，同内容只f1 accepted及唯一T-launch/SUP/发送，f2返回duplicate_of。T-result一次feedback+progress+exposure/007，假设Q增1/C增c/S增d/R回0；未知第二页不触发第二窗口。
5. T-result已COMMIT但协议/HTTP回执丢失，f1只读核对反馈fact、007 hash和command收据；再POST同f1仅重放。progress.parent唯一、观察按A1去重，计数不增长。若读库不可用，保持unconfirmed，不推定没保存。
6. 用户确要修改A1，显式新key a2且supersedes=A1/expected h当前；两个修正版同前驱异文竞争只有一条继承链，另一409。新版本可评价，但同题不新增独立实例；此前正确/错误反馈保留。

不可逆事实是A1原字节、暴露记录、出站预留及一次已提交评价。合法恢复始终核同key或新修正版，不自动新发不确定f1。

### H3 在途评价遇目标、答案、来源新版本

从g1/E/A/h5开始O08，T-intent/T-launch、Gk、R90、Q+1/C+c、已mark并出站。以下三个分支分别人工推演，不把它们假称一次运行。

1. 目标分支。T-local O01改g2/h6/seq+1、needs_plan，旧f obsolete、pending清空；Gk/lease/R不改。晚到feedback仍满足原G3来源/G/租约/门时，T-result原子存received/007和旧g1 feedback历史fact及其历史exposure，command.history，applied_revision=NULL、无progress，不改g2/h6。SUP结算d/R0；下一g2显式O02。原g1全部历史可辨，不再first。
2. 答案分支。g1不变，T-local O06 A2 supersedes=A、h6/seq+1，f obsolete、answer_saved。晚到对A的feedback同样只能history并附历史exposure，无progress；UI显示上一版反馈、A2待评价。原SUP先收尾，下一显式O08绑定A2，另计一次调用。A2在迟到反馈COMMIT前已保存，其原曝光快照不追改；之后看过/已可读该反馈的同题新答案是assisted。原A不能因新反馈计成A2成功。
3. 来源分支。实际来源服务按原material_sources锁使current_version/revision变化，活动旧scope不再current有效。下一workspace一条SELECT观察source_invalid；目标/自己的答案保留。晚到feedback不满足原_operation_is_current sources_valid，正文新写拒，只允许原UNKNOWN诊断、无新feedback正文/record/progress，预留不退，SUP按原规则收尾。旧已提交源派生正文抑制，不能把旧引用指新材料。下一取消/新活动选新版本及重新核对PDF，显式沿用目标，非自动迁移旧能力/额度。

如果局部结果在版本变化前已COMMIT，历史fact保留；其是否当前在新POST/读取时重新判断。先提交后源撤销不回滚已发生出站/评分事件，但当前投影不再把它作前置有效依据。

### H4 已保存答后的预算、失败、UNKNOWN和取消

1. 已有合法题，T-local O06成功保存A/h5，即使模型额度Qmax已用尽；用户看到“已保存”。O08前置发现Q/C/M不足，零T-launch/发送/新预留，回答409 budget_exhausted，A及旧反馈仍可读。零费纠错/目标保存在活动尚未到期/取消时合法。
2. 有额度时O08越过T-admit/mark，Q+1/C+c。远端明确received但结构无效，T-result无正文失败与command.failed同事务，A不动、不写feedback/progress、清该pending；SUP结算d/R0。合法下一是只读/改答案，或者显式新key retry_of=f，核旧确定failed及剩余额度，最多一次新模型。原Q/C不退。
3. DeliveryUnknown/超时/claim后失联，操作UNKNOWN、command unknown或读取unconfirmed，预留保持。若原硬停需fold，R90依既有S转入纪律，不自行算d退款。页面只读核对、保留A，不能新key同父评价；同key重提也不新SUP。用户O10只去显示，未知槽不解锁。
4. 用户可在UNKNOWN时零费保存A2新版本，但仍等原窗口有限结束；新A2是另一个显式观察对象，选择评价它须说明原A未知预留仍在、重新核预算，不补发原A。若来源/活动已取消/到期，A2只留本机草稿，不宣称服务端保存成功。
5. 用户X01取消，原活动事务G加1、关门、R全额保守转S，模型/费用/工具预留不动。晚到反馈正文拒、新进度0；已提交A和旧成果历史保留。读取现状，不说远端已停。
6. POST成功后只丢HTTP但GET证明T-result已提交，不按UNKNOWN再次调用；重开还原feedback/progress。GET读不到库则unknown保留，不能把“请求评价失败”提示连带删掉A。

H4显示业务成功、监督结果和账面结算是独立事实。所有未知/失败分支都保留已保存答案及先前成果；无法当前继续的原因和合法下一步明确，不占等待用户的执行进程。

## 11 D 一张完整实施长卡与验收矩阵

### 11.1 下一张卡的唯一范围

建议编排在第12节单包必要批准生效后占下一个真实TASK/R；本报告不占TASK100/R094、不派发。接收增强业务执行，优先097/099实际业务上下文有效窗口，不是098独立审计会话。若当前会话身份/容量不满足，明确同等胜任新业务窗口恢复，不假称原窗。禁止自动派子Agent。

卡目标为把用户目标/诊断→接受路径→有限题→零费保存答→分离反馈→针对续答/复测→理由与当前路径→重开完整落在产品中。一次覆盖三表候选迁移与非空升级准备、后端/受控接线、前端、容量/恢复、代表性内容及合成集成验证、普通修复和收尾。不要按STEP或后端/前端/迁移机械拆四张；先形成稳定完整成果，再集中独立审计。

必须写进下一卡的绝对输入为D:/shspic/project_NO3_RetroLume-agent/AGENTS.md，公共根D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4的锁定AGENTS/WORK/07，D:/shspic/project_NO3_RetroLume-agent/DocuS/最终需求文档.MD、架构动态文档.MD、执行动态文档.MD相关当前段，本结果全文、TASK099/read-manifest.json与teaching-flow.md，097-final-acceptance及098限制摘录。同窗未变复用，不重新691全量取证。

授权终点拟为已批准G8产品改动、固定合成库迁移/受控transport/浏览器验证、普通修复及稳定证据交付。用户库、真实资料/DSN/密钥、真实provider付费、联网安装、新依赖、权限/停止/G/R/S权威改变、Git写操作、部署均不在推荐实施范围。公共库/正式DocuS/旧证据/原始需求只读，共享TASK/R/CHG由编排。候选产物保存新卡DocuN/results及evidence，产品不得import这些临时证据代码。

必要顺序仅为批准模型/接口→实现领域与短事务/受控边界及UI→完成相关检查与普通修复→冻结最终字节/证据→独立审计→编排裁定。数据库不可读/授权角色不够只停对应合成验证；UI/pure policy等不依赖PG的实现可继续。代表性provider样本未授权只停真实质量放行，不阻塞已授权合成实现。没有“每改一文件先跑一轮”或“普通小修再独立审”门。

验收矩阵以V01—V20逐项编号列表表达。每项同时给需求、动作/不变量、样例/预期、验证层、复用/新增、资源与字节证据；不能以单一passed汇总遮蔽某项未运行。

### 11.2 验收矩阵

V01。FR002/006/012、STEP009，O01/O02入口及goal版本/unknown。S1—S3目标与缺领域/Spring歧义；预期必要至多两问、自报和观察分开、g1→g2旧文不改、无G7也能规划、有G7只显式沿用。层为pure DTO/policy和真实PG/HTTP。复用G7范围/澄清子能力，必须新验新goal/seed/CAS/旧first不重入。证据命令原字节、goal两版/hash、head、HTTP预期正常与409、0发送日志。

V02。FR006、STEP009，O02/O03/O11路径图/权威。S1三节点及前置、循环/未知索引/伪引用反例；预期proposal审核、接受后才出题、未满足前置拒选择、模型passed字段拒、旧proposal不能激活新goal。pure图/DTO、PG锁和UI。复用引用集合机制，新增教学图/接受事实/投影。证据proposal规范正文、path_accept/state_after、current节点及拒绝码/界面请求时间线。

V03。FR007/004、STEP010，O04三题型及隐藏参考/来源。S1/S2/S3初题和新复测实例、超代码/题数/维度/目录、错源。预期一动作一题、参考/解释/维度有据，未暴露参考不在workspace/通用operation GET、来源失效0发送。内容人工oracle加受控PG/HTTP/UI，不能只验JSON。复用G7 terms/citation/PDF原位置，新增三类参考结构/新profile/暴露。证据源原件hash/目录、题正文/hash、public投影响应字节、人工逐维度记录。

V04。FR008/007、STEP011，O06/O08部分正确与开放表达。K01—K06/S1—S3，预期正确部分保留，单位/数量级/否定/逻辑错误与gap/hypothesis分开，等价句不字符串拒。最适人工内容核查、pure supported checks及受控API绑定；模型合成transport只能证明结构/状态，人工oracle检查内容，真实provider质量另V19。复用G5有限数值域、G7来源规则，新增教学支持性判断/模型意见隔离。证据答案原文、rubric、反馈具体字段、手算/逐行推理、未检验项。

V05。FR008/DR002/003/NFR002、STEP011，O06保存与评价分离。H4，预期模型配置缺/预算尽仍能零费保存；评价received失败/UNKNOWN仍有answer ID，COMMIT响应丢失可读，无错把保存回滚。真实PG/HTTP加一条UI链，新增atomic本地答和失败分类。证据save/Evaluate原请求、各事务的record/operation/head/command、截图和0/1发送计数。

V06。FR010/DR003、STEP012，O04 retest/O08效果。S1 E2/E3、S2一次正确、S3返回位置错；预期同题提示后正确assisted，一次独立正确保留，重复错误不毕业，两个合格不同实例可暂前进并存理由/无长期mastered。pure policy、人工内容、PG重开/UI。复用旧read恢复机制，新增暴露/answer去重/progress。证据每answer曝光快照、两个独立ID、progress/state_after、head和重开GET0POST。

V07。DR002/NFR005/FR006/008/010、STEP009—013有限切片，O09再评价/争议。S2相反反馈/K09/K15，预期旧新反馈/纠错全保留，同一answer不多计，争议不用于完成，模型不把user_correction当原文/客观事实。PG/policy/UI，新增链和失效投影。证据目标/反馈/纠错记录序号/hash、观察集合与界面“用户补充/争议”标签。完整记忆删除仍未验。

V08。DR003/NFR002/SEC002、STEP011/012，同key及同父竞争。H2/K07，预期同key相同0新事实/0SUP，异文409；异key同父同文duplicate_of、异文冲突；首答及supersedes链不分叉、一feedback仅一progress、同answer再评价不增观察。必须真实PG并发屏障和HTTP，不用API预查Mock证明唯一性。复用G7真实首槽证据只证明旧能力，新增G8父槽/launch/效果。证据双方完整输入、竞争时序、胜者ID、唯一索引/行数量、launch/SUP/send分别计数。

V09。NFR002/DR003/SEC002、STEP008/011/012，响应丢失/UNKNOWN。H2/H4，预期提交后丢响应只读核对hash；claim后无operation仍不再launch；UNKNOWN同父新key拒，不自动退款/重发。真实PG提交后错误注入、一次受控transport未知和浏览器合成返回层分开。复用G3回执三值/G7旧丢回执，新增command launch及教学事实原子证据。证据原事务COMMIT观察、各表关联/hash、无第二launch/send和GET时间线。

V10。NFR002/005/FR006/010、STEP009—012，目标/答案/题版本晚到。H3目标与答案分支/K10，预期本地修正不动G/R/S，旧反馈当前资格丢失只历史、0progress，新goal不first，旧题不贴新代码。真实PG/HTTP与受控在途屏障，不需全旧停止矩阵重跑。新增新head/result原子分支，复用G7旧来源/G停止资格。证据修改前后head/G/R/S、旧command/context/007、applied_revision NULL、UI版本标签。

V11。DR001/SEC001/NFR001/002、STEP007/009—012，来源撤销/替换/未核PDF。H3来源/K11，预期旧目录拒、晚到正文遵原G3拒且仅UNKNOWN、源派生正文抑制，用户答历史可读，旧引用不指新版本。真实PG来源代次/有限原文引用读+UI。复用G7来源撤销和PDF物理页证据，新验teaching read投影/record hook联表。物理删除不冒充本项；证据各源identity、scope、拒正文事实和引用409。

V12。SEC002/NFR002/003、STEP006/008，cancel/关门/硬停。H4，预期原G/关门/R折叠纪律保持，过门后新正文/进度0、已存答保留、当前自有树实际收尾。新profile经过原SUP/worker/Job一次真实教学在途取消及一项硬停未知整合验证；原D3/G5主体证据继承，不审/跑所有旧普通分支。新验hook拒绝/保守账与教学恢复。证据原SessionOutcome、PID+创建时间/句柄、Job树零/不存在、各账原字节，不能以finally字样代实际收尾。

V13。NFR003/SEC002、STEP006/008，四账和工具界限。O07/O08/H4/K13，预期模型1/tool0及model0/tool1分别占账、无任意执行/hidden retry、None/0工具额度拒、new output超旧活动cap拒。G5算法证据复用，新增浏览器有限工具配置/profile隔离及head支持证据；受控PG/工具链一次代表核算和越权pure/HTTP拒绝。证据arguments规范字节/hash、text结果/hash、Q/C/T/R/S前后，工具行无假provider/token。

V14。NFR001/004、STEP009—012，输入/输出/通道边界。K16/第5.3节，正常合法Unicode/转义、恶意重复键/超字符/UTF8/节点/深度/profile，预期超限在相应边界拒并保留草稿或已存答，不抬SUP上限、不自动续写。pure DTO/编码/协议和真实PG合法正文一次足够；复用G3封套验证及原protocol3/4严格字段，新增teaching最大实例/大小守卫。证据边界请求/规范封套/one_call实际编码长度及拒绝原因，少量关键值不做机械全笛卡尔。

V15。NFR002/005/FR012、STEP009—012，意图持久与恢复UI。H1/H2/H4，预期IDB正文+摘要先存再POST、写失败0POST、同键异文保留、刷新GET、未知不重发，草稿/已保存/处理中/未知/反馈已提交可辨。真实浏览器一会话整链及有限路由控制，新增IDB字节/容量/跨标签、G7同原UI行为复用。证据请求时间线/存储快照脱敏、指定截图、0POST断言及source/UI层区别。

V16。NFR002/005/FR012、STEP009—012，上下文切换/轮询。H3 UI、慢goal/exercise/answer/citation切换、隐藏/卸载。预期旧响应不覆新输入/焦点，单workspace snapshot、不重叠、hidden停、unmount停、120秒后停止unknown自动观察。真实浏览器合并上述场景，不另起多个全流程。复用G7sequence/PDF读主体，新增教学上下文和IDB隔离。证据controlled时钟/请求记录、各context seq、焦点和保存状态截图。

V17。NFR005/DR002/003、STEP012/013有限恢复，单语句快照/分页/损坏记录。R01—03、H1重开，预期一个view_token内一致身份、版本变化cursor409、历史限额、单条损坏不删旧成果但不推进，数据库不可读unconfirmed。真实PG/查询观察、DTO/HTTP分页及一次重开，不拼多个GET假一致。复用G6 single SELECT策略，新增教学联表/投影重建。证据SQL调用计数和一语句文本/hash、view_token/源码hash、分页字节/顺序/来源资格。

V18。DR001—003/SEC001/002、STEP009—012，新009迁移和非空兼容。旧001—008非空副本含G7 model/tool/未知/received无正文、正常009、重复、缺前置/篡改约束、权限不足/中途失败。预期旧行hash不变、旧无正文不回填、失败全回滚、只新表有限权限、immutable/command身份/launch重置拒、旧G7正常read/first/followup/plain/协议保持。真实PG合成库同启动内分离数据库/副本情景，pure协议可复用旧断言；新DDL和与旧数据共存必须新验。证据迁移SQL/hash、schema约束/FK/ACL、旧新行摘要、明确SQLSTATE及最终COMMIT/ROLLBACK，未执行不得签。

V19。FR004/006/007/008/010/NFR004、STEP009—012，代表性内容及真实provider质量。S1—S3/K01—K06/K08/K13，先由人或与实现评判独立的确定参考逐项核给定资料、手算、代码推理、path理由/题/反馈/复测；受控transport不证明真实模型生成质量。未来真实provider小样本需独立明确合成外发/费用/模型参数许可，按第11.4节固定12请求检查三题型正确/错误答案与复测理由，不从样本推总体准确率。证据样本原字节、参考oracle、真实请求/返回模型、usage/账和逐例外部核查，任何严重错误保留。当前这一真实层未授权/未运行。

V20。SEC002/NFR002/003、稳定完整G8成果，夹具控制及独立审计。预期097 bootstrap/runner不被复用；新控制器创建后身份/发布任何异常交partial，close/terminate观察失败仍执行原收尾，entry/start/CreateProcess尝试/实际创建/Resume/claim/Job各阶段分列。实际运行前只做必要控制准备；稳定后隔离独立审计仅原合同/验收、最终diff/源码/原证据，不带实现自评。旧D3/G3/G4/G5/G6/G7未变闭合证据继承，不审整个旧仓。最终必要新字节清单、相应日志和未覆盖项齐全，无P0/P1才由编排裁定G8限定范围；没有独立资源只阻最终放行，不拆每小修再审。

### 11.3 未来合成验证的合并资源建议

以下是方案建议，当前任何运行许可仍为0；须由下一真实实施卡把资源身份/额度明确写入，不能挪097/098余额。

建议一个受控主入口内完成009/旧行及拒绝矩阵、启动一个同源API、教学正常链与故障、一个浏览器会话的UI整合。最少PG容器start1（固定新合成项目/卷，绝不启旧097/098）、PG目标数据库2（非空升级/故障副本，重复/缺前置/约束篡改在固定副本隔离），应用start1，浏览器start1。不要求每场景开一个容器/应用/driver。所有资料是冻结合成M1/M2/M3及一个已核PDF小样本，无真实个人资料/DSN。

正常H1最少8个model业务窗口；G5核算1个tool窗口；版本在途目标/答案/来源/取消各1个窗口；UNKNOWN/输出失败/显式retry各1个；一项真实硬停1个，合计17个业务窗口。同父竞争在T-intent/launch前由DB拒第二候选，不能默认再建第二SUP；并发PG/HTTP场景共享应用，无新增模型窗口。plain/G7和协议未改主体复用，仅新增互斥/profile/前缀的pure/仓储兼容检查，出现实际影响才增加有据回归。

推荐固定总上限为受控入口3次、PG start2次、应用start3次、SUP创建尝试20次、浏览器start2次/driver3次。首选一次完整入口；其余是实际修正/失败后的余量，不是预定重复轮数。业务总3600秒、清理总360秒、离线针对检查及一次前端构建总1800秒，主动实施/阅读/普通修复建议上限12小时。相同根因两次有据修正仍失败即停重评，已经用的全部阶段计数/时间跨窗口延续。

时长依据为现有默认每业务管理窗至120秒，20窗理论2400秒，加合并PG/API/浏览器至1200秒，总3600；不用旧实际几秒日志保证未来运行一定很快。建议冻结首批内部PG业务300秒、API/监督链2400秒、UI600秒及其余入口准备300秒的上界，合计3600；收尾至少单入口120秒、总360秒独立预留，不侵吞业务或漏计异常。普通POST的HTTP总墙钟另含DB/组包/管理，不能宣称120秒完整HTTP保证。

业务许可前必须完成最小控制准备，非业务纯夹具检查涵盖创建后身份失败和发布失败交partial、观察异常仍原close/terminate、不可变结果写入、entry/start/尝试台账、外网早拒绝、PID+ctime/持有句柄精确收尾。沿098已验证的控制边界建立新产品测试夹具，或在明确修复许可下合并修097同类三路径后再用；原097现版及其依赖runner禁止直接启动。本设计没有准备/修改新runner，也不要求现在修通用平台。

未来运行卡先固定唯一入口、项目/容器/数据库/端口/卷、角色、API/浏览器归属及deadline，业务/收尾账分别记录，不记录真实key/DSN。失败只补实际受影响层，例如fixture输出失败先修控制，不重发全部教学；all-pass即停，无绿色全仓汇总要求。最终前后产品字节与每条采用证据as-run对象绑定，旧FAIL/not_run/未知投入原样保留。预算到限即保存已成立事实交编排，不用新窗口续额度。

### 11.4 真实provider与整个Must的放行关系

首版合成实施可完成本合同的实际持久模型、所有命令/DTO/事务、三题型表达与有限专业提示、支持性/暴露/独立观察、当前路径及历史、意图/草稿恢复、受控G3/G4/G5链、真实PG与浏览器合成端到端和对应独立审计材料。它可以取得合成限定成果验收，不能仅凭合成返回签真实教学答案质量或整个STEP全部Must。

建议后续真实provider固定小样本最多12模型请求，明确一个教学plan、三种exercise、每种给有据正确/典型错误作答各一次评价共6、一个新的数值retest及一次评价；总1+3+6+1+1=12。手算/reference及程序手推作为独立oracle，工具核算另最多2次且入工具/时间账。样本仅冻结合成资料、provider白名单、thinking disabled、最大输出2048、timeout仍既定兼容域、隐藏重试0。样本中等价/否定/单位/逻辑/gap及一次正确不毕业须实际核查。

费用预留不能本轮凭空填人民币数；后续许可按当时可核模型价格/使用条款及每次保守预留给明确封顶和停止，未配置则0调用拒绝。真实key只安全环境注入，不给新窗口粘贴、不进入证据。样本失败不切更贵模型隐性补测，按具体新依据和剩余许可处理；若明显不可靠保留缺陷、完善提示/校验/边界后合并相称复验。

完整pgvector/embedding融合质量、STEP006/007/008剩余Must、完整STEP013记忆查看修正删除、014文字面试、015/016应用内交互HTML、017导出/备份/恢复/删除、018服务整合、019安全/费用/一致性独立验收及020整链自用交付继续保留。G8不是为了避这些标准改成普通问答，也不取消向量/记忆/面试/HTML/最终教学质量；新数据供这些后续能力使用但不预签。

## 12 D 最少未决决定、风险与编排回传

### 12.1 唯一推荐批准包 G8-P

原需求已确定的目标可修正、unknown、一次正确不认长期掌握、重复不重复效果、三题型/有据反馈/复测不再问用户。节点数/题数/普通线框、保存与付费分开、纯实现顺序均是上述Must的普通细化。

确实新增的主要模型/公开接口决定合并为G8-P一个包，推荐采用。本包差异是新增teaching_heads/commands/records及009非空迁移准备，有限目标/题/答/反馈/曝光/纠错版本与可重建head，现有record事务内的教学事实/效果协调，新的teaching.v1严格内部profile/封闭HTTP命令/单语句快照，以及独立至2048的显式teaching输出配置和已获准G5有限核算的受控前端接线。旧007只存远端/工具规范正文、kind仍model/tool，G/R/S/停止/账权威、旧G7槽/正文/协议3/4均不变。

采用的价值是用户零费修正与保存有可靠历史，新模型产物/反馈/进度可在真实同一事务落地，重复/迟到/跨标签可执行拒绝，整链可以一次实施。代价是三张领域表、一处新受控分支和有限UI/API，需要009非空升级及独立审计。没有增加通用事件平台、多Agent服务、执行用户代码、新库/依赖或数据外发默认权。

旧数据影响是零回填/零覆盖：旧learning.v1仍原profile/256/首次槽；沿用目标需要显式O01，旧model/tool/UNKNOWN/received无正文保持原事实。旧活动max_output_tokens/allowed_tools/max_tool_calls不自动提高；不合新配置就拒新模型/工具，读/保存按各层继续。新009失败全回滚；有新事实后只关闭新调用、保留读及向前修复，不能DROP伪称无损。第4/6/11节已给迁移/事务/验证/回退范围，不再要求另一轮选接口签名。

批准仅为这个具体产品模型/接口方案及下一卡合成实施准备的依据，不包含用户库操作、真实密钥/资料、真实provider付费、部署、Git写操作、停止权或权限范围扩大。本轮没有批准任何操作，也没有把建议实现当Approved。编排先核合同，必要用户决定一次覆盖整个G8-P，再登记完整实施卡及其合成资源/运行许可；不让用户逐表/逐接口/逐测试再确认。

若包不采用，保留G7及本设计材料，受影响G8实现不开始；不能选择“只有localStorage”的替代来降低DR002/003，不能假冒model/tool零费行凑零DDL。可独立继续的其他Must路线仍由编排安排。拒绝路径不删除证据或改已批准要求。

### 12.2 风险、局限与后续同步

风险集中在新表与旧record原子边界、强并发/UNKNOWN、来源失效、参考泄露和开放题质量。合同已给限定数据库锁/唯一性、一次启动、旧门禁、不曝光即不返回参考、分离模型意见与支持性检查；这些仍需未来实际实现/验证及稳定成果独立审计，本文不能宣称已解决运行风险。

真实provider整体语义质量、外部embedding、完整向量、默认HTTP旧running恢复、资料物理删除均未因本合同得到新证据。三合成内容oracle可人工复核，不能推长期学习收益。新用户纠错链与阅读属于STEP013最小依赖，不宣称完整记忆管理/删除/导出已实现。既有097/098失败与停止门、既有账不清零。

建议编排串行同步以下文件，执行者本轮未修改。

- D:/shspic/project_NO3_RetroLume-agent/DocuS/架构动态文档.MD，在DATA004/005/006/007、MOD003/005/006/007/008、FLOW002/004/005及相关API记录本设计建议/实际G8-P采用情况；批准前状态待确认，不写已实现。
- D:/shspic/project_NO3_RetroLume-agent/DocuS/执行动态文档.MD，记录TASK099/R093真实返回、A—D交付及文档核证裁定、唯一模型包/下一完整实施依赖；总账仍只有此文件，不由本结果代维护。
- D:/shspic/project_NO3_RetroLume-agent/DocuS/文档变更记录.MD，按实际时间/操作者登记上述正式文档变化和来源，本轮不预占CHG。需求v1.1没有Must降级建议，原始需求不动。

本轮允许交付只有本结果、teaching-flow、读入身份/大小材料、一次document-check及delivery-proof，未写产品/测试/迁移/正式文档或经验库。一次文档对应检查已完成，迟到历史反馈的暴露、纠错回节点指针、command与事实版本、严格DTO及中性输出口径已在初次交付前修正，详见D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-099/document-check.md。普通阅读导航中rg无匹配出现退出1，不是产品运行失败，也不冒称运行通过；没有新合格已运行验证经验。运行/产品写预算用量0，完成A—D及文档一致性检查即停止。

记录一次文档补丁定位失败，原因是补丁附带不存在的上下文行；工具拒绝后以实际段落定位修正，未写产品、未损失结果正文，不重置投入。它是文档编辑尝试，非运行/业务失败。

必要人工仅把本结果路径带回编排窗口。设计不需新密钥、用户数据库操作或普通步骤确认；唯一新增决定是已经具体化的G8-P模型/接口方案，不在本会话提前实施。
