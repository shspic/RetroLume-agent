# TASK-097 / R-091 续作01当前有效

结论：当前产品的首次学习→持久成果→原文引用→显式续问→刷新恢复与有限客户端反例已补齐；本卡仍如实部分完成，最终SUP观察器修正02的完整业务动态补证因新增8次SUP额度用尽而not_run，未自签G7或独立终审。

实际可用流程：配置本地存储及已批准的有限活动/模型/learning配置，在「学习活动」选择就绪资料并零费创建活动，填写目标并确认范围、服务用途与额度，点「确认并开始学习」。成果以答案/追问/不足/冲突分别显示，可点击TXT/MD行段、PDF物理页或用户补充引用，再显式续问；整页刷新只读持久结果，断线/未知不自动重新调用。意图台账损坏或保存失败会阻止依赖恢复的新写动作，读取/取消仍可用。模型HTML作为文字显示。学习入口缺配关闭、旧L0/L1仍按实际配置工作。

本轮新增真实材料根：[续作01证据导航](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097/continuation-01/evidence-navigation.md)。[当前T01—T18矩阵](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097/continuation-01/current-matrix.md)同时给通过、复用、FAIL及not_run。实施前原合同：[implementation-contract.md](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097/implementation-contract.md)。本结果初轮全文原字节保留于后段，禁止用本段覆盖原失败历史。

## 身份、范围和A—D成果

TASK-097 / R-091，原实际A+ Codex desktop同窗续作，系统基于GPT-6；精确客户端模型ID未提供，未伪称其它型号。工作目录 `D:/shspic/project_NO3_RetroLume-agent`，PowerShell/functions.exec、既存backend/.venv Python、Node/Playwright、Docker/psql、真实Windows launcher/SUP/Job。时区Asia/Shanghai；当前冻结时间 @@FROZEN_AT@@。单执行者串行，无子Agent，无096审计窗口，无独立验收。

采用task_model/V4.0/公共AGENTS CHG-0003，七项锁定hash实核一致；最终需求v1.1、架构v0.74、执行v1.96。关联原STEP006/007/008和009意图子集、FR002/003/004/012、NFR001/002/003/004、DR001/003、SEC001/002、CON001及原MOD/FLOW/API/DATA范围。授权仅合成候选产品/验证，无真实provider/外网模型/费用、用户库、主模型、发布、迁移或停止/权限扩展。

|组|当前成果和真实状态|
|---|---|
|A 原合同|初轮已实施前冻结learning.v1/terms.v1、稳定首次槽、可信目标/目录、原子结果、幂等/恢复和矩阵；本续作不重开设计。C/verification-plan和补充计划在各资源入口之前保存。|
|B 产品|初轮7个learning模块、受控profile薄适配、两个只读仓储助手及API既有职责细化均保持冻结。当前first/followup经真实链规范化目标/catalog/body与received同事务；伪字段/假确认、有限额度、来源撤销及真实硬停/声明恢复有当前反例。|
|C 客户端/使用说明|初轮目标确认、结构结果、引用、显式续问、意图匹配/迟到保护及README均保持原最终字节；本续作实际最终bundle和14个不同浏览器场景补齐主链/恢复/写前关闭。无新build。|
|D 验证/证据|当前主链、原子PG/HTTP、真正SUP截止与一次折叠、14有限UI场景成立；新增夹具两次观察落盘故障保留FAIL，最后不可变记录修正只经Windows文件并发，完整SUP业务not_run。最终快照/差异/构建服务绑定/逐项矩阵/累计资源账与收尾已保存。|

|续作组|结果|
|---|---|
|S1|谱系07→08→真实库/原件冷复用、显式许可/累计停门、独立场景和观察器已实现；原子替换观察文件在Windows并发读期间仍遇PermissionError，修正02改为不可变发布/partial句柄交回。文件并发通过，最后完整SUP业务未动态验证，因此本组不报完整通过。|
|S2|通过当前主链及当前严格确认/profile守卫：一个新合成活动真正首学/续问、两个send、原子xmin/body/hash；已保存07成果冷恢复/整页刷新0学习POST。|
|S3|真实来源撤销、当前HTTP限额与伪引用、真实SUP硬停及显式已有恢复声明下折叠一次通过；不同目标HTTP竞争唯一槽/send及不套旧body成立，额外两完整SUP生命周期断言FAIL。|
|S4|14个不同有限场景有有效当前证据：09有效7、10有效5、11有效2；包括冷读/刷新、完整主链/引用、丢回执核对匹配/冲突、未知同键重试/放弃、坏台账/保存失败、缺配、坏引用/XSS、慢回包/切换/卸载、隐藏暂停与非重叠轮询、主动外部请求阻断。|
|S5|当前产品/资源/证据冻结与完整结果回传完成，准确保留初轮/09/10FAIL和未测项；不据此给整卡或终审通过。|

## 当前接口、字段与信任归属

接口未再改变：`POST /api/activities/{id}/learning/first` 仅 `{business_key,goal,confirmed:true}`；`POST .../learning/followups` 仅 `{business_key,parent_operation_id,question,confirmed:true}`；`GET .../learning/intents/{key}?action=first|followup`只读事实；`GET .../learning/operations/{operation}/citations/{citation}`只读真实原文位置。原activity四类读取、create、cancel、continuations保持。confirmed必须实际bool True，1/字符串/false均422；额外profile、scope、路径、ready、来源正文/预算/模型URL不可授予权限。

首次operation为稳定 `learn-first-v1.<规范请求SHA256>`，客户端不同UUID不另造首次槽；续问为 `learn-next-v1.<新业务UUID>.<规范SHA256>`，合法当前同活动model父成果/摘要与scope CAS仍由G4/准入复核。摘要绑定goal/question、来源实际版本/revision、scope、profile、父结果与输出上限。相同输入返持久事实，异输入明确冲突/失败关闭，不能把旧答案当新请求；未知不自动换键或重发。

public学习JSON归现有通用结果body：版本、action、request_sha256、可信goal/question、scope、来源目录catalog/有限模式/能力限制及四类结构result。内部history、父payload摘要/消费凭证不进入public正文或模型外发；模型自报goal/source/verified不能取代应用事实。每个catalog含不透明lc ID、真实source/version/source_revision、原件/unit/fragment hash、行段/offset或PDF物理页、origin_kind和补充身份。source_revision合法域0..2147483647，发布后取仓储真实值，不人为加一；09撤销负例用实际合法修订变化，非产品删除功能。

限额仍为目标/问题1024字符/4096UTF8字节、24词项、10来源、原件总5MiB、PDF50物理页/100units、候选512、top8/12000字符/24000字节证据、结构输出小于16KiB、学习输出1..256token。无tools、无Embedding；词项有限召回/引用位置合法/结论支持分别呈现。结构/引用规范化发生gateway原record_outcome之前，body与received同事务；不新增主要表字段、DDL、第二份状态账或提交后补写目标/catalog。

恢复限制有真实证据：产品HTTP使用既有默认 `single_host_single_session_recovery=False`，旧running预留未知时失败关闭、保留R与旧有效成果；不是自动重试入口。10仅在本卡已限定同主机/交互会话、旧SUP/树已零的受信内部现有入口显式声明既有前提，验证G递增/保守90秒折叠一次及后续同key HTTP返事实；没有给产品HTTP新增该恢复配置。系统硬杀worker时gate的Python finally不适用，实际Job终止/树零才是停止证据。

## 当前pre/post、有限diff与构建绑定

111初轮最终对象和七规则逐项校验一致，并保存pre原字节；receipt SHA256 `319e4fb39b8226cdbd904a1820dcecb3d176074c22d9170a1ec9f95cb9bfe220`匹配。本续作backend/app、frontend/src/dist、README及产品示例配置均0字节变化；没有Git写入、依赖安装、核心停止/写锁、materials/pdf认证或核对主体变化。完整初轮产品差异仍见原changes.json/limited.diff，不用Git基础提交替代真实pre。

当前快照 @@FILES@@ 文件，本续作新增/修改 @@CHANGES@@ 个必要夹具/定向测试/证据代码；精确列表、pre/post哈希和完整有限diff见C/post-manifest.json、changes.json、limited.diff、final/files。主要新增persistent_fixture、continuation_runner/run/repair/ui、publication、task097-continuation浏览器与两个test_learning文件；resource_runner仅显式许可分支，bootstrap只本卡观察器/边界注入，browser_run修谱系复用、processes认真实created身份。原普通入口8次用尽仍拒绝，最后已用23 SUP不再允许任何新监督启动。

构建未重复：原 `build-05-complete-inputs` 命令/原始输出/16输入全hash与当前一致；09实际页面执行HTML/JS/CSS/PDFworker，四类成功取回字节与当前dist比hash。C/build-binding.json串联原构建→当前源码/输出→真实服务，资源名从真实产物发现：index.html，assets/index-CYYBTgCl.js，assets/index-C8N4OxWs.css，assets/pdf.worker.min-Dswkl-cV.mjs。原build04相同事实保留；初轮build02浏览器身份不冒充当前build05。

最后夹具变更的适用性：正常业务产品字节均直接绑定09/10；客户端写前关闭绑定11。bootstrap/publication/processes修正02对最后SUP业务完整运行not_run，只有Windows文件并发/compile、11无SUP app启动的证据。原脚本全部as-run保存，到当前不同文件逐项列出，不能以编译覆盖必要动态缺口。

## T01—T18与真实运行导航

18项的预期、当前实测、精确方法/场景、旧复用和限制在 [current-matrix.md](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097/continuation-01/current-matrix.md)。T08/T15对最后不同目标竞争的完整SUP生命周期补证仍部分，T18保留历史缺件/最终观察器not_run；真实provider/Embedding/OCR语义质量、完整删除Must、全部STEP和发布均未完成或不在本卡授权。其余有限目标不因此扩为全系统验收。

|实际命令/批|退出/业务秒/清理秒|已成立/未成立|
|---|---|---|
|backend/.venv/Scripts/python.exe -B backend/tests/fixtures/task097/resource_runner.py combined --permit continuation-01（累计09）|1 / 283.000 / 0.641|当前首续/引用/冷恢复/四产物、来源撤销、严格API、硬停通过；两个恢复UI前提不足/轮询glob错误、默认HTTP恢复拒绝及观察计数JSON失败原文保留。|
|同一入口 repair --permit continuation-01（累计10）|1 / 20.828 / 0.594|5个浏览器失败/未覆盖项通过；已有恢复声明折叠及HTTP边界通过；额外两完整SUP回执断言因观察器PermissionError失败。|
|同一入口 ui-only --permit continuation-01（累计11）|0 / 11.328 / 0.609|两个写前关闭场景，0SUP/0send、费用/请求预扣0；精确新活动清理，旧恢复样本保留。|
|C/control.py c01-offline-01/02-repair→offline_checks.py|均0 / 1.407、1.203秒|源码compile、Node模块、5当前严格守卫方法通过；02重复了未改变的5方法，属不必要复跑，预算如实计入，不算10个新方法。|
|C/control.py c01-offline-03-publication→publication_run.py|0 / 0.500秒|1个真实Windows文件并发方法：150不可变发布、并发读无错误、拒覆盖；0进程/0SUP/0Job，仅观察文件层。|
|C/control.py c01-offline-04/06→resources.py|均0 / 1.407、1.313秒|10之后与11之后的实际只读资源结束核实，后次因新增UI资源而必要。|
|C/control.py c01-offline-05-ui→ui-preflight.py|0 / 0.422秒|仅新增UI夹具模块/源码就绪，无资源启动。|
|错相对路径的PowerShell启动命令|1 / 保守1.342秒|Python/测试未启动；tool输出转录与实际修正绝对命令保存，非资源入口/非模型失败。|
|C/finalize.py 最终整理|0 / 保守30秒|实际measured与保守charged分列于artifact-assembly.run.json，最终保存/readback与快照，不当业务或动态通过。|

所有资源入口命令/预期与被测源码/runner/fixture原字节在C/as-run/{batch}/manifest.json和files；实际应用/SUP/worker导入hash与各批post-hashes已绑定。原始二进制stdout/stderr、场景错误/请求时间线、真实transport/response/session/gate/Job以及PNG/HTML都保留。当前14成功浏览器截图与09两个失败截图有可读原件；poll被有据终止未伪造截图。没有任何汇总FAIL被改写绿色。

## 失败、修正、未完成及偏差

1. 已知07/08谱系复用缺check的夹具风险改为07真实首/续→08reuse→当前PG与原件hash验证；原恢复样本不纳入新清理集合，没有再生成旧首成果或人工插body。
2. 09恢复UI未选活动却等待通知、poll用有问号glob而实际列表无query，修正01补真正页面前提/pathname、有界屏障、独立场景；原FAIL保留，10实际仅复验失败/未覆盖项。卡住Node只在PID/创建时间核实后定向终止本卡树；即时zero=false未当通过，finally与最后资源proof确认真实zero。
3. 09计数记录被并发读到截断JSON，10原子os.replace在Windows读句柄期间又遇PermissionError；第二SUP已创建未Resume，原tmp记录真实PID/创建时间。该启动计入8，不能按claim少记。修正02不可变计数/独立created记录、发布失败partial交原launcher cleanup；Windows文件层通过，完整业务动态not_run。新增SUP8达到许可，停止受影响补证，剩余入口/秒数不作为额外启动许可。
4. 09默认恢复声明false的失败关闭是真实既有权威，10内部显式已有前提路径通过；不把内部配置路径当产品HTTP新功能，不改变停止/退款参数或持久模型。
5. 09/10“额外两完整SUP生命周期”断言均不成功，其中09未到CreateProcess；真实不同目标请求/唯一槽/唯一send与失败关闭有限事实成立，但不足以宣称两份完整Windows竞争绿灯。最后夹具修正02未运行完整SUP，新普通model兼容未追加（旧有效链复用）；初轮普通调用缺SessionOutcome始终保留。
6. 子运行cleanup与外层finally都检查同一process-cleanup文件，后次记录保留零状态而初次动作明细未另存；完整累计业务/清理用入口真实钟，最后PID/树/Job/端口另有只读原件。没有用它推断未记录的初次清理命令耗时。
7. HTTP限额只做合法正常256、代表性1024请求/128活动输出及输入/profile上下界，未逐数据库CHECK全域扩测。真正完整删除、Embedding、真实provider语义/费用、用户库迁移、G7最终/全部STEP/M-1/发布均not_run或范围外。测试语义支持与引用身份合法分开，不产生质量百分比。
8. 最终证据组装第一次把旧offline12文档回读的inputs manifest当成产品files manifest，KeyError在结果写入前退出1；该次快照/已生成暂存文件与tool输出转录在C/finalization-attempt-01原样保留，实测0.990秒计离线。修正读取身份后仅重做证据组装，未重启任何资源/业务/浏览器；成功第二次raw stdout/stderr在C/finalization-attempt-02。

停止原因及仍未完成的唯一续作关键动态项明确如上，不能以文件压力测试、compile、app无SUP启动、未来独立审计代替它。原根post-manifest/final/files/evidence-applicability/build-binding/旧结果和账原字节保留；本轮使用新C命名空间。

## 累计投入、资源与准确收尾

@@BUDGET@@

口径：实际SUP计CreateProcess尝试，含未claim与创建未Resume；09另一次创建前JSON计数拒绝只列业务尝试，不虚加真实Windows会话。原15 SUP/14 SessionOutcome历史缺件不抹平；C/supervision-ledger包含23启动、原tmp身份补充和不同于启动数的回执数量。浏览器/driver按实际启动分别计，新3、总6/7已达上限。业务/预检/子段与子段清理包含在入口单调business；外层finally单调cleanup分别计，没有省略abort。主动为真实墙钟保守上界，初轮12681.232保留，人工交回间隔不计本段；不是精确键盘工时。离线保守30和错命令1.342与实测分列。

精确容器CID `e49d3acc3c1be13d670af68bca2b082fea4faeeb9b9babe69df7f1d3941696a4`、镜像 `sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f`、retrolume-task-088-g3-w1-data卷及1CPU/512MiB/pids128/127.0.0.1:55441白名单在每次start前全inspect内存核对，不输出Env。只复用retrolume_task097_g7/retrolume_task097_synth，重置本卡口令仅stdin/短期内存/子环境；未建库/role/容器/卷、未重跑迁移，未触旧088/092/095/用户库。

最终 [resources-final.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097/continuation-01/resources-final.json)：Running=false/Pid=0，所有本卡PID+真实创建时间匹配后不活跃，含10未Resume的tmp身份；现存后代为空，20个有SessionOutcome的适用Job读取为not found/树零，21份Job-close历史与初轮缺件分开。18097/15197/55441释放。097库、卷、07一活动三来源与09真实新主链样本保留，10/11新临时行定向清理；没有drop或清空库。每批cleanup_ok=true。清理没有杀别人，没有读旧Env/真实DSN/私有配置；只读最后核实不启动或终止资源。

合成网络守卫仅允许本卡loopback与已验证stdlib selfpipe；模型传输边界只在本卡测试进程替换，真实launcher/SUP/worker/Job/gateway/仓储主体保留。浏览器主动外部探针在context路由拒绝，未因其他上下文“没见请求”推为全机防外网。全卡真实模型/外网模型费用0；没有真实key、用户资料或外部源码/新依赖。

## 正式文档建议与候选经验（由编排维护）

操作者：本TASK-097原A+ Codex实现窗口；时区Asia/Shanghai，建议时间同本段冻结 @@FROZEN_AT@@。未写DocuS、公共规则、经验库或占用DEF/OPT/CHG新共享编号。

- `D:/shspic/project_NO3_RetroLume-agent/DocuS/架构动态文档.MD`：MOD001/003/004/005/006/007/008与FLOW002/003/005、API002/004/006、DATA002/003/005/007及FILE新增learning模块/四接口/可信内部profile与public结果JSON/两只读助手。保留无新主要模型/写锁变更、limited terms、公开body不含消费凭证、HTTP默认running恢复关闭、Embedding及完整删除Must未实现；新增真实SUPdeadline/显式已有声明折叠的证据和最终观察器not_run。
- `D:/shspic/project_NO3_RetroLume-agent/DocuS/执行动态文档.MD`：TASK097/R091续作01按本结果有限成果与部分状态接收，S2/S4具体场景及T08/T15动态缺口、新3入口/start3/SUP8/browser3/driver3和实际秒数累加，不能复写初轮失败/旧095/096；后续独立终审须由编排据未测状态另安排，不由本窗自签。
- `D:/shspic/project_NO3_RetroLume-agent/DocuS/文档变更记录.MD`：编排同步上述当前实际边界、路径/原因/操作者/+08:00时间，正式共享编号由编排分配，避免把内部测试恢复声明误写成HTTP产品开关。
- 可复用候选仅随根因/修正/真实验证导航交回：保留结果按实际谱系读、不把保留样本纳入清理；Windows读者共享删除导致原子replace仍失败，不可变计数/独立created记录与partial句柄保全；浏览器阶段前提/确切列表URL与有界屏障，显式POST观察窗不把自身算禁止POST。Windows文件修正未完整业务动态验证，不能作为已验收通用经验。

本结果仅候选交回，不给G7、完整STEP006/007/008/009、M-1、真实服务、发布或项目通过。达到已授权计数停止受影响部分，其他独立成果与材料已收尾。
