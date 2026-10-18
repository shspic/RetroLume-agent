# TASK-078 / R-072 — review-03：N1修复增量独立复核（当前待转交）

接收Agent：继续TASK078 review-02原Work Buddy独立审计窗口。该窗口不得参与TASK077修正轮02；若实际是同一窗口或继承了实现聊天，先报告独立性冲突，不签独立结论。型号如实记录即可，不以模型名称不一致为理由重审。用户最新指示：任务按成果验收，未完成时才说明是否需要强模型。此指示优先于本卡历史附录中的品牌/档位补审要求。
任务类型：独立审计续作；TASK078/R072不变；STEP008局部、父TASK077、NFR002/003、SEC002、FLOW005、DATA007。需求v1.1、架构v0.29、执行状态v1.30。
本轮是既定单行修复和现成客观证据的增量检查，难度/推理需求低、边界明确、可直接验证；原独立窗口常规执行足够。原review02对高风险事务部分的已完成工作保留，不因更换分档名称或客户端重复审查；发现实质未完成或能力缺口再交编排升级。
项目根D:/shspic/project_NO3_RetroLume-agent。
入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。
公共AGENTS：D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD（2026-09-23T09:02:19.8371311+08:00）。
公共WORK编排依据：D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/WORK.MD（2026-09-23T09:04:14.5455941+08:00），执行者无需全文加载。公共库只读，补读规则变化，不重载未变材料。

目标：确认review02唯一确定阻断N1在当前快照关闭，并给出当前代码层审计结论及进入定向PG的意见。保留已确认D1/D2/O1与标准1/2/4/5/6/7结论及原始证据的适用范围；不宣称PG或M-1/STEP008通过。
最小独立输入：自己的TASK078 review02结果与范围证据；TASK077原合同中ActivityLease必填window_seconds/claim实际W_eff返回条款；当前repository定义及成功返回调用点；Ndocu/evidence/task-077/revision-02/diff_revision02_repository.txt、pre__repository.py、construct_check.log、check_activitylease_contract.py、post_hashes.txt。只读原始证据，不读TASK077结果/自评/实现聊天；已有review02上下文保留。同窗未变代码不再全文加载。

当前六文件冻结SHA256：
- backend/app/activities/repository.py：045a3cf8b1c81d7a1336c3bd2e90e891e4e53934027c9fea9727fafde7202534
- backend/app/activities/__init__.py：6bdb960912ea3fc7ddd8730f37a44e580b73768e1067d23facc9983ca04a46dd
- backend/migrations/004_activities_time_budget.sql：8f04f57c743c260f5081e0c6f232860301b30c7b03fef69498d7c0704c0a97cc
- backend/tests/test_activity_time_budget.py：63a19d1f2a99236d56bd1cc1841953908fa8c1f955ff0c6d5d61b4ee84621a86
- backend/tests/test_activity_ledger.py：fb174d4c29355bb0e57ac013d4e8555ef9ac342e9be804e0edbf732112de63da
- backend/tests/test_activity_recovery.py：0e5d9c89a7a3fce490cc60deb7c0a608b8c54356edd7c4b18ee66165bf88bf7a

一次连续完成：
1. 确認新增必填window_seconds:int位于lease_expires_at之后、保留frozen，和claim六参数位置一致；diff仅+1行，无事务/SQL变化。
2. 核对真实导入构造脚本与日志绑定当前hash、六参数79和前五字段断言、exit0；它只证明构造契约，不证明PG。复用日志，不重新运行构造/compile。
3. 对未变五文件确认hash适用；将review02原不通过结论按N1是否关闭更新为当前代码层结论。若有实质证据缺口明确指出，不凭编排建议直接签通过，不重复所有八项审查。
4. 复用review02最小PG清单，仅更新N1前置状态与当前hash。迁移检查按实际列级/表级约束逐项核对，不把“五列+四条约束”当完整CHECK总数；其他用例与test08当前名称保持。无需重编清单或测试框架。

读写/资源：只读上述实现与原始证据；仅写Ndocu/evidence/task-078/review-03/必要增量记录，以及Ndocu/results/TASK-078-result.md置顶本轮结论，保留原轮历史。正式docu/公共库/业务/测试/迁移/旧证据禁止修改。无DB/端口/容器/服务；无并行实现任务，源码冻结。PG、Docker、迁移、compile、unittest、应用、联网安装/真实模型/配置密钥/Git操作均不执行。
预算/停止：一次有界增量阅读及必要hash核对，完成以上四项即停；不重复review02整段审计，不重跑有效验证。漂移、独立性冲突、实质新缺陷或不能可靠裁定时带位置/证据回传，由编排决定是否升级，不自行扩大。旧尝试和13元费用预算不重置，本卡PG额度0。
返回：N1结论、当前快照/原证据适用范围、独立性与实际身份、原代码结论如何更新、未验证及PG清单差异。保存D:/shspic/project_NO3_RetroLume-agent/Ndocu/results/TASK-078-result.md并确认可读；只回复一句结论和可点击绝对路径，统一回传，不填写编排最终验收。

历史合同已归档至 Ndocu/archives/TASK-078-before-review03-20260923.md，仅供追溯，本轮无需读取或执行。

