# STEP018有限验收合同

本文件定义未来验收，不是本轮测试记录。冻结[输入JSON](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-116/design/sample-inputs.json)中的8份纯合成源、1份两页PDF定义、明确答案变体及28个场景。实际样本bytes/hash、产品分配的source/version/record ID映射须在未来首次运行前记录；不借真实资料、不覆盖旧夹具。本文所有“应”是正确预期，当前状态均NOT_RUN。

## 观测和通过语义

每个新场景保存：输入alias/sha、真实层（协议/合成、真实PG、真实Windows监督、真实最终bundle、真实provider）、UTC/mono及准备/运行/持有/停止区间、域及before/after head/goal/scope/view/DataContext、命令key/request/context hash/launch事实、operations kind/state/requests/cost/running/tools/preview四账、007正文hash/相应领域记录/向量空间、引用source/version/page/origin/codepoint、资格/正文抑制原因、自有资源与StopProof。不可读私密/key/DSN；fee记录货币/预留/实际可知费用及UNKNOWN，不冒供方最终账单。

五层分别判定，不能互相代替：①封闭schema/消息容量；②引用原件版本/位置；③结论逐项被引用支持（或明确不足/冲突/自报）；④确定计算的手算/Decimal/真实控件读值；⑤长期效果。①②合格不证明③；③由真实服务输出与冻结rubric核对，模型复判可辅助，不能自签全部语义。④不覆盖开放概念/程序逻辑；⑤本轮不做、不称长期掌握。

只要一个冻结Must场景不满足，应保存失败及范围内修正/最小复检，不填全链通过。可复用已成功且输入/源码/环境未变的部分；付费动作从已COMMIT处GET继续。修改了某adapter只补其相关protocol/调用/语义，不能默认重跑所有旧组件。新的外部能力和R02/记忆域边界在稳定完整成果上集中独审；全项目最终裁定归主控。

## 28个场景与准确预期

| ID / 新证层 | 冻结操作/输入 | 正确预期及持久事实 |
|---|---|---|
| L01 U/T/Q 完整学习 | N导入→核对范围→numeric_goal→plan/accept→numeric_initial_question→wrong_answer→反馈→targeted_question/answer→retest_question/answer→保存理由并显式下一动作；当前feedback生成固定交互说明 | 路径指向分钟换秒/速度依据；错误反馈认可120÷2的算术、指出时间单位/数量级错而非能力事实；下一题针对换算。真实answer/version留原文；feedback/progress原子保存。一次复测正确可保留节点并说明独立证据仍不足；已看参考答案的针对练习不凑独立次数。主链必须完整到保存理由，不能停在生成题。 |
| L02 T/Q 数量/等价正例 | 对N的同一题分别保存JSON内3个numeric_positive_answers，各独立答案版本/命令 | 1m/s、60m/min和完整肯定换算属于等价速度，正确部分获认可。有限确定检查只在支持单位/完整肯定语法内给confirmed；开放理由需语义核对，不能仅按含“1”通过。所有实际调用计预算。 |
| L03 T/Q 单位反例 | numeric_negative_answers前3项：60m/s、1m、1000m/s | 分别指出60倍换算错误、维度不符、1000倍数量级错误；引用N行1—4及120/120手算依据。不能抹去已对的路程/除法步骤。未提供该单位自动核算支持时标unchecked而非虚假confirmed。 |
| L04 T/Q 否定/不确定 | “不是1米每秒”；numeric_ambiguous_answer | 不从否定句抽“1m/s”硬判对。否定答案语义为不正确/需说明；不确定答案按unknown/必要追问处理；当前确定parser应unchecked。不能说已证明用户不会换算。 |
| L05 T/U 进度与暴露 | 在L01后再生成一个未暴露独立题（240米1分钟，答4m/s），保存/evaluate；同键重交该作答；另读取参考答案后作答 | 仅两份不同exercise_id的未暴露、无冲突、required met作答可达到evidence_sufficient并带引用/原因推进一次；若L01复测已暴露则仍不够。重复命令不多一条有效answer、不重复计分。暴露后的正确属于assisted。不能输出“长期掌握”。 |
| L06 T/Q 概念/逻辑 | C目标及concept_positive/negative/partial三个答案 | 等价正例获认可；从原子性推出永不丢失的推理被指出不成立；partial的原子性部分获认可，持久性缺口需补而非全错；引用C的正确行。开放语义检查不冒确定数值算法，归因保持假设。 |
| L07 T/Q 程序推理 | P题及program_positive/negative | 正确序列1→3→6获认可，错误10定位range不包含4及逻辑偏差；引用P行1—5。没有执行用户程序、shell、eval或新增代码工具，tools账无此调用。 |
| L08 T/U/Q 同名歧义 | 同scope两个Java.md，ambiguous_goal，然后用户ambiguous_clarification并把scope明确为J-CODE | 先问实际领域，不能静选。修订后目录只含J-CODE当前版，旧query/结果失效；用户目标草稿/历史保留。真实服务澄清应针对这两义，不问无关背景。 |
| L09 T/Q 不足/冲突 | no_evidence_query；scope N+N-CONFLICT并问conflict_query | 前者明确现范围缺证据，不虚构火星答案。后者同时展示两源矛盾，120m/120s=1m/s为可核计算，不让词项/向量高分自动覆盖来源或伪装N-CONFLICT正确；错误源仍可辨历史。 |
| L10 T/U 真实交互 | L01的合格父feedback→描述生成→v2-08真实宿主；固定d/t控件d120,t120读1，t240读0.5，t0及未定义字段被前拒，reset回1 | 应有真实input ACK/PNG或可信读值、description/artifact/parent hash绑定和现有stop证；无脚本/导航/URL/文件/联网新权限。失败停止保留先前题/答案/进度，有限预览starts/seconds不回退。G11未改边界不重做32项全套。 |
| I01 U/T/Q 完整文字面试 | R+M、interview_goal→ask→incomplete_answer→必要probe→supported_answer→review→finish；可选冻结memory偏好 | 追问具体分工/测量口径；对100→80的20%耗时减少给予相应认可，仅限合成测量。原回答/修正版/问/追问/反馈链可回查，probes≤2，不编雇主/商业效果。记忆只影响解释风格，不进入履历/measurement证据。 |
| I02 T/Q 缺证/自报 | scope只有R，supported_answer的测量部分无M；再self_report | 已证“参与”获认可；测量与个人分工分别标需具体数据/自报未独立证，不能全盘否定，也不能把R用途标签当实际收益证明。该缺口可probe，不必无限追问。 |
| I03 T/Q 虚构收益/范围错引 | invented_claim；把M不选入scope但引用它；给位置正确而不支持“利润50%”的M行2 | 明确拒绝无据履历/吞吐/利润提升；范围外M不得有效引用。位置正确引用仍语义不支持该结论，两层分别记录失败，不称可追溯即可信。 |
| X01 T/U 输入失败/PDF | 一批N、坏UTF-8、PDF-2；仅确认PDF第1页后尝试纳入，再确认两页；替换成功与失败各一次 | 坏项独立原因，N可用；未全核PDF不ready、不索引、不模型。完成确认才可选；补正身份仍user_supplement。失败替换旧版继续，成功替换新版本待核，旧activity/query/chunk资格失效，草稿保留。 |
| X02 T/U 记忆变动 | 学习与v2面试各选冻结memory；修订body、撤销、删除三次明确动作；每次在旧命令freeze后放行晚到 | 旧selection/body/dependency hash不合即拒新调用/抑制旧正文，元数据/成本/原回答保留；新偏好非能力事实，不作源证据。删除影响包含检索/域命令资格；不复活v1面试支持或旧memory版本。 |
| X03 T/U 同键/并发 | 同键同正文并发2提交；同键不同正文；新域动作两个key争同semantic slot；index同一batch竞争 | 同键只有一次claim/admission/外发与effect；异正文409且不改原体，semantic duplicate只指原事实；向量不重复写、费用不退次数。非权威前端/receipt不是可重试许可。 |
| X04 T/U 晚到/失效 | query/model执行中改scope/goal/source；新view或只读selector已切换后送旧response | 007事实可按旧绑定保存，当前目录/feedback/进度不污染；旧DataContext/owner/view响应不显示、不提交后一步、不外发；真实最终bundle验证，不能只做mock route。 |
| X05 T Windows/PG 发送前失败 | 未就绪服务/欠费配置、预算不足、request超65536、缺provider/key名字映射、Embedding维度配置错、启动前owner不准 | fail closed且无出网、无假向量；仍可GET历史。确未发送按not_sent，原reserve/退款含义沿旧账，不假造已收费或新资格。模型工具权限不能由源malicious_material_text批准。 |
| X06 T Windows/PG 发送后未知 | 最低传输替身分别模拟timeout、HTTP响应失联、收到非法schema/非有限vector；取消后晚到 | 发出后unknown保留预留、不隐藏retry；received非法内容保留事实/错误但不授向量/领域资格。停止只自有Job/SUP；远端可能继续如实显示，不声称已取消供方。禁止真实provider做费用故障注入。 |
| X07 T/U 持久预算 | 令一个活动剩1request但动作需query+model；另耗尽running/tool/preview或到deadline；重开同库 | 整步预览不足时拒，不能只做query后偷偷chat；每个实际调用仍逐笔准入防并发耗尽。四账跨重开不归零、累计费用不超批准门；工具/预览耗尽只拒对应动作，既有answer可读，必要Must门仍未通过。 |
| X08 T/U COMMIT丢响应 | 索引query、answer本地保存、feedback投影三类COMMIT后丢HTTP回包，浏览器刷新/GET原key | 读取确已提交事实，向量/answer/feedback各一份；继续已成功处，调用计一次，不因重开自动POST。GET不增requests/费用/计分。 |
| X09 T/U 同normal库重启 | 在L01保存回答、I01保存probe回答及一笔unknown后，正常停止并重新开API，同CID/volume/profile；GET后显式继续新合格动作 | 源/目标/路径/回答/记忆/历史/理由/预算仍在；owner/旧session停止核准后新generation，不复用旧lease；unknown原预留不变且不重发。至少完成一次新的feedback并保存后续理由/面试反馈，只读历史不替代连续执行。 |
| X10 T 数据删除/引用 | 新源index/query/result已存在后删源/版本，随后检索、citation、快照/覆盖恢复；同源chunk跨活动复用 | 当前与历史引用不可用标记、向量清理/抑制、命令及预算元数据保留；不从007/cache旁路回出源文/向量。shared referenced originals沿原fence政策，不无证硬删；维护lane清理与并发新read拒绝精确传播。 |
| X11 T/U 服务/端口/内存 | 迁移失败、缺缓存服务、正常profile不匹配；指定端口分别foreign listener、已知应用listener、无listener但bind拒绝；Docker唤醒后内存低门 | 不改用户端口/kill他人/换名借旧对象；缺能力明确原因，旧数据不覆盖。迁移整txn回滚保旧链；新资源保失败事实、不删卷。2GiB实时门未达不启动依赖资源，不从入口旧采样冒当前达标。 |
| X12 T/U 外发与消费隔离 | 恶意source/tool请求、浏览器伪provider/预算、把embedding007当学习父/teaching/interview/HTML parent；profile同space但不同model/dim混排 | 拒越权，零非法工具/额外服务/混空间；请求只含本步必要范围，UI用途/供应商/次数/费用可见，key不进浏览器/log/包。语义文本不能批准资源。snapshot/readonly角色不能造embedding调用或改结果。 |
| P01 T 非空升级 | compat合成库001—013有model/tool(NULL tokens)、记忆、面试、HTML、unknown/预留及R01正常控制；014整体前向迁移 | 旧行byte/hash/预算/历史语义不变，工具NULL合法；新R02精确shape/owner/trigger/profile核准，未知DDL不容忍。失败不半迁移、不改013原文；旧R01备份仍独立读。 |
| P02 T/U R01兼容 | 全新R01 package恢复目标按1..13可信链，核对并seal，再应用查看 | 原已验查看合同保持；永久只读、无新表/新写/自动索引，不改target到normal、不fallbacksource，不因新v2 profile冒写支持。这里只补新reader仍接受旧profile的定向传播。 |
| P03 T/U R02包 | normal R02快照有两个space身份、received/query/unknown事实、已删源overlay，恢复新target按1..14装载并seal | space/512维/向量hash/007/指针/新三表/预留一致，已删向量不加载；旧execution/秘密不激活，GET可核、全部POST拒。一个损坏维度或hash反例必须failed且不激活；新副本执行不在许可内。 |

## 继承方法、最小新增方法与规模

可复用方法源码（不是本卡新PASS）：`backend/tests/test_teaching_policy.py::test_s1_minute_conversion_arithmetic/test_s1_retest_hand_arithmetic_and_tolerance/test_program_question_is_never_executed/test_two_independent_instances_required/test_partial_unknown_and_errors/test_reference_hidden_until_exposed`；`test_teaching_recovery.py`四种receipt/unknown分类；`test_task103_memory.py::test_cross_unit_exact_ratio_and_support_limit/test_negated_and_uncertain_answers_remain_unknown`；`test_interview_contracts.py::test_probe_cap_and_catalog_identity/test_three_profiles_exclusive_and_frozen_message_binding`；`test_data_exit_c03.py::test_01_same_operation_parameters_identity_and_live_pin/test_02_no_connect_without_time_or_exact_lease/test_03_actual_load_propagates_and_never_publishes_after_late_identity`。旧v1 profile未改部分直接继承结果，v2/v3新分支要新断言，不把函数名当已跑证据。

原件主锚：TASK100教学/修复及其有限独审、TASK103/104记忆/引用、TASK106/107文字面试有限关闭、TASK111/C07与TASK112 G11关闭、TASK114/C03与TASK115有限STEP017终审、TASK116 input-manifest导航。旧RootLease/StopProof/32宿主边界/013 ACL和恢复先引用已采原件；旧PG两秒只证明reading超时，controlled连接参数、最终bundle route只在各自实际层成立，不能拼成物理PG全时限/完整应用质量。

必须新增的最小实现方法：`test_step018_embedding_contracts.py`（wire v4+v3旧体、维度/返回身份/容量、kind和父消费隔离）；`test_step018_retrieval_pg.py`（space/filter/RRF固定排序、原件复核、received+007+vector同COMMIT、unknown及删源传播）；`test_step018_profiles_pg.py`（非空含tool升级、R01/R02可信链/角色/seal）；`test_step018_flows.py`（两域目标/feedback/进度/记忆v2接线及fault families）；`frontend/tests/step018-flow.mjs`（最终bundle两链+草稿/同键/晚到/重开）。写有意义的新断言，不逐份复制旧保护层。实际PG/Windows/SUP/browser尽量在同一完整批内有界合并；不把28场景拆28运行根。

协议/合成故障完成后，真实provider验收只用本JSON合成必要片段：至少L01/L02—L04关键正反、L06三答、L07二答、L08/L09和I01—I03语义，当前题/解释至L10真实宿主；旧安全故障不付费重放。可在一learning活动逐goal修订覆盖三代表类型，interview活动完整包含有据/缺据两分支；其它异常用最低传输替身、真实PG/Job/HTTP/bundle验证。真实语义只记录逐例rubric，不承诺全学科准确率或性能；超10s/输出不足留失败，不能静改时限/换模型。

新paid pilot最多80个外部请求/20元，包含Embedding与chat和全部失败；活动额度与global gate见采用包。开始前按实际已成功部分列剩余矩阵/最坏调用数并确认余量，若80内不足，停止并交缺口，不以“样本已跑一部分”签完整语义。结构/PG传播已成功部分保持，不因真实provider门未开阻塞这些实现。没有费用/账号许可时Q全部未验证，STEP018整体不得通过。

这28个场景覆盖两链所有Must及有限新风险，跨链异常以一个学习域/一个面试域的传播代表加新边界针对例收口，不枚举无限笛卡尔组合。首版保留原Should Office/图片/来源推荐、Could语音及未来Linux公开部署为未纳入；长期效果另收集证据，不成为本有限样本的伪精确指标。
