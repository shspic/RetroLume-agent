# TASK-111 / R-105 续作03 — 修复真实根因并完成受信交互HTML验证

## 目标与交付

你是本卡唯一执行者。连续完成DEF-027修复、一个最小真实renderer闭环、正确部署绑定的两项正常业务闭环，以及G11剩余安全、事务、资格、预算和停止矩阵。完成或触发真实停止条件后统一回传，不逐项向用户索要同范围普通修复许可。

本任务仍为已采用的G11-P110。用户应能从当前学习答案或教学练习/反馈显式生成、保存、打开交互解释，在独立容器内调参数并看到重新计算的数字和图形，回查资料，停止并回到学习，刷新后按持久事实核对。主应用不可用本地模拟数字或静态截图冒充远端执行。

交付产品必要差异、M01—M12逐项证据和复用依据、真实工程账及精确清场。完整结果仍保存到 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-111-result.md，置顶“续作03”，当前75828字节原报告完整保留为原字节历史后缀。新证据进入 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/execution/continuation-03/，不覆盖原失败、预算或as-run文件。

本卡是工程实现与验证，不能自签G11、SEC003/B01、STEP015/016、M1、整个项目或发布通过。完整稳定候选后由编排另安排一次隔离增强终审，普通修正不逐次审计。

## 项目、规则与接收安排

根目录 D:/shspic/project_NO3_RetroLume-agent；入口 D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。task_model，V4.0，公共AGENTS CHG-0003。公共根 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，读取DocuS/AGENTS.MD和WORK第2、6、8章适用部分。锁定指纹 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/v4-migration-20260930/rules-snapshot.json，不能自动采用后来版本。需求v1.2、架构v1.15、唯一执行动态v2.37，当前07。

关联TASK108/110的已采用合同、109封存反证、DEF-027/P1、FR009、SEC003、B01、STEP015/016、原四账与G3—G10。用户2026-10-10确认G11-P110，随后要求查清反复失败根因再编排；根因复盘已完成。本卡为编排在同一已批准范围内签发的具体合成工程许可 TASK-111-G11-C03-20261011。基础HostPolicy候选身份仍关联 TASK-111-G11-P110-20261010，不新增公开绕过授权。

接收A+，用户最强且胜任本工程的执行Agent；使用全新工程会话，实际客户端、模型与推理标签如实登记。原111窗口多轮历史许可与上下文混杂，现已停止并冻结；新窗口以本份唯一现行合同恢复。不是独立审计窗口，不同时让原窗口修改或运行，不派子Agent、不接管共享编排。

原任务编号、失败、原件和投入延续。现成结果为75828字节，SHA256 31a88d3f1ca1b724225eaafa33ca685a2eb526a88cb9082cd1b1b8692b32476c；66项交付源及七规则指纹在本次出卡前匹配。原109/global78封存，加111八根为86真实入口，不是86通过；旧13元及UNKNOWN不清零。

本文件替代全部旧111实际入口许可。旧合同原字节保存在 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/orchestration-continuation-03/prior-TASK-111.md，仅为历史，不执行其中旧时窗、旧root循环、额度或待转交声明。旧C02截止已经过去，不能用它挡住本卡新许可，也不能用新许可追认旧超限合规。

## 背景与最小充分上下文

关键根因已定界，先修原因而非继续延等待。renderer-host.cjs的compiledHTML使用字符串replacement，runtime.cjs第51行正则中含美元符加单引号，按JavaScript替换语义把HTML尾部插进脚本。15586字节固定脚本在HTML中被提前截成3352字节，CSP允许的完整脚本hash不匹配；三个旧构建版本都受影响。现有frame.waitForFunction候选没有修这条路径且不在最后镜像中。

两次真实启动日志的事实是trusted_frame中Runtime未定义；主控只读B类证明确定脚本损坏，没有伪造当次CSP拒绝日志。仍需判断正确字节后的异步加载与8秒截止，不提前宣称唯一根因消除或浏览器通过。

另有两个已知继续问题。policy_config_sha256包含image/load；已有活动预算拒绝不同config，所以旧部署活动不能直接用于新镜像的正常UI测试。c02_faults.py目前只实现normal_http，其它故障未准备，不能冒称完整矩阵只差运行。

按顺序读取必要输入，先读新合同和复盘，再读实际函数。新窗口不要求阅读全文旧实现聊天或全部嵌套结果历史。

- D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-111-root-cause-review.md，完整根因及规范链接；SHA256 f8f67827e5c79720ce7584388def0dc17b2e3fa37d7935dbe248dd1457c22547。
- D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-110-work-decision.md的采用段，TASK-110-result.md的C2—C7、D2/M01—M12；这是有效功能、数字、协议、权与安全合同，不重新选择方案。
- D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-111-result.md置顶本轮的前104行及按缺口引用的原件；需要旧实现事实时再读相应历史段。
- D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/orchestration-continuation-03/input-and-resource-check.json、continuation-budget.json；前者保存66项冻结源与精确资源，后者是本卡权威工程预算。
- D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/orchestration-review-03/review-evidence.json；用其中三个as-built上下文、脚本截断推导和现成stderr定位，不启动旧镜像复现已确定问题。
- 必要直接源 deploy/preview/renderer-host.cjs、runtime.cjs/css/html、renderer-bootstrap.cjs、backend/app/preview/compiler.py、host_policy.py、production_supervisor.py、production_reaper.py、process.py、host_job.py、docker_control.py、pipe.py、repository.py及012；task111的control、resources、http_matrix、c02_runtime_probe、c02_normal、c02_faults、c02_coordinator及必要前端解释面板。以真实调用位置选择，不全仓重审。

当前规则与源如与冻结值不符先定位实际差异，不覆盖他人成果。旧source、build-context、snapshot、结果和预算只读。新修改前留pre/hash，消费者停后再改源，新加载记录as-run；充分未变证据直接复用，不重采500项。

## 执行边界与资源

允许在以下既有范围做必要修复和补证。

- backend/app/preview内生产模块；012_html_explanations.sql只在本次确定领域缺陷迫使修正时修改，已应用原件保留，不重写001—011。
- capabilities/contracts.py、gateway.py、activities/repository.py、service.py、api.py、service_config.py、main.py与worker仅原HTML profile、binding、同connection hook和资格投影的必要薄适配；保旧admit/mark/record/recover/四账/UNKNOWN和Windows停止权，不重写旧核心。
- deploy/preview内新生产host/runtime/bootstrap、可测试的纯组装函数、production Dockerfile、公开manifest与已有版本许可；必要构建入口、README、deploy/start_local.py、compose.local.yml和config示例。旧109 host/wrapper/h0、缓存与已构建上下文保持只读，新context另建。
- frontend/src/explanations及原LearningResult、TeachingWorkspace、Exercise/Feedback、ActivityWorkspace的必要挂载和身份守卫；backend/tests相关交互域、frontend/tests/task111、backend/tests/fixtures/task111的本任务保留式夹具、runner与冻结故障variants。
- DocuN/results/TASK-111-result.md和本卡新证据目录。正式DocuS、共享编号/状态和公共库由编排维护。

禁止新引擎/依赖/数学库、修改锁文件、第五表或新权域、自由模型HTML/JS执行、任意CDP/selector/URL公开输入、用户原文/资料/库/local配置、真实provider/密钥/付费、联网安装/pull、旧109运行、特权/宿主挂载/socket/preview端口、Git写入、删除库/卷/image/证据/合成行或发布。越权负例只在本专库完整ROLLBACK；不得COMMIT DELETE来清样本。

沿用已采用的数据与产品限额。描述是interactive_description.v1，8 inputs、32 calculations、256 AST节点/深度16、图形合计128点、每更新50000步、13种有限数学op/reset；规范描述24576、固定HTML65536、artifact110592、旧正文131072字节，token4096还受原活动更小限。未知/重复键、UTF8、类型、引用、hash、非有限与能力字段失败关闭；文字只textContent、固定Canvas，无eval/Function/动态markup/URL/模型代码出口。

数字格点按规范十进制精确比较；有限数学语义、域和oracle按110执行。更新先完成整个候选快照，拒绝时保上次完整数值/图形/帧。编译/hook同COMMIT只做有限纯数据，不在短事务内启动或等Docker、网络、浏览器。合法结构不自动代表解释语义正确。

每活动预览3次/180秒、每窗30—60秒。t0在reserve前固定，准备/事务/启动均计入D，ready不晚于t0+8且不晚于D-10，D-10关输入；软停止2秒后外部精确kill，停止确认不延D。失败不退次数，UNKNOWN全reserve保持且禁新start；只有确认未启动或完整停止证据齐，才能按既有函数结束preview账。preview退款不触原模型次数/工具/费用/原生时间账。

只复用一个PG容器与卷。CID 1791a2d086228c618bf043b0565e215828ff0ccfe5a858486488f1329a16ef51，name retrolume-task-111-g11-v2-pg1，image sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f，卷retrolume-task-111-g11-v2-pg1-data，127.0.0.1:55451、1CPU/512MiB/pids128。main、upgrade、fault已经存在，admin/app/denied三个本任务角色保留，不drop/recreate。可核专属身份后仅重置这三个角色口令于内存/stdin/限定子进程Env，不输出argv、Env或秘密，不改其它角色权限。

renderer继续缓存基础c091b21d…、Node v24.18.1、PW1.62.1、Chrome151.0.7922.34及既有浏览器binary/许可来源，不下载替代。新派生生产镜像标签v2-04起，immutable image与load必须实际绑定。UID/GID10001、sandbox、networknone、readonly、CapDrop ALL/NNP/原seccomp、默认独立PID/private IPC、init/no restart、1CPU/1GiB及等swap、pids256、SHM64MiB、/tmp128MiB与/home/preview32MiB的安全tmpfs保持。一时只一个preview。API仅127.0.0.1:18111。

新preview名字限定retrolume-task-111-g11-preview-15至44，共30个。旧01—14均不得重启或再create；本卡每个name只对应一次新create/start，失败和未知也占实际计数。新名字序列与旧累计counter分开映射，不能按累计第5次直接选旧preview-05；真实计数继续从create4/start2递增，名字仅从本卡白名单选择。旧unused名字不是第二份余额。新合成活动与材料ID用本卡前缀/UUID定向登记，不触原旧活动预算；使用最终部署绑定的新活动，不能改旧budget config、重置starts或复制用户材料。独占写入，无并行执行者或审计。

### 本卡明确工程预算

同一份累计账继续。原真实根8、build3、PG start7、API3、主browser3、合成发送6、Windows6、frontend2、preview create4/start2、Reaper验证批2、offline批18；real6541.282、offline200.828、cleanup44.4247405秒及旧分类unknown/超限保留，不清账。本卡仅增加以下前向工程许可，不追认历史。

- 采用一个新的综合工作窗28800秒，自新执行者第一次读取本卡立即记录真实UTC与同机monotonic_ns、固定截止。原总体授权64800加本增量28800为93600秒，旧已过时窗仍历史，不重算起点。metadata、实施、相关离线统一包含在本窗，分类实记但不再各设中途停线门；推理、等待与修正都计经过时间。业务在总截止前600秒收线，清场不依赖业务state尚有效。
- 真实组合根累计上限14，已8，最多新增6；每根1800秒，新增真实经过最多7200秒且累计real不超过14400秒，两门取早。一个根内多个有据普通修正与子步骤不另开根，源码消费者停后新加载。不设300秒work-intent等卡外退出门，无工作且无需持有时主动结束；严重安全或所有目标结束才清场交回。
- image build累计7，已3，最多新增4，安排生产修复镜像1、必要冻结故障variant镜像至多1、两个有据修正复验余量。基础/许可/vendor复用，不为改标签、再查许可或相同源反复构建。
- PG start累计10，已7，新增最多3；API累计7，已3，新增最多4；主browser累计6，已3，新增最多3；frontend build累计5，已2，新增最多3。PG普通子项失败不自动停止，预留整卡后续和清场。最小renderer闭环已完成后，若确需较长离线编写故障、当前无消费者，可有意结束该阶段并精确停PG，用第二次start运行集成；第三次留有据资源修复，不靠任意短闲置超时耗尽start。
- 模型合成发送累计10，已6，最多新增4；Windows OneCall累计10，已6，最多新增4。优先只用两次建立正确最终部署下N1/N2的Native完整链，另两次留因真实修改确实影响对象绑定的必要复验。非法/UNKNOWN旧证据直接继承，不为每个描述反例重发；真实provider和支付仍0。
- preview create累计34，已4，新增30；start累计32，已2，新增30。新计划最多22个基线生命周期加8个相关修正名额。基线22包含最小核心1、正常UI2、原十独立故障、最多四种准确资格race、预算所需最多三个生命周期、两个确需独立对象的输入/失联场景；可合法合并同生命周期断言就不占额外名额。基线必须先按具体方法及对象映射，修正名额只用于新证据支持的普通修正。每活动3次/180秒仍成立，不追借旧已启动对象。
- 原Reaper验证分组2/3与offline批18继续保历史；本C03两者只记录实际分组，不另设与preview、根和经过时间重复的硬分组门。每个实际Reaper绑定本preview、外部截止、进程归属与停止要求，不能因分组门取消而无边界运行。
- HTTP累计5000、PNG GET3000、公开input300、内部input500、一时一个preview、一个PG容器/卷保持原硬限。cleanup累计1800秒、已44.4247405，另有总窗末600秒保留；业务到限仍按精确归属完成清场和保存账目，不暗开新业务。

权威数值见 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/orchestration-continuation-03/continuation-budget.json。启动任何真实资源前，把该增量合并进实际control/预算入口，保存旧budget原件并核旧用量不减、新门只有一份、旧C02截止不误拦、本卡总窗/单preview截止不被延后。只读metadata和纯文件预检不先占真实根；真正build、start、SQL/业务或浏览器动作进入对应真实账，预检失败原件仍保留，不倒改旧8根。

## 验证、证据与审计关系

按以下三个内部阶段连续执行，阶段完成不用转卡；达到整卡目标或停止条件再回传。

### A 修根因并取得第一个真实闭环

1. 先保存实际pre，修compiledHTML的字面插入，排查同函数的相邻replacement。可以用函数replacement返回固定script/style，或等价不解释美元符的组装；不得仅延长等待、改CSP允许任意脚本、删特殊字符或改变模型输入来制造成功。
2. 让实际生产组装函数可在无Docker的纯函数边界验证。使用该函数的真实输出，核script/style提取字节与镜像固定源完全相同、CSP hash匹配、无意外提前闭合/残留占位，并与Python实际runtime_html/compiled_html相同。包含已有美元符加引号触发以及替换特殊字符的辨别反例。不能在测试里复制另一个组装算法自证，不以Node require运行计算替代浏览器页面载入。
3. 一次相关离线批核完成后构建首个修复生产镜像，保存原context/pre/新source/manifest和实际image。先用现有runtime_probe模式与真实producer创建一个明确合成前提的新活动/产物，走真实PG预算、生产SUP/Reaper/容器、真实sandbox/frame/固定程序；不启动主UI、不发模型来定位这个固定程序。此证据标核心链，不冒Native/UI链。
4. 在原ready8内取得真实ready、实际iframe/target/URL与运行API身份、58.8及零边界ACK、真实PNG和停止组合，且无父页面本地写死读值。域错误应保完整旧快照。若未ready，一次捕获有限stage、browser console/CSP/脚本错误、frame实际URL、脚本文本hash和必要时序，区别页面字节、CSP、加载、程序异常和进程退出；停止本对象后按新依据修正。正常日志不输出模型/DB/owner秘密。不能只看到undefined再猜race。

### B 同一最终部署完成用户正常链

A完整通过后固定生产image/load。若后续改生产字节，重新冻结和补实际影响，不把A绑到旧镜像而签最终版。

建立该最终部署的正确新合成活动/父对象，至多两次必要Native合成生成产生机械能N1与二项N2；真正使用Windows OneCall/SUP/worker/Job、合成传输、PG record_outcome同COMMIT，费用0。旧已绑定活动不能reset来适配新image。只读继承旧有效生成边界；要宣称同一对象端到端就用本次真实新对象，不能拼接异activity证据冒完整链。

尽量一个API/主browser会话覆盖两正常链、来源回查、用户停止/回学习、刷新只GET、owner不续活、隐藏/卸载和迟到视图；剩余两个主browser名额留给有据普通修正。实际输入经可信number/range/reset控件到remote，独立核ACK、公式/读值、图形几何和PNG变化。

N1覆盖58.8、h=0、m=0和负值拒绝；N2覆盖n3/k2/p0.5=.375、四柱.125/.375/.375/.125及和为1、p0/p1、n0/n1/n20含21柱、k>n/非整数/p>1拒绝。保持资料/父身份回查。合法文本含既定两类XSS/脚本闭合样本，实际作为文本展示且不产生节点/脚本/请求/导航，不能先删除文字再测。

### C 补剩余矩阵并完整收尾

在触发相应故障前，把完整场景函数、实际注入位置、独立对象、预期、停止证明和所需生命周期写入matrix-plan.json。允许在A已证后补未完成故障，但不能把只有normal_http或NotImplemented的文件说成已制齐。按上述22基线/8修正的对象与根、时间同时计算；在本上限内自主合并真正同生命周期的断言，所有必须项都保留。

M01/M02由B的两个实际闭环覆盖。M03继承32类数据、非法RECEIVED无artifact与跨语言规则，新增源变化才复验；对公开/内部入口仍缺的反例定向补，不发32次模型。

M04/M05核有限描述与event拒绝导航/history/hash/data/blob/file/http/https、popup/newframe、网络/文件/download/chooser/系统/模型工具与markup等能力字段；实际正常frame基线的完整URL/fragment/loader/document/target/OOPIF保持。一次受信bootstrap外任何导航/新target/frame均FAIL。实际固定文本/Canvas与网络/文件/下载事件、无秘密哨兵按对应入口给证据，不用空网络日志或纯扫描签安全。

M06核真实remote域错误、格点、步数上限和拒绝后的全快照保留；忙死只用冻结受信故障夹具，不能执行模型任意循环作为合法描述。

M07核v1/rawHTML、重复init、未知field/nonce/hash/大小/乱序/重复异hash、坏PNG及错owner/activity/generation，给编解码/库和实际host路径的相称证据。相同seq同hash不重复执行，假console/postMessage不能注入协议或改变deadline/账。输入权反例尽量在正常session内完成，需要真正停止的pipe反例用独立对象。

M08继承最终生成、DML拒绝、hook同事务回滚+UNKNOWN等现成原件，只补未闭同key并发至多一发送、异输入409、丢HTTP回包GET同artifact不重发，以及实际受本轮代码影响的权限/COMMIT。不得重新赋app DML迁就夹具，不把profile/head正确推成所有原子性已证。

M09设准确“候选frame已缓存、公开资格查询尚未开始”的barrier，合成来源、父、记忆失效或cancel按真实合同/可适用父逐类COMMIT后释放；拒绝旧帧/正文/input。无记忆依赖的父明确不适用，不能虚构v2依赖。客户端切activity/父/owner/view/代次、隐藏/卸载，在真实HTTP/PNG解码/引用迟到后不能复活；已核后合法在途字节边界如实分级，不用序列化后的delay冒race。

M10合并正常与相关故障生命周期验证并发同start_key同session/CID、异键共享3次/180秒、最低30、失败占次、refresh只核对、config变化不重置、create成功回包丢失按精确身份找回不二次create、UNKNOWN保R/封新start和重启先核对救援。新合成前提和反例数据定向登记，旧budget/旧失败原件不修改。最多三额外生命周期用于必须的实际预算覆盖。

M11分别触发固定renderer忙死、实际browser忙死、Node宿主忙死、SUP死亡、Reaper死亡、两监督者终止、控制路径失联、pipe破坏、硬deadline，以及正常用户停止/回学习/隐藏失联的对应主张。每个不同故障有独立触发对象与结果；不能同一Chrome SIGSTOP冒renderer和Node两个不同故障，不用一个正常stop替签全部。可在测试控制进程内注入，或一个冻结专用variant image中承载有限受信故障模式，生产公开接口/config不含fault或任意代码入口。故障variant不签生产导航安全通过。

完整TreeProof需真实kernel/platform适用、非空private PID/init/出生及ready后工作子树、无逃逸条件、精确CID/image/nonce、外部kill/wait/events、attach和管道EOF、拥有CLI/HostJob/控制者结束和无restart互相绑定。单Stopped/Pid0、kill0、数据库状态不足，不宣cgroup目录或内存全部释放。控制不可达/双监督者终止时正确预期为unconfirmed、保R/禁新start；独立本卡验收控制器仅清精确对象，再按持久恢复合同核证，不能冒生产自行停止能力或停Docker daemon。

M12继承012前置拒绝、限定非空升级、材料/许可等充分原件；现成upgrade使用schema-only恢复限定010/011前提，不称该库原001—012逐条均重新通过。raw ACL新增NOLOGIN HTML owner九SELECT不是旧主体权限变化，报告保此细分，不把raw ACL字节相等误报PASS。只补当前修改真正影响的兼容、生产启动/退出、manifest/许可证/源码自包含与前端行为；不重跑未变G3—G10全套。

各场景的PNG、引擎事件、DB持久事实、请求次数/时间线和真实资源收据绑定最终source、bundle、image和activity身份。现成生成/事务等字节仍适用就引用，构建通过不替代最后UI行为。每个已运行版本的pre/diff/post/as-run保存，新源不能回写原失败为PASS。

## 停止与回传

同卡持续完成普通实现、必要测试与有依据修正，不因一个字段/夹具/页面中间错误返回请示。达到目标即停，不消费全部名额。修正前分析原件，固定新依据；同一原因两次有据修正仍失败、关键前提推翻、权限/数据/主要接口/依赖必须扩大、实际资源身份不明或总限到达时停受影响动作，完成可独立部分与精确清场后交回。不同已定界问题不混作同因两败，历史同因失败也不清零。

预检不要使用旧过期permit、旧硬编码root上限或任意新增work-intent门导致新许可自相矛盾。deadline与预算在真实入口处自动检测，不依赖执行者很晚才看时钟。清场不经已到期的业务闸；仅停止本卡精确PG/app/browser/preview/CLI/guardian，核端口及birth/Job归属，全部DB/卷/image/合成资料/失败保留。

结果以三轴分别报告实现、证据和执行控制，列M01—M12每项PASS/继承/FAIL/not_run/unknown与实际方法、版本、范围；不要用报告存在、语法、mock、当前Stopped或少数正常例签完整成果。原报告和失败原字节保留，新旧工程计数和时长可独立重建，重叠/unknown不补造。

保存并回读 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-111-result.md 后，回复只给一句结论和可点击完整绝对路径。人工仅转交本卡与带回路径，不需要用户贴密码或手动开服务。

## 必要人工与待同步信息

本卡当前待人工转交新A+工程窗口，未声明已接收/运行。原111窗口保持停写，无并行产品改动。本执行不得维护DocuS、公共规则、TASK/R/CHG/DEF共享编号或最终验收。

交回给出真实文件、签名、事务/权限、renderer组装与部署身份、预算/停止和前端行为的文档建议，以及仅已解决且验证的经验候选。DEF-027关闭由编排据修复与实际证据裁定；完整候选的集中独立审计归编排另卡。用户原始需求、既有110采用和全部旧有效成果保持原职责。
