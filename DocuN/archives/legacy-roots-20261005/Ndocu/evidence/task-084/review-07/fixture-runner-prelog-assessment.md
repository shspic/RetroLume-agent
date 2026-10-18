# review-07 夹具/runner 初判（读取原始日志与 083 自评前）

已读：`test_d3_recovery.py`、`test_worker_session.py`、`offline_unit.py`、`d3_pg_windows.py` 当前完整可达测试流（不读取运行时 DSN）；`runner_replacement.py` 非凭据行、first/replacement as-run 哈希及非凭据资源/控制流；001/002/004/005 必要约束。凭据相关 runner 源码行未输出；不读容器 Env、真实配置。更早一次宽泛 grep 请求被自动批准审查拒绝（可能输出密码/DSN），此后仅用非凭据内容继续。

1. 定向纯单元覆盖同/异/NULL、Open 2/5/87、旧树零、claim 丢响应，均为替身，不能证明 PG/Windows。`offline_unit.test_05` 的局部确定性时钟仍有可追算的 +0.4s 与 C1；当前改动仅增强 D3 适配，无动态结论。
2. PG 夹具 `make_schema` 每个 case 新随机 schema，001—005/006 顺序明确、scoped `search_path` 传给仓储和行查询；006 空/旧行/失败回滚路径结构成立。**确定下一故障**：`d3_pg_windows.py:150` 旧 G 以 SID=0 claim；:169 合法接续却改用 SID=4294967295 且传 `expected_previous_generation=first.G`；repository.py:374-379 要求旧 SID 与本次 SID 相等，故必抛 `ActivityLedgerConflict`，不能到 :170 新 G 断言。最小修复：同号恢复用 0；DWORD 上界新 claim 另建 pending 活动独立验。
3. 夹具版次：attempt-01/as-run hash 7C650F78…，当前 fixture 5F256503…，只有 :111 `psycopg.CheckViolation` → `psycopg.errors.CheckViolation`；因此 attempt-01 对最终夹具的迁移断言不作通过证明。runner replacement as-run hash 56E698A7…，当前 39E5917E…，只扩 :226 复验 parts 白名单；当前未运行版不能倒签历史复验。
4. runner 资源身份核验（CID/标签/镜像、端口/限制、镜像匿名卷 + 新建时点）比 first runner 的 `mounts==[]` 已改善；容器 selected inspect 不包含 Env。已跑 as-run 在校正信号和 `batch` 间保留同一进程内的合成连接资料，但记录内容与真实授权额度须看原始证据后裁定。
5. **确定 runner 证据缺陷**：`runner_replacement.py:239-303` 捕获所有 BaseException、最终写 verdict 后无非零退出；即使 FAIL/BLOCKED/cleanup_incomplete，顶层脚本正常 return 0。不能以 runner 进程 exit=0 判 PASS，必须看 `state.verdict`、子进程 exit、逐 phase 及最后清理。
6. **Windows 场景控制缺口**：`batch` :116 `subprocess.Popen` 立即启动 fixture，:118 才读精确创建时间，创建失败/读取失败会落入 finally；若在已启动后 `process_created` 失败，:273-277 仅 kill 父句柄且标未知，不能保证其已创建的 SUP/Job 树停止。runner 本体若死亡也没有外部独立收尾。`windows_case` 会创建旧 Job 及调用真实 launcher；因此此 runner 静态尚不能作为 Windows 恢复场景安全运行门。须先建立 Resume 前归属/独立截止及精确整树收尾，验证不使观察句柄污染最后句柄语义；PG-only 子集可分开评估。
7. 预算条件风险：`docker()` :53-55 与 `batch` :122 均以 `max(1,left()-reserve)` 允许总 deadline 已耗尽后再启动一秒动作；finally 连续 stop/inspect 可越过 60s 收尾预留。须改成剩余≤0先停止新动作、清理步骤使用统一剩余与保守未知；有限故障模型外的内核无限阻塞不要求硬实时。

这些是日志前静态判断。初批具体到达哪一行、资源是否已停止、attempt-02 是否实际启动，待原始证据核对。
