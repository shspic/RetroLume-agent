# review-01 操作与口径说明

本轮仅创建本目录内的标准库文件解析、hash、有限 diff 和算术工具。首轮审计 helper 只读其必要逻辑，未执行，未写旧证据。

元数据工具曾按单 JSON、独立 batch_start 事件、Docker 原始 SecurityOpt 列表假设解析，但原件实际为 JSONL、reserved 后的 batch 计时、产品归一化 SecurityOpt 字典。按原件与实际 batch 源修正审计工具后重算通过；解析错误和失败判据未当产品失败，业务运行始终为零。

五份保存的 source diff 用 CRLF，独立重算用 LF：原字节 diff 不相等而统一 CRLF 后全文相等，pre/post 本体 hash 均符合冻结身份。未为统一换行修改产品或工程证据。

registry 的加密控制字段没有解密、使用或复制到交付正文；只据公开身份、时刻、准确进程实例及 Job 前提核对。所有引用的命令原件只读取与解析，未执行其中 shell、Docker、Node、SQL 或产品调用。

metadata 初段有工程实现混分，accepted_utc 与扣 300 秒后的 accepted_ns 不冒作同一次精确采样；真实根的 elapsed 先采样，再保存 budget 和 batch_end 事件，事件落盘时戳不能替代 elapsed 终点。real phase 比资源 batch 多 0.234 秒是前后阶段外围，不再补入资源账。
