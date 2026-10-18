# TASK-075 补充01（supplement-01）读取范围与只读声明

- 日期：2026-09-21（Asia/Shanghai）。执行者：Codex Sol（C 档，原会话续作）。
- 本补充由 Astra 验收 075 原结果（部分通过）后发出，不占新 TASK/R；原 075 结果与证据不覆盖、不修改。
- 全程只读产品代码与文档；未运行测试、Docker、PG、应用；未联网、未安装依赖；未修改产品/测试/DDL/锁/正式 docu。
- 仅写入：`Ndocu/results/TASK-075-supplement-01.md` 与 `Ndocu/evidence/task-075/supplement-01/`（本文件、read-hashes.txt）。

## 本补充新读取文件（SHA-256 见 read-hashes.txt）

- Ndocu/results/TASK-075-result.md（原结果全文复核，确定修订点）
- backend/tests/test_activity_ledger.py（L80-160 段：ActivitySpec 构造 L95/L154、claim_lease L97、cancel_activity L193 调用事实）
- backend/tests/test_activity_recovery.py（rg 定位：ActivitySpec L112/L276、claim_lease L126/L156/L293）

## 复用已读事实（075 主卡 read-scope.md，不重复读取）

- repository.py / 002_activities.sql / gateway.py / contracts.py / runtime.py / _windows_job.py / supervisor.py / main.py / TASK-060-result.md / 074-result.md / 架构 v0.25 / LATER_REQUIREMENTS v1.1 / 执行状态（含 v1.19 变更后口径以卡面描述为准，本补充未重新读取执行状态全文）。
- 新增定位检索：`ActivitySpec\(|claim_lease\(|cancel_activity\(|recover_unknown\(`（backend/tests）。

## 声明

- 本补充全部内容为未实施方案：未实施任何代码/DDL/接口变更，未动态验证任何时钟/监督/结算/竞争行为。
- 各竞争/幂等场景的"结果"是设计校验逻辑推演（依据=给定校验链+既有同型机制定位行号），不是已验证事实。
