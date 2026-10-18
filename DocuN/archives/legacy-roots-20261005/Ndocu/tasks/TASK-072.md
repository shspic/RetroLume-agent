你是本卡的独立审计 Agent。完成后输出供用户带回 Astra 的结果包，不接管编排。
TASK-072 / R-066；类型：独立只读差异审计；STEP-008局部；父TASK-071，关联068/069/070、NFR-002/003、SEC-002、FLOW-005、DATA-007。
执行者：Codex Sol，C档强档，必须全新隔离会话，未参与071实现。涉及事务锁定集合、终态保护及数据改写，需强档；仅审新增差异，不重审整个账本。
项目根：D:/shspic/project_NO3_RetroLume-agent。
基线：需求文档v1.1、架构v0.23、执行状态v1.15；沿用已授权开发及必需独立审计范围。

目标与现状：
068已实现旧代次未决操作发现/收敛，070已有代码层审计；071将无界收敛改为默认100、最大200条的单批事务。此次只判断该差异是否保留锁序、精确更新集合和终态纪律，以及新增测试是否能观察批次边界。
真实PG尚未运行；本卡不运行、不以语法证据判动态通过。不要求证明M-1/worker/性能已经解决。

上下文与独立性：
先读根AGENTS.md、docu/AGENTS.MD。
标准仅按需读取docu/LATER_REQUIREMENTS.MD的NFR-002/003、SEC-002；docu/PROJECT_ARCHITECTURE.MD的FLOW-005和内部恢复信任边界，跳过执行者评价及Work验收段。
读Ndocu/tasks/TASK-071.md原合同。
直接比对Ndocu/evidence/task-071/repository.py.pre-task071与backend/app/activities/repository.py；必要时读_source_rows、_lock_sources、_transaction、record_outcome及001/002迁移，定位差异的上下文。
直接比对Ndocu/evidence/task-071/test_activity_recovery.py.pre-task071与backend/tests/test_activity_recovery.py，重点test_06及清理边界，不重审五组未改断言。
不读取071结果、自评、执行聊天、make-diffs-run或其推理说明；不得继承实现会话。无需加载整个历史审计报告。若误接触自评，披露内容和对独立性的影响，不隐瞒。
原始输入hash：
repository pre cc7fddd4e685e1d3af859c7b402d0734354cef5675ed72f2f8acb83c92e6dcc7
repository current 50ec537b07533c68194651b008d275176430effeb67126391ef43b96155cfce6
test pre 7bf924cded794b94bdc213d255177253af2b3948ad844f302d7bd987ae6804f4
test current ef705113fbf6af83a0a29e99b40dfdb68109282c0ae8b724790e1d440575d246
hash不符先报告差异，不能审旧快照后宣称适用新文件。

允许与禁止：
只读相关源码、迁移、原始差异；仅写Ndocu/evidence/task-072/和Ndocu/results/TASK-072-result.md。
不改实现/测试/迁移/依赖/正式docu/旧证据；不跑compile、unittest、Docker、PG、EXPLAIN、应用、模型；不安装、联网、读真实配置或凭据；不做Git提交。
生产与测试文件本卡期间冻结。无端口/数据库占用；没有并行修改任务。本卡完成后由Astra安排真实PG运行。

审计标准：
1. limit须在事务前拒绝bool、非整数及1—200以外值；默认100、返回本批实际改动数；无内部循环或隐式重试。
2. 来源→活动→操作锁序保持；活动锁后取当前代次；候选严格限本活动、reserved/dispatched、旧代次并排序/LIMIT。
3. UPDATE只用实际加锁取得的ID集合，同时重判活动/状态/旧代次；空集合不更新；不得重新宽更新或另选候选集合。
4. 当前/未来代次和既有终态不改；费用/次数预留不退、不发送。旧permit仍可能提交UNKNOWN，检查其与本批更新的锁/终态竞争，不能仅凭代次不同假定互斥。
5. 新test_06能观察2/2/1/0、逐批未选项保持、当前代次/预算/终态字段及非法limit；原定向外键清理保留，未把无DSN的skip当成功。实际六个test方法，基类不计用例。
6. limit不保证扫描/排序输入或耗时有界；不把源码注释中的执行计划形状当已取得EXPLAIN证据。返回0/<limit不是活动永久无未决项证明。列出真正需要真实PG确认的适配/行为，不能因尚无动态证据要求再造模拟器。
7. 内部调用方仍须有活动写权限；本卡不扩展列表投影、HTTP权限、worker、时钟、持久预算或索引。未变门槛保持，不用这些已知未完成项重复否决本次局部代码。

交付和足够性：
输出每项标准的源码/差异定位、成立或缺口、影响及最小建议；问题区分确定缺陷、条件风险、未验证，不能把推断写成事故。
限定结论可为代码层通过/有条件通过/不通过/证据不足，明确不是G-1或STEP完成。
保存读取范围、输入hash、独立性声明及必要原始摘录；只作一次差异审查，覆盖充分即停。不重复070的整仓审计，不增加性能或动态任务。

停止与升级：
发现会导致越权/误改终态/不限定集合的明确问题时留证交回，不自行修复；缺必要文件/快照漂移则报告具体缺口。其余已知M-1、worker和PG未运行只作为适用边界，不扩卡。

回传：
TASK/R/STEP、建议结论、独立性、读取快照、逐项标准与证据、发现及严重度、未验证/限制、需求架构影响、待同步文档、必须人工操作和下一步。
保存Ndocu/results/TASK-072-result.md并回复完整可复制结果块；不填写Astra最终验收，不宣告STEP/项目完成。
