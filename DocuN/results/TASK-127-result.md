# TASK-127 / R-121 首次正常安装真实验证结果

本卡未通过：两个新槽位已创建并各启动一次，但正式安装器均在真实连接调用处停止，六项验收未完成；三个合并入口已用满，两容器已按精确CID停止，原对象、失败收据和全部证据保留，Q和付费继续关闭。

## 六项结果与原件导航

证据根为[D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-127/execution/](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-127/execution/)。本报告不自签验收，不裁定STEP018/019/020、M1、发布或项目完成。

| 检查 | 实际状态 | 预期与观察 | 原始证据 |
| --- | --- | --- | --- |
| 1 空库拒绝辨别力 | 失败，仅执行首个错误OID输入 | 应真实连接后拒绝`target_identity_mismatch`；实际CLI退出2，`installation_stopped`，观察到一次连接请求、无连接返回事件、安装写请求0。错误system_identifier、非空表、职责组碰撞尚未执行；未创建或DROP这两个探针对象。 | [command-009.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-127/execution/entry-03/command-009.json)、[source trace](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-127/execution/entry-03/source-wrong-database_oid-trace.jsonl)、[停止收据](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-127/execution/entry-03/source-wrong-database_oid-receipt.jsonl) |
| 2 原001—015完整安装 | 未执行，被1阻断 | 没有源成功安装、37行完整收据、17阶段提交或R01/R02/R03实际推进。不能复用离线结果宣称通过。 | [最终检查点](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-127/execution/final-checkpoint.json) |
| 3 两登录及权限 | 未执行，缺少成功安装 | 新业务/快照登录仅有卡面计划和本地配置；未实际创建这些登录，未认证或验证其权限，不将bootstrap观察冒充登录能力。 | 同上 |
| 4 原生启动、停止、同库重开 | 未执行，缺少成功源 | API启动0次；没有ControlHub、正常源注册或原生来源绑定通过证据。关闭配置/启动准备代码没有实际运行，不能算loader验证。 | 同上及[本次as-run](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-127/execution/entry-03/as-run.json) |
| 5 独立002提交后隐藏确认 | 失败，未到注入点 | 为避免源故障阻塞独立项，source停后真实尝试interrupted。实际同为`installation_stopped`，连接请求1、返回事件0、写请求0、注入次数0。未执行001/002，未产生预定提交未知。两个停止收据均只有intent和stopped，confirmed=[]、unknown_stage=null。 | [command-015.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-127/execution/entry-03/command-015.json)、[interrupted trace](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-127/execution/entry-03/interrupted-expected-unknown-trace.jsonl)、[停止收据](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-127/execution/entry-03/interrupted-expected-unknown-receipt.jsonl) |
| 6 源成功收据只读verify | 未执行，缺少成功收据 | 没有正常verify、错误绑定拒绝或收据不变的真实验收；没有为复验重放安装。 | [最终检查点](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-127/execution/final-checkpoint.json) |

两个停止收据都不是完整成功收据，也不是“002实际提交后未知”的验收证据。没有补签、从库状态推断迁移成功、自动继续或用新收据重试。保留的interrupted槽位是新PG初始化后的失败安装目标，不能称为已达到002边界的部分安装库。停止后没有再次连接数据库，因此不额外声称已经独立核验全部表/角色为空。

## 真实失败、修正和停止依据

1. 首次筹备入口：受限令牌访问Docker named pipe被拒；获平台宿主访问后，同一客户端`info`仍返回`/v1.55/info` HTTP500，外层进程退出0但门未通过。随后同客户端`version`25秒超时，退出124/包装脚本退出1；当时尚未创建或启动资源。[首次version](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-127/execution/docker-version.json)及[筹备失败账](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-127/execution/preparation-failures.json)保留。用户回复“恢复引擎后继续本卡”，未将该回复直接当引擎可用事实。23:55:49Z同客户端有界复核服务端恢复为Docker29.7.2/API1.55，见[recheck](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-127/execution/docker-version-recheck.json)。未重启宿主Docker服务、换客户端、修改API版本或拉镜像。
2. 第二入口筹备时，受限令牌的原生`GetExtendedTcpTable`返回errno5，保存失败后，以相同原生查询取得平台宿主访问并成功；这是平台读取权限差异，没有改网络/端口/他人进程。新辅助代码AST、导入、非凭据DPAPI往返、当前SID、根实体、候选端口和41输入检查见[prepare-check.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-127/execution/prepare-check.json)。这些只属于控制器准备，不冒充六项通过。
3. 第二入口实际控制器在资源创建前失败：辅助层只匹配`No such`，Docker卷返回小写`no such volume`。定向只读检查确认指定容器、卷、网络均不存在，见[原始诊断](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-127/execution/slot-gate-diagnosis.json)。保留[entry-02实际代码](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-127/execution/entry-02/run-six.py)，仅改辅助层为大小写不敏感匹配并保存stderr，已有或未知对象仍拒绝。另在创建前核查中补全网络身份：未启动容器可暂为空NetworkID，网络自身的不可混淆Id必须来自新项目bridge实际inspect，运行时要求相同Id。[修正依据](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-127/execution/entry-02-failure-and-correction.json)完整保留；没有改产品或SQL。
4. 第三入口是最后定向续验，六项此前均未实际执行。两个槽位创建、版本/身份查询及精确停止成功。控制器以真实psycopg连接查询到了两库身份；但正式安装器的真实连接调用均未产生返回事件，最终被原工具归一为`installation_stopped`。观察包装器保留了host、hostaddr、端口、库及登录白名单，但未保存真实连接异常的脱敏类型/SQLSTATE；因此根因尚未判定，不能认定是产品、权限、密码、service参数或旧F126的回归。也不能把顶层控制器退出0当验收通过：其最终JSON明确包含两失败、四阻断。

按[任务卡](D:/shspic/project_NO3_RetroLume-agent/DocuN/tasks/TASK-127.md)“最多一个合并初验入口加两次……定向续验，共3入口；入口/准备失败仍记账”和“根因不稳……停止受影响段”停止新增验证。独立第五项已按串行边界尝试；其失败后没有剩余可独立完成的安装验收项。本卡没有第四入口，剩余PG/API启动和工具额度不能替代合并入口额度。

后续需由主控处理本TASK/R的明确增量范围和额度后再转卡，不要求用户手工建库、删除对象、提供密钥或再次恢复当前已可用的引擎。优先在既有两个同身份对象上定位正式连接与控制器连接的差异；保存脱敏真实异常，产品/SQL仍冻结，不能凭本报告直接获得续跑许可。若后续证据确证产品差异，再交主控决定增量修复/审计。本报告不擅定根因或提前关闭缺口。

## 接收、规则与继承

- TASK127/R121关联STEP018部署前置、STEP019权限证据、STEP020本机交付；原TASK125/R119和TASK126/R120只沿用已验收工具、有限离线证据及独审结论。原18项及修复批9项均未重跑。现有`evaluate`保存`progress.reason`的已确认语义不改动。
- 执行身份为Codex桌面中的Codex/GPT-6家族编码Agent；具体后端变体没有可核读取途径，未用A+冒充实际型号。无并行工程、子Agent或新独审。
- 用户人工转卡请求及本窗口接收有效；本卡接收前置核验记录2026-10-22T23:32:11.270235Z，即2026-10-23 07:32:11+08。许可签发2026-10-22 16:14:03.021104+08，截止2026-10-23 16:14:03.021104+08；真实入口3结束08:03:19+08，未跨截止。
- task_model，锁定V4.0/公共AGENTS CHG-0003，需求v1.4、架构v1.70、执行动态v2.98。最小执行规则和卡面输入按同窗口已读部分复用，开头及最终均核41冻结输入、七份规则字节；全部一致。当前采用包的授权依据为AP-125-NORMAL-INSTALL-01新回执/permit，旧草案adopted=false仍是历史事实。
- TASK125精确工具unknown/保守4200秒/10800秒、3/4批封存；TASK126精确unknown/保守2400秒/3600秒封存。TASK120根64/64及149失败、117旧81等历史账不清零，不挪为本卡余量。旧报告、卡、采用包和归档均未改写。

## 对象身份与配置

仅使用缓存`pgvector/pgvector@sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f`，真实镜像Id相同。实际查询两库server_version_num=170011、vector默认0.8.6。只执行正式Compose的pg服务create，pull never/no-build；CPU1、内存536870912、pids128、restart=no、唯一专有卷挂载、127.0.0.1映射。未启动renderer、整栈up或host网络。

| 对象 | source | interrupted |
| --- | --- | --- |
| 容器 | retrolume-q-first-normal | retrolume-install-interrupted |
| 精确CID | db709b67cc8af398edf1735b0ac6fe365898264326466b2566f904784bfef48d | 549f36f11827babea930f0338149aa3542e8ea4d3d7cceb67b54b79e25dca8e8 |
| PG映射 | 127.0.0.1:55482→5432 | 127.0.0.1:55483→5432 |
| 实际数据库 | retrolume_q_first_normal | retrolume_install_interrupted |
| OID | 16384 | 16384 |
| system_identifier | 7699647093882925094 | 7699647123872251942 |
| bootstrap登录 | retrolume_source_bootstrap | retrolume_interrupted_bootstrap |
| 保留卷 | retrolume-q-first-normal-data | retrolume-install-interrupted-data |
| Compose项目 | retrolume-first-install-source | retrolume-first-install-interrupted |
| bridge Id | 2f79fb05977e79f3fa89791f4a97553334be384ba6df89ecd0dc650c2018adb2 | c333276027ca367edf8086eec15763185fe2800f66c820792e7ad96cb842d610 |
| dataset_id（本地配置） | 6f283260-33d0-4465-bbcd-b29e50f57aab | c33c6969-e725-4c85-8505-54782c82f635 |
| instance_id（本地配置） | 4236ae70-6718-4141-9b6d-694c95b0fae4 | a454416e-8cba-4335-8be6-37d0444e2bb9 |
| originals_root_id（本地配置） | acde4327-a170-4a8d-97e9-1bcafbf28efc | 15358f69-d76a-41ce-9e08-f5b0ffe97b54 |

OID相同不构成同库证明，CID/system_identifier/卷/根联合区分。三个UUID只生成一次并与新根实体一并入账；安装失败，尚未写入成功控制行，也没有ControlHub控制身份。源成功库和002未知提交库的身份验收均未达成。

新私有根为D:/shspic/project_NO3_RetroLume-agent/.runtime/normal-first-install/source及对应interrupted；首次创建前均不存在。分别创建data、backup、control、restore四个独立根以及data/originals、config、receipts。创建前核父链reparse，真实device=1031070048549017791，当前SID/根owner均为S-1-5-21-1598749804-2478933926-3421301008-1001。各file-id、卷/网络创建时刻、固定候选端口依据及创建前计划在[源身份](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-127/execution/entry-03/source-created-identity.json)、[中断身份](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-127/execution/entry-03/interrupted-created-identity.json)和[最终投影](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-127/execution/post-snapshot.json)可核，收尾仍相同。没有枚举或读取旧runtime/scratch私配。

四份秘密每槽位独立随机生成，通过明确子进程环境引用；不写JSON/argv，私有根仅存当前用户DPAPI加密二进制。Docker完整inspect仅在内存取白名单，证据未输出Env/完整Compose。最终对本卡execution文件及自有新config扫描真实秘密，命中0；不扩大为整机无秘密证明。bootstrap账号未重置或吊销，容器已停止，不能宣称账号已经失效。应用尚未启动，因此不存在实际继承安装管理员DSN的应用进程。

## 累计投入、启动与持有

| 项目 | 实际累计/保守占用 | 本卡上限与说明 |
| --- | --- | --- |
| 合并入口 | 3/3 | 入口1筹备引擎失败；入口2预建辅助门失败；入口3两实际连接边界失败。只读诊断和最终收尾没有新增安装/服务验证入口。 |
| 每槽位create | source1、interrupted1 | 各最多1次；没有再次create、换名或第三槽位。 |
| 容器/卷/网络 | 2/2/2，全部保留 | 两个Compose bridge均有新建身份账。 |
| PG启动 | source1/4；interrupted1/2 | 总2次；最多一个PG运行，无并行重叠。 |
| API启动 | 0/3 | 无API PID树，无API端口选定或原生服务生命期。 |
| PG保守持有 | 8.117866039276123秒/1800 | source4.3092648983秒，interrupted3.80860114098秒；从start请求到stop确认的外层区间，不只计SQL耗时。 |
| API持有 | 0秒/900 | 尚未启动。 |
| 工具wall精确总计 | unknown | 本窗口早期读入/工具外层与子进程部分重叠，无完整精确账，不编造精确总和。 |
| 工具可证下界 | 至少63.90秒 | 取不重叠的首次version25.0546015秒、恢复version4.2541763秒、第二控制器10.875秒、第三控制器16.062秒、两次原生准备5.6421773/1.4004092秒和定向Docker诊断0.6145544秒；其余读写/筹备/保存未据此漏称0。 |
| 工具保守占用 | 4800秒/10800 | 筹备预留4200秒，另600秒保守覆盖控制器、诊断、读取、最终核验和报告保存；900秒保存/收尾总预留纳入本卡管理，未以测试秒数代替工具投入。未用额度交回封存。 |
| 费用/真实provider | 0元/0次（限本卡） | 没有模型/Embedding/计量入口、业务Job、浏览器或renderer启动。 |

控制器第二入口约2秒采样6次，最低1084.57421875MiB；第三入口8次，最低749.0625MiB。每次PG启动均先实时核>=512MiB，未出现两次<256MiB或压力退出；PG/API持有、日历和保存储备门均有辅助代码。准备时可用内存2775.3828125MiB的记录不能代替启动前实时门。最终只读停止核验未启动PG或API。

实际命令、退出码及子命令wall分列在entry-02/command-001—002和entry-03/command-003—016。控制器父/子重叠不重复累加。入口3顶层退出0只表示按设计收集失败并收尾，不表示六项通过。最后停止投影核两个CID Running=false/Pid=0、ExitCode=0；选定PG端口及API候选均无LISTEN，API从未创建进程。只停止自有容器，没有prune、compose down、删卷/网络、DROP DATABASE或递归清理。

## 最终字节、交付与仍缺事实

[pre-snapshot.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-127/execution/pre-snapshot.json)和[post-snapshot.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-127/execution/post-snapshot.json)确认41冻结输入及七规则均未变。安装器仍29403字节、SHA256=68d7b71fc7296111e894df4cba21a4ed7830f9cff069c1fc500dfbd7734c0a09。原迁移、配置schema、职责组/profile、后端业务、正式启动器和Compose均未改。新辅助代码及两轮as-run副本只在本卡execution，未成为产品运行依赖。

README.md与deploy/normal-install.md原字节保留于pre/post，允许文档diff为空。由于真实验证失败，没有把“正常部署已验证”写入用户说明。正式DocuS、唯一状态账、架构、需求、旧任务与旧结果均未维护；主控需要登记本卡未完成、实际创建的两个停止对象、3/3入口和连接边界缺口。

原始收据在两个私有根各自receipts下，与证据副本原字节/hash相同；后续仍须保留，不可覆盖或伪称完整收据。最后证据清单、停止对象白名单、根实体、41输入、七规则、收据hash、秘密扫描与端口观察均在post-snapshot。控制器恢复检查点只记录本卡事实，不是新的迁移平台或状态账。

Q保持FROZEN，T0/72h未起；100次/25元及48/28/24分额、28Must/89动作/24片段/6索引的既有口径不改。本卡没有新增账号、token、模板、Embedding容量外部事实，没有grant、QAuthority.bind或InstanceBinding。原有限工程/独审通过部分仍按其适用范围继承，不能替代此次失败的真实连接、安装、ACL和启动证据。
