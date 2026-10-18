# TASK-114 / R-108 续作03两项修复与定向补证结果

两项余缺已完成本卡范围内的修复和定向补证，稳定候选已形成，供原TASK115窗口仅对F02/F03及实际传播增量复核；本窗口不关闭DEF035/036，不签独审、STEP017、M-1或项目完成。主控已关闭的F01/F04原问题按未变字节和影响分析继承，不重开四项全审。

本轮产品差异只有LoadingReferencePin绑定同一Operation、restore._load唯一构造点传参，以及DataWorkspace的文件／删除策略／计划／范围输入生命周期。受控原始连接检查三组通过，最终dist真实Chromium十二场景通过，typecheck和一次build通过。未启动或操作PG、API、Vite、Native业务窗口、preview或真实selector，未安装依赖或触及真实资料。首轮Browser夹具失败及全部旧FAIL保留，实际新增Browser两次均已正常close并核准确PID/birth结束。

## 接收、许可与断点

项目根D:/shspic/project_NO3_RetroLume-agent，根AGENTS入口；task_model，V4.0／公共AGENTS CHG-0003，阶段07。卡面需求1.2、架构1.30、执行2.54。七锁定规则在接收和最终冻结时实核相符，适用公共AGENTS／WORK2/6/8正文复用或补读；公共库、原始需求、DocuS和主控DEF/CHG记录只读。

许可TASK-114-STEP017-C03-20261014，继续原工程窗，Codex desktop／系统GPT-6，具体后端子型号未披露，A+为资源标签。没有子Agent、并行修改、独立审计派发或自行组织新卡。

接收前237登记项实核，实际存在235文件，两个旧构建项缺失。原69598字节结果、旧receipt/events原字节和当前文件原件先保存到continuation-03/pre。新证据唯一根为D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-03，唯一计数仍是implementation/control/receipt.json及events.jsonl，不新建总进度账。旧C02结束段完整追加到continuation_history，不改原起点、旧资源、计数、失败和原事件前缀。

首工具没有同步mono。首次同步.NET QPC/UTC采样为2026-10-13T23:49:44.004654Z、1206845296862400ns，另保守扣300秒，本段从23:44:44.004654Z／1206545296862400ns计，不追认精确首点。读取、实现、普通等待、验证及落盘连续计时，未倒填暂停。接收后24小时与旧2026-10-15T08:54:00Z取较早者，本段日历门为2026-10-14T23:44:44.004654Z，原C02硬截止未延长。

前一断点因内存约1.70—1.79GiB没有启动Browser。用户释放后2026-10-14T00:45:28Z实采2456150016字节，约2.29GiB，当前字节／原报告身份／活根／剩余预算吻合，直接继续矩阵，没有重跑后台测试或build。该等待完整占本段；checkpoint-first-result.md、checkpoint.json、当时结果原件和观察更正均保留，最终结果替换本窗口自己的未完成前缀，仍保原C02全文69598字节后缀。

## F02 — loading pin消费原Operation的同一D

reference.py的LoadingReferencePin新增必需关键字operation，核operation.hub为factory.hub且job_id为target.job_id。进入专用身份查询前核Operation及准确lease/root、allocated/running、临时loader登记；专用连接从原Operation.connection创建。该机制已有的正整数connect_timeout、剩余statement_timeout／lock_timeout被实际消费，没有固定独立3秒连接，也没有新started、deadline或clock_domain。

身份查询结果fetch后、连接事务返回后再check；以后每次pin.check也先核同一Operation。身份未核定、结果消费时已过D或lease/prepared不匹配都不能授原件发布资格。restore._load唯一产品构造点在445行明确operation=operation；对backend/app的定向搜索没有其它真实产品构造点。普通ReferencePin AST不变，source普通权限和原ticket/epoch协议不改。

最终后端身份如下，完整原件及diff见final/source和final/diff。

1. reference.py的SHA256为0b0f671c7760ded575816461732b105022172defad6e0952c3490f4452d3e163。
2. restore.py为3536262ef399790eb1f3d968cd8a1f712ce6828bcad430ad6c347d87159248c6，仅该构造点的传参改变。
3. operations.py仍为b57348ca484717a2c147087c46c6edc4702983a900f65ce5475e00346f64a876，未突破冻结核心。

方法loading-pin-1207676843000000 exit0，外层2.735秒，unittest三项实际1.964秒，适用最终reference/restore/test字节。日志在offline同名文件，01—03原件在offline/cases/loading-pin-1207676843000000，真实argv、UTC/mono和方法环境在methods及final/method-index.json。

1. 01-same-operation.json调用实际LoadingReferencePin、Operation、BoundedConnection及lease。受控剩余2.8秒产生connect_timeout2、连接启动options的statement/lock2800ms；原始connect替身推进0.25秒后，实际查询前SET LOCAL均为2550ms。pin持有原Operation对象，execution前后started/deadline/clock_domain相同。root/prepared错误拒绝，后续pin检查过D也拒绝。
2. 02-no-connect.json覆盖剩余0.75秒、已过D、exclusive、wrong_operation、wrong_root、not_allocated，均未调用原始connect。没有以0超时表示无限等待。
3. 03-actual-load.json通过实际_load／PackageRows／RootLease／pin／Operation／OriginalStore。connect、query、fetch和COMMIT返回分别受控推进至D外，或者wrong_instance／not_loading，全部在打开原件stream前拒绝，无incoming、无发布、无verified。正常原件子路径实际发布合成原件，随后在operation-history入口明确fixture_stop_after_original。合成rowset仅支持此子路径，不模拟完整restore／seal／verified。

这些方法只在psycopg原始connect边界返回合成身份并记录参数／语句；没有替换被测pin、Operation或_load。受控monotonic_ns推进不改系统／数据库时钟。正常连接与所有时限点的原started_ns=10000000000、deadline_ns=12800000000及该测试进程clock_domain均按各case原件保存，不冒真实PG计时。

结论为同D传播、参数和返回后执行资格拒绝的受控边界通过。物理PG等待上界、驱动强制终止、内核挂死或新正常完整恢复主链均未新增验证，本卡明确不要求它们。

## F03 — 删除策略、计划及范围输入绑定

只改DataWorkspace.tsx，SHA256为878b2ef365e704b01432e6d1d934034d2e7e2ce3c506577dfa682415491fd3da。context.tsx/dataApi.ts无需改动，分别保持fdf86fb80f394fb59becae1a86deabf4bd15179d4eb4f7fcc3635a17d4e908f9、d6865057747dab1604c9d22f3a623d95f8b7e3af577e17ded31cd305c360e679。

restore和scope共用必要的InputBinding机制，含输入revision和既有dataset lifetime。相关onChange同步推进ref并清空当前计划／恢复资格或范围预览；每个具有当前执行资格的await返回后再核绑定。文件、policy、计划与验证结果属于restore输入；mode、source_ids、activity_ids属于scope输入，卸载／数据身份变化使两类绑定同时失效。

上传hash完成后才允许上传；收到原上传事实后，若绑定仍有效才请求该policy计划；计划返回后核绑定和deletion_policy再安装。旧HTTP事实和rememberJob业务键保留只读核对，但不重新获得当前计划资格，不自动重POST、重上传、建立restore job或激活。

呈现和动作使用相同planCurrent／planConfirmed条件及actionPlan校验，当前policy必须等于plan.deletion_policy。snapshot_only明确确认和unknown删除确认保留。verify核plan_id/hash、确认字段和返回plan_id；activate核当前绑定、已verified且同plan的restore job、hash及selection_generation。撤回snapshot确认立即失效当前绑定。

refresh仅能更新当前显式取得的计划、相同plan_id／plan_sha256／package_root_sha256及对应恢复任务，返回时再核输入和当前ref；历史jobs继续展示事实，不自动采用旧计划。原按钮额外捕获旧restoreJob再GET回填的闭包去除。scope预览绑定当前mode及两类选择，点击导出前再核绑定／closure_sha，原expected_closure_sha256后端防线保留。处理期间file本来disabled，夹具先断言真实enabled才选择文件，未强制绕过disabled；policy及材料／活动选择可在挂起期间正常改变，revision负责废弃晚到结果。

## 最终bundle的精确矩阵

现有npm run build一次，frontend-build-1207705703000000 exit0，7.578秒，包含现有typecheck；之前单独typecheck exit0，21.985秒。原有dynamic-import／large-chunk警告仍保留，依赖、锁文件和配置不改，没有额外递归清理。

构建自产index-DZduJTtr.js，SHA256为9c9a3c69659371fac708d3ace004aca67b67f789a2b4a3725da1bf5c3cf60181。index.html为df38c0f0ca2630dfbe678d23aca7884c9063a0b9f7c0f80e5bfcc68a607a9f63。旧index-NDc3grUN.js改前原字节在pre，构建实际移除；更旧index-CJ8Yp7JQ.js／index-DcQS7jxH.js仍缺失，不构造当前hash。CSS／PDFworker未变。

最终方法c03-browser-1210447187000000 exit0，4.984秒，实用本项目最终dist、已安装Playwright／Chromium、全新独立profile。所有应用请求由明确127.0.0.1:18114合成URL的routes处理，没有TCP监听、API、Vite或PG；未知URL失败关闭，非白名单请求和pageerror均0。静态资产按当前dist实际读，finalIdentity与as-run/final逐hash一致。Plan回应包含实际DTO的plan_id、deletion_policy、plan_sha256、package_root_sha256、latest_status、overlay_count、executor_configured、permanent_readonly。

以下十二场景的marker、请求体、接收顺序、按钮状态、DOM和截图保存在batches/c03-browser-1210447187000000/result.json及01—06文件。

1. upload-pending-policy-change。snapshot_only先明确确认，上传挂起时改respect_current，旧上传事实返回后不再POST旧policy计划，restore-jobs为0。
2. plan-pending-policy-change。snapshot_only的restore-plan挂起时改respect_current，旧删除覆盖7199回包不显示，不出现可验证计划，不发restore-jobs。
3. fresh-respect-positive。明确选择新文件并取得respect_current计划，覆盖31可验证；点击一次只发送对应plan_id/hash、confirm和acknowledge_unknown_deletions=false，未自动验证。
4. refresh-plan-late-policy-change。对当前已取得并验证的计划，真实挂起GET restore-plans；改变policy后旧GET不回填，snapshot确认重新要求。此项补充刷新入口，不替代前两项上传中改变策略的反例。
5. snapshot-unknown-positive。snapshot确认后选择文件，unknown计划覆盖41，未确认unknown时verify disabled，明确确认后只发送对应plan一次、acknowledge_unknown_deletions=true。显式一次activate携原plan hash、generation0、confirm=true。真实main.onSelection引发window.location.reload，夹具跟随重载再进入工作区，旧历史plan不自动取得资格。该受控activate响应只证UI动作字段／重载，不证真实selector。
6. same-context-file-replacement。先有覆盖51的计划，处理settled后更换文件，原计划立即失效；新上传挂起时没有旧verify/activate，file真实disabled。新计划覆盖52后才可验证，没有自动restore POST。
7. verify-late-input-change。用户合法点击一次verify后返回挂起，改变policy使绑定失效；旧verified事实不成为当前activate资格，原业务键仍可核。
8. source-A-to-B。材料A scope挂起时改材料B，迟到A不能显示或启用当前导出；B显式核对后只POST一次B的source_ids、空activity_ids及B closure_sha。
9. activity-A-to-B。活动A挂起后改活动B，迟到A不取得资格；B显式核对后只POST一次空source_ids、B activity_ids及B closure_sha。
10. mode-change。selected范围核对挂起时改all，旧selected预览不显示；再回selected必须重新核对，不能借旧closure启用。
11. unmount-plan-late。备份计划挂起时切回资料页，返回后再进入工作区、只读刷新，旧marker8899不显示，历史GET不采用旧plan。
12. context-plan-late。计划挂起时可信capabilities推进至generation1／新dataset/instance／restored_readonly，旧marker9999不显示，不授当前verify/activate。

113个合成应用请求，上传POST8、restore-plan POST7、scope-preview POST5；这些均承接实际显式文件／核对操作。恢复验证POST3、导出POST2、activate POST1，均按对应真实按钮动作恰一次；未经显式验证／导出／激活动作的新消费POST0。没有把文件选择正常触发的上传／计划称为“所有POST零”。

routes只模拟目标界面状态和动作字段，不是完整后端ControlHub等价实现。activate已存业务键的合成历史查询未建立真实激活journal，回查fallback只能显示受控未知事实；该记录不参加当前plan绑定、未形成执行资格，也不作为真实后台恢复证明。新browser不测实际source freeze、目标封存、删除覆盖内容或真实切换，这些未变部分按下述旧证据继承。

## 失败保留和修正依据

本轮所有真实方法和失败见final/method-index.json、final/failures.json、preflight-failures.json，原C01/C02及115 FAIL不改。

1. 首条同步采样Python路径用根.venv而非backend/.venv，exit1，没有执行Python或消费者；更正现存路径后读取成功。
2. 初次bootstrap以path读取规则对象，实际字段为absolute_path／relative_path，KeyError发生在C03目录和旧账写入前；按实际清单结构与锁定七指纹修正后接收成功。
3. 一次Windows rg未展开路径通配、一条猜测日志后缀读取不存在文件，均为只读工具错误，无产品动作，修正后直接读取实际返回名。
4. 曾将Python stdout中文乱码误判为输入含替换字符。随后直接检查Unicode值无U+FFFD且七绝对路径全部exists，输入正常，观察判断已更正，原观察和纠正事件均保存，没有修改规则／输入。
5. c03-browser-1210213609000000 exit1、7.954秒，在exact“删除处理”label定位时超时。CAP／材料／活动请求已到，pageerror0，十二业务场景全部not_run，未误签产品失败或passed。依据实际label包含select选项文本改为combobox关联label前缀，同时静读main的真实onSelection=window.location.reload修正夹具重载步骤并增加后续FAIL的DOM／截图保存。没有改产品、bundle或删正确断言。复检c03-browser-1210447187000000的十二项通过。

第一次运行的failure.json、stderr、method、as-run及准确close留原字节；当时没有保存失败DOM，不追认存在。第二次前的locator/reload脚本语法检查exit0。第一次脚本SHA与最终不同，final_binding=false实标，不能将其改写成最终方法。第二次所有前端被测源码、脚本和bundle均与final一致。

没有本轮backend/typecheck/build产品失败、自动审批拒绝或机械第三次Browser。Backend本地文件检查基于旧轮已证sandbox硬链接权限问题采用明确获批执行，只写C03合成根并替代原始PG连接；Browser同样只在精确本轮profile获批运行，未向用户索取旧密钥或突破冻结核心。

## 最终字节、方法索引与继承

final/manifest.json登记246项，实际存在243文件。pre保原当前235原件；final/source、final/diff保本轮实际新增、修改和构建移除。新六个c03夹具适配器、test_data_exit_c03.py、task114-c03-inputs.mjs有真实added标记，没有伪造pre。原budget.py／freeze.py未改，C03薄适配单独约束新许可、累计门和本轮证据根。

final/method-index.json实填十三项，其中十一项离线／syntax／typecheck／build、两项Browser。每项真实argv、cwd、UTC/mono起止、exit、独立实际耗时、as-run和针对真实参数／被测文件的最终hash映射均存在，offline_exact和browser_exact不是空数组。早期metadata或夹具之后修改的语法方法身份差异明确false；同字节比较不把syntax方法升为功能通过。最终LoadingPin功能方法和最终十二项Browser方法直接适用当前产品。构建as-run保存输入，输出名以真实build日志和后续两个Browser／final原件的同bundle身份绑定，不伪称构建前as-run含自产输出。

final/inheritance.json实核原事件字节前缀、全部旧资源对象、完整C01/C02结束段、原根起点、七规则、原115报告／采用合同和普通ReferencePin AST。原115报告仍61253字节／3d6a4ce4e30284f6799f61462e84c419a9fdd7226ef1f1e73dc468815b04a0f2，原113合同仍81813字节／8a56ebf3c1715895e3ee7a0dcf1f621b591335400e9898aa00df8cb2b7a61aaa。

F01取消请求／不可逆短CAS、joined消费者、撤权准确停止及completion确认核心，F04同RR正文依赖投影，control/api/readability/snapshot/packages/deletions/maintenance/files、001—013/schema/codec/ACL、原业务模型／Native/worker/StopProof/preview均未改。新pin Operation.check加强同D和取消拒绝，没有重开取消准入；旧真实PG／HTTP正常身份、取消、撤权／停止和31域权限证据在未变范围继承。原CAP反序六场景不重复，context/dataApi/ReadonlyRecords/main未改；本轮DataWorkspace输入入口以新最终route方法补足。

原真实PG两秒期限样本按115原件纠正。deadline-original-progress.json只有prepared→running/reading→reading→failed，耗时2.047秒，小于设计publication延迟2.1秒，没有到capture后注入。只继承真实PG读取过D拒绝和无发布，不能称真实PG捕获完成后的后段延迟已通过。原文件层capture后截止、最终成功帧／observer的有效方法保留其原受控层级，本轮不另开PG维持过强表述。

## 累计预算与准确收尾

原C02 root21、build5、Browser5、offline172.317、hold462.047沿用。本轮新增根2，分别c03-check-group和c03-browser-group；两次Browser在同一活根连续记录，不按命令拆根，不复活结束的C02根。

本轮交回累计root23/24且本轮最多23，Browser7/9且本轮最多7，build6/7。PG create9/12、physical success9/9、start37/37，Windows11/12、API8/11均未新增；本轮真实PG/SQL/create/start/API/Vite/Native业务/preview/provider/费用/公网操作0。PG与本轮Browser启动门已用满，不借其它资源余额再启动。

离线实际新增33.642秒，累计205.959秒，受本轮1800与旧7200双门。持有保守新增25.829秒，累计487.876秒，受本轮600（最后120收尾）和旧10800／业务9600双门。controller和Chrome各自准确PID/birth登记，二者begin统一取controller创建前实采作保守上界，不少算持有。

本轮活动上限10800含最后1200收尾，占旧C02剩余额；旧C02已用9188.720111与本轮连续活动相加不超21600。包含从内存门提问至回复的普通等待，没有暂停或换窗清零。最后结束点、精确活动秒数／合计、receipt/events和结果SHA以final/delivery.json及唯一control的结束段为准，正文不虚构先于保存的精确终点。旧C01活动9739.953、旧55525.796／净unknown、115累计8617.261566及其独立资源账、G11/25/UNKNOWN/R60/count1/13元/626.566全部保留，不借审计余额。

本轮第一对消费者controller43948／birth134364123527258761、Chrome17968／134364123544075882；第二对controller46336／134364125862860846、Chrome22724／134364125866259439。均有真实browser_closed事件、WinAPI准确birth的process_ended及method结束原件。新profile、DOM、截图、合成原件／测试Hub、失败和预检记录保留，不删除以清场。

旧九PG对象、旧source frozen／target07 generation1、新C02 target01只读／failed target02、卷、旧业务selector/journal和旧进程停止metadata完全冻结。本轮没有唤醒Docker或重新实查容器，旧stopped事实如实按既有闭包／115／主控metadata继承，不冒称今天现场重查。C03合成测试Hub的running/allocated为受控已退出进程留下的事实，不是活动PG对象或可恢复的旧执行许可，未授verified。

## 未新增验证、风险与下一步

本卡必需修复及受控／route定向证据已完成，无剩余外部内存阻塞。边界是受控连接参数和真实Chromium route交互，不声称物理PG挂死／驱动强制终止、真实恢复主链、源fence／selector切换或完整ControlHub后端在本轮新测。原正常链在未变实现上继承，不外推新bundle全链HTTP/PG已经重跑。

建议主控将稳定候选交原115仅复核loading pin传播、删除策略／计划及两类范围输入和实际改动影响，同时核上述继承更正与方法身份。无需重做F01/F04或旧G11全链。最终DEF035/036、有限STEP017、正式架构／执行状态／CHG仍由主控据独审裁定，本窗口不自签或主动派发。

## 以下保留上轮69598字节结果全文原字节

