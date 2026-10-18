# TASK-092 / R-086 续作03 独立审计两项证据收口 当前有效

2026-10-01。接收A+，沿092实际实现窗口，不用093审计窗口。根D:/shspic/project_NO3_RetroLume-agent，task_model/V4.0 CHG0003，根AGENTS与锁定规则继续有效。需求v1.1、架构v0.64、执行v1.86。原合同的业务安全、精确资源和隐私约束继续有效；本增量仅补证，不新增G5功能，不占新TASK/R。

## 目标与已接受结论

093独立审计已回，未发现确定产品缺陷；产品代码审查结论保留，不重新全面审计。但C2参数长度显式检查缺用例，real01旧测试版本未留原件造成其余通过方法到最终测试的适用性缺口。一次连续收口两项，完成即停，不逐项回传。不要把“非阻断”写成已验证，也不扩大重跑范围。

补读本置顶、DocuN/results/TASK-093-result.md第6节、DocuN/evidence/TASK-093/audit-verification.json及real01/03原始as-run与stderr。原审计末尾“D3及四容器仍待决定”是过时叙述，不采纳、不重开083/084。原投入/失败不清零，当前真实5次/启动5、61.452秒、Windows7、离线6.655秒；旧unused real06许可已随完成结束，本卡若需要PG由以下新授权单独授予。

## E1 长度边界 按实际可达路径验证

允许修改backend/tests/test_activity_tools.py或test_worker_one_tool.py中最小新增定向边界测试，不改任何app产品、迁移或旧断言。修改前保存原件和hash到DocuN/evidence/TASK-092/continuation-03/pre。最终清单补充新版本及测试增量，不覆盖旧final-product-hashes、as-run和093审计冻结原件。

先区分两个真实路径：ToolRegistry.plan接收原始JSON字符串，ToolExecutionInput.to_wire校验严格规范字节。CalculationArguments只有operation/left/right、有界int/float，不能假定合法规范参数能长到2048字节。核实可达性并留简短依据，不放宽Schema、长度常量或patch产品制造成功样本。

用真实公开函数和有效身份/摘要测试：原始JSON路径可用合法JSON空白达到精确2048与2049 UTF8字节，分别验证长度边界并记录该路径不是规范wire；规范wire路径使用可达合法短样本作成功对照，2048字节非规范输入应到后续语义/规范校验拒绝而非误称接受，2049应在解析前命中长度拒绝。若能找到实际合法规范2048样本则用它；不可达时明确理由和对应防御检查证据，不自称“2048规范参数成功”。至少覆盖to_wire及from_wire实际委托路径，无PG/Job/网络。必要多字节长度反例按实际schema拒绝阶段区分，不能混同字符数与字节数。

只跑新增定向方法及确受改动的共享测试helper调用；不重跑93全套。离线新增总上限60秒计原1800秒，一次批及有明确修正依据最多一次定向复检。通过后保存真实调用/样本字节数/异常阶段/输出/hash，不能仅compile替代边界运行。

## E2 旧夹具身份 优先零运行恢复 否则一次定向PG

在项目既有本卡副本/工具保存的项目内补丁证据中有限查找real01的test_activity_tools.py原件，最多15分钟，不读客户端聊天/秘密存储、不全盘扫描。只有候选文件SHA256精确等于real01原始记录的完整eecba489开头hash，才可作为旧版本；可从已存补丁逆向重建到新证据文件，但必须完整hash匹配，记录重建方法及来源，不能凭记忆编一份假旧件。找到后逐函数diff证明只有已重验c7/c9及无关变化，若足够则复用原15通过+2复验，本轮PG零运行。

找不到精确原件或diff显示其他受影响方法，才启用以下一次定向PG许可，不再询问：对real01中最终版本适用性缺证的工具PG方法运行，排除已由real03最终版真实通过的c7/c9；原real01那4项旧model回归所属文件若hash本来一致则直接复用，不跟随整文件重跑。不得默认13或17全跑，冻结具体缺证方法ID、版本理由再运行。相同测试文件仅增加E1离线方法不自动使未变PG方法失效。

本轮新授权real06一次入口、原精确容器一次启动，总尝试最多6，不继承旧unused许可。业务180秒+清理120秒总300秒，计原3600秒；Windows业务会话新增0、新容器/卷/镜像0、真实provider/费用0。只用原retrolume_task092_tools库及task092_synth角色，不运行迁移/upgrade、不重建schema/数据库。精确CID e49d3acc3c1be13d670af68bca2b082fea4faeeb9b9babe69df7f1d3941696a4，镜像sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f，原卷retrolume-task-088-g3-w1-data，loopback55441/1CPU/512MiB/pids128/no restart/非privileged无host bind保持。首次完整JSON只读核停止/归属/白名单，不输出Env，无法确认就不接管。凭据仍只专用role、内存/stdin/子进程环境，不读用户DSN、不进argv/日志。

复用既有控制代码编排最小新入口或在本卡证据目录副本适配，仅运行上述缺证PG方法，无隐藏retry。新入口先持久记尝试、累计账及条件授权依据，不改旧批目录。真实目标、源码与测试hash绑定原始输出，逐例清理合成ID，finally树零/关句柄/精确stop核Running=false/Pid=0。失败即收尾交回，不暗开real07。控制器外层Job可用于回收PG子进程，不得借此调用业务worker/Windows场景。

## 交付、写权与停止

新增证据仅DocuN/evidence/TASK-092/continuation-03和必要real06；允许新增本次专用runner，旧原始证据与产品只读；原attempt/budget索引追加，source/post补充清单另存。本轮主动投入最多60分钟且受原8小时余量约束；同缺陷两次有据修正仍失败仍停，不能利用新轮重置。成功即结束全部新增许可。

若产品缺陷/Schema新语义或真实资源归属异常，停止相关部分并带具体证据交回，不在本补证卡修产品。完成两项后置顶TASK092-result.md续作03，保留历史，分开写E1真实路径与可达性、E2确切旧原件证明或必要最终方法PG、全部累计/资源事实和剩余限制。

该补证不重开原代码审查；只影响新增测试与证据适用性，后续如需原093窗口确认只限这两项，不全面重审。最终是否关闭G5由编排据证据裁定。回复一句结论与D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-092-result.md绝对链接即可。

## 以下为前轮合同历史
# TASK-092 / R-086 续作02 升级库完整收尾 当前有效

2026-10-01，编排在用户已批准的G5合成验证边界内授权。接收A+，沿TASK-092实际Claude桌面Code实现窗口；不换到审计窗口，不新占TASK/R。下方原合同继续有效，运行次数与范围冲突以本置顶为准。本轮是连续完成剩余迁移证据，不是新增产品开发或独立审计。

## 目标与已核证断点

根D:/shspic/project_NO3_RetroLume-agent，入口根AGENTS.md，V4.0/CHG-0003及规则锁定指纹不变。需求v1.1、架构v0.62、执行v1.83。补读本置顶、DocuN/results/TASK-092-work-decision.md当前轮及你已保存的续作01事实；同窗未变资料复用。

real-04已结束：Windows五函数六会话exit0/failed=[]，upgrade exit1，树零/句柄关闭、容器停止、active为空。编排复算21条最终清单和real-04产品/迁移指纹无漂移；原Windows及17唯一PG方法、93离线有效证据复用，不重跑。旧版探针是行为副本局部证据，不冒称完整跨版本部署兼容。

剩余唯一成果：升级库s1生命线拒绝/重复008完整收尾、s2篡改约束识别失败且全回滚、s3缺前置拒绝且零DDL。你已修正生命线探针到有效窗口内且T1上下文配T1输入，但此前0.234秒复检未连接PG，只证明到达事务边界，不能替代三个真实目标。本轮完成后提交稳定全包，编排另卡集中独立增强审计。

## 允许动作及冻结

所有backend产品、迁移、测试继续冻结，不改业务来迁就夹具。允许写DocuN/evidence/TASK-092内的upgrade_child.py及本次专用upgrade-only runner、必要child_control夹具控制修正；新证据存continuation-02、real-05，必要定向复验real-06。旧real-01—04/offline/continuation-01原始证据只读；准备前保存当前副本/hash，变化有diff。

不修改win_chain/bootstrap/legacy_probe去重新测Windows，不运行tool_pg_child，不运行旧整批final/continuation_runner，不全量离线。预算/attempt总索引仅追加真实记录，保留旧上限历史和本次增加授权；结果继续同一TASK-092-result.md置顶续作02、保留全部前轮。

先在同一执行窗口一次核对整个剩余路径，特别是来源/活动/租约/操作键前提、异常目标、schema search_path及重复/失败迁移后的事务状态。不要仅确认探针通过Python校验就直接认为数据库路径正确。可修改确定夹具问题及增强必要证据，不改变预期产品语义。

s1/s2/s3改为明确独立结果与独立连接，每个finally收连接；一个断言失败且该schema连接已回滚/关闭、无持锁或清理不全时，继续其他隔离schema，失败仍使整批非零。不得让s1失败再次使s2/s3全部not_run。资源/归属/清理不确定则停止后续，不能强行继续。

负例不能以任意Exception判通过：保留异常类型、SQLSTATE及有限脱敏识别文本，确认是008预期重复痕迹/成本约束识别/缺前置拒绝，不是DSN/权限/SQL语法/夹具表不存在。比较目标schema前后列、约束定义、合成行/正文；s2须没有五新列、无部分DDL、旧行不变；s3明确零目标对象；s1重复008不改变已有schema与数据。现有identification_failure只记录布尔不足以支持结论，需实际断言或等效明确判定。

s1可重建本卡happy schema并一次完整走通，此前行不变证据复用但为建立本轮生命线前提执行001—008不算重跑全仓。s2/s3分别独立基线和失败连接，不依赖s1产物。实际运行过的失败/成功schema均如实保留摘要。

## 合成资源与新额度

原8小时总主动投入不重置，当前约2.2小时为执行者声明；本轮主动工作上限90分钟且受原8小时剩余共同约束。离线准备/定向复检最多60秒计原1800秒；只检查本次夹具/控制，不重复93方法。

新增最多两个升级库批槽：real-05一次完整三个场景；仅当real-05因有明确根因、范围内夹具或控制缺陷失败，且已按原同缺陷两次修正门纠正时，允许real-06一次只测失败/未运行项。若real-05全过立即停止，不为额度用完启动06。产品缺陷、根因不稳、身份/安全问题不允许用06继续试探，应收尾交回。预检失败也记批，不能隐藏内层整批重试。

累计批次/精确容器启动上限4→6；真实累计原3600秒上限不变，已有53.030秒保留。每批业务最多180秒、清理预留120秒、总截止300秒；两个批次合计最多600秒且受原剩余约束。Windows业务受控会话新增0（原累计7/12封存，不使用余5），仅允许PG夹具外层自有Job回收子进程，不调用业务launcher/worker。付费/真实provider/新容器/新卷/安装/联网/Git写操作0。

精确资源完整CID e49d3acc3c1be13d670af68bca2b082fea4faeeb9b9babe69df7f1d3941696a4；名字retrolume-task-088-g3-w1；镜像sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f；唯一命名卷retrolume-task-088-g3-w1-data；loopback55441，1CPU/512MiB/pids128/no restart/非privileged、无host bind。沿原白名单先完整inspect JSON在内存核证，不保存Env；历史停止不代实时。不是本卡可确认的停止/所有权就不启动、不杀他人工作。

只访问retrolume_task092_upgrade及角色retrolume_task092_synth，既有本卡创建证据沿real-01/04，不触tools库数据、不创建新DB/role。容器内既有管理通道仅必要专用角色凭据管理，secret仅内存/stdin/子进程环境，不进argv或报告。不存在/归属不符不自动接管或重建。

可在确认current_database/current_user及既有本卡归属、保存旧schema摘要后，定向重建task092_upgrade_happy、task092_upgrade_rollback、task092_upgrade_missing三schema；不能drop public/数据库/role/卷或其他schema。定向06只重建所需失败schema，不抹掉其他通过证据。所有连接/锁/语句有界，按真实事务失败rollback/close。

批次入口先持久登记尝试及预算，累计旧4批4启动，源文件开跑即冻结。独立超时/自有进程标识、树零/句柄关闭/精确容器stop与Running=false/Pid=0必留原件；资源清理失败停止任何下一批。原同缺陷两次有据修正仍失败门保留，不因续作02清零。

## 证据、交付和停止

本轮按三个目标分别记结果，不把一次子批exit0当全部目标通过。每项记录产品实际加载hash、SQL/注入点、前后投影、异常/SQLSTATE、源hash和生命周期；生成upgrade-summary包含s1/s2/s3独立passed/failed/not_run。负例识别错误不能报通过。对已复用的原Windows/PG只列原件和适用范围，不复制日志。

real-05后若需06，先保存明确诊断与单次修正diff及复验对象映射，再只重测受影响项；普通有据修正无需再转卡。成功即整卡收尾，失败用尽或关键阻断则如实交回，不自开第7批、不追加业务运行。

结果继续D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-092-result.md，置顶本轮范围/实际结果/累计预算/资源状态/原证据复用/未覆盖。完成后只能称G5候选实现及卡内验证完成待隔离审计，不能自签独立审计或M-1。正式DocuS/CHG由编排维护。回复一句结论和完整结果绝对路径。

## 以下为续作01与首轮合同 历史保留
# TASK-092 / R-086 续作01：剩余迁移与Windows链一次收尾 当前有效

你继续本卡执行，不重新实现G5，不承担独立审计。接收A+，沿TASK-092实际Claude桌面Code实现窗口；实际型号如实登记，不因已完成模型标签重复工作。原任务卡保留在下方，冲突以本置顶有限增量为准。

## 接续目标与输入

项目D:/shspic/project_NO3_RetroLume-agent。读取根AGENTS.md，公共V4锁定规则沿用，补读DocuN/results/TASK-092-work-decision.md、你的原结果、DocuN/evidence/TASK-092/orchestration-review-01/check.json和本置顶。需求v1.1、架构v0.61、执行v1.82。TASK-091设计、原实现合同与首轮有效证据不重读全历史。

目标是修正剩余夹具的确定问题，一次合并完成非空迁移收尾和Windows剩余六方向，整理最终成果供下一独立审计。不要重跑已有效通过的93离线/17PG方法，不启动原final或retry_upgrade整批。完成标准是精确剩余清单逐项真实结论、最终绑定证据、资源收尾、计数修正；未通过如实交回，不自签验收。

## 先完成的有限准备 同卡连续执行

1. 保存当前runner/upgrade/win夹具副本与hash到新continuation-01/pre；产品、backend测试及迁移全部冻结于final-product-hashes.json和real-03原始指纹。本轮不改产品，发现产品阻断停止相关运行并报告，不越权补产品以破坏旧证据适用性。
2. 必修F-U2：upgrade_child.py check_happy比较旧操作行时只排除kind，漏掉新增arguments_sha256/tool_call_id。先断言三列新增集合、kind=model与两元数据NULL，再排除精确三列比较原全部字段；保留旧正文逐字节/哈希、旧预算/时间计数不变。此为不同于活动快照遗漏列的后继缺陷，不可直接运行当前版本碰运气。
3. 一次走查upgrade完整后继、六方向夹具和legacy_probe的真实调用关系。核对真实migration前后列差、行值、约束数量、旧model生命线、重复008/篡改约束/缺前置全回滚，C10结算等式、C11真实mark后硬停及恢复的上下文/租约/身份，混用正反照。可以在证据夹具内修正明确的同链静态缺陷，保留具体依据及diff，不弱化身份/停止/预算/正文断言，不patch产品校验。没有新证据不扩大调查范围。
4. 原runner硬编码3批/3start，必须依据本增量加入独立continuation入口，只调度upgrade_child和win_chain；新场景记录包含续作授权、累计旧账及单批420秒。不要只改预算JSON绕过代码上限，不删除旧attempt。业务300秒与清理120秒分开，修正旧deadline-180预留使有效时间不被静默挤成120秒；所有子进程截止以同一单调总截止推导，无无界等待。入口只允许历史3批已完成、无active进程且此次未用；一次调用立即记第4次，即使预检失败也占槽。累计费用仍0。
5. 核证专用DB/角色归属沿real-01创建及后续manifest，不重新创建旧库。upgrade三schema task092_upgrade_happy、task092_upgrade_rollback、task092_upgrade_missing仅在retrolume_task092_upgrade内，确认current_database/current_user与既有本卡归属后可先保存现状摘要，再定向重建这三个自有合成schema。禁止drop public、旧工具库/旧role/旧卷或其他schema，不让缺DSN落到默认连接。
6. 当前runner使用Go投影而原卡要求完整JSON，属控制实现偏差：本轮按原要求改为完整inspect JSON在内存解析白名单字段，只输出白名单，不保存/打印Env；缺字段按需失败关闭。无需额外运行探针证明Docker新特性，不碰其他容器。
7. 允许一次不触Docker/PG/Job的准备检查及有明确修复依据的定向复检，累计60秒内，计原离线总额。可以compile不写pyc及有限纯数据断言，禁止拿mock冒充真实事务。确认剩余全部路径输入/输出、计数、身份和清理后冻结，一次启动，无逐步问用户。

本轮可写本卡evidence下batch_runner.py、upgrade_child.py、win_chain.py及必要bootstrap/legacy_probe/child_control夹具级同链修正；不得改变产品安全主体、注入绕过真实链、用副本行为冒充真实旧版本整链。旧legacy行为副本与原pre的适用范围明确标注，局部探针不能升级为完整跨版本部署兼容。写新的continuation-01、real-04证据，旧real/offline目录只读；预算/场景总索引追加历史，原manifest不覆写。

## 唯一真实批与运行许可

编排在已批准原完整合成验证范围内追加real-04一批及原容器一次启动，累计上限从3增4，不重置任何历史。该批业务运行最多300秒，加收尾最多120秒，入口总截止420秒；原累计3600秒/主动8小时/Windows12次/离线1800秒上限不变。本轮Windows至多6次，包含停止和恢复两个会话及所有失败启动，不把一个组合函数当一次会话漏计。上次已用25.921秒、3批、3启动、1Windows、5.327离线秒继续累计；主动约1.5小时为执行者声明，补真实时间不得伪造。

只允许升级收尾子批和六方向Windows：tool_chain、旧model合成transport回归、tool_stop、tool_recovery、old_sup_reject、old_worker_reject。Windows实际5函数含一个两会话组合，报告区分函数/方向/会话。旧model transport为合成回复，不准外部真实请求。PG c7/c9和其他通过方法直接复用。upgrade失败可以在库隔离且清理确认后继续独立Windows；同活动stop失败则recovery不可伪独立通过，标not_run。任何清理不全停止后续场景，先只收尾。

资源仍仅完整ID e49d3acc3c1be13d670af68bca2b082fea4faeeb9b9babe69df7f1d3941696a4，原名字retrolume-task-088-g3-w1、原镜像/卷/loopback55441/1CPU/512MiB/pids128等全部沿下方原合同。开始前核停止及精确身份，无法确认不启动、不停止未知他人工作。仅本卡tools/upgrade库及task092_synth角色，凭据不入日志/argv。新容器、新卷、网络provider、安装、Git、用户库额度均0。批后精确stop核Running=false/Pid=0、树零/句柄关闭、active_processes空，保留库/卷供审计。

同缺陷累计两次有据修正仍失败即停；本轮真实入口只一次，不因剩秒再开第5批。开始前已确定缺陷在有限准备中合并修正，启动后冻结文件，不边跑边改。真实失败先保留证据并收尾，再交回编排；不自动制造下一轮测试。

## 证据、报告与审计

保存continuation-01准备diff/hash/控制核对及real-04实际加载/场景/DB断言/树和资源证据。与旧as-run分开，不用当前夹具hash回填旧批。最后C1—C12逐子目标标真实通过、mock局部、静态、未覆盖和旧证据复用；17方法通过不是12大类全覆盖，未覆盖如实交审计，禁止一行“全部符合”跳过矩阵。

纠正原报告差异计数：final-product-hashes.json21项含4项pre=post，实际差异17项；离线93通过另71skip，不是164通过；PG首批17加复验2为19执行实例/17唯一方法。scenario-manifest.frozen_utc与原批时间有不一致时据真实文件/原件披露，不改旧时间去补造批前冻结；本次冻结使用真实时点。

结果继续D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-092-result.md置顶续作01，首轮全文保留。报告实际准备修复/运行/未运行、源码冻结、累计账/资源状态、注入边界及偏差。审计尚未进行；稳定后由编排另卡隔离集中审计，本实现窗口不自签、不自动转派。

完成回复一句结论和结果绝对路径。仅真正关键阻塞才交回，正常准备与一次真实批连续完成。

## 原TASK-092合同 历史与未覆盖边界继续有效
# TASK-092 / R-086 G5有限工具执行与持久次数完整实现

## 目标与交付

你是本卡执行者。连续完成G5已批准内部最小切片的实现、针对性验证、范围内普通修复和资源收尾，不承担独立审计或项目最终验收。完成后交回一个稳定成果包，不在正常实现、写测试、首次成功或普通修正节点分别交回。

用户价值：受信内部调用方可以显式发起一次finite_calculate；工具次数持久有限，重复/不确定操作不自动重执行，结果可恢复读取，执行受原Windows Job停止与时间账本控制；工具结果不能隐式成为模型父输入。

交付：008迁移、仓储与内部适配/受控worker接线、必要测试与本卡隔离夹具；C1—C12逐项事实和证据；最终实际文件差异、加载指纹、尝试账及资源收尾；D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-092-result.md。产品候选完整交付后由编排另卡组织集中独立增强审计；本卡通过不等于G5已最终放行，更不等于M-1/整个STEP完成。

## 项目、规则与接收安排

根目录D:/shspic/project_NO3_RetroLume-agent，入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。以下产品相对路径全部相对该根。

模式task_model，V4.0、公共AGENTS CHG-0003。公共根D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4。读取该根DocuS/AGENTS.MD；适用WORK.MD第2节task_model及第6/8/9节委派、接续和核证，由编排落实，执行者只补必要合同职责。公共task_model/TASK_TEMPLATE.md为回传结构依据；主控阶段07_开发执行循环.md已读取，不要求执行者重读全套阶段。七份规则锁定指纹见项目DocuN/evidence/v4-migration-20260930/rules-snapshot.json；不能自动采用后续规则。公共库只读。

任务为增强开发与受控验证，父TASK-091/R-085，关联090/G4、088—089/G3、083—084/D3、STEP006/008、FLOW-005、DATA-007及既有工具权限与NFR-002/003、SEC-002。需求v1.1、架构v0.60、执行v1.81；这些版本包含本卡编排批准记录，底层批准目标未改。

授权：用户2026-09-30明确“批准”091-work-decision中的单一G5变更包。授权终点为本卡内部切片及下述合成验证和收尾；用户库、真实provider、公开入口、任意工具或命令、工具→模型循环、额度扩容、跨机恢复及部署均不包含。

接收A+增强执行，优先TASK-091修正轮01实际Codex执行窗口；原窗口不可用时可同档新实现窗口，补读完整本卡及批准正文。不是旧091首轮窗口的强制回迁，不使用独立审计窗口。实际客户端/模型可知则如实记载，不凭A+冒称型号。不自动创建子Agent或并行执行窗口。

Git基础45951501d2741630a229762d6b2d3f4b34d7f702仅为历史提交；当前未提交成果才是实施基线，不reset/checkout覆盖、不commit/push。编排已核20项直接backend指纹与091修正清单一致，见DocuN/evidence/TASK-092/baseline.json。其余允许改动文件先存原件及hash，新文件核不存在；若存在不属本卡的改动，定位并保留，不覆盖、不伪报由本卡产生。

091设计已关闭，累计106.449/120分钟及K1—K5历史保留；090旧批次/费用和083旧失败不清零。本任务新授权范围首次启动，当前实施/验证尝试0，预算单独记录，不借用旧余量。

## 背景与最小充分输入

按顺序读取或复用同窗未变材料：

1. 根入口、锁定公共AGENTS、本卡全文，DocuS/执行动态文档.MD及架构动态文档.MD顶部本次范围。
2. DocuN/results/TASK-091-work-decision.md置顶批准及设计验收；DocuN/results/TASK-091-result.md修正轮01完整A—D、B1—B10、C1—C12、K关闭表，止于首轮历史前。该结果冻结SHA256 a6dfdd231ea1cac76497c1a6c3dd77a77e7b653cac2231850d95d49128c92866。正文为本卡技术合同的完整组成部分；首轮被替换方案不能重新继承。不可读取时交回必要合同缺口，不依据聊天重建。
3. DocuN/evidence/TASK-092/baseline.json及091 revision-01/files-read-hashes.json中产品项；正式管理文档本次已合法更新，不能拿旧管理hash误报产品漂移。
4. backend/app/activities/repository.py、service.py、__init__.py；capabilities/contracts.py、tools.py及必要出口；worker/command.py、worker_main.py、launcher.py、supervisor_main.py、session.py、one_call.py和其直接协议/停止依赖；001—007迁移、相关现有测试。按函数影响读取，不重审全仓。
5. 需要复用证据时定向读取Ndocu/results/TASK-090-independent-audit.md、DocuN/results/TASK-090-final-acceptance.md及090原始证据索引；D3/旧G3依据实际未变路径引用，不全套重跑。

已解决历史问题必须避免复现：不要让服务进程持租约直算并自行结算；不要以allowed_tools为空代替父结果kind隔离；不要给原三字段AdmissionPermit虚构摘要字段；不要依赖可变Mapping或SQL CHECK的NULL漏洞；不要混同未提交崩溃与已提交丢响应。旧Job夹具曾因硬编码身份/句柄撞号失败，新夹具必须派生真实身份，不patch随机ID绕过校验。

## 已批准固定技术边界

以下是关键摘要，细节以091修正轮01完整合同为准；实现普通命名/helper拆分自主决定。

1. 仅finite_calculate。max_tool_calls为严格有限整数0..INT_MAX，拒bool/字符串；NULL未配置、0禁用。tools_reserved非负，NULL上限必须已用0，配置时已用不超过上限。每次成功持久工具准入耗用1，响应丢失/未execute/unknown也不自动退次。模型次数/成本独立，时间使用原窗口账，不把“无工具扣次”当“时间零消耗”。无运行中加额。
2. 008在同事务增activities两列及operations.kind/tool_call_id/arguments_sha256；旧行kind=model；按model/tool建立完整条件约束，明确非空、元数据、正值与成本0语义；精确识别旧成本约束，歧义失败回滚。旧001—007不修改。007正文表复用，非空迁移仅合成库，保留锁表/扫描和已使用后不能虚构安全降级的说明。
3. 新独立ToolExecutionInput/ToolIntent/ToolAdmissionPermit，原模型凭证兼容。调用方Mapping仅一次私有快照，严格schema、规范UTF8 JSON不超过2048字节，hash及工具名/call_id/活动/G/范围/执行者绑定；execute从同一不可变规范输入解析，mark/record重新核对输入、凭证和锁内DB，不信客户端kind。
4. 新admit_tool_operation/mark_tool_started/record_tool_outcome维持来源→活动→操作锁序；操作键与model共用命名空间；提交确认才下一动作。工具成功正文和received同短事务；明确失败received/error无正文；unknown不伪成功，响应丢失按持久事实只读或严格终态确认，绝不重算。原model mark/record也验证kind=model，受限幂等不能因代次已关闭而误拒合法确认。
5. ActivityService.execute_tool_action→run_one_tool→原固定launcher/SUP/worker，WorkerCommand只加固定one_tool；service不claim、不execute、不settle。原命名Job归属、旧树恢复、暂停创建/归Job/恢复、受控时间、树零及句柄关闭→关门→结算保留。业务UNKNOWN与时间已结算分开；失去有效停止证明不能部分退款。取消线程/协程保留有界收尾。
6. model外2/内3精确兼容；tool专用外3/内4严格帧，不宽松回退。SessionOutcome新增可选tool_receipt但旧帧显式旧字段集；尺寸和身份早拒，旧worker拒新工具不代表先前时间预扣不存在。无secret/正文/参数进argv或日志；诊断只脱敏事件码及必要关联标识。
7. read/list权威投影类型及工具绑定，文本正文继续G3有效性与hash验证。service早拒tool父结果；仓储锁内model父准入再次拒绝，即使直接构造正确引用且allowed_tools为空。工具只读恢复，不自动接模型/循环/重发；不承诺阻止受信调用方手工复制普通文本的范围外行为。
8. 逐事务分别处理admit/mark/record/close/settle提交前后丢响应，保留同G/W/C有限一次settle确认。两种scope竞争必须用真实CAS和屏障证明发生点，正常并发仅承诺至多一次准入/执行资格，崩溃可能实际零执行但耗次1。

## 文件写入、整合与禁止范围

允许修改：backend/app/activities/repository.py、service.py、__init__.py；backend/app/capabilities/contracts.py及必要包出口；backend/app/worker/command.py、worker_main.py、launcher.py、supervisor_main.py、session.py；仅为保持精确旧帧兼容所需的worker/one_call.py小范围适配。

允许新增：backend/migrations/008_activity_tool_budget.sql；backend/app/capabilities/tool_execution.py；backend/app/worker/one_tool.py；backend/tests/test_activity_tools.py、test_worker_one_tool.py。

允许必要受影响测试适配：backend/tests/test_activity_results.py、test_activity_continuation.py、test_capabilities.py、test_worker_session.py、test_worker_one_call.py；现有文件若实际命名有后缀，只能选择同一被测功能的对应文件并记录映射，不能借此全仓放开。如现有activity ledger/recovery测试仅因新增可选字段仍兼容则不动；出现必须修改其业务语义的情形报告具体冲突。

新增runner、故障夹具、清单、原始输出、pre副本只在D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-092/。生产模块不得导入该证据目录；测试注入不能进入公开产品控制面。总结果仅D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-092-result.md。

禁止改HTTP/UI/main/runtime、transport/model发送路径、gate/windows_job/supervisor_ipc安全主体、materials权威更新、001—007、依赖锁、正式DocuS、其他卡/结果/旧证据、公共库、用户原始需求及共享记忆。原ToolRegistry校验/计算语义复用只读。不安装/联网/下载、不改宿主系统/DB时钟、不开Docker Desktop/服务、不更改ACL/安全工具、不Git写操作。当前源码由本卡独占，无并行测试；共享状态与编号只由编排维护。

## 运行资源和预算 新授权且不继承旧余额

先完成实现和有辨别力的离线检查，再运行完整定向真实链；不把每个C项拆成独立审批或新卡。资源不可用时可先完成不受影响实现和离线部分。

本卡总主动投入上限8小时，从首次读取本卡开始记录，等待用户/断线不假称工作时间。完成即停，不以消耗额度为目标。离线测试/compile子进程累计上限1800秒；真实PG/Windows验证最多3个完整批次、所有批次累计3600秒，单批最多1200秒。首次执行入口即占1批，预检失败也计数；批内按冻结场景清单连续运行，禁止隐藏的批内自动整批重试。每个独立缺陷最多两次有证据修正，仍失败即停止受影响运行交回；不能换入口/窗口重置次数。

Windows真实受控会话总计至多12次，包含C10、C11及C11所需恢复会话和失败启动；框架批次/场景/会话计数分开。每会话配置总截止至多120秒，另有一次有界清理；使用已有生产不等式选合法窗口和超时，不靠缩短到不可启动或全局改时钟造样本。每个外层runner有独立总截止和自有树回收；不得用runner自身等待线程充当它自身卡死的绝对保障。

只可核证后复用以下历史测试资源，不创建替补：容器完整ID e49d3acc3c1be13d670af68bca2b082fea4faeeb9b9babe69df7f1d3941696a4，名字retrolume-task-088-g3-w1，镜像sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f，唯一命名卷retrolume-task-088-g3-w1-data；loopback端口55441；1 CPU、512MiB、pids128、无自动重启、非privileged、无host bind。禁止新容器、新卷、新镜像拉取和参数修改。Docker只访问这个完整ID，禁止按模糊名全局stop/prune。

首次资源接触只读精确inspect，解析完整JSON的明确属性，缺可选字段按“缺失”处理后作安全判定；不要重复历史Go模板HostConfig.Mounts与Id组合错误。输出仅上述白名单字段，不输出Config.Env或凭据。还须确认容器实际停止；若已运行且无法证明本卡所有权，停止资源部分而非停他人任务。镜像、挂载或限制不匹配立即停止资源部分；只读诊断累计至多10分钟且不可凭探针扩为后台测试。

确认匹配后授权对此精确容器start至多3次，批后stop并核实Running=false/Pid=0；不得remove，保留旧卷/库/证据。旧090的停止记录仅历史，不替代本卡实时核证。宿主Docker不可用不授权安装/启动服务。

只允许在该容器中新建两个专用合成数据库retrolume_task092_tools、retrolume_task092_upgrade及任务角色retrolume_task092_synth；使用既有容器内本地管理角色retrolume_task088_synth的现有可用本地通道完成管理，不读旧配置/密码。如果该通道不可用，不改认证、不查用户凭据。新任务角色随机凭据仅内存/受限子进程环境或stdin，不写报告、命令行、Git或日志。测试DSN专名RETROLUME_TOOL_TEST_DATABASE_URL与RETROLUME_TOOL_UPGRADE_TEST_DATABASE_URL，缺失明确skip；正式批次所需skip视作未完成，不回退用户DSN。若同名对象先已存在且无法由本卡manifest证明归属，停止该资源动作，不清库或接管。仅可对本卡已确认创建的对象做幂等接续。

tools库验证新建001—008与真实工具链；upgrade库验证合法非空001—007→008及失败回滚。负例优先事务/savepoint回滚，必要隔离schema只在这两个本卡DB内且manifest列出，不跨旧库。授权仅本卡合成ID行清理，活动外键按实际顺序；不得广泛TRUNCATE/删旧库/旧role/卷。保留最终专用库和角色供审计，容器停止。迁移锁等待、语句和连接均设有界超时，遵守现有事务边界。

真实模型/provider/互联网请求预算0，付费额度0。工具运算不能发网络请求。不能以本卡8小时变为付费API额度；测试必须隔离外部transport并可观察调用数0。

清理为必做工作，预算到限或失败亦执行限定自有进程/句柄/精确容器停止；另预留最多120秒只用于收尾，不可跑新场景。清理不全立即如实回报归属和残留，不用“进程不存在”文本冒充树零，不杀名字相同的他人进程。

## 验证、证据与独立审计关系

C1—C12必须逐项映射091修正合同，下面给最小分组，不减少其验收语义。

A. 离线：参数规范化、输入域、别名变更、凭证跨kind/摘要绑定、严格协议版本与旧精确字段兼容、服务早拒父tool、新控制流的停止权限。Mock仅证明编码/控制逻辑，不证明PG事务或Job实际停止。只跑实际受影响旧方法，不全仓discover。
B. 真实PG：C1空/非空迁移与全部条件反例、重复008和中途失败全回滚；C2—C5真实绑定、预算、同键两连接屏障及父kind服务/DB双拒；C6—C8各提交前后独立故障位、一次实际计算、正文原子性及确认重试不写账；C9真实CAS两种竞争/取消/来源及晚到；C12关门结算持久事实。故障注入切真实COMMIT边界，不伪造仓储返回值充事务证明。每个负例须确认命中目标而不是前序夹具错误。
C. 最小真实Windows：C10受信service→固定launcher/SUP/worker→真实finite_calculate→真实PG正文→树零/关句柄/close/settle；C11工具mark后阻塞替身→实际Job硬停→旧窗口恢复/折叠→unknown不重执行；C12相关帧/关闭事实可合并其中。正常工具运算和阻塞替身分开标明，不能说替身是实际工具会挂死。旧model精确协议至少定向兼容回归，无真实模型网络。

每批开始前保存不可变场景清单、运行文件hash、配置、资源核证、超时和本批预算。每次真实运行记录产品实际加载路径及hash、DB前后投影、异常/退出码、PID与创建时间、Job/会话身份和树/句柄收尾；不记录参数正文或凭据。runner若运行中修改则该批不能绑定为最终版本，先结束、保留旧证据，再在剩余额度定向复验。

原始证据只保留一份，不覆盖失败批。attempt-ledger或等价清单连续记录每次入口、命令脱敏形式、开始/结束/耗时、截止、exit、场景pass/fail/not_run/skip、源hash、故障位和资源收尾。汇总区分执行实例、唯一方法、组合场景，不把同方法多批相加称独立覆盖。

最终建立C1—C12→测试ID/原始输出/hash/结论/限制映射；源码修改后只补跑受影响项，明确哪些旧证据仍适用以及依据，不因小修全量重跑。最终pre/post差异和产品清单应让隔离审计者可独立重建，不依赖你的聊天推理。未变D3/G3/090证据按作用范围引用；不重新进行已闭合设计审查。

本卡可内部推进实现、测试、普通修复及收尾。独立增强审计由编排在整体稳定后另卡隔离会话承担，输入为原始目标/批准合同/最终实际diff/源码/原始证据；本窗口不得自签审计或自动另派审计。隔离终审及编排验收尚未完成时仅候选交付。

## 停止、回传及待同步

达到完整成果即停。主要模型/协议形状与已批准包冲突、必须改禁止安全主体、需新增工具或服务、身份/资源无法确认、未知他人改动、根因不稳、同缺陷两次有依据修正仍失败或额度到限，停止受影响部分；完成不受阻部分后一次交回具体差异和最小决定。不在未获证据时扩大运行或弱化断言，不为保持表面通过删掉必要场景。

断线恢复先核本卡checkpoint、活跃PID+创建时间/容器状态、已提交DB事实及日志，不重复启动已有批。恢复不重置编号/失败/预算，不把已经发生的实际计算当可再试。未完成但同边界沿本卡和结果续作，不自行占新TASK/R/CHG。

完整结果保存D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-092-result.md。内容包括一句结论、TASK/R/STEP、实际身份与窗口、授权引用、实现字段/签名/返回/协议清单、全部实际差异和pre/posthash、C1—C12证据分级与最终适用范围、尝试与失败修复账、预算、资源状态与清理、未完成/未验证/风险/偏差、需同步文档及下一步。保留失败原文和旧轮历史，候选状态不冒充最终通过。

正式架构、执行、变更账和共享经验由编排更新；你只在结果提出具体位置/变化及来源许可。新增依赖与外部代码引入不在授权内。必要人工事项当前无，资源真实阻塞时带回最少非敏感信息。确认结果文件真实保存且可读后，回复一句结论和结果的可点击绝对路径即可。