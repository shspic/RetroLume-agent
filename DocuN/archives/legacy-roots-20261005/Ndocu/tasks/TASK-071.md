你是执行Agent，完成后输出结果供用户带回Astra。
TASK-071 / R-065；开发；STEP-008局部；父TASK-068，关联069/070、NFR-002/003、SEC-002、FLOW-005、DATA-007。
执行者Codex Sol，C档，新会话。事务批次、锁定集合和UPDATE一致性风险高，采用强档；不是独立审计。
根D:/shspic/project_NO3_RetroLume-agent；需求文档v1.1、架构v0.22、执行状态v1.14。原开发授权；内部仓储无调用方，Astra裁定补单批上限，不改HTTP/DDL或产品范围。

目标/事实：
068旧代次收敛SELECT/UPDATE没有批次上界。070指出大候选集可能使现有语句超时后整批回滚；这是风险推断，尚未实测，不写成已发生事故。
069已修测试定向清理外键顺序，保留，不重做。当前代码层审计限旧hash有效；本次差异完成后由Astra安排定向审计复核与真实PG验证。
只把旧代次收敛改为有界单批，不实现worker、不处理M-1、不加循环恢复器。

上下文：
根AGENTS.md、docu/AGENTS.MD、当前执行状态及架构G-1；
backend/app/activities/repository.py的两个新方法、事务包装及record_outcome；
backend/tests/test_activity_recovery.py；
只读001/002迁移、Ndocu/results/TASK-070-result.md的F-1及终态边界。审计“代次互斥”只说明旧代次不能提交received；旧permit仍可记unknown，因此保留终态竞争保护。
冻结输入：
repository.py cc7fddd4e685e1d3af859c7b402d0734354cef5675ed72f2f8acb83c92e6dcc7
test_activity_recovery.py 7bf924cded794b94bdc213d255177253af2b3948ad844f302d7bd987ae6804f4
不符先核对差异，不覆盖。

允许：
仅repository.py的recover_obsolete_operations及必要局部参数校验、上述测试文件的相关用例；
Ndocu/evidence/task-071/、Ndocu/results/TASK-071-result.md。
禁止DDL/索引/依赖/锁、其他生产模块、recover_unknown时间语义、正式docu、旧证据、Git；不运行Docker/PG/应用/模型、不联网安装、不读凭据。

实施合同：
1. 方法改为recover_obsolete_operations(activity_id, *, error_code="executor_lost", limit=100) -> int。
limit必须非bool整数1—200，非法明确ValueError；不静默截断。旧调用默认仍可用，但返回值现表示本批改动数，不代表整活动已恢复。
2. 保持来源→活动→操作锁序。活动锁后读当前代次，按operation_id排序SELECT候选并LIMIT，FOR UPDATE仅锁定本批候选；保留activity/state/旧代次过滤。
3. 收集实际锁定的operation_id；UPDATE限定为该确切ID集合，并再次限制activity/state/旧代次，RETURNING计实际改动数。空集合直接0。禁止UPDATE重新只按原宽谓词扫全部旧项；禁止通过重新选取另一个LIMIT集合代替锁定集合。
4. 单次事务不内部循环。调用方未来按有界次数/总期限调用至0并复查；无自动重试/调度，不把返回小于limit或0解释为活动永久无未决项。
5. 当前/未来代次、终态、预留/费用、准入与发送事实不变。不能以“都是unknown”放宽元数据幂等；不更改列表投影或引入新的凭据方案。
6. 批次上限限制改写及加锁行数，不保证扫描/排序输入有界或彻底消除锁等待，文档与结果如实说明，不为此改索引或跑性能基准。

测试准备及本卡验证：
保留069定向ID清理与5组原业务断言。
追加最小真实PG用例：5个旧未决项、当前代次对照，limit=2连续收敛得到2/2/1/0，逐批仅对应已选项变unknown、当前代次/预算不变；补limit的bool/0/201/非int拒绝。保持专用DSN缺失skip，不回退用户DSN，不全表清理。
测试只编写，本卡不运行PG/unittest。
C档一次差异/锁定ID→UPDATE追踪与语法检查：现有backend/.venv/Scripts/python.exe读取修改源码compile，不写pyc，最多60秒；失败仅有据修正后复检一次。不要用mock或SQL字符串断言冒充事务验证。
保存原文件副本、新旧hash、实际命令输出、未运行用例清单；达到范围即停，不扩测试平台。

返回：
TASK/R/STEP、建议状态、接口/实际差异、批次与终态边界、命令/证据/hash、未验证/风险、文档建议、必须人工操作、下一步。保存指定结果并回复完整可复制块，不填Astra验收，不宣告G-1或STEP008完成。
