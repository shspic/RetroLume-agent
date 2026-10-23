# TASK-128 / R-122 正式安装连接故障完整收敛与六项真实验证闭合

## 目标与交付

接收A+增强工程，继续刚执行TASK127的原TASK125安装工程窗口。你在同一卡内先取得真实连接失败的可比较、脱敏诊断，完成范围内最小修复，再把127未完成的六项真实部署检查连续闭合并精确停止。不是重做旧离线或盲重跑；遇真实停止条件才统一回传。工程不代签独立审计、主控验收或Q启用。

结果保存D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-128-result.md；新辅助/运行原件保存D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/。127统一报告、收据、检查点、as-run及历史原件全部只读保留。不要把127失败改写为通过；本卡六项可以用新实证补足原采用包目标，并逐条交叉引用。

完成要求是连接根因有可复核证据、必要增量最小且原隔离不减、六项各有真实目标行为证据及完整资源/预算/停止账。仅原代码/记录器通过或顶层控制器exit0不能称完成。若产品有增量，交稳定候选与集中增量独审所需证据，不自签最终通过。

## 项目、规则和安排

真实项目根D:/shspic/project_NO3_RetroLume-agent，入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。模式task_model，V4.0/AGENTS CHG-0003。公共根D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4；读DocuS/AGENTS.MD及WORK.MD合同/停止/记录有关章节，锁定指纹在项目DocuN/evidence/v4-migration-20260930/rules-snapshot.json。未变同窗材料复用，只补当前差异，不读其他模式或自动采用新版本。

需求v1.4，架构v1.71，执行动态v2.99；关联原TASK127/R121、已验收125/R119与126/R120、STEP018部署前置、STEP019适用权限证据、STEP020本机交付，NFR-004/CON-002/DR-002和既有隔离约束。新增受限连接修复权使本卡区别于127冻结版纯验证，旧失败/投入随相同资源和目标连续，不因新编号清零。

A+理由是正式连接与可用控制连接差异、libpq环境、权限和真实事务边界的故障定位；实际模型/客户端如实登记，不以档位代身份。默认原工程唯一窗口，无并行实现/审计，126独审窗口不执行本卡。没有实际接收前仅待转交，已记录主控回收127不等于你已接收128。

实际授权仍是用户确认AP-125-NORMAL-INSTALL-01的两固定PG槽位/原六项及项目范围内普通缺陷修复；主控现按本卡显式恢复同包剩余工具和资源额度，不请求用户重复批准普通步骤。读DocuN/evidence/TASK-128/orchestration-20261023/内restored-scope.json、input-manifest.json、permit.json及本卡全文。正式签发2026-10-23T08:41:22.786112+08:00，截止仍为2026-10-23T16:14:03.021104+08:00，Asia/Shanghai，不新开24h。

## 真实断点与先读材料

127报告16765字节，SHA256=e001d7892f3e11581db4731e53242cd007870165c97a7b186496ebb84b3dc73b。主控已核168条身份引用无漂移；41产品/七规则及三辅助as-run相符。两槽位曾真实启动且控制器连接查得PG17/vector0.8.6及OID/systemid。正式CLI的两trace各只有一次real_connect_requested、没有returned，写请求0，收据仅intent/stopped、confirmed=[]、unknown_stage=null。错误OID反例和002注入都未真正到达，六项没有一项完整通过，不能称部分迁移成功。

关键证据缺口是install-observer.py调用real_connect抛出后未保留脱敏异常；产品将其归一为installation_stopped。因此产品、环境、凭据还是夹具的根因未知。正式connect比控制器连接另带service空串和options等参数，这是待验证差异，不是已确认原因，禁止照猜测改一行就宣称修好。

已有Docker API500/version超时、原生读取受限令牌errno5、辅助No such/no such大小写误判的失败及修正保留；最后一次已证明引擎与两个PG可用，不重复拉镜像、建资源或要求用户恢复引擎。原收尾post时点两CID均Running=false/Pid=0、端口无监听；当前执行前仍核实际归属和状态，不凭历史推断实时已停。

按序读取根入口/已变共享顶部/本卡与许可；TASK127-result、TASK127-work-decision、本卡input-manifest与旧127原完整合同；127 execution的post-snapshot/final-checkpoint、entry-03/as-run、两trace/command/receipt及实际run-six.py/install-observer.py/win-support.py；正式initialize_normal.py的connect/read_credentials/apply/verify和当前psycopg/conninfo直接依赖；最后按实际需要读原001—015固定清单、原生start_local/Compose和data_exit配置/ControlHub/根绑定/权限原接口。旧126代码审计和18/9方法仅复用适用结论，不重新全审或重跑。所有相对路径以真实根为准，必要上下文同窗未变只补缺。

## 精确对象，只复用不创建

source固定CID=db709b67cc8af398edf1735b0ac6fe365898264326466b2566f904784bfef48d，容器retrolume-q-first-normal；卷retrolume-q-first-normal-data，项目retrolume-first-install-source，bridge Id=2f79fb05977e79f3fa89791f4a97553334be384ba6df89ecd0dc650c2018adb2；127.0.0.1:55482，库retrolume_q_first_normal，OID16384，system_identifier=7699647093882925094，管理员retrolume_source_bootstrap。

interrupted固定CID=549f36f11827babea930f0338149aa3542e8ea4d3d7cceb67b54b79e25dca8e8，容器retrolume-install-interrupted；卷retrolume-install-interrupted-data，项目retrolume-first-install-interrupted，bridge Id=c333276027ca367edf8086eec15763185fe2800f66c820792e7ad96cb842d610；127.0.0.1:55483，库retrolume_install_interrupted，OID16384，system_identifier=7699647123872251942，管理员retrolume_interrupted_bootstrap。

镜像仍仅缓存pgvector/pgvector@sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f，CPU1/512MiB/pids128/restart=no/loopback/无host bind，最多一个PG活跃。新容器/create尝试、卷、网络均0；不compose up/create/down、换名换端口、重置账号/密码、换镜像、拉取构建或接管别的资源。只按上述CID start/stop并核镜像/挂载/创建时刻/网络Id/映射，现有名字不足以授权。

私有根只复用D:/shspic/project_NO3_RetroLume-agent/.runtime/normal-first-install/source及interrupted。原data/backup/control/restore和originals实体file-id/owner/SID/三个UUID逐项沿用final-checkpoint及本卡scope。device=1031070048549017791；source四根file-id依次562949953906263/6264/6265/6266（后三项完整值分别562949953906264、562949953906265、562949953906266），interrupted依次562949953906295、562949953906296、562949953906297、562949953906298；完整精确实体以原JSON和本卡scope为准，不按字符串简写匹配。当前SID/owner仍须符合原记录。发现漂移停止，不再生成新的安装UUID或root身份。不存在成功控制行或ControlHub是原报告范围，不假称已核当前DB为空。

原DPAPI秘密只能通过现有本卡归属私有位置在当前用户内存解密复用，不能重新随机密码或ALTER ROLE。诊断前先在内存确认控制器与正式入口使用相同秘密字节；证据只记相等/引用名，不输出值、可猜测摘要、DSN或完整环境。安装/业务/快照/maintenance四用途继续分离；source业务/快照登录仍retrolume_normal_app/retrolume_normal_snapshot，interrupted仍retrolume_interrupt_app/retrolume_interrupt_snapshot。应用不继承安装管理员DSN。

本机API候选只从18122、18124、18126按序核可用后一次选定；原API尚未选定，不能把PG端口选定的限制错套为API无可用端口。选定后不轮换。遇系统保留端口不改Windows网络/排除范围，不结束他人进程。无用户库、旧合成库或旧TESTONLY配置。

## 诊断、允许修复与先后门

先离线把新观察/控制器/保存/预算/压力退出准备完整，原127原件不覆盖。可以复制必要辅助脚本到新execution后修改为128，但产品不依赖这些脚本。新检查点引用原final-checkpoint并继承实际数值和资源身份，不改原checkpoint/旧permit强行再跑127入口，也不绕旧3/3门。

第一步先补证据能力。观察层在real_connect外捕获异常，记录实际异常类/模块、SQLSTATE（可空）、安全类别及限长已脱敏诊断；处理所有当前秘密、连接串和参数后才落盘，禁止原样str(error)/repr(kwargs)/整个stderr/traceback泄露。保留异常原义继续抛给正式工具，外部CLI脱敏归一仍可保持。必须在无凭据合成异常里验证记录确实生效且不泄密，不能再次只有installation_stopped就盲重试。

比较必须固定同一源CID/host/hostaddr/port/database/login/秘密、驱动版本与子进程环境，只改变经过源码核实的最小参数差异。离线能经真实libpq参数解析定位的问题先离线确认，不为每个猜测start一次PG；纯记录器只用于安全/调用序检查，不能证明真实库可用。需要实际认证时，先在source本轮唯一启动中以控制器真实连接查同一身份，再用正式connect做只读连接及真实异常对照；此诊断阶段禁止apply/DDL/DCL和业务写。

定位证据须能区分环境/凭据注入错误、验证包装错误、正式连接参数/驱动适配缺陷。不得通过去掉hostaddr、放松loopback/OID/systemid/NAT核验、借助未知service配置或旧环境回退来制造成功。不读取用户PG service/passfile等未授权私配。service空串或options若证实为根因，修复必须保留原来防环境隐式改写目的地及凭据的安全目标；不能简单删掉隔离项使PGSERVICE/PGHOSTADDR重新取得效果。

允许只修新增execution辅助；如果真实根因确在产品，可修改deploy/initialize_normal.py的connect参数适配和为维持既有环境隔离所必需的直接局部帮助，backend/tests/test_normal_install.py补最小正/反例，并在README.md、deploy/normal-install.md按真实事实最小更新。必须先存pre副本/hash、最终完整diff、受影响调用分析和as-run hash。禁止修改SQL/role/profile/manifest/原配置schema/权限模型/业务代码/原native启动器/Compose/依赖锁；不得全局修改驱动或用户环境。

旧测试若断言的正是已证缺陷参数，按根因改成能区分坏行为和安全修复的新断言，保留其他安全断言与原失败；不能以删除测试/替换真实connect/跳过apply来造绿。只集中验证直接受影响方法与新根因正反例，不重新全跑旧18/9或整仓。保持F126-01显式host/hostaddr=127.0.0.1、合法NAT支持和F126-02物理路径保护、四秘密隔离、提交未知不重放、schema/权限检查。若要改变安全策略、认证信任、安装目的地、ROLE/SQL或公开接口则停相关部分交回，不能凭普通连接修复权扩范围。

根因和修复验证具备后，先完成当前source同一身份的只读核验，确认未有迁移、额外表/职责组/登录或未知提交；以实际原只读预检/目录事实与原收据交叉验证，不凭旧trace的writes=0作DB绝对空证明。只有该证据及修复安全门均满足才用新收据执行下一段。若发现真实submitted未知或非本卡对象，不清库、不补签或自动续装。

若产品未改，原126门按不变范围继承；若产品连接增量落地，工程稳定后由主控集中安排独立增量审查其连接边界、差异/直接影响与新真实原件，不重复未变SQL/角色全审。本卡工程不自签该独审或最终关闭；角色/不可逆原风险边界沿用原126已审模型，新增策略变化仍是前述硬停止条件。

## 六项合并验收，全部原目标不删减

原六项完整标准以只读TASK127.md“六项真实检查”为原合同输入，本节同步列出，不能仅凭引用跳过。原失败不重复覆盖，用本卡独立收据/trace，旧收据仍保留。

1. source空库分别错误OID/system_identifier真实拒绝、非空表和职责组碰撞各自拒绝，须命中对应原因且安装器无写，不能都命中other_clients。允许的临时对象仍仅public.retrolume_install_probe_nonempty及retrolume_data_app NOLOGIN碰撞组；只在事前证不存在并记录本次创建OID后创建，按同名同OID精确撤销，仅安装成功前完成，不触动后续正式同名职责组。不要全库清理。
2. 同一source原生正式apply完整执行原001—015，不改SQL/guard/事务，不再运行initialize-materials；实际观察013后normal/R01、014/R02、015/R03、原schema_checks/q_roles及37条完整成功收据。确认17个submitted/confirmed和complete均对应真实提交；只用观察包装，不能Recorder替代驱动或patch核验。source真实成功仅一次，后续不重放迁移。
3. 真实新业务/快照登录分别认证，核ROLE_CAPABILITIES/MEMBERSHIPS及实际最小读取。快照不能业务写/读maintenance/SET业务或owner，业务无超级/建库/建角色/复制/bypassrls/owner/传递SET/INHERIT/ADMIN越权。实际权限查询或少量有界回滚反例即可，不扩全安全矩阵、不造业务账。
4. 按原loader/data_exit结构和四根/UUID建立真正normal源与ControlHub绑定，model/integration/Q/preview关闭。正式deploy/start_local.py --container retrolume-q-first-normal --port 已选API --shutdown-stdin启动，读真实capabilities/readiness，区分预期Q外部门未齐和本地来源/schema失败。正常停止，再同一CID/库/根/身份原生重开一次、读取和正常停止；无自动迁移/换身份/重置。保持安装管理员不交应用。无需浏览器/worker/模型/预览；不得为绕正式生命期改startup源码或用旧只读恢复目标假装正常源。
5. source停止后只启interrupted，在原002真实执行、耗尽结果且COMMIT已成功之后唯一隐藏一次确认，观察001 confirmed、002 submitted/unknown、无003/complete/自动重放，另真实只读查提交事实。保留部分库/卷。原收据再次apply与verify本地拒绝，新收据对部分库真实零写拒绝；不续装/清空/补签。此前127尚未到此注入，因此本次仍只许一次实际注入，不误称重复配额。预定此例未知允许按场景观察/收尾，其他非预期未知均停。
6. interrupted停止后source同一成功收据真实verify，只提供管理员密码环境引用，不提供其他三秘密及业务/快照DSN。READ ONLY/schema/roles/身份一致、收据字节不变，无DDL/DCL/业务写；坏收据绑定在连接前拒绝。正常verify必须真实连接，拒绝前0连接可用观察器证明。最后停止source。

开始真实段前把以上六项的身份/连接/退出和预期断言核成完整计划，避免到末尾才发现控制器分支先天不能到达。可以复用127未变正确辅助和已核资源创建证据；不能继承不存在的六项PASS。原3入口与全部失败原件照留。

## 连续预算与可行顺序

原采用包工具10800秒未加总；127精确unknown、保守已占4800秒。本卡只恢复余6000秒，含900秒保存/自有收尾；新增实际投入与原4800累计不得超过10800。日历仍至2026-10-23T16:14:03.021104+08:00，不因新卡重启24h。125/126/120/117旧账保持。

原合并入口3/3封存，本卡前向增加至累计最多6，新增至多三个显式进入受控真实段的合并入口，编号沿entry04—06留账。离线读取、控制器语法/安全自检和一次有界只读引擎前置不独立算真实入口，仍记实际失败/耗时；不能用长驻循环隐藏真实多次启动或绕平台审批。修正后只续失败/尚未执行段，不把六项全套反复跑。

资源累计硬上限不变。source start原1/4，剩最多3；interrupted原1/2，剩1；API原0/3；PG持有原8.117866039276123/1800秒，API原0/900秒。新create/卷/网络均0。预算应读原checkpoint和新连续账，不写零起点。

可行顺序是先离线定位/修辅助，source第2次启动内合并真实只读连接诊断、必要确认、拒绝反例、成功安装/权限和首个原生API周期；source第3次启动作同库重开第二周期后停；interrupted第2次启动作唯一真实注入/拒绝/停；最后source第4次启动verify/停。可在同次PG存活期间安排两个API周期以节省一次start，但不能为了省次数虚报同库重开或占用长时PG等离线改码。若实际诊断须停库修码，重新计算剩余启动能否覆盖原六项，不能暗加第五次source或第三次interrupted。

启动PG/API前现机Docker暖机后可用物理内存>=512MiB；约2秒采样，连续两次<256MiB停止新动作并精确关闭自有API/PG。不反复要求用户释放内存、不用2GiB门、不同时开两PG、不启动浏览器/renderer。PG/API持有按start请求到stop确认计，不只算SQL秒数；命令父子重叠分层不双算，不漏筹备/修码/保存。

原生start_local优雅停止150秒和父等待/终止已有上界须预留，不能自行缩短导致误判。压力退出/日历/剩余工具不足时只作有界自有收尾并保存。产品或同根因两次有据修正仍失败、根因不稳、新高风险/权限范围改变、任一累计上限到门，停受影响部分并完成不受阻项后一次交回。工具unknown如实标未知及保守占用，不编精确秒数。

## 安全、证据与最终回传

主控只恢复本卡范围内许可，平台审批仍适用；审批容量/权限拦截如实记未执行，不拆命令/换客户端或参数绕过。无SQL/权限/镜像/依赖新授权需求时不要重问用户已决定的普通步骤。

随机秘密/DPAPI密文、DSN、Env和完整Compose禁止进入公开证据。新diagnostic须有安全白名单和实际异常留存，避免两端都“泛化错误”导致无法定位；脱敏前不得写临时原日志。真实值只在内存/安全子进程环境，不重置或索取聊天密钥。Docker只输出完整JSON在内存取白名单后的投影，不用旧HostConfig.Mounts格式模板。

保存接收/规则/输入pre、每次实际as-run源码或完整指纹、产品pre/post与diff、根因反证和最小修复验证、六项原始收据/trace/DB错误码/权限及两次原生API的真实事实。停止证明按精确CID/创建身份和自有API PID/birth/句柄或进程树，最终Running=false/Pid=0/端口释放；同时保存旧成功和失败数据。无prune、compose down -v、DROP DATABASE、递归删除、第三槽位或清理旧scratch。允许精确临时反例表/组撤销的原边界不扩大。

Q保持FROZEN、T0/72h空，真实provider/Embedding/计量/费用、索引/查询/生成/三活动/grant/QAuthority.bind/InstanceBinding、浏览器/预览/业务Job、Git写均0；原100/25及分额不变。无新账号/token/模板/容量事实。本卡关闭式正常安装不能替代真实Q前置，也不自动放行STEP018/019/020、M1、项目或发布。

报告先写一句结论、连接根因证据、实际改动、六项逐项实际状态和原件导航，区分复用、实际新通过、失败/未跑；再列TASK/R/STEP、实际模型、基线/hash/配置身份、全部失败/修正与实际预算/持有/启动连续账、清场与保留、限制/风险/偏差、待同步文档、必要人工和下一步。若产品修改，给下一隔离独审的稳定差异与原始证据，不给实现聊天/思考过程，不自签独审。

本卡及结果未验收的同范围续作沿用本TASK/R和本结果置顶保留历史；不得改127原结果/原卡/原checkpoint或正式DocuS/公共库。当前唯一人工动作是把卡交原工程窗口、完成带回路径；不要求用户建库/删东西/释放内存/发送秘密。整卡完成或真实停止门到达后保存并复读结果，只回一句结论与D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-128-result.md的可点击绝对路径。
