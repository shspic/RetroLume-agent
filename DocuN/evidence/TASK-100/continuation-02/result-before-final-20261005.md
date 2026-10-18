# TASK-100 续作02结果：代码修正交付，整链验证尚未完成

结论：最终产品已完成本轮合同修正，52项离线检查、27项不同的真实PG检查及六类009迁移场景通过；第三个真实入口因HTTP夹具字段断言失败结束，修后HTTP、Windows监督主链和浏览器尚未运行，不能签完整教学闭环通过。三个真实入口均保留失败状态。2026-10-05恢复时已只读确认本卡容器、进程和端口完成收尾。

## 1. 身份、读入与交付边界

执行身份为Codex Desktop报告的GPT-6，精确变体未确认；用户转交的新业务实施聊天，非独立审计窗口。沿用TASK-100/R-094、G8-P与续作02许可，没有创建子Agent、审计卡或其他实施聊天。

实际根目录为D:/shspic/project_NO3_RetroLume-agent。已读取项目入口、锁定V4.0/公共AGENTS CHG-0003及必要WORK/07正文；七个规则指纹一致。需求v1.1、架构v0.80、执行动态v2.02只读。099唯一业务合同SHA256仍为0f38de84d6036e48a9fa544ba8304b37a72cf89e56e29fc05bef500609cc0e67。

首改前103项核对及75份必要原文件副本见[preparation.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/continuation-02/preparation.json)。本轮22个既有文件修改、16个明确新增文件及107项最终运行身份见[final-file-identity.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/continuation-02/final-file-identity.json)和[diff-from-pre.patch](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/continuation-02/diff-from-pre.patch)。30个既有、未取首改副本的外围文件仅记录最终身份，不冒称本轮新增或改动。46项受保护输入在结果置顶前核为不变，结果历史的字节保留另有证明。

没有改001—008、原launcher/SUP/worker/Job/停止主体、依赖锁、用户配置、原始需求或共享DocuS；没有安装、下载、真实provider、真实密钥、用户库迁移、Git写入或发布。本结果是候选实现和有限证据，未裁定DEF正式关闭、G8最终放行、STEP009—012全部通过或项目完成。

## 2. 实际修正及证明范围

1. DEF-003：009按实际PostgreSQL表达式核前置约束，拒同名宽松CHECK；records全部UPDATE/DELETE拒绝，运行角色仅SELECT/INSERT；commands使用有限列级UPDATE。本地goal/答案/暴露/纠错/选节点和模型feedback/progress均在INSERT前形成最终效果，不做分次回填。真实PG已验证全列保护、零半写和既有事实不变；原Windows工具同事务分支仍缺运行证据。
2. DEF-004：冻结实际目标、接受路径、题目、量规、答案、纠错、已有反馈、核算及原目录hash；修复gateway受信封套及Message类型接线。T-intent/claim/admit/mark在锁内复核当前pending、版本、父事实和资料，拒占位或漂移绑定；允许原settle后的pending/dispatch_closed状态开启合法下一窗。真实PG已证明冻结四父事实、无受信绑定不预留、答案改变后mark前拒、合法连续账本租约及相反意见争议；连续真实SUP教学窗口尚未证明。
3. DEF-004原子提交：缺command、operation或受信封套时拒绝并回滚原007正文与终态；当前正常反馈原子写feedback/exposure/progress及一次head效果，合法旧版结果有history分支。本轮真实正向record事务和错误封套回滚通过；Windows四类在途迟到及ALREADY_PRESENT新完整性分支仍缺相应动态终验。
4. DEF-005：workspace/command/history/record公开读取各用一条业务CTE快照；适配TEXT正文与psycopg原生JSONB；核正文/hash、有限view_token/游标和暴露集合，坏单项抑制，来源失效保留用户文字。真实SQL计数与HTTP游标漂移409通过。引用复用原件位置/hash；实际引用端点返回200，但第三批夹具误读响应封套，后续作答offset、无token及no-store断言未到达。
5. DEF-006：新有限runner实现真实测试发现、累积单调deadline、动作前计数、blocked/not_run非PASS、依赖阻断、完整stdout/stderr和独立finally；新增实际Windows组合与本地Playwright脚本。观察器只替provider传输并观察原执行链，不替代产品账本和停止。离线控制通过，三个批的失败、下游未运行和真实收尾均如实保存。Windows/browser代码可发现与Node语法检查通过，尚无运行通过结论。
6. DEF-007：确定未准入才判failed并清本键pending；claimed但没有operation、取消且无收据或UNKNOWN继续保留语义槽；同键重读不重新启动。七项真实恢复PG检查通过。提交响应丢失、原SUP无效输出后显式retry及硬停止已写组合场景，尚未实际执行。
7. 领域补全：纠错可绑定实际progress和对应feedback，保留旧事实及争议；旧路径的纠错仅作历史，旧proposal不能冒用当前待接受建议。有限进度按不同未暴露实例、复测、辅助与争议重算；核算复用finite_calculate而不执行用户程序。相反评价与纠错的真实事务证明已通过，完整H1推进和有限工具账尚缺。
8. 界面：完整意图正文先写原生IDB、摘要再写localStorage，写失败零POST；跨标签互斥、迟到读取保护、草稿/保存/评价分离、显式复测与续答、历史/纠错、参考暴露及有界只读轮询已接线。最终源码和dist精确绑定、构建通过；全部浏览器行为仍为未运行。README已更新有限配置、显式动作、恢复和限制。

这些是最终函数和已有证据的范围说明，不继承续作01“全部缺陷关闭”的自评。

## 3. 三个真实批次及全部失败

- 批一[2026-10-04T151643.300656-0000-main-combo](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/continuation-02/2026-10-04T151643.300656-0000-main-combo/summary.json)：精确容器、角色/两库归属、主库001—009与最小权限通过，六类迁移通过；仓储26项中16项通过、10项ERROR。根因是定向种子把dict消息交给需要Message的受信封套，AttributeError发生于共同前置。修正只在fixture将真实消息转换为Message；应用及后续段not_run。原始错误未覆盖。
- 批二[2026-10-04T152236.912137-0000-main-combo](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/continuation-02/2026-10-04T152236.912137-0000-main-combo/summary.json)：只复验受影响整合类，10项中9项通过、1项FAIL。观察器把原事务的两条SELECT set_config超时设置也算作教学事实读取，断言得到3而非1；业务读取确为一条CTE。排除仅超时配置语句，并保持恰一条WITH断言。应用及后续段not_run。
- 批三[2026-10-04T154155.612447-0000-main-combo](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/continuation-02/2026-10-04T154155.612447-0000-main-combo/summary.json)：单快照复验及新增纠错/相反评价事务2项通过；原应用健康200、实际本地会话bootstrap通过。HTTP 4项中3项通过、1项ERROR。合法未暴露单项、零费expose、暴露后参考及绑定引用端点已实际200，夹具随后以cited['text']读取引用封套导致KeyError。合同和实际路由使用cited['citation']['text']，产品读取没有为迁就断言而改动。Windows和browser依赖HTTP，均not_run；总批fail。

三批分别保存repository-raw、migration-raw或http-raw目录的完整stdout.txt/stderr.txt/result.json、as-run-files.json、segments.json及cleanup.json。逐方法定位、失败保留和有效通过复用见[verification-index.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/continuation-02/verification-index.json)。三个批均未汇总为PASS。

第三批后修正HTTP测试为CatalogEntry封套、ID/片段hash/offset断言；新增无PG的实际引用路由检查，使用真实临时原件并核位置/hash，明确读取服务和授权只为离线替身。该修正已包含于最终52项离线通过，但真实HTTP复验未运行。27项不同的PG检查由首批16项、次批9项和末批2项构成，具体方法不重复计数；不据总数签未测模型/工具/Windows行为。

最后真实批后仅backend/tests/test_teaching_api.py变化，产品与其余fixture字节不变；原有真实结论可以按上述具体行为复用。全量最终文件与最后离线批精确匹配。没有通过换文件清单倒推旧批执行新版。

## 4. 构建、迁移与原件身份

最终离线批为[2026-10-04T154746.119772-0000-offline](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/continuation-02/2026-10-04T154746.119772-0000-offline/offline-raw/stderr.txt)，52 tests、0 skip、OK；包含封闭DTO/输出、来源/暴露纯投影、控制故障及S1—S3确定oracle。它不证明真实provider质量或数据库事务。早期失败及不同字节批仍分别保留。

本轮唯一构建[2026-10-04T151300.859935-0000-frontend-build](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/continuation-02/2026-10-04T151300.859935-0000-frontend-build/build-raw/stdout.txt)实际执行npm run build，含tsc --noEmit和vite构建。构建后未改frontend/src或package.json，四份dist原字节hash精确一致。最终JS为index-DnD3XCQb.js，SHA256 3032cc6ca0276562664c25dcb829311af4dde8e0af87ab79d913f8b38eb78e5e。browser未运行，因此没有浏览器消费该bundle的网络与截图证据；只有源码—构建产物绑定通过。

009文件原字节SHA256为11b1c2bc8cb2482a4fa509b897c3afb8f3f5f7be3eb4e8e4aab559706944c1a3。Python read_text把CRLF转LF后实际交PG的UTF-8 SQL SHA256为e6d9628e98b74c42aba217b9068825a5fafac93b61e21cda729856ff48a984b2；migration-facts.json记的是后者，as-run-files.json记前者，二者对应同一文件，没有迁移后改版。

六类实际迁移为非空增量、重复、缺前置、同名约束篡改、中途失败及denied权限失败。五张旧表非空前后逐行hash一致，旧G7 received无正文保持无正文，无teaching回填；故障SQLSTATE P0001/42501及回滚对象集合保留。只在既定六个schema运行，未删库、表、schema、容器、卷或事实。当前非空样本尚未覆盖旧tool/unknown/正常G7读取的全部代表分支，不能称整个兼容矩阵通过。

## 5. V01—V20有限验收映射

- V01：部分；真实两版goal、CAS、零费及HTTP重放成立；完整诊断与G7显式seed入口仍缺整链观察。
- V02：部分；严格路径合同、真实接受路径前置与原子事实可复用；UI及旧建议/全部前置反例缺动态终验。
- V03：部分；三题型确定oracle、严格输出、真实隐藏/暴露投影成立；三题型真实出题与来源变化零发送缺Windows/UI。
- V04：部分；单位/数量级、概念否定、程序条件、四类反馈oracle及实际受信封套成立；实际provider质量未授权。
- V05：部分；Q耗尽仍保存、评价拒绝保留答案、真实零费HTTP和错误结果回滚成立；浏览器保存/丢响应缺运行。
- V06：部分；进度重建代码及样本已交付；H1两实例推进、辅助续答、复测和重开尚未运行。
- V07：部分；真实纠错与相反反馈保留旧hash、争议不加独立观察通过；界面标签未运行。
- V08：部分；真实同父并发同文一个效果、异文一个胜者、不分叉及HTTP同键异文409通过；SUP发送计数未运行。
- V09：部分；claimed无operation不再启动、UNKNOWN占槽及恢复PG通过；真正在途未知和浏览器丢响应未运行。
- V10：部分；真实当前资格改变后的mark拒绝成立；目标/答案晚到历史正文与零progress的实际SUP窗未运行。
- V11：部分；目录/原件校验候选、来源失效纯投影及真实引用200成立；来源替换在途与UI未运行，修后引用断言未真实复验。
- V12：未完成；原停止主体未变，只继承旧边界；本轮教学cancel及硬停止、命名Job树零没有新运行证据。
- V13：未完成；有限工具接线和配置候选已交付；本轮真实G5核算及四账未执行。
- V14：部分；严格UTF-8/大小/输出及真实合法正文原子写入有证据；新profile的原SUP通道字节未运行。
- V15：未完成；IDB/摘要持久与恢复代码和浏览器脚本已交付；原生浏览器零POST等断言尚未执行。
- V16：未完成；读取seq、活动/实体隔离、120秒/40次轮询控制已接线；hidden/unmount/切换和焦点断言尚未执行。
- V17：部分；四公开读取一条业务CTE真实计数、HTTP游标漂移409、坏单项离线抑制通过；浏览器重开与完整R03后半段尚缺。
- V18：部分；最终009六类迁移、最小权限、records全列拒写及旧无正文不回填通过；全部旧G7/tool代表兼容分支未新验。
- V19：真实provider层not_run，未授权；确定内容oracle仅证明合成内容与合同，不证明真实生成质量。
- V20：未完成；有限控制离线、尝试账和本轮实际资源收尾有证据；Windows/Job异常控制与集中独立审计未完成，不自动出101/R095。

## 6. 投入账、资源终态与恢复

新许可账见[attempt-ledger.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/continuation-02/attempt-ledger.json)：真实入口3/3、精确容器start3/3、app启动1/3、SUP.create进入0/24、browser0/2、driver0/3、frontend-build1/1。失败和预检均不退次数，未使用SUP/browser的名义额度不能抵扣入口。真实业务计50.108秒、离线含构建25.376秒；三批收尾15.828秒，10月5日只读恢复核查另3.828秒，合计收尾19.656秒。恢复收口主动时间另记checkpoint，不把夜间无运行间隔伪装成业务时间，也不清零原投入；原主动墙钟算法没有自动切分中断尾段，精确未记主动投入仍单列限制。

初轮至少9个真实入口、至少一次容器start及漏计5.940秒、部分未知投入仍保留；续作01入口4、start1、app1、build2、离线14.880/真实17.910/收尾0.890秒仍保留。旧“blocked总批exit0”不是通过，旧41项离线报告缺原始日志不作为本轮动态证据，旧009中间版不移植为当前009通过。

末批cleanup通过，taskkill只针对实际自有Popen根17312及其树；redirector实际应用21712已停止。精确容器80ae914138fa42a9ae72acf898d13f7e740b759ff09fc248470abb6df0c15d4d被停止并inspect Running=false/Pid=0，55442和18100无监听。2026-10-05恢复只读再次核容器同ID/镜像/唯一卷/512MiB/1CPU/pids128，仍停止，五个本批已知PID均未发现，两个端口无监听，见[resumption-resource-check.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/continuation-02/resumption-resource-check.json)。没有已创建SUP或Job，因此没有本轮树零/句柄关闭的教学监督证明。

两库retrolume_task100_g8_main/fault和admin/app/denied测试角色、六个固定schema、合成资料与事实、唯一卷全部保留。三次凭据仅在核归属后于内存重置和环境注入，没有落日志或证据；不会回退真实配置。Docker Desktop无需再次手工开启来解释本次失败。

## 7. 未完成项与下一步所需

完整成果还需一次修后HTTP定向复验、原launcher/SUP/worker/Job的17窗主链与异常、有限工具核算以及最终dist的三题型/恢复/存储/轮询浏览器证据。实际ALREADY_PRESENT新完整性及部分旧数据兼容反例尚不足，应在同一有限续验按影响补证，不重跑已通过的六个迁移schema或27项未受影响PG方法，不再构建前端。

真实入口和精确容器start均达到任务卡上限。本轮恢复请求明确沿用约束，未将“继续”推定为追加额度，未运行第四入口。继续这些依赖项需要用户或编排给明确的追加有界许可；所有旧计数、失败、未知投入和成果必须沿用。旧runner以起始墙钟估算主动投入，隔夜恢复前还须按实际工作段登记主动时间并保守保留尾段缺口，不能因换窗重置账。

必要用户动作仅为决定是否给剩余合成整链追加许可或将本结果转交编排；不需要真实密钥、用户库操作、删除许可或重新安装依赖。共享状态、DEF/CHG和后续集中审计由编排维护。当前完整验证阻塞有具体预算依据，候选实现和所有证据已保存，可审阅，不声称已经满足正常终点。

以下初轮与续作01原文逐字节保留，仅作历史，当前结论以上方续作02为准。

---


# TASK-100 结果：G8 完整教学闭环实施与合成验证

- 任务卡：`DocuN/tasks/TASK-100.md`
- 角色：本卡业务实现执行者（不承担编排裁定与独立审计）
- 授权终点：G8 产品实现 + 卡内合成验证 + 普通修复 + 字节与原始证据冻结；交回等待一次完整成果集中独立审计
- 结论口径：**实现完成，验证部分完成**。离线层与迁移层已通过；仓储层在真实 PG 上定位并修复 2 个真实产品缺陷，但修复后的终验与后续真实分层因用户裁定停止真实验证而 `not_run`。

---

## 续作01 结果（G8 合同修复与剩余受控验证，2026-10-03）

一句话结论：**DEF-003—007 五缺陷全部修复完成且离线验证通过；真实入口 4/4 按预算用尽，主链真实验证（009 应用/PG 终验/HTTP）未完成——但此过程中新暴露的 5 组夹具/验证层缺陷已全部定界并修码（未复验），容器已限定启动并收尾停止，g8_main/g8_fault 两库已建立（owner=admin），三测试角色凭据已安全重置。**

### 续01-1. DEF 修复明细（全部完成，离线验证）

| DEF | 修复内容 | 离线验证 |
|---|---|---|
| DEF-003 不可变事实 | records 全表禁 UPDATE/DELETE（含 applied_revision/state_after），INSERT 即最终值无回填；pg_setup 授权 records 仅 SELECT/INSERT，列级 UPDATE 白名单限 heads/commands 状态机列 | py_compile 过；权限断言在 pg_setup grant 内置（leaked/records_writable 计数） |
| DEF-004 真实上下文与屏障 | `_freeze_model_context` 锁前组包 + `accept_teaching_command` 锁内逐项核对 reference_hashes（漂移抛 version_conflict）+ T-launch 当前绑定复核（obsolete 显式检查、head.pending 不匹配返回 no_longer_current_binding）；`_load_teaching_entities`/`_build_profile`/`_stored_document` 全真实装配 | 离线单测 41 OK（含 recovery 4 反例） |
| DEF-005 只读面单语句快照 | `read_teaching_workspace` 重写为单条 CTE；view_token 用真实 source_identity_sha/command_state_sha hash（取消 "na" 占位）；source_invalid 真实计算；007 正文投影；坏单项局部抑制 → integrity_error；来源失效抑制派生正文但保留 goal/answer/correction 用户文字；前端 feedback 链改直接消费 workspace 区域 + toFeedbackView 映射 | WorkspaceProjectionOfflineTests + DtoOfflineTests 过；tsc --noEmit 过；真实 build ×2 成功 |
| DEF-006 runner 控制器 | 计账先于预检（blocked 也消耗入口）、损坏账 SystemExit(5)、timeout≠not_run、资源白名单（精确容器 ID/512MiB/1CPU/pids128）、真实 npm run build、新独立账本 attempt-ledger-continuation.json | 4 次真实入口全程记账（含 blocked/fail 如实记录） |
| DEF-007 恢复状态机 | finish_teaching_supervision 以确认后结局处理：definitely_not_admitted 仅认 `not receipt_present and state in (not_started,budget_exhausted,startup_deadline,partial_window_too_small)`；final_status=failed 才清 pending，unknown 占槽可恢复；"取消且无收据"不构成未准入证明 | SupervisionFactsOfflineTests 4 反例 + RecoveryPgTests 6 用例（PG 用例待真实验证） |

### 续01-2. 离线验证汇总

- py_compile：全部产品/测试/夹具文件通过（多次）
- 离线单测：contracts/policy/recovery-offline/api-offline 共 41 tests OK（skipped=8 为 PG 类按设计 skip）
- tsc --noEmit：通过；真实 `npm run build` ×2 成功（vite 33 modules，build 预算 2/2 已用尽）
- 断点核验：resume-check.json——86 项 hash 一致、3 项漂移均归属本窗口 DEF-003 修复（保留不回退）

### 续01-3. 真实验证账（入口 4/4 时间线）

| # | 场景 | 入口级结果 | 实际达成 |
|---|---|---|---|
| 1 | main-combo | blocked（identity_gate DSN 未注入） | 记账先行 ✓；暴露预检形态矛盾 |
| 2 | main-combo | pass（退出码 0，实际未达主链） | container-start 真实启动（pid=403，512MiB/1CPU/pids128）✓；super-resolve 打通 ✓；roles-prepare 因接线遗漏 blocked |
| 3 | main-combo | pass（同上） | roles-prepare 走到 SQL 层，暴露 ALTER ROLE 参数绑定限制 |
| 4 | main-combo | fail | **roles-prepare PASS（3 角色凭据内存重置）**；**databases-prepare PASS（g8_main/g8_fault 新建 owner=admin）**；migrate blocked（env_admin 丢 password）→ pg-repo 9 errors（空库连锁）→ pg-recovery 装载错（类名）→ fault 场景静默切库失败 → http 403（会话 token） |

资源与预算终态：real_entries **4/4 尽**、container_starts 1/3、app_starts 1/3、frontend_build 2/2、browser 0/2、driver 0/3、sup_creates 0/24；offline 14.88s、real 17.91s、cleanup 0.89s。注：#2/#3 入口级 result="pass" 系进程退出码语义（blocked 子段不计 fail），子段真相以 attempts[].source_identity 同批 runtime log 与 segments 明细为准。

### 续01-4. 新暴露缺陷定界与修码（全部已修，均未复验——无剩余入口）

1. **入口预检与合并形态矛盾**：main-combo 自带准备链但预检要求入口前注入 app 口令 DSN（口令入口内才生成）→ main-combo 预检延后到子段硬核
2. **角色凭据死锁**：runner 曾对已存在角色自行加"不重置"禁令（卡面 65 行无此明文，"不可重置"仅见于 launch 保护/预算条款）→ 改为 ALTER ROLE 设新内存口令（token_urlsafe 字面量内插，注入风险为零）
3. **migrate env_admin 丢 password**：rsplit(' ',1) 剥段后拼 dbname 导致 fe_sendauth → 改全量构造 + admin_password 入 state
4. **RecoveryPgTests 类名**：runner 两处写 PgTests → 改正
5. **fault DSN 双格式**：ensure_fault_database 的 rpartition("/") 仅适用 URL 格式，key-value 注入静默切库失败 → _switch_dbname 双格式兼容
6. **HTTP 会话 token**：403 实为 local_session 校验（非配置缺失；activity.example.json 本为占位无效模板）→ HttpTests setUp 经免 token 的 GET /api/session 取 token，请求带 X-RetroLume-Session 头

**未复验声明**：上述修码后 py_compile 全过，但 009 应用、pg-repo/pg-recovery 终验、fault 六场景、HTTP 主链、Windows 17 窗、浏览器一会话全部 `not_run`——真实入口预算用尽，属合同停止条件（任一投入上限到达即停）。**离线通过不冒充真实通过**。

### 续01-5. 资源终态与待续

- 容器：cleanup PASS，running=False pid=0（证据 runtime/cleanup-20261003T065720Z.log）
- 持久合成资源（保留）：retrolume_task100_g8_main / retrolume_task100_g8_fault（owner=admin，两库为空库待 009）；retrolume_task100_admin/app/denied 角色存在（口令已重置，仅历次运行内存持有，未落盘）
- 待续窗口第一步：重新授权真实入口后直接 `runner.py main-combo`——本次修码已就位，预期链路：角色已存在走重置分支 → 两库已存在走 preserved 分支 → 009 首次应用 → PG 终验 → fault 场景 → HTTP（token bootstrap 已修）
- 台账：`attempt-ledger-continuation.json`（7 attempts、6 corrections、只追加）；runtime 日志 7 份

### 续01-6. 续作01 证据索引

- 账本：`DocuN/evidence/TASK-100/continuation-01/attempt-ledger-continuation.json`
- 断点核验：`DocuN/evidence/TASK-100/continuation-01/resume-check.json`
- 运行日志：`DocuN/evidence/TASK-100/continuation-01/runtime/`（frontend-build ×2、main-combo ×4、cleanup ×1）

---

## 一、结论

| 项 | 状态 | 依据 |
|---|---|---|
| G8 教学闭环产品实现（后端 7 模块 + 009 迁移 + 接线 + 前端 7 件） | **完成** | `DocuN/evidence/TASK-100/final-file-identity.json`（34 文件，582056 字节） |
| 离线合同层 + 策略层 | **通过 20/20** | `runtime/offline-20261003T042953Z.log` |
| 009 迁移真实 PG 六场景 | **通过 11/11** | `batch-PG-M-migration.json` |
| 教学账本真实 PG 用例 | **部分通过 8/9**，定位并修复 2 个真实缺陷后**终验 not_run** | `runtime/pg-repo-20261003T041438Z.log`、`attempt-ledger.json` |
| HTTP 主链 / Windows 组合 / 浏览器一会话 / 前端 build | **not_run** | 用户 2026-10-03 裁定停止真实验证 |

**不签**：G8 最终验收、真实 provider 教学质量、STEP009—012、M-1、整个项目通过。

---

## 二、交付物（A—D）

### A. 后端教学域（新）
- `app/learning/teaching_contracts.py` — Strict DTO、canonical/request_sha256、semantic_slot、命令回执、低信任输出联合
- `app/learning/teaching_policy.py` — 阶段转移、路径 DAG、支持性检查、进度推导、公开投影、view_token
- `app/learning/teaching_service.py` — `submit_command` 分流、模型/工具两阶段提交
- `app/learning/teaching_api.py` — 命令 POST/GET、工作区、历史、记录读
- `app/learning/teaching_adapter.py` — 请求身份/目录来源复核
- `app/learning/teaching_prompt.py` — plan/exercise/evaluate 三固定 system prompt
- `app/learning/teaching_evidence.py` — 有限目录装配（top_k=4）
- `app/activities/teaching_repository.py` — 三表账本 Mixin（`TeachingLedgerMethods`）
- `migrations/009_teaching.sql` — 三表 + 索引 + FK + 不可变/身份守卫触发器 + `REVOKE ALL`

### B. 现有文件接线（改）
`activities/repository.py`（5 处教学钩子）、`capabilities/contracts.py`、`capabilities/gateway.py`、`service_config.py`、`main.py`、`activities/service.py`、`learning/service.py`（拒绝教学前缀绕过）、`activities/api.py`（教学操作只回元数据）

### C. 前端（新 7 + 改 1）
`teachingApi.ts`、`teachingIntents.ts`（localStorage 台账 + IndexedDB 草稿）、`teachingDrafts.ts`、`teachingIntentMatch.ts`、`TeachingExercise.tsx`、`TeachingFeedback.tsx`、`TeachingWorkspace.tsx`；`ActivityWorkspace.tsx` 挂载

### D. 测试与夹具
`tests/test_teaching_contracts.py`（9）、`test_teaching_policy.py`（11）、`test_teaching_repository.py`（9）；`tests/fixtures/task100/`：`support.py`（保留式夹具）、`pg_setup.py`、`pg_migration_scenarios.py`、`runner.py`（唯一真实入口 + 预算台账）、`diag_capture_local.py`、`diag_teaching_pg.py`

---

## 三、O01—O11 与验证映射

| 命令 | 产品实现 | 验证状态 |
|---|---|---|
| O01 goal | `apply_teaching_local` + `_teaching_apply_local_effects` | 真实 PG 通过（原子写 command/head/record） |
| O02 plan | `accept_teaching_command` + 冻结上下文 | 合同层通过；真实模型链 not_run |
| O03 accept_path | 本地 | 身份门通过（`record_not_found`）；阶段门 not_run |
| O04 exercise | `accept`+`claim`+`run_one_call`+`finish` | 合同层通过；真实链 not_run |
| O05 expose | 本地 | 合同/投影层通过（未暴露不返回参考） |
| O06 answer | 本地 | 合同层通过 |
| O07 calculate | G5 `execute_tool_action` | 合同层通过；真实工具链 not_run |
| O08 evaluate | 模型 + progress/head 同事务 | 策略层通过（两次独立观察、无 mastered） |
| O09 correct | 本地 | 合同层通过 |
| O10 abandon | 本地 | 未单独实跑 |
| O11 select_node | 本地 | 合同层通过 |

---

## 四、本卡发现并修复的真实产品缺陷（5 项）

全部为产品缺陷，非测试期望偏差（除第 5 项）：

1. **阶段门对未知动作静默放行** — `validate_transition` 用 `_ACTION_PHASES.get()`，未知动作落到 `None` 分支被当作"无限制"通过，可绕开阶段约束。改为先校验 `ALL_ACTIONS` 封闭集合。
2. **非有限数值被误报 conflict** — `Decimal("NaN")` 不抛 `InvalidOperation`，`NaN != NaN` 使合法解析路径产出 conflict。conflict 参与推进裁决，不能由非法数值伪造。改为显式 `is_finite()` 门，一律 `unchecked`。
3. **进度推导两处错判** — ①`all(...)` 带 `if dim in observations` 过滤，缺失必需维度时因空集真而判"满足"；②独立观察未按 `answer_record_id` 去重，同一作答重复计入。改为逐维命中 + `len(set(...))`。
4. **不可变触发器误拦同事务投影回填** — `teaching_records_immutable` 禁止一切 UPDATE，但仓储必须在同事务回填 `applied_revision`/`state_after`（099 的保留/修补/前进裁决）。结果是**任何本地命令都失败**。改为只保护身份/正文/来源/创建时点，DELETE 一律禁止。
5. **head 指针哨兵被当 UUID 传** — `_teaching_update_head` 只对 `node_id` 特判 `"__clear__"`，UUID 列（`path_record_id` 等）未处理，PostgreSQL 报 `22P02 invalid input syntax for type uuid`。**第二版目标必然失败**。改为统一哨兵常量，NULL 化对所有列一致生效。

第 5 项修复后 `py_compile` 通过，但**终验 not_run**。

另修正 1 项测试期望偏差（非有限数值应判 `unchecked` 而非空列表），以及 4 项错误码/返回结构期望写错。

---

## 五、009 迁移真实 PG 场景（11/11 通过）

| 场景 | 结果 | 关键事实 |
|---|---|---|
| M01 非空升级 | PASS | 三表建成；`activities 1→1`、`teaching_heads=0`，零回填旧行 |
| M02 重复执行 | PASS | 整体回滚，无多余对象 |
| M03 缺 008 前置 | PASS | 拒；`teaching_tables=0`，无半状态 |
| M04 008 约束被删 | PASS | 拒（不只比表名）；无半状态 |
| M05 事务中途失败 | PASS | `1/0` 注入后三表与两触发器全不存在 |
| M06 权限不足 | PASS | denied 角色对教学三表 3/3 真实拒绝 |

修正后的迁移重建了主库（`retrolume_task100_main`，DROP WITH FORCE + OWNER=admin）。

---

## 六、资源账

| 项 | 上限 | 实际 |
|---|---|---|
| 真实入口 | 6 | **6（耗尽）** |
| 容器启动 | 4 | 1（`retrolume-task-100-g8-pg1`，Up） |
| 应用启动 | 6 | 0 |
| SUP 创建函数进入 | 32 | 0 |
| 浏览器 | 3 | 0 |
| driver | 4 | 0 |
| 前端 build | 3 | 0 |
| 真实秒 | 5400 | 51.23 |
| 离线秒 | 2400 | 0.75 |

台账：`DocuN/evidence/TASK-100/attempt-ledger.json`

预算调整（均经用户裁定，记录在 `adjustments`）：
- 041121Z 运行改记 `not_run` 并释放 1 次入口（沙箱阻止在证据目录内写 `OriginalStore` `.incoming-*` 临时文件，属环境限制）
- 最终裁定：停止真实分层验证，不再释放预算

---

## 七、保留式夹具与数据保留

按用户指示，夹具已取消全部 DELETE：只核对专库身份并记录残留量。合成数据与失败证据保留在 `retrolume_task100_main` 及证据目录内，清理权归编排。原件暂存目录已移出证据目录（`%TEMP%/retrolume-task100-originals`），避免与证据冻结冲突。

专库身份核对：库 `retrolume_task100_main`、角色 `retrolume_task100_app`，runner 在每个真实场景前硬核对，不符即 `not_run`。

---

## 八、未验证 / 风险 / 偏差

### 未验证（not_run）
1. `pg-repo` 终验（哨兵修复后）——**最高优先级**：缺陷 5 的修复未在真实 PG 上确认
2. HTTP 主链（O02/O04/O07/O08 的真实请求-响应）
3. Windows 组合八窗口、晚到/UNKNOWN/硬停
4. 浏览器一会话（草稿→摘要→POST 顺序、轮询上限、context_key 迟到保护）
5. 前端 `npm run build` 与 served bundle 身份
6. 缺陷 4 的修复仅在重建库后由 M01—M06 覆盖，**未由真实命令写入路径回归验证**

### 风险
- 缺陷 4/5 同属"迁移约束与仓储实现不一致"，可能还有第三处未被发现；建议独立审计优先复跑 `pg-repo` 终验
- `teaching_records_immutable` 现允许投影列回填，需确认 `applied_revision`/`state_after` 不会被用于改写事实语义
- 前端 7 件从未经浏览器实跑，IndexedDB/localStorage 容量与顺序保证仅有静态保证

### 偏差
- 预算口径：卡面"真实入口 ≤6"在实现过程中被早期未走 runner 的直接执行消耗，runner 建立后无法追溯校正，故最终真实分层未执行
- 原件目录从证据目录移出，属对沙箱限制的适配，已在夹具注释与本文件记录

---

## 九、证据目录

`DocuN/evidence/TASK-100/`
- `input-snapshot.json` — 56 必要输入身份（前置）
- `batch-B1-offline.json` — 离线批次与 4 项修正
- `batch-PG-M-migration.json` — 迁移 11 场景
- `attempt-ledger.json` — 预算台账、逐次尝试、源码身份、调整记录
- `final-file-identity.json` — 34 文件最终字节身份
- `runtime/` — 各次 as-run 日志与 `diag-local-error.json`（原始数据库错误）

---

## 十、给编排的建议

1. 独立审计**第一件事**：复跑 `pg-repo` 终验，确认缺陷 5 修复生效（需新批真实入口预算）
2. 缺陷 4/5 建议合并为一条设计一致性检查项：迁移层约束与仓储层写入模式必须逐条对账
3. HTTP/Windows/浏览器分层与前端 build 需在获得新预算后一次性排期
4. `DocuS/执行动态文档.MD` 需登记本卡结论与上述未验证项（本卡未代写）
