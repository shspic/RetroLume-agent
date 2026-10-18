# TASK-114 / R-108 续作02 — 四项P1合并修复与关闭前定向验证

## 目标与交付

你沿原TASK114 A+工程窗口接续，一次完成TASK115独立审计确定的F01—F04（DEF034—037）修复、实际影响复验及已明确的必要余项补证，形成可交原TASK115窗口增量终审的稳定候选。不接管编排或独立审计，不重新开发已通过主要链，不每个普通步骤回传。

产物仍为 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-114-result.md，置顶“续作02／审计修复”，原53842字节、SHA-256 c0f970d48ac57d1081e79afa90bcab5822d4c6058e60ed7f9fb6f9b0cd770e2e全文作原字节后缀保留。新证据只入 DocuN/evidence/TASK-114/implementation/continuation-02/，旧115反例/FAIL和114所有原件不修改。

完成标准是四项P1有明确正确行为和最终版本证据、相关取消/期限/资格/晚到及必要安全余项足以增量复核；静态/受控注入/真实PG或HTTP/Browser分层，未执行不标PASS。整卡完成即停，不宣STEP017/M-1/整个项目通过。

## 项目、规则、窗口与授权

根 D:/shspic/project_NO3_RetroLume-agent；入口 AGENTS.md在该根。task_model、V4.0、公共AGENTS CHG-0003，七锁定指纹沿DocuN/evidence/v4-migration-20260930/rules-snapshot.json。公共根 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，AGENTS及WORK适用2/6/8章，同窗未变材料复用、变化头和必要缺失补读。需求v1.2、架构v1.28、执行动态v2.52、阶段07。

TASK114/R108/STEP017，父设计113/R107、当前独审115/R109，关联STEP017-P1、MOD008/FLOW007/API005、DR001—003、NFR002/003/005、SEC001/002和DEF034—037。用户已经确认采用完整技术包，并要求继续未完成任务；此为原Must修复及相同受控合成验证，不需重复采用方案。主控新前向许可TASK-114-STEP017-C02-20261013在TASK-114-work-decision.md和本轮continuation-permit.json，原许可没有自动复活。

接收A+增强执行，优先刚完成114续作01的原工程窗口，实际客户端/型号如实登记；原窗确实不可用才同等A+新窗最小恢复，不因已完成任务的模型标签重做。原115审计窗保持独立，不在其窗口改产品，不派子Agent/并行测试。产品/测试/配置及本卡资源独占，主控维护共享状态。

原114根18/18、PG create/success6/start27、Windows11、API5/Browser3/build3，旧C01活动封口9739.953（9185.438只是封存中间观察）、offline51.238/hold377.280及旧55525.796日历/净投入unknown保留。115另有根3、API3/Browser2、offline125.610/保守hold14.874/活动上界5490.683454，均已结束不借余额。旧目录误计、首次bundle pre缺失、异步两超时、所有FAIL/G11/25/UNKNOWN/R60/count1/13元/626.566不抹去或追认。

## 最小充分输入与断点

先读本卡、根规则、正式文档当前头及本轮主控许可；读TASK-115-result.md四P1、第79—101行的具体继承、第171行后最小余项。实现者现在可读独审完整报告与原件，不能只凭聊天摘要修。

唯一已采用原完整A—D在DocuN/evidence/TASK-113/design/revision-01/current-contract.md，81813字节/8a56ebf3c1715895e3ee7a0dcf1f621b591335400e9898aa00df8cb2b7a61aaa。原目标/正常链不变。本轮只补问题和实际传播，不重新研究技术路线或把只读恢复扩成旧活动执行恢复。

现前基线为114/C01 final/manifest.json的216当前文件（212源、4bundle）和1移除输出；原件在final/source、diff和pre。115已确认这些字节未动，报告37767字节/7d34ec7e7f433effe3bf51367c68229a566dc525361a30c4b2c496702f4ca67a。源码改前留本轮副本/hash，每批as-run和最终真实字节保存，未登记漂移先查明不覆盖。

精准反例在TASK115/audit：offline/attempt-03/01-restore-cancel-overwritten.json、02-publish-after-accepted-cancel.json、04-upload-after-accepted-cancel.json、05-post-capture-operation-deadline.json，browser/late-only/result.json及截图，offline/readonly-projection-input-02.json。前两类工厂/输入/延迟边界有受控替身，F03是实际Chromium与冻结bundle/路由回包；它们不冒真实PG完整恢复。F04合法依赖行与源码反例已确定，但两60秒异步夹具未得到动态结果，根因unknown，禁止第三次机械重跑原诊断。

源持久frozen、原Hub选择target07/generation1、旧6个容器全部停止；全部旧逻辑slot01—08占。不得解围旧源、回收意图、启动failed目标或把Stopped当normal。正向修复验证改用下述新受控测试域，旧源码/包/控制/历史只读保留；生产代码仍只在正式产品目录，不import证据脚本或公共提示词。

## 四项修复合同与关键决定

### DEF034／F01 取消与不可逆成功准入

统一ControlHub job的请求取消、执行者确认、不可逆准入和终态CAS。用户取消请求被受理不等于已停止；只有执行者在真实安全边界确认没有尚需收尾的工作，才确认cancelled。成功提交须同时核期望revision、允许前状态、当前阶段资格，不能临终读latest revision再覆盖cancelled/cancel_requested。

为文件发布、上传EOF后验证/发布、恢复last-load后seal、资料墓碑COMMIT、readonly维护/selector建立明确短CAS线性化准入。取消先胜时不进入对应副作用或成功许可；准入先胜、动作已不可撤销时取消要如实返回不可取消/待核结果，不能确认取消再发布、seal、删除或选择。对进入维护后无法无痕回退的source状态给真实未完成说明，不自动normal。短journal锁只用在许可CAS，不能持它等文件/PG/网络。

已发布文件/已提交墓碑/已生效selector保留，响应丢失按原键只读核事实；GET/reconcile不重发/退款/新建目标。恢复取消后准确目标封存/撤loader及admin/停止，不写verified。上传取消不能EOF后received；未发布pending可准确收尾但不删旧包或全目录。所有业务kind的取消语义同机制、不同不可逆点，正常终态幂等和跨选择Hub查询保持。

实现可自主采用私有job受限字段/阶段/准入票据及新内部helper，状态/前后兼容须在结果列完整。旧合法terminal/文件事实仍可只读；旧无新协议字段的inflight不得默认补时限/恢复许可。新增协议与deadline字段不出数据包或普通DTO秘密域。不新增业务表/列、外部服务或停线平台；若确需关键模型扩围，报告具体冲突并停受影响部分。

### DEF035／F02 一个覆盖完整消费链的绝对截止

job首次真正消费时固定operation_seconds的绝对单调截止及受信时钟域；同一次capture→spool→ZIP→全量校验→copy/fsync/no-replace→收据，restore的allocate/初始化→组件load→校核/seal→成功收据均传播同D，不另起started或因重试/进度/换阶段延后。用户准备/明确确认前等待与真正执行分开记录，不能把每阶段当新预算。

每个不可逆准入和成功许可前重新核D，PG/connect/lock/statement及可控I/O有界量取剩余时间和原子上限较小值；不足即停止，不把timeout=0当无限。期限过后不得启动新阶段或授published/verified/selected成功许可；已有确切文件/DB事实保留为未确认/实际已发生状态，不删除文件假称没副作用。清场只做本对象必要撤权/关闭，不以清场额度续业务。

持久job时钟域/进程重启未知不可凭旧monotonic数字或墙钟新发有效许可，不重置已用时间；GET仅核原有效事实。不改变原模型/工具/preview的计时、8秒ready/D/StopProof或四账。本卡低值profile与准确延迟证明超时路径，不造内核卡死或声称所有磁盘/驱动故障已可强制终止；新增平台需求应交回。

### DEF036／F03 新鲜上下文和生命周期保护

capabilities刷新必须有请求序/取消与完整生命周期检查；同一control的selection_generation不可下降，同代不同dataset/instance不能被陈旧回复强换。未mount/已卸载/更早请求返回不能提交caps/context/资料/计划/记录。不同control变化也需受信重连或新的明确页面/会话依据，不能任一迟到包自动替换全局身份。

区分稳定Hub jobs/by-key/包历史查询与依赖当前dataset/instance的capabilities/saved-records和动作；不能整个/api/data前缀免所有namespace/响应保护，也不能修成切断旧业务键只读核对。bootstrap能力GET如何安全接受真正的新身份由实现者按既有认证/接口决定并记录，不加入用户无意义的确认流。

最终bundle测试同control generation1先到、generation0晚到仍保持新readonly；请求上下文、旧localStorage/IDB草稿、材料/计划/记录均不回退/串写，刷新GET-only。反序路由fixture属前端真实/受控回包层，另在新完整HTTP流程检查新身份更新及旧Hub查询确实可用，不把前端夹具冒真实selector。

### DEF037／F04 正文资格与删除覆盖

saved_records.memories及历史相关正文在同一读取查询/一致只读快照内复用memory_revision_readable或严格相同的source/event/upstream依赖资格与删除overlay；仅资格明确true且自身active/有body/无自身墓碑才可给正文。false或unknown不返回正文，availability给明确dependency_invalid/source_deleted/无法核对原因，不能只检测当前activity scope或memory自身墓碑。

保memory头/版本/原hash/依赖、purge pending/done、旧备份时点事实，不用改头为revoked、删body或伪purged修投影。检查learning/teaching/interview历史来源/事件和上游依赖，旧scope删除检测不能代历史依赖；只做同类必要读取资格修复，不改原生成/预算/immutable纪律。

真实新PG和HTTP覆盖合法active来源依赖→删除、source pointer/revision/hash失效、event/上游失效、有效样本仍可读；默认respect_current恢复后依赖正文抑制，snapshot时点明确政策和原事实分层。F04旧两超时先读其脚本/环境/loop差异，不复跑相同unknown方法；采用项目既有Selector兼容loop、明确新数据库及真实TCP方法，有界输出/SQLSTATE，不以fake cursor/mock或旧frozen 42501签动态通过。

## 文件范围与继承

允许原data_exit内api/control/contracts/packages/snapshot/restore/repository/deletions/maintenance/files/spool/config等必要实现与新的同职责内部helper；前端data/context.tsx、DataWorkspace.tsx、dataApi.ts、ReadonlyRecords.tsx及必须的main上下文/意图传递。必要memory/learning/teaching/interview读取资格包装可定向改直接涉及函数，原写/预算/StopProof/解析核心不顺手改。

013仅在已有只读资格函数最小EXECUTE/安全投影或本原契约必要身份修正确需时可精确改并同步固定schema/codec/角色指纹；不得授普通app owner/admin/loader/业务UPDATE或放宽immutable，001—012原件不改。现已合法C01包继续正确解释，不让新增私有job字段变导入执行权。代码、状态/签名/ACL/返回值实际清单完整回传。

允许本卡backend/tests中test_data_exit前缀文件、fixtures/task114新增C02入口，frontend/tests中task114-c02前缀mjs、必要最终dist与README状态/操作文案。改既有测试先存副本，原业务断言保留，旧114/115证据只读；审计的fixture可以复制到本轮后有据修，不改原反例。依赖锁/安装/镜像pull-build/Git写/公共库/DocuS/AGENTS/原始最终需求禁止。

旧C01的真实94行/4原件/14组件加载、role/seal、两锁序/迟到COMMIT、正常删除、真实SUP/双EOF/四账及正常最后TCP/Browser按实际字节/作用保留；本轮变到的cancel/deadline/投影/上下文才追加。115认可的相同机制归约写清，不把已通过正常链全部重跑，不重审G11/旧25。

## 精确新合成域与资源

原source/target04—08及原业务control/journal/selector/credentials/包/旧数据全冻结，不启动写、改mode/重seed/回收slot。旧执行总控制账implementation/control可按新许可追加事件/累计资源记录，原内容快照和旧事件保留，不开第二实时总账；这是执行额度账，区别新测试业务ControlHub。

本轮验证用最多三个新对象，不借旧八slot，独立受信profile TASK-114-C02-PG17，固定本地image sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f：

- source：retrolume-task-114-c02-source，卷同名加-data，127.0.0.1:15452→5432，库retrolume_task114_c02_source。
- target01、02：retrolume-task-114-c02-target01/02，卷同名加-data，127.0.0.1:15453/15454→5432，库retrolume_task114_c02_target。两个独立cluster只实际需要才建，不把failed目标恢复正常或改名增加机会。
- 每个固定1CPU/512MiB/pids128/restart=no，一份named卷到/var/lib/postgresql/data，无host bind/socket/privileged/host network，最多两个同时Running；低于2GiB内存门前不启动，入口在写新target意图前先核，目标阶段再核不足准确停止不循环占新slot。
- API仅127.0.0.1:18114、必要Vite15114沿原task端口但与旧进程无冲突才用；Browser本卡新profile，既有依赖/Chromium，不下载。新Native SUP/preview/真实模型/provider/费用/公网均0，原未变管理/停止链继承，不伪造StopProof。

所有新业务工作根为DocuN/evidence/TASK-114/implementation/continuation-02/synthetic/下互独立source-root、backup-root、restore-root、control-root、scratch、sentinel-root、browser-root；不复制旧control注册器为新执行权。资料/记忆/活动用新合成ID和明确限额，DSN仅本新cluster，凭据随机仅stdin/限定Env或DPAPI私有引用，不argv/普通日志/DTO/包dump，不读真实user配置或fall back旧DSN。

创建前核完整image/名字/卷/全TCP状态（含Bound而不只Listen）/目录和内存，成功后绑定完整CID/image/name/label/volume/port再SQL，后续只准确ID。遇碰撞/身份未知不改名/recreate或停第三方软件；本轮不用旧55461，不能改Windows网络/服务。旧gdpsvc停止由用户完成，不借此取得更广系统权限。

计划顺序：先完成全部四修与离线正确断言；一个新source生成最小合法源/记忆/历史和新包，测取消/超时/发布/正文及source_delete传播；target02专测last-load后取消与撤权失败封存，target01完成默认删除overlay的正常readonly恢复/核对。激活取消在不可逆准入前应不切，入准入后正确拒取消或给待核事实，允许一条新独立测试源的正常readonly选择；旧selector始终不动。根据依赖把正常选择放在本轮所有需要source normal写的场景之后，免为测试解围新冻结source。

## 前向预算与连续验证

本许可TASK-114-STEP017-C02-20261013追加21600秒分段活动工时，接受首工具实采UTC/mono，接受后48小时日历门；正常读/实现/修码/测试/文档计活动，最后1200只清场。只有真实外部等待/用户中断、全部自有资源准确停妥/无子消费者且暂停时间原因断点记录齐全可暂停活动，无记录间隔保守计。生产operation deadline不随执行工时暂停，所有实际资源持有始终连续累计。

TASK114根上限18追加6至累计24，旧18不清零；本轮最多6个合并真实根，根内普通方法/有据修复连续、不逐target多扣或换根规避失败。PG create尝试原12不加（已6剩6）、成功物理对象原9不加（已6剩3），新增三个对象正好物理上限，故严格先离线准备。PG start原32加5至37（已27，本轮余10），API原8加3至11（已5余6），Browser原6加3至9（已3余6），build原6不加（已3余3），Windows原12不加且本轮不新增业务窗口，preview/Vite旧用0不消费preview。

离线原7200/已51.238、真实持有原10800/已377.280/业务门9600、清场1200均不加，按新阶段继续旧累计；115独审的3根/API3/Browser2/14.874持有/125.610离线/控制缺口单独保历史不挪回开发账。商业费用0，真实Provider/模型0，源码不以卡名/窗口重置任何次数或投入。

先在唯一control保存C01旧receipt/events身份和原permit，追加C02绑定/累计上限/阶段，不直接替换旧received_monotonic_ns。每个真实root/对象create/start/SQL/HTTP/Browser第一消费之前登记，目录/AST/metadata不占根；argv脱敏/exit/SQLSTATE/时间及每个方法前缀立即落盘，后继FAIL也保存。新code/profile/输入最终as-run快照前后hash，无法重建的旧缺件保持unknown，不倒填旧原件。

真实资源不足先实现/离线，不停用户app/daemon或降低门。默认sandbox拒绝按实际精确低风险权限申请，自动审查拒绝要记录动作/理由并完成无依赖工作，不绕过。所有新容器、卷、数据、失败包和日志最终Stopped并保留，不DROP/REMOVE/prune/递归删除。释放host bind probe立即close，socket可绑定不等容器/PG/业务已通过。

## 关闭所需定向方法与独立复核

A. F01审计三个已证取消点转正断言：真实ControlHub和no-replace文件、真正上传EOF前取消、restore load-return/seal边界；再对新PG target02真实取消/failed/不可verified/撤loader-admin和source_delete/activate的实际准入做有界验证。每类测cancel-first与admission-first（后者不假已取消）、重复/同键只读核事实，已确认取消不能被成功覆盖。

B. F02用同job唯一D，在真实capture后封包/Reader/发布前受控延迟，restore初始化/组件后/seal前相同预算，不同子阶段不能重新获operation_seconds。可信低值profile清楚记录，无超时后published/verified新许可，已发布事实保留/同键核对不复制，PG timeout剩余量最少和0边界明确。受控延迟不是实际kernel卡死，不能凭throw异常说已证明所有挂死能强停。

C. F03修后最终bundle真实Chromium重放115反序两GET和卸载/旧request/同代不同instance旧草稿；当前context/caps/材料/计划/记录和后续请求不降级。新真实HTTP普通导出/上传/取消/同键hash冲突/丢响应刷新只GET，以及本轮正常readonly选择后旧Hub键/包仍可查；正确新身份可接收不能修成永久卡旧身份。

D. F04明确新PG合法active memory→来源删除/替换、上游或事件失效时源码资格和实际HTTP正文None/availability；有效样本仍可读，body/hash/head/purge元值不被修投影改变；本轮正常target01尊当前删除overlay后同样抑制依赖正文，source/旧包和被删元数据保留，既有历史学习/面试正文相关影响核同一资格。旧两超时不算产品已闭，新的实测需要保存实际SQL/行值/HTTP原件及环境差异。

E. 余项只按115第177行的明确机制门合并：九online guard在共同合法准入后反例（不拿frozen或无DML权限挡全部冒通过）；真实reparse/链接与外部sentinel前后字节，权限不足就明确限制；JSON深度/组件容量/上传中断，spool/copy/fsync/半发布同键补收据，半注册/seal/selector拒绝及不授新权，实际HTTP/普通日志secret marker。已由同机制/同字节/原动态严格覆盖的变体说明继承，不开无界组合或整仓压力试。

6根/3对象是成果组织边界，不用完即停。若余门需要更多资源或推翻关键前提，完成不受阻部分后给一个明确最小剩余清单，不自行回收slot/解除旧源。每次普通失败有准确因果再卡内修/复验；同因两次有证据修正仍失败、任一门到限、权限未知或超范围停依赖消费者并精确清场。原RootLease/迟到COMMIT/角色/四账/原SUP/G11未变不重跑完整正常链，变到的真正传播才补。

稳定完整候选后交原TASK115独立窗口review-01，仅核四P1/必要新证据和实际影响，继承已独审通过范围，不重开新的全面审计。本卡不自签四DEF关闭或stage；下一复核卡由主控回收后另给，不预派/不自行占TASK116。

## 停止、回传及共享归属

每根finally及外层准确有界清场核CID/image/label/volume或PID/birth/owner，防CLI超时掩消费者存活；只本卡准确树/容器，unknown不冒停止或退款，不全局kill/service/network reset。记录所有自有Running=false/Pid0、端口全状态无本卡占和Browser实际close/根process结束，不仅看runner退出。已有文件/墓碑/selector副作用按事实保留，只有本单准确新失败文件处置有授权，绝不删旧证据或取消后假清空成功。

统一结果先写真实结论/完成与未验证、四DEF正确契约和实际作用、文件diff/pre/as-run/post、状态/签名/返回/协议字段清单与证据导航；再列A—E逐层实际方法/环境/SQLSTATE/argv脱敏/exit/耗时、错误根因及修正次数/旧停止门是否同因、预算/资源/side-effects、所有历史限制、正式文档建议及原115增量复核输入。

原53842字节全文原后缀保留，其他成果/FAIL只引用；源码/编译/真实层不同结论分开，不造SQL字符串断言/mock事务证明，不因未测的一般组合宣MUST全部动态通过。保存复读TASK-114-result.md后只回复一句话事实及完整可点击结果路径；主控负责DocuS/CHG/DEF最终关闭、原始需求只读、公共库不写。本次人工仅转本卡给原A+工程窗口，无用户密钥/资料或重复技术采用需求。
