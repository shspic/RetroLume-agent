# TASK-108 / R-102 — G11 HTML宿主与学习接线合同

A—D设计合同已交付；唯一推荐为既定独立容器、可信wrapper与受限子frame、容器外监督、有限画面和输入，配套新HTML生成与持久资格；G11-P为待采用建议，自身全协议导航的创建前/提交前守卫仍是实现卡内前置缺口，未关闭B-01或STEP015/016。

交付身份：项目根 D:/shspic/project_NO3_RetroLume-agent，入口 AGENTS.md；task_model V4.0，公共AGENTS CHG-0003；需求1.1、架构1.00、执行动态2.22、阶段07。接收标签A+，本聊天连续承接业务上下文；实际可确认身份为Codex、系统描述基于GPT-6，部署型号后缀与实际推理档位没有可核信息，不用A+推定。未派子Agent。规则指纹核对见证据，未采用后来版本。

许可 TASK-108-G11-DESIGN-20261008，首次读卡2026-10-08 15:40:45 UTC，2026-10-08 23:40:45 +08:00。既有固定单调起点和截止保留于 design/session.json，续作不清零。此次仅阅读、hash、函数AST定位、精确镜像元数据、六个官方页面及文稿；产品运行、产品写入、费用和Git写入均为0。

## A 当前事实与唯一最小选择

### A1 复用、缺失和新建

FR009要求抽象概念的实际计算、图形和交互，以及资料、知识点或错题难点的来源关联。SEC003允许计算与图形JS，禁止页面获得网络、文件、系统、模型或业务工具能力。NFR001要求来源与语义准确性分别核证；NFR002/003要求单次键、可见有限额度、取消和UNKNOWN不自动重发；NFR004要求冻结有辨别力的代表样本。这些Must保持。

当前正式产品没有 backend/app/preview/ 或 frontend/src/explanations/ 实现。service_config.py的 quota_preview 是既有活动额度说明，不是HTML预览功能，记忆修改的 preview_change 也不是HTML宿主。FILE010已计划上述两个目录；DATA008和API007尚未落地。deploy/start_local.py当前只管理既有资料应用和精确本地数据库，不提供受限HTML生命周期。

确定复用：原学习与教学不可变成果、来源scope和资格、007调用收据/正文、原请求/工具/费用/原生运行时间四账、单次键、admit/mark/结果COMMIT、本机意图核对、引用回查、Windows原生模型监督与UNKNOWN纪律。G3—G10未变证据有效；TASK106/107有限验收已关闭，DEF024/025/026和E106-SEM不重开，O107-01/02仅保留历史观察。真实provider质量、完整向量、全Must、M-1和发布没有通过。

044归档报告和任务卡可读，仅是只读候选Review。D:/shuice12/RetroLume-SPIKE-017及原host、energy.html、probability.html原件已确认不可达；本卡没有还原、执行或重认旧八例。报告中的旧hash、路径与失败保持历史含义。本合同提出新代表页与计算oracle，不声称与旧原件逐字节等同。

本机精确基础镜像 sha256:c091b21d9fae78c76e85cd4356431e9b018402f172a214fc7d7a5e9a7e29d8ac 有缓存，元数据为linux/amd64、2026-07-30创建，默认User未指定。inspect未读容器内包或执行浏览器，不证明非root、sandbox、包版本和可运行性。frontend声明/锁及本地playwright-core包为1.62.1，browsers.json描述Chromium151.0.7922.34、revision1234；这证明包描述身份，不能代替镜像内实际加载身份。

需要新建：HTML专用profile和父成果适配器、不可变产物与命令、预览持久预算/会话、严格API007、隔离镜像和可信宿主、容器外监督/救援、画面客户端与可访问的有限控制。以下所有新字段、文件、SQL与运行参数都是下一卡的合同建议，本卡没有实现。

### A2 推荐拓扑与可信锚

主应用React工作台 → 本地FastAPI HTML资格/API → 独立的宿主机PreviewSupervisor进程 → Docker CLI参数数组的create/start/attach/kill/inspect → 非root预览容器的可信Node宿主 → 保留Chromium sandbox的浏览器 → 可信空白wrapper → 仅 sandbox="allow-scripts" 的唯一不可信srcdoc子frame。

另有宿主机PreviewReaper进程持有专用CID登记和硬截止，独立于FastAPI请求、PreviewSupervisor和容器。主应用浏览器只显示有界PNG和可信应用文本，输入通过有限协议回传。Docker控制端留在宿主机；容器既无socket，也无应用令牌、DSN、资料原件、公共提示词库、OPEN_project或旧SPIKE依赖。容器内Node进程和协议输出是可信程序，生成HTML及其DOM、console、postMessage、readout均为不可信数据。

iframe的sandbox属性由容器内可信wrapper在注入前设置，只含allow-scripts；不给allow-popups、allow-same-origin、allow-top-navigation及其用户激活变体、allow-forms、allow-downloads、modals、pointer-lock、presentation或存储权限。父/顶层的真实数据不在wrapper内。跨源隔离和不提供父消息命令桥保护父DOM；所有message、console和dialog均无命令解释器，dialog直接dismiss。容器权限、宿主命令种类、停止权和额度由应用配置与监督器决定，模型manifest不得改变。

B-01候选可信锚是浏览器实施的辅助浏览上下文sandbox拒绝分支，发生在新顶层目标创建之前；不是window.open覆写、点击脚本、CSP截图、page事件关闭或Target.autoAttach暂停。[HTML目标选择规范](https://html.spec.whatwg.org/multipage/document-sequences.html)支持这一候选；固定151浏览器的动态性质仍须H0证明。

H0必须以同一固定浏览器、同一真实鼠标/键盘输入，先在无害测试对照中成功创建新页，再在受限子frame拒绝window.open、target blank、新命名target和form target。冻结夹具不覆写window.open，不用evaluate里的click模拟用户。记录可信宿主实际发送的鼠标/键盘事件、无害对照isTrusted/激活标记、引擎目标/页面/root frame事件和前后集合；页面自报只作辅助。生产初始稳定集合为一个page、一个root frame、一个HTML子frame，不把正常初始子frame误计为违规新页。

### A3 权限逐项边界与准确缺口

自身导航是独立缺口。HTML sandbox不禁止导航自身；[导航许可规范](https://html.spec.whatwg.org/multipage/browsing-the-web.html)的自身目标分支明确允许。location赋值、anchor自身目标、meta refresh、history和data/blob/file/http导航不能靠popup拒绝推导关闭。网络路由只能覆盖实际进入拦截器的请求；本地 protocol.d.ts的 frameRequestedNavigation 是通知，不是同步否决API。收到frameNavigated再停止属于已发生后检测，不能签默认禁止导航。

因此正式宿主必须有 NavigationGate：只允许可信宿主一次建立空白wrapper和一次注入指定子frame文档；之后所有非bootstrap导航，包括同文档URL变更、data/blob/file/http/https及新子frame，必须在浏览器创建/提交相应文档或目标前否决。此接口是必需实现性质，不是已发现的Playwright现成API。本卡读取范围内没有足以证明151对全部这些路径同步否决的锚。不能把这个缺口藏在普通超时配置中。

最小证伪路径：固定sandbox子frame中的真实点击把自身location指向带独特标记的data页面，再试由页面构造的blob页面；独立观察frame/loader/document身份是否变化及标记是否执行。任一提交即失败，哪怕无外网、最终页面仍受sandbox或随后被kill。H0优先核这两条，避免先耗费完整业务运行。若现有固定版本路由确不能满足，宿主、画面接线及HTML安全放行停在H0；可以完成不依赖运行的生成/持久合同实现，能力保持关闭。唯一必要替代是浏览器进程内的原生导航/目标否决组件，须另报同一G11-P的准确增量、固定源码/构建及成本后再采用；不在本包暗装CEF、Electron或浏览器fork，不接受新增页面权限来替代事实。

HTTP/HTTPS与容器回环：注入前 context.route 的全URL谓词一律abort，不转发、fulfill外部内容或访问宿主；serviceWorkers="block"。network=none只作外层出站隔离，不阻止回环，容器不得启动HTTP/WebSocket/CDP TCP监听服务；Playwright经浏览器进程管道通信。[BrowserContext官方说明](https://playwright.dev/docs/api/class-browsercontext)提示网络路由与service worker范围，并要求在创建页面前配置WebSocket路由。本合同的routeWebSocket全URL处理直接close且不connectToServer；这两层的实际零请求仍须固定版本观察。

file和运行时文件：不提供file导航或文件上传接口；file URL请求必须由NavigationGate/实际路由在读取前拒绝，input file不在有限控制集合，filechooser事件取消，绝不setInputFiles。只读根目录防写，不能证明防读；临时目录与只读镜像仍含运行时文件，必须以容器内无秘密哨兵反例核文件读取，不靠“没有宿主挂载”签通过。data/blob作为导航拒绝；首版只允许直接内嵌PNG图片数据，其他资源连接和worker由wrapper固定CSP收紧，CSP仅纵深防护。

下载：iframe不授allow-downloads，同时由可信宿主向明确BrowserContext发送 Browser.setDownloadBehavior(behavior="deny", eventsEnabled=true)，检查方法成功、下载事件及文件结果。API参数存在于本地固定包protocol.d.ts；当前tot Page官方页仅能读到方法索引，不能替代151兼容与阻断证明。下载事件到来后的cancel只是补救，不能当默认拒绝已经成立。

父/顶层导航、新iframe、网络、文件、下载每项均有独立H0观察，不互相替签。新iframe的创建前拒绝同样没有现成证明，frame-src 'none'与静态拒绝frame标签只作收紧，动态创建空白iframe须检验引擎frame数量。这里若失败，和自身导航一样停止宿主放行，不能把B-01窄新页通过扩大成整份SEC003通过。

### A4 依赖、版本与离线重建

候选组合保持Playwright1.62.1、Chromium151.0.7922.34、上述缓存基础digest，不追随当前Docker文档的1.64.0示例。[Playwright Docker说明](https://playwright.dev/docs/docker)说明镜像不含Playwright npm包，默认root会禁用浏览器sandbox，并提供namespace所需seccomp建议；这是测试/开发基础镜像，不是现成的产品安全认证。

新增 deploy/preview/Dockerfile、package.json与package-lock.json、host.cjs、seccomp.json、wrapper.html、依赖/加载manifest和LICENSES。以精确缓存digest为FROM，把有校验的playwright-core1.62.1及必要npm依赖包与可信宿主复制到构建上下文，禁止由产品运行自动npm install或下载浏览器。使用镜像既有Node仅在将来构建阶段查清实际版本/许可并冻结，要求Node>=20、与Playwright兼容；不凭User/OCI标签推定Node版本。依赖缺离线包时，下一卡只可按采用包显式取得固定npm tarball/官方源码及SHA，来源变更不能自动落入已缓存许可。

Playwright本地许可Apache-2.0已读；浏览器本体和第三方、Node、Ubuntu组件的实际license/NOTICE清单须从未来真实构建原件收录，未读镜像内容不签清单齐全。代码和构建入口在产品目录，构建manifest保留FROM digest、完整lock/hash、Node/npm版本、browser二进制hash、revision、真实version输出、宿主/wrapper/seccomp hash及最终image ID。启用能力前全部匹配固定部署清单；不按latest/tag、动态路径、公共库或实验路径加载。

本地类型和bundle确认chromiumSandbox默认false且会追加no-sandbox，正式launch必须显式chromiumSandbox:true并检查实际argv无禁sandbox参数。默认disable-popup-blocking参数也存在；H0对照须说明实际argv，候选生产配置移除该单一默认参数，不能依赖普通popup blocker代替sandbox。不得加SYS_ADMIN、privileged、host IPC/network、宿主目录或关闭seccomp来解决启动失败。私有IPC与有界SHM能否保留sandbox由H0核，失败就停相关依赖。

## B 唯一完整合同

### B1 显式生成与冻结输入

新增API入口 POST /api/activities/{activity_id}/html/commands。strict、extra=forbid，body仅有 business_key(UUID)、parent、focus、expected_config_sha256、confirmed=true。配置hash由当前能力响应提供，服务锁内比较不符即409且不准入。父选择是有判别字段的联合：learning含operation_id、payload_sha256、segment_index；teaching含record_id、body_sha256、point_id可空。focus限1024字符/4096 UTF-8字节，whole HTTP body限8192字节；布尔与数值拒绝字符串和bool混入数字。用户选择父对象与难点是一次明示动作，不随学习刷新自动生成。

learning适配器只接受本活动仍合格、已提交的learning.v1 answer及合法segment；clarification/no_evidence/conflict不当已核结论，提示先澄清。teaching适配器接受本活动仍current的exercise或feedback记录；反馈沿其answer/exercise/point的原依赖闭包核对，知识点必须属于实际记录。当前RECORD_KINDS没有explanation类型，解释从exercise/feedback已有内容投影，不新增虚构knowledge_point表或解释实体。teaching.v2记忆依赖须全量传递原固定选择与body hash，不能删记忆字段降级v1。首版HTML不读取interview、工具结果、历史失效记录或另建全局用户记忆选择，拒绝这些父类不影响原领域。

服务器冻结 activity_id、goal/goal_version、scope_revision、排序规范化的source版本/原件hash、父kind/ID/body hash/依赖闭包、难点文本、有限catalog、model身份、html配置版本/hash、运行预算快照。源scope排序只在新HTML规范化投影执行，不借机修改O107-01旧行为。父摘要<=4096字节，catalog至多8条/累计12288字节，教学引用闭包至多12个记录；原闭包更大不能截断变合格，返回html_context_limit。父输入摘要、catalog和说明按已用证据装配函数受限读取，原PDF/整份资料和DSN不进入模型之外的HTML容器。输入规范JSON的UTF-8 SHA256称request_sha256，冻结上下文另有context_sha256；相同业务键的输入字段或hash不同返回409，保留原命令。

新HTML规范JSON固定sort_keys=true、紧凑逗号/冒号、ensure_ascii=false、allow_nan=false、UTF-8无BOM；UUID规范小写、整数严格不接受bool，十进制控件参数为有限规范字符串，禁止负零/多种等价拼写造成同键歧义。原领域canonical/hash不改。learning父沿原ResultConsumptionRef核同activity/正文hash；teaching父及v2闭包由HtmlCallBinding的专用适配器核，不能伪造TeachingCallBinding。带固定记忆选择的活动使用新HTML记忆资格传导分支，在admit、mark、commit和公开读逐点核同一选择/版本/依赖，缺完整绑定拒绝；不把新profile误送旧只接受teaching绑定的入口。

新增受信 HtmlGenerationProfile(profile="html_explanation.v1")、HtmlCallBinding 和 AdmissionIntent.html_binding、ModelCallRequest.html_profile；在gateway从可信profile构造binding，公共body不能传profile、messages、model、tools、执行权限或deadline。原operation kind仍model，新增专用前缀 html11m.{business_key的32位hex}。profile与learning/teaching/interview互斥，固定两条message、JSON_OBJECT、allowed_tools为空。该新角色/绑定是G11-P实质新增，不能冒用learning.v1的256 token输出限。

命令接受事务先核父/源和配置、写不可变输入意图；admit、mark_sending和结果提交各自按原事务锁序重新核资格和binding。生成的请求数、费用预留/收到结算、工具数0、原生运行时间完全走原四账。HTML生成不旁路受控模型链，不在Node容器调用模型，不隐式工具调用，不隐藏重试。建议HTML输出上限4096 tokens，且不超过活动与服务已有显式上限；上限不足即能力关闭或预检拒绝，不静默扩旧预算。请求body仍<=65536、OneCall完整线包仍<=131072，配置更小取更小。

模型输出严格结构：schema、title、concept、html、controls、readouts、calculation_notes、limitations、citations。schema仅html_explanation.output.v1；title<=128字符，concept<=1024，html非空且UTF-8<=24576；首版资源直接嵌入html，仅data PNG，解码累计<=8192字节、至多4张，各<=640x480。不支持引用外部script/CSS/font/import或资源文件路径。whole model JSON UTF-8<=49152，catalog和持久封套共同仍在007的131072字节上限内。含NUL、无效UTF-8、重复JSON key、错误引用、超界数据或不受支持控件拒绝为invalid_html_output，不截断成成功。

controls至多8个，id为 hctl_ 加1..24个ASCII字母数字或下划线、全局唯一，kind为number/button/range；label<=80、description<=256，数值min/max/step/default必须有限且相容，十进制字符表示<=24字节。range要求(max-min)/step为整数且<=100，固定Home/方向键最多100步到值，超界不支持；不使用任意页面脚本设置值。readouts至多8个，id采用 hout_ 同规则，label<=80、unit<=24，显示值后续<=128字节。manifest只是有限控件/显示数据，不是权限申请。计算说明至多4条，含formula文本<=512、适用域/误差/至少一个正常与一个边界样例、citation IDs；程序计算仍由HTML执行，后端不eval、不运行脚本、不以模型自评签数学或安全。

HTML静态解析仅查编码/结构/尺寸/允许资源及manifest目标，不执行DOM/JS；静态检查通过命名为structural_valid。concept_verified仅可由未来冻结oracle的实际交互得到，并记录实际输入/读值和来源；host_policy_verified仅可绑定已审计的固定宿主加载manifest。模型输出不含可生效的验证布尔、trusted或新页面权限。

### B2 不可变产物、COMMIT与资格

提议012_html_explanations.sql四个新表，007保持原收据/结算事实。

- html_commands：PK(activity_id,business_key)，唯一operation_id；不可变request/context hash、父选择/闭包、source_scope、goal/scope/config版本、model身份、有限输入封套；有限launch/outcome状态，更新时间和首次失败码。只允许accepted→launch_claimed→terminal，失败/UNKNOWN不复活。
- html_artifacts：artifact_id UUID，唯一command/operation；不可变version=1、parent/goal/scope/config/source引用、原始HTML/manifest/计算说明/limitations、byte counts、artifact_sha256、execution_package_sha256、body_sha256及创建时间。与007合格正文在同一事务插入，没有UPDATE/DELETE正文权。新生成是新artifact/version链的行，不覆盖旧行。
- html_preview_budgets：每activity一行，首建冻结配置/hash、max_starts、max_seconds、starts_used、settled_seconds、reserved_seconds、revision。只计HTML预览；不是替代原模型时间账。默认建议3次/180秒，首次建行后配置变化不加额度、不清零。
- html_preview_sessions：preview_id UUID、activity/artifact/hash、start_key UUID、preview_generation、command_nonce、owner_id/owner_key_sha256/boot_id、CID、image/load hash、配置hash、墙钟记录与进程内固定单调deadline、额度reserve、有限状态和停止收据。唯一(activity,start_key)，一个activity至多一个未确认会话；物理运行全局也至多一个，见B4。身份/CID/初始截止仅能从null一次写入，停止收据首次写入后不可覆盖。

command的terminal_disposition仅succeeded/invalid_output/not_sent/unknown/refused。preview状态仅reserved、registered、start_requested、ready、running、stopping、stopped、failed_unstarted、cleanup_unconfirmed；ready→running仅首次合法输入，用户未操作亦照原截止停止。stopped/failed_unstarted不得重启；cleanup_unconfirmed只可补确认后到stopped或failed_unstarted，不恢复ready/running。preview_generation在activity预算锁下严格递增，不复用；每会话的状态revision递增，故障/停止原件摘要每条<=4096字节、累计<=24576，异常原stderr只存有限摘要与证据定位，不以页面字符串填可信状态。

artifact_sha256覆盖规范UTF-8的html、manifest、计算说明、引用及限制；body_sha256覆盖完整持久业务封套，沿用原正文hash语义。版本、hash、原模型结果和原始HTML不因资格变化而更新。历史列表只返回有限元数据与history_only/source_invalid/cancelled/expired/integrity_error/unconfirmed等资格，不把旧产物当当前解释。

收到模型响应时，新HTML语义校验、绑定复核、007 _write_outcome、html_artifacts插入和command terminal写入在原 record_outcome 的同一connection/COMMIT中；不能先保存artifact再结算或另起连接补写。trigger核对前缀、普通模型kind、合法command、RECEIVED合格正文、封套hash和全部父/源依赖；rollback则007与artifact都不提交。收到但结构非法保留原真实调用/收费事实，无可用artifact；UNKNOWN保留原预留且没有成功artifact。模型费用与调用事实不由preview状态代结算。

相同terminal收据严格相等的重入不重复插行，不重复退款，不用新的来源版本改写原事实；已提交artifact身份不一致则报integrity_error并屏蔽公开正文。网络回包丢失先按原business_key GET核对，服务器读同键持久状态，不再发模型。接受意图而未claim可以由用户显式同键恢复，经原子claim和新资格检查至多首次派发；launch_claimed、sending、UNKNOWN绝不自动或显式重新派发同一次执行。服务器或客户端恢复默认只读。

新 html_artifact_eligible(activity,artifact)在同一个SQL资格快照核活动未取消/到期、原scope/current来源/原件身份、父正文/依赖仍current、artifact与007/command身份和所需schema完整。teaching替换、修订、答题依赖或记忆失效按原资格闭包传播；learning原不可变父不用虚构“替换”事件，来源变化/父hash或资格变化足以失效。SQL异常/未知schema按unconfirmed拒绝，不回退裸HTML。

读取/输入/帧交付都有各自资格线性化点：锁内查询与封套复核成功的时刻。帧先进入监督器有界缓存，公开GET在取候选帧后、序列化发送前重新读资格，提交失效发生在该检查前必须拒绝和丢帧。检查之后已进入传输的有限字节不可撤回；客户端代次守卫和下一次资格读取清空旧画面，不宣称能撤销此前合法的在途字节。不持DB锁等待浏览器、Docker或网络发送。

新增来源/父资格观察器每250ms有界核对，单次DB上限1秒；确认失效或DB不可核立即撤销输入/画面服务、发高优先级停止。运行授权有效期至多1秒且不得越总deadline，无法续核不继续运行。已开始容器终止有物理停止余量，不能把资格关闭时刻当容器已空。旧成果事实保留，失效时不得展示原HTML、历史截图或旧readout为当前成果。

### B3 公开API与有限管道

全部沿用 _guard/X-RetroLume-Session 和UUID校验，只供本地应用，no-store/nosniff，无跨源授权。以下是新的API007语义，待G11-P采用；生成HTML不成为text/html响应或主应用srcdoc。

- POST .../html/commands 仅B1输入；返回activity/key/operation、命令状态、artifact_id可空、read_status、四账与原监督摘要，不返回未核HTML。GET .../html/commands/{key}核对同键，并返回有限accepted_input(parent/focus/config hash/request hash)供意图比对，无模型上下文或秘密；GET .../html/artifacts?cursor=...默认20条元数据且全JSON<=65536，GET .../html/artifacts/{id}返回合格解释的title、controls、readouts定义、说明/引用/limitations及资格，不公开raw html字段。
- POST .../html/artifacts/{id}/previews 仅start_key、expected_artifact_sha256、input_owner_key、confirmed=true，body<=2048字节；input_owner_key是当前面板在内存产生的32字节随机值，服务器仅保存SHA256，与本activity/preview/generation绑定，不传模型或容器。资格/预算/物理owner通过后返回preview_id/generation、owner_id、状态、固定有效截止与显示额度。相同键及相同owner key返回同一会话事实，不另建CID；同键异owner key409。GET .../html/previews/{id}读取状态和预算，不返回owner key，绝不恢复启动。source_invalid为409、能力缺失为503、大小413、速率429，控制状态未知以明确unconfirmed字段返回。
- GET .../html/previews/{id}/frames?generation=N&after_seq=S 返回一个最新PNG的application/octet-stream及有限可信响应头：preview ID、generation、artifact hash、frame seq、width/height和sha256；无画面为204，失效拒绝。只在匹配的当前会话发送；请求1秒超时，不阻塞停止。主浏览器仅decode PNG，不接SVG/HTML/任意data URL。
- POST .../html/previews/{id}/inputs 仅preview_generation、seq、payload_sha256、event；body<=1024字节，事件联合为click(x,y)、key(key)、set_number(control_id,value)和activate(control_id)。坐标整数0..639/0..479，key仅Tab/ShiftTab/Enter/Space/四方向/Home/End/Backspace及单个数字、小数点、负号，无Ctrl/Alt/Meta、浏览器快捷键、任意文本、剪贴板或文件。数字拒绝NaN/Inf，范围与step来自已核manifest。range通过固定有限值适配器操作，禁止传入CSS selector/JS表达式。
- POST .../html/previews/{id}/stop 仅generation、stop_key、reason(user/back_to_learning)；幂等，物理停止为异步状态，不用HTTP200假称已停止。活动取消后的stop仍允许针对该精确已登记会话，其他输入/画面已拒绝。应用退出/资格失败的停止来自监督器，无需再由失效页面提交业务授权。

HTTP与内部输入两次校验：API检查session/owner/activity/generation/hash/资格/速率，监督器检查已登记状态、固定deadline、schema、seq和长度，Node只接受可信监督器的有限命令。客户端ID仅索引，不能指定image、CID、Docker参数、URL、路径、CDP method、selector、evaluate或工具。停止队列独立且优先，不被大量输入占满。

frames/inputs的HTTP请求另带X-RetroLume-Preview-Owner，由服务器按持久hash核当前输入owner；拥有普通API会话只能读元数据和停止，不能从GET取得输入权。owner key不写localStorage或HTML意图账，卸载/刷新销毁，因此刷新不会接管旧运行；可只读核对并停止，再显式新键打开。stop不依赖owner key，保留同一应用用户取消/失联收尾能力。owner_id是可信状态身份，不能仅把可读ID当授权。

跨Docker采用create后start -a -i的匿名stdin/stdout管道；不publish端口、不exec每次输入、不拼shell字符串。宿主机按参数数组启动固定Docker CLI，精确CID由create回包取得。容器entrypoint为固定Node宿主，不接运行命令或路径。包从stdin传入内存一次，不写宿主或挂目录；PNG编码与浏览器临时profile只用有限tmpfs。

管道采用4字节网络序头长度+UTF-8 JSON头+头内body_bytes指定的有界binary体，不以换行或页面文本划分消息。头含protocol="retrolume.preview.v1"、type、preview_id、generation、artifact_sha256、channel_nonce、seq、body_bytes、body_sha256，头<=2048字节，初始化包<=65536字节，输入体<=1024，status<=4096，PNG<=524288。启动随机channel_nonce由可信父进程送给固定Node宿主，后续头核nonce；它只是该匿名管道的防串会话标记，不是应用凭据，也不交给页面。channel_nonce与input_owner_key都以32字节值的64位小写hex表达，后者hash核原始32字节，绝不发给容器。JSON拒绝未知字段/重复key/坏UTF-8/负长度；长度先查上界再分配内存。

init body只含schema、html、controls、readouts及固定viewport；整体SHA256由监督器核已提交artifact的对应执行投影，另保留artifact完整hash身份。不传catalog、父模型封套、源ID/版本记录、原文文件、DB结果或应用/owner令牌；HTML本身允许必要的解释文本，但不夹带整份原始资料。Node核包hash后以内存注入一次，ready必须带image加载manifest hash、sandbox/guard安装摘要及固定两帧基线。ready摘要不代替H0票据。

init/ready的seq=0；input/ack共用输入seq，frame使用独立frame seq，status使用独立递增status seq，stop使用自己的幂等stop_key而不等待输入ACK。input body为规范event对象，公开payload_sha256等于该body_bytes的SHA256。frame头另有format="png"、width=640、height=480；status body只含state、封闭reason_code、last_input_seq、有限readouts与单调剩余毫秒，不接受页面决定deadline。readout值为字符串，至多8个/累计1024字节，schema其他字段一律拒绝。

host→supervisor只允许ready/frame/status/input_ack；supervisor→host只允许init/input/stop。DOM、console和postMessage不进入上述parser。Node自己的stdout专属协议；子页面console只丢弃或写有界stderr摘要，不拼接原文到stdout；浏览器进程stderr另行限长，不继承到协议输出。stdio源的OS进程/管道身份才是可信锚，页面喊“ready”或伪造JSON没有写这个管道的能力。

输入seq从1递增、每次最多一个未ACK；相同seq同hash只回已记ACK，不重做click，相同seq异hash或跳号/乱序拒绝，重连不回放未确认输入。节点收到ACK不等于正确概念或预算结算。frame seq独立递增，DPR=1、viewport640x480、最多3fps、每秒<=1572864字节；保留最新及一个在途帧，丢弃中间帧。ACK/读值和截图被busy JS阻塞超过2秒触发停止，不排无限队列。尺寸/hash/编码不符、大帧、协议伪造直接进入stopping；输入最多20次/秒，超率拒绝且持续一秒违规停止，单会话最多1200个输入。主浏览器再校验ID/代次/hash/seq、PNG签名和解码尺寸后替换画面。

### B4 时间、物理停止与预算

推荐给预览单独、显式的新资源额度，避免把Windows Job的已有停止证明套给Docker。默认每activity至多3次启动、累计180秒，每次reserve最多60秒；不足最低启动/停止余量即拒绝。预览不计模型请求/工具/费用，不改旧max_running_seconds；UI明确显示“模型执行剩余”和“交互预览剩余/剩余次数”，不能把新额度隐藏成旧活动免费无限能力。这项新增时间/频次主权是G11-P的一部分，尚未生效。

html_preview_budgets与sessions在activity锁内原子reserve，starts_used在预扣获准时加1，不因创建失败退次数，避免无限create重试；剩余秒数是max_seconds减settled与reserved。未知物理树保留全额reserve并封闭新预览；确认未启动或精确停止后按监督器单调实耗结算，unused仅退回这个preview预算。原调用数、费用、工具和模型时间绝不由此退款。刷新、重连、更改配置、换活动面板或重新启动应用不清零持久累积。

应用主机同时只有一个PreviewReaper/全局预览owner，采用进程外的命名互斥和boot_id，并持有最多一个CID。数据库会话记录不替代物理互斥。命名互斥持有者死亡、登记不全、过期或Docker不可达不构成新的执行资格；恢复先精确停止已知CID并确认，不能靠租约过期抢占。旧模型链仍按其原四账/Windows Job规则独立准入，不因预览unknown伪称整个活动树已停止；HTML再生成/打开由新服务对本活动未确认预览失败关闭。主应用的原学习只读和停止保持可用。

PreviewReaper先完成READY和专用登记日志同步成功，Supervisor才能create。create使用固定image ID、固定名称由preview_id/generation派生、专用labels与随机command_nonce；不按名称模糊查找、杀全部容器或删用户资源。取得精确CID后，原子登记于监督器/救援日志和sessions，Reaper确认其接管及固定deadline，之后才允许start。DB写失败或ack未确认不start，精确停止已取得CID。create回包丢失时只按本次固定名称、nonce/labels和image严格找回自己的唯一创建结果；找不到或多结果为ownership_unconfirmed，不再create、不start、不清理其他容器。

固定单调起点t0在预算reserve前建立，SQL/owner准备上限3秒计本会话总耗；runtime截止D=t0+min(60,实际reserve)秒；ready截止min(t0+8秒,D-10秒)，交互截止D-10秒，开始stop后2秒软停止、随后Docker kill，最迟D完成预期物理确认；额外诊断/去掉已停止专用容器上限15秒，不延长D，不允许在diagnostic时继续HTML运行。输入、frame、heartbeat、重连均不延后任何截止。若有效窗口不足8+10秒，拒绝物理启动并按确认未启动结算。

Supervisor外部循环与Node/浏览器分离，每250ms核截止/资格/owner/控制连接，Docker调用单次<=2秒，最终停止确认循环受D或固定清理截止约束。Node忙循环、浏览器hang、全容器无响应时仍能Docker kill精确CID。Supervisor每秒向Reaper发有界存活消息；Reaper在2秒失联或Supervisor进程身份死亡时按既定CID/截止立即kill并确认。Reaper丢失时Supervisor立即停止；FastAPI生命周期控制器也保存登记副本，在观察Reaper死亡时触发同一精确CID救援，禁止新的预览。

停止证据必须同时包含CID/image/nonce身份，Docker stop/kill原回包，Running=false及State.Pid=0、无Restarting、无restart policy，attach/stdio与监督器拥有的CLI进程已结束，以及当前固定Docker/Linux平台对该容器cgroup无残余任务的可核证明。普通API stop返回、Exited标签、浏览器close回包或配置inspect各自不充分；下一卡须验证该平台的容器停止事件/任务消失观察与kill语义，若无可靠cgroup空证据，标tree_unconfirmed，不把字段拼接成证明。不得启动特权辅助容器、挂宿主cgroup或开放socket以换取证明。

应用Ctrl+C/正常退出先关新准入，再通知Reaper和Supervisor停止，有限等待确认再结束控制进程。UI关闭或控制连接丢失2秒同样停止，不在后台恢复画面。监督器全部死亡、宿主断电、Docker daemon卡死或内核不可用时，应用不能保证容器按D物理停止；持久态cleanup_unconfirmed、reserve不退、HTML能力关闭，直到授权后按登记精确确认。应用下次启动只读核对/救援，不再生成或启动，不声称配置time limit能独立抵抗宿主监督全失效。

### B5 工作台、正常交互与可访问性

LearningResult合法答案段、TeachingWorkspace已有知识点/练习/反馈旁新增“交互解释”入口，带出原activity/parent身份；不能在interview历史或失效结果旁显示可执行入口。生成确认区展示难点、资料版本/引用、一次模型调用和剩余额度；状态为预检拒绝/等待/结果未确认/生成失败/已保存未打开。等待时保留旧有效学习成果，失败不把截图或静态回答冒充互动。

用户显式打开已保存且合格产物，显示独立画面、title、来源、原限制、preview剩余时间/次数，以及常驻停止和回到学习按钮。正常页面数字输入或range导致计算与图形刷新，按钮/键盘操作在640x480远端viewport内执行；主页面不eval、不直接挂HTML。窗口缩放只按已知比例转换点击坐标；无滚轮/任意键通道，画面外点击拒绝。

可信React控件根据合格manifest提供有label的number/range/button、键盘焦点顺序和文本readouts。数值输入走set_number，按钮走有限activate，range走有界步进或固定数值适配器；Node只按验证的id构造精确escaped-ID定位和固定动作，不运行客户端表达式。显示读值由Node对已登记hout元素读取textContent/value，限长、只作escaped文本，aria-live节流至1秒；来源于页面的数值明确是展示数据，不作为正确性、权限、预算或学习答题的权威。未来oracle实际核数值与图形，页面自报不签概念正确。

主界面停止按钮在远端挂死时仍可用；Escape只用于离开本地画面焦点，不转成浏览器全局快捷键。Tab/ShiftTab可在可信控件和画面区之间移动，无键盘陷阱；学习侧引用继续使用原引用回查/PDF展示而非容器文件上传。readout与图形说明提供文本替代，不承诺整份远端DOM的任意屏幕阅读支持；若首版两代表页无法用可信控件完成全部必要操作，不能判可用通过。

“停止并回到学习”即刻切回原activity/parent只读位置，显示停止中；确认后允许新的HTML启动，未确认时保留清理状态和同键核对，不显示已停止。取消活动撤销输入/画面并请求精确停止，已提交产物事实保留但当前正文/画面被抑制。恢复只GET命令/artifact/会话/额度，未完成本机意图核对后不自动POST或复用remote input seq。

前端HTML面板使用 mount_generation、activity_id、parent ID/hash、owner_id、view_generation、preview_id、preview_generation、artifact hash、request seq与AbortController。切活动、父变化、卸载、失效、停止时先递增本地代次、撤销输入/读图、清画面与readouts，再处理异步响应；HTTP成功/失败、PNG解码完成和引用回包均先比较整组身份。隐藏页停止控制连接并请求停止，不只暂停截图；另一标签页最多只读，显式当前owner才可输入/停止，可幂等停止已有owner会话但不能接管输入。无独立HTML下载、外部分发或可信源加载功能。

### B6 配置和有限容量

新增html_generation与html_preview两个独立LayerState，默认未配置关闭；旧create/continue/learning/teaching/interview能力不因新配置缺失而关闭。generation须新profile/schema、原模型服务/四账可用；preview须012完整schema/ACL指纹、H0通过及稳定点审计签收、精确image/load manifest、监督/救援可用。用户实际HTML生成/打开入口要求两层均可用，避免生成付出后得到不能交互的产物；未核宿主时仅获准实施/合成验证内部生成与存储，历史元数据仍可读。未来获准的隔离合成验证实例在卡面固定许可内验证候选，不把测试配置冒充用户放行票据或默认配置；因此独立终审可读到真实正常闭环原件而不要求先签未验候选。缺字段、坏布尔、非有限参数、未知schema、依赖或安全票据hash不匹配分别显示原因，绝不裸HTML降级或偷偷更新镜像。旧ActivityConfig字段输出不无条件新增空值到旧profile封套。

建议首版固定：generation输出4096 tokens及B1大小；preview每活动3次/180秒，每次60秒，startup8/准备3/交互ACK2/软停止2/诊断15秒，640x480/DPR1/3fps。容器user固定UID/GID10001，cap-drop=ALL、no-new-privileges，network=none、无port/mount/socket、read-only、restart=no、init回收，CPU1、memory768MiB且memory-swap相同、pids128、private IPC、SHM64MiB、tmpfs /tmp128MiB与运行时home32MiB均nosuid/nodev、无额外宿主可写目录。seccomp以固定Docker默认基线与Chromium所需最小namespace调用差异审阅并冻结；noexec临时挂载是否兼容实际浏览器须H0核，不默认允许可执行文件或放宽安全配置。

这些是需下一卡冻结的合理首版建议，不是已生效额度。给两个交互概念、有限数字控件和一小幅图形留空间，不支持视频、WebGL大场景、字体下载、任意文件或worker型功能。资源不足只报明确失败；不根据页面自报自动增mem/PIDs/帧率/time。没有新Redis、队列平台、通用远程浏览器服务或Agent平台。

构建依赖manifest记录输入源/包/二进制/wrapper/seccomp身份，容器ready回报这一内嵌清单hash；构建后外部部署manifest另把最终image ID绑定到它，避免image ID写入自身镜像形成循环hash。完整Chromium可执行路径在未来构建与首次H0 ready核实后固定，不靠PATH/环境选择headless-shell或Canary。依赖/版本/sandbox检查并入首次获准H0容器，不另启动“准备”容器。

### B7 四条手工轨迹

以下是文档事件推演，不是程序、SQL、浏览器或安全测试。

轨迹1，正常生成/交互/回学习：用户在current父成果上以K确认难点 → 服务冻结输入并提交command accepted，尚无模型收费 → 原生监督/四账准入、mark与一次响应 → record_outcome同COMMIT写007和artifact A，真实收据结算，原时间按原监督收尾 → 用户以P显式打开A，预览预算reserve60且次数+1，Reaper登记精确CID后start → ready/数字输入/新画面各核代次与资格 → 用户停止，界面回原学习；监督证明精确树空后结算实耗并释放本preview未用秒数。下一动作由用户发起；页面从未取得调用/停止权。模型已发送和产物COMMIT分别是不可撤销事实。

轨迹2，提交丢响应/恢复：K的模型响应和artifact已COMMIT，HTTP断线 → 本机intent留unconfirmed，不改预算 → 刷新只GET K，比较原parent/focus/config输入hash → 找到同一个artifact则清意图、显示已保存未打开，无第二次模型请求、无容器 → 若命令仅accepted可由用户显式同键首次claim；若launch_claimed/UNKNOWN只显示原状态和预留，不重发。P启动回包丢失亦只读原会话；CID未知或ready未确认时走停止核对，不新建。

轨迹3，失效/取消与迟到画面：A/CID运行，frame F先在缓存 → 来源或父修订/取消COMMIT → F公开检查若在失效后则拒绝，观察器关输入并停止CID；原artifact/007不改、preview reserve待物理确认 → 即使旧HTTP/PNG解码后来成功，UI身份代次已变，不能复活画面/readout/意图；失效前已合法发出的少量字节不可撤回 → 用户在新活动只能显式选择新父/新键生成，旧source资格不被新scope冒认。预算事实与停止证据各自处理。

轨迹4，恶意页/宿主失联：恶意导航/新页先由原生guard否决；若H0发现实际创建/提交，能力不放行 → 已合格宿主中恶意协议/大帧/无限循环触发停止，Node不需要成功处理stop → Supervisor按精确CID外部kill；Supervisor崩溃由Reaper使用原deadline执行 → 若Docker与停止证明可达，留原事件并结算preview实耗；若不可达，cleanup_unconfirmed且全reserve保留，禁止新预览，不假称Linux树空或给旧费用退款。原学习只读可用；全监督失效的物理期限不保证如实显示。

## C 最小完整实施与G11-P待采用包

### C1 文件与实际复用接口

以下路径均相对项目根；没有创建这些产品文件。

- 新 backend/app/preview/contracts.py：strict输入、父联合、HtmlGenerationProfile/Binding、输出/产物/会话/有限协议；generation.py：显式生成、冻结父/来源、同键恢复与受控一次模型；repository.py：012命令/产物/预算/会话同事务方法；api.py：B3全部严格公开入口与有界读取；host_policy.py：加载manifest/H0审计票据、能力失败关闭；supervisor.py/reaper.py：宿主机双进程精确CID/截止/管道/停止收据，禁止公有任意Docker执行接口。
- 新 backend/migrations/012_html_explanations.sql：四表、约束/身份与状态触发器、资格函数、最小owner/app权限和schema识别材料；不改001—011原件或旧行。新 backend/config/html.example.json及配置说明，只含安全固定建议，不覆盖本机private配置。
- 新 deploy/preview/ 下的A4构建文件、依赖锁/离线清单、wrapper/host/协议说明和许可证；未来镜像构建产物hash由实施证据冻结，不在设计卡生成dist或镜像。
- 新 frontend/src/explanations/HtmlExplanationPanel.tsx、PreviewCanvas.tsx、htmlApi.ts、htmlIntents.ts、contracts.ts及必要样式，承载完整生成/核对/存储/显式打开/有限输入/停止/恢复/引用/可访问性。新HTML本机意图键独立、只存用户parent/focus/key/config hash，不存令牌、HTML或模型正文。
- 修改 backend/app/capabilities/contracts.py、gateway.py：仅新增html可选类型/binding、互斥、固定消息与输出校验；旧profile排除None序列化保持。修改 backend/app/activities/repository.py：Mixin接入、新前缀在admit/mark/record_outcome/read资格的薄扩展，同connection hook；原公共方法签名不变。对html11m的记忆资格路由到新HTML专用适配器，旧_memory_require_call和教学/面试绑定主体不变；新SQL复用原记忆资格函数核v2闭包。新HTML不能被旧generic continue/learning followup/teaching/interview消费，明确拒绝html11m父，不能泛化为普通model成果。
- 修改 backend/app/service_config.py、main.py及activities/api.py能力投影：新增两个LayerState、配置/012/schema/加载身份检查、新router和生命周期监督收尾；新增域失效不屏蔽旧能力。修改 frontend/src/activities/ActivityWorkspace.tsx、LearningResult.tsx、TeachingWorkspace.tsx，必要时仅给TeachingExercise.tsx/TeachingFeedback.tsx加父选择回调：合法父入口、HTML面板与整组迟到守卫，不修O107-01/02或重写旧意图/引用实现。修改 deploy/start_local.py与Windows启动说明：新预览控制器启动/正常退出精确清理，不在用户普通启动时安装、pull或迁移。

实际函数级复用依据：PostgresAdmissionLedger.admit(intent)位于repository.py:1086，mark入口与同一锁序见AST索引；record_outcome(permit,outcome):1689、_write_outcome(connection,...):1658、read_committed_result(activity_id,operation_id):1805、cancel_activity(activity_id):851、read_operation:2275。新HTML hook必须处于其真实connection内，不能由GenerationService随后补COMMIT。ActivityService.cancel_activity:292目前仅封装ledger取消，新preview观察器负责精确物理停止，不能把该返回直接显示成树空。

LearningService.execute(activity_id,business_key,text,config,parent_operation_id=None,run_tag):30和reconcile:23保留；HTML新GenerationService.generate(activity_id,command,config,run_tag)及reconcile(activity_id,business_key)不扩普通learning参数。TeachingService.read_record:116与ledger.read_teaching_record:1497提供current/body/hash身份，父冻结参考现有_load_teaching_entities:310，不能读取history_only public_body当当前上下文。原LearningResult.showCitation:46有sequence+abort身份；ActivityWorkspace的mounted/selected/seq和轮询守卫复用模式而非借用同一个seq变量。

worker/one_call.py:218的run_one_call(ledger,config,activity_id,executor_id,operation_id,request,service,run_tag)及launcher.py:274的run_supervised_window(...,one_call=None,tool_action=None)签名保持，新的html_profile须穿过原OneCall严格式/大小/无工具验证；SessionConfig和原WindowLedger不转成Docker停止主权。PreviewSupervisor.run(session_identity,validated_artifact,preview_config,deadline_ns)是新的内部有限入口，传入非秘密产物及批准控制配置，不复用WorkerCommand字符串执行Docker。

### C2 SQL、角色与兼容降级

参照011实际owner/app模式，新建NOLOGIN、无superuser/createdb/createrole/replication/bypassrls的 retrolume_html_owner 与 retrolume_html_app；具体部署LOGIN仅获后一角色。四表/触发器/资格函数由owner拥有，PUBLIC撤全部新表权和新函数EXECUTE；app只获各必要列/表的SELECT、command/sessions/budget的受约束INSERT/UPDATE、artifact INSERT，无DELETE/TRUNCATE和artifact UPDATE，触发器同时校验身份与合法状态。owner对旧资料/活动/007/教学/记忆仅获资格/插入校验必需的SELECT或已许可资格函数EXECUTE，无旧表写权；不给容器DB身份或迁移角色。

必要数据库函数明确职责：html_artifact_eligible的SQL资格快照；html_command_guard冻结输入/claim/terminal；html_artifact_insert_guard核007/command/父/源封套；html_artifact_immutable_guard拒绝UPDATE/DELETE；html_preview_budget_guard核固定上限、非负及session预扣/结算；html_preview_session_guard核不可改ID/CID/截止/状态/收据。需要SECURITY DEFINER的跨表检查只用于上述有限校验，固定search_path=pg_catalog,public、对象全限定、owner最小权限、撤PUBLIC；不提供动态SQL、任意表名、删数据或系统能力。

预扣/结算和session改变同一activity锁/同connection，budget.revision CAS及未确认会话唯一约束防并发超发。source→活动→原父操作/教学依赖→html_command/artifact→budget→session为固定加锁顺序，领域已有source/memory/teaching锁顺序先行；不得让资格函数从新锁反向获得旧域锁。迁移与真实catalog/函数/ACL指纹整体识别，absence关闭HTML域、partial/unknown关闭且不猜结构；不是仅检测一张表存在。

无012时旧活动、007、learning.v1、teaching.v1/v2、interview.v1继续按已有schema兼容识别；新前缀/profile在不支持进程中拒绝，不把None写进旧v1封套。旧普通读取默认65536 JSON上界和007131072正文边界保持；HTML metadata/details受单独受限投影，不给旧全域泛读增加rawHTML；旧DB事实不迁移到HTML、不清除历史FAIL/UNKNOWN或预算。停用只关闭新能力、停止精确CID并保留新旧事实；逆迁移、数据删除和旧ACL回滚不是默认许可。

### C3 唯一G11-P采用包

G11-P尚未批准。供编排核证并在确需时一次交用户决定的实质新增对象是：html_explanation.v1生成角色/父消费隔离；012四表/两NOLOGIN角色/上述校验函数与权；API007新增生成/产物/预览/有限输入/停止；固定Playwright npm运行依赖与产品镜像/最小seccomp差异；独立宿主机Supervisor/Reaper的精确Docker控制；持久预览3次/180秒预算及可访问画面客户端。

建议批准的动作范围是下一完整卡在上述产品文件实现、接线、普通卡内修复，并在新合成资源上执行D的最小定向验证及一次稳定点独立安全审计。安装/取得固定npm tarball、构建派生镜像、创建/启动新的合成PG和精确预览容器、应用/HTTP/真实浏览器/原生受控模型替身，都须下一卡列实际根、identity、次数、截止及cleanup额度后才有效；本设计许可不授权这些动作。缓存基础可复用，不需现在pull；若需补离线包，限定官方包源、固定版本/hash和下载对象，不许可运行时外网或页面网络。

保持禁止：原HTML不进主应用浏览器；无新页面/文件/工具权限，无root/no-sandbox/privileged/SYS_ADMIN/host IPC/network/挂载/socket/端口；不读真实资料/private配置、真实provider或密钥，不外发用户数据、不计费调用、不删除数据/逆迁移、不启动旧106/103/100/088资源、不改DocuS/公共库/原需求、不Git/发布。原FR009和独立Docker方向已有批准，不重复呈请同一选择。B01和全协议导航守卫未核，不能把G11-P的采用当运行安全票据。

代价是四表和一个隔离资源域、每次最多60秒独立浏览器、有限画面性能及运行依赖许可清单；回滚为能力关闭、精确停止和保留事实。原生导航组件替代若必需，不在此候选包无成本默认允许；H0失败带回最小证伪原件和明确浏览器层差异，编排裁定是否扩大同包，不能连续盲换依赖。此处是具体技术缺口处置，不新增一串参数审批或恢复旧实验套件。

## D 未来最小验证与一次独立终审

### D1 冻结、正常页与资源建议

本节全为未来计划，当前not_run。下一完整卡冻结最终源/迁移/lock、基础与派生image ID、真实Node/Chromium版本和二进制hash、host/wrapper/seccomp/协议schema、012真实catalog/ACL、frontend实际加载bundle。不得用声明版本、旧044hash或旧Windows Job收据替代当前加载原件。H0在实现卡内先执行；安全条件不成立则相关宿主接线停用，非依赖工作可交付，不将整个设计阶段再拆成泛读审计卡。

新的合成资料冻结两份短文与source版本/hash/页行位置：N1机械能，定义E=mgh、g=9.8，m/h有限非负范围0..10，N2二项概率，定义独立试验恰k成功 P=C(n,k)p^k(1-p)^(n-k)，n整数1..5、k整数0..n、p∈[0,1]。二者计算oracle由冻结原文公式与独立手算保存；这只是两类代表性概念，不冒全学科/provider质量。

N1实际交互输入(m,h)=(2,3)，显示58.8 J；改h=0显示0且图形高度/能量柱更新；改m=0,h=3仍0；负数由可信控件拒绝且图形不发生非法更新。N2输入(n,k,p)=(3,2,0.5)，显示0.375；p=0,k=0显示1，p=1,k=3显示1，p=1,k=2显示0；计算采用适用的边界定义，不用0^0的JS偶然值；k>n或p>1拒绝。保存每次输入、ACK、页面可见数值/图形观察和独立预期，容差1e-9，不能仅截图或静态写58.8/0.375判交互通过。

未来建议资源上界：一个新的隔离合成PG17实例，用main及同实例内升级/缺schema合成数据库，精确image/卷/CID由下一卡冻结，其他旧库保持停止；一个本地API实例/端口，一个受控模型传输替身、一个Windows原生控制链；一个主应用浏览器持久会话最多1800秒；一个持久PreviewReaper控制会话最多900秒，预览容器串行至多12次创建/启动、同时最多1个，单次60秒执行/15秒诊断，总预览执行<=720秒、诊断<=180秒。不同合成activity有显式3次/180秒预算，不用验证batch绕产品累计限制。

12次首次实施验收启动的建议分配为：无害popup对照1、N1/N2共2、有限恶意权限/协议组合1、无限循环1、浏览器hang1、Node hang1、Supervisor死亡1、Reaper死亡1、create回包丢失1、硬截止/控制路径失联1、源失效/取消迟到窗口1。同一组合页串行必要反例；失败立即停止相关剩余项。未知停止分支在新专用控制路径失联后，以真实CID仍运行/预算保留观察，再由授权的独立验收控制器精确清理，不能用mock“已空”；不停止Docker daemon或影响其他容器。建议开跑前另冻结至多4次相关普通修复重测储备；若采用，整卡最多16次/960执行秒/240诊断秒，同一Reaper总截止固定为1200秒，不能运行中延后900秒的首次限额。独立终审读稳定原件，不默认再跑套件。

原生模型替身通过实际gateway/OneCall/PG，首次最多4次单次请求：N1、N2各一次合格响应，第三次非法结构/引用响应，第四次发送后断开造成UNKNOWN；费用0，不连外部provider。同键恢复、PG并发/权限/rollback与资格race复用这些产物，不再发模型。若采用修复储备，开跑前另冻结至多2次直接相关请求，整卡最多6次，原计数不清零，每窗按已有有效原生配置与实际W/管理截止固定。旧Job/四账主体不重跑，新的profile传递/提交与preview物理权威实测。若真实provider质量需后续验收，单独冻结已授权身份/资料/费用，不纳入上述替身结论。

建议实施完整卡active21600秒、metadata10800秒、一个离线定向批与一次typecheck/build，必要高风险SQL和公开链共用上述资源。首次验收HTTP最多720请求，包含PNG读取最多300、公开输入最多200；内部协议故障注入输入最多1000，输入合计<=1200。修复储备若采用开跑前冻结整卡HTTP1024/PNG500/公开输入300/内部输入1200/输入合计1500上限和前述1200秒控制会话截止，不改首次使用计数。各限额共同有效，不能相加造无限调用。H0失败即停止相关负例串，不消耗正常闭环/审计预留；普通修正只验证实际改变性质。此为供编排冻结的资源建议，不是占号、派发或生效额度；上界不足时编排按准确原因调整合同，不在运行中清零或暗增。

### D2 定向矩阵与观察点

- H0-GESTURE/B01：同固定image/browser/argv，测试专用无害允许popup对照先出现新Target/page/root，证实真实点击/Enter与有效激活；生产受限sandbox夹具分别window.open、target blank、新命名target、form target，辅以无手势/有手势比较，独立Target及Page/root frame集合不得增加，window.open拒绝或null可作辅助。对照仅合成测试模式，不成为生产配置权限开关。事件流从触发前持续到超出该动作2秒观察窗；生成后close/暂停一律FAIL。任一未触发、对照不成功、observer丢事件或浏览器版本未知均UNKNOWN/FAIL，不PASS。
- H0-NAV：先真实自身data和blob最小证伪，再自身http/https/file、meta refresh/anchor/history，parent/top有手势与无手势、动态子iframe。观察引擎frame/loader/document/URL提交与哨兵执行、父wrapper身份、是否有读取/新目标；原生guard应给可信否决记录，数量/身份不得变化。反例在限定2秒窗内必须实际触发并在创建/提交前阻断；只有CSP、词扫描、timeout或事后停止不满足。iframe初始化的允许两帧基线与新创建分开计数。
- H0-NET/FILE/DOWNLOAD：外网及127.0.0.1/IPv6回环HTTP、fetch、XHR、img/script和WS；记录路由拒绝、连接事件与无响应，测试专用无秘密回环哨兵只在有隔离的反例夹具启动，生产仍禁止任何监听服务。仅network=none/连接失败不足以定位浏览器层。file哨兵为未来构建的无秘密测试内容，不挂宿主原件；核未读取、下载data/blob/HTTP均未创建下载文件或有效下载任务。socket/文件chooser/工具入口不存在还须从实际协议检查。无新增特权或外网服务。
- H0-PARENT/PROTOCOL：不可信frame试parent DOM、修改sandbox、向父发送伪ready/input/预算/工具JSON、console打印合法头与超长消息，父/主应用不接受命令，Node管道保持原有限协议；只有可信父进程能送init。超大长度头、错hash/nonce/代次、SVG假PNG、大尺寸/大帧、乱序/重复异hash/高频输入分别在受信parser/客户端拒绝或stop，内存/队列有限。伪协议不能增加原模型/工具/费用。
- P-STOP：无限循环、renderer/browser/Node hang、管道断开、Supervisor死亡、Reaper死亡、用户stop、回学习/取消、硬deadline。按B4每层保留精确CID/进程/单调时间/真实kill/状态与cgroup停止原件，截止不变且主界面停止可用。复用一个malicious页串行有限反例，忙循环最后执行；hang/crash用剩余专用启动，禁止4个旧容器套件。Docker不可达一次模拟仅对新专用控制路径，必须UNKNOWN、reserve保留/新start拒绝，不用mock判物理树空。
- G-COMMIT/KEY：四次原生请求实际到达PG；两合格artifact与007同COMMIT；非法结构/引用保留真实收据无artifact；UNKNOWN保留预留。普通app尝试改artifact/输入/hash/旧身份、越权DELETE/角色权限均拒绝；强制新hook异常使007/新产物整体rollback。两个并发同键claim至多一次发送，同键不同输入409，丢响应GET只读找到原artifact，原native Window主权未变。
- Q-QUALIFICATION：父/源/记忆依赖改变及活动取消/到期，GET详情、start、input、frame各检查关闭；准确暂停在“候选帧进入缓存之后、公开资格检查之前”，提交失效再放行候选，必须无正文/画面；不是请求发起前已失效的伪race。资格检查之后合法已发送的在途字节按B2边界观察客户端清空，不误签服务器撤回。SQL坏schema/ACL/依赖未知关闭HTML且旧兼容域可用，历史事实/费用不改。
- P-BUDGET/RECOVERY：并发start_key同键只一CID，异键共享3次/180秒预扣，刷新/配置改动不重置；创建成功回包丢失按精确身份找回不二次create；启动失败仍扣次数、确认未启动可退本preview未用秒数，停止未知不退；应用重启先只读/救援，未确认不能接管。真实PG预算与真实Docker状态分开观察，不用数据库unknown字段代物理证明。
- UI-CLOSURE：两概念生成/打开/数字与图形更新/引用回查/停止/回原学习/刷新只读；keyboard可信控件与文本readout可用，画面挂死时主应用响应。旧HTTP/PNG解码/错误/引用回包分别延迟到切activity/view/owner/preview代次之后，整组guard不得复活旧画面或意图，原父与来源按实际hash关联。全部为真实HTTP/主应用浏览器链，不能用组件mock替整链。

事件deadline、失败次数和运行资源由下一卡开跑前冻结，启动前hash检查只用于身份，不签正常/安全通过。新检查足以区分触发、浏览器拒绝、容器隔离、公开资格、UI防迟到与外部停止；各层失败保留真实原件、同卡修普通缺陷，达到卡内失败限额或需新原生组件即停止依赖并回传，不追加零散G10补验卡。

### D3 一次稳定点独立安全/一致性审计

最终候选与定向原件稳定后进行一次隔离增强审计，审计者未参与108设计或后续实现，仅接原任务合同、有效采用决定、最终实际diff/加载hash、SQL/catalog/ACL、原始浏览器/管道/停止/预算/资格race原件。审计集中检查B01创建前拒绝、全部导航与文件/网络/下载、主应用无执行桥、外部停止证明、同COMMIT/资格/UNKNOWN/预算及正常学习闭环。与G10原107独立窗口可保持隔离，但是否派卡由编排决定，本卡不发送或新建线程。

没有H0与独立终审通过不得开放HTML预览；设计完成、采用批准、普通自检、静态规范或一次截图均不能关闭B01/SEC003。无需本设计交付后再安排泛读方案审计。TASK109/R103仅未来计划，先核证合同和必要G11-P、冻结许可，才由编排出一张完整实现/接线/定向验证/普通修复/收尾卡；没有在本卡占号或派发。

## 证据、限制与文档核对

### 实际证据索引

- [读入身份与锁定规则](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-108/design/input-identity.json)：编排冻结363个current_files及9个合同输入与七项锁定公共规则核对，不把可读身份当业务通过。
- [实际函数AST定位](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-108/design/source-function-facts.json)：11个必要源码文件的221个函数签名/行号；只解析文本，未import或compile产品。
- [精确缓存镜像元数据](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-108/design/known-image-metadata.json)：仅image inspect，无容器创建/启动、pull或包执行。
- [补充本地包/源码与六页来源](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-108/design/fact-addendum.json)：17个追加必要读入hash、Playwright包/类型/bundle事实与页面访问结果。
- [原固定许可与资源记录](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-108/design/session.json)：原起点/截止不重置、实际读入缺口及0运行/0产品写入；最终耗时和核对收据见同目录delivery-check.json。
- 历史044原件：[result](D:/shspic/project_NO3_RetroLume-agent/DocuN/archives/legacy-roots-20261005/Ndocu/results/TASK-044-result.md)和[任务卡](D:/shspic/project_NO3_RetroLume-agent/DocuN/archives/legacy-roots-20261005/Ndocu/tasks/TASK-044.md)；实际报告SHA256 e31ca3e0bae40fe5a93e5c05349aaed74763fb519597729b9b6313ca57328801，卡SHA256 3e4f6fc9d4b03fcc622b9e0283adc44dbbbef24219f9fefc6d5dfe027850dd82，保持原字节。

官方页面总额6/6，访问失败也计入，不另开第七页：两页HTML规范、Playwright Docker、BrowserContext、CDP Page、固定151的Chromium源码。最后一项 [151 render_frame_host_impl.cc](https://chromium.googlesource.com/chromium/src/+/151.0.7922.34/content/browser/renderer_host/render_frame_host_impl.cc)返回Internal Error，未读到正文；不从044的历史HEAD描述推定这个版本源码已核。[CDP Page索引](https://chromedevtools.github.io/devtools-protocol/tot/Page/)仅方法索引可读；具体deny参数引用本地1.62.1 protocol.d.ts，尚未运行验证。当前官网内容和规范不冒固定浏览器动态原件。

现有事实/候选/新建/未核已分别注明。核心未核项为全协议自身导航及动态frame创建的原生否决锚、固定非root/private IPC/seccomp实际sandbox、镜像内部Node/browser/许可证全清单、平台cgroup停止证明、计算语义与可访问交互。前两项失败明确停宿主依赖，不以风险接受、新页权限、事后close或静态替代降标准。

一次文档一致性核对已合并修正实际teaching父种类、输入owner权限/有限状态、管道字段和首次/修复资源的总上界。核对覆盖A—D、原Must/禁止边界、原事实与新增、协议上界/方向/代次、精确CID/单调期限与未知停止、同COMMIT/资格/恢复/四账分工、文件/签名/SQL/配置/UI的相互对应、唯一G11-P、两概念正常oracle与安全/业务矩阵、稳定点独立审计、只读产物范围及实际引用。该核对为文档自检，不是测试或独立审计；收据记录最终字节/hash与原输入差异，不签未来安全通过。

旧70真实入口、全部FAIL/UNKNOWN、历史13元投入及其他旧许可按TASK108原合同原文继承，未重置或复活。107原root/start/API/browser-driver/离线批各3/3，SUP及最低发送各5/8、口令2/2；active14515.5/21600秒、metadata10000/10800保守未知分割、real127.407、offline0.641、cleanup18.452保持原重叠口径，全部旧许可封闭。本次active上限14400、metadata7200；读取/研究/推演/写作/修正均计active，metadata无法精确分拆的重叠以本轮全部active作为保守上界披露。六页额已用完；无SQL/HTTP/浏览器/原生SUP/模型/业务工具/安装/容器运行/build/Git，费用0。完成一次文档核对和保存身份即停，唯一总状态、采用决定、B01及STEP记录由编排维护。

本次交付记录：截至最终保存读回，active保守上界3814.6秒/14400，metadata按全部active重叠计的保守上界3814.6秒/7200，均含30秒交付尾段余量；官方页面6/6。冻结current_files 363项、合同输入9项、锁定规则7项及追加读入17项差异详见delivery-check.json。未运行未来矩阵，无新增需停止的产品资源。
