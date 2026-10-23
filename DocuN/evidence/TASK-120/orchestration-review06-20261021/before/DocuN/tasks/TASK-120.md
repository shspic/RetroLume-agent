# TASK-120 / R-114 — 续作06：范围移除权限、严格兼容及最后两项迟到UI收口（当前有效）

## 目标与交付

你是本卡唯一工程执行者，连续完成获准实现、定向验证、普通修复及精确清场，不接管编排或独立审计。交付一个可交集中独审的完整稳定候选：**真实范围移除可用且权限/指纹保持严格；namespace与完整DataContext迟到响应的真实UI证明闭合；既有充分证据原对象复用。** 不重跑完整正常五入口、99→100预算基线、全部ACK/权限/K2矩阵。

交付A—D：A为015单表权限及精确profile兼容，B为实际范围收缩与其直接竞态，C为两项真实迟到UI，D为最终身份、证据映射、金融分账、完整失败/投入及StopProof。普通中间步骤不回传，独立子项逐个checkpoint；普通修正和有依据的定向复检在本卡连续完成。完成或触及真实停止门才统一回传，不因一个报告/夹具错误丢弃其他独立成果。

## 项目、规则、授权与接收安排

- 根目录：D:/shspic/project_NO3_RetroLume-agent；入口：D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。
- task_model，V4.0/公共AGENTS CHG-0003。公共只读根D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4；适用DocuS/AGENTS.MD、DocuS/WORK.MD的task_model分工、完整合同、证据、投入/停止和集中审计章节，以及task_model/TASK_TEMPLATE.md、task_model/prompts/07_开发执行循环.md。七锁定指纹：项目DocuN/evidence/v4-migration-20260930/rules-snapshot.json；同窗未变已读材料复用，只补变化或缺失，不自动采用后来规则。
- 需求v1.4、架构v1.53、执行动态v2.81。TASK120/R114/STEP018和TASK119批准合同关联不变；本卡不是新的TASK/R，不占121/R115。
- **接收Agent：A特殊指派，继续刚完成“完整收尾05”的原A独占工程窗口。** 实际客户端/模型如实登记，未暴露就不编型号。原先A+窗口继续停止，不是本次接收者。不委派子Agent、不并行运行实现/测试/独审。权限、严格版本兼容、真实上下文及不可逆freeze相互关联，须使用胜任此复杂度的最强工程资源；不再换窗重建历史。
- 用户在主控2026-10-20给出的AP-120-06包后明确回复“批准”。采用原件D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/orchestration-adoption06-20261020/adoption-proposal.md，SHA256 **3884a5c056cb13f0216c59652a408ea57edbbc5064d429b5d2ea783f172c5c70**。其中“待决定”保留为当时提案历史，本卡与主控最新裁定登记其已获采用。
- 本次前向许可：**TASK-120-Q-PREP-CONTINUATION-06-20261020**，精确机器可读边界在D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/orchestration-continuation06-20261020/permit.json。本卡仅取代旧卡对本次015/严格profile适配、一个新合成源库/一个恢复目标和新时窗的禁止；其余安全/语义/原预算继续。
- 原05已结束且过期。本卡首次实际接收后才把新permit/接收时点/新计数上限差异append-only登记到原execution/budget.json及events.jsonl；不能把主控签发时点伪称工程收到，也不修改旧permit/caps历史。
- Q继续冻结，真实provider、真实密钥、实际付费、preview、Git写入及用户库迁移预算均0。此处100/25为原TESTONLY合成上限，非再次授予真实100次/25元。最终独立终审和主控验收仍待，不宣告STEP018整体、019/020、M-1、项目或真实Q放行。

## 背景与最小充分上下文

主控已核7规则、202当前文件身份、05唯一产品diff、原503/ACK/K2/UI/金融及058—059回执。多数剩余矩阵已有证据，当前不是root64用尽；两组真实余缺是scope移除42501和namespace/完整DataContext迟到UI。

按序仅补读：

1. 项目入口/同版适用规则；D:/shspic/project_NO3_RetroLume-agent/DocuS/执行动态文档.MD和架构动态文档.MD置顶；DocuN/results/TASK-120-work-decision.md最新06采用段；上述采用原件与本次permit。
2. D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-120-result.md只读最新完整收尾05；DocuN/evidence/TASK-120/execution/finalization-05/final-review-index.json、remaining-gaps.json、source.diff、final-file-identities.json。按导航读scope-removal-blocker.json、scope-diagnostic-PASS.json、UI-readonly-root-36.json、readonly-actual-PG-body-closed-reconciled.json；不重读全部历史聊天或重跑历史证明。
3. 同目录ACK-matrix-PASS.json及三个checkpoint、K2-head/revoke/scope/source-PASS.json、K2-memory-persistent-reconciled.json、UI-head-scope-root-33/34.json、old-scope-503-reconciliation.json、financial-final-separated.json、retained-original-Q-witness.json、final-stop-proof.json、command-058/059.receipt.json。原件各自名称按实际索引定位，不猜另造成功文件。
4. 原唯一账DocuN/evidence/TASK-120/execution/budget.json与events.jsonl；原118独立归属、TASK119 K1/K2仅取未变验收边界；TASK116冻结样本DocuN/evidence/TASK-116/design/sample-inputs.json和sample-identities.json。原05窗口已有材料直接复用。
5. 直接依赖：backend/app/activities/repository.py的_apply_scope_locked及锁/CAS；backend/migrations/013_data_exit.sql、014_step018_retrieval.sql；backend/app/data_exit/schema_profiles.py、schema.py、schema_checks.py、实际profile引用和正常restore.py中的TargetFactory.allocate/_probe_readonly/_activate_readonly；必要maintenance/control/config及其当前fixture。前端frontend/src/data/context.tsx和实际消费Q响应的活动/教学/面试/检索/HTML组件，frontend/tests/task120-final05-*.mjs。按本次变更沿直接调用读，不全仓重审。

身份基线以05的202项清单和本次input-verification.json为准；修改前存必要preimage/hash，区分旧已存在改动与本轮。当前repository.py SHA256=fee7d35f1c182c78a97152f7a7caeca7a7c38d3fa2174a712494be271a6315f9。unexpected漂移先查归属，不覆盖。旧报告、证据和归档原字节保持。

## A. 已批准的015与严格兼容（实施及先行风险检查）

新增前向迁移backend/migrations/015_activity_scope_delete_permission.sql，**仅向现有NOLOGIN应用组retrolume_data_app增加public.activity_scope_sources的DELETE**。事务化先核预期schema/角色/guard与旧版本，再锁表/授此单表权限，并完成与之匹配的精确版本标识；001—014原字节不改。DocuN中015-permission-core.proposed.sql只是权限核心，不是可直接执行的完整迁移。

这是表级权限，不是行级CAS。可信应用若绕仓储裸SQL可删本库任意活动的绑定；本包明确接受这一最小现有角色模型，正常路径的来源锁→活动锁→CAS/资格及data_runtime_write guard必须继续有效。不得宣称数据库ACL单独能限制每个activity_id；也不得因此另做SECURITY DEFINER范围替换接口、RLS平台或第二路线。

不得授其他表DELETE、TRUNCATE、PUBLIC、superuser/owner/bypassRLS/管理能力；不改既有登录口令/成员关系。正常source app凭据与readonly/snapshot/restore-loader分离，后者不能随此GRANT获得正常DELETE权。只有新隔离源/批准恢复目标执行015或新版本初始化，旧四库不迁移/不扩权。

按实际需要增加一个精确前向profile版本及匹配迁移链/权限/形状检查，允许该标识必需的元数据验证适配；只对应已批准单表ACL差异，不改业务列、金融模型、公开HTTP/备份包格式或编码。R01/R02原常量/旧合同/合法读取恢复识别保留，默认或配置分支不得把旧库自动升级；不把精确检查改成“足够权限即可”。未知profile/多余ACL/不符迁移hash必须失败关闭。

**真实GRANT/迁移前**先完成并保存权限风险检查：实际diff逐项列GRANT对象/角色、profile差异/原常量不变、guard覆盖和回退；用定向离线检查核新旧profile选择及拒绝分支。它是本卡工程自检，不冒称独审。此前主控用户采用不等于代码已经审过。若出现批准范围外的额外授权/表列或公开接口变化，停依赖部分交具体差异，不自行加权。

真实定向验证：015及匹配版本初始化成功；合法ACL精确匹配、故意不符的检查在预期边界拒绝；非normal的写入仍被guard拒绝；新旧profile直接受影响的读取/备份恢复识别保持。失败子例用隔离事务/受控fixture和回滚，不能破坏源库唯一正常样本或旧库。无需全跑旧data_exit套件，不造SQL字符串/mock冒充数据库授权和事务证据。

必要回退限新合成实例：事务REVOKE这一单表DELETE并恢复匹配版本检查/配置，保留数据；不声称撤销已提交的业务scope变更，不把回退当额度重置或再次创建目标许可。

## B. 真正范围移除与直接影响（在源仍normal时完成）

05产品已改为差集DELETE+upsert，新增/更新已通过。保留该成果，只补实际删除：用真实应用角色和正常仓储/HTTP完成合法scope缩减，证明只移除目标绑定、scope_revision恰增一次；其他活动、head及金融按业务预期核对。区分“合法用户显式更新head/范围”和模型旧结果不得偷偷推进；不能把合法资料共享误当跨活动越权。

以最小定向反例确认旧CAS、来源无效、未知活动/错误父身份等在既有目标边界拒绝、无部分绑定写入；未受改变的11项全请求反例按原对象继承，不要求全跑。正常入口准确错误码，不用任意409/403/503充当通过。

只新增**scope真实收缩**的K2释放窗口：真实shared dispatch段释放后、结果exclusive重取前由独立actor合法移除绑定；记录两方时序/锁/COMMIT、007 received与费用保留、旧head不推进。scope新增、head/revoke/source及原memory证据不重做。未知/已领取旧键不得为了测试重新发送。

先保存B金融/范围/身份checkpoint，再进入冻结/目标切换。若A/B发现真实普通缺陷，可在下述允许范围同卡修复并只补直接影响，不能提前冻结源再靠重建源补B。

## C. 最后两项UI：先取真实正常响应，再切换

原matrix-final永久frozen，不是可回用normal样本；旧过期root/grant/活动不延期、不重绑。根36的错误顺序是先冻结，再取Q正常响应，正确q_root_changed使UI路径根本没开始。**本轮不得重复这个顺序。**

实际启动前以所读代码完成一次有界顺序核对，逐项写明normal准备、两个GET捕获点、可能触发freeze的backup/maintenance、restore verified、上下文刷新和各响应释放点。若正常backup本身会冻结，两个响应都须在backup之前完整取回并暂停交付，而不是等目标verified后才尝试取旧Q响应。已有fixture合理适配，不增通用调度平台。

在新源仍normal且原批准合法时，从生产HTTP取得**两个独立的真实批准/资格GET 200响应**，包括实际请求身份、原响应头和完整body，浏览器路由只延迟交付，不改body/签名/权限。每个捕获立即保存checkpoint与摘要；运行根内预先安排有界释放/finally，不能持PG/response等主控聊天。可复用正式未变bundle；有前端产品变化才正常build并以实际JS/CSS响应hash绑定被测字节。

1. **完整DataContext子例**：经正常维护机制冻结/readonly，生产capabilities/上下文刷新真实生效。逐字段核control_id/selection_generation/dataset_id/instance_id/current_mode/read_only，单独展示namespace可不变而mode/read_only已变。确认UI已观察新完整状态后释放第一个旧正常响应，旧正文/输入/继续资格/意图台账不得污染新状态。
2. **namespace子例**：通过正常backup→restore→verify→activate_readonly，实际选中已验证恢复只读目标；生产selector、DataContext、instance/dataset/generation、storage namespace已改变后释放第二个旧正常响应，确认新身份内容/草稿/资格/意图台账不被覆盖、零自动POST。普通同文档tab/view切换不等于namespace切换。

两个子例独立checkpoint，成功一个不能因另一个夹具失败被汇总丢失；原根/子例FAIL不改绿。若生产客户端实际取消，记录真实abort/传输终止与未污染事实，不虚报body被业务handler消费；不能用取消标签、静态setter或旧保存JSON替代原合同需要的实际迟到路径覆盖。正常只读查看及hubRead/hubCancel/bootstrap的既有明确例外保留，不为测试粗暴禁掉所有GET。发现同namespace下完整DataContext校验缺口，允许针对实际响应守卫/消费组件同卡修复；必须由真实路径复验，不降低条件。

## 精确资源与数据许可

所有private配置、临时凭据、正常控制根、originals合成副本和浏览器profile限D:/shspic/project_NO3_RetroLume-agent/.runtime/TASK-120/continuation-06/；证据不含可用授权物、口令、DSN、签名密钥或完整私有票据。口令只走stdin/继承环境/既有vault，不进argv、日志、报告。使用正常生产初始化/选择/授权流程、现有最低传输替身及出站回环守卫，真实外网/模型0，无用户DSN fallback。

**原源容器仅精确复用**：CID b89522070d4b64fc67efed810852ccc21948058f154bf4fa1889f4d8d69a102f；name retrolume-task120-qprep-pg1；volume retrolume-task120-qprep-data；image sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f；原permit标签TASK-120-Q-PREP-IMPLEMENTATION-20261018保留，1CPU/512MiB/pids128/restart=no/no host bind；127.0.0.1:55480，API18120。身份缺失/不符停相关动作，不重建原源、不改系统端口限制或重启Docker。

旧retrolume_task120_flow、retrolume_task120_budget_01、retrolume_task120_budget_02、retrolume_task120_matrix_final四库保留，除有具体核证需要的只读事务不访问；不写、迁移、解冻或延长旧权利，不查改更早六旧资源。只有在原CID/卷新建**retrolume_task120_scope_ui_final**一库，fixture槽scope-ui-final，逻辑库创建尝试/实际对象各至多1；必要时唯一新应用登录名retrolume_task120_scopeui_app，最小权限，不重置旧角色/成员/密码。存在同名对象先核本次创建收据，外来碰撞不删/加后缀，已确认本次对象可原样复用但不能删重建。

新源仅TASK116冻结8份文字与原有限输入。固定活动ID和synthetic限额：01800000-0000-4000-8000-000000000001为48次/12000000微单位，...0002为28/7000000，...0003为24/6000000；共同100/25000000、单笔250000、max_running_seconds=3600。不新加活动ID/改额度，不重刷99笔；来源/版本/normal控制dataset/instance身份由正常新实例实际生成并记录。新immutable TESTONLY root仅用于本轮最小父准备/B/C，截止不晚于本轮业务门，不复制旧批准/重放旧键，不转成正常真实Q。

**仅至多一个新恢复目标容器/命名卷**，必须由生产TargetFactory.allocate创建：name retrolume-task120-scopeui-ro1；volume retrolume-task120-scopeui-ro1-data；数据库retrolume_task120_scopeui_ro；镜像与原源同完整ID，本机已有、不下载；1CPU/512MiB/pids128/restart=no、named volume无host bind、仅127.0.0.1。创建前只读预检55481、55482，固化第一个实际可bind端口；两者均不符则带事实停止依赖，不杀别的进程/系统服务。

正常工厂的slot/accepted profile/schema profile和login_prefix可以在本轮私有测试配置按上述精确目标注册，不改公开接口。工厂的retrolume.data.job/profile/target/purpose标签、随机目标dataset/instance/root/job ID是正常生成身份，逐项捕获实际值；不强行给新目标套原源旧标签，也不冒充源实例。实际CID一返回立即登记到唯一账和精确停止白名单，厂内create/start/后续probe均先计数。不得仅靠同名前缀操作容器，不能绕过factory直接拼造verified/selector或伪造只读身份。

逻辑库新增不等于新容器；新目标容器/卷实际对象累计cap从各1增至各2，创建尝试cap仍各2（当前各用1，只余各1）。Docker隐式创建卷同样先计尝试/对象，失败不能再造替补/第三只卷/第二目标。完整inspect JSON后选择白名单字段核身份/资源，不输出Env，不使用脆弱格式模板碰运气。两个PG只在正常备份恢复/激活确实需要时最短重叠，其余串行；现有目标factory正常流程不能满足时在create前报告具体不符，不能试着创建再找理由。

## 允许范围与不可变边界

允许为A—D最小修改：

- 新增backend/migrations/015_activity_scope_delete_permission.sql；backend/app/data_exit中直接承担严格profile/指纹/迁移链、正常初始化/备份恢复版本识别与配置选择的相关文件（schema_profiles.py/schema_checks.py/schema.py及其确有必要的contracts/codec/restore/snapshot/reference/config/control调用点），仅精确015兼容。不要为文件数扩大改动；实际清单/diff给到函数和调用关系。
- backend/app/activities/repository.py的scope路径及现有activity/teaching/interview/retrieval/learning API与服务中A—D直接受影响的资格/返回投影，维持旧写事务/出站/007/金融合同。原Q包必要profile传播只做同一精确版本支持。
- frontend/src/data/context.tsx；frontend/src/activities中现有ActivityWorkspace/TeachingWorkspace/InterviewWorkspace/RetrievalPanel及其Api/intents/intentMatch、学习原键恢复；frontend/src/explanations中HtmlExplanationPanel及其Api/intents/contracts。仅本次完整DataContext/namespace迟到隔离直接影响，不重做UI。
- backend/tests中本次直接相关scope/profile/Q检查与backend/tests/fixtures/task120/，frontend/tests/task120-*.mjs；原有效断言不删、不把正确权限拒绝放宽到任意失败。必要正式frontend/dist只由正常build生成，未变bundle直接复用。
- 本卡私有配置目录、DocuN/evidence/TASK-120/execution/continuation-06/及原唯一budget/events的append-only收据；统一结果DocuN/results/TASK-120-result.md置顶保留旧全文。不能改旧finalization-05证据、原package或历史失败。

禁止改001—014、原R01/R02冻结常量或任意额外ACL、依赖/锁文件、金融/权威账本/SUP/Job/时钟/恢复主体、preview固定编译/渲染/部署、用户真实配置/输入、公共库/DocuS/共享任务或CHG、已有私密票据。旧作用域中尚未获本包授权的公开接口/业务表列/备份格式/费用/许可证变化仍须交回，不以本卡“完整收尾”为理由扩大。禁止Git/发布、安装升级、镜像/浏览器下载、服务重启、Drop/Truncate/Prune、批量或递归文件删除。

工程产品实现及测试独占归本窗口；主控只维护共享文档，原118只在稳定后另合同独审，不在本卡并行写产品。不要让产品运行依赖DocuN临时实现或公共提示词库。

## 沿用预算、新时窗与低内存控制

接收时先按实际读回核账；签发基准：root40/64、PGstart39/64、API44/96、Browser11/16、build4/8、Native59/128、HTTP1303/10000、111条失败记录；旧TASK117的81条另留。未用余量不是计划用满，更不是每4次另转卡。PG/卷各create尝试1/2、对象1→获准cap2；新源逻辑库单列1次/1对象，不归零原matrix-final的1/1。

command wall保守43917.209199/57600秒，余13682.790801；持有并集2443.530295/21600秒。旧报告43972.006199含059保存预留60，唯一账以实际059=5.203替换后为上述数，早前全部unknown/中断不确定性预留仍保留。人工总量UNKNOWN_NOT_ZERO，不能把calendar间隔一概叫CPU或资源持有，不双计同一并集，不把旧未知偷偷核销为0。

**新时窗不是新增12小时wall额度。** 本轮实际接收时刻必须在首次实际工具前登记；finish_deadline=min(实际接收+43200秒, 原96h截止2026-10-22T08:41:08.5687758Z)，最后1800秒只清场/保存，business_deadline=finish_deadline-1800秒。新TESTONLY grant/动作根必须不晚于此business_deadline；原首点2026-10-18T08:41:08.5687758Z、96h及任何旧grant/活动到期不变。中断、继续消息、换模型不重开这12h；时间没记齐用最早可信下界保守计，不事后假定刚接收。

所有新增动作先经现有控制入口，普通metadata单批≤60秒、测试/build子批≤300秒、真实根≤1800秒含末120清场且受更早门。先将已批准单表权限/新profile/新库/新目标精确白名单和双资源停止登记适配到原控制器，定向离线核截止/压力/异常退出，再启动真实资源；不新造通用runner，不让审批/预检自身错误吞掉业务前置后立刻盲跑。

命令从059后续号（预期060，若唯一账已有更后编号则按实际），根从40后（预期41）；每次根、厂内container start、API/browser/native/HTTP/build均照实累计；旧失败条目不覆盖、同一问题两次修正计数跨窗继承。依赖子项不要机械串成“前一report文件不为全PASS就全体not_run”，按核证checkpoint与真实持久业务事实判断。

PG/API/唯一headless-browser+单context+单page启动门512MiB；每约1秒采样，连续两次<256MiB停止新增动作并自动精确清场。本次无preview/PDF/并行渲染，不关sandbox/证书/会话认证/出站守卫，不杀用户程序，不反复要求用户腾内存。内存/审批只阻相关依赖，推进不受阻离线项；真实限制保留，不能换shell/模型/连接器绕自动审批。

## 证据复用、验证与集中审计

复用05真实11项请求权限与三个ACK、head/revoke/scope新增/source及列明memory、根33/34 head/scope UI，和更早练习/五入口/owner-view/C12等原适用范围。每条继承给具体旧文件/方法/身份和当前适用理由。单表ACL/精确版本增量不自动重审整仓；旧合法profile若被改坏则补实际影响。memory缺即时before-financial快照如实交终审，不为美化包强迫重跑。

原A1 1f5c659f-4a5a-4fee-bfbe-3f245eb5bc7e、A2 430a4e36-08e1-411f-a73e-097506a6278b、A3 3b561488-07b7-4d6d-8b98-05e793c96749及所有后来claim/UNKNOWN、007 received/费用照留，不二发、不退款、不释放slot。旧scope503已经核NOT_COMMITTED且原revision1保留；模型45b8d0b4-dd77-44d7-8cdd-370ef475c7b3 committed/received不重发，不再把旧503当未知根因重诊。

每项真实证据在成功/失败发生当时独立保存，包含实际输入摘要/身份、时间/期望/实际/拒绝码、before/after业务事实、as-run产品/fixture/bundle与最终文件hash。两项UI的响应捕获/切换/释放顺序与六字段DataContext逐步落证，不仅给自评PASS。对不符的金融/身份先核持久事实，不盲重发；日志仅安全字段/异常类型/SQLSTATE，不输出秘密或大段不受控数据库异常文本。

工程检查不是独立审计。完整稳定后主控另行签发集中增强终审，沿原118独立归属安排真正隔离审计会话，重点本次015/ACL/profile兼容、scope收缩和最后两UI，以及可复核的执行控制。独审接原目标/验收/最终diff/实现/原证据，不接实现思考/完整聊天；本卡不自签独审、不启Q。普通小修不逐项另开审计。

## 停止、精确清场与回传

完成A—D即停；普通夹具/实现修正持续在卡内处理，只复检实际影响。不确定根因、同问题两次有依据修正仍失败、新高风险/重大方案改变、权限越出包、对象碰撞/身份漂移、审批拒绝不可安全替代、任一实际投入/有效期门到达，停止受影响部分并保存具体事实，不机械开新根尝试。不要把账号模型用量、runtime次数、合成费用、日历时间混为一种额度。

收尾先关闭本卡浏览器/API/业务树，随后精确停止源CID及工厂实际登记的新目标CID；核PID/birth、命名Job、两容器Running=false/Pid0、源55480/目标固化55481或55482/API18120无监听。工厂意外创建返回后即便时间已到仍须登记并清场，不能丢掉实际CID；失败创建也核可能已产生的精确卷。保留所有库/目标/数据/卷，不drop/truncate/prune。清场/保存预留不能拿来新验证，也不能以普通额度已满不清场。

结果在D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-120-result.md置顶“续作06”，此前完整报告原字节后缀/hash保留；原始证据统一D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/execution/continuation-06/，唯一账仍execution/budget.json与events.jsonl，不复制成第二预算。结果优先给A—D完成程度、真实diff/权限清单/指纹、复用映射、最终as-run对象身份、金融按实例分账、失败/尝试/实际投入/余量、资源停止证据、未验证/限制/偏差、建议状态及必要文档同步。

不得改旧FAIL/UNKNOWN原件或把合成上限/恢复副本金融相加成正常真实Q。没有完整通过则如实部分返回；完整完成仅建议工程候选可交集中独审，不宣告主控验收/发布通过。确认统一结果真实保存可读后只回复一句话结论和可点击绝对路径，由用户带回主控。

## 必要人工与待同步

除用户人工转交本完整卡/带回结果外，无需用户提供密钥、SQL、内存或重新决定已批准包。包内实现细节、定向测试顺序、普通修复由你连续处理，不为已获权限重复请示。共享状态/架构/CHG/后续审计卡由主控维护；只报告已证实的产品和版本/兼容变化、限制及可复用经验候选，不自行占共享编号。

# TASK-120 / R-114 — 当前停止通知：完整收尾05已返回，AP-120-06待采用

2026-10-20T21:00:42.355974+08:00。**本置顶通知优先于下面历史卡的“当前有效”字样。当前无新增运行许可，不是06执行卡。**

05已回传并有限核证，原业务时窗已在2026-10-20T20:04:46.848938+08到期。原A工程窗口保持停止，原A+同样停止；次数余量不重开旧时窗，不GRANT/建库/解冻/重绑旧批准。多数安全矩阵、ACK和head/scope UI按原证据收存；尚欠真实scope移除权限、namespace/完整DataContext迟到UI，Q继续冻结。

具体待采用包：D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/orchestration-adoption06-20261020/adoption-proposal.md（SHA256 3884a5c056cb13f0216c59652a408ea57edbbc5064d429b5d2ea783f172c5c70）。权限核心审阅草案同目录015-permission-core.proposed.sql，不是正式迁移，不可执行。待一个合并采用决定，主控才签同号06完整合同与精确前向许可给刚完成05的原A窗口；本通知不冒称已转交/开始。

完整核证：DocuN/results/TASK-120-work-decision.md置顶；唯一当前状态：DocuS/执行动态文档.MD v2.80。原首点/预算/失败/UNKNOWN/冻结状态和有效证据全保留；旧05及更早合同仅作为历史，不赋予过期运行权。

---

# 以下为原05及更早合同原字节

# TASK-120 / R-114 — 完整收尾05：剩余安全矩阵与晚到围栏（当前有效）

## 接收、目标及窗口

接收Agent：**A特殊指派，用户当前最强可用的工程执行资源，新建一个独占工程窗口。** 原A+窗口已回传并清场，收到本卡后保持停止，不再并行修改或续跑。新窗用于从实际原件重新审视剩余验证和夹具依赖，避免继续沿多轮隐含状态试跑；它是实施/修复负责人，不是独立审计者。实际客户端/模型照实登记，不虚构官方型号，不委派子Agent。

一次完成原TASK120剩余工程验证、必要普通修正、证据收口与精确清场，达到可集中独审的完整稳定候选。**不得因一个夹具错误或一个证据汇总错误就结束整批，把独立余项全部丢回主控。** 普通修正、有新依据的定向复检均留在本卡连续完成。结束条件仍包括真实安全门、主要方案需改变、同问题两次有依据修正仍失败、总投入/日历/有效期到达；不能以用户要求完成为由造通过或绕安全边界。

Q继续冻结，真实provider/实际费用/preview/Git新增全0。本卡不签真实Q启用、STEP018整体/019/020/M1/项目；完整稳定后仍由主控安排隔离集中终审，不逐小项增加审计卡。

## 项目、规则及授权

根D:/shspic/project_NO3_RetroLume-agent；入口同根AGENTS.md。task_model，V4.0/公共AGENTS CHG-0003；公共只读根D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，读取DocuS/AGENTS.MD及WORK.MD适用任务合同/证据/预算/停止/审计章节，task_model/TASK_TEMPLATE.md与prompts/07_开发执行循环.md。七锁定指纹在DocuN/evidence/v4-migration-20260930/rules-snapshot.json，不自动采用后来版本。

当前需求v1.4、架构v1.51、执行动态v2.79；原TASK120/R114/STEP018关联不变。用户已批准119范围，并于本轮明确要求“下一次必须完成”。主控据此在既定零外发合成验证目标内，明确扩大验证资源与一次完整收尾时窗，**不是扩大真实费用、正常Q或公开接口/持久模型权限**。

此置顶完整合同及permit优先于旧合同每次仅4根、固定三库及旧测试目标用途/时窗限制的对应部分；其余原A—D/需求/安全/允许产品文件继续有效。旧任务号、R、首点、原96h截止、失败、预算、结果、unknown与证据全保留。旧grant及旧活动期限不改、不续、不重绑；不把新实验的成功回填成旧失败批通过。

## 最小交接输入

新窗口按序读取：

1. 根入口、锁定规则；DocuS/执行动态文档.MD和架构动态文档.MD置顶，仅补实际相关章节。新窗不可冒称已读旧窗上下文。
2. D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-120-work-decision.md置顶05；同目录TASK-120-result.md只读最新续验04，较早根因/成功按直接引用读取，不全文复盘所有历史聊天。
3. D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/orchestration-final05-20261019/permit.json、input-verification.json。原唯一账在execution/budget.json和events.jsonl；先核24根已结束、active_root/command空、055 StopProof及最后成功receipt。只有实际接收本卡后才append-only登记新负责人/permit/caps，不改历史counts/投入。
4. execution/validation-04/final-review-index.json、remaining-gaps.json、acceptance-matrix.json、source.diff、fixture.diff、final-file-identities.json、financial-summary.json、original-exercise-positive.json、positive-operation-map-root-24.json、memory-display-PG.json、copied-control-reconciliation.json、final-stop-proof.json及055退出回执；按索引核根23/24真实UI和scope失败原件，不重跑为了了解历史。
5. repair-03锁诊断/五产品diff/实际模型及记忆COMMIT原件，TASK119采用K1/K2及TASK116冻结sample-inputs，原TASK120完整最小矩阵。旧完整合同附后供查具体原权限，不全仓阅读。
6. 直接源码：q_context/q_gateway/q_store、interview bind_scope事务、teaching读取显示投影、相关API映射；task120的setup/resources/api_runtime/pg_boundaries/recovery_races/repair03与最终UI脚本。只读旧counter/原件，不执行旧runner/已完root。

## 已完成，禁止重建证明

原练习cd632dfd-8a25-465b-895e-375b0ce1d48e在根21真实committed/007 current；两域query→model、已选记忆模型、legacy followup和HTML description已有真实PG/SUP/领域提交。五入口有限正常UI根23/24已通过，正式JS/CSS hash绑定成立，owner/view列明子项可沿用。教学无记忆v3读取显示投影修补已在根24实际验证，budget02仍已选，不降低真实memory资格。

原C12双backend99→100、双provider达限拒绝、原库重开100/25000000，旧embedding/first、R300核销、九函数EOL及未变S有限验收直接继承；不再刷99笔、不重应用012、不重跑完整正常UI或重复build。若本卡真正改动上述行为，只补实际影响并解释，不能把读取/包格式修正当重测理由。

原A1 UNKNOWN1f5c659f-4a5a-4fee-bfbe-3f245eb5bc7e、A2原430a4e36-08e1-411f-a73e-097506a6278b、A3原3b561488-07b7-4d6d-8b98-05e793c96749及所有后来领取/unknown事件保持，不二发、不退款、不释放旧slot。原FAIL不改绿；receipt保存错误不代表业务未提交，必须按实际PG事实复核。

## 必须先完成的收尾准备（不依赖旧授权未到期）

### 1. 先核scope503的持久结果，禁止盲重放

budget02释放锁窗口的scope变更POST返回503/database_unavailable，原变更是否COMMIT未知。先以原精确库/业务键/请求摘要只读核interview_commands、head、activity scope、来源绑定、原model operation/007/费用；对照原mutation请求和before快照，给出“已提交/未提交/证据不足”及依据。原model键45b8d0b4-dd77-44d7-8cdd-370ef475c7b3已claim且007 received，禁止重发。过期不妨碍经原应用角色核对持久事实，但不得因读事实重新授予出站资格。

503不等于回滚。若是代码/SQL/权限错误，使用目标模块的异常类型、SQLSTATE、相对文件/函数/行和SQL模板hash定位；禁止日志原异常正文/DSN/口令。旧日志不足时，在独立新合成矩阵场景最小复现并修复，不能声称新场景证明旧交易回滚。

### 2. 修测试协议和逐项checkpoint，再开整套矩阵

逐项把预期错误码与生产实际枚举/原件对齐，尤其control_tail_unconfirmed是正确失败关闭；不能只接受control_tail/control_corrupt而误报合法拒绝。每例立即保存输入身份、预期、实际码、PG前后/claim/dispatch/费用和退出状态；在下一例失败前已完成证据必须落盘。不把整串全PASS之后的一次write当唯一证据。

每项独立返回PASS/FAIL/NOT_RUN及真实原因，局部fixture错误只隔离依赖该fixture的项，其余独立项继续；finally精确恢复临时artifact/关闭barrier/收束线程。普通修正后只重跑失败项及直接影响，不重新做已过正例或整套基线。禁止为了让negative变绿而接受任意错误码；必须证明拒绝发生在目标边界。

head晚到UI旧失败是同文档prepare后列表未刷新。显式GET刷新并等待正确行，再进行原键只读核对；不能自动POST、移除正确晚到断言或改产品流程掩盖夹具问题。核原批准但未claim键9d478f34-cfef-4753-8b73-fb8a4d5f7631及fa4d574c-e47b-4db6-832b-56ae55289582状态，过期/失效不重交；可在新独立场景使用新的有限实验意图，不把它冒充旧意图复验。

## 新独立TESTONLY矩阵样本：旧库/账/期限完全保留

旧flow/budget02批准今晚20:19:22+08到期，原budget01更晚14分钟。**不得赶时间延长/重签/重绑旧root，不替换旧grant，不复制旧Q批准到新实例。** 旧三库保留原bytes/金融/command/unknown，除上述只读核证不继续新出站实验；C12原预算证据继续有效。

为剩余权限/ACK/竞态/晚到的独立实验，准许在**同一原CID和卷内只新增一个确切逻辑库retrolume_task120_matrix_final**，fixture槽名matrix-final。只允许一次对象创建；已有同名对象必须先核本任务创建身份，外国对象/身份不符则停，不删重建或加后缀另开。新逻辑库不是新容器/卷；旧financial row和各库SUM不迁移、不清零、不混算。

用原001—014原字节和正常schema profile/权限初始化；沿已验证同簇角色核对/复用模式。必要时只新建本矩阵专用最小权限应用角色retrolume_task120_matrix_app，仅授新库；既有共享非登录角色只核后复用，不改旧角色密码/权限，不读出或记录凭据，口令只进stdin/子进程环境。无依赖安装、镜像下载或用户库。

新样本仅TASK116冻结8份合成文字/固定输入、同三个固定UUID（...0001/0002/0003）、48/28/24次及12/7/6元合成预留、单笔250000、共同100/25，max_running_seconds仍3600。按实际剩余矩阵提前安排不同来源/正常head/创建时memory选择，尽量一次建全；不得临时重绑活动、复制已消费批准或按测试失败重建样本。

新正常bind仍是immutable TESTONLY root/manifest/grant，身份来自实际新库dataset/instance/OID，来源/记忆经生产接口形成。**仅新样本**有效期为实际接收本卡至多24小时且不晚于原96h截止减1800秒；创建时记实际时间，不能回填旧T0。新配置仅私有测试目录、TESTONLY、原最低传输替身/回环守卫；不得形成正常启用root/真实key/provider配置或可部署票据。旧grant过期的失败关闭行为保持，不因新样本存在被宣布可继续。

新样本是剩余反例的独立fixture，不是恢复旧100额度，更不是新的真实100次/25元预算。测试准备只跑这些反例真正需要的最小正向父，不重新宣称完成五入口正常链；全部真实provider/费用仍0。fixture允许名单只能精确增加这一个库/槽及本矩阵角色，不能取消实例/库/来源白名单或走用户DSN fallback。

## 剩余验收闭环（一个完整成果）

### A. 全请求权限反例

在正常实际PG快照、真实冻结typed request/provider payload和原精确批准下，逐项覆盖原未足的未批准answer/history/memory/title、异活动/foreign parent、真实不同实例/副本、完整字节/endpoint变化、missing original artifact、journal tail、readonly以及删除/撤销后正文不可再取。给准确拒绝码与目标边界，核无新增claim/准入/发送/预留/正文泄露。已保存的副本身份拒绝和尾损坏拒绝按同对象直接引用，只有新的live-PG组合缺口才补。

副本破坏仅新的私有副本；原artifact的临时移置必须锁内finally恢复，先过正常来源/身份，避免用“不相关的过期/实例拒绝”冒充目标权限反例。readonly/删正文等不可逆实验仅新matrix-final；不得解除旧source freeze/永久readonly或在旧三库删除内容。不可逆步骤安排最后，不能先破坏其他用例前提。

### B. 三种丢确认与K2竞态

对accepted COMMIT、launch claim COMMIT、result COMMIT丢响应，逐项证明原持久事实、GET无新动作、同键恢复边界和0重复出站/预留；不得重发已claim/UNKNOWN，不把回执丢失当未发生。每例保存checkpoint，不依赖旧成功文件名或另一个negative全过才装载fault。

在真实shared dispatch释放后、结果重新取exclusive policy/MutationGate/PG前用有辨别力的barrier完成head/revoke/source/scope/memory变更；保存实际worker与变更actor身份、锁窗口、PG COMMIT/head/scope前后、不可变007/费用保留与迟到head不推进。scope先查旧503，再在新样本独立验证修复。变更响应异常必须立刻做持久事实核对，不能继续按回滚分支猜。

在新matrix-final中安排相互不污染的顺序/活动；先收证正常父和只读反例，再故障/失效，source/memory撤销/readonly最后。不要让一例故意制造UNKNOWN后把所有后继永久卡住；按既有本地abandon仅整理业务pending，Q/financial未知照留，必要合法新父必须真实生成，不改槽规则。

### C. 剩余晚到UI围栏

只补新v2 head/scope/namespace/DataContext未足项，owner/view及五入口正常UI直接继承原证据。使用正式bundle，实际JS/CSS响应hash绑定；单Browser/context/page串行。被延迟的旧响应不能改当前内容/输入/可继续资格/新身份台账；记录准确路由/请求业务键和变更前后身份，无自动POST、无原claim二发。数据库状态变更与客户端view切换必须按测试目的区分，不能把仅切标签证明scope失效。

fixture刷新缺陷修正后一次运行相关最小场景，不重跑正常五入口。前端源码未改不build；真正产品修正才按实际影响补构建与绑定。未启动浏览器/内存门阻塞不称UI通过。

### D. 最终完整性、差异与审计就绪

C01—C15及原矩阵最终逐项链接原件/复用/新验证；缺项不得藏在总PASS后。保存各实例分开的新连接金融快照、operation/claim/未知状态、正常与失效后的当前资格、最终产品/fixture/as-run/dist身份；只保存一个准确审阅入口，不复制所有旧ZIP递归膨胀包。

历史FAIL/超限/UNKNOWN保留，当前修后成功分层独立成立即可，不为“把过去全变绿”重复运行。新高风险增量/确实无法满足的原要求带具体差异交主控，不自行改Must。源码/相关测试/证据稳定且没有并行写后，交主控安排原118独立归属集中终审；本工程不自签独审，不以期限将到删必需安全检查。

## 一次完整收尾时窗及预算（不再每4次普通启动就转卡）

前向许可TASK-120-Q-PREP-FINALIZATION-05-20261019。实际接收起一个至多24小时完整收尾窗，仍受原96h截止2026-10-22T08:41:08.5687758Z/末1800保存更早门。原首点2026-10-18T08:41:08.5687758Z不变；新样本时窗也不得晚于本窗可用运行终点。

原已用root24/PG23/API24/Browser6/build4/Native36/HTTP800、88失败记录及原117的81历史、wall保守24382.005564、持有1875.827295和全部未知预留保留。累计兜底caps改为root64、PGstart64、APIstart96、Browser16、build8、Native128、HTTP10000；command wall57600秒、资源持有并集21600秒。次数逐次照记；这些是失控兜底上限，不是计划用满，也不是允许机械重复。

原容器/卷实际对象各1不变，创建新容器/卷预算0；仅增加上述一个逻辑库对象，创建尝试cap1。正常根最多1800秒含末120清场，metadata单批60/测试build子批300；长矩阵按有限阶段在根内自动串行，提前冻结计划，不能PG持有时等聊天。命令从055之后、根从25续号。原88/81记录不清零；同问题失败/修正计数跨窗口不重置。新投入记录真实起止/区间，不重复累加、不机械另加7200、不把unknown记0。

只要未触发真实停止门，普通fixture错误→定位→合并修正→失败项定向复检在本窗完成，不单独带回“额度又差一点”。同问题两次有据修正仍失败、根因不稳/主要方案变化、范围外/新高风险、平台拒绝无法解决或本窗/总投入硬门到达，停止受影响部分，继续不受阻项后统一带回事实；不能承诺未知缺陷为零或虚报完整。

PG/API/Brower单页启动门512MiB，约1秒监测，连续两次<256MiB精确清场。只一Browser/context/page，无PDF/preview/并行渲染，不关sandbox/认证/证书/出站守卫，不杀别的程序/重启Docker/改系统限制。内存只阻相关UI层，独立PG矩阵继续；不反复要求用户腾内存或持PG等内存。全窗都无足够内存则准确报平台限制，不能伪造浏览器通过。审批拦截也不可换模型/shell/连接器绕过。

固定CID b89522070d4b64fc67efed810852ccc21948058f154bf4fa1889f4d8d69a102f；name retrolume-task120-qprep-pg1，volume retrolume-task120-qprep-data；image sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f；原permit标签保留，1CPU/512MiB/pids128/restart=no/无host bind。PG127.0.0.1:55480/API18120，仅原三库及新增matrix-final，禁止替补容器/第五库/新UUID/旧六资源操作。

## 允许范围、停止证明与回传

继承原产品允许路径，额外仅明确fixture新矩阵槽/逻辑库/安全诊断、必要scope503同链修复；不改001—014/依赖锁/schema profile/金融模型/SUP/Job/时钟/用户私配/正式DocuS/公共库/旧原件。若需要主要接口/持久模型变化，完成非阻塞部分后提交最小采用包，不能以本卡“必须完成”扩大权限。原独占实施权从旧A+交新A，主控只维护共享状态，不代做代码或运行。

唯一工程账仍DocuN/evidence/TASK-120/execution/budget.json和events.jsonl。新证据execution/finalization-05/；私密配置仅.runtime/TASK-120/matrix-final，纳入忽略，公开包不含秘密/可用Q批准。新窗先核055及当前精确CID/PID/Job/端口状态；旧停机仅指原时点，不虚称当前查过。

结束先关本卡Browser/API/业务树，再停精确CID；核PID/birth/命名Job、Running=false/Pid0和55480/18120无监听，保留四库/数据/容器/卷，不drop/truncate/prune/批删。清场/保存预留独立于业务额度，不能因普通测试额度到达而不清场。

完整结果仍D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-120-result.md，新轮置顶、旧报告原字节保留。先给真实完整结论和四组余项映射，再给修复/操作/实例分账/失败/投入/精确StopProof/独审入口。不能用已保存或候选字样代替未满足的验收；完整充分即停。用户只需把本同号完整卡转给新A窗口，无密钥/SQL/内存操作要求。

---

# 以下为先前完整合同，原字节保留；本次明确修订部分以上文为准

# TASK-120 / R-114 — 续验04：仅补教学练习、边界矩阵与最终UI（当前有效）

## 目标与接收

接收Agent：A+增强工程，继续TASK120原TASK119/117工程窗口，单一执行者；不委派、不新建TASK、不自行独审。接续已保存的真实成果，只补当前缺口并统一交回稳定完整候选，不重建正常链基线。实际模型照实登记，标签不冒充型号。

本次成果：原accepted/unclaimed教学练习经最终字段修补后真实提交；剩余全请求权限/ACK/K2/source-scope-memory竞态；正常五入口及晚到围栏的正式UI实证；真实PG最终金融快照、最终差异与精确清场。范围内必要普通修复卡内完成，不逐小项回传。Q继续冻结，provider/实际费用/preview/Git新增全0，不签STEP018整体/019/020/M1/项目。

## 项目、规则与真实输入

项目根D:/shspic/project_NO3_RetroLume-agent；入口同根AGENTS.md。task_model，锁定V4.0/公共AGENTS CHG-0003；公共只读根D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，DocuS/AGENTS.MD、WORK.MD适用核证/委派/预算/审计章节、task_model/TASK_TEMPLATE.md、prompts/07_开发执行循环.md。七指纹在DocuN/evidence/v4-migration-20260930/rules-snapshot.json。同窗已读未变内容复用，不采用后来版本。

口径需求v1.4、架构v1.50、执行动态v2.78，原120/STEP018关联不变。用户已采用119完整包；主控在原合成实施目标内前向组织剩余验证，不新增真实Q权益、DDL或公开权限。旧完整A—D/产品允许与禁止路径均附后继续有效，本段只修订剩余工作、依赖顺序与资源。

先读最小变化：

1. D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-120-work-decision.md置顶04、同目录TASK-120-result.md置顶“集中修复03”；旧正文和失败原样保留。
2. D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/orchestration-validation04-20261019/permit.json、input-verification.json。本卡新许可收到后才向原唯一execution/budget.json/events.jsonl追加采纳与cap，不改旧counts/投入/失败。
3. execution/repair-03/final-review-index.json、remaining-gaps.json、final-file-identities.json、source.diff、fixture.diff、readonly-diagnosis.json、repair-tests-050.json、final-stop-proof.json、command-050.receipt.json。
4. repair-03/teaching-plan-reconciled-positive.json、flow-interview-reconciled-positive.json、budget-02-interview-reconciled-positive.json、legacy-html-positive.json及其直接指向的PG/SUP/原artifact/as-run。优先核实际业务键/operation/结果摘要，不用仅“某文件存在”充当业务成功。
5. backend/app/capabilities/q_context.py最后PathNode增量、原accepted练习的冻结原件、backend/tests/fixtures/task120/repair03.py的汇总/后续gate、pg_boundaries.py/recovery_races.py、frontend/tests/task120-ui-continuation.mjs和原最小矩阵。不要全仓重读/重新研究模型账号。

## 已完成事实直接继承

根17已真实证实锁升级根因及修后读取，五产品修补已保存；050最终11项定向通过。原Q UNKNOWN事件序列完整保留，旧键不二发不退款。原flow面试、已选记忆面试、legacy续问、HTML description均有真实SUP/领域/007提交事实；教学plan/007已成。最后教学PathNode/rationale修补仅离线通过，不能扩大成练习动态通过。

C12共同99→100双backend同锁、达限双provider拒绝和原库重开100/25000000，旧embedding、first、R300核销、九函数EOL/普通角色指纹及未变S有限验收均直接继承，不重跑/重应用。前端源码与4正式dist未变，旧build和实际加载hash继承；不以此签最终UI。

实际产品增量/as-run分级必须保留：根20成功链按当时字节成立；最终新增的PathNode字段识别不影响其未涉及路径，按有限差异说明继承，不重新发送已成功原键。

## 先纠正证据依赖，不再重跑已成业务

上轮两条面试已COMMIT，但汇总读取retrieval回执不存在的operation_id而FAIL。主控已收存reconciled-positive的有限事实；旧FAIL不改绿，不把该汇总错误当后端未提交。

当前repair03.boundaries/flow_tail仍按flow-interview-positive.json等旧文件存在判断前置，不能仅因真实成功保存在reconciled文件就跳过。以原业务键、模型operation、query业务键/retrieval_ref.result_sha256、实际PG/007/SUP及原件hash构成有限映射，并正常只读复核当前资格。修正消费者读取映射；不复制/改名一个“PASS”文件骗gate，不重发已claimed键，不造新的全局状态账或通用框架。

若原成功已被后续正常动作转历史，则保留成功事实并在所需后继用真实当前父；不能把“曾成功”当“当前仍有资格”。具备同等业务前置的独立阶段不依赖无关教学练习或旧汇总文件；所有新运行阶段在启动前列明实际依赖和完整有限队列。

## 仅补四组缺口，按下面顺序

**一、原练习与PG金融基线。** 读取原accepted/unclaimed练习及Q prepared/claim事实。确认原键尚未claim/未启动、父/范围/记忆/截止和完整原请求不变后，使用最终严格限定task.path_nodes整数项的PathNode字段修补重新prepare/批准/原键继续。先用完整冻结请求做有限无发送校验，不再逐字段撞生产。不得重做plan、换key绕冲突、扩任意文字白名单、把已claim/UNKNOWN当unclaimed。若事实不符，停止该原键并带准确信息，不猜测处理。

需要真实007/领域提交/结果资格、预扣/mark/settle回执和树零。此时读取flow/budget02金融SUM和各活动R/S；旧budget01的100门只继承，不再积累99笔。每个对金融有预期的后继保存前后读数，最终保留实际PG新连接快照；Q journal不冒充财务权威。

**二、正常UI及只读/副本负例。** 正常五入口UI先做，再进行会破坏来源/范围/记忆/head的测试。原教学/面试/legacy/HTML已提交父正常读取可复用；确需新动作才按当前合法新意图、有限文本、批准和原键继续。覆盖教学、面试、检索、legacy、HTML等待/GET/刷新不自动POST/本机批准/同键显式继续；旧成功只读呈现与必要新等待分别记证，不说所有模式都重新调用过。

只用正式bundle，核实际JS/CSS响应hash；完成owner/view/head/scope/namespace/DataContext迟到围栏的现有缺项，不以旧S矩阵替代新v2。已具足够同对象证据不再重复。UI可按模式独立继续，后端仍失败的模式不启动浏览器复制相同失败。

全请求未批准文本/foreign parent/实际其他实例、missing artifact、copied root/journal tail、readonly/删除后正文关闭等只补原矩阵确有缺口。用原真实PG快照/实际gateway拒绝证明其准确层次和0新增claim/外发/预留；副本损坏仅新私有副本，原artifact临时移置须锁内finally恢复，不损坏活根/日志/原证据，不解除旧source frozen/永久readonly。会不可逆关闭测试实例权利的分支必须最后做，不能阻断还待运行的正例。

**三、ACK/K2及失效竞态最后做。** 原三种COMMIT丢确认按持久事实读取；不因回执丢失重发claim或退款。真实共享发送锁已释放后、结果事务重新排他前，在有辨别力的barrier中做head/revoke/source/scope/memory变更，核不可变007保留、费用不退、迟到结果不推进当前head及后续请求拒绝。按实际已验范围继承，未跑不补绿。

先保存UI/正常正例，再让budget02的source/scope/memory失效；先核各case scope和父，固定活动/来源不足时不要暗建第四库/新活动。ACK产生的未知态和revoke不能阻挡后续正例；若需本地abandon仅依原精确已停合成命令及正常接口，保留原Q/operation/预留，不改金融状态。竞态失败必须有真实阶段/退出/锁窗口证据，mock不替代PG。

**四、统一收口。** 根据上述有限映射更新C01—C15与原最小矩阵，保留每一FAIL、accepted/claimed/UNKNOWN和每项复用范围；只补实际剩余项。检查最终last增量与实际运行对象绑定，不为包格式重跑业务。真正充分即停；没有完成的门如实保留，不为根/时间将满伪造通过。

## 低内存执行调整（仅前向）

用户已要求按现有低内存串行推进，不再反复释放内存。本次将**唯一headless Chromium启动门前向调整为512MiB**，PG/API仍512MiB；不追认根20的768MiB门未过为已启动。仅一个Browser、一个context、一个page，模式串行复用，禁并行标签/第二Browser/PDF/preview/额外worker池；普通正式渲染/正常sandbox/认证不能关闭。

约1秒监测实际可用内存和自有进程工作集；连续两次<256MiB停止新增并精确清场Browser/API/业务树/PG。任何启动前实采仍<512MiB则不启动该层，记录当时时点和实际计数，不要求用户再腾内存，不机械反复采样等待。该有界尝试不保证本机一定可跑浏览器，未运行仍未验证。可以先完成不依赖Browser的PG余项，但不要持数据库空等内存或聊天。

## 前向许可、原期限和资源

许可TASK-120-Q-PREP-VALIDATION-04-20261019。当前原根20/20已经用尽；只有实际收到本卡和permit后才新增运行，原根不可重开。累计cap改为roots24、PGstarts24、APIstarts24、command wall28800秒；其余caps不变：Browser8、build6、Native48、HTTP5000、持有14400秒。最多4新根，从21起；这是剩余练习/权限竞态/UI及必要有据复检的余量，不是必须用满或可重复整批。

返回累计root20/PG19/API18/Browser3/build4/Native25/HTTP353、77失败记录与原117的81历史、wall保守21629.019209/25200、持有1593.890295/14400全部保留；新许可仅增加cap，不改已用/unknown/两笔7200预留，不把记录数当独立缺陷数。命令从050之后续号；同问题已失败次数跨轮保留，两次有据修正仍失败停止该问题并完成独立部分，不靠新增根机械撞。

新增容器/卷/库/活动ID/真实provider/费用/preview/Git均0。固定CID b89522070d4b64fc67efed810852ccc21948058f154bf4fa1889f4d8d69a102f，name retrolume-task120-qprep-pg1，volume retrolume-task120-qprep-data，image sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f；原permit标签保留，1CPU/512MiB/pids128/restart=no/无host bind。PG127.0.0.1:55480/API18120，仅原flow/budget01/budget02；对象缺失/漂移就停依赖，不替补，不查改旧六资源。

原首点2026-10-18T08:41:08.5687758Z、原96h截止2026-10-22T08:41:08.5687758Z和末1800保存不变；**flow/budget02的2026-10-19T12:19:22.457756Z（当日20:19:22+08）及原活动更早截止不延长，budget01为12:33:23.767900Z。** 本卡不刷新grant/重建实例恢复权利。收到后立即核实际有效余时，将有限阶段装进最短门，装不下不启动；过期只停相关动作并保存，不回头执行旧root或换库清账。

每根最多1800秒含末120清场，测试/build子批300、metadata单批60；计时按真实区间不重叠累加，不机械新增7200预留、不将未知记0。原正常审批继续适用，新拦截不换壳/模型/连接器绕过。

## 文件边界、收尾和回传

保持原完整卡产品允许/禁止范围及金融/权限/锁序；可修现有剩余fixture、必要同链产品缺陷，不另建通用平台或改001—014/依赖锁/schema profile/SUP/Job/时钟/用户私配。正式DocuS/公共库/共享编号仅主控维护。本卡普通执行可维护自身唯一账和新证据，不写共享状态。

新证据D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/execution/validation-04/；预算/events沿原execution唯一文件，旧as-run/失败/ZIP/报告不可覆盖。末次先停Browser/API/业务树，再停原CID；核PID/birth/Job、Running=false/Pid0、55480/18120无监听，保留全部数据和原对象，不drop/truncate/prune/批删。050的原停止证据只表示2026-10-19T10:39:53Z时点，不能代替新重开前/收尾核查。

完整结果仍D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-120-result.md，置顶续验04并保留旧全文原字节。交最终差异/源与fixture/as-run/dist身份、精确用例—原件映射、四组实际完成/未跑、金融前后读数/最终新连接快照、累计失败/投入/剩余和精确StopProof。source修补的建议状态与工程验收分开；稳定完整后主控另安排原118独立归属集中增强终审，本卡不自签。

无新增用户决定/密钥/SQL/内存动作，人工只需转交本同号完整卡。保存复读后回一句真实结论及可点击绝对结果路径。

---

# 以下为先前完整合同，原字节保留；与本次明确修订冲突时以上文为准

# TASK-120 / R-114 — 集中修复03：锁分类、未知态与剩余业务闭环（当前有效）

## 目标、接收者与交付

接收Agent：A+增强工程，继续TASK120原TASK119/117工程窗口，单一执行者，原运行已停止。真实客户端/模型照实登记，不因标签重新审已完工作；不委派、不启动独审、不新建TASK。

交付一个稳定完整的Q v2零外发工程候选：合并修复本次确定路径和同链夹具问题，补两域query→model→007/领域提交、旧learning/HTML、已选记忆、剩余权限/ACK/K2与五入口正式UI；普通修正卡内完成，统一回传。先定位并修正根因，再验证，不直接重开旧失败整批。以下附旧完整合同，未明确修订的A—D/Must/文件边界均继续有效。

本卡不是独立审计，不签STEP018整体/019/020/M1/项目或真实Q。Q继续冻结，真实provider、实际费用、preview、Git新增全0。未来100次/25元并未在本卡启用，不再要求用户提供key、SQL或释放内存。

## 项目、规则、依据与输入

根D:/shspic/project_NO3_RetroLume-agent；入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。task_model，锁定V4.0/公共AGENTS CHG-0003；公共只读根D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，DocuS/AGENTS.MD、WORK.MD适用task_model/核证/委派/预算/审计章节、task_model/TASK_TEMPLATE.md及prompts/07_开发执行循环.md；七指纹以DocuN/evidence/v4-migration-20260930/rules-snapshot.json为准，不自动采用新版。同窗已读未变材料复用。

当前需求v1.4、架构v1.49、执行动态v2.77；STEP018和原120关联继续。用户已批准119增量，主控在同一实施/零外发目标内前向续发附条件资源许可，没有新增真实费用、持久模型或公开权限。

按序只读变化及直接依赖：

1. D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-120-work-decision.md置顶03及同目录TASK-120-result.md置顶“断点纠正02”；不覆盖首轮/续作历史。
2. D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/orchestration-repair03-20261019/permit.json、input-verification.json。实际旧账为execution/budget.json、events.jsonl，当前16/16根、active_root/command空。收到本卡后才追加permit_history与caps，主控没有代改工程账，不追认过去动作。
3. execution/continuation-02/final-review-index.json、final-file-identities.json、final-stop-proof.json、retained-unknown-witness.json、fixture.diff、command-039/040/041.receipt.json，root15-diagnosis.json；root-16-c02-core-result.json及三份root-16-batch-06-ui-*-proof.json、root-16-batch-02-failure.json。已有失败和原件直接复用，不先重现。
4. backend/app/learning/teaching_adapter.py、activities/teaching_repository.py的_teaching_read_snapshot/read_teaching_command、activities/repository.py的_transaction、data_exit/q_store.py的method_name/is_read_method/async_policy、capabilities/q_gateway.py共享临界段；interview_repository.py的accept/abandon/goal；preview/repository.py的parent资格与learning/service.py的原输入/父槽守卫；相关最终夹具和冻结TASK116输入。

## 已定位问题与一次合并修正

### P1：教学只读调用被误分类为写操作

确定的代码链：q_gateway.call_with_policy先进入shared policy；gateway再调用validate_teaching_request；v2/v3路径调用read_teaching_command→_teaching_read_snapshot；_transaction用method_name得到“_teaching_read_snapshot”。现is_read_method只匹配read_/list_/inspect_/find_/q_snapshot及少量精确名称，漏该私有只读方法，导致申请exclusive policy；async_policy在继承shared时明确抛q_policy_upgrade_forbidden；adapter的except Exception统一返回teaching_validation_unavailable。这是可从源码确定的冲突路径，本次worker日志只录统一错误码，**尚不能宣称原运行已采到内部异常或唯一根因**。

按只读语义修正这条精确路径及实际直接受影响的同类读取；不得泛化为“所有下划线方法都是读”、对所有transaction跳过policy、放开写锁升级或移除结果事务排他锁。保留K2发送共享锁先释放、结果再排他policy→MutationGate→PG的顺序。

用最小定向检查证明真实方法闭包的分类/实际shared嵌套读取可达，且shared内真实写操作仍在SQL前被拒；覆盖无记忆的teaching.v3及有记忆v2/v3适用分支。替身只证明锁/控制流，不冒充PG事务；之后用真实PG/SUP补模型提交。若另有内部异常，按下面安全诊断捕获后针对性修复，不能猜字段或放宽守卫。

### P2：历史UNKNOWN并不会因新goal自动解除

interview.accept检查全部历史model UNKNOWN，包括obsolete项，先前主控“只建新goal即可”的安排不充分。原键430a4e36-08e1-411f-a73e-097506a6278b及新教学键3b561488-07b7-4d6d-8b98-05e793c96749绝不重发；原A1键1f5c659f-4a5a-4fee-bfbe-3f245eb5bc7e也永久保留。

准许在精确停止/当前PG回读后，对已停止的上述A2面试及A3教学实验命令通过既有本地abandon接口显式结束业务pending；须保存前后状态、真实新head/父和原Q claim/operation/预留原样保留的证据。abandon不释放旧semantic slot、不证明未送、不退款；不能SQL改unknown为not_sent/删除历史/清余额。随后才按原生产goal/版本规则创建合法新父，核所有历史unknown/未决operation/owner，不只看head。若仍被生产规则拒绝，保留准确原因，不换key撞旧槽。

### F1—F3：已知夹具前提一次收敛

- observer必须在正常TESTONLY应用装配前安装原最低传输替身；不能靠重跑C12隐式安装，也不能把外部transport误当合成。
- retrieval source_index/query可合法命中terminal/received缓存，按原键、原终态和真实结果资格核证继承；不一律索取pending approval，不二发已领取/未知请求。冷准备、合法缓存、部分接续三种输入状态应可区分，不弱化业务断言。
- creation-memory及其他已保存JSON显式UTF-8读取。budget02已部分初始化，不当空库；复用真实身份、root/grant、已有roster/来源/原保存业务键，按生产MemoryService和create_activity(memory_selection=...)补创建时选择。禁止重建库、重绑旧活动、延长有效期或生成任意记忆文字。

最终041只证明语法/冻结memory解码/schema和停机，不能算这些修后PG已通过；保留修前/as-run与新字节差异。

### P3：HTML/legacy的409先拿确切拒绝原因

原409未记录安全错误码，禁止猜验签或父域。夹具应保留有限结构的status、detail/error层code、terminal disposition和关联业务键/operation；不输出DSN、令牌、签名或任意异常正文。核原first成果的实际kind/版本/资格/segment，COMMIT不自动代表它是合法HTML answer父；核legacy followup的原规范输入、父资格和单槽。若须先用既有合法followup形成answer，就完成该真实步骤再生成HTML，不改生产parent/业务提示使不合格父通过。已存在正常HTML验签与九函数EOL修补直接继承，不再应用012/改schema profile，不启preview。

## 诊断、修复与运行次序

先离线完成上述源/夹具对账和已知修正，保存一张有限“当前真实状态→合法动作→预期结果→原证据/新证据”表，覆盖所有剩余C项。每个会消耗新Q claim的正例，先核全链的父、未知态、当前ness与结果类型；不能只核accept，再到worker才发现同链静态不兼容。

若旧原件仍不足以绑定教学异常或HTML/legacy拒绝，允许**至多一个只读诊断根**，总时长420秒含末120秒清场；仅原PG/必要API和冻结请求复核，不启Browser/业务SUP，不调用admit/mark/record/claim/真实传输，不POST新业务。可在独立测试进程对原validator捕获目标模块的异常事件，记录类型、DataError.code/SQLSTATE、相对文件/函数/行与SQL模板hash，禁止原始异常字符串/连接信息。保持失败关闭，不把捕获改为成功。原始症状已有充分绑定时跳过该根，不为凑流程再诊断。

真实PG/SUP及UI前必须先有：上述同链修正的有限差异、锁读/写反例及保存回执状态/UTF-8定向检查、UNKNOWN本地处理方案和HTML父/错误码核对结果、完整有限计划与预留清场时间。诊断不能收敛则不启业务正例，完成独立可交付部分后停止并带准确缺口；不再用UI循环定位worker内部异常。

修正稳定后按正常PG/HTTP/SUP→剩余ACK/K2/权限反例→最终UI推进。正常教学/面试/legacy/HTML及已选记忆正例先成，再做会失效scope/source/memory/head/revoke的破坏性竞态；保存正例身份，避免后例先破坏前例前置。GET仍无副作用、批准仍本机operator精确全文、POST继续仍原键。三种ACK、foreign-instance/artifact/log/readonly等只补原矩阵实际未足项，不因保存了脚本就通过。

最终UI只有后端正例已闭合才进入相应模式；独立模式可单独推进。浏览器对已提交父只读核证后继承，不为重复证明而再model。核正式JS/CSS响应hash及五入口的等待/刷新仅GET/批准/同键显式继续、owner/view/head/scope/namespace/DataContext晚到围栏。旧三浏览器FAIL不改绿，加载hash子事实直接继承，产品未变不重复build；前端产品实际改变才绑定新正式build。

不在PG持有时等待聊天投下一批。每根启动前冻结有限阶段、依赖、总时长和as-run；独立子项不被无关失败阻断，但同问题两次有依据修正仍失败/前提推翻即停该问题，不机械重试。普通修正卡内合并，充分即停。

## 原证据复用与范围

C12原共同99→100双backend同锁、达限双provider拒绝、root12/14同库重开100/25000000和三R0不重跑；旧R300已核销不再处理。旧learning first COMMIT、既有embedding、九函数EOL与普通角色指纹、未变S有限验收直接继承。

本轮产品增量0属断点事实，未来本卡修复允许原120批准产品边界中的teaching_adapter/teaching读取、q_store精确读分类、同链Q/业务薄接线与必要测试；不得借此改金融主模型、历史原件、001—014、正常profile、SUP/Job/时钟、依赖锁或用户配置。公开接口/持久模型/权限模型若需改变，完成不受阻部分后交具体最小差异，不自行扩大。原完整允许/禁止文件附后，正式DocuS/公共库与共享CHG仅主控写。

## 附条件资源许可与停止

前向许可TASK-120-Q-PREP-REPAIR-03-20261019，只有收到本完整卡和permit.json才登记；原16根全部已用且保持，不能重开旧根。

| 项 | 返回累计 | 新累计cap | 前向新增 |
|---|---:|---:|---:|
| 根 | 16 | 20 | 4 |
| PG启动 | 15 | 20 | 原cap16→20，增加4 |
| API启动 | 11 | 20 | 原cap16→20，增加4 |
| Browser/build | 3/4 | 8/6 | 0 |
| Native/HTTP | 13/240 | 48/5000 | 0 |
| 命令wall保守秒 | 17789.126332 | 25200 | 原cap21600增加3600 |
| 持有并集秒 | 1258.061295 | 14400 | 0 |

四余根是同一完整修复目标的上限，非必须用满：至多一根只读诊断，其余仅用于通过前置后的正常闭环和剩余验证。一个完整正例仍在同一确定前置处失败时，不继续启动三个UI复制该失败。57失败记录及原117的81历史、所有旧投入/两个7200未知预留保留，不当独立缺陷数；旧原首点/所有失败/未知账不清零。新计时按真实起止/区间，不机械另加固定7200，不将未计量记0。

每正常根最多1800秒含末120清场，测试/构建子批300、元数据单批60；受总wall/持有/有效期最短门限制。新根从17、命令在041之后续号；038仍未执行，039—041已真实成功，自动审批容量目前已恢复，不继续以旧容量错误当阻塞，不换通道绕过任何新拦截。

唯一CID b89522070d4b64fc67efed810852ccc21948058f154bf4fa1889f4d8d69a102f，name retrolume-task120-qprep-pg1，volume retrolume-task120-qprep-data，image sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f；原permit标签TASK-120-Q-PREP-IMPLEMENTATION-20261018保持。1CPU/512MiB/pids128/restart=no/无host bind，PG127.0.0.1:55480/API18120；仅原flow/budget01/budget02，不新增/替补容器/卷/第四库或活动。失踪/身份不符则停相关层，不查改旧六资源。

原首工具2026-10-18T08:41:08.5687758Z、原96h截止2026-10-22T08:41:08.5687758Z不延长；最后1800秒仅保存。TESTONLY flow/budget02的2026-10-19T12:19:22.457756Z及budget01的12:33:23.767900Z、活动期限仍须实际核较早门，不刷grant/换实例恢复旧权利。到期只停止依赖动作并保存，不用本卡延长权限。

PG/API最低512MiB、Browser768MiB、约2秒采样连续两次<256精确清场保持；不要求用户再释放内存。本轮最低835289088 bytes且无压力事件，不能再把已发生业务失败归内存。每次实际启动尝试照账，包括未ready。

## 收尾、成果、审计与回传

原041在2026-10-19T05:54:10Z已核120 PID/birth、58 Job、精确CID Running=false/Pid0与两端口无监听，并另有041自身tree_empty/exit0；这仅是当时时点，不冒充主控实时查询。新启动前/结束后均精确核身份/停止，最后先停Browser/API/业务树再停CID，保存全部维度；保留容器、卷、数据，不drop/truncate/prune/批删。

唯一工程账仍D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/execution/budget.json与events.jsonl；新增证据execution/repair-03/，旧根/失败/as-run/报告和ZIP不可覆盖。完整结果仍D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-120-result.md，新轮置顶且旧全文原字节保留。输出锁分类根因/修复/反例、业务未知处理/原领取不二发证明、C01—C15/原矩阵逐项证据/未跑、最终源码/fixture/dist/as-run身份、准确累计账和精确StopProof。

稳定完整后主控再安排原118独立归属集中增强终审，不在本卡自审自签，不把诊断当独立审计；未成则带真实失败与最小剩余缺口，不以“语法通过/已保存”代替完成。无需用户新决定；用户仅人工转交本同号完整卡。保存复读后只回一句真实结论与可点击绝对结果路径。

---

# 以下为先前合同，历史原字节保留；与本次明确修订冲突时以上文为准

# TASK-120 / R-114 — 断点纠正02：补合法测试起点并完成剩余成果（无新增额度）

## 目标、窗口与当前许可

接收Agent：A+，继续TASK120原TASK119/117工程窗口；不新开实施者，不委派，不启动独审。本次纠正上一续作01两处不可行测试安排，沿已采用完整Q v2成果继续，正常实现/修复/相关验证卡内连续完成。交付仍为一个稳定、可集中独审的零外发完整工程包，不能把本次只当准备报告。

此段优先于以下历史中的A1两步切目标、budget-02用途限制及“共同100门待跑”表述；未改原A—D、Must、安全合同和允许产品文件。**没有新增预算，没有新TASK，没有新真实Q授权**。现有许可TASK-120-Q-PREP-CONTINUATION-01-20261019及原许可均在后文，保持同一budget/events、全部失败和原首点。

## 项目、规则、依据和最小输入

根D:/shspic/project_NO3_RetroLume-agent；入口同根AGENTS.md。锁定V4.0/公共AGENTS CHG-0003，公共根D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，DocuS/AGENTS.MD、WORK.MD第2/5/6/8/9章、task_model/prompts/07_开发执行循环.md和TASK_TEMPLATE；同窗未变复用。七锁定指纹在DocuN/evidence/v4-migration-20260930/rules-snapshot.json，本轮一致；不采用后来公共版本。

口径需求v1.4、架构v1.48、执行动态v2.76，STEP018及原TASK120全部关联。授权仍为用户采用119包，范围为合成/零外发实施与验证，真实provider/实际费用/preview/Git新增0，Q冻结。资源标签不冒充模型身份。无需用户密钥、SQL或释放内存。

按序只补已变部分：

1. D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-120-work-decision.md置顶02和同目录TASK-120-result.md续作01；本次主控已直接明确两个测试安排，**不要再询问是否可用A3或预留budget-02**。
2. D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/orchestration-recovery-20261019/input-verification.json、scope-clarification.json；原资源permit仍在orchestration-continuation01-20261019/permit.json。本文后附全部旧合同，可脱离聊天执行。
3. DocuN/evidence/TASK-120/execution/budget.json、events.jsonl、case-index.json、remaining-readiness.json和continuation-01/final-review-index.json、final-file-identities.json、automatic-review-block.json、final-stop-proof.json。旧as-run/未执行标记/原报告后缀保持；不要执行旧root或重写旧计划原件。
4. backend/app/activities/teaching_repository.py的apply_teaching_local槽判定在效果前、teaching_contracts.semantic_slot，repository.create_activity记忆绑定，interview_repository.apply_interview_local/_interview_replay，及已保存flow/setup/integrated/pg_boundaries/UI夹具；只补这次直接依赖，不全仓重读。

## 已通过直接继承，不重跑

真实C12：budget-01原99→100双backend同锁竞争、两provider达限拒绝、root12/14同库重开100/25000000，三活动48/28/24且R0；对应budget-last-slot-race.json和root-14-budget-reopen.json。旧R300已经生产折叠，不能再核销/退款。旧learning原键COMMIT、原embedding索引/查询、9函数EOL修补及普通角色指纹检查均按原对象继承，不再应用补丁/012或重复全套业务。

最终前端源码/dist本轮未变，继承原typecheck/build及四文件hash；这不是浏览器通过。q_context/q_protocol两产品修补仅15项定向检查通过，面试真实链仍须跑。根15/16及最后预检没有执行，不能按已通过使用。

## 一次补齐两个合法起点

**教学：采用原flow固定A3=01800000-0000-4000-8000-000000000003。** 原A1的相同goal no-op已COMMIT，占据revision1 goal槽；上一主控concept→numeric处方撤销，不再尝试该槽。A3仍沿同grant/Nscope/24次与6元合成分额/原deadline，保留其旧learning COMMIT，不清额度。先只读核A3无teaching/interview互斥head、范围/余额/时间合法，再通过原生产local goal建立真实head，固定一次新业务键，回读记录/版本后正常query→精确准备/批准→同键显式model→007/领域提交及需要的后继。旧A1 UNKNOWN键1f5c659f-4a5a-4fee-bfbe-3f245eb5bc7e及其父槽永久保留，不重发、不换文字绕槽。若A3实际有冲突则停此例交具体事实，不能暗建第四活动或改生产槽。

**已选记忆：准许原allowlist内尚未初始化的retrolume_task120_budget_02作记忆专用TESTONLY库。** 仅原CID/卷内第三库，不新容器/卷，不重建旧库/换source或readonly权利。初始化前就固定A2=...0002的scope、TASK116冻结memory_body及选择；经既有生产memory保存/选择接口，再create_activity(memory_selection=...)一次绑定。固定全roster与100/25、48/28/24分额不变；manifest只沿原冻结输入，不扩文字白名单。新TESTONLY根/活动的valid_until/deadline不得晚于原flow的2026-10-19T12:19:22.457756Z，不延长旧根，不出具真实启用物。正例证明实际选择记录/完整请求中有限memory来源及一次合法模型提交，反例沿原有限来源/撤销矩阵；不因新库独立而称旧budget-01总账恢复。不重复100门，不增加库对象上限。

**面试/HTML：** 原flow A2的旧claimed UNKNOWN430a4e36-08e1-411f-a73e-097506a6278b不重发。源码面试goal确实产生新版本，按真实当前head/槽先提交local goal并回读，再准备新ask和query；不能仅改key。HTML仅补原learning成果的description，继承已修9函数，不启preview、不改profile。

## 剩余完整交付及有限执行

先将上述教学/记忆真实父、面试、HTML、ACK/K2/有限权限反例、五入口最终UI全部落进同一有限用例—依赖—原件表，再运行。当前plan-root15仅core面试/legacy_html/ACK和两种UI，**没有教学和记忆，不能当完整计划**；保留旧未执行计划，保存修正版本与hash。不要再次以“等待主控决定测试活动”为由启动/清场/返回。

独立阶段只依赖实际需要的父，不用一个未成教学阻断整个面试/HTML/UI。共享一次正常API和PG生命周期，阶段均在根内自动执行；每个成功/失败和源as-run独立留证。父已COMMIT时GET核证后继承，不再发送；新请求保留完整原键/批准/实际费用预留/007和领域结果，不以替身或隔离断言冒PG。

最终浏览器实际加载正式bundle并核响应hash；覆盖五入口等待/GET无副作用/原键继续及本卡新v2 owner/view/head/scope/namespace/DataContext晚到围栏。同阶段普通夹具修正可在卡内处理，不弱化正确断言。源码不变不重复build；前端产品实改才用剩余build绑定新字节。只跑原矩阵实际缺项，C12/旧S闭环/原未变审计不重复。

根15优先完整正常PG/SUP及权限/记忆/ACK-K2，根16仅确有必要的未成增量及UI；允许合并，两个余根不是必须用完。启动前冻结每根有限阶段与总时长，必须装进真实剩余截止及清场预留。不依赖PG运行时聊天投批，不将未执行计划当通过；相关同问题两次有依据修正仍失败须停止该问题，保留独立成果。

## 平台、资源、预算和停止

command038的自动审批服务原文为“Selected model is at capacity”，executed=false，未占根，无receipt。**它不构成需要新增预算的理由。** 原正常审批通道恢复后才提交更新后的必要预检，保留原阻塞记录，执行回执用独立新标识；不切模型/shell/连接器绕过，不反复发命令探测服务。服务未恢复时可做授权文件编辑/保存，不能运行被拦动作或下游。

当前counts/caps：根14/16、PGstart13/16、API9/16、Browser0/8、build4/6、Native9/48、HTTP54/5000；44失败记录及原117的81条历史保留。命令wall保守17553.845332/21600、持有1150.108295/14400；原两笔7200未知预留保留，不冲销，也不因换轮机械新增同额或重复计同一覆盖区间。未来受控命令实计、新未测量投入列实际边界上界，手工总工时不冒充0。主控没有改工程账；执行者收到本明确范围修正后append-only记采纳，计数/时间cap均不改。

固定CID b89522070d4b64fc67efed810852ccc21948058f154bf4fa1889f4d8d69a102f，名称retrolume-task120-qprep-pg1，volume retrolume-task120-qprep-data，image sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f；标签沿原TASK-120-Q-PREP-IMPLEMENTATION-20261018；1CPU/512MiB/pids128/restart=no/无host bind。PG127.0.0.1:55480/API18120。缺失/不符不替补，不碰旧六资源；逻辑库仅flow/budget01/budget02。新增create/真实费用/provider/preview/Git0。

最新Docker实时inspect曾permission denied，只继承09:47原停止；最新PID/Job/两端口观察不代替当前Docker状态。任何重开前先正常完成精确身份/状态检查，无法读则不启业务。PG/API最低512MiB、Browser768MiB，约2秒采样连续两次<256精确清场；不要求用户再释放内存，不关守卫。不满足只停相关层，不宣称“下一次一定成功”。

原首点2026-10-18T08:41:08.5687758Z、原截止2026-10-22T08:41:08.5687758Z不变，末1800仅保存清场；grant/活动更早截止不延长。每根1800秒/末120清场、元数据单批60秒/测试build子批300秒上限保持，按各层最短剩余门。过期不换库刷新批准，余量不够完整步骤不开始。

允许产品/测试文件范围、禁止001—014/依赖/锁/正式DocuS/公共库/旧证据/用户配置、SUP不触账、所有出站与金融主契约，均严格沿下方原完整合同。本卡不扩大公开接口、持久模型或正常启用权。新只写执行continuation-02子目录、原唯一账及指定结果，旧原件不可覆盖。

## 收尾、审计与回传

结束精确停本任务Browser/API/业务树，再停原CID，核PID/birth/命名Job、Running=false/Pid0、55480/18120无监听，保留数据/容器/卷/失败，不批删/drop/truncate/prune。若某维不可复核就明确时点及未知，不称全清场。

完整结果仍D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-120-result.md，新轮置顶且旧续作01/首轮原字节保留。交C01—C15及原最小矩阵逐项证据/复用/未跑、最终源/构建/fixture身份、准确累计账及精确StopProof；新模板/控制器最后未跑要标清，不以保存完毕自签通过。稳定完整后主控另安排原118独立归属集中终审，不逐小项审计，不自签Q/STEP018/019/020/M1/项目。

无额外用户决定/密钥/SQL/内存操作。用户人工转交本同号完整卡即可；平台容量无法由本卡保证。保存并复读后只回一句真实结论与可点击绝对结果路径。

---

# 以下为续作01及原合同，历史原字节保留；冲突以以上明确修正为准

# TASK-120 / R-114 — 续作01：Q v2完整工程与剩余PG/UI合并闭环（当前有效）

## 目标、接收窗口与完成终点

接收Agent：**A+增强工程，继续刚返回TASK120的原TASK119/117工程窗口**。这是同一未验收成果的完整接续，不新占TASK、不启动独审、不重新设计。真实客户端/可知模型如实记；不因标签追问已完工作。不自动委派子Agent、不并行第二实施者；只有原窗口确不可用，才允许同等胜任A+新窗独占接续，原窗停止。

一次完成剩余教学/面试query→已批准model→007及领域COMMIT、旧learning/HTML等待与原键继续、权限/丢确认/K2并发、真实PG共同100门和最终正式bundle UI。范围内普通实现/夹具修正、定向验证、精确清场连续做完，达到完整稳定可审包再统一返回。已有足够证据直接复用，不把本卡拆成修一个fixture/补一项的小卡。

你只交事实与工程候选，主控裁定。**Q继续冻结，真实provider/费用/preview/Git新增均0**。未来100次/25元是用户已采用的条件上限，不是本卡可花费用，不需用户重批/给key/释放内存。真实账号、计量、返回身份及正常启用门UNKNOWN不阻塞零外发工程，但不能伪填为ready。

## 项目、规则、优先级与输入

根D:/shspic/project_NO3_RetroLume-agent；入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。task_model，锁定V4.0/公共AGENTS CHG-0003，七指纹仍全部匹配；公共只读根D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，DocuS/AGENTS.MD、WORK.MD第2/5/6/8/9章、task_model/prompts/07_开发执行循环.md与TASK_TEMPLATE。原窗已读同版内容复用，仅补变更。

本次口径需求v1.4、架构v1.47、执行动态v2.75，STEP018关联原TASK120全部需求/架构/父项。采用仍为用户2026-10-18对119完整包的批准。**本置顶续作01及本段permit优先于下面原卡相应运行额度/调度/Git公开范围旧描述；其余原A—D、完整最小矩阵、产品允许/禁止文件继续有效**，不是重授未列权限。

按序读下列真实文件，已读且未变不重读全部：

1. 根入口、锁定规则及DocuS/执行动态文档.MD置顶、架构动态文档.MD置顶。
2. D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-120-work-decision.md及同目录TASK-120-result.md，后者是本次交回原件，不能覆盖历史。
3. D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/orchestration-continuation01-20261019/input-verification.json、permit.json。本次642文件/修改前副本、4 bundle、ZIP全匹配；它们就是接续基线，不用GitHub6302b0c覆盖本地新成果。
4. D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/execution/下budget.json、events.jsonl、case-index.json、remaining-readiness.json、final-stop-proof.json、root08-next-batch-timing.json、root08-unexecuted-next-batch.json、flow-committed-receipts.json、final-file-identities.json、source.diff和final-bundle-identities.json。只读旧失败原件，不执行旧晚到指令。
5. 下面原卡完整A—D/原许可及TASK119采用K1/K2原件；同窗未变直接继承。原TASK116 sample-inputs冻结文字和实际finite/provenance仍有效，不自行扩大文字白名单。HTML TESTONLY许可沿本次html-testonly-adoption.json/command021正常host身份，不准启preview。
6. 当前backend/tests/fixtures/task120/flow.py、budget.py、merged.py、ui.py、run.py、resources.py，DocuN/evidence/TASK-120/execution/runtime_control.py及command_control.py只读作旧控制依据；实际teaching_repository.py的local goal/no-op、semantic_slot与claim/结果路径，q_context/q_store/主进程与worker锁路径。只补直接依赖，不重审整仓。

## 已收存、真实断点与必须先修的同链问题

本轮原报告是**未完成**。19项定向、2项正常配置与typecheck/build有原exit0；多为隔离证明，非真实PG currentness。3条embedding实链（一次source_index/两次query）有原HTTP/Windows/PG/007/领域提交；root08-batch01仅flow/budget夹具后来改变、产品无差，batch02与最终被测表一致。这些事实保留，不为补model再次重跑原成功三条，除非新差异确影响其路径。

原账8/8根、PGstart7/8、API5/8、Browser0/8、build4/4、Native4/32、HTTP31/3000；25条失败登记含根/子批重复引用，不等于25独立缺陷。旧UNKNOWN键1f5c659f-4a5a-4fee-bfbe-3f245eb5bc7e已claim，不能再发，原PG只读观察时operation/请求费用预留0不等于现在可放行/可清账。旧budget运行R300的原耗时未知，不能当0或退款。

先一次修正整条fixture和调度链，不能只把第一处错误改到下一处再停：

- **合法新父槽（C09及后续C11/UI共同前提）**：abandon UNKNOWN不释放其语义槽；teaching_repository.py625—637相同goal body确为no-op，换business_key不能改变父。可在原固定A1/原grant内，通过两个明确、合法、冻结文字的本地goal动作形成真正不同父，例如仅本地先切到已有concept_goal，再明确回到numeric_goal；中间不发送概念模型、不改N资料范围。canonical request含实际expected revision/goal version，semantic slot绑定真实父；每步回读确认record/revision/goal_version确变化，最终仍是数字目标/N来源，再准备新的独立意图。该例是已授权fixture细节，不能改业务no-op规则、改semantic_slot、重绑活动或SQL清UNKNOWN。若实际原资格/版本不允许，不硬做，不换grant重试。
- 所有旧retain键、旧冻结body、失败命令和UNKNOWN保持；不要把已缓存expected_revision=1的请求就地改成新body。新场景名/新意图只在真实新父成立后生成，旧未claim原键只有完整冻结体和当前资格都合格才原键显式继续。预先对账正常plan/exercise、release-gap plan、UI后继的全部父槽；不能修好首次plan后又在同父重复plan。
- **预算顺序（C12）**：先accepted/准备/真实operator批准及launch资格，再claim lease执行；按真实monotonic在窗关闭后settle，下一笔再accepted。未结算的旧R300先核旧身份/过期及原StopProof，只有生产原过期折叠或既定保守取消规则可核销；不伪造过去elapsed，不手改活动/operation金融行。已有budget.py修正是候选不是已跑证明，必须读实际生产函数对账全循环、最后竞争与post100探针。
- **消除60秒外部投批依赖**：原merged.py等外部写下一文件60秒后退出，root08 budget文件晚到退出9.240832秒，没有child/receipt。续作在启动前固定有限阶段列表、前置/依赖、单批上限和失败分支，由根内控制入口自动串行执行；不启动PG后再等下一次聊天/工具提交文件，不沿旧root08恢复。每阶段保留真实previous exit/独立as-run，不能硬设0跳失败；某链失败只阻其真实依赖，预算/已满足前提的UI等独立目标可在同根原期限内继续。新故障需修正时先确认该阶段子树已净；原根deadline不延长。

旧两条失败路径不清零。此次继续的依据是上述函数级事实、真实父槽计划和有限自动队列；若新路径仍落回同一unknown_slot且无新的可核解释，立即停该相关链，不继续换键撞槽。新问题两次有依据修正仍失败的停止规则继续。

## 一张卡内的剩余完整成果与证据标准

继续完成原卡全部未满足矩阵，不能只跑下面摘要后称整卡通过。用实际case ID/方法/场景写出已有覆盖、这次补证和仍UNKNOWN：

1. **五入口正常链与恢复**：教学、面试各至少一条实际query已提交→model pending→GET不写→operator逐请求精确批准→原冻结key显式POST→真实Windows SUP/worker→生产admit/mark→007与领域COMMIT。旧learning与HTML description各一条等待/GET恢复/原键继续；同key异体409、未批准零发送、claim/UNKNOWN不重发、准备ACK/claim ACK/COMMIT ACK分别只读对账。既有3 embedding成功引用旧原件，仅新必需query新增。全部供方实际网络由最低transport替身封闭，真实供应商/费用0。
2. **有限来源和新权限反例**：已选memory正常model至少一例；未批准answer/history/memory/标题、foreign parent/实例副本、artifact缺/日志换身及相关readonly/恢复拒绝按原最小矩阵补足。完整request/provider对象/实际规范发送bytes及parent资格都核；不可把隔离字符串检查或旧S08当新v2 PG通过。原wire3/v1充分原件继承，原wire4只补新传播实际影响，不默认全仓回归。
3. **K2实际竞争**：正常model结果必须可落地；source/memory/scope/head/revoke按受影响边界给真实锁/屏障窗口，分开临界前拒绝、已准入NOT_SENT、可能已送UNKNOWN。尤其共享发送锁释放后排他变更先完成，007不可变结果及费用保留、head不误推进；两端线程/PG connection身份与时序可辨别，不能外层串行冒并发。main.selection_guard Q短锁、launcher父data permit释放、owned_service Q注册缩短要证明直接传播，不借改非Q生命周期/恢复规则解死锁。
4. **真实共同100门**：优先原budget-01，不清其历史。逐笔生产真实准入47/28/24→SUM99/24750000，两provider在同A1合法lease争最后slot，真实两backend/同固定全局advisory锁/原SUM/同事务预扣COMMIT，最多一个成功；新独立连接最终100/25000000，输方零发送，达100后两provider拒绝、账不变。UNKNOWN/超时/已准入确定NOT_SENT都保留费用。实际停止再同库重开核权利不复活。原budget-02只在第一有具体修正且确需隔离复证时按原许可初始化，旧库保留，不是新收费余额。不可伪造99但两个活动都余一slot、或99次已25元等不可达前提。
5. **最终UI与正式字节**：源未变的最终JS 7cd5ed25…456b07、CSS6f02da29…9e8b94及index/PDF worker哈希可复用正式build；不要为恢复对话重build。若实际frontend变化，受新build额度约束重建，绑定真实Browser响应JS/CSS hash。教学/面试等待批准后显式继续、检索批等待、legacy/HTML恢复入口、刷新/重开仅GET、draft保留，旧owner/view/head/scope/DataContext/namespace迟到不推进/不额外POST。请求时间线锚定显式动作，避免把显式POST本身计作“之后自动POST”的旧夹具错误。仅description，不启动固定preview。
6. 最终实际SUM新连接回读、case-index/readiness、原/新差异及pre/post/as-run、最终包和StopProof齐备；成功按子项实际字节分级，任何旧失败批不改绿。正式最终稳定点后才交主控安排一次独立增强审计；不在本卡自签，不提前让独审窗口参与修实现。

## 允许修改、所有权与禁止

下面原卡允许的产品/前端/测试/配置示例/README/deploy说明范围保持，仅新协议和直接影响的必要修正；修前preimage/hash，差异能追溯A—D。现代码/最终bundle是候选，不以“只是验证”拒绝卡内必要普通产品修复，也不借机改业务提示/推进标准。

现行backend/tests/fixtures/task120可改，保存本轮preimage和fixture.diff；前端夹具仅task120-*.mjs。主控本段orchestration只读。旧roots01—08、command001—028、旧source.diff/ZIP/receipts原件不覆盖；旧runtime_control.py/command_control.py如需改控制，先封存其hash和原字节，再在D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/execution/continuation-01/保存明确新控制副本和计划，纠正文件层级ROOT/manifest路径，不跑旧晚到指令。产品不能import这些临时控制；唯一实际账仍为原execution/budget.json及events.jsonl，新的permit_history追加，不平行第二本活动账。

原始需求、DocuS/共享CHG、公共库、001—014/金融模型/角色profile、旧source与恢复selector、固定renderer/host/Job/时钟主体、依赖锁/安装/联网模型保持禁止。新的公开权限、主要模型、DDL或持久金融语义变更须停依赖并报具体最小差异。原非Q锁/兼容不顺手改写。禁止直接SQL改请求/费用/预留、清日志、revoke冒独立delete、手动重绑grant或用新实例刷余额。

Git项目范围已由用户2026-10-18更新为除.gitignore外均可公开，主控已同步main；这覆盖下面原卡“不上传DocuN”的旧全局表述，但**不把Git执行授权移给本卡，Git写额度仍0**。源码可能比公开快照新；不得checkout/reset用Git旧版覆盖候选，也不得上传私有目录或输出凭据。

## 前向追加资源许可与原账继承（必须精确执行）

许可ID：TASK-120-Q-PREP-CONTINUATION-01-20261019，完整机读文件D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/orchestration-continuation01-20261019/permit.json。主控已批准本表的零外发续作，不再向用户索要同一预算批准；收到后先核原账与原停止证明、实际资源身份，再把许可ID/时间/原cap/新cap追加到原budget的permit_history，保持counts/roots/events/failures全部旧前缀和首点。主控未代改工程账，不追认此前超限或未执行动作。

| 项目 | 本次返回已用 | 旧上限 | 新累计上限 |
|---|---:|---:|---:|
| 真实运行根 | 8 | 8 | **16**（新根从9） |
| PG starts | 7 | 8 | **16** |
| API starts | 5 | 8 | **16** |
| Browser starts | 0 | 8 | **8**（不追加） |
| 正式build | 4 | 4 | **6**（仅确实需要时） |
| 真实业务SUP/worker会话 | 4 | 32 | **48** |
| HTTP | 31 | 3000 | **5000** |
| 命令wall保守累计秒 | 9538.921332 | 14400 | **21600** |
| 自有资源持有并集秒 | 267.641 | 10800 | **14400** |

新增create/实际容器/卷/preview/provider/实际费用/Git均0；旧create未用余量在本续作也不用于重建。8根是余量上限，不是必须用满的计划：尽量将可共用PG生命周期的有限阶段合并，新增根只因明确需要/修正/阶段隔离，充分即停。

唯一CID b89522070d4b64fc67efed810852ccc21948058f154bf4fa1889f4d8d69a102f，retrolume-task120-qprep-pg1；卷retrolume-task120-qprep-data；image sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f，原label含retrolume.permit=TASK-120-Q-PREP-IMPLEMENTATION-20261018保持（新许可不会逼你改标签/重建）。固定PG127.0.0.1:55480/API18120、1CPU/512MiB/pids128/restart=no/无host bind；逻辑库仅原flow/budget-01及有条件budget-02，CID/卷/金融行/unknown/journal保留。精确对象丢失/身份不符就停依赖，不建替补，不查改旧六资源。

原首工具2026-10-18T08:41:08.5687758Z，**原截止2026-10-22T08:41:08.5687758Z不延长**，最后1800秒仅保存/清场。已有TESTONLY不可变grant及活动deadline可能更短，先核自己fixture有效期，不延长、不重绑；到期不能刷有效期或另换库恢复权利。每根最多1800秒、末120精确清场；离线元数据单批60秒/测试build子批300秒，各层按剩余日历/命令/持有/计数/fixture权限最短截止，不拿跨中断日历差当CPU。

旧1840.326332上界、7200未聚合元数据不确定性预留继续占账，9538.921332不是精确投入，不冲销；手工阅读编辑unknown不能记0。新的runtime控制副本要将原硬编码10800持有门改为明确读取本许可14400上限并受原账约束，不能改成无限/default免费；记录实际源diff。命令从29续号，新证据加continuation01或新root前缀，旧失败25条及TASK117原81条保留，不拿新轮次清次数。

PG/API最低512MiB，Browser768MiB；约每2秒采样，连续两次低于256MiB停止新增、精确停自有Browser/API/业务Job/PG。内存/系统端口门不满足只停相应层，不反复要求用户释放内存，不改系统保留端口/杀占用进程/重启Docker；没有实际运行不假造通过。每次启动尝试包括未ready计数；离线只读/hash/edit不是运行根，任何实际runtime都从有界入口计根，不借裸命令绕账。

## 整卡顺序、停止、集中审计与回传

先保存本次fixture完整修正和有限计划，做必要小范围离线控制/槽身份/字节检查，再用当前实际可执行入口串行跑PG/HTTP/Windows/最终UI和budget，独立子目标不被无关单个失败全挡。启动计划必须已经齐全，不持PG等待外部工具再投下一批；先算完整阶段时长能否装入原根剩余，装不下准确收尾后用真实余根，不能超时外塞指令。运行不可能由静态检查保证首遍成功，未知按事实处理；不是再写准备提案后停。

完整充分即停。相同问题已有失败/修正次数跨轮保留；无新依据不再机械重试；两次有据修正仍失败、根因不稳、主要前提/新权限模型变化或硬门到达，停受影响部分并完成可独立工作后统一回报。平台审批拒绝记录并停止该动作，不换壳/提权绕过。任何StopProof不完整先处置精确本卡资源，不再开根。

末次先停本卡Browser/API/业务树，后停精确CID；核PID/birth/命名Job、容器Running=false/Pid=0、55480/18120不监听。保留数据/原件，不prune/drop/truncate/批删。主控只继承原停止时点，不声称替你实时清场；你在本次重开和最终停线必须更新真实证据。

完整结果仍为D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-120-result.md，置顶“续作01”，**本次返回正文完整原字节保留**。新证据DocuN/evidence/TASK-120/execution/continuation-01及原唯一账；旧原件只引用。给最终源/构建/fixture差异和as-run、C01—C15及原最小矩阵逐项映射、正确SUM回读、失败/投入/余量/偏差、精确StopProof、工程与真实Q readiness分开、独审输入索引。

稳定完整后由主控另卡集中独审，优先原TASK118独立归属，未占新号、不在本卡自签；旧充分证据不全量重做。README/部署说明/架构建议如实列，DocuS及CHG由主控维护。没有必要用户密钥/SQL/内存操作；用户仅人工转交本卡。完成保存并复读后只回一句结论与可点击完整绝对结果路径，不贴完整长报告，不宣告STEP018/019/020、M1、项目或收费Q通过。

---

# 以下原TASK-120合同原字节保留；与上文冲突处以上文明确续作/用户授权为准

# TASK-120 / R-114 — Q逐请求批准完整接线与零外发验证

## 目标、接收者与完整成果

你是本卡A+增强工程执行者，继续刚完成TASK119设计的原TASK117 S08工程窗口。一次完成已采用Q v2协议的产品实现、所有受影响入口与界面、正常和拒绝路径、真实PG共同预算证明、最终bundle传播、必要普通修复及精确清场。不是再写一轮设计，不是先开真实Q。整卡达到稳定可审成果后统一回传，不按准备、修夹具、补一例拆小卡。

可观察完成标准是：在一份不可变v2根及实例绑定下，后继请求使用上次真实持久提交的有限结果，实际完整请求经本机operator精确批准后，原键显式继续可以成功；未批准／失效／未知事实不发送；所有准入仍由同一个生产PG事务中的固定roster SUM、锁及原活动／operation预扣决定，已消费或unknown不借批准重发。教学、面试、检索、旧learning和HTML的等待／GET／显式继续均完整落地，旧v1与非Q行为兼容。

本卡全部真实provider调用及费用为0。用户已批准未来这一份Q最多100次／25元，但本卡没有首次启用回执，也不得填真实有效期、配置真实key或执行付费。未知官方／账号／计量事项只使真实Q readiness关闭，不阻塞本卡零外发实现与合成验证。

交付为正式产品／测试／必要配置模板和用户说明、可独立重建的最终差异与验证原件，以及D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-120-result.md。建议状态只能写工程候选；独立审计和最终裁定归主控。

## 项目、规则、采用与窗口

项目根目录D:/shspic/project_NO3_RetroLume-agent，入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。模式task_model，V4.0，公共AGENTS修订CHG-0003，锁定七指纹见D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/v4-migration-20260930/rules-snapshot.json。公共只读根D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4；读取其DocuS/AGENTS.MD及WORK.MD第2章task_model、第5/6章合同与状态规则，适用task_model/prompts/07_开发执行循环.md。不自动采用公共库后来版本。同窗已读且指纹不变则复用。

需求v1.4、架构v1.46、执行动态v2.73。父STEP018，关联STEP006/008、FR004/FR006/FR009/FR011、NFR002/003、SEC001/002/003、TASK116 AP1/AP2、已验收有限S的TASK117/118、TASK119/R113。编号只作追踪，不将所有关联父STEP判为完成。

授权依据为用户2026-10-18对主控三项合并增量提案明确回复“批准”；具体不可变提案及采用回执见本卡orchestration目录。采用包括零DDL的Q v2本机精确批准及响应／wire细化、候选deepseek-flash、未来100次／25元条件总门。原116用户“一并批准”的其余限制持续。采用不是官方、账号、计量、独审或真实语义通过，不是付费即刻授权。

优先原TASK119工程窗承接，原因是涉及私有权限、持久费用、丢确认与五入口跨层接线，需要沿用实际函数和历史失败上下文。仅原窗确不可用时，允许一个同等胜任A+新窗独占接续，原窗停止；不得并行两位实现者、自动委派子Agent或让原TASK118独审窗口写实现。A+是路由档，不冒充真实模型标识；如实登记客户端与可知型号，不因已完成任务的标签重审。

## 必须读取的最小充分输入

1. 上述入口／锁定规则；D:/shspic/project_NO3_RetroLume-agent/DocuS/执行动态文档.MD、最终需求文档.MD、架构动态文档.MD只读当前置顶与对应采用段，旧历史按需。原始需求文档只读，不代写。
2. D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-119-result.md全文A—D，SHA256=2d10d08bf2d16ff136258b122d93d12747b659744a4ae5c6036d348806096346；同任务design/protocol.json、call-matrix.json、official-facts.json、input-identities.json、四条hand-traces与document-consistency。不是执行capture_inputs.py／verify_documents.py或重复官方检索。
3. D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-119/orchestration-acceptance-20261018/adoption-proposal.md，SHA256=394dfae437dd416770104425aefc5386a95420edd4a3ef07dfa029bcd330db8f；其K1/K2及新分额覆盖119原稿相应旧数值／歧义。采用回执D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/orchestration-20261018/adoption-receipt.json。
4. 本卡orchestration-20261018下input-manifest.json、product-baseline.json、permit.json、resource-policy.json、scope-index.json。product-baseline是只读身份清单，不是批准任意文件改动。首工具重核你会改的实际文件；漂移先定位归属，不覆盖未知改动。
5. 原116 design/integration-contract.md与acceptance-contract.md、sample-inputs.json中有限L/I目标、33项字面值及八份合成文字的必要段；原117／118有效证据导航同窗复用，不重新通读归档、不重跑七族。未变的独审结论不是新v2已经通过。
6. 按119 D1直接读取当前实际实现及调用处。尤其ControlHub／RootLease／MutationGate／GuardedAsyncConnection、双provider生产admit/mark/record、领域accept/claim/GET与真实result/head写回、OneCall wire及受信loader、前端intents和late guards。不根据猜测文件名另造平行实现。

有关键输入不可访问或指纹漂移，仅停受影响部分，保留已完成结果；同窗旧材料继续有效只补变化，不能假称读取。

## 本次有效合同优先级与兼容

以本卡及实际用户采用回执为授权，以主控adoption-proposal的K1/K2和100／25／48-28-24为规范修订，再引用119 A—D完整设计。119原文80／20、40-24-16、79临界属于上一版限制和推演历史，不得套作本卡新v2总门；v1原行为和原预算样本按各自旧身份兼容保留。不要改写119原报告、机器原件或原116批准包来消除历史差异。

本卡不修改001—014、不新增表列或角色profile、不新增R03、不重绑既有活动、不另建金融账。正常结果／失败／UNKNOWN、007原子正文及现资格处理持续，SUP仍不得写费用／退款／settle。任何必须变更上述持久模型／公开动作或主要安全假设的发现，先交确切函数、差异和影响，停止依赖改动，不自行扩大。

## 需要连续完成的实现

### A 稳定根、完整请求、权限与规范字节

实现119 B1—B3的严格v2 root／grant／instance binding、PreparedRequest、精确Approval、有限字面值及同活动合格派生证明。完整typed request、实际provider对象、最终发送bytes分别hash并绑定，不只核catalog。actual URL／provider/model／配置／模板／source／memory版本／parent／scope／head／batch／原key共同核定；拒重复JSON key、未知字段、非法数值、容量越界和来源不明的任何文字／元数据。原件输入与JSON字符串摘要不混用，不隐式trim／归一化任意用户文字。

派生只来自同grant／activity／instance、received＋007＋领域record已合格COMMIT且当前父消费资格通过的有限投影；未知／失效／他活动／旧个人内容／原恢复副本不合格。自由答案、目标、记忆、来源标题等仍须实际字节及用途合格，正常本地保存不因此被关闭。合成fixture对真实动态ID、business key、generation和schema组包，不硬编码与实际调用身份冲突的回执。

在本机operator受信入口实现inspect／approve／revoke及封闭q日志事件和私有artifact。无HTTP通用批准／签票端点，无客户端批准路径／签名物／任意文件路径，不增加签名平台、watcher或自动approve-next。正常operator每次明确审查完整实际请求才批准；fixture可在隔离TESTONLY根调用真实入口，不能据此在正常模式自动批准未知请求。同OS principal的可信代码与真实文件ACL边界如实说明，逻辑方法限制不冒充OS隔离。

K1必须落实。先在日志锁内确定DecisionBody及event_seq，body排除approval_id自身，再计算规范摘要形成ID；所有重复／过期／续批分支明确。新批准期限仍15分钟、活动deadline、grant终点三者取最短，128 prepared／256 approval事件／262144 artifact／65536帧等原设计限额不提高。artifact不含key、DSN、整库或他活动正文；清理源／记忆时不得从私有副本回出已删内容。

仅Q分支增加只收已批准不可变bytes的transport私有路径。旧v1 transport、wire3及原wire4兼容不顺手重写；v2授权引用不塞入provider消息或造成摘要自引用。实际worker依据原data_guard和ControlHub重核，不能只信HTTP／IPC声称approved。默认外部能力未就绪继续fail closed，未知returned_models不可填成已核。

### B 五入口等待与原键继续

教学、面试、检索、HTML均在现accept/freeze已COMMIT后、launch claim前准备并等待。首次pending无SUP、无收费operation、无请求／费用／running／工具／preview新增预留。GET只读，不补artifact、不claim、不自动POST；accept确认丢失按原持久事实恢复，不把accepted先终结再伪称可重跑。

本机批准不自动执行，用户显式携原key和原冻结体继续，核同prepared及当前资格后只claim一次。同键异体409，已claim／unknown不回退等待、不借重新批准重发。claim确认丢失与结果COMMIT丢确认分别只读对账；已received但没有合格007／领域record不得进入下一步。

旧learning没有PG accepted体的特例按119 B4.5实现私有冻结intent与原GET恢复，不改first单槽及followup父规则、不把私有intent变成业务／费用权威。检索先冻结每批、所有待发批获批后显式继续，等待时不持SUP／数据库事务；未知批不自动重发。HTML批准仅授生成description的模型请求，不授preview／renderer／Docker／host权限，不重做固定renderer或真实预览。本卡preview创建／启动0。

前端教学、面试、检索、旧learning、HTML统一等待／过期／失效／未确认／可继续投影和实际provider用途告知。原IDB草稿、原键、owner/view/head/scope/namespace/DataContext及迟到围栏保留；切换、重开、刷新只GET，批准不后台提交，不丢正常本地草稿。产品用户页面不展示SQL、私有路径、grant摘要或实现步骤；operator CLI另有必要的技术说明。

### C 锁、结果落地、共同持久费用与恢复

K2必须完整落实，不能只补注释。共享Q policy lease覆盖资格核定、准入／mark及有限transport至完成／异常退出；它在任何会改head的record_outcome／领域结果事务前必须释放。之后先取适当排他policy lease，再MutationGate和原PG锁，按原CAS/currentness提交；禁止共享升级排他、PG锁内反向等待私有lease或网络跨PG事务。释放间隔发生变更时保留原operation／007事实和预留，抑制失效消费，不重新发或退款。revoke只有真实取得排他锁才报本地阻断，不能撤回已送远端。

双provider在真实生产admit／mark事务中核受信proof、完整当前身份、固定全局advisory锁及实际PG roster SUM，与原活动和operation预扣一起COMMIT。私有q.admission_intent／observed只提供核对与关闭见证，不计算可花余额、不充值、不退款。缺尾COMMIT、artifact丢失、hub换身、PG回退／operation消失、换实例／目标／grant等均不授新执行权；unknown保持原预留并只读对账，不能以HTTP异常判断未提交。

恢复和导出只保业务与金融历史，不导出可执行批准、秘密、旧launch或可恢复租约。旧source frozen／selector永久readonly与六旧对象不改变，普通数据包复制或重开不能取得Q权利。本卡新根全为TESTONLY，不得制造可部署的真实激活材料。

### D 配置、候选、条件额度与说明

采用候选deepseek_chat_completions／deepseek-flash、原base及ChatCompletions、thinking disabled；zhipu_embeddings／embedding-3／512不变。没有第三方／Pro fallback。输出learning≤256、teaching/interview≤2048、HTML≤4096，request／response≤65536 bytes、timeout≤10秒，embedding≤4 inputs／每项≤2048 codepoints、query≤1024 chars／4096 bytes等上限不放宽。公开资料不是本账号／token／framing／reasoning／含税币种或严格返回身份证明，正常配置必须如实UNKNOWN并关闭外部按钮。

未来一份Q的固定三个ID与上限如下，全局最多100次／25000000 microunits，单笔仍250000，不按两家分别发100次。学习01800000-0000-4000-8000-000000000001为48次／12000000；面试01800000-0000-4000-8000-000000000002为28次／7000000；补证01800000-0000-4000-8000-000000000003为24次／6000000。保留原固定全局锁、无跨活动挪用、无已建活动重绑。失败、超时、NOT_SENT已准入及UNKNOWN照计预留；新上限替换尚未激活的80／20，不叠加成180／45，不恢复旧13元。

更新惰性示例配置、必要正常loader和README/operator说明，明确如何准备／查看／批准／原键继续／撤销及信任边界、Q默认关闭、非敏感readiness和失败恢复。不能生成已签可用grant、填写真实T0／72h、把测试价率／dummy审计hash写入正常配置或请求真实key。本卡不再消耗119官方检索，不联网核价；留一份准确的启用余缺索引即可，设计矩阵81次及L05/F片段未知如实保留，非付费安全故障用替身。

## 允许文件与排他安排

仅本工程窗写本次产品，无其它在途实现或测试可与本批并发；不启动独审，不委派。以下均为项目根相对路径，修改前登记实际preimage/hash，实际diff必须能逐项追溯A—D。范围内可自选直接清晰分解，不为文件数另求确认。

- backend/app/capabilities/embedding.py、contracts.py、gateway.py、transport.py，必要新增该包q_开头的专用协议模块。
- backend/app/data_exit/control.py、files.py、maintenance.py、deletions.py、operations.py，必要新增该包q_开头的私有存储／policy模块；不得改schema／profile／restore／selector主体。
- 新backend/app/operator/__init__.py与q_request.py；backend/app/service_config.py、main.py只做本协议初始化／配置，不添加公网或通用批准接口。
- backend/app/activities/api.py、service.py、repository.py、teaching_repository.py、interview_repository.py；backend/app/retrieval/api.py、contracts.py、repository.py、service.py，必要直接返回投影文件；backend/app/learning/api.py、service.py、contracts.py、teaching_api.py、teaching_service.py、teaching_contracts.py、teaching_views.py；backend/app/interview/api.py、service.py、contracts.py、views.py。限准备／批准／等待／资格与直接影响，不重写业务提示、推进标准和旧模型正文合同。
- backend/app/preview/generation.py、api.py、business_contracts.py及必要repository命令GET投影，只接生成等待；固定compiler/description/renderer/supervisor/host及预览权限不改。backend/app/worker/one_call.py及worker_main.py／command.py／session.py／launcher.py中确有直接授权传播所需的最小改动，SUP不触账本、不改Job／时钟／恢复保证。
- frontend/src/activities中的ActivityWorkspace／TeachingWorkspace／InterviewWorkspace／RetrievalPanel、相应Api/intents/intentMatch及learning原键恢复组件；frontend/src/explanations/HtmlExplanationPanel.tsx、htmlApi.ts、htmlIntents.ts、contracts.ts。必要样式只服务新增等待，不借机重做界面或削弱S08迟到门。
- config/activity.example.json、integration.example.json、data-exit.example.json及必要新q-approval.example.json，README.md、必要新deploy/q-approval.md；.gitignore只追加本卡精确private路径，不修改旧排除规则。
- 新backend/tests/test_task120_outbound_approvals.py、test_task120_outbound_pg.py、test_task120_outbound_api.py、backend/tests/fixtures/task120/、frontend/tests下文件名以task120-开头的mjs夹具；既有测试仅真正受签名／返回影响的参数适配与新分支，不删有效断言、不把正确旧失败改绿。测试名称可按现风格小幅调整并给映射。
- frontend/dist仅正式本地构建生成；不能手改bundle。必要运行资源仅下面本卡新private目录，证据DocuN/evidence/TASK-120/execution/及统一结果DocuN/results/TASK-120-result.md。

禁止修改公共库、DocuS、用户原始输入／真实配置、旧报告／旧证据／工程账、001—014、schema fingerprint、R01/R02角色／包、固定preview部署和任何依赖／锁文件。不得安装／升级／下载SDK、浏览器、镜像、服务或tokenizer，不作Git初始化／add／commit／push／merge／publish。用户指定仓库https://github.com/shspic/RetroLume-agent仍是已有origin，发布执行留后续适用阶段，不上传DocuN或私有配置。

## 资源精确许可与低内存执行

本卡runtime只允许新隔离TESTONLY资源，不复用六旧PG／source／恢复根，不运行旧runner或恢复旧许可。运行前先封装一个有真实截止、内存采样、归属与自动精确清场的控制入口；离线定向核其执行边界后再开真实资源，不额外造通用调度平台。旧control/fixture只能只读借鉴，适用部件可复制到本卡新夹具并登记来源，不修改／执行已封存原件。生产路径不依赖DocuN临时实现。

PG只准一个新容器retrolume-task120-qprep-pg1、一个新命名卷retrolume-task120-qprep-data，label至少retrolume.task=TASK-120、retrolume.scope=q-prep-testonly及本卡permit ID；Docker Compose可复用现deploy/compose.local.yml、独立project=retrolume-task120-qprep，只启动pg服务，不启renderer-build。用已有本地锁定pgvector镜像，原compose引用pgvector/pgvector@sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f；先只读核本地ImageId／RepoDigests与实际引用一致，不能pull、换tag或重建镜像。主控未实时检查本地缓存，缺镜像只阻断PG部分。

容器1CPU／512MiB／pids128／restart=no，仅命名卷，无host bind／host network／privileged／额外capability。PG端口候选127.0.0.1:55480、55481、55482、55483；API候选127.0.0.1:18120、18121、18122、18123。首个真实根前一次只读检查占用／实际bind能力／Windows排除范围，按顺序选一个可用值记录后固定；这些预授权备选用于避免已知10013，不杀占用者、不改系统保留段／WSL／Docker daemon／安全设置。全不可用只停相应层，不能另找任意端口或重启系统。测试请求只能精确回环API，供方网络和其它路由拒绝。

容器create最多2尝试但最多1个实际对象，卷create最多2尝试但最多1卷；确认成功或ACK不明先inspect同名及label，精确复用，不create第二对象。最多3个逻辑测试库：retrolume_task120_flow、retrolume_task120_budget_01、retrolume_task120_budget_02。第二budget库只能在第一已有具体修正且须重新证明临界时启用，第一完整保留，都是明示TESTONLY，不是新付费余额；本卡不创建真实收费Q库。按既有001—014及现测试角色规范初始化隔离库，必要fixture角色仅本新容器范围，口令仅本任务synthetic随机值。新业务principal不授管理只读元数据权限，instance观察由隔离部署管理入口核。

自己的normal控制根、originals合成副本、浏览器profile及配置统一在D:/shspic/project_NO3_RetroLume-agent/.runtime/TASK-120/，明确flow／budget-01／budget-02不同instance/control/root/DB OID并登记。原三Q UUID可用于这些隔离测试实例，但不能把各库金融账相加或冒充真实Q；future收费许可仍0。预留／失败／unknown行、两个budget库和卷保留，不清零／truncate／drop／回滚库镜像来再试上限。其它确需FK清理只限本卡精确登记的临时合成ID，不动金融fixture／旧数据，不执行批量或递归文件删除。

为自己的API／PG注入的synthetic配置／口令放本卡ACL私有目录或安全子进程环境／stdin。Compose仅继承本任务显式synthetic变量，不输出配置渲染或env。口令不进argv、日志、报告、HAR或DocuN；本卡private路径先加精确.gitignore排除。不得枚举或输出真实环境变量／用户私配／真实key，不使用原.env／DSN／正常数据库fallback。docker inspect完整JSON只在内存解析并输出非敏感白名单，不能记录Env或用已知有缺字段风险的14字段Go投影。CID、ImageId、port、labels、mounts、Running/Pid等可存证。

启动PG/API最低可用内存512MiB；启动Browser最低768MiB。约每2秒采样，连续两次低于256MiB停止新增动作并精确关闭本卡Browser/API/PG，保留状态。采用低内存串行，只在当批需要时保持最少资源；不再要求Docker暖机2GiB或反复让用户释放内存。preview预算0，不受1GiB预览门拖住。缺运行能力不影响其余离线完成，不能绕平台自动审批或关闭浏览器隔离。

## 时间、次数与历史账

本许可ID为TASK-120-Q-PREP-IMPLEMENTATION-20261018。实际收到本卡后首工具同步UTC／宿主mono及控制器时钟身份，96小时日历有效，最后1800秒只清场保存。不得拿签发时间冒首工具，跨账号／中断日历差不冒CPU或连续活动，不新增不可观测的跨中断活动硬门。实际阅读／编辑尽量按可观察段记，不能测得就unknown。

全卡命令进程wall累计14400秒，运行资源持有并集10800秒，均含本卡实际预检／失败／修复／核对／清场；嵌套进程按实际外层覆盖不重复加作精确wall，无法包住的工具回执单列，不能漏成0。元数据单命令≤60秒，测试／build子批≤300秒，每个真实根从首次预检至业务结束≤1800秒，末120秒留精确清场。根内取日历／命令／持有／计数中最短实际截止，子批和复验不能延长根截止；清场不得因业务失败被跳过。

新增上限为真实根入口8、PG start8、API start8、Browser start8、frontend正式build4、真实Windows业务SUP/worker会话32、HTTP3000。测试root控制器的精确自有Job另记实际PID/birth，不伪充业务监督；真实预览create/start0、provider调用0、实际费用0、Git写0。根入口指实际调用本卡合并runtime控制入口，开始预检即计一次；普通read/hash/edit不是根，所有启动尝试即使未ready也计对应次数。不能通过裸命令绕runner、漏记预检失败／派生会话、把一次业务拆别名或借117剩余额度。

工程唯一子账位于DocuN/evidence/TASK-120/execution/budget.json、events.jsonl、case-index.json，记录permit/first-point/原截止/active_root/attempt/as-run/失败/冻结／各上限／StopProof。本卡是新成果许可，原117的root25、PGcreate/object/volume6、PGstart46、API33、Browser19、build8、Native140、HTTP2486、preview各2、fixture server3、provider费用0及81失败原样只读引用；不重置或倒写原账，不把新任务delta=0称全项目0。新增provider／实际收费始终0，未来条件总额不是本卡运行预算。

重启／换窗／恢复先核本卡active_root、原deadline、CID及PID/birth/端口归属；可能在途先精确处理，不开启第二控制器。mono倒退／域未知／UTC明显回退不沿旧mono续跑，未知持有上界照留；原运行deadline无法可靠映射则停止该根，准确收尾后仅在原96h和真实余量内重锚，没有资源与账目事实不能擅自认为已清空。

## 验证分层、最小充分矩阵和运行顺序

目的仅证明新完整授权／等待与真实PG预算和最终UI传播，现在必须检查因为下一步真实外发依赖它。不付费重现故障，不重跑七族／PDF／固定preview／R01R02全矩阵，不通过编译或Mock冒真实PG。旧S08 v1完整消息反例、ControlHub身份、owner/view/head、实际provider告知及未变旧恢复原件直接引用；旧测试字节／对象仍适用才复用。

先连续实现并离线验证，再跑一组正常PG／HTTP／Windows合成链，再跑最终bundle，最后在独立budget库做真实100临界；可按真实依赖调整以减少持有，不为每一层等主控。所有集成入口在开始前预检自身测试发现、test class／方法名、专用DSN来源、Selector loop、session bootstrap及合成响应schema，预检不得偷偷执行产品runtime。PG／browser脚本用最终字节，不复现已知Proactor／遗失admin DSN／空库分页等旧根因。预检只读与必要无资源小检查计入自己的实际wall，不编造全静态能保证运行成功。

至少覆盖以下完整事实，方法可合并但给真实标识与结果映射。

1. 完整typed／payload bytes和finite provenance的正常／反例；两个依赖请求沿同一immutable root，第二个取第一真实合格record父；未批准answer／history／memory／标题／foreign parent／ID／template／endpoint／byte篡改均零外发。真实gateway最低transport只数恰一次发送，配置／worker v4传播及v1／v3／原v4兼容，returned identity未知关门。单纯SimpleNamespace／字符串SQL断言不替代真实装配或事务。
2. prepare／approve／原key continue：accepted未claim且四账0、GET零写和零自动POST、same key异体409、同prepared重复批准、过期未claim可明确续批、已经claim／unknown不可二发、准备ACK／claim ACK／结果COMMIT ACK丢失分别正确恢复。实际teaching和interview至少各一条query已提交→model等待→operator批准→显式继续→007＋业务record COMMIT链。旧learning和HTML各一条原键等待／GET恢复／显式继续；HTML只生成description，不启preview。
3. K2正常结果落地必能完成，有界的source／memory／scope／head变更或revoke与发送竞争必须分清临界前拒绝、已准入NOT_SENT保留和可能已送UNKNOWN。共享锁释放后结果被后来的变更失效时，原费用与不可变结果留账、head不错误推进。不准用外层Python串行调用冒并发／PG锁；核无共享升级死锁／PG反向等锁。journal换身／尾损坏／artifact消失／instance复制／readonly入口关闭，删除后副本不泄漏。
4. 生产真实PG共同准入：一个budget库、原固定三活动、相同实际模型与embedding准入实现／同全局锁／真实SQL SUM／活动和operation同事务COMMIT，无Proxy SUM／替换connection／内存预算。99临界为47／28／24次及24750000预留，两provider不同合法prepared/operation、同一个有资格的A1 lease同时竞争其最后一个slot；真实两个backend PID和锁／屏障证明窗口，最多一个COMMIT、输方零发送，最终新连接回读≤100／25000000。99基线须经生产准入逐笔持久累计，不能手写requests_reserved或state造金融样本；真实业务／claim要求与原资格仍核。
5. 有效的100门下不同两活动都余一个slot且SUM=99不可达；不得伪造。固定0.25下99次／25元也不可达，不伪造单独费用耗尽fixture。实际临界同时核次数和费用及源码各比较式；达100后两provider都拒、原操作UNKNOWN／超时／已准入确定未送都保预留。准确停自有树后同库重开、GET只读，新grant／instance／拷贝／旧root不能产生余额或再发。两预算库是明确隔离的零外发测试，不是真实收费“换库续费”。
6. 最终正式build的JS/CSS实际响应hash绑定：教学和面试正常等待／批准／同键继续，重开仅GET，旧owner/view/head/DataContext迟到不得发下一POST，local draft仍在；检索批等待、legacy learning和HTML显示可恢复；未批准文字可本地存但不会发。记录请求时间线与显式动作锚点，避免把显式POST自身算“动作后自动重发”的旧夹具误报。用受控HTTP／实际本机API与真实Windows链，合成transport及回环网络守卫；不向真实provider打故障。
7. 正常secret／激活loader的非敏感fail-closed证明：缺真账号／税／token／framing／reasoning／returned identity／审计回执等不得变成ready，原模型候选不fallback。TESTONLY合成readiness／receipt只在隔离夹具注入且明确分级，不能输出为真实启用包或在产品加环境开关免审。正常两链无真实key时仍可本地保存与只读，不将全部产品功能关死。

所有测试必须明确专用RETROLUME_TASK120_FLOW_TEST_DATABASE_URL、RETROLUME_TASK120_BUDGET_TEST_DATABASE_URL、管理夹具专用RETROLUME_TASK120_ADMIN_TEST_DATABASE_URL或本卡安全子进程注入；每次核本卡精确库／实例身份，缺失明确skip/blocked，不回退用户DSN，skip不算通过。本机Windows psycopg采用项目已验证Selector loop。合成fixture保留动态真实ID／正确schema／operator顺序，不将真实产品拒绝改为宽松断言。99基线与结果、控制根及失败原件保留；如确需第二budget库复证，先精确收尾第一、留下as-run和修正依据，在同本卡余量与次数内执行。

每层检查原则一次，新的明确修正或诊断依据才重试。同一问题两次有依据修正后仍失败、主要方案根因不稳、新高风险或任一硬门到达，停止相关机械重跑并交具体事实；仍可完成不依赖该失败的离线交付和文档，不把一次夹具失误自动结束整个尚有余量的卡。达到整卡充分证据即停，不为用满配额追加测试。资源前提不达就准确not_run，不要求用户释放内存或付费。

## 证据、审计与保存

证据保存DocuN/evidence/TASK-120/execution/，含首点／资源白名单、源preimage与pre/post/hash/diff、实际命令exit／耗时／开始结束／失败和修正、准确版本的as-run、loader/wire／PG持久回读／并发窗口／最终bundle实际加载、用例到A—D映射、预算／持有及StopProof、精确剩余readiness。正式测试夹具放backend/tests/fixtures/task120和frontend/tests，DocuN runner仅外部执行组织，产品不import它。

正常／失败日志和原样历史只增不覆盖。若最终产品或测试字节变了，按实际影响复检或给可证继承依据，不把旧失败批全改PASS、不拿变更后最终文件hash冒充旧as-run加载hash。仅结构／hash证明用B，真实PG／Browser／Windows行为用A，声明C／推断D分开；私有文本／token／Env不入证据。

本卡范围的稳定完整成果必需独立增强审计，归主控另卡安排，优先原TASK118独立审计窗口承接新边界；当前不预占其新TASK，不让它参与实现或读本窗完整聊天／思考／自评。审计收到原目标／采用规范、最终实际diff／代码／原始证据，核新增批准权限、K1/K2、PG共同权威、原键恢复、最终UI及执行控制；旧D01—D04和七族充分原件复用。未有适用独审与主控真实启用回执，Q始终冻结，不能用实现者自查放行收费。

每个真实根结束或异常先准确停本卡Browser／API／业务Job，再停精确新CID并核Running=false/Pid=0，核登记PID/birth与选定端口释放。保留容器／卷／库／journal／失败，禁止Docker prune、批量删、杀用户进程、重启Docker／系统。看不到的对象标unknown并停依赖运行，旧六CID没查就不写“全部实时停止”。平台审批拒绝记录原因、停止该动作，不换壳／提权绕过。

完整结果写D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-120-result.md，先一句结论／工程候选、真实实现范围和接口／兼容／权限／账本清单、A—D与最小矩阵证据，再列失败／修正／实际计数耗时／所有unknown／not_run／偏差、精确停止、官方与账号未决、建议DocuS更新、必要人工和下一审计。新旧源及最终bundle和最坏费用仅按实际证据声明，不宣告Q动态、STEP018/019/020、M1或项目通过。

如发生中断，原结果置顶追加、旧正文原字节保留，同TASK120/R114与原窗口续作，不重置预算／96h／失败。保存后完整复读，带回一句话结论和可点击绝对路径即可；无法保存如实写未保存，不交虚构链接。共享编号／状态／DocuS／变更由主控串行维护，本窗只报告建议；没有此刻要求用户给key、重新批准100／25、运行SQL或释放内存的必要动作。
