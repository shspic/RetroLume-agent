# TASK-104 / R-098 review-02 — 两文件修复与新增证据独立增量结论

完成时间：2026-10-07T13:55:48.551083+00:00。许可TASK-104-G9-REVIEW02-20261007。结论以本轮末次308对象冻结为准；原104历史原字节附在后面。

代码：通过本次两文件及直接调用影响的有限复核。R104-F01准确控制点已修正，未发现本次确定同链回归。

证据：通过本次有限补证。real03真实新效果覆盖回执确认后列表GET挂起窗口；real01/02支持正常确认、卸载重开和回执前切换；real02闭合R104-E01。没有把根批FAIL或继承条目改成新执行通过。

执行控制：通过本次有限复核。当前版本链、九份真实执行记录、授权写域、旧事实与精确收尾原件一致；保留原失败、保守计费和未知分级。本轮104只读审计的测试、产品/fixture执行、资源启动、SQL连接与业务写次数均为0。

综合：本批准G9有限切片具备交编排关闭条件，建议编排关闭DEF023/P1（R104-F01）及R104-E01。此处不代签G9或父STEP013，也不宣告M-1、真实provider质量、部署或项目验收。原O01—03仍是非阻断观察，DEF019—022沿首轮既定有限结论，不重开。

## 当前对象、依据与独立性

继续实际完成首轮104的独立窗口；原101审计历史未清空，未参与102/103实施或本次修复，其受限披露已由本卡明确接受。运行客户端是Codex桌面，本会话系统声明基于GPT-6，具体部署型号不可见；A+是本次资源标签。未读取TASK103结果、自评、work-decision或实现聊天，未接管共享状态。编排输入仅用于对象身份、原件导航及执行账定位；在读取本轮运行判断前，先独立写入[source-prelog.md](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/review-02/source-prelog.md)。

本轮重读入口和有效任务卡，复用同窗已读且指纹未变的V4.0/公共AGENTS CHG-0003、WORK适用章及阶段07正文；七份锁定规则和两份父合同指纹匹配。需求v1.1、架构v0.94、唯一执行动态v2.16作为卡面合同身份，本轮不读其通过性判断、不修改正式DocuS。

308份当前文件与308份完整post分别核SHA，一致；原297基线中293份未改。允许差异只有两源码及dist index，移出旧JS、新增替换JS和十一份r03测试/fixture；保护域无增量。原104已审291份对象的旧SHA全部链接本轮297基线，六份首轮104 fixture也未改。证据见[初始身份核对](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/review-02/initial-identity-check.json)、[完整post核对](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/review-02/complete-post-check.json)、[基线继承核对](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/review-02/baseline-inheritance-check.json)和[末次冻结](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/review-02/final-identity-check.json)。

- MemoryWorkspace.tsx：pre aebaf2e520177519e53f34699558ab780e72f4c636157284ac15d27ef7610684；当前/post 6102079c19c5874ad0c204e787162871e2eb2b420db059e49c3046db04b00286。
- memoryIntents.ts：pre b6c6080f3714df6d38c54d19721b3778db73f0095286bb1a2e4b9f666d2ed890；当前/post aed035d2def4c852af65e77c6f171917c830ef1e87939b889ab1706171fcda9a。
- 当前index-GgrE4smT.js：773924字节，SHA cdb6fa381256cb3128433f4ab1dfbe1b6c0fd4087e379b9bfcfed002e2abd52d。CSS、pdf worker原字节不变。旧index-D7dvfnOT.js只作首轮缺陷对照，不为新guard签证。

## 问一：F01关闭及同链回归

[MemoryWorkspace.tsx](D:/shspic/project_NO3_RetroLume-agent/frontend/src/activities/MemoryWorkspace.tsx:131)第131—173行固定提交时lifecycle、owner、完整ID/version/revision/body SHA、read/edit序号。回执后允许核自己的持久意图，副作用分别由sameInstance、sameEditor、unchangedEditor约束；旧保存离开原编辑身份后不能再清稿、写旧错误或选回A。两处保留新输入分支在await refresh后再次核sameEditor；正常分支清稿后重核身份和edit，再以unchangedEditor约束列表和最终select。原首轮135行缺失的后置检查已补齐。

正常select自身递增readSequence后，detail与本机草稿读取由select的新序号保护；execute不在select完成后再要求旧序号才能确认，finally以sameInstance解忙。实际正常新建v1和正常修订v5显示及清稿成立，排除了“加guard导致所有合法确认失败”。当前实例切B时清notice，旧catch按sameEditor抑制；同实例busy仍属于在途请求，卸载/token effect更新则使旧finally失效。effect的owner、初始草稿、caps、列表回调也核lifecycle，cleanup增加lifecycle/readSequence并abort旧detail，旧实例不能以重开后的mounted=true恢复资格。

[memoryIntents.ts](D:/shspic/project_NO3_RetroLume-agent/frontend/src/activities/memoryIntents.ts:78)第78—90行在openDb之后及事务get成功回调内分别核current，随后同步delete原完整草稿key。开库/get期间的新编辑或卸载使条件失效；回调之后的新编辑写事务排在既有删除之后，不会被该删除吞掉。依据为源码及[W3C IndexedDB事务规范](https://w3c.github.io/IndexedDB/#transaction-scheduling)：请求事件内事务有效，重叠写事务按创建顺序调度。error/abort返回false、事务失败回滚；不声称本轮运行了IDB故障注入。

新增函数只由execute调用，key仍含ID/version/revision/body SHA/owner。业务键、canonical请求摘要、待发正文先保存、回执key/id/action/hash匹配、refused/unconfirmed分类、显式同键恢复及intent清理语义未改。原恢复证据仅在这些未改部分继承，新guard和条件删除则以本次源码、规范及对应实际正常/晚到原件裁定；没有把未改恢复路径说成新增修复。

结论：F01关闭，未发现本次确定相关阻断。源码推导属于B级；准确窗口及持久效果属于本次已有运行的A级原件，不是本审计新运行。

## 问二：准确竞态窗口、持久效果与兼容性

real03原始[p1-post-controller.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/audit-repair-03/groups/real-03-r03-p1-unique-effect/browser/p1-post-controller.json)和[p1-confirmed-refresh-controller.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/audit-repair-03/groups/real-03-r03-p1-unique-effect/browser/p1-confirmed-refresh-controller.json)记录严格顺序，时间均UTC：

1. 12:35:14.365取得实际POST 200 committed，14.376交付回执。
2. 14.378才发起后续真实列表GET，14.432取得其真实200并挂起交付。
3. 15.032时用户已明确载入干净B、detail及本机草稿核对完成。
4. 15.416释放旧列表GET，15.417完成控制器交付。

这不是首轮C02仅扣住POST回执的早窗口。旧源码在列表await返回后无条件select(A)，干净B的dirty=false会使A正文接管；新源码重核原readSequence及完整绑定，已切B时不发该select。

B是9ca75481-a170-48b8-8e6b-6ebd3fa17b62，version/revision均1，body SHA ae7c86ea0066a2369b007ec107d17eb5be625853caaa68e0ce8b381281a79a65，owner 92229572-3e26-481e-b60a-6095e11ada05。释放前无该owner的B草稿；释放后的完整身份、标题和“B干净正文”与释放前一致，旧A详情GET增量0。其后用户输入“P1之后仍属于B的新草稿”，原始values保留B完整key及正文，旧A新输入也未被删除。case.after是释放后且再次编辑前；p1-after-values/PNG是随后新B输入，不混为同一捕获时点。见[独立准确窗口配对](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/review-02/F01-exact-window-binding.json)。

A是3f6c33b3-ed59-4358-9cd1-63ad2636cbe8，本根实际key 6d84c0ed-5565-4ee0-8a88-6962a443fa49，请求SHA ddcaf538e1395cb5d868af9f66119d5591c4d7c63d13cae44f24786c4ac1186f。提交nonce正文“p1提交时正文 real-03-r03-p1-unique-effect 538e7f”，M5一次effect=true；M2 version6、created_by_key匹配，M3正文185字节/SHA 77342507813cf12c91a5b1a0ad3f34a695c11c961e38adeec998270e26163a1c；M1 head version/revision均6。原始网络请求、回执、M5请求摘要和M2/M3由本审计重新算SHA配对，不凭fixture的PASS字段。

real02的P1 key 0e40d5ab-b091-4bf0-961d-f657a94e9f2d是同内容合法no-op：原version2正文相同，M5 effect=false、revision/version仍2，未生成该key的M2。此事实保留，准确新效果依据采用real03，见[同内容no-op原件配对](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/review-02/real02-same-content-noop-proof.json)。

正常新建A/B v1由real01真实执行，normal-save-values中editor draft及intent为空。real02真实执行卸载重开B、回执交付前切B继续输入、正常修订v5；相应before/after完整身份正文一致、正常修订显示末版并清对应原稿。real03前五项只是继承：正常新建继续追到real01，其余追到real02，本根只有准确P1新执行一项。见[实际/继承场景配对](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/review-02/actual-and-inherited-case-binding.json)。

## 问三：E01最后引用迟到

real02真实浏览器请求activity a29a945b-a58f-4798-b4b3-93cc1e736aed、record e6964ce9-7686-45c3-b8b2-8e247cd25dcf、citation lc_c0655a9aed2099f2e0d9f328。原始[late-citation-controller.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/audit-repair-03/groups/real-02-r03-preloaded-targets/browser/late-citation-controller.json)记录route.fetch取得实际服务200与非空原文；其171字节原文SHA等于冻结original的2cf6d42095064095a7c82760eee133b1ef3f69b1abb7f7a766b154e654e50d80，来源、版本、行/偏移身份均保留在原件。

UTC 12:26:45.561发GET，45.782取得服务200并挂起；卸载旧面板后，46.234浏览器记录net::ERR_ABORTED。不同活动0643576f-0c29-46ce-aff8-2e0653a03b6f的新workspace 47.070返回，head revision1/goal_version1/needs_plan在47.078完成新面板加载；47.078才尝试释放，47.080 route.fulfill返回。

分级结论：服务端200和控制器释放实际成立；delivered_at只证明route.fulfill返回，浏览器该旧请求已中止、没有旧citation response事件，不能宣称客户端解析并接纳过旧正文。本场景验证卸载取消及新身份不复活旧引用；新的教学区域无旧完整原文/引用面板，DOM呈现新head revision1。TeachingCitations及其挂载原字节未改，首轮源码判断继承，不把本次Abort场景冒充单独覆盖解析后分支。

引用阶段浏览器POST增量0。PG捕获是整根之前/之后，非记忆业务表及四账整根相等；所有旧业务行除本轮允许A/B头revision/current_version/updated_at外保持，旧M2/M3/M4/M5原行均保留。没有引用阶段专属PG快照，不能把整根三次记忆效果算成引用写，也不声称原104缺失快照已取得。既有PNG仅作显示布局见证，精确身份和正文依据网络、控制器与DOM/values。见[独立引用分层配对](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/review-02/E01-late-citation-layered-binding.json)。

结论：E01在本卡要求的真实GET200、卸载、新活动加载后尝试晚交付范围关闭。原104三根前置FAIL/浏览器NOT_RUN保留，不能改写为首轮补证成功。

## 问四：最终版本、旧范围继承与执行控制

九份execution的实际as-run原文件与before清单全匹配；每根104个产品/配置/锁文件在before和after均适用于当前，其中前端源码24份。build01仅一次，构建after的四份dist与当前一致；三个真实根实际加载的六份完整JS/CSS副本与当前/网络哈希一致。新JS中可直接定位完整身份guard、条件删除及await后的再核，见[九根版本与加载绑定](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/review-02/all-nine-run-and-loaded-bundle-binding.json)、[产品/构建适用性](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/review-02/unchanged-product-and-build-dist-applicability.json)及[当前bundle片段](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/review-02/new-bundle-guard-excerpts.json)。

实际执行是9份：5 offline、1 build、3真实根；卡面所述汇总“八份”属于数量误写，不能覆盖九份原始记录。必须继续保留：

- real01根FAIL：分页/目标等待超时，正常A/B保存及一次A修订已经产生3次效果，不回退、不重复。
- real02浏览器六类记录PASS，其中正常新建是继承；根仍FAIL，因为原fixture把允许A头版本修改也判成“旧行发生修改”。PG已捕获，按本轮真实允许域重核，而非改根状态。
- offline03原FAIL：把合法effect=false一概判错。real02该no-op和real03后续nonce效果由M5及原正文分别确认，offline05的已捕获核对不算新PG或重放。
- real03根PASS：只新执行准确P1；五项继承不算第三根再次执行六类。

三根网络共有八个不同POST key，均为专用A/B的save/revise；M5八行、七次effect及一个合法no-op，请求摘要均独立重算一致，七次效果各绑定一个M2/M3。三组21表的旧行差异仅A头允许字段，B头不变，专用A/B从未被旧活动选择，捕获域无DELETE/正文删除，非记忆业务表全部相等。见[八POST及持久效果](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/review-02/eight-POST-and-persistent-effect-binding.json)。

固定许可动作前计数与session/receipt起点、截止相符，未重置；闭账hash一致。103修复03计数offline5/build1/entry3/container_start3/listener3/browser3/driver3/memory_POST8/password_reset2，SUP/model/tool/provider、迁移、新容器/卷/role为0。两个RAM口令设置在原角色，三根catalog的角色属性及表/函数/约束/触发器目录一致；源码只有所准ALTER ROLE口令操作，原ACL/成员资格结论沿首轮有效证据，不宣称重新跑全套权限攻击。

103修复03账内offline 9.079秒（含唯一build），real 77.702秒，cleanup 4.375秒，metadata 98.266秒。metadata中40+20秒为保守项，38.266秒实测，精确拆分未知；cleanup处于real墙钟内，不能相减返额或相加冒充独立总墙钟。主动账3270.215秒。原42根加本次103三根合计45，均保留失败投入；本轮104 review-02新增真实根0。

UNKNOWN a392c565-1731-4314-b22e-6cee9458f862及所属activity be3d572f-8e04-4008-96d3-ec4fc99afa6c在三组PG前后完整行不变，requests_reserved4/cost_reserved4000/tools_reserved1/running_settled12/running_reserved20保持；没有退款或重发。pg2旧落点、pg3 pending与原停止主体范围沿首轮，未对其开新运行。

复用实际收尾原件：pg1/2/3精确CID分别4889202d…、f96ac8dc…、4b813f9e…，均Stopped/Pid0，五端口18103/18104/55443/55444/55445释放；六个server/driver PID加出生身份均已终止，自有Chrome精确剩余为空。原件保存完整CID/镜像/卷和端口/出生记录。此为收尾及编排观察时点证据，本审计未启动/停止/连接任何资源，也不把旧runner可读当作执行许可。见[独立控制原件绑定](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/review-02/execution-control-independent-binding.json)。

## 原104继承范围、计费与待同步

首轮七类中真正受影响的第5类/V15、最终字节及控制适用性由本轮更新；未改的完整33项产品审查、后端/SQL/001—010/12函数、角色与清理边界、legacy/v2、依赖资格、四账、worker、停止主体和其他充分原件继续有效，不另签一遍G9旧链。原整体代码不通过仅由本轮F01闭合而更新，原证据缺口仅由新E01原件闭合而更新。原O01—03维持原级别和适用界限，不扩展成新运行硬门。

本轮首读前段未精准测量，于首次登记时保守预扣120秒并固定单调起点/7200秒截止，跨工具和上下文恢复不延后。到交付的主动用量1754.382秒；metadata按实际读取/核证命令墙钟累计，另含首读120秒、已知首段1.5秒及官方规范/显示/文稿未测开销保守补计90秒，合计223.121秒，限额1200秒。本轮仅浏览一页官方IndexedDB原文，未查实现聊天；所有产品/fixture/测试/compile/build/PG/HTTP/browser/模型/业务POST/密码/DDL/资源运行用量为0。具体命令、真实失败和用量见[本轮审计账](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/review-02/session-accounting.json)。

审计自身有四次元数据结构展示错误（列表/字典、计数字段、activities主键字段误判）及多次过宽输出截断；已按实际结构及原始PG/exec修正，仅补未显示范围，不覆盖输入、不冒充测试失败已返额。记录见[audit-mistakes.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/review-02/audit-mistakes.json)。

建议编排只同步DEF023/F01与E01关闭、当前冻结及九份记录的准确数量/继承关系，按有效授权完成有限G9裁定；没有新增业务修复或用户操作要求。共享DocuS、TASK/R/DEF/CHG及其他结果由编排维护，本次均未改。

原104报告21896字节，SHA 54306f7a9e7145f52ef22cdd8c99511f173f9674deda22f2418779ab32d48d3b，完整作为下面历史suffix保留。交付可读性、prefix与suffix字节证据见[delivery-check.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/review-02/delivery-check.json)。

## 以下为原104完整原字节历史

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


## 六 封装与最终计量

最终封装检查点主动计入11666.360秒，含初读保守360秒；加封装/回传预留60秒为11726.360/21600秒。已完成helper函数已测14.219000秒，仅为部分口径；工具/shell/最初读入未逐项精确计量，未知保留。metadata保守记600/1800秒。最终325身份行及291完整post仍相同，三CID Running=false/Pid0、本卡相关Python/Node/Chrome进程0、18103/55443等端口可用；最终核为只读元数据，不恢复运行许可。

完整自有证据与最终冻结检查见[交付核对](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/audit/delivery-check.json)，结果文件保存回读后交回，编排据此维护唯一总账。
