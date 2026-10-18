# review-07 独立产品初判（读取测试与日志前）

身份：当前 084 独立审计窗口，未参与 083 实现；仅对冻结源码和 083 `pre/` 副本作静态只读判断。九个指定文件本地 SHA-256 与任务冻结表一致（另见 `hashes.txt`）。083 包内未找到所称 `incremental.diff`，故本窗口由真实 `pre/` 副本与当前源码生成有限 `product-pre-current.diff`。尚未读取 D3 测试、runner、动态日志或 083 自评。

1. 006 单列 `running_owner_session_id BIGINT DEFAULT NULL` 加 DWORD 约束。claim 在来源→活动行锁事务内校验旧 G/SID，折叠 R 并写新 G/SID；结算、取消、折叠耗尽清 SID。旧 `NULL`、他会话 ID 均不能由产品 SUP 恢复。低层 `claim_lease` 可传 NULL 是合成兼容边界，不能单独当生产恢复入口。
2. SUP 自身读取 SessionId，活动互斥覆盖 inspect→旧 Job 核查/终止→claim→结果。仅显式 `single_host_single_session_recovery=True` 的 running 分支可接续；旧 SID 相同、来源有效、租约到期、deadline 未过才 Open 确切 `Local` Job。只把 `OpenJobObjectW` 错误 2 候选当不存在，其他错误失败关闭；存在时 terminate→ActiveProcesses==0→close；随后 claim 再查 G/SID/租约。该路径按单主机单会话且无外部绕行的受限部署前提，静态上实现保守整树核查；当前未获得运行证据。
3. 确定代码缺陷候选：repository.py:369-413 和 :447-449 将新时钟改成 PG `CURRENT_TIMESTAMP`。它是事务起点时间，事务在 `_source_rows`/来源行锁/活动行锁等待后仍为旧值。若事务在 deadline 前开始而来源锁等待跨过 deadline，`claim_lease` 的 :380 检查仍可通过，:413 写入已过期 `lease_expires_at` 并返回新 lease；SUP 可继续建 Job/Resume。须将过期判定和 lease 计算基于取得锁后的数据库实时时钟，并针对锁等待跨截止设定定向 PG 证据。`inspect_window` 也可给出陈旧的可恢复判断；claim 最终须兜底。
4. 待合同判断的条件风险：运行配置只携带布尔部署声明，没有代码内跨主机/跨会话物理证明（session.py:177）；用户批准的受信部署配置若是外部操作前提则可接受，但需由编排验证部署约束且不能把 numeric SID 当跨主机身份。pending 快照到 claim 不带预期 G/状态；同会话活动互斥可排除本切片 SUP 竞态，跨会话或其他不守互斥的低层调用是否在允许部署内尚需核调用边界。此点暂不下确定缺陷结论。
5. `NamedJob` 的同名碰撞拒绝、无继承进程句柄、Job kill-on-close、ActiveProcesses 查询及 SUP 外层未知结果保守字段属于未变链；本轮只对 D3 传播重新核对。是否具备动态运行门需后续审测试/runner及原始日志。
