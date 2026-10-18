# TASK-076 读取定位材料（只读声明）

任务：TASK-076 / R-070；类型：定向方案纠错；STEP-008；父 TASK-075；关联 NFR-002/003、SEC-002、FLOW-005、DATA-007。
执行环境：全新会话（Codex Sol C档），不沿 075 执行会话，不加载执行聊天。
日期：2026-09-22（Asia/Shanghai）。

## 读取范围（共 8 个文件，均为只读）

1. 根 AGENTS.md —— 规则入口。
2. docu/AGENTS.MD —— AI 工作规则与项目特有约束。
3. docu/PROJECT_ARCHITECTURE.MD —— 架构 v0.25 相关段：FLOW-005 及补充（L143-159）、概念数据 DATA-007（L189）、追踪矩阵 NFR-002/003/SEC-002（L276-286）、第4-5节相关行。
4. docu/REQUIREMENTS.MD —— 需求 v1.1 的 NFR-002/NFR-003 行（L102-103）。
5. backend/app/activities/repository.py —— 全文；重点 claim_lease（L274-303）、cancel_activity（L305-328）、admit（L527-584）、mark_dispatch_started（L633-645）、record_outcome（L698-722）、recover 系列（L330-474）、_activity_allows（L508-525）、事务超时配置（L86-105）。
6. backend/migrations/002_activities.sql —— 全文；activities 表 CHECK（L13-16、L28-31）、activity_operations 状态机 CHECK（L65-81）。
7. backend/app/pdf_import/_windows_job.py —— 全文；Job 限制设置（L115-130）、挂起-关联-恢复（L135-153）、超时强杀与有限等待（L156-161）。
8. Ndocu/results/TASK-075-supplement-01.md —— 全文；重点 §3 结算（修订3）、§4 监督（修订4）、§6 事件表（修订6.2）。该文件为待纠错方案，非批准基线。

## 只读声明

本卡未修改任何产品代码、测试、迁移、依赖、正式 docu 文档；未运行脚本计算、compile、测试、Docker、PG、应用、模型；未联网安装；未读凭据；未做 Git 操作。唯一命令操作为生成本目录下的 SHA-256 读取哈希（Get-FileHash，证据记录用途，非方案计算）。B 部分三条数值轨迹为手工推演。

哈希清单见同目录 read-hashes.txt。
