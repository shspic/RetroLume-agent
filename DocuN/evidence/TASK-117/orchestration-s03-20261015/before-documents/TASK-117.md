# TASK-117 / R-111 / STEP-018 — 客户端额度中断后的完整接续补充

你是本卡增强工程执行者 A+。继续 TASK-117 的同一个完整 S 合成集成成果，不重做已完成工作，不承担独立审计或最终验收。本补充是当前有效合同；后附原卡的产品合同、资源归属、安全边界及未改额度继续有效。不是把任务从头执行的指令。

## 接收、规则与目标

项目根目录 D:/shspic/project_NO3_RetroLume-agent；入口 D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。task_model，锁定 V4.0、公共 AGENTS CHG-0003，阶段07，需求v1.3、架构v1.35、执行动态v2.62。公共只读根 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4。七项规则身份以 DocuN/evidence/v4-migration-20260930/rules-snapshot.json 为准，不能自动采用更新版本。

用户已经明确：中断原因是其GPT账号的Sol使用配额耗尽，不是本卡预算用尽或自动审批服务拒绝。可使用仍有可用额度、能承担本卡的A+资源继续，不要求等待Sol恢复。若原 TASK-117 / 原 TASK-111、114、116 的工程窗口支持切换到可用资源，优先沿用原窗；否则由一个 A+接续窗口独占接手。人工转卡即选择该窗口为唯一写者，原工程窗口在接手续作期间保持停止，不自动恢复并行。没有确认原窗停止则只读核对，不运行业务、不修改产品或执行主账。实际客户端与模型如实记录，换窗不重置 TASK/R、首点、计数、失败或资源归属。不派子Agent，不开第二个工程写者。

目标仍是116已批准 AP1 的学习、面试、混合检索、记忆、四账、014兼容、R01/R02只读恢复、同正常库重开与本机交付的稳定 S 候选。保留原始失败并完成必要普通修复、针对验证和准确收尾后统一回传。已经充分验证的对象直接引用；没有证据的项明确未完成，不用合成传输证明真实供应商语义。AP2 80次/20元条件性授权仍在，Q尚未启用，真实provider调用/费用必须为0。

## 先读的最小断点输入

以下均相对上述实际项目根。原窗已读且未变材料复用，新窗先读入口、锁定公共 AGENTS、当前完整卡与主控裁定，按缺口补读116冻结合同，不能把聊天或截图当作唯一合同。

1. DocuN/results/TASK-117-work-decision.md 最新段，及本完整卡本补充、低内存段和S02段。更早S01全文仅在追溯原契约时按需读。
2. DocuN/evidence/TASK-117/orchestration-quota-recovery-20261015/inspection.json，本次主控核证的84项 as-run 字节绑定、计数、时间与限制；不是执行回执。
3. DocuN/evidence/TASK-117/execution/budget.json、events.jsonl 的实际最新尾段、continuation-01/receipt.json、low-memory/adoption.json。只由唯一工程执行者前向维护这份主账。
4. continuation-01/root09-error-1792038493721512900.txt、root09-cleanup-1792038022321090500.json、root09-stop-1792038022321090500.json、api-stop-8.json、browser-stop-3.json。
5. continuation-01/browser-3/proof.json、browser-3.log、15-teaching-complete.yml、17-failure.yml及必要截图；root09-as-run-1792038022321090500.json、before-normal-reopen-pg.json、memory-teaching-before-reopen.json、frozen-memory-binding.json、root09-inputs/proof.json。有权限时安全复用本任务浏览器状态文件，不打印其中的会话认证内容。
6. 当前 frontend/tests/step018-flow.mjs，execution/control.py、runtime_control.py、continuation-01/batch_runtime.py、root09_batch.py，及 backend/tests/fixtures/step018/lifecycle.py 的直接相关段。只读后定位，禁止直接再次运行 root09_batch.py。
7. 116 design/integration-contract.md、acceptance-contract.md、sample-inputs.json、adoption-package.md 的适用项，及原卡所列正常operator许可/资源profile。输入绝对前缀均为 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/；不读取公共库以外其他项目或旧任务私有配置。

主控读取时，TASK-117-result.md 仍为S01历史报告，未包含本次S02完整收口。不得据其文件存在声称本轮已交付。完整产品快照以实际 as-run 清单及本轮新pre/diff/post为准，不拿旧77项快照覆盖现在的84项候选。

## 已核证的事实及不能误认的结论

- root09 的84项 as-run 文件逐项与当前字节一致，浏览器脚本 sha256=3520123fb8080c1487f89b739e673e4368c51d84992a5065c5db01828f48a389；JS bundle /assets/index-D4ghd8lG.js 的实际响应 sha256=6f3f3b0242c5ab0a746e2c861322132dc03383af6ed3a3519e24541feda8df97。未变就复用，不重建、不重跑其完整成功部分。
- 浏览器教学活动 b7f32142-b5b3-4a5c-b561-f927bcbe1b6d 已有 select_node、exercise、answer、evaluate、expose 等14笔新增 committed 回执，最后记录为 answer、applied_revision=16。目标/路径的旧三笔回执也保留。已有错答、针对练习、参考展示、再次作答不应新造key重发。最后一笔answer已提交不代表对应评价已完成；“teaching-complete”截图名不代表独立次数或推进验收已通过。
- 选记忆教学基线是另一活动 bbe0617f-0417-4490-8a8f-354ab0e10ae3；memory c110aa4b-095c-4fec-905d-37fe3922e3cc/version1，不能与上述浏览器活动混为一项证据。原8份文本导入、014兼容前向修补和R01恢复已有部分证据，逐项按层和版本继承，不重复导入或重迁移。
- root09 浏览器在面试页勾选“选用记忆 S02偏好”时失败，错误是 locator.check 后状态未改变；随后异步response.json在页面/context/browser关闭后发生未捕获异常。业务失败与观测/清场失败必须分别保留，不能仅写“客户端额度中断”。勾选失败的产品或夹具根因仍待依据DOM/源码判定，不强制勾选、放宽断言或伪造选择状态。
- browser-3/proof.json 的 status=failed，未记录 browser_closed=true；Node退出1。api-stop-8记录原句柄退出0，PG原时点记录 source 停止/Pid0，固定端口原时点无监听。但cleanup.all_confirmed=false、stop.all_stopped=false；主账 active_root=9 且end为空。历史不能改成PASS。本次主控无法经受限Docker管道重查当前状态，也没有用空的进程查询结果冒认整树已停。
- root09 原业务/清场截止已过。不得恢复其业务时钟、把end置空后续时，或把同一个根整体再跑一遍。原本次运行失败及晚核停止的偏差真实保留。

## 先恢复停止事实，再从持久断点继续

先记录本补充接收时间、当前合同hash、实际唯一接手窗口、当前UTC/QPC及主账hash。先只读核对进程、容器和端口，按已登记CID、PID/birth、原句柄/进程树归属识别本TASK资源。确有残留时只精确清理已证归属的实例；不按进程名批杀，不杀用户浏览器、不重启Docker全局、不删容器/卷/库/行。

为这次恢复另存当前停止核查及适用范围。需要修观测回调时，先保存pre/hash/diff，捕获并收口异步response读体的失败、等候本夹具在途观测并保证finally中的浏览器关闭与回执写盘；不要为消除异常静默吞掉实际业务失败。退出码1不能被当成浏览器整树停止证明。若过去缺少所需身份，保留历史停止未确认与当前可确认范围，不伪造当时browser_closed、StopProof或完成时间。

只有当前精确资源停止条件真实成立，才前向关闭root09并保存晚核证时间、旧失败和保守计时。不得倒填12:28为当时已确认的整树结束；有界根超时与客户端等待仍如实记账。无法确认归属或停止时只停依赖的真实运行，完成证据/文档与可独立离线部分后交回。

后续在新获准根内先GET同一source库的当前head、原command key/record、资格、期限及四账，再选择下一笔未提交的合法动作。成功回执直接继承；无回执但可能提交时先GET原key确认，必要显式同键恢复沿原幂等契约，不换key重复已经成功的动作。旧活动已过期则只读保留，不改期限或额度；新合成活动不替代X09要求的同一正常库/活动连续执行。

## 卡内连续完成的剩余成果

1. 在上面停止门处理后，一次合并修面试页记忆选择的实际根因与观测/清场夹具问题；修fixture不等于可改产品语义。仅有必要产品修正时，沿原白名单与pre/diff/post处理，最终正式bundle与实际加载字节绑定，影响未发生的旧成功证据保留。
2. 在原教学活动从真实未完成的评价/独立复测断点继续，核对曝光后作答、两次独立实例及“推进或保留理由”，不能只按截图标题判完成。完成R+M面试 ask/probe/支持回答/review/finish 与选记忆边界、X02/X04等实际余项；缺项按原116矩阵，不另写一套相矛盾的新流程。
3. 合并完成X09：同一source CID/volume/normal profile，先存L01与I01回答及unknown基线，正常停止重开，GET确认原事实和不重发，再显式继续新的合法反馈/理由。当前root09失败后的重新启动本身不自动满足X09全部条件。
4. 按原P02/P03合同补R01应用只读查看及R02完整31表/向量/007/unknown/已删除源覆盖的真实恢复查看、拒写和坏包failed反例；已有R01装载或seal证据有效复用。不能把直接SQL可读当“应用查看/GET与POST拒绝”全部通过，不把R01/R02目标改成normal继续执行。
5. 按低内存补充完成L10真实固定预览及尚缺的X01—X12适用层，README/配置示例/正常start_local交付与最终case-index。原两次PDF解析失败保持独立未闭，本恢复补充不授权第三次同样尝试或重开已停诊断；没有新的根因依据时不以“下一次可能通过”消耗入口，也不把暂时不跑写成无需验收。将其准确缺口和最小必要处理统一交回，其他可执行目标继续。

以上普通步骤留卡内连续执行，达到一个稳定候选统一返回，不把每次成功点击或fixture修正另拆一张卡。先核已有证据是否足够，不重跑整套旧PG、旧G11/D3或前阶段审计。不新增第三方依赖、框架、模型、持久模型变更包或外围服务。

## 剩余额度及本次明确调度增量

GPT账号Sol配额是平台限制，本卡不能解除，也不能靠反复重试绕过。此次配额中断本身不另记为一次PG/API/Browser启动或业务失败；已经实际发生的root09运行失败、既有启动和已用时间照记。任务执行许可是另一份账，仍是 TASK-117-STEP018-INTEGRATION-S02-20261015，不重新initialize/activate，不建新TASK、R或S03。换模型/窗、自动压缩或等待不退旧时间。

S02首点保留2026-10-15T02:24:00.722344Z，QPC4278922854000，calendar截止2026-10-17T02:24:00.722344Z，活动28800秒、25200后不扩新目标、27000后仅保存清场、最后1800为收尾。原时钟域未变时，对应本地当日17:24不扩、17:54仅收尾、18:24总门；以实际统一账/可靠时钟域核算为准，不能只看日历48h。换机/重启不直接减不同域QPC，不确定时用原UTC/已有可靠点保守补账，不能获得新28800秒。恢复时已过门则不运行新业务，先完成准确核证/清场/报告，具体余缺交回主控。

主控核证观测：root9，PG create/object/volume3，PGstart12，API8，Browser3，build4，Native预记51，HTTP278，preview create/start0，provider/fee0。已结束S02 runtime_intervals合计430.752秒、offline_intervals812.968秒；root09尚未结算、资源持有另账尚须合并，不能把这些小计写成全部已用或扣掉中断时间。2026-10-15本次观测仅是快照，启动前按唯一账重算实际剩额。

为避免原两次API余额迫使同库重开与两种应用恢复查看互相挤占，本次只追加如下前向调度许可：从实际接收本补充起最多4个新S目标根，S累计最多13，TASK最多14且仍为未来Q保留1；API累计上限从10改为14。当前已用根9/API8、旧9根内全部失败不减计；原低内存补充的S根11/TASK12和旧API10保持历史，并由本段明确替代其调度上限。

执行者仅在原主账前向追加本补充采用记录和新调度覆盖，guard读取有效覆盖；先存原guard/账身份。不要把旧cap或旧失败改写成一直拥有13根/14次API。不得借关闭旧root09向其补时，新增真实入口在新根计数，所有启动仍累计。

除此之外时间、持有、离线、物理资源、费用和启动门不加：S02持有10800秒/offline3600秒，PGstart20，PGcreate8/对象5/卷5，Browser8，build5，Native160，preview create/start12，HTTP3000；每个真实根2100秒业务+300秒清场，单活动preview原3次/180秒不变。总活动/持有/离线不同量分别核，不用窗口数多冒总时间足够，不把所有额度当必须用满。

正常同库重开、两个只读恢复API及L10按实际依赖归并安排。先保证必要前置，允许同一有界根连续串行阶段；不要为等代码、审批或聊天让PG/API空转。不能因本补充有新调度门而重跑已充分部分。新根/API预算不足或原总门先到则停受影响运行，准确收口，不能暗开下一批。

## 内存、资源和禁止事项

低内存许可继续：默认PG1；第二PG仅必要恢复短窗，API/host Browser/preview先停。基础/单PG/API前可用物理内存512MiB，host Browser/第二PG768MiB，固定preview1024MiB；Docker暖机后每次启动各实采。约2秒采样，连续两次低于256MiB即拒新工作，已登记闭包先消费者后API/PG精确清场。未知采样拒本次启动，不反复让用户释放到2GiB。

PG原512MiB/1CPU/pids128、固定preview1GiB和等额swap/pids256、网络隔离、只读文件系统、正常验签、Job/EOF/身份/StopProof不减。build和离线在运行资源已停时完成；L10与一般UI可按依赖分时，必要U门不删，不用静态图/route替身冒真实宿主。特定阶段实测放不下仅标对应依赖受限，不降低验收或无限轮询。

资源仍限原source/compat/r01及已许可r02/r02-fault五slot、原精确CID/卷、15481—15485/18118、固定已缓存镜像、正常安全loader与本TASK私有synthetic凭证。不重建原库/行，不删卷、改端口、拉镜像或安装依赖，不读取用户数据、别任务private、真实key/DSN。正常operator rekey沿已批准授权，不向用户索key、不改验签门。共享DocuS/任务卡/主控裁定/公共规则/Git/原需求不由工程执行者修改。

## 停止、证据与回传

同缺陷两次有据修正仍失败、关键根因不稳、权限/资格/停止不明、新高风险或任一硬上限先到，停止受影响动作，不换名称绕计数。平台仍报客户端额度或审批服务用量限制时不机械重试，真实资源必须由事先登记的有限控制器独立收尾。不能承诺平台不会再中断或实现一定无缺陷。

执行仍独占原产品白名单及 execution/continuation-01 的本轮新证据；保存每次as-run/pre/diff/post、真实回执、加载bundle、原始错误与预算/资源账。旧证据目录不覆盖，browser-3原FAIL不重写，新增恢复证据用新文件/唯一后缀。不将业务提交成功、浏览器操作成功、观察器退出和资源整树停止互相替代。

最终更新并复读 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-117-result.md，新增当前S02接续段置顶，原S01历史全文保留。逐项列：已交付、证据层/对象版本/复用、实际未完成与原因、产品/夹具差异、全部失败和偏差、各段及累计额度、最后资源事实和未确认项。源码写入不冒真实通过；S不冒Q，工程不自签独审、STEP018/019/020、M-1或项目完成。

稳定完整S结果回传后，主控安排新隔离增强窗口集中独审；本卡中途不每改一处插一次审计。必要人工仅转交本卡到唯一有可用额度的A+工程窗口；不要求用户提供密钥、系统操作或逐步批准。保存可读后，只回一句准确结论及上述结果文件的可点击绝对路径。

## 以下为原低内存、S02、S01完整合同及历史


# TASK117/R111 S02 — 低内存串行执行补充（当前有效）

用户明确表示没有更多内存，并要求在现有条件继续。主控允许原A+工程窗口按以下测试资源profile推进，不再以统一2GiB门要求用户释放内存。本补充优先于原卡/S02的2GiB测试预检及下述根调度项，其余范围、时间/费用/安全/验收不变。

## 调整依据与正确边界

执行窗口报告在Docker暖机、所有本任务PG/API停止后约1.66GiB可用；已有post-root07-memory.json记录停止时1.717GiB。2GiB当前只是runtime_control.memory_gate的统一夹具阈值，没有产品最低内存实测结论。本次改变的是测试启动策略，不是删除内存观测或放宽安全隔离，也不证明1.66GiB一定足够每个场景。

不要减少PG既有512MiB/1CPU/pids128限制，也不要改变固定preview的1GiB memory与等额swap、pids256、read-only、network none、cap-drop、sandbox/Job/EOF/nonce/验签/StopProof及固定程序。不得为省内存添加关闭安全机制的浏览器参数，不改WSL/Docker全局资源、系统分页或用户软件/进程。

## 分时安排

1. 默认同时只运行一个本任务PG；完成一个目标就精确停止。compat检查、source快照/业务、恢复target逐段进行，不为等待代码、审批或人工保留PG。读取/计划阶段仍可做纯离线工作。
2. 源与target确需同时存活的真实恢复/校验短窗允许两个PG，先停本任务API、外部UI浏览器和preview；不以串行为理由破坏恢复算法的源pin/权限/事务前置，不伪称一个库完成了两端验证。若应用查看只需target，停另一个PG后再起API。
3. API只配当前目标PG按需运行。host UI浏览器单实例/headless，复用同一浏览器上下文内的必要流程，避免保留多个页面/全程视频/不必要全量trace；保留正确断言、关键失败DOM/截图/加载身份。不要重建未变bundle或重跑已充分方法来花内存。
4. L10固定preview与一般两链UI分段。优先在停止外部UI浏览器后，经真实API/原宿主协议验证已冻结artifact、d/t输入、ACK/PNG和停止证；教学入口到父身份/生成回执的最终bundle验证单独保留。若既定U门确需UI与preview同时，则按实测余量短窗执行，不能用静态图/纯mock冒实际交互或删掉必需门。结束preview并证明确停，再继续其它UI。
5. Typecheck/build/离线检查在所有本任务PG/API/Browser/preview已停后进行；已绑定的build4如未变直接复用，不添加依赖、不改锁文件、不重新构建镜像。控制器的2400秒根/2100秒业务/300秒清场和S02总窗继续。

## 分阶段预检和运行压力退出

允许工程修本任务runtime_control.py、continuation-01/batch_runtime.py、profiles_batch.py及必要本任务fixture的调用位置，先存pre/hash/diff。本补充不能被实现成只把所有2替换为更小数字，必须标明确切stage/阈值/样本时间/当前本任务资源/结果。

- 基础预检、单PG启动、API启动要求当时可用物理内存至少512MiB。
- host UI浏览器启动、确需的第二PG启动要求至少768MiB。第二PG同时必须满足上一节API/Browser/preview均停。
- 固定preview启动要求至少1024MiB，并先清除可分开的外部UI浏览器/不相关PG。若preview与UI存在不可拆的真实依赖，两个各自启动点都核其对应门，不因其中一个已启动就忽略第二个门。
- 每次启动前在Docker已暖机后重新实采；同窗旧采样不替代当前值。未知/采样失败保持拒本次启动，不拿磁盘空余或pagefile字段冒物理内存。
- 在已有有界控制器中每约2秒采一次物理余量，记录有限摘要/最低值/压力事件。连续两次低于256MiB时停止新增本任务动作，并由已登记的原清场闭包先结束高占用本任务消费者，再API/PG；只动自有精确实例，按原证据确认，不依赖下一条工具批准。OOM/进程异常/不明停止也记录为实际失败或未确认，不写通过。

这些是本轮低内存试行调度值，不是硬件容量保证。未达到某类门时先精确停本任务可拆分消费者，再采一次；仍达不到就停止该依赖段并完成其它部分，不无限轮询、不反复让用户释放内存。若只有固定preview实测资源不足，只将对应L10/相关必要U门标受限，不能冒整个产品通过，也不阻碍其它真实PG/API/UI/文档收口。

## 在途、计数及根安排

S02已实际接收，原首点2026-10-15T02:24:00.722344Z、S02-host-restart-new-QPC与首采样回推/保守5秒说明不改；旧S01/QPC不同域不能跨域直接相减。当前在途观测root8、PGstart11、API7、Browser2、build4、Native预记31、HTTP164等只作观测，执行者以唯一主账实际最新值为准。

为把原未完成目标按内存分时而不强塞同一并发批，本次只调整根调度上限：从本次收到时最多再开3个有界S目标根，S累计最多11，整个TASK最多12且仍另保留1个未来Q根；原S01/S02历史根/失败原文保留，不减计或将已结束根重新续时。不得把同问题两次失败换名后无依据再跑。

不增加S02活动28800/日历48h/持有10800/offline3600及其累计门，不增加PGstart20/API10/Browser8/build5/Native160/preview12/HTTP3000或物理对象/卷预算。不重新起S02首点，不将等待内存的已用时间退款。分时也必须服从这些原剩额，启动次数不足或硬门已到则停止相关操作交回，而不是偷偷延长。

仍TASK117/R111/S02，不建S03/118，不启真实provider/费用，不动已批准20元/80次Q门。原operator认证正常流程和旧结果/preimages/全部失败不改；本次不修PDF解析失败，也不将memory门解除写成PDF/Browser通过，独立缺口按真实根因分别处理。

读取本补充后，在原唯一budget/events中前向追加low-memory profile及根调度采用记录，不覆盖旧permit/原cap/失败；更新本轮辅助guard并继续实际剩余目标。产品源码/共享DocuS/公共规则/原始需求由原分工维护，主控不接管实施。新合同hash须实际读入后记录，不能追认已按新门跑过。

最终与TASK117统一结果回传实际峰值/最低物理余量、各阶段门、启动/停机证、所有失败和受限项。允许继续低内存工程，不承诺所有真实矩阵一定能在该设备关闭。

# TASK-117 / R-111 — S02完整合成集成收口续作01（当前有效）

## 目标、接收与授权终点

接收A+增强执行Agent，继续原TASK117/116/114工程窗口。实际客户端/型号如实记录，A+不冒型号。人工转卡，未确认接收前不视为启动；不派子Agent、不并行写产品，不承担独立审计。

本轮许可TASK-117-STEP018-INTEGRATION-S02-20261015。用户已采用AP1/AP2并带回部分结果，主控在既有开发范围内追加明确的原卡续作许可；不是要求用户重新批准项目/模型/20元。当前只允许S合成候选，Q仍未启用，真实供应商调用/费用0，个人资料/用户库0。

根D:/shspic/project_NO3_RetroLume-agent；入口同根AGENTS.md；task_model/V4.0/公共AGENTS CHG-0003/阶段07。公共只读根D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，仍按原卡AGENTS、WORK适用章及七锁定指纹复用；本轮需求v1.3、架构v1.35、执行动态v2.60。未变材料不再全文重读，不自动采用新公共版本。

本轮完整成果仍是原AP1两条学习/面试主链、hybrid/记忆/四账/同正常库重开、014/R01/R02/启动文档的稳定S合成候选。将剩余实现、夹具修复、分层验证、普通修复和准确收尾连续做完，达到稳定候选后统一回传。S完成不冒真实服务语义Q通过，也不签STEP018全部/STEP019/020/M1或项目。

原S01已部分停止，所有失败、超额、UNKNOWN、数据库与原件保留。原活动/持有许可不能继续消费；本补充只给下述前向段，不把超额追认为合规。新旧计数/资源仍归同一TASK117/R111主账，不另建零账或新TASK118。

## 接续位置与必要输入

先读本补充和原卡未变合同、主控S01接收裁定，再从保存事实继续。

- D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-117-result.md，S01报告sha256为db9dd539274c9b77db237410de31a6c9cc75595bae3b758d6e6c2d5573351b53，21405字节；原文保留。
- D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-117-work-decision.md本轮裁定。
- D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/execution/final-source-manifest.json，共77登记项，sha256为a5610ca9591cefd9e20a58c06a2416196179feb84c8b1247df64f9c8cfc2c210。当前改动有pre/diff/post，旧dist删除项按post.exists=false核，不重造历史文件。
- 同execution目录final-binding.json、result-save-receipt.json、final-resource-stop.json、final-budget-observed.json、final-holding-union.json、budget.json、events.jsonl、case-index.json、official-check.json。
- 同execution目录root02-retrieval-proof.json、root04-flow-proof.json、browser-2/proof.json及对应as-run/raw；它们是部分实际成功证据，按对象与版本复用，不能签冻结L01/I01或最终全量通过。
- 同execution目录runtime_control.py、root04_start.py、root04_http.py、control.py和root05_profiles.py，只读取到具体根因再修，不直接运行未审草案。frontend/tests/step018-flow.mjs有选择n1的未跑修正，且错误处理仍须保证超时/null回执能准确保存/退出。
- D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-116/design/integration-contract.md、acceptance-contract.md、sample-inputs.json、adoption-package.md原冻结规范和本卡原S01语义；不重写方案。
- D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/orchestration-preview-config-20261014/notice.md正常operator授权继续有效，原控制器退出后内存key已失，需要正常rekey并实际注入新API子进程，不向用户索key，不假定原票据可直接复用。

已存在的source/compat CID、volume、持久事实/角色/本TASK117私有凭据只在正常安全loader中沿用；不得为接续丢数据、换名字、重建或回填旧成功。你可读取本TASK117自有private配置，不读取111/114等别任务private或真实用户配置。

可接续原浏览器活动b7f32142-b5b3-4a5c-b561-f927bcbe1b6d的已提交目标/路径，先GET实际当前head/期限/原键再显式选节点。HTTP教学498ed460-7006-42e3-a8ab-04dfcfb2712f、面试d3ee1276-b628-4834-8344-0171c6703c14（已ended）、检索0830ec45-bd62-45e9-9f4d-c773a3ce635b保持原事实。旧活动如已到deadline只读保留，不能改期限/预算续命；在本轮明确的新合成场景中创建新活动，并保留原尝试/全局账。X09必须用未到期的同一正常库/活动真实停止重开完成后续动作，不能拿另建活动替代。

## 一次合并完成的余缺及准确预期

1. 先补本卡测试控制器的完整有界收尾，再启动任何PG/API/Browser。S01明确根因是source被root04_start.py独立启动，API控制器到期只关闭API，PG在审批阻断/聊天中断后继续运行。所有本卡PG/API/browser/preview必须归当前同一有界控制器登记，业务截止、异常、子进程失败、正常退出均进入精确清场；真实超时动作不能依赖Agent再次获得工具审批。优先修现有fixture/controller，不新建常驻服务、第三方框架或多层看门平台，不改产品SUP/Job/退款主体。
2. 修X07整步预算预览门。当前逐笔准入正确不等于整步可执行：剩1request而query+model需2时，在第一个query之前明确拒整步且无外发。仍保留服务器逐笔PG事务准入，UI预览不冒原子预留，不为此加入未采用的新通用预算表。新的source_index批数/费用预览及记忆/当前domain身份按116合同同步，不暗中多发。
3. 完成既有OutboundGrant source_manifest_sha256到实际source/version/必要片段集合的采用闭包，补合法grant离线/合成正例、过期/篡改/不在roster/不在白名单/跨活动并发价额反例；model/embedding共用同一PG累计门，未知不退、grant不可重绑。不能只验证64位hash格式而不比较实际外发范围，不能借有key或本轮operator票据开Q。这是原AP1/X12未完成部分，不另扩平台。
4. compat补齐最后已批准的invoker teaching_commands只读授权，与当前014可信定义/源库逐项对账。既有source/compat不能重新跑001—014建库链或吞重复迁移错误；必要最小前向ALTER/GRANT修补明确写before/after、对象定义及事务。014文件继续给全新库正确最终定义，旧001—013不改；新catalog/fingerprint必须由已采用DDL与准确增量逐项解释，不把任意DB实测shape自动学成可信基线。
5. 审查root05等草案的入口、包路径、R01/R02/profile/断言和权限后，合并完成P01最终非空旧model/tool/unknown/domain/预算不变及R01包、P02旧链新隔离只读目标、P03新R02包/31表/向量float32/007/grant及unknown往返、坏维度/hash拒绝/failed不激活。R01/R02永不转normal，loader只loading、seal后真实拒写。成功目标与failed目标不可复用，source/compat原卷/事实保留。
6. 完成冻结正确输入的最终bundle学习链，而不只原N正确答案状态链。补wrong_answer、针对新题、新实例复测/曝光/独立次数及推进或保留理由；核L02—L09正反/单位/否定/概念/程序/歧义/冲突的协议及本地确定检查层，程序题不执行用户代码。冻结R+M面试链、必要probe及I02/I03证据不足/自报/错引，选记忆的学习与interview.v2实际链及修订/撤销/删除失效传播。明确S用最低传输替身，正确模板不是Q语义质量证明。
7. 补固定预览L10的真实artifact/父资格、v2-08真实宿主、d120/t120读1→t240读0.5、t0/未知字段前拒、reset回1及原StopProof/EOF/双Job/CID闭包。先审本轮合成HTML回复符合冻结有限描述，再启动；不签票绕过正常loader、不改固定程序，不重跑G11已足够的全套宿主反例。原25/UNKNOWN/R60/count1不触碰。
8. 合并完成X01—X12适用S层余项，尤其PDF-2逐页确认与失败隔离、同键/CAS/并发、COMMIT丢回包后GET、scope/源/记忆/view/DataContext晚到、source删除后007/cache/快照/恢复不可旁路、真实同normal库正常重开后的新feedback/理由。用一学习域/一面试域代表传播再加新kind/profile的针对例，不枚举笛卡尔积，不把route替身冒真实后端。
9. 后端/前端必要修正集中后再正式build，最终bundle绑定实际HTTP/Browser，统一更新README、公开integration/teaching配置示例及preview README陈旧候选文案，并实际走一次现有start_local的本轮正常合成profile启动/就绪/停止/同库重开。启动器只能复用精确本TASK资源，不重新初始化正常库或迁移用户库。缺能力/只读/未知/剩余预算文案必须准确。

当前28冻结场景均未整体通过，不以此否定已得到的typed/PG/HTTP成功方法。分层收口S后，Q仍记未启用/未验证，不能把不具真实provider的S完整候选称整项目已过。

## 收尾关口先行与审批受阻的处理

新PG/Browser启动前，先对现有控制器补最小有意义的确定性自检，证明业务截止不需新工具命令便触发其所有注册自有资源清场回调，子启动失败/异常也进入finally。再在本轮首次真实批结束保存PG精确stop/inspect、API/browser句柄等待及无自有监听证明；未证闭环就不能让后台资源跨工具等待留存。定时清场逻辑随当前本卡控制器运行，不能仅在聊天里约定“稍后停止”。

每个真实完整目标根业务持有最多2100秒，最后300秒仅清场，本根全部资源从启动到精确结束不得超过2400秒。根内有限正常操作/普通修复可连续，读代码/长编辑/等人工/等审批前先停归属资源；后续在本根是否可继续以原deadline和真实剩额为准，不重启同根时钟。跨根资源全部停止确认后再开下一根，不藏后台PG持有。

自动审批服务的用量限制不是动作不安全的证明，也不是主控能取消的平台限制。曾拦截的第三次Browser未执行、旧browser计数2保持；保存失败请求和未执行事实。新许可不恢复平台审批额度，不绕审批或改工具/客户端降低权限。如果所需启动仍被同样拦截，立即停止该依赖段并由已有控制器完成清场，不重复提交相同命令耗时、不让PG等待；可完成不受影响文档/离线工作后一次交回具体平台阻塞。

首工具重新实际采本段UTC/mono。原S01活动到最后保存为37651.0027854秒，原28800上限超额8851.0027854；停机点36673.4247854不是最后写盘值。保守运行持有16219.360/14400（实际CID并集另为16216.391），离线1724.875。全部原失败/错记修正/缺birth/少pre原文保留，不追造实际StopProof或运行日志。

## 明确前向预算及累计门

本段S02新增活动最多28800秒，包含准备/普通等待/实施/测试和最后1800保存清场，接收后48小时日历。到25200不扩大范围，到27000只收尾。新段开始前的停线间隔不追称执行活动；原S01首点/活动/超额/日历原字段不改，新增S02实际首点与段账。累计已用显示S01封存37651.0027854加S02实际，新增授权的累计活动门66451.0027854；这不把旧超额追认为合规。

新增真实运行及持有最多10800秒，旧保守基数16219.360和旧原上限14400保留，前向累计门27019.360；另存真实资源区间并集，不能悄改旧保守基数少计。新离线最多3600，仍同时服从原总offline7200；旧1724.875加本段不超过5324.875。总活动/持有/离线分类不同，不能用子余额越硬门。

新完整目标运行根最多5，旧4保留，S累计最多9，整个TASK总根最多10且保留1给未来Q；原S01 4/7历史不改。建议依赖合并为控制器/预算闭包及当前合同定向检查、profile/两恢复、冻结两链与预览、故障/正常重开、本机交付与必要一次最终定向复检；可按真实依赖安排，不强制跑满或拆更多根。

正式build明确增加2次，原3/3用满的历史保留，TASK累计最多5。API新启动最多5且累计最多10，旧5/8保留。Browser本段最多6且仍服从原累计8（旧2），PG start本段最多17且原累计20不变。PG create总8/成功对象5/卷5、Native总160（旧预记28，保留其保守性质）、preview create/start总12且每活动3次180秒、HTTP总3000（旧146）均不扩，同在PG2/API1/browser1/preview1不变。

只复用原两个PG并使用原三个尚未建立target；禁止额外新名字/卷/库。两旧CID：source=1df68961975a43929fa06f63314a0da6e4e5cea113e3c403fc1ffd90d7c0fa5f，compat=0741d770fe07cc145660929044c471ef73fee11bb58e3ee6593e9a47adaa67c8。原name/volume/15481—15485/18118/image/labels/CPU1/512MiB/pids128/restart=no/loopback及原资源profile完全继承；label中的S01许可保留，登记S02对同一对象的前向复用，不重打label隐藏历史。

每次实际依赖启动前核可用物理内存至少2GiB、缓存image/内核/精确CID/全部端口状态/独占bind与owner。资源不足先不启、准确停已拥有资源并继续离线，不停用户进程/改系统端口。旧停止证是上轮时点事实，不能直接当今天启动前状态；主控没有重新运行Docker核现场。

官方文档可新增最多8个准确官方页面目标，旧10个目标/失败/可访问状态保留，累计最多18；优先补直接Embedding官方API/定价/条款和Chat候选差异。不整站抓取、不读账号、不发模型试探。现有报告记录的候选差异仅列Q精确待核/待采用影响，不能擅自改DeepSeek候选模型或供应商/维度。无法取得只影响Q准备，不能冒S工程未完成都是外部服务原因。Q的80次/20元许可不重批、不扩大、不激活。

原S01预算文件/事件不可删除或将permit/start/caps直接改成新值掩盖超额。沿单一主账前向追加S02 activation/segment/limits，保留S01封存hash和原字段；活跃guard可以明确识别本S02许可与本段首点/到期/子门，不能靠改原start_mono_ns续命。所有尝试与真实持有按原账连续，加S02原件导航。原root04控制器、预算/现场观察/错误日志全留。

## 文件权、验证范围和完成回传

原完整卡允许的产品写范围继续，只改本轮列出的原标准余缺及实际回归，不重写实现、不改用户需求/公共库/正式DocuS、旧001—013或固定preview/SUP/Job/停止退款核心。原S01新测试/fixture可正常修；本TASK控制器control.py/runtime_control.py等可作上述收尾/新段识别修复，先存当前副本/hash/diff，既有原始events/失败/结果不可覆盖。无需为漏列的同功能普通适配每个文件问用户；超出原模块/新主要数据或外部权限仍交主控，不广泛重构。

新增验证文件优先写D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/execution/continuation-01/，旧证据原字节保留。只允许正常单一budget/events追加和同一结果文件前置本轮段；S02首次改某产品/fixture给准确pre、变更理由、diff、post及as-run绑定。新快照与S01保留并存，不能用新hash覆盖旧失败的实际版本。

复用相称成功方法，不重做原112/G11/115整套或已有无变化的索引/HTTP调用。ROOT01初版12方法与后续v4/null改动存在版本差异，只做其实际影响的最终合同定向复检；真实PG/Windows/HTTP/bundle和纯替身分别标层。新target/profile确未跑，不能引用准备脚本的存在代替通过。数值/引用位置通过不签开放语义质量。

某问题两次有据修正仍失败、根因不稳、关键前提推翻、越权或任一门到限即停相关路线，完成不受影响部分并保存准确余缺。一次明确正常/负例不是重试，但同问题换脚本/窗口不清失败。已有审批服务阻塞不用机械第三次提交；源码/夹具错误依实际根因修，不删有效测试、弱化断言或静换模型求绿。

S稳定完整后精确停机统一交回，主控再给真实隔离A+集中独审卡，只审新类型/接口/权限/预算/014/R02/最终bundle实际影响；不在当前不完整阶段先插一轮全面审计。工程不能自签，S02也不代表Q真实语义；后续同工程窗Q接续与原独审增量仍按已经批准的条件，不重新请求20元。

结果仍D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-117-result.md，置顶续作01保留原21405字节全文。先写完整S完成/部分的真实结论、未启Q/费用0、修正与有效原证/新增层、28 case-index、最终profile/014/source/bundle绑定，再给失败/超限/活动和资源区间/次数/精确清场/保留对象及未验证。包括审批被拦动作未执行，不伪填tool回执或平台恢复。

确认唯一结果完整可读并保存hash后，只回一句结论和绝对结果路径。共享编号/DocuS/最后验收由主控维护；没有新关键许可缺口不重复问用户。旧剩额、历史超限和全部Must不清，未完成不改口为已验收。

## 以下为S01原卡及operator补充历史，未覆盖旧失败或修改原文

# TASK-117 / R-111 — STEP018完整学习与面试集成

## 目标与交付

你担任本卡增强执行Agent，在已批准边界内连续完成一个完整工程成果，不承担独立审计或项目最终裁定。

交付目标是用户在本机从资料入口连续完成学习和文字面试两条主链，hybrid检索、引用、低信任记忆、持久预算、失败恢复及同一正常库重开贯穿。现有领域实体、007原子正文、CAS、四账、Windows监督和固定交互宿主直接复用；不是重建这些模块。

当前有效执行段S交付完整合成集成候选。一次覆盖必要官方文档核查、实现、离线检查、真实专用PG、Windows监督、HTTP、正式bundle浏览器两链、正常同库重开、R01/R02隔离只读恢复、文档和普通修复，达到稳定成果后统一回传。Q真实服务语义段已获用户条件性费用许可，但须稳定新增边界独立审计及主控启用回执后才能进入；当前S段任何真实供应商调用/费用均0。S完成不因为Q尚未启用而虚报失败，也不宣STEP018全部完成。

学习链包括资料导入与全部PDF核对、范围/必要用途确认、目标及澄清、路径、初题、保存作答、有据反馈、针对练习、固定交互解释、复测、保存推进或保留理由和明确下一步。面试链包括资料/目标、问题、回答、必要有限追问、有据反馈、结束及重开。不是仅生成首题或显示历史。

具体交付是本卡产品增量、28个场景的分层证据与继承导航、最终源码/bundle/profile绑定、单一真实资源和预算账、本机README、唯一结果文件。冻结语义预期来自116验收合同；不得以替身给定答案冒真实服务语义。

## 项目、规则、批准与接收安排

项目根目录 D:/shspic/project_NO3_RetroLume-agent。
根入口 D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。
模式 task_model，锁定V4.0/公共AGENTS CHG-0003，阶段07。

公共只读根 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4。
读取该根DocuS/AGENTS.MD；WORK.MD只读第2章task_model分工、第5—6章适用审计/验收和第9章Agent产品边界。卡模板为该根task_model/TASK_TEMPLATE.md。七条锁定身份在D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/v4-migration-20260930/rules-snapshot.json，不自动采用新版本。

关联 STEP018、后续STEP019/020；父TASK116/R110；FR001—004/006—012、NFR001—005、DR001—003、SEC001—003、INT002及既有G3—G11/有限STEP017。新卡不恢复旧任务许可，不清旧失败/费用/UNKNOWN。

当前生效需求v1.3、架构v1.34、执行动态v2.58。原始需求仅用户维护。新v1.3只登记本次采用增量，不删除原31项编号/Must或扩成真实个人数据授权。

授权依据是用户在编排展示AP1与AP2具体范围后明确回复“一并批准”。原文、绑定采用包hash及有效门保存在D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/orchestration-20261014/adoption-receipt.json，主控裁定为D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-116-work-decision.md及TASK-117-work-decision.md。设计完成/用户费用批准均不代替新增边界独审或真实能力/价额核对。

接收A+增强执行Agent，继续TASK116/原TASK114工程窗口。该窗口已实读116全部设计并持有工程事实，复用上下文避免重做；不是独立审计窗口。最近自报为Codex desktop/系统GPT-6，具体后端子型号未披露；本卡不冒认客户端或型号，实际接收者如实登记。不得派子Agent、并行改写或调用审计窗口自签。

许可 TASK-117-STEP018-INTEGRATION-S01-20261014。当前只有S01合成工程段可执行。实际接收时首工具同步UTC和mono，签发时间不冒接收首点。旧材料同窗已读且未变直接复用，只补本次采用/正式文档和卡面变化。

TASK116设计活动5133.7887266/7200与2066.2112734封存，原114/115及13元/626.566/25/UNKNOWN/R60/count1等历史继续原账；原图/代码/充分证据保持。TASK117在签发时未接收/未运行，新增使用0，是新完整集成成果预算，不是旧失败重置。

## 最小充分输入与对象身份

先读根入口、锁定公共规则、本卡和以下材料；已有同窗有效内容不全文重读。

- D:/shspic/project_NO3_RetroLume-agent/DocuS/最终需求文档.MD当前采用段及相关Must。
- D:/shspic/project_NO3_RetroLume-agent/DocuS/架构动态文档.MD、执行动态文档.MD当前顶部和本卡相关实际机制；旧未开始表不覆盖当前裁定。
- D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-116-result.md，设计结果sha256为1a0da889b0636437bf6652669b35d4911fefcbdbb77213a53c41b641b0b1949a。
- D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-116/design/integration-contract.md，sha256为7b053fedc7424373a04a06e8f6966ead15b5dad2e01fb9f0d1f201b50df43cea。完整A/B1—B7是规范合同，不按聊天回忆重写方案。
- 同design目录acceptance-contract.md，sha256为ed147e7e79763c454d712cf129f3d4e94634661d0385c8c3b781e1c058f66e3c；sample-inputs.json为304a4b131d04cd4132334bebd091f94ff62bec5660698457487e14136023c113。
- 同design目录adoption-package.md，sha256为84cb852946220a09873225f8bde7b7138aa7366e137297638bb2aab01dbc1c84。其原文“待决”是历史，本次生效以主控批准回执和本卡门为准，原文件不改。
- 同design目录actual-call-map.json、source-identities.json、sample-identities.json、git-baseline.json、consistency.json；D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/orchestration-20261014/input-manifest.json给本卡实际输入和允许文件pre身份。
- 原TASK115 review-02/114 C03终审、TASK112/111 G11稳定原件只按本卡实际直接依赖读取。原115在D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-115-result.md，G11在TASK-112-result.md；不重新运行旧runner/全套旧保护层。

原Git HEAD为45951501d2741630a229762d6b2d3f4b34d7f702，116只读porcelain633行属既有成果。HEAD不冒当前产品快照。首编辑前逐个核实际受影响文件pre并留必要副本/hash/有限diff；设计66项源身份中未改产品可继承，不再全仓重hash243件。未知漂移先核归属，保护用户或其他成果，不reset/stash/覆盖。

## 采用后的工程合同及不得放宽的语义

AP1已采用以下唯一方案，具体DDL/接口/正常失败时序沿integration-contract B2—B7。

1. 新014_step018_retrieval.sql，三表retrieval_spaces/retrieval_commands/retrieval_chunks及activities.outbound_grant_sha256可空列。新embedding kind独立typed request/credential/outcome/007值，不伪装chat/tool；wire v4封闭union，旧v3聊天字节及旧profile事实可读。输入向量同空间、512维、有限非零；源版本/片段/物理页/补充身份和每次原件回查保留。
2. 同space精确cosine与词项RRF60，目录有限、显式索引/查询、每批最多4片段/每片段2048codepoints、query1024chars/4096bytes。命中缓存不虚造收费调用；unknown不暗换query重复收费。旧terms.v1仅可明示降级，不冒hybrid验收。完整参数、批次及正文上限沿116。
3. received+007正文+向量或领域投影同一短事务；取锁相对顺序、代次/取消、当前scope/source/memory/domain绑定保持。新增grant锁在source等锁前，不能反向嵌套。旧tool的NULL request/token、零费用形状原样保留；model/embedding独立核次数/费用/时间，不能用统一非空正值约束伤旧行。
4. learning.v2/teaching.v3/interview.v2严格冻结检索引用；面试新v2可在创建时显式选最多4条学习记忆为低信任背景。旧v1拒选记忆语义与原请求hash保持，记忆不当源证据/测量，不把新功能的加入追认旧有限验收失效。
5. R02精确001—014/profile/角色/函数/trigger/31业务表及活动grant列传播，R01仍其原001—013和28表/原包规则。迁移非空旧model/tool/unknown/domain/预算不重算；新表写guard/loader/seal/purge权限精确，PUBLIC不得获新执行权。快照不能以索引可重建为由丢受控调用和预留事实。
6. 正常同库重开先GET原意图/事实/heads/预算，再明确继续合格未发动作；不复用旧lease/generation，不自动重放unknown。恢复R01/R02的隔离副本永久只读，不转normal，不继承执行权/secret/SUP，不能作为正常库继续的替代证明。
7. Windows原生API/SUP/Job继续，PG按已有Compose承载，预览沿固定v2-08宿主动态创建。无常驻renderer、Web Docker socket、SDK、Redis业务依赖或新框架。Linux/Nginx完整公开部署保持后续条件目标，不凑技术词扩平台。

两项主控解释必须与上述规范共同落实。

- 取消或其他失效之后的新结果只沿原record_outcome的UNKNOWN诊断，不新增received正文/向量。已经COMMIT的事实仍可按持久记录核对，当前展示/投影资格抑制；116“晚到007事实”的概述不得解释成放宽原资格。
- 向量hash定义于实际存储并可恢复的规范数值表示。实现先收敛pgvector浮点量化/序列化，再保证007、数据库回读、R02往返逐项一致；不能用供方double原文本hash声称PG存储逐字相同。使用现Python/SQL，不为此增依赖或另开研究卡。

AP2已获用户条件性批准，最大80次/人民币20元新总额，仅冻结合成必要片段、DeepSeek chat和智谱embedding-3/512候选。当前S阶段不得激活付费gate。以下准备属于本卡，不能把它写为“费用仍待用户批准”。

- 可在实施前做最多10个官方页面的必要只读核查，限DeepSeek官方文档/价格/条款域及智谱bigmodel官方文档/价格/条款域；可用web搜索但只采用官方原文，不上传项目/私密，不登录账号、不发模型API试探、不安装/下载实现。记录日期、精确URL、模型/返回别名、维度/批量、计量、价格币种/税边界、必要账户条款及适用性未知；仅保存必要摘要，不能整站抓取。该有限外部文档读取是本卡明确授权的必要输入，取代116草案的“另行核查范围待给”，不是新增调研任务。
- 官方当前事实若推翻候选能力，不静换供应商/模型/512维或超10s时限；保留合成实现和准确差异，暂停依赖的真实启用，交主控必要采用变更。一般实现细节、名称映射依据已核官方事实即可决定，不为普通细节重复问用户。
- 新真实model/embedding要求受信OutboundGrant，固定活动roster、批准回执hash、source_manifest_sha256/price_snapshot_sha256/有效期及PG跨活动累计核门。活动grant只能受信create绑定，不可重绑；没有/过期/不匹配就关闭真实外发。所有新API继续session/DataContext/mutation gate；GET不触发模型、Embedding或SUP。
- 用户批准不是当前账户适用性/凭据存在性证明。密钥仅正常server env loader读取RETROLUME_MODEL_API_KEY及RETROLUME_EMBEDDING_API_KEY；不向对话索key、不读旧任务private、不写日志/证据/导出/前端。缺密钥不阻塞S合成实现。
- 只有未来主控给出新增边界独审可用结论、官方核对记录及Q启用回执，原窗口才可进入Q。Q活动时间/资源继续本TASK原账，不借审计预算；S收尾必须保存准确剩额，不在本卡等待期间保持资源运行或暗开付费。跨审计需要续作许可只是启用门/有效执行窗登记，不是重新审批20元。

## 允许写入的产品与测试范围

以下相对路径均相对实际项目根；只改本合同的接线/新类型/profile/权限传播，不顺手整理全文件。不存在而标新增的文件才可创建，已有冲突先保留。

backend/app现有允许范围

- main.py、service_config.py。
- capabilities/contracts.py、gateway.py、transport.py。
- worker/one_call.py、worker_main.py、launcher.py、session.py、command.py仅新封闭wire/config入口适配，原停止/退款/RootLease/Job边界不改。
- activities/api.py、service.py、repository.py、teaching_repository.py、interview_repository.py。
- learning/contracts.py、service.py、evidence.py、adapter.py、prompt.py、api.py、teaching_contracts.py、teaching_service.py、teaching_evidence.py、teaching_adapter.py、teaching_prompt.py、teaching_views.py、teaching_api.py。既有teaching_policy/progress算法只读，不借集成改变保守判断或评分标准。
- interview/contracts.py、service.py、evidence.py、prompt.py、policy.py、views.py、api.py，仅新增profile及必要两链接线，原probe/来源可信度约束不削弱。
- memory/context.py、repository.py、service.py、contracts.py、api.py，仅v2/typed binding及当前资格的必要传播，不重构记忆实体。
- retrieval/evidence.py仅封闭融合排序/目录共用接线，原片段identity不改。
- data_exit/contracts.py、schema.py、schema_checks.py、codec.py、packages.py、snapshot.py、readability.py、restore.py、reference.py、deletions.py、repository.py、control.py、config.py、api.py、maintenance.py仅R02 registry/profile/权限/新三表及grant传播。operations.py与原pin/deadline/取消机制只读，既有DataContext/RootLease/停止主体不重写。
- 上述包必要__init__.py仅新接口导出。

backend新增允许 capabilities/embedding.py；retrieval/contracts.py、repository.py、service.py、api.py；data_exit/schema_profiles.py；backend/migrations/014_step018_retrieval.sql。001—013严格原字节不改；旧函数精确变更由014前向完成并登记新指纹。

frontend现有允许 src/main.tsx；src/activities/ActivityWorkspace.tsx、TeachingWorkspace.tsx、InterviewWorkspace.tsx、MemoryWorkspace.tsx、LearningResult.tsx、TeachingExercise.tsx、TeachingFeedback.tsx、TeachingCitations.tsx、InterviewCitations.tsx、teachingApi.ts、interviewApi.ts、memoryApi.ts、pendingIntents.ts、teachingIntents.ts、teachingIntentMatch.ts、teachingDrafts.ts、interviewIntents.ts、interviewDrafts.ts、memoryIntents.ts、learningIntentMatch.ts；src/data/dataApi.ts、ReadonlyRecords.tsx、DataWorkspace.tsx仅R02元数据/正常只读显示适配，不改已验InputBinding/view/lifetime保护；src/data/context.tsx原canonical身份规则只读。样式限src/style.css及src/activities/activity-workspace.css、interview-workspace.css、memory-workspace.css的新增流程样式。新增src/activities/RetrievalPanel.tsx、retrieval-api.ts。

部署/公开文档允许 deploy/start_local.py、start-backend.ps1、compose.local.yml；README.md、deploy/preview/README.md；config/activity.example.json、preview.example.json、data-exit.example.json；新增config/integration.example.json。仅正常profile/显式初始化迁移/本机就绪/停止/例子和准确流程文案；不新增常驻服务或依赖。frontend/dist内只允许本卡正式build生成，记录被替换旧hash，不手改bundle。

新增测试允许 backend/tests/test_step018_embedding_contracts.py、test_step018_retrieval_pg.py、test_step018_profiles_pg.py、test_step018_flows.py、backend/tests/fixtures/step018/的本卡有限fixture及frontend/tests/step018-flow.mjs。旧有效方法可引用复用，不改旧TASK夹具/报告/runner以追认行为。本卡新增测试及fixture可范围内修复；若旧测试必须参数适配，先报告准确单文件/方法和原因交主控合并，不弱化业务断言。

执行记录只写D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/execution/及D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-117-result.md。本目录不得成为产品运行/构建依赖。所有其他正式DocuS、AGENTS、公共库、用户需求、编号/总状态/变更账/经验记忆由主控维护。

禁止依赖锁、安装/升级/pull/新image build、Git写/commit/push/reset/stash、系统服务/网络改造/关闭用户进程、用户库/真实资料、旧frozen/failed/sealed对象或旧private/control写入、旧runner执行、自由HTML/JS/URL/导航/新页面权限、跨恢复开写。固定G11四runtime、renderer ingress和SUP停止退款主体只读。新增主要模型/服务/权限不在本批准包内的先停相关部分，完成不受阻部分。

## 精确资源profile及隔离

全部新对象，名称/volume/port/CID/image/labels/归属必须先登记再创建。同一在途对象身份一致才可接续；不能删重建换计数。缓存PG17/pgvector image固定sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f，pull_policy=never。每PG为CPU1/512MiB/pids128/restart=no、127.0.0.1，无host bind。先实核缓存扩展版本纳入R02，不用模块版本猜。

- source名retrolume-step018-syn-source，卷retrolume-step018-syn-source-data，15481，DB step018_syn，正常R02；两链、预算、重开、快照。
- compat名retrolume-step018-syn-compat，卷retrolume-step018-syn-compat-data，15482，DB step018_compat；001—013非空旧model/tool/domain/unknown，先R01包再014升级。迁移失败回滚反例应在精确事务/此库中保旧行，不另造无限新库。
- R01 target名retrolume-step018-syn-r01，卷retrolume-step018-syn-r01-data，15483，DB step018_r01，factory slot r01；原链1..13，验证后永久只读。
- R02 target名retrolume-step018-syn-r02，卷retrolume-step018-syn-r02-data，15484，DB step018_r02，slot r02；新链1..14，成功后永久只读。
- 独立失败target名retrolume-step018-syn-r02-fault，卷retrolume-step018-syn-r02-fault-data，15485，DB step018_r02_fault，slot r02_fault；只供P03坏维度/hash或必要部分装载失败验证。优先在包预检拒绝，只有必须核failed target才实际创建。该第五对象是主控为“失败对象必须保留且不能复用为成功目标”补齐的预算，不改变产品模型或复用旧失败对象；不必为了花满额度创建。
- API固定127.0.0.1:18118，Windows hidden uvicorn/Selector loop，同在最多1；记录PID/birth/launch handle，正式dist同源，Vite服务0。
- 预览仅沿已核v2-08 image sha256:ec3c70c7a8a8894c647a69b08b0c296727bb052f639e487567e9cd4624766789，load为8a047050ffe584dffa6e85222c16c8f400c0ab4db82f72a32812c2befd082b3f，renderer入口hash为6cc300164a6cb364d9bd0bae4897f06d3f6a65cf5d4272477d2bccde67312597。只复用已验签票/正常operator部署流程，不自己伪签，不借原111对象或UNKNOWN名额。新registry/nonce/CID精确登记。

同在PG最多2、preview1、API1、主browser1，禁止多个批并行争账/写产品。每个新PG/Browser/preview启动前采Docker已唤醒后的可用物理内存至少2GiB；不达门只继续不受影响离线部分并说明真实阻塞，不关闭用户应用/服务。所有15481—15485/18118实际待绑端口核全部状态与独占loopback bind；未知owner/listener、10013排除或仅bind失败均明确冲突，不擅自换端口/kill他人。

normal runtime只能用新非super应用登录，授精确data_app/领域app/retrieval_app；迁移管理角色只在本卡新cluster初始化/升级短窗，业务API/worker不持其权限。snapshot只读，各target独立loader/只读/snapshot，seal真实撤写。固定schema/role名称按014与既有013正确执行，不用管理员掩盖ACL缺陷。

新合成数据root/backup/incoming/restore/private/preview registry可位于D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/execution/synthetic/不同canonical子根，只作本卡测试配置。产品正常配置必须项目自包含并使用正式operator选择位置，不能内置DocuN路径。凭据正常随机生成/安全本地loader，仅子进程环境/stdin注入，不入argv/log/报告/浏览器；不要从旧报告找明文口令。

默认保留所有卷/库/镜像/失败原件和合成行，不以tearDown清空历史。X10明确测试的合成源/版本/记忆删除只经真实受控产品接口和影响确认、精确合成ID，保存before/after及闭包事实，不写批量DELETE/通配清理。旧用户对象零接触。R01/R02成功目标不能回退loading或转normal，failed对象不复用。

## 时间、批次与次数上限

本卡新预算在接收前使用0，旧全项目账保留。当前S01活动总窗最多28800秒，包含准备、普通等待、实施、检查和最后1800秒收尾；接收后72小时日历。到25200秒不再扩大范围，到27000秒只保存和精确清场。首点缺失如实说明并保守扣；未登记时段UNKNOWN或保守算，不填0。不要把活动秒数、运行持有秒数和墙钟混算。

完整运行根最多8，当前S最多使用7并保留1给未来Q或获准定向复检；不是8条shell命令。一个根从为当前完整目标第一次实际产品运行到所有其自有资源结束，同根连续普通修夹具/必要复测允许，但每次调用/失败/修正必须逐项记，不能把无关新目标/新资源/无限尝试归同根。建议目标按协议/纯逻辑、014与检索、学习链、面试链、异常权限、重开/两恢复、最小有据复检合并；实际以执行前phase登记为准。纯读文件/hash不算运行根。

真实运行和背景持有累计最多14400秒；离线产品检查/测试/构建累计最多7200秒，与总活动窗分类重叠不双加。同一PG/API/browser/preview从start到精确stop包括根间空等全记持有，以实际同时段归并记录并列各资源生灭；时间上限不能用其他余量替代。

PG物理成功对象最多5、创建尝试最多8、volume最多5、PG start尝试最多20。只允许上述五个精确角色对象，预算富余不允许第六个名字/额外库。API启动最多8、主browser生命周期最多8、正式frontend build最多3、Windows Native/SUP窗口最多160含失败、dynamic preview create/start各最多12且每活动仍3次/180秒、HTTP最多3000。启动前先记attempt，spawn/create失败也计相应次数；后台消费者的启动与结束、PID/birth/CID和首末事件不可漏记。

普通修复不限为“每卡只能修一次”，但选定检查原则一次；具体失败有根因修正依据才能复检。某问题两次有据修正仍失败、根因不稳、范围/主要前提变化或任一上限到达就停止该路线交主控，不靠换命令/脚本/窗口重置。输入不同的规定正常/负例不是失败重试，同一夹具错误也不能在不同目标下隐去累计。

新增供应商API调用当前0。AP2总封顶80次/20000000人民币microunits，1元等于1000000，两个供应商合计，所有失败/timeout/UNKNOWN计入，不按供应商分别80。预留每call 250000，真实最坏价额须经官方依据/计量保守上界/必要币种税边界及至少25%裕量核算不超预留；缺依据关闭发送，不把UTF8bytes冒精确tokens，不自动提预留或总门。

未来Q仅固定三活动：01800000-0000-4000-8000-000000000001为学习40次/10元，01800000-0000-4000-8000-000000000002为面试24次/6元，01800000-0000-4000-8000-000000000003为剩余语义16次/4元。各deadline24小时、max_running_seconds3600、request65536bytes/common output4096tokens、finite_calculate最多8、预览3次180秒。每实际model/embedding共扣活动与grant，换活动/新grant/换provider不能重置本许可。收费grant未来明确启用才起72小时，不从现在批准或S接收起算；不借旧13元。timeout10秒/窗口90秒/管理120秒沿原边界。

Q尚无启用回执，所有真实API/model/Embedding/付费/真实账号资料0；只读官方10页不算模型调用。无其它外网、安装/pull、Git写或个人资料。S合成测试活动使用独立UUID和清楚test transport隔离，不能占三条未来收费活动或伪造真实grant放行。

## 验证目的、样本、证据与复用

当前验证为实现阶段，证明新类型和持久模型/权限传播、两链实际接线、最终bundle及正常重开，避免把旧局部成功拼成整链。不是再前置测试已关闭模块。

冻结116 sample-inputs.json的8个纯合成源、两页PDF定义、答案变体及28场景：L01—L10、I01—I03、X01—X12、P01—P03。首次实际生成时保存精确bytes/hash及产品分配ID映射；PDF生成不添依赖，不拿真实履历或旧用户资料代替。S按真实协议/PG/Windows/HTTP/最终bundle层分别完成；Q预期保持NOT_RUN，不能因stub恰给标准答案签语义。

必要正常链及关键反例预期以验收合同逐行执行，尤其是同键/semantic slot唯一effect、取消/晚到/current资格、四账/unknown/显式确认与COMMIT丢响应、记忆失效、源替换/删除、正常重开后新反馈和新理由、R01/R02永久readonly/坏包failed。不需要把28场景机械拆28运行根或穷举全部维度；一个学习域和一个面试域代表传播，再对新kind/R02/角色做针对例。

source index received+007+vector原子、query结果身份、固定RRF和原件复核、grant跨活动竞争/过期/不可重绑、Embedding父消费拒绝、旧tool NULL/零费用非空升级、旧R01包和新R02精确profile/角色/seal，均须相称真实PG证据。旧不变Supervision/32宿主反例不重放全套；本次只补真实题/反馈父关联与v2-08 ACK/bitmap或可信读值/StopProof。

先把测试环境按实际Windows口径搭好，不用重复真实根排查已知环境问题。仓储/fixture统一读取既有app.runtime.psycopg_compatible_loop_factory，asyncio.Runner和async测试基类明确Selector兼容；可参考backend/tests/test_activity_ledger.py及test_activity_tools.py的现有模式，不运行其旧整套runner。HTTP同源session bootstrap使用真实local_session流程，不能改产品认证绕过测试。

Docker inspect使用完整JSON再解析精确所需字段，缺可选字段按实际schema区分，不拼曾失败的HostConfig.Mounts模板；不输出Env。新数据库owner/role及DSN仅来自本卡receipt/安全loader，不猜历史retrolume角色名。浏览器脚本先离线语法/路径/静态启动参数核对，正式bundle绑定后集中运行。当前修复后与批时源码差异、加载捕获和build输出hash分别留证，不能以typecheck替代未跑实机。

每场景索引保存正确预期、实际层、输入hash、命令/上下文/操作/源/记忆/head及DataContext before/after、四账/预留、007和领域或vector提交事实、失败/修正/as-run身份、UTC/mono/自有资源/停止证据。五层分别标记schema、位置、语义支持、确定计算、长期效果；位置/schema通过不证明语义正确，一次正确不写长期掌握。

旧充分证据按116验收合同和原任务原件直接引用，含G3正文原子、G5工具隔离、G8/9教学记忆、G10面试、G11安全宿主及STEP017精确pin/恢复。改变新分支才补方法，不全仓跑/不重hash全库/不重采未变原件。009/013旧失败记录和PG两秒仅证reading超时的限制保持；纯route浏览器不冒真实后端，受控连接不冒物理PG阻塞。

## 连续执行、集中独审及准确收尾

按实际依赖自行分解，在同卡连续完成接口/DB/配置/UI/文档、检查及有据普通修复；不要每做完一小步要用户转卡。优先收敛真实可执行的环境/fixture，允许有限普通修码，不能只修改正确测试期望求绿。已成功且实际对象未变的检查不再重复；稳定候选前不逐文件独审。

本成果新增kind/入站接口/角色/数据清理/费用gate/R02是高风险完整成果，稳定后必须新隔离A+窗口集中独审，未参与本卡实现，只读业务与原始目标/验收/最终diff/源码/原始证据，不传实现完整聊天或自评。独审编号和预算由主控之后安排，本工程窗口不得自签。原独审充分旧边界直接继承；发现问题合并一条修复路线，复核问题和实际影响。

S完成时保存稳定合成候选并精确停机交回，不等待审计时继续计费或保后台。主控核证/集中独审完成后原窗口只补Q与实际变更，不重做整套。全部Must适用层齐备、无开放P0/P1后才请求STEP018；STEP019/020和M1/发布由主控另裁定。用户AP2批准已记录，不能再问是否愿付20元；确实缺安全配置/账号条件时只报具体缺口与正常配置位置，不索聊天secret。

每次停止先拒本launch新mutations，处理归属明确的窗口/预览；按原StopProof/Job/EOF/CID/nonce核树及停机，API用PID/birth+原有界信号。只停止本卡启动的精确PG，用户原先运行或其他任务不动；Docker daemon不在停机范围。确认不足写unknown并保预留，不用异步命令返回或Pid0单项冒完整清场；卷/库/镜像/failed对象不自动销毁。端口检查可见无监听和实际归属消费者结束分别存证。

出现真实关键缺口先完成不依赖部分，保存准确差异；平台审批/内存/端口问题不能改系统绕门。缺官方能力只停相关真实能力；缺审计只停相应放行/付费，不阻S候选。两次有据修正仍失败、资源/时间/投入门、重大数据模型或服务改变、许可越界都按停止合同交回，不机械新开第五/第九批。

## 结果、保存复读与必要人工

完整结果保存D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-117-result.md，所有新增执行证据在D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/execution/。只有一个主资源/预算账和一个case-index，不并行立全局进度。历史失败、补丁pre/diff/post、首点/UNKNOWN段、旧卡投入原文保留；不自行写DocuS或占编号。

报告先写一句实际结论、S完成范围/候选状态、Q尚未启用及真实费用0、文件及字段/签名/返回/迁移/权限差异、关键原始证据导航。再给28场景的实际层/继承/新证/失败与not_run、最终加载/源码/bundle/profile、官方核查适用性、预算和资源累计/剩额/精确清场、偏差和真正未决。不能把“代码已写”称全部验证或审计通过。

S完整候选达到本段终点即回传，不为使报告全部绿而偷开Q；若部分停止，明确哪一Must和哪个精确方法/资源未完成、根因证据及合理接续，不把原因全写“额度不够”。必要人工只有人工转卡/带回结果；实际执行资源未知导致必须用户处理时一次给最少步骤、位置、成功标志和非敏感回传，不在聊天询问key。

建议主控同步正式架构/状态/新FILE与API、必要经验，只报已解决且真验证的根因候选；不自行改用户需求/公共提示词/记忆或新增OPT。确认UTF8结果完整可读并留hash/复读证明后，只回复一句结论和可点击的结果绝对路径，供用户带回编排。未能保存才如实标未保存，不提供虚构路径。


# TASK117/R111 — 预览operator部署交接补充

接收A+，继续当前TASK116/114延续的TASK117工程窗口。本补充是原S01许可内的准确部署交接，不是新任务、重新审计、扩预算或要求用户找密钥。读完本补充并在当前执行账记录新合同hash后继续原卡；其它实现/验证不中断。

## 已查明的缺口与采用依据

主控确认TASK112独立终审已完成、G11有限切片已正式关闭，但当时没有创建正常operator部署配置/审核票据。TASK117把“复用已验签票”写为现成输入不准确。本补充取消寻找不存在现成票据的要求，明确允许正常部署动作；不改原独审结论、不自行审计产品。

独立终审结果是D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-112-result.md，冻结SHA256为1dab1126aa72e335288d037baed5bc13b7cfdc1e4a386b6c04553e630f871571。主控已采用的有限关闭依据为D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-111-G11-final-acceptance.md及TASK-112-work-decision.md。按上述报告的Windows单机、合成资料、固定程序/描述/输入和原故障模型适用；不是整个项目、任意脚本、真实个人资料或新kind独审通过。

允许的固定宿主身份如下，必须实核一致。

- image_id为sha256:ec3c70c7a8a8894c647a69b08b0c296727bb052f639e487567e9cd4624766789。
- load_manifest_sha256为8a047050ffe584dffa6e85222c16c8f400c0ab4db82f72a32812c2befd082b3f。
- renderer_sha256为6cc300164a6cb364d9bd0bae4897f06d3f6a65cf5d4272477d2bccde67312597。
- kernel_release仍为6.6.114.1-microsoft-standard-WSL2。当前真实环境不同则不伪填，不改HostPolicy白名单；只停预览依赖并交准确差异。

当前Python预览停止/资格传播按随后已关闭的114/115源身份继承。主控核得host_policy.py为7c54c0d4574ecfd9edd2b2a70821a731d3f219df3c7abf5bd14e17d8acb90b83，pipe.py为db2a742a559d7905012273e9fd9acaec441a549e12d71fa8ac77a3f486d3f974，production_supervisor.py为d6870137371caf003412fc4089bfc1e0dcf6ecf859ee05633fd5024d894c6d58，三者逐项匹配TASK115最终接收的current清单；其中SUP不是112早期报告的715649值，不能抹去后续已验收的传播或冒称所有源从112以来不变。本轮仍禁止改这些主体。

原112正文中未签生产票据和未开启生产部署的限制仍是当时事实。本次仅正常配置本轮已获准的合成集成验证实例，不据此开启用户库/个人资料/真实服务或公共部署。

## 原窗口可连续完成的正常operator动作

你可作为本轮合成实例的受托operator，基于上述既有独审事实生成认证文件。HMAC签名是部署认证，不是补造一次新独立审计。本次授权来源为用户已采用G11/已批准117 AP1及合成验证范围，主控在本补充中明确给出；无须向用户索密钥、另找旧私配或重新请付费批准。

1. 只读核终审报告/主控关闭记录及上述固定源身份，按原117实时门核实际缓存image、Docker CLI绝对路径和内核。禁止pull/build或改固定runtime/host_policy.py、验签器、known授权字面值。原111历史runner/私密控制根不读取或复活。
2. 使用本轮新目录D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/execution/synthetic/operator/。正常部署配置固定为preview.deployment.json，票据为preview.review.json；它们是本卡合成配置，不进入公开config示例或用户配置。目录若有内容先核本卡归属，不能覆盖未知对象。
3. 配置严格使用retrolume.preview.deployment.v2现有封闭字段，image/load/renderer/kernel按实核相等值，docker为实际绝对路径，review_ticket为本轮preview.review.json绝对路径，review_key_env指定RETROLUME_TASK117_PREVIEW_REVIEW_KEY。registry仍由实际本卡settings.data_dir/preview-control派生，不能借新配置绕owner/nonce/旧UNKNOWN。
4. 本轮私有控制器内存以安全随机源生成至少32个UTF8字节的认证key，不显示、不输出、不写shell历史/脚本常量/argv/报告/原始证据/公开配置、不写setx或用户全局环境。只在本卡API/必要受控测试子进程env注入RETROLUME_TASK117_PREVIEW_REVIEW_KEY和RETROLUME_PREVIEW_CONFIG。如果控制器重开丢失内存key，可依据同一冻结审核事实正常生成新key及相应认证文件，留旧票据hash和更新原因，不清任何业务账/预览计数，也不复用旧控制密钥。
5. 票据严格为retrolume.preview.review.v2现有七字段。decision为approved，仅认证已正式关闭的固定G11；result_sha256必须为上述真实TASK112报告hash，三个加载身份逐项相等。signature按现产品canonical的UTF8字节和HMAC-SHA256正常计算，不手填任意签名，不给票据加loader不支持的字段。secret只在受信内存/子进程环境，票据与配置虽不含key也按本卡operator输入保护，不发浏览器/导出。
6. 使用原产品load_host_policy正常读取验证，并在实际API子进程确认有且仅有配置存在/环境变量存在布尔值、HostPolicy正常加载结果与固定身份；不打印变量值或整个子进程环境。不从主控工具进程的环境存在性推断API进程已经注入。api启动/测试/preview的真实运行按原单账计数，不能因本补充加额度。
7. 同时沿原117确认HTML活动profile和输出token限额真实就绪；公开示例仍保持不可误激活，不将用户部署密钥或本轮测试值写回示例。走原真实生成/准入/宿主/输入/停止链完成L10及相关集成，不能直接构造无审计的另一HostPolicy绕正常loader。仍只用本轮合成资料和最低传输替身，无真实provider/费用。

本补充不在本窗口生成密钥/票据、运行产品或修改执行层源码。真正部署由当前工程窗口在原卡内完成。若正常loader拒绝，先依据具体身份/签名/路径/进程注入事实修正正常配置，不能patch验证函数或把authorization改成旧TASK111合成入口；两次有据修正仍失败按原停止条件交回。

## 预算、历史与回传

仍为TASK117/R111/S01，原首点2026-10-14T05:21:48.590792Z及全部UTC/mono/等待/已用root/1186.219秒离线等按真实单账连续，不重置或延长。主控读取的是在途账观测，不签当前预算最终验收，不动execution/receipt/budget/events或产品文件。正常部署文件写入不是新增产品运行根；实际loader导入/测试/API/容器/预览仍按原定义实际计入。

本卡其它实现/验证继续。完成后与原TASK117统一结果一并回传，记录配置/票据路径及hash、固定审核报告/身份绑定、API进程注入布尔检查、正常loader结果与运行证据，绝不回传key。旧接口/角色/数据模型/签票schema不变，Q真实调用门与独立新边界审计未开，不签STEP018/项目通过。
