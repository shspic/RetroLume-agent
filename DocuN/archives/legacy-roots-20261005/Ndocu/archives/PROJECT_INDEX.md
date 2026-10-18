> **只读历史／已迁移（2026-09-13，Asia/Shanghai）**：当前唯一有效文件见 [docu/PROJECT_EXECUTE_STATE.MD](../../docu/PROJECT_EXECUTE_STATE.MD)。依据用户V3指令保留以下原文，不再双写；旧“当前/下一步/待批准”只属于原时点，不能作为现行动作。流程和导航已并入执行状态，全部旧编号与记录保留。

# PROJECT_INDEX

- 项目：溯光教育Agent / RetroLume
- 版本：v0.42
- 最近更新：2026-09-11（Asia/Shanghai）
- 当前状态：真实TXT/Markdown上传→保存→列表→原文→替换已接通；STEP-003完成，STEP-004待补行段片段定位。启动start-local.cmd；本轮服务已停止保留。
- 用途：只导航到实际事实源，不代替原文，不登记 STEP/TASK 的第二套状态。
- 路径约定：项目文件使用相对路径；用户指定的外部实验目录使用 D:/shuice12 下的绝对路径。

## 已存在的文件

| 文件路径 | 用途 | 当前状态 / 版本 | 来源阶段 | 最近更新或核查 | 下一读取场景 |
| --- | --- | --- | --- | --- | --- |
| [AGENTS.md](../../AGENTS.md) | 所有 Agent 的权限、安全、修改、验证及文档规则 | 原有适用规则；本轮未修改 | 用户预置 | 原文件 2026-09-03 15:30:57 +08:00；本轮核查 | 每轮工作开始 |
| [CHANGE.md](CHANGE.md) | 唯一正式文档变更总账 | 已建立；CHG 递增维护 | 00 | 2026-09-10 | 任一正式文档成功创建或实质修改后登记 |
| [PROJECT_FLOW.md](PROJECT_FLOW.md) | 阶段关卡及登记迁移导航 | v1.5；最终流程及最新编制裁定 | 00/04/06 | 2026-09-11 | 阶段进入条件；活动TASK/R已迁出 |
| [PROJECT_INDEX.md](PROJECT_INDEX.md) | 实际文件导航与事实源映射 | v0.42；随实际产物更新 | 00 | 2026-09-10 | 每轮定位当前阶段原文 |
| [PROJECT_EXECUTE_STATE.md](PROJECT_EXECUTE_STATE.md) | 唯一STEP/TASK/R登记、证据与阻塞入口 | v0.8；待批准；STEP-002工程入口已完成 | 06 | 2026-09-11 | 23个候选STEP、全部历史迁移及当前下一入口 |
| [REQUIREMENTS.md](REQUIREMENTS.md) | 已确认的初步需求、优先级、证据状态和现实边界 | v0.2；已确认的初步需求／非最终基线 | 01 | 2026-09-03 | 阶段 02 只读取用；调研建议不得自行改写需求 |
| [OPEN_SOURCE_RESEARCH.md](OPEN_SOURCE_RESEARCH.md) | 候选、版本/许可/安全证据、覆盖矩阵、复用/退出建议与技术假设 | v0.1；调研报告完成，关键建议待用户决定 | 02 | 2026-09-03 | 第 9～11 节：阶段 03 假设、必须验证路由及关键决定；非最终选型 |
| [TECHNICAL_FEASIBILITY.md](TECHNICAL_FEASIBILITY.md) | 完整 HYP backlog、真实实验、限制与需求影响 | v0.23；局部证据支持进入最终需求收敛 | 03 | 2026-09-10 | 第 5.3～5.13/12.5/13.2～13.5 节：接口、解析、迁出、数据库、HTML 隔离审计、检索反馈、候选循环与具体取舍 |
| [spikes/SPIKE-001-text-provenance/README.md](../../spikes/SPIKE-001-text-provenance/README.md) | 样本、重现命令、原始证据导航、Work 复跑和视觉记录 | v0.1；局部实验交接 | 03 | 2026-09-06 | 读取 results/work_review_20260906；复用样本与反例 |
| [D:/shuice12/RetroLume-SPIKE-002/README.md](D:/shuice12/RetroLume-SPIKE-002/README.md) | 用户指定外部目录的源码/环境、安装及候选组件证据导航 | v0.2；局部实验，不是整体通过 | 03 | 2026-09-06 | 原始 evidence、installed-versions 与反例；只在此目录安装实验依赖 |
| [D:/shuice12/RetroLume-SPIKE-003/README.md](D:/shuice12/RetroLume-SPIKE-003/README.md) | 两平台接口、原 Flash 计算反例、向量形状与首批累计账入口 | v0.1；局部取证，原失败保留 | 03 | 2026-09-07 核查 | 原 request/response 与当前 first_batch_ledger.json；旧 summary 为历史快照 |
| [D:/shuice12/RetroLume-SPIKE-004/README.md](D:/shuice12/RetroLume-SPIKE-004/README.md) | Pro 原题对照与 Flash 独立工具往返、原账继承证据 | v0.1；TASK-007 已验收的局部诊断 | 03 | 2026-09-07 | 原题 payload 比较、工具关联与 ledger_before/after；非完整 RAG 通过 |
| [D:/shuice12/RetroLume-SPIKE-006/README.md](D:/shuice12/RetroLume-SPIKE-006/README.md) | 完整解析服务、评分反例、学习状态及非空迁出证据；数据库历史提案（已执行结果见 SPIKE-007） | v0.1；局部取证已验收，非整体通过 | 03 | 2026-09-07 | 七文档/十评分例、状态/导出核对、失败快照和最少人工操作 |
| [D:/shuice12/RetroLume-pgvector-validation/README.md](D:/shuice12/RetroLume-pgvector-validation/README.md) | 固定镜像、合成记录/向量检索、重启/转储恢复及停止证据 | v0.1；TASK-011 局部必要条件已验收 | 03 | 2026-09-08 | attempt2 有效结果、根首轮失败、work_review；数据库环境不再阻塞 |
| [D:/shuice12/RetroLume-SPIKE-008/README.md](D:/shuice12/RetroLume-SPIKE-008/README.md) | 原样 HTML、八例交互、权限反例与工具桥补证/隔离审计 | v0.1；局部已测边界通过，产品条件未关闭 | 03 | 2026-09-08 | 原始生成/浏览器记录、TASK-013 有界结论及局限 |
| [D:/shuice12/RetroLume-SPIKE-009/README.md](D:/shuice12/RetroLume-SPIKE-009/README.md) | 四检索/七反馈与实际向量/回答、普通复核和预算 | v0.1；局部效果取证完成 | 03 | 2026-09-08 | manifest、原请求响应、work_review；非完整复测或面试 |
| [D:/shuice12/RetroLume-SPIKE-010/README.md](D:/shuice12/RetroLume-SPIKE-010/README.md) | 七个原上游循环断言、五类复核与失败/联网阻断 | v0.1；候选内存循环局部取证完成 | 03 | 2026-09-08 | manifest、result、work_review、首次错误；非跨恢复预算或安全全验 |
| [D:/shuice12/RetroLume-SPIKE-011/README.md](D:/shuice12/RetroLume-SPIKE-011/README.md) | 资料版本、词项检索与原件回查正反例 | 2026-09-08首轮报告；局部取证 | 03 | 2026-09-08 | 25项结果/五类Work核对、已知复杂反例限制 |
| [D:/shuice12/RetroLume-SPIKE-012/README.md](D:/shuice12/RetroLume-SPIKE-012/README.md) | 七组跨请求进程预算与故障记录 | 2026-09-08首轮报告；原pending属历史，当前审计见可行性5.12 | 03 | 2026-09-08 | 原合同快照/manifest/49步日志/SQLite与TASK-019独立重算 |
| [D:/shuice12/RetroLume-SPIKE-013/README.md](D:/shuice12/RetroLume-SPIKE-013/README.md) | 真实反馈续答、归因失败/修正及下一缺失类别候选提案 | v0.2；原三例单次修正局部通过，原失败保留 | 03 | 2026-09-08 | revision1原请求/响应/账、work_review；gap_proposal已批准且单次执行结果见SPIKE-015，不可重复调用 |
| [D:/shuice12/RetroLume-SPIKE-014/README.md](D:/shuice12/RetroLume-SPIKE-014/README.md) | 本地在途停止四例及预算恢复，原始证据入口 | 首轮报告为历史；最新组合局部审计通过见可行性13.5 | 03 | 2026-09-10 | 首轮run/manifest；TASK-023原阻塞与TASK-025限定解除均保留 |
| [D:/shuice12/RetroLume-SPIKE-014/revision1/README.md](D:/shuice12/RetroLume-SPIKE-014/revision1/README.md) | 每例强制监督、主动超限及额外计数断言失败的原记录 | 原suite退出1保留；当前组合审计见可行性13.5/R-020 | 03 | 2026-09-10 | 原manifest/diff、15秒终止日志、组合证据限定 |
| [D:/shuice12/RetroLume-SPIKE-014/revision1/completion/README.md](D:/shuice12/RetroLume-SPIKE-014/revision1/completion/README.md) | 原停止账逐字副本恢复补证 | 局部组合已独立审计通过；非原地恢复 | 03 | 2026-09-10 | before/hash、受监督新进程、恢复前后账与原日志 |
| [D:/shuice12/RetroLume-SPIKE-015/README.md](D:/shuice12/RetroLume-SPIKE-015/README.md) | 同名消歧/面试正对照单次空答案及预算核查 | v0.1；失败，无重试 | 03 | 2026-09-10 | 原请求/响应/账与未执行配置修正候选 |
| [D:/shuice12/RetroLume-SPIKE-016/README.md](D:/shuice12/RetroLume-SPIKE-016/README.md) | PDF核对/原片段重排/跳过/替换局部证据 | 已普通Review通过；非产品 | 03 | 2026-09-10 | manifest/代码/40项结果与模拟用户限制 |

| [LATER_REQUIREMENTS.md](LATER_REQUIREMENTS.md) | 正式需求基线、31项映射和验收边界 | v1.0；已批准，当前有效正式需求基线 | 04 | 2026-09-10 | 阶段05架构与后续开发验收读取 |
| [D:/shuice12/RetroLume-SPIKE-015/revision1/README.md](D:/shuice12/RetroLume-SPIKE-015/revision1/README.md) | 同样三例配置修正的真实响应和普通Review | 局部通过，旧失败保留 | 03 | 2026-09-10 | 原请求/响应/预算与限制 |

| [PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) | 唯一架构候选和稳定架构编号 | v0.11；待批准 | 05 | 2026-09-11 | 架构审阅和STEP实现边界 |

WORK.md 尚不存在。本轮适用的 Work 协作规则由用户在对话中提供，不以索引条目冒充已落盘文件。后续 Session 需要这些规则作为输入。

## 预计产物（尚未创建）

下表只列规划名称；不表示阶段已启动、任务已分发或成果已完成。条件阶段仅在触发后创建有实质内容的文档。

| 预计文件 | 用途 | 对应阶段 / 生成条件 | 当前状态 |
| --- | --- | --- | --- |


| ACCEPTANCE_REPORT.md | 针对明确快照的集成验收证据与结论 | 08；开发门槛满足 | 未创建 |
| RELEASE_RUNBOOK.md | 发布准备、人工关口、备份、回滚和验证 | 08；不自动授权生产发布 | 未创建 |
| POST_BUILD_REVIEW.md | 开发后反馈评审，区分缺陷和新增价值 | 09；反馈或用户需求触发 | 未创建；条件启用 |
| OPTIMIZATION.md | 用户已选择 OPT 的优化范围与回归记录 | 10；优化项获批 | 未创建；条件启用 |

阶段 07 不为形式创建同职责“任务总表”；其状态使用 PROJECT_EXECUTE_STATE.md。没有已解决且验证可复用的问题时，不创建空的 spi_error.md 或 spi_index.md。

## 读取和登记入口

1. 先读 AGENTS.md 及用户提供的 Work 规则，再通过本索引定位当前阶段文档。
2. 当前读取REQUIREMENTS.md v0.2、OPEN_SOURCE_RESEARCH.md v0.1及TECHNICAL_FEASIBILITY.md v0.22第13.6；原研究为历史快照，已批准决定读取FLOW8.6/8.11。
3. 唯一登记在FLOW：TASK-001～030、R-001～023、SPIKE-001～017已占用；下一候选TASK-031/R-024/SPIKE-018未占用。
4. PROJECT_EXECUTE_STATE.md 已按原编号迁入活动登记，本索引只更新导航，不复制任务状态。
5. 初步需求已获用户确认；主要复用、框架与数据建议已批准，其他具体组件/服务仍需按范围核实，正式需求、架构、执行及发布批准各自独立，不能相互替代。
6. 用户最新技术选型读取 FLOW 第 2.1 节：PostgreSQL、Redis、pgvector 等已明确；原调研/可行性实验不是该组合适配通过的证明，三个 LLM 框架已明确按需选择。不得仅依据旧 CON-002 将全部选型继续视为未决定。

7. 阶段04已完成；31编号处理与Must验收读取LATER_REQUIREMENTS v1.0，最终阶段深度/审计/迁移规则读取FLOW第9节；旧待决段落保留为历史。

8. HTML 首版执行边界已获用户确认：FLOW 8.4 / 可行性 12.4；后续沿用，不重复索取相同批准。最小宿主内容/数值/已测权限和 TASK-013 隔离审计已完成，见 SPIKE-008；真实产品宿主及完整安全条件仍未验证。

9. 唯一累计账SPIKE-003/first_batch_ledger.json：11聊天/2向量、保守预留13/13元，实付未知。追加调用未授权；无需重配密钥或重复数据库实验。

10. 当前入口为PROJECT_FLOW第10节、PROJECT_ARCHITECTURE v0.5第12节；需求v1.0不变，方案已确认，架构尚待新宿主验证，不进入06。

| [D:/shuice12/RetroLume-SPIKE-017/README.md](D:/shuice12/RetroLume-SPIKE-017/README.md) | 镜像原失败及revision1启动受阻证据 | 已取证，未通过 | 05回03 | 2026-09-11 | revision1/README.md及NEXT_PROPOSAL.md（未批准单次启动诊断） |

当前入口更新2026-09-11（R-025）：TASK-032创建命令超时，未启动浏览器；[启动预检记录](D:/shuice12/RetroLume-SPIKE-017/startup-check/README.md)。架构保持待批准；失败不重试已停止。

当前入口R-026：[TASK-033实际启动与误报记录](D:/shuice12/RetroLume-SPIKE-017/startup-check2/README.md)。浏览器已启动；正常关闭未验证，未重试。

## 外部任务交接快照（2026-09-11）

| 路径 | 用途/状态 | 下一读取场景 |
| --- | --- | --- |
| [执行包](D:/shuice12/RetroLume-SPIKE-017/handoff/TASK-034-execution.md) | TASK-034完整合同快照；已生成未分发 | 用户转交有本地工具的执行模型，先准备提案 |
| [独立审计包](D:/shuice12/RetroLume-SPIKE-017/handoff/TASK-035-audit.md) | TASK-035完整合同快照；未开始 | 034证据就绪后，隔离新会话只读审计 |

任务主登记和合同原文在PROJECT_FLOW.md；交接文件不是第二项目状态表。

R-027当前入口：[TASK-034修正补充](D:/shuice12/RetroLume-SPIKE-017/handoff/TASK-034-R027-corrections.md)，已核查产物[运行提案](D:/shuice12/RetroLume-SPIKE-017/handoff-run/run-proposal.md)目前不可批准。原代码未由Work修改，未构建运行。

R-028入口：[TASK-036离线接管完整任务包](D:/shuice12/RetroLume-SPIKE-017/handoff/TASK-036-offline-takeover.md)，已登记未分发；原TASK-034不重跑真实实验。

R-029入口：[TASK-036复核补充](D:/shuice12/RetroLume-SPIKE-017/handoff/TASK-036-R029-review.md)；[实际提案](D:/shuice12/RetroLume-SPIKE-017/task-036/run-proposal-v4.md)尚未批准。

R-030入口：[TASK-036候选裁定与准备要求](D:/shuice12/RetroLume-SPIKE-017/handoff/TASK-036-R030-routing.md)。

## 2026-09-11当前入口覆盖说明

此前下文/条目中的R-030实验准备入口保留为历史证据导航，不是当前运行任务。当前阅读顺序：需求v1.0→架构v0.6第12节→执行v0.1第1～11节。执行文件已实际存在，不再属于预计产物；全部活动登记已迁移。

## 正式工程入口（2026-09-12）

[本地启动说明](D:/shuice12/RetroLume/README.md)；[TASK-038证据](D:/shuice12/RetroLume/evidence/task-038/README.md)。工程已存在；它不替代此处正式事实文档。
