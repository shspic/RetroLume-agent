# TASK-085 / R-079 — STEP-006/008 受控单次业务调用接线

建议状态：**实现与卡内定向验证完成，待编排安排独立增强审计；未自签独立通过。** 已落地受信内部 `run_one_call` → 固定 launcher/SUP → 成功 claim 的 G/scope → worker → ClosingCallGate → ControlledModelGateway/PostgresAdmissionLedger → 有界未提交回执 → 树零、句柄关闭、原关闭/结算链。没有新增 HTTP、业务结果表、工具自动执行、供应商网络调用或付费。

日期：2026-09-28，Asia/Shanghai。项目根 `D:/shspic/project_NO3_RetroLume-agent`。关联 INT-002、NFR-002/003、SEC-001/002、MOD-003/007/008、FLOW-005、DATA-007。基线为需求 v1.1、架构 v0.48、执行状态 v1.68，Git HEAD `45951501d2741630a229762d6b2d3f4b34d7f702`，保留全部既有未提交差异。

实际执行身份：本窗口 Codex，系统提供标签为基于 GPT-6；执行 Agent/增强任务，不接管编排。客户端未向本执行上下文提供可核实的具体模型后缀、推理档位或与 TASK-083 窗口同一性的证明，因此不虚称已核实最高档或原窗口连续性；本次没有主动切模型、开新执行窗口或派子 Agent，没有重做 083。

已读取根入口与公共 `D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD`，公共规则修改时间 `2026-09-23T01:02:19.8371311Z`；执行者未加载 WORK/全阶段提示词，公共库零写入。本卡与公共规则冲突处依任务卡：只写本结果/证据，不写正式 docu/CHANGE。

## 交付及证据导航

所有以下相对路径均以本项目根为基准。

| 路径 | 内容 |
| --- | --- |
| `backend/app/worker/one_call.py` | 有限 OneCallInput、公开 run_one_call、身份/容量/回执校验与未提交语义 |
| `backend/app/worker/command.py` | 固定解释器/模块/cwd/任务枚举，仅增加受限随机 mapping 名 |
| `backend/app/worker/launcher.py`、`supervisor_main.py` | 协议 2、显式请求配置传递、SUP/业务身份分层校验，丢失或畸形回执失败关闭 |
| `backend/app/worker/session.py` | claim 后派生 worker 身份与不可后移 stop_ns；回执经校验后关闭映射，再走既有 Job 关闭/关门/结算 |
| `backend/app/worker/worker_main.py` | 真 gateway + 真 PG ledger + 兼容循环，经 Gate 最多一次调用；无配置失败退出，不回退环境 |
| `backend/app/worker/supervisor_ipc.py` | 1 MiB 有界映射、严格 JSON 帧、显式受保护 DACL、创建者清零与关闭 |
| `backend/app/worker/__init__.py` | 必要内部导出，保留 run_controlled_worker 导出兼容 |
| `backend/tests/test_worker_one_call.py` | 新合同、gateway、序列化、秘密默认 repr、配置/期限拒绝与入口回归 |
| `backend/tests/fixtures/task085/` | 本卡独立离线 runner、合成自举、PG/Windows 场景、外层控制和证据汇总脚本 |
| `Ndocu/evidence/task-085/pre/`、`pre-hashes.json` | 改前副本及依赖指纹，包括原 worker、只读 app、迁移、直接复用旧测试范围 |
| `Ndocu/evidence/task-085/task085.diff`、`post-hashes.json` | 相对改前副本的有限差异和最终源码指纹；worker 原本未跟踪，不能用空 git diff 冒充无改动 |
| `Ndocu/evidence/task-085/offline-01` 至 `offline-05` 的 `*-meta.json`、日志 | 命令、exit、实际耗时、as-run/post 指纹；失败历史保留 |
| `Ndocu/evidence/task-085/20260928T001119Z-77ba1b/` | 唯一真实批 manifest、原始脱敏 stdout/stderr、as-run/post 指纹 |
| `Ndocu/evidence/task-085/delivery-check.json` | 指纹归属、逐场景完成索引及预算汇总；不代替原始日志 |

既有 `gate.py`、`windows_job.py`、activities 仓储、runtime、capabilities 业务实现、001—006、`test_worker_session.py` 和旧 task083 fixtures 均未改；pre 指纹检查没有范围外漂移。未修改正式文档、083/084 任务/结果/旧证据、锁文件或其他产品。没有安装、迁移用户库、提交/推送、删除历史或资源。

## 接口、身份和结果语义

内部入口为 `run_one_call(ledger, config, activity_id, executor_id, operation_id, request, service, *, run_tag)`。request/service 为现有 ModelCallRequest/ModelServiceConfig，ledger/config 运行时限定现有 PostgresAdmissionLedger/SessionConfig。它返回 SessionOutcome；监督 `state`、结算和进程诊断独立于 `model_receipt.result.status`。

调用方必须显式提供 DSN、服务配置、请求和稳定 operation_id；入口不接受 G/scope。activity 使用规范 UUID，executor/operation 使用受限字符集，runTag 为受限 ASCII。SUP 成功 claim 后由 ActivityLease 构造 CallContext，传递实际 G/scope 与按 claim 前 t0、实际 W_eff 计算的 stop_ns。有效旧租约、无余额、取消、来源失效或短窗均不产生有资格出站的 worker；实际短窗不扩展 W。claim 身份不匹配直接失败关闭。

worker 使用 `psycopg_compatible_loop_factory`。服务网络 timeout 不能超过监督请求预算；整体 asyncio timeout 覆盖准入/发送/记账，此外 SUP 的硬 stop_ns 约束进程树。发送仍为 admit → mark_dispatch_started → transport → record，未改恢复器/事务/仓储。正常返回和 TOOL_PLAN 都只有一次 gate.call，工具计划仅返回，不调用 execute，也不续轮。

回执绑定 activity/operation/executor/G/scope/runTag，包含有限 ModelCallResult 文本、JSON、工具计划、usage、状态和错误码；SessionOutcome 默认 repr 隐藏整份回执，OneCallInput 默认 repr 隐藏请求与配置。schema、未知字段、重复 JSON 键、非有限 JSON、校验和、容量及身份不符均拒绝。SUP 只在整树退出、主 worker exit=0 后读取回执；错误或缺失不伪造成功。错误类型可诊断，异常消息/traceback 不跨业务进程输出。

**SUCCEEDED 只表示模型已返回、尚未提交业务成果。** 每份回执显式 `business_commit="not_committed"`，不是提交资格/授权票据，所有正文均是未发布的临时返回。原 begin_window_close 会推进活动 G，真实成功样例回执 G1/操作 G1、关门后活动 G2；不能据回执晚写学习/面试成果。取消/来源变化仍可竞争，单次身份检查不是原子业务提交。G3 原子持久提交/幂等正文读取依旧未实现，没有正文结果表或重启取回承诺。

IPC 显式升级到协议 2，旧协议 1 被拒绝；新增 SessionOutcome.model_receipt，不悄悄混用旧 shape。旧 083 的 v1 专属协议夹具不是新协议可直接执行的证据，不修改/重跑旧 runner。

## 通道容量、秘密及生命周期

- 使用 Windows page-file named mapping：总 1,048,576 字节，两个 524,288 字节槽；每槽头 36 字节（uint32 长度＋SHA-256），写前完整编码检查，最后提交长度。输入和回执业务封套另限 131,072 UTF-8 JSON 字节。
- 本入口要求服务 `max_request_bytes` 和 `max_response_bytes` 均不超过 65,536，DSN/key 各不超过 4096 UTF-8 字节；较大的现有服务默认值必须由受信调用者显式调小，不能默默截断或宣称支持原 2/4 MiB 上限。gateway 原有请求/响应限额继续适用。
- 随机名称固定为 `Local\\RetroLume.SUP.<32hex>`；不能传任意文件路径、exe、模块/函数或序列化代码。生产解释器/模块/cwd 保持固定。argv 只含任务与通道名，不含 DSN/key/正文。
- 映射使用非继承句柄、受保护 DACL `D:P(A;;GA;;;OW)(A;;GA;;;SY)`，授权对象所有者与 SYSTEM。信任边界是当前 Windows 用户和本机管理员/SYSTEM；**没有声称防御同一受信用户下的恶意进程**。随机名称/校验和不等于身份认证；checksum 只检测损坏。
- launcher 拥有 caller→SUP 映射，SUP 拥有 SUP→worker 映射；对端打开自己的 view/handle。worker 写回并关闭自身 view，SUP 在树零后读/验证并清零关闭自身映射，再关闭自有 Job/进程句柄，之后才 begin_window_close/settle。launcher 只在精确 SUP 退出后读取其回执，最后清零/关闭自己的映射。
- 未落临时凭据/正文文件，不扫描 `.env`，无隐式 DSN/key 回退。真实批凭据为新随机合成值，仅由控制者内存提供；Docker 容器自身配置需要持有合成 PG 口令，未 inspect Env、回显、写入 manifest 或复用旧凭据。短生命周期映射不保证 Python 堆或操作系统交换页的密码学擦除。
- 生产 provider 白名单、trust_env=False、禁重定向/隐式重试实现未变，未添加生产 transport/command 选择器。

## 验证与要求映射

离线均通过项目 venv 的 `-B -m unittest -v`，单个实际测试子命令均远低于 60 秒。offline-01 为 27 项一次影响基线；offline-02 为新严格回执/映射补项 4 项；offline-03 的新增往返断言失败，原因是 JSON Sequence 还原成 list 而非原 tuple，非正文丢失。一次修正为按合同 JSON 语义比较，offline-04 单项通过；同时把离线 runner 控制台输出改为使用已脱敏日志。offline-05 单项验证固定 main 的 idle 与 one_call 缺配置退出。没有重跑已通过的全套，失败日志未覆盖。

| 要求 | 实际测试 ID / 场景 | 证据与替换边界 |
| --- | --- | --- |
| 一次真实 gateway 流程、身份及账本绑定 | `OneCallTests.test_real_gateway_single_send_claim_context_and_redaction`；真实 `success` / `json` | 离线 ledger/transport 明示替身，断言 admit/mark/send/received 顺序及恰好一次 send；真实 PG 操作 G/scope/executor/operation 与回执一致，requests_reserved=1 |
| 新链无余额/取消/来源失效拒绝 | 真实 `no_balance` / `cancelled` / `source_invalid` | 真实 PG 和固定 SUP 核心；均 pid=None、无操作行、无模型返回 |
| 有效旧租约/身份错配 | 真实 `lease_conflict`；`test_frame_limits_tamper_and_schema`、`test_receipt_wrong_identity_generation_missing_unknown_and_overlimit` | 旧租约不认领/不生成 worker；operation、executor、G、scope、bool 伪代次等错误拒绝 |
| UNKNOWN/timeout/HTTP失败、同 operation 不重发 | `test_unknown_timeout_failure_denial_and_no_operation_retry`；真实 `unknown` / `unknown_repeat` | 使用真实 gateway；真实 PG 中原 G1 UNKNOWN 保留，新 G3 的同 operation 被拒绝，requests_reserved 仍为 1，不改 NOT_SENT |
| TOOL_PLAN 不执行 | `test_tool_plan_never_executes`；真实 `tool` | 工具 execute 替换为必失败哨兵；只产生 tool_plan/received，没有第二轮 |
| 关门/在途等待/不可重开 | `tests.test_worker_session.GateTests.test_gate_closure_waits_for_marked_before_send_and_never_reopens`、`test_gate_close_timeout_keeps_closed` | 离线定向保留断言；真实成功后 dispatch_closed=true、R=0、S=1 |
| 实际窗口/配置不足 | `test_missing_data_idle_and_actual_short_window`、`test_public_rejection_before_launcher_and_bounded_result_roundtrip`；真实 `short` | 配置 timeout 超限在 launcher 前拒绝；实际剩余窗口不足不构造 ledger；余额 W_eff=1 不启动 worker，保守 R=1，不扩窗 |
| 字节边界/畸形/旧回执/秘密 | `test_frame_limits_tamper_and_schema`、`test_input_bounds_and_fixed_argv`、`test_mapping_owned_lifetime_and_malformed_json`、`test_receipt_wrong_identity_generation_missing_unknown_and_overlimit` | 精确槽上限、超一字节、校验和、重复键/NaN、身份、超限、映射最终销毁；默认 repr 隐藏正文/key |
| 有界正文/JSON/计划/usage 回传 | `test_public_rejection_before_launcher_and_bounded_result_roundtrip` | pack/unpack→ModelCallResult→SessionOutcome 协议2完整 JSON 语义往返，无截断 |
| 显式配置、旧协议及未知字段拒绝 | `test_sup_protocol_roundtrip_and_missing_configuration`、`test_fixed_worker_idle_and_missing_configuration_fail_closed` | 缺 one_call 数据不转 idle；无配置直接 exit2，未构造 ledger；idle main exit0 |
| 固定生产入口实际数据传递/失败关闭 | 真实 `production_rejected` | **未替换启动模块/argv/transport**。固定 launcher→SUP→worker→真实 gateway/PG；活动未授权该模型，REJECTED，无操作/发送，监督仍 settled |
| 专用 PG+Windows 成功组合 | 真实 `success` / `json` / `tool` | 仅测试自举替换 SUP 启动模块、worker argv 和 HttpxModelTransport.send；产品 SUP/worker/session/gate/gateway/PG 核心不替换，R/S/操作终态/树零/Job 销毁有断言 |
| 新业务在途硬截止 | 真实 `hard` | 测试 send 内同步阻塞至超出硬截止；真实 PG 已 dispatched，SUP 在约 9秒杀局部树，state=stopped_at_deadline、树0、回执None、R=10/S=0、未伪造 received/成功 |

真实成功组合的替换边只存在 `backend/tests/fixtures/task085/bootstrap.py` 和 `real_cases.py`，产品不导入测试或 Ndocu。独立外层控制来自 083 已验 controlled_child 的必要复制，现置于 task085，纳入当前指纹；没有修改/调用旧 runner。**这不是供应商连通性验证**：provider 网络与费用均为 0；生产固定入口仅证明真实输入传递与拒绝出站，成功响应来自测试 transport。离线 gateway 原有失败/取消/响应限制测试按影响随首批运行，没有拿最终返回 mock 冒充 gateway 流程。

真实批 12 个精确 ID 的 start/result/complete 齐全，唯一总 complete、批 exit0，外层实际进程 exit0；没有把批 exit0逐项伪装为 12 个独立场景进程 exit。每次 SUP 身份与实际 worker（若有）的 PID+创建时间见原始记录。测试 skip=0、无 None 冒充成功；None 仅在应拒绝/硬停止场景作为期望回执不存在。

`lease_conflict` 的 SessionOutcome.cleanup_incomplete=true 是既有 SUP 对未启用自动恢复、旧运行窗的保守诊断；夹具只创建了数据库租约，从未创建对应旧 Job/worker，新调用也没有 worker。它不是“旧树已清理”的证据，不被报告成 settled。该已知合成无进程前提与外层树零分开记录。新建资源未出现归属/停止不明，批末 cleanup_incomplete=false。

## 实际预算、资源与冻结

唯一真实批起止 `2026-09-28T00:11:19.601355Z` 至 `00:11:55.142761Z`（以 manifest 实际字段为准），含镜像/端口核对、创建/准备/就绪等待、运行、精确收尾，35.532 秒；真实批 1/3，SUP 会话 12/12，其中 7 次实际启动 worker。独立外层硬总窗 480 秒，至少 120 秒预留；观察到约 25.4 秒即外层树零/句柄关闭。没有再次启动资源，未用额度不是继续运行授权。

离线测试子命令累计 5.469 秒（2.781 + 0.765 + 0.657 + 0.641 + 0.625），5 次定向命令，1 次夹具断言失败/1 次有据修正；无产品核心失败。脚本编写/只读源码整理不冒充测试时耗；真实资源动作全部在上述单 runner 计时内。没有 D3 八场景或 079 全套重跑。

- CID：`f67f57cd43914c05c192282f438afa193ca97b68b29912c538d9f27d741eb7a3`。
- 名称：`retrolume-task-085-onecall-20260928t001119z-77ba1b`；唯一卷 `retrolume-task-085-20260928t001119z-77ba1b`。
- 镜像：`sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f`，已存在本地镜像，未拉取。
- DB：`retrolume_task085_onecall`；合成角色 `task085_8e1596ac`，新随机口令未写证据；仅在该新空库应用原 001—006，没有重测历史迁移。
- `127.0.0.1:55440`，1 CPU、512 MiB、pids128、restart=no、privileged=false、no-new-privileges，无宿主 bind。
- 外层进程 PID `27412`，creation time `134350278889701065`；外层 Job 的精确句柄从悬停创建→Assign→Resume→树零→关闭全程持有。
- manifest 记录 `docker stop --time 10 <精确CID>` exit0，随后 `State.Running=false`；容器与卷停止保留，未删除。只在记录时点确认停止，不宣称后台持续监控；083/079 容器/卷/凭据零接触。

真实 as-run/post 源码完全一致。真实批后产品源码未变，最终新增/变化仅为新增回执/idle离线断言、离线 runner 的输出脱敏，以及不运行测试/资源的 finalize_evidence 汇总脚本；逐项列于 delivery-check。新断言实际执行通过，不用最终测试文件 hash 反向冒充真实批当时文件。原始 as-run/hash/日志保留。

## 未完成、风险、偏差及编排下一步

1. 必须由编排另卡、隔离 Session 安排增强独立审计；本报告不是独立通过。审计输入用原 TASK-085 目标/标准、本卡有限 diff、最终源码、pre/as-run/post 和原始日志，不让实现聊天或本人的结论替代审计。
2. 未验证真实供应商成功出站、生产成功响应，未启用费用；当前成功组合的测试自举差异已明确。Linux、UI、HTTP、完整业务提交/结果持久化、M-1/STEP008整体和发布均未完成。
3. 同用户权限边界、SHA 非认证、内存非密码学擦除、默认服务大载荷不适用于本入口，是显式合同限制。进程硬杀时 PG 操作可保持 dispatched、R 继续占用，留给原恢复纪律，不擅自改 UNKNOWN/退款。
4. 已关闭 083/084 的 D3 单机单交互会话、锁序、最近 G/C 幂等等仅按未变依赖复用。session 新增接线和协议2以本卡证据为准；旧批准不自动覆盖新秘密/结果通道。
5. 没有发现必须修改只读仓储/迁移/runtime/capabilities 的合同障碍；没有提出扩大权限、安装或付费要求。执行标签/窗口连续性未能独立核实如实披露，不据此自称满足不可观察的配置证明。
6. 正式文档建议由编排在审计后登记：TASK085 内部单次调用切片及新映射协议2、64 KiB入口限制、结果未提交语义、上述验证/平台边界；保留完整 G3、G4、M-1/STEP008 及生产连通性缺口，并登记本结果/证据关联 CHANGE。执行者未代写正式文档。

必要人工动作仅为既定任务结果转交；无需用户配置真实凭据、启动 Docker、再次测试或清理资源。本卡执行到此停止，等待独立审计与编排裁定。
