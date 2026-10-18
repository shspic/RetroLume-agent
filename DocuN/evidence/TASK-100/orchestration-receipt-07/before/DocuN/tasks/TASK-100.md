# TASK-100 / R-094 定向修复04 — 有限答案可靠解析与推进屏障收口

本节为当前有效合同。沿用原TASK-100/R-094，父TASK-099/R-093，独立审计TASK-101/R-095，STEP-009—012，F01/DEF-008/P1。只恢复本节明确的离线修复范围；下面修复03及其他历史许可均已结束。

## 目标与交付

你是本卡实现与验证执行者，在同一卡内完成剩余F01修复、受影响离线验证、最终字节绑定和统一回传，不担任编排或独立审计者。

目标是：只有可可靠识别的明确肯定有限数值答案，才能支持数值维度被核定。否定、不确定、假设、引用示例或无法可靠解析的文字，即使只包含一个与参考相同的数值，也须保留未检验/unknown，不能被模型的全met反馈升级成独立观察或evidence_sufficient。

交付为有限解析修复候选、真实函数的正反例及进度合并验证、完整pre/diff/post和as-run身份、投入与失败账。结果置顶续写 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-100-result.md，标“定向修复04”，保留原49113字节全文。新证据仅写 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/answer-support-repair-04/。

完成标准是：下文两条确定触发均闭合；不同实例、无曝光、含retest、模型全met的反例不能推进；既有明确正确答案、单位换算、真实值/单位冲突与参考自身核查保留；受影响最终字节的定向离线批通过，未变高风险权威和原证据零漂移。完成即停，不为获得新整批PG/浏览器PASS重复旧链。

## 项目、规则与接收安排

项目根目录 D:/shspic/project_NO3_RetroLume-agent；根入口 D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。需求v1.1不变，架构v0.85，唯一执行动态v2.07，当前公共阶段07。

模式task_model，公共规则锁定V4.0/AGENTS CHG-0003。公共AGENTS为 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4/DocuS/AGENTS.MD；主控WORK为同公共根 DocuS/WORK.MD，第4/6/8/9章为本卡组织、结果、接续与核证依据。当前07为同公共根 task_model/prompts/07_开发执行循环.md；完整合同结构依 task_model/TASK_TEMPLATE.md。七项实际锁定指纹见 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/v4-migration-20260930/rules-snapshot.json。执行者只补读入口、公共AGENTS及本卡必需变化；同窗未变且已读正文直接复用，不自动采用新版或其他模式。

任务类型为同边界产品修复及离线定向验证，关联G8、F01/DEF-008、V04/V06/V20与H1，原需求/架构编号沿099和100原合同，不新增持久模型或批准包。授权来自用户对099的G8-P批准及已授权任务的必要修复，终点为候选交付，不能签G8/STEP/M-1/项目或发布。

接收为原TASK-100审计修复03实现窗口，执行档A+增强执行。该窗口上一回报实际客户端Codex desktop、系统标识GPT-6，具体部署型号未暴露；标签只作如实登记，不按品牌重新评价已完成工作。有限语义与推进正确性需要增强推理，原上下文有效，优先原窗口；不能改用TASK-101独立审计窗口。原窗口确不可续时才用新的A+实现窗口，先交接本卡和原结果，不清零历史，不自行派子Agent。

当前快照在 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/orchestration-receipt-06/essential-identities.json 与 identity-checks.json；编排已核132当前、7规则、18保护对象及实际101报告共158项一致。关键SHA-256如下，首改前核对，不符查明而不覆盖：

- backend/app/learning/teaching_policy.py：7a1a89e64d94e8da5d85917e6d269c7dc7f84715c5171e1d4d016315051fc9c7。
- backend/app/learning/teaching_progress.py：edb9d4ac91711d8be82443b3ba8a38f114bfb3df885faedc1ea8c2aa0fb68bb6。
- backend/app/activities/teaching_repository.py：7d9e28575780e4ac3665f3197b022ff1a3a5c27fc49877067de8f55aef4fe127。
- backend/tests/test_task100_repair.py：3f48312285a42c771b39f5482bba6901eb2f7900637de37988f34a9a7d7158cc。
- backend/tests/test_teaching_policy.py：a7bc7670e1bad6da45a50edb79210273fe134d2a71e55d0aef8f37d862d139d0。
- backend/migrations/009_teaching.sql：11b1c2bc8cb2482a4fa509b897c3afb8f3f5f7be3eb4e8e4aab559706944c1a3。
- TASK-101-result.md：b75f00d8a9a1e3c564d221dc70ca591cb0fa0a23ddf276a691cd1d323ba1dbb2；TASK-099-result.md：0f38de84d6036e48a9fa544ba8304b37a72cf89e56e29fc05bef500609cc0e67。

历史投入不重置：100修复03四入口全部结束，entry4/4、container-start4/4、app3/3、SUP12/18、browser2/3、driver2/3、build2/2；离线78.735秒、真实199.422秒、清理26.906秒、主动10059.821秒为其冻结口径。B1/B2/B3总批FAIL、B4只读专项PASS原样保留。续作02、续作01和初轮的原入口、漏计5.940秒、未知开销与失败另列保留，不借旧名义余额。101 review-02新增业务/资源0，主动6778.853/10800秒及已登记元数据3.725/600秒、未逐次登记开销未知，许可结束，不能转借。

本轮新许可 TASK-100-F01-repair-04-20261005：主动3600秒、离线验证累计600秒，最多3个定向测试批；当前新增使用0，调度待转交，没有实际接收、开始或运行事实。正常主批一次，最多两次有明确修正依据的受影响复检，单批有界不超过60秒。所有读取、修复、取证及封装计入主动时间，测试子时长另记，不以系统日期替代单调截止。旧累计账与本轮新账并列，新许可不追认旧偏差。

## 背景与最小充分上下文

101 review-02审计交付已由编排验收通过；代码轴仍因F01不通过。DEF-009—018在报告的有限范围关闭，DEF-005剩余逐记录来源/公开投影范围也已关闭；旧缺原件、真实provider和其他分层限制仍保留。本卡不重新实现或验证已关闭项。

当前 teaching_policy._answer_quantity 在整段文字finditer，再按参考量纲筛唯一候选。因此“平均速度不等于1m/s”和“答案未知，可能1m/s”会得到实际答案1m/s；derive_support_checks把它标matched，rebuild_progress不能再收紧模型met。两个不同instance_data、无曝光且含retest的答案可误入independent_answers并推进。这是当前源码可确定的B级缺陷；101没有运行这些新反例，也没有宣称真实provider误判。

旧“不读answer_text”根因已修，60m/s与0.01m/s即使模型全met也不推进已由真实旧证据证明；这些事实不因新解析遗漏失效。只需补可靠解析这一环，不建设开放自然语言判分器。

按顺序读取，已有同窗未变资料复用：

- 项目入口与锁定公共AGENTS；本卡全文。
- D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-101/review-02/F01-static-finding.md；该件SHA cf78e29a0563e925253f46cabd90f9e69f2fd51256b4cf4815b04eb7c0e0eaca。TASK-101-result.md仅本次F01及有限继承/未验证段，不从零重读两轮完整审计。
- D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-099-result.md第5.2节有限支持检查、进度独立性相关合同；当前 D:/shspic/project_NO3_RetroLume-agent/DocuS/架构动态文档.MD顶部与 D:/shspic/project_NO3_RetroLume-agent/DocuS/执行动态文档.MD顶部。用户原始需求只读，位置为 D:/shspic/project_NO3_RetroLume-agent/DocuS/原始需求文档.MD，不要求为本次修复全文重读。
- D:/shspic/project_NO3_RetroLume-agent/backend/app/learning/teaching_policy.py 的有限解析/derive_support_checks；同目录teaching_progress.py的实际rebuild_progress； D:/shspic/project_NO3_RetroLume-agent/backend/app/activities/teaching_repository.py 中实际支持检查与progress提交调用点。仅读直接依赖，不执行仓储。
- D:/shspic/project_NO3_RetroLume-agent/backend/tests/test_task100_repair.py 中相关两个离线方法及numeric PG方法的既有合法文字； D:/shspic/project_NO3_RetroLume-agent/backend/tests/test_teaching_policy.py 中支持性与进度方法。按需只读相关合成样例，确认改动所影响的真实文字形式，不读取私有配置。

必要输入路径不可读时用卡内缺陷/合同摘录及同版本已有原件；关键缺失无法补齐则仅交回受影响部分，不能假称读取或复用。

## 执行边界与资源

允许修改仅以下对象：

- D:/shspic/project_NO3_RetroLume-agent/backend/app/learning/teaching_policy.py：_answer_quantity及本次必需的局部解析辅助，必要时derive_support_checks的有限答案接入；不修改参考算术域、其他政策函数或对外签名。
- D:/shspic/project_NO3_RetroLume-agent/backend/tests/test_task100_repair.py：仅两个相关离线方法补正反例；PG/HTTP/控制类与其他方法原字节保护。
- D:/shspic/project_NO3_RetroLume-agent/backend/tests/test_teaching_policy.py：仅本次相关离线用例的必要增加，不弱化旧断言。
- 可新增一个纯离线测试 D:/shspic/project_NO3_RetroLume-agent/backend/tests/test_task100_answer_support.py，实际调用产品解析、support和rebuild_progress，不能增加通用测试平台、数据库替身或业务runner。
- 本轮指定evidence新目录和原TASK-100-result.md的新增前缀。写结果前保存原结果hash/长度，新增段之外必须逐字节不变。

teaching_progress.py与teaching_repository.py只读；现有unknown收紧已经存在，优先由解析修正闭合。若真实调用冲突使额外生产文件、持久模型、接口或仓储提交变化成为必需，先完成不受阻部分，带明确调用点及最小差异交回，不自行扩大范围。

实现由你自主选择闭集肯定语法或已有明确结构位置，须给完整接受/拒绝语法和边界理由。不能只加“不等于/可能”黑名单、仅取第一/最后数值、按量纲筛唯一候选，或放行任意解释尾段。未能可靠识别整个回答的确定断言时按unknown；不得把unknown伪造为conflict来阻止推进。可识别首部明确结果及有限辅助说明，但整个文本须符合可说明的有限肯定形式，不能跳过否定、猜测或开放尾文。

兼容目标包括明确的1m/s、空白/现有单位写法、60m/min与约0.5无单位样例，以及已验的“1m/s，2分钟=120秒”和“1m/s；先统一秒，单位与数量级合理”。相关正常样例用离线真函数核对；多值歧义仍保留unknown。若某旧开放表达无法可靠支持，须具体披露，不能静默改旧PASS或扩大到任意语言评分。原参考自身合法/冲突、60/0.01及单位冲突、程序不执行、有限Decimal域、独立性/曝光/纠错纪律不变。

禁止改001—009、仓储/service/API/contracts/views、worker/launcher/SUP/Job、工具/模型gate、资料/PDF、前端源码及dist、依赖锁、配置、DocuS/公共规则、归档、其他结果与旧证据。冻结范围以repair03最终132对象及18保护对象为基线，除明确写权外保持不变。不运行全仓测试、旧PG/HTTP/Windows/browser控制器或任何旧真实入口。

本卡PG/HTTP服务器/Docker/容器start/应用/SUP/Job/driver/browser/frontend-build/真实模型工具/付费/联网安装/Git写入均为0。也不连接用户库或合成库，不重置凭据，不DELETE/DROP/TRUNCATE，不改系统/DB时间。原容器、卷、库及数据保持，原2026-10-05T19:43:39+08停止观察仅作为历史时点，不因本卡未启资源而虚构当前检查。

测试用项目既有 D:/shspic/project_NO3_RetroLume-agent/backend/.venv/Scripts/python.exe，不安装依赖、不读取真实配置。允许纯离线测试过程导入受影响产品函数，禁止触发服务器或数据库基类；使用-B避免pyc。未需运行独立compile批，实际单元验证足够时直接完成。

本卡独占policy及相关测试文件，无并行实现或审计。原101窗口此时只等待结果，下一增量复核前冻结最终候选。整合与共享DEF/总状态/CHG由编排串行维护。没有新TASK号或后续审计已派发事实。

## 验证、证据与审计关系

现在验证的理由仅为剩余P1能从实际答案传播到进度，不是重新证明未改的数据库事务、停止/退款或界面。以真实derive_support_checks与rebuild_progress作为判定对象，不mock这两个函数、Decimal或解析结果，不用SQL字符串断言替代业务证据。

本卡至少覆盖以下紧密矩阵，可合并测试方法但保留逐样本结果：

- 确定负例“平均速度不等于1m/s”和“答案未知，可能1m/s”：参考自身matched、answer_status未检验、对应数值维度unknown，不能是matched或伪造冲突。
- 同一根因的单值否定/不确定在数值之前和之后、只引用参考/例子、假设/问句、多个矛盾候选、未知开放文字；这些不能靠唯一同量纲量值通过。保留原歧义、科学计数等已定unknown边界。
- 明确正确数值与上述有限正常辅助说明仍matched；60m/min转换正确；60m/s、0.01m/s与1m的真实值/单位冲突仍conflict，参考自身核算分别成立。约0.5无单位及程序原文不执行沿既有纪律。
- 为两条确定负例分别构造有效的两套不同练习/answer ID，一题initial、一题retest，均无先行曝光，模型维度全met。instance_data、参考left/right及正确量值互相一致；直接调用真实rebuild_progress，independent_answers为空且status非evidence_sufficient。不要用结构不合法或重复实例使反例天然被挡，不虚构这个返回值没有的advance字段。
- 一个明确正确实例加一个未知实例最多一个独立观察；两个明确正确、不同实例且含retest仍可达evidence_sufficient。相同答案ID/相同实例、曝光、continuation与争议等不受影响者复用现有证明，不为这些再扩真实矩阵。
- 将不确定文本的进度解释与已存support读法核对，证明实际仓储调用仍采用同一个纯函数；这是源码调用证据，不宣称本卡新PG提交通过。

默认一个主离线批：tests.test_teaching_policy、若新增则tests.test_task100_answer_support，以及 tests.test_task100_repair.RepairOfflineTests 的两个受影响方法，按最终实际名称记录。不得整文件运行test_task100_repair而带入PG/HTTP/控制类。若扩入另一旧离线方法，须明确直接依赖且仍在总批/时间内，不机械重跑原76项。现有充分证据直接引用。

最多3批含失败，每批动作前计数，超时/失败原文保留；正常通过后停止，只有实际失败或新的未解直接风险才有据修正复检。不能因预算尚有余额加样本到无关阶段。保存真实命令、cwd、Python身份、开始/结束/单调耗时/退出码、方法与subtest计数，不能把汇总数冒称独立方法数。首读即固定主动计时；未能精确记录的开销标未知而不假称0。

首改前保存全部目标pre/hash；每个实际测试批保存被测产品/测试源码完整快照及hash，测试前后核一致，最终新增正确统一diff及post/hash。旧测试字节的局部回放不能作为最终版通过；发生修正只重验受影响部分并逐方法解释最终适用性。原132对象/18保护对象/七规则与旧证据身份复用，不重复2618原件全hash。最终对所有本次可写对象和范围外冻结文件作一次差异核，hash只证明身份，不替代结果断言。

原101 review-02是本轮充分的独立基线：F02—F09/E02/E01、旧真实numeric冲突和正确推进、当前源码—bundle—UI绑定与执行控制均按报告有限范围继承。部分旧表达若受本次解析直接影响，在本轮纯函数矩阵映射其新行为，不把旧PG/Windows总体重签当前版，不撤销其事务/身份/停止/正文等未改事实。旧原始FAIL及缺原件限制仍保留。

本轮稳定完整返回后，由编排另更新原TASK-101/R-095合同，只在原独立窗口核F01实际差异、对应离线原件、真实调用传播和未变基线；这是剩余P1所需独立确认，不从零重复两次全面审计。现在不先转审计、不让实现者自签。若离线纯函数证据足够，不为汇总PASS另设PG/Windows/browser门。

## 停止与回传

卡内连续完成，不按解析、测试、证据分别回传。完成全部目标即停；超范围、需要新语义/持久字段、关键前提推翻、根因不稳、两次有依据修正仍失败或任一新增上限触顶时，保存事实并停止受影响部分，不能暗开第四批或真实资源。

沿用同TASK/R，新段只称定向修复04，不重置原失败/投入/预算，不改101独立结果。封装及最终保存属于主动预算，不能在宣告停止后暗跑。反例离线运行A级只证明真实函数的本地结果，源码传播B级只证明调用关系；均不签新的PG/HTTP/Windows或真实provider质量。

完整结果仍为 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-100-result.md。先写一句结论与候选/停止状态，随后写实际语法边界、差异作用、F01逐样本/进度结果、最终字节绑定及证据导航、真实命令与投入、失败/修正和未验证限制、旧证据继承/不适用、偏差、待编排同步项及人工事项。旧49113字节完整历史逐字节保留，不把旧“全部修完”改写成新审计通过。

结果保存可读后，回复仅一句结论和完整绝对路径，供用户带回编排。不得签DEF-008关闭、G8、STEP-009—012、M-1或项目完成；这些由编排据原101增量结论裁定。真正无法保存才标未保存并提供必要正文，不给虚构链接。

## 必要人工与待同步信息

必要用户动作仅转交本完整卡，完成后带回结果文件路径；不需要提供密钥、启容器或另批准G8-P。发现关键原窗口不可续才说明替代窗口原因，已完成工作不按模型品牌重审。

由编排同步 D:/shspic/project_NO3_RetroLume-agent/DocuS/架构动态文档.MD、执行动态文档.MD、文档变更记录.MD，以及100/101的work-decision和完整卡；执行者不写这些共享文件。经验只报告经核实可复用候选，不占共享经验号或写公共库。

## 以下为已结束的原合同及全部历史
# TASK-100 / R-094 审计修复03已返回冻结通知（2026-10-05，当前）

修复03真实回传已完成编排普通回收，接受候选及有限证据；F/E和G8放行待101独立增量复核。全部运行许可结束，禁止启动repair-combo、readonly-browser-combo/main-combo或借用SUP/browser名义余额。当前产品、009、夹具、dist和原证据冻结，无并行业务运行。

原结果/许可/失败/历史原文保留；本次完整执行合同原字节见DocuN/evidence/TASK-100/orchestration-receipt-05/TASK-100-card-as-returned.md。此通知不修改被审实现，不签G8或父STEP，后续有据修正必须取得编排新合同。

## 以下为已结束的原合同及全部历史

# TASK-100 / R-094 审计修复03 — G8合同修正、内容依据与最终版本补证

本节为2026-10-05当前有效合同，覆盖下方旧冻结通知仅就本节明确范围及新许可生效；旧运行许可仍结束。沿用TASK-100/R-094，父TASK-099/R-093，审计TASK-101/R-095，STEP-009—012。你是实现与验证执行者，卡内连续完成一个完整修复成果，不签独立审计或编排验收。

## 目标与交付

一次修复TASK-101的F01—F09，修正E02的合成引用依据，并收口E01的最终版本证据限制。目标是正确处理有限答案支持、旧记录来源、严格输入、同键恢复、容量、G7目标沿用和完整教学读面；实际引用须支持计算、概念、程序三个已批准场景。修复、相关夹具、一次集中验证及必要范围内返工在卡内完成，整卡统一回传，不按单个发现或文件拆卡。

交付最终产品差异与完整pre/diff/post身份、有限内容oracle、最终被测字节、原始PG/HTTP/Windows/浏览器证据、全部尝试与资源账、证据适用性清单。结果沿用D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-100-result.md，置顶“审计修复03”，此前全文原字节保留。新普通证据仅写D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/audit-repair-03/，不覆盖旧原件。

完成标准为全部F/E逐项有修正或准确补证、最终实际受影响的正常/异常路径成立、源码与被测字节及dist绑定、失败/未运行不隐去、精确资源停止并保留。完整成果稳定后由原101独立窗口集中增量复核，本卡不自签G8、STEP、V19真实provider质量、M-1、部署或项目通过。

## 项目、规则与接收安排

项目根D:/shspic/project_NO3_RetroLume-agent，入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。模式task_model，锁定公共V4.0/AGENTS CHG-0003，公共库D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，只读。读取公共DocuS/AGENTS.MD；WORK第2/4/6/8/9章按执行职责适用；当前阶段task_model/prompts/07_开发执行循环.md，不读取其他模式替代合同。七指纹按项目DocuN/evidence/v4-migration-20260930/rules-snapshot.json，本轮核一致，不自动升级。需求v1.1、架构v0.83、执行动态v2.05。

类型为原合同内开发修复、合成定向验证和补证，L，C3/U3。接收A+增强执行，优先原TASK-100续作02最强业务实现窗口；能实际执行Windows/PG/浏览器完整链。客户端及实际型号如实登记，A+不冒充型号，不因已完成任务品牌而重审。若原窗口确已不可续，采用同能力新业务窗口并读齐交接，不使用101审计窗口，不自动派子Agent或并行执行。

授权依据为用户2026-10-02批准G8-P、DocuN/results/TASK-099-work-decision.md及持续推进授权；本轮是编排依据101审计组织的同边界修复，不新增业务范围或再次申请原批准包。授权终点是本卡候选交付及精确自有合成资源收尾，不含真实provider、付费、用户库或发布。

调度待转交，尚未声称接收或开始。原任务/R编号、失败、投入、源文件用户改动及历史许可不重置。新预算单列，不能借101未使用的显示probe或100旧SUP余额。

## 背景与最小充分上下文

101审计已完成且交付通过；G8当前不通过。141个当前合同/产品/保护对象/规则/报告身份经编排复核零漂移，审计报告hash b5db0b2e6f787fd6a3fb78ee1e4c1f6ee54b98114731890fb889accd88bd71b4。审计没有产品写入或新资源运行。2026-10-05T16:32:48+08只读检查：精确容器Exited(0)、Running=false/Pid=0，18100/55442无监听，无本卡运行进程；接手首次实际使用前再核实际状态，不能重复启动在途进程。

原续作02账终点为entry6/6、container-start5/5、app3/3、SUP21/24、browser3/3、driver3/3、build1/1；离线42.750、真实261.211、清理33.313秒，主动13643.958505为原分段口径并保留未知旧尾段。初轮至少9入口、至少一次start、漏5.940秒及续作01的4/4入口等历史不确定性照旧；六个原总批FAIL不改PASS。

逐方法原29PG/4HTTP OK不是“最终29PG通过”：前25PG依赖三个无完整中间原件的旧模块，最后4PG及HTTP/真实窗口只证明其具体范围。原连续8模型/1工具主链、来源冻结、晚到/UNKNOWN/取消/停止及重开等真实事实按101分级可复用；概念/程序“有据”内容层因引用无关不能继承。浏览器尾FAIL已独立判为夹具取字段错误，实际中文/字面脚本显示证据可采，无需只为把旧总批变绿重启。

按序读取以下必要材料；同窗读过且hash未变的原合同与旧原件直接复用，不全文重读历史：

1. 本节完整合同、项目入口、锁定公共规则、DocuS/执行动态文档.MD顶部，以及DocuN/results/TASK-100-work-decision.md本轮裁定。
2. DocuN/results/TASK-099-result.md第3—8节、V01—V20/H1—H4，sha 0f38de84d6036e48a9fa544ba8304b37a72cf89e56e29fc05bef500609cc0e67；099-work-decision的批准边界。原100完整执行合同原字节在DocuN/evidence/TASK-100/orchestration-receipt-03/TASK-100-card-as-returned.md，sha 7a1fb0226faf36d13c84b19c491cd9f016612eec9ca9fbb8763a0366cfc703ab。
3. DocuN/results/TASK-101-result.md全部F/E与验收映射；其evidence/source-prelog.md、method-bindings.md、database-http-method-runs.json、reconstructed-version-bindings-corrected.json、independent-content-citation-read.json、final-freeze-and-usage.json。实现者可读审计结果；不得让未来审计者读取你的完整聊天/推理。
4. 本轮DocuN/evidence/TASK-100/orchestration-receipt-04/continuation-input.json与baseline-checks.json是当前身份入口，不是运行通过证明；原100 continuation-02日志、许可/账、最终manifest按上述具体引用读取。
5. 实际直接源码和测试：activities/teaching_repository.py；learning/teaching_contracts、policy、progress、views、service、api、evidence及prompt；教学前端、G7入口直接读取调用；task100 synthetic_content、runner/control/support/windows_chain/浏览器与相应用例。G3/G4/D3/G5/G6/G7只读必要直接依赖，不重审整仓。

首改前存实际pre副本/hash并核本轮输入；核心基线teaching_repository.py=d2188480337d8d3cddb4e892387acd028f7e0577c3732017f6417af9ef204454，teaching_service.py=5f7c66482c6b5685665d7e75364ee931b5912cf24cb49899cdcf53aa6941e2c0，teaching_views.py=e9cead410475adbb0e41c3fd4f827688ff9f8446c35a58b7415894cef17653ab，009=11b1c2bc8cb2482a4fa509b897c3afb8f3f5f7be3eb4e8e4aab559706944c1a3。其他逐文件值在input中。无解释漂移先查明，不覆盖现有改动。关键材料不可访问只暂停依赖部分并明确缺口，不能假称已读。

## 执行边界与资源

下列十一个缺陷同卡处置，DEF映射由编排已占用，执行者不再自行选号：

- DEF-008/F01/P1：derive_support_checks目前不使用实际answer_text，只核参考自身运算。修为批准有限域内实际答案—数值/单位/数量级核对，与参考内部一致性分开；明确冲突收紧对应dimension，即使模型误判met也不能加入独立观察。参考120/120=1m/s、用户60m/s或0.01m/s须被屏障阻止；可靠解析不足返回未检验/unknown，不把参考算对当答案正确。保持Decimal/G5精度及开放概念/程序不自动执行评分，不引入任意自然语言判分器。
- DEF-009/F02/P1：只核当前activity_scope_sources会让有效新范围恢复旧源派生正文。用每条事实的source_refs及原source/version/revision/hash核真实资格，同一SQL快照覆盖workspace/record/history派生投影，expose写路径核原题实际来源。旧S1被替换/撤销后将活动改成有效S2或S1新版，旧题/反馈/路径正文及未暴露参考不得重新公开；用户答案和纠错原文、事实身份/历史保留。仍有效的旧历史按099分类，不能把“历史”一律当违规或把用户文字删除。不得放宽既有引用回查及出站冻结屏障。
- DEF-010/F03/P2：HTTP按stream累计到32768字节即拒绝超限，不先全量body缓冲；严格UTF-8解码、递归拒JSON重复键，保留认证和现有错误封套。重复嵌套goal、UTF-16/32、坏UTF-8及超限都零业务写入。
- DEF-011/F04/P2：同hash已accepted且launch_claimed_at为空的命令，用户显式同键再试可恢复原T-launch CAS一次。只能用持久原request/frozen context与真实当前资格；不以重新组包的新上下文替换已接受身份。并发至多一次claim/SUP/发送。已claim、无operation、started、UNKNOWN或旧版本事实仍只读核对，不重发/退款；GET永不执行。恢复资格及收据准确表达，兼容model/tool命令。
- DEF-012/F05/P2：活动锁内计已接受path数量，第32合法、第33拒，旧历史不清零，同键重放不占新数；其他容量与原序号守卫保持。
- DEF-013/F06/P2：接通用户明确G7“沿用此目标”和服务端有效当前G7 operation/hash/goal及来源核定，goal事实保留seed身份。直接无G7目标仍可用；假hash、错误kind/活动、陈旧/失效成果拒绝且零新事实/调用。seed不成为能力观察、不重入G7 first槽、不自动改目标，不把G7正文当新的出站授权。
- DEF-014/F07/P2：路径、已公开参考、反馈保留各自citation身份，接既有只读citation回查及原位置入口，包括PDF抽取序列/物理页标记，失败/失效如实显示；不从未暴露题目泄漏参考。补完整历史分页，前端使用后端cursor而非before_seq，旧页/409处理、只读选择及当前视图分离。不能只显示最近20条就称历史完整，不改旧PDF解析主体。
- DEF-015/F08/P2：编辑/草稿绑定完整activity/goal/path/node/exercise/answer及head revision身份，同题A1变A2须提示并保留未保存文字，不默默以新A2为旧输入supersedes。不要用每次轮询revision变化无条件清空编辑。历史R1→R2选择有独立序号或取消，迟到R1不得覆盖R2/纠错目标；切换/卸载后的回包同样不能污染。
- DEF-016/F09/P2：分字段执行原规范十进制字符串域，value及instance_data的value绝对值≤1e18，left/right沿G5≤1e12；tolerance非负≤1、至12位小数；拒JSON数值冒充字符串、超域/非法精度/非有限/科学计数注入。value=1e13不能因共用操作数上界拒绝。精度/单位展示按099，不扩G5域，失败保留已存答案。
- DEF-017/E02/P1：修synthetic_content固定evidence[0]，按每节点、参考维度与反馈论点选择实际支持资料。计算/原子性与隔离/程序条件与return分别有真实匹配片段，不能只通过目录成员检查。建立逐条内容oracle：实际论点、实际citation_id、实际目录正文/出处/hash、支持或不足及理由；内容判定与fixture选择逻辑分离，留给101独立逐例复核。重排目录仍正确，无支持时明确no_evidence/unknown，不能猜索引或用重写摘要掩盖旧无关引用。
- DEF-018/E01/P2：旧25PG仍为中间版A，不补造原件。先有限检查已有备份/pre/完整diff是否能精确恢复三个目标hash及函数边界；101已做失败的同一重建不重复。可恢复则逐方法登记未变依据；不可恢复或修复影响性质则并入一批最终版本定向PG。25个方法来自repository/recovery/integration，具体标识在101的database-http-method-runs.json；按本轮事务/来源/容量/恢复直接依赖选，不默认重跑29PG、六迁移或17旧Windows场景。仍有缺口须逐方法明列，不能降级Must为可不测。

允许产品修改：backend/app/activities/teaching_repository.py；backend/app/learning下teaching_contracts.py、teaching_policy.py、teaching_progress.py、teaching_views.py、teaching_service.py、teaching_api.py及teaching_adapter.py/evidence/prompt的本轮缺陷直接路径；frontend/src/activities下TeachingWorkspace.tsx、TeachingExercise.tsx、TeachingFeedback.tsx、teachingApi.ts、teachingDrafts.ts、teachingIntents.ts、teachingIntentMatch.ts和教学相关样式。ActivityWorkspace.tsx/LearningResult.tsx只允许G7显式seed传递/挂载及既有引用显示的必要薄接线，旧G7first、消费、重试/资格行为不变。README.md只更新必要教学使用节。允许新必要教学组件和定向测试，不建通用框架。

允许测试/验证修改：backend/tests下test_teaching_repository.py、test_teaching_recovery.py、test_teaching_policy.py、test_teaching_contracts.py、test_teaching_api.py、test_task100_integration.py、test_task100_control.py、test_task100_content.py及必要本轮教学定向新测试；backend/tests/fixtures/task100/；frontend/tests/task100-browser.cjs及同目录task100审计修复专用脚本；新合成样本只进backend/tests/data/task100/audit-repair-03/。runner可增加repair-combo选择性执行入口及修运行控制，不得弱化原身份/限额/截止/失败统计。上次最终runner含未运行改动，必须先离线核实际边界，不能凭旧PASS恢复许可。

禁止修改001—009迁移、持久模型/ACL、activities/repository.py旧写入主体、worker/launcher/SUP/Job/gateway/transport停止与退款权威、旧G7后端主体、materials/PDF主体、配置私件、依赖锁、正式DocuS、公共库、旧证据及归档。产品运行/构建/测试不得依赖公共库或DocuN临时实现。若本轮需要新列/迁移、角色扩大、语义放宽、付费或额外服务，完成不受阻部分后交具体差异，不自行实施。

精确资源仅复用以下已有合成对象，串行独占，不新增容器/卷/镜像/服务：

- 容器80ae914138fa42a9ae72acf898d13f7e740b759ff09fc248470abb6df0c15d4d，名retrolume-task-100-g8-pg1；镜像sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f；卷retrolume-task-100-g8-pg1-data挂/var/lib/postgresql/data；127.0.0.1:55442。1CPU/512MiB/pids128、restart=no、非privileged，无host bind/devices/cap-add。inspect完整JSON只抽必要字段、不输出Env；命名卷不是host bind，不复用旧错误模板投影。
- 现有库retrolume_task100_g8_main/fault，账号retrolume_task100_admin/app/denied。先核合成库/owner/009状态和最小权限，仅这些角色的凭据可经内存/STDIN重置，密码不进argv/报告/日志/DSN文件。业务真实调用用app最小权限，denied只负例，admin只精确准备；不得用admin成功代替业务权限验证。不创建别库/角色/故障schema，不重跑未变009迁移。
- 同源产品应用127.0.0.1:18100，既有venv、node与本地浏览器依赖。Windows受控模型/工具只回环和固定合成传输，真实launcher/SUP/worker/Job不被替换；没有外网、真实密钥/provider/付费。测试注入只在子进程测试环境，不进入产品配置。
- 保留容器/卷/库/原数据，零DELETE/DROP/TRUNCATE/删除资源/清历史。新测试使用唯一合成ID及保留式收尾，不假设库空，不重复读取真实配置。不安装/拉镜像/联网/Git stage或commit/push。源码、dist、相同端口/对象本轮无并行写入或测试；编排是唯一整合及共享账维护者。

新许可从本轮首次执行独立记账：主动21600秒、离线1800秒、真实业务3600秒、独立收尾480秒；真实合并入口4、精确容器start4、app start3、SUP尝试18、browser launch3、driver launch3、frontend build2。新增使用目前0，旧许可用满/未知仍并列。计数在动作前写账，入口BLOCKED/FAIL也计；SUP调用尝试含预扣后未Resume，不仅按实际进程数计。入口内多个有名子段不得混成额外隐匿入口；直接诊断连接/业务运行也须经过同一账与截止，不在runner外绕跑。

额度是上限，不是要求花完。默认一个主合并批，另三个仅实际有据修正后的受影响补验；不机械重跑全链。管理截止本轮固定、单调、覆盖子段与外层等待，剩余必须留收尾；卡内普通修复可继续到整卡完成。发现同根因已两次有依据修正仍失败、前提被推翻或任何对应额度触顶，停止受影响运行并交回，不暗开第五入口。

## 验证、证据与审计关系

先完成产品与夹具修正、与F/E及099映射的静态核对、适当离线行为检查和前端typecheck/build；这些针对确定缺陷，不复现旧失败来再次找已知根因。现有psycopg Windows Selector loop、认证token bootstrap、合成库非空、Unicode stdout及目录/role边界已知，实际脚本离线核准后才用真实入口。构建完成保存源码—bundle身份，后续产品变化须说明影响，确实影响dist才用第二次构建。

主批repair-combo或等价有界runner的精确执行计划在首启前保存，列实际方法/场景、最终模块与夹具hash、预期、资源/账守卫、依赖失败时后段not_run。顺序为精确身份与最小库预核→受影响PG/HTTP→有限实际Windows业务→最终dist浏览器→finally独立收尾；真实脚本上级设硬截止，不能只在某子测试里计时。原件保存stdout/stderr/退出码/耗时、断言及跳过，禁止只以聚合PASS或mock/SQL字符串证明事务。

必要检查矩阵如下，能同一例覆盖多性质就合并，不按条另起入口：

1. F01/F09离线真实函数与PG实际结果提交：正确有限答案、60/0.01m/s确定冲突、单位冲突、无法解析/歧义unknown、模型误报met不加独立数、不推进；规范上下界与12/13小数位容差，JSON浮点/超域字符串拒绝。保留概念/程序原文与逐维度理由，不执行用户代码。
2. F02真实PG单快照/暴露反例：旧S1形成题/反馈→S1替换或撤销→活动合法新范围S2/S1新版；workspace/record/history派生正文抑制，旧未暴露reference拒绝，答案/纠错仍可读，实际引用失效如实拒绝。每公开读取一条业务SQL，两个set_config不冒充业务查询，前后资格不得跨快照拼接。
3. F03真实HTTP严格边界：流式超限早拒、UTF-8合法/非法、UTF-16/32及嵌套重复键，认证不变，拒绝后行数/四账不变。内存有界性质用真实流读取观察及代码证明，不制造大流量压力批。
4. F04实际仓储和服务的accepted COMMIT后/claim前中断点，同键显式并发恢复至多一次CAS和真实SUP/外发；至少一次真实组合证明恢复入口可达。claimed/no-operation/UNKNOWN只读、GET不执行及既有取消/版本屏障按受影响方法复核。无需要求重跑原全部故障17窗。
5. F05路径32/33、同键重放真实PG；F06有效G7seed沿用、来源/hash/kind/活动/当前资格反例真实PG/HTTP，seed写入可恢复且不加观察，不重启first。G7合法seed可用本轮固定合成身份准备或已有准确成果，经旧受控链真实获取若确有必要计SUP，不能伪造G7权威。
6. F07/F08一个浏览器专项消费最终dist及真实或清楚标注的合成只读快照：显式seed入口→查看路径/已公开参考/反馈各自真实引用与位置→翻过20条历史及坏cursor→两标签同题A1/A2和未保存输入保护→同上下文R1/R2迟到选择→卸载/切换无旧回包污染。使用真实产品HTTP核引用/历史及source-invalid，UI时序可由有界网络延迟注入；注入不作为PG资格证明。已有轮询/草稿/UNKNOWN控制无影响者复用，不为旧reason字段FAIL专门再跑。
7. E02一次受影响内容与实际接线补验：路径三节点、计算/概念/程序各至少一个完整练习—作答—反馈和有必要的新实例，实际provider目录/输出/提交/引用回查可关联，correct_parts/errors/evidence_gaps所用引用逐条支持相应论点。程序不执行，概念不把来源未给的隔离级别推断成事实。数字/单位、概念性质/例子、程序严格条件/逐次状态/return位置分别留有限oracle；至少一反例能识别错引速度资料，不能由同一选片算法自证。无需重跑旧晚到/停止矩阵来证明内容有据。
8. E01按受影响方法清单收口最终版本缺证；原25方法如均实际依赖本次改动，可同批运行并逐方法说明，不回避应测性质以追求少测。旧4个后期PG和4HTTP仅在对象/依赖/样本确实未受影响时继承。报告具体剩余、实际not_run/skip，禁止再称无绑定的“最终全量绿”。

防止版本补证再次失效：每批启动前保存实际要加载的源码、测试、夹具、前端脚本和最终bundle完整字节到新证据as-run目录及SHA索引，不能只存post-hash或不可逆diff。尤其保存teaching_repository/service/views、policy/contracts/progress、合成内容与该批方法的完整文件。批后hash核零漂移，出现有据普通修正保留批时原件，再分类哪些结论可继承/哪些需要最终字节复验。loader实际模块路径与跨进程注入身份证据沿既有机制留档，不把后来最终源码绑定到之前运行。

证据分A实际运行、B代码/静态、C外部可靠资料、D推演，精确到实际对象/配置/样本与断言。模型内容oracle为本有限合成包，不是实际付费provider通用质量。009、未动G3/G4/D3/G5/G6/G7已有证据按依赖范围引用，不拓展其声明。

必需独立审计仍属TASK-101完整G8成果。修复稳定、原件齐备后由编排向原101审计窗口另发一次实际增量复核合同；此前该窗口不并行读正在改的文件、不修产品。本卡不追加审计或以自评关闭DEF，原101七规则/保护对象及已可采结论不机械重审。

## 停止与回传

按完整成果执行到成功或真实停止条件；不要只修两项代码P1就把其余批准合同遗留交给下一小卡。范围扩大、持久模型/权限/关键状态冲突、新高风险、关键材料缺失、同根因两次有据修正仍失败、预算到限时停止受影响部分，先保存已完成成果与最小缺口。不新增目标、额度或特殊人工审批来遮住正常中间步骤。

每批finally以精确已登记身份停止本卡应用/浏览器/自有Job并有界核树零、容器Running=false/Pid=0、18100/55442无监听；资源或引擎不可确认时如实记录未确认与安全下一步，不能一律写cleanup PASS。全部库/行/卷保留，不能以批量删除或DROP清理测试。未启动的依赖段not_run，有异常退出保留原日志；已充分且不受改动影响的证明不重复运行。

置顶结果必须先给一句真实结论、完成范围、产品/夹具差异与证据导航，再列TASK/R/STEP、实际身份、F01—F09/E02/E01逐项状态、原合同映射、全部pre/diff/post/as-run与原件路径、分级验证、失败及修正、复用适用性、未完成/未验证、偏差、新旧分列账、资源终态、风险、建议DocuS同步及最小下一步。正文较长可链接新evidence子文档，不把原件内容复制进多份报告。

保存结果后复核真实可读、实际文件/链接存在，再回复一句结论与D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-100-result.md可点击绝对路径，供用户带回编排。真正未保存才明确未保存；不填编排最终验收、不以修复完成宣告G8放行。

## 必要人工与待同步信息

必要人工仅转交本完整卡，完成后带回结果文件路径；不需要用户密钥、用户库操作或重复原G8-P批准。旧窗口必须读取本节及变动的根路径映射，旧四根目录已归档，不再重建或改写归档；历史路径按根AGENTS映射读取。

需主控后续同步DocuS架构/执行动态的实际教学变化、DEF状态、证据与预算、CHG，不由执行者改共享文档/选号。可报已根因确认且实证解决的夹具经验候选，不自行写公共规则或经验库。整卡完成后一次集中回传，编排据原件裁定并安排101增量复核。

## 以下为已结束的原卡、冻结通知和全部历史
# TASK-100 / R-094 已返回冻结通知（2026-10-05，当前）

续作02已真实回传并完成编排普通核证；候选与有限证据部分通过，集中独立审计待101。原三许可、追加许可及其额度终点保留在下方和原账，禁止再启动main-combo或借用名义剩余SUP。产品、009、夹具与旧原件冻结，独立审计只有其新卡指定写权。原完整合同原字节快照见 DocuN/evidence/TASK-100/orchestration-receipt-03/TASK-100-card-as-returned.md。

这不是G8、父STEP或项目放行。下方仍为原执行合同及全部历史。

# TASK-100 / R-094 续作02 — G8剩余合同修正与完整教学主链收口

本节为2026-10-04当前有效合同。沿用TASK-100/R-094、G8-P及原成果目标；下方续作01和初轮保留历史，它们的运行许可已经结束，不再启用。你是业务实现与验证执行者，不是独立审计者或编排者。本轮交付完整修复、缺失的验证链与原始证据，卡内连续完成后统一回传。

## 目标、正常终点与接收安排

一次完成目标与诊断→接受路径→计算/概念/程序推理练习→零费保存作答→有据反馈→续答与新实例复测→路径更新或保留理由→刷新/重开恢复。包括参考暴露、版本与历史、来源失效、UNKNOWN、取消、预算和本地停止。既有实现保留；不是再设计，也不是只修runner后跑当前四个子段。

交付批准范围内最终产品、009候选、实际可执行的PG/HTTP/Windows/浏览器夹具、限定合成证据及必要README；稳定后编排另卡集中独立审计。不自签G8、全部STEP009—012、真实provider质量、M-1、部署或项目通过。

项目根D:/shspic/project_NO3_RetroLume-agent，入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。task_model锁定V4.0/公共AGENTS CHG-0003。公共只读根D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4；公共DocuS/AGENTS.MD、WORK.MD第2/4/6/8/9、task_model/prompts/07_开发执行循环.md。七指纹按项目DocuN/evidence/v4-migration-20260930/rules-snapshot.json，编排本轮核未变，不自动升级。当前需求v1.1、架构v0.80、执行动态v2.02；原需求/架构关联编号沿下方原卡。

类型实现、普通修复、隔离合成定向验证，大小L；父099/R093，STEP009—012，关联DEF-003—007。接收A+增强执行，使用用户当前最强可用、能执行完整Windows/PG/浏览器链的**新业务实施窗口**。原因是初轮和续作01都未到达主链，续作01的“全部关闭”与当前函数事实不符，运行器还缺两类必需子段；需要从实际函数与原合同建立完整接续，而不是继承该自评。不是因为完成任务所用的模型品牌而重审。请如实登记客户端、型号和窗口，档位不冒充身份。禁止原审计窗口兼任；不自动派子Agent或开并行执行。

授权来源：用户2026-10-02批准G8-P，D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-099-work-decision.md；本轮是编排据返回证据组织的原边界续作，不重复申请同一批准包。允许实施、普通修复、合成验证及精确自有资源收尾；禁止用户库、真实资料外发、真实密钥/provider/付费、安装/下载、Git写入、发布、共享规则或停止/权限权威扩大。

## 断点事实与最小充分输入

按序读取：本节和下方原业务合同；项目入口/锁定公共规则；DocuS/执行动态文档.MD顶部；DocuN/results/TASK-100-work-decision.md本轮裁定；DocuN/results/TASK-099-result.md第3—8节和V01—V20/H1—H4；再按实际依赖读相关源码与测试。099唯一有效业务合同SHA256为0f38de84d6036e48a9fa544ba8304b37a72cf89e56e29fc05bef500609cc0e67。新窗口读齐必要合同；同窗未变材料可复用，不要求重读全部项目历史。

当前身份导航D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/orchestration-receipt-02/continuation-input.json，本轮普通核证DocuN/evidence/TASK-100/orchestration-receipt-02/receipt.json。索引是首改基线，不是通过证书。首改前核对象，发现不明增量查归属，保护他人改动。正式DocuS不作全篇冻结。

实际断点：续作01两次frontend-build日志存在，第二次含tsc/vite成功；没有最终前端源码—dist绑定清单。41项离线通过仅有报告声明，所回传目录没有该批原始unittest日志，不能凭声明签动态通过。四个main-combo入口中两个汇总exit0实际在roles-prepare BLOCKED，末入口migrate-main009阻断，后续仓储/恢复/故障/HTTP失败；当前Windows和浏览器子段根本未实现。子段原错误和旧PASS文字原样保留，核证单列纠正，不覆盖原件。

续作01账载入口4/4、容器start1/3、app1/3、SUP0/24、browser0/2、driver0/3、build2/2；离线14.880、真实17.910、收尾0.890秒。该许可已结束，名义未用数不借出。初轮至少9个真实入口、已计时仓储57.170秒而账载51.230漏5.940、至少1次容器启动而原账载0；其余初始化/诊断总量未知，继续保留，不因新窗口或新账清零。

前轮代码基线：teaching_repository.py cc8da07dca9174dd2546c3674cdf27556572dcba343dbc33afd3650fe14066fc；009_teaching.sql 9fb8a3a261a1d01a658478ba31bcdd79ef409823b7490f93cb8ee52f696b638c；runner.py a6a640e04ac827c6143f4ea6fcd9ca619884560e93d885e45fa7f73bdbaaba82；pg_migration_scenarios.py 80285f7a123058205c7d0c1a31a65b49f8a9d9c94c4116919189bd4296463d01。不得用旧初轮c250/924cec基线覆盖当前成果。

原始失败导航：DocuN/evidence/TASK-100/continuation-01/attempt-ledger-continuation.json及runtime/main-combo-20261003T063821Z.log、064217Z.log、064847Z.log、cleanup-20261003T065720Z.log、两份frontend-build日志。初轮有效策略与中间版迁移证据沿原裁定分层继承，不复制所有旧证据，不把旧版本11项迁移通过移植到当前009。

## 必须合并完成的修正，不能采纳“已全部关闭”

以下是编排对少量关键函数的普通核证，不是全面审计或完整缺陷清单。执行者须把这些与099逐项对账，落实同一批准合同；不扩大规格。

**DEF-003，不可变事实与权限。** 009现已恢复records全部UPDATE/DELETE拒绝，仓储已去掉分次回填，方向有效，但尚无最终真实本地命令写入证明。核每个本地/模型/工具分支在INSERT前算好最终applied_revision/state_after，并与head/command同事务；既有行全列不变。产品records只SELECT/INSERT；最小commands列级UPDATE与身份触发器一致，不能只查表级GRANT就声称无列级写权。保护反例按原合同验证，禁止DELETE清理、删库重建或抬高app权限来跑通。009已应用对象若与最终触发器/权限不同，只做本卡合成对象的必要向前修正并存数据不变证据；不修改001—008。

**DEF-004，当前身份及跨窗口主链仍未落实。** 当前teaching_repository.py的_locked_teaching_binding约738—766仅核command状态/摘要/context，没有锁内复核head/revision、真实goal与父题/答/纠错、当前pending及冻结引用。claim_teaching_launch约678在pending为NULL时仍可能放行；约686把pending且dispatch_closed也一概拒绝，但既有settle会将活动变为pending/dispatch_closed=true，合法下一次claim才重开门。按原launcher/仓储真实资格语义修新教学入口，不修改旧关门或停止实现，不简单删除安全条件。必须真实证明同活动连续两个以上教学模型窗口可达。

T-launch和admit/mark复核当前资格，已经改变目标/答案/父题或来源的候选在首个出站前拒绝；不能仅以Python冻结profile代替数据库屏障。result分支仍按099区分当前与合法历史，不能把历史结果全部拒绝当安全修复。_write_teaching_outcome约787缺command或operation不匹配时直接return，会留下原正文终态而缺教学事实；新教学链不完整须在同短事务拒绝/回滚，ALREADY_PRESENT先判受限完整性，合法迟到保留history，旧G3取消/来源失效纪律优先。核实实际目标/题目/rubric/答案/纠错/核算及source/body hashes组包，禁止全零ID、占位答案、空冻结引用冒充正常评价。

**DEF-005，真实SQL及读取。** 当前workspace的exposures CTE约1074对TEXT列body使用body->>'part'，与009定义不符；约1094对psycopg默认已解码的jsonb dict/list再次json.loads，亦不适配实际仓储行类型。必须修真实查询及返回类型，不能让手写假row的离线测试掩盖。逐个R01—R03做到一个SQL快照，合法007正文投影、来源资格、真实view_token、引用暴露、坏单项局部抑制；命令和历史端点仍有多次SELECT的路径也需按099对账。GET零写/零执行，未暴露参考不能从任意读面漏出。

**DEF-006，控制与夹具仍有结构性缺口。** pg_migration_scenarios.py当前约80—82调用re.search/re.sub但没有import re，key-value DSN路径会先NameError；同卡修并离线验证两种DSN。runner汇总只统计fail/timeout，漏blocked；迁移失败后还执行依赖测试制造大量无意义错误；main-combo的2400秒变量没有包住直接builtin调用，累计时限及完整finally未落实。两项HttpTests只检查未知活动404/坏DTO，不是HTTP教学主链。没有Windows/browser实际子段，现有main-combo不能靠重跑变成完整验证。与凭据/env/类名/loop_factory/会话token这些已定位修正一起一次补齐，下节给具体控制要求。

**DEF-007，失败收据恢复。** final_status替代旧command.status方向有效，但只属静态候选。证明确定未准入清本键pending、claimed但资格/operation不明仍UNKNOWN且保留槽、同键刷新不重发、提交响应丢失重读；取消或缺model_receipt不能单独提供“未准入”证明。复用真实停止/结算主体，不让SUP/API代退款。

## 执行边界、串行资源与新增限额

可修改下方原卡已经允许的教学领域模块、teaching API/配置/前端、009、必要新教学prefix薄hook/读取投影、直接相关测试/fixtures、README。允许在backend/tests/fixtures/task100/新增本轮合成Windows组合与控制测试，在frontend/tests/新增有限task100浏览器脚本；测试实现不得放DocuN供产品import。共享DocuS/编号/DEF状态/公共库仅由编排维护。只写自己的结果及DocuN/evidence/TASK-100/continuation-02/新证据。

禁止修改001—008、依赖锁、原G3/G4/D3/G5/G6/G7未变写入与停止主体；worker_main/command/one_tool/gate/launcher/session/supervisor_main/supervisor_ipc/windows_job不重写。原允许的one_call教学profile薄接线及仓储新prefix hook仍可修；若必须改上述禁止主体、增加表/持久列或推翻原资格/退款合同，停止相关部分并交具体差异。097旧bootstrap及依赖runner全部禁用。保护用户配置、旧证据、结果历史和不明来源改动。

精确容器ID 80ae914138fa42a9ae72acf898d13f7e740b759ff09fc248470abb6df0c15d4d，名retrolume-task-100-g8-pg1；唯一卷retrolume-task-100-g8-pg1-data；已在本机镜像sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f。仅127.0.0.1:55442 PG与18100同源应用。单CPU/512MiB/pids128/restart=no，无host bind/特权/新增网络/镜像pull。启动前完整inspect JSON核对象，不用历史误判的Go投影；不输出Env。

仅retrolume_task100_g8_main、retrolume_task100_g8_fault两库及retrolume_task100_admin/app/denied测试角色；现已存在声明需首用真实核owner和身份，保留数据与旧表。原实际_main与_s系列库只读不用，不创建第三库或新容器/卷。故障schema上限六个，沿pg_migration_scenarios.py SCHEMA_NAMES的task100_m01_nonempty、m02_duplicate、m03_missing、m04_tampered、m05_midway、m06_denied。已有schema查状态与可复用证据，不能仅“存在即SKIP”当通过；缺证且无法安全重验的项明确not_run，禁止无限换名。测试每例合成唯一业务ID并保留，查询按ID断言，不要求全库为空。

凭据只经stdin/环境/内存；精确测试角色密码可在确认归属后重置，不能重置其他角色或写argv/日志/证据文件。两库owner必须本卡admin，app/denied最小权限；测试super只初始化本卡对象，不运行产品。DSN必须专用且不回退用户配置；缺少口令/字段先在纯离线控制用例定界，不向用户索要真实凭据。无DROP DATABASE/表/schema、TRUNCATE、事实DELETE清理、容器/卷删除或旧证据覆盖。

编排2026-10-04只读核查时Docker Linux引擎管道不可连接，不能实时签容器已停；上一cleanup原件是Running=false/Pid=0。端口与task100执行进程未发现残留。**现在可以先离线修复；真实验证前须Docker Desktop引擎就绪。** 若仍不可连接，停止依赖运行，只交最少人工“打开Docker Desktop等引擎就绪”；不启动/重启共享系统服务、不重建资源。不会因为等待而宣称结果通过。

本轮新增许可：主动6小时，离线含build1800秒，真实业务3600秒，独立收尾480秒；真实合并入口最多3，精确容器start尝试3，app启动3，SUP创建函数进入尝试24，browser启动2/driver3，frontend-build最多1。初始新增使用0；旧至少9+续01的4入口及全部失败/漏时/未知单列保留，不追认超限，不跨许可借额。首入口为完整主批，另两个只用于有依据修正后的受影响项与尚未到达的子项，不计划跑满；完成即停。

新账DocuN/evidence/TASK-100/continuation-02/attempt-ledger.json明确本许可与旧账引用、每次尝试和实际counter/time。任何涉及真实PG连接/DDL、container update/start、app/SUP/browser的诊断或测试都必须在该有限runner入口内，入口前先持久计数；任何BLOCKED/失败/预检/timeout均占本次入口，不释放。纯读取引擎可达性/inspect且没有资源变更或业务连接的准备可不算真实入口，但计主动时间、留证，不借此夹带运行。cleanup及只读收尾不算新的业务入口，计独立收尾额且必须执行。

## 先完成可执行的完整控制，再集中运行

你自主在卡内分解并完成，不逐项请用户批准。先修上面确定合同差异和同源直接影响；再补缺失的真实组合与浏览器夹具、可靠runner。不要在缺子段或缺依赖时先耗真实入口。离线用例是针对已见故障的必要控制验证，不是扩建通用框架，也不是拿mock假装数据库正确。

一次有限离线批至少实际覆盖：两种DSN/保留password；每个真实测试类/方法可发现及loop_factory；token bootstrap/环境变量对实际API；已有资源/角色/数据库分支；missing/corrupt/负值/bool账不清零；限额检查在实际动作前；blocked/skip/not_run不能汇总PASS；依赖失败不执行下游；累计单调deadline和有界finally；观察/日志异常不吞收尾。控制替身可模拟外部进程异常，但必须标离线、保留raw，不能据此签PG/Job通过。

runner输出一个具体execution-plan.json，列实际存在的模块/类/方法/Windows场景函数/浏览器入口、依赖、预期证据、精确资源、预算与截止。不得用placeholder或待写脚本占位；新窗口要完成缺失实现，不照抄旧runner的四子段列表。计划完整、final product/fixture/hash就位、控制离线过后才可启动主入口，不另设需要用户逐项确认的门。

main-combo可以同一个入口串行完成migrate/最小权限及最终仓储→有效HTTP→真实Windows主链/异常→最终dist浏览器→收尾。按实际依赖执行，已有安全完整初始化可复用；迁移/健康关键失败时，相关下游not_run且总批非PASS，不继续运行必败测试。单入口墙钟单调截止最多1800秒，并受真实累计剩余额限制；给每个子进程取min(子段额度,批剩余,累计剩余)，直接builtin也受该deadline，不能只声明外层timeout。收尾始终有独立预算及finally，输出/观察失败不能跳过关闭。

每段完整stdout/stderr、退出码、as-run产品与夹具hash、开始/结束/elapsed、test计数与skip、业务事实保存独立原件；不要仅留末尾200/3000字导致全部setup错误无法重建。秘密从异常与输出中脱敏，保存完整非敏感错误；不为了抓错误直接重跑整套。报告PASS要求所有必需段达到判据，或该段有逐项绑定的有效旧证据；BLOCKED、缺阶段、skipped不能靠总进程exit0变PASS。

应用与真实worker均用项目既有runtime启动口径、固定合成配置与回环隔离，只替换provider返回/传输。测试代码不得替代产品账本/admit/mark/record/launch/Job/停止链；注入点显式白名单，仅测试进程环境可达。真实产品运行不得依赖公共库、DocuN临时实现或097旧注入器。只管理本卡创建且身份证实的进程树和句柄；不知道归属的进程不taskkill。

## 本轮最小完整验证矩阵与证据复用

按099 V01—V20/H1—H4给最终有限映射，V19真实provider保持not_run。原20项未受影响的纯合同/策略证据可复用；旧D3/G3/G5/G6/G7主体不重跑。旧009、中间仓储、仅编译的修复不能升级成当前真实通过。两次build仅能证明当时构建成功；核最终源码到bundle的绑定，只有当前前端变化或绑定无法成立才用本轮一次真实build，保存served dist hash和浏览器读取对象。不要为省build伪造绑定。

**PG与009：** 用最终仓储和最小app权限真实走通本地O01/03/05/06/09/11，以及真实教学模型/工具record同事务路径。证明全列不可变、权限与实际INSERT一致、第二版目标UUID清空、失败零半写/回滚、同键与语义槽竞争、两重当前绑定、原正文/教学fact/exposure/progress/head/command原子；ALREADY_PRESENT与响应丢失、历史迟到、UNKNOWN及failed/pending。有效活动workspace/command/history/record实际返回、一个SQL计数与快照、来源失效、暴露抑制、坏单项局部失败。不能用未知活动404来替代已存在教学读取。009只补最终差异、当前结构/权限及必要迁移反例，能按旧字节证据继承的前置不重建，不将SKIP说成通过。

**HTTP：** 真实本地会话/同源权限，GET一个合法教学workspace及实际正文；目标/路径/题/零费答/评价分离、同键重试/异文409、来源/版本拒绝、未暴露参考及敏感标识不泄漏、坏单项与分页。每个新核心动作核PG事实与费用/请求副作用；不是仅两项基础路由测试。既有plain/G7/model/tool回归按真实hook/配置影响选择。

**Windows：** 实际launcher/SUP/worker/命名Job/PG组合，原卡17窗有限矩阵优先一次串行共享前置：8模型主链、1G5有限核算、目标/答案/来源/取消四种晚到、UNKNOWN/无效输出/合法显式retry、一次硬停止。可用同一次真实事件覆盖多个同等判据，但逐项解释，不删关键异常。真实核组包内容与引用hash、首个出站数据库屏障、最终持久内容/四账/时间账、树零/关门/退款权限；连续两次成功教学窗口必测，防settle后dispatch_closed使后续永不可达。拒绝候选预扣与无发送如实记，所有SUP函数进入尝试都计上限24。

**浏览器：** 一个真实最终bundle会话优先消费同批持久主链。看见实际路径、三种题型、保存答案后刷新恢复、反馈/理由/合法参考暴露、续答/复测/历史纠错；HTTP与PG值交叉，GET不自动POST、IDB写失败0POST、同键核对、UNKNOWN/失效/取消/低预算、隐藏暂停/卸载/迟到、键盘/禁用文案、多字节和XSS按原合同合并。显示异常允许有限路由替身，但报告分清显示替身与真实HTTP/持久主链，不能全路由伪造整链。新增脚本先离线自检身份/选择器/计数窗口，不能带旧明确夹具错误再烧入口。

证据D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/continuation-02/按真实批ID新建。至少含读入/前置/差异、pre/diff/post、as-run/as-loaded/最终hash、各段完整原件、业务映射/失败与有据修正、attempt账、资源归属/权限及保留式收尾。原件只存一次，索引引用；不存在的运行/抓取/历史字节绝不补造。

## 停止、最终回传与必要人工

卡内普通错误留原件、定位、有依据修复，在剩余新额度内只复验受影响和未测项，继续到完整成果。相同根因两次有据修正仍失败不因换文件/名称清零；根因不稳、泄露、无法确认本卡树收尾、上限到达或需要推翻合同时停相关运行，完成不受阻部分后一次交回。禁止额外直接unittest/PG/browser诊断绕runner或暗开第四入口。

所有入口都保留finally：关本卡Job私有句柄、终止确认自有树与应用、释放18100、停精确容器并inspect Running=false/Pid=0，库/卷/数据/角色保留。未确认就写unconfirmed，不把主进程退出等同整个树已停止；不得代worker结算/退款。最后冻结实际最终产品与所有夹具，并说明证据针对哪个字节，旧FAIL/UNKNOWN不改写。

结果仍D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-100-result.md，在最顶追加“续作02”，原初轮/续作01逐字节保留。先一句实际完成/未完成，再列合同项与DEF候选修正、真实文件/版本作用、最终批证据与复用理由、完整旧/新账及偏差、资源收尾、not_run/风险、待同步DocuS、必要人工。不要只用compile/build宣称DEF全关闭，亦不填编排验收。

完整稳定成果后由编排另发一次隔离集中审计（下一101/R095仍只留计划，本卡不占号/自派审计）。共享状态、CHG/DEF与最终验收由编排串行维护。确认结果真实保存且可读，回复一句事实结论及上述结果绝对路径，供用户带回；不得每个子段索要转卡。

唯一当前必要人工是Docker引擎若仍不可连接，用户打开Docker Desktop并等待就绪；不需要真实密钥、用户库或删除许可。离线修正及完整夹具准备可先完成。无需重复批准G8-P或普通测试修复。

## 以下为续作01及初轮完整合同历史（运行许可已结束）

# TASK-100 / R-094 续作01 G8合同修复与完整剩余受控验证

本节为2026-10-03当前合同，覆盖下面原卡中已结束的运行许可和旧基线；原卡业务目标、099完整规格和禁止边界继续有效。原卡原字节见D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/orchestration-receipt-01/TASK-100-original-card.md。不得把下方旧6入口/32SUP额度再叠加启用。

## 目标与完整交付

你继续担任本卡业务实现执行者，不承担编排裁定或独立审计。一次完成已批准G8教学闭环的合同缺陷修复、有限控制器与夹具修正、全部剩余必要合成验证、范围内普通修复及保留式收尾。先完成下列已定位修正和原合同直接相关对账，再集中运行；不要只跑最后UUID用例、再交一张仍缺主链的报告，也不要把每个修正拆成多次回传。

用户可观察终点仍为目标修正/诊断→接受有依据路径→计算/概念/程序推理练习→零费保存答案→反馈→续答/复测→更新或保留理由→刷新/重开恢复。参考暴露、当前与历史版本、来源失效、未知和取消、持久预算及限定停止真实成立。模型/工具/监督权威与旧业务保持，不代替真实provider质量或完整项目。

交付修复后的项目内产品/009候选、相关测试与完整as-run证据、必要README操作说明；置顶保存原结果D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-100-result.md，初轮全文保留。正常完成即停止并交编排，后续一次隔离集中审计；本卡不自签G8、STEP009—012、M-1或发布。

## 项目 规则 授权与接收

项目根D:/shspic/project_NO3_RetroLume-agent，入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。模式task_model，锁定V4.0/公共AGENTS CHG-0003。公共库D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4只读，公共DocuS/AGENTS.MD、WORK.MD第2/4/6/8/9及task_model/prompts/07_开发执行循环.md同窗同版已读复用，缺失再补；七项指纹按项目DocuN/evidence/v4-migration-20260930/rules-snapshot.json，2026-10-03核一致，不自动升级。

当前需求v1.1、架构v0.79、执行动态v2.01。TASK100/R094沿用，续作01，父099/R093，STEP009—012，原关联需求/架构编号不变；实现/验证/普通修复，大小L。接收A+增强执行，继续刚返回TASK100的真实业务实现窗口，原因是合同/源码/失败连续；不是独立审计窗口，不自动派子Agent。请补登真实客户端/模型和窗口身份，不假称某个旧型号；确实无法可靠承接才由用户转给同等胜任新窗口，仍沿原TASK/账/失败，不自行换号。

授权依据为用户2026-10-02批准G8-P及其D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-099-work-decision.md，完整同边界续作由编排据真实返回核证分配。不重新问同一个批准包。普通实现/修复/合成验证已授权；本节新增投入仅用于原目标及控制修复，禁止用户库、真实资料/密钥/外网/模型付费、依赖安装、Git写入、发布或停止/权限权威扩大。

## 断点和最小充分输入

先读本节、D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-100-work-decision.md和项目执行动态顶部，再按问题读相关源码。唯一业务规格仍为D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-099-result.md，第3—8节全文和V01—V20/H1—H4，SHA256 0f38de84d6036e48a9fa544ba8304b37a72cf89e56e29fc05bef500609cc0e67；同窗已读正文复用，只补本轮偏离的具体段，不另写新设计合同。

当前对象身份索引D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/orchestration-receipt-01/continuation-input.json，必要当前文件及七项规则。它是导航/基线，不是当前产品已通过结论。首改前核相关hash；漂移须查实际归属，保留他人改动，不覆盖不明增量。正式共享DocuS会由编排更新，不要求其全文旧hash冻结。

初轮结果hash df26be0d…9ecd；当前teaching_repository c250401c…be94，009 924cec98…3c33；runner当前58907d27…cc11，已与原final-file-identity中的600d47ef值不同。旧清单/日志原样保留，不能补写旧as-run为当前值。

复用实际20项离线合同/策略通过及其字节绑定。迁移11项绑定旧009 9b5db84c，最后仓储8OK/1ERROR绑定旧教学仓储2ea63987；只有不受本轮改动影响的子结论可继承。当前不变G3/G4/D3/G5/G6/G7审计/运行结论直接引用，不重跑全旧链。旧097 bootstrap及依赖runner禁用；098已核控制模式仅参考，不从证据目录import实现。

旧运行许可结束。旧ledger报6入口，但有8仓储入口及另一次迁移，至少9，初始化/诊断/直接运行还未完整重建；仓储计时合计57.170而旧账51.230漏5.940，容器至少start1而旧账0。旧超限/失败/未知不清零。所谓沙箱失败不计entry和全分层由编排暂停，当前没有可核实依据，不能据此释放额度；前条编排暂停只针对违规命令/删除。补账给原始出处，用户决定如有独立有效原文可披露，不能虚构或覆盖原账。

## 合并修复清单与完成标准

一，DEF-003，恢复批准的不可变事实和最小权限。099第4节明确records禁止UPDATE/DELETE，applied_revision/state_after也属于不可变效果事实。当前009允许它们任意UPDATE、仓储依靠多处回填、pg_setup授records UPDATE/DELETE均需修。先在同一原事务计算最终效果/唯一state_after、分配批次事实，再INSERT最终记录并更新head/command；保持一事务、失败全回滚、一版本至多一个state_after，历史不生效仍成对NULL。新事实FK插入顺序可自主实现，不新增表或新语义。不把“服务器维护”当作擅自可变例外，不通过弱化触发器/测试制造绿。

二，DEF-004，落实真实教学上下文和数据库屏障。_stored_document现仅目标版本和目录，evaluate只是answer_pending，reference_hashes空、profile.goal_record_id全零；必须按099回查并装配真实目标/路径/节点/题与rubric/答案/纠错/有限前史/核算事实，填写真实引用和hash，消息摘要由实际provider投影计算。完整OneCallInput序列化/配置兼容在接受/claim前检查，防仅因组包错误消耗持久launch；接收后再锁内核全部冻结实体/来源hash与版本。T-launch、原admit/mark的新教学分支必须核head/revision/goal/题/答/纠错/pending/obsolete/abandoned及上下文；工具recipe同样核真实arguments/name/call_id。adapter复核不能替代两个DB屏障。

T-result继续原record同事务原子保存规范正文/received/教学事实/exposure/至多一个progress/head/command。缺失或损坏command/fact不能静默按received成功；旧终态重试保持ALREADY_PRESENT优先，并核G8链完整，不追补旧损坏。当前/合法历史/原G3旧代次或取消拒绝的分支按099区别，不用SUCCEEDED推定推进。未露参考不经通用GET泄露，迟到可读反馈仍配历史exposure。

三，DEF-005，完成一致且可实际查看的只读面。当前workspace四条SELECT，默认隔离不构成一个快照；source_invalid硬编码false、view_token的na占位、model fact没有007正文投影均需修。按099第7节每端点一条SQL取权威/所需有限正文及暴露/源资格，再应用纯投影。真实返回路径、题干、合法hint/reference、反馈、更新理由，不只返回ID或暴露布尔值。失效抑制派生正文但保留用户文字历史，坏单项局部拒绝不拖垮列表；view_token含真实有关状态。GET绝不写exposure、启动或发送，分页/上界/跨活动/敏感拒绝真实成立。

四，DEF-007，失败/UNKNOWN恢复。finish_teaching_supervision不能在UPDATE后按旧command.status清pending；以确认后的结局执行正确指针处理。取消且无model_receipt不是未准入证明；claim已持久且无operation按unknown/read_only处理，不能重开同一launch。已明确未准入、未知、committed、history、abandoned、显式合法新retry按099状态机对账，保存答案不依赖评价成功。

五，DEF-006，控制器、夹具和资源修正。按下一节先建立完整有限runner；pg_setup和pg_migration_scenarios中DROP DATABASE WITH FORCE/PUBLIC临时放权/过宽应用授权必须取消，保留原失败和数据。frontend-build不能继续映射策略unittest，HTTP/recovery/Windows/browser测试不存在的先准备实际文件。临时原件当前放TEMP的事实登记；后续正式夹具使用项目内本卡data根，只复制已存在且可核字节，不删除/搬走旧Temp原件，不依赖外部临时文件提供产品业务能力。

除这五个已定位归属，按099对本卡尚未验证的命令、投影和前端调用作一次范围内普通对账，完成原卡目标。不要把本列表当缩减验收矩阵，也不要重审整仓或更换旧监督实现。修正前保存必要pre/hash和实际diff，未变同窗材料复用。

## 修改权与串行整合

沿原100允许的产品、009、相关正式测试和前端目录；本轮修复归上述教学模块/新前缀hook/教学投影/配置/UI及task100有限夹具。具体文件以当前索引和原卡允许清单为准，必要新HTTP/recovery/Windows/browser测试与保留式runner helper可在原正式测试目录创建。README只写真实可用操作/限制。正式产品不import DocuN/evidence或公共库的执行实现。

001—008、用户原始需求、正式DocuS/公共源/旧证据/旧结果、依赖锁、Git、deploy只读。worker one_call仅可为原已批准的新profile检查薄适配；worker_main、command、one_tool、gate、launcher、session、supervisor_main、supervisor_ipc、windows_job主体不改。需要改变停止/结算/恢复权威或新增主要模型/公开接口时停相关部分，给具体差异，不自行扩大。

本轮产品/测试/端口/合成数据独占，单执行窗口串行，无并行测试或其他写者。执行者自己完成整合，编排仅维护共享状态；不要求用户逐条执行命令。

## 精确资源与数据保留

只复用当前已停容器ID 80ae914138fa42a9ae72acf898d13f7e740b759ff09fc248470abb6df0c15d4d，名称retrolume-task-100-g8-pg1，镜像sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f，唯一retrolume-task-100-g8-pg1-data命名卷至/var/lib/postgresql/data，PG 127.0.0.1:55442，应用127.0.0.1:18100；restart=no、非特权、无host bind/devices/cap_add，不新增资源/镜像下载/外露端口。

编排receipt实时核Running=false/Pid=0/exit0，两个端口空且无task100进程，但Memory=0/NanoCpus=0/PidsLimit=null。你首用重新核精确身份，唯一runner中先在停止态对此ID落实memory512MiB/cpus1/pids128，完整inspect投影确认后才计start并启动。身份或限制不符且无法在本卡范围修复时停止该资源运行，不换替代容器。

保留原实际retrolume_task100_main和retrolume_task100_s_各库、全部旧schema/行只读，不改旧009、不删库重建。续作只写原卡已批准固定两库retrolume_task100_g8_main、retrolume_task100_g8_fault；首次连接先核库身份/owner/已有结构，存在有效成果则保留复用。不存在时限该精确容器内创建这两个，不扩其他数据库。main用于最终001—009完整实现与合成业务；fault用于迁移反例，最多六个显式本轮schema，创建前冻结名称与search_path，防回退public串读；每例保留，不按失败清空。

角色限该100测试集群已有retrolume_task100_admin/app/denied；必要初始化沿现有retrolume_task100_super或该精确集群管理连接，仅用于两库/schema归属与最小权限，不能传应用或当产品身份。新表按099只授SELECT/INSERT及head/commands指定列UPDATE，records无UPDATE/DELETE、PUBLIC无访问，旧表权限不扩大。口令安全生成/仅内存及stdin/子进程env注入，禁止argv/证据/聊天/文件存明文DSN或口令。

本卡没有删除授权。禁止DROP DATABASE、TRUNCATE、DELETE教学或其他历史事实、批量表/schema删除、容器卷删除和历史文件删除；旧脚本存在该代码就不得运行。迁移反例在受限新schema/回滚事务验证，001—008原文不改，009真实提交/拒绝及事务行为仍须测，不能靠字符串断言冒充。需要破坏性重建才能继续时先保留其他部分，交回具体原因，不自动清库。

## 新增预算与唯一受控入口

新增许可主动6小时；离线含typecheck/build累计1800秒；真实业务累计3600秒，收尾独立480秒。真实入口最多4、精确容器start尝试3、应用启动3、SUP创建函数进入尝试24、实际browser2、driver3、前端build2。所有上限同时成立，当前新增使用0；旧原限/至少9入口及未知、至少start1、原失败和旧主动时间未知分别保留，不把新预算加到旧账后倒称原来合规。

默认第一次主要合并入口连续做PG/HTTP/Windows/浏览器，资源只start一次；剩余仅给有依据修正/失败影响或实际未测项。不是计划跑满4批或24窗；全过即停。每个主批业务最多1800秒、收尾最多180秒且受总额，正常主链达到即可结束。单个子命令/网络/查询均有有限timeout，不能把串行子超时叠成无限。

真实启动唯一入口D:/shspic/project_NO3_RetroLume-agent/backend/tests/fixtures/task100/runner.py，由本机现有backend/.venv/Scripts/python.exe -B调用，冻结有限permit/阶段选择与预算。不要再用直接unittest/诊断脚本/docker start/应用命令在runner外消耗真实资源。准备期只做离线静态、控制器单测、typecheck及必要真实build；inspect-only等不接触真实服务的自查应明确离线模式，不混在实际验证入口中免计账。

runner进入实际验证模式就在任何Docker/PG/身份预检之前追加持久entry，blocked也消耗入口，拒绝损坏/缺失预算账。先保存start-at/permit/目标与as-run文件hash再运行；新增账只追加，旧attempt-ledger.json只读，生成带出处的校正和新permit账。timeout发生时标started_failed/timeout及实际已启动子段，未开始子段才not_run；不释放额度，不用“环境问题”改写尝试事实。

分别在实际start/应用/driver/browser/SUP函数进入前扣次数，CreateProcess/Resume/claim/Job另观测，不混称一类。累计业务/离线/cleanup秒数按真实单调时间，预检/诊断阶段也记；清理预留独立，业务熔断不阻断finally。准确记录每个失败根因/修正次数，同一根因此前已达两次失败不得无新方法证据继续。

执行前离线验证控制器关键差异：计账先于失败前检、损坏账拒绝、累积超时熔断、启动失败也计数、子段fail/not_run区分、资源白名单拒绝、异常不阻断自有树收尾、真正build命令。所有创建后立即进入partial保护；观察身份/日志异常不能跳过terminate/close。被测产品原停止逻辑不替换、不用旧097注入器。输出用不可覆盖批ID；凭据不出日志，任何外部网络禁止，transport替代点仅provider。

## 本轮必要验证和证据

按099 V01—V20建立有限映射，V19真实provider仍not_run。现有已可继承证据逐项绑定最终差异；被本轮修正影响的用例按真实最终字节定向补测，没有影响不重跑旧D3/G3/G5/G6/G7。修复/实现稳定后集中运行，不每次编辑就启动真实PG。

PG优先最终仓储终验，并覆盖本轮新增真实风险。至少证明本地O01/03/05/06/09/11可以在不可变records与最小权限下原子提交，所有列UPDATE/DELETE反例拒绝、失败无半写；目标第二版UUID清空；单语句workspace/正文/源失效/暴露投影与分页坏单项；T-intent/launch/admit/mark/result的当前绑定及竞争；received/body/fact/exposure/progress同事务与提交响应丢失；failed/pending及UNKNOWN恢复。迁移只补009实际增量和当前最终结构/触发器/权限/关键回滚，不机械重建六个旧数据库。若旧迁移证据不足以继承则在fault隔离schema定向补，保留所有数据。

HTTP沿实际路由/共享会话，零费保存/评价分离、严格DTO/权限/同键异文、来源/当前版本、坏单项与参考不泄露；新旧plain/G7/model/tool不受新前缀影响的核心回归按具体改动选择。不能用服务mock替代原仓储事务证明。批时fixture身份和产品身份同时保存。

真实Windows参考原卡17窗矩阵，复用共享已成功前置，不重跑每条完整链。8次模型主链、1次G5有限核算、目标/答案/来源/取消四种晚到、UNKNOWN/无效输出/合法显式retry、一次实际硬停。每窗通过真实launcher/SUP/worker/Job/PG，transport只替外部返回；目标是证明上下文装配/数据库屏障/持久效果/账/停止，不能替fake ledger。允许合并证明相同事件但必须说明覆盖理由，不能漏核心异常。上限24包含全部创建尝试，拒绝候选不为测试强行多开SUP。

前端真实npm run build，保存源码/配置/build输出/served dist的hash链；frontend-build入口禁止策略unittest占位。一个浏览器会话优先消费同次真实持久主链，验证三题型/正文、保存后刷新恢复、反馈/理由/参考暴露、续答/复测/历史/纠错、键盘及禁用说明。GET不自动POST、IDB写失败0POST、同键核对、未知/失效/取消/低预算、隐藏/卸载/切换迟到及多字节/XSS反例按原合同合并；部分显示异常可用有限路由替身但分清真实HTTP/旧持久事实/显示替身，不把全部合成路由当整链。

实际原件在D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/continuation-01/，批ID不可覆盖。包含校正账和新permit账、pre/diff/post、startup/as-run/post哈希、实际worker加载/SessionOutcome/正文hash/账、HTTP与浏览器时间线/截图、schema归属/权限/回滚事实、最终资源收尾。单条证据只存一份、报告引用路径，不重新复制全部旧证据。

不能只凭被测最终文件清单倒推旧批跑了新版；修改后只对未受影响结论复用，变化行为最小目标复验或not_run。修复records合同后，旧允许投影UPDATE的测试OK不继承为不可变保护。构建/离线不冒充真实PG、Windows、provider质量。正常完成需实际主链、核心异常及预算/原件可复核，不把文件存在当完成。

## 停止 审计与回传

范围内首次失败保存原件、定界、有据修正；在本节剩余额度只复验受影响项并继续未测项，不因为一次普通夹具问题永久冻结整个成果。两次有依据修正仍失败、根因不稳、实际安全/泄露/无法确认树收尾、核心合同要推翻、越界或任一投入上限到达即停受影响运行，完成其他获准且不受阻部分再统一交回。不能把旧失败换名归类为新问题清零重试。

结束时无论通过/失败，终止且确认本卡自有树和监听释放、停精确容器并inspect Running=false/Pid=0，Job句柄关闭及残留不确认如实写；保留库/卷/原件，不对用户进程或不明归属进程taskkill。停止资源也经过runner有界finally，不让输出/观察异常吞掉收尾。

完整成果稳定后编排才出101/R095新隔离集中审计，关注三表/权限与实际写入、当前资格/原子事实、读取/暴露、受控组合/界面和执行账；不每个修复补独立卡，不由你自审。不自动创建新审计或实施窗口。

原结果置顶续作01，初轮原文和失败保留。先一句实际结论，再写逐项完成/未完成、真实差异/身份/作用、原件导航、继承理由、全部失败及校正账/新增用量/剩余、资源归属与收尾、未验证风险、待编排同步和必要人工。报告不得继续把G8实现全完归因文件数量，不把预算超限追认为授权内，也不声称所有not_run都是编排撤销目标。

确认保存且可读，回复只给一句结论与D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-100-result.md可点击绝对路径供用户带回。通常必要用户动作只有转交本卡；不需要真实密钥、删除许可或用户库操作。共享状态/DEF/CHG由编排维护，执行者只给事实建议。

## 以下为2026-10-02原完整卡 保留历史

# TASK-100 / R-094 G8完整教学持久闭环实施与限定合成验证

## 目标与交付

你是本卡业务实现执行者。用户已明确批准G8-P，按完整成果连续实现、定向验证和普通修复，不承担编排裁定或独立审计。不要重新给设计方案、逐项请求转卡或把本卡拆成后端/前端/测试几个回传。

唯一成果为用户在现有活动工作区完成目标修正与诊断→接受有依据的路径→获取计算/概念/程序推理代表练习→零费保存作答→收到有据反馈→针对续答/新实例复测→看到路径更新或保留理由→刷新/重开继续。参考暴露、重复提交、旧版迟到、UNKNOWN、取消、费用/时间及恢复边界真实成立。

交付为项目内候选产品和009迁移、相关真实及离线证据、必要用户README，以及完整结果D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-100-result.md。原始运行证据只写D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/，相同原件只留一份，以索引引用。产品和正式测试不得import临时证据实现。

本卡正常终点是批准的G8产品实现、卡内合成验证及普通修复完成、最终字节和原始证据冻结、资源已收尾，交回等待一次完整成果集中独立审计。不签G8最终、真实provider教学质量、全部STEP009—012、M-1或整个项目通过。

## 项目 规则 身份 路由 授权

根目录D:/shspic/project_NO3_RetroLume-agent；入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。task_model锁定V4.0、公共AGENTS CHG-0003；公共只读根D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，必需DocuS/AGENTS.MD、WORK.MD第2节task_model及4/6/8/9、task_model/prompts/07_开发执行循环.md。同窗同版已读复用，版本指纹以项目DocuN/evidence/v4-migration-20260930/rules-snapshot.json为准，不自动采用后来版，不切模式。正式DocuS、共享状态和公共库只读。

任务类型为实现、迁移准备与隔离合成验证、前端接线、普通修复；大小L。父TASK099/R093，承接限定验收G7（097/098）及G3/G4/D3/G5/G6；关联STEP009—012，DR002/NFR005有限版本/恢复，FR002/004/006/007/008/010/012，NFR001—005、DR001—003、SEC001/002，MOD001/003/005/006/007/008，FLOW002/003/004/005，API002/003/005/006、DATA004/005/006/007。旧夹具DEF001/002是禁用边界，非本卡产品缺陷修复范围。

接收A+增强执行，优先继续TASK099实际业务设计窗口。该窗口报告系统Codex/GPT-6、精确变体和原097同窗身份未核实；按你当前真实身份登记，不冒用旧标签。不是098独立审计窗口。确因窗口不可用/上下文容量无法可靠承接时，可由用户交同等胜任新业务窗口，沿本卡恢复，不清零预算。禁止自动派子Agent。复杂度来自多表原子性、幂等版本恢复、受控模型/工具和UI完整链，需一次集中完成。

用户2026-10-02在编排展示具体G8-P范围和裁定后明确“批准”，生效记录D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-099-work-decision.md置顶。批准三张教学表、009迁移、新profile/HTTP、原record同事务教学效果、独立至2048显式教学配置与有限核算界面，授权本卡具体隔离合成实现/验证/普通修复。无需再询问这些已批准细节。基线需求v1.1、架构v0.78、执行v2.00，产品相对099读入无漂移。

不包含真实provider/外网/付费、用户库迁移、真实资料/密钥、部署、Git写入、新依赖、任意用户代码执行或停止/权限权威扩大。下一阶段费用/真实质量许可不能从本卡推导。本卡不修改原始需求、Must、旧主要模型或旧额度。

## 唯一合同与最小上下文

下列文件是本卡组成部分，必须能够访问。完整规格不在此复制第二套。

1. D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-099-result.md全文，SHA256 0f38de84d6036e48a9fa544ba8304b37a72cf89e56e29fc05bef500609cc0e67。第3—8节为业务/数据/DTO/事务/API/UI完整合同，S1—S3/K01—K16/H1—H4为合成内容和推演，V01—V20为验收映射。V19真实provider部分明确不运行。
2. D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-099-work-decision.md当前批准记录及裁定。此前“待决定”段是历史，不能拿它阻塞已批准实施。
3. D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/input-snapshot.json，SHA256 717089d55394371faf00b10c7f065c3818c0fcf60318a0af602bb16091b513c1，56必要输入身份。它不是全仓清单，也不是要求全文件再读。核产品/合同身份，正式状态后续更新与产品漂移区分。已有其他改动先辨来源，不覆盖或还原。
4. 本项目DocuS/最终需求文档.MD相关FR/Must及数据安全，架构动态文档.MD当前G8采用和相关FLOW，执行动态文档.MD顶部及相关STEP。已读同版仅补变化，不重读几十万字历史。
5. DocuN/evidence/TASK-099/teaching-flow.md、model-output-examples.json、document-check.md及read-manifest.json按需复用；占位citation不是实际已存在源，未来合成夹具须绑定真实冻结资料。
6. DocuN/results/TASK-097-final-acceptance.md及TASK-098-result.md的范围/控制缺陷/有效证据，不重采691输入或557旧原件。097完整旧bootstrap及依赖runner禁用。098的probe_bootstrap.py及controlled_entry.py位于DocuN/evidence/TASK-098/，只作已验证控制边界参考；正式新夹具必须落backend/tests/fixtures/task100，不能从证据目录import。
7. 直接相关现有源码和测试按099 F01—F13定位：learning、activities事务/读/服务、capabilities契约/gateway/工具、worker typed输入、service_config、001—008、前端意图及工作区。旧监督/资料/PDF无影响主体复用，不全面研究旧仓。

任一必要合同不可读，仅暂停其依赖部分并带具体缺口交回，不声称已加载。基线漂移若为已知合法共享文档更新可记录继续；产品存在未归属修改先隔离，禁止两人并行写测试对象。本卡执行期产品目标、构建生成物和资源独占，原099设计已返回；无其他已派发冲突卡。

## 完整实施内容及成功条件

A 领域与持久原子链。

按099实现teaching_heads/commands/records三表和009_teaching.sql。不可变goal/题/答/反馈/暴露/纠错与可重建head分开；007仍唯一存模型/工具正文，operation kind仍model/tool。完整字段/索引/同活动FK、command身份与launch不可重置保护、records不可无痕改删、有限容量及权限必须实际落地，不只复制SQL中表名。

009在一笔事务核001—008实际结构/必要列和约束域、无G8冲突残迹；非空升级只新增，零回填旧G7、旧received无正文不补正文。重复009、缺前置、被篡改的必需约束、权限不足及中途失败须有明确失败/全回滚事实，不能只比较名字。001—008只在新合成库空时顺序初始化，先完成008再放旧行样本；004空活动限制不能被跳过。故障前后旧行逐字段/hash留证。

O01—O11全部可执行，X01仍旧cancel，R01—R03只读。零费保存用户文字不调用模型或claim、不修改G/R/S，活动取消/到期边界照合同；合法历史留稿只绑定旧题事实，不能推进当前路径。T-intent冻结内容与父槽，T-launch持久CAS一次启动；无operation但已claimed不能视为安全重发。admit/mark锁内再次校验当前教学身份，网络/工具在事务外。

record_outcome和record_tool_outcome在原短事务内原子提交规范正文/终态、教学fact/exposure/必要progress、command和head；不在service收到成功后另开事务写进度。原_terminal_confirmation等值无写幂等优先级不变，旧终态不能补正文或补教学事实。只教学版本过时且原G3资格仍合法时可历史提交；源/取消/G/门不合法时仍拒正文，仅原UNKNOWN诊断。正常反馈多事实只一次head效果，任何一项写失败整笔回滚。

固定来源排序→活动→相关operation排序→head→command排序→新records锁序。同键同文重放、异文拒绝，同父跨键唯一槽及无重复计数，答案继承不分叉。工具仅原finite_calculate，一动作一tool，模型动作一model；禁止eval/exec用户程序。重新规划/纠错/复测的有限推进、争议与暴露资格必须由应用裁决，模型不能回受信状态/权限字段。

B 严格接线与恢复读取。

实现teaching.v1受信profile、严格输出联合、封闭HTTP命令与一条SQL快照；所有尺寸、身份、hash及序列化域按099，禁止循环hash和重复正文无界膨胀。旧learning.v1仍1..256，teaching独立配置1..2048且默认关闭，旧活动不自动提高输出/工具余额。one_call/SUP/007字节上限、协议3/4、固定WorkerCommand、SessionConfig与停止/退款权威保持。

教学习题参考未经持久exposure不可被workspace、历史单项或旧operation通用GET泄露；反馈可读前与其暴露记录一起提交。纯GET不写暴露、不恢复claim、不发送。源失效抑制派生正文但用户文字可辨历史；当前head不能引用失效观察推进。单条坏记录局部抑制，数据库不可读显示unconfirmed，不能猜成功。旧plain/G7调用和通用继续拒教学前缀绕阶段，旧合法行为保持。

实现新本地能力层/有限工具配置和可解释缺配拒绝；不读用户activity.local.json或真实环境secret。README只教配置/显式调用/停止/恢复及限制，示例占位不能激活付费服务。

C 工作区与教学质量表达。

按teaching-flow及完整合同挂载目标、诊断、路径接受、题、参考、作答草稿/保存、四类反馈、续答/复测、更新理由、历史/纠错。普通界面不暴露SQL、执行凭证、DSN或测试控制细节；按钮有可解释禁用、键盘焦点/状态文本。

完整待发正文先入有限原生IndexedDB、摘要台账再入localStorage、成功后才POST。失败保留输入且零POST；刷新/跨页只GET，同键核对摘要/实体，迟到保护覆盖活动/目标/路径/题/答。区分草稿、已保存、正在评价、未知、已提交；不能把显示放弃当取消/释放UNKNOWN。单workspace轮询不重叠、hidden暂停、卸载清理、120秒/40次自动观察上限；不让用户等待占worker。旧G6/G7台账兼容，不能覆盖旧数据。

S1/S2/S3手工oracle写成有限真实合成材料，保留原件hash/引用身份及逐维度期望。数值/单位/数量级、概念否定/等价、程序手推逻辑、部分正确、证据不足/归因假设均可区分；程序题只阅读，不执行给定代码。模型意见不能替代确定算术/证据冲突，未知保留。两不同未暴露实例且含复测才形成有限前进，同题辅助/重复/争议不重复加观察；不输出长期mastered。

D 合成验证、普通修复、交付。

按下节V01—V20分层完成，相关修改完成后集中验证；普通有据修复可在本卡继续，无需每个小修交回。保存每次失败，最终证据与实际运行字节绑定，复用仍适用的通过项，只补新影响/未覆盖项。不能在最后修产品只跑构建就宣称原业务日志覆盖修后字节。达到成果即停，不为了用完预算重跑。

## 可写文件与禁止边界

相对根目录的产品允许范围如下，必要改动保持目的可追踪。

- backend/app/learning新增teaching_contracts.py、teaching_policy.py、teaching_service.py、teaching_adapter.py、teaching_prompt.py、teaching_evidence.py、teaching_api.py；必要包导出。现有service.py/api.py/evidence.py仅教学父/前缀兼容拒绝和公共引用薄复用，不重构G7。
- backend/app/activities/repository.py新增教学方法及新前缀admit/mark/record锁内分支、只读投影；必要内部教学helper可单独放同目录teaching_repository.py，仍使用调用方同一connection，不增加通用框架或另事务。service.py仅教学前缀阻断及必要薄调用，api.py仅能力面和未暴露参考防泄露投影。
- backend/app/capabilities/contracts.py、gateway.py及tool_execution.py的受信绑定/新profile处理与精确拒绝；原tools.py算法和有限执行域只读。
- backend/app/service_config.py、main.py教学路由/专用大小守卫与配置挂载；local_session和materials/pdf认证行为不变，不扩大allow_own_origin。
- backend/app/worker/one_call.py仅typed新profile/新前缀输入检查兼容；worker_main、command、one_tool、gate、launcher、session、supervisor_main、supervisor_ipc、windows_job保持不改。需要改变这些执行/停止主体时先停相关修改并带具体冲突，不能用新profile名悄悄重写监督。
- backend/migrations/009_teaching.sql新增；001—008禁止改写。合成初始化/角色/故障脚本写下述测试夹具，不把测试专库/角色硬编码进生产迁移。
- frontend/src/activities新增TeachingWorkspace.tsx、TeachingExercise.tsx、TeachingFeedback.tsx、teachingApi.ts、teachingIntents.ts、teachingDrafts.ts、teachingIntentMatch.ts及必要同功能小模块；ActivityWorkspace.tsx只挂载与上下文协调，activity-workspace.css必要样式。现有LearningResult/旧台账等只在新教学直接兼容需要时薄改并明确测试影响，禁止无关美化。
- config/activity.example.json、根README.md说明新功能/显式配置/限制，.gitignore仅必要阻止本卡私有运行输入入库，不忽略测试/证据以隐藏失败。
- backend/tests中新增test_teaching_contracts.py、test_teaching_policy.py、test_teaching_repository.py、test_teaching_api.py、test_teaching_recovery.py及完整成果确需的同前缀测试；旧相关activity/learning/gateway/config测试只做真实新契约/直接影响适配，记录差异，不修无关旧失败。新夹具backend/tests/fixtures/task100/、frontend/tests/task100-teaching.mjs及必要同前缀辅助；固定runner入口见资源节。
- frontend/dist允许现有本地build正常生成，绑定实际源码/锁/配置与被服务bundle；backend/.venv、frontend/node_modules及本机浏览器二进制仅复用，禁止安装/升级/修改依赖锁。

除此只写DocuN/results/TASK-100-result.md和DocuN/evidence/TASK-100/新增自己的材料，input-snapshot.json只读。保留原结果/旧证据及用户改动，不能覆盖、移动或删旧文件。公共库、正式DocuS、原始/最终需求、其他任务卡/结果、旧资源、Git索引/提交/分支/远程、部署文件只读。不建立另一个总进度账。

## 精确隔离资源与操作许可

以下是本卡明确合成操作许可，不涉及用户数据库。首用必须重新核归属、精确配置和端口；本卡不允许占用或终止其他进程。全卡串行，同一时点一个真实入口、一个应用、一个业务链，PG并发屏障用同一入口控制的有限连接；不要与其他窗口同时构建/测被改产品。

唯一镜像为本机已存在的sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f。编排2026-10-02 22:53只读核镜像可用，新名未存在，指定端口无监听；不是执行时保证。禁止pull/build镜像、联网安装、创建替代容器或换旧历史容器。

允许创建且只创建一个容器retrolume-task-100-g8-pg1和一个命名卷retrolume-task-100-g8-pg1-data，标签明确项目与TASK100。卷只挂/var/lib/postgresql/data，禁止host bind；1CPU、512MiB、pids128、restart=no、非privileged、非host网络，不额外cap/add或设备。PG只发布127.0.0.1:55442到5432。用已有默认bridge，不创建新网络。不得--rm或删除容器/卷；本卡末必须停止核Running=false/Pid=0并保留数据/证据。创建前若同名对象存在却非本卡账内ID，不碰它、不覆盖或“清理后重建”，停资源部分交回。

容器初始化管理员retrolume_task100_admin，仅在新集群；主库retrolume_task100_g8_main，故障/升级对照库retrolume_task100_g8_fault。仅两库业务对象获本卡写权；系统postgres库仅初始化CREATE DATABASE/ROLE所必需操作，不放业务或探测其他旧库。新应用角色retrolume_task100_app无SUPERUSER/CREATEDB/CREATEROLE及业务DDL能力；可建一个拒绝探针角色retrolume_task100_denied，故意不足以跑009。管理员只做新合成初始化/迁移/明确故障布置，HTTP/worker用应用角色。授予旧权威表本来所需DML及新表最小权限，不把DB超级权限放到应用。这里的新合成角色不是变更产品授权体系。

主库空时用原001—008顺序初始化，再插固定旧model/tool/UNKNOWN/received无正文/G7合成样本，记录基线，然后009非空升级与业务。fault库按固定顺序验证缺前置→001—008及旧样本→必需约束篡改/权限拒绝/中途故障回滚→必要精确还原。重复009在已升级主库确认自身拒绝/旧行不变。允许只在fault库对本卡明确创建的合成约束/ACL作定向故障设置和还原；原文件不改，禁止DROP DATABASE、TRUNCATE/批量删表、删除原件或重建库伪造回滚。无需每场景新库，隔离不清楚就停止该场景，不能串成脏数据仍称通过。

新应用仅127.0.0.1:18100，同源服务实际构建dist和API；不用5173开发服务/热更新冒充最终bundle，不再开通用代理或额外外露端口。transport替身可在本卡测试进程/固定子进程启动环境注入，必须沿原launcher/SUP/worker/Job/真实仓储，替代点只限外部provider传输/返回或明确故障观察。允许临时测试配置、合成session token和身份；不使用真实配置。所有材料为M1—M3及项目已有可核合成PDF，上传与产物只在DocuN/evidence/TASK-100/data相应本卡目录，不读用户资料。

测试新DSN只由RETROLUME_TEACHING_TEST_DATABASE_URL等本卡专用环境值注入；缺失明确skip/blocked，不能fallback用户DSN。真实入口若关键方法skip不能当通过。密码随机、仅内存/stdin/子进程环境，Docker创建使用继承环境变量名传递而不把值放argv；不打印完整Env/DSN/连接串，不写明文密码文件/报告。保留本卡容器内原有随机凭据，若换窗无安全恢复通道不读用户secret或重置旧角色，交回仅缺口。

只读docker完整inspect JSON可在内存解析，证据投影白名单ID/image/mount/ports/resource/security/state；不得打印含Env原件，禁止复用曾失败的HostConfig.Mounts Go模板。创建后记录精确CID、镜像ID、卷、端口、角色/库归属，随后每次接触按CID核不混同名。跨进程清理只用本卡持有句柄或PID加创建时间；禁止按python/node/docker进程名大范围taskkill。Windows后台Start-Process如使用必须Hidden。资源冲突不任意换端口/库/新容器以绕预算。

外网/真实provider/下载/真实费用均0。运行主进程、worker及浏览器建立早期回环网络限制；DNS和transport不得出站。替身不改变权限判定、canonical绑定、admit/mark/record/锁/停止/Job/结算，不能mock ledger冒充真实PG。观察日志失败不得阻断原terminate/close；创建成功后的identity、发布等任何失败必须携partial移交原收尾。097旧bootstrap/依赖runner禁止import或启动，采用098核过的边界在正式测试目录做必要新夹具。

## 固定预算 尝试账与停止门

本卡新增主动实施/阅读/普通修复上限12小时；离线定向检查和构建累计2400秒；真实业务累计5400秒；资源收尾独立累计720秒。正常完成即止，绝不以“消耗完额度”为目标。本卡新使用0；099设计上界6568/10800秒、其文档失败1次及097/098全部失败/用量/许可结束原样继承，不借余额，不按换窗清零。

新增最多真实入口6次、容器启动尝试4次、应用启动6次、SUP创建函数进入尝试32次、实际浏览器启动3次、driver启动4次、前端build3次。首次主链参考099估计17业务窗口；余量只给有据修正/直接影响，不是预定32次或6整轮。相对099建议增加的固定余量由编排本卡分配，用于减少普通修复重新转卡；功能/安全边界没有扩大。首次构建和最多两次有实际产品修正依据的重建计入3次，typecheck计离线秒数。所有上限同时满足，先到先停受影响验证。

唯一真实入口为D:/shspic/project_NO3_RetroLume-agent/backend/tests/fixtures/task100/runner.py，执行用现有backend/.venv/Scripts/python.exe -B。执行者先实现并离线检查这个有限runner，冻结CLI/permit、选择场景、资源和timeout清单再第一次真实运行。每次实际调用进入runner无论预检是否成功均计entry一次；同一次受控入口内可连续PG/API/Windows/浏览器子段，但不能以内部重启runner绕entry。没有容器启动则start记0，不把entry伪称0。

docker create次数最多1、命名卷创建最多1；start尝试在命令前计数，创建/start分开。SUP函数进入、CreateProcess调用尝试、实际CreateProcess成功、Resume、claim、Job绑定分别记录，32限制作用最早SUP创建函数进入；失败前没有成功就记阶段未达，不能含糊合并。browser/driver同理。离线纯fake进程不算真实SUP；任何实际Windows子进程控制探针计相应真实上限。

每次entry先持久写不可覆盖batch账、输入hash、选择场景及本批最大业务/清理秒数；累计剩余由本卡原件计算，单入口业务不超过剩余且不超过5400秒、清理上限120秒独立预留，所有批清理合计720。推荐第一入口只分足够实际场景的时间，不为早期失败空耗满额。总业务5400依据最多32管理窗乘120秒为3840秒，PG/API/UI和初始化余量1560秒；这是上限，不承诺每HTTP在120秒内结束。固定原监督deadline不延后。

业务计从入口业务预检开始至测试动作结束，涵盖真实资源/应用准备，不能把DB初始化/API轮询藏到离线；清理单列。主动记录至少开始/结束和明确等待，未记时部分保守记录，不编造精确活动时间。低风险离线读/hash/语法/控制检查可在准备期做，但真实PG、浏览器或子进程探针不得藏入“离线自检”。

运行前一次最小控制准备覆盖创建后身份/发布失败携partial、观察异常仍调用原close/terminate、角色和inspect投影、不可变日志、选择用例计数、外网早拒。不要预先搭通用平台或机械重复旧失败。成功证据保存后无需更放心重测。

一个普通产品/测试问题首次失败后，保存原件、定界、有据修正，可在本卡剩余额度内只复验失败/受影响项并继续未测项。没有“一次任何失败整卡永久冻结”的额外门。相同根因两次有依据修正仍失败、根因不稳、核心合同需推翻、新越权/泄露/无法确认自有树收尾、资源身份不符或总额到限时，停止相关运行并保存事实交回；先做不依赖该阻塞且仍在总投入内的部分，不暗开替代资源/第七入口。

达到预算要正常退出与精确收尾，不让测试继续。收尾超时只允许对已识别自有句柄/精确CID执行一次必要停止并如实登记超额/未确认，禁止无限轮询、范围扩大或借清理时间测业务。任务结束保留所有库/卷/合成数据，记录容器Running=false/Pid=0、应用/本卡树退出及端口释放、业务Job关闭/不存在可核证事实；不能只写finally已执行。

## 分层验证与证据采用

以099 V01—V20为完整映射，下面是本卡运行层授权与合并安排。详细对应由执行者保存acceptance-map.json，逐项标PASS/FAIL/not_run/reused及具体原件/最终字节，不要求每条单独开批或容器。

一，离线与内容。Strict DTO/图与状态/semantic_slot/暴露和独立观察/规范序列化/调用权限/所有大小边界；S1—S3和K01—K16给定资料/手算/逐行推理内容oracle；有限工具算法未改复用，程序题绝不执行用户代码。新支持性检查只能证明其确定判断，不把模板答案通过当开放题总体质量。配置缺层/模板不可启用、新旧profile混用和前缀越权必须失败关闭。前端原生IDB/迟到保护/无自动POST关键行为以真实浏览器补，不只断言源码字符串。

二，真实PG/HTTP。完成009空结构与非空旧行升级、重复/缺前置/篡改域/权限不足/中途异常全回滚，正文/received/教学事实和效果同事务，失败注入无半写；旧plain/G7/model/tool/无正文行兼容，应用最小权限和不可变保护。并发同键/同槽/答案继承链/唯一launch，COMMIT响应丢失、已claimed无操作未知，目标/答案在途版本变化和源失效。单语句快照/坏单项/分页/返回无参考泄露，真实调用计数和表事实证明，不能SQL字符串/mock代替。基线与副本方案提前固定，不把每例seed污染当空库假设。

三，真实Windows组合。沿实际用户/API或服务入口、原launcher/SUP/worker/Job/真实PG及受控传输，覆盖H1正常八次模型的完整持久链、一次有限G5核算、目标/答案/来源/取消四种晚到边界、UNKNOWN/无效输出/合法显式retry及一次实际硬停止。共享前置可按有效版本绑定复用，不重复整条链造场景；预算参考17窗。行为证明包括实际PID+创建时间、原始SessionOutcome/回执/hash、send/admit/账和树零/Job关闭，外部请求只是合成替身，不宣称真实provider语义。两候选竞争应在新意图/launch锁内拒第二候选，证据需显示真实双方及一次创建/发送，不为此强行多开SUP。

四，真实浏览器。一个有界会话优先覆盖目标/路径接受/三题型呈现、保存/评价分离、参考暴露、正确部分与争议、续答/复测/更新理由、历史/纠错、刷新重开、双页重复/同键核对、IDB写失败0POST、未知/取消/低预算、隐藏/卸载/切换与迟到保护。有限路由注入可以测显示/恢复，但至少正常主链走真实HTTP和持久读取，不能全拦截API假装PG整合。可把同一次真实业务链的输出供浏览器验证，不额外重发8次模型；每场景写实际底层是PG、路由替身或既有持久事实。最终served dist哈希与构建源码绑定，截图/请求时间线含核心可读状态，XSS/多字节/转义等受影响反例合并。

五，兼容与复用。实际改admit/mark/record/gateway/config及通用operation读取，选旧直接受影响语义做必要回归，不能只因旧测试文件未改排除影响；也不默认全仓/全部D3/G5/G6/G7重跑。原同事务/终态/关门/资料来源/协议证明未受影响处直接引用，若新分支影响旧行为才补对应方法。旧097bootstrap禁用，不为了重放旧成功把它重新启用。物理删除、向量、完整记忆/HTML/部署等不在本卡测试扩围。

六，证据冻结。改动前各目标保存pre或可独立重建diff及SHA256，失败用不可覆盖batch目录。每批记录被执行产品和测试/夹具的实际hash，关键worker新profile加载hash与源身份绑定；UI记录实际served bundle。最终post/diff、每条采用证据as-run版本与最终的差异及复用理由逐项列明。中间版本只对未受影响部分有效；修改后以最小有意义目标复验，没复验如实not_run，不能只借“最终所有hash一样”倒推旧测试已跑新版。

七，审计及真实质量。V19的手工oracle本卡交付；真实provider12请求建议不授权，真实密钥/费用0。稳定完整G8之后由编排另卡给真正隔离A+窗口作代码/证据/控制集中独立审计，输入原合同/最终diff/代码/原件，不给本实现聊天和自评。本卡自查不是独立审计，不逐个普通小修出审计卡，不提前占TASK101。必要独立审计未完成仅阻G8最终放行，不把当前候选交付说失败。

## 停止 回传 必要人工

完成全部授权可完成目标或触及真实停止条件，即精确收尾并保存结果。不为了等用户继续占进程，不扩建通用框架，不因为可用额度多而增加新功能或付费验证。

完整结果D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-100-result.md先给一句话结论与候选边界，再给A—D交付/真实文件差异、O01—O11与V01—V20映射、每批原命令/退出/耗时/尝试、旧证据继承依据、资源账和收尾、失败根因与有据修正、未验证/风险/偏差、需DocuS同步的逐项建议。建议状态由编排裁定，不写最终验收。

至少交付pre/post文件身份与统一diff、acceptance-map、attempt-ledger、每批配置非敏感投影/as-run/hash/原输出、内容oracle核查、迁移及旧行回滚记录、最终served bundle身份、资源最后事实。可以合并合理JSON索引，不为凑格式建空报告。旧失败原样保留，不移走错误日志或以新的PASS覆盖。

共享TASK/R/CHG、架构/执行账及经验库由编排维护；README是允许的用户文档。已解决且可复用的根因只报告经验候选，不占公共ERR编号。无需要用户提供的密钥或数据库操作，用户只人工转卡并回传结果路径。真正环境/授权缺口先具体记录，不擅自安装或读取用户配置。

确认完整结果真实保存且可读后，只回一句话结论和该文件可点击绝对路径，供用户带回编排。未完成同边界续作保留TASK100/R094和历史、原窗口优先，不能自行新增编号或重置已用预算。
