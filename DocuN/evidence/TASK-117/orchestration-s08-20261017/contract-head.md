# TASK-117 / R-111 — S08 保留初版、补齐四项修复与定向验证

## 完整成果、窗口与授权

你是 A+ 增强工程执行者，继续刚交回 S07 的 TASK117 原工程窗口。以已经保存的六份初版源码为起点，完成 D01—D03 的普通复查、必要修正和测试，完成 D04，再集中完成后端/typecheck/build及正式 bundle 的最小浏览器验证，交回一个稳定可审候选。不要重新研究全部 STEP018、重写现有初版、再交只读提案或逐个普通步骤回传。

沿用原 A+ 窗；仅原资源不可用时由一个 A+ 接续窗独占，原窗停止。标签不冒充真实模型身份，记录真实客户端/可知型号。仍人工转卡，不再委派子 Agent，不向审计窗转实施聊天。TASK仍117、R仍111，无新TASK119，原118独审仅在稳定后复核实际增量。

根目录 D:/shspic/project_NO3_RetroLume-agent；入口 D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。task_model/V4.0、公共AGENTS CHG-0003、阶段07；需求v1.3、架构v1.42、执行动态v2.69。公共只读根 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，读其DocuS/AGENTS.MD，适用WORK第2章task_model、第4—6、8—9章和task_model/prompts/07_开发执行循环.md；七锁定身份仍本项目DocuN/evidence/v4-migration-20260930/rules-snapshot.json。同窗已经读取、未变正文直接复用，不混入后来版本。

用户已批准116 AP1/AP2及继续开发，四项仍是原批准边界的缺陷修复。主控本次前向许可为 TASK-117-STEP018-AUDIT-REPAIR-S08-20261017，见 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/orchestration-s08-20261017/continuation-permit.json。许可只向前生效，不赦免S07或其它历史超额。Q/真实provider/真实费用始终0，80次20元仍为未来条件许可，不要求用户再次批准，也不得自制正式启用文件。

## 先核断点，只补剩余

1. 原结果 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-117-result.md，88265字节，SHA256 fc600e1381e44542fc933bdd294e471e2e1a5d4b70b979a5a2be708878993aab。S07明确未完成；末79709字节与原S06精确相同。本轮置顶S08时保留全部88265旧字节，不改失败、时间、not_run或旧结论。
2. D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/execution/continuation-06/ 的 receipt.json、post-source-manifest.json、changes.json/preimages、S07-product.diff、as-run.json、final-timing.json、final-binding.json、bundle-7-post.json、final-stop-observation.json；本次主控核证、输入和许可在orchestration-s08-20261017/received-s07.json、input-manifest.json、continuation-permit.json。同窗只补本次增量。
3. 原TASK118结果 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-118-result.md 第四节及证据继承/Q门，41590字节/dd0a5f1d2ddb2ffcd9a168496e4cca5b8292b7221977c76b8ff417f9ff0f21f1；原TASK116批准合同、X02纠正和原S06有效证据按四项实际依赖复用，不重采。
4. D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-117-work-decision.md 本次置顶，以及原源码和直接测试。原S07完整卡已备份在本次before-documents/TASK-117.md，作为历史合同，不恢复其已到限运行权。

本次核证S07清单15项均匹配、旧原件前缀/后缀保持，确实只有6个产品文件变化。D01 control.py 已抽取_validated_locked，当前SHA256 0db51f9ff61f4005854f32007d3c0727d966c062f33e0a64c0a56af8b926bf7e。D02 embedding.py=09e788f3e2207349b6bd5a11df2ec25a09893e8b0a504399332fbd44c5863e41，gateway.py=07f38bf2e4c11a7ca6be31b2cf9290e6a9db9ee349299f992d93bc692149bfc7。D03 TeachingWorkspace.tsx=8e1b851ceba2180755b61925f6c8ad6551eba0190a93b2cf7811c6b3cf947dd6，teachingIntents.ts=031464bac96413c8c72cb068e0a82555b0d17a131470dc2a55174f11e0f0a2ce，teachingApi.ts=1bca0ed927e1b03fc8b893b732d527841d7efb29d68b29f51cd04e6daf330afd。不能据“已落盘”声称修复通过；先定向普通复查和补测试，发现具体问题直接修。

D02初版增加有限model_requests批准对，结合完整payload及typed request摘要，空字段拟保持旧Embedding清单hash；还缺实际装载/私有传递、旧wire/Embedding兼容、正常批准send和拒绝反例。D03初版已捕获owner/view/head/scope/DataContext并调整草稿、POST和domain_sent时序，类型/原键恢复及真实竞态尚未核实。D04完全未实施。测试、typecheck、build、浏览器、控制器边界自检全部not_run；不要把未执行的修正计为第二次失败，也不要为了确认缺口原样运行已知不兼容夹具。

当前dist四项仍为原bundle7，主JS 58a87abf5ff4b02b33aab5dc3735507f4f097791e021aeb4ddfbf0b62ac115e8，不包含S07教学源码。旧bundle文件和原件继续保存，本轮必须在实现收齐后生成并实载新正式产物。

当前唯一工程账execution/budget.json phase=S07_returned_incomplete_activity_limit、active_root=null。S07未开任何根或浏览器/服务器：累计root24、Browser16、build7、fixture_server0、HTTP2324；PG创建尝试/对象/卷6、PGstart46、产品API33、Native140、preview各2、provider费用0保持。本卡仅重新授权未消费的3根/3Browser/2build/3fixture server/600HTTP，累计cap不增加，不挪未来Q预留。

S07首点2026-10-17T01:14:01.395492Z，最终复读2026-10-17T09:38:56.049183Z，保守活动30294.653691秒/21600，超8694.653691秒。宿主单调值低于起点，连续时钟域未知，不能把差值变负数、重置旧起点或补造pause。没有新测试根，不是“验证又失败”。旧63条失败前缀保持，新增三条控制/观察事实累计66；metadata wall漏记仍unknown，受控验证0秒不代表全部进程0耗时。

下面四项验收正文沿用有效S07合同。各“现状”指118审计基线，不要求撤回S07六份初版；以本卡当前hash接续。原要求不降低，本轮实际目标是把它们全部实现并验证。

