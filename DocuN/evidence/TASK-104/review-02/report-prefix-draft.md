# TASK-104 / R-098 review-02 — 两文件修复与新增证据独立增量结论

完成时间：{{FINAL_AT}}。许可TASK-104-G9-REVIEW02-20261007。结论以本轮末次308对象冻结为准；原104历史原字节附在后面。

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

本轮首读前段未精准测量，于首次登记时保守预扣120秒并固定单调起点/7200秒截止，跨工具和上下文恢复不延后。到交付的主动用量{{ACTIVE_SECONDS}}秒；metadata按实际读取/核证命令墙钟累计，另含首读120秒、已知首段1.5秒及官方规范/显示/文稿未测开销保守补计90秒，合计{{METADATA_SECONDS}}秒，限额1200秒。本轮仅浏览一页官方IndexedDB原文，未查实现聊天；所有产品/fixture/测试/compile/build/PG/HTTP/browser/模型/业务POST/密码/DDL/资源运行用量为0。具体命令、真实失败和用量见[本轮审计账](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/review-02/session-accounting.json)。

审计自身有四次元数据结构展示错误（列表/字典、计数字段、activities主键字段误判）及多次过宽输出截断；已按实际结构及原始PG/exec修正，仅补未显示范围，不覆盖输入、不冒充测试失败已返额。记录见[audit-mistakes.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/review-02/audit-mistakes.json)。

建议编排只同步DEF023/F01与E01关闭、当前冻结及九份记录的准确数量/继承关系，按有效授权完成有限G9裁定；没有新增业务修复或用户操作要求。共享DocuS、TASK/R/DEF/CHG及其他结果由编排维护，本次均未改。

原104报告21896字节，SHA 54306f7a9e7145f52ef22cdd8c99511f173f9674deda22f2418779ab32d48d3b，完整作为下面历史suffix保留。交付可读性、prefix与suffix字节证据见[delivery-check.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-104/review-02/delivery-check.json)。

## 以下为原104完整原字节历史

