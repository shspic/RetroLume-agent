# TASK-112 / R-106 G11有限候选集中独立终审结果

本轮完成TASK-112规定的完整有限切片审查，复用现有原件，业务运行次数为0。当前TASK-111冻结候选不能由编排关闭。原因是两项P1停止控制缺陷、一个P2双校验域差异，以及未完整核销的历史PG持有账段。没有发现需要改回109自由脚本方案或重跑全部G11的依据。

代码轴不通过，定位为F112-01、F112-03，另有F112-02。证据轴对下述已运行方法限定充分，但无法签最终候选全部Must闭合，三个新定位分支未有对应修正证据。执行控制轴存在确定历史偏差与计时缺口；C06新增次数和自身用时符合其前向许可，不能据现有14546.863秒账面数签全部真实累计合规。这三个判断互不替代，不抹去已成立的运行事实。

报告只裁定批准的G11有限切片是否具备交编排关闭条件。项目、全部STEP、M-1、真实provider、用户数据库、生产票据和发布均未获本报告签署。TASK-112审计交付已完成，产品缺陷由原TASK-111工程窗口负责，编排负责正式验收和状态账。

## 接收、独立性与边界

项目根为D:/shspic/project_NO3_RetroLume-agent，入口为[AGENTS.md](D:/shspic/project_NO3_RetroLume-agent/AGENTS.md)。模式task_model，V4.0，公共AGENTS为CHG-0003。需求v1.2已读FR009、SEC003、NFR002/003及有限方案生效头；架构v1.19和执行v2.41作为本卡指定版本引用，未读取主控111验收段。已读同版公共AGENTS及WORK适用2、6、8章，七份锁定源均独立哈希相符，没有采用后来规则正文。

实际客户端为Codex desktop，系统可见身份为基于GPT-6的Agent，精确部署后缀及推理档位未暴露。A+是用户指定的审计资源职责，不冒充型号或声称已核客户端的最强模型配置。本会话没有110/111实现对话、设计推理或工程参与历史；未沿用111工程窗口，没有子Agent、并行写产品或资源运行。

[窗口安排](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/orchestration-20261011/window-assignment.json)原件仍为待人工转交，未由审计者改写。实际接收来自本次用户转卡。本报告及[receipt.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/audit-20261011/receipt.json)记录本会话已实际开展审查，不将旧安排文件的布尔值当成真实派发工具证明。

首个工具时钟锚为2026-10-11T15:06:14.1464331Z，即北京时间23:06:14；Windows QPC为10026384166335，频率10000000。其前已经读取入口及卡面，首读未同步采样，准备段精确耗时未知，没有倒造时刻或填0。元数据脚本登记为15:07:41Z。审计上限10800秒按此已知工具锚持续约束，终点及已观测用时见交付回执；不能把首读准备段说成已精确计入。没有以剩余额度启动业务验证。

独立定位先存[checkpoint-01](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/audit-20261011/independent-checkpoint-01.md)，再存[checkpoint-02](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/audit-20261011/independent-checkpoint-02.md)。未读取TASK-111-result各轮自评、111聊天/推理、orchestration-receipt-07/received或methods-byte-check结论。规范性预算宽检索意外显示111卡面历史主控核证摘要，接触发生在第一独立定位之后，已在[接触披露](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/audit-20261011/exposure-and-dismissed-hypotheses.md)如实登记；这些摘要没有用作本审计通过依据。运行方法索引中的PASS、执行收据状态及failures-and-reuse的无新阻断措辞只作导航，不能覆盖独立发现。

写入范围只有本结果与DocuN/evidence/TASK-112/audit-20261011。未修改产品、夹具、迁移、锁文件、DocuS、111证据、原始需求或公共库；未运行产品模块、测试、compile、build、SQL、PG、Docker、Job、浏览器、模型、安装、下载、Git写操作或旧runner。查看的是已有PNG文件。只查阅两份官方机制页面，未作方案研究。

## 快照及最小读取范围

开工对冻结清单的225项独立哈希全部一致，其中105项源码/配置、5项主要输入、7项锁定规则、27项证据索引及81份runtime副本。105项是身份导航，没有宣称105份全部全文阅读。结束再次核对同一清单，结果见[frozen-identity-start.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/audit-20261011/frozen-identity-start.json)与[frozen-identity-end.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/audit-20261011/frozen-identity-end.json)。

关键当前SHA256如下。

- production_supervisor.py为f757477cf2ac9cc321c036383f9b06a7cb18e88a174ae5197d2753fa4c99f9c9。
- host_job.py为51163b93cad0efd0a14536b070ae2102a12d470043cc03e9146d8e98bfed7841。
- preview/repository.py为bf5e04cd8aaed6ded8c120b601ec7d8718df6e4484747203a3791eef8188de06。
- activities/repository.py为29c3415576382623e300d67d9d0c76b945bcb410c7e981976a44022f6152608d。
- 012为a400170b010ad5f8adca2003a6829519b435b14160ade01fd8283e9fcd3c87b7。
- Panel为7c7204690f3d2f72129c9ab377101fe849ad98eef9dbf0b6432bfca5e050b513。
- 最终前端assets/index-DeYBJidT.js为e76cacf45e2a435446277a1977a01a87bd5da4b09665e95a67bc834be9c8a488，已核实际dist字节和as-run build记录。

生产image为sha256:c23c7489d56fa2cc955dc15e86e0b710b476589997d57ee33c9eb9f3949e826f；load为bea3f1ebc033635fdac71e1134ed66632947d994b701c9a7b76d942ff036ad00；四runtime集合为6cc300164a6cb364d9bd0bae4897f06d3f6a65cf5d4272477d2bccde67312597。已独立核v2-07 load中651项本地资源全部相符，见[加载清单核对](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/audit-20261011/load-manifest-verification.json)。image与实际Node/PW/Chrome、argv、UID/sandbox的绑定依原始ready、registry和停止原件核，未在本审计启动image。

v2-06故障image为sha256:8d3811cdf4b9d6edd00a5dd438e382d1700335fb0109084a59e69813fbc97016，load为3762e87b9fafca30c90de616018006eddeb5defcee6dee9c9f8a92618027342f。仅继承实际故障variant范围，未将其签为v2-07正常导航、帧率或任意脚本安全证据。

必要正文包括110 C2—C7/D1/D2及work-decision生效首段，preview完整直接控制/描述/编译/管道/API/事务实现，012，原record_outcome及新hook接线、Gateway/OneCall序列化直接影响，Panel/Canvas/API及两父视图挂载；再按M01—M12读取对应原件、as-run夹具和必要控制入口。初始pre-final差异及C04—C06差异用于识别实际影响。逐文件路径、读取目的及hash见[reads.jsonl](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/audit-20261011/reads.jsonl)，实际解析操作见[commands.jsonl](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/audit-20261011/commands.jsonl)。纯哈希或索引解析不冒充全文审查。

81份C06 runtime-originals副本与其指向的81份原件另逐字节SHA核对，无差异，见[副本核对](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/audit-20261011/runtime-copy-verification.json)。最终方法索引19个指向文件及6会话索引12个指向文件也独立核hash。未从头通读上万份日志，仅对3507条有限事件账做确定字段解析。

## 确定缺陷

本地发现编号仅作本审计定位，不占共享DEF编号。严重度按公共规则，所有修复均归原TASK-111。

### F112-01 P1 迟到ready可跳过8秒检查

定位为[production_supervisor.py](D:/shspic/project_NO3_RetroLume-agent/backend/app/preview/production_supervisor.py:390)，另见283—294行。接收ready仅验证身份并置Event；外层只在Event.wait返回false时检查ready_deadline。成功分支直接执行ready事务，没有复核收到完整ready的单调时刻。

具体路径为在t0+7.998秒进入20ms等待，完整ready在t0+8.005秒到达，wait成功，进入ready状态。身份、description/load/policy都正确也不能修复时窗错误。更长调度停顿同样没有成功分支的拒绝。合同C6及TASK112明确ready最多8秒且在D-10前，此路径确定违背原Must。它不延原D，但可能把逾期初始化作为可用预览接受。

证据为冻结源码与[静态反例数据](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/audit-20261011/static-counterexamples.json)，等级B，可信度高。没有运行该调度反例，出现频率未知。已有较快ready原件仍有效，不能证明迟到分支关闭。

最小修正为在完整ready接收时记录并核原单调边界，在wait成功后再次核停止标志和ready边界，越界进入既有停止/未确认路径；保t0预扣前、原D及不返次数。最少补证为该成功wait迟到分支与及时ready对照，确认超窗不进入ready、停止按真实证明结算。无需再跑两次Native生成、全部数学或全部浏览器。

### F112-03 P1 stderr提前退出可冒充真实EOF

定位为[production_supervisor.py](D:/shspic/project_NO3_RetroLume-agent/backend/app/preview/production_supervisor.py:322)及421—423行。stderr累计超过8192字节后置stop并break，未读到实际EOF。最终只用stdout的pipe_eof、attach进程退出及两reader线程不再存活构造attach_ended；stderr线程因break或异常退出也满足该谓词。

因此，在stderr尚未观察EOF、stdout随后EOF、attach和两个reader已结束的情况下，stop_owned仍能得到attach_ended=true并写attach_eof_confirmed=true。Linux/init和Job结束可能实际成立，但这不证明stderr已经读到EOF，不能据线程结束补签合同要求的真实管道事实。该收据又可使confirmed成立并退未用preview秒，未达到本合同的完整证明门。

证据为冻结源码与静态反例，等级B，可信度高，未运行溢出分支。没有宣称历史零stderr正常会话或已有故障原件已经命中此缺陷，也未声称发生资源逃逸、内存泄露或数据破坏。

最小修正为分开登记stdout/stderr真实EOF，保有界存储，超限后置stop并按原截止/诊断界限排空到实际EOF，未取得则保持未确认；不得把读线程break当EOF。最少补证包括大于8192的stderr、读取异常/未EOF，以及正常EOF对照，核停止收据和退款门。现有准确CID/kernel/Job原件可复用，不能因此抹去全部停止证据。

### F112-02 P2 Node接收域与原字节规范化不一致

定位为[description.py](D:/shspic/project_NO3_RetroLume-agent/backend/app/preview/description.py:136)与[runtime.cjs](D:/shspic/project_NO3_RetroLume-agent/deploy/preview/runtime.cjs:57)，并涉及runtime 108行及renderer-protocol 23行。Python对存在且为null的constraints调用bounded_list而拒绝；Node使用nullish默认，把显式null变成空数组接受。规范序列化保留null，正确hash不能排除此差异。

反例在原合法机械能描述中仅把constraints改为null，其余正常域、默认值及引用不变。正式Python生成入口会拒绝，未发现该差异能让模型执行代码、导航或网络；P2依据是第二防线合同一致性缺陷且前置防线仍成立，不把它夸大成已证逃逸。M03/M07的两处校验域一致性不能据现有32例签完全符合。

同一Node入口另有BOM原字节缺口，定位[renderer-protocol.cjs](D:/shspic/project_NO3_RetroLume-agent/deploy/preview/renderer-protocol.cjs:8)。TextDecoder只设fatal，默认会移除UTF-8起始BOM，然后以canonical(value)对解码后text比较。原字节带EF BB BF的正常规范JSON可经过此比较；Python严格UTF-8 decode保留U+FEFF，JSON入口拒绝它。无BOM合同因此不成立。此判断来自冻结源码及[WHATWG Encoding官方BOM算法](https://encoding.spec.whatwg.org/#textdecodercommon)，为机制与源码结合的静态结论，未运行Node或浏览器。header/body长度与hash都正确也不能补原字节规范性。

最小修正可在实际Node描述入口明确区分缺省键与显式null，要求存在时为数组，再调用现有验证；boundedJSON应核原始UTF-8字节与规范序列化字节相同，或显式拒绝起始BOM，不能只比已移除BOM的text。两处可在renderer-protocol集中修正并保持四runtime/编译包身份，避免不必要改变数学程序；若实际改runtime，则如实绑定新的renderer、编译包及SQL期望身份。无论哪种方案，改变镜像内容都需新的image/load证明，不能沿旧hash签新代码。

最少补证为缺省、空数组、null和非数组的两端一致结果，加无BOM/起始BOM的header和body对照及真实Node ingress拒绝。无需32次模型、重新生成旧成果、清旧预算或全部浏览器。当前image已7/7，该最小改动也不能用本审计或已冻结C06恢复构建许可。

## M01—M12完整判断

每项以110 D2原文为准。符合仅指批准的有限G11范围；证据为现有A运行原件与本次B静态核对。没有以矩阵计划代实际方法。

### M01 正常机械能

判定符合。C04真实Native/OneCall生成、同键并发、公开COMMIT回执及真实主UI驱动远端预览形成链。m=2/h=3得到58.800000000000004，零因子得到0；range键盘、number及reset都有实际请求，负值422后原PNG不变。来源真实回查、停止并回父均保原件。

来源为[Native-and-normal-UI](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/execution/continuation-04/final/Native-and-normal-UI.json)及其root14/step08/ui-attempt01/ui-effects.json。独立核算见[normal-ui-oracle](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/audit-20261011/normal-ui-oracle.json)。源码为有限AST实际mul与Canvas，不是写死58.8。机械能和二项合计21个公开输入响应中只有17个成功远端ACK，另4个为422；索引所称21个ACK需按此纠正。

### M02 正常二项分布

判定符合。第二真实Native会话覆盖0.375及四柱0.125/0.375/0.375/0.125、p端点、n=1/k=1/p=0.25、n=0和n=20/21柱。全部成功读值和完整点列经独立组合数oracle一致，柱和误差在1e-9内。k越界、非整数n及p>1通过真实服务拒绝。

p>1采用测试路由把真实请求的event.value改为1.05并重算hash，不能描述成滑块自然提交1.05；原件及as-run c04_ui_workflow 134行支持该限定方法。标签和concept保留两种脚本闭合/XSS文字，实际远端DOM title/concept仍是原文，固定script只有1个，危险节点0，网络/下载/dialog/filechooser记录0。不是先删除恶意文字后通过。两会话43张PNG保存字节均与记录hash一致，实际查看已有图像，未重新渲染。

### M03 生成与解析边界

判定确定违背双校验一致性子项，见F112-02；其余已运行反例限定符合。offline01的32个Python/Node描述反例原件、调用stdout及夹具实际逐例断言已核，当前description/compiler/四runtime字节与该批相同。覆盖未知HTML/script/CSS/frame、hash/history/data/blob、文件/HTTP/parent、原型键、bool/UTF-8/NUL、节点/引用/格点/负零/过量输入/arity等。重复JSON key另有实际Python拒绝，Node canonical字节回比另由生产protocol原件支持。

原始非法响应通过真实受控替身/OneCall/PG，terminal invalid_output且无artifact；原UNKNOWN也无artifact。没有把32例说成32次模型。现有32例未含constraints:null和原始封包起始BOM，不能用其PASS排除新定位。只补这些类型/原字节边界，不默认重跑所有反例或模型。

### M04 导航、整frame与target

判定符合批准的数据入口边界。已核生产描述、真实公开输入类型拒绝及Node真实header/init函数的hash/history/data/blob/file/http/https/parent/top/popup/blank/named/form/newframe能力请求。两正常会话完整CDP frame、document URL、loaderId、backendNodeId和page/iframe target基线均为准确两frame/两目标；机械能5次、二项12次已保存输入观察与其基线相同，无新增请求或目标。

依据见[normal-runtime-originals-analysis](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/audit-20261011/normal-runtime-originals-analysis.json)、C03 prepared-offline/host-boundary-result及root10/step09/public-capability-rejections。已核固定程序无导航/任意函数出口和受信文本sink。未把CSP/route/事件观察宣称为任意已执行脚本的全路径事前否决，没有hash豁免，109反证不改、不复演。

### M05 网络、文件、下载与XSS

判定符合有限入口及既定隔离范围。file、回环/外部HTTP/WS、fetch/XHR、download/chooser/系统/模型工具字段被封闭schema或公开event类型拒绝；HTML/SVG/CSS/event模型字段不可入可执行位置，合法恶意标签原样仅作文本。runtime无文件、网络、eval、Function、任意DOM selector或URL出口。

实际ready证明Node v24.18.1、Playwright 1.62.1、Chrome/151.0.7922.34、UID/GID10001和真实Namespace/Seccomp-BPF sandbox，argv无no-sandbox；生产inspect与create数组确认network none、只读、CapDrop ALL、NNP、原seccomp、private PID/IPC/init/no restart、1CPU/1GiB等swap/pids256/SHM64MiB及128+32MiB安全tmpfs。没有host bind/socket/preview端口或特权。固定宿主读取镜像资源和proc用于身份取证，不等于模型页面获文件能力；未读真实秘密或签浏览器漏洞免疫。

### M06 数学、域、步数与整快照

判定符合。规范十进制和格点以整数缩放/BigInt对账，禁止bool冒数字、指数、负零、超范围；n/k整数和k le n、p域、pow_int 0—10、sqrt负域和非有限中间值关闭。256 AST节点、深度16、图形128点与50000步独立限界，有限递归和binomial迭代也计步。

C03 root10/step09/real-domain-limit原件给初始12802步/128点，真实负域及calculation_limit ACK均accepted=false，保留原输入、读数、完整PNG；C03 prepared-offline还核了独立有限上界。没有执行模型永久循环作合法描述。renderer/browser/Node忙死另属M11故障variant，不能混签计算安全。

### M07 管道及输入权

判定确定违背两端接受域及BOM原字节子项F112-02，其余已覆盖方法限定符合。真实生产header/init拒绝v1/raw HTML、未知键、nonce/hash/renderer/viewport漂移和bool/负序号/超长。Python保规范UTF-8/JSON、长度、正文SHA和类型；Node有重序列化但起始BOM被解码器移除的缺口尚未关闭。PNG有CRC、codec、尺寸、压缩终结及扫描行检查，现成损坏PNG原件分别拒绝signature/truncated/CRC。

原件覆盖无owner/错误owner、代次、同seq同hash幂等与异hash冲突，host重复init拒绝及精确停止；控制者只一个未ACK输入，未知ACK不自动回放。公开stop用应用身份，不需owner。C04 fake_console/postMessage seq999没有成为协议、原D不变，后续真正ACK有效。F112-03影响停止EOF证明门，在M10/M11分别标出，不能靠本项常规封包通过略过它。

### M08 COMMIT、费用与原四账

判定符合已核范围。actual record_outcome同一connection写原received/正文，再写HTML artifact和terminal；新hook异常整笔回滚。未因旧函数文字不变而跳过实际SQL，已比较当前012的15个函数正文与真实catalog原件全部一致；schema摘要727f40a510e1ed9f6443a0491e5a23184d46ca94191a05078f06ae2749ef4eb8与当前配置相同，compiler固定HTML16575字节及renderer hash与SQL常量相符。

依据为[compiler-and-SQL-metadata](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/audit-20261011/compiler-and-SQL-metadata.json)，C02 root08/attempt17的hook-before/hook-after完全相同，operation仍dispatched、command仍launch_claimed、正文/artifact均0；其后hook-unknown原件为terminal unknown、reserved_cost仍100、仍无正文/artifact。该方法无transport/OneCall，不冒真实模型质量验证。

初始real06/attempt01四次真实OneCall/受控替身包含两个正常、一个invalid_output和一个delivery_unknown；后来的C04两个正常Native形成当前UI完整链。已核同键并发不二次发送、异输入409、丢HTTP只GET原artifact及非法/UNKNOWN终态。父或来源资格失效后的新写拒绝及UNKNOWN诊断沿原记录主权，不把Gateway record_denied视为可用正文或给原费用退款。preview账只更新两张preview表，不改原活动四账，C03预算方法还实际比较活动整行前后相同。

### M09 资格、迟到及客户端代次

判定符合。来源/记忆/activity/operation沿原锁序，父/来源/记忆闭包及取消资格在真实事务与公开读取查询内核。C03 source/parent、C04 memory/cancel均在候选PNG已缓存、公开_owner_row查询未开始处暂停，失效COMMIT后释放，真实frame/正文/input都拒绝。原件的candidate hash、entered及COMMIT单调时刻相符，没有用检查前后顺序含糊的替身代准确竞态。

012新增PDF权限仅三表六列SELECT，无正文、DML、GRANT OPTION或membership扩张；实际attacl为r，html_app无这六列直接权限，extracted_text/warnings及三表DML都42501。Memory闭包/取消竞态及PDF实际资格方法见C04原件。保留旧table ACL主体原权限，不把其既有合法权误判为新扩权。

C05 tail-attempt2真实fetch的Response读取完成后暂停，真实PNG先解码再延迟ImageBitmap，切实际activity/父/view/owner后释放旧input/stop/frame/citation/bitmap。已有记录显示旧ImageBitmap调用原生close后宽高0、无旧draw，新身份未被旧值恢复；后面的hidden失败不否定已完成组合。C06真实hidden及READY组件卸载原件同样释放实际旧值、清canvas/引用/读数、撤owner且禁输入。当前Panel与Canvas的代次/owner/preview/artifact核和bitmap.close路径已读，不把本地假图当远端输出。

### M10 预算、刷新与恢复

判定确定违背ready时窗F112-01及完整EOF/退款门F112-03，其余已运行预算/刷新/恢复方法限定符合。t0固定在预扣前，原D由reserve30—60秒构成，次数3/总180持久，失败不退次数；异key不重置，同key并发只一session/CID。C03实际create回包丢失记录原create成功且仅一次，再按精确name/nonce/labels/image找回；预算最终starts3/reserved0/settled24，第四次和reserve29拒绝，config变化不重写旧预算。

刷新旧页侧PASS不成立为GET-only整窗。服务端事件3167/3169确有stop POST尝试，虽ClientDisconnect在接受body前发生，也不能说根本未发送。新bundle窗口从事件3456、13:24:27.740190Z的实际reload GET到13:24:32.353Z判定终点，37条原始事件全部GET，逐行与完整索引相同，客户端无owner，无新start，原D/starts不变，停因control_lost。清场POST在13:24:32.387960Z，位于判定窗口外。见[refresh-independent-window](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/audit-20261011/refresh-independent-window.json)。这是实际修正关闭旧刷新缺陷，旧FAIL不删除。

同根恢复核准确原实例结束、私有Job实际premise、kernel/事件和真实EOF；晚到/UNKNOWN恢复全R=60结算，不退未知期间秒数。旧25保持cleanup_unconfirmed/R60/count1及旧根blocked，不以当前Pid0补其缺kernel/EOF。六个C06新生命周期均最终stopped，真实DB投影的confirmation原字节与source proof一致，见[persistent-six-sessions-verification](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/audit-20261011/persistent-six-sessions-verification.json)。这些实际正常证明未覆盖F112-01/03异常分支。

### M11 独立忙死、外部停止与证明归因

判定完整停止门因F112-03确定违背；下列独立方法的原件可限定继承，不因代码缺陷或历史观察者统一抹去。

- renderer_busy为C03冻结v2-06在实际sandbox renderer固定无限循环，真实input未ACK，原privatePID/init/kernel、die/wait/EOF及两Job零证明该对象结束。browser_busy为准确浏览器根PID19及birth_ticks、真实cmdline确认后SIGSTOP，区别于renderer/Node，后续停止原件成立。对应独立解析为[renderer-busy-proof](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/audit-20261011/renderer-busy-proof.json)和[browser-busy-proof](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/audit-20261011/browser-busy-proof.json)。
- node_busy与reaper_death为C04两个独立v2-06方法，分别固定Node循环和准确真实Reaper实例死亡，活Supervisor控制停止。Witness确实额外持两Job且finish可以Terminate，不能签私有句柄自然销毁；但as-run顺序是先actor自身完成stop/两Job实际零及退出，再Witness drain/finish。因此该独立对象的生产停止证明不由事后Witness冒充。其持句柄影响须保留，不能推广双监督自主结束。
- owner_control_lost、pipe_corrupt、SUP死亡、双监督死亡为C05 v2-07实际四方法。PassiveWitness只持进程同步/查询及两个读副本，父退出后才读，不持Job或写端。SUP死亡有parent_lost的Reaper原件和外部清场前已停止事实；双死亡只签该次物理结果、未知全reserve和同根精确恢复，不承诺任意双死亡自主停止。
- C06 control_path_lost在真实READY后切断两个生产控制进程的Docker访问，daemon未停。原件先有cleanup_unconfirmed、R60和拒start，再有自然EOF及精确恢复；该次对象因管道/正常宿主退出已物理停止，不能据此声称生产控制路径故障时必然自主完成证明。
- C06 hard_deadline明确冻结SUP的实际_db直到D+1秒，独立Reaper按原D-10触发，准确对象FinishedAt在原deadline_at前；两原管道自然EOF、两Job严格证明和同根持久恢复后仍结满60秒，不能因物理早停退未知余量。

最终6会话的CID/image/nonce/labels、kernel摘要、准确PID namespace/init、wait/die、原D、资源边界及两Job逐项独立解析全部相符，见[final-session-proof-verification](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/audit-20261011/final-session-proof-verification.json)。job_destroyed仅用实际flags、非继承私有句柄、无breakaway、准确owner/member实例结束及准确Open error2，未填ActiveProcesses0；另有错误名/缺premise/error5的失败关闭原件。静态F112-03不能反向证明这些正常原件的stderr没EOF，反过来也不能让常规零stderr证明超限分支。

### M12 兼容、许可与自包含

判定符合批准的受影响边界。012旧非空资料/活动升级保原行/旧主体字段和权限，只添既定新域；missing_baseline及坏前置类型事务拒绝后无HTML部分DDL。当前html_schema_shape/指纹失败关闭，坏ACL/policy/load/bundle不开放HTML；原业务不被改成新HTML parent，旧html11m不能被旧消费路径采用。

已读旧payload的OneCall exclude_none序列化、新profile互斥、旧活动/Gateway薄接线和旧影响测试真实command退出0；不是只看旧函数未改。正式runtime、vendor、license和构建脚本均在deploy，651个load对象实际一致；主Chrome实际credits及版本许可目录进入正式build context，没有产品运行依赖公共提示词、OPEN_project或DocuN临时实现。build所用本地OCI是项目deploy内固定材料，不将其误认为公开联网拉取或恢复旧runner许可。

真实synthetic API/生命周期/PG及容器准备、启动、停止链有原件；产品启动器新graceful-close调用与API lifespan接线已核。未在本卡启动正式用户部署、重跑充分未变G3—G10、验证真实provider质量或签发布。后续若修F112-02改变host资源，只补实际新load/image和该入口影响，不因此重审全项目。

## Panel最终改动的证据继承

当前Panel相对C06 pre只有leavingDocument、beforeunload/pagehide/pageshow及自动stop抑制，既有普通hidden/组件cleanup、输入与引用的代次/owner核仍在。C04正常两Native、C05迟到组合、C06旧bundle下真实hidden/组件卸载，方法从READY到判定都在同一个活文档，没有进入新文档退出分支。按真实分支与静态diff，可限定继承这些旧原件；不声称它们在新bundle重新跑过。

新文档退出分支只由新bundle的真实refresh及完整HTTP窗口签该限定行为。旧响应因generation/owner撤销不能重新赋owner或发input，普通同文档hidden和组件卸载仍请求精确stop；pageshow只清退出标志，不授owner。BFCache恢复、取消导航、跨浏览器和真实provider未验证，未升级新Must。没有用未跑的新目标阻塞已证正常链，也未以静态diff替代已真实发生的刷新反例。

## 执行控制与预算

已从原111规范性预算、C01—C06 timing、authority、原始事件、pre/diff/as-run、命令及清场原件重建前向许可。原43200秒，C01沿用；C02加21600到64800，C03加28800到93600，C04加14400到108000，C05加10800到118800，C06加10800到129600。C02同CID PG第7次有明确用户增量authority，不把后来C03或C06许可追认旧超限。工程C03—C06许可不改变产品HostPolicy的TASK-111-G11-P110-20261010。

3507条原事件独立分类后，18根、create45/start41、PG14/API12/browser11、image7/frontend4、模型9/OneCall9、HTTP1611/PNG182/public input68/internal26与现账相同。offline关联30由28个reserved加两个事后低影响许可检查组成；internal26包含三个迟记输入，不能当事前已登记。45/41为预扣尝试，不由现存40个容器倒算或退失败名额。

C06准确接收为2026-10-11T12:48:21.602848Z/994365953000000ns，总窗10800秒，末600清场。新root17=453.125、root18=140.282，PG停机确认段1.078和0.953，新增real595.438小于1800。各资源新增均符合C06前向累计cap，只有50—55新名字使用，56/57未用；没有root19或新模型。final停止元数据及端口原件显示精确40对象不运行/Pid0、登记实例已结束、两端口18111/55451无监听；新6行没有未知，旧25未知保留。此处是已保存停止事实，不是本审计实时运行资源查询。

现账real14546.863可以由18根合计14538.362加八个已保存外围补计8.501复算。但它不足以证明全部真实持有时间。独立定位的执行偏差E112-01如下。

root6在2026-10-10T02:03:30.140158Z、869276343000000ns结束，旧finally受已过期业务闸阻止。直到独立cleanup的pg-before，871554875—871555187000000ns，准确PG CID仍running=true/PID945；pg-stop实际成功结束为871556046000000ns。该root结束到停机确认间为2279.703秒，现18根账和八个补计均没有该段。文件哈希、命令、原输出与计算见[execution-budget-independent](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/audit-20261011/execution-budget-independent.json)。

确定事实是晚清场前同一PG仍运行以及现账无该区间。连续持有推断依据是唯一PG、既有start及无中间stop/start原件，未声称采到精确物理停机瞬时。按完整持有至stop确认保守核销，累计应为16826.566秒，较16200高626.566秒；若有可缩小该段的有效当时停止/重启/持有记录，应只读补核并说明依据。不能以当前已停止、同型号标签、后续预算采用或旧分类unknown把该段填0。该项是执行投入/授权核销问题，不能当产品停止实现已复现失败，也不自动抹去其间的真实测试。

历史偏差另保留如下。

- 原metadata/实施分类和C03/C04首读精确时钟缺失，不把保守减300秒的登记冒精确首次读取。C05接收前准备mono仍未知。
- C01实施7530.953对3600门超3930.953；原root6=3600.047对3600、C03 root10=1800.047对1800均保留超限，不改成0或以新许可清零。
- 两次低影响离线检查事后登记、三个内部输入迟记、早期pre缺失及曾撤销的薄接线越界历史都保留，不追造pre。
- C04 schema-fingerprint原字节pre没留；当前fingerprint/catalog已真实一致，可审当前对象，无法还原历史pre。
- C06 offline27在Infinity转int时失败，reserved次数保留，没有batch-finally秒数；综合phase记时存在。215.358秒仅是有批次终点的离线账，不能当所有实施/离线经过时间或把失败批秒数填0。
- root16因协调误操作空耗80.172、旧browser 600/step650/coord900提前闸、假hidden及READY前Reaper失败都留原件；C06对应修正依真正新方法关闭，未把旧FAIL删掉。
- 旧13元及旧78根按本卡与历史账保留，本次没有复核旧13元每条支付明细，不冒确认该全账，更没有新增真实费用。

执行轴结论为存在偏差，且全累计真实时间合规不能签通过。后续先由编排核销E112-01并给有效前向资源安排，不能认为111剩余运行额度由本审计恢复。

## 非阻断观察与真实未验证

非阻断观察O112-01为公开输入索引21个ACK的措辞不准确，实际17个远端成功ACK加4个服务端422，建议更正导航描述，不改原件。O112-02为上述历史pre与首读采样缺口；当前源和原件可审，不以缺历史pre取消充分当前事实。正则美元锚末尾换行疑点已依据[TC39官方CompileAssertion](https://tc39.es/ecma262/multipage/text-processing.html#sec-compileassertion)排除，实际没有m标志，未新增产品测试或登记为缺陷。

没有验证F112-01的实际调度频率、F112-03异常stderr分支、新修正产物、BFCache/跨浏览器、真实provider、用户数据、正式部署票据、产品全验收或内存全部释放。Windows/Linux证明只适用于准确已拥有任务实例及本卡锁定内核/运行边界；不是Stopped/Pid0单证，不声称任意已执行自由脚本的导航全路径原生事前拒绝。全球所有外部窗口状态无法由本会话证明，实际能确认本窗口未运行产品、未派Agent及核对区间必要冻结对象未漂移。

## 最少后续行动及正式文档建议

1. 编排把F112-01、F112-03、F112-02合成一次修复回原111 A+工程窗口；修复成功分支ready门、真实双管道EOF门和实际Node ingress的constraints类型/BOM原字节门。保单调D、preview独立预算、原四账、资格锁序、原数据和UNKNOWN，不由审计直接改产品。
2. 编排先核销E112-01。原件不足则将该持有段保为有明确上下界的投入缺口，按保守已知段计，不重置旧失败/时间。已满18根、PG14/API12/browser11、image7的旧合同不恢复；后续必要新image/load及集中定向验证要有新的前向卡面许可。
3. 工程只补三个缺陷的相关反例/对照与真实影响。Node入口若能保持四runtime，可复用原数学、编译包与两Native；新host镜像只核新load/actual runtime绑定、该拒绝入口和必要普通正常对照。SUP两处修正只补ready时窗和stderr/停止退款门，不机械重做六故障、32例或全项目。
4. 修复与原件完成后，本TASK-112/R-106只复核三缺陷、E112-01及实际变化传导。除发现新的跨模块影响外，不循环再做一次完整终审。编排据复核裁定批准有限G11关闭；本报告当前不签关闭。
5. 正式文档由编排维护。执行动态登记TASK112审计已返回、G11最终验收未过及本地发现向共享DEF的归属，保TASK111/所有预算和旧25UNKNOWN；架构动态仅记录实际修正后的ready/EOF/数据类型门与加载身份；最终需求不降Must、不新增BFCache目标、不改用户原始需求；文档变更记录登记这一次集中裁定和后续实际变化。未由审计写入DocuS或共用编号。

报告、原件解析、静态反例与交付回执均已保存并复读。达到合同覆盖即停止，无补跑业务、源修复或发布行为。
