# TASK-122 / R-116 统一结果

A—D前置核查与操作包已完成并可供主控核证；当前计量、账号适用性和正常部署事实仍未核齐，Q继续冻结。

本卡为STEP018开发阶段07的A+前置执行者交付，不是独立审计、工程复跑或真实Q试跑。客户端为Codex desktop，系统给出的Agent家族为GPT-6，精确后台模型ID unknown。需求v1.4、架构v1.60、唯一执行动态v2.88，task_model、V4.0/公共AGENTS CHG-0003。主控最终验收与DocuS维护权未代行。

## A 当前官方事实与计量费用门

公开资料取证于2026-10-21 22:44—22:59，Asia/Shanghai。使用9个主题、6条定向查询、11个直接官方文档身份；实际22次open/click与9次find逐项保存，4次find无匹配，没有HTTP抓取失败。重定向尾斜杠按同一正文身份记录，搜索返回的其它版本/语言未另开正文，也不拿摘要充当本账号事实。见[官方事实与短摘录](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-122/preparation/official-facts.json)及[完整请求元数据](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-122/preparation/web-request-ledger.json)。

当前公开候选仍为deepseek-flash，对应Flash-1017。最新已见发布事件为2026-10-17，与原119的10-18核查相比未发现需改候选或价格的后续事件。[官方更新日志](https://api-docs.deepseek.com/updates/)与[人民币价目](https://api-docs.deepseek.com/zh-cn/quick_start/pricing/)支持这个公开层结论。旧deepseek-chat/reasoner的2026-07-24退役不追认成今天新发生的事件，也不恢复调用。

[DeepSeek接口正文](https://api-docs.deepseek.com/api/create-chat-completion/)支持现配置ID与显式thinking disabled；公开响应示例仅提供候选返回字符串，不是实际返回。每次现有网关仍须严格校验returned_models，未知/不符保留收到事实与预扣，不授父资格。当前公开上下文1M、最大输出393216 tokens，不扩大产品256/2048/4096、10秒及65536字节限制。

[Embedding-3官方页](https://docs.bigmodel.cn/cn/guide/models/embedding/embedding-3)支持既有端点、配置名、512维与0.5元/百万tokens；保留单项及保守整批均≤3072 tokens、本地批4。其8K窗口或最大64项不能替代这些门。实际响应model和本账号价费均未调用核验。

公开报价按最高时段/缓存未命中取输入2元、输出8元/百万tokens，缓存命中最高0.04元只登记不用于压低准入。新核到Search/Fetch在2026-11-01 00:00北京时间另按次收费；它不在本包的固定chat/embedding请求范围，本卡未证明该公告是10-18之后发布。[人民币价目](https://api-docs.deepseek.com/zh-cn/quick_start/pricing/)只证明公开报价，不证明本账号含税、主体或额外收费。

数据条款按[DeepSeek开放平台协议](https://cdn.deepseek.com/policies/zh-CN/deepseek-open-platform-terms-of-service.html)、[DeepSeek隐私政策](https://cdn.deepseek.com/policies/zh-CN/deepseek-privacy-policy.html)、[智谱服务协议](https://docs.bigmodel.cn/cn/terms/service-agreement)和[智谱隐私政策](https://docs.bigmodel.cn/cn/terms/privacy-policy)分别登记。DeepSeek协议更新04-22/生效04-29、隐私02-10；智谱隐私生效2025-05-20，服务协议整体日期未明示。它们不能证明本API账号默认不训练、零保留或确切留存天数。原119对智谱匿名训练的描述本次未核齐，不直接当今天已证事实。主体、输入/输出许可、必要保留及取证局限均在official-facts逐源记录，不要求提供私人账单。

计量硬缺口仍存在。[官方token说明](https://api-docs.deepseek.com/zh-cn/quick_start/token_usage/)给的是近似字符比例及tokenizer链接，没有为当前服务证明完整token≤线上JSON bytes+framing，也没有证明framing≤4096。针对当前官方源的第二种查法仍缺证后已停止该题；没有下载或运行tokenizer。disabled切换行为已证，额外reasoning/隐藏收费的严格上界仍UNKNOWN。

现代码的request_bytes是canonical完整线上JSON的UTF-8字节数W，包含字段、转义和协议数据，既不是原文UTF-8字节U，也不是供方tokens T。若要证明T≤W+F，至少需证明当前分词/归一化不会扩张到超过已界定U、每token消耗的字节下界，以及当前消息模板/特殊tokens等额外项F。只有已绑定当前模型/模板的无扩张、非空字节分割等官方前提成立，才能由T文本≤U、U≤W、T总≤T文本+F完成推导；本次没有这些前提，所以不能引用这一条件推导签verified。4096只是在grant中可表达的设计上限，不是已核模板常数。

Embedding的2048 codepoints单项最多可有8192 UTF-8字节，query的1024字符/4096字节也不能自行证明≤3072 tokens。源码没有独立的逐项/整批token准入断言；现成本门成功也不证明容量合格。固定片段虽短，仍缺当前官方分词/请求计量边界。确切缺证、代码影响及最小后续核证均列入同一个待决包，不持续换说法扩搜。

以Decimal和整数向上取整复现现门，条件公式为ceil(((W+F)×输入价+输出tokens×输出价)×1.25)，单位为microunits，1元=1000000。仅在W≤65536、F=4096已证、最高含税2/8适用且无未知额外收费时，embedding共同最高价174080、learning256为176640、teaching/interview2048为194560、HTML4096为215040，形式上均≤250000。Embedding自身0.5价的对应上界43520，草案32768字节时23040；正式共同门仍不因此另开余额。只用官方1M上下文而不证字节关系，输入一项已达2621440，不能满足单笔预留。

这些数值是条件算术，不是可用最高适用报价；actual_applicable_per_request_ceiling=null。所有币种/税/额外收费和计量缺口保持关闭，不能填零或加margin制造通过。逐类、逐行与分额比较见[费用核算](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-122/preparation/cost-calculation.json)。

## B 正常配置与readiness分层

已沿实际源码核model、integration、operator字段与main装载链、固定root/instance绑定、严格返回allowlist和本机principal入口，没有执行loader、configure_application、operator_ledger、QAuthority.bind或ControlHub。完整字段、真实GET入口、预期和失败行为见[readiness清单](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-122/preparation/readiness-plan.json)。

本聊天继承子进程只对15个项目已声明必要环境变量做名称存在性检查，全部absent；没有读取值、值hash、全Env、密码库、.runtime、私人配置、cookies或账号后台。该结果只适用于本次元数据进程，正常API进程是否注入仍UNKNOWN，见[presence记录](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-122/preparation/environment-presence.json)。

未来正常服务器通过RETROLUME_ACTIVITY_CONFIG、RETROLUME_INTEGRATION_CONFIG、RETROLUME_Q_APPROVAL_CONFIG装载私有绝对配置；两个key只经正常进程安全环境注入。main把embedding的同一受信grant/manifest装入chat，无grant时关闭模型层。enabled=false示例不证明实际部署。operator读取同一控制根、正常PG与真实SID，完整正文仅在受信本机inspect，不进入公开日志或聊天。

正常只读入口GET /api/activities/capabilities已有storage、provider、quota、retrieval、q_approval，但会探PG，且不能充分证明服务器key presence、返回allowlist/服务限额与全部绑定指纹。最小后续差异是沿此现有入口给已载入状态的非敏感投影。缺项要明确false/reason，不能伪称本卡已经检查。真实activation receipt.TASK目前只接受117/120，下一回执若填新ID会失败；先由主控明确真实实现谱系与新的执行授权，能如实复用现谱系就复用，只有实际不兼容才定向适配，不预设必改loader，不冒写旧卡或重用旧票据。

公开启动器只有实际存在的--container/--port/--shutdown-stdin，没有旧设计提议的--profile/--initialize/--migrate；initialize-materials.py也只应用001。后续卡需把新normal当前R03/001—015链、角色与初始化入口列清，不使用旧runner或假命令。以上均为静态部署准备发现，不是重开旧120权限/清理/时钟/领取修复。

本人需做的仅是一次账号非敏感事实确认及获准正常进程的安全注入；其余配置/绑定/审核/资源动作归主控与后续执行者。保存位置和最少步骤已在runbook与账号草案集中给出，无逐项弹问、无索key。

## C 有效100/25下的剩余Must

原119动作复制为新产物，没有修改旧call-matrix或原116合同。24份锁定输入和关闭回执随7条规则身份一起共32项核对零漂移；读取的具体span/实际文件hash另记，不把哈希读取当通读全部历史。八份材料精确来自原sample-inputs的JSON正文，未读取本人资料或用户库。

最关键修正是当前build_fragments按行保留换行再切2048 codepoints，八份资料静态推得24片，空缓存要6次索引，旧81次/20.25元中的2索引不能直接继承。片数为4/4/5/1/1/2/3/4，每片最长100 UTF-8字节、任意4片canonical线上payload上界446字节；未来真实ID/排序/批次未造。此为固定正文加已读规则的标准库算术，没有产品分片实验、PG或向量服务。

将L05独立题和评价的4次纳入后，完整有限最坏为89次、22.25元预留，含41普通模型、41query、6索引和1HTML。有效分额原样保留。

- 学习01800000-0000-4000-8000-000000000001，计划43/48次、10.75/12元，余5次/1.25元。
- 面试01800000-0000-4000-8000-000000000002，计划28/28次、7/7元，余0。
- 补证01800000-0000-4000-8000-000000000003，计划18/24次、4.5/6元，余6次/1.5元。
- 全局89/100次、22.25/25元，余11次/2.75元，不能挪分额；条件共同价tokens算术总额16.373760元不替代22.25元逐笔预留。

面试正常最坏没有失败余量，不承诺必成功；任何额外必要请求都须停止并精确报缺口，不新grant/库/roster补账。原100/25只用一次，不与旧80/20、13元或TESTONLY叠加。当前真实完成0，因此当前未使用余额仍是各完整分额，表述的余量是正常路径之后的预测。

[机器矩阵](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-122/preparation/remaining-must-matrix.json)保存13组动作、89个逐请求动作、28个Must的来源/父COMMIT/本机精确批准/输出和语义判定/原键恢复与停止要求。动作顺序让初始题的多答案正反例先完成，再以长错答成为当前版本走L01后续与HTML，防止在换题后用旧feedback。面试两轮同A2通过scope/goal修订，末轮才finish；不是新建面试活动借额度。

缓存仅接受same source/version/revision/space/recipe/currentness和vector/PG摘要真实可核的源向量，A1/A3只复用A2对同八源的已提交向量。首次无normal缓存证据，按全miss。query只限原键完整绑定不变的GET复用；同文字/新head/新活动均重新计。typed/payload未实生的身份为null，不能把草案装成授权。

L01—L10与I01—I03的真实支持/反例/部分认可/不足/冲突/自报/复测均保留。X01—X12、P01—P03分到原已验零外发/PG/Windows/UI/恢复层，按主控121 closure范围继承；新normal的实际readiness/身份仍待核，不把未覆盖安全故障丢给真实收费试错。所有Must都未被本卡自签真实语义通过。

## D 一次后续操作包与唯一待决清单

[操作runbook](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-122/preparation/operation-runbook.md)按前置事实→正常配置/readiness准备→主控核计价计量/独审/精确样本→新normal资源与物理身份→主控首次回执/完整绑定→有限真实Must→停止留账→集中验收排序。实际normal运行readiness只能在获准创建后取得，不能把此前静态准备填成运行通过。

包内已明确无自引用顺序，binding/模板/manifest先定、price原字节先定、activation body不含grant/root自身摘要、grant引用activation/price原字节与manifest/binding规范摘要，最后单独并列部署摘要。operator的DecisionBody在锁内固定event_seq/clock后才得approval_id。T0和终点均null，72h只从未来真实首次启用开始。

资源仅建议一个新normal PG/Windows API及原固定三活动，两个provider共用一份PG账。候选名/loopback端口/512MiB等在草案内均标未创建/未探测；最终CID/PG OID/cluster/SID/根file-id只在获准真实创建后冻结。不恢复旧TESTONLY，不继承120旧96h或已尽根数，不堆看门/影子账。每活动24h/3600秒、finite_calculate≤8、预览3次/180秒与原窗口限制照留。

逐请求inspect→精确APPROVE→GET→用户显式原键继续，以及COMMIT丢确认、accepted未claim、claimed/UNKNOWN、非法received、进程/预览/费用停止证明都有真实源码入口。失败保原键与预扣，不自动重试、不退款、不重开余额。原完整层验收和新增差异必要独审由主控集中核。

唯一[集中交回包](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-122/preparation/decisions-and-blockers.json)按影响排序为计量/账号硬门、24片6批和有限文字的精确冻结、非敏感readiness与新receipt谱系小差异、后续精确资源/运行/首次启用许可。只阻Q启用，不阻本卡其余文档收口。没有要求用户再次批准相同模型、预算或Q v2设计；没有让用户逐项手动解决Agent能完成的准备。

所有草案均disabled或外层非产品schema，数值未知用null，实际grant/manifest/binding/approval/activation不存在。根README仅更新当前有限关闭、正常operator步骤与仍关闭限制；原字节/摘要/差异已保存为[README变更记录](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-122/preparation/README-change.json)和[README差异](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-122/preparation/README.diff)。

## 操作、投入、限制与交回

首次可靠采钟为2026-10-21T14:41:11Z，准确人工接收时刻unknown，依卡以签发2026-10-21T22:37:01.283336+08保守起算，24h截止2026-10-22T22:37:01.283336+08。首读/采钟发生在落盘登记前，bootstrap如实计账；本卡新尝试1，历史投入/失败不清零。工具wall上限2400秒、单批≤60秒，无持有型产品资源。实际累计与未知预留以[执行工具账](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-122/preparation/command-ledger.json)及[交付记录](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-122/preparation/delivery.json)为准，human/model tokens unknown。

本卡只有标准库文本/hash/JSON/整数与Decimal、限定变量名称存在性、官方公开网页取证。产品import/tests/compile/build、PG/SQL、Docker/卷/容器、服务/API/browser/业务Job、provider/真实费用、Git写、依赖安装均0，没有待清理的本卡产品进程或资源；不声称现场核了旧资源停止。历史工程149失败、旧117的81失败、wall69357.418110和holding2943.704295、审计保守2113.8359792均按handoff原样引用，不与本卡抹平。

实际资料操作中有文本输出截断、一个settings路径rg失败和一个不存在activities/contracts.py的读取失败；后者按真实schema在activities/api.py定位并继续。部分rg批命令对候选不存在路径隐藏了stderr且末命令覆盖退出码，相关子退出明确unknown，不能把整批exit0当每项成功。真实命令/整批退出与最少已知失败分别保留在工具账。未因这些读取问题运行产品或重开旧runner。

最后仅做一次文档一致性核对，范围是输入/规则身份、日期与历史继承、预算与28 Must/父依赖/价格条件、集中缺口与操作顺序、可读路径、草案保持关闭及写入范围。结果见[文档一致性](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-122/preparation/document-consistency.json)，它不是产品测试、行为验证或独立审计。

待主控同步的事实是本卡真实接收/返回及A—D准备交付、24片6批与89次矩阵、readiness/receipt小缺口和继续冻结门；DocuS架构/唯一状态/CHG与最终采用均未写。没有改原始需求、公共库、任务卡、历史证据、产品源码或私有运行配置，无合格经验入库动作。原S有限关闭和历史控制不通过保留；Q、STEP018整体、019、020、M-1、项目与发布均未由本卡签通过。
