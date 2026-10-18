# TASK-100 审计修复03：范围与证据适用性

本卡11项修正与必要补证已完成，作为原101窗口集中增量复核的候选。这里列执行事实及适用范围，不代替独立审计或编排验收。

A＝实际合成PG/HTTP/Windows/浏览器事实；B＝源码、固定参考推导与身份核对；C＝明确标注的只读显示/时序控制；D＝未运行。A中的模型返回是固定合成transport，不能作为真实provider质量。

批次：B1＝101329.428351首合并批，B2＝101919.561049目录修正前批，B3＝103020.095611主链与实际HTTP/Windows批，B4＝110007.993696最终只读浏览器批，均为2026-10-05 UTC，完整目录在本证据根。原总批FAIL保留。

## F/E修正与直接证明

| 项目 / DEF | 修正和实际判据 | 证据与范围 |
|---|---|---|
| F01 / 008 | 分开参考内部运算与实际作答的数值/单位核查；Decimal有限换算，可靠信息不足为unchecked/unknown；冲突不能加入独立观察或推进。 | B1及B3 numeric_result PG；B3实际60m/s和0.01m/s两个窗口故意将模型观察设全met，确定屏障均拦下。离线正确单位、冲突、歧义及无法解析。A/B；开放概念/程序不使用任意自然语言自动判分器。 |
| F02 / 009 | 每记录原source/version/revision/hash资格进入同一业务SQL读面，曝光写路径也核旧题原来源。合法新范围不能恢复旧源派生正文，用户答和纠错仍保留。 | B1及B3 source PG覆盖新S2、同源新版、撤销后新S2三分支，workspace/history/record/command各一业务SELECT；旧未曝光参考写入拒绝。B3实际HTTP旧正文抑制、引用409、用户原文可读及零读副作用。A/B。 |
| F03 / 010 | 累计读取stream，首超限块即拒；严格UTF-8与递归重复JSON键检查，认证前后边界保持。 | B3真实HTTP7个负例、合法Unicode目标写入及行数/四账无额外作用；实际reader观察34次块长度。离线ASGI连续块证明不读取后续块、UTF-16/32、非法UTF-8、嵌套重复键。A/B；未做压力批。 |
| F04 / 011 | accepted且未claim允许用户显式同键恢复，使用原持久request/frozen context；当前资格与原CAS、admit/mark仍为权威。claimed/无operation/UNKNOWN仍只读。 | B1真实PG4竞争claim只一次，claimed不重发；原7recovery方法当前字节重验。B3原accept COMMIT后中断点、两个并行同键模型恢复仅1SUP/1请求，原context/hash不变；实际工具恢复1SUP/1tool、模型账不变，GET和重放零新动作。A/B。 |
| F05 / 012 | 活动锁内累计所有历史path_accept，上限32；同键回放先判，不重复占数。 | B1实际32合法、33拒绝、同键回放零新增，源/头/事务正常路径同批。A。 |
| F06 / 013 | G7明确沿用入口，服务端验证当前model/G7规范成果、operation/hash/goal及原源；goal保留seed身份。 | B1/B3 PG及B3真实HTTP合法seed目标保存、伪hash/kind/活动/陈旧与失效反例零新增；B3浏览器真实seed读取→明确点击→保存目标且模型账不变。G7前提通过原admit/mark/007身份链合成准备，标为无SUP/无provider发送。B4最终包只读seed入口确认0POST。A/B/C；旧first未重启。 |
| F07 / 014 | 路径、公开参考、反馈各自record/citation身份和原位置入口，真实cursor分页与400/409处理。 | B3实际HTTP三类引用/隐藏参考/失效源/分页及负例；B3实际浏览器三类入口、超过20历史、R2纠错、真实400/409。B4最终包用真实PG只读投影补验三类入口及分页显示。PDF物理页2、抽取序列1仅为B3标注显示夹具C；PDF解析主体未变，不声称新PG资格/PDF抽取。 |
| F08 / 015 | 完整goal/path/node/exercise/answer及head revision编辑身份；外部变化保留输入、提示、禁用，明确换绑；历史/工作区/citation各自序号及Abort。新增标签页owner与Web Lock防克隆身份覆盖。 | B3实际新答案POST、原A1输入保留及禁用；实际迟到R1不覆盖R2，零费纠错目标确为R2。B3也暴露共享IDB槽缺陷，FAIL保留。B4最终包实际Chromium/Web Locks/IDB证实克隆sessionStorage得到不同owner、两旧槽不覆盖、A2明确载入/沿用、刷新复原、迟到记录和workspace卸载不污染。API为标注只读快照，0POST；不声称B4又有真实HTTP写入或新应用。A/B/C。 |
| F09 / 016 | 字段独立严格十进制字符串，value/instance≤1e18，left/right≤1e12，tolerance≤1且≤12小数位。 | 离线真实DTO函数覆盖1e13、边界、12/13位、浮点/科学计数/非有限/超域拒绝；B1/B3真实结果提交与B3实际三个场景消费规范引用。A/B；G5域不扩张。 |
| E02 / 017 | 合成资料三主题原文分别匹配节点及各参考维度/反馈论点；不固定取evidence[0]。 | 重排目录及缺依据no_evidence离线；B3实际已保存8条记录、24个论点—citation—目录原文—位置/hash—真实HTTP回查对。独立固定前提和逐条参考解释见content-review.json；不只按目录成员检查。其余正常复测反馈是实际窗口/进度事实，没有追加原文回查行。两个故意false_met是F01负例，不作为内容通过。A/B；101仍须独立核例。 |
| E01 / 018 | 不补造无法恢复的旧三个模块；最终字节下按事务/恢复/来源等直接依赖定向执行，并逐方法说明替代及复用。 | B1当前后端29个定向PG，B3受目录/夹具变化影响的3方法再次实际通过；共32次执行、29不同方法。旧29方法中24同方法当前PG、跨活动/隐藏参考由新实际HTTP替代、单SQL由新PG替代，immutable与009兼容只继承未变迁移依赖。旧4HTTP方法不重新冠以PASS，新增3个受影响真实HTTP。完整身份与原始行号见method-bindings-final.json。没有“旧最终29PG整体通过”结论。 |

## 099 V01—V20与H1—H4

| 编号 | 本轮直接依据及有效继承 | 仍受限的层 |
|---|---|---|
| V01 | 当前goal/CAS PG，F06 seed PG/HTTP/真实UI；无G7直接目标正常。 | seed是目标身份，不是能力观察。 |
| V02 | 当前path语义槽/接受事务，F05 32/33与重放，B3实际plan→accept→exercise及三节点引用。 | 不使用模型passed声明授予节点权威。 |
| V03 | B3实际计算/概念/程序题和逐点依据；F02旧源资格；隐藏参考404/公开后成功；F07引用UI。 | PDF新资格及解析D，位置显示C；不执行用户代码。 |
| V04 | F01确定冲突屏障，程序正确结果与错条件/缺说明分离，概念四维正常；逐论点固定参考核对。 | 开放自然语言等价与真实模型总体质量D。 |
| V05 | 当前耗尽预算仍零费保存PG，B3真实答/改答/纠错及四账对照；旧invalid/UNKNOWN保答按未变主体继承。 | 未扩到所有配置组合。 |
| V06 | 当前distinct/assisted/contested策略与PG、B3两真实独立计算实例→n2；两个false_met阻止错误推进。 | evidence_sufficient为本路径有限依据，不是永久mastered。 |
| V07 | 当前相反反馈/纠错争议PG；B3实际R2零费纠错、旧新事实保留；分页和选择补齐。 | 全面记忆删除不在本卡。 |
| V08 | 当前同键、语义槽与真实答案竞争PG；F04并发恢复一次SUP。 | 没有隐含同父再发/退款。 |
| V09 | 当前7 recovery及F04 accepted恢复；原UNKNOWN/丢响应事实只继承其已确认范围。 | claimed/no-operation继续保守unknown。 |
| V10 | 当前冻结上下文/admit/mark PG；原真实late_goal/late_answer结果仅历史、不推进部分依赖未变；F08新答案UI补齐。 | 不把历史结果删除，也不把旧预算归零。 |
| V11 | F02实际三源分支、实际HTTP引用资格及原late_source出站/终态屏障；F07自身引用入口。 | PDF所有组合D。 |
| V12 | 原cancel/hard_stop/SUP/Job/关门主体hash不变，既有真实停止证据复用；本轮12个实际窗口均settled/树零，四批精确收尾。 | 旧硬停待折叠事实仍保守，未改成已结算/退款。 |
| V13 | B3实际11model+1tool各自Q/C/T/R账；工具同键恢复和已有有限G5算法复用。 | 无任意程序执行、真实token计费或自然语言工具规划质量声明。 |
| V14 | F03真实stream/编码/重复键/auth零副作用，F09各字段闭域，F05实际容量；合法Unicode实际入库/UI显示。 | 没有压力或全笛卡尔组合测试。 |
| V15 | 本轮实际同键恢复/完整草稿绑定；B4原生两标签页/克隆owner/IDB重开；旧IDB全文先存、失败0POST、UNKNOWN只GET行为按未改提交路径复用。 | 旧显示替身仍C；不声称新实际PG写入。 |
| V16 | F08 R1/R2、切换/卸载、答案变更完整身份；citation独立Abort/序号。旧单快照轮询、最大重叠1、hidden/卸载、120秒边界保留。 | B4变化时序以已存A1/A2快照控制，明列C。 |
| V17 | F02真实每读1 SQL、逐记录来源；B3实际cursor400/409与完整分页UI；当前DTO局部抑制。 | 名为rebuildable的方法只测封闭枚举；全面投影重建未动态运行，原限制保留。 |
| V18 | 001—009与旧写入/停止主体hash未变；四批真实已有库/owner/角色、009函数/触发器、全列ACL核定；旧非空兼容/六迁移原件有效范围复用。 | 未重跑六迁移、全部旧G7 first/followup/plain；不执行DELETE负例或DDL。 |
| V19 | 三场景固定资料/手算/程序手推，8条实际记录24对引用核例；错答故意false_met负例明确。 | 真实provider小样本、付费、外发未授权/未运行D。 |
| V20 | 全部尝试保留、新旧账分列、最终源/dist/as-run/post绑定、精确收尾；旧许可失效，新入口守卫离线证实；结果交原101。 | 独立复核及编排G8/STEP/M-1/部署裁定尚未执行，本窗口不签。 |
| H1 | 旧实际8模型+1工具持久链/保存/复测有效事务与停止部分复用；本轮5窗口真实plan/计算/独立复测及另4窗口概念/程序补内容依据，1模型+1工具恢复、另1数值负例，共12SUP。 | 旧概念/程序无关引用内容不继承；本轮固定返回不等同真实provider。 |
| H2 | 当前实际PG同键/答案竞争、F04实际并发恢复一次SUP、原丢响应重开只GET事实。 | 没有新许可外直接诊断/重发。 |
| H3 | 当前admit/mark资格PG、原目标/答案/来源晚到事实、F02有效新范围旧源反例、F08编辑切换补证。 | 外部有效范围不能恢复旧派生正文；预算/G不重置。 |
| H4 | 当前recovery、错误答案屏障、实际零费改答/纠错；原invalid/UNKNOWN/cancel/hard_stop证据及只读显示保留适用范围。 | 进程树零不等于把旧保守账强制折叠/退款。 |

## 原件与最终身份入口

- [最终完整身份、36项实际差异及132个post对象](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/audit-repair-03/final-identity.json)；实际运行源/dist范围124，另8项未执行但未变的保护迁移单列。正确diff为其中链接的diff-final/；diff/是交付索引修正前的错误原件，不作为产品删除证明。
- [逐方法绑定](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/audit-repair-03/method-bindings-final.md)、[首批夹具变化适用性](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/audit-repair-03/first-PG-fixture-applicability.json)。
- [实际8条内容oracle](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/audit-repair-03/2026-10-05T103020.095611-0000-repair-combo/content-oracle.json)、[逐对固定参考核对与全部11个模型样本性质](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/audit-repair-03/content-review.json)。
- [最终只读浏览器7项检查及原生存储](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/audit-repair-03/2026-10-05T110007.993696-0000-readonly-browser-combo/readonly-browser/facts.json)、[只读PG投影及其零作用对照](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/audit-repair-03/2026-10-05T110007.993696-0000-readonly-browser-combo/readonly-browser-input.json)。
- [全部批次/窗口/原旧账/清理索引](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/audit-repair-03/attempts-and-resources.json)、[持久计数账](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/audit-repair-03/attempt-ledger.json)、[最终只读OS/容器/Job核对](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/audit-repair-03/final-resource-read.json)。

原009/停止/G7等依赖未变并有具体旧动态事实时复用；旧不具完整被测模块的业务结果不借当前编译升级。最终前端owner改动只影响本机编辑隔离，B3业务HTTP/Windows的精确后台及直接夹具依赖与当前一致，复用证明另存B4的http-reuse.json/windows-reuse.json。B3旧bundle不是最终bundle；最终浏览器读取字节与第二构建及B4完整as-run绑定。
