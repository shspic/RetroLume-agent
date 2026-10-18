# TASK-062 受控入口ID契约一致性与准入异常可诊断性 — 结果

任务：TASK-062 / R-056；类型：开发；STEP-006；父 TASK-060；关联 TASK-058/046、SEC-002、NFR-003、MOD-007、API-006。
执行者：Work Buddy（GLM-5.3-Flash），B档，新会话；实际模型标签 GLM-5.3-Flash。
日期：2026-09-21（Asia/Shanghai）。项目根：D:/shspic/project_NO3_RetroLume-agent。
基线：需求文档 v1.1、架构 v0.18、执行状态 v1.5。原始开发范围已授权；无真实模型调用授权，全程未调用任何供应商。

## 1. 建议状态

部分目标完成并已验证（离线范围）：L-1 与 L-3 均已实现并通过离线契约测试。本卡不声称完成 STEP-006，不声称真实供应商兼容，不涉及 M-1 时钟问题（保持开放）。

## 2. 实际差异

### L-1（backend/app/capabilities/contracts.py）
- CallContext 的 operation_id/executor_id 增加 pattern `^[A-Za-z0-9._:/-]+$`（与 activities/repository.py L26 _SAFE_FACT 同一字符集，长度保持 1—128）。
- activity_id 新增 field_validator：必须可被 `uuid.UUID(value)` 解析（与仓储 _uuid 的"UUID 可解析"语义一致）；只校验不改写，不做静默规范化，字段仍为 str、长度限制不变。
- 三个 ID 字段外部类型（str）与既有长度限制均未变；未新增公开字段，未改公开数据结构形状。

### L-3（backend/app/capabilities/gateway.py）
- admit→permit_check→mark_dispatch 三阶段用 stage 变量跟踪。
- 异常区分：AdmissionDenied → "admission_denied"（原码保留）；AdmissionUnavailable → "admission_unavailable"（原码保留，含 _validate_permit 不匹配路径）；其余意外异常 → 新稳定码 "admission_internal_error"，仍 REJECTED 且不发送。
- 意外异常记录本地脱敏诊断日志（logging.getLogger(__name__)，warning 级）：稳定事件码 admission_internal_error、uuid4().hex 随机关联标识、阶段、异常类型名（type(exc).__name__）。不记录异常消息、traceback、局部变量、密钥、请求正文、资料或完整 ID；未使用 logger.exception。
- 未新增公共结果字段；保留 mark 失败的保守账本语义（不退款、不重发、不假记业务成功）。已预留但 mark 意外失败现在归入 admission_internal_error（原先被折叠为 admission_unavailable），行为仍是 REJECTED + 不发送。
- 未改 transport、序列化、预留口径（L-2 已被 060 否定）；未触碰其他异常路径与费用口径。

### 测试（backend/tests/test_capabilities.py）
- 替身样本 "activity-1" 换成固定合成 UUID `3f2b8c64-1d4e-4f5a-9b6c-7e8d9a0b1c2d`（仅本测试文件）。
- 新增 test_call_context_rejects_ids_violating_ledger_contract：非法 UUID（含 activity-1、缺一位伪 UUID）、空白、中文 operation/executor 均在 CallContext 构造时 ValidationError；有效组合通过。
- 新增 test_unexpected_admission_errors_are_distinguishable_and_sanitized：admit 与 mark_dispatch 意外异常均返回 admission_internal_error 且 transport 发送次数为 0；日志含 stage=admit/mark_dispatch、exception_type=RuntimeError、两个不同的 32 位十六进制 correlation_id；含合成秘密的异常文本不泄漏到日志。
- 强化 test_dispatch_or_admission_failure_prevents_network：deny 断言 admission_denied，mark 意外失败断言 admission_internal_error（原断言 REJECTED + 零发送保留）。

## 3. 真实命令与结果

命令（均为实际执行，cwd=backend，使用项目现有 venv，未安装任何依赖）：
- 基线：`./.venv/Scripts/python.exe -m unittest tests.test_capabilities -v` → Ran 13 tests, OK, EXIT=0（改动前）
- 改动后同命令 → Ran 15 tests, OK, EXIT=0（0.137s，远低于 120 秒上限）
- hash 计算：`backend/.venv/Scripts/python.exe` + hashlib.sha256（改动前后各一次）

运行一次通过，未动用修正复检机会。transport/ledger 均为进程内替身，使用合成数据；未启动 PG、Docker、浏览器、应用，未联网。

## 4. 证据路径

- Ndocu/evidence/task-062/hash-before 记录：hashes-before-utf8.txt（改动前 hash）
- Ndocu/evidence/task-062/hashes-after-utf8.txt（改动后 hash）
- Ndocu/evidence/task-062/baseline-run-utf8.txt（基线 13 通过）
- Ndocu/evidence/task-062/after-run-utf8.txt（改动后 15 通过，含一条真实脱敏日志样例）
- 原始重定向文件 baseline-run.txt / after-run.txt / hashes-after.txt 为 PowerShell 默认编码，内容与上述 UTF-8 版本一致。

## 5. 未验证与风险

- 未运行 test_activity_ledger.py 等其他套件（卡限定仅 test_capabilities 一批，既有 051/055 PG 证据不重跑）。只读核对确认该文件 activity_id 来自 ActivitySpec（仓储本身要求 UUID）、operation/executor 样本匹配新字符集，预期不回归，但此为静态判断非运行证据。
- admission_internal_error 只覆盖 admit/permit_check/mark_dispatch 阶段意外异常；record_outcome 意外异常仍走既有 ledger_record_failed → UNKNOWN 路径（卡要求不顺手处理其他异常路径，未改动）。
- CallContext 契约收紧属于公开行为变化：今后任何以非 UUID activity_id 构造 CallContext 的调用方将在契约校验时被拒。当前仓库内仅测试构造 CallContext，无产品接线调用方（应用接线本就未完成）。
- 日志为标准 logging，项目当前未配置 handler 时默认输出到 stderr（测试输出中可见），格式与脱敏范围已验证；正式日志接线属 G-6/worker 接入卡范围。
- 本卡为实现与局部验证，不是独立审计；整体受控入口审计与真实组合门槛保持未关闭。

## 6. 需求/架构影响

- SEC-002/NFR-003：无效 ID 在契约层明确拒绝，异常三分类可区分，保持失败关闭与不发送；与 MOD-007/API-006 的入口契约一致，无接口形状变化。
- FLOW-005/STEP-006：本卡只关闭 058 的 L-1/L-3 两项局部缺口；STEP-006 剩余前置（真实供应商返回兼容验证）与 M-1 时钟缺口保持开放。
- 046 离线证据中 "activity-1 非 UUID 亦通过" 的旧口径不再成立，新口径以本卡测试为准。

## 7. 文档建议（交 Astra，本卡不改正式 docu）

1. CALL 契约/架构文档补 CallContext 的 activity_id UUID 可解析、operation_id/executor_id 字符集 `^[A-Za-z0-9._:/-]+$` 约束（060 §9.2 已建议）。
2. 错误码清单补 admission_internal_error：含义、与 admission_denied/admission_unavailable 的区分、日志定位方式（stage + correlation_id + exception_type）。
3. 执行状态 TASK-062 行验收留空，待 Astra 核对本结果与证据后裁定。

## 8. 必须人工操作

无。本卡全部工作在允许文件与离线测试范围内完成，无安装、无 Docker、无真实调用、无 Git 操作。

## 9. 下一步（供 Astra 裁定）

- 验收本卡并同步执行状态；L-1/L-3 关闭后 STEP-006 剩余真实供应商兼容验证需另立真实调用卡（需费用授权）。
- 下次真实 PG 运行卡可一并回归受影响用例（060 §7.4 同一逻辑：契约收紧触及账本定位入口）。

（Astra 最终验收结论留空）
