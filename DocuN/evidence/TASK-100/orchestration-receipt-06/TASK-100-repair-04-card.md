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
