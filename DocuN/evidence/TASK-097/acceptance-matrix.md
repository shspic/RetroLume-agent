# TASK-097 / R-091 T01—T18真实验证矩阵

2026-10-02，Asia/Shanghai。本矩阵记录执行者卡内检查，不是独立验收。整卡为部分完成，所有8个集成runner整体exit=1，未执行项不能转为PASS。

证据根为D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097。下文批次即该根目录的实际子目录。每批被测源码与夹具版本均在该根as-run/{批次}/files，manifest.json给出SHA256、命令和预期。最终版本由post-manifest.json及final/files给出；每批到最终的差异见integration-01至08-to-final.diff及evidence-applicability.json。字节相同只支持版本绑定，不能代替动态断言。

## T01 就绪资料与片段身份

预期：仅活动实际来源，TXT/MD中英文、就绪PDF物理页和用户补充的真实代次、ID、hash及位置可复查。

实际：通过已执行范围。test_learning_contracts.test_english_chinese_pdf_supplement_and_revision_zero纯函数覆盖revision=0/3/5和中英；integration-02-pg的test_learning_pg.test_authoritative_txt_md_pdf_supplement_scope_and_utf8真实发布并读取TXT/MD、PDF及补充，按仓储值比对revision；integration-07-browser正常引用回查到文本及PDF。

原件：as-run/offline-01/stdout.bin、integration-02-pg/stdout.bin及pg-summary.json、integration-07-browser/browser-report.json的text_citation_utf8_lines_and_xss、pdf_physical_page_original、pdf_user_supplement_identity。PDF解析文字为合成核对页，不验证真实PDF OCR质量。

## T02 范围过滤先于外发

预期：未选、删除、替换、未核PDF和范围外近似源不能进入包或获得新调用资格。

实际：部分完成。integration-02-pg上述范围样例含范围外高频近似资料，目录无其ID；test_deleted_replaced_unreviewed_and_budget_reads_single_select实际触发revision变化和未核PDF无current_version；test_real_gateway_atomic_normalization_and_citation_invalidation实际发布替换版本后引用不可用。offline-05/07的adapter范围/槽位反例在admit前拒绝、send=0。真实PG删除来源的独立场景not_run，不能因测试名称含deleted宣称已执行删除。

原件：integration-02-pg/stdout.bin、pg-summary.json，as-run/offline-05-worker-authority和offline-07-final-guards原始输出。方法和模块实际版本按各批manifest，最终validate_snapshot/原文组装版本可比对post-manifest。

## T03 输入、歧义、不足与冲突

预期：空/过长、缺领域、Spring/同名歧义、零候选和冲突有独立提示，不扩大范围或自动调用。

实际：通过冻结样例范围。test_learning_contracts.test_empty_long_multibyte_query_ambiguity_no_evidence_and_bounds拒绝空、1025字符、控制字符、25词项、513片段，Spring及无法定位输入追问，无候选no_evidence。真实PG支撑HTTP在没有候选时requests_reserved=0、操作数=0。integration-05-business实际受控调用分别原子保存clarification、no_evidence、conflict并计账，不假造无模型received。

原件：as-run/offline-01/stdout.bin与stderr.bin；integration-02-pg/stdout.bin；integration-05-business/business-checks.json中atomic_structured三项、对应transport/session原件。未验证真实供应商识别冲突的语义质量。

## T04 配置与有限额度

预期：缺配、坏配、请求/输出及账面额度在应拒位置关闭，旧层级兼容，不额外调用。

实际：部分完成。test_learning_config三方法实际检查默认关闭、未知profile、257/布尔输出值、混入工具、密钥缺失、坏L1、服务输出128不兼容；旧读取/零费新建/普通继续层保持。真实HTTP test_layers_l0_l1_l2_and_budget_preflight检查缺学习/坏学习/缺服务密钥层503、读取200、活动请求字节降至1024时413且零预扣、取消200。全部来源/字节/运行/费用及输出使用量上界没有逐项真实PG触发。

原件：as-run/offline-01原始输出，integration-02-pg/stdout.bin和pg-summary.json。最终confirmed严格布尔额外检查在offline-07；缺配UI反例not_run。

## T05 首次原子保存与持久读取

预期：真实产品链保存应用目标/目录/正文/received同事务，成功正文才确认committed，刷新只读恢复。

实际：通过所绑定主链版本，最终新增守卫未完整链复验。真实PG test_real_gateway_atomic_normalization_and_citation_invalidation的operation/result xmin相同；修正公开正文后integration-03复验该方法通过。integration-04-business真实launcher/SUP/worker/Job/gateway首次及续问，两个send，规范公开正文与received_xmin/body_xmin均2858。integration-07浏览器也完成实际首次；integration-08新应用/新浏览器上下文读07持久首成果及续问，learning_posts=0。

原件：integration-03-business/affected-pg-summary.json及stdout.bin，integration-04-business/business-checks.json的normal_first_followup_atomic和session/transport原件；integration-07/08-browser/browser-report.json。最终None-profile保留命名空间拒绝分支仅offline-07验证，不扩写为最终正向Windows重验。

## T06 非法结构、引用与支持性

预期：伪/外域/错误版本、hash和位置以及非法JSON/未知字段不能成为可用成果；引用身份合法和结论支持分开。

实际：通过冻结反例层级。test_learning_contracts四种结构、非法引用/未知goal/verified、重复JSON键和NaN、版本/revision/hash/行/offset篡改拒绝；gateway已收到非法输出是received失败且无payload。真实PG及integration-05 actual_invalid也观察received、invalid_learning_output、无正文；不冒充UNKNOWN。固定语义正句“所有修改一起提交或都不提交”由原句支持；反句“每项独立提交”与原句矛盾，两份结构均合法，逐句对照原件保留。资料注入位于user数据，未变system或工具集。

原件：as-run/offline-01/stdout.bin固定semantic_sample及测试输出；offline-03/07原始输出；integration-02-pg/stdout.bin；integration-05-business/business-checks.json的actual_invalid。没有供应商整体正确率或独立语义审计结论。

## T07 原文、版本与安全渲染

预期：UTF-8、CRLF、转义、PDF物理页和补充身份可查；替换后拒用新版本，模型文本不执行脚本。

实际：正常回查通过，失效UI部分完成。真实PG回查目录文本一致、lc_fake拒绝、发布替换后citation_unavailable且旧正文hash不变；浏览器07查到真实文本第二行的img/onerror文字，learningXss未执行、没有生成img元素，实际PDF原页canvas和物理页/补充身份可见。浏览器替换后/伪引用不可用UI尚未执行。

原件：integration-02-pg/stdout.bin；integration-07-browser/browser-report.json、browser-text-citation.png和browser-pdf-original.png。引用查询不同只读请求不声称共同SQL快照。

## T08 首次槽位与真正竞争

预期：同键同文返回事实、异文冲突、不同客户端UUID及真并发至多一次send。

实际：通过已执行竞争和顺序反例。integration-05真实两客户端异UUID并发，启动两个真实SUP，均取得同一operation事实，实际合成send=1；随后同文新客户端键只读取、不同目标409、学习降级普通继续409，sends_added=0。没有新字段或种父结果。不同目标的并发竞争not_run，不能等同于顺序异文反例。

原件：integration-05-business/business-checks.json中的real_concurrent_first、stable_first_slot_and_profile_downgrade_refusal；两份实际sup-launch/session及transport原件。当前service/repository指纹与该批比对见evidence-applicability.json。

## T09 丢回执、未发送与未知

预期：真实持久事实可查询，UNKNOWN不自动换键、不重复预扣或退款；提交成功丢回执仍可读。

实际：后端通过，UI组合部分完成。真实PG test_committed_ack_loss_and_real_scope_slot_conflicts在原record成功后抛模拟ack丢失，gateway返回UNKNOWN但GET为committed_current；取消后旧正文是committed_history_cancelled。integration-05 actual_unknown持久unknown并保留预留、actual_not_sent持久not_sent、非法received无正文，各自同键额外send=0。UI“请求未到达/响应丢失/核对/重试/放弃”的完整组合not_run。

原件：integration-02-pg/stdout.bin，integration-05-business/business-checks.json的actual_unknown/actual_not_sent/actual_invalid，相关session/transport。not_sent的合成send方法进入不等于产生外部socket请求。

## T10 学习父成果与旧继续

预期：真实首次成果经G4父凭证、新操作/scope重新准入续问；旧普通model继续可用，tool隔离不退化。

实际：首次/学习续问与普通model继续通过绑定版本。integration-04及browser-07的父成果均来自真实首次链；integration-05 legacy_no_profile_real_parent_and_continue的普通父正文也由真实run_one_call形成，再走旧continuations。工具凭证隔离没有新增真实Windows业务场景；protocol4/工具主体原字节未改，offline-02直接协议4兼容用例通过，旧有效审查作为限定复用。

原件：integration-04/05-business/business-checks.json；integration-07-browser/browser-report.json；as-run/offline-02-fixture-protocol输出、core-freeze-check.json。最终保留命名空间拒绝分支仅offline-07；不声称完整旧G4/D3全量重验。

## T11 取消、替换与晚到

预期：失效/取消晚到不污染已有成果和账面，新操作无不合规提交；仅停止自有树，远端请求不可撤回。

实际：部分完成。真实PG在send后改revision或取消，结果无正文、保持原UNKNOWN纪律；integration-05在实际合成send后取消正在阻塞的续问，旧首成果仍可读、新结果无正文、取消后最终R=0/S=92，相关会话树零。计划120秒专门挂死由Job硬停场景not_run；60秒阻塞取消/异常退出不标为硬停场景通过。

原件：integration-02-pg/stdout.bin、integration-05-business/business-checks.json的cancel_after_send_preserves_results、对应session/gate-close/job-close文件及resources-final.json。页面取消文案为产品实现，组合UI仍有缺口。

## T12 客户端意图与显式POST

预期：先存后发、旧格式兼容、损坏关闭、刷新只GET，核对/同键重试/放弃互不替代。

实际：部分完成。browser-07每个显式首次/续问各1个POST，夹具在请求事件检查台账已存在；offline-09直接导入真实意图函数，旧continue、新首次/续问、保存失败、损坏形状、目标/问题/父键匹配和冲突均检查通过；冷恢复browser-08无学习POST。最终新增核对输入匹配及迟到保护只经这些纯函数与构建，真实UI的未知横幅/重试/放弃/损坏读取消组合not_run。

原件：integration-07/08-browser/browser-report.json及as-run脚本；as-run/offline-09-intents/stdout.bin、files/frontend/tests/task097-intents.mjs，最终ActivityWorkspace由build-05绑定。

## T13 轮询与迟到上下文

预期：不重叠、隐藏暂停、卸载清理，慢活动/成果/引用回包不能串正文。

实际：部分完成。旧D2轮询主体未改变，限定复用TASK-095-final-acceptance关闭结论和当前pre字节比较，不重审095/096。新引用正常切换在browser-07走通；慢回包、活动/操作快速切换、隐藏/卸载的专门浏览器断言未执行。新核对迟到保护的最终字节仅typecheck/build，不能按代码存在报动态通过。

原件：pre/frontend/src/activities/ActivityWorkspace.tsx、limited.diff、integration-07-browser/browser-report.json、build-binding.json；旧接受原件为D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-095-final-acceptance.md，身份在input-verification中匹配。

## T14 真实PG与HTTP

预期：新增快照/槽位投影真实查询，正文/meta/原子事实一致，旧列表无正文、单SELECT兼容。

实际：通过所执行数据库层范围。integration-02的5个PG方法均通过；旧四个读取及两个新助手各实际execute=1，列表未请求payload列。实际原子xmin一致、ack丢失、版本失效和已知非法结果有原件。三个HTTP方法分布在02及04通过；03/04只重验失败/受到公开正文修正影响部分，不追加全量回归。

原件：integration-02-pg/stdout.bin、pg-summary.json；integration-03/04-business/affected-pg-summary.json及stdout.bin。02整体仍含一HTTP断言与FK清理失败，不能改汇总为PASS；最终confirmed类型补强是offline-07，不扩写为最终HTTP全量通过。

## T15 真实Windows组合链

预期：真实首次/续问、重复/失效/取消、准确send/关闭/R/S/G与树零，不伪造G/Job身份。

实际：部分完成。真实链启动共15次，04为2、05为11、07为2；有15份SUP启动、15份真实Job关闭、14份SessionOutcome。一个旧普通直接调用在安装观察器前导入函数，缺SessionOutcome文件，实际Job代次/worker导入/transport证明到claim，不减次数。合成Transport.send入口共14次；外网模型发送为0。首学/续问、两会话竞争、UNKNOWN/非法/NOT_SENT/取消已执行。专门硬停场景和最终新增守卫后的完整Windows正向not_run。

原件：supervision-ledger.json、各业务批次实际boot/import/transport/sup-launch/session/gate-close/job-close、resources-final.json。14份已记录会话active_processes_at_end均0；最后只读核实所有本卡根及既存后代树零。

## T16 真实浏览器主链与反例

预期：选择→零费新建→目标确认→首次→原文→显式续问→刷新恢复，并有缺配/坏引/XSS/慢回包等反例。

实际：部分完成，整体FAIL。browser-07六项check真实通过选择新建、显式首次、TXT/XSS、PDF原文、补充身份及续问；刷新之后定位器误用UUID而页面以来源标题列活动，超时。browser-08新应用新context冷读取此前真实父/续问，无学习POST，check通过；紧接刷新时资源response.body Promise因页面关闭拒绝，Node整体退出1。后续UI反例及本页完整刷新断言未走完。修正脚本未动态重跑，最后build-05 bundle未在浏览器服务。

原件：integration-07-browser/browser-report.json、browser四张截图、browser.stdout/stderr.bin；integration-08-browser/browser-report.json、browser.stderr.bin、retained-fixture.json。前者6项和后者1项不能相加成整卡绿色。浏览器实际启动3次，另一次driver在启动Chromium前模块失败。

## T17 profile、协议与敏感信息

预期：原protocol3/4/无profile保持，未知/非法/混用profile拒绝、不降级；敏感授权物不入外发/正文/浏览器。

实际：通过直接契约和限定业务范围。offline-02七个直接协议/网络夹具方法通过；offline-03/05/07严格profile/范围/混用工具/消息/response_mode与未知版本拒绝、admit/send=0、正常受信正文与无正文回执检查通过。外发payload不含profile、input_result、activity_id、source_revision、api_key字段或工具；实际传输测试不产生DNS/外网socket。真实旧无profile model继续在05通过。保留命名空间却无profile拒绝是后补分支，只做最终offline-07，未在最终真实Windows跑一轮。

原件：上述as-run原件/原始输出、integration-05-business/business-checks.json、core-freeze-check.json。父payload摘要及history仅内部，不持久公开；未知profile没有降级路径。浏览器主动外网探针未执行，不能以blocked为空宣称全机网络机制已阻断。

## T18 冻结链、构建与资源

预期：独立重建所有实际被测版本、修正diff、最终源→产物→实际服务、资源及计数收尾。

实际：部分完成。原pre40、dist前置4、每批as-run原件/运行后hash、实际导入、失败原文和到最终diff、最终快照、构建5次原始输出均保存。build-05包含HTML模板/tsconfig等完整源码输入；四类输出与build-04相同。browser-07实际服务build-02四类字节并逐个hash匹配，最终build-05浏览器not_run。旧模型调用SessionOutcome少一份且首次证据组装未独立计时，分别披露并按60秒保守记离线额。

资源入口8/start8/SUP15/实际浏览器3/保守driver4，业务226.312秒、清理4.937秒；精确容器Running=false/Pid=0，本卡树零及18097/15197/55441释放。097库/卷及一活动三来源保留、不drop。最终完整矩阵与独立审计均不成立。

原件：pre/pre-dist/post-manifest、changes/limited.diff、as-run、evidence-applicability.json、build-binding.json、budget-final.json、attempt-ledger.json、supervision-ledger.json、resources-final.json、delivery-proof.json。delivery-proof只能证明保存和一致性，不是动态复验。
