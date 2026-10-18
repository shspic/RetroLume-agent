# TASK-083 / R-077 / STEP008 执行结果：审计修复轮02（当前有效）

**状态：部分完成并停止本轮。不得进入 Job/PG 运行门或产品接线。** 本窗口实际标签 GPT-6，是原083实现者，不承担独立安全审计。084的D1管理启动上界、D3恢复证明仍未闭合；本轮最终命令路径修正后的定向复检3项中1项失败，原因未证实，修正/复检额度已用尽。原5个Job、旧04缺证及历史失败预算不清零；005未执行，PG/Job本轮启动数均为0；不宣告STEP008或M-1完成。

## D1—D8 增量结论

| 审计项 | 本轮变更与最终定位 | 状态和限制 |
| --- | --- | --- |
| D1 启动/IPC/期限 | launcher.py:46 将管理截止分出清理预留，所有已返回的Process对象使用同一绝对截止有限join/terminate/kill；start异常后按精确对象尝试收尾，poll/recv/close异常保留未知结果。纯替身09—11覆盖这些分支。 | **未闭合、运行阻断。** multiprocessing.Process.start返回前没有独立可终止的SUP句柄；子pipe.send和父recv仍可能卡在无独立取消的调用，有限故障模型下不能证明整体期限。不得以替身通过冒充生产启动/IPC上界。最小控制结构变更见下文。 |
| D2 固定入口/门 | command.py:15,28 固定项目venv解释器与唯一 app.worker.worker_main 模块，只接受 idle/one_call受限任务数据，不能由生产参数提供exe、-c或脚本；worker_main.py:27,46 的真实模块入口调用run_internal_task→run_controlled_worker→ClosingCallGate。one_call在无供应商接线的产品入口会明确失败；假gateway纯单元12证受控调用。 | **代码候选，Job与真实供应商未验。** venv转发器可能增加Job内进程，未来控制器按确切Job整树检查；不得把初始PID当最终解释器。 |
| D3 失败后恢复 | session.py未改；旧Job打不开时仍失败关闭，claim已提交但Job已消失可永久挂R。 | **提案待编排裁定。** 不能把Open失败或单纯主进程退出当整树空；下述持久证明/所有权扩展超出已批准005单列。 |
| D4 合成Job控制 | test_worker_session.py已移除可直接执行的旧WindowsJobTests；job_control.py:18,165、scenario_child.py、job_batch.py:20准备01/02/03/05统一Start→悬停身份→精确Job/进程句柄/创建时间核验→Arm→Resume；04的fixture.py:20加入Start门和单进程Job限额，04观察句柄在Exit前释放。单场景25/20秒，批入口55秒且失败停批。 | **仅准备，全部not_run。** 04最后句柄关闭后不能再查询该Job的ActiveProcesses，结果诚实写null，仅报告关闭前count=1及该单进程夹具的精确进程退出；此证据强度须独立审计。初批04旧count0仍不足。 |
| D5 PG02 | pg_close.py:122 将预留凭证按原合法UNKNOWN收敛，统计期望unknown=2；repository.py未改。 | **静态修复，PG not_run。** |
| D6 取消 | offline_unit.py:145 对claim响应未知的取消断言改为R/S=(None,None)，保留取消重抛与收尾断言。 | **纯单元初批通过，最终此路径源码未再改。** |
| D7 PG隔离 | pg_close.py:38每例随机schema，001—005在其内准备；仓储、行查询、并发、定向FK清理均使用同一search_path DSN；pg_close.py:140以实际来源锁持有/请求屏障控制close先提交和mark先提交的正反序。pg_migration.py:26失败保留schema，本轮不DROP；仅专用环境变量RETROLUME_TASK_083_DATABASE_URL，缺失skip。 | **可执行候选，PG not_run。** 锁与迁移实际事务效果、失败保留和清理仍待定向PG验证；新schema最终删除须另卡授权。 |
| D8 未知树结果 | launcher.py:46后所有外层超时、SUP丢失、start/recv失败均返回R/S/待折叠=None和cleanup_incomplete=True，即使SUP已退出亦不声称Job树空；有SUP结果但外层清理异常时标记不完整。 | **纯替身08—11通过；真实Job未证。** D1未闭合，不能进入运行。 |

## D1与D3的具体决定边界

D1的决定性缺口是CPython Process.start和Connection.recv的调用中没有可在调用尚未返回时由当前父方握持并取消的精确SUP对象。现有代码已在返回后的故障路径保守收尾，但无法证明启动前后整体deadline。最小后续实现是替换该父级Process/Pipe控制段：父方创建悬停SUP并在Resume前握精确进程/管理Job句柄，使用有界、可取消或可由终止SUP保证结束的结果协议，所有等待共享同一截止；CreateProcess自身内核不返回的情形仍在有限故障模型之外。此项需要先核对相应Windows API事实并经084独立复核，不能继续用新线程包装阻塞start。没有请求本轮额外运行或新增服务。

D3的最小恢复闭环**提案，不是本轮实现或已获批准**：新增按(activity UUID,G)唯一的持久window witness记录及持久owner epoch/CAS接口，记录命名空间/登录会话/boot身份、Job名、worker PID与创建时间、阶段CLAIMED→ASSIGNED→ARMED→TREE_EMPTY及可信主体。claim同事务写CLAIMED；单一持有活动互斥的所有者创建悬停Job/Assign，ASSIGNED提交或同代次读回确认后才可写ARMED并Resume；Job外可信持句柄者查询确切ActiveProcesses=0后写TREE_EMPTY，再允许close/settle。旧SUP晚到须受互斥和epoch CAS拒绝；提交响应丢失只读回同G/owner阶段，不盲目再领或Resume。整应用重启由独立于应用SUP的持句柄见证者按持久记录找回；见证者或证明丢失、命名空间/权限/boot不符时失败关闭，绝不凭Job不存在退款。仅用DB标记和易失Job无法原子地区分“从未创建”与“创建后在标记前崩溃”；该空隙归UNKNOWN，未ARMED者不得曾执行受控工作，仍需互斥/进程归属证明排除迟到创建。见证者自身死亡后的正常恢复仍需经官方Job销毁语义与同命名空间实证判定，否则保持保守预扣，不把新的看门责任递归假定为永不失败。

原批准边界只有005的dispatch_closed；上述持久表/接口及独立见证者均是**需编排取得具体批准的模型/职责扩展**。现合同的失败关闭代价是旧R可能长期不能折叠、无新窗，不能作为满足恢复目标的解法；不能擅自改折叠/结算或添加字段来掩盖。

## 最终文件、差异与验证账

所有改前已保存副本在 Ndocu/evidence/task-083/audit-fix-02/pre；逐文件旧/新SHA256、AST及冻结仓储/005匹配在 static-final.log，增量文本在 incremental.diff。例外：原有 fixture.py 的改前**字节副本遗漏**，其084基线hash为D511DCEA4E7E22F5E01D91B2845479FB8DB4CF5D33405C18E0E1C6ABA7F5636E，最终hash见静态日志；diff将其误列为全新文件，不能据此声称精确增量。其余重要最终hash：command b0e91c3a…、worker_main 5d065b5e…、launcher f650d2b8…、job_control 62396193…、pg_close 00b58fe7…、pg_migration 85d27efd…。repository 929320BA…、005 26B71A83…与084冻结值相同，001—004未改；没有改正式docu、公共库、gateway主体、HTTP/runtime、PDF、配置或Git。

| 验证 | 真实命令/证据 | 结果 |
| --- | --- | --- |
| 初始纯单元 | backend/.venv/Scripts/python.exe -B backend/tests/fixtures/task083/run_audit_fix_02.py；unit-initial.log、unit-initial-meta.txt | exit 0，14/14，约0.89秒；属于修正解释器路径**之前**快照。 |
| 唯一修正复检 | backend/.venv/Scripts/python.exe -B backend/tests/fixtures/task083/run_audit_fix_02_recheck.py；unit-recheck.log、unit-recheck-meta.txt | exit 1，3项中2过；test_05_early_success_uses_tree_zero_close_then_same_g_settle_retry返回elapsed_violation_full_reservation而断言期望settled。原因未证实，最终快照**不能称通过**。约0.62秒。 |
| 最终静态 | backend/.venv/Scripts/python.exe -B - 执行一次限定AST/差异/hash脚本；static-final.log、incremental.diff | exit 0，13个改动/新增Python文件AST通过，冻结仓储/005匹配；局部无明文凭证或真实外发URL模式。它不验证行为、OS或PG。 |
| Job/PG/迁移 | 本轮未执行 | not_run；Job启动数0，PG连接数0，005未执行。 |

复检失败后没有再改源码或追加测试。初批14项只有不受最终命令argv改动的条目可作局部证据；05最终失败，不将旧PASS沿用为最终PASS。历史Job 5例及旧04缺证原样保留。没有真实出站或旧进程调查/操作。任务预算未按新脚本或中断重置。

后续最小门：先由原084独立增强窗口只读复核D1/D2/D4/D8最终控制链、D3权限提案和本次复检失败；不对未改仓储全量重审。D1/D3和05单元失败未关闭前不进入Job运行。若编排修复并另给预算，Job最小清单为01正常退款、02挂死全额预扣、03主退后代、04最后句柄/旧失败、05因统一控制器和身份入口变化需核验同名碰撞；每例按job_batch的精确对象与停止条件复审后才可执行，不承诺按当前脚本直接放行。PG定向ID为 PGMigrationTests.test_pg_migration_01_empty_table_adds_only_closed_column、test_pg_migration_02_nonempty_table_rolls_back_whole_005、PGCloseTests.test_pg01_close_settle_and_old_gc_does_not_touch_new_window、test_pg02_closed_gate_rejects_admit_mark_but_records_outcomes、test_pg03_close_commits_before_concurrent_admit_and_mark、test_pg04_cancel_closes_gate_and_old_dispatched_unknown_converges；专用DSN缺失skip，另卡授权运行/清理。文档建议由编排把083保持“部分/运行冻结”，登记D1/D3与本轮复检失败；本实现者不签安全通过。

---

## 历史：离线补足轮01原文


