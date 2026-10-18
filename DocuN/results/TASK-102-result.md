# TASK-102 / R-096 学习记忆生命周期与删除一致性完整实施合同

结论为 A—D 合同收敛完成，唯一推荐 G9-P 是独立版本化记忆、固定的新活动选用快照、服务端全链失效和记忆正文精确清理；合并包待编排核证及必要批准，产品尚未实施，G9、STEP-013、M-1 和项目均未获通过。

## 交付、身份与证据边界

本结果是唯一合同正文。完整结果位于 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-102-result.md。证据目录为 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-102/，包含 read-hashes.json、function-facts.json、source-facts.md、consistency-check.json 和 session-accounting.json。唯一附录位于本结果末尾，不另建合同或演示平台。

审阅导航为 [读入指纹](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-102/read-hashes.json)、[实际函数定位](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-102/function-facts.json)、[源码事实及读取范围](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-102/source-facts.md)、[文档一致性记录](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-102/consistency-check.json)、[计量与失败账](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-102/session-accounting.json)。

实际根目录为 D:/shspic/project_NO3_RetroLume-agent，入口为同根 AGENTS.md，task_model，锁定 V4.0 / 公共 AGENTS CHG-0003，需求 v1.1、架构 v0.87、执行动态 v2.09，公共阶段 07。关联 STEP-013、STEP-009/012、STEP-017 和 STEP-006/007/008 的消费边界，NFR-005、DR-001/002/003、FR-003/004/010、SEC-001/002，MOD-005、FLOW-004/007、DATA-006、API-005。FR-004 的引用支持与位置仍须分别验收。

当前真实客户端是 Codex desktop，系统标识 GPT-6，精确部署型号不可见；A+ 是卡面安排。本聊天实际接收用户转来的 TASK-102。当前上下文没有原 TASK-100 执行聊天，无法证明本聊天就是原修复04窗口，也无法核实原窗口是否可续，故只依据指定文件承接事实，不伪称恢复了原聊天。没有接管 TASK-101 独立审计，没有派子 Agent，没有重审品牌或旧 G8。

首个固定时点为 2026-10-06 09:31:13 +08:00；此前入口与首读的逐段耗时未知，另作保守计量。最终计量见 session-accounting.json。只读/hash/文档封装计入本卡的新许可，不借用 100/101 余额，不清零旧失败与未知。

输入快照的 40 个项目对象、七项公共规则和本卡共 48 项初核一致。必要直接依赖补核 11 项，总计 59 项，完整 SHA-256 和字节数见 read-hashes.json。七规则的 hash 核对不代表读取了不适用的 00/05/06 正文；实际正文读取为入口、公共 AGENTS、WORK 第4/6/8/9章、07、TASK_TEMPLATE，以及卡面最小输入。源码核心三个 hash 与卡面相同。

本卡证据是 B 级文件、源码与合同一致性，附录推演是 D 级逻辑说明。没有 DDL、compile、unittest、PG、HTTP 应用、Windows/Job、Docker/inspect、browser/driver、build、模型、工具、真实 provider 或付费运行。没有 Git 写入、安装、产品/测试/夹具/dist/配置写入，也没有正式 DocuS、公共库、原始需求、归档或其他卡的修改。四个 PostgreSQL 官方页面只核必要数据库语义，未向外查询项目路径、私有代码、资料或凭据。

## A 真实基线与完整闭环

### A1 当前四类状态

当前活动事实由 activities、activity_scope_sources、activity_operations 和 activity_operation_results 承担。活动记录 scope_revision、execution_generation、发送关门、租约和四类累计预算；007 的模型/工具规范正文是唯一结果正文。它们不是用户显式保存的长期记忆。

009 增加 teaching_heads、teaching_commands、teaching_records。事实以 activity_id / record_id / body_sha256 / source_refs 绑定，用户目标、作答、纠错以新记录追加，模型正文仍在007。teaching_records_immutable 对任何 UPDATE/DELETE 拒绝，applied_revision/state_after 也是一次 INSERT 形成的历史效果。teaching_heads.projection 是可重建的当前教学投影，不能充当长期能力事实。

长期学习记忆尚无实现表、保存/修正/撤销 API、跨活动选用快照或清理授权事务。旧 LearningService.execute 和 messages_for 只装配目标、资料和一个父成果；TeachingService._freeze_model_context 装配本活动实体、资料、有限前史，未接个人记忆。词项片段不是已接通的 pgvector 记忆检索。

前端 teachingIntents 的 localStorage 摘要和 IndexedDB 正文用于恢复未确认动作及编辑草稿；teachingEditorOwner 使用 sessionStorage 加活跃 Web Lock 防止复制标签页共享 owner。它们不证明服务端保存，不是记忆库，也不能自动生成长期记忆。

以上依据分别为 backend/migrations/002_activities.sql、007_activity_operation_results.sql、009_teaching.sql，activities/repository.py、activities/teaching_repository.py、learning/teaching_service.py、learning/service.py、learning/prompt.py，以及 frontend/src/activities/teachingIntents.ts。精确定位见 source-facts.md 和 function-facts.json。

### A2 可复用能力与真实缺口

复用 G8 的不可变事实、逐记录来源资格、曝光纪律、纠错争议、有限进度、严格 HTTP 输入、同键恢复、版本 CAS、公开读面及编辑身份。TASK-099 第3/4/6/7节定义其批准边界；TASK-100 的最终差异和 TASK-101 review-03 确认有限成立。未改变的监督、停树、结算、UNKNOWN、模型/工具预算证明继承，不把它们重新包装为本卡新运行。

缺口不止一个记忆列表。当前 context_body 保存完整 frozen.messages；若直接把记忆正文拼入这里，撤销后持久消息会成为新的副本。现有单 SQL 公开读只核活动/来源，不能阻止通过007、教学历史、引用、G7 seed 或派生重建绕回记忆。当前资料 API 只有列表、导入/替换和内容读，没有真实用户删除入口；原件库只有 put/verify/read，没有发布原件的删除方法。009 也没有事实删除例外。实际数据库登录角色、拥有者及授权未读取、未连接核实，不能把 REVOKE PUBLIC 宣称为已验证的普通 app 最小权限。

本推荐对这些缺口各给一处实现归属，不扩建向量工程、通用事件平台、记忆微服务或监督器。

### A3 唯一最小闭环

用户在教学成果旁明确“保存为学习记忆”，或者在记忆区保存自己的偏好、自报或待练难点。服务端形成独立记忆 ID、版本、性质、不确定性与来源依赖；不覆盖教学事实，不自动保存模型建议。

用户在记忆区查看、修正或撤销。修正追加版本；旧版本保留为历史但停止消费。教学观察的受检层由应用依据指定事实构造，用户编辑只能改变用户注记或明确的自报层，不能把文字改成已验证掌握。

新活动明确勾选具体记忆版本，创建事务同时冻结资料与记忆选择。旧活动不自动获记忆，新活动不自动沿用最近选择。本版通过教学工作区的 plan/exercise/evaluate 使用有限背景。旧 G7 学习、普通 continue 和通用工具入口不消费这种背景；对已选记忆的活动拒绝这些不理解记忆合同的调用，不能静默忽略选择。未选记忆的旧调用保持原行为。

来源替换/撤销、相关原观察被纠错/续答替代、上游记忆修订/撤销、本记忆修订/撤销或活动范围改变，均使既有选择失效。消费只接受固定选择，不自动切新版。失效立即进入服务端读取、意图接受、launch、admit、mark、结果提交及重建的判定；旧输出不再成为当前依据。

撤销先提交不可逆的逻辑墓碑，再按已确认的精确版本/hash清单清除记忆自身正文。原事实、资料、活动历史和备份的实体删除不在 G9-P 内，归 STEP-017 或另获授权的退出合同。旧远端请求和此前已返回浏览器的字节不能召回。

### A4 边界与取舍

长期记忆保存零模型、零工具、零模型费用；本次不调用模型写摘要。有限教学观察摘要用确定性白名单投影，性质始终是“该活动当时的有限观察”。记忆只是当前任务背景，不加入本活动的新独立作答计数，不授予工具或费用权限，不构成题目正确性的新引用通道。

后续文字面试可以采用同一选择与资格协议，须由 STEP-014 的实际接口合同接入；本包不实现面试。STEP-017 负责备份、跨副本恢复和原事实/原件删除。完整向量检索、真实 provider 条款/容量/质量、HTML、M-1、部署和全 Must 均保留原门。

选择活动级失效，而非逐句追踪模型如何受一条记忆影响。一个活动选了四条记忆，任一失效便抑制该活动全部派生模型/计算结果及进度。这是保守且可解释的最小合同，避免未知的内容依赖漏记。用户原始目标、作答和纠错仍可按历史身份查看；它们不自动重新变成记忆或当前能力。更细粒度复用只能另行提出具体变更。

## B 唯一最小数据、事务与服务合同

### B1 拟新增持久对象

以下七表属于拟议 010_learning_memory.sql，不是现存实现。不修改001—009，不增加 activities、activity_operations、007正文或教学事实的列，不增加 operation kind，不更改现有 source_refs 形状。

七表分别承担头、不可变版本元数据、可精确清理正文、类型化依赖、幂等收据、活动选择头与选择项。正文单独分表，使清理不必改写版本身份、FK 或不可变教学事实；选择项单独分表，使版本 FK 真实成立；收据不能塞入009固定 action 或007 model/tool非空域。没有摘要/向量/缓存表。

所有新对象使用本次核定的同一产品 schema。下一卡先核实际 schema；推荐合成目标为 public。若既有库不在 public，不自动建平行基线，交编排给实际同构落点。下列关系均无 ON DELETE CASCADE。UUID 只承载身份，不作认证；时间均为服务端 TIMESTAMPTZ。

M1 learning_memories

- memory_id UUID 主键。
- revision INTEGER NOT NULL，1..2147483647，为修改/撤销 CAS 版本。
- current_version INTEGER NOT NULL，1..32，为当前正文版本。
- state TEXT NOT NULL，active 或 revoked。
- created_at、updated_at TIMESTAMPTZ NOT NULL。
- revoked_at TIMESTAMPTZ、revocation_key UUID、purged_at TIMESTAMPTZ 可空。
- purge_state TEXT NOT NULL，none、pending、done。
- CHECK 规定 active 时 revoked_at/revocation_key/purged_at 均空、purge_state=none；revoked 时 revoked_at/revocation_key 非空，pending 时 purged_at 空，done 时 purged_at 非空。
- (memory_id,current_version) 指向 M2 的 FK 为 DEFERRABLE INITIALLY DEFERRED，允许同事务插入头和首版；(memory_id,revocation_key) 指向 M5 的 (memory_id,business_key)，延迟检查，撤销收据必须属于本记忆且 action=revoke。
- 索引 (state,updated_at DESC,memory_id)。状态不可从 revoked 回 active，不能因恢复清零 revision。

M2 learning_memory_revisions

- (memory_id,version) 为主键；memory_id FK M1，version 1..32。
- claim_kind TEXT NOT NULL，self_report、preference、focus、learning_observation。
- uncertainty TEXT NOT NULL，self_reported、unknown、limited。learning_observation 只能 limited 或 unknown；其他种类只能 self_reported 或 unknown。
- policy_version TEXT NOT NULL，memory.user.v1 或 memory.observation.v1，与 claim_kind 对应。
- body_sha256 TEXT NOT NULL，小写64位hex；body_bytes INTEGER NOT NULL，2..4096。
- dependencies_sha256 TEXT NOT NULL，小写64位hex；dependency_count SMALLINT NOT NULL，0..32。
- created_by_key UUID NOT NULL UNIQUE；(memory_id,created_by_key) FK M5 的 (memory_id,business_key)，延迟检查；created_at TIMESTAMPTZ NOT NULL。
- 版本元数据 INSERT 后任何 UPDATE/DELETE 均由触发器拒绝。没有正文、标题、用户文字或模型意见。
- 受检观察至少有一个 event 依赖，并由对应 progress 的真实关联链补齐来源、answer/exercise/feedback/纠错资格；不能只拿单个 record_id 赋性质。

M3 learning_memory_bodies

- (memory_id,version) 主键，FK M2；body TEXT NOT NULL，规范 UTF-8 JSON，2..4096字节。
- body 包含标题、用户正文/注记、受限观察摘要、性质与不确定性；标题至80字符，用户正文至1024字符且总正文仍受4096字节约束。禁止 NUL、孤立代理、重复键、非有限 JSON 数值及超深结构。
- INSERT 触发器先核并取得本M1头的KEY SHARE锁，要求active且属于正在原子形成的合法版本，再核真实 UTF-8 bytes/SHA-256 与 M2 一致，应用同时核 canonical JSON。revoked/purged头禁止重插正文，不能用INSERT恢复已删内容。UPDATE 永久拒绝。
- DELETE 仅允许专用 NOLOGIN 清理函数拥有者的执行上下文；普通 app 既无 DELETE 权限，也不能 SET ROLE 到该拥有者。
- 清理仅删除这一行；M2 和引用身份保留。原始正文移除后不可由头重建，缺行只能表示不可用，不能从旧活动补齐。

M4 learning_memory_dependencies

- (memory_id,version,ordinal) 主键，ordinal 1..32；FK M2。
- dependency_kind 为 source、event 或 memory。
- source 组使用 source_id UUID、source_version_id UUID、source_revision INTEGER 0..2147483647、original_sha256 TEXT 64hex；(source_id,source_version_id) FK material_versions(source_id,id)。
- event 组使用 origin_activity_id UUID、record_id UUID、record_kind TEXT、record_sha256 TEXT 64hex、origin_scope_revision INTEGER 正数、origin_goal_version INTEGER 1..32；(origin_activity_id,record_id) FK teaching_records(activity_id,record_id)。record_kind 限 exercise、answer、feedback、progress、correction。
- memory 组使用 upstream_memory_id UUID、upstream_version INTEGER 1..32、upstream_body_sha256 TEXT 64hex；复合 FK M2，且 upstream_memory_id 不等于 memory_id。
- CHECK 用逐组显式 IS NOT NULL / IS NULL，恰好一个组完整，其他组全空，拒 SQL NULL 三值绕过。
- 每类目标的去重使用三项部分 UNIQUE 索引；source 索引 (source_id,source_version_id,memory_id,version)，event 索引 (origin_activity_id,record_id,memory_id,version)，memory 索引 (upstream_memory_id,upstream_version,memory_id,version)。
- 应用只从服务器核过的来源/事实/选用继承依赖，不接受客户端传依赖数组。每版至10个来源、8个教学事实、14个上游版本，合计至32项，超限拒绝保存，不静默丢依赖。上游依赖以有界闭包展开并携全部源/事件依赖，避免运行时无限递归。循环、自引用、闭包超限拒绝。
- INSERT 后禁止 UPDATE/DELETE。用户修正保留既有依赖，不允许移除失效来源来“修复资格”。

M5 learning_memory_commands

- business_key UUID 主键；action 为 save、revise、revoke、purge。
- memory_id UUID NOT NULL，FK M1，延迟检查。
- request_sha256、slot_sha256 TEXT NOT NULL，64hex；effect_applied BOOLEAN NOT NULL。slot_sha256 仅在 effect_applied=true 时由部分 UNIQUE 索引占用；同内容无效应收据不占未来CAS修订槽。
- UNIQUE(memory_id,business_key) 支持头和版本的同记忆复合FK。after/before关系由guard按action核定，不能统一假设每次操作都增加revision。
- before_revision INTEGER 0..2147483647，after_revision INTEGER 1..2147483647，after_version INTEGER 1..32。
- result_meta TEXT NOT NULL，规范 JSON，2..4096字节，仅 ID、版本、性质、结果状态和计数。
- cleanup_manifest TEXT 可空，规范 JSON 2..8192字节；manifest_sha256 TEXT 64hex可空，成对出现。只有 revoke 收据携完整清单；purge 收据只引用原 revoke key/hash。
- committed_at TIMESTAMPTZ NOT NULL。收据、请求身份与清单全部不可改写/删除。
- 不保存请求正文、标题、注记或撤销正文。请求 hash 的比较必须由服务端重算，模型不能指定。
- 所有记录代表已 COMMIT 的数据库事实；数据库不可读时不制造 unknown/failed 收据。确定失败通过 API 与脱敏诊断报告，未确认通过本机意图保留。

M6 activity_memory_bindings

- activity_id UUID 主键，FK activities。
- selection_sha256 TEXT NOT NULL 64hex；create_request_sha256 TEXT NOT NULL 64hex。
- bound_scope_revision INTEGER NOT NULL 正数；bound_scope_sha256 TEXT NOT NULL 64hex。
- selected_count SMALLINT NOT NULL，1..4；policy_version TEXT NOT NULL 固定 memory.selection.v1；selected_at TIMESTAMPTZ NOT NULL。
- 无记忆选择的旧/新活动不建此行，不回填。头与项的精确数量、规范排序 digest 和资料快照由延迟约束触发器核对。
- 全列不可 UPDATE/DELETE。只在创建活动同一事务中 INSERT；没有给已执行活动补选、自动清空选择或改选的接口。

M7 activity_memory_choices

- (activity_id,memory_id) 主键，activity_id FK M6。
- version INTEGER NOT NULL 1..32，FK (memory_id,version) 到 M2。
- selected_revision INTEGER NOT NULL 正数；body_sha256 TEXT NOT NULL 64hex；ordinal SMALLINT 1..4。
- UNIQUE(activity_id,ordinal)，索引 (memory_id,version,activity_id)。
- 全列不可 UPDATE/DELETE。选择顺序和具体版本是用户同一次确认的内容，不是最近版本查询结果。

M2/M4/M5/M6/M7 的不可变触发器、M1 的单向撤销与版本递增 guard，以及 M3 的正文核验/精确清理 guard 属于010。新增纯 SQL 资格函数 memory_revision_eligible(memory_id UUID,version INTEGER) 为 STABLE、SECURITY INVOKER；活动资格函数 activity_memory_eligible(activity_id UUID) 同样只读。它们不写时间、摘要或清理状态，不标 IMMUTABLE，不持网络等待。

memory_revision_readable同为STABLE/SECURITY INVOKER。三个资格函数与guard/清理函数均在创建事务撤销PUBLIC权限；app仅获需要的只读函数与清理函数EXECUTE。依赖摘要使用固定ASCII字段顺序的行串，按ordinal连接source|source_id|version_id|revision|hash、event|activity_id|record_id|kind|scope|goal|hash、memory|memory_id|version|hash，各行以换行分隔。选择摘要按ordinal连接memory_id|version|revision|body_sha256；资料范围摘要按source UUID排序连接source_id|version_id|revision|original_sha256。UUID/枚举/hash不含分隔符，整数用无前导零十进制。应用与SQL使用相同UTF-8 SHA-256协议，禁止用JSONB::text当现有canonical JSON，否则键序/空格会改变hash。正文/manifest/context仍对保存的canonical TEXT原字节核hash。

### B2 唯一资格公式与依赖传播

单版记忆可消费，必须同时成立以下条件。只读函数 memory_revision_readable(memory_id UUID,version INTEGER) 核正文、来源和依赖，允许仍active的旧版作为明确的superseded历史查看；memory_revision_eligible另加current_version要求；activity_memory_eligible再加所选revision与活动范围要求。历史可读不等于可消费。

- M1 存在、active，消费时 current_version=所选 version；活动消费另核 revision=所选 selected_revision。revoked头的任何版本均不返回正文。
- M2/M3 存在，真实正文 bytes/hash 与版本元数据一致，结构与 policy 可理解。
- 全部 source 依赖对应材料当前版本、revision、原件hash；PDF 还须沿既有 confirmed/逐页核对完整性。原件读取时沿 OriginalStore 的实际校验。
- 全部 event 依赖对应不可变的种类、hash、原 goal/scope。其关联 answer 未被后续 answer.supersedes_record_id 替代，相关 feedback/progress 没有后续 correction 争议或新的同答案评价。保守地把这些后继视为原摘要已过时，须用户明确新保存当前观察，不能推断“后来也正确所以旧版重新有效”。
- 每一 upstream 依赖的头仍 active、仍是该 version，正文hash仍相等；其源/事件闭包已经随当前版保存并逐项核。坏组、缺项、循环或未知 policy 一律无资格。
- 没有依赖的用户自报/偏好可独立保存；它们永远不是证据判断。对已有来源记忆的用户编辑仍携原依赖，不能洗掉来源。
- 来源 old activity 的取消、到期或新目标本身不抹除当时的事实；不要求旧活动仍能执行，但上述原观察及来源的资格必须成立。

活动选择可消费，还须 M6/M7 数量/digest/hash完整，活动当前 scope_revision 与 bound_scope_revision 相等、当前资料快照 hash 相等，且全部选择可消费。选择为零的 legacy 活动走原合同，不因010安装自动获得背景。来源范围必须覆盖所选记忆所有来源依赖的同一版本/revision/hash；记忆不能扩大范围读取未选资料。

此公式由同一 SQL 读取快照产生布尔资格和原因；API 在同一语句中 CASE 抑制失效正文。失效先于旧终态正文展示；同键收据仍可确认已提交身份，但不回撤销正文。新增 invalidated_memory / memory_invalid qualification 只描述读取资格，operation 的真实 received/unknown、原费用和预算不改。

来源变更无需全库写 invalid 标志或改记忆 revision。PostgresMaterials.save / confirm_pdf_candidate 在原来源锁内提升 revision，后续公式立即拒旧版。M1 的修订/撤销直接改变同一公式。删除、后台缓存通知或 UI 广播都不是这道数据库权威的替代。

### B3 HTTP、DTO 与实际服务签名

拟新增模块为 backend/app/memory/。MemoryLedgerMethods 复用 PostgresAdmissionLedger 的同一 _transaction/连接；没有第二状态账。MemoryService 只做规范输入、确定性有限投影和事务调度，模型不写记忆。

新的服务面如下，都是拟议签名。

~~~text
MemoryService.submit_command(command: MemoryCommandInput) -> MemoryReceipt
MemoryService.list_memories(limit=20, cursor=None) -> MemoryPage
MemoryService.read_memory(memory_id, version=None) -> MemoryView
MemoryService.read_command(business_key) -> MemoryReceipt | None
MemoryService.preview_change(memory_id, expected_revision, action) -> MemoryImpact
MemoryService.preview_observation(activity_id, progress_record_id) -> MemoryCapturePreview
MemoryService.purge_memory(command: MemoryPurgeInput) -> MemoryReceipt

PostgresAdmissionLedger.apply_memory_command(command) -> MemoryReceipt
PostgresAdmissionLedger.read_memory_snapshot(memory_id=None, limit=20, cursor=None)
PostgresAdmissionLedger.read_memory_selection(activity_id) -> MemorySelectionSnapshot
PostgresAdmissionLedger.create_activity(spec, memory_selection=None) -> None
~~~

最后一个是既有 create_activity 的新增 keyword 参数，原 spec-only 调用仍合法。MemoryLedgerMethods 的全部辅助方法用 _memory_ 前缀，不能覆盖原 _transaction、_source_rows 或教学 MRO 行为。

HTTP 为 GET /api/memories，GET /api/memories/{memory_id}（可带version查询读取只读历史），GET /api/memories/commands/{business_key}，GET /api/memories/{memory_id}/impact?expected_revision=...&action=revise|revoke，GET /api/activities/{activity_id}/memory-selection，以及 POST /api/memories/commands。观察预览为 GET /api/activities/{activity_id}/teaching/records/{record_id}/memory-preview，只接受 progress 及其可核关联链。命令静态路径先于 UUID 路径。GET 全部无副作用，不保存新摘要，不启动清理。

MemoryCommandInput 为严格 schema=memory.command.v1，business_key UUID，memory_id UUID，expected_revision 整数，action 及对应 body 的封闭联合。body 只有以下四类。

- save。expected_revision=0。自报/偏好/难点给 kind、title、text；不确定性由类型限制。教学观察给 kind=learning_observation、title、note 和 capture{activity_id,progress_record_id,record_sha256,view_token}。应用重取指定事实及关联链，构造观察正文，客户端不得提交 observed_count、mastered、support_checks、source_refs 或摘要权威字段。
- revise。expected_revision≥1，body 给 title、text 或用户 note、base_body_sha256、impact_token。学习观察受检层不接受任意替换；改成自报需要 body 明确 kind=self_report，保留并显示原来依赖。每次版本加1、revision加1；同内容无效应重复不增加版本。revoked 不能修订。
- revoke。expected_revision≥1，body 给 impact_token、confirm_revoke=true、purge_memory_content=true。确认涵盖当前及所有历史记忆正文，以及所有固定选用/派生依赖的失效；不包含删除原始作答、资料、活动历史或备份。原子提交 M1.revoked/revision+1、精确清单和收据，再在该显式动作内至多尝试一次第二阶段。重复原 revoke 请求只重放收据，不额外触发清理。
- purge。body 给 revocation_key、manifest_sha256、confirm_memory_cleanup=true。只接受已撤销的该 memory_id 和原清单；用户显式重试待清理时使用此命令。不接受任意表名、路径、记录清单或原件 hash 作为新的删除目标。

Canonical 规则沿项目已有 canonical/sha，业务 hash 排除 business_key、包含 schema/action/memory_id/expected_revision/body。服务端拒未知字段、递归重复键、非法UTF-8、NUL/孤立代理、非规范UUID、bool冒充整数及超过32768字节输入；正常 Unicode 保留。请求文本规范化须前后端一致，不在 hash 核对之后再悄悄 strip。response 上限65536字节，列表默认20、最大50，用单语句 watermark/当前资格 digest 的分页游标；变化回409 snapshot_changed，不拼不同快照。

MemoryReceipt 包括 schema、business_key、action、request_sha256、memory_id、revision_after、version_after、status=committed、duplicate_of可空、qualification_now、purge_state_now、revocation_key/manifest_sha256可空。收据无正文。MemoryView 包括 ID、revision、version、性质、不确定性、read_at、view_token、资格、来源事件身份、当前正文可空和删除阶段；revoked 或来源/依赖失效时标题、用户注记和摘要全部抑制，仅保留固定标签、ID、性质与不可用原因。

权限沿真实 _guard → local_session(allow_own_origin=True)，每个记忆读/写都检查会话和来源请求。当前只有单人本地工作区，不虚构账号/user_id/租户；有这个有效应用会话才可访问本工作区。浏览器 owner 只管草稿，客户端 UUID/hash/CAS 只管身份，不授予权限。模型、资料和工具结果没有记忆命令入口。

错误语义为400 invalid_input、413 request_too_large、403 本地会话/跨站拒绝、404 memory_not_found 或 record_not_found、409 memory_revision_conflict / command_key_conflict / memory_revoked / memory_source_invalid / memory_dependency_invalid / memory_dependency_limit / memory_scope_mismatch / memory_context_limit / snapshot_changed / memory_version_limit / memory_version_not_current / memory_profile_required / impact_changed / context_version_unavailable，503 memory_unavailable / memory_schema_not_ready / memory_permissions_not_ready / integrity_error。原教学 TeachingRefusal 的映射需增这些确切 code；其真实未登记code默认422，不能沿默认值冒充约定409或503。连接中断或提交回执丢失为前端 unconfirmed，不等于确定未提交。

创建活动的兼容扩展为可空 memory_selection，非空时恰有 confirmed=true 和1..4项 entries{memory_id,version,revision,body_sha256}，按用户顺序且不重复。其规范创建 fingerprint 只含客户端 activity_id、source_ids、这个选择；不含服务端重新计算的 deadline/额度。资料和记忆在同一 create_activity 事务核定、同一 COMMIT。旧请求省略字段仍按原 create；非空选择在 capability 未就绪时拒绝，不能丢字段后创建。

同一 activity_id、同一创建 fingerprint 的重放返回既有创建事实和原额度，不改截止时间，不更新选择。不同 fingerprint 返回 activity_exists_conflict。已有 legacy 活动不能靠重放补选。GET 活动和 GET memory-selection 增加选择 digest/版本/资格元数据，恢复不能只比较 source_ids。

### B4 锁顺序、短事务与并发

对有记忆的路径统一采用下列扩展顺序，已有相对秩序来源→活动→操作→教学头→教学命令保持。

1. 无锁读取定位 hint。收集活动当前/原事实来源、所有记忆依赖来源、上游记忆 ID，以及待消费活动和所有原事件活动 ID。
2. 来源行按 UUID 数值升序 FOR UPDATE；去重，一次锁全部源，不在锁了其他对象后补锁更小来源。
3. 涉及的 M1 头按 UUID 数值升序 FOR UPDATE，含本记忆和上游；新 memory_id 的不存在不作有效锁，最终由主键/唯一槽竞争裁决。
4. activities 行按 UUID 数值升序 FOR UPDATE，包含消费者和原事件活动；核所有范围 hint、事件后继与选用快照。原事件活动上锁用于与 G8 的作答/纠错/新评价串行，不修改这些活动。
5. 对相关消费活动按 activity_id、operation_id 排序锁 activity_operations；再同序锁 teaching_heads、teaching_commands。M6/M7 不变，无需反向行锁。
6. 最后 M5 命令键/唯一槽，M2/M4 元数据及 M3 正文目标。新 INSERT 和更新只在这一顺序后发生。

记忆 save/revise 若带原事件，同样先来源→所有记忆头→原活动。纯自报写不需要来源或活动，只进入记忆头→收据/版本。revoke/purge 不锁或改任何活动、来源和上游；它们只锁本记忆头→收据→至多32个正文目标。这样不会形成活动→记忆的反向边。来源替换只持来源；G8 原纠错只持来源→原活动→操作/头/命令，绝不在后面补锁记忆。

既有 _teaching_lock 不能先返回锁定 activity 再去锁 M1。有选择时必须由新的 _memory_lock_prefix 完成前缀，再交 _teaching_lock 的已有后半段。admit、_locked_operation、admit_tool_operation、mark_tool_started、record_tool_outcome、claim/launch 和 T-local 同理，新增记忆前缀必须发生在第一次活动锁之前。无选择走旧路径。恢复、cancel、结算这些不消费正文且不读/写 M1 的旧控制路径不加记忆锁，不更改其监督证明。

hint 不一致、M1版本变了或来源集合发现遗漏，当前事务失败并回滚；不能持原锁补读新上下文或自动重试模型。纯DB唯一键竞争可以在一次已确定回滚后读赢家收据，不能在 aborted transaction 内继续 SQL。锁超时/确定回滚无新效果；提交状态不明则保留原键，只读核对。

新save按锁与资格核定后INSERT M1首版头→M5有效收据→M2版本元数据→M4完整依赖→M3正文，COMMIT时检查延迟FK/计数/摘要。revise先锁旧头与CAS，再INSERT M5→M2/M4/M3，最后UPDATE M1.current_version/revision；正文INSERT guard只允许首版的current_version或该受信收据对应的current_version+1，版本不得跳号。revoke先形成并INSERT M5清单，再UPDATE M1单向状态/revision，延迟FK指同记忆revoke收据。无效应/别名仅INSERT M5 false收据。purge按B7头锁与原清单核定，M3 DELETE、M5收据和M1清理状态在第二事务同COMMIT。延迟约束trigger对最终状态核M2的dependency_count/hash及M6的项数/摘要；不是在读取时容忍缺依赖。

公开读取用一条 SQL 同时取资格、相关头、版本/依赖和有资格正文；_transaction 包着几次 SELECT 不足以宣称同一快照。PostgreSQL Read Committed 的不同语句可以见到不同提交，依据 [事务隔离文档](https://www.postgresql.org/docs/16/transaction-iso.html)。写事务的多语句一致性靠上述锁及锁后 hint/CAS复核，模型、文件读取、用户等待和外部网络调用均在事务外。统一对象顺序依据 [显式锁文档](https://www.postgresql.org/docs/16/explicit-locking.html)。

同键优先于“现在是否仍 active”的资格拒绝。服务器先认证，再核持久 key/hash；同键同规范请求只返回原事实加当前抑制资格，同键异内容409。并发首次没有头时，PK/slot UNIQUE 保证一个获胜；失败方整笔回滚后核赢家。save 的语义槽是 memory_id；revise/revoke 是 memory_id 加 expected_revision，两者竞争同一修订槽；purge 是原 revocation_key 加 manifest_sha256。相同槽同 payload 返回 duplicate_of；相同槽不同 payload 返回冲突。不同 memory_id 的自报不做模型语义去重。观察捕获另外核同 memory_id 的原事件身份，不以换 business_key 覆盖。

同内容 revise 在头已锁定后核等价规范正文/依赖，不增加 version或revision；记effect_applied=false的无效应收据，不占其slot的唯一有效行，之后合法异内容仍可从原CAS修改。别键同效果的别名收据同样为false并指向真实赢家。save/revise/revoke有效效果使用true；purge只改变清理状态，不增加revision。与旧 key 不同但 CAS 陈旧的异内容拒绝，不能最后写入者覆盖。revise 与 revoke 竞争只允许一方从同 revision 生效；后到撤销需重新看新版影响。revoked 头永远不能变 active；新 memory_id 的显式自报是新的用户动作，不是恢复旧 ID。

### B5 记忆装配与 G8 接线

本版不把记忆拼入旧 TeachingFrozenContext.messages。新增 TeachingMemoryFrozenContext，schema=teaching.context.v2，profile_version=teaching.v2，只支持 model。既有 TeachingFrozenContext / TeachingProfile / TeachingCallBinding 和 v1 序列化字节保留。

v2 持久冻结内容为 operation_id、reference_hashes至12、memory_selection_sha256、固定 memory_refs至4、memory依赖摘要、catalog、max_output_tokens、prompt_version、projection_policy_version、recipe 和 assembled_messages_sha256。recipe 只列实际 goal/path/exercise/answer/correction/前史/核算记录 ID/hash、原命令动作参数和白名单投影规则，不存这些生成背景的全文。catalog 是当前资料有限片段，仍沿 existing source/evidence身份；记忆文本不成为 catalog.text。

新 TeachingMemoryProfile 使用 profile=teaching.v2，继承旧受信教学身份的字段职责，另带 memory_selection_sha256、memory_refs 和 assembled_messages_sha256。新 TeachingMemoryCallBinding 在原五个绑定字段之外核上述两个摘要。它们都是可信应用/worker内类型，不是 HTTP 输入字段。

_freeze_model_context 在当前真实实体和资料装配处取得同一资格快照，构造 recipe，读取固定记忆版本并生成实际消息，核预算，再冻结两个 digest。_submit_model 发送这个实际消息数组；接受事务核 recipe 引用、选择 digest、记忆头/正文/源/事件资格和最终消息 digest。recover accepted 时只重建原 recipe、原版本及原 prompt policy，逐字节核 assembled_messages_sha256，不重检索、不换最新记忆、不形成新摘要。旧 policy 不再可理解则 context_version_unavailable，只保留意图，不能替换冻结内容。

TeachingService._build_profile 的 v2 分支用实际发送消息 hash；旧 v1仍用 frozen.messages。teaching_adapter.validate_teaching_request 的 v2 分支从持久原 recipe 和资格快照重新构造期望消息，对比真实 request.messages，不能仅对请求自带 user JSON/hash 相互自证。gateway.call 构造 v2 binding，admit/mark锁内对冻结消息摘要和选择再次核定；OneCallInput.to_wire/from_wire 已按 ModelCallRequest 规范序列化，因此仅扩受信DTO联合，不改协议3/4、进程/SUP/Job、停止或时间账。

stored_teaching_result 的 v2封套只额外存选择ID/版本/hash及政策标识，不复制记忆正文或输入消息；模型产物仍是007结果。输出引用只能沿当轮 lc_ 目录，不能把 memory_id 当正确性引用；旧观察作为背景，不加入当前独立计数。v1封套字段/None形状不变，不能在旧 model_dump 中默认加入新可空键而改变旧 context hash。

上下文配置单独为 memory_context，默认未配置。推荐明确配置 selected_items=4、max_memory_bytes=4096、max_memory_chars=2048、max_input_tokens_estimate、protocol_reserve_tokens、model_context_tokens、reserved_output_tokens、safety_tokens、estimate_policy=utf8_bytes.v1，以及 model_identity 绑定。数值是待下一卡冻结的有限建议，不移用旧实验token。所有整数须正且相互兼容，max_input_tokens_estimate+reserved_output_tokens+safety_tokens≤model_context_tokens，输出仍不高于原 activity/service/教学2048上限。

估算为全部实际消息UTF-8字节数加显式协议预留，不声称它是所有供应商的精确 tokenizer 或已验证的上界。缺模型容量/已采用估算政策、身份不匹配、未证实适用真实供应商时，memory_model.available=false；合成卡可以核确定性估算/字节拒绝，真实容量在正式 provider 接入前另核，不借合成证明放行。精确 provider 输入限额及必要 tokenizer 如果成为采用前关键事实，再按其官方资料收敛，不本卡安装新库。

同时核完整 provider JSON bytes≤min(activity.max_request_bytes,service.max_request_bytes)、v2冻结包≤49152字节、OneCall输入/内部65536字节边界，以及所有已有目标/答案/证据/引用上限。记忆自身先受4项/总4096字节约束，不读取全库。

缩减只可去掉非必要的旧前史整项，保留它的来源/不确定性；不截断当前作答、必要原文或一条记忆中的否定/未知。所有所选记忆均作为固定依赖，本版不静默漏发某条或重写为“已掌握”。仍超限则在 accept/launch之前409 memory_context_limit，明确要求减少选择或新建较小活动，零模型/零工具。原 evidence无候选仍 no_evidence，不用记忆补伪证据。

### B6 失效时点与旧结果

逻辑修改/撤销的线性化点是 M1 与 M5 的 COMMIT；源失效是原 material_sources.current_version/revision 的 COMMIT；相关观察改变是原活动事实提交。提交后开始的单 SQL 读必按当前资格，不承诺撤回在提交前已经形成的读快照/已返回字节。

T-intent、T-launch、admit、mark 任一点发现失效均不获得下一资格。不清累计预算、不自动取消别的进程、不换 generation，不绕原claim/唯一槽。mark COMMIT 先于撤销时，远端仍可能发出或继续；这属于已消费的发送资格，撤销不能与事务外网络发包形成“零字节必然未外发”的虚假保证。

结果提交先保留原 _terminal_confirmation。已经相同终态的重放只确认旧事实，新增效果为零；其公开正文按当前记忆资格抑制。尚未提交且记忆资格已失效的成功结果，拒007正文/教学事实/进度新写；只允许原凭证的 UNKNOWN 脱敏诊断，预留保持，不退款。_locked_operation 可以返回资格布尔，不能在获取诊断资格时一概抛 memory_invalid 使 UNKNOWN 也无法登记。

原活动/来源/G/租约仍合法但仅教学答案或目标变动时，沿原G8 history分支。记忆失效则采用更严格的无正文分支，不能套“教学迟到可历史保存”例外。这种差异必须进入新受影响PG用例。

已提交的派生模型/工具结果及教学 path/proposal/exercise/feedback/progress 全部抑制正文，引用只返回不可用标记。用户 goal/answer/correction 可历史读，但不展示失效派生的节点和评价，不对这些文字自动重做记忆。_teaching_rebuild_progress、_load_teaching_entities、G7 seed和父结果消费必须先核资格，不能从旧 records/007把节点或摘要重新填入 head。

没有新 Redis/向量/持久摘要副本。进程内缓存若实际存在必须以 selection digest、各头revision、源revision、事件依赖与 policy 为键，每次出站前重核PG；本版推荐记忆正文不缓存。浏览器广播只发 ID/版本/失效状态，接收页清已显示的相关派生内容并只GET。离线/未打开页面和既有下载副本不能保证即时清除，服务端新读不会再返回。

### B7 两阶段清理、最小权限与恢复

撤销预览显示本条全部记忆版本、选用活动数量及有界分页身份、派生记忆依赖、旧内容停止展示/消费的影响，并明确原事实/资料/活动历史/备份仍保留。impact_token 绑定当前 revision、正文/依赖摘要和固定影响政策；确认授权的集合是“此记忆所有版本及所有依赖选用”，不是屏幕上前20行。提交时重算实际数量和清单，返回生效时事实。若目标版本或清单变化则409 impact_changed，不能把新版清掉。

第一阶段仅将本 M1 头 active→revoked、revision加1、purge_state=pending，与 revoke 收据/cleanup_manifest一起提交。它不遍历改活动，也不写010以外事实。即使所有模型配置失效或来源已经不可用，仍允许有权限用户撤销本条记忆。所有旧M2/M3版本在读面立即不可用。

cleanup_manifest 只含 policy=memory.purge.v1、memory_id、revocation_key、逻辑撤销revision、targets[{memory_id,version,body_sha256,body_bytes}]，按version排序，1..32项。targets精确覆盖该记忆当时全部正文版本，不携正文、标题、路径或其他记忆。清单/hash在M5不可变。被撤销内容造成的007/原教学记录副本不加入该清理清单；它们已经被全读面抑制，实体删除明确归后续原事实/活动退出授权。另经用户显式保存的派生记忆正文也不偷删，预览说明它们失效且实体仍保留，需各自明确撤销才进入各自清理清单；不能称所有内容副本已擦除。

第二阶段唯一 SQL 函数为 public.purge_learning_memory(revocation_key UUID,manifest_sha256 TEXT,purge_business_key UUID,request_sha256 TEXT)。函数读取原持久清单，核 memory_id、已撤销头/版本和清单真实hash；不接受外部目标数组。先FOR UPDATE锁M1头串行化清理，M3 INSERT guard与此冲突且永久拒revoked插入，正文又不可UPDATE，因此无需给清理角色M3 UPDATE权限去执行SELECT FOR UPDATE。核精确M3集合的真实UTF-8 bytes和SHA-256、无额外/漏列版本、无活动或来源删除项，按版本以精确PK的DELETE取得正文行锁；同事务写purge收据、M1.purge_state=done/purged_at。同清单并发和响应丢失依唯一purge槽重放，不删第二批，不产生新清单。

PostgreSQL16官方提供核心 sha256(bytea)、convert_to 和 encode，可核正文及清单，无须为此安装 pgcrypto，依据 [二进制函数文档](https://www.postgresql.org/docs/16/functions-binarystring.html)。拟用表达式为 encode(pg_catalog.sha256(pg_catalog.convert_to(body,'UTF8')),'hex')。本机实际PG版本未连接核实；下一卡先核语法/版本支持，缺核心函数则停相关迁移，不偷偷增加扩展。

拟分三个 NOLOGIN、NOSUPERUSER、NOCREATEDB、NOCREATEROLE、NOREPLICATION、NOBYPASSRLS角色。retrolume_memory_owner拥有七表/guard，retrolume_memory_purger只拥有清理函数并获M1/M2/M3/M5 SELECT、M3 DELETE、M1的purge_state/purged_at列UPDATE、M5必要INSERT；不授M3 UPDATE。retrolume_memory_app获新表所需SELECT/INSERT及M1非清理列UPDATE，只有清理函数EXECUTE，没有任一表DELETE/TRUNCATE、DDL、owner或purger成员权。M1列UPDATE加SELECT支持其头锁，M5的同记忆FK由头guard核定。业务应用现有登录身份仅在明确合成许可内映射到 app角色；本卡没有创建或授予角色。

清理函数 SECURITY DEFINER、固定 search_path=pg_catalog,pg_temp，全部产品对象 schema-qualified，不查可写public路径中的同名对象、不接动态SQL。新函数创建、REVOKE PUBLIC EXECUTE、精确GRANT与拥有者设置同一个迁移事务完成，避免默认PUBLIC执行窗口。依据 [函数安全文档](https://www.postgresql.org/docs/16/sql-createfunction.html)。普通app不能设置自定义GUC冒充删除授权，不借 current_setting 开009触发器后门，清理角色无 teaching_records/007/materials/originals删除权。

M3 DELETE guard 仅识别专用函数拥有者上下文；该角色NOLOGIN且app无其成员权。函数内仍核清单、已撤销状态、hash和完整目标，不能只认角色名就删。M1 guard只允许app递增合法版本/单向撤销，清理角色仅可从pending改done；M5保护原revoke身份和清单，清理角色也不能UPDATE旧收据。所有 PUBLIC表权限撤销；角色没有 schema CREATE、函数替换或禁用trigger权。迁移前若实际app是superuser/owner/拥有purger权，则memory_cleanup capability拒开启，不能以HTTP挡住就宣称DB隔离完成。

上述guard函数使用SECURITY INVOKER，不能用SECURITY DEFINER重置current_user，致使正文DELETE守卫看不到唯一清理函数的purger上下文。app的M1列UPDATE精确限current_version/revision/state/updated_at/revoked_at/revocation_key/purge_state（仅none→pending），禁止memory_id/created_at/purged_at；guard同时核M5动作与before/after，purger仅pending→done。readonly资格函数在结构缺失时失败关闭，绝不返回默认True。

任一hash不符、缺行、多行、角色/清单不符或SQL失败，第二阶段整体回滚，第一阶段保持revoked/pending。故障发生在“已删一行但尚未完成”时也不能留半清理。确认SQL回滚的失败可显示“已撤销，清理未完成”；提交回执未知则GET收据/头核对，未确认不能称未删或done。重开只读，不自动调用函数，用户明确“重试清理”才再用原manifest的新/同键合法意图。

done只表示在线产品库中的本条记忆正文行已清理，版本ID/hash/依赖墓碑仍在。它不承诺磁盘页、WAL、备份、浏览器外部副本、原始作答、活动结果或供应商字节彻底擦除。已知保留副本不会从常规在线恢复重新变成可用记忆；跨库/备份恢复须由STEP-017合并当前撤销墓碑/清单并先验证。如果当前撤销信息无法取得，恢复副本只读隔离、memory capability关闭，不能先消费旧active头。本包不实施完整备份恢复器。

本版恢复验收是同一PG权威库的重开/未确认核对/派生重建。当前没有产品备份恢复写入口，未来STEP-017必须在恢复导入门取得当前墓碑并保持隔离；普通启动不等于已完成副本恢复检查。未经应用控制的离线替换整库无法靠库内墓碑证明检测到回退，不作已解决承诺。已发现010残迹或teaching.v2结果但新选择/资格结构不可读时，所有相关派生读失败关闭，不能把M6缺失当legacy的True。

### B8 迁移前置、非空兼容与回退

下一卡拟编写010，单一BEGIN/COMMIT核001—009真实列、FK/CHECK/不可变trigger与008kind条件，特别009 hash/当前事实禁止UPDATE/DELETE、007正文TEXT及FK。只凭表名或同名CHECK(true)不得采用。核新七表/函数/角色残迹，重复运行或不完整前置明确报错，全事务回滚，不宣称天然幂等。

目标数据库编码必须为UTF8，schema、核心hash函数和迁移拥有者权限须在获准合成目标实查；不把非UTF8的octet_length与应用UTF-8字节上限混用。当前没有这些运行事实。

七表新增对非空001—009零回填，既有活动无M6行就是未选择，旧 received无正文不补，旧UNKNOWN/四账/范围/目标/作答不动。安装DDL与角色权限不是用户库迁移授权。本包后续只允许明确登记的合成新库与合成非空副本验证；实际库登录、非空量、拥有者、升级锁时间未知。

任一前置、索引/FK/guard/grant失败，010新对象和该事务内授权全部回滚。启动不自动运行010或创建role；只探测结构/最小权限并分层失败关闭，资料与未选记忆旧活动仍可读用。010缺失时新记忆API unavailable，不能假建空记忆表。

迁移成功但七表全空时，下一卡可在准确枚举的新对象、无外部依赖、无其他role用途证明后验证受控反向DDL；不DROP CASCADE，不动001—009。产生任何新记忆/选择后，没有批准的无损反向DROP，采用关闭新消费、保留记忆-aware读面/墓碑/数据和向前修复。不能回旧二进制让它忽略M6资格从007展示失效内容。旧二进制回退仅在没有任何新选择依赖或保留了同等失效守卫时成立；否则停服务或保留维护读面，后续用户库恢复另门。

## C 工作区、动作与文件接线

### C1 最小工作区线框

~~~text
活动工作区
  新活动的资料范围
  学习记忆背景  默认为未选择
    可选项显示性质、版本、来源活动/事件、不确定性
    本活动只用勾选的具体版本，旧作答不算本活动新表现
    选用摘要与资料范围冲突时说明原因，不能自动扩大资料
  创建活动

教学工作区
  目标 / 路径 / 题目 / 已保存作答 / 反馈 / 有限进度
  成果旁的 保存为学习记忆
    展示保存预览，性质为本活动有限观察，原始事实保留
  本活动已选记忆
    具体条目、版本、用途、外发供应商及本次用途
    失效项只显示不可用原因，提供新建活动重新选择

学习记忆区
  查看  性质 / 版本 / 不确定性 / 来源事件
  修正  用户文字与受检观察分开，变动影响先显示
  撤销并清理  先停止选用，再清理本条全部记忆正文版本
  已撤销，记忆内容清理待核对
    核对状态 / 明确重试清理
  未确认动作与本机草稿  与已保存记忆分别显示
~~~

这是现有工作区的侧区/页签，不是新的独立演示站点。按React文本展示，记忆不能插入任意HTML/脚本。来源详情只显示可理解资料/活动/事件标识、版本与原文位置，不显示数据库、路径、密钥、role或SQL。

### C2 动作纪律与用户文案

保存预览是GET及纯投影，无写入、无模型。点击确认时先规范请求→存完整本机草稿→用Web Locks写意图摘要→标submitted→POST一次。回执必须核key/action/hash/memory_id及实际结果；成功才清该动作草稿，失联保留原键。重开只GET command/detail，404仅表示读时没发现，不能自动补POST。

记忆编辑身份为 memory_id、version、revision、body_sha256、editor_owner_id。新建身份用预分配memory_id和owner；捕获还绑定原activity/record/hash/view_token。复制标签继承sessionStorage时使用活跃锁重新取得owner，缺 Web Locks/IDB 时写能力关闭，文字仍可留当前页。另一页修订后本页旧文字不自动改绑，显示“记忆已有新版本；请先核对，再明确沿用草稿”，沿用也是新的显式命令和新CAS。

恢复台账另用 retrolume.memory-intents.v1 / retrolume-memory 的专用有限库，最多16摘要/32768字节、16草稿/262144字节。复用teachingIntents的实际实现纪律，不改旧槽、不共享跨标签正文键、不创建隐式全局当前记忆。摘要只ID/hash/版本/状态，不存正文。撤销成功的本次明确动作清除本机该memory_id对应的精确草稿ID；其他活动原始答稿不删。离线设备或未知浏览器副本的清理不能冒称已完成。

修正预览说明旧选择不会换新版，所有原选用活动将停止使用旧版。撤销预览说明原事实和活动历史实体仍在，派生读面已停用，第二阶段只清记忆正文。修改或删除的未确认响应不能立即显示“全部删除”；只读核对保留动作，不重发。清理重试只用原清单。

能力门分 memory_read、memory_write、memory_cleanup、memory_model、selected_activity_legacy_actions。存储/角色未就绪显示“学习记忆暂不可用，请核对本地设置”，不能把技术role说明放业务流程。模型容量未配但存储可用时仍能查看/保存/修正/撤销，选用模型动作显示“背景使用尚未配置，本次不会发送记忆”。若已选择却能力关闭，拒动作，不静默忽略选择。

来源或记忆失效显示“所选背景已更新或撤销，此活动的相关教学内容暂不可作为当前依据；你的原始作答仍保留，可新建活动重新选择”。源替换后不展示旧来源标题/正文副本，记忆自报性质仍能辨别。并发409保留输入，让用户刷新核对；数据库503显示“状态未确认”，不当空库。

选用页面与教学请求前显示实际供应商/用途和有限所选背景；不自动外发整库。没有选用就旧教学v1。选择后旧资料问答/普通继续入口显示“此活动的背景由教学工作区使用，请从教学工作区继续”，并由服务器拒绝，不只禁按钮。后续要让G7/面试消费再接独立明确profile；本版不借普通续问接过来。

任何刷新、轮询、重新打开、游标翻页或广播只做读取；不会保存、重建持久摘要、发新模型或重试清理。最新快照失效后先清已缓存正文再展示不可用，不用旧成功卡片遮住错误。迟到读取/POST回执须比对 activity_id、memory_id、版本、owner和读序号，不抢当前编辑器/焦点。

### C3 完整拟改文件与 before/after

以下是下一实施卡的范围，本卡全部只读。新文件名是具体建议，不宣称存在。

- backend/migrations/010_learning_memory.sql。新增B1七表、精确FK/index/guards、只读资格与唯一清理函数/角色授权；001—009零修改。
- backend/app/memory/__init__.py、contracts.py、repository.py、service.py、api.py、context.py。分别提供有限导出、封闭DTO/canonical、MemoryLedgerMethods同连接事务、零费服务/显式两阶段、受保护HTTP单语句读、确定性观察/recipe重建和预算。没有provider、文件清理器、向量worker或新依赖。
- backend/app/main.py 的 create_app。现有include_router顺序增加memory router和可用性状态；不执行迁移或读取私有资料。继承no-store中间件。
- backend/app/service_config.py 的 ActivityConfig/load_activity_config。新增可空 memory_context 和分层memory能力，旧配置缺段仍保持旧层；不改用户私有配置，下一卡只在合成配置副本冻结容量。
- backend/app/activities/api.py 的 CreateActivityInput/create_activity/capabilities/_fact_payload。创建增加明确选择，单事务交ledger；能力/活动返回添加选择元数据。旧body和模型额度不自动提高。严格有界新选择请求不回退普通body解析。
- backend/app/activities/repository.py 的 PostgresAdmissionLedger。接MemoryLedgerMethods，create_activity增加keyword选择；revise_scope仍只修来源scope，它使固定选择按revision失效，不改选择。_RESULT_READ_SQL、read_committed_result/list_committed_results、_OPERATIONS_SELECT/_OPERATIONS_LIST_SELECT、read_operation/list_operations、read_activity_facts/list_activities、read_learning_snapshot均在原语句中并入选择资格，失效不投影正文。ResultReadStatus增INVALIDATED_MEMORY，旧无选择结果保留原值。
- 同repository.py的 admit、_locked_operation、mark_dispatch_started、record_outcome、admit_tool_operation、mark_tool_started、record_tool_outcome。既有来源→活动锁之前增加B4记忆前缀；所有选择活动核权限、范围和资格。通用模型/tool路径没有教学v2或合法教学calc绑定就memory_profile_required。原_terminal_confirmation/UNKNOWN/账本逻辑继承，失效成功正文拒写；诊断不被新gate堵死。
- backend/app/activities/service.py 的 continue_from_result/execute_tool_action/read_result/read_activity。原父结果状态检查包含INVALIDATED_MEMORY；选择活动仅允许教学v2与合法教学calc，不允许普通continue借旧正文重开。读服务只传递同一快照，不另读后拼装。
- backend/app/activities/teaching_repository.py 的 _teaching_lock/_teaching_lock_command、apply_teaching_local、accept_teaching_command、claim_teaching_launch、_teaching_verify_current、_locked_teaching_binding、_write_teaching_outcome、_teaching_fact_result、_teaching_rebuild_progress、_teaching_validate_seed、_teaching_read_snapshot。前缀锁→固定选择/recipe/hash→每边界复核；本地goal/answer/correct失效时仅沿有限历史保存，不产生新progress；expose/accept_path/select_node等派生动作拒。快照及history/source/payload/引用同时带记忆资格，不能从裸head投影恢复节点。
- backend/app/learning/teaching_contracts.py。保留v1类型/字节，新建v2 frozen/profile/binding严格联合及视图memory_invalid字段；stored_teaching_result v2只带身份依赖。原TeachingCommandInput字段与hash不扩，选择已由不可变activity绑定固定。
- backend/app/learning/teaching_service.py 的 submit_command/_read_receipt/_submit_model/_freeze_model_context/_load_teaching_entities/_stored_document/_build_profile。无选择走原v1，有选择走B5 recipe；模型不生成记忆；accepted显式恢复不换上下文；缺配置/失效在启动前明确拒。失效accepted的只读收据仍确认原key/hash，但retry_policy只能read_only，不能显示same_key_before_claim为可启动。
- backend/app/learning/teaching_adapter.py 的 validate_teaching_request。新增从持久recipe重建消息的v2检查，v1原检查兼容，admit/mark仍是最终权威。
- backend/app/learning/teaching_prompt.py 的 messages_for_teaching/prompt_version。新增明确版本的memory低信任背景政策，旧prompt正文/版本不改；旧已接受上下文仍可按原policy理解。
- backend/app/learning/teaching_views.py 的 public_record/regions/view_token/verified_document。结合单SQLmemory资格抑制派生正文/节点，token包含选择digest与依赖revision/资格；坏单项不扩大返回。取消历史也不绕墓碑。
- backend/app/learning/teaching_api.py 的 _workspace_payload/_current_regions/read_teaching_command/read_teaching_record/read_teaching_history/read_teaching_citation/read_teaching_seed。资格memory_invalid先于返回007派生正文和catalog，引用不可用不带撤销片段；原answer_reference只读用户原始答文，不能赋记忆资格。新增捕获预览只读progress链，不写事实或exposure。
- backend/app/learning/service.py 的 LearningService.execute。已选记忆活动在first/followup前服务器拒memory_profile_required；无选择仍旧learning.v1。learning/prompt.py读取确认没有记忆消费，本包零修改。
- backend/app/capabilities/contracts.py 的 ModelCallRequest/AdmissionIntent，gateway.py 的 ControlledModelGateway.call/结果规范分支。扩受信v2联合和binding字段，不开放客户端任意消息；原模型/tool限制和输出校验保留。worker/one_call.py 仅读兼容型序列化，无监督主体修改许可。
- frontend/src/activities/MemoryWorkspace.tsx、memoryApi.ts、memoryIntents.ts。新增实际记忆工作区、封闭读写客户端、独立owner/IDB/意图纪律。不是临时演示代码。
- frontend/src/activities/ActivityWorkspace.tsx 的 create/submitCreate/reconcileCreate/selectActivity/refreshDetail。新增选择及精确恢复identity；现有只比source_ids不能用于带记忆的创建确认。记忆创建意图用新memoryIntents分支，旧活动意图存储及槽不迁改。
- frontend/src/activities/TeachingWorkspace.tsx 的 refresh/submit/resumeAccepted/selectHistory。显示保存预览及已选背景，编辑/响应identity扩选择digest，memory_invalid清派生显示但保留原答稿；恢复只明确同键原recipe，不自动保存。teachingApi.ts增加视图/错误/预览DTO；TeachingCitations.tsx的身份包含selection/view_token，失效时清已展开引用并只GET。
- frontend/src/activities/teachingDrafts.ts、teachingIntents.ts 原格式/算法保留，不扩成跨业务共用正文槽；新记忆模块复用其设计纪律，不借重构占写范围。若实现需要直接复用teachingEditorOwner，只允许明确导出复用，不改其旧字节语义。
- 有必要的工作区样式仅限该组件实际使用的现有CSS文件，先由下一卡定位真实文件后登记，不泛泛全站美化。合成配置/迁移夹具和专用 memory tests由下一卡建立在既有tests体系，所有旧测试/夹具基线保护，不删/弱化断言。
- backend/app/materials/repository.py、materials/api.py、storage/originals.py、retrieval/evidence.py，teaching_evidence.py、teaching_policy.py、teaching_progress.py 默认只读。资格复用原source切换/PDF/OriginalStore/词项片段和纯progress规则，不改资料写锁或原件接口。DEF-019若另在相关完整实施授权内合并，按D4只动policy及必要离线边界例。

现有公开错误码/字段变化、结果资格增项、选择活动的旧调用拒绝、v2内部profile，以及新增清理函数权限，均属于G9-P一次批准的接口语义差异。除这些对象外没有随手重构或旧接口升级。未知实际样式位置不是业务关键前提，下一卡定向定位即可，不为此单独向用户问布局。

## D 验收矩阵、实施次序与合并批准包

### D1 按性质组织的未来验收矩阵

以下均是未来预期，未运行。拟议新接口以B3为定义，原接口以C3真实函数为接点。每例须留最终源hash、实际输入/返回/SQL事实/请求计数和限额；未来行为目标为A级，本卡对其只有B级映射与D级推演。

V01 显式保存与分层。输入已验合成G8 progress及其answer/exercise/feedback链，再给自报“我觉得掌握了”。观察 apply_memory_command仅用户点击保存后生成M1—M5；观察正文标limited，自报标self_reported，teaching_records及007 hash不变，模型/工具计数0。新增记忆PG/HTTP，继承G8事实性质，不从报告PASS推导新保存通过。

V02 查看/修正/历史。修订标题/用户文字，正确revision得新M2/M3/M4和头；旧版本不被覆盖。同内容无新版本；revoked不可改。接口memory detail、submit_command及版本只读。新增真实PG及定向HTTP，旧answer修正版链证明继承。

V03 新活动固定选择。带1..4有效版本、同一资料快照创建活动，原子出现activities/scope/M6/M7；任何无效记忆整笔零创建；省略选择无M6。read_memory_selection和read_activity同一快照一致，budget/deadline不重复重算。新增PG/HTTP，原活动创建预算约束继承。

V04 有限模型装配。用冻结合成资料、教学目标及两条记忆，检查实际v2消息/recipe、profile/adapter/OneCall wire hash和固定版本。两条记忆的性质/不确定性完整，旧作答ID不会成为当前独立answer；超过4096/输入估算/provider字节/内部通道边界拒于accept前。新增离线及合成HTTP/受控fake provider，全部示例调用仍走真实监督和账本；不使用mock账本代替PG。没有真实provider容量结论。

V05 来源替换与待核PDF。替换S1旧版，或建立未确认PDF候选；成功切换才改变current/revision，旧记忆拒，新候选未切换不抹旧资格。scope改成合法S2不使S1记忆复活。接口PostgresMaterials.save/confirm_pdf_candidate、memory_revision_eligible、教学read/mark。新增PG组合，复用原G8来源/PDF正常证据，不重做全解析。

V06 逻辑修订/撤销。revision1选用后修订或撤销，提交后的read/admit/mark/结果提交全部失效；旧选择不换version2。模型/工具/费用预留不退款，用户原始答文仍可历史读。新增PG竞争/HTTP；未受影响G/R/S与停止主体继承。

V07 原观察后继。保存progress为记忆后新增对应correction、answer revision或同answer新feedback；原摘要过时，后续来源仍合法也不恢复。无关活动/无关answer新增不误变成这条观察的后继。接口apply_teaching_local/_write_teaching_outcome、资格函数。新增PG，不能靠比较全head revision代替针对关联的检查。

V08 上游派生记忆。选择M1形成活动A后保存其成果为M2，撤销/修订M1，M2及选M2的B失效；闭包不得遗漏M1来源/event。伪造自引用/循环/33依赖/未选上游拒，缺闭包不能降为自报。新增PG与有限纯投影例，合成数据，不测试真实个人记忆。

V09 单SQL读快照。并发修订/来源切换与memory list/detail/selection/teaching workspace/history/operation读，允许前或后完整状态，禁止正文旧、资格新或不同区域混拼。对实际SQL数量/CASE投影留原件；新增PG并发与HTTP，不用多次SELECT的事务名称证明一致。

V10 同键、响应丢失和不同键。save/revise/revoke同键同规范请求只有一个效果，同键异内容409；相同槽不同键同内容duplicate，异内容冲突。故意丢COMMIT后响应再GET，只读核出实际key/hash，零模型/工具/额外清理。新增PG/HTTP和浏览器意图，用真实行数/版本/函数调用数观察。

V11 CAS竞争。两标签同revision编辑不同内容，或revise与revoke竞争，一个COMMIT另一个409保留草稿；不能以新业务键重置期望版本。新增PG和真实两标签浏览器，原G8的两标签编辑证据仅继承旧流程，不冒新记忆验证。

V12 伪身份与最小权限。非法memory/版本/hash、跨活动record、错误claim_kind、伪来源、额外trusted/tool/SQL/path/delete_originals字段、无会话/跨站全拒并零写。当前单人没有虚构跨租户，但仍核activity/record绑定。真实app role直接UPDATE不可变表、DELETE/TRUNCATE正文或教学事实、SET ROLE purger、禁trigger/替换函数均拒；合法精确清理可成功。新增真正不同PG角色与HTTP，不能以superuser夹具成功称权限有效。

V13 未claim恢复与已claim未知。accept后未claim、固定recipe全有效的同键显式恢复最多一launch/SUP；版本已变则不启动。claim后无operation不证明未启动；GET/刷新不补发，UNKNOWN不退款/占槽保持。新增定向PG/受控HTTP，继承原G8恢复窗口纪律。

V14 在途晚到。分别在accept→launch、admit→mark、mark→result插入撤销/来源切换。前两处拒下一资格；已mark不能承诺远端撤回；未提交正文记忆失效时只UNKNOWN诊断，007/教学fact/progress新写0。相同已终态重放只确认不再生效。新增PG和一个受控监督组合，停树主体未改不全重跑D3/G8。

V15 刷新、重开、两标签及切活动。浏览器记录实际GET/POST、模型/清理计数；刷新/轮询/翻页/打开草稿无POST。复制标签owner不同，迟到回执/读不改当前editor。source新版本、memory新revision、activity切换都清旧引用。新增最终bundle的定向浏览器；只读快照回放不能证明新认证或写入。

V16 原事实不可变与旧结果旁路。尝试写/删009事实继续拒；原answer/goal可历史读，失效模型文本通过workspace、record、command、007结果、list_operations、G7seed、lc_引用均不得返回。answer_reference只能返回原用户答案且无当前掌握资格。新增PG/HTTP负面，原不可变trigger证明继承。

V17 派生重建与撤销复活。清空本活动可重建head.projection再按产品恢复流程读取/重建，在M1 revoked、旧body存在或M3已purged三种状态都不恢复节点/记忆摘要；不从teaching_records/007自动建M1，不用source旧版回填。新增PG重建专项，是原“全面重建未动态验证”的新受影响缺口，不声称旧证据已覆盖。

V18 精确清理正常。实际manifest只列本ID的全部版本/hash/bytes，函数删M3精确行且M2/M4/M5/M6/M7墓碑、001—009、另记忆、原件目录不变；同清单/丢响应再核仅一次有效删除。新真实PG，文件hash/目录元数据只能辅助证明未碰原件，不用“无API调用”代实际DB结果。

V19 清理异常/攻击。错manifest/hash、额外版本、缺正文、body篡改、临时同名对象、PUBLIC执行、普通app直删或自定义GUC伪授权全部拒。中途故障整体回滚M3，M1保持revoked/pending；数据库不可读保留未确认不做新清单。新真实PG最小角色与故障事务；清理会话没有009/007/material权限，正常用户原始事实不作为故障样本。

V20 迁移新/非空/坏基线与回滚。已登记合成空基线、含G7/G8/UNKNOWN非空副本均新增010且旧行零变；篡改同名CHECK、007类型不符、缺009trigger、新表/角色残迹或缺sha256支持，整体失败回滚。成功空010的反向迁移按精确清单；有新事实时只验证维护模式/向前修复，不DROP个人记录。新真实PG，旧001—009迁移正确性证据继承，不再跑其原全名单。

V21 默认关闭和降级。缺memory_context、缺角色/schema、估算/模型identity不匹配，memory_model拒且原无选择G8仍走v1；已选择活动不能回G7或普通continue绕过。关闭新消费后旧选用失效读面仍生效。新HTTP/少量浏览器，旧预算计数继承。

V22 内容支持与位置。冻结平均速度资料加“我仍容易把分钟当秒”的自报、有限progress记忆；新题/反馈的lc_引用逐一核正确版本/位置，并人工核结论支持，记忆不提供额外来源引用。加入同名概念、来源冲突、否定/unknown、模型故意all-met负例；旧答案不计本活动独立观察。新增有限合成内容核查和原件，以引用位置正确代替语义支持必须判失败。无真实provider泛化质量结论。

V23 备份恢复门。对合成旧active副本给当前revocation墓碑输入，未合并前memory关闭/只读隔离；缺墓碑不能打开选择。这里只核本版fail-closed识别和恢复前置，不实现/验收STEP-017完整备份器，独立解读/原件删除仍在后续验收。

V24 兼容。v1旧profile/frozen/receipt/UNKNOWN/旧创建请求的规范字节与接口语义不变，新增字段不改变旧hash；M6不存在不会变记忆活动，旧工具结果仍不能当模型父输入。新增少量最终字节离线/PG/HTTP回归；其他G3—G8已充分证明按hash/实际未变范围继承。

### D2 一张完整实施卡的顺序与有界批次建议

先由编排核本合同和G9-P，获得必要一次批准后再登记一张完整G9实施卡，明确合成库/角色/端口/进程/计时/工具次数与收尾许可。本结果不是运行授权，不先派审计依赖卡。

实施顺序为010结构/最小权限和纯DTO→记忆保存/修订/撤销/精确清理→活动固定选择及资格锁前缀→v2 recipe/profile/消息与提交守卫→全部只读/引用/恢复/重建读面→实际记忆工作区和意图恢复→受影响定向验证及卡内普通修复。权限/清单边界在后续依赖和不可逆真实用户操作前验证，先用合成数据；稳定完整G9之后集中一次独立增强审计权限、来源、删除、晚到与恢复。

建议未来资源上限为主动21600秒、标准元数据600秒；离线至多3批每批180秒，PG至多3批每批600秒，HTTP定向至多2批每批300秒，浏览器最终bundle至多2批每批600秒，受控监督组合至多2次/各按既有窗口上限；实际资源由下一卡给精确实例和总额，不按这份建议自行使用。独立审计单独隔离会话和资源，普通模块不逐个加审计门。

同性质用例一次集中验证，只因修改、失败或具体证据缺口补相关例，不重新全G8；PG事务/权限不能用mock替代，实际HTTP/浏览器写入不能用只读快照替代。未改监督主体不默认重跑全部Windows停树；确有新权限传播失败或主体改动才交编排扩大相应范围。真实provider/付费、用户数据、原件删除和部署没有默认额度。

关键停止条件是源码漂移归属不明、必须改001—009/停止/预算主权、无法保持来源→活动相对锁序、闭包/正文清理不能收敛、实际app拥有超权限且不能隔离、v1字节无法兼容、需要真实用户迁移/备份或新依赖/provider能力、两次有据修正同问题仍失败、根因不稳或预算触顶。保存完整已成部分、旧失败与精确缺口，由编排重评，不换窗口/模型清零。

### D3 唯一合并批准包 G9-P

建议编排向用户一次提交并推荐采用以下完整包，而非逐表/逐字段索要决定。

- 新增B1七表及010合成新库/非空副本迁移准备，保持001—009不可变事实与旧数据零回填。
- 批准记忆类型、追加修订/CAS/墓碑、固定新活动选择，以及活动级保守失效。旧选择不会自动取新版；选择活动通过教学工作区使用背景，旧G7/普通continue/通用tool拒绝绕行。
- 批准新的受保护API及v2受信recipe/profile/binding、所有admit/mark/提交/读面/引用/重建的资格接线，v1旧规范字节兼容；原预算、G/R/S、UNKNOWN和停树主体继承。
- 批准独立正文分表和唯一精确清理函数/NOLOGIN最小角色设计，只在后续明确合成实施范围创建/授予角色、执行010及验证。产品用户确认撤销动作仅授权其本条记忆正文清理，不赋app普通DELETE、不关009trigger。
- 批准实际工作区、有限配置/草稿/意图协议和D1受影响合成验收范围，稳定完整G9保留一次独立增强审计。具体资源/安全收尾仍须在下一实施卡登记。

价值是用户能看见并控制长期记忆，撤销可以同时抵达生成、旧结果和恢复，而不改写原作答。代价是七张职责分开的小表、一个受控清理函数、教学v2 recipe及活动级失效造成的保守重新选择；无向量/微服务/新runner/新依赖。只有UI/localStorage的替代缺持久身份与删除一致性，直接改009或赋app全库DELETE的替代违反既有不可变和授权边界，故不推荐。

包外明确为用户库迁移/真实role重配、用户真实删除、007/教学事实/材料/PDF/原件/WAL/备份物理清理、真实provider/密钥/付费、面试/HTML、完整向量工程、部署、Git写入、联网新权限和全仓安装。本文中的角色和函数是待实现方案，不是本卡已获实施许可或已批准包。

最少决定只有采用或不采用G9-P这个整体方案。编排可以凭现有有效授权判断谁需要作该批准，不把任务下发当包生效。本卡不向用户预先索取空泛许可。若不采用，保留已有G8与本合同，G9相关实施不开始，不能悄悄降低记忆Must；无关后续规划不受阻。

### D4 DEF-019 最小合并建议

DEF-019/P2仍为既有64有效位比较的B级观察，不重开G8、不阻塞G9。将来相关完整实施若获范围，可在 teaching_policy 的同单位比较保留原Decimal，跨单位使用可证明的精确比例/足够精度或超过支持域unknown。仅增加同单位1与1+10^-65、合法跨单位60m/min与1m/s及超支持域的定向离线边界例，落已有真实policy测试体系，不能新增微修卡或默认PG/浏览器门。

本卡没有写、导入或运行数值代码。原18方法/81子测试的修复04证据及review-03限界原样继承，不把建议例写成新PASS。

## 实际检查、计量、风险与编排回传

本卡只做一次最终文档/字段/调用一致性检查，检查A—D、七表字段/约束/角色、接口与真实函数映射、锁序、v1兼容、清理范围、四条推演和权限门。原件见 consistency-check.json。保存确认不是DDL或行为通过，尚未实际验证PG锁/权限/非空迁移、v2重建字节、HTTP写入、两标签、新清理失败和模型输入容量。

一次检查的16项文字/身份核对中，首次七表计数表达式仅匹配learning_memory_，漏了实际M1名称learning_memories，得到该项false；实际正文仍为七表。仅对此元数据表达式按七个确切名字纠正，首次结果与补正原因原样保留在consistency-check.json，不重跑产品或其余检查。有效文档项16/16，59项读入结束零漂移；26项初始函数定位均存在。计量、三次路径错误及这次检查辅助错误单列，业务/测试/DDL运行0。最终文档hash在该证据的final_document_binding及交付计量中绑定，不能以首次检查前的旧hash签本次封装段落。

三次只读检索包含不存在的候选路径，分别为 test_teaching_pg.py，worker/one_call_session.py及protocol.py，worker/one_call_input.py。实际目录定位后使用 test_teaching_repository.py/recovery.py/api.py 和 worker/one_call.py，无产品运行或写入。它们是元数据路径错误，不删除、不计为业务测试失败。部分合并读取输出被工具截断，必要正文按真实小范围补读；截断未当完整证据。无命中的可选检索不等于产品失败。

设计风险集中于活动级保守失效的用户代价、原观察后继识别、上游闭包、DB最小角色的真实基线、v2 recipe的可重复重建和在线删除之外的保留副本。均有具体未来A级用例和停止条件；当前源码与需求没有被反向降级。四个官方页面采用PG16文档的稳定语义，不声明本机运行的是PG16，也未证明环境支持。

编排待同步项目正式 DocuS 的G9合同/采用包、唯一执行动态的真实转交/返回与TASK/R/预算、架构的记忆选择/删除/权限边界及所需CHG。共享编号、采用状态与未来实施卡由编排串行维护，本执行者没有占新号或写这些文档。原TASK100修复04、TASK101 review-03和更早历史FAIL/投入/未知留在原记录，不借出余额。

没有由本卡只读推演产生的合格已验证经验入库候选。可复用候选仅为“撤销资格必须跨持久上下文与全部读面”“不可变身份与可清理正文分开”，尚未动态验证，不写经验库或用户记忆。

当前必要人工仅为把本结果绝对路径带回编排。建议编排核证完整合同和G9-P，按实际授权一次处理包，再下发一张完整实现卡，稳定后独立审计。本卡达到文档交付终点即停止。

## 唯一附录  四条手工推演与数据库查证

下面全是必要手工推演，不是程序、SQL、HTTP或产品运行，数字是示意版本。

H1 正常保存、修正与选用

1. 活动A的progress事实P有真实答/题/反馈、有效S1版本，用户明确保存，得到M revision1/version1/limited。
2. 用户在新活动B选择M1，创建同时冻结S1和M1，B的plan经v2 recipe/资格/限额后最多一次模型，旧A作答不计B独立观察。
3. 用户修正M注记，得到revision2/version2，P原字节不变。B仍指version1，因此资格失效而不是取新版。
4. 用户新建C明确选M2，可再作为背景；新的模型动作仍计C原预算，不从B复制计数。

H2 来源/记忆撤销与晚到

1. B已accept旧选择的evaluate，但尚未mark；S1成功替换或M撤销COMMIT。
2. 下一launch/admit/mark拒旧资格，用户答文留历史；若mark已先COMMIT，远端可能继续，不能承诺撤回。
3. 旧成功结果在撤销后才提交，记忆资格失效，007/feedback/progress新写拒绝，原凭证只记UNKNOWN脱敏诊断，预留不退款。
4. 旧已提交结果重复到达只确认原终态，不产生第二效果；workspace/007/引用所有新读抑制其正文。

H3 同键或CAS竞争

1. 两个请求同memory_id、key/hash都相等并发save，主键/槽只允许一个COMMIT，失败方确定回滚后读同一收据。
2. 响应丢失后GET核相同ID/key/hash，不自动POST；同键异文字409，无新版本。
3. 两标签从revision1发不同revise，或一方revoke另一方revise，只有一个修订槽获胜；另一方旧文字留在不同owner草稿，不改绑revision2。
4. 新键不清CAS，用户重新核对影响后才可提交新的明确动作。

H4 恢复、重建与精确清理失败

1. M撤销第一阶段已COMMIT，manifest列version1/2各自PK/hash/bytes，头revoked/pending；进程在第二阶段之前退出。
2. 重开只GET显示待清理；旧M3还在也不返回，head/progress重建不能用旧007重新造可用M。
3. 用户明确重试清理。事务删完第一行后第二行hash不符，函数抛错整笔回滚，两行均保留，头仍revoked/pending、原manifest不变。
4. 问题在许可范围内修正后使用原清单显式重试，合法完成只删M3、保留无正文墓碑；提交响应丢失只核收据，不开新清单。合成旧备份若缺当前墓碑则隔离且memory关闭，不能复活旧active。

官方查证日期为2026-10-06 +08:00，共4页，均只读公开PostgreSQL16手册；没有确定本机数据库版本。

- CREATE FUNCTION 安全段。短原文为 “execute privilege is granted to PUBLIC”。采用明确拥有者、可信search_path、pg_temp末位、同事务撤PUBLIC执行与精确grant。[官方页面](https://www.postgresql.org/docs/16/sql-createfunction.html)。
- Explicit Locking。短原文为 “consistent order”。采用所有新增前缀顺序一致，不在锁后补取上游对象；不借此声明已实测无死锁。[官方页面](https://www.postgresql.org/docs/16/explicit-locking.html)。
- Transaction Isolation。短原文为 “two successive SELECT commands can see different data”。采用单SQL读面及锁后复核，而非几次读冒充同快照。[官方页面](https://www.postgresql.org/docs/16/transaction-iso.html)。
- Binary String Functions。短原文为 “sha256 ( bytea ) → bytea”。采用核心SHA-256及UTF-8转换核精确目标，不引pgcrypto；实际支持待下一合成PG验证。[官方页面](https://www.postgresql.org/docs/16/functions-binarystring.html)。
