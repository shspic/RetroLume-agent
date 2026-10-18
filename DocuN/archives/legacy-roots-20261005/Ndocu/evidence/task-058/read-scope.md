# TASK-058 只读审计读取范围与独立性记录

日期：2026-09-20（Asia/Shanghai）。执行方式：全新独立会话（未参与 TASK-046/051/055/056/057 任何实现或运行），只读。

## 实际读取（全部只读）

规则与合同：

- AGENTS.md；docu/AGENTS.MD
- Ndocu/tasks/TASK-058.md、TASK-046.md、TASK-051.md、TASK-055.md、TASK-056.md

需求与架构（仅相关条目）：

- docu/LATER_REQUIREMENTS.MD（SEC-002、NFR-002/003、DR-003 及其余上下文）
- docu/PROJECT_ARCHITECTURE.MD（FLOW-005 与原子准入补充、DATA-004/007、API-006、第6/7/8节相关段）
- docu/PROJECT_EXECUTE_STATE.MD 顶部当前入口与 TASK-055/056 登记段；docu/CHANGE.MD 前 60 行（确认其只登记文档、不登记源码）

被审源码（核心）：

- backend/app/capabilities/{contracts,gateway,tools,transport,__init__}.py
- backend/app/activities/{repository,__init__}.py
- backend/migrations/001_materials.sql、002_activities.sql
- backend/app/runtime.py；deploy/start_local.py；deploy/start-backend.ps1
- backend/app/materials/repository.py（只读版本原子更新语义）；backend/app/main.py（只读应用组合确认）

测试与原始证据：

- backend/tests/test_capabilities.py、backend/tests/test_activity_ledger.py、tests/run_ledger_check.py（源码）
- Ndocu/evidence/task-046/{protocol-source.md, verification.md}
- Ndocu/evidence/task-051/{verification.md, command.txt, environment.txt, source-hashes.sha256, ledger-check-final.stdout.log}
- Ndocu/evidence/task-055/{verification.md, command.txt, static-check.txt, environment.txt, source-hashes.sha256, ledger-check.stdout.log, ledger-check.exit-code.txt, container-after.txt, timing.txt}

## 明确未读取（保持独立性与范围）

- Ndocu/results/ 下全部结果文件（含 TASK-046/051/055/057-result.md）；不读任何实现 Agent 自评或执行聊天。
- Ndocu/evidence/task-054/*、Ndocu/evidence/task-057/*、tests/task057_watchdog.mjs、tests/task054_pdf_materials_integration.mjs（057 正在变动的对象，按卡不读）。
- 其余项目历史（spikes/、frontend/、pdf_review 实现、003 迁移等），仅按引用需要确认边界。

## 未执行的动作（本卡禁止项）

未运行任何测试、Docker、应用、模型、安装、真实配置读取；未修改实现/测试/锁/正式 docu/既有证据；未提交 Git。

本卡自行只读复算的哈希与时间戳见同目录 audited-hashes.sha256、audited-mtimes.txt。
