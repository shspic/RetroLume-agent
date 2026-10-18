# TASK090 独立审计输入

原目标/授权：Ndocu/tasks/TASK-090.md与用户附件dabcf0f3-4e17-4eb5-a67f-fbe77b5755cb/已粘贴的文本.txt；设计TASK-089-next-contract；前置正式验收TASK-088-089-final-acceptance。主执行聊天/自评不作为输入。

当前产品/测试/runner已冻结，final-hashes.json绑定现文件；pre/及pre-hashes.json保存原58项/正式文档；diff/含本卡精确增量，新文件以完整新增diff供读。正式docu/001—007/旧fixtures/证据没有变更。

原始动态证据real-03/（manifest、stdout/stderr、case-summary、as-run/post、loaded-source-bytes、parent-loaded-source、bootstrap-SUP/worker），离线offline-01/02/03/04/（各自原始case/log/hash/外层Job）。独立核计数/适用性，不按摘要代验。

预算单账budget-manifest.json；real-01原inspect入口失败，第2独立诊断在resource-diagnostic-02.json（保守亦计attempt），最后real-03实际批。Docker不可用记录resource-blocker.md，后用户明确已就绪才执行末批。旧失败不抹除。

实际改动文件：
- backend/app/activities/__init__.py
- backend/app/activities/repository.py
- backend/app/capabilities/__init__.py
- backend/app/capabilities/contracts.py
- backend/app/capabilities/gateway.py
- backend/app/worker/launcher.py
- backend/app/worker/one_call.py
- backend/app/worker/session.py
- backend/app/worker/supervisor_main.py
- backend/app/activities/service.py
- backend/tests/test_activity_scope.py
- backend/tests/test_activity_continuation.py
- backend/tests/fixtures/task090/bootstrap.py
- backend/tests/fixtures/task090/controlled_child.py
- backend/tests/fixtures/task090/offline.py
- backend/tests/fixtures/task090/real_batch.py
- backend/tests/fixtures/task090/support.py
- backend/tests/fixtures/task090/win_chain.py

增量01冻结入口 incremental-01/index.md，含初审pre哈希、最终哈希、两项最小diff和匹配实际加载的final源码；offline05十一项原始日志/摘要/指纹/Job收尾。真实03加载修正前快照，未变仓储/IPC/PG类及成功路径适用性须独立限界。AGENTS外部V4变化及用户明确替换见external-rule-change.json和rule-update.json；另正式架构只出现外部编码/换行字节变化，规范文本与本卡pre完全一致，见external-navigation-change.json。产品hash未变。
