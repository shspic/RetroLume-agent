# K2/K3 控制权威与同T元数据

本文件是修正后合同的证据，所有控制表/ControlHub/工厂仍拟新增。现存28业务表，建议新增3，未来31不是当前事实。长期export/backup/restore/activate数据job的唯一权威为受信私有控制区ControlHub；业务库中的data_operation_jobs仅是同T可读观察/归档史，record_class=reference_fence则是K1源PG引用准入事实，两者不混为同一进度权威。

ControlHub位于受信配置RETROLUME_CONTROL_ROOT，Windows本机私有目录，独立于data_dir/backup_dir/restore_root。普通包、浏览器及模型不能给路径/DSN/命令。控制journal按长度/序号/前hash/内容hash/commit尾标验证，追加flush/fsync完成尾标为权威发布点；state.json/selector.json仅可重建缓存，不是第二套权威。job、target注册、模式fence、selector_commit在同一journal时序，限定单个OS文件锁写者。断尾不算COMMIT，已确认prefix可重放；中段坏/根身份不符/权限未知失败关闭。只写本产品数据操作状态，项目TASK/STEP唯一状态仍DocuS执行动态，由主控维护。

控制区持plans、published包root收据、target业务ID到精确资源/生成路径/DPAPI凭据引用的私有注册、原恢复job、selector、mode fence、停止登记、latest accounting/删除索引及各hash。资料/学习/原件/账业务权威仍在source/target PG与原件根。控制区删除/账旁证带来源/时点/digest，源不可读只作为last-known，不能声明最新或授额度；控制秘密和资源实例不进包。

三个同T载体

- data_control只读投影源dataset_id、schema_profile、created_at及instance/mode的observed字段、已知来源snapshot/摘要；排除live mode写票据、root epoch授权、选择器、秘密和可执行实例。源PG的同一个REPEATABLE READ READ ONLY连接用snapshot角色读取，写入metadata/source_control.json；manifest记其hash/观察时点。不读取ControlHub实时state补进T。
- data_operation_jobs只读投影source row ID、record_class、原业务键的普通历史标识、kind、request hash、scope摘要、observed stage/state、package/root摘要、byte/file/row counts、error、created/updated/terminal及control_event_seq observed。source history mirror可能落后Hub，明示只是T观测；reference票据仅安全历史摘要，排除pin_nonce/owner/active权限。载体metadata/operation_history.jsonl；checkpoint对应历史codec，不恢复成活job/票据。
- data_tombstones投影entity_kind/id、effective_revision、删除时间、普通revocation/business标识、cleanup_state观察、manifest hash和仅hash/size的清单。路径/PID/secret不含。载体metadata/tombstones.jsonl，同T支撑deleted/revoked与引用不可用；后来删除并集在overlays/deletion_overlay.jsonl，明确T2和来源unknown，不伪装同T。

snapshot只对28表白名单列及这3表的安全列/只读view SELECT，不得以data_app成员或EXECUTE写/删除函数补读。三view为data_export_control_v1、data_export_job_history_v1、data_export_tombstones_v1，固定受信定义，security_invoker和必要底层列SELECT对应。一个连接/一个T读取31表安全投影，非多个事务，角色无DML/DDL/服务器文件能力。

目标data_control的target dataset/instance/root IDs、mode=loading和加载绑定由可信工厂/data_owner初始化，source投影仅元数据，不覆盖该行。target data_operation_jobs由restore_loader INSERT record_class=archive_history、authorizes_reference=false的历史映射，原ID置origin_source_row_id，目标history ID按受信codec生成，不保活key/票据；只读data_snapshot_job_history_v1供读，切换后job查询不依赖它。target data_tombstones由loader INSERT包内同T安全行，再按受信计划在seal前INSERT后续删除覆盖；冲突取较新修订，旧行保origin标识，不能把pending清理当目标实际done动作。目标无清理任务授权。

源snapshot LOGIN只成员retrolume_data_snapshot；runtime LOGIN成员retrolume_data_app只读状态/固定业务函数。source不授restore_loader。引用票据/epoch函数只受信本机协调器可用，API不提供任意nonce/根/状态参数。target bootstrap掌握单次初始化DDL/role许可；loader只在新目标loading时有固定INSERT及来源指针回填；seal撤成员/票据，readonly LOGIN有28安全读及3安全view SELECT，无普通DML/退款/旧执行权。data_owner控制函数不从PUBLIC执行，ControlHub私有句柄/工厂凭据由可信host持有，snapshot无此权限。

内部闭包签名

- ControlHub.create_or_get_job(command, origin_context) -> JobReceipt，固定kind/业务键/request hash，先journal持久确认，不依赖当前选中PG；不同hash冲突。
- get_by_key(key, kind)/reconcile(job_id) -> Receipt+control_seq，不执行业务；读取完整journal权威，缓存坏则只读重建，不能重新发恢复/切换。
- RestoreController.prepare(upload_id, policy, origin_context) -> Plan(plan_id, plan_sha, package_sha, overlays_status, limits)，包校验和范围确认，不建目标；latest source不可读标unknown。
- TargetFactory.allocate(job_id, accepted_profile_id) -> TargetRef，profile来自私有受信配置，含固定OCI/版本、root/port/name/额度；新建精确独立集群，注册intent早于动作，实际CID/身份确定后注册，碰撞/未知停止对应目标，不重建。返回无DSN。
- verify(job_id, plan_sha) -> VerificationReceipt，解密私有credential引用仅入内存/限定子进程，受信001—013先安装，加载31安全域、原件、九分支/两FK，做只读数据/权限核对；源不可读不当验证已失败，但未知删除/账边界保留。
- seal_readonly(target_ref, verification_sha) -> SealReceipt，确认PG mode只读、撤loading权/临时bootstrap与loader凭据，保readonly凭据DPAPI引用供后续本机只读连接；先seal确认，再journal verified。
- activate_readonly(job_id, plan_sha, confirmation_key, expected_selection_generation) -> SelectionReceipt，先校验sealed/计划/用户动作、提交fence、停止精确源自有工作、冻结源写、保存latest旁证，再journal selector_commit。选择器提交为切换点；实际新app绑定与模式检查不符则不可用，不回退旧源写。

凭据仅host可信ProfileProvider读取，bootstrap/loader每target新生成并在seal/失败后撤销，readonly凭据可用DPAPI保护持久引用；Source snapshot凭据只按受信配置载入。跨Windows用户无法解密不能绕过，用户可另行配置新受信只读/验证profile，不从包恢复私配。只有能力配置缺失时return restore_executor_missing，不“看情况”自动扩大权限。

切换失败闭包

- source不可读，Hub仍能查原job/包/验证收据；latest账和删除状态unknown，只可验证/隔离只读查看，不宣源停止；没有可证明停写/旧实例结束则不提交selector。
- 旧实例仍活，fence拒新业务，已登记manager/preview走原停止权；止不住保maintenance_unconfirmed，源执行/退款不猜，target仍sealed，selector不变。
- 控制区不可读或中段journal坏，拒create/verify/activate和新业务写，不靠target历史表、cache、已有目录或旧私配选择源；完整prefix和配置可取得时只读replay/reconcile，不制造新操作。
- credential blob/file已落但target_ready/selector尾标未COMMIT，只为未引用私有资源/意图；不得当切换。已selector_commit而HTTP响应丢失，GET原key回同generation，不第二次activate。
- 新dataset/instance后刷新，/api/data/jobs/by-key和包入口仍由同ControlHub解析，独立于当前PG；业务GET只读新target。namespace切换使旧draft/owner不复活，丢模式信息或target连接则显示不可用，不自动尝试原源。

MaintenanceCoordinator新增全应用MutationPermit和实际自有登记，非当前ClosingCallGate。原所有POST及资料发布/新引用、PDF确认/补充、范围/目标/记忆命令、model/tool admit+dispatch、preview open、内部producer/后台补收据都在新写入口检查当前selector代次和fence；业务写permit持至DB结果/dispatch登记的核对点，关闭收尾lane仅授已有登记owner。fence先拒新permit，再让原SUP关发送/等旧工作收尾，再取跨进程写排他、把source data_control置frozen。停写区间持续跨selector COMMIT和新只读绑定，失败也不因超时重开；reconcile只能在确认旧绑定/状态后受信解围。读job/只读核对不中断，DB事务不等网络/用户。包的历史state不解除这个fence。

永久只读恢复副本能验可携导出、隔离恢复一致和只读查阅，不能验恢复后持续付费/工具/预览/旧学习活动继续。原库普通本机重开不变，完整NFR005持续使用/执行恢复属于后续验收，STEP017-P1通过也不能签全部恢复并继续Must。这一边界必须在采用包、UI和矩阵一致，而非另让用户选一套技术。
