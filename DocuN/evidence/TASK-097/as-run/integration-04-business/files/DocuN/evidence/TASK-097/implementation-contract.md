# TASK-097 / R-091 实施合同冻结

冻结时间为2026-10-02，Asia/Shanghai。执行身份为Codex desktop中的Codex，系统标识基于GPT-6，客户端精确模型版本不可读，不虚构型号。工作目录为D:/shspic/project_NO3_RetroLume-agent。规则为根AGENTS.md及公共V4.0、CHG-0003。7个公共规则指纹全部匹配锁定清单。输入索引SHA256为91110dbd7563b1a170f5605cb3fc42b164dd2224ec8db327f3c8e9add5f2605c，71个输入对象全部匹配。原字节已保存pre/，不是Git提交基线。

本合同在产品修改前冻结。授权终点为合成环境候选实现、定向验证及资源收尾，不是G7独立验收。无子Agent、无真实供应商、无付费、无用户库、无DDL模型扩展。原claim、admit、mark、record、settle、cancel、recover和停止实现不改。

## 权威与接口

- POST /api/activities/{activity_id}/learning/first接受business_key、goal、confirmed。business_key为客户端规范UUID，goal去首尾空白，confirmed必须为true。客户端不得提供来源、版本、范围修订、路径、正文、profile、system、工具、执行身份、服务或预算。首次槽位由服务端产生，与客户端UUID无关。
- POST /api/activities/{activity_id}/learning/followups接受business_key、parent_operation_id、question、confirmed。父成果必须为同活动当前model学习成果；继承其受信目标，重新从活动权威范围检索，构造现有G4父消费凭证。旧普通model继续URL及行为保持。
- GET /api/activities/{activity_id}/learning/intents/{business_key}只核持久槽位或该续问键，不发调用。首次读取不依赖客户端目标或正文缓存。既有四类读取接口保持单条业务SELECT；操作列表保持无正文投影。
- GET /api/activities/{activity_id}/learning/operations/{operation_id}/citations/{evidence_id}从持久catalog限定身份，复核范围、版本、原件和片段摘要与位置，返回有限原文、TXT/MD行段或PDF物理页、原文或用户补充身份。PDF原页显示复用既有materials/pdf只读原件URL和expected_version，认证默认行为不改。

空或超过1024字符、4096 UTF-8字节、24查询词项的目标或问题在claim前拒绝。confirmed缺失或false拒绝。无具体词项或多个同名来源不能唯一定位时返回最少追问，零模型计账；零候选返回词项证据不足，不扩大范围。资料和历史助手正文均为低信任内容，不授予权限。

## 有限证据与数值

应用读取活动实际scope_revision及全部SourceSnapshot，来源revision域为0..2147483647，使用仓储实际值，不人为递增。现evidence纯函数revision下限1将兼容调整至0。先核未删除、当前版本与实际revision一致、PDF confirmed及完整有效核对页，再读取；任何活动来源失效整体关闭新动作，未就绪源不进入包。最多10来源、累计5 MiB原件、50物理页每PDF、100文字单元、512片段。超限明确要求缩小活动范围或问题，不静默发送整库。

词项模式terms.v1复用既有位置切片、SHA256和中英候选排名。有限top-k为8，包最多12000字符、24000 UTF-8字节，不超限剪掉完整片段。片段不足以容纳则拒绝缩小范围。catalog保存应用分配的lc_不透明ID、source_id、version_id、真实source_revision、title、format、original_sha256、unit_sha256、fragment_sha256、原evidence ID、行与offset、physical_page、origin_kind及supplement_id。外发只含目标/问题、必要片段及本次引用ID和身份，不含DSN、密钥、父消费凭证、内部目录或整篇文件。

L0/L1/L2旧行为保持。新增显式learning配置仅接受profile=learning.v1及max_output_tokens=1..256，缺配或坏配只关闭学习入口。输出上限不超过旧继续256、L1活动上限或L2服务上限。请求在claim前按真实供应商payload字节检查活动与服务上限。费用预扣仍来自原服务端活动配置及账本，无新增默认免费模型预算。新调用工具集合恒为空。

## 请求身份与首次槽位

规范摘要为SHA256稳定JSON，绑定learning.v1、action、activity_id、规范goal/question、scope_revision、按source_id排序的完整来源快照、父operation/hash以及输出上限。首次operation_id为learn-first-v1/加64位摘要。续问为learn-next-v1/{business_key}/加64位摘要，长度不超过128。

只读槽位助手最多读两个首槽操作，多个为完整性错误。首次任何既存槽位都阻止第二个首调用，同摘要返回事实，异摘要明确learning_input_conflict。未知和已结束无正文也占槽位，不换键。摘要编码在既有operation_id中，所以UNKNOWN无需新增持久字段也能复核异文。客户端首次UUID不是服务器授权或可制造的新槽位。

应用预查后，经真实run_one_call、launcher、SUP、worker、Job和gateway链执行。worker取得原独占租约后的gateway再次核profile、scope与首槽，防止预查竞态和排队请求在首调用结算后再次发送。现有ActivityMutex、独占租约及admit操作唯一约束继续负责真实竞争，既有锁序不改变。没有admit的拒绝未形成持久调用槽位，合法同键显式重试可重新尝试；一旦有持久操作，无论NOT_SENT、FAILED或UNKNOWN都只返回事实。

## 受信profile与原子提交

ModelCallRequest可选learning_profile为严格learning.v1内部类型，未知版本、额外字段、混用工具或不匹配消息/目标/范围拒绝。OneCallInput原三字段、worker协议3与tool协议4外层字段、父凭证及回执三值保持不变；无profile调用原行为保持。profile只来自应用；模型或资料字符串不能启用它。

模型输出只接受JSON对象，恰有kind、message、segments、questions。kind为answer、clarification、no_evidence、conflict。segments恰有text与citations，引用只能是本次允许ID。answer每段至少一引用；clarification至少一个必要问题；no_evidence不含确定回答段；conflict至少关联两个不同来源。每种有严格条数、字符、UTF-8和未知字段检查。引用目录由应用传入，模型不提供或覆盖goal、catalog、权限、模式或已验证标志。

gateway在原record_outcome前规范化为版本化业务JSON，含profile、action、request_sha256、goal、question、parent_operation_id、scope_revision、sources、retrieval_mode、catalog、result及固定能力说明。正文与received一起原子保存；不存在提交后追加目标/引用的第二笔写。已知收到非法结构为received失败无正文；真正提交未确认为原UNKNOWN，保留预留且不重发。引用身份/位置检查与结论支持性分开，不能把ID合法当答案正确。

## 客户端与恢复

活动工作区提供目标输入和确认，显示实际资料范围、有限四账、服务用途和词项限制。缺学习配置时显示关闭原因。结果按四种类型展示，所有文本由React安全文本显示；不创建HTML宿主。引用回查按版本，替换或删源为明确409不可用。慢引用回包用序号、AbortController及组件卸载防护，切换活动/操作时不串正文。

新首次及学习续问意图在POST前持久记录business_key、规范用户输入、活动及父业务键，不存返回正文、授权物或密钥。兼容旧create/continue格式；损坏台账关闭依赖恢复的新动作，读取和两步取消仍可用。刷新只GET，核对、同键显式重试和放弃分立。放弃不撤回远端或退款。unknown保留未确认提示，无后台自主循环。原D2轮询不重叠、隐藏暂停、卸载和迟到保护保持。

## 冻结样例

- 正常英文与中文目标对应就绪TXT、MD、已核PDF原文及用户补充，模型返回answer分段和lc_ID；读取目标、目录及原文完全对应版本。
- Spring范围内同名两份资料且目标只写Spring，返回clarification_required，询问目标领域，零模型调用。
- 没有词项候选时返回no_evidence预检查，零received；明确调用返回no_evidence时为真实received及正文，不隐藏计账。
- 两份原文分别声称值为10与20，模型conflict必须关联两不同来源，保留矛盾、不裁决。
- 模型返回lc_fake、原evidenceID、旧包ID、额外goal或非法JSON，received失败且无可用正文；资料中要求执行脚本仍只是文本。
- 组包后替换来源或改范围，claim/admit或record权威拒绝；原有效成果不覆盖。已提交引用源替换后409。
- 首次同摘要不同客户端键读取同槽；同键异目标或范围明确冲突。真正并发至多一次外发。
- 先提交后丢HTTP响应，刷新GET能找到正文；DeliveryUnknown保留未知和预留，同键核对不再次发送。

## 验收矩阵与证据安排

- T01 新纯函数/合成来源组包及真实PG资料读取，覆盖中英、TXT/MD/PDF/补充hash、位置和真实revision。
- T02 新组包及PG失效例，先过滤删除/替换/未核PDF/未选近似源，拒绝新调用。
- T03 输入/歧义/零候选纯函数与HTTP；模型四类合成响应严格校验，缺证据不自动重试。
- T04 分层配置定向离线兼容与学习预算HTTP前置拒绝，核发送计数。
- T05 真实Windows+PG+HTTP首次完整链，检查目标/catalog/正文/received原子事实及刷新读取。
- T06 profile与输出负例纯函数/gateway；错版本/hash/位置引用回查PG，支持性固定正反例逐句人工核证。
- T07 真实UTF-8/CRLF/XSS文本及PDF位置回查，浏览器安全显示，版本替换409。
- T08 同文/异文/不同UUID/真实并发及排队槽位复核，PG+Windows真实发送与账本核对。
- T09 NOT_SENT、DeliveryUnknown、HTTP丢响应、已提交后丢响应事实恢复，不自动新键与重扣。
- T10 真正首成果派生学习续问；旧protocol3无profile普通model和protocol4/tool父隔离定向兼容。
- T11 来源替换和取消晚到，最小真实Job硬停/树零与账本，既有D3主体证据精确复用。
- T12 浏览器先存再发、旧意图、坏台账、刷新只GET、一次POST、核对/重试/放弃。
- T13 浏览器慢回包/切换/隐藏/轮询/卸载防串，原D2控制直接保留。
- T14 新只读投影与原子结果真实PG；运行时计数四类读取单SQL及列表不取正文，旧未改回归结论复用。
- T15 真实Windows首/续/竞争或取消组合，记录所有监督启动含未claim，发送、R/S/G、关门及树零。
- T16 真实浏览器选资料→创建→目标确认→首次→引用→续问→刷新主链；附关闭配置/失效/XSS/切换恢复场景，合成响应层级单列。
- T17 原3/4/无profile兼容及未知/非法/混用profile拒绝，敏感字段不进provider、browser、正文和日志。
- T18 每入口先保存as-run源码/测试/runner/fixture与hash，记录实际导入与post。构建留原始命令、输出、源到bundle清单和实际服务bundlehash，最终diff及完整资源账可重建。

## 运行口径与停止

主动总8小时，合同最多45分钟包含其中。离线每批最多60秒，累计2400秒；正式构建若更长单列实际时长。真实入口最多8、容器start8、业务Windows16、browser4。业务累计3600秒，清理600秒，每批900加清理120。预检abort计入口及实际时间，不隐藏漏时。推荐一个PG业务批加一个合并Windows/浏览器批，后续只用于有据失败/缺口复验。

资源仅精确e49d3acc3c1be13d670af68bca2b082fea4faeeb9b9babe69df7f1d3941696a4容器、原命名卷、127.0.0.1:55441、097专库和最小角色，应用18097、前端必要15197。完整inspect仅内存白名单，绝不打印Env。先核未被占用、不创建替代容器。口令仅stdin/短期内存/本卡进程env，不存文件/argv/log。只在097空库顺序001—008，无新迁移。所有资料和响应合成，传输边界替身，真实监督/Job/仓储不替换，socket守卫限制本卡loopback，浏览器阻断并记录其他请求。

finally只清本卡进程树并确认树零、端口释放、精确容器Running=false/Pid=0，保留097库与卷。每例FK定向清理，不drop未知对象。资源冲突、清理不完整、同根因两次修正仍失败、超限或主要模型/权限/停止扩展即停受影响部分。卡内测试只是自查，完整稳定后由编排另卡隔离独立审计。

## 实施前勘误01

既有操作读取路由使用单路径段，不接受operation_id中的斜线。上述服务端操作ID实际采用learn-first-v1.摘要及learn-next-v1.UUID.摘要，保持原字符域和长度上限，不改既有读取URL。意图事实GET添加必须明确的action=first或followup查询，防止不存在的续问误读首槽。其余冻结预期不变。
