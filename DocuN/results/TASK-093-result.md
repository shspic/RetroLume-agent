# TASK-093 / R-087 G5有限工具完整成果集中独立审计结果

## 1. 限定结论

代码：通过。B1—B10 合同与 A—E 判据对最终源码静态逐条对照，未发现违背合同的产品实现；未发现确定产品缺陷（P0—P3 均无新增）。

证据：基本齐备，存在两项确定缺口，均判非阻断。C2 的 2048 字节参数边界无用例（实现有检查，合同明确列出的该反例项未验证）；real-01 以旧版测试夹具执行 15 例通过且旧版原件未存档，最终版 PG 测试全量通过无可证（产品代码五批 hash 一致缓解）。

执行控制：符合授权。容器/镜像/卷/端口/资源限制逐批与授权参照一致；预算与次数在累计上限内；五次尝试（含三次失败）与冻结时间矛盾如实保留；敏感信息口令走 psql stdin 轮换、清单内 psql 命令脱敏。

整体切片：具备交编排验收条件，边界为 G5 受控工具完整批准切片（B1—B10 对应实现与验证），附第 6 节两项缺口的处置建议。本审计不宣告 STEP006/008 完成、不签 M-1、不构成发布通过，不填写编排最终验收。

## 2. 审计身份、隔离与接触披露

执行者 A+，GLM-5.3-Flash（如实登记实际身份，未冒称其他型号）。全新隔离会话，2026-10-01 03:05 起，未参与 091 设计或 092 实现/修复，未读取 TASK-092-result.md、TASK-092-work-decision.md、实现者聊天、编排自评及 orchestration-review 正文。input-snapshot 仅作身份索引用于 hash 核对，未按其读取任何被禁文件。偶然接触披露：会话启动时注入的项目工作记忆含 TASK-088 及更早历史摘要（G3/D3 边界），本审计未据此复用任何未验证结论，旧边界仅按卡面第 5 条定向引用。客户端共享 MEMORY 与完整历史聊天未读取。运行预算 0：全程仅文件读取、hash 计算、文本搜索与 diff，未 import 产品、未执行被审代码、未触 Docker/PG/Windows/网络。

## 3. 快照与输入身份

源合同 TASK-091-result.md 实测 SHA-256 a6dfdd231ea1cac76497c1a6c3dd77a77e7b653cac2231850d95d49128c92866，与卡面一致；approved-contract.md 为其 B1—B10/C1—C12 原样摘录（实测 806497ef…9fa44c9e，为摘录件自身值）。input-snapshot 列 120 个证据文件逐个 SHA-256 匹配，零缺失零漂移。当前工作树 21 个产品文件与快照完全一致，审计批期产品冻结成立。锁定规则索引 rules-snapshot.json 已读，公共 AGENTS.MD 按锁定版本读取。

## 4. 实际差异范围

17 改 4 不变，与 final-product-hashes.json 一致。新增 5 文件：capabilities/tool_execution.py、worker/one_tool.py、migrations/008_activity_tool_budget.sql、tests/test_activity_tools.py、tests/test_worker_one_tool.py。修改 12 文件：activities/repository.py 与 service.py、capabilities/__init__.py 与 contracts.py、worker/command.py、launcher.py、session.py、supervisor_main.py、worker_main.py、tests 三件（test_activity_continuation/test_activity_results/test_worker_one_call，改动均为 kind='model' 合成快照适配与外 2 字段集适配，无断言弱化）。未变 4 文件：activities/__init__.py、worker/one_call.py、test_capabilities.py、test_worker_session.py。001—007 迁移未改（real-04 as-run hash 与 088 时代冻结值一致）。final-diff.patch 为自定义格式（pre原件 vs 工作树），非 git diff 头，内容与上述一致。

## 5. A—H 与 C1—C12 覆盖索引

A 持久次数与 008：008 文本与 B2 逐条一致（三具名 CHECK、kind_shape 总条件、pg_constraint 唯一识别匹配数不等于 1 即回滚、全约束当次验证、重复执行命中 008 自身 RAISE）。ActivitySpec.max_tool_calls 严格 int 拒 bool、0..2147483647、None 未配置（repository.py 321—326）。admit_tool_operation 锁内先比较上限再 +1（1163—1168），tools_reserved+1 与 INSERT kind='tool' 同事务。unknown 收敛不退款、模型计数不混用由 C3/C6/C10 断言。证据 real-01 C1 两例、real-05 s1/s2/s3。

B 输入与授权：服务入口一次读取 Mapping 到私有浅拷贝（service.py 58—76），_OnceMapping 离线证明单次读取且后续变异免疫；to_wire/from_wire 重复键、NaN、非规范字节、伪造摘要、额外字段全拒（offline + real-01 C2）；专用凭证类型隔离双向拒绝（旧 AdmissionPermit 包装工具准入拒、工具凭证操作 model 行拒，C2）；_locked_operation 默认 kind='model'，_tool_identity_matches 锁内 kind='tool' 全字段对齐；执行无网络/文件/命令（tools.py 未变，bootstrap 注入 forbidden_send/forbidden_execute 反证）。

C 状态与原子性：C6 用真实 PG 触发器在 COMMIT 前失败、用子类在 COMMIT 后丢响应，分别观察 reserved/dispatched 与 T1；C7 record 前失败保持 dispatched 无正文、恢复 unknown 后同成功结果不能覆盖也不能 ALREADY_PRESENT；C8 ALREADY_PRESENT 经 xmin 不变证无写；C4 两连接 Event 屏障至多一凭证、胜者崩溃执行 0 而 T1；C12 close 丢响应后 ALREADY_CLOSED 确认、settle 同 G/W/C 一次、异 C 拒绝、业务 UNKNOWN 与时间结算独立。record_tool_outcome 与模型共用 _terminal_confirmation/_write_outcome/_operation_is_current 核心且凭证分离；模型 record_outcome 与 mark_dispatch_started 锁内 kind='model' 复核（cross-kind 拒绝由 _locked_operation 保证）。

D 消费隔离：read/list 同一 SQL 权威 JOIN 投影 kind/tool_call_id/arguments_sha256/tool_names，调用方不输入 kind；失效分支 SQL 内抑制正文；kind=tool 时 read 与 list 双复查 _tool_payload_semantics_ok（text 封套内原精度 50 规范有限十进制、绝对值 1e18 上界、规范化逐字节相等），失败抛 ResultIntegrityError；NO_OPERATION kind=None 不伪造。service 与仓储锁内双层拒工具父（C5），合法 model 父对照正常；list 轻量元数据 256KiB 预算保留。服务不 claim/execute/close/settle（service.py 无相应调用）。

E 固定受控链：one_tool 经 run_supervised_window（真实 _SuspendedSupervisor 停止/句柄主体）→ bootstrap 包装的真实 supervisor_main.main（真实 claim/Job/树零/关门/结算）→ bootstrap 包装的真实 worker_main.main（仅 ToolRegistry.execute 边界计数或阻塞替换、transport.send 禁止）；外 3/内 4 与外 2/内 3 帧全部由产品代码生成与解码。real-04 六方向实证：tool_chain execute1/T1/model 计数0/树零/job 消失(open_error 2)/关门/结算 G1→G2/read committed_current/payload hash 一致；tool_stop 阻塞 600 秒被 SUP 截止硬停、stopped_at_deadline、R=10 全额保留、T1 不退、无伪正文；tool_recovery 同会话接续 G2 新键成功、旧 R 只折叠一次、旧操作 unknown 不重执行；old_sup_reject 旧副本（pre hash c329e531/5372ac4b 与 pre 原件一致）拒外 3 无 claim 零预扣；old_worker_reject 旧 worker 退 2、worker_failed_full_reservation、R=10 如实保留 T=0（符合 B6 不宣称混用零时间预扣）。

F 证据完整性：C1—C12 逐项映射见 DocuN/evidence/TASK-093/audit-verification.json。用例未到达分支、反例同源、缺断言、mock 代真实事务的专项检查未发现（C6/C7 故障注入位于真实事务提交点，C4/C9 用事件屏障非 sleep）。缺口见第 6 节。

G 包装与适用：真实工具计算（计数真实 execute）、真实 PG（专用合成库与角色，身份断言 current_database/current_user）、加载捕获（bootstrap 记录 19 个 app 模块实际加载字节，抽查 8 项与最终版全等）、合成 transport（一次发送禁重发）、同步阻塞替身（sleep 600 停止反例）、旧版行为副本（正反照证明副本为旧逻辑而非一律拒绝）分别定界成立。每批 as-run 与最终版独立核对，未用最终 hash 回填旧批；real-01 测试文件差异如实保留。

H 尝试账与收尾：5 次真实尝试（real-01 exit1、real-02 预检失败未运行、real-03 exit1、real-04 exit1、real-05 exit0）与 2 次离线全量加 3 次定向离线检查全部原样保留；scenario-manifest 顶层 frozen_utc 与 real-01 实际时间的不一致由 attempt-ledger 显式披露为书写投影值且不回改。real-04 upgrade_child 失败后 windows_child 继续，child_finalized 两者 clean，与冻结清单"失败不清空后续场景、清理不全才停止"一致。五批 container_stopped=true、cleanup_incomplete=false、new_containers=new_volumes=0、paid=0、network=0。

## 6. 确定问题、覆盖缺口与最小补证

确定缺陷：无。

缺口一（覆盖缺口，非产品缺陷，严重度评估为不影响 G5 门槛的低风险缺失）。C2 合同要求"大小 2048 边界"逐项检查，test_activity_tools.py 与 test_worker_one_tool.py 均无 2048 字节边界用例；实现侧检查存在于 canonical_tool_arguments（contracts.py 464）与 ToolExecutionInput.to_wire（493）。触发与影响：恰好 2048 字节与 2049 字节参数的实际接受/拒绝行为无 A 级证据；越界参数在 admit 前即被 to_wire 拒绝，不触及持久层，风险限于输入边界回归。最小修复：离线新增两例（2048 字节规范参数通过、2049 拒绝 tool_arguments_limit），属纯离线补充，不需 PG；最小复验范围仅该两例加 offline-01 口径重跑。

缺口二（证据适用性缺口，非阻断）。real-01 以旧版 test_activity_tools.py（eecba489…）执行 15 例通过；real-03 仅对修复的 c7/c9 两例以最终版（fc6da437…）真实 PG 复验；最终版其余 PG 用例（C2/C3/C4/C5/C6/C8/C12）从未整体在真实 PG 重跑，且旧版原件未存档，无法逐字排除其余用例在两版间被动过。缓解事实：产品代码五批 hash 一致（含迁移），real-01 stderr 保留逐用例输出，失败两例均为夹具构造缺陷且 traceback 显示产品行为正确（scope_changed 为产品在正确拒绝旧 context）。最小补证选项（交编排裁量，不实施）：以最终版测试对 retrolume_task092_tools 库做一次定向全量复跑，或由编排确认接受"产品行为五批一致 + 逐用例名单相同 + 失败两例修复复验"的推理链并登记残余风险。

## 7. 非阻断观察

一，Windows 场景中 SUP 侧 WorkerCommand.argv 被 bootstrap.test_argv 替换，worker 进程由 bootstrap.py 启动后导入真实 worker_main.main 执行；argv 非产品固定形态属场景注入必要，实际执行字节由加载捕获补偿，包装保留了身份、序列与停止控制（launcher _SuspendedSupervisor 主体未替换）。

二，old_worker_reject 场景 R=10 未结算保留、old_sup_reject 场景 cleanup_incomplete=true（launcher 失败路径如实标记），均为设计内如实记录，不构成执行违规。

三，real-02 的 state 记为 finished 而 exit 为 null（预检失败未运行子批），账目含义依赖 attempt-ledger 文字说明，建议后续 runner 统一 exit 语义。

四，real-01 与 real-03 的 manifest 中 psql -U retrolume_task088_synth 明文出现角色名（非口令），口令本身走 stdin 轮换未落 argv/日志，符合脱敏纪律；记录角色名可接受。

## 8. 预算、执行控制与收尾事实

真实累计 61.452 秒 / 3600 秒，容器启动 5 次（原卡 3 + 续作01 +1 + 续作02 +1，累计上限 6），Windows 会话 7 次（real-03 一次 + real-04 六次，上限 12，续作02 新增 0），离线 6.655 秒 / 1800 秒，付费与网络 0。单批时长 16.6/1.8/7.5/27.1/8.4 秒均远低于单批上限。五批运行前后产品 hash 零漂移；容器终态 Running=false 保留（未删除，归属与身份快照在案）。本审计运行 0、批期 0、无并行写入；审计自身仅新增 DocuN/evidence/TASK-093/audit-verification.json 与本结果文件，未覆盖编排两文件，未改任何产品或 092 证据。

## 9. 未验证项与建议下一步

未验证：任何动态行为的当前重放（运行预算 0，全部结论基于既有原始证据与静态结构核对）；最终版 PG 测试全量绿（缺口二）；2048 边界（缺口一）；真实生产部署形态（部署统一切换为运维前提，未在验证范围）。

建议下一步：交编排验收 G5 切片时附第 6 节两项缺口与最小补证选项，由编排裁定补证方式与是否需要沿唯一实现路线开修复卡；缺口一可并入任意后续离线窗口低成本补齐。旧 D3 批准门与四容器处置仍按 084 review-06 待用户决定，不在本卡范围。
