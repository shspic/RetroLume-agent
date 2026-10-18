# TASK-110 读入范围与权限记录

本记录只保存本卡取证范围，不维护项目总状态。实际客户端为 Codex，系统描述基于 GPT-6；部署型号后缀和实际推理档位不可核。接收档位 A+ 是任务资源标签。本窗口未参与 TASK-109 实现，未读取 TASK-109-result.md、其实现聊天或思考过程；没有派发子 Agent，也不声称本卡是独立终审。

项目根 D:/shspic/project_NO3_RetroLume-agent。入口 AGENTS.md 全文。公共规则锁定 V4.0 / AGENTS CHG-0003，七项实际 hash 均与 rules-snapshot.json 相符。正文加载公共 AGENTS 全文、WORK 第 2 和 6 章必要合同、task_model 的 07 与局部 05。其他三个锁定文件只核身份，没有加载正文或切换模式。

读取 TASK-110.md、TASK-110-work-decision.md 和 orchestration-20261010/input-manifest.json 全文。执行动态文档只读首 95 行和定向匹配，其中首 19 行 v2.31 为当前依据，其余保留历史。正式 DocuS 全部只读。

原始需求文档只定向读取 HTML、交互、计算、图形、安全等匹配行，主要依据第 29、39、54、71、92、120、144—146 行。它是用户维护的历史整理材料，不把其中代理整理文字称为用户逐字原话。最终需求文档定向读取 FR-009、SEC-003、B-01、范围、采用和验收相关行，主要依据第 18、57—61、77、93、110、121、156、181、196、212、228 行。

TASK-108-result.md 读取第 1—279 行，覆盖原 A—D 正文及其证据边界；采用状态以 TASK-108-work-decision.md 全文的置顶有效决定为准。原结果中当时的待采用措辞不覆盖后来采用决定。没有读取 108 附录实验或扩展历史。

TASK-109.md 读取置顶关闭许可与 C05 第 1—75 行，并曾定向匹配导航、关闭和预算关键词。其后旧卡只用于确认历史，不恢复任何许可。没有读 109 结果自评。

必要源包括 deploy/preview/host.cjs、wrapper.html，backend/app/preview/contracts.py、supervisor.py、reaper.py 全文；navigation-tail.cjs 只读固定 fixture、顺序、观察、Frame 绑定、投影、判定和首反证停止相关匹配段。activities/repository.py 只核 admit、cancel_activity、_write_outcome、record_outcome、read_committed_result 的真实定义位置及是否存在 HTML 接线。没有 import、解析执行或调用产品代码。

补充读取 C04 attempt-02 的 vendor/playwright-core/package.json 中 name/version/license/engines 和 LICENSE 首 18 行。前者说明本地包为 1.62.1、Apache-2.0、Node 要求 >=20；后者只核许可标题，不称第三方清单完整。

原件包括 R08 preview 下 navigation-hash-counterexample.json、frame-binding.json、observations.json、resource-observations.json 和 container-stdout.bin。JSON 只做字段读取；stdout 只从既存字节解码有限头、JSON、分块及 hash，不运行 Node 或 fixture。raw-navigation-reading.json 保存范围与交叉结果，不复制原始证据，也不是新运行证明。

input-identity.json 核对编排冻结的 16 个直接输入，全部相符；再保存 7 个直接补充输入和 7 个公共锁定指纹。稍后附加的两个本地包许可输入单独列 supplementary-input-identity.json。不重算原 500 对象。

只枚举了必要目录及与任务有关的文件名。一次 deploy/preview 文件名搜索误包含 vendor 子树，未因此读取额外 vendor 内容，随后改为单层文件清单。四次缺失路径读取或查找分别是误置于 evidence 的 110 work-decision、缺失的 frontend/src/explanations、尚不存在的 deploy/preview/package.json、误置于 deploy/preview 的 reaper.py；只纠正 work-decision 到实际 results 路径，其他依现有正确源或计划事实处理，没有安装、创建产品空壳或运行重试。

第一次保存有限摘录时，单个数值范围被PowerShell意外展开，出现6次参数类型错误；只将该资料脚本改为明确from/to对象，重写本卡摘录文件为6源/11段/123行。没有重复软件测试或修改源。此修正发生在正式文档一致性检查之前，不伪称该初次摘录已完整。

允许写入只有 TASK-110-result.md 与本 evidence/TASK-110 内的新 solution-20261010 证据。创建证据目录前核其解析绝对路径位于项目根下。没有修改原证据、任务卡、产品、测试、锁、迁移、DocuS、公共库、原始需求或记忆，没有 Git 写入。

公开资料见 official-sources.json。两原生候选、一个输出合同方向；8 个不同官方资源含 4 个源码文件尝试，其中 1 个失败。既读页面内查找复用，不追加新资源，不下载二进制或 clone。

运行事实为零产品运行、零 compile/test/build/Node 程序/浏览器/Docker/PG/模型/provider/付费/安装/删除。文件 hash、JSON 读取和末尾一次文档一致性检查属于本卡资料许可。总资料起点没有在首次读文件前精确打钟，采用首次可核 UTC 时钟点再追加 180 秒准备的保守上界；不虚报精确工作秒数，详见 delivery-check.json。
