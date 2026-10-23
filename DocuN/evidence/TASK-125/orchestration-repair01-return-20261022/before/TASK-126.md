# TASK-126 / R-120 正常首次安装工具链集中独立审查

## 目标与完整交付

你担任独立审计执行者，只读审查TASK125稳定的完整安装工具工程和原始离线证据。一次回答首次真实apply前的安装代码/角色权限门是否具备通过条件，给出确切缺陷或通过边界，以及后续最小真实安装验证清单。不是实现卡、运行卡或新的计量调研。

范围是六个最终文件及其直接依赖、相对pre的实际差异、两批原始日志/实际受测hash和执行控制事实。原TASK123/124的readiness、准确理由及13方法，原120/121未变业务/迁移/profile/权限结论按其适用范围继承，不重审全仓或重复原安全矩阵。

交付为D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-126-result.md，原始核证只写D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-126/audit/。报告分代码、证据、执行控制三轴，独立给出确定缺陷、条件风险、未知及适用范围。报告写完不等于主控最终验收。

## 项目、规则和接收安排

根目录D:/shspic/project_NO3_RetroLume-agent；入口同根AGENTS.md。模式task_model，阶段07，V4.0/公共AGENTS CHG-0003，锁定清单为DocuN/evidence/v4-migration-20260930/rules-snapshot.json。公共根D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4。

接收A+增强独立资源，优先继续原TASK124独审窗口，前提是没有参与125实现、普通修复或测试设计。原窗不满足真实隔离时改用新隔离审计窗口，不改变TASK126/R120编号，不要求为模型标签重审旧成果。实际客户端/模型如实登记；无法证实的后端变体写未知，不伪称身份。不能使用原TASK125工程窗口自审。

关联STEP-018、STEP-020的部署交接和未来STEP-019适用安全证据，父TASK125/R119，需求v1.4、架构v1.66、执行动态v2.94。原因是安装器将来执行固定迁移及创建角色，属于原TASK125已规定的首次真实apply前必需独审；稳定候选现已返回，不按每个文件分别审。

授权终点是当前冻结代码、已有证据与有限文件核证，运行和真实资源额度全0。本卡尚待人工转交，主控未通过工具派发；接收后登记实际时间及独立性。工程候选已返回并冻结，原窗口停止写入，不与本审计并行修改。

## 独立输入与读取顺序

1. 根入口、同版公共AGENTS，以及公共WORK第6节结果、第8节独立接续、第9节分轴结论。已读且指纹不变的规则复用。不得采用后来公共版本或读其它模式替换合同。
2. 本卡配套DocuN/evidence/TASK-126/orchestration-20261022/input-manifest.json、raw-evidence-index.json和permit.json。先独立核六文件及关键直接依赖身份，漂移只停止相应对象并报告具体path/hash，不能对旧快照签当前结论。
3. DocuN/tasks/TASK-125.md原始完整合同，包含正常首次空库、固定001—015、关闭配置、角色分工、非原子整包、提交未知不重试及本地离线边界。本卡不改变其目标或增加新的产品Must。
4. 六份最终文件全文、execution/changes.patch及pre/README.md；其余五文件原为不存在。先以原合同和源码形成独立判断，再查看测试和执行记录，不以工程自评替代判断。
5. backend/migrations/001—015，按清单逐项核原字节hash与当前schema_profiles；原SQL未改，不重审已验SQL全部逻辑。重点读安装依赖所需013控制行/R01、014/R02、015/R03与角色/guard，和backend/app/data_exit/schema_profiles.py、schema_checks.py、q_roles.py、files.py、config.py的直接相关职责。必要时只读现有schema.py/contracts.py等直接依赖。
6. 固定关闭模板config/activity.example.json、integration.example.json、q-approval.example.json、preview.example.json及data-exit.example.json，原deploy/start_local.py、initialize-materials.py、compose.local.yml。只核新工具与正常启动/原profile的接口相容和真实副作用边界，不另做预览镜像或Compose部署审计。
7. 原始18方法、harness/runner、两批command/output/summary、tested-before-batch-01/02、post/pre-snapshot及source-preservation。再读command-ledger、junction-diagnostic和correction-01中的实际操作/错误/修正/预算事实；作者推断只作待核事实，不当结论。

不读DocuN/results/TASK-125-result.md、实现聊天、完整思考、自评及主控对工程优劣的结论。可读取本卡列明的原始日志、差异和身份元数据。若偶然接触，披露内容、时点及对独立性的影响，不伪称从未接触。旧124窗口若已读同一已验源码，仅补真实新差异，不重复旧13方法或原业务审计。

## 当前冻结对象

以下是主控当前重算并与批2受测及post副本相符的对象身份，仅表示身份，不预设代码结论。

- deploy/initialize_normal.py，28872字节，e112ce498f73371e6d788ed834c4c0414f3c8728579ec1ddc9df6c4942ffce5d。
- deploy/normal_install_manifest.json，4325字节，f2ed126daa1c5a982b490a9343d6c17053c0f385e7a2f55676ecf4132dd2abf0。
- deploy/normal-install.md，10496字节，dc46e05bb8e01873c5ce359a9d2665d57e27e4c9a5d89c11ade18fd4128c61cc。
- config/normal-install.example.json，869字节，95c97092a95fd39b116fe4e85fd4d5d4c7bb6757fc45efe76cc600863b55df3b。
- backend/tests/test_normal_install.py，26021字节，ca2fb5fa09776a73e6e8983dd2a47f9be399dcc141ea196f31ec8a6cf69e4633。
- README.md，27130字节，7ebb7d680949ce10c9c63f2e31b26f318145eba3309ab42e1891783526602db8。

README的pre为0410c7573027f7f6e75635c3a8d050e2be375d98ab0a4b503ddf3e076104d938。其余原迁移/运行入口/产品app/原模板/依赖锁不在125写入范围。

## 一次集中审查标准

### A 默认关闭、本地输入及计划

默认/help/坏参数/plan是否确实不会连接PG、启动进程、读取真实凭据、装载app/ControlHub/QAuthority或写安装结果。确认plan的结构通过、输入不完整、真实目标未观察和安装/资格未验证可区分，不把示例/null/字节长度误当实际ready。

校验原始15份固定白名单/顺序/hash与正式profile，不glob并吸纳未来SQL；固定清单不是由调用者可替换的信任根。考察配置严格类型、对象标识、目标身份冲突和文件路径/junction/NTFS别名/输出冲突边界；按实际威胁和原合同判断，不要求能抵御拥有操作系统管理员权限的人篡改整个产品。路径TOCTOU只在可触达且影响原边界时定级，不机械把任意理论竞态当P1。

### B 身份和空库预检

显式apply在DDL/DCL/业务写之前是否核精确loopback连接、实际数据库名/OID/system_identifier/安装身份/PG版本、全新空库与独占集群、vector适用性及全局角色碰撞。主机映射地址与PG服务端实际地址应正确区分，不错误要求两端同端口，也不因允许容器NAT绕开真实身份核对。

不得静默采用旧用户/TESTONLY/共享角色或重置其密码。确切输入缺失、目标不符、非空/碰撞时应零数据库写。安装意图收据的本地记录不等于DDL或账本写入，按真实副作用区分。

### C 迁移顺序和中断语义

逐项对账完整001—015固定原SQL、013后normal/R01控制行、014/R02和015/R03以及最终schema/role检查，核现有模型/函数/guard实际所需字段和顺序。不得替换CREATE ROLE、去掉010/011碰撞guard、规范化SQL以伪造hash或从tests/DocuN读取实现。

各文件原BEGIN/COMMIT须保留，不承诺整包一个原子事务。检查多语句结果集/COMMIT确认、局部阶段、响应丢失、最后核验失败、收据写入失败和重复apply的实际路径。已确认与提交未知不能混淆，不能误记整体installed、自动重放/清空或使verify写入。收据仅部署元数据，不是新的授权或金融账。

### D 角色及真实可用性

检查登录创建、业务/快照职责组、INHERIT/SET/ADMIN选项、CONNECT/对象权限、安装管理员与业务进程的隔离。确认新工具真正复用当前schema_checks/q_roles的实际能力检查，包括传递SET/INHERIT/ADMIN及owner路径，而非仅直接membership。

重点找会导致未来合法首次安装必败、最终业务连接不可用或snapshot越权的确定代码问题，不只复述18个替身用例。也不把首次安装没有覆盖就地升级判为本范围缺陷；其明确只支持独立新集群空库。PG语法/实际ACL尚未运行需分清静态可判与动态未知，不凭Mock称真实成功。

### E 凭据、关闭配置和启动兼容

凭据只按显式未来安全通道读取，不能进入argv、说明、错误/日志/计划/安装收据；未知异常内容不外泄。维护摘要按既有模型只应写DB，不成为公开安装收据内容。示例和原原生模板保持关闭，不构造grant、operator批准、T0或真实Q根。不新增旧loader不支持字段来冒充关闭。

新工具不能暗改start_local重开、旧001初始化或原source/readonly恢复资格。README和说明里的参数必须对应最终真实入口，无不存在参数，准确说明未来独审/精确许可与目前未运行边界。不要把外部token/账号仍缺变成此离线工程必须重复研究的门槛。

### F 测试、字节绑定及执行控制

独立核批2的18方法、0失败/错误/skip、exit0及实际受测六文件与最终字节一致。读harness/runner，判断隔离、调用记录器、审计钩子和纯角色样本真实能证明什么；禁止将0计数字段本身当全系统无副作用的独立证明。核批1的junction夹具失败原文、后续实际junction断言与NAT修正是否对应实际增量，不能篡改首批为通过。

审两批上限、单批600秒、许可24h、工具10800含900收尾的事实。工程精确工具总wall为unknown、保守列支3600/10800；检查可恢复记录/封存时间能否支持，不能把两个进程实测之和当总投入。脚本预算/结果保存的缺失和偏差据实分级，未知不伪成精确合规或已违规。旧120/117历史失败与原123/124封存账均不清零。

本地NTFS junction夹具留在125的execution/scratch，允许只读核实际reparse目标与原记录的范围，不能为审计重新创建或删除。读任何嵌套目录前查reparse边界，不递归跟随junction扫描。

### G 后续最小真实验证清单

按真实新风险给一份可直接编排的有限清单，精确指到安装入口/观察项、适用状态和现存缺口。至少包括新正常空库完整001—015/R03及业务/快照实际角色与连接、关闭配置下正常启动/同库重开/停止、身份/空库/碰撞零写拒绝、一次安装中断或提交未知保留与无自动重放、成功收据verify只读。安全失败可用单个有界事务/只读比较或预先构造状态完成的，不默认各建一套容器或重跑全项目。

需要补的用例说明真实观察与最少资源，不在本卡编写/运行。不会因本卡动态额度0就判代码自动失败，也不将后续PG未跑写成当前动态通过。不得要求已可静态确定的夹具错误等到未来再耗真实额度。

## 范围、资源及停止

只读上述冻结对象及必要直接依赖。只写TASK126/audit证据和TASK126-result.md，不改源码、测试、SQL、配置、README、dist、旧证据、原结果、主控orchestration、DocuS或公共库。不读实际local/private配置、.runtime、凭据库、账号后台、用户资料/库或旧封存数据库。

允许PowerShell/标准库作有界文件读取、hash、JSON、文本diff及AST分析。禁止导入/运行产品、安装器CLI（含help/plan）、compile/unittest、PG/Docker/Compose/端口/应用/浏览器/Job/预览/模型/Embedding/网络、依赖安装和Git写入；真实资源与费用额度全0。不得用不可信源文件作为可执行脚本加载；不创建子Agent或发外部消息。

本卡新工具wall上限3600秒，含480秒保存，单命令通常60秒，日历permit签发至24h，先到停止。足够一次覆盖即停；不为用尽预算扩审。旧TASK124余量和125未用第三批不是本卡许可。根因/对象不稳定、需业务修改、新重大决定或预算到门时，停止相应审查，完成不受阻部分后带精确缺口回传。

确定缺陷按P0—P3，给来源、触发、影响及最小修正，修复归原125工程窗口。本卡不得直接修复；发现明确数据破坏/凭据泄露先留证回报，其余完成一次全范围审查后统一交回。非阻塞观察不自动升级新硬门槛，审计范围外增强不作为本次关闭条件。

## 回传

结果先给三轴结论和可否进入未来精确首次安装运行门，列独立性、六文件及直接依赖hash、审查范围、逐项事实定位、确定问题/条件/未知、原18方法证据适用性、失败和执行账、后续最小真实验证清单、需主控同步文档与最少人工。保存完整报告并复读，历史补证按轮次追加不改旧结论。

不能填写主控最终验收或签Q、真实安装/权限/语义、STEP018/019/020、M1或项目通过。无须用户提供key、开服务、释放内存或删除文件。完成后只回复一句话结论及可点击的D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-126-result.md绝对路径，用户带回主控。
