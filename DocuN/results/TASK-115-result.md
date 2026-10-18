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

# TASK-115 / R-109 review-01 增量独立复核结果

## 当前结论

本轮增量复核不通过，有限 STEP017 仍不建议关闭。DEF034/F01 和 DEF037/F04 的原问题可建议关闭；DEF035/F02 和 DEF036/F03 仍有明确传参与生命周期缺口。没有新增业务运行，没有直接修产品，也没有将已有方法的 passed 扩大为最终版全部 PG/HTTP 通过。

- 代码轴部分通过。取消与不可逆准入、已删除依赖正文投影已形成正确机制；恢复原件 pin 的 PG 检查未纳入同一 D，上传／范围选择变化仍可被旧计划结果覆盖。
- 证据轴部分充分。支持原取消反例转正、正文资格及正常只读副本的具体事实，也支持最终文件／Hub 的六项方法；不能证明上述两个未修分支，真实 PG 期限样本也没有到达所声明的发布延迟点。
- 执行控制轴本轮只读范围内合规，首工具 mono 没有同步实采的计时偏差如实保留并保守扣时。产品、PG、Docker消费者、Browser、API、编译、测试、build、Native、preview、模型、费用、公网、Git写均新增0；旧失败、投入、权限、原报告和预算未清零。

这是独立执行者的建议，不填写主控最终验收或 DEF/STEP 状态，不签完整 NFR005、恢复后继续执行、M-1、项目或发布通过。原正常恢复、31域、同T、两锁序、两FK、共享引用、原SUP双EOF/四账和G11的未受影响结论继续有效。

## 范围、独立性和身份

继续原 TASK115 独立会话，实际客户端 Codex desktop，系统身份标签 GPT-6，用户资源标签 A+；未参与 TASK114 实现，未派子Agent。只读当前合同、增量源码／方法／原始证据，没有读取 TASK114-result.md 或 pre 中的自评正文、实现聊天／思考。原首轮意外接触主控候选摘要的披露继续保留。本轮授权段提供前置与文件身份，没有将其作为四项产品通过证明。

项目根 D:/shspic/project_NO3_RetroLume-agent，task_model，V4.0／公共 AGENTS CHG-0003，需求v1.2、架构v1.29、执行动态v2.53、阶段07。根入口及本轮合同已读；同窗未变公共 AGENTS/WORK 适用2/6/8章正文复用，七个锁定实际指纹再次相符，没有自动采用后来规则。

采用合同仍为81813字节、8a56ebf3c1715895e3ee7a0dcf1f621b591335400e9898aa00df8cb2b7a61aaa。工程本轮卡21703字节、66d59f421d7514247f2cc88d6a229d582d06448c9c6848058930153e8e35ce4c，作为目标和许可读取。

新证据根为 [review-01](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/review-01/)。原37767字节报告先保存为 [prior-result.md](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/review-01/prior-result.md)，本文件原结果区为相同原字节后缀，旧结论／反例没有改写。未修改 DocuS、AGENTS、公共库、用户原始需求、原工程证据／控制账／tests／源码／bundle。

## 冻结核对和实际读取

[identity-before.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/review-01/identity-before.json) 实核当前237登记项、final/source237项、pre217项、七规则、八合同／账／metadata身份、358份旧审计原件、58份本轮原批次索引原件全部匹配。当前实际存在235文件，两项旧构建输出不存在。index-CJ8Yp7JQ.js为本轮移除，index-DcQS7jxH.js在C01已缺失、此次登记unchanged；没有把它们算新缺陷或当前文件。

21个 as-run 原件内部 hash 全部匹配。最终 c02-boundaries-1161322062000000 的产品字节与当前无差异。前端 index-NDc3grUN.js及相关源码与两次实际 Browser 方法适用版本一致，不重build。001—013、schema/codec、原角色／业务模型和 Native/worker/preview 原写／停止核心未改；新增可选 Operation 路径仍逐调用分析，不能用这些未改身份证明所有截止传播完整。

读取 operations/control/api/packages/snapshot/restore/repository/deletions/reference/config/maintenance/files/readability，以及前端 context/DataWorkspace/ReadonlyRecords/dataApi/main、README 的实际增量和直接调用。读取 c02 方法、原始 SQLSTATE／行值／HTTP／DOM／截图导航、原 events/receipt、closure 与最新已保存 owned metadata。没有 import 产品或执行其方法；新脚本仅作文件hash、JSON、AST和有限diff。

[as-run-identity-and-method-deltas.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/review-01/as-run-identity-and-method-deltas.json) 保存逐函数差异。[rebuilt-offline-navigation.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/review-01/rebuilt-offline-navigation.json) 从真实日志补导航，工程 method-index.offline_exact 的空数组保持不改；重建不是同点采样，未知的每方法独立墙时不补造。完整 argv 可由原 events 对应 label 读取，最后六方法 unittest耗时7.027秒、外层事件子进程7.641秒分列，不混为同一数。

## F01／DEF034 取消与不可逆成功

建议原问题关闭，原严重度P1的根因已消除。Operation 固定私有 actor、D、精确 revision 和准入票据；request_cancel 只写 cancel_requested，执行者收尾确认后才写 cancelled。admit 以短 CAS 在线性化点进入 committing，之后取消返回 operation_not_cancelable。ControlHub.update_job 同时核前状态、revision、允许的kind成功状态和准入，拒绝临终读取latest revision覆盖取消。journal锁没有持有到文件／PG I/O结束。

已分别核 portable_export/restore_checkpoint 的 file_publish、upload_publish、readonly_seal、source_tombstone_commit、readonly_maintenance_selector 六种 kind。未消费取消由 acknowledge_unstarted 阻止以后新消费；已开始同步消费者的 upload/source-delete 使用 joined_thread，重复协程取消不放弃线程。schedule 的后台线程在running后取消不会直接确认停止或重发原job，验证／封存的准入仍由Operation和同operation_lock控制。

证据组合如下。

- c02-boundaries-1160855671000000 的01-cas-all-kinds、03-last-load-cancel、04-asgi-upload以及12-joined-consumer，对六kind顺序、load后取消、EOF取消和重复协程取消有真实Hub／文件／实际handler层事实。factory/load与receive边界明确受控，不冒PG。
- 最终 c02-boundaries-1161322062000000 的02-real-file-cancel记录取消先胜无文件、准入先胜明确拒取消并正常published，适用当前字节。
- c02-pg-cancel-1159293593000000 实际完成新PG load，随后受控请求取消；loader/admin真实NOLOGIN且password清空、目标failed、准确Stopped，不seal、不verified。01/02/03阶段原件和方法相互对应，不只依赖终态词。
- c02-pg-source-resume 的06/07真实仓储取消先胜无墓碑，准入先胜拒取消并删除。c02-activate 的01取消先胜无fence/selector，02真实冻结后精确注入selector拒绝、保frozen/无选择/target已停，03另一次显式确认选择新域generation1。原selector未改。

最终新增 completion_protocol 只加强成功显示与确认，不重开取消门；Operation.admit/check/validate_admission、request_cancel与F01核心状态条件对上述批次未改变。文件当前版复验加上相同PG撤权／停止与CAS归约，足以关闭原取消覆盖缺陷。没有宣称真实内核崩溃、实际丢COMMIT或全部半注册物理异常均验证。

## F02／DEF035 完整绝对截止

原快照后仍新授 published/verified 的根因已有有效修复，但本项仍不建议关闭，严重度沿P1。主要链现在从 Operation 首次消费固定 started_ns/deadline_ns/CLOCK_DOMAIN，不阶段重起D；ZIP/hash/Reader/fsync/link、组件、受限连接、probe、source mirror、Gate和终态确认传入同一对象。新时钟域不续旧inflight或cleanup；私有执行字段不进入普通DTO、包或旧Native/preview执行权。

最终成功协议先短CAS提交成功帧，真实返回后在D内取确认时刻，再写私有completion确认；GET/列表在未确认前投影为未确认，finish失败保已发生文件／selector事实而不授新成功。first成功帧返回被精确延迟至D外时，最终13-success-receipt-deadline实际保持published_unconfirmed/file_publication=confirmed。最后14-mirror-same-D证明observer同一D、超时不能跳到成功，15-upload-file-fact证明同键只核原文件、不再流入第二个body。确认之后仅持久记录已在D内观测的事实，不视为新消费许可。

明确剩余路径为 [restore.py:445](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/restore.py:445) 调用 [LoadingReferencePin.__init__](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/reference.py:45)。该构造器仍直接 psycopg.connect(loader_dsn, connect_timeout=3)，随后 SELECT data_loading_allowed/data_state，既不接收Operation，也不设该job剩余statement/lock timeout。外围 bounded 在进入前调用一次，不能中断尚未返回的独立同步PG调用；该连接的固定3秒也可能长于剩余D。无法以之后的 operation.check 或组件连接已受限证明这条连接完整受同D约束。

这是B级确定的传参／时间边界缺口，未新增PG运行，未声称已经观察到内核／PG挂死。现有loader正常成功和load后取消A只证明正常身份及角色逻辑，未覆盖此失效时的截止。最小修正为 pin 的加载检查显式接收并使用同一Operation／受限连接和check；不要另设D，也不要改001—013或授更大角色。

另有证据适用性更正。real-PG-whole-deadline.json耗时2.047秒、D2秒；方法设计的publication延迟为2.1秒。独立只读解析原journal得到该job只有prepared→running/reading→reading→failed，没有copying/verifying/file_publish，见 [deadline-original-progress.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/review-01/deadline-original-progress.json)。该运行在读取阶段已过D，未到所声明的capture后发布延迟点。它证明真实PG读取超时拒绝且无发布，不能证明真实PG完成capture之后的后段注入；最终文件层05-one-deadline的受控已完成capture输入仍有效，两层不能混写。

如修正pin后需要补证，只做一个真实受限loader检查的剩余D/查询等待反例或准确受控连接参数检查，并保存实际 reached-stage／一次D／无verified事实。若还要支持“真实PG capture后发布延迟”，须保存capture完成与注入调用标志；使用合理小数据/profile确保先到该点，避免被读取阶段提前超时替代。不要求重跑完整正常恢复或全部PG矩阵。

## F03／DEF036 上下文、选择与计划新鲜性

原capabilities反序导致全局dataset/instance/generation回退已修，原反例可关闭；本项完整传播仍不建议关闭。setDataContext 拒同control代次降低、同代异instance和read_only回normal，异control仅可信会话bootstrap。dataFetch 区分稳定Hub GET/取消与依赖当前数据请求；saved-records真实同T身份核对且陈旧header409，Hub旧键仍200。refresh序号/Abort/生命周期和ReadonlyRecords类别、main列表/阅读缓存清空均有实际增量。

原实际Chromium route方法覆盖gen1先到/gen0晚到、同代异instance、异control、两次refresh的GET plan反序、类别切换和unmount；最终真实sealedPG/TCP/bundle方法无响应替身，已删正文NULL、有效正文、旧Hub键、GET-only刷新均有原件。这些方法及前端最终字节相同，保持有效，不重跑。

剩余P1为删除策略改变没有失效pending upload/plan。当前 [DataWorkspace.tsx:47](D:/shspic/project_NO3_RetroLume-agent/frontend/src/data/DataWorkspace.tsx:47) 的upload捕获旧policy，等待fileHash、上传与restore-plan后在55行setPlan。删除策略select在74行没有busy禁用，只setPolicy和setPlan(null)，不会推进lifetime、计划请求序或取消旧请求。request检查仅token/control/instance/generation的lifetime，57行verify也不核 plan.deletion_policy 与当前policy一致。

具体触发为已确认snapshot_only_readonly后上传中切换到respect_current_deletions；旧闭包仍请求并回填snapshot_only plan，页面select显示respect_current，而后续验证用旧plan_id/hash。这会把新的删除选择与旧计划绑定，涉及是否重新显示已删除内容的Must确认，不能降作普通文案或让用户自己识别hash。静态反例来自当前代码，未在本轮启动Browser，不将其签为动态已发生。

同修复传播还包括scope-preview：选择／mode改变只setScopePreview(null)，旧scope请求没有独立selection版本，回来仍可重填。backend expected_closure_sha256可以拒错误导出，因此该支不证明实际导出了错资料；但UI会显示旧闭包并错误启用确认，需一并修正。

最小修正为上传／策略／计划及范围核对各自绑定输入revision或显式禁止处理期间改变选择；变化清空并取消／废弃旧计划结果，呈现和verify前再核policy与plan及scope与预览身份相符。不能只在第二次refresh增加保护，因为原Browser的“older plan response”测的是GET refresh反序，不是上传中改变policy。只需补两个精确最终bundle交互反例及新选择正例；可用明确routes定位UI，不再真实分配／恢复PG目标。

## F04／DEF037 正文资格和删除覆盖

建议原问题关闭。当前saved-records在一个READ ONLY/RR里核实际库dataset/instance，memory_projection调用既有memory_revision_readable并查memory/source/upstream墓碑谱系，false/unknown不返回body；history_qualification处理原文自己的source_refs/catalog/reference_hashes/memory_refs及活动选定memory，不能仅以当前scope替代旧依赖。数据头、原正文/hash、版本和purge没有被改写来制造成功。

真实新PG source-resume 的02六类合法依赖均present，04 source pointer/revision/hash替换及upstream更新失效，05 event correction失效，08 source deletion使body不暴露但head仍active/revision1/purge none，原stored body hash保持，valid正例仍present。方法、原始行值、SQL函数、schema/codec身份均对上；九guard方法是新正常管理员合成连接、共同准入通过、loading=false、特定P0001/context，并非普通app权限A，普通app ACL在未变范围继承原证据。

实际TCP source HTTP进一步核memories/learning/teaching/interview投影；默认overlay恢复后的target01实际64行/2原件/9组件、31安全域、撤权与sealed事实、最后TCP和真实bundle的deleted body NULL/valid body可读均充分。不能与旧C01的94行/4原件/14组件混成一份样本。

前PG到final只有history_qualification增加选定memory检查，memory_projection与saved-records本体不变；最终HTTP原件用的是新增后版本。再之后只有packages列表等期限/确认路径，未改变该投影。原两次unknown异步诊断未重跑、未转PASS；新实际Selector兼容loop/新PG/TCP是新方法，不倒写旧原因。

## 最终版与前批的继承裁定

各 [late-文件.diff](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/review-01/late-operations.py.diff) 为本卡从最终HTTP as-run重建的只读差异，不修改工程原件；完整逐函数导航在as-run文件中。

- operations.__init__/finish/fail及control.create_or_get_job/current_receipt增加completion协议、D内实际返回确认、未确认投影与失败保存。旧PG角色/load/资格事实仍适用，旧terminal按原协议保留；新协议正常／迟到文件成功由最终六方法实际覆盖。没有最终新协议PG全链A，不称有；关键F01准入状态不变，可严格继承，F02未贯通pin仍保留。
- packages.capture_and_publish把source mirror移到最终成功之前，向observer传同Operation并复核；config.observe_job/validate_source、repository.state/observe_job、maintenance Gate/Permit和deletions/reference.acquire传播可选Operation。None分支保原调用形状与旧Native/worker/preview语义，SQL、ACL、行/根锁顺序及准确删除判据没变，新增有D路径是加强检查，不借None让本job续权。最终14-mirror-same-D证明调用对象相同，但没有真实SQL执行所有新增传参分支，不能只说SQL没改。
- restore._activate_readonly改用公开完成投影判verified，未确认成功不可activate；实际maintenance/selector拒绝与新显式generation1保留，最终验证条件更严格。GET明确区分selector已提交的事实和activation完成未确认，不回退normal。
- api.upload增加current_job对已有文件的只读核对，packages列表使用完成投影，SafeDataRoute避免422回显原始输入。真实TCP断线/hash冲突/secret HTTP方法较早但相同受影响核心已说明，最后15-upload-file-fact覆盖新增同键文件核对；session endpoint named token是认证bootstrap出口，不把此命名出口混为普通DTO泄漏。
- F03最终源和bundle与Browser方法匹配，已经证明的全局身份／类别／unmount不作废；未测且未保护的policy/scope选择仍是具体余项。F04实际read函数/identity/资格和最终真实数据投影匹配，不因其他文件hash不同重新验证。

## 原V门本轮变化

仅列变化或本轮实际传播；未列V01—06、V10—12、V14等原充分正常链按原报告和未变机制继承，不重建第二份29项清单。

- V08新增normal共同准入后九特定guard的真实P0001/context，排除了frozen/42501/零行快捷证明；其连接为新合成admin，不能写普通app九分支都动态通过。与相同SQL、bound loading条件和原普通role ACL反例组合，原guard传导缺口已有充分有限证据。
- V13/V15/V16新增真实合法/替换/upstream/event/delete及默认overlay正文资格，F04可关闭；F03策略计划错绑定可能绕过本次用户的尊重删除选择，因此整个策略确认余门仍留DEF036。
- V18新增真实Windowsjunction/reparse有效ZIP父路径拒绝，10a/10b外部sentinel文件集合/长度/hash一致；原白名单路径/压缩拒绝保持。脚本直接核集合，没有穿过保留链接读取或删链接。无需枚举所有相同白名单输入。
- V19新增JSON深度恰界/超一、组件1行98字节恰界/超一、真实TCP Content-Length不完关闭、取消/准入两序。组件为真实pre-SQL bound方法，非目标SQL事务A；日期/未知时钟不能给新预算。F02 pin截止和F03policy/scope生命周期仍阻相关有限门。
- V20最终版spool-open/copy-read/pending-fsync精确受控失败保旧文件、不发布、pending准确收尾；成功文件/Hub收据失去返回只GET原键，capture/body流不再消费。不是实际内核挂死或真实丢COMMIT，正常原no-replace事实继承。
- V21真实load后取消、角色撤权/停止failed目标，以及controller/Hub的半注册/seal/allocate截止受控边界均有明确层；未把工厂替身写物理PG崩溃。F02未贯通加载pin保留，其他同组件/角色关系不用重跑。
- V22/V28实际新源冻结、准确selector拒绝注入保无选择/frozen，另新明确确认选择generation1，旧键/包跨切换仍可达；不冒物理日志lost COMMIT。新completion不能从旧inflight续权，源不可用不自动normal和旧SUP停止证明保原边界。
- V23实际普通响应、422/hash conflict及普通API log marker扫描补齐有限面；原包secret扫描和安全codec继承。api.log为0字节的实际样本，needle_count及范围明示，不能据此保证任意历史/未来日志或用户文本无秘密；未清洗源码或正文。
- V24/V25/V29全局身份反序、同代异instance/异control、类别/unmount、草稿未迁执行权与GET-only、真正readonlyHTTP/PG/Browser可继承；旧草稿独立下载不自动POST。F03policy和范围旧请求仍需最小修正，不将现有Browser的6个场景解释成所有选择生命周期。
- V26本轮独立审查和零新增运行完成；仍有DEF035/036余项，未满足有限STEP017关闭条件。

## 执行与预算真实性

本卡仅解析既有文件，没有CLI唤醒Docker、PG连接、SQL、API/Browser、compile/unittest、产品导入、安装/build/provider/费用/公网或Git写；也没有访问Env/凭据密文内容、修改系统／服务／时间／网络。没有新增执行根或借旧计数余额。需要的停止事实引用已保存metadata，不再重复运行查场。

最新owned metadata为2026-10-13T12:26:36.3482277Z，九准确PG对象Stopped/Pid0、十七消费者结束、相关TCP0；只是该时点事实，不当作业务或物理异常逻辑全通过。本轮没有创建消费者，故无新停止动作。closure和原events的消费者始终保留。

原TASK114累计root21/24、create9/12、success9/9、start37/37、Windows11/12、API8/11、Browser5/9、build5/6、offline172.317、hold462.047、C02活动9188.720111、C01 9739.953、旧55525.796和净unknown均保留。新增methods与whole-run墙时部分是交付回补，以原event标注exit/argv来源，不倒造独立同点采样。

所有FAIL保留。早期离线60秒超时、不完整日志及夹具签名/预期问题到正确断言；source-init系统Python缺psycopg、两次唤醒后内存门不达均发生在source创建前，后续前提达到再开；source第一阶段memory_profile_required到正确既有记忆准入和保留已提交fixture前缀接续。未改产品权限／DDL制造通过，不将相同异常type一概当相同根因，也不把成功日志追认旧控制完全正确。

本轮首工具内UTC整秒样本2026-10-13T13:16:15Z，未同步取得mono，不伪称精确首点。实采对为2026-10-13T13:18:14.039696Z／1168955812000000ns，按首样本前5秒13:16:10Z保守连续计，所有读审／hash／等待／落盘计入，没有自行暂停。最终本輪工时、旧5490.683454累计和7200/21600余量见 [delivery.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/review-01/delivery.json)；原日历截止仍2026-10-15T06:16:24.914938Z，不延后。

原审计root3/4、API3/3、Browser2/2、offline125.610、保守hold14.874和两次unknown异步FAIL保留。本轮解析耗时属只读活动，不冒测试离线时间。G11/25/UNKNOWN/R60/count1/13元/626.566原样保留，不新签恢复执行／退款。

## 交回最小清单

主控可据本报告裁定关闭DEF034/037，保持DEF035/036与有限STEP017未关闭，并串行维护正式状态。审计者没有改DEF/STEP/CHG号，没有占TASK116或接管工程。

只需将两个余项一次合并交原TASK114工程：loading pin检查贯通原Operation受限连接／check；策略/计划与范围核对绑定输入revision并拒旧结果。补证限于这些点的具体参数／等待、policy/scope变更最终bundle反例与有效新选择正例。真实PG“capture后延迟”的证据若继续声称该层须补阶段抵达原件，否则准确降为已证读取超时、复用文件后段方法；不重新全库/旧G11/正常恢复主链。

本轮禁止新增产品运行，已按该终点收口，不自行申请复验或扩大资源。用户人工只有带回结果路径，不需要密钥、释放内存、启容器或重复采用STEP017-P1。原报告以下为原字节历史。

---

# TASK-115 / R-109 集中独立审计结果

## 结论与交付范围

当前冻结候选不通过，建议有限 STEP017 暂不关闭。确认四项影响原合同 Must 的 P1，涉及取消后的不可逆收尾、发布总时限、晚到能力响应回退当前上下文，以及删除依赖后的记忆正文投影。前三项有冻结真实实现的精确边界补证；第四项为明确代码反例，异步夹具两次超时，未冒称真实 PG 或动态通过。

代码轴不通过。证据轴可支持主要正常链和上述具体反例，不能支持 V01—V29 全部动态通过。执行控制轴部分合规，旧账、失败、源和选择器保留；本卡首工具计时缺失、夹具失败、根标签补账和异步诊断未完成均披露，不宣无偏差。

本卡完成集中审查、必要异常取证及完整差异回传。产品冻结，未修产品、未迁移、未重跑既有主要链。确定缺陷后停止依赖其正确性的正常恢复、删除和切换消费者，完成不受阻的代码、原件和控制核对。API 3/3、Browser 2/2 已到门，后续不再消费这两类资源。未完成门留给合并修正后的定向复核，不建议重新全仓、全部 G11 或无界变量组合测试。

这是审计者的判断与建议，不填写主控最终验收；不宣完整 NFR005、STEP018—020、M-1、项目或发布通过。

完整证据根为 [TASK-115/audit](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/audit/)。新写入仅在该根和本结果文件。DocuS、公共库、AGENTS、原始需求、产品源码、迁移、依赖锁、原测试、原构建和 TASK114 原证据未修改。

## 身份、输入和独立性

用户将 TASK115 人工转入当前全新会话。当前执行者为 Codex desktop，系统身份标签为 GPT-6，用户资源标签 A+。没有参与 TASK113/114 实现，没有使用其工程窗口、实现聊天、推理、自评或子 Agent；标签不冒充额外可验证的官方模型规格。

项目根为 D:/shspic/project_NO3_RetroLume-agent。依据 TASK115/R109、TASK-115-work-decision、STEP017-P1 已采用段及原完整合同执行。规则为 task_model、V4.0、公共 AGENTS CHG-0003；实际读入公共 AGENTS 全文和 WORK 适用 2/6/8 章。七个锁定指纹均匹配，没有采用后来规则。独立执行者不承担共享状态和最终裁定，不接管编排。

读取共享状态当前版本段时，意外看到主控候选摘要和对主要链的概括。此污染边界已在 commentary 和 control/receipt.json 登记。没有继续读 TASK114-result.md 或实施者自评；没有用该摘要证明通过。下面依据合同、实际代码、差异、原始方法和输出独立形成判断，且找出了原候选尚未关闭的问题。不能把本会话描述为从未见过主控摘要。

有效输入为需求 v1.2、架构 v1.27、执行动态 v2.51、阶段 07。原始需求用户维护，只读且未代写。合同 [current-contract.md](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-113/design/revision-01/current-contract.md) 为 81813 字节、SHA-256 8a56ebf3c1715895e3ee7a0dcf1f621b591335400e9898aa00df8cb2b7a61aaa，另读 B5 权限、格式及控制例、关系图和 TASK114 原目标／许可。示例文件只作合同，不能当运行原件。

身份核对见 [identity-before.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/audit/identity-before.json)、[frozen-and-as-run.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/audit/frozen-and-as-run.json) 和 [static-and-inheritance.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/audit/static-and-inheritance.json)。216 个当前文件为 212 源／配置／测试等登记项和 4 bundle 项，全部匹配当前封存副本；第 217 项是已移除旧 bundle 的登记，不伪造其当前文件。八个结果和十三个 FAIL 索引的 hash 匹配；存在的 C01 as-run 文件逐字节匹配。c01-fault-1135456156000000 因旧构建文件缺失未形成完整 manifest，保留此缺口。

001—013 共十三个受信迁移与产品固定摘要匹配，013 的十九个控制函数和九个业务 guard 的源码归一化摘要，共二十八项与产品固定指纹相符。这是 B 层身份核对，不冒当前数据库实查。

记忆只用于直接完成、复用充分证据和不虚签的操作偏好，候选事实全部由当前材料核对，不以历史记忆证明产品行为。

## 确定问题及合并最小修正

### F01 P1 取消收据会被后续成功终态覆盖

触发为用户取消在最后检查之后、不可逆发布／seal 或成功收据之前到达。[api.py](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/api.py) 的 cancel 将 prepared/running 直接写为 cancelled；[packages.py](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/packages.py) 和 [restore.py](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/restore.py) 随后读最新 revision，再写 published/verified，没有要求前状态仍然可成功。上传流也没有检查取消状态，收到 EOF 后继续发布并写 received。

补证为真实 ControlHub、文件、PackageReader 和冻结收尾函数；capture 输入、restore 工厂和最后 load 返回为明确受控边界，未运行真实 PG／Docker load。

- [01-restore-cancel-overwritten.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/audit/offline/attempt-03/01-restore-cancel-overwritten.json) 中先保存 cancelled，随后真实 verify 仍调用 seal 边界并返回 verified，revision 4。工厂／load 是替身，不称真实 target 已被取消后 seal。
- [02-publish-after-accepted-cancel.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/audit/offline/attempt-03/02-publish-after-accepted-cancel.json) 在真实 no-replace 调用前保存 cancelled，真实文件仍发布，最终 published，revision 5。
- [04-upload-after-accepted-cancel.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/audit/offline/attempt-03/04-upload-after-accepted-cancel.json) 在 ASGI 流 EOF 前接受取消，真实上传 handler 仍发布文件，最终 received，revision 3。ASGI receive 受控，不冒 TCP 中断。

source_delete 和 activate 同样对通用 cancel 开放，却没有执行者确认的取消线性化点。_confirm 在墓碑前后没有读取该取消门，_activate_readonly 在 selector_commit 前也不核取消。此两支为 B 层传播判断，未执行真实删除或切换反例。

影响 V19/V21/V24/V29，以及 V20/V22/V28 的不可逆点和准确 job 收尾。不能将“已请求取消”冒取消已完成，也不能把已确认取消覆盖成新的成功许可。

最小修正为同一 job 的取消请求、执行者确认和不可逆准入组成明确状态协议。在最后 load 后、seal 前、upload 验证／发布前、文件发布前、墓碑和 selector 准入前做相同资格核对，终态 CAS 同时校 revision 与允许的前状态。已进入不可逆点时给真实不可取消／结果待核状态，原键只读核对；已经发布的文件保留。取消先成立时阻止后续副作用和成功许可，准确目标失败封存与撤权，不能补写 verified。不要用持有 journal 锁等待整个文件／PG 操作的方式修复。

### F02 P1 operation_seconds 不覆盖快照之后的发布阶段

[snapshot.py](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/snapshot.py) 对 capture 计时，但 capture 返回后，ZIP 写入、PackageReader 全量校验、fsync／link、最终收据没有继承同一绝对截止。[packages.py](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/packages.py) 只核取消，未核总时间。restore 的 _load 又另起 started，allocate／初始化及之后 seal／证明不在这个总窗口中；此恢复传播为 B 判断。

[05-post-capture-operation-deadline.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/audit/offline/attempt-03/05-post-capture-operation-deadline.json) 使用可信低值 profile operation_seconds=1，在真实发布入口精确受控延迟 1.2 秒，实际耗时超过 1 秒仍返回 published。capture 为固定已完成输入，未冒真实 PG 快照或内核卡死。这证明发布阶段没有执行该限额，不能外推真实 2 GiB 吞吐或崩溃恢复。

影响 V19/V20/V21 的 Must 时间门，与 F01 一并修复但不共用错误结论。最小修正是 job 首次消费时固定绝对截止，向 capture、封装、校验、复制、组件、初始化和 seal 传播剩余量；在成功许可提交前再核。阻塞 I/O 和 PG timeout 与实际剩余量相称。超时后保留源、旧包和已发布事实，返回真实失败／未确认收据，不删除已发布文件来假称没有副作用。

### F03 P1 晚到 capabilities 响应回退全局数据身份

[context.tsx](D:/shspic/project_NO3_RetroLume-agent/frontend/src/data/context.tsx) 将整个 /api/data/ 前缀免于 namespace／响应上下文检查；[DataWorkspace.tsx](D:/shspic/project_NO3_RetroLume-agent/frontend/src/data/DataWorkspace.tsx) 的 refresh 无条件 setCaps 和 setDataContext。useEffect 的 alive 只用于 catch，不保护这些提交。相同 ControlHub 的历史 job 可跨数据集查询，capabilities 和 saved-records 却不能因此获得回退当前身份的资格。

[late-only/result.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/audit/browser/late-only/result.json) 为真实已有 Chromium 和冻结最终 bundle。两次能力 GET 反序到达，先接受 generation1 的只读实例，后接受 generation0 的旧 normal 实例，late_old_response_reverted_context=true，后续请求上下文也回到旧实例。全部回包由浏览器 route 夹具提供，没有实际后端 selector 切换、旧 Hub 写入或旧数据库回退。

已人工查看 [新上下文截图](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/audit/browser/late-only/01-new-context.png) 和 [旧响应到达截图](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/audit/browser/late-only/02-old-context.png)，后者只读告知及已保存记录区域消失。此反例不证明后端写围栏失守；后端拒写和真实选择器主链另有有效原件。

影响 V24/V29 的当前身份、草稿命名空间及晚到输出门。最小修正为 refresh 请求序号／取消及完整生命周期检查，同 control 的 generation 不允许下降；区分稳定 Hub 查询和依赖当前 dataset/instance 的数据查询。capabilities 采用新身份须有新鲜性依据，旧响应不得提交 caps、context、材料、计划或记录投影。保留旧键查询，避免为了修此缺陷切断跨切换核对。

### F04 P1 已删除依赖的记忆正文仍可被标 present

[api.py 的 saved_records](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/api.py) 在 memories 分支仅检查 learning_memories.state、body 存在和该 memory 自身墓碑，直接返回正文并标 present；没有核 source／event／upstream 依赖资格。该行没有 activity_id，前面的 activity_scope_sources 删除检测也不适用。

合法反例是 active memory 依赖某来源，随后删除该来源，或者尊重当前删除覆盖恢复旧备份。source deletion 保留记忆头、版本和历史，不自动调用 revoke；恢复仅把命中来源的 current_version 置 NULL，并不把所有依赖记忆头改 revoked。上述条件下 handler 仍返回 body。与原 [010_learning_memory.sql](D:/shspic/project_NO3_RetroLume-agent/backend/migrations/010_learning_memory.sql) 的 memory_revision_readable 对 source pointer/revision/hash 和上游／事件的失效规则，以及 B4 的恢复 DTO 删除屏障不符。

原合法样本来自已实核包 737bf7ba-18c2-436c-a011-3aabbc1a8b2b.rldata，SHA-256 45177d58ea58fcaa704bfdd48641aceade7ca6e6f4fe5d6759b3a46bf2671665。active memory 8149c454-3e1d-48cc-ab6e-37ef5dd7c570 当前版本2依赖 source 21d146e0-6cb9-454f-817a-60b30d8bb429／version 8cdff230-db23-454c-84a1-1240a05ce36b。反例只需之后使该 source 删除，不需要伪造非法 memory 行。原样行／body 输入身份见 [readonly-projection-input-02.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/audit/offline/readonly-projection-input-02.json)。没有对这个原 source 执行删除。

本项确定性来自 B 层分支和合法状态构造。首次异步 handler 夹具和随后同步 read 转移夹具均在外层 asyncio 运行中超时；第二次只保存了合法输入前缀，没有结果原件。原因尚未核清，不将其归为产品延迟，也不宣 handler 或 PG 动态通过。保留两次失败并停止该诊断，不机械第三次重跑。

影响 V13/V15/V16/V29 的资格和已删除正文抑制。最小修正是复用既有 memory_revision_readable／相同依赖资格和删除 overlay，保留头、原 hash、purge pending/done 与备份时点事实，正文不可回查且 availability 明确 dependency_invalid/source_deleted。并定向检查 learning/teaching/interview 的历史引用，不能只查活动当前 scope 来覆盖旧正文依赖。不得通过改头、撤销原历史或把 pending 改 done 来修 DTO。

## 代码、版本和主要证据继承

三表、三安全 view、四 NOLOGIN 角色、固定 search_path、PUBLIC EXECUTE 排除和 snapshot 白名单列有实际实现。data_loading_allowed 绑定 mode/loading、SESSION_USER、受信 source_snapshot_id 与 loader 成员，包 SET 不产生 loader。memory_body_guard 的 loading 普通 SELECT 只替代在线 FOR KEY SHARE，正文 hash/bytes/性质检查保留；在线行锁、immutable UPDATE/DELETE 和 memory_final_shape 未移除。两教学 FK 默认 IMMEDIATE，加载明确延后，当前 check_data_shape 还逐表／列／引用核其形状。此轴未发现放宽源码权限的新确定缺陷，九 guard 的普通在线逐支动态仍没有充分原件，不能将 frozen/无 DML 权限的 42501 代替它。

材料 TXT/MD 新建、替换、PDF 候选和 confirm 在 put/复用/verify 前取得 pin。仓储 save/create/confirm、PG ticket/nonce/epoch、引用同 COMMIT、target LoadingReferencePin 均逐入口核对。RootLease 是真实 Windows 文件对象锁；清理先独立确认取消旧 epoch，再另开 READ COMMITTED 事务取 PG 排他，以全部未删除来源的历史及候选版本为最后判据，未知不 unlink。源码与两个锁序／迟到 COMMIT 原件可严格归约；不把每个相同 put 入口重开一批。

单一 RR 连接以专用 snapshot LOGIN 读取28业务域和三个安全投影，数据库结束后仍持 shared RootLease 完成文件复制；memory body 删除由同连接 MVCC 观察。scope、outcome、settle、墓碑采用同事务的机制继承为 B，原真实 T 后替换提供 A 级实例。并未逐项动态执行这些变体或断线，因此不会把它们签成逐分支 A。

ZIP_STORED、EOCD 目录限额、成员白名单、CRC/SHA/长度、行/类型 codec、metadata 排除、原件 hash、required 缺失及 no-replace 有实际实现。manifest 不自引用，摘要不冒作者可信或执行权。已读原包测试方法及日志，新 A1 仅补恰边界／超一和明确失败点。没有实际制造 reparse/junction、真实磁盘崩溃、全组件故障或真实丢 COMMIT；两处脚本输出的 outside_write_count/sentinel_unchanged 为夹具声明，缺单独前后 sentinel 原件，只按 C/B 对待，不作为全文件系统零写的 A 证明。

工厂只能读本机固定 profile；新空集群受信001—013、真实受限 loader、完整关系和正文／额度逐列对账、seal 撤 loader/admin 登录及 loader 成员、只读实际读取／拒写都有原件。failed 目标不可被 target() 作为 sealed 使用；部分初始化缺 loader 时 admin 仍撤销的修正及真实 probe 可继承。没有在审计中启动 failed target 或用旧管理员／loader。

ControlHub 完整 COMMIT/hash 链是长期 job/selector 权威，source 镜像与 archive_history 不授活权限。只读调用原 _read/replay 核107个完整事件、无断尾；没有调用会写旧 ACL／根的构造器。selector generation1 绑定 target07，原 fence=frozen；这是原日志及原 PG 观察与冻结字节的组合，当前未连 PG 重新核 mode。全部 public/internal 写入口、producer/admit/dispatch、worker/preview 的 owned 登记、close lane、后台清理和 mode gate按真实增量审查；close lane 只用于已有收尾。未知 owned 不自动解围，selected target 不可用不回源 normal。

以下原批次目录均为 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-01/batches 下的实际原件，详细路径及摘要在审计身份文件中。

- c01-restore-1131663078000000 的 03a/03b/03c/05/06/07 有新 target05 全迁移、94 行、4 原件、14 组件和 sealed 角色证据。当前 _load、seal、包／codec、文件及引用核心相同；后续 _initialize 加入精确 shape 核对、abandon 修部分初始化，不能称整文件未变。target07/08 的后续成功初始化和 source shape 反例覆盖新增核对。
- c01-source-1133792718000000 有 snapshot 禁写／控制秘密／删除函数拒绝、source SET 不能授 loading、两项 shape 负例、真实 T 后替换、共享删除、pending 注入和同键清理重试。source 是非空升级及前向函数修正，不能冒新空 source 一次安装。
- c01-race-1134754921000000 及其明确引用的前缀有准确 D 最后检查窗口、B/D 两序、实际 client 退出而 PG flush 后迟到 COMMIT、双 EOF、第二次查询保共享文件。取消确认 unknown 为准确注入边界，不称实际 PG 取消 COMMIT 已未知。reference/files/originals、墓碑窗口和取消协议未变；删除错误分类及只读错误优先级改变不削弱这些事实。
- c01-fault-1138756812000000 为独立 fault 集群，非空004/005、已有010/011角色反例真实 P0001。不是普通 snapshot 因权限不足的代用品；负例 rollback 明确，集群之后失败封存。
- c01-overlay-1139001578000000 及其原前缀对 target07/08 比较 respect_current 与 snapshot_only：只读可回查差异、源墓碑不撤、preview 3/0/60 账和31域只读拒写。不代表 F04 的全部依赖正文资格已正确。
- c01-integrate-1139419843000000 的真实有限 SUP、准确 Job/owned、双 EOF／结束、未结束 owned 阻切、selector 已 COMMIT 后注入失去返回、同键同 generation、28表拒写保留。该批最后 HTTP 失败不使前缀消失。c01-integrate-1139729250000000 对最终主入口补真实 TCP 和最终 bundle Browser。
- c01-harden-1139975718000000 核部分初始化 admin 撤权、真实坏尾／中段文件拒绝、selected target/source 均不可用时真实 TCP 旧键／旧包可查且不回源。当前相关函数 AST 无增量。secret scan 实际范围为三个包；没有把它扩大成所有 HTTP／普通日志也已扫过。

## 原合同 V01—V29 充分性并列清单

下列 A 为原始真实运行或本卡真实文件／TCP／Browser 层，B 为实际源码／身份／严格机制继承，受控注入逐项注明。未动态不自动要求新批；只有影响原 Must 的缺口或实际修正传播才安排补验。

- V01。原义为全28表、原件／PDF／补充／作答及独立解读。原包与原全量加载、文本/hash/引用导航有 A；固定 codec/README/关系为 B。正常合成闭包充分，未签任意规模或任意语义引用质量；本卡未重跑。
- V02。原义为 teaching/interview/model/memory/HTML 正文联接，旧 received 无正文不补 usage。原 _load 对94行逐列 codec 回读及正文摘要为 A+B，operation5/results4 的合法旧缺正文保留。正常样本充分；F04 涉及资格投影，不能因此认旧正文当前可用。
- V03。原义为真实 T 前后替换、scope/outcome/settle 及断线整次失败。实际 T 后替换和原 spool 为 A；单 RR 同连接及无重接路径为 B，其他值变体可归约到同 T 机制。断线没有独立动态原件，标未动态，不能称跑过所有四类并发提交。
- V04。原义为准确最后检查/unlink窗口、两锁序、共享引用、进程死/迟到 COMMIT、epoch 取消未知。原两序、client 退出、PG 提交行、EOF/文件及锁等待为 A；unknown 取消为受控注入；各引用入口共用 pin/PG ticket 为 B。正常准确清理机制充分，不重复 TXT/MD/PDF/直接元数据的相同锁实现；旧 epoch 拒绝分支没有独立完整 SQLSTATE 原件。
- V05。原义为 pending/confirmed/skipped PDF、逐页补充和删除资格。原3候选、6提取页、2核对/2补充的恢复对账为 A，既有解析和页纪律按未变实现继承。保存状态保真充分，不冒重解析；删除后的旧正文／资格需随 F04 检查。
- V06。原义为真实独立新 cluster、受限 load、文件/关系/正文对账和 HTTP。target05/07/08 完整加载、seal、最后31域和 TCP/Browser 是 A，最终实现差异已逐函数说明。主要正常链充分，F01 的取消和 V21 异常不被该结果关闭。
- V07。原义为非空迁移、已有 role、错函数/约束/列/编码 profile。004/005及010/011碰撞是实际负例 A；错 factory profile 无分配及缺 trigger/错 parent FK 有原件；精准函数/角色/codec 身份为 B。其他约束／列／函数异常的逐项动态未齐，原同一检查机制可继承部分，不能一括动态通过。
- V08。原义为九历史 INSERT 分支、旧 goal/obsolete/committed/supersedes/body/HTML/预算与两 FK，普通在线反例及 immutable纪律。合法全量 loader 对账为 A，九分支限定条件和在线原逻辑为 B。普通角色合法通过共同准入后触发每个专门 guard 的 A 缺失；frozen/无 DML 权限42501不能替代。保留这一具体门。
- V09。原义为 loading 自授拒绝、source 不授 loader、目标 seal 拒 DML/退款和撤权。source SET false、snapshot负例、sealed readonly 三项真实42501和角色/成员观察为 A+B。已测权限充分；不把普通 readonly 的权限拒绝冒旧拥有者或旧 StopProof 真正退款函数分支执行。
- V10。原义为四账、execution_generation、M/R/S/last_settle及旧 received 保真不退款。原逐列 load/checksum和 account rows为 A，归档 executor/owner 转换及禁止认领为 B。主要快照保真充分，未恢复支付/工具资格，旧UNKNOWN保持。
- V11。原义为 stopped/failed_unstarted/cleanup_unconfirmed 和 preview starts/S/R，旧 StopProof/PID/CID不退款。三状态、3次/0结算/60预留和转换清单有 A；旧控制字段不入 codec及readonly拒写为 B。保真充分，未实执伪 StopProof 退款专门分支，不操作旧25。
- V12。原义为备份后 source 增长/unknown，旧快照不造新可消费额度。源 latest 与旧包、只读冻结事实有 A+B；所有账逐列保真而执行权未迁。没有单独对每类新增消耗/unknown逐值动态，按相同冻结机制继承；不宣多机预算保证。
- V13。原义为旧 source/goal/parent/memory/cancelled/dispatch_closed/旧答案资格。既有领域 eligibility未变为 B，删除覆盖和只读回查有 A。F04 在新 saved-records 投影绕过资格，故本项不充分，需修正并定向核历史依赖。
- V14。原义为共享原件删除、非共享 pending、同键重试/修订不重复和包/WAL保留。source组及两序有 A，准确根/键/大小与无递归GC为 B。该正常/受控失败清理机制充分；用户取消删除事务边界属于 F01 静态传播，不能用本项替代。
- V15。原义为 revoke/purge pending/done、排除 revoked body、旧选择闭包及不伪清理成功。原恢复排除 revoked body、保 head/command/revision/purge facts为 A+B，旧 M3不重写。F04 的 source/upstream/event invalid active body DTO 尚未满足，故资格/正文部分不充分。
- V16。原义为默认 respect_current 和明确 snapshot_only、源墓碑不撤、unknown不称最新并集。原 target07/08策略对照及 readonly为 A，prepare谱系/latest unknown为 B。source命中和自身memory撤销覆盖充分；依赖正文的 F04 不通过，unknown用户确认的全部交互变体未动态。
- V17。原义为截断/损坏/错 SHA/CRC/长度/缺 required/unknown availability及合法缺省区分。原真实 ZIP 反例与固定 codec方法可继承；本卡补一字节截断、低值目录/成员/manifest/文件刚好与超一。已执行具体文件分支充分，不宣所有成员组合／关系损坏变体都动态执行。
- V18。原义为绝对/UNC/盘符/../反斜杠/ADS/大小写重名/链接/reparse/嵌套/压缩炸弹/EOCD和目标外零写。实际 ZIP reader拒八种路径/结构为 A，白名单、不 extract、准确普通文件/根/no-replace 为 B。真实 reparse/link 与外部 sentinel前后实测未齐；固定拒压缩可归约压缩炸弹准入，不冒真实巨大包吞吐或全部目标外文件都已动态核零写。
- V19。原义为 bytes/member/JSON/row/component/time恰界/超一、用户cancel、上传中断及准确job/旧成果。本卡四文件限额与行长度/行数恰界/超一为 A；F01 三个取消收尾和 F02 后段时间失败为反例。JSON depth／组件限额和 TCP 上传中断未完整动态，当前不通过。
- V20。原义为 spool/copy/fsync/no-replace/收据断点、原键补确认不复制、保存和访问区分。本卡真实文件发布后受控 Hub收据失败，published_unconfirmed，同键 file_publication=confirmed，capture_calls=1、同文件hash不变，为该分支 A。spool/copy/fsync逐点失败未全齐；F01/F02 阻此门，不以已有正常保存替代。
- V21。原义为组件中断/DB拒绝/文件损坏后failed目标不可读、不复用、源旧包保留。原受限 load 42501失败、fault目标封存、abandon修正和target()状态门为 A+B。F01 load后取消仍 seal/verified反例不通过；真实多组件中断及 seal后故障未齐，只需定向补此影响。
- V22。原义为verified前拒 activate、owned/停线不足不换、selector失败不解围及永久readonly。原owned未结束阻切、真实源frozen、selector同键代次1及后端拒写为 A+B。F01通用取消对activate的传播未关；selector成功但回应丢失是注入，未执行真正 journal selector_commit失败负例，保留区别。
- V23。原义为 DSN/key/session/DPAPI/control/private path不进包/普通DTO/错误/日志，正文不无痕清洗。原三个包对真实合成凭据needle扫描为 A；safe codec/DTO/fixed error/public job白名单为 B。新 HTTP fixture未注入真实秘密来签全扫描，原 HTTP/log marker矩阵不足；不将包扫描扩大成所有公开面已动态扫过。
- V24。原义为真实丢回应、同键重复/hash冲突、刷新和晚到/切换只GET原键。原selector lost-return同代次为受控A，本卡真实TCP POST 202后浏览器受控 abort，刷新GET同job且未自动第二POST，有前缀A。HTTP hash冲突请求实际发出，但夹具错误未保存/断言该响应，不签动态通过；F01取消与F03晚到不通过。
- V25。原义为草稿不进服务器包、独立未提交下载、旧编辑身份不迁/刷新不POST。原最终bundle Browser草稿IDB/localStorage下载及GET-only刷新为 A，字段/namespace和明确未提交为 B。本卡未重跑已充分主链；F03污染namespace需修后定向核，不以草稿下载通过签上下文晚到正确。
- V26。原义为角色、文件、HTTP、UI、as-run/manifest一体绑定及准确收尾，必要独审无开放Must问题方可建议关闭。身份和原件可读、原六CID及本卡停止有 A/B，完整本报告已交付。存在四P1及必要余项，本项不满足关闭条件，最终裁定留主控。
- V27。原义为31安全域同T最小snapshot权限、控制秘密拒读、目标新身份/archive history/tombstones及撤loader。source专用角色负例、同RR和目标新身份/31读/撤权为 A+B。不同domain值的同T可归约同连接机制；墓碑/操作镜像变化和断线未逐支A，不说多个GET构成同T。
- V28。原义为source不可用/切换后同Hub原key/包/收据、cache坏/断尾/中段坏、半注册和selector丢回应同代次。原真实文件日志负例、跨切换和target不可用TCP、原key/包及selector注入为 A+B。cache只按日志读取，未由缓存授新权；credential/target半注册的全部故障点未全齐。文件已发布无收据同键不复制由本卡补证，F01不可逆收尾尚未关闭。
- V29。原义为全部公开/内部新写fence、owned真实结束、unknown不解围、模式/旧owner/draft不恢复权及永久readonly。原28表拒写、真实SUP和owned阻切、sourcefrozen/targetreadonly/Hub选择、最后TCP/Browser为 A，内部调用和模式/代次门为 B。未发现后端回源或恢复执行权的确定缺陷；F01/F03/F04使取消、当前身份和正文资格部分不通过，不能宣全部持续恢复Must。

## 实际补证、失败和资源账

本卡原始新方法计划见 [method-plan.md](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/audit/method-plan.md)，实际事件及 argv/UTC/mono在 [control/events.jsonl](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/audit/control/events.jsonl)，计数和补账在 [control/receipt.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/audit/control/receipt.json)。所有 FAIL 保留，没有删除、覆盖测试或弱化断言。

- A1 使用 run_offline.py／offline_cases.py。初轮 bytes digest错误为夹具 AttributeError；修正后默认沙箱在私有 hardlink处 WinError5；自动审查允许精确审计根文件运行后第三次 exit0，保存6个方法及逐阶段原件。三次离线子进程 1.703、0.813、3.047秒，共5.563秒。修正的只是本卡夹具，原产品无改动。
- D1 使用 run_network.py／api_fixture.py／browser_cases.mjs。第一API启动后事件字段kind冲突为夹具 TypeError；第二使用系统Python缺项目httpx为夹具错误；均准确停止，计数不返还。第三改用已有backend/.venv，真实API18115和Browser工作；完成真实丢回应／同原key GET前缀后，浏览器夹具将Fetch Response.status误作方法而失败，原前缀和stderr保留。
- API额度3/3到门后没有再启API。仅消费尚余第二Browser，通过 run_browser_only.py／browser_late_only.mjs加载原dist文件并route输入，exit0，保存晚到反例。没有新TCP服务器，没有冒后端真正selector切换。原HTTP hash冲突和取消UI流程未走到最终断言，不签通过。
- B1 使用 run_projection.py／readonly_projection_case.py。两次60秒超时，记录60.032和60.015秒含进程结束开销；第二次只保存合法原样行输入，未有结果。根因未核清，没有将方法超时写成产品行为FAIL，也未换PG/开放旧权限来绕过。相关动态诊断停止。其 root.resume误标A1，原事件保留，按独立新增诊断单元保守补扣第三根，未倒填伪begin或返还失败。
- 静态身份脚本 inventory.py 首次遇一失败目录缺as-run manifest，随后按实际缺件登记；元数据查找/脚本失败不冒业务执行。首个CIM默认沙箱拒绝，升级只读核查获允许；开跑前实际可用2.9913GiB达到2GiB门，之后每次真实API/Browser再核。自动审批没有拒绝本卡动作，没有降门或关闭用户软件。

当前保守扣额为3/4根，source create0/2、成功0/1、source start0/3、target07 readonly start0/2，API3/3、Browser2/2。Native/SUP、preview、build、安装、镜像pull、模型/provider、费用、公网及Git写全部0。未建新审计PG／卷、未使用旧readonly凭据，也未启动source/failed target；产品问题已阻关闭，未为了完整PASS继续消费不必要的真实PG主链。

API/Browser按登记点的观测持有13.220秒。因为Popen至登记有小间隔，最终从每次root/resume（早于创建）到准确consumer.end对各资源分别连续保守扣14.874秒，见 [holding-reconciliation.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/audit/control/holding-reconciliation.json)。这不是精确净持有，低于业务2100/总2400秒，清场300秒未挪作新增业务。实际补证离线子进程累计125.610秒；普通元数据／读审命令另属活动工时，不能声称全部执行准备耗时已逐子进程精确采样。

首工具UTC/mono未同时落盘是本卡控制偏差。实际记录点为2026-10-13T06:22:36.073640Z／1144022781000000ns，之前不补造精确锚点。最终活动／日历用许可保存2026-10-13T06:16:24.914938Z作为早于接受的保守起点，并按记录后的单调观察取较大上界；全部间隔连续计，没有自行暂停。实际收尾计时和余量见 delivery.json，不把48小时日历或旧墙时冒净投入。

## 原 TASK114 执行控制独立判断

旧根18/18、PG create/success6、start27/32、Windows11/12、API5/8、Browser3/6、build3/6、preview/Vite/provider/fee0保留。原control/events及receipt身份与输入登记一致；本卡不借其余时、slot或物理余额。

首轮 real_roots=7 实为七目录的错误。closure budget-reconciliation-note 保留8个PG资源批、1个Windows锁批和 target-saved创建前失败分类，C01采用保守10基线加8新根至18，没有重新把7当真实根返额。本卡认可前向保守限制，但不能据此追认首轮根计数正确。

旧55525.796为日历观测，净活动unknown。C01封存9185.438秒是保存时点观察；budget-final实际记9739.953秒，不能遗漏后续保存工时，也不能称它等于所有接受前后精确投入。原早期created至首次begin的1158.657秒另记，载入的377.280持有不证明此前所有准备已按同一计量口径完整纳入。保持unknown/分列事实，不改旧账。

十三个C01 FAIL为原实际尝试，逐个读其failure.txt/SQLSTATE及原方法。memory_body_guard 的真实42501到loading专用普通SELECT修正后目标加载成功；竞态夹具的边界等待／共享影响变化到fresh impact确认；HTTP readonly错误优先级到最后主入口；Browser失败到最终bundle方法；failed bootstrap admin撤权均有具体传播和原件。不把generic RuntimeError计为相同产品根因。多次before_create/before_start内存失败与原样本及门检查一起保留，新采样到门才继续；不能用结果PASS证明停止/资格控制从未偏差，尤其无完整首轮argv和净活动的旧段仍无法全签。

原所有失败和根本原因修正计数没有清零。没有发现可据充分记录确定的生产模型/权限/用户数据越界；原目录误计、首dist pre缺失、旧PG命令缺完整argv、一个失败as-run缺件及部分旧记录乱码属于证据/控制限制。旧源码归档、G11/25/UNKNOWN/R60/count1/13元/626.566等不重开、不改写、不退款。本卡也不将自己的两次诊断超时或夹具错误覆盖成通过。

## 当前冻结与停止事实

[stop-metadata.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-115/audit/control/stop-metadata.json) 是2026-10-13T07:24:05.894045Z的只读实查。原准确source、target04/05/06/07/08六CID全部Running=false/Pid0；本卡audit容器名字不存在，15451/18115无TCP状态，本卡脚本进程／已登记父子候选为空。两个Browser均有await context.close事件、准确Chromium根birth的结束观察以及runner结束。没有用runner退出单独代替停止核对，未全局kill/stop/prune或触碰旧25。

受保护前后逐字节清单包括原source/backup/control/restore-root文件、旧control receipt/events、原包和当前源码/bundle，最终比较见 delivery.json。该比较是实际文件身份，不是当前PG mode/账的再次SQL查询。原selector、journal、credential密文和预算原件保持，不能由停止状态推导source自动恢复normal。

## 最小下一步与交回归属

主控将 F01—F04 一次合并交原TASK114工程窗口，只修实际问题及受影响测试。本卡不改源码，不生成TASK116或新许可，原114已结束18/18许可不能自行复活。STEP017-P1采用无需重复批准；新增实际修复和运行资源由主控按真实剩余范围另给精确前向合同。

修后最小复核覆盖取消与成功准入的三个已证点及 source_delete/activate传播、同一绝对总截止、最终bundle反序caps和旧namespace/草稿、默认删除overlay下依赖记忆/历史正文不可回查。上述反例先转为正确断言，再对实际改动层给真实PG/文件/TCP/Browser证据。F04异步夹具的环境/loop问题应先定位，以已有受信本机方法或新明确合成源验证，不以mock或旧frozen角色42501替代。

剩余原Must补证只针对V08普通在线九guard共同准入后的拒绝、V18真实reparse/外部sentinel、V19深度/组件/上传中断、V20spool/copy/fsync故障、V21/28半注册/seal/selector拒绝点和V23实际HTTP/普通日志secret marker等确需运行的机制缺口。可以按相同实现/对象字节和原证据严格归约，不要求逐值组合；修复若未触及正常恢复、准确引用清理和原SUP/G11，不重跑那些完整链。

DocuS更新和主控最终裁定由编排者完成。本卡建议保持TASK114/STEP017未关闭，保留全部未验证和历史事实；本次必要人工仅将此结果路径带回主控。没有新增经验库或记忆写入。
