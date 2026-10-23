# TASK-121 / R-115 review-02 独立增量复核结果

F02、F03 关闭；F01、F04、F05 原关闭结论按原范围保留。当前有限工程切片的代码轴通过、定向证据轴充分，具备交主控作有限切片关闭裁定的条件；历史执行控制轴仍不通过，不能被本次技术关闭追认。Q 继续冻结，本窗不代填主控验收，不签 STEP018 整体、019、020、M-1、项目完成或发布。

最小夹具经用户明确批准，足以证明本次“Q 副本删除失败后 GET/重开不得报全部完成，原显式重试可以完成”的清理投影与恢复目标。它不证明正常请求装配、来源资格或合法外发；这些原有门与原审已接受证据各守其范围。

## 1. 合同、独立性与冻结身份

继续原 TASK-121 独立审计聊天，沿 TASK-121/R-115/review-02，只复核两项剩余边界、五个产品文件及直接影响。没有派子 Agent、接管工程或重跑业务。Codex desktop；A+ 为资源标签，精确后台模型变体 unknown。已读 task_model/V4.0、公共 AGENTS CHG-0003、阶段07规则按未变指纹复用；本卡需求v1.4、架构v1.59、执行动态v2.87。原采用07、08合同/permit和样本方法批准按本次输入复核，不自动采用后来规则。

首次有限读卡采时为2026-10-21 13:32:06 UTC（21:32:06 +08），准确人工接收时刻 unknown。原截止2026-10-22 00:51:52.291692+08及原投入不重置。断点时本轮尚无已写审计产物；本窗未启动业务进程，工程停止事实仅按原保存记录核对，没有现场探针。

[开场身份核对](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/review-02/identity-opening.json) 共750条引用校验，零不匹配；这是含重复引用的校验数，不是750个产品。当前冻结清单532条、注册当前文件18个、实际变化15项，其中产品恰为五个。独立核全部 preimage 摘要并重建真实增量，且逐段核 supplied source.diff / fixture-completed.diff 均可还原当前规范化行，见[差异还原](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/review-02/provided-diff-reconstruction.json)及[覆盖范围](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/review-02/scope-coverage.json)。

完成包1341581字节、147条目，SHA256 `15ec6b364ca9d16e2020a2c17640a655f5074bc9464f57a6747ac239e5e62ae4`；逐条目原字节均与当前文件一致，未递归重建旧包。[ZIP字节核对](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/review-02/zip-members-opening.json) 不解码工程报告、备份或同类条目。工程报告134777字节仅作 opaque bytes/hash，最新 budget/events、1006退出和停后核证从包外读取。

独立性披露：本轮未读取工程聊天、思考、实现记忆或工程报告正文；通用工作偏好检索不含工程实现。一次有限批读 command-1004.log 时旁见其一行保存/工程状态摘要（含 F02 PASS、F03 BLOCKED），没有据此判定。索引及工程 PASS/状态字段一律只用于定位，finalizer 脚本只取字节摘要。

原统一审计报告完整55795字节、SHA256 `75d40d166010d29b28065327a8a911a859200d6da01cac080ab13b72748da595` 原字节保留为本文件后缀，另存本轮 prior-result-original.md。原 audit/review-01、工程候选/证据/账、任务卡、输入根、DocuS和公共库均未改写。收尾身份及后缀证明另见本轮 identity-closing.json / result-save-proof.json。

## 2. F02 关闭：潜在 ADMIN 组合能力

[q_roles.py第36行](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/q_roles.py:36) 的 accessible 以 selected/effective 两种模式进行有界单调闭包：SET 只从可选择角色沿 SET 边传播，INHERIT 只在有效权限模式传播；可用 ADMIN 目标进一步作为可选择角色处理，并继续其 SET、INHERIT、ADMIN 关系。每个角色每模式只处理一次，环不递归放大；输入超过1024角色或4096成员边直接拒绝。INHERIT-only 不被自动当成 SET。原用途分层、真实权限查询、owner/definer、control/schema/database、管理属性和危险预定义角色检查继续保留，没有把无害成员关系全部拒绝。

最终文件SHA256 `fbc4534b899a40c1b5ce6d596c45e2b20d088e1ddfb1e3bd58ed703ab9dca30e`。本轮原 P1 的空权限桥 B→app SET、S→B ADMIN/no-SET/no-INHERIT 已进入潜在闭包，不能再只凭 B 当前空表权限放过。PG17 ADMIN/SET语义沿用前审已读的[GRANT官方规则](https://www.postgresql.org/docs/17/sql-grant.html)，没有新增外部研究。

根62的[原始组合记录](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/execution/audit-repair-08/F02-ADMIN-delegation-SET-combination-PASS.json)与[实际方法第12行](D:/shspic/project_NO3_RetroLume-agent/backend/tests/fixtures/task120/repair08_permissions.py:12)相符：main库 `retrolume_task120_audit07_main`、cluster system identifier `7697981369175429158`、backend PID33；single() 在制造图前确认没有其他 client backend，API/worker未运行。同连接显式 BEGIN，原快照登录主体 `task120_flow_snapshot` 当前 DELETE=false、SET-app=false，产品严格检查先拒绝 `data_role_capability_mismatch`。

随后真实 S 执行 `GRANT ...bridge1 TO retrolume_data_snapshot WITH INHERIT FALSE, SET TRUE`，记录 actor确为 `task120_flow_snapshot`，其 SET-app变true；实际 SET ROLE到 `retrolume_data_app` 后 DELETE=true。维护超级用户只制造事务内反例，未代做关键委派。finally ROLLBACK；完整35角色/21成员边及全部查询权限与 before完全一致，新连接再核原图、正常schema检查通过。事务中临时36角色/23成员边未COMMIT，没有改LOGIN/密码、持久授予或执行服务器程序。

离线实际共5个测试方法：4个角色算法方法覆盖原组合、多级ADMIN/环、合法无害ADMIN与INHERIT-only对照、容量拒绝，另1个投影方法。1000初始化超时、1001诊断失败照留；1001栈停在Windows asyncio fallback socketpair，1002保存日志列明5方法全部通过、exit0/tree_empty，wall0.984秒。不能称“5个角色图都在PG实跑”，也不能把一个PG反例提升为所有角色图的动态证明。前审已接受的旧11角色场景和两份正常快照拒写仍按原范围继承。[独立记录比较](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/review-02/F02-record-comparison.json)

## 3. F03 关闭：只读组合投影与权限边界

[MemoryService第15行](D:/shspic/project_NO3_RetroLume-agent/backend/app/memory/service.py:15) 的 read_command/read_snapshot 统一进入新 read_projected；[API第41行](D:/shspic/project_NO3_RetroLume-agent/backend/app/memory/api.py:41)及列表/详情均使用这两个固定服务端入口。原DB receipt/记忆头不改写：仅返回字典在对应Q副本未确认时增 `cleanup_status_unconfirmed=true`，把组合 `purge_state_now` 或 `purge_state` 投影为 pending；已提交revoke、原业务键、manifest、revision/version、007和预留保持。

[cleanup_projection.py第17行](D:/shspic/project_NO3_RetroLume-agent/backend/app/memory/cleanup_projection.py:17) 每次验证根、真实短journal锁和完整控制链，残尾明确报错；依赖索引缺失/形状不明、文件访问错误均失败关闭。匹配副本 cleanup不是done即pending；标记done但准确路径存在或重现仍pending，只有 lstat 明确 FileNotFound 才确认该路径缺席，不将权限不明当不存在。投影只读标识/元数据及文件状态，不打开Q正文、不执行cleanup、不append Q事件、不observe approval、不claim或外发。

原正常依赖建立方法 cleanup_dependencies 以当前snapshot refs为起点，纳入文档中的标识、活动所选历史版本及上游版本递归依赖；清理目标 q_snapshot_memory_cleanup_ids 反向覆盖本记忆及派生记忆，递归 UNION 有去重。投影拒绝无法确认集合或未包含自身的结果。正常明确无Q、或没有本对象Q依赖，返回实际DB状态；sealed data_readonly目标不拿旧源Q索引当目标副本，也不建立正常Q authority。原只读目标PG guard和source binding未改变。

真实锁序为 shared Q policy → PG读事务 → 短journal核对。取得policy前的初始journal核对已释放锁，没有持journal再等待policy。policy争用以非阻塞尝试、async短等待并限3秒，未持PG事务等待policy；POLICY在同一协程finally reset并关闭lease。当前三个入口及其依赖没有派出越过lease寿命的异步子任务。已有policy要求相同control_id，新标记为 `(control_id, True)`；原写方法仍先请求exclusive policy，QAuthority拒绝把shared升级，q_cleanup另要求精确 `(control_id, False)`。

[activities/repository.py第346行](D:/shspic/project_NO3_RetroLume-agent/backend/app/activities/repository.py:346) 只对服务端方法名分类为纯读的操作，在sealed或既有POLICY上下文中跳过 writable QAuthority初始化；客户端不能提交方法或POLICY标记。已核 read_memory_command/read_memory_snapshot/q_snapshot依赖的当前SQL为读操作，原 GuardedAsyncConnection、连接/事务、只读目标和写permit检查保持。它不是通用写权限；将来新增纯读方法仍须保持无写入、无逃逸子任务，不能把这个条件当任意回调的独占资格。

Q-enabled根先 regular核已有 `.q-policy.lock` 再使用现有 RootLease；缺锁直接失败，不由GET初始化丢失的正常Q存储或锁文件。有效根上的既有稳定锁句柄和identity检查沿用。离线投影方法保存了pending/新ControlHub读取、journal不变、读期间writer被拒与释放后可取锁、done、重现路径、sealed/no-Q及未知依赖/残尾拒绝。各动态/静态证据分别采纳，没有把模拟PG操作称实际PG竞争。

## 4. 获准最小夹具及真实故障—重开—重试链

[样本批准原件](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/execution/audit-repair-08/sample-method-user-adoption.json) 保留实际答复“允许这个最小清理夹具调整”，首次恢复采钟11:47:48 UTC、登记11:48:49.502316 UTC；实际人工接收时刻UNKNOWN，无延时窗或加次数。原三活动固定选择的记忆已于07撤销，现有接口不能把新memory自然改选进固定Q请求，不能要求本轮新建选择平台。

[实际夹具第64行](D:/shspic/project_NO3_RetroLume-agent/backend/tests/fixtures/task120/repair08_memory.py:64) 通过正常HTTP创建新memory；从真实artifact reader读取仍存在的合成样本，保留原request/payload/provenance字节，只以新 prepared/business/operation身份建立一条明确依赖新memory的清理副本，并立即revoke。该行没有已接受业务命令、approval或claim，不产生新的Q外发能力。这是合成的依赖/正文清理对象，不能冒充新memory已通过正常装配或来源资格。

其效力足以覆盖本次修正：后续调用真实ControlHub、真实PG和正式HTTP revoke/GET/purge，经产品准确依赖匹配、journal pending、实际文件删除及组合投影；没有把GET或重试结果stub为PASS。故障在准确文件删除边界一次性注入PermissionError，不伪造DB purge失败；若实现仍漏合并Q状态，三GET和页面刷新会立即暴露done，因此该样本与原残余缺陷有直接因果。正常Q装配、旧引用与worker保护继承review-01有效证据，未声称新增完整native负例。

| 已保存阶段 | 独立采纳的事实 |
|---|---|
| 根63故障 | memory `9b06bcbc-9d07-43ff-95cc-e9f4e0bd5745`，revoke键 `febeea5f-3d38-4336-ac75-968936cfd784`；DB实际revoked/revision2/purge_state=done/body_rows0，准确Q文件仍同identity/hash。POST及原键receipt/detail/list全为pending，三个GET期间writable QAuthority构造为0。 |
| 根63停止 | 下一API启动的可用内存520859648低于536870912，原batch/root FAIL保留；故障POST/三GET已先独立保存，不抹去也不把整根改为PASS。 |
| 根64新进程 | 真实API连接actor从PID37904变为PID12004；同库、同control `69fb59ce-9f51-4f84-acc3-e70bf8dfbaab`、同memory/revoke/manifest仍pending。复用进度，不再造memory或再次注入故障；512MiB启动门不降低。 |
| 浏览器重开/刷新 | 一个headless context/单页，未变正式dist。API重开页和reload两步都显示待清理与“明确重试原清单清理”，POST计数0。 |
| 显式retry及再刷新 | 点击后恰一POST `/api/memories/commands`，action=purge，沿原revoke及manifest；done、按钮消失，再reload仍done，累计POST1。随后新ControlHub回放确认done，不能称又启动第三API。 |

原始[故障POST/三GET](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/execution/audit-repair-08/F03-memory-failure-POST-and-three-GETs-PASS.json)、[新API重开](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/execution/audit-repair-08/F03-memory-API-reopen-pending-PASS.json)、[浏览器请求/步骤/资产记录](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/execution/audit-repair-08/F03-memory-browser-root-64.json)与本窗[独立比较](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/review-02/F03-record-comparison.json)对应。已直接查看保存的[pending截图](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/execution/audit-repair-08/memory08-page-reopened-pending.png)和[done截图](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/execution/audit-repair-08/memory08-page-reopened-done.png)，画面与步骤断言相符；截图没有替代请求/文件/PG证明。

正式浏览器实际加载JS `50b035784109bb04b444ffedf48186d14b9042a6139f8b22df59814d6a81b285`、CSS `6f02da29293bb8bf41825425f1d9d0c5da950ab02e77dfa4854ed195f49e8b94`，三次加载共6条网络摘要均独立匹配当前dist；无响应处理错误。artifact/operator拒读、reference=None只证明其实际调用层级，不称本轮新跑完整worker拒绝链。

原010函数在精确revoke/manifest核验并锁定记忆头后，先查同business_key或已effect-applied的purge slot，存在就返回原meta，早于DELETE/UPDATE分支。retry前DB已done/body_rows0，实际retry成功并返回相同memory/revoke/manifest/revision2/version1；结合未变SQL，可确认DB purge业务效果没有再执行。不能把新Q文件清理或新返回业务键表述为又做了一次DB正文删除。[010第372行](D:/shspic/project_NO3_RetroLume-agent/backend/migrations/010_learning_memory.sql:372)

## 5. 被测字节与继承范围

五产品最终SHA256依次为：q_roles `fbc4534b899a40c1b5ce6d596c45e2b20d088e1ddfb1e3bd58ed703ab9dca30e`；service `fd9a76597608fdc897f4be6914727c823407d2c49cba0d2009ac355568ef1962`；api `a1d0b69b86626429be37f73e12554dd7c291f501aa61bf5b5f34fcd8f867b4a9`；cleanup_projection `75a51e184a591053723b3d1f0bb988c8b588f41b8623ab6947893f42578c0bc9`；activities.repository `b0afbefe8ac0577548742fab07ca2c41a212c8e2d1b0d034b35aac2b7ac72282`。

根62/63/64各实际batch as-run清单均独立比较131个backend/app文件，另核43个frontend/src及4个dist，共每批178条产品/资源引用，全部与最终冻结字节相符。[被测字节比较](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/review-02/as-run-comparison.json) 分别保留夹具变化：根63 memory夹具为 `ae9c67…`，确切原件已留；根64只改闭合app周期回收、复用checkpoint、取消不必要第三API并改成page reload/fresh ControlHub，故障及三GET成功段未改，未改产品或门槛。

根64浏览器脚本 `e26ee14dc0630d24f07c65275be1f5e548a24b298d319d841dae266ea47d8490`，由已存根63脚本两处literal修改可逐字节重建，并与asrun-root064副本完全相同。其额外摘要在停后登记，不能倒填为执行前已发出的JS摘要；实际网络dist摘要是另一类同时保存的证据。1002离线有实际方法/log和后来checkpoint，没有虚构该命令同时发出全部产品hash的回执；根62—64真实产品清单与静态闭包审查提供本轮冻结绑定。

F01迁移/codec、F04时钟、F05命令消费投影、F03源删除私有cleanup attempt，以及原三ACK、99→100、正常入口、有限UI、K2和DataContext迟到切换结论均按前审边界继承。本轮未重审原55项或完整矩阵，也未重跑旧成功样本。未知真实Q官方/账户/readiness、首次启用及72h起点仍是后续原有门。

## 6. 金融、清理、唯一账与停止

F03前后完整operations、007 payload hashes、prepared/artifact hashes及financials逐值相等，无关文件摘要由真实fixture逐项核相等；清理副本的准确文件最终缺席。main仍5次合成准入/1250000 microunits，三个活动1/2/2及五个007 received，R/tool0继承；本轮admit/approve/claim/dispatch增0。r02与旧实例只继承各自时点，未重新赋余额。

只新增删除一个6661字节Q正文文件 `q-prepared-bf4cceed-83da-4cfa-9369-2e0db123b972.bin`，volume `1031070048549017791`、file_id `1125899907308760`、SHA256 `bdd3919cb57868f29a4550ce4a78ba7f42a6a6bac01787a1ce93ab13a6439f5f`；准确清单在获批新根下，不与原6份重叠，累计7/16，未删旧根/历史证据、事件或金融事实。本窗没有访问该.runtime实物或凭据，只审保存清单/方法/前后记录。

唯一最新账计数为root64/64、PG64/64、API65/96、Browser15/16、build5/8、Native69/128、HTTP1572/10000；容器/卷创建及对象2/2，preview/provider/实际费用/Git0。新增四根、三次PG、两API、一Browser、52HTTP，无新库/LOGIN/密码、恢复目标未启动。原60根/141失败与原events字节前缀完整保留。根61采样路径失败、1000/1001和根63失败等原记录不清零；完成包保存失败数148，最新唯一账149的最后一条是停后元数据误读已记录缺席的旧JS导致FileNotFoundError，修正为hash/null比较后通过，不是第149个产品缺陷或业务运行。

wall独立按原观察区间重建：旧上界64525.559426 +（10:51:48至12:12:18.858684 UTC连续观察4830.858684秒 +1秒采钟边界）=69357.418110/72000。新增测量command/runtime合计201.561 +08未包裹保守区间4630.297684，恰覆盖4831.858684一次；保留旧post-save60和所有unknown预留。包保存69322.102513含1006预留60，1006实际2.187；后续观察另前向入账，不能仅扣预留算最终。holding2943.704295/21600，新增58.219等于四根0+11.906+16.532+29.781。等待答复纳入保守观察上界，不冒称CPU、人类总投入或精确接收时间。[wall还原](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/review-02/wall-reconstruction.json)

1005于2026-10-21T12:01:58.174181Z保存停止证据。从sole roots、08追加事件、1000—1004退出回执和memory samples独立重建的28组PID/birth与记录集合完全一致，28组这次均为明确exited；8个准确Job全部absent、无unknown/unresolved。两精确CID `b8952207…`、`4eb5be54…` 均stopped/Pid0，55480/55481/18120无监听；1005自身及后续1006均另有exit0/tree_empty回执。后续仅保存/只读核证，记录中无业务重启。[停止名单还原](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/review-02/stop-registration-reconstruction.json)

旧079中20条unknown继续使用review-01已接受的19条精确历史退出+root22精确Job替代组合，不把旧unknown改成当次fresh；旧摘要缺陷O01及注释O02保留。这里仅核原停止时点，不代表今日即时全机状态，没有运行Docker/端口/进程探针。原20:29:21+08业务、20:59:21+08保存清场门及96h未延长，记录均在原界内；root/PG次数已尽，其他余量不能恢复运行。

## 7. 三轴裁定、观察与审计停止

| 轴/事项 | 本轮结论 |
|---|---|
| F02/F03确定残余缺陷 | 两项关闭，本轮有限范围未发现新增阻断确定缺陷。 |
| 当前有限代码轴 | 通过，五个产品增量及直接权限/读写/兼容调用链已覆盖。 |
| 定向证据轴 | 充分；最小夹具只证明清理投影与恢复，正常Q链按前审范围继承。 |
| 历史执行控制轴 | 不通过。05/06旧时序及07/08登记前有限读取披露、unknown/预留均留账，不用技术关闭追认。 |
| 条件限制/非阻断观察 | unknown必须失败关闭；纯读分类与协程lease不可被未来写方法借用；1000/1001、61/63失败及停后149元数据错误照留；JS停后摘要不冒充事前摘要。 |
| 交主控终点 | 具备当前有限工程切片的关闭裁定条件；主控须按原职责保留并处理历史控制记录，不由本窗代签。Q、整STEP及项目/发布门不放行。 |

本轮保存记录比较106项通过，另独立验证wall区间、停止注册集合及包身份；没有为更放心扩大运行。工具只执行自写stdlib hash/diff/ZIP/保存记录比较和有限文件读取/保存，查看两张既有截图；compile/unittest/产品测试import/PG/Docker/API/Job/Browser/build/模型/业务网络/Git全部0。先前已读官方6页全部复用，新增页0。

审计工具累计保守已用1459.2202126秒及旧unknown预留全留；本轮实际shell逐条回执见command-log.json，另留600秒覆盖未独立精确计量的采钟、图像读取、patch和functions包装等元数据开销，不记为实测CPU。新增保守计费在1200秒内、累计在3600秒内；精确全工具wall、人类投入、模型token均unknown，以session-receipt.json记本轮最终数和截止核验。收尾只核本轮报告保存、冻结输入及原55795字节后缀；完成这两风险覆盖即停止。

[本轮结构化结论](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/review-02/findings.json) · [保存记录比较](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/review-02/record-checks.json) · [控制核对](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/review-02/control-record-comparison.json) · [最终审计回执](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/review-02/session-receipt.json)

---

