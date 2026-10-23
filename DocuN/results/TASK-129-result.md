# TASK-129 / R-123 两处安装修复与前三项真实证据集中独审结果

代码轴可通过本次两处增量审查，未发现新增确定功能或安全缺陷，另有一项非阻断P3注释语言偏差；证据轴可采纳正确预检及前三项限定真实事实；控制轴本轮身份、容量拦截和精确停止可核，完整历史工具投入仍为unknown，第四、五、六项仍为not_run，本报告不关闭TASK128或放行STEP019、Q及项目。

本轮为TASK129/R123，关联TASK128/R122、TASK127/R121及TASK125/126，涉及STEP018部署前置、STEP019适用安全证据、STEP020本机交付及NFR-004、CON-002、DR-002。需求v1.4、架构v1.73、执行动态v3.01取自本卡合同，没有读取共享文档验收段或维护共享状态。项目根为D:/shspic/project_NO3_RetroLume-agent，入口为该根AGENTS.md，模式task_model，锁定V4.0及公共AGENTS CHG-0003。

客户端为Codex desktop，平台身份GPT-6，具体后端变体未核实；A+为本次资源标签。本聊天可见上下文未参与TASK127/128实现、修复、测试设计或工程自评，也未接收其完整聊天和思考。原TASK126旧聊天上下文在本次不可见，不能声称恢复了那份对话；本轮在当前独立审计上下文接续，按保存的TASK126结果和指纹复用未变SQL、角色/profile及目录保护范围。没有派生子Agent、并行工程或模型切换，没有重置原126或工程旧账。

已读根入口、公共AGENTS全文、WORK的task_model合同及必要委派、审计、接续、核证、停止条款、本卡、127/128完整适用合同、输入和原件索引、必要源码及直接依赖。公共规则与锁定快照的七项指纹相符；仅实际读取必要正文，不假称已通读七份文件或加载主控阶段提示词。本轮没有读取原始需求或完整共享历史，卡面已给本次必需目标和约束。

独立性披露一项元数据范围误读。首次标准库分析统一计算entry06 as-run输入hash时，误包含TASK-128-work-decision.md，仅读取字节计算长度和hash，没有解码、显示、搜索或引用其正文，只接触路径及hash。首次分析因此把这个运行后更新的非产品文件误判为冻结漂移。原方法与结果保存在[static-crosschecks-01.py](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-129/audit/static-crosschecks-01.py)和[static-crosschecks.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-129/audit/static-crosschecks.json)，时点见其中at；修正方法不再读取该项。TASK128结果也仅核身份hash，没有打开正文。未取得上述自评或主控结论的语义内容，不以它们支撑本次判断；不能将这项误读省略为从未接触其文件。

1. 对象稳定性和独立差异

首轮对input-manifest、raw-evidence-index及permit明确引用的127项身份逐一核大小/hash，全部相符，其中含41个产品、8个两轮pre副本、2份原合同、7份规则和63个原件引用，包含重复身份引用。完整逐项值见[input-integrity-start.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-129/audit/input-integrity-start.json)。补充读入及原件交叉核对见[static-crosschecks-02.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-129/audit/static-crosschecks-02.json)，其81项均为静态元数据、JSON或AST检查，不是81项产品测试。

当前安装器29865字节，SHA256为7cd62b4f3526510c6f38de2a033a01d6ae36bcd661e90dbaca6b551db8141ba8。测试35468字节，SHA256为2357a7031d2da858224d75b56ee0173a3166b0ca68c6905994009b7e64e6b3c3。固定安装清单hash为f2ed126daa1c5a982b490a9343d6c17053c0f385e7a2f55676ecf4132dd2abf0。41项均与当前审计冻结清单相符，没有产品源码漂移。

独立从两轮pre和当前原字节重建[连接修复差异](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-129/audit/repair1-independent.diff)、[地址修复差异](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-129/audit/repair2-independent.diff)及[最终合并差异](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-129/audit/combined-independent.diff)。产品AST仅connect和observe_identity变化，其他函数、类及模块数据不变；测试仅test19适配已证实的坏参数，并新增22/23。未仅凭作者列出的函数名认定范围。

最终合并diff去掉文件头和换行编码后与提供件逐hunk相同。两份工程分轮diff的README区各有8个CRCRLF，文本分行会多出裸空行；保留该观察，忽略这些包装空行后内容亦相符。原始证据未改写，定位见[diff-packaging-clarification.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-129/audit/diff-packaging-clarification.json)。这不构成源码漂移。

entry06的73项as-run输入中，两份用户说明在运行后作了合同允许的事实更新，TASK128结果为合同明确说明的置顶追加。前两项的实际diff已核，后一项只保留阶段性报告hash差异，不读正文或冒称已另行验证其历史后缀。主控work-decision从审查对象排除。9份三阶段helper as-run副本均与其所记hash/大小相符。当前驱动四份原审源码指纹也与126保存值相同，已安装包元数据为psycopg 3.3.5，见[diff-driver-baseline.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-129/audit/diff-driver-baseline.json)。

2. connect安全与兼容结论

[connect第321行](D:/shspic/project_NO3_RetroLume-agent/deploy/initialize_normal.py:321)在导入驱动及调用psycopg.connect之前，以环境键是否存在拒绝PGSERVICE、PGSERVICEFILE，包括空值，不读取service配置，也不修改环境。load_config第156行仍限定host为127.0.0.1；实际驱动参数仍显式传同一host和hostaddr，以及精确端口、库名、安装登录和安装密码。connect_timeout=3、autocommit、dict_row、sslmode=disable及search_path/statement_timeout/lock_timeout/idle超时选项均保留。

当前驱动get_param先取显式参数，_conninfo_attempts在已有hostaddr时直接保留该地址；conninfo_to_dict及make_conninfo保留显式kwargs，不丢弃空串service。移除service空串并在驱动前拒绝环境service选择，既避开真实空服务名失败，又保留目的地址隔离。PGHOST/PGHOSTADDR不能替换显式loopback。apply、verify及直接调用仍共用这一个connect；没有新增DSN回退、凭据来源或全局环境纠偏。

真实根因证据由[credentials-equal.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/entry-04/credentials-equal.json)、[connection-comparison.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/entry-04/connection-comparison.json)及其diagnose.py共同支持。同一进程环境、同一目标和四份秘密字节比较相等，控制连接成功取得source身份，原正式连接报psycopg.OperationalError及空服务定义不存在，SQLSTATE为空。修后[fixed-formal-connection.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/entry-05-ready/fixed-formal-connection.json)真实认证成功，原options仍在，后续entry06又实际完成apply。此组合足以定位已修正根因，不需要再真实复现旧失败或连对手服务。

公共CLI仍只输出固定InstallError码或通用失败，不渲染驱动异常、kwargs或密码。观察器第41—54行捕获真实异常，按本次四秘密、实际password及其编码形式先替换，再移除URI形式DSN并限长700，保存异常类/模块/SQLSTATE后原义重抛。合成安全原件保存了四值和DSN被替换的结果；实际空服务异常亦保留了诊断。未发现本次真实诊断泄密或把故障吞成成功的证据。这只支持当前观察器和本次秘密形式，不扩称任意第三方异常文本的通用脱敏证明。

结论为本次connect增量的功能与安全目标可采纳，原F126-01显式地址保护保持。这里没有将旧126对旧connect的结论直接迁移给新代码。

3. observe_identity及三项定向测试

[observe_identity第286行](D:/shspic/project_NO3_RetroLume-agent/deploy/initialize_normal.py:286)只将ip_address改为ip_interface并核prefixlen等于该地址max_prefixlen，裸IPv4/IPv6及完整/32、/128主机形式可用，短前缀和非法地址拒绝。返回的server_address/server_port仍为原始行值，没有改SQL投影、强制loopback或重新序列化掩码。

database/OID/system_identifier/installer与session login等式、superuser、PG17、UTF8、server_port精确int类型及范围检查未变。客户端127.0.0.1:55482与实际服务端172.19.0.2/32:5432的NAT差异合法。verify第497—499行仍要求当前观察字典与成功收据原观察值相等，不因新增兼容而伪造相等。

三层证据分别成立。entry05真实认证行含172.19.0.2/32，原preflight真实拒绝；nat-reproduction明确为该行回放且没有新增连接，属于B/D佐证；entry06的[correct-empty-preflight.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-01/entry-06/correct-empty-preflight.json)才是修后正式正确预检的A类原件。未将回放计为另一次真实运行。

[测试第471—556行](D:/shspic/project_NO3_RetroLume-agent/backend/tests/test_normal_install.py:471)的19会拒绝原service空串坏行为，并继续检查direct/apply/verify三用途、显式hostaddr和秘密、选项及环境不变。22对两个service键各测空/非空，要求固定拒绝码、驱动零调用和环境原样。23覆盖实际/32、裸IPv4、裸IPv6及/128，非法地址、短前缀和越界掩码拒绝；随后恢复合法/32再分别改错OID/systemid/登录等身份，避免格式先失败导致错身份断言假绿。

[targeted-tests.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-01/targeted-tests.json)与其实际运行脚本对应，历史集中批为3方法、0失败、0错误，前后安装器/测试hash与当前相同。test19使用Recorder及核验替身，22/23为定向控制流测试，不能证明真实PG认证、迁移或ACL。其原安全断言未被削弱；本审计没有重新运行这些方法或旧18/9项。

结论为地址格式修复满足本卡边界，未发现需扩大协议、平台或身份模型的新确定问题。原server_major类型观察及受信父目录并发替换条件风险按126范围保留，没有新增触达事实或新的硬门。

4. 前三项真实事实的可采纳范围

第一项可采纳。entry06的command-026—029均exit2，分别对应错误OID、错误system_identifier、非空表和职责组碰撞，原因依次为target_identity_mismatch、target_identity_mismatch、target_not_empty_or_exclusive、global_role_collision。四份trace均真实connect_requested/returned，各1连接、0安装器写请求；四份拒绝收据均仅intent/stopped、confirmed为空、unknown_stage为空。不是四次统一installation_stopped或other_clients拒绝。

[实际控制器第315—351行](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-01/entry-06/run-six.py:315)先证对象不存在，创建public.retrolume_install_probe_nonempty后记录OID16385，关闭旁观连接才调正式apply；撤销前锁表并核同OID。碰撞组retrolume_data_app为NOLOGIN，创建OID16388，亦在连接退出后调用apply并在撤销前核同OID。最后核public表为空再安装。正式安装后的同名职责组OID17362，与临时16388不同，没有把后来的正式职责组当临时对象删除。对应实际返回及OID原件为[check1.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-01/entry-06/check1.json)。

非空trace未逐字段保存EMPTY_QUERY返回值；故不声称有该时点other_clients=false的独立数值日志。专有目标、调用前已退出的旁观连接、指定表的创建/精确撤销流程，以及其他三种可区分拒绝和随后真实成功预检/安装，共同支持本次非空反例的预定原因。这是证据粒度限制，不将其升级为必须重跑的缺口。

第二项可采纳。command-030使用正式产品CLI、真实psycopg连接和原SQL。as-run观察器第171—182行从固定清单读取原字节，仅在真实驱动外包观察；execute转交原SQL/params，Cursor转交真实nextset/status，原schema_checks/q_roles及verify_installed没有被Recorder、改SQL、删guard或核验替身替代。

[source-success-trace.jsonl](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-01/entry-06/source-success-trace.jsonl)有82行。15个original_migration_submitted依001—015原次序，各有实际结果耗尽、final_status=COMMIT、transaction_status=0、commit_observed=true；另有normal_control及login_roles两个真实事务返回。第37行观察013刚提交时控制行尚为空，随后第40行normal_control实际插入normal/R01；第43、46行分别为014/R02及015/R03，属于设计中的完整顺序，不把013刚提交时的空行冒称R01。

[成功收据](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-01/entry-06/source-success-receipt.jsonl)逐行核为intent、preflight、17对submitted/confirmed、complete，共37行；阶段次序及固定15份迁移hash与当前manifest相同。trace第6、60行真实管理员身份与收据观察相符，保留172.19.0.2/32。最后原schema及角色校验均沿正式调用执行，command-030 exit0与17阶段输出仅作交叉支持，没有单独以exit0或installed代替成功证明。

本轮额外只对原command-030精确指定的单一非敏感私有收据做hash。完整父链无reparse，未读取同目录配置、DPAPI或DSN；私有原件、证据副本及checkpoint三者hash均为a2211aa56f0497ef55e2ff42f4ea2e6b3b50bb3049cca62cbd5ef06844df6f06。具体路径与安全父链在static-crosschecks-02.json。本次没有取得数据库查询许可，也没有查询实时数据库。

第三项可采纳。[check3.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-01/entry-06/check3.json)记录业务current_user=session_user=retrolume_normal_app、PID45，以及快照retrolume_normal_snapshot、PID46，与安装管理员PID44分离。两者实际读取相同normal/R03导出控制视图，维护摘要列读取权限均false；业务activities INSERT能力true，快照false。

两个实际连接均执行原ROLE_CAPABILITIES/MEMBERSHIPS及check_role_capabilities。保存的6条登录成员边为业务5组、快照1组，INHERIT=true、SET/ADMIN=false；静态重算可达角色不含owner或管理能力，登录无superuser/建库/建角色/复制/bypassrls、对象/definer所有权及control/schema/database管理权。业务SET owner实际42501一次；快照SET owner、SET业务、读维护列和INSERT实际42501四次，每次ROLLBACK。辅助层没有其他成功业务测试写入，因此支持没有持久化业务测试记录；未另做全库表计数或声称全部业务表已由本审计实时查询为空。

以上采纳仅限该source、该冻结对象及当次实际行为，不扩称整个权限矩阵、API运行、跨重启或成功收据正常verify通过。

5. 身份、容量、停止及历史控制账

source固定CID为db709b67cc8af398edf1735b0ac6fe365898264326466b2566f904784bfef48d，127.0.0.1:55482，库retrolume_q_first_normal，OID16384，systemid7699647093882925094。interrupted固定CID为549f36f11827babea930f0338149aa3542e8ea4d3d7cceb67b54b79e25dca8e8，端口55483，库retrolume_install_interrupted，OID16384，systemid7699647123872251942。本轮中断槽位没有重新连接。没有因为两个库OID同为16384混淆来源。

已将127原final-checkpoint与128本轮checkpoint的CID、端口、bootstrap、三个UUID、五个根实体、数据库身份、创建投影、卷/网络身份、Windows SID及create次数逐项比较，两槽位各12类字段全部一致，见[original-identity-chain.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-129/audit/original-identity-chain.json)。entry06前置检查、command-021—024的卷/网络inspect、source-running-identity-4及最终停止投影互相对应。CPU1/512MiB/pids128/restart=no、原卷、单bridge及loopback映射保持，没有换资源身份或重建根。

续作许可签发09:33:10+08:00后，entry06于09:39:56进入，累计入口5→6，未使用仅有条件的entry07。source累计3→4，start请求09:39:57.935398，停止确认09:40:10.412059，本段持有12.476661205291748秒；累计PG持有为34.1386296749115/1800秒。interrupted仍1/2，API仍0/3、持有0/900，两个新场景均在计数增加前被门阻止。

[memory.jsonl](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-128/execution/continuation-01/entry-06/memory.jsonl)共8样本，间隔约2秒。最低105.33203125MiB发生在09:40:02，下一样本为336.08203125MiB，连续低于256的最大长度仅1，未满足连续两次压力退出条件。source启动前相邻样本大于512；guard实际另调GlobalMemoryStatusEx，精确启动门瞬时值没有落盘，不能把邻近样本冒称它的精确值。

API失败时点09:40:09.387590和第五项失败时点09:40:10.569830均为startup_memory_below512。api_once第426行在Popen、API端口选择及计数前检查；start_pg第238行在interrupted start、计数和区间创建前检查。故应表述为容量启动门拦截，产品/API/002场景均未启动，不能称产品启动失败或002注入失败。没有把一次低于256误写成连续压力退出。

command-031只停止精确source CID；随后两份source停止和interrupted停止投影均Running=false/Pid=0，后者StartedAt/FinishedAt保持原127时点。09:42:57的post-snapshot记录选定PG端口无监听、API从未启动。它支持那个历史时点的停止/端口事实，不是本审计实时检查或全宿主清场证明。卷、网络、库和全部收据保留；本轮命令及实际分支没有新create、重置角色密码、DROP DATABASE、删卷或付费操作，只有已授权两临时SQL对象在成功安装前精确撤销。

完整工程工具wall继续unknown，保守累计8400/10800、余2400封存；入口6/7、source4/5、interrupted1/2、API0/3等均沿用，不由本审计恢复。原125保守4200/10800及126保守2400/3600、原127保守4800和128首轮/续作的连续账不重算为精确值，也不挪用余额。

原历史Docker API500/超时、受限读取、夹具路径和大小写错误、目标测试未完成后中断、freeze准备失败及其已记录修正继续保留。126指出的旧批失败、中间版本完整副本不足和平台原审批回执缺口亦保持原结论。本次真实新证据不能倒签这些旧控制合规；现存短命令/局部计时不能组成全程精确工具账。新证据未呈现需要新增判断的明确历史越权事实，但也不足以证明全部历史控制通过。

Q保持FROZEN、T0/72h空和本轮provider/费用0有合同、关闭配置及实际执行分支支持；未查整机或账号后台，不将自报0升级为全平台零调用证明。100次/25元及原分额、外部门事实均未变。

6. 缺陷、条件风险及普通观察

F129-01为确定P3维护偏差。[connect第323—324行](D:/shspic/project_NO3_RetroLume-agent/deploy/initialize_normal.py:323)的两行新增英文注释没有满足公共AGENTS第三章及TASK128要求的新增代码注释使用简体中文。触发条件为交付该新增片段，影响仅为注释规范，没有改变连接行为。最小修正由唯一工程路线把两行译为中文即可，B级文本差异足够，不需重跑认证、19/22/23或前三项，不阻塞本次独审交付及剩余动态取证。本卡无修改产品权限，保持原字节。

未发现新增确定P0/P1/P2功能或安全缺陷。原126的受信父目录并发替换条件风险和server_major类型观察无新增事实，原范围继承。两份分轮diff的CRCRLF包装、非空trace未逐字段记录EMPTY_QUERY、启动门瞬时值未单独落盘、完整工具精确unknown均已按证据粒度定界，没有据此虚构新的功能缺陷或扩大验证矩阵。

本审计方法首次误判非产品元数据的exit1及后续修正全部保留，未改产品、未修改既有测试断言或旧证据来消除该失败。早期终端输出截断/中文编码导致的有限补读只影响可见输出，不影响原字节指纹。初次结果存在性查询时报告尚不存在的PowerShell非零退出也不属于产品失败。

7. 剩余最小动态工作及恢复条件

第四项仍not_run。需在原成功source同身份上实际完成两个原生API周期及中间真实PG停/开，核normal根/ControlHub/业务登录、capabilities/readiness、外发关闭、身份和数据不变及完整优雅停止。当前首API未启动，不能用两个GET、同一PG周期或文档填补跨重开。

第五项仍not_run。仅对原interrupted槽位在原002真实执行、结果耗尽和COMMIT成功之后唯一隐藏确认，核001 confirmed、002 unknown、无003/complete/重放，另查实际提交事实及原收据重复/新收据部分库拒绝，保留部分库与卷。旧127失败和本轮启动门拒绝都没有消耗这次真实注入。

第六项仍not_run。回到原成功source，用原37行成功收据，仅提供管理员密码环境引用，正常verify必须真实连接并保持READ ONLY、schema/roles/身份一致及收据字节不变；坏绑定须连接前0调用拒绝。不能用本轮私有收据hash或test19的Recorder verify代替它。

最小可行次序为source首API并停库，interrupted唯一002场景并停库，再同一source跨重开第二API和verify并停库；不重装成功source、不重跑前三项、不恢复新空库、不重跑旧18/9或全安全矩阵。最少还需source两次启动、interrupted一次及API两次。source现为4/5，仅余一次，不足以满足跨PG重开，主控至少须前向明确多一次source启动额度及真实恢复入口；当前entry07仅限已证普通夹具缺陷，不能默认拿它重试容量问题。本报告不补授权或执行这些动作。

主控还须在恢复前判断旧2400工具秒及原截止是否足够覆盖剩余三项和900秒工程保存/收尾、原生150秒优雅停等已有上界；不得因本审计交付自行清零账、续时或视旧许可已恢复。内存只在获恢复的实际启动时按既定512/连续两次256策略检查，不能把释放内存或重测容量变成本卡完成条件。

若两函数和其风险没有新变化，后续仅需审新增真实动态原件及相应身份/资源账即可更新事实，无须重新全审这两函数。只改P3注释时以最小文本差异和新hash维护对象追踪，亦无功能重测理由。

8. 证据分级、本轮投入及回传

A级为沿冻结身份可追溯的既有真实连接、命令退出、原始trace、收据、实际登录拒绝及内存/停止原件；既有3方法测试仅在其离线范围为A。本轮没有新产品运行A级证据。B级为本轮hash、有限diff、AST、源码/配置及标准库JSON交叉分析。工程ledger中的passed、零费用、预算占用和未执行理由等声明本身为C，均按可核原件限定；NAT回放因果、无未记录旁观客户端及后续最小启动需求中的推导为D，已给源码与原件依据，不以C/D独立代替真实完成。

本卡工具上限2400秒含480秒保存，日历截至2026-10-24T10:01:34.514706+08:00。完整工具wall精确值记unknown，采用900/2400秒保守列支，余额1500秒在交回后封存，不恢复原126或128额度。可取得的exec_command和apply_patch工具回报wall逐条记录在[closure.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-129/audit/closure.json)，并行短命令相加仅为保守可核分项，不将其冒称整个会话精确总投入，也不把外层functions.exec再次叠加到同一父子耗时。

本轮PG、Docker、API、端口/内存探测、浏览器、Job、产品import、compile、测试、构建、网络/provider、安装/依赖、费用、删除和Git写均0；只执行标准库hash/JSON/diff/AST分析和必要文件读取。写入仅本报告及TASK129/audit目录，未修代码或改测试、迁移、配置、旧证据、DocuS及公共库。结果保存后复读、输入最终指纹及产物身份见closure.json。

建议主控只同步以下事实。两处功能增量独审已完成，记录F129-01非阻断P3；前三项在上述限定范围可采纳；第四、五、六项仍未运行；源码稳定但工程恢复存在source启动余量不足及旧预算/日历约束。README与normal-install说明没有冒称后三项完成，后续只按真实新结果最小维护。TASK128最终关闭、STEP018/019/020、Q、M1、项目及发布验收均留给主控，不在本报告裁定。

本轮没有新增可入库的已解决且实际验证经验，不写错误经验库。必要人工只有用户把本报告路径带回主控，无须提交密钥/账单、释放内存、建库、删卷或清理资源。补证继续同TASK129/R123追加保留历史，不覆盖本轮限制或失败。
