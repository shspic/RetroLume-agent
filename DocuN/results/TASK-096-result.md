# TASK-096 / R-090 review-02 G6三处修正与运行证据增量终审结果（2026-10-02）

## 结论

增量终审通过：D1（materials/PDF 认证恢复默认）、D2（轮询与异步上下文保护）、O1（操作列表无正文投影）三处修正与合同及已批准 094 设计逐项相符；G2 以字节级重建闭合（当前 reads 仅还原分页区段后整文件 SHA-256 精确等于批时 c1c40c…，26 个 OK 方法字节适用性成立，分页单方法在最终字节上真实专用 PG 重跑 OK 且非 skip）；G1 经批时脚本逆变换逐字节重建（5e541e22…）独立判定：9 场景实际执行、25/25 checks 为 true，唯一 FAIL 系夹具观察窗定义错误（结构必真，非额外写行为），刷新只 GET、显式恰 1 POST、动作后读取等有效子项独立成立并予采纳，原 FAIL 与原报告不改写；执行控制与新增记账相符（续作01 入口 2/2、容器 2/2、浏览器 1/2；续作02 各 1/1；累计入口 10/10、容器启动 9/9；业务 74.440 秒记实；旧超限/漏时原样保留）。原 TASK-095 G6 完整成果（含三处修正与两轮补证）已具备交编排关闭 G6 的验收条件；未发现阻断缺陷，真正剩余项均为非阻断观察与限制（见后）。本文件不代替编排最终裁定。本轮全部为只读核验，新增运行额度 0。

受影响验收项映射（增量）：C1/C12←O1（列表 DB 层无正文列 + 损坏正文列表/单项区别 + 分页适配）；C6←D1（materials/PDF 默认恢复 + 定向区别测试批时 ok）；C9 与「五、界面」←D2+G1（刷新/意图只 GET、慢响应不重叠、隐藏/卸载、迟到隔离、展开正文）。

## A 代码轴：D1/D2/O1 三处修正（前件→当前有限差异）

前件 = DocuN/evidence/TASK-095/continuation-01/pre-originals/ 五份副本（pre-hashes.json 绑定首轮审计身份），本轮对三产品 + 两测试生成全文差异（见本卡 evidence：diff-materials-api.diff、diff-repository.diff、diff-activity-workspace.diff、diff-test-api.diff、reads-pre-to-current.diff）。

### D1 认证恢复（backend/app/materials/api.py 09b2be09…→e463ed5d…）

- repository() 由 `local_session(request, allow_own_origin=True)` 恢复为 `local_session(request)`（单一 hunk + 注释），恢复默认固定来源白名单与拒绝文案。
- PDF 复用链同步恢复：backend/app/pdf_review/api.py（a50fc89b…，未变）全部路由经 `repo = repository(request)` 复用 materials 的依赖，因此同源自身来源不再放行。
- 活动面保留：backend/app/activities/api.py:85 `local_session(request, allow_own_origin=True)`（dcccbbb1…，未变，属合同明示）。
- local_session.py（fed7bbde…，未变）：跨站先拒；固定白名单仅 127.0.0.1/localhost 的 8000 与 5173；allow_own_origin 仅放行 requests 自身 scheme://netloc；常量时间 token 比对。未扩大白名单/会话 token/TrustedHost/Sec-Fetch 语义。
- 定向区别测试真实覆盖：test_activity_workspace_api.py（81fcb6d3…→a5c95c79…）新增 test_materials_default_origin_policy_restored：同源自身来源（http://testserver）下 /api/materials→403、/api/pdf-candidates→403、/api/activities/capabilities→200；原 test_own_origin_allowed_for_same_site_page 断言保留。批时原始输出该例 ok。首轮未变认证结论继续继承。

### D2 前端轮询与异步上下文（frontend/src/activities/ActivityWorkspace.tsx a3ba46d6…→b6a339d0…）

- 新增 mountedRef（卸载置 false）、pollInFlight 在途标志、listSeq/detailSeq/openSeq/opsLoadSeq 四个请求序号。
- refreshList/refreshDetail/loadMoreOperations 的成功与失败路径均做「mounted + 序号 + selectedRef.current 上下文」保护：迟到响应与迟到失败不覆盖新选择、不写旧状态。
- selectActivity 递增 openSeq 使在途展开失效并显式同步 selectedRef；toggleOperation 任何面板切换先递增 openSeq，迟到正文不覆盖新面板，失败保持列表行信息。
- 轮询重写：仍为 3 秒 setInterval；poll() 于 pollInFlight 或 document.hidden 时跳过（在途不重入、隐藏暂停）；标志在 finally 必然释放（单次失败不永久卡死）；visibilitychange 隐藏 stop、恢复 start 并立即一次只读 poll；卸载 stop + 移除监听。
- 仍为只读：轮询仅 refreshList/refreshDetail（GET）；无自动 POST、无自动换键/业务重试、无缓存队列；显式动作后的读取不受抑制（G1 s3 实测动作后 11–14ms 内 list/detail/ops 三个 GET）。
- 与 094 B2「自动刷新仅在有运行中或未确认意图时进行、只发 GET、约 3 秒、可中止、不并发」一致；与合同「保护活动/操作上下文及请求序号」逐项对应。

### O1 操作列表投影（backend/app/activities/repository.py 295e3e95…→ac55739c…）

- 差异仅 4 处：移除已无用途的 replace 导入（合同明示不升新硬门）；新增 `_OPERATIONS_LIST_SELECT = _RESULT_READ_SQL + 元数据列 + payload_eligible 布尔 + FROM/JOIN`（数据库层不返回 payload 列）；新增 `_operation_list_row_from_row`（状态行内推导；payload_eligible 与状态推导双向核对，不一致即 ResultIntegrityError 失败关闭；绑定损坏仍失败关闭；payload 恒 None）；list_operations 改用之。
- 原 _RESULT_READ_SQL、_OPERATIONS_SELECT（单读）、_read_status、read_committed_result、list_committed_results、写路径、持久模型、worker/监督/transport 均未动（继承首轮结论）。
- 单条路径保持单 SQL 完整校验：payload 非空即 validate_business_payload（hash 复算/封套）+ kind=tool 工具语义校验，损坏即单项拒绝（repository.py:2055-2094、2170-2183）。
- 测试差异（reads 5a7c8941…→ed32fe37…）：CountingLedger 增记 cursor.description 列名；新增运行期断言「list_operations 返回列不含 payload」；损坏正文用例改为「单读拒绝 + 列表 4 行元数据仍可读、T1/P payload_available 为真、payload 为 None」；分页用例按合同改为子集/顺序断言（本例三 ID 全部被遍历、首页只含本例最新行、全局倒序、无重复、非法游标拒绝），未删除合同要求保留的任一断言。API 测试改动为纯新增，不看弱原有断言。

## B 证据轴（一）：G2 最终后端证据适用性 —— 已闭合

- 批时字节判别：续作01 批时 reads = c1c40c356ca22e719f2ba1f7a937f9546eff48c10fb089d066c51a112b5ed19e（final-merged 的 pre/import/final 三次记录一致）；其原 pre 5a7c8941… 不是该批实际测试字节（首轮 post-hashes 注记中「批时跑的是 5a7c8941」一句与事实不符，close-02 已作纠正，原历史不改写）。
- 本轮独立重建：取当前 reads（ed32fe37…），仅把 test_activity_list_pagination_cursor 方法区段（232-266 行）替换为 pre 原文（224-247 行），整文件 SHA-256 精确 = c1c40c…（副本 reads-as-run-c1c40c-reconstruction.py 在案）。重建文件中失败断言位于第 243 行，与批时 traceback「line 243, self.assertEqual(set(seen), …)」逐字一致——批时字节的三重指纹 + 重建 + 行号一致互证。
- 27 方法真实输出（final-merged/unittest.out.txt，returncode=1，Ran 27，11.274s）：唯一 FAIL = 分页用例（专用库 095 批次3 残留合成行 d77fe53c… 撞上旧空库隔离假设；非产品缺陷，其余同方法断言与游标逻辑保持）；其余 26 OK = 7 reads PG + 10 PG API + 9 离线 API，不与「26 全部 PG」或「整批通过」混淆。
- 适用性：c1c40c 与当前仅分页方法一处不同（其余方法字节全同，重建已证），26 个 OK 的字节适用性成立；后端 app 8 文件（local_session/service_config/activities api/repository/service/main/materials api/pdf_review api）在续作01 与续作02 的批时 hash 均 = 当前；dist 四产物、两测试同绑定；本轮 identity-recheck 索引 48e7a55e… 重算一致，51+5+47 项全部 MATCH。
- 分页单方法重跑（续作02，run_c02_merged.py 唯一入口；开跑前 FROZEN 强制核六项 + 夹具 5e541e22）：returncode=0，Ran 1 test in 0.488s，OK，skipped_present=false；阶段 11.713 秒（含容器启动/身份核验/stdin 口令重置/单测全段）与测试 0.488 秒分开记录，不虚算。身份核验原件：owner=retrolume_task095_synth、role=[login 仅]、memberships=0、sessions=0、task095 库 7 表。
- 单 SQL 计数、cursor 列名不含 payload、损坏正文列表/单项区别：均以真实方法（repository.py 2009-2183；测试 184-197、267-331）与原始输出（26 OK 逐例）核验，未以 SQL 字符串断言替代。
- 结论：G2 闭合；首轮登记的「batch4 批时绑定无逐批哈希」缺口消除，且 reads 8/8 方法均具备当前字节上的真实 PG 通过（7 例经字节全同继承 + 分页直接重跑），API 19/19 同批通过（10 PG + 9 离线）。

## C 证据轴（二）：G1 浏览器原 FAIL 与有效行为子项 —— 有效子项成立

- 批时脚本身份：当前 frontend/tests/task095-continuation01-browser.mjs = ee9074b8…（两处跑后修正，not_run）；本轮逆变换（还原 s3 的 some(POST) 失败行、删除新增 summary.post_total 同步行、其余字节不改）逐字节 = 归档副本 browser-as-run.mjs = 5e541e22…（复算一致；该副本为可独立复算的逆变换重建，非当时独立留存原件，如实标注）。续作01 实跑版为 63863d65…（拼写错 fulfilAfter，ReferenceError 崩溃、报告未生成，s0-s3 截图在案）。
- 控制流独立复核（读批时脚本全文）：静态服务只服务真实 dist（越出 DIST 403、缺文件 404、no-store）；全部 /api/** 由 Playwright route 合成；未知/未合成路径拒绝并记 blocked（blocked_empty 检查）；route 回调异步异常显式记 failure + 兜底 500；主循环异常记 exception 且 finally 必写报告；checks 失败不中止后续场景。
- 9 场景实际执行（相位请求计数）：s0 8 / s1 9 / s2 7 / s3 11 / s4 6 / s5 6 / s6 12 / s7 7 / s8 3；每步以 DOM 等待锚定（超时即异常）；5 张截图本轮目视复核：s0 能力带与「选择一个活动」、s2 未确认横幅（含三项只读动作文案）、s3 显式创建横幅与「尚无操作」、s6 B 面板仅含 B 行且 FAST-正文标记ⓑ 渲染、s7 失效行无继续入口/OP-A1 展开显示含转义与多字节正文及「从该成果继续…」。25 项 checks 全 true（运行期）；唯一 failure=「s3 after-action slice contains POST」，该串仅存在于批时字节（当前 fixture 已无），报告与批时脚本互相印证。
- s3 误报独立判定：beforeS3b 于显式点击之前记录（批时脚本 298-300 行），切片必然包含该显式 POST 自身，some(POST)→failure 为结构必真。独立证据：s3_explicit_post_exactly_one（postTotal-postBefore=1）、post_total_is_one（全局恰 1）、s3_submitted_intent_no_auto_post（刷新窗全 GET）、s3_read_after_explicit_action（动作后 list GET）全 true。完整日志重计：69 条 = 68 GET + 1 POST；该 POST 于 22:39:55.612、耗时 1ms、在途 0，属「重新提交同一意图」点击；其后 11-14ms 内 list/detail/ops 三个 GET（显式动作后读取）。刷新观察窗（session/materials/pdf-candidates/capabilities/list，含 2 秒稳定期）全 GET，独立证明无自动动作。report.post_total=0 为报告字段未同步（跑后已修、not_run），与日志计数 1 分开核明。
- s4：两次 list 相距 6.003 秒、各约 3.2 秒、无重叠、窗内配对峰值 2（来自同 tick detail+ops 微重叠）——与「3 秒节拍 + 在途跳过」精确一致；s5 隐藏 5 秒 0 请求、恢复≥2 只 GET；s8 卸载后 0 请求。
- 修正版（ee9074b8）not_run 处置：两处修正均为夹具观察窗定义与报告字段同步，不增加尚缺的产品覆盖；有效行为子项本已成立，依合同「可以采纳有效子项，不以整批汇总变绿为额外门」，无需真实重跑；原 FAIL/原报告/脚本运行史/预算不改写。
- 证据边界：隐藏经 document.hidden + visibilitychange 合成，只证明对应事件处理，不夸称完整 OS 遮挡；合成 API 只证明前端，不冒充新增真实 HTTP/PG/模型/Job 链。dist 对象关系：dist/index.html（ce7f4d66…）引用 assets/index-CiaiBKAO.js（b2ae0531…），续作02 报告 bundle.index_js 同名，c01/c02 三份指纹与当前一致；内容级判据：CiaiBKAO 含 "visibilitychange"（D2 新监听）而首轮重建旧 bundle 7xLKRnHC 不含 → 现行 dist 确为 D2 修复后的重建产物。构建命令/输出未在可核证据中留存，不据共存 hash 声称构建起源已证明（构建起源由内容判据 + 运行行为证据支撑）；CSS/pdf.worker hash 与旧 dist 相同（无样式/资源差异）与此一致。

## D 控制轴：执行控制与资源

- 续作01：入口 2/2（#1 run_pg_batch.py 因 schema 探针错连 postgres 库（pg_class 按库隔离恒 0）abort——原件 pg-batch/adopt-identity.out.txt schema_tables=0 在案；#2 run_final_merged.py 合并批）；容器启动 2/2；浏览器启动 1/2（崩溃后二启无承载入口，遵停）；业务 31.517 秒（PG 15.275 + 浏览器 16.242）/600；收尾 0.685/240。
- 续作02：唯一入口 1/1；容器启动 1/1；浏览器启动 1/1；业务 74.440 秒（PG 阶段 11.713 + 浏览器 62.727）/300；收尾 0.69/120；容器批末 Running=false/Pid=0，端口 18095 先核空闲、跑后释放。
- 累计：入口 7+2+1=10/10；容器启动 6+2+1=9/9；旧 claim10/保守 SUP14、原 7/6 入口/启动超限与漏时原样保留；新许可与旧用完许可分开，未以同窗口清零。
- 资源纪律（原件核）：仅复用 e49d3acc3c1be13d670af68bca2b082fea4faeeb9b9babe69df7f1d3941696a4/镜像 cf134a76…/卷 retrolume-task-088-g3-w1-data/loopback 55441；口令 token_urlsafe(24) 经 stdin（输出原件无口令）；DSN 仅子进程环境并清除继承 RETROLUME_DATABASE_URL/DATA_DIR/BACKUP_DIR；两批 finally 停容器并核停。无需重做 Docker inspect/启动/收尾；编排 2026-10-02 00:10 的端口/进程观察（listeners 0、fixture 进程 0、docker 查询 0）按索引如实登记为「该时点观察」，不等于实时 Docker 查询。
- 记账观察（非阻断）：续作01 入口#1 abort 段（约 21:25:44–21:25:50 加容器启停，约 10 秒量级）未计入其 31.517 业务秒，按「漏时原样保留」类别登记；续作02 post-hashes.json 的 generated_at（22:35:49）早于其描述的 22:39–22:40 运行、mtime 22:42，属时间戳滞后小瑕疵（内容与哈希无碍）。

## 最终对象 hash（关键，本轮重算）

- reads 当前最终 ed32fe37004bde9af37a33066cb8c79755754aa6fcdff7cd24f51ee06fbae268；批时（重建）c1c40c356ca22e719f2ba1f7a937f9546eff48c10fb089d066c51a112b5ed19e；续作01 pre 5a7c8941a69dce17a41d6297afd55eb72ef7e0766c729bca86c6a6cba21a3907。
- API 测试 a5c95c794e8e8f91ff71ba3427e964dd177ee4be413c6966750bb7ec31885a4f；materials/api e463ed5d90a656527b33fa3829f74d0716d99635e9a27683d1e82155affb3d79；repository ac55739c9f35596f62b610069dd6f1ca558cc98bf666bcc814533ee257e7670c；ActivityWorkspace b6a339d0847699caa3aa998c6f063997d9f7d236035f2d13070fb728c95348b5。
- 浏览器 fixture：as-run（重建）5e541e22e60b3d69e2e9f334ce52abd3248c2bb0fe01622f8a38aad9dbc124a3；当前（not_run 修正版）ee9074b8f85ab94d382c6843e5d1d3f6d3a6eb42dfc69d14c9b8f151f15970c1；续作01 实跑 63863d6545502fb2f72dba9d026eb32c67ab55efc190c30fd1486cf192729cab。
- dist：index.html ce7f4d66cb368186ed4a9e7a67486724e3abed546361b6f1e5510aa2f6aa3476；index-CiaiBKAO.js b2ae053151ef410b604a60983b13260c97abd69b3353701e8a32d053c70538e7；CSS/pdf.worker 未变。
- 增量索引 increment-input.json 48e7a55e4e019e82a74af647352168196ac2437f48266210078ddc21c08b5b86（重算一致）；51 项当前/5 补充/47 证据全部 MATCH（identity-recheck.json）。

## 继承范围、限制与未验证

- 继承：旧 51 项中 46 项未变身份继承；80 项旧证据与首轮全部未受影响的代码/证据/控制结论直接复用；旧 D3/G5 运行证据不重跑。首轮两处证据缺口（最终字节刷新只 GET 浏览器证据、batch4 批时绑定）在本轮闭合。
- 限制与未验证（均非阻断）：（1）两处批时副本（reads c1c40c、browser 5e541e22）为可独立复算的逆变换重建，非当时独立留存原件（browser 原运行件未留；reads 另有三次运行期指纹与行号一致）；（2）CiaiBKAO 构建命令/输出未留存；（3）夹具未含显式外网阻断——运行日志/console/blocked 未见未知路由与外网痕迹，但不夸称已阻断任意外网；（4）report.post_total 字段未同步、console log 引用未赋值的 summary.inflightPeak（外观性）；（5）UI 文案「已提交，正文可回查」（ActivityWorkspace.tsx:89）由 read_status 派生（绑定/范围/来源），不承诺正文内容完整性——损坏正文行列表仍显示该状态、展开时才暴露单读拒绝，措辞略强于候选语义，属既有文案非本次引入；（6）续作01 post-hashes.json 的批时字节一句已注明与事实不符（实际 c1c40c）。

## 独立性、接触与实际操作披露

- 实际环境：Claude 桌面 Code（会话环境登记模型 Fable 5 / claude-fable-5），新会话窗口；未参与 092/094/095 实现与续作01/02 修复；与修复窗口（登记 WorkBuddy GLM-5.3-Flash、非 096 审计窗口）为真实不同会话。披露：首轮结果文件自登记客户端为 WorkBuddy（GLM-5.3-Flash），与本窗口实际环境不同——不凭资源标签声称身份，差异如实列出供编排裁定；相同/不同型号都不单独作为独立性证明，独立性由「未参与修改 + 仅读允许对象 + 结论由源码/合同/原件独立支撑」成立。
- 接触：只读本卡允许的源码/合同/原件（清单见 verification-summary.json）；未读 TASK-095-result.md、TASK-095-work-decision.md、TASK-096-work-decision.md 及任何实现聊天/推理/自评；无意外接触；未读或恢复任何用户配置/秘密/已删除 dsn.json。
- 本轮操作：纯只读——103 项身份重算、6 份差异重建（含两份批时副本逆变换）、完整 69 条请求日志重计与相位统计、5 张截图目视、两账本/两 runner/全部相关原件文本核验。未运行编译/单测/构建/浏览器/PG/Docker/应用/Windows Job，未安装、未 Git 写入、未触网；新增运行额度 0。用时：本轮无法自测精确分钟，按约 50 次只读工具调用与串行窗口保守估计低于 90 分钟上限，并与首轮 4 小时审计总账累计；精确值无法分层确认，如实标注。

## 待同步文档与建议下一步（由编排裁定）

- 执行动态文档登记本 review-02 结论与 G1/G2 缺口闭合；架构动态/文档变更记录如采纳非阻断观察再顺延登记。
- 建议：以本增量结论交编排关闭 095/G6（含 D1/D2/O1 与两轮补证）；「已提交，正文可回查」文案与构建留存两类小项可作为后续非阻断改进，不设为验收门。
- 本文件不代替主控最终裁定；不宣告完整 STEP006/008、M-1、真实 provider/用户库或整个项目通过。

---
以下为首轮（2026-10-01）完整结果全文，原样保留、未改动：

# TASK-096 / R-090 G6完整成果集中独立审计结果

## 结论、差异与证据导航

本轮为 R-090 独立增强审计（接收 A+，真实客户端 WorkBuddy（GLM-5.3-Flash），全新隔离会话，未参与 092/094/095 实现或设计）。对象为 TASK-095 完整 G6 成果（浏览器活动动作面与服务端配置受控接线），审计时点 2026-10-01 17:06—18:10 左右，主动投入约 60 分钟，运行额度仅本卡授权的最小浏览器专项（构建 3.1 秒 + 浏览器两次启动共约 47 秒业务）。

三轴结论。

一，代码轴：未发现确定缺陷（无 P0/P1/P2）。登记范围偏差 2 项、非阻断观察 5 项，全部列于下文"发现清单"。核心合同条款（认证提取、单 SQL 快照、四账与文案口径、意图台账与同键边界、配置三层失败关闭、脱敏投影、零新 DDL）逐项与源码核对一致。

二，证据覆盖轴：执行者的关键缺口（batch4 采集后 16:30 对 ActivityWorkspace.tsx 做两处 UI 缺陷离线修复，仅 typecheck/build 验证、未实机复验）已由本卡闭合——本卡从冻结源码重建 bundle，四个产物 SHA-256 与正式 dist 完全一致，证明现有 dist 绑定最终字节；随后以合成响应浏览器专项实测最终 bundle，11 项显示行为检查全部通过（含列表无正文、单操作正文显示含转义与多字节、低信任字符串不执行、慢回包与切换不串正文、失效抑制正文且不开继续入口、陈旧 running 前端两步取消）。仅"刷新只 GET 无 POST"一项在最终字节上未取得浏览器级证据（本卡夹具缺陷耗尽 2 次启动额度，记 not_run），以静态结构证据加 batch4 旧字节 A 级证据支撑，登记为非阻断证据缺口。

三，执行控制轴：容器守卫、专用库角色、凭据纪律、传输注入边界、finally 收尾全部合规；批次入口 7 次（上限 6，超 1，与执行者 stop-decision 自报一致），容器启动 6 次（上限 6，恰在限内），Windows 监督会话可证下界 10 个 claim 窗口（上限 12 内）、保守上界 14（超 2，账本自记"超 1 次"存在口径误差），业务累计约 173.7 秒（上限 3600）。超限与越界未因最终成功追认为合规，按偏差登记。

完整 G6 能否交编排验收：建议可以提交编排验收，按"有条件通过"路径处理两项已登记缺口（最终字节上的刷新只 GET 浏览器证据、后端 batch4 测试绑定缺逐批哈希），二者均有 B 级或旧字节 A 级支撑、无已知缺陷指向。本审计不签 M-1、完整 STEP006/008 或整个项目通过。

对象身份核验：当前 51 项产品/测试/依赖文件 SHA-256 与 input-snapshot.json 全部一致（51/51 MATCH）；80 项原始证据全部一致（80/80 MATCH）；最终快照 16 个产品副本与当前产品字节逐一相同（identity-check.json 见本卡 evidence/audit/）。

## 发现清单

### 范围偏差（合同范围条款与实现不一致；均无安全影响）

D1 共享认证提取非纯等价：materials 的 repository() 改为 local_session(request, allow_own_origin=True)，PDF 面经 materials 复用同样生效。原合同（095 第二条）要求"资料/PDF 拒绝行为"保持；094 B8 要求"行为逐字保持"。实际效果：生产 8000 端口行为不变（自有来源 http://127.0.0.1:8000 / localhost:8000 本就在固定白名单内）；非标准端口（如测试端口 18095/18096）下，此前一律 403 的"未知来源"中等于服务器自身来源的请求现被放行。活动路由使用 allow_own_origin 属合同明示（"写动作必须验证本地会话及同源"），材料同步启用无合同依据。可利用性分析：跨站请求先被 Sec-Fetch-Site 拒绝；浏览器 Origin 由真实页面源决定，攻击者页面无法呈现服务器自身来源；DNS rebinding 的 Origin 为攻击者域名不匹配。结论：无可利用的跨站暴露，测试端口未成为任意来源通道（仅"同一来源"放行）。最小修正归属：若编排要求逐字等价，可仅在活动路由传 allow_own_origin、materials 恢复默认；属低风险代码微调，不阻断。另 /api/session 仍为严格 local_request（无自有来源放行），行为不对称但方向保守。

D2 前端轮询无在途防重入：ActivityWorkspace.tsx 轮询为 setInterval 每 3 秒直接触发 async GET，无 in-flight 守卫；响应慢于 3 秒时可能并发重复 GET；亦无 document.hidden 暂停（仅卸载清理）。合同（095 第五条）要求"轮询约3秒只GET、不重叠、隐藏/卸载可停止"。全部为只读 GET、服务端有界，无安全影响；"不重叠"未严格达成。最小修正归属：前端 ActivityWorkspace 轮询 effect 增加在途标志与可见性判断。

### 非阻断观察

O1 操作列表 SQL 在数据库到应用层传输正文后在 Python 剥离：_OPERATIONS_SELECT 复用 _RESULT_READ_SQL 并投影 CASE 抑制后的 payload 列，list_operations 在返回前以 replace(payload=None) 剥离。HTTP 层"列表不携正文"成立（有测试）；但"单条结果读取是唯一正文通道"在 DB 传输层不严格成立（一页最多 100 行 × 128KiB 正文流量），且任一行正文损坏会使整页列表 409（同源校验失败关闭，方向安全）。建议后续把列表 SQL 的 payload 列改为可用性布尔投影。

O2 无结果行的读取状态判定与 read_committed_result 字面不同源：read_operation/list_operations 对无结果行按 state 细分（reserved/dispatched/unknown 为 unresolved，其余为 terminal_without_payload），read_committed_result 对无结果行一律 unresolved。有结果行走同一 _read_status，完全同源。新行为与 094 B1 文案定义（terminal_without_payload 覆盖 not_sent）一致，属更精确而非缺陷；"同源"表述在无正文分支不严格成立。

O3 HTTP 错误映射依赖中文异常消息匹配：api.py 以"已存在"/"撤销"/"替换"/"不存在"子串匹配 ActivityLedgerConflict 消息决定 409/404 分支。消息改动会静默改变映射；建议后续改用专用异常类型或错误码属性。

O4 未列彩排脚本：frontend/tests/task095-browser-rehearsal.mjs 未列入 product-hashes-final.json（20 项清单），但属合同允许的 task095 前缀浏览器测试命名，内容为离线渲染彩排 helper，无产品依赖。清单遗漏，已在 input-snapshot 纳入身份核验。

O5 逐批产品字节未冻结：common.product_hashes() 仅在 finalize 调用，batch1—4 运行时未记录导入哈希；"每次开跑冻结产品"的合同要求未完整执行。影响见"证据绑定缺口"。

### 证据绑定缺口（验收条件项）

G1 刷新只 GET 在最终字节上无浏览器证据：本卡专项 s1—s6 通过后，s7（reload 后清点请求）因夹具未合成 /api/materials 与 /api/pdf-candidates 路由并漏点击活动而中止；本卡浏览器 2 次启动额度（首启因夹具路径分隔符缺陷失败、二启复验 s1—s6 全过）已用尽，按卡停止。支撑证据：静态层面最终字节 ActivityWorkspace 挂载 effect 仅调用 GET（capabilities/activities/detail/operations），POST 仅存在于三个显式点击处理器；batch4 browser-workspace（旧字节）实测 reload 后 POST 计数精确等于两个预期写入流（hold 2 + abort 2），无额外自动重发。两处离线修复（展开取单操作、面板渲染取回数据）不触及意图提交与挂载逻辑。

G2 后端 batch4 测试的批时绑定无逐批哈希：batch4 PG API 18 例 OK 证明其时后端字节，但无批时哈希证明该字节与最终字节一致；"两处修复仅涉 ActivityWorkspace.tsx"系执行者账本声明（补录说明不当客观证明）。支撑：finalize 快照 post 哈希=当前=输入快照；前端 bundle 重建已证 dist 绑定最终源码；静态复核最终后端代码与测试断言一致。风险低；如需更强绑定，编排可另行安排一次只读 API 测试批（不属本卡授权）。

## 操作与验证详情

### 读取与独立核对

按卡顺序读入：根 AGENTS.md、公共库 DocuS/AGENTS.MD 与 WORK.MD（第 2/6/8/9 节，指纹与 rules-snapshot.json 一致：AGENTS.MD e7e6b1a8…d4514、WORK.MD 96211d15…3461a）、本卡、input-snapshot.json、TASK-095 完整合同、TASK-094 修正轮01 A—D 与置顶六项修订、51 项当前源码/测试/配置、TASK-095 原始证据（attempt-ledger.json、common.py、finalize.py、run_batch1_pg.py、run_batch2_win.py、inject/sitecustomize.py、win/bootstrap95.py、batch1—4 输出与截图、final-snapshot 20 份）。禁止项遵守：未读 TASK-095-result.md、TASK-095-work-decision.md 及任何实现自评；未读 runtime 私有配置与 dsn.json（已确认其不存在）；未执行任何旧 runner。接触披露：无意外接触。

身份核验脚本（本卡 audit/verify_identity.py）输出 identity-check.json：51/51 与 80/80 MATCH；final-snapshot 与当前产品逐字节相同。

### A 真实对象、差异和兼容

改动集合重建：product-hashes-final.json 的 pre 取自 094 读入清单与两份合同冻结哈希。有真实 pre 的 6 个文件全部实际变更（repository 26c8eecf…→295e3e95…、service 1718c9ef…→f98b25b7…、main 4eb9f27b…→b0e71fca…、materials/api f66650e1…→09b2be09…、.gitignore 7b56964c…→3bbc35fa…（与 TASK-080 续作01 post 连续）、main.tsx 04817ccc…→e8ec380e…）。新增 9 文件（local_session、service_config、activities/api、activity.example、pendingIntents、ActivityWorkspace、css、三个 workspace 测试、两个浏览器测试）均落合同允许路径。pre=null 且非新增的 test_materials.py 与 test_d3_recovery.py 经内容检索无任何 095 痕迹（无 allow_own_origin/18095/workspace/活动引用），无断言弱化迹象；字节级等价无法证明（pre 未存档），按实际证据限制结论。

repository.py 只增核验：新只读区段自 1877 行注释起（probe_storage/list_activities/read_activity_facts/read_scope_source_versions/list_operations/read_operation + _ACTIVITY_FACT_SQL/_OPERATIONS_SELECT/_activity_fact_from_row/_operation_row_from_row），新增 ActivityFactView/OperationRow 数据类恰解释 094 合同锚点位移（_transaction 238→300、read 1643→1705、list 1713→1775，均 +62）；_transaction/_RESULT_READ_SQL/_read_status/read_committed_result/list_committed_results/record_outcome/create_activity/cancel_activity 结构与 094 定位一致，未见写路径改动。service.py 新增 7 个薄包装（245—271 行独立区段），continue_from_result 与 execute_tool_action 主体结构匹配 094 定位。冻结范围（worker、迁移 001—008、gateway、transport）不在改动集。test_d3_recovery 未超允许清单；test_materials 无旧断言调整痕迹。

### B 浏览器授权、配置和既有接口

local_session.py：跨站拒绝、未知来源拒绝、固定白名单、常量时间会话比对逐字保留；allow_own_origin 仅放行"与请求自身 scheme://netloc 相同"的来源（见 D1）。activities/api.py 全部路由经 _guard（local_session）；capabilities 先于带参路由声明；读取与取消不依赖配置（L0 不调 _config）；503 database_not_configured/config_unavailable 可辨；请求体 extra=forbid、仅业务键与文本；executor 固定 local-ui、run_tag 服务端生成（ui-+32hex）；followup ≤4096；operation_id 白名单正则；无 DSN/密钥/provider/额度/G/scope 输入通道；浏览器无法传 argv。无 CORS 中间件；TrustedHost 保持 127.0.0.1/localhost/testserver；no-store/nosniff 中间件保持；账本独立失败关闭（DSN 缺失只关活动面，资料入口不受影响）。

service_config.py：L0 无需配置；L1 需模型标识与额度段且经 ActivitySpec 纯内存演练；L2 需完整 service 段、api_key_env 声明的环境变量、thinking=disabled、timeout≤10、请求/响应字节≤65536（one_call 配置上限启动前校验）、输出预算兼容、ModelServiceConfig 完整构造加 OneCallInput 线格式前置；任何失败按 config_missing/config_invalid/config_incompatible/provider_key_not_configured 精确失败关闭；启动一次加载、无热更新；key 仅经环境变量，不进文件/响应/日志。activity.example.json 全占位值（0、"REPLACE ME MODEL"）无法通过校验（测试证实）。.gitignore 增补 config/activity.local.json，原 12 行未动。main.py 注入路径 RETROLUME_ACTIVITY_CONFIG 或默认 config/activity.local.json。

### C 读取、账本和文案

四类读取每请求恰一条 SQL 由 CountingLedger SQL 计数测试证明（均=1）；_ACTIVITY_FACT_SQL 单语句内用 jsonb_agg 派生来源有效性（判定口径与 claim/admit 一致：current_version 与 revision 同时匹配快照）；_OPERATIONS_SELECT 与 read_committed_result 共用 _RESULT_READ_SQL 绑定三联列与 _read_status。失效抑制正文（SQL CASE + Python 双重）、列表 payload=None、元数据有界（B1 白名单投影）、limit+1 探测、活动 (created_at,id) 双键倒序、操作 operation_id 序、坏游标 400、空页 null、末页 null 均有断言。131072 字节合法正文（含反斜杠/引号/控制字符/多字节）经 HTTP 可读（test_max_legal_payload_is_readable_through_http）。UI 文案逐条核对：预扣不退还、S 为单调实测含保守折叠、账本只留最近一次结算、本机单调硬停止与墙钟租约分层、运行中为账本事实且执行存活未知、取消不撤回远端、120 秒为管理预算非完整 HTTP 上界（截图确认）。页面无 SQL/路径/hash/admission_id/executor/G/remote_request_id（投影白名单加检索测试）；正文纯文本 React 转义渲染，本卡审计实测 XSS marker 不置位。

### D 动作、意图和异步界面

创建范围服务端权威（list_scope_source_versions 后 ActivitySpec 锁内 create_activity 再校验快照，来源替换映射 409 source_replaced）；409 activity_exists 前端只读核验（范围集合排序比对，一致才视为该意图实现，不一致如实报冲突）；缺配零写入（create_layer 失败关闭先于任何写）。意图台账：retrolume.pending-intents.v1，create 存规范化去重排序 source_ids，continue 存 operation_id/parent_operation_id/followup；无授权物与结果正文；先存成功再 POST；写入失败或损坏（loadIntents ok=false）阻止依赖恢复的新写动作而读取取消可用；清除提示"不撤回已提交或延迟到达的请求"；输入本地持久有占位说明可清除；改参数必须放弃原意图换新键。刷新仅挂载 GET；网络失败 status=0 → unconfirmed 且不重发；同键重试为显式动作；404 核对文案为"尚未发现持久迹象"不称"确定未发出"。继续仅限有效模型父（kind=model + committed_current + 活动未取消）；to_thread/shield 边界保持（service 主体未改）；监督与时间口径如实（supervision 对象回显）。并发同键至多一次业务出站由 batch3 屏障实测（1 行、单次发送、预扣恰 +1）。见 D2 轮询观察。

### E 证据覆盖与复用（C1—C12 映射）

C1 单 SQL 与投影一致：test_activity_workspace_reads（batch4 OK；单SQL计数、并发未提交写、来源有效性翻转、失效抑制、完整性门）。A 级（batch4 字节绑定见 G2）。
C2 新建与幂等：api 测试（409 一致/不一致两变体、source_not_ready、缺配关闭）+ batch2—4 create-via-http + batch4 浏览器 409 核验。A 级。
C3 取消与保守折叠：api cancel 幂等测试 + batch4 两步取消 + 本卡合成两步取消复验；杀树/退款语义沿 G3/D3 既有证据，本卡与 095 均未重跑（符合合同）。A+B。
C4 继续正常链：batch3 全绿（settled=6s、reserved=0、单次传输 roles=[assistant,user]、PG received+正文原子、requests/cost 各 +1、dispatch_closed、Job ERROR_FILE_NOT_FOUND 消失）；真实 launcher/SUP/worker/Job 链，替身仅 worker 传输边界（sitecustomize 只替换 _SuspendedSupervisor.create 的 SUP 进程目标与 HttpxModelTransport.send，真实 CreateProcessW/claim/关门/结算主体不变；socket 守卫仅回环）。A 级。
C5 同键竞争与 admit 前失败重试：batch3 屏障 race（rows=1、sends 唯一、预扣=3）、pre-admit-fail 0 行 supervision_unknown、显式同键重试成功。A 级。
C6 权限反例与认证提取兼容：离线 4 反例 403 + own-origin 200 + 坏 UUID/越界 400；test_materials/test_pdf_review/test_config 未改动（内容核验）；batch4 pdf-branch-reason + materials-upload-read。A 级（D1 偏差已单列）。
C7 敏感不暴露：错误体检索测试 + 投影字段检索测试 + batch4 浏览器目视 + 本卡审计截图。A 级。
C8 来源替换与范围修订：reads 失效样本 + continue 拒绝映射（source_invalid/integrity_error/activity_cancelled/result_kind_read_only）。A 级。
C9 断线/刷新/意图恢复：batch4 browser-workspace 全绿（banner、409 核验、显式同键重试、损坏台账闸门；旧字节）；最终字节刷新只 GET 见 G1（B+旧A）。部分 A。
C10 资料页不回归：batch4 materials 上传读取 + 坏 PDF 分支原因 + 既有测试未动。A 级。
C11 配置分层：config 12 例离线（模板不可启用、严格类型、越界失败关闭、服务不兼容、密钥变量名声明）+ capabilities 两态。A 级。
C12 分页与大小：reads 游标/越界 + api 坏游标 + 131072 转义多字节 HTTP 可读 + 本卡最终 bundle 实测。A 级。

复用与边界：G3/G4/D3/G5 未改区按合同仅 hash 绑定复用，未重跑；本卡审计同样未重跑（运行额度 0 于 PG/Docker/Windows 业务链）。

### F 尝试、资源与执行控制

从 runner 与原始输出重建（入口即计数）：批次入口 7 = ①guard 夹具误判（容器未触）②admin 角色名错误 abort（容器 1 启）③创建成功+迁移 001—008 全 rc=0+unittest 26 例 errors=10（1 启）④adopt 复用+failures=4 errors=5（1 启）⑤batch2（1 启，链缺陷 worker_failed_full_reservation）⑥batch3（1 启，全绿但 2 浏览器步骤失败）⑦batch4（1 启，api OK+workspace 全绿+continue 只读失败）。容器启动合计 6/6；每次启动前 inspect_guard 断言精确 CID e49d3acc…696a、镜像、命名卷、127.0.0.1:55441、1CPU/512MiB/pids128/no-restart/非特权/无 host bind；批末 stop 并核 Running=false/Pid=0（账本 container_after 逐项一致）。Windows 会话：batch2/3 各保守 7（SUP 启动上限口径）、实际 claim 窗口各 5；合计保守 14（上限 12 超 2）、claim 口径 10（限内）；账本 stop-decision 自记"超上限 1 次"与保守计数不完全吻合，属账本口径误差，如实登记不凑整。业务秒合计 173.720/3600、收尾 23.217/600。补录说明（16:15:17 correction）与输出文件吻合（preflight 文件被第④次覆盖为 1/1、create-role-db 与 migration 输出属第③次），矛盾已解释。凭据：口令 token_urlsafe(24) 经 stdin 内存，dsn.json 已由 finalize 删除（runtime 目录现存无此文件）；传输捕获仅含 sends 计数与消息角色，无凭据。修正轮次：根因两次有据修正后按卡停止实机运行并交回（post-batch-fixes + stop-decision），未以换编号继续；超限已按偏差登记，不因最终成功追认。本卡实时未操作 Docker/PG/Windows 业务链。

### 本卡实际操作与预算

构建一次：vite 8.3.0 从当前冻结源码构建至本卡 evidence/browser-check/dist-audit（3.1 秒，returncode=0），4 个产物 SHA-256 与正式 frontend/dist（2026-10-01 16:29:21 构建）完全一致（index-7xLKRnHC.js 70377b64…、index-PXrCNFBs.css e352c703…、pdf.worker 8ab0e5e3…、index.html 05807efc…），证明现有 dist 绑定最终源码、两处离线修复字节在案。浏览器专项一次批：进程内静态服务 127.0.0.1:18096（启动前核空闲、单进程含服务与浏览器驱动、收尾关闭并核端口释放）；首启因夹具 path 分隔符缺陷静态 404 失败（一次有据修正：path.relative 判定）；二启复验 s1—s6 全过（11 项检查 + 3 截图 + 请求日志），s7 夹具缺 materials/pdf-candidates 合成路由而中止；2 次启动额度用尽即停，记 not_run。业务累计约 47 秒（限 300）、构建 3.1 秒、离线准备并入同一预算（合计远在 300 内）；收尾核端口 FREE。外网/未知请求零（blocked 空，仅静态 404 一条属首启缺陷留证）。PG/Docker/Windows 业务/真实模型调用 0。产品与正式测试零写入；本卡仅写 DocuN/evidence/TASK-096/ 与 DocuN/results/TASK-096-result.md。

### 独立性与接触范围声明

本窗口为全新隔离会话，真实客户端 WorkBuddy（GLM-5.3-Flash），与 092/094/095 的 Claude 桌面 Code 窗口不同家族。审计判断全部基于源码、合同文本与原始输出；执行者账本补录仅作为导航线索并经原始文件交叉验证（O5、F 节两处如实标注其证据地位）。未读任何实现自评。

## 交回事项

待同步文档（由编排裁定后书写）：执行动态文档登记本审计结果与两项验收条件项（G1/G2）；架构动态文档如采纳 D1 修正或 O1/O2 改进另行登记；文档变更记录顺延。

合格经验候选：其一，Windows 下 Node/Python 混合夹具中 path.join 产物与字符串前缀比较因分隔符不一致恒假，路径归属判定应使用 path.relative；其二，Playwright route 合成取证须覆盖页面全部默认请求（含默认视图的 materials/pdf-candidates）后再断言"无额外请求"，否则夹具自身会污染计数。均已在本卡留证，是否入库由编排核证。

必须人工动作：无。建议下一步：编排按本报告裁定 G6 验收路径；如采纳 G2 强绑定，可另发一张只读 API 复验小卡（本卡不执行）；D1 是否恢复 materials 逐字等价由编排决定（低风险微调）。

本文件不代替主控最终裁定。
