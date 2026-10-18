# SPIKE-001：文字资料与来源定位基线

- 关联：TASK-003、HYP-001；FR-001/004、NFR-001/002、DR-001/003。
- 版本：v0.1；执行始于 2026-09-04，Work 复跑与交接补齐于 2026-09-06。
- 这是隔离实验。Work 验收登记见 PROJECT_FLOW.md 的 R-002；不可直接作为产品实现。
- 执行 Agent 留下脚本、样本和结果但未完成 README 交接；Work 检查既有实现后补齐本文，没有重新实现解析器。

## 范围与预期

manifest.json 在提取前单独记录预期，不能根据抽取结果倒推正确答案。七份自编资料：中英文本、Markdown、普通两页文字 PDF、双栏及表格 PDF、损坏 PDF、两个目录下同名 notes.pdf 的两个版本。PDF 使用本机 SimHei 字体生成；无真实用户数据。

普通 PDF 的印刷页码 101/205 与物理页 1/2 故意不同。复杂页明确要求先左栏后右栏，表格按行读取，内容流顺序故意交错；它是可推翻简单提取策略的反例。两个版本将复习间隔从三天改成七天。

## 重现

从项目根目录运行；使用已存在的 fixtures，不再生成或覆盖输入：

```powershell
& 'C:\Users\28432\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -I -B 'spikes/SPIKE-001-text-provenance/probe.py' --run-id work_review_20260906
```

以上为 Work 实际运行命令，exit 0。再次运行请使用尚未存在的新 run-id。只有在经授权的新隔离副本、fixtures 尚不存在时，才使用 --generate 生成样本；保留现有证据，不自动清理。

实测环境：Windows 11 10.0.26200、Python 3.12.14、pypdf 6.10.0、reportlab 4.4.9、Pillow 12.3.0、Poppler 26.07.0。没有安装依赖或调用模型。平台运行时和字体路径依赖本机；其他设备需先核实已有工具，不能据本文自动安装。

## 实际结果

| 检查 | Work 复跑结果 | 含义 |
| --- | --- | --- |
| 7 份资料 × plain/layout | 14 次；12 成功、2 个预期损坏文件错误 | 文本/MD 使用 UTF-8 直接读取，模式重复不代表两种 Markdown 解析器 |
| 片段 / 位置 | 62/62；62/62 | 合成样本内原文片段和物理页/文本行可查；不是引用支持性 |
| PDF 页数 | 8/8 | 两模式下四份可读 PDF |
| 阅读顺序 | 11/14；3 项失败 | plain 双栏、plain 表格、layout 双栏失败 |
| 裸批处理 | 两模式均被第二个坏文件中止 | 后续文件未执行 |
| 逐文件包装 | 其他资料继续输出 | 只验证实验 try/except 包装，未验证产品 |
| 两版本 | 哈希不同，三天与七天片段能区分 | 未验证知识库更新、删除或旧索引失效 |
| 渲染 | 4 条命令成功，5 张 PNG | Work 实际查看全部五页，中英可读、无明显裁切/重叠 |

plain 双栏顺序 L1,R1,L2,R2,L3,R3，预期 L1,L2,L3,R1,R2,R3；plain 表格 TH1,T1A,T2A,TH2,T1B,T2B，预期 TH1,TH2,T1A,T1B,T2A,T2B。layout 保留了横向间距，但平铺文本的双栏阅读顺序仍不符；表格顺序通过不等于得到结构化表格。

损坏样本实际错误为 PdfStreamError: Stream has ended unexpectedly，日志 WARNING pypdf._reader: EOF marker not found。错误为预设反例，不应隐藏。脚本 exit 0 表示实验取证条件满足（包含复杂反例），不是 HYP-001 整体成立。

## 证据与 Work 复核

主要读取 results/work_review_20260906/：
- summary.json：计数与反例；visual_review 保留原始机器输出 pending，实际目视结论记录于本文，不回改运行证据。
- results.json、extractions/：逐文件内容、片段、页与错误。
- bare_batch.json、replacement.json：裸批次中止与版本比较。
- environment.json、commands.json、stdout.txt：实际环境、命令、退出码和警告。
- input_inventory.json、expectation_snapshot.json、probe_snapshot.py、artifact_hashes.json：输入/预期/实现快照和产物校验。
- renders/：ordinary-1/2、complex-1、version_1-1、version_2-1.png。
- results/first_run/：首轮证据，保留用于比较。

Work 实际核验：输入清单、预期快照、版本比较与首轮一致；当前产物清单的 SHA256 全部匹配；五张渲染图与首轮哈希一致。results.json 原始全文比较不相同：仅两个坏文件 traceback 中脚本行号由 188/134 变成 189/135；其余字段一致。快照差异显示执行 Agent 增加了 base64 原始日志保留与子进程 UTF-8 参数，未改变提取/评价逻辑。排除已解释的 traceback 行号后，内容、评价、状态、错误类型和消息一致；不声称日志逐字相同。

Work 比较命令首次未显式指定 UTF-8，因 Windows 默认 GBK 解码 UTF-8 JSON 失败；明确 encoding='utf-8' 后成功读取。第二次全文相等断言揭示上述行号差异，经逐字段及脚本快照对比解释；没有修改样本或放宽解析成功标准。未因此写入错误经验库。

本轮运行前 Git HEAD 为 7011cd70712c25def203fde93e2f75b68f62fb22；上层知识库可能自动备份，不能只依赖瞬时工作区差异。脚本 SHA256 为 a823e2b1303f3ef0c7996a0db0881ea0e76842e6f3b9be5ae1711a386bc86639；manifest SHA256 为 7bb229801eb3c29f82bbb8eba12cf0b43ce7bd4cae595636677d8995e9b42f96。

## 结论边界与下一入口

HYP-001 在本组简单合成文字、物理页/行及包装层隔离范围内部分成立；不能以单一平铺文本策略承诺所有文字 PDF。extracted_offset 是提取文本偏移，不是原始 PDF 字符范围或坐标。扫描/OCR、公式、真实教材、多文件规模、延迟承诺、检索、学习效果、DeepTutor 和真实 API 均未验证。

样本、标注和证据可用于后续比较；probe.py 默认不可移入生产。数据与日志保留，不自动删除。正式结论与下一实验入口见 ../../TECHNICAL_FEASIBILITY.md 和 ../../PROJECT_FLOW.md。
