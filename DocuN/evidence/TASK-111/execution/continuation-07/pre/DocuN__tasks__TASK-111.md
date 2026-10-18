# TASK-111 / R-105 续作07 — 三项终审缺陷修复、账段核销与定向验证

## 目标与交付

你沿原111续作06 A+工程窗口恢复同TASK-111/R-105，连续完成一个成果：修复TASK112集中终审的三项确定缺陷，核销历史PG持有段，给修正候选建立必要的离线与真实运行证据，精确清场并一次交回。不是又做一次G11设计、整仓复测或独立审计。

缺陷映射为DEF-031/F112-01/P1迟到ready、DEF-032/F112-03/P1真实stderr EOF、DEF-033/F112-02/P2 Node constraints/null与BOM原字节一致性。E112-01为历史执行账段，不当产品缺陷。有效正常、数学、资格、迟到、前端生命周期和不同故障原件保留，仅补这些修正及真实传导范围。

结果仍存 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-111-result.md，置顶续作07，当前146608字节全文作为原字节后缀保留，SHA fcee65ac816c59e364f26c23d0feaec023b28a97b170e78785d16af19d4be5f4。新证据只入 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/execution/continuation-07/。完成修正/相关验证/原件索引/账与精确收尾后交候选，原112独立窗口随后只复核缺陷及实际影响。本窗口不自签G11、SEC003/B01、STEP、M-1、项目或发布。

## 项目、规则、授权与窗口

根 D:/shspic/project_NO3_RetroLume-agent；入口 D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。模式task_model、V4.0/公共AGENTS CHG-0003，公共根 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4。读DocuS/AGENTS.MD及WORK适用2/6/8章，七锁定身份在DocuN/evidence/v4-migration-20260930/rules-snapshot.json，已读未变正文复用。需求v1.2、架构v1.20、执行动态v2.42、阶段07。

工程许可 TASK-111-G11-C07-20261012；基础产品HostPolicy仍TASK-111-G11-P110-20261010。用户已采用110有限方案并持续授权完整实施、验证、范围内修复和独立门；本卡明确恢复原工程窗并给予以下前向工程增量，不追认历史超限。接收原续作06 A+工程窗口，由用户最强且胜任者执行，真实客户端/型号如实记录。TASK/R不换；不派子Agent，不与112审计或其它窗口并行写产品/运行资源。

112审计已真实返回，交付36048字节/SHA ea51e0f49f556fd6f07aea11741d26099a534550850c0c68dfa49a9ab4c3b522；105当前源、七规则及225审计身份核对无漂移。40已登记Docker对象当前Stopped/Pid0/restart0，预算active_batch null。主控核证/裁定/新预算在 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/orchestration-receipt-08/。旧C06卡原字节保存同目录prior-TASK-111.md，仅历史；不按C06或更早到期许可开跑。

## 最小上下文与已有证据

依次补读本卡、TASK-112-result.md的三缺陷/账段/最少后续行动、DocuN/evidence/TASK-112/audit-20261011/static-counterexamples.json和execution-budget-independent.json、主控PG-hold-disposition/continuation-budget。再读production_supervisor.py的_read/_stderr/_run_owned及停止确认/恢复直接路径，renderer-protocol/renderer-host/runtime对应入口、Python description/pipe、必要build/installation身份以及task111控制/资源/真实夹具。

当前基线SUP SHA f757477cf2ac9cc321c036383f9b06a7cb18e88a174ae5197d2753fa4c99f9c9，host_job51163b93cad0efd0a14536b070ae2102a12d470043cc03e9146d8e98bfed7841，preview repository bf5e04cd8aaed6ded8c120b601ec7d8718df6e4484747203a3791eef8188de06，012 a400170b010ad5f8adca2003a6829519b435b14160ade01fd8283e9fcd3c87b7；最终Panel7c7204690f3d2f72129c9ab377101fe849ad98eef9dbf0b6432bfca5e050b513不需要改。其余以C06 final/source-identity的105项必要清单核身份，未变正文/原件按已有读取复用。

独审已经限定接受正常两Native/数学/图形、32边界的充分部分、资格/前端迟到/隐藏/卸载/修正刷新及不同故障等原件；本次不重放这些整链。新发现是此前未覆盖的分支，旧正常结果不证明其已安全。公开输入措辞更正为21条记录=17个远端成功ACK+4个422拒绝；不能把拒绝叫ACK，不改历史原件。

## 三缺陷的修复合同

### DEF-031 ready完整接收与成功分支时窗

完整ready在t0+8.005秒到达时，旧Event.wait可以从t0+7.998的20ms等待成功，外层绕过ready_deadline。修复必须在完整packet接收时保存真实单调时刻，核身份与原 min(t0+8秒,D-10) 边界；wait成功后再核接受时刻/当前时窗/stop标志，不能直接提交ready。边界定义、原t0、产品D、ready8和关输入门不后移，不按墙钟判断，不因等待成功授迟到资格。

晚到ready中的真实内核信息仍可用于该对象停止取证，不能为了拒绝资格丢失唯一物理证据；区分收到事实与接受ready。已经start的对象不能标“从未启动”。逾期进入原失败/停止路径，只有真实完整确认才能结算，缺证保R/封新start，次数不退。

定向离线调用实际产品门和成功wait分支，覆盖及时、边界/迟到、Event成功后stop已置、调度延迟当前时窗已闭；明确各采样含义。真实反例用准确对象/实际合法ready包有界延迟到原8秒之后，保存原t0/packet完整读取/接受或拒绝/DB状态/真实停止。不要靠几十次碰运气抢20ms，也不改本机/DB时钟。离线确定调度样本与真实单调观测分级，不伪称替身时钟是实机发生。

### DEF-032 stdout与stderr真实EOF及退款门

旧stderr在累计超8192后break，线程结束不是EOF；旧停止谓词只核stdout EOF与两线程不活，会冒真实双EOF并可能退款。分别维护实际stdout/stderr EOF、读取异常与有界捕获事实；stderr超限置stop，存储仍最多原8192或明确有界上限，随后在原D/诊断界限内排空同一流直至实际空读。不能无限缓存或无界等待，不用break/线程退出/文件写成/进程Pid0替代EOF。

最终停止确认与preview退款门必须同时要求真实双EOF及原Linux/kernel/nonce/事件/准确实例/两Job证明。读异常、尚未EOF或截止到仍不确定保持未确认和reserve，不用新字段默认true；物理精确救援可以继续，但它不能伪造被跳过的流观测。新增仅私有状态/证据，不扩大公开退款/API或持久模型。

离线调用实际读取/最终确认门覆盖正常双EOF、8192/8193及分块累计溢出、读取异常与“线程已退但stderr EOF=false”反例，确认无结算/退款调用。真实至少一次READY对象的受控有限stderr大于8192进入实际attach stderr流，看到超限停止、有限保存、真实排空EOF和完整停止/持久结算；不是把伪流当实机管道。读异常/未EOF若还需真实持久反例，在本批预排准确对象及PassiveWitness同根恢复，不能现场造新未知再换根绕过。原历史正常/零stderr原件和已结收据按真实旧证据限域，不回写新字段冒充当时已采。

### DEF-033 Node有效入口与原字节规范性

Python constraints存在且null会拒绝；Node nullish默认则接受，且TextDecoder默认移除UTF-8起始BOM，文本canonical比较无法检查原始字节。优先在实际renderer-protocol的validateInit/原始JSON入口集中加强：缺省可按原空数组规则，存在必须为数组，null/其它非数组拒绝；原始UTF-8字节与规范序列化UTF-8一致或明确拒起始BOM。不能把合法字符串内部U+FEFF删除，也不能放宽Python前置防线。

完整Node入口是纯JSON解码、init结构/类型/身份/hash与runtime校验的真实调用链，不只测试旁路新helper。优先保持四runtime、编译包与SQL期望renderer身份不变；若必须改runtime/计算语义或SQL安装模型，先给实际冲突并停相关修改，不自行扩大本卡。两处合同仍需由实际入口证明域一致，不能只改测试期望或以Python已拒绝忽略Node第二防线。

离线用实际Python/Node产品入口对缺省/空数组/null/字符串/对象/数字/bool、无BOM/起始BOM header和body做同域对照，含正确长度/hash的反例。新加载Node宿主真实管道拒绝相应非法init/封包。BOM header/body可在合法READY后注入固定非法input包，保既有kernel/Job证据；显式null init只改测试wire，不往DB造非法artifact，已有bootstrap物理信息按实际用。注入仅冻结harness，不进公开fault/config或模型可执行数据。

## E112-01历史持有段一次核销

主控已只读核root6结束869276343000000ns至精确PG stop确认871556046000000ns，旧cleanup前同CID Running=true/Pid945，已知账无该段。原输出与审计计算吻合；完整保守持有段2279.703秒，旧账14546.863变保守16826.566，相对旧16200超626.566。物理停机瞬时未采，不把此称每一瞬连续观测的精确时间，也不填0。

开工先保全预算原字节；追加唯一E112-01 adjustment及原件/hash/计算/确定性说明，将运行账基线按保守16826.566对齐。原14546.863和626.566历史超限始终可查，不返counts/time/费用，不靠新cap追认旧合规。只读找到当时有效停止/重启原件才能提出有依据缩小；无新原件不能重算省掉。Adjustment不得重复加，原账事后复检要能明确判断已生效。

E112-01是执行投入核销，不是重新运行旧PG或重现root6的任务；不测历史丢失段，不改旧日志。新真实区间包括PG持有/修正等待/跨根/停止确认外围，明确区间并集与重分类，禁止再让过期业务门挡清场。

## 范围与固定资源

允许修改上述真实涉及的backend/app/preview/production_supervisor.py与必要私有pipe/process/停止证据校验、deploy/preview/renderer-protocol.cjs及必要构建身份文件；backend/tests/fixtures/task111与相关定向测试/Node测试。新build-contexts只新增v2-08及必要一次有据修正v2-09，不覆盖旧v2-01—07原件。使用项目已有本地OCI/Node/PW/Chromium资源和现行构建链，不联网下载/install/pull/clone、不增加依赖/许可证或权限。只为修改过的Node ingress重建新image/load。

禁止改001—012/SQL/ACL/角色域/持久模型、原四账/worker主权、固定四runtime/数学语言、前端产品/既有bundle、锁/用户资料/配置/DocuS/公共库/旧证据。必要私有StopProof补真实双EOF不能变成公开新接口。新image身份是真实新事实，不能沿v2-07旧hash签新代码。依赖不自包含、资源必须扩大或更改主要合同，报告最小冲突，完成不受阻部分。

PG仍精确CID1791a2d086228c618bf043b0565e215828ff0ccfe5a858486488f1329a16ef51、retrolume-task-111-g11-v2-pg1/同名-data卷，image sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f，127.0.0.1:55451、1CPU/512MiB/pids128。只原main/upgrade/fault与原三合成角色，口令内存/stdin/限定子进程Env，必要精确重置可做，不输出Env/秘密/argv，不建库/卷/角色、drop/recreate/DELETE或清行。

仍唯一registry D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/execution/continuation-04/synthetic/control/。旧25/preview542b0750-6e02-418a-b216-5dfbd3b93047/CID742543c26e0507a62d3797f86f9a88bea3c433bc75d4d681b87f5a6e2dd23944UNKNOWN/R60/count1及旧root blocked保持，不因新EOF标志补旧证明。新未知本对象严格救援/同根恢复后才继续，不再换registry。

preview原UID10001/sandbox/network none/read-only/CapDrop ALL/NNP/seccomp/private PID/IPC/init/no restart、1CPU/1GiB/swap同值/pids256/SHM64MiB/安全tmpfs128+32MiB全不变。无host bind/socket/preview端口/特权。一个PG/卷与一个preview同时运行。新合成活动/父/producer真实资格与仓储、无Native模型调用；新image不重写旧budget.config，不把已有旧image预算免费迁移。

## 前向成套工程预算

首个C07接收工具同时采真实UTC/monotonic，综合14400秒、末600清场。旧授权129600前向加14400为144000，旧投入/失败和采样unknown保留。只读预检不计真实根；启动build/load/PG/preview按真实动作计数，不把离线纯语法或元数据充业务通过。

- 真实根18→20，仅root19/20，各最多1800秒；本C07新增real最多2400，累计上限16200→20400，按保守新基线16826.566投影19226.566。历史626.566仍超旧许可；20400只许可本次前向工作，不是历史免责。build/load实际资源期、PG持有/修正等待/跨根/停机外围都计real。
- image build已7，上限9，新最多2：一次确定修复版本及一次有据修正余量。本地缓存构建/载入与真实load/程序hash/基image/Node/PW/Chromium/隔离绑定一次保存；不拉新包，不先重复旧v2-07验证。
- preview已create45/start41，累计上限55/51，各新最多10；准确名称retrolume-task-111-g11-preview-56至65，各一次。六到七个基线：及时正常、迟到ready、真实stderr超限、必要未EOF反例、null init及BOM header/body；最多其余三到四个有据修正。可合法组合及时正常与后续协议反例，少用即止，不要求用满。原56/57未用名继承，新58—65前向追加，旧失败不返。
- PG start14→16，最多2；API12/12、主应用browser11/11不增，本卡计划新0，使用真实仓储/生产控制链与匿名管道验证。不重启主工作区。preview内部Chromium计该preview生命周期，不冒主browser/模型OneCall额度。
- model/Windows OneCall各9/10保持且计划新0；frontend4/5保持、计划build0；HTTP1611/5000、PNG182/3000/public input68/300/internal26/500保持。一PG/卷/preview并发不增；清场累计1800/已77.2837405，末600预留，必须不经到期业务闸执行。

新C07许可、timing、保守账调整、caps、names、root和唯一registry一次写入所有实际入口与传递消费者，不能还默认选C06；保存原账和旧deadline历史，校验adjustment已且只一次生效。离线/Reaper分组次数记录，整组时长只用当前根/总余时，不另设600/650/900秒第二套截断。产品ready8/原D/soft2/诊断15与合理单调用边界始终保留。

## 验证安排与完成判据

先一次制齐产品修复、对应反例/对照、真实wire注入和协调/预算。定向离线实际调用产品，不能SQL字符串断言/mock当真实事务。其后一次新本地image/load与PG/生产控制合并批，建立上述缺陷真实影响证据；有普通失败且归属/物理状态已知，保存失败/停止相应消费者后，在本卡修正余量只复验失败方法，不默认掐掉全部余项。

至少保存一个新image的真实及时ready/单个既有机械能输入及实际PNG/ACK、完整stop/两EOF/DB结算对照。旧四runtime若未变则原数学/图形/两Native/前端、SQL/资格/六停止有效部分直接继承；新宿主加载只补实际Node ingress及SUPer修正，不能以旧load替签新image，也不要求再跑整套正常UI/32例/六故障。

迟到ready反例要证明未提交ready/无输入资格且停止真实；stderr反例要证明超限不能把线程已退当EOF/不能提前退款，正常排空对照才可确认；Node两端反例和新实际宿主均需准确版本/原字节/拒绝位置，不能只给测试方法数量。有限异常注入仅在本对象harness中、实际管道读写/固定有限数据，原kernel/nonce/birth/Job原件齐备，公开产品无fault入口。

自主停止/独立观测/精确外部救援分层，取证不持额外Job或写端、不与存活reader争流。真正需要UNKNOWN反例时先配齐实际读副本、accurate birth与原D、本对象kernel及同根恢复路线，确保不重演旧25缺证；缺证明仍R保持，不能为跑余项假确认或换目录。所有真实结算与退款都按原StopProof/资格门，不以新时窗扩大权。

通过修复/反例/对照及版本绑定即收口，不耗尽剩余额度。两次同因有据修正仍失败、根因不稳、公共权限/持久模型/四runtime语义需改、归属不明、新未知无法完整恢复或真实上限到达，停相关依赖并完成不受阻部分及清场。不能暗开root21/image10/PG17，不只回“准备下次重跑”，交具体事实和最小未完差异。

## 回传与独立复核

保存TASK/R/许可/真实身份、三个DEF及E112-01逐项事实、pre/diff/post/as-run、实际命令/失败/时间/加载与kernel/两EOF/Job/DB原件、完整count/time调整与当前余额、精确停止索引/端口/active_batch、复用版本/局限及建议文档。保初始负例、原报告/审计/日志和历史626.566超限；绝不改审计原文或原105冻结快照。所有本批对象/登记实例精确停止，库/卷/image/行/资料/旧证据保留，不停daemon/用户进程，不Git/删除/发布。

主控维护DocuS、DEF/CHG和最终裁定；本窗口只保存111结果/新工程证据及实际预算。完成后原TASK112/R106独立审计窗口只增量核三缺陷、账核销及实际变化传播，不再完整重审。回传只给一句真实结论和上述完整结果绝对路径。
