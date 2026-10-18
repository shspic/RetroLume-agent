# TASK-075 读取范围与只读声明

- 日期：2026-09-21（Asia/Shanghai）。执行者：Codex Sol（C 档强档，新会话）。
- 本卡为定向诊断与接线方案（TASK-075 / R-069 / STEP-008 / 父 TASK-060）。全程只读产品代码与正式文档；未修改任何产品/测试/DDL/锁/正式 docu 文件；未运行测试、Docker、应用、模型、性能或模拟器；未联网研究/下载/安装；未读取真实配置（数据库连接串、密钥等）；未 Git 提交。
- 仅写入：`Ndocu/evidence/task-075/`（本文件、read-hashes.txt）与 `Ndocu/results/TASK-075-result.md`。

## 实际读取文件（SHA-256 见 read-hashes.txt）

规则与正式文档：
- AGENTS.md（根入口）、docu/AGENTS.MD
- docu/PROJECT_ARCHITECTURE.MD v0.25（重点：FLOW-005 及补充、§3 MOD-003/007/008、§5 DATA-007、§6 API-006/FILE-009、§8 质量与验证、R-053~R-068 增量裁定）
- docu/LATER_REQUIREMENTS.MD v1.1（重点：NFR-002/003、SEC-002、§13 非阻塞参数）
- docu/PROJECT_EXECUTE_STATE.MD（任务登记表、R-053/R-054 验收与重新规划段）

产品代码（只读，未运行）：
- backend/app/activities/repository.py（PostgresAdmissionLedger 全量）
- backend/app/activities/__init__.py
- backend/migrations/002_activities.sql
- backend/app/capabilities/gateway.py、contracts.py、transport.py（transport 仅经 gateway 调用关系核对，未逐行审计）
- backend/app/runtime.py
- backend/app/pdf_import/supervisor.py、_windows_job.py（既有受监督子进程边界参照）
- backend/app/main.py（import/include_router 全量核对，确认未接线 activities/capabilities）
- deploy/start_local.py、deploy/start-backend.ps1（仅 grep 核对启动入口，确认无 worker 启动路径）

历史结果（按卡面限定读取）：
- Ndocu/results/TASK-060-result.md（M-1 分析与 R-054 保留纠正）
- Ndocu/results/TASK-074-result.md（成功边界与仓储接口相关段落；未加载全套历史日志/自评）

## 定位检索（rg）

- `worker`（backend/app）：仅命中 pdf_import 的受监督子进程与注释；backend/app/worker/ 目录不存在。
- `claim_lease|create_activity|PostgresAdmissionLedger|ControlledModelGateway`（backend）：仅 repository.py、activities/__init__.py、gateway.py、capabilities/__init__.py 及 backend/tests 三个测试文件命中；无任何产品调用方或应用接线。

## 证据继承说明

- 072（代码审计）与 074（六例真实 PG）对 list_unresolved_operations / recover_obsolete_operations 仓储切片的证据继续适用；本卡不重验、不重写。本卡方案仅在其调用方（未来 worker）层面引用该切片，未触碰其实现；repository.py 当前 hash 与 R-065 登记 50ec537b…55cfce6 一致。
- TASK-060 §4.2 "单换 DB 时钟即修复" 的方案已被 R-054 否定（事务 now 固定于开始、不能据此断言锁等待被计入；3600 秒封顶无真实耗时依据）。本卡不重走该路线：DB 时钟仅作为组合方案中的辅助判定项，回拨防护主责由持久计数器承担。
