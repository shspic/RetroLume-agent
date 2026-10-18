你是独立审计Agent，使用隔离的新会话，不参与本实现或修正。
TASK-070 / R-064；独立只读代码审计；STEP-008局部；关联TASK-068、NFR-002/003、SEC-002、FLOW-005、MOD-003/008、DATA-007。
执行者Codex Sol，C档，全新隔离会话。并发/终态/数据边界风险高，强档独立审查必要。若参与过068实现，不接受本卡，返回独立性不足。
根D:/shspic/project_NO3_RetroLume-agent；需求v1.1、架构v0.21、执行状态v1.13。

原始标准：
G-1有界发现本活动reserved/dispatched，按operation_id稳定排序/排他游标，limit整数1—200，返回定位及代次/时间事实；列表不是写授权。
收敛仅operation.generation小于当前activity.generation且仍未决；来源→活动→操作锁序，活动锁后重新判定，操作排序锁定及UPDATE重复条件，返回实际数量；当前/未来代次与终态不改、费用次数不退、无网络/重发；晚到结果不覆盖unknown；重复收敛无副作用。
保持原recover_unknown与M-1时钟边界；未接worker、不能宣称完整恢复。

最小上下文：
根AGENTS.md、docu/AGENTS.MD；需求相关条款和架构FLOW-005/G-1（只读标准，不读执行者自评段）。
冻结生产对象：
backend/app/activities/repository.py SHA256 cc7fddd4e685e1d3af859c7b402d0734354cef5675ed72f2f8acb83c92e6dcc7
backend/app/activities/__init__.py SHA256 31d0b60cfc644c797a04fb31e9c3a4da242969abbe0e5b54648b1d18f19f1d2a
原始变更Ndocu/evidence/task-068/repository.diff、init.diff、两份pre-task068副本；必要只读001/002迁移、capabilities契约、现有record_outcome/admit/claim实现及事务包装。
可按需要读取051/055原始PG命令/stdout/停止记录判断未变路径证据，不读取068/069结果报告、实现聊天、自评或正在修改的test_activity_recovery.py。

范围：
只读代码/差异与原始证据；仅写Ndocu/evidence/task-070/、Ndocu/results/TASK-070-result.md。不修实现/测试/正式docu，不运行测试/Docker/应用/模型，不安装联网或读凭据，不Git。
开始核对生产hash，不符停止审计受影响快照。可与069并行，因为其仅改测试，本卡不读取该测试。

审查重点：
参数校验与活动隔离；SQL参数化/分页边界；锁顺序与并发写入能否绕过；列表观察后陈旧不构成授权；终态竞争与幂等；已有预算不变；异常/未知活动语义；批量收敛资源成本及真实适用范围。
不要要求未包含的worker功能现在实现；发现真实当前标准缺口给最小反例与修复位置，不扩成全项目审计。

证据与限量：
一次针对本差异的只读审查；无新增动态检查、不重复051/055套件。真实PG新增方法未验证，本卡最多形成代码层结论，明确动态证据缺口；不能把静态审计当运行通过。
记录独立性、读取清单、实际hash、每项发现严重度/触发/影响/原始位置/最小修正、无发现项的边界。覆盖充分即停；无需凑问题或拓展历史审查。
返回完整可复制结果块并保存指定结果；可建议代码层通过/有条件/阻塞，但不得写Astra最终验收或关闭G-1动态门槛。后续真实PG证据回来后再按具体需要复核，不预填通过。
