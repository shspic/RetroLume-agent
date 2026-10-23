# TASK-121 / R-115 — Q v2完整工程候选集中独立终审

## 目标与交付

你是本卡独立审计者，只读审查TASK120的**完整实际变化**、证据与执行控制，给出批准的有限工程切片是否具备交主控关闭条件。不是只审续作06的8个文件，不重新审TASK117中未变且已由118接受的S，不运行/修复产品，不批准真实Q、用户库、付费或发布。

交付一个完整集中终审结果：代码、证据、执行控制三轴分别裁定；C01—C15按原合同对照；问题合并列出严重度、精确触发、影响、最小修正/补证及复用边界。独立判断先依据原合同、真实diff/实现、方法与原始运行记录形成，不能以工程自评或主控收存结论替代。

当前目标限定在获批Q v2逐请求批准/原键恢复与显式继续、真实PG合成预算与竞态、最终UI隔离、015单表权限及严格profile兼容的工程交付。真实供应商/账户/计价/币种税/模型返回身份/正式启用readiness等依旧按原采用合同留后续；它们未运行不是本卡要求偷偷补跑的事项，也不因此把“工程切片可关闭”扩成真实Q可用。

## 项目、规则、关联与接收安排

- 项目根D:/shspic/project_NO3_RetroLume-agent；根入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。
- task_model，V4.0/公共AGENTS CHG-0003，阶段07；需求v1.4、架构v1.54、执行动态v2.82。公共只读根D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，读DocuS/AGENTS.MD、WORK.MD适用task_model/完整审计合同/证据/投入/停止章节与task_model/prompts/07_开发执行循环.md；七锁定指纹在本项目DocuN/evidence/v4-migration-20260930/rules-snapshot.json，不自动采用后来版本。
- TASK121/R115，父TASK120/R114，关联TASK119采用K1/K2、116、117/118的有限S与STEP018，NFR002/003/005、SEC001/002/003及DR002按原合同适用范围。新号仅用于首次完整独立审计，工程修复仍唯一归TASK120；不把旧118四项关闭冒称Q v2完整已审。
- **接收A+增强独立审计资源，沿原118独审责任，新建一个隔离审计会话。** 理由：本次是TASK120完整高风险候选首次终审，含55项相对初始清单的产品变化、跨轮证据与新权限/profile；须与117/120实现上下文隔离。可由原118审计者承担，但不继承工程聊天/思考/实现自评，不委派子Agent或并行审计。客户端/实际模型照实登记，标签不冒充型号。
- TASK120已回传并封存；本卡期间产品、测试、dist、原结果/证据和唯一工程账全部只读冻结，工程原A及更早A+均保持停止。主控只维护共享账，不作工程或独审执行。
- 授权为已批准工程成果所必需的集中只读独审，无产品运行许可。新审计工具wall/日历额度独立记，不重置、借用或增加120的旧运行/资源额度。卡面保存不表示已转交/接收/开工。

## 独立输入、冻结与读取顺序

本卡路径除另有说明均相对项目根。审计输入根为**D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/orchestration-20261021/**。

1. 根入口、同版适用规则、本完整卡；输入根audit-inputs.json、scope-index.json、audit-permit.json。它们仅给对象/路径/hash/合同边界，不向你预填通过结论。先独立复算209当前文件身份及scope-index中额外实际产品文件；有漂移给期望/实际hash，暂停对应对象“当前通过”，其余独立部分继续。
2. 原始TASK120完整合同：DocuN/evidence/TASK-120/orchestration-20261018/task-contract.md及adoption-receipt.json；原设计合同DocuN/results/TASK-119-result.md中有效A—D/K1/K2和实际采用原件仅用于确认目标/约束。补读后续前向许可及合同：orchestration-repair03-20261019、orchestration-validation04-20261019、orchestration-final05-20261019，和orchestration-continuation06-20261020/contract-06.md、permit.json、approval.json。AP-120-06原提案位于orchestration-adoption06-20261020/adoption-proposal.md，SHA256 3884a5c056cb13f0216c59652a408ea57edbbc5064d429b5d2ea783f172c5c70。不要把提案“待决定”旧文当用户从未批准。
3. scope-index列出初始基线616项、相对初始清单55个产品净变化、实际diff链、preimage和209当前文件。审完TASK120实际变更与直接依赖，不能只看最后8文件，也不要求全仓无关源文件全文。原执行根DocuN/evidence/TASK-120/execution，初始preimage及continuation-01、repair-03、validation-04、finalization-05、continuation-06增量按索引组合；原source.diff很大，先按净变化/函数定位，复用未变实现。初始清单缺项区分新文件与无原件，不能凭null自动声称新建或用后版倒填原基线。
4. 自己的原独审结果DocuN/results/TASK-118-result.md可读，仅作为S与四D的原适用结论、历史控制和Q尚未启用边界。只分析TASK120新变化对原S的传导，未变七族不全面重审。
5. 看下述实际测试方法/fixture/runner，再读原命令日志、请求响应、PG/屏障/回执/as-run/资源记录。工程JSON中的PASS/summary/checkpoint仅作导航，实质依赖方法和原记录；不是文件名含PASS就采纳，也不是整根FAIL就抹掉此前独立已保存子事实。

**不得解码工程结果DocuN/results/TASK-120-result.md、TASK-120-work-decision.md、主控收到候选的自评/裁定段、完整实现聊天/思考或含实现推理的个人记忆。** 工程报告可仅按opaque bytes/hash核封存；候选ZIP如含报告/自评条目同样不解码。允许读批准合同与原始运行事实，不把源fixture中的结论字符串当证明。宿主意外注入或先前接触须如实披露具体范围与影响，不伪称完全未接触。

候选归档DocuN/evidence/TASK-120/execution/continuation-06/final-review-candidate.zip，1936840字节、286条目、SHA256 **3e96aeee40b35e0e0e1a4d42e82452b3cc2a0286fe1ce3ae4bf24219211bed69**。旧七ZIP按原引用保留，不递归重建。唯一最新budget/events及末次071回执为包外附件，不能仅靠包内旧预算判断结束状态。

## 必审代码与证据范围

### 1. Q v2精确逐请求批准与原键恢复

对照119 K1/K2和120原合同，核完整模型payload与typed wire双摘要、source catalog/currentness、goal/answer/memory/history/title/endpoint/provider/thinking/timeout/输出边界的冻结与精确批准；manifest/grant/root/control/current tail/副本和原件身份、单调/日历有效期和错误拒绝契约。批准/等待/claim/dispatch/record各异步与事务边界仍须核相同对象，不能先验合法随后换实际send字节，不能以获批资料顺带授权任意新增模型文本。

核协议、loader、网关最低transport和实际业务请求装配，不只看模型类型校验或高层替身。GET/轮询/重开/同键批准不自动POST、不重新claim或发送；批准未领取与已claim/UNKNOWN严格区分，旧提交成功响应丢失按持久事实恢复。两家provider共同100/25000000、固定三个活动48/28/24与12/7/6合成上限、单笔250000的条件合同不变，候选deepseek-flash不冒称已获实际账户启用。

既有11项全请求反例在execution/finalization-05/的相关实际方法、case/checkpoint及其根/命令原件；副本/残尾/原件缺失等继承链按acceptance-matrix的具体来源读取。实际错误码须命中所测边界，不能拿任意403/409/503充数。原S中的控制日志当前字节/身份/锁内复核不能被Q缓存新路径绕开。

### 2. 持久账、COMMIT丢确认和K2

核原费用/次数/时间/工具账和操作终态主体未被顺手改写；真实PG同全局锁/同事务SUM预扣，两个实际backend竞争99→100且输方零出站的原C12证据仍适用于最终实现。新R03没有金融SQL变化时按实际函数字节/调用关系继承，不为版本名变化要求重刷99笔。

分别核accepted COMMIT、launch claim COMMIT、result COMMIT丢确认的实际持久记录/原键GET/零重复出站与预扣；最新ACK索引在finalization-05/ACK-matrix-PASS.json及三个独立checkpoint，不以一个成功样本代替三路径。

核head/revoke/scope新增/source、最新scope**真实收缩**、memory的shared dispatch释放→独立actor COMMIT→result exclusive重取的实际窗口。007/原件/费用保留，旧结果不能推进变更后的head；未知、迟到、取消不退款/不释放旧slot/不重发。新scope收缩原件在continuation-06/K2-scope-shrink-before.json、COMMIT.json、final-checkpoint.json及对应worker/actor/原命令输出。

原memory根35未即时保存before-financial快照，原trace/COMMIT/007与后续PG核证有明确有限证明范围；独立判断其能否支持当前验收，不能虚构缺失快照，也不因已披露限制默认要求把整套memory重跑。旧scope503已核原命令不存在/原scope_revision1，而另一model已committed/received，核其事务事实而非用503推断回滚。

### 3. 015权限、严格R03及真实scope移除

最新015_activity_scope_delete_permission.sql SHA256 **59b2e556a81a5383e9144a967fa90b5abedb26284d50cbf150db1dd77f34ef0e**；连同schema_profiles/schema_checks/snapshot/q_protocol及完整调用审查。

逐项核先锁/旧R02及静默前提、角色/guard真实检查、失败全事务回滚、仅单表DELETE、profile metadata精确前向变更；多个权限的校验不能漏项，SQL真实语义不可只由普通正例推断。001—014、旧R01/R02冻结常量/合法包、业务列/金融/公开wire/编码保持。表级权限不是行级CAS，按批准的可信应用模型判断，不额外要求本卡没设计的RLS/SECURITY DEFINER平台。

核ACL表级/列级/owner/grantor/grant option/实际成员能力及normal/loading/frozen/restored_readonly形态均精确，snapshot/readonly/restore-loader不获正常DELETE/TRUNCATE/管理权；归一化/投影前必须已验证真实profile/ACL，不能先把多余权限抹成旧基线。新profile选择、错误迁移hash/未知profile/少权多权拒绝、R01/R02读取和R03正常backup/restore/seal都检查证据适用性，不能把ZIP reader说成做过真实R01库恢复，也不凭“旧常量未改”忽略新调用影响。

scope实际缩减的CAS/锁序、仅删差集、版本upsert、不部分提交/不动他活动，和interview_repository新增锁内source current_version/revision校验→source_invalid准确409核对。原根43的500是已记录真实缺陷，修后根44的具体拒绝与真实财务不变须按被测字节采纳，不只看报表。

证据从continuation-06/permission-risk-check.json、062/064/065日志与实际方法、real-profile-ACL-and-guard-PASS.json、scope-exact-actual-ACL.json、actual-scope-shrink-PASS.json、scope-targeted-negatives-PASS.json、old-new-package-compatibility.json、old-R02-and-final-readonly-reconciliation-PASS.json及真实PG/恢复记录核。A的先行风险自检不是独立审计。

### 4. 正式UI与完整DataContext、只读恢复列表

核原键等待/显式继续、owner/view/head/scope和真实namespace/完整DataContext在异步回包前后的边界；localStorage/IDB草稿/意图只含允许业务数据，无授权物或原始返回正文泄入。五入口有限正常UI、练习、head/scope和owner/view按原字节/实际case继承，不用旧bundle证明新守卫。

最终普通dataFetch守卫比较完整DataContext而非仅namespace；hubRead/hubCancel/bootstrap的现有例外必须保持准确，不扩成普通业务响应例外，也不粗暴破坏合法只读查看。核延迟在真正生产响应处，源normal时两个真实GET200/headers/body/can_continue已取回并暂停，随后真实freeze、verified目标/selector和上下文刷新，再释放旧响应；原生fetch完成/业务JSON拒绝与传输取消必须区分。

重点独立核namespace capabilities的**真实已认证请求跨过selector/rebind提交**：原header/新生产body、完整当前身份、bootstrap前进规则与后续正常bootstrap/存储一致，确无setter/body/token注入。不能只因新旧namespace字符串不同就判实际UI链成立。

原件在continuation-06/UI-normal-GET-1/2-root-46.json、UI-complete-DataContext-PASS-root-46.json、UI-namespace-PASS-root-46.json、namespace-capabilities-authenticated-barrier.json、normal-backup-checkpoint.json、normal-restore-verified-checkpoint.json、normal-selector-activation-COMMIT.json、浏览器原始事件/实际bundle响应；按索引读实际fixture与root46日志，不默认复跑浏览器。

额外审查最新repository._transaction在**服务器绑定data_readonly且既有纯读分类**时不构造normal QAuthority的修补：方法分类来源不可客户端伪造，PG readonly guard仍在，每个写/claim/外发分支不可能借读投影逃逸；正常源分支和Q根拒绝未改变。不能只看list返回3项就排除写权回归。根50真实API及写拒绝、根51只读UI/金融原件按字节对照。

最终正式bundle：JS frontend/dist/assets/index-GSKO5ska.js，SHA256 **50b035784109bb04b444ffedf48186d14b9042a6139f8b22df59814d6a81b285**；四资产以formal-bundle-identities.json为准，真实JS/CSS加载与磁盘四项一致不是同一声明。根46与最终产品仅差后续sealed-reader修补；独立核该分支差异和50/51补证能否封闭影响，根51与最终一致不能自动覆盖46全部异步分支。fixture后改同样按as-run分层，原067整体FAIL保留其独立R01子例，068补证须核方法/进入上下文后的真实行为。

### 5. 执行控制、资源与证据完整性

按原采用与每次前向permit对应真实时段核时间/次数/对象，不能套最后宽上限追认旧越界，也不能用早期小上限误判后续获准批。新06实际接收登记/首次读卡顺序与3秒时钟边界披露须基于原receipt定性，未知时间明确unknown，不把日历/审批排队当CPU工作，也不把未知预留清零。

唯一工程账execution/budget.json/events.jsonl：roots51/64、PGstart52/64、API55/96、Browser14/16、build5/8、Native64/128、HTTP1459/10000、对象/卷2/2、create尝试各2/2；原失败125条、TASK117旧81另存。当前wall在071退出后为50243.003003/57600、持有2667.078295/21600；报告50299.862003含最后60秒预留，以实测071=3.141替换，不变其他unknown。工程账active_root/command空，不因此认历史全过程合规。

原源精确CID b89522070d4b64fc67efed810852ccc21948058f154bf4fa1889f4d8d69a102f/卷retrolume-task120-qprep-data，恢复目标CID 4eb5be54b713e5412be702e27684d98d2b7de92a77f9085b3ce84a5f4b124332/name retrolume-task120-scopeui-ro1/同名-data卷；同原完整镜像sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f、1CPU/512MiB/pids128/restart=no、loopback55480/55481、API18120、无host bind。原四库不迁移，唯一新增source retrolume_task120_scope_ui_final、目标retrolume_task120_scopeui_ro、工厂标签/登记/创建前计数与创建后实际CID检查，不要求新目标伪装旧源标签。

070在2026-10-20T23:08:53.727173+08:00的最终停止记录为622组PID/birth、135Job、两CID Running=false/Pid0与三端口无监听；071只文件保存exit0/tree_empty。核该原时点的StopProof及后续无业务再起，**本卡不要运行Docker/进程/端口探针重验现在状态**。旧对象/数据/失败全保留，无批删、prune/drop、绕审批或真实provider/费用/preview/Git操作。

财务按实例分开：旧flow25/6250000、budget01 100/25000000、budget02 8/2000000、matrix-final23/5750000不变；新源5/1250000，恢复副本5/1250000只是备份时点历史，不相加作新预算。核实际PG新连接/生产只读记录、R=0、007与原件摘要、原UNKNOWN事件子序列、未领取/已领取状态，不能用Q日志当唯一余额证明。

## 验证方式、可写范围与投入

只读上述实际源/测试/合同/原证据和必要直接依赖。允许自写并执行只用stdlib的有限文件hash、ZIP目录/条目身份、diff/记录对照脚本，不导入产品/测试模块，不执行归档runner或脚本正文。必要语义无法从本地确认时可有限查至多6页相应版本官方一手文档，记录实际URL/适用版本；不扩为全网调研。

**本卡compile/unittest/PG/Docker/API/Windows Job/浏览器/build/真实模型/网络业务运行额度全部0。** 不读.runtime、凭据/vault/真实配置、不安装/联网下载、不作Git写。当前已有证据充分则直接复用；如存在具体必须动态补证的缺口，给最小操作/对象/期望和现有证据为何不足，交回主控，不自动创建运行预算，也不默认全套复跑。

仅写D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/和统一结果D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-121-result.md；输入根orchestration-20261021与所有工程原件只读。不得修改产品/测试/迁移/dist/旧证据/工程账/任务卡/公共库/DocuS，不直接修缺陷。

本次独审从首次实际接收起至多8小时日历，工具实际wall累计至多1800秒、单条文件元数据命令至多60秒；真实运行仍0。这是审计失控兜底而非用满目标，按覆盖完成即停。记录真实命令/退出码/投入/失败；人工实际耗时若无法核得写unknown，不虚构模型token预算。旧工程全部投入/125失败/81历史保持，不因新TASK、窗口或模型清零。

## 停止、结论与回传

当前范围一次审完并合并所有已确定问题，不逐小项回传或边审边修。发现明确数据破坏/越权先留证报告；其余独立部分继续完成本范围审查。输入漂移暂停相关对象，关键上下文缺失、超范围或8h/1800工具wall到门则保存具体缺口；不要用无关Must阻塞无关审阅，也不要自行把真实Must缺口降成建议。

三轴各给通过/有条件通过/不通过/证据不足及适用快照。区分确定产品缺陷、条件风险、证据缺口和非阻断观察，给出严重度、文件/函数/行、可达触发、影响、最小修正或补证。历史执行违规原样登记，与当前代码/证据分层，不用技术通过洗控制历史。说明TASK120有限工程切片是否具备交主控关闭条件，以及真实Q尚待的原有前置；不代填主控最终验收，不宣告STEP018整体/019/020/M1/项目/发布或Q启用通过。

统一结果保存DocuN/results/TASK-121-result.md：先一句结论和三轴/问题摘要，再给独立性、版本/hash/实际阅读范围、C01—C15对应证据/继承与限制、必要问题、执行控制重建、未验证和最小下一步。证据中附可独立复核的hash/差异/记录引用，不重新复制大批原件。确认真实保存可读后，仅回一句话结论和可点击完整绝对路径，供用户带回主控。

后续若需修正由主控合并交原TASK120工程窗口；本卡后续增量复核沿用原121及本审计窗口，只核修正和直接影响，不重启本轮完整审计。除人工转卡/带回结果外无需用户额外操作或再次批准已授权只读审查。共享状态/编号/CHG由主控统一维护。
