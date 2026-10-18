# TASK-112 / R-106 — G11有限交互解释完整候选集中独立终审

## 目标与交付

你是独立增强审计Agent，在一张卡内完成G11-P110已采用有限切片的代码、证据和执行控制三轴终审，判断TASK-111当前冻结候选是否具备交编排验收关闭条件。审计对象是完整G11实际增量与必要直接依赖，不是只看最后五个测试，也不重审全项目或把前期每轮修复再各做一次审计。

交付 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-112-result.md 及 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/。保留快照、最小读取范围、独立性、M01—M12逐项判断、确定缺陷/证据缺口/执行偏差及非阻断观察、剩余精确行动。审计一次完成后统一回传，不接管编排或直接修复，不自签项目、发布、M-1或全部STEP。

本卡只读代码和现成原始证据，业务运行额度0。不要启动旧runner、补跑测试或创建资源。已有充分证据按身份/配置/作用域继承；有真正缺口则说明为什么现成证据不成立、最少还缺什么，不把普通版本标签不同直接变成全套重测。

## 项目、规则与接收安排

项目根 D:/shspic/project_NO3_RetroLume-agent；根入口 D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。模式task_model、V4.0、公共AGENTS CHG-0003。公共根 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，读取DocuS/AGENTS.MD与WORK适用2/6/8章，使用DocuN/evidence/v4-migration-20260930/rules-snapshot.json的七锁定版本，不自动采用后来版本。需求v1.2、架构v1.19、执行动态v2.41、开发阶段07。

父TASK-111/R-105，关联TASK-108/110、FR-009、SEC-003、NFR-002/003、B-01、STEP-015/016及API007。用户2026-10-10已采用G11-P110，持续授权实现、必要验证和完整稳定点的隔离增强审计；本卡是该既定终审门，不是新技术方案、用户库/真实付费或发布授权。

接收A+，由用户配置中最强且胜任该安全/事务/进程/前端异步审查的Agent承担。必须新建真实隔离审计会话，未参与110/111当前候选设计实施，不沿用111工程窗口，不继承其聊天/推理，也不派子Agent。真实客户端/型号如实记录，A+标签不冒充型号。只能一个审计者串行持有本卡；原111工程窗口冻结，不并行写产品/证据/运行资源。已有模型身份标签不作为否定已完成事实的理由。

审计接收前产品、夹具及build冻结。身份清单为 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/orchestration-20261011/frozen-inputs.json，其中105项源码/配置/构建对象沿用C06最终快照，只作身份导航，不要求105份全部全文重读。开工独立核对必要对象；漂移停止相关判断，报告具体path/hash，不对旧快照签当前通过。

## 独立输入与已采用边界

先读根/公共规则、本卡、DocuS/最终需求文档.MD的FR009/SEC003/NFR002003/B01、TASK-110-result.md的C2—C7及D1/D2。110是被采用的设计合同，其原pending措辞仅表达当时状态；采用依据是TASK-110-work-decision.md首段及下列规范性细化。不要读取该文件中的主控文档验收自评或工程验收结论。

有效合同是有限interactive_description.v1、html_explanation.v2、compiled_interactive_html.v1和retrolume.preview.v2。模型不提供可执行自由HTML/JS/markup/URL/DOM命令；固定项目程序处理有限AST及set_number/reset，保留真实计算/图形。合法描述和输入不能引起导航、URL/历史变化、新target/frame；突破时判缺陷并关闭能力/精确停止，不冒任意已执行脚本全路径原生事前否决。原109同文档hash反证不改，不复演它作为本卡前置。

原四表、两个NOLOGIN角色、父/来源/记忆资格、同COMMIT业务正文/成果、旧四账/OneCall/UNKNOWN/worker主权、独立持久3次180秒预览预算保持。只确认停止才能退未用preview秒；未知保满reserve并封新start，预览结算不改原四账。t0在预扣前，ready最多8秒且在D-10前，末10秒关输入，soft-stop2/诊断15、窗口30—60秒及原固定单调D保持；工程根时窗不能延产品截止。

下列已获实施许可的细化一起审，不用原未采用承诺或方案中仅建议的工程次数替代正式许可。

- Linux结束证明采用实际私有PID namespace/init结束与准确子树/nonce/kernel、wait/die事件、无restart、CLI/真实管道EOF、Windows登记实例及两Job严格结束组合，不指定停后读host cgroup目录为唯一证明，不宣内存全部释放。仅Stopped/Pid0/kill返回0不足。
- retrolume_html_owner补资格闭包必需列级SELECT：pdf_review_candidates(id,version_id,status,page_count)、pdf_review_pages(candidate_id)、pdf_extracted_pages(version_id)。无表级正文读取、DML、grant option或membership扩大；审实际012与合成列补丁/ACL，不以“有GRANT”本身判新权限域。
- 私有Job结束可为实际Query零；或事前实际创建/flags/成员/非继承私有句柄、无breakaway、准确owner/子实例均结束以及准确Job名Open仅error2的job_destroyed。后者不填ActiveProcesses0；错误名/缺前提/error5等仍失败关闭。观测者额外持Job或主动Terminate会改变归因，不能签自主终止。
- 产品HostPolicy基础许可仍TASK-111-G11-P110-20261010；C03—C06是前向工程许可，不变公开权限。唯一新测试registry为continuation-04/synthetic/control。旧25缺kernel/EOF的UNKNOWN/R60/count1和旧根blocked保留；开发隔离不等于产品公开换根或绕过未知。
- 生产preview非root UID/GID10001、真实sandbox、network none/read-only/CapDrop ALL/NNP/seccomp、private PID/IPC/init/no restart、1CPU/1GiB/swap同值/pids256/SHM64MiB、原安全tmpfs128+32MiB，无host bind/socket/preview端口/特权。一PG/卷/preview并发，真实provider/用户库/安装/发布未授权。

独立判断前禁止读取TASK-111-result.md各轮自评、111实现聊天/推理、主控111验收段、orchestration-receipt-07/received及methods-byte-check中的结论。原始测试PASS/FAIL、调用日志及as-run记录可以读取，但必须验证其所称事实。先留独立判断/定位，再如确有需要核对实现者披露，只读相关披露段并记录接触时点和影响，不用自评证明自己结论。意外暴露如实披露，不伪称未见。

## 当前冻结对象与证据入口

核心当前SHA256如下，其余身份见完整清单。

- backend/app/preview/production_supervisor.py = f757477cf2ac9cc321c036383f9b06a7cb18e88a174ae5197d2753fa4c99f9c9。
- backend/app/preview/host_job.py = 51163b93cad0efd0a14536b070ae2102a12d470043cc03e9146d8e98bfed7841。
- backend/app/preview/repository.py = bf5e04cd8aaed6ded8c120b601ec7d8718df6e4484747203a3791eef8188de06。
- backend/app/activities/repository.py = 29c3415576382623e300d67d9d0c76b945bcb410c7e981976a44022f6152608d。
- backend/migrations/012_html_explanations.sql = a400170b010ad5f8adca2003a6829519b435b14160ade01fd8283e9fcd3c87b7。
- frontend/src/explanations/HtmlExplanationPanel.tsx = 7c7204690f3d2f72129c9ab377101fe849ad98eef9dbf0b6432bfca5e050b513。

最终生产image为sha256:c23c7489d56fa2cc955dc15e86e0b710b476589997d57ee33c9eb9f3949e826f，load bea3f1ebc033635fdac71e1134ed66632947d994b701c9a7b76d942ff036ad00。四runtime集合6cc300164a6cb364d9bd0bae4897f06d3f6a65cf5d4272477d2bccde67312597。故障v2-06 image sha256:8d3811cdf4b9d6edd00a5dd438e382d1700335fb0109084a59e69813fbc97016，load3762e87b9fafca30c90de616018006eddeb5defcee6dee9c9f8a92618027342f，不替签v2-07正常导航/帧率。新最终bundle assets/index-DeYBJidT.js SHA e76cacf45e2a435446277a1977a01a87bd5da4b09665e95a67bc834be9c8a488。

以下入口均在 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/execution/，展开后是绝对路径；审计证据索引文件已逐项给完整绝对路径与hash。不要从头读取上万份日志。先按原合同找相关产品与原件，缺关键链才扩读直接依赖。

- 初始差异：pre/、source-pre-identity.json、delivery/pre-post.json和pre-final.diff；continuation-01/delivery/pre-gaps.json。pre不存在的地方只记真实缺口，不造旧件。continuation-03/04/05/06各final/source-identity及实际source-differences/source-changes与diffs，后两轮包含私有Job和Panel最终增量。
- C03：final/image-bindings、evidence-manifest；root-10/step-08-probe、最终固定程序/描述/协议/数学边界；root-11/预算/rollback/upgrade的逐方法实际输出；root-11/step-15-faults/renderer_busy和browser_busy原件。它们是独立故障variant范围，不替签生产运行任意脚本。
- C04：final/Native-and-normal-UI、normal实际ui-effects/PNG/ACK、root-14/step-09-races、六列资格及启动异常原件、step-10-faults/node_busy与reaper_death；final/pre-gap及source-differences。Witness持句柄/finish主动终止的具体影响必须按触发与证据归因分析，不能省略或直接全盘抹去。
- C05：root-15/step-03-tail/tail-attempt-2/tail-effects.json；step-01-job_probe实际辨别；step-04-faults的owner/pipe/SUP/双死亡、pretrigger/kernel/被动EOF/before_external_cleanup/same-root恢复；final/会话和as-run/source/raw索引、cleanup-only/never-created-full-R-recovery。
- C06：final/source-changes/as-run-bindings/five-methods-final/active-refresh-complete-HTTP/session-proof-index/runtime-originals-index；root-17真实hidden/unload和两故障，root-18修正refresh。81份runtime-originals是原字节副本，须核copy与被引用原件身份；不能只看汇总PASS。
- 执行控制：budget.json、events.jsonl、各timing/phase、root原始命令/开始结束/精确cleanup、C06 final/event-ledger-as-observed、command-index、failures-and-reuse、exact-resources/ports；全部旧attempt和失败保留。工程许可与上限见本卡执行控制审查要求，不执行这些runner或命令。

## 审查要求：一次覆盖完整实际影响

代码轴先从实际增量形成自己的判断，原M01—M12以110 D2原文为准，下列是重点而非新Must。说明每项“符合/确定违背/无法判定”、实际定位及影响，避免只复述实现状态。

1. 模型到业务正文/有限描述/编译包/固定程序，两处Python/Node校验域、规范JSON/hash、AST引用/原型键/重复key/UTF-8/尺寸/步数、非有限值和类型边界一致。代码/URL/HTML仅拒绝或文本，固定程序无危险sink/任意代码/文件网络动作出口；数学与图形真实，不用硬编码样例替代。
2. 012四表/NOLOGIN owner、SECURITY DEFINER搜索路径/ACL、不可变字段/预算/事务并发和artifact资格逐层对账；原record_outcome同事务hook/失败rollback、旧四账/worker主权和未知不重发。不能靠测试全绿跳过实际SQL与Python契约冲突，也不能因旧函数文本未改自动排除传导。
3. runtime/renderer-host/CSP/实际Node/PW/Chromium加载与许可清单、完整frame/target基线、实际argv/UID/sandbox/限制、产物身份一致；产品准备/启动/停止不依赖DocuN临时实现/公共库/OPEN_project。记录固定程序边界，不审理已废除的“执行任意脚本后所有导航原生事前拒绝”承诺。
4. 公开读取与stop/owner输入权，activity/parent/source/memory/取消资格，同键/丢回包、真实PNG/ACK身份序列，检查前后竞态以及前端跨视图/owner/代次、真实bitmap销毁和引用迟到。当前Panel文档退出守卫重点看beforeunload/pagehide/pageshow与同文档hidden/卸载路径是否兼容、旧响应是否能恢复owner或发送动作。
5. 预扣/起算/ready/关输入/单调D、3次180秒、不明create找回、不退款UNKNOWN、同根重启恢复以及实际Linux/Windows/Job/EOF证明。私有recovery_observation与已结证据重用不能授公共退款或假树空。SUP/Reaper/独立观察者/验收者先后及权限分明。

证据轴对M01—M12建立原件链，明确正常两Native/数学/图形、32边界、域与整帧、管道/输入权、COMMIT/rollback/费用、资格竞态、迟到/三生命周期、预算/恢复、各独立忙死/故障、兼容与许可的实际方法/版本/环境/结论。不能以六停止覆盖renderer/browser/Node，不能以计划matrix填actual；历史variant、观察者干预与生产路径不同如实限域。

特别核最终Panel改动的证据继承。hidden/unload和原正常两Native在旧bundle，C06修正refresh在新bundle；静态diff说明未触发新文档退出分支是否足以保持这些限定原件适用，由你独立判断。真实影响才指出缺证，不默认重跑全部浏览器；不存在的新BFCache/跨浏览器/真实provider目标不自动升级Must，若发现确定缺陷仍按实际影响报告。

核首轮刷新页侧PASS与服务端两个旧文档stop尝试及ClientDisconnect的反例，再核新bundle完整HTTP窗口37条、起止边界、ownerless、原D/starts和清场POST分层。不能把请求未被接受说成根本未发送；旧FAIL保留，新的实际修正证据才可能关闭该缺陷。

执行控制轴独立重建原卡及C01—C06的实际授权、前向增量与用量，缺时/pre/迟记/超限不清零。冻结审计不恢复111剩余运行额度。C06许可基准：根最多18/当前18，单根1800；新增real1800、累计16200/实际14546.863；create47/start43上限、实际45/41；name50—57仅新用50—55；PG start14/API12/browser11均实用满；image7/7、frontend4/5、model/Windows9/10；HTTP1611/5000、PNG182/3000/public68/300/internal26/500。综合C06实际接收UTC12:48:21.602848Z+10800秒/末600清场；旧13元、第一采样缺口/旧超限与离线漏计批内秒数不能删。

可读原111各卡规范性预算条款或原timing/caps/authority原件，避开其实现自评。区分执行不合规、确定产品缺陷和证据失效；普通超限不自动抹去有效证据，也不能隐去。现成对象停止metadata、Global/端口与精确归属收尾在证据中核，不启动Docker或以目前Pid0补旧25缺kernel/EOF。原旧根blocked/UNKNOWN保留且本批无新未知须有持久原件。

## 资源、允许写入与停止

只读上述必要产品、对应夹具和直接依赖、历史原件、锁定规则；只写TASK112报告/证据。允许自己用纯元数据脚本哈希、有限diff、JSON/日志解析、计时/次数/数值oracle核算；不得导入/运行产品、compile/unittest/build、SQL/PG、Docker/Job/进程/浏览器、模型、安装/下载、真实配置/凭据或Git写。不得执行任何旧授权runner、不改源/测试/迁移/锁/DocuS/111证据。必要机制原始资料只读已有本地资料；确有关键API不明可有限查官方一手资料最多6页，保精确来源，不扩新方案研究。

一次审查综合最多10800秒，从实际接收工具UTC/mono固化，记录实际阅读/元数据操作与准备缺口。无按文件数/命令数的短时限和真实运行补测额度；不用额度尽为目标。达到合同覆盖即停止。版本漂移、确实缺关键输入或越权风险停止相关依赖并完成可独立部分；发现明确越权/数据破坏先留证说明，余项仍一次完成。本卡不自行修复或要求用户替你启动资源。

所有发现给具体文件/行、触发、影响、事实证据/可信度、最小修正或最小补证；不得把非阻断观察升级新硬门。三轴分开判定，可输出代码通过但证据不足，或合规偏差不阻证据的限定结论；不能只给一个含糊“有条件通过”而不列条件与归属。

## 回传

保存TASK/R/实际身份与独立性、快照/读入hash、代码/证据/执行控制三轴及M01—M12完整结论、确定问题/非阻断/真实未验证、范围和机制局限、实际命令/时间、最少后续修复或补证及正式文档建议。给明确是否可由编排关闭“批准的G11有限切片”，不签项目/所有STEP/真实provider/用户数据或发布，也不要求重走已弃用的109方案。

结果保存复读后，只回一句话结论及可点击绝对路径。若无阻断，编排据你的独立报告裁定关闭；若有阻断，由编排把真实相关问题合并回原111工程窗，复核仅缺陷和实际影响，不循环重复完整审计。
