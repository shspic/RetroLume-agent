# TASK-100 / R-094 审计修复03结果

**F01—F09及E02/E01修正和本卡必要补证完成；精确资源已停止并保留，候选成果交原TASK-101窗口集中增量复核，本窗口不签G8放行。**

完成有限答案核查、逐记录来源资格、严格HTTP输入、accepted未claim同键恢复、32路径容量、G7明确seed沿用、引用/历史读面、完整编辑身份与标签页草稿隔离、数值字段闭域，以及三场景实际内容依据和最终被测字节绑定。本轮32次PG执行（29个不同定向方法+3次受影响补验）、3项真实HTTP、12次实际Windows SUP均通过各自断言；最终76项离线、第二次typecheck/build、7项最终包浏览器补验通过。原前三个真实总批FAIL保留，不改成PASS。

## 身份、合同与交付

- TASK-100/R-094；父TASK-099/R-093，审计TASK-101/R-095，STEP-009—012；实际客户端Codex desktop、模型GPT-6（精确部署型号未向此窗口暴露），A+为角色安排，沿用同实现聊天窗口；没有派子Agent。
- 根目录D:/shspic/project_NO3_RetroLume-agent；task_model，锁定V4.0/AGENTS CHG-0003，需求v1.1、架构v0.83、执行动态v2.05。首改前141个输入/产品/保护对象/规则/审计身份全部核一致，原pre保存；最终公共七指纹、18个保护对象、099合同与101原报告未变。
- 当前有效合同为[TASK-100审计修复03](D:/shspic/project_NO3_RetroLume-agent/DocuN/tasks/TASK-100.md)顶部；新许可TASK-100-audit-repair-03-20261005单列，不借用任何旧额度。授权终点为候选交付和精确自有合成资源收尾。没有真实provider、付费、外发、部署、Git写入、安装、DDL/角色扩权或用户库操作。
- [完整身份及正确diff/post导航](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/audit-repair-03/final-identity.json)：14个既有产品模块修正、1个必要教学引用组件新增；7个既有测试/夹具修正、11个专用测试/夹具新增；3项生成dist差异，共36项。001—009、旧activities写入主体、worker/launcher/SUP/Job/停止、G7后端、资料/PDF主体、依赖锁、私配置和DocuS未改。
- [F/E、V01—V20和H1—H4的证据适用性](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/audit-repair-03/evidence-applicability.md)、[逐方法绑定](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/audit-repair-03/method-bindings-final.md)、[实际论点—引用核对](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/audit-repair-03/content-review.json)、[尝试及资源索引](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/audit-repair-03/attempts-and-resources.json)。不导出完整聊天/推理给审计者。

## F01—F09 / E02 / E01状态

| 项目 / DEF | 本轮状态和具体结果 |
|---|---|
| F01 / DEF-008 | 已修并实测：参考自身算对与答案支持分开；60m/s、0.01m/s即使模型全met也不能加入独立观察或推进；歧义/无可靠解析保留unknown。Decimal有限域，不扩任意自然语言判分。 |
| F02 / DEF-009 | 已修并实测：同一业务SQL快照核每记录原来源；S1替换/撤销后合法S2或S1新版不能恢复旧题/路径/反馈；旧未曝光参考拒写，用户答/纠错仍读。 |
| F03 / DEF-010 | 已修并实测：HTTP累计stream早拒超限、UTF-8严格、递归重复键拒绝；真实负例auth/字节/编码/重复键零业务写入，合法Unicode仍可存。 |
| F04 / DEF-011 | 已修并实测：accepted未claim明确同键恢复原request/frozen context，实际并发模型只1SUP/1请求，工具只1SUP/1工具；claimed/无operation/UNKNOWN和GET不补发、不退款。 |
| F05 / DEF-012 | 已修并实测：活动锁内历史路径总数32合法、33拒、同键回放不占新数。 |
| F06 / DEF-013 | 已接通并实测：G7明确“沿用此目标”，服务端核当前G7身份/hash/goal/来源，goal留seed；伪hash/kind/活动/陈旧/失效拒绝且零新事实/调用。无观察、无重入first。 |
| F07 / DEF-014 | 已接通并补证：路径/公开参考/反馈各自引用回查、真实来源失效提示、完整cursor历史与400/409；PDF页号/抽取序列仅标注显示验证。 |
| F08 / DEF-015 | 已修并补证：完整编辑身份和head revision、外部A2变化保输入/提示/禁用、明确换绑；历史R1/R2独立取消序号，切换/卸载隔离；修复实际发现的两标签页IDB共享槽。最终原生Web Locks/IDB/刷新实测通过，API快照层准确标注。 |
| F09 / DEF-016 | 已修并补证：value/instance≤1e18、left/right≤1e12、tolerance≤1且≤12小数；严格十进制字符串，1e13合法，浮点/超域/非有限/科学计数/非法精度拒绝，G5域不扩。 |
| E02 / DEF-017 | 已修并补证：三主题选择实际支持片段、重排不猜索引、缺依据no_evidence；实际8条保存记录24对引用经原文/hash/位置/真实HTTP及独立固定前提核对。两个故意误判负例不当内容PASS，真实provider质量不声明。 |
| E01 / DEF-018 | 已收口适用范围：旧中间三模块无法精确恢复，不重复101失败重建、不补造；当前29定向PG+3补验与完整原件绑定，旧方法逐项同方法/等价替代/未变依赖/未重跑列清。没有整体升级旧29PG/4HTTP。 |

以上是执行者修正及验证结论；DEF状态、独立审计裁定和总账仍由编排维护。

## 原件、最终被测字节与分级验证

[首改pre及141个实际读入身份](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/audit-repair-03/preparation.json)对应120个项目pre副本。最终132个post对象中124是B4实际as-run源/dist范围，另外8个是未执行且未变的001—008保护迁移。完整副本/hash、正确diff-final及每个变化均由final-identity.json索引；新增文件不补造pre。交付索引初稿误把运行清单之外的保护迁移记成删除，交付前已纠正并保留错误索引/diff原件；实际产品无这些删除，最终只采用diff-final。

最终后端全部app字节在B1/B3/B4一致；009为11b1c2bc8cb2482a4fa509b897c3afb8f3f5f7be3eb4e8e4aab559706944c1a3。首批PG后夹具唯一内容变化为缩短n2概念题干，B1所选PG只使用n1题/plan；完整AST与直接依赖核对另存，数据根移到独立data/backups后，受影响数值/来源/seed三个方法在B3真实重验。没有仅凭函数名声称版本未变。

- **PG/HTTP A层：** [B1完整29方法stderr](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/audit-repair-03/2026-10-05T101329.428351-0000-repair-combo/repository-raw/stderr.txt)、[B3受影响3方法](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/audit-repair-03/2026-10-05T103020.095611-0000-repair-combo/repository-raw/stderr.txt)、[B3真实HTTP3方法](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/audit-repair-03/2026-10-05T103020.095611-0000-repair-combo/http-raw/stderr.txt)。每段完整stdout/stderr、exit/时间/as-run副本/后置hash保留。业务身份均为合成主库app最小权限；没有用admin成功代替业务权限。
- **Windows A层：** [B3四具名场景及12 SessionOutcome](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/audit-repair-03/2026-10-05T103020.095611-0000-repair-combo/repair-windows-facts.json)：11模型+1工具，12次SUP函数进入/创建、12 Job创建/挂起启动/Resume/close，11次固定transport实际发送/返回，所有窗口settled、active_processes_at_end=0、cleanup_incomplete=false。原真实launcher/worker/Job/PG权威未替换。概念/程序前置通过原身份链合成准备且明列无SUP；旧17故障窗不重跑。
- **内容 A/B层：** [B3原始内容oracle](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/audit-repair-03/2026-10-05T103020.095611-0000-repair-combo/content-oracle.json)及content-review逐对列实际论点/citation_id/catalog/原文位置/hash、支持/不足理由。速度120/(2×60)=1，复测180/(3×60)=1；原子性保持A100/B50且不单独保证隔离、具体隔离级别未给；程序固定列表手推0/0/1/2，0>0为假，return在循环后，没有执行用户代码。路径独立复测理由属于099政策，不冒称资料本身的事实。
- **前端 A/B/C层：** [第二构建完整输出](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/audit-repair-03/2026-10-05T105833.370399-0000-frontend-build/build-raw/stdout.txt)typecheck/vite通过，最终index-B3juxyZb.js/C8N4OxWs.css与B4实际消费字节/hash一致。B3真实HTTP浏览器已完成seed保存、三类引用、分页、R2纠错和实际A2改答，但尾部IDB共享槽断言FAIL。修正后[B4最终7项检查](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/audit-repair-03/2026-10-05T110007.993696-0000-readonly-browser-combo/readonly-browser/facts.json)通过：原生Chrome/Web Locks/sessionStorage/IDB实际执行，已存A1/A2及本次真实PG只读投影用来控制时序。56个浏览器GET、0POST/0SUP/0业务写入；应用未再启动，没有新HTTP认证/写入证明。列表筛选、空PDF候选和history token重绑明确列为只读显示控制。
- **离线 B层：** [最终common 58](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/audit-repair-03/2026-10-05T105948.833483-0000-offline/common-raw/stderr.txt)+[repair/control/bootstrap/readonly 18](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/audit-repair-03/2026-10-05T105948.833483-0000-offline/repair-raw/stderr.txt)，共76、0skip，真实函数/ASGI输入及运行控制通过。owner函数纯JS锁替身为离线控制，不冒充浏览器；最终native证明另在B4。

## 全部失败、修正和依赖未运行

9个离线批、2个构建批、4个真实入口均在尝试索引及持久账中逐段保留。离线出现3批FAIL：补充控制测试的TestClient参数/API路由假设、goal DTO版本构造、TS7无旧JS transpile API；分别修夹具后通过，均无业务资源。离线成功曾为69/70/72/75，最终为76；构建两次各PASS。交付索引另有一次解析docstring换行导致FAIL及一次保护对象清单误分类，原稿/说明保留；修正不改任何原测试结果或重新运行资源。

| 真实入口 | 总状态 | 实际失败、已生效部分及修正 |
|---|---|---|
| B1 / 101329 | FAIL | 精确容器/库预核和29PG PASS；app启动因bootstrap仅识别旧许可拒绝，后续HTTP/Windows/browser not_run；补新许可显式白名单及真实ASGI配置离线测试。cleanup PASS。 |
| B2 / 101919 | FAIL | 29PG按精确依赖继承、不再执行；app启动发现data下嵌套backups违反独立目录合同；后段not_run。改为同级data/backups，再定向补验受影响资料根。cleanup PASS。 |
| B3 / 103020 | FAIL | PG3/真实HTTP3/Windows12及已完成浏览器检查PASS；两标签页共享A1 draft_id导致第一旧槽被另一标签页覆盖，尾断言FAIL。修完整身份+标签页owner/Web Lock，而不是修改断言掩盖产品问题。cleanup PASS。 |
| B4 / 110007 | PASS | 受影响F08最终包专项：已有精确容器和库→真实只读PG投影→标注快照的原生浏览器→独立收尾。没有app启动/POST/SUP。已有后台HTTP/Windows依赖逐hash复用。cleanup PASS。 |

app3/3触顶后停止受影响应用启动，按卡内第6条允许的真实或标注只读快照补验界面；未追加许可、未开第5入口，没有把B4当新应用整链。前三个失败及全部not_run留在原件。

## 新旧投入与资源终态

| 本轮计数 | 实际 / 新上限 |
|---|---|
| 真实合并入口 | 4 / 4 |
| 精确容器start尝试 | 4 / 4 |
| 应用start尝试 | 3 / 3 |
| SUP创建函数进入 | 12 / 18 |
| 浏览器launch | 2 / 3 |
| driver launch | 2 / 3 |
| 前端build | 2 / 2 |

本轮最终冻结计时：离线78.735/1800、真实199.422/3600、独立收尾26.906/480、主动10059.821/21600秒；主动固定单调口径包含首读保守120秒，未因换上下文清零。第一真实批77.094秒保守含其5.188秒child cleanup，另外5.172秒cleanup收费仍保留，未退回；后批只从外层真实elapsed扣已单列child cleanup。证据封装尾段按完整finalizer墙钟15.453秒保守追加离线账，前置重叠小段不退回；主动补计到最终封装核验时点。最终精确数字及账hash见[最终冻结和投入](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/audit-repair-03/final-freeze-and-usage.json)。截止/有界finally覆盖完整入口和全部子段；所有计数动作前持久扣记。

旧续作02仍为entry6/container5/app3/SUP21/browser3/driver3/build1，离线42.750、真实261.211、清理33.313、主动13643.958505秒（原分段口径及未知尾段）；其6个总批均FAIL、许可已结束。初轮至少9入口/至少一次start、漏5.940秒、续作01的4入口及历史未知不改。新旧不合并为精确总数，不借未用额度。

[最终只读资源核对](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/audit-repair-03/final-resource-read.json)40项通过：精确容器80ae914…d4d Exited(0)、Running=false/Pid=0，18100/55442无监听，自有SUP/worker按PID+birth不存在/已结束，12个命名Job查询均无活动树，无Playwright profile残留。四批finally各自原件PASS。没有删除容器/卷/库/资料/事实行，所有合成数据和失败证据保留；仅核定归属后通过内存/STDIN重置三个既有合成角色凭据。历史running/UNKNOWN账不因进程零被改为settled或退款。本轮候选交付后运行许可结束，不因脚本可读、SUP/browser尚有名义余额恢复执行。

## 未验证、风险与编排下一步

真实provider/付费外发及V19真实质量D；固定transport只支持给定三场景，不推总体教学准确率。PDF页号控制是C，未新增PDF资格或全部解析组合。旧未变009/停止/真实晚到/UNKNOWN与既有只读重开按清单继承；未再跑六迁移、17旧故障窗或全部旧G7业务。全面投影重建未动态执行，方法名不能升级其枚举检查。完整记忆删除、M-1、部署和项目通过均不在本卡交付范围。

剩余合同内产品修正/必要补证无未完成项；独立复核与编排验收仍待原101窗口。建议编排登记本卡候选交付及新旧账、保持G8待复核，把本结果、最终正确diff/源码身份、逐方法/内容/适用性及原始证据交原TASK-101集中增量复核，再由编排裁定DEF-008—018与STEP/G8；执行者不写共享DocuS或自签关闭。

结果已保存于指定TASK-100-result.md，原历史全文以连续原字节追加在下方；历史字节33904、sha256 4d12379a337fd65600264b9c0e95eac35251891485389e61e8eecf7000b164be，已与首改保存核一致。当前文件和全部新导航链接可读核验见[交付可读性](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/audit-repair-03/delivery-readability.json)。

---

以下为此前TASK-100结果全文原字节，历史结论/路径/预算/失败不改；遇四个旧根历史路径按项目AGENTS归档映射读取。

# TASK-100 / R-094 续作02结果（2026-10-05最终回传）

结论：剩余产品修正、真实教学主链及存储/轮询控制已取得逐项证据，可交编排集中独立审计；没有一个原始main-combo总批为PASS，末批的纠错封套断言已修正但未重新启动浏览器，原始FAIL全部保留。不能据本报告签G8、STEP009—012全通过、真实provider质量、部署或项目通过。

实际证据包括58项最终离线检查、29项不同的真实PG检查、4项有效HTTP检查、最终009六类迁移场景及补充非空兼容、原Windows监督矩阵17窗、重开后三题型主链和10项实际浏览器控制。最后纠错成功、UTF-8和HTML字面显示由真实收据、保存的原生页面/截图及有界原件核验补证；不把原始浏览器总批FAIL改写为PASS。

## 1. 身份、规则和成果保护

执行者为Codex Desktop报告的GPT-6，精确变体未确认；是用户转交的业务实现聊天，不是独立审计者或编排者。沿用TASK-100/R-094/G8-P，没有自派Agent、开新聊天、占用101/R095或维护第二份总状态账。

项目根D:/shspic/project_NO3_RetroLume-agent，入口AGENTS.md。公共规则锁定V4.0/CHG-0003，必要AGENTS、WORK及07已读，七指纹一致；099唯一合同SHA256仍为0f38de84d6036e48a9fa544ba8304b37a72cf89e56e29fc05bef500609cc0e67。本卡读入时需求v1.1/架构v0.80/执行动态v2.02；运行期间另一个获用户批准的归档维护将项目入口和导航更新为架构v0.81/执行动态v2.03，已补读改动，仅采用历史路径映射，不重置业务合同或预算。公共规则版本未变。

首改前103项核对、75份必要副本、最终产品/夹具、逐文件差异和来源归属见[最终身份](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/continuation-02/final-file-identity.json)、[最终差异](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/continuation-02/diff-from-pre-final-20261005.patch)及preparation.json。仅有最终身份但没有首改副本的既有外围文件不冒称本轮新增。README中本轮教学说明与另一项归档的导航增量分别归属；他人的AGENTS/DocuS/归档修改保留。

没有修改001—008、原launcher/worker/SUP/Job/停止主体、依赖锁、用户配置或原始需求，没有安装/下载、真实provider/密钥/付费、用户库迁移、Git写入或发布。原初轮与续作01结果16992字节逐字节保留；置顶更新只处理本执行者续作02报告，先前版本亦留在本证据目录。

## 2. 最终修正与业务事实

- DEF-003候选：009核真实前置结构及CHECK定义；records全列UPDATE/DELETE拒绝，app仅SELECT/INSERT，commands/head仅必要列级UPDATE。本地及模型/工具效果在INSERT前成形，并与head/command/原007正文同事务；真实最小权限、不可变与零半写成立。
- DEF-004候选：冻结真实目标、接受路径、题/量规、答、纠错、反馈/核算及目录/正文hash；T-intent/claim/admit/mark锁内复核当前父事实、pending与来源。原settle关门后合法下一窗可进入，实际同一活动连续模型窗口已走通。无受信绑定不预留，版本改变在mark前拒；缺command或坏教学封套回滚原正文/终态。当前反馈/exposure/progress/head一次原子效果；目标/答案合法晚到仅历史，来源/取消仍按原G3拒新正文。
- DEF-005候选：workspace/command/history/record各一条业务CTE快照，TEXT与psycopg JSONB类型正确处理。view_token/游标漂移409、参考暴露、实际目录引用与作答offset/hash、no-store和本地会话权限已验证；坏单项局部抑制，来源失效保留用户文字。
- DEF-006候选：唯一有限runner有动作前持久计数、真实发现/方法白名单、单调截止、依赖阻断、完整原始日志及独立finally。Windows子段实际通过；浏览器实际执行最终bundle。README导航不由产品加载，现与严格产品/夹具身份校验分列，避免并发文档维护被误作运行源码变化；归档增量没有回退。
- DEF-007候选：确定未准入才清本键pending，claimed但无operation/无收据/UNKNOWN保留槽且不重发。同键核对0新增SUP/Q；无效输出确定失败后显式新键retry可提交；真实提交成功但浏览器丢响应后只GET恢复并核对。终态相同record重读在原settle后返回ALREADY_PRESENT，各相关表和Q/C/T均零变化。
- 进度与界面：参考后同题续答记辅助；两个不同未暴露实例才形成有限推进，并保留理由。纠错及相反反馈保留旧事实和争议，不永久宣告mastered。三题型、保存/评价分离、历史、有限计算、只读重开、原生存储失败0POST、容量/跨标签、隐藏/卸载和迟到输入/焦点保护已取得下述限定证据。

这些是候选修正及有限事实，不自行把DEF正式状态改成关闭。

## 3. 六次入口、失败及证据复用

| 入口 | 实际结果及后续处理 |
|---|---|
| 1，2026-10-04T151643.300656-0000-main-combo | 容器、两库、001—009/权限和六迁移场景通过；26项PG中16通过、10 ERROR，共同前置把dict消息传入Message封套。只修fixture转换，后续依赖not_run。 |
| 2，2026-10-04T152236.912137-0000-main-combo | 受影响整合类9通过、1 FAIL；SQL观察器误计两条set_config超时设置。仅修观察器，仍要求一条WITH业务读取。 |
| 3，2026-10-04T154155.612447-0000-main-combo | 两项定向PG、应用和3项HTTP通过；引用端点实际200，夹具误读citation封套后ERROR。只修引用夹具，Windows/browser未运行。 |
| 4，2026-10-05T033911.225278-0000-main-combo | 受影响HTTP方法通过，原Windows17窗全通过；最终dist主浏览器H1通过，第二浏览器完成概念/程序、恢复及丢响应核对。剩余控制因错误横幅含关闭按钮，严格文字定位超时。原批FAIL保留，改为alert局部文本定位。 |
| 5，2026-10-05T040952.525997-0000-preflight-refusal | README在最近计划/离线后被获准归档维护更新，预检拒绝；没有启动资源，仍消耗入口，0.697秒向上计入真实账。已查明归属，保留增量，修正文档与运行身份校验边界。 |
| 6，2026-10-05T041623.670843-0000-main-combo | 两项补充PG通过：ALREADY_PRESENT零写及已有m05非空009兼容。应用、10项浏览器控制、键盘及真实零费纠错成功；末尾夹具读取reason.text，而实际统一workspace为reason.body.text，断言FAIL。已修夹具并保存最终离线；原页面/截图/收据另经原件核验通过，未重启浏览器，不把该批改为PASS。 |

每个实际批含完整stdout/stderr/result、as-run身份、分段时间/退出码、事实与cleanup。第五次拒绝为真实工具输出的保存副本，明确没有独立业务子段，不补造运行。逐方法、逐断言和产品字节复用绑定见[验证索引](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/continuation-02/verification-index.json)。29个不同PG方法和4个HTTP方法仅各计一次，不因失败后定向复验重复计总数。

第四批Windows记录8个函数：正常H1、目标晚到、答案晚到、来源晚到、取消晚到、UNKNOWN与放弃、无效输出与显式retry、硬停止，共17个真实业务窗。H1 activity为617759bb-693a-4e4d-a754-a5dc47d60956；首浏览器8模型+1原finite_calculate，Q8/C800000/T1，n1两个未露不同实例后推进n2。重开后另4模型完成概念与程序部分正确，Q12/C1200000/T1，n3保留needs_repair；实际只传输合成provider内容，用户程序不执行。

第四批共有21个实际SessionOutcome（17矩阵+4重开），21次SUP/create/Job/spawn/resume/close观察；20次模型provider_started、18次provider_returned，工具不冒用provider字段。全部已观察SessionOutcome树零且cleanup_incomplete=false，含PID/创建时间/Job身份。取消和硬停仍保留原R90/pending fold保守账，不代worker退款；末屏H1时间账R0/S14。

## 4. 构建、迁移和浏览器原件

本轮唯一build为2026-10-04T151300.859935-0000-frontend-build，tsc/vite通过。最终frontend/src/package与dist仍精确绑定，浏览器确实读取该bundle；没有第二次构建。JS index-DnD3XCQb.js SHA256为3032cc6ca0276562664c25dcb829311af4dde8e0af87ab79d913f8b38eb78e5e。

009原文件SHA256为11b1c2bc8cb2482a4fa509b897c3afb8f3f5f7be3eb4e8e4aab559706944c1a3；Python统一换行后执行的UTF-8/LF为e6d9628e98b74c42aba217b9068825a5fafac93b61e21cda729856ff48a984b2，二者分别登记。六类既有最终迁移证据不重跑；第六入口使用固定task100_m05_midway原回滚后的001—008，加入四种合成旧操作再执行最终009，五旧表全部行摘要不变，零backfill。没有第七schema、删除或重建；此前m05中途回滚原件继续有效。

10项浏览器控制为：原生IDB失败、UNKNOWN有界单快照轮询、隐藏暂停、卸载停止、只GET重开、迟到不覆输入/焦点、跨标签摘要容量、来源失效禁用、取消禁用、预算尽模型禁用且允许零费保存。UNKNOWN读33次、最大重叠1，观察截止后不再自动读，均零POST。资格响应替身仅证明显示控制，来源/取消/UNKNOWN的服务端事实另由真实PG和Windows证明。

第六入口只有一个实际新增命令：correct，record b579188b-0c6e-42e9-8665-870aa32804bf，seq36，revision24，model_called=false/tool_called=false。错误发生在该提交及预算等值断言之后。真实原生DOM与截图显示中文、表情和转义的script字面文本，历史记录保留；[原件核验](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/continuation-02/browser-final-artifact-verification.json)通过，且没有新的浏览器/HTTP/PG动作。

**保留的验证限制：** 修正后的末尾CJS断言及新增workspace原始响应保存尚未在浏览器中重新执行；window全局变量探针未执行，当前证明为真实DOM字面显示且无注入script元素。原始总批仍FAIL。进程观察有真实fixture_ready/执行身份与as-run源码绑定，没有逐进程独立as-loaded模块内容hash；不补造该证据。Chromium由原夹具实际await context/browser.close并退出，未分别登记每个Chromium后代PID出生时间。上述限制须由集中独立审计评估，不能据报告措辞消去。

## 5. V01—V20及H1—H4有限映射

| 项 | 最终有限证据与限制 |
|---|---|
| V01 | 目标两版、首次goal_version=0约束、冻结/CAS和正常HTTP/UI已验；G7 seed全部代表组合未新跑，未变旧能力只按原证据复用。 |
| V02 | 图/前置/未知引用/权威字段纯拒绝及真实path proposal/accept/node selection；旧proposal不能激活当前目标的合同检查。 |
| V03 | 计算、概念、程序三题及复测实例实际UI/PG；未露参考被抑制，引用及目录hash真实回查。 |
| V04 | S1分钟换算与单位、S2原子性/隔离证据、S3正数计数/return位置的给定确定参考核对；部分正确、错误/gap/hypothesis分列。仅合成transport，不证明真实生成质量。 |
| V05 | 零费保存与评价分离，预算尽保存、UNKNOWN/失败仍保留答案、真实提交丢响应后恢复。 |
| V06 | 辅助与两个不同未露独立实例、只一个实例不前进、理由与head/重开；无永久mastered。 |
| V07 | 真实纠错/相反反馈争议不推进、旧事实不改；零费UI用户补充显示及实际收据。完整记忆删除不在本次范围。 |
| V08 | 真实同父并发同文一个效果、异文一个胜者；HTTP同键异文409，Windows同键不新增SUP/Q，ALREADY_PRESENT零写。 |
| V09 | claimed无operation不重发、UNKNOWN占槽、原SUP未知、真实提交后丢响应与只读核对；放弃只改本机显示。 |
| V10 | 目标/答案在途改变后旧007/反馈/exposure仅历史、applied_revision为空、无progress；mark前当前绑定拒绝。 |
| V11 | 来源版本在途失效遵原G3拒新正文、UNKNOWN且用户答保留；实际引用位置/hash与显示禁用。未新验所有PDF/物理删除组合。 |
| V12 | 原SUP/worker/Job实际教学取消和85秒硬停止，树零，保守时间账与旧关门主体保持。 |
| V13 | 原finite_calculate一次真实工具/Q-C-T-R-S隔离，T1；模型窗口独立Q/C，无用户代码执行。配置/输出越界纯检查。 |
| V14 | 严格字段/UTF-8/边界/输出与真实合法规范正文；原生末屏HTML按字面显示。独立window全局探针未到达。 |
| V15 | 实际原生IDB失败、跨标签容量零POST、恢复及真实同键只读核对；最终末屏由原件核验补证，修后整脚本未重启。 |
| V16 | UNKNOWN单快照33次/不重叠/截止停、hidden/unmount、迟到读取保护输入与焦点。未对每种goal/exercise/citation组合另跑笛卡尔矩阵。 |
| V17 | 四读面恰一条业务CTE、真实JSONB/游标漂移409、局部坏项抑制、重开与历史正文。 |
| V18 | 最终009六类反例及非空model/tool/unknown/无正文保留、ACL与immutable；旧plain/G7正常完整业务没有新跑，主体复用不能冒称新回归。 |
| V19 | 确定合成参考可核；真实provider/12请求质量层not_run，未授权。 |
| V20 | 有限控制、原始失败/计数/收尾、最终差异及字节绑定已交付；独立审计not_run，逐进程as-loaded/Chromium子PID限制见上，不自签。 |

H1由8模型+1有限工具真实主链、另4模型三题型与保存重开构成；H2由真实并发/同键/ALREADY_PRESENT和浏览器提交丢响应组成；H3由四种实际在途屏障/迟到及显示控制组成；H4由预算尽零费保存、UNKNOWN、无效输出/显式retry、取消与硬停止组成。各层相互引用，不把显示替身移植为PG或Job通过。

## 6. 旧新投入、追加授权和收尾

原卡新增上限为入口3/start3/app3/SUP24/browser2/driver3/build1，主动6小时、离线1800秒、真实3600秒、收尾480秒。用户2026-10-05先明确追加入口与start各2及主动3小时，其余不变；再批准仅1次browser；第五次预检拒绝后又批准仅1次real entry。各原文、批准前账副本与严格条件见三份supplementary-permit证据；没有退款、借旧许可或清零。

最终次数：real entry **6/6**、精确container start **5/5**、app **3/3**、SUP.create进入 **21/24**、browser **3/3**、driver **3/3**、build **1/1**。实际秒数与最终主动checkpoint见[attempt-ledger.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/continuation-02/attempt-ledger.json)。主动新增段从2026-10-05T03:33:03.647264Z保守计，原段9877.438016秒及旧未精确尾段缺口保留；隔夜等待未冒充新增主动业务，也不抹去旧投入。

初轮至少9入口、至少1次容器start、漏5.940秒与部分未知投入保留；续作01入口4/start1/app1/build2、离线14.880/真实17.910/收尾0.890秒保留。旧blocked汇总exit0和缺原始日志的41项离线声明不作为通过，旧009字节不升级为当前迁移证明。

末入口cleanup通过：停止确认自有应用树、精确同一容器，Running=false/Pid=0，55442与18100关闭；第四批42个已观察自有PID不存在、21个命名Job返回ERROR_FILE_NOT_FOUND，全部原件保留。两库retrolume_task100_g8_main/fault、admin/app/denied、六个固定schema、合成资料/事实及唯一卷保留；没有DELETE/DROP/TRUNCATE/容器卷删除或代结算。

最终再次只读核对同一容器、端口、54个已登记进程身份及21个命名Job：[资源终检](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/continuation-02/final-read-only-resource-check-20261005.json)通过。53个PID不存在，1个PID已被无关进程复用且创建时间不同，没有干预该无关进程；21个Job均不存在，容器仍停止、两端口关闭。该检查单独计收尾时间，没有业务连接或资源变更。

## 7. 回传与待同步

最终产品/009/夹具及完整有效证据已保存，单批FAIL与逐项合并证据分列。无需真实密钥、用户库许可、下载、删除或重跑已验主链。修后浏览器整脚本未运行及as-loaded/Chromium身份粒度限制已单列，若独立审计裁定需要补验，必须依据剩余资源上限另给有限许可，不能暗开第七入口。

共享DocuS、正式DEF/CHG及G8裁定由编排串行维护；本报告只提供待同步的事实：任务100实现/有限主链与控制证据、全部六入口失败和追加账、上述未验证粒度及一次集中独立审计需求。没有自发101/R095或独立放行。

下方初轮与续作01原字节为历史，当前结论以本节为准。先前续作02“尚未进入Windows/browser”的报告副本亦保留，不覆盖其时点事实。

---
# TASK-100 结果：G8 完整教学闭环实施与合成验证

- 任务卡：`DocuN/tasks/TASK-100.md`
- 角色：本卡业务实现执行者（不承担编排裁定与独立审计）
- 授权终点：G8 产品实现 + 卡内合成验证 + 普通修复 + 字节与原始证据冻结；交回等待一次完整成果集中独立审计
- 结论口径：**实现完成，验证部分完成**。离线层与迁移层已通过；仓储层在真实 PG 上定位并修复 2 个真实产品缺陷，但修复后的终验与后续真实分层因用户裁定停止真实验证而 `not_run`。

---

## 续作01 结果（G8 合同修复与剩余受控验证，2026-10-03）

一句话结论：**DEF-003—007 五缺陷全部修复完成且离线验证通过；真实入口 4/4 按预算用尽，主链真实验证（009 应用/PG 终验/HTTP）未完成——但此过程中新暴露的 5 组夹具/验证层缺陷已全部定界并修码（未复验），容器已限定启动并收尾停止，g8_main/g8_fault 两库已建立（owner=admin），三测试角色凭据已安全重置。**

### 续01-1. DEF 修复明细（全部完成，离线验证）

| DEF | 修复内容 | 离线验证 |
|---|---|---|
| DEF-003 不可变事实 | records 全表禁 UPDATE/DELETE（含 applied_revision/state_after），INSERT 即最终值无回填；pg_setup 授权 records 仅 SELECT/INSERT，列级 UPDATE 白名单限 heads/commands 状态机列 | py_compile 过；权限断言在 pg_setup grant 内置（leaked/records_writable 计数） |
| DEF-004 真实上下文与屏障 | `_freeze_model_context` 锁前组包 + `accept_teaching_command` 锁内逐项核对 reference_hashes（漂移抛 version_conflict）+ T-launch 当前绑定复核（obsolete 显式检查、head.pending 不匹配返回 no_longer_current_binding）；`_load_teaching_entities`/`_build_profile`/`_stored_document` 全真实装配 | 离线单测 41 OK（含 recovery 4 反例） |
| DEF-005 只读面单语句快照 | `read_teaching_workspace` 重写为单条 CTE；view_token 用真实 source_identity_sha/command_state_sha hash（取消 "na" 占位）；source_invalid 真实计算；007 正文投影；坏单项局部抑制 → integrity_error；来源失效抑制派生正文但保留 goal/answer/correction 用户文字；前端 feedback 链改直接消费 workspace 区域 + toFeedbackView 映射 | WorkspaceProjectionOfflineTests + DtoOfflineTests 过；tsc --noEmit 过；真实 build ×2 成功 |
| DEF-006 runner 控制器 | 计账先于预检（blocked 也消耗入口）、损坏账 SystemExit(5)、timeout≠not_run、资源白名单（精确容器 ID/512MiB/1CPU/pids128）、真实 npm run build、新独立账本 attempt-ledger-continuation.json | 4 次真实入口全程记账（含 blocked/fail 如实记录） |
| DEF-007 恢复状态机 | finish_teaching_supervision 以确认后结局处理：definitely_not_admitted 仅认 `not receipt_present and state in (not_started,budget_exhausted,startup_deadline,partial_window_too_small)`；final_status=failed 才清 pending，unknown 占槽可恢复；"取消且无收据"不构成未准入证明 | SupervisionFactsOfflineTests 4 反例 + RecoveryPgTests 6 用例（PG 用例待真实验证） |

### 续01-2. 离线验证汇总

- py_compile：全部产品/测试/夹具文件通过（多次）
- 离线单测：contracts/policy/recovery-offline/api-offline 共 41 tests OK（skipped=8 为 PG 类按设计 skip）
- tsc --noEmit：通过；真实 `npm run build` ×2 成功（vite 33 modules，build 预算 2/2 已用尽）
- 断点核验：resume-check.json——86 项 hash 一致、3 项漂移均归属本窗口 DEF-003 修复（保留不回退）

### 续01-3. 真实验证账（入口 4/4 时间线）

| # | 场景 | 入口级结果 | 实际达成 |
|---|---|---|---|
| 1 | main-combo | blocked（identity_gate DSN 未注入） | 记账先行 ✓；暴露预检形态矛盾 |
| 2 | main-combo | pass（退出码 0，实际未达主链） | container-start 真实启动（pid=403，512MiB/1CPU/pids128）✓；super-resolve 打通 ✓；roles-prepare 因接线遗漏 blocked |
| 3 | main-combo | pass（同上） | roles-prepare 走到 SQL 层，暴露 ALTER ROLE 参数绑定限制 |
| 4 | main-combo | fail | **roles-prepare PASS（3 角色凭据内存重置）**；**databases-prepare PASS（g8_main/g8_fault 新建 owner=admin）**；migrate blocked（env_admin 丢 password）→ pg-repo 9 errors（空库连锁）→ pg-recovery 装载错（类名）→ fault 场景静默切库失败 → http 403（会话 token） |

资源与预算终态：real_entries **4/4 尽**、container_starts 1/3、app_starts 1/3、frontend_build 2/2、browser 0/2、driver 0/3、sup_creates 0/24；offline 14.88s、real 17.91s、cleanup 0.89s。注：#2/#3 入口级 result="pass" 系进程退出码语义（blocked 子段不计 fail），子段真相以 attempts[].source_identity 同批 runtime log 与 segments 明细为准。

### 续01-4. 新暴露缺陷定界与修码（全部已修，均未复验——无剩余入口）

1. **入口预检与合并形态矛盾**：main-combo 自带准备链但预检要求入口前注入 app 口令 DSN（口令入口内才生成）→ main-combo 预检延后到子段硬核
2. **角色凭据死锁**：runner 曾对已存在角色自行加"不重置"禁令（卡面 65 行无此明文，"不可重置"仅见于 launch 保护/预算条款）→ 改为 ALTER ROLE 设新内存口令（token_urlsafe 字面量内插，注入风险为零）
3. **migrate env_admin 丢 password**：rsplit(' ',1) 剥段后拼 dbname 导致 fe_sendauth → 改全量构造 + admin_password 入 state
4. **RecoveryPgTests 类名**：runner 两处写 PgTests → 改正
5. **fault DSN 双格式**：ensure_fault_database 的 rpartition("/") 仅适用 URL 格式，key-value 注入静默切库失败 → _switch_dbname 双格式兼容
6. **HTTP 会话 token**：403 实为 local_session 校验（非配置缺失；activity.example.json 本为占位无效模板）→ HttpTests setUp 经免 token 的 GET /api/session 取 token，请求带 X-RetroLume-Session 头

**未复验声明**：上述修码后 py_compile 全过，但 009 应用、pg-repo/pg-recovery 终验、fault 六场景、HTTP 主链、Windows 17 窗、浏览器一会话全部 `not_run`——真实入口预算用尽，属合同停止条件（任一投入上限到达即停）。**离线通过不冒充真实通过**。

### 续01-5. 资源终态与待续

- 容器：cleanup PASS，running=False pid=0（证据 runtime/cleanup-20261003T065720Z.log）
- 持久合成资源（保留）：retrolume_task100_g8_main / retrolume_task100_g8_fault（owner=admin，两库为空库待 009）；retrolume_task100_admin/app/denied 角色存在（口令已重置，仅历次运行内存持有，未落盘）
- 待续窗口第一步：重新授权真实入口后直接 `runner.py main-combo`——本次修码已就位，预期链路：角色已存在走重置分支 → 两库已存在走 preserved 分支 → 009 首次应用 → PG 终验 → fault 场景 → HTTP（token bootstrap 已修）
- 台账：`attempt-ledger-continuation.json`（7 attempts、6 corrections、只追加）；runtime 日志 7 份

### 续01-6. 续作01 证据索引

- 账本：`DocuN/evidence/TASK-100/continuation-01/attempt-ledger-continuation.json`
- 断点核验：`DocuN/evidence/TASK-100/continuation-01/resume-check.json`
- 运行日志：`DocuN/evidence/TASK-100/continuation-01/runtime/`（frontend-build ×2、main-combo ×4、cleanup ×1）

---

## 一、结论

| 项 | 状态 | 依据 |
|---|---|---|
| G8 教学闭环产品实现（后端 7 模块 + 009 迁移 + 接线 + 前端 7 件） | **完成** | `DocuN/evidence/TASK-100/final-file-identity.json`（34 文件，582056 字节） |
| 离线合同层 + 策略层 | **通过 20/20** | `runtime/offline-20261003T042953Z.log` |
| 009 迁移真实 PG 六场景 | **通过 11/11** | `batch-PG-M-migration.json` |
| 教学账本真实 PG 用例 | **部分通过 8/9**，定位并修复 2 个真实缺陷后**终验 not_run** | `runtime/pg-repo-20261003T041438Z.log`、`attempt-ledger.json` |
| HTTP 主链 / Windows 组合 / 浏览器一会话 / 前端 build | **not_run** | 用户 2026-10-03 裁定停止真实验证 |

**不签**：G8 最终验收、真实 provider 教学质量、STEP009—012、M-1、整个项目通过。

---

## 二、交付物（A—D）

### A. 后端教学域（新）
- `app/learning/teaching_contracts.py` — Strict DTO、canonical/request_sha256、semantic_slot、命令回执、低信任输出联合
- `app/learning/teaching_policy.py` — 阶段转移、路径 DAG、支持性检查、进度推导、公开投影、view_token
- `app/learning/teaching_service.py` — `submit_command` 分流、模型/工具两阶段提交
- `app/learning/teaching_api.py` — 命令 POST/GET、工作区、历史、记录读
- `app/learning/teaching_adapter.py` — 请求身份/目录来源复核
- `app/learning/teaching_prompt.py` — plan/exercise/evaluate 三固定 system prompt
- `app/learning/teaching_evidence.py` — 有限目录装配（top_k=4）
- `app/activities/teaching_repository.py` — 三表账本 Mixin（`TeachingLedgerMethods`）
- `migrations/009_teaching.sql` — 三表 + 索引 + FK + 不可变/身份守卫触发器 + `REVOKE ALL`

### B. 现有文件接线（改）
`activities/repository.py`（5 处教学钩子）、`capabilities/contracts.py`、`capabilities/gateway.py`、`service_config.py`、`main.py`、`activities/service.py`、`learning/service.py`（拒绝教学前缀绕过）、`activities/api.py`（教学操作只回元数据）

### C. 前端（新 7 + 改 1）
`teachingApi.ts`、`teachingIntents.ts`（localStorage 台账 + IndexedDB 草稿）、`teachingDrafts.ts`、`teachingIntentMatch.ts`、`TeachingExercise.tsx`、`TeachingFeedback.tsx`、`TeachingWorkspace.tsx`；`ActivityWorkspace.tsx` 挂载

### D. 测试与夹具
`tests/test_teaching_contracts.py`（9）、`test_teaching_policy.py`（11）、`test_teaching_repository.py`（9）；`tests/fixtures/task100/`：`support.py`（保留式夹具）、`pg_setup.py`、`pg_migration_scenarios.py`、`runner.py`（唯一真实入口 + 预算台账）、`diag_capture_local.py`、`diag_teaching_pg.py`

---

## 三、O01—O11 与验证映射

| 命令 | 产品实现 | 验证状态 |
|---|---|---|
| O01 goal | `apply_teaching_local` + `_teaching_apply_local_effects` | 真实 PG 通过（原子写 command/head/record） |
| O02 plan | `accept_teaching_command` + 冻结上下文 | 合同层通过；真实模型链 not_run |
| O03 accept_path | 本地 | 身份门通过（`record_not_found`）；阶段门 not_run |
| O04 exercise | `accept`+`claim`+`run_one_call`+`finish` | 合同层通过；真实链 not_run |
| O05 expose | 本地 | 合同/投影层通过（未暴露不返回参考） |
| O06 answer | 本地 | 合同层通过 |
| O07 calculate | G5 `execute_tool_action` | 合同层通过；真实工具链 not_run |
| O08 evaluate | 模型 + progress/head 同事务 | 策略层通过（两次独立观察、无 mastered） |
| O09 correct | 本地 | 合同层通过 |
| O10 abandon | 本地 | 未单独实跑 |
| O11 select_node | 本地 | 合同层通过 |

---

## 四、本卡发现并修复的真实产品缺陷（5 项）

全部为产品缺陷，非测试期望偏差（除第 5 项）：

1. **阶段门对未知动作静默放行** — `validate_transition` 用 `_ACTION_PHASES.get()`，未知动作落到 `None` 分支被当作"无限制"通过，可绕开阶段约束。改为先校验 `ALL_ACTIONS` 封闭集合。
2. **非有限数值被误报 conflict** — `Decimal("NaN")` 不抛 `InvalidOperation`，`NaN != NaN` 使合法解析路径产出 conflict。conflict 参与推进裁决，不能由非法数值伪造。改为显式 `is_finite()` 门，一律 `unchecked`。
3. **进度推导两处错判** — ①`all(...)` 带 `if dim in observations` 过滤，缺失必需维度时因空集真而判"满足"；②独立观察未按 `answer_record_id` 去重，同一作答重复计入。改为逐维命中 + `len(set(...))`。
4. **不可变触发器误拦同事务投影回填** — `teaching_records_immutable` 禁止一切 UPDATE，但仓储必须在同事务回填 `applied_revision`/`state_after`（099 的保留/修补/前进裁决）。结果是**任何本地命令都失败**。改为只保护身份/正文/来源/创建时点，DELETE 一律禁止。
5. **head 指针哨兵被当 UUID 传** — `_teaching_update_head` 只对 `node_id` 特判 `"__clear__"`，UUID 列（`path_record_id` 等）未处理，PostgreSQL 报 `22P02 invalid input syntax for type uuid`。**第二版目标必然失败**。改为统一哨兵常量，NULL 化对所有列一致生效。

第 5 项修复后 `py_compile` 通过，但**终验 not_run**。

另修正 1 项测试期望偏差（非有限数值应判 `unchecked` 而非空列表），以及 4 项错误码/返回结构期望写错。

---

## 五、009 迁移真实 PG 场景（11/11 通过）

| 场景 | 结果 | 关键事实 |
|---|---|---|
| M01 非空升级 | PASS | 三表建成；`activities 1→1`、`teaching_heads=0`，零回填旧行 |
| M02 重复执行 | PASS | 整体回滚，无多余对象 |
| M03 缺 008 前置 | PASS | 拒；`teaching_tables=0`，无半状态 |
| M04 008 约束被删 | PASS | 拒（不只比表名）；无半状态 |
| M05 事务中途失败 | PASS | `1/0` 注入后三表与两触发器全不存在 |
| M06 权限不足 | PASS | denied 角色对教学三表 3/3 真实拒绝 |

修正后的迁移重建了主库（`retrolume_task100_main`，DROP WITH FORCE + OWNER=admin）。

---

## 六、资源账

| 项 | 上限 | 实际 |
|---|---|---|
| 真实入口 | 6 | **6（耗尽）** |
| 容器启动 | 4 | 1（`retrolume-task-100-g8-pg1`，Up） |
| 应用启动 | 6 | 0 |
| SUP 创建函数进入 | 32 | 0 |
| 浏览器 | 3 | 0 |
| driver | 4 | 0 |
| 前端 build | 3 | 0 |
| 真实秒 | 5400 | 51.23 |
| 离线秒 | 2400 | 0.75 |

台账：`DocuN/evidence/TASK-100/attempt-ledger.json`

预算调整（均经用户裁定，记录在 `adjustments`）：
- 041121Z 运行改记 `not_run` 并释放 1 次入口（沙箱阻止在证据目录内写 `OriginalStore` `.incoming-*` 临时文件，属环境限制）
- 最终裁定：停止真实分层验证，不再释放预算

---

## 七、保留式夹具与数据保留

按用户指示，夹具已取消全部 DELETE：只核对专库身份并记录残留量。合成数据与失败证据保留在 `retrolume_task100_main` 及证据目录内，清理权归编排。原件暂存目录已移出证据目录（`%TEMP%/retrolume-task100-originals`），避免与证据冻结冲突。

专库身份核对：库 `retrolume_task100_main`、角色 `retrolume_task100_app`，runner 在每个真实场景前硬核对，不符即 `not_run`。

---

## 八、未验证 / 风险 / 偏差

### 未验证（not_run）
1. `pg-repo` 终验（哨兵修复后）——**最高优先级**：缺陷 5 的修复未在真实 PG 上确认
2. HTTP 主链（O02/O04/O07/O08 的真实请求-响应）
3. Windows 组合八窗口、晚到/UNKNOWN/硬停
4. 浏览器一会话（草稿→摘要→POST 顺序、轮询上限、context_key 迟到保护）
5. 前端 `npm run build` 与 served bundle 身份
6. 缺陷 4 的修复仅在重建库后由 M01—M06 覆盖，**未由真实命令写入路径回归验证**

### 风险
- 缺陷 4/5 同属"迁移约束与仓储实现不一致"，可能还有第三处未被发现；建议独立审计优先复跑 `pg-repo` 终验
- `teaching_records_immutable` 现允许投影列回填，需确认 `applied_revision`/`state_after` 不会被用于改写事实语义
- 前端 7 件从未经浏览器实跑，IndexedDB/localStorage 容量与顺序保证仅有静态保证

### 偏差
- 预算口径：卡面"真实入口 ≤6"在实现过程中被早期未走 runner 的直接执行消耗，runner 建立后无法追溯校正，故最终真实分层未执行
- 原件目录从证据目录移出，属对沙箱限制的适配，已在夹具注释与本文件记录

---

## 九、证据目录

`DocuN/evidence/TASK-100/`
- `input-snapshot.json` — 56 必要输入身份（前置）
- `batch-B1-offline.json` — 离线批次与 4 项修正
- `batch-PG-M-migration.json` — 迁移 11 场景
- `attempt-ledger.json` — 预算台账、逐次尝试、源码身份、调整记录
- `final-file-identity.json` — 34 文件最终字节身份
- `runtime/` — 各次 as-run 日志与 `diag-local-error.json`（原始数据库错误）

---

## 十、给编排的建议

1. 独立审计**第一件事**：复跑 `pg-repo` 终验，确认缺陷 5 修复生效（需新批真实入口预算）
2. 缺陷 4/5 建议合并为一条设计一致性检查项：迁移层约束与仓储层写入模式必须逐条对账
3. HTTP/Windows/浏览器分层与前端 build 需在获得新预算后一次性排期
4. `DocuS/执行动态文档.MD` 需登记本卡结论与上述未验证项（本卡未代写）
