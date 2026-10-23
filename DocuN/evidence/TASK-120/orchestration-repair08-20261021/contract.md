# TASK-120 / R-114 续作08 F02与F03剩余边界合并修复（当前有效）

## 目标、身份和接收

本卡交付一个完整成果。修复TASK-121 review-01仍开放的F02 ADMIN组合能力漏验、F03记忆清理失败后GET/重开误报完成，并完成各自最小正常/异常实证及精确清场，交原TASK-121窗口只做对应增量复核。F01、F04、F05独审关闭及已接受子事实直接继承，不重做完整权限矩阵、正常业务链、金融100门或前轮清理全链。

接收为刚完成TASK-120续作07的原A独占工程窗口，使用胜任本权限/删除安全修复的最强可用增强能力，如实登记真实模型；旧A+和其他工程窗停止，不委派、不并行。沿TASK-120/R-114/STEP018，不占新TASK/R，发现编号仍为TASK-121-F02/F03。

根目录 D:/shspic/project_NO3_RetroLume-agent；入口 D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。task_model、V4.0、公共AGENTS CHG-0003，公共只读根 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4。需求v1.4、架构v1.58、执行动态v2.86，七规则指纹仍取DocuN/evidence/v4-migration-20260930/rules-snapshot.json。本卡覆盖旧工程冻结通知，但仅前向允许下面两项修复，不授权真实Q。

## 依据与最小读取

用户对AP-120-07已明确批准，新增合成库、未提交权限反例和新造准确正文清理的对象与范围继续有效，本卡不扩资源、权限、删除对象类型或费用。本次是同一尚未验收成果内的定向普通修复与取证，按既有开发与转卡授权直接签发，不需再请用户逐项批准。

先补读本卡与根入口、适用锁定规则，原窗未变已读材料复用。然后读取下列根相对路径，均展开为本项目绝对路径。

1. DocuN/results/TASK-121-result.md的review-01第3、4、8节和关闭/继承结论；DocuN/evidence/TASK-121/audit/review-01/findings.json、evidence-comparison.json、identity-closing.json、result-save-proof.json。
2. DocuN/evidence/TASK-120/orchestration-adopted07-20261021/contract.md、permit.json、adoption-receipt.json，只复用已有有效边界；本轮精确permit与input-check在DocuN/evidence/TASK-120/orchestration-repair08-20261021/。
3. backend/app/data_exit/q_roles.py及其schema_checks调用、backend/app/memory/service.py、repository.py、api.py、frontend/src/activities/MemoryWorkspace.tsx中清理状态/重试/刷新部分，以及q_cleanup.py、ControlHub正常只读状态与清理方法的直接依赖。
4. 原audit-repair-07中F02角色用例、正常memory清理、原始前后金融与007记录、精确文件清单和相关fixture；原唯一execution/budget.json/events.jsonl。只读旧正文/凭据需要限于正常受信运行路径，禁止将其输出到报告或证据。

review-01报告55795字节，SHA256 75d40d166010d29b28065327a8a911a859200d6da01cac080ab13b72748da595。F01/F04/F05已关闭；两项开放P1是新的组合边界，不声称实际库已经被越权或泄露。主控接收的是静态可达缺陷与证据限定，不是动态事故。

## A 完整ADMIN能力组合检查

审计触发为真实快照登录S已正常通向snapshot组，空NOLOGIN中间角色B以INHERIT FALSE/SET TRUE通向app，而S对B有ADMIN TRUE、INHERIT FALSE、SET FALSE。B当前自身无权限，但S可按PG17 ADMIN语义把B再授予其已经能SET的snapshot，使其能进入B再SET到app。原accessible只计算当前SET/INHERIT、ADMIN只看目标当前权限，漏掉这次能力扩大。

在现有有界role检查中纳入ADMIN可授予/改变成员选项后的SET/INHERIT和继续ADMIN组合能力，以实际用途判定潜在越权，考虑多级链、循环和容量上界。不能只把B当前表权限加入一次并集、只禁止直接ADMIN→app，或将所有ADMIN/membership无差别拒绝。无需新建权限平台或给产品扩权，算法细节由执行者自主决定，并对照本地PG17及已读官方GRANT语义。

先补离线针对该组合、合法无害图和有环图的真实检查函数用例；不要用预设拒绝结果替代算法。随后只在已批准audit07_main内用单连接显式未提交事务构造此组合，主体/桥角色沿用原已批准集合，观察实际能力，在事务内证明原主体可按ADMIN路径产生危险SET能力，再核产品严格schema检查在扩大前准确拒绝data_role_capability_mismatch。一个正常图对照通过。finally ROLLBACK，独立新连接核完整原成员图与权限不变，不提交危险关系、不执行服务器程序、不变密码或角色管理属性。

角色是集群级对象，负例期间API/worker和其他相关连接停止。不能在正常浏览器链运行中临时改角色。旧8例/管理拒绝例不整批重跑；只补算法直接影响的必要对照，成功即存独立checkpoint。

## B 记忆DB事实与Q清理状态统一只读投影

当前POST在DB purge已经COMMIT而Q文件删除失败时临时返回pending/unconfirmed，但GET收据和列表/详情从learning_memories读到DB done，重开后因此显示全部清理且隐藏原显式重试。必须同时修GET命令收据、单记忆详情、列表及重开实际使用投影，覆盖原命令键和当前记忆的准确依赖集合。

保留已COMMIT的数据库purge原事实，禁止回写done为pending来伪造DB回滚。组合投影在Q依赖pending/unknown时必须显示未确认，不能声称全部完成；DB已清理与Q副本尚待清理的含义保持可区分。正常无Q或本对象确无Q依赖仍可按真实DB事实显示，不能令所有记忆永久pending。控制根/当前日志读不明、依赖索引不能确认时失败关闭，不将异常吞掉后落回done，不显示正文。

复用既有字段和原显式清理重试，不新增公开请求类型、表/列或新的后台清理队列。只读投影不得初始化正常写QAuthority、记新批准/claim/发送或借GET执行文件清理，不损坏sealed reader的只读资格。只读恢复和无Q旧路径按真实状态兼容；物理完成必须依据真实清理结果。必须核并发清理/GET的锁序或快照边界，不让读线程持相反锁造成死锁。

同键GET和重开视图保持“清理待核对”及既有明确重试入口；用户显式retry成功后准确变done。retry必须复用原清单/记忆/依赖身份，不重复源墓碑、模型调用或已提交DB purge业务效果，不恢复旧Q批准/UNKNOWN，不误删其他对象。原source_delete cleanup attempt/完成见证已经由独审接受，除必要共享纯投影不修改其授权协议；不重开旧Operation票据路线。

## C 两个风险的最小合并实证

在原已批准audit07_main新建准确合成memory和它的Q prepared副本，复用仍合格的原固定文字/来源与既有正常业务接口；不恢复上一轮已撤销记忆、已删来源或旧批准，不改活动/root/grant绑定。为样本准备若确需原query/index，仍走原正常批准/限额路径，仅使用原两库合计16笔的真实剩余，不重做模型主链或引入新文字。

文件只在既有.runtime/task120-audit07内生成，修改前登记本轮准确file identity/hash/依赖键/用途与旧清单差集，最多再使用原16份额度中的未用部分，不能把旧已删6份重新计为0。源冻结八文本只复制，不删除原件。注入一个准确Q文件删除边界的PermissionError或等价真实共享失败，正常HTTP revoke/purge已提交DB正文清理。不要patch收据或GET返回值制造现象。

完整一次流程为正常POST失败关闭，随后同键GET收据、列表与详情、API停后同库/同控制根重开读取，均显示组合未确认且文件仍在；最后用户式显式retry准确清理，GET/列表/详情和重开视图变为确认完成。全过程正文读和旧引用拒绝；真实文件缺席、无关对象hash、原007/业务键/费用/UNKNOWN与原预留分别核对，GET不增加动作。保存每步独立checkpoint，旧成功memory清理不重跑。

优先仅改后端投影，让原正式bundle既有pending与重试分支工作；前端未变则不build。使用一个既有headless单context/单页浏览器会话，复用正式dist，在同一流程观察真实重开页面仍见待清理/明确重试及成功后done，不能只拿HTTP字段代替已列浏览器承诺。若前端字段接线确需直接小改，只改MemoryWorkspace该状态和提示，记录依据，集中typecheck/build一次并绑定实载hash。既有两项DataContext迟到/五入口UI不重跑。

先完成代码、离线与runner入口/fixture预检，再开启PG。F02在API启动前完成并回滚核图，之后串行API/浏览器记忆流程。可在同一真实根内分段保存；若清理故障checkpoint已保存，修复夹具后只续剩余步骤，不重新造旧清理事故。明确错误根因才卡内修正复检；同一问题两次有依据修正仍失败按原停止门，不能机械碰运气。

## 修改及保护范围

允许backend/app/data_exit/q_roles.py、memory/service.py、repository.py、api.py和q_cleanup.py中两项问题的必要增量；必要正常装配及纯投影小依赖首次改前登记准确路径与因果。frontend/src/activities/MemoryWorkspace.tsx、对应样式/类型仅必要状态接线；对应backend/tests、fixtures/task120和本次定向浏览器脚本可改。产品文件先存pre/hash，检查冻结冲突，不覆盖他人改动。

禁止015及001—014再改、profile/codec身份/金融SQL/原子007/worker协议/联合时钟/PG领取门重写；已关闭项直接继承。原清理文件身份保护与schema检查不得削弱。禁止公共库/DocuS/任务卡/独审结果及原证据写入、依赖安装/锁变化、用户库/旧实例业务写入、新DB/容器/卷/LOGIN、密码调整、pull/prune/drop/批删、真实供应商/付费/preview/Git。独审旧证据发现摘要错误只补限定，不改原件。

新证据目录 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/execution/audit-repair-08/。唯一原budget/events只前向追加本轮许可和实际尝试。统一结果仍是DocuN/results/TASK-120-result.md，置顶08、原109435字节/hash3772e95062f1f423b299ee6542364a5ce0ca8c4eae92717b35b41efca79a86a4原字节后缀保留。旧成功/失败原始材料不改。

## 精确资源、剩余额度与时窗

本轮permit为TASK-120-Q-PREP-TARGETED-REPAIR-08-20261021。只恢复原源容器 b89522070d4b64fc67efed810852ccc21948058f154bf4fa1889f4d8d69a102f、卷retrolume-task120-qprep-data、镜像sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f，1CPU/512MiB/pids128/restart=no、loopback55480/API18120、无host bind。启动前重核精确CID/label/mount/limits，不输出Env。目标4eb5be54b713e5412be702e27684d98d2b7de92a77f9085b3ce84a5f4b124332/卷retrolume-task120-scopeui-ro1-data/55481保持停止。

只写已经批准并创建的retrolume_task120_audit07_main，原r02只在确有必要时只读核已存事实；不新增逻辑库，不写原四库或06源/恢复副本。桥接组仍仅原两个NOLOGIN名、事务内创建和回滚，现有合成登录凭据通过原安全机制注入。新真实配置或主机权限调整不在卡内。

原账root60/64、PGstart61/64、API63/96、Browser14/16、build5/8、Native69/128、HTTP1520/10000，容器/卷及创建尝试2/2保持。最多剩4根、3次源PG启动、2次浏览器、3次build；其他只按原差额，不新分每场景启动额度。新收费admission本轮仍受07两库合计16、已用5的总额限制，已有单实例100/25000000与原三活动分额不变。旧141失败/117的81、所有unknown保留。

保守wall64525.559426/72000，剩7474.440574秒，holding2885.485295/21600。不得将时间包装器预留重复扣减或记0，原post-save60与未知预留结转；本轮实际文件工具、离线、运行都进唯一账，不在runner外开业务。元数据单批60秒、离线/build单批300秒，每根1800秒且末120秒清场。

本卡不重新开启07的12小时窗。沿其更早签发保守终点，2026-10-21 20:29:21.021710+08为最后新增业务门，20:59:21.021710+08为清场/保存终点，且原96h终点2026-10-22T08:41:08.5687758Z不变。若实际收到时业务门已到，禁止新业务，能在原剩余工具/收尾窗完成的离线与保存继续；不能伪造接收时点或因换卡再续旧批准。当前许可用于剩余窗口内的两项定向修复，不延长旧grant。

首次允许一条有限非业务bootstrap读卡/原账、采时并前向登记，未知人工接收写unknown，不声称首工具之前已登记。原A接收后才追加08许可，主控不代改工程账。

低内存沿512MiB启动/每约1秒采样/连续两次低于256MiB精确清场。PG/角色负例/API/浏览器串行，离线等待不占运行服务；不要求用户反复腾内存，不关sandbox，不绕审批。

## 停止证明、审计关系与回传

本轮停止助手必须把unknown/access-denied观察保留unknown，不能由same_identity_running=false推出已退出。按准确PID/birth、具名Job归属/树零/同名Job缺席等有效组合证据核本轮自有对象；原079中20条unknown的19条旧明确退出和1条原Job替代证明由独审已接受，原件保留，不能改写成705项全为新鲜退出。没有独立依据的未知项如实交回。

最终核本轮注册进程树、源CID Running=false/Pid0及55480/18120无监听，恢复目标未启动保持原身份/停止。保存有限差异/精确pre-post/as-run、两P1证据与正常对照、金融逐实例、累计账及原停止限定；只打包本轮必要材料，不递归旧ZIP、不带凭据/可用批准/待删正文。工程完成即停止。

F01/F04/F05与F03源清理及_CleanupAttempt受审通过部分保持；只对本轮改变及直接影响回原TASK121窗口增量复核，不新建全面审计。历史执行控制不通过保持，Q、STEP018整体/019/020/M-1/项目不宣告通过。

两项成果整卡完成或达到明确停止门才统一回传，不逐场景转卡。遇范围/权限扩大、新主要模型、身份漂移或审批真实阻断，保存具体事实并停依赖部分，其他不受阻工作继续。不作“下一次保证成功”承诺，不拿新卡清零失败。

报告两项修复及原始证据、真实文件差异/摘要、每步被测字节、准确异常和成功对照、未完成/未验证、旧证据继承、资源停止/unknown、预算和偏差。保存复读后只回一句话结论及统一结果绝对路径；主控与独审最终验收由相应窗口负责。人工仅转交本卡并返回结果，卡内范围不再逐项请求批准。
