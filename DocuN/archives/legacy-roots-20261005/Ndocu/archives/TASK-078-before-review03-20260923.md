## 历史附录：此前合同（保留追溯，不重复执行）
旧接收模型、强档资格补审、hash及全量审查要求由上方review03和用户最新指示替代；原行为标准仍有效。
# TASK-078 / R-072 — 修正后强档独立补审（当前待转交）

你是本卡独立审计执行Agent，不接管编排、不修改被审代码。完成完整范围后统一回传。
接收：Codex Sol，C强档；全新隔离窗口，不能使用TASK077实现窗口。原078由Work Buddy其他模型完成，用户已确认属于GLM/KIMI等其他模型但未明确型号，尚不能确认原强档资格。原有效发现/证据保留；本轮补齐高风险强档结论，不推定其他模型不具能力。沿用TASK078/R072，不因换执行者或窗口新占编号。
关联：STEP008、父TASK077、NFR002/003、SEC002、FLOW005、DATA007。需求v1.1、架构v0.27、执行状态v1.27。数据约束/事务/幂等错误风险高，需独立强档；实现者自查不能替代。
实际根：D:/shspic/project_NO3_RetroLume-agent。
入口：D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。
公共AGENTS绝对路径：D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD。
编排依据公共WORK绝对路径：D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/WORK.MD；执行者不必读取全文。公共库只读，不以项目内旧副本替代入口映射。规则修改时间仍为AGENTS 2026-09-22T10:50:32.1271135+08:00、WORK 2026-09-22T10:50:40.8660779+08:00。

目标：对当前时间账本候选给出可供编排裁定的强档独立代码结论，确认三个修正及调用适配，并形成可直接编排的最小PG清单。原078八项标准继续适用；只处理该切片，不能借补审扩成M-1/worker或全仓审计。
授权边界：五列时间账本及可信内部claim/settle/cancel，尚无生产接线；用户库、真实模型、迁移运行不在本卡。原13元费用额度已尽，PG运行额度0。

独立输入按顺序：
1. 根入口、公共AGENTS、本卡当前段及末尾八项原始标准。
2. D:/shspic/project_NO3_RetroLume-agent/Ndocu/tasks/TASK-077.md的原始固定契约和修正轮01执行要求，只作为需求，不读取实现聊天/思考/自评。
3. 六份被审文件及必要直接依赖；首轮原始前快照Ndocu/evidence/task-077/pre/四文件；修正前快照Ndocu/evidence/task-077/revision-01/pre__004_activities_time_budget.sql、pre__test_activity_recovery.py、pre__test_activity_time_budget.py。
4. 原始有限差异可复用Ndocu/evidence/task-078/diff-*.txt、Ndocu/evidence/task-077/revision-01/diff_revision01.txt；用当前hash确认适用范围，不为换窗重新生成重复证据。需要原始结构可读001/002/003，但mtime不证明未变；缺旧hash时明确证据限制。
不读TASK077结果文档及完整执行状态、交接聊天、实现者自评。无需先读原078结论，独立形成判断后可为结果续写而读取原078结果保留历史；披露接触范围，不把前一模型结论当作自身证明。不要求把历史报告删除/覆盖。

当前冻结SHA256（本段替代末尾历史hash）：
- backend/app/activities/repository.py：33b733e66fcabb7a86edf9c6080051c55ecb1294042d60b6afa176a13dffa57e
- backend/app/activities/__init__.py：6bdb960912ea3fc7ddd8730f37a44e580b73768e1067d23facc9983ca04a46dd
- backend/migrations/004_activities_time_budget.sql：8f04f57c743c260f5081e0c6f232860301b30c7b03fef69498d7c0704c0a97cc
- backend/tests/test_activity_time_budget.py：63a19d1f2a99236d56bd1cc1841953908fa8c1f955ff0c6d5d61b4ee84621a86
- backend/tests/test_activity_ledger.py：fb174d4c29355bb0e57ac013d4e8555ef9ac342e9be804e0edbf732112de63da
- backend/tests/test_activity_recovery.py：0e5d9c89a7a3fce490cc60deb7c0a608b8c54356edd7c4b18ee66165bf88bf7a
漂移即停止受影响审查，不以旧hash给当前通过。当前无其他授权写入；串行冻结，不占端口/DB/容器。

重点增量与验收：
- recovery test04第二ActivitySpec的M3600、claim W300及None检查完整；原隔离/分页业务断言、创建前ID登记与FK清理保留。
- 新test08改名为test_08_ceiling_rounding_zero_and_fold_reclaim_partial_window：M200、已结算S21、残留100折叠后S121、新R79、可用余额0；返回窗口79及身份/代次与DB投影一致。正常真实耗尽仍由test04证明候选覆盖。不得要求改产品实现迁就旧None断言。
- 004历史generation增加非负CHECK，NULL/NULL与0/0合法，-1/0非法；仍为五列、锁内判空、同事务非空拒绝、无回填。逐列域一致，不能用应用验证代替DB约束。
- 为补齐此前未确认的强档门，对首轮生产差异按末尾标准1—6独立形成一次判断；不重审未受影响的恢复器或其他模块，只看实际claim/cancel依赖影响。标准7仅围绕现有测试及修正；旧有效原始证据复用。
- 标准8输出具体测试类/方法或缺口及依赖理由：新八例、004空表成功/非空拒绝并回滚、各必要CHECK负例及正例；旧用例按claim/cancel/必填夹具实际依赖逐项选取。若确实覆盖旧两文件全部须说明，不能机械全跑，也不能为了数量少删真实影响覆盖。只给清单，不编写运行框架。

写入只限：Ndocu/evidence/task-078/review-02/必要新增范围/hash/结论依据；Ndocu/results/TASK-078-result.md新增本轮段置顶并保留原轮历史。正式docu、公共库、业务/测试/迁移、原证据均只读。无新增依赖/安装/联网/真实配置读取/Git提交。不得运行compile、unittest、PG、Docker、EXPLAIN、应用或模型调用。
预算与停止：一次有界代码审查，覆盖八项即停，不重复采集未变证据，不为归档重跑。此为补齐强档资格与修正快照的新增审计轮；旧轮预算和结论保留，不自动续跑旧测试。发现确定缺陷不自行修改，给触发、定位、影响、最小建议；冻结不稳/新增高风险越界/所需模型能力不可用则回传具体缺口。普通步骤卡内连续完成。

交付：逐项结论与原始位置、增量修正是否满足原合同、当前代码层通过/有条件通过/不通过/证据不足、最小PG清单、未验证和剩余门。不能用代码结论宣称PG/迁移、M-1或STEP008通过。记录实际客户端/模型标签及可得标识（不要求API配置或密钥）、新会话独立性、读取范围/意外暴露、命令/证据与当前hash。
回报保存D:/shspic/project_NO3_RetroLume-agent/Ndocu/results/TASK-078-result.md；先本轮摘要/证据导航再详情，原轮历史保留。确认可读后只回复一句话结论和可点击绝对路径，供用户转交编排；不展开全文、不填写Work最终验收。

---
## 历史附录：首轮任务合同
原八项审查标准继续作为验收要求；旧版本/hash/窗口及全文回传方式由上方当前指令替代。
你是本卡独立审计Agent，完成后回传结果，不接管编排。
TASK-078 / R-072；独立只读代码审计；STEP-008局部；父TASK-077，关联076/072/074、NFR-002/003、SEC-002、FLOW-005、DATA-007。
接收Codex Sol C档，全新隔离会话，未参与077实现。事务/迁移/退款语义风险需强档。不是运行测试卡。
根D:/shspic/project_NO3_RetroLume-agent；需求v1.1、架构v0.27、执行状态v1.23。
目标：一次审完077实际变化，给出是否可进入定向PG验证的代码结论及必要用例范围，不重审整仓，不要求测试证明本卡未实现的worker。

独立输入：
根AGENTS.md、docu/AGENTS.MD；Ndocu/tasks/TASK-077.md完整原合同；架构FLOW-005/本次批准边界（跳过Work验收与实现自评段）。
原始源码、004迁移和对应测试；原始修改前副本位于Ndocu/evidence/task-077/pre/：
backend__app__activities__repository.py
backend__app__activities____init__.py
backend__tests__test_activity_ledger.py
backend__tests__test_activity_recovery.py
允许自行只读生成有限diff和hash，不运行代码。
不读077结果、自评、执行聊天或其推理。不继承实现会话；偶然暴露须披露，不伪称独立。已知本次是未接线内部时间账本，不带入“已完成M-1”的假设。

当前冻结SHA256：
backend/app/activities/repository.py
33b733e66fcabb7a86edf9c6080051c55ecb1294042d60b6afa176a13dffa57e
backend/app/activities/__init__.py
6bdb960912ea3fc7ddd8730f37a44e580b73768e1067d23facc9983ca04a46dd
backend/migrations/004_activities_time_budget.sql
1501e1f1dd38770eceaf26430882a62e9bac8fdfec41d6303c8531ef0654db6b
backend/tests/test_activity_time_budget.py
a4e3070eb2137da8feb28a67161f391bd9568264189410cf97c52f966bea5ab4
backend/tests/test_activity_ledger.py
fb174d4c29355bb0e57ac013d4e8555ef9ac342e9be804e0edbf732112de63da
backend/tests/test_activity_recovery.py
93ab4e2c5a481dc7b880ef7c8e696b9ac4981e7e52938b095f12a8fb8ebd3cba
hash漂移则报告，不对旧快照出当前通过结论。

审查标准：
1. 五列DDL与Python域一致：正/非负/上界、NULL成对语义、M/R/S不溢出和running形状；原合同要求历史数值非负，逐列查实际约束，不用应用校验替代宣称DB有约束。nullable表达“未结算”可保留，但不能允许非法已结算值。
2. 004同事务先锁再判空，非空拒绝不留下部分DDL；无自动回填/用户库修改；001/002/003未改。不据静态DDL声称迁移已运行。
3. claim普通/折叠/耗尽分支保持锁序和原冲突；仅残留R折叠；耗尽关闭必须提交后None，不异常回滚；成功实际W=min(请求,余额)，ActivityLease与返回契约一致。pending耗尽不无故写行。
4. settle向上取整、非法数值与范围、当前身份/代次/R匹配、整窗移出R只将C入S、原子关闭旧资格。审查极端输入是否符合拒绝契约及错误传播；不以普通样例覆盖全部参数域。
5. 最近G/C受限幂等在锁内判断；关闭后重试不改账；冲突/更旧拒绝；提交响应丢失不重复折叠；cancel竞争和重复取消不重复扣费。五列不保存历史executor/W的限制是已批准内部契约，不要求扩成全历史回放。
6. 次数/费用/旧操作终态纪律不变；未接worker/HTTP/模型，settle不能当生产停止证明。按实际diff确认list/recover/admit/mark/record未被顺手改写；仍分析claim/cancel变化对这些调用路径的影响，不能因函数文本未变就自动排除回归。
7. 测试准备是否真实调用仓储、专用DSN缺失明确skip、定向FK清理正确、投影覆盖断言字段、夹具修改仅必要参数/None检查。检查新增八例对关键分支覆盖，避免把未来运行卡浪费在已可静态定位的夹具错误。不会因此扩建mock/通用测试框架。
8. 必须输出“后续最小PG验证清单”：新增用例；004空库成功/非空拒绝及必要CHECK反例；既有用例按具体claim/cancel/夹具依赖选择。逐项给现有测试标识或缺口，不默认三个文件全跑，也不为了少测删除真实受影响行为。本卡不编写缺失用例。

边界：
只读上述文件及必要直接依赖；仅写Ndocu/evidence/task-078/、Ndocu/results/TASK-078-result.md。
禁止修改产品/测试/迁移/锁/正式docu/旧证据，不跑compile/unittest/PG/Docker/EXPLAIN/应用/模型，不联网安装、不读真实配置、不Git提交。
本批源码冻结，无并行写入；不占端口/数据库。达到覆盖即停，不做M-1/worker未实现部分的重复审计。

交付：
逐项标准、事实定位、问题严重度/触发/影响/最小修正；区分确定缺陷、条件风险、未验证。结论限定代码层通过/有条件通过/不通过/证据不足，不宣告动态通过。
记录读入hash/有限diff/读取范围和独立性；不直接修复发现。不把任何非阻塞观察自动升级为新硬门槛。
发现明确数据破坏/越权问题先留证回报；其余完成本范围一次审查。冻结对象不稳定则停止相关审查，带具体文件/hash交回。

回传TASK/R/STEP、独立性、范围快照、逐项结论/发现、最小PG清单、未验证与风险、文档建议、必要人工操作、下一步。
保存指定结果并回复完整可复制块，不填写Astra最终验收，不宣告时间监督或STEP008完成。



