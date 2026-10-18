# TASK-117 / R-111 — S03 SQL修补、业务余项与集成收口

## 目标与交付

你担任本卡A+工程执行者，继续原TASK-117的一个完整S合成集成成果。先解决当前可定位的数据库不一致及运行阻断，再连续完成两条业务链、兼容恢复、预览和交付资料的实际余项，统一返回稳定候选及准确证据包。你不承担独立审计或项目最终验收。

原AP1产品合同继续；本卡明确新前向执行许可S03，替代已交回且根额度耗尽的S02业务执行权。旧TASK/R、源码、已提交事实、失败、超额和账目保留，不重新立零账。不能直接再次运行root09、root11、root12或root13等旧入口。

本文件是当前完整有效执行卡。以前的完整卡原字节保存在 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/orchestration-s03-20261015/before-documents/TASK-117.md，仅按具体历史问题追溯，不逐段重读全部旧补充。产品验收原文仍以116冻结合同为准，不因整理当前卡而失效。

完整结果仍保存到 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-117-result.md，S03段置顶并原字节保留现有31949字节结果及S01历史。新执行证据在 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/execution/continuation-02/；唯一执行主账仍为原 execution/budget.json、events.jsonl，不另起一份累计账。

## 项目、规则与窗口

根目录 D:/shspic/project_NO3_RetroLume-agent；入口 D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。当前task_model/V4.0，公共AGENTS修订CHG-0003，阶段07，需求v1.3、架构v1.36、执行动态v2.63。公共只读根 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4。锁定AGENTS、WORK、模板及00/05/06/07指纹在 DocuN/evidence/v4-migration-20260930/rules-snapshot.json；已读未变材料复用，不自动采用公共后续版本。执行者读取入口和锁定公共AGENTS，不接管WORK所规定的主控裁定。

继续刚返回S02部分结果的原A+工程窗口。其Sol账号额度不可用时，可由一个有可用增强资源的接续窗口独占接手，原窗口保持停止；如实记录实际客户端/模型，不要求等待Sol。没有唯一写者条件则只读，不同时起两套工程。用户人工转卡/结果回传，不派子Agent、不自动转发、不建立常驻编排服务。

父任务TASK-116/R-110，当前TASK-117/R-111/STEP-018；沿用116设计中的相关需求/API/FLOW/DATA编号。G11、STEP017及以前充分验收沿原适用对象继承，不重审整仓。用户已“一并批准”AP1/AP2；本卡是在同一采用包内修补和验证，不新增用户库、真实付费或生产部署权限。

## 必要输入与现状

按以下绝对路径读取当前未变材料所缺部分，同窗已读有效内容直接引用：

- D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-117-work-decision.md 最新S03裁定。
- D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-117-result.md 前51行S02报告及必要历史。
- D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/orchestration-s03-20261015/received.json、continuation-permit.json、input-manifest.json。
- D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-116/design/integration-contract.md、acceptance-contract.md、sample-inputs.json、adoption-package.md。
- D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/orchestration-20261014/adoption-receipt.json、resource-profile.json。
- D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/execution/budget.json、events.jsonl、case-index.json。

为避免重复长路径，以下C明确代表绝对目录 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/execution/continuation-01/，S03新材料目录N明确代表绝对目录 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/execution/continuation-02/。

- C/final-source-manifest.json、final-binding.json、result-save-receipt.json、final-budget-observed.json、final-resource-stop-binding.json及所指quota-recovery/final-stop-1792047466058959200.json。
- C/ordinary-db-fixes/pending-forward-repair.sql、adoption.json、derived-shape.json、before.json及两个pre副本；C/quota-recovery/PG-final-errors.json。只有最末版adoption生效，iteration01不是当前修补。
- C/source-closure-check.json、X03-X07-real-PG-only.json、root12-cleanup-1792045254766060400.json、root11-error-1792044433057294900.txt、root11-before/1792044426924248300.json、必要的SUP/worker原始诊断与transport记录。
- C/browser-3/proof.json、browser-4/proof.json及对应真实DOM/截图、memory-teaching-before-reopen.json、frozen-source-bindings.json、frozen-memory-binding.json、before-normal-reopen-pg.json、unknown-before-normal-reopen.json、bundle-5.json。
- 原controller/fixture的实际相关源码：execution/control.py、runtime_control.py，C/batch_runtime.py、frozen_http.py、http_remaining.py、pg_remaining.py、final_restore.py、preview_case.py，以及当前产品直接依赖。先读本次直接调用链，不重读全部旧实现聊天或所有证据。

主控已核：当前结果31949字节，sha256=5f2e0a19f893dcd6634345b86149d9a35de41354cb50f2694f76a024ba1c0c8d；113项最终manifest的现存/缺失标志与字节均相符，bundle5四项均匹配。014当前sha256=3a919b2562ded5765de132519b841c1d1439c65c001795cfbd608cbc03586e78；新R02预期shape=5b7dc68a94101307bcbd63a16607c5b2ee79906b5f32669d764853a55172dc12。旧source/compat库仍是旧014/shape，不能直接按新代码开正常业务。

最终bundle5主JS frontend/dist/assets/index-CMtT5rez.js，sha256=ff79970bb39382abbe668c13b73cba06befb65c4535decaa9ccfb44661cf43af；尚无实际HTTP/Browser加载证。build4的已成功动作按旧加载字节继承，不能把最终bundle生成等同于浏览器通过。

实际问题为：面试记忆invoker读取权限缺失；retrieval_chunk_guard局部row变量与DELETE别名c冲突；查询键95a0b55e-b5fb-45d7-ad6e-310f3bc4b572在007写入阶段CancelledError后返回UNKNOWN；root12实测内存降至约93MiB触发正确清场。诊断trace/state读取约4—5倍成本只是旁证，尚非UNKNOWN确定根因。禁止将全部问题归成账号Sol额度耗尽或只追加入口试跑。

## 第一步：有界准备和精确SQL前向修补

首条工具操作同次采集UTC/QPC，存本卡接收hash/真实窗口及新首点。先核当前无本任务在途资源、原首点和失败数，保存budget/events原件身份、S02返回回执和当前候选输入。S02返回时的active段字段不是继续跑旧业务的许可；新段采用按后述额度前向追加。

先完成有限离线走查，覆盖本轮将调用的入口/参数、DSN角色选择、profile/source与恢复目标区分、API/Browser关闭顺序和预期字段。只对实际修改或阻断处补必要检查，不重跑整套旧测试。先把每个阶段的预期和失败后可独立继续的部分写进一份本卡执行清单；这是卡内步骤，不先交“准备卡”。

主控已对照010/011/014源码确认：五个新增SELECT目标确为memory_revision_readable及其invoker传递依赖；接收者是既有NOLOGIN、非superuser、NOBYPASSRLS的retrolume_interview_owner，而不是普通app/PUBLIC。014差异只有这项只读补齐及删除分支别名更正；前向SQL中的函数体去空白SHA与新014均为2b8801abe7c42eaaa8c2ffc5e4117e251c459c593110c16faf0016d696431bab。本次允许在精确source/compat合成库事务内应用这两个范围内修补，未签动态正确或最终安全验收。

应用前必须核精确CID/卷/数据库/profile、原受信catalog及函数身份、执行角色和当前ACL。pending-forward-repair.sql自带的单函数守卫不替代完整身份核对；新代码拒旧shape时使用独立受信维护检查进入修补，不跳过正常schema门去跑业务。原受信shape a3c9bc08f104ad5f6dfc03c3902ad720ea871f6ff94fab299210cd68befaedbb及旧函数4efdb6c4b774ef67c00534c26e7c1b9963d4341b6113a7d1c9ce339e0aaddf55必须与实际匹配或由明确已批准增量完整解释，未知漂移停止该库。

在原事务内最小执行GRANT SELECT与CREATE OR REPLACE，不重跑001—014链、不改001—013、不授写权/角色成员/登录权、不把所有表全授权。提交后核函数owner/SECURITY DEFINER/search_path、五表SELECT且无写权、可信派生完整catalog与新014/shape；正常入口只有核通过后才能使用。差异只能由上述明确增量推导，不能把实测库shape自动学成可信基线。

最小真实回归是带选记忆的interview.v2本地start和删源trigger实际路径。涉及删源/记忆修订的反例先核依赖，不破坏尚待完成的L01/I01父来源或所选记忆。必要时先用独立合成对象/可回滚事务验证guard，最终X10仍须真实提交删源overlay。业务行、预算、旧UNKNOWN前后不变的断言与受控测试动作分开记录。修补不应用到R01永久只读目标。

## 第二步：先关闭运行阻断，再完成最终业务闭环

UNKNOWN原键及其预留、007/向量事实按原纪律只读保留，不重发、不补造received、不退款。按原run_tag、generation、时间线、worker stderr、record_outcome/取消来源定位真实原因。可移除本任务高成本诊断trace对正常验证的干扰，但不能因此写“根因已确定”，不能关闭出网守卫/必需证据或放宽产品停止/退款规则。

在有新依据且明确改动后，允许一次最小正常检索提交对照，经真实仓储/SUP/Job验证合法received及007/向量一致，使用明确新测试意图并注明它是诊断对照而非原UNKNOWN重试。普通有据修正及必要复检在同一有限根连续做；两次有据修正仍同样失败即停依赖Native/模型链，不再换key或换root名称盲试。PG-only、只读恢复、离线与文档等不依赖部分继续完成。

首要业务目标是活动b7f32142-b5b3-4a5c-b561-f927bcbe1b6d的最后answer/revision16之后的合法评价、独立次数及理由，和R+M面试I01。每次先GET实际head/原键/资格/四账；成功已提交的goal/path/select/exercise/answer/expose不新造key重放。该活动与记忆教学bbe0617f-0417-4490-8a8f-354ab0e10ae3分开核。当前readonly/过期/取消不绕过；若旧活动已经到deadline，只读留存，需新合成活动时明确记录新场景和不可继承的资格，不能改旧deadline、用导入伪造新表现或宣称旧活动已继续。

用最终正式bundle实际完成一条教学链和一条R+M选记忆面试链，覆盖错答、针对练习、参考曝光、真正新实例、受助/独立计数、推进或保留理由、必要probe、支持回答/反馈/finish及来源可回查。先零费开始面试再确认索引的本轮产品修正应实际验证，未获得目录/索引资格前不能先消耗新模型预算。两域的所选记忆只影响解释方式，不冒履历或能力证据。

L02—L09/I02/I03按116矩阵分S与Q验证：确定计算、协议、保守决策及失效传播用实际受影响层覆盖；未变算法充分旧例可继承，新profile分支给必要新断言。只有真实供应商才能证明的语义保留给Q，不让S模板正确冒Q，也不要求把每个确定反例重复跑完整Windows/UI链。程序题仍不执行用户代码。

X09必须使用同一未过期normal库/活动的真实停止重开。先保存学习回答、面试probe回答、unknown及四账基线，正常启动器/原stdin与句柄结束后同CID/volume/profile重开；GET原事实无自动POST，再显式产生新的合法feedback与后续理由/面试反馈。只启动过一次start_local、只读看历史或另建活动均不替代本项。

## 第三步：恢复、故障传播、固定预览和交付收口

P02：已有R01真实装载/seal/普通UPDATE42501事实有效复用，只补新reader的应用GET/只读查看及拒POST；不重建成功目标，不升级到014或normal，不fallbacksource。R01精确旧链/旧profile字节保持。

P03：在正常源中保存新shape下合格received/query、两个space、512维float32摘要、007绑定、grant非执行元数据、unknown/预留及真正已提交的删源overlay，再生成R02包。原6向量/22received/22份007一致仅是已有源基线，不冒往返。使用原已许可r02与r02-fault两个独立slot，真实装载/核对/seal/应用GET及拒所有写入；损坏维度或hash的目标必须failed且不激活，不能把failed目标清空后复用为成功。新副本永不获得grant、lease、密钥或SUP执行资格。

X02/X04/X08/X10及其它实际余项按原矩阵作代表性精确验证：新profile/新kind变化要覆盖，充分未变层继承；同键/CAS/整步预算PG证明直接复用。晚到/刷新/断线必须真实经过新前端意图与后端持久事实，纯route假响应不冒端到端。危险删除/修订使用可区分的独立合成对象，在正常主链所需事实完成后再执行；原UNKNOWN/失败/费用元数据保留。

PDF原两次HTTP422仍未闭，孤立worker两页成功不替代HTTP逐页确认。本卡允许先按两次实际HTTP错误、API/受限worker上下文与原成功孤立探针完成一次离线根因核对；只有取得新的具体根因、完成范围内普通修正及有区别的定向检查后，才可在本卡一个阶段内作必要HTTP复验，绝不裸重试第三次同输入。同根因仍不能解释则冻结PDF依赖，完成其它目标后给具体缺口，不把“暂不跑”写成无需验收。若修复要求降低PDF隔离、改持久模型或新增服务，停依赖交主控，不自行实施。

L10复用固定v2-08已审宿主，不重跑G11全套。先有本轮合法父feedback和有限description/artifact，正常operator配置/验签，实际d120/t120读1、t240读0.5、拒t0/未知字段、reset回1，保留真实ACK/PNG或可信读值、父/description/artifact身份及原StopProof/EOF/双Job/CID闭包。一般UI与实际宿主可分时，必需U门保留，不用静态图/mock冒预览。

正常operator授权继续：原 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/orchestration-preview-config-20261014/notice.md 的真实112审查依据不变，内存随机key仅正常API子进程env；可按本轮新启动正常rekey，保存旧票据身份，不向用户索密钥、不伪造新审查、不改验签器。固定image sha256:ec3c70c7a8a8894c647a69b08b0c296727bb052f639e487567e9cd4624766789、load 8a047050ffe584dffa6e85222c16c8f400c0ab4db82f72a32812c2befd082b3f、renderer 6cc300164a6cb364d9bd0bae4897f06d3f6a65cf5d4272477d2bccde67312597、kernel 6.6.114.1-microsoft-standard-WSL2继续；image/内核真实漂移先停预览依赖。

完成README、实际config示例与preview部署说明的已批准本机步骤，明确层级缺配、只读恢复、显式操作、合成/真实区别及具体未开放项。构建与实际HTTP/Browser加载精确绑定，最终case-index分别给S层结果/Q未启用，不用“28场景全部未过”掩去充分分层证据，也不把这些分层证据凑成全场景PASS。

## S03明确前向额度

许可标识 TASK-117-STEP018-INTEGRATION-S03-20261015。收到后首条工具同次UTC/QPC为新首点，日历48小时，活动21600秒含末1800保存清场；18000秒后不扩新目标、19800秒后仅保存清场。S01/S02的原首点和超额不变，新段不是重启旧时钟。新段启用前先保留现有budget原件/hash，再前向登记S02交回事实/已停线、新段与新上限；不覆盖旧段字段，不将用户转卡期间无业务的间隔伪作真实运行。

基数是已返回S02最终观测：S01活动37651.0027854、保守持有16219.360、offline1724.875；S02保存时活动17303.702146、保守持有5702.094、offline821.686。主控核证此时累计活动54954.7049314、保守持有21921.454、offline2546.561。若核对发现返回后还有实际动作/未计时，先如实补入，不能用本基数覆盖更大实际数；本段新增额不随旧账补录而扩大。

本段新增活动21600、实际运行/保守持有10800、offline3000秒，并保留原全任务offline7200总门；按目前基数前向累计活动76554.7049314、持有32721.454、offline5546.561。PG区间并集另存，不能用PG728.626秒替掉root09保守持有。不同计时域不得直接相减，首采不明按可靠点保守计时，不自行退款或追造历史。

最多4个新的完整真实目标根，旧13全部保留，S累计17，TASK18且未来Q保留1。建议四个目标为SQL/最小正常提交、最终两链及同库重开、两种只读恢复、预览与剩余传播收口；依赖可合并，全过即止，不强制用满。纯离线检查只登记离线投入，不再为每个脚本占一个真实根。各真实根仍2100秒业务+300秒清场；根内普通修正/复检不另开新根，精确清场后可在原截止内续同根，必须保留每次尝试、原首点/截止和累计启动数。截止已过不得复活旧根。

新增启动上限为PG12次（累计28）、API8次（累计19）、正式build2次（累计7）；Browser只使用原剩4次/累计8，不增加；Native累计160、HTTP3000、preview create/start各12保持。PG create attempts8/物理对象5/卷5总门不加，当前三者均3；仅剩两个已批准恢复slot可成为新对象。新段每项新增与累计门同时核，所有失败/启动预记保留，原未发生启动不伪造计数，预检失败不冒创建成功。

根开始前记录完整目标、前置和子预算，在一个独立有界资源控制器里登记所有自有PG/API/browser/preview及精确清场，不为等代码/审批让PG空转。内存预检纯读取不冒一次实际browser/PG启动；旧根的历史计数不重算。出现普通夹具错误时按因果修正并在同根原截止内必要复检，不再“每几十秒失败即换一个根”。业务/资源总门先到仍立即收尾，不暗开第五根。

官方只读核查沿原S02剩余页面额，不因新段重新给18页；不为S已知问题泛查网络或加新调研任务。Q仍关闭，真实供应商调用及实际费用0，原AP2 80次/20元条件性许可和旧13元已用账不变。本卡不启用Q，不把自有合成传输花费当真实费用，不静换provider/model/dimensions。

## 低内存、精确资源与写入边界

低内存profile继续：默认PG1，第二PG仅恢复必需短窗且API/host Browser/preview先停；基础/单PG/API前物理可用512MiB，host Browser/第二PG768MiB，固定preview1024MiB，Docker暖机后每次实采。约2秒采样，两次连续低于256MiB自动拒新动作、先消费者后API/PG精确清场，不能依赖下一条工具批准。

内存仍不足时只停本任务可拆消费者后再采一次，仍不足则停该依赖，不循环唤醒/等内存、不反复要求用户腾到2GiB、不降低浏览器sandbox/PG和preview隔离。93MiB实测说明设备压力真实存在，新的入口数不被当作解决压力的方法。本段同一种资源组合再次触发压力后不再以相同组合连续试跑，完成其它不依赖工作；恢复前须有可验证的环境变化。

PG image固定 sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f；1CPU/512MiB/pids128/restart=no/仅回环绑定，卷保留。source CID=1df68961975a43929fa06f63314a0da6e4e5cea113e3c403fc1ffd90d7c0fa5f、retrolume-step018-syn-source/source-data、15481/step018_syn；compat CID=0741d770fe07cc145660929044c471ef73fee11bb58e3ee6593e9a47adaa67c8、retrolume-step018-syn-compat/compat-data、15482/step018_compat；R01 CID=185cb0ca16203196597ac4c4e00b99b5725fe9806f72e2046d817f913e0f51d4、retrolume-step018-syn-r01/r01-data、15483/step018_r01。卷全名均为对应完整container名后加-data。

未创建的r02/r02-fault只可用 retrolume-step018-syn-r02、retrolume-step018-syn-r02-fault，同名-data卷，15484/step018_r02、15485/step018_r02_fault；API18118，host Browser1、preview1，原preview每活动3次/180秒不改。启动前核CID/标签/镜像/挂载/端口，不重建原source/compat/r01。旧S01资源标签保持，追加S03复用权不伪造创建身份。使用本TASK117安全loader中的自有synthetic凭证，不读其它任务private或用户DSN，不在argv/日志/正文输出秘密。

允许修改仅为原AP1影响范围及113项登记对象的必要直接依赖、step018测试/fixture、原执行controller与本轮新证据、README/配置示例。包括014及其R02可信profile、retrieval/typed embedding/新领域profile的普通修补和当前前端接线。旧001—013、已验固定renderer/验签器/Job与退款主体、依赖锁、公共库、用户原始需求、共享DocuS/任务卡/裁定文档/Git均不写。新的持久字段/服务/模型、放宽权限或改变既定停止/退款语义需停依赖回主控。

不安装、联网拉取、建镜像、改全局Docker/WSL/系统配置，不按名称批杀用户进程、不动旧任务容器/资料。禁止为清场清库/删卷/覆盖失败原件；X10批准的专用合成资料删除、记忆修订/撤销等真实产品动作不等同于随意清理，必须按冻结用例身份与预期执行并保留事实。

## 完成、停止与统一回传

当前运行门需要修补的数据库与正常提交对照确实通过后才进入其依赖的大业务链；这是真实前置，不再预跑整个全套。局部失败后继续不依赖部分，在同卡内完成全部可执行成果。所有检查只补实际变化，充分旧证据直接引用，不写mirror实现的mock/SQL字符串断言冒事务证明。

同缺陷两次有据修正仍失败、根因无法稳定位、越原采用范围、停止不明、资源条件无法满足或任一上限先到，保存实际结果并停受影响动作。一个已到门的完整目标不可换名称或换窗口复跑；不能通过移除门、强制勾选、改断言或造回执使其通过。平台账号/审批服务限制仍按真实类别记录，已有独立有界控制器收尾，不机械重试。

本段作为一次合并收口：结束时必须给稳定S候选，或给可定位的剩余产品/物理/平台阻断及最小待决动作，不再只报“额度到了再加一些”而不指出实际改变。未满足Must仍未满足，不保证设备能运行全部矩阵；某项受限不能冒STEP或项目通过。恢复/SQL、普通UI、preview各自实际证据层分开，不用纯模拟顶替缺失动态项。

结果先一句准确结论，再按实际完成/未完成和证据导航、文件pre/diff/post及as-run绑定、28场景的S/Q分层、全部失败/UNKNOWN/偏差、各段累计计数/时间、CID/进程birth/端口/StopProof、当前硬阻断与待同步文档收口。历史失败原字节保留。确认 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-117-result.md 已保存可读后，只回复一句话与可点击绝对路径。

稳定完整S后由主控安排一次新隔离A+集中独审，重点新kind/权限/源白名单/共享外发预算/原子提交/R02传播与停止。实现者不自签；不在本卡普通修复之间逐项插审计，也不提前启真实Q。必要人工仅转交本卡并带回结果，不索用户密钥、不逐次审批普通步骤。
