# TASK-115 / R-109 — review-01 四项修复与定向补证增量独立复核

## 目标与交付

你是原 TASK115 独立审计窗口的执行者。本轮连续完成一个完整成果，确认 TASK114 续作02 对原四项 P1 的修复、实际传播和必要补证是否足以关闭有限 STEP017。沿用原 TASK115/R109，不重做原七项全范围审查或旧阶段审计，不参与产品修复，不接管编排。

逐项回答 DEF034/F01、DEF035/F02、DEF036/F03、DEF037/F04 是否关闭，分别给最终代码依据、适用的实际运行、受控注入、未变机制继承与限制。形成代码、证据、执行控制三个独立判定和有限 STEP017 建议。主控裁定后才能更新 DEF 与 STEP，本卡不签项目、M-1、完整 NFR005 或恢复后继续执行通过。

结果置顶保存 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-115-result.md，原37767字节结果全文作为原字节后缀保留。新证据只写 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/review-01/。交付问题及传播复核、方法适用性、必要余门差异、真实计时/操作/失败/偏差与建议，不写主控最终验收。

本轮采用零新产品运行的只读复核。现有实际方法、源码差异和原始证据足以形成独立判断时立即收口。若仍存在确切原 Must 缺口，说明具体分支、已有证据为何不能证明、最小所需补证及资源，回主控一次处理，不自启动 PG、Browser 或重复原反例。

## 项目、规则与窗口

根 D:/shspic/project_NO3_RetroLume-agent，入口 D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。唯一模式 task_model，V4.0、公共 AGENTS 修订 CHG-0003。公共根 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，公共 DocuS/AGENTS.MD 和 WORK.MD 的适用2/6/8章继续生效。七锁定指纹在 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/v4-migration-20260930/rules-snapshot.json，未变同窗正文复用，漂移不自动升级。

口径为需求v1.2、架构v1.29、执行动态v2.53，阶段07。TASK115/R109/review-01/STEP017，父TASK114/R108，关联TASK113/R107、STEP017-P1、MOD008/FLOW007/API005、DR001—003、NFR002/003/005、SEC001/002与DEF034—037。原始需求用户维护，只读；新结论不反向降低已采用 A—D 合同。

接收 A+ 增强独立审计 Agent，继续原 TASK115 集中审计窗口。上一轮实际为 Codex desktop / GPT-6，当前身份如实登记，标签不代替真实身份。复杂取消、事务确认、绝对截止、身份新鲜性和正文权限的跨模块修复需要增强执行。原114工程窗口保持封存，不能由其换模型标签承担本轮；不派子Agent，不并行写入或运行。若原115窗口确实不可续，先回主控说明，由主控安排真实隔离替补，不自行改变独立性。

授权是用户已采用 STEP017-P1 并持续要求完成原任务，以及主控对合并修复后的原必需独审接续安排。无需重批方案。当前本轮仅已登记、待人工转交，未虚报派发/接收/开始。旧审计结果、失败、投入、旧工程用量和资源门不清零。

原审计关于意外读到主控候选摘要的披露继续保留。本轮不读 TASK114-result.md、实现聊天/思考/自评或记忆中的工程结论，不把主控已核身份当作产品通过。原 TASK115 结果和自产证据可复用；先由增量、契约和原始输出形成本轮判断，再置顶续写历史。如有新增意外暴露，注明实际内容、时间和先后，不假称未接触。

## 前置与最小充分输入

以下都是已保存文件，不要求另向用户索取正文。按事实与风险读取，历史已读同字节部分只核身份和引用。

1. 本卡、根入口、锁定公共规则，以及 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-115-work-decision.md 的本轮授权段。正式架构/执行动态只读版本、授权与相应模块；状态摘要不能证明四项关闭。
2. 原已采用完整合同 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-113/design/revision-01/current-contract.md，81813字节，SHA256为8a56ebf3c1715895e3ee7a0dcf1f621b591335400e9898aa00df8cb2b7a61aaa。原目标不变，同窗既有全文复用；仅补读真正涉及的条款。工程本轮合同 D:/shspic/project_NO3_RetroLume-agent/DocuN/tasks/TASK-114.md，21703字节，66d59f421d7514247f2cc88d6a229d5822d06448c9c6848058930153e8e35ce4c，给四修和原Must范围，不作为工程自证。
3. 本轮冻结导航 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/orchestration-review01-20261013/input-manifest.json。列当前235个文件、两项已移除构建输出、最终/pre原件、逐批as-run差异与原始方法导航。先核实际 hash，新增文件没有伪pre，已移除的旧输出不能恢复成当前输入。
4. 原四项反例及判断在 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/audit/。重点复用 offline/attempt-03 的01-restore-cancel-overwritten、02-publish-after-accepted-cancel、04-upload-after-accepted-cancel、05-post-capture-operation-deadline原件，browser/late-only/result.json和两截图，offline/readonly-projection-input-02.json。旧358份原件未改，不再采集原失败。F04的两个60秒异步诊断没有实际PG结果，原因unknown；不第三次机械执行。
5. 本轮工程证据基址为 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-02。该基址下 final/manifest.json、final/source、final/diff、pre-manifest.json、pre、as-run、offline、batches、closure.json、accepted.json均只读。原235个当前字节与final/source一致，manifest有237登记项。index-CJ8Yp7JQ.js为本轮deleted，index-DcQS7jxH.js为C01已缺失但本轮登记unchanged；不把两者当235当前文件或新缺陷。
6. 只读本次实际产品增量和必要直接调用。重点 backend/app/data_exit 的 operations/readability/control/api/packages/snapshot/restore/repository/deletions/reference/config/maintenance/files，以及 frontend/src/data/context/DataWorkspace/ReadonlyRecords/dataApi、frontend/src/main.tsx、README。测试实际方法在 backend/tests/fixtures/task114 的c02系列、backend/tests/test_data_exit_c02.py和frontend/tests/task114-c02-context.mjs、task114-c02-selected.mjs。001—013、codec、原角色/业务模型、Native/worker/preview直接依赖按真实影响核身份与传参，不把未改函数文本等同无传播。
7. 原工程唯一运行账 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/control/receipt.json、events.jsonl，C02 final/delivery-observation.json、final/delivery.json、closure.json及每批argv/资源记录。旧C01与原115预算原件继续引用，不能因新许可清旧锚点。主控最新精确只读资源观察在 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/orchestration-c02-receipt-20261013/current-owned-metadata.json；只证明观察时准确对象已停，不等业务或物理停止逻辑通过。

工程C02已实际返回，当前产品冻结，无在途消费者或并行写入。九个准确PG对象Stopped/Pid0、十七原消费者结束、相关端口无占。原source frozen、target07/generation1未写；新的C02业务域独立source frozen、target01/generation1另存。全部失败对象、卷、合成数据、原包和原控制保留。本轮不要求释放2GiB内存或解除端口再开跑，因为不启动产品。

## 四项必答与必要传播

### F01／DEF034 取消与不可逆成功

对原三处确定反例的真正修复点逐项判断。cancel_requested是否仅为请求；执行者是否等准确同步消费者返回、撤权/准确停妥后才确认cancelled；重复协程取消是否可能先抛出、底层线程仍活而假称停止。成功的短CAS是否同时约束revision、原状态、kind/阶段、准入票据，是否还存在临终读取latest revision覆盖取消的旁路。

检查package/no-replace发布、upload EOF、restore seal、source tombstone、maintenance/selector六种kind的共同协议及各真实不可逆点。取消先胜不能发布/verify/墓碑/selector，准入先胜应如实拒绝operation_not_cancelable；已存在文件或已提交事实不能被改写为没有发生。锁不能持有到IO结束。老terminal、同键补确认和UNKNOWN分支不赠新权限或重复消费者。

只据真实层判定：六kind私有日志顺序和实际文件/ASGI，PG加载后取消及角色撤销，实际源删除与selector拒绝/重新显式确认。它们不自动证明内核崩溃、丢COMMIT或所有半注册物理点。原正确Normal/RootLease/原SUP闭包可以继承，修复真正影响到的路径必须分析。

### F02／DEF035 一次绝对截止与完成确认

第一次真实消费确定started_ns/deadline_ns/受信clock_domain，传播capture、ZIP、hash、copy/spool/fsync/publish、PackageReader、allocate/start/initialize/load/seal/probe、DB连接/锁/statement、source mirror与Gate。重试不能重新起D，未知进程时钟域和旧inflight不能生成新执行许可。D是产品协议门，不受本卡审计工时、暂停或预算安排改变。

区分不可逆提交的真实事实与截止内成功确认。成功帧真正COMMIT返回后才可确认；确认前GET/列表不能授成功，迟到返回/镜像失败保留真实但未确认状态，不倒填时间、忽略迟到或把异常当已回滚。completion_protocol/execution_protocol及票据私有字段应失败关闭、兼容已有真实terminal、不进入普通DTO/包，也不改旧Native/工具/preview的时钟与StopProof权限。

这是本轮重点证据门。真实PG/HTTP/selector批后仍有api/config/control/deletions/maintenance/operations/packages/reference/repository/restore等增量，不默认用其PASS覆盖当前最终字节。最后 c02-boundaries-1161322062000000 在产品层绑定最终版，但它只跑六方法，不冒最终版全量PG。独立读每批as-run到final的实际差异及调用传参，对每项确认为何原PG结果仍适用、最终实际Hub/文件方法覆盖了什么、仍缺什么。源码hash不同不是自动作废，相同SQL/ACL也不是自动继承；以实际行为影响给有限判定。

### F03／DEF036 上下文新鲜性与稳定Hub读取

核所有setCaps/setContext、refresh序号、Abort、mount/unmount、类别/计划切换、迟到响应、主页面材料/阅读缓存和草稿归属。同control下selection_generation不能倒退，同代不同instance不能替换，异control仅受信新会话bootstrap。不能用只保护某一请求遗漏其余提交。

数据依赖读写必须校验当前dataset/instance/generation，稳定Hub历史GET与原键按合同保持可达，整个/api/data免namespace不能成为旧身份读正文的旁路。区分旧数据请求409与仍合法的Hub核对200，刷新与恢复不自动POST；UI不得因迟到normal返回重开写入口。

实际Chromium反序/生命周期批用受控routes，另实际TCP+sealedPG+最终bundle批无routes。核原始请求、DOM/截图、实际导入bundle及源映射，分别描述层与局限，不能把route中的selector当真实后台切换。当前最终index-NDc3grUN.js和相关源可继承同字节前端方法，不重build或重跑浏览器。

### F04／DEF037 正文资格与删除覆盖

同一READ ONLY/RR快照核受信ledger/库身份和完整memory_revision_readable。source/version/event/upstream当前资格与墓碑必须真实应用，false/unknown均不呈body。learning/teaching/interview等派生历史的source_refs/catalog/reference_hashes/memory_refs及选定memory同样不能绕过依赖失效。不能用改memory head/version/stored body/hash/purge掩盖只读DTO问题。

核合法可读正例、源替换、上游更新、事件修正、source deletion和默认overlay恢复后的抑制。仅body/null或顶层passed字段不足，读同T身份、原头/body/hash保留、具体SQL/函数调用、真实HTTP与最终sealed库的原始投影。正常管理连接用于九guard的测试不等普通app权限动态证明，app在线ACL的原证据只在真实未变范围继承。

### 原余门与边界收口

对原115明确保留的V08、V18、V19、V20、V21、V22、V23、V24、V28，给本轮变化后的充分性差异。原29项只列发生判断变化的项和原结论引用；不要机械重建整份审计或穷举所有参数。原已判充分的正常恢复、31域、两FK、同T/两锁序、共享引用、原SUP双EOF/四账及G11保持有效，除非本轮有具体传播反证。

私有job字段/阶段/显示文案细化与已采用模型和接口边界对照，不能让新completion协议暗改包、DDL、业务表、原生产权限或复制执行权。api输入422的错误回显、普通secret扫描和认证兼容仅检查实际增量。发现原Must确切未满足应保留阻断，非阻断限制不得自动升级为新硬门。

## 原始证据导航与适用性

以下路径均相对于前述C02绝对证据基址；要读各阶段原件、方法源码与as-run，不只读result.json中的passed。方法实际argv部分为最终回补，方法墙时没有独立同点采样；如实分层，不倒造命令/耗时。

- offline/c02-boundaries-1161322062000000.log，最终六方法7.027秒OK，包含发布两顺序、完整D/收据、spool/copy/fsync、成功帧迟到、observer同D、upload只读补确认。offline/c02-boundaries-1160855671000000.log等较早方法必须按as-run差异判适用。所有FAIL与不完整日志保留。
- final/method-index.json 的offline_exact实际为空。由offline原日志、offline/cases、对应as-run、events和固定方法代码补出本轮复核导航，不改工程索引或把空项当全量证明。本卡生成的索引注明重建来源与未知字段，不伪造同点采样。
- batches/c02-pg-source-resume-1159215656000000 的02-all-dependencies-valid、04-pointer-revision-hash-and-upstream、05-event-correction、06-delete-cancel-first、07-delete-admit-first、08-source-deleted-body-masked-head-retained、09-online-nine-guards、10-default-deletion-plan.json。九guard前共同准入通过且normal/data_loading_allowed=false，特定P0001/context要对上；不是42501或frozen一括拒绝。
- batches/c02-pg-cancel-1159293593000000 的01-actual-loaded、02-actual-revoked-before-stop、03-cancelled-stopped.json，核actual role NOLOGIN/password清空及停止事实，failed目标不复用、不seal。
- batches/c02-pg-normal-1159441609000000 的01-actual-loaded、03-verified-sealed-stopped.json，实际64行/2原件/9组件、31域、默认overlay与角色事实；原94行/4原件/14组件属于旧C01另一个有效方法，不混写样本。
- batches/c02-activate-1159966015000000 的01-activate-cancel-first、02-actual-maintenance-selector-rejection、03-normal-readonly-selection、04-selected-HTTP-old-Hub、05-selected-target-role-facts.json，真实source被冻结后的精确journal拒绝点为受控注入，不冒真实丢COMMIT。原selector未动，新域显式选择generation1一次。
- batches/c02-http-source-1159676406000000 的HTTP-projections、TCP-upload-disconnect、HTTP-secret-and-conflict、ordinary-log-scan、real-PG-whole-deadline.json和api.log，actual TCP/Selectorloop/真实PG，分别核已删正文、有效样本、未完Content-Length和冲突。session bootstrap命名token是明确认证出口，普通响应/日志扫描范围不得混写。
- batches/c02-browser-1156168718000000 的result/截图/请求时间线，实际Chromium、受控routes、最终bundle；batches/c02-final-http-1160210203000000 的browser-result、browser-events、HTTP-projections、context-dependent-vs-stable-Hub.json、actual-selected.png/DOM和api.log，真实sealed副本TCP/最终bundle，无route响应夹具。
- offline/cases 的reparse/junction和10a-external-before、10b-external-after，核真实哨兵文件集合/长度/hash及有效ZIP父路径重定向拒绝；链接/哨兵保留，不清理。JSON depth/component恰界超一、allocation/half-registration/seal故障按实际控制工厂层列明，不能写物理PG故障全部覆盖。

前向协议补改、oldterminal兼容、source mirror、可选Operation的默认None路径及参数贯通是本轮必须看的真实传播。最终补改没有再开PG是既有资源门事实，不能暗开，也不能只凭工程“SQL没改”忽略影响。已有充分证据可以由实际差异证明继承，不为补填全绿重新跑主要链。

## 允许、禁止、计时与资源

允许只读上述合同、对应源码/差异/原件/截图和必要直接依赖。允许文件hash、JSON读取、有限diff/AST结构解析等纯元数据脚本，不import产品或运行其方法。可写本轮报告与review-01证据、自己的只读解析脚本/方法导航/计时记录；所有新脚本只处理已存文件，不回放业务。保存时先核实际绝对路径和junction目标，不触证据目录里的链接。

禁止修改产品源码、原tests/fixtures、frontend/dist、README、001—013、依赖锁、任何用户配置/秘密、DocuS/AGENTS/公共库、原114/115证据/控制/账、报告历史、经验库/记忆。禁止运行compile/unittest/产品导入、SQL/PG连接、Docker启动/停止/exec/create、Browser/API/Vite/Native/preview、镜像pull/build、依赖安装、Git写、provider/模型/费用/公网、系统时间/服务/网络变更或任何删除。若平台要求审批，按真实权限处理，不以卡绕过；被拒只停依赖部分并报告，不伪造“已查”。

新许可 TASK-115-STEP017-REVIEW01-20261013，仅激活本轮只读活动段。活动本轮上限7200秒，含首工具读取、hash/解析、等待、报告保存与复读，最后300秒用于落盘；达到目的立即停，无需耗完。旧115保守活动5490.683454/21600继续累计，本轮实际加回，最多12690.683454，小于原总门；不清原UTC/mono锚点。原日历从主控保守许可起点2026-10-13T06:16:24.914938Z起48小时，到2026-10-15T06:16:24.914938Z仍为截止；本轮未另延后日历。首工具UTC与mono实采并记录，不事后伪称精确首点；漏记间隔保守计入。

本轮新增真实根/PG/create/start/API/Browser/build/Windows/preview/provider/费用上限全部0，不借旧根1的残量、旧审计端口、114余额或新业务域。必要时只能只读精确已登记对象的metadata，不唤醒引擎/消费者、不读Env/凭据；最新主控metadata已充分，正常无需重查。

旧115用量root3/4、API3/3、Browser2/2、PG/Native/preview/build0，offline125.610、保守hold14.874和活动上界5490.683454原样保留。本轮测试离线运行0，文件解析实际时间计入活动，不冒测试时间。

旧114累计root21/24、PG create9/12、物理success9/9、start37/37、Windows11/12、API8/11、Browser5/9、build5/6、offline172.317、hold462.047、C02活动9188.720111、原C01活动9739.953、旧55525.796及净投入unknown保留，余额不转。本轮工程已封存，源frozen、原target07与新target01只读选择不回退。旧G11/25/UNKNOWN/R60/count1/13元/626.566及所有FAIL不改。

## 执行顺序、停止与回传

接收后先实采身份/时间，核本卡授权、规则、最终snapshot与独立性。按四项和真实传播连续读审，逐方法决定当前字节适用性，把C02必要余门一起收口。各问题判定先形成并留证，再与自己原报告合并；不因一次已知P1重复停止其它不受阻阅读。

最终冻结漂移、独立性不成立、关键前置不符、超授权、新高风险、原Must确切缺证、根因不稳或活动/日历到限时停止受影响操作，完成已能判断的其余范围，交回具体差异。不直接修产品，不申请无依据大重跑，不新增TASK/DEF/CHG号或下一实施卡。

交付建议只能是有限增量复核通过、不通过或关键证据不足，并独立列三轴。F01—F04分别列严重度/触发/根因是否消除/最小剩余影响、代码定位、当前/批时hash和证据层。如可关闭，应明确原Must已满足的证据组合及永久只读/受控注入/旧记录/实际物理异常未测等边界；如不能，集中给真正阻断项和最小完整修复或补证，非阻断不变成新门。

报告包含实际客户端/模型、独立性披露、读取范围、hash链/有限diff、最终与中间版的继承解释、V差异、真实计时与零运行账、旧超限/unknown保留、必要人工及主控文档建议。原37767字节结果SHA256为7d34ec7e7f433effe3bf51367c68229a566dc525361a30c4b2c496702f4ca67a，先存本轮原件核副本，再用置顶+原字节后缀续写，不能覆盖原反例、失败或旧结论。

确认报告完整保存且可读后，只回复一句结论和可点击绝对路径，供用户带回主控。用户无需给密钥、释放内存或启容器；人工只有把本完整卡转交原115窗口及带回结果路径。DEF状态、正式架构/执行/变更账由编排者串行维护，执行者只给建议，不自签最终验收。
