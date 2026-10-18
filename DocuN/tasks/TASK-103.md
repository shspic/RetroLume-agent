# TASK-103 / R-097 审计修复03 — 编辑身份风险修复与最后引用补证

## 目标与交付

你继续担任原TASK103实现执行者，一次完成R104-F01/P1的最小身份保护修复、准确竞态窗口验证、最后引用迟到补证和最终候选封装。三项前轮补证与104已完成的其他独立审查有效范围直接复用，普通修正留在本卡连续完成，统一返回。

核心问题不是保存响应送达之前切换，而是保存回执已经确认、后续列表refresh仍在await期间显式切换。旧refresh返回后无再次核身份就select(A)，能够抢回用户已经明确载入的B。当前源码和已实际加载的最终JS都存在该路径，104据源码作B级确定推导，尚未声称真实误写。本卡必须验证这个准确窗口。

结果继续置顶 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-103-result.md，标题审计修复03。当前52856字节／SHA-256 8b544e505c574b0bc666ca8ebd651bf4275000848dbb9b2af8ad386cb835aa18全文作为新前缀后历史原字节保留；新原件仅写 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/audit-repair-03/，不覆盖C01／C02／104的失败、数据、账或快照。

完成标准为P1准确窗口不再抢回身份，正常保存及未确认／新草稿语义保持，引用迟到真实只读性质成立，最终源码／dist／实际加载／fixture／PG证据可绑定，精确资源收尾。你交付修复候选与卡内证据，不签独立终审、共享DEF关闭、G9／STEP013／M-1或项目。

## 项目、规则与接收安排

根 D:/shspic/project_NO3_RetroLume-agent，入口同根AGENTS.md。task_model，锁定V4.0／公共AGENTS CHG-0003，需求v1.1、架构v0.93、唯一执行动态v2.15、阶段07。公共根 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4；读DocuS/AGENTS.MD，适用WORK第4／6／8／9章、task_model/prompts/07_开发执行循环.md及TASK_TEMPLATE.md。七锁定指纹仍项目 DocuN/evidence/v4-migration-20260930/rules-snapshot.json，不自动采用新版。

接收A+增强执行，沿实际完成TASK103续作02的原业务窗口，使用强推理模型处理异步身份和真实控制链；具体客户端／部署型号如实登记。原窗确不可续才新A+按文件接续，不派子Agent，不用104独立窗口修业务。原104已返回并停止，只等待修后增量复核，没有并行源码写入。

关联原G9-P／TASK102/R096、STEP013及实际006／007／008／009／012消费边界、TASK104/R098。本轮主控登记DEF023/P1对应R104-F01；DEF019—022由主控依据104已核有限范围关闭，不在本轮重开。用户已批准G9-P，无主要模型或权限变更，不重复询问采用或是否继续。

旧许可全部结束，不借余额。103初轮24根、C01十二根、C02三根，104三根共42真实入口，均不是成功数。104补证browser／driver为0，三根前置失败与原所有失败保留；不能将新许可当相同根因清零。新许可 TASK-103-G9-R03-20261007，使用及失败从零开始单独记账，旧累计不变。

## 背景与最小充分上下文

只补当前改变和缺失，同窗已读102合同、规则及旧结果复用。按序读本卡当前前缀、入口／未变规则、以下材料。

- D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-104-result.md 的第二节R104-F01、第四节fixture失败、第五节建议边界；其他已核结论按需要查，不重新读全部33产品差异。
- D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/audit/R104-F01-static-finding.md 与 R104-F01-final-bundle-excerpt.json，核源码与现有dist实际路径，不凭聊天概括修。
- D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-103-work-decision.md 当前审计回收／修复03裁定和 DocuS/执行动态文档.MD v2.15当前段。
- D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/repair-03-input.json，含297现有对象冻结、291旧对象／325审计输入核对、精确资源和旧账；新测试必须另存as-run。

直接源码为 frontend/src/activities/MemoryWorkspace.tsx 的execute／refresh／select／草稿及相邻异步副作用，memoryIntents.ts／memoryApi.ts与真实TeachingCitations／工作区挂载。当前MemoryWorkspace SHA aebaf2e520177519e53f34699558ab780e72f4c636157284ac15d27ef7610684；当前JS index-D7dvfnOT.js，SHA d2e8179a85dbc10a6f5bf920764f0e3420d051188714235364e81d3106744093，CSS index-COpEVDbn.css／39bfb4f09992c354b628f8e2542b3e75b46a86d8910a29f3dd2331eeb1ddf86b。

104的其他代码、SQL／权限、legacy／v2、精确清理与42根旧证据适用性已有集中核证，原独立审计同窗未参与102／103，实际沿101审计历史的隔离例外已披露且接受。不因模型或不是字面空白窗口再做全面重审。R104-O01—03保持非阻断观察，不在本卡修改仓储／模型／锁域，不自动新增验证硬门。

引用真实目标仍可先查103/continuation-02/target-selection.json、browser-target.json，activity a29a945b-a58f-4798-b4b3-93cc1e736aed，record e6964ce9-7686-45c3-b8b2-8e247cd25dcf，citation lc_c0655a9aed2099f2e0d9f328。以前GET200不是当前资格或迟到证明；本轮真实只读重核。当前expired overlay不授执行资格，合法历史引用读权限与写许可分开。

## 执行边界与资源

只允许最小修复 frontend/src/activities/MemoryWorkspace.tsx，以及有具体同链证据必需的memoryIntents.ts／memoryApi.ts小范围辅助；不做无关重构／文案美化／新持久schema。新fixture与离线回归在 backend/tests/fixtures/task103/r03/、backend/tests/test_task103_r03.py，浏览器脚本 frontend/tests/task103-r03-ui.cjs。旧103／104fixture与全部原件只读，可复制最小已核资源／server逻辑到新r03，并核目录深度、ROOT／EVIDENCE／permit／日期／cwd，不能激活旧control。

允许现有项目构建正常更新已冻结的frontend/dist生成物，最多2次、先存全部既有dist原字节／hash，保留被替换资产pre；不手工递归清空目录、不改依赖锁／版权文件、不安装库。源没再变不重复build。TeachingCitations、TeachingWorkspace／ActivityWorkspace产品、后端／001—010／数据库函数／role ACL／worker／SUP／Job／关门／结算／gateway／transport／材料／PDF／原件、正式DocuS／公共库／原始需求、Git和旧证据均禁止改。

代码修正应保持每次异步返回后的当前实例、owner、完整绑定ID／version／revision／body_sha、读取／编辑epoch的授权范围。旧保存确认可以确认自己的持久事实，不能借随后await重新选回用户已经离开的ID、覆盖新输入／清新草稿或把旧错误／notice写到新身份。不要仅补135行一个if却遗漏本次同一execute后续await的副作用；同时避免把正常本请求自己的合法select序号变化当成用户切换而全拒成功刷新。

若确需超出上述前端范围、改变已批准持久模型或后端语义，停相关改动，完成可做部分后交回具体差异；不能为四处局部观察顺手改010／SQL／lock／JSON权威字段。发现新的真实引用产品缺陷只留证，不自行扩大TeachingCitations写权。

仅复用精确pg1 CID4889202d9a58c622fb7cd2bd3087e5bceb7ad20a049c6550f4bd3588ff66ac11，retrolume-task-103-g9-pg1，卷retrolume-task-103-g9-pg1-data，库retrolume_task103_g9_main，127.0.0.1:55443。镜像sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f、1CPU／512MiB／pids128／restart=no，只有该命名卷，无host bind／特权，旧permit标签TASK-103-G9-20261006不改。

pg2 CIDf96ac8dcb64648c76a2bc70f3f8b75969ada0ea0ea69b5896fe5ecb71affab85、pg3 CID4b813f9e4317aef9c613eb140fcb2d40c55a6bd98ee5d79807ea5851975d7f68只读inspect保持停止，不连PG。API与最终dist仅18103，不需要fake监听／SUP／模型／工具／外网。所有用户配置／用户数据／真实provider／费用／新容器／卷／角色0。

测试业务写仅通过真实产品记忆commands，在本轮登记的独立合成ID上save／revise，用于修复回归，最多12次显式POST尝试含失败／重复；无revoke／purge／cancel、无新活动／教学命令／SUP，不直接SQL改业务。优先创建A/B两条专用用户记忆，或证明未被任何既有活动选用的独立样本；不能修订引用目标依赖的记忆导致它失效。所有旧事实保留，零DELETE／DROP，旧未确认save和失败UNKNOWN不重发。

凭据从精确owned资源取单项到RAM／stdin／子进程Env，不输出Env或入argv／日志。104已重置本卡app口令，不猜旧口令；本轮若不可恢复，可在确认所有旧服务停止后最多2次精确retrolume_task103_app RAM随机口令重置，核属性／membership／ACL不改。不能动其他账户或提升权限。session token只内存，原件认证头脱敏。

新额度主动10800秒、离线及build合计600秒、真实PG／HTTP／browser1200秒、独立收尾300秒、辅助metadata600秒；真实根／pg1 start／API listener／browser／driver各6，离线5批各≤120秒，build2各≤300秒，真实根各≤300秒并受剩額。预计一根主组合，必要旧字节辨别／有据受影响补验才使用余量，不为了用满反复启动。新SUP／model／tool／provider、create容器／卷／role、迁移／DDL均0。

固定首读与单调主动截止，动作前计数，真实预检BLOCKED／失败／未知也计；同根因两次有据修正仍失败即停该路径，即使总次数尚余。6次是容量上界，不是六次相同方法盲试许可。旧42根及全部未知／失败保留，不改变日期／窗口／驱动方式返额。

command a392c565-1731-4314-b22e-6cee9458f862的requests4／cost4000／tool1／settled12／R20和UNKNOWN不改；树零不授权退款／结算／恢复或重发。旧非规范M5、pg2反向落点、pg3 pending墓碑／正文保留。

## 验证、证据与审计关系

先完成最小源修正及整条fixture／控制／selector／auth走查，再在新许可内连续真实验证。不能只处理每个首失败然后盲启动下一根。现有已验SQL、权限／旧账、三项C02性质和未改的模型／停止主体按104版本对照继承，不重跑全部G9或旧Windows。

本次运行前把反复出现的确定前置一次核全，必要离线检查只针对新fixture。

- Docker inspect使用完整JSON按Actual Mounts判断Type／Name／Destination；HostConfig.Binds字符串可描述命名卷，非空不能直接认定host bind。严格匹配原精确卷，不因此放宽到真正bind mount。
- 参数化psycopg查询正确处理百分号；可沿104已修的%%，或使用准确等价参数，不复制未转义的LIKE。角色／ACL检查不借机扩权。
- /api/session原接口的native bootstrap GET不加不支持的Origin；其他受保护业务请求用真实session及18103同源要求。先从实际local_session源码核各接口，不改产品认证，也不取消业务Origin检查来让测试绿。HTTP失败保存status／code／脱敏响应，不能只记non200丢原件。
- 实际UI是section.library、button.material，列表默认参数与cursor从当前产品请求读取；不能用section.collection／limit20假定数量匹配，或同名标题任意取first。取得真实详情／DOM数据身份，必要用“加载更多”，不只以索引签ID。
- runner不等待已关闭stdin的人工stop输入；各根有硬截止和finally精确收尾，保留PID／出生／命令身份。helper导入路径和模块启动从backend正确cwd核，Windows psycopg事件循环沿产品／既有Selector口径，不复制错误Proactor。

P1准确窗口的主回归必须是真实浏览器、API与PG，使用真正服务器响应暂停，步骤如下。

1. 确认A/B是专用且不影响引用的合法记忆，B在本次新profile无旧草稿。打开A、编辑并实际save／revise，服务器真正COMMIT的POST回执可暂停；继续输入使编辑epoch增加，再允许该回执交付，触发原新输入保护分支。
2. 针对这个保存确认后的列表refresh GET取真实服务响应并暂停向页面交付。证明已进入“回执确认后、列表GET未返回”窗口，而不是再次只暂停原POST。
3. GET挂起期间实际点击B，按现有“明确载入新版”载入干净B；核绑定完整B ID／version／revision／SHA／owner、正文与dirty对应现象。这条干净B路径能辨别旧135行漏洞，不能用带脏草稿B挡住旧select而假称修复。
4. 释放旧列表响应，核当前仍是B，没有旧A详情选择抢回、错误／notice／草稿混入。接着编辑B的新输入／IDB草稿，仍绑定B；A原提交的key／hash真实收据与唯一effect存在，不退款／重发。

至少再核同一旧续处理在实际导航卸载后不会选择或污染重新打开的面板，以及正常未切换／未追加编辑的保存仍正确显示新版本、清对应旧草稿且确认一次。C02“POST回执前切B”和“只继续输入”的适用证据可继承，但本轮execute语义若影响它们，合并最小受影响检查。不要写镜像实现的mock或只用AST if存在代替这些真实性质。

如可在不新建业务效果／不增无关批的前提下用已保留旧bundle展示上述准确窗口必然切回A，可保存一次反例增强辨别力；它不是额外硬门。无论是否跑旧版，给出本用例为何会检出104原路径的具体控制点，不能用宽sleep或最后文本碰巧相同当完成。

最后引用迟到在同一根／真实页面和当前合法目标连续完成，只GET／SELECT、业务POST增量0，不做新教学。

- 真实核现有workspace／citation可读，界面选择后确认确切activity／record／citation／viewToken，旧GET200不可直接复用为当前资格。
- route.fetch取真正GET200引用原文后暂停交付；以真实控件切另一合法活动／记录，或导航卸载后打开另一个明确身份，核新页面读取完成及身份。
- 尝试释放原真实响应，记录实际Abort／交付／错误层级和时间；条件等待后旧原文／位置不复活、不串入新面板，业务POST0。真实Abort抑制可合格，但不能没发请求就按static seq通过。
- 保存前中后DOM／截图／请求响应时间／加载字节，与PG业务表／四账前后对应；无需重新发送no_evidence或旧CAS来使总批绿。

每实际批保存新fixture／脚本完整as-run和被测产品／dist身份，先测后改的部分必须复验实际影响或标not_run。当前297对象中禁止域核冻结，差异限允许前端／生成物和本轮材料；源->build->实际完整加载JS／CSS链都绑定。最终构建改变生成字节不能借旧bundle签新guard，但SQL／后端未改证明可直接继承。

PG只接受新登记A/B记忆的合法save／revise效果，旧表／原行保持，统计每key／effect／version及真实字节。引用阶段与其他旧状态GET零效果；旧UNKNOWN／旧submitted意图／旧profile不自动处理。失败批中的真实COMMIT必须保留，下一根只读核收据，不重发或创建同一效果；新的独立场景明确不同ID／目的。

本卡不是审计。修复稳定、两个真正剩余性质成立后交回，编排只把本次实际差异和新增原件交原104独立窗口做一次增量；104已覆盖的其他未变范围直接继承，不能为一处await修复重做集中审计。审计若发现新的直接回归仍回唯一103路线，不自签DEF023关闭。

## 停止与回传

卡内连续完成修复、相关检查和普通fixture修正；达成目标立即封装收尾，不逐子项回传。根因不稳、对象／资源漂移、范围扩大、同根因两修仍失败或相关次数／时间触顶时停止受影响操作，完成不受阻证据和原件，给具体未满足与最小需要变化，不偷开额外批。

独立300秒精确收尾本卡PID／出生／命令身份、Chrome／driver／API和pg1，核18103／55443无监听、三CID皆Stopped／Pid0。留容器／卷／库／role／数据／profile／原字节副本；不删除合成样本，不杀用户进程，真实非零退出或未知照实。

结果先写修复候选完成或部分停止、P1准确窗口及最后引用实际结果、差异和原件导航；再给原审计发现到修正对照、其他await副作用保护、正常保存／新输入／卸载行为、完整pre／diff／post／构建加载／SQL未改证据、原新累计账／失败／COMMIT不重发／资源／偏差／未验、待原104增量输入。保留52856字节历史并核suffix hash，不覆盖104不通过原文。

保存且可读后只回复一句结论和 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-103-result.md 的可点击绝对路径。任何DEF／G9／STEP／M-1／项目最终裁定留编排，不耗尽预算、不更换窗口返额。

## 必要人工与待同步信息

用户只需将本卡当前前缀转给原TASK103 A+强模型窗口，完成后带回原结果路径。无需再批G9-P、新用户密钥／provider／用户库权限；当前具体修复和合成资源许可已写明，关键未知才给最少问题并继续不受阻部分。

共享编号、状态、架构、CHG与审计卡归编排；你只报告待同步事实及已证实经验候选，不改正式DocuS／公共库／原始需求或记忆。原104保持独立，不参与修复。

## 以下为已结束的续作02、续作01和初轮历史合同

# TASK-103 / R-097 续作02 — G9最后四项补证与候选封装

## 目标与交付

你继续担任原TASK103实现执行者，在同一任务内补齐最后四项直接证据，保留已经成立的实现与子性质，完成最终候选封装和精确收尾后统一回传。不是重开G9、重跑24组，也不是先做独立审计。

本轮只补V15晚到保存回执、晚到引用响应、浏览器实际冲突POST，以及续作01最后新增LearningRefusal／no_evidence错误映射的真实HTTP零副作用确认。普通修正和必要受影响复验留在本卡连续完成。达到四项与最终身份记录标准立即停止，余量不以耗尽为目标。

完整结果继续置顶 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-103-result.md，标题续作02。当前结果41022字节、SHA-256 fe80b6161bff72942a09bb3ef8cb5a61e507aa42015f149aa9e3495fed1591c3，全文作为新前缀后的原字节历史保留。新证据仅写 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/continuation-02/；既有pre／post／runs／失败／账／checkpoint不覆盖。

完成标准是四项都有真正执行的明确断言和原件，绑定最终源码、测试、实际加载bundle与持久事实；未改分支按适用字节继承，没有新阻断，旧副作用与资源保持可辨。不把总批FAIL改PASS、继承项伪称本轮运行、skip或退出0当通过。你交付候选，不关闭共享DEF、G9、STEP013、M-1或项目。

## 项目、规则与接收安排

项目根 D:/shspic/project_NO3_RetroLume-agent，入口 D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。task_model，需求v1.1、架构v0.91、唯一执行动态v2.13，阶段07。公共根 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，锁定V4.0／公共AGENTS CHG-0003。

读公共根DocuS/AGENTS.MD，适用WORK第4／6／8／9章、task_model/prompts/07_开发执行循环.md和TASK_TEMPLATE.md仍同版。锁定指纹在项目 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/v4-migration-20260930/rules-snapshot.json。同窗已读未变正文复用，只补改变和缺失；不采用公共新版或其他模式。

接收A+增强执行，沿实际完成TASK103续作01的原业务窗口，使用可用强推理资源处理真实异步状态与证据。型号如实登记，不按品牌重审。原窗口确不可续才用新A+并按文件接续，不派子Agent、不用未来独立审计窗口实施。本卡串行独占相关页面／fixture／dist和pg1，没有已派发的并行104。

批准依据仍用户2026-10-06采用G9-P、TASK102合同与编排work-decision。同TASK103/R097未验收补证，不重复请求采用。关联STEP013及原006／007／008／009／012消费边界、DEF019／020／021、102/R096、G8/100/101。本轮主控另登记DEF022/P2为no_evidence错误映射修复候选，不扩大持久模型。

原许可全部已结束。初轮entry24、browser／driver3、build3、start23、SUP16及全部原失败；续作01entry12、browser／driver3、offline6、build1、start14、listener3、SUP22及主动12072.453秒都保留，不借任何名义余额。新许可 TASK-103-G9-C02-20261007 的计数单独登记，失败与未知仍累计，不清零同根因历史。

## 背景与最小充分上下文

本轮起点已由编排普通回收，当前281个文件逐项与完整281份post一致，20份保护文件、9项规则／合同及七份锁定规则匹配。结果原24351字节历史后缀精确保留；三容器Stopped／Pid0，18103／18104／55443—55445无监听。编排未启动数据库、应用、测试或构建，不是独立审计通过。

最小输入按顺序读取本卡当前前缀、入口／未变规则、下面三份文件的当前前缀；同窗已读内容不全文重复。

- D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-103-work-decision.md 的续作01回收与续作02裁定。
- D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-103-result.md 的续作01结果及四个剩余子项，不重读所有历史。
- D:/shspic/project_NO3_RetroLume-agent/DocuS/执行动态文档.MD 的v2.13当前段。

冻结基线及资源、旧账、原件导航在 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/continuation-02-input.json 和 orchestration-receipt-02/receipt.json、finite-binding-checks.json、resource-readonly.json。必要时按需读续作01的final/pre-diff-post.json、validation-matrix.json、bundle-chain.json、sql-chain.json、accounting-final.json、runs-ledger.json及相应原始浏览器／运行结果，不读整包来重复研究。

直接源码只需 frontend/src/activities/MemoryWorkspace.tsx、memoryIntents.ts、memoryApi.ts、TeachingCitations.tsx、TeachingWorkspace.tsx及调用依赖，backend/app/learning/teaching_api.py与真正触发no_evidence的服务前置。上述均以项目绝对根拼接；冻结值见input，不靠聊天猜实现。

续作01的010三函数已向前应用，最终十二函数源码／应用指纹／真实catalog一致，旧行与安全属性不变。sql-chain的migration_sha256按read_text统一换行文本计算，915f0ed9…；完整CRLF文件原字节hash为33df4bcd8c040035f360cfc21c845e8f54e426832959e41477e67496f733c83c。两域已核，不是产品漂移，不重跑迁移或改catalog。

最终24份前端源码与build01一致，加载JS为index-D7dvfnOT.js／773070字节／d2e8179a85dbc10a6f5bf920764f0e3420d051188714235364e81d3106744093，CSS为index-COpEVDbn.css／39bfb4f09992c354b628f8e2542b3e75b46a86d8910a29f3dd2331eeb1ddf86b。若本轮不改源，直接服务并核加载这些字节，不重构建。

旧browser01／02仍总FAIL，browser03只补尾链，不冒整链全新运行。已过慢真实GET、新输入旧绑定保护、COMMIT失响应GET核对、固定选择三SUP、撤销／清理／引用抑制等直接继承。当前还没有晚到保存响应、晚到引用响应和第二页真正POST冲突的直接原件；上轮409仅impact GET。最终no_evidence映射只有offline06 ASGI及真实异常类型替身，不能替代实际HTTP／PG零写证明。

## 执行边界与资源

默认冻结全部产品与SQL，只新增本轮定向fixture、浏览器脚本、必要离线方法和结果证据。新执行代码在 backend/tests/fixtures/task103/c02/、frontend/tests/task103-c02-browser.cjs、backend/tests/test_task103_c02.py；按当前必要性建立，不建通用平台。旧fixture默认只读，可复制最小已验控制／资源／server逻辑，必须改成C02许可和新账，不直接重启已结束C01入口。

若直接原件证明同合同产品缺陷，允许最小修复上述MemoryWorkspace、memoryIntents、memoryApi、TeachingCitations、必要TeachingWorkspace身份传递或teaching_api的该错误映射，及直接相关CSS；保存pre／diff／post并只复验受影响性质。只会多一次构建且绑定最终源。任何仓储／持久模型／权限函数／监督协议必须改动的需求都停相关项交回，不能借补证回到大改。

001—010、其实际数据库函数／角色／ACL、全部worker／launcher／SUP／Job／关门／结算、gateway／transport、既有材料／PDF／原件、共享local_session、依赖锁、正式DocuS／公共库／原始需求、Git与旧证据均禁止写。不得重建库、重跑010、关触发器、清库或改不可变收据、client epoch／资格校验以迎合测试。

仅可启动精确pg1，CID 4889202d9a58c622fb7cd2bd3087e5bceb7ad20a049c6550f4bd3588ff66ac11，名称retrolume-task-103-g9-pg1，命名卷retrolume-task-103-g9-pg1-data，库retrolume_task103_g9_main，127.0.0.1:55443。镜像sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f，1CPU／512MiB／pids128／restart=no／仅loopback／无host bind或特权，标签仍TASK-103-G9-20261006。只核实际身份后复用，不改旧标签冒新创建。

pg2 CID f96ac8dcb64648c76a2bc70f3f8b75969ada0ea0ea69b5896fe5ecb71affab85、pg3 CID 4b813f9e4317aef9c613eb140fcb2d40c55a6bd98ee5d79807ea5851975d7f68继续停止，只读metadata，不连PG、不改pg2反向DDL落点或pg3 pending墓碑／正文。API与最终dist仅18103。不需要fake listener；如必要有限provider用已验进程内最低传输替身，无外网／真实provider／付费。新容器、卷、角色、依赖安装、私有配置、用户数据均0。

复用本卡app／denied／admin时只从已核owned容器Env取单项口令到RAM或经stdin／子进程Env注入，不输出完整Env、不入argv／日志／报告。若本卡app／denied密码确需重置，先证明本卡旧应用都已停、单独记录精确角色动作；不重置其他角色或账户。

新独立额度为主动7200秒，离线及构建合计600秒，真实PG／HTTP／browser及必要Windows1200秒，独立收尾300秒，纯辅助metadata300秒。次数真实根3、pg1 start3、API listener start3、browser／driver各3、离线3批、build1；create容器／卷／角色均0。根各≤600秒、离线批≤120秒、build≤300秒并受剩额；创建浏览器context／page不算新的browser进程，但实际新启动必计。

预计只用一个主组合根／一次pg1／一个listener／一个浏览器与driver。余下最多两根只用于有具体原件、明确不同修正依据的受影响复验，不分别为三个场景另开入口，不为挑目标反复启动。当前卡一旦实际载入就固定首读／单调基点和主动截止，动作前计数；预检BLOCKED、失败、超时与未知均不返额。记录根、driver、浏览器、方法、页面、请求、SUP的不同计数，不借内部子进程暗开另一个批。

默认新SUP0。先在同一主根用真实只读资格选择已经存在且current的教学／引用目标，沿用已有最终记录，不新生成同一效果。只有旧目标都已经合法失效、无法得到可读引用时，允许本卡原合成授权内最多2次受控教学SUP准备最小新合法引用，并保存为何不能复用；不用真实模型或伪007／009结果。该附条件次数是同卡总SUP上限2，包含失败；SessionConfig仍W20／request2／grace2／startup5／manager_db5／cleanup5／mutex3／overhead30／manager50／lease20／single_host_recovery=false。

command a392c565-1731-4314-b22e-6cee9458f862及其requests4／cost4000／tool1／settled12／reserved20／UNKNOWN原样保留。树零不授退款、结算、重发或恢复开关修改权。no_evidence负例SUP必须0，不得先进入上述新SUP准备分支再称零副作用。

## 验证、证据与审计关系

在首真实根前完成一份四项小矩阵与完整脚本走查，核当前selector、可达编辑动作、实际API参数／错误码、owner与IDB绑定、两页相同有效revision／impact预览取得顺序和引用目标需求。普通准备用离线预算，不能以离线替身结果签真实性质；不把重复sleep换数值当根因修正。

主根先核许可、基线、资源身份及现有只读target，启动pg1与真实API服务当前dist。取得合法session／Origin；所有新行用新合成ID登记，保留已有有效或失败数据，零DELETE。只用当前本机真实HTTP／PG；按下列顺序或同等有据顺序连续完成。

1. 最后错误映射。对 POST /api/activities/{activity_id}/teaching/commands 构造合法鉴权、有效配置、确实没有合格证据的目标，实际服务抛LearningRefusal。收到409／no_evidence／对应中文提示，实际计数证明0新accepted command／operation／provider发送／SUP、四账未变化，目标行和头／记录无变化。可在新合成活动上做一次请求，不能用无权限403、字段错误422、service异常替身或另一拒绝路径替代。此前成功分支按未改逻辑继承，不重跑完整教学。

2. 双页真正陈旧提交。取得两个独立owner编辑页对同一current记忆、同revision／hash的真实详情及有效impact预览，再让A确认追加一次修订；B保留旧预览与草稿，实际点击原确认按钮发POST，收到409。保存B真实出站payload、旧expected_revision、code、前后DOM／owner／IDB绑定／新输入；数据库只产生A一个有效新版本，B没有第二效果或自动POST。关键是B已成功取得预览后才允许A提交，不能再次在B的impact GET409处止步。

3. 保存回执晚到。以真实页面提交一项save或revise，route.fetch先取得真正已COMMIT的响应，暂停向页面交付；在等待期间用现有可达控件输入新文本，或明确切换到另一记忆编辑身份，再释放原真实响应。确认晚到回执不覆盖新输入、不静默改绑新owner／ID／version／revision／hash、不清掉新草稿；原命令只一次effect、原key／hash收据可读。若两种可达路径共享同一运行进程、无需重复提交可一并观察；本项至少真实覆盖编辑epoch变化，新身份切换按实际代码影响核。不得强制busy=false、写组件私有状态、伪造成功回执或绕开真实持久动作。

4. 引用响应晚到。从真实已存且当前有资格记录发引用GET，先取得真实响应并暂停交付；在同一页实际切换活动／记录／viewToken或卸载对应面板，再释放旧响应。旧原文／位置不得在新面板复活，新身份／已有显示保持正确，不能因为刷新又误发业务POST。实际Abort导致客户端不接纳响应是合格停止路径，但原服务响应与晚到尝试、切换时序、当前DOM／新身份必须可辨。用真实引用资格与存储，不用fixture编造citation成功、手工假的ready或直接patch序列变量。

四项各给executed／status／明确检查值和证据；网络请求与响应时间线、真实控制器等待点、POST次数、最后DOM／草稿绑定、PG行／预算快照、最终source／fixture／dist／加载字节与进程出生身份都足够独立重建。密码／session token只内存，不保存认证头；来源与正文均本卡合成，截图无需复制长payload进报告。

不因其他V01—V24的有限边界追加穷举、全旧model／tool／PDF／Windows停树、全数据库破坏或恢复测试。续作01DEF020／021真实子证据、DEF019既有精度例及不受影响的旧契约直接继承。catalog只读确认最终指纹足够，不再部署三函数。历史purge收据和UNKNOWN必须保留。

若本轮产品未改，只补新直接证据并核最终bundle身份。若必须改直接源，一次最小修复、必要离线／最多一次build，明确最终版与已运行版影响，复验改变过的四项分支；没有新变化不扩大复跑。主组合已经通过的子项，在字节和前提未变时可精确继承，不为把整体FAIL换成PASS重做已提交效果。

三次根上限包含主组合与最多两次有据受影响补验；同根因两次有依据修正仍失败、根因不稳、源码或资源漂移、范围扩大或任一相关额度触顶即停受影响项，保留所有原件、完成不受阻封装。不用异常掩盖原提交事实、未确认或计数，不暗开诊断根／第四批。

稳定完整G9候选才由编排另派计划中的TASK104/R098集中隔离增强审计。审计仍必需，但不先逐这四项审计；你不占共享号或自签最终通过。

## 停止与回传

达到四项与最终封装立即停。在独立300秒精确收尾本卡PID／出生／命令身份和pg1 CID，核18103／55443及自有Chrome／driver／可选监督树无残留，Running=false／Pid0；核pg2／3仍Stopped。保留容器／卷／库／角色／原数据／profile／失败和旧报告，不删合成行，不杀其他服务；非零退出与未知照实。

结果先写完整候选完成或具体部分停止、四项逐项直接证据与实际变化，再写继承边界、最终输入／代码／SQL字节与加载bundle、命令／失败／修正、原新累计账、收尾／偏差／未知、独立审计输入和需要同步事实。保留当前41022字节历史并给suffix hash核对；SQL文本与原字节hash分别标口径，不混同。

每实际根／build／离线批先存as-run完整源和测试副本与hash，批后比对；源码未改则引用已验281份冻结副本加当前核对，但新增脚本需存本轮完整字节，不虚称此前已经运行。证据只能表示其真实版本与条件。末改未验证明确列not_run，不能称整卡全过。

保存并确认可读后只回复一句话结论和 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-103-result.md 的可点击绝对链接，供用户带回编排。不能填写编排最终验收或申请把剩余时间当新许可。

## 必要人工与待同步信息

用户只需把本卡当前前缀转交原TASK103窗口，完成后带回原结果路径。G9-P不用重批，无需用户密码、真实provider、安装或用户库操作。真正关键缺口才给最少具体问题并继续不受阻部分。

执行者只报告待同步架构／状态／偏差事实，正式DocuS、TASK／R／CHG／DEF与总状态归编排串行维护。经验仅提出已确认且有真实验证的候选，不自行改公共库或记忆。

## 以下为已结束的续作01与初轮合同历史

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
