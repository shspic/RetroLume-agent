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


