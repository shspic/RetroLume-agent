# TASK-046 结果：受控模型与工具入口

状态：卡内实现及有限离线验证完成，候选交回 Astra；不是独立安全审计或产品最终验收。

## 已实现

- `backend/app/capabilities/` 提供一个稳定的 `ControlledModelGateway.call(context, request)` 异步入口。配置明确区分 provider、固定允许的 base URL、model、thinking、超时、输出 token、请求体和响应体上限；密钥用 `SecretStr` 保存且不进入 repr、账本事实或错误结果。
- 当前仅实现 DeepSeek Chat Completions 非流式适配。httpx transport 关闭环境代理和重定向，不配置重试；除分项 IO 超时外，网关以单调总期限覆盖完整发送及响应读取，持续小块响应不能无限延长期限。连接建立前可确定失败记 `not_sent`；开始出站后的总期限、超时、断线、取消及其他不明 transport 状态记 `unknown`，不自动重发。
- 只有持久账本依次完成 `admit` 和 `mark_dispatch_started` 才能进入 transport。默认 `RejectingAdmissionLedger` 失败关闭；没有布尔“已批准”参数，也没有内存预算替身。收到结果后必须成功 `record_outcome` 才向调用方返回成功；记账失败返回 `unknown`。
- 响应严格检查单一 choice、返回 model、非负 usage、finish reason、空白、截断、非法结构/JSON、非有限 JSON、递归深度异常、响应大小和工具调用。可见调用事实只含 ID、模型、finish reason、token、字节数和错误分类，不含提示词、回答正文、密钥或远端错误正文。
- 工具目录只有 `finite_calculate`，字段关闭扩展，输入绝对值、幂指数、参数字节数、结果绝对值和 Decimal 精度均有限；没有 eval/exec/shell、文件或网络能力。模型工具建议只返回校验后的 `ToolCallPlan`，不自动执行；应用显式执行后可用受控 `assistant.tool_calls` 与配对 `tool` 结果发起下一请求。Schema 通过只表示结构和授权有效，不表示模型建议在业务语义上正确。

## STEP-008 最小持久账本接入契约

`AdmissionLedger` 保持三个异步方法，不要求 TASK-046 内造数据库抽象：

| 方法 | 必须持久检查或写入的字段与语义 |
| --- | --- |
| `admit(intent) -> AdmissionPermit` | 在一个短事务中以 `activity_id`、`operation_id`、`executor_id` 定位持久操作；检查 `execution_generation`、`scope_revision`、活动取消/租约、操作唯一且未消费、持久范围快照及来源代次、provider/model 权限、`request_bytes`、`max_output_tokens`、`tool_names` 与全部剩余额度；唯一预留次数/费用/时间资格。返回的 `admission_id` 必须绑定相同 `operation_id` 和 `executor_id`，且一次性。来源版本明细应由 operation 的持久范围快照取得，不相信调用方临时声明。 |
| `mark_dispatch_started(permit)` | 在网络调用前持久化不可逆出站边界；再次核对 admission/operation/executor 绑定、资格尚未消费、执行代次/租约/取消仍有效。失败或状态冲突必须拒绝网络；成功后崩溃要由恢复流程保守视为可能已发送。 |
| `record_outcome(permit, outcome)` | 幂等记录同一 admission 的终态，禁止第二结果覆盖。`RECEIVED` 保存脱敏响应事实与实际 usage（非法响应也可能已计费）；`UNKNOWN` 保留全部预留且禁止自动重试/重新领取；`NOT_SENT` 仅表示 transport 能确定连接建立前失败，**不代表网关有权自动退款或释放预留**，由 STEP-008 在事务中按正式账本政策决定，保守默认仍保留到对账。 |

如 `record_outcome` 本身失败，入口只返回 `ledger_record_failed/unknown`；持久记录会停在 dispatch-started，恢复监督必须先对账，不能据调用方收到的结果重发。

## 验证与限制

原完整局部测试 12 项通过；工具往返修正后两个受影响测试通过；总期限与递归解析修正后的四个受影响测试通过，遵照停止条件未重复完整旧组。命令、环境、修正记录与最终源码哈希见 `Ndocu/evidence/task-046/verification.md`；官方协议字段与来源见 `Ndocu/evidence/task-046/protocol-source.md`。

没有真实模型调用、费用、外部数据发送、数据库、Docker、新依赖、入口/API、配置或锁文件修改。尚未验证具体 DeepSeek 模型/账号兼容、真实超时边界、供应商数据条款、费用估算，以及 PostgreSQL 的并发准入/崩溃恢复/取消竞争。SEC-001/002 和 NFR-003 只能在 STEP-008 持久账本集成、真实获准服务小样及独立审计后关闭。
