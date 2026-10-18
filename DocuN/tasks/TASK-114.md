# TASK-114 / R-108 — 续作03 两项余缺修复与定向验证收口

## 目标与交付

你继续原TASK114工程，不接管独立审计或编排。本卡一次完成DEF035/F02的loading pin截止贯通、DEF036/F03的删除策略/计划及导出范围输入生命周期修复，连同必要定向验证、准确收尾、最终字节和报告一起交回，不按普通实现步骤拆卡或逐项请示。

主控已核原115 review-01并关闭DEF034/F01取消覆盖成功、DEF037/F04正文依赖投影的原问题。它们的实现、正常PG/HTTP和停止证据保留，不再重做四项全审。DEF035/036仍为P1，有限STEP017未关闭。本卡修后稳定候选由原115窗口仅对这两项和真实传播增量复核，最终裁定仍属主控。

结果置顶保存 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-114-result.md，当前69598字节旧报告全文原字节作为后缀保留。新证据唯一根 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-03/。交付最终差异/pre/post、真实调用/参数检查、最终bundle的精确选择竞态与正例、失败账、实际资源/时间、继承依据和剩余限制，不自签独审、STEP017、M-1或项目完成。

本卡不启动PG、不创建或恢复容器、不跑真实恢复主链；采用原审计明确允许的受控连接参数检查，和既有真实Chromium在最终dist上的route交互。层次须实标，不能把受控连接写真实PG、把route写真实后端切换。原PG deadline只证读取阶段超时，纠正适用性后直接复用有效部分，不为维持过强表述另开PG。

## 项目、规则与接收

根 D:/shspic/project_NO3_RetroLume-agent，入口 D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。task_model，V4.0/公共AGENTS CHG-0003，阶段07；需求v1.2、架构v1.30、执行动态v2.54。公共根 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，读取DocuS/AGENTS.MD及WORK适用2/6/8章，同窗同字节部分直接复用，锁定七指纹在项目DocuN/evidence/v4-migration-20260930/rules-snapshot.json，不自动采用后来版本。

TASK114/R108/STEP017-P1，父TASK113/R107，关联TASK115/R109 review-01、MOD008/FLOW007/API005、DR001—003、NFR002/003/005、SEC001/002、DEF035/036。原113完整采用包与永久只读边界不改；原始需求用户维护只读。

接收A+增强执行Agent，继续原TASK114工程窗口，上一轮续作02实际Codex desktop/GPT-6，当前如实登记，不把档位当官方型号。路由原因是跨受信截止和用户删除策略的高风险修复，范围已明，不需重新设计整套协议。原115独立窗口不实施本卡；人工转卡，当前未实际派发/接收；不派子Agent或并行修改。

用户已采用STEP017-P1并持续要求完成，原合并修复及独审交回的两处具体缺口均在已授权范围。主控给本轮前向受限许可，不重批方案、不换TASK/R、不清旧失败和投入。原结束的C02根、日历/进程/资料/selector不因本卡自动复活。

## 断点和最小充分输入

1. 本卡、根规则和 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-114-work-decision.md 的本轮许可。原公共规则未变复用，关键源不可读按同一锁定版本规则处理，不凭记忆冒称已加载。
2. 独立增量结论 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-115-result.md，当前61253字节，SHA256 3d6a4ce4e30284f6799f61462e84c419a9fdd7226ef1f1e73dc468815b04a0f2。只需本轮F02/F03、最终版继承和最小交回段，不重读自己的全部历史。具体发现原件 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/review-01/findings.json、deadline-original-progress.json、as-run-identity-and-method-deltas.json、delivery.json。首工具mono缺同步采样已保守扣时，不追认精确计时。
3. 原采用合同 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-113/design/revision-01/current-contract.md，81813字节，8a56ebf3c1715895e3ee7a0dcf1f621b591335400e9898aa00df8cb2b7a61aaa。同窗未变正文复用，只补两项涉及的截止、删除策略、明确确认及只读界面条款，不继承被审计否定的运行层表述。
4. 本轮输入与许可 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/orchestration-repair-c03-20261014/input-manifest.json、continuation-permit.json。上轮有效当前235文件和两个已移除旧bundle项按实际核对，原final/source/pre不改。冻结基址 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-02/final/，没有pre的新增文件不伪造旧字节。
5. 实读 backend/app/data_exit/reference.py 的LoadingReferencePin、restore.py的_load和唯一调用，operations.py受限connection/BoundedConnection仅作复用依赖；frontend/src/data/DataWorkspace.tsx的upload/verify/activate/refresh、scope-preview及各输入onChange，context.tsx/dataApi.ts及fileHash直接调用。必要原件和夹具在backend/tests/test_data_exit_c02.py、backend/tests/fixtures/task114、frontend/tests/task114-c02-context.mjs。读取实际文件，不把建议当现成补丁。
6. 原工程唯一计数账 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/control/receipt.json、events.jsonl，C02 final/delivery.json、closure.json。旧消费者全stopped；原115本轮新增业务0，沿用已保存准确metadata，不凭此宣称今天重新实查。旧source frozen、target07 generation1、新C02 target01只读及failed target02全部保留，不启用、不回退、不借角色。

改前关键SHA256如下，完整输入清单为准。

- backend/app/data_exit/reference.py 为 b64abf231560f431e0b935d14cd0a09143767b5b5045059d83da865a4ded564c。
- backend/app/data_exit/restore.py 为 5107b7b8c946ffb875f21e90e3b49f81a45970fdb0793b9211fc4b8a2fa6893a。
- frontend/src/data/DataWorkspace.tsx 为 0faf25daffe885e2046ceb81ef15aafc576b047538073a52f0c2f276f8fe57f2。
- operations.py 为 b57348ca484717a2c147087c46c6edc4702983a900f65ce5475e00346f64a876，默认冻结。
- context.tsx 为 fdf86fb80f394fb59becae1a86deabf4bd15179d4eb4f7fcc3635a17d4e908f9，dataApi.ts为d6865057747dab1604c9d22f3a623d95f8b7e3af577e17ded31cd305c360e679，非必要不改。

对象漂移先查归属，不覆盖用户或他窗成果。存在的旧报告/FAIL/as-run原件不重采、不清洗、不改写。

## 实现成果A — loading pin贯通同一Operation

已确认根因在restore._load为每个原件构造LoadingReferencePin。构造器直接psycopg.connect固定connect_timeout=3并做data_loading_allowed/data_state查询，没有接收Operation，也没有该job剩余statement/lock限制。外层进入前check和返回后check不能证明该独立调用消费同一D。

将恢复原件的loading检查显式绑定原Operation，复用现有受限连接/check和既有身份核对，使连接、查询、结果消费以及后续pin检查均按该job唯一D判断，不另设started或deadline，不用0超时表示无限。对不足libpq整数秒下限的剩余量应失败关闭，不在尚未确认loading身份时开始store.put/发布。查询返回后已过D不能授新原件执行资格。

保持factory/target/loader身份、allocated/running、精确root/lease/prepared校验；不扩大loader角色、不改变001—013或source普通ReferencePin权限。取消/成功短CAS、撤权/准确停止、completion确认和UNKNOWN原纪律不退化。检查唯一产品调用的传参，以及其它真实调用是否存在，不以仅改构造器定义冒传播完成。

本卡优先复用Operation.connection，operations.py本体冻结；若发现必须修改该公共机制才能正确实现，先完成不受阻前端与测试准备，交回具体阻碍及最小差异，不顺手扩写原核心时间协议。

## 实现成果B — 删除策略、计划与范围输入绑定

原全局capabilities反序、dataset/instance/generation保护已正确，保持机制不变。此次真正漏点是upload捕获旧policy，等待fileHash/上传/restore-plan期间更改策略仅清空plan，旧闭包仍能回填；verify不检查plan.deletion_policy是否等于当前选择。scope-preview在mode/source/activity变化后也可被旧响应回填并启用导出。

为上传/文件/策略/计划建立清晰的输入revision或在相关处理期间明确禁止变更，绑定每个await后的提交。输入或上下文失效时，旧结果不得重填、启用或携旧plan_id/hash执行verify/activate。允许HTTP上传事实和原操作键按合同保留核对，但过期结果不重新获得当前计划资格；不自动重新POST、重上传或创建恢复任务。

范围核对同样绑定mode、选择的source_ids/activity_ids及当前数据身份。选择更改立即撤销旧scopePreview；旧请求返回不能重填。点击导出前再次核输入绑定与closure_sha，后端expected_closure_sha256防线不删。处理材料与活动两类选择、mode切换、刷新读回计划、同上下文更换文件、卸载或切换上下文后的晚到，使用同一必要机制，不分别堆积通用框架。

verify/activate呈现与动作校验必须一致，维持snapshot_only明确确认和unknown删除确认的原要求，不能显示respect_current而执行旧snapshot_only计划。不能仅用当前busy或隐藏按钮而忽略异步结果、刷新回填和动作本身的输入校验。控件暂时禁用是一种可选实现，不要求强制让用户能在处理中改变选择；如采用禁变，settled后改变输入仍须使旧计划/预览失效。

## 允许文件与冻结边界

允许改reference.py、restore.py、DataWorkspace.tsx；context.tsx/dataApi.ts仅在直接完成上述输入绑定确有必要时最小改，并在报告解释原因/传播。允许新增backend/tests/test_data_exit_c03.py、backend/tests/fixtures/task114/c03系列夹具、frontend/tests/task114-c03-inputs.mjs。允许既有budget.py/freeze.py为C03许可/目录/累计门做必要夹具适配，或新增薄适配器，不改变历史账或产品安全检查。

允许现有本地依赖构建前端dist、仅替换本次构建自产输出，改前先存精确原件；不额外执行递归清理。允许本轮pre/final/as-run/日志/DOM/截图/合成小文件和准确消费者收尾记录写入continuation-03。唯一control账允许追加真实本轮许可/事件/资源，原锚点、历史段、计数、资源和全部原事件不可删改；旧C02目录与原控制业务Hub/selector全冻结。

禁止改operations.py本体、其它data_exit模块、001—013、schema/codec/ACL/业务模型、原生成/预算/worker/SUP/StopProof/preview核心、依赖锁、用户配置/凭据、README无关段、DocuS/AGENTS/公共库/经验/记忆。不得修审计报告或写主控DEF/CHG。无Git写、安装、镜像pull/build、真实provider/付费/公网、用户库或真实资料操作、系统时间/服务/网络变更。不得读取原密钥或启旧admin/loader/failed对象。

范围内实现细节、定向测试和普通修复自主完成。主要模型/公开接口变更、新依赖、新服务或需要突破冻结核心时停止受影响部分交主控，不自扩方案。新原件只存一份，旧已确认F01/F04不人为重开；实际修改若产生具体回归必须如实报告。

## 验证与证据成果C

先完成两项相关改动及夹具自检，再集中验证。一次普通失败先定界，在本卡范围和额度内作有依据修正与复检，不立即逐步退回用户。只有根因不稳、同因两次有依据修正仍失败、必须变更方案/冻结边界或上限到达才停止。已有历史失败与原停止门保留，不用换label或新文件清账。

### C1 真实产品调用的受控连接检查

新增定向测试调用实际LoadingReferencePin、实际Operation/受限连接路径和_load传播。仅在psycopg原始连接边界用明确替身捕获参数/查询并返回合成身份；不能替换掉被测pin/Operation方法再声称它们有效。记录同一operation对象、started/deadline/clock_domain、实际连接参数、语句前的剩余限制、返回后check与未执行副作用。

覆盖正常身份/原lease约束、传入原Operation对象不重设D、剩余不足1秒或已过D时不调用原始connect、连接/查询返回过D不进入store.put/不授verified，以及不匹配loading身份仍拒绝。用确定时钟或受控连接阶段推进测试时，明确为受控边界，不改系统/DB时钟，不把参数检查称实际PG等待上界。按实际调用关系选最少充分方法，不用测试复述实现。

固定旧原PG两秒样本的证据说明。其journal只有reading到failed、耗时2.047秒，未到设计的2.1秒publication注入点；只能继承实际读取过D拒绝/无发布。文件层capture后截止和最终成功帧/observer方法有效。本轮选择受控连接参数检查闭合新pin传播，不再声称新增真实PG/capture后延迟全链通过。

### C2 最终构建的一次合并浏览器矩阵

使用已安装Playwright/Chromium和本项目最终frontend/dist，沿用c02-browser实际Chromium+全部route接管模式，不启动API/Vite/HTTP服务器或TCP监听，不探PG。不依赖公共提示词库、临时产品实现或旧浏览器profile。所有请求按明确127.0.0.1合成URL由routes处理，非白名单或未处理请求失败关闭，真实公网为0。

至少合并以下精确场景与有效正例。

- 已明确snapshot_only后上传/计划请求挂起，用户改为respect_current，旧snapshot_only回包不能呈现为当前可验证计划或产生restore-jobs；新选择重新明确取得对应plan后，点击一次仅发送该plan_id/hash和原有确认所需字段。
- mode/source/activity选择A的scope-preview挂起，变为B，迟到A不能显示或启用当前导出；B核对返回后才能按B的精确scope/closure_sha显式一次POST。覆盖至少一种材料和一种活动选择，mode切换走相同失效机制。
- 刷新读回旧plan、同上下文更换file/策略、卸载或数据身份改变后的晚到，以实际修复共同机制证明不会绕过。原全局CAP反序6场景已有A，不整套重跑；只补此次改动直接涉及的计划/选择入口。

若采用处理期间禁变方案，先断言相应控件真正disabled，不能强制绕过disabled后拿不曾触发的onChange当产品失败；任务结束再改变选择必须撤销旧绑定。若采用revision方案，在真实可达交互中释放旧响应后观察。不能拿旧GET plan两次refresh方法冒上传中改policy。

夹具Plan必须携真实DTO字段，包含deletion_policy、plan_sha256、package_root_sha256、executor_configured等；回应与本场景实际选择一致。旧/新marker、请求体、接收次序、当前select/按钮/DOM、构建导入hash与准确关闭原件齐存。有效请求应恰一次、自动POST零，错误/未达场景如实FAIL/not_run，不靠删除正确断言制造通过。

先完成typecheck/所需脚本语法检查，再用原package.json现有build命令生成实际bundle。浏览器必须绑定当前最终被测源/脚本/bundle的as-run哈希；若之后又改产品，按受影响方法复检并明示证据有效版本。达成即停，不为把全部历史方法凑最终一版重跑PG或整仓。

### C3 完整差异和保存

改前存当前235文件必要原件/哈希，改后完整记录实际新增/修改/构建移除和精确diff。旧C02已移除输出仍缺失，不构造当前hash。每次方法记UTC/mono、真实argv/exit/耗时、pre/as-run/post与阶段marker、环境/层级/局限；日志保留FAIL。最终方法索引必须实填，不再留空的offline_exact而让主控猜重建。

F01取消准入、F04正文与角色/SQL/Native未变部分凭hash/直接影响分析继承。最终产品对旧PG的适用性单列，明确没有新PG。只证明传参/选择生命周期与route交互，不声称物理PG挂死、驱动强制终止或真实selector切换已经新测。

## 许可、预算与资源

本轮许可 TASK-114-STEP017-C03-20261014，只激活当前两项修复/定向验证，不重置任务累计。唯一control仍为implementation/control；C03目录只是本次证据，不是第二总进度账。接收先实采首工具UTC/mono并核旧冻结/停止事实，在continuation_history完整保留已结束C02与所有旧锚点，再追加C03段及许可，不回放c02_bootstrap或复活已结束根。

本轮活动最多10800秒，含读取、实现、验证、等待、落盘，最后1200用于准确清场/报告。该段占原C02的21600剩余活动额度，原已用9188.720111加本轮最多19988.720111，不新加21600。原C02日历硬截止2026-10-15T08:54:00Z不延；本轮允许启动的日历限为该时点与接收后24小时中较早者。不得事后倒填暂停，普通等待计时；异常计时缺口保守记录，不追认精确首点。

原计数root21/24、PG create9/12、success9/9/start37/37、Windows11/12、API8/11、Browser5/9、build5/6。此次新增根最多2，累计不超过23/24；两个真实根为合并修复定向检查组和route浏览器组，组内有据复检同一活根连续记全部方法/失败，不按每条命令拆根，也不复活已关闭根或把Browser启动藏在组计数外。

本轮新增Browser启动最多2次，累计最多7/9；真实build最多2次，前向累计frontend_build上限由6明确增加1至7，已有5次不清零。第二次build/Browser仅用于有明确修正依据的复检，全过不用完。其它资源累计上限不加，C03新增PG/SQL/create/start/API/Vite/Native/preview/provider/费用/公网全部0。两个根和两个Browser是独立上限，不以子进程/入口换label规避。

离线测试/build仍受原累计7200秒、已用172.317和本轮最多1800秒双门；方法实际用量加回旧账。Browser控制进程和Chrome按原保守口径分别登记准确PID/birth、开始/结束和持有，新真实持有最多600秒，原462.047加最多1062.047，原10800/业务9600总门不扩；最后120秒真实持有用于清场，业务到480秒即收尾。进程用CREATE_NO_WINDOW或隐藏启动，保留profile/截图不删除，关闭只限准确本卡消费者。

Browser启动前复核既有2GiB可用内存门，纯只读预检不扣根/Browser、不循环盲占额度或停用户软件。若内存或现有Chromium能力未满足，完成不受阻修复与离线并给真实外部阻塞，不降门或转去新容器。由于PG新增0，本轮无Docker唤醒/端口解绑/用户密钥前置。

原C01活动9739.953、旧55525.796/净unknown、历史根补账、全部FAIL和115累计审计活动8617.261566/21600、审计root3/API3/Browser2/offline125.610/hold14.874分开保留。G11/25/UNKNOWN/R60/count1/13元/626.566不抹去、不借审计余额、不退旧UNKNOWN预留。旧源和selector/journal/卷/九PG对象全只读冻结，不唤醒、销毁或复用失败目标。

## 停止、回传与必要人工

接收核前置后直接连续实施、定向检查、允许范围内普通修复和复检；不在计划/临时成功处提前结束。达到本卡完整终点即停。原根因路线之外的新高风险/模型接口变化、同因两次有依据修正仍失败、冻结/独立性冲突、产品核心必须越界或资源/工时/日历停止门到达时，保存事实和旧成果，停受影响消费者并准确收尾，再一次交回主控。

结果按一句结论/实际差异、F02/F03各要求和方法映射、最终与as-run绑定、继承/纠正、全部失败与真实累计预算、准确清场、未完成/未验证/风险/偏差、文档建议与下一步组织。旧69598字节报告SHA256 e457d13159c439da8c56814b4f9c860973c0ff5d8622793ab4663584ffe5ad11留本轮pre，追加前缀后原字节后缀一致；不得覆盖115结果或历史FAIL。

确认结果保存完整可读，回复仅一句真实结论和结果绝对路径，供用户带回。必要人工仅转交原工程窗口及带回结果，不重复采用、不要求用户提供密钥或启旧数据库。主控之后安排原115仅两项/影响增量复核，最终DEF/STEP和正式架构/状态/CHG仍由主控维护；本窗口不自签审计或自行派新卡。
