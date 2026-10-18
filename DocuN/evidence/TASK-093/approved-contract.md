# G5独立审计原始验收合同摘录

来源D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-091-result.md，修正轮01的B1—B10与C1—C12，正文原样摘录，止于D批准提案之前。源SHA256 a6dfdd231ea1cac76497c1a6c3dd77a77e7b653cac2231850d95d49128c92866。该合同经用户2026-09-30明确批准，已授予TASK092实现；标题“尚未实施/未来检查”是设计时点原文，不代表当前产品状态。本文件不包含092结果自评、实现聊天或编排验收结论。读实际源码和原始证据形成审计判断。
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

