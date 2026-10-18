# TASK-104 / R-098 — G9集中独立终审与最后只读引用补证

## 目标与交付

你是本卡独立增强审计执行者。对TASK103最终G9实现、原始运行证据与执行控制作一次集中审查，并在同卡补最后一个只读浏览器场景，交付可供编排裁定整个批准G9切片的结论。只审业务，不修业务，不接管编排。

TASK103实现候选已稳定，续作02全部281个既有对象未改，只新增10个验证材料；三项核心缺证已实际补齐。剩余是引用响应晚到，因测试活动选择器错误尚未真正发起浏览器引用GET。此次把这个只读补证纳入终审，G9通过仍同时要求该性质有效与独立代码／证据／控制结论成立，不预先视为通过。

交付 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-104-result.md。审计、只读补证及预算／收尾原件只写 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/，与原103所有证据隔离。新运行fixture在 backend/tests/fixtures/task104/、浏览器脚本在 frontend/tests/task104-citation-audit.cjs，必要时建立，不改变原103脚本。完整成果统一返回，不把读代码、核证、引用补证分别转卡。

结论至少分代码、证据、执行控制三轴，给出通过／有条件通过／不通过／证据不足及确切适用范围。发现确定阻断留证，不修复；其余完成本次实际影响审查。不要为有限未实现项或非阻断观察添加新硬门槛，不宣告整个STEP013／M-1／真实provider／发布／项目通过。

## 项目、规则与接收安排

根 D:/shspic/project_NO3_RetroLume-agent，入口 D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。模式task_model、锁定V4.0／公共AGENTS CHG-0003，需求v1.1、架构v0.92、唯一执行动态v2.14，阶段07。公共根 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4；读DocuS/AGENTS.MD，适用WORK第4／6／8／9章、task_model/prompts/07_开发执行循环.md与TASK_TEMPLATE.md。锁定指纹见项目 DocuN/evidence/v4-migration-20260930/rules-snapshot.json，不采用后来版本。

接收A+增强执行，使用可用强推理模型，全新隔离审计窗口，未参与TASK102方案或TASK103实现／修正／验证。本次事务、不可变模型、权限清理、异步恢复与版本证据的集中裁定需要增强能力。实际客户端／模型如实登记，不按品牌追溯重审已完成工作。

父TASK103/R097，原合同TASK102/R096；关联G9／STEP013、NFR005、DR001—003、FR003／004／010、SEC001／002、MOD005、FLOW004／007、DATA006、API005，以及实际006／007／008／009／012消费边界、DEF019—022。G9-P已获用户2026-10-06批准；本卡是必需独立验收与已授权合成范围最后只读核验，不重复采用审批，不增持久模型。

不得继承实现窗口、实现聊天／思考过程、TASK103结果自评或103-work-decision的通过性结论。若已经偶然暴露则披露范围及影响；不能伪称完全隔离。先据原始合同、源码与原件形成自己的判定，不能复制主控或实现者结论。卡内给定目标与冻结身份不是审计答案。

当前291份对象与291完整post、20保护对象、9规则／原合同匹配；原233对象基线及全部差异链保留。见 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/orchestration-setup-20261007/audit-input.json 的完整路径／SHA。发现漂移先定位，不对旧快照签当前通过。

## 背景与最小充分上下文

先读原始批准约束及实际差异，然后直接源码，再按性质选原件核证。最小上下文如下，所有相对项均以实际根拼绝对路径，完整导航也在audit-input.json。

- DocuS/最终需求文档.MD 的持久背景、来源／事实区分、旧活动与恢复、限额／停止／数据退出相关条款。原始需求仅按需读取，不改写。
- DocuN/results/TASK-102-result.md 的A—D最终有效合同，以及TASK-102-work-decision.md的批准G9-P与固定澄清。它们是批准边界，不是103实现自评。
- DocuN/tasks/TASK-103.md中原始实施合同及C01／C02的授权、实际允许／禁止、次数与停止条款；只用于判范围与运行控制，不把其中背景摘要当审计结论。
- 初始前字节 DocuN/evidence/TASK-103/pre/、初轮final/pre-diff-post.json／product.patch、continuation-01/final/pre-diff-post.json／product.patch及continuation-02/final/pre-diff-post.json／post。当前完整冻结291对象；代码范围由audit-input.json的产品差异列表限定。
- 原始证据导航 DocuN/evidence/TASK-104/orchestration-setup-20261007/raw-evidence-navigation.json，指向103初轮、C01、C02的执行记录、as-run、原始输出、网络／DOM／PG／SQL、前后资源与账。不要通读所有重复副本；选足够证明或否定合同性质的原件，核hash与其版本。

产品实际差异覆盖010、memory模块、activities／teaching／learning／capabilities受影响接线、service_config／main／示例、前端记忆及相关工作区／引用。按完整diff审读，不能只看最近四项或只看函数文本未变就排除调用影响。直接依赖旧准入／终止／结果／v1主体可以读取，不重审旧D3平台全部实现或重跑G3—G8大套。

三组历史许可已结束且原账必须保留。初轮entry24／browser-driver3／build3／start23／SUP16；C01 entry12／browser-driver3／offline6／build1／start14／listener3／SUP22；C02 entry3／offline3／browser-driver2／start2／listener2／build0／SUP0。真实根合计39不是39个成功批。初轮三browser、C01前两browser及C02两个browser总FAIL原样，各自已成立子性质另判适用性。

C02最后fixture修正未经执行，不能据“已改section.library”签引用性质。最后三项原件是no-evidence-http.json、browser/result.json／late-edit-controller.json和tail/pg-before.json／final/persistent-proof.json；显式身份切换另有browser-02/late-switch-controller.json，但末后PG独立快照未取得，须限定证据层级。未收到COMMIT响应的旧保存key必须只读，不自动重发。

## 执行边界与资源

允许读取本卡必要项目合同、被审产品、原字节副本与原始证据。只写104结果／证据、新104只读runner／浏览器脚本。产品、原103代码／fixture／报告／证据、001—010／数据库模型／函数／ACL、worker／launcher／SUP／关门／结算／gateway／transport、依赖锁、用户配置／原件、Git、正式DocuS、公共库、归档全部只读。

新补证只用现有真实数据的GET／SELECT，不新建活动、记忆、教学命令／结果，不发业务POST，不做revoke／purge／cancel，不修改时间／资格／head／revision／budget／UNKNOWN，不伪receipt／citation／ready或patch组件状态。代码审计发现问题只报告定位、触发、影响和最小修正，修复回原103路线，不能在审计窗口自己修产品。

唯一可启动资源是旧pg1 CID4889202d9a58c622fb7cd2bd3087e5bceb7ad20a049c6550f4bd3588ff66ac11，名称retrolume-task-103-g9-pg1，命名卷retrolume-task-103-g9-pg1-data，库retrolume_task103_g9_main，127.0.0.1:55443。镜像sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f，1CPU／512MiB／pids128／restart=no／无host bind／无特权，旧标签TASK-103-G9-20261006保持，不改名或标签冒104新建。

pg2 CIDf96ac8dcb64648c76a2bc70f3f8b75969ada0ea0ea69b5896fe5ecb71affab85、pg3 CID4b813f9e4317aef9c613eb140fcb2d40c55a6bd98ee5d79807ea5851975d7f68仅只读inspect且始终停止，不连接数据库。它们的反向DDL落点／pending墓碑／正文不变。旧用户库及100资源完全不接触。

真实API／当前dist只在18103；使用与C02相同有效的非秘密合成运行配置和本次独立data／backup／Chrome profile，按已存内容hash复制必要本卡合成原件到104工作目录，不移动或写旧原件。数据、角色、库、容器、卷、旧profile全部保留，无DELETE或DROP。正式配置不读、不写；受信启动实际产品factory／router／读取，不伪API成功响应。

凭据仅在核精确owned资源身份后取owned admin Env单项到RAM。如本卡旧随机app口令不可恢复，只允许旧服务确认全停后，对精确retrolume_task103_app重置一次本次RAM随机口令，记录角色属性／ACL不变，随后实际应用用普通app。此为合成资源准备，不授权改其他role、owner、membership／权限或业务行。禁止整Env打印、口令进argv／源码／配置／日志；session token只内存，网络原件删认证头而保留路径／payload身份。

新许可 TASK-104-G9-AUDIT-20261007。主动21600秒，纯读取／hash／diff／证据整理metadata1800秒；真实只读准备／HTTP／browser累计600秒，独立清理300秒；本卡fixture离线300秒。正式产品测试／compile／build／迁移／SUP／model／tool／provider／真实外网付费均0。必要外部API事实最多6页官方支柱原文、计metadata；已有足够原件不联网重查。

真实组合根3、pg1 start3、API listener start3、browser／driver各3；离线检查最多3批各≤120秒。预计一个主根足够，余下最多两次只为本次独立fixture或读取目标的已定位不同原因修正，不三次盲重试。每根≤300秒且受剩额；如选择器或配置前置未满足，先保存DOM／网络／实际参数排错，不启动业务补建或无限换目标。新建容器／卷／角色、build／SUP均0，不借任何103余量。

从首真实读卡固定单调基点、主动截止和动作前计数，跨中断不后移；源码audit不每个查询另开真实根。预检失败／BLOCKED、浏览器／driver、超时与未知全部占相应额度；同根因两次有据修正仍失败或额度触顶停止相关运行，仍完成不受阻静态和原件审查。保存完整新runner／脚本字节和所有失败，不能偷偷启动第四批或给总FAIL换绿。

本卡串行独占104文件、pg1与18103。103原窗口已停止，仅等待审计结果，不并行改源／SQL／dist。若实际有其他写入或活动进程，先按归属确认，不误杀用户服务。

## 验证、证据与审计关系

先以当前完整差异形成静态和证据初判，重大数据破坏／越权风险先留证交回；没有相关阻断才运行最后只读补证。审计范围一次覆盖以下七类，逐条对原批准包给满足／不满足／证据层级与定位。

1. 七表与最小权限。010非空升级／前置／事务／反向边界、版本身份／容量／hash／复合FK／不可变guard、普通app列权限与NOLOGIN owner／purger、受限definer的search_path／PUBLIC／可信对象。三函数前向的源码／应用／实际catalog以及原行／安全属性继承成立，不能只据包自称。原CRLF文件hash33df4bcd8c040035f360cfc21c845e8f54e426832959e41477e67496f733c83c与统一换行文本915f0ed9…分域，重建函数指纹不能混换行口径。

2. 来源与事实权威。用户自报和有限观察可辨、原事实不可覆盖，观察取服务端实际事件及完整上游闭包，容量／循环／漏依赖／伪capture／跨活动拒绝，来源／反馈／上游变化传播及无关事件不误伤。固定记忆ID／version／revision／hash不得自动换新版，记忆只背景不作新引用或独立表现，不提升掌握或模型／工具权限。DEF019数值比较只按原批准最小范围评，不重开F01已闭合同。

3. 事务、CAS与v2接线。同连接来源／记忆头／活动前缀锁接旧后段，锁后范围／head／版本重核，幂等同键／同槽唯一效果及并发；实际claim／accept／launch／admit／mark／result／read／rebuild全链资格与不可逆出站窗口。v1字节保持，v2类型／父输入／工具标量／消息／持久正文有限边界正确；schema damaged可靠可辨legacy与v2残迹失败关闭。分析未改函数的调用影响，不能仅凭文本未变排除回归。

4. 撤销与精确清理。第一墓碑／原manifest先提交、第二清M3唯一精确效果、失败保墓碑和全部回滚、同键不自动补清；旧非规范M5收据保原字节可读，新canonical TEXT符合实际接口。禁止清007／009事实／来源／原件／WAL／备份或其他记忆，读取和重建不复活撤销内容。原物理缺正文／DB不可读／中途故障／权限反例证据按最终函数和实际条件使用，不默认为每个危险组合都跑过。

5. UI、鉴权和异步恢复。actual factory／session／Origin／body／分页只读投影、IDB owner／key／hash／草稿保留、GET恢复零重发、同槽冲突、新输入和完整绑定不被晚到读／保存回执覆盖、引用身份与Abort不复活。逐项核C02真实no_evidence409零副作用、陈旧POST409和晚保存，而非只看摘要；新保存显式切换没有末后PG快照的有限层级单列。不得因旧总FAIL丢弃已独立成立子项，也不得借子项扩大为总批成功。

6. 最终版本证据。V01—V24映射到真正as-run字节／环境／SQL／最终bundle，方法／窗口／元数据／语法／真实PG／HTTP／browser分层；对最终变化所影响项核必要正反例，不机械重跑全矩阵。旧未知worker底层原因、代码晚改和版本继承限制照实，原弱断言不得升级。真实provider质量／容量、未观察的前态／穷尽容量组合、离线整库回滚等不是本有限G9的已验能力。

7. 执行控制。三个旧许可的累计次数、动作前计数、反复预检／fixture失败、旧metadata保守／重叠、真实COMMIT响应丢失、失败未知预留／不退款、资源归属／收尾、偏差／未验／允许写域。核实际效果不只算报告的成功数。command a392c565-1731-4314-b22e-6cee9458f862的requests4／cost4000／tool1／settled12／R20与UNKNOWN原样，树零不授退款或重发，single_host_recovery=false保持。只读许可不能用于修旧失败状态。

最后引用迟到只读补证在新104主根按如下完整顺序完成，不再运行整个C02业务脚本。

- 先只读核现有目标activity a29a945b-a58f-4798-b4b3-93cc1e736aed、record e6964ce9-7686-45c3-b8b2-8e247cd25dcf、citation lc_c0655a9aed2099f2e0d9f328的真实workspace／citation当前可读。来自103/continuation-02/target-selection.json及browser-target.json，时间和过期overlay不得假称新执行资格。若该引用不再可读，从已有实际current记录有限选择，只GET不生成新记录；无法找到有效目标就记真正阻塞。
- 创建本次空profile，在真实产品页面定位section.library／活动列表／button.material。按实际页面发出的GET默认参数及cursor核数据与DOM顺序；必要用产品“加载更多”取得目标，不假定目标一定第一页、精确按钮数固定或标题唯一。界面本身没有完整ID标签时，以实际列表响应确定索引并核点击后的活动详情／teaching workspace确切ID，不能只凭索引签身份。
- 核所点引用button确实对应上述record／citation及当前viewToken，再route.fetch取得真正服务GET200原文，保存请求／真实响应／资格与时间，暂停向页面交付。不从旧JSON伪造成功response或改组件状态。
- 暂停期间用实际用户控件切到另一合法活动／记录，或用现有导航卸载引用面板；记录确切新身份、读取完成的网络／DOM和切换时间。操作为只读，全部业务POST应0。若采用卸载再回新活动，应同样验证当前身份，不能只在空页面观察。
- 尝试释放旧真实响应，实际Abort／交付失败可作为正确取消路径，但要留服务200与晚交付尝试／客户端接纳结果。条件等待后核旧原文／位置未在新身份复活，新面板内容未串入旧目标；记录前中后DOM／截图／真实网络，console只排除明确由所测Abort引发的预期项，不忽略未知错误。
- 绑定最终JS／CSS完整加载字节，不build；DB前后同一组业务表与头／记录／四账快照或行hash不变，证明补证GET／SELECT无写。不为追求全新PASS改旧事实，不再发送no_evidence plan／CAS／save。

新补证脚本及runner先在离线额度内做一次必要语法／路径／permit日期／selector与产品接口核对。复制旧helper时核C02日期字面量和权限假设，用104新账，不激活原已结束control；不重复“许可日期错”或“collection／limit20”作为新的盲尝试。

如代码发现阻断，仍完整给出本次可支持范围和最小统一修正清单，最后只读运行可在未受阻范围进行或标not_run。没有阻断且补证成立，给出批准单机／有限G9切片是否具备交编排验收条件。共享DEF019—022的建议关闭分别有源码和最终证据支持，不由你直接改总账。

## 停止与回传

覆盖本范围即停，不以增加检查或耗尽额度证明努力。高风险新发现、对象漂移、新权限／模型／用户数据必需、根因不稳、两次有据修正仍失败或相关额度到限，停受影响操作，保留完整原件与其他审查成果。不要追加自发实现、更多模块审计或新任务号。

独立300秒只收尾本卡PID／出生／命令身份、browser／driver与精确pg1，核18103／55443释放，pg1 Running=false／Pid0，pg2／3保持停止。只保留所有容器／卷／库／role／profile／旧样本；本次GET补证业务行／预算不变。非零退出、未知和清理局限照实，不停用户进程，不改旧资源状态。

完整结果先三轴结论与批准G9有限范围、实际四类产物和关键证据，再列独立性／读入／完整hash和diff范围、七类审查逐项事实定位、确定缺陷／条件风险／非阻断观察、最后只读引用实际结果、版本继承和未验、累计投入／原新预算／偏差／收尾、最小修正或建议关闭／下一步。区分静态通过、原动态证据有效和本次真实运行，事实支持不足不能写通过。

结果以本卡R098首轮保存；后续若获准增量仍沿本结果追加历史，不覆盖本轮失败。不读取103实现自评来补答案；隔离例外必须披露。保存并确认可读后只回一句话结论和 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-104-result.md 的可点击绝对路径，不签编排最终验收。

## 必要人工与待同步信息

用户只需把本卡转给未参与102／103的全新A+审计窗口，完成后带回104结果路径。原103窗口保持停止等待；本卡资源准备和只读补证已明确授权，不再询问G9-P、用户密钥或生产库。

共享任务号／R／DEF／CHG、正式文档及最终关闭由编排统一维护。执行者只给需同步事实和合格经验候选，不维护第二个总状态，不改公共库、原始需求或记忆。
