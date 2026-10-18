# TASK-112 实际元数据操作与记录局限

本窗口只执行文件读取、SHA256、有限diff/JSON/日志解析、标准库数值oracle及报告落盘，没有产品运行。完整实际工具调用语句留在本会话工具记录，commands.jsonl保存两份审计辅助脚本的实际argv和UTC/monotonic；它不冒充全部PowerShell、rg和view_image的全量机器计时清单。

首次读入为Get-Content -LiteralPath对项目AGENTS.md和DocuN/tasks/TASK-112.md，随后读rules-snapshot.json。七规则使用Get-FileHash -Algorithm SHA256对锁定absolute_path逐一比对；正文按AGENTS及WORK 2/6/8读取。最早准备段没有同步工具时钟，15:06:14Z第一已知时间和QPC原样存receipt.json，不追造首读时间。

文件导航使用rg --files，章节、差异入口及直接调用搜索使用rg -n。实际目录定向使用Get-ChildItem -LiteralPath和Get-Item，只读。采用python -X utf8运行TASK112目录自己的audit_metadata.py和audit_evidence.py，未导入backend/app、fixture或Node/PW模块。脚本源及argv可复查全部哈希、原件比对和数值计算方法。

两张已有图片由view_image读取，分别为C04 root14/step08/ui-attempt01/ui-remote-1.png及ui-binomial-ready.png。没有调用浏览器、图像生成或编辑。

外部机制仅查TC39 CompileAssertion与WHATWG Encoding TextDecoderCommon两个官方页面，原URL保在报告及独立定位中。没有搜索新技术方案、下载依赖或传出项目代码。

真实准备失误保留。首次Python输出因本地stdout编码出现乱码，后用-X utf8读取同一文本；有限导航数次猜错输出文件名产生FileNotFoundError，之后按rg返回的真实原件读取，没有补造不存在文件。读取raw sessions时辅助脚本假定CID为顶层列而KeyError，实际原件该列在confirmation_receipt内，修辅助解析后逐条与真实原件匹配。一次functions.exec语法错误和一次报告apply_patch上下文不匹配未执行动作，随后更正；这些不冒产品测试失败或重跑。

报告本身仅检查12项覆盖、链接、身份与结论一致性，并复读。初末冻结清单各独立核225项，无漂移；81对原件/副本另核一致。artifact保留全部历史FAIL、UNKNOWN、超限、pre与时间缺口，不用元数据修正改写原账。
