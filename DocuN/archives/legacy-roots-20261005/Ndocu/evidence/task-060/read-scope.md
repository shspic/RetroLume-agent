# TASK-060 读取范围与只读声明

日期：2026-09-20（Asia/Shanghai）。执行：本卡全程只读；未运行测试、Docker、应用、模型、安装；未读真实配置；未修改产品、迁移、锁、正式 docu、旧审计报告；未 Git 提交；未读取 TASK-059 的变动脚本。

## 读取清单

规则与编排：
- AGENTS.md（根入口）
- docu/AGENTS.MD
- docu/WORK.MD（编排规则，用于门槛/状态口径参照）

058 审计与证据：
- Ndocu/results/TASK-058-result.md（全文，更正对象）
- Ndocu/evidence/task-058/ 目录清单（audited-hashes.sha256、audited-mtimes.txt、read-scope.md 未逐字节复读，仅确认存在）

架构与状态：
- docu/PROJECT_ARCHITECTURE.MD（FLOW-005 L116-132、FLOW-005 补充 L126-132、相关索引行）
- docu/PROJECT_EXECUTE_STATE.MD（STEP-006/008 条目、TASK-058/059/060 登记行、NFR/SEC 映射行，grep 定向）

被审源码（只读）：
- backend/app/activities/repository.py（全文）
- backend/app/capabilities/contracts.py（全文）
- backend/app/capabilities/gateway.py（全文）
- backend/app/capabilities/transport.py（全文）
- backend/migrations/002_activities.sql（全文）

第三方事实核对：
- backend/.venv/Lib/site-packages/httpx/_content.py（encode_json L176-183 及 encode_request 分发）

051/055 原始证据（定向部分）：
- Ndocu/evidence/task-055/verification.md（全文）
- Ndocu/evidence/task-055/ledger-check.stdout.log（全文：七类 ok、loop factory、库名 retrolume_task_048_synthetic、PG 17.11）
- Ndocu/results/TASK-051-result.md、TASK-052-result.md、TASK-057-result.md（迁移应用口径定向 grep：001/002/003 的执行与未在用户库执行的事实）

## 未读取

- TASK-059 的变动脚本及其证据目录。
- 真实配置文件（config/、环境变量、.env 类）。
- 用户数据库、真实资料、凭据。

## 事实核对方式

- F-1（L-2 更正）：直接读取本机 venv httpx 源码与 gateway/transport 源码逐参数比对。
- F-2（迁移口径）：055 stdout 的库名/版本行 + 051/052 结果中迁移应用范围表述交叉核对。
- F-3（L-1 保持）：contracts.py 与 repository.py 校验逻辑逐行比对 + 046 离线测试用例 id 字面核对（"activity-1" 非 UUID，走离线假账本）。
- F-4/F-5（M-1 方案边界）：PostgreSQL CURRENT_TIMESTAMP/now()/clock_timestamp 语义为公认数据库行为，结合 FLOW-005 三条并列要求推理；未做动态验证（只读卡禁止）。
