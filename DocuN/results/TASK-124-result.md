# TASK-124 结果

本轮 R-118，父 TASK-123 / R-117，关联 STEP018、TASK116 固定 Must、119 有效采用、120 有限工程、121 旧独审和122准备。适用需求 v1.4、架构 v1.62、执行动态 v2.90及 NFR002/003/005、SEC001/002/003、DR002。审计日期为2026-10-22，时区 Asia/Shanghai。

## 结论与交付边界

集中独立增量复核已完成。有限前置工程结论为不通过，当前不具备整体交主控关闭的条件。确定阻断为 F124-01，P1。新增交付把中性的继续理由映射为 correct；现有实现会把该记录当成对父反馈的争议，即使 disputed_dimensions 为空，也会从进度依据中排除该反馈对应的作答。这违反 L01/L05 保存继续理由、保留真实进度依据的原目标。

- 代码轴通过。本次只读 readiness 产品增量未发现确定的新增授权、秘密属性直出或启动回归；适用范围和配置字符串的风险限界见 A、B，不是对任意人为填入的配置内容作保密承诺。
- 证据轴分开判断。最终13方法的运行事实、输入字节、原始日志和覆盖解释通过；完整交付的适用性不通过，有限输入及交接的 correct 映射存在 F124-01。13方法没有覆盖此映射，不能替它背书。
- 执行控制轴在原许可与现存记录可核证的范围通过。完整工具实测仍 unknown，采用原账保守包络，不追认历史控制通过，不把预留记成实耗。
- Q 启用资格未具备，继续冻结。外部分词、模板、Embedding 容量和账号缺口独立保留，不用这些外部未知解释或掩盖本次确定缺陷。

可单独采纳已完成的只读投影、有效离线证据、HTML focus 冻结和有限计量结论；不能据此签 STEP018/019/020、M1、项目或发布通过。最终验收和共享状态仍归主控。本次未改产品、测试、原123交付或 DocuS。

## 身份、独立性与对象

接收客户端为 Codex desktop，系统身份说明为基于 GPT-6 的 Codex；无法从当前接口核验具体部署模型标识，记 unknown。A+只是本卡资源标签。本会话按合同允许的新隔离审计窗口接收，不声称为原TASK121窗口；没有参与TASK123实现、测试、资料取得，没有其实施推理聊天。不委派子Agent。

暴露情况如实登记。用户本次提供“工程候选及13项证据已核对、计量外部依据仍缺”的摘要；只作为接收背景，不当作通过证据。读取了记忆中通用的 RetroLume 规划核验偏好，没有TASK123实施内容。未打开TASK123统一结果、实施聊天、自评或主控候选裁定正文。输入和交付清单中出现其结果路径及hash是元数据，不等于读取结果正文。build_delivery.py只核身份，未读其实现自评。

依据为根入口、同版公共 AGENTS CHG-0003、WORK适用段、07、本卡和原TASK123合同。七项锁定规则hash与快照一致；没有加载后来规则。审计接收和未知时间记录见 [reception-and-independence.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-124/audit/reception-and-independence.json)。

本次独立核对79项输入，全部与TASK124清单的字节数和SHA256匹配，排除了TASK123统一结果文件读取。六个冻结文件为 main.py、activities/api.py、q_readiness.py、test_q_readiness.py、README.md、deploy/q-approval.md；四份pre原字节均匹配，两个新增文件的pre不存在状态一致。完整当前hash、pre核对及区分全文/片段/仅身份的读取范围见 [input-verification.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-124/audit/input-verification.json) 和 [read-scope.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-124/audit/read-scope.json)。

从pre副本重新生成了 [独立差异](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-124/audit/independent-product.diff)。按原差异采用的行尾及末尾换行规范化后，与product.diff完全一致。pre README没有末尾换行，最初按原始行尾直接拼接的差异文本因此不同，已经定位；这不是文件漂移。原字节区别由pre/post hash保留，不用规范化差异冒充原字节。

## A 只读投影与资格语义

[main.py](D:/shspic/project_NO3_RetroLume-agent/backend/app/main.py:93) 只在原装载后保留候选对象及embedding key存在布尔，在既有grant附着、DataRuntime、Q配置成功或失败关闭之后构造最终快照。没有改变这些原步骤的次序，也没有增加configure_application调用。

[q_readiness.py](D:/shspic/project_NO3_RetroLume-agent/backend/app/q_readiness.py:133) 不读文件、环境或PG，不构造ControlHub、QAuthority或批准。IntegrationConfig.available只按已装载service、reason、grant和transport类别判断；它不是新增存储探针。GET在原session校验后调用read_readiness深复制快照，缺快照的旧夹具返回未知。原storage/memory探测、同源校验、DataContext和R01/R02写门没有改动。快照明确标为 startup_loaded_snapshot，重启后才能取得新装载事实。

candidate是装载器当次返回的层状态，不能视为可发调用。effective是原启动处理之后的对象，也不取代每笔授权、PG准入或活动已冻结额度。缺模型配置、坏JSON、缺service、密钥缺失及集成关闭分别沿装载器的失败对象投影；模型key只有成功装载service才为true，明确缺key为false，其余无法保留事实的失败为null。embedding key存在与集成是否enabled分别表示，不混为同一门。

原q_approval原样保留，新副本只投影其布尔与Q/TESTONLY类别。存在已装载grant但Q配置disabled的状态不能靠effective层的available推导Q已启用；这里报告的是原对象状态。authorizes_requests恒false，qualification恒unknown，账号、计量、正常部署及真实返回均null。grant/manifest只作形状及对象一致性检查，价格、激活与实例只保留引用摘要和未核字段，不把它们当本人账号或当前部署证明。没有发现新增误授调用权。

## B 信息边界与启动风险

新字段未访问api_key或其摘要、base_url、DSN、配置路径、完整正文、用户名或任意异常原文。reason使用有限集合，未知原因转稳定码；quota和limit来自正常装载器已约束的数值。正常成功/失败返回对象具备投影所需属性，数值及别名元素类型由装载校验保证；未发现本次新增投影使这些既有正常启动状态抛异常的确定路径。grant解析异常只产生loaded_evidence_invalid，不回传原始错误。

OBS124-01为配置内容的条件风险，不报为已经发生的秘密泄露。provider有枚举约束，embedding的model和正常returned_models限制为embedding-3；聊天model字符串此前已在provider字段公开。新增聊天returned_models仅受list[str]、数量及投影正则约束，并未限定为官方公共别名。字母数字、点、横线和下划线的128字符正则不能识别秘密，也能接受64位hash。因此如果部署者把密钥、密钥hash或敏感标签主动填入该身份栏，它会被新字段反射。不能声称任意配置内容均已脱敏。本次没有读取私配或真实key，也没有发现credential属性自动流入别名的路径；不将既有model公开风险冒充本次新增确定泄露。交接应明确只在这些栏位填写可公开的模型身份，未知别名不得当真实返回资格；若以后要求对任意配置误填也强制保密，应在公开投影边界定向收紧，不能仅增加字符正则。

## C 三批与最终13方法

[evidence-binding.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-124/audit/evidence-binding.json) 独立计算三批各六个测试输入的当前hash，并核对completion引用的stdout/stderr字节与hash，全部匹配。六个输入是三个产品Python文件、新readiness测试和两份既有配置/API测试。未以作者final-consistency中的true代替计算。

- 第一批父计时120.031秒，completion的124来自runner捕获TimeoutExpired后的映射，不是子进程原生退出码。原stderr停在第一个auth/context方法，stdout为空，没有完成summary，不能算任何13方法通过。
- 第二批选定同一首挂点诊断，20.453秒、退出1。faulthandler的20秒回溯定位到TestClient门户创建Selector循环时的socketpair/accept；不是业务断言失败，也不是完整测试集结果。原件保留，不重跑该失败。
- 第三批按合同及工具账记录的正常平台审批执行，父计时1.828秒、退出0。原stderr列13个方法均ok，unittest计时0.445秒；summary的含导入/安装tripwire计时约1.296秒，failure/error/skip均0。三种时长不相加。原警告不是失败，不借本卡升级依赖。

新增七方法实际覆盖缺/坏/关闭配置、任一key缺失及双key无grant、候选/有效限额及允许集合、重复读取不热加载或新增探针、session/同源/DataContext拒绝、合成Q/TESTONLY和坏grant不能核证资格、空允许集合/未知原因/部分敏感内容拒显。既有六方法为四个配置方法和两个API认证/同源方法，没有运行它们所在文件的其余方法或真实PG测试。

[run_offline_tests.py](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/run_offline_tests.py:16) 使用独立进程和仅SYSTEMROOT/WINDIR/TEMP/TMP的环境；合成凭据由夹具显式注入，没有继承用户provider key、DSN或私配。外层tripwire先于测试suite装载，但解析patch目标本身会先导入部分模块；不声称安装之前所有导入都受其覆盖。新夹具内层又替换部分外层mock，外层0不能单独证明这些路径；内层在create_app和完整GET之后另断言装载器各1、构造/授权/PG等替身0，重复GET保留原合成storage与memory probe各2次。

因此采纳的是实际create_app及完整GET在受控合成环境中的证据、纯投影反例和所选既有方法。没有验证真实PG、正常profile、完整Q配置、真实服务/账号，也没有证明“任何系统调用都为0”。本次未重跑13方法、旧Q矩阵或122分片。13方法不覆盖下面的继续理由保存及进度重建，不能用于关闭F124-01。

## D 计量分级与外部停止

M01可采纳。当前聊天及embedding纯文本payload的完整JSON序列化没有解压、base64解码或文本缩减，文本UTF8字节和U不大于线上JSON字节W。这个关系没有约束供应商预处理、分词或角色模板，不能扩成T≤W+F，更不能据此证明F≤4096。

M02的有限文档推论可采纳，不升级为实测。存档W123-04的thinking开关，W123-05内API源行276—281的生成上限、681—718的completion计数和reasoning明细，结合W123-06源行25及76的计费定义，足以支持该公开契约范围内max_tokens覆盖包含reasoning明细的生成总量。它是有原文支持的推论，不能声称disabled实测reasoning为0、本人账号无特约，或全部费用门已关闭。原文件已明写这些限制，本次不要求重新浏览。

M03/M04/M06维持缺外部依据。当前tokenizer、normalize/pretokenize、完整服务模板、完整commit与服务字节绑定、许可证原件以及Embedding-3单项/保守整批≤3072均未闭合。下载失败只说明未取得原件，不说明资料不存在；公开同名模型、版本前缀或MIT检索标签不是原件/许可证核证。没有tokenizer运行或有限token计数，24片/6批及字节算术只继承原用途。短文本、4项、2048字符、4096查询字节、费用余量和其它模型的tokenizer均未被用来填补这些门。

token_upper_bound_verified保持false，账号权限/币种/税费/特约和智谱相关事实为null；用户余额声明没有冒成账号核验。Grant、费用、容量、wire和gateway没有改动。两段未发送的供应商问题分别询问服务版本/分词/模板和prompt计量关系、Embedding逐项与整批容量及计费关系，不索key或无关账号资料；问题足以定位缺口。此卡不恢复浏览、下载或联系供应商。

## E 有限文字、部署交接与F124-01

HTML文本为171 codepoints、405 UTF8字节，SHA256为c4c8ff9522d7e5522858d764133050bf012826a48877151c8f016c7128e4e6fb；理由文本为53 codepoints、159字节，SHA256为9563a959fa373da25d4b347c84d2b1f5aa198cfe026d9945e750715ba9b5bf2a，均独立重算一致。原116 sample-inputs和122矩阵身份未变，没有重新分片或加总89动作。

HTML焦点与原L10相符。米/秒、d/t、120/120读1、t240读0.5、t0及未定义字段计算前拒绝、reset回1，都来自原rubric；原来源只提供这次单位换算，不扩张长期掌握目标。它是待发focus，未冒充description、控件或artifact。122顺序中的Q01.03.model、Q10.html、Q01.04.query依次相邻，当前长错答和合格feedback要求相符；真实父ID/hash/point/config、业务键、描述及产物都仍null，禁止回用历史父。

理由原文“继续核对分钟换秒与平均速度的单位，下一步仅按当前已保存的作答、反馈和复测记录选择；本次练习不说明长期掌握。”本身符合L01/L05的有限目标，没有预写成功。问题发生在交付指定的动作映射。

### F124-01，P1，继续理由被错误当成反馈争议

新增位置为 [finite-inputs.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/finite-inputs.json:84) 的action=correct、target为当前feedback/progress、disputed_dimensions=[]，以及 [deployment-handoff.md](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/deployment-handoff.md:25) 对该映射的执行指引。finite-inputs第89行同时声称不改变进度判据。

可达触发为L05已有两个不同、未暴露且required met的独立实例，其中有retest，随后按交接把上述中性理由作为correct保存到其中当前合格feedback或其progress。CAS和同作答链核对成功也不能消除此问题。

实际数据流为 [teaching_repository.py](D:/shspic/project_NO3_RetroLume-agent/backend/app/activities/teaching_repository.py:830) 校验目标后，为当前feedback/progress构造kind=correction并调用进度重建；目标是progress时也会归到其feedback。 [teaching_progress.py](D:/shspic/project_NO3_RetroLume-agent/backend/app/learning/teaching_progress.py:21) 将所有correction的parent加入争议集合，第45—50行据此排除作答，完全不读取disputed_dimensions。只剩一个有效独立实例时，原evidence_sufficient会变成needs_repair；原实现还可能回到受影响节点并清空当前练习指针。目标是feedback或progress均不能充当中性理由存储。

这不是对未运行语义的猜测，而是被审新交接与现有确定分支的冲突，证据为B级源码与交付文本，未运行产品/PG复现。原correct真实纠错语义没有改，是本轮新增用途错误；不能靠空争议数组、真实CAS或改一段理由文字修正。

最小修正是沿原TASK123唯一修复路线撤销该错误映射、同步修正两份交付，并明确中性理由持久化仍缺真实无争议副作用的承载。select_node现有输入也不携理由文本，不能换一个现有动作名声称已有能力。主控再裁定最小必要承载或准确界定有限交付终点；本审计不扩权实现新接口，也不建议削弱现有correct的争议保护。原理由文字和HTML focus可直接保留。尚有此P1时不能以有条件通过整体关闭。

部署入口陈述通过。已对照start_local实际参数仅公开container、port、shutdown-stdin，隐藏serve-owned；initialize-materials只执行001迁移，不具备normal全链初始化。没有杜撰profile/initialize/migrate参数，没有生成enabled配置、normal资源、grant、密钥、T0或首次回执。receipt.TASK谱系限制保留，新normal缺口不要求本卡实现。

## F 控制账、历史与停止

原123许可允许上述最小产品/测试/说明增量、三批有依据的离线验证及有限官方资料取得。六文件差异在允许范围，两份既有测试身份未变。13方法最终通过没有抹除首批超时、第二批诊断、原下载失败或任何旧预算。

原预算方法已对照close_delivery源码和实际时间独立重算。permit签发至budget为2654.557411秒，加300秒短并行/未记录保守项及600秒收尾预留，得到3554.557411/7200。budget至实际seal为160.194959秒，少于600秒；permit至seal为2814.752370秒，封存于2026-10-22 01:06:06.203425，早于原24小时截止。3554.557411不是实测工具wall，600也不是已经发生的消耗，完整工具实测仍unknown。逐批父计时保留，不与tool轮询层重复相加。交付清单除独立性排除的统一结果外47行重算匹配；save-proof的布尔只作线索。

两个metadata请求分别约0.047秒、42.14秒并报URLError；acquire_vendor捕获错误后外层可退出0，不能视作下载成功。0已保存下载字节、无解包/安装/远程代码，与现存记录相符。网页账有6次工具返回、17个子请求、4条搜索；账列6个新增文档身份，即使把所有显式直连及复用URL也计入，共10个，未超过12。没有进一步供应商检索或以失败重置额度的记录。缺完整旧控制实测的部分照留unknown，不据目录可读恢复旧runner。

继承原121保守2113.8359792/3600、122保守1340.9775537、123保守3554.557411；原120控制不通过、149失败、原117的81失败及122至少两次metadata失败/未知子退出均不清零，不追认旧控制通过。不声称实查旧进程已停。

本卡仅执行文件读取、stdlib hash/JSON和有限差异计算及获准结果写出；没有compile、unittest、产品导入、TestClient、PG/SQL、Docker、应用/API、browser、Job、provider/embedding/计量接口、费用、Git、网络、下载、安装、私配/后台或委派。第一次动作确切时刻unknown，未补0；首次捕获时钟为2026-10-22 07:28:09，实际工具账、保守包络、收尾与截止核对见 [control-ledger.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-124/audit/control-ledger.json)。没有把本卡预算借给旧任务或反向改其控制结论。

## 交回事项

主控保存本次独审完成和有限工程不通过的分轴结论，保留可单独采纳的有效成果；沿原TASK123集中处理F124-01的两份交付及实际承载缺口。修正后只核对应映射、相关语义和实际影响；本报告不要求重跑已有13方法、旧Q矩阵或再开同样的供应商查核设计卡。

计量外部事实清单保持当前分词/预处理/模板与服务绑定、许可证原件、Embedding逐项及整批容量、非敏感账号适用事实，Q继续冻结。后续若需产品承载变更或正常部署，由主控给相应精确范围；此报告不创造执行权。DocuS状态及版本由主控按真实裁定串行同步，审计未改共享账。无新增已解决且实测验证的错误经验候选。

完整结果和审计证据已保存，最终封存复读记录见 [save-proof.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-124/audit/save-proof.json)。
