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
