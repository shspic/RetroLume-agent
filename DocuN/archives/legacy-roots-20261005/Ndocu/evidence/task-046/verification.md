# TASK-046 离线验证证据

时间：2026-09-14 04:39:39 +08:00（最终源码哈希取证时间）  
范围：仅 `backend/tests/test_capabilities.py`；合成响应与注入 transport；无网络、无真实模型、无数据库、无费用。

## 环境

```text
Python 3.12.10 (MSC v.1943 64 bit AMD64)
httpx=0.28.1
pydantic=2.13.5
```

TASK-046 首次完整最终通过时使用上述既有虚拟环境及原锁中的 httpx/Pydantic。并行 TASK-047 后续追加的 pypdf 与本模块、测试及结论无关。

## 完整局部测试

命令（工作目录 `D:/shspic/project_NO3_RetroLume-agent/backend`）：

```text
.venv/Scripts/python.exe -m unittest -v tests.test_capabilities
```

最终结果：12 个测试，`Ran 12 tests in 0.339s`，`OK`。

覆盖：默认无持久账本拒绝；固定服务 URL 与密钥隐藏；结构化成功；空白、截断、非法 JSON、非有限 JSON；无准入/准入记录失败；明确未发送与发送状态不明；取消记 unknown 后继续传播；HTTP 失败与过大响应；未知/越权/非法字段工具；有限计算正常与资源边界；请求上下文和输出 token 上限；无自动重试。

开发中出现并已纠正的两项局部问题：第一次失败来自测试把“结果过大”错误地放在计划校验阶段，改为在显式执行阶段检查；随后发现 Decimal 在离开 50 位局部上下文后 `normalize` 回落到默认 28 位，已把格式化移入同一上下文。修正后的完整局部测试通过。

## 工具往返定向验证

父级复核指出原 `Message` 无法表达合法 `assistant.tool_calls`，会使工具结果成为孤立 `tool` 消息。补充精确协议结构、调用 ID/权限/参数/配对顺序校验后，只运行受影响的两个既有测试：

```text
.venv/Scripts/python.exe -m unittest -v tests.test_capabilities.CapabilitiesTests.test_tool_suggestion_is_validated_and_only_returns_plan tests.test_capabilities.CapabilitiesTests.test_unknown_unauthorized_and_extra_tool_fields_are_rejected
```

结果：2 个测试，`Ran 2 tests in 0.174s`，`OK`。验证模型建议先成为计划，应用显式执行有限计算，再以配对的 `assistant.tool_calls` + `tool_call_id` 发起下一次受控请求；孤立工具结果在准入及网络前拒绝。

## 总期限与递归解析定向验证

后续复核发现 httpx 的分项 IO 空闲超时不能限制持续小块响应的总耗时。网关增加覆盖完整 transport 发送及读取的 `asyncio.timeout` 总期限；期限发生在出站边界之后，结果为 `deadline_exceeded/unknown`。同时将响应及工具参数解析的 `RecursionError` 转为明确失败，保证已收到响应仍完成 `RECEIVED` 记账。

命令（只运行直接受影响的 4 项，未重复完整旧组）：

```text
.venv/Scripts/python.exe -m unittest -v tests.test_capabilities.CapabilitiesTests.test_absolute_deadline_stops_continuous_slow_stream_as_unknown tests.test_capabilities.CapabilitiesTests.test_cancellation_is_recorded_unknown_then_propagated tests.test_capabilities.CapabilitiesTests.test_blank_truncated_and_invalid_json_are_rejected_as_received tests.test_capabilities.CapabilitiesTests.test_unknown_unauthorized_and_extra_tool_fields_are_rejected
```

最终结果：4 个测试，`Ran 4 tests in 0.116s`，`OK`。慢 transport 每 5ms 持续产生活动但不完成，30ms 总期限仍停止且仅调用一次；显式外部取消继续向上传播并记 unknown；响应解析递归异常记 `invalid_response_json/RECEIVED`；工具参数递归异常转为 `ToolValidationError`。

第一次定向运行中，人工构造的 1000 层 JSON 在当前解析器上没有触发递归异常，而是在解码后按顶层结构得到安全的 `invalid_response_shape`，导致测试对错误码的断言失败。改为定向注入解析器 `RecursionError` 后验证了目标分支；这不是产品逃逸或漏记账证据。

## 最终源码 SHA-256

```text
backend/app/capabilities/__init__.py 9E38CF8897C0B14A25203E4F9B88D93799F1F12A52C059B1471CABEC332857EE
backend/app/capabilities/contracts.py 43B6BD2B9DDFF196A1D39CBC92E13ACD00836ED1263CED119AB94228FE906C84
backend/app/capabilities/gateway.py C7778589251BD140D5186F8D997A66E9226781073C40544AD2114D7B3A60531A
backend/app/capabilities/tools.py BB94408FC68B31B35BFB423C618D82C2B4FC3971C559C03948D4D70A4CEA5838
backend/app/capabilities/transport.py 1D80347E2E41434297DAFEDFC7123CFDAFDB661F576672290108DE191E55B656
backend/tests/test_capabilities.py 4B2DF693C30E598A5AE9A0154184CF9B4ACEB368E07CC494961EBF4F792C6717
```

以上哈希在定向验证完成且解释器缓存清理后计算。证据与结果文档不包含在源码冻结集合中。
