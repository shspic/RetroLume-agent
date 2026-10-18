# TASK-048 PostgreSQL持久准入与调用账本

类型开发；STEP-008局部；R-042；前置TASK-046入口契约已固化；NFR-002/003、SEC-002、DR-003、MOD-003/007/008、FLOW-005、DATA-004/007；后续worker/业务提交与独立审计仍需完成。
执行者：待派发Codex内部Sol强档；事务/并发/预算/版本撤销高风险，需要强档实现和真实PG反例。不是独立审计。
根D:/shspic/project_NO3_RetroLume-agent；有效需求v1.1、架构v0.14；用户已授权07/08内本地开发和必要局部验证，无新增付费API或生产操作。

## 目标与上下文
为ControlledModelGateway的AdmissionLedger提供真实PG实现，建立可持久活动/来源范围/有限调用预算与操作账本。默认拒绝实现不移除；只有显式配置完成的应用组合才能接入真实账本。本卡无真实模型请求。
先读AGENTS.md/docu规则、架构FLOW-005及其原子准入补充、DATA-004/007、TASK-046-result与最终capabilities/contracts.py、gateway.py；当前materials/repository.py及001_materials.sql只读。不复制旧SPIKE代码作为产品实现。

## 边界和协作
独占backend/app/activities/、backend/migrations/002_activities.sql、backend/tests/test_activity_ledger.py、tests/run_ledger_check.py及自身Ndocu/evidence/task-048与结果；不改main、materials、capabilities、前端、锁、用户配置或正式docu。契约必要变动先给Astra具体建议，不并行改046文件。047只pdf_import/锁，045只materials/前端，避免读取正在变动文件来测试。
迁移只新增计划中的表/约束，不重写001，不在已有用户库执行，不自动随应用启动迁移。凭据只用自建合成测试密码，不读真实配置。沿用现有psycopg，无新依赖。

## 关键不变量与验收
活动显式有限请求次数、累计费用上限、每请求保守预留、期限、允许模型/工具、来源快照；无正数有效限额拒绝创建可执行活动。费用用Decimal/整数最小单位，不用浮点；未知与已收到请求保守保留预留，不猜测成本或自动退款。额度不是用户旧13元实验余额。
按来源UUID排序→活动→操作的固定锁序：admit与mark_dispatch_started均核对来源current_version/revision、活动scope_revision、执行代次/执行者/租约、状态和期限、权限及限额。admit一次事务唯一操作键占用和预留；重复请求不得得到第二次发送资格。mark_dispatch_started一次性CAS，不自动重新授予；跨重启保留消费。活动cancel递增代次；来源替换已有FOR UPDATE冲突可复用，当前版为空/来源缺失视撤销，不改原资料写入逻辑。
record_outcome幂等，凭证/执行者绑定且不可变；重复同结果无重复计费，不同结果不能覆盖已终结事实。失联/截止/取消后的在途操作可记unknown/诊断，不得更新为业务成功；未知保留预留、不自动再发。记录返回模型/finish reason/有限用量与脱敏错误，不存密钥/输入正文。DB不可用失败关闭；连接/事务有上限，网络调用不持事务。
本卡不声称完整worker监督/取消远端/学习业务提交已实现。提供后续活动创建/领取租约/取消/恢复未知的窄领域方法及明确契约，保持当前架构的来源版本撤销能被准入检查。

## 有限真实测试子项
强档，目标新迁移/仓储，合成来源及模型响应，无真实资料/外网模型。现有镜像2026-09-14只读确认ID sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f，可使用但不下载/升级。允许一次专用测试容器retrolume-task-048-pg（若已存在先核对身份状态，不重建覆盖），只绑定127.0.0.1:55433、CPU1/512MiB/PID128/restart=no，无宿主挂载/真实配置。容器自有存储仅合成数据库，结束停止保留。端口被占或Docker不可用即报告，不杀占用者/不改其他容器。最长10分钟，独立监督持有唯一容器ID，异常也停止并确认；停止未知时中止后续操作，不删除任何数据。
使用本项目.venv对新测试库执行001+002，真实psycopg测试至多8类：合法一次准入/重复并发只一个资格/限额拒绝/源版本撤销/取消或过期代次拒绝/unknown跨新连接恢复且预算不返还/幂等结果冲突/事务失败无半次预留。每类一次，原始stdout/退出码/环境/命令/最终hash落盘。只因明确修正重跑受影响项，两次仍失败停止升级。不能将SQL静态或内存mock当真实PG行为。

## 返回和完成边界
Ndocu/results/TASK-048-result.md：结果候选、文件与设计不变量、命令/证据、真实DB范围、未测崩溃/监督/业务集成、必要独立审计、关闭自有资源结果、文档建议。不把局部账本通过写成整个008完成，不触发费用，不开始下一业务任务。
