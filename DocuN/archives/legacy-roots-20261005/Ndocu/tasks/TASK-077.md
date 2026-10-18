# TASK-077 / R-071 — 修正轮02：补齐ActivityLease返回字段（当前待转交）

你是本卡执行Agent。接收：Codex Sol，C强档；继续TASK077原实现窗口，完成修复与本轮最小验证后统一回传。本轮不是重做首轮实现或修正轮01，也不是独立审计。首次操作前如实登记实际客户端/模型；不能仅照卡面声称Sol。指定模型不可用则报告，不冒用身份。
关联STEP008、父076、078/review-02 N1、NFR002/003、SEC002、FLOW005、DATA007。需求v1.1、架构v0.28、执行状态v1.28。沿用原窗口及原编号，因为这是未验收077原合同遗漏；单行修改但涉及受控租约返回契约，原强档窗口有上下文，足以限域处理。
项目根：D:/shspic/project_NO3_RetroLume-agent。
入口：D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。
公共AGENTS：D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD。
公共WORK（编排依据，执行者不必全文读）：D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/WORK.MD。
公共库只读；规则修改时间仍为AGENTS 2026-09-22T10:50:32.1271135+08:00、WORK 2026-09-22T10:50:40.8660779+08:00。同窗口只补读变化；最小上下文本段、原合同ActivityLease/claim返回条款、Ndocu/results/TASK-078-result.md的review-02 N1位置和当前定义/构造调用。无需重读全部方案/审计。

事实与目标：当前repository.py约70—77行ActivityLease仅activity_id/executor_id/execution_generation/scope_revision/lease_expires_at五字段；约382—389行claim成功路径传入第六参数effective_window，运行时必TypeError。这是原合同要求的window_seconds字段漏实现，首轮compile不能证明构造成功。N1静态证据已足，不重复运行修改前失败。D1/D2/O1已修并保留，不能再次重做。

动作：在ActivityLease的lease_expires_at之后补必填window_seconds: int，使六位置参数顺序一致，调用方可读取实际W_eff。保留frozen=True，不加默认值，不截断成功路径参数，不改事务、锁序、分支、SQL或迁移。只允许必要这一字段修改；若发现仍须改其他产品逻辑，停相关项回报根因/范围，不能顺手扩围。

写权限：backend/app/activities/repository.py仅上述字段；Ndocu/evidence/task-077/revision-02/用于前快照、差异、构造检查脚本/日志/前后hash；更新Ndocu/results/TASK-077-result.md，当前轮置顶并完整保留首轮/修正轮01。其他五目标文件、001/002/003、正式docu、公共库及全部旧证据只读。编排统一维护状态和CHANGE。
开始前六文件冻结值（本段替代所有历史冻结值）：
- repository.py：33b733e66fcabb7a86edf9c6080051c55ecb1294042d60b6afa176a13dffa57e
- backend/app/activities/__init__.py：6bdb960912ea3fc7ddd8730f37a44e580b73768e1067d23facc9983ca04a46dd
- backend/migrations/004_activities_time_budget.sql：8f04f57c743c260f5081e0c6f232860301b30c7b03fef69498d7c0704c0a97cc
- backend/tests/test_activity_time_budget.py：63a19d1f2a99236d56bd1cc1841953908fa8c1f955ff0c6d5d61b4ee84621a86
- backend/tests/test_activity_ledger.py：fb174d4c29355bb0e57ac013d4e8555ef9ac342e9be804e0edbf732112de63da
- backend/tests/test_activity_recovery.py：0e5d9c89a7a3fce490cc60deb7c0a608b8c54356edd7c4b18ee66165bf88bf7a
repository完整路径为D:/shspic/project_NO3_RetroLume-agent/backend/app/activities/repository.py，其余均相对实际项目根。不明漂移/EBUSY覆盖/并发变更先停止受影响文件，保留事实，不覆盖猜测恢复。无Git仓库，不初始化或提交。

最小验证子项（C档、本轮新增预算）：一次改后真实Python数据类构造检查，补足单纯compile无法发现N1的证据。使用现有D:/shspic/project_NO3_RetroLume-agent/backend/.venv/Scripts/python.exe，工作目录backend，以-B执行revision-02下短脚本；导入实际app.activities.repository.ActivityLease，使用合成活动/执行者/代次/范围/datetime及79作为第六位置参数构造，断言window_seconds==79且其余字段按位置保留。不复制数据类或mock构造，不实例化仓储/连接DB，不读取配置/环境密钥，不写pyc。运行前仅确认直接导入路径无连接副作用；如存在此类副作用停下报告，不改业务或绕过。记录真实命令、被测hash、输出、退出码、耗时。
改后这一批上限60秒；有明确本范围修正依据最多一次复检，无依据不重试。此为N1新增增量额度；首轮及revision01已消耗检查额度不恢复。达到上限或两次有据修正仍失败交回，不循环试错。导入已检查语法，无须额外compile全文件/全测试。用现有post_hashes和修正轮01证据保留D1/D2/O1，仅差异/hash核对其他五文件未变。
禁止运行PG、迁移、unittest套件、Docker、应用服务、真实模型、安装/联网；不复测055/074，不建立通用测试框架。构造成功只能关闭N1构造缺口，不能宣称claim事务或数据库通过。

协作资源：仅该产品文件和revision-02输出独占，串行；无端口/账号/DB/容器/后台进程。078/review-02已返回，后续审计暂不并行读取正在修改的快照。原13元付费额度耗尽、PG预算0、旧运行资源保持，不接管或删除。
验收：实际字段存在且类型/位置满足返回契约，一次构造检查成功、有明确差异和新repository hash、其他五文件hash不变；结果保留未验证限制。完成即停；独立强档审计和真实PG仍由编排后续安排。审计原实际GLM-5.3-Flash与指定Sol不一致，其有效发现保留但不能由本实现窗口补签强档独立结论。
返回：实际模型/窗口、N1修正范围、命令及客观证据、六hash及未变化证明、未验证/风险/文档建议。保存D:/shspic/project_NO3_RetroLume-agent/Ndocu/results/TASK-077-result.md，当前修正轮02置顶、保留各轮历史；确认可读后只回一句结论和可点击绝对路径，不填编排最终验收。

---
## 历史附录：修正轮01及首轮合同（只作追溯，不重新执行）
以下旧调度状态、版本、写范围、hash和预算由上方修正轮02替代，原需求契约继续适用。
# TASK-077 / R-071 — 修正轮01（当前待转交）

首轮实现及TASK-078审计结果均已收到。本次仅修复审查发现，不重新实现时间账本，不重跑首轮检查。
接收：Codex Sol C强档；继续TASK-077原实现窗口。当前执行范围、冻结hash、预算和回报方式以下方“接续修正轮01”为准。
文件末尾保留首轮合同仅用于追溯原需求；其中旧“新会话”、旧版本、旧hash、原全量修改范围及全文回传要求均不再作为本轮操作指令。
## 接续修正轮 01（2026-09-22；当前有效执行指令）

你是本卡执行 Agent，继续 TASK-077 / R-071 原实现窗口（Codex Sol，C 强档）；不新开任务、不重做首轮实现。原窗口确实不可用时才按本卡交接至同档新窗口，保留失败历史和额度，禁止两窗同时执行。本轮状态待转交，首轮部分通过保留。本卡涉及迁移约束和测试契约，沿用掌握实现的强档能限域可靠修正；不是独立审计。

目标：一次完成时间账本候选的三个已知缺口及同一测试调用点的遗漏适配，交付可供独立复核的最终差异。当前需求v1.1、架构v0.27、执行状态v1.25；STEP-008仍进行中/部分验证。用户批准范围仍限五列账本基础、内部接口和测试准备。

实际项目根：D:/shspic/project_NO3_RetroLume-agent。
入口：D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。
公共规则：D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD（修改时间2026-09-22T10:50:32.1271135+08:00）。
编排依据：同公共根/docu/WORK.MD（2026-09-22T10:50:40.8660779+08:00）、Ndocu/TASK_TEMPLATE.md（2026-09-22T10:50:42.6645261+08:00）、Ndocu/prompts/07_开发执行循环.md（2026-09-22T10:53:59.6314667+08:00）；执行者不必读编排全文。公共库只读，项目内旧docu/AGENTS.MD不替代入口映射。
最小上下文：本卡原合同与本补充、公共AGENTS变化、Ndocu/results/TASK-076-work-decision.md批准记录、自己的TASK-077-result.md及原始证据、架构时间账本增量。必要时读取TASK-078-result.md的D1/D2/O1原始位置；不需要重读075/076方案。未变且已读内容不重复加载。

本轮读写范围：仅修改 backend/migrations/004_activities_time_budget.sql、backend/tests/test_activity_recovery.py、backend/tests/test_activity_time_budget.py；新增证据仅 Ndocu/evidence/task-077/revision-01/；更新 Ndocu/results/TASK-077-result.md并保留首轮全文及历史。repository.py、__init__.py、test_activity_ledger.py只读冻结；001/002/003、其他业务、正式docu、公共库、旧证据禁止修改。正式状态及CHANGE由编排回收后统一维护。

开始前核对以下SHA256；先保留本轮三文件前快照/hash，不能覆盖首轮pre。项目当前不是Git仓库，不初始化Git；用副本差异。出现不明漂移/并发写入或再次EBUSY覆盖事件，停止冲突文件并回传，禁止重写整文件恢复猜测版本。
- backend/app/activities/repository.py：33b733e66fcabb7a86edf9c6080051c55ecb1294042d60b6afa176a13dffa57e
- backend/app/activities/__init__.py：6bdb960912ea3fc7ddd8730f37a44e580b73768e1067d23facc9983ca04a46dd
- backend/migrations/004_activities_time_budget.sql：1501e1f1dd38770eceaf26430882a62e9bac8fdfec41d6303c8531ef0654db6b
- backend/tests/test_activity_time_budget.py：a4e3070eb2137da8feb28a67161f391bd9568264189410cf97c52f966bea5ab4
- backend/tests/test_activity_ledger.py：fb174d4c29355bb0e57ac013d4e8555ef9ac342e9be804e0edbf732112de63da
- backend/tests/test_activity_recovery.py：93ab4e2c5a481dc7b880ef7c8e696b9ac4981e7e52938b095f12a8fb8ebd3cba

连续完成以下修正后统一回传：
1. D1及同点遗漏：recovery test_04第二个ActivitySpec补max_running_seconds=3600；其other_lease调用（当前301行）补window_seconds=300，并在传给intent前明确assertIsNotNone。当前该调用即使修好构造仍会缺参数报TypeError；不要只修构造。保留创建前登记extra_activity_ids、FK清理和原业务断言。静态确认本文件所有相关构造/claim调用均符合既有合同，不扩大业务修改。
2. D2：保持test08原数字和前序向上取整/零秒/有效租约冲突检查。过期折叠后应成功取得window_seconds=79，明确非None，并核对S=121、R=79、M=200、可用余额0、status=running及租约身份/代次与返回一致；不硬编码generation数字。修正误导的耗尽注释/用例名称（如改名，报告新旧映射），保留未知活动冲突检查。真实耗尽None及关闭已提交继续由test04覆盖，不能删除或降低该断言。不改实现迎合错误预期。
3. O1：004为last_settled_generation增加允许NULL、非NULL须>=0的数据库CHECK，保持INTEGER类型及五列/成对NULL约束，不增加第六列，不以应用验证替代DB域约束。保留锁内判空、事务、非空拒绝、余额及running形状。只改候选DDL，不执行。结果给后续真实PG增加“generation=-1且seconds=0被拒，NULL/NULL及0/0合法”的反例/正例建议；无需为此创建运行框架。

协作资源：本轮串行独占这三文件及revision-01证据路径；无端口/数据库/容器/账号/后台进程。不得接管旧运行资源，不安装、不联网、不调用真实模型、不读用户DSN/密钥、不提交推送。若发现原窗口还有其他在途任务先报告目标/hash，不重复派发。

验证子项（C档执行）：新改动需要局部语法与合同一致性证据，已有首轮compile/旧074 PG证据保留、不重跑。一次三文件差异/参数/断言/DDL域一致性检查；对本轮修改的两个Python测试文件，使用现有D:/shspic/project_NO3_RetroLume-agent/backend/.venv/Scripts/python.exe，以脚本文件读取源码后compile、不import、不写pyc，单批最长60秒。允许修改后这一批及有明确新修正依据时最多一次复检；这是本修正增量预算，首轮已消费预算不重置。两次有据修正仍失败、环境启动失败或达到额度立即返回，不换壳盲试。记录实际命令、退出码、耗时、改前后hash、有限diff至revision-01；不得用语法成功宣称用例或SQL通过。
不运行unittest/PG/迁移/Docker，不复现已知TypeError，不重测055/074，不新增mock或SQL字符串匹配测试。禁止借无DSN skip称通过。

验收：上述修正均落实、未改三份冻结文件和旧迁移、原业务断言/清理保留、差异及新语法证据完整；004与真实八例及受影响旧测试仍标未运行。超出三文件、发现需改产品事务/主要模型/新依赖或不明漂移，先停止受影响部分并带事实交回。完成即停，不重复审整仓。强档独立审计必须与实现隔离，TASK078资格尚未证实，本执行窗口不能补签审计；修正回收后由编排另行安排必要独立复核及PG，不能据此关M-1或STEP008。

回报：更新D:/shspic/project_NO3_RetroLume-agent/Ndocu/results/TASK-077-result.md，顶部列本轮结论、三文件实际差异和证据导航，保留首轮及失败历史；列实际客户端/模型标签、窗口是否续用、检查及未运行项、风险、文档建议。确认保存可读后只回复一句结论和可点击绝对路径，不展开全文、不填最终Work验收。无需用户选择测试数字或重新批准已授权范围。
---

## 历史附录：首轮合同（只读追溯，不重新执行）

以下保留原合同及固定行为标准。执行动作仅限上方修正轮01；本附录不授权重做首轮实现或重复消费原检查预算。
你是本卡执行Agent，完成后输出结果供用户带回Astra。
TASK-077 / R-071；开发：时间账本基础切片；STEP-008；父TASK-076，关联075/071/072/074、NFR-002/003、SEC-002、FLOW-005、DATA-007。
执行者Codex Sol，C档强档，新会话。涉及事务、余额守恒、幂等及迁移，需强档；本卡不是独立审计。
根D:/shspic/project_NO3_RetroLume-agent；需求v1.1、架构v0.26、执行状态v1.22。
授权：用户2026-09-22明确“批准时间账本基础切片”；具体边界Ndocu/results/TASK-076-work-decision.md。本卡只实现及准备测试，不执行迁移/PG。

目标：
实现持久时间额度的预扣、结算、保守折叠和取消；无worker/HTTP/模型接线。不宣称M-1或实际运行时长已受控。
074已验证旧代次恢复；复用实现，不重写恢复器。

上下文：
先读根AGENTS.md、docu/AGENTS.MD、Work裁定文件；架构FLOW-005及时间账本批准增量。
读backend/app/activities/repository.py、__init__.py、001/002迁移、backend/tests/test_activity_ledger.py和test_activity_recovery.py。
075/076旧方案仅作历史，冲突以Work裁定和本卡为准，不继承其错误公式/代次示例。
冻结repository SHA256=50ec537b07533c68194651b008d275176430effeb67126391ef43b96155cfce6；
recovery测试=7839af04e3043a173f8caaeefd5085ff72e138891207a0e882d8b2ef585d15e4。
其他目标文件先存副本/hash；不符查明，不覆盖已有改动。

允许文件：
backend/app/activities/repository.py、必要__init__.py导出；
新增backend/migrations/004_activities_time_budget.sql；
backend/tests/test_activity_ledger.py和test_activity_recovery.py中必需构造/认领参数适配；
新增backend/tests/test_activity_time_budget.py；
Ndocu/evidence/task-077/、Ndocu/results/TASK-077-result.md。
禁止修改001/002/003、gateway/transport/HTTP/main/runtime、依赖锁、正式docu、旧证据；不建worker，不改用户库，不安装/联网/模型/容器/Git提交。
本卡独占上述文件，无并行测试。正式文档仅由Astra维护。

固定契约：
1. activities增加5列max_running_seconds、running_reserved_seconds、running_settled_seconds、last_settled_generation、last_settled_seconds。M>0，R/S/历史数值非负，R+S<=M，running当且仅当R>0；其余状态R=0。计数用足够范围整数，校验上界、加法或CHECK采用防溢出写法；不存在无限预算/自动免费默认。
004在单事务先锁activities再判空并DDL；非空明确失败并全回滚，禁止先无锁判空再迁移。002保持不变；本卡只写迁移，不运行。

2. ActivitySpec新增必填max_running_seconds，拒绝bool/非整数/非正/超存储范围；create_activity写M及零计数。
claim_lease新增必填关键字window_seconds，非bool整数1—3600；保留lease_seconds原限制，不把墙钟或租约长度称为实际单调时间保证。
成功返回ActivityLease（增加window_seconds字段，返回实际预扣W_eff）；预算不足返回None，唯一含义“未获得新租约：时间预算耗尽”。其他原冲突仍按既有异常。
调用者必须检查None；本卡仅既有合成测试调用方，无产品接线。

3. 同一来源→活动→操作锁序，单短事务：
普通认领先校验原准入条件，A=M-S-R，W_eff=min(window_seconds,A)；有余额才预扣并建立新代次。
旧running租约按既有规则允许接续时，先将真实残留R全额移入S并清零、关闭旧代次资格；不能折叠已结算pending/R0窗口。
若折叠后A=0，提交折叠及关闭（pending、executor/lease清空、代次失效），返回None；禁止用事务内异常回滚后声称关闭。若可认领，则原子折叠并建立新代次一次；不硬编码测试代次，写清两路径递增规则。
不得抢占有效租约，不改变来源/取消/过期冲突含义。时间预算不足的返回与未知活动/有效租约冲突必须可区分。

4. 新增settle_execution_window(activity_id, executor_id, execution_generation, *, window_seconds, elapsed_seconds)。
仅可信内部合成调用，本卡无外部路由。elapsed_seconds必须有限非负数，拒绝bool/NaN/无穷；C=向上取整秒数，0仅表示真实零耗时；拒绝C>W，不静默钳制超额。整数范围与SQL一致。
正常路径要求running、executor/代次匹配、R等于实际W，原子S+=C、R-=W、关闭本代次（递增generation、pending、executor/lease清空），写最近结算G及C。返回明确settled。
最近已结算G相同且规范化C相同，返回already_settled不改账；C冲突拒绝；更旧或未知G拒绝且不改账。只承诺最近G/C的受限确认，五列无法确认任意历史executor/W，不虚构完全请求回放能力；这些参数仍校验格式，确认分支不授予任何执行资格。
重试判断与事务锁一致，不能因已关闭状态先拒绝所有幂等重试。提交成功响应丢失按持久事实重试，不重新折叠/退款。
接口不提供停止证明，也不等于准许生产退款；未来调用方必须先证明本窗口不能继续出站/执行，当前生产组合保持未接线。

5. cancel按既有锁序及幂等：真实在途R全额转S，R0，取消终态及代次失效；重复取消不重复扣账。
模型次数/费用预留不动，旧操作不重发；record_outcome旧UNKNOWN纪律保持。
不修改list/recover/admit/mark/record主体，不顺手换时钟。若新不变量确实迫使其他接口改变，停止相关改动，报告具体冲突，不扩大范围。

6. 既有两测试文件只适配ActivitySpec必填和claim参数/None检查；保留业务断言和069定向FK清理。
新增真实PG测试准备，调用实际仓储，专用RETROLUME_TIME_BUDGET_TEST_DATABASE_URL缺失明确skip，绝不回退用户DSN；每例合成ID定向清理。
覆盖紧密场景：M200/W100/C20→S20/R0/A180；相同结算重试及冲突；已结算后新认领不折叠；未结算崩溃残留按允许接续条件全额折叠；折叠耗尽返回None且关闭已提交；取消/重复取消；旧代次晚到拒绝；参数非法和向上取整；数据库CHECK/非空迁移拒绝留真实运行验证。
不得改本机/DB系统时间来造样本；用合成行的租约前提，不把它称真实回拨实验。
测试只准备，不跑PG/unittest/迁移。

本卡最小验证：
一次差异/调用位置/不变量一致性检查；项目现有backend/.venv/Scripts/python.exe读取改动Python文件compile，不写pyc，单批≤60秒；有明确修正依据最多一次复检。
不复现旧失败、不运行旧055/074、不造SQL字符串断言/mock冒充事务验证。记录真实命令/退出码、新旧hash、差异及未运行测试；已完成即停。
后续独立审计与PG由Astra另卡安排，只覆盖实际影响；不在本卡追加。

交付/停止：
实现上述基础契约及测试准备，迁移未执行、真实PG未验证明确标记；字段/签名/返回语义实际清单必须完整。
出现范围扩大、既有状态冲突、需要第6列或额外服务/主要模型变化时，先完成不受阻部分，交回具体差异，不自行实施。
回传TASK/R/STEP、建议状态、文件差异、事务/接口/边界、命令/hash/证据、未验证风险、文档建议、必要人工操作、下一步。
保存Ndocu/results/TASK-077-result.md并回复完整可复制块；不填Astra最终验收，不宣告M-1/STEP008完成。

