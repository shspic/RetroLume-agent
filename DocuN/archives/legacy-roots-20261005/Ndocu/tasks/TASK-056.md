# TASK-056 持久准入账本独立代码与证据审计
类型独立审计；R-050；STEP-006/008局部；父TASK-046/051/055；SEC-002、NFR-002/003、DR-003、MOD-003/007/008、FLOW-005。执行Codex内部Sol强档，新隔离Session，不继承执行聊天/自评；高风险并发/预算/版本撤销需要独立判断。
根D:/shspic/project_NO3_RetroLume-agent；有效需求v1.1/架构v0.16；用户07/08原授权，仅只读审计，不模型调用/DB运行/安装/代码修复。
目标：判断当前冻结capabilities+activities/002的有限准入实现能否作为后续worker/业务接入基础；不是整个STEP008或生产审计。先读根AGENTS及docu/AGENTS.MD，再读LATER_REQUIREMENTS相关上述需求、架构FLOW-005原子准入/数据与安全边界；TASK-046、TASK-051、TASK-055原合同；capabilities所有源码、activities所有源码、002、001与资料原子版本更新相关代码（其他PDF仅按需要只读）。不要读执行Agent自评/结果报告或聊天；原始测试脚本/log/exit/environment/hash可读。
冻结与协作：055只改runtime/deploy和测试入口，不改账本/capabilities/002；先对核心代码只读审计，证据部分等待055完成后Astra提供原始路径，不读取正在写入日志。054独占集成脚本/合成环境，与本卡无资源共享。必要最终hash自行只读复算一次，不重跑测试。
验收标准：来源UUID→活动→操作锁序；准入/发送边界均核实current_version/revision/scope/executor/generation/lease/deadline；有限模型/工具/请求/保守费用，唯一operation不二次发送；短事务不跨网络；未知/取消/过期不可提交业务成功、unknown不退款不自动重试；结果幂等且事实不被覆盖；故障事务无半次预留；默认拒绝账本、固定模型URL和工具白名单/总deadline/错误脱敏。审查实际gateway与ledger契约是否一致，不把测试成功当充分证明。费用是本地保守额度机制，不声称供应商账单硬上限或已完成真实费用标定。
排除：真实模型效果、worker真实进程/崩溃监督/业务成功CAS/完整学习链/HTML；这些未实现必须列入后续门槛，不能把整项目未完成当当前有限基础必修缺陷。
允许只写Ndocu/results/TASK-056-result.md及Ndocu/evidence/task-056本卡必要只读审计证据。禁止改业务/正式docu/锁、触碰用户数据、Docker、测试调用或追加新要求。代码具体缺陷列路径/位置/触发条件/影响/最小修正；证据不足精确列缺口与下一次必要集成能否补齐，不泛化追加套件。
验证为一次只读审计/差异与证据一致性检查，不执行产品测试。完成覆盖即停；范围变化/需要动态证据回报Astra，不能自授运行或接受风险替代审计。返回候选通过/部分/阻塞与具体理由、当前快照、证据适用范围、未验证、独立性、后续门槛，不替Astra写最终共享结论。
