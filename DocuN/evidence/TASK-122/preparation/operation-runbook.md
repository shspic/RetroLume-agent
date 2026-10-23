# TASK122 后续首次正常 Q 操作包

本包是 non-executable draft，Q 继续冻结。它复用已实现且有限关闭的 Q v2，不产生运行许可、grant、operator 批准、真实根、服务、T0 或启用回执。主控以后只需围绕本包补齐真实前置、采纳最小差异并给一张精确实施与验证合同，无需再做同一批准协议设计。

项目根为 D:/shspic/project_NO3_RetroLume-agent。入口为同根 AGENTS.md，task_model、V4.0/CHG-0003、阶段07。原 TASK120 工程与 TASK121 独审的有效关闭范围继承；历史控制不通过、149 工程失败及 TASK117 旧81失败均保留。TASK120 的根64/64、PG启动64/64及旧96h不属于后续许可。

## 1 前置事实补齐

先由主控取得当前模型、账号与计量的非敏感依据。官方公开结论及每次取证时间见[官方事实](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-122/preparation/official-facts.json)，两种有依据查法仍未封闭的主题已经停止扩搜。

必须闭合的项目是当前 Flash-1017 的输入分词和服务消息模板上界、thinking disabled 的额外 reasoning 或其它计费上界，以及 Embedding-3 单项和整批 token 上界。现有代码的 request_bytes+framing 假定需要真实依据；4096只是设计可表达上限。不能以更大 margin、官方近似字符比例、样本很短或余额充足替代证明。

本人账号只需一次确认两家模型 API 项目权限、可用余额是否足以覆盖有限预算、人民币或其它币种、最高适用含税价及附加计价、API 训练/保留特约和输入权利。材料留在正常本机安全位置，只回传非敏感确认事实和官方/合同引用。可填写[账号事实草案](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-122/preparation/account-attestation.draft.json)。不提供 key、DSN、验证码、账单全文或个人截图。

唯一推荐方向是保留已采用的两个 provider 和候选，取得官方当前版本的计量/计费依据。若官方只能提供可运行 tokenizer，另由主控明确授权锁定版本的离线核证及模板分析；取得文本 token 数仍不自动证明服务 framing、额外收费或账号条款。本卡不安装、下载或运行 tokenizer，不调用计量接口，不以一次小调用代替全输入上界。依据仍不足就保持相关外发关闭，其他准备成果不撤销。

严格返回身份需要先冻结有官方或账号契约支持的有限 allowlist。公开示例仅支持候选 deepseek-flash 和 embedding-3，不能宣称已经收到真实响应。以后第一个真实请求收到响应后，按现有严格门逐笔记实际 model；不符即留收到事实和预扣并停止，不自动扩大 allowlist 或更换模型。

## 2 正常配置与非敏感 readiness

配置准备保持 disabled，模板为[部署包草案](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-122/preparation/deployment-package.draft.json)、[integration 关闭草案](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-122/preparation/integration.disabled.draft.json)和[operator 关闭草案](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-122/preparation/q-approval.disabled.draft.json)。部署包外层 schema 不是产品配置，不能直接交 loader；没有可用 grant。两个原生 schema 草案均为 enabled=false、私有路径 null。

正常部署者选择独立私有配置保存位置，之后通过服务器启动进程安全注入 RETROLUME_ACTIVITY_CONFIG、RETROLUME_INTEGRATION_CONFIG 和 RETROLUME_Q_APPROVAL_CONFIG 的绝对路径。密钥分别来自 activity 的 api_key_env，当前模板名 RETROLUME_MODEL_API_KEY，以及 embedding 固定名 RETROLUME_EMBEDDING_API_KEY。数据库和 data_exit 的声明变量、路径与角色见[readiness 清单](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-122/preparation/readiness-plan.json)。不把 .env 示例当自动 loader，不把聊天子进程的变量存在性当 API 进程已经注入。

Chat 必须为 deepseek_chat_completions/deepseek-flash、https://api.deepseek.com，显式 thinking=disabled、timeout≤10秒、请求/响应≤65536字节。learning 输出≤256、teaching/interview≤2048、HTML≤4096。Embedding 固定 zhipu_embeddings/embedding-3、https://open.bigmodel.cn/api/paas/v4、512维、每批≤4项；草案请求32768、响应65536字节，query≤1024字符且≤4096字节。保持模型语义请求 allowed_tools 为空；本地 finite_calculate 另按原8次工具账。

正常装载链是 main.create_app → load_activity_config/load_integration_config → 从 embedding 向 chat 复制同一受信 grant/manifest → configure_application。后者可能绑定 Q 根，不是只读 readiness 函数，本卡未调用。任何字段/摘要/身份未知均不能设置 verified=true。

未来正式卡允许启动后，可在同源 session 与正确 DataContext 下读取 GET /api/activities/capabilities。入口是 backend/app/activities/api.py::capabilities，包含 storage_ready/reason、provider、quota_preview、retrieval 和 q_approval。GET 会查 PG，所以本卡也没有执行。首次激活前预期 q_approval.available=false、reason=q_disabled、real_outbound_authorized=false；正常实例的真实装载证据只能在获准创建后取得，不能在此阶段预签。

当前入口不能充分证明 key 在正常 API 进程中存在、完整返回 allowlist、有效服务限额及全部 binding/price/grant 一致性。最小后续差异是在现有 capabilities 里投影已装载的非敏感状态，不新建管理平台，不调用配置/ControlHub/QAuthority 来补读状态。缺字段应返回 available=false 和逐项原因，不能写“检查通过”。完整建议字段与失败行为在 readiness-plan.json。

另有一处回执谱系的条件限制。retrieval/service.py:79 当前只接受 activation receipt.TASK 为 TASK-117 或 TASK-120；若下一回执填写新的 TASK，当前会关闭。主控先明确该字段的真实实现谱系与新的执行授权，能够如实复用既有谱系就沿现实现。只有实际需要新的TASK字段而不兼容时，才在下一实施卡定向适配该明确谱系；不冒填旧120借执行权，不开放任意TASK或削弱stage/status/hash/audit门。下一回执未定前不判必须改loader，也不重开旧五项工程缺陷。

## 3 主控一次核齐并冻结样本

主控核账号、最高适用含税价格、计量与额外收费证据、原有限独审适用范围及新增差异所需审查。原 review02 结果摘要为 ffbd03ce3d5ce34ca22570aeaaafbf72c295fc09a88a1f1c2b4fdac79dc1c12f，不把它扩称本账号或真实 Q 已通过。

冻结原八份材料精确正文。正文位于 TASK116 sample-inputs.json 的 /sources/0 至 /sources/7/text，并不存在八个可随意猜测的新材料路径。保留 UTF-8/LF 与原无尾换行约定，不加入 PDF、本人履历、用户库或任意新 memory。PDF 与恶意材料故障仍由已验零外发层覆盖。

当前逐行规则推得 N4、C4、P5、J-CODE1、J-COFFEE1、N-CONFLICT2、R3、M4，共24片，首次空缓存需6批。每片最长100 UTF-8字节，任意4片实际 canonical embedding JSON 的静态字节上界446。这个字节上界不是 token 证明。详见[片段算术](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-122/preparation/sample-fragments.json)。真实 UUID/version/revision、按 evidence_id 的排序、分组与 currentness 在获准正常导入后核齐；不沿用 TESTONLY 旧 ID 或缓存。

原116“≤8片/≤2批”规模与现实现不符。主控明确采用24片/6批作为本次精确准备规模，原有限目录512与批4不扩大。L05额外独立题/评价的4次已经计入，不再靠可选注释省去 Must。固定 HTML d/t 描述和继续理由的确切有限文字需在发出前零费用冻结，来源仅限原 L10/L05 合同和合格父内容，不能扩成任意正文白名单。

完整[剩余矩阵](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-122/preparation/remaining-must-matrix.json)含原 Q00—Q11、补入 Q12、89个逐请求动作及28个 Must 的证据层。当前真实完成0。正常有限最坏为41个普通模型、41个query、6个索引、1个HTML，共89次、22250000微单位。A1学习43/48、10750000/12000000，余5次/1250000；A2面试28/28、7000000/7000000，余0；A3补证18/24、4500000/6000000，余6次/1500000。全局余11次/2750000，不能跨活动借用。

面试最坏已无失败余量。它不保证模型成功；任一失败、未知、额外必要调用或缓存失效都保原预扣。若实际所需超出分额，原键留账并一次报精确缺口。不能删支持/反例/部分认可/不足/冲突/自报/复测来省调用，也不能新建 grant/活动/库补余额。不重新索取已批准的候选或100次25元。

## 4 获准后精确创建新 normal 与物理绑定

本卡没有创建资源。建议下一卡仅一个新 normal PG、一个原生 Windows API 和原固定三活动，两 provider 共用该 PG 金融账。候选名 retrolume-q-first-normal、数据库 retrolume_q_first_normal、卷 retrolume-q-first-normal-data；PG候选127.0.0.1:55482，API候选127.0.0.1:18122。端口、镜像缓存和资源现状均未探测，名称不是已存在身份。

PG候选沿当前 compose 的固定 pgvector 镜像摘要、CPU1、512MiB、pids128、restart=no、pull_policy=never。最终 image/CID/label/port/volume/账号角色由主控新卡明确；不靠换名绕失败或把旧 TESTONLY 解冻为正常根。data、backup、restore、control 根由部署者选独立绝对位置，ACL与真实 SID、设备/file-id 均在创建后记，不在草案造hash/CID/SID。

沿原正常限制在每次启动前核端口所有权和 bind、Docker唤醒后的实时可用内存及获准精确限额。原116一般2GiB门与后续120特定512/768许可不能混成新卡默认许可；本包推荐保留一般门，若主控另发特定资源门须明示依据。不得要求用户反复释放内存，也不启动无关缓存/看门/影子账。HTML 预览仍由已有 SUP 动态拥有，不能先开常驻 renderer。

创建和初始化只作用于新 normal。当前闭合源码支持 data_exit.v1.r03 与001—015链；核实际 schema_profiles.py 与采用源码摘要后执行新卡明确列出的初始化/角色动作。公开 deploy/initialize-materials.py 只处理001，start_local.py 没有 --initialize、--migrate、--profile，不能用它们当完整初始化命令。未来正式卡须列准确当前迁移文件和受信执行入口，不能运行旧 DocuN runner 或临时实验作为产品依赖。

先以关闭的外发配置启动正常数据层，登记 source 注册/normal schema/dataset/instance/originals_root/control_id、selection generation、cluster system identifier、database OID、connection_target摘要和 control volume/file-id。只导入八份精确材料，确认真实 source/version/revision 及24片规则；暂不索引、暂不创建不带 grant 的三个固定活动。普通 UI 随机 UUID 新建不能替代已批准固定 roster。

再冻结 InstanceBinding、模板/atoms与 derivation policy、真实 manifest、适用 price 和 readiness 证据。这里的物理绑定资料不等于 QAuthority.bind；后者需要主控真实首次回执和完整 grant，不能在回执之前伪造。source_index/query/模型的执行时间窗尚未起。

未来实际启动入口是 deploy/start_local.py 的 --container、--port 和 --shutdown-stdin；它会启动 PG/应用、连接数据库并可能装载 ControlHub，只有新卡资源许可后使用。正常私有配置由父进程安全环境继承到 API，不读取本聊天进程的presence来代替。

## 5 主控真实首次启用与无自引用摘要

先核本项目仍无真实 Q 使用的相反持久事实；若发现真实已用账，停止“首次”假定，保原账和根，不能再开第一份。当前输入一致声明 Q 未启用，T0=null，真实费用/调用0；本卡未扫描私有运行根。

摘要顺序如下。不同摘要域不能互换。

1. 真实资源身份稳定后计算 InstanceBinding 的 canonical JSON 摘要；模板集按 canonical({messages,atoms}) 摘要。derivation policy沿当前源码。
2. manifest包含 binding、模板、有限输入与真实source/fragment身份，计算 canonical 对象摘要。
3. price 形成不含其自身hash的固定原文件bytes，计算原字节SHA256。真实价格未知则不生成可用price。
4. 主控此时明确首次启用，记录真实 T0 与截至时间≤T0+72小时。activation body只引用前序 manifest/price/binding、采用回执、有效独审、readiness与矩阵，不引用尚未生成的 grant/root 自身摘要。保存原文件bytes及其SHA256。
5. grant引用 activation原字节摘要、price原字节摘要、manifest canonical摘要和binding canonical摘要，再计算grant canonical摘要。不能把grant摘要放回activation body形成循环。
6. root bundle固定 schema、execution_class=Q、grant、manifest、binding、templates、template_atoms、operator_principals；独立部署绑定记录并列所有摘要和真实授权合同ID。所有有效配置只在这一实际获准阶段写入私有位置。

上述T0不是本卡日期或草案签发时刻。QAuthority.bind 只在真正正常配置启动、完整门已满足后落原控制日志；同根已经有Q或selector/fence冲突就拒绝，不换根绕开。root中命名root_sha256实际指manifest规范摘要，不能误拿整bundle原字节hash替代。

用正常API装载并读取非敏感readiness，精确确认execution_class=Q、非TESTONLY、normal实例/价格/manifest/grant/严格身份/限额一致。失败立即停并保主控已开始的时间窗与原事实，不重新选择T0。启用回执不自动批准任何请求。

随后经正常 create_activity 入口为三个已批准固定 UUID 建活动，带 source_ids 和 expected_sources 精确版本，不选新 memory。activities/api.py:344—361从受信v2 grant按UUID索引覆盖48/28/24、12/7/6元及24h/3600秒/0.25元/4096输出/8工具限额，不需要逐活动改配置或反复重启；客户端不得自填额度。创建时冻结同一 grant 摘要。A2初始scope含八源，start(goal=null)建立interview.v2 head后做索引；A1/A3保留各自后续范围。

## 6 有限真实 Must 与逐请求保存

按矩阵 actions_in_recommended_order。每次先GET当前head/scope/父记录，再保存完整业务键和规范正文；prepared绑定typed request、实际payload对象、canonical UTF-8 bytes、endpoint/model、service/templates、provenance、memory/instance。未准备不猜模型接口，不从模型文字派生任意外发权限。

源索引为同一业务键6个批次，每批完整请求都需本机批准，全部合格后才沿原索引键显式继续。不得把第1批批准当后5批批准。批序号和operation由真实按evidence_id排序的manifest确定。

在正常 backend Python 环境使用现有 app.operator.q_request。以下是后续有条件语法说明，当前没有运行；路径、ID和摘要必须取真实冻结对象，不能复制草案null或占位值执行。

```text
<正常后端Python> -m app.operator.q_request inspect --config <私有绝对配置> --prepared-id <真实prepared_id>
<正常后端Python> -m app.operator.q_request approve --config <同一私有配置> --prepared-id <同一prepared_id> --expected-prepared-sha256 <inspect真实摘要>
<正常后端Python> -m app.operator.q_request revoke --config <同一私有配置> --prepared-id <同一prepared_id>
```

inspect会检查当前资格并读取PG及本机允许的完整请求正文，不是本卡可运行的纯元数据命令。只在受信本机终端查看，核正文/来源/父记录/endpoint/模型/字节。approve要求交互输入精确 APPROVE 加该SHA256，principal_id对应真实Windows SID及root allowlist。批准有效期取15分钟、活动deadline和grant终点最短，联合时钟与失效规则按已验实现，不补旧批准有效期。

批准后回原页面GET核状态，再由用户显式继续原键原体。query received、合格512维向量、原retrieval_ref及currentness真实COMMIT后，模型动作另准备、另批准、另显式继续。常用入口为 retrieval/commands、teaching/commands、interview/commands 和 html/commands，均在 /api/activities/{activity_id}/ 下；读取用相应GET原业务键。模型操作另可GET /api/activities/{activity_id}/operations/{operation_id}。

查询正文用当前已保存有限goal。教学前端当前取 workspace.goal.goal，面试取 target 与可选focus拼接；本包将面试focus固定null，因此query恰为冻结interview_goal。程序目标取原P完整正文，不新编program_goal。derived模型字符串只用于同活动、同grant、当前合格已COMMIT父的有限领域输出；query仍是adopted-fixed-input-only。

初始120米/2分钟题上先依次评价L02三正例、L03三反例、L04否定/不确定的独立answer版本，随后保存L01冻结长错答作为当前修订。由它的当前feedback立即做Q10，再针对题、复测、额外独立题；避免换题或换scope后引用旧feedback。每个新answer版本须指真实当前exercise及答案链末端；每次评价前重新冻结query/head，不拿相同query文字当跨命令缓存。

模型生成题必须满足原有限题目rubric；不合即保留失败，不偷偷改固定答案或免费抽题。L01错误应认可正确算术并指出单位，L02—04不得靠含数字评分，L06部分认可与推理缺口分开，L07不执行程序，L08先澄清再改范围，L09不足与冲突保留。L05仅两份不同未暴露合格实例可推进；针对练习若已看参考按assisted，重复键不加次数。继续理由明确保存后才下一动作。

面试A2按R-only和R+M两轮。同轮每个supported/self-report/invented/incomplete均独立保存版本与review。R-only对“参与”认可、测量缺据、自报未独立证分开；该轮结束只保存结果，不finish。经同A2的bind_scope与goal修订建立R+M新轮，最后才finish，避免ended后再提交。R+M认可20%耗时下降但不推利润/吞吐。I01首个必要probe必须真实产生并消耗两次上限之一；可选晚probe只在真有且不超上限时评价，输入仍限原冻结回答。无probe不凑次数，缺必要probe则Must失败。范围外M与位置合法但不支持利润分别核对，不假“可引用即可信”。finish为本地保存。

HTML在当前合格长错答feedback后生成一次，不额外query；description批准不授host权限。原host_policy与独审/镜像材料另核后才真实预览，保存parent/description/artifact/hash、d120/t120读1、t240读0.5、t0/未定义字段拒绝、reset回1的ACK/PNG或可信读值和StopProof。最多3次/180秒、每次30至60秒，失败不回退账。

X01—X12、P01—P03沿其已验零外发/PG/Windows/正式UI/退出层继承，不用真实provider做安全故障注入。新normal实际身份/readiness及运行停止仍需当次证据。正常重开可插在已保存回答、模型未claim处，先停止确认，再同库/同卷/同根GET；已有query COMMIT可沿原键恢复，不新发以补重开。与新normal有关的未知不抹掉旧已验范围。

## 7 失败、COMMIT丢确认与停止

收到HTTP错误或丢响应，先GET原命令、operation、007与领域head。已COMMIT就保原记录继续下一明确动作；accepted且确未claim、当前资格一致才可精确重审/续批并显式继续原键。claimed、可能已发或UNKNOWN只读对账，不能重新approve后重发，也不能换key。

schema、返回身份、非有限向量、超响应字节或语义不合格均保收到事实与原预扣，不授后继。准入后not_sent、取消、超时、UNKNOWN保250000预留及次数；确未准入的拒绝不伪造收费。只有本账号可核最终计价能补实际费用，unknown不填零。余量不足完整query+model时整步拒绝，不能先query再越额chat。

停止先拒新mutations，等待/取消本launch窗口并取得PID+birth、Job/句柄、worker退出、运行时结算、preview准确CID/nonce/双Job/EOF与端口停止证。缺物理停止证就记unknown并封闭后继，不把“stop已接收”当结束；已在远端的字节不能声称收回。

API沿当前owned stdin正常关停或精确PID/birth流程，只停止本launch启动的PG与预览。记录启动前已运行对象，不能擅停用户资源。保留卷、库、失败/UNKNOWN、原grant/roster及全部四账；不删除以清额度。新卡的wall/持有/日历到门就收尾，72h或活动24h/3600秒也不因停机重开延长。

## 8 集中语义与安全验收

逐Must保存真实输入映射、层、UTC/mono、before/after head/scope/DataContext、键/哈希/claim、operation/007/向量/领域COMMIT、引用和四账、原资源与停止证明。原件版本/位置正确与语义支持分开判断；模型自评、JSON合法、Mock、TESTONLY不证明真实Q语义，更不证明长期掌握。

主控按28项矩阵一次集中核语义、安全继承、新normal事实与新增差异必要独审。任何Must不合保失败及精确后续缺口，只补受影响范围，不重跑TASK120关闭的权限/清理/时钟/领取修复。Q/STEP018/019/020/M-1/项目最终裁定均由主控作出，本操作包不签通过。

所有缺口与唯一最小待采用差异集中于[交回清单](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-122/preparation/decisions-and-blockers.json)。本包不是要求逐条弹问用户，也不要求再批准同一候选或预算。
