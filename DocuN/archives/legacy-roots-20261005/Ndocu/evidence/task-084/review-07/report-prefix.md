# TASK-084 / R-078 / STEP008 — review-07 D3候选与完整验证链独立审计（2026-09-25，当前有效）

**结论：D3核心的同机同会话旧G全额保守折叠，在批准的受信部署前提下具备静态实现骨架；当前仍有两项产品确定缺陷、PG夹具一项必然失败的错误，以及runner运行控制和证据协议缺口。代码层不通过，PG与Windows运行门均未打开。** 006空表执行及负SID CHECK拒绝仅有局部真实证据；真实claim、完整迁移、旧G Windows恢复均未到达。两容器额度已用且仅有记录时点的停止证据，本审计未启动资源或批准重启、轮换凭据、第三容器。旧Job07、PG08、09、084 review-06按未变方法/依赖及各自证据范围复用；不签M-1/STEP008或产品接线完成。

## 身份、顺序、快照

当前为原084独立审计上下文；实际客户端Codex desktop，本轮可见模型标识GPT-6（无更细后缀可核），未参与083代码/测试/runner编写或运行，不接管实施编排。根及公共AGENTS沿同窗已读未变复用。先读082批准的D3决定、当前TASK-083合同/停止前缀及自己review-06三条件；再审006/repository/session/windows_job、launcher/supervisor出口和真实pre副本，保存`product-prelog-assessment.md`；之后审四项测试、runner各as-run版与差异，保存`fixture-runner-prelog-assessment.md`；最后才看原始offline/PG/资源日志、fix记录和083结果置顶两段（待评陈述）。未读实现聊天、容器Env、真实配置、任何口令或完整DSN；未作新网页查询，review-06官方Windows语义按原限定复用。

九个指定冻结文件本轮SHA-256全部MATCH，逐项见`review-07/hashes.txt`。直接出口`activities/__init__.py`、`worker/launcher.py`、`worker/supervisor_main.py`与本轮pre副本哈希相同。首runner as-run `6B796C00…`、首修正`E21B41B6…`、替补as-run `56E698A7…`、当前候选`39E5917E…`分开归属；替补夹具as-run `7C650F78…`，当前`5F256503…`只改异常类第111行。083包内未找到卡面泛称的`incremental.diff`，故从真实pre和当前产品生成`review-07/product-pre-current.diff`。两次宽泛读取请求被自动审批审查拒绝，理由是可能输出密码/DSN；之后仅用非凭据源码行、选取JSON字段及排除凭据行的日志完成审查，没有绕读秘密。本轮仅文本/hash/只读diff；未import、AST、compile、单元、Job、spawn、PG、Docker、网络、安装、模型或诊断脚本，动态额度0。

## 产品逐项结论

| 条款 | 当前静态判断 | 限制 |
| --- | --- | --- |
| 006与身份域 | **代码通过**。`006_activities_running_owner_session.sql:1-8`仅增BIGINT NULL默认列、CHECK 0..4294967295、BEGIN/COMMIT；`repository.py:356-364`精确int拒bool/负/溢出，0有效；旧行不回填。 | 完整回滚、上界/超界、旧行NULL真实PG未验。 |
| claim、折叠与清理 | **主体静态成立，时钟缺陷阻断整体**。`repository.py:366-435`保留来源→活动锁，旧running G/SID在同事务重检；R→S全额，耗尽时提交pending/关门/清SID后返回None；新G/R/SID同UPDATE；`settle:558-586`最近G/C先判、成功清SID，`cancel:598-622`全额折叠并清SID。旧record/admit语义未改。 | `:369-413`截止时钟失真，见P1；新SID原子写尚无真实PG证据。 |
| 可信恢复入口 | **有条件成立，报告缺陷阻断**。`session.py:142,170-219`SUP自身读SessionId；running必须显式配置单机单交互会话、旧SID非NULL且相同、来源有效、租约/截止可接续；在ActivityMutex内Open精确旧G，只有JobOpenError.code=2可作为对象不存在候选；存在则terminate→ActiveProcesses0→close，随后claim CAS。`windows_job.py:162-168,260-267`保留Windows错误码，5/87拒绝；claim响应丢失不spawn/重认领，互斥至DB返回和收尾后才释放。 | 布尔开关是受信部署声明，不自证同主机；多主机共享库/迁库/异会话须由部署约束禁用。旧Job未证收尾可报clean，见P2。 |
| 并发与迟到 | **受限模型内静态可守**。同机同会话所有SUP守同一Local互斥时，活旧SUP挡新SUP；旧SUP死后无迟到Resume主体，旧Job的KILL_ON_JOB_CLOSE/无breakaway沿review-06官方语义。claim重验G/SID/租约，取消/来源变化在事务中重新拒绝。 | inspect快照至claim可变；中间取消或来源变更可先停旧树后由claim冲突，属保守停止而非退款。非守互斥的低层调用、多主机不在批准生产模型。 |

**P1｜事务起点时钟可在活动截止后授予新窗，确定产品缺陷。** `repository.py:139-164`事务在来源锁前启动，`:250-268`可等待来源锁；`:369-413`以PG`CURRENT_TIMESTAMP`为now，它固定于事务开始；`inspect_window:441-460`同样。最短交错：deadline剩不到2秒时启动claim，另一事务持来源锁至deadline后，当前claim获锁；`:380`仍以锁前时间判未过期，`:413-433`可写入已到期lease并提交running/G+1/R/SID，SUP管理期限内仍可建Job/Resume。2秒锁超时足以出现此交错。旧租约在锁等待期间的判定则偏保守，不能据此断言提前抢占；主要风险是过期活动获新窗。**最小修复**：恢复原claim在完成锁后采主机UTC墙钟的口径，并让inspect在锁后同口径判租约/截止；若选PG`clock_timestamp()`，须明确时钟契约变化并以锁屏障PG证据证明。不能把`CURRENT_TIMESTAMP`挪到同事务另一SQL假装修复，也不承诺任意内核阻塞下绝对硬实时。

**P2｜旧Job失败出口会把未知树/句柄报作清理完整，确定产品缺陷。** `session.py:190-208`旧Job terminate/等待false/查询异常或close失败只设old_failure并抛；`:301-304,331-344`因created_job=False且cleanup_errors通常空，可返回`failed_closed, cleanup_incomplete=False`。最短触发是同号旧Job打开后wait_empty_until返回False、close成功：最后句柄是否由他者持有未知，树零未证，却显示clean。Open5/87或SID不符等旧running在claim前拒绝还可能输出账目`(0,0,0)`，而快照R>0。未见误退款或新spawn，但外层若凭结果续批会误判。**最小修复**：跟踪旧树/句柄未确认，旧Job停止/查询/close失败或存在性无法确认时`cleanup_incomplete=True`；running旧账在无已确认新claim/折叠结果时用`None`表达未知，或严格定义并要求消费者识别“仅本次新窗”的字段语义。有效租约有意拒接旧树可另列状态，不能当全活动已清理。补定向纯替身断言，不改账本事务。

