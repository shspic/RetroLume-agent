# TASK-118 / R-112 — STEP018合成集成候选集中独立审计

## 目标、交付及独立窗口

你是本卡独立审计执行者，集中审查TASK117/R111从S01到S06的完整实际增量及可继承证据，交付代码、证据、执行控制三个轴的独立结论，并列清真实供应商Q的剩余启用门。此次不实施修复、不重复运行已成功业务，不签STEP018整体、Q、M-1或项目发布通过。

接收A+增强资源，新建真正隔离的审计会话；不得使用TASK117实施窗口或继承其聊天/推理。实际客户端/模型如实登记，不因既有成果模型标签不同要求重做。理由：新Embedding类型/跨provider总账/SQL权限/记忆失效/恢复codec/只读切换及停止证明同时受影响，必须在完整候选稳定后一次集中审计。原TASK117工程窗口保持停止；本卡源代码、迁移、前端资产、原证据及账只读，无并行写入。

主控只完成前置核证，不预设你的审计结论。发现确定缺陷给出触发、影响、定位与最小修正，交主控合并派回原工程窗；不直接修、不把每个非阻断观察都变新门，不逐普通修正另起全面审计。

结果保存 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-118-result.md；新证据/有限脚本只写 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/audit/。一次形成可裁定成果，覆盖达到即停。主控共享状态与最终验收仍由主控维护。

## 项目、规则与授权

根 D:/shspic/project_NO3_RetroLume-agent；入口 D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。task_model/V4.0、公共AGENTS CHG-0003、阶段07；需求v1.3、架构v1.40、执行动态v2.67。公共只读根 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4；锁定七项身份在 DocuN/evidence/v4-migration-20260930/rules-snapshot.json，不自动采用后来版本。

新窗先读入口、锁定公共AGENTS、本卡；公共WORK只读独审/证据/权限相关章节及TASK_TEMPLATE结果要求，不读其它模式替代当前。遵循WORK第2章task_model、第6章适用协作合同及07开发循环的稳定成果独审/三轴判定要求。主控已读未变的材料可作为路径映射，但审计源/原始目标需要自己核。

父TASK117/R111，关联116/R110批准AP1/AP2、STEP006/008/009—018、NFR002/003/005、SEC001/002/003、DR002及DATA/FLOW相关实际变动。用户已批准116 AP1合成实施及条件AP2；必需独审现前置具备。原G3—G11、STEP017既有有限验收不重开，只有本117新增/改写及直接影响纳范围。GitHub已指定shspic/RetroLume-agent，原本地origin已关联，独审不授外部发布。

## 独立输入与读取顺序

先读原始目标/约束、实际差异和源码，再读运行原件。不要读取TASK117结果报告、自评段、实施聊天/记忆文件或其推理；可只按字节hash报告以核封存身份，不解码正文。若为执行控制核账确需实施者的偏差声明，先形成自己的事实判断再按主控指定最小段读取并披露接触范围；不要因未读自评就遗漏原账中的失败。

必要原始合同如下，同窗无重复全文需求；路径均以实际项目根为准：

- D:/shspic/project_NO3_RetroLume-agent/DocuS/最终需求文档.MD相关Must，不修改用户原始需求。
- D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-116/design/ 下 integration-contract.md、acceptance-contract.md、sample-inputs.json、adoption-package.md；DocuN/evidence/TASK-117/orchestration-20261014/adoption-receipt.json确认原采用，不读主控对实现的通过评价作证明。
- D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/orchestration-s06-20261016/X02-contract-correction.md及X02-source-basis.json。该主控更正只处理三个效果与独立delete命令混淆，NFR005/DR002的真实清理/失效要求不降。原116矩阵与旧错误卡保留历史。
- D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/orchestration-20261017/audit-inputs.json、contract-index.json、audit-permit.json；本卡列的冻结身份是对象边界，不是审计通过依据。

E表示 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/execution/，C表示E/continuation-05/。完整变化先看E/changes.json及preimages、E/final-changes-limited.diff，再沿continuation-01的changes/preimages及continuation-02/03/04/05的changes/preimages/source-changes.diff建立首次修改前→当前的真实差异。初轮diff是当时版本，不直接冒最终总diff；同文件跨轮相加要以首次pre及当前原文件核。新增/缺失标记和未首次备份的边界如实指出，不用mtime代替hash。

当前163项身份见C/final-source-manifest.json；当前正式bundle7四项见C/final-bundle-7-binding.json，主JS SHA256=58a87abf5ff4b02b33aab5dc3735507f4f097791e021aeb4ddfbf0b62ac115e8。产品关键当前config.py SHA256=f3582c2bca0db6dadc8fd5cfb3dfb9caa25b951848eb046861f04a21a856e38f。源冻结时有任何漂移，先报告具体文件/期望/实际hash，停止该对象结论；未变独立部分继续，不对旧快照签当前通过。

C/final-binding.json绑定27项，其中报告路径只hash，不读自评；final-readback.json、final-fixture-manifest.json、changes.json、source-changes.diff、historical-ledger-preservation.json、rules-and-protected-readback.json及API29—33 as-run用于版本适用。原E/budget.json、events.jsonl、case-index.json是工程唯一账，只读，不另写一份全局状态。

按实际依赖读取产品：activities仓储/只读投影/teaching/interview；capabilities contracts/embedding/gateway/transport；retrieval API/contracts/repository/service；014 SQL及R01/R02 schema/codec/snapshot/package/restore/reference/deletion/control/maintenance/config；learning/teaching/interview/memory新接线与policy/prompt/views；worker wire v4/v3、service_config/main、deploy/start_local及相关Compose；frontend活动/资料/两域/只读和意图门；preview生产SUP/REAP/Job/协议及PDF supervisor/worker/Job仅实际直接影响。未改主体可以有限diff及调用路径论证复用，不能因为函数文本未变就自动排除新接线影响。

旧G模块原源码和审计只按确需引用的具体断言查阅，历史TASK001—090路径按入口归档映射，不新建旧根。必要直接依赖可只读补入scope/hash；不扫描用户私配/真实库、不读其他Agent记忆或聊天。

## 集中审查的代码断言

1. 新类型、协议及出站约束。Embedding wire v4与旧v3精确分流，provider/model/512维/有限数值/容量/身份/父消费闭包；model/tool/embedding凭证隔离及007确认语义。只用合格源片段，selected memory低信任、不是履历或源证据；unknown不能重发/退款。新整步预算门不把仅预览够额当服务端已扣费。

2. 共享费用/次数和真实当前资格。两种provider沿同一全局锁序到活动/操作，持久预扣、请求/费用守恒、时间窗口/取消/恢复不绕过；grant日期/允许活动/源manifest/费率/请求上界/默认关闭受信配置一致。逐读_postgres实际sum/锁/更新事务，不能只靠共享gate被替身调用就判完整实际PG准入。S06两个连接真实锁但sum/预算是内存，证据范围必须保持；若代码明确有不安全路径给确定缺陷，若只缺实际写账证给Q前置最小补证，不虚构已过，也不默认把未来Q配置未开启列作S产品缺陷。

3. 检索和014。固定space身份/模型维度/canonical float32/hash、源/版本/片段current复核、cosine+词项RRF60边界；准备/query/cache/received+007+vector的同短事务确认、并发同键/semantic slot/CAS/晚到invalidated；容量/分批/unknown/partial清楚。014空/非空升级、最小NOLOGIN权限/SECURITY DEFINER固定search_path/明确EXECUTE、旧工具NULL tokens和旧预算数据不变；未知DDL不能宽松认已批准。001—013原字节保护与实际014前向修补/受信shape/两库ACL证据逐层核，不把源当前shape直接当可信基线。

4. 两域、记忆和UI。学习目标/路径/作答/参考曝光/独立证据计数与理由、面试v2目标/追问/自报/支持边界，保存/消费/进度同原协议；新检索引用及低信任记忆不升级事实。X02按revise资格、revoke墓碑、purge精确物理效果审，清理失败不复活，旧作答/最小历史费用保留。最终bundle的就绪门、意图原键GET/显式重试、owner/view/范围/selector晚到抑制、刷新无POST按实际改变核。旧完整业务链+当前变更U可组合证据；若认为不可继承，指出真正的新分支/版本/绑定缺口，不因非同一个Browser重跑而一律否定。

5. 恢复/只读/完整性。R01旧profile和R02新profile精确注册、31表全列codec/float32/007/unknown/预留/删除overlay及row/component事务/容量/超时；包/源最新tombstone不匹配即拒，failed对象保留/撤loader，seal后readonly。ControlHub缓存每次锁内核当前完整字节+文件身份/摘要，append/尾帧/同size同mtime篡改/换文件/外来hub/control_id/跨进程取消与fence均不误授写，返回不外泄可变缓存；commit持久性和Operation deadline/revision/clock authority保持。

6. owned/停止及两种readonly入口。原precreate未确认必须沿真实正常恢复取得新证明并保守全额，不把当前无PID/CID代替首次StopProof。_end_recovered_owned只能关闭唯一匹配的preview/parent/birth/nonce/原scope已验证owned，不关闭其他工作。新preview严格t0/3/4.5/8/D、真实Job/管道/private PID/init/image/CID/nonce/ready完整包时点、冻结renderer及签票/隔离/关闭和预扣结算权限；旧unknown和新正常停止分开。

隔离sealed-reader只持目标只读能力，真实目标/profile/目录/行资格核对，不能接source写/loader/维护/provider/preview执行配置；API全部写在业务前拒，不能成为绕正常selector激活任意DSN/本机文件的HTTP入口。原source正常activate的drain/owned/fence/selector原子事实、COMMIT响应丢失/故障不回source、同根不能回normal或换target；当前R02重开caps.format修补只使用已验证目标profile，R01保持。恢复副本永久只读是批准切片边界，不冒用户库持续执行恢复。

7. PDF与本机运行。诊断探针对真实HTTP/parse/实际受限worker起效且保留原分支/返回，原样本942字节/两物理页/人工确认/补充身份可回读，无放宽Job10秒/256MiB/2进程，旧两次422不能被新成功抹成“旧因已找到”。Windows原生API/SUP/Job与Compose PG分工、回环/会话/同源认证/无socket给Web、只读和错误体脱敏不退化。独立审查不要求Linux全应用/Nginx/公网发布这种尚未采用批次的动态证明。

## 原始证据核对范围

本卡不重跑产品。以下是入口和断言，不是要求复制所有日志或预设PASS：

- 014/检索原E/root02-retrieval-proof.json、compat前后目录/legacy行、r02-frozen-catalog.json、S03真实前向SQL/业务/删除/记忆晚到；初轮到最终预期shape依据、真实目录与失败原件按字节核。需要旧版本测试原件则先查已存as-run，缺失如实分级。
- S03两域持久及重开、S04 bundle7原键GET/就绪门/理由、S05 Browser12/13真实同键/晚view/owner/账门，S06 Browser14/15/16实载四asset。用响应/请求时间线及实际persistent receipts核，没有新UI分支不再要求整链重做；Browser15整体FAIL与可采信子事实和16修正头后证明分开。
- S06 C/X02-current-physical-deletion.json：真实清单hash和各版本hash/bytes、body_rows0、GET null、版本和选择身份保留；继承S03修订/撤销晚到原件，不虚构新的delete事件。
- C/L10/input-acks.json、actual-frame.png、supervisor-result.json、stage-times.json、ready-decision/ready-reception和settled-status及原进程/Job结束：PNG属于实际已接seq2的.5，不能声称reset后的1；ready约6.047秒、reaper约1.484秒、settled11/累计71/R0及次数2。旧第一次UNCONFIRMED、S05新恢复never_started/60秒与此次confirmed=true逐笔核，进程birth复用不误杀。
- C/PDF-diagnostic-admission.json、pdf_probe.py与HTTP as-run、PDF-HTTP-bounded-probe.json、PDF-two-page-confirmed.json及指向原确认/content原件；探针是在准入前冻结的新增观察能力，不以确认后错误GET404否定已COMMIT，也不抹错误。
- C/semantic-slot-race.json、inflight-goal-invalidation.json、R02-selector-increment.json及真实先dispatch再变goal/selector后释放旧响应；S06/source-targeted与Browser原件绑定正确schema/owner/view，不依赖脚本最终自评字符串。
- S04原617行/3938960字节包root b040841394dfa82a14c2b180e60393b3b7f0d222b11016b468a81d6f17c3a347、success01 target634aa034-51f6-4510-b075-38cb005481d8真实装载/seal/逐列回读/撤loader/readonly SQL证据；两个failed目标原件保留。S06无success02、不重装载，不能将正常PDF新增行外推已含在旧包。
- C/R01-final-browser-verified.json、reader-host-proof.json及S05 R01真实HTTP；C/R02-current-overlay-and-owned.json、R02-one-PG-switch-stage.json、R02-formal-readonly-reopen.json和原激活收据。原source控制根真实唯一selector generation1，activation55e4e1dc-e956-4a8d-801f-234580d6870e，源已冻结、target只读重开、无fallback和新目标。R01运行早于最后format补丁的版本适用性以实际差异判定。
- C/shared-global-budget-concurrency.json、shared-global-budget-PG-lock.json及shared_gate_check.py、root24_global_gate.py：原生产门被调用、两个PG真实advisory锁有等待，而manifest/grant/sum及计数由内存替身承载。明确这层局限与真实预扣的差距；首次45秒超时保留、后8秒有界检查不替旧超时找未证原因。

可用标准图片查看工具读本地PNG/截图，不启动真实Browser/Node，不调用产品脚本作“查看图片”。证据自述的独立性/成功/cleanup只是声明，核原命令/输出/时间/身份。原源码和fixture改动要区分运行时实际字节、最终字节、可继承的不行为差异；版本断链先查最小缺口，不默认全量运行来补。

## 执行控制与Q门，分别裁定

审计时工程全部预算封存，原未用S根25、API34、PG47、Q保留根均不授本卡。当前工程实际counts：roots24/PGcreate对象卷6/PGstart46/API33/Browser16/build7/Native140/HTTP2324/preview create-start2/provider与费用0。原工程budget状态returned_engineering_candidate、active_root空；S06活动12244.341136/14400、持有139.233/5400、离线进程保守257.6443102/1800；连续无资源12104.874136没有第二滚动offline门，不偷换为CPU或宣称完整连续监控。

按原contracts/continuation-permit及实际receipt分段核S01—S06：旧S01/S03/S04/S05超额/漏采、账号中断未知、原45秒失败、旧PG实际持有与次数、S06null新门/真实首点/未预记暂停、旧账原前缀保留。旧偏差不能追认合规，充分真实代码/行为证据也不因偏差自动全无效。给实现/证据/执行控制各自结论，指出哪一项确实影响安全或证明力，不由“总计数绿/红”替代事实。

C/final-resource-stop-binding.json指向2026-10-16T15:45:05Z的六CID非running/Pid0、端口和登记birth清单；新preview StopProof含原Job ActiveProcesses0/双EOF。旧预览当前OpenJob error2只代表当时不存在，不假填历史0。主控本轮没有实时Docker/PG查询，审计亦不准启动/重启资源，旧停止与当前文件只读封存分开。

Q仍未启用。第二个结论单列“Q前置已具备/仍缺哪些可验证条件”，不要把S工程通过写成Q可立即付费。必须列：实际provider/model/维度/官方现行能力、价格/条款、最坏调用和逐活动额度/费用预扣/共享总门的真实PG组合证据、账号与密钥的正常本地配置、72小时grant有效起点与主控Q回执。已有条件批准80次/20元不重问，原旧13元已用账不复活。

现有S source控制根已永久readonly、源DB frozen，不能拿它重新写入Q名册/试点或回normal。Q如需新normal合成库/控制根及精确资源许可，属于后续原工程窗的明确Q卡前置，本卡不创建或借新根清零费用；保留历史而不是将这种预期资源安排误写成S缺陷。官方现行事实留未来启用前核，本卡无公网访问额度，不签今天的价格/可用性通过。实际新代码安全缺陷和未来未启用条件分开。

## 权限、投入与停止

只读上述原始合同、源码、必要直接依赖、冻结输入和原始证据。可用已有解释器做标准库read/hash/JSON/AST/有限diff/账目归并，不import产品或执行任何旧runner。独立metadata小脚本每批<=60秒、累计进程<=1800秒；自有脚本普通修正连续，失败保留，不造mock测试来冒数据库事务。

本卡活动14400秒/接收后48小时，10800后不扩新审查族、13200后只报告/保存/复读，预留1200。首工具直接同步UTC/当前host单调时间，不从签发时追造首点；边界检查/读取/思考/保存算活动。阶段已完成就停，不用满预算。明确外部等待前关闭自有活动段/记原因；意外账号中断恢复先核无在途和时钟域，保留不明区间，不能以换窗/模型清零。新审计无既有运行尝试，产品真实运行预算为0；所有工程累计事实照留，不把审计metadata当第25个工程根。

仅写DocuN/evidence/TASK-118/audit/和DocuN/results/TASK-118-result.md。产品/测试/迁移/锁/dist/config/README/原证据/共享DocuS/主控裁定/任务卡/Git均不改；不跑compile/unittest/PG/SQL/Docker/WindowsJob/应用/模型/Browser，不装依赖、不联网、不读私配/密钥/env值，不解DPAPI控制键。必要registry只抽取非秘密身份/时钟/状态，不复制控制blob或浏览器storage正文。

同类读取/脚本问题两次有据修正仍失败、冻结对象不稳定、关键输入或独立性被推翻、实际安全数据破坏/越权发现、超范围或硬门到达时停止受影响范围并保存具体事实；其余独立审查继续。缺产品动态证据仅输出最小补证清单与为何影响哪条结论，不自行启动，更不要求所有旧测试重跑。

## 结果与回传

先给三轴结论和S候选是否具备交主控验收条件，再列Q门结论。逐项审查标准给事实定位/版本/证据/适用性；发现按确定缺陷、条件风险、证明缺口、非阻断观察和Q后续分层。确定缺陷写严重度、触发、影响、最小修正；不得将观察自动升级门槛。

列每项原证据继承/不能继承的准确理由，所有FAIL与unknown保持原貌；当前只读冻结和实际停止不外推过去。给原始scope/hash/有限diff/自己的命令和exit、投入、独立性披露、必要文档建议和最小下一步。没有必要人工事项就写无，不向用户索凭据或让用户执行代码。

最终保存并复读 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-118-result.md，只提出建议状态，不填写主控最终验收。确认可访问后只回一句话结论和可点击完整绝对路径，供用户带回。发现的修复集中交主控另续原117，本独审窗后续只作必要增量复核。
