# TASK-101 / R-095 review-03 — F01有限答案修复的独立增量收口

本节为2026-10-06当前有效合同，沿用TASK-101/R-095、父TASK-100/R-094、批准合同TASK-099/R-093、G8及STEP-009—012。只恢复本节只读审计许可；review-01/02及所有100运行许可仍结束。

## 目标与交付

你是本卡独立审计者，不接管实现或编排。唯一成果是裁定100定向修复04是否关闭F01/DEF-008/P1：核有限肯定语法、反例及正常兼容、进度传播、最终字节离线证据与本轮执行控制，给出批准G8有限切片是否还存在阻断的建议。

不从零重审G8，不重复F02—F09/E02/E01或旧PG/Windows/UI矩阵。卡内必要核对一次完成、统一回传，不按解析/测试/计量分别补审。

交付置顶续写 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-101-result.md，标review-03；原70370字节完整历史保留，原SHA b75f00d8a9a1e3c564d221dc70ca591cb0fa0a23ddf276a691cd1d323ba1dbb2。自有新证据只写 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-101/review-03/。交付代码/证据/执行控制三轴和综合结论、准确事实定位、有限继承及尚未验证范围，不填写编排最终验收。

完成标准为：三份实际源码/测试差异及直接调用已核；两条确定单值反例与两个有效实例不能误入独立观察，已验正常有限形式仍成立；18方法/81子测试/64样本的实际来源、断言及最终字节适用性有据；本轮许可/停止与历史账保留。够用即停，零新增业务验证。

## 项目、规则与接收安排

根目录 D:/shspic/project_NO3_RetroLume-agent，入口 D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。模式task_model，公共规则锁定V4.0/AGENTS CHG-0003，需求v1.1、架构v0.86、唯一执行动态v2.08、公共阶段07。

公共AGENTS：D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4/DocuS/AGENTS.MD；WORK为同公共根DocuS/WORK.MD，第4/6/8/9章适用本卡组织/回收/接续/核证。07为同根task_model/prompts/07_开发执行循环.md；合同结构依task_model/TASK_TEMPLATE.md。七项锁定指纹见 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/v4-migration-20260930/rules-snapshot.json。同窗已读且未变的正文直接复用，只补当前合同和必要变化；不采用新版/其他模式。

类型为剩余P1的集中只读增量终审，关联F01/DEF-008、V04/V06/V20及H1。授权终点为本轮独立结论和自有证据，不扩大实施或运行权。用户原始需求在 D:/shspic/project_NO3_RetroLume-agent/DocuS/原始需求文档.MD，只读，本次不要求重读整份。

接收Agent为原TASK-101 review-02独立审计窗口，执行档A+增强执行。该窗口前次实际客户端Codex desktop、系统标识GPT-6，具体部署型号未独立核实；如实登记，不因品牌重审。原窗口未参与100实现，已有独立基线有效；不能转到100实现窗口，不读其聊天/推理/实现记忆，不派子Agent。原独立窗口确不可续才说明原因并用新隔离A+窗口，沿用同TASK/R及证据，不清零历史。

独立输入为 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-101/review-03-input.json，SHA f5febafa84ace45f2a77783873a641ea414ec165ee7d55224f570bfd5d15959f。索引列133当前源码/测试/dist、7规则、3合同及163本轮原始证据；只提供导航/身份，不把编排或作者评价当证据。

关键冻结SHA-256：

- backend/app/learning/teaching_policy.py：efb2ec6a7e4452e0cbfe8365e2d58bea7a8793abe37892f082827dc829bbd303。
- backend/tests/test_task100_repair.py：9ee63357fbf935c0ea1cdeddac781179f6a11cc3f635ac3f6a165e2fdbb5f53f。
- backend/tests/test_task100_answer_support.py：47bae86e3a8afd13b3943fe9e9e94ca02970c9a20dcca2346bea53181d3783c8。
- 未改teaching_progress.py：edb9d4ac91711d8be82443b3ba8a38f114bfb3df885faedc1ea8c2aa0fb68bb6。
- 未改activities/teaching_repository.py：7d9e28575780e4ac3665f3197b022ff1a3a5c27fc49877067de8f55aef4fe127。
- 未改test_teaching_policy.py：a7bc7670e1bad6da45a50edb79210273fe134d2a71e55d0aef8f37d862d139d0。
- 未改009：11b1c2bc8cb2482a4fa509b897c3afb8f3f5f7be3eb4e8e4aab559706944c1a3。

100修复04已真实返回，普通回收部分通过，F01仍待本卡独立判断，不能继承“已修”自评为关闭。其新账测试1/3批、离线1.6463436/600秒、最终主动保守上界1779.265/3600秒，资源0；报告1776.750为封装前检查点，差2.515在最终原账中追加，不改历史报告。本轮许可已结束，剩余批不借出。

101旧review-02主动6778.853/10800、已登记辅助3.725/600秒及前读/未登记开销未知，首轮3038.528身份核后范围及未知、100旧初轮/续01/02/修复03所有原失败和预算继续保留，不能换轮清零。

本卡新许可 TASK-101-F01-review-03-20261006，主动3600秒、纯读/hash/AST/JSON配对元数据300秒，新增使用0，调度待转交；没有实际接收/开始事实。主动时间从本轮首读固定并涵盖封装回传，无法逐段计量者标未知/保守，不把未测开销写0。所有业务、资源、产品执行与新增显示probe额度均0。

## 背景与最小充分上下文

原F01根因是全文搜索数值后按参考量纲筛唯一候选；“平均速度不等于1m/s”“答案未知，可能1m/s”可被当matched。若模型全met，两个无曝光、不同实例且含retest的答案可进入independent_answers。review-02已给确定B级源码缺陷，未运行反例，不声称真实provider已经误判。

原“不读实际答案”已修，60/0.01的真实冲突屏障及正确推进有限事实有效。本次实际差异为policy局部解析、两个指定离线方法及一个新增纯离线测试；其余policy函数、support主体、进度和仓储调用未改。有限语法的目的为可靠识别，其他开放表达留unknown，不要求任意自然语言评分器。

按顺序最小读取：

- 入口、锁定公共AGENTS、本卡；唯一状态顶部仅定位调度。无法避免看到编排评价时披露，不能将其作证明。
- 中性索引中的TASK-099-result第5.2节和相关完成/独立性条款；修复04完整原合同快照 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/orchestration-receipt-07/TASK-100-repair-04-card-as-returned.md，只读当前修复04有效前缀。原审计基线为同目录TASK-101-review-02-report-as-frozen.md和你已有review-02独立源码/结论，不必重读全部历史。
- D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-101/review-02/F01-static-finding.md；当前policy及其pre/diff、新测试全文、test_task100_repair的两方法与diff。按需读未改rebuild_progress及仓储支持检查/投影提交调用点。
- 先保存源码初判，包括实际接受/拒绝形式、极端但真实可达输入与正反例辨别力，再读取本轮运行原件。不能先沿作者语法解释认定正确。
- D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/answer-support-repair-04/batch-01/ 的execution、python-identity、unittest真实观察器、stderr/stdout、unittest-result、as-run/after及完整被测副本；session-accounting、pre-targets/changes/diff/post和最终身份。163项是可读原件目录成员，依据具体断言选择，不能只读汇总PASS。
- 初判完成后才按需读grammar-and-applicability.md、propagation-source.md、method-applicability.json，视为待核主张和文字导航，不用作者说明替代源码/原件。case-results.json须与真实stdout独立核对，不自动信导出。

禁止读取TASK-100-result.md、result-prefix.md/template、pre/post中的TASK100结果、该结果diff、实施聊天/推理或客户端实现记忆。中性索引已排除这五份作者结果原件及当前实施报告。普通编排回收评价不可用于本轮证明。

同窗未变材料复用。必要合同不可读时用本卡完整缺陷/边界摘录和同版本既有原件；关键缺口仍不能补齐才停止相关判断，不假称读取。

## 执行边界与资源

只读上述源码、测试、精确证据、必要直接依赖与规则。仅可写自己的review-03证据和TASK-101-result新增前缀；产品、测试/夹具、迁移、dist、其他结果、旧审计/实现证据、DocuS/任务卡/共享账/公共库/归档全部禁止修改。

允许纯标准库文件读/hash、AST结构与原字节差异、JSON和日志配对，自有元数据辅助程序也受300秒预算。不能导入或执行产品/测试/作者脚本，不run compile/unittest/PG/HTTP/Windows/Job/Docker/inspect/应用/browser/driver/build/模型工具/网络/Git，不读真实配置，不安装依赖或改时钟。

本卡范围对象冻结、无并行写入。前置是100最终返回和字节稳定；编排已普通核133被测对象、168本轮证据身份和完整diff，不能代替你的断言核查。作者final-identities的旧共享state/task/work-decision是当时接收上下文，已由编排正常更新；核当时身份可用orchestration-receipt-07/before副本，不能把当前共享前缀变化误报产品漂移。源码冻结用本卡中性133项及七规则。

原容器、卷、库与停止观察保持历史时点，本卡不启资源，也不声明新检查。原100和101未用预算不复活。元数据核证已完成的132/2618/2933大基线直接继承，不重复全量旧证据采集。

可自主决定有限静态抽查及证据配对方法，不能自行补产品反例运行或修复。若发现确定新阻断，带真实可达触发/影响/最小修正完成本范围一次审查后交回；不能将未知开放表达、非阻断观察或长期provider质量升级为额外本卡硬门槛。范围漂移、关键前提推翻或未稳对象须停止受影响判断。

## 验证、证据与审计关系

本轮只核剩余P1的完整修复，不重复审查已关闭F02—F09/E02/E01。逐项裁定：

- 实际全文解析是否覆盖有限肯定形式，单值否定/不确定、引用/问句/假设、多值或开放尾部须unknown；不是关键词黑名单、首末量值或任意尾段放行。新辅助等式与固定短语是否守住这条边界，非法/非有限/参考未知单位和程序路径如何传播，按真实可达输入分析，不虚构可达类型或要求开放语义评分。
- 两个确定反例须reference matched、answer/status unchecked，不伪造conflict。真实rebuild_progress将对应数值意见收紧为unknown，不能因为模型四维全met误增独立观察。测试使用合法不同实例、不同答案ID、initial/retest及无曝光，不能靠坏结构或重复实例天然阻断。
- 正常1m/s、单位空白/60m/min、约0.5及合同指定有限说明仍成立；60m/s、0.01m/s、1m和参考自身冲突保持分离。一个正确加未知最多一个独立观察，两个明确正确不同实例含retest仍evidence_sufficient。不检查返回值没有的advance/opinion字段。
- 源码实际只有三个文件改变，两个原离线方法的增强不弱化旧断言，其他9个policy函数与26个测试函数保护、test_teaching_policy/进度/仓储/009/前端及dist保持。原仓储写路径继续调用同一个support/progress，局部语法变化是否引入确定回归按调用分析，不因函数未变自动排除传导。
- 18方法和81子测试回调须用真实执行观察器、stderr方法名及结果/退出0配对；64样本导出与stdout实际值一致、有效实例事实与断言有辨别力。as-run133完整副本、after和当前最终版一致；未执行的开放旧文字只能B级推导，不能假称新的PG/Windows动态通过。
- 旧开放文字改为unknown是否属于已批准可靠解析不足边界；其存储/并发/CAS/账本/停止等未变事实可继承，其旧数值解析结果不能强行继承。保留原FAIL和未知，不要求为旧总FAIL改PASS再跑。
- 动作前计数、55秒子截止/整批≤60秒、1/3测试批、1.6463436秒与最终主动1779.265上界、180秒和15秒保守开销、封装检查点差2.515及元数据检索错误的原账是否准确。预算资源0与许可结束事实有据，不把已登记计量称精确全部开销。

原review-02三轴充分结论、内容/方法/UI/原资源执行控制按有限范围直接继承。你本轮结论应区分A级真实本地函数结果、B级源码传播、未验证PG/HTTP/Windows及真实provider；旧高风险事务/资格/停止/退款主体未改则不新增真实验证门。

综合结论限代码通过/有条件通过/不通过/证据不足，并明确F01是否关闭和有无新的确定阻断。若F01关闭且无回归，说明已批准G8有限切片是否具备交编排关闭条件，不签全STEP/V19真实质量/M-1/部署/项目。只有真实缺陷或证据缺口才给最小补项；不为少量语法改动再安排全面审计或新PG/浏览器。

## 停止与回传

在同卡连续完成源码初判、原件配对和三轴裁定，普通读取不逐次回传。达到上述覆盖即停；预算触顶、关键合同缺失、冻结漂移、真实数据破坏/越权或根因不稳定时，保存事实并交回。不能换工具/模型/窗口清零，不自行追加业务运行。

新结果置顶review-03，保留原70370字节全文。先一句结论、范围/独立性与最终快照，随后按上述标准给触发/定位/严重度/依据、原日志方法与样本映射、证据继承和限制、真实读取/元数据命令/计量与失败、差异/风险/建议。不修改原review-02“P1未关闭”原文，当前判定在新增段更新。

所有自有证据在指定review-03新目录，不能覆盖旧原件；记录源码初判先于作者说明的顺序及偶然接触。纯元数据结论不冒充新产品运行。完整保存后核原报告尾段SHA/长度与链接可读，再回复仅一句结论和完整绝对结果路径，供用户带回编排。

## 必要人工与待同步信息

必要用户动作仅转交本卡与带回结果路径；不需要密钥、启容器、额外G8-P批准或重复选择模型。共享DEF、总状态、架构/CHG及最终验收由编排串行维护，审计者只建议，不改共享文档。经验仅报告已核实候选，不占共享编号或写公共库。

## 以下为已结束的原合同及全部历史

