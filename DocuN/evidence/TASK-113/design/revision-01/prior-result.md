# TASK-113 / R-107 结果

STEP-017的A—D只读设计合同已完成。推荐用现有Python/PostgreSQL/不可变文件库实现同一数据包系列的可携导出与恢复快照，恢复先进入新的隔离PG实例和独立数据目录，验证后只读核对；旧工作、预算和删除事实不因此获得继续执行资格。本合同含必要的STEP017-P1采用增量，尚未实施、运行或验证产品，不代替主控采用、STEP完成或项目验收。

接收身份为A+设计角色，Codex desktop，系统身份GPT-6，精确子型号没有可核工具。继续已完成TASK111续作07的同一聊天，TASK-113/R-107是新合同，不继承111/112运行许可。规则为task_model、V4.0、公共AGENTS CHG-0003。入口为D:/shspic/project_NO3_RetroLume-agent/AGENTS.md；公共AGENTS和WORK适用2/6/8章按同窗未变正文复用，补读TASK_TEMPLATE，七锁定指纹实核匹配。当前需求v1.2、架构v1.22、执行动态v2.44、阶段07；G11按已采用Windows有限切片关闭，其失败、旧UNKNOWN、13元及626.566历史超限保留。

首个真实采钟为2026-10-12T02:25:28.088959Z、1043391734000000ns，设计截止1054191734000000ns。首个只读接收工具没有同步采钟，其采样前段标unknown，不倒推精确首读。产品操作预算全0。本轮只读规则、文档和源码，做标准库文件hash、SQL文本/AST结构索引、设计示例生成及最终一次文档核对；未import产品，未做compile/test/build/SQL/PG/Docker/Job/浏览器/模型/安装/费用/删除/Git写，未读取私有配置、环境值、真实数据目录或凭据。独立审计窗口未参与，也未派子Agent。

证据分级中，下面实际文件、表、约束和签名为B类源码事实；推荐算法、权限增量和四条手工轨迹为D类设计推演，没有本轮产品A类运行证据。工程自查不冒独立审计。输入导航44项逐字节匹配编排manifest；源码读取为相关正文、完整DDL结构及必要方法片段，不称已经全文重审全部业务。

- [接收及七规则核对](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-113/design/accepted.json)
- [44项输入身份](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-113/design/input-identity.json)
- [28表DDL及关系字段索引](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-113/design/schema-source-index.json)
- [实际方法及行号索引](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-113/design/method-source-index.json)
- [实际关系及拟增边界图](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-113/design/relationships.mmd)
- [格式说明例，非真实数据包](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-113/design/format-example.json)
- [有限官方核查，4/6页](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-113/design/research.json)
- [G11关闭事实及许可终点](D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-111-G11-final-acceptance.md)

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

### A3 同一逻辑时点

推荐新增SnapshotCoordinator及SourceFileLease，明确它们尚不存在。可携包和恢复快照均先取源文件清理共享租约，再由专用只读连接在一个REPEATABLE READ、READ ONLY事务里读取整个选定关系闭包和额度；首个非事务控制SELECT定义T。不能用现有多个READ COMMITTED工作区GET拼成全库快照。[PostgreSQL事务隔离说明](https://www.postgresql.org/docs/16/transaction-iso.html)支持同事务一致可见性；此引用不证明本轮实际运行。

DB阶段用流式游标、固定表/PK顺序写本地受控spool，最多60秒，不在事务内等待网络模型、渲染、用户确认、ZIP组装或大量文件拷贝。超时整次失败，保已有包。事务结束后只按T的不可变内容键复制原件并核hash，源清理共享租约持续至复制结束；新资料DELETE/精确原件清理必须先取同一租约的排他面，不能在T到复制期间unlink旧引用键。普通上传/替换继续追加不可变文件；DB已提交引用的原件按现有“先文件、后DB”顺序应已存在，外部篡改/缺失则失败或显式不完整导出。

模型、工具及preview在T之后的结果不混入T的包。包可含running、unknown和预留，准确说“截至此时点”，无需为了备份退款或假称远端停止。记忆body的并发DELETE由MVCC保T可见性；用户之后的删除不反写已经完成的备份。恢复时另核最新可取得墓碑，B4解释这一差别。新模块不假设已有全局停线锁。

只有“把验证副本切换为当前只读数据”的动作需要短暂停止新业务写和登记的本应用自有工作。拟新增MaintenanceCoordinator从受信父进程登记精确worker/preview实例，请原SUP按原ClosingCallGate、deadline、stop/settle路径收尾；没有直接关闭其他进程或daemon的权限。收尾不完整则不切换，隔离验证仍可交付。历史UNKNOWN可以存在，不要求复跑旧25补证明；但不能把一个当前仍可能写入的自有实例冒作已结束。取得停写确认后只在短事务/本机原子发布阶段做选择器切换，见B2。

## B 唯一最小实施合同

### B0 推荐及权限包关系

采用Python标准库JSON/ZIP_STORED/文件hash和现有psycopg，不加数据库、框架、压缩/加密依赖或向量产品。两种包共用严格manifest、关系codec和文件发布器，kind分别为portable_export、restore_checkpoint。导出能由文本编辑器/普通JSON工具解读；恢复checkpoint多一层受信类型映射，仍不含SQL/DDL/脚本或角色授权。恢复需要新隔离PG实例，因为010/011拒绝集群已有角色，不能用“同集群另建库”天然满足原迁移前提。

完整实现需要B5/C1的最小新持久控制、最小读取/恢复角色、九个仅隔离加载分支和两条教学FK的可延迟属性。它们构成一个STEP017-P1可审查采用包；本设计没有执行或代用户批准。普通接口/布局/参数是本合同推荐，不要求用户重新选择三套技术。

### B1 包、独立解读和完整性

格式为retrolume.data-package v1，后缀.rldata，容器ZIP_STORED，无加密、执行文件、任意路径或外部URL消费。默认本机私有备份目录手工创建，默认无定时任务；建议用户在重要批次/升级前手工备份，按需要自行复制到第二本地介质。频率与介质是可配置推荐，不启用后台全库外发。

布局为manifest.json、README.txt、records/固定表或领域名.jsonl、references/reference_edges.jsonl、originals/64位hash、summaries/活动UUID.txt。checkpoint另有checkpoint/固定table_id.jsonl及codec_description.json；README说明两种包、身份/引用、时间口径、缺失和查看方式。只有服务端固定路径白名单可生成/接收，original_filename只是标签，不参与落盘路径。原件不重编码，用户/模型文字按纯文本处理；HTML只在.json记录中保有限描述，不生成可自动执行的网页。

manifest包含package_id/kind/version、logical_time_utc、source_schema_profile、可信迁移链身份、应用/codec身份、范围闭包、表/记录/文件计数、各entry的byte_count/SHA、snapshot预算/未决摘要、删除/缺失/可选说明、browser_drafts_included=false以及root_sha256。根hash是删去root_sha256后规范UTF-8 manifest的SHA；不会把自引用hash当校验。逐文件hash与CRC只证明字节一致，不证明可信作者、工具权限或预算事实来自真实服务。已由本机服务创建的包可在外部私有控制区保存根hash收据用于核对；收据/密钥不打包，未知来源包只能作为待核对数据，不授执行权。

JSON要求UTF-8、无起始BOM、无重复键、非法数值/孤立surrogate拒绝，枚举和字段完全匹配codec。UUID/hash保持原标识；bigint、成本和时间账等用十进制字符串避免JS精度丢失，NULL保持null，array顺序保持；PG text内的payload/request_body/context_body/source_refs/body按原字符串保存并核原UTF-8 hash，不能格式化它们再签原hash。timestamps用带UTC偏移的ISO格式；jsonb的语义结构与text原字节身份区分。

availability为present、deleted、revoked、never_received、legacy_without_payload、missing_optional或missing_required，并给原因和原标识。缺失已删除原件、已撤销记忆body及旧received无正文是有依据的合法缺省，不补空答案。active且应存在的原件/body损坏是missing_required：完整backup失败，不能显示可恢复。用户明确选择“保存可读的不完整导出”才可发布portable_export，completion=incomplete、restore_eligible=false，并列具体缺项；它不替代完整备份。

select支持全本机已提交数据或选定来源/活动。活动导出自动纳入范围、父记录、所选记忆版本/闭包、引用版本和实际所需原件；未选但必要的依赖须在确认页列出数量，不偷偷扩成整库。恢复checkpoint首版只支持一个完整本机数据集，选定子集包不接受恢复，避免恢复半个FK/额度域。已撤销在线body默认不进任何包，历史原始作答和模型上下文若仍属于保留事实则按用户选择保存，不承诺记忆撤销清除它们。

### B2 备份、验证、恢复和切换

新增DataPackageService.create_job(command)返回持久job_id。状态为accepted→capturing→files→validating→published，失败为failed/cancelled；请求丢响应只GET原业务键，不自动重新写包。临时路径为受信backup_dir/.pending/job_uuid，完成文件为backup_dir/packages/package_uuid.rldata，均按ID派生。未完成文件没有published收据。先完成数据和hash、写句柄flush/fsync、同卷不覆盖发布，再短事务写published/root_sha256。文件发布成功而DB回执失败时，原业务键核对精确ID/hash可补“收据确认”，不能造第二包或说文件没保存；反向失败只能保持未发布。

恢复上传是独立Explicit动作，包被存为backup_dir/incoming/upload_uuid.rldata，连续计大小并校验整个结构。然后prepare_restore(package_id, deletion_policy)生成计划摘要，用户确认根hash、范围、删除影响和只读结果后才verify_restore(plan_id, business_key)。这不是运行包里的内容。目标必须是预配恢复工厂新建的隔离PG集群/卷、回环专用端口、独立目录及三套临时凭据，资源由下一实施卡冻结；同名已存在或有业务行/角色痕迹的目标拒绝，不DROP/recreate碰运气。

顺序固定为新目标身份/空集群检查→受信项目001—012→013安装控制/加载协议→schema、role、函数和约束身份核→设置loading和一次加载身份→原件目标copy/hash→严格codec加载→关系/正文/预算/删除可用性和只读HTTP核→撤销加载权限→target mode=restored_readonly→发布verified副本收据。001—012永远在加载数据之前执行；不在非空库补跑004/005，不用ALTER关闭FK、CHECK、NOT NULL、触发器，不设session_replication_role=replica，也不执行包内SQL。

源侧新增013可以在已核001—012非空合成库上追加，前置逐项核真，没有旧行额度回填或重置；初始墓碑可从现有revoked记忆头派生元数据，不能从current_version=NULL猜资料已删除。用户库实施仍是后续单独明确许可，当前不做。

教学commands.parent_record_id/result_record_id与records的循环FK需要在013只将这两条实际列集合匹配的FK设为DEFERRABLE INITIALLY IMMEDIATE，正常事务仍即时；加载对应活动组件时明确延后，全部记录在同事务结束前齐备。其他非可延迟约束按依赖拓扑加载，material_sources先current_version=NULL、versions齐备后仅回填当前指针。记忆使用已有可延迟FK/约束触发器，相关memory/绑定/choices/依赖闭包在一个有界事务完成，不能拆到不同COMMIT制造缺闭包。只可延迟已明确允许的约束，CHECK和NOT NULL不能因此延后。[SET CONSTRAINTS官方说明](https://www.postgresql.org/docs/16/sql-set-constraints.html)。

每个恢复连通组件上限5万行/64MiB，单事务最多30秒；大组件超限先拒绝，不临时关约束。各组件可COMMIT，但整个目标在verified前始终不可作为用户数据服务。剩余字段顺序由受信schema/真实FK拓扑确定，包不得自订table/column/type。九个受信加载分支只适用于新隔离目标、mode=loading、绑定的一次SESSION_USER成员角色、TG_OP=INSERT和已校验行；B5给出精确列表。它们跳过“在线生成当时才成立”的时序判据，仍保类型、正文hash及最终完整关系验证，不允许原历史UPDATE/DELETE。

未知format/schema/codec/renderer或迁移链不符、重复PK、hash/大小/正文绑定损坏、非法角色定义或不支持的数据域均failed，不做猜测修复。首版只支持本次受信profile及v1，不接受旧SPIKE SQL/任意pg_dump/未知旧版本；将来向前兼容须另加受信适配器。恢复失败只回滚当前组件、封存本次目标为failed；现库/旧包不变，目标不自动再用。数据库清理不在恢复重试中暗做，必须以后按精确清单另行执行。

verified表示隔离副本的数据和只读行为核对通过，不表示当前应用已换库。activate_readonly(job_id, expected_plan_sha256, confirmation_key)须用户另一次明确确认。MaintenanceCoordinator先关本次应用新业务写，收尾精确登记自有工作；失败不换。切换前用专用只读连接保存同谱系源的最新四账/preview账、操作终态/未知、最近settle及代次为latest_source_accounting.json，附读取时点/hash，与备份时点账分列，不用旧包覆盖或丢掉后续消耗事实；若源不可读就记latest_accounting=unknown，不能补0或称最新账齐备。记录超过受信容量也不截断后签完整。此旁证不作为新执行权，源数据库仍保留。

拟新增受信本机选择器在单个控制JSON中原子选择已verified的target业务ID，DSN仍只在私有目标注册器，current source完整保留。下一启动读取选择器及目标mode，生成新会话和编辑身份、跳过PreviewController.recover与worker恢复。发布失败继续原源；发布已完成而响应丢失则只读核对选择器。不能靠移库/改junction/覆盖旧目录或静默改私有配置切换。

首版生效范围是“当前应用读取验证副本，业务写冻结”，不承诺恢复副本可直接续发旧任务。后续若要恢复旧活动的付费/工具/预览执行，需要真实最新账、单机旧实例结束与范围资格另成受控续作门；不作为本合同隐藏待实现分支。旧源码的普通本机重开不变，数据备份恢复有这一明确更保守的边界，见C1采用包。

### B3 状态、额度和控制转换

checkpoint不是原数据库目录的物理镜像。活动/操作/领域业务键、admission_id、scope_revision/execution_generation、原额度上限、所有预扣/结算数、last_settled_generation/seconds、操作终态、record正文与hash、父/资料/记忆版本都保留。restore_manifest同时保存变换清单，区分快照原值、实际导入值、当前有效资格，不能标所有列原字节相同。

不打包live executor/Windows owner_session、owner/control key或hash、nonce/boot_id、PID/Job/CID、DPAPI、临时token、单调时钟控制文件。必需列由受信codec在隔离目标生成不可用的归档占位身份：activities.running_owner_session_id=NULL；running的executor_id为固定archived身份，原lease/deadline只作历史时刻；operation.executor_id同为归档身份。html_preview_sessions仍保preview_id/generation/start_key、state/reserve/elapsed/deadline_at，owner/boot/nonce与两key hash由本次加载产生新随机不可公开的占位，cid=NULL、t0_ns=1、deadline_ns=1+reserve_seconds×10^9仅满足存储形状，标clock_origin=archive_placeholder，绝不视为真实计时或新截止。占位原始密钥立即丢弃，不交给UI/控制者。原StopProof最多导普通脱敏历史事实和原receipt hash；不保可用于当前确认的完整控制receipt，first_stop/confirmation存archived_non_authorizing摘要或null，额度和原已结算状态不改。

DB层新增模式写门，restored_readonly禁止28业务表的INSERT/UPDATE/DELETE，旧HTML函数也不能绕过；应用入口同样关模型/tool/start/recover/settle，只有数据核对/导出可用。既有raw StopProof或PID即使伪造到包中也只能被拒绝/当普通未信任字段，不能确认新树结束、退款、折叠R、推进代次或重发。未知保unknown，running保R>0，preview cleanup_unconfirmed保reserve且elapsed null。来源已失效、记忆revoked、旧目标/答案版本、cancelled/dispatch_closed都不自动变当前。

旧备份可能早于后续额度消耗。恢复副本展示“备份时点的账”，并分列可取得的最新源账及未知差异，不称旧数为最新余额；其业务完全冻结，源库和外部最近账/删除控制索引保留，因此不使用旧快照制造可消费余额。最新旁证本身也不能结算或退款。源仍存活、跨位置/换Windows用户或最新账不可取得时也只支持验证/只读副本，不能保证任意多机共享额度、抢旧工作或通过多个副本获得新旧同一活动额度。旧25只按既有UNKNOWN事实入包，不申请新停止证明。

### B4 删除、引用和旧备份

资料删除为拟新增SourceDeletionService.preview/confirm，不把当前不存在的DELETE接口冒事实。preview(source_id, expected_revision)返回本条所有版本、引用活动、PDF候选、记忆依赖、HTML/预览影响、待处理hash及共享原件计数，签有界impact token。confirm同一业务键/修订/impact hash，用户明确“删除本条资料及全部版本的回查内容，历史关系和旧备份保留”。普通刷新不触发。

提交先取源文件清理排他租约，再按原源→记忆→活动锁序完成短事务：精确核source、插入data_tombstones、current_version=NULL、revision+1，登记不可变删除收据/待清理manifest。待PDF不能再确认或取原件，当前资料/引用读返回deleted，不把NULL待核对来源混成deleted。活动scope保原事实但资格失败；有关已生成学习/面试/HTML历史留元数据及原hash，当前消费和正文投影按依赖失效门抑制。PreviewController只停止该资料影响的准确当前自有session，控制/物理stop与数据库墓碑不混成一个事务；无法确认仍保原preview R及未知，不能为了删除退款。

之后按准确hash/size清单逐个核根、普通文件、hash、共用引用并unlink；不是递归GC。只删除本条全部版本的原件，另一个未删除来源的任一保留版本/候选共用该hash就保留文件，但本条回查仍不可用。失败时墓碑已生效、文件清理pending，原单清单和业务键明确重试；删除收据记录确切成功/失败，不称已经物理擦除。不可变版本/教学/面试/操作历史不删，文件名等必要元数据可能仍在受保护备份/历史，UI说明这一范围。

记忆沿已有MemoryService/apply_memory_command及purge_learning_memory，不新增通用DELETE或把purger权限授普通app。只将已提交revoke元数据同步到data_tombstones/外部本机删除索引，M3继续按原清单、版本hash和业务键精确处理body。DTO恢复只读投影先检查删除覆盖；memory_dependency_invalid、旧选择/父记录和HTML关联不自动换新版。既有revoked/pending不升级done，旧正文hash/元数据仍在。

已完成备份包含T当时内容；源之后删除不会使这个文件消失。默认恢复计划respect_current_deletions：同一来源谱系可读的当前墓碑/本机索引与包内墓碑取并集，标明其独立时点和digest。目标不复制命中的原件/在线记忆body，资料current指针保持不可用，记忆在有效view里deleted/revoked不可读；快照原始头状态及事件保留并显示覆盖理由，不无痕重写不可变历史和hash。引用marked unavailable，不把略过的文件当传输损坏。覆盖计划及结果成为新的restore_manifest。

用户若选snapshot_only_readonly，确认页逐项说明将从旧备份重新取回哪些已删除内容，仅到隔离只读副本，不撤销当前源墓碑/清理收据、不自动变当前；切换还需B2另一次动作。跨位置没有当前删除索引时，默认为“删除历史无法核对，只读验证”，用户明确按备份时点核对才能查看相应内容，不宣删除并集已知。旧备份、WAL、供应商、实验和用户其他副本不自动删除，也不承诺彻底擦除。

### B5 拟新增持久模型、权限和具体修改

唯一迁移建议为backend/migrations/013_data_exit.sql，001—012原文件保持。新增三表，不新增通用文档/向量/任务业务域。

- data_control为单行部署控制，含dataset_id、instance_id、schema_profile、mode(normal/loading/restored_readonly)、source_snapshot_id、source_root_sha256、restore_manifest_sha256、created_at。实例身份从受信初始化生成，不由包授予；源谱系是普通元数据，mode只能由受信控制函数改变。
- data_operation_jobs含business_key主键、job_id唯一、kind、request_sha256、scope_json、state、stage、package_id、root_sha256、byte_count/file_count/row_count、plan_sha256、target_id、error_code、created_at/updated_at/terminal_at、revision。schema规定终态不可退回，业务键不同hash冲突409，阶段CAS仅单个拥有者推进。路径/凭据不入请求或返回。此表的运行票据不恢复为活任务，包只带普通操作历史摘要。
- data_tombstones含tombstone_id、entity_kind(source/memory)、entity_id、effective_revision、business_key唯一、snapshot/plan digest、deleted_at、cleanup_state(pending/done)、manifest_json/hash。记录追加、状态完成不可回退，source不靠删除旧版本行实现；memory使用既有revocation key去重。外部只读删除索引可从本表/现有revoked头重建，读不到最新源时必须标unknown。

新增retrolume_data_owner、retrolume_data_app、retrolume_data_snapshot、retrolume_restore_loader，全部NOLOGIN/NOSUPERUSER/NOCREATEDB/NOCREATEROLE/NOREPLICATION/NOBYPASSRLS。由明确受信bootstrap给专用LOGIN精确成员资格，应用和包不能自授；普通runtime不给owner/loader或旧memory_purger成员资格。

data_owner只拥有新三表及固定控制函数，函数固定search_path、从PUBLIC撤EXECUTE；data_app只SELECT安全状态和EXECUTE create_job/CAS/本条source_delete函数。snapshot只对28表的codec白名单列SELECT，排除运行秘密列，不给DML/服务器文件读取/旧角色owner。source_delete函数获得精确UPDATE(material_sources.current_version,revision)及必要读取，新文件清理由本机路径守卫执行，不给数据库任意文件权限。snapshot DSN用新的受信配置键RETROLUME_DATA_SNAPSHOT_URL安全注入，不输出、不进浏览器/包。

restore_loader只授新隔离目标的白名单表SELECT/INSERT和material_sources.current_version回填，不能UPDATE旧历史/DELETE/TRUNCATE、建角色/库、改schema或读服务器文件。source端不能授此加载资格。模式写门data_runtime_write_guard在28业务表守normal/loading/restored_readonly，loading仅匹配一次bootstrap身份的INSERT及精确来源指针回填；普通角色在只读目标不能因SECURITY DEFINER函数改业务。loading票据/SESSION_USER绑定不来自包字段或任意SET自称。结束后撤loader LOGIN成员和加载票据，目标封为只读；失败也封存，不再生效加载身份。

仅以下九个既有guard增加受信隔离INSERT分支，正常在线分支保持原规则，原不可变UPDATE/DELETE函数不改。

- memory_head_guard、memory_body_guard。允许既有历史头和旧body版本载入；body仍核原UTF-8 hash/bytes/类型，已撤销body按合同略过，状态和值不伪造。
- interview_record_insert_guard、interview_command_guard、interview_head_guard。允许历史最终状态的INSERT，仍核原PK/FK/hash/answer/parent与最终图，不伪装为新的在线命令效果。
- html_command_guard、html_artifact_insert_guard、html_preview_budget_guard、html_preview_session_guard。允许历史产物/非零账/终态或未知的受控加载，archive控制变换明确，不能走实时退款分支。

memory_final_shape_guard及现有可延迟依赖摘要规则保留；teaching_records_immutable、memory_immutable_guard、interview_record_immutable_guard、html_immutable_guard仍拒历史覆盖/删除。两条教学FK按B2改变deferrability，正常默认IMMEDIATE。精确匹配实际列集合/目标，不猜约束自动名称。十三版安装后更新memory/repository.py中受影响函数指纹和preview/schema-fingerprint.json/catalog基线，保原十二版身份及迁移链记录；不从包的expected hash信任目录。不能悄悄让旧fingerprint把新guard当同版。

拟新增backend/app/data_exit/{contracts,codec,repository,snapshot,files,packages,restore,deletions,maintenance,api}.py，各职责及方法如下，均非现存实现。

- contracts定义DataJobCommand(kind,business_key,scope,expected_plan_sha256,confirmation)、DataJobReceipt及Code错误；未知字段拒绝。
- codec定义28表固定字段/类型、text原hash、控制排除/归档转换、reference edges和依赖图；decode_row(table_id,line)不得使用包的任意表/列。
- repository提供create_or_read_job、advance_stage(expected_revision)、read_job、read_control、append_tombstone、delete_source_metadata；read_snapshot_records(scope)专用只读事务，不复用分页工作区或返回旧控制能力。
- snapshot的capture(scope,limits)管理唯一T、spool和SourceFileLease(shared)，只得到SnapshotRecordSet；不调用recover_unknown、settle或模型。
- files的copy_originals/validate_package_paths/publish_no_replace/unlink_exact_manifest拒重解析点和逃逸，流式计限/hash，单个临时文件的创建/清理由操作清单负责，旧包/实验不自动GC。
- packages的build_export/build_checkpoint/publish/reconcile_published只处理固定布局，manifest完整后才发布。
- restore的prepare/verify/seal_readonly/activate_readonly使用固定目标工厂、受信schema和一次loader；rollback只作用未提交目标组件，不执行包内SQL。
- deletions的preview_source_delete/confirm_source_delete/reconcile_memory_tombstone处理影响和精确清理；不取代M3。
- maintenance的register_owned_work/drain_for_readonly_switch登记本进程启动的真实实例，按既有监督权发停线意图；SourceFileLease只防本应用文件清理，与全局业务停线不同。
- api复用本机认证及受限DTO，不把文件系统路径/DSN/DDL/凭据作为客户端参数。

拟修改main.py注册data路由、只读实例启动分支和capability；materials/api.py、repository.py及pdf_review/api.py为源墓碑/候选/原件访问增加屏障；activities、teaching、interview、memory、preview仓储的公共读取在恢复实例标archive/read-only及删除覆盖，写入口失败关闭。worker/launcher.py和PreviewController.open/主应用manager仅接只读/停线登记，原Job/EOF/deadline/预算确认算法不重写。新增受信deploy/data_restore.py和config/data-exit.example.json，start_local.py接选定只读目标但不自动迁移/覆盖私配。生产代码不依赖DocuN、公共提示词或SPIKE。

### B6 API、路径、限额和用户入口

新增API前缀/api/data，所有签名均为拟新增。

- GET /capabilities给format、scope、limits、backup_available、restore_executor_configured、current_mode，不启动动作。
- POST /jobs接kind=portable_export/restore_checkpoint、business_key、scope和明确确认；202返回job_id/revision/state。相同键同hash返回原收据，不同hash409。
- GET /jobs/{job_id}、GET /jobs/by-key/{business_key}、GET /packages给只读进度/原收据；GET /packages/{id}/content是认证的固定已发布文件流，不接路径。未发布409、丢文件/坏hash409。
- POST /uploads是流式接收，返回upload_id；客户端只给包字节，不给本地读路径。POST /restore-plans接upload_id/deletion_policy，返回计划和根hash；POST /restore-jobs接plan_id/expected_plan_sha256/business_key/确认，202开始隔离验证。POST /restore-jobs/{id}/activate-readonly再确认切换；无工厂503，不假称恢复开始。
- POST /jobs/{id}/cancel只停止本操作的本地拥有者，已published不能删包；其失败影响不扩到其他数据。POST /materials/{source_id}/deletion-preview、POST /materials/{source_id}/deletions是新资料影响/确认，后者必有原expected_revision、impact hash、业务键与confirm。

共用错误为invalid_input(400)、session_invalid(403)、not_found(404)、request_conflict/plan_changed/snapshot_changed/source_deleted/package_incomplete/restore_not_supported(409)、capacity_exceeded(413)、unsupported_format(415)、integrity_failed(422)、storage_unavailable/restore_executor_missing/maintenance_unconfirmed(503)、operation_timeout(504)。HTTP丢响应不推断失败；job.stage+是否有published/verified/active selector原件决定实际完成点。错误不返回SQL、堆栈、真实路径/连接串、环境或用户正文。

限额为可审查数据操作建议，不是当前运行许可或性能保证。首版一次并发1，包总字节/实际展开内容各2GiB、成员2万、manifest及中央目录各8MiB、JSON行1MiB、JSON深度32、单个row chunk32MiB、记录50万、事务组件5万行/64MiB。DB快照60秒、单恢复组件30秒、全操作1800秒、停线等待按既有监督原截止及配置明确上限，不延产品ready/D。上传300秒连续计限；未达到完整发布/验证时失败，不自动提升上限或重试。原件仍按已有版本5MiB上限；ZIP_STORED、非加密、非ZIP64，超过版本容量说明不支持。更大实际规模须在实施卡有据调整可信配置，不把限制宣称为已测吞吐。

接收先有界检查EOCD/中央目录长度和成员数，再构造ZipFile，避免未限目录元数据先耗内存。全路径仅固定POSIX ASCII白名单：拒绝绝对/盘符/UNC、..、反斜杠、NUL/控制字符、ADS冒号、非白名单文件、目录项/链接/硬链接标记、重复/大小写折叠冲突、未知压缩、嵌套包、外部引用；实际每次读取也计字节而不只信header。目标根从受信配置和UUID派生，lstat逐级拒重解析/链接，打开/复制和发布再次核根/目标身份；拒覆盖已有成员。不能直接extractall不可信包。[Python zipfile文档](https://docs.python.org/3.12/library/zipfile.html)用于标准库与不可信提取边界核查，具体白名单/限额为本合同新增策略。

新导航“数据与备份”，包括“导出可读资料”“创建恢复备份”“核对/恢复备份”“删除影响”。入口GET-only。导出页显示选择范围、自动加入的证据依赖、原件/历史/已撤销处理、浏览器草稿不在服务器备份。确认文案“导出这些已保存内容”，不堆内部TASK/表名。备份文案“保存当前时点的原件、关系和状态；在途调用与未知预留会如实保留”。

进度依次为“读取已保存记录”“复制原件”“核对完整性”“已保存”，故障为“本次未完成，已有数据和旧备份保留”。可携不完整包明确“已保存可读的部分内容，缺少…，不可用于完整恢复”。小于128MiB可通过认证fetch下载；大包保存到已配置本机备份目录，页面只给业务名称/编号，提示用本机文件管理器取出，不把整包放浏览器Blob，也不开放任意服务器路径。

恢复上传后先显示“范围与完整性核对”“已删除内容影响”“建立隔离验证副本”。按钮“确认验证这个备份”与之后“切换为当前只读数据”分开。verified文案“副本已验证，当前应用仍使用原数据”；切换成功“当前读取恢复副本，未继承旧调用或预览的执行资格”。损坏/不支持显示具体可理解原因；不能把“备份已保存”称恢复验证通过，不能把验证通过称已经换库。历史预算显示“备份时点记录，执行已冻结”，未知显示“未确认，预留保留”。

frontend拟新增data/DataWorkspace.tsx与data/dataApi.ts，main.tsx增加导航；已有pending/teaching/interview/memory意图模块增加dataset/instance namespace和只读核对状态，MemoryWorkspace增加恢复删除覆盖说明。切换清理当前DOM owner/请求并生成新编辑身份，旧localStorage/IndexedDB草稿保留为原数据集提示，不自动提交、不静默覆盖。数据job意图只保存业务键/hash/状态，任何刷新/晚到响应都只GET原键；新schema投影检查和caps先于按钮可用。恶意页面POST仍由服务端/DB模式门拒绝。

## C 准备实施与最少决定

### C1 STEP017-P1唯一采用包

当前确有需要采用的增量，不能写“完全无需采用”。推荐一次采用以下完整包，实施者和编排者可按本条审查，不需要用户提供数据、DSN或密钥来决定设计。

1. 采用可携/恢复v1格式、MVCC时点与源清理租约、新三表和最小四角色。代价为一次013向前安装及专用读取凭据配置；源旧28业务表/记录/额度不回填，不自动迁移用户库。
2. 采用两条教学FK可延迟属性和九个只允许新隔离loading的guard INSERT分支，以及28表只读模式写门。代价为更新真实schema/函数指纹和受影响领域边界验证；普通在线规则、不可变UPDATE/DELETE和预算确认不放宽。没有这个包，历史最终状态不能假称能按现有producer直接加载。
3. 采用新隔离PG集群恢复、控制字段排除及公开变换、恢复副本默认且首版生效只读。原件/正文/引用/额度/未知保留，旧执行身份不复活。代价是无法直接用旧备份继续付费或预览；后续执行启用需要另外核最新账和拥有者，当前不扩建分布式平台。
4. 采用资料删除的墓碑先行/精确原件清理和默认恢复删除覆盖。用户每次动作仍需范围确认；旧备份、WAL和其他副本不自动擦除。代价为明确新文件删除实施授权及失败pending机制，不能把设计卡当数据操作许可。

仅这一主要包需主控按有效用户指令处理采用；本窗口不提出新权限问题来阻塞文档完成，也不替用户批准。频率/介质推荐、UI措辞、初始操作上限在下张实施卡冻结即可，不人为再拆审批。新依赖/安装、用户库实际迁移、真实数据删除/覆盖/切换不在本次授权；未来先合成副本。

### C2 文件与资源清单

拟增文件为B5列出的data_exit十模块、013_data_exit.sql、deploy/data_restore.py、config/data-exit.example.json、frontend/src/data两个模块、必要真实夹具和定向测试。拟改文件为main/local_settings相关、materials/PDF访问与删除、五领域仓储读写冻结、worker launcher/主应用管理登记、preview启动冻结、schema指纹、start_local、README和四类客户端意图/MemoryWorkspace。拟改范围只为数据出口/恢复/删除，不能顺手改provider、数学、解析器、模型预算或当前G11宿主。

数据包/恢复工厂配置放受忽略的config/data-exit.local.json，由样例描述安全配置键和有限profile；真实值只由本机接受机制注入。新增RETROLUME_DATA_SNAPSHOT_URL及受信恢复profile引用，数据/备份/恢复工作根须独立且验证raw路径后才resolve。第三个恢复根建议RETROLUME_RESTORE_ROOT，已存在本机绝对目录，与data_dir/backup_dir互不包含；候选按job_uuid派生。它不是包或浏览器提供的路径。README说明手工导出/备份、独立解读、隔离验证、只读切换、停线/失败/取包、旧删除影响和不自动迁移。

下一实施卡给精确新source/restore PG集群、卷、端口、目录、role及生命周期上限；可复用现有已接受本地OCI/运行时，不借111/112容器、角色、旧名字或余量。真实server_version_num本次未探测，未来在获准合成对象记录；target与source按固定profile和兼容主版本核，不从官方文档16推断当前现场为16。采用专用非超级用户snapshot LOGIN、临时bootstrap、loader和普通只读验证LOGIN，凭据在内存/stdin/限定Env，禁止打印或写包。

资源建议按成果冻结为一个source与一个target同时运行，上限由编排按真实机器/工作量核定。专用合成数据覆盖28表、5MiB以内原件、PDF核对/补充、教学和面试修正/历史、记忆撤销/清理、工具/model未知与两种R、预览已停/unknown；真实provider、付费、旧25取证、真实用户资料全0。失败保确切目标和数据，不删除/重新建同名目标绕过次数；普通修正连续完成，最多两次同因有据修正仍失败转诊断。

### C3 顺序和门

先完成codec/格式/权限迁移/隔离加载/状态冻结/精确文件路径合同的代码，再一次集中离线合法及恶意输入检查；同一实施卡连续跑获准真实PG非空013升级、全关系快照和文件原件、隔离全链恢复、只读HTTP及必要UI。先核role/DDL身份，再加载历史；先完成副本验证，再按明确同源合成目标做只读切换与失败轨迹。没有真实文件和PG证据，mock不算恢复通过。

G3—G11未变的预算/同COMMIT/原件/资格/Job/停止/数学/页面原件按对象与hash继承。增量覆盖013指纹/角色、source墓碑可用性、恢复INSERT和FK时序、snapshot真实并发、文件路径/发布、恢复冻结与UI意图，而非重复全部Native/六故障/32例。若新门改变真实跨模块行为，针对改变处扩矩阵并记录，不以继承省掉新增边界。

迁移/权限、导出数据范围和恢复执行权是高风险，在完整稳定实现与相关原件齐备后集中独立审计一次，隔离新会话。审计包含原需求、此合同/采用包、最终差异、实际源码/角色/DDL/as-run、原始快照/恢复/失败与清场，不给执行者完整聊天或用自评替代。当前设计只做一次文档一致性核对，不前置真实运行；必要风险门仍须在用户库/生产权限扩散前满足。最终STEP017仍由主控裁定。

## D 未来验收矩阵与四条手工轨迹

### D1 未来最小真实矩阵

所有以下条目是未来方法，不是本次PASS。每项的样本、精确资源/范围和次数由实施卡冻结；无关G3—G11继承仅在同版本/边界处适用。一次连续实施中合并相关修正，真实故障只停止受影响消费者，未知不能换根或篡改收据。

- V01，DR001/DR002，PG+文件+独立文本读取。全28表合成闭包，含当前/旧/待PDF、补充、作答修正、模型正文和引用；创建可携包，用与应用无关的JSON/文本工具核原件hash、版本关系和引用身份。原件/语义映射与packet不能仅靠目录有文件判断；缺项则不完整导出或失败，旧包不变。
- V02，DR002/NFR005，PG正文联接。teaching/model结果、interview local_body/model结果、memory版本/选择、HTML descriptor逐类对照源与导出，核原text hash和类型/来源；旧received无正文、not_sent、unknown不补正文/usage。原业务同COMMIT未改处继承，新增全量codec必须实核。
- V03，DR001/DR003，真实并发snapshot。在DB T前后两连接提交替换、scope变化、outcome及最近settle，用T的原始snapshot/rows证明包内各表同T，不以多个HTTPGET复核代替。断开快照连接后不能偷接另一个T继续，整次失败保旧成果。
- V04，DR003，文件清理并发。备份先得共享租约，资料删除排他等待；按T引用的旧不可变键完成copy/hash后再允清理。反顺序删除已提交时包要明确deleted。冻结/租约丢失不执行unlink，不能用实际读到一半的字节宣完整。
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
- V22，DR002/SEC002，只读切换及源仍活。verified前activate拒绝；owned stop/停写不完整时不换；选择器发布失败原源继续。成功后新本机会话/实例、GET只读、全部旧动作拒绝，原数据目录和source保留。
- V23，SEC001，凭据不泄露。用合成marker经配置/限定Env注入，搜索实际包/响应/日志，apikey/DSN/session/DPAPI/控制秘密及私配不在其中；用户正文不为了扫描被无痕清洗。运行历史只有白名单普通事实/占位变换。
- V24，NFR002，幂等/刷新/晚到。HTTP真实丢响应、重复业务键、键hash冲突、页面刷新或目标切换后旧结果到达；只GET原job，不二次恢复/删除/切换，不污染当前instance。复用原意图原则，增量UI须实测。
- V25，DR002/NFR005，浏览器草稿。数据库导出中未提交IDB/localStorage内容缺省清楚；独立客户端草稿下载标未提交，编辑身份不迁入新数据集，不因恢复自动POST。只读取合成浏览器样本。
- V26，全部本合同，源/target角色、文件、HTTP、UI及精确收尾。manifest/root/codec/schema/as-run一体绑定，报告实际层、失败、余额与精确资源状态；集中独审验范围、权限和恢复执行门。无开放影响Must的失败或缺必要审计才能建议STEP017通过，主控裁定；不顺带签STEP018/019/020、M-1或项目。

### D2 四条手工轨迹

轨迹一，正常导出和恢复。源码事实是material_sources当前指向material_versions，teaching_records的模型类body在activity_operation_results，memory_choices和HTML context有原版本闭包。方案推演为T读上述关系→原hash复制文件→发布v1 checkpoint→新集群先001—013→教学循环FK事务与记忆闭包加载→原件/record/hash一致→verified→用户明确切换只读。普通outside JSON工具可读文本包，原源不变；没有本次真实包或恢复PASS。

轨迹二，快照/文件失败。源码事实是OriginalStore先文件后DB、不覆盖原件，DB失败可留孤儿。推演为T已读取版本v1，copy发生hash不符或source文件清理排他租约错误→本job failed，旧published包继续可用，不更新其manifest、不用v2补成混合T；若文件已经完整发布而DB收据断开，则原业务键读取精确root核对后只补确认。未运行这个故障。

轨迹三，删除后恢复。当前事实只有记忆revoke→purge，资料删除为拟新增。推演为旧包T含source S的v1及memory M；之后本条资料墓碑和M撤销已提交→默认计划并入当前墓碑→目标不复制相应原件/在线body，原record/hash与引用边仍保存但unavailable；用户明确选备份时点只能在只读副本查看旧内容，源墓碑和旧备份本身不改变。未声称擦除WAL/副本。

轨迹四，在途UNKNOWN及R。源码已有activities running R、unknown操作预扣、preview cleanup_unconfirmed/R60及guard约束。推演源在T为requests_reserved=2、工具已用1、running R=30/S=10/G=7、preview R=60/start1；之后源可能继续消耗或失联。目标保这些快照数和未知/代次，owner/control时钟改归档占位，RO门拒重发/claim/settle/start，旧StopProof不能使R归零。查看不是证明源停止，跨位置不能自动得到最新账；本次不启动旧25或任何工作验证它。

## 实际操作、核对和交回

本次产品/源码/配置/迁移/DocuS/旧证据写入0，只写TASK113结果和指定新设计证据。官方一手研究4页，未安装或下载工具；PG现场主版本仍按未探测登记，现有固定镜像/psycopg3.3.5及保存的Python312身份只用于设计适用边界。读取命令中几次Select-Object的数字参数误写为英文单词，只读失败，无产品效果；后改为标准库文本切片/结构读取补足，未做机械产品复测。

达到合同完整后进行一次文档一致性核对及保存回读。具体结果、真实时长、hash、路径/输入未变及A—D/矩阵/权限包覆盖见同目录delivery.json。没有独立审计、迁移执行或备份恢复运行，故实现状态和功能验证仍未开始/未验证；这不是未保存或把设计失败称通过。

建议主控审阅一次STEP017-P1，再按已采用范围冻结合成资源/次数/故障余量并发完整实施卡。更新架构MOD008/FLOW007/API005的实际合同、数据图/恢复冻结/删除范围，执行动态仅登记设计交回/采用及后续任务，文档变更记录集中登记；最终需求不降DR/SEC/NFR，不改用户原始需求。新共享TASK/DEF/CHG或验收状态仍由主控维护，本窗口不占号、不启动下一周期。

本轮没有可称已解决且经产品运行验证的错误经验候选，不写外部经验库。用户此刻无需提供密钥、DSN、数据或执行恢复操作；唯一必要关键决定是上面的具体采用包，后续真实迁移/删除/切换按对应有效授权与必需独审处理。
