# review-07 原始证据核对后补充判断

本页不覆盖先前两份日志前初判；以下为完整可达路径复核后新增的静态发现与原始记录对照。

## 静态新增

- `session.py:190-208,331`：旧 Job 的 terminate/树零/close 任一失败被记到 `old_failure` 并抛出；因 `created_job=False` 且 `cleanup_errors` 通常为空，结果会 `failed_closed, cleanup_incomplete=False`。最短触发是旧 Job 打开成功、`wait_empty_until` 返回 False、close 成功；或树零已得而旧 Job close 失败。此时旧树或句柄未得确证，结果不能报清理完整。旧 running 在 Open 错误、异号等 claim 前拒绝时也输出 `(settled,reserved,pending)=(0,0,0)`，而账本原 R 可能非零；字段若被当总账事实使用会误导。最小修正是显式跟踪旧树/旧句柄未确认并上报 `cleanup_incomplete=True`、账目未知 `None`；有效租约有意不接管旧树可单独定义为“本次未清理”，不得让外层误认全活动干净。
- `runner_replacement.py:151,239-303`：`ok` 只查子进程 exit0、stderr 空和任意 `complete` phase，未核 `all_pass` 及所选各 phase/结果；顶层吞 BaseException、写 verdict 后没有失败退出码，FAIL/BLOCKED 也返回进程 exit0。必须加逐项 phase/字段/exit 一致校验和非零退出。
- `runner_replacement.py:116-154,264-280`：测试进程 Popen 后才取创建时间；timeout 时 `taskkill /T /F` 的返回码只记录不校验，子进程退出即置 `active_proc=None`，未知 SUP/业务 Job 未独立核查；Windows 相位失败仍可能 `cleanup_incomplete=False`。须在 Resume 前确立控制、持精确身份及独立 deadline，并在失败时有整树停止正证，否则上报未知且停批。
- `runner_replacement.py:109-116` 继承父环境且未见排除 `PYTHONOPTIMIZE`；fixture 大量关键判断是 Python `assert`。若环境启用优化，子脚本退出0和 `complete` 可能绕过关键断言。下次控制须固定优化关闭或把关键断言改为显式失败，并验运行标志。当前实际环境未取，不能说本次已优化。
- `d3_pg_windows.py:240` 的 `"mutex_release":"SUP outcome returned after DB settlement"` 是写死字符串，不是观测到的跨进程互斥释放次序。该次序由当前源码及纯替身事件可静态支持，未来 Windows 单次结果不应独自声称实测此细节。

## 原始事实

- 首资源 attempt-00 runner verdict=BLOCKED、7.859s、0测试；匿名卷 `mounts==[]` 误判，后来同 ID 事后 stop exit0、Running=false；首 runner 原状态 `cleanup_incomplete=True` 不得回写成干净。
- 替补 attempt-01 meta：仅1 PG 测试进程，PID31624/created_100ns134348108976985801，exit1、0.891s；stdout 仅 `schema(empty)`，stderr PostgreSQL 确认负 SID 违反 CHECK，然后 `except psycopg.CheckViolation` 本身触发 AttributeError。只能证明 006 在空表执行且 -1 拒绝；其余迁移/ledger/Windows 未运行。
- 替补 as-run runner 56E698A7… 缺全量复验白名单；go 文件确为 `migration,ledger,windows`，runner-log 在第二 Popen 前报 invalid correction selection。当前 runner 39E5917E… 已补白名单但没有运行证据。替补 runner-state verdict=ATTEMPT_1_FAILED，elapsed81.765s，stop exit0、容器 final Running=false、cleanup_incomplete=false（仅记录时点）。当前 fixture 5F256503… 对 as-run 7C650F78… 只改异常名称，未复验。
- 自动批准审查两次拒绝宽泛 grep/未过滤 manifest，因为可能输出密码/DSN；随后的审查限定为非凭据源行、选取的 JSON 字段及排除凭据的日志行。未读容器 Env 或完整 DSN/口令；审计不据未读秘密推断认证可行。
