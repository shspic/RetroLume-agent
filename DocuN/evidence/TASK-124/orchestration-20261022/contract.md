# TASK-124 / R-118 正常readiness与计量交付的集中独立增量复核

## 一个完整成果

你是本卡A+独立审计者，一次审完TASK123稳定的六文件增量、有限文字、计量结论和原始离线证据，回答是否具备交主控关闭该有限前置工程的条件。不得把本次有限工程验收和Q启用资格混为一项；Q尚缺当前分词/完整服务模板、Embedding容量与账号等依据，继续冻结。

本卡只读、零运行，使用已有最终13方法证据，不重跑旧Q矩阵，也不开展下一轮供应商浏览或分词下载。覆盖完本范围就保存一次完整结论并结束。

项目根D:/shspic/project_NO3_RetroLume-agent，入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。模式task_model，V4.0/公共AGENTS CHG-0003，阶段07，需求v1.4、架构v1.62、执行动态v2.90。公共只读根D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4；七锁定指纹在DocuN/evidence/v4-migration-20260930/rules-snapshot.json，不自动采用后续版本。

TASK124/R118，父TASK123/R117及STEP018；关联已结束的122准备、119有效采用、116固定Must；NFR002/003/005、SEC001/002/003、DR002沿原定义。A+为用户资源标签，实际客户端/模型如实登记，不按完成报告的型号另开重审。

## 独立性与接收安排

优先继续原TASK121的独立A+审计窗口，前提是该窗口未参与TASK123实现/测试/资料取得，且没有持有其实现推理上下文。原121任务已结束，本卡是实际新六文件和新文档的集中增量，不恢复121运行许可，不重复其旧五缺陷。若原独立窗口不可续或参与了123，使用未参与123的新隔离A+审计窗，按本合同读最小输入即可。不委派子Agent。

不读取TASK123统一结果、实施聊天、自评或主控候选裁定段来形成判断。TASK123计量文件、有限输入和部署交接本身属于被审交付物，允许阅读，但其中推导必须与原始源码/官方返回分开，不能拿作者结论证明自己。审计判断先于需要保留历史/逐条回应时读取实现自评。任何记忆或共享上下文偶然暴露据实披露，不伪称从未接触；实际独立性不成立就不签独立结论。

## 冻结对象与最小输入

完整合同和真实输入hash在D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-124/orchestration-20261022/contract.md、input-manifest.json与permit.json。先核身份，再按下列顺序读。旧同窗已读未变的规则/旧协议只补变化，不重读全仓。

1. 根入口、公共DocuS/AGENTS.MD及WORK中独审/证据/停止/验收适用段、07提示词、本完整卡。不得根据原已结束任务跳过本卡实际新增边界。
2. TASK123原完整实施合同，使用DocuN/evidence/TASK-123/orchestration-20261022/contract.md；其permit只看原允许文件、资源与预算。TASK120的有效采用回执DocuN/evidence/TASK-120/orchestration-20261018/adoption-receipt.json只用于固定范围，100次/25元、48/28/24与12/7/6元不重问。
3. DocuN/evidence/TASK-123/execution/product.diff、pre-snapshot.json和pre/四份原字节、post-snapshot.json；六个当前文件全文。下列post SHA256为实际冻结值。

- backend/app/main.py，da3f864b469dcf38d5fa699044fca454b2844f1e9ead93c44bade74f0896a41e。
- backend/app/activities/api.py，865583497763dd7c853b6dbbcb5aa14bc7be69f508a3bc357b86f022dec2fdb9。
- backend/app/q_readiness.py，9644904e802283adb9ac575fcdf59ab6c7bd02fb8083ae58f48c8c37a0f2d063。
- backend/tests/test_q_readiness.py，612acc3f77011b15cffb94409104b916a9c96852ed329b5560fcce2d95340a96。
- README.md，0410c7573027f7f6e75635c3a8d050e2be375d98ab0a4b503ddf3e076104d938。
- deploy/q-approval.md，0a3a44dd445de0b92fbdf5f9aea21c40b8ad7a42969b3f46e94885322c33cb60。

4. 直接依赖只读service_config正常装载、retrieval/service.py::load_integration_config/IntegrationConfig、operator/q_request.py::configure_application返回、capabilities/contracts.py的ModelServiceConfig、embedding.py的服务/Grant/manifest解析，以及main现有认证/DataContext接线。以本次新增调用和公开字段为界，不重新审费用事务/权限角色图/所有Q协议。
5. execution/batch1—3的command/completion/原始stdout/stderr、batch3/summary.json及run_offline_tests.py；最终实跑字节对应的两份既有配置/API测试仅看所选六方法和直接夹具。原两次失败原样读取，不用第三批成功抹去。delivery-manifest.json、save-proof.json、input-check.json、final-consistency.json与预算/工具/download/web账作身份和控制证据，不把作者布尔自查当独立证明。
6. execution/metering-evidence.json、metering-verdict.md、finite-inputs.json、deployment-handoff.md；计量新增结论只对照已存web-responses/W123-04/05/06及web-request-ledger，按真实路径读取，不发新网络请求。其余缺失分词/模板/账号事实已保持unknown，不为这些外部缺口阻断有限工程交付。
7. 原116 sample-inputs.json及acceptance-contract.md中L01/L05/L10必要原文，原122 remaining-must-matrix.json用于确认有限新文字的用途/父顺序。89动作/24片6批预算已由主控验过，原文未变则直接继承，不重新分片或全量加总。

## 本次必须集中回答的六组问题

### A 新只读投影是否真正不授权

按实际diff核main只捕获启动当次候选/最终对象与key存在性，build_readiness不重读配置/环境、不查询PG、不调用configure_application/QAuthority/ControlHub/approve等，不改变原装载/关闭/绑定顺序。GET只复制快照，新字段不添加storage/memory probe，原认证/同源/DataContext及R01/R02读写纪律不变。

candidate、effective、q_approval和qualification语义必须明确。key存在、allowlist配置、形状校验、同对象/摘要相等、TESTONLY、作者写verified均不能投影为本人账号/当前token/正常部署/真实响应已经合格。检查坏/关闭配置和已装载对象的实际可达状态，不能只据字段名或少量合成断言称全域通过。快照明确为startup_loaded_snapshot，不要求新增热加载或实时授权平台；只有具体误报或改动风险才提出问题。

### B 敏感信息与启动回归边界

按数据流逐列核返回模型/alias/limits/reason/摘要，拒绝key/其hash、DSN、私有路径、完整正文/异常原文泄露，检查错误和异常传播是否可能破坏原正常启动/读取。有限identity正则不自动证明任意配置值均不敏感，要结合现有装载约束判断可达性及新旧责任边界。不得把既有未变公开字段的历史风险冒成新增确定缺陷，但真正新增回归不能因旧函数未改排除。

### C 最终13方法证据的准确适用性

从batch3实际command输入字节、completion日志hash、原始stderr、summary和测试实现绑定六个测试输入文件的当前hash，确认13方法无failure/error/skip和实际检查内容。审查tripwire的安装时机、范围/计数与测试导入路径，区分“替身未被调用”“真实完整GET的受控合成测试”和真实PG/profile/服务；不能用计数0泛称无任何系统调用。

复核初批120.031秒超时及第二批20.453秒诊断、第三批经正常平台审批1.828秒通过的实际原件。判断两次失败与最终证据关系，不要求再运行原失败以证明其存在，不把映射124当原生退出或外层0当下载成功。新增7方法加既有6方法的覆盖和未跑项必须分开。没有具体缺证不追加运行。

### D 计量结论的分级与外部停止点

被审结论没有启用token_upper_bound_verified，也没有更改Grant/费用/容量门。核U≤W只针对当前纯文本规范JSON范围的推导，不能扩成T≤W+F。核官方材料能否支持“max_tokens覆盖包含reasoning的生成总量”的有限文档推论，并区分公开契约、推断、实际服务和本人账号事实；有材料不完整就明确降级该项，不把未实测当错误，也不声称所有费用/输入上界已关闭。

确认tokenizer/模板原件、完整commit/服务绑定、许可证和Embedding计量缺失均如实unknown，没有把下载失败说成资料不存在、把短文本/费用裕量当容量证明、或拿其它模型tokenizer替代。判断供应商待询问题是否精确到尚缺的关系且不索敏感信息。无需重新寻找这些外部原件，也不以继续冻结本身认定本卡违反目标。

### E 有限文字和部署交接

核HTML focus与继续理由的原文/hash/用途同原116约定相符。真实父必须当前已提交且合格，不能把文字草案当已有父/description/控件/artifact，也不能扩大模型可用来源或预写成功。核HTML父在下一query前、现correct本地保存契约和CAS限制。若卡内补的文字改变了既定目标，给精确原文差异，禁止只凭关键词给PASS。

检查交接准确写现有启动/初始化入口能力，没有造不存在参数、在文档中授予正常资源、启用回执/密钥/配置enabled或新T0；新normal初始化尚缺和receipt TASK谱系限制照留，不要求本卡实现它们。

### F 执行控制与正式结论分轴

根据原permit/receipt/命令与下载/网页账复核三测试批、允许文件和网络/安装边界、时间包络及unknown处理。原123保守记3554.557411/7200含600收尾、完整工具实测unknown，先核证方法和实际关闭时间，不将预留当实测、不盲信其数字。原122/120/121失败与预算/停止事实继承，不清零、不追认旧控制通过。

本次最终结论按代码、证据、执行控制分别给出，再给有限前置工程是否可交主控关闭；计量启用资格另列为未具备。已知严重失败写不通过，关键证据真缺写无法判断；只有轻微且已获真实接受的限制才能用有条件通过。不要因Q冻结或新normal未创建而否认本卡本来就允许的有限工程终点。

## 范围、预算、独占与停止

产品、测试、README/deploy说明、123执行证据与报告全部冻结，无并行写入。只允许写D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-124/audit/及DocuN/results/TASK-124-result.md，主控orchestration目录和DocuS/旧历史不可改。可以stdlib计算hash、读JSON/文本、生成有限diff，不能导入产品或执行原runner。

本卡工具wall上限1800秒，其中240秒预留写出/收尾；通常单命令60秒。日历截止按permit签发24小时；实际接收未知用签发保守，不自动延期。原121保守2113.8359792/3600已结束留档，1233554.557411及1221340.9775537是历史原账，不从新卡擦除或借其余量。本卡新工作首次动作如实登记，未知不填0，不为凑时间重查已匹配身份。

compile/unittest/产品导入/PG/SQL/Docker/应用/API/TestClient/browser/Job/模型/embedding/计量接口/真实费用/Git/联网/下载/安装/私有配置/账号后台/委派上限全部0。无需用户释放内存或提供key。不查询系统实时进程以替代原控制事实，不把旧资源的过去停止证明说成现在实查。

发现具体确定缺陷先保事实，非破坏/泄露即时风险则完成本范围一轮合并后回传，不逐个问题打断。若冻结漂移或关键对象不可读，停止依赖部分并交准确路径/hash；不审旧快照冒当前通过。遇超范围、独立性不成立或到预算门保存事实停止，不能自行修代码、扩大测试或改任务。

## 完整结果与回传

保存TASK/R/STEP、真实身份和独立性、当前对象/差异及读取范围hash、A—F结论与具体定位、确定缺陷/条件风险/未验证区分、真实控制账/边界、有限交付及Q启用两种状态、文档建议、最少下一步。确定缺陷给严重度、触发、影响与最小修正，不把非阻塞观察自动升级新硬门。

原始证据足够就明确采纳，不要求为更放心重跑13方法或旧安全链。没有新缺陷时交关闭条件和保留的外部事实清单即可，别再提出同样查核设计卡。最终验收与共享状态归主控，审计不得签Q启用、STEP018/019/020、M1、项目或发布通过。

结果完整保存复读后仅回复一句话结论和可点击的绝对路径D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-124-result.md，供用户带回主控。
