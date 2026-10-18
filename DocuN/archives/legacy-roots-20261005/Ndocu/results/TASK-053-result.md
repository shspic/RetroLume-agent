# TASK-053 结果：版本化证据片段与词项检索基线

- 执行时间：2026-09-14 +08:00
- 关联：TASK-053 / R-047 / STEP-007 局部实现
- 结论：已完成可复用的纯函数证据片段及范围内词项候选基线。该结果仅提供后续 MOD-005 的位置与候选能力，不表示完整 RAG、向量召回、pgvector 持久索引、活动权限或问答已接通。

## 调用契约

`app.retrieval.SourceTextUnit` 是服务端已经从原件或已确认 PDF 得到的单个文本单元，字段为 `source_id`、`version_id`、正整数 `source_revision`、`physical_page`（TXT/MD 为 `None`）、`origin_kind`（严格为 `original` 或 `user_supplement`）、未改写 `text`、以及权威流程给出的 `ready_for_learning=True`。

`build_fragments(unit, *, max_fragment_codepoints=2048, max_fragments=2048)` 按原始 Unicode code point 的右开字符区间逐字分片，保留 CRLF/LF/CR，给出行号、offset、来源/版本/物理页/身份、原文 SHA-256 与可复算 `ev_` ID。来源原文 UTF-8 最大 5 MiB，长行仍按片段上限切分；超出任何上限明确抛错，不静默丢弃后段。非 ready 单元拒绝生成片段。

`verify_fragment(unit, fragment)` 同时回查来源、版本、修订号、物理页、身份、offset、摘录、hash、行号与 ID；错来源、旧 version、错页/offset/hash 均返回 `False`。同名资料不参与身份判断。

`rank_term_candidates(query, fragments, *, allowed_versions, top_k=10)` 只接受冻结的 `(source_id, version_id)` 范围，先过滤范围再排序。它使用英文词项与中文相邻双字候选，查询为 16 KiB/最多 24 个去重词项，`top_k` 最大 50；按命中次数降序、证据 ID 固定破同分。无命中返回空元组，表示这个词项通道没有证据，不补模型记忆或自动解决冲突。

## 实际差异

- 新增 `backend/app/retrieval/__init__.py` 与 `backend/app/retrieval/evidence.py`。
- 新增 `backend/tests/test_retrieval.py`。
- 未修改 `materials/`、`pdf_import/`、`pdf_review/`、`activities/`、`capabilities/`、数据库迁移、`main.py`、前端、依赖或共享正式文档。

## 验证证据

实际执行一次局部命令：

```text
D:\shspic\project_NO3_RetroLume-agent\backend\.venv\Scripts\python.exe -m unittest tests.test_retrieval -v
```

退出码为 0；6 个合成测试在 0.008 秒通过：中英 CRLF 原文裁切、长行与片段上界、确定性 ID 与摘录回查、同名不同来源隔离、旧版本与未就绪拒绝、范围先过滤及有界排序/无证据空结果。未重跑资料、PDF 或前端套件。

写入结果后的 SHA-256：

```text
f06f9694e213db25dff7119f6609ca553ffb339868b51c1d9e181104d91efdcc  backend/app/retrieval/__init__.py
632363754f465303cd424c66b8e61d38a27f6352f0c1efbad807a16ea2da1a60  backend/app/retrieval/evidence.py
0060b56aad05b26080e583f002d6165c7580768e9c1b3db205d074d7401001e  backend/tests/test_retrieval.py
```

## R-047 普通复核修正

复核指出原 `build_fragments` 会先实体化所有行跨度，并为每个片段重扫原文以重新定位行号；在 5 MiB 多行文本和最多 2048 片段的合法边界上会产生不必要的重复全量扫描。现已改为只保留当前行跨度、流式读取下一行开头；生成阶段直接使用已知的当前行号。每行在创建任何片段前先计算所需数量，若会超过最大数立即拒绝，不继续读取后续行。`verify_fragment` 仍只对单个外来片段按需扫描一次原文，未改变其回查语义。

实际只运行本修正对应的一个合成反例：

```text
D:\shspic\project_NO3_RetroLume-agent\backend\.venv\Scripts\python.exe -m unittest tests.test_retrieval.RetrievalTests.test_long_line_and_fragment_limit_are_bounded -v
```

退出码为 0；1 个测试在 0.001 秒通过。该例以受控行迭代器确认：第一行已可确定超过片段上限时，函数在读取第三行前抛出明确上限错误。原 6 项通过证据未重跑。

此次修改前后 SHA-256：

```text
632363754f465303cd424c66b8e61d38a27f6352f0c1efbad807a16ea2da1a60 -> 4c79fc6531bcf323ea05dcae85d181ed555024f9bbdf2d0ede9897678601475a  backend/app/retrieval/evidence.py
0060b56aad05b26080e583f002d6165c7580768e9c1b3db205d074d7401001e -> dfc2e066160346f7234e7f408acfd02b4bcee66597f99c55304a750894ccda50  backend/tests/test_retrieval.py
```

## 限制与后续建议

本卡不读取 HTTP 自报的 ready 状态，也不自行实现权威范围核验；后续 PostgreSQL/活动集成必须在权威活动范围、当前版本、删除/撤销和 PDF 确认状态后才调用本模块。PDF 每个物理页与同页的用户补充应传为两个独立单元，不能合并其 text 或页身份。词项结果只是和后续批准的向量通道融合的候选，不代表语义支持、冲突已解决或引用已经授权给模型。

正式文档建议：待 PG/活动/embedding 接入后，将本模块的固定位置、范围先过滤、ID 可复算和词项限制写入对应实施记录；在融合参数以中英样例冻结前，不将当前排序分数写成召回或质量结论。Astra 验收及独立审计不在本结果填写。
