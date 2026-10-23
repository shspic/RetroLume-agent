# TASK-120 / R-114 — 集中修复03：锁分类、未知态与剩余业务闭环（当前有效）

## 目标、接收者与交付

接收Agent：A+增强工程，继续TASK120原TASK119/117工程窗口，单一执行者，原运行已停止。真实客户端/模型照实登记，不因标签重新审已完工作；不委派、不启动独审、不新建TASK。

交付一个稳定完整的Q v2零外发工程候选：合并修复本次确定路径和同链夹具问题，补两域query→model→007/领域提交、旧learning/HTML、已选记忆、剩余权限/ACK/K2与五入口正式UI；普通修正卡内完成，统一回传。先定位并修正根因，再验证，不直接重开旧失败整批。以下附旧完整合同，未明确修订的A—D/Must/文件边界均继续有效。

本卡不是独立审计，不签STEP018整体/019/020/M1/项目或真实Q。Q继续冻结，真实provider、实际费用、preview、Git新增全0。未来100次/25元并未在本卡启用，不再要求用户提供key、SQL或释放内存。

## 项目、规则、依据与输入

根D:/shspic/project_NO3_RetroLume-agent；入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。task_model，锁定V4.0/公共AGENTS CHG-0003；公共只读根D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，DocuS/AGENTS.MD、WORK.MD适用task_model/核证/委派/预算/审计章节、task_model/TASK_TEMPLATE.md及prompts/07_开发执行循环.md；七指纹以DocuN/evidence/v4-migration-20260930/rules-snapshot.json为准，不自动采用新版。同窗已读未变材料复用。

当前需求v1.4、架构v1.49、执行动态v2.77；STEP018和原120关联继续。用户已批准119增量，主控在同一实施/零外发目标内前向续发附条件资源许可，没有新增真实费用、持久模型或公开权限。

按序只读变化及直接依赖：

1. D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-120-work-decision.md置顶03及同目录TASK-120-result.md置顶“断点纠正02”；不覆盖首轮/续作历史。
2. D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/orchestration-repair03-20261019/permit.json、input-verification.json。实际旧账为execution/budget.json、events.jsonl，当前16/16根、active_root/command空。收到本卡后才追加permit_history与caps，主控没有代改工程账，不追认过去动作。
3. execution/continuation-02/final-review-index.json、final-file-identities.json、final-stop-proof.json、retained-unknown-witness.json、fixture.diff、command-039/040/041.receipt.json，root15-diagnosis.json；root-16-c02-core-result.json及三份root-16-batch-06-ui-*-proof.json、root-16-batch-02-failure.json。已有失败和原件直接复用，不先重现。
4. backend/app/learning/teaching_adapter.py、activities/teaching_repository.py的_teaching_read_snapshot/read_teaching_command、activities/repository.py的_transaction、data_exit/q_store.py的method_name/is_read_method/async_policy、capabilities/q_gateway.py共享临界段；interview_repository.py的accept/abandon/goal；preview/repository.py的parent资格与learning/service.py的原输入/父槽守卫；相关最终夹具和冻结TASK116输入。

## 已定位问题与一次合并修正

### P1：教学只读调用被误分类为写操作

确定的代码链：q_gateway.call_with_policy先进入shared policy；gateway再调用validate_teaching_request；v2/v3路径调用read_teaching_command→_teaching_read_snapshot；_transaction用method_name得到“_teaching_read_snapshot”。现is_read_method只匹配read_/list_/inspect_/find_/q_snapshot及少量精确名称，漏该私有只读方法，导致申请exclusive policy；async_policy在继承shared时明确抛q_policy_upgrade_forbidden；adapter的except Exception统一返回teaching_validation_unavailable。这是可从源码确定的冲突路径，本次worker日志只录统一错误码，**尚不能宣称原运行已采到内部异常或唯一根因**。

按只读语义修正这条精确路径及实际直接受影响的同类读取；不得泛化为“所有下划线方法都是读”、对所有transaction跳过policy、放开写锁升级或移除结果事务排他锁。保留K2发送共享锁先释放、结果再排他policy→MutationGate→PG的顺序。

用最小定向检查证明真实方法闭包的分类/实际shared嵌套读取可达，且shared内真实写操作仍在SQL前被拒；覆盖无记忆的teaching.v3及有记忆v2/v3适用分支。替身只证明锁/控制流，不冒充PG事务；之后用真实PG/SUP补模型提交。若另有内部异常，按下面安全诊断捕获后针对性修复，不能猜字段或放宽守卫。

### P2：历史UNKNOWN并不会因新goal自动解除

interview.accept检查全部历史model UNKNOWN，包括obsolete项，先前主控“只建新goal即可”的安排不充分。原键430a4e36-08e1-411f-a73e-097506a6278b及新教学键3b561488-07b7-4d6d-8b98-05e793c96749绝不重发；原A1键1f5c659f-4a5a-4fee-bfbe-3f245eb5bc7e也永久保留。

准许在精确停止/当前PG回读后，对已停止的上述A2面试及A3教学实验命令通过既有本地abandon接口显式结束业务pending；须保存前后状态、真实新head/父和原Q claim/operation/预留原样保留的证据。abandon不释放旧semantic slot、不证明未送、不退款；不能SQL改unknown为not_sent/删除历史/清余额。随后才按原生产goal/版本规则创建合法新父，核所有历史unknown/未决operation/owner，不只看head。若仍被生产规则拒绝，保留准确原因，不换key撞旧槽。

### F1—F3：已知夹具前提一次收敛

- observer必须在正常TESTONLY应用装配前安装原最低传输替身；不能靠重跑C12隐式安装，也不能把外部transport误当合成。
- retrieval source_index/query可合法命中terminal/received缓存，按原键、原终态和真实结果资格核证继承；不一律索取pending approval，不二发已领取/未知请求。冷准备、合法缓存、部分接续三种输入状态应可区分，不弱化业务断言。
- creation-memory及其他已保存JSON显式UTF-8读取。budget02已部分初始化，不当空库；复用真实身份、root/grant、已有roster/来源/原保存业务键，按生产MemoryService和create_activity(memory_selection=...)补创建时选择。禁止重建库、重绑旧活动、延长有效期或生成任意记忆文字。

最终041只证明语法/冻结memory解码/schema和停机，不能算这些修后PG已通过；保留修前/as-run与新字节差异。

### P3：HTML/legacy的409先拿确切拒绝原因

原409未记录安全错误码，禁止猜验签或父域。夹具应保留有限结构的status、detail/error层code、terminal disposition和关联业务键/operation；不输出DSN、令牌、签名或任意异常正文。核原first成果的实际kind/版本/资格/segment，COMMIT不自动代表它是合法HTML answer父；核legacy followup的原规范输入、父资格和单槽。若须先用既有合法followup形成answer，就完成该真实步骤再生成HTML，不改生产parent/业务提示使不合格父通过。已存在正常HTML验签与九函数EOL修补直接继承，不再应用012/改schema profile，不启preview。

## 诊断、修复与运行次序

先离线完成上述源/夹具对账和已知修正，保存一张有限“当前真实状态→合法动作→预期结果→原证据/新证据”表，覆盖所有剩余C项。每个会消耗新Q claim的正例，先核全链的父、未知态、当前ness与结果类型；不能只核accept，再到worker才发现同链静态不兼容。

若旧原件仍不足以绑定教学异常或HTML/legacy拒绝，允许**至多一个只读诊断根**，总时长420秒含末120秒清场；仅原PG/必要API和冻结请求复核，不启Browser/业务SUP，不调用admit/mark/record/claim/真实传输，不POST新业务。可在独立测试进程对原validator捕获目标模块的异常事件，记录类型、DataError.code/SQLSTATE、相对文件/函数/行与SQL模板hash，禁止原始异常字符串/连接信息。保持失败关闭，不把捕获改为成功。原始症状已有充分绑定时跳过该根，不为凑流程再诊断。

真实PG/SUP及UI前必须先有：上述同链修正的有限差异、锁读/写反例及保存回执状态/UTF-8定向检查、UNKNOWN本地处理方案和HTML父/错误码核对结果、完整有限计划与预留清场时间。诊断不能收敛则不启业务正例，完成独立可交付部分后停止并带准确缺口；不再用UI循环定位worker内部异常。

修正稳定后按正常PG/HTTP/SUP→剩余ACK/K2/权限反例→最终UI推进。正常教学/面试/legacy/HTML及已选记忆正例先成，再做会失效scope/source/memory/head/revoke的破坏性竞态；保存正例身份，避免后例先破坏前例前置。GET仍无副作用、批准仍本机operator精确全文、POST继续仍原键。三种ACK、foreign-instance/artifact/log/readonly等只补原矩阵实际未足项，不因保存了脚本就通过。

最终UI只有后端正例已闭合才进入相应模式；独立模式可单独推进。浏览器对已提交父只读核证后继承，不为重复证明而再model。核正式JS/CSS响应hash及五入口的等待/刷新仅GET/批准/同键显式继续、owner/view/head/scope/namespace/DataContext晚到围栏。旧三浏览器FAIL不改绿，加载hash子事实直接继承，产品未变不重复build；前端产品实际改变才绑定新正式build。

不在PG持有时等待聊天投下一批。每根启动前冻结有限阶段、依赖、总时长和as-run；独立子项不被无关失败阻断，但同问题两次有依据修正仍失败/前提推翻即停该问题，不机械重试。普通修正卡内合并，充分即停。

## 原证据复用与范围

C12原共同99→100双backend同锁、达限双provider拒绝、root12/14同库重开100/25000000和三R0不重跑；旧R300已核销不再处理。旧learning first COMMIT、既有embedding、九函数EOL与普通角色指纹、未变S有限验收直接继承。

本轮产品增量0属断点事实，未来本卡修复允许原120批准产品边界中的teaching_adapter/teaching读取、q_store精确读分类、同链Q/业务薄接线与必要测试；不得借此改金融主模型、历史原件、001—014、正常profile、SUP/Job/时钟、依赖锁或用户配置。公开接口/持久模型/权限模型若需改变，完成不受阻部分后交具体最小差异，不自行扩大。原完整允许/禁止文件附后，正式DocuS/公共库与共享CHG仅主控写。

## 附条件资源许可与停止

前向许可TASK-120-Q-PREP-REPAIR-03-20261019，只有收到本完整卡和permit.json才登记；原16根全部已用且保持，不能重开旧根。

| 项 | 返回累计 | 新累计cap | 前向新增 |
|---|---:|---:|---:|
| 根 | 16 | 20 | 4 |
| PG启动 | 15 | 20 | 原cap16→20，增加4 |
| API启动 | 11 | 20 | 原cap16→20，增加4 |
| Browser/build | 3/4 | 8/6 | 0 |
| Native/HTTP | 13/240 | 48/5000 | 0 |
| 命令wall保守秒 | 17789.126332 | 25200 | 原cap21600增加3600 |
| 持有并集秒 | 1258.061295 | 14400 | 0 |

四余根是同一完整修复目标的上限，非必须用满：至多一根只读诊断，其余仅用于通过前置后的正常闭环和剩余验证。一个完整正例仍在同一确定前置处失败时，不继续启动三个UI复制该失败。57失败记录及原117的81历史、所有旧投入/两个7200未知预留保留，不当独立缺陷数；旧原首点/所有失败/未知账不清零。新计时按真实起止/区间，不机械另加固定7200，不将未计量记0。

每正常根最多1800秒含末120清场，测试/构建子批300、元数据单批60；受总wall/持有/有效期最短门限制。新根从17、命令在041之后续号；038仍未执行，039—041已真实成功，自动审批容量目前已恢复，不继续以旧容量错误当阻塞，不换通道绕过任何新拦截。

唯一CID b89522070d4b64fc67efed810852ccc21948058f154bf4fa1889f4d8d69a102f，name retrolume-task120-qprep-pg1，volume retrolume-task120-qprep-data，image sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f；原permit标签TASK-120-Q-PREP-IMPLEMENTATION-20261018保持。1CPU/512MiB/pids128/restart=no/无host bind，PG127.0.0.1:55480/API18120；仅原flow/budget01/budget02，不新增/替补容器/卷/第四库或活动。失踪/身份不符则停相关层，不查改旧六资源。

原首工具2026-10-18T08:41:08.5687758Z、原96h截止2026-10-22T08:41:08.5687758Z不延长；最后1800秒仅保存。TESTONLY flow/budget02的2026-10-19T12:19:22.457756Z及budget01的12:33:23.767900Z、活动期限仍须实际核较早门，不刷grant/换实例恢复旧权利。到期只停止依赖动作并保存，不用本卡延长权限。

PG/API最低512MiB、Browser768MiB、约2秒采样连续两次<256精确清场保持；不要求用户再释放内存。本轮最低835289088 bytes且无压力事件，不能再把已发生业务失败归内存。每次实际启动尝试照账，包括未ready。

## 收尾、成果、审计与回传

原041在2026-10-19T05:54:10Z已核120 PID/birth、58 Job、精确CID Running=false/Pid0与两端口无监听，并另有041自身tree_empty/exit0；这仅是当时时点，不冒充主控实时查询。新启动前/结束后均精确核身份/停止，最后先停Browser/API/业务树再停CID，保存全部维度；保留容器、卷、数据，不drop/truncate/prune/批删。

唯一工程账仍D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/execution/budget.json与events.jsonl；新增证据execution/repair-03/，旧根/失败/as-run/报告和ZIP不可覆盖。完整结果仍D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-120-result.md，新轮置顶且旧全文原字节保留。输出锁分类根因/修复/反例、业务未知处理/原领取不二发证明、C01—C15/原矩阵逐项证据/未跑、最终源码/fixture/dist/as-run身份、准确累计账和精确StopProof。

稳定完整后主控再安排原118独立归属集中增强终审，不在本卡自审自签，不把诊断当独立审计；未成则带真实失败与最小剩余缺口，不以“语法通过/已保存”代替完成。无需用户新决定；用户仅人工转交本同号完整卡。保存复读后只回一句真实结论与可点击绝对结果路径。

---

# 以下为先前合同，历史原字节保留；与本次明确修订冲突时以上文为准

