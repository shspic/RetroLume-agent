# 项目规则入口

本文件所在目录 D:/shspic/project_NO3_RetroLume-agent 是项目根目录，项目相对路径均以此为基准。

公共规则源为 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4。
当前唯一模式为 task_model。采用 V4.0，公共 AGENTS 修订 CHG-0003；锁定的实际读入指纹见 DocuN/evidence/v4-migration-20260930/rules-snapshot.json，不自动采用后来版本。

## 规则读取

- 全部 Agent 读取本入口及公共库 DocuS/AGENTS.MD。
- 承担需求、规划、组织、架构、共享状态维护或最终裁定的主控，同时读取公共库 DocuS/WORK.MD。
- 主控读取本项目 DocuS/执行动态文档.MD，再按真实当前阶段读取公共库 task_model/prompts 中的提示词。当前为 07，00 仅用于恢复，05／06 按需维护。
- task_model 完整任务卡使用公共库 task_model/TASK_TEMPLATE.md；普通执行者只读取卡面指定的最小充分上下文。
- 本次目标、交付物和授权终点以用户有效请求与项目记录为准，规则不增加操作权限，不读取其他模式代替当前合同。

## 项目路径与维护权

用户指定的原始需求输入当前实际位置为 D:/shspic/project_NO3_RetroLume-agent/DocuS/原始需求文档.MD。
用户最终需求实际位置为 D:/shspic/project_NO3_RetroLume-agent/DocuS/最终需求文档.MD。

原始需求输入依据用户 2026-09-30 明确重命名要求从 docu/REQUIREMENTS.md 原字节迁入，历史整理性质和原文不改。此后仍仅由用户维护，Agent 不代写、覆盖、移动或重命名；本次特定迁移不是未来任意改写授权。

正式文档在 DocuS 单层 Markdown，最终需求、架构动态、执行动态和文档变更记录各有唯一职责。DocuS/执行动态文档.MD 是唯一总进度与任务状态账。完整旧路径映射和版本在该文件，不并行维护第二份状态。

新执行材料进入 DocuN 的 tasks、results、evidence、spikes、handoffs、archives，有内容才创建。已有 TASK-001—090 的卡、结果、证据及旧实验继续位于 Ndocu 或原已登记位置，未验收同边界续作沿原路径，不复制或强搬证据。新卡自 TASK-091 使用 DocuN，编号连续。

旧 docu 英文文档只保留只读迁移导航。docu/AGENTS.MD、WORK.MD 的原正文已归档在 DocuN/archives/legacy-project-rules-v3-20260930，不作为当前规则。历史证据记载的旧路径和规则时点不追改。

产品源码、资源、配置在 backend、frontend、deploy 等既有产品目录。开源参考库沿用 D:/shspic/OPEN_project，错误经验库沿用 D:/shspic/错误记录；实际映射和待归档事实见执行动态文档。产品运行、构建、业务测试不得依赖公共提示词库或临时实验实现。

## 协作与恢复

公共库只读，项目产物不写回；修改公共库须有对应明确授权。
task_model 保留人工转卡和结果回传，编排者按已确认范围自主出卡，默认不接管执行。资源配置 A-／A+／A 的当前安排见执行动态文档，标签不冒充真实模型身份。

合同须给实际根目录、本入口、锁定规则版本、必要输入和产物绝对路径。旧窗口收到新合同后补读已变规则，不能追认未读取的版本已经生效。

换窗、换规则或改目录不清零 TASK、R、CHG、失败次数、投入、预算、在途或有效证据。已有资料同窗未变则复用，只补缺失。公共源不可读时使用同一明确版本的必要正文或完整导出件并登记；关键规则缺失仅暂停依赖部分，不假称已加载。

保存成功但接收者不可访问时说明真实保存和访问限制，提供必要正文；真正未保存才标未保存。平台权限、用户有效要求及公共安全边界继续适用。

