# TASK-089 / R-083 — Windows收尾01最终交接（2026-09-29，当前有效）

结论：剩余Windows接线与最终证据补齐完成；原独立审计者确认本批准G3切片达到可供编排验收关闭条件。正式验收由编排完成，不代表STEP008整体或真实provider通过。

## 最终成果与独立结论

依用户转交收尾01及TASK-089-work-decision执行，沿需求v1.1/架构v0.55/执行状态v1.75。产品、测试、001—007未改。原final-hashes.json的27项保留，仅获准bootstrap.py/win_chain.py有本次入口与采集增量，新增windows_completion.py。repository仍a31e7d770b9f8746bfe66dd4fc7ea946b195eca21b029b370940810fd0a938b2；one_call仍cb1bf3f2440c6727311fb2a8af27d1b9668a6abc1ef00c84e6ff4e465ce57727。

真实Windows固定SUP→worker→gateway→专用真实PG链通过；测试transport合成响应、每会话发送恰1。内3回执无正文，经真实外2校验；回执/DB/合法read的SHA256均为07642a332cbe8328edcfca6161c69da2b15b76fa5e7a02183b7a3845c548ca7b。最终账户R0/S1、操作G1、活动G2、关门true。SUP203条原始轨迹及成功返回共同证明树零→关闭自身句柄→关门→结算。父进程17、SUP18、worker18个实际编译源码字节hash与as-run/post一致；不是仅在运行后读取磁盘hash。

[独立审计报告](TASK-089-independent-audit.md)最后增量由原TASK089/Audit窗口本人追加，已保存且本次读取核实；四类结论为产品合同通过、动态证据适用、收尾01合规、资源最终记录通过，无剩余G3关闭阻断。主执行没有代签或改写独立报告。审计窗口随后遇额度错误不影响此前已保存且核实的报告，无需重开审计。

测试自举仅替换测试启动入口/worker argv及transport发送边界，并禁止工具执行；真实监督主体、身份/IPC、安全门、gateway、PG提交读取均实际执行。没有真实供应商请求或真实账号数据结论。

## 两批运行与最终资源账

两次命令：`backend/.venv/Scripts/python.exe -B backend/tests/fixtures/task089/windows_completion.py`。

- 总attempt2（本段attempt-1）：1发现/1执行/0skip/1通过/0失败，exit0，11.25秒。链成功；父进程轨迹不足以证明SUP顺序，原始证据保留。
- 总attempt3（attempt-2）：仅修正SUP采集位置及父导入钩子位置后，1发现/1执行/0skip/1通过/0失败，exit0，5.11秒；实际SUP203条轨迹补齐缺口。这是唯一受影响采集续验，没有扩大业务覆盖。
- 全卡启动3/3、Windows2/6（本段2/2），新容器/卷0。本段实测16.36秒另保守扣启动开销4秒；全卡真实50.594/2400秒，离线8.5055802/1800秒。本段静态保守扣3秒，含UTF8读取和清单路径错误；未重跑44离线/18PG或迁移。

只操作指定CID e49d3acc3c1be13d670af68bca2b082fea4faeeb9b9babe69df7f1d3941696a4。每批先核精确配置、DB所有者、任务角色非超级权限/零成员关系/无占用，再按新明确授权轮换一次retrolume_task089_synth口令；仅内存/stdin/受控子进程env，不在argv或日志打印。不读取旧秘密，不修改管理角色，不创建库/角色/容器/卷。仅本例随机ID定向清理；原资源/合成库保留。两批外层树零、句柄关闭、cleanup_incomplete=false；末批06:51:53Z精确inspect确认Running=false/Pid0。其他旧资源未操作，不冒称持续监控。

## 交接与历史保留

A/B/C/D在本卡边界内已达到可交回成果。[下一业务闭环只读合同](TASK-089-next-contract.md)沿已接收版本，本次不重写或实施。编排待办是G3正式验收/状态更新以及下一合同裁决；G4/G5/STEP008整体和真实provider仍不在本次通过范围。正式docu/公共库未改，无提交、推送或安装。

[本次证据索引](../evidence/task-089/windows-completion-01/index.md)定位pre/精确diff/as-run/post、原始日志、实际加载hash和顺序轨迹；[统一预算](../evidence/task-089/budget-manifest.json)及[断点](../evidence/task-089/checkpoint.md)保留历史。旧real-01的19项中1项测试构造失败和TASK088越界均未抹除，本次通过不追认旧操作。

上次统一结果保存被自动审批服务以额度不足拒绝执行（非不安全判定）；本次继续后正常审批完成保存。没有因此重跑验证或绕过审批。

---

# 以下为原结果全文（历史；旧凭据停止门已由收尾01具体授权解除）

# TASK-089 / R-083 — G3收尾与下一业务闭环合同

结论：部分完成；三组确定缺陷已修复，离线44项与真实PG18项通过，下一闭环合同已完成；真实批另有1项测试构造失败记录，Windows最终绑定补证未执行，不能关闭G3。独立初审已完成，最终增量审计见独立报告。

## 入口与授权

实际项目根 D:/shspic/project_NO3_RetroLume-agent，Git基础45951501d2741630a229762d6b2d3f4b34d7f702。需求v1.1、架构v0.54、执行状态v1.74。保留全部已有未提交差异；不更新正式docu/CHANGE、不提交推送。

主执行客户端Codex；系统标识GPT-6，实际后端型号/推理档未提供独立查询凭据，未虚报已切换型号。新主窗口；审计子会话TASK089/Audit以fork_turns=none创建，不继承本聊天、实现者记忆或自评；另设TASK089/Next只读设计子会话。主执行唯一产品与资源owner。

已读根AGENTS.md和公共规则D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD（卡载版本2026-09-28T14:08:37.3969855+08:00）。执行者按卡读取必要合同，没有接管全局WORK编排。批准权威为087-work-decision P1—P5、088完整功能合同及089运行/收尾细化。

## 证据入口

- 本卡基线：Ndocu/evidence/task-089/pre-hashes.json与pre/；21项均匹配088 post清单。这只证明接收现场一致，不倒签历史运行hash。
- 受保护文件：Ndocu/evidence/task-089/protected-hashes.json。
- 单一预算账：Ndocu/evidence/task-089/budget-manifest.json；断点checkpoint.md。
- 独立审计：Ndocu/results/TASK-089-independent-audit.md（仅实际审计者写入）。
- 下一合同：Ndocu/results/TASK-089-next-contract.md（仅设计，不实施）。

## 旧088事实与本卡分账

1. 5个批启动、5容器，相对原上限3批/1容器的历史越界保持，089授权不追认。现存5份manifest记录的wall_seconds合计518.766秒，仅是各runner自报值，不涵盖无法证明的批间准备/全部操作耗时，不能代替完整合规计时。
2. 规范路径Ndocu/evidence/task-088/pg-run-01确实missing；有限文件定位找到原件backend/Ndocu/evidence/task-088/pg-run-01/manifest.json及runner.log。已记录创建、ready和停止，没有迁移/测试完成日志。原件不移动、不改写；不是089补造的旧记录。
3. PG02原日志01—09 ok，10超时；PG03为10失败、11—15 ok；PG04仅10 ok；w1两个场景complete。是否适用最终快照须由审计逐项判断，不能由总数代替。
4. 原离线“Ran57，skipped15”只可能有42个非跳过执行，报告“57全过”不正确；未找到该命令离线原始日志及运行hash，不伪造。全仓138的两个失败仅有执行者解释，缺原始证据，不能确认预存或环境根因；本卡不重跑无关全仓。
5. 旧manifest mounts_unknown及端口键名不足证明当时完整配置；今天的只读检查只能证明检查时点。现存runner将口令放入docker参数/环境的历史事实也须单列，不能写“从未进argv/环境”。

## A—D交付情况

| 成果 | 实际状态 |
|---|---|
| A 独立完整初审 | 完成。TASK089/Audit新隔离会话先冻结21项，形成A1—A3及证据缺口，再由主执行集中修正；初审后才读088摘要核真实性，接触面由审计者披露。 |
| B 修正与定向验证 | A1—A3已修；离线两次只运行需要覆盖的用例，合计44个非跳过通过。真实PG一次19项，18通过、1个错误测试前提失败；修正该前提后只补离线预算分支，通过。最终产品hash与PG18项实际加载一致。真实Windows补证未跑。 |
| C 最终独立判定 | 已完成第一轮增量终审。独立报告C节确认代码增量通过、动态证据部分充分、089已观察执行合规/088偏差保留、资源收尾通过；唯一关闭阻断为最终hash绑定Windows链。原初审保留，主执行不代签。 |
| D 下一闭环合同 | 完成，见TASK-089-next-contract.md。明确G4范围修订权威、read_scope/CAS、锁后集合复核、持久父成果→新操作准入、取消/未知不重发/预算不复活；G5是工具计数，不扩成新业务。只读设计没有提前跑实验或实施。 |

## 实际补丁与最终快照

相对本卡pre共7个既有文件变化，新增6个task089测试控制文件；其他产品、旧runner、旧证据和正式docu均未写。完整SHA256见`Ndocu/evidence/task-089/final-hashes.json`，逐文件最小diff见`diff/`，变更文件最终副本见`final/`。

| 文件 | 修正及最终SHA256 |
|---|---|
| backend/app/worker/one_call.py | record_denied和record_unconfirmed统一UNKNOWN/unconfirmed；decoder严格核status/error/commit配对，record错误不得挂其他状态。`cb1bf3f2440c6727311fb2a8af27d1b9668a6abc1ef00c84e6ff4e465ce57727` |
| backend/app/activities/repository.py | 历史正文同值确认前比较结果admission/G/scope与锁内操作权威；损坏拒绝，合法取消后历史确认保持无写。`a31e7d770b9f8746bfe66dd4fc7ea946b195eca21b029b370940810fd0a938b2` |
| backend/app/capabilities/gateway.py | 只修正文档，删除AdmissionDenied必然证明事务回滚/无既存结果的过强描述。`3951ad65c27fb2e2cc0eb361a1a98c4b491b2fd9ccddfd15f3f676e17f468345` |
| backend/tests/test_activity_results.py | 提交配对正反例；实际发送数和并发双成功分类；历史绑定/新正文各失效权威/存储篡改与驱动取行投影反例；分页编码独立离线边界。最终`16fb3a25712af545daa61fc6f6765bed610ccc8c25784e7b5968f658f71c71f8` |
| test_activity_ledger.py、test_activity_recovery.py、test_activity_time_budget.py | 仅撤销088新增的不必要results清理，三文件均与088 pre字节hash重新一致。没有运行旧全表清理；这不承诺旧006数据库可以运行依赖007的当前产品。 |

task089夹具：controlled_child逐字复制task085同名受控Job控制器；win_chain/bootstrap复制task088，改新库身份/仅一json场景/单次发送防护与加载指纹；offline、real_batch、check_runner为本卡控制。产品不依赖Ndocu。未新增008、未改001—007、gate/windows_job/supervisor_ipc/transport安全主体及预算模型。

## 新验证原始账与适用边界

以下命令均在项目根，解释器为现有`backend/.venv/Scripts/python.exe`，无安装依赖。原始stdout/stderr单份保存在相应目录，测试计数不包含子断言数量。

| 命令（均python -B后参数） | 原始结果 | 时间与绑定 |
|---|---|---|
| `backend/tests/fixtures/task089/offline.py offline-01 tests.test_activity_results tests.test_capabilities tests.test_worker_one_call tests.test_worker_session` | exit0；发现62，非跳过执行43，skip19，43通过/0失败；原始日志offline-01/ | runner1.875秒，工具端到端3.8463014秒；as-run和加载模块hash、source_unchanged、外层树零/句柄关闭均记录。 |
| `backend/tests/fixtures/task089/check_runner.py` | exit0；6文件编译/AST静态检查，docker仅inspect/start/exec/stop、单账、精确收尾、无口令argv；三旧测试与088 pre相同 | 内部0.047秒，工具端到端0.3524394秒。静态检查不是超时故障注入通过。 |
| `backend/tests/fixtures/task089/real_batch.py` | exit1；7迁移成功；19PG项实际执行，18通过/1失败/0skip；Windows0，失败即未进入该阶段。原始real-01/ | runner24.922秒，含预检/准备/起停；最终产品hash全部匹配该批。外层Job树零/句柄关闭、容器Running=false。 |
| `backend/tests/fixtures/task089/offline.py offline-02 tests.test_activity_results.ResultPageBudgetOfflineTests` | exit0；发现/执行/通过各1、skip0、失败0。只补新分页编码反例，不重复43项 | runner0.610秒，工具端到端1.3068394秒。使用数据库投影行替身执行真实list编码分支，不冒充PG资格或真实provider。 |

**real-01失败保留及修正**：新增test19错误地假定200行长ASCII元数据必超256KiB，实际未触限而断言失败。它不是已确认产品缺陷。先核测试文件仍等于as-run哈希，保存`real-01/as-run-test_activity_results.py`，再移除这条错误前提；新离线用例验证200行ASCII可返回、100行多字节元数据可返回、200行多字节元数据超过总页预算明确拒绝。多字节投影样本不声称供应商正常生成。未改产品编码逻辑、不倒改失败日志。`final-applicability.json`按AST核实其他18个PG方法及其共同夹具未变，按SHA256核实产品与该真实批一致；因此复用18项通过，不把失败批改称全通过。

**本卡停止门及责任**：real_batch在PG测试失败后完成精确收尾并退出，随机新库口令随资源owner内存生命周期结束；没有预留可续批的凭据内存owner。这是本卡runner组织上的不足，导致剩余2次许可无法安全接续，不是用户少给了运行额度或登录信息。按第7节凭据丢失即停真实部分执行；不重置新旧角色口令、不读取旧Env/密码、不绕认证、不另建容器/库。未向用户追问普通修复。下一次若需真实补证，编排必须给具体凭据/资源生命周期授权，不能直接重跑现runner；现runner也会拒绝已有attempt。

预算单账最终扣账：离线5.5055802/1800秒（端到端），真实30.234/2400秒＝批实测24.922＋只读观察0.312＋解释器/启动未单测部分保守扣5秒；30.234是保守预算扣账，不伪称精确实耗。1/3总批，Windows0/6，新容器0、新卷0。原始更细计时保留于manifest，余量不绕过凭据停止门。主动工作前段00:15—00:23后遇额度中断，07:21用户明确恢复；暂停没有在途资源，累计主动时间未到6小时，不清零运行账。

## 批准矩阵覆盖索引

采用087修正轮01并由P1—P5覆盖冲突文字。087矩阵没有定义T07—T09，不虚构用例补号。

| 合同项 | 最终证据及限制 |
|---|---|
| T01—T03、T17 | offline-01 PayloadEnvelopeOfflineTests、GatewayCommitConfirmationOfflineTests；真实字节限额、伪hash/结构/同存同缺、received失败无成功正文；不采用64KiB必扩张超128KiB的错误前提。 |
| T04/T06b | offline-01 ProtocolThreeOfflineTests含新增status/error/commit真值表；经外帧还原后再执行实际nested decoder。仅协议层，不冒称完整监督运行。 |
| T05/T16/T16b | real-01 test12/13/18：状态、来源/空集合/scope、行绑定、当前存储hash重验、驱动fetchone处失效正文None；列表test14。缺失source行受FK约束，LEFT JOIN防御分支静态确认，不假造坏FK。 |
| T06 | offline-01 test_n1_early_rejection_before_claim，one_call两入口claim前拒>120，idle域未收紧。 |
| T10/T21 | PG成功提交/read和结算组成段由real-01 test03/08/15支持；088 w1两例为历史真实接线证据但无as-run hash。最终Windows一体接线本卡未执行，是未闭合证据，不能写最终全链通过。 |
| T11/T11b/T12/T20d | real-01 test03/04/05/16：终态同值、无正文/异文冲突、关门拒新写、取消/G变化后无写确认、三种损坏绑定拒绝。专门“settle后再重放”没有单独新动态断言；相同历史分支静态支持，不伪称该精确轨迹跑过。 |
| T13/T13b/T14 | real-01 test06/10/11/17，来源及取消先后锁屏障、取消后不额外结算、permit/G/scope/lease/executor逐项拒新正文。recover_unknown后续收敛未新增动态复验，旧代码未变，不把088报告沿用068的口述当本卡原始通过。 |
| T15/T20c | real-01 test15，实际settle锁等待连接终止前失败与真实提交后丢响应分开；R残留才折叠，R0不重复加账，正文保留。 |
| T18 | real-01迁移001—007原始事件及test01/02，旧received不回填、重复007回滚、FK/约束；仅新合成库。 |
| T19/T20a/T20b | real-01 test07/08/09，真实事务先UPDATE后INSERT触发器失败回滚；真实super.record返回后抛丢响应并read恢复/发送恰1；双连接结果严格RECORDED＋ALREADY_PRESENT。 |
| 页预算补项 | offline-02真实编码分支边界通过，数据库投影替身；错误real-01 test19仍记录为失败。 |
| T22 | 原合同可选，未运行、不构成新增门槛。 |

## 资源最终状态与交接

real-01只复用获准w1 CID；运行前原始结构核对名称、imageID、Mounts Type/Name/Destination/RW、loopback HostIp/HostPort、1CPU/512MiB/pids128/restart=no/无特权、Running=false/Pid0及独占端口。安全字段没有unknown放行。

仅经容器内既有受信管理连接创建`retrolume_task089_g3`和新LOGIN角色`retrolume_task089_synth`，无超级用户扩权；001—007及所有合成测试仅操作新库。随机口令走owner内存→psql stdin→受控子进程专用环境，不进入argv/日志；未读取旧私有Env/DSN，不改旧088数据/口令/pg_hba。受控子进程PID42184、创建时间134351117108524988已记；Job树零和自有句柄关闭可查process_events。合成库/角色与所有旧容器卷保留未删。

`final-resource-observation.json`在2026-09-29 07:31:14+08:00精确只读核五旧CID均Running=false、Pid0；仅w1由本卡起停，其余不启动/改动。今天状态不替代历史隔离证据。

编排需要处理的真实事项：按独立报告保留G3未关闭；唯一关闭补项为最终hash绑定Windows链。上表精确轨迹未单测属于覆盖披露，不另扩大独立审计要求。安排补证时单张具体卡先解决合成目标库/角色和内存凭据生命周期授权，保留本卡1次已用批历史，不自动继承或重置；不再重复已充分的PG/离线。D合同可独立裁定，不因G3未关闭就重开设计。正式docu/CHANGE只建议登记本结果、独立审计、下一合同三份文档及已有偏差，不由本窗口写入；无新TASK/R占号、无提交/推送/服务/付费模型。
