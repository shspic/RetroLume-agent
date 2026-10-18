# TASK-115 / R-109 — review-02 F02/F03增量独立终审

## 目标与交付

你继续原TASK115独立审计窗口，只对TASK114续作03的DEF035/F02、DEF036/F03修复、相关证据和实际传播完成一次增量终审。不是四项全重审、不是新实现或新验证卡。主控已关闭F01/DEF034和F04/DEF037，其未变机制与原有效证据直接继承；本次改动产生的具体回归仍须指出，不凭“已关闭”排除真实影响。

输出两项是否具备关闭条件，以及代码、证据、执行控制三个独立判定和有限STEP017建议。结果置顶保存 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-115-result.md，当前61253字节原报告作为原字节后缀保留。新证据只写 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/review-02/。不填主控最终验收，不宣完整NFR005恢复后继续、STEP018—020、M-1、项目或发布通过。

本轮产品运行新增0。以实际差异、原始方法、版本绑定和原审查完成判断，充分即收口。真正原Must尚缺的，给具体阻碍、已有什么/缺什么及最小修复或补证；不自行运行或修复，不把非阻断观察升级为额外门，也不要求完整主链重新全绿。

## 项目、规则、窗口与授权

根 D:/shspic/project_NO3_RetroLume-agent，入口 D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。唯一task_model，V4.0、公共AGENTS CHG-0003，阶段07；需求v1.2、架构v1.31、执行动态v2.55。公共根 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，公共DocuS/AGENTS.MD及WORK适用2/6/8章继续生效。七指纹在项目DocuN/evidence/v4-migration-20260930/rules-snapshot.json，同窗未变正文复用，后来的源版本不自动采用。

TASK115/R109/review-02/STEP017，父TASK114/R108续作03，关联TASK113/R107、STEP017-P1、MOD008/FLOW007/API005、DR001—003、NFR002/003/005、SEC001/002、DEF035/036。原采用包、用户原始需求和永久只读边界不变。原始需求用户维护，只读。

接收A+增强独立审计Agent，继续原TASK115窗口，上一轮实际Codex desktop/系统GPT-6，当前身份如实登记。此窗未参与113/114工程或修正，原暴露主控摘要的披露继续保留；不能由原114窗换标签审自己。人工转卡，当前本轮已登记待转交，不冒派发或接收；不派子Agent，不并行写产品。原114已封存，不得自修。

授权是用户已采用STEP017-P1并持续要求完成，及稳定双修后原必需独审的接续。原115初轮与review-01的结论、FAIL、投入和独立性继续有效；不重置TASK/R或假称全新审计。仅两个余项及真实传播需要增强执行，不另向用户重批方案。

不读TASK114-result.md及pre中的工程自评、实现完整聊天/思考或记忆中的工程结论。只读目标、验收、实际源码/差异、原始方法及输出。自己的原115报告和自产证据允许复用；先形成当前增量判断再续写历史。意外暴露要说明时间、范围、先后，不能伪称绝对未接触。主控已核身份只作输入定位，不代产品通过。

## 前置与最小充分输入

1. 本卡、根入口/锁定规则和 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-115-work-decision.md 的本轮许可。正式架构和执行动态只取版本/授权及适用条款，不把候选摘要当独立证据。
2. 原采用完整合同 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-113/design/revision-01/current-contract.md，81813字节，SHA256 8a56ebf3c1715895e3ee7a0dcf1f621b591335400e9898aa00df8cb2b7a61aaa。未变同窗正文复用，不通读重审其余阶段。
3. 工程本轮目标/许可 D:/shspic/project_NO3_RetroLume-agent/DocuN/tasks/TASK-114.md，20398字节，c40644b07a3b3556edd5082e3d48a1af0e6146b4c655763d994b1a65647fcaa8。原115 review-01报告当前61253字节/3d6a4ce4e30284f6799f61462e84c419a9fdd7226ef1f1e73dc468815b04a0f2；原发现和方法在 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/review-01/，只补F02/F03及对应继承原件。
4. 中性输入 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/orchestration-review02-20261014/input-manifest.json，含当前243文件/三已移除输出、final/pre、实际方法、原始证据和控制身份。先核实际hash，漂移停止相关审查，不对旧快照发当前通过。
5. 本轮原始证据基址 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-03。读final/manifest.json、final/source、final/diff、final/method-index.json、final/failures.json、final/inheritance.json、final/delivery.json，pre/as-run/methods/offline/batches、accepted和observations中的必要原件。pre内源码按项目相对路径，旧报告为pre/TASK-114-result.md，旧执行账为pre/receipt.json与pre/events.jsonl，不沿C02布局猜路径，不读旧报告自评。
6. 源码实际增量只有backend/app/data_exit/reference.py、restore.py和frontend/src/data/DataWorkspace.tsx。必要直接依赖包括operations.py受限connection/BoundedConnection、原OriginalStore/RootLease、context/dataApi/Plan/ReadonlyRecords/main的调用契约；未变部分做身份/传播分析，不全仓重审。测试为backend/tests/test_data_exit_c03.py、backend/tests/fixtures/task114/c03系列、frontend/tests/task114-c03-inputs.mjs。
7. 旧唯一执行账 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/control/receipt.json、events.jsonl及本轮final/delivery。C03只新增两次Browser及controller，精确PID/birth关闭原件在两个batches和final/delivery。旧九PG对象Stopped按已有精确原件继承，本轮无Docker/SQL/监听，不能伪称今天现场重新核查。

已实际回传稳定候选；当前冻结，不存在并行写或待回的工程消费者。final登记246项，其中243实际存在，index-NDc3grUN.js本轮构建移除，index-CJ8Yp7JQ.js和index-DcQS7jxH.js更早已缺失。不得恢复旧输出或把三个缺失项当新产品缺陷。

最终关键SHA256如下，完整清单优先。

- reference.py为0b0f671c7760ded575816461732b105022172defad6e0952c3490f4452d3e163。
- restore.py为3536262ef399790eb1f3d968cd8a1f712ce6828bcad430ad6c347d87159248c6。
- DataWorkspace.tsx为878b2ef365e704b01432e6d1d934034d2e7e2ce3c506577dfa682415491fd3da。
- 最终bundle index-DZduJTtr.js为9c9a3c69659371fac708d3ace004aca67b67f789a2b4a3725da1bf5c3cf60181，index.html为df38c0f0ca2630dfbe678d23aca7884c9063a0b9f7c0f80e5bfcc68a607a9f63。
- operations.py仍b57348ca484717a2c147087c46c6edc4702983a900f65ce5475e00346f64a876，context.tsx仍fdf86fb80f394fb59becae1a86deabf4bd15179d4eb4f7fcc3635a17d4e908f9，dataApi.ts仍d6865057747dab1604c9d22f3a623d95f8b7e3af577e17ded31cd305c360e679。

## 必答A — F02同一截止的原件pin传播

对照你在review-01定位的restore._load→LoadingReferencePin→独立固定3秒连接漏洞，检查当前必需operation参数、唯一产品构造点operation=operation、hub/job/target同一性、进入连接前后和fetch/COMMIT返回后资格检查。连接/查询限制必须真正复用原Operation，不是重新计D、额外可选None放行或仅包装名称。

对实际代码逐分支核身份、lease/root/prepared、allocated/running与临时loader条件。未知身份或D外结果不能进入原件store.put或授verified；普通ReferencePin的ticket/epoch与source权限不能回归。operations核心未改不等所有调用已正确，当前pin与_load的真实传播仍独立对照。

读offline/cases/loading-pin-1207676843000000中的01-same-operation.json、02-no-connect.json、03-actual-load.json及相应方法/测试。检查实际LoadingReferencePin、Operation、BoundedConnection、_load/PackageRows/RootLease/OriginalStore均参与，替身只在原始psycopg连接边界与明确阶段推进。若替换掉被测核心，必须指出，不能凭方法名通过。

已记录三组方法为正常同operation/剩余2.8秒、connect_timeout2、options/语句前2800到2550ms；不足0.75秒/过D/错误lease或operation不连；connect/query/fetch/COMMIT返回分别D外、错误instance/not_loading在打开原件stream前拒绝。正常子路径止于fixture_stop_after_original，不冒完整restore/seal或真实PG。

受控参数/传参/执行资格检查是本轮工程卡和原审计明确选择的验证方法，评估其对该B级漏洞的充分性。不要因没有新增物理PG就自动创造新硬门；若受控方法实际遗漏关键可达分支，给具体缺口。驱动强制终止、内核挂死和PG等待上界未新验证，保留边界，不能反向签为通过。

旧PG两秒样本只到reading后failed，未到设计的2.1秒publication注入。沿review-01更正：仅继承真实读取过D/无发布，独立文件后段方法另按其受控层成立。此次不要求重跑capture后真实PG，也不以旧过强表述判本轮未完成。

## 必答B — F03策略、文件、计划、范围与动作绑定

独立检查当前InputBinding在restore/scope输入revision与dataset lifetime上的作用：mode、source_ids/activity_ids、file、deletion_policy、snapshot确认、当前plan及其verify/activate的每一可达提交点。变化清空UI不等旧请求失效；await后的回填和动作前校验都要看。

重点是原可达反例。snapshot_only确认后上传或计划等待期间改为respect_current，旧响应不能恢复当前可执行计划；当前选择与plan.deletion_policy/plan_id/hash必须一致。文件hash、上传已发生的事实或已verified旧job可以保留核对，不能回填为新输入的执行资格，也不能自动重POST/重上传/激活。

scope-preview要绑定材料和活动集合及mode，A迟到不能成为B闭包、启用确认或携A closure_sha导出。原后端expected_closure_sha256防线和显式确认保留。refresh读取历史、同上下文换文件、verify回包、卸载/重挂或可信上下文推进不能绕过绑定。已关闭的全局CAP反序和正文资格未变机制直接继承，只分析DataWorkspace改动的实际传播。

呈现与动作共享planCurrent/planConfirmed/actionPlan等机制时，核真实依赖和ref/state更新先后，不仅看新增函数。保留正常新选择、snapshot与unknown原明确确认，以及只读历史可核对性；不能用一律禁用动作或丢弃全部历史伪造修复。

最终c03-browser-1210447187000000十二场景需要逐关键原子义项核充分性，合并覆盖不重跑。

- upload-pending-policy-change、plan-pending-policy-change，两个独立挂起点，不能以两次GET plan refresh替代。
- fresh-respect-positive、snapshot-unknown-positive，当前计划明确点击验证字段/次数正确，unknown未确认前不可验证；受控activate字段和main真实reload后不自动采用历史plan。
- refresh-plan-late-policy-change、same-context-file-replacement、verify-late-input-change，旧HTTP事实不重授当前资格。
- source-A-to-B、activity-A-to-B、mode-change，材料/活动两类范围与mode失效及B正向精确closure/request。
- unmount-plan-late、context-plan-late，重新进入/刷新或generation1变化后旧marker无效。

检查113请求时间线、held/released记录、实际控件动作、对应POST体、按钮/DOM/截图和当前bundle加载。正常文件选择本就显式触发upload/plan POST，不能把这些当自动业务重发；应核restore3/export2/activate1均对应各自明确动作，未经动作的新消费POST0。routes为合成DTO，不是完整后端Hub/selector；其中activate历史fallback的受控未知事实不参加当前资格，不能拿它签真实激活或凭该分层限制要求重做PG。

## 证据绑定、失败与有限传播

final/method-index有13方法，11离线/syntax/typecheck/build、2Browser。loading-pin-1207676843000000和第二次Browser是功能方法，核实际argv/cwd/start/end/exit/log/as-run、被测fixture/源/bundle与最终hash。syntax或构建通过不能单独支持功能；首次或早期脚本之后修改的false绑定必须保留，不能伪装全部最终方法通过。

第一次Browser c03-browser-1210213609000000在exact“删除处理”label定位失败，业务矩阵0项到达，7.954秒exit1。保留failure.json/stderr/as-run/准确close和首次缺失败DOM的事实。随后按真实label及main.onSelection=reload修夹具，未改产品/bundle；最终十二场景另批4.984秒exit0。判断修正是否针对真实夹具且未弱化正确断言，不能倒写首FAIL为PASS。

原C03bootstrap规则字段KeyError、Python路径/rg、stdout乱码误判及后续Unicode纠正均按原件保留；不把已承认观察错误当未披露规避，也不把它们升级成产品失败。首工具未同步mono、后实采QPC/UTC再保守扣300秒，内存等待连续计入，不签“完美计时”。

三产品文件之外的001—013、schema/codec/ACL、普通ReferencePin、F01取消/准入/completion、F04正文依赖、Native/worker/StopProof/preview、context/dataApi/ReadonlyRecords/main未改则按真实身份与传播继承。只在本轮确有影响时深入直接依赖，不能重做G11、原PG正常恢复、31域、两FK、两锁序/共享引用或整份29项表。原Must确切新回归仍为阻断，不因有限复核漏掉。

## 读写边界与预算

允许只读本卡输入、必要直接代码、diff、已有日志/JSON/DOM/截图/原件和既有预算。允许文件hash、有限AST/JSON/diff等纯元数据脚本，不import产品、不运行方法。只写review-02证据、自己的只读解析/结论与原115结果新前缀，原61253字节全文保为后缀；新证据不跨出项目或穿过保留junction。

禁止修改产品、tests/fixtures、dist、README、迁移/锁/用户配置、原114/115证据/控制账、原报告历史、DocuS/AGENTS/公共库、经验/记忆；禁止compile/unittest、产品导入、PG/SQL、Docker唤醒或任何变更、API/Vite/HTTP监听、Browser/Native/preview/build、Git写、安装、模型/provider/费用/公网、时间/服务/网络调整与删除。必要平台权限按实际处理，不用卡绕过审批；拒绝只停依赖部分并给原因。

新许可TASK-115-STEP017-REVIEW02-20261014，只读活动本轮最多5400秒，含首工具读取、hash/解析、普通等待、报告保存/复读，最后300用于落盘。首工具同时实采UTC/mono；漏点按实际披露并保守扣时，不倒填精确值或借换轮清零。

旧115活动累计8617.261566/21600，本轮全部加回，最大14017.261566，余额不自动继续；原日历硬截止2026-10-15T06:16:24.914938Z不延。原root3/API3/Browser2/offline125.610/保守hold14.874和所有FAIL仍在，本轮新增真实根/PG/SQL/Docker/API/Browser/compile/test/build/Native/preview/provider/费用/公网全部0。文件解析时间属于只读活动，不冒测试离线时间。正常无需再查现场资源，引用已存准确关闭原件，不因内存2GiB门阻塞只读审查。

原114累计root23/24、Browser7/9且C03门7已满、build6/7、PG create9/12/success9/9/start37/37、Windows11/12、API8/11、offline205.959/hold487.876、C03活动4495.4211376及C02+C03活动13684.1412486保留，不转移工程余额。原C01 9739.953、旧55525.796净unknown、G11/25/UNKNOWN/R60/count1/13元/626.566不清，不新签执行/退款权。

## 顺序、停止与回传

接收实采后核冻结与独立性，读取两项增量及关键原件，连续完成代码/证据/控制判断，给关闭或最小剩余缺口，充分即保存停止。已经判断的F01/F04和未变方法只引用，不耗时重新证明；读到确切阻断时先留证，其它不受阻阅读仍集中完成。

漂移、独立性不成立、关键资料缺失/越界、新高风险、原Must确切缺证、根因不稳或时长/日历门到达，停依赖部分并具体交回。不得自修、自开验证、分配共享TASK/DEF/CHG或要求无依据全量重跑。

报告先一句有限增量结论，然后F02/F03逐项根因/触发/当前定位与关闭依据或具体剩余、代码/证据/控制三轴、当前/批时身份、层级和继承、原失败/偏差与实际计时、必要人工/共享维护建议。区分确定缺陷、确切Must缺证、非阻断边界；不把受控PG参数检查写真实PG等待，不把routes写实际后台切换，不要求本卡未授权的新动态以凑“全绿”。

原115结果61253字节SHA256为3d6a4ce4e30284f6799f61462e84c419a9fdd7226ef1f1e73dc468815b04a0f2，先存本轮旧原件再置顶续写，旧报告及反例/失败原字节不动。确认完整可读后，只回一句真实结论和结果可点击绝对路径，供用户带回主控。人工仅转本完整卡和回传路径，无需密钥、释放内存或启容器；最终DEF/STEP/正式状态和CHG由主控裁定维护。
