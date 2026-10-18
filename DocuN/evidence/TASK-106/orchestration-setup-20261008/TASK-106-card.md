# TASK-106 / R-100 — G10文字面试完整实现、接线与受控验证

## 目标与交付

你是本卡实现执行者。用户2026-10-08已对具体G10-P合成实现/定向验证包明确“批准”；在一张卡内连续完成011/领域持久、受信profile与原子正文、公开接口/配置、完整文字面试工作区/本机恢复、相关验证和普通修复、最终封装及资源收尾。

目标是资料/可修正目标→问题→回答→必要追问→有依据反馈→显式继续/结束/历史恢复，活动有可见有限预算，不固定方向/题数。自报/证据/语义建议可辨，正确部分给予对应认可，不编造经历/测量；原学习/教学/记忆/准入/停止/未知预留不被新领域绕过。

交付结果 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-106-result.md，新原件 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-106/。完成标准是105 A—D及本卡明确边界实际实现，V01—V24的新性质/实际影响有最终版本原件、兼容范围有据继承、没有相关确定阻断，许可和资源可独立重建。不能用建议轨迹/fixture输出/模型自评签通过。

普通修复在本卡内完成，完整候选和最终证据统一返回，不按表/接口/页面分别转卡。达到标准即停，不用满额度；你只建议候选状态，不自签G10/独立终审/STEP014/M-1/发布/项目完成。

## 项目、规则与接收安排

根 D:/shspic/project_NO3_RetroLume-agent，入口同根AGENTS.md。task_model、V4.0/公共AGENTS CHG-0003锁定，需求v1.1、架构v0.97、唯一执行动态v2.19、阶段07。公共根 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，读DocuS/AGENTS.MD；WORK第4/6/8/9章、task_model/prompts/07_开发执行循环.md及TASK_TEMPLATE.md同版，七锁定指纹在项目 DocuN/evidence/v4-migration-20260930/rules-snapshot.json。旧窗已读未变正文复用，只补改变，不采用新版。

接收A+增强执行，继续实际完成105、此前103的原业务窗口，使用可用强推理资源处理事务/权限/类型/异步与完整证据，真实客户端/型号如实登记。原窗确不可续才新A+带文件接续，不派子Agent，不使用104独立窗口实现。你独占本包源/测试/dist和本卡新合成资源，当前没有并行业务写者。

父105/R099，G10/STEP014，FR002/004/011/012、NFR001—005、DR001—003、SEC001/002、MOD006/FLOW002/003/005/DATA005/API002；实际受影响006/007/008/009/011边界。105设计和G3—G9有限验收保持，DEF019—023有限关闭/O01—03非阻断观察不重开；45旧真实入口、各FAIL/费用/UNKNOWN和已封闭预算原样。

授权采用的是 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-105-result.md 的完整A—D（77012字节/SHA c1b192aa05cdab6384b9c3114269c7396ec44022685f1ac7d48edcd03f37483d），以及 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-105-work-decision.md 的批准段/普通读界限。原待批准措辞在历史，不是当前状态；新批准证据在106/orchestration-setup-20261008/adoption-received.json。无需重问采用/是否继续，包外实质模型/权限变化仍交具体差异。

## 背景与最小充分上下文

先读本卡/入口/未变规则、105-work-decision最新批准和固定澄清、105完整合同对应实施段。原窗已读105原文复用，不整段重研究设计；源码在动手前定向读实际类型/调用/已有改动。当前308对象及31直接源冻结在本卡baseline-input.json与105/source-baseline.json，原73处函数位置可导航，不假称新功能已存在。

主控普通界限仍是history元数据投影不先取正文、workspace有界当前投影；workspace完整wire≤131072字节，history/record/citation≤65536，超限413/interview_snapshot_limit不静默截断。新读上限不扩大模型/命令/OneCall旧较小容量。资格/正文同语句，分详情读需view/owner/panel绑定。

首先对16新增/11修改/1公开例子的真实签名与类型作一份实施映射；特别核ModelCallRequest可选carrier/AdmissionIntent尾部、007同事务hook、scope同连接helper、L-I来源/记忆/活动→operation→interview head→commands、同键/槽、S1/角色指纹、旧v1 exclude_none字节。不要到真实首根才发现字段/类名/loop/配置参数或FK错配。

既有G3—G9证明只在未改条件继承，源变后重核相应调用影响；新领域/新carrier/新hook/新窗口不能借旧结果冒新动态通过。原job/manager/恢复代码不重写、不重跑整个平台矩阵。正式产品代码/运行不可import DocuN临时实现、公共提示词库或旧实验；测试故障注入只在项目backend/tests/fixtures/task106内，证据目录不作运行库。

## 执行边界与资源

允许新增生产文件按105 C1的16个：backend/migrations/011_text_interview.sql；backend/app/activities/interview_repository.py；backend/app/interview的__init__.py、contracts.py、prompt.py、evidence.py、policy.py、views.py、service.py、api.py；frontend/src/activities的InterviewWorkspace.tsx、InterviewCitations.tsx、interviewApi.ts、interviewIntents.ts、interviewDrafts.ts、interview-workspace.css。全部相对路径以实际根拼绝对路径。

允许修改11个生产文件的指定新域接线：backend/app/activities/repository.py、service.py、api.py、teaching_repository.py；backend/app/learning/service.py；backend/app/capabilities/contracts.py、gateway.py；backend/app/service_config.py、main.py；frontend/src/activities/ActivityWorkspace.tsx、frontend/src/main.tsx。另改config/activity.example.json为显式禁用占位。必要中性DTO出口可最小追加activities/__init__.py，先留依据/差异，不借此导入服务形成循环。

允许新增backend/tests/test_interview_contracts.py、test_interview_postgres.py、test_interview_http.py、本卡实际所需fixtures/task106/与frontend/tests/task106-interview.mjs；旧受影响测试仅必要签名/类型/None/夹具适配，原业务断言/定向清理/已失败原件保持，不改预期来贴错误行为。具体旧改动留pre/diff/post及原因，非受影响测试不写。

最多三次现有frontend build正常替换本卡已冻结dist生成物，先完整保存旧dist字节/hash，保留被替换资产pre，不手工递归清目录或改版权。新增正式素材/依赖不得靠DocuN挂载，不安装/升级/修改锁文件/引入新服务或框架。

保护001—010迁移、全部backend/app/worker与原生Job/launcher/session/协议3/关门/停止/退款主体、memory模块、旧teaching service/policy/views/api及学习contracts/prompt/Normalizer、资料/PDF/原件/local_session/deploy/runtime/用户配置、锁/旧证据/归档/其他结果/Git/正式DocuS/公共库/原始需求。可改白名单源中的新domain guard及旧公共helper的同连接提取，不重写旧计数/来源/UNKNOWN规则；必需越界就报告准确影响，不能默扩。

数据库与权限实现遵循105 B/C，三表/五函数/两个NOLOGIN领域角色，无旧数据回填。模型record最终字段一次INSERT，不先占位再UPDATE不可变事实；必要deferred FK只同事务末完整核，不沿旧100曾犯的“禁一切UPDATE但自己还回填”错配。原read/write/code不存在011而有int10m残迹必须失败关闭，不用table exists/宽TRUE绕S1。

真实模型、用户资料/简历/DSN/密钥/账号、外网调用、费用、安装、Git写0。只新合成cluster及虚构样本，替身只在最底层transport回原始OpenAI兼容响应和合成usage，不能mock ledger/SQL/资格/结果提交/停止/Job/profile授权或伪成功UI。任何资料内指令不授工具权，interview allowed_tools为空。

新许可 TASK-106-G10-20261008，主动28800秒，离线检查与build合计1800、真实准备/PG/HTTP/Windows/browser7200、独立收尾900、辅助metadata1800。真实runner入口16、精确container start18、API/fake监听进程启动合计8、native SUP尝试48、最底合成transport发送48、browser/driver各4、离线6批每批≤180、build3每次≤300；Python改动compile内存不写pyc初批1及有明确修正依据最多1复检，计offline。每真实根≤900且受剩额；SUP仍原manager50/lease20，均计真实。SUP尝试与transport发送分别计数，未发送不退款或返SUP次数。新container/volume各最多3。

上述是总上限而非目标；预计合并为核心PG/HTTP/协议/权限/异常窗、最终browser两主组及必要有据复验。一次root固定目标，可含批内方法，不把每小查询开新根；不能通过起driver/子runner隐匿新的独立根。失败/BLOCKED/未知动作前计数，循环日期/模型/窗口不返额，same-root因果计数不清零。root启动前预留本卡remaining cleanup和各类余量，任何分类触顶停止对应运行，不借旧余额。

新资源精确配置如下，执行前重核；主控当前只读核缓存镜像可用、以下名称/卷/端口无冲突，没有创建或启动。

- pg1 retrolume-task-106-g10-pg1，卷同名-data，127.0.0.1:55446，数据库retrolume_task106_main，正常实施/HTTP。
- pg2 retrolume-task-106-g10-pg2，卷同名-data，127.0.0.1:55447，数据库retrolume_task106_upgrade，001—010真实旧行基线后非空011升级。
- pg3 retrolume-task-106-g10-pg3，卷同名-data，127.0.0.1:55448，数据库retrolume_task106_fault，缺/坏schema和原子/资格故障。

镜像固定sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f，缓存tag原pgvector0.8.6-pg17-bookworm；pull=never，1CPU/512MiB/pids128/restart=no，唯一声明命名卷，无host bind/额外cap/privileged/docker socket/外网公开绑定。labels retrolume.task=TASK-106、retrolume.permit=TASK-106-G10-20261008、retrolume.synthetic=true。每次最多一个本卡PG容器运行，创建后立刻冻结完整CID/卷/镜像/标签/配额/绑定，后续只精确CID操作，不凭名字猜归属。

每cluster bootstrap admin为本卡新隔离准备，普通runtime retrolume_task106_app/拒绝样本retrolume_task106_denied按新cluster创建，NO SUPERUSER/BYPASSRLS/CREATE DB/ROLE/owner或purger成员。新增interview_owner/app按011；普通runtime只已有必要旧表/资格函数能力及新最小app成员，ACL/属性逐项留证。实际应用用普通runtime，admin仅合成准备/明确故障，不拿admin结果证明用户权限。

端口API/最终dist18106，必要最低fake provider18107，均loopback。所有data/backup/profile/合成配置本卡独立，RETROLUME_DATA_DIR/BACKUP_DIR/DATABASE_URL/ACTIVITY_CONFIG明确注入，绝不回退用户DSN/私有activity.local.json。bootstrap/普通/denied随机口令只RAM/stdin/子进程Env；只核自己新CID身份后可取其Env单项恢复bootstrap，不打印完整Env、入argv/日志/报告/截图或Git。

旧103/100/088等CID/库/卷/角色/数据/profile与旧runner全部只读，不启不删不恢复许可。新库先001—010顺序空活动应用，004不能非空先填样本；正常/非空升级/坏克隆隔离。V18可在本卡fault环境用回滚事务或新坏基线测试缺/改定义，留before/after/恢复证据；不得DROP表/角色/库/volume造故障、DELETE旧事实、关旧trigger或系统时钟。实际逆迁移/物理删除未授权，C2退路只给方案/静态适用性，不为它另闸实施。

无并行业务写入；共享状态与编号归编排。本卡ROOT/EVIDENCE/permit路径/日期/命名空间必须实际验证，permit日期是本授权标识不是午夜重置口令；不import旧控制器激活已结束许可，也不照搬R03的SUP禁止注入到本卡真实组合。

## 验证、证据与审计关系

首真实前一次核全控制与类型前置：16/11源/字段/类名/函数位置/SQL复合FK/不可变/矩阵数据、真实psycopg兼容Selector loop、OneCall纯构造与完整wire大小、配置/profile层、普通role/owned DSN、真实session bootstrap与业务Origin、Node selector/默认分页/cursor，以及实际JSON inspect。

不得用HostConfig.Binds非空判host bind（命名卷也可在其中），按实际Mounts匹配；inspect完整JSON取白名单而非旧14字段HostConfig.Mounts模板。参数化SQL中的LIKE百分号遵循psycopg实际格式规则；session入口native bootstrap不加其不支持Origin，业务保持真实session/Origin；selector按当前DOM/API响应和ID确认，不凭同名标题/固定第几行或section.collection。失败保存真实status/脱敏body/stack/DOM/ledger，不能只记录non200或空AssertionError。

实施前冻结实际V01—V24→用例/层/样本/调用数/预期和预算映射。允许方法联合覆盖，不为24编号机械24runner或删除实际影响。代表性样本至少两方向，完整原文/角色/expected判断/位置与hash在本卡落盘；不能写死产品学科。

T方向使用明确合成的“单独读余额、计算后写回”算法与小事务轨迹，初值100，加20减10，串行结果110，两个先读100的写回可导致覆盖。只核给定算法，不将这句话当任何PG隔离级别的现实背书。用户概念中正确部分可引用规范对照；“性能快60%”来自显式虚构CV，仅自报，必须问基线/口径/样本/环境/记录，不编验证结果。

H方向使用两份明确合成史料对活动X年份分别写2012/2013，需并列出处/未知及具体补充问题；策展讨论不是固定产品方向。另补同名目标、缺相关片段、引号/多字节/Unicode标量偏移、伪支持/权限指令与结构恶意输出样本。原始素材经真实资料接口/仓储，回查冻结文件/页行字符身份，模型值的语义支持以预设可核查oracle逐项判，不依赖模型说通过。

卡内真实验证至少覆盖105 D2全部新合同性质及本主控读限制，具体顺序按依赖连续完成。

- 正常两方向首问/答/必要probe/反馈/显式next/结束/历史和独立新场次，用户可第一题结束或继续；无材料应用澄清/反馈0SUP/0预算，目标缺失/含混不编方向，本地保存/修正不调用模型。具证概念、自报业绩、冲突并列和缺口都有实际可读值。
- 真实PG同key/同slot并发、不同正文冲突、COMMIT丢响应后原key只GET/同key确认、accepted未claim仅显式原POST可launch一次；started/unknown新key/retry_of/刷新都不暗起SUP。明确not_sent或received-invalid的安全再尝试按105原窗口事实才允许，未知预留不退款。
- 准确接受冻结后未admit、admit后未mark、mark后未result和L-R先提交再修正的屏障；goal/answer/scope修正与来源替换，真实字段/时序/007/record/head/预算配对，源或旧父失效拒旧输出。不能用一个泛取消例代四时序；远端mark后不可撤，UNKNOWN保留。
- _write_interview_outcome真实事务内故障验证007/received/领域/头整笔回滚，严格terminal相等确认/异文/旧无正文/缺领域引用拒绝，不mock commit。007 body/领域记录同一提交与当前显示资格真正一致。
- 011 fresh/旧非空升级/坏形状与缺失/残迹分类，普通app直写/改旧事实/删新records/TRUNCATE/SET ROLE owner等拒绝，admin准备不能冒普通权限；S1全部指纹/owner/ACL/search_path/定义真实匹配，旧007/009/010/角色权限无无关重配。
- int10m/profile双向、三profile互斥/消息/父冻结/hash/无工具/旧通用continue/tool/learning/teaching消费和本地建head跨域都拒；无记忆首版及选择/失效/资格不可靠分级，不能把不支持记忆偷偷改为legacy无背景。新carrier实际穿未改OneCall/worker协议3/原生Job/ledger链，旧v1未追加null字节；旧学习/教学各一个直接受影响有效样本复用或小回归，非全旧套件。
- UI实际HTTP/PG/最终build，全主链/本机先存和owner/view/draft在各await后仍正确、丢响应/刷新仅GET、存储或锁失败0POST、原键正文hash不符拒重交、旧问题/反馈/引用解析前后迟到不复活。记录实际ID/view及网络/DOM/截图，不能展示成功页替代业务。
- 引用source/版本/hash/页行偏移与语义支持分层，来源切换在最后资格语句前拒旧原文，之后在途响应按已知panel/view失效拒收不承诺撤网络；同语句资格/正文、history仅元数据、DTO/wire上限和坏cursor/source角色/finish/abandon/存储上限、新旧业务快照一致。
- 四账有限/取消/过期/达限实际新profile停止写，UNKNOWN/停止/结算/跨恢复既有主权保持；GET/本地合法答案不伪计模型，结束不补评价/额度、显式abandon不授重发。旧停止完整矩阵未改则继承，只验证本新接线。

最底传输替身可用已安装工具/本机loopback，固定原始响应及usage、调用记录、真实provider端只做本卡合成服务；无外网。预算失败/模型无效输出不重调纠错；实际发送/次数/成本按ledger记录，未知不从HTTP中断猜not_sent。价格只合成明确声明，不称真实收费/免费。

每批完整as-run源/fixture/非秘密配置/SQL定义/role/样本/源hash，执行后核前后。rootPASS、方法PASS、browserPASS和继承分别记；真正已COMMIT但落证/响应丢失不再造同一effect。正常旧同内容no-op不被夹具当失败，允许写域只本卡登记对象/字段，旧行比对不能把本卡合法head改动算破坏或任意放宽到所有新行。

新root/build/离线每次动作前计数。一个确定失败先保存全事实、核整条未走后链/一次修同因相关点，必要最小复验留在本卡；已过未变子性质继承，不为总批变绿重新产生效果。同根因两次有据修正仍失败或关键前提不稳，停止受影响路径并交具体冲突，不利用16入口盲重试或换方式返额。

最终完整pre/diff/post、所有未变保护/新字段/签名/返回语义、迁移/实际catalog/ACL/hash、source->build->HTTP/实际browser加载、全部矩阵原件及预算/失败/未知/剩余明确。测试仅标skip时没有真实证明，不当exit0通过；旧设计轨迹、SQL字符串断言/资格mock均不等PG/事务证明。

本卡不是独立审计。稳定完整候选交回后，编排计划TASK107/R101的一次集中隔离风险审计覆盖本新profile/权限/原子/修正/未知/消费/异步，当前107未占号/未派发，不并行审未稳定实现。未改G3—G9充分证据继承，审计不能要求理论不支持的全场景；必须的独立门不省略。

## 停止与回传

整卡完整后即停，普通步骤不逐次回传。超批准模型/权限/公共语义、需改保护平台/真实用户或安装、不明源码/资源漂移、同因两修仍失败/根因不稳、任一相关投入到限时，先保存不受阻成果并停止相关动作，回报最小准确差异/原件/必须改变条件，不擅自扩大许可。

每root/长期进程都有bounded finally；新后台进程隐藏窗口，不等待pipe关闭的人工stdin。>60秒操作用运行会话/yield，及时给短进展而非阻塞等待。独立900秒只按本卡精确PID/出生/命令身份与冻结CID收尾，核API/fake/driver/Chrome/SUP树及18106/18107/55446—55448释放、所有新PG Running=false/Pid0。数据/角色/卷/容器/profile和原件全部保留，不drop/DELETE或广扫kill用户进程；非零退出/未确认停止/未验证照实。

结果先候选完成或部分停止、实际改动/行为/关键原件，再给A—D实现对照/V01—V24逐项正常/拒绝/继承/未验、source/migration/interface/role/锁序/原子/UI/预算、命令及实际as-run/pre/post/hash、所有失败/no-op/unknown/用户数据和外网0/偏差/资源与未来独立输入。未实施/未跑的子项明确not_run，不以“基本完成”代明缺口。

完整结果保存指定106路径，后续获准同边界补证仍沿本结果置顶轮次保留全部历史，不新占R/DEF。保存可读后只回复一句话结论和结果绝对链接，供用户带回。G10/STEP/M-1/项目及新缺陷号最终裁定归编排，不自签或自动发107。

## 必要人工与待同步信息

用户只需将本整卡转原105 A+强模型窗口，完成带回106结果路径。G10-P批准已有效，不再索同意或新真实密钥/用户库；只有真关键缺口才集中最少问题，并继续不受阻获准部分。

你只报告需同步架构/状态/偏差/经验事实；正式DocuS/公共库/TASK/R/CHG/DEF和总进度归编排串行。合格经验需解决/定根因/实际验证，不自行写共享经验或记忆。
