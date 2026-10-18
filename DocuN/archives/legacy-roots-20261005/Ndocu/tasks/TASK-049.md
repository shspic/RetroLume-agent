# TASK-049 PDF候选、原页核对与确认准入

开发；STEP-005；R-043；关联TASK-045/047，FR-001、DR-001/003、SEC-001，MOD-001/004/008、FLOW-001、API-001/004。强档内部Sol：跨前后端候选版本事务与人工核对门禁，目标原子且风险中高，必须保留失败旧版。
根D:/shspic/project_NO3_RetroLume-agent；需求v1.1、架构v0.14，用户授权07/08。本卡实现已批准PDF Must，不含OCR/Office/学习模型。045 API位置完成、UI已补异步身份及重复选择，浏览器尚待集成；047分页解析组件存在，独立审计另行，不改其冻结核心。

## 上下文与目标
读AGENTS及docu规则、架构FLOW-001/003、最终FR-001/DR-001/003、TASK-047-result、pdf_import/contracts.py及公开parse_pdf_bytes、materials/api.py/repository.py、001迁移、main.py、frontend/src/main.tsx。实现上传PDF→原页/提取文逐页对照→用户明确确认/补充/跳过→当前资料可用，替换期间旧版保持。

## 独占范围与约束
允许新backend/app/pdf_review/、003_pdf_review.sql、必要materials/api.py与repository.py的PDF读取/候选整合、main.py路由、frontend/src/pdf/与main.tsx、前端package.json/package-lock.json（仅新增指定pdfjs-dist）、自身测试及结果证据。不得修改pdf_import冻结核心、activities/002迁移、capabilities、backend锁、真实DB/数据/凭据、正式docu。048只activities/002及自身测试，与本卡无同文件改动。没有真实模型调用、Docker实验或用户库迁移。
003只扩展已有来源/版本表示以支持PDF及独立候选/分页提取/人工记录，保留原001历史；准备迁移但不在用户库执行。当前版本字段仍是唯一活动版，待确认版本不可被materials列表/检索当可用；资料锁顺序与原CAS保持，确认必须事务比较上传时expected_version/revision，第三方更新则409而非覆盖。首次PDF可在候选列表出现但不误称已激活。

## 原页与依赖
仅新增pdfjs-dist==6.3.289前端渲染组件，源https://github.com/mozilla/pdf.js/releases/tag/v6.3.289，NPM固定元数据https://registry.npmjs.org/pdfjs-dist/6.3.289。Astra核查Apache-2.0、Node>=22.13或>=24（当前24）、无基础依赖；可选@napi-rs/canvas不安装。固定integrity sha512-ZHjSVpDa3D6izMq8/04lvkhkATUmL9px6ChPaXc1k6nU2Mrhlg1/7F0bdUqCwUjw3NsPTfPZsMDUU6ZIcRaeQw==。本地npm精确安装一次、10分钟，无旧版本升级、保留license/NOTICE（本地依赖及必要源码资源内），失败先诊断不盲重试。不用CDN/外部worker。
只使用PDF.js分页canvas渲染，不载完整viewer、JS动作、XFA表单、附件或活动链接；禁eval/远端字体资源等可关闭项，worker/CMap/必要资源走项目本地。原PDF通过会话受控API取得bytes，不能公开任意路径，不嵌入未经处理的HTML。每次只渲染当前物理页，限制像素，切换销毁旧文档/任务，渲染失败不能自动确认。解析还是pypdf，页图与提取文并列，不把图像或文本等价性自动判定为真。

## 业务验收
PDF原件仍5MiB、逐文件失败隔离；parse_pdf_bytes在线程池调度其受限子进程，返回pending，不把普通线程当超时终止机制。候选包含不可变version/hash、physical_page和raw extracted text。确认要求用户逐页对照勾选，分页列表必须完整且同版本；空/重复/越界/缺页/陈旧确认拒绝。用户纠字或解释独立标用户补充并保存关联页，绝不覆盖或冒充原提取文字。取消/跳过候选保留原件与旧活动版本，不自动删除。
原活动PDF的content返回物理页及用户补充身份，不能按UTF-8解码PDF原始bytes。后续RAG只接受已确认版本；本卡提供明确查询就绪状态和分页片段契约，不实现RAG。替换原TXT/MD为PDF或PDF为TXT/MD的候选/活动转换保持CAS与旧版可用，不能静默丢弃核对条件。
UI沿用已有资料工作台，额外候选区和逐页核对组件；保持行段摘录异步身份规则，TXT/MD正常。API错误用中文、原始bytes不出日志。内存替身不得成为正式持久化回退。

## 限量验证与返回
本卡一次局部HTTP/领域测试组（最多6类、10分钟，合成提取与内存仓储只作契约），覆盖待确认不可激活/缺页拒绝/用户补充身份/陈旧确认冲突/跳过或失败旧版仍在/当前PDF读取不解码原bytes。一次前端构建5分钟，不重跑047解析器或045已充分后端。真实PG事务+浏览器原页渲染/乱序交互另由集成卡验证，不伪称本卡已经通过；新迁移未经真实PG不得标持久层已验证。
代码/锁/证据hash、实际命令输出、依赖来源及改动、未运行/风险写Ndocu/results/TASK-049-result.md。达标停，连续两次有据修正仍失败或需要改锁定架构/安全边界交回。不得把整个005/项目标完成，不在本卡申请付费调用。
