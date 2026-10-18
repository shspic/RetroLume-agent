你是执行Agent，完成后把结果交用户带回Astra，不接管编排。
TASK-068 / R-062；开发；STEP-008局部；父TASK-060，关联058/051/055/062、NFR-002/003、SEC-002、FLOW-005、MOD-003/008、DATA-007；目标G-1旧代次未决操作发现与收敛。
执行者：Codex Sol，C档，新会话。涉及事务、执行代次和终态竞争，采用强档；本卡不是独立审计。
项目根D:/shspic/project_NO3_RetroLume-agent；需求文档v1.1、架构v0.20、执行状态v1.12。沿已有STEP008开发授权，无真实模型费用。

目标/背景：
活动账本已有准入、发送、结果记账及051/055合成PG证据；062修复ID契约与脱敏错误。旧代次reserved/dispatched操作无发现入口，重新领租约后现recover_unknown因当前有效租约而拒绝整批恢复。
本卡只实现G-1：有界发现未决项，并在事务内只把比当前活动执行代次更旧的未决项置unknown。不得伤及当前代次，不退款、不重发。
M-1墙钟/单调监督/跨重启预算尚未解决；本卡的旧代次判据不用时间，不宣称解决时钟或完整worker恢复。

上下文：
先读根AGENTS.md、docu/AGENTS.MD、Ndocu/TASK_TEMPLATE.md及执行状态当前入口；
架构FLOW-005及G-1记录；backend/app/activities/repository.py、__init__.py、backend/migrations/002_activities.sql；
backend/app/capabilities/contracts.py、backend/tests/test_activity_ledger.py；
Ndocu/results/TASK-060-result.md的G-1与058终态边界、051/055必要原始证据。060时钟方案已被Astra否决，不照抄now修复。
不通读全部项目、不重做已有账本模块。

允许写：
backend/app/activities/repository.py、必要的__init__.py；
backend/tests/test_activity_recovery.py（本卡新增，使用现有unittest/psycopg设施）；
Ndocu/evidence/task-068/、Ndocu/results/TASK-068-result.md。
允许只读现有调用/测试/迁移以核对契约。禁止修改DDL、原test_activity_ledger.py、gateway、运行启动器、锁/依赖、正式docu、旧证据、用户数据和Git。
不启动Docker/数据库/应用、不联网、不安装、不读取真实配置/凭据、不调用模型。

实现约束：
1. 增加内部仓储list_unresolved_operations(activity_id, *, limit=100, after_operation_id=None)：仅返回本活动reserved/dispatched；按operation_id稳定升序、排他游标，limit整数1—200，非法值明确拒绝。返回operation_id/admission_id/executor_id/execution_generation/scope_revision/reserved_at/dispatch_started_at，保留现有类型约定。现有部分索引可复用，不加索引/字段。列表只是观察，不是后续写授权。
2. 增加内部仓储recover_obsolete_operations(activity_id, *, error_code="executor_lost") -> int：保留现有来源→活动→操作锁序；锁住活动后以其当前generation重判；只改operation.execution_generation < activity.execution_generation且state为reserved/dispatched的操作。按operation_id锁定，更新条件仍重复代次及状态保护，返回实际改动数。未知活动、非法ID/error_code沿现有异常语义。
3. 更新为unknown/disposition unknown、recorded_at及受限error_code，保留准入/发送事实。当前代次、未来异常代次和已有received/not_sent/unknown绝不覆盖；重复调用返回0。计数和费用预留不减少，无发送或重新调度副作用。
4. 不修改现有recover_unknown的取消/租约/时钟语义。新方法仅旧代次路径，后续监督器负责“新代次建立→旧项收敛→新动作”；本卡不接worker或自动调用。
5. 与旧permit结果记账竞争时以数据库锁和终态纪律为准：先成终态者保留；晚到操作不得把unknown改为received，不放宽原结果幂等规则。相同unknown但元数据不同不能凭“都是unknown”宣称幂等成功。
6. 保持短事务，不在事务内网络调用。不引入通用恢复框架或新时钟服务，不顺手改M-1。

交付与验收方向：
真实查询实现而非空方法；当前代次持有效租约仍可发现/收敛旧代次，当前代次操作不变；列表有界且游标不串活动；终态与费用不变。
新增后续PG用例覆盖：旧reserved/dispatched+当前未决混合；重复收敛；既有终态保留及预留不退；跨活动隔离/分页；旧permit晚到不能覆盖unknown。测试应调用实际仓储而非复制SQL或用mock冒充事务。
测试文件必须默认无专用测试DSN就skip，不能回退用户DSN；准备/清理只按每例新建合成活动/来源ID定向操作，不沿用旧测试全表DELETE夹具。专用真实PG执行由后续运行卡授权，本卡不运行它。

本卡验证子项：
C档只做改动差异、契约、锁序及测试代码一致性核对；使用现有Python对修改/新增文件做一次不写pyc的语法编译检查（读取源码后compile），最多60秒。保存原始命令/结果及新旧hash。
不跑整组旧测试、不运行数据库、不扩建模拟器。明确“实现候选/真实PG未验证”，不能因静态通过宣告G-1全部关闭。
无法在上述无schema变更边界完成则停止相关部分，给出具体冲突与最小替代；不猜测扩大接口或数据模型。

协作/审计/返回：
独占上述文件，其他账本修改必须串行。后续真实PG证据与所需独立审计由Astra另卡，不以本卡自查替代。
保存结果文件并给完整可复制结果块：TASK/R/STEP、建议状态、实际变更及接口、锁序/终态说明、准确命令与证据/hash、未运行PG用例、风险和M-1限制、文档建议、必须人工操作、下一步。不填Astra验收，不宣告STEP008完成。
