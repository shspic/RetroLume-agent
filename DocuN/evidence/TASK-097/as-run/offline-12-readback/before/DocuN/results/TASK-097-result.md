# TASK-097 / R-091 G7首次学习与资料证据结果

候选产品实现已保存，真实首次学习、引用回查、显式续问与冷读取恢复有通过证据；卡内验证部分完成，8次集成入口及8次容器start已耗尽，最终UI反例与最终bundle动态复验未完成，不能提交为G7完整稳定成果或独立终审通过。

## 1. 实际用户流程与交付导航

在完整且显式启用的本地学习配置下，用户选择活动范围内就绪TXT/MD或已核对PDF，零费新建活动，输入目标并确认范围/用途/限额，点击“开始学习”；一次受控调用可保存答案、必要追问、证据不足或来源冲突。点击引用可查看同一版本的真实行段/PDF物理页及用户补充身份；从当前学习成果显式续问会使用新的操作和原G4父凭证。刷新和切换读取服务器持久正文，不自动调用。

这个流程在本卡合成资料、合成模型传输和真实PG/Windows/浏览器中走通到首次/续问；另一次新应用、新浏览器上下文冷读取了同一真实持久成果。browser-07的整页刷新定位器失败、browser-08后续资源观察Promise失败均保留，不能把这两段说成完整浏览器套件通过。最终修正的意图核对和迟到保护尚未浏览器复验。

- [产品使用说明](D:/shspic/project_NO3_RetroLume-agent/README.md)：真实启动配置、首次/续问/引用/恢复、坏配置和词项限制。
- [实施前冻结合同](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097/implementation-contract.md)：业务接口、信任、典型正常/追问/不足/冲突/伪引用/失效/异文/丢回执样例及预期。
- [实施差异与复用边界](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097/implementation-notes.md)：实际DTO/profile、后补修正和not_run。
- [原始证据导航](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097/evidence-navigation.md)：失败原文、每批命令、PG/进程/浏览器原件、截图和资源账。
- [T01—T18逐项矩阵](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097/acceptance-matrix.md)：每项方法、预期/实际、被测版本和证据路径。

## 2. A—D实际差异

A已完成。实读函数级输入后，在产品修改前冻结短合同；首次冻结距实际开工436.804秒，计入主动总额，未用另一个设计卡或逐阶段人工确认。根入口/锁定公共规则指纹7项相符；给定索引71项初始匹配。未读取其他模式、私有配置/真实密钥/用户DSN，也未重新审计095/096。

B候选实现已保存。新增[learning目录](D:/shspic/project_NO3_RetroLume-agent/backend/app/learning/contracts.py)的contracts、prompt、evidence、adapter、service、api及初始化模块；活动API/capabilities给出学习可用性，repository仅追加两个单SELECT只读助手。严格内部profile经已有one_call请求进入真实launcher/SUP/worker/Job/gateway；gateway在admit前复核，在record前完成输出规范化。目标、目录、正文和received原子同事务保存，没有新表/字段/迁移或第二笔目录写入。原写/锁/恢复及停止主体复用。

C候选实现已保存。活动工作区增加目标确认、首次入口、四类结构化成果、按版本引用、PDF物理页薄复用及显式学习续问。台账先存业务意图再POST；缺配置关闭新入口，损坏台账阻止依赖恢复的新写动作，读/取消仍可用。新增输入核对匹配与活动切换保护；最后两处仅离线/构建，不声称UI验证完成。React文本显示不执行模型HTML/脚本；README已写实际启动与能力限制。

D部分完成。纯函数/配置/协议/受控gateway检查、真实PG与HTTP、15次真实Windows监督会话、3次实际浏览器启动均留原始证据。集成夹具发生多次不同事实/观察错误，普通修正后只复验受影响或未执行部分；8个runner最终整体都exit=1。资源已准确收尾，未为了绿色汇总再启动第9批。

本卡没有派子Agent、自签独立审计、写DocuS正式状态、占用新TASK/R/DEF/OPT/CHG编号、修改经验库、远程Git动作或发布。

## 3. TASK、基线、身份和关联范围

- TASK-097，结果R-091，初次执行。建议状态为“候选产品实现已保存，卡内验证部分完成，运行入口上限已触发”。不写“候选实现与卡内验证完成”。
- 实际根目录D:/shspic/project_NO3_RetroLume-agent；入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。模式task_model，V4.0/公共AGENTS CHG-0003，锁定指纹来自DocuN/evidence/v4-migration-20260930/rules-snapshot.json。
- 输入基线：最终需求v1.1、架构v0.73、执行v1.95；G6已限定关闭，G7未验收。给定input-snapshot SHA256为91110dbd7563b1a170f5605cb3fc42b164dd2224ec8db327f3c8e9add5f2605c。初始71对象匹配，当前授权变化见post-index-check，不把旧源hash当当前通过。
- 实际身份：Codex desktop内Codex，系统标识基于GPT-6；客户端精确模型identifier不可读。A+为用户指定资源标签，不伪称具体增强型号。PowerShell，Windows AMD64，项目Python 3.12.10；Node/npm及依赖为现有安装，无安装或升级。工具为本地文件/命令、既有Playwright、Docker/psql与真实Windows进程接口；没有外部provider调用。
- 关联STEP-006/007/008及STEP-009意图澄清子集；FR-002/003/004/012、NFR-001/002/003/004、DR-001/003、SEC-001/002、CON-001，MOD-001/003/004/005/006/007/008、FLOW-002/003/005、API-002/004/006、DATA-002/003/005/007。这些关联不等于全STEP关闭。
- 前置G3/G4/D3/G5/G6有效边界保留。旧G6九场景25check及原浏览器整体FAIL、旧095失败/超限/未知主动时间不更改、不借余量。

## 4. 实际接口、字段和信任

POST /api/activities/{activity_id}/learning/first仅接受business_key、goal、confirmed；续问POST /api/activities/{activity_id}/learning/followups仅接受business_key、parent_operation_id、question、confirmed。business_key为规范UUID，confirmed必须是真布尔true，目标/问题去首尾空白，最多1024字符及4096 UTF-8字节。非法/多余字段、空输入和前置不足在claim前关闭。

GET /api/activities/{activity_id}/learning/intents/{business_key}?action=first或followup读取已存在业务槽位；GET /api/activities/{activity_id}/learning/operations/{operation_id}/citations/{citation_id}按持久目录回查有限原文。旧四类读、旧continuations、取消路由保持职责。活动allow_own_origin可同源写，materials/pdf默认来源认证未改。

private LearningProfile版本为learning.v1，包含服务端活动范围、版本/revision、目标/问题、目录、输出规则及必要父消费摘要/低信任历史。public StoredProfile没有父payload摘要、history或消费凭证。持久通用JSON正文的value包括profile、action、activity_id、request_sha256、goal/question、scope_revision、sources、parent_operation_id、max_output_tokens、retrieval_mode、catalog、result及固定能力限制。模型仅能给kind/message/segments/questions，不能给服务端goal、权限、模式、目录或verified标志。

result.kind为answer/clarification/no_evidence/conflict；answer段必须引用允许的lc_ ID，conflict至少两不同来源，非法JSON、未知字段、伪ID、篡改版本/hash/位置、过长及无效结构不能成为成功正文。已收到非法输出按received失败，无正文；真正提交未确认仍UNKNOWN保留预留。引用存在/位置与语义支持分开。

首次operation_id为learn-first-v1.加规范摘要，稳定首槽不依赖客户端UUID；续问为learn-next-v1.UUID.摘要。规范摘要绑定目标/问题、活动scope/来源快照、profile/输出及父身份。应用预查后由现有租约独占，worker在取得租约后再查首槽，避免真竞争第二次send。同请求返回持久事实，异文409；UNKNOWN/NOT_SENT/已知非法正文不自动换键或重发。

来源revision接受0..2147483647，使用仓储发布真实值；本卡真实PG正常发布为1，纯函数覆盖0及其他值。最多10源/5 MiB原件、50物理页每PDF、100文本单元、512片段、24查询词项、top8、证据12000字符/24000 UTF-8字节。先过滤资格再读取/排名，超限要求缩小范围。当前为terms.v1，未接Embedding/向量融合，不给召回质量百分比。

新增learning配置默认关闭，只允许profile=learning.v1、max_output_tokens=1..256且不超过旧继续/L1/L2上限。示例值0不能激活；原服务端预算/预扣/停止/退款权威不变，工具集合为空，外部API不开放服务URL/system/工具/预算/执行身份。原protocol3/4精确外层与无profile行为保持；未知profile拒绝，不降级。

## 5. Pre/post、有限diff和构建绑定

初始40个直接目标原件在[pre-manifest](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097/pre-manifest.json)及pre/；原dist4件在第一离线与首次build前已保存，另列[pre-dist-manifest](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097/pre-dist-manifest.json)，不回写历史pre导航。

最终111个必要文件实字节及hash在[post-manifest](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097/post-manifest.json)与final/files/；49个产品/测试/产物变化在[changes](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097/changes.json)，有限源码/测试差异在[limited.diff](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097/limited.diff)。现有用户未提交修改以真实pre保存为准，不以Git提交为基线。

repository字节前缀false是末尾既有只读read_operation的CRLF转LF；归一行尾后全部旧正文为当前前缀，原ActivitySpec/Lease及所有写/锁/恢复未改。11个停止/传输/工具/认证冻结模块字节相同，001—008迁移、materials/pdf写/认证、local_session、依赖锁及正式DocuS未改，见[core-freeze-check](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097/core-freeze-check.json)。这项静态事实不替代动态测试。

最后正式构建为build-05-complete-inputs，源模板/tsconfig/package/lock/全部src在构建前保存，npm build原始输出、退出码、耗时及产物hash见[build-binding](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097/build-binding.json)。五次build均exit=0，最后一次针对前置模板/配置原件遗漏补起源链；产品没有再变。Vite有大于500kB chunk提示，未因本卡改分包或宣称性能验收。

最终四类产物：index.html SHA256=cd3fa8d962f33d4a348332bfc93bbe3edf0d8869c3fb32d0c55e4c58394f7bcf；assets/index-CYYBTgCl.js SHA256=757d763b220025da1980581d0bf229e63c6839d3dc241efc7de6a8d82e4c35df；assets/index-C8N4OxWs.css SHA256=3a129b535b475ca1d9262480da2662a2964eb5361486faf648dbf230f3d5283c；assets/pdf.worker.min-Dswkl-cV.mjs SHA256=8ab0e5e30031b4a06ecfddd5ae9562f0227f830ee7ec9ed1a968b134243d2386。04与05输出相同。

真实浏览器服务的是build-02的index-J2uHZoHy.js及对应HTML，07实际取得四类字节并比hash。最终bundle未浏览器服务。每个资源入口都有actual as-run及运行后指纹；实际worker导入时摘要核到这些原件。最后变更的客户端核对与gateway额外守卫不能被早期动态证据无条件覆盖，见[evidence-applicability](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097/evidence-applicability.json)。

## 6. T01—T18结果

方法、完整预期、证据文件及被测版本详见逐项矩阵；以下状态均限实际样例层级。

- T01：中英TXT/MD、PDF/补充、仓储revision/位置/hash通过纯函数、真实PG和正常浏览器；真实OCR质量不在内。
- T02：未选近似源/替换/revision失效/未核PDF及admit前范围反例成立；真实PG删除来源专例未执行，部分完成。
- T03：输入/歧义/零候选前置提示及真实clarification/no_evidence/conflict原子结果成立；不代表供应商语义质量。
- T04：缺/坏配置、请求413/零预扣、旧层级通过；全部数值/额度上界及缺配UI未逐项动态覆盖，部分完成。
- T05：PG同xmin、真实首次/续问及冷持久读取成立；最终额外守卫后完整链未重验，版本限定。
- T06：伪/非法结构、版本/hash/位置纯反例和received失败无正文成立；固定支持性正反句独立对照，未签语义质量。
- T07：UTF-8/CRLF/行段、PDF物理页、补充/XSS文本显示成立；替换后后端拒绝成立、对应UI专例未完成。
- T08：两真实SUP异UUID竞争仅1 send，同槽同文读取/异文409成立；不同目标并发专例未执行。
- T09：提交后ack丢失可持久读、真实UNKNOWN/NOT_SENT和同键零新增send成立；完整UI丢响应/重试/放弃组合未完成。
- T10：真首次父成果→学习续问及旧普通model真父→继续成立；tool凭证仅直接协议及冻结主体复用，未新做真实Windows专例。
- T11：真实PG send后替换/取消与Windows阻塞取消保留旧成果/账面成立；专门Job硬停未执行。
- T12：浏览器先存后发、各1 POST、冷恢复0 POST及真实意图纯函数成立；最终匹配/迟到修正和损坏/核对/放弃组合UI未复验。
- T13：旧D2主体和有限接受结论复用；新引用正常点击成立，慢回包/切换/隐藏/卸载专例未完成。
- T14：5个真实PG方法、3个HTTP方法在各对应批成立，6类读取每次1 SELECT、列表不取正文；保留02整体failure/error和后续修正原件。
- T15：15实际SUP启动、15真实Job关闭、14份SessionOutcome；一旧普通调用观察器缺件如实披露。专门硬停与最终完整正向未执行。
- T16：07真实浏览器6 check及08冷持久读1 check成立；两批整体FAIL，后续UI反例与最终bundle未动态通过。
- T17：原3/4直接协议、无profile旧业务、严格profile/混用拒绝及敏感正文边界成立；最终额外无profile保留命名空间拒绝仅离线验证。
- T18：真实pre/post/as-run/diff/失败/构建/资源账已保存；最终bundle→浏览器链和一个旧调用SessionOutcome有缺口，部分完成。

没有将skip、未执行、fixture误报或整体FAIL改为PASS；没有执行真实provider或付费，所以不会宣称真实供应商总体质量已成立。

## 7. 真实命令、退出码与失败历史

命令全文来自attempt-ledger、各as-run/manifest及run.json，凭据不在argv。命令族如下，均用项目现有工具，没有安装：

```text
backend/.venv/Scripts/python.exe -B backend/tests/fixtures/task097/offline.py <本卡导入记录> <定向test方法>
backend/.venv/Scripts/python.exe -B backend/tests/fixtures/task097/preflight.py
node frontend/tests/task097-intents.mjs
cmd.exe /d /c npm.cmd --prefix frontend run build
backend/.venv/Scripts/python.exe -B backend/tests/fixtures/task097/resource_runner.py pg|business|browser
```

每个集成入口始末及command真实内容在其as-run manifest，不让上述简写替代复现参数。角色口令只有stdin/短期内存/子进程环境，报告无口令或用户凭据。

1. 01 PG：exit=1，业务10.125秒/清理0.656秒；fixture无用导入+Windows Selector selfpipe被守卫误拒。库/schema正确，测试未成立。后续仅定向清理自有三源。
2. 02 PG：exit=1，11.516/0.578秒；5 PG及2 HTTP方法成立，末HTTP错猜201导致failure并有自有FK清理error，下一批定向修复。
3. 03 business：exit=1，9.328/0.656秒；受影响原子PG复验成立，HTTP错猜顶层activity_id导致KeyError，无SUP。
4. 04 business：exit=1，10.391/0.640秒；HTTP修正成立、真实首/续2 SUP/2 send成立，后续夹具错写旧/continue路由404。
5. 05 business：exit=1，89.094/0.578秒；11 SUP/10合成send入口，多项真并发/未知/非法/结构结果/旧继续/取消成立；浏览器driver JS变量声明错误在Chromium前退出。
6. 06 browser：exit=1，41.484/0.594秒；browser1，零费新建实际成功，但观察文案错误超时，首次未调用。
7. 07 browser：exit=1，41.890/0.610秒；browser1/SUP2，六个主链check成立，刷新后用UUID定位来源标题列表超时，保留真结果。
8. 08 browser：exit=1，12.484/0.625秒；browser1/SUP0，冷读取真首/续成立，后续资源response.body观察Promise错误退出，UI其余反例及硬停未执行。

首次离线子程序30方法exit=0，但外层展示有GBK输出错误；原子结果公开projection、strict confirmed、命名空间防降级及客户端输入核对补强的测试版本分别保留。最初文件核对命令也发生一次输出编码失败，不当作产品测试失败或忽略其投入。所有失败原文、as-run与对应修正diff保存，未用新汇总遮盖。

有据普通修复已保存：真实DTO/路由/文案/标题定位、Selector自管selfpipe、观察器Promise保护、明确自有FK登记及清理、公开profile不含父消费摘要、profile命名空间/严格确认、目标核对与迟到保护。最后几项动态缺口未重跑，因为入口已达上限，不用编译宣称行为通过。

## 8. 累计投入、资源收尾和剩余

开工时刻为2026-10-02 10:43:52.161 +08:00；原execution-ledger的10:48:30登记值保留，不能缩短投入。到最后保存核查，主动墙钟保守上界12347.906秒，剩余16452.094秒；该上界包含等待/阅读/写文，不虚构精确键盘主动时长。

离线检查/构建实测51.031秒，另为最初未独立计时的证据finalize/编码核对保守计60秒，累计按111.031秒，占2400秒许可，剩余2288.969秒。业务226.312/3600秒，剩3373.688；清理4.937/600秒，剩595.063。最大单批业务89.094秒、小于900秒，最大清理0.656秒、小于120秒，纯离线批均小于60秒。异常预检/abort包含在对应批业务计时。

集成runner入口8/8、精确container start8/8、真实Windows监督15/16；浏览器实际启动3/4，driver保守尝试4，05在Chromium前失败单列。入口/start没有余量；其他剩余秒数或名义监督余量不授权继续集成。旧095的入口10/start9/claim10/保守监督14、业务279.677秒/清理24.592秒及旧未知不重记、不借用。

唯一容器CID e49d3acc3c1be13d670af68bca2b082fea4faeeb9b9babe69df7f1d3941696a4，名retrolume-task-088-g3-w1，镜像sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f，卷retrolume-task-088-g3-w1-data，127.0.0.1:55441、1 CPU/512MiB/pids128。首次完整inspect在内存白名单核身份/权限/停止/占用，不显示Env，不用失败的Go模板投影。

只新建retrolume_task097_g7库和retrolume_task097_synth角色，管理路径使用已知合成管理角色；业务角色非superuser/非越权成员，仅097必要权限。原001—008只在空097库顺序应用并连目标库验证，无新DDL迁移、无旧库/用户库动作。旧095/092/088库不改。

所有8批finally物理收尾成功，最后只读核查见[resources-final](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097/resources-final.json)：Running=false、Pid=0，本卡应用/driver/SUP及现存后代树零，18097/15197/55441释放，没有停止别人或新建替代资源。Job关闭/门记录依实际原件，不猜run_tag/G/Job；没有patch uuid4。

097库与卷保留、不drop。保留本卡活动ac547323-7a53-400a-8f11-3ce93b1a8efc及三来源：332a4f77-5d2f-4743-9afb-e698712b9ac4、11b79bb5-f67a-48bb-aadc-e44e528d0c0b、c86d3c8c-c85d-4bcf-9ec9-4f3daa5df749；其版本/实际首续operation/hash/root见[retained-fixture](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097/integration-08-browser/retained-fixture.json)。这是实际真链成果，后续同卡补证不得盲drop或重发。

真实model/外网/费用为0；合成Transport.send入口14次，其中not_sent进入边界后并无实际外部发送。Python守卫只许本卡loopback及线程局部stdlib selfpipe，实际离线验证拒绝其他目标；browser装路由白名单并记请求，但主动外网探针未执行，不能据blocked为空宣称全机网络阻断。

[budget-final](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097/budget-final.json)、attempt-ledger和supervision-ledger给出实际口径；[delivery-proof](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097/delivery-proof.json)核结果真实保存可读、链接/快照一致。它们是本卡材料，不是第二份项目总状态。

## 9. 未完成、风险与下一边界

本次因次数上限停止受影响集成部分，并完成不依赖新资源的使用说明、证据冻结、差异和结果保存。还缺最终意图匹配/迟到修正的真实UI复验；完整丢响应/同键重试/放弃/损坏台账/缺配/坏引用/替换/慢回包/切换/隐藏/卸载组合；专门自有Job挂死硬停；部分范围删除/数值上界动态反例；最终bundle实际服务到浏览器绑定。一个旧普通调用缺SessionOutcome，已有真实Job/导入/transport及总启动计数，仍应保持原件缺口而非伪补回执。

后续若编排安排未验收同边界补证，应沿TASK-097/R-091追加修正轮01并保留8批失败与累计账；当前许可不支持新入口，不能换runner/窗口/Agent重置计数。本次不直接派新的执行或独立审计。完整稳定候选形成之后，才由编排另卡隔离增强审计profile信任、原子提交、幂等/范围/恢复和最终动态原件。

仍未实现或未验：Embedding/向量融合及正式语义质量、完整STEP-006/007/008/009与尚未完成Must、M-1、真实服务、用户库或项目发布。没有扩大模型、权限、费用、停止/退款权威或主持久模型，不需要用户密钥/付费/用户库操作。

## 10. 给编排的正式文档建议

建议操作者为后续编排者；依据为本执行者2026-10-02 Asia/Shanghai保存的R-091及最后delivery-proof时间。本执行者未写任何以下正式文件，未占共享CHG编号。

- D:/shspic/project_NO3_RetroLume-agent/DocuS/架构动态文档.MD：在当前G7增量及MOD-001/003/004/005/006/007/008、FLOW-002/003/005、API-002/004/006、DATA-002/003/005/007的相应小节记录学习薄入口、terms.v1范围/目录、strict内部/公开profile、原子通用JSON、首次槽位及显式续问/引用恢复。FILE映射补backend/app/learning七文件、前端LearningResult/learningIntentMatch及097定向测试实际路径，既有gateway/config/活动workspace薄变化。注明无新主表/字段/停止权限，保持向量/供应商质量Must待验及最终UI动态缺口。
- D:/shspic/project_NO3_RetroLume-agent/DocuS/执行动态文档.MD：唯一总账登记TASK-097/R-091“部分完成，入口上限触发”，STEP-006/007/008及009子集仅候选范围，G7未关闭/未独立审计。合入8入口/8start/15SUP/3实际browser/4driver、226.312业务秒/4.937清理秒、离线实测+60保守额和主动墙钟上界，旧095及所有历史账不清零。记录097库/卷保留和本卡fixture归属，不并行第二总状态。
- D:/shspic/project_NO3_RetroLume-agent/DocuS/文档变更记录.MD：由编排在实际维护时登记上述章节/路径、原因、操作者和+08:00时间，导航至最终changes/diff/矩阵/资源/结果，保留部分完成与未验Must；共享编号由编排分配。
- 经验候选只在本结果和证据内交回：真实DTO/路由/列表身份必须由代码/响应核对，Node语法预检不能代替模块执行，资源观察Promise必须处理页面关闭，FK对象在断言前登记，Windows Selector selfpipe守卫不能扩大业务socket权限，观察器必须早于导入绑定。各根因/修正/实际原件导航已保存；没有写D:/shspic/错误记录。
