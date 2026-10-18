# TASK-118 / R-112 — review-01 四项合并修正的独立增量复核

## 完整成果与原独审窗口

你继续 TASK118 首轮的独立审计上下文，只复核 D01—D04 的合并实际修正、直接影响、证据适用性及 S07/S08 执行控制，给出四项是否可关闭、完整S是否具备交主控验收条件，以及Q前置如何更新。不是重做S01—S06七族全面审计，不实施修复、不重跑产品、不签Q或STEP018/019/M-1/项目通过。

接收A+增强资源，优先原TASK118真正独立的审计上下文，不能用TASK117工程窗口。首轮实际采用fork_turns=none隔离上下文且未继承实现聊天，该披露继续有效；不冒充另一个客户端或确定模型。如果原上下文不可续，只能由一个保持独立的A+接续审计窗口依据原合同/源码/证据恢复，禁止承接117完整聊天、思考、自评或读个人记忆。不为型号变化重做已有审查，不再委派新的并行审计。

原117工程已交回候选，源/测试/正式产物和原证据在本卡期间只读冻结，无并行写入；主控仍负责共享状态与最终验收。保持人工转卡和统一结果路径回传，卡面保存不代表已接收或开工。

## 项目、规则与授权

实际根 D:/shspic/project_NO3_RetroLume-agent，入口 D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。task_model/V4.0、公共AGENTS CHG-0003、阶段07；需求v1.3、架构v1.43、执行动态v2.70。公共只读根 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4；锁定七项身份仍DocuN/evidence/v4-migration-20260930/rules-snapshot.json，沿同版公共AGENTS、WORK第2章task_model/第6章独审合同及task_model/prompts/07_开发执行循环.md。已读且未变正文直接复用，只补变化，不自动采用新版规则。

仍TASK118/R112，轮次review-01，父117/R111，关联116 AP1/AP2、STEP018及相关NFR002/003/005、SEC001/002/003、DR002。范围来自首轮D01—D04和已授权合并修正；没有新TASK119、费用、数据外发或产品运行授权。主控只核封存身份和可审原件，未预设你的缺陷关闭或通过结论。

## 独立输入与冻结身份

1. 本入口、公共适用增量、本卡。原始需求/116采用包仅按四项依赖复用；D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-118-result.md 首轮原41590字节，SHA256 dd0a5f1d2ddb2ffcd9a168496e4cca5b8292b7221977c76b8ff417f9ff0f21f1。自己的原发现、依据与其余可继承结论可直接用，不重跑已完成七族审查。
2. 本次 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/orchestration-review01-20261018/ 的 audit-inputs.json、review-permit.json、scope-index.json。它们仅给对象、路径、许可和主控身份核对，不代替你的实质判断。不得读取本目录received-candidate.json中的工程评价作为独立结论。
3. C表示实际绝对目录 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/execution/continuation-07/。先读C/post-source-manifest.json、TASK118-four-repairs.diff及直接实现；它们含S07初版和S08最终增量，不能只审S08-delta.diff而漏S07六文件。post清单20项、相对独审基线18项有差异，S08本身14项变化。按preimage链重建：首轮实际源码→continuation-06/preimages→C/preimages/当前文件。新增/原件缺失如实登记，不把规整换行的diff冒原字节。
4. 再读下述最小原运行证据。as-run/case计数与“passed”只作导航，真正依据是源/测试方法/原命令日志、请求响应和资源结束记录。实现自评不是证明。

当前工程报告 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-117-result.md 为104337字节，SHA256 90b4ebc77c34cf7886f5e4bb624a9912c14df9b5a7b53ac2528826487bd771e2；仅可按bytes/hash和旧后缀核封存，禁止解码本轮/历史实现结果、before-result、完整实施聊天/思考/记忆。C/final-binding.json中工程结论字段同样只导航，不把其D01/D02数量作为你必须签的答案。

新正式bundle8主JS frontend/dist/assets/index-BuUoTjO5.js，855765字节，SHA256 bc2768fdd2d1878b44decfabd6912fdd2df7469198f9b563bca5b34edfa3c0c1。C/bundle-8.json另列index.html/CSS/PDF-worker共4项；真实浏览器主要证明JS/CSS实际fetch，不把磁盘四项一致扩称四项全实载。旧bundle7原字节在C/bundle-7-before/，不能用其UI证据覆盖新源码。

current_source与关键证据的完整冻结列表见audit-inputs.json；主控已核20项、28项binding及4bundle无漂移，但你仍要独立核本次实际读取对象。漂移给具体期望/实际hash并停对应对象结论，其他未变独立部分继续，不对旧快照签当前通过。

## 四项实质问题与直接影响

### D01 原P1 控制日志写身份

核对_validated_locked是否确在commit/create_or_get_job/change_job各自同一次真实锁内校验完整当前字节、文件身份、首hub.init与绑定control_id，之后才replay/CAS/append。合法缓存不能绕过当前字节、残尾、同size/mtime篡改；same-key路径不能返回foreign job。公开状态和写回执不可泄出可变缓存或让调用者改缓存事件；正常peer取消/fence、revision/clock/deadline、fsync和原容量保持。

证据先看backend/tests/test_step018_control_snapshot.py和C/backend-targeted-v2.log、targeted-as-run.json。该命令整体随后在另一个async夹具构造时超时，日志12个已完成方法不能改写成整批exit0。独立核其方法字节、实际完成输出、最终产品未变及测试后续差异，决定这些子事实能否继承；不因为命令整体TIMEOUT就自动全无效，也不因为摘要写12就自动采纳。三个foreign有效日志反例必须覆盖commit、同键create返回及change命中外来job，零追加、零外来返回/decide副作用。

### D02 原P1仅未来Q 全模型正文与受信批准

核model_requests的有限严格字段、完整payload和typed request双摘要、重复/非法值拒绝、非空hash变化、空新增字段旧Embedding hash兼容；实际loader、grant绑定、私有wire v4和旧v3边界一致。源catalog校验不能被完整payload审批替代丢掉，或反向只核catalog漏正文。准入前/await准入后/dispatch前/mark后实际send对象须与同一受信批准一致；变化时保守预留、NOT_SENT/UNKNOWN纪律、不得退款/重发。不要要求测试故意对外发送隐私。

看backend/app/capabilities/embedding.py、gateway.py、直接loader/请求装配，及实际测试test_step018_audit_repairs.py、test_step018_flows.py、test_step018_embedding_contracts.py。原日志C/backend-no-io.log、model-scope-v2.log、approved-model-final.log，导航as-run-final.json、targeted-no-io-as-run.json、model-v2-as-run.json。尤其核最后批准正例确实调用真实TeachingService._stored_document/typed消息/真实网关最低transport，而不是只测SimpleNamespace或换掉准入拒绝；原记录未隐藏两次async构造超时和后续tuple/list夹具修正。

无实际I/O的测试采用backend/tests/fixtures/step018/s08_loop.py避Windows socketpair沙箱阻塞，检查它是否只移除不需要的fd能力并保留asyncio调度/timeout，不替换产品协程、网关校验、消息装配或未知语义。不能将该层证据冒真实PG、外网或产品事件循环已验证，也不要要求为本局部无I/O反例重跑全部Windows/PG。

明确区分安全收口与Q可执行性：一组固定批准请求能正常send不代表依赖未知上一模型输出的多步Q链已可执行。核“不可重绑已有活动grant/roster”与后续新增payload批准是否仍有合同缺口；有则准确列为Q待解决的范围/最小决定，不能偷换既定学习/面试语义目标、自动加白或签Q就绪。只有实际发现当前修复本身违背既定安全/兼容合同才保留相应代码缺陷，不把未来未启用本身又判成S外发事故。

### D03 原P2 同activity原owner/view晚到

核TeachingWorkspace及teachingApi/teachingIntents、直接DataContext/草稿依赖：一次原意图的activity/owner/view/head/scope/namespace应不可变，所有await后的后续domain POST受同一身份约束，不能比较两个新owner；domain_sent与实际发送顺序、原key/完整草稿和GET恢复不丢。检查共享owner/摘要锁变动对旧学习、记忆、面试调用的直接影响，不因未改调用者文本而排除回归，也不扩成全部旧链。

看frontend/tests/step018-s08.mjs和C/root-25/attempt-03/proof.json、network-timeline.json、browser-as-run.json。四个D03场景应发生在同activity、query已返回持久化、原生IndexedDB draft commit之后/native oncomplete之前，再驱动正常刷新改变owner或view/head；确认不是换到另一活动，也不是注入修改产品guard/组件内部状态。原生IDB屏障是否真在风险await、下一POST0/原key与正文不丢、正常对照恰一次POST，都依据时间线和实际对象。

owner反例若只是A lease因session A→B而失效只读，要如实限定，不说已成功取得B lease。head反例不能扩称DataContext已动态覆盖。原key读取为真实浏览器显式fetch+合成HTTP，不称真实后端资格链；已有未变GET实现的原证据能按实际适用性继承。

### D04 原P2 三处实际供应商告知

核RetrievalPanel/retrieval-api、TeachingWorkspace、InterviewWorkspace、ActivityWorkspace和retrieval/service.py的实际provider/model字段投影，确认前能见向量/后续聊天的身份、用途、请求/费用/窗口，缺失/坏格式/未知时关闭相关外发。不要硬编码配置不支持的供应商能力或泄露秘密，正常本地保存/取消/只读资格不受无关关闭影响。

按上述正式bundle实际响应、三处场景/缺字段门/改值对照核。synthetic_vector_b/s08-vector-model-b和synthetic_chat_b/s08-chat-model-b只是证明消费配置字段，不代表正式支持新provider；封闭fixture未填的新建quota区域undefined不能冒完整页面通过，也不能无依据升级成当前产品缺陷。需要图片时只读C/screenshots.json所列本地PNG，可用静态图片查看，禁止启动Browser/Node求图。

## 证据、原账与历史控制分层

C/as-run-final.json列33个方法仅是导航，按唯一方法名、原日志实际完成、测试与产品hash逐项去重，D01/D02及D04共用方法不重复认领。targeted-as-run、targeted-no-io-as-run、model-v2-as-run、browser-as-run记录各批字节。某些测试最后修正但旧方法语义未变时，可以做有限方法级对照继承，不机械要求最终全文件一口气重跑。确有证明缺口给最小补证和所影响断言，不自行执行。

根25三次attempt和原FAIL/TIMEOUT全部保留。attempt01缓存目录错误未建Browser、attempt02受sandbox回环限制、attempt03经平台批准同根原截止内成功，区分启动尝试/实际进程/普通权限升级与产品权限。原图像、原工具批准/错误收据可按具体问题查读取范围，不能绕权限读取密钥/私配。fixture的生命周期Job属于本卡自有清场，不混同原产品Windows业务监督新调用；原产品Native计数仍140，不能只凭看到Job API就推断偷跑业务。

原唯一工程账 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/execution/ 下budget.json/events.jsonl/case-index.json只读。C/before-budget/events/case-index和before-result只作bytes/hash/必要原账对象对照，禁止读实现报告正文。S07保守30294.653691秒及超8694.653691、metadata漏账/mono跨域unknown不改；原66条failure前缀保留，S08新增15累计81不等于15个产品缺陷。以前S01—S06原审计控制轴结论继续有效，不追认。

S08前向许可在D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/orchestration-s08-20261017/continuation-permit.json及其before-documents原完整卡。它明确48h日历+子进程wall3600/持有并集3600和次数门，无跨中断活动硬门，不准重新套旧S07的21600或初卡cap。首点2026-10-18T01:30:39.437716Z，日历截止2026-10-20T01:30:39.437716Z。按当时许可核，后来许可不追认以前违规。

最终已观测UTC上界2133.185536秒，through-readback保守命令wall473.6992712/3600，持有并集上界30.11/3600。实际累计root25、Browser19、build8、fixture server3、HTTP2486、PG创建/对象/卷6、PGstart46、产品API33、Native140、preview各2、provider/费用0，active_root空。Browser/server上限用满，根26/27未用也不授权本审计。

C/control.py/check_control.py/runtime.py、control-selfcheck.json、19项有限自检原件、final-timing.json、tool-receipts-at-seal/complete等及原root25元数据可只读核边界。首点/当前域/同根截止、单调倒退拒绝、时间/次数/准确自有树/压力/父退出清场不许只抄passed。metadata保守嵌套相加和原unknown分开；核是否有真正控制缺陷及影响，不将历史红轴自动推翻充分行为证据。

C/root-25/attempt-03/stop.json的2026-10-18T01:54:55.272724Z是child exit0、PID/birth和18119记录；final-resource-stop.json于2026-10-18T02:06:12.601520Z复核已登记自有树、same_birth_alive/current_lookup_unknown均空、无监听。它们只证明其时点和归属，主控与本审计均不实时查Docker/PG。原六CID、frozen source/permanent readonly selector未启动；旧PG停止仍只引用2026-10-16T15:45:05Z原件。不要为“核实时停”执行产品或系统启停。

## 只读权限、原审计余量与停止

允许读取上述源/测试/构建资产/原始合同/直接依赖/证据，已有解释器仅标准库read/hash/JSON/AST/有限diff/账目核算；不import产品，不运行原脚本。只写 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/audit/review-01/ 与 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-118-result.md。旧audit目录、原首轮结果/回执/证据保持，不覆盖；结果review-01置顶，原41590字节精确后缀保留。

所有产品/测试/compile/unittest/build/Node/PG/SQL/Docker/业务Job/API/Browser/provider/联网/费用/Git写新增0；不读取env值、真实key/私配、DPAPI或用户库，不安装/签票/发布。没有新证据要求时不扩查旧七族或等待全部Q，覆盖四项和实际影响即可结束。

原审计metadata保守已扣116.9280809秒/1800。本review-01从该余量中最多使用1200秒，保守累计至1316.9280809，不清零首轮；单批标准库命令<=60秒。首轮活动保守3017.5108645秒和偏差照留。本增量从实际首工具采UTC/本机单调域起48h，最后日历1200秒只保存；不另用跨未知中断的总UTC上界作新活动硬门，实际可观测段/未知和命令收据分开记账。恢复遇时钟域不明只停止对应读取执行段，保留旧采样，按本轮剩余日历/metadata许可重锚，不改首点或加余量；无任何产品资源需运行。

metadata问题两次有据修正仍失败、冻结漂移、独立性缺失、范围/关键前提被推翻、实际严重安全问题或门到时停对应部分并留事实。权限不足用获准只读替代，不借审计升级产品权限。主控未授权本卡动态补证；缺证如实给最小缺口，不暗开工程26根或付费。

## 一次形成结论并回传

逐项D01—D04给关闭/不关闭/证据不足及定位、触发、影响、适用hash、旧结论如何继承。代码、证据、执行控制三个轴分别给本次和历史边界；完整S是否具备交主控关闭条件独立表述。不能把报告完成等同所审S通过，历史控制不通过也不自动要求重做所有代码。

Q继续另列未启用：真实PG roster SUM/两provider持久共同预扣组合、官方当前能力/费率/条款、正常账号配置、新normal合成库/控制根、有限完整请求批准对后续多步链可执行性、72h和主控Q回执。已有80次20元条件许可有效，不索用户再次批准或凭据，不联网核现行事实，不删既定语义目标、不解冻旧source。确认安全修正不等于Q可以马上付费。

新确定缺陷合并交主控回原117，非阻断观察不升为门，明确修复/补证最小范围；没有缺陷不为了更放心加测。记录读取/有限diff/hash、原方法/批次可继承依据、原始失败/unknown、投入及独立性，结果只提建议，不填主控最终验收。

保存并完整复读原结果路径D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-118-result.md，原41590字节历史完整保留；新回执另在review-01/。必要用户动作无。确认可读后只回一句真实结论与完整可点击绝对路径，供用户带回。
