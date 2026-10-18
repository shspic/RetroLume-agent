# TASK089/Next — 范围修订与持久成果受控续接合同

日期：2026-09-29（Asia/Shanghai）。状态：只读设计合同已完成；G3最终关闭仍以独立审计为准，推荐合同尚未批准实施、未派下一卡。实际项目根 `D:/shspic/project_NO3_RetroLume-agent`；入口 `D:/shspic/project_NO3_RetroLume-agent/AGENTS.md`；公共规则 `D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD`，现场修改时间2026-09-28 14:08:37 +08:00。本D成果的设计操作不实施产品/迁移、不运行实验；整卡G3修复和验证另见result，不混成整卡运行0。初稿由TASK089/Next保存，07:21用户恢复后由主执行按最终源码/证据收敛；未把实现者自评作为独立通过依据。正式CHANGE登记交编排。

## 1. 唯一推荐成果与完成边界

推荐下一张完整实施卡交付：**同一活动的真实范围修订，以及把已持久的上一操作正文安全用于一个明确新操作的内部闭环**。调用方能读回已提交成果、明确看见失效或未知；可更新当前来源集合并推进范围修订；只有当前范围、来源、租约和剩余预算仍有效，才能把一个当前持久成果作为下一次受控调用输入。沿既有单次监督入口，每次最多一个新模型操作，不引入自主多轮循环。

依据：需求v1.1 NFR-002/003、SEC-002；架构v0.54 FLOW-005、DATA-007。架构第102行已明确 G-4=范围修订，G-5=工具计数，不能把G5解释成任意“下一业务入口”。本切片落实G4及G3消费接线；工具计划仍不执行、此入口工具集合必须为空，G5、完整STEP006/008、完整学习/评分业务、HTTP/UI、生产provider、用户库和发布继续开放，不借此宣布整体完成。

完成条件：下文接口/锁序/失败出口全部实现；针对新行为的最小矩阵有适用证据；独立增强审计无阻断；范围修改、消费、取消与持久恢复可沿真实仓储和既有监督入口走通。文档本身以覆盖和一致性完成，不以前置实验作为交付条件。

## 2. 现状、缺口与具体调用路径

以下均为源码只读事实，不代表动态验证通过；函数名是稳定定位锚点。

| 环节 | 已有事实与文件/函数 | 下一切片缺口 |
|---|---|---|
| 来源变更 | `backend/app/materials/api.py:upload`调用资料仓储；`materials/repository.py:PostgresMaterials.save`锁来源行、替换current_version并revision+1；`confirm_pdf_candidate`确认PDF时同样推进revision | 已有共享来源权威，不另造第二份revision；它不替活动选择新范围 |
| 活动范围 | `activities/repository.py:create_activity`写`activity_scope_sources`和初始scope_revision；002定义相关表 | 未找到运行期范围更新方法；不能把测试SQL改revision叫产品G4 |
| 调用与监督 | `worker/one_call.py:run_one_call`→`launcher.py:run_supervised_window`→`supervisor_main.py`/`session.py` claim→`worker_main.py`→`ControlledModelGateway.call`→`admit`→`mark_dispatch_started`→transport→`record_outcome` | 当前可传任意受信请求，但没有“持久成果选择→正文组装→新准入”业务所有者 |
| 持久恢复 | `activities/repository.py:read_committed_result/list_committed_results`，007结果表；内部回执仅身份/hash；read在SQL内抑制失效正文 | 没有受控消费入口；read的返回只是单次快照，不能沿用为新出站权 |
| 取消/预算 | `cancel_activity`推进G、关门、R转S清零；`claim_lease`保守接续；`settle_execution_window`独立结算 | 新范围写入不得复活cancelled或重置预算；取消落库不等于自有树已经结束 |
| 外部入口 | `backend/app/main.py:create_app`只挂资料和PDF审阅路由 | 没有活动HTTP入口。本卡下一成果明确选内部受信调用入口，不把不存在的页面描述成可用 |

具体内部路径：受信调用方持有activity_id和已持久operation_id → `read_result`或`resume_result`只读恢复 → 若来源替换/范围选择改变，显式调用`revise_scope` → 旧成果返回失效、需新范围下另行产生有效成果 → 对当前有效成果，显式调用`continue_from_result(...new_operation_id...)` → 固定one_call监督链 → 新操作持久结果read。任何取消请求仍通过`cancel_activity`落库；自有树退出由既有有界监督链确认，不把cancel数据库返回等同于即时杀树。终态返回正文状态、监督状态、结算状态三份独立事实。

## 3. 推荐接口、权威与并发合同

### 3.1 所有者和接口

新增 `backend/app/activities/service.py` 为受信内部业务服务；它不接收模型自行产生的权限指令，不持有第二套预算，不直接调用transport。

- `read_result(activity_id, operation_id)`/`resume_result(...)`：薄封装G3 read，维持现有状态和脱敏错误；恢复永远是查同键持久事实，不claim、不发请求。不增加自动轮询器；暂不可读即返回unknown/read_unavailable供调用方以后显式再查。
- `revise_scope(activity_id, expected_scope_revision, sources)`：委托仓储新增`revise_scope`；sources为明确的完整新集合，每项source_id/version_id/revision，不接受正文充当权威；沿用create_activity的唯一性、大小和类型上界。返回新scope_revision和当前元数据，无正文。无变化返回当前revision；CAS不符返回scope_conflict，不盲重试。
- `read_scope(activity_id)`：委托新增仓储`inspect_scope`，同一SQL快照返回scope_revision与完整来源集合的轻量权威快照；供CAS冲突及范围提交响应丢失后的只读核对。不用read_result推测当前完整集合，不推进revision或执行代次。
- `continue_from_result(activity_id, parent_operation_id, new_operation_id, followup, service, config, executor_id, run_tag)`：只允许同活动一个父成果，父/新operation_id必须不同；服务从G3受控read获得正文，固定将其作为低信任assistant历史内容、followup作为user内容，不把正文拼入系统权限指令。text直接取封套value，json以规范JSON作为内容；必须经过既有请求字节/输出/上下文上界，超限拒绝，不截断、不自动摘要。allowed_tools为空，预算显式有限。返回监督结果及对新operation_id的受控read结果；不因回执UNKNOWN自动调用第二次。

本切片不持久化新“消费事件/业务评分/父子任务”模型。结果的admission/G/scope仍由既有007权威。新内部请求增加可选`input_result`（见3.3），仅为本次准入携带可验证引用；不声称已提供持久父子溯源图。

### 3.2 G4真实写入：revision只有仓储可推进

`revise_scope`使用一个短事务：读旧集合提示 → 旧、新来源ID并集排序加锁 → 活动行锁 → 重读旧集合并与提示完全比对 → 校验expected_scope_revision、完整新集合的共享来源current_version/revision → 在同事务替换该activity的scope集合并scope_revision+1。旧来源已换版本不妨碍移除/刷新它，**只要求新集合的版本有效**；来源行仍按ID锁定以排除与共享来源写入交叉。

允许活动pending或running修改范围，不改变status、G、executor、租约、dispatch_closed、截止、M/R/S、请求/费用计数；cancelled拒绝修改。范围变化立即使旧scope的后续准入/新正文提交失效；现有SUP在`job.wait_empty_until`等待退出，并无实时范围轮询器，不能声称修改范围会即时中止在途请求。旧窗口按原截止/树零/关门/结算合同收尾，不由范围方法擅自折叠或重领；返回的业务状态可能UNKNOWN而监督已结算。空新集合允许表示移除全部范围，并推进scope；随后claim/admit/read正文均因空来源拒绝，不允许空范围调用。scope达到数据库整数上界则明确拒绝，不绕回1。相同集合在CAS匹配时无写幂等；提交响应丢失用read_scope核对，不能无条件再次+1。

**必须同步修正的真实竞争点**：当前`_source_rows`在活动锁前取提示，G4引入后该集合可以变化。所有“来源→活动→操作”事务在拿到活动锁后都须重读并比较集合；若不同，回滚整个事务后返回明确冲突，不能拿活动锁再补锁新来源（反向锁序），也不能继续用旧集合。范围写者遵守同协议，所以持有活动锁后集合稳定。统一小helper覆盖`claim_lease/inspect_window/begin_window_close/settle_execution_window/cancel_activity/recover_unknown/recover_obsolete_operations/admit/_locked_operation`；`create_activity`保持新建路径。取消/收尾遇范围冲突可由原有有界调用层重新调用，所有重试计入原总期限，不做无限重试或重置时间。只读G3单SQL继续沿其快照语义，无需为了读历史持长锁。

此处锁后集合比较是G4引入的新必要行为，不反向声称冻结G3已存在可变范围支持。

### 3.3 消费快照与重新准入

增加纯数据引用`ResultConsumptionRef(activity_id, operation_id, scope_revision, payload_sha256)`，UUID/受限操作键/正整数/64位小写hex严格校验。`ModelCallRequest.input_result`默认None，服务在拿到`COMMITTED_CURRENT`正文后构造；`AdmissionIntent`携带同一引用。gateway的`_build_payload`继续显式投影供应商字段，引用不发给供应商；请求经IPC前后都进行类型、限长及同活动检查。

仓储`admit`在现有来源锁→活动锁及锁后集合复查之后，按operation_id排序锁父操作与新操作定位（新键不存在时仍以活动锁串行化插入）；核父正文绑定、当前scope、来源非空有效、实际字节合法/hash一致，并核引用hash/scope与父结果、当前活动及本次context一致。父必须是本活动的可读当前成果；取消历史状态不能消费。全部成立才在同一事务占用新操作键、预留次数/费用。任一失败无新操作/费用预留。旧调用的input_result=None保留其原合同。

服务组装正文与引用后，不允许自由替换父正文；低层仍处于既有受信应用边界，不能称此引用是防恶意同用户进程的密码学能力。若必须对任意外部调用方证明“请求正文确实包含父成果”，应另设计外部API身份及请求指纹，不在此切片暗扩。

`mark_dispatch_started`仍重新检查活动scope/G、来源和门：若范围在admit后变更，拒绝后续dispatch，已经占用的预算按原未知/预留规则保留，不退款。若变化发生在最后资格事务提交以后，遵守FLOW-005逻辑出站分界：请求可能在途，不能承诺撤回；旧scope响应只能诊断/未知，不能新增成功正文。已有父成果与结果行不更新，所以通过scope/source检查已保证此前验证的消费引用不被另一合法路径悄悄替换。

read快照允许历史展示，但只表示返回时有效；客户端应标示版本/修订，下一次展示可重新读取。系统无法撤回已经返回的字节。取消前已提交且来源/scope仍有效的正文可作为取消历史查看，绝不转换为新执行权；来源失效/范围变化时历史正文继续由G3抑制，仅元数据可见。

### 3.4 未知和预算不可复活

同键reserved/dispatched/unknown没有可读正文 → unresolved，保留原预留且不重发；record异常、回执丢失、DB暂不可读均不能推断库内不存在正文。read找到当前合法正文才返回已恢复；NO_OPERATION或TERMINAL_WITHOUT_PAYLOAD也不让恢复入口自动发模型。

新操作必须来自明确的新调用意图和不同operation_id，在原activity上重新准入。不能在resume内部随机造新ID重试，也不能新建activity绕过原活动预算。用户明确另起活动的产品规则尚非本切片。范围修改/读取/进程重启不重置截止、请求/费用预留、M/R/S；R已因cancel清零则settle不得再次累加；未知发送预留不退款。无余额可以历史读取，不能新调用。

## 4. 一次可实施文件清单、兼容与失败出口

| 文件 | 本切片增量 |
|---|---|
| `backend/app/activities/repository.py`、`__init__.py` | ScopeSnapshot/范围结果类型、inspect_scope/revise_scope、锁后集合复核helper；admit增加受控消费引用验证；导出必要类型 |
| `backend/app/activities/service.py`（新增） | 上述read/resume/read_scope/revise/continue业务方法；同步监督调用与异步仓储明确分界，不在已有事件循环中裸用asyncio.run；阻塞监督走既有调用线程边界 |
| `backend/app/capabilities/contracts.py`、`gateway.py` | ResultConsumptionRef及可选请求/AdmissionIntent字段；严格验证、传递到admit；供应商payload不携带内部引用 |
| `backend/app/worker/one_call.py` | OneCallInput的request序列化/反序列化接纳新版请求字段，仍由类型校验恢复；普通入口不自动改成续接。确有直接严格schema消费时只做必要适配 |
| `backend/tests/test_activity_scope.py`、`test_activity_continuation.py`（新增） | 范围CAS/竞争及消费/未知/取消/预算的行为证据 |
| `backend/tests/test_activity_results.py`、`test_capabilities.py`、`test_worker_one_call.py`、`test_worker_session.py` | 仅变化字段、来源复核及调用接线所影响的既有用例；不重写旧证据 |
| 未来卡专用`backend/tests/fixtures/<该卡目录>/`及`Ndocu/evidence/<该卡目录>/` | 需要真实验证时使用的合成夹具/有界运行控制/快照绑定证据，旧task083/085/088/089夹具日志只读 |

不修改001—007，不新增008、不迁移/回填用户库。范围集合和scope_revision沿002既有结构；007正文不可变。资料仓储save/confirm只复用权威，无新增来源接口或DDL。旧无正文received保持不可恢复；旧result只有来源/scope匹配才可见。

请求内部schema属于加字段兼容增量：新代码接受旧请求（input_result=None）；旧代码因extra=forbid拒绝新续接请求，禁止新旧worker混用/忽略字段降级。外层协议2/内层回执3无新增字段，不仅为请求可选字段重编号；同版caller/SUP/worker整体部署并验证旧端拒绝新字段。service与request正常配置域、64KiB请求及128KiB业务封套上界不抬高。

失败出口固定为：scope_conflict（需读当前范围）、source_invalid或result_invalidated（隐藏正文，需重新选择有效输入）、unresolved/read_unavailable（以后显式只读对账）、cancelled/budget_exhausted（停止新动作）、input_too_large/invalid_input（配置或用户问题）、integrity_error（失败关闭并脱敏诊断）、supervision_unknown（旧树不明，不启动新窗口）。不要把所有失败映射成可自动重试。终端响应不泄漏DSN/SQL/正文到错误日志。

## 5. 最多四条状态推演

1. **先读后改再调用**：A/scope7父P可读 → 读出P → revise到scope8 → 使用P引用发起新Q → admit在锁内拒绝，Q未占位、请求/费用不增加；P元数据保留但正文失效。反向若Q先准入，则之后scope8阻止旧scope新提交；若发送已越过分界只承认可能在途。
2. **范围与来源竞态**：事务X提示{S1}；事务Y先完成{S2}/scope+1 → X锁活动后发现集合变化 → 整事务回滚，不在活动锁下补锁S2。S2共享revision更换早于新范围校验则拒绝；晚于校验提交则立即使该范围的后续准入/读正文失效。
3. **取消与历史成果**：P先持久提交 → cancel使G失效/R转S一次 → 来源和scope有效时P仅历史可读，Q拒绝；来源再失效时P正文隐藏。先取消后P的新提交则拒绝，树零和结算事实另报，不用read成功代替停止证明。
4. **重启未知和预算耗尽**：P提交响应丢失 → 重启resume(P)查库：有合法正文则恢复，没有/不可读则未知；不重发P。只有明确新Q且P当前可消费和原活动余额足够才准入；旧R依原D3恢复折叠，不从新窗口/范围修改补回余额，耗尽只读不调用。

## 6. 最小验收矩阵（未来实施执行，本设计未运行）

| 项 | 最小有辨别力证据 | 可复用/新增边界 |
|---|---|---|
| V1 范围写入 | 实际PG：完整替换+CAS冲突+相同集合无写+空集合关闭调用；预算列前后相等 | 复用002结构；新增真实G4路径，非直接SQL改revision |
| V2 来源集合竞态 | 实际PG锁屏障，分别证明变更先提交/旧事务先持锁；旧新集合不重叠样本证明锁后复查确实拒绝 | 只测新竞态，不复开全D3；每轮记录屏障顺序和最终行 |
| V3 消费准入 | 实际PG当前P→Q成功；读P后scope或共享revision变更→Q无新预留；伪父hash/跨活动拒绝 | 复用G3正文合法性证据，新增准入消费绑定及真实计数 |
| V4 已准入后失效 | Q已预留后scope变更，mark_dispatch拒绝/旧响应不得新正文；费用/次数不退款 | 复用G3记录拒绝主体，仅新增真实scope写入触发 |
| V5 取消/恢复/额度 | P取消历史可读但续接拒绝；重启查同键已提交/未知两分支均零自动发送；耗尽时读取可行、Q拒绝、R/S无重复折叠 | 复用089确认后的取消/record丢响应证据，新增服务决策和调用计数 |
| V6 真实内部接线 | 最小Windows监督链：真实PG P→新Q→read；transport合成替身，记录父/新键、回执hash与正文一致及树零/结算；离线拒绝旧端新字段、引用不进provider payload、超长早拒绝 | 不调用生产供应商；只补真实新请求字段/服务接线，不重跑旧12场景 |

V1—V5可以在一组合成PG批内共用资源与已绑定最终hash；V6只需要真正新增的成功接线，失败分支能离线或PG证明的部分不重复Windows运行。具体容器/CID、运行次数/秒数、合成库和新卡凭据责任由编排在未来实施卡冻结；本089/旧088剩余额度均不继承。实现后独立增强审计针对本切片实际变化、锁序/读与再准入、未知/预算和原始证据，未变G3/D3结论按hash与路径复用，不再次全仓审查。

## 7. 真正待决定项与G3接口依赖

没有新增业务目标、主要持久模型、公开HTTP接口或供应商选择待用户决定；上述内部服务/可选引用及scope CAS均是既定FLOW-005/G4的实施细化。唯一推荐就是本合同，不要求用户选择普通函数名、重试算法或多个路线。

**本卡权限仍仅只读设计。** 编排可在既定07开发范围内采用本合同，下一完整卡明确授权产品写入、定向合成运行与独立审计；不能把“没有新的用户模型决策”写成目前已获下一卡实施权限。若实际落地发现必须新增持久父子模型、外部API或更改预算/取消语义，则已超本方案：先给具体影响与一个推荐批准包，不顺手实施。

G3独立终审已回收：`TASK-089-independent-audit.md` C节确认A1—A3及本轮代码增量通过，18项真实PG主体和离线协议证据可复用；G3整体仍缺最终hash绑定的一例Windows组合，不具备关闭条件。本合同依赖的`RecordOutcome`提交确认、read/list抑制、两个record错误统一unconfirmed、严格回执配对、取消/settle事实分离均未发生接口签名变化。它们的源码合同已有独立确认，但下一切片的完整运行验收仍以G3这项接线缺口补齐为前置；不把接口确认写成G3全链已通过。

编排可立即裁定本D设计，G4范围权威、锁后集合复查与预算不变部分不依赖缺失的Windows证据；消费端实现和组合验收应在后续明确授权中列G3补证依赖。最小补证是一次新许可合成凭据生命周期下的Windows链及证据增量审计，不重跑本卡18项PG或43项旧离线。不能复用本卡已结束owner的内存口令，也不能自行换库/重置已有角色。该资源决定属于具体运行授权，和下一业务模型选择分开；本D不提前派卡或授予资源。

只读设计核查：六项D要求已分别覆盖于第2、3、4/5、6、7、7节；最多四条推演；明确G5真实含义；不占未来TASK/R；本文件尚非实施卡或全局验收记录。
