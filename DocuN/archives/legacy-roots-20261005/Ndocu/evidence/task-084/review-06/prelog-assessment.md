# TASK-084 review-06 prelog — 接触顺序与初判时点披露

日期：2026-09-25；性质：R-078 review-06 独立增量终审（09完整成果），GLM-5.3-Flash 窗口，未参与 083 代码/测试实施，不接管实现。

## 实际接触顺序（如实登记）

1. 工作记忆/任务卡（R-078 review-06 合同）→ Ndocu/tasks/TASK-083.md（09完整合同）。
2. **先读原始源码独立判断**（读任何证据与实现者自述之前）：
   - backend/tests/fixtures/task083/launcher_control.py（全文）
   - backend/tests/fixtures/task083/launcher_scenario.py（全文）
   - backend/app/worker/launcher.py（全文，注入边界核对）
   - backend/app/worker/supervisor_main.py（全文，SUP 主循环）
   - backend/app/worker/windows_job.py（全文，Job/互斥语义）
3. **再读 09 证据**：results.json、batch-meta.txt、runner.py、runner-log.txt、manifest.md、post-run-check.json、两轮 p-evidence/p-stderr 四组、batch-stdout.log。
4. **后读待评声明**：Ndocu/results/TASK-083-result.md 置顶段（09 完整成果自述）→ Ndocu/results/TASK-084-result.md（review-03/05 复用边界）→ d3-sources-and-decision.md（D3 提案）→ 082-work-decision 批准段（Grep 定位批准边界）。
5. hash 独立复算（托管 Python hashlib，12 文件，只读）——第 1-3 块初判在此时已成形；D3 逻辑初判在读官方页前成形。
6. D3 支柱官方页有限抽查（≤3 页，WebFetch 只读，验证决定性原文；S2/S5 未重开，按摘录内部一致性评估并如实标注）。

未读实现聊天；未运行 AST/import/compile/单元/Job/spawn/PG/Docker/安装/模型/私有配置，未运行任何实现者脚本。本轮执行的两类操作：托管 Python hash 复算（只读）、官方页 WebFetch（卡面唯一网络范围）。写入仅限本目录与 Ndocu/results/TASK-084-result.md 置顶 review-06 段。

## 初判要点（读实现者自述与 D3 提案前/后时点标注）

- 第1块（注入语义、屏障位置、覆盖分级）：源码+证据阅读后、读 083 自述前成形。
- 第2块（观察者效应、句柄清单、B 结果独立性）：源码+证据阅读后成形。
- 第3块（尝试账、日志覆盖、预算口径）：manifest/post-run-check/runner-log 后成形。
- 第4块（D3 充分性）：launcher_control/scenario/windows_job 源码 + d3 提案阅读后成形；官方页抽查仅验证 S1/S3/S4 决定性原文。
