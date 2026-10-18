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

