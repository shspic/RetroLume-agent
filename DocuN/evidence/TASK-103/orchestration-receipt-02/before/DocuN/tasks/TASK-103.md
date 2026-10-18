# TASK-103 / R-097 续作01 — G9剩余实现与最终证据一次收口

## 目标与交付

你是原TASK103的实现执行者。本轮沿同TASK/R、G9-P已批准范围和全部历史接续，完成当前剩余代码/数据库函数/工具/浏览器及验收性质，保存稳定完整候选、最终字节证据和资源收尾后统一返回，不自签独立审计或G9/项目验收。

原已保存代码与真实子性质保留；本卡不是重新开始，也不是只再跑一次旧脚本。原卡的产品文件写权/包语义继续适用，本节覆盖起点、资源复用、配置口径、剩余验证和新配额。批准依据仍为用户2026-10-06“批准”G9-P与TASK102结果/已采用work-decision，不再询问采用包。

交付继续置顶 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-103-result.md，标题续作01，原24351字节全文保留，原SHA b62695f7da2b3b5c65553f7a7ec5f87a979c7029c3e2b33ed5ee9cb06fe21b13。新证据只写 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/continuation-01/，不覆盖旧runs/failures/checkpoints/pre/post。

完成标准：下面剩余清单实际闭合、未变子证据准确继承、所有新性质绑定最终源码/SQL函数/测试/运行环境/最终bundle，完整候选和执行控制可独立复建；存在真正不受支持的分支则按有限边界说明，不造假或扩建。整卡完成即停，不按一处修复/一个层分别回传。

## 项目、规则与接收安排

根 D:/shspic/project_NO3_RetroLume-agent；入口同根AGENTS.md，task_model、锁定V4.0/公共AGENTS CHG-0003，需求v1.1、架构v0.90、唯一执行动态v2.12，公共阶段07。公共根 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，读DocuS/AGENTS.MD；适用WORK第4/6/8/9章、07_开发执行循环和TASK_TEMPLATE按同窗已读未变复用。锁定指纹仍项目DocuN/evidence/v4-migration-20260930/rules-snapshot.json，不采用新版/其他模式。

接收A+增强执行，沿实际完成TASK103的原业务窗口，使用可用最强推理资源完成事务/类型/权限/最终证据；具体型号如实登记，不重审已完成的品牌。原窗口确不可续才用新A+带完整文件交接，不派子Agent，不占独立审计窗口。

关联原G9/STEP013与102/R096、G8/100/101及原需求/架构；DEF019仍为修正候选待独立确认。主控登记DEF020/P2（真实普通continue业务拒绝却HTTP200，末尾映射修正待实测）和DEF021/P2（memory结构damaged时全活动失败关闭，能安全识别的无选择legacy降级未达合同）。没有发现就直接自行占共享DEF号的许可。

当前266个存续源/测试/资产、2个已删除但pre保留资产和10合同/规则身份已普通核一致；246份post运行清单只是其子范围，不冒完整266份运行副本。基线见 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/continuation-01-input.json。010最终3ffe743b64037039512df683b1e21386b8869fc1726fcc9e3da04a4dac2d1194；memory/repository.py cb4bd4adc8e2d3744692b6577fc51cd2bd9a43dba522472a24a55ee90ce4a5d5；activities/api.py 8207d7bea2f22e7167c02aad0b4c31cc8e223ac06e92d3be378014a44f8863d3；MemoryWorkspace.tsx 4d1a449e175c8107f3dfc8882151b05a62c358a4a7f1b83cd4c5950d6477d79d。首改前补pre/hash，漂移辨归属，不覆盖。

原许可已结束：entry24/24、browser/driver3/3、build3/3；offline4/6、container/volume create3/3、start23/24、listener3/12、SUP16/64。原主动保守19020.059186/28800秒、offline及build15.453、real539.251（内外重叠保守不返额）、cleanup22.018、metadata548.453及未知/全部失败保留。其余时间/次数不借本轮；先前browser三总FAIL保持，不因本卡新许可清零同根因失败。

新许可 TASK-103-G9-C01-20261006：主动21600秒、离线1200、真实准备/PG/HTTP/Windows/browser总3600、独立清理600、元数据600（含于主动）。新根入口12、container start16、listener/fake启动合计6、SUP launch尝试24、browser/driver各3、build2、离线6批。新create容器/卷0，无新镜像/依赖。根入口单次≤900秒、离线批≤180、build≤300、SUP管理≤50，受剩余总额和原字段域限制。动作前计数，失败/BLOCKED/诊断也是实际入口；全部读取/修正/封装用同一固定单调截止，跨窗/日期/方式不清零。本轮实际新使用0，待转交，尚未发送/接收/开始。

## 背景与最小充分上下文

读本入口/锁定AGENTS、当前完整本节、TASK103最新真实结果及原102批准合同与work-decision；未变同窗内容直接引用。原G9包/源码边界在下面旧完整卡中保留，只补变化，不全仓重读。父G8等未变证据继承，但新G9源码/行为不得仅靠已有结果自评通过。

必须核final/pre-diff-post、accounting-final、runs-ledger、function-diff、bundle-chain和SQL快照；按剩余性质读取原real07/08/09/16/19—24、browser03 checkpoint/实际两页缺证据的范围。已提交UNKNOWN/root21序列化错误、已清理/撤销/修订事实只读确认，不重发或重新seed同效果来换绿。

源码重点是memory/repository、010两个末改函数、activities/api映射、MemoryWorkspace与frontend/tests/task103-browser.cjs以及原task103实际fixture。必要资料无法读就只交具体缺口，不凭聊天或猜文件路径造实验；不读真实配置/旧role密码。

原SQL最后修改只有离线，pg1/pg3实际函数仍旧；新严格指纹因此先关能力。HTTP real24业务拒绝有效但返回200已改409，未实测。旧浏览器03已证明最终包保存/刷新GET/owner分离的具体步骤，未证明后续完整流程；second页详情/输入/DOM缺件，不能断言纯fixture。代码有editSequence保护，不因泛泛“等待竞态”全面重写；必须同时核加载时绑定身份、输入epoch和保存能力。

## 执行边界与资源

允许原TASK103已列本包文件、相应直接依赖和新task103 fixture内普通必要修正；本轮集中于010现有函数/其指纹、memory读面/降级与标准收据、API映射、合法calc/旧通用tool拒、工作区加载/编辑/恢复及相应测试。若其他核心实现真实残缺，仍在原B1—B8/C1—C3范围完整补足并在计划列实际差异，不能只跑脚本即返。

原001—009、角色/表主权之外范围、worker/launcher/SUP/Job/关门/结算主体、旧证据/归档/正式DocuS/公共库/原始需求/私有配置/依赖锁保护不变。无新的表/角色/持久字段、容器/卷、旧100库或其他服务授权。memory已损坏不可辨的情况失败关闭，不为修legacy可用性伪造“无选择”。

精确复用原三CID，镜像/卷/标签/配额/loopback及一次一PG运行限制仍旧：

- pg1 CID4889202d9a58c622fb7cd2bd3087e5bceb7ad20a049c6550f4bd3588ff66ac11，卷retrolume-task-103-g9-pg1-data，55443，retrolume_task103_g9_main。
- pg2 CIDf96ac8dcb64648c76a2bc70f3f8b75969ada0ea0ea69b5896fe5ecb71affab85，卷retrolume-task-103-g9-pg2-data，55444，retrolume_task103_g9_upgrade。
- pg3 CID4b813f9e4317aef9c613eb140fcb2d40c55a6bd98ee5d79807ea5851975d7f68，卷retrolume-task-103-g9-pg3-data，55445，retrolume_task103_g9_fault及原已登记case库。

旧标签permit仍TASK-103-G9-20261006，配合本卡精确CID与新授权复用，不改标签/原ledger冒新实例。镜像cf134a76…、1CPU/512MiB/pids128/restart=no/无特权host bind等按原完整卡；API/最终dist18103、必要fake18104，当前只读核三实例均Stopped/Pid0。执行前重核，不影响别的资源。取本卡ownedbootstrap Env单项口令仅内存不输出；原本卡app/denied角色密码需重置时先停本卡树，动作在新driver内记账，不能ALTER旧/用户角色。

只允许向前更新本包两个已改函数activity_memory_eligible、purge_learning_memory，以及本轮确需且列明的本包函数，不重跑整个010创建、不清库、不改旧不可变M5收据。更新程序放新证据/fixture，先读实际函数定义/签名/owner/ACL/search_path/安全属性与原实测pre比对，单事务精确CREATE OR REPLACE至最终源语义，核保留所有M1—M7/007/009行身份和权限。发现未知漂移停相关更新，不无条件覆盖或松指纹把旧函数称新。

pg2原受控反向DDL后的真实落点先查；本轮不强制重装旧010或重复CREATE ROLE。如果无需新真实性质只继承其旧行/升级/反向结果。若确需更新须先给同授权内准确方案和前置，不借结构准备删旧样本。

继续沿已实际验证的SessionConfig口径：W20、request_timeout2、grace2、startup5、manager_db5、cleanup5、mutex3、overhead30、single_host_recovery=false；manager_total=50，真实SUP lease=window=20。原卡建议lease60只低层旧种子使用，偏差按实记，不改监督代码硬配60，也不冒原先已满足。新上下文/合成预算/profile类型沿原配置，真实provider/token容量和用户数据仍0。

新driver/ledger写continuation-01独立目录，引用原accounting/runs/hash，不改原计数或permit，不执行旧103入口绕新限额。可复用driver代码但新授权启动必须有本轮账/固定截止/动作前计数；不要用每个小查询另开真实诊断根，按明确主组合顺序连续做，同一个入口不掩盖重复启动的测试根/进程。new测试数据使用本轮合成ID并登记，旧已有效数据不重复变更。

## 验证、证据与审计关系

卡内先完成一份实际剩余矩阵及修正/运行计划，映射V01—V24到已可采事实、最后改变直接影响和真正未做子项，保证正常/关键失败/兼容都具体。不是将所有“部分”机械全跑，也不能只修当前首失败而跳过整条后链。准备及普通修正无需用户再次批准。

按下面一个完整成果接续，允许合并测试方法和根入口：

- 先完成确定源修正与薄fixture，计划中把新入口分为一个核心PG/HTTP/工具/缺口组合、一个最终浏览器组合及必要有据受影响补验，余量仅真实失败或未解风险才用。首真实前只做必要离线控制/选择器/字段/错误码/最终payload一致性核对，保留原方法和断言，不写通用框架。
- 两函数向前应用后核最终DDL/代码指纹、缺M6时v2结果/accepted-context残迹失败关闭，清理新收据canonical TEXT实际输出；原非规范历史收据不改字节，只读确认原key/hash/manifest/效果，不能因新序列化丢掉已提交事实或授新执行权。现有json.loads兼容若足够无需另造迁移或重写旧行。
- 真实复验DEF020：普通continue选记忆分支409、具体code/中文、0新业务/0SUP；未选legacy相同有效路径保持原行为。新mapping不能只是源码字符串断言。
- 完成DEF021有限降级：当结构damaged但不可变M6仍可可靠读取、该活动真实无绑定且无v2残迹时，旧有效活动读/使用兼容按约定保持；已选/残迹/不能可靠分类仍抑制、失败关闭。禁止damaged直接FALSE/selected=True一刀切影响已证legacy，也禁止M6缺表/权限未知直接True。只核真实可辨样本与合理信息不足限制，不加第八表/新回退保证或宣称离线整库损坏可自动辨。
- 合法选记忆教学calc真实工具调用、kind隔离/计数/结果和清理；通用tool拒绝0新增effect，原模型父输入限制不变。使用有效当前关联entity与原result checkpoint，不能沿错误old_aid/new_operation_id字段再盲启动。
- 补真正未做的记忆传播：待核PDF候选与确认/替换后的资格（只新记忆关联，不重跑PDF解析大套）、相同answer新的feedback/无关事件反例、闭包循环/自引用/漏项/越界以及源切换的并发读快照。以实际仓储、合成ID和真实DB并发/锁事实，不mock资格或手写假ready；已成立源替换/纠错/续答/上游正例直接继承。
- 最终UI覆盖V15及配置/选择/撤销/原清单重试/丢响应恢复/迟到清引用/XSS/实际SUP未做部分。先对整条task103-browser现有选择器、预期错误code/文案、分页/详情/owner/title/正文/绑定版本与真实产品逐一核，不只改第二页的一次sleep。每页读完成及表单身份/值确认后再填/点击，使用条件等待不固定等待；同时测试慢真实响应下新输入不会被覆盖或静默改绑、清/保留草稿与真正CAS的语义，不用改变页面操作掩盖产品问题。
- 原browser三FAIL导致分支已停止，本轮是编排对源码与缺证据路径的新完整有限方案授权，不重置原失败或再试原等待方案。若原件加静态核仍不能定根因，先在新预算内最多一次双页GET诊断保存双方DOM/控件值/资格/版本/owner/网络时间线，不做无谓POST；否则直接最终主验证并同样留双页事实。新browser3含这次诊断/主批/最多一次有据不同直接原因的补验；相同未定位原因再次失败立即交回受影响项，不靠额度重复碰运气。
- 浏览器保留已有最终bundle的已完成保存/GET/owner事实，后续代码若不改对应条件可继承；新修复影响最终bundle须构建并绑定src/build/浏览器加载完整hash/bytes，再跑受影响性质。browser真实写通过需新API/PG，不能用GET快照/console0替代。
- DEF019现有明确离线证据作为候选修正可采，原v1、F01及未变父权威按实际条件继承；新G9后端和UI关键性质不能借旧自評升级。原model/费用/工具UNKNOWN留预留不退；正常时间窗口树零/关门后结算规则仍原，不重新跑全Windows停树。

记录每个根/方法/窗口的最终版本与before/after、修正原因和继承条件，新case事实可独立重建。原root19弱numeric_status断言已改但没跑，针对answer_status和实际支持/不推进补受影响例即可；未知/有据冲突/模型allmet负例与引用真实支持分层，不能将旧弱断言签整项。

权限/清理攻击余项仅补未覆盖：物理缺正文、数据库不可读时保墓碑/未确认、伪依赖/跨活动/漏闭包、无当前复活。原正常清理/中途故障/manifest/hash/临时对象/普通app最小权限已真成立，更新函数影响其相关分支才新验证；未经改变不重复为总批换PASS。新正常清理收据用最终函数实际JSON字节，旧结果原文/坏样本/时间重叠不返额。

所有新实际PG/HTTP/Window/browser都在driver许可内，动作前计数和单调剩额硬限；依赖BLOCKED标下游not_run不强启，skip/exit0不是PASS；关键预检先核源/函数/role/DSN/运行loop与数据前置，合法边界没变就不重复旧31根。元数据inspect仍完整JSON只留白名单，不能输出Env/secret。命令或子进程>60秒用运行会话/yield及及时简短进展，不盲阻塞。

源/测试/fixture/config非秘密字段在每实际批前完整保存as-run，在批后核一致；部分方法绑定旧源有据直接继承，新增修改后的结果按最终字节定位。最终完整pre/diff/post和SQL实际旧/新定义、schema/ACL/角色、source->dist->加载链、全部新旧账指针及资源见证齐全，不把246副本扩大成全部266。

全部资源在独立600秒内精确收尾：只本卡PID/创建时间/命令身份和CID，核app/provider/Chrome/受监督树及18103/18104/55443—55445释放；容器Stopped/Pid0，卷/库/role/数据/旧profile保留。DB函数更新与M3清理不删旧事实/收据，不DROP库/容器/卷，不改或杀其他服务；退出1与未知照实。

稳定完整G9才派原计划TASK104的集中隔离独立审计。现在不先审未稳定实现、不逐模块追加审计；你只签候选及卡内证据，不能关闭共享DEF或宣告G9/STEP/M-1/项目。

## 停止与回传

卡内连续补全剩余工作和普通修正，统一返回；已足够立即停止。范围扩大/新持久模型/监督主权或用户数据操作必需、旧状态不明、真实根因不稳、同根因两次有据修正仍失败或任何本轮限额触顶时停受影响操作，完成不受阻部分并给确切差异/原件/需要改变的最小合同，不更换方法或窗口偷偷加批。

结果先一句稳定候选完成或部分停，以及真实剩余/不满足条件；写本轮实际差异与接口/锁/role/forward SQL/legacy分级/工具/UI变化、V01—V24已有继承与新填缺口逐项、命令/最终字节/失败/预算/收尾/偏差/未知、原history原字节与下一独立审计输入。不能改旧24/三browserFAIL、UNKNOWN已提交或旧弱断言原文。

原结果24351字节在新前缀之外逐字节保留，新证据目录不覆盖旧报告/尸件。保存可读并冻结后回复仅一句结论和可点击绝对结果路径，供用户带回编排。G9、独立审计、DEF最终关闭、全STEP和项目由编排裁定。

## 必要人工与待同步信息

用户只需转本卡并带回原TASK103结果路径，G9-P不用重新批准，也无需新密钥/容器/用户库。只有真关键缺口才给最少具体问题。共享状态/架构/CHG/TASK/R/DEF归主控，不更新公共库/正式DocuS或代派卡；经验只报根因确认且已验证可复用的候选。

## 以下为已结束的原完整合同及历史

# TASK-103 / R-097 — G9学习记忆完整实现、受控验证与收尾

## 目标与交付

你是本卡实现与验证执行者。用户2026-10-06已明确“批准”G9-P；在本卡内连续完成一个完整候选成果：版本化学习记忆、固定新活动选择、教学v2背景及全链失效、两阶段记忆正文精确清理、实际工作区、受影响验证和资源收尾。不接管编排，不自签独立审计或最终验收。

实施语义依 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-102-result.md 的A—D完整合同及 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-102-work-decision.md 的已批准包和固定澄清；本卡给实际写权、资源和验证许可。合同不按七张表、各层或单个失败拆成往返小卡，卡内普通修复一次整合返回。

交付010迁移与最小权限、memory模块、兼容v1的v2接线和公开读/重建守卫、真实记忆工作区、最终字节测试/资源账/完整pre-diff-post和候选结果。结果为 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-103-result.md；新证据/合成数据仅在 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/。

完成标准是102的B1—B8/C1—C3与D1的V01—V24按本卡实际影响交付，全部核心通过有最终版本原件；失败/未运行/条件范围明列，不靠汇总PASS；已有充分且未变证据直接继承。达到标准立即收尾交付，不为耗尽额度增加验证。无法闭合时完成不受阻部分并精确交回。

## 项目、规则与接收安排

项目根 D:/shspic/project_NO3_RetroLume-agent，入口 D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。需求v1.1、架构v0.89、唯一执行动态v2.11，task_model/公共阶段07。

规则锁定V4.0/公共AGENTS CHG-0003。公共AGENTS为 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4/DocuS/AGENTS.MD；适用WORK为同根DocuS/WORK.MD第4/6/8/9章；07为同根task_model/prompts/07_开发执行循环.md，卡结构依task_model/TASK_TEMPLATE.md。七锁定指纹见项目 DocuN/evidence/v4-migration-20260930/rules-snapshot.json。入口和AGENTS必须读，同窗未变已读正文复用，不自动采用新版或其他模式。

本卡为G9-P合成实施及定向验证，父TASK102/R096，关联G8/TASK100/101、STEP013和006/007/008/009/012的实际消费边界、后续017；NFR005、DR001—003、FR003/004/010、SEC001/002、MOD005、FLOW004/007、DATA006、API005。用户批准是包采用及此受控实现基础，不扩大到真实用户库/原件删除、真实provider/付费/部署或无关Must。

接收A+增强执行，沿用实际完成TASK102的业务方案窗口，原窗口已具有完整合同和59项真实依赖。该窗口自报Codex desktop/GPT-6、具体部署型号不可見；不冒称与原100同聊天、不按品牌重审。不能用101独立审计窗口执行；原102确不可续才用新A+并按文件交接。单执行窗口，无子Agent、无并行源码写入。

G9-P批准裁定SHA-256为 ee1afe5e72781f89fed37ebc27b00082e2b8d1933f83bfde571587513bd9b35b；原102结果SHA f3bf109c1398b5cf1a8d112f4ebcc55db6d3c0a1f42dc2f92d7aff67377f22b3。输入和冻结边界见 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/input-snapshot.json。首改前逐项核必要源/规则/合同，漂移先辨归属，不覆盖已有改动。

关键代码基线：activities/teaching_repository.py为7d9e28575780e4ac3665f3197b022ff1a3a5c27fc49877067de8f55aef4fe127；learning/teaching_policy.py为efb2ec6a7e4452e0cbfe8365e2d58bea7a8793abe37892f082827dc829bbd303；009为11b1c2bc8cb2482a4fa509b897c3afb8f3f5f7be3eb4e8e4aab559706944c1a3。其他实际目标hash/pre副本依新输入保存。

本TASK103/R097此前无实现/运行尝试，新投入0、调度待转交，未实际发送/接收/启动。独立许可 TASK-103-G9-20261006：主动28800秒，离线累计1800秒，真实准备/PG/HTTP/Windows/浏览器累计7200秒，独立清理预留900秒。元数据/控制辅助≤600秒计入主动；主动从首读固定单调基点/不可后移截止，包含阅读、编码、准备、失败修正、封装回传。等待也不得借新窗重置；未知开销标未知/保守不填0。

次数上限：离线测试6批（每批≤180秒）、frontend build3次（各≤300秒）；真实根入口24次（每次≤900秒），新容器create3/新卷create3、容器start24次、监听应用/测试provider进程start合计12次、SUP业务launch尝试64次（每会话管理预算≤120秒）、browser/driver启动各3次。所有限额动作前计数，首次失败/BLOCKED/超时也占额；各子项共享总真实时间，不能把分项上限相加另生预算。

原102主动3122/10800墙钟保守、元数据300/600及未知/检索错误、运行0已结束；100修复04的1/3批、1.6463436离线、1779.265主动和101 review03的2002.341/180保守元数据以及更早FAIL/漏5.940/未知全部保留，不借任何名义余额。本卡新预算不追认旧偏差。

## 背景与最小充分上下文

G8批准有限合同已验收关闭，F01/DEF008闭合；F02—F09/E02/E01、DEF005及原G3/G4/D3/G5/G6/G7未变事实继承，不从零重审/重跑。项目完整Must、真实provider、向量、HTML、面试、退出/备份与部署仍有后续门。

本包用户代价已获采用：记忆/源/原观察/上游失效会让已选活动全部派生成果停用，旧选择不会自动取新版；原目标/答/纠错历史保留，新活动明确重选。记忆是低信任背景，不作正确性引用、不升级长期掌握或本活动独立表现、也不授权模型/工具。

先读入口、锁定AGENTS、完整本卡，再读批准102原合同和work-decision；同窗已读且不变无需全文再读。其后按实际写路径读 source-facts/function-facts 的必要函数、010拟议七表与001—009必要前置、G8上下文/adapter/资格/原子提交/读面及前端owner/意图。源码以实际项目为准，原规则和文档不回写公共库。

数据库新七表/角色/函数、前端和v2此前未实施/验证。表名存在不证明约束一致；schema/hash/旧不可变触发器/最小角色必须实际核。已有复合FK目标为001的(source_id,id)和009的(activity_id,record_id)，不需重写旧迁移。

允许只读参考已验bootstrap模式：backend/tests/fixtures/task100/bootstrap/sitecustomize.py、repair_windows.py和实际相关源码；不得运行旧runner/旧bootstrap或借旧角色/库/额度。新fixture只在task103命名空间，不能重造庞大通用运行平台。

## 执行边界与资源

允许产品修改范围如下。首改前保存真实pre/hash，新增文件注明原不存在；路径内必要普通修复可自主完成，其他已有改动保护：

- 新 backend/migrations/010_learning_memory.sql；新 backend/app/memory/{__init__,contracts,repository,service,api,context}.py。
- backend/app/main.py、service_config.py；activities/{__init__,api,repository,service,teaching_repository}.py的本包分支/读面/导出，旧时间/账本/终态主体不顺手改。
- learning/{teaching_contracts,teaching_service,teaching_api,teaching_views,teaching_adapter,teaching_prompt,service}.py。learning/contracts.py仅确有必要的资格兼容类型，不改learning.v1规范正文；默认旧prompt/evidence与teaching_evidence/progress只读。
- capabilities/contracts.py和gateway.py的受信v2联合/绑定/结果规范接入。必要时capabilities/admission.py仅相同受信类型贯通，先在执行计划登记，不增工具权限。transport.py只读，测试替身只替代最底层传输。
- worker/one_call.py只允许v2类型to_wire/from_wire的透明兼容所必需变更；不改协议3/4、launcher、SUP、Job、关闭/恢复见证或任一停止/退款主体。无需变更则保持原字节。
- frontend/src/activities/{MemoryWorkspace.tsx,memoryApi.ts,memoryIntents.ts}新增；ActivityWorkspace.tsx、TeachingWorkspace.tsx、teachingApi.ts、TeachingCitations.tsx及必要实际CSS/新memory-workspace.css；frontend/src/main.tsx仅导航/挂载。LearningResult.tsx仅直接资格显示兼容确需时登记。旧teachingDrafts/Intents格式算法保持，必要导出复用不得改旧语义。
- config/activity.example.json仅新增默认关闭的memory_context无密钥模板与说明，不改私有配置；README仅实际新配置/工作区/删除范围/限制说明；.gitignore仅本卡私配置、合成浏览器profile及凭据路径的精确忽略，不宽泛屏蔽源码/证据。
- backend/tests/的本包专用测试、fixtures/task103/；frontend/tests/task103-前缀脚本。既有测试只做实际兼容所必需的构造适配，业务断言/FK清理/历史原件不删、不弱化。
- DEF019/P2本卡明确允许合并最小局部修复：仅teaching_policy的同单位保留原Decimal、跨单位精确比例/可靠比较或超支持精度unknown，以及相应纯离线边界测试。不改全文肯定文法、参考范围/其他政策/签名，不做通用算术平台，不另开微修卡。原F01正常/unknown及独立实例断言定向回归，不能把极小差额舍入后宣称精确matched。
- DocuN/evidence/TASK-103/、本结果；运行数据/备份目录在该证据workspace/data与workspace/backup两个独立兄弟目录。新test配置只写无密钥副本；所有原件和行保留，正文删除仅新记忆M3的获准合成目标。

禁止001—009文件、原资料/PDF/storage/retrieval主体、监督/关闭/结算/费用模型主权、依赖锁/安装、正式DocuS/根入口/公共库、旧证据/归档/其他卡、私有activity.local.json、旧container/volume/DB/roles、任何用户库或实际个人资料修改。不能引新表/服务/持久字段、关闭009触发器、授app普通DELETE或改造旧proto为新平台。

G9核心契约须落实而非只交准备：M1—M7与B1全部约束/角色；来源→记忆头→全相关活动→操作/教学对象→M5/版本/正文的同连接锁顺序；固定CAS/选择/同键受限回放；单SQL资格投影与全部旁路抑制；v2从持久recipe重建而不复制记忆正文；逻辑撤销与唯一函数精确清M3、失败回滚/不复活；实际HTTP/工作区、配置、草稿owner及恢复。

MemoryPage只返元数据/有资格短标题，不携正文/完整依赖，不先传全正文到Python再删；合法50项/Unicode时真实wire≤65536。完整正文/依赖走受资格控制的有限详情。保留旧v1精确序列化，无选择仍旧路径；010不就绪但有残迹/v2结果时不能把M6缺失当legacy True。选记忆活动普通G7/continue/通用tool不能绕过；合法教学calc仍原工具账。

memory失效的UNKNOWN不退模型/费用/工具未知预留，不重发；时间窗口在真实树零/关门/合法凭证下的原结算规则保持，不把“未知输出”混成修改D3时间退款政策。取消/恢复/关门/settle不消费正文，不追加记忆锁。不得因无效记忆堵死UNKNOWN诊断或旧终态确认。

真实资源仅以下新合成实例，按需创建，不使用旧100容器/卷。缓存镜像已核为sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f（本机tag为pgvector/pgvector:0.8.6-pg17-bookworm）；按ID使用、pull=never，不安装扩展或宣称项目向量已接。原设计PG16文档不是本机版本证明，启动后核真实版本/UTF8/核心hash：

- pg1：容器retrolume-task-103-g9-pg1，卷retrolume-task-103-g9-pg1-data，127.0.0.1:55443→5432；主库retrolume_task103_g9_main，负责正常PG/HTTP/UI/真实监督链。
- pg2：容器retrolume-task-103-g9-pg2，卷同名-data，127.0.0.1:55444；库retrolume_task103_g9_upgrade，非空旧G7/G8数据升级、旧行不变、空新对象精确反向DDL等。
- pg3：容器retrolume-task-103-g9-pg3，卷同名-data，127.0.0.1:55445；retrolume_task103_g9_fault及至多12个retrolume_task103_g9_case_前缀数据库，坏基线/权限残迹/清理故障和攻击反例。角色在独立cluster内隔离，避免010固定cluster角色跨库重复冲突。多个坏样本若同cluster造成残迹，应先合理排序/分事务/明确隔离，不修改产品为宽松复用不等价角色。
- 每个容器1CPU、512MiB、pids128，restart=no、非privileged、无host bind/devices/cap-add/host network；唯一PGDATA命名卷挂/var/lib/postgresql/data。标签retrolume.task=TASK-103、retrolume.permit=TASK-103-G9-20261006、retrolume.synthetic=true，卷同归属。一次最多一个本卡PG容器运行，切换先停验前者；新创建后记录不可变完整CID并此后用ID核，不靠名字判断归属。
- API/静态最终dist只监听127.0.0.1:18103；如确需最底层HTTP fake provider仅127.0.0.1:18104，无外网。优先已验低层传输替身且实际profile/PG/准入/mark/record/Job均真实；不能mock这些权威函数或让fake直接写结果。端口冲突不杀/迁别人的服务，不自动另找端口或扩大资源。

资源核对的保存时点显示新三名/卷无冲突、上述五端口空闲、镜像/venv/node_modules/playwright和Chromium缓存现存；每次首次实际用再核，不将旧时点当当前。读取docker完整JSON后只抽白名单，无HostConfig.Mounts格式化模板、无Env/secret输出。缓存缺失不pull/安装；先继续不受阻离线工作，真实部分交精确阻塞。

三个专用NOLOGIN角色沿102定义，在新cluster中创建；bootstrap admin仅本卡新容器，普通登录retrolume_task103_app与负例retrolume_task103_denied等仅本卡新role，不能用admin证明app最小权限。权限授予/撤销只新合成目标；不ALTER旧角色。合成故障样本可在pg3以新admin按计划制造坏基线或本包清理异常，必须有pre/rollback/恢复证明，不改正式迁移或正常路径来迎合断言。

清理测试的DELETE仅M3精确ID/version/hash清单和获准新函数；禁止删除旧事实/原件或用泛DELETE/TRUNCATE扫库清夹具。DROP仅V20获准空新010对象的准确反向DDL，须事先列清单/证明无新数据及外部依赖，不DROP CASCADE/旧表/数据库/卷/容器；已产生数据只保留和向前修复。所有坏样本、合成数据、角色、容器和卷最终保留停止。

凭据用secrets随机值，只在内存/stdin/本卡子进程环境；Docker初始化用环境按名称传值，不在argv、日志、报告、配置文件/原始inspect或对话中出现。只在核定标签/CID/镜像后可从本卡新容器Env单项在内存取回本卡bootstrap口令，严禁输出或读旧/其他容器Env。确需重置本卡新app/denied密码，先证明本卡服务/worker已停，动作计入入口及账，不能重置旧role。所有HAR/trace/异常/命令记录脱敏auth/session/DSN；不查pg_authid或dump全cluster密码。

合成memory_context固定建议：selected_items4、max_memory_bytes4096、max_memory_chars2048；model_context_tokens32768、max_input_tokens_estimate24576、protocol_reserve_tokens1024、reserved_output_tokens2048、safety_tokens2048、estimate_policy=utf8_bytes.v1。model_identity绑定唯一受控fake provider/model，以实际类型在执行计划冻结；这只是合成容量，不打开真实provider或宣称真实token上界。旧无选择配置缺段保持旧行为；选用缺/非法配置在accept前拒，不能静默忽略背景。

其他合成额度沿既有合法字段在计划冻结：每活动运行额度240秒、单窗请求W20秒、lease60秒、请求超时2秒、单会话管理上限120秒、窗口宽限2秒；实际配置的准备/报告/settle余量按已有合法类型显式配置并通读约束，不造新worker配置文件或无限默认。每活动模型次数≤24、费用合成封顶≤1.00、工具≤4，价格/metrics按现有类型明确合成值且有界，零真实扣费；不得把估计价格或fake用量当供应商测量。

生产规则不因合成fixture放宽：DATA_DIR/BACKUP_DIR为上述独立存在目录，ACTIVITY_CONFIG指本卡无密钥配置，所有DSN只指新CID端口/前缀库。Windows asyncio/psycopg使用实际backend/app/runtime.py的psycopg_compatible_loop_factory，避免已知Proactor错误；TestClient/IsolatedAsyncio也按同一正确口径，不用旧错误诊断脚本。不要import/create_app默认读用户配置。应用/助手后台Start-Process用Hidden，只终止本卡PID/创建时间/命令身份匹配的树，不能taskkill所有python/node或关系统服务。

## 验证、证据与审计关系

先完成足够实现与薄fixture，保存一次实际执行计划：拟改文件/旧字节保护、V01—V24逐性质到实际方法、合成库/role/数据ID、场景顺序、真实入口/进程/会话计算、计时/脱敏/收尾和预期FAIL/BLOCKED分级。这是卡内准备，不单独回传或要求新确认。禁止停在“已写runner等待运行”，已有资源前提满足就推进实现及获准真实验证。

driver在tests/fixtures/task103中保持薄而具体，负责账/固定单调截止/子进程限时/本卡资源识别/聚合/收尾，不建平台或复制故障旧runner。每个真实PG/HTTP/Windows/浏览器根准备或测试启动都是一个真实入口，包括仅预检失败；同服务器内具体SQL/HTTP请求不是新根入口但逐项记效果；重新运行测试根命令或普通复验必须新增入口，不能在一个入口里隐匿无限重启。小型readonly Docker/端口/文件检查逐动作记但不虚增业务测试成功。

首次真实前用纯离线方式验证本driver的计数先于动作、None/bool/NaN/负数/未知预算失败关闭、固定截止不可后移、依赖BLOCKED不启动下游、失败结果不因“exit0”掩盖、精确资源/Env脱敏/自己树识别和cleanup路径。不mock SQL或仓储来证明事务。完成必要控制检查后直接一次集中真实推进，无额外前置独立审计卡；未来权限/清理证明先在合成环境核，再接实际动作。

真实子命令≤当前入口900秒与剩余分项/总额的最小值，HTTP/PG内部timeout仍短且有界；所有自有活动启动前拒无预算。driver外壳不得同步等超过60秒不给进度：工具以运行session/yield返回，≤60秒有意义说明，deadline/cleanup不靠聊天sleep。达到已授权限额、同根因两次有据修正仍失败或关键超范围即停相关部分，保留结果不暗加第三次同根因修正/新入口。正常全部通过即停止，不用剩余quota反复全跑。

将24性质合并进实际测试与少量组合，不机械一例一启动：

- 离线：DTO/canonical、v1原字节/v2 recipe重建/请求核对、限制与配置、来源/事件投影及前端身份/列表大小的有效边界；合并DEF019的同单位1与1+10^-65、跨单位60m/min正确及超过支持精度明确unknown/冲突的真实函数例，原F01负例与双正确保留。不要镜像每行实现或做SQL字符串断言。
- 主PG：M1—M7、真实同键/不同键/CAS/无效应收据、复合FK/数量/hash/闭包/失效/合法旧历史和body抑制、实际SQL数/并发快照、原事实/预算不变；最小普通login角色及受控definer清理正反例，不能以superuser全过冒app权限通过。源替换/PDF/观察后继/上游/选择多跳均用真实仓储及持久事实。
- pg2/pg3：非空旧基线010升级旧行逐字段不变、坏前置/残迹/缺核心函数/权限/约束等按实际影响失败全回滚；精确清理中途失败/M3集合或hash不符/临时同名对象/未授权执行/旧007及009未碰；空新对象精确反向DDL。使用真实SQL和不同角色，不mock事务，不DROP数据夹具。
- 固定镜像已具备的核心函数或实际不成立的版本条件，不为造负例删pg_catalog、换镜像或伪造环境。该项用真实能力查询与失败关闭源码分级说明，未实际运行的分支明列，不将静态说明称实测；其他可制造的新合成坏基线仍真实覆盖。
- HTTP：实际local_session/Origin/严格UTF8/递归重复键/新code映射、保存/修订/撤销/清理/收据核对/选择原子创建、失效workspace/record/history/command/007/list_operations/seed/citation全读面抑制与用户原答历史；新列表合法50项/多字节真实≤65536。TestClient可作定向API证据，完整浏览器/监督链必须实际新服务器/PG，不假GET快照替写入。
- Windows：受控fake最低传输，真实launcher/SUP/worker/Job、普通PG、v2 profile/消息与原子保存；集中正常带记忆plan/exercise/evaluate/恢复以及accept→launch、admit→mark、mark→result失效几个具有辨别力的窗。实际观察下一资格/0新写或UNKNOWN/预留/树零/关门/结算，计launch64上限。旧D3停树/退款主体未改就继承，不全重做停树矩阵；不能patch uuid4/Job身份/单调钟/资格/record函数、绕关门或代结算。
- 浏览器：最终bundle真实新API/PG，记忆保存与性质、固定选用、修订/CAS/撤销两阶段及原清单重试、失效清正文、刷新只GET/响应丢失保原键、owner两标签与迟到切换不串、合法渲染/XSS不执行、无配置门。场景内所有写/模型/清理调用计数，含20/50列表与有限详情；不只看截图/console0。发生产品修复后构建并只补受影响最终例，不能用修前绿证据签最终UI。

V23只核在线重开、墓碑缺失/结构残迹失败关闭与未来备份恢复前置，不实现整备份器或声称任意离线整库回滚可检测。V22引用位置与支持分别核少量冻结合成原文/记忆自报/有限观察正反例，故意模型全met为负屏障，fake不是供应商质量证明。原G8场景按同模块/函数/条件未变继承清单列明，有实际变化只补直接影响，不默认旧全29PG/4HTTP/所有Windows/76离线全跑。

每个阶段启动前冻结实际被测源码/测试/fixture/config非秘密字段完整副本与SHA，运行后核一致；修正只能由明确失败/缺口支撑，保留pre/diff/post、旧stdout/stderr/退出与账，然后受影响新版本复检。最终规范统一diff及文件清单包括未改保护对象，不将运行清单未纳入的文件误写成删除。显示bundle保存最终src→build→浏览器加载hash链；构建后的源码再改则需更新/限定证据。

未来真实PG tests专用RETROLUME_TASK103_DATABASE_URL与管理/负例DSN由driver安全内存注入；缺失必须明确skip或受控BLOCKED，不回退用户DSN。真实段skip/not_run/blocked非PASS，聚合区分错误/expected负例/已执行事实/有限例成立/整批失败；echo exit0或bool字符串不能代结果。每例合成ID清单、行数/版本/hash/预算、实际操作序、预期与实际、命令/cwd/工具身份/时间/退出/局限齐全。日志不包含完整聊天/推理给审计。

所有阶段结束及失败均在独立900秒内收尾：停并核本卡应用/测试provider/Chrome与受监督树，关闭本卡端口；精确CID停止Running=false/Pid0，卷/库/角色/数据保留；不要删除容器/卷/临时数据/原件，也不影响其它进程。资源计数真实更新、未确认直说，不把关门/kill未知称已退款或确认停止。正常退出统计包括封装尾段，旧许可余额不恢复。

高风险完整G9稳定返回后由编排另派一张集中隔离增强审计，主要验权限/来源/删除/失效/晚到/恢复和执行控制及最终字节。当前不先发依赖卡，不自签，没有每模块独立补审。最终候选等待审计期间源码/证据冻结；即使本卡全绿也不签G9/STEP013/M-1/项目。

## 停止与回传

卡内持续完成实现、相关测试、普通修复和资源收尾，中间常规步骤不分卡回传。全部目标达成即保存停止；超出七表/批准权限/旧协议、需要改001—009或监督/退款主权、新服务/依赖/真实provider/用户库、v1兼容不能保持、资源归属不明/ledger失效、同根因两次有据修正仍失败或任何上限到达时，停止受影响操作、完成不受阻部分、带具体最小分歧交回。不得换模型/窗/方式清零、直接绕driver跑真实诊断或借旧预算。

结果首句必须限定完成/候选/部分停止及未验证状态；随后实际文件pre/post/hash/影响与接口/角色/锁序/清理边界、V01—V24逐性质真实最终证据/继承、DEF019修复及范围、原命令/计时/失败与修正、预算/资源收尾、偏差/未知/剩余与待同步文档、建议独立审计输入。测试方法/子测试/业务窗/入口分开计，真实内容oracle/副作用与版本，不只填总PASS。

结果保存到 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-103-result.md，证据实际可读且hash绑定后回复只给一句结论和可点击绝对结果路径供用户带回。后续未验收同边界续作沿本结果置顶保留全部历史/旧失败，不填写编排最终验收，不宣告G9/STEP/M-1/项目或真实provider通过。

## 必要人工与待同步信息

G9-P采用已批准，不再请求重复批准或逐表确认。用户只需转本完整卡并带回结果路径；当前无密钥/用户库/启动服务等必要人工前置。真正关键资源/范围阻塞才给最少明确步骤与非敏感回传，不将普通代码/夹具决策交用户。

主控串行维护DocuS架构/唯一状态/CHG、TASK/R/DEF、最终裁定；执行者不写这些文件、不自行占号或派卡。只报告已解决/根因确认/已验证且可复用的经验候选，不写公共提示词库/用户记忆或共享经验库。
