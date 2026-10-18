# TASK-092 / R-086 G5有限工具执行与持久次数 执行结果

## 续作03：独立审计两项证据收口 E1+E2 当前有效

一句话结论：续作03两项证据缺口已按置顶卡收口——E1（C2参数长度边界）以纯离线新增四例绑定真实可达路径通过（原始JSON路径精确2048字节通过/2049长度阶段拒绝；规范wire路径2049长度阶段拒绝、2048非规范规范等值阶段拒绝；多字节按字节非字符；并给出2048规范参数不可达的可达性依据），E2（real-01旧夹具原件缺失导致的适用性缺口）在项目内未找到精确原件、哈希仲裁逆向重建164个结构化变体全部未中后不伪造旧件，按卡启用授权内一次定向PG（real-06）：最终版冻结的11个缺证方法在真实工具库11/11通过，c7/c9已由real-03最终版通过、4项旧model回归文件hash与real-01一致直接复用——全部13个ToolPostgresTests方法自此均有最终版本真实PG通过证据。产品、迁移零改动零漂移；G5仍为候选实现，最终是否关闭由编排据证据裁定，本窗口不自签。

授权与身份：TASK-092置顶续作03（只补两项证据，不新增G5功能；E1允许最小新增离线边界测试；E2优先零运行恢复，必要时新授权real-06一次入口+原容器一次启动，总尝试≤6；业务180秒+收尾120秒总300秒；Windows业务会话新增0；费用0）。沿用原Claude桌面Code实现窗口（Fable 5），补读093审计第6节与audit-verification.json，不重开代码审查、不回传中间步骤。

E1（长度边界，真实可达路径）：先区分两条真实路径并核实可达性——ToolRegistry.plan收原始JSON字符串（长度按UTF8字节先行拒绝），ToolExecutionInput.to_wire/from_wire收严格规范字节（长度通过后仍要求逐字节规范等值）；合法规范参数受Schema约束（仅operation/left/right三标量、|数值|≤1e12），枚举最坏样本规范字节最大<128，2048规范参数不可达，其长度分支属纵深防御——以可达性依据作证，不伪造"2048规范参数成功"样本，不放宽Schema或长度常量、不patch产品。新增ArgumentLengthBoundaryTests四例（纯离线，无PG/Job/网络）：原始路径精确2048字节（合法JSON空白填充、明确记录该路径不是规范wire）通过且2049命中长度阶段"工具参数不是有界 JSON 字符串"；wire路径短规范样本成功对照（to_wire/from_wire共同委托），2049解析前命中"tool arguments exceed limit"，精确2048非规范在规范等值阶段命中"tool arguments not canonical"；多字节样本证明按字节计长（字节超限而字符未超在长度阶段拒绝）、精确2048字节含多字节样本通过长度后由Schema阶段拒绝额外字段（阶段可分，不混同字符与字节）；规范2048不可达依据与空白剥离规范等值。首跑2处断言把非规范键序误当规范形式，第1次有据修正后4/4通过（0.359秒）；离线账新增0.859秒（首跑0.5+复跑0.359）。测试文件pre fc6da4375c7615d5482feeedf5ff7165baea9d438f97b277ab3004968fe19733→post 08063c224b400f972e893640b4591cb0657ee088e313c903366495969a01c40c，pre原件存continuation-03/pre；旧final-product-hashes、as-run与093审计冻结原件未覆盖，增量见continuation-03/final-product-hashes-03.json与e1-increment.json。

E2（旧夹具适用性，优先零运行未果→授权定向PG）：在项目内有限查找（find全项目test_activity_tools*与*.patch/*.diff，≤15分钟、不读聊天/秘密存储、不全盘扫描）未发现与real-01 as-run记录的完整hash eecba489fb93efa3a384e8ce5ffb557c1f3ed1662cc198374dee8cb3d1330a0f 一致的原件；按卡允许的"从已存证据逆向重建且必须完整hash匹配"路径，对final版反向应用两次已记录修改（c7方法块、c9上下文块）并枚举注释措辞/插入位置/标点等结构化变体共164个候选，逐候选计算完整SHA256全部未中（结构性交叉核对c9 admit行号992与real-01回溯一致，但逐字节不等即不采信）——拒绝凭行号或记忆宣称原件，不伪造假旧件；全过程存continuation-03/reconstruction-attempt.json。据此启用授权回退：新最小入口real06_runner.py冻结11个缺证方法ID与理由（排除已由real-03最终版通过的c7/c9；4项旧model回归文件test_activity_results/test_activity_time_budget的hash与real-01一致故直接复用不跟随重跑），real-06一次入口：只访问retrolume_task092_tools与task092_synth角色、不运行迁移/upgrade、不重建schema/数据库；完整JSON白名单核停止与归属，凭据仅stdin/子进程环境；attempt#6与启动#6均立即登记。结果：11/11真实通过（测试4.813秒，批12.704秒，exit0，source_unchanged），树零、句柄关闭、精确stop核Running=false/Pid=0、cleanup_incomplete=false、Windows会话0、无隐藏retry。全部13个ToolPostgresTests方法自此均有最终版本（含E1增量）的真实PG通过证据，审计缺口二以直接终版证据闭合，强于旧原件反转证明路线。

累计预算与资源（不重置历史）：主动投入本轮约0.5小时（首轮1.5+续作01约0.7+续作02约0.3声明另计，仍远低于原8小时且本轮≤60分钟限内）。离线累计7.514/1800秒（新增E1首跑+复跑0.859）。真实累计6/6批、74.156/3600秒（新增real-06 12.704；批次与容器启动额度6/6已用满，无剩余许可）。Windows业务会话7/12未新增；付费与网络请求0；新容器/卷/镜像0。资源：仅精确容器e49d…，批后完整JSON核实Running=false/Pid=0、外层树零、句柄关闭、active_processes空；tools库仅新增/清理本批测试自有合成行（各用例teardown），upgrade库本次未触；旧real-01—05/offline/continuation证据只读未覆写；attempt-ledger第6条含授权、冻结目标、理由与前后累计。

原证据复用与剩余限制：Windows六方向、PG17唯一方法、93离线、real-05升级收尾均列原件不复制；审计缺口一与缺口二均关闭且升级方式更直接（终版真实运行）。剩余限制仅两类：E1未伪造不可达的"2048规范参数成功"样本而以其不可达依据+阶段可分证据替代（属如实设计而非缺口）；如编排认为需要，093审计窗口可对新增E1测试与real-06批做限该两项的增量确认，不全面重审。最终G5关闭由编排据全部证据裁定。

## 续作02：升级库完整收尾 real-05 历史保留

一句话结论：续作02唯一批real-05在8.422秒内一次通过，升级库三个剩余子目标s1（happy重建全走通含生命线拒绝与重复008）、s2（篡改成本约束识别失败整事务回滚）、s3（缺前置在ALTER前拒绝且零DDL）全部独立真实通过，exit0、树零、句柄关闭、容器停止、Windows业务会话0；real-06按"real-05全过立即停止"未使用。至此C1—C12全部子目标均已有真实运行通过证据，G5为候选实现且卡内验证完成，待编排另卡隔离集中独立增强审计，本窗口不自签、不宣告放行或M-1。

授权与身份：TASK-092置顶续作02（只收尾升级库；批/启动上限4→6；每批业务180秒+收尾120秒、总截止300秒；real-05一次三场景，real-06仅限范围内缺陷且过两次修正门后定向；Windows业务会话新增0；费用0）。沿用原Claude桌面Code实现窗口（Fable 5），不重读全历史、不重跑已通过的Windows与17唯一PG方法及93离线项、不运行旧整批入口。

准备（同卡连续，不触Docker/PG/Job）：升级库夹具原件存continuation-02/pre（upgrade_child.py、child_control.py与win_chain/bootstrap/legacy_probe哈希；未触碰脚本在准备核对中断言未变）。upgrade_child.py按卡重构：s1/s2/s3改为独立场景函数、各自独立连接与独立结果（upgrade-summary含各自passed/failed/not_run，单场景失败且清理确认时不阻塞其他隔离schema，失败仍使整批非零；连接finally关闭，清理不确定即停后续并标not_run）；阴性识别废弃布尔标记，改为expect_migration_rejection显式断言SQLSTATE=P0001且isinstance RaiseException且命中008自身有限识别文本（已有痕迹/唯一识别/前置不存在），排除DSN/权限/语法/夹具表缺失类错误；强化前后投影——s2断言五新列=0、008具名约束=0（无部分DDL）、篡改约束仍在、旧行与正文逐字节不变；s3断言表/列/约束/序列全零；s1重复008后schema与数据逐字段不变；保留TASK092_UPGRADE_ONLY定向重跑（只重建所选schema，不抹其他通过证据）。剩余路径一次走查记录continuation-02/walkthrough.json（来源/活动/租约/操作键前提、异常目标、search_path、失败后事务状态）。新专用入口upgrade_runner.py：仅调度upgrade_child，完整inspect JSON白名单核证，180/120/300三段截止由同一单调总截止派生，真实闸门（历史4批finished、active空、未用；retry需real-05非零且未用过retry），Windows会话非零即判违规，attempt立即登记。准备核对continuation-02/check.py 0.547秒通过（其中independent_results一项为检查脚本自身引号写法误报，已用正确形式直接确证结构存在），计离线账。

real-05三目标结果（exit0，8.422秒，attempt#5、启动#5；源hash开跑即冻结，批后产品48项零漂移、证据零漂移）：
- s1 通过：001—007合法非空基线→008提交；行不变全量断言（三列新增集合、kind=model、两元数据NULL、其余逐字段字节相等、正文sha 4377a73e…不变、活动仅两列默认）；旧model生命线全走通（含claim/admit含tool_names/mark/record/read kind=model/未配置额度拒工具tool_limit_unconfigured且零副作用/关门结算）；重复008在独立连接命中008自身"已有痕迹"RAISE（RaiseException/P0001）且主schema约束15项与数据逐字段不变。
- s2 通过：独立基线+篡改成本约束定义；008在唯一识别阶段RAISE（P0001，"原成本正值约束未能唯一识别（匹配 0 条）"）；整事务回滚证实：schema约束总数84不变、五新列0、008具名约束0（无部分DDL）、篡改约束仍在、旧行与正文逐字节不变。
- s3 通过：独立空schema；008在ALTER前门禁RAISE（P0001，"008 前置不存在"）；事后表/列/约束/序列全零。
- real-06未使用（real-05 failed=[]，按卡不消耗额度）；real-05全过即为升级库收尾终点。

累计预算与资源（不重置历史）：主动投入续作02约0.3小时（首轮1.5+续作01约0.7声明另计，总量仍在8小时内且本轮90分钟限内）。离线累计6.655/1800秒（新增check 0.547）。真实累计5/6批、61.452/3600秒（新增real-05 8.422）；容器启动5/6（第6次额度按"全过即止"未使用）；Windows业务会话7/12封存未用；付费与网络请求0；新容器/卷/镜像0。资源：仅精确容器e49d…，批后完整JSON核实Running=false/Pid=0、外层树零、句柄关闭、cleanup_incomplete=false、active_processes空；upgrade三schema保留供审计（s1含008后状态与生命线行、s2含篡改基线与回滚后原状、s3零对象）；tools库未触数据；旧real/offline/continuation-01目录只读未覆写；attempt-ledger第5条含续作授权与前后累计。

C1—C12收口状态（本轮更新后）：C1空库001—008真实通过（real-01）+非空001—007→008真实通过（real-05 s1）；全部条件反例真实通过（real-01）；重复008整体回滚真实通过（real-01工具库+real-05 s1）；篡改约束识别失败回滚与缺前置拒绝真实通过（real-05 s2/s3）。C2—C6、C8真实通过（real-01）；C7、C9真实通过（real-03）；C10真实通过（real-04工具链+旧model回归）；C11真实通过（real-04两会话）；C12真实通过（real-01目标项+real-04两混用探针）。全部子类均标注真实运行证据；注入边界沿用既有如实声明（哈希捕获包装、计数包装真实调用、同步阻塞替身、合成transport、旧版行为副本局部探针），不冒称完整跨版本部署兼容。

原证据复用与限制：Windows与PG旧项、93离线只列原件与适用范围，未复制日志、未重跑。剩余限制仅两类：独立增强审计未进行；单样本合成覆盖与替换型自举的固有边界（已在各轮如实标注）。下一步由编排在稳定全包上另卡组织隔离集中独立增强审计；本卡此后只能称"G5候选实现及卡内验证完成待隔离审计"。

## 续作01：real-04一批与收尾 历史保留

一句话结论：续作01按置顶卡在唯一批real-04内完成——Windows六方向（C10工具链与旧model端到端回归、C11硬停止与恢复、C12两个混用探针）五个场景函数、六次受控会话全部真实通过，C10/C11/C12混用与旧model兼容由此转为真实通过；升级库非空迁移的008提交与旧行逐字段不变已获真实通过（含F-U2修复在真实运行中生效），但该子批在旧model生命线的工具拒绝探针处以本卡第三处夹具缺陷中止，缺陷已修复并经真实校验路径定向复检通过却无批槽复跑，s2篡改约束回滚与s3缺前置两个子目标仍未运行。本卡仍为候选交付：剩余夹具级缺口如实交审计与编排决定，不暗开real-05，独立增强审计尚未进行，不等于G5放行或STEP-006/008完成。

### 授权、身份与准备修复

授权：TASK-092置顶续作01（编排在用户已批准范围内追加real-04一批与原容器一次启动，累计上限3→4；业务300秒+收尾120秒、入口总截止420秒；Windows本轮至多6会话；费用0）。执行身份沿用原Claude桌面Code实现窗口（Fable 5），不重读全历史、不重实现G5、不自签审计、不自动转派。

准备阶段（同卡连续，全部不触Docker/PG/Job）：runner与夹具原件存 continuation-01/pre（8份+pre-hashes，其中batch_runner/bootstrap/legacy_probe/child_control/tool_pg_child/offline_runner六份与编排check.json逐hash一致，已断言未变）；修复并验证F-U2——upgrade_child旧操作行比较先断言三列新增集合（kind/arguments_sha256/tool_call_id）、kind=model与两元数据NULL，再排除精确三列比较旧行原全部字段，未迁就测试改迁移；修复win_chain场景清单/函数映射（原清单六名引用不存在的scenario_tool_stop/tool_recovery，实为5函数含一个两会话组合）；新增清理纪律（会话supervision.cleanup_incomplete即CleanupFatal停止后续场景、stop失败显式emit recovery_not_run并停测、verify_bootstrap按mtime取最新捕获）；新independent入口continuation_runner.py：只调度upgrade_child与win_chain、完整inspect JSON在内存解析白名单（不保存/打印Env、缺安全字段失败关闭）、业务300秒与收尾120秒由同一单调总截止派生（旧deadline-180静默挤压修正为显式两段）、入口三先决（历史三批finished、active为空、未用）后一次调用立即记第4次尝试（预检失败也占槽）、未改batch_runner、未删旧attempt。准备核对prep_check.py（compile20文件+纯数据断言：场景映射、F-U2合成行、runner常量420/300/120与子批清单、闸门、全JSON inspect、legacy pre存在）通过，0.547秒并计离线账；启动前冻结 continuation-01/frozen-hashes.json。

### real-04实际结果

入口一次：27.109秒（业务27秒内完成，远低于300秒），attempt#4、启动#4、Windows会话6；升级子批exit1后按授权在库隔离与清理已确认（cleanup_confirmed=true）时继续独立Windows；批后容器Running=false/Pid=0、外层树零、句柄关闭、cleanup_incomplete=false、active_processes空。

Windows子批（exit0，complete failed=[]，产品加载与as-run逐hash一致）：
- tool_chain（C10）：service→固定launcher/固定链→真实finite_calculate一次（worker捕获tool_execute_calls=1、transport_sends=0）→真实PG正文{"format":"text","value":"3"}与双hash一致、read/list类型一致、tools_reserved=1且模型请求/费用为0、树零→句柄关闭→关门→结算，S=1恰等于sup.settled_seconds（real-03误加1断言修正后真实成立）、业务Job确认消失（ERROR_FILE_NOT_FOUND）。
- model_regression（C10配套）：旧无工具model外2/内3端到端，合成transport恰好1次发送、消息序[assistant,user]、工具执行被禁（0次），业务committed_current、父P哈希不变、Job消失。
- tool_stop_recovery（C11两方向两会话）：停止会话在mark确认（dispatched）后以不合作同步阻塞替身触发SUP截止硬终止，state=stopped_at_deadline、树零、Job消失、无部分退款（tools_reserved=1、R=10、S=0、未关门）；恢复会话同会话显式接续新键，租约到期后claim折叠一次，S=11=10+结算1、T1收敛unknown且无正文不重执行、T2 received且恢复worker恰执行1次。
- old_sup_reject（C12混用）：旧SUP行为副本真实会话收到外3即拒绝exit1，零claim零副作用（活动仍pending、G=0、R=0、T=0、无op无正文）；场景内正反照证明副本接受外2帧、拒绝外3帧。
- old_worker_reject（C12混用）：旧worker行为副本拒one_tool退出2→worker_failed_full_reservation、树零；tools_reserved=0无工具准入，但R=10时间预扣保留——"旧worker拒新工具不代表先前时间预扣不存在"获真实证据。

升级子批（exit1，仅运行到happy path中段）：001—007合法非空基线应用→008提交——`upgrade_happy_rows_intact`真实发出：3条旧操作行仅新增kind/arguments_sha256/tool_call_id三列、kind=model、两元数据NULL、排除三列后与008前逐字段字节相等、正文逐字节与sha不变、活动行仅新增max_tool_calls=NULL与tools_reserved=0；随后旧model生命线（claim→model admit含tool_names→mark→record→read且kind=model→close→settle）按哈希绑定脚本顺序全部通过；中止于“未配置额度拒工具”探针，AssertionError(invalid_input)——第三处夹具缺陷：探针用model键M1的CallContext配工具键T1的call，先命中admit_tool_operation的操作键绑定校验（且旧排序在settle之后，即使绑定正确也会先遇lease_invalid）。运行后修正：探针移到close/settle之前、以T1自身上下文执行、并断言零副作用（T1无行、tools_reserved=0）；补丁存 continuation-01/upgrade_child-postreal04.patch（4,739字符）。定向复检control-check-02.py（子类占位事务边界的真实校验路径，零PG零网络，0.234秒计离线账）通过：错误配对在事务前被拒，修正配对通过绑定校验并到达事务边界。**该修正未获真实复跑**。未运行：s1完整收尾（生命周期工具拒绝真实断言、重复008在upgrade库的schema级复跑——同机制已在real-01工具库验证）、s2篡改成本约束识别失败整体回滚、s3空schema缺前置拒绝。

### 计数纠正（按编排核对件）

final-product-hashes.json为21条清单，其中4条pre=post（app/activities/__init__.py、worker/one_call.py、tests/test_capabilities.py、tests/test_worker_session.py），实际差异为12改+5新共17项，不是21项改动。离线为93执行并通过、另71跳过（PG专用DSN缺失），不是164通过。PG首批17方法（15过2败）+real-03定向复验2方法=19执行实例/17唯一方法有效通过，不是19个独立方法。原scenario-manifest.frozen_utc=2026-10-01T00:05:00+08:00为书写时投影值，与real-01实际时间2026-09-30T22:51:47+08:00不一致，据真实manifest披露且不回改旧值；续作01冻结条目使用真实时点2026-09-30T23:18:56+08:00。

### 累计预算与资源（不重置历史）

主动投入约2.2小时/8小时（首轮约1.5小时声明+续作约0.7小时，连续执行无等待）。离线累计6.108/1800秒（offline-01 2.687、offline-02 2.640、prep 0.547、control-check-02 0.234）。真实累计4/4批、53.030/3600秒（real-01 16.593、real-02 1.844、real-03 7.484、real-04 27.109）。容器启动4/4，Windows会话7/12（首轮1+本轮6），付费与网络请求0。同缺陷修正次数：c7夹具1次（已复验）、c9夹具1次（已复验）、runner预检1次（已复验）、upgrade活动快照1次+操作行F-U2一次（前者real-04中以行不变全量断言生效）、win场景清单1次（real-04通过）、生命线探针1次（复检通过未复跑）——均未超两次上限。资源：仅精确容器e49d…，批后stop并核Running=false/Pid=0（完整JSON解析）、树零/句柄关闭、active_processes空；库retrolume_task092_tools/upgrade与角色task092_synth保留供审计，upgrade三schema已在real-04先摘要后重建；无新容器/卷/镜像，旧批证据目录只读未覆写。

### C1—C12逐子目标最终标记（真实通过/mock局部/静态/未覆盖/旧证据复用）

- C1迁移：空库001—008真实通过（real-01应用+标记、real-03/04复验）；非空001—007→008的旧行逐字段不变与预算默认真实通过（real-04）；六类条件反例、NULL/零额/满额真实通过（real-01工具库）；重复008整体回滚真实通过（real-01工具库，upgrade库schema级未复跑）；s2篡改约束识别失败回滚、s3缺前置拒绝未覆盖（静态逻辑在008内，未真实执行）。
- C2、C3、C4、C5、C6、C8真实通过（real-01，未变复用）；C7、C9真实通过（real-01夹具修正后real-03定向复验）。
- C10：工具链真实通过（real-04）+旧model外2/内3真实回归通过（real-04）。
- C11：硬停止与恢复真实通过（real-04两会话）。
- C12：PG目标项真实通过（real-01）；外3/内4与旧帧混用真实通过（real-04两探针）；旧worker拒新工具与时间预扣并存真实通过（real-04）。
- 框架计数区分：Windows 5场景函数/6方向会话（含一个两会话组合）/7次累计会话；PG 19执行实例/17唯一方法；离线164发现/93执行通过/71跳过。
- 注入边界如实标注：SUP/worker为行为保持的哈希捕获包装（真实模块与协议帧不替换）；工具执行计数包装调用真实execute；C11阻塞替身为执行边界不合作同步阻塞反例（不代表真实finite_calculate会挂死，正常运算由C10证明）；旧model回复为合成transport（无外部请求）；旧SUP/旧worker为pre原件行为副本，仅证明混用失败关闭与预扣存在，不构成完整跨版本部署兼容结论。

### 未覆盖、风险与下一步

未覆盖：upgrade库s2/s3两回滚子目标；修复后生命线拒绝探针与s1收尾的真实复跑；批内upgrade库schema级重复008。风险：两处未复跑的夹具修正已有静态+真实校验路径复检，但仍属"未在PG上钉死"；独立增强审计尚未进行，当前成果为候选，任何放行决定属编排与审计。

下一步（不自行执行，交编排最小决定）：可续一张极小的定向批（沿本卡边界：修复版upgrade_child单批，预计1分钟内，批/启动上限各再+1）闭合upgrade全部子目标，或在已知缺口清单下直接进入隔离独立增强审计；两者都不改变已通过的Windows/PG结果与冻结产品（48项app+迁移零漂移）。

## 以下为首轮全文 历史保留

一句话结论：G5内部最小切片的实现与离线定向验证已完整交付（离线93/93通过，其中PG项71跳过）；真实PG工具库上C1—C9、C12目标项与旧model定向回归已经真实通过（17项中15项首轮过、2项夹具修正后在real-03复验通过，产品源码跨批48项指纹零差异）；非空迁移收尾、Windows C10末例确认、C11与混用探针因批次额度3/3用尽而未完成，相关夹具缺陷已修复就位但需编排批准新批槽复验。本卡为候选状态，不冒充最终通过，不等于G5放行，更不等于M-1/STEP-006/008完成，独立增强审计尚未进行。

## 任务、身份与授权

- TASK/R：TASK-092 / R-086。父TASK-091 / R-085（设计已验收关闭，冻结结果SHA256 a6dfdd231ea1cac76497c1a6c3dd77a77e7b653cac2231850d95d49128c92866），关联090/G4、088—089/G3、083—084/D3、STEP006/008、FLOW-005、DATA-007及NFR-002/003、SEC-002。需求v1.1、架构v0.60、执行v1.81。
- 授权引用：用户2026-09-30对091-work-decision置顶唯一G5合并变更包的明确“批准”；本卡全文（含全部预算、资源白名单与停止门）。技术合同正文为TASK-091-result.md当前修正轮全文，本轮实施逐条对齐B1—B10与C1—C12。
- 实际执行身份：Claude桌面Code窗口（本会话），实际模型Fable 5（claude-fable-5）；为同档新实现窗口，非091修正轮01的Codex原窗口，未创建子Agent、未使用独立审计窗口、未并行执行。A+是编排资源安排标签，本记载不将标签冒称为型号。
- 运行边界：本窗口只在项目内实施、运行本卡授权的合成资源与测试；用户库、真实provider、公开HTTP/UI、其他工具、自动循环、额度扩容、跨机恢复、Git写操作、部署均未触碰；付费额度0、网络请求0。

## 实现清单（已落盘产品改动）

迁移。backend/migrations/008_activity_tool_budget.sql：单事务；先核001—007基线并拒绝008痕迹（重复执行报错整体回滚）；activities 增 max_tool_calls（NULL或0..2147483647）与 tools_reserved（NOT NULL DEFAULT 0）及三个具名CHECK（limit/reserved/balance，NULL必须已用0、已用不超上限）；activity_operations 增 kind TEXT NOT NULL DEFAULT 'model'（值域model/tool）、arguments_sha256、tool_call_id(VARCHAR128)，放宽provider/configured_model/request_bytes/max_output_tokens非空，原成本单列正值CHECK按pg_constraint定义唯一识别后精确DROP（数量或定义不符即回滚），新增kind_domain与kind_shape总条件（model/tool双向非空、工具名单项数组、sha64小写、call_id受限ASCII、工具行禁一切模型元数据且成本=0，全部显式IS NOT NULL）；新约束当次验证既有行，不留NOT VALID。001—007未改，007正文表零新增列。

契约（capabilities/contracts.py及包出口）。新增 MAX_TOOL_ARGUMENT_BYTES=2048、canonical_tool_arguments（原Schema校验后 sort_keys=True/ensure_ascii=False/separators紧凑/allow_nan=False 的UTF8规范字节与SHA256）、parse_tool_arguments（拒重复键与非有限常量）、ToolExecutionInput（冻结、arguments_json隐藏repr；to_wire/from_wire每边界重新解析、原Schema校验、规范编码逐字节复核）、ToolIntent、ToolAdmissionPermit（admission_id/operation_id/executor_id/activity_id/execution_generation/scope_revision/tool_name/tool_call_id/arguments_sha256；不复用旧三字段模型凭证）、ToolCallStatus（succeeded/rejected/not_sent/failed/unknown，无TOOL_PLAN）、ToolCallResult、ToolAdmissionLedger协议与RejectingToolAdmissionLedger失败关闭实现。旧AdmissionIntent/AdmissionPermit/模型接口与ResultConsumptionRef结构未改。

工具适配器。capabilities/tool_execution.py 的 ControlledToolExecutor.call(context, call)：规范复核→admit_tool_operation→mark_tool_started→（仅一次）ToolRegistry.execute→record_tool_outcome；执行只从同一不可变arguments_json重建计划；错误码有限allowlist（其余拒绝收敛admission_denied）；admit/mark不确认→UNKNOWN+admission_unconfirmed/mark_unconfirmed；确定计算失败→RECEIVED+tool_execution_failed无正文；record_denied/record_unconfirmed→UNKNOWN且无成功hash。

仓储（activities/repository.py）。ActivitySpec尾部max_tool_calls=None并严格校验写入；CommittedResultSnapshot尾部增kind/tool_call_id/arguments_sha256/tool_names（NO_OPERATION全None）；_RESULT_READ_SQL与list增四字段投影（list编码含新元数据、256KiB预算不变、kind=tool且正文可读时复查工具语义）；新增admit_tool_operation（来源→活动→操作键锁序；活动running/未cancel/未过期/来源有效/executor/G/scope/租约/关门/白名单/NULL或满额拒绝先于+1；同键按kind与工具身份区分operation_key_conflict/tool_input_conflict/operation_already_exists；INSERT kind='tool'、成本0、单项tool_names并按参数规范摘要落行；tools_reserved+1同事务）、mark_tool_started（专用凭证、锁内DB行权威复核kind与工具身份，reserved→dispatched，二次mark拒绝不返回ALREADY_STARTED）、record_tool_outcome（与模型共享受控提交核心_terminal_confirmation/_write_outcome；拒not_sent与一切模型元数据；成功正文额外复查text封套内原精度规范有限十进制；终态严格等值幂等、正文三字段同存同缺、关门拒新正文、UNKNOWN诊断仅按原纪律）；模型mark/record补锁内kind=model校验且受限幂等不受代次关闭影响；模型admit在锁内对父行kind!=model返回result_kind_not_consumable；新增_tool_payload_semantics_ok与read/list工具语义复查（失败按完整性错误）。

服务（activities/service.py）。新增execute_tool_action(activity_id, operation_id, plan, config, executor_id, run_tag)->ToolActionOutcome（status/business/supervision/settlement）：身份与计划校验→调用方Mapping仅一次私有浅拷贝并规范编码（拷贝中变化或抛错即invalid_input）→同键按kind/身份只读或明确冲突（snapshot缺失时原样返回只读状态）→request_timeout>120与类型冲突在监督前早拒→asyncio.to_thread(run_one_tool)+shield有界等待（不吞合法监督结果）→业务读与回执判定；服务不claim、不execute、不settle。continue_from_result在COMMITTED_CURRENT后增拒tool父（result_kind_not_consumable、零监督）。

worker（command/one_tool/worker_main/session/launcher/supervisor_main）。WorkerCommand仅增固定枚举one_tool（argv仍仅枚举+校验过的mapping名）；one_tool.py为工具编解码与run_one_tool（外由launcher固定链，请求严格帧protocol=4精确7字段、context取SUP实际lease、大小与身份早拒、stop余量检查；回执精确5字段、result7字段kind=tool、身份/参数与请求一致、committed/unconfirmed/not_committed严格配对、缺成功hash或夹带hash即拒）；worker_main增execute_one_tool与run_internal_task的one_tool分支（ClosingCallGate包住完整call、令牌从admit前到record返回、单调截止含准入与记账、工具路径无网络无子进程）；SessionOutcome尾部增tool_receipt（默认None、repr隐藏，model_receipt在工具路径必须None）；launcher冻结外2/外3字段集（外2精确20字段排除tool_receipt并补默认；外3含tool_receipt的21字段精确集），请求按command分协议3（工具外请求精确字段、不带one_call/模型service/API key）与2（原样），成功路径对tool_receipt逐跳复核身份并调用decode_tool_receipt，settled缺业务回执拒绝；supervisor_main按protocol分派严格校验（2↔idle/one_call、3↔one_tool，混用拒绝），serializer外2弹tool_receipt外3含之。one_call.py保持原外2/内3与模型回执形状未改（本卡零修改）。

## 全部实际差异与pre/post哈希

改动16个既有文件、新增5个文件，共21项。pre原件（实施前字节）在 DocuN/evidence/TASK-092/pre/（16份+pre-hashes.txt），逐文件pre/post SHA256与行数见 DocuN/evidence/TASK-092/final-product-hashes.json，统一diff（utf-8）见 DocuN/evidence/TASK-092/final-diff.patch（76,848字符）。审计者可用 post在工作树、pre在pre/、哈希对比独立重建。

关键post哈希：008迁移 aa97942899eeb6601c82e49c3367ec3409e156b55c5758f789073d4a0df4f959；tool_execution.py 92f4f528e4aac2031bffc31857f64e59d9cecfdceaeb8dea7b425e27aa912326；one_tool.py 44339a110fedeb46832f8f57d8a8fa30286d77a3823b92905e63c35365bd4333；test_activity_tools.py fc6da4375c7615d5482feeedf5ff7165baea9d438f97b277ab3004968fe19733；test_worker_one_tool.py 1f6e3aedf54bead9f4d625fe3565d67ecd5ce5983f65df0e25b9e4748a3421c4。其余13项（repository/service/__init__两处/contracts/command/worker_main/launcher/supervisor_main/session与测试适配四项）逐项哈希在final-product-hashes.json。允许但未改：one_call.py（基线hash保持3120abbe…）；未触及禁止清单任何文件。

适配说明：test_activity_results.py 两处合成外2帧补 pop tool_receipt 与假行补投影列（形状对齐，断言未弱化）；test_activity_continuation.py 三处合成model父快照补kind='model'（真实投影必然携带）；test_worker_one_call.py 两处按冻结字段集与 _validated_request 返回元组位次适配。以上均为双版本协议/kind投影的直接影响面，原有断言语义保留。

## C1—C12证据分级与适用范围

离线（offline-02，最终测试版本绑定：93执行/93通过/71跳过，source_unchanged，hash见real目录同级 offline-02/as-run-hashes.json）。A级：参数规范化与Schema域、ToolExecutionInput伪造/非规范/重复键/额外字段拒绝、跨kind凭证、外2/外3与内3/内4帧形状与双向拒绝、工具回执真值表与夹带拒绝、服务早拒父tool与同键只读/冲突、受控执行器调用序与record不确定映射、worker固定argv与门包裹、旧Job不可判在claim前失败关闭、旧model协议离线兼容回归（test_worker_one_call/test_worker_session/test_capabilities/test_activity_results离线部分/test_activity_continuation离线部分）。Mock只证明其边界内编码与控制逻辑。

真实PG（real-01+real-03定向复验，库retrolume_task092_tools，001—008全量建于real-01）。A级通过：
- C1 迁移与完整条件约束：008应用与五具名约束/两列/kind列标记核验；六类工具行条件反例与model缺provider全被SQL CHECK拒绝；真实admit落行身份（kind/tool_names/摘要/call_id/成本0/模型列为NULL）；NULL已用1被balance拒绝、未用0可NULL回填；重复008报错整体回滚列与数据保持。
- C2 参数与凭证绑定：mark/record对异call_id与伪造摘要拒绝且事务前失败；旧三字段模型凭证操作tool行、工具凭证操作model行均锁内kind拒绝；二次mark拒绝。
- C3 权限与计数：白名单缺名/NULL未配置/零额/正额2两次/第三次与重连后拒绝；工具预扣与model请求/费用独立；已准入未mark收敛unknown不退款。
- C4 同键竞争：两连接事件屏障下唯一凭证+operation_already_exists；胜者mark后恰执行1次真实有限计算并record成功；model占键冲突；胜者崩溃样本execute 0而T1。
- C5 类型隔离：真实工具received的read/list带kind/tool元数据与正文；service与ledger.admit双拒tool父（直接构造正确scope/hash引用、allowed_tools为空，无新模型行/预留/transport）；model父对照准入成功。
- C6 admit/mark边界：COMMIT后丢响应（子类super后抛）reserved/dispatched/T1；触发器提交前失败零残留；三未决操作收敛unknown无成功正文且计数不退。
- C7 执行后未提交（real-03）：受控执行器execute=1、record触发器提交前失败→UNKNOWN/record_unconfirmed、dispatched与T1保留、无results；恢复unknown后同键成功正文不可覆盖且不能ALREADY_PRESENT；确定失败received+tool_execution_failed无正文；重领折叠一次后窗口独立结算。
- C8 record已提交丢响应：真实COMMIT后丢响应→DB received+正文、只读确认typed hash；直接同凭证等值确认ALREADY_PRESENT且xmin不变；异文拒绝；received无正文补写拒绝；json或非原精度十进制工具正文拒绝且行保持dispatched。
- C9 资格变更：CAS先提交→旧context拒scope_changed；屏障事件证明的ScopeConflict整事务回滚零预扣；admit后CAS→mark拒绝T保留；cancel一次折叠、重复cancel不重复、工具计数不动；UNKNOWN诊断可写、成功正文拒绝。
- C12目标项：close丢响应不退款（ALREADY_CLOSED确认）、settle丢响应同G/W/C一次ALREADY_SETTLED且异C拒绝、S只变一次、业务UNKNOWN与时间已结算互不冒充、工具账独立。
- 旧model定向回归：test_activity_results 03/05/16与test_activity_time_budget 01在008 schema真实通过（共享提交核心与admit/mark改动的回归面）。

真实PG部分完成：非空001—007→008（upgrade库，real-03）——001—007合法基线应用成功，在其上插入旧model received有/无正文、unknown、白名单非空、额度未配置行后执行008，第一项断言通过（操作列漂移恰为kind/arguments_sha256/tool_call_id三项，证明008提交且列集合符合合同）；其后活动行漂移断言因证据脚本快照SELECT遗漏两新列而中止，完整收尾与旧行逐字段不变、旧model生命线、重复008回滚、篡改约束失败回滚、缺前置拒绝未运行。这些是脚本缺陷，不是迁移失败。

真实Windows（real-03，1/12会话，工具库）。C10工具链一例实际执行：service→真实launcher/固定链；SUP与worker以加载hash捕获自举进程运行产品真实模块（SUP调用真实supervisor_main.main；worker经bootstrap路由到真实worker_main.main，任务argv与协议帧、账本、执行代码均不替换，仅对真实ToolRegistry.execute加计数包装），bootstrap捕获loaded_source_bytes 20项与as-run逐hash一致；执行真实finite_calculate。worker捕获tool_execute_calls=1、transport_sends=0；进程内检查依冻结脚本顺序通过至第11项（业务committed_current、监督settled、回执protocol4/committed/succeeded/身份、DB单received op与正文{"format":"text","value":"3"}与双hash一致、T1、请求0/费用0、R=0与关门、代次递增），第12项“结算秒数等式”因夹具期望误加1失败（已修正为S==C），该例不作通过。旧model外2/内3真实端到端、C11硬停止与恢复、旧SUP拒外3、旧worker拒one_tool四个方向未运行。C11的停止机制反例与恢复折叠只有代码与离线边界证据，无真实会话。

未验证与限制汇总：upgrade完整校验收尾；Windows五个场景；工具链结算等式实证；旧SUP/旧worker混用真实会话；legacy_probe正反照未运行（旧版逻辑本体已作为行为副本落盘并绑定pre哈希）。迁移真实锁与时长未另行测量（README式说明保留在008注释）。D3旧树身份、附件句柄顺序、gate/windows_job主体未改，沿090/089既有证据。

## 尝试与失败修复账（连续记账，失败原文保留）

- 批1 real-01（pg，16.6秒，exit1）：001—008全量应用与标记核验通过；17项执行，15过2败。失败原文保留于real-01：c7以“AssertionError: 0 != 1”（夹具在executor前重复准入致execute未达）、c9以“AdmissionDenied: scope_changed”（夹具未随scope修订更新T2上下文）。均属测试夹具缺陷，各做第1次有据修正，产品源码未动。
- 批2 real-02（retry_upgrade，1.8秒，预检失败按卡面计数）：runner自身 prior-manifest 解析TypeError（new_database列表不可哈希），未运行任何子批、未产生运行证据；第1次修正（列表扁平化）。容器经确认停止。
- 批3 real-03（final，7.5秒，exit1）：pg定向复验子批2/2通过（source_unchanged）；upgrade子批在活动列漂移断言因snapshot SELECT遗漏两列中止（第1次修正：快照纳入两新列并按列存在性兼容008前库；为跨批重跑加自有schema先清后建）；windows子批在“settled once”夹具期望误加1中止（第1次修正：等式改S==C；场景失败改为继续后续场景，不重试失败场景）。两处修正未复跑（批槽用尽）。
- 账目：真实批3/3、容器启动3/3、Windows会话1/12；同缺陷均未超过一次修正；无失败批被覆盖或转写为通过。

## 预算与资源状态

- 主动投入约1.5小时/8小时（自首次读取本卡连续执行，无等待时段；保守向上取整）。离线子进程累计5.3/1800秒（offline-01 2.69s、offline-02 2.64s）。真实批次3/3、累计25.9/3600秒、单批最大16.6秒。Windows受控会话1/12、单会话截止均在120秒配置内。真实模型/provider请求0、费用0、外部网络请求0。
- 容器：仅精确ID e49d3acc…，启动3次，批后均stop并核Running=false/Pid=0（real-01/02/03 manifest的final_resource与container_stopped），未remove、未新建容器/卷/镜像。合成库retrolume_task092_tools、retrolume_task092_upgrade与角色retrolume_task092_synth保留供审计；凭据仅批内内存/psql stdin/受控子进程环境，未入argv、日志或报告（日志已redact）。清理：外层Job树零、句柄关闭、active_processes为空，三次批均cleanup_incomplete=false，无残留自有进程。
- 证据目录 DocuN/evidence/TASK-092/：baseline.json（编排）、pre/、offline-01、offline-02、real-01、real-02、real-03、attempt-ledger.json（3条）、budget-manifest.json、scenario-manifest.json（含final）、final-product-hashes.json、final-diff.patch、README式夹具与runner（batch_runner/child_control/tool_pg_child/upgrade_child/win_chain/bootstrap/legacy_probe/offline_runner）。各批as-run哈希绑定产品实际加载。

## 偏差、风险与待最小决定

- 偏差：批2因runner自身缺陷浪费一个批槽（按卡面如实计数，不申辩）；两处证据夹具缺陷各耗一次修正而未复验；本卡为候选交付，不声明C10/C11/迁移收尾通过。
- 风险：已修复脚本需要至少一次新批槽复验（upgrade完整子批约1分钟；windows六场景约3分钟）；工具链结算算术的实证值（预期S=ceil(elapsed)）待复验钉死；替换型自举（hash捕获与执行计数包装、同步阻塞替身、合成transport、旧版行为副本）已如实标注，替代不了真实多样性。
- 需要的最小决定：编排批准一个沿本卡边界的续作批（不重开设计、不重置本卡账）：建议单批并入三个阶段（修复后upgrade子批+修复后windows六场景+无代码变更的收尾核对），1个批槽、约300秒即闭合剩余C10末例、C11两段与混用探针；独立增强审计在本续作稳定后再按V4另卡隔离组织，当前不满足“稳定完整成果”条件。

## 建议同步（由编排维护）

- DocuS/执行动态文档.MD：TASK-092调度记为已返回（候选）；预算与资源实数（上节）；G5实现完成、方向性真实通过C1—C9/C12目标项与旧model回归、待续批闭合剩余三项；下一可用编号与批槽建议。
- DocuS/架构动态文档.MD：G5批准包已实现（008、专用凭证、受控one_tool、外3/内4与类型隔离双层拒），候选待定向复验与独立审计。
- DocuS/文档变更记录.MD：本卡新增实现与预算事实条目（编号由编排裁定）。
- 经验候选（不入库）：夹具级教训二则（跨批重跑需自有schema幂等重置；runner预检需对既有manifest字段做类型容忍）供编排去重判定。
