# TASK-069 结果报告

TASK-069 / R-063；开发（G-1 测试清理修正）；STEP-008；父 TASK-068；关联 DR-003、NFR-002。
执行者：Work Buddy（GLM），B 档。日期：2026-09-21（GMT+8）。

## 结论

已完成：修复 backend/tests/test_activity_recovery.py 的资源清理缺陷（FK 清理顺序 +
test_04 第二活动失败窗口），仅改该测试文件，生产代码、DDL、依赖零改动。
建议状态：完成（待 Astra 验收）。静态验证通过；真实清理路径未运行（本卡禁跑 PG），
须由后续运行卡验证。

## 改动内容（差异明细见 task_activity_recovery.diff，共 3 处）

1. asyncSetUp：新增 `self.extra_activity_ids: list[str] = []` 本例创建 ID 登记。
2. asyncTearDown：统一收尾。对登记的全部活动 ID（主活动 + 额外活动）逐个执行
   操作/模型许可/来源关联/活动四表按 ID 删除；随后按外键顺序处理资料侧。
3. test_04：第二活动 other 在 create_activity 之前登记 ID；原 try/finally 局部清理
   移除，其断言体逐行原样保留（仅去一层缩进），收尾统一交 asyncTearDown。

## 外键删除顺序及依据

依据：backend/migrations/001_materials.sql 第 19-20 行
`material_current_version_source FOREIGN KEY (id,current_version) REFERENCES material_versions(source_id,id)`
（立即外键，默认 MATCH SIMPLE）；002_activities.sql 中
activity_scope_sources 双外键（→ material_sources.id、→ material_versions(source_id,id)），
activities 系列表自引用 activities.id。

删除顺序（全部 WHERE 限定本例 ID，单事务）：

1. activity_operations（WHERE activity_id=本例ID）
2. activity_allowed_models（同上）
3. activity_scope_sources（同上）——先于资料侧删除，解除对 material_sources 与
   material_versions 的两个外键引用
4. activities（WHERE id=本例ID）
5. UPDATE material_sources SET current_version=NULL WHERE id=本例source_id——
   关键修正：先解除对版本的引用再删版本，否则 001 组合外键阻止删除
6. DELETE material_versions WHERE id=本例version_id
7. DELETE material_sources WHERE id=本例source_id

WHERE 全部绑定本例 uuid4() 生成的 ID；无全表 UPDATE/DELETE；清理失败异常如实抛出，
不吞掉。

## test_04 第二活动失败路径说明

原代码 other 活动在 try/finally 之前存在失败窗口：create_activity 成功后、进入 try
之前的 claim_lease / admit / reclaim_next_generation 任一失败（或创建前任何断言失败），
finally 不执行，other 的活动行泄漏。

修正：other.activity_id 在 create_activity 调用前登记入 extra_activity_ids——
- 创建中途失败：create_activity 单事务回滚，无残留行，收尾按 ID 删除为空操作；
- 登记后、try 前任一步失败：asyncTearDown 必然运行（IsolatedAsyncioTestCase 语义），
  统一清理 other 与主活动；
- 正常路径：收尾重复删除为空操作，无害。
未扩大为通用测试框架，登记列表仅在 asyncSetUp 初始化、test_04 登记。

## 未变更项核对

- 5 组业务断言：diff 逐行核对等价（仅 test_04 断言体缩进调整），断言内容零变更。
- generation 规则、DSN 专用变量（RETROLUME_TASK_068_DATABASE_URL）、无 DSN skip 规则：
  未触碰（不在 diff 中）。
- 生产代码/DDL/依赖锁/正式 docu/旧证据/Git：零改动。生产 hash 冻结不受影响。

## 验证证据（Ndocu/evidence/task-069/）

- test_activity_recovery.py.pre-task069：原始副本（18309 字节）
- pre-change-hashes.txt：变更前 hash 及来源说明
- test_activity_recovery.diff：统一差异（143 行）
- compile-check-and-hashes.txt：检查命令、输出、新旧 hash

SHA-256：变更前 c7450f088235945281c0c25bdf4a57337bd671d34ea10e3de258fb36220896e2
（实测与卡面一致）；变更后 7bf924cded794b94bdc213d255177253af2b3948ad844f302d7bd987ae6804f4。

## 未运行项（not_run）与风险

- not_run：unittest 运行、真实 PostgreSQL 清理路径验证、3.13 复检（卡内明确无需）、
  应用/Docker/模型（本卡禁止）。
- 风险 1：静态正确 ≠ 真实通过。asyncTearDown 在清理 SQL 单事务内含 UPDATE，若运行时
  出现意外锁或 FK 顺序问题仍以运行卡实测为准。
- 风险 2：清理成功不代表产品验证通过，仅保证测试资源不泄漏；不把清理成功当产品验证。
- 风险 3：项目 venv 解释器为 Python 3.12.10，compile 通过；与目标 3.13 行为一致性由
  运行卡覆盖（本卡按卡面无需重做 3.13 检查）。

## 文档建议

建议 Astra 在 PROJECT_EXECUTE_STATE.MD 登记 TASK-069 完成候选（生产 hash 未动，
068 运行卡可直接复用本修正后的测试文件）；TASK-070 若需引用清理顺序，以本报告
"外键删除顺序"节为准，无需读本测试文件。

## 下一步

1. 用户带回本结果块交 Astra 验收。
2. 验收通过后按既有流程出 TASK-068 运行卡，用修正后测试在专用合成 PG 上实跑，
   验证真实清理路径。
3. TASK-070 可继续并行，与本卡无文件交集。
