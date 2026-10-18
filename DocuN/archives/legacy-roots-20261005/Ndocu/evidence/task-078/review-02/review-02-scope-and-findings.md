# TASK-078 / R-072 补审轮（review-02）证据记录

日期：2026-09-22
审计者：Work Buddy 执行 Agent（模型自报标识：GLM-5.3-Flash；未配置/未使用任何 API 密钥验证）
会话独立性：全新隔离会话，未参与 TASK-077 实现，未使用 077 实现窗口；判断形成于读取原 078 结果文档之前（N1 缺陷已先行定位确认），读取仅为续写保留历史。

## 一、冻结 hash 核验（六文件全部一致，无漂移）

见同目录 hash_current.txt（PowerShell Get-FileHash，SHA256）：
- backend/app/activities/repository.py 33b733e6…ffa57e 一致
- backend/app/activities/__init__.py 6bdb9609…a46dd 一致
- backend/migrations/004_activities_time_budget.sql 8f04f57c…97cc 一致
- backend/tests/test_activity_time_budget.py 63a19d1f…1a86 一致
- backend/tests/test_activity_ledger.py fb174d4c…de63da 一致
- backend/tests/test_activity_recovery.py 0e5d9c89…f88bf7a 一致

旧证据适用范围确认：Ndocu/evidence/task-077/revision-01/diff_revision01.txt 三个 post_sha256 与当前冻结值逐项一致，修正轮差异适用于当前代码；Ndocu/evidence/task-078/diff-*.txt 为首轮差异（repository/init/ledger 三文件当前 hash 与首轮一致，recovery/time_budget/004 的增量由 revision-01 差异覆盖），本轮未重新生成重复差异。

## 二、001/002/003 旁证补强

首轮证据仅有 mtime+sha256 前缀；本轮补算全量 hash（见同目录 hash_migrations_001_003.txt）：
- 001_materials.sql 767f47c331ba1e03… 与首轮记录前缀一致
- 002_activities.sql 3a9c5855aa9ddc54… 一致
- 003_pdf_review.sql 1ac29bafe58348a0… 一致
前缀一致支持"001/002/003 未改动"结论；仍属旁证而非冻结基线对比，如实标注。

## 三、N1 缺陷证据（确定缺陷，产品代码，高）

事实定位：
1. backend/app/activities/repository.py 第 70–77 行：ActivityLease 数据类仅 5 个字段（activity_id、executor_id、execution_generation、scope_revision、lease_expires_at），无 window_seconds 字段。经 Grep（class ActivityLease -A 9）与全文读取双重确认。
2. 同文件第 382–389 行：claim_lease 成功路径以 6 个位置参数构造 ActivityLease（末位为 effective_window）。frozen dataclass 收到多余位置参数必抛 TypeError。
3. 合同（TASK-077 固定契约 2）与测试均要求 ActivityLease 携带 window_seconds（如 test_activity_time_budget.py 第 152、200、215、348 行 lease.window_seconds 断言）。
4. 首轮 diff-repository.txt 无任何为 ActivityLease 增加字段的 hunk，与首轮报告"标准 3：ActivityLease 新增 window_seconds 字段""标准 6：ActivitySpec/ActivityLease 各一字段"的表述矛盾，属首轮报告事实错误并漏检本缺陷。
5. 与首轮报告口径冲突的披露：首轮报告结论"未发现确定缺陷（产品代码）"不成立；本判断在读取首轮报告之前已独立形成（先 Grep/Read 定位，后读报告），未受其影响。

影响：任何成功返回租约的 claim_lease 调用运行时 TypeError（TypeError 不属 psycopg.Error，_transaction 不转换，原样抛出）。折叠耗尽 None 路径不构造 ActivityLease，不受影响。所有依赖成功认领的 PG 用例（time_budget test_01/02/03/05/06/07 部分段/08、ledger 与 recovery 全部夹具）在 N1 修复前必然失败。

## 四、命令与边界记录

本轮仅执行：PowerShell New-Item（创建 review-02 目录）、Get-FileHash（两组 hash 文件）；未运行 compile/unittest/PG/Docker/EXPLAIN/应用/模型调用，未联网、未安装依赖、未读真实配置、未 Git 提交，未修改产品/测试/迁移/正式 docu/旧证据。
