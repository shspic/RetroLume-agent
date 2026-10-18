# TASK-097 / R-091 续作01当前T01—T18

状态：部分完成。当前产品主链和14个有限浏览器场景已形成有效证据；最终观察器修正02的完整SUP业务动态复验not_run。不是独立验收。旧8批整体FAIL、09/10整体FAIL全部保留；11整体PASS不能代替整卡通过。

本表根 `D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097/`。09=`integration-09-combined`，10=`integration-10-repair`，11=`integration-11-ui-only`，C=`continuation-01`。旧具体方法/预期和原件见根acceptance-matrix.md；对应字节、控制流增量和原始导入的绑定见C/evidence-applicability.json。每个场景以下同时保留所绑定方法整体状态，不能把未执行或失败部分转换为PASS。

|编号|当前结论及实际证据|复用与限制|
|---|---|---|
|T01 范围/位置/身份|限定通过。09 `final_first_followup_citations`实际选TXT/MD/就绪PDF，双语目标；catalog、hash、TXT行与PDF物理页1/补充页2从持久结果与回查API逐字段比对，XSS原文纯文本；09 `current_first_followup_atomic`保存真实目录。|旧02PG的authoritative_txt_md_pdf_supplement_scope_and_utf8、旧纯函数revision0/3/5等字节/流程复用；无OCR质量/向量质量结论。|
|T02 未选/失效过滤|已实施边界限定通过。09 `source_availability_withdrawal`真实PG将独立来源current_version撤销、revision实际+1；引用409，新动作409、0新send，原body hash保留。|旧02范围外高频候选、未核PDF/替换场景复用。新例是来源可用性撤销等效反例，**完整产品删除Must未实现/物理删除not_run**，不把方法名deleted当删除证据。|
|T03 输入/歧义/不足/冲突|限定通过。10 `http_bounds_and_forged_citation_zero_call`空400、1025字符422，无SUP/预扣；C offline01/02验证1字、1024字/4096UTF8字节及溢出。|原纯函数Spring/同名歧义、零候选与词项/片段上界；旧05三个真实结构结果clarification/no_evidence/conflict的调用计账复用。不证明供应商语义识别质量。|
|T04 配置/预算边界|限定通过。C current contracts输出1/256合法，0/257/布尔拒绝且旧L1/继续层保留；10真实HTTP请求1024字节413/输出活动128而学习256时409，两个活动预扣0；09缺学习能力UI读取/新建/取消保留。|旧02真实L0/L1/L2坏配/缺配、预算读与旧config测试复用。没有逐个数据库CHECK全域重跑；合法正常256在09真实主链通过。|
|T05 最终正常原子链|通过所测主链。09当前first→followup真实launcher/SUP/worker/Job/gateway、两个send，received与结果xmin相同；规范goal/catalog/body/hash，父operation对应真实首成果，正文read_status committed_current后呈现。整页刷新与07保留活动冷读0新增学习POST。|最后gateway/confirmed/客户端匹配修正后的当前产品与初轮最终完全同字节；不只用compile/build证明。09 `business-checks.json#current_first_followup_atomic`与browser-persistent-first.json。|
|T06 非法结果/引用/支持性|限定通过。C当前API严格确认与受信字段关闭、内部未知/混用/无profile保留命名空间拒绝0admit/send；10真实伪引用404，09注入片段仍仅user证据、无工具。|旧02/05已收到非法引用/JSON→received且无body、旧纯函数错误版本/hash/位置/未知字段及固定语义正反例逐句证据复用。ID/位置合法不等于结论正确，真实provider语义质量not_run。|
|T07 原文/失效/安全显示|通过有限场景。09真实UTF8/行段、PDF页及补充引用；09合成409失效文案、10真实lc_forged404+UI同错误显示，慢原页不得覆盖后点补充页2。模型img/onerror文本没有img元素或执行。|旧02真实版本替换与旧07原文转义/换行验证复用，四类最终资源真实服务匹配。不同HTTP读取不宣称共同SQL快照。|
|T08 首槽/真并发|部分完成。09真实不同目标Barrier并发、唯一持久槽位/获胜目标/1send、另一请求失败关闭，不把旧正文套给新目标。10重试上述业务断言执行到额外生命周期断言前均成立；额外“两完整SUP回执”断言FAIL，原文保留。|原05异UUID同目标真两SUP竞争/顺序异文409和同文稳定槽位继续有效。09另一候选在计数观察器JSON读失败，10另一真实SUP创建后未Resume因观察器PermissionError失败；不能把它们充作两份正常SUP不同目标竞争通过。最终修正02完整动态not_run。|
|T09 丢回执/UNKNOWN/显式重试|通过分层范围。10 `lost_response_matching_conflict`服务器返回07原持久事实、浏览器故意丢回执，刷新保留意图、GET核对同输入移除/异输入保留拒绝，放弃0POST；同槽位显式1POST无新模型。10 `unknown_same_key_retry_abandon`合成HTTP UNKNOWN→GET核对→用户同键1POST，刷新/放弃0POST。|真正transport UNKNOWN、NOT_SENT和原子提交成功ack丢失来自旧02/05，仍有效；UI UNKNOWN替身不是新的真实provider未知证明。|
|T10 首成果/续问/旧继续|通过所测及复用。09当前真正首成果由G4父凭证、新操作重新准入续问。10受信内部合法恢复后同key HTTP仅返原事实，send总增1。|旧05普通model父结果/继续真实链、旧协议3/4和tool凭证隔离直接用例复用；原普通案例缺一份SessionOutcome继续披露，不新增一次普通调用填旧缺件。|
|T11 硬停/取消/晚到|通过分层范围。09约85.953秒SUP真实deadline、Jobterminate时active>0→tree0，R90留存、不退款，旧父仍可读；10已有内部SUP入口显式同主机/会话声明后G递增、折叠90一次、同key不折第二次。09损坏台账仍读/两步取消UI（cancel响应替身）；真实取消/晚到来源反例复用旧02/05。|HTTP默认SessionConfig恢复声明false，09恢复失败关闭是既有边界；10**没有开启产品HTTP旧running恢复配置**。硬停杀死worker的Python gate finally不适用，不能造gate-close。|
|T12 意图先存/恢复/失败关闭|通过有限场景。09 first/follow POST前真实台账已submitted，无凭据/返回body；10匹配/冲突、旧格式/未知重试/放弃；11已选资料+坏台账点创建仍0POST、Storage.setItem异常点首学0POST/0SUP/0send/请求费用预扣0。读取仍可用。|原09-intents纯函数兼容/坏格式及存储失败复用，原corrupt按钮未选资料的弱断言不单独充足，11有实际点击补证。|
|T13 轮询/上下文迟到|通过有限受控场景。09慢操作切换、引用卸载、迟到核对不能把活动选回；10慢引用→补充页2、慢活动详情切换、poll真实列表URL受控running标记，hold期间12秒无重叠、隐藏暂停/显式可见恢复1读、卸载12秒0读。|时钟/visibility/running标记仅UI测试替身，HTTP读到真实097应用，未改系统时间或SUP时钟。旧D2主体与095/096有效关闭结论复用，不重审。|
|T14 PG/HTTP/四读|限定通过。09当前两次received/结果xmin一致、HTTP守卫422与撤销409；10实际HTTP请求/输出限额/伪引用、恢复同键只读；11存储失败后的真实费用/请求0。|旧02五PG方法、02/04三HTTP方法及六个查询每次单SELECT/列表无body复用；repository与写锁/恢复主体本续作零变化，不重跑全量。|
|T15 Windows真实监督|部分完成。新实际SUP8（总23）：09五、10三；新增6次claim/Job、7次Resume及一次创建未Resume；真实首续、硬停/声明恢复都有真实G/Job/run_tag/收据/树0。新增send6，全为合成transport，无provider socket。|09另一个业务候选的JSONDecodeError发生CreateProcess前，不计真实SUP但另记业务尝试；10一次已创建未Resume有原tmp身份且计入。观察器修正02仅Windows文件并发PASS，**完整业务动态not_run**；旧普通缺SessionOutcome不补造。|
|T16 当前浏览器|14个不同有限场景有当前产品有效PASS，09有效7、10有效5、11有效2；完整新主链/引用/刷新、保留冷恢复、恢复反例和写前关闭均覆盖。10/11browser aggregate true；09被有据结束卡住的本卡Node，aggregate false保留。|浏览器次数新3/总6、driver新3/总7；独立context、请求时间线、14成功截图及2失败截图原件，poll中止无伪造截图。UI替身与真实PG/Windows层各自标识，非供应商质量验收。|
|T17 3/4/profile/敏感信息|通过直接契约及有限复用。C当前5定向测试含严格布尔、输出数值、source_revision0..INTMAX、未知profile/字段/混用及保留namespace无profile拒绝；09真实HTTP额外profile/scope422，无新调用。|旧协议3/4/无profile直接用例及普通model真实链复用。浏览器09主动outside.invalid探针被route拒绝；仅声明本测试Python/浏览器context边界，非全机防火墙结论。凭据stdin/内存/子环境，DSN/key不入浏览器/结果/外发。|
|T18 冻结/构建/收尾|证据整理和当前产品绑定完成，整体仍部分。C pre原字节/七规则、每批as-run/导入hash/post、最终snapshot/有限diff/构建链；产品与初轮final完全同字节，16构建输入与build05、四产物与09实际服务匹配，无新build。资源final stopped/Pid0/trees0/ports释放，保留库卷及07/09真实样本。|原8FAIL、09/10FAIL及最后观察器动态not_run/旧缺件保留。报告精确计数/测量与30秒保守收尾额度，不用compile/file stress当Windows完整通过；独立终审尚未安排/未完成。|

最终动态字节适用性：本续作无backend/app、frontend/src/dist、README或产品配置变更；因此当前全部产品字节直接绑定09主链、10/11反例。新增/改变的是本卡夹具和证据代码。09/10旧夹具精确字节在C/as-run中；最后bootstrap/publication/processes修正只适用于其离线文件/compile与11无SUP的app启动，不能扩为最后夹具Windows业务绿灯。
