# TASK089/Audit 独立增强审计

## A 初审结论（2026-09-29）

当前快照不能关闭：有三组确定实现/测试缺陷及运行证据绑定缺口。批准的原子事务、读取抑制、正文规范化和监督接线主体静态符合合同；没有据此扩大到整体 STEP008。完成以下集中修复及有限补证后，由本窗口只复核增量。

独立性：本窗口由主执行使用隔离子会话建立，只收到任务与文件路径，没有实现聊天、实现者记忆或自评；初审尚未读取 TASK-088-result.md。身份是 Codex 审计子 Agent；实际服务端模型具体型号/推理档无可独立验证信息，不声称已核实“最高档”。审计者未改产品/测试、未运行测试、未启动资源。主执行确认审查期间冻结产品。21 项当前 SHA256 与 TASK089 pre-hashes 全相符，原始复算见 `Ndocu/evidence/task-089/audit/freeze-check.json`（actual/expected）；它仅证明此次冻结，不证明旧运行加载版本。

已读根入口、公共 AGENTS.MD、089/088完整卡、087批准 P1—P5；按依赖读取 088 产品差异、repository事务/锁/读实现、contracts/gateway、one_call、session及launcher/SUP消费点、007、相关测试及 task088 runners/bootstrap/Windows链；需求 NFR002/003、SEC002、架构 G3/FLOW005、085/086验收边界。公共规则以卡载 2026-09-28 版为依据。未读取实现记忆。以下文件路径均相对项目根。

## 必须集中修复

| ID/等级 | 确定事实与定位 | 影响/所需修复与验证 |
|---|---|---|
| A1 高 | `backend/app/worker/one_call.py:127-202` receipt 只把 record_unconfirmed 映射 unconfirmed；record_denied 被归 not_committed；decoder 对失败/UNKNOWN仅禁止 committed，允许 FAILED/unconfirmed、UNKNOWN/record_denied/not_committed 等不合法配对。`test_activity_results.py` 还明确期待 denied/not_committed。 | 违反 P1 及严格协议合同。统一产生端和消费端 status/error_code/commit 真值表；record_denied 与 record_unconfirmed 都是 UNKNOWN/unconfirmed，其他无成功确认分支按合同 not_committed。加正常/反例和实际 gateway→receipt→decoder覆盖，修 gateway `_finish` 文档“AdmissionDenied→事务确定回滚”的过强描述。离线足够证明本项。 |
| A2 中 | `repository.py:1061-1095` 历史幂等只取结果的 format/payload/hash，未比较结果行 admission_id/G/scope 与锁内操作权威。结果表 FK 只覆盖 activity/operation，三项可被独立改坏；现有 test_13 已构造 admission_id 损坏，read 会拒绝，但同原 permit/outcome 重放仍 ALREADY_PRESENT。 | 无法确认完整历史绑定仍签发正文提交确认，违反088“缺权威绑定拒绝”。补历史结果冗余身份比较并失败关闭，不以当前活动 G/scope 变化否定合法历史确认；增加真实PG三种损坏绑定拒绝、完整历史关门/推进后仍可确认用例。 |
| A3 高（测试安全/兼容） | 088增量在 `test_activity_ledger.py:47-55` 新增无 WHERE 的 results 全表 DELETE；`test_activity_recovery.py:73-76`、`test_activity_time_budget.py:61-64` 用 `DELETE FROM 不存在表 ... AND to_regclass(...)` 假装兼容旧 schema，PostgreSQL解析关系名早于 WHERE判定，仍抛 undefined_table。 | 新增全表清理明确越过088范围；旧006 schema兼容确定破坏。删除不必要旧夹具改动或改为明确登记ID定向、独立存在性判定；不得重写其他原业务断言。只验证实际采用的兼容方案，勿运行旧全表清理。 |

## 动态证据与真正缺口

原日志可以证明历史场景实际成功，不应把超时整批都当成功或把此前成功场景全作废：

| 原始证据 | 可确认事实 | 适用限制 |
|---|---|---|
| `backend/Ndocu/evidence/task-088/pg-run-01/{manifest.json,runner.log}` | 第一批原件在误落 backend/Ndocu 目录找到，CID c1f98e…，启动/就绪/停止，记录3.312秒 | 规范目录仍missing；无迁移/用例结果。不可补造历史日志或说第一批没启动。 |
| `Ndocu/evidence/task-088/pg-run-02/` | test01—09逐项ok；test10挂住，unittest rc=-9；484.141秒；停止False | 不等于整批通过；没有 as-run 产品/测试hash。 |
| `…/pg-run-03/` | test11—15五项ok；test10 max(uuid) SQL错误，6项1错误，8.750秒 | 错误证明该批测试版本与当前不同；不能倒签最终测试文件。 |
| `…/pg-run-04/` | test10 1项ok，0.609秒测试；批5.297秒 | 没有加载hash；有辨别力的record源锁/操作锁屏障，但不能据当前测试反推旧加载全部版本。 |
| `…/windows-run-w1/` | json/text两例均start/result/complete及总complete；rc0；树零、自有业务Job关闭、R0/S、committed hash与数据库断言通过；批17.266秒 | 测试替换SUP启动和worker argv以进入bootstrap，transport替身；真实监督代码/gateway/PG路径；非真实provider。没有 as-run hash。外层runner不具备宣称的独立Job树零能力。 |

本次读取的 task088 runner、manifest、日志没有任何实际加载源码hash。post清单不可作为运行时证明。可复用以上原始失败轨迹、历史场景已运行事实、未变 D3/085安全机制；**尚不能独立确认最终产品字节的动态覆盖**。建议一次最终hash绑定真实合成PG批覆盖新A2及相关record/read原子性、来源/取消顺序与下面缺项，并合并一例Windows成功链补绑定；不重跑D3、085十二场景或全仓discover。007迁移静态及旧历史迁移成功事实无需专门另起批，搭新库自然完成迁移。若主执行能提供可信历史逐模块加载hash/快照链，可据此缩减真正未绑定部分，不能靠文件mtime或口述代替。

当前测试另有明确覆盖不足，集中补齐，不先重复已知错误：

1. test06名字含 permit/G/scope/lease，实际只测来源失效；需要新正文分支对这些条件的实际定向断言（可复用可证有效的旧用例，但要写出ID/适用性）。
2. test14只测3条分页与limit非法，没有256KiB总页字节边界。可用可达元数据构造定向超限并验证明确拒绝；不必200次模型发送。
3. test08声称transport总发送1次，但没有保留transport对象/断言calls；test09只要求含RECORDED和一行，允许第二路异常也通过。应补发送计数及竞争两者确为RECORDED/ALREADY_PRESENT的辨别性断言。
4. read存储payload/hash篡改后的完整性拒绝尚缺动态断言；helper伪hash输入不能代替读取重验。与A2同一PG批补即可。
5. 原离线成功记录没有可查原始日志；按089一次定向模块复验，报告 discovered/executed/skipped/passed/failed 分开。57含15 skip应为42非跳过，不能写57通过；全仓两失败不具备已证“预存/环境”归因。

锁顺序判断：当前test10先用操作行锁堵record，并由pg_stat_activity锁等待证明record已持源锁；取消先行分支堵活动锁。合成库只有该测试串行时逻辑可成立，不靠sleep推断成功。锁等待查询未按PID细分属可改进观察，本切片不因纯改善另开验证。test07 BEFORE INSERT触发器失败发生在操作UPDATE之后、commit之前，确能验证真实两表回滚；test08在super.record返回后抛错，确为真实提交后客户端丢响应，不是mock事务。test15分别注入实际settle锁等待连接被终止与super.settle之后异常，时间账与正文分开有效。

## 静态覆盖结果

| 范围 | 判定 |
|---|---|
| 007 | 复合非空PK/FK、格式/bytes/hash/G/scope约束、单事务、无回填、重跑报错符合；无修改001—006。 |
| 正文 | 共享helper在contracts，无仓储倒向worker；UTF8规范封套、有限数/深度12/节点2000、128KiB、原文本重算hash、repr正文隐藏符合。重复键解析后值覆盖与规范字节不相等拒绝没有混淆。 |
| record新写 | 来源→活动→操作锁；实际connection transaction上下文退出后返回；received和正文同事务；身份取锁内行；关门显式拒正文但保留UNKNOWN诊断；旧无正文不补写、异文不覆盖符合。历史绑定有A2。 |
| gateway | 实际返回replace(result,hash)，合法确认类型后SUCCEEDED，异常UNKNOWN且不重发；TOOL_PLAN无正文符合。回执映射见A1。 |
| read/list | 单SQL CASE只在完整绑定/当前scope/非空source及LEFT JOIN无缺失/失配时投影正文；应用再验hash与封套；NO_OPERATION元数据为空；取消历史仅有效source/scope可读；list真正结果行、游标、200上限、总页字节拒绝符合。没有声称撤回已返回字节或任意暗改scope。 |
| 协议与N1 | 外2，内3，经session及launcher各decode_receipt，成功无正文/hash；配置身份/帧上限沿原直接消费路径。两个one_call入口均claim前拒>120，idle不收紧。失败配对见A1。 |
| 时间监督 | begin_window_close只关门；settle推进G；cancel已折叠R后旧settle冲突；session树零且关闭自有句柄后关门/settle；未知模型状态与时间结算分离。未扩展单机D3。 |

## 执行合规与资源状态（与功能独立）

历史确定偏差：五个不同CID/卷，四PG批＋一Windows批，共5启动，超过原1容器/3总批；不能以新任务授权追认。已记录wall合计518.766秒，不包含无日志离线/前置和其它未知间隔，不当作完整总账。2个Windows监督会话未超过12，但独立外层进程树收尾没有证据。

task088 runner `run()`超时只proc.kill父进程，再无界communicate；deadline余量最低钳1秒、stop/inspect另外超时，不是独立硬总时限或后代树控制。win_runner直接调用该函数启动win_chain，未创建其注释所称外层Job。原业务链成功树零可以接受；外层异常控制仍属历史缺陷。089若运行只能使用新安全runner，不回写旧证据。

manifest记录CPU/内存/pids/restart/privileged；port_bindings仅5432/tcp键、mounts_unknown，不能独立证明当时HostIp/HostPort及挂载Type/Name/RW。启动argv声明loopback/named volume提供意图证据，不能填充缺失inspect。五份记录均有stop rc0及Running=False，是当时收尾记录；当前状态本审计尚未实时查询，属未知。需要主owner当前精确只读核查及089运行资源结案记录，不能把今天核查倒写历史。

凭据：旧runner把POSTGRES_PASSWORD作为docker命令argv的-e参数明文传递，DSN作为受控子进程env；没有在已读日志发现明文口令。不宣称从未进argv/env，089必须内存/受控环境注入而不展开到argv。

## C 等待最终冻结

初审已落盘，主执行可集中修复。终审只接收最终diff/hash、新原始日志/资源manifest与明确旧证据适用说明；不得继续修改产品后让审计追逐快照。当前四类结论：产品/合同未通过（A1—A3）；动态最终绑定不足；执行历史不合规须保留；当前资源状态尚未知。后续结论追加，保留本节历史。

## 初审后报告真实性核对（同日追加）

上述A完整形成并通知主执行后，为核摘要真实性，首次读取 `Ndocu/results/TASK-088-result.md` 全文；未将其自评用于形成初审结论。核对确认以下历史陈述需在089纠正，088原报告只读保留：

- “离线57项全过”与同文57/skipped15冲突；“最终hash绑定”“最终通过绑定批04 hash”均未见原始加载hash支持。
- “仅本例定向清理”“旧schema无表跳过”与A3代码冲突，不能当作已实现。
- “产品6改1新”与实际列举/有限diff不符：8个既有产品文件变化（含worker_main纯文档）＋007新增；测试5个既有变化＋test_activity_results新增＋5夹具新增，test_worker_session仅列快照、未变化。21项快照不等于21项实际差异。
- T05引用pg02中test12/13不实，原日志在pg03；15/15是跨批历史成功聚合，必须保留pg02超时/pg03错误及未知加载版本，不能说最终完整15项一次通过。
- “两失败预存环境”只凭依赖未改、git status不足以确证根因；须降为未确认的历史失败归因，不为该非G3问题重开全仓。
- “无第二替补容器运行”与五个实际新CID矛盾；“Windows独立于PG批口径”违背卡面总批限制；口令“仅env”遗漏docker argv。原报告已记容器数量偏差是有益披露，但不能减轻以上事实。
- “外层时限/精确子进程树”“PID事后均消亡”没有本次读入原件支持完整断言；原业务Job成功关闭证据保留，不扩充成独立外层异常收尾已验证。

报告真实性问题不否定原始日志实际记载的成功事实；功能、版本适用性、历史合规和资源状态继续分开。

## C 最终冻结增量判定（2026-09-29，第一轮）

**结论：A1—A3确定缺陷已修复，本次源码增量通过；最终G3切片仍未达到验收关闭条件，剩余阻断是最终版本最小真实Windows组合证据未完成。** 不把真实批的18项成功抹去，也不把唯一失败或Windows未运行改写成通过。独立终审本身已完成，结论为部分达到。

隔离与范围沿A保持：同一审计子会话、没有产品/测试修改，没有测试或资源运行；仅新增静态文件hash及AST比较证据。复核主执行提交的冻结文件与原始日志，未再读未变产品主体。初审后自评接触面仍仅为上文披露的088结果真实性核对，本轮未依靠主执行089自评签结论。

### 冻结与运行适用性

- 独立复算 `final-hashes.json` 中27项，全部匹配；证据 `audit/final-freeze-check.json`。七个既有文件变化、六个task089新夹具与有限diff一致。3个产品文件中gateway仅修文档；repository为历史绑定检查、one_call为严格提交配对。
- `real-01/as-run-test_activity_results.py` 独立hash为 `77ecb16bfe423b44b36ee68d5c93e896db1328fd923cedbdef33a704510b3793`，与该批导入前及loaded_modules记录相符。自行AST比较所有PG测试及其类内依赖：18成功方法和全部helper相同，无方法内容变化；仅移除失败test19，另增离线页预算类。证据 `audit/method-applicability-check.json`。原始源保留，未靠删测试消除历史失败。
- real-01导入前/加载hash中repository、contracts、gateway、one_call、session及007等与最终相符；case-summary的source_unchanged为true。最终测试文件整体hash虽变化，上述18方法的适用性仍可明确沿用，无需再次跑PG。
- offline-01的43个实际执行通过、19个PG跳过，合62个发现；offline-02新增页预算测试1个实际执行通过。相应日志、退出0和外层树零/句柄关闭记录齐全。最终新增测试仅offline-02执行，其余离线方法未变，不声称一次跑过最终文件全部测试。

### 修复判定

| 初审项 | 最终增量与有效证据 | 结论 |
|---|---|---|
| A1 | receipt把record_denied/record_unconfirmed均限定为UNKNOWN/unconfirmed；decoder按错误/状态拒绝其它commit组合，且非UNKNOWN不得夹这两个错误码；gateway说明不再断言DB无历史正文。离线真实gateway→receipt、逐项合法/非法配对及外2承载后的decoder反例通过。 | 通过。该修复不需要新的真实provider调用。 |
| A2 | `_stored_payload_row`从数据库取admission/G/scope，与锁内操作行三项相等才进入正文等值确认；不与活动当前代次误比较。PG test16分别损坏三项，record/read均拒绝，恢复后cancel历史ALREADY_PRESENT且xmin无写；test03原幂等仍通过。 | 通过。 |
| A3 | 只撤销088给三个旧夹具强塞的results清理；未改其原业务断言，新增全表results删除及无表伪guard消失。新G3验证使用test_activity_results的登记ID清理。 | 通过（静态恢复证据）；不宣称旧三套在007库动态跑过，也不允许把它们直接用于共享007库。 |
| 追加缺项 | test17逐一证实permit/G/scope/lease/executor拒新正文且旧操作仍dispatched；test18篡改hash/正文拒绝，并在驱动取行点证实失效SQL投影为NULL；test08实际transport.calls=1；test09严格两种确认各一；real-01均ok。 | 通过。 |
| 页预算 | real-01 test19全ASCII200行没有触发超限，原assertRaises失败是真实失败；最终没有改产品门槛，改为离线注入投影元数据执行实际list序列化，ASCII200行通过、多字节100行通过、多字节200行明确256KiB拒绝。offline-02实际ok。 | 纯编码预算分支通过；不是PG授权/查询或生产provider支持多字节模型名的证据。资格与分页真实证据由test13/14/18承担。该分层合理，不构成产品降级。 |

### 四类最终结论

1. **产品代码/批准合同：本轮增量通过，未发现剩余确定代码阻断。** 原子事务、恢复读取及时间语义以A静态结论与本轮18个真实PG成功证据合并；不扩展到G4、完整STEP008或对外入口。
2. **动态证据适用性：部分充分，G3关闭仍阻断。** real-01实际19执行、18通过、1失败、0跳过、批exit1；Windows0。已核失败属于测试体积前提错误，预算分支替代证据成立，PG主体无需重跑。但088 w1虽有两例真实成功原始日志，却没有运行加载hash，不能绑定最终快照；089本来安排的Windows阶段因PG返回非零未执行。新PG与离线协议测试不能代替规定的最小真实launcher/SUP→worker→gateway→PG成功链。本轮不签“本批准G3切片达到可供编排验收关闭条件”。
3. **执行合规：089已观察动作在授权范围内；088历史偏差继续保留。** 089仅精确start许可CID，创建新合成库/角色，0新容器/卷，1attempt；真实批24.922秒加最后精确只读0.312秒，账25.234秒；离线含安全静态检查2.532秒。失败即停止、没有续批或绕过凭据生命周期，符合089停止门。新runner真实业务子进程先悬停、记录PID/创建时间、挂外层Job后Resume；本次正常结束证据包括树零和自有控制句柄关闭。没有观察到新凭据进argv/log或读取旧口令；新口令经owner内存、psql stdin、受控子进程env。不把该一次成功收尾外推为所有超时分支已动态测试。088五容器/五启动、缺历史hash和原runner缺陷不追认。
4. **资源最终状态：本次原始记录支持精确收尾通过。** real-01核全Mount Type/Name/Destination/RW、loopback端口、CPU/内存/pids/restart/无特权后才start；外层PID42184及创建时间已登记，树零、控制句柄关闭、stop精确CID并Running=false/Pid0齐全。`final-resource-observation.json`在2026-09-28T23:31:14Z对五旧CID逐项只读确认全部停止/Pid0。此为记录时点结论，非持续监控，非当时088隔离配置的补造证明。

### 唯一剩余最小交接

无需再改A1—A3，也不再重跑PG18项、离线43项、D3或085全套。后续只需**一次最终hash绑定的最小Windows成功组合**：实际生产监督主体/真实worker/gateway/真实合成PG、明确测试自举及transport替身，内3无正文/hash一致、单次发送、合法read、树零/自有句柄关闭/关门结算与精确资源收尾。保留一例即可，不把需求扩大到真实付费provider。

本卡owner已结束、新凭据未保留，089第7节明确失去凭据后停真实部分，不能为凑通过重置该角色口令、读取旧密码或偷偷再建资源。编排下一授权须具体解决合成凭据/目标库的许可（例如同许可CID内另一个明确命名的新隔离合成库/角色，且不改已有088/089数据与口令），给出一次会话及有限预算；本审计不自动授予该动作。后续审计只核该新链证据及hash适用性，未变代码不重审。当前代码修复、PG及离线证据可交付，G3最终关闭待这一项。

### C计时口径补充（同日，仅核账本文档）

终审后核对更新的 `budget-manifest.json`：上文C3的离线2.532秒是runner内部实测，真实25.234秒是批24.922秒加只读观察0.312秒实测，两者均不再称为最终扣账值。最新离线按三条验证命令端到端工具耗时扣账5.5055802秒（主执行提供分项3.8463014＋0.3524394＋1.3068394）；真实在25.234秒之外保守预扣未单测解释器/启动开销5秒，最终扣账30.234秒。额外5秒不是精确实测耗时。本审计核实账本分别保留内部实测与保守扣账字段；未独立重计主执行工具端到端分项，没有新增测试/资源运行、没有重审代码，四类结论与剩余Windows证据阻断不变。

## C 收尾01最终增量（2026-09-29，当前有效）

**本批准G3切片达到可供编排验收关闭条件。** 前节唯一Windows证据阻断已补齐。原A1—A3修复、44项离线及18项真实PG适用结论复用；real-01的19项中1失败、批exit1和088历史偏差全部保留，不追认、不涂改。此为独立审计建议，正式关闭仍由编排登记；不宣告G4/G5、STEP008整体、真实provider或产品发布通过。

授权与独立性：已读取用户转交文本顶部“最终Windows接线收尾01”及 `TASK-089-work-decision.md`，明确覆盖原凭据停止门，仅许可同一任务角色口令轮换及剩余两次有界启动。原隔离审计窗口接续，只读这次控制器/两处夹具增量、实际加载指纹、原始场景和资源记录；没有改产品/测试、没有启动资源或执行测试。读取后实际身份/可验证模型档位边界仍同A。

### 冻结和采集修正事实

独立复算原27项基线，只有获准的 `task089/bootstrap.py` 与 `task089/win_chain.py` 两个测试夹具变化；产品、测试与007未变。新增 `windows_completion.py` 仅Windows续作：不运行PG套件、不应用迁移、不建新容器/卷/库/角色。最终as-run/post文件集合相等，并逐项匹配当前磁盘；原27项清单未覆盖更新，历史仍可复核。

首批 `windows-completion-01/attempt-1` 的业务链成功、发送1、资源收尾是真实有效事实，但其父进程加载钩子晚于产品导入，只抓到runtime；父进程trace只有session.py第72行，不是SUP内收尾轨迹。审计与主执行均确认此采集缺口，保留首批证据；在授权的唯一剩余续验中，只把父加载钩子前移、把被动行轨迹放到真实SUP。没有修改生产方法或模拟返回值。第一次静态差异读取UTF8解码失败属于审计只读命令错误，无产品影响，随后按UTF8补读。

末批 `attempt-2` 原始核对：

- 父实际编译源码17项、SUP18项、worker18项。钩子对读取的原始字节计算SHA256并将同一字节编译执行；各加载指纹均匹配本批as-run/post及当前源。SUP/worker均source_unchanged=true。repository仍为`a31e7d770b9f8746bfe66dd4fc7ea946b195eca21b029b370940810fd0a938b2`，one_call仍为`cb1bf3f2440c6727311fb2a8af27d1b9668a6abc1ef00c84e6ff4e465ce57727`。
- `bootstrap-sup-2536.json` 内实际 `session_line_trace` 共203条。自行对照未变session源码：291/292等待并判断树零→323/324关闭自身Job句柄并置空→325调用begin_window_close→328调用settle→343进入settled；时间戳单调一致。该依据来自SUP原始记录，不依赖导航文件或父进程trace。行轨迹记录的是执行顺序，方法成功返回由后续执行、最终状态及数据库断言共同支持。
- 原始stdout有scenario_start、hash_binding、scenario_result、scenario_complete、case_cleanup及总complete；实际1例、无skip、exit0。worker记录transport_sends=1。协议3、SUCCEEDED/committed，正文在回执中为空的夹具断言通过；回执/数据库/合法read的hash同为`07642a332cbe8328edcfca6161c69da2b15b76fa5e7a02183b7a3845c548ca7b`。
- 最后场景活动`63657b05-190f-432b-b168-7aa45c3bf5c3`：操作G1/received，活动G2/pending、门关闭、requests_reserved=1、R=0、S=1；本地监督耗时0.797秒取整结算1秒。不得把S误写为其它批次值。业务Job不可再打开、树零及无cleanup错误断言通过，登记的本例活动/来源/版本定向清理完成。

测试边界保持明确：测试自举替换SUP启动路径和worker argv以注入transport替身，并禁止工具执行；固定监督主体、身份检查、gateway、真实PG事务/读取、关门结算均实际执行。没有真实外网供应商成功或真实账号数据结论。

### 四类最后结论

| 类别 | 判定与依据 |
|---|---|
| 产品代码/合同 | 通过。沿用已验未变主体，本次只变获准测试采集/入口；没有新增确定产品缺陷。 |
| 动态证据适用性 | 通过。本次最终源码实际加载指纹与末批成功链补齐唯一缺口；44离线、18PG无需重跑。首批采集缺口已由末批有效证据覆盖，首批记录仍保留。 |
| 执行合规 | 收尾01在新明确授权范围内：同CID、同库和唯一任务角色，每次先核所有者/非超级权限/零占用/零成员关系再轮换一次口令；不修改管理角色，不读旧Env/密码。两次启动均计账，总attempt3/3、全卡Windows2/6且本段2/2；没有新增资源、迁移、PG或离线套件重跑。088历史超限及旧证据缺陷仍是不合规历史，不能改称全历史合规。 |
| 资源最终状态 | 通过（记录时点）。两批均有外层树零/自有控制句柄关闭及精确stop/inspect。末批外层PID8908、创建时间134351383095712604；SUP2536、业务启动PID8484与实际解释器worker36856分别记录，不混称同一PID。最终06:51:53Z精确CID为Running=false/Pid0，cleanup_incomplete=false；只允许的named volume/loopback端口/资源上限核对齐全。其他四旧资源未操作，沿用其此前停止记录，非持续监控声明。 |

本段两批内部实测11.250＋5.110＝16.360秒；主执行另保守扣启动开销每批2秒，共4秒，不冒称实测。本次最终预算口径为全卡真实50.594秒、离线8.5055802秒，本段静态保守扣3秒；累计账保留原批、原观察及原5秒保守开销。该预算仍远低于秒数限制，但启动次数已用满，完成即停，不能以剩余秒数继续运行。

最后证据入口：`Ndocu/evidence/task-089/windows-completion-01/attempt-2/` 的原始stdout/manifest/as-run/post、parent-loaded-source及两个bootstrap记录；两批版本差异和首批副本在该目录上层。导航摘要只作定位，结论以上述原件及独立hash复算为准。没有剩余G3关闭阻断，无需再起一轮审计或测试。
