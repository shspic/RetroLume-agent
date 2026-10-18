# TASK-119 / R-113：Q 多步请求批准与启用前置合同

交付性质：设计完成，待采用及实施；Q 继续冻结。本报告没有启用 grant、签发可用批准、启动 72 小时窗口或执行产品验证。唯一推荐为“不可变授权根＋本机逐请求批准＋原命令显式继续”，采用零 DDL 的最小持久增量。每个实际完整请求仍须精确批准，不能把“来自合成活动”作为任意消息的外发许可。

本轮发现两个独立的启用缺口：官方已公告旧候选 deepseek-chat 停服；按下述保留全部语义目标的有限最坏安排需 81 次预留，且补证活动需 18 次，超过原全局 80 次及该活动 16 次。另有计量上界、账号适用性和实际 PG 组合证明未就绪。这些事实不阻止本设计交付，也不推翻已验收的 S。没有重新索取原 80 次／20 元条件许可，没有增加余额。

## A. 当前事实、阻点与唯一推荐

### A1. 合同、身份与继承

1. 根目录为 D:/shspic/project_NO3_RetroLume-agent，采用根 AGENTS.md 指向的 task_model、V4.0／CHG-0003 锁定规则。本窗为原 TASK-117 S08 工程归属的 A+ 路由，非 TASK-118 独审窗；没有委派子 Agent。输入许可为 [design-permit.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-119/orchestration-20261018/design-permit.json)。本报告及 design 目录是本轮全部写入范围。

2. 已核主控当前裁定与 TASK-118 review-01 的适用第 1、4、8 节。审计报告 65525 bytes、SHA256 8f4569489faef05fe212e943f6c33a1e4a94bdcaae6da4fac3958f425e654af6；TASK-116 采用包 SHA256 84cb852946220a09873225f8bde7b7138aa7366e137297638bb2aab01dbc1c84；后来的 [AP1/AP2 回执](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/orchestration-20261014/adoption-receipt.json)有效，不以旧设计中的“待批准”字样撤销它。编排列出的 19 份输入全部逐字节匹配，额外读取及冻结文字的元数据见 [input-identities.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-119/design/input-identities.json)。该文件同时列出 33 个固定输入值的 raw UTF-8 摘要和 JSON 字符串摘要，二者不混用。

3. D01—D04 及有限 S 的功能、工程证据已由主控验收关闭；历史控制偏差不追认。继承 S08 的完整请求前后检查、控制日志身份检查、最终 bundle 的 owner/view/head 防晚到和供应商告知，以及已通过恢复、两域持久性、只读查看原件。不重开四项缺陷，不重跑 28 场景，不把替身、结构或引用位置证明当真实服务语义。TASK-117 总体仍部分通过，STEP018 总体、Q、STEP019、STEP020、M1 和项目整体均不因本报告通过。

4. 原 source frozen、selector 永久 readonly 及六个旧 PG／失败／恢复对象保持原事实。本轮没有查询它们的实时状态，也没有复用其执行资格。未来 Q 只可在下一合同精确批准的新 normal 合成库与控制根执行；新资源不清零历史失败、旧 13 元耗尽账或任何累计预算。

### A2. 实际调用链与不可变对象

1. [create_activity](D:/shspic/project_NO3_RetroLume-agent/backend/app/activities/api.py:304)只从受信配置取得 grant，将其 SHA256 写入 activities.outbound_grant_sha256；固定 roster、分活动额度和两 provider 由服务器写定，客户端没有选择或重绑 grant 的字段。[create_activity 持久事务](D:/shspic/project_NO3_RetroLume-agent/backend/app/activities/repository.py:548)及后续准入继续以该活动行为权威。

2. [OutboundSourceManifest](D:/shspic/project_NO3_RetroLume-agent/backend/app/capabilities/embedding.py:136)的 v1 包含实际 source/version/revision/original hash、fragment identity/input hash、query_input_sha256 和 model_requests。非空 model_requests 进入 manifest 摘要；空值保留旧 Embedding 摘要。model_requests 的每项分别绑定完整 typed request 和完整 provider payload 的规范摘要。[check_model](D:/shspic/project_NO3_RetroLume-agent/backend/app/capabilities/embedding.py:183)还核 catalog 片段与原件，不允许只有 catalog 合格便外发其它正文。

3. [ControlledModelGateway.call](D:/shspic/project_NO3_RetroLume-agent/backend/app/capabilities/gateway.py:100)冻结请求和服务配置，在 admit 前、admit 后、mark 前及 mark 后复核。收费 admit 经 [PostgresAdmissionLedger.admit](D:/shspic/project_NO3_RetroLume-agent/backend/app/activities/repository.py:1130)和 Embedding 的 admit_embedding，共同进入 [_outbound_lock](D:/shspic/project_NO3_RetroLume-agent/backend/app/retrieval/repository.py:41)。固定 retrolume.outbound-roster.v1 advisory 锁、真实 roster SUM、原活动与 operation 预留均在同一 PG 事务；unknown 仍占用原预留。不能将其拆为两家各 80 次，不能从批准日志产生新余额。

4. 教学 [submit_command／_submit_model](D:/shspic/project_NO3_RetroLume-agent/backend/app/learning/teaching_service.py:59)将固定消息、实际目标、路径、题目、作答、纠错及历史装入完整请求；[accept_teaching_command](D:/shspic/project_NO3_RetroLume-agent/backend/app/activities/teaching_repository.py:975)先 COMMIT accepted 和冻结 context，再由 claim_teaching_launch 一次领取启动权。面试 [submit_command](D:/shspic/project_NO3_RetroLume-agent/backend/app/interview/service.py:88)与 accept_interview_command／claim_interview_launch 有相同的接受、领取分界；面试 v2 另有 selected memory 和按持久 seq 排列的本轮回答链。

5. 检索的 [RetrievalService.submit](D:/shspic/project_NO3_RetroLume-agent/backend/app/retrieval/service.py:127)先保存 retrieval_commands 冻结体，再 claim，逐批经原 one_call／SUP；实际 query 也绑定 domain_revision、parent_refs、memory dependency。教学当前 UI 通常以固定 goal 作 query，仍因 head/parent 身份改变而产生新请求，不能把相同 query 文字当同一命令。旧 [LearningService.execute](D:/shspic/project_NO3_RetroLume-agent/backend/app/learning/service.py:34)在 operation 之前没有与教学同样的 PG accepted 命令；[HtmlGenerationService.generate](D:/shspic/project_NO3_RetroLume-agent/backend/app/preview/generation.py:15)则已有 accepted／claim。后述合同分别补齐它们，不能只改教学入口。

### A3. 两个具体阻塞序列

1. 教学：固定 numeric_goal 和 N 资料形成 query Q1；Q1 的 received＋007＋向量结果 COMMIT 后才能组装 plan 请求 M1。M1 成功并在 007 及 teaching_records 中 COMMIT 后，产品才知道真实 path_record_id、node、正文摘要和 head revision。用户显式 accept_path 后，下一 query Q2 及 exercise M2 又绑定这些身份。把 M1、M2 的精确 request/payload 摘要都预填进一次不可变 v1 清单做不到；替换清单会改变 grant 摘要并违反活动不可重绑。仅将 path 的所有未来字符串视为已批准则重新打开 D02。

2. 面试：固定 R/M、interview_goal、冻结 memory_body 版本形成 ask。已提交的 question／probe、每个 answer_version、selected memory dependency 和本轮 record seq 决定下一 review 的完整消息。浏览器在本地保存另一段真实履历回答，或选择同名但不同 memory 版本，即使 catalog 仍为 R/M，也不得被下一请求的批准接纳。上一响应未 COMMIT、unknown、已失效或来自另一活动的正文不能作为派生项。

### A4. 唯一推荐及输入分类

采用固定 root manifest v2 和 grant v2，在新 normal Q 活动创建前一次绑定；未来批准是该根之下的独立、精确、一次消费回执，绝不追加 root.model_requests 或改绑活动。保留 v1 精确白名单分支及原结果；不引入另一套批处理平台、签名服务或费用账。本机受信工具按原键读取已冻结请求、审查并批准，浏览器只获得等待状态和显式继续能力。

根内输入严格分五类：冻结 JSON／验收合同中的有限文字；服务器分配且能在同库查实的 ID 和 revision；同一活动合格 received 结果的有限正文投影；客户端自由文字；源／记忆的实际版本。前三类依 B 中规则逐字段证明来源，第四类只可等于有限字面值，否则拒外发但允许正常本地保存，第五类必须逐版本匹配。资料目录相同、文件同名、ID 形似 UUID、字符串没有敏感词、模型自称“合成”都不是来源证明。

## B. 可直接实施的批准协议

本节是唯一规范合同；[protocol.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-119/design/protocol.json)为结构化索引，不是可用部署配置。所有新名称是待实施对象，不能误称现代码已经支持。

### B1. 稳定授权根及兼容

1. OutboundSourceManifest v2 的封闭字段为 schema、frozen_samples_sha256、acceptance_contract_sha256、sources、fragments、fixed_inputs、derivation_policy_sha256、template_set_sha256、instance_binding_sha256。schema 固定 retrolume.outbound-sources.v2。sources/fragments 保留 v1 的实际身份字段和检查；fixed_inputs 的每项是 alias、purpose、raw_text_sha256、json_string_sha256、max_utf8_bytes、allowed_activity_ids、allowed_actions。不得保留一个可动态追加的 model_requests 字段。有限字面值来自原 33 项及原验收合同的明确文字；缺失的 program_goal 直接使用 P 原文作目标，L05 的 240米／1分钟／4m/s 只在继承的本地验证中使用。任何另拟提示语必须先以新有限模板列入采用包，不能由 operator 临场扩大。

2. grant v2 保留原 grant 的批准回执、72 小时、80／20、三活动及分额、synthetic、price snapshot 等不可变约束，新增 schema=retrolume.outbound-grant.v2 和 instance_binding_sha256；source_manifest_sha256 指向上述稳定根。provider_capabilities 仍按已采用候选逐项封闭；本次不填可用新模型。source_manifest、template、policy、instance 或价率改变均使旧根不可用；只能停用并交主控，不能对已建活动换 hash。唯一活动集合及 PG 全局锁名不随 grant_id／provider 改变。

3. QInstanceBinding 是在未来精确资源许可下、创建三活动前固定的私有非秘密对象：hub_control_id、dataset_id、instance_id、originals_root_id、normal selection_generation、schema_profile、source_registration_sha256、正常连接目标摘要、PG cluster system identifier／database OID 的受信观察、控制根绝对路径与 Windows volume/file identity。连接摘要只在本机计算，不输出 DSN；普通业务角色不增加 pg_control_system 等权限，必要元数据由已有受信部署管理入口读取。服务端每次用同一连接的 data_state、当前 DataContext、固定部署连接和控制根身份核验；不可核即关闭。逻辑拷贝的新 instance／database OID、物理拷贝的新控制根或未经登记的目标均拒绝；具管理员能力复制全部秘密、原地回滚 PG 和控制根不在本地普通客户端威胁边界内，检测到恢复／缺事实仍停止，不能承诺抵御管理员克隆。

4. v1 原 model_requests 非空精确核验不删除；v1 空清单仍拒模型，原 embedding 检查不放宽。v2 只能经新批准协议；不能伪装 v1 空列表而免审。OneCallInput v3 原字段／字节和非 Q 路径不变；现 v4 在 grant v2 时增加独立 outbound_authorization 引用，内容仅 root_sha256、prepared_sha256、approval_id、approval_event_seq，不能放进 ModelCallRequest 或 provider payload，避免摘要自引用。v4 原体不带此项时沿原规则。worker 从既有 ledger.data_guard 指定的本机 ControlHub 复核，不能信任 IPC 所声称的 approved。typed request、请求、响应和原监督上限仍各自检查，不增加 65536 bytes／10 秒上限。

### B2. 规范字节与 PreparedRequest

1. 新对象的规范化 C：UTF-8、无 BOM／尾换行、对象 key 按 Unicode 顺序排序、无多余空白、ensure_ascii=false、禁止 NaN／Infinity／重复 key／未知字段；整数保留整数，时刻采用带 Z 的 UTC，价格用十进制定点字符串。列表保留其语义顺序；set 仅按封闭字段规则排序，Q 的 allowed_tools 固定空。H 是 SHA256(C(object))。raw_text_sha256 永远是未经 trim／Unicode 改写的实际 UTF-8 字节摘要。query 仅允许现有明确 strip 规范；批准的是 strip 后实际字符串及原冻结 command。历史 v1 digest 和业务 context/hash 按原函数，不把新 C 追溯套到旧数据。

2. 服务端无出站地重建 ModelCallRequest／EmbeddingRequest，使用同一纯 payload builder 生成实际 provider 对象及 C(payload) 字节。PreparedRequest 的封闭元数据是 root_sha256、grant_sha256、instance_binding_sha256、activity_id、domain、action、business_key、operation_id、batch_ordinal、command_request_sha256、frozen_context_sha256、typed_request_sha256、payload_object_sha256、payload_bytes_sha256、payload_bytes_count、provider、base_url_path、configured_model、thinking、response_format、max_output_tokens、template_set_sha256、source_refs、memory_refs、parent_refs、scope_revision、head_revision、goal_version、created_at、valid_until、provenance_sha256。max_output_tokens 对 embedding 为 0。parent_refs 明确指到记录和 operation 的 admission_id／scope／generation／007 payload hash，不只存标题或文本。

3. 私有 artifact 同时保存完整规范 typed request、实际 payload 字节和封闭 provenance，单 artifact 上限 262144 bytes；typed 与外发 payload 各仍不超过 65536。artifact 的 SHA 由 q.prepared 日志绑定，单帧只存元数据，不抬高 ControlHub 的 65536 帧限额。路径由服务器按固定 category 和 prepared UUID 构造，HTTP 不接受绝对路径。artifact 不含 API key、DSN、完整用户资料库、其他活动正文。正式日志只保 ID/hash/bytes 和分类原因。

4. Q v2 的 transport 增加接受 frozen JSON bytes 的私有方法，HTTP 只发送已批准的这些 bytes、固定 endpoint、Content-Type 和由正常 loader 注入的 Authorization。不得批准规范对象后再次按另一 serializer 组包或从可变原对象发送。旧 v1 transport 行为不因此重写。worker 重新构建的完整 typed/payload 三个摘要与 artifact 均须相等；不同则零发送。

### B3. 批准者、入口、权限和有限来源证明

1. 批准主体是正常部署中明确登记的本机 operator OS principal，在 AP2 的有限合成范围内作逐请求授权，不是授予新数据外发权的个人同意入口。未来新增 `backend/app/operator/q_request.py` 的本地命令：inspect／approve／revoke，参数仅活动 ID 和原 business key（批量索引另带 batch ordinal）。工具从受信部署入口解析原 ControlHub 和原 PG，读取完整 artifact 与冻结事实，自行计算摘要；操作者不从聊天粘贴正文／hash／密钥，也不提供任意 URL、文件或 grant。approve 在同一有界本地进程显示供应商、用途、输入来源与字节数后，由 operator 本机确认一次，写入精确回执。没有 HTTP 批准／签票接口，没有后台 watcher、自动 approve-next、浏览器“同意全部未来内容”。

2. 本方案不另造签名密钥。真实性来自受信 loader、固定 operator principal、原 ControlHub 私有 ACL、真实 RootLease 和 D01 已关闭的完整日志／首 control_id 核验。q.prepared 只能由服务端 prepare 写，q.approved／q.revoked 只能由上述 operator 命令的专用入口写；浏览器没有日志路径、写权限或调用该入口的 API。worker 可以读已批准 artifact，并通过受限方法写 claim／admission 观察，不能调 approve。若部署无法区分这些逻辑能力或 ACL 不能核准，readiness=false；不能把普通 hash 称密码学签名。私有目录拥有者／系统管理员仍属于部署信任边界。

3. 每个非模板文字字段都有 provenance 路径，覆盖 goal、answer_text、corrections、历史、selected memory、引用标题、来源名、page/origin、节点名／题干／参考、feedback 摘要、ID、角色标签与其它实际发送字段。固定输入按 alias＋用途＋实际字节完全相等；不作语义相似匹配。来源须是当前获批的 source/version/revision/original，fragment 与位置、实际文字 hash 同时合格。memory 须精确 memory_id/version/revision/body hash，等于冻结 memory_body，仍为低信任偏好，不能当履历或能力证据；选择别的同名 memory 不合格。

4. 模型输出不自动扩大文字白名单。只有同 grant、同 activity、同 instance 的 model operation 已 received，007 正文与相应 teaching/interview record 在同一有效提交链可读，admission／generation／scope／payload／record body hash 全部对应，且现时父消费资格合格，才能由受信纯投影器提取本动作允许的有限字段。教学只取实际路径节点、当前题、当前反馈、允许的数值核算及已核原答案；面试只取本轮按 seq 排列、至多原 12 refs 内的问／probe／答／feedback；HTML 只取合格当前父反馈与批准 catalog。每次批准仍审查这些新字符串的完整 bytes。模型产生任意标识、命令或新来源不授权限，超出 schema／容量／用途即拒；unknown、late-invalid、历史不合格、跨活动、跨库、旧个人记录均不能派生。

5. query 的批准同样覆盖完整 typed request 和 payload。当前固定 goal query 可以按有限文字证明；若以后取已提交题干或节点作 query，必须标明同活动合格 parent 的允许投影，不能启用一个“任意 model output 都可检索”的规则。embedding 的 source_index 与 query 不互认，不能把 embedding007 当模型父。模板、IDs、catalog 与正文的 provenance 是联合校验，不能仅批准某几个敏感字段后放过其余字段。

6. Approval 的封闭字段为 approval_id、prepared_sha256、root_sha256、operator_principal_id、issued_at、expires_at、decision=approve、event_seq。approval_id 对本次完整决定取 H；相同 prepared 重复 approve 返回原决定，不能发第二份可消费许可。同一 activity/operation/batch 对不同 prepared hash 冲突并关闭；失效后只能在原体确未 claim、现资格完全一致时显式签新时限回执并保留旧事件。有效期为签发后 15 分钟、活动 deadline、grant 终点三者最早值；root 撤销、源／记忆／scope／head 改变、模板／服务配置漂移均立即失效。每根最多 128 个 prepared、256 个批准事件，原 journal 容量不提高；达到上限交回。

### B4. 等待状态与逐入口接线

1. 教学／面试／HTML 先完成现有 accept 的 PG COMMIT，保持 status=accepted、launch_claimed=false／NULL，再保存 q.prepared。首次 POST 在 grant v2 下只准备并返回 accepted 与 outbound_approval.state=pending，不启动 SUP、不创建收费 operation、不占 requests/cost/running/tool/preview。若 accept 成功而 artifact 发布丢确认，GET 显示 accepted／preparation_unconfirmed；服务端只可从同一持久 context 幂等补齐原 artifact，不重检索、不换 key，不把它终结为 rejected／unknown 再声称批准后可重跑。

2. 现命令 GET 新增可选 outbound_approval 小对象：state、prepared_id、purpose、provider、model、request_count、reserve_microunits、expires_at、can_continue、reason。可见等待态由 accepted＋尚未领取 launch＋当前批准投影得出，不新增 PG status。原 retry_policy=same_key_before_claim 仅在批准仍有效时允许继续；未批时给 can_continue=false 并显示“等待本机批准”。GET 不写日志、不补 artifact、不领取启动权。prepare 修复仅由原 POST 或本机显式 prepare 命令触发。

3. operator 批准不自动执行。用户在原页面显式“继续原请求”，携原 key 和 IndexedDB 原体再 POST。后端先比原 request/context/prepared，再核当前批准，之后才进入原 claim_launch。前端 resumeAccepted、teachingIntents、interviewIntents、retrieval chain 和 HtmlExplanationPanel 均只读取原事实，不自动重新 query、另建命令或再次 POST。原 owner、view、head、DataContext、draft identity 的 S08 检查继续保留。

4. 检索在 retrieval_freeze COMMIT 后、retrieval_claim 前准备每批 envelope；source_index 所有待发批均先获批，然后一次显式继续按原顺序执行，不能中途等待时持有 SUP／PG 事务。查询只有一批。部分 received 保留，任何 unknown 不重发；后续新命令只处理确需且未存在合格缓存的片段，并明示 unknown 可能重复费用。等待中不改 accepted 的冻结 manifest。

5. 旧 learning first／followup 没有 PG accepted 行，因此在这个非默认 Q v2 分支中，由 q.prepared 持久保存其原完整 intent、frozen profile、operation slot 和 artifact；原 GET `/activities/{id}/learning/intents/{key}?action=...` 先查 PG 已有 operation，再查同一私有 prepared，返回 awaiting_approval／approved／consumed／invalidated。它不是新的业务或费用事实。显式原 POST 用原 frozen profile；first 的原单槽和 followup 的原 parent 规则继续有效，不能借批准绕过 find_learning_operation 冲突。PG 已存在 operation 时只 GET，不再以私有 intent 覆盖。新字段只在 Q v2 生效，非 Q 旧响应保持兼容。

6. HTML 在 accept_html_command 之后、claim_html_command 之前准备和等待；批准不授予新 preview ticket、renderer、Docker、工具或 host 权限。生成 description 是一笔模型费用；固定交互启动仍独立沿已验签票据、原预览账和 StopProof。没有为解释请求自动增加一个 query，也不把旧解释当当前 Q 题的真实解释。

### B5. 消费、事务、失效与恢复

1. 原 command GET 证明 accepted 且未 claim、当前 head/scope/memory/parents 合格时，显式继续先核批准，再执行原唯一 launch claim。claimed 后无论费用是否产生均不能回退到等待来重用该 launch。持久 q.claim 绑定 prepared、approval、原 operation 和实际执行者／generation／run_tag；worker 在 admission 前一次消费该批准。该事件不增加费用或余额。claim 确认丢失时先 GET 原 PG 命令及私有事件，不启动第二监督；无法证明未领取就保持只读未确认。

2. 锁序：正常维护 MutationGate 与原 worker owned 资格保持；新增 `.q-policy.lock` 共享读租约覆盖该次有限执行，operator revoke／根停用及该 Q 根内会使外发资格失效的 source／memory／scope／head 写操作取排他租约，在取得它之后才开 PG 写事务；每请求另有由 prepared ID 派生的独占 RootLease 防双消费。日志锁只短持，不跨网络。PG 内仍先固定全局 advisory，再按原 source→memory→activity→operations→domain/command 顺序核定；不在已持 PG 行锁时反向请求私有消费锁。共享 policy lease 允许不同请求并发，不能以 Python mutex 代替 PG 总门。operator 撤销或 Q 根内失效写等到已进入发送临界段的有限调用退出，最多原受控调用及收尾期限；等待取锁失败应报 busy，不能谎称已经撤销远端调用。该序列化仅适用于新 Q 根，非 Q 的原晚到／历史处理保留。

3. admission 前、同一 admission 事务内、admission 后、mark 前、mark 事务内和 mark 后都重新比完整 identity／payload bytes／当前时限／父资格。PG 事务内通过受信 q proof 验证原 prepared 和消费身份，实际 roster SUM 与活动预留、operation insert 一起 COMMIT。mark 仍一次 reserved→dispatched。最终字节检查与 transport 进入处使用同一不可变 bytes 和有效 policy lease；一旦调用 transport 不得改正文／URL／服务。改变发生在批准后且 admission 前：零 reserve，原接受体 invalidated／等待新合法动作；发生在 admission 后且确定未发送：原 reserve 留账、NOT_SENT；mark 后确定未进 transport 也是 NOT_SENT 留账。已经可能发送则 UNKNOWN；收到晚到结果保事实，当前消费资格不合则抑制正文，不投影新 head。任何分支都不退款或复用原 key 自动重发。

4. 同 key 同 body／prepared 并发仅得一个 launch、一个 q.consume 和一个 PG operation；同 key 异 body 409 保原体；同 semantic slot 异 key 仍按原领域重复／冲突规则处理。批准回执和当前 prepared 不同、旧 approval 与新模型／记忆／父摘要拼接、把新 operator 批准套在已 unknown operation 上，均 fail closed。没有“重新批准便允许 retry unknown”分支。已确定 failed／NOT_SENT 的显式新 key 重试仍要新 prepared／approval，旧预留照计。

5. 在原 ControlHub 添加 q.bind、q.prepared、q.approved、q.revoked、q.claim、q.admission_intent、q.admission_observed、q.closed 的封闭事件投影。q.admission_intent 在实际 PG admit 之前持久记录该 operation 的完整预期与原 roster 观察，观察不是预扣。admit ACK 丢失时以原 activity/operation 回读 PG；只要存在原 operation 就保留其 requests/cost。没有 operation 且已证明原执行树停止、原事务结束，才可认本次未准入；仍不回退已经领取的 launch。不能靠 HTTP 失败推断未 COMMIT。

6. admission_observed 只保存原 PG 已提交 operation 身份、admission、provider/model、固定 reserve 及三活动累计值，作为防缺事实的单调核对见证。它没有余额、充值、退款、结算或“剩余可花”权威。新 admit 仍只查原 PG SUM；观察值落后不多授一笔，观察值领先／已见 operation 消失／grant 不同即关闭。并发在途 intent 由准确 owned/birth 和 PG 原行核对；重启发现未结 intent 先只读对账，禁止开新根抹掉。私有日志损坏、尾 COMMIT 不确认、artifact 丢失、身份换根、PG 数据回退或任一核对不可用，统一拒新外发，保留原操作／预留／失败。

7. received＋007＋业务正文 COMMIT 的 ACK 丢失，只 GET 原 command／operation／record；经原 committed_current 判定读回同 payload 后才能准备下一步。父结果没有与业务 record 一起合格提交时，不能仅凭网关收到 JSON 就批准下一步。重新启动本机正常应用可以恢复已接受的等待意图和只读事实，不能恢复旧租约、旧 clock domain 或 claim；新 generation 只有新的合法动作，旧 unknown 不重发。批准过期会阻止新调用，activity 的 24 小时和 grant 的 72 小时照常流逝，等待不延长期限。UTC 回退或时钟域无法解释时拒新外发；重开重新核绝对有效期和未 claim 事实，不追补跨中断可用时长。

### B6. 最小持久差异、退出和回滚

本方案不新增表／列／SQL／角色／profile，不改 001—014。accepted、冻结 context、operation 唯一性、实际预留已经足够承载业务与费用；缺的是跨请求的私有批准身份和无 PG intent 的旧 learning 等待信息，故仅扩当前 normal ControlHub 的封闭事件与私有 artifact。q 事件的 schema、actor 分工、ACL、RootLease、容量及 worker 接口属于采用项，不能用“零 DDL”掩盖新权限边界。

R01/R02 数据导出、恢复链和永久只读角色不变：业务行、outbound_grant_sha256、operations、007、领域／检索事实按既有格式导出；API key、DSN、operator 能力、q 执行批准与可恢复 launch 不入包。私有审查记录在本机保留 hash／身份历史，普通数据包没有它便绝不能重获 Q 执行权。拷贝包／恢复目标最多读取，不把旧 approval 当新 normal 授权。发生源／记忆清理时，正常业务 purge 继续；q artifact 的正文副本同步抑制并清理，保留不可授权的 hash／事件，清理不确认便关闭 Q，不能从 artifact 回出被删内容。

回滚采用为关闭 Q v2 并保留新事件、原 PG／预算，不迁回旧 grant、不删 private journal。旧程序遇 v2 配置必须明确不支持而 fail closed；只读查看旧业务事实仍可。没有改 DB shape，因此不需 R03，也不能以此允许运行不认识 v2 的旧程序消费 Q。完整卸载事件正文须沿获准数据退出清理，不擦除金融和失败历史。

### B7. 四条手工轨迹

仅有四条设计推演，均未执行、未产生请求或费用；完整事件索引见 [hand-traces.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-119/design/hand-traces.json)。

1. 正常两次依赖模型调用：学习 A1 的原 K-plan 在 Q-plan received 后 accepted／P1 pending；operator 批 A1p，原 K-plan 显式继续，只发 M1 一次，PG 从 1 次 query 增为 2 次、500000 预留；M1＋007＋path COMMIT。accept_path 为本地动作，下一 Q-exercise 经另一个精确批准和新 key 发一次，随后 K-exercise／P2 使用实际 path parent；批 A2p 后 M2 一次，合计 4 次外发／1000000 预留。两个模型请求的批准依赖真实已提交父，活动 grant/hash 始终不变。

2. 第一结果 COMMIT 丢 ACK／重开：沿同 K-plan／P1，M1 已收到且 PG、007、path 一起提交；HTTP ACK 丢失。重开 GET 找同 admission／payload／path，provider 发送仍 1 次 M1，requests/cost 仍含 Q-plan＋M1 两次。没有重新 approve 或 POST M1；只有合格 GET 后新 K-exercise／P2 可以准备。若回读只有 received 元数据没有合格正文或业务 record，则停在未确认，不派生、不退款。

3. 等待批准遇变更：原 K-review／P3 accepted，尚无 operation；改变 scope 或 memory 版本后，P3 invalidated。把未批准回答保存成本地新版本仍可，但原 K-review GET 不允许继续，operator 工具也不能批准该真实文字。旧 key 不换冻结体，零新增 provider／reserve。若同类变更已发生在 admission 后，则原 250000 保留，确定未送按 NOT_SENT，否则 UNKNOWN，不回等待恢复资格。

4. 跨 provider 临界竞争：同 normal 库已有总计 79 次、19750000 预留，A1 的 model 与 A2 的 embedding 各有不同合法 key／P／approval；它们同时走生产 admission。真实 PG 同一全局锁使至多一笔新 operation 与活动预扣 COMMIT，总计最多 80／20000000。输方不发；胜方即使 timeout unknown、重开或撤销批准，预留仍在，不能另建 grant／活动借第 81 笔。在全部收费请求固定 250000 的合法 Q 账中，requests=79／cost=20000000 不可达，不能伪造这个“费用单独耗尽”行。临界前后同时观察次数和费用两个门，80／20000000 后两方均拒；各比较式的其它语义由源码和受影响的零出站边界断言核对。

## C. 官方事实、计量与有限调用矩阵

### C1. 公开官方核查及唯一模型差异建议

核查日为 2026-10-18，仅查 DeepSeek／智谱官方公开文档与条款。共 8 条搜索查询、22 次文档读取尝试，其中 7 次抓取失败；成功文档响应 15 次，包含重复 URL、三次 find 无匹配响应及一个价目 JS 壳，保守计入 16 页上限。检索摘要不冒充新增逐页打开。重复和失败都保存在 [web-request-ledger.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-119/design/web-request-ledger.json)，没有为凑满额度继续读取；没有账号、账单、登录或实际模型 API 操作。自述摘要、版本、未知与来源详见 [official-facts.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-119/design/official-facts.json)。

1. DeepSeek 的 2026-04-24 官方公告明确旧 deepseek-chat／deepseek-reasoner 于 2026-07-24 15:59 UTC 后停止服务；2026-10-17 更新使用 deepseek-flash，对应 DeepSeek-V4.1-Flash-1017。因此原候选不能当作现行可用能力。唯一最小替换建议是保留原 deepseek_chat_completions、base 和 ChatCompletions 接口，仅把候选 configured_model 改为 deepseek-flash、继续显式 thinking disabled。它是待采用的模型变更，本轮没有改配置、调用旧名探活或自动切到 Pro／其它服务。[停服公告](https://api-docs.deepseek.com/news/news260424/)、[官方更新日志](https://api-docs.deepseek.com/updates/)。

2. 当前接口文档列出的模型名为 deepseek-flash／deepseek-v4-pro，提供 thinking disabled、max_tokens、json_object 及 usage 字段。JSON mode 仍需提示 JSON，且可能空内容／截断，不保证本地业务 schema 或语义。公开材料未使本轮获得完整、确定的 returned_model 别名集合；现在网关只核返回字符串格式，未来 Q v2 应从受信 capability snapshot 增加严格 returned_models 校验，未知或返回不符仍留 received／失败及预留，不能作下一父项。不能把输入 model 名等同已经实测返回身份。[Chat Completions 文档](https://api-docs.deepseek.com/api/create-chat-completion/)、[JSON 输出说明](https://api-docs.deepseek.com/guides/json_mode/)。

3. DeepSeek 中文价目当前 Flash 高峰、缓存未命中输入为 2 元／百万 tokens，输出为 8 元／百万 tokens；不采用低谷或缓存折扣。英文价目用美元，不能把美元数值当人民币。公开价格会变，页面未给本账号含税最终适用价或计费模板上界。官方最大输出虽已更高，产品 learning≤256、teaching／interview≤2048、HTML≤4096，以及 10 秒、65536 bytes 原限额全部保留。[人民币价目](https://api-docs.deepseek.com/zh-cn/quick_start/pricing/)、[英文价目](https://api-docs.deepseek.com/quick_start/pricing/?model_version=DeepSeek-V4-Pro-0813)。

4. 智谱 Embedding-3 官方页确认既有 endpoint、配置名 embedding-3、512 维、返回示例 model=embedding-3 和 prompt／completion／total usage，公开输入价 0.5 元／百万 tokens，数组最多 64 项。页面同时列 8K 窗口和“单条请求最多 3072 Tokens”；本合同按保守解释要求每项及整批均有已核 ≤3072 的输入上界，仍最多 4 项，不用较大官方批量扩大本次能力。现 2048 codepoints 输入限制不能证明 token 限制；Q 另做 UTF-8 字节／计量上界检查，超界拒绝，不截断冻结样本。返回 vector 数量、index、512 个有限数、使用量和 response≤65536 仍逐一核。[Embedding-3 官方文档](https://docs.bigmodel.cn/cn/guide/models/embedding/embedding-3)。

5. DeepSeek 中国开放平台条款更新于 2026-04-22、生效于 04-29，覆盖 API 开发者、输入权利、key 保管及预充值；隐私政策更新／生效为 2026-02-10，覆盖 API 但允许特约，说明境内存储、必要保留和法定例外，并有拒绝训练使用的设置。不能由此签“此 API 账号默认不训练”或“零保留”；本轮没有核账号适用开关、特约或具体 API 留存天数。[开放平台条款](https://cdn.deepseek.com/policies/zh-CN/deepseek-open-platform-terms-of-service.html)、[隐私政策](https://cdn.deepseek.com/policies/zh-CN/deepseek-privacy-policy.html)。

6. 智谱隐私政策生效日期为 2025-05-20，主体为北京智谱华章科技股份有限公司；适用平台／API，说明境内存储及必要／法定保留，并允许匿名数据用于算法训练。服务协议含实名平台账号、人民币预充值、促销限制和必要数据留存；抓取正文未给清楚的该协议版本日期。不能宣称默认不训练、固定零保留或拿 Coding Plan／赠金当 embedding API 权限。本轮未核实际账号、key、税或特约。[智谱隐私政策](https://docs.bigmodel.cn/cn/terms/privacy-policy)、[智谱服务协议](https://docs.bigmodel.cn/cn/terms/service-agreement)。

公开文档只证明上述公开事实。未来正常 secret loader 的非敏感 readiness 必须分别报告 model／embedding key 是否在服务器正确注入、目标账号/地域/币种/含税价及条款是否适用；不输出值，不向对话索 key。当前全部相关账号事实为 UNKNOWN，不能填 capabilities_verified／account_terms_verified=true。没有个人数据外发授权，模型返回的文字也不产生这项权利。

### C2. 逐次费用公式与关闭条件

原单次 reserve=250000 microunits，1 元=1000000 microunits。未来 price snapshot 每项有官方 URL、取证日期、币种、适用主体／账号非秘密标识、输入／输出最高含税价、计量证明摘要、thinking disabled 的额外收费界及 expiry；原 grant 的同一组价率可取两 provider 的逐项最高值，不拆预算。价率或币种不明不发，不能因 embedding 通常便宜给它另一份余额。

本轮只给条件反算：在已核“输入 tokens≤实际完整请求 UTF-8 bytes＋framing”、framing≤4096、disabled 不另收未界定 reasoning、人民币含税最高输入 2／输出 8 均适用时，以 25% 裕量按 microunits 向上取整。公式为 ceil((T输入×2＋T输出×8)×1.25)，其中 T输入不是精确计数，4096 也只是既有 grant 可表达的设计上限，不是本轮已核事实。

在请求上限 65536 bytes 下，输入反算为 69632。embedding 输出 0 时共同最高价上界 174080；learning 输出 256 时 176640；teaching／interview 2048 时 194560；HTML 4096 时 215040，均形式上小于 250000。若按 embedding 自身公开 0.5 输入价单独说明，其条件上界为 43520；正式共同门仍可采用更保守的 174080。任何费用计算均用 Decimal／整数向上取整，不用浮点截尾。

这不是可用报价或 token 证明：官方 tokenizer／消息模板额外 framing、额外 billed reasoning、账号币种和含税边界尚未核清，相关 verified 全为 false，活动量也未实际测量。即使形式费用低于预留也不得开启 Q。embedding 另需证明每项及整批输入 token 限制，不能拿宽松的成本反算值证明 3072 限额。没有官方可证或获准的保守计量方法时，该能力保持关闭，不下载 tokenizer／SDK、不增加计费 API。下一轮在明确允许的官方核查中补这些事实，确认后才产生正式 snapshot；有模型、报价或条款变化就回主控，不能扩大 10 秒或预留。

### C3. 完整语义矩阵、缓存和精确不足

结构化逐行动作、输出上限、层级及分配见 [call-matrix.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-119/design/call-matrix.json)。下列为一次有限成功／必要追问路径的最坏准备量；所有失败和重试另消耗既有余量，并非承诺一定能通过语义。当前没有任何真实 Q COMMIT 可扣减。

1. Q00 索引 2 次：八份短合成文本设计假设各形成一个合格 fragment，F=8，则 ceil(F/4)=2。由面试活动先在 interview.v2 的 start(goal=null) 建 head、固定八源范围内明确索引；该顺序沿当前 start 允许空目标及索引要求 head 的真实接口。索引后把范围明确修订为 R，再保存冻结面试目标。两笔索引各须批准，源向量可被另两个活动按相同 source/version/revision/space 复用。正式准备必须先无费用核实际 fragment 数，若 F>8 直接改用真实 ceil(F/4) 并扩大缺口，不能假造单片。

2. 学习活动为 L01 的 plan、initial exercise、错答评价、targeted exercise／评价、独立 retest exercise／评价，共 7 model＋7 query；L02 三个独立肯定答案各评价，3＋3；L03 三个精确反例，3＋3；L04 否定和不确定，2＋2；L08 歧义澄清、显式范围与目标修订后的新 plan，2＋2；L09 无证据及冲突各一次，2＋2。沿 teaching.v3 已有 clarification／no_evidence／conflict 输出联合，不能用 scope 改变后已无资格的旧 learning 父续问。每个新 head 的 query 即使文字相同也计一次。

3. L10 在 L01 首次合格 feedback 之后、后续题改变父项之前，生成当前题的固定描述一次 HTML model，不额外发 query。随后真实宿主 input ACK、读值／PNG、reset 和 StopProof 属本地验证，沿原票据和预览账，不伪造真实服务生成。上述学习活动合计 19 个普通模型＋19 个 query＋1 个 HTML=39 次，9750000 预留，低于其 40／10000000。

4. 补证活动覆盖 L06：concept_goal 的 plan／exercise、三个固定概念答案评价，5＋5；L07：用 P 原文这一有限文字作目标，plan／exercise、两个固定程序推理答案评价，4＋4。合计 18 次、4500000 预留，超过固定 16／4000000 两次和 500000。没有用户程序执行，没有因本地确定 parser 可用便取消真实开放语义。

5. 面试用两轮合并覆盖，逐个答案仍独立保存、批准、query 和 review，不把一条正确回答冒充其它输入。R-only 轮包含 I02 的 supported／self-report 和 I03 的 invented claim：1 ask＋3 个基础 review＋最多 2 个额外 probe 回复 review，共 6 model＋6 query；该轮同时核范围外 M 不可作依据。R+M 轮覆盖 I01 完整链及 I03 位置正确却不支持利润收益：ask，incomplete 必须产生首个必要 probe，另存 invented claim 作负例，再以 supported answer 收口；加上至多一个剩余 late probe 的回复 review，共最多 5 model＋5 query，最后本地 finish。首个必要 probe 已消耗两次上限中的一次，不能再凭空加两次；反之若首个未产生必要 probe，该 Must 失败，不能免费抽样到满意。两轮最多 12 refs 边界仍核，满额拒绝而非裁掉必要正文。两轮 22 次加索引 2 次=24 次、6000000，正好用满该活动。

6. 全部合计 39 个 2048 上限模型、1 个 4096 上限 HTML、39 个 query、2 个索引，即 81 外部请求、20250000 预留。按 C2 尚未核实的共同最高价公式反算，token 费用上界为 14940160；它不能替代 0.25 逐次 reservation，不能因估算便宜而批准第 81 次。全局少 1 次／250000，补证分额少 2 次／500000；学习剩 1 次不能挪给补证。即便索引全在面试活动完成，学习语义核心 57 次也大于两个学习类活动合计 56 次，不能靠换索引承担方解决。

7. L05 的暴露、独立实例计数、去重、理由推进和 assisted 判断继承已验收的 S 的 T/U 层；L01 仍有真实服务独立 retest。本矩阵不称新 Q L05 已通过。若实际新路径还需要一份新的独立 exercise／evaluate 才满足当前语义链，追加 2 model＋2 query 的实际需要和缺口；不得删掉 Must 或把已暴露正确当独立证据。X01—X12、P01—P03 的安全故障、持久性、PDF／恢复／只读原件按实际已验层继承，新批准边界与 PG 组合只做零外发补证，不付费注入故障。

缓存只限真实存在的合格向量：相同 provider/model/dimensions/space、同 source/version/revision/original/fragment 文字，vector digest 复核及当前 source 无 tombstone；跨活动复用源向量不授权跨活动模型父。query 只能从原 key、完全相同冻结 body/head/parent/memory 的 received 命令 GET 复用；目标修改、回答新版本、换活动、相同文字或另一个 key 都不是 query 缓存命中。没有缓存实际存在证据时按 miss 计。

既有 80／20、分额、72 小时及 24 小时／3600 秒等限制原样保留；本轮不提出可用新额度。不足已精确交回，后续主控必须先取得一份保留全部 Must 且合法分额可容纳的剩余矩阵，或将新增额度／分配作为明确新许可合并决定，不能静默增费、换 grant、换 roster、开新 DB 或切成功口径补余额。没有解决该项时完整 Q 付费启用门关闭。

## D. 完整下一实施、独审和采用包

### D1. 一个连续工程成果合同

下一实施在同一原工程归属连续完成下面全部改动、普通修复和必要补证；不为每次准备、组包或修夹具另转卡。以下是待实施范围，本轮没有写产品或测试。

1. `backend/app/capabilities/embedding.py` 增加严格 v2 根／grant／PreparedRequest／Approval 类型；v1 不改语义。`contracts.py` 给受信 Q 模型配置增加 returned_models 和独立授权引用，空／未核集合关闭 Q。`gateway.py::_build_payload/call/_parse_success` 和 embedding gateway 共用准备与核定原语，exact typed/payload/bytes、批准失效、返回身份及 reserve 分类同时传播。`transport.py` 增加只收冻结 bytes 的 Q 私有发送方法，不允许该方法附带任意 endpoint／工具。现公共 capability 两家告知从实际采用配置读。

2. `backend/app/data_exit/control.py` 添加 B5 的封闭 q 事件、方法和私有 artifact 分类；复用完整日志锁内核验和同 hub 身份，不能改成只校验缓存。未来 `backend/app/operator/q_request.py` 是唯一批准／撤销命令，默认拒任意路径、root 替换和权限越界。`data_exit/maintenance.py` 的当前 normal Q 根专用 policy lease 与 private claim 入口接线，source／memory／scope／head 失效写在原事务之前取排他 policy lease，避免发送临界段反向锁。`data_exit/deletions.py` 使被删正文的 q 副本抑制／清理，与原删除 fence 和失败保留一起核，不改旧 selector／恢复权限。不得直接把 ControlHub 的 data-exit Operation 当成可重用模型调用许可；其 clock-domain／一次消费语义保留。

3. `activities/api.py::create_activity` 只在 fixed root/instance/价格等身份一致后写原 grant hash；已有活动不能重绑。`activities/repository.py::admit/mark_dispatch_started/record_outcome` 和 `retrieval/repository.py::_outbound_lock/admit_embedding/mark_embedding_dispatch_started/record_embedding_outcome` 在原 connection.transaction 中核受信 proof、当前来源／父、原 global SUM，再写实际活动和 operation。明确 commit-unconfirmed 对账路径，不能在异常处理时假写未准入。唯一新见证是关闭条件，PG 仍为费用权威。

4. `learning/teaching_service.py::_submit_model`、`interview/service.py::submit_command`、`retrieval/service.py::submit`、`preview/generation.py::generate` 都在 accept/freeze 后、claim 前准备并等待；各自 GET 和 receipt 装饰器读取批准投影。`learning/service.py::execute/reconcile` 的 Q v2 分支使用私有冻结 intent 补齐 operation 前的 GET 恢复；不改旧 first 单槽／父消费规则。`worker/one_call.py::to_wire/from_wire/decode_worker_request` 与正常 `retrieval/service.py::load_integration_config`、`service_config.py` 共同传严格授权引用，worker 用原 data_guard 和真实 root 复核，不能仅相信调用方已核。秘密仍只从服务器现 env loader 来，不进入日志／artifact／浏览器。

5. `frontend/src/activities/TeachingWorkspace.tsx` 的 resumeAccepted、`InterviewWorkspace.tsx`、`ActivityWorkspace.tsx`、`RetrievalPanel.tsx` 及 teaching／interview／learning／retrieval intents 和 API 类型，连同 `frontend/src/explanations/HtmlExplanationPanel.tsx`，统一展示等待及原键显式继续。保持原草稿、owner/view/head/DataContext guards、GET 后状态比对和供应商用途告知；pending 不禁正常本地保存，批准不触发后台重发。按钮只描述等待／继续及用途，不把 file path、DB、grant hash 或签名步骤塞给普通用户。

6. README／部署说明在实际采用并实施后更新正常 loader、operator 使用、Q 默认关闭、账号非敏感 readiness、预算不足与 GET 恢复。DocuS 的唯一共享账、架构和最终裁定仍由主控串行同步；本窗不改共享文档、不占新 TASK/R/CHG、不执行 Git 发布。001—014、R01/R02 表／角色／profile、旧结果和固定 renderer 本方案均无修改需要；若实施发现必须改 DDL／公开写接口等超出本合同，保存精确差异后交主控采用，不能静默扩模型。

### D2. 最小而充分的新增验证

第一批是纯类型／合成 transport 与本机文件故障，第二批是真实 PG 零外发组合，第三批是受影响最终 bundle；在完整稳定候选上交原独审窗集中复核。实际收费前没有独审有效结论就关闭。以下名称为应新增的方法合同，不是已存在／已运行的方法。

1. 新 `backend/tests/test_task119_outbound_approvals.py`：`test_two_dependent_requests_keep_one_immutable_root`，实际 accept／prepare／approve／原键 continue 两次，第二次使用第一笔真实持久 record 身份，最低 transport 计一次每请求；`test_unapproved_answer_memory_title_history_and_foreign_parent_never_launch`，覆盖完整正文与 metadata 来源，不只改 catalog；`test_pending_approval_is_unclaimed_and_reserves_nothing`，逐 GET 证明 accepted 尚未启动及四账零变化；`test_claim_commit_ack_loss_and_result_commit_ack_loss_read_original_only`，分清 launch 与正文 COMMIT 丢确认；`test_approval_change_before_after_admit_and_mark_retains_original_reserve`，明确零发送／NOT_SENT／UNKNOWN；`test_journal_tail_identity_artifact_or_instance_mismatch_closes_gate`；`test_v1_exact_approval_v3_and_original_v4_compatibility`。只用最低 transport，不向供方发未批准／恶意内容。

2. 对继承的 `test_step018_audit_repairs.py`，复用 S08 已通过的 v1 摘要、完整消息反例、admit/mark 变更、空 model_requests、loader/wire 和 public identity 原件。新增 v2 断言只核新边界；不复制成第二套全量旧测试。复用 `test_step018_retrieval_pg.py` 和 `test_step018_profiles_pg.py` 的既有检索、旧 profile／升级成果，但不能把名字或其有限通过当本轮新 PG 组合已证。

3. 新真实 PG 方法 `test_pg_two_provider_original_roster_persistent_commit`：所有准备／seed 均在一个明确 TESTONLY normal 数据库、其原控制根和固定三活动内；model 与 embedding 的真实生产准入均不得 Proxy SUM、替换 connection、Python 内存累加或 mock advisory。保存真实两个 PG backend PID、advisory 竞争观测、原查询参数／roster 三行、activities requests/cost 前后、activity_operations 的 admission/provider/model/reserve/state、007 或明确无结果、事务 COMMIT 后新连接回读。最低 transport 的 is_external=false 不等于跳准入；要保留有效的 TESTONLY 根／proof 和全部生产检查。

4. 临界 fixture 必须是合法可达账：在 A1 39、A2 24、A3 16 共 79 次／19750000 时，两 provider 的新 intent 都放在尚余一次的 A1，使用同一个真实有效 executor lease、不同合法 operation／批准。不能声称“不同两活动都余一次且全局已79”可达，因为三活动分额和为80。通过原领域 freeze／claim 形成可并存的 model 与检索命令，不改 status 或 reserve 造数。并发生产 admit 后恰至多一笔新 COMMIT、输方零发送；最终只读连接看到 SUM≤80／20000000，成功方 reserve=250000。共同 policy lease 允许并发，不能在外层串行调用后冒充 PG 锁竞争。79 笔基线应经真实生产 admission 持久累加（或使用已有可信同等逐笔原件的合成 fixture）；不以手改总计充当真实预扣。

5. 新 `test_pg_unknown_reopen_and_instance_copy_never_reset`：赢家在最低 transport 中可能已送后 timeout，原 unknown＋reserve 留账，停止准确 owned 后同库重开，GET 不发第二次；新 admission 仍拒。确定未送与已准入同样不退 reserve。另对不同 normal instance／逻辑 DB、另一个 control_id、旧 v1／另一 grant、原 frozen／restored_readonly 入口，证明新准入为零，且原总计不降；私有见证未结／领先时只读对账。固定 0.25 下次数与费用同增，不能伪造 79／20元 的不可达单独费用边界；对真实临界点同时核两值及各拒绝式。

6. PG fixture 数据与真实收费 Q 资料彻底分离：预算 fixture 达 80 后保留它及全部失败，不删行、不归零、不复用该库作真实 Q。真实 Q 的首次部署另有明确 instance/control 绑定和全新有限 synthetic roster，批准前证明该真实许可 provider/费用仍为0；不能把一次试跑的真实费用挪去 TESTONLY 账。若已有任何真实 Q 已用，真实 Q 必须复用其原 PG/root，只补剩余，不能再开库。当前主控确认 Q 未启用，没有可恢复付费事实。

7. 最终 bundle 最小传播：同一个编译候选核一条教学和一条面试“query 已提交→model 等待→本机批准→原键显式继续”的完整链；重开只 GET、local draft 不丢；未批准文字零 model POST/零外发；owner/view/head/namespace 在批准等待期间改变则旧继续拒绝。learning intent 和 HTML 各核一次新等待状态与原键恢复，v1 原兼容不重做全面 UI。浏览器只连接获准本机 synthetic API，不对真实 provider 做安全故障。已有供应商告知／权限门／PDF／readonly／宿主 32 边界等未变原件直接继承。

### D3. 资源、审计和正式启用顺序

下一工程卡可在用户既有授权内一次批准纯合成实施及上述零外发验证。建议最小资源安排为一个新 PG 容器／卷，预算 fixture normal DB 及其新控制根；真实 Q normal DB／控制根只在实际启用条件具备时首次创建，可用同一新 PG 服务的第二个逻辑 DB，不能从旧六对象复制成可写源。具体 CID、卷、端口、DB/instance/root 身份、开始／持有／停止次数、内存门、SUP/API/Browser/build 配额必须由下一卡精确给定，本报告不借旧余量。若平台额度／内存不达真实门，只继续离线工作，停止自有资源后交回，不绕审批。

先完成整个稳定新协议、真实 PG 零外发组合及受影响 UI，保留所有 FAIL／UNKNOWN／费用与累计账，立即完成精确 StopProof，再交原 TASK-118 独审归属增量核：新增授权边界、无第二金融权威、原键等待、失效锁序、实际 roster COMMIT、完整请求来源、身份与恢复关闭、最终 bundle 传播。独审不重开 D01—D04 或重做未变七族；工程窗不能自签新安全门。只要新协议或任一门未证，Q 保持冻结，普通已证 S 不受牵连。

真正付费前由主控核齐：具体采用决定、实际 source/input/模板根及新 normal 绑定、两 provider 当前官方与账号适用事实、严格返回身份、含税币种／token／framing／reasoning 上界、精确剩余调用矩阵与预算可容纳、独审结果 hash、正常 secret loader 非敏感 readiness。只有主控明确启用回执与同一 grant/root/price/instance/roster 一致，才写未来真实 valid_from=T0、valid_until≤T0+72小时；每活动原24小时、3600运行秒、finite_calculate≤8、预览3次／180秒及单次30—60秒等仍沿采用原限额。receipt/hash 应对一个无自引用的规范激活对象计算，不把包含自身 hash 的整张回执拿来循环绑定：先固定不含 grant hash 的 activation body，再在 grant 中引用其 hash，部署绑定单另外并列两者摘要。

本轮公开核验不是账号许可／启用回执。模型替换和矩阵缺口尚未被批准；即使下轮纯合成实现及独审通过，也不能顺手启用 Q。未来真服务只验证冻结 rubric 的支持／反例／部分认可／不足／冲突／自报和当前解释至 L10；从已 COMMIT 处 GET 继续，实际通过和失败逐例记，长期学习效果不冒通过。之后原独审窗只增量看语义及实际改动，再由主控裁定 STEP018/019，STEP020 后续本人交付门保持。

### D4. 最小采用包及交回边界

合并差异见 [adoption-package.md](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-119/design/adoption-package.md)。主控可在既有 synthetic AP1/AP2 开发授权内直接采用原键等待、私有逐请求批准、配置/wire/显示的实现细化，并发一个连续零外发工程合同；这些不要求用户再次批准原80／20。候选模型改变及若需追加／重分配额度，属于真正新决定，应把本报告完整差异一次合并交有权主体裁定，不先执行、不分散重复问。预算不足时仍可完成前置实现与独审，不能签 Q 整体启用。

采用后最低变化为零 DDL、同固定 roster、同原 PG 费用事务、v3/v4兼容、private ControlHub 精确批准及当前模型候选的明确决定；没有签名平台、任意网页批准端点、队列或 watcher。若不采用本方案，现 v1 仅支持预知完整请求，后续依赖链继续阻断；保留原成果和只读数据，不用宽松摘要模板充通。回滚为关 Q、留账及新事件，旧模型停服不作 fallback。

### D5. 本轮执行事实与结果

首工具 UTC 2026-10-18T06:45:16.4903015Z，host QPC995761626509／frequency10000000；48小时日历止2026-10-20T06:45:16.4903015Z，最后1200秒仅保存。本轮没有跨中断活动硬门，UTC 日历跨度不能冒连续工作／CPU；元数据单批及累计收据见 [execution-receipt.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-119/design/execution-receipt.json)。公开抓取失败、metadata 路径猜测／无匹配及输出截断保留为本轮设计读取事实，不归为产品缺陷，不改 TASK-117 的原81条失败或旧计数。

本轮只有只读定向文本／hash／JSON 元数据及获准官方文档请求；产品 import、测试、compile/build、PG/SQL/Docker、业务 Job/API/Browser、实际 provider、费用、Git 写全部为0。没有新开持有型产品资源，因而没有本轮待清理产品进程／端口／PG；这不声称旧六 CID 当前实时停止。没有读取实际环境值、私配、key、账号或运行旧 runner，没有修改任务卡、产品、SQL、dist、DocuS、历史原件或公共库。

本轮只做一次最终文档一致性核对：输入未漂移、A—D 与机器清单、81次／分额／保留门、四条未执行轨迹、引用和输出路径、禁止星号／表格的文档约束及本轮产物身份，结果保存在 [document-consistency.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-119/design/document-consistency.json)。它不证明协议实现、PG 行为或任何新产品 PASS。真实结果为 TASK-119 设计包已完成，Q 启用仍受上述明确缺口关闭；主控按唯一共享账接续采用与实施，本窗没有代签最终验收。
