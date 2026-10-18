# TASK-045 TXT/Markdown行段定位与版本回查

类型：开发；STEP-004；R-039；前置TASK-043通过；关联FR-001/004、NFR-001/002、DR-001/003、MOD-004、FLOW-001、API-001/004、DATA-002。
执行者：待派发Codex内部中档Agent；位置映射和兼容HTTP集成推理中等，可纯函数及HTTP反例验证，不改持久数据模型，因此中档足够。前置未通过不修改工程。
根：D:/shspic/project_NO3_RetroLume-agent。有效目标docu/LATER_REQUIREMENTS.MD v1.1，架构v0.13；用户已授权07/08。

## 目标、现状与上下文
已有UTF-8 TXT/MD上传、替换、原件hash、PG版本与React阅读器；只补行段位置及引用回查。先读AGENTS.md、docu/AGENTS.MD、执行文档STEP-004、架构FLOW-001/003、TASK-043-result及实际materials/api.py、repository.py、frontend/src/main.tsx、后端test_materials.py。历史上传/PG事务和浏览器证据已有效，不重写已有流程。

## 范围、兼容与契约
独占backend/app/materials的定位实现及必要只读API集成、frontend/src/main.tsx和相关样式、backend/tests/test_locations.py；自身Ndocu/results与evidence/task-045。禁止修改迁移、库数据、锁、原件存储逻辑、上传语义、正式docu、其他Agent文件。无模型/PDF/向量/安装/外发。
保留现有content响应material/text语义，可增加派生locations；引用定位使用source_id、version_id与起止行（从1开始、闭区间），摘录仅从该原文切出，不接受客户端摘录当原文。可在原content GET增加可选expected_version、start_line/end_line（两者同时提供）；旧调用行为保持，旧version与当前不一致显式409不返回新版冒充旧引用。首版旧引用可明确失效，不伪称已经实现历史正文浏览。
行规则：只识别CRLF/LF/CR，保留原text逐字不变，说明末尾换行的行号规则；连续非空行形成段，Markdown只按原文纯文本，不执行HTML；空白行仍可定位。不要返回每行一份重复全文造成无界放大，位置用有限元数据或分页（上限与完整数量分开）；正文界限沿用5MiB。UI显示同一响应的版本、行号/段号及有限范围选择，替换/异步加载后清除旧位置，不让错版本选择继续显示为当前。界限错误400/422、超出原文范围明确失败。

## 验收与验证子项
回查普通中英文、空行、CRLF/LF/CR时摘录与不可变版本原文一致；错误行范围拒绝；旧版本引用在替换后明确失效；恶意HTML仍纯文本；大量短行不会生成无限DOM或重复正文。现有列表/上传/替换不改语义。
中档执行一次局部测试组，最多6类合成样本、10分钟，涵盖上述实际变化；无真实PG/用户资料/付费服务。允许前端一次类型检查及构建（5分钟），复用043入口证据，不启动整套浏览器/PG回归。记录实际命令、源码hash和原始输出，不能以测试数量代替结论。修正有明确原因才重跑受影响项，两次有据修正仍失败交回。

## 输出与停止
写Ndocu/results/TASK-045-result.md，列实际文件差异、来源规则、命令证据、未验证、旧引用限制、文档建议；不写Astra验收。若必须改变锁定数据模型/权限或无法保持旧HTTP兼容，先报告具体冲突。达到标准即停，不追加测试。
