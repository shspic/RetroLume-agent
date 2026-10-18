> 2026-09-29编排最终状态：088/089批准G3切片合并验收通过，详见Ndocu/results/TASK-088-089-final-acceptance.md；本卡执行已结束，代码/运行余量不再授权续作。旧缺陷、失败与执行偏差保留历史。下一成果按TASK090执行，不重新启动下方原卡。

> 2026-09-29回收状态：088已回候选实现/运行结果，21项post哈希核对一致；原授权结束，代码和运行停止待TASK089统一收尾。存在回执合同不符、证据待核与超批次/容器上限偏差，未最终验收；详见TASK-088-work-decision.md。以下原卡保留作审计依据，不再按其待转交状态启动。

# TASK-088 / R-082 — G3业务正文原子提交与受控恢复读取
你是本卡执行Agent，完成整个成果后保存结果，回复一句话结论及绝对路径供用户带回编排；不接管编排，不自行签最终验收。

类型：开发＋必要适配＋定向验证及范围内修复；STEP-006/008局部，父TASK-087，依赖已关闭085/086及083/084；关联G3、NFR-002/003、SEC-002、FLOW-005、DATA-007。
接收：原TASK-085/087执行窗口，增强执行，当前客户端最强可用模型/最高可用推理档。跨事务持久提交、权限投影和跨进程协议需强推理且由真实行为验证；如实登记实际客户端/模型，不因历史标签重做成果。
状态：待用户转交，尚未实施/运行。本卡不是独立审计；实现结束后编排另安排隔离新会话的增强审计。
根目录：D:/shspic/project_NO3_RetroLume-agent。
基线：需求v1.1，架构v0.53，执行状态v1.73；Git基础提交45951501d2741630a229762d6b2d3f4b34d7f702，后续大量已验有效差异未提交，禁止reset/覆盖。
授权：用户2026-09-28明确“批准”TASK-087-work-decision置顶完整G3持久模型/提交语义变更包；本卡具体化已批准实施与合成验证，不再等待同项确认。付费provider/用户库/部署/提交推送均未授权。

## 1. 一个完整交付目标
将成功正文与操作received在record_outcome同一短事务原子持久化；仅确认提交后业务结果可SUCCEEDED；worker协议3只回传身份/状态/hash；新增失败关闭的内部只读恢复接口。一次交付实现、必要适配、受影响离线/真实PG/最小Windows接线证据和资源收尾。普通步骤与已授权修复连续完成，不能只交“准备完成”或每个失败另等一张小卡。真正停止门见第9节。
D3、085既有受控调用及监督成果复用，不重开其全套验证。G4范围管理、G5后续业务、真实provider和STEP008整体不在本卡完成声明中。

## 2. 最小充分读取与合同优先级
首次/版本变化先读：
- 根入口 D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。
- 公共 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD，2026-09-28T14:08:37.3969855+08:00版本需补读，不能假设旧窗口已读；公共库只读。
- 编排所用WORK为同库docu/WORK.MD（2026-09-28T14:27:08.2195352+08:00）、模板同库Ndocu/TASK_TEMPLATE.md（14:23:15.6061911）、阶段同库Ndocu/prompts/07_开发执行循环.md（2026-09-23T09:02:19.8381135+08:00）。本卡已携带执行约束，执行者不加载全套阶段或WORK全文。
依次读项目：
1. Ndocu/results/TASK-087-work-decision.md当前批准包及P1—P5，完整读取；Ndocu/results/TASK-087-result.md置顶修正轮01的A—D，只读取未冲突部分，首轮为历史。
2. docu/PROJECT_ARCHITECTURE.MD当前G3/FLOW-005/DATA-007相关段；docu/PROJECT_EXECUTE_STATE.MD当前088/资源/导航；docu/LATER_REQUIREMENTS.MD相关NFR/SEC；Ndocu/results/TASK-085-086-final-acceptance.md（含关门不推进G勘误、N1/N2）。
3. backend/app/activities/repository.py及__init__.py，capabilities/contracts.py、gateway.py及必要导出；worker/one_call.py、worker_main.py、session.py、launcher.py、supervisor_main.py及直接协议消费点。gate.py、windows_job.py、supervisor_ipc.py和transport只读按需定位。
4. backend/migrations/001—006现有文件；直接受影响测试/调用方。先定位签名/回执调用点，再按依赖读，不全文重审整仓。
5. 085 post-hashes.json及其真实批20260928T001119Z-77ba1b仅复用相关证据/运行控制；087 revision-01/input-hashes-r01.json作为现有源码基线。已读未变原文不再重载。

优先级：用户本次批准＋TASK-087-work-decision P1—P5 > 本卡实施/资源细化 > 087修正轮01其余不冲突内容 > 历史。旧B4拒绝即无正文、轨3取消后再结算、T20c结算丢响应一概折叠、空集合NOT EXISTS放行、64KiB必扩张超128KiB等错误不得照抄。本卡明确列出的兼容适配允许执行，不被报告“零改动/文件总数”限制。

## 3. 固定实现合同
### 3.1 数据与规范化
新增backend/migrations/007_activity_operation_results.sql：单事务新增activity_operation_results，不改001—006、不回填旧received、不要求activities为空；重跑明确重复对象错误且事务回滚，不宣称天然幂等。
表以(activity_id UUID, operation_id VARCHAR(128))为非空主键，并以相同复合键外键引用activity_operations；admission_id UUID、execution_generation INTEGER>=0、scope_revision INTEGER>0、payload_format(text/json)、payload TEXT、payload_sha256 TEXT、committed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP均非空。正文octet_length为1..131072，hash为64位小写十六进制。身份冗余值取锁内权威行并校验，不直接相信调用参数。DDL完整列/约束按批准A2落地并留实际清单。
规范正文为JSON封套{format:F,value:V}的UTF8，ensure_ascii=False、separators=(',',':')、allow_nan=False，不sort_keys。沿原解析重复键后值覆盖；按解析后有序对象规范字节比较，键序/int与float可产生不同hash，不承诺跨语言语义等价。
共享纯数据校验放capabilities/contracts或同层单一必要helper；仓储不得import worker。仓储对传入的实际payload文本复查封套、format/value类型、有限数、原深度12/节点2000限制、编码长度、规范形式和SHA256匹配，不能仅验hash正则，也不能把已有封套字符串再包一层。字段repr/诊断不泄漏正文。

### 3.2 事务、提交确认与旧状态
LedgerOutcome增加可空payload_format/payload/payload_sha256（全有或全无）；RecordOutcome枚举RECORDED、ALREADY_PRESENT；AdmissionLedger、真实仓储、Rejecting实现与直接替身同步签名。Rejecting仍失败关闭，无隐式None成功。
按原来源→活动→操作锁序在单短事务内验证、保存正文及received，网络不得入事务；COMMIT确认后才返回枚举。成功带正文新写要求当前permit/代次/executor/scope/来源/租约且dispatch_closed=False；_operation_is_current本身不足，显式查关门。次数/费用/UNKNOWN诊断纪律保持，不将全部旧诊断record改成正文授权。
终态无写幂等先于新写资格拒绝：原元数据及正文存在性/format/hash/规范内容严格等值才ALREADY_PRESENT；相同历史提交即使关门/G推进可确认，但不给正文访问或新执行权。正文与无正文不等价；异文冲突保留已有正文/终态；旧received无正文不能补写。缺权威绑定拒绝。
gateway只有合法正文获得真实提交确认后SUCCEEDED，实际返回对象必须携带payload_sha256，不能只给随后被丢弃的_finish临时结果补字段。内存ModelCallResult可保留合法正文；IPC按下一节去正文。
record异常/AdmissionDenied/无效枚举或None都不推出DB无正文；尝试提交但未确认统一UNKNOWN＋unconfirmed，保留record_denied/record_unconfirmed等错误码。committed仅本次已确认；not_committed只是本次无成功确认，不否定同键历史。无确认不自动重发或新建operation。真实提交后回执丢失先读持久事实；本卡提供同键读取/受限重放，不构建新后台恢复服务。

### 3.3 协议及时间权限
worker内部回执升级3；SUCCEEDED必须business_commit=committed且hash合法，text/json_object=None、tool_plans空；失败/UNKNOWN与三值提交状态按P1严格配对。TOOL_PLAN仅有限计划、不持久化成功正文、不自动执行。外层launcher↔SUP仍2，嵌套worker回执单独严格验3，拒混版/身份不符/正文夹带/非法hash。修改实际消费点，保留帧长度和映射秘密生命周期控制。
N1：所有one_call入口在claim前拒绝request_timeout>120秒，直接session入口同样受约束；idle配置域不收紧。保留请求余量、树零、关闭自有句柄、关闭门、结算及固定生产启动链顺序。
begin_window_close只关门不增G；settle才增G。取消已折叠R入S且清R/失效，旧settle不得再加C。settle提交前失败才残留可折叠；提交成功响应丢失已R0/S持久，不再折叠。业务正文已提交不因结算失败、取消或workerUNKNOWN被删除/降级。worker exit0不自动证明结算条件满足。

### 3.4 只读恢复接口
实现内部read_committed_result(activity_id, operation_id)与list_committed_results(activity_id, *, limit, after_operation_id)，类型/状态以批准C1加P3为准，无HTTP。
有效正文必须结果/操作/活动/admission/G/scope完整绑定、结果scope等于当前scope、来源快照非空且每项来源存在/版本revision一致。使用同一SQL语句/快照判定与正文投影，非空EXISTS＋LEFT JOIN缺失/不匹配反例或等价逻辑；失效时SQL不把正文返回应用。有效返回前重算存储字节hash及合法封套；不以hash正确替代来源授权。
NO_OPERATION允许未知元数据为None，不伪造；not_sent/received无正文为TERMINAL_WITHOUT_PAYLOAD；reserved/dispatched/unknown为UNRESOLVED。取消后的历史成果仅来源/scope有效才可读，不授予新写/发送资格。
list仅真正results行，包含失效记录的必要元数据、不含正文；operation_id稳定游标、最多200行，全页编码≤256KiB，超限明确拒绝而非悄悄裁剪。read单项正文≤128KiB。当前接口不保证撤回已返回字节，不支持不推进revision的范围暗改，不新增绕过失效策略的历史正文导出。

## 4. 允许文件与协作
可修改：
- backend/app/activities/repository.py、__init__.py。
- backend/app/capabilities/contracts.py、gateway.py、必要__init__.py；可新增同层一个必要纯数据helper。
- backend/app/worker/one_call.py、worker_main.py、session.py、launcher.py、supervisor_main.py、必要__init__.py，仅正文提交接线/协议和N1必需适配。
- 新增007迁移；backend/tests/test_capabilities.py、test_worker_one_call.py、test_worker_session.py及实际存在的直接相关测试；test_activity_ledger.py、test_activity_recovery.py、test_activity_time_budget.py仅新签名/返回确认/必要定向FK清理适配，保留原业务断言。
- 新增backend/tests/test_activity_results.py、backend/tests/fixtures/task088/（本卡合成PG/Windows/runner）；Ndocu/evidence/task-088/、Ndocu/results/TASK-088-result.md。
既有task083/task085夹具及Ndocu旧证据只读；必要复用逻辑复制到task088并记录来源/差异，产品不依赖Ndocu或外部绝对路径。产品gate/windows_job/supervisor_ipc/transport、001—006、HTTP/main/runtime、锁/依赖、正式docu、公共库不改。若真实直接消费点超出上列，先定位具体必需差异交回，不能借适配改监督安全模型。
独占上述待写文件，无并行实现/审计/测试；发现其他执行者在途先核对归属和已生效产物，不重复启动。无Git提交/推送、无删除旧成果、无安装/拉镜像/外网模型、无真实配置/用户DB。只读git状态用于保护差异，不以Git基础提交覆盖当前有效成果。

## 5. 快照与执行顺序
1. 核本卡是否已有产物/runner在途；已有结果和有效运行日志优先接续，已完成项不重跑。087设计运行0不等于已启动088。
2. 对087 revision-01/input-hashes-r01.json中的产品/测试逐项核当前hash；formal doc本次批准同步导致hash变化属预期，不误报为产品漂移。新增改动文件保存pre/hash/有限diff。repository基线=bca8283316f62216f5ba94959f5c36f8c3395301aeb9dc7f21a9b376f92e29a3；gateway=f57e3fe3e35ddab58e7e28e4ec1300b528f5ce6d55a2fb0d832525d06b547437。其他采用上述manifest；未覆盖的文件先留pre/hash。发现陌生改动查明再继续，不覆盖。
3. 完整实现与必要夹具/运行控制一并做好，差异与离线通过后在同卡继续真实PG/Windows，不另等“运行准备卡”。普通实现/夹具/runner问题在预算内有据修正，无需每次回编排；不为理论担忧增加前置独立审计轮。
4. 每批绑定实际加载/执行源码hash、精确用例、原始日志/退出码、资源manifest；修正后只复验受影响和未跑项，未变已过项复用。
5. 完成即精确收尾，写完整结果/未验证边界后停止修改。最终独立增强审计由编排另卡，执行者不自签。

## 6. 验证矩阵（T01—T21依批准P1—P5修订覆盖，不机械21次启动）
理由：这是新持久模型、原子提交、恢复读取与协议行为，必须有真实事务与最小真实进程组合证据。测试数据全合成、transport为测试替身，替身不冒充PG提交或供应商。
A. 离线定向：
- canonical编码/正确hash/同对象稳定、合法text/json、实际字节边界及超1字节、非法类型/非有限/深度节点/伪hash/不规范封套；超128KiB可在helper层合成，不强造未经证明的64KiB供应商扩张样本。
- gateway真实控制流：RECORDED/ALREADY_PRESENT成功hash到实际返回值；None/错误枚举/record冲突/异常→UNKNOWN与正确提交状态；TOOL_PLAN/失败不伪造正文成功；无自动重发。
- 协议外2内3合法配对、混版/身份/hash/夹带正文拒绝、帧与字段边界受影响项；N1 one_call超120在claim前拒绝，idle原合同保持。必要旧替身适配不得降低断言。
B. 真实PG（直接调用实际仓储，专用RETROLUME_ACTIVITY_RESULTS_TEST_DATABASE_URL，缺失明确skip不回退用户DSN；真实批运行前该变量必须已绑定本卡合成资源，skip不算通过）：
- 007在空结果结构及含旧合成活动/操作的001—006基线上成功；旧received不回填；约束/FK/正常读写及重跑错误回滚。不同基线用本卡专用库内隔离schema/数据库，记录连接search_path与归属。
- 正常received＋正文原子提交；同permit完全相同重试不写；关门/settle后历史无写确认；正文有无/异文冲突不改旧行；旧received无正文不得补写。验证实际commit返回与hash。
- 两连接同操作竞争，无双结果；来源替换与提交两种先后、cancel与提交两种先后均以明确屏障/锁事件证明顺序，不靠sleep推断；取消后不得额外结算，已提交成果按有效读规则保留。
- 关门先于新record拒写；失效permit/G/scope/租约/来源拒写；read/list对scope改变、空来源、缺失来源、版本失配/绑定不符抑制正文。制造反例不得破坏全局FK；确无法构造的损坏绑定可说明现有约束并定向检验查询，不以不可达坏行阻断正常完成。
- read缺活动/缺操作、各无正文状态、取消后有效历史、列表游标/无重复/limit及总字节边界；失效分支查询实际不投影正文，不以UI隐藏代替。
- 真实事务首写后/commit前抛错→两表无半写；真实commit后客户端注入丢响应→gateway UNKNOWN/unconfirmed，read查到正文，等值确认不再写且transport总发送1次。记录注入点，不能用全mock仓储冒充原子性。
- 已提交正文后settle提交前失败与settle提交后响应丢失分开：前者仅真实残留可后续折叠，后者R0/S已结算不折叠；正文均保留。时间账与业务提交分别断言。
C. 最小真实Windows组合：
- 通过实际固定launcher/SUP→真实worker→gateway→真实PG成功链，以task088测试自举/替身transport注入合成成功，真实监督、身份及提交路径不绕过；最终内3回执不含正文，hash与关门/settle后的合法read一致，单次发送、树零/自有句柄关闭/结算顺序有证据。
- 受影响协议拒绝/N1尽量离线覆盖，确需组合才能证明的少量场景按依赖增加并在资源上限内；不得为凑数跑085十二场景或D3八场景。
- 明确测试自举替换了什么、生产固定入口哪些行为真实执行；生产provider白名单/命令不放宽，不能宣称真实provider成功。
将087 T01—T21逐项映射到实际test ID/证据/复用或不适用理由；差异引入同类用例可合并，不删实质覆盖。业务事实用真实PG，调用合同用替身；验证层次分别报告。

## 7. 精确新资源和预算
本卡新预算，不承接083/085已结束余量；资源额度不是付费模型额度。
- 离线累计≤900秒，单命令≤60秒；现有backend/.venv/Scripts/python.exe，不写pyc的compile按需一次；有明确修正才复检。普通命令不做无意义重复全扫。
- 真实最多3批（首次＋至多2次有据修正后的受影响/未跑项续验），单批≤600秒；资源累计≤1800秒，至少留120秒收尾；Windows监督会话合计≤12，仅实际必要场景使用。准备/启动/失败/探针/等待/收尾全部入账，跨进程/窗口不重置。真实PG测试可同一批串行组织，有设计目的的两连接竞争不算并行无关运行。
- 最多一个全新合成PG容器：已有本地镜像sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f；名retrolume-task-088-g3-<唯一后缀>，DB retrolume_task088_g3、独立合成角色/新随机口令、独占新卷；1CPU/512MiB/pids128/restart=no/无特权/无宿主bind；仅127.0.0.1:55441。无pull、无第二替补容器、无改宿主服务。端口占用/Docker不可用/镜像缺失交具体阻塞，不停别人资源。
- 在本卡合成库按顺序应用现有001—006后验证007；其他已批准迁移只作合成基线搭建，不操作用户库。不要用缺新表的旧schema测新record后称产品失败。
- 运行前manifest记精确CID/imageID/卷/端口/资源配置和PID＋创建时间；新runner复用已解过的inspect缺键兼容，缺安全字段为unknown需核实，不能置常量蒙混。只读必要Docker字段，不输出完整Env/认证串。新口令仅运行期受控注入，不写版本化文件/日志；若PG镜像用环境注入如实披露，不声称从未进环境。旧容器/卷/口令均不接触。
- runner必须有独立于业务阻塞的外层总时限与精确子进程控制，保留现有Job树零/句柄合同；PG connect/lock/statement均有界，不用单个subprocess timeout冒充所有后代清理。后台启动隐藏窗口。
- 清理先results子表、再旧FK链，所有DELETE仅本用例注册的activity/operation/source ID；禁止全表DELETE或给只运行旧schema的历史夹具强塞新表清理。
- 结束stop本卡精确CID并只读确认Running=false，保留容器/卷；自身进程树退出可证，禁止宽泛taskkill/删除/停别人容器。归属/树零/停止状态不确定优先精确收尾，停止后续业务批并如实报告。

## 8. 交付与独立审计输入
Ndocu/results/TASK-088-result.md：先结论/实际文件变化/证据导航，再列实际字段、签名、enum及每跳protocol、P1—P5/T矩阵对应、事务/权限/时间边界、实际命令与退出码、运行/资源预算账、未验范围及正式文档建议。
Ndocu/evidence/task-088/：一份pre/post/as-run hash清单与有限diff；每批case start/result/complete及真实输出、故障注入/锁屏障说明、测试注入边界、资源manifest/最终收尾。生成后核文件可读，日志一处保存多处引用，不复制旧证据。完整源码及夹具在backend，不依赖Ndocu执行产品功能。
结果列真实成功/失败/skip/not_run；批exit和场景结果分开，旧证据说明适用当前hash范围。不伪称最终版本测试通过于旧加载模块或中间hash。实现普通自查不是独立审计。
高风险最终独立增强审计必须另隔离Session，仅交原始合同、批准约束、实际源码/差异/原始证据；不继承实现聊天推理。由编排安排，不由本窗口自评替代。新经验只给根因/修正/已验来源建议，正式经验及共享状态由编排统一维护。

## 9. 停止与统一回传
完成本卡目标与资源收尾即停；不追加“再放心一次”测试。范围内普通产品/夹具/runner修正可连续做，已知历史错误不复现，同一核心验收问题两次有依据修正仍失败才按门交回；根因不稳/需要推翻批准模型、额外权限/服务/费用/用户数据、陌生冲突修改或预算/精确资源安全门触发，先完成不受阻部分，安全收尾后统一交回具体差异及剩余量。
本卡中断或换窗必须保留当前代码/已过证据/尝试/资源状态，不重置或重复启动。不得宣告G3最终验收、M-1、整个STEP008或产品可发布；可建议“实现与卡内定向验证完成，待独立增强审计”。
确认完整结果已保存且可读后，只回复一句话结论及可点击绝对路径D:/shspic/project_NO3_RetroLume-agent/Ndocu/results/TASK-088-result.md。
