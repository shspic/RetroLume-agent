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


# TASK-121 / R-115 review-01 独立增量复核结果

review-01 尚不具备交主控关闭条件：F01、F04、F05 关闭，F02、F03 各保留一项 P1；代码轴不通过，证据轴证据不足，历史执行控制轴不通过，Q 继续冻结。

本轮一次合并复核五项修正及直接影响，没有重启完整审计或业务验证。新增两项未封闭边界分别为 ADMIN 经中间角色扩大 SET 能力，以及记忆 Q 副本清理失败后的 GET/重开投影遗漏。它们是合同与冻结代码可达路径的静态确定缺陷；本窗没有运行动态复现，也不声称实际测试实例曾发生越权、正文外泄或该记忆故障。

## 1. 独立性、冻结及阅读范围

继续原 TASK-121 审计聊天，未接收工程聊天、思考或实现自评，未派子 Agent。客户端为 Codex desktop；系统声明家族 GPT-6，精确后台变体 unknown，A+ 只表示资源路由。沿原审披露宿主提供的通用规划偏好及 MEMORY.md 检索，本轮没有读取工程实现记忆，没有用通用偏好降低审计门槛。

按本卡、原采用07合同、许可、采用回执及绑定提案补读；task_model、V4.0、公共 AGENTS CHG-0003、阶段07不变，卡面需求v1.4、架构v1.57、执行动态v2.85。七规则指纹再次匹配，未变已读正文复用，没有加载另一版本或主控候选评价段。

本轮 [identity-opening.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/review-01/identity-opening.json) 独立复算606条引用，零非预期漂移。606含重复引用，不是606个产品；原清单269个去重当前文件、31个注册文件及249份工程原件按各自范围核对。全部15产品增量及30项实际变化的真实差异、必要调用者和定向方法已审，见 [diff-index.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/review-01/diff-index.json) 与 [scope-coverage.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/review-01/scope-coverage.json)。

候选 final-review-candidate.zip 为1132289字节、275条目，SHA256 0196dd9686f5cc266ff390615b34e8a5b40c93513b43ea8349e50cce11de10e7。逐条目只取原始字节摘要，未解码工程报告或自评条目；TASK-120-result.md及work-decision同样未解码。唯一最新budget/events与999回执从包外读取，没有用包内保存前的账代替最新账。

原首审结果33054字节、SHA256 c4c30439cd6a2d7b63b12254a76550013ae8da93b50c9cf2d6836451588314d8，完整原字节作为本文件后缀保留，另在本轮目录保存原件。原audit证据、本卡、输入根、产品、测试、dist、工程账、公共库及DocuS均未修改。收尾重新核验输入及原后缀，见本轮identity-closing.json和result-save-proof.json。

## 2. F01 关闭：必需权限和两种精确迁移身份

最终015 SHA256为874d2a173f401ce923680d184eb5687c121fd70831d8b86cd9b6740a7c330915。[015第17行](D:/shspic/project_NO3_RetroLume-agent/backend/migrations/015_activity_scope_delete_permission.sql:17) 已分别要求SELECT、INSERT、UPDATE；DELETE/TRUNCATE的逗号列表继续用于发现任一多权。锁内前提与同事务保持，正常有行R02的CHECK转换改为NOT VALID、UPDATE、VALIDATE后才COMMIT。

三个真实负例来自根52，实际权限分别为真/假/真、真/真/假、真/假/假，均为P0001及scope_delete_migration_requires_exact_quiescent_r02。前后ACL、constraint、control和对象镜像完全相同，新连接再核相同。它们运行的是首修订SQL 1fbe278e19bd65f55d043159167e108563adcde8dae870a0bcf060b2f9c0a712；本窗按字节证明其GRANT之前的全部前提与最终SQL完全一致，并按hash精确重建根52的schema_profiles。没有将三个负例冒称最终整文件实跑。

根52正常样本23514保留；根54在真实R02 control行存在时执行最终SQL并成功COMMIT至R03，严格schema核验成功。首修订失败版本没有进入兼容白名单。上述绑定见 [migration-as-run-reconciliation.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/review-01/migration-as-run-reconciliation.json)。

[schema_profiles.get_read_profile](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/schema_profiles.py:51) 对完整迁移字典作精确相等检查，只认当前874d…和历史59b2…两种R03 codec；PackageReader仍检查完整codec对象及包身份。历史codec保持旧hash，初始化/恢复目标的migration_chain只取当前015。未知hash拒绝codec_mismatch；原06真实PG备份经真实reader只读打开，原包摘要不变。001—014、R01/R02冻结常量及未变恢复主体继承。

本结论不表示旧已应用库重过新前提，也不表示本轮新做了完整PG restore。保存的旧包读取、空业务codec正反例、最终正常安装与未变恢复调用链足以关闭本项精确修正，不要求再造整套恢复或重刷金融样本。

## 3. F02 不关闭 / P1：ADMIN目标的后续SET闭包漏核

位置为 [q_roles.py第43行](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/q_roles.py:43) 的accessible，以及[第76行](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/q_roles.py:76)的ADMIN边判断，当前文件SHA256为78a062ad19c9a917ff3c7991427c28a4b15ee3c7f9708e0c1d304905d1b9ad39。

新实现正确分开session用户的SET链与各可选角色的INHERIT链，核真实表/control/schema/database权限、owner/definer、管理属性及列明预定义角色；并在严格形状/ACL投影前执行。根54原八例、根57新增管理负例与合法/快照对照的有效事实保留。13份F02记录包括11个角色图场景及两份正常快照拒写记录，不能合称13个新负例。实际单连接、同集群、事务内制造、finally回滚、新连接核原图的方法及原图已核；没有把新数据库当角色隔离，也没有执行服务器程序。

仍可接受下列不合格配置。S表示原真实快照登录角色，保存原图已有S→retrolume_data_snapshot的INHERIT TRUE、SET TRUE关系。B为没有表/control/schema/database/owner权限的NOLOGIN中间角色：

1. B→retrolume_data_app为INHERIT FALSE、SET TRUE。
2. S→B为ADMIN TRUE、INHERIT FALSE、SET FALSE。
3. 其他角色属性和直接ACL保持正常。

这是未执行的静态触发配置。S的当前selected/effective中没有B；第78行只看B当前实际权限、属性及owning事实，均无危险。B因不是受信组、owner或可达受信组的登录主体，在第59行被跳过。检查从未计算“ADMIN目标B可SET到app”的能力，所以该配置可以通过。

S已经持有B的ADMIN，无需超级用户或CREATEROLE，便可把B以SET TRUE授予现有retrolume_data_snapshot；此后S的SET链到snapshot→B→app，得到normal app DELETE。PostgreSQL17明确允许ADMIN成员继续授予成员关系及修改成员选项，SET只要求路径各边SET TRUE。[PG17 GRANT规则](https://www.postgresql.org/docs/17/sql-grant.html)

这不是声称当前测试库有该坏图，而是合同要求拒绝的组合能力未被校验。原“ADMIN直接指向app”负例和“SET桥直接可达”负例分别通过，不覆盖两者组合；已有实际桥角色的空当前权限与真实S成员边也支持上述配置条件。

最小修正为把ADMIN可授予后的有界SET/INHERIT及继续ADMIN能力纳入用途检查，保留真正无害关系；不能只把所有membership一律拒绝。最小补证为一个合成事务内组合反例、一个合法图对照、实际能力观察及精确回滚/新连接核图。不重跑全部角色例，不执行服务器程序。详细触发保存在 [findings.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/review-01/findings.json)。

## 4. F03 不关闭 / P1：记忆清理失败后的只读回执丢失Q待清理状态

准备时新增依赖索引，覆盖当前资料、请求/历史中的身份和所选记忆的传递依赖；删除/revoke/purge先持Q独占policy，再走原MutationGate/PG及文件路径。q.cleanup_pending先落日志，artifact/operator/reference/worker入口均拒绝已清理或待清理正文，物理清理只处理准确pid文件，不扫描目录。

q_cleanup核根、regular file、链接数、文件身份、大小和摘要；Windows目录句柄不共享DELETE，子文件句柄拒写/替换，按打开句柄删除并确认路径缺席。替换或不明身份失败关闭；完成后若路径重建也不以旧完成记录误删。原摘要、事件、007和费用不删除。原始记录中的六个准确新造文件在批准根与16份上限内。

根58的正常memory revoke+purge确实使数据库body_rows=0、三个Q副本缺席，artifact/operator/reference与真实gateway检查拒绝，operations、007摘要、prepared摘要和金融前后相同。源删除的准确文件失败先产生deleted_pending；原根58稍后的Origin 403属于夹具，原FAIL保留，不改成整根通过。根59核既成子事实，源content准确404、无关源200、旧继续result_invalidated及零金融变化有效。gateway负例只是在admission前进入真实授权检查，未声称新native负例。

跨进程重开首次失败operation_authority_unknown属于实际恢复缺陷；最终新增_CleanupAttempt的直接高风险增量已经单独审查。它不恢复原Operation执行票据，不能admit新墓碑；只有source_delete、原source_tombstone_commit票据、待清理job才可建立新actor/deadline。PG在MutationGate和原references锁内回读同source/business/impact及expected_revision+1墓碑，核当前dataset/instance/normal，再允许准确清理。最新尝试、revision、时钟域、有限deadline及原execution原字节均受检；旧actor失效，完成不能重复写，GET只认完成见证。根60最终产品/夹具字节下的真实HTTP重开retry成功，以及078本地journal负例可采纳；它属于原批准“幂等重试和断点恢复”的必要范围，没有扩成通用旧票据恢复或Q授权。源路线因此具备限定关闭证据。

尚未关闭的是记忆故障的读回路线。[memory/service.py第47行](D:/shspic/project_NO3_RetroLume-agent/backend/app/memory/service.py:47) 在DB purge已COMMIT而Q文件删除失败时，只改当前POST返回字典为cleanup_status_unconfirmed=true、purge_state_now=pending。这两个值没有进入数据库完成事实，也没有被GET合并。

下一次[GET命令收据](D:/shspic/project_NO3_RetroLume-agent/backend/app/memory/api.py:37)直接调用ledger.read_memory_command；[_memory_receipt第309行](D:/shspic/project_NO3_RetroLume-agent/backend/app/memory/repository.py:309)只读learning_memories.purge_state，因此会返回done并省略Q未确认状态。重开视图同样读取DB purge_state；[MemoryWorkspace第271行](D:/shspic/project_NO3_RetroLume-agent/frontend/src/activities/MemoryWorkspace.tsx:271)显示正文已清理，并在done时隐藏既有“明确重试原清单清理”。

具体触发为正常记忆revoke/purge已删DB正文，精确Q prepared文件因权限或共享句柄删除失败。pending日志仍会关闭其正文读取和外发，这部分保护有效；但该明文文件还在，GET/重开却能把组合清理显示为完成，且普通重试入口消失，违反清理不确认不得表现全部完成的合同。没有声称当前成功样本发生此故障或已泄露正文。

最小修正为将DB清理事实与依赖匹配的Q cleanup状态统一投影到GET收据和重开视图，pending/unknown不得显示组合done，保留既有显式重试。不要回写或撤销已COMMIT的DB purge事实。只补一次新合成memory文件操作失败→同键GET/重开→明确retry成功，核副本、007/原费用和无关对象；原成功memory与整套旧K2竞态不重跑。

三条已保存清理路线的真实前后对照见 [evidence-comparison.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/review-01/evidence-comparison.json)。原根35缺即时before金融快照的限制仍保留，没有补写旧件。

## 5. F04 关闭：联合时钟和不可逆失效

[q_clock.domain/validate](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/q_clock.py:17) 将Windows boot GUID与实际monotonic实现绑定。签发记录issued上下界及固定deadline；900秒单调期限不能后移。UTC已见回退/过期、单调超期、域变化或未知均拒绝；ControlHub在真日志锁内采样、核当前批准ID，并先追加不可逆失效见证。后续同一旧批准不能靠回拨、重开或另一进程恢复。

projection、reference、check_reference及worker仍使用同一批准有效性路径；旧无充分证书批准失败关闭，显式新决定须当前资格一致且未被领取。DecisionBody的私有clock进入批准ID，不进入provider payload或公开业务wire；旧无clock的ID算法用exclude_none保留旧字节语义。没有改金融SQL或执行窗口90秒来冒充批准期限。

七场景调用真实QAuthority、ControlHub、文件和锁，只注入q_clock.sample：含未投影但单调已经超过15分钟后UTC回退、已见过期再回退、观察回退不可逆、域不明/变化、同域重开、合法继续及claim后零重发。旧无证书的validate分支另有直接断言；不冒称曾动态消费整套历史旧批准。

根55真实API/operator批准、显式原键继续、native/SUP/PG received组合使用同一+2秒依赖注入，记录当时API19508及worker16444的同域样本，恰一次生产准入，从0/0至1/250000。公共响应payload_sha256为null，未拿它充007摘要；后续真实PG的007摘要及原预留由清理witness继续核保留。其后增加的source_delete完成见证不改变本路径。

Python3.12的Windows参考实现使用GetTickCount64，不能凭文件开头的QPC注释推断实现；最终代码同时接受GetTickCount64并把实现名纳入域，实际正向原采样也成立。[Python3.12时间语义](https://docs.python.org/3.12/library/time.html#time.monotonic)、[CPython3.12参考实现](https://raw.githubusercontent.com/python/cpython/v3.12.10/Python/pytime.c)

1秒为UTC取样/漂移容差，和900秒硬期限分开；本结论不承诺识别任意小的未观察回拨。未调整主机或DB时间，也不授真实provider、账户或价格readiness。

## 6. F05 关闭：PG已领取与合法worker分离

[q_snapshot_command_fact](D:/shspic/project_NO3_RetroLume-agent/backend/app/capabilities/q_context.py:389) 单独读取PG status、launch_claimed及终态事实，普通命令缺行/错误失败关闭。operator在Q独占policy内读取并批准；claim_approved持相同policy完成最后检查及原PG launch callback。真正worker仍用原冻结snapshot/reference；可变领取状态没有粗暴加入冻结snapshot全等。legacy learning在首次admission前本来没有PG accepted命令，缺行作为未消费的特例与其私有launch witness对应，不扩大给普通命令。

根57真实claim_interview_launch已COMMIT后才注入ACK丢失；原键18aa9c03-c255-4fd9-a3a1-8d7f6ab37ad8为started、launch_claimed=true，Q claim和007均无，完整冻结snapshot不变。两次GET均consumed/can_continue=false；立即和+901秒operator均q_approval_consumed；重复POST两次，批准事件、worker dispatch和金融均无增加，维持3/750000。原未领取合法组合由F04正例提供。不是仅凭原业务拒绝重复launch来判operator已修。

## 7. as-run、继承与证据限制

独立重算各实际批次文件摘要，见 [as-run-comparison.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/review-01/as-run-comparison.json)。根54 q_roles原件与其原hash相符；到最终只增加control/schema/database及预定义管理拒绝，旧用途/图逻辑按实际差异继承，新增分支由根57原记录支持。根59 control/deletions原件同样精确匹配，后续只增加清理attempt及完成见证；根60最终产品与夹具摘要一致。根52schema_profiles按第一修订015字面量精确重建，未执行重建文件。

部分更早fixture全文未收存，保留其原hash、trace和实际case层级，不伪造为当前文件。根55的合法组合、根57PG领取及根58子事实不因为整根稍后FAIL就被抹除，也不因为根60最终零差异就冒称那些路径全部在最终整文件重跑。F03新attempt用根60/078直接补证；F04/F05授权主体字节未变，后加source_delete见证的传导已静态分离。

C01三ACK和原007、C02十一全请求反例、C03旧wire、C05冻结、C08检索、C09练习、C10有限五入口、C12真实PG共同100门及C13完整DataContext/namespace/只读列表中未受改变部分直接继承。C11只补审新增清理的policy→MutationGate→PG锁序和完成见证，原K2事实不重做。C04/C15因F02/F03仍不能关闭；C06按07精确两库资源核定；C07的PG误投影已修；C14按下一节组合证据限定。未重刷99笔、三ACK、正常五入口、浏览器或build。

## 8. 工程控制、停止和非阻断观察

[control-reconstruction.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/review-01/control-reconstruction.json) 复算唯一5608条events，原5121条前缀原字节、原51根及原125失败前缀完全保持。累计141条失败是记录数，不是141个独立缺陷；TASK117原81条另留。新根52—60的入口均在07实际登记之后，采用当期cap；所有新根elapsed最大92.422秒，9根均保存准确清理确认。

累计roots60/64、PGstarts61/64、API63/96、Browser14/16、build5/8、Native69/128、HTTP1520/10000，容器/卷及创建尝试仍2/2。新增各一次create的两逻辑库为retrolume_task120_audit07_r02/OID24351、retrolume_task120_audit07_main/OID25874，两个NOLOGIN桥只在负例事务内；无新增登录、密码调整、服务器程序执行或目标启动。源CID b89522070d4b64fc67efed810852ccc21948058f154bf4fa1889f4d8d69a102f及原镜像/卷、1CPU/512MiB/pids128/restart=no、loopback55480/API18120保持。恢复CID 4eb5be54b713e5412be702e27684d98d2b7de92a77f9085b3ce84a5f4b124332保持停止。

wall逐字段合计64525.559426/72000；64583.418426是含999最多60秒预留的包内时点，真实999=2.141替换后差57.859秒。另一个post-save只读60秒预留和所有旧unknown原样保留，没有再扣一次。持有2885.485295/21600，新增218.407。不能把这些保守投入当CPU或人工实测。

07原adoption明确两批只读工具早于持久登记，精确人工接收unknown；采用签发时刻保守门，业务截止12:29:21.021710Z、收尾12:59:21.021710Z，未延长原96h。已保存业务/999结束都在保守门内；两批先读的登记限制与05/06历史控制不通过保留，不追认为首工具前已登记，不用本轮技术子项通过洗掉。

金融按实例分账。新r02为0/0，新main为5/1250000，等于1次model及4次embedding合成准入，低于两库合计16。新增synthetic transport亦5次，三个活动分别1/2/2，R与工具预留均0。旧四库、06源及恢复副本仅继承原时点事实，没有本轮再查或相加给新额度。八个新批准已明确revoke，只适用本轮对象；旧UNKNOWN、原预留、007和冻结事件不重发/不退款。

079在2026-10-21 16:14:39.838517+08:00保存705组PID/birth、153 Job、两CID stopped/Pid0及55480/55481/18120无监听；079/080/999回执exit0/tree_empty，080/999为文件收存，没有后续业务再起记录。本窗没有启动Docker、进程、Job或端口探针。

O01为非阻断的证据汇总缺陷：final-stop-check.py第55/78行把state=unknown/error5也导出same_identity_running=false，从而声称all_fresh。原079有20组这种记录，不能当20次新确认退出。原首审对该总汇总采用得过宽，本轮纠正证据解释，旧报告正文不改。

本轮按准确PID/birth复用早期原件，19组已有明确exited原观察，见 [stop-history-resolution.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/review-01/stop-history-resolution.json)。剩余18452/birth134368818656922573在根22实际NamedJob成员中被观察27次，原准确Job tree_empty，079同名Job absent；独立证据见 [stop-root22-job-resolution.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/review-01/stop-root22-job-resolution.json)。这些退出后的原进程身份不能随PID复用复活。组合证据足以支持列明对象停止，不能把组合结论改写为所有维度均新鲜实测；无需再探这20个旧PID。以后汇总应保留unknown，或显式引用这样的替代证明。

O02为q_clock开头QPC注释不准确，实际代码和保存的GetTickCount64正向证据正确，不阻断F04。

## 9. 本窗投入、终点与最小后续

本轮首次采钟为2026-10-21 16:54:33+08:00，精确人工接收秒值unknown，按更早许可签发16:51:52.291692+08:00取8小时保守截止2026-10-22 00:51:52.291692+08:00。首轮769.9025901秒保守工具投入及unknown预留全保留，原8小时未追认延长；本轮单独增量与累计3600秒上限分账，见本轮command-log.json和session-receipt.json。中途“继续”未清零或另开时间。

本窗运行compile、unittest、产品/测试导入、PG、Docker、API、Job、浏览器、build、模型/业务网络、Git全部0，未读.runtime、凭据、vault或真实配置。仅执行自己的stdlib hash/diff/ZIP与已存记录对照。有限元数据检索的不存在路径、一次FileNotFoundError和输出截断均记账，没有触发产品复跑。人工思考/阅读实际耗时与模型token为unknown。

原官方页2/6沿用；本轮新增PG17 GRANT、Python3.12时间文档、CPython源文件的GitHub页及其raw表示，按两种表示各算一页，累计6/6。没有扩网调研、安装或下载依赖。

最小下一步由主控一次合并交原TASK120工程窗口：只修F02组合ADMIN闭包及F03记忆失败后的统一只读/重开清理投影，按上文两个最小场景补证，再回本TASK121同窗增量复核。F01/F04/F05及未受影响的C12、ACK、UI、K2等不重跑；本审计没有自动建立新的运行预算或修改共享状态。

真实Q仍待原合同所留官方/账户/计价与币种税、token/framing/reasoning上界、严格返回身份、正常secret loader非敏感readiness、实际新normal实例及固定roster、剩余Must矩阵、独审缺陷关闭和主控首次启用回执。T0/72h未建立；不签STEP018整体、019/020、M-1、项目或发布。

以下为原首审结果的完整原字节后缀；当前裁定以本review-01为准。

---



# TASK-121 / R-115 集中独立终审结果

TASK-120 当前有限工程切片不具备交主控关闭条件；代码轴不通过，证据轴证据不足，执行控制轴不通过，四项 P1 和一项 P2 合并交原 TASK-120 工程窗口处理，Q 继续冻结。

本报告是 TASK-121 的独立审计建议，不代填主控验收。P1 为 F01 迁移前提漏验权限、F02 严格 ACL 未核实际成员能力、F03 Q 正文副本未接入删除清理、F04 批准期限可随 UTC 回退恢复；P2 为 F05 PG 已领取但尚无 Q claim 时批准投影及续批仍可能开放。F01—F05 是本报告内部定位号，不占用共享 DEF、TASK、R 或 CHG 编号。

现有 ACK、真实 PG 共同 100 门、列明正常业务及 UI、K2 窗口、严格包读取和最终停止的有效子事实保留。没有要求重新刷 99 笔、重跑五入口、真实供应商或整套业务验证。以下确定缺陷来自合同与当前实现的静态可达路径；本审计没有运行它们的动态复现，也没有将静态判断写成真实事故。

## 1. 独立性、规则和授权

本窗为用户人工转入 TASK-121 的 Codex desktop 审计聊天，与 TASK-120 工程聊天分离；未继承工程聊天、思考或完整自评，没有派发子 Agent、创建并行审计或接管工程实现。系统声明的模型家族为 GPT-6，精确后台型号或变体未暴露；A+ 仅登记为资源路由，不声称来自另一个模型家族，也不声称延续了原 TASK-118 的物理执行上下文。

实际读取项目根 AGENTS.md、锁定公共 AGENTS.MD、WORK.MD 适用内容、07 提示词及完整 TASK-121；七项文件与 rules-snapshot.json 的指纹均匹配，未自动采用新版。00、05、06 和任务模板仅核锁定身份，没有将它们冒称为本轮已全文加载。合同身份为 task_model、V4.0、公共 AGENTS CHG-0003、阶段 07，卡面需求 v1.4、架构 v1.54、执行动态 v2.82。本审计不承担共享状态维护，未解码执行动态中主控收到候选的评价段。

读取顺序为规则与审计合同、封存身份、TASK-120 原合同和前向采用合同、TASK-119 有效设计及 K1/K2、真实差异和实现、方法及原始记录。TASK-118 只读取四项关闭、有限 S、历史控制与 Q 边界的适用段，不重做未变七族。

TASK-120-result.md 只作为 opaque bytes 核对，91351 字节，SHA256 为 3d044a788f7354e9a3b1fec0f75bab100f182469dea42613d3112078cda67b03。未解码该报告、其 ZIP 条目、TASK-120-work-decision.md 或对应备份正文。允许读取的 acceptance-matrix、scope-index、budget 和 checkpoint 中确有工程 PASS、自评字段，本轮只用作导航，未据此预填结论。

宿主提供了通用规划偏好摘要，首批工具还检索过 MEMORY.md 的规划验证边界；没有接触 TASK-117/120 的实现记忆或工程推理。该偏好未用于降低本卡安全、证据或独审门槛。没有隐瞒这次通用记忆接触，也不声称完全未接触任何宿主记忆。

产品、测试、dist、工程原证据、工程账、任务卡、公共库、DocuS 均未修改。未读 .runtime、真实配置、凭据或 vault；compile、unittest、产品/测试导入、PG、Docker、API、Job、浏览器、build、模型、业务网络和 Git 写入均为 0。仅执行自己的标准库文件 hash、ZIP 条目、差异和已保存记录对照。官方资料查询限于两页 PostgreSQL 17 文档，适用版本由实际 fixture 的 pg_major=17 确认。

## 2. 对象、差异和可复核证据

审计起点和收尾的身份核对分别见 [identity-check-opening.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/identity-check-opening.json) 与 [identity-check-closing.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/identity-check-closing.json)。322 项核对包含重复引用，不是 322 个不同对象；209 项冻结清单、55 项净变化的额外实际产品路径、六段 diff、两份 as-run、规则、dist、工程账及附件均无非预期漂移。两个旧 JS 的期望摘要就是 null，实际不存在，按预期缺席处理。

初始 product-baseline 有 616 项，复算其中 47 项发生变化，45 项属于列明产品净变化，另两项为旧 dist JS 移除及 index.html 更新；没有发现该清单内未纳入范围的额外产品差异。55 项中，45 项取得与初始 hash 精确相符的 preimage；必要时使用后轮实际保存且摘要等于初始摘要的原件，没有拿不相等的后版补初始基线。其余 10 项初始清单未列且无初始原件，已审当前完整内容，但不凭 null 声称独立证明了新建。

完整文件列表、preimage 来源和逐文件净差异见 [net-diff-index.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/net-diff-index.json) 及 [baseline-closure.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/baseline-closure.json)。实际覆盖包括全部 Q 新模块、业务 accept/claim/GET/请求组装的净差异、网关和最低 transport、原费用事务调用、新权限/profile/备份恢复直接依赖、全部前端净变化及配置说明。测试和 runner 按真实证明方法定向读取，不宣称全部 38 份 fixture 都全文审过。

.gitignore 除本卡精确私有目录外，还包含独立 GitHub 同步形成的排除规则；其 2026-10-18 明确公开同步授权保存在 DocuN/evidence/github-sync-20261018/explicit-publication-authorization.json。没有把该独立工作区变化算成 TASK-120 已执行 Git 写，也没有回滚它。

候选 ZIP 为 1936840 字节、286 条目，SHA256 为 3e96aeee40b35e0e0e1a4d42e82452b3cc2a0286fe1ce3ae4bf24219211bed69，目录和逐条目身份见 [candidate-zip-members.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/candidate-zip-members.json)。条目只读原始字节取摘要，未解码工程报告。没有重建或递归打包旧七 ZIP，最新 budget/events 和 071 回执按包外附件审查。

最终 015 的 SHA256 为 59b2e556a81a5383e9144a967fa90b5abedb26284d50cbf150db1dd77f34ef0e；正式 JS 为 frontend/dist/assets/index-GSKO5ska.js，SHA256 为 50b035784109bb04b444ffedf48186d14b9042a6139f8b22df59814d6a81b285。四资产以冻结清单核对，实际 JS/CSS 响应摘要另从浏览器原记录复算匹配，不用磁盘声明代替真实加载。

根 46 与最终产品仅 repository.py 存在差异，为 data_readonly 且既有纯读方法时延后 normal QAuthority 构造。normal 源分支、写/claim/出站分支未获此例外，仍进入原 GuardedAsyncConnection；方法分类来自服务器闭包的 qualname，客户端不能指定。写 SQL 仍拒绝，未把“列表有三项”单独当成写权安全证明。根 50 API 及根 51 只读 UI 对该增量提供补证，根 51 的 202 项 as-run 与最终一致。

根 46 后变更过的三份 Python fixture 已在审计目录中按当时 hash 精确重建，见 [verification.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/as-run-reconstruction/verification.json)。变化为后加的 old_compatibility/只读列表与 UI 方法、重启既有恢复目标 helper、对应阶段白名单；UI 正常响应捕获和 authenticated capabilities barrier 的方法没有随之改变。真正运行的前端 continuation06 UI fixture 的自身摘要也与当前文件一致。重建仅做字节对照，没有执行这些源文件。

额外原件身份见 [reviewed-raw-evidence-identities.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/reviewed-raw-evidence-identities.json)，PG/预算、UI 和停止的独立记录对照分别保存于本审计目录。

## 3. 合并发现

### F01 / P1 015 把三个必需权限写成了任一权限即可

位置为 [015_activity_scope_delete_permission.sql 第17行](D:/shspic/project_NO3_RetroLume-agent/backend/migrations/015_activity_scope_delete_permission.sql:17)，关联续作06合同 A 的精确旧 R02 前提与失败全事务回滚。

has_table_privilege 的逗号列表按“任一权限成立”返回 true。因此当前 NOT has_table_privilege(...,'SELECT,INSERT,UPDATE') 只有三项全无时才拒绝。具体触发为预期旧 R02 的 app 仍有 SELECT/UPDATE，但 INSERT 已被撤销，其他已列前提满足；第17行不会拒绝，随后 GRANT、profile 约束和 metadata 可 COMMIT。只剩 SELECT 的前提也一样。后续严格 profile 可能拒绝这个少权库，不能把迁移已经提交后的拒绝冒称迁移前精确拒绝及原子回滚。[PostgreSQL 17 权限查询语义](https://www.postgresql.org/docs/17/functions-info.html#FUNCTIONS-INFO-ACCESS-TABLE)

最小修正为逐项核三项必需权限，要求全部成立，并保留正确的额外权限拒绝。第18—20行用于发现任一 DELETE/TRUNCATE 的逗号形式本身是正确的，不能一律替换。补证只需在获准隔离 R02 对象中分别缺 INSERT、缺 UPDATE、仅剩 SELECT，核目标错误及 ACL/profile/metadata 无提交变化。当前 profile_checks 的 missing-delete 是迁移后的 R03 检查，不覆盖这三种迁移前提。

### F02 / P1 精确 ACL 只看直接授权，未拒绝实际继承或 SET ROLE 能力

位置为 [schema_profiles.py 第114行](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/schema_profiles.py:114) 的 SCOPE_ACL_QUERY、check_scope_permissions，以及 [schema_checks.py 第9行](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/schema_checks.py:9) 的 ROLE_QUERY。关联续作06“snapshot/readonly/restore-loader 不获正常 DELETE/TRUNCATE/管理权”和本卡“实际成员能力”要求。

查询只展开 activity_scope_sources 的表/列 ACL，把直接 grantee 归类；ROLE_QUERY 只核角色本身的布尔属性。两者均不读取成员关系或验证正常登录角色的有效/可切换权限。具体触发为 snapshot 或 restore-loader 通过直接或间接成员关系继承 retrolume_data_app，或某实际只读登录角色另有通往 app 的 INHERIT/SET 链。表/列 ACL、grantor、grant option 和当前四角色属性可以完全不变，精确检查仍通过；015 新授的 app DELETE 会传给这条成员链。normal 模式的原 data_runtime_write_guard 对 DELETE 返回 OLD，不负责区分调用者的用途，不能代替这项权限分离。[PostgreSQL 17 角色成员、INHERIT 与 SET](https://www.postgresql.org/docs/17/role-membership.html)

这是有明确配置触发的确定校验缺陷，不声称已保存的实际测试库发生过该成员配置，也不把管理员恶意改库当普通客户端攻击。合同明确要求此类不合格权限失败关闭；现有直接多权/少权正反例没有覆盖它。sealed reader 独立装配对 current_user 的有效写权探针是局部保护，不能证明正常 snapshot/loader、全部成员链和 SET 能力都受同一检查。

最小修正为在真实 profile/ACL 投影前核受信角色和相关实际登录主体的有效能力及可切换的危险角色链，拒绝 snapshot/readonly/loader 获得 normal DELETE、TRUNCATE 或管理能力。补证使用事务内成员关系反例，核真实 has_table_privilege/角色可达性与精确拒绝，结束回滚。无需新增 RLS、SECURITY DEFINER 平台或行级授权设计；获批的表级 DELETE 及仓储 CAS 模型不推翻。

### F03 / P1 Q artifact 正文没有进入源删除和记忆清理链

位置为 [q_store.py 第246行](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/q_store.py:246) 的完整 request/payload/provenance/intent 落盘、[deletions.py 第118行](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/deletions.py:118) 的源文件清理，以及 [memory/service.py 第22行](D:/shspic/project_NO3_RetroLume-agent/backend/app/memory/service.py:22) 和 memory/repository.py 的原 purge 路线。原采用设计 TASK-119 B6、D1 第2项明确要求 q 副本同步抑制并清理。

具体触发为准备过含源片段或已选 memory 正文的请求，随后正常删除对应资料或 revoke+purge 记忆。新 q-prepared 私有文件保存完整正文；源清理只处理 originals 的 hash/size targets，记忆 purge 只处理原 SQL 清单，tombstone observer 只登记观察，没有任何 Q artifact 清理入口。搜索全部 Q artifact 引用及原清理调用链未发现注册或调用。q.closed 的现有写入只用于 admission 的关闭诊断，也不删除正文副本。

inspect_request 的当前资格拒绝确实成立，原 root35 的 body_rows=0 和删除后 operator 拒绝也有效；它们只能证明业务正文及受控读取被抑制，不能证明新增加的私有明文副本已清除。源/记忆清理结束后该副本仍按代码留在控制根，缺少原合同承诺的清理及清理不确认时的 Q 关闭。此处没有读取 .runtime 文件或现场提取被删正文，不宣称发生了 HTTP 外泄。

最小修正为将受影响 prepared 正文副本纳入原删除/revoke+purge 的精确清单与确认过程，保留不可授权的摘要、事件和原费用，清理失败或未确认时关闭相关 Q 执行及正文读取。补证只在新的获准合成对象中做一次源清理、一次 memory purge 和一次清理失败；核准确副本已处理、哈希历史/007/预留保留、零重发。不得删除本次冻结工程原件或用批量清理擦除旧证据。

### F04 / P1 批准有效期只读 UTC，过期批准可因时钟回退重新可用

位置为 [q_store.py 第262行](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/q_store.py:262) 的 projection、approve、check_reference，以及 [q_protocol.py 第219行](D:/shspic/project_NO3_RetroLume-agent/backend/app/capabilities/q_protocol.py:219) 的 utcnow。关联 TASK-119 B5 第7项及本卡单调/日历有效期要求。

签发和消费只比较 datetime 的当前 UTC 与 expires_at，没有保存或检查可解释的批准时钟域、单调期限、已见 UTC 下界或失效不可逆事实。具体触发为活动及 grant 仍有充分余时，一个未领取批准签发后实际已过16分钟，UTC随后回退2分钟；prepared 的冻结 PG 快照未变，projection 会重新给 approved，reference/check_reference 的 expires_at 比较也允许继续。新创建的90秒执行窗口和 worker stop_ns 只限制该次运行，不约束这份已存批准的15分钟历史。原 grant.check 同样只比较当前 UTC，不能补足此门。

原 test_expiration_currentness_and_claim_never_enable_resend 测了单方向过期、重新批准及 Q claim 后拒绝；没有“先过期或已见较晚时间，再回退”的反例。本次静态缺陷与实际当前已冻结/已停止状态分开，不声称本机发生过回退或已有过期请求实际发送。

最小修正为在原授权路径实现可解释的单调/UTC 联合时限，时钟回退、域不明或重开无法解释时拒新外发；不能仅增加 now>=issued_at，因为回退后的时间仍可能晚于 issued_at。只补批准的前进过期、回退、重开域不明、当前合法继续及已 claim 零重发定向检查，不调整系统时钟，不借此扩大真实 Q readiness 或计价调研。

### F05 / P2 PG 已领取但无 worker Q claim 时，operator 仍可给出可继续或续批

位置为 [q_context.py 第134行](D:/shspic/project_NO3_RetroLume-agent/backend/app/capabilities/q_context.py:134) 的命令快照、[q_store.py 第265行](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/q_store.py:265) 的投影及续批条件，关联 K1 和原 launch claim 丢确认合同。

真实 ACK-launch-claim 原件已展示 command=started、launch_claimed=true、007=null。对应 Q worker 尚未启动时 q.claim 和私有 q.launch_claim 都可不存在。snapshot 虽读取 accepted/started 命令，但不把其领取事实用于投影/续批核定；QAuthority.projection/approve 只看 Q 行的 claim/launch_claimed/closed。因此在 head/scope 等未变时可继续显示 approved/can_continue，或在原批准到期后给这个已经 PG 领取的请求签新批准，违反“确未领取才能续批”的要求。

没有发现该路径会绕过业务 status/claim 检查造成第二次出站。interview/teaching 服务及仓储仍拒绝再次 launch，这正是 P2 而非已证重复收费的原因。现有三路径 ACK 的零重发事实保留。

最小修正为在投影及 operator 续批中单独核原 PG 已领取/终态，已领取只读并拒新批准；保留合法 worker 领取后的发送路径，不把可变 launch 状态粗暴加入整个冻结快照全等比较。补一个“PG claim 已 COMMIT、Q claim 未记”的投影与到期续批拒绝检查即可。

## 4. C01—C15 对照与继承

以下“通过”只覆盖写明的检查事实和快照，不覆盖 F01—F05，也不表示当前完整工程切片通过。

1. C01，三类 COMMIT 丢确认的持久事实与只读恢复通过。finalization-05 的 ACK-accepted-COMMIT、ACK-launch-claim-COMMIT、ACK-result-COMMIT 三份 checkpoint 对应不同注入边界。方法先 await 原真实事务返回再抛 ACK 异常。前两例均7次/1750000不变，分别 accepted/unclaimed 与 started/claimed，007 为空；结果例只增一笔至8/2000000，007 received 摘要一致，恰一次 transport，两次 GET 不增动作。F05 为这些事实之外的批准投影缺陷。

2. C02，列明11项全请求反例通过，整个批准有效性门仍受 F04 阻断。final05.permissions 的 actual PG snapshot/provenance 拒绝 answer、goal、memory、title、history，准确字段路径均落在被改文字处；foreign parent 为 q_parent_unqualified，不同现有实例为 q_instance_mismatch，字节/endpoint 为 q_prepared_changed，missing artifact 为 FileNotFoundError.2，重复批准保持同决定和 event_seq。前后金融相同、claim/admission为空，不把任意403/409/503充数。模型 schema 的合法性与真实全文来源证明分开评价。

3. C03，wire 兼容的列明路径通过。OneCallInput 原v3省略新增空字段，原v4仍沿原分支；新v4授权引用不进入 provider payload。现有 test_wire3_original_bytes_have_no_new_default_fields、test_wire4_carries_private_authorization_without_provider_message_change、v1/v2额度分支与旧S08原件按其原层级继承，实际模型/embedding请求组装和最终 send_frozen 使用同一已核 bytes 的代码链已审。本审计未重新运行兼容单测。

4. C04，不通过。副本根的 q_instance_identity、残尾 control_tail_unconfirmed、missing artifact、source/memory 资格变化和 readonly 根拒绝的原记录成立；ControlHub 每次在真锁内重新读完整当前字节与文件身份，新 Q cache 仍经 assert_writable/check_root，不绕过原S控制核验。但 F02 的实际成员能力和 F03 的副本清理未满足，不能扩大成完整权限及删除合同通过。

5. C05，获批工程范围的冻结/零真实外发通过。惰性示例保持关闭，returned_models 未核不放行，TESTONLY 根与最低 transport 的 is_external=false 分支分开；真实 provider、费用、preview、Git 在本工程记录均为0。此结论不提供正式账户或外部计价 readiness。

6. C06，精确合成资源和采用范围通过。一个原CID/卷内新增批准源逻辑库，一份生产工厂创建的隔离恢复目标；preflight、create前计数、实际CID返回登记、镜像/limits/mount/ports/labels的代码与原件对应。未要求新目标伪装旧源label，未迁移旧四库。015 的权限正确性另按 F01/F02 判不通过。

7. C07，零重发/原UNKNOWN/原预留保留的事实通过；批准投影与续批的完整合同未通过，见F05。最新见证保留原三个键的事件子序列，新源三个批准未领取意图没有变成新执行权；源frozen、selector选只读目标后未重绑grant。不能把没有Q claim等同PG尚未领取。

8. C08，列明真实检索及 query→model 接线通过。两域的生产 retrieval freeze/claim、实际 embedding、received/ref、模型等待及原键继续原件可继承；缓存限原source/version/revision/space和合格当前结果。未用未批准新文字或跨活动父替代完整请求。严格权限和时间缺陷不因检索正例通过而消失。

9. C09，原教学练习和记忆显示的有限事实通过。validation-04/original-exercise-positive.json 的原accepted/unclaimed练习 cd632dfd-8a25-465b-895e-375b0ce1d48e 在根21提交；根24及 memory-display-PG 对无记忆 teaching.v3 与仍有选择的 budget02 分开核证。最终只改变读取显示，不宣称删除后记忆仍可作模型父，亦不宣称真实供应商语义已验证。

10. C10，五入口有限正常UI可继承。根23原文件为PARTIAL，保留面试query/model、legacy followup、HTML的三个已保存子例；根24补教学query/model，检索入口由其中实际RetrievalPanel交互覆盖。owner/view晚到及重开仅GET、同键显式继续按各自case和方法接受，没有把根23/24整根FAIL改绿。旧bundle仅证明当时路径；最终context.tsx普通响应门加严由根46的新正式bundle补证，不把旧bundle直接冒称最终全UI。

11. C11，K2并发一致性的列明范围通过。真实transport返回后释放shared，独立actor提交head/revoke/source/scope新增/memory，再由结果事务重取exclusive；原007及预扣保留，迟到不推进改变后的head。新scope收缩的before为scope4/head5、actor COMMIT后scope5/head6，007当时dispatched，最终received且实际摘要等于2ef25ef0b1e2dbc8f97def352e77736bc91b02a22f533f08a6344e6d1c0a4e82，head保持6，费用仅从3/750000到4/1000000。新scope只删差集，CAS/来源锁/版本upsert与其他活动不变的原件成立。

12. C12，真实PG共同99→100门通过。budget.py 经真实生产admission累积99笔，roster为47/28/24、24750000；实际两个等待advisory的backend为3923和3925。同一A1有效lease、不同合法model/embedding请求竞争，最终100/25000000，model rejected、embedding unknown，新operation与一次合成transport对应，输方不出站；达限后两provider准确拒outbound_grant_exhausted，同库重开保留100/25000000。最终015/R03和readonly读取分支未改变该金融SQL及正常源admit/mark调用关系，无需重刷99笔。对照见 budget-evidence-comparison.json。

13. C13，列明最终UI与只读恢复列表通过。两份真实normal GET200的headers/body/can_continue已捕获，批准未领取；同namespace下真实freeze改变mode/read_only后才释放第一份，真实verified目标及selector/rebind完成后才释放第二份。原生fetch确已fulfilled，业务JSON未被消费，前后页面/输入/存储相同且无自动POST，区别于传输取消。authenticated capabilities请求在生产local_session检查后、构造body前被屏障暂停，原请求header跨过提交后获得新生产body；后续session bootstrap和新namespace存储读取一致，没有setter/body/token注入。根50/51封闭最终pure-read增量，不能替代根46的两条异步证明。对照见 ui-evidence-comparison.json。

14. C14，规定历史时点的精确停止证据通过。070于2026-10-20 23:08:53.727173+08:00记录622组PID/birth、135个Job、两精确CID Running=false/Pid0和55480/55481/18120无监听；原070、071均exit0/tree_empty，071为文件保存。已保存事件序列未显示070后业务再起。没有运行Docker、进程或端口探针验证现在状态。对照见 stop-record-comparison.json。

15. C15，不通过。候选身份、范围和原始子事实可审，集中独审也已实际交付，但四项P1及F05未关闭，权限、清理、时间门缺少对应反例。不能把工程JSON中的engineering_complete/stable_for_independent_audit当本审计批准，更不能签STEP018整体、019/020、M1、项目、发布或Q启用。

memory窗口的证明特别限定如下。根35原trace、共享释放屏障、独立actor COMMIT、最终007和后续PG对账足以支持“实际撤销/purge发生、late head未推进、007和原reservation保留、GET无动作”。该根没有即时保存before-financial快照，不能补写它，也不能声称单靠该轮精确证明了全部金融差值；后续核证用原operation条数和reserved_cost对齐，范围明确。本缺口不要求整套memory重跑。F03是另外的私有正文副本清理缺陷。

旧scope503按原精确命令缺失、scope_revision仍1及另一个模型45b8d0b4-dd77-44d7-8cdd-370ef475c7b3已committed/received判其原scope变更未提交；不是从503反推回滚。根43 invalid-source 的500保留为真实旧缺陷，最终interview_repository锁内补current_version/revision，根44准确409/source_invalid且业务/金融前后不变，按修后字节接受。

R01/R02/R03兼容亦分层。001—014及旧常量未改只是B层依据；另有旧四库真实新只读连接与R03正常backup/verified restore/seal原件。067整体FAIL保留其独立R01文件域子例；068修正为真正进入PackageReader上下文后，错误迁移hash为codec_mismatch，未知profile为unsupported_format，合法R02包读取和真实R03包读取成立。没有把ZIP reader说成真实R01数据库恢复。

## 5. 执行控制重建

工程账重建见 [engineering-control-reconstruction.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/engineering-control-reconstruction.json)。实际核对5121条events、51根、70份已执行command回执；038原未执行，不补造第71份历史回执。按各许可生效分段核对，不套最后宽上限追认以前行为。

1. 初始许可根1—8，root/PG/API cap为8/8/8，wall14400，持有10800。
2. continuation01实际采纳后根9—16，cap16/16/16，wall21600，持有14400。
3. repair03实际采纳后根17—20，cap20/20/20，wall25200；validation04根21—24，cap24/24/24，wall28800，持有仍14400。浏览器512MiB门仅从04前向采用，不追认早先768MiB门未过为已启动。
4. finalization05实际采纳后根25—40，cap64/64/96，wall57600，持有21600；新增matrix-final仅用于批准的独立TESTONLY反例。
5. continuation06实际登记后根41—51，root/PG/API等额度未重开，只按批准将对象/卷cap各1→2；新增scope-ui-final和工厂目标各在精确许可内。已有失败、余量和unknown未归零。

已保存各根的入口计数未超当期cap、未早于该期实际采用登记；已保存单根elapsed均小于1800秒，回执wall未超各自声明限额，51根结束清理记录均确认。该检查不等于每个未观测历史瞬间都合规，也不代替同问题失败次数的原始保留。

最终累计为roots51/64、PGstarts52/64、API55/96、Browser14/16、build5/8、Native64/128、HTTP1459/10000；PG/卷create尝试各2/2、实际对象/卷各2/2。125条失败记录和TASK117旧81条分别保留，不把记录条数冒充独立缺陷数。active_root/active_command为空只说明末态。

wall逐字段复算为50243.003003/57600秒，与唯一账相同；50299.862003是含071预留60秒的旧报告时点，以071实测3.141替换，差56.859秒。持有为2667.078295/21600秒，根9的79.139295不确定性上界等仍保留。两个7200预留、其他中断不确定性未核销为0；这些是保守上界，不叫CPU或精确工作量，人工实际总时长unknown。

控制轴不通过的原因是接收/计时登记合同未全满足，而非发现最终资源仍在运行。06自身adoption.json明确初次合同读取工具早于登记，13:36:43Z是读卡期间首次采钟，登记为13:38:10.345685Z，未满足permit要求“实际接收在首次新工具前登记”。3秒边界的精确首工具起点没有独立原回执，不能把采钟当接收首点；该微小差异不影响本次实际业务都远早于次日01:06:43Z停止的事实，也不能被后来的登记追认为先登记。

05的精确接收时间未保存，采用签发时刻作更早保守下界并登记finish_deadline=2026-10-20 20:04:46.848938+08:00。059仅文件保存的结束为20:12:01.236510+08:00，晚于该登记期限约434.388秒。真实接收至多24h是否越界仍缺原首点，不虚构连续CPU工作，也不将这份晚保存回执当作业务重启或新24h许可。历史控制限制由主控留账，不能通过改写旧收据消除。TASK117既有控制不通过同样继续保留，不传成TASK120代码已坏，也不被本次技术子项通过洗掉。

源精确CID为b89522070d4b64fc67efed810852ccc21948058f154bf4fa1889f4d8d69a102f，卷retrolume-task120-qprep-data；目标CID为4eb5be54b713e5412be702e27684d98d2b7de92a77f9085b3ce84a5f4b124332，name为retrolume-task120-scopeui-ro1，卷为同名-data。原件核对同一完整镜像sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f、1CPU/512MiB/pids128/restart=no、loopback55480/55481、API18120、无host bind。只接受原停止时点，没有探测当前机器。

财务按实例核对。flow为25/6250000，budget01为100/25000000，budget02为8/2000000，matrix-final为23/5750000，新源为5/1250000；各实例当前已保存快照R均0，工具预留未增加。恢复副本的5/1250000是备份时点历史，不能与源相加成新预算。真实PG新连接/production readonly读取是这些余额事实的依据，Q journal仅作身份、关闭与事件见证。

未发现本工程原记录中的批删、prune/drop、真实provider/实际付费、preview或Git写。独立GitHub同步具有单独授权，未混入本工程0新增Git计数。无法从只读证据确认的整个宿主外部活动没有冒称为0。

## 6. 审计投入、未验证与最小后续

本审计首批先读入口和卡面，未在第一条工具前单独采钟；首个可信时点为2026-10-21 07:44:23+08:00。精确人工接收秒值unknown，保守采用早于该点的卡面签发2026-10-21 07:41:23.826587+08:00作为8h下界，截止15:41:23.826587+08:00，没有用签发冒称实际接收。

实际命令、退出码、wall、非零退出和投入保留在 [audit-command-log.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/audit-command-log.json) 与 [audit-session-receipt.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/audit-session-receipt.json)。专门的逐命令台账从第9条文件命令开始；启动期8条按本窗工具回执和用途汇编，完整命令串未在专门台账保存，不能冒称精确重放清单。其中一份大输出截断导致对应wall的精确回执未完整保留，按60秒保守预留，不记0；其他可见收据与后续逐命令数据保留。另有自己的元数据脚本一次因permit_history字段不统一KeyError退出，已按真实id/permit_id结构修正；若干rg不存在路径、初始Python控制台编码及输出截断也如实登记。没有以这些元数据问题触发产品运行、改工程原件或重置投入。

本次实际访问两页官方文档，未安装或联网下载。自身写入仅本审计证据目录与本统一结果；报告落盘后核可读和身份，产品/工程输入再次冻结核验结果另存。人工实际思考/阅读耗时与模型token用量无法可靠取得，均为unknown，不编造。

最小下一步由主控把F01—F05一次合并交回原TASK120工程窗口。修正方案与验证预算须按主控后续合同执行，本审计没有自动建立任何业务运行额度。

1. 修F01/F02后，只补迁移缺权与实际角色继承/SET反例、准确失败回滚和受影响profile/backup/restore识别；原001—014、R01/R02、旧四库及金融事实保持原适用边界。
2. 修F03后，用新批准合成对象补源与memory的精确Q副本清理、失败关闭及原摘要/007/费用保留，不删除本次封存原件，不重跑整套memory竞态。
3. 修F04/F05后，只补批准时间回退/域不明、合法继续、PG已领取未Q claim的投影与续批拒绝及零重发。若只改服务端时限/投影且前端未变，不要求重建bundle。
4. 本TASK121和本独审窗口后续只增量复核修正与直接影响。当前C12、三ACK、列明K2、UI和停止等证据按对象复用，不重新启动本轮完整审计。主控负责共享状态、验收与编号。

真实Q仍待原采用合同所留的当前官方及账户适用性、价格/税费币种、token/framing/reasoning上界、严格返回身份、正常secret loader非敏感readiness、实际新normal实例与固定roster、全部Must可容纳的剩余语义矩阵、集中独审修正关闭及主控首次启用回执；T0/72h未在本轮建立。这些后续事项未运行不另判成本卡事故，也没有被上述工程子事实授权。

报告保存并回传到此为本卡终点。除了人工带回此结果，不需要用户提供密钥、SQL、截图、额外放开Q或再次批准本次只读审查。

