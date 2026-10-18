# TASK089 审计证据索引

所有相对路径以D:/shspic/project_NO3_RetroLume-agent为根；只引用原件，不复制日志。产品/测试最终冻结时间见final-hashes.json；终审没有代替编排关闭G3。

| 目的 | 唯一来源 |
|---|---|
| 接收基线/规则版本 | 本目录pre-hashes.json、pre/、rule-versions.json；087批准包/088原卡/089完整卡保持原路径 |
| 088实际差异数量 | 088-diff-inventory.json；原diff位于Ndocu/evidence/task-088/diff/ |
| 088批01原件 | backend/Ndocu/evidence/task-088/pg-run-01/；规范目录missing，不倒造 |
| 旧PG02/03/04及Windows | Ndocu/evidence/task-088/{pg-run-02,pg-run-03,pg-run-04,windows-run-w1}/；只支持其原始历史事实，缺as-run绑定 |
| 初审/终审报告 | Ndocu/results/TASK-089-independent-audit.md，仅TASK089/Audit写入 |
| 审计独立复算 | audit/freeze-check.json、final-freeze-check.json、method-applicability-check.json |
| 集中修复快照 | final-hashes.json、diff/、final/；保护边界protected-hashes.json |
| 离线43项＋新增1项 | offline-01/及offline-02/各自原始stdout/stderr、case-summary、as-run-hashes、manifest |
| 新runner静态检查 | runner-static-check.json；静态检查不冒充异常收尾动态注入 |
| 真实PG18成功/1失败 | real-01/stdout.log、stderr.log、case-summary.json、as-run-hashes.json、batch-input-hashes.json、manifest.json |
| PG原加载测试源 | real-01/as-run-test_activity_results.py，运行后仍相同hash时保存；失败test19保留 |
| 最终复用适用性 | final-applicability.json；审计独立AST复核原件在audit/，18方法及helper未变 |
| 资源/预算 | budget-manifest.json为单账；real-01/manifest.json为起停原始记录；final-resource-observation.json为五CID当前只读状态 |
| 继续断点 | checkpoint.md；凭据owner已结束，不启动新真实批 |
| 下一业务合同 | Ndocu/results/TASK-089-next-contract.md，仅设计，没有G4产品实施 |

本卡未生成bootstrap运行记录、Windows场景日志或batch-post-hashes：真实批在PG测试非零后退出，未进入Windows段；这些文件缺失具有明确原因，不能由夹具存在推断场景执行。最终产品hash由PG as-run/source_unchanged和独立复算支持，不补造未执行的阶段记录。
