# TASK-126 / R-120 review-01 双缺陷修正独立增量复核 当前有效

## 唯一目标与四个问题

你继续原TASK126独审责任，只对稳定修复增量完成一次独立复核。不重新做首轮安装器完整审查，不运行任何产品、测试或服务，不引入新的计量/账号研究。

本轮回答四问。

1. F126-01 P1是否消除。真实产品connect是否显式固定host和hostaddr为原配置允许的127.0.0.1，apply/verify是否共享这一路径；原真实数据库身份和合法容器NAT语义是否保留，是否不靠全局环境修改或预检后的身份查询掩盖认证目的地。
2. F126-02 P2是否消除。原拼写的reparse/junction拒绝是否在物理长路径身份归一之前；实际父目录与项目根归一及归一失败关闭能否封闭已证8.3别名路径，并覆盖new_output、plan输出、Journal/apply收据，保留正常输出、排他创建和完整收据verify仅读。
3. 原始batch03的9方法及三文件最终字节、明确选例/继承和控制记录是否真实对应修正；未变12方法、旧18方法/首轮其它结论在哪些范围能继承。不能以参数记录器、零字段或本地文件元数据称真实TCP/认证/PG/ACL通过。
4. 根据上述事实更新当前代码门/证据轴/控制轴结论，给两项发现逐项关闭或保留理由；首轮最小真实验证清单仅列因本次变化而确有必要的差异，没有差异即明确沿用。不新写一份同样部署设计。

交付仍为D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-126-result.md，在review-01置顶追加完整增量结论，原33379字节首轮全文及失败结论完整保留。新增原始核证只进D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-126/audit/review-01/，不改首轮audit文件。

## 身份、规则与基线

项目根D:/shspic/project_NO3_RetroLume-agent，入口同根AGENTS.md。模式task_model，V4.0/公共AGENTS CHG-0003，来源D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4。锁定规则沿DocuN/evidence/v4-migration-20260930/rules-snapshot.json，当前需求v1.4、架构v1.68、执行动态v2.96。已读且指纹不变规则和首轮上下文直接复用，只补新增合同与实际差异。

接收A+，继续刚完成TASK126首轮的原独审窗口，须未参与TASK125修复实施或测试设计，不得让125工程窗口自审。若原独立窗口确不可用，才用新隔离独审窗口接续同号，先披露独立性并读取原结论/必要证据，仍不重审未变完整业务。真实客户端/模型按实际登记，不因标签变化自动作废已有工作。

本轮仍TASK126/R120，父TASK125/R119，STEP-018/020及未来019适用安全证据。不占新TASK或R。工程修复01已返回并冻结，没有并行写入；本卡待人工转交，未声称接收/启动。旧首轮审计交付已结束，本卡才给明确的有限增量许可。

当前三个变化对象的冻结hash如下。

- deploy/initialize_normal.py，29403字节，68d7b71fc7296111e894df4cba21a4ed7830f9cff069c1fc500dfbd7734c0a09。
- backend/tests/test_normal_install.py，32786字节，93dabd4887760641884fc7ca5d5c83e520522563ea2d44be4dc2e72db320c3b7。
- deploy/normal-install.md，10845字节，fb553199dafb11be8608a3608ff2f18778f07acbff265badb2994855c0fd6ddb。

未变README、固定清单、安装示例、001—015和原业务/profile/角色检查保持首轮身份与结论。原F126-01/F126-02在主控账仍开放，工程自评不能替代本轮独立判断。原报告hash为b1f52e0284e37b5e67f28ef1a1c2dee7d1c7d255a3e090d1478bc5747d72b1d3，原首轮代码门不通过历史不得追改。

## 最小充分独立输入

1. 根入口、当前有效卡及主控DocuN/evidence/TASK-126/orchestration-review01-20261022/input-manifest.json、raw-evidence-index.json和permit.json，核本轮真实范围和冻结身份。
2. 原TASK125审计修复01合同的范围与验收部分，以及你自己的TASK126首轮F126-01/F126-02及其原始依据。原合同已读内容不重读；不读TASK125统一结果或result-prefix.md，不读工程聊天/思考/自评。偶然接触如实披露，不伪称从未接触。
3. execution/repair-01/changes.patch、pre/中的三产品原件、当前三个完整文件及post副本。先以原始缺陷和合同形成判断，再检查已有测试对实际风险的证明边界。完整源码可读，但审查归属限定本次变化及其传导。
4. 现有psycopg3.3.5的必要驱动源码、当前Python标准库pathlib.py/ntpath.py相关严格resolve/realpath实现。主控清单给出当前实际绝对路径/hash，不猜安装目录。只读源码，不import或执行产品、驱动、安装器CLI。对当前Windows实现判断，Linux并非本轮新增交付平台。
5. repair-01的batch-03-selection、tested-before-batch-03、batch-03-start/command/output/summary、harness/runner、post/pre-snapshot、junction-before、command-ledger及必要旧batch02原件。不要执行它们，也不只信作者的match布尔或硬编码计数。

本轮主控身份元数据用于找到原件，不提供产品优劣预结论。不得把实现报告放进独立输入。原首轮已核的SQL顺序、角色分工、未知提交/不重放等未变主体直接继承；若本次helper修改传导到Journal或apply/verify，则只追对应调用影响。

## 对新增证据的具体核点

F126-01检查test19实际替换驱动入口之前后顺序、局部合成PGHOSTADDR/PGHOST、真实产品connect的direct/apply/verify三用途kwargs和当前驱动显式参数优先关系。保留客户端127.0.0.1映射端口与服务端172.18.0.2:5432不同的语义。不得为了证明修复尝试向非loopback连接或运行真实认证。

F126-02检查test20是否取本机真实GetShortPathNameW/GetLongPathNameW和samefile，backend/deploy/config三类实际别名是否命中同一保护；写入探针是否只阻断写、没有把危险路径先改为安全路径或伪造lstat/物理身份。test21的归一失败分支与原test07正常/冲突、08真实junction及11/12/13收据路径和17脱敏要与实际代码对上。

主控未新增NTFS探针或重建夹具，原junction由已有元数据和原证据引用。本轮若需确认当前fixture，只读lstat/readlink即可，不跟随递归或新建/删除。受信目录下的对手并发替换仍是原条件风险，不将未获证实的任意理论竞态自动升级为新P1；也不能用它掩盖确定的本次别名回归。

batch03原日志9/9、fail/error/skip0及exit0是已有待你核证的客观输入，不要求重跑。测试正文共原18方法加新19/20/21；原18 AST正文相符并不单独证明12未跑方法仍有效，须结合两处产品diff与调用影响判断继承。不得宣称最终21项全跑或把旧18和新9简单相加为不同方法数量。

工程本轮600秒和累计4200/10800是保守账，精确总工具wall仍unknown；实际进程1.7951588000287302秒、harness0.6536168999737129秒和工具外层2.6215342秒不同层级不相加。累计3/4批，batch04未用。保持原批1失败、原中间版未完整存档、平台原批准回执缺失等边界，不能从日历包络直接签精确控制合规。

读取文件名时曾一次误枚举旧scratch的范围偏差已留在本轮账，未声明读旧正文或改删旧对象。按实际证据定级，不补造原始命令或将unknown转成已违规。新增11个测试目录和junction未变记录可以在原summary/post中核对，禁止借审计整理或删除。

## 预算、权限及停止

本轮从原TASK126已封存余量中明确恢复最多1200秒工具，含240秒保存；原保守1800/3600、精确unknown照留，总cap3600不变。原截止2026-10-23T09:56:00.006928+08:00不重置，工具或日历先到门停止；单命令通常60秒，不为用满预算扩审。完成四问即可统一回传。

只允许PowerShell/标准库的有界文件读取、hash、JSON、diff和AST分析，以及保存指定报告/新证据。产品/测试/SQL/配置/README/DocuS/公共库、原审计/工程证据及主控orchestration不可改。不能访问实际local/private配置、.runtime、用户资料/库、凭据或账号后台。

产品导入、CLI/help/plan/apply、compile/unittest、PG/Docker/Compose、端口/服务、浏览器/Job/预览、provider/Embedding/网络、安装依赖/Git写入/费用/委派全部0。不通过执行新harness来确认旧日志，不创建短别名/junction或系统设置。

冻结对象漂移则只停止对应复核，带具体path/hash和影响交回。新确定风险直接由增量引出时定位并说明，不借机扩审整仓；必要缺口保存事实，不能直接修复或虚签关闭。无新增产品变化和直接风险就不得要求再全审或无理由重跑18/9项。

## 回传与验收边界

review-01置顶写独立性、精确范围/读取hash、两项逐一关闭或保留的代码事实、当前三轴结论、9方法字节绑定/继承依据/未验证项、本轮实际命令/时间/失败/unknown和原账累计、最小真实清单差异。原首轮全文及报告hash链完整保留，新增原始输出只存audit/review-01。

报告结论限定为当前代码门可通过/仍不通过及已有证据范围，不签真实PG/认证/ACL/正常安装/正常启动或Q启用。最终TASK125关闭和后续真实资源许可由主控另行裁定；Q继续冻结，T0为空，STEP018/019/020、M1/项目不宣告通过。

无须用户提供key、开服务、释放内存或删文件。保存并复读原结果D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-126-result.md，只回复一句话结论和可点击完整绝对路径，供用户带回。

## 以下为原TASK126完整审计卡 原字节保留

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
