# TASK-115 / R-109 — review-02 F02/F03增量独立终审

有限增量结论：F02/DEF035、F03/DEF036均具备关闭条件；本轮两项的代码、证据与增量执行控制判定通过，建议主控结合原有效主链关闭有限STEP017，本轮新增业务运行全部为0。

2026-10-14，Asia/Shanghai。本结果限于TASK114续作03两处余项及其实际传播，未填写主控最终验收，不宣完整NFR005恢复后继续、STEP018—020、M-1、项目或发布通过。原F01/DEF034与F04/DEF037按主控已关闭和未变充分证据继承，未重做四项全审或29项表。

## 范围、独立性与当前身份

继续原TASK115独立窗口，实际环境为Codex desktop、系统GPT-6，A+仅为资源标签；未参与TASK113/114工程、未派子Agent。已实读review-02卡、根入口、本轮许可及工程目标卡，七锁定规则实际SHA均一致，同窗已读V4.0/CHG-0003正文复用，WORK适用2/6/8章不变。正式文档仅作版本/授权定位：需求v1.2、架构v1.31、执行动态v2.55、阶段07。

原主控摘要意外暴露的披露继续保留。本轮首批目标、许可及中性输入包含候选定位，随后正式文档版本检索附带显示架构动态第7行候选摘要；发生在本轮源码裁定前，未作为独立通过证据，不能声称绝对未接触主控摘要。未读取TASK114-result.md及pre内工程自评正文、实现完整聊天/思考或记忆中的工程结论；工程结果仅在delivery中见身份元数据。自己的原115报告、findings及原始反例允许复用。

读取/解析861项登记身份全部相符：当前246项中243实际文件、三缺失输出；final/source、pre、七规则、根入口、原采用合同、工程卡、原报告、review-01的23原件及本轮必要原始导航未漂移。原采用合同81813字节/8a56ebf3c1715895e3ee7a0dcf1f621b591335400e9898aa00df8cb2b7a61aaa不变。原结果61253字节/3d6a4ce4e30284f6799f61462e84c419a9fdd7226ef1f1e73dc468815b04a0f2已先存本轮prior-result.md，全文原字节保为本次结果后缀。

实际产品源码增量仅reference.py、restore.py、DataWorkspace.tsx。其它变化为六个C03工程夹具、一个后端定向测试、一个前端方法，以及构建的index.html/新bundle/移除旧bundle，共14项新增、修改或移除。index-NDc3grUN.js为本轮构建移除，index-CJ8Yp7JQ.js、index-DcQS7jxH.js更早已缺失；三者均未恢复，也未视作产品缺陷。

本轮独立身份与差异原件见 [identity-before.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/review-02/identity-before.json)、[current-deltas.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/review-02/current-deltas.json)、[as-run-identity.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/review-02/as-run-identity.json)。所有检查均为标准库文件hash、JSON、AST或diff，不import产品、执行原方法或穿过保留junction。

## F02/DEF035：同一截止的loading pin传播

原根因是在_load复制原件前，LoadingReferencePin直接独立connect_timeout=3查询loading身份；外层Operation无法给该调用分配本job剩余D。当前 [reference.py](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/reference.py:45) 构造器的operation为必需关键字，先检operation.hub与factory.hub同一对象、job_id与不可变TargetRef的job_id一致，再做live pin检查。连接使用该对象的operation.connection(factory.loader_dsn(target))，没有新Operation、started、deadline或可选None放行。实际唯一产品构造点为 [restore.py](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/restore.py:445)，明确传入_load接到的原operation；全app搜索无第二个产品构造点。

直接依赖Operation.connection未改：连接前check，按原D剩余量给connect_timeout、statement_timeout、lock_timeout；不足整数秒下限拒绝，不以0放无限等待。BoundedConnection在语句前重检、重设剩余语句限制，并在execute返回后check。pin在fetchone返回后再check，连接上下文在COMMIT前后均check，构造器退出连接后再做完整pin.check；即使原始连接、query、fetch或COMMIT已经返回D外结果，该结果也不能授原件执行资格。

live pin还检共享lease存活与准确root、target位于factory._ephemeral、Hub目标allocated/job running，以及prepared一致。PG返回必须明确data_loading_allowed=True且dataset_id、instance_id、originals_root_id与目标相符；未知/错误身份拒绝。_load保持PackageRows的原operation.check、原D剩余RootLease取得和eligible_hashes/删除覆盖，先成功建立pin，才打开原件archive stream进入OriginalStore.put。发布前仍检pin及prepared hash/size。失败向原恢复controller传播，未提前授verified；取消、不可逆准入和completion核心不变。

功能原件为 [loading-pin方法](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-03/methods/loading-pin-1207676843000000.json) 与 [定向测试](D:/shspic/project_NO3_RetroLume-agent/backend/tests/test_data_exit_c03.py:79)。实际argv为既有backend/.venv/Scripts/python.exe -m unittest discover -s backend/tests -p test_data_exit_c03.py -v，cwd为项目根。批次UTC 2026-10-14T00:03:35.907594Z至00:03:38.641145Z，单调时钟1207677140000000至1207679875000000，外层耗时2.735秒、exit0；原unittest正文为3 tests/1.964秒/OK，二者口径不同并分别保留。本轮未运行该方法。

- 01-same-operation：实际Hub、Operation、BoundedConnection、LoadingReferencePin和RootLease参与，pin.operation与原对象相同，started_ns=10000000000、deadline_ns=12800000000、actor/clock_domain保持原值。剩余2.8秒时实际connect_timeout=2，连接options为2800ms，受控connect消费0.25秒后语句前限制为2550ms；root/prepared错误以及D外live pin均拒绝。
- 02-no-connect：剩余0.75秒、已经过D、exclusive lease、wrong_operation、wrong_root、not_allocated六个输入均在原始connect前拒绝，连接次数0。其它Hub/目标/身份分支按当前源码的具体拒绝路径判断，未把未枚举分支冒称动态跑过。
- 03-actual-load：实际RestoreController._load、PackageRows、pin、Operation、RootLease和OriginalStore参与；合成reader提供一条material_versions与小原件，factory只提供Hub、临时loader映射/DSN，未替换pin/Operation/_load/store核心。connect/query/fetch/COMMIT晚返回以及wrong_instance/not_loading均未打开原件stream、无原件发布、无incoming残留、未授verified且原D未重计。正常输入实际发布正确bytes的小原件，然后fixture_stop_after_original停在元数据边界；这不是完整restore/seal通过。

替身仅在原始psycopg连接边界、明确的模拟时钟推进和合成输入，符合工程卡/原审计选择的受控参数与真实传参验证层级。关键被测源码、测试与直接依赖的as-run和最终hash一致，故足以闭合原B级未贯通调用漏洞。普通PreparedReference、ReferencePin、OriginalReferenceCoordinator的AST与改前完全相同，ticket/epoch、source permit及两阶段引用协议未回归。

不签新增物理PG等待上界、驱动强制终止或内核挂死处理。旧两秒真实PG样本只到reading后failed、实际2.047秒，未抵达2.1秒publication注入；仍仅继承真实读取过D拒绝/未发布，文件后段受控方法另按原层级成立，不要求为旧过强表述重跑PG。

判定：F02/DEF035具备关闭条件；未发现该修复产生的具体新Must缺口。独立解析见 [pin-raw-analysis.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/review-02/pin-raw-analysis.json)，普通引用继承见 [ordinary-reference-ast.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/review-02/ordinary-reference-ast.json)。

## F03/DEF036：输入、计划、范围和动作共用资格

原反例是已经确认snapshot_only时上传/建plan挂起，选择改成respect_current只清UI，旧闭包仍能装回snapshot plan并被verify消费。当前 [DataWorkspace.tsx](D:/shspic/project_NO3_RetroLume-agent/frontend/src/data/DataWorkspace.tsx:23) 的InputBinding同时携kind、dataset lifetime epoch和restore/scope各自revision。invalidate同步推进ref revision，并清planRef/restoreRef后再清相应React state；不会等下一次render才撤销旧对象资格。策略/文件/撤回snapshot确认均失效restore，mode和材料/活动ID选择均失效scope；卸载、重挂、token或受信实例/代次推进改变lifetime并清两种绑定。

upload在fileHash后、上传JSON返回后、restore-plan返回后逐段checkInput，installPlan同时检查返回deletion_policy、捕获expectedPolicy与同步policyRef。refresh只可刷新它开始时已持有且仍current的plan/job，回包前同时核原ref未被替换，并核plan_id、plan_sha256、package_root_sha256；历史jobs的只读GET不能自行建立当前计划资格。全局CAP反序和dataFetch身份防线未修改，dataset_id不独立列为effect依赖也不构成新绕过：未变context契约拒绝同control/instance/generation下dataset身份改变，有效推进会触发既有依赖。

呈现planCurrent、确认planConfirmed与动作actionPlan共用绑定、deletion_policy和executor资格。verify发送当前plan_id/hash及明确confirm/unknown字段，返回后再查binding和job.plan_id；输入已变的verified事实可由原操作键读取，但不回填restoreRef。activate还核当前plan对应的verified job、当前模式、原hash和selection_generation，回包后再查绑定才调用main的真实onSelection=reload。撤回unknown确认使planConfirmed为false；撤回snapshot确认还失效restore绑定。没有以一律禁用动作或丢弃全部历史代替修复。

scope-preview的await后checkInput保护整个mode/source_ids/activity_ids集合，BoundScope只在当前revision安装。create点击时再核scope绑定与closure_sha256，selected导出仍携expected_closure_sha256；原后端闭包比对防线保留。材料/活动选择及mode变更可在处理中真实触发，旧scope不能变成新输入的闭包。已明确提交后输入变化不撤销已发生HTTP事实，但不会把旧回包授给新输入，也不会自动重POST、上传或激活。

最终功能方法为 [c03-browser-1210447187000000/result.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-03/batches/c03-browser-1210447187000000/result.json)，实际方法是node执行frontend/tests/task114-c03-inputs.mjs，cwd项目根，参数为项目根/该批输出/该批独立profile。UTC 2026-10-14T00:49:46.282969Z至00:49:51.272815Z，mono1210447484000000至1210452468000000，4.984秒、exit0。实际Chromium加载当前最终dist，服务由Playwright routes读冻结文件直接fulfill，全部请求限定127.0.0.1:18114并阻止非白名单，零TCP监听/API/PG。它证明真实控件/最终bundle的交互，不证明真实后台Hub、selector切换或激活。

独立核对113请求、十二case和十组held/released记录；十次释放均为fulfilled，未用旧响应已经被fixture预先丢弃替代产品检查。以下逐原子义项成立。

- upload-pending-policy-change：seq10实际上传已挂起，snapshot确认有效后改respect，再释放旧上传；旧事实保留，但restore-plan POST0、verify/activate按钮0、restore POST0。与GET plan反序是不同挂起点。
- plan-pending-policy-change：seq11上传、seq12 snapshot plan已挂起，改respect后释放；7199 marker不回填，当前respect仍无可执行plan，restore POST0。该路径独立覆盖计划响应。
- fresh-respect-positive：seq13/14明确选择新文件并取得respect计划104，seq15明确点击仅一次验证该plan/hash，unknown=false、confirm=true；删除覆盖31呈现，验证和切换按钮可用，证明正常路径没有被全面禁用。
- refresh-plan-late-policy-change：已绑定job的只读刷新GET plan挂起，策略变更后旧GET不能重新授资格，snapshot确认被重置、文件选择disabled。该GET只用于这条入口，未冒前两条覆盖。
- snapshot-unknown-positive：先明确snapshot确认，删除历史unknown时验证disabled，明确unknown确认后seq26验证计划108、正确hash/unknown=true，seq27一次受控activate携同hash、generation0、confirm=true。真实main触发page reload并新增一次session GET；重新进入仍无执行plan，不自动采用历史。
- same-context-file-replacement：旧文件overlay51已有效，新文件选择立即失效旧plan，replacement上传挂起期间无plan且文件控件真实disabled；新plan52回来后才能重新呈现，restore总数不自动增加，旧51不回填。
- verify-late-input-change：seq48是输入改变前一次明确验证，响应挂起期间改policy，释放旧verified后无当前plan/activate资格。历史GET仍可核对该job，不自动再次验证或切换。
- source-A-to-B：seq49范围A挂起，真实取消A/选择B后释放旧scope，导出disabled且A marker不呈现；seq50重新明确核对B，seq51明确导出仅一次，source_ids仅22、activity_ids空、closure为B的5f12dc…bbfa0。
- activity-A-to-B：seq52活动30范围挂起，真实换31后旧回包不能启用导出；seq53核对B，seq54明确导出，activity_ids仅31、source_ids空、closure为5f77b4…6bc64，材料与活动两类入口均覆盖。
- mode-change：seq55 selected范围挂起，改all后释放旧scope不出现活动31 marker；再回selected必须重新核对，导出disabled。
- unmount-plan-late：seq56/57原计划挂起，点击我的资料卸载，再释放8899，重新进入及只读刷新均不采用旧plan；marker不呈现。
- context-plan-late：seq91/92计划挂起，通过真实capabilities刷新推进generation1及新dataset/instance/只读模式，再释放9999；旧marker不呈现，当前无verify/activate资格。

对应新增消费动作只有restore3、export2、activate1，分别对应fixture里的三次verify click、两次export click和一次activate click；未经动作的新增消费POST0。另有上传8、plan7、scope-preview5，分别来自明确文件选择和核对点击，不能把这些正常调用误报为自动业务重发。DOM/按钮原件与02-plan-policy、03-fresh-respect、06-context-late截图已实读/查看：旧snapshot计划未呈现，正向31计划有动作，可信新上下文保留历史而无旧计划。其余场景以实际控件动作、assertion、POST体及held/released原件共同支持，未声称每场景都有独立截图。

route DTO包含Plan的policy、plan/hash/package-root、executor及明确最新删除状态；activate返回和历史fallback仍为合成事实。该分层限制不参加真实激活通过，也不授当前资格；当前InputBinding和动作链已由源码及上述实际浏览器方法共同闭合，无依据要求重做PG。

判定：F03/DEF036具备关闭条件；未发现当前选择、计划、确认或范围的具体新Must缺口。独立时间线与动作解析见 [browser-raw-analysis.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/review-02/browser-raw-analysis.json)。

## 最终/批时绑定、继承和证据边界

当前关键身份已实际核对：reference.py为0b0f671c7760ded575816461732b105022172defad6e0952c3490f4452d3e163；restore.py为3536262ef399790eb1f3d968cd8a1f712ce6828bcad430ad6c347d87159248c6；DataWorkspace.tsx为878b2ef365e704b01432e6d1d934034d2e7e2ce3c506577dfa682415491fd3da；最终index-DZduJTtr.js为9c9a3c69659371fac708d3ace004aca67b67f789a2b4a3725da1bf5c3cf60181；index.html为df38c0f0ca2630dfbe678d23aca7884c9063a0b9f7c0f80e5bfcc68a607a9f63。HTML实际引用该bundle，最终Browser seq2及reload的seq29均实际请求该文件，其finalIdentity与当前所有登记assets相符。

method-index实填13方法：11个离线/syntax/typecheck/build、两个Browser。独立核196条tested-file绑定，记录hash、实际as-run文件hash、最终hash和same_final标志全部一致，无虚假绑定。loading-pin核心/测试与最终版一致；最后Browser源、夹具及最终bundle均一致。较早Browser syntax、delivery syntax、locator修正syntax、route-whitelist syntax、bootstrap syntax及第一Browser等七条相关绑定真实为false，均保留，未以它们给最终功能通过。构建as-run在执行前保存，其dist HTML仍为旧输出，这是预执行快照，不是最终Browser加载旧包；构建源与最终一致，输出由原build日志、当前HTML及最终Browser另行绑定。

最后build原日志exit0，7.578秒，typecheck为21.985秒/exit0；build仍带已有dynamic import和chunk-size warning，未把syntax/build当功能证明或将这些非阻断提示升级成新门。实际argv、cwd、UTC/mono、日志和绑定导航见 [method-navigation.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/review-02/method-navigation.json)、[tested-file-binding-checks.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/review-02/tested-file-binding-checks.json)。

未变部分按实际身份与传播继承：operations.py仍b57348…a876，context.tsx仍fdf86f…08f9，dataApi.ts仍d68650…e679；001—013、schema/codec/ACL、普通ReferencePin、F01取消/准入/completion、F04正文依赖及api投影、Native/worker/StopProof/preview、ReadonlyRecords/main不变。pin增量只收紧原件进入资格、不改角色、SQL恢复/封存或停止流程；前端增量只改变DataWorkspace的输入资格，不改全局CAP和正文读取机制。原正常PG/31域/两FK/两锁序/共享引用/SUP及其它未变主链继续按原适用层级有效，未因为字节有变化自动作废，也未因SQL未变直接授整个新版本动态通过。

确定新缺陷与确切原Must缺证：本轮未发现。物理PG等待/驱动终止、完整真实selector及全量恢复后继续均不是本轮已验证对象，保持原边界；它们不改变两处原根因已按既定方法闭合的判断。

## 原失败、修正与执行控制

第一Browser c03-browser-1210213609000000在exact删除处理label等待超时，7.954秒exit1；原failure/stderr/方法/as-run保留。只有9个initial请求、业务matrix为0，pageerror0，无该失败时的DOM/截图，不能追认PASS或伪造失败截图。最终夹具将真实select定位改为role combobox加label前缀；main.onSelection本来就是reload，原不可达的激活后继续操作旧页面断言改为核真实reload、一次session GET、重进无历史执行plan，同时补后续失败DOM采集。源/bundle未因修夹具改动。第一到最终diff显示原上传/策略/范围、字段/次数与旧marker正确断言保留，修正针对真实夹具与可达生命周期，不以删正确断言凑通过。第二批十二场景独立exit0，不能倒写第一FAIL。

C03的bootstrap规则字段KeyError、Python路径/rg/猜日志名错误、stdout乱码观察及其Unicode纠正均按原件保留。accepted旧文字曾称路径有替换字符，后续实际Unicode/Path检查明确否定该观察；锁定七路径当前也均不含U+FFFD且hash匹配，故不能继承已纠正的错误解释或据此把产品判失败。本轮Python stdout也出现过显示乱码，落盘JSON用明确UTF-8，判断采用原UTF-8原件与PowerShell实读，没有改工程原件。

本轮首批大清单直接显示曾被工具截断，随后以标准库逐项核861身份、13方法及196绑定完成读取，不依赖被截断片段下通过判断。另发生两次纯元数据路径猜测错误：Browser方法实际在batches而非methods；C03 as-run项目路径直接置根，未使用source前缀。均为不存在文件读取exit1，改从真实目录列表/已核as-run实际路径读取后完成；失败解析脚本原字节及原因保留在 [metadata-failures.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/review-02/metadata-failures.json)，没有产品运行或原证据修改。

C03原唯一账counts为root23/24、Browser7/9且本轮门7已满、build6/7、PG create9/12/success9/9/start37/37、Windows11/12、API8/11。离线累计205.959秒（C03增33.642），保守真实持有487.876秒（C03增25.829），活动C03 4495.4211376秒、C02+C03 13684.1412486秒。首工具未同步mono，后实采QPC/UTC并保守早扣300秒；中途内存不足等待连续计入，不能签完美计时。四次低于2GiB的门原件保留，两个实际Browser入口分别达到2486710272/2439004160字节后才启动；未因本轮只读复核再查内存或启消费者。

原账pre/events.jsonl的187887字节全文是当前234236字节事件账的精确前缀；新70事件追加，旧resources和continuation_history逐项原值不变。C03仅新增两次Browser及两个controller，精确关闭原件均记录process_ended/actual_browser_close：第一controller43948/birth134364123527258761与Browser17968/birth134364123544075882，第二controller46336/birth134364125862860846与Browser22724/birth134364125866259439。相应批时事件有真实browser_spawn/browser_closed，最终delivery四资源均stopped。旧九PG对象Stopped仅继承旧精确原件，本轮未Docker/CIM/SQL/监听现场核查，也未伪称今天重新观察。

原114 C01活动9739.953、旧55525.796/净unknown、全部FAIL，以及G11/25/UNKNOWN/R60/count1/13元/626.566均未清除或重开；未借用工程余额、签退款或执行许可。本轮审计只读解析不是离线产品测试，其耗时只进入审计活动。TASK115旧累计8617.261566/21600，原root3/API3/Browser2/offline125.610/保守hold14.874及初轮和review-01全部失败、偏差保留。

本轮许可TASK-115-STEP017-REVIEW02-20261014，5400秒含最后300秒落盘，日历硬截止仍2026-10-15T06:16:24.914938Z。首工具返回UTC 2026-10-14T01:20:19Z未同步mono，下一次实际同步样本为01:20:37.9530199Z、QPC ticks12122991647744/frequency10000000；不倒填首点，采用保守UTC起点01:15:19Z扣300秒并连续计入所有读取、模型处理、普通等待、报告保存和复读。最终实际落盘及累计值以本轮 [delivery.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/review-02/delivery.json) 为准；该文件还核原61253字节后缀、保护输入和报告完整可读性。首点偏差不因此清零。

本轮新增真实根、PG/SQL/Docker/API/Vite/Browser/compile/test/build/Native/preview/provider/费用/公网全部0；无Git写、安装、产品/原tests/fixture/dist/用户配置/原证据/DocuS/公共库/记忆修改。新增文件仅在review-02，结果仅增加本前缀。控制原件解析及最终身份见 [final-binding-and-control-summary.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/review-02/final-binding-and-control-summary.json)。

本轮保存前实际计时观察：UTC 2026-10-14T01:39:23.444027+00:00，本轮从保守起点连续计1444.444027秒，旧累计加回为10061.705593秒/21600。最终保存、完整复读和保守收尾累计以delivery.json的实采值为准，本观察不是倒填首工具精确计时。

## 三轴判定与最小交回

- 代码判定：F02同D传参和pin返回资格、F03输入revision/lifetime及计划/范围/动作绑定通过；未发现两处修改向F01/F04或未变Must传播出具体回归。
- 证据判定：原始方法、正常/拒绝原件、十二route场景与最终版本绑定足以支持两原根因关闭；原充分主链和已关闭项直接继承，真实PG与selector层级限制保留。
- 执行控制判定：本轮只读边界和所核C03增量许可、计数、失败保留、连续保守计时与准确关闭可接受；旧FAIL、UNKNOWN和历史控制偏差未被改成通过或抹去。

建议主控关闭DEF035/F02和DEF036/F03，并以已有有效主链、F01/F04已关闭及本次两余项闭合裁定有限STEP017。最终DEF/STEP/正式文档状态和CHG仍由主控维护，本窗未修改共享账或自签主控验收。无需新动态、工程重跑、密钥、释放内存或开启容器；必要人工仅带回结果路径。独立裁定原件见 [findings.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/review-02/findings.json)。

## 以下为review-01及更早报告原字节

