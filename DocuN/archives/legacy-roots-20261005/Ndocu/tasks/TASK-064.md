你是执行Agent，完成本卡后输出结果供用户带回Astra。
TASK-064 / R-058；类型：开发（夹具定向修正）；STEP-004/005；父TASK-063，关联061/059/052、FR-001、DR-003。
执行者：Work Buddy，GLM或KIMI K3，B档；记录实际标签。局部谓词与固定DDL一致性问题，已有真实反例，离线可验证，中档足够。
项目根D:/shspic/project_NO3_RetroLume-agent；需求文档v1.1、架构v0.19、执行状态v1.8。原开发授权；本卡不授权Docker、应用、浏览器或真实组合运行。

目标/问题/已有成果：
063唯一一次运行exit1，尚未启动业务场景。003实际产生两条约束：status取pending/confirmed/skipped；pending时decided_at为空、其他状态非空。主脚本verifyMigrationStructure约883行却要求同一CHECK包含confirmed、skipped、decided_at，误拒绝正确迁移。
Astra已直接核对003、原始迁移后清单、summary及停止日志；本次合成容器65b7ebcb4b979e4068974f4bc3c5da0aa54159538926676c6c4815ddeabf1a64已停止保留。无需复现旧失败，不碰该容器。
只消除这一谓词误报，同时保留缺约束仍拒绝的能力。不要改变业务DDL迎合测试。

上下文：
读根AGENTS.md、docu/AGENTS.MD、Ndocu/TASK_TEMPLATE.md和执行状态当前入口；
tests/task054_pdf_materials_integration.mjs中的verifyMigrationStructure；
backend/migrations/003_pdf_review.sql；
Ndocu/evidence/task-063/task063-resume1-20260921T0905Z/task057-db-schema-inventory-after-migration.json、task057-summary.json、task057-run-notes.log。
只读上述必要范围，不加载全历史或重复全面审计。

边界：
允许改tests/task054_pdf_materials_integration.mjs中候选状态/decided_at谓词及必要的局部导入；可新增tests/task064_candidate_constraints.mjs纯函数和tests/task064_candidate_constraints.test.mjs小型离线检查（仅必要时），以及Ndocu/evidence/task-064/、Ndocu/results/TASK-064-result.md。
禁止业务源码、迁移、其他结构校验/业务场景、47条业务断言、监督/归属/期限、依赖锁、正式docu、旧证据及Git。
不运行主脚本，不查询/启动Docker或进程，不安装/联网/模型调用/读取凭据。

实现约束：
1. 分别核对候选状态值域与状态/decided_at一致性；依据固定003及实际PostgreSQL导出表示，不要求它们同处一条CHECK。范围只支持本项目固定DDL，不建通用SQL解析器，不为未使用的等价DDL形式扩需求。
2. 不只查约束名字或关键词存在就通过；针对已知导出式校验两个条件及AND/OR、NULL/NOT NULL的实际结构，避免把反向条件当成正确。可做有限空白规范化后比对固定结构；遇未知表示明确拒绝，不能默认成功。
3. 若抽纯函数以供离线调用，主脚本必须真正使用同一函数，测试不得复制一份相似谓词。不得import会自动启动资源的主脚本做测试。
4. 其他验证及六业务场景保持原样；不顺手修复或重构。主脚本修改前SHA256为12888be4d3faa2b8c583308301e0e2f370ee964c63a048314b4b58c9df5eb493，若不符先核对差异，保护他人修改。

验收与必要验证：
复用063原始结构JSON，不运行数据库。B档一次离线检查批次，覆盖4个样本：
a 原始真实清单通过该局部谓词；
b 去掉status值域约束失败；
c 去掉decided_at一致性约束失败；
d 将pending分支IS NULL与非pending分支IS NOT NULL反转的弱化/错误约束失败。
反例仅在内存副本生成，不能修改原证据。使用现有Node内置assert或node:test，无新依赖。修改后的mjs一次node --check；记录实际命令和退出码。
单批最多60秒；仅允许一次有明确修正依据的受影响复检，仍失败交回。达到4例标准即停，不扩建模拟器、不全量重测。
交付前对照差异确认47条业务断言及场景块未变；保存修改前副本、新旧hash和原始输出。此为夹具离线通过，不等于六业务场景通过。

协作/停止：
独占本卡允许文件，不与其他修改这些文件的任务并行。无端口或外部资源。出现必须变更DDL/监督系统/验收标准时停止相关修改并回报，不自行扩大。
返回TASK/R/STEP、建议状态、实际文件与差异、准确命令/结果/证据、新旧hash、4例结果、未运行/风险、文档建议、必须人工操作及下一步。保存Ndocu/results/TASK-064-result.md，回复完整可复制结果块，不填Astra验收结论。
修正冻结后由Astra另出真实运行卡；063一次运行已用尽，本卡不续跑环境。
