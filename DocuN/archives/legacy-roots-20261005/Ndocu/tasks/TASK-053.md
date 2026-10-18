# TASK-053 版本化证据片段与词项检索基线

开发；STEP-007局部；R-047；FR-003/004、NFR-001、CON-001、DATA-002/003、MOD-005/FLOW-003。中档内部Agent，纯确定性位置/范围规则推理中等，不涉数据库写入或外发，可用有限合成反例验证。
根D:/shspic/project_NO3_RetroLume-agent；需求v1.1、架构v0.15；用户授权07/08。005PDF集成与008账本仍进行中，本卡只建立其后可复用的证据及词项候选检索，不宣称完整RAG/向量库/问答已可用。

## 目标及最小上下文
先读AGENTS/docu规则、架构FLOW-003、FR-004/NFR-001、materials/locations.py纯原文行跨度和pdf_import/contracts.py物理页结构。学习只用当前获准范围，证据必须能回原来源版本位置；模型检索相似不代表支持结论。
输入定义为服务端从原件/已确认PDF读取的归一化文本单元：source_id、version_id、source_revision、physical_page（TXT/MD为空）、origin_kind（original/user_supplement）、原text、是否可学习。PDF各物理页及用户补充分开，不能用阅读器合并text或页标记作为原文；非ready单元不产生学习片段。输入类型不构成权限授权，后续PG集成必须从权威范围校验，本模块不得自动信任来自HTTP的自报ready。

## 边界与产物
只写backend/app/retrieval/、backend/tests/test_retrieval.py、自身结果/证据。不得改materials/pdf_import/pdf_review/activities/capabilities、迁移、main、前端、锁、正式docu。无数据库/模型/网络/安装，无与051/052的文件冲突。
实现可复用纯函数/小型数据契约：原文分片、可复算证据ID、同源回查验证、范围内词项候选排序。片段原文逐字裁切，source/version/page/origin绑定，位置包含行与明确字符偏移（Unicode code point，end exclusive）；长单行仍有限分片，CRLF不改写。ID由稳定规范字段+原文hash产生，不用随机ID/进程hash。
有限输入（沿5MiB来源边界）、单片段大小、最多片段数、查询大小/词项数及top-k；超界明确失败，不静默遗漏后半资料或生成全部巨大中间对象。词项同时支持中文相邻字和英文词，范围过滤先于排序；确定性排名仅为检索候选，不自动声称事实冲突已解决/语义有据。查询无匹配返回空候选/证据不足，不补模型记忆。旧version、错source、错页/offset/hash验证失败；同名资料不靠文件名合并。
向量召回/pgvector持久索引/embedding费用/活动权限由后续集成补，不建立内存数据库替代品或假向量，不暴露新HTTP接口。结果明确该词项基线将与向量融合，而非静默删掉已批准向量能力。

## 验证及停止
一次局部unittest组，最多6类合成输入、5分钟：中英/CRLF原文裁切；长行和上界；确定性ID与摘录回查；不同来源同名隔离；过期版本和未ready拒绝；查询无证据及有界排名。复用现有行段语义，不重跑045或PDF测试。记录实际命令/输出/hash，性能结论不外推。两个有据修正仍失败/涉及权威数据或接口新决定则回报，不扩范围。
输出Ndocu/results/TASK-053-result.md，含调用契约、实际差异、真实证据、未接向量/PG/活动权限等限制与文档建议，不填Astra验收。
