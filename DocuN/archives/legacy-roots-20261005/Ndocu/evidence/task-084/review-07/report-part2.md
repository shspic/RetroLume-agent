## 夹具与runner完整路径

| 项 | 最短触发、影响、最小修复 |
| --- | --- |
| F1 确定阻断 `d3_pg_windows.py:150,164-170` | 旧G SID=0，合法接续却传4294967295和expected_previous_generation；`repository.py:374-379`必因SID不同拒绝。合法接续改0；上界在另一pending活动初领并查持久值。 |
| F2 已修未验 `d3_pg_windows.py:108-115` | as-run误捕获`psycopg.CheckViolation`导致AttributeError；当前改`psycopg.errors.CheckViolation`，未运行。 |
| F3 已修未验 `runner_replacement.py:219-228` | 替补as-run遗漏合法`migration,ledger,windows`白名单；当前已补，未运行。 |
| R1 Windows控制阻断 `runner_replacement.py:116-154,264-280` | Popen先运行后取PID创建时间；读取失败时子进程已可建SUP/Job，finally仅杀父句柄。超时taskkill返回码只记录，未取确切SUP/Job树零；active_proc置None后不再收尾，Windows失败仍可cleanup_incomplete=False。runner死亡无独立收尾。需悬停创建、精确归属与独立deadline、控制建成后Resume、失败整树正证；无证则unknown停批。观察句柄不得保活被测最后句柄。 |
| R2 证据协议阻断 `runner_replacement.py:136-154,239-303` | ok只查子进程exit0、stderr空、任意complete相位，不核所选各场景与all_pass/parts；顶层吞BaseException后仍进程exit0。必须核逐项唯一完整结果及clean，任何失败非零退出，保留原始证据。 |
| R3 期限/断言 `runner_replacement.py:52-55,109-128,204-228` | `max(1,left()-reserve)`允许deadline/预留耗尽后再启动一步；Popen与taskkill+二次communicate未共用≤60s；Windows场景只结束后assert≤30s。按绝对截止控制每步/每场景、预留收尾。继承父环境未排除PYTHONOPTIMIZE，大量assert可被优化关闭；固定优化关闭并核子进程标志或显式raise。实际环境未知，不能说本次触发。 |

夹具已有的正确结构：`d3_pg_windows.py:43-52`每子例随机schema，按001—005/006顺序；`:64-90`限定search_path传仓储、行查询、expire；`:93-140`意图覆盖空表/旧running NULL、0/上界、负/超界和失败事务回滚；`:143-193`意图覆盖有效租约、新G、全额折叠、耗尽；`:196-241`真实建旧Job、取PID和创建时间/树零、close后Open错误2，再走固定run_supervised_window到新G/真实PG结算。此为生产路径合成前提，未替换被证明的恢复函数。`windows_case:240`写死的mutex_release文本不是真实互斥释放观察；顺序现由源码和纯单元事件支持，未来Windows单场景不得凭该字段声称实测。失败/成功schema都保留，无DROP。替补资源核准CID/标签/镜像/限制/loopback端口/镜像声明匿名卷与CreatedAt；所存selected inspect不含Env。资源检查通过不抵消R1—R3。

## 原始事实与预算

| 事件 | 已证 | 不可推出 |
| --- | --- | --- |
| 首资源1086a37d… | 首as-run以`mounts==[]`误拒镜像自动匿名卷；runner verdict BLOCKED、7.859s、PG/Windows测试0、原状态cleanup_incomplete=true；事后`cleanup-after-identity-check.txt`同ID/标签stop exit0、Running=false。 | 不倒改原先未知，也不是迁移测试。 |
| 替补85242648… attempt-01 | meta：PG测试PID31624/创建时间134348108976985801、exit1、0.891s，phases仅schema；stdout仅empty schema；stderr先是负SID的PG CheckViolation，再是错误捕获AttributeError。 | 只证明006空表执行与-1拒绝；0/上界/超界、旧行/回滚、claim/Windows均未运行。 |
| 替补go与收尾 | go为`migration,ledger,windows`；runner-log在第2 Popen前报invalid correction selection；attempt总数1，Windows启动0。最终所选身份/资源字段匹配CID、镜像、标签、loopback55439、唯一匿名卷；stop exit0、Running=false、cleanup_incomplete=false，81.765s。 | runner退出0不是测试PASS；停止仅日志时点，本窗未查Docker；当前未运行修正不能倒签历史。 |

累计离线3批；真实PG测试进程/批1、Windows0。原上限3批/3PG/12Windows账面余**2批/2PG/12Windows**，但容器已达2上限，不能自动继续。总时至少**7.859s+首次事后收尾耗时（无完整可合并数字）+81.765s**，原30min总限不重置。离线最终D3六项、受影响旧Protocol两项和offline05 PASS；offline05诊断绑定session `DFD342…`/fixture `BB301…`、Δ400ms/C1/W6，仅证明替身。Job07 create/碰撞/最后句柄、PG08 005/关门/最近G-C原语义、09固定launcher四场景沿未变方法和原始证据复用；新增SID、时钟、恢复分支的动态证明不在那些PASS中。

