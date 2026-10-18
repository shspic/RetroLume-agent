# 编排验收关闭通知 2026-10-02 当前

G6限定成果及096独立审计已由编排验收关闭，依据DocuN/results/TASK-095-final-acceptance.md。该TASK全部执行与运行许可结束，历史合同/失败/预算原样保留；不得用旧许可继续修改或运行。完整STEP、M-1和项目未据此完成。

## 以下为原合同与回收历史

# TASK-096 / R-090 review-02 G6三处修正与运行证据增量终审 当前完整合同

## 目标与交付

你是原TASK096的独立审计执行者。本轮只确认095续作01/02的实际变化及新增证据，形成能供编排关闭G6的增量结论。原完整审计未受影响部分直接继承，不全面重审，不接管编排，不修产品，不追加真实验证。

一次完成三处产品修正D1/D2/O1、两份后端测试差异、G1/G2原始运行证据及执行控制的必要增量核验。分别给出代码、证据、控制结论，以及原G6完整成果是否已经具备交编排验收条件。交付同根DocuN/results/TASK-096-result.md置顶review-02，保留首轮全文；本轮自己的证据只写同根DocuN/evidence/TASK-096/review-02/。

完成标准为差异及对象可识别、三处修正与原合同相符、证据覆盖及限制可独立重建、必要剩余门明确。不能因已有整批FAIL强制要求所有行为重跑，也不能因为checks全true就跳过断言/对象/原件核验。结论由你形成，本卡不预填通过。

## 项目、规则、关联与接收安排

实际根D:/shspic/project_NO3_RetroLume-agent，入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。模式task_model，锁定V4.0、公共AGENTS CHG-0003；公共根D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，公共DocuS/AGENTS.MD仍适用，WORK.MD第6、8、9节为本轮合同依据。同窗已读未变规则直接复用，指纹以项目DocuN/evidence/v4-migration-20260930/rules-snapshot.json为准，不自动升级公共库。

需求v1.1、架构v0.72、执行v1.94；父TASK095，关联094、G6、STEP006/008、API003/006、FLOW005、DATA007、NFR002/003/005、SEC001/002。用户已批准094最终唯一包，本轮是在既有必需独立审计中确认稳定修复，不是新的产品接口或数据操作授权。

接收A+，继续原TASK096真实独立审计窗口，已回首轮的WorkBuddy窗口。当前实际客户端与模型如实登记，不凭资源标签声称身份，不因模型名称变化重复已成立审查。此窗口必须与095续作01/02修复窗口为真实不同会话，未参与这些修改；即使客户端/型号相同也不能混作同窗。若真正无法维持独立性，交回具体缺口，不沿095窗口自审，不自动派子Agent。原095实现/测试窗口保持冻结。

旧096主动约60分钟、构建3.1秒、浏览器两启约47秒、两次夹具失败及首轮记录保留；原所有动态许可已结束。本次新增主动只读投入最多90分钟，并受原审计4小时总上限约束；如可靠总账余量不足则取更小值，无法确认精确用时如实分层记录，不清零。新增compile/unittest/build/浏览器/PG/Docker/应用/业务Windows/模型/网络安装运行额度均0。

## 原件与读取顺序

先本卡、项目入口、必要锁定规则、D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-095/orchestration-close-02/increment-input.json。该索引只是当前51项身份、5项补充文件与47项证据导航；不是审计结论。其SHA256为48e7a55e4e019e82a74af647352168196ac2437f48266210078ddc21c08b5b86，关键对象自行重算。

1. 复用你自己的D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-096-result.md首轮范围、D1/D2/O1/G1/G2及未变结论，以及同根DocuN/evidence/TASK-096/input-snapshot.json。旧51项内允许变化为三份产品文件及两份测试；其他46项按身份继承，不重复80项旧证据全量采集或审查。
2. 读取同根DocuN/tasks/TASK-095.md原合同及续作01/02合同。置顶回收通知只说明许可结束，不能替代验收。原C1—C12、认证/单SQL/有界列表/异步纪律继续有效。必要设计依据只取DocuN/results/TASK-094-result.md修正轮01及TASK-094-work-decision.md六项批准修订，跳过后来编排状态评语。
3. 三份产品为backend/app/materials/api.py、backend/app/activities/repository.py、frontend/src/activities/ActivityWorkspace.tsx。可信前件在DocuN/evidence/TASK-095/continuation-01/pre-originals/五份副本，pre-hashes.json绑定首轮审计身份。按前件与当前只读生成有限diff；两份当前测试为backend/tests/test_activity_workspace_api.py、test_activity_workspace_reads.py。必要直接调用者只读local_session、pdf_review/api及活动API相关段。
4. 续作01实际批件为DocuN/evidence/TASK-095/continuation-01/final-merged/的hashes-pre/import/final.json、unittest.out.txt、pg-segment.json、browser.out.txt及runner。失败预检与新旧尝试从attempt-ledger-continuation01.json、run_pg_batch.py按必要范围核；不运行它们。
5. G2复用字节证明为DocuN/evidence/TASK-095/orchestration-reuse-02/reuse-binding.json。不要把其中编排采纳文字当结论，独立核整文件还原方法、hash与26个OK方法适用性。剩余单方法原件在continuation-02/final-run/unittest-pagination.out.txt，结合hashes-import/final.json、pg-segment.json和run_c02_merged.py实际命令核验。
6. G1原件为continuation-02/final-run/browser-report.json、browser-segment.json、browser.out.txt、shots/五截图、hashes-pre/import/final.json。续作02browser-fixture.diff、pre/post-hashes.json、pre-originals及当前frontend/tests/task095-continuation01-browser.mjs用于差异归属。
7. 批时脚本缺独立完整留存件，现有可校验的逆变换重建副本为DocuN/evidence/TASK-095/orchestration-close-02/browser-as-run.mjs，SHA256为5e541e22e60b3d69e2e9f334ce52abd3248c2bb0fe01622f8a38aad9dbc124a3，与原运行hash相同。它是编排文本重建，非当时原件，未执行；recipe在increment-input.json中。可独立逆变换验证，全脚本以该批时字节审查，不能用当前未运行版本代批时控制流。

绝对路径均相对上述真实根拼接，公共库只读。同窗已读未变正文与旧证据直接复用，只补实际变化。禁止读095-result.md、095-work-decision.md、096-work-decision.md、实现聊天/推理/自评及含实现记录的记忆文档。原始账本备注或索引中的判断只作为导航，不能作为独立证明。自动注入或意外接触如实披露，不伪称未见；结论仍须由相关源码、合同和原件独立支撑。

## A 三处产品修正与传导影响

D1核materials.repository恢复local_session(request)默认固定来源拒绝，PDF复用链同步恢复；活动已批准的allow_own_origin保持。不能扩大白名单、会话token、TrustedHost或Sec-Fetch含义。核API新增的认证区别方法是否真实覆盖materials/PDF与活动的不同拒绝/接受，沿首轮未变认证结论继承。

D2核轮询在途释放、慢响应不重入、隐藏暂停/恢复只GET、卸载清理，以及list/detail/operations/openOperation/loadMore等请求序号与选择上下文保护。异步失败不能永久卡死或覆盖新选择；显式动作后的读取仍允许，不能把合理显式读取或不同组的并发简单列为全部禁止。仍为约3秒只读轮询，无自动POST/换键/自动业务重试或新缓存队列。

O1核列表单SQL只投元数据及候选资格布尔，不返回正文列；单项仍完整校验payload/hash/来源/绑定/kind，损坏正文单项拒绝但不拖垮合法元数据页。候选可读标识不冒充正文已经完整验证。核心写路径、原_RESULT_READ_SQL、持久模型、worker/监督、transport等未变范围继续继承。仅因清理已无用途replace导入而变化不升级为新硬门。

两份测试新增/适配必须针对真实差异，不弱化原业务断言。分页用例适配专用库既存合成行时，必须仍保证本例三ID全部被遍历、首页顺序、全局倒序、无重复和非法游标拒绝，不能仅为绿色删除正确断言。未授权删除残留行或改系统/数据库时间。

## B G2最终后端证据适用性

先区分续作01批时reads c1c40c356ca22e719f2ba1f7a937f9546eff48c10fb089d066c51a112b5ed19e与其原pre 5a7c8941…，后者不是该批实际测试字节。当前最终reads为ed32fe37004bde9af37a33066cb8c79755754aa6fcdff7cd24f51ee06fbae268；API测试为a5c95c794e8e8f91ff71ba3427e964dd177ee4be413c6966750bb7ec31885a4f。

核还原当前reads的分页方法为pre方法后，整文件hash是否精确等于实际批时c1c40c…；其他方法未变及后端app批时/当前绑定是否成立。实际27方法中26个OK允许继承，但其中含离线方法，不称26全部PG或旧整批通过。单SQL实际计数、cursor返回列不含payload、损坏正文列表/单项区别反例须读真实方法与原始输出，不接受SQL字符串断言替代。

续作02只运行ReadProjectionTests.test_activity_list_pagination_cursor。核import/批末最终字节、真实专用PG方法、returncode/Ran1/OK且非skip、清理与残留边界；阶段11.713秒及测试0.488秒分开记录，不虚算。就这些证据判断G2是否已闭合，不重复reads/API整套，不追补不存在的历史as-run身份。

## C G1浏览器原FAIL与有效行为子项

独立读批时5e541e22脚本，确认真实产品dist静态服务、全合成API路由、未知/外网拒绝、请求记录/检查形成位置、异常传播、每场景观察窗和失败后是否继续。判断nine steps实际执行及25 checks是否有足够辨别力，不能只看steps标题或当前修正版；以请求时间线、DOM等待、对应截图和原控制流交叉判断。

原browser-report整体ok=false，failures含s3 after-action slice contains POST；post_total汇总字段为0，与记录计数须分别核。针对s3检查beforeS3b记录于显式点击前还是后，切片是否必然包含该显式POST，刷新观察窗是否已独立证明无自动动作，显式动作后是否有读取。重计完整log的方法/时间/路由，不用执行者一句“只有夹具错误”代独立判断。若行为证据本来成立，可以采纳有效子项，不以要求整批汇总变绿作为额外门。

其余影响点为普通刷新不恢复旧选择、unconfirmed/submitted意图刷新只GET、显式同意图动作一次、慢列表不重叠及跳过在途tick、隐藏/恢复只GET、活动与正文迟到隔离、失效抑制继续入口、展开真实单项正文、卸载后无自动请求。隐藏通过document.hidden及visibilitychange合成，只证明对应事件处理，不夸称完整OS遮挡行为；合成API只证明前端，不冒充新增真实HTTP/模型/Job链。

核当前frontend/dist/index.html及index-CiaiBKAO.js与续作01构建/续作02加载原件的对象关系，勿把源码和bundle同时有hash直接说成构建起源已经证明。原096旧bundle绑定仅继承未变部分；需要时读现有构建原件和新bundle实际增量，不启动重建。G1的最终产物、真实已运行界面及改动源码关联须明确说明证据边界。

当前fixture ee9074b8f85ab94d382c6843e5d1d3f6d3a6eb42dfc69d14c9b8f151f15970c1比批时多两处收尾后修正，实际not_run。仅文本/node语法声明不算修正版行为通过；但测试报告修正是否需要真实重跑，按其是否增加尚缺的产品覆盖判断。保留原FAIL，不改写原报告、脚本运行史或预算，不运行重建/当前脚本。

## D 执行控制与审计边界

核续作01/02的runner和原始账，旧全项目审计控制不重做。新增续作02唯一入口/container start/browser start各1，累计入口10/start9；业务PG阶段11.713加浏览器62.727为74.440秒。旧claim10/保守监督14、原7/6入口超限以及漏时原样保留，实际控制偏差不因行为成立消失。新许可与旧用完许可分开，不以同一窗口或余秒数清零次数。

精确资源仍原task095合成DB/role与e49d3acc…容器；白名单、权限、stdin口令、finally、停止/端口原件按必要范围确认。无需重做Docker inspect/启动/收尾，不读或恢复用户配置/秘密/已删除dsn.json。容器停止取原件时点；编排的2026-10-02 00:10端口及相关fixture进程观察不等于实时Docker查询。

相同客户端模型不等于独立性，也不自动否定真正隔离的原审计会话；披露实际窗口和接触范围。只审新增差异与影响，首轮其它结论及旧D3/G5运行证据继续复用，不以新增可选观察扩建新服务或监督平台。

## 允许、禁止、投入与停止

只读上述相关源码、合同、原件及必要直接依赖。只写D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-096/review-02/及D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-096-result.md置顶轮次，历史不改。

仅允许文件读取、有限文本差异/SHA256、原件JSON等文本处理，不导入/执行产品或fixture，不运行compile、unittest、node检查、build、浏览器、PG、Docker、应用、Windows Job、网络/模型，不安装、不Git写入。产品/正式测试/dist/锁/正式DocuS/公共库/旧证据/用户配置全部禁止写。新增运行额度0，没有可借剩余预算。

原095期间无并行写入，本次串行审计，编排只维护自己的共享文档；审计结果整合与最终G6裁定归编排。达完整增量覆盖即停，新增主动最多90分钟并计原4小时，不自行扩展。对象漂移只停止相关判断；确定严重缺陷或关键不足留证，完成不受影响项后一次交回。只有影响本轮通过的具体缺口才提出最小后续目标/依据，不自动复跑失败，不把非阻断观察变验收门。

## 回传与人工

结果先一句结论，列D1/D2/O1、G1/G2与代码/证据/执行控制三轴，指出可否由编排关闭095/G6以及真正剩余阻断或有据无阻断。列原FAIL与有效子证据、最终对象hash、重建副本身份、继承范围及限制、差异与所读原件、独立性/接触披露、实际只读操作与投入、未验证/风险/偏差、待同步文档及建议下一步。

保存原096结果置顶review-02，原首轮文字与证据全文保留，不填写编排最终验收；不宣告完整STEP006/008、M-1、真实provider/用户库或整个项目通过。用户只需人工转交本卡，完成后带回结果路径，不提供密钥、不启动数据库。

确认完整保存且可读后只回复一句结论及结果可点击绝对路径。

## 以下为历史合同 不授予新的运行许可
# 编排回收通知 2026-10-01 当前

本卡审计已返回，独立审计交付通过，运行许可结束；报告的有条件G6验收建议尚未采用。TASK095沿原实现窗口续作01合并合同缺口与补证，详见DocuN/results/TASK-096-work-decision.md。当前不对原对象继续运行或重审，保持原独立窗口用于修复返回后的必要增量确认；增量合同须待真实结果后再交，不能使用本历史卡剩余额度。
# TASK-096 / R-090 G6完整成果集中独立审计与最小界面补证

## 目标、角色与交付

你是独立增强审计执行者，一次审查TASK095完整G6成果及证据，分别判断代码、验证覆盖和执行控制是否符合批准合同。只读业务，不接管编排，不修产品或正式测试。重点为新增浏览器动作信任边界、读取与恢复、配置/监督组合及受影响资料/PDF权限；不重审全项目，不重跑G3/G4/D3/G5整套。

交付D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-096-result.md，证据D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-096/。允许严格有限的独立合成响应与真实浏览器取证，以补最终UI正文显示及必要状态证据；不启动PG或业务Windows监督链。必要缺口集中列出，不能用代码分析冒充动态通过。

## 项目、规则、授权和窗口

项目根D:/shspic/project_NO3_RetroLume-agent，入口同根AGENTS.md。模式task_model，锁定V4.0/CHG-0003。公共根D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，读DocuS/AGENTS.MD；WORK.MD第6、8、9节适用。指纹以项目DocuN/evidence/v4-migration-20260930/rules-snapshot.json为准，公共库只读、不自动升级。

父TASK095，关联094、G6、STEP006/008、API003/006、FLOW005、DATA007、NFR002/003/005、SEC001/002。需求v1.1、架构v0.69、执行v1.91。用户2026-10-01已批准094最终裁定唯一包；本卡是稳定成果必需独立审计和有限合成取证，不重新询问旧批准。

接收A+，全新隔离会话，未参与092/094/095实现或设计，不沿095窗口。优先不同模型家族，真实客户端/型号如实登记，不因型号标签重审已成立证据。人工转卡，不自动派子Agent。本卡期间原095窗口冻结，不并行修复。发现对象漂移只停止受影响结论，不对旧快照签当前通过。

新审计主动投入上限4小时。旧095尝试、失败与超限原样保留，全部运行许可已结束；本卡不借其未用秒数。自己的有限运行单列，详见运行段。

## 独立输入与读取顺序

先根入口、锁定规则、本卡及DocuN/evidence/TASK-096/input-snapshot.json。该索引保存51项当前产品/测试/依赖及80项原始证据的hash，仅为身份导航，不是审计结论；独立核对关键对象及证据适用性。

1. D:/shspic/project_NO3_RetroLume-agent/DocuN/tasks/TASK-095.md完整原合同，文件范围、资源、额度、C1—C12仍适用，不以本卡摘要遗漏要求。
2. D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-094-result.md修正轮01 A—D，仅设计合同；D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-094-work-decision.md置顶六项设计修订优先。它们不是095实现自评，其中待批准时间点已由用户批准解除。
3. 实际源码/测试及必要直接依赖；DocuN/evidence/TASK-095/final-snapshot/product-hashes-final.json和20份最终副本；遗漏的frontend/tests/task095-browser-rehearsal.mjs、PDF调用者按影响核对。旧前件按项目实际证据定位，不能用历史Git HEAD猜本卡全部diff。
4. 原始证据DocuN/evidence/TASK-095/attempt-ledger.json、common.py、run_batch1_pg.py、run_batch2_win.py、run_batch3_final.py、run_batch4_final.py、inject/sitecustomize.py、win/bootstrap95.py、finalize.py；batch1—4实际测试输出、steps、HTTP返回、浏览器stdout/截图，必要transport-send记录。全部只读，禁止执行这些旧runner。
5. 必要既有G3/G4/D3/G5结论从架构已批准范围定位，然后取直接相关原始证据。正式文档仅取需求/接口/批准边界，跳过095自评及编排验收段。

禁止读TASK095-result.md、TASK095-work-decision.md、实现聊天/推理和用户复制的执行自评。原始账本中的执行者补录说明不当客观证明；必要接触如实披露，独立判断基于源码/合同/原始输出。意外接触不得伪称未读。默认不读取095/runtime私有配置、数据或应用日志；确需核某段合成原始日志时限定必要脱敏内容，不输出凭据，不读或恢复已删除dsn.json。

## A 真实对象、差异和兼容

确认对象身份、实际改动集合、最终字节与各次as-run版本。pre=null可能未存档而非新增，最终快照存在不证明每批执行了它。核对repository/service是否只增允许只读方法/薄包装，核心写路径/_transaction/原continue是否保持；worker/迁移/gateway等冻结范围有无变化。

正式测试改动须有原行为依据，不允许删除/弱化断言制造通过。test_d3_recovery是否超允许清单、test_materials旧断言调整是否合理、未列彩排脚本等按事实判断。若缺pre，寻找现存可信前件；仍无则限制相关差异/复用结论，不造历史、不把全部当前测试算本次新增。

## B 浏览器授权、配置和既有接口

核对Origin、Sec-Fetch-Site、Host/端口、代理头、会话token获取/比对、未知来源/跨站拒绝、CORS/简单CSRF与本地监听边界。分析allow_own_origin及材料/PDF/活动各调用方，不能因称“提取”就断言等价，也不因存在变化自动断言漏洞。合同范围偏差与可利用安全缺陷分别列明。测试端口不得成为允许任意来源的理由。

L0/L1/L2按原合同独立失败关闭，坏模板/类型/字段不能启用；浏览器无DSN/key/额度/executor/G/任意URL或argv输入权。配置10秒、请求字节与输出限制满足OneCallInput，序列化前置、启动一次加载/不热更新明确。key不泄漏；capabilities存储就绪判断不能掩盖不兼容schema或异常。代码未来配置能力不等于审计可访问用户库/私有配置，无自动迁移。

## C 读取、账本和文案

四类数据读取每请求单SQL，同快照来源/范围/绑定/kind状态符合既有只读契约，合法正文可读、失效抑制正文；列表无正文，元数据有界，游标/大小/空末页/多字节与JSON转义符合要求。不把跨请求/跨页说成固定历史快照。

四账独立，S包含保守折叠，running不证明进程存活，取消不是退款/即时杀树/远端撤回，120秒仅管理预算非完整HTTP上界；D3单机故障模型与M-1未完成边界不缩水。页面不能暴露内部路径/hash/SQL/身份或执行低信任HTML。

## D 动作、意图和异步界面

创建范围和额度由服务端权威、锁内检查；409只在只读核事实后呈现。意图先存再POST、source_ids不可变持久、禁用/损坏存储门、刷新/丢响应不自动重发换键，清除不取消在途，输入本地持久须可知晓。

继续仅有效模型父、沿原service及真实监督链；读取无执行副作用，断线/shield行为准确。同键原子模型准入/发送与可能额外监督/时间开销分开，不要求不存在的全历史参数幂等。审同键预查竞态、admit前失败后重试、取消和旧代次。

列表不含正文，展开必须取单项正确显示。活动/操作切换、慢响应乱序、轮询刷新及结果失效不能串旧正文或错误开放继续入口。只读轮询有界不重叠且可停止，网络失败不自动执行动作。

## E 证据覆盖与复用

将C1—C12逐项映射到真实方法、样本、原始输出和最终对象。分开整批失败内有效子项与整批通过，不以截图标题/自评代断言。核对最终构建和浏览器bundle；最后修复只有类型/构建成功不足以证明显示行为。

reads测试最后仅新增skip装饰器时按实际方法差异复用，不为文件hash不同机械重跑PG。陈旧窗口取消前端、数据库折叠和本地停止是不同证据；坏PDF拒绝不等于完整PDF核对流通过，按实际影响判断所需覆盖。已有充分证据不重复采集。

在静态未发现会推翻相应测试的阻断后，允许下面一次最小浏览器专项。若已有产品阻断，停止依赖动态补证，完成其他只读审查后合并发现。不为已知失败对象耗尽预算。

## F 尝试、资源与执行控制

按原合同入口即计数，从runner/原始记录重建预检失败、真正启动次数及业务监督会话，不能用batch标签代实际次数。核对账本补录和各批windows_sessions字段，区分启动尝试/成功；无法精确还原写可证下界与缺口，不凑整数。耗时包括可证abort范围，不因剩余秒数存在追认超次数许可。

核精确容器/卷、权限、专用DB/role、网络守卫与传输注入是否保持真实链、finally和树/句柄/端口收尾原件。不实时操作Docker重复旧收尾；记录证据时点。超限与越界不因最终成功变成合规，也不凭控制偏差自动否定充分绑定的全部行为证据。代码、覆盖、执行控制三轴分别给结论。

## 写入边界与有限动态授权

只写本卡evidence及TASK096-result.md；禁止修改产品/正式测试/迁移/依赖锁/正式DocuS/公共库/旧证据/用户配置，禁止Git写入、联网安装、真实账号/外网。允许新增审计脚本及合成响应仅证据目录，产品不得依赖它们。

允许最多一项针对实际认证拒绝边界的进程内HTTP或纯函数探针。它与必要离线准备/构建累计最多300秒；静态已能判断则不运行。只导入必要定义，隔离合成参数与替身仓储，无任何DB连接，不继承用户.env/DSN/key。不重跑全部后端测试。

浏览器一次定向批，业务最多300秒，收尾预留60秒；浏览器最多启动2次，第二次仅因审计夹具自身确定修正复验失败项。产品问题不可本卡修复复跑。准备/构建最多一次；仅审计命令参数错误可一次有据纠正，仍计300秒。既有frontend/node_modules/Playwright及已装浏览器，无安装下载。

仅本卡静态服务127.0.0.1:18096，先核空闲，冲突不kill他人工作。服务隐藏启动，记录所有者/PID/启动时间，收尾只停本卡服务/浏览器。所有合成API请求由Playwright route或有限本地fixture截获，只有静态资源可访问本服务，未知/外网请求拒绝且留证。PG、Docker操作、业务Windows Job与模型调用额度均0；不得使用095旧runner或旧余量。

必须使用真实最终ActivityWorkspace和应用。优先已有且可证明绑定最后修复的bundle；无法绑定则用现有Vite从冻结源码构建到本卡evidence下专用空输出目录，不覆盖正式dist/锁。保留源/输出hash与命令退出码，不手写复刻UI，不修改产品JS绕过授权/状态。

合成响应按当前API真实序列化结构构造，独立读投影/现有原始响应确定字段，保存样本及其契约依据。最小场景为列表无正文→点击单项→显示text/json及低信任字符串；切换操作与慢回包不串正文；失效响应不能泄漏旧正文/开启继续；刷新只GET无POST。陈旧running取消前端若有缺口，可同批用合成响应验证两步取消与只读更新，但明确仅前端行为，不能称真实折叠或杀树证据。

专项只补前端和响应契约，必须确认旧HTTP/PG/监督证据仍适用才能组合验收。若必须新增真实DB/业务会话，给精确最小目标与理由，本卡不运行。每次运行前保存目的/快照/样本/预期/次数/截止；原命令脱敏、逐断言结果、控制台/请求日志/截图、耗时及资源收尾均保留。不要把浏览器进程当业务监督会话。

## 停止、回传与人工

覆盖充分即停。确定缺陷留证，完成其他不受阻检查后合并一份清单，不直接修；数据泄露/破坏风险先停止相关运行。对象漂移、关键前提不足、根因不稳、超范围、两次有据夹具修正仍失败或预算到限则交回，保留旧失败，不换窗口清零。

报告先给代码、证据覆盖、执行控制三项结论，以及完整G6能否交编排验收；每发现有位置/触发/影响/严重度/最小修正归属，区分确定缺陷、条件风险、非阻断观察。不将可选增强升硬门，不用有条件通过掩盖必需门缺失。包含独立性与接触范围、对象/差异重建、C1—C12对应、复用/局限、实际本卡操作和预算、收尾、必要人工与建议下一步。

不得读取095自评来对答案，不维护共享编号或正式状态。结果D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-096-result.md，证据同根DocuN/evidence/TASK-096/。用户无须提供密钥或启动数据库。保存完整核可读后只回一句结论和可点击绝对路径。最终验收由编排裁定，不签M-1、完整STEP或整个项目通过。