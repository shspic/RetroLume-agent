# TASK-128 / R-122 连接诊断、修复候选与停止回传

连接根因已实证并最小修复，正式只读连接与两项定向离线测试通过；原预检另有带主机掩码地址文本的确定缺陷，且剩余source启动数不能覆盖原六项顺序，已停止自有资源交回，本卡整体未通过。

## 已确认的根因及实际修复

原127的连接失败不是PG不可用的证明。entry04在同一source CID、端口、库、管理员、驱动及进程环境下比较：控制连接成功；原正式连接返回psycopg.OperationalError，SQLSTATE=null，脱敏原文为`connection is bad: definition of service "" not found`。四份内存秘密逐项字节相等，仅保存相等布尔值，没有秘密摘要。正式连接另传的`service=''`被libpq作为空服务名查找，而非禁止服务配置。[连接对照](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/entry-04/connection-comparison.json)、[同秘密/版本证据](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/entry-04/credentials-equal.json)可复核。

只修改正式安装器connect：不传无效service空串，且在调用驱动前拒绝环境中存在`PGSERVICE`或`PGSERVICEFILE`，包括值为空的情况，固定错误`ambient_service_rejected`。不读取service文件、不修改进程或用户环境；host/hostaddr仍显式127.0.0.1，端口/库/用户/密码、options超时与search_path、SSL模式、原事务及身份核验均保留。没有移除环境隔离以换取成功。

entry05在同一实际库使用修后正式connect成功，原options未改变，真实查询返回同一OID/system_identifier/管理员。这与原错误共同限定了空服务参数根因，不以单纯参数记录器代替认证。[修后正式连接](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/entry-05-ready/fixed-formal-connection.json)。原观察辅助已补real_connect异常类型、模块、SQLSTATE及限长脱敏诊断，继续抛原异常；合成四用途值与DSN的安全检验在[diagnostic-safety.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/diagnostic-safety.json)。该观察辅助没有替代真实驱动或patch产品核验。

修改原test19中恰好固化缺陷的service空串断言，改为不传service；其显式host/hostaddr、恶意PGHOST/PGHOSTADDR覆盖防护、端口/库/登录/密码、options以及direct/apply/verify共用连接和合法普通NAT地址断言保持。新增test22覆盖PGSERVICE和PGSERVICEFILE非空/空值四反例，要求驱动调用0、环境不变。只集中运行这两项，2/2通过，unittest0.636秒，工具外层1.9813818秒，两层不相加；旧18/9项未重跑。[名单及结果](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/targeted-tests.json)。离线记录器不证明真实SQL/ACL，此处只验证连接边界直接影响；真实认证由上述entry05补证。

## 新的确定阻断与停止依据

entry05实际原预检返回`target_identity_mismatch`。[真实预检](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/entry-05-ready/real-preflight.json)与实际身份行可交叉核对：database/OID/system_identifier/installer/session login、PG17、UTF8、superuser均符合，服务端地址却是PostgreSQL查询`inet_server_addr()::text`实际返回的`172.19.0.2/32`。原observe_identity用`ipaddress.ip_address`，拒绝带`/32`的有效主机地址文本。对刚取得的真实行作不联网回放，同一原函数确实拒绝；独立解析确认它是完整主机掩码，而非另一个数据库或网络前缀目标。[最小复现](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/nat-reproduction.json)。回放不冒充第二次真实连接，真实拒绝来自原预检本身。

另在同一真实连接以BEGIN READ ONLY执行原EMPTY_QUERY，全部字段false：没有额外库/客户端/角色、公有表/类型/函数等，未安装vector扩展、未有PUBLIC CREATE等额外对象。[真实空态](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/entry-05-ready/actual-empty-facts.json)。这补上127仅依赖trace零写的空态缺口，但不能替代完整成功预检、安装或六项通过。

本卡产品写权限定connect参数适配及保持环境隔离的局部帮助；新缺陷在observe_identity的服务端身份格式核验，未擅自扩大为修改身份guard、SQL投影或驱动行工厂绕过检查。提供[未应用的最小修正草案](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/proposed-nat-fix.diff)：解析IP interface且只接受完整主机掩码，其他身份等式不动；该草案不是已修复或已验证的产品。

此外source已累计start3/4。即使现在修该guard，剩一次启动也不能同时满足“源安装/两API周期→停源→interrupted→停中断→回源verify”的原顺序，且最多一个PG活跃。未消耗最后一次source启动去制造不能收口的半套验证；interrupted也未再启动，因为同一原身份入口仍不可用。按任务卡范围与启动可行性停止门交回；剩余entry06和工具额度不等于额外source启动权。需要主控集中决定身份格式修复范围和至少再增加一次source启动上限，或另行明确调整验收顺序。没有请求用户重批已有普通连接修复或手工建库/删除对象。

## 六项逐项状态

原六项仍未完整通过，原TASK127失败不改写；本卡新补的是连接根因、连接修复与实际源空态。

| 项 | 本卡实际 | 缺口及导航 |
| --- | --- | --- |
| 1 空库拒绝辨别力 | 原只读空态已核；四反例未执行 | 正确配置已先命中地址格式误拒绝，不能把它算错误OID/systemid反例通过；没有创建临时表/职责组，也没有DROP探针。见真实预检与空态原件。 |
| 2 原001—015完整安装 | 未执行 | 两个本卡真实入口均只读，没有apply/DDL/DCL、17阶段或37行完整成功收据。 |
| 3 实际两登录权限 | 未执行 | 没有正式业务/快照登录的创建或认证，不将bootstrap读库冒充能力验证。原角色模型/旧独审仅继承未变范围。 |
| 4 原生API两周期 | 未执行 | API累计0/3，无normal ControlHub或来源注册、无Q读取成功事实；辅助准备代码不算启动通过。 |
| 5 interrupted/002提交后隐藏确认 | 未执行 | 原127没有真正触发，本卡也未触发；interrupted仅保留127初始化对象，不能称002提交未知库。未补签、续装、清库或重试原收据。 |
| 6 成功收据真实verify | 未执行 | 没有成功收据；本卡的直接正式只读连接/原preflight不等同verify CLI。 |

本卡没有新安装收据，原127两份intent/stopped仍只读保留。没有把控制器exit0、自报零写或旧18/9记录器结果提升为六项通过。

## 资源、规则、实际身份

接收原A+工程窗口，实际客户端Codex桌面，Codex/GPT-6家族，具体后端变体不可核读取；A+是安排标签。无子Agent、并行实现或独审。关联TASK128/R122、127/R121、125/R119、126/R120，STEP018/019/020及NFR-004/CON-002/DR-002；不自签独审、主控验收或阶段/发布完成。

已补读当前完整TASK128、permit/restored-scope/input-manifest、执行动态v2.99/架构v1.71顶部及TASK127主控work-decision；原六项、同窗公共V4.0/CHG-0003执行条款和未变依赖沿用已读内容。58输入pre全部匹配，末次仅允许四文件变化；七份规则hash仍一致。任务签发2026-10-23 08:41:22.786112+08，截止仍16:14:03.021104+08；新增实际段为08:54和08:59（Asia/Shanghai），未延长原日历。

| 资源 | source | interrupted |
| --- | --- | --- |
| CID | db709b67cc8af398edf1735b0ac6fe365898264326466b2566f904784bfef48d | 549f36f11827babea930f0338149aa3542e8ea4d3d7cceb67b54b79e25dca8e8 |
| 映射 | 127.0.0.1:55482 | 127.0.0.1:55483 |
| 库/OID | retrolume_q_first_normal / 16384 | retrolume_install_interrupted / 16384 |
| system_identifier | 7699647093882925094 | 7699647123872251942（本卡只继承旧查询） |
| 本卡动作 | 原CID只读诊断启动2次并停止 | 只读inspect，未再次启动/认证 |
| 累计start | 3/4 | 1/2 |

缓存镜像实际Id仍sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f；source实际PG170011/vector默认0.8.6。未create/up/down、拉取、构建、换名/端口/镜像、第三槽位或重置密码。原两个专有卷及bridge网络按Id/创建时刻/标签复核保留，CPU1/512MiB/pids128/restart=no/loopback/无host bind未改变。四根及originals的device/file-id/owner逐项与原127检查点一致，三个UUID沿用，没有生成新身份；源尚无成功控制行/ControlHub。

原DPAPI仅在当前用户内存解密复用，未把密文/明文、DSN、Env或完整Compose复制到证据。新异常限长、脱敏后保存；最终任务execution顶层及实际运行入口文件扫描秘密命中0，范围见post-snapshot，不扩大为整机无秘密或无流量声明。bootstrap账号未吊销，不宣称其已经失效。安装管理员没有交给应用，因为API尚未启动。

## 连续预算、失败与原件

| 项 | 原127 | 本卡新增/当前累计 |
| --- | --- | --- |
| 工具wall | 精确unknown，保守4800/10800秒 | 本卡精确unknown，保守2400/6000秒；连续保守7200/10800，包含筹备、首轮测试停滞、修正、读写和保存，不只报0.636秒。900秒保存/收尾预留纳入本卡6000管理；未用交回封存。 |
| 合并真实入口 | 3/3封存 | entry04诊断、entry05修后只读核验，共新增2，累计5/6。entry05冻结准备失败时未启动PG，保留entry-05文件，随后同一预留编号在entry-05-ready进入真实段；没有重开旧127入口。 |
| PG累计持有 | 8.117866039276123秒 | 新增13.544102430343628秒，累计21.66196846961975/1800；从start请求到stop确认计。 |
| source新增区间 | — | 08:54:17.065006—08:54:24.969621，7.90461444855秒；08:59:48.581147—08:59:54.220635，5.63948798180秒。 |
| PG/API启动 | source1、interrupted1、API0 | 累计source3/4、interrupted1/2、API0/3；API持有0/900。 |
| 新create/卷/网络 | 原各2 | 本卡新增均0，旧对象全部保留。 |

本卡工具可证下界包括实际诊断工具9.6043323秒、实际修后核验6.8658649秒、通过定向测试工具1.9813818秒等不重叠调用，合计至少18.45秒；这不是精确总计。首轮测试等待与其他准备/读写未因此被写成0，保守占用覆盖这些未完整计时段。父/子和测试/外层工具不重复相加。

约2秒采样：entry04最低314.30078125MiB，entry05-ready最低1215.671875MiB；启动前实时>=512MiB门通过，未出现连续两次<256MiB压力退出。314MiB是运行中样本，不谎称全程>=512或把它改成2GiB门。各实际入口有内存、持有、日历和停止逻辑，诊断离线修码时PG停止，未同时运行两PG。

新增全部失败和修正列入[failure-ledger.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/failure-ledger.json)：复制辅助保留旧permit日期导致prestart FileNotFound、已存在合成证据导致排他创建失败、首轮定向测试长时无完成输出后中断、受限CIM不可读、entry05准备hash尚未保存、两次无写入文档编辑失败。它们没有被删改为成功。首轮测试停滞根因unknown；改为明确新execution/offline测试根及10秒faulthandler后两项成功，不据此武断认定旧临时目录故障。中断后仅对本卡完整脚本路径匹配的CIM只读查询无残留进程，未结束他人程序或清理旧scratch/Temp。

两个真实入口的as-run辅助副本和原始安全结果分别保留entry-04、entry-05-ready；entry-05保留未过冻结门的准备副本。原127全部证据/结果/检查点/许可只读，旧125/126unknown保守投入及120根64/64、149失败、117旧81等历史账不清零。

## 稳定候选、停止核验与交接

产品变化只在四份允许文件：connect服务选择防护、test19直接断言更新/新增test22，以及README和normal-install说明。完整pre/post/hash和[changes.diff](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/changes.diff)可供集中增量独审。说明明确当前真实安装仍被NAT格式拒绝，没有宣称六项通过；SQL/manifest/角色/profile/业务/原配置schema/启动器/Compose/依赖锁未改。源目录的旧规则和原始需求未写入。

最终[post-snapshot.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/post-snapshot.json)核两个精确CID均Running=false/Pid=0、卷/网络/根保留、所选PG与API候选无LISTEN；API PID树未创建。没有prune、删卷/网络、DROP DATABASE、角色重置或递归清理。新source实际空态留证，interrupted内容未重新查询，仍按旧事实保留。

供主控的最小下一步是集中核本连接增量和原始对照，处理已给出具体未应用diff的身份格式缺陷，并明确后续source启动总上限/验收顺序。本工程不能自行把4次改成5次，也不将修改身份函数暗藏在连接参数修复中。没有新增要求密钥、账单、截图、释放内存或手工Docker恢复的用户动作。正式DocuS/唯一进度账由主控登记本卡部分成果和六项仍未通过。

Q保持FROZEN，T0/72h为空；本卡provider/Embedding/计量/费用、业务Job、浏览器/renderer/预览、索引/查询/生成、固定三活动、grant/QAuthority.bind/InstanceBinding和Git写均0。原100次/25元及48/28/24等分额、账号/token/模板/容量外部缺口不改。本连接候选及原有限独审结论不放行Q、STEP018/019/020、M1、项目或发布。
