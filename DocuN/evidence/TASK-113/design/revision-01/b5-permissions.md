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
