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
