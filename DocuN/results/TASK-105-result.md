# TASK-105 / R-099 文字模拟面试实施合同

完整交付唯一推荐的 G10 最小合同：独立 interview.v1 事实与工作区，共用现有活动四账、007 正文原子提交和原生监督；首版只允许未选择记忆的全新活动。本文为建议合同，未实施、未获 G10-P 采用批准，全部产品运行次数为 0。

根目录 D:/shspic/project_NO3_RetroLume-agent；task_model，锁定 V4.0／公共 AGENTS CHG-0003。需求 v1.1、架构 v0.95、执行动态 v2.17。依据 [任务卡](D:/shspic/project_NO3_RetroLume-agent/DocuN/tasks/TASK-105.md) 与 [冻结输入](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-105/orchestration-setup-20261007/design-input.json)。接收为原 103 业务窗口 A+；A+ 是调度标签，本会话开发者标识为基于 GPT-6 的 Codex，未提供可核实的部署子型号，不以标签推断型号。

本合同分 A 实际基线与用户流、B 持久及接口、C 文件差异与唯一采用包、D 下一完整实施卡及验收。函数位置／原字节指纹见 [函数事实](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-105/design/source-function-facts.json)，46 项输入与冻结清单全部匹配，见 [输入身份](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-105/design/input-identity.json)。核对结论和资源实录在本文末尾及 [会话记录](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-105/design/session.json)。这些是文件读取／设计证据。

## A 实际基线、唯一用户流与事实边界

### A1 可复用事实及面试缺口

- [活动仓储](D:/shspic/project_NO3_RetroLume-agent/backend/app/activities/repository.py:280) 的 PostgresAdmissionLedger 已合成 TeachingLedgerMethods／MemoryLedgerMethods。create_activity:499、revise_scope:464、claim_lease:565、admit:1078、mark_dispatch_started:1506、record_outcome:1672、read_committed_result:1782、list_committed_results:1852 是真实接口。准入、预算预留、发送 mark、终态及停止结算继续由这条链决定，面试不再做一套余额或运行窗口。
- record_outcome 的严格终态等值确认先于新写资格检查；旧 received 无正文不能补写；失效执行只能按既有合同登记 UNKNOWN 诊断；关闭发送门后不能新写正文。教学现已在同一事务联写领域事实。面试须新增同级钩子，不能在服务层先提交 007 再提交面试记录。
- [活动服务](D:/shspic/project_NO3_RetroLume-agent/backend/app/activities/service.py:83) 的 read_result／resume_result 只读，continue_from_result:104 和 execute_tool_action:194 是独立写边界。恢复查询不启动 SUP；新领域必须封住这些通用入口对面试结果的跨 profile 消费。
- [教学仓储](D:/shspic/project_NO3_RetroLume-agent/backend/app/activities/teaching_repository.py:124) 的锁前缀、同键回执、同槽识别、冻结后一次 launch claim 可借鉴；其 goal／path／exercise／feedback／retest、暴露集合、教学支持检查和掌握投影属于教学。009 表及 derive_progress 不接纳面试记录或面试分数。
- [受控契约](D:/shspic/project_NO3_RetroLume-agent/backend/app/capabilities/contracts.py:127) 目前只含 learning_profile／teaching_profile；[ControlledModelGateway](D:/shspic/project_NO3_RetroLume-agent/backend/app/capabilities/gateway.py:100) 与 _parse_success:327 分别校验受信身份和领域输出。新增 interview_profile 必须在这两个真实位置接入，不能换成普通聊天请求。
- [OneCallInput](D:/shspic/project_NO3_RetroLume-agent/backend/app/worker/one_call.py:54) 使用 ModelCallRequest，worker_request:96 按 exclude_none 序列化；run_one_call:218 与 [SessionConfig](D:/shspic/project_NO3_RetroLume-agent/backend/app/worker/session.py:43) 保留原生监督、停止证明、租约及恢复限制。仅增加可选 carrier，不改协议 3、launcher、manager、Job 权威或 recovery=False。
- [记忆准入](D:/shspic/project_NO3_RetroLume-agent/backend/app/memory/repository.py:35) 只允许已选记忆活动使用受信 teach8m／teach8t；_memory_lock_prefix:210 保持来源→记忆→活动锁序和真实资格。面试首版不扩展 v2，不引入 interview-memory，也不改 010 的身份、依赖／墓碑／清理合同。
- [配置入口](D:/shspic/project_NO3_RetroLume-agent/backend/app/service_config.py:272) 具有分层失效关闭，当前无 interview 配置；[前端入口](D:/shspic/project_NO3_RetroLume-agent/frontend/src/main.tsx) 的“模拟面试”尚是占位。现有 TeachingWorkspace、本机正文先存、摘要与 Web Locks 身份机制能复用规则，但教学阶段、intent namespace 和草稿库不能直接混用。

当前真实缺口是面试目标／回答版本／追问与反馈的持久模型、受信 carrier、输出校验、公开接线及恢复工作区。G9 单机有限验收没有验证这些行为；本卡不把计划文件里的面试状态当动态证据。G3—G9 未改资产有效，103／104 不重开；旧 FAIL、UNKNOWN、45 次真实入口、非阻断 O01—03 和尚未放行的完整 Must／STEP018—020／M-1 均保留。

### A2 一条用户主流

用户从“模拟面试”选现有可用资料，使用现有活动创建接口创建新活动；先看到资料范围、模型身份、剩余次数／时间／工具／费用及一次动作的上限。已有活动若有教学／学习事实、调用／窗口预留、未确认操作或已选记忆，不转成面试，界面明确给“请新建未选择记忆的面试活动”。不复制旧预算或自动清空记忆。

start 只在本地登记面试域及可选目标，允许目标暂缺。缺目标显示持久的“希望针对哪个主题、角色或场景练习？”提示；用户填写或修正 goal 后，显式“开始提问”发 ask。目标、材料角色及澄清说明自由填写，不预设岗位／学科。ask 生成一个有来源身份的问题；无法定位可用片段时先以本地问题问具体缺口。目标同名含混时，问题说明候选解释及需要澄清的点，不把“Spring”默认解释成某一个主题。

用户保存 answer，得到不可变版本及“回答已保存，尚未请求反馈”；保存本地回答不调用模型。显式“获取追问或反馈”发 review。一轮 review 仅有两个输出分支：就实际缺口提出一个 probe，或给出 feedback。probe 同时可指出已有支持的部分；用户提交对 probe 的回答，再显式 review。追问达到配置深度时仅给反馈及未解决项，不自动扩出问题、调用或假称通过。每个模型动作至多一次受控调用，没有后台自动循环。

feedback 分开列“回答中有依据的部分”“尚缺依据／不确定”“冲突资料”“建议下一步”，并显示对应回答版本与引用。用户选择“继续下一题”才 ask(next)，或选 finish。题数由用户、目标和活动有限预算决定；没有固定总题数、面试方向或预设通过线。finish 是本地域结束，不取消已发送的远端请求、不新结算四账。已结束场次只读；再练习创建新活动，明确重新确认资料与预算，不自动续旧调用。

goal、correct_answer、bind_scope 允许修正当前场次，增加版本／事件；旧问题、回答及评价保留身份。修正会清除不再合格的当前评价并标旧评价资格，必要时重新提问。刷新／重开仅 GET 持久快照与原 key 回执；任何提交、继续、重试、结束都需要显式用户动作。

### A3 反馈和材料的信任边界

答案、简历、经历、测量、收益、优化效果均为用户陈述。材料角色 resume、experience、measurement 和 unspecified 默认按自报使用；reference 只说明供概念对照，也不是来源真实性的背书。模型输出是受检建议，没有“可信事实”“掌握”“已验证业绩”或分数写入权限。

应用核对引用的 source_id／version_id／revision／原字节 hash、单元／片段 hash、页／行／字符位置和当前资格，得到 position_verified。semantic_support 只是模型对“支持／冲突／不清楚”的解释，与位置校验分别展示。首版不声称通用机器语义证明，不调用教学数值评分／掌握函数；未来技术样本由实施验证的可核查答案与引用逐项评审，不能用模型自评充当通过。

每个认可项必须锚定实际回答片段。带合格 reference 引用的概念认可显示“资料对照建议”，并列语义理由；没有这样的依据，仅认可用户已经说明的内容，不宣称其真实或正确。自报认可由应用固定呈现“你已说明：〈实际回答片段〉；尚未独立核实”，不采用模型编造的业绩认可文本。收益缺基线时具体追问基线值、统计口径、样本／环境、时间窗口和可核查记录；不自动补“提升 60%”的测量、成功项目或经历。冲突引用并列原文与解释，保留不确定。

用户可通过 bind_scope 纳入新版本或补充资料；资料写入继续走原有资料接口，不在面试接口上传、解析、抓取或发送简历。模型只接收当前目标、必要回答版本和有界片段，不接收整份简历／知识库、持久文件路径、DSN、密钥或记忆正文。外发范围预览在第一次 ask／review 前可见，缺模型配置仅关闭模型动作。

FR-011／012 的文字面试闭环由本方案完整承接；FR-010 是学习／教学进度与复测要求，现有实现继续承担，未要求面试必须选记忆。首版面试仅无选择活动，不删已批准 Must。已选记忆或资格不可靠时确定拒绝，不能将背景降成通用 profile 输入；后来若要面试记忆，须另给受信消费类型及完整失效合同。

### A4 工作区草图与恢复

```text
模拟面试                     历史场次／新建场次
资料范围  [当前版本、可用／待重新确认]    查看范围
目标 v2   [自由目标、重点、材料用途]      修改目标
剩余次数／时间／工具／费用；一次提问或反馈的最大预留
首版提示：本场次不使用已保存记忆

当前阶段：等待回答／可请求反馈／正在处理／未确认／已结束
问题／必要追问               对应目标、轮次及问题依据
回答 v3 [多行正文]           保存回答／修改后另存版本
有依据的部分                 回答片段、资料对照建议、查看引用
尚缺依据及冲突               具体缺口、并列来源、补充资料
显式动作                     获取追问或反馈／继续下一题／结束

持久历史：目标修正、资料范围、问题、回答版本、追问、反馈、结束
历史标记：旧目标／旧答案／来源失效；当前资格与历史存在分别显示
本机待确认：查看原提交结果／在安全条件下显式再提交原意图
```

未确认文案为“尚未确认是否完成，请查看原提交结果”；取消／达限保留历史和未发草稿，明确本动作关闭原因。来源失效时提示“资料已更新，确认新的范围后再继续”；不自动采用当前资料版本。旧模型正文若失去资格只显示元数据、旧版本及抑制原因，本地用户回答历史仍可查看。结束本身不降低已有合格历史结果；007 的原有只读资格仍是下限。

工作区和引用异步响应同时核对活动、面板代次、view_token、本机 owner、intent key／草稿 hash；卸载／切换立即 abort 并使代次失效，响应解析前后均复核。迟到问题／反馈／引用不能进入新面板。页面不显示内部运行者、数据库连接、内部文件路径或执行开关；“资料版本”“回答版本”“剩余额度”“未确认”是用户决策信息。

## B 最小持久、状态、接口和事务合同

### B1 封闭类型、规范化和上限

所有新增输入 extra=forbid；JSON 深度≤12、节点≤2000、UTF-8 严格解码，拒绝重复键、NaN／Infinity、整数布尔替代。UUID 使用小写标准带连字符形式；hash 为 64 位小写 SHA-256。文本保留用户实际内容，不静默 trim／改换行再冒充原文；空白目标／回答拒绝。规范 JSON 采用排序键、紧凑分隔符、ensure_ascii=False、allow_nan=False，数组顺序保留；前后端使用相同固定测试向量，不使用浏览器 stringify 的插入顺序作权威。

共通身份为 activity_id、business_key、record_id（UUID）；expected_head_revision：0..2147483647，0 仅 start；expected_goal_version：0..32，0 仅目标未定；expected_scope_revision：1..2147483647。goal_version 增加不超过32；round_index 0..4096；answer_version 1..256；probe_depth 0..4。每活动 command≤4096、record≤4096、一次 effect 最多2个 record。达到上限拒绝新写且可读，UI显示“本场次记录上限”，不是固定完成题数。

GoalBody字段为target非空string、focus:string|null默认null、clarifications:string[]默认空、material_roles:SourceRole[]默认空；target≤1024字符／4096字节，focus≤1024字符／4096字节，clarifications≤8，每项≤256字符／1024字节。SourceRole={source_id:UUID,role:enum}，role∈resume|experience|measurement|reference|unspecified；不提供的当前source默认unspecified，重复／非当前source拒绝，冻结时展开全部用途映射。答案 text≤4096字符／16384字节。SourceBinding={source_id:UUID,version_id:UUID,source_revision:严格int1..2147483647,original_sha256:hash}，范围数1..10；进入原_scope helper时明确映射source_revision→SourceSnapshot.revision，hash另对当前原件核验。现有活动创建最多128源，这是面试额外限制。

command 正文≤32768字节，冻结 context≤49152字节；catalog≤12片段且片段正文合计≤8192字节，回答引用≤12项且发送正文合计≤16384字节。实际发送消息和完整 OneCallInput 分别还必须通过原有服务与 worker 上限（当前 worker 请求／响应至多65536），不是把49152上下文直接视为能够出站。过大拒绝，不静默截去答案／依据改变 hash。面试规范value≤32768字节，加入应用catalog/身份的完整封套仍受007的131072字节硬上限。

公开命令 InterviewCommandInput 固定字段：schema='interview.command.v1'、business_key、action、expected_head_revision、expected_goal_version、expected_scope_revision、body。request_sha256 对加入 activity_id 后、排除 business_key 的完整规范输入计算；body 中的 retry_of 若存在也参与 hash。request_body保存该排除key的同一规范文本，key单列保存，故不同key精确同文可比较；回执回送 hash。不接受客户端传入 provider／budget／operation_id／context／profile／可信度字段。

冻结 InterviewContext.schema='interview.context.v1'，含 activity_id、business_key、request_sha256、action、expected 三修订、goal_record_id／goal_body、sources、material_roles、current round／probe_depth、parent_record_refs、catalog、prompt_version、identity、input_policy='user_statements_not_verified'、limits。parent_record_refs 每项带 record_id／kind／version／body_sha256 和必要正文；model record 引用再带 operation_id／payload_sha256／007绑定身份；catalog 带本节完整来源与单元／片段位置 hash。冻结字段由服务只读加载、准入锁内重新验证，模型不得输出或覆盖。

### B2 三张新表；既有正文和四账不搬移

建议下一真实空闲编号为 D:/shspic/project_NO3_RetroLume-agent/backend/migrations/011_text_interview.sql。本卡仅确认001—010存在且无011，没有创建迁移。

- interview_heads：activity_id UUID PK／FK activities；revision int≥1；goal_version 0..32；phase∈needs_goal|ready|question_ready|answer_ready|feedback_ready|ended；last_seq 1..4096；round_index 0..4096；probe_depth 0..4；goal_record_id／root_question_id／current_question_id／current_answer_id／current_feedback_id／pending_key 可空 UUID；scope_revision int；source_snapshot_sha256；created_at／updated_at timestamptz。投影不是回答或模型正文。所有指针同活动／对应 kind，goal与scope匹配；需要 deferred FK 时仅限该事务末核验，不跨事务留悬挂。
- interview_commands：PK(activity_id,business_key)；action 为B3九动作；request_body TEXT／request_sha256；semantic_slot hash；execution_kind∈local|model；context_body／context_sha256 仅 model 非空且受上限；operation_id model时 int10m.<business_key去连字符32hex>，local时 NULL，UNIQUE(activity_id,operation_id)；status∈accepted|started|committed|history|not_sent|failed|unknown|abandoned；launch_claimed bool；obsolete bool；effect_applied bool；duplicate_of／retry_of UUID可空且同活动；before_revision、after_revision可空、goal_version、scope_revision、result_record_ids UUID数组≤2、error_code可空受限字符串≤64、created_at／updated_at。原 request/context/hash/action／绑定身份不可更改；obsolete 只可 false→true；一次 launch_claimed 只可 false→true。terminal effect／record IDs／after_revision 不可重写；status/诊断仅按B4的单向转换。
- interview_records：PK(activity_id,record_id)，UNIQUE(activity_id,seq)，UNIQUE(activity_id,business_key,ordinal)；seq 1..4096、ordinal0..1、kind∈start|goal|scope|question|answer|probe|feedback|finish|abandon；origin∈application|user|model；goal_version、scope_revision、round_index、probe_depth、answer_version可空；parent_ids UUID数组≤12；question_record_id、supersedes_record_id可空；source_refs JSONB≤10、body_sha256；local_body TEXT 与 model operation_id／payload_sha256 二选一；created_at。本地规范body≤32768字节；model body始终 NULL，只以007 FK与 hash引用正文。父记录 seq 必须更小、同活动且身份相符，禁止环；answer 的(parent question,version)唯一、supersedes严格前版本。整行不可UPDATE／DELETE，不提供清理器。

LocalBody统一schema='interview.local.v1'，共通字段activity_id/business_key/kind/goal_version/scope_revision/round_index/probe_depth/parent_ids/value须与行一致。value：start={goal_provided:bool}；goal={goal:GoalBody,copied_from_goal_id:UUID|null}；scope={before_sources,after_sources,before_roles,after_roles}；answer={question_record_id,answer_version,text,supersedes_record_id:UUID|null}；finish={reason:'user_end'}；abandon={pending_key}；应用question/feedback使用B6同类value。start/scope/finish/abandon及应用问题/反馈origin=application，goal/answer=用户显式确认；model的question/probe/feedback只引用007。parent_ids只表达同goal/scope的语义依赖：question引用当前goal及可选前feedback，probe/feedback引用当前question/answer，answer引用父question；supersedes与copied_from是历史来源，不进入依赖遍历。绑定新scope的新goal只依赖本次scope事件，避免复制旧goal的失效依赖。本地finish/abandon只记录关闭，可沿旧来源身份留历史，无当前证据资格要求；其他新增事实仍按B3核验。

011 增加不可变触发器、head／command单向约束、父绑定检查、hash／字节约束及必要索引：commands operation／pending／slot，records seq／question-answer-version／父引用GIN。live slot 唯一索引只作用于 duplicate_of IS NULL 且 status∈accepted|started|unknown|committed|history；失败／确定未发送不继续占 live slot，但原命令和预算保留。PK/FK、同活动、模型引用007入库身份、计数限额必须由数据库约束／受保护触发器与短事务同时保证，不能只靠客户端。

模型 success 若要产生 question／probe／feedback：在原 record_outcome 的同一事务写 received 与007、插入一条引用正文的 interview_record、将命令置 committed/effect_applied=true、CAS head revision+1／last_seq+1／清pending。任何一步失败全回滚；随后只按旧终态及UNKNOWN合同处置，不允许“007已成功，后补领域事实”。model record的body_sha256=payload_sha256，指007完整规范封套hash；解析得到value不另冒充正文hash，parent_ref沿封套hash核验后才提取必要正文。本地start可写start+goal，有目标的bind_scope写scope+重新绑定goal，其余最多单条本地事实。每个effect只增加一次head revision；accept／launch／诊断不增加head，pending/status纳入view_token。

S1按011全部对象、列、约束、触发器与受保护函数的批准定义比对 ready／absent／damaged；精确指纹由实施卡冻结，不用表存在就算 ready。新增对象缺失／部分安装／异常形状时面试读写503 interview_schema_not_ready。遗留库无011且无面试残留仍允许旧功能；只要有 int10m、007 profile interview.v1 或领域残留，就禁止按普通结果展示或消费，不能靠schema缺失降级授权。

### B3 九动作、body与状态转换

九个 action 固定为 start、goal、ask、answer、correct_answer、review、bind_scope、abandon、finish。GET恢复／查询、现有取消、资料上传不新增面试动作。状态缺goal＝needs_goal；有效goal无当前问题＝ready；当前问题未保存答＝question_ready；已保存答待review＝answer_ready；完整反馈＝feedback_ready；结束＝ended。pending_key 非空是独立“处理中／未确认”覆盖，不把问题阶段改成另一个聊天状态。

- start 本地：body={goal:GoalBody|null}。只接受无领域head、无任何activity_operation、status=pending／generation=0／无executor或lease、requests_reserved=cost_reserved_microunits=tools_reserved=running_reserved_seconds=running_settled_seconds=0且未选记忆的新活动；沿create_activity:499的实际初始事实核验，不仅检查“没有成功调用”。expected_head_revision=0、expected_goal_version=0，scope与创建事实一致，来源1..10有效。创建head revision1及start，goal非空再写goal v1进入ready；空goal为v0／needs_goal。已有教学head或学习记录不转域。不同键争start只有一个head，精确同槽可回无effect别名。
- goal 本地：body={goal:GoalBody}。未ended且活动可写；v+1并写goal，重置当前问题／答／反馈与轮次指针为ready，旧模型命令及其依赖 obsolete=true；pending原意图失效，不删旧事实。缺目标时只允许本动作补齐。不能以goal改模型身份或额度。
- ask 条件本地／模型：body={mode:'first'|'next',parent_feedback_id:UUID|null,retry_of:UUID|null}。first只在ready且无当前round；next只在feedback_ready并精确引用当前完整feedback。成功产生question，round+1、probe_depth=0，phase=question_ready。材料找不到可定位片段时由应用产生一个说明具体缺口的 clarification question（origin application、无SUP／额度），context不假装有证据；有片段则一次model。含混目标允许模型输出clarification question，但不得生成实际候选材料以外的“已确定身份”。
- answer 本地：body={question_record_id:UUID,text:string}。question_ready且精确当前question/probe；写该问题answer v1，phase=answer_ready，清当前feedback。用户输入不是模型或教学成绩。对同一问题已保存答再写不同正文须correct_answer，不悄然覆盖。
- correct_answer 本地：body={answer_record_id:UUID,expected_answer_version:int,text:string}。允许当前goal／scope内未ended的历史或当前回答，目标版本/hash可核对且不存在更高答版本；写version+1及supersedes，不修改旧行。对父图求有界后继，将依赖旧答的所有模型命令及pending置obsolete，保留其历史；head回到该问题的新答／answer_ready，清其后问题／反馈指针，round/probe回到该问题坐标。模型问题本身若已因其他祖先失效则拒绝，先goal／bind_scope。持久图≤4096记录，锁内不递归执行业务／模型。
- review 条件本地／模型：body={question_record_id:UUID,answer_record_id:UUID,retry_of:UUID|null}。answer_ready且两个ID是当前问题和最高答版本；目标、范围、祖先链和引用均合格。若上次问题为应用生成且仍无可定位材料，应用写feedback，具体指出自报／缺材料，只认可已说明的片段；否则一次model。probe结果→写probe，probe_depth+1、question_ready、等待用户回答；feedback结果→写feedback、feedback_ready。达到 max_followups_per_round 时只接受feedback；模型返回probe属于 invalid_interview_output，不自动改写成“通过”。
- bind_scope 本地：body={sources:[SourceBinding],material_roles:[SourceRole]}，只接受显式确认的当前资料版本。原scope即便失效可在活动未取消／未过期时以旧expected_scope_revision和新有效范围替换，锁内同时更新公共scope／head／scope事件、obsolete所有旧模型命令，清问题／答／反馈和round/probe指针至ready或needs_goal。有目标时保留target/focus/clarifications正文，按新用途映射写新goal记录、goal_version+1并与新scope绑定（本动作scope+goal两条、head只+1）；无目标只写scope、goal_version仍0。即使源集合未改，仅用途改变也写新scope事件并在此面试事务让scope_revision+1，避免评价沿旧用途继续合格。来源与用途完全相同回no-effect。容量或goal_version已达限则整笔拒绝，不半改scope。不能先调用公开scope再补head。
- abandon 本地：body={pending_key:UUID}。只对精确pending的accepted／started／unknown；写abandon，标原命令abandoned/obsolete，清pending，恢复原问题阶段。不改007、operation、预留或停止证明。若原窗口仍不能释放，后续model照旧拒绝；abandon不是未知重发授权，也不是取消远端。
- finish 本地：body={}。无pending时从任一未ended阶段写finish、phase=ended；可以有未回答的问题，不编完整反馈。已取消／过期且无pending也允许单纯结束领域、保留本地事实，不能使任何旧模型正文恢复资格。结束后九动作写均拒绝；同key已完成回执仍可核对。若pending应先查原结果、现有取消或abandon，finish不能偷偷清pending。

除goal／correct_answer／bind_scope为有意识的修正、abandon处理pending外，pending拒绝其他新动作。正常本地写不耗模型／工具／费用，但仍受活动截止、取消与存储上限；无模型配置不阻止合格的本地goal／answer／correct_answer及只读。目标／范围更新对原窗口不发新SUP；尚未mark的旧准入禁止发送，已mark的远端不能撤销，迟到只按UNKNOWN保留预留。finish／abandon的关闭语义不绕过存储限额。

### B4 同键、同槽、launch与未知

semantic_slot 对规范{activity_id,action,expected_head_revision,goal_version,scope_revision,round_index,question_record_id,answer_record_id,target_record_id}计算；无关字段为null，父ID由权威记录核对后确定。start用head0，goal／scope／finish等以当前头为语义坐标。slot定位先于CAS，用来解释同一旧意图，不能把新修订自动改进原请求。

锁内先查同business_key：request hash与正文都相同则返回原回执，即使已失效也只报告资格，不新增effect。不同正文/hash则409 interview_key_conflict。若是accepted且launch_claimed=false，用户显式重发原POST可以继续唯一launch claim；GET永不执行。started／unknown／terminal的原POST只回回执，不再次run_one_call。

不同key同slot、完整request hash/body相同：保存 duplicate_of 指向winner的别名回执、effect_applied=false，不新record／admit／launch／预算。规范hash排除key但保留原三修订；不能把新head修订的请求伪装成旧槽同文。不同正文同slot为409 interview_slot_conflict，尤其pending／unknown不转成第二次调用。别名查询跟随原状态且禁止自己launch。

retry_of 仅ask／review支持，须指向同活动同语义父的确切 not_sent，或 received但结构不合格而failed且无领域effect的终态；旧未确认/UNKNOWN不支持。新key、新hash、明确用户动作、当前三修订及父资格、原窗口已有合格停止／结算才可重新接受；仍消耗本次新的准入额度，旧次数／费用／时间不退。恢复未确认后改key、换slot或goal来绕过UNKNOWN的行为由原生window gate阻止。其他类型／已产领域effect的命令拒绝retry_of。

model命令：accepted（冻结已保存）→started（一次launch_claimed），然后committed；后续被新的正常轮次替代展示可标history。确定未发送→not_sent；已收到但输出拒绝／终态已明确→failed；无法确认→unknown；显式放弃→abandoned。过时committed/history仅置obsolete，不倒退终态或抹record。local命令在一个事务直接committed；别名回执不自行effect。启动领取先锁及复核、置claim一次，再离开事务进入原SUP。跨中断status=started且无最终见证不因重开服务变成not_sent或清claim。

是否 definitely_not_admitted 只取原生监督的明确状态及持久receipt缺失，沿现有教学链的有限判定，不从HTTP断开、客户端超时、空stdout或模型错误文本推定。停止、运行秒数与窗口可重入的权威仍为原worker/manager/ledger。没有停止证明不退款；未知不重发；COMMIT响应丢失只以原key和持久结果核对。

### B5 锁序、CAS、原子提交与竞态窗口

所有面试写、claim、admit／mark／outcome的新增分支使用同一锁序 L-I：先读取定位hint；调用 _memory_lock_prefix(connection,activity_id,extra_sources=旧新范围及必要记录来源)，由它按UUID升序锁来源、记忆头、相关活动并复核hint；接着按operation_id排序锁该活动所有operation；再锁interview_head；最后按business_key排序锁所需interview_commands；插入immutable records并CAS更新head。没有锁后再补来源／记忆，也不把head放在operation前。G8真实_teaching_lock已有operation→head次序，L-I与其兼容；共享活动行互斥保证一个活动只有一个业务域，跨域guard无需逆序锁另一个领域head。

本地effect提交点 L-C：同键／槽核对→三修订CAS→活动／来源／记忆／父资格（关闭事件例外见B2）→存储容量→immutable本地记录→必要命令失效投影→head UPDATE WHERE revision=r／command committed→一个COMMIT。effect=false不增head，错误整笔回滚。绑定scope提取_apply_scope_locked(connection,activity_id,activity_row,locked_sources,expected_scope_revision,sources,force_revision=False)同连接helper；原公开入口保持force_revision=false，bind_scope仅用途改变时在同事务设true递增scope。面试域的原公开revise_scope拒绝并提示bind_scope，避免双写；获取_memory_lock_prefix后不能调用另开事务的公开方法。start先在同活动锁下插入命令和local records再建head；seq按既存record最大序号+1分配，最终head.last_seq等于最大seq。已有head新record插入后再更新投影；pending/诊断同revision只允许其非事实指针变化，effect必须精确+1，不允许头降版。

模型接受 L-A：事务外只读冻结／组装，先纯校验完整OneCallInput容量；锁内重算冻结身份／context hash并核三修订、scope、goal、父版本／hash、来源定位、未选记忆、budget和无pending。插入accepted、设置pending，不增head revision；同槽／别名在此归一。launch claim L-L重新走L-I并复核所有身份、accepted与claim=false；置started/claim=true后才run_one_call。不存在“GET恢复自动claim”。

原生准入 L-N：admit在现有memory前缀及operation锁之后接_locked_interview_binding；再次验证当前head revision／goal／scope／pending key、命令started／claim／未obsolete、request/context/prompt hash、provider/model/预算，并拒绝混合profile／工具。实际admit一次写四账reserve及operation；mark_dispatch_started在原同锁事务再核同一binding，关门／取消／源变／修正均不能越过发送边界。

成功 L-R：record_outcome原严格_terminal_confirmation优先。同一terminal三元组＋正文完全等值时新增_interview_confirm_integrity检查领域引用也完整，然后只返回原RECORDED，不修复或补写；异文／旧无正文保留拒绝。新正文只有原_operation_is_current、dispatch_closed=false以及interview binding仍当前时才允许；_write_outcome及_write_interview_outcome同事务完成007、record、command和head。新增hook必须在COMMIT前执行；向UI回传body只从提交后合格GET读取，不使用worker返回内存文本。

修正／取消与L-N、mark、L-R共用活动与operation锁。修正先提交，旧admit/mark/结果正文拒绝；mark先提交，则不能假称撤出站，修正使旧命令obsolete，旧结果仅走无正文UNKNOWN。L-R先提交成功，则修正事务保留记录再抑制当前资格，不能删除已提交正文。准确三窗口在D中用真实PG屏障核验，不能只测一般“取消中”。现有cancel_activity继续控制活动／dispatch关闭，面试读取叠加cancel覆盖；不新增面试取消账本。

只读 L-V：workspace、history、record、command回执的身份／资格／正文投影使用单条SQL的同一statement snapshot；不能先读资格，再独立取007正文。eligible predicate同时要求007原绑定／scope／来源／活动资格、011 ready、领域model command与record完整/hash吻合、未obsolete／未abandoned、相应goal/scope/父答版本与当前采用版本可核对、无记忆选择且记忆资格可靠。父图版本更改通过L-C原子标后继命令obsolete，不以模型summary代替。已结束phase不单独抑制原来合格的历史；取消、失效或旧goal／旧answer的模型正文抑制。

同一predicate接入通用read_committed_result、list_committed_results、operation/list及任何结果正文消费。跨profile input_result、learning seed、teaching seed与通用continue/tool不能消费int10m，也不能把缺失011或伪造payload.profile当普通结果。保留metadata、hash、旧版本和suppression reason，本地用户输入历史可读；不在invalid分支返回全文、引用片段或隐藏的缓存body。

引用在资格快照取得catalog后校验原文位置，并在返回前用新的资格语句复核同activity/record/citation/view及片段身份；其授权截止是这条最后语句的snapshot。来源在该语句前更换必须拒绝旧片段；语句后才更换可能已有响应在途，不能承诺撤回网络字节。前端对已获知的失效、owner／活动／panel/view切换拒收晚结果，后续GET统一抑制；这种截止不升级成尚未验证的全网络时序保证。

### B6 受信profile、上下文、输出与配置门

ModelCallRequest新增 interview_profile:InterviewProfile|None=None；三种profile最多一个。interview须JSON_OBJECT、allowed_tools为空、input_result=None、恰好两条消息（固定system＋规范frozen context user）。InterviewProfile.schema='interview.v1'，字段为activity_id／business_key／action(ask|review)、request_sha256／context_sha256、expected_head_revision／goal_version／scope_revision、round_index／probe_depth、goal_record_id／question_record_id／answer_record_id、prompt_version='interview.prompt.v1'。身份来自冻结及DB，不由公开命令直接提供；AdmissionIntent尾部新增 interview_binding=None，保留旧默认序列化与位置参数兼容。

gateway.call在原学习／教学分支旁增加受信validate_interview_request：operation前缀int10m与profile双向匹配；消息与保存context逐字／hash一致；模型身份和各种限额匹配；调用ledger validate后才admit。不带profile的int10m、带profile的其他前缀、混合profile、任意工具、Generic input_result一律拒绝。_parse_success在原JSON分支新增strict parse／normalize；completion_tokens越配置上限、截断、tool_calls、未知键／权威字段、引用越界／实际答片段不符或分支不合格导致invalid_interview_output，保留真实终态／计费，不写领域fact，不自纠重调模型。

AskOutput={type:'question',purpose:'interview'|'clarification',reason:'topic'|'ambiguous_target'|'missing_material'|'missing_claim_evidence',text,reference_ids}；text1..2048字符且≤8192字节，refs≤6且须属于冻结catalog，澄清允许无refs并明确不确定。goal缺失不会发模型。review为ProbeOutput或FeedbackOutput：probe含type='probe'、reason∈ambiguous_answer|missing_claim_evidence|conflicting_sources、text、recognitions≤8、gaps≤8、reference_ids≤6；feedback含type='feedback'、summary≤1024字符、recognitions≤8、gaps≤8、conflicts≤4、next_steps≤4。各项目正文≤512字符、引用≤6、总输出≤32768字节；未知字段拒绝，不允许score、mastery、budget、authority、catalog、目标／版本覆盖或业绩验证字段。

RecognitionInput={answer_record_id,start_offset,end_offset,answer_excerpt,reference_ids,semantic_support:'supports'|'unclear',explanation}。偏移为Unicode标量索引（前后端一致，不能混JS UTF-16单位），片段非空且严格等于冻结答案切片；gaps包含对应answer_record_id、具体缺口／补充问题及引用，conflict至少两个不同且合格引用。模型不得输出 position_verified／verification_kind。应用附加这些字段，resume／experience／measurement／unspecified和无支持引用的认可统一verification_kind=user_statement及固定文案；仅reference角色定位有效且模型明确语义supports时可标source_interpretation，始终是对照建议。semantic_support='unclear'不能进入“有依据的部分”。局部正确和缺项可同时存在，不强制整答单一对错。

stored_interview_result由应用形成标准封套：profile='interview.v1'、activity/key/action、goal/head/scope身份、prompt/context/request hash、source refs/catalog及规范value；模型只提供value允许字段。记录model kind与value.type必须匹配，只有当前认可来源资格与模型语义建议分别成立才投影相应文案。应用clarification/feedback使用相同用户显示结构但origin=application，没有假operation或虚构token／账本调用。

新增公开层 interview_local_layer 与 interview_model_layer；read层由local_session及S1决定，不要求模型密钥。ActivityConfig尾部可选字段保留旧默认，缺配置时model层不可用但原create／continue／learning／teaching／memory各层独立。新增私有配置section interview（本卡不读取或修改私有配置）：profile严格'interview.v1'，max_output_tokens严格int1..2048，max_followups_per_round严格int1..4；未知键拒绝。缺省section=interview_not_configured，输出0、无fallback；格式错误=interview_config_invalid；原L1／L2不可用则interview_model_unavailable。令牌不超过既有activity/service配置，模型/provider只能沿活动实际绑定，价格与账本预留完全沿原配置。

公开例子拟加interview={profile:'interview.v1',max_output_tokens:0,max_followups_per_round:2}：0明确是无效禁用占位，读取产生interview_config_invalid，必须在未来获准配置中改为合法正额度才开model。不提供真实端点／价格／密钥或免费额度；私有运行配置需要未来实施卡授权，重启加载而非假热更新。工具允许集合空，活动工具限额/已用仍显示但面试不使用。model仍要求原L2/SUP及finite W，降层不能换成普通聊天、mock provider或未配置出站。

### B7 公开读写、错误码及前端意图

新增路由都在/api/activities/{activity_id}/interview，调用现有activities.api._guard（local_session、allow_own_origin）；沿同一session、媒体类型、请求字节和Origin策略，不新增公网／cookie旁路。POST /commands 接InterviewCommandInput；GET /commands/{business_key}；GET /workspace；GET /history?limit=1..50&before_seq=N&view_token=T；GET /records/{record_id}；GET /records/{record_id}/citations/{citation_id}。citation_id为冻结catalog opaque ID，不接文件路径。history游标包含snapshot last_seq与view_token，变化409 interview_view_changed要求重新GET，不拼接不同快照正文。

workspace在未start的合格新活动返回head=null／domain='none'和能力，不写head；已有面试返回domain='interview'；其他业务domain显示不可转域原因。读DTO固定schema='interview.view.v1'，activity_id、domain、head(revision/goal_version/scope_revision/phase/round/probe/pointers/last_seq)、sources身份／资格、budget为原四账可公开事实、capabilities、pending、records、view_token、qualification/suppression_reason。view_token对规范head、source_snapshot／当前来源资格、记忆资格、pending status／claim／obsolete、记录投影资格及公开budget状态求hash，不含read_at。它不是授权或余额，只防拼读和迟到面板。

CommandReceipt固定schema='interview.receipt.v1'，activity_id／business_key／request_sha256／action／status／execution_kind／operation_id可空／duplicate_of／retry_of／effect_applied／before_revision／after_revision／goal_version／scope_revision／record_ids／qualification／suppression_reason／error_code／view_token。model接受后未终态返回202和receipt；已持久本地effect／明确终态／别名返回200。回执不夹带未提交模型body。错误结构{schema:'interview.error.v1',code,retryable,receipt:null|receipt,view_token:null|string}，不输出SQL、DSN、内部路径或provider原始响应。

错误映射封闭如下；原local_session认证失败继续原403，原媒体／字节错误沿原415／413，未知活动／key／record404 not_found，不改旧接口错误枚举。

- 422 interview_invalid_input：未知action/键、非法类型、父字段缺失、文本/深度/hash/偏移格式或体积；存储前拒绝。
- 409 interview_key_conflict／interview_slot_conflict／interview_head_conflict／interview_goal_conflict／interview_scope_conflict：分别异文同key、异文同slot及三修订CAS不符；retryable=false，GET核对后用户新意图。
- 409 interview_phase_conflict／interview_pending／interview_parent_invalid／interview_retry_forbidden／interview_record_limit／interview_version_limit／interview_view_changed：状态、父版本、未知重试、容量及游标边界。
- 409 interview_domain_conflict／interview_profile_required／interview_parent_forbidden：非全新域、普通调用或跨profile消费。只读metadata不因此起业务。
- 409 interview_memory_not_supported：确定已有记忆选择；interview_memory_dependency_invalid：现有记忆资格不可靠或失效；无清空、降级、替换或新call。
- 409 source_invalid／cancelled／activity_expired／budget_exhausted／window_unavailable：公开沿既有原因映射；expired/cancelled允许纯关闭的finish/abandon特例，其余新业务写拒绝。达限终态查询仍200。
- 503 interview_schema_not_ready／interview_not_configured／interview_config_invalid／interview_model_unavailable：持久或模型能力缺失；retryable=false，无自动重试。
- 持久命令diagnostic包括 invalid_interview_output、interview_context_too_large、interview_binding_invalid、launch_already_claimed、supervision_unknown。出站前context过大用422；已发送输出不合格或未确认以200/202 receipt明确failed/unknown返回，不用可重试5xx掩盖次数已耗。原窗口及存储连接瞬态故障如不能确定是否commit，只返回可核对key的未确认语义，不许可重发；原输入DSN错误不回显。

前端 interviewIntents 与 interviewDrafts 为独立namespace：localStorage摘要 retrolume.interview.intents.v1，IndexedDB retrolume-interview-drafts v1、store drafts；Web Locks使用retrolume.interview.intents.v1和draft-owner相应锁，保留现有teachingEditorOwner身份生成／owner防碰撞机制，复用该不含业务正文的身份函数，不能把教学intents存储拿来放面试。正文只在本机draft，摘要为key/activity/action/hash/expected三修订/owner/state，不放答案或简历。

首次及再提交前先获得owner、规范hash，将完整body/key/identity保存IndexedDB，再在锁内保存摘要，两个步骤成功才POST。不得先POST后补本机正文；存储不可用给可理解原因并禁止写，用户可复制草稿。刷新只读核对原key：原hash一致才更新intent；服务器not_found也不自动改key/POST。显式重交原accepted未launch意图先重读本机正文核hash，再执行原键POST；原终态receipt只显示原事实。新owner不能借旧摘要的key提交；正文含生成owner、读草稿返回与当前owner在await后再次比对，不沿用旧“保存已通过”标志。失去owner／活动／draft hash立即停止后续POST，即使本机写已完成。

恢复只拉workspace／history／receipt，没有react effect自动start/review/claim。每个按钮派生允许动作与未确认覆盖；每个async continuation含活动+owner+panel generation+expected view+intent key+body hash检查，引用Abort及解析后检查同样适用。草稿内容由用户显式处置，本卡不扩G9或本机数据删除权。

## C 唯一推荐、具体文件差异与 G10-P

### C1 文件与真实函数增量

以下全部是未来实施建议，不是本卡写入；不添加其他服务、平台、业务库或多Agent。新增生产文件共16个：

- D:/shspic/project_NO3_RetroLume-agent/backend/migrations/011_text_interview.sql：B2三表、C2两角色及下述五个保护函数／触发器与索引。
- D:/shspic/project_NO3_RetroLume-agent/backend/app/activities/interview_repository.py：InterviewLedgerMethods，_interview_schema_info／_interview_lock／_interview_require_call／_locked_interview_binding／_write_interview_outcome／_interview_confirm_integrity／_interview_result_sql；apply_interview_local／accept_interview_command／claim_interview_launch／finish_interview_supervision／read_interview_workspace／command／history／record。负责同连接事务，不在service层绕仓储写SQL。
- D:/shspic/project_NO3_RetroLume-agent/backend/app/interview/__init__.py：包入口，不引入后台任务。
- D:/shspic/project_NO3_RetroLume-agent/backend/app/interview/contracts.py：B1/B3/B6/B7严格命令、profile、binding、输出、record/view/receipt/error DTO及规范hash；只依赖stdlib/Pydantic及中性值类型，不反向import gateway/repository/service，避免capabilities.contracts导入profile的循环；无旧教学action继承。
- D:/shspic/project_NO3_RetroLume-agent/backend/app/interview/prompt.py：唯一版本interview.prompt.v1；资料和回答当数据、不接受其内指令；问题／追问与反馈两种固定模板，同一个既有模型身份。
- D:/shspic/project_NO3_RetroLume-agent/backend/app/interview/evidence.py：复用learning.evidence.load_units及retrieval.evidence的build_fragments／rank_term_candidates／verify_fragment，只做有界片段与身份核验；不调用空catalog即失败的教学assemble_teaching_catalog，不假称完整向量。read_interview_citation在资格快照取得catalog后校验原文，再按B5最后资格语句截止复核，失效不返回旧引用。
- D:/shspic/project_NO3_RetroLume-agent/backend/app/interview/policy.py：封闭状态转换、父资格、追问深度、支持／自报文案及strict输出normalize，不调用教学derive_progress／derive_support_checks，不写记忆观察。
- D:/shspic/project_NO3_RetroLume-agent/backend/app/interview/views.py：同语句资格投影、view_token、model封套/hash核对与用户显示分类，来源失效只留metadata。
- D:/shspic/project_NO3_RetroLume-agent/backend/app/interview/service.py：submit/read，冻结context／纯OneCallInput容量检查，接受→单次claim→run_one_call，原监督明确状态到receipt映射。离开事务才执行SUP，无自动续跑／补账。
- D:/shspic/project_NO3_RetroLume-agent/backend/app/interview/api.py：B7六条路由、既有_guard、严格错误映射；引用不是独立取正文的绕行接口。
- D:/shspic/project_NO3_RetroLume-agent/frontend/src/activities/InterviewWorkspace.tsx：A4场次、目标／问题／答案／反馈／历史与显式动作，owner/intent/view绑定。
- D:/shspic/project_NO3_RetroLume-agent/frontend/src/activities/InterviewCitations.tsx：按活动、record、citation及view代次加载，Abort及解析前后身份检查，抑制／旧引用文案。
- D:/shspic/project_NO3_RetroLume-agent/frontend/src/activities/interviewApi.ts：B7 DTO/路由/错误及Abort传递；不使用通用continue发面试动作。
- D:/shspic/project_NO3_RetroLume-agent/frontend/src/activities/interviewIntents.ts：独立摘要、draft store、锁、owner及恢复只读；复用现有teachingEditorOwner的身份原语，不改旧命名空间。
- D:/shspic/project_NO3_RetroLume-agent/frontend/src/activities/interviewDrafts.ts：规范hash和九动作构造，正文先存与三修订固定；偏移按Unicode标量。
- D:/shspic/project_NO3_RetroLume-agent/frontend/src/activities/interview-workspace.css：沿活动工作区样式，移动端同顺序，不引入UI库或原型运行时。

需修改既有生产文件共11个，范围如下：

- D:/shspic/project_NO3_RetroLume-agent/backend/app/activities/repository.py：PostgresAdmissionLedger新增InterviewLedgerMethods；revise_scope提取_apply_scope_locked同连接helper，旧调用行为保留，面试调用公共revise_scope拒绝；admit、admit_tool及mark入口加入domain/profile guard，_locked_operation对int10m先锁全operation；record_outcome加B5等值完整性／原子领域钩子；read_committed_result、list_committed_results、list_operations、read_operation的model投影及input_result消费加同一面试资格。read_activity_facts提供可选business_domain只读元数据(interview|existing|unknown)，按ready/absent/damaged可靠分类，不影响旧四账数值。没有011且无残留只用原分支；有面试残留资格未知则不降级。
- D:/shspic/project_NO3_RetroLume-agent/backend/app/activities/service.py：continue_from_result／execute_tool_action明确拒绝面试域及int10m父结果，scope写给出bind_scope路径；read/resume继续只读，cancel_activity仍原权威。
- D:/shspic/project_NO3_RetroLume-agent/backend/app/activities/api.py：沿现有序列化加入可选business_domain及面试能力摘要，接口没声明面试时不要求新的输入字段；面试实际写均在新router，原create／cancel／_guard协议保留。
- D:/shspic/project_NO3_RetroLume-agent/backend/app/activities/teaching_repository.py：_teaching_lock完成现有活动锁后以同连接只读domain guard拒绝interview head；教学local write也必须挡住，不能只在model服务挡。其事实／阶段／锁序／progress不改。域guard在head创建前核对，不逆序锁interview head。
- D:/shspic/project_NO3_RetroLume-agent/backend/app/learning/service.py：LearningService.execute前核domain，拒绝int10m parent或面试活动，保留已选记忆现有拒绝。学习冻结／prompt／normalizer不改。
- D:/shspic/project_NO3_RetroLume-agent/backend/app/capabilities/contracts.py：B6 optional interview_profile和AdmissionIntent尾部interview_binding，三profile互斥；旧请求未带该字段继续exclude_none，旧carrier输出字节不被追加null字段。
- D:/shspic/project_NO3_RetroLume-agent/backend/app/capabilities/gateway.py：ControlledModelGateway.call受信双向验证、AdmissionIntent绑定，_parse_success专用normalize，_finish仍取ledger提交确认，profile无工具；旧学习／教学分支不改正文结构。
- D:/shspic/project_NO3_RetroLume-agent/backend/app/service_config.py：ActivityConfig尾部默认字段、_InterviewInput、_interview_check、load_activity_config独立层；新profile纯dry-run容量，不出站，不扩L1/L2。local层取S1，与model配置分开。
- D:/shspic/project_NO3_RetroLume-agent/backend/app/main.py：挂interview router及已有materials/originals/ledger/session依赖，不启新worker或常驻队列。继续用既有同一SessionConfig。
- D:/shspic/project_NO3_RetroLume-agent/frontend/src/activities/ActivityWorkspace.tsx：新入口variant与business_domain识别；面试域仅挂InterviewWorkspace，隐藏旧教学／通用调用按钮；unknown资格只读提示。既有活动默认仍TeachingWorkspace，创建继续既有API与范围选择。
- D:/shspic/project_NO3_RetroLume-agent/frontend/src/main.tsx：“模拟面试”占位改为活动工作区面试variant，旧学习导航与已验布局保持。

另修改一个公开配置例子 D:/shspic/project_NO3_RetroLume-agent/config/activity.example.json，新增禁用interview section；缺失section仍拒绝model。总数16新增生产文件、11修改生产文件、1修改公开配置。建议定向验证源为D:/shspic/project_NO3_RetroLume-agent/backend/tests/test_interview_contracts.py、D:/shspic/project_NO3_RetroLume-agent/backend/tests/test_interview_postgres.py、D:/shspic/project_NO3_RetroLume-agent/backend/tests/test_interview_http.py；未来browser/fault runner及样本只写下一卡自己的evidence。建议测试源不计入生产16/11。

只读复用且不建议修改：001—010全部迁移；backend/app/worker/{one_call,launcher,session}.py；backend/app/memory全部；旧learning contracts／teaching service/policy/views/api；frontend TeachingWorkspace／teachingApi／teachingDrafts／teachingIntents正文；锁文件、旧证据、DocuS、公共库和原始需求。前述花括号为同目录三个具体原文件，不是新增目录。若实施发现必须改变这些受保护内容，应先记录具体影响并由编排核范围，不把兼容修复当开放改平台许可。

### C2 权威、最小权限、升级与退出代价

采用011只增加上述三表和两个NOLOGIN角色 retrolume_interview_owner、retrolume_interview_app。owner拥有新表／索引／五个保护函数，不能赋给HTTP/worker运行身份；app角色只作为既有普通运行账户的能力成员，不能有SUPERUSER／BYPASSRLS／建库建schema／owner成员／旧表新删除权。未来合成库用一个明确的普通runtime账户验证，迁移admin与runtime分离；真实用户账户授予不在本卡或G10-P默认授权内。

五个新函数固定为 public.interview_record_insert_guard()、interview_record_immutable_guard()、interview_command_guard()、interview_head_guard()（四个trigger函数），以及 public.interview_result_eligible(uuid,text)（只读领域predicate）。拥有者、SECURITY DEFINER、固定search_path及完全限定对象名纳入S1指纹，撤销PUBLIC执行；trigger函数不向app开放直接EXECUTE，只读predicate仅授予app。owner仅获需要的旧activities、scope、material_sources、operations、007及已有领域／记忆资格依赖SELECT／既有资格函数EXECUTE，不写旧事实、四账或007。只读predicate核领域与007绑定，_interview_result_sql再与原007和_memory_sql_guard交集，不由新函数重定G9资格。start guard对可选记忆依赖采用同一ready/可靠legacy/damaged分类：缺失只在无v2/M6残留且可靠确认无选择时可行，损坏拒绝。

app新权限：三表SELECT；commands INSERT与仅status／claim／obsolete／effect／after_revision／record IDs／诊断列UPDATE，受trigger单向限制；heads INSERT与规定投影列UPDATE，受CAS／指针binding和revision规则限制；records INSERT，由insert guard核model引用、父顺序、seq/kind/goal/scope/版本/hash/限额，无UPDATE/DELETE。任何表DELETE、TRUNCATE、ALTER、触发器禁用、owner SET ROLE均不授予。record/model插入必须引用同活动、同operation、007 hash/绑定和受信命令，不能指向别的profile。领域head只对全新活动启动，数据库start guard与同连接仓储双重核对旧域／原操作及窗口未开始。

应用／领域仓储管目标与回答版本、幂等、投影；原ledger独占准入／发送／四账／007终态；worker/manager独占原生停止事实；provider输出不拥有任何一项。这些权限服务于同进程受信代码，不把public command暴露成数据库自由写接口或新的SQL工具。

数据升级：011只在既有001—010批准基线上新增，不重写旧body/hash，不回填旧学习／教学／记忆为面试；旧活动默认domain existing。未来卡在fresh与旧非空合成库验证S1／不可变约束／新权限，不连用户DSN。未部署011且无面试残留，旧能力沿原资格可用；011损坏时不显示面试正文，不能可靠分类的活动business_domain=unknown、新写失败关闭，原四账metadata可读；已有旧域可可靠证明且无面试残留时只保持其原资格，不宣称任意损坏不影响全部旧功能。缺面试配置只关闭面试model，旧学习／教学配置层仍独立。

退出代价明确：尚无任何interview head/command/record、int10m operation、007 interview.v1及外部依赖时，可在明确授权下先撤app权限／路由，再仅删除011新命名对象和两个新角色，保留所有旧对象／事实；不能只检查三表为空便删角色。已有任何面试事实时禁止自动逆迁移／删除：关闭新写、保留只读资格及本地答案，采用前向修复；需要导出／迁移／清理则另走原数据退出授权。还原旧应用而保留面试007会缺消费guard，因此不能作为可发布回滚；先部署兼容的拒绝guard或保持新reader，禁止普通profile读出残留面试正文。

### C3 唯一 G10-P 采用包及未决项

推荐由编排将下列内容作为一个具体G10-P包核证并提交采用决定：三表／011／五保护函数／两NOLOGIN角色与最小运行能力，九动作公开写及六条读写路由，interview.v1受信carrier／无工具同模型接线，首版全新且无记忆选择的明确边界，目标／答／范围修正与严格失效历史，独立前端意图／引用／工作区，以及独立配置层。对应用户价值是有据、能纠正并恢复的文字面试完整闭环；代价是新增持久及公开语义、原ledger增加同事务hook和消费隔离，须在下一完整卡定向核验。

这个包是真实主要模型／公开写／受信profile增量，不能从G9-P或本卡设计许可推导已经批准。采用前本稿仍是建议。包不包含用户库迁移、真实简历／数据、真实provider条款／账户／付费、安装、联网招聘、自动发送、生产发布、工具权限、数据清理或Git写。已批准FR-011/012和路线是需求依据，未另造一次需求批准；G10-P只核新实现边界。

普通字段、命名、布局、九动作、无默认额度、追问上限／版本界限、兼容与测试层已在本稿作唯一裁决，无需逐项问用户。没有阻塞设计的关键方向缺口；唯一待决定是是否采用这个完整G10-P包及未来实施卡的有限资源／授权。编排负责正式DocuS、状态、TASK/R/CHG/DEF同步与验收，本窗口不自签采用、不改正式文档、不新建／发送下一卡。

## D 下一完整实施卡、定向矩阵与手工轨迹

### D1 一张完整实施卡的建议顺序和资源

建议编排在G10-P采用后出一张完整实现／接线／定向验证／卡内修复／收尾卡，路线预留TASK-106/R-100仍只是建议，不在此派发。顺序：冻结本合同及代表性合成样本→011/权限与领域仓储→profile/原子hook/公开消费隔离/配置→HTTP和完整工作区／本机意图→受控模型与真实PG异常窗口／浏览器→修复全部卡内问题→稳定候选一次相关风险独立审计→必要增量修复验证→停止并保留证据。不要按表／接口／页面拆成重复批准卡。

建议未来新许可主动21600秒、metadata1200秒；定向root runner最多8个，PG合成库最多3个、owned容器最多3个，native SUP／本地合成transport调用最多32次，HTTP runner最多2个、browser最多2个、frontend build最多2次、定向test runner最多3次、compile最多1次、install／真实provider／用户库／Git写为0。root是固定目标及子入口上限的验证runner启动，SUP/browser/build等为其分类计数，不重复相加充当旧累计。32次建议分配正常及质量联合链8、幂等/丢响应3、修正/取消准确窗口4、输出/原子/carrier5、跨旧功能2、未知及明确再尝试5、范围/历史恢复3、必要修复预留2；别名、本地及纯读负例0 SUP。通过后不补跑以用满次数；超范围带证据/缺口让编排调整新卡，不借45次或103余额。

模型替身只位于最底层transport，回传冻结的OpenAI兼容原始响应与真实usage，不能mock ledger、SQL资格、profile授权、Job停止或领域提交。HTTP连接真实合成PG及真实新router；browser访问此次最终build及真实HTTP，不展示手拼成功页。SUP仅在旧批准单机恢复范围内，显式保留SessionConfig约束；建议合成W=20秒、request=2、grace=2、manager overhead=30／总50、lease=20、recovery=False，以实际校验后可用参数冻结。旧平台未改证据继承；只补新增profile穿过OneCallInput协议、原生生命周期和消费guard的实际链，不重跑整个launcher／Windows／G3—G9全套。

下一卡在自己的evidence下保存样本hash、许可起点／截止、精确或保守投入、每runner/子入口台账、失败/no-op/unknown、SQL前后快照、原始HTTP、browser截图/网络/意图状态、最终build身份和owned资源停止证明。合成资源新建且可归属，103旧停止／保留资源只引用、不启动；不清用户库／旧证据。只收尾自己创建的容器／进程，删除若必要须精确核目标和授权，不随意广扫端口／杀旧进程。

稳定后的一次独立审计关注新profile真实性、native ledger同事务、未知／晚结果／修正窗口、旧调用消费隔离、普通DB权限、async owner及引用晚交付，不替代implementation测试，不全盘重审旧观察。若审计发现影响本卡行为的P1，原业务窗集中修复并由独立窗只作增量复核。

### D2 验收矩阵：全部为未来验证，当前运行0

每项必须保存可观察事实；模型建议文字质量按冻结参考与人可核查依据判，不接受“模型说通过”。技术样本T建议用事务隔离／丢更新与给定小事务轨迹及来源行；不同方向H建议用展览策划／史料判断，有日期不详与两份冲突说明。两类均为人工合成且明确虚构身份，不固定产品学科或岗位；文本、位置、expected输出和hash在实施卡才冻结。本稿不调用模型或预建可运行fixture。

- V01 正常闭环／题数：真实HTTP+PG+一次browser，T与H各一链start→goal/ask→answer→review→显式next→finish；观察immutable版本、phase／head／007/领域同提交、预算真实变化，无自动下一题／调用；用户可第一轮结束或继续，不预置题数。
- V02 必要probe／局部认可：合成transport经真实SUP/ledger送“概念已说明、测量依据缺失”的probe，认可锚实际片段，下一答／review得到feedback；可观察probe深度、父版本、每个显式动作一次准入。到配置深度再返回probe必须failed且无新domain fact，不自动回调。
- V03 目标缺失／同名：start(goal=null)不发模型；goal补齐后用Spring多义片段的明确clarification question询问真实候选；回答/goal修订再继续。记录实际澄清文字、版本和0/1调用，不能只测“有问号”。
- V04 缺资料／证据：资料ready但无匹配片段，ask/application clarification及review/application feedback，模型/SUP/四账增量0；提示实际所缺范围或证据，补资料bind_scope后真实ask可行，无假引用。
- V05 支持与自报：T可核查部分得到资料对照建议、其他遗漏列缺口；合成CV自报“快60%”只显示应用固定自报认可，并追问基线/口径/样本，禁止升级业绩事实；检查原答案片段和可点击引用及正常type，不靠模型自评。
- V06 冲突：H两份冲突史料，review并列两个身份及不确定，不能择一制造定论；真实引用加载回原页/行/offset，反馈语义与材料逐项核对。
- V07 引用／输出身份：真实normalizer+PG+HTTP，伪source/version/revision/hash、越界片段、UTF-16误偏移、非实际答案片段、自己添加position_verified/score/mastery及tool_calls均拒绝；invalid output没有domain effect，received失败诊断及已耗预算仍可核查。
- V08 同key并发：真实PG连接屏障＋真实submit、不同connection同body同key仅一command、一effect、一007及一次admit；异body同key409且旧正文/hash不变，不mockSQL字符串。
- V09 同slot异key：两个不同key同规范hash同时POST，唯一winner和duplicate_of/effect=false，无第二launch或费用；异body同slot409。检查partial unique index、三修订和持久别名，不能只测服务内字典。
- V10 丢响应／读恢复：真实COMMIT后切断一次HTTP回传，原key GET找到receipt/record；重发同key不多admit，浏览器刷新只GET且sup计数不变。accepted未claim丢响应只有显式原POST能领取，started/unknown不领取。
- V11 修正准确窗口：真实PG屏障分别在接受冻结后未admit、admit后未mark、mark后未result提交；goal或correct_answer先提交，前两者旧请求不出站，第三者只UNKNOWN无007/body/domain effect，预留不退；L-R先提交后修正保留immutable历史且抑制旧评价。每窗口记录时间序、operation/head/command/007事实。
- V12 历史答纠正：当前goal内早期answer v1→v2，原回答仍可读；有界后继obsolete、新head回正确问题、旧反馈／后续题body抑制，新review仅用v2。跨goal/已失效祖先/过期／结束纠正拒绝，不能只更新UI文字。
- V13 来源替换／显式范围：真实material source新版本使旧snapshot失效；workspace/record/history/citation/generic007读一致抑制，目标／本地答保留；仅bind_scope新版本能够继续，旧新源锁并集及scope/head事件一次commit，没有自动采用。
- V14 记忆消费边界：真实已选G9记忆活动start/ask拒绝interview_memory_not_supported；依赖失效／schema损坏按既有真实资格拒绝。伪通用profile、强塞v2引用/记忆正文不得出站；选择及010/教学进度字节不变。无选择可靠legacy库按边界可用，不把失效记忆换成无背景。
- V15 取消／过期／四账达限：真实取消与mark屏障、耗尽各已有账限，model停止新写；未知预留、原出站次数/费用、停止秒数不重置，GET纯读；无pending可finish、pending可显式abandon但没有退款或原窗口绕行。
- V16 未确认／安全再尝试：断底层transport/监督响应形成unknown；新key/retry_of及刷新不出第二SUP。只有明确not_sent或无领域effect的received-invalid且旧窗口已合格结算，显式retry_of新key才多一次准入；原历史/预算不改。
- V17 原子与严格重复终态：真实PG在_write_interview_outcome中触发故障，007/received/head/record整笔回滚；等值terminal只读确认，异文／无正文补写／缺领域引用拒绝，不补写旧received。FAULT注入保持ledger／DB实际函数，不用mock commit。
- V18 异常schema／升级／权限：三合成库分别fresh、旧非空、损坏/降级克隆；011不改旧007/009/010/hash，普通runtime不能UPDATE/DELETE records或旧不可变事实、TRUNCATE/SET ROLE owner；缺/损坏011不能普通展示int10m/007 interview.v1。S1不能仅返回table exists。
- V19 跨profile与跨活动：真实gateway/ledger/HTTP，普通continue/tool/learning/teaching seed消费int10m、面试活动建教学head、错activity父/007hash/nonce／混合profile均拒绝；非面试旧合成学习/教学各一个已有基线样本仍走原资格，四账没有面试旁路。这是受影响接口小样本，不重跑G7/G8/G9所有验收。
- V20 配置层／容量：纯严格contract/config核对与真实HTTP，无section／非法bool令牌／不同model／限额超服务／超完整OneCallInput分别拒绝；本地答与旧学习层保留。模型配置无免费fallback，工具集合空、协议3旧request exclude_none hash不变，新carrier完整往返至nativeworker。
- V21 本机先存／原key：真实browser＋HTTP／PG，阻止IndexedDB/摘要锁/owner时0 POST；故障在body先存后summary前、summary后POST响应前，刷新仅GET／原key；摘要无正文，原hash不符不允许原键重交；默认owner碰撞保护仍在。
- V22 精确身份续处理／晚面板：browser屏障在draft读取、保存、原owner复核及POST前；切activity/owner后所有await continuation停止POST或投影。本机保存成功不等于仍有旧发送资格；新面板后尝试交付旧问题/feedback/引用，解析前及解析后各一支均不复活；保存真实网络和面板结果。
- V23 恢复／快照：关闭并重开同场次，workspace/history/receipt当前头与版本一致，budget不清零，GET0业务写；history游标view变409，资格与body同SQL快照。源更换并发引用在最后资格语句前／后分支分别核验：前者无旧片段，后者如在途只按已知panel/view失效拒收，并保留真实截止证据，不宣称网络撤回；无跨场次缓存。
- V24 有限存储／结束／收尾：容量边界拒绝额外record/command/goal/answer version，finish无pending才结束且不编完整评价；ended只读历史、下一场次独立确认。最终build/hash/HTTP载入同身份，owned进程/容器停止见证及没有pending新runner，旧资源不启不删；汇报所有FAIL／unknown和未验范围。

矩阵使用真实函数对象：新增InterviewService/InterviewLedgerMethods/routes/policy，现有ControlledModelGateway、PostgresAdmissionLedger的admit/mark/record/read与run_one_call。UI不mock服务器domain/receipt/body；SQL不靠字符串断言。V11、V17、V22是新增高风险窗口，不能用先前G9证据冒充；未改Job停止、旧记忆身份/清理、旧教学质量及平台证据直接引用原件，不重测。

### D3 五条方案级手工轨迹（不是运行证据）

T01 正常概念链：新activity范围s1/v1 → start(goal“解释给定事务的丢更新”)写start+goal，head1/g1/ready → ask keyK1接受pending但head不增，成功007+question后head2 → answer keyK2/v1 head3 → review K3的feedback引用来源第3—5行及实际答片段，head4/feedback_ready → 用户ask(next) K4 head5／新轮 → 用户finish K5 head6/ended。本地K2/K5无SUP；三次模型动作最多三admit，GET不增加任何账。

T02 缺证与认可边界：用户在明确合成经历材料中回答“优化后快60%，方法是减少重复查询”。review先认可“你已说明减少重复查询及60%的主张，尚未独立核实”，具体probe基线／统计口径；不存在可支持业绩的reference引用。用户新答提供可核查测量记录、bind_scope显式纳入新范围，旧评价标旧范围；再ask/answer/review对新材料给对照建议和剩余环境限制，不把原自报补成真实成功事迹。概念正确部分与测量缺口分别显示。

T03 重复／丢响应：K提交body先存本机，server一次L-R成功后回包丢失；刷新GET K读取原request_sha/record IDs，界面恢复已完成；用户同key同文POST仅回原receipt。另keyK'同旧槽/规范hash为duplicate_of=K、effect=false，没有新record/admit。若首次仅accepted且未claim，GET继续显示待显式处理；仅用户原POST可领取一次launch。若已started/unknown，任何上述恢复均不启动。

T04 修正与迟到：answer A/v1对应已mark的review K；用户correct_answer基于当前head写A/v2、置K obsolete、head新答/answer_ready。远端K晚返回不能新写007/domain body，只按UNKNOWN保留预留；history保留A/v1、A/v2及K诊断。用户新review必须通过原窗口门及v2绑定，不因abandon或改key自动放行。另一竞态若L-R先成功，旧feedback存在但修正后失去当前资格，不能静默覆盖它。

T05 来源／多方向／恢复：展览史料sH/v1有两处日期冲突，feedback展示两出处和未定结论；源替换v2使旧question/feedback/citation正文抑制，历史只留版本/原因及用户原回答。刷新只读仍scope旧绑定，不自动用v2；用户bind_scope确认后scope+1、目标同文重新绑定goal+1、scope+goal两条及head+1同commit，ready后显式ask。误选已有G9记忆活动start前拒绝，不清记忆、不执行model。该轨迹不将策展方向固定为产品身份。

### D4 文档核对、实际投入与回传事实

本卡只进行了必要读取、hash／AST函数定位与一次最终文档一致性核对；没有compile／test／build／PG或SQL连接／HTTP／app／browser／Windows业务／Docker／SUP／模型／业务工具／安装／付费／Git写，全部为0。未读取activity.local.json、用户DSN／简历／凭据，未调用网站；官方页0/4。产品、配置、迁移、锁、旧证据、其他任务报告、正式DocuS、公共库、原始需求与外部记忆未写。

首读UTC 2026-10-07 16:46:18（本地10-08 00:46:18）；原单调start_ns=662987407364000，固定deadline_ns=673787407364000，沿原另扣60秒保守基点，不因中断后移。主动上限10800秒，metadata上限900秒；先前纯读取按保守300秒计，后续纯文件操作及最终核对实测累计见session.json，metadata与主动计数不另作额度或重置。旧45入口和旧任务失败/投入不并入新设计0运行，也不清零。

未实现／未验证项就是本合同全部新行为、011与新角色/profile/写路由、模型语义质量、D矩阵和五条轨迹；未自签独立审计、G10-P采用或G10验收。关键风险是原子hook／跨profile消费、修正和来源晚结果、普通SQL权限、front owner及引用晚交付，已落实到明确修改点和V07—V23，不泛化成重审全项目。

唯一待同步：编排核证本完整G10-P建议、正式架构/总状态与下一卡范围；采用后在一张完整实施卡内接线、定向验证、修复、资源收尾，再一次独立风险审计。103／104继续关闭，O01—03仍非阻断观察，完整Must／M-1仍未放行。没有设计阻塞或需要用户在聊天补充的密钥/材料。

一次最终文档核对完成：A—D、16新增/11修改生产文件及1配置例子、九动作/六阶段、三表/五函数、六路由、L-I至L-V、hash/回执/错误/修正/无记忆边界、唯一G10-P、32次未来调用建议、V01—V24及T01—T05互相对应。核对中补齐scope与goal重新绑定、封套hash、本地依赖/历史来源区分、引用截止及损坏schema分类；并将教学catalog定位名改为真实assemble_teaching_catalog。一次核对发现并在同次补正该登记名，其他21项有效核对直接复用，没有第二轮全量核对；这不是程序测试或独立审计。46主要输入、5直接依赖及001—010迁移最终hash匹配冻结源。

收尾UTC 2026-10-07T17:52:09.808651+00:00；主动累计约4011.7秒（含原保守60秒，未重置），metadata保守累计约660.1秒（此前300秒、续作纯文件操作60秒、一次人工文档核对300秒及实测hash/AST操作）。未独立计时部分明确保守计入，不假称精确。文档patch预期段落未匹配1次、函数登记名核对发现1项均已补正，产品FAIL新增0、metadata问题2；无在途运行或新业务资源。实录见session.json，核对原件见document-consistency.json，均在本文design证据目录。
