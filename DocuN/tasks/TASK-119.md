# TASK-119 / R-113 — Q多步请求批准与启用前置的完整实施合同

## 目标、交付与窗口

你担任A+增强设计执行者，沿用刚完成TASK117 S08的原工程窗口。有限S合成工程成果已经主控验收关闭，D01—D04关闭；当前不继续修S或重跑旧验证。你的一个完整成果是解决Q多步链的请求批准缺口，连同官方能力/价费/条款事实、调用矩阵及最小实施验证路线，一次交付可执行的唯一推荐合同。

本卡为只读设计与有限官方资料核查，不是代码实施、真实PG、真实模型试点或独立审计。仍由用户人工转卡，连续完成必要子项后统一回传；不另委派Agent，不占新的工程运行根。优先原117工程窗以复用实际上下文，仅确不可用时一个A+接续窗独占。记录真实客户端和可知模型，不以A+标签冒充身份。

结果正文完整A—D保存到 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-119-result.md。事实与必要机器清单只写 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-119/design/，不并行写第二份全局状态或重复合同。交付应让下一实施卡可直接按函数、对象、数据与观察结果执行，不能用“后续再定一个批准协议”代替当前目标。

## 项目、规则与有效授权

根 D:/shspic/project_NO3_RetroLume-agent，入口 D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。task_model/V4.0、公共AGENTS CHG-0003、阶段07；需求v1.3、架构v1.44、执行动态v2.71。公共只读根 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，适用公共DocuS/AGENTS.MD、WORK第2章task_model和本卡设计/证据/授权章节、task_model/TASK_TEMPLATE.md及prompts/07_开发执行循环.md。七项锁定身份见本项目DocuN/evidence/v4-migration-20260930/rules-snapshot.json，同窗未变正文复用，不自动采用后续公共版。

新TASK119/R113，父117/R111，关联116/R110 AP1/AP2与118/R112 review-01、STEP018/019、SEC001/002、NFR002/003/005、DR002。用户2026-10-14已明确一并批准AP1及附条件AP2；回执 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/orchestration-20261014/adoption-receipt.json。80次/20元许可不重复索取，当前仍未激活，旧13元耗尽不复活。新增真实模型、个人资料外发、用户库写入、服务更换和发布均不在本卡授权。

主控已接收118增量独审并关闭有限S功能/有效证据成果，不追认TASK117全过程执行合规；历史控制不通过留史，STEP018整体仍进行中，Q/STEP019/020/M-1/项目未通过。必要新的模型/权限/主要数据/公开接口改变须先有具体采用边界，本卡可以完成该可审方案，不提前实施。普通内部技术细节不自动升级为新的用户许可问题。

## 最小上下文与已知缺口

1. D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-118-result.md 本轮review-01第一、四、八节。当前65525字节，SHA256 8f4569489faef05fe212e943f6c33a1e4a94bdcaae6da4fac3958f425e654af6，原41590字节首轮完整后缀保留。四项安全/客户端缺陷已关闭；第八节是本卡原始问题，不重审关闭项。
2. D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-116/design/ 下adoption-package.md、integration-contract.md、acceptance-contract.md、sample-inputs.json，及上述用户采用回执；原包hash 84cb852946220a09873225f8bde7b7138aa7366e137297638bb2aab01dbc1c84。只读适用条款，不推翻固定样本和Must，不把历史文件的“待批准”字面误判为用户后来未批准。
3. 实际当前backend/app/capabilities/embedding.py、gateway.py，activities/api.py与repository.py的创建/grant/准入/mark/record及retrieval/repository.py的_outbound_lock，retrieval/service.py及service_config.py的受信装载。按需读worker/one_call.py的私有wire、learning/teaching_service.py与interview/service.py的请求装配/记录/后继资格，原始命令与意图只读恢复接口。先按函数穿透，不通读全仓。
4. 若方案复用私有控制事实/原键恢复，按需读data_exit/control.py和operations的原契约，以及新normal控制根和旧frozen/readonly的分工；不要操作任何控制根。前端只需核可能的显式准备/待批准/按原键继续语义是否已有承载点，不实现页面。
5. D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-119/orchestration-20261018/ 的input-manifest.json、design-permit.json和scope-index.json给当前身份/许可；同窗S08已读未变源/证据直接复用。DocuN/results/TASK-117-work-decision.md、TASK-118-work-decision.md本次置顶只取采用/终点，不把主控评价当设计可行性证明。

现状是活动创建时绑定不可改的outbound_grant_sha256，grant又绑定source_manifest_sha256；S08的model_requests对完整typed request和payload双摘要作有限精确批准。非空批准集合变化会改变manifest/grant。下一请求中的真实模型输出、持久记录ID、父引用、派生上下文及新业务键事前不一定已知，因此不能仅靠将未知hash先填白名单完成多步Q。也不能改活动grant、开新roster、换库/供应商或重置计数借额度，不能自动将任意用户正文/记忆加白。

这不是恢复已关闭D02，也不是重新验收S。需要形成能支撑既定学习/面试多步语义且仍synthetic-only的具体批准机制。单个固定批准请求已证明能发送，不代表完整Q能执行；本卡不能拿静态结构/手工图替真实可执行边界作保证。

## A 当前事实、冲突与唯一推荐

A应明确当前原字段/调用/锁序/持久事实及两条具体链的阻断位置。至少穿透“当前合成goal和资料→第一次模型请求→received/COMMIT记录及服务生成ID→下一次query+model请求”，再穿透含selected memory/历史回答的面试链。列出消息中的固定合成输入、运行时标识、同许可下已确认模型产物、客户端自由正文、资料/记忆版本分别由谁证明。

在上述事实之上交付一个唯一最小推荐，不把技术选择甩给用户。确需比较仅限最多两种真正可行机制，用具体影响收敛；不要罗列平台或泛化Agent框架。方案必须说明如何在旧grant/roster不可重绑与共享预算不清零的前提下，批准事前未知但来自同一受限合成链的下一次完整请求。

不能笼统说“operator另行批准”“生成一个新grant”或“provider输出天然可信”。若采用逐请求批准/有限派生规则/私有回执等机制，给准确批准主体、实际入口、绑定字段、规范字节与摘要/签名对象、批准源、持久位置、权限、期限、读取者、失效和撤销边界。受信审批者只能批准原合成范围，不可把无关本人目标/回答/履历、旧学习记录或其它活动数据借同catalog送出。

## B 可直接实施的完整协议

B必须给函数级时序、状态转换、字段和失败返回。至少回答以下问题，必要子项合并进一个完整协议。

1. 稳定权限根究竟绑定什么，哪部分可随一笔新请求更新、哪部分永久不可变；新机制如何与现有source_manifest/model_requests精确路径及旧Embedding/v3/v4兼容。不能改旧grant活动绑定或对不同provider使用两份互不计账预算。
2. 下一请求如何在尚未付费/出站时构造、校验并取得批准；批准可验证对象必须等于最终将发送的完整请求，不能只检查catalog。若需人工/operator确认，明确正常本地工具/文件/私有IPC的具体入口、原键恢复方法及最低操作次数，不要求用户每次在聊天贴正文/摘要/密钥，不偷偷新增面向浏览器的任意签票接口。
3. 模型上轮产物何时可成为有限合成派生输入，必须有received+007+正文COMMIT、同grant/活动/原父链和当前资格等真实事实；UNKNOWN、晚到失效、其它活动/其它库/旧本人记录不能以“是模型产物”为由混入。固定合成goal/answer/memory等自由文字如何仍有限绑定；必要派生内容和可能含敏感字段的元数据逐项列明。
4. 目标/范围/记忆/head/DataContext在批准后、admit后、mark前后或原键重试时变化怎样拒绝，已预扣如何保守保持；不以重新批准绕过UNKNOWN或重复调用。并发同键/异文、两个批准冲突、COMMIT成功响应丢失、进程/服务重开均有明确持久事实与恢复路径。
5. 未批准时停在哪一个零付费状态，如何经现有原键GET/显式继续恢复；不得先把命令落成不可再继续的拒绝/unknown，再声称稍后审批可重跑。若要改变已有accepted/launch/record接口，给精确旧/新语义和直接调用影响，不靠新业务键抹掉上一尝试。
6. 全局唯一预算权威仍是同一获准normal库中原生产admission/PG SUM/锁/活动与操作预扣。批准文件/日志不能成为第二份可充值费用账，失败/超时/unknown都不退款，重开/新进程/新批准对象不回零。跨库复制真实grant和重绑活动如何失败关闭；权限根与正常运行实例的关系必须明确。
7. 持久改动清单及理由。优先使用现有资产，零DDL可行则不新增表；若确需列/表/profile/公开接口/私有wire或权限变更，给最小完整diff级定义、为何原基础不足、兼容/迁移/失败回滚和恢复导出影响，作为必要采用项，不自行写源码/SQL。不要为可选理论完美扩建常驻签名服务、消息队列或多层看门。

最多四条手工事件轨迹即可：正常两笔依赖调用；第一笔COMMIT丢回包后重开；审批/等待期间换scope或混入未批准回答；双provider near-limit并发。每条写原键/父链/批准身份/发送次数及预算不变量，不运行产品、不用手工推演冒动态通过。

## C 有限官方事实与调用/费用矩阵

本卡允许有限公开互联网只读核查。最多8次搜索查询、16个实际有效文档页，优先官方一手文档和条款；同URL重复打开按实际请求留痕，不为用满额度重读。只访问当前DeepSeek/智谱官方文档、价目、服务/隐私条款，以及它们明确链接的同主体官方页。可从api-docs.deepseek.com、deepseek.com、docs.bigmodel.cn、open.bigmodel.cn、bigmodel.cn的实际导航查找；域名只是候选入口，不是假称页面已核。禁止模型API调用、登录、账单/账号浏览、下载SDK/安装依赖、非必要第三方调查。

给每项URL、官方主体、读取日期/页面适用版本、支持事实与未确认边界；报告用自己的简述和少量必要摘录，不复制整站正文。技术事实只取一手资料，无法读到的条款/账户条件保留未知，不能把公开介绍当当前账号确有权限或key已配置。

候选仍是现有deepseek_chat_completions/deepseek-chat、既定chat-completions/base路径与thinking disabled，zhipu_embeddings/embedding-3/512维。核当前configured/returned身份、结构输出、usage、embedding维度/批量、输出上限和账号适用性、保留/训练/用途条款、币种/价率/必要税汇率边界。发现不兼容/已下线/必需条件无证据时给准确差异与唯一最小建议，不能自行换模型、放宽10秒/65536bytes或提高费用预留；不阻塞其它合同文档的完成。

把原acceptance的L/I冻结rubric映射为逐动作最坏调用矩阵。至少含必要索引批、query+model、追问/反馈/参考/独立复测、面试、当前题解释至L10，以及缓存能确定复用的实际条件。区分本地动作/合成安全故障/真实语义；不付费重放已验证安全失败。给每笔最大请求/输出、价费依据、保守token上界及至少25%裕量、向上取整microunits；UTF8bytes不能冒精确tokens，framing/额外思考账单无上界时明确关门。

固定三活动ID仍为学习01800000-0000-4000-8000-000000000001、面试01800000-0000-4000-8000-000000000002、补证01800000-0000-4000-8000-000000000003；分额分别40次/10元、24次/6元、16次/4元，总计80次/20元，单笔250000microunits预留，1元=1000000microunits，所有失败/timeout/unknown计入同总额；72小时从未来明确激活起，每活动24小时/3600运行秒等原批准限制保留。给最坏总和与实际缺口，不为了凑80删Must或以本地parser代真实语义，不能用新库、新grant或新roster补余量。

账号/secret readiness只能在后续正常本地装载中做非敏感检查，本卡不读实际env值/私配/key，不向用户索账号凭据。官方条件和价率只是本次读取时点，未来真正开启Q前须复核过时/变化部分，不生成status=enabled的正式回执，不启动72小时收费窗。

## D 一次完整实施、取证、审计与必要采用边界

D应列下一完整实施成果的产品文件/函数变化、必要测试和最小runtime资源建议，普通修正连续完成，避免再拆准备/修夹具/补一例为多卡。给清楚前置和独立审计时点：新的权限边界必须在真实付费前有必要独立结论；稳定合成实现+真实PG零外发组合证明后才可申请主控Q启用回执，真实语义补证再按原审核窗增量确认，旧关闭四项不重审。

真实PG最小组合验证计划须调用两种provider的实际生产admission，真正PG roster SUM/同一全局锁/活动和操作持久预扣/COMMIT，near-count与near-cost跨provider竞争最多一个新提交、unknown不退/重开不清零、旧grant/活动/不同实例不能借新余额。给现有测试标识或准确缺失方法/观察点，不运行、不编写测试，不用SQL字符串/mock SUM替事务证明。已有只证明锁+内存SUM的证据直接复用其有限层，不再误说已完成组合。

资源只给下一实施卡的最小建议与核验字段。原S source已frozen、selector永久readonly、六个PG/failed/restore目标及其数据全部保留，不能建议回normal或清理旧资源重跑。新normal合成库/控制根的身份、固定roster与后续唯一真实grant关系要明确；合成预算测试和真实Q许可的数据身份分开、不清真实财务历史。不要求本卡实查Docker/端口或读取凭据，具体创建/启动由后续精确许可安排。

最后收敛为一个最小采用包，只纳入确需改变原批准合同的项目，并写旧/新、必要性、影响、替代和恢复边界。若只是既有授权内实现细节，明确主控可直接采用，不机械要求用户再批准；若有真正新增主要模型/公开接口/权限/数据外发决定，则给一个具体可审的合并决定，不混入已批准80次20元或未授权本人资料。不要以本卡写完宣称采用生效、代码已实现或Q可以调用。

## 只读边界、投入、检查与停止

只读上述项目文件和必要直接依赖、已有官方事实与有限官方新页。只写本TASK119结果与design/内证据/元数据读取脚本，不写产品、测试、SQL、lock、dist、README、DocuS、公共库、原需求、旧任务卡/报告/证据、Git或真实配置，不创建新服务/容器/库/卷/进程常驻，不启动原runner。产品import/compile/unittest/build/PG/SQL/Docker/Job/API/Browser/provider/费用/Git写额度全部0。当前无本卡运行尝试，项目旧81失败/所有投入/旧13元等不清零。

本卡接收首工具同步UTC及本机单调域，48小时日历，最后1200秒只保存；元数据命令单批<=60秒、累计wall<=1200秒，公开检索按上述8查询/16有效页。思考/阅读/间隙与未知按真实可得范围记录，不再以未观测跨账号中断冒连续工作或新许可，不需任何产品资源。工具受限只用获准只读替代，不绕平台权限；关键官方未知仅阻塞相应事实通过，其它A—D交付继续。

完成全部正文后做一次文档一致性核对：原grant/roster/四账/unknown/旧兼容和synthetic-only不变量，学习与面试至少两步的请求批准路径，函数/字段/状态闭包，当前官方事实与未知，80次20元矩阵及采用边界、路径和单一正文。不要为设计交付运行产品或前置POC，不把未采纳机制写成事实。

范围/主要前提被推翻、同类资料获取两次有据修正仍失败、许可硬门先到或必须触碰真实资料/费用时停依赖部分，保存已完成和准确缺口。无关键缺口不问用户普通技术选择。达到完整目标即停，不为用满额度追加研究。

结果先写一句结论及A—D完整合同，再给实际读入hash/官方事实与日期/命令或检索收据/检查结果、已知限制与最少未决决定、待主控同步建议。没有实际运行要明确0，不自称独审/实施/批准/项目通过。保存D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-119-result.md并完整复读；同卡修正置顶保留原文，不覆盖失败。确认真实可读后只回一句结论与完整可点击绝对路径，供用户带回。
