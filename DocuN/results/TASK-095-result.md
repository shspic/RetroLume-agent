# TASK-095 / R-089 G6活动工作区与受控动作完整接线 结果

## 0a. 续作02（2026-10-01 晚）：唯一合并入口——PG 分页单方法 PASS；浏览器 9 场景全执行、checks 全 true，仅夹具观察窗定义失败

真实身份：续作01 同一实际修复窗口延续（WorkBuddy，GLM-5.3-Flash），非 096 审计窗口、非旧 Claude 窗口，如实登记。合同为 DocuN/tasks/TASK-095.md 置顶续作02 节；复用依据为 DocuN/evidence/TASK-095/orchestration-reuse-02/reuse-binding.json；本轮证据在 DocuN/evidence/TASK-095/continuation-02/。

### 0a.1 两段实际结果

**PG 段：PASS。** 唯一运行 `ReadProjectionTests.test_activity_list_pagination_cursor`（修正后冻结字节 ed32fe37…），11.713 秒，returncode 0、OK、无 skip。身份核验全过：owner/role 旗标/成员资格/会话数（postgres 库经管理身份）+ 7 表 schema 核对**连接 task095 库本身**（续作01 夹具错误不再重演）；口令 stdin 随机重置，DSN 仅经子进程环境。原始输出 final-run/unittest-pagination.out.txt；as-run 字节绑定 hashes-import/final（产品六项与 dist 四产物全一致）。断言覆盖：本例 3 活动全部被翻页遍历、首页只含本例最新行、无重复、全局倒序、非法游标参数 ValueError；库内 095 时代残留合成行按卡未删。

**浏览器段：FAIL（唯一 failure 为夹具观察窗定义错误；产品行为断言全部成立）。** 实跑脚本 as-run 字节 5e541e22…（本轮三处卡面点名修正后：summary.ok 收紧为 checks 全 true 且无 failures/blocked/console 错误、s4 在途数改观察窗配对时间线计算 windowPeak、route 回调异常显式记失败并兜底响应）。62.727 秒，**steps s0—s8 全部执行**（挂载路由覆盖/普通刷新只 GET 且不自动恢复选择/unconfirmed 意图刷新只 GET/submitted 意图显式 POST 恰一次且动作后重读触发/慢响应 tick 跳过与列表组内不重叠/隐藏暂停与恢复只 GET/活动切换与展开迟到双向隔离/失效分支与展开正文/卸载清理），**checks 全部为 true、blocked 空、console/page errors 空**。唯一 failure：`s3 after-action slice contains POST`——根因是 beforeS3b 记录于显式点击**前**，after-action 切片必然包含显式 POST 请求自身；全局计数 postTotal=1 已由同场景 `s3_explicit_post_exactly_one=true` 证明显式动作恰一次、无任何自动 POST。次要点：summary.post_total 报告字段未同步全局计数（runner 读到 0，实际 1）。

按卡"一次运行失败即收尾交回"：未重跑。两处确定性夹具修正（s3 窗口断言改为"窗口内 POST 恰 1 个（显式动作本身）且其余全 GET"+post_total 同步）已完成并 node --check 通过，**实机 not_run**；pre 副本、diff、as-run/post 哈希均在 continuation-02/ 留证。

### 0a.2 26 项复用依据与历史误表述纠正

- 26 项已通过方法直接继承，不重跑：编排核证"当前 reads 仅分页区段还原为 pre 原文后整份 SHA256 恰等于批时字节 c1c40c35…，批时全部 backend/app 指纹与当前一致"（reuse-binding.json，8 个 app 文件 as-run=当前逐项 match）。
- **纠正**：续作01 第 0.2 节"PG 批实跑的是测试文件修正前字节（5a7c8941…）"表述不成立——5a7c8941 是续作01 修改前基线，批时实际 import 为 c1c40c35…（含续作01 对 CountingLedger/单SQL断言/损坏正文反例的修改、不含最后的分页断言适配）。原历史正文不改，以本节与 work-decision 置顶裁定为准。
- 26 项构成含离线 API 用例与 PG 用例，不称"26 个全部真实 PG"；其余 25 个 PG/离线方法本批未执行，证据按 as-run 字节继承。

### 0a.3 产品未改声明与资源账

- 产品源码全部冻结：六项（materials/api.py、ActivityWorkspace.tsx、repository.py、两个测试文件、浏览器脚本）启动前逐项与续作01 post-hashes 核对一致；本轮仅改浏览器测试脚本（允许的夹具修正，pre/diff/post 齐全）；分页测试保持冻结 ed32fe37…。无依赖/DDL/正式文档/旧证据改动，无 Git 写入。
- 预算：新增入口 1/1（累计 10/10）、容器 start 1/1（累计 9/9）、浏览器启动 1/1（续作01 另计 1）；业务合计 74.440/300 秒（PG 11.713 + 浏览器 62.727）；离线准备远低于 60 秒；主动投入约 25 分钟/60 分钟上限。旧账（095 claim10/保守14、累计业务 205.237 秒口径）不变，超限不追认。
- 收尾：容器批末 Running=false/Pid=0（final-run 记录）；端口 18095 释放核过；dsn 未落盘、口令未入 argv/日志/报告；资源无异常，故浏览器段在 PG PASS 后按计划执行完毕。

### 0a.4 状态与下一步

- G2 分页单例：**已闭合**（真实 PG 实测通过）。至此续作01 三处产品修正的全部后端定向证据齐备。
- G1 浏览器 s0—s8：**待一个最小复验批**——当前脚本已含全部修正，接手批仅浏览器单段（零 PG、约 60 秒）即可取数；或由编排裁定以"9 场景全执行+checks 全 true+唯一失败为夹具窗口定义"的现状按增量确认口径处理。
- 原 096 独立窗口随后仅增量确认：D1/D2/O1 三处产品修正 + 本轮新证据；未变区域继承。本卡不自行做独立验收。
- 不签 G6 最终通过、STEP006/008、M-1 或整个项目通过。

## 0. 续作01（2026-10-01）：三处合同修正与最终补证——代码修正完成，G1/G2 实机收口因预算到限部分未运行

真实身份：本续作窗口为 WorkBuddy（GLM-5.3-Flash），非 092/094/095 的 Claude 桌面 Code 窗口，亦非 096 审计窗口，如实登记。合同为 DocuN/tasks/TASK-095.md 置顶续作01 节；裁定输入为 TASK-096-work-decision.md（D1/D2/O1）与 TASK-096-result.md（D1/D2/O1/G1/G2）。

### 0.1 三处产品修正（全部完成，离线验证通过）

| 修正 | 文件 | pre → post SHA-256 | 内容 |
| --- | --- | --- | --- |
| D1 | backend/app/materials/api.py | 09b2be09…a3449 → e463ed5d…3d79 | repository() 恢复 `local_session(request)` 默认固定允许来源/拒绝行为；PDF 复用链（pdf_review/api.py 经同函数）同步恢复；活动路由 allow_own_origin 保留。未改固定 Origin、TrustedHost、Sec-Fetch、常量时间 token 语义，未扩白名单 |
| D2 | frontend/src/activities/ActivityWorkspace.tsx | a3ba46d6…ff392 → b6a339d0…b5 | 轮询在途标志防重入（finally 释放，单次失败不卡死）；document.hidden 暂停/恢复（恢复只 GET）；卸载清理（interval+visibilitychange 监听）；detail/operations/openOperation/loadMore/list 全部加请求序号与选择上下文保护，切换/卸载/迟到读取不覆盖新选择。3 秒节奏与"显式动作后读取"不变，无缓存/队列/自动重试 |
| O1 | backend/app/activities/repository.py | 295e3e95…ee0 → ac55739c…70c | 新增 `_OPERATIONS_LIST_SELECT` 列表专用投影：数据库不返回正文列，改投 payload_eligible 布尔（单语句内绑定/scope/来源判定的正文候选资格）；`list_operations` 改用之（单 SQL 不变），行内绑定损坏仍失败关闭，正文损坏不再拖垮整页元数据列表；`read_operation` 仍走 `_OPERATIONS_SELECT` 完整校验正文/hash/工具语义。未改原 _RESULT_READ_SQL、核心写路径与持久模型；顺带清理因此不再使用的 dataclasses.replace 导入 |

离线验证（预算 300 秒内）：py_compile 全过；OfflineApiTests+config+materials+pdf_review+config 共 45 例 OK（skipped=10 为 PG 条件跳过，不计通过），其中新增 `test_materials_default_origin_policy_restored` 定向断言 materials/pdf-candidates 对同源自身来源 403 拒绝而活动面 200 放行（D1 区别测试）；npm run build（含 typecheck）通过，bundle 更新为 index-CiaiBKAO.js（CSS 未变）。

### 0.2 G2 PG 批（入口 #1+#2、容器 start 2/2）：26/27 通过，1 例失败已定位并修正测试，修正后实机复验 not_run

- 入口 #1（run_pg_batch.py，失败原件保留）：预检身份核验失败——runner 夹具错误，schema 核对查询在 postgres 库执行（pg_class 按库隔离恒为 0）；role/DB 归属本身全部正确。计入口 #1+start #1。
- 入口 #2（run_final_merged.py 合并批，PG 段）：身份核验全过（owner/role 旗标/成员资格/7 表），重置专用 role 随机口令（stdin 注入，不进 argv/日志/报告），unittest 实跑 27 例：**26 OK + 1 FAIL**（11.274 秒业务）。API 当前 PG 方法 10 项全过；workspace reads 8 方法中 7 过，`test_activity_list_pagination_cursor` 失败。
- 失败根因（非产品缺陷）：专用库存在 095 批次3 运行期返工中断残留的合成活动行 d77fe53c…（created_at 更旧，被第二页捞出）；该用例首次在非空库上运行，"翻页集合恰等于本用例 3 活动"的空库隔离假设失效（095 批次1 通过时库为全新空库）。list_activities/游标逻辑未改动，该例其余断言（limit/游标衔接/全局倒序/无重复）全部成立。
- 测试适配（不弱化游标语义断言，库内残留行按卡不删）：本用例 3 活动必须全部被翻页遍历到 + 首页只含本用例最新创建的行 + 无重复 + 全局倒序。静态与编译通过；**PG 实机复验 not_run（入口预算到限）**。注意：PG 批实跑的是测试文件修正前字节（5a7c8941…），修正后字节 ed32fe37… 未经实机验证。
- G2 其余项以实跑证据成立：单 SQL 计数（含 list_operations 恰 1 条）；列表投影真实返回列不含 payload（cursor.description 观察，非 SQL 字符串断言）；损坏正文仅单项拒绝而列表元数据仍可读、候选资格与内容校验语义分离（T1 反例，实跑通过）；绑定损坏失败关闭路径保持。

### 0.3 G1 浏览器批（合并批内首启）：夹具拼写缺陷 0 场景完成，修正后实机运行 not_run

- 合并批浏览器段：正式 dist 静态服务 127.0.0.1:18095（启动前核空闲）+ Playwright 首启即崩于 `fulfilAfter is not defined`（脚本拼写不一致），0 场景完成，16.242 秒。计浏览器启动 1/2。
- 修正（node --check 通过，实机 not_run）：统一拼写；静态复查另修三处——迟到响应锚点改用 waitForResponse 精确等待（原设计 fulfilments 数组未实现，会退化为 sleep 猜测）、s1 恒真断言改前缀判断、inflight 断言限定 s4 观察窗增量；加固 safeFulfill（导航/关闭竞态不再产生假 console 错误）、reload 前 settle、s5/s8 按 t_start 过滤。
- 脚本 s0—s8 覆盖卡面 G1 全部要求：刷新只 GET（普通 + unconfirmed/submitted 意图各一例）、刷新后不自动恢复旧选择、未知路由拒绝记失败、慢响应 tick 跳过与组内不重叠时间线断言、隐藏暂停/恢复只 GET、卸载清理、活动/展开迟到不串、失效分支与展开正文（转义/多字节）复验、显式动作后重读。**全部未实机运行**。

### 0.4 预算与收尾账（旧账/新增账分开）

- 旧账保留：7 次入口/6 次精确 start、claim 10 与保守 SUP 尝试 14 分开、业务 173.720 秒/收尾 23.217 秒；095 旧 8 小时投入实际已用分钟数无法可靠读取，按卡标未知、本轮以新增 120 分钟硬止（本轮实际主动投入约 90 分钟，限内）。
- 新增账：入口 2/2、容器 start 2/2、浏览器启动 1/2；业务合计 31.517/600 秒（PG 15.275 + 浏览器 16.242），清理 0.685/240 秒；离线准备与静态检查在 300 秒内；Windows Job/模型监督/真实模型/外网/用户库/费用全部 0。
- 收尾：容器批末 Running=false/Pid=0 原件留证；端口 18095 释放核过；dsn 未重建、未留任何口令落盘；残留合成行未删除。
- 停止依据：卡面"预算到限，完成独立部分并交回"。两个夹具修正均已完成至"待一个最小验证批"状态，不启动第三个真实入口。

### 0.5 未验证项、风险与下一步

- 未验证（not_run）：修正后 pagination 测试的 PG 实跑；修正后浏览器脚本 G1 全场景实跑。二者脚本/测试已就绪，接手批只需：一次合并入口（PG 段复跑 reads+api、浏览器段跑 task095-continuation01-browser.mjs）。
- 字节绑定提示：本节 post-hashes.json 为当前最终字节；PG 批 hashes-import/final 对应实跑时点字节（reads 测试文件与浏览器脚本此后有修正），原始三份哈希均在 continuation-01/final-merged/ 留证，不混称。
- 验收映射变化：C1/C12 相关由 O1 修正新增"列表投影无正文列"运行时观察（PG 实跑通过）；C6 新增 D1 定向区别测试（离线通过）；C9 的刷新只 GET 浏览器证据仍缺（G1 not_run）；D2 轮询修正无实机证据（离线构建通过）。
- 风险：O1 列表 payload_available 语义由"内容校验后可用"变为"候选资格"（前端展开仍走单条读完整校验，展示语义不变）；D2 轮询行为变更未经实机回归——上述均待 096 独立窗口按"只确认实际增量"处理。
- 本节不宣告 G6 最终通过、STEP006/008、M-1 或项目通过；不修改 095/096 历史正文与证据，正式 DocuS/CHG 留编排维护。

以下为原 TASK-095 合同窗口结果（历史保留，续作01 之上文）。

## 1. 结论与候选状态

实现候选已交付：活动只读面（列表/详情/四账/操作与正文）、零费新建、取消、显式继续（真实 launcher/SUP/worker/Job 链，替身传输零外网）、能力三层配置失败关闭、客户端意图台账与刷新恢复、工作区界面与导航挂载全部完成；定向验证中 PG/HTTP、真实 Windows 链与浏览器工作区全流均已通过原始证据留档。一处产品缺陷（展开成果未取回正文）经浏览器测试发现并修复，修复版仅以 typecheck/build 验证；受卡面批次与监督会话上限约束，未再进行实机复验，按停止规则交回（详见第 9、10 节）。G6 独立增强审计、STEP006/008、M-1 与整个项目均未宣告通过。

## 2. 身份、输入与快照

真实身份：本窗口为 Claude 桌面 Code（执行者 A+，与 TASK-092/094 同一实际窗口延续），运行模型 claude-fable-5，如实登记，不受档位标签影响。用户已于 2026-10-01 明确批准 094 裁定唯一包，本卡据此实施。

实施前核对（全部一致，未漂移）：有效合同 TASK-094-result.md（SHA-256 478b6cf7…f2fd）与 TASK-094-work-decision.md（8dce8806…49d0）按卡面指纹读取；冻结核心 repository.py（26c8eecf…bc3）与 service.py（1718c9ef…e03）在全部修改前实测一致；线框 4ffdbc2d…21f7 仅作布局参考，时间/同键/等待文案按六项修订执行。规则仍为 V4.0/CHG-0003 锁定版，未采用后来版本。

## 3. 实际文件差异与pre/post hash

20 个产品文件为本卡差异（8 个新增、12 个修改），逐项 pre（若曾读取登记）与 post 见 DocuN/evidence/TASK-095/final-snapshot/product-hashes-final.json，最终被测字节完整快照在同目录（可按相对路径独立重建，不依赖 Git）。要点摘录：

- 新增：backend/app/local_session.py、backend/app/activities/api.py、backend/app/service_config.py、config/activity.example.json、frontend/src/activities/（ActivityWorkspace.tsx、pendingIntents.ts、activity-workspace.css）、backend/tests/test_activity_workspace_config.py、test_activity_workspace_reads.py、test_activity_workspace_api.py、frontend/tests/task095-browser-continue.mjs、task095-browser-workspace.mjs（另有彩排脚本 task095-browser-rehearsal.mjs 未列入快照清单，仅离线使用）。
- 修改：backend/app/materials/api.py（认证提取为共享依赖，拒绝行为逐字保持；同源自身来源放行以便同一页面在测试端口发起同源写请求）、backend/app/main.py（路由挂载与配置状态注入，签名兼容）、activities/repository.py（仅追加只读方法与投影，未动原写路径与 _transaction）、activities/service.py（仅追加薄读取/取消包装，continue 签名不变）、frontend/src/main.tsx（导航挂载）、.gitignore（config/activity.local.json）、backend/tests/test_materials.py（一条 PDF 支持上线前的旧断言 415→422 修正，记录依据）、test_d3_recovery.py（G4 范围 CAS 引入 scope 提示校验后未同步的冻结假夹具补 version_id/source_revision 两字段，时钟顺序断言未动）。
- 未改：001—008 与全部持久模型、worker 全部文件、capabilities/gateway/transport、既有 claim/settle/cancel/admit/mark/record/recover 主体、runtime/deploy、依赖锁、正式 DocuS、公共库、用户配置；无 Git 写操作。

## 4. 实现纪要

后端：local_session 共享依赖（原 local_request/会话常量时间比对行为等价提取，materials/pdf 复用）；service_config 按 L0/L1/L2 三层加载本地配置（严格类型、无默认值、示例模板占位值校验失败、密钥仅经声明环境变量注入、L2 需完整 ModelServiceConfig 构造与 OneCallInput 线格式前置通过、启动一次加载不热更新）；activities/api.py 提供 capabilities、活动列表/详情、操作列表/单操作（每次请求恰一条 SQL 快照、状态与 read_committed_result 同源、列表不携正文、limit 加一探测、坏游标 400）、新建（服务端配置派生额度、锁内复核来源）、取消（既有幂等仓储薄包装）、显式继续（缺层 409 失败关闭、executor 固定 local-ui、run_tag 服务端生成、沿用既有 continue_from_result 与 to_thread/shield 边界）。操作列表投影同时复核工具结果语义，失效分支抑制正文；合法 131072 字节正文含多字节与转义经 HTTP 可读（专项用例）。

前端：意图台账（localStorage 单键，含 create 规范排序去重 source_ids；先写成功再 POST；损坏即阻止依赖恢复的新写动作，读取与取消不受影响；无授权物与返回正文）＋ 工作区（能力分层、额度预览、界面新建、两步取消、继续表单、操作与正文展开、四账与存活未知文案、每面板最后更新时间、约 3 秒仅 GET 轮询、未确认横幅与核对/同键重试/放弃三动作）。浏览器测试中发现两处产品缺陷：展开操作未按单操作接口取回正文；修好后仍误用列表行（不携正文）渲染详情面板——均已修复（前端源码），修复后 typecheck 与构建通过。

## 5. 合同到 C1—C12 证据映射

- C1 单SQL读取与投影：test_activity_workspace_reads（含执行次数计数探针、并发未提交写屏障，8/8 通过，批次1）；API 层同源与投影一致性、内部标识不出现（test_activity_workspace_api，批次3/4 全绿）。说明：该文件在批次1 全绿后仅追加了 DSN 跳过装饰器，最终字节的 PG 复跑未再做（行为差异仅为装饰器，按真实差异登记）。
- C2 新建幂等/409核验/来源竞态/缺配零写入＋浏览器恢复：api 测试（activity_exists、source_not_ready、source_replaced 映射、缺层 409 零写入）＋浏览器工作区流（响应丢失后刷新横幅、同键重试命中 409→范围核验、请求未到达→核对 404→显式同键重试成功；路由命中计数断言无自动重发）批次4 全绿。
- C3 取消：api 重复取消幂等与不存在 404、浏览器两步确认与文案，批次4 全绿；R 保守折叠与历史只读沿用 G3/D3 已验证主体，不重跑。
- C4 显式继续真实链：批次3 全绿——正常继续（committed_current、settled、reserved 0、cleanup 不全为假）、单次替身发送（消息角色 assistant,user）、PG 账面（received、正文值、请求/费用各加一、dispatch_closed、R=0、最近结算代次）、命名 Job 消失（FILE_NOT_FOUND）。浏览器查看该成果正文的复验未完成（见第 9 节）。
- C5 同键竞争与预检查后失败重试：批次3 全绿——并发同键至多一行/至多一次外发/请求恰加一；慢窗期间第二次请求 0 行 0 外发，随后显式同键重试成功；PG 层同键事实读取用例批次4 全绿。
- C6 权限反例与认证兼容：无会话/跨站/陌生来源 403、坏 UUID/游标 400（离线与 PG 均过）；test_materials、test_pdf_review、test_config 在提取后原样通过。
- C7 敏感不暴露：响应与错误体不含 DSN/密钥/内部标识/路径（断言与离线扫描）；意图台账仅业务键与用户文本；浏览器控制台除预期网络中断外零错误。
- C8 失效与禁止继续：来源替换后投影 invalidated_source 且正文抑制（reads 用例）、继续被拒 source_invalid（api 用例），批次1/3/4 通过。
- C9 断线/刷新与意图恢复：浏览器真实覆盖横幅、核对只读、同键重试、放弃前提示、损坏台账闸门（新建被暂停且可清除恢复）；"陈旧窗口取消"未做浏览器专项（仓储层幂等取消已由 api 用例覆盖），如实登记。
- C10 资料与PDF回归：浏览器真实上传 md→列表→正文可读；坏 PDF 得到"PDF损坏或格式无效"具体原因；既有资料/PDF 测试全部沿用。
- C11 配置分层与坏配置：10/10 配置用例（模板不可激活、缺段/坏类型/越界/不兼容、密钥缺失仅关 L2）；capabilities 运行时三层文案与管理预算 120 秒标签（不含排队/前后读取/清理）实测。
- C12 分页与大小：活动/操作两类分页、空/坏游标、limit 上界（PG 用例）；最大合法正文（中文多字节约 129KB 与反斜杠/引号/控制字符变体）经 HTTP 完整回读，批次4 全绿。

## 6. 预算、批次与失败修正账

批次入口 7 次（含一次仅 inspect 的夹具失败，未接触容器；上限 6，超出 1）；精确容器启动 6 次（上限 6，用满）；真实 Windows 业务监督会话约 13 次（上限 12，超出 1；两次为运行期缺陷返工所致）；真实业务累计 173.7 秒（上限 3600），资源收尾 23.2 秒（预留 600）；离线少于 1800 秒。全部原始记录见 attempt-ledger.json，失败原件未覆盖。

修正序列：批次1 三次失败（检验守卫把命名卷误判为非白名单绑定→修；管理角色名错用 retrolume→查 092 证据后改用 retrolume_task088_synth；TestClient/anyio 事件循环在 Windows 默认 Proactor 与 psycopg 不兼容→按产品启动口径固定 Selector 策略，离线验证后生效）。批次2 失败：bootstrap95 自举参数索引错（应为 argv[3]）、同键用例构造错（父键不可作同键目标，改为同租约多操作）——批次3 中 Windows 链六步全绿。批次3/4 浏览器失败：产品展开成果未取回正文、详情面板误用列表行渲染（两处产品修复，构建验证）；工作区流在批次4 全绿并留 9 张截图。同一缺陷两次有据修正后按规则停止实机复验。

## 7. 资源归属与收尾

仅使用精确旧合成容器 e49d3acc…（名称 retrolume-task-088-g3-w1，镜像 cf134a76…，命名卷 retrolume-task-088-g3-w1-data，127.0.0.1:55441，1CPU/512MiB/pids128，无 host bind；每次启动前按完整 inspect JSON 白名单核对，从不输出 Env）。新库 retrolume_task095_g6 与角色 retrolume_task095_synth（随机口令仅经 stdin/子进程环境，未入 argv/日志/报告；收尾已删除本地 dsn.json），001—008 顺序应用；库与角色保留不 drop。全部批次结束时容器 Running=false/Pid=0，应用进程已停（taskkill 本卡树并验端口释放），18095/55441 无监听，无本卡残留进程。未触碰旧合成库与任何用户库；无新容器/卷；真实外网、真实密钥、付费全部 0（socket 回环守卫＋受控传输替身，注入仅存在于测试进程环境，产品文件零修改）。

## 8. 复用与未重测

G3（正文原子提交与读取语义）、D3（监督/停止/恢复主体）、G5（工具与 kind 隔离）、G4（CAS 与父成果消费）在未改代码处沿用既有验收，未重跑；0092 批的注入式 Windows 链模式被复用（身份、序列、句柄与停止控制均走真实产品路径）。受共享认证提取直接影响的部分（materials/pdf 拒绝行为）以既有测试复验。

## 9. 未验证、缺口与风险

未验证：（1）修复后的"展开成果查看正文"未再实机复验（批次/会话/启动上限已尽，按停止规则交回；修复为前端渲染源切换，typecheck 与构建通过，建议并入独立审计卡的一次最小浏览器检查）。（2）reads 测试文件最终字节未在 PG 复跑（差异仅为跳过装饰器）。（3）陈旧窗口取消的浏览器专项。（4）真实环境网络中断、真实 provider、真实密钥、用户库迁移与生产部署均未涉及。风险：浏览器控制台在预期中断路径外无错误；响应丢失核对期阈值未做长时观察；监督会话与批次均超限一次，如后续卡延续将无剩余额度，建议审计卡自带明确小预算。

## 10. 偏差登记

D1 批次入口 7/6、D2 监督会话 13/12、D3 容器启动 6/6（超限原因：首检夹具误判 1 次与运行期才可见缺陷返工；每次失败均有原始记录且未覆盖）。D4 test_materials 415→422 旧预期修正（PDF 支持上线后行为已变化，修正依据记录于测试注释）。D5 test_d3_recovery 假夹具补字段（G4 引入校验后未同步）。D6 过期线框的等待/同键文案未照抄，按六项修订执行（卡面要求）。以上均不降低任何正确断言。

## 11. 建议 DocuS 变化与后续

架构增量（由编排书写）：G6 实现候选落地——activities HTTP 只读面与三类动作、service_config 三层、local_session 共享依赖、工作区与意图台账；状态"已实现候选，待独立增强审计"；FILE 登记新文件；API-002/003 状态注记更新。执行动态：登记本结果、批次账与超限偏差、下一 TASK-096/R-090 独立增强审计的输入（本结果、final-snapshot、attempt-ledger、四批原始证据），审计建议自带小预算并包含一次最小浏览器复验（展开成果正文）。文档变更记录顺延。README 未来应补：活动配置步骤（复制 config/activity.example.json 为 activity.local.json、密钥环境变量）、意图台账可清除说明、工具动作与首次学习入口尚未开放。必要人工：仅转交下一审计卡；无需用户密钥、无需用户库操作。
