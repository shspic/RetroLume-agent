# TASK-083 09轮 D3 旧G恢复 — 有限事实收敛与恢复决策建议

日期：2026-09-25；性质：只读事实决策，不实施、不改模型。此前调查基础：Ndocu/evidence/task-083/official-facts.md（六页摘要，原事实引用不重复取证）；本轮新增官方来源 5 个（≤6 上限内），未做系统身份探针、未做真实旧G实验。

## 一、新增官方决定性事实（5 项）

| # | 来源 | 决定性内容 |
| --- | --- | --- |
| S1 | Kernel object namespaces — learn.microsoft.com/en-us/windows/desktop/TermServ/kernel-object-namespaces | ① 命名内核对象（含 event/mutex/file-mapping/job object）按会话分命名空间：除 Global 外"each session has a separate namespace"；② `Local\` 前缀（或无前缀，客户端进程默认）= 在**本进程所属会话**的命名空间创建/打开；③ "Fast user switching is implemented by using sessions. The first user to log on uses session one, the next user to log on uses session two, and so on." — 会话号按登录次序顺序分配。 |
| S2 | Object Names — learn.microsoft.com/en-us/windows/win32/sync/object-names | job object 与 event/mutex/semaphore/timer/file-mapping 共享同一命名空间与 `Local\`/`Global\` 前缀语义；同空间同名即碰撞（ERROR_ALREADY_EXISTS）。 |
| S3 | Job Objects — learn.microsoft.com/en-us/windows/win32/procthread/job-objects 及 JOBOBJECT_BASIC_LIMIT_INFORMATION（JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE 0x2000） | "The job is destroyed when its last handle has been closed and all associated processes have been terminated. However, if the job has the JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE flag specified, **closing the last job object handle terminates all associated processes and then destroys the job object itself**."（本产品 NamedJob 恒置此标志。） |
| S4 | ProcessIdToSessionId — learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-processidtosessionid | 进程可取得自身（或持 PROCESS_QUERY_INFORMATION 的目标进程）所属 RDS 会话号；当前控制台会话号另有 WTSGetActiveConsoleSessionId。即 SUP 进程可在 claim 时**自证**其会话号，无需特权。 |
| S5 | logoff 命令 — learn.microsoft.com/en-sg/windows-server/administration/windows-commands/logoff | "When you log off a user, **all processes end and the session is deleted** from the server."（会话注销终止该会话全部进程并删除会话。） |

与 official-facts.md 既有结论合用：`Local\` 对象随会话（进而随 boot）生灭；numeric session id 与 uptime 均非唯一化身（墙钟/uptime 不得充当 boot 身份——维持原判）；本批 C2 场景提供了 S3 的**真实进程实证**：SUP 被父终止后其业务 Job 内 2 个进程仍存活（控制者持句柄观察到 active=2），由控制者终止后才归零——"SUP退出≠树空"的同时，"最后句柄关闭→树灭→对象销毁"语义成立（C2 中 SUP 自身收尾后 Job 对象查询如实失败、两个 worker PID 复核均消亡）。

## 二、同命名空间"对象明确不存在+无迟到创建"能否足以全额折叠？——**能**，条件收敛如下

1. 恢复主体先取得**活动级互斥**（`Local\…Owner`，S1/S2：同会话内可见、互斥）并持有至折叠事务提交。互斥是"无迟到创建"的屏障：能创建该活动 Job 的主体（旧SUP）在 run_once 全程持互斥；互斥易手后旧 SUP 要么已结束（其 run_once 已把 DB 收敛为非 running，或已死亡），要么已死亡。
2. 在互斥内重读 DB running/G/租约；严格区分 `OpenJobObjectW` 的 **ERROR_FILE_NOT_FOUND** 与权限/其他失败（后者一律失败关闭）。
3. FILE_NOT_FOUND + 租约已过期 ⇒ 按 S3 语义：若旧 SUP 曾创建 Job，其死亡（会话内唯一持句柄者）即触发 KILL_ON_JOB_CLOSE 杀树并销毁对象；对象不存在与"旧树已灭"在**同一会话内**等价。无部分退款、无 t1 记账——全额保守折叠 W（S+=W，R=0），与 082 批准的保守模型一致。
4. 旧 SUP 仍存活的对偶情形被互斥+对象存在性自然排除：活着则必持 Job 句柄（对象可打开→走精确 terminate/整树确认路径，本批 B 场景实证控制者持句柄可收尾）或持互斥（等待其退出）。

## 三、推荐方案（最小持久扩展；新增持久字段=真越界项，**须用户批准门，本卡未实施**）

**claim 事务内随 G 原子新增一列 `running_owner_session_id`（bigint/DWORD 取值），值=SUP 进程经 S4 自证的会话号**。恢复策略按值裁决：

| 恢复进程会话号 vs 旧行 | 裁决 | 依据与保证 |
| --- | --- | --- |
| 相同 | 允许全额保守折叠（互斥→FILE_NOT_FOUND 核查→租约过期→折叠 W） | 同号⇒同 `Local\` 命名空间（S1）⇒ 对象核查精确命中；无迟到创建由互斥保证。跨 boot 同号（会话号每 boot 顺序重发）时旧 G 的进程/对象已随前次 boot 全部消亡，折叠同样安全——即同号路径在"同boot同会话"与"跨boot同号"两种子情形下均安全，**无需可靠 boot 身份**，从而绕开官方无用户态可查 boot GUID 的事实缺口。 |
| 不同 / 字段缺失（含迁移旧行 NULL） | 失败关闭，不自动折叠，保留 R 等人工处置 | 异号时无法区分"同 boot 异会话的活旧窗"（危险：对象在别会话命名空间，open 失败但旧树可能活着）与"跨 boot 异号"（安全但不可证）；一律保守。 |

- **可达保证**：同号路径的折叠正确性（不双跑、不漏杀、不误退）；异号路径的安全停止。
- **不能保证**：异号旧 G 的自动恢复（恢复可用性在此路径受限，接受保守代价）；任何部分退款（不追溯死亡窗，维持批准边界）。
- **部署限制（不批字段的替代解，二选一）**：应用固定单交互会话运行（不做服务、不经计划任务跨会话拉起），跨会话/跨机重启的旧 G 一律人工按 runbook 核实后手工折叠。即"同号自动折叠 + 异号人工"或"全部人工"。
- **不采用**：常驻见证平台/逐阶段 witness/owner epoch 表（082/084 已论证非必要且自身也会死）；uptime/墙钟充 boot 身份（维持排除）。
- **迁移兼容**：005 之后新迁移（如 006）只加列带 NULL 默认；旧行缺值失败关闭；claim 接口同步写入；取消/旧SUP结算仍以原 status/G/C/CAS 裁决，不受影响。
- **最小后续验收（若获批实施）**：定向 PG 用例（同号折叠/异号拒/缺值拒三例）+ 恢复路径纯单元；不重跑 079/PG08。

## 四、结论

D3 的决定性缺口（旧 G 所处 Local 命名空间化身的可靠标识）在"boot 级化身"维度无官方用户态来源，维持不可得结论；但**会话级化身**（S4 自证 + S1 命名空间语义）足以支撑安全全额折叠，代价仅一列随 G 原子写入的会话号与"异号失败关闭"的保守限制。是否接受该持久模型扩展与部署限制，交用户/编排批准；D3 决策未批不妨碍本卡 D1 独立成果（四场景真实通过）。
