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

