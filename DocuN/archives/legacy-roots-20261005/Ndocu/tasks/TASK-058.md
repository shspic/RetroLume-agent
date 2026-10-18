# TASK-058：持久准入账本独立只读审计接续

你是本卡的独立执行 Agent，不接管项目编排。
任务：TASK-058；R-052；类型：独立审计；STEP-006/008局部；接续TASK-056，关联TASK-046/051/055。
需求/架构：SEC-002、NFR-002/003、DR-003、MOD-003/007/008、FLOW-005。
接收：Codex中的Sol，C档/高推理，必须使用未参与本实现的新会话。不能与TASK-057使用同一执行会话。
理由：预算、并发、权限和版本撤销需要强档独立判断，已有客观证据充分的部分不重测。
项目根：D:/shspic/project_NO3_RetroLume-agent。需求文档v1.1（目标v1.0）、架构v0.16。用户授权手动转交；状态待转交。

目标与已有材料：
判断当前capabilities、activities和002迁移这组有限基础是否满足原合同，给后续worker/业务接入的明确门槛。
056曾派发但截至接续检查没有结果文件，不能当审计通过；本卡保留其关系，不伪造旧结论。
001/002、gateway与ledger源码及051/055原始证据已存在。本卡不要阅读实现Agent的自评报告或完整聊天；自行从标准、源码和原始记录判断。

必要上下文（相对项目根）：
先读AGENTS.md、docu/AGENTS.MD、本卡；
docu/LATER_REQUIREMENTS.MD的上述需求，docu/PROJECT_ARCHITECTURE.MD的FLOW-005、DATA-004/007及安全边界；
原合同Ndocu/tasks/TASK-046.md、TASK-051.md、TASK-055.md、TASK-056.md；
backend/app/capabilities/、backend/app/activities/、backend/migrations/001_materials.sql与002_activities.sql；
backend/app/runtime.py、deploy/start_local.py、deploy/start-backend.ps1；
资料来源版本原子更新只按需要读backend/app/materials/repository.py。
检查对应测试源码及Ndocu/evidence/task-051/和task-055/内stdout、exit-code、环境、命令、hash、停止记录；046原始可用证据按项目内路径定位。证据缺失如实记录，不通过阅读自评补齐。
不用通读其余项目历史。若执行时出现新056结果，先核对日期/独立性及覆盖，报告可继承部分，不再无依据重复审计。

范围与资源：
核心被审源码和迁移只读；允许写Ndocu/results/TASK-058-result.md及必要Ndocu/evidence/task-058/。
禁止修改实现、测试、锁、正式docu或既有证据；禁止运行产品测试、Docker、应用、模型、安装和真实配置读取；不提交Git。
以少量相关hash/差异确认对象，无Git时不假造提交。TASK-057只改独立集成脚本，与本审计无写冲突；不读取其正在变动文件。

审计标准：
1. 来源UUID→活动→操作锁顺序；准入及发送边界均核对当前来源版本/revision、活动范围、执行者、代次、租约、期限。
2. 请求/工具/模型与保守费用限额有效，唯一operation不能二次发送；短事务不跨网络；失败回滚无半次预留。
3. 取消/失联/超时/旧代次不能被误记成业务成功；unknown不自动退款、不自动重发；结果幂等且不同终态不能覆盖。
4. gateway与ledger接口及异常处理吻合；默认拒绝账本、固定服务URL、工具白名单、总期限、无隐藏重试、敏感信息不进入日志。
5. 正式Windows启动loop与异步psycopg兼容；已有证据是否确实覆盖相应实现快照。不要把本地费用预留宣传为供应商账单硬上限。
6. 区分代码缺陷、已有有效证据、缺失证据、尚未实现的后续责任。worker监督/业务提交/真实模型/完整学习链/HTML不在当前有限验收范围，须列后续门槛，不能据此虚构本卡已覆盖。

交付与验收：
每项重要问题给准确文件/位置、触发条件、影响、证据和最小修正建议；证据缺口说明能否并入后续必要集成，不能泛化要求重跑全部套件。
给出有限范围的审计建议及独立性声明、被审快照、覆盖矩阵、未验证和后续门槛；即使无缺陷也说明依据，不宣告STEP-008或整个项目完成。

验证与停止：
只做一次只读代码/契约/原始证据一致性审计，不执行产品测试。覆盖充分即停；确需动态验证或改实现时只给精确补证/修复建议，交回Astra，不自行扩权或代修。

回传：
保存Ndocu/results/TASK-058-result.md，并回复一个完整可复制结果块：TASK/R、完成/部分/阻塞建议、独立性、读取范围/快照、发现及证据、未验证/风险、需求/架构偏差、文档建议、下一步。不得填写Astra最终验收结论。用户原样带回后由Astra裁定。
