# TASK-094 / R-088 修正轮01 G6活动可观测与用户控制入口完整接线合同（当前有效）

## 0. 修正结论

K1—K5 已一次收敛：提交意图改为客户端持久意图台账（刷新可恢复、绝不自动重试或自动换键）；四类读取改为每请求恰一条 SQL 快照并删除整页超限失败路径；监督配置九字段映射、能力三层失败关闭与事实文案补全，时间硬停止与墙钟判定分层表述，G5 两缺口时点更正；批准包收敛为唯一一项「浏览器活动动作面与服务端配置受控接线」，明确不含用户库迁移与真实付费验证；实施边界改为专用合成库端到端，产品库未迁移时按 storage_not_ready 失败关闭。首轮全文保留于文末作历史，冲突处一律以本节为准。

## 1. 修正轮身份与读取增量

同窗同 A+（Claude 桌面 Code 窗口，claude-fable-5）。首轮 43 项读取零漂移复核：40 项逐字节一致；变化恰为 3 项且均属预期（架构动态文档 v0.65 至 v0.66、执行动态文档 v1.87 至 v1.88、本卡更新为修正轮01），变化部分已重读。本轮新读并登记于 [files-read-hashes-revision-01.json](../evidence/TASK-094/revision-01/files-read-hashes-revision-01.json)：repository.py 的 _transaction 与 _RESULT_READ_SQL、materials/repository.py 方法清单、.gitignore 全文、本卡与 [K1—K5 裁定](TASK-094-work-decision.md) 全文。运行与费用 0。

首轮更正点（已并入本节正文，不再只是勘误尾注）：一，原三项批准包收敛为一项并剔除用户库迁移与真实付费验证；二，TrustedHost 实为 127.0.0.1、localhost、testserver 三项，保持不改；三，时间「硬停止」表述分层（本机单调时限硬停止为已验事实，墙钟只影响账本资格判定）；四，092 最终验收已将 E1（2048 边界）与 E2（real06 证据）关闭，旧夹具原件未找回属编排已裁定的保留历史事实，不再是待处理缺口；五，认证机制「稳定工作」的表述收窄为既有资料/PDF 范围，活动面属新代码未运行验证；六，新建后的产品状态诚实为「等待学习入口接入」，验收对已存在父成果使用明确标注的合成种子。

## 2. K—源码定位—修正决定—矩阵目标

K1 动作身份与响应丢失恢复。
- 源码定位：service.py 116—125（同键只核事实、不生成替代键）、153—178（监督任务与 shield 等待）、196—211（工具同键分支）；repository.py 1020—1023（同键拒绝）；frontend/src/main.tsx 53—138（现状仅会话内状态，无持久意图设施）。
- 修正决定：活动 UUID 与继续操作键在「意图」创建时由客户端生成一次，存入本机浏览器存储的意图台账；台账只含业务键与用户自己输入的文本，不含密钥或任何授权物，不被服务端读取、不构成授权；刷新或重开后仅显示「上次动作未确认」横幅与三个显式动作（核对、同键重试、放弃），写入类动作绝不自动执行、绝不自动生成替代键。创建 409 必须先只读核验（见 B4）才能声称该意图已实现。「无行且无窗口」只表述为「尚未发现该动作开始的持久迹象；即使原请求稍后到达，同键至多一次执行」，不表述为「确定未发出」。零新增服务端字段即可完成核对；若实施中证明必须新增持久结构，停止该改动并携具体影响并入唯一批准包。
- 矩阵目标：C2、C5、C9。

K2 一致性与大小。
- 源码定位：repository.py 238—267（_transaction 未设置固定读快照；多条 SELECT 在 psycopg 默认 READ COMMITTED 下各自取快照）；1643—1711 与 1713—1811（现有 read/list 各为单条 SQL）；1573—1597（_RESULT_READ_SQL 绑定列集合）。
- 修正决定：四类读取每请求恰一条 SQL，状态与绑定判定全部在该条 SQL 内以 CASE 表达式完成（沿用 _RESULT_READ_SQL 模式），payload 合规复算在返回行上做纯函数校验、不二次读库；不依赖任何隔离级别默认值；不改原写路径。操作列表不携带正文且行投影字段全部有界（B2 列明），删除整页 256KiB 失败语义；单条结果读取是唯一正文通道，其可读性由既有 131072 字节正文契约保证，任何合法已存在正文永远可读。游标与空页规则按 B2 的 limit 加一探测明确。
- 矩阵目标：C1、C12。

K3 配置与事实文案。
- 源码定位：session.py 42—74（SessionConfig 九字段、两条构造不等式、manager_total 为 window 加 overhead）；session.py 154—170 与 280—285（claim 前早拒与窗口余量检查）；service.py 128—130、214—216（request_timeout 不超过 120 与 service.timeout 不超过 request_timeout 的服务层早拒）；main.py 41（TrustedHost 实含 testserver）。
- 修正决定：给出能力三层与完整监督配置映射（B5），缺配置按层失败关闭，读取与取消在无任何配置时也可用，密钥缺失不阻塞零费新建；监督参数首切片固定为代码默认并经构造不等式校验，不作为用户配置暴露，部署声明保持 False（陈旧窗口只走取消路径），无热重载、变更需重启。事实文案改为账本口径（B7）：运行中是账本事实且执行存活未知，不得由 running 断言进程仍在或服务曾中断；时间语义分两层，本机单窗口由单调时限硬停止属已批准 D3 事实，墙钟只影响账本租约与到期的资格判定口径（M-1 未闭合仅限此层），S 的累计来自单调测量的实际耗时。092 最终验收已关闭 E1/E2 的结论按此表述，不再列为待处理。
- 矩阵目标：C4、C9、C11。

K4 授权打包。
- 事实定位：本卡无法也不去核实产品库身份、迁移史、备份位置与恢复验证（不读取本机私有配置）；002/003/004/005 的历史执行与空表门事实均只覆盖合成库。
- 修正决定：唯一批准包为「浏览器活动动作面与服务端配置受控接线」一项（6.1），绝对不含用户库操作与真实付费验证；下一实施卡只用专用合成库，产品库默认显示 storage_not_ready 并全部失败关闭；用户库迁移留待有具体对象、备份与恢复方案、空表门事实可审阅时另行单独授权，且不作为当前代码与合成验证的前置；付费接线与真实启用分离，配置存在不构成 Agent 使用真实密钥的许可，实施与验收全程真实请求与费用 0。
- 矩阵目标：C2、C4、C11。

K5 闭环与代码事实。
- 源码定位：materials/api.py 17—31（local_request 与会话比对的具体实现）、pdf_review/api.py 11（跨模块 import 该模式）；main.py 41；.gitignore 现状（config/database.local.json 等已忽略）。
- 修正决定：诚实闭环，新建后为「等待学习入口接入」状态，不声称新建到首次学习已闭环；验收涉及已存在父成果的核对一律使用明确标注的合成种子（非产品链）。完整修改与新增文件清单（B8）含认证提取（新增 local_session.py，materials 与 pdf 改 import，拒绝码与文案逐字保持，既有 test_materials/test_pdf_review 为兼容门）、配置模板 config/activity.example.json（提交、含不可用占位值）与 .gitignore 增补 config/activity.local.json、前端意图台账与工作区、测试清单。材料标题与版本有效性、本地会话判定只按代码与既有资料/PDF证据范围陈述；活动面为新代码，本卡未运行验证。
- 矩阵目标：C6、C7、C10。

## 3. 修正后 A 事实地图与用户闭环

### 3.1 差距地图

已有可复用（代码与证据范围同首轮，结论不变）：001—008 持久模型与四账；read_committed_result、list_committed_results 与 ResultReadStatus 七态（G3）；cancel_activity 幂等与保守折叠（G3/D3）；continue_from_result 与 execute_tool_action 的固定 launcher/SUP/worker/Job 链（090/G5，适用范围内不重跑）；资料/PDF 的本地会话边界实现（既有证据范围）。既有 read/list 均为单条 SQL，满足本次单快照规则，直接复用。

需新增（本合同对象，均不新增DDL）：活动/操作读取 HTTP 面与脱敏投影；活动列表、活动详情、操作列表三条有界且单条 SQL 的只读查询；新建、取消、显式继续三个动作入口与服务端身份派生；客户端意图台账（仅本机浏览器存储）；本地配置三段（模型标识、活动额度、密钥经环境变量）与能力三层失败关闭；前端工作区与文案。

仅历史实验或不在本卡：13 元旧实验预算与旧合成资源（保留原状不复活）；首次学习动作（业务卡）；工具动作UI、范围修订UI、未知操作收敛UI、SSE/Redis（不在本卡）。

### 3.2 用户完整旅程（目标态；诚实边界在此明确）

进入工作区 → 新建活动（选当前有效资料范围；只读展示服务端配置的额度；创建零调用零费用）→ 活动就绪并显示「等待学习入口接入」（本切片不产生首次学习动作，界面不设假按钮；验证时以合成种子构造既有父成果）→ 成果显示（逐项操作状态与正文可用性）→ 显式继续（仅对已提交且正文可回查的模型成果出现；提交前显示剩余额度与最坏等待口径；键在意图生成时确定并进入意图台账）→ 运行中（账本事实「运行中」，执行存活未知，最后更新为页面读取时间）→ 失败（白名单错误码文案，区分「被拒绝未开始（无操作行）」与「尝试过（有操作行）」）→ 取消（不再开始新动作；本机窗口按单调时限自行停止；远端不可撤回；次数费用不退还）→ 刷新、断线或重开（只重读；未确认意图以横幅呈现，核对与重试均为显式动作）→ 显式发起新动作（新意图、新键、重新显示额度、重新权威准入）。

### 3.3 只读恢复与重新执行、未批准前置

GET 一律无副作用；重新执行只在用户显式动作且服务端锁内权威准入通过时发生。当前唯一未批准的主要信任接口是浏览器活动动作面与服务端配置受控接线的单一包（6.1）。用户库迁移不再是前置（合成实施）；真实付费启用属用户本机行为，Agent 全程不使用真实密钥。界面不显示任何尚不能运行的按钮承诺。

线框与状态文案全文见 [wireframe-workspace.txt](../evidence/TASK-094/wireframe-workspace.txt)（已按本修正同步：能力分层、存活未知、意图恢复、时间两层语义）。

## 4. 修正后 B 唯一推荐实施合同

### B1 事实权威

字段来源与派生公式同首轮 B1（活动列表行、详情四账、操作与正文、可用额度公式、NULL 与 0 的区别均保留），以下四点按修正收敛。一，取消时间与状态仍全部取自 activities 行；execution_generation 与 dispatch_closed 仅用于按钮可用性推导，不展示。二，操作投影字段有界且固定：operation_id 不超过 128、kind、state、disposition、error_code 不超过 64、reserved_at、dispatch_started_at、recorded_at、prompt_tokens、completion_tokens、finish_reason 不超过 64、returned_model 不超过 128、committed_at、payload 可用性（布尔）；hash、admission_id、executor_id、G、remote_request_id 一律不出投影。三，时间语义两层：本机单窗口由 SUP 以单调时钟固定 stop_ns 并终止自有 Job（已批准 D3 事实，属实际停止证明）；账本 lease_expires_at 与 deadline_at 为墙钟判定，系统时间调整只影响开新窗口的资格口径（M-1 未闭合仅限此层）；S 由单调测量的实际耗时向上取整累计，不称墙钟累计。四，运行中是账本事实；执行存活无法由账本证明，界面统一显示「执行存活未知」，不得据此断言「仍在运行」或「服务曾中断」。

### B2 读取与历史

轮询唯一推荐不变；不虚构事件流与完整历史不变。以下为修正后的读取与大小契约。

单快照规则。四类读取每请求恰一条 SQL；绑定与状态判定全部在该条 SQL 内以 CASE 表达式完成（沿用 _RESULT_READ_SQL 的 binding_consistent、scope_current、sources_valid 三联列模式）；payload 的规范字节复算在返回行上做纯函数校验，不二次读库；不依赖 READ COMMITTED 之外的任何隔离假设，也不得改用多语句组装视图。实现提示：三条新查询各自单条 SQL 可完成（活动详情用 jsonb_agg 汇总范围与逐项有效性），无需事务级快照设置。

端点（不变部分从首轮）：GET /api/activities/capabilities（另回报能力三层旗标与 wait_bound_seconds、window_seconds 两个只读数字，供文案使用；声明顺序须先于带参路由）；GET /api/activities；GET /api/activities/{activity_id}；GET /api/activities/{activity_id}/operations；GET /api/activities/{activity_id}/operations/{operation_id}。

分页与上限。活动列表按 created_at 与 id 双键倒序，游标为服务端编码对，limit 默认 20、最大 50；操作列表按 operation_id 主键序，游标为上一页末键，limit 默认 20、最大 100。两者均以 limit 加一探测下一页，仅当存在额外行时返回 next_cursor，否则为 null；空页合法且 next_cursor 为 null；无法解码的游标返回 400 invalid_cursor，前端回第一页（等价回快照）。切片内无删除，锚行不消失；新增行在头部不影响倒序扫描；排序键不可变。

大小界限。操作列表不携带正文，行投影字段全部有界（B1），页编码不存在超限失败路径，删除首轮「整页 256KiB 直接失败」语义；单条结果读取是唯一正文通道，正文上限沿用既有 131072 字节契约并可加 256KiB 帧保护，二者保证任何合法已存在正文永远可读。可辨响应不变（403/400/404/503 与 200 内 read_status 枚举）。

一致性与轮询不变：页内单快照；跨请求不合并承诺视图；动作后立即重读；自动刷新仅在有运行中或未确认意图时进行、只发 GET、约 3 秒、可中止、不并发；断线重连只重读。

### B3 动作与信任

动作集不变（新建、取消、继续纳入；工具动作、范围修订、额度修改、首次学习、未知收敛不开放）。

信任边界修正后表述：新动作面沿用既有本地会话边界（仅 loopback 监听；TrustedHost 现值为 127.0.0.1、localhost、testserver 三项，保持不改并如实登记；local_request 拒绝 cross-site 与未知 Origin；动作端点要求 X-RetroLume-Session 常量时间比对；自定义头阻断简单 CSRF，跨站预检无 CORS 许可）。认证提取为共享依赖后行为逐字保持（B8 清单）。localhost 不是授权；只承诺抵御跨站浏览器攻击，不承诺抵御同账户恶意本地程序。不新增公网认证、端口或代理。

服务端掌握上下文不变（客户端只提供业务键与用户文本；executor_id 固定为 local-ui；run_tag 服务端生成；G、scope、额度、DSN、密钥、argv 不接受自客户端；权威判定全在既有锁内）。动作语义如实显示不变（取消只使资格失效并保守折叠，不即时杀树、不撤回远端；继续至多一次受控调用；查询无副作用）。新增说明：意图台账不是授权，服务端不读取它；同键至多一次执行由服务端主键约束保证，与客户端台账无关。

### B4 幂等与恢复（按 K1 重写）

客户端意图台账。位置为本机浏览器存储（建议 localStorage 单键 retrolume.pending-intents.v1，数组）。条目字段：intent_id（随机）、kind（create 或 continue）、activity_id、operation_id（continue）、parent_operation_id（continue）、followup（continue，用户自己的文本）、created_at、state、last_error_code（可选，白名单码）。绝不存结果正文、payload、密钥、令牌或任何授权物；台账可被用户清除且清除无害（仅失去恢复提示）。台账不是幂等保证，服务端主键才是。

状态机。意图创建（生成键，pending）→ 提交（submitted）→ 服务端确认成功（confirmed，界面展示事实后移除条目）→ 明确拒绝（refused，保留原因供用户处理）→ 网络失败或超时（unconfirmed）→ 用户放弃（abandoned，移除且该键此后不再使用）。页面加载时对 unconfirmed 与 submitted 条目只做只读轮询并可展示横幅；写入类动作仅由用户点击触发，绝不自动。

创建流程与 409 核验。重复提交同键，服务端以 activities 主键拒绝并返回 409 activity_exists；前端必须只读核验后处理：读取该活动与其实际范围来源集合，与意图的 source_ids 集合一致才可视为「该意图已实现」并展示（额度以库中实际为准，不显示预览值）；不一致或读取不果则如实报告冲突，不声称创建成功。来源竞态拒绝（source_replaced 一类）不是冲突，提示刷新后重选，键可继续用于该意图重试。

继续流程。键与文本在意图内绑定；用户想改文本必须放弃原意图并以新意图新键发起（服务端不承诺同键异文识别，模型动作的父键与文本不持久，客户端台账负责此纪律，且该纪律不冒充服务端检测）。同键重试安全：原请求未到达则成为首次提交；已在途则被有界拒绝（local_owner_busy 或租约冲突）或返回既有事实；已完成则只读事实；任何情形至多一次执行、至多一次预扣。并发同键至多一个监督尝试。

响应丢失、刷新与断线。响应丢失即 unconfirmed；刷新后横幅提供核对（只读）、同键重试（显式）、放弃三动作；核对只轮询读取，不因等待超时升级为写入；「尚未发现开始的持久迹象」不得表述为「确定未发出」。

其余场景（超时映射 unknown 不重发；时间预算耗尽与锁内拒绝不留操作行且区分「未开始」与「尝试过」；来源替换与范围修订按 B1 状态呈现；旧代次晚到无新资格；取消无需意图记录且幂等）同首轮并继续有效。身份持久性：键一经服务端持久即不可复用为新意图；服务重启后一切以持久行判断。

零新增服务端字段。核对完全基于既有读取；若实施发现确需新增持久结构（例如服务端意图表），停止该改动，给出具体字段、迁移与影响，并入唯一批准包（K4），不得暗加。

### B5 配置与预算（按 K3 补全）

能力三层与失败分层。L0 读取与取消：仅需存储就绪（storage_ready，活动表探测）；无任何配置也可用。L1 新建：需模型标识段与活动额度段（构造 ActivitySpec 校验；allowed_models 必须非空是 repository._validate_spec 既有要求），不需要密钥。L2 继续：在 L1 之上还需密钥环境变量存在。缺密钥不阻塞 L0 与 L1；缺标识或额度不阻塞 L0；任何缺层只关闭该层能力并显示对应文案，不产生半可用状态。

配置来源。新增本地私有配置 config/activity.local.json（忽略规则增补见 B8），含 model_identity（provider、model 两项，无密钥）与 activity_defaults（deadline_hours、max_requests、max_cost_microunits、reserve_cost_microunits、max_request_bytes、max_output_tokens、max_running_seconds、allowed_tools、max_tool_calls）两段；密钥经环境变量注入，变量名在配置文件中声明、值不进文件不进响应。提交 config/activity.example.json 模板，占位值必须无法通过校验（直接复制示例不产生可用能力）。测试值（092/090 夹具数值）不迁为产品值；项目不自带静默默认。加载时点：应用启动时加载一次并用既有校验器逐项校验，生成能力旗标；动作请求时使用已加载值并复查旗标；无热重载，配置变更需重启。

监督参数完整映射（首切片固定为代码默认，不作为用户配置暴露；对用户可见的只有 wait_bound_seconds 与 window_seconds 两个只读数字）。

- window_seconds 90，单窗口时长，claim 按可用余额预扣 W_eff 为 min(W, 可用)；构造不等式 W 大于 startup_limit 加 request_timeout 加 stop_grace 已由 session.py 强制。
- request_timeout_seconds 10，worker 业务整体时限；服务层另有 service.timeout 不超过 request_timeout 不超过 120 的双重早拒（service.py 既有）。
- stop_grace_seconds 5，窗口内停止预留。
- startup_limit_seconds 5，claim 后到 armed 的启动上限。
- manager_db_timeout_seconds 5，单次 DB 等待上限。
- cleanup_seconds 5，清理上限。
- mutex_wait_seconds 3，活动互斥等待上限。
- manager_overhead_seconds 30，管理余量；构造不等式 overhead 大于 mutex_wait 加 3 乘 manager_db_timeout 加 cleanup 已由 session.py 强制。
- 派生 manager_total_seconds 为 window 加 overhead 等于 120；这是「发出并等待」的最坏等待口径，UI 与 capabilities 一致显示。
- 部署声明 single_host_single_session_recovery 固定 False（不暴露）：陈旧窗口不使用 D3 接续折叠路径，只走用户取消（B6）。

展示与确认、失败关闭不是免费默认、费用授权不扩大（同首轮）：新建表单只读展示额度预览；修改者只有用户本人编辑配置文件；无运行时扩额接口；G5 的 max_tool_calls 为 NULL 语义保持；真实付费启用为用户本机行为，配置存在不构成 Agent 用真实密钥的许可，设计为本阶段真实请求与费用 0。

### B6 长任务与隔离

HTTP 生命周期不绕过监督不变（继续经 to_thread 监督线程与固定链，shield 语义保持，最坏等待为 manager_total 120 秒；断开不取消、不重放、不伪称取消）。不新增后台服务、队列或持久结构不变；并发动作不排队、被有界拒绝不变。

服务进程重启修正表述：若监督途中应用进程退出，持久事实是权威；界面显示账本状态加「执行存活未知」，不得显示「服务曾中断」。陈旧 running 的唯一自愈路径是用户取消（R 保守折入 S，无会话门槛）；部署声明保持 False，因此下一次显式动作对陈旧窗口按既有 SUP 逻辑失败关闭（JobUnknown），不折叠、不重发；未来若开启 D3 单机接续折叠需另行显式变更，不在本切片。

### B7 展示与隐私

文案按修正后的账本口径（清单同步于线框文件）：运行中为账本事实、执行存活未知；不得出现「服务曾中断」；时间说明分两层（本机单调硬停止已验；墙钟只影响开新窗口的资格判定）；storage_not_ready 与能力三层（新建未开放、继续未开放）文案；未确认意图横幅与三动作文案；错误码白名单外显示「内部错误（未分类）」。其余不变：不显示 SQL、runner、堆栈、异常 repr、hash、admission_id、executor_id、G、remote_request_id、路径与 argv；正文纯文本低信任；PDF 先核对的门保持（待核对 PDF 无当前可用版本）；金额按微单位整数；意图台账不含密钥并可清除。

### B8 修改与兼容、实施顺序（按 K5 补全清单）

新增文件：backend/app/local_session.py（本地会话共享依赖，行为等价提取）；backend/app/activities/api.py（活动路由）；backend/app/service_config.py（建议名，配置加载与能力旗标）；config/activity.example.json（提交，占位值校验失败）；frontend/src/activities/ActivityWorkspace.tsx 与其样式；backend/tests 新增活动读取/HTTP/动作测试文件（命名由实施卡定）。

修改文件：backend/app/materials/api.py（改为引用共享依赖，拒绝码与文案逐字保持）；backend/app/pdf_review/api.py（改 import）；backend/app/activities/repository.py（仅新增三条只读方法与投影辅助，既有方法与 _transaction 不改）；backend/app/activities/service.py（新增薄读取与取消包装，continue 签名不变）；backend/app/main.py（挂载路由、注入配置状态；create_app 签名兼容）；frontend/src/main.tsx（导航与工作区挂载，资料视图不动）；.gitignore（增补 config/activity.local.json）。

明确不改：001—008 迁移与全部持久模型、worker 全部文件、capabilities 契约与 gateway、one_call/one_tool 协议、session/launcher、materials 与 pdf 语义、TrustedHost 列表（含 testserver）、需求基线。无任何新增持久模型；若实施需要则停止并入唯一包。

兼容门：test_materials、test_pdf_review、test_config 必须原样通过（认证提取等价性由它们作证）；test_activity_results 与其它按影响范围复核，不弱化断言。

实施顺序（单卡连续）：一，共享会话依赖提取与兼容门；二，配置加载三段与能力三层旗标；三，仓储三条单 SQL 只读方法与状态同源测试；四，HTTP 只读面与脱敏、可辨响应、分页边界；五，意图台账与新建动作（含 409 核验）；六，取消动作；七，继续动作（身份派生、分层失败关闭、与监督线程边界、最坏等待文案）；八，前端工作区全量文案与未确认横幅；九，合成端到端与资源收尾、文档增量。稳定后独立审计仅限实际新增信任边界（浏览器动作面）与影响。

失败映射增补：503 storage_not_ready（表缺失）；409 layer_not_configured（新建缺额度或标识）、provider_key_not_configured（继续缺密钥）；其余同首轮（400/403/404/409 各码与 200 内状态枚举）。

## 5. 修正后 C 定向验收矩阵

均为下一实施卡的检查设计；运行时冻结源码、样本与上限；括注为对应 K。

C1 读取单快照与投影一致（K2）。预期：四类读取各为单条 SQL，行内自洽，状态与 read_committed_result 同源；白名单外字段不出现。最小样本：含 model 与 tool 两 kind、覆盖 committed_current 与 invalidated_source 与 unresolved 的一个活动；并发一笔写入期间的读取。证据：离线断言加合成PG逐行对照。环境：合成PG 必须。

C2 新建与幂等（K1、K4）。预期：双击与响应丢失后同键重试不产生第二个活动；409 核验两变体（范围一致视为该意图、不一致如实报冲突）；来源竞态明确失败；缺配置按层失败关闭零写入。最小样本：同键两次、竞态一次、缺额度一次、409 不一致一次。证据：HTTP 级原始请求响应加PG行数断言加浏览器一条。

C3 取消与恢复真实语义（不变）。预期与样本同首轮；复用 D3/G5 停止主体证据。

C4 继续正常链与配置分层（K3、K4）。预期：缺密钥、缺额度、缺标识三层各自失败关闭且只读与新建不受影响；合成 transport 替身下经真实链完成一次，received 加正文落库，请求与费用各加一，时间按实际结算。最小样本：三层缺配各一加一条 Windows 组合（零真实网络）。环境：真实 Windows 一条。复用：链主体 090/G5 证据，不重跑全套。

C5 双击与同键竞争（K1）。预期：并发同键至多一次监督；第二者 busy 或租约拒绝；零第二次预扣。样本与证据同首轮（事件屏障，不用 sleep）。

C6 权限反例与认证提取兼容（K5）。预期：无会话头 403、跨站 403、坏 UUID 400、跨站预检阻断；materials 与 pdf 拒绝码与文案逐字不变。最小样本：四反例加既有 test_materials/test_pdf_review/test_config 全绿。证据：HTTP 级加浏览器一条加既有测试。

C7 敏感不暴露（K1、K3）。预期：响应与界面无内部标识、hash、路径、密钥；意图台账内容仅业务键与用户文本；错误仅白名单。最小样本：错误路径注入后全文检索加台账结构检查。证据：离线扫描加浏览器目视。

C8 来源与范围变化（不变）。替换与修订两样本，合成PG。

C9 断线与刷新重启、意图恢复（K1、K3）。预期：未确认横幅出现；核对、同键重试、放弃三动作行为正确；刷新与断线无任何自动写入；存活未知文案正确；取消自愈陈旧窗口。最小样本：响应丢失一次、刷新一次、断网一次、陈旧窗口取消一次。证据：浏览器手工加服务日志加合成PG 支撑。

C10 资料页不回归（K5）。预期与样本同首轮；加认证提取后 materials 与 pdf 的界面流一条。

C11 配置分层与监督参数（K3）。预期：三层旗标与文案独立正确；capabilities 的 wait_bound_seconds 与 window_seconds 与监督实际一致（120 与 90）；坏配置（占位值、缺段）不产生半可用状态。最小样本：四种配置状态各一。证据：离线加浏览器一条。

C12 分页与大小界限（K2）。预期：limit 加一探测正确；空页、满页、末页 next_cursor 语义正确；坏游标 400；长列表翻页无重复无丢失；操作列表无正文；正文仅在单结果通道且 131072 上限正确。最小样本：超一页的操作与活动各一。证据：合成PG 加 HTTP 级。环境：合成PG 必须。

手工推演四条（不是测试，数值为手工样本）。一，新建加取消（同首轮）。二，继续正常（同首轮）。三，响应丢失与刷新恢复：继续提交后响应丢失，台账 unconfirmed；刷新后横幅；核对发现 received 行，只读展示，确认零重发；变体，核对未见行，显式同键重试，若原请求已在途则被有界拒绝或返回既有事实，账至多一次。四，来源替换与范围修订两变体（同首轮）。

资源类型与有界批次建议（基本同首轮，按修正调整）：离线至多 1800 秒；一个专用合成PG资源承载 001—008 与端到端；PG 批至多 3 次；真实 Windows 组合至多 2 批（每批业务 180 秒、清理 120 秒；transport 替身零网络）；浏览器手工在合成库；真实 provider、密钥使用、付费与网络 0；产品库只读探测 storage_not_ready 一项（不做任何用户库写入）；用户库迁移不出现于本实施卡。普通夹具问题卡内修复；具体数值编排出卡冻结。

## 6. 修正后 D 决定与完成

### 6.1 唯一批准包（一项，提交用户）

浏览器活动动作面与服务端配置受控接线。内容：在同一既有本地会话边界下开放活动读取与新建、取消、显式继续三类动作；服务端配置三段与能力三层失败关闭；浏览器首次获得触发活动写动作的能力。理由：G5 验收明确内部受信调用许可不等于浏览器动作许可，这是本切片唯一新的主要信任接口；其余部分均可按既有批准推导。影响：配置缺省时全部动作失败关闭；继续动作在用户自行配置密钥前不可运行，Agent 不使用真实密钥；不新增持久模型（零 DDL）。最小替代：仅只读面（读取与只读恢复先行，新建、取消、继续全部延后），工作区只可观察已有活动。明确排除：用户库任何操作（迁移留待具体对象与备份恢复方案可审阅时单独授权）；真实付费验证（属用户本机行为）；若实施证明必须新增持久结构，停止并携具体字段、迁移与影响并入本包。

### 6.2 无需询问项

端点与字段名、游标与上限、轮询间隔、意图台账结构与文案、配置模板与文件名、共享依赖提取方式、键与 run_tag 生成格式、派生标签写法、错误码文案。均按本合同直接实施。

### 6.3 未验证与限制

本卡与修正轮均为零运行、B 级一致性检查加 D 级推导。未验证：单条 SQL 读取的实际快照自洽（C1、C12 安排）；意图恢复流程的实际行为（C9）；监督链由 HTTP 线程发起的组合（C4）；认证提取的行为等价（C6 以既有测试作证）；配置三层与监督参数文案一致性（C11）。M-1 的表述范围已限定为账本资格判定层；G5 的 E1/E2 已由 092 最终验收关闭，旧夹具原件缺失为保留历史事实；G5 结论边界（不含真实 provider 与产品 HTTP/UI）保持。产品库实际迁移状态本设计刻意不核实也不依赖。

### 6.4 投入

首轮约 80 分钟（声明保留）；修正轮约 25 分钟（估计，含补读、修订与同步线框）；累计约 105 分钟，在 150 分钟上限内；运行与费用 0。

### 6.5 建议 DocuS 变化（由编排采纳后书写）

架构动态文档：G6 增量段更新为「合同修正后待唯一包批准」，登记合成实施边界与 storage_not_ready 默认可见状态。执行动态文档：登记修正轮01结果、唯一批准包待用户决定、下一实施范围（合成端到端）。文档变更记录顺延登记。不改需求基线，不改 001—008。

### 6.6 下一完整实施范围建议

TASK-095/R-089（编号由编排出卡），A+，范围即 B8 九步，专用合成库端到端；真实模型调用、真实密钥使用、用户库 DDL 与付费全部 0；产品库默认 storage_not_ready；前置为 6.1 唯一包获准（或按最小替代仅只读面实施）；验收按 C1—C12；稳定后仅一次必要独立审计限新增信任边界。

---

# 首轮原文（历史保留；凡与上方修正冲突处以上方为准）

# TASK-094 / R-088 G6活动可观测与用户控制入口完整接线合同

## 0. 结论

G6首切片唯一推荐合同为，在既有内部受控能力之上接入「活动工作区只读事实、新建活动、取消活动、显式继续」四项，轮询读取，本地会话边界不变，零新DDL，真实provider与付费动作失败关闭；除一个三项合并批准包（产品库受控迁移、浏览器活动动作边界、付费继续接线与配置门槛）外，其余可直接按既有授权实施。工具动作UI、范围修订UI、首次学习动作不在本切片。

## 1. 身份、读取范围与指纹

实际身份为 Claude 桌面 Code 执行窗口（接收 A+，与 TASK-092 接收环境同一类实际窗口），运行模型 claude-fable-5，如实登记，不冒充档位标签。本卡为只读设计，运行0，未写任何产品/正式DocuS/旧证据，未触数据库、容器、浏览器、网络与模型。

读取43个文件及范围逐项见 [files-read-hashes.json](../evidence/TASK-094/files-read-hashes.json)。其中公共规则 DocuS/AGENTS.MD（SHA-256 e7e6b1a8…d4514）与 task_model/prompts/05_架构生成与维护.md（aade437a…d2235）与锁定快照 [rules-snapshot.json](../evidence/v4-migration-20260930/rules-snapshot.json) 完全一致，零漂移；项目入口 AGENTS.md、DocuS 执行动态文档（1—160行当前裁定）、架构动态文档 v0.65 全文、最终需求 v1.1 全文、本卡、092最终验收、093结果、[G5批准合同摘录](../evidence/TASK-093/approved-contract.md) 均按实际读入登记。未读 TASK-092 结果自评、实现聊天、旧审计推理原件、旧测试正文与历史运行日志细目，不声称读过。最小文本线框见 [wireframe-workspace.txt](../evidence/TASK-094/wireframe-workspace.txt)。

## 2. A 事实地图与用户闭环

### 2.1 现状到目标差距

已有可复用（有代码且有对应有效证据，无需重构）：

- 活动持久模型与四账。001—008迁移（不含新增）已实现：activities 的 status/scope_revision/execution_generation/deadline_at/次数/费用/M·R·S 五列/工具次数与 kind 隔离；activity_operations 的 model/tool 状态与元数据；activity_operation_results 正文表。G3/G5 证据按范围有效。
- 只读恢复与状态语义。repository.read_committed_result、list_committed_results 及 ResultReadStatus 七态已实现并经真实PG验证（G3）；正文抑制与绑定复查规则完整。
- 取消与保守折叠。repository.cancel_activity 幂等，R 全额折入 S、次数/费用不退还；G3/D3 已验证。
- 显式继续与监督链。service.continue_from_result（090 Windows 组合证据）与 execute_tool_action（G5 real-04/05 证据）已走通固定 launcher/SUP/worker/Job 链；时间结算、树零、句柄关闭秩序已验证；09x 证据适用范围内不重跑。
- 本地会话认证。materials/pdf_review 已有的 local_request（Origin 与 Sec-Fetch-Site）加 X-RetroLume-Session 常量时间比对，TrustedHost 与 no-store 中间件、静态同源托管，均已在运行中的应用上稳定工作。

需新增（本合同对象，均不新增DDL）：

- 活动/操作读取的 HTTP 面与脱敏投影（当前应用无任何活动路由）。
- 活动列表与操作列表的有界只读SQL（现无 list_activities；list_committed_results 只列有正文行；list_unresolved_operations 明确不得直接暴露给 HTTP）。
- 新建活动、取消、显式继续三个浏览器动作入口及其实例身份派生。
- 本地产品配置（额度与provider描述、密钥经环境注入），缺配置失败关闭。
- 前端活动工作区（导航、列表、详情、动作、轮询、空/加载/错误/未知文案）。

仅历史实验或不在本卡：

- 13元旧实验预算、旧合成容器/库/角色、旧失败记录：保留原状，不复活、不重测。
- 首次学习动作（意图/计划/出题/追问的提示词与证据装配）：属学习/面试业务卡；本卡不做新检索、出题与记忆系统。
- 工具动作UI、范围修订（配置）UI、未知操作的一键收敛UI、SSE/Redis：不在本卡；SSE 在架构中为显示加速建议，当前零实现。

### 2.2 用户完整旅程（目标态，含当前真实缺口）

进入工作区（导航「学习活动」点亮）→ 新建活动（选择当前有效资料范围；表单只读展示服务端配置的有限额度；创建本身零模型调用、零费用）→ 活动就绪（空闲态；首次学习动作入口属后续业务卡，界面以「等待学习入口接入」如实说明，不设假按钮）→ 产生成果后（经后续业务卡或既有内部链）工作区显示每项操作状态与正文 → 显式继续（仅对「已提交且正文可回查」的模型成果出现按钮；提交前再次显示剩余请求与费用预留；运行中可刷新查看）→ 运行中（状态徽标「运行中」、预留窗口说明、最后更新时间；不提供伪进度条）→ 失败（白名单错误码对应可理解文案，如超时/远方未知/远端拒绝/提交未确认）→ 取消（确认文案说明：不再开始新动作、在跑窗口按自身期限停止、远端不可撤回、次数费用不退还；取消幂等）→ 刷新或断线（只重读；恢复同一持久事实；服务重启时按账本事实如实显示，陈旧 running 以取消为可靠自愈手段——取消把 R 保守折入 S 且无会话前提；若本地配置显式开启单机单会话恢复部署声明且前提满足，下一次显式动作也可按已批准 D3 规则接续折叠，否则动作对陈旧窗口明确失败关闭，绝不自动重发）→ 显式发起新动作（每次都是新操作键、重新显示剩余额度、重新权威准入）。

### 2.3 只读恢复与重新执行的区分，以及未批准前置

只读恢复指对既有持久事实的读取（列表、详情、操作、正文回查），不产生任何发送、预留或监督；重新执行只发生在用户显式动作且服务端权威准入通过时，两者在界面与接口上严格分开（GET 永无副作用）。

真实执行前置中尚未批准或配置的有：对本机产品库应用 002/004—008 的迁移（至今仅授权合成库）；浏览器活动动作边界（内部受信接口许可不得直接当浏览器动作许可，G5验收原文）；真实provider密钥与条款核对、付费调用授权与额度值；活动额度配置本身。以上缺一即对应能力失败关闭，界面不显示不存在的按钮承诺。

## 3. B 唯一推荐实施合同

### B1 事实权威

每个可见字段的唯一来源如下（同一事实不得有第二个计算位置；HTTP 层只做白名单投影，不重算状态）。

活动列表行。摘要标签为派生值，不持久化，由 activity_scope_sources 关联 material_sources.title 生成（「由「A」「B」等 N 份资料组成」，N 与首两个标题实际读取；范围为空时显示「无来源范围」）。状态取自 activities.status（pending 显示「空闲」、running「运行中」、cancelled「已取消」）。剩余请求取自 max_requests 减 requests_reserved（预扣口径）。费用取自 cost_reserved_microunits 与 max_cost_microunits。创建时间 created_at，最近更新 updated_at，期限 deadline_at。

活动详情。范围取自 activity_scope_sources 与 material_sources（标题、current_version、revision），逐项派生「当前有效／已失效」，判定与 claim/admit 相同的口径：该来源当前版本与修订快照一致才有效。范围修订 scope_revision。预算四账：请求 max_requests/requests_reserved；费用 max_cost_microunits/cost_reserved_microunits/reserve_cost_microunits；时间 max_running_seconds/running_settled_seconds/running_reserved_seconds 及 last_settled_generation/last_settled_seconds；工具 max_tool_calls/tools_reserved（NULL 显示「未配置」，0 显示「明确禁用」，两者都不可执行工具）。可用额度的派生公式：剩余请求为上限减已预扣；剩余费用同理；可用时间为 M 减 S 减 R，S 为各窗口向上取整秒的累计。取消时间 cancelled_at。execution_generation 与 dispatch_closed 为内部 CAS 事实，用于按钮可用性推导（活动已取消或已到期时「继续」不可用；存在活跃执行窗口时动作按 B4 被有界拒绝并提示），不作为用户可见字段展示。

操作列表与详情。行主事实取自 activity_operations（kind、state、disposition、error_code、reserved_at、dispatch_started_at、recorded_at、prompt_tokens、completion_tokens、finish_reason、returned_model），正文事实取自 activity_operation_results（payload_format、payload、payload_sha256、committed_at）。读取状态必须与 read_committed_result 同源，即同一 SQL 投影与同一绑定复查规则（结果行与操作/活动/admission/G/scope 一致、scope 当前、来源当前、活动取消分支、payload 逐字节与 hash 复查、工具结果语义复查），实施卡不得另写第二套状态判定。terminal_without_payload 同时覆盖 not_sent、received 无正文与确定失败行。

不确定性必须原样呈现，不得被摘要或诊断覆盖。R 是运行中的预留而非实际耗时，结束按实际耗时向上取整结算；五列账本只保留最近一次结算对，不提供逐窗口历史，界面不得展示结算历史；requests_reserved 与 cost_reserved_microunits 是预扣，含提交丢响应的保守耗用，不是「成功调用」计数，取消与失败不退还；unknown 不等于未发出，也不等于远端已停止；取消不是停止证明，也不撤回远端；settle 已确认不等于业务成功；业务已提交不等于树已停；费用账为本地保守预扣微单位，语义由本地配置声明，不代表真实计费；系统时钟回拨时时间上限不具硬性保证（M-1 未闭合，沿 058/060 事实，不宣称硬耗时上限）；摘要标签是派生标签而非持久字段。

### B2 读取与历史

唯一推荐为纯轮询的有界读取，不引入SSE。API-003 的「只读、有游标、过期游标回快照；断线不取消不重做业务」语义由本合同的游标读取满足；SSE 仅是未来显示加速，不影响本合同的正确性，实施卡不得以「将来上SSE」为由改变读取形状。本项目没有完整事件存储，本设计不虚构事件流与完整历史；游标只是不可删除行的分页锚（活动与操作在本切片均不可删除），非法或无法解码的锚返回 400 invalid_cursor，前端回第一页（等价于回快照），不做事件回放。

新增只读端点（全部走既有本地会话边界，全部无副作用，全部 no-store）：

- GET /api/activities/capabilities。返回 storage_ready（活动表可用性探测）、quota_configured、provider_configured 及只读的额度预览与输入上限（供前端决定是否显示按钮与展示文案）。该路由须先于 /api/activities/{activity_id} 声明，避免字面量被 UUID 校验拦截。
- GET /api/activities?limit=&cursor=。活动列表，按 created_at 与 id 双键倒序，游标为服务端编码的（created_at,id）对；limit 默认20，最大50。
- GET /api/activities/{activity_id}。单事务返回活动事实、四账、范围与逐项有效性、到期与取消事实。不存在返回 404。
- GET /api/activities/{activity_id}/operations?limit=&cursor=。按 operation_id 稳定排序（主键索引天然有序），游标即上一页最后 operation_id；limit 默认20，最大100；行投影与读取状态同源（B1）。不得复用 list_unresolved_operations（其含可构造凭据的 admission_id/executor 等信息，既有注释明确不得暴露给 HTTP）。
- GET /api/activities/{activity_id}/operations/{operation_id}。单操作事实与读取状态；正文仅在状态为 committed_current 或 committed_history_cancelled 且绑定与来源复查通过时返回；正文永以纯文本字段返回，不回传规范封套以外内容。

可辨响应：403 会话失效或来源不合法（复用现有判定）；400 非法 UUID、非法游标或越界长度；404 活动或操作不存在（与 no_operation 语义合并为「无此操作」，不伪造 admission/G）；503 数据库不可用；200 携带 read_status 枚举表达业务读取状态。分页整页编码设 256KiB 硬保护，超限直接失败而非静默截断。

一致性与轮询。每页读取在单事务内完成，页内字段互相一致；跨请求不承诺一致，界面每个面板独立显示「最后更新」为客户端接收时间，且任何动作完成后立刻重读相关面板，不把两次不同时刻的响应合并成单一承诺视图。自动刷新只在活动为运行中或存在在途动作时进行，固定间隔约3秒，只发 GET，可中止，不并发重复；活动静止后停止自动刷新，保留手动刷新。断线重连只重读。

### B3 动作与信任

首切片动作集与未开放项逐项如下。

纳入首切片：新建活动（本地写，零费用）；取消活动（本地 CAS，幂等）；显式继续（一次模型调用，经既有监督链；真实付费需配置且失败关闭）。读取不属于动作。

未开放并如实标注：单次工具动作（finite_calculate 是内部校验能力，不作为用户产品按钮；工具结果若因内部链存在，仅按 B1 只读展示，界面无执行入口）；范围修订（配置类动作，其后果为成果失效语义，先让只读失效展示稳定后再开放）；额度修改（无运行时扩大额度接口，沿 G5 边界）；首次学习动作（业务卡）；未知操作一键收敛（内部 recover_unknown 不暴露；用户面对陈旧 running 的手段是取消或下一次显式动作的保守折叠）。

信任边界。新动作面与既有 materials/pdf_review 完全同一边界：仅 loopback 监听，TrustedHost 限 127.0.0.1/localhost，local_request 拒绝 cross-site 与未知 Origin，动作端点要求 X-RetroLume-Session 常量时间比对（自定义头也构成对简单 CSRF 的阻断，因为跨站表单无法带自定义头，跨站 fetch 会先触发预检而应用无 CORS 许可）。实施卡把 local_request 与会话比对提取为共享依赖（行为不变），三组路由共用，避免出现第二套认证实现；若实施者选择直接 import materials.api 的 repository()，须在卡内记录其对活动端点 503 文案不贴切并接受。localhost 本身不是授权，此边界继续只承诺抵御跨站浏览器攻击，不承诺抵御同账户恶意本地程序（沿架构既有声明）。不悄悄新增公网认证平台、不新开端口、不引入反向代理。

服务端掌握上下文，客户端不能提供任何授权物。请求体只接受业务键（新建接受 activity_id 与 source_ids；继续接受 parent_operation_id、new_operation_id、followup）；executor_id 由服务端固定常量派生（建议 "local-ui"，登记为持久执行者身份，未来不改名）；run_tag 由服务端每动作生成（受限 ASCII、≤64）；execution_generation、scope_revision、额度值、deadline、provider、模型名、DSN、密钥与 argv 一律不接受自客户端；所有权威判定在既有仓储锁内（来源排序锁、活动锁、操作键锁）完成。

动作语义如实显示。取消为数据库事实，只使旧资格失效并把 R 保守折入 S；正在运行的本机树由既有 Job 期限停止，取消不即时杀树、不撤回远端（G5 语义保留）；继续动作只做一次受控调用，失败关闭不伪成功；查询无副作用。

### B4 幂等与恢复

- 双击新建。前端在进入新建表单时生成一次活动 UUID 并保存于该意图的表单状态；重复提交同键，服务端 create_activity 以主键拒绝「活动 ID 已存在」，HTTP 映射为 409 activity_exists，前端把它解释为「该活动已创建」并直接进入详情。页面刷新后的再次创建是新意图、新 UUID，语义正确。不依赖布尔提交标记。
- 双击继续。new_operation_id 在确认发出时生成一次并绑定该意图；同键第二个请求走服务端既有的「已存在只核事实」分支，返回现有状态，零第二次调用。并发同键时线程本地互斥（local_owner_busy）或租约冲突先于任何执行拒绝第二个请求，至多一个监督尝试。诚实说明：模型动作的 followup 与父键不持久，服务端无法比对「同键异文」；因此界面必须把表单与该意图键绑定，换内容必须换键，接口不承诺不存在的异文检测（工具参数有摘要绑定，模型没有）。
- 刷新、断线、提交响应丢失。动作的监督在其有界线程内独立完成，客户端断开不取消它也不触发重发；客户端在响应丢失后展示「结果未确认，正在按持久事实核对」，以轮询查找操作键：找到即按事实展示；在界定的核对期后仍无操作行且无运行窗口，提示可显式再次发起（新键）。绝不自动重发同一键。
- 超时与预算耗尽。远端超时映射 unknown（可能已执行，不重发）；时间预算耗尽由 claim 返回 None 进入 budget_exhausted，不留操作行；次数或费用达限由锁内 admit 拒绝，同样不留操作行——界面不得把「无操作行」显示为「已尝试失败」的含混状态，需区分「被拒绝未开始」（无行）与「尝试过」（有行）。拒绝前可能已消耗一个时间窗口，按实际耗时如实结算。
- 来源替换。创建时快照与当前版本不一致即失败（来源快照已撤销或被替换），提示刷新后重选；活动存续中来源被替换，旧成果按 invalidated_source 只读展示且正文抑制，继续被拒。
- 范围修订、旧G晚到、同键冲突。修订只改 scope_revision 与快照，使旧结果按 invalidated_scope_changed 失效；旧代次晚到结果没有任何新资格（既有仓储保证）；同键冲突按 B1 状态展示。旧结果有效性一律由权威仓储判定，前端不做任何本地推断的资格结论。
- 身份持久性。活动 UUID、操作键一经持久即不可换身份；服务重启后依据持久行判断一切（存在即事实），不存在任何依赖浏览器临时状态的幂等，也不在内存中保留「已处理」集合。

### B5 配置与预算

额度来源为新增的本地私有配置（建议 config/activity.local.json，含注释模板 config/activity.example.json 提交入库，真实文件被忽略）。内容包含 provider 段（provider 枚举、base_url 允许列表内、model、thinking、密钥经环境变量注入，密钥不写入配置文件正文也不进入任何响应）与活动默认段（deadline_hours、max_requests、max_cost_microunits、reserve_cost_microunits、max_request_bytes、max_output_tokens、max_running_seconds、allowed_models、allowed_tools、max_tool_calls）。服务端启动时用既有 ModelServiceConfig 与 ActivitySpec 校验器逐项校验；任何缺项或不合法即视为未配置，能力整体失败关闭并在 capabilities 中如实显示缺项位置指针。示例模板不得含可直接使用的数值（占位值必须校验失败），测试值（如 092/090 夹具中的 M=100、max_requests=5 等）不迁移为产品默认，项目不自带静默默认值。

展示与确认。新建表单只读展示上述额度预览（来自服务端，不可在界面改动）；用户确认创建即接受该额度包。修改者只有用户本人编辑本地配置文件；本切片无任何 HTTP 额度修改接口。重试说明：SDK 隐藏重试已关闭（沿既有架构），显式重试就是新的操作键并消耗一次请求；「重试上限」由 max_requests 截断，不另设计数器。

失败关闭不是免费默认。G5 的 max_tool_calls=NULL 语义保持（未配置即不可能执行工具），不得因 UI 需要改为自动免费额度；费用授权不扩大，本设计不启用任何真实付费调用，真实provider验证若未来需要，另提精确的最小调用与费用决定（当前零执行）；真实provider启用门槛为用户配置密钥与额度值并主动点击继续动作。

### B6 长任务与隔离

HTTP 生命周期不绕过监督。继续动作由请求处理器经由既有 service.continue_from_result 进入 asyncio.to_thread 的监督线程与固定 launcher/SUP/worker/Job 链，屏蔽调用方取消的既有 shield 语义保持不变；最坏等待约为窗口加管理余量（默认约120秒），本地单用户可接受。请求断开不取消监督、不重放、不伪称取消；结果以持久事实为准，客户端用轮询恢复。

不新增后台服务。首切片不引入持续 worker、队列或新持久结构；监督的所有权、期限与收尾沿用 D3/G5/G4 已验证主体。并发动作不排队：同一活动第二个动作在本地互斥或租约处被有界拒绝（local_owner_busy 或租约冲突），UI 显示「已有动作进行中」。

服务进程重启。若监督途中应用进程退出，持久事实是权威：窗口仍有 R 与租约，操作可能停在 reserved/dispatched。界面按事实显示「运行状态未知（服务曾中断）」。陈旧 running 的恢复有两条既有路径，如实区分：用户取消在任何前提欠缺时都可使用（R 保守折入 S，无会话门槛）；单机单交互会话恢复走已批准 D3 合同，但需本地配置显式声明 deployment 前提（SessionConfig.single_host_single_session_recovery，建议默认关闭，由用户在本地配置中显式开启并理解代价），未声明时下一次动作对陈旧窗口失败关闭（JobUnknown），不折叠、不重发。是否需要自动对账留给后续卡，不在本切片新增常驻组件。

### B7 展示与隐私

状态与失败文案采用固定中文短句映射（正面清单见线框文件；错误码映射为有限白名单，未知码显示「内部错误（未分类）」）。界面不显示 SQL、runner、堆栈、异常 repr、hash、admission_id、executor_id、execution_generation、remote_request_id、host 路径与 argv。响应投影白名单为 operation_id、kind、state、disposition、error_code、时间戳、token 数、finish_reason、returned_model、committed_at 与正文可用性；正文仅在 B1 条件满足时以纯文本（或格式化文本的 json 字符串）展示，绝不注入执行，不扩大 HTML 权限；PDF 先人工核对的门保持（新建活动只能引用当前有效版本，待核对 PDF 在核对完成前没有当前可用版本，天然不可选）。金额显示为微单位整数及其上限（不做虚构汇率换算）；时间显示秒。

### B8 修改与兼容、实施顺序

拟改文件与模块（下一完整实现卡范围）。

- backend/app/activities/repository.py 仅新增只读方法与投影辅助（list_activities、read_activity_facts、list_operations；读取状态复用既有 _read_status/_snapshot_from_row 与绑定 SQL），既有方法签名与语义零改动。
- backend/app/activities/service.py 新增薄读取包装与 cancel 包装（复用 read_result/read_scope 与 ledger.cancel_activity），continue_from_result 签名不变。
- 新增 backend/app/activities/api.py 路由（复用共享会话依赖）与配置加载模块（建议 backend/app/service_config.py，产出 ModelServiceConfig 与活动默认段；加载失败只影响活动能力）。
- backend/app/main.py 增补路由挂载与 app.state 注入；create_app 签名保持兼容（新参数带默认值），test_config 既有行为保持。
- frontend/src/main.tsx 增加导航选择与工作区挂载；新增 frontend/src/activities/ActivityWorkspace.tsx 与样式，复用现有 api() 请求模式与错误文案纪律；资料页面结构不动。
- backend/tests 新增离线与PG用例（沿用既有专用 DSN 环境变量隔离模式，不回退用户库）。
- 明确不改：001—008 迁移（无新DDL）、worker 全部文件、capabilities 契约与 gateway、one_call/one_tool 协议、session/launcher、materials/pdf_review 行为、需求基线。无任何新增持久模型与迁移；活动数据模型完全复用 001—008。

拟新增接口签名（实施卡在此形状内细化参数名与类型，不改变语义）：

```text
repository: list_activities(limit, cursor) -> (rows, next_cursor)
repository: read_activity_facts(activity_id) -> ActivityFacts | None
repository: list_operations(activity_id, limit, after_operation_id) -> (rows, next_cursor)
service:    list_activities / read_activity / list_operations / cancel_activity_view 薄包装
http:       GET  /api/activities/capabilities
            GET  /api/activities
            GET  /api/activities/{activity_id}
            GET  /api/activities/{activity_id}/operations
            GET  /api/activities/{activity_id}/operations/{operation_id}
            POST /api/activities                       {activity_id, source_ids}
            POST /api/activities/{activity_id}/cancel
            POST /api/activities/{activity_id}/continuations
                 {parent_operation_id, new_operation_id, followup}
```

所有新读方法只读且无锁提升；取消与继续复用既有方法，不新增仓储写路径。

失败映射（HTTP 层）：400 invalid_input（UUID/游标/长度）；403 会话或来源；404 not_found；409 语义拒绝（activity_exists、provider_not_configured、activity_cancelled、activity_expired、source_invalid、source_replaced、result_not_committable、result_kind_read_only、budget_exhausted、time_budget_exhausted、busy、scope_conflict）；503 unavailable；200 读取成功或一次有界动作已得出结论（含 supervision_unknown 等如实状态）。响应不得包含异常文本。

写权边界：浏览器只经上述三动作写；仓储对活动的写仍只在既有锁内方法；工具与模型准入资格不因新 HTTP 面扩大；运行环境不因新面新增任何网络暴露。

实施顺序（单卡内连续完成实现、相关测试、范围内普通修复与资源收尾）：一，配置加载与 capabilities 失败关闭；二，仓储只读三方法与投影一致性测试；三，HTTP 只读面与脱敏、可辨响应；四，新建动作与幂等；五，取消动作；六，继续动作（服务端身份派生、缺配置失败关闭、与监督线程边界）；七，前端工作区与文案；八，合成PG与前端组合验证、资源收尾与文档增量。稳定后仅对实际新增信任边界（浏览器动作面）与影响做必要独立审计，不重开 G5/D3。

## 4. C 定向验收矩阵

以下为下一完整实现卡的检查设计，不是已运行结果；运行时冻结源码、样本、资源与上限，逐项留原始证据。

C1 读取与投影一致性。预期：列表/详情/操作/成果的四类读取与 read_committed_result 对同一行给出同一状态与同一正文有无；白名单外字段不出现；NO_OPERATION 不伪造任何字段。最小样本：一个活动含 model/tool 两种操作，覆盖 committed_current、invalidated_source、unresolved、terminal_without_payload。证据：离线断言加合成PG逐行对照加一条浏览器目视。环境：离线与合成PG（必须），浏览器一条（因展示层是新行为）。

C2 新建与幂等。预期：双击、响应丢失后同键重试都不产生第二个活动；来源竞态（预读后替换）明确失败；缺配置失败关闭且无任何写；参数非法拒绝。最小样本：同键两次 POST、两连接竞态一次、缺配置一次。证据：HTTP 级原始请求响应加PG行数断言。环境：合成PG 加 HTTP 层；浏览器手工一条。

C3 取消与恢复真实语义。预期：重复取消幂等且账不变；取消后旧资格失效、继续被拒并给可读原因；在跑窗口不因取消即时停止（沿用 Job 期限停止的既有证据，不重造反例）；次数/费用不退还；刷新后同一事实。最小样本：pending 取消、running 取消、已完成活动取消三种。证据：合成PG；Windows 停止主体复用 D3/G5 已验证据并说明适用性。

C4 显式继续正常链。预期：缺配置失败关闭（新证据）；配置存在（合成transport替身）时经真实 launcher/SUP/worker 链完成一次调用，落库 received 加正文，时间账按实际结算，请求与费用预扣各加一，UI 显示结果。最小样本：一条 Windows 组合，transport 替身零真实网络、零费用。证据：真实 Windows 组合加HTTP 级加浏览器目视。环境：真实 Windows（因监督链）。复用：链主体 090/G5 证据适用，不重跑全套；外2/内3 协议回归点一项。

C5 动作双击与同键竞争。预期：同键并发至多一次监督；第二者 local_owner_busy 或租约拒绝；无第二次调用、无第二次预扣。最小样本：两并发同键请求加事件屏障（不用 sleep 猜顺序）。证据：合成PG 加线程级并发记录。

C6 权限反例。预期：无会话头 403；跨站（Sec-Fetch-Site 或陌生 Origin）403；坏 UUID 400；跨站预检被浏览器阻断（手工一条）；localhost 不产生额外放行。最小样本：四类反例各一。证据：HTTP 级加浏览器手工。

C7 敏感信息不暴露。预期：响应与界面任何位置无 DSN、密钥、参数正文、hash、admission_id、executor 与路径；错误只现白名单码。最小样本：错误路径注入一次（如故意缺配置、非法输入）后的全文检索。证据：离线扫描加浏览器目视。

C8 来源/范围变化与旧结果失效。预期：替换资料后旧成果 invalidated_source 且正文抑制；范围修订后 invalidated_scope_changed；继续被拒且文案可懂；创建时竞态明确失败。最小样本：替换一条、修订一条。证据：合成PG。环境：合成PG（必须，因涉及真事务与CAS）。

C9 断线、刷新与重启语义。预期：自动轮询只发 GET；手动断网期间无重发；恢复后同事实；服务重启后的陈旧 running 显示与取消自愈；响应丢失核对路径不自动重发。最小样本：轮询抓取请求日志、断网一次、重启一次。证据：浏览器手工加服务日志；合成PG 支撑。

C10 旧资料页面不回归。预期：资料上传/核对/替换/摘录流程不变，导航新增不影响原视图。最小样本：一条已保存资料打开加一条上传。证据：既有 materials/pdf 测试全部沿用（不重跑历史PG细目）加前端构建加浏览器一条。复用：既有证据适用，不重测。

手工推演四条（明确不是测试，仅守恒演示；数值为手工样本，非产品默认）。轨迹一，新建加取消，同步活动创建后无操作行、四账为初始值，取消只改状态与时间折叠。轨迹二，继续正常，父为已提交 model 成果，窗口 claim 预留 W、admit 后请求与费用各加一、received 正文提交、settle 按实际秒、读为 committed_current；同键复查零变化。轨迹三，提交丢响应与服务中断，操作停在 dispatched 无正文，恢复按 unknown 只读，不自动重发；下次动作 claim 只折叠一次旧 R。轨迹四，来源替换与范围修订两个变体，旧成果状态迁移与正文抑制一致，账不变。

下一完整实现卡的资源类型与有界批次建议：离线至多1800秒（含前端构建）；一个专用合成PG资源（002—008 全量，或按卡精确复用已停止的既有合成容器并写明身份），PG 批至多3次；真实 Windows 组合至多2批（每批业务180秒、清理120秒；transport 替身零网络）；浏览器手工组合在合成库进行；真实provider、付费与网络0；用户库迁移仅在批准包获准后作为卡内受控步骤（先只读核实实际迁移状态，再备份，再按序补差，每迁移单事务且失败回滚）。普通夹具问题卡内修复，不再为单断言拆卡；具体数值由编排出卡时冻结。

## 5. D 决定与完成

### 5.1 唯一合并批准包（三项，一起提交用户）

一，对本机产品库执行受控迁移授权。需要用户批准在备份与只读状态核对后，把 002/003/004—008 按实际缺失情况补差应用到本机应用库（此前仅授权合成库；这是用户库首次 DDL）。理由：活动工作区没有产品库无法真实使用。影响：本机数据 DDL，每迁移单事务，004/005 的空表门保持，失败回滚，备份先行。最小替代：不迁移，工作区对未迁移库显示「活动存储尚未就绪」，仅资料功能可用（工作区无实际对象）。

二，浏览器活动动作边界授权。批准在同一既有本地会话边界（loopback、TrustedHost、Origin/Sec-Fetch-Site、会话令牌、自定义头）下开放读取、新建、取消、显式继续四类 HTTP 能力；不加公网认证、不加端口、不改 loopback。理由：用户持续开发授权与 API-002/003 架构已规划此类动作，但「内部受信调用许可不等于浏览器动作许可」（G5验收原文），需一次明确采用。影响：浏览器首次能触发活动写动作；未配置环境全部失败关闭。最小替代：仅只读面，动作全部延后（产品库活动表尚未迁移，工作区无实际对象，效果为空壳；实际状态以实施卡第一步只读核实为准）。

三，付费继续的接线与启用门槛。批准显式继续完成接线但默认失败关闭；真实付费调用仅当用户在本地配置密钥与额度值（示例模板不含可用数值）并主动点击时发生；初始额度与费用数值不在本设计编造，启用时由用户确认，配置即上限。理由：NFR-003 要求启动前可见有限上限，13节规定未配置即拒绝付费动作；不扩大原费用授权。影响：首个经产品UI的真实付费路径在用户配置后可用。最小替代：继续动作延后到学习入口卡，本切片零付费路径（工作区仅读、新建、取消）。

### 5.2 无需询问、按既有授权直接实施

端点 URL 与字段名、游标与上限数值、轮询间隔、按钮布局、空/加载/错误文案、配置文件名与模板、共享会话依赖的提取方式、操作键与 run_tag 的生成格式、列表派生标签的写法。这些均由本合同的边界直接推导，不再形成用户问题或偏好问卷。

### 5.3 未验证与限制

本卡零运行，全部结论为 B 级（源码与文档一致性）加 D 级推导；没有任何新动态证据。未验证：监督链由 HTTP 线程发起的真实组合（安排为 C4）；浏览器动作面的实际安全表现（C6）；产品库迁移的实际状态（实施卡第一步只读核实）；真实provider兼容与付费路径（启用时另行最小决定）；M-1 时钟边界（保持未闭合）。既有 092/093 的两项低风险证据缺口（2048边界、旧夹具原件）不在本卡范围，按编排裁定处理。G5 的结论边界（不含真实 provider、产品 HTTP/UI）保持。

### 5.4 投入

本卡主动投入约80分钟（自首次读取卡至保存，估计值；预算90分钟未耗尽），未使用任何运行额度；跨窗不作投入清零处理。

### 5.5 建议 DocuS 变化（由编排采纳后书写）

架构动态文档增 G6 增量段（合同要点：只读面加三动作、无DDL、轮询、配置失败关闭；API-002/003 注记「合同就绪待实施」；FILE-001/002 登记前端工作区与 activities/api.py；DATA-009 登记本地私有配置行）。执行动态文档登记 TASK-094 结果、批准包待用户决定、下一 TASK-095/R-089 实施范围与资源建议。文档变更记录从 CHG-0722 起登记。不修改需求基线，不修改 001—008。

### 5.6 下一完整实施范围建议

TASK-095/R-089（编号与资源由编排出卡冻结；本卡不占号），A+ 档，范围即 B8 八步，含实现、相关测试、范围内普通修复与资源收尾；前置为 5.1 三项获准（其一为可选替代路径）；稳定后仅按实际新增信任边界做一次必要独立审计。验收按 C1—C10 执行，复用范围按各条注明。
