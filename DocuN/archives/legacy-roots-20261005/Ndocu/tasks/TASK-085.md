> 2026-09-28：TASK-085 已由编排验收关闭其批准成果。最终裁定见Ndocu/results/TASK-085-086-final-acceptance.md。以下为原合同/历史状态，不再授权运行或修改；无阻断补项。

> 2026-09-28执行回传状态：本卡实施与卡内验证已结束，候选等待TASK086独立审计。停止本卡代码写入与测试/资源启动；剩余批次/秒数不是续跑许可，Windows会话额度已用12/12。以下原合同保留供独立核对，不再按“待转交”启动。

# TASK-085 / R-079 — STEP006/008 受控单次业务调用接线
状态：待用户转交；2026-09-28。你是本卡执行Agent，不接管编排。完成后保存结果，回复一句结论和绝对路径。

## 1. 成果、执行者与授权
完整成果：受信内部调用者提供有限请求/配置 → 固定launcher/SUP → 真实预扣后把租约上下文交固定worker → ClosingCallGate → ControlledModelGateway+PostgresAdmissionLedger → 有界结果回传 → 原树零/关门/结算收尾。实现、夹具、定向离线/合成PG与Windows验证及范围内修复同卡连续完成，统一回传，不只交方案或准备脚本。

接收：继续刚完成TASK-083完整收尾14的最强执行窗口，保持当前客户端最强可用模型及最高可用推理档，增强执行；登记实际标签。仅原窗口不可用才新开续接，不重做083。路由理由：跨进程身份、秘密通道、停止与账面边界。
关联：STEP-006/008；INT-002、NFR-002/003、SEC-001/002、MOD-003/007/008、FLOW-005、DATA-007；依赖已关闭083/084，复用046/048及077—079有效证据。新成果085/R079，不续写已关闭083。
根：D:/shspic/project_NO3_RetroLume-agent。
基线：需求v1.1、架构v0.48、执行状态v1.68（本卡编排更新）；Git初始提交45951501d2741630a229762d6b2d3f4b34d7f702，后续未提交差异也是当前基线，不reset/checkout覆盖。
授权：用户“转向STEP006/008的受控业务调用接线”及“继续未完成任务”、既有07连续开发。编排据此安排内部实现和本卡独立合成验证预算，不继承083已撤销余量。真实付费模型额度0，用户库/个人资料操作0，无安装、外部HTTP入口、部署、提交/推送授权。

## 2. 最小上下文
入口：D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。
公共规则：D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD。
原窗口已读未变内容只核变化。公共库只读；执行者无需WORK及全阶段提示词。
项目内顺序：
1. docu/PROJECT_ARCHITECTURE.MD本卡增量、FLOW-005及G3/G4缺口；执行状态顶部和STEP006/008，需求相关条款按需。
2. Ndocu/results/TASK-083-084-final-acceptance.md；review09中直接复用控制的边界，不重读全部历史。
3. backend/app/worker/{worker_main,command,gate,launcher,supervisor_main,supervisor_ipc,session,windows_job}.py；capabilities/{contracts,gateway,transport,tools}.py；activities/repository.py、runtime.py（以上均在backend/app/）。
4. backend/tests/test_worker_session.py、现有gateway测试及fixtures/task083中实际复用的直接依赖；旧证据只按未变行为引用。
现状：worker_main.main用_UnwiredGateway，one_call传None上下文/请求；固定SUP只收command.task，真实租约在SUP获得；账本存操作元数据，不存业务正文。IPC现有8192字节槽不能直接假设容纳最大请求/响应。Windows PG用psycopg_compatible_loop_factory。

## 3. 固定实施契约
A. 内部入口及身份
- 类型化one_call接口供未来应用调用，接收既有活动ID、执行者、稳定operation_id、ModelCallRequest、ModelServiceConfig、监督配置。测试自行创建合成活动；不另建HTTP/队列/轮询。
- activity/executor/runTag严格校验；generation、scope_revision必须派生自本次成功claim返回的ActivityLease，不允许调用者指定代次作为执行权。W_eff/截止沿当前session，不由消息改写。
- 保持固定解释器/模块/cwd/有限任务枚举；可新增纯数据载荷或通道标识，不接受任意exe/argv/模块函数名/路径或反序列化代码。
- claim None、有效旧租约冲突、来源失效、取消、输入非法不得启动有出站资格的worker。保留idle用途；one_call缺数据明确失败，不静默变idle或空调用成功。

B. 通道与秘密
- 在固定启动链上把配置/请求及claim后身份交worker，提供有界回传。自行选最小机制并实现，无须先交设计卡；记录容量、schema/完整性校验、句柄/文件所有权、关闭时机和生命周期。
- 请求/响应写前限长，与ModelServiceConfig协调；内部限额更小时明确拒绝，不截断、不虚称支持最大载荷。未知字段拒绝；帧校验和不等于身份认证。
- DSN/key/正文不进argv、普通日志、证据或Git；配置由受信调用者显式提供，不扫描用户.env/真实凭据、不加隐式回退。秘密只在受控短生命周期通道传递，测试用新合成凭据。
- 生产endpoint白名单、trust_env=False、无重定向/隐式重试不变；禁止为测试放宽URL或加入生产可用的任意transport/command选择器。

C. 调用、时间和停止
- worker实际构造/使用ControlledModelGateway和PostgresAdmissionLedger，经ClosingCallGate传非None上下文/请求。一个one_call最多一次gateway调用，TOOL_PLAN只返回计划，不执行工具/自动续轮。
- 用兼容PG循环；timeout、启动/收尾余量与实际W_eff及不可后移单调截止相容。余额形成短窗则明确拒绝/保守收尾，不能为发送扩窗。保持先预扣后启动，不重写恢复器。
- 保留admit→mark_dispatch_started→网络→record；UNKNOWN不改成NOT_SENT、不换operation_id重发；取消/代次/来源失效不转成授权成功。
- 门关闭阻止新增调用，在途有界收敛；树零/自有句柄关闭先于原begin_window_close/settle。worker不接管SUP结算。模型状态与进程退出状态区分，不吞异常伪造成功。
- 保留D3单机/单交互会话、源→活动→操作锁序、G/SID、保守折叠、最近G/C幂等；不改仓储/迁移/取消合同。

D. 结果边界
- 调用结果与监督/结算状态分别可辨，绑定activity/operation/executor/G/scope/runTag；错身份、缺失、畸形、超限、旧窗口回执失败关闭。
- 返回ModelCallResult文本/JSON/tool plan/usage/错误码的有界形式，诊断/repr默认不泄露正文/秘密；保持既有SessionOutcome/IPC兼容或明确版本校验，不悄悄混改。
- SUCCEEDED仅表示模型调用结果，“模型已返回、尚未提交业务成果”须显式。它不证明活动成果生效、持久化或仍有提交资格；接收后到业务写入存在竞争，一次检查不能冒充原子提交。
- G3业务结果原子持久提交/幂等读取仍待后续合同，本卡不新增结果表或声称重启可取正文。取消/超时/旧代次晚到只按原账本纪律记诊断，不发布成有效学习/面试成果。
- 完成标准是受控内部one_call接线及证据，M-1/STEP008整体、UI、生产调用和完整G3不随之完成。

## 4. 允许范围、资源独占
允许修改backend/app/worker/内必要模块/新增小模块，不泛化平台；worker/__init__.py、capabilities/__init__.py必要导出。
允许新增backend/tests/test_worker_one_call.py、backend/tests/fixtures/task085/；既有test_worker_session.py及直接受接口变化的worker测试只做必要适配、保留断言。
允许Ndocu/evidence/task-085/、Ndocu/results/TASK-085-result.md。
只读：activities/repository.py、001—006迁移、runtime.py、capabilities业务实现、其余产品、083/084任务/结果/旧证据、正式docu和公共库。若这些只读合同确需改动，先完成无阻部分，交具体最小差异及理由，不自行扩大。
不安装/拉镜像/改锁、不改main/HTTP/资料/PDF/检索、不读用户数据、不提交/推送、不清理历史。本卡独占worker和所列测试，无并行写入/审计。
新测试控制代码置自身目录，不改旧runner；复用旧逻辑须复制必要部分并纳入当前hash。正式产品不依赖Ndocu或测试代码。

## 5. 验证与预算
新跨进程身份/载荷/结果链必须定向验证；D3成功不等于新接线成功。按影响一次基线批，普通失败在卡内定位/修正/定向复验，不逐项回传；不重跑D3八场景或079全套。
至少映射到实际test ID：
1. 正常one_call：真实gateway逻辑，真实或明示替身transport，恰好一次发送/返回；G/scope来自claim，operation与账本一致。
2. 新链相关的无余额/取消/来源失效/身份错配拒绝无发送；UNKNOWN不重发，不能只mock最终返回。
3. gateway超时/失败/UNKNOWN、TOOL_PLAN不执行、关门拒绝新调用；已有操作按原终态纪律收敛；配置/实际窗口不足拒绝不扩时。
4. 载荷边界/畸形/身份/旧G回执拒绝；秘密不泄漏argv/log/repr，缺配置无回退；idle必要回归。
5. 本卡专用PG+真实Windows Job组合：固定启动入口→SUP认领→worker→操作账本→结果→树零/句柄关闭→关门结算，断言R/S/G/操作状态、模型结果与监督状态分开。
6. 一项新业务在途的失败收尾（如合成transport延迟至硬截止），证明局部树停止/保守R/没有伪成功结果；不重跑全部D3故障。

分层：
- provider付费/真实网络调用0。成功响应可用测试专属transport替身，复用产品worker核心；自举/注入只在backend/tests。逐项披露替换边，不能称真实供应商连通。
- 固定生产launcher/worker入口仍需实际数据传递或失败关闭证据；若成功组合用测试自举，单列它与生产入口证据差异，不能替代全部入口验证。
- 不靠生产任意代码/endpoint放开满足测试；真实供应商未验证为已知边界。不用SQL字符串断言冒充PG，不把skip/None当通过。

离线额度：累计≤900秒，单命令≤60秒；一次通过不重跑。同一核心问题最多两次有据修正，仍失败升级。编译不写pyc，可用项目venv，按需要而非重复静态全扫。
真实额度：最多3批（首次+至多2次因修改/明确新诊断的受影响及未跑项续验），资源累计≤1800秒，至少留120秒收尾；单批≤600秒，真实Windows会话≤12。准备/失败/探针/等待/收尾计入，换进程/窗口不重置。
专用PG容器最多1个，仅用已存在本地镜像sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f；名称retrolume-task-085-onecall-<唯一后缀>、DB retrolume_task085_onecall、专用合成角色/新随机口令，1CPU/512MiB/pids128/restart=no/无特权/无宿主目录bind，仅127.0.0.1:55440，本任务独占卷。缺镜像/端口冲突/Docker不可用则交具体阻塞，不拉取/重启服务/停别人资源/建第二容器。
授权在这个新空合成库应用原001—006供测试，不重测历史迁移。核实DB身份；缺专用测试DSN应skip而非回退用户DSN，实际批skip不计成功。
manifest记精确CID/镜像/卷/端口/限额、PID+创建时间。Docker只读必要字段、不回显完整Env/秘密；083/079容器/卷/凭据不接触。
真实批必须有独立于被测进程的有界外层控制、精确Job/进程收尾、退出码；复用已验控制经验，并将全部直接源码/测试依赖纳入pre/as-run/post指纹。不能裸PID或广泛taskkill，不能靠挂死被测者自证成功。
归属、树零或资源停止未知先精确收尾并停止后续批，如实保留未知。结束stop本任务CID并核Running=false，保留容器/卷不删；记录实际起止/耗时/尝试，批exit不冒充场景独立exit。

## 6. 快照、独立审计、交付
先有限git status/diff保护原差异，改动前pre副本/hash；末尾出卡hash只是源码快照，漂移查归属，不覆盖。必要运行脚本和夹具也是冻结对象。
高风险停止/凭据/事务接线完成后必须独立增强审计，由编排另卡隔离Session；只给原始目标/标准/diff/源码/证据，不继承实现聊天自评。执行者不自签独立通过，普通修正不额外加逐次前置审计。
完成即停；主要模型/权限变更、新费用/用户库/依赖、未知资源无法安全清理、同一核心两次修正仍失败、预算上限触发交回，保留已有成果与精确缺口。
证据：pre/post/as-run hash、有限diff、测试与要求映射、命令/exit/耗时/尝试账、注入边界、原始脱敏日志、资源manifest及停止证明、复用证据适用范围。失败历史不覆盖。
结果保存D:/shspic/project_NO3_RetroLume-agent/Ndocu/results/TASK-085-result.md；证据D:/shspic/project_NO3_RetroLume-agent/Ndocu/evidence/task-085/。
报告TASK/R/STEP、实际执行身份、建议状态、接口/文件作用、真实证据、未完成/未验证/风险、合同偏差、正式文档建议、仅必要人工动作、下一步。正式docu/CHANGE由编排维护，不宣告M-1/STEP008/发布/G3完成。

## 出卡源码快照（SHA256）
backend/app/worker/worker_main.py  5d065b5e44b678c08dc34c9e611a5dcaaa2d0aa3ed2c6e588fe7a70ca25a1454
backend/app/worker/command.py  b0e91c3a2e65de19656b3c902df49a33bdd29dc135bc9c292e7732e300a5e273
backend/app/worker/gate.py  7e7588a58869038f53d850816c027aab00ecd1270d2c893d1fc4902978d32674
backend/app/worker/launcher.py  703ceb0344e21a174f3d70e81b05ede5635d700ed84f53e26e9ae70037d2acea
backend/app/worker/supervisor_main.py  98c420e75671b3ad1823ea5a72a3866221e7cb0fc1defe032feb0a5822afb145
backend/app/worker/supervisor_ipc.py  57be00aead15114673b180b1abb436dde10ef426a618d56f30d0031e3201ac96
backend/app/worker/session.py  eb514b5f76b0dc8b43ed8dfe116d2dc7be5a181011e1516faaa4d8005461d71c
backend/app/worker/windows_job.py  d04ed8f249106328d81147707451e6092c2d650c9199bd6c4989931d5249c596
backend/app/activities/repository.py  bca8283316f62216f5ba94959f5c36f8c3395301aeb9dc7f21a9b376f92e29a3
backend/app/capabilities/gateway.py  f57e3fe3e35ddab58e7e28e4ec1300b528f5ce6d55a2fb0d832525d06b547437
backend/app/capabilities/contracts.py  bca21efd268ba5119176f9c0e66c4ebd42db252db3c8f1c78ee701be56b2f07d
backend/app/capabilities/transport.py  1d80347e2e41434297dafedfc7123cfdafdb661f576672290108de191e55b656
