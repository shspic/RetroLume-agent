# TASK-046 官方协议核对

核对日期：2026-09-13；来源仅用于实现协议适配，没有发出 API 请求。

- DeepSeek 官方 [Chat Completions API](https://api-docs.deepseek.com/api/create-chat-completion/)：`POST /chat/completions`；请求的 `messages`、`model`、`max_tokens`、`thinking`、`response_format`、`tools`/`tool_choice`；响应的 `model`、`choices[].finish_reason`、`message.content`/`message.tool_calls` 与 `usage`。官方说明 `finish_reason=length` 可能得到截断内容，JSON Output 也可能产生空白结果，因此本实现都明确拒绝为可用回答。
- DeepSeek 官方 [Error Codes](https://api-docs.deepseek.com/quick_start/error_codes/)：400/401/402/422/429/500/503。实现记录脱敏 HTTP 分类，不回显远端正文，也不按官方“稍后重试”建议自动重试；是否形成新操作由上层持久预算重新准入。
- DeepSeek 官方 [Rate Limit & Isolation](https://api-docs.deepseek.com/quick_start/rate_limit/)：请求从发送至响应完成占用连接，并可能返回 429。当前实现不采用官方账户并发数作为产品预算，也不把服务端限速替代本地持久准入。

当前明确支持的服务类型只有 `deepseek_chat_completions`，base URL 固定允许 `https://api.deepseek.com`，不接受用户提供任意 URL。模型 ID 是服务端配置项，未对白名单中的任何具体模型做真实兼容验证；官方页面内容和可用模型会变化，正式使用前仍须核实账号、模型、价格和数据条款。

