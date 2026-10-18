# TASK-082 / R-076 独立诊断结果：先预扣再启动的单窗停止结算协议

**结论**：081修正轮01仍不能作为退款或跨恢复时间安全的实施合同。推荐一个可证伪的最小路径：每个受控会话先由可信启动器完成一次既有 `claim_lease` 持久预扣，再创建并运行唯一Windows Job；从认领前的单调时间起至该Job全部进程确认退出止计入本窗 `C`；先关闭不可重开的发送门，后确认整树退出，再由Job外可信监督者调用既有 `settle_execution_window`。失败保守折叠W且旧树未明不启新窗。新增一个持久 `dispatch_closed` 位及内部关闭接口是推荐的明确DB关闭门；不推荐081的两列会话数候选。本报告是**设计与取证结果**，不是实现、运行证据、安全验收或STEP008/M-1完成声明。

**身份/独立性**：本窗口系统标识为 GPT-6；具体 Sol/Astra 后缀或推理档位未向本窗口暴露，不冒称Codex Sol。全新诊断窗口，未参与081首轮及修正轮；任务卡已给出缺陷摘要，因此是**带已知发现的独立诊断，非盲审**。本窗口按根 `AGENTS.md`→公共 `docu/AGENTS.MD`→需求v1.1/架构v0.34/076批准边界→冻结源码→先保存 [`independent-initial.md`](../evidence/task-082/independent-initial.md)→再读081修正轮01→077—079必要导航→四页官方文档的顺序开展；未读完整执行聊天或全执行历史。基线提交 `45951501d2741630a229762d6b2d3f4b34d7f702` 与既有文档差异按卡面给定，未独立重建Git差异。`repository.py` SHA-256 `045a3cf8b1c81d7a1336c3bd2e90e891e4e53934027c9fea9727fafde7202534`、004 SHA-256 `8f04f57c743c260f5081e0c6f232860301b30c7b03fef69498d7c0704c0a97cc` 均实测吻合，未漂移。

## 依据及四问结论

**需求和既有批准**：`docu/LATER_REQUIREMENTS.MD:94-95,109,156-166` 要求取消/晚到/重启不污染状态，活动启动前可见有限时间等预算，达限停止本地自有工作，跨恢复不重置，远端可能继续须如实显示；`docu/PROJECT_ARCHITECTURE.MD:169-185,215` 将单调监督、持久预算、旧代次隔离和发送资格列为FLOW005/DATA007。076批准的只是004五列与 `claim/settle/cancel` 基础切片，部分退款必须另取得关闭/停止证据；用户库迁移、worker接线未获本卡授权。077/078当前修正与079结果只作为既有基础切片导航：079所报22例真实PG、004空库与约束验证限定有效，本卡未复跑，不延伸为监督通过。

**A 关闭与退款**：081的“有在途便不够时间新发送”不是不变量。若W剩余90秒、单请求timeout10秒、margin5秒，已有请求在途仍满足90≥15，另一调用可通过。当前 `gateway.py:117-143` 的 `admit→mark_dispatch_started→transport.send` 分离，`transport.py:52-85` 是异步httpx调用；`CancelledError` 只尽力记UNKNOWN（gateway:149-151）。`repository.py:709-766,815-827,880-904` 的DB短事务、操作表空或UNKNOWN均不能证明协程、底层传输或整个执行载体已结束。推荐双层不可重开门：worker本地读写门以**共享通行令牌覆盖从admit前直到该调用的传输与结果收尾**，关闭者独占取门并永久置closed，阻断新任务且join全部已登记任务；DB在同一活动行锁序下把 `dispatch_closed=true`，`admit`与`mark_dispatch_started` 均须检查false，关闭后永不为本代次复开。已获permit但尚未实际发送者仍持共享令牌，关闭必须等其完成或终止整个Job；DB mark先提交不等于已经发送，保留未知费用预留。**部分退款只在Job整树已证实退出后由Job外可信SUP结算**，此时任何worker协程、子进程或传输任务不可能再发送；SUP仅凭操作表/UNKNOWN不得退款。正常C<W仍可退款；无法取得退出证明则保留W，区别是用户会少得一次可复用余额、可能等待人工恢复，须如实显示。

**B 累计时间**：`repository.py:394-478` 允许C=0，也允许C远小于W；004仅保证 `S+R≤M`，故“W≥1 ⇒ 窗口数≤M”不成立。081的持久 `sessions_opened/max_sessions` 若严格先登记再产生受控工作且每会话一窗，**可以**界定窗数≤K；但单独的K×T有限上界并不等于原可见活动时间M，尤其K×T>M时。推荐把既有claim本身变为会话登记和预扣，且放在任何受控进程Resume、模型/工具动作之前；每会话恰一窗，启动、自检、传输、排空、Job退出均计入C。可信启动器在调用claim**之前**取 `t0=monotonic_ns`，正常可信SUP在Job全部退出后取`t1`，传 `C=ceil((t1-t0)/1s)`；若`t1≤t0`、C>实际预扣W或结算失败，不传虚假的0/封顶C，按W保守收费并登记异常。实际成功启动会话因此C≥1；失败会话全额折叠W≥1，故成功认领的会话数≤M，且在受监督退出耗时≤W的条件下，所有本地受控会话时间之和≤所有实收C/折叠W之和≤可见M。仓储仍可接受合成C=0，生产SUP不得用0结算一个已成功认领的会话。响应丢失的claim**不启动任何进程**，从持久事实恢复或在过期后折叠，绝不再次无条件认领；partial W使用返回的`ActivityLease.window_seconds`，若小到无法完成启动/停止保留全额、不开工。用户若坚持“启动/停止不计入M”，则此推荐时间口径不适用，需要额外持久预算并单独批准；不能借K×T把超出M的执行描述成满足M。

**C 所有权和重启**：统一顺序为 `t0→claim提交并确知结果→按(activity UUID, generation)确定唯一Job名→CreateJobObject(不得接受ERROR_ALREADY_EXISTS作为新建)→CREATE_SUSPENDED→Assign→SUP取得句柄及t0/W交接确认→Resume/armed→执行`。启动器持有本活动的命名互斥锁，覆盖“查旧树/认领/创建并分配悬停进程/交接”全段，防止另一实例误判“Job尚不存在”后旧启动器迟到创建；释放前不得留下未来还能创建Job的主体。SUP只监视本Job，不得换窗、再spawn或重开门；worker只在Job内运行。Job名由已持久的活动ID与代次导出，Job非继承/受限ACL、无breakaway；以CreateJobObject的已存在返回拒绝命名碰撞。启动器在claim成功但交接失败时关闭/终止所持Job，账本仍留R供保守折叠；SUP死亡由最后句柄关闭的KILL_ON_JOB_CLOSE处理。整应用重启先取得同一互斥锁，读取持久运行代次并由确定的名字 `OpenJobObject`，如仍存在则按精确对象终止并查询`ActiveProcesses=0`后才可能新claim；若名字、权限、句柄是否最后一个、活动进程数或旧SUP是否还能创建受控工作任一不明，**失败关闭**，保留R、拒绝新会话。明确对象不存在只能在“命名空间/互斥锁/无迟到创建均已验证，且确认最后句柄关闭后的OS终止与销毁语义”的条件下用作安全事实；其他Open失败不可当作整树退出。主进程退出、PID消失、单次Terminate返回均不足以代替。恢复与旧SUP并发settle时，活动行锁/CAS决定谁赢；旧树先证实结束，再处理残留折叠，绝不先claim后查树。

**D 最小取舍**：可信SUP可以接触账本并在Job完全退出后调用既有settle；SEC002没有禁止。推荐仅一窗一Job，无另起K列、无无限递归看门。启动器若负责SUP健康检查，就是**新增监督责任**：存活时可在固定检查期限后精确终止本Job；启动器自身死亡时，存活SUP继续监督；SUP死亡且无额外Job句柄时OS关句柄杀Job。二者同时存活但都不动作、整机无限停调度不在有限停止保证内；这不是“已实际验证”。后台心跳可省，改用启动器已有前台控制循环/恢复入口进行期限检查；若产品要求无人值守自动恢复，才把有界健康检查加入实现与故障模型，不再叠第三看门。参数由工程按实测停机上界配置，不能全部转给用户确认。

## 唯一推荐状态/时序表

| 阶段与持久态 | 唯一动作/门 | 进入下一阶段的可观察条件；失败处置 |
|---|---|---|
| 0 待认领，R=0 | 启动器取活动互斥锁，先读并确认旧代次Job整树退出；取t0后调用既有claim(W请求) | claim提交且返回W_eff/G才可建Job；返回丢失或失败不spawn，旧R待保守折叠 |
| 1 running，R=W_eff，门closed | 启动器建唯一命名Job，悬停创建并Assign worker，SUP取得Job句柄与t0/W，固定截止，然后Resume并armed | Job归属、句柄交接、SUP确认全部成功后worker才可工作；任一失败kill/关Job且不退款 |
| 2 running，R=W_eff，DB门open | worker收到armed后本地门open；每调用先取得共享令牌，`admit→mark→send→record/UNKNOWN`皆在令牌内；SUP管绝对截止 | 只有DB `dispatch_closed=false`且现有代次/租约/来源检查通过才允许admit/mark；mark已完成仍须持本地令牌才可实际send |
| 3 running，R=W_eff，closing不可逆 | 关闭请求使本地门永久closed并等待全部共享令牌；可信SUP调内部`begin_window_close(E,G)`原子将DB门置closed；必要时精确TerminateJobObject | 在窗口截止前得到Job内全部进程退出的正证据，才可退款；DB不可用/超时/不明则无退款并阻断新窗 |
| 4 Job空，DB门closed，R=W_eff | Job外SUP取t1，确认C=ceil(t1−t0)且1≤C≤W_eff，调用既有settle | 提交后pending、R=0、S+=C；响应丢失按最近代次幂等核实，不改已提交结果；无法确认则R保留供全额折叠 |
| 5 pending或cancelled | 旧Job已证实空，启动器才可依余额再次从阶段0开始；取消沿现有全额折叠合同 | 旧树未知一律不再开工；远端继续的可能性与次数/费用预留独立展示 |

**最多四个交错反例处置**：① 剩余90/timeout10/margin5时已有请求仍可再发送，阶段3依本地独占门加DB门截断新请求，不靠算术推断。② `mark`已提交、send尚未进入：共享令牌使关闭等待该调用，或杀Job后整树确认；账本保留UNKNOWN/费用预留。③ claim提交响应丢失：没有Job Resume；不重试创建未登记会话，过期后折叠W。④ C=0或partial W：实际会话不以0结算；W_eff不足以容纳启动/关闭时不开工并全额折叠，避免无限免费零窗。

## 不变量、数值与证据界限

设M为已配置且可见的活动执行秒数，S/R为004既有值，A=M−S−R；每次认领实际W_i∈[1,3600]且W_i≤A。正常C_i=ceil(t1−t0)∈[1,W_i]；故障折叠收费W_i。现有原子转移给出 `Σ(正常C_i + 故障W_i)+当前R≤M`，每会话收费至少1秒，从而会话数≤M；不用新增K。`t0`在claim前，交接前任何 worker 都悬停；故即使登记失败、响应丢失、SUP死亡，不能产生未登记执行。退款前DB门closed、持令牌的所有worker调用已退出且Job `ActiveProcesses=0`，因此旧permit即使在关门前取得也不能在退款后发生本地发送。旧树未知时不claim新窗，故无跨代本地重叠。以上为**待实现审计的不变量**，不是现代码已满足。

工程可行关系：令请求超时`q`、强制停止加整树退出预留`g`、启动及交接上界`s`、实际窗口W。必须有`W>s+q+g`才允许首个出站；每次新发送最迟`t0+W−q−g`，停止/kill最迟`t0+W−g`，整树确认目标≤`t0+W`。以W=90、q=10、g=5举例，最迟75秒开始新发送、85秒进入强制收尾、90秒前整树应为空；已有在途不改变75秒前可发新请求这个事实。5秒是**示例工程候选**，只有本机后续测得stop/Job退出和调度误差确能容纳时才可采用，不能写为Windows硬保证。DB结算事务在t1之后，另以事务/连接超时控制，严格不算Job执行时间；若每次其上界为d且会话数≤M，整段本地管理墙钟最多M+M·d（并非声称M覆盖全部监督开销）。若某次实际Job退出超W达ε_i，真实执行上限只能写`≤M+Σε_i`，记录违例并停新工，**不得**把W封顶记账冒充真实≤M；在确认`ε_i=0`的调度/终止故障模型下才得严格≤M。整机无限不调度没有有限实时保证。时钟用同一Windows主机CPython3.12的`monotonic_ns`计算差值；跨整机重启不比较旧t0，残留W全额折叠。

## 官方核对（仅四页；不是本机动态验证）

1. [Microsoft Learn：Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)，适用Windows Job Object：默认子进程继承Job，除非允许breakaway；可用精确Job终止；命名Job可重开；最后句柄关闭且设置KILL_ON_JOB_CLOSE会终止全部关联进程后销毁。**Job句柄signaled只被该页说明为end-of-job time limit触发的场景**，故081不能把一般正常退出/显式Terminate后的Wait(signaled)当通用整树证明。该页没有给停止耗时硬上界。
2. [Microsoft Learn：JOBOBJECT_BASIC_ACCOUNTING_INFORMATION](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_accounting_information)，适用Windows XP及以后桌面API：字段实际名为`ActiveProcesses`，不是081所写`NumberOfActiveProcesses`；定义是当前关联进程数，终止进程退出且引用释放后递减。对**仍可查询的确切Job**取0可作比主进程退出更强的整树证据；仍需本机实现核对结构、权限、查询失败与句柄存活，不能把失败当0。
3. [Microsoft Learn：CreateJobObjectW](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-createjobobjectw)，适用Windows桌面API：同名既存对象返回句柄并给`ERROR_ALREADY_EXISTS`，默认句柄不可继承；命名、权限及会话边界须在实现中核对，不能以同名返回冒充新建。该页说明最后句柄关闭/终止/销毁顺序；“Open明确不存在”可推断旧Job已销毁，但**此推断依赖确切命名空间、错误码和无迟到创建机制**，没有本机实测。
4. [Python 3.14 time文档](https://docs.python.org/3/library/time.html)，用于项目所记CPython3.12.10：`monotonic`在Windows基于QPC，Python 3.5起跨进程同钟，`monotonic_ns`免float精度损失；文档未给休眠、整机挂起时本机的计时误差或调度/Job停止上界，本报告不臆造。

## 最小拟变更与批准边界

| 项 | 必要性/依据 | 状态 |
|---|---|---|
| 004五列、既有claim/settle/cancel及次数费用账 | 保持076批准及079限定证据；不迁移用户库、不重复测试 | **已批准基础**，本卡零修改 |
| 005候选仅增`dispatch_closed BOOL NOT NULL DEFAULT FALSE`；claim重置、admit/mark检查、settle须已关闭；内部`begin_window_close(E,G)`沿现有锁序做不可逆CAS | 当前running与R>0绑定，不能借pending表示“仍预扣但停止新发送”；一位持久门是推荐的最小明确状态 | **主要模型/内部接口变更，需批准后实施**；不改004原合同 |
| claim先于spawn；t0前置、C计至Job全部退出；Job外SUP可信结算 | 使每个已启动会话先占W，C0不能免费重开；正常C<W仍可真实退款 | **主要时间语义变更，需批准后实施**；现卡只提案 |
| 命名Job、活动互斥锁、悬停Assign/交接、单窗worker门与SUP停止/查询 | 无迟到创建、无逃逸执行、整树退出确认；worker/Job接线不可省 | 后续STEP008实施卡，**本卡未授权实现**；工程内部细节不逐项向用户设确认门 |
| `sessions_opened/max_sessions`两列、SUP零账本禁令、Job句柄signaled等待、额外常驻看门层 | 在先claim+一窗+C≥1设计中不需要；前两列只给K×T上界，无法单独等同M | **可省/不推荐** |

## 后续真实新行为验证矩阵（非本卡执行）

| 新行为 | 实现定向证据 | 独立审计焦点 | 必要运行验证 |
|---|---|---|---|
| 005关闭位与admit/mark/settle锁序 | 新005候选、DB条件和少量有针对性用例；保留004 | 关闭后不可重开、旧permit、cancel与结果记录合法性 | 合成空库迁移/约束、真实PG关门与admit/mark并发；不重跑079账本全套 |
| 先claim后启动、响应丢失、partial W、C0禁用 | 可读的唯一时序及调用替身轨迹 | 无未登记Resume、t0传递、最小窗与费用保守性 | 本机定向启动失败/提交响应丢失、部分窗；检查没有受控动作 |
| 关闭和正常C<W退款 | worker共享/独占门、SUP在树空后settle的代码路径 | permit→mark→send交错、协程取消与DB门、退款主体只信整树证明 | 本机多并发异步发送的可控替身+真实Job，先确认全部本地进程退出，再看PG退款；不调真实模型 |
| 旧SUP/整应用重启与Job身份 | 命名、互斥、句柄交接、ActiveProcesses结构和错误处理 | Open失败/同名碰撞/最后句柄/无迟到spawn/无breakaway | 最小本机双进程Job：主进程先退出、后代仍在；SUP死亡、应用重启、查询0与未知失败关闭；记录实际Windows版本 |
| 时间边界与可见M | t0/t1单调差值、q/g/s关系、超窗诊断 | 不能把C封顶或K×T冒充M，SUP管理开销口径 | 仅新监督路径的正常早停、超时/kill延迟与时钟环境定向测量；不宣称硬实时 |

**实际操作和限制**：本卡只读本地源码/文档/hash，有限浏览四个微软/Python官方页面；只新增本结果及独立初判。未跑探针、compile、测试、PG、Docker、应用、模型，未下载/安装、未动源码/迁移/配置/Git/正式docu/公共库，未改原证据。手工推演不是测试，官方说明不是本机动态验证。Win32 Job明确不存在时的销毁先后推断、命名互斥锁与句柄交接、停止延迟，以及CPython3.12本机休眠行为仍须在**实施后的单次最小运行验证**中核对；任何一个身份或树退出事实不明即失败关闭。编排应先决定是否批准上表两项主要变更，再据此圈定实现与独立审计范围；本报告不填写编排验收。
