# TASK-091 / R-085 修正轮01 当前有效合同

2026-09-30，Asia/Shanghai。本轮为第一次合并修正，依据TASK-091-work-decision的K1—K5。本卡只交只读设计，不实施、运行或独立审计。完整A—D已在本轮置顶保存，K1—K5合并修订完成，建议交编排核证；首轮全文在文末原字节保留；当前有效建议以下方修正轮01为准，历史中进程内执行、旧D1/D2及失败轨迹等已撤销。编排最终验收仍待其裁定。

项目根D:/shspic/project_NO3_RetroLume-agent；需求v1.1、架构v0.58、执行v1.79，task_model，V4.0 CHG-0003。Git基础45951501d2741630a229762d6b2d3f4b34d7f702及原未提交成果保留。根AGENTS与锁定公共源见DocuN/evidence/v4-migration-20260930/rules-snapshot.json。本轮补读指定WORK第2、5、6、8、9章，不取得正式文档、产品、测试或资源写权。

实际接收为Codex桌面当前主窗口，延续此前TASK090上下文；首轮报告记载其执行者为WorkBuddy，不冒称本窗口就是该会话或已核实其不可用。用户实际将本轮合同转交此窗口是当前接续依据，原编号、55分钟声明投入及失败历史保留。A+是增强资源安排，不是已核实的具体型号。没有委派新Agent或使用090审计者设计本轮。

## A 事实地图与最小影响

A1 现有工具是capabilities/tools.py的finite_calculate。CalculationArguments只允许operation、left、right，拒绝bool、非有限数、额外字段及绝对值超过1e12；五种原运算不变，幂指数为-12..12整数，除零及零负幂拒绝。ToolRegistry.plan要求有界JSON参数，MAX_ARGUMENT_BYTES=2048；execute用Decimal精度50，结果有限且绝对值不超过1e18，返回十进制字符串。它是显式执行函数；生产工具计划链没有自动调用它。

A2 gateway.call经admit→mark_dispatch_started→transport.send→解析→record。工具建议通过ToolRegistry.plan返回TOOL_PLAN；_finish只记received元数据，没有业务正文、不执行工具。模型请求一次可建议最多8项，不能把一次模型请求计数当作多个实际工具动作的计数。ToolCallPlan虽frozen，arguments是Mapping，内容并非深层不可变。AdmissionPermit只有admission_id、operation_id、executor_id，确实没有参数摘要。

A3 repository.admit预留requests_reserved和cost_reserved_microunits，allowed_tools只是白名单。活动无工具计数。_locked_operation使用admission定位，再来源排序锁→活动锁及_verify_scope_hint→操作锁；mark只允许当前reserved且门未关闭。record_outcome先严格比终态与正文，再判新写资格；UNKNOWN可作为失效诊断，reserved不能新记成功正文。终态同值无写返回ALREADY_PRESENT；已received无正文不能补写，异文冲突不能覆盖。

A4 002中provider、configured_model、request_bytes、max_output_tokens、reserved_cost_microunits原为非空，成本为正；prompt_tokens、completion_tokens、returned_model、remote_request_id、finish_reason及response_bytes本来可空。007显式不要求activities为空，不回填旧正文、不支持重复执行天然幂等。首轮“token计数均NOT NULL”和“008首个非空迁移”均不成立。

A5 G3 read_committed_result/list_committed_results同SQL判资格并抑制失效正文，当前CommittedResultSnapshot无kind。service.continue_from_result把COMMITTED_CURRENT正文放assistant，再设allowed_tools为空；admit锁内核父正文却没有kind判断。因此互斥input_result与allowed_tools不足以阻止工具正文被消费。

A6 D3实际由launcher→SUP→固定worker负责。session.run_once在原互斥下核单机部署声明、running_owner_session_id、旧租约与来源，再打开旧命名Job；只有确认不存在或已终止且树零并关闭句柄，才允许claim接续。claim提交丢响应不spawn/重claim。worker先悬停入Job后Resume；正常树零、退出码及回执校验后，job.close→begin_window_close→settle。异常失败保留全额时间预扣。租约过期、无子进程或DB拒写均不能证明服务进程计算已停止。

A7 已通过证据引用DocuN/results/TASK-090-final-acceptance.md、Ndocu/results/TASK-090-independent-audit.md的G节和原real-03/offline-05；不重采。工具计划相关测试真实ID包括test_capabilities.CapabilitiesTests.test_tool_suggestion_is_validated_and_only_returns_plan、test_unknown_unauthorized_and_extra_tool_fields_are_rejected；test_worker_one_call.OneCallTests.test_tool_plan_never_executes；test_activity_results中的test_tool_plan_and_failure_never_fake_payload_success。读到测试源码本身只算B级，已有真实运行结论按对应旧原件范围引用，不能用测试函数存在代替执行。

最小新增是两列活动账、操作kind与工具标识摘要、独立工具意图/凭证、已有监督链的固定one_tool分支、共表结果的类型投影与模型父准入拒绝。无需第二套结果表、父子图、通用插件、网络工具或第三监督层；旧模型发送和有限计算语义保持。

## B 唯一推荐实施合同 全部尚未实施

### B1 权限与次数单位

只允许受信调用方一次显式execute_tool_action，工具限finite_calculate一项。授权来自已持久的活动allowed_tools与有限max_tool_calls，以及受信调用方明确新动作。模型计划、资料、父正文、call_id、摘要、协议字段均不是授权。可以执行调用方自行明确构造的合法计划，不强制绑定未持久化的模型TOOL_PLAN为父；选择的权威来源就是该显式内部动作，不增加假父图。

次数单位为一次成功持久准入的工具尝试。admit_tool_operation提交操作reserved与tools_reserved+1的同一事务即计一次，包含提交丢响应或准入后未执行的保守耗用，绝不是“execute已经调用”的保证。一动作一工具，不批量、不自动多轮；不同新键须另一次显式意图。成功工具动作不增加模型请求和模型成本，但独立占用既有时间窗口。原计数、已用次数与时间都不因读取、重启、取消或scope变更而复活。

max_tool_calls严格int、拒绝bool/字符串，0..2147483647，None表示未配置，0表示明确禁用。tools_reserved严格累计非负INTEGER，永不自动减一。未配置必须已用0；已配置必须已用不超过上限。无有限默认、无自动扩容。allowed_tools非空但max_tool_calls=None的旧活动仍可按原模型路径产生建议，工具实际执行拒绝，不破坏旧计划调用方。

### B2 008拟议持久约束与迁移

建议文件backend/migrations/008_activity_tool_budget.sql。以下是DDL目标合同，未授权生成/执行产品迁移。001—007只读。原002模型行逻辑加kind='model'，旧活动max_tool_calls=NULL及tools_reserved=0；这是新增字段对旧行的解释，不声称旧行全部字节无变化或ALTER零扫描。

activities增加max_tool_calls INTEGER NULL和tools_reserved INTEGER NOT NULL DEFAULT 0，具名CHECK精确定义如下。

```sql
CHECK (max_tool_calls IS NULL OR max_tool_calls >= 0)
CHECK (tools_reserved >= 0)
CHECK (
  (max_tool_calls IS NULL AND tools_reserved = 0)
  OR
  (max_tool_calls IS NOT NULL
   AND tools_reserved BETWEEN 0 AND max_tool_calls)
)
```

INTEGER自身限制上界。锁内先比较上限，再+1；INT_MAX已满时拒绝，不先算会溢出的加法。允许旧白名单不空而额度未配置，不添加与allowed_tools非空等价的约束；零额度只禁用执行，白名单仍可供旧模型计划校验。不得事后把max置NULL却保留已用正数，CHECK会拒绝；本切片只在新建活动显式配置，不新增运行时扩大额度接口。

activity_operations增加kind TEXT NOT NULL DEFAULT 'model'、arguments_sha256 TEXT NULL、tool_call_id VARCHAR(128) NULL；kind仅model/tool。工具名复用tool_names的一项数组，不多加同义tool_name列。放宽provider/configured_model/request_bytes/max_output_tokens的NOT NULL，保留其原正数CHECK及字段长度；它们的可空性由以下总条件收紧。reserved_cost_microunits保留NOT NULL，替换原“必须大于0”单列CHECK为以下条件的一部分。

```sql
CHECK (kind IN ('model', 'tool'))
CHECK (
 (kind = 'model'
  AND provider IS NOT NULL AND configured_model IS NOT NULL
  AND request_bytes IS NOT NULL AND request_bytes > 0
  AND max_output_tokens IS NOT NULL AND max_output_tokens > 0
  AND reserved_cost_microunits > 0
  AND arguments_sha256 IS NULL AND tool_call_id IS NULL)
 OR
 (kind = 'tool'
  AND provider IS NULL AND configured_model IS NULL
  AND request_bytes IS NULL AND max_output_tokens IS NULL
  AND reserved_cost_microunits = 0
  AND tool_names = ARRAY['finite_calculate']::VARCHAR(64)[]
  AND arguments_sha256 IS NOT NULL
  AND octet_length(arguments_sha256) = 64
  AND arguments_sha256 ~ '^[0-9a-f]{64}$'
  AND tool_call_id IS NOT NULL
  AND char_length(tool_call_id) BETWEEN 1 AND 128
  AND tool_call_id !~ '[^A-Za-z0-9._:/-]'
  AND remote_request_id IS NULL AND returned_model IS NULL
  AND finish_reason IS NULL AND prompt_tokens IS NULL
  AND completion_tokens IS NULL AND response_bytes IS NULL)
)
```

显式IS NOT NULL防止SQL三值逻辑放过不完整工具行。模型原可空返回/usage字段不改为非空，继续原取值校验。工具没有provider/model/token/remote元数据，不以虚假模型、0 token或伪费用占位；本地正文长度由results的octet_length约束，不复用模型response_bytes统计。tool_call_id采用既有操作键式有限ASCII域，仅新工具动作严格拒绝不合域ID，旧模型计划ID契约不改。

原state/disposition、recorded_at及dispatch_started_at三个状态约束、主键、admission唯一和恢复索引保留。007表零新增列，主表kind通过JOIN权威投影；原FK、正文大小、格式、hash与冗余绑定仍生效。工具成功只存text封套里的有界有限十进制字符串，工具失败/UNKNOWN无新正文。

迁移先在单事务内核001—007基线、无008痕迹、当前schema及旧行约束符合预期，再ALTER及验证完整CHECK，最后COMMIT。旧成本CHECK的真实名称从pg_constraint按目标表、列及原正值表达式唯一核实，引用安全标识符后精确DROP；数量/定义不符立即回滚，不猜名、不宽泛DROP。所有新CHECK当次验证，不留NOT VALID逃逸。重复008应报错并整体回滚，不宣称天然幂等。

新空合成库001—008；非空合成库先用001—007合法造旧model/received-with/without-payload/unknown行，再单独008，验证旧结果/预算兼容。不得对非空库重放004/005或手工更新历史正文；不授默认工具额度、不伪造历史调用。DDL可能扫描、锁表或按数据库版本改变存储，未来实现记录真实锁与时长，不能从DEFAULT语法保证零重写。事务失败回滚旧schema；上线前后若008已COMMIT且工具行已用，不承诺反向DROP回到007可无损，保留备份及向前修正门。以上合成策略绝不授权用户库执行。

### B3 参数快照、工具意图与真实凭证

选定新增独立ToolExecutionInput、ToolIntent、ToolAdmissionPermit，不给原AdmissionPermit虚构字段。旧AdmissionIntent、AdmissionPermit、模型Ledger接口原签名及三个凭证字段保持；工具方法使用不同类型，并在数据库锁内复核kind，不能用重造的旧三字段model凭证操作tool行。

ToolExecutionInput候选字段为operation_id、call_id、name、arguments_json、arguments_sha256，均为严格有限字符串，冻结且arguments_json隐藏repr。operation_id沿既有有限ASCII键，call_id同域1..128，name必须finite_calculate。ToolIntent包含严格CallContext及该input；ToolAdmissionPermit候选字段为admission_id、operation_id、executor_id、activity_id、execution_generation、scope_revision、tool_name、tool_call_id、arguments_sha256。工具名/ID/摘要与DB行一致才可使用；其中kind由独立类型及DB权威限定tool，不靠客户端自称。全部签名是待批准新增，不是当前函数。

受信service在入口只读取调用方ToolCallPlan.arguments一次到私有浅拷贝。Schema只允许三个不可变标量，拒绝嵌套、多余字段与非法类型后，用CalculationArguments的原校验与model_dump得到私有值。Mapping在拷贝中变化或抛错即invalid_input；不能直接继续使用调用方Mapping。规范参数定义为对校验后对象json.dumps(sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)所得UTF8；长度1..2048，SHA256为64位小写hex。保留int/float域的校验后表示，不声称数学等价的1与1.0必同摘要，不引入数值舍入规则。

将字节解为严格UTF8字符串作为不可变arguments_json，并在每个解码端重新解析、原Schema校验、规范编码，要求重新编码逐字节等于输入且hash相等；拒绝重复JSON键、非有限常量、额外字段、非规范字节、布尔revision/G及身份不一致。输入对象虽然冻结，to_wire/from_wire仍完整验证，不能用dataclass构造或model_copy绕正常边界。

admit_tool将这个计算出来的摘要、call_id和单项tool_names写DB，返回上述专用凭证。mark_tool_started(permit,call)及record_tool_outcome(permit,call,outcome)都重新计算call的摘要，对齐凭证和锁内DB的完整身份及参数元数据。实际execute只从同一不可变arguments_json解出的worker私有值重建ToolCallPlan，不再读取外部原Mapping，也不执行从别处拿来的plan。预扣、最后资格、执行、提交共享同一参数快照；把A参数预扣后换成B参数将被拒绝。

数据库只持久参数摘要，参数字节由本次受控映射/worker私有内存传递，不另存计划正文。崩溃后参数内存丢失没有自动再执行用途，故不必为恢复执行增加参数表；读结果不需要取回参数。安全边界仍是内部受信同用户进程，不承诺摘要能抵御恶意同用户重新计算摘要并滥用受信接口。

### B4 短事务与至多一次执行资格

候选admit_tool_operation(intent: ToolIntent) -> ToolAdmissionPermit采用来源排序锁→活动锁→完整提示复核→同键操作锁。核活动running、未cancel/expire、非空有效来源、context活动/executor/G/scope及有效租约、dispatch门、工具白名单和显式额度；不查模型provider白名单、不预留模型请求/费用。两账互相独立，工具动作只消耗工具次数及时间；模型TOOL_PLAN已消耗其自己的模型准入。达到相应额度拒绝相应动作，活动取消、到期及时间不足统一阻止新窗口。

操作键仍是(activity_id,operation_id)，模型/工具共一个键空间。若已占用，先按kind、单项工具名、call_id、摘要判断operation_key_conflict或tool_input_conflict；同一工具身份也只返回operation_already_exists拒绝，不返回第二个可执行凭证。服务可以在同键且完整工具身份相同时只读返回已知事实；UNKNOWN、无正文、暂不可读都不启动新监督，不生成替代键。不同新键只能来自之后单独明确意图，不自动重算旧未知动作。

全部通过才同事务INSERT kind=tool、state=reserved、成本0及参数标识，UPDATE tools_reserved+1，COMMIT确认后返回唯一凭证；任一回滚无新行/工具预扣。它不是模型admit的改名复用，校验集合与模型字段不同。admit丢响应不假定DB无行，也不再次admit或重新执行。

mark_tool_started在同一锁序核凭证/参数/持久kind及当前范围代次与门，reserved→dispatched，只在COMMIT获确认后允许执行一次。同一凭证第二次mark即拒绝；不返回ALREADY_STARTED给再次执行。资格提交与实际运算存在时间缝，取消或scope变更仍可能发生在mark之后；不能承诺此时零次运算，但旧资格的新正文提交被拒绝。并发同键是至多一个获准者、至多一次执行资格；只有获准者未崩溃且成功到达execute的正常样本才可断言实际恰一次。

ControlledToolExecutor候选纯内部适配器实现call(context,ToolExecutionInput)，按规范验证→admit_tool→mark_tool→ToolRegistry.execute→record_tool执行一项。使用ClosingCallGate已有Any接口包住完整call，令牌从admit前持有到record返回；不改gate主体，不把原始执行器交给外部调用者。execute严格在事务之外，没有网络、文件、命令或新子进程。

record_tool_outcome使用专用凭证与参数快照，复用G3规范正文和终态等值原子提交核心。工具行所有模型元数据保持NULL。成功LedgerOutcome(RECEIVED,payload三元组)，text value为原execute输出；确定计算失败为RECEIVED + tool_execution_failed、无正文，不用not_sent假装未尝试。失效后的新成功正文拒绝；仅已注册凭证可按原纪律写UNKNOWN诊断，不能在拒绝admit后伪造操作行。

模型mark_dispatch_started/record_outcome也必须补锁内kind=model校验；专用工具方法只接受tool。终态严格幂等先于当前资格拒绝，类型与参数身份校验先于幂等。跨kind凭证、同键异文、旧received无正文补正文均拒绝。只在已提交的严格同值终态下ALREADY_PRESENT，无正文未提交崩溃不满足这一前提。

### B5 固定launcher/SUP/worker工具分支

唯一运行形态为service.execute_tool_action→run_one_tool→既有run_supervised_window→SingleWindowSupervisor.run_once→原固定worker_main的新one_tool。WorkerCommand只增加固定枚举one_tool，解释器/模块/工作目录仍固定，argv仅该枚举及校验过的mapping名；不得传任意命令或工具函数指针。服务不claim、execute、close或settle，不在未纳入Job的进程计算，不添加监督层。

所有工具配置、input规范字节、请求版本、身份、SessionConfig及request_timeout_seconds有限正数且<=120在launcher/SUP claim之前早拒。继续既有W>startup_limit+request_timeout+stop_grace，manager余量与DB时限规则，tool整体call包含admit/mark/execute/record。SUP claim给出W_eff后仍应用原partial_window_too_small及startup检查，不为了工具放开较短余额。claim响应未知不spawn、不重claim，时间预扣是否已发生需只读核事实。

SUP保持原互斥、旧Job恢复身份、来源及租约前提，owner_session_id由SUP当前Windows会话提供，不来自服务传参。使用同(activity,G)命名Job、先悬停/归入Job后Resume，工具代码仅在该受控worker运行。stop_ns沿原t0/W_eff/manager及停止预留计算；CPU同步执行不能只靠asyncio.timeout，必须由SUP在截止终止自有Job并确认整树零。计算很快或租约失效都不替代硬停止证明。

正常顺序是worker完整工具call→本地gate关闭/活跃归零→worker退出→SUP确认树零、退出0及工具回执→关闭exchange及自身Job/进程句柄→begin_window_close→settle。时间结算与业务成败分开：有效UNKNOWN业务回执也可在工作已停止后按真实C结算；确定业务失败不是退款工具次数的理由。树未知、非零退出、回执不可信、句柄关闭失败或无法确认收尾时，沿原D3拒绝部分结算、保留全额R及cleanup/未知事实，不能把received正文当树零证明。

DB取消先使旧资格失效并把R全额折叠入S；它不是停止证明。工具worker仍由既有Job截止/管理期限收尾，不新增瞬时跨进程撤回承诺。cancel已折叠后不额外settle、不再加S；scope修订本身不强杀、不结算，也不改R/S/工具账。异步service沿090的shield等待唯一有界监督线程退出后才传播调用方取消，不能把取消async任务当Job已停。旧Job不明或会话不匹配的恢复拒绝逻辑原样保留。

### B6 版本化工具协议与兼容

模型/idle保留当前外2、模型内3及原精确字段集，不借工具升级重写其回执。新工具动作选定外层协议3、SUP↔worker工具协议4，严格按command区分，不协商降级。旧SUP收到外3拒绝且无claim；新SUP不把outer2伪装tool。旧worker若收到one_tool会拒绝且没有工具准入/执行，但新SUP可能已经claim时间，不能宣称所有混用都零时间预扣。部署应统一切换该固定后端源码，混用只失败关闭，不重发。

候选工具外请求精确字段protocol、mapping_name、activity_id、executor_id、run_tag、deadline_ns、command、config、ledger、tool_action，不带one_call/model service/API key。tool_action仅ToolExecutionInput规范字段。工具内请求精确protocol=4、call、ledger、context、run_tag、stop_ns、call_seconds。context的activity/executor/operation/G/scope取SUP实际lease；各跳重校与外层活动/op及call一致，不能用调用方假代次认领。ledger沿现有受控映射四字段，不在argv/日志输出DSN。

规范参数<=2048字节，整体业务数据<=131072且必须满足现有pack_frame槽容量扣头后的更小上限，使用原NamedMapping封帧与身份纪律，未知/额外字段拒绝。protocol须严格int，身份有限ASCII/规范UUID、G/scope正整数、hash64小写，call_seconds有限<=120且剩余stop时间符合原保护余量。任一不能满足即失败关闭，不改supervisor_ipc容量或安全主体。

工具回执协议4仅context、run_tag、business_commit和result；result精确包含kind=tool、name、call_id、arguments_sha256、status、error_code、payload_sha256，不带参数、结果正文、tool_plans、provider或usage。身份/参数与请求、DB凭证绑定一致。SUCCEEDED必须record已确认并有合法结果hash，business_commit=committed；record_denied/record_unconfirmed必须UNKNOWN+unconfirmed，无成功hash；其余本次未携带成功提交确认为not_committed，不能据此推DB无历史。不接受TOOL_PLAN作为工具执行回执。

工具外响应仍由原launcher接收其创建的SUP，protocol=3，沿run_tag/activity/outcome身份格式。SessionOutcome候选仅新增tool_receipt默认None且repr隐藏，model_receipt在tool路径必须None。外2序列化/解码明确使用冻结的旧字段集、排除新tool_receipt并补默认，外3使用包含tool_receipt的精确集合；禁止依赖动态fields(SessionOutcome)同时接收两个版本导致旧2多字段/缺字段。工具回执在SUP和launcher逐跳复核。模型路径的provider/model及原协议3校验维持原样。

### B7 持久类型隔离及读取

CommittedResultSnapshot候选在尾部增加kind、tool_call_id、arguments_sha256、tool_names等轻量元数据；NO_OPERATION的kind=None，不伪造model。read/list从同一权威operation JOIN投影，不让调用方输入kind，参数正文不投影。合法kind=model/tool都可按原G3条件只读；来源/范围失效先在SQL抑制正文，再返回状态，取消历史仅条件仍有效时展示。record_tool_outcome对新工具正文另核text格式、有限有界十进制value及原精度50规范字符串；read/list在SQL资格成立且kind=tool时同样复查这一工具结果语义，非法JSON形态/非数值工具正文视完整性错误，不将同表的model json许可自动给tool。这属于应用层kind条件校验，007的通用格式CHECK不伪装成跨表工具约束。结果与操作admission/G/scope、规范hash和payload三字段继续真实校验，未知类型失败关闭。

continue_from_result在COMMITTED_CURRENT父之后还必须snapshot.kind=='model'；tool返回result_kind_not_consumable且零监督。仓储admit锁到父行后也必须parent.kind=='model'，再做其余绑定/hash/当前资格，并在任何新模型行及次数/费用预留之前拒绝工具父。ResultConsumptionRef结构维持090原样，不添加可冒充授权的client-kind字段；gateway的原input_result/allowed_tools互斥继续。

反例为真实received tool正文T当前有效、模型请求allowed_tools为空，直接构造activity一致、scope/hash正确的ResultConsumptionRef(T)，绕过service调用gateway或ledger.admit，仍由父行kind拒绝。对照model父P相同结构正常。这是本切片工具→模型隔离的实际边界；任意内部受信调用者手抄字符串普通模型消息并不被该引用机制承诺拦截，更不声称可抵御恶意同用户进程。

工具输出仍低信任，只供read/list，不自动接模型、不执行工具计划循环。确定性不赋予重算豁免，scope读快照也不授之后新资格。这些不扩围规则沿已批准边界，不重新作为用户D3/D4选择。

### B8 失败事实、恢复及有限重试

以下均为合同，不是已运行故障测试。tools_reserved在准入提交后始终保留，read/resume不触发动作。每次claim、工具admit、mark、record及settle按各自事务事实讨论，不用一个unknown笼统推出所有步骤未执行。

1. 纯参数/未知工具/协议/配置非法在launcher/SUP早拒，无claim、工具操作或execute；工具DB白名单/限额/来源的权威拒绝发生在已claim的worker时，事务回滚无工具/模型次数及费用预扣，但已有窗口管理耗时仍按D3处理。不得把所有admit拒绝说成时间零变化；也不得将其合法时间记账叫工具扣次。

2. admit_tool DB故障可能未提交，也可能reserved与计数已COMMIT而凭证响应丢失。本次没有凭证确认，不mark、不execute，返回admission_unconfirmed/UNKNOWN，查同键事实；不能推DB无行，不隐式重新admit。拒绝原因仅返回/记录有限脱敏code/run_tag，admit回滚没有操作行可记录，不能冒称有持久拒绝条目。

3. 已确认reserved但尚未mark，worker终止、关门、取消或资格失效：execute尚未获许可，工具额度已用，不能退款。活跃租约不由其他进程随意收敛；符合recover_unknown条件或旧G的recover_obsolete_operations才置UNKNOWN，无正文。known owner可一次有界写UNKNOWN诊断，不生成新操作；这不是not_sent退款路径。

4. mark数据库失败/响应丢失：持久行可能reserved或dispatched，worker必须没有execute调用，返回mark_unconfirmed/UNKNOWN；不重试mark获取执行资格，即使后来查到dispatched也不能恢复execute。仅事实读取和原保守收敛。mark明确回滚的scope/取消拒绝与不知commit结果的AdmissionUnavailable分开。

5. mark确认后execute发生，record前崩溃或record事务未COMMIT：dispatched、无results（以后符合条件收敛unknown），工具已用、可能实际算过。没有成功终态，不得以同record必得ALREADY_PRESENT；恢复进程不能凭未知补写成功，未知不自动重算。若纯计算明确抛ToolValidationError且worker仍活着，写received/tool_execution_failed无正文，COMMIT确认才是已记确定失败；错误原文不进回执。

6. execute已发生后record DB不可用：返回record_unconfirmed/UNKNOWN+unconfirmed，不说“未执行”，也不把本地答案当持久成功。COMMIT是否成功未知时不自动覆写UNKNOWN或重复提交循环，之后只读同键。若新成功record因scope/取消确定拒绝且事务回滚，可用同一已登记凭证至多一次有界UNKNOWN诊断；诊断再失败保留未决，原门/预算不放开。

7. record已COMMIT、响应丢失与第5项独立：操作received与正文同在，resume可确认committed_current或当前已失效/取消历史。同凭证、同参数身份、完全同终态/正文的直接仓储确认重试可ALREADY_PRESENT，无写；异文或原received无正文后补正文必须拒绝。本切片控制器默认只读恢复，不自动record重试。将该严格幂等契约作为测试，不赋恢复进程从丢失内存重建答案的权利。

8. begin_window_close提交丢响应：不确认关门就不进入新settle，不重新计算或执行，按原失败路径报告并保留时间未知/预扣。现有方法的ALREADY_CLOSED可由显式同身份核对确认，工具路径不另加无限重试或改变D3。

9. settle第一调用提交前失败与提交后丢响应分开。SUP只在剩余manager期限内按原实现相同G/W/elapsed（同C）有限重试一次；未提交可完成一次结算，已提交返回ALREADY_SETTLED不再次加S/减R。若两次均未知，settled/R/pending_fold字段为None，不能推仍未结算；下次按持久pending/R0或旧running事实处理。更旧G不承诺历史重放，相同G不同C拒绝。cancel已折叠R后新settle拒绝，不另结算。

10. scope CAS在admit取提示前已完成：提示是新集合，context却旧revision，明确scope_changed拒绝、工具预扣零。另一真实前提是旧集合提示已读但尚未锁，CAS提交不同集合后该事务继续，_verify_scope_hint抛ScopeConflict整事务回滚。这两个场景不能要求同一异常。admit已提交后范围变化，mark拒绝；mark后变化允许实际运算可能已发生，但新正文record拒绝并保守收敛，不退工具预扣。只读旧scope正文被抑制。

11. cancel、来源失效、deadline或租约到期均阻止新资格；停止/必要诊断不追加来源有效性门。旧G晚到仅UNKNOWN诊断或已存在严格同值的无写确认，不取得新正文/执行资格；恢复SQL按reserved/dispatched处理两种kind，不改计数/模型元数据。recover_unknown仅账面收敛，不能伪装成树零证明。

12. 同键并发至多一工具准入、至多一mark资格。获准者崩溃可实际执行零次；正常获准者样本执行一次。op键被模型占用、同工具键改名/call_id/参数均明确冲突，无新工具扣次。max为NULL/0/已满或INT_MAX已满拒绝，跨连接重启仍同值。所有候选错误码均为有限allowlist，不暴露参数、正文、DSN或异常repr。

### B9 内部接口与完整实施文件清单

现有真实签名仍是AdmissionLedger.admit(intent)、mark_dispatch_started(AdmissionPermit)、record_outcome(AdmissionPermit,LedgerOutcome)，ActivityService.continue_from_result及launcher.run_supervised_window(...,one_call=None)。以下是唯一候选签名，不是已存在函数。

```text
ActivityService.execute_tool_action(activity_id, operation_id, plan: ToolCallPlan,
                                    config: SessionConfig, executor_id, run_tag) -> ToolActionOutcome
run_one_tool(ledger, config, activity_id, executor_id, call: ToolExecutionInput,
             *, run_tag) -> SessionOutcome
PostgresAdmissionLedger.admit_tool_operation(intent: ToolIntent) -> ToolAdmissionPermit
PostgresAdmissionLedger.mark_tool_started(permit: ToolAdmissionPermit, call: ToolExecutionInput) -> None
PostgresAdmissionLedger.record_tool_outcome(permit: ToolAdmissionPermit,
                                            call: ToolExecutionInput,
                                            outcome: LedgerOutcome) -> RecordOutcome
ControlledToolExecutor.call(context, call: ToolExecutionInput) -> ToolCallResult
run_supervised_window(..., one_call=None, tool_action=None) -> SessionOutcome
SingleWindowSupervisor.run_once(..., one_call=None, tool_action=None) -> SessionOutcome
```

ToolCallResult是新纯数据结果类型，按B6七字段输出，无模型provider/usage字段，不拿ModelCallResult填假供应商。序列化status严格为succeeded/rejected/not_sent/failed/unknown之一，不接受tool_plan；ToolAdmissionLedger无持久实现时默认失败关闭，不提供进程内计数替代。ToolActionOutcome包含status、business ReadOutcome、supervision SessionOutcome、settlement独立事实。existing相同工具身份只读；同键异身份明确冲突，不默默返另一组参数的旧答案。新call入监督后status按业务持久读与有限工具回执判定，记录失败/监督未知不得自动调用；结算已确认不等于业务成功，业务已提交也不等于树已停。service不能直接通过新工具ledger接口执行本地运算，只能让固定worker使用ControlledToolExecutor。

完整候选产品改动如下。

- migrations/008_activity_tool_budget.sql，B2事务及验证约束，不改001—007。
- activities/repository.py及必要__init__.py，ActivitySpec尾部加max_tool_calls=None、create严格校验/写入；新增专用工具方法/锁内kind和参数身份、共用原子record核心；旧模型permit拒tool行；read/list/snapshot及unresolved元数据带持久kind，恢复和cancel不动工具计数。
- activities/service.py，新增固定工具入口、同键身份与只读处理、规范快照及有界线程等待；continue_from_result先拒工具父。read/resume只是类型增强，无出站。
- capabilities/contracts.py及必要导出，增加ToolExecutionInput/ToolIntent/ToolAdmissionPermit、ToolCallResult及ToolAdmissionLedger失败关闭接口；旧model凭证和引用结构不改。
- capabilities/tool_execution.py新纯内部工具适配器，复用原tools.py校验与execute；模型gateway不改发送路径，不改变ToolRegistry计算语义。
- worker/one_tool.py新有界工具编解码和run_one_tool；worker/command.py只加one_tool固定枚举。one_call.py保留原外2/内3，不把tool塞入model结果形态。
- worker/worker_main.py、launcher.py、supervisor_main.py、session.py，仅新增工具分支及B6版本化严格输入/输出；SessionOutcome尾部新tool_receipt默认None，外2精确旧字段兼容；旧停止/恢复/时间退款授权主体不变。
- tests/test_activity_tools.py、test_worker_one_tool.py新覆盖；test_activity_results、test_activity_continuation、test_capabilities、test_worker_session及旧worker_one_call仅实际受影响兼容/回归，不能弱化原断言。新增本卡后续实现专用fixture/runner，编号与资源由获批实施卡指定，本设计不占新TASK或预建夹具。

不改HTTP/UI/runtime、transport、gate/windows_job/supervisor_ipc安全主体、materials权威更新、依赖锁；不加入公开接口、可变命令、网络/file工具、跨机恢复或常驻服务。若未来实现确需突破该清单安全主体或主要协议形状，先定位差异交回，不靠本候选扩大授权。旧无工具调用方保留默认None额度及外2/内3，旧allowed_tools非空仅计划调用方也兼容。

### B10 四条手工守恒轨迹 非运行

四条各用独立合成活动，初始M=100、S=0、R=0、scope=1、generation=g0、max_tool_calls=4/T=0、max_requests=5/Q=0，模型成本已用0；无历史工具、无额度扩容。W=10且配置满足原startup/request/stop不等式，数值只是手工样本非产品默认；每次claim G+=1，正常settle再G+=1，取消G+=1，recover_unknown本身不加G。

轨迹1正常及同键复查。SUP claim得到g0+1、R10；admit A使T1，mark/execute得3，record received+正文h；树零关闭句柄及门，elapsed2.2取C3，settle得到S3/R0/G=g0+2。Q0/成本0、T1/4、M守恒S+R=3。再次显式提交A同name/call_id/规范参数，服务只读现行tool结果，不claim或execute，所有计数不动；A改参则冲突，也不claim。

轨迹2执行后未提交崩溃。独立U claim g0+1/R10，admit使T1，mark确认、execute发生，record前worker崩溃，持久dispatched、无results、S0/R10。监督先停止自有树且不做正常部分结算；租约已过且符合权限时recover_unknown置U unknown，T1、S0/R10及G不变。再由受信调用者明确cancel，该活动S10/R0/G=g0+2；重复cancel不再扣时间，Q0/成本0/T1。read U为unresolved无正文，成功record不能把unknown改received或返回ALREADY_PRESENT；无自动重算。取消仅本轨迹的有界收敛选择，不代表未知自动取消全部业务。

轨迹3已提交响应丢失。独立V同样claim/admit/mark/execute，record实际COMMIT使V received+正文h，响应丢失后worker回UNKNOWN/unconfirmed；此回执不否认DB正文。worker退出0/树零，SUP按C3关门结算得S3/R0/G=g0+2，T1/Q0/成本0。service或后来resume只读确认committed_current(kind=tool,h)；直接仓储相同身份与完整终态/正文确认重试得ALREADY_PRESENT，无新写和无执行，即使G已推进。该轨迹没有recover把received改unknown，与轨迹2绝不能合并。

轨迹4取消及范围竞争的独立变体。4a额度初始4：已claim/admit D后T1/R10，mark前cancel使S10/R0/G=g0+2，mark拒绝、无execute；凭证UNKNOWN诊断/恢复不改T1，监督确认停树后不再settle。4b另一个初始T0活动：旧scope context在CAS已完成至2后admit拒scope_changed，T0、无op；另一次独立竞争安排先读旧集合提示、暂未锁，另一连接CAS提交不同来源集合，再恢复工具事务，抛ScopeConflict回滚T0。两者已开窗时间按实际停止事实结算，不能把工具预扣零等同时间零。4c若CAS在工具admit或mark后才提交，T1保留；mark前拒执行，mark后可能已运算但旧scope新正文被拒。全部变体不扩容、不回绕scope/G，不重复取消或退款。

## C 最小验收矩阵 仅设计未来检查

当前文件事实与契约为B级，四条轨迹及未来风险推导为D级；下列离线/真实PG/Windows检查实际运行后才有相应A证据，Mock只证明其边界内行为。全部新动态未运行。未来实施卡必须冻结源码、配置、样本、资源归属、上限/清理及as-run加载指纹，不沿用090旧运行许可。

C1 迁移及完整条件约束，真实新合成PG。空库001—008和合法非空001—007→008各一个固定样本，覆盖旧model含NULL usage、旧received有/无正文、unknown及allowed_tools非空且新额度NULL。断言原请求/成本/M/R/S/结果字节与hash不变，新kind=model、工具已用0、未配置拒执行，旧模型计划仍可用。反例包括max NULL而已用1、负/超限已用、零上限配正计数、model缺provider/正请求字段、model携工具ID/摘要、tool缺标识或错误sha/call_id/tool_names、tool携任何模型元数据、tool成本非0。全部SQL CHECK明确拒绝；重复008及中途故障整体回滚，无用户库动作。数据库列最大值与API int/bool/字符串边界离线覆盖。

C2 规范参数绑定，定向离线加PG。对拷贝后原Mapping外部变更、同键改参、大小2048边界、非规范编码、重复键/NaN/嵌套/额外字段、摘要伪造、call_id或name更换逐项检查；断言执行从独立规范快照取得原参数，错误新输入不能获得工具预扣/mark。凭证摘要或持久摘要与输入不同，mark与record均拒绝；用旧AdmissionPermit三字段包装真实tool admission也拒绝，反向工具凭证操作model拒绝。运行离线只能声称编码/适配边界A，锁内绑定需要真实PG A。

C3 权限及有限计数，真实PG。白名单缺名、NULL额度、零额度、正额满、INT_MAX满各拒绝；预扣提交才T+1，正额2最多两次持久准入，第三次无新op/工具/模型费用变化，重连后不重置。纯非法输入在SUP前零claim；锁内拒绝若已开窗，允许真实时间记账，不能要求既有时间列也零变化。未知/未mark失败不退款，model请求与成本独立不被工具使用；日志只有限脱敏code。

C4 同键竞争，真实两连接/同当前lease，明确锁屏障或任务事件，不用sleep猜顺序。两个真实admit_tool同键至多一凭证、一T增量，mark至多一执行资格；正常胜者对实际有限计算execute计数1，胜者在mark前崩溃的独立样本为0而T1。同键同身份只有read/resume；同键异参数或model占键明确冲突、无第二扣次。不能把“唯一准入”写成所有故障条件下“恰好执行”。

C5 类型隔离，真实PG与服务离线。用真实工具准入/record造当前有效received tool T，read/list能识别kind/tool元数据并读正文；service以T作父拒绝且launcher零调用。直接构造T正确scope/hash引用、allowed_tools为空，绕服务的gateway及ledger.admit也拒绝result_kind_not_consumable，无新模型行、request/cost预留、transport。合法model父P对照正常。正文存在而主表kind/绑定损坏不能以hash正确放行。

C6 admit/mark边界故障，真实PG。分别在admit COMMIT前回滚与COMMIT后丢响应注入，不混成一例；前者无行/T0，后者reserved/T1，但本次都execute0，不重新admit。另测已reserved未mark终止，以及mark COMMIT前失败/后丢响应，分别观察reserved或dispatched/T1，execute0，恢复为unknown且无成功正文。故障位于真实事务提交点，替身只负责截断响应/屏障，不用伪造ledger结果冒充事务。

C7 execute后未提交，真实PG。确认mark及一次实际计算后，在record前停止或record事务提交前失败。断言无results、恢复unknown、T1保留、本地execute计数1但resume无正文；后续同成功结果不能ALREADY_PRESENT或覆盖unknown。另测明确ToolValidationError经received/tool_execution_failed、无正文、T1、不泄露参数，窗口可独立正常结算。

C8 record已提交丢响应，真实PG。在真实COMMIT之后丢响应，DB存在received+正文、控制器回UNKNOWN/unconfirmed；resume只读确认正文/typed hash。直接同凭证/参数/完整终态record确认ALREADY_PRESENT、xmin/计数不变，异文及received无正文补写拒绝。与C7分开的fixture/case，不用一条崩溃故事同时宣称两种持久事实。

C9 资格变更，真实PG两条并发顺序。CAS先提交再使用旧context拒scope_changed；读旧提示未锁时CAS提交不相交新集合，再恢复旧事务拒ScopeConflict、回滚无工具预扣，屏障证明发生点。admit之后CAS/来源替换/关门/租约或活动到期使mark拒绝，mark之后变化允许算过但record新正文拒绝，T保持。cancel包括空/失效来源可收尾、重复cancel不重复折叠、旧G晚到无成功写；typed读失效先抑制正文，当前有效cancel历史可读。不得用直接SQL改scope代替revise_scope，时间与工具账分开断言。

C10 最小真实Windows正常组合。受信service显式finite_calculate一次，真实新合成PG及固定launcher/SUP/worker/Job，真实有限运算；无模型provider或transport调用。实际加载hash、外3/内4身份与参数、DB工具摘要、正文hash/read/list一致；execute1、T1、model计数/费用不变，SUP实际树零→句柄关闭→关门→结算，业务/监督/账面事实分开。只有工具动作走新版本，另一个旧无工具model协议编解码/必要回归证实外2/内3形状保持。

C11 最小真实Windows停止与恢复组合。在真实工具mark确认后，用受控fixture在worker执行边界替换为不合作阻塞，SUP Job截止硬停止，PID/创建时间/命名Job归属与树零可核，失败不获部分退款，T不退，DB无伪成功正文。随后在原单机同会话/旧租约允许前提下显式接续，确认原Job消失或已停才claim，旧R只折叠一次，旧工具操作unknown不重执行。该阻塞替身是停止机制反例，不宣称真实finite_calculate会无限运行；正常真实计算由C10证明。旧会话不明、Job不可判、句柄失败的未变主体证据复用，新工具分支至少证明不会绕该拒绝，不另重造监督层。

C12 close/settle及版本兼容，定向PG/离线，必要部分与C10/C11合并。close提交丢响应不得先退款；settle提交前失败可一次成功、提交后响应丢失同G/W/C有限一次ALREADY_SETTLED，账只变一次，相同G异C及更旧G拒绝，cancel已折叠不另settle。旧SUP拒外3无claim、旧worker拒one_tool无工具准入/执行但可能已预扣时间；新model外2不含tool_receipt，旧one_call/idle请求照旧，type混用/额外字段/过长参数/假身份/无剩余时限早拒。检查业务UNKNOWN却时间已结算，不能用结算成功推正文成功。

证据复用须按实际差异。原G3正文规范/hash、旧D3安全主体及090的CAS锁序有适用结论时直接引用。008改条件约束、锁内kind、record共享核心、read/list投影、continue父资格、session/launcher版本分支都确实受影响，必须做上述针对性回归，不能因函数名仍旧就免检。旧完整discover、全套D3/G3和真实provider不是默认前置。C10/C11是两个必要组合方向，不是本卡授予启动次数，资源和批次数由将来的完整实施卡集中授权。

未来G5完整实现、相关验证和普通修复在同一获批实现卡连续完成；稳定快照及资源收尾后，由编排另发隔离独立增强审计卡，限原目标、最终差异/直接源码/原始日志，无实现聊天/自评。门槛是本切片权限、持久预扣、kind/参数绑定、旧模型兼容和停止恢复无阻断，证据及资源结论清楚。必要审计未完成不启用工具权限或宣告G5通过，不要求每个文件小修复单独审。重大前提推翻则在权限启用/依赖扩散前处理，本设计本身不替代该审计。

## D 一个合并变更决定包

建议编排完成本轮合同一致性核证后，将下列内容作为一个整体批准包提交必要决定，不重复询问首轮D1/D2，也不把拒绝工具→模型或未知重算变成用户风险选择。

包内持久模型是B2的候选008，activities的有限独立工具次数、operations的model/tool条件及参数标识、共表结果类型投影和旧model兼容。迁移只给空/非空新合成验证策略，不授权用户库，不承诺无扫描/重写；历史model新增字段解释和故障回滚/已用工具行后的恢复限制明确。主要数据模型变化须批准后才能落DDL。

包内执行权是受信活动显式有限配置与单个显式工具动作，唯一finite_calculate，次数在准入提交时持久耗用，即使未实际执行也保守不退；工具不占模型request/cost但计原时间，已开窗后拒绝也不豁免真实管理耗时。固定one_tool枚举及已有launcher/SUP/worker受控Job是唯一执行位置，禁止未纳入Job的服务线程计算，禁止可变命令和额外工具/监督层。

包内接口/协议是B3/B9专用意图/凭证、规范快照、外3/内4工具帧与SessionOutcome可选tool_receipt；model外2/内3及原凭证保持。工具read/list可见且低信任，service和DB父准入拒工具→模型，UNKNOWN不自动重算/重发。仅新增可信内部入口，不开放HTTP/UI或父子模型循环。

唯一推荐理由是复用原持久状态机/正文原子性与D3强制停止，同时补齐其不能自动涵盖的类型和参数边界，减少两套恢复/预算逻辑。一个最小替代是另建专用activity_tool_operations及工具正文/读查询，仍必须同样受控Job、有限活动工具计数与模型消费隔离；代价是跨kind键域、恢复与读投影重复、更多迁移及审计负担，须另定完整合同，当前不推荐。未经批准维持现有计划展示和拒实际执行，不在本卡部分启用。

普通类型名、具名CHECK命名、helper拆分、日志code文案由实现者在本合同域内收敛，不让用户选择；工具→模型、自动循环、未知重算、额度扩容、其他工具、跨机恢复、用户库或真实provider均没有本卡新增决定需求或授权。只有上述聚合主要改变缺少批准；本窗口不请求睡前/现场操作，不自批实施。批准后才能由编排出完整实施卡，当前不占TASK-092或声称已派发。

## K1—K5修正关闭对照

K1首轮以纯计算/租约替代停止证明；session.py:211—235及282—327实际依赖命名Job、树零和句柄。现B5/B6复用原受控链，只加固定工具分支；C10/C11及C12验证硬停止/旧树拒绝/结算次序，无进程内豁免。

K2首轮以allowed_tools空宣称工具父不能消费；service.py的输入组装及repository.py:975—983实际无kind。现B7双层检查持久kind并保留模型引用结构；C5直接构造真实tool父引用的绕过反例在锁内无新模型预扣，读/list仍类型可见。

K3首轮要求原permit不存在的摘要，又把Mapping冻结视为内容冻结；contracts.py:181—186与392—395明确相反。现B3独立工具凭证、一次私有规范快照/各跳再验，B4 mark/record按DB行绑定；C2及C4覆盖参数变更、伪摘要/跨kind凭证、同键冲突和唯一资格。

K4首轮误报002非空和007前提且漏类型兼容；两份实际DDL已核。现B2完整model/tool条件、NULL预算必须已用0、0额度和溢出、历史model解释、非空合成及迁移真实限制，B7/B9补旧方法语义适配；C1与C12验证旧模型NULL usage、旧计划调用方及新字段/帧兼容。

K5首轮把未提交崩溃与已提交响应丢失混写、统一DB故障无执行、并发恰一次、取消扩容及scope冲突前提错误。现B8逐事务/执行边界、B10四条独立数字轨迹；C4/C6—C9/C12对应至多资格、丢响应与回滚、已执行DB故障、预扣未mark、取消一次折叠、不同scope竞争和有限同G结算确认。没有动态通过声明。

## 本轮操作、投入及交回

允许改动仅本结果与DocuN/evidence/TASK-091/revision-01文件。原首轮完整原字节保留，编排裁定、任务卡、原证据、所有产品/测试/迁移/正式DocuS/公共库未写。零compile、unittest/pytest、PG、Windows Job、Docker、业务工具execute、模型或provider；文件读取、hash及文档写入不是产品动态验证。正常沙箱命令因已知helper ACL故障未创建，通过平台原require_escalated审批完成有限读写，未修改系统ACL或绕过审批。

首轮55分钟属执行者声明，非独立计时；本轮从首个可核UTC时间2026-09-30T13:09:36.021426起记录，读取启动保守预扣2分钟，剩余上限65分钟不重置。实际结束时间/耗用及建议状态见revision-01/checkpoint.json与consistency-check.json。若早期资料有未记录投入不能据此宣称更高精确值；本次按卡面保守账执行，完成即停。

实际源码读取限工具/凭证、admit/record/read/list、窗口恢复及直接编解码/固定命令/gate依赖，正式文档只读当前导航及必要目标；一次定向导航搜索曾返回较多历史关联行，后缩为顶部和函数片段，没有沿历史重审090。读取范围和文件级指纹记录revision-01/files-read-hashes.json，指纹是只读对象核对，不是本卡运行加载证明。五个直接核心与090冻结值/091原清单核对；其余直接依赖仅记录现场文件事实，不重算整仓67项。

全部新增动态项和008真实DDL尚未验证；四条轨迹仅D级守恒推演。本轮不是独立审计，不代签编排通过。风险仍包括条件约束/旧数据兼容、工具参数与kind权威实现遗漏、严格协议混用、未知提交和强制停止次序；每项已定位到未来矩阵及集中独立审计，不能用用户接受风险替代必须检查。

建议状态为A事实地图、B唯一合同、C矩阵与审计门、D一个决定包均完整交付，K1—K5按源码事实合并修订，待编排本轮核证及主要改变批准。必要人工只有带回本结果路径，不要求密码、Docker或普通技术选择。正式架构/执行/CHANGE由编排核证后统一登记本轮和批准状态；本卡只建议同步有限工具计数、受控one_tool及类型消费边界，不宣告G5/整个STEP-006/008完成，不写外部经验库或项目记忆。


修正轮证据导航

[编排合并裁定](D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-091-work-decision.md)；[本轮断点与投入](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-091/revision-01/checkpoint.json)。完成时生成的files-read-hashes.json和consistency-check.json仅记录定向文件核对与一次文档检查，无产品运行或as-run声明。

## 首轮全文历史保留

以下为首轮原文，仅作历史；与修正轮01冲突的推荐已撤销，不能作为当前实施依据。

# TASK-091 结果

## 结论、差异与证据导航

本轮为 R-085，对象快照为 090 验收基线（需求 v1.1、架构 v0.57、执行 v1.78，Git 基础 HEAD 45951501d2741630a229762d6b2d3f4b34d7f702，五个 G5 直接相关主文件 hash 与 Ndocu/evidence/task-090/final-product-hashes.json 逐项一致、零漂移），完成情况为完整：A 事实地图、B 唯一推荐合同、C 验收矩阵、D 合并变更决定包四项一次交付，全部为只读设计产物，未修改任何产品、测试、迁移或共享文档。

一句话结论：现有链路已具备「工具计划的模型侧产生、白名单校验、协议级结果回传形态」三段，但工具实际执行、持久次数预扣、工具结果持久提交与跨恢复读取四段完全未接线，且持久账本不存在任何工具次数列；本卡给出以「一次获准工具调用尝试」为计数单位、复用 activity_operations 状态机加 kind 列、新增 008 迁移（activities 两列加操作表列放宽）、进程内受租约保护执行、G3 结果表经 kind 区分承载工具正文的唯一最小合同，以及一份含三项主要决定与一项次要决定的变更包。

关键验收结果与证据导航：本卡无运行检查，全部结论为 B 级（代码、配置、文档直接读取）加 D 级（设计推演），动态项一律未运行。读入文件清单与 SHA256 见 [files-read-hashes.json](../evidence/TASK-091/files-read-hashes.json)；规则版本沿 rules-snapshot.json 锁定值，本次三份规则指纹复核一致。既有证据复用边界在「操作与验证详情」一节。

## A. 事实地图：现有能力、真实缺口与最小改变范围

以下全部为对当前磁盘源码的直接函数级事实（hash 见证据文件），逐条区分「已有实现」「已有运行证据」「推导」。

### A1 已有实现（代码事实）

一、工具目录与有界语义（backend/app/capabilities/tools.py）。唯一登记工具 finite_calculate：TOOL_NAME 常量；参数为两个有限数值（field_validator finite_bounded_number 拒绝 bool 与非有限值，绝对值上限 MAX_ABS_INPUT=1e12），operation 限 add/subtract/multiply/divide/power，divide 除数非零，power 指数为 -12 到 12 整数且零不取负幂（model_validator operation_limits）；参数字符串上限 MAX_ARGUMENT_BYTES=2048 字节；execute 用 Decimal prec=50 计算，结果必须有限且绝对值不超过 MAX_ABS_RESULT=1e18，返回规范化十进制字符串。ToolRegistry.schemas_for(allowed_tools) 对白名单外名称抛 ToolValidationError；ToolRegistry.plan(call_id, name, raw_arguments, allowed_tools) 完成 call_id（非空、不超 128 字符）、名称登记、活动授权、参数有界 JSON 与 strict Schema 四重校验后返回 ToolCallPlan(call_id, name, arguments)。execute 的 docstring 明确「模型入口不会自动调用本方法」。

二、模型请求契约（backend/app/capabilities/contracts.py）。Message 已支持 role=tool（必须同时携带 content 与 tool_call_id）与 assistant.tool_calls（至多 8 个），即协议层已能表达「工具结果作为对话消息回传给模型」的形态。ModelCallRequest.allowed_tools 上限 16 个名称。CallStatus 枚举已含 TOOL_PLAN。AdmissionIntent 携带 tool_names；AdmissionLedger Protocol 定义 admit／mark_dispatch_started／record_outcome 三方法；RejectingAdmissionLedger 为默认失败关闭实现。

三、受控网关（backend/app/capabilities/gateway.py）。call() 的完整次序为：前置校验（100 至 105 行：input_result 存在时，activity 不一致、operation 同键或 allowed_tools 非空任一命中即 REJECTED invalid_input，即受控续接与工具授权在网关入口互斥）→ _build_payload（schemas_for 白名单生成 tools 数组加 tool_choice=auto）→ ledger.admit → _validate_permit → mark_dispatch_started → transport.send → _handle_response → _finish。finish_reason=tool_calls 时解析 1 至 8 个 tool_calls，逐个经 tools.plan 校验，返回 CallStatus.TOOL_PLAN 与 tool_plans；_finish docstring 明确「TOOL_PLAN 不持久化业务正文、不自动执行」。TOOL_PLAN 的 LedgerOutcome 处置为 RECEIVED（持久登记 received 终态、带 returned_model 与 usage、无正文）。_validate_conversation 强制 assistant 工具调用与 tool 消息严格配对（重复 ID、悬空 tool 结果均拒绝）。

四、持久账本（backend/app/activities/repository.py）。activities 表预算列恰好四组：模型请求次数（max_requests/requests_reserved）、费用（max_cost_microunits/cost_reserved_microunits/reserve_cost_microunits）、请求与输出字节、时间账本五列（004 迁移：max_running_seconds/running_reserved_seconds/running_settled_seconds/last_settled_generation/last_settled_seconds）；另有 dispatch_closed（005）与 running_owner_session_id（006）。allowed_tools 为 VARCHAR(64)[] 名字白名单（cardinality 上限 32），不携带任何计数。admit() 的 _activity_allows（919 至 936 行）对工具仅做集合包含检查 set(intent.tool_names).issubset(activity["allowed_tools"])，不查任何工具额度；且 967 行规定 input_result 引用存在时 intent.tool_names 非空即 AdmissionDenied invalid_input，账本层同样互斥。同键拒绝在 974 行：「操作键已经占用，不能获得第二次发送资格」，幂等键即 (activity_id, operation_id)。状态机为 reserved→dispatched→{not_sent, received, unknown}；record_outcome（1172 至 1235 行）实现终态严格等值幂等（RecordOutcome.RECORDED/ALREADY_PRESENT，含正文三元组同存同缺与 1204 行「关闭门后不接受正文新写」）；1202 行规定 reserved 态不能直接登记非 UNKNOWN 结果，必须先经 mark_dispatch_started 越过出站边界。read_committed_result/list_committed_results 提供失效不投影正文的只读恢复。claim_lease 预扣 W_eff=min(window, M-S-R) 并递增代次；cancel_activity 将时间残留全额折叠入 S 而「模型次数/费用预留不动」；recover_unknown 与 recover_obsolete_operations 按 state in (reserved, dispatched) 收敛 unknown，不退预留、不重发。

五、Windows 监督链（worker 侧）。launcher.run_supervised_window 仅支持 Windows；SUP 进程（supervisor_main）执行 SingleWindowSupervisor.run_once：inspect_window→恢复检查（含 running_owner_session_id 单机身份核对）→claim_lease 预扣时间→NamedMapping 写协议3 请求→NamedJob 创建并 spawn 固定 worker→wait_empty_until(stop_ns) 树停止→主进程退出码校验→decode_receipt 回执校验→job.close→begin_window_close 关闭门→settle_execution_window 结算（S+=C，R-=W，相同 G 相同 C 才 ALREADY_SETTLED）。worker_main.execute_one_call 构造 ControlledModelGateway 后经 ClosingCallGate 恰好调用一次。one_call.decode_receipt 已能校验 tool_plan 形态回执（business_commit 必须 not_committed、无正文、tool_plans 非空，且用 ToolRegistry().plan 以固定 frozenset({"finite_calculate"}) 复核每个计划）。

六、G3 正文表（backend/migrations/007_activity_operation_results.sql）。activity_operation_results 以 (activity_id, operation_id) 主键外联 activity_operations，payload 封套 {format, value}、1 至 131072 字节、sha256 绑定 admission/代次/范围。

### A2 已有运行证据（引用，不重跑）

test_capabilities.py 的 test_tool_suggestion_is_validated_and_only_returns_plan（311 行）在合成账本下验证 TOOL_PLAN 返回计划、手动 ToolRegistry().execute 计算得「3」、随后以 assistant tool_calls 加 tool 消息形态回传结果再请求获 SUCCEEDED；test_unknown_unauthorized_and_extra_tool_fields_are_rejected（356 行）验证未知名称、未授权、多余字段拒绝。test_worker_one_call.py 的 test_tool_plan_never_executes（203 行）将 ToolRegistry.execute patch 为 AssertionError，证明 worker 内一次调用后仍为 TOOL_PLAN 且发送次数为 1，即产品链内工具从不被执行。test_activity_results.py 的 test_tool_plan_and_failure_never_fake_payload_success（314 行）验证 TOOL_PLAN 不伪造正文。G4 范围 CAS、锁后来源复核、受控续接、低信任正文与未知不重发的真实 PG 与 Windows 证据沿 DocuN/results/TASK-090-final-acceptance.md 原范围引用。

### A3 缺口与未接线步骤（本卡要收敛的范围）

缺口一：无执行接线。TOOL_PLAN 返回 tool_plans 后调用链终止；产品路径没有任何代码调用 ToolRegistry.execute（唯一调用在测试）。执行、结果持久化、结果读取三步不存在。

缺口二：无工具次数持久账本。activities 无 max_tool_calls 或 tools_reserved 任何列；admit() 只查白名单不查工具额度；FLOW-005 要求的「有限模型请求/工具调用/内部步骤/重试/耗时/费用；每次出站先事务性占次数」中工具维度未落地。模型请求次数不能暗中充当工具次数：一次 TOOL_PLAN（一次模型请求）可含 1 至 8 个工具计划，且工具执行不消耗模型请求，两者是独立可观察单位。

缺口三：无工具操作身份。activity_operations 各列语义绑定「一次模型调用」（provider、configured_model、request_bytes、max_output_tokens、token 计数均为 NOT NULL），工具操作无法按当前约束落行；需要一个类型区分与列放宽，而不是因字段名相似强行复用或另起炉灶。

缺口四：受控续接与工具互斥。gateway.call 100 至 105 行与 repository.admit 967 行双重规定 input_result 与 allowed_tools 互斥。首切片不改动该互斥（见 B9 与 D3），因此「模型→工具→模型」循环不在本切片。

### A4 最小改变范围（推导）

需要新增：activities 两列（工具额度上限与已用预扣）、activity_operations 的 kind 类型列与模型专属列放宽、工具准入方法、进程内工具动作编排、工具结果经 G3 正文表承载的类型区分。不需要改动：tools.py（有界语义原样）、transport.py、gateway.py 模型路径、one_call 协议3 与回执、worker 三件套与 gate.py、launcher.py、既有 Windows/D3 设计、既有测试断言。理由：工具执行无出站、无子进程树，Windows 窗口的强制停止基础设施对纯本地有界计算不是必要条件；持久纪律（租约、代次、关门、结算、恢复收敛）全部可在仓储层复用。

## B. 唯一推荐实施合同

以下为推荐的完整合同。所有「建议」字样的函数签名仅为契约说明，实际命名由实现者在获准范围内收敛；凡涉及持久模型与权限的项均已列入 D 决定包，未获批准不实施。

### B1 权限模型

工具执行权由两个且仅两个来源承载：受信活动配置（activities.allowed_tools 白名单加显式 max_tool_calls 额度）与明确调用方动作（编排层显式发起的工具动作调用，携带显式 operation_id）。资料内容、模型输出、持久父正文、tool_call_id、路径或配置文件均不能授予或扩大工具权限。在实际执行边界（进程内动作函数入口）重新完整校验：工具名称在活动白名单内、参数经 ToolRegistry.plan 精确 Schema 校验（含 2048 字节、有限数域、1e12 输入与 1e18 结果边界）、一次动作至多一个工具调用（不批量）、来源集合与范围修订经仓储锁后复核。未知名称与越权一律拒绝并持久记录脱敏错误码。finite_calculate 的有界运算语义不扩大：不改数值边界、不增运算类型、不加任何 IO。

### B2 计数单位、预扣时点与输入域

计数单位为「一次获准的工具调用尝试」：一个工具操作通过 admit_tool 获得持久登记（含 tools_reserved 加一）即计一次，与预扣时点（准入短事务内）严格配对。模型一次响应含 1 至 8 个工具计划时，每个计划须经单独的显式工具动作逐个获准，不存在一次预扣多个；动作发起方一次只提交一个计划，超出即拒绝。与相邻账本严格区分：工具次数（tools_reserved）独立于模型请求次数（requests_reserved）、费用（cost_reserved_microunits）与时间账本（R/S 五列），任一账本不充当另一账本。输入域：max_tool_calls 仅接受 1 至 2147483647 的整数；NULL 表示「未配置」，与「零额度禁用」不同——禁用由 allowed_tools 空集表达，未配置由 NULL 表达，两者都拒绝准入但错误码可区分（前者 unauthorized，后者 tool_limit_unconfigured）。防溢出：每次准入恰好加一，tools_reserved 与 max_tool_calls 同处 INTEGER 域并加不变式约束 tools_reserved 小于等于 COALESCE(max_tool_calls, 2147483647)，无批量加法、无回绕。不引入无限、默认免费或隐式额度；需求第 13 节「未配置有限预算则拒绝付费动作」在此体现为 NULL 即拒绝。

### B3 持久模型（未获实施批准；拟议 DDL 契约）

新增迁移 backend/migrations/008_activity_tool_budget.sql，拟议契约如下。此迁移设计为非空安全：所有 ADD COLUMN 带默认或可空，不回填、不删除、不改写任何已有行值；这使其成为首个允许在已有数据的 activities 库上执行的迁移，与 004/005 的「仅空库」约定不同，该差异本身列入 D1 决定。

一、activities 表：ADD COLUMN max_tool_calls INTEGER NULL CHECK (max_tool_calls IS NULL OR max_tool_calls BETWEEN 1 AND 2147483647)；ADD COLUMN tools_reserved INTEGER NOT NULL DEFAULT 0 CHECK (tools_reserved >= 0)；ADD CONSTRAINT 检查 tools_reserved <= COALESCE(max_tool_calls, 2147483647)。已有行 max_tool_calls=NULL 天然拒绝工具准入，旧行为完全不变。

二、activity_operations 表：ADD COLUMN kind TEXT NOT NULL DEFAULT 'model' CHECK (kind IN ('model', 'tool'))，已有行全部为模型操作，默认值语义正确；ADD COLUMN arguments_sha256 TEXT NULL（工具计划规范化参数字节的 SHA-256 小写十六进制）；ADD COLUMN tool_call_id VARCHAR(128) NULL（模型给出的调用 ID，仅诊断与配对记录，不作授权或幂等键）。约束调整：provider、configured_model 放宽为可 NULL 且加检查 kind='tool' 时为 NULL、kind='model' 时非 NULL；request_bytes、max_output_tokens 同理（kind='model' 时保持非 NULL 且大于 0）；reserved_cost_microunits 的 NOT NULL 保留但原 CHECK（大于 0）改为条件检查 kind='model' 时大于 0、kind='tool' 时等于 0（工具为本地确定性计算，不占费用预留）。原 002 三个状态机 CHECK（state 与 disposition 关系、reserved 与 dispatch_started_at 关系、终态与 recorded_at 关系）全部不动。实现时须先查询 pg_constraint 取得未命名 CHECK 的实际约束名再 DROP，不猜测名称。

三、activity_operation_results 表：零改动。工具结果正文复用本表与同一封套/校验/绑定/hash 规则，工具与模型操作经主表 kind 列区分。理由：read/list 的绑定一致性与失效不投影逻辑免费继承，避免第二套正文表与第二套恢复查询。

空库与已有数据策略：新合成库按 001 至 008 全量建基线；已有活动库（若用户数据存在）直接执行 008，不重放 004/005 的空库校验，不自动回填任何历史操作的 kind 以外字段。不做自动数据迁移工具。

### B4 工具操作身份、幂等键与冲突语义

一次工具操作的身份绑定五元组：活动（activity_id）、权威来源动作（编排层显式调用与显式 operation_id）、执行租约上下文（executor_id、execution_generation、scope_revision，取自当前持久租约而非调用参数直信）、工具调用标识（call_id 与工具名）、规范参数（canonical JSON 字节及其 SHA-256）。幂等键沿用 (activity_id, operation_id)，与模型操作同域同约束。冲突语义：同键再次 admit_tool 一律 AdmissionDenied（操作键已占用），无论参数是否相同，因此重复同键不能再次执行；同键改参在键占用处即被拒绝，额外以 arguments_sha256 在 mark 与 record 时核对 permit 携带值与存储值，不一致按完整性错误拒绝，用于防御实现缺陷而非替代键检查；跨活动天然隔离（键含 activity_id 域）；旧范围、旧代次、取消、关门经现有 current 检查（_operation_is_current 语义）在 admit、mark、record 三处分别拒绝或收敛为 unknown 诊断，行为与模型操作一致且可区分（错误码不同路径不同）。

### B5 预扣、登记与执行的事务边界

新增仓储方法 admit_tool_operation(context, tool_ref)，在单一短事务内按既有锁序执行：来源 UUID 排序 FOR UPDATE→活动行 FOR UPDATE→锁后来源集合复核（ScopeConflict 语义原样）→操作键 FOR UPDATE 检查。事务内校验：活动 running、dispatch_closed 为 FALSE、executor 与当前租约一致、execution_generation 与 scope_revision 匹配、租约未过期、活动未过期、来源快照有效；工具名属于 allowed_tools；max_tool_calls 非 NULL 且 tools_reserved 小于 max_tool_calls；操作键未被占用。全部通过后同一事务内 UPDATE activities SET tools_reserved = tools_reserved + 1 并 INSERT activity_operations（kind='tool'，state='reserved'，tool_names=(name,)，reserved_cost_microunits=0，arguments_sha256，tool_call_id，模型专属列为 NULL），返回 AdmissionPermit（复用现有三元组结构）。数据库异常统一映射 AdmissionUnavailable，拒绝映射 AdmissionDenied，与现有 admit 相同。

执行严格在事务外：编排层在 admit_tool 返回后，先经 mark_dispatch_started（复用现有方法，其「发送资格已消费或活动已失效」检查对工具语义同样成立；docstring 文案可改为通用的「执行资格」，属实现细节）将 reserved 推进为 dispatched，作为开始执行的持久边界；然后调用 ToolRegistry.execute(plan)。执行前最后资格检查即 mark 事务本身；不虚构零竞态：mark 与 execute 之间活动可能被取消或范围被改，此时「已发生的本地运算」不可撤销，但结果提交按资格规则收敛——record 时 current 检查失败且处置非 UNKNOWN 即 AdmissionDenied，编排层将其登记为 UNKNOWN 诊断后结束，预扣保留。工具代码不在任何数据库事务或锁内执行。

### B6 失败、未知与恢复的持久语义（逐边界）

执行前失败（plan 校验失败或 admit_tool 拒绝）：无预扣、无操作行、无执行，拒绝原因持久化仅限准入拒绝时的脱敏错误码路径（与模型 admit 拒绝同等粒度）。

已标开始后进程崩溃（dispatched 悬挂）：持久事实为操作停在 dispatched、无 results 行、tools_reserved 已加一。恢复路径复用 recover_unknown 与 recover_obsolete_operations：租约过期或活动取消后收敛为 state='unknown'、disposition='unknown'、error_code=executor_lost。允许的下一动作：仅显式新 operation_id 的重新准入（消耗第二次额度）或人工裁定；不自动重发、不自动退款、不靠任何进程内计数实现跨恢复约束。对本地确定性计算的「重算豁免」默认不授予（见 D4）。

结果提交丢响应：record_outcome 的 COMMIT 已确认但响应丢失时，按持久事实重试同一 record 调用即得 ALREADY_PRESENT（终态严格等值幂等），不重复写、不改变额度。

执行异常（ToolValidationError，如结果超 1e18）：确定性失败，持久登记 received 加 error_code=tool_execution_failed、无正文；预留不退（该次获准尝试已实际发生）。选择 received 而非 not_sent 的理由：与模型侧「收到明确失败响应」的结构一致（有确定终态、无结果正文），且不引入第四种 disposition、不改 002 状态机约束。

取消（cancel_activity）：活动 cancelled 后 admit_tool 直接拒绝（cancelled）；已 admitted 未 mark 的操作经 recover 路径收敛 unknown；tools_reserved 与模型次数、费用预留同等「不动」，维持「取消不退款」的现行纪律。

来源替换与范围 CAS：admit_tool 的锁后来源复核失败抛 ScopeConflict 整事务回滚（无预扣）；admitted 后 scope_revision 变化使 current 检查失败，后续 mark 拒绝、record 只能登记 unknown。

旧代次晚到：execution_generation 低于活动当前代次的未决操作由 recover_obsolete_operations 收敛 unknown；其 permit 已不可用于 mark 或 record（current 检查含代次相等）。

并发同键：两事务竞争同一 (activity_id, operation_id)，主键与 FOR UPDATE 保证恰好一个插入成功，另一个在键占用处拒绝；本地执行恰好一次成立。

预算耗尽：tools_reserved 达到 max_tool_calls 后 admit_tool 以预算类错误码拒绝；跨进程、跨重启、跨恢复该事实仅存于持久列，任何内存计数不参与约束。

DB 不可用：admit_tool、mark、record 全部映射 AdmissionUnavailable，编排层不执行、不登记、不重试循环；与 FLOW-005「DB 不可用时拒绝有副作用动作」一致。

### B7 结果提交、读取与消费边界

工具成功结果经 record_outcome 持久提交：disposition=RECEIVED 加正文三元组（payload_format='text'，value 为 execute 返回的规范化数字字符串，经 build_business_payload 封套与先拒后写长度检查），与 received 终态同事务提交，COMMIT 确认后返回 RECORDED。读取沿 read_committed_result/list_committed_results 原样：绑定一致性（admission、代次、范围）与来源有效性检查、失效不投影正文、取消后历史可读但不授予新权。CommittedResultSnapshot 增加只读字段 kind（自操作行投影），调用方可区分工具与模型成果；_RESULT_READ_SQL 增加一列投影。工具输出属低信任：正文封套与字节完整性检查全部适用，不因「本地计算」提升信任；不提升任何 system 权限。消费边界（首切片）：工具结果提交后仅可只读恢复；不自动成为任何后续模型请求的输入，不解除 gateway 与 admit 双层的 input_result 加 allowed_tools 互斥，未知不自动重发。若未来需要「模型→工具→模型」，须先以具体契约解禁互斥并定义工具消息的引用形态，属 D3 待决，本切片不实施。

### B8 与 Windows 窗口、停止与结算的整合

单次工具执行不进入 Windows worker 路径，也不改 D3。推荐形态为进程内受监督工具动作（service 层编排函数，建议签名 execute_tool_action(activity_id, executor_id, operation_id, plan, run_tag) -> ToolActionOutcome）：inspect_window 确认可行→claim_lease（进程以自身 current_process_session_id 提供 running_owner_session_id，window_seconds 取显式配置的较小值）预扣时间→admit_tool 预扣次数→mark→execute→record→begin_window_close→settle_execution_window，异常路径全部有界收尾。持久纪律（租约互斥、代次递增、时间守恒 C≤W、关门先于结算、结算幂等）与 SUP 窗口完全同源，但不创建 NamedJob、无子进程树：纯本地有界计算没有需要强制停止的执行单元，SEC-002「停止只处理本应用自有工作」由「无自有子进程」平凡满足；工具不主动合作冒充强制停止的问题不存在（执行体即本进程函数，异常与超时由编排层有界等待与活动租约过期共同兜底）。不为工具次数重写 D3；若未来工具引入 IO、子进程或网络，必须整体迁移进 Windows 监督窗口路径并重新过权限审计，该边界写入 D2。时间计入：工具动作墙钟计入既有时间账本（claim 预扣、settle 结算），不新增时间列。

### B9 最小接口与修改文件清单

建议新增或修改（全部未实施）：backend/migrations/008_activity_tool_budget.sql（新）；backend/app/activities/repository.py（ActivitySpec 增 max_tool_calls 字段与 create_activity 校验写入：allowed_tools 非空则 max_tool_calls 必须为 1 至 2147483647 整数，allowed_tools 为空则必须为 NULL；新增 admit_tool_operation；CommittedResultSnapshot 与 _RESULT_READ_SQL 增 kind）；backend/app/capabilities/contracts.py（新增 ToolIntent 冻结数据类：context、call_id、name、arguments 规范字节摘要；LedgerOutcome、RecordOutcome、AdmissionPermit 零改动复用）；backend/app/activities/service.py（新增 execute_tool_action 编排与失败映射：plan 校验→claim→admit_tool→mark→execute→record→close→settle，异常到状态字符串的映射对齐 ContinuationOutcome 风格）；backend/tests/test_activity_tools.py（新测试文件）。明确不修改：tools.py、gateway.py 模型路径与前置互斥、transport.py、one_call.py、协议3、worker_command、session.py、supervisor_main.py、launcher.py、gate.py、既有测试断言。旧无工具调用方兼容：ActivitySpec.max_tool_calls 默认 None；allowed_tools 空的活动全部既有行为、错误码与测试不变。允许一次显式工具动作即满足首切片；不自动加模型→工具→模型循环、公开 API、页面或后台轮询。

### B10 设计推演轨迹（非运行测试）

以下四条为纸面推演，逐步核对持久守恒；G 值用符号表示，不硬编码任何已有执行代次。设活动配置 max_tool_calls=3、allowed_tools=(finite_calculate,)、max_requests=5。

轨迹一（正常）：初始 tools_reserved=0、代次 G0、pending。claim 得 G1、R=W_tool；admit_tool(op-A) 后 tools_reserved=1、op-A reserved；mark 后 dispatched；execute 得「3」；record 后 op-A received 带正文行（hash h3）；close 关门；settle 后 S+=C、R=0、G2。终态守恒：工具额度 1/3，模型请求 0/5，正文可读 committed_current。

轨迹二（同键重试与新键）：对 op-A 再次 admit_tool 拒绝（键占用），tools_reserved 仍 1，read(op-A) 返回已提交正文（幂等读不执行）；以新键 op-B 提交相同参数获准，tools_reserved=2，独立操作行独立正文。守恒：实际准入次数=预扣增量=2，重复键与幂等读均不改变额度。

轨迹三（执行后提交未知）：op-C admit 后 tools_reserved=3（额度满）、mark dispatched、execute 完成但进程在 record 前崩溃。持久事实：op-C dispatched、无正文行、tools_reserved=3。租约过期后 recover 收敛 op-C 为 unknown（error_code=executor_lost），额度仍 3/3；下一次 admit_tool 因预算拒绝；read(op-C) 为 UNRESOLVED 无正文；不自动重发。任何进程重启后上述事实不变（全部在持久列）。

轨迹四（取消与范围变化）：变体一，revise_scope 使 scope_revision 变化后 admit_tool(op-D) 在锁后复核抛 ScopeConflict，整事务回滚，tools_reserved 仍 3、无操作行；变体二，op-E 在额度扩容后 admit 成功（tools_reserved=4/扩容后上限）而 mark 前活动被取消，mark 抛 denied，编排层 record UNKNOWN 诊断收敛 op-E 为 unknown，预留保留；两变体下守恒均成立且错误路径可区分（ScopeConflict 回滚无痕迹 versus 取消收敛留痕）。

## C. 最小验收矩阵（留待实现卡运行，本卡不执行）

按真实风险选取，每项给可观察断言、合成输入或故障、证据级别与阶段。

一、权限拒绝无执行无预扣：白名单缺名、max_tool_calls 为 NULL、allowed_tools 为空三种输入下 admit_tool 拒绝且错误码可区分；断言 activities 无新操作行、tools_reserved 不变、ToolRegistry.execute 未被调用（监控替身）。阶段离线（合成账本），B 级证据。

二、有限额度耗尽与跨恢复不重置：max_tool_calls=2 的活动连续获准两次后第三次拒绝；关闭全部连接模拟进程重启后重连仍拒绝；断言 tools_reserved 列值与准入次数相等且无任何路径减一。阶段真实合成 PG，A 级证据。

三、并发同键只执行一次：两个并发事务 admit_tool 同键，断言恰好一个成功、另一个收到键占用拒绝；执行监控替身断言 execute 恰一次。阶段真实合成 PG 并发用例，A 级证据。

四、同键改参拒绝：同键不同参数 admit 拒绝；构造 record 时 arguments_sha256 不匹配按完整性错误拒绝。阶段离线加真实 PG 各一，B 加 A 级。

五、提交与响应丢失边界：dispatched 后注入崩溃（替身抛出）断言恢复收敛 unknown、预留保留、无正文可读、record 重试得 ALREADY_PRESENT 不重复写正文。阶段真实合成 PG，A 级证据。

六、取消、范围变化、过期与停止窗口：取消后 admit 拒绝；admitted 后取消时 mark 拒绝且 record 仅接受 UNKNOWN 诊断；scope 变化后 admit 抛 ScopeConflict 回滚；租约过期后旧代次操作由 recover_obsolete 收敛。阶段离线（替代账本）覆盖分支、真实 PG 覆盖持久性，B 加 A 级。

七、结果绑定与完整性：工具正文行的 admission/代次/范围绑定核验、hash 重算、失效不投影、kind 字段正确区分工具与模型。G3 既有证据（test_activity_results 与 090 real 批次）直接引用适用；仅对 kind 投影做增量检查。阶段离线加真实合成 PG，B 加 A 级。

八、已有无工具调用方兼容：allowed_tools 空、max_tool_calls NULL 的活动上，既有全部离线、PG、Windows 行为与断言不变。复用 088/090 既有证据，不默认重跑；仅对 ActivitySpec 默认值与 008 迁移后旧行投影补静态与合成库检查。B 级。

三层验证各自补的缺口：离线合成检查覆盖全部分支逻辑与错误码映射（快、无基础设施）；真实合成 PG 覆盖持久性、并发、崩溃恢复与迁移非空安全（这是离线无法证明的核心）；最小 Windows 组合仅在应用接线后做一例端到端显式工具动作（进程内路径不依赖 Windows 基础设施，此项为可选增量而非本合同前置）。未经修改的 D3 停止、G3 正文提交、090 范围 CAS 与 continuation 证据按原适用范围直接引用，不整套重跑。真实 provider 不是本切片前置（工具执行无模型调用）。全部留待实现卡，本卡零运行。

## D. 合并变更决定包（供编排或用户一次决定）

D1（主要，持久模型与迁移策略）：批准 008 迁移按 B3 契约实施，含 activities 两列、activity_operations 的 kind 列与模型专属列放宽、非空安全执行策略。影响：首个允许在已有数据活动库执行的迁移；已有行零改值、旧行为不变。推荐理由：复用操作状态机与恢复读路径，改动面最小。最小替代：独立 activity_tool_operations 新表加独立恢复查询——语义更干净但恢复、幂等、读取三套逻辑双份，实现与审计成本显著更高。不批准则 G5 无持久账本，工具只能停留在计划展示。

D2（主要，工具执行权与运行位置）：批准「进程内受租约保护执行」作为首切片工具运行位置（B8），并接受其边界：finite_calculate 为纯本地有界确定性计算，无子进程、无网络、无强制停止需求；任何未来含 IO、子进程或网络的工具必须迁移进 Windows 监督窗口路径并另过权限审计。影响：D3 与 Windows 链零改动、实现最小；代价是工具与模型调用走两套窗口形态（模型走 SUP、工具走进程内编排），需在架构文档注明。最小替代：工具也走 SUP+worker 的 tool_execute 任务——统一形态但为微秒级本地计算引入完整进程树开销，且需扩展协议3。不批准进程内方案则需先批准协议扩展，工期与审计面更大。

D3（主要，可延后，工具结果作为后续模型输入）：本切片明确不解除 gateway 与 admit 双层的 input_result 加 allowed_tools 互斥，工具结果不自动成为模型输入；后续如需「模型→工具→模型」最小链，须另立具体契约（tool 消息引用形态、互斥解禁条件、计划与执行的配对校验）再批。影响：当前无；该互斥保持使 G3/G4 纪律零豁免。最小替代：本切片即解禁——拒绝理由：一次改动两个高危边界（续接授权与工具授权），审计面不可控。无决定则维持互斥，不阻塞首切片。

D4（次要，默认拒绝，确定性重算豁免）：对已收敛 unknown 的本地确定性工具操作，是否允许凭「纯函数无外部副作用」豁免未知纪律自动重算。推荐维持默认拒绝（显式新操作重新准入，额度照扣），理由：豁免需要定义「纯确定性工具」的可审计判定且为未知收敛开辟第二条路径，收益仅省一次额度计数。若用户希望豁免，须明确批准并限定于 D2 边界内的工具类。最小替代：无（维持现状即零成本）。不决定则默认拒绝生效。

无需批准项（执行者已收敛）：operation_id 由调用方显式命名的既有惯例、execute 异常映射 received 加 tool_execution_failed、reserved 经 mark_dispatch_started 推进的复用、CommittedResultSnapshot 增 kind、约束名按 pg_constraint 实查、错误码文案。无「无变更可写」情形：D1 与 D2 是真实的主要变更，缺少批准不得实施。

## 操作与验证详情

关联需求与架构：NFR-002/003、SEC-001/002、INT-002；MOD-007、FLOW-005、DATA-007、API-006；父 TASK-090，相邻 TASK-083/084（D3）、TASK-088/089（G3）。

实际操作：按合同顺序读取规则、文档与源码；指纹核验（三份规则与 rules-snapshot 一致；五个核心文件与 090 冻结清单一致）；27 个文件读入清单与部分读入范围见 [files-read-hashes.json](../evidence/TASK-091/files-read-hashes.json)。产品快照只读，零写入、零运行、零端口、零容器。实际投入约 55 分钟，低于 120 分钟上限，完成即停。本卡没有运行尝试、失败尝试或修正轮。

既有证据复用边界：090 的 3/3 真实入口、20.421/2400 秒、Windows 1/6 与 67 项冻结 hash 原样保留并作为本卡对象基线，不清零、不重审；083/084 的 D3 与 088/089 的 G3 证据按其验收范围引用；工具相关的四个既有测试用例按 A2 所列以 B 级证据引用。未覆盖范围：test_activity_scope.py 与 test_activity_continuation.py 仅登记 hash 未通读，其行为结论全部沿 090 验收引用，未独立复核其内部断言；此为有意的最小读取，不影响本卡结论，因其覆盖的行为本卡零改动。

与合同的偏差：无实质偏差。一处口径说明：执行窗口为 WorkBuddy 会话（GLM-5.3-Flash），符合「原窗口不可用时同等胜任 A+ 新窗口承接、不换编号」的安排，资源标签按执行动态文档口径不虚构平台型号。

最终只读一致性核对已做一次：合同各条与 A 事实、D 决定包交叉核对无矛盾；B5 的「reserved 不能直接 record」以 repository.py 1202 行为据，B8 的「工具不进 Windows 路径」与 B2 的计数单位、B10 的守恒轨迹互洽。所有动态项未运行，静态正确不等于真实通过。

## 未完成、未验证与风险

未完成：008 迁移、admit_tool_operation、execute_tool_action、kind 投影及相关测试全部未实现（本卡为设计卡，须待 D1/D2 批准后另卡实施）；架构动态文档与本结果的关系由编排裁定后同步，本卡不改共享文档。

未验证：全部动态行为（持久预扣、并发、崩溃恢复、迁移非空执行）未运行；「工具执行在应用进程内不失控」基于 Decimal 有界计算的推导，非运行证据。

风险：一、008 对已有库的首次非空 ALTER 若实现时约束名处理不当会失败，已在 B3 注明实查 pg_constraint；二、进程内路径绕过 Windows 强制停止的前提是工具保持纯本地有界计算，该前提被破坏时必须回走 Windows 路径（D2 已写死边界）；三、admit_tool 与既有 admit 的校验子集若有遗漏（例如新增预算检查遗漏关门条件），可能构成越权，验收矩阵第一、六项正是针对此。无其他已知风险。

## 交回事项

待同步文档（归编排）：执行动态文档登记本卡已返回；架构动态文档在 D1/D2 获批后登记 008 契约与进程内执行边界；文档变更记录按实际时间补 CHG。本卡不改这些文件。

合格经验候选：无新的跨项目可复用错误经验（本次为纯设计收敛，无失败修正）。

必须人工：仅转交本卡与带回结果路径；不要求密码、Docker 或实现细节选择。建议下一步：编排读本结果与决定包，组织 D1/D2（必要时 D3/D4）一次决定；批准后按本合同出 G5 完整实施卡（实现加离线与真实合成 PG 验证同卡），稳定后按 V4 另卡隔离独立审计。

本文件不代替编排最终验收；不宣告 G5 实施完成或 STEP-006/008 完成。后续补证按轮次追加，保留历史。
