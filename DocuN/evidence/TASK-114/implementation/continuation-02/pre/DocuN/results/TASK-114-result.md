# TASK-114 / R-108 续作01结果

续作01完成真实隔离恢复、删除覆盖、原件锁序/迟到提交、源冻结与只读选择、最终HTTP/浏览器等主要链及范围内修复；仍有原合同异常子分支未执行，累计真实根已到18/18停止门，建议保持未完成实施候选，不能签全部29项或直接宣完整验收。

一、断点和本轮实际成果

沿用原TASK114/R108、STEP017-P1采用、V4.0/CHG-0003和续作许可TASK-114-STEP017-C01-20261013。本轮没有派子Agent、改公共库或DocuS、借旧任务对象、调用真实provider或新增费用。旧34931字节结果作为本文件后缀全文原字节保留，SHA-256仍c655556d7b783a871e34c5a50c40cb9d477504d0b8d389f028e14f68b091d1af。

真实首工具批UTC观察为2026-10-13T02:43:31.5316719Z。接收边界保守取同批早31.532秒的02:43:00Z，monotonic由bootstrap实采反推，明确不是冒精确首工具时刻。活动段从首个非只读操作前实采02:46:28.968841Z/1131051312000000ns开始。中断、端口/内存等待没有登记暂停的间隔均保守计活动，没有倒填暂停或清零旧锚点。

原source CID与55461复用。端口先实际WinError10013，主控定位占用并通知释放后启动成功；没有换端口、重建source或操作项目外服务。内存多次从入口通过降至创建门不足，均保留采样/FAIL；修正factory先核host/内存再登记意图，后续不足未消耗新slot。

target04真实加载失败，原因是memory_body_guard的FOR KEY SHARE要求loader没有的UPDATE权限。修复只在受信loading身份分支改为普通SELECT，在线分支保原行锁/拒覆盖/正文hash校核，没有扩大loader业务UPDATE授权。最终source仅准确前向更新该guard，28表已有业务值对照不变；没有重跑初始化或重seed。

target05完整恢复原306945字节包，实际4原件、94行、14组件，28表逐列codec、正文/关系对账后seal，31域可读，3项DML/退款返回42501，loader/admin登录及临时成员撤销。target06为独立负例集群，真实非空004/005、已有010/011角色及错profile拒绝；负例未作为恢复目标重用。部分初始化缺loader时原abandon会在撤loader失败后遗漏admin撤销，已修正按实际存在角色撤销，并对准确failed target06仅作必要清理，确认admin NOLOGIN/PASSWORD NULL。

target07默认respect_current_deletions：原包中后来删除的source ead33e27-3e1a-4d6f-9e91-8433af5a390b当前指针/HTTP正文不可回查，墓碑与共享原件保留。target08显式snapshot_only_readonly：旧包时点资料可回查，原source墓碑未撤，两目标都永久只读。目标意图01—03、failed04/06、sealed05/07/08均保留，不回收逻辑slot或倒改FAIL。

实际source同T快照期间另一连接正常提交替换，包内仍为T的旧指针/版本。共享删除、准确清理失败pending、同键retry不二改revision通过。D最终检查后/unlink前与B上传同hash的真实窗口、B先SH/D等EX两序及真正client退出后PG迟到COMMIT通过：D先时准确unlink后B重发布，B先时新增共享引用使旧impact失效，重新核对后明确确认并保F；迟到提交文件未被误删。取消确认unknown的注入边界不进入unlink，不冒该注入为真实PG取消成功。

原SUP实际执行有限加法工具，tool receipt succeeded/business_commit committed；真实Job active_processes=0、双EOF/原管理归属与最近结算正证据保留。无模型调用。真实注册服务收尾未结束时切换拒绝且draining持久；已有close lane完成后source frozen，selector提交generation1。提交后精确注入丢返回，GET原键及显式重复动作仍同generation1、不二次分配/切换。

真实只读HTTP七类保存记录可读，28源表普通app UPDATE拒绝，资料/活动/取消/教学/面试恶意POST被门拒绝，旧包下载hash相同。最终既有Chromium对只读工作区、类别回查、合成旧实例IDB/localStorage草稿独立下载、刷新仅GET通过。浏览器第一次因标签含option文本的精确匹配定位器超时，改定位器后复验，不改产品断言。目标/source均不可用后重新启动API，原jobs/包仍由Hub可查，业务读取503，不回退旧source。

二、修复和最终字节

本轮产品增量为config、deletions、maintenance、restore、schema/schema_checks、main、013和DataWorkspace九处；另四个既有fixture适配分段计时/渐进日志/冻结，新增十三个Python验证入口、两个浏览器mjs。C01最终登记217条：212当前源文件、4当前bundle、1旧bundle移除登记；14改、16增、186未变、1构建输出移除。全部pre原字节在continuation-01/pre，逐文件diff及当前原字节在final，不以累计Git HEAD作本卡基线。

除加载行锁和失败撤权外，定向修复三项闭包：缺失/坏定义的两teaching FK与两final-shape约束必须被指纹拒绝；明确snapshot_changed删除拒绝记failed并提示重新核对，不冒commit未知；只读模式先于已保留fence判拒，POST返回data_readonly而非maintenance_unconfirmed。selected target不可连时保留同Hub查询，关闭业务绑定并标target_observation_status=unknown，界面有明确不可用文案。

最终TypeScript检查、frontend-build-c01-03和Python入口检查退出0；build沿用原依赖，未安装/改锁，未重跑未变G11。bundle index-CJ8Yp7JQ.js为836315字节/SHA-256 f1ea32ccb110016757732742a7ca7a6c937e59b6f895bbf675e55bf8fbb73bb3，四文件hash见bundle.json。最终只读浏览器实际使用此bundle。旧首次dist pre缺失仍保留历史偏差，本轮pre bundle已保存。

证据导航全部位于唯一新目录D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-01/。

- [最终源字节/身份](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-01/final/manifest.json)、[逐文件变化](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-01/final/changes.json)、[最终bundle](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-01/final/bundle.json)。
- [批级真实结果索引](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-01/final/batch-result-index.json)、[原FAIL索引](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-01/final/failure-index.json)：链接对应batches内逐阶段JSON、失败栈、API日志、截图与请求线；as-run在同目录，每批精确原件保留。
- [资源准确停止](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-01/final/resources.json)、[端口](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-01/final/listeners.json)、[封存时账](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-01/final/budget-at-freeze.json)。实时唯一账仍implementation/control/receipt.json与events.jsonl，不另开总账。
- [正常目标加载原始对账](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-01/batches/c01-restore-1131663078000000/03c-loaded.json)、[角色撤销](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-01/batches/c01-restore-1131663078000000/07-sealed-roles.json)。
- [两序/迟到COMMIT/旧包删除](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-01/batches/c01-race-1134754921000000/result.json)、[策略对照](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-01/batches/c01-overlay-1139001578000000/result.json)。
- [真实SUP](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-01/batches/c01-integrate-1139419843000000/01-native-supervisor.json)、[selector丢回应](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-01/batches/c01-integrate-1139419843000000/03-selector-lost-response.json)、[最终HTTP/浏览器](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-01/batches/c01-integrate-1139729250000000/result.json)。
- [目标不可用仍可核原件](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-01/batches/c01-harden-1139975718000000/03-target-unavailable-HTTP.json)、[包内合成secret扫描](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-01/batches/c01-harden-1139975718000000/04-secret-scan.json)。不输出DSN、密码、Env、session token或DPAPI明文。

三、V01—V29实际矩阵

没有将核心方法通过扩大为每项全部子分支PASS。下列“已实测”只覆盖所列方法；未列分支仍未验证，旧充分证据按字节/影响继承。初始八项故意断尾scratch原件不重跑/清除。

V01 部分关闭。真实全28表/31安全域、PDF补充/正文/关系、标准工具解读、可携portable与checkpoint已发布；完整逐语义映射异常目录尚未全枚举。

V02 部分关闭。target05/07/08逐列codec/正文hash对账及HTTP七类别回查，模型/教学/面试/记忆/HTML事实保留；合法旧received无正文的专门负例输出仍不足。

V03 部分关闭。同一真实RR T中，另一连接正常替换，spool保旧指针/版本，未拼T；scope/outcome/最近settle/墓碑各变体及断开连接整次失败尚未完整运行。

V04 部分关闭。跨进程稳定RootLease沿用；真实D最后窗口/B等待、B先SH/D等待、同hash重发布、client实际退出而PG仍迟到COMMIT与文件保留通过。替换/PDF候选/直接元数据/target发布各并发分支尚未全组合；取消unknown为明确故障注入边界，非真实丢取消COMMIT回包。

V05 部分关闭。三PDF状态、逐页supplement在真实target加载逐列不变，HTTP记录可读；pending学习资格与删除覆盖各PDF回查专门组合尚未全部实测。

V06 主要方法关闭。新独立target05完整001—013、4原件/94行/14组件、28域逐列关系/hash对账、31安全域只读真实读/拒写，最终target07实际HTTP可回查；source/旧包保留。

V07 主要方法关闭。原非空source前向改guard保28表值；独立target06实际非空004/005与已有010/011role、错误profile拒绝；source实际缺/坏特定约束拒绝。列/编码/所有错误函数反例未完整枚举。

V08 部分关闭。九加载guard包含旧目标/历史命令/作答/memory/HTML和非零账，在真实完整加载对账中通过，两teaching FK实际DEFERRABLE INITIALLY IMMEDIATE；普通online逐九分支的精确反例仍不全。

V09 部分关闭。source snapshot四个42501独立落盘、source SET不能自授loading、sealed撤loader/admin、31域读/三项DML退款42501及最终HTTP拒写通过；所有伪mode/SET和旧退款变体未全枚举。

V10 部分关闭。28表逐列对账保四账/代次/UNKNOWN，readonly不认领/折叠/退款；另有真实有限工具与原结算证明。完整四账达限各分支和旧received缺正文专例仍有缺口。

V11 部分关闭。failed_unstarted两条/cleanup_unconfirmed/R60/starts3在所有目标保真，控制占位明示，不复活source旧CID。stopped历史样本与伪StopProof各反例未运行，不取证旧25。

V12 部分关闭。源新增正常有限工具与最新账旁证保留，旧target显示原时点不覆盖source；专门备份后增长/unknown两副本逐字段异常矩阵仍不完整。

V13 部分关闭。历史目标/答案/记忆依赖和revoked通过加载/HTTP投影；旧scope/cancelled/dispatch_closed与资格函数全组合专例仍缺。

V14 主要方法关闭。共享hash删一条保另一条、墓碑后回查失效、物理故障pending、明确原键重试修订只加一次；old包/WAL/无关目录未删。真实预览影响停止分支没有新preview消费。

V15 部分关闭。源revoke既有样本、revoked body打包排除与target缺省通过，未重写M3，未purged不冒done；M3 pending/done专门恢复覆盖组合仍缺。

V16 主要方法关闭。备份内真正存在source后来删除，target07默认遮蔽/HTTP404、target08显式快照可回查、原墓碑不撤。memory备份后新撤销及未知最新删除的全部用户确认组合仍不足。

V17 部分关闭。旧四package方法继承，C01真实坏ZIP/截断/错字节/缺省结构/秘密metadata即使重算hash仍拒绝；逐原件/CRC/合法missing异常尚未全运行。

V18 部分关闭。真实文件路径、绝对/UNC/ADS/重名/链接entry/压缩/嵌套/EOCD目录超界等拒绝，哨兵和旧包不变。实际Windows文件symlink若host权限不足，在input结果明确not_run；不冒全部reparse/发布窗口通过。

V19 仍未完整。实际低限members2、rows1、chunk_bytes10及目录8MiB拒绝；全部恰好上限/超一、组件时间/容量、用户cancel/中断上传及不干扰其他工作未运行。

V20 仍未完整。正常真实publish/fsync和独立Hub published收据、旧键GET/download只读成立；spool/copy/fsync/no-replace/DB四处故障、半发布补收据而不复制全部分支未运行。

V21 部分关闭。target04加载中SQL42501失败并保留，source/旧包不变，failed04/06不作为恢复重用；目标组件崩溃/文件损坏/取消的专门分支未完整执行。

V22 主要方法关闭。真实owned未结束拒切，draining不自动解除，已有close lane完成，source frozen/target readonly/Hubgeneration1一致；selector已提交丢返回GET同generation，重复不二切，会话/绑定切换，源保留。全部selector失败位置/受信解围分支仍缺。

V23 部分关闭。DPAPI/ACL历史正证据继承，source合成密码/maintenance值对全部实际包扫描零命中，普通日志/DTO不dump秘密；完整marker在全部HTTP/日志载体扫描仍不足。

V24 部分关闭。真实TCP旧键/GET不写、包下载、readonly POST拒绝、selector丢回应同代次、两最终浏览器刷新GET-only。普通导出/恢复/删除真实HTTP丢回应、同key异hash和切换晚到全流尚未全运行。

V25 主要方法关闭。真实合成localStorage与旧实例IDB草稿单独下载，submitted=false/不授执行，页面刷新不POST，服务器包声明不含浏览器草稿；同一活页面编辑身份跨切换的完整晚到场景仍缺。

V26 部分关闭。pre/as-run/post、最终source/bundle、方法原日志/SQLSTATE、准确停止/端口、失败和累计计数已封存。本卡不独审，Must异常缺口未全消除，不能建议全部STEP017通过。

V27 部分关闭。真实同T31域及三metadata、snapshot拒秘密/DML/删除EXEC、target新控制/受限load/seal、readonly读/撤权通过；T前后墓碑/操作观察全组合不完整。

V28 主要方法关闭。source停/target选中但不可用时真实HTTP仍GET旧jobs/包，业务503不回退；新scratch真实坏cache、断尾只读前缀/阻新写、中段坏失败关闭，selector丢回应不二增。target半注册各故障位置仍缺。

V29 部分关闭。全部28源表普通app冻结拒写、实际新SUP与registered close lane、readonly多领域POST门、Hub/source/target一致和不可用无fallback通过。每一内部producer/后台清理/preview出站失效分支、模式unknown与全UI旧draft晚到仍未全测。永久只读不等于全NFR005持续执行恢复。

四、尝试、投入、停止门和保留状态

C01八个有限合并根为restore/source/http-unavailable/race/fault/overlay/integrate/harden，各含有界的既定方法和普通修正，真实退出/FAIL不换根清计数。旧raw7目录错误、主控前向保守基线10及旧全部事件均保留。现累计real_roots18/18，全部新根ended；因此停止新真实消费者。剩余时间不能替代根许可。

封存UTC2026-10-13T05:19:34.545809Z时：活动9185.438/21600秒（最终报告保存段另据实封口）、offline51.238/7200秒、真实持有377.280/10800秒/业务门9600秒。旧44.052离线、68.655持有和55525.796旧墙时历史均继承，不倒改为净投入。暂停记录none，无记录中断均计活动。只有资源准确Running到Stopped（含保守启动/停止等待）计持有。

累计PG create6/12、物理成功6/9、start27/32；Windows11/12、API5/8、Browser3/6、build3/6；Vite/preview0。费用/provider/public业务新增0。逻辑slot01—08均占，01—03无CID意图保留，实际source+04/05/06/07/08共六对象；额度余额不授新slot/新root或failed重用。当前所有容器Running=false/Pid0，本卡18114/15114/55461—55469无监听，API/browser/child/SUP准确结束。Chromium主PID退出/实际browser.close与parent双EOF有原记录；没有将普通PID检查冒新增preview StopProof。

source持久mode=frozen；选中target07，selection generation=1，target07当前Stopped，这是保存的只读选择，不是回源normal。targets/卷、旧/新包、spool/incoming、坏输入、坏scratch journal、DPAPI和全部FAIL保留，无DROP/REMOVE/prune/Git写/递归删除。

错误历史除旧FAIL外，保留C01内存门、55461权限拒绝（主控后解除）、source首次Docker启动拒绝、包装器dist旧asset缺失（改freeze登记移除/捕获新bundle）、线程名误判及旧impact失效的fixture问题、readonly POST错误码顺序及browser定位超时。每个真正影响分支修正后定向复验，原FAIL未涂改。当前managed权限访问Docker需要升级工具，自动审查已允许对应卡面范围动作；没有自动审查拒绝或额外用户技术采用。

五、待主控处理与下一步

本轮保存的是较前轮明显推进的候选和主要真实闭环，但尚不足以把V01—29全部签PASS。优先补V19/V20完整容量/取消/半发布故障、V03全并发/断线、V04剩余引用类别、V08/09越权细分、V11/15/16历史/记忆分支、V24/25晚到与HTTP丢回应。新真实根已无余额；所有逻辑slot都占，source现frozen/selector已只读。主控须明确续作额度与可复用已sealed对象/测试状态边界，不能由执行者自动解围、回收slot或新建资源绕过。

本窗口不改DocuS/CHG，不占TASK115/R109，不代独立审计。主控同步唯一总账、实际source frozen/selector与资源、九产品增量、18/18停止及矩阵缺口后决定下一步。原需求Must/G11有限关闭、旧unknown25/R60/count1/13元/626.566不改；不宣STEP018—020/M-1/发布/项目完成，不把永久只读替代完整NFR005。

下列为原结果全文原字节后缀；其中旧“target未创建”等状态是前轮历史，不与上述续作当前事实拼成新状态。

# TASK-114 / R-108 执行结果与停止门交回

主体源码、迁移、配置和工作区候选已形成，非空 source 升级及合成快照打包已有部分真实证据；隔离恢复、删除竞态、源停线与浏览器验证尚未完成，原 28800 秒总窗口已到停止门，建议保持“未完成实施候选”，不得签完整通过。

一、接收身份、范围和本次断点

实际根目录 D:/shspic/project_NO3_RetroLume-agent，接收 Agent 为本工程窗口 Codex；A+ 是资源安排标签，不冒充可核的精确模型子型号。执行沿用 TASK114/R108/STEP017、父 TASK113/R107，task_model、V4.0、公共 AGENTS CHG-0003。未派子 Agent，未接管 TASK112 审计窗口。

采用依据为 [TASK-114-work-decision.md](D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-114-work-decision.md) 与 [当前 A—D 合同](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-113/design/revision-01/current-contract.md)。完整技术采用保持有效；本次没有用户库、真实资料、真实 provider 或新增费用授权。

2026-10-13 恢复时先核中断结果。source 准确 CID 仍为 exited/Running=false；本卡端口无监听。上次 target 验证实际进入工厂，但在创建前第二次内存检查处失败，没有 target create/start/SQL。没有正在运行的本卡产品消费者需要继续等候或强杀。

总窗由实际首工具接收锚点计，不因换窗、中断或等待内存重置。原锚点 UTC 2026-10-12T08:31:24.422001+00:00、monotonic_ns=1065347750000000。业务停止门为北京时间 2026-10-13 00:11:24.422001，总停止门为 00:31:24.422001。2026-10-13 07:56:51 的封存观察累计 55525.796 秒单调时间；已超过 28800 秒。恢复后的操作仅为准确资源观察、既有证据读回、原件封存和必要结果交回，没有新测试、build、SQL、API、浏览器或容器启动。中断期间的墙时纳入窗口；未逐段记录的净活跃人工投入为 unknown，不能用墙时冒充净投入。

停止依据直接来自 [TASK-114 卡面](D:/shspic/project_NO3_RetroLume-agent/DocuN/tasks/TASK-114.md)：“从实际首工具UTC/monotonic接收起，本卡总前向工作窗口28800秒”，及“总窗口同样提前预留1200秒清场时间，禁止新消费者”。现有“继续未完成任务、沿用目标与约束”没有追加时间额度。后续实施需要主控在原 TASK114/R108、原锚点和计数上给出明确续作时间授权，无须重复批准技术包。

二、可审证据入口

- [接收、计数和资源原账](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/control/receipt.json)：原字节未被本次恢复改写。
- [原事件和命令账](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/control/events.jsonl)：离线命令参数/退出码/时间及真实资源失败、开始和准确停止观察。
- [逐文件差异索引](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/closure-20261013/change-index.json)：只比较本卡接收基线，不比较累计 Git HEAD。
- [最终源码原字节及 hash](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/closure-20261013/final-source-manifest.json)：对应 final-source 子目录，差异在同级 diff 子目录。
- [批级 as-run 与最终字节对应](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/closure-20261013/as-run-to-final.json)：用于判定哪些旧通过可继承，不能将封存标签当被测标签。
- [最终 bundle 原字节及 hash](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/closure-20261013/final-bundle-manifest.json)：对应 final-bundle 子目录；没有浏览器通过声明。
- [实时资源白名单观察](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/closure-20261013/resources-observed.json)、[窗口停止事实](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/closure-20261013/stop-boundary.json)、[计账缺口说明](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/closure-20261013/budget-reconciliation-note.json)。
- [现存 Hub 的只读观察](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/closure-20261013/hub-readonly-observation.json)：标准库读原 frame/hash/COMMIT 链，不调用产品构造器、不解密凭据、不写 journal。
- [现存完整包身份](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/closure-20261013/package-identities.json)、[三控制载体身份](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/closure-20261013/package-metadata-observation.json)。

三、实际源码差异及作用

接收前保存 145 个既有文件的原字节及 hash；最终封存 197 个源文件，38 个既有文件修改、52 个本卡新增、107 个既有文件未变。所有原件副本与接收登记 hash 相符。001—012 零修改；没有依赖安装、锁文件改动或 Git 写操作。新增文件在批级 manifest 以 before_exists=false 登记；最终清单同时明确原始 scoped inventory 不覆盖的测试、配置等路径，不反造不存在的 pre 字节。

新增 backend/app/data_exit 的 17 个生产模块，实现固定合同/codec、磁盘 spool、同连接快照、包发布/读取、私有 ControlHub/DPAPI、ReferencePin、恢复工厂、维护围栏、资料删除和 HTTP 入口。新增 [013_data_exit.sql](D:/shspic/project_NO3_RetroLume-agent/backend/migrations/013_data_exit.sql)、[配置样例](D:/shspic/project_NO3_RetroLume-agent/config/data-exit.example.json)、[维护 CLI](D:/shspic/project_NO3_RetroLume-agent/deploy/data_restore.py)，配置样例默认 disabled。

013 定义三控制表、四 NOLOGIN 角色、固定安全投影、九受信历史加载 guard、两指定 teaching FK 延迟约束及运行写围栏。source 无 loader 成员，loading 分支绑定实际 SESSION_USER/目标状态。源引用 ticket/epoch 在 PG 中持久化，RootLease 固定文件对象采用 Windows LockFileEx 跨线程/进程锁；原件 put、同 hash 复用、资料/PDF 元数据提交均接 live pin。代码提供先独立确认取消旧 ticket、再新 READ COMMITTED 检查全部保留引用、共同排他下准确 unlink 的路径；关键并发仍待真实验证。

快照代码用专用非超级 snapshot 登录和单个 REPEATABLE READ READ ONLY 事务，读 28 业务域及 3 安全控制投影，spool 有界，RootLease 共享延续至原件复制结束。包采用 ZIP_STORED、data_exit.v1.r01，记录和 checkpoint 同字节；独立正文、关系、原件、README 与无自引用 root hash，拒绝包内路径/SQL/权限/资源指令。ControlHub 以完整 COMMIT frame、顺序/hash 链、flush/fsync 为长期 job/selector 权威，GET/reconcile 不启动动作。

恢复候选提供可信 host profile 的新独立 cluster 工厂、001—013 初始化、受限 load、加载对账、seal 撤 loader/admin 登录和 readonly 登录探针、只读选择。源码有受控原件加载、控制占位变换、archive_history、默认当前删除覆盖及显式 snapshot_only_readonly 路径。这些生产路径已经写入，尚未在 target 真值上执行完毕。

既有 backend 定向接线覆盖 main、OriginalStore、materials/PDF、activity/learning/interview/memory 仓储和服务、worker 与 preview 管理。MutationPermit 绑定 control/generation/dataset/instance；新增 live source 模式检查和持久维护准入门，spawn 前登记自有资源，原 ClosingCallGate/SUP/preview 停止链用于既有工作收尾。没有以日志中的旧 owner/CID/PID 恢复执行权；原预算、退款和停止证明核心未作为新功能重写，但围栏增量必须完成定向验证。

资料删除候选提供影响预览、impact hash/revision 锁内复核、墓碑 current_version=NULL/revision+1、共享 hash 保留、准确文件清理 pending/unknown 及同业务键明确重试。memory 沿既有 revoke/M3，只补墓碑观察、写门和恢复 mask，未声明 purge 已完成。

新增 frontend/src/data 六个文件，挂载“数据与备份”，提供范围预览、可携导出/备份、上传 hash、恢复计划/验证/只读选择、资料删除影响确认与清理重试、只读记录和草稿说明。main、PDF 面板、各业务 API/意图模块接 dataset/instance/generation namespace、caps 和迟到响应检查；选择更新时刷新会话/编辑身份。用户界面不以 TASK/role/表名作为操作流程。

README、start_local 和 .gitignore 仅补配置、安全启动/维护说明与私密 runtime 忽略规则；没有自动迁移现有用户库、自动备份或默认后台安装。全量 38/52 文件名及原字节 diff 以差异索引为准。

四、最终身份与版本对应

013 最终 64872 字节，SHA-256 15074997652bae1e66e2f7237a7e68d98e2164f5e148460d900adfe374520e4f。schema.py 最终 43592 字节，SHA-256 cb1d30a26154402775cf50f24dead1e89d26b590219c79d96b3c0e09cfb35fd5。preview schema-fingerprint.json 最终 SHA-256 11265108b26ef6242012c8d03841c74d736ef0099bd7c40e4696f1d470aa250d。

最终 197 源文件与 target-saved-1089363562000000 的 as-run 全部相同；与 source-forward-1088469781000000 的 as-run 相同，唯一该批缺失文件是其后新增的 verify_saved.py 测试入口。因此最后 source 前缀观察绑定的是最终产品字节，但不延伸到该批未到达的恢复/HTTP/UI 分支。

最终 bundle 共 4 文件。index-DcQS7jxH.js 为 836151 字节，SHA-256 0b884db3eb928d8581066c78ee630e1a9015c99ddccd6e1793996cae01ea8174；CSS、index.html、PDF worker 的精确 hash 在 bundle manifest。frontend-build-02 退出 0，保留动态 import 与大 chunk 警告，未顺手更改性能/依赖配置。首次 build 之前的 dist 原字节未留副本，这是证据偏差；不从 HEAD 构造或追认 pre bundle。最终 bundle 原字节已保留，真实浏览器仍 not_run。

封存时原需求、最终需求、架构/执行动态、根 AGENTS、采用材料、TASK113 原结果/当前合同及七锁定公共指纹均与输入登记相同。见 [锁定输入复核](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/closure-20261013/locked-inputs-observed.json)。公共库与 DocuS 均未写入。

五、真实 source、迁移和现存包

source 名 retrolume-task-114-data-source，CID 2659f71b56015c0de1be5a3d5790a47e0362139bbbaae45ad3a45bf562706c22，卷 retrolume-task-114-data-source-data，端口 127.0.0.1:55461，完整 image ID sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f。实际 PG server_version_num=170011。检查结果绑定 name/image/label/volume/loopback、1 CPU/512 MiB/pids128/restart=no，未使用活动 tag。

先应用可信 001—012 并通过正常仓储生成非空资料/旧版本、活动范围/允许模型、旧/当前教学目标与命令，再应用当时的 013。28 表的已有业务值计数/hash 对照相同，见 [升级前业务值](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/control/source-012-before-013.json)、[升级保真](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/control/source-013-business-preservation.json)、[角色和 PG 身份](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/control/source-schema-role-identity.json)。

source 并非直接一次应用最终 013：后续准确比对旧函数 hash，前向更新 data_runtime_write_guard/data_control_frozen/data_mutation_enter，之后更新 data_material_reference_guard；每次独立 forward-result 或 result 保留 business_values_equal=true 和新 schema probe passed。最终四函数实际 hash 分别为 91dac86ea0de0c3f943160430d30777528df2ecdbfe8fa7802a0debd90ca6295、15c82d578ab33971a00de9237d5dc7eae34c50586361b55115f13a20a969335b、3df177409824ddf31122dcc3007754207a207f66e9ed797bbe030fbdd974c84d、ad71fc59e78275c58857b0fb009db8764eb6b662df25cb927399c081ea7bd0f4。原始记录见 [最终前向补丁结果](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/batches/source-forward-1088469781000000/forward-result.json)。最终 013 的新空集群一次初始化与九 guard/撤权真值尚未执行，不能用 source 前向修码替代。

实际 source fixture 含 28 个非空业务表：当前/旧资料、共享原件、pending/confirmed/skipped PDF 和真实逐页 supplement、教学/面试旧目标与修正、模型正文、memory 版本/依赖/选择与 revoked 墓碑、HTML artifact 和三条 preview 历史。fixture ID 见 [source-full-fixture.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/control/source-full-fixture.json)。HTML/preview 历史为合成数据库事实，没有真实 renderer/Native SUP 启动，不冒停止证明。包含 failed_unstarted 两条及 cleanup_unconfirmed 一条、starts=3/R=60/S=0；stopped 历史分支没有覆盖。早先失败已提交的合成前缀和额外活动均保留，未为整洁删掉原账。

实际发布完整 restore_checkpoint 737bf7ba-18c2-436c-a011-3aabbc1a8b2b，306945 字节，文件 SHA-256 45177d58ea58fcaa704bfdd48641aceade7ca6e6f4fe5d6759b3a46bf2671665，root SHA-256 312e673b22e0957217c74d116ed3de6d1b068a1124b1fc2939b11385f8be8d10。包内 77 个 ZIP member，manifest 列 76 个 content，28 records/checkpoint 域和 metadata/source_control.json、operation_history.jsonl、tombstones.jsonl 均存在。snapshot=832:832:，时间 UTC 2026-10-12T14:56:52.595155+00:00；manifest 声明 browser_drafts_included=false/runtime_authority_included=false。关闭时包仍存在，原 pending、incoming、副本 spool 和私有控制文件均未删除。

下载原件为 [现存 .rldata](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/synthetic/backup-root/packages/737bf7ba-18c2-436c-a011-3aabbc1a8b2b.rldata)。关闭时只是读既有包做身份清点，没有重跑产品包测试或把其 completion=complete 冒 TASK114 完整通过。

六、执行过的方法、退出码和证据边界

离线确实执行并有普通日志的通过项：初始控制/锁/输入 8 项，package 4 项，增量 spool/ClosingCallGate 2 项，FastAPI TestClient 2 项，前端增量 SHA-256 15 个 oracle 向量，最终 TypeScript noEmit、两次 Vite build、Python AST/必要入口导入。TestClient 是进程内测试且数据库替身，不是 18114 TCP 实测；spool 样本不是并发 PG 快照。容量负例实际用 members=2、chunk_bytes=10，不声称 2 GiB 吞吐或全上限矩阵。

RootLease 真实 Windows 子进程 PID49100、creation/birth=134362769271637543：共享获得、排他等待真实释放、稳定 lock 文件不能替换，子进程退出 0。见 [跨进程锁原观察](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/control/cross-process-lock-result.json)。这不是 PG 最后查询/unlink 窗口或迟到 COMMIT 验证。DPAPI 实际 roundtrip、明文不在密文、private ACL 设置成功见 [DPAPI 原观察](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/control/dpapi-result.json)，没有把测试凭据值输出到公开材料。

PG/文件最后成功前缀：source schema probe、全部 28 非空表检查、4 个 snapshot 权限负例要求 SQLSTATE42501、source app 无 loader 成员、同连接快照打包、独立 zipfile/json/hash 逐 content 解读、复制 incoming、prepare 和 restore job。之后工厂 before_create 内存检查失败，整批退出 1，整批状态为 failed，不能改成 passed。

该前缀由被冻结的 matrix_pg.py 顺序断言、实际 published 包/journal 与进入 allocate 的原失败栈互证。权限负例的返回数组和全部 source_rows 当时只暂存在 runner 内存，runner 仅在整批通过才写 result；失败后未单独落盘逐 SQL 查询结果。这是取证缺口，不能凭本文补造 raw SQLSTATE 日志。续作只需补对应精确权限/行值输出，复用 source 种子和包，不重建全部 fixture。

主要实际命令与结果如下；全部离线命令的准确参数、exit_code、seconds 在原 events.jsonl 和 [封存命令事件](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/closure-20261013/command-and-resource-events.json)，不以摘要替换原件。

- backend/.venv/Scripts/python.exe -X utf8 backend/tests/test_data_exit_offline.py：退出 0，子进程 0.485 秒，初始 8 项；该 scratch/offline-control 最后故意保留断尾，不自动重跑。
- 同 Python 的 test_data_exit_package.py：首批退出 1；最后 package-boundaries-04 退出 0，0.438 秒，4 项。
- 同 Python 的 test_data_exit_incremental.py：最后 offline-incremental-02 退出 0，1.110 秒，2 项。
- 同 Python 的 test_data_exit_api.py：最后 api-boundaries-03 退出 0，1.188 秒，2 项；保留 Starlette deprecation 警告，不安装依赖。
- node frontend/tests/task114-hash.mjs：初次退出 1、修正导入后退出 0，0.156 秒，15 向量。
- node frontend/node_modules/typescript/bin/tsc --noEmit --project frontend/tsconfig.json：frontend-types-07 退出 0，2.110 秒。
- node frontend/node_modules/vite/bin/vite.js build frontend --outDir dist：两次退出 0，最后 0.750 秒；build 次数 2。
- 同 Python 的 check_offline.py：最后 python-entries-06 退出 0，1.171 秒，只解析/导入，不连 PG/启服务。
- setup_source.py 的创建批 pg-source-init-01：创建成功后因启动前内存不足退出，未 start/SQL；原 CID 后由 pg-source-init-02 恢复，实际非空升级成功，未 recreate。
- forward_source.py 首批：准确前向补三函数、业务保真及 schema probe passed；其后 --matrix 合并批分别因 PDF guard、Provider 夹具枚举、HTML 指纹和内存失败，原 failure/result/forward-result 分别保留。
- 最后 source-forward-1088469781000000：四函数补丁与业务保真 passed；matrix 进入新 target allocate 前的内存门失败，退出 1。
- verify_saved.py：target-saved-1089363562000000，source 保持 stopped，使用现存计划，目标创建前内存再次不足，退出 1；未执行目标 DDL/load/seal。

七、失败与修复历史

早期生成器正则量词、CRLF 匹配、profile 条件括号、cmd 相对路径启动失败保留于 early-observations.json，未知逐进程时间按工具等待上界保守计 15 秒离线。TypeScript 改用现有 node 直接调用项目编译器；前端 hash 测试导入改用现有运行时支持，未安装新包。

package-boundaries-01 合法 README 因大小写 whitelist 校核被拒，修正后 02—04 通过。vault-01 在 Windows 对 rb 文件 fsync 失败，修正发布打开模式后 vault-02 通过。两者旧 FAIL 原文未改写。

pg-complete-03 在 PDF confirm 的 data_material_reference_guard 失败，仓储公开封装只给 DatabaseUnavailable，原 SQLSTATE 没有保留；根据表特定 NEW 字段的触发器分支修正为分表处理，准确前向补丁通过，之后 PDF confirm、supplement、memory/interview 数据成功保留。不能编造该首失败 SQLSTATE。

source-forward-1087242843000000 的产品补丁 passed，但夹具用不存在的 Provider.DEEPSEEK 失败；改为实际枚举 DEEPSEEK_CHAT_COMPLETIONS。复用已确认提交前缀，不重新导入/覆盖资料，不清原四账。

HTML 新增 013 后 fingerprint 两批返回 html_schema_not_ready。修正受信角色/owner/ACL 的投影，并保存实际 raw/normalized shape；仍失败的精确差异为新增两条 teaching FK constraint trigger 在 pg_constraint 中 type=t 的投影。最后按具体名称、表、类型、验证与定义筛掉这两条新增项，旧约束继续核验，最终实际 HTML artifact/preview 历史及完整包成功形成。两次相同公开错误码的原件、修正中间字节和差异仍保留，集中审计需核因果及“同因修正两次仍失败”停止门，不能只见末次产物即抹去早期失败。

最后两次目标分配前的内存检查失败，不是 restore/load 已通过，也没有用新容器/slot 绕过启动门。每次内存采样和判断留在 control 中以 memory-before- 开头的 JSON；用户此前答复“稍后释放内存”，本窗口未关闭用户软件或重启 daemon。

八、V01—V29 真实矩阵

以下使用“部分观察”或“not_run”。没有任何完整 V 项用 build/mock/单样本代签 PASS。以当前 A—D 合同 D1 原子分支为基准，未出现的分支均仍未验证。

V01 部分观察。实际 28 非空表闭包、旧/当前资料、PDF、补充、作答/模型/HTML/记忆形成 306945 字节包，最后 PG 前缀执行标准库 JSON/ZIP/hash 解读。包与逐表行数可独立读取。尚缺完整原件/语义映射逐项输出与可携 export 模式实测；当前实际产物为 restore_checkpoint，不冒两种模式均通过。

V02 部分观察。包有 teaching、interview 修正、model body、memory 两版本/选择、HTML artifact 及合法 unknown；revoked body 有缺省原因。尚未形成逐类源/导出原正文 hash 和旧 received 无正文反例的完整原始对照。

V03 部分观察。真实单连接同 T 捕获 28+3，manifest snapshot=832:832:。T 前后两连接的替换/scope/outcome/settle 并发，以及断开不能拼新 T，not_run。

V04 部分观察。真实 RootLease 跨线程/进程、稳定文件不可替换有日志。D 最后查询后到 unlink 前、B/D 两序、同 hash/替换/PDF/直接元数据/目标发布、COMMIT 丢回包、进程死 PG 迟到、epoch 取消未知等关键 PG/文件竞态全部 not_run，不能只凭锁测试通过。

V05 部分观察。实际三 PDF 状态和六 extracted pages、两 review pages、两独立 supplement 已在 source/包中。target 恢复后资格、删除覆盖和 pending 不误授学习，not_run。

V06 not_run。两个 target 意图登记后都在 create 前失败；没有新 cluster 初始化/加载、逐列/关系/原件对账或 readonly TCP 回查。

V07 部分观察。真实合法非空 source 001—012→013 保旧业务值。独立 fault target 的非空004/005、已有010/011 role、错误 schema/codec/profile 拒绝，not_run。

V08 not_run。旧目标、历史命令/作答、memory、HTML、非零账样本已准备；九历史 loading guard、两 FK 循环加载、普通角色越权拒绝和不可变 UPDATE/DELETE 需真实 target。

V09 部分观察。最后 source 前缀执行 app 无 loader、snapshot DML/秘密/删除 EXEC 负例；缺单独 SQLSTATE 结果文件。loading 自授模式/SET、sealed readonly DML/退款拒绝及撤 loader 真值，not_run。

V10 部分观察。实际包保留请求/预算/结果、代次、unknown 和 preview R60，未调用旧认领/结算/退款。完整四账逐字段源/target 对照和合法旧 received 无正文，not_run。

V11 部分观察。三条合成 preview 历史中 failed_unstarted/cleanup_unconfirmed、starts=3/R60 已入包。stopped 样本、真实 restore 变换、伪 StopProof/CID/PID/owner 不授权反例，not_run；没有重跑旧25。

V12 not_run。备份后 source 新消耗/unknown 与旧备份验证的双副本完整对照尚无；source 最新账未用旧包覆盖，但这不能替代所需前后实验。

V13 部分观察。源/包有旧目标、scope、答案/记忆依赖、revoked 及历史状态，候选 readonly DTO 有 mask。恢复后真实当前资格和删除覆盖 DTO 核对，not_run。

V14 not_run。共享 hash source 已有样本；尚未真实墓碑提交、历史/PDF 回查失效、共享保留、准确 unlink 故障 pending 与原业务键 retry 不二改 revision。

V15 部分观察。正常 revoke 路径产生 revoked memory 墓碑，包正文缺省说明存在；原 M3 算法未重写。purge pending/done、旧选择闭包、restore mask 和物理清理状态完整矩阵未执行，不冒 purge done。

V16 not_run。准备代码支持 respect_current_deletions 默认和明确 snapshot_only_readonly；尚未真实备份后 source/memory 删除与两种恢复策略，源墓碑/unknown 最新删除账的前后对照缺失。

V17 部分观察。真实合成 ZIP 文件的截断、错字节/缺 member、未知 metadata、完整合法包拒/收有 package-boundaries-04 日志。CRC/manifest/row/原件各种长度与合法 missing 的完整子分支未穷尽，未进入真实失败 target。

V18 部分观察。合成文件 reader 对 traversal、大小写冲突、额外项、deflate 拒绝有日志。真实发布边界外零写、UNC/ADS/reparse/link、巨大 EOCD/嵌套包等全部路径子分支尚未完成；ZIP reader 单测不冒真实恢复发布通过。

V19 部分观察。实际低值 members=2 与 spool chunk_bytes=10 拒绝；其他全部“恰好上限/超一”、组件/时间、用户 cancel/上传中断及不影响其他工作，not_run。不声称 2 GiB 吞吐。

V20 部分观察。实际完整文件和 Hub published 收据各自存在，Windows publish/fsync 正常路径有执行。spool/copy/fsync/no-replace/DB 四处故障、半发布/丢响应补准确收据而不复制的完整真实矩阵，not_run；现存 pending 保留。

V21 not_run。没有目标组件已载后崩溃/拒绝/损坏，因为 target 未 create。source 与旧包仍保留，但不替代真实失败封存目标实验。

V22 not_run。现存 Hub 无 selector_commit、无 maintenance.fence。verified 前拒激活、真实 owned stop/unknown、source frozen、选择失败/成功、会话变化、所有旧动作拒绝及不自动解围，未实测。

V23 部分观察。实际 DPAPI roundtrip/明文不在密文/private ACL、包不带 runtime authority 和控制投影缺秘密有证据；没有解密公开输出。合成 secret marker 对完整实际包/HTTP响应/日志的系统扫描尚未做，不能声明全链零泄漏已验证。

V24 部分观察。ControlHub 单测同键/hash 冲突、只读查询、selector 响应丢失同 generation；TestClient 认证/GET 不写 journal、readonly/旧 context 拒绝；前端类型/build/hash 通过。真实 TCP 丢响应、刷新只 GET、切换后晚到/旧 intent 全用户流，not_run。

V25 not_run。UI 和包声明未包含未提交浏览器草稿，提供独立草稿下载代码；真实合成 IDB/localStorage 下载、实例切换隔离、不自动 POST，没有浏览器证据。

V26 部分观察。pre/as-run/post、最终 source/bundle、包、源角色/DDL修正、精确 stopped 和端口、原失败/计数都已封存。target/HTTP/UI/截图缺失，真实批次根登记口径缺陷与首次 dist pre 缺失未解除，集中独审尚未派出；不能建议完整 STEP017 通过。

V27 部分观察。实际 snapshot 28 业务+三控制安全投影同 T、4 个 snapshot 权限拒绝前缀；包三 metadata 载体分别 source_control 1 对象、operation_history 6 行、tombstones 1 行。T 前后墓碑/操作变化、target 新控制身份/受限 load/seal/readonly 安全 view 和撤权实际验证，not_run。

V28 部分观察。初始真实文件 ControlHub 8 单测包含坏 cache 无权、未确认断尾只读前缀/阻写、丢 selector 响应同 generation；source stopped 时 verify_saved 入口能读取原已保存 plan/job，但未完成目标。封存原 Hub 19 个完整 frame/hash/COMMIT，未确认尾=false，6 jobs（1 published、2 failed restore、3 prepared），两个 allocating 无 CID 意图。真实跨选择 GET 旧 key/包/旁证、target 半注册故障和中段坏完整产品路径，not_run。

V29 部分观察。源码在公开/内部写、引用、admit/dispatch、preview/后台清理加 gate；TestClient 和 ClosingCallGate 只验证有限拒写/既有收尾。真实 PG 冻结跨所有入口、准确自有 SUP/preview 原证明、失效 fence/未知模式、Hub/source/target 一致及永久 readonly 全场景，not_run。没有新付费/工具/预览/持续学习恢复授权，不签完整 NFR005。

九、尝试、投入、资源余额和账缺口

原 receipt 计数：PG create 1/12，成功对象 1/9，start 7/32；preview create/start 0/2；API 0/8、Vite 0/8、Browser 0/6；Windows 子进程 1/12；frontend build 2/6。容器同时 Running 观察上限 1，本卡许可上限 2。商业费用新增 0、真实 provider 调用 0；合成 SQL 模型正文不算真实 provider 请求。没有公网/provider 业务，localhost 只用本卡固定 PG 端口。

离线累计 44.052/7200 秒，含早期保守 15 秒。真实资源登记持有合计 68.655/10800 秒，其中 source 七段 68.421 秒、Windows 锁 child 0.234 秒。开始记录在 docker start 前，包含启动/停止等待，属保守上界；没有把检查源码或等内存的 stopped 时间计作 Running。source 成功 create 登记到首次 start 登记准备时长 1158.657 秒，单列准备，不误记 Running=0 的未知开始。

各独立数字的名义余量为 PG create 11、成功对象8、start25、preview各2、API/Vite各8、Browser6、Windows11、build4；离线7155.948秒、真实总持有10731.345秒、真实业务持有9531.345秒。它们不是恢复许可：总窗口已过期，不能靠子额度余量继续。

原 real_roots=7/12 有实际登记口径缺陷。prepare_offline.py 在创建四工作根、scratch、sentinel 和 offline-control 七个目录时占此计数；source 的每个真实生命周期批次没有另 reserve 根。不能将“7/12、余额5”当作真实批次合规结论。可由原件重建的 PG 资源批次为 pg-source-init-01（实际 create，仅启动门失败）、pg-source-init-02、五个 source-forward 批、pg-complete-03，共8个；另有真实 Windows 锁子进程批次1个；target-saved 是实际恢复校核但 create/start/target SQL 前失败，另列事实。离线文件/控制/DPAPI 方法的根口径须由主控核正。原计数不被追返清零，也不能为后续临时换根扩额。这是本轮已知 runner 账缺陷，续作先作最小修正和据实补账，再启动消费者。

真实 PG 持有七段分别 8.515、7.500、8.516、12.312、8.812、9.219、13.547 秒，每段 end 有准确 CID/Running=false 观察；最后停止 UTC 2026-10-12T14:56:56.235719+00:00。原事件和封存副本可重建，不因中断改写失败次数。离线子进程 argv/exit_code 已逐命令留原事件；部分真实 PG 入口未单独保存完整启动 argv/终端输出，只能由入口/as-run、batch 结果、失败栈与资源事件重建，这是另一取证缺口，不称每条真实命令均有独立原始 shell 日志。

十、精确清场与保留状态

source stopped，关闭观察核 CID/image/name/job label/named volume 与原登记匹配，512MiB/1CPU/pids128/restart=no；Docker 对本卡9个固定 PG 名字和卷清点仅见 source 对象及其卷。18114/15114/55461—55469 无监听。没有 API/Vite/浏览器/真实业务 Native SUP/preview 在途。锁子进程已有真实 exit0/process_ended 记录，不全局 kill 或凭 PID 再杀旧进程。

target01 意图 e210c2de-34af-49f8-8578-89b8392bac30、job5106c014-446c-4492-840e-85b2fdb9fadb；target02 意图0734c636-fab4-477b-8a61-56beea44c229、jobc6d95b83-6175-431b-a82b-6ec43d18e434。两 restore job 为 failed，两个 intent 仍 allocating、无 CID；未分配容器/卷，不自行删 journal 或重用 slot。三个 prepared checkpoint job 仍保留，需按准确原键区分早先未发布前缀，不能冒已完成。

selector_commit 与维护 fence 未实际提交，source 仍是 normal 的持久数据库事实；“容器 stopped”不冒 source frozen 业务状态。source/全部合成根、包/pending/spool/incoming、控制 journal/DPAPI 及失败材料保留；不 DROP/REMOVE/prune/递归删除或停止其他任务对象。

十一、未完成、风险和可直接续作的最小顺序

1. 主控补明确前向时间许可，保 TASK114/R108、当前计数、所有失败和旧投入；核正真实批次根口径，修复 source runner 每真实批次登记，检查可用内存满足启动门。无需用户密钥、真实库或重复批准设计。
2. 复用现有 source/28表 fixture/完整包/plan。不要重新运行 initial offline-control（故意断尾），不要重新导入合法 source 前缀，不要 recreate source。已有 target01/02 意图保持；下一新目标与负例目标先按原合同/当前账确认 slot，不能用内存失败当理由任意换名或清空计数。
3. 最先跑新目标的最终001—013、九guard/two FK、完整load/原件/31域对账、seal真实readonly/拒DML与退款；同时补原缺单独的 source 权限/逐表观测。失败保原 target，准确 finally。
4. 完成真实 T 竞态、ReferencePin/PG 最后查询/unlink、迟到COMMIT/未知取消、资料删除/共享保留/pending同键retry、M3/旧包删除覆盖、四账与preview各历史反例。
5. 同最终字节接18114 HTTP和已有浏览器，完成ControlHub不可连/半发布、全应用维护围栏、自有SUP/preview精确原证明、selector/只读绑定、刷新/晚到/draft/恶意POST。只在新增围栏确实影响真实预览收尾时消费许可preview，不重跑未变G11全矩阵。
6. 只修失败/字节变化影响的分支，复用未变静态/包/锁观察；完成原29项必要分支后再形成稳定完整审计输入。当前候选不足以直接发“完整独审已就绪”。

核心剩余风险是工厂真实受限加载/撤权、文件与PG迟到提交竞态、全部写入口围栏的闭包、source frozen与selector/readonly绑定，以及最终HTTP/UI。编译、包存在或单测通过都不消除这些门。

十二、正式文档、历史与交回

DocuS 唯一共享状态未被本执行者改写。当前正式执行动态仍为 v2.47 的原登记，本轮真实 source、候选差异、未完成矩阵、窗口停止和根口径缺陷由主控同步；需求v1.2/架构v1.25与用户原始需求原文不改。新功能配置/README和仅候选的经验线索交主控决定，不写公共经验库。

TASK113/R107 设计已验收，当前原件指纹保持。旧TASK111/112、G11有限关闭、unknown25/R60/count1、旧13元/626.566以及全部原失败/预算不变，本轮没有取证旧25或复活旧runner。

本窗口未独立自审或代主控签验收。TASK115/R109 仅是卡面计划，未自行占号、发卡或创建新窗口。候选永久只读不等于全部 NFR005/恢复后继续学习，未签 STEP018—020、M-1、发布或项目完成。

本结果为真实保存的实施断点交回，配套源字节和普通证据已封存；后续只需要主控补续作时间及计账口径，不再询问已采用技术选择。
