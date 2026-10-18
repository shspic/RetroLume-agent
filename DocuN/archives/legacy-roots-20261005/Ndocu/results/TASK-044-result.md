# TASK-044 HTML局部阻塞定向方案审查结果

日期：2026-09-13（Asia/Shanghai）  
类型：只读方案 Review；不是产品测试，不是独立动态安全审计。  
建议任务状态：TASK-044 可按“审查完成、候选成立”回收；B-01 仍为“已有可行候选、待固定版本单次动态验证”，本报告不能把它登记为已验证关闭。

## 1. 结论

候选可作为 B-01 的下一实现决定：在原独立 Docker 受监督浏览器内，由可信顶层 wrapper 创建 sandbox="allow-scripts" 的 iframe，且明确不加入 allow-popups、allow-popups-to-escape-sandbox、allow-top-navigation、allow-top-navigation-by-user-activation、allow-top-navigation-to-custom-protocols、allow-downloads、allow-same-origin。按 HTML Living Standard，这会保留“sandboxed auxiliary navigation browsing context flag”；该标志直接禁止内容创建新的辅助浏览上下文，覆盖 target="_blank" 和 window.open。用户激活只影响另一组顶层导航标志，不会解除辅助浏览上下文标志。因此，普通可信点击触发的新页可由浏览器原生沙箱在创建阶段拒绝，不需要把“CDP 创建后暂停/关闭”改称成功，也不依赖可被页面改写的 window.open 覆盖。

这个判断与 FR-009、SEC-003 和 FLOW-006 的原安全标准一致，没有要求用户接受“已创建但零副作用”这种较弱语义，也没有把生成 HTML 放回主应用浏览器。独立容器、network none、非 root、只读根、资源限额、浏览器 sandbox、无挂载/端口/凭据/工具桥、外部监督停止等原边界必须全部保留。

规范和源码阅读只证明候选设计有依据，不能代替固定镜像中的实际 Chromium 行为。当前 B-01 不能因本报告直接关闭。

## 2. 原标准逐条对照

| 原标准 | 候选判断 | 必要限制或改动 |
| --- | --- | --- |
| FR-009：应用内 HTML 可交互，正常/边界计算和概念可核查 | 原理兼容；allow-scripts 允许内联脚本和普通 DOM 事件。原 energy/probability 两页仅使用 input、button、内联脚本和 CSS 图形条，静态上无冲突 | 必须在固定浏览器中重走原有限输入链；不能以规范推断代替八例实际结果 |
| SEC-003：允许计算/图形脚本 | 兼容；该 token 只解除脚本和相应自动特性限制，并未开放弹窗、顶层导航、下载或同源能力 | 不加入 allow-same-origin。表单提交、模态框、pointer lock、cookie/localStorage 等会受限；当前两页不依赖这些能力。以后生成合同应拒绝或显式标出此类依赖，不能自行加 token |
| SEC-003：默认禁联网、本地文件、系统命令、模型/工具调用 | iframe sandbox 不能独立完成这些边界 | 原 context.route、CDP Fetch/Network 观察、WebSocket 拒绝、network none、无文件/工具接口等仍需保留，并改为覆盖子 frame |
| FLOW-006：独立容器画面和有限输入，主页面不执行原 HTML | 一致 | wrapper 和 iframe 都只存在于容器内浏览器；工作台仍只收画面和有限输入响应 |
| FLOW-006/B-01：新页创建前拒绝 | 规范层成立，且强于旧 CDP 事后关闭候选 | 成功证据必须是可信手势有效、尝试真实发生、目标数始终不增加；page/target 事件出现后再 close 只能算失败或后备防护触发 |
| 顶层导航和下载默认拒绝 | 规范层有对应 sandbox 标志 | 不加入任一 top-navigation、custom-protocol 或 downloads token；仍需固定版本反例验证 |
| 自身导航拒绝 | 候选本身不满足 | HTML 规范明确 source 与 target 是同一 navigable 时允许导航。原自身 HTTP/data 导航阻断必须继续由宿主策略承担，并在新 frame 拓扑下复验；不能把 iframe sandbox 写成全部导航拒绝 |
| 父应用/工具桥不可达 | 不加 allow-same-origin 会给子文档不透明源，阻止其直接读可信 wrapper DOM | postMessage 仍可发送。wrapper 最好不监听不可信消息；若确有显示消息，只能按唯一 frame 的 event.source、严格 schema 和方向白名单处理，不能把 origin="null" 当身份，也不能转成任意宿主命令 |

## 3. 浏览器原生边界与便利层

浏览器原生信任锚是可信 wrapper 在子文档导航前设置的 iframe sandbox 属性及浏览器据此形成的 active sandboxing flag set。HTML 规范说明：省略 allow-popups 会设置辅助浏览上下文阻断标志；选择新 navigable 时该标志使新目标选择失败，window.open 随后返回 null。顶层导航的“有/无用户激活”是另外两项标志，二者都因本候选未加 token 而保持。Chromium 当前官方源码还有浏览器进程侧回归测试：allow-scripts 且无 allow-popups 的 frame 被标为 kPopups sandboxed；即使模拟受损 renderer 直接发 CreateNewWindow IPC，也应终止该 renderer且窗口数不增加。这支持它不是单纯页面 JS 约定。

以下都不是 B-01 的成功信任锚：

- INIT_POLICY 对 window.open 的覆盖：不可信页可尝试改写或删除，只能作为易用提示；建议从新页成功判定路径移除。
- context.on("page") 后立即 close：这是事后后备防护；一旦事件出现，就说明“创建前拒绝”未通过。
- Target.setAutoAttach 后暂停/关闭：目标已经创建，仍只适合旧方案的零脚本副作用论证。
- 普通浏览器弹窗拦截策略：旧提案已确认可信手势可例外，不能代替 iframe sandbox 标志。

## 4. 旧宿主的最小实现影响

核对的旧 host/host.cjs 固定 SHA256 为 691DA71D33CD29A484BD2C1F8A4FD2978B88B0B58B886C6188D21104EEDDEF74。它当前在第 216—220 行直接 page.setContent(html)，第 223—246 行用主 frame locator 完成 fill/click/read，第 159—163 行把新 page 创建后关闭；这三处需要有界调整：

1. open_page 先加载固定的可信 wrapper，再由可信代码创建唯一 iframe；必须先设置完整 sandbox token 集合，再用 srcdoc/等价安全赋值装入原 HTML。不能把不可信字符串拼进 wrapper 的 script、属性或模板文本。原 HTML 文件及 hash不变。
2. 状态保存并绑定该唯一子 Frame/FrameLocator。fill、click、read_output、手势探针、doc identity 和所有页面侧反例都在此 frame 内执行，禁止使用“任意 frame 搜索”。截图仍可取整页画面。
3. click_xy 的协议范围仍是 640×480，且继续核对点击位于白名单目标内。Playwright 官方说明子 frame 元素的 bounding box 以主 frame viewport 为坐标，因此现有坐标协议可保留；但实现必须从子 frame 中取得目标框，不能再在 wrapper 主文档找 #calc。
4. 所有 context.route、WebSocket、Fetch/Network、download deny 和浏览器进程观察继续保留。要确认它们实际覆盖子 frame；wrapper 自身的初次 about:blank/srcdoc 装载应与后续不可信导航事件区分。
5. 新页检查改为“目标清单/页数基线不变且没有新 page/targetCreated”。可以保留自动 close 作为异常收束，但判定器见到它必须失败，不能因关闭成功而通过。
6. 旧 C11 的 parentIsSelf/topIsSelf 判据不再适用，因为 iframe 中 parent/top 本来就不是自身。替换为：不透明源；访问 parent.document/可信 wrapper 状态抛 SecurityError；无 retrolumeBridge/chrome.runtime；伪造 postMessage 不触发任何协议结果或宿主动作。
7. 可信 wrapper 自己持有 iframe 属性，子页不具备同源 DOM 访问能力，不能取得并删除 sandbox。不得加入 allow-same-origin，也不得暴露可令子页要求 wrapper 修改 sandbox/srcdoc 的消息命令。

Playwright 官方 frame locator 和 frame API 已直接支持 iframe 内定位、fill 和 click，不需要新依赖或开放任意 CDP。现有有限协议的 op、字段白名单、数值/坐标上限可以保留，只改变内部目标 frame。

## 5. 必要反例与兼容限制

必须明确保留以下反例，防止只修 B-01 却回退原边界：

- 可信普通左键点击 target="_blank" 的 data/about:blank 锚点；记录 click event.isTrusted 与 userActivation，尝试后浏览器 target/page 数不增加。
- 可信点击事件内直接调用原生 window.open，返回 null，且 target/page 数不增加。
- 新命名目标与 form target="_blank" 各一例，用于覆盖非单一路径。表单例会同时受 forms sandbox 标志影响，不能单独作为 popup 机制证据。
- 对照只使用无害 about:blank：同一容器内的合成控制 frame 临时加入 allow-popups 后，可信点击能创建目标；该对照只证明探针可触发，不进入产品 wrapper。
- 自身 location 到 data: 与 HTTP 两例必须仍被宿主原策略拒绝、frame 文档身份和 URL 不变。若发生自身导航，即使新页为零，整体候选集成仍不满足 FLOW-006。
- 伪造 parent.postMessage、访问 parent.document、外部 fetch/WebSocket、file fetch 和 download 各保留一例，只核对新 frame 拓扑未绕过现有宿主层。不存在的文件或无监听服务不能独立算阻断证据。

仅 allow-scripts 会有意限制 form submission、modal、pointer lock、真实源身份和持久存储。当前两份固定 HTML 不使用这些能力。若产品后来需要其中任何能力，应先判断是否属于 FR-009 必要交互；需要新增 iframe token 时才是新的页面权限决定，按 SEC-003 独立批准和审计，不能在实现中静默加入。

浏览器 UI 的 Ctrl/中键“在新标签页打开”不在当前有限输入协议中；协议没有任意修饰键或浏览器 chrome 操作。若未来协议开放这类输入，需要另加反例，不能从本结论外推。

## 6. 最小可证伪下一卡

建议下一卡只做一次“固定 wrapper + 单容器最小验证”，不重跑四容器套件：

- 输入：原 hash 不变的 energy.html 与 probability.html；Playwright 1.62.1、Chromium 151.0.7922.34、原镜像 digest 和全部容器隔离参数冻结。
- 正常交互：复用两页原八例和有限协议截图/读值，证明 frame 改造未破坏输入、计算和 CSS 图形反馈；不扩展模拟器或模型样本。
- 新增边界：上述四个新页路径、一项无害正对照、两项自身导航回归、父 DOM/消息桥回归。
- 上限：1 个容器，仍按 create≤30s、运行窗口≤30s、watchdog 25s、最迟 28s 确认停止；失败即停，不重试、不下载、不安装、不新增权限。无需请求四容器/120秒套件。
- 成功门：可信手势和真实尝试均成立；产品 sandbox frame 的 target/page 基线始终不变；原八例正确；自身导航及父/网络/file/download 既有拒绝未回退。任一新 target/page 创建、wrapper token 被改变、探针跑在主 frame、或正常交互失效即失败。
- 通过后再由新的隔离 Session 对固定实现及原始证据做必要独立审计。普通 Review 或同一执行 Session 自检不能替代该审计。

这张下一卡不要求用户改变已锁定边界，也不引入依赖、费用、数据外发或新页面权限。是否运行 Docker 仍需由 Astra 按现行执行权限登记具体卡；本 TASK-044 没有该授权。

## 7. 已核证据、版本和限制

| 证据 | 本次用途 |
| --- | --- |
| D:/shspic/project_NO3_RetroLume-agent/docu/LATER_REQUIREMENTS.MD 第 66、82、110 行 | FR-009/SEC-003 原标准 |
| D:/shspic/project_NO3_RetroLume-agent/docu/PROJECT_ARCHITECTURE.md 第 118—126、267、302 行 | FLOW-006、RISK-004、B-01 的现行架构边界 |
| D:/shuice12/RetroLume-SPIKE-017/task-036/run-proposal-v5.md，SHA256 65771CA08FAB6372900609E566D98D947EBCC15B092CD7B64387BA6ABB4ABBE8 | 旧 B-01 对象拆分、CDP 方案限制和原最小实验 |
| D:/shuice12/RetroLume-SPIKE-017/task-036/host/host.cjs，SHA256 691DA71D33CD29A484BD2C1F8A4FD2978B88B0B58B886C6188D21104EEDDEF74 | 当前主 frame 加载、有限协议、JS便利层、事后关闭实现 |
| D:/shuice12/RetroLume-SPIKE-017/task-036/checks.json | 原状态保持：9 pass、0 fail、48 not_run、0 block计数；总判定仍因 B-01 开放而“阻塞” |
| HTML Standard sandboxing flags：https://html.spec.whatwg.org/multipage/browsers.html#sandboxing-flag-set | allow-popups 缺失时设置辅助上下文阻断；allow-scripts 只解除脚本/自动特性；无 allow-same-origin 时为不透明源；无 allow-downloads 时禁止下载 |
| HTML Standard iframe sandbox：https://html.spec.whatwg.org/multipage/iframe-embed-object.html#attr-iframe-sandbox | token 的权限语义及 allow-scripts + allow-same-origin 同源风险 |
| HTML Standard target selection：https://html.spec.whatwg.org/multipage/document-sequences.html#the-rules-for-choosing-a-navigable | sandboxed auxiliary navigation 标志阻止选择/创建新 top-level traversable；window.open 无目标时返回 null |
| HTML Standard navigation check：https://html.spec.whatwg.org/multipage/browsing-the-web.html#allowed-by-sandboxing-to-navigate | source==target 时返回 true，证明 iframe sandbox 本身不禁止自身导航 |
| Chromium HEAD 浏览器侧回归测试：https://chromium.googlesource.com/chromium/src/+/HEAD/content/browser/security_exploit_browsertest.cc#2351 | allow-scripts 且无 allow-popups 的 frame 在 browser process 侧保持 kPopups，拒绝直接 CreateNewWindow IPC |
| Playwright frames：https://playwright.dev/docs/frames 与 boundingBox：https://playwright.dev/docs/api/class-elementhandle#element-handle-bounding-box | 子 frame 定位/输入可用；子 frame 元素坐标相对主 frame viewport |

固定版本限制：本地冻结清单写明 Playwright 1.62.1、Chromium/Headless Shell 151.0.7922.34 和基础镜像 digest sha256:c091b21d9fae78c76e85cd4356431e9b018402f172a214fc7d7a5e9a7e29d8ac；本次没有启动该浏览器。Chromium HEAD 回归测试不是该镜像 digest 的运行证据，HTML Living Standard 也会更新。因此结论是“设计有充分依据、值得实施一次最小验证”，不是“固定浏览器已实测通过”。

本次只读检查没有运行 Docker、浏览器、产品测试或模型/API，没有安装/下载、读取凭据/真实数据，也没有修改代码、夹具或共享文档。唯一写入为本结果文件；全局状态、CHANGE 和最终验收留给 Astra。
