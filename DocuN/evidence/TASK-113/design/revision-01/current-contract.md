# TASK-113 / R-107 修正轮01完整当前合同

K1—K3已合并到以下完整A—D设计合同，首轮28表事实地图、格式/归档状态、九个隔离加载INSERT分支和两条教学FK思路复用；原件新引用/清理、三控制表同T投影、持久控制权威和切换闭包按本轮重写。STEP017-P1仍recommended_pending，供主控核证后提交唯一采用包，此刻未要求/获得用户批准，未实施、未验证产品。首轮后缀仅作历史，不让实施者拼接旧冲突段。

A+设计角色，Codex desktop，系统身份GPT-6，精确子型号无可核工具。用户指定续原TASK113聊天，窗口ID不可核不冒工具确认，无子Agent/112审计窗参与/共享状态并行写。task_model/V4.0/公共AGENTS CHG-0003，同窗AGENTS/WORK适用2/6/8/TASK_TEMPLATE未变复用，七锁定指纹实核。需求v1.2、架构v1.23、执行动态v2.45、07。

许可TASK-113-STEP017-DESIGN-R01-20261012。首个接收工具实采2026-10-12T06:13:28.613848Z / 1057072062000000ns，新6000秒截止1063072062000000ns；原已观测3261.109/10800、余额7538.891、原准备unknown不清，旧设计许可不恢复。两页关键官方核查用于跨进程文件锁/事务锁，累计6/6，不新增产品研究。产品import/compile/test/build/SQL/PG/Docker/Job/browser/model/安装/费用/删除/Git写全0，用户私配/环境/数据目录未读，源码/DocuS/公共库/旧证据未改。

源码事实和主控K反例为B级；下面协议、权限、格式和轨迹为设计D级，无新产品A运行或独立审计。K1仅是新增DELETE候选的静态并发反例，当前产品无资料DELETE，不登记为已发生丢失或产品DEF。G11/111112已有限关闭，其旧unknown25/R60/count1、13元、626.566及失败/账不重开。可携导出/隔离恢复和永久只读查看只验本切片，旧任务/持续付费工具预览执行恢复、完整NFR005及M-1仍后续。

原首轮59137字节/SHA1ca9cda00bcfb7f01bfd5630d909cea211f90e8951011159be984fb1925dff06完整原字节留尾。只写本结果及D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-113/design/revision-01/。

- [本轮接收与读入身份](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-113/design/revision-01/accepted.json)
- [主控K1—K3事实](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-113/orchestration-receipt-01/design-gap-facts.md)
- [原28表DDL索引，未变复用](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-113/design/schema-source-index.json)
- [原方法索引，未变复用](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-113/design/method-source-index.json)
- [本轮统一引用协议](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-113/design/revision-01/k1-reference-protocol.md)
- [控制与同T闭包](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-113/design/revision-01/control-and-snapshot.md)
- [新权威图](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-113/design/revision-01/relationships.mmd)
- [新格式说明例，非真实包](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-113/design/revision-01/format-example.json)

## A 当前数据与信任边界

### A1 配置和落地能力

[main.py](D:/shspic/project_NO3_RetroLume-agent/backend/app/main.py:28)的Settings只有data_dir、backup_dir，要求已存在绝对目录且不相同/包含。原件位置为data_dir/originals；backup_dir目前没有产品导出/恢复消费者。create_app建立新的本机会话token，挂载资料、PDF核对、活动、学习、教学、记忆、面试和预览路由，lifespan会调用PreviewController.recover/close。这些恢复调用是当前部署的拥有树恢复，不是数据备份恢复API。

[local_session.py](D:/shspic/project_NO3_RetroLume-agent/backend/app/local_session.py:13)校验Origin、Sec-Fetch-Site与x-retrolume-session，localhost自身不是授权。新数据路由复用local_session(request, allow_own_origin=True)，所有GET、POST、上传和下载都受同一本机会话保护；不改资料/PDF现有固定Origin边界。

[start_local.py](D:/shspic/project_NO3_RetroLume-agent/deploy/start_local.py:18)读取受信本机配置，核精确原PG镜像/容器，再启动本次应用。它不创建数据库、不运行迁移，也没有隔离恢复目标工厂。README同样没有产品备份命令。禁止把backup_dir存在或旧架构“已实现”标签当作STEP017已经落地。

### A2 权威地图及纳入规则

下列28表来自当前001—012；不是按历史DATA标签虚构的新表。主键、外键、NULL与CHECK、触发器和权限正文见schema-source-index。导出保留用户能解读的事实，恢复快照保留复原关系所需的严格类型记录，但排除执行控制材料。

1. 来源与版本为material_sources、material_versions。前者的id/title/current_version/revision决定当前版；后者含source_id、id、filename/format、sha256/size/created_at，以及复合来源版本约束。替换追加版本再更新指针，失败不改当前版。两种包纳入全部选中来源的当前、历史和待核对版本元数据，原件按是否仍可回查纳入；旧版不冒当前资格。当前PostgresMaterials没有删除方法，资料DELETE路由也不存在，不能称资料删除已实现。

2. 原件为OriginalStore中64位小写hex内容键对应的普通文件。put先同卷不可覆盖发布、再由仓储提交版本；DB失败可留下无引用原件，不自动GC。read/verify核长度和SHA，拒链接、重解析点、非法键。两种包按数据库引用键纳入原字节，保BOM/CRLF等原貌，不把文本解码后的字节替代原件，也不扫描全部目录把孤儿、私配或控制文件带入。来源事实见[originals.py](D:/shspic/project_NO3_RetroLume-agent/backend/app/storage/originals.py:24)。

3. PDF为pdf_review_candidates、pdf_extracted_pages、pdf_review_pages、pdf_user_supplements。候选含expected_version/revision、pending/confirmed/skipped、提取方法与页数；提取文字含物理页/warnings，核对表逐页记录，补充有独立identity=user_supplement。纳入原PDF、原提取物、逐页核对和补充，维持不同身份；pending/skipped不因恢复就可供学习。TXT/MD的行段位置由原件和locations逻辑重建，不虚构独立持久提取表。

4. 活动为activities、activity_scope_sources、activity_allowed_models。范围锁定source_id/version_id/source_revision，状态是pending/running/cancelled。保存scope_revision、execution_generation、deadline、模型白名单及既有M/R/S/最近settle字段；运行owner、executor、lease等中有执行身份，不作为新部署资格。导出以普通事实解释，恢复对账字段按快照保留，执行身份按B3转换并保持冻结。

5. 模型/工具与正文为activity_operations、activity_operation_results。操作kind=model/tool、admission_id、operation_id、代次/范围、请求/费用/工具预扣、reserved/dispatched/not_sent/received/unknown及usage是权威；结果的payload_format/payload/payload_sha256/committed_at在同COMMIT绑定。四账为模型请求次数、模型成本、工具次数、执行时间；preview账另属第9类。received没有结果行的有效旧事实要标legacy_received_without_payload，不补正文、不制造0 usage。引用可在正文内嵌，恢复须核其原text/hash，而非把所有JSON重序列化后替代它。

6. 教学为teaching_heads、teaching_commands、teaching_records。heads是revision/goal_version/phase及目标、路径、练习、作答、反馈指针的投影；commands有原业务键、request/context/slot hash、retry、状态和结果指针；records保seq/kind/parent/exercise/answer/supersedes、source_refs及一次写定的applied_revision/state_after。model类正文在operation_results，用户/应用事实在records.body，不能仅导出heads或遗漏原回答修订。不可变历史不允许为恢复结果回填新的效果事实。

7. 面试为interview_heads、interview_commands、interview_records。保目标/范围摘要、question/answer/probe/feedback/finish、round/probe_depth、answer_version、supersedes及source_refs。origin=model的正文通过operation_id/payload_sha256回结果，user/application在local_body，历史列表当前有正文容量/资格限制。数据退出是专用受控全量读取，不以分页20条工作区投影冒完整备份；不同目标及资料角色保原语义，不升级用户陈述为验证事实。

8. 记忆为learning_memories、learning_memory_commands、learning_memory_revisions、learning_memory_bodies、learning_memory_dependencies、activity_memory_bindings、activity_memory_choices。头保active/revoked、revision/current_version、revocation_key/purge_state；版本/依赖/命令/活动绑定不可变，body独立存放。revoke先墓碑，M3清理只删本条在线body，原教学、资料、模型上下文和备份仍在。导出默认不带revoked记忆的在线body；恢复也不带该body，保原版本/hash/依赖/撤销/待清理元数据，不把正文缺失叫自动清理成功。已purged或revoked是合法有原因缺失，active且本应存在的body缺失属于损坏。未来view新增删除覆盖必须先挡正文，不能只改标签。

9. HTML为html_commands、html_artifacts、html_preview_budgets、html_preview_sessions。保parent/context、descriptor/renderer/package/content hash及业务结果；独立3次/180秒、starts_used/settled/reserved、每session的reserve/elapsed/state/generation是权威。可携包只导有限描述、输入证据、普通记录和已产生结果说明，固定可执行HTML/脚本分发不是Must。恢复保额度与终态，CID/PID/Job/nonce/key/boot/旧单调时钟和原StopProof不能作为新运行控制能力。PNG缓存和当前attach不是备份必需项。

10. 引用不是一个已存在的通用citations表。证据在学习payload、teaching_records.source_refs、interview_records.source_refs、memory_dependencies、HTML冻结context/parent中，连向实际source/version/页/行/offset/hash或作答/事件。导出以reference_edges.jsonl统一列出原定位与身份，附qualification_at_snapshot和历史/删除/缺失原因；它是派生导航，原引用和正文保留。offset注明Python Unicode code point右开区间，行号/物理页规则不改。

11. 派生检索为[retrieval/evidence.py](D:/shspic/project_NO3_RetroLume-agent/backend/app/retrieval/evidence.py:25)的纯词项/片段基线，未在这28表中看到完整向量索引持久域，也没有当前Redis产品存储消费者。已有Embedding适配或pgvector镜像不等于索引已建立。不把Redis、完整向量或图形缓存列为已存在备份；派生片段可按固定算法从原文重建，未来索引仍属后续范围。

12. 浏览器中pending-intents.v1是localStorage摘要；teaching-intents.v1、interview.intents.v1、memory-intents.v1是摘要，正文分别在IndexedDB retrolume-teaching、retrolume-interview-drafts、retrolume-memory。editor owner在sessionStorage并受Web Locks，MemoryWorkspace的new-id也仅本机。这些不是DB教学历史；浏览器未提交草稿/页面内尚未保存输入不属于服务器完整备份。UI先提示保存或另存草稿，可提供单独客户端JSON下载，标未提交、无服务端COMMIT、无执行授权；不合并成同一DB时点或自动恢复提交。

13. 运行材料为worker launcher/session的映射、manager/worker birth、Windows会话及Job资格，以及data_dir/preview-control中的DPAPI control_key_blob、parent/attach/Reaper登记。ClosingCallGate在单worker内，是永久发送门，不是全应用快照锁；run_supervised_window是阻塞内部入口，PreviewController.open/recover/close也没有数据包恢复能力。上述材料、API key/DSN、本机会话token、私有config、环境、DocuN、Git、构建缓存和临时实验不进入默认包，不从旧句柄或旧receipt恢复控制权。

### A3 同一逻辑时点与统一引用围栏

推荐新增SnapshotCoordinator、OriginalReferenceCoordinator和RootLease，尚未实现。快照先取同根RootLease共享面，再用一个专用REPEATABLE READ READ ONLY连接，首个非事务控制SELECT确定T。流式读取28业务表及A4的三控制表安全投影，最多60秒写受控spool；事务中不等模型、渲染、用户或大量文件copy。事务结束后仅按T不可变内容键复制/hash，共享面持至复制完成。不能拼多个READ COMMITTED GET为全库快照。[已读PostgreSQL事务说明](https://www.postgresql.org/docs/16/transaction-iso.html)仅支持该稳定语义，不冒现场主版本或运行通过。

上传/替换可以并行追加不可变文件；其新引用必须按下面相同根协议保护，所以幂等命中现有hash也不能越过最后清理窗口。模型/tool/preview在途按T原样保未知/预留，不因快照退款。记忆body的并发DELETE由MVCC保T，T后的删除另有恢复覆盖时点，不无痕改已完成包。

拟新增OriginalReferenceCoordinator，单Windows部署、一个源业务库与一个原件根绑定一个originals_root_id。根重定位、同根多库、多主写者、外部绕过生产接口的文件操作不在此切片内；绑定不符拒绝启用清理。不得用内存RLock代替跨进程协议。

OS层RootLease为固定、不会被替换的控制文件同一字节范围的LockFileEx共享/排他锁。每个线程任务单独非继承句柄，不把同句柄可重叠锁用作升级；捕获文件对象身份，禁止unlink/replace锁文件。共享用于完整引用建立和快照copy；排他用于逻辑删除及物理最后判据/unlink。实际成功获取为资格，超时/未知/进程退出不靠墙钟或PID推断自动取得锁。Windows锁随句柄关闭/进程终结由OS释放但可能延迟，未实取排他不能清理。依据[LockFileEx官方定义](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-lockfileex)，未运行API探针。

PG层统一根键的事务级advisory shared/exclusive fence覆盖所有原件元数据新引用。根键由受信绑定ID确定，不由请求或包给。引用事务先shared，清理事务先exclusive，再按源→记忆→活动既有顺序锁业务行。它用来等待已进入DB的事务结束，不代替OS文件锁。事务级advisory锁结束时释放，依据[PostgreSQL锁说明](https://www.postgresql.org/docs/16/explicit-locking.html)，本次未连接DB。

来源PG拟data_control增加originals_root_id/reference_epoch。拟data_operation_jobs中record_class=reference_fence是源侧引用准入事实，不是长期数据job进度权威。它含prepared source/version/candidate ID、sha/size、root_id/epoch、state=open/committed/rejected/ambiguous/cancelled和私有pin_nonce_sha256；私有owner/nonce不出包，公开仅历史安全投影。创建票据的固定函数只有受信协调器可调用，不由客户端文档字段或任意SET自称。材料元数据INSERT/指针激活的新增guard校验已绑定票据，不能直接SQL绕开。原九个隔离加载INSERT分支和两教学FK另行保留；这是K1新增引用围栏，不替换它们。

正常引用顺序

1. 请求有界接收/验证后，服务端prepare_reference生成原件hash及预分配source/version/candidate ID，取得RootLease shared并检查控制选择代次没有维护fence。
2. 短事务登记匹配root/epoch和随机私有nonce的open票据，确认其COMMIT。失败或未知不发布/复用原件。
3. 在同一live ReferencePin中调用OriginalStore.put/verify，包括FileExistsError幂等命中，核实际hash/size；PDF解析失败可以留孤儿，但不能提交新保留引用。
4. save/create_pdf_candidate/confirm_pdf_candidate以reference_pin和prepared IDs为必填内部参数。引用事务先PG shared，再核票据nonce/epoch/state及已取OS pin，然后业务行锁、INSERT引用、在同COMMIT把票据改committed。API只返回普通业务收据，不返回pin/nonce/锁键。
5. 至少确认该事务COMMIT或用预分配ID读取核实结果后才正常释放shared。明确rollback/rejected保旧成功项，已发布无引用文件仍可留，不自动GC。COMMIT丢回包保ambiguous，有限核对期间持pin；无法核清可终止本请求、留下持久票据并拒清理，不能标not_committed。

进程死亡或shared已放而DB仍可能延迟提交时，不用一次SELECT没行证明没有引用。清理必须取得OS排他，再取得PG exclusive等待在途引用事务；随后在单独短事务取消所有旧未决引用票据并推进reference_epoch，确认该取消COMMIT。排他OS仍持有。旧排队SQL即使稍后获PG shared也因旧epoch/已取消票据拒绝INSERT。该取消结果未知就不unlink；不得把取消与物理unlink放在一个可能rollback的事务中，使票据又恢复open。

确认取消后，在第二个READ COMMITTED短事务再次取得PG exclusive，取得锁之后才用新语句查询全部保留引用。查询保留所有未墓碑来源的全部material_versions，包括历史、current_version=NULL的待PDF及候选；共享hash任何一条保留引用成立都保文件。核本删除manifest及源修订、普通文件身份/hash/size后，在同一OS排他+PG排他期间做唯一准确unlink，再写清理结果。检查到unlink之间不放锁、不释放epoch围栏，不在这段等网络、模型、渲染或用户。单键5MiB/有限时间，失败记pending/physical_result_unknown；若结果COMMIT丢失只核单键/旧收据，不再盲unlink。源DB或票据资格未知一律不删。

删除墓碑提交和之后精确文件清理是两个阶段，各自重新取排他；中间允许新的成功导入，由后段最后引用查询保护。快照持shared直到复制完成，使清理只能在T文件闭包结束后进入排他。文件入库的无引用孤儿不是自动清理授权。

必要入口

- materials.upload的新TXT/MD、替换、PDF候选，pin在put之前取得并跨run_in_threadpool保持，直到save/candidate的持久结果核清。
- PostgresMaterials.save/create_pdf_candidate不得在013启用后无pin直接造版本；预分配ID用于未知COMMIT核对。
- confirm_pdf_candidate激活指针同样校验pin/票据/墓碑；旧候选的已有保留引用仍纳入最后判据。skip不解除所有历史保留引用，不凭current_version=NULL视作可删。
- 其他直接元数据入口必须经协调器和新增guard；活动/记忆/HTML只允许引用仍保留且未删除的版本，不能靠激活已墓碑源重新保留已删键。
- 恢复工厂在独立target原件根建立target RootLease，发布文件及metadata加载全段持shared，使用绑定的loading身份。target没有在线GC，加载失败只封存；包不能选择源根或取消源票据。

锁序为控制选择读取→MutationPermit→OS RootLease→PG根advisory→引用票据→源/记忆/活动锁。控制journal锁只短时读/追加，不能持它等待RootLease/PG；清理不能在source行锁内反向取RootLease。模式fence发起先拒新permit、允许已登记收尾，之后才等排他。丢失pin/连接/模式代次拒绝继续新引用，不做自动锁升级。

修正前D已查A外无引用，B无共同锁复用F/提交vB，D unlink F，B缺原件。修正后若B先得shared，D的排他等待B COMMIT，最后查询发现vB保留F；若D先得排他，B在put之前等待，D精确删后B重新发布F再提交。B死亡或提交未知时，D需PG等待/持久取消旧epoch及第二次最新查询，不能利用OS句柄已释放直接删。全部为手工推演，无真实竞态运行。


### A4 三控制表与T闭包

三个同T载体

- data_control只读投影源dataset_id、schema_profile、created_at及instance/mode的observed字段、已知来源snapshot/摘要；排除live mode写票据、root epoch授权、选择器、秘密和可执行实例。源PG的同一个REPEATABLE READ READ ONLY连接用snapshot角色读取，写入metadata/source_control.json；manifest记其hash/观察时点。不读取ControlHub实时state补进T。
- data_operation_jobs只读投影source row ID、record_class、原业务键的普通历史标识、kind、request hash、scope摘要、observed stage/state、package/root摘要、byte/file/row counts、error、created/updated/terminal及control_event_seq observed。source history mirror可能落后Hub，明示只是T观测；reference票据仅安全历史摘要，排除pin_nonce/owner/active权限。载体metadata/operation_history.jsonl；checkpoint对应历史codec，不恢复成活job/票据。
- data_tombstones投影entity_kind/id、effective_revision、删除时间、普通revocation/business标识、cleanup_state观察、manifest hash和仅hash/size的清单。路径/PID/secret不含。载体metadata/tombstones.jsonl，同T支撑deleted/revoked与引用不可用；后来删除并集在overlays/deletion_overlay.jsonl，明确T2和来源unknown，不伪装同T。

snapshot只对28表白名单列及这3表的安全列/只读view SELECT，不得以data_app成员或EXECUTE写/删除函数补读。三view为data_export_control_v1、data_export_job_history_v1、data_export_tombstones_v1，固定受信定义，security_invoker和必要底层列SELECT对应。一个连接/一个T读取31表安全投影，非多个事务，角色无DML/DDL/服务器文件能力。

目标data_control的target dataset/instance/root IDs、mode=loading和加载绑定由可信工厂/data_owner初始化，source投影仅元数据，不覆盖该行。target data_operation_jobs由restore_loader INSERT record_class=archive_history、authorizes_reference=false的历史映射，原ID置origin_source_row_id，目标history ID按受信codec生成，不保活key/票据；只读data_snapshot_job_history_v1供读，切换后job查询不依赖它。target data_tombstones由loader INSERT包内同T安全行，再按受信计划在seal前INSERT后续删除覆盖；冲突取较新修订，旧行保origin标识，不能把pending清理当目标实际done动作。目标无清理任务授权。

源snapshot LOGIN只成员retrolume_data_snapshot；runtime LOGIN成员retrolume_data_app只读状态/固定业务函数。source不授restore_loader。引用票据/epoch函数只受信本机协调器可用，API不提供任意nonce/根/状态参数。target bootstrap掌握单次初始化DDL/role许可；loader只在新目标loading时有固定INSERT及来源指针回填；seal撤成员/票据，readonly LOGIN有28安全读及3安全view SELECT，无普通DML/退款/旧执行权。data_owner控制函数不从PUBLIC执行，ControlHub私有句柄/工厂凭据由可信host持有，snapshot无此权限。

## B 唯一最小实施合同

### B0 一个推荐方案与采用关系

采用现有Python标准库、PostgreSQL/psycopg、不可变原件库、ZIP_STORED和单机受信私有ControlHub。没有新控制数据库或分布式服务。28业务表是现状，三控制表、31安全域、ControlHub及恢复工厂是拟新增。可携与checkpoint共用严格包，不执行包内SQL/角色/命令；新隔离PG集群先受信schema后数据，避免010/011集群角色碰撞。

长期export/backup/restore/activation job由ControlHub唯一裁定；data_operation_jobs的业务库行只含同T观察/归档史，另有K1引用票据是源PG元数据准入事实，不把两者互作权威。该分工与DB mode屏障/只读范围均列入一个STEP017-P1，仍recommended_pending。项目TASK/STEP状态仍只在DocuS执行动态，不由产品控制日志维护。

### B1 包、独立解读和完整性

格式仍是未采用的retrolume.data-package v1草案，本轮codec/schema_profile明确为data_exit.v1.r01，首轮无产品包可追认兼容；后缀.rldata，容器ZIP_STORED，无加密、执行文件、任意路径或外部URL消费。默认本机私有备份目录手工创建，默认无定时任务；建议用户在重要批次/升级前手工备份，按需要自行复制到第二本地介质。频率与介质是可配置推荐，不启用后台全库外发。

布局为manifest.json、README.txt、records/固定表或领域名.jsonl、references/reference_edges.jsonl、originals/64位hash、summaries/活动UUID.txt。两kind均另含metadata/source_control.json、metadata/operation_history.jsonl、metadata/tombstones.jsonl及其manifest hashes，来自同一个T；checkpoint另有checkpoint/固定table_id.jsonl及codec_description.json和B5的三控制域受限映射；README说明两种包、身份/引用、时间口径、缺失和查看方式。只有服务端固定路径白名单可生成/接收，original_filename只是标签，不参与落盘路径。ControlHub日志、selector、目标私有注册器、活引用票据/nonce不入包，metadata中的mode/instance仅观察字段，不是loading许可。后续删除/最新账旁证放单独overlays及明确T2，不伪装T。原件不重编码，用户/模型文字按纯文本处理；HTML只在.json记录中保有限描述，不生成可自动执行的网页。

manifest包含package_id/kind/version、logical_time_utc、source_schema_profile、可信迁移链身份、应用/codec身份、范围闭包、表/记录/文件计数、各entry的byte_count/SHA、snapshot预算/未决摘要、删除/缺失/可选说明、browser_drafts_included=false以及root_sha256。根hash是删去root_sha256后规范UTF-8 manifest的SHA；不会把自引用hash当校验。逐文件hash与CRC只证明字节一致，不证明可信作者、工具权限或预算事实来自真实服务。已由本机服务创建的包由ControlHub保存根hash完成收据用于核对；Hub live journal/注册器/选择/密钥不打包，未知来源包只能作为待核对数据，不授执行权。

JSON要求UTF-8、无起始BOM、无重复键、非法数值/孤立surrogate拒绝，枚举和字段完全匹配codec。UUID/hash保持原标识；bigint、成本和时间账等用十进制字符串避免JS精度丢失，NULL保持null，array顺序保持；PG text内的payload/request_body/context_body/source_refs/body按原字符串保存并核原UTF-8 hash，不能格式化它们再签原hash。timestamps用带UTC偏移的ISO格式；jsonb的语义结构与text原字节身份区分。

availability为present、deleted、revoked、never_received、legacy_without_payload、missing_optional或missing_required，并给原因和原标识。缺失已删除原件、已撤销记忆body及旧received无正文是有依据的合法缺省，不补空答案。active且应存在的原件/body损坏是missing_required：完整backup失败，不能显示可恢复。用户明确选择“保存可读的不完整导出”才可发布portable_export，completion=incomplete、restore_eligible=false，并列具体缺项；它不替代完整备份。

select支持全本机已提交数据或选定来源/活动。活动导出自动纳入范围、父记录、所选记忆版本/闭包、引用版本和实际所需原件；未选但必要的依赖须在确认页列出数量，不偷偷扩成整库。恢复checkpoint首版只支持一个完整本机数据集，选定子集包不接受恢复，避免恢复半个FK/额度域。已撤销在线body默认不进任何包，历史原始作答和模型上下文若仍属于保留事实则按用户选择保存，不承诺记忆撤销清除它们。

### B2 权威、发布、目标工厂和完整恢复切换

#### B2.1 独立持久ControlHub

受信配置新增RETROLUME_CONTROL_ROOT，本机Windows私有绝对根，与data_dir/backup_dir/restore_root互不包含、禁止UNC/junction/重定向；由可信宿主首次初始化，不能从包或HTTP取根。它不是新的业务库，不因切换dataset/instance改变。host持私有Root绑定、不可继承锁句柄和DPAPI凭据引用，浏览器只用普通业务ID及本机会话。

ControlHub的有界journal是长期数据操作唯一权威。每条包含format/control_id/seq/prev_hash/event_id/job_id/kind/普通受限payload/body_hash/commit尾标；持同一稳定OS独占文件锁追加，flush/fsync尾标完成才算COMMIT。target注册、job阶段CAS、fence、selector_commit都是同一时序事件。state.json/selector.json是可从完整journal前缀重建的缓存，不能独立授权；坏缓存不自动造新job，断尾无COMMIT只读核未发布，中段/hash/根身份损坏失败关闭。确认过的事件不可回退，业务键映射由事件唯一。

[私有控制格式说明例](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-113/design/revision-01/control-format-example.json)给event、target注册和selector缓存的字段，仅示例未建真实控制区。断尾后的新写保持禁止，先核完整已确认prefix并保全原尾；受信修复可从该已确认head另建有链绑定的后续segment，不改确认事件、不用坏缓存重置generation。修复本身不得重发job或改变source模式，只有明确有效事件/模式核对后才解除维护。

控制区保存plans、包完成root收据、target私有注册、原恢复job/收据、当前选择、停止登记、删除索引与latest账旁证及hash。source/target PG仍分别是业务/原件/账事实权威。源data_operation_jobs只是包含control_seq_observed的安全物化观察，镜像写失败不推翻已确认Hub事件；GET/恢复/reconcile不从镜像决定。K1 reference_fence行则控制源引用事务，不能被镜像规则忽略。目标archive_history行不会变活票据。

target注册事件仅可信工厂生成target_id、origin dataset、job_id、profile_id、resource身份、生成根/端口、credential_ref、target dataset/instance及seal状态。credential_ref指私有固定文件ID，blob先持久再commit target_ready；注册器路径/DSN/密码/PID/CID不会返回API或打包。bootstrap/loader凭据每target新生成，seal/失败后撤成员和票据、丢弃；只读连接凭据以DPAPI保护引用留控制区，同Windows身份解密后仅内存/限定子进程使用。源snapshot凭据按受信profile读取。不可解密/缺profile明确不可用，不从包接凭据、不默认改角色/安装服务。

journal建议单frame64KiB、总64MiB、并发写者1、活job256/target32，旁证独立有界文件由hash引用；达到上限拒新动作，不自动删旧控制史。只读重放验证全链前缀，无网络/SQL/外部脚本。受信运维恢复根须保持control_id及完整已确认事件，不能以旧缓存清零job或fence。

#### B2.2 明确签名与发布点

- ControlHub.create_or_get_job(DataJobCommand, origin_context) -> JobReceipt(job_id,business_key,request_sha,state,revision,control_seq)。命令固定kind/业务ID，origin来自受信当前选择；相同键同hash回原收据，不同hash409。先Hub COMMIT再动作，source镜像只观察。
- ControlHub.get_by_key(key,kind)/reconcile(job_id) -> Receipt/known_or_unknown。只读完整journal/cache/精确已登记文件核对，不执行创建、模型、恢复、切换。所有/api/data/jobs/by-key及GET进度走Hub，切换后仍可查原job/包。
- DataPackageService.capture_and_publish(job_id,scope) -> PackageReceipt。按A3取RootLease shared及同T31安全域，copy/hash，manifest完成、写句柄flush/fsync、同卷no-replace，再Hub.commit(published,root_sha)。文件已发布而Hub尾标失败只记unconfirmed，精确ID/hash reconcile补确认，不生成第二包；source镜像失败可之后补观察，不能称保存失败或启动重跑。
- RestoreController.prepare(upload_id,deletion_policy,origin_context) -> RestorePlan(plan_id,plan_sha,package_sha,codec_profile,scope,overlay/latest_status,resource_profile_id)。校包/范围，不建target；后续unknown保留。用户确认plan/hash/只读代价后才verify。
- TargetFactory.allocate(job_id,accepted_profile_id) -> TargetRef。profile由私有可信配置预先给固定本地OCI/版本、root、名字/端口分配范围、创建次数和时限，不取包指令。先Hub.intent，再仅创建本次独立PG/卷/目录，实核CID/image/name/空cluster/普通role基线并注册；碰撞或不确定停本目标，不DROP/recreate、换名绕次数。未配置则restore_executor_missing，签名不留“到时看情况”。
- RestoreController.verify(job_id,expected_plan_sha) -> VerificationReceipt。host从私有引用拿限定bootstrap/loader凭据，受信001—013先安装，再按B2.3加载31安全域/原件及目标覆盖，取真实只读PG/文件/HTTP原件。source不可读不阻独立验证，但不冒最新删除/账已知。
- seal_readonly(TargetRef,verification_sha) -> SealReceipt。PG mode=restored_readonly、全部加载权/票据撤销，只读LOGIN和私有引用可用，schema/view/digest匹配，方可Hub.commit(verified)。源码或包字段不能把mode写为normal。半seal或权限未知不verified。
- MaintenanceCoordinator.drain_for_readonly_switch(source_ref,expected_selection_generation,deadline) -> FenceReceipt。动作/自有实例/模式闭包见B2.4，权限来自可信host及原监督，不给DB恢复loader停止源的权力。
- activate_readonly(job_id,plan_sha,confirmation_key,expected_selection_generation) -> SelectionReceipt(generation,target_id,dataset_id,instance_id,read_only=true)。匹配verified/seal及用户确认→fence/精确源收尾→最新账/删除旁证→Hub.selector_commit。该事件COMMIT是切换点，GET原key可核，不靠响应到达判断。

包/上传目录仍只在可信backup_dir/packages和incoming/.pending按UUID派生，文件发布与DB/Hub不是一个事务，完成点分别标清。控制区文件不在任何扫描打包范围，包摘要引用不成为服务器任意路径读写接口。

#### B2.3 实际受控恢复步骤

新独立集群/卷/根由下一卡冻结，不能借111/112。010/011集群角色残迹拒绝，故不把同集群另库当隔离前提。顺序是身份/空集群核→受信项目001—012→013控制/加载协议→schema/role/函数/约束身份核→可信data_owner初始化target data_control和loading→target RootLease shared中发布原件/加载→预算/正文/关系/删除资格核→只读seal→Hub verified。004/005永远在数据前，不补跑非空迁移，不执行包内SQL，不停触发器/CHECK/FK，不设replication_role。

两条teaching_commands.parent_record_id/result_record_id FK在013精确按列集合改DEFERRABLE INITIALLY IMMEDIATE，正常仍即时，加载活动组件才明确延后；其他非延后约束按真实依赖拓扑。material_sources先NULL指针，versions齐备才精确回填。记忆7表/choices与依赖连通闭包在已有可延迟事务规则内完成，不拆COMMIT造缺闭包。每组件5万行/64MiB/30秒，超限拒绝，不关闭约束。九个仅隔离loading INSERT guard分支保B5，原不可变UPDATE/DELETE和摘要规则不改。[首轮已读SET CONSTRAINTS说明](https://www.postgresql.org/docs/16/sql-set-constraints.html)。

28业务codec和三控制域按A4/B5分别加载，包的source_control不写target身份/mode；操作观察转archive_history，不复活Hub job/reference_fence。load完成后snapshot/readonly角色能读31安全域，loader成员已撤，直接DML/旧退款函数必须被模式门拒绝。恢复manifest声明控制排除、归档占位和当前删除覆盖，不称原控制行原字节恢复。

未知format/codec/schema/renderer/role定义、重复PK、缺required/错hash/非法引用或容量违规均failed；旧SPIKE SQL/任意dump不兼容。失败只回滚当前组件并封存本target，源/旧包不变，不自动清目标或授重试资源。verified不表示选中，选中也只永久只读。

#### B2.4 全应用停线、切换和故障

拟新增MutationPermit覆盖本产品所有公开业务写及内部提交：资料upload/replace/PDF候选/确认/补充/新引用、活动create/cancel/scope、教学/面试/记忆命令、model/tool准入与dispatch、preview open、内部producer、后台补收据/清理。permit绑定control_id/selection_generation/dataset/instance，持至该DB COMMIT/持久核对或dispatch登记点；ModelWindow按原监督登记到最终收尾，不能在HTTP返回202就忘记真实子工作。发布原件还受A3 RootLease/引用ticket，不互相替代。

可信host在spawn/派内部工作之前登记实际父/子/boot/birth和原Job/registry归属，停止只经原SUP/ClosingCallGate/preview.stop及真实证明，不给客户端PID/命令。ClosingCallGate仍只单worker发送门，没有冒成现成全应用停线。新的维护fence先Hub COMMIT拒新permit，再通知已登记owner关闭并允许其已有结算/结果通过受信收尾lane；收尾lane不能新增admit/dispatch或来自包。控制journal锁仅短追加，不能持它等网络/文件/PG。

旧工作收尾确认后，维护者取得跨进程写排他并将源data_control置frozen，DB业务mode门拒全部新DML；普通业务read与Hub GET仍只读。源最新账/删除旁证从专用只读连接持久入控制区，有来源/T2/hash；取不到标unknown，不填0或说最新齐备。没有源停写/当前自有结束资格则maintenance_unconfirmed，selector不变，target仍sealed；历史UNKNOWN留事实，不要求新取证旧25。原ready/D/监督时限不延长，不停daemon/用户工作。

停写围栏跨selector_commit和新只读绑定持续。新app通过Hub选择TargetRef、私有只读连接与target data_control匹配，生成新会话/编辑身份，skip worker/PreviewController.recover，不加载源旧PID/密钥。源冻结/选择提交失败保旧selector并保持维护未确认，不超时自动开写；reconcile只读确定已确认事件/模式后才允许可信操作解除源围栏。已selector_commit但新绑定失败时只读不可用，不回退旧源normal。

源不可读时可依Hub查原job/包、继续独立target验证；latest账/删除索引只是last_known/unknown，激活所需停线证明缺失则不能切换。控制区不可读或journal中段坏时create/verify/activate及新业务写失败关闭，不能从target归档表、cache、旧私配或文件目录推断选择。credential blob已写但注册尾标没COMMIT不授权，selector尾标没COMMIT不算换库。已COMMIT丢HTTP响应则GET同key回同generation，不二次activate。

切换后/api/data进度/确认收据/包/删除/账旁证仍从同ControlHub解析，与当前PG无关；业务GET读新target安全view。选择上下文缺失/target不可连时显示只读不可用，浏览器namespace/owner/迟到响应不能恢复旧提交。本切片只可携退出、隔离副本验证、永久只读核对；不承诺旧活动/付费/tool/preview执行恢复或全部NFR005持续使用。原源普通本机重开保持，后续执行恢复须独立真实范围/最新账/拥有者门，不作为本卡隐含实现。

### B3 状态、额度和控制转换

checkpoint不是原数据库目录的物理镜像。活动/操作/领域业务键、admission_id、scope_revision/execution_generation、原额度上限、所有预扣/结算数、last_settled_generation/seconds、操作终态、record正文与hash、父/资料/记忆版本都保留。restore_manifest同时保存变换清单，区分快照原值、实际导入值、当前有效资格，不能标所有列原字节相同。

不打包live executor/Windows owner_session、owner/control key或hash、nonce/boot_id、PID/Job/CID、DPAPI、临时token、单调时钟控制文件。必需列由受信codec在隔离目标生成不可用的归档占位身份：activities.running_owner_session_id=NULL；running的executor_id为固定archived身份，原lease/deadline只作历史时刻；operation.executor_id同为归档身份。html_preview_sessions仍保preview_id/generation/start_key、state/reserve/elapsed/deadline_at，owner/boot/nonce与两key hash由本次加载产生新随机不可公开的占位，cid=NULL、t0_ns=1、deadline_ns=1+reserve_seconds×10^9仅满足存储形状，标clock_origin=archive_placeholder，绝不视为真实计时或新截止。占位原始密钥立即丢弃，不交给UI/控制者。原StopProof最多导普通脱敏历史事实和原receipt hash；不保可用于当前确认的完整控制receipt，first_stop/confirmation存archived_non_authorizing摘要或null，额度和原已结算状态不改。

DB层新增模式写门，restored_readonly禁止28业务表的INSERT/UPDATE/DELETE，旧HTML函数也不能绕过；应用入口同样关模型/tool/start/recover/settle，只有数据核对/导出可用。既有raw StopProof或PID即使伪造到包中也只能被拒绝/当普通未信任字段，不能确认新树结束、退款、折叠R、推进代次或重发。未知保unknown，running保R>0，preview cleanup_unconfirmed保reserve且elapsed null。来源已失效、记忆revoked、旧目标/答案版本、cancelled/dispatch_closed都不自动变当前。

旧备份可能早于后续额度消耗。恢复副本展示“备份时点的账”，并分列可取得的最新源账及未知差异，不称旧数为最新余额；其业务完全冻结，源库和外部最近账/删除控制索引保留，因此不使用旧快照制造可消费余额。最新旁证本身也不能结算或退款。源仍存活、跨位置/换Windows用户或最新账不可取得时也只支持验证/只读副本，不能保证任意多机共享额度、抢旧工作或通过多个副本获得新旧同一活动额度。旧25只按既有UNKNOWN事实入包，不申请新停止证明。

### B4 删除、引用和旧备份

资料删除为拟新增SourceDeletionService.preview/confirm，不把当前不存在的DELETE接口冒事实。preview(source_id, expected_revision)返回本条所有版本、引用活动、PDF候选、记忆依赖、HTML/预览影响、待处理hash及共享原件计数，签有界impact token。confirm同一业务键/修订/impact hash，用户明确“删除本条资料及全部版本的回查内容，历史关系和旧备份保留”。普通刷新不触发。

提交先按A3取得RootLease排他及PG根exclusive，再按原源→记忆→活动锁序完成短事务：精确核source、插入data_tombstones、current_version=NULL、revision+1，登记不可变删除收据/待清理manifest。待PDF不能再确认或取原件，当前资料/引用读返回deleted，不把NULL待核对来源混成deleted。活动scope保原事实但资格失败；有关已生成学习/面试/HTML历史留元数据及原hash，当前消费和正文投影按依赖失效门抑制。PreviewController只停止该资料影响的准确当前自有session，控制/物理stop与数据库墓碑不混成一个事务；无法确认仍保原preview R及未知，不能为了删除退款。

后续精确清理每键先按A3持久取消旧未决引用ticket/确认COMMIT，再重取PG根exclusive和最新READ COMMITTED查询，保持RootLease排他直到unlink与结果核对。之后按准确hash/size清单逐个核根、普通文件、hash、共用引用并unlink；不是递归GC。只删除本条全部版本的原件，另一个未删除来源的任一保留版本/候选共用该hash就保留文件，但本条回查仍不可用。失败时墓碑已生效、文件清理pending，原单清单和业务键明确重试；删除收据记录确切成功/失败，不称已经物理擦除。不可变版本/教学/面试/操作历史不删，文件名等必要元数据可能仍在受保护备份/历史，UI说明这一范围。

记忆沿已有MemoryService/apply_memory_command及purge_learning_memory，不新增通用DELETE或把purger权限授普通app。只将已提交revoke元数据同步到data_tombstones/ControlHub中带来源/时点的本机删除索引，M3继续按原清单、版本hash和业务键精确处理body。DTO恢复只读投影先检查删除覆盖；memory_dependency_invalid、旧选择/父记录和HTML关联不自动换新版。既有revoked/pending不升级done，旧正文hash/元数据仍在。

已完成备份包含T当时内容；源之后删除不会使这个文件消失。默认恢复计划respect_current_deletions：同一来源谱系可读的当前墓碑/本机索引与包内墓碑取并集，标明其独立时点和digest。目标不复制命中的原件/在线记忆body，资料current指针保持不可用，记忆在有效view里deleted/revoked不可读；快照原始头状态及事件保留并显示覆盖理由，不无痕重写不可变历史和hash。引用marked unavailable，不把略过的文件当传输损坏。覆盖计划及结果成为新的restore_manifest。

用户若选snapshot_only_readonly，确认页逐项说明将从旧备份重新取回哪些已删除内容，仅到隔离只读副本，不撤销当前源墓碑/清理收据、不自动变当前；切换还需B2另一次动作。跨位置没有当前删除索引时，默认为“删除历史无法核对，只读验证”，用户明确按备份时点核对才能查看相应内容，不宣删除并集已知。旧备份、WAL、供应商、实验和用户其他副本不自动删除，也不承诺彻底擦除。

### B5 精确表、角色、私有控制和文件增量

以下均为拟新增/修改，不是当前权限。仍一份backend/migrations/013_data_exit.sql，001—012原件不动，当前28业务表不变，提议3控制表、未来31安全域。新增文件ControlHub不是第四业务库，不引入SQLite/新服务。

- data_control单行含dataset_id/instance_id/schema_profile/mode(normal/loading/frozen/restored_readonly)、source_snapshot_id/source_root_sha256/restore_manifest_sha256/created_at，以及K1 originals_root_id/reference_epoch。工厂/data_owner写target身份/mode/绑定，snapshot只读安全观察，包不能写loading/epoch授权；source frozen仅由受信维护者设置，解除须核Hub状态，非超时自动normal。
- data_operation_jobs增加record_class=hub_observation/reference_fence/archive_history。hub_observation为source端长期job的T观察，列origin job ID/business key/hash、kind、scope摘要、observed_state/stage、package/root摘要、counts/error/时间及control_event_seq_observed，不裁job进度。reference_fence为K1源PG准入事实，另有prepared source/version/candidate IDs、sha/size/root/epoch、open/committed/rejected/ambiguous/cancelled状态、私有pin_nonce_sha256/owner绑定；metadata引用与票据committed同COMMIT。archive_history承载受限安全投影，origin_source_row_id保来源、target history ID按codec生成、state=archive_only/authorizes_reference=false，不作为活job/旧ref票据恢复。
- data_tombstones为不可回退的删除事实，含tombstone_id/entity_kind/id/effective_revision/原业务普通标识/deleted_at/cleanup_state/manifest hash及hash-size清单，源角色受控写。目标加载同T和T2覆盖，但cleanup观察不是目标当前清理许可，不带路径/控制秘密。

ControlHub journal状态/selector/目标私有注册/计划和凭据引用永远在RETROLUME_CONTROL_ROOT，由可信host生成，不能通过loader/data_app SQL复制或打包。参考票据的nonce/actor句柄也不进安全view。镜像来源可核而滞后，Hub事件不因PG镜像失败被撤销。

源/目标/加载/只读权限矩阵用如下并列定义，所有NOLOGIN角色均NOSUPERUSER/NOCREATEDB/NOCREATEROLE/NOREPLICATION/NOBYPASSRLS，由明确bootstrap给对应LOGIN精确成员。

- retrolume_data_owner只拥有三控制表、三个投影view及固定控制/引用/墓碑函数。固定search_path、PUBLIC撤EXECUTE；不授ordinary app该owner成员。必要精确material_sources(current_version,revision) UPDATE及业务元数据SELECT用于source_delete，不能全表DELETE。
- 源runtime LOGIN可成员retrolume_data_app，SELECT安全状态及EXEC固定source_delete/reference_begin/reference_commit/reference_cancel_epoch/control_frozen函数。它们校原业务上下文/根绑定/live pin私有nonce/期望修订或维护资格，客户端不能任给mode/nonce/根/角色。长job的create/CAS/get改为ControlHub；PG函数最多写其观察，不再当job主控。
- 源snapshot LOGIN仅成员retrolume_data_snapshot，对28业务表codec列及data_export_control_v1/data_export_job_history_v1/data_export_tombstones_v1的固定SELECT。security_invoker view所需底层安全列也按名单SELECT，不含nonce/hash/owner活票据/私配/控制区访问。一个DSN/连接/REPEATABLE READ T读31安全投影，不能授data_app写/删除EXEC来补读。
- 目标bootstrap是单次可信工厂持有初始化能力，不来自包。先空集群身份和受信001—013；data_owner初始化新的root/dataset/instance和loading、受信loader绑定，绝不复制source mode/instance为权限。
- 目标restore_loader仅有28固定业务列及archive_history/tombstones映射的SELECT/INSERT、material_sources.current_version精确回填。不能更新data_control、改scope/counters/角色/DDL、直接删body或启动源清理。target文件publication持target RootLease；loading固定绑定才允许K1 material引用guard专门加载路径，不授源根例外。
- 目标seal经受信控制函数将mode置restored_readonly、撤loader LOGIN成员/票据/初始化凭据。readonly LOGIN只得业务安全读、三个安全view和正常只读资格函数，不得恢复DML/结算/旧nonce。data_control此时是真正目标写保护权威，Hub sealed/selector必须与它绑定；两处不符失败关闭。
- 切换后的进度/原key/包/删除索引/最近账只由host私有ControlHub读，不依赖source或target data_operation_jobs。普通本机会话能读受限DTO，不能解密target credential、读journal路径或任意文件。

三个同T投影精确载体及字段为A4，metadata/source_control.json只含源观察，target不覆写；history/tombstones由loader受限装载并形成只读view。包schema_profile/codec为data_exit.v1.r01，manifest包含三元数据entry/hash和snapshot_control_domain_count=3；首轮格式是未采用草案，无产品包兼容追认。最新删除/账文件写独立overlays，保存T2/known_or_unknown来源，不假同T。只读核对要验证撤权后的角色实际读view/拒写，而非仅在seal前验证。

九个隔离INSERT扩展仍为memory_head_guard/memory_body_guard；interview_record_insert_guard/interview_command_guard/interview_head_guard；html_command_guard/html_artifact_insert_guard/html_preview_budget_guard/html_preview_session_guard。只在新target loading且绑定SESSION_USER/TG_OP=INSERT适用，保hash/类型/最终关系，在线正常规则不改。两教学FK仍只parent_record_id/result_record_id变可延迟默认IMMEDIATE。原teaching/memory/interview/HTML immutable UPDATE/DELETE函数及memory_final_shape摘要闭包不放宽。

K1另新增data_material_reference_guard，覆盖material_versions INSERT及material_sources指针激活两个触发入口；普通source须先PG shared并校root epoch/私有票据、禁止无pin元数据及已墓碑源复活。target loading只有工厂绑定路径豁免source ticket，但仍有target RootLease/已发布文件或明确deleted略过清单。epoch取消先独立COMMIT确认，不与unlink放同一可能rollback事务。data_runtime_write_guard覆盖28业务表的source frozen/target readonly，archive历史不能解除模式。新控制表不是自动的持久执行许可。

新增函数/触发、ACL/view和九guard函数身份需由可信十三版安装器更新memory/repository.py受影响指纹、preview/schema-fingerprint.json及data_exit schema/codec profile；保十二版身份/迁移链，不能信包expected hash。普通G3—G11不重开，但改到这些门的实际传播必须有最少真实验收和集中独审。

拟增生产文件为backend/app/data_exit/{contracts,codec,repository,snapshot,files,packages,restore,deletions,maintenance,reference,control,api}.py，deploy/data_restore.py和config/data-exit.example.json、frontend/src/data/{DataWorkspace.tsx,dataApi.ts}。全部项目内自包含，不依赖本设计脚本、DocuN/公共库/实验。

- reference.py定义prepare_reference(...) -> PreparedReference、acquire_shared(root,mutation_permit) -> ReferencePin、begin_ticket(pin,prepared) -> private token、reference_transaction(connection,pin,prepared)以及cancel_old_epoch/exclusive_cleanup(root,manifest)。RootLease Win句柄跨线程任务正确持有、PG事务锁与源票据匹配，不由HTTP序列化pin。
- OriginalStore.put/verify及精确unlink在启用清理的十三版入口必须从协调器走live pin；PostgresMaterials.save(...,reference_pin,prepared_ids)、create_pdf_candidate(...,reference_pin,prepared_ids)、confirm_pdf_candidate(...,reference_pin)为必填内部契约。materials.upload在put前取得，不能在run_in_threadpool返回后先放pin再开DB。PDF skip不移掉保留元数据，直接metadata入口/未来恢复publication同协议。十二版未启用清理可留原行为，不能在同根一边允许无围栏旧writer一边开启GC。
- control.py定义ControlHub/可信ProfileProvider、长度/序号/尾标journal、目标注册/selector/cache重放、DPAPI引用和只读get/reconcile。rawDSN/资源及path不进公开DTO/包。
- repository.py只管同T安全投影、源引用准入/墓碑、source观察/target归档和模式，不重复ControlHub长job CAS。snapshot/packages负责31安全域/原字节/发布；restore/maintenance使用B2明确签名、工厂/撤权/源fence/只读绑定；deletions仍沿原M3而新增准确source清理。
- main.py按Hub选择受信DataContext，同data_control匹配，readonly启动跳过旧worker/preview.recover并生成新会话；local认证不变。materials/PDF/活动/教学/面试/记忆/预览及内部producer的全部新写入口接MutationPermit，真实manager/launcher在spawn前登记自有工作，原停止/预算/Job算法不重写。
- start_local.py接可信Profile/控制根选择，只停止本次自有进程/PG，不自动迁移或回退源；README明确取包、持久job/query、源不可读、永久只读与后续持续使用未验。frontend四类意图/MemoryWorkspace按selection/dataset/instance命名隔离，刷新只GET Hub key，不提交旧draft/owner。

参数/状态转换/文件发布边界见B2/B6，API始终普通业务ID/显式动作，本轮一条源码/DDL/config均未写。

### B6 API、路径、限额和用户入口

新增API前缀/api/data，所有签名均为拟新增。

- GET /capabilities给format、scope、limits、backup_available、restore_executor_configured、current_mode，不启动动作。
- POST /jobs接kind=portable_export/restore_checkpoint、business_key、scope和明确确认；202返回job_id/revision/state。相同键同hash返回原收据，不同hash409。
- GET /jobs/{job_id}、GET /jobs/by-key/{business_key}、GET /packages固定从ControlHub给只读进度/原收据，不查当前选中PG来恢复job；GET /packages/{id}/content是认证的固定已发布文件流，不接路径。未发布409、丢文件/坏hash409。
- POST /uploads是流式接收，返回upload_id；客户端只给包字节，不给本地读路径。POST /restore-plans接upload_id/deletion_policy，返回计划和根hash；POST /restore-jobs接plan_id/expected_plan_sha256/business_key/确认，202开始隔离验证。POST /restore-jobs/{id}/activate-readonly再确认切换；无工厂503，不假称恢复开始。
- POST /jobs/{id}/cancel只停止本操作的本地拥有者，已published不能删包；其失败影响不扩到其他数据。POST /materials/{source_id}/deletion-preview、POST /materials/{source_id}/deletions是新资料影响/确认，后者必有原expected_revision、impact hash、业务键与confirm。

共用错误为invalid_input(400)、session_invalid(403)、not_found(404)、request_conflict/plan_changed/snapshot_changed/source_deleted/package_incomplete/restore_not_supported(409)、capacity_exceeded(413)、unsupported_format(415)、integrity_failed(422)、storage_unavailable/restore_executor_missing/maintenance_unconfirmed(503)、operation_timeout(504)。HTTP丢响应不推断失败；job.stage+是否有published/verified/active selector原件决定实际完成点。错误不返回SQL、堆栈、真实路径/连接串、环境或用户正文。

限额为可审查数据操作建议，不是当前运行许可或性能保证。首版一次并发1，包总字节/实际展开内容各2GiB、成员2万、manifest及中央目录各8MiB、JSON行1MiB、JSON深度32、单个row chunk32MiB、记录50万、事务组件5万行/64MiB。DB快照60秒、单恢复组件30秒、全操作1800秒、停线等待按既有监督原截止及配置明确上限，不延产品ready/D。上传300秒连续计限；未达到完整发布/验证时失败，不自动提升上限或重试。原件仍按已有版本5MiB上限；ZIP_STORED、非加密、非ZIP64，超过版本容量说明不支持。更大实际规模须在实施卡有据调整可信配置，不把限制宣称为已测吞吐。

接收先有界检查EOCD/中央目录长度和成员数，再构造ZipFile，避免未限目录元数据先耗内存。全路径仅固定POSIX ASCII白名单：拒绝绝对/盘符/UNC、..、反斜杠、NUL/控制字符、ADS冒号、非白名单文件、目录项/链接/硬链接标记、重复/大小写折叠冲突、未知压缩、嵌套包、外部引用；实际每次读取也计字节而不只信header。目标根从受信配置和UUID派生，lstat逐级拒重解析/链接，打开/复制和发布再次核根/目标身份；拒覆盖已有成员。不能直接extractall不可信包。[Python zipfile文档](https://docs.python.org/3.12/library/zipfile.html)用于标准库与不可信提取边界核查，具体白名单/限额为本合同新增策略。

切换后资料/学习/面试/记忆按钮须按永久只读caps禁写，文案“仅恢复记录与只读查看，未恢复继续学习或调用的执行资格；原数据保留，持续使用需后续验收”，不称全部恢复并继续Must通过。GET进度/包走持久Hub；无法核模式就拒业务写，不回退源。新导航“数据与备份”，包括“导出可读资料”“创建恢复备份”“核对/恢复备份”“删除影响”。入口GET-only。导出页显示选择范围、自动加入的证据依赖、原件/历史/已撤销处理、浏览器草稿不在服务器备份。确认文案“导出这些已保存内容”，不堆内部TASK/表名。备份文案“保存当前时点的原件、关系和状态；在途调用与未知预留会如实保留”。

进度依次为“读取已保存记录”“复制原件”“核对完整性”“已保存”，故障为“本次未完成，已有数据和旧备份保留”。可携不完整包明确“已保存可读的部分内容，缺少…，不可用于完整恢复”。小于128MiB可通过认证fetch下载；大包保存到已配置本机备份目录，页面只给业务名称/编号，提示用本机文件管理器取出，不把整包放浏览器Blob，也不开放任意服务器路径。

恢复上传后先显示“范围与完整性核对”“已删除内容影响”“建立隔离验证副本”。按钮“确认验证这个备份”与之后“切换为当前只读数据”分开。verified文案“副本已验证，当前应用仍使用原数据”；切换成功“当前读取恢复副本，未继承旧调用或预览的执行资格”。损坏/不支持显示具体可理解原因；不能把“备份已保存”称恢复验证通过，不能把验证通过称已经换库。历史预算显示“备份时点记录，执行已冻结”，未知显示“未确认，预留保留”。

frontend拟新增data/DataWorkspace.tsx与data/dataApi.ts，main.tsx增加导航；已有pending/teaching/interview/memory意图模块增加dataset/instance namespace和只读核对状态，MemoryWorkspace增加恢复删除覆盖说明。切换清理当前DOM owner/请求并生成新编辑身份，旧localStorage/IndexedDB草稿保留为原数据集提示，不自动提交、不静默覆盖。数据job意图只保存业务键/hash/状态，任何刷新/晚到响应都只GET原键；新schema投影检查和caps先于按钮可用。恶意页面POST仍由服务端/DB模式门拒绝。

## C 准备实施与最少决定

### C1 STEP017-P1修正后唯一采用包

状态仍recommended_pending。先交主控核证完整合同，再由主控提交用户一个包，本窗口不现在索批准、不代批准、不发TASK114。当前合成实施权/真实删除/切换没有由设计新增。

1. 原首轮只有备份共享/清理排他，改为全部put/幂等复用/新引用/最后unlink的跨线程进程RootLease，源PG shared/exclusive事务围栏与持久reference ticket/epoch取消；加入材料引用guard及必填pin调用点。新引用结果未知不删、已成功共享原件受保、可留原有孤儿。代价为触及导入/替换/PDF/元数据和恢复publication的定向修改/验证，但不新增分布式平台或自动GC。
2. 原snapshot仅写28表读取，改为同一T读28业务加3控制安全投影，三个明确metadata/checkpoint载体，源snapshot仅SELECT，target control身份可信新建、历史/tombstones受限加载并有readonly view。仍3提议表/4NOLOGIN角色、九加载分支和两FK，增加引用相关列/函数/guard、source frozen及profile指纹；无需第四业务控制库。代价是十三版真实身份/权限/元数据闭包验证，活票据/包mode不能迁执行权。
3. 原long job依赖源PG且selector/工厂不闭合，改为独立可信RETROLUME_CONTROL_ROOT的ControlHub journal唯一权威；PG只是T观察/引用事实。明确profile工厂allocate/prepare/verify/seal/activate/reconcile/get-by-key、DPAPI凭据生命周期、跨切换原key查询和所有新写/自有收尾fence。代价是新的私有控制根/控制文件协议和失败关闭；不可读时不能凭缓存/包/旧源推权，不赋任意DSN/命令/路径能力。
4. 保留可携独立解读、隔离新PG恢复、状态/预算保留、控制排除、资料墓碑/准确清理、默认删除覆盖，以及永久只读副本的推荐有限支持。原库普通本机重开不改；旧任务/持续付费/tool/preview/学习活动执行恢复不在本切片，STEP017-P1不替完整NFR005/持续使用/STEP018—020/M-1。真实用户库迁移、真实数据/删除/覆盖/切换仍另有明确授权及风险门，不能以本设计默许。

采用后下一实施卡只按合成source/target、可信profile/固定目录/role/次数/故障余量执行完整成果与集中独审；没有当前产品运行权。不提出多套技术/一串选择，备份频率/介质/有界参数沿推荐由编排冻结，不自动定时/外发。若主控/用户要求付费执行恢复扩围，必须另收敛最新账/拥有者/持续使用门，不能偷偷把只读副本当达成该Must。

### C2 文件与资源清单

拟增文件为B5完整名单的data_exit模块，新增reference.py和control.py、013_data_exit.sql、deploy/data_restore.py、config/data-exit.example.json、frontend/src/data两个模块、必要真实夹具和定向测试。拟改文件为main/local_settings相关、materials/PDF访问与删除、五领域仓储读写冻结、worker launcher/主应用管理登记、preview启动冻结、schema指纹、start_local、README和四类客户端意图/MemoryWorkspace。拟改范围只为数据出口/恢复/删除，不能顺手改provider、数学、解析器、模型预算或当前G11宿主。

数据包/恢复工厂配置放受忽略的config/data-exit.local.json，由样例描述安全配置键和有限profile；真实值只由本机接受机制注入。新增RETROLUME_DATA_SNAPSHOT_URL及受信恢复profile引用，数据/备份/恢复工作根须独立且验证raw路径后才resolve。恢复根RETROLUME_RESTORE_ROOT与私有控制根RETROLUME_CONTROL_ROOT均为受信已存在Windows本机绝对目录，与data_dir/backup_dir及相互之间不包含；候选按job_uuid派生。它不是包或浏览器提供的路径。README说明手工导出/备份、独立解读、隔离验证、只读切换、停线/失败/取包、旧删除影响和不自动迁移。

下一实施卡给精确新source/restore PG集群、卷、端口、目录、role及生命周期上限；可复用现有已接受本地OCI/运行时，不借111/112容器、角色、旧名字或余量。真实server_version_num本次未探测，未来在获准合成对象记录；target与source按固定profile和兼容主版本核，不从官方文档16推断当前现场为16。采用专用非超级用户snapshot LOGIN、临时bootstrap、loader和普通只读验证LOGIN，凭据在内存/stdin/限定Env，禁止打印或写包。

资源建议按成果冻结为一个source与一个target同时运行，上限由编排按真实机器/工作量核定。专用合成数据覆盖28表、5MiB以内原件、PDF核对/补充、教学和面试修正/历史、记忆撤销/清理、工具/model未知与两种R、预览已停/unknown；真实provider、付费、旧25取证、真实用户资料全0。失败保确切目标和数据，不删除/重新建同名目标绕过次数；普通修正连续完成，最多两次同因有据修正仍失败转诊断。

### C3 顺序和门

先完成codec/格式/权限迁移/隔离加载/状态冻结/精确文件路径合同的代码，再一次集中离线合法及恶意输入检查；同一实施卡连续跑获准真实PG非空013升级、全关系快照和文件原件、隔离全链恢复、只读HTTP及必要UI。先实现全部引用入口/持久取消epoch围栏，再启用精确清理；先核role/DDL及三控制投影身份，再加载历史；ControlHub与target角色撤销验证齐备才测只读切换/丢响应。先完成副本验证，再按明确同源合成目标做只读切换与失败轨迹。没有真实文件和PG证据，mock不算恢复通过。

G3—G11未变的预算/同COMMIT/原件/资格/Job/停止/数学/页面原件按对象与hash继承。增量覆盖013指纹/角色、source墓碑可用性、恢复INSERT和FK时序、snapshot真实并发、文件路径/发布、恢复冻结与UI意图，而非重复全部Native/六故障/32例。若新门改变真实跨模块行为，针对改变处扩矩阵并记录，不以继承省掉新增边界。

迁移/权限、导出数据范围和恢复执行权是高风险，在完整稳定实现与相关原件齐备后集中独立审计一次，隔离新会话。审计包含原需求、此合同/采用包、最终差异、实际源码/角色/DDL/as-run、原始快照/恢复/失败与清场，不给执行者完整聊天或用自评替代。当前设计只做一次文档一致性核对，不前置真实运行；必要风险门仍须在用户库/生产权限扩散前满足。最终STEP017仍由主控裁定。

## D 未来验收矩阵与四条手工轨迹

### D1 未来最小真实矩阵

所有以下条目是未来方法，不是本次PASS。每项的样本、精确资源/范围和次数由实施卡冻结；无关G3—G11继承仅在同版本/边界处适用。只读副本不会完成持续使用/执行恢复Must，矩阵通过只支持该切片。一次连续实施中合并相关修正，真实故障只停止受影响消费者，未知不能换根或篡改收据。

- V01，DR001/DR002，PG+文件+独立文本读取。全28表合成闭包，含当前/旧/待PDF、补充、作答修正、模型正文和引用；创建可携包，用与应用无关的JSON/文本工具核原件hash、版本关系和引用身份。原件/语义映射与packet不能仅靠目录有文件判断；缺项则不完整导出或失败，旧包不变。
- V02，DR002/NFR005，PG正文联接。teaching/model结果、interview local_body/model结果、memory版本/选择、HTML descriptor逐类对照源与导出，核原text hash和类型/来源；旧received无正文、not_sent、unknown不补正文/usage。原业务同COMMIT未改处继承，新增全量codec必须实核。
- V03，DR001/DR003，真实并发snapshot。在DB T前后两连接提交替换、scope变化、outcome及最近settle，用T的原始snapshot/rows证明包内各表同T，不以多个HTTPGET复核代替。断开快照连接后不能偷接另一个T继续，整次失败保旧成果。
- V04，DR003/K1，真实最后检查窗口与新引用并发。准确停在D的最终无引用检查后、unlink前，并发B上传同hash/替换/PDF候选/直接元数据/target发布。B先得shared时D等B COMMIT并保共用F；D先排他时B在put前等待、之后重发布再提交。再覆盖COMMIT丢回包、客户端进程死而PG迟到事务、ticket取消COMMIT未知：未决不删，旧epoch SQL拒新引用，第二次READ COMMITTED查全部历史/待PDF保留引用。记录真实RootLease/PG锁、ticket/epoch/事务/文件hash前后；孤立内存锁、两次hash或一空SELECT不能通过。失败保旧成功项/未知，不能换根。
- V05，DR001/DR003，PDF状态与原件。pending/confirmed/skipped及逐页supplement样本，恢复后资格相同或因删除覆盖不可用；不重新核对/解析就授pending学习资格。复用原解析/页规则，测试新增codec及墓碑屏障。
- V06，DR002，真实隔离恢复。source含非空活动/关系，target为新集群，先001—013后加载，逐表PK/count/原text hash/文件hash/关系闭包核，HTTP只读实际可回查。只构建或mock不通过；失败保source/旧backup。
- V07，DR002/SEC002，迁移/role反例。在另一个明确负例目标用非空004/005、已有010/011角色、错函数/约束/列/编码profile触发明确拒绝；不DROP/recreate或宽松认同名role。未来负例有独立target/次数，不能动原source。
- V08，DR002/SEC002，历史恢复guard。旧goal、obsolete/committed/history命令、superseded作答、历史body版本、终态HTML、非零预算及两教学FK循环载入；真实受信loader成功后普通role尝试该分支必须42501/拒绝。不可变历史UPDATE/DELETE继续失败；九分支/指纹改动需独审。
- V09，SEC002，loading与sealed越权。普通runtime、snapshot、包自称restore_mode/SET变量不得变成loader；只读目标直接business DML/旧HTML退款函数拒绝。source不存在loader授权，目标完成后临时成员撤掉，包内容不产生DDL/role权限。
- V10，NFR003/SEC002，四账保真。请求/成本/工具、execution_generation、M/R/S和last_settle逐字段对照，加上一条合法旧 received无正文。只读恢复不折叠/退款/认领，达限与unknown仍反映原值；原四账正常业务可继承，新增读取/冻结必须实核。
- V11，NFR003，preview保真。stopped/failed_unstarted/cleanup_unconfirmed及starts/S/R分别载入，控制变换清单可追。伪旧StopProof/CID/PID/owner密钥不确认新树或退款，R60保持；不用旧25真实运行作反例。
- V12，NFR002/NFR003，快照后额度增长。备份后source新增消耗/未知，再验证旧包；target显示快照时点并冻结，source最新账未被覆盖，两副本不能续发同一旧活动。未知源或跨位置仍无新额度授权，不宣多机保证。
- V13，NFR005，目标/父/资料/记忆资格。替换、revoked记忆、旧scope/目标版本、cancelled/dispatch_closed、旧答案依赖，在恢复只读DTO中不可误标当前可用。source/parent/memory旧资格算法继承，新增删除覆盖与archive投影核实际前后。
- V14，DR003，资料删除与共享原件。两条source共享hash，仅删除一条；墓碑commit后其当前/历史/PDF回查不可用，另一条原件完整。非共享准确键清理失败显示pending，明确同业务键重试不二次改revision；包/WAL/无关目录保留。
- V15，DR003/NFR005，记忆撤销/清理。revoke/purge pending/done及旧选择闭包样本；备份不带revoked在线body，原作答/上下文保留政策可解释，不把略过body冒原源purge done。既有M3物理门不重写，测新增打包/恢复mask。
- V16，DR003，旧备份与删除覆盖。备份后删source和memory，respect_current默认验证副本无有效正文/原件，manifest列覆盖与引用unavailable；snapshot_only_readonly明确确认才到只读副本，source墓碑不撤。未知最新删除历史显示无法核对，不假称并集完整。
- V17，DR001/DR002，截断/损坏/缺文件。截zip/manifest/row/原件、错SHA/CRC/长度、缺required/未知availability，输入原件+明确拒绝码；不发布完整备份、不覆盖旧包。合法deleted/legacy缺省与损坏严格区分。
- V18，SEC001/SEC002，恶意路径结构。绝对/UNC/盘符/../反斜杠/ADS/重名大小写/链接/reparse/嵌套包/压缩炸弹及EOCD巨大目录，真实文件系统核目标外0写入，逐字节计限。ZIP metadata/mock不能替代真实路径和打开/发布边界。
- V19，NFR002，容量与取消。字节/成员/JSON/行/组件/时间刚好上限和超一、用户cancel、中断上传；准确job state与未发布文件，source及之前可用包未变，取消不终止其他工作。
- V20，NFR002/DR003，文件发布/收据断点。spool/filecopy/fsync/no-replace/DB记录四处受控失败；丢published响应按原键只读核对，已有完整文件补收据而不复制。保存成功与接收可读分别记录。
- V21，NFR002，恢复中断/失败。target组件后崩溃/DB拒绝/文件损坏，目标failed不可读，source仍可用；原target不重用，真实有限修正新target额度由卡面负责，不因余秒复活旧运行。
- V22，DR002/SEC002/K3，只读切换及源仍活。verified前activate拒绝；owned stop/停写不完整时不换；选择器提交失败保旧选择和源完整数据，维护围栏不自动解除；只读核对后受信解围才能继续原源写。成功后新本机会话/实例、GET只读、全部旧动作拒绝，原数据目录和source保留。
- V23，SEC001，凭据不泄露。用合成marker经配置/限定Env注入，搜索实际包/响应/日志，apikey/DSN/session/DPAPI/控制秘密及私配不在其中；用户正文不为了扫描被无痕清洗。运行历史只有白名单普通事实/占位变换。
- V24，NFR002，幂等/刷新/晚到。HTTP真实丢响应、重复业务键、键hash冲突、页面刷新或目标切换后旧结果到达；只GET原job，不二次恢复/删除/切换，不污染当前instance。复用原意图原则，增量UI须实测。
- V25，DR002/NFR005，浏览器草稿。数据库导出中未提交IDB/localStorage内容缺省清楚；独立客户端草稿下载标未提交，编辑身份不迁入新数据集，不因恢复自动POST。只读取合成浏览器样本。
- V26，全部本合同，源/target角色、文件、HTTP、UI及精确收尾。manifest/root/codec/schema/as-run一体绑定，报告实际层、失败、余额与精确资源状态；集中独审验范围、权限和恢复执行门。无开放影响Must的失败或缺必要审计才能建议STEP017通过，主控裁定；不顺带签STEP018/019/020、M-1或项目。

- V27，K2/DR002/SEC001，真实同T31域及最小权限。T前后两连接变墓碑/操作观察，snapshot专用角色在同一REPEATABLE READ读28业务+三安全投影，文件载体/hash/缺活票据匹配；snapshot DML/写删除EXEC/控制秘密读取被拒。target新data_control由工厂生成、history/tombstones受限装载，seal后readonly安全view可读/loader权限已撤，包mode/instance不自授loading。
- V28，K3/NFR002，ControlHub跨切换及部分发布。source明确停止/不可连、dataset切新target后，GET原restore key/job/完成收据/包和旁证仍由同journal权威；只坏cache可read-only重放，断尾不算COMMIT、中段坏失败关闭。target注册半落、selector_commit已成功但响应丢失返回同generation，不二次分配/激活、不从旧PG或包重建权限。
- V29，K3/SEC002/NFR005，覆盖全写入口/fence失效/永久只读。源公开POST及内部producer、后续引用、admit/dispatch/preview和后台清理在fence后零新动作，已有登记收尾按原证明；unknown不解除围栏。核source frozen/target readonly/Hub选择一致，旧nonce、owner、draft、ledger或模式未知不能写，原源不毁。明确仍未覆盖恢复后付费/工具/预览/持续学习，不签全部恢复并继续Must。

### D2 四条手工轨迹

轨迹一，正常导出和恢复。源码事实是material_sources当前指向material_versions，teaching_records的模型类body在activity_operation_results，memory_choices和HTML context有原版本闭包。方案推演为同T读28业务和三安全投影→原hash复制文件→发布v1 checkpoint→新集群先001—013→教学循环FK事务与记忆闭包加载→原件/record/hash一致→verified→Hub持久job/target/seal→源写fence和自有收尾→selector_commit→只读绑定，GET原job仍走Hub。普通outside JSON工具可读文本包，原源不变；没有本次真实包或恢复PASS。

轨迹二，K1修正前后与丢提交。当前源码put/幂等命中与save分两阶段，只有source行锁。旧提议推演D查A外无引用→B复用F/提交vB→D unlink，B刚成功却缺原件，未实际发生。修正后B先shared则D等其COMMIT、最终见B保F；D先排他则B在put前等、删后重发布F再提交。B死/丢COMMIT回包时OS放锁不等于DB没提交，D须PG等待、旧ticket取消/epoch提交确认及第二次最新查询；取消结果未知不unlink。失败可留孤儿，不清旧成功件，全部为方案手工推演。

轨迹三，删除后恢复。当前事实只有记忆revoke→purge，资料删除为拟新增。推演为旧包T含source S的v1及memory M；之后本条资料墓碑和M撤销已提交→默认计划并入当前墓碑→目标不复制相应原件/在线body，原record/hash与引用边仍保存但unavailable；用户明确选备份时点只能在只读副本查看旧内容，源墓碑和旧备份本身不改变。未声称擦除WAL/副本。

轨迹四，在途UNKNOWN及R。源码已有activities running R、unknown操作预扣、preview cleanup_unconfirmed/R60及guard约束。推演源在T为requests_reserved=2、工具已用1、running R=30/S=10/G=7、preview R=60/start1；之后源可能继续消耗或失联。目标保这些快照数和未知/代次，owner/control时钟改归档占位，RO门拒重发/claim/settle/start，旧StopProof不能使R归零。查看不是证明源停止，跨位置不能自动得到最新账；本次不启动旧25或任何工作验证它。

## K对照、实际操作及交回

K1用统一OS根共享/排他、PG事务围栏、持久引用票据/取消epoch、两阶段最新查询及必填pin调用点关闭首轮设计缺口，覆盖幂等命中/全部新引用/迟到COMMIT/进程退出；不靠复查hash。K2增加三安全投影的同T只读权限、metadata/checkpoint载体、target可信新身份与history/tombstones载入/readonlyview，活票据不迁权。K3把长期job/selector/私有注册/旁证权威移到ControlHub，source PG仅观察及引用事实，补工厂/停线/切换/半发布/GET闭包及永久只读代价。均是当前合同设计闭合建议，不是实现/独审PASS或已采用。

原首轮44输入/4补充/7规则，正文未变处复用；新架构1.23/执行2.45头与主控gap补读，原件put及资料/PDF链重读。源码/迁移/配置/正式文档/旧证据写0，当前28表无变；新证据只入revision01。资料索引图/格式例在本轮新建，不覆盖首轮九原件。官方补读LockFileEx/PG explicit-locking两页为关键协议依据，累计6/6，未下载工具、import产品、构造真实包或运行任何产品命令。一次Select-Object只读数字参数误写英文，相关confirm正文用标准库文本切片补足，无产品动作。

本轮真实时长、累计观测/旧余额/unknown、文档一次一致性核对、源/规则未变与旧59137后缀证明见revision01/delivery.json。产品及未来V01—V29未运行；独审仍在完整稳定实现及必要高风险权限门，当前不宣STEP017产品/持续恢复/项目完成。原G11和旧UNKNOWN不作新前置，不重审或复跑。

建议主控先核证本完整修正合同及STEP017-P1差异，再提交用户一个真实必要采用包。尚未批准、未占TASK114，不代主控维护DocuS/CHG/共享状态或授权合成资源。实施另卡冻结精确对象/角色/路径/预算、未来运行/删除/切换边界；用户库/真实数据/私配/真实删除/覆盖/切换/新费用均不在本轮。普通不变内容不再问选择，无新测试经验入库。

本轮已完成的唯一文档核对实采截至2026-10-12T07:01:25.537109Z，新增已观测2876.891秒，旧3261.109合为6138.000/10800秒；旧观测余额7538.891保留，实采新窗余3123.109、总余4662.000，准备unknown不清。最终保存及剩余按delivery新实采更新，不把核对截点冒保存瞬间。命令范围为Get-Content/rg定向读、标准库时间/hash/有限文档解析、python rebuild-contract.py纯文档生成及读回，官方两页只读open；无产品import/执行。

[本轮K对应和权限/格式闭合](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-113/design/revision-01/k-closure.json)、[实际投入及后缀交付证明](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-113/design/revision-01/delivery.json)给完整机器核对记录。

以下为首轮59137字节完整原字节历史。当前实施只取以上完整A—D，不执行旧冲突设计或旧到期许可。

