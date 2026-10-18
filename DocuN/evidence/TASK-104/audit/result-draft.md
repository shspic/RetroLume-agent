# TASK-104 / R-098 G9 集中独立终审结果

2026-10-07，Asia/Shanghai。综合结论不通过。最终源码与实际构建 JS 存在 R104-F01/P1 的旧保存后续读取抢回当前编辑身份路径；最后引用迟到补证的三根均在104专用fixture前置失败，浏览器未启动，直接证据仍不足。批准单机有限G9暂不具备交编排关闭条件。

代码轴不通过。证据轴证据不足，限定为新增引用迟到仍NOT_RUN及P1待修，既有已核动态子性质继续有效。执行控制轴在实际次数、身份、固定计时、允许写域和资源停止范围通过，原C01晚计、新fixture错误及取证限制保留，不称所有历史控制均无偏差。本报告不签整个STEP013、V19真实provider质量、M-1、发布或项目完成。

## 一 交付、隔离与实际对象

本卡统一完成源码、证据、执行控制审查，并按许可尝试最后只读补证，达到entry3/3与fixture_offline3/3后停止受影响运行，完成其余核证。产品与原103材料未修改。

四类实际产物如下。

- 本结果文件，D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-104-result.md。
- 独立初判、缺陷、版本和原件配对材料，D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/audit/。
- 新只读fixture，backend/tests/fixtures/task104/中的common、server、run_readonly、preflight及包入口；不导入103旧control，完整as-run字节分别保留在read-only-01—03/as-run-harness。
- 新浏览器脚本frontend/tests/task104-citation-audit.cjs及三根真实预算、前置失败和收尾原件。浏览器脚本语法已检查，浏览器场景没有实际运行，不冒称已生成新DOM、截图、引用GET200或新加载bundle证据。

实际客户端Codex desktop，系统标识GPT-6，具体部署未暴露；A+为接收档位。本会话先前承担TASK101独立审计，从未参与102方案或103实现、修正、验证。它不是字面完全空白的新会话，该例外已在接收与源码初判披露。没有继承102/103实施窗口、聊天、思考或103结果/work-decision。独立判断据原102批准合同、最终源码和原件形成；任务卡、执行动态顶部及原件中合计/oracle判断字段只作路由或声明，不代裁判。未派子Agent。

根目录D:/shspic/project_NO3_RetroLume-agent，task_model，V4.0/公共AGENTS CHG-0003，需求v1.1、架构v0.92、唯一执行动态v2.14、阶段07。根入口、公共AGENTS、适用WORK第4/6/8/9章及07读入；七项锁定指纹与rules-snapshot一致，同窗有效正文复用，未采用后来规则。

[初核身份](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/audit/initial-identity-check.json)共325行，包含291当前文件及291完整C02 post逐字节比较、20保护对象、9规则/原合同与5目标合同。291不是291项产品测试。完整初始到当前[产品差异](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/audit/product-diff-current.patch)覆盖21既有产品文件与12新增产品材料，共33项，包括memory六模块、010、受影响activities/teaching/learning/capabilities、main/config、实际UI与许可证。未只看最近四项。001—009、worker/launcher/SUP/关门/结算、旧测试/锁文件等保护字节不漂移。

关键快照如下。

- 010 CRLF文件SHA-256 33df4bcd8c040035f360cfc21c845e8f54e426832959e41477e67496f733c83c。
- 同文件LF文本SHA-256 915f0ed9bbfd0a4263434dc431c8bd7b8c8d3c40a17b901eead46fe98946ebc6，两种口径不混用。
- MemoryWorkspace.tsx为aebaf2e520177519e53f34699558ab780e72f4c636157284ac15d27ef7610684。
- 最终JS index-D7dvfnOT.js为d2e8179a85dbc10a6f5bf920764f0e3420d051188714235364e81d3106744093，773070字节。
- 最终CSS index-COpEVDbn.css为39bfb4f09992c354b628f8e2542b3e75b46a86d8910a29f3dd2331eeb1ddf86b，10654字节。

## 二 确定阻断 R104-F01/P1

位置为[MemoryWorkspace.tsx:123](D:/shspic/project_NO3_RetroLume-agent/frontend/src/activities/MemoryWorkspace.tsx:123)至145行，关键135行，相关72—105、216、230行。关联102 C2与V15、104第5类。共享DEF归属由编排统一，本窗口不新占共享号。

正常UI可达路径如下。

1. 编辑A并提交保存/修订，execute记录submittedSequence、submittedEdit及identity=A。输入框仍可编辑，用户等待回执时继续输入，editSequence增加。
2. 回执确认时readSequence尚未改变，133行初次比较通过，134—135行进入新输入保护分支并await refresh。该列表GET可以晚到。
3. 在此GET等待期间，用户点仍可用的B memory-open，并在冲突区明确载入B。明确载入按钮只禁reading，没有因旧busy禁用；B详情已完成且没有本机B草稿时，binding=B、dirty=false。
4. 旧refresh返回，135行无再次比较提交序号、完整绑定、owner或mounted，直接select(A)。select递增读取序号并abort当前读；A真正文返回后不触发dirty/编辑变化拦截，94—99行把当前binding、view和标题/正文切回A。

该路径会抢回用户已明确切换的编辑身份，后续编辑可能落回错误记忆，违反当前Must的异步绑定保护。不是坏ID、伪状态或新增能力要求。它属于B级源码确定推导，未新增POST复现，不声称已经发生真实误写。

该遗漏也存在于最终JS。[构建片段](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/audit/R104-F01-final-bundle-excerpt.json)在708220附近直接保存编译代码，能见到初次序号判断后，新输入分支依次await列表刷新、await原ID选择，中间没有第二次身份复核。24份前端源与真实最后构建as-run一致，C01/C02的六份完整实际加载JS/CSS副本与当前相等。因此不只是假定源码将来会构建出问题。

旧C02“仅继续输入再释放保存回执”和“回执到达前已显式切B”两类真实验证保持有效；后者进入133行的提前返回。它们没有覆盖上述回执已确认、随后列表GET挂起期间再显式切B的窗口，不能据这两个子PASS排除本项。

最小统一修正建议是在每个await之后、任何选择/清稿/notice副作用之前重新比较提交序号、完整编辑绑定与owner；旧保存确认不主动选择已离开的ID。回原103路线只补这一窗口的有辨别力验证，复用原链。104没有修业务。

## 三 七类审查事实与范围

### 1 七表、迁移与最小权限

静态结构与已经定位的实际目录成立，非穷尽权限组合承诺。010 68—176行是M1—M7唯一模型，复合FK、版本/容量/hash、NULL组互斥及不可变触发器按合同形成；新对象无ON DELETE CASCADE。1—63行为单BEGIN内前置，核public/UTF8、核心sha256、旧列/复合键、009触发器和008 kind约束，重复/残迹失败；未改001—009。

273—370行guard与372—419行唯一清理函数的身份语义对应，421—443行拥有者、PUBLIC撤权、精确列权限及purger最小权限在同一迁移事务。definer固定search_path，产品对象schema-qualified，目标只从不可变原manifest读取，没有任意表名/路径或动态删除列表。

[source/app/实际目录绑定](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/audit/sql-current-source-app-live-catalog-binding.json)核12个函数，来源是104第3根真正只读取得的pg1目录。12个prosrc去空白hash均匹配SQL和应用，资格函数STABLE、guard VOLATILE、dependency_line IMMUTABLE；仅purge为definer且拥有者retrolume_memory_purger，search_path一致。普通实际app为retrolume_task103_app，非superuser、非owner/purger成员。新增密码重置前后非秘密角色属性/表及函数ACL相同；新目录不冒本轮实测全部列权攻击。

原非空升级14表32行前后SHA190592af…一致，空010精确反向39语句、无外部FK、原数据/v1读取保留。坏kind CHECK、007列类型、009 trigger、新表/角色残迹各有P0001及整笔回滚等值hash。C01三函数前向的pg1/pg3原行hash、原权限和旧收据身份继承；pg2原14表32行仍匹配。三台旧容器/卷/库/角色均保留，不新连接pg2/pg3。

### 2 来源、事实与固定选择

MemoryCommandInput只接受封闭用户输入，capture不接受observed_count/mastered/support/dependencies权威。repository372—433从实际progress、相关answer/exercise/feedback和固定上游补闭包，SQL201—270核来源、hash、原事件后继及版本/revision/范围。来源/同answer新反馈/修订/撤销使旧选择失效，无关活动/旧feedback注记的原动态不误伤证据可继承。固定ID/version/revision/hash不会自动换新版，记忆只低信任背景，不形成lc_引用、工具授权或当前独立答计数。

C01真实两层上游、漏闭包/无选用/自引用/循环/11来源/ordinal33、跨活动capture/伪hash/伪token均有具体SQLSTATE/HTTP及副作用核对。记忆源切换与待核PDF的有限组合成立，不推成PDF整体解析质量。

受检摘要IDs另有R104-O01/P2。当前真实PG四个记忆正文中的independent_answer_ids与原progress合格独立集合不同，当前答案被闭包集合混入显示字段。原status仍needs_repair/practising且uncertainty=limited，不增加本活动progress计数，不宣称已经误增新活动次数；建议分离闭包相关答案与合格独立集合并明确名称。[实值对照](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/audit/R104-O01-observation-count-live-comparison.json)保留四例，不新增运行。

DEF019按批准最小域成立。同单位保留原Decimal，跨单位在256有效位/指数域内Fraction精确比例比较，超支持域unchecked；原F01完整肯定文法未变。只建议此有限项关闭，不签任意十进制精度或重开已闭G8。

### 3 事务、CAS与v2接线

MemoryLedgerMethods复用同一_transaction，不覆盖旧连接权威。source→M1→相关activities→operations/教学对象→M5/M2/M3的前缀锁接旧后段，锁后头和来源hint复核；不能在aborted事务中续写。首次同键/同槽唯一效果、不同内容409、同内容无效应不占未来CAS槽已有真实PG与源断言对应。

context14—94、teaching_service及adapter从持久recipe/原记录hash/固定选择重建消息，持久context不复制记忆正文；gateway和受信v2 binding接accept/claim/launch/admit/mark/result。旧v1未加默认None键，worker/协议3/4/监督主体保持。普通continue/G7与通用tool拒选择活动，合法teach8t还需旧锁内command/call绑定；字符串前缀单独不授工具资格。

旧真实after_admit与before_result窗保存dispatch_started_at差异、结果/事实新写0、UNKNOWN诊断和预留。相同终态只确认，_terminal_confirmation先于新正文资格。类型/父输入/工具scalar、预算拒绝和无记忆legacy按对应最终变化复核，不据未改函数字面自动排除调用风险。

公开读主要保持同语句资格。R104-O02/P2是read_committed_result/list_committed_results的SQL CASE仍只按来源/scope提payload，随后Python按同快照INVALIDATED_MEMORY丢公开正文；原公开读抑制断言成立，没有证据把这点升级成外部泄露。建议将资格同步纳入这两处SQL CASE以符合更直接的抑制边界，不添加整链门。

### 4 撤销与精确清理

第一阶段墓碑/原manifest/M5先COMMIT，第二阶段只清本ID M3精确version/hash/bytes，再同事务写purge收据和done。重复revoke收据不再次清理，用户明确purge只用原manifest。失败保留revoked/pending，不自动新清单、不删007/009/原件/备份。

原角色反例涵盖app直写/删、GUC、SET ROLE/DDL、PUBLIC/denied执行、临时同名对象；中途第二版删除故障前后两正文保留且hash同、错hash/漏/额外版本零效果、合法精确清理只一次。C01最终canonical TEXT收据已逐字节重算canonical相等；旧非规范JSON TEXT收据原字节可读，不追改旧原件。最终函数的物理缺正文和真实DB不可读例均保存墓碑、收据与正文前后hash及无自动重试证据，不称每个危险组合都跑过。

R104-O03/P2是revoke也进入上下游/来源/活动的宽锁前缀，宽于原本头/收据最小域。尚无实际死锁或不能撤销证据，建议后续局部缩小，不作为新的P1或真实验证门。完整磁盘/WAL/备份擦除、跨库恢复与STEP017不在本验收。

### 5 UI、鉴权与异步恢复

真实factory、local_session/Origin、严格UTF8/重复键/32768流量、列表默认20/最大50及65536响应、IDB owner/key/hash、16摘要/16草稿容量、GET恢复零重发均有源与原行为定位。50项Unicode列表25641字节且无正文/完整依赖；当前单人工作区不虚构租户。用户原答与派生内容的失效公开读分开。

C02实际no_evidence POST响应409/code no_evidence，与六表逐对象和四账相等、SUP/provider0配对。真实陈旧POST409/key未插入、B草稿与旧绑定保留；晚编辑200的请求hash、回执、PG M5和M3正文相同，只保存提交时文本，后续新输入仍在。晚保存显式切换的真实200/网络/DOM成立，但末后PG快照未取得，严格限定层级。均不据旧总FAIL撤销这些性质。

R104-F01仍阻断完整编辑身份承诺。当前TeachingCitations将activity/record/citation/viewToken合成身份，cleanup abort与sequence正确具有B级依据；本卡最后迟到引用没有新A证据，不能只凭“脚本改好”或static代码签通过。

### 6 最终版本与V01—V24适用性

[55份执行版本对照](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/audit/all-run-version-applicability.json)逐份before/after及当前产品差异留存，55是执行记录，不是55个成功根；C01另一个离线导入失败独立登记。291完整post和初始233差异链保留，C02原281对象零变化，仅10验证材料增加。未全量重采所有重复原件。

V01/02/03/10/11按CRUD、版本历史、无效应、原子选择、并发唯一槽及C02 CAS实值有限成立。V04/05/06/07/08/09/12按v2消息/recipe、source/PDF/闭包/相关后继、Unicode投影与角色反例的对应最终版本成立。V13/14/16/17/18/19/20/21/23/24按接受恢复、资格/终态/UNKNOWN、读面/重建、精确清理、非空迁移、可靠legacy/v2残迹、兼容层的实际原件及源码变化有限继承；不同前态与穷尽组合、底层worker未知仍保留。

V15部分成立，完整晚引用直接性质NOT_RUN且R104-F01未闭。V22对真实引用位置和冻结原文120/120=1的支持分别核，用户记忆不充当lc_来源；不能用引用位置正确推泛化教学质量。原全矩阵汇总的PASS不替代方法/网络/SQL/Job原件。

[最终bundle绑定](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/audit/final-bundle-source-and-old-native-load-binding.json)实际核24前端源=最后build as-run=当前，六份旧Native完整JS/CSS加载字节=当前。后台teaching_api晚改不影响这24份前端身份，但必须用C02真实no_evidence补该HTTP分支。未做新build或新浏览器加载，旧参数、skip、语法检查或弱断言不升级成当前整批成功。

### 7 执行控制、旧UNKNOWN与收尾

[旧新控制账](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/audit/execution-control-conclusion.json)保留三组结束许可。初轮entry24/start23/listener3/SUP16/browser-driver3/build3/offline4；C01 entry12/start14/listener3/SUP22/browser-driver3/build1/offline6；C02 entry3/start2/listener2/SUP0/browser-driver2/build0/offline3。真实根合计39，SUP38；39不等于39成功批。

初轮已记offline15.453、real539.251、cleanup22.018、metadata548.453、主动含回传保守19020.059秒。C01为12.641/233.702/13.513/413.812及主动12072.453秒；C02为7.906/50.233/2.687/82.5及主动3159.755秒。原metadata保守/重叠、C01 offline03次数晚记、真实COMMIT响应丢失、根失败和worker底层异常未取得均保留，不退额度或猜根因。

本次真实PG只读快照再次核command a392c565-1731-4314-b22e-6cee9458f862仍UNKNOWN，requests4/cost4000/tool1/settled12/R20不变，single_host_single_session_recovery=false按C02配置保留。树零不授退款或重发。旧未收到COMMIT回执key只读核对，未重POST。

## 四 最后只读补证实际结果和自身偏差

新许可TASK-104-G9-AUDIT-20261007，从首次读卡前段未知保守360秒绑定固定单调原点632434.421/截止654034.421，不后移、不借103余额。主动21600、metadata1800、real600、cleanup300、fixture_offline300；本轮真正完成helper/工具时间与初读/shell未知分别登记，不把局部测量当全部精确开销。最终主动计量见交付账，封装/回传仍计入。

本轮实际entry3/3、pg1 start2/3、listener1/3、browser0/3、driver0/3、fixture_offline3/3、允许RAM口令重置1/1。真实43.906/600秒，清理24.2681504/300秒，fixture离线0.264/300秒。正式产品测试/compile/build、SUP/model/tool/provider、业务POST、业务SQL写均0；基础设施例外仅精确retrolume_task103_app密码一次重置，角色属性/ACL不改。脚本AST与Node --check是fixture预检，不是产品测试。

三根原件均保留。

- [根1](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/read-only-01/root-result.json) FAIL。fixture把HostConfig.Binds非空误当host bind，实际Mounts为已批准的命名卷；数据库/应用/浏览器/PW启动0。首版只有异常类型和空message，原异常栈缺失；实际字段和完整as-run定位原因，未伪造旧栈。原cleanup_complete=false是同一错误判断，独立diagnostic实际核三容器全停/Pid0，旧记录不改绿。
- [根2](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/read-only-02/root-result.json) FAIL。fixture参数化LIKE百分号未转义，psycopg在角色查询报ProgrammingError。仅pg1启动；密码/监听/浏览器0。实际pg1已停、资源保留。修正%%为同一个SQL模式，不动产品。
- [根3](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/read-only-03/root-result.json) FAIL。实际普通app与factory已启动，health成功；/api/session前置非200后停止。actual_get给会话入口加18103 Origin，而此入口local_request不默认allow_own_origin。403为固定输入与当前guard源码的B级推导，原HTTP状态/响应正文未保存，不能假称已有403网络原件。目标workspace/citation及浏览器尚未运行，属于104 fixture前置问题，不据此判103引用坏。

工具普通pipe的stdin关闭使根2辅助runner不能接stop输入；初次自有清理helper又因脚本路径不在backend导致ModuleNotFoundError，尚未执行动作。随后按确切PID42564、出生2026-10-07T10:05:31.121556Z和命令身份停止旧等输入进程，原venv父20508已退出；0.8771504秒独立收尾计入cleanup。未停止新根3或用户进程。读取错误路径等metadata失败亦单列保留。

[根3收尾](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/read-only-03/resources-after.json)证明API对应进程已退出、18103/55443释放、pg1 Running=false/Pid0，pg2/3始终停止；容器/卷/库/role/profile/样本保留。本轮没有native浏览器实例。没有取得本卡citation前中后DOM/截图、加载bundle及业务表末后快照；已有Root3业务-before真快照只证明该时点数据，不能称本卡整组DB前后实测一致。GET健康/被拒会话入口无业务写的B级依据与实际零POST/零模型证据保留。

## 五 建议关闭、最小统一修正与未验

建议DEF019、020、021按原批准最小范围和已配对最终证据关闭，DEF022仅no_evidence真实HTTP409与六表四账零副作用部分闭合；这些建议不包含R104-F01或引用迟到，不由104改总账。R104-O01—03为非阻断局部观察，替代/影响如上，不为它们增加全套PG/Windows硬门。

最小后续是回原103路线修R104-F01并补对应await窗口的定向验证；修104 fixture的session bootstrap用法，GET该入口按真实接口不加不支持的Origin，保留各失败及预算，另由编排明确一个增量只读引用许可。固定目标当前无法读时只GET有限选择已有current记录，零补建。需要的是具体剩余性质，原39根、已验方法、角色/SQL/UI字节绑定复用，不能要求为了总批绿而从头重跑。

没有用户真实库迁移/个人数据删除、磁盘/WAL/备份彻底擦除、真实provider条款/容量/质量或任何部署/全Must放行事实。离线整库替换无法从库内墓碑自行检测的限制、缺失worker前态、未取得末后PG快照等不变。当前必要人工只有把本结果路径带回编排；本卡不再请求资源余额，不启动第四根，不更改共享DocuS/任务号/R/DEF/CHG/公共库或记忆。

