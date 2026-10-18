# TASK-051 结果：PostgreSQL 持久准入与调用账本接续

状态：局部实现候选已形成，真实 PostgreSQL 验证未闭合，交回 Astra。不能登记为 TASK-051 完成、STEP-008 完成或独立审计通过。

父任务映射：本卡接续额度中断且无结果的 `TASK-048`，当前登记为 `TASK-051 / R-045`；没有沿用旧调用额度或虚构旧验证。

## 候选文件

- `backend/app/activities/repository.py`：既有接续代码经审查保留，提供 `create_activity`、`claim_lease`、`cancel_activity`、`recover_unknown` 及 `AdmissionLedger` 三方法的真实 PostgreSQL 实现。
- `backend/app/activities/__init__.py`：导出活动、租约、来源快照和账本类型。
- `backend/migrations/002_activities.sql`：新增活动、来源范围快照、允许模型和操作账表及约束；没有修改 001，也没有应用到已有用户库或应用启动流程。
- `backend/tests/test_activity_ledger.py`：8 类真实 PostgreSQL 合成反例；本次只修正了清理夹具的外键顺序。
- `tests/run_ledger_check.py`：专用迁移/检查入口；修正无包目录的测试发现及 Windows psycopg 事件循环兼容。
- `Ndocu/evidence/task-051/`：原始 stdout、退出码、脱敏命令、环境、容器身份/关闭状态和最终源码 hash。

本次没有重写父任务已经正确留下的仓储和迁移主体，也没有新增或升级依赖。

## 设计不变量

- 可执行活动必须显式提供未来期限、正数请求/费用/单次预留/请求字节/输出 token 上限、至少一个允许模型、有限工具集合和至少一个来源版本快照；费用使用整数 microunit，不使用浮点。
- 准入按来源 UUID 排序锁来源，再锁活动和操作；核对来源当前版本与 revision、活动 scope revision、执行代次、执行者、租约、状态、期限、模型、工具及额度。
- `admit` 在一个短事务中以唯一操作键预留请求次数和保守费用；重复操作不能得到第二发送资格。网络调用不在事务内。
- `mark_dispatch_started` 只允许 `reserved -> dispatched` 一次，并重新核对来源、活动、代次、执行者和租约。
- 取消活动递增执行代次并清除租约；来源丢失、当前版本为空或 revision 不匹配会使新准入和发送边界失败关闭。
- `record_outcome` 绑定 admission、operation 和 executor；同一终态可幂等重放，不同终态不能覆盖。失效活动只能登记 unknown；unknown 和 not_sent 都不自动返还预留。
- 账本只保存有限 token/字节用量、返回模型、finish reason、远端请求 ID 和脱敏错误码，不保存密钥或输入正文。
- 数据库/驱动错误对准入表现为 unavailable；连接、语句、锁和空闲事务均有上限。

## 验证结论

指定专用合成 PostgreSQL 容器已经创建，001 与 002 已在新库成功应用。最后一次卡内运行中，第 1 类“合法准入/发送/收到结果”真实通过；第 2 至 8 类因测试清理夹具违反 001 的当前版本外键而没有执行。夹具已经修正，但根据卡内连续修正失败停止条件没有继续启动数据库，因此不得把剩余 7 类写成通过。

详细记录见 `Ndocu/evidence/task-051/verification.md`。所有进程退出码和原始 stdout 已落盘；最终专用容器 `retrolume-task-048-pg` 状态为 `exited`、`running=false`，停止保留。没有真实模型请求、费用、真实资料、真实配置或用户数据库操作。

## 未闭合项和建议

- 需要新的受限验证/审计卡，从已修正夹具开始，仅补第 2 至 8 类真实 PostgreSQL 证据；不得沿用本卡未通过结论。
- 当前 Windows 单进程 Uvicorn 默认 Proactor，与异步 psycopg 不兼容。正式应用组合接入真实账本前，应由 Astra 在部署/应用集成范围明确 Selector 兼容启动方式并验证；本卡没有修改越界的部署文件。
- 进程崩溃、监督器失联、worker 实际终止、取消远端、业务成功提交与业务幂等均未测试或实现，仍属于后续 STEP-008/worker/业务任务。
- SEC-002、NFR-002/003、FLOW-005 和整个 STEP-008 仍需补齐真实并发/事务证据及隔离的独立强模型审计。
- 建议 Astra 保持 STEP-008 为“进行中 / 未验证”，并为本批 Ndocu 结果/证据补记 `docu/CHANGE.MD`；执行者遵守任务卡“不改正式 docu”的边界，未直接更新正式状态或变更账。
