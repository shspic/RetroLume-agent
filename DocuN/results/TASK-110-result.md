# TASK-110 / R-104 G11 导航边界方案收敛结果

唯一推荐是有限结构化交互描述，由项目固定、版本化的受信程序生成并运行交互 HTML；保留独立非 root 容器、真实浏览器 sandbox、画面输出、有限输入及容器外停止。模型自由 HTML、JavaScript、任意 markup 不再成为运行输入。两类真实计算与图形交互仍是交付目标，不采用静态图片替代。

推荐状态为 recommended_pending_user_adoption，implementation_authorized=false。必须一次明确采用 D1 的 G11-P110 增量，才可把原全协议同步否决合同改为本报告的数据与代码边界合同。没有找到支持全部原强化条款的低成本现成原生锚；这不是所有浏览器均不可行的证明，也不允许默许 hash。本卡只完成 A—D 决策输入，软件可运行、B-01、SEC-003、G11、STEP-015/016、M1 和项目最终验收均未签通过。

项目根 [D:/shspic/project_NO3_RetroLume-agent](D:/shspic/project_NO3_RetroLume-agent)，入口 [AGENTS.md](D:/shspic/project_NO3_RetroLume-agent/AGENTS.md)。task_model / V4.0 / AGENTS CHG-0003，需求 v1.1、架构 v1.09、执行动态 v2.31。接收为 A+ 新隔离技术方案窗口；实际身份是 Codex、系统描述基于 GPT-6，部署型号后缀与实际推理档位不可核，不用 A+ 冒充模型名。未参与 109 实现，未读取其结果自评、实现聊天或思考，未派子 Agent。主控保留最终采用、架构裁定与共享状态维护；本卡不是完整独立安全审计。

实际只写本结果和 [solution-20261010 证据](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-110/solution-20261010/reading-scope.md)。产品、测试、迁移、锁、正式 DocuS、公共库、原始需求、旧证据和记忆均未修改。真实 root、compile/test/build、Node 程序、浏览器、Docker、PG/SQL、模型/provider、付费、安装、下载二进制、clone、Git 和删除均为零。已有原件只读解析，不复演 109。

结论分级如下。A 中的原件行为为继承 A 类证据、此次只读核对为 B 类，公开源码/文档的 API 明示范围亦为 B 类；B 的工程成本判断和 C 的可实现路线为 D 类推断/计划。没有来源支持的覆盖、动态效果、成本或许可完整性明确列为未知，不由 Agent 声明提升证据等级。

## A 约束出处、已采用合同与实际差异

### A1 四层来源分别成立

1. 用户目标来源是 [原始需求文档](D:/shspic/project_NO3_RetroLume-agent/DocuS/原始需求文档.MD:92) 的 FR-009，生成本地交互 HTML 帮助理解和记忆抽象概念，关键内容、计算结果和执行边界可检查。第 54、71、120、144—146 行关联学习闭环、Must 和安全。该文件由用户维护，保留历史整理性质；这里引用正式记录，不把代理整理句子说成用户逐字原话，也不因缺少逐字聊天就断言用户未提出安全要求。

2. 已批准最终 Must 以 [最终需求文档](D:/shspic/project_NO3_RetroLume-agent/DocuS/最终需求文档.MD:93) 为准。FR-009 要求应用内真正交互、正常和边界输入计算及概念可核、资料关联、非法动作被阻止、失败不破坏原活动，不得用静态答案冒充。第 121 行 SEC-003 允许计算和图形脚本，默认禁联网、本地文件、系统命令、直接模型和工具调用，正常交互与真实宿主反例一起验收。第 61 行没有独立 HTML 导出 Must。第 18 行 B-01 与必要独立审计仍限制 HTML 及完整 MVP 放行，不阻塞无关规划。

3. 更强具体合同来自 [108 A2/A3/B3/B4](D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-108-result.md:25) 以及 [有效 G11-P 采用决定](D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-108-work-decision.md:1)。108 把模型生成 HTML/计算图形 JS 送入受限子frame，并明确一次 bootstrap 后所有导航、同文档 URL 变更、data/blob/file/http/https、新子frame及 target 必须在创建或提交前拒绝。用户 2026-10-09 的采用使该具体合同生效；108 原正文的待采用措辞只保留其原时点。四表、两个 NOLOGIN 角色、profile/API007、画面/输入、外部控制和独立预览预算一并采用。不能凭 Must 未逐字列出 fragment 就自行删除该条款。

4. 现状来自真实源与原始反证。[host.cjs](D:/shspic/project_NO3_RetroLume-agent/deploy/preview/host.cjs:2) 自述只承载关口反例；其 route/WebSocket 处理、sandbox、CSP 与事后事件观察没有生产同步否决锚。[wrapper.html](D:/shspic/project_NO3_RetroLume-agent/deploy/preview/wrapper.html:2) 仍允许 inline script。backend/app/preview 只有诊断封包及精确资源控制辅助模块，012 四表迁移和 frontend/src/explanations 尚不存在；activities/repository.py 的真实 record_outcome 等原入口存在，新 HTML 接线未存在。不能把 108 中的计划接口说成已经实现。

### A2 每种路径的要求及现有证明范围

同文档 fragment、history 或其他 URL/历史更新均在原合同禁止范围。正常 DOM 值、文本、图形变化不属于禁止的 URL 变化。本轮原件已证明 hash 提交；不以 loader 不变、document backend 不变或裸 URL 不含片段签拒绝。HTML 规范也区分同步 fragment 和 URL/历史更新路径，本项目的禁止项比某一规范算法名更广。[HTML 导航规范](https://html.spec.whatwg.org/multipage/browsing-the-web.html)

跨文档 data/blob/file/http/https 必须按原合同在提交前拒绝。route 只拦进入其请求路径的动作，network=none 不能阻止 data/blob 提交，也不能证明运行时 file 防读或容器回环拒绝。R08 的 child/blob/data 因首个 hash 反证而未运行，不能把它们改成通过或另一个反证；更早 data 附近的 origin CHECK/fork 因果仍未知。

父/顶层导航与修改父 DOM 必须被阻止。唯一子frame不授 allow-same-origin 或 allow-top-navigation，父 wrapper 不含业务秘密、不提供页面命令桥，这些是有效保护方向；不由自身 hash 反证泛指父权限已经越界。

popup、target blank、新命名 target 与 form target 原来要求创建前拒绝。109/C04 的真实手势正对照及四种受限情况只继承有限子事实，form 还受未授 allow-forms/CSP 约束；不由这些事实签全部导航或全部 frame 创建前拒绝。

新子frame原合同禁止创建；初始化一个根页和一个子frame是受信 bootstrap 例外。frame-src、后收到 frameAttached 再删除、暂停新 target 都不等于创建前否决。动态 about:blank child 的全路径覆盖当前未证明。

正常计算、数字/range/button、键盘可访问操作和图形必须真实可用；原合同允许模型自由脚本更新 DOM。推荐方案保留这些用户效果，限制其实现语言和布局、资源及动作集合，详见 B3/C2。这个限制属于需采用的合同变化，不以安全之名自动生效。

### A3 R08 原件支持的准确结论

原始位置为 [navigation-hash-counterexample.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-109/execution/continuation-05/root-08/preview/navigation-hash-counterexample.json) 与同目录 frame-binding.json、observations.json、container-stdout.bin、resource-observations.json。本卡 [只读交叉摘要](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-110/solution-20261010/raw-navigation-reading.json) 从 38,699 字节 stdout 解码 36 个封包、34 条完整记录，长度、序号、正文和分块 hash 相符；H0_NAVIGATION 与独立 JSON 的 case、FAIL、frame 和完整 document URL 一致。这是既存证据核读，不是新的 A 类运行。

真实主体是 OOPIF frame/target 9861FE7EB06B3FB0068E15805B842257，直属根 3DB3D1A7FAA56FC0AAE1AC2C1B4658C9，owner 的 sandbox 为 allow-scripts。匹配主体执行上下文的 gesture trusted=true、active=true 和 handler ACK 均存在，实际观察 2.055964316 秒。Page.navigatedWithinDocument 将完整 URL 提交为 about:srcdoc#H0_SAME_DOCUMENT_COMMITTED，document URL 和 target URL交叉一致，原 frameTree 的 urlFragment 也存在。loader 23723DA20245F69D7D3EC70D0A0444EF 与 document backend=2 不变是同文档性质，原 urlChanged=false 的片段排除语义原样保留。

故当前宿主不满足已采用导航合同，属于已明确 P1 缺口；不是观察不足。原 TASK-109 完整验收失败、诊断子目标完成；置顶 [109 关闭合同](D:/shspic/project_NO3_RetroLume-agent/DocuN/tasks/TASK-109.md:1) 封存全部许可。global78 非 78PASS，TASK/H0 各 8/8、build/controller 各 4/4、preview 4/16 的名义余额不可用，失败、未知、投入和费用 13 元均不清零。

资源原件最多 pids.current=125、上限128，memory.current=731,951,104 字节，即约698.043 MiB、上限768 MiB；这是缺少余量的风险线索，不证明旧 fork 的唯一原因。当前 data/fork 未知不阻塞本卡方案交付，也未被本卡解决。Chrome151.0.7922.34、Playwright1.62.1、Node v24.18.1、浏览器二进制 SHA256 0b20b130e7edd9dd51873be867761295fe0cfad490c2b9a64f95bd3cfc08fa71 的身份来自 R08 加载原件，不是本轮启动所得。

## B 有限可实现性判别与唯一选择

### B1 原生候选一 CEF

读取 CEF 官方 master 头文件在线快照，未取得 commit，不冒充某个已部署发行版。CefRequestHandler::OnBeforeBrowse 在 UI 线程同步返回 bool，true 取消、false 继续，参数含 browser/frame/request/user_gesture/is_redirect；OnOpenURLFromTab 是特定分支的同线程 bool 入口。CefLifeSpanHandler::OnBeforePopup 是新 popup browser 创建前的 bool 入口，true 取消、false 允许。[CEF 请求头](https://raw.githubusercontent.com/chromiumembedded/cef/master/include/cef_request_handler.h)，[CEF 生命周期头](https://raw.githubusercontent.com/chromiumembedded/cef/master/include/cef_life_span_handler.h)

可核覆盖是这些 API 声明的导航和 popup browser 分支。它们的返回值有实质否决性质，区别于 OnAfterCreated 通知；但头文件没有保证 renderer 同步 fragment 全部先经 OnBeforeBrowse，没有任意新子frame 创建前 bool 锚，也没有保证每个底层 Target 尚未创建。data/blob/file/http/父导航的完整分派、初始空白 frame 与 history 等例外没有逐路径核实。尝试的 libcef/browser/navigation_throttle.cc 返回 Internal Error，计入资料额度，未伪造内部链已读。

Chromium 当前 NavigationThrottle 头明确说明部分导航不走普通 throttle；WillCommitWithoutUrlLoader 还须单独注册，并排除 renderer 发起的非 history 同文档路径，因为它在 renderer 同步处理后才通知 browser。这是共享机制的警示，不证明未读的 CEF 实现或固定151与 main 逐字相同。[Chromium NavigationThrottle](https://raw.githubusercontent.com/chromium/chromium/main/content/public/browser/navigation_throttle.h)

正常数字和 DOM/图形可以继续工作，拒绝导航会去掉导航式交互；真正满足原绝对条款还需要 renderer 同文档提交、history、frame/target 创建多个路径的同版本证据和原生接线。没有这些证据就排除本轮采用 CEF；写一个 Gate 类、网络 handler 或加 browser throttle 不能补足。引入 CEF 会新增原生构建、离屏输入/画面、sandbox 和更新维护域；具体体积、平台资源及兼容未测。头部为 BSD 三条款式许可，Chromium/第三方清单未核，不能把这一头部当完整发行许可证。

### B2 原生候选二 Qt WebEngine

官方页面当前跳转到标为 Qt WebEngine 6.140.0 / 6.140 branch 的在线快照；没有安装 Qt，不把该标签称为项目稳定版本。QWebEnginePage::acceptNavigationRequest(url,type,isMainFrame) 同步 bool，false 拒绝该请求、true 接受，含主/子frame标志；文档明确同页 fragment 不调用，加载通知还可能先于决定发生。因此它不覆盖已发生的 hash 问题，也不能用 loadStarted/loadFinished、urlChanged 或回滚补签。[Qt QWebEnginePage](https://doc-snapshots.qt.io/qtwebengine/qwebenginepage.html#acceptNavigationRequest)

createWindow(type) 同步返回新 QWebEnginePage 指针或 null；返回 null 后可能发 newWindowRequested，应用还须不调用 openIn 才能保持不提供新页。该对象分配接口不证明全部底层 Target 创建时点。动态 child 创建前、全部 data/blob/file/父导航分支和 history 变体没有完整证明；资源请求 interceptor 不是 fragment 否决。正常控件和 DOM 图形不依赖页面导航，可以保留；原绝对合同仍明确缺 fragment 覆盖，故排除本轮采用。

Qt部分存在商业或 LGPLv3/GPLv3/GPLv2 等选择，还须核 Chromium 第三方义务；本轮没有具体发行合规裁定。新增 Qt 原生事件循环、离屏接线、包装和更新依赖，也没有证明能省资源或免维护。[Qt WebEngine 许可](https://doc-snapshots.qt.io/qtwebengine/qtwebengine-licensing.html)

本轮不推荐浏览器 fork。坚持执行模型自由 HTML/JS、同时禁止全部 renderer 同步 URL 更新和一切新 frame/target，需要覆盖 renderer 与 browser 两侧多种初始化、history、导航和创建入口，并随浏览器更新维护。准确补丁、验证对象、工期和成本都未证；这不是一句新增原生组件能承担的小改。两候选的排除分别是明确不覆盖或覆盖未证明，不推广成所有其它引擎不可行。

### B3 唯一输出与信任合同方向

采用 interactive_description.v1 作为模型数据输出，受信 renderer policy 以项目内固定源码、字节 hash 和构建版本确定。它接收类型明确的参数、算式 AST、说明、有限图形和 reset 动作，不接收语言代码。生成的 HTML 包在原独立容器内运行固定计算与图形脚本，主应用只提供可信控件、文字和 PNG；计算解释器和远端 DOM 不移回主应用运行。

首版支持连续参数、整数参数、算术/有界函数、柱形图、有限曲线、有限点线图与文本读值。能源/比例/函数变化、基础概率分布、简单几何坐标等概念可以表达。首版不支持任意 HTML/CSS/JS、任意 DOM/事件处理器、动态插件、文件/资源 URL、网络、任意 SVG、模型图片数据、视频/WebGL、可执行公式字符串、开放循环/递归或任意工具。按钮只 reset 已定义参数；复杂拖拽、模拟器、任意动画及新数学函数不自动进入能力。遇不支持的概念返回明确生成失败，保留原学习成果，不用静态图冒交互成功。

这是表达能力和信任边界的实质变化。FR-009 的交互、计算、图形与资料目标仍保留 Must；SEC-003 的计算/图形脚本只允许固定受信实现。原模型自由 HTML 输出及浏览器对任意自由脚本全协议同步拒绝，不能声称原封不动保留。具体待采用文本见 D1，不预先生效。

不选择把 hash 宣布无害、延迟 close/回滚、关掉脚本后给静态图片、将自由 HTML 放回主应用、字符串黑名单或把任意 JS 包成受信脚本。这些均不能同时给出本轮需要的用户效果与可核边界。结构化数据方案新增的是一个有限语言校验器和固定渲染器；不新增引擎、服务或数学第三方库，维护范围可随有限操作枚举识别。其安全和正常效果仍须实现验证与集中终审，本报告只给工程推断。

## C 唯一推荐的完整最小实施合同

### C1 入口、可信对象和权限

正常入口继续是 current 的 LearningResult answer 段、TeachingWorkspace 的 exercise/feedback。用户选难点并显式生成，确认父成果、来源、配置 hash 和一次模型调用/余额；同键恢复只读核对。clarification/no_evidence/conflict、interview、失效或历史父不变成可执行来源。原 learning 父与 teaching.v2 记忆闭包、goal/scope/source 的冻结和逐事务资格检查完整继承 108 B1/B2，不截断闭包使其合格。

可信对象是项目加载的 backend 校验/编译逻辑、固定 Node 宿主、固定 renderer 源与策略、浏览器部署清单、Supervisor/Reaper、配置和资格/预算权。模型文本、描述、引用指向、参数与公式始终是不可信数据；校验后只取得有限数据语言的资格，不成为可信代码或数学正确性证明。客户端不能传 profile、messages/model/tools、URL/path、DOM selector、JS、image/CID、Docker/CDP 方法、deadline 或权限。容器没有 DSN、应用 token、owner key、资料原件、秘密或宿主挂载。

模型的有限相关片段外发仍走已采用服务入口和旧数据合同，不新增 provider、真实用户数据、费用或外发权。引文由原 catalog 对照，来源回查继续在主应用原引用链执行；容器只收解释所需有限文本，不读取资料库或引用 URL。C 内所有新类型、函数职责和文件都是实施计划，没有建立 stub 或声称已有新签名。

### C2 数据语言、计算和渲染边界

模型输出必需字段为 schema、title、concept、inputs、calculations、views、actions、calculation_notes、limitations、citations。schema 唯一 interactive_description.v1；未知键、重复键、坏 UTF-8/NUL、非有限数据、错引用和超界一律 invalid_interactive_output，原调用/收费事实照实保存，无可用 artifact。模型输出 UTF-8 总计不超过24576字节，title<=128字符、concept<=1024，有限引用与说明延用原 catalog 上界，不截断成功；4096 token 上限及原活动更小限制继续取小。

inputs最多8个，kind只 number/range/integer，id采用 hctl_ 后接1..24个ASCII字母数字或下划线，唯一。label<=80、description<=256，min/max/step/default使用<=24字节规范十进制字符串，绝对值<=1000000；无指数、负零、前导零等同值多拼写，拒绝字符串转布尔或布尔冒数字。default在范围与step格点内，range最多100步。至多4个参数关系约束，只支持两个已定义参数的 le；不接可执行 predicate。整数及参数关系在候选更新上检查，失败不提交参数或图形。

calculations最多32项，使用唯一 hcalc_ ID，按固定拓扑顺序只能引用输入及前面的结果。AST全描述累计最多256节点、深度16。叶为 const/input/result；curve 内额外有局部 sample_x。计算操作枚举为 add/sub/mul/div/neg/abs/min/max/pow_int/sqrt/sin/cos/binomial_pmf；add/sub/mul/div/min/max/pow_int固定2个参数，neg/abs/sqrt/sin/cos固定1个，binomial_pmf固定3个。没有字符串公式执行、属性访问、对象调用、赋值、循环、递归、模块、随机数、时间、URL/DOM或工具操作。用封闭 switch/Map 解释节点，禁止 eval、Function、字符串定时器、表达式转 JS 源。binomial_pmf 要求 n整数0..20、k整数0..n、p在0..1，有限循环按n计；p=0或1显式处理端点。pow_int 指数整数0..10，零次幂定义为1且写入说明；除零、sqrt负域和任一非有限中间值报 calculation_domain_error。

views最多4项，包括 readout/bar/curve/points_lines，readout最多8个，图形最多2幅。bar的source只允许固定values或binomial_distribution；values引用已定义值，binomial_distribution只引用已定义n/p输入或结果、按受信适配器枚举k=0..n，最多21柱且每柱计一个点。curve用有限AST对显式有限区间采样，points_lines只接有限数值/已定义结果坐标。全部图形合计最多128点，坐标和比例有限，颜色只选项目固定调色板，布局是固定组件枚举。每次更新解释器至多50000步，binomial内部迭代和所有采样也扣步，达到上限 calculation_limit，不继续或自动增加额度。计算在容器内完成，先获得整个候选数值/图形快照再原子替换；错误保留最后一致画面并显示明确错误，不留下部分成功输出。首个完整数值/图形快照失败则init失败、不能发ready，保存已付生成事实并停止该preview；没有“上次画面”时不造成功读值。重算结果不是教学对错、权限、额度或学习记忆权威。

actions最多4个，首版只有 reset，绑定已定义参数默认值；不存在 onClick 字符串、自定义函数、navigate/open_url/submit/download 等操作。公开有限输入只 set_number 和 activate(reset)，删除原计划通用坐标 click/raw key 通道；键盘、range和按钮由可信 React 控件转成这些类型。正常文本和图形可访问操作仍真实驱动远端计算，不能在主应用伪造读值或图形。

backend在原始模型 JSON 解析时就拒绝重复key；容器只收可信监督器发出的规范 JSON。Node还必须核全字段和递归类型，并将整个收到的对象重新规范序列化与原字节比对，非规范数据或重复key造成的差异拒绝，不能仅靠 JSON.parse 的最后值覆盖。规范沿原新HTML规则的排序键、UTF-8无BOM、紧凑分隔、ensure_ascii=false、无NaN；数字配置用字符串，计数是有界整数，跨语言差异在未来同一批验证。ID索引用 Map，禁将任意模型键合并到 DOM、配置或原型对象；未知属性一律拒绝，这是允许类型集合而非危险词黑名单。

可信编译器生成固定 HTML shell、固定 script/CSS 字节及专用 CSP hash。模型 JSON 通过固定代码的单次参数传递初始化，绝不拼入 script/style、模板属性、URL、innerHTML、document.write、事件属性、srcdoc字符串或CSS。正文只写固定非script/nonstyle元素的 textContent/文本节点；图形只调用受信 Canvas 数值绘制。模型文字含脚本标签、javascript或CSS url也只成为普通文本，不能新增元素/属性/链接。textContent 的文本节点语义有规范支持，但本方案完整安全性仍依赖实际固定节点和危险 sink 排除。[DOM textContent 规范](https://dom.spec.whatwg.org/#dom-node-textcontent)

编译包含固定受信 HTML shell 与严格描述及 renderer policy，不承诺单独导出后脱离宿主运行。compiled_html<=65536字节、规范描述<=24576，产物完整投影<=110592字节，007原完整正文131072字节上界不变且更小配置仍取小；超界拒绝。init不接 compiled_html/raw html 或资源路径，只传描述与受信 policy 身份，Node从镜像固定位置加载相符的项目 renderer，不允许模型选择版本。原生成图片入口取消，图形由计算绘制；不新增图片、字体或资源数据权限。

### C3 两类有据真实交互样例

样例来源为 108 D1 已定义的未来合成材料和独立手算，不是恢复不可达的旧 SPIKE 页，也不是本轮已实测结果。实际实施前仍冻结合成原文、版本、页行引用与 hash。

第一类为机械能。资料规定 E=mgh、g=9.8，m/h范围0..10；描述包含两个参数、mul AST、能量数值及随 h 更新的柱/高度图。计算节点可用以下数据表达，没有代码字段。

```json
{"id":"hcalc_energy","expression":{"op":"mul","args":[{"op":"mul","args":[{"op":"input","id":"hctl_m"},{"op":"const","value":"9.8"}]},{"op":"input","id":"hctl_h"}]}}
```

用户在可信控件把 m=2、h=3，远端重新计算58.8 J并更新图形；h=0得到0、图形归零，m=0且h=3也为0。负值拒绝、不更新已有一致快照。独立oracle为手算2×9.8×3=58.8、零因子为0，绝对误差<=1e-9。必须保输入seq/ACK、实际页面文本、图形几何变化与独立期望，不能仅生成写着58.8的静态HTML。

第二类为二项概率。资料规定独立试验的 P(X=k)=C(n,k)p^k(1-p)^(n-k)，首验 n范围1..5、k范围0..n、p范围0..1。描述是三个参数、k le n 关系、以下有限操作及0..n的概率柱图，采样k只在受信分布图适配器有限枚举。

```json
{"id":"hcalc_pmf","expression":{"op":"binomial_pmf","args":[{"op":"input","id":"hctl_n"},{"op":"input","id":"hctl_k"},{"op":"input","id":"hctl_p"}]}}
```

输入 n=3,k=2,p=0.5，远端显示0.375，柱图为0.125/0.375/0.375/0.125。p=0,k=0和p=1,k=3均为1，p=1,k=2为0；n=1,k=1,p=0.25为0.25。k>n、非整数n或p>1拒绝。依据为独立组合数手算、端点定义和全柱和为1，误差<=1e-9。模型式子、引用和概念仍需内容核证，这两例不证明全学科或真实provider质量。

### C4 生成、产物身份与同COMMIT

改用受信生成 profile html_explanation.v2，输出 interactive_description.v1，domain artifact schema compiled_interactive_html.v1，内部管道 retrolume.preview.v2。不修改既有 learning/teaching/interview 的版本或结果封套；html11m.前缀保留专用父消费隔离，但必须与新profile/schema匹配，旧html_explanation.v1自由HTML候选不被v2宿主接受。它们尚未实现，命名仅为拟采用合同。

request/context hash继续覆盖父、来源、goal/scope、model和generation/preview配置；新增固定 descriptor schema、renderer policy ID/version及 bundle sha。renderer由配置决定，不由模型 body 决定。description_sha256覆盖规范描述；renderer_sha256覆盖固定程序/CSS/shell；execution_package_sha256覆盖规范描述加policy与固定程序身份投影；artifact_sha256覆盖产物内容/引用/说明/限制/编译包；body_sha256保持完整持久业务封套语义。各hash的内容投影排除该hash自身、会话CID/nonce/deadline及未来image ID；runtime session再绑定已存在的artifact和实际image，不反向改artifact。构建内清单绑定源码/依赖/浏览器，外部部署清单再绑定最终image ID，避免image写入自身形成循环hash。

原012四表和两个NOLOGIN角色可保留设计。html_commands保存冻结输入、版本与claim/terminal；html_artifacts保存不可变描述、编译包、引用、各hash；html_preview_budgets持久计预览额度；html_preview_sessions登记真实owner/boot、CID/image/policy、generation/nonce、初始单调截止及停止收据。没有第五表、旧行迁移或新DB角色要求；字段/校验函数须按v2类型调整，不能宣称已迁移。

新校验/编译和父资格复核接入原 record_outcome 的同一connection，007真实收据/合格正文、artifact和command terminal同COMMIT。编译失败不保存可用artifact，收到非法输出仍保存实际RECEIVED/费用事实；编译 hook异常整体rollback，UNKNOWN保留原预留无自动重发。模型请求、工具、费用、原生时间四账与原OneCall/Windows监督主权不改；preview额度不能给它们退款。相同business_key不同输入409；丢回包只GET原键，claim/sending/UNKNOWN不得重发。

artifact还需资格snapshot核父/source/scope/记忆闭包和新policy/描述hash。public详情、start、input、frame分别检查；帧进入缓存后、公开序列化前再检查，失效先提交则拒绝候选帧，检查后合法在途字节不能撤回。客户端整组身份守卫清空迟到PNG/readout/引用；不持DB锁等待Docker或网络。原owner/app最小权、PUBLIC撤权、无artifact UPDATE/DELETE、固定锁序与未知schema失败关闭，按108 C2逐项保留。

### C5 公开界面、管道和失败文案

API007原计划路由保留，即 commands显式生成/GET同键，artifacts有限列表/详情，artifact previews显式打开，preview状态/frames/inputs/stop。_guard、X-RetroLume-Session、no-store/nosniff、本地同源和UUID规则保留。commands请求仍只business_key/parent/focus/expected_config_sha256/confirmed，不新增公共schema/renderer选择权。详情投影只title、可信派生控件/读值定义、说明、引用和限制，加schema/policy的非秘密身份；不返回可执行HTML或模型上下文。

打开请求仍start_key/expected_artifact_sha256/input_owner_key/confirmed。32字节owner key只留面板内存、服务器存hash，绑定activity/preview/generation，不给容器或GET读取；刷新不接管旧运行。输入保留seq、payload hash、generation和owner核对，event缩为set_number(control_id,value)或activate(action_id)，没有click/key/selector/URL字段。停止不依赖owner key，以同应用身份针对精确session幂等停止；响应仅说明停止请求，不把HTTP200称为树空。

内部继续匿名stdin/stdout有界二进制封包，4字节网络序头长度、规范JSON头、限长body及SHA，保preview_id/generation/artifact hash/channel_nonce/seq，新增description/policy身份纳入init/ready。头<=2048、init<=65536、input<=1024、status<=4096、PNG<=524288。v2的init只有规范描述/固定policy/viewport；host→supervisor仅ready/frame/status/input_ack，反向仅init/input/stop。只一个未ACK输入，同seq同hash幂等、不回放未知输入；stop队列独立优先。PNG640×480/DPR1/至多3fps，只保最新及一帧在途，尺寸/hash/序号和解码身份核对沿原合同。

Node仅对固定受信 renderer 调用固定数据入口，不能接代码、DOM selector、任意CDP方法或函数名。console/postMessage/解释文字不进入协议parser；stdout只由受信Node进程写。page读值是显示数据，不可宣称生成内容正确或预算可用。受信HTML仅一次初始化，模型不进入任何srcdoc构造字符串；初始化后对description重复init、policy漂移或protocol v1/raw-html封包拒绝并停止。

UI继续“交互解释→确认生成→已保存未打开→显式打开→调参数/查看公式与来源→停止并回到学习”。可信控件有label、焦点顺序、键盘可操作和节流aria-live文本；主应用停止按钮独立于远端忙碌。切活动/父/owner/代次/卸载/隐藏/失效先递增代次、撤销输入、清画面与读值，所有成功/失败/PNG解码/引用回包核完整身份。真实参数操作必须在远端改变计算和Canvas，不能用本地模拟值替代。

失败文案至少覆盖“该概念超出当前交互描述能力，原学习成果已保留”“交互描述不符合安全格式，未创建可预览产物”“计算输入超出定义域，已保留上次画面”“运行组件版本不匹配，交互解释暂不可用”“来源或父成果已失效，停止中”“预览额度不足”“停止尚未确认，暂不能再次打开”。unknown必须保留未知事实，不显示成功、清空费用或换键偷偷再试。

### C6 导航边界、隔离和外部停止

推荐的可信锚是有限语言校验与固定程序的数据到代码边界。描述没有导航/历史/创建frame/target/下载/文件/网络操作，文本没有markup解析通路，按钮/输入只有固定数据更新；受信运行程序不调用这些API、不生成a/form/iframe等可导航结构。一次 bootstrap 允许根wrapper和唯一sandbox子frame；之后有效描述和输入只能修改数字、固定文本与Canvas。任何新导航、URL fragment/history变化、frame/target增加都是缺陷，禁止给hash豁免。

这是对合法不可信数据入口的可实现前置拒绝，不是浏览器面对任意已执行脚本的全协议同步否决。CSP、route和事件观察不再冒充这一更强性质。若受信程序出错、代码/URL穿过校验或浏览器被攻破，现Playwright不能保证任意fragment发生前取消；事件只用于发现偏差、立即关能力并外部停止，不能签该动作事前已拒绝。这个承诺调整必须采用D1，保留旧109 FAIL原文。

外层仍UID/GID10001、真Chromium sandbox、cap-drop ALL/NNP、只读、无bind/socket/port/secret、networknone/privateIPC、CPU1、SHM64MiB、tmpfs128+32MiB/nosuid-nodev-noexec/0700、restartno/init。保留route/WebSocket拒绝、无监听/ServiceWorker、下载deny、子frame无allow-popups/same-origin/top-navigation/forms/downloads；不靠这些层声称任意脚本导航前拒绝。旧151/Playwright1.62.1/Node24.18.1候选身份可复用来源，但新产物实际加载必须重新绑定，不启旧容器。Playwright本地声明Apache-2.0/Node>=20；新渲染器和校验器使用项目自有实现，不新增运行依赖。Node/浏览器/基础镜像的完整第三方许可清单仍需未来构建整理。

首版建议固定资源改为pids256、memory和memory-swap各1024MiB，较旧上限多128任务及256MiB；其它隔离权限不变、同时仍仅一个preview。依据是R08125线程/约698MiB的真实小余量，属于有限余量建议，不是旧fork根因修复或新性能通过；主机实际余量未知。不得运行中自动升资源。若这一上限仍不满足启动/真实交互/停止，停相关实现并交实际缺口，不再按旧128/768反复开小批。

preview预算保每activity3次/180秒、每次reserve<=60秒；预扣即扣次数、失败不返次数、刷新/配置/新owner不清零。t0在reserve前固定，runtime D=t0+reserve；准备最多3秒计入D，ready<=t0+8秒且<=D-10秒，输入到D-10秒截止；停止2秒软请求后按精确CID kill，剩余物理确认不延D。资格最多1秒有效、250ms核对，控制失联2秒触发外部停止；diag<=15秒不得继续HTML执行。实耗只有确认未启动或精确停止后结算，未用秒数只返preview账；unknown全reserve保留、新start封闭。

Reaper先READY和登记意图落盘，Supervisor固定数组create，取得CID/image/nonce并登记、Reaper确认绑定和截止后才能start；丢create回包仅按精确name/nonce/labels/image找回唯一自有对象，不再次create。Supervisor死亡由Reaper按原deadline kill，Reaper死亡由Supervisor及应用生命周期持登记副本救援；全监督/宿主/daemon不可用不承诺按D物理停止，记录cleanup_unconfirmed，保留reserve且关闭HTML。

停止证明继续要求精确身份、原kill/wait/events/EOF、Running=false/Pid0/无restart、拥有的CLI/管道结束以及固定Linux后端任务/cgroup无残余的可靠证据。Windows/Docker Desktop下不增加特权的直接cgroup核对路径本轮未证；不能由Stopped/Pid0或数据库状态补签。后续完整实施应首先核该证据能力；缺可靠路径时保留tree_unconfirmed并停受影响放行，不暗加特权辅助容器、宿主cgroup挂载或放宽合同。此前已充分的有限停止子事实复用，完整树空与正常运行仍由未来原件决定。

### C7 真实文件职责和兼容恢复

现有 deploy/preview/host.cjs、wrapper.html 及 backend/app/preview 的几个模块是109诊断材料，旧permit/协议只读封存，不能原样挂成生产服务。后续新生产入口拟为 [deploy/preview/renderer-host.cjs](D:/shspic/project_NO3_RetroLume-agent/deploy/preview/renderer-host.cjs)、runtime.html/runtime.cjs/runtime.css、descriptor.schema.json及版本/许可清单；这些路径现在是计划。renderer-host承载验证后的单次bootstrap、固定程序/数据入口、有限管道及画面；runtime只有上述有限运算和DOM/Canvas渲染；schema是共同类型来源。Dockerfile和受信bootstrap在获准实施卡构建新派生identity，不改旧上下文或旧镜像原件。

backend/app/preview/contracts.py未来区分v2业务和旧h0观测，不扩旧h0执行许可；新增description.py负责严格数据/AST/域/大小，compiler.py负责受信policy绑定和编译包，generation.py/repository.py/api.py负责原生成、同COMMIT、资格/预算/API007，host_policy.py绑定manifest/候选验证/独立终审批据。supervisor.py/reaper.py只在明确生产控制合同下改为精确新session管理，旧permit硬编码不能复用为授权。计划012_html_explanations.sql保四表/角色与校验；这几项并未创建。

主业务薄扩展仍在 capabilities/contracts.py、gateway.py、activities/repository.py 的profile/binding/admit/mark/record_outcome同connection及新父消费；service_config.py、main.py和activities/api.py接新能力和生命周期。实际旧入口位于repository.py的admit1086、_write_outcome1658、record_outcome1689、read_committed_result1805、cancel_activity851行；只核真实职责，不预造新签名。worker/OneCall/Window/Job/原四账不改权。

前端计划原HtmlExplanationPanel/PreviewCanvas/htmlApi/htmlIntents/contracts及可信参数控件，接ActivityWorkspace/LearningResult/TeachingWorkspace；原TeachingExercise/Feedback仅必要父选择回调。deploy/start_local.py和用户启动说明只增加显式配置的生产控制/停止，不在普通启动时安装、pull、迁移或开启旧109许可。不修G10旧O107观察、不改001—011、旧记录或原profile序列化。

新域未配置、012不存在/partial/ACL未知、policy/image/bundle不符、验证或终审批据缺失、停止未确认，都只关闭HTML生成与预览，旧G3—G10的学习/教学/面试/引用/记忆充分未变证据继续有效。恢复只核键/产物/session/额度、精确停止、保留新旧事实；不回退自由HTML/v1，不逆迁移或删除，不自动接管输入，不宣称已迁移。资料/学习原成果仍可只读访问。

## D 一个采用增量包与未来最小验收

### D1 唯一待决定包 G11-P110

这是一个合并包，当前未采用，不另拆引擎、参数、schema和预算审批。主控核证后可一次提交以下具体决定文本。

1. 采用模型输出interactive_description.v1、受信profile html_explanation.v2、compiled_interactive_html.v1产物与retrolume.preview.v2管道。模型自由HTML/JS/markup不再是可执行输入；HTML计算与图形只由固定项目renderer在原独立容器运行。允许能力限定为C2的有限类型、AST、图形和reset，unsupported明确失败；FR-009真实交互、可核计算/内容、来源和SEC-003无网/文件/系统/模型工具权限继续Must，独立HTML导出仍非Must。

2. 明确替换108 A3及109中“执行模型自由脚本后，对所有同文档/跨文档导航、frame/target在浏览器创建/提交前同步否决”的具体实现合同。新条款为“一次受信初始化后，任何合法描述及有限输入不得引起导航、URL/历史变化、新target或追加frame；代码、markup、URL、DOM/任意工具操作在输入类型与编译边界拒绝，字符串只作文本。程序无此能力出口；突破边界或观察到上述行为立即判缺陷、关闭能力并精确停止，不将事后停止称为事前拒绝”。不允许hash豁免。原浏览器面对已经任意执行的脚本全路径同步否决不再被承诺；这是需要用户明确接受的安全合同取舍，不是原109失败已解决。

3. 四表/两个NOLOGIN角色、父资格、原四账/OneCall/UNKNOWN、API007路由、PNG、owner、持久3次/180秒和外部Supervisor/Reaper保留原采用设计；新类型/hash/校验函数与详情投影按C4/C5更新。输入移除原计划click/raw key，保有限set_number/reset；旧模型生成图片输入取消。主要模型和公开语义变化都包含在此包，普通组件内部名字/布局不另审批。现四表/API未实施，保留是设计延续，不是已迁移声明。

4. 不采用CEF/Qt/fork，不新增引擎、第三方数学库、服务或运行许可证类别；新增有限数据校验/编译器和固定renderer的源码、构建身份、样例oracle与集中安全维护职责。沿既有缓存与本地包派生，实际基础/Node/Chromium/第三方许可仍必须完整登记，缺材料不自动外网安装。资源权只明确固定pids256和memory/swap1024MiB，较旧多128任务、256MiB，同一时刻一个preview，时间/频次不增加。成本是限制自由页面表达、维护两处数据边界与有限计算语义、准备新产物/profile兼容和本次完整成果隔离终审；没有证据支持具体工期或保证资源足够。

采用本包只确定下一完整实施与有限合成验收的技术基线，不恢复TASK109或现在授予运行。下一卡必须另冻结真实identity、资源、root/构建/HTTP/模型替身/容器次数和硬截止、权限与收尾范围；所有数值建议均非当前许可。真实用户数据/provider/费用、联网安装、新特权/页面能力、Git、删除或发布不由本包取得。

如果不采用本包，原G11-P仍有效但现宿主仍失败，生成/四表/API/预览继续冻结；不交叉使用新输出与旧全协议承诺。没有第二个建议用户先试的候选包，也不要求先运行某组件才能交本方案。

### D2 身份、oracle与最小矩阵

未来实现验证只对采用后的完整候选组织一次合并批，先核严格输入到固定程序边界、真实加载/隔离与停止证明，成立后同卡继续业务接线/正常闭环/必要普通修复。新反证、关键资料不足或需扩大权/资源时停依赖保存事实；不连续改参数重跑旧hash。既有109反证及充分未变G3—G10原件直接继承。

开跑前冻结最终产品差异、descriptor schema与两处校验/规范化版本、renderer/host/wrapper/CSP/协议hash、基础和派生image ID、Node/PW/Chromium实际版本/二进制/argv、UID/sandbox、资源限制与真实policy票据、012catalog/ACL/function、frontend实际加载bundle、activity/source/parent/body/request/descriptor/artifact身份、owner/boot/CID/generation/nonce和全部固定deadline。记录实际目标frame/target和完整URL及fragment，覆盖OOPIF；仅标签、Frame.url或loader不足。代码与参考的版本来源、许可清单一起交审计。

M01 正常机械能。一个实际生成/COMMIT/打开会话，C3的三个正常/零边界和一个负值；UI键盘/number/range/按钮驱动远端ACK、文字和几何变化，独立手算误差<=1e-9，来源回查、停止和回父。数值或截图静态写死、只组件mock、ACK未完成均不通过。

M02 正常二项分布。第二个真实会话，C3的中心、三端点、n=1例和k>n/noninteger/p>1拒绝；读数、完整柱图与和为1同时核。第一次初始化使用含两种XSS/脚本闭合文本的合法标签，必须原样文本展示、无新节点/执行/请求/URL变化；不是先删文字才签安全。

M03 生成与解析边界。未来定向离线/服务校验共32个有限描述反例，八类各4个，覆盖原html/script/event/markup字段、URL/导航/frame/target动作、未知AST/属性引用/原型键、循环/前向结果引用、重复key/UTF-8/类型混淆、深度/节点/尺寸/采样、坏引用/hash/policy、域/非有限值。至少一个非法模型响应经过真实受控模型替身/OneCall/PG，只保存真实调用结算，无artifact；其余复用原件验证API/库/host边界，不为32例发32次模型。

M04 导航/新页/子frame。反例分别含hash、history、data/blob/file/http/https、parent/top、popup/blank/named/form和新增iframe能力请求，全部经生产描述/公开输入/内部v2封包入口拒绝；无可用产物或拒绝input，不能进入自由HTML运行。两正常会话初始化后保持准确两frame/目标基线，独立观察完整URL/fragment/loader/document/target；任何提交或创建FAIL，事件缺失UNKNOWN。它验证新数据边界，无任意脚本导航前否决声称；旧109 hash FAIL不改写。旧B01四种sandbox有限子事实仅在完全未变对象和范围复用，不能代新全成果验收。

M05 网络/文件/下载/XSS。file、回环/外部HTTP/WS、fetch/XHR、图片/字体URL、download、文件chooser/系统/模型工具字段及HTML/SVG/CSS/event注入被严格schema或纯文本边界处理，前四类至少各一反例。生产runtime没有这些能力出口、危险sink或文件/网络接口；核实际产物/载入/浏览器事件/子frame与无秘密合成哨兵结果，不能仅靠没有出网或空日志通过。原宿主代码正常读取固定程序/有界运行临时文件与页面读取文件的禁止分开；不读真实用户或宿主秘密。

M06 计算上界与正常错误。域、规范十进制、bool混数字、step、k le n、前向引用和负域都按明确oracle拒绝；接近节点/采样/迭代上限的描述耗步到限给calculation_limit并保上次一致画面。永久循环代码不是合法描述，必须入口拒绝，不为证明安全执行模型任意循环。固定受信故障夹具另验证宿主忙死的外部停止，不能混作描述安全通过。

M07 管道/输入权。v1/rawHTML init、重复init、未知field/坏nonce/descriptor/policy/hash、超长头/体、乱序/重复异hash、伪console/postMessage、错PNG编码/尺寸/代次均拒绝或停止。两处校验规则及规范JSON跨Python/Node同语义。无owner/异activity/过期owner不能frames/input，普通应用身份仍可精确stop；相同seq同hash不重复处理，未知ACK不回放。伪协议不得改变截止、预算或调用次数。

M08 COMMIT与四账。N1/N2各一合格响应，非法响应一例、发送后断开UNKNOWN一例，共4次受控替身请求；同键并发只一次发送，同键异输入409，丢HTTP回包GET同artifact，不发新模型。新hook强制失败使007/artifact/terminal整体rollback；真实app越权改artifact/旧source/hash或DELETE拒绝。原四账、费用事实与原生停止主权不变，preview退款不触旧账。

M09 资格与迟到。准确在候选帧已进缓存、公开资格查询前暂停，合成来源/父/记忆失效或取消COMMIT后释放，禁止旧帧/正文/input；再核检查后合法在途字节与客户端整组guard。切activity/父/owner/view/preview代次和卸载/隐藏时，HTTP、PNG解码和引用迟到均不能复活。qualification unknown失败关闭但保留成果/费用事实。

M10 预算/刷新/恢复。并发同start_key仅同一session/CID，异键共享3次/180秒；刷新不新启动或获得owner，配置变化不重置。create成功回包丢失按精确身份找回、不二次create；失败扣次数，确认未启动只退未用preview秒；stop未知reserve不退、新start拒绝。应用重启先只读核对和精确救援，不能租约到期抢占或声称旧树已空。

M11 外部停止。用户停止、回学习、隐藏/失联、硬deadline、renderer/browser/Node忙死、Supervisor死亡、Reaper死亡和专用控制路径失联，分别记录实际固定identity/单调计时/外部kill/任务与cgroup/EOF。注入只在冻结合成夹具和精确新资源，诊断variant有独立hash且不作为生产程序的导航安全证据；不存在公开fault开关。控制不可达必须cleanup_unconfirmed和全reserve保留，由获准独立验收控制器仅清理本CID，不停daemon或用户容器。缺任务空原件不得PASS。

M12 兼容与许可。012不存在、坏schema/ACL、policy/bundle缺失或不同，HTML关闭，旧学习/教学/面试/引用/记忆读写的实际受影响签名及能力继续；旧payload不新增None字段，新html11m不能被旧父消费。许可/构建清单完整、产品不依赖公共库/OPEN_project/DocuN临时实现，真实准备/启动/停止链自包含。这里只核受影响边界，不复跑充分未变G3—G10全套。

### D3 一次批次资源组织和隔离终审

以下是待编排冻结的未来建议，不是本卡或109运行许可。复用既有新域采用思路，只新合成PG17及同cluster升级/缺schema库、一个本地API/主应用浏览器会话、一个模型传输替身和一条生产控制链；不启动旧106/103/100/088/109资源，不使用用户private配置或provider。

首次最多12个串行preview创建/启动尝试，实际未start也计创建/产品扣次数，分配为N1、N2、资格race、取消/刷新/预算、renderer忙死、browser/Node忙死、Supervisor死亡、Reaper死亡、create回包丢失、控制路径失联、协议破坏、硬截止。正常会话复用做图形/输入权/迟到，不把每个普通断言拆成新容器；32描述拒绝大部分不启动浏览器。必要修正最多2次相关重测储备，开跑前统一cap14，旧失败和计数不返；同问题两次有据修正仍失败即停重评。

每尝试至多60秒运行加15秒停止诊断，14次运行上界840秒、诊断210秒，总1050秒；一个Reaper验证批固定1200秒，150秒余量用于批内控制/收尾，不运行中延后。每个需要动态观察的实际动作有完整2秒，单preview最多8个此类动作共16秒，ready8秒+输入16秒+其余采集16秒+停止余量10秒共50秒，小于60秒；不能把9项至少18秒塞进15秒。超过该分配必须在开跑前重排或裁定，不临时缩观察窗造通过；非观察式校验不假计2秒运行。

受控模型替身首次4请求，最多2次直接相关修复储备，总6，provider/费用0；身份和OneCall窗口按新卡固定，发送/失败/UNKNOWN计数原样保留。一个离线定向验证批加一次必要typecheck/build，相关普通修正才复验，不反复做前置测试。主应用浏览器会话建议1800秒，HTTP合计<=1024、PNG<=500、公开输入<=300、内部协议输入<=300；每类是总HTTP的子计数或独立内部输入，均不无限相加。启动/构建/PG/realroot/cleanup及实施active/metadata真实上限由完整卡另冻结，不借当前5400秒资料预算。

完整候选和原件稳定后保留一次隔离增强安全/一致性终审，未参与本方案或实施，原107隔离不破坏。只传原目标/最终有效采用、最终diff/加载hash、实际实现与SQL/ACL、正常数值/图形、数据到代码/导航/文件网络、预算资格/停止原件；不传完整实现聊天、思考或自评。审计集中覆盖上述完整高风险成果，普通修正不逐卡加审计，真实新风险仍按其范围补审。无充分动态证据或必需终审不得启用用户生成/预览；隔离合成验证按实施卡许可运行候选不等于用户放行。

## 证据、实际投入、未知与回传

### 本卡证据和文档核对

[input-identity.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-110/solution-20261010/input-identity.json) 保存16个冻结直接输入的实际SHA256/大小，均匹配；7个补充输入和七项公共锁定指纹亦登记，不重算原500对象。[supplementary-input-identity.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-110/solution-20261010/supplementary-input-identity.json) 为本地包/许可两项身份。[reading-scope.md](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-110/solution-20261010/reading-scope.md) 分别登记全文/定向范围及未加载规则。

[local-source-excerpts.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-110/solution-20261010/local-source-excerpts.json) 有6个必要源、11段共123行有限摘录与原身份。[raw-navigation-reading.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-110/solution-20261010/raw-navigation-reading.json) 保存真实Frame/URL/ACK及stdout交叉，不改变原件。[official-sources.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-110/solution-20261010/official-sources.json) 列8个官方资源，7成功/1失败，4源码尝试/3读到；两原生候选、一输出方向，失败页计额，未再研究其它浏览器。移动branch未取commit，只支持API范围，不冒固定151源码或未来构建hash。

公开研究从首次可核17:17:35到17:21:48 UTC，253秒墙钟保守计入研究，低于2400秒；同一已读页面内9次find复用。总资料投入首个可核时钟为17:14:18 UTC，此前读取起点未精确打钟，追加180秒准备保守计入5400秒总上限，最终墙钟与余量见 [delivery-check.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-110/solution-20261010/delivery-check.json)。不把时间窗说成精确CPU投入，也不和旧109投入相加清零。资料路径四次缺失/纠正、一次有限摘录脚本的范围类型错误及有据修正均如实记录；它们没有发生产品运行。

本卡验证只做一次A—D完整、Must/采用变化显式、唯一推荐/唯一采用包、类型/hash/预算/接口计划相容、路径/证据/未知边界和完整可读检查，<=60秒；记录与最终文稿hash见delivery-check.json。只有具体文稿修正才允许一次复检。该检查是B类文档证据，不代动态安全、数学、产品或独立审计通过。

### 具体未证与唯一下一步

未证包括有限解释器/编译器实际实现及两处校验一致、数据到危险sink无通路、真实正常图形/可访问交互与内容质量、新资源实际足够、完整依赖许可证清单、Windows/Docker Desktop无新特权的任务/cgroup空证据路径、真实业务COMMIT/资格race/公开接口兼容及稳定成果独立终审。CEF内部源码失败与全部target/frame覆盖未知已经用于排除，Qtfragment明确缺口已经用于排除；无需下一卡轮流试两候选。旧data/fork、旧未运行反例与已有失败/未知保持原事实。

编排核证本结果后，只需就D1的一个完整G11-P110包取得明确采用，再给一张新完整实施/接线/定向验证/普通修复/收尾卡，前置和精确运行许可在该卡冻结。共享DocuS中架构/强导航合同/profile/API追踪及唯一执行状态更新由主控串行维护，本执行者未写最终验收、未占新任务号、未派发实施。若不采用，保留当前失败和冻结；本卡目标的技术决策输入仍已完整交付。没有合格已解决/验证的新错误经验入库候选。
