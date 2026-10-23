# TASK-121 / R-115 集中独立终审结果

TASK-120 当前有限工程切片不具备交主控关闭条件；代码轴不通过，证据轴证据不足，执行控制轴不通过，四项 P1 和一项 P2 合并交原 TASK-120 工程窗口处理，Q 继续冻结。

本报告是 TASK-121 的独立审计建议，不代填主控验收。P1 为 F01 迁移前提漏验权限、F02 严格 ACL 未核实际成员能力、F03 Q 正文副本未接入删除清理、F04 批准期限可随 UTC 回退恢复；P2 为 F05 PG 已领取但尚无 Q claim 时批准投影及续批仍可能开放。F01—F05 是本报告内部定位号，不占用共享 DEF、TASK、R 或 CHG 编号。

现有 ACK、真实 PG 共同 100 门、列明正常业务及 UI、K2 窗口、严格包读取和最终停止的有效子事实保留。没有要求重新刷 99 笔、重跑五入口、真实供应商或整套业务验证。以下确定缺陷来自合同与当前实现的静态可达路径；本审计没有运行它们的动态复现，也没有将静态判断写成真实事故。

## 1. 独立性、规则和授权

本窗为用户人工转入 TASK-121 的 Codex desktop 审计聊天，与 TASK-120 工程聊天分离；未继承工程聊天、思考或完整自评，没有派发子 Agent、创建并行审计或接管工程实现。系统声明的模型家族为 GPT-6，精确后台型号或变体未暴露；A+ 仅登记为资源路由，不声称来自另一个模型家族，也不声称延续了原 TASK-118 的物理执行上下文。

实际读取项目根 AGENTS.md、锁定公共 AGENTS.MD、WORK.MD 适用内容、07 提示词及完整 TASK-121；七项文件与 rules-snapshot.json 的指纹均匹配，未自动采用新版。00、05、06 和任务模板仅核锁定身份，没有将它们冒称为本轮已全文加载。合同身份为 task_model、V4.0、公共 AGENTS CHG-0003、阶段 07，卡面需求 v1.4、架构 v1.54、执行动态 v2.82。本审计不承担共享状态维护，未解码执行动态中主控收到候选的评价段。

读取顺序为规则与审计合同、封存身份、TASK-120 原合同和前向采用合同、TASK-119 有效设计及 K1/K2、真实差异和实现、方法及原始记录。TASK-118 只读取四项关闭、有限 S、历史控制与 Q 边界的适用段，不重做未变七族。

TASK-120-result.md 只作为 opaque bytes 核对，91351 字节，SHA256 为 3d044a788f7354e9a3b1fec0f75bab100f182469dea42613d3112078cda67b03。未解码该报告、其 ZIP 条目、TASK-120-work-decision.md 或对应备份正文。允许读取的 acceptance-matrix、scope-index、budget 和 checkpoint 中确有工程 PASS、自评字段，本轮只用作导航，未据此预填结论。

宿主提供了通用规划偏好摘要，首批工具还检索过 MEMORY.md 的规划验证边界；没有接触 TASK-117/120 的实现记忆或工程推理。该偏好未用于降低本卡安全、证据或独审门槛。没有隐瞒这次通用记忆接触，也不声称完全未接触任何宿主记忆。

产品、测试、dist、工程原证据、工程账、任务卡、公共库、DocuS 均未修改。未读 .runtime、真实配置、凭据或 vault；compile、unittest、产品/测试导入、PG、Docker、API、Job、浏览器、build、模型、业务网络和 Git 写入均为 0。仅执行自己的标准库文件 hash、ZIP 条目、差异和已保存记录对照。官方资料查询限于两页 PostgreSQL 17 文档，适用版本由实际 fixture 的 pg_major=17 确认。

## 2. 对象、差异和可复核证据

审计起点和收尾的身份核对分别见 [identity-check-opening.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/identity-check-opening.json) 与 [identity-check-closing.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/identity-check-closing.json)。322 项核对包含重复引用，不是 322 个不同对象；209 项冻结清单、55 项净变化的额外实际产品路径、六段 diff、两份 as-run、规则、dist、工程账及附件均无非预期漂移。两个旧 JS 的期望摘要就是 null，实际不存在，按预期缺席处理。

初始 product-baseline 有 616 项，复算其中 47 项发生变化，45 项属于列明产品净变化，另两项为旧 dist JS 移除及 index.html 更新；没有发现该清单内未纳入范围的额外产品差异。55 项中，45 项取得与初始 hash 精确相符的 preimage；必要时使用后轮实际保存且摘要等于初始摘要的原件，没有拿不相等的后版补初始基线。其余 10 项初始清单未列且无初始原件，已审当前完整内容，但不凭 null 声称独立证明了新建。

完整文件列表、preimage 来源和逐文件净差异见 [net-diff-index.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/net-diff-index.json) 及 [baseline-closure.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/baseline-closure.json)。实际覆盖包括全部 Q 新模块、业务 accept/claim/GET/请求组装的净差异、网关和最低 transport、原费用事务调用、新权限/profile/备份恢复直接依赖、全部前端净变化及配置说明。测试和 runner 按真实证明方法定向读取，不宣称全部 38 份 fixture 都全文审过。

.gitignore 除本卡精确私有目录外，还包含独立 GitHub 同步形成的排除规则；其 2026-10-18 明确公开同步授权保存在 DocuN/evidence/github-sync-20261018/explicit-publication-authorization.json。没有把该独立工作区变化算成 TASK-120 已执行 Git 写，也没有回滚它。

候选 ZIP 为 1936840 字节、286 条目，SHA256 为 3e96aeee40b35e0e0e1a4d42e82452b3cc2a0286fe1ce3ae4bf24219211bed69，目录和逐条目身份见 [candidate-zip-members.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/candidate-zip-members.json)。条目只读原始字节取摘要，未解码工程报告。没有重建或递归打包旧七 ZIP，最新 budget/events 和 071 回执按包外附件审查。

最终 015 的 SHA256 为 59b2e556a81a5383e9144a967fa90b5abedb26284d50cbf150db1dd77f34ef0e；正式 JS 为 frontend/dist/assets/index-GSKO5ska.js，SHA256 为 50b035784109bb04b444ffedf48186d14b9042a6139f8b22df59814d6a81b285。四资产以冻结清单核对，实际 JS/CSS 响应摘要另从浏览器原记录复算匹配，不用磁盘声明代替真实加载。

根 46 与最终产品仅 repository.py 存在差异，为 data_readonly 且既有纯读方法时延后 normal QAuthority 构造。normal 源分支、写/claim/出站分支未获此例外，仍进入原 GuardedAsyncConnection；方法分类来自服务器闭包的 qualname，客户端不能指定。写 SQL 仍拒绝，未把“列表有三项”单独当成写权安全证明。根 50 API 及根 51 只读 UI 对该增量提供补证，根 51 的 202 项 as-run 与最终一致。

根 46 后变更过的三份 Python fixture 已在审计目录中按当时 hash 精确重建，见 [verification.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/as-run-reconstruction/verification.json)。变化为后加的 old_compatibility/只读列表与 UI 方法、重启既有恢复目标 helper、对应阶段白名单；UI 正常响应捕获和 authenticated capabilities barrier 的方法没有随之改变。真正运行的前端 continuation06 UI fixture 的自身摘要也与当前文件一致。重建仅做字节对照，没有执行这些源文件。

额外原件身份见 [reviewed-raw-evidence-identities.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/reviewed-raw-evidence-identities.json)，PG/预算、UI 和停止的独立记录对照分别保存于本审计目录。

## 3. 合并发现

### F01 / P1 015 把三个必需权限写成了任一权限即可

位置为 [015_activity_scope_delete_permission.sql 第17行](D:/shspic/project_NO3_RetroLume-agent/backend/migrations/015_activity_scope_delete_permission.sql:17)，关联续作06合同 A 的精确旧 R02 前提与失败全事务回滚。

has_table_privilege 的逗号列表按“任一权限成立”返回 true。因此当前 NOT has_table_privilege(...,'SELECT,INSERT,UPDATE') 只有三项全无时才拒绝。具体触发为预期旧 R02 的 app 仍有 SELECT/UPDATE，但 INSERT 已被撤销，其他已列前提满足；第17行不会拒绝，随后 GRANT、profile 约束和 metadata 可 COMMIT。只剩 SELECT 的前提也一样。后续严格 profile 可能拒绝这个少权库，不能把迁移已经提交后的拒绝冒称迁移前精确拒绝及原子回滚。[PostgreSQL 17 权限查询语义](https://www.postgresql.org/docs/17/functions-info.html#FUNCTIONS-INFO-ACCESS-TABLE)

最小修正为逐项核三项必需权限，要求全部成立，并保留正确的额外权限拒绝。第18—20行用于发现任一 DELETE/TRUNCATE 的逗号形式本身是正确的，不能一律替换。补证只需在获准隔离 R02 对象中分别缺 INSERT、缺 UPDATE、仅剩 SELECT，核目标错误及 ACL/profile/metadata 无提交变化。当前 profile_checks 的 missing-delete 是迁移后的 R03 检查，不覆盖这三种迁移前提。

### F02 / P1 精确 ACL 只看直接授权，未拒绝实际继承或 SET ROLE 能力

位置为 [schema_profiles.py 第114行](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/schema_profiles.py:114) 的 SCOPE_ACL_QUERY、check_scope_permissions，以及 [schema_checks.py 第9行](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/schema_checks.py:9) 的 ROLE_QUERY。关联续作06“snapshot/readonly/restore-loader 不获正常 DELETE/TRUNCATE/管理权”和本卡“实际成员能力”要求。

查询只展开 activity_scope_sources 的表/列 ACL，把直接 grantee 归类；ROLE_QUERY 只核角色本身的布尔属性。两者均不读取成员关系或验证正常登录角色的有效/可切换权限。具体触发为 snapshot 或 restore-loader 通过直接或间接成员关系继承 retrolume_data_app，或某实际只读登录角色另有通往 app 的 INHERIT/SET 链。表/列 ACL、grantor、grant option 和当前四角色属性可以完全不变，精确检查仍通过；015 新授的 app DELETE 会传给这条成员链。normal 模式的原 data_runtime_write_guard 对 DELETE 返回 OLD，不负责区分调用者的用途，不能代替这项权限分离。[PostgreSQL 17 角色成员、INHERIT 与 SET](https://www.postgresql.org/docs/17/role-membership.html)

这是有明确配置触发的确定校验缺陷，不声称已保存的实际测试库发生过该成员配置，也不把管理员恶意改库当普通客户端攻击。合同明确要求此类不合格权限失败关闭；现有直接多权/少权正反例没有覆盖它。sealed reader 独立装配对 current_user 的有效写权探针是局部保护，不能证明正常 snapshot/loader、全部成员链和 SET 能力都受同一检查。

最小修正为在真实 profile/ACL 投影前核受信角色和相关实际登录主体的有效能力及可切换的危险角色链，拒绝 snapshot/readonly/loader 获得 normal DELETE、TRUNCATE 或管理能力。补证使用事务内成员关系反例，核真实 has_table_privilege/角色可达性与精确拒绝，结束回滚。无需新增 RLS、SECURITY DEFINER 平台或行级授权设计；获批的表级 DELETE 及仓储 CAS 模型不推翻。

### F03 / P1 Q artifact 正文没有进入源删除和记忆清理链

位置为 [q_store.py 第246行](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/q_store.py:246) 的完整 request/payload/provenance/intent 落盘、[deletions.py 第118行](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/deletions.py:118) 的源文件清理，以及 [memory/service.py 第22行](D:/shspic/project_NO3_RetroLume-agent/backend/app/memory/service.py:22) 和 memory/repository.py 的原 purge 路线。原采用设计 TASK-119 B6、D1 第2项明确要求 q 副本同步抑制并清理。

具体触发为准备过含源片段或已选 memory 正文的请求，随后正常删除对应资料或 revoke+purge 记忆。新 q-prepared 私有文件保存完整正文；源清理只处理 originals 的 hash/size targets，记忆 purge 只处理原 SQL 清单，tombstone observer 只登记观察，没有任何 Q artifact 清理入口。搜索全部 Q artifact 引用及原清理调用链未发现注册或调用。q.closed 的现有写入只用于 admission 的关闭诊断，也不删除正文副本。

inspect_request 的当前资格拒绝确实成立，原 root35 的 body_rows=0 和删除后 operator 拒绝也有效；它们只能证明业务正文及受控读取被抑制，不能证明新增加的私有明文副本已清除。源/记忆清理结束后该副本仍按代码留在控制根，缺少原合同承诺的清理及清理不确认时的 Q 关闭。此处没有读取 .runtime 文件或现场提取被删正文，不宣称发生了 HTTP 外泄。

最小修正为将受影响 prepared 正文副本纳入原删除/revoke+purge 的精确清单与确认过程，保留不可授权的摘要、事件和原费用，清理失败或未确认时关闭相关 Q 执行及正文读取。补证只在新的获准合成对象中做一次源清理、一次 memory purge 和一次清理失败；核准确副本已处理、哈希历史/007/预留保留、零重发。不得删除本次冻结工程原件或用批量清理擦除旧证据。

### F04 / P1 批准有效期只读 UTC，过期批准可因时钟回退重新可用

位置为 [q_store.py 第262行](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/q_store.py:262) 的 projection、approve、check_reference，以及 [q_protocol.py 第219行](D:/shspic/project_NO3_RetroLume-agent/backend/app/capabilities/q_protocol.py:219) 的 utcnow。关联 TASK-119 B5 第7项及本卡单调/日历有效期要求。

签发和消费只比较 datetime 的当前 UTC 与 expires_at，没有保存或检查可解释的批准时钟域、单调期限、已见 UTC 下界或失效不可逆事实。具体触发为活动及 grant 仍有充分余时，一个未领取批准签发后实际已过16分钟，UTC随后回退2分钟；prepared 的冻结 PG 快照未变，projection 会重新给 approved，reference/check_reference 的 expires_at 比较也允许继续。新创建的90秒执行窗口和 worker stop_ns 只限制该次运行，不约束这份已存批准的15分钟历史。原 grant.check 同样只比较当前 UTC，不能补足此门。

原 test_expiration_currentness_and_claim_never_enable_resend 测了单方向过期、重新批准及 Q claim 后拒绝；没有“先过期或已见较晚时间，再回退”的反例。本次静态缺陷与实际当前已冻结/已停止状态分开，不声称本机发生过回退或已有过期请求实际发送。

最小修正为在原授权路径实现可解释的单调/UTC 联合时限，时钟回退、域不明或重开无法解释时拒新外发；不能仅增加 now>=issued_at，因为回退后的时间仍可能晚于 issued_at。只补批准的前进过期、回退、重开域不明、当前合法继续及已 claim 零重发定向检查，不调整系统时钟，不借此扩大真实 Q readiness 或计价调研。

### F05 / P2 PG 已领取但无 worker Q claim 时，operator 仍可给出可继续或续批

位置为 [q_context.py 第134行](D:/shspic/project_NO3_RetroLume-agent/backend/app/capabilities/q_context.py:134) 的命令快照、[q_store.py 第265行](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/q_store.py:265) 的投影及续批条件，关联 K1 和原 launch claim 丢确认合同。

真实 ACK-launch-claim 原件已展示 command=started、launch_claimed=true、007=null。对应 Q worker 尚未启动时 q.claim 和私有 q.launch_claim 都可不存在。snapshot 虽读取 accepted/started 命令，但不把其领取事实用于投影/续批核定；QAuthority.projection/approve 只看 Q 行的 claim/launch_claimed/closed。因此在 head/scope 等未变时可继续显示 approved/can_continue，或在原批准到期后给这个已经 PG 领取的请求签新批准，违反“确未领取才能续批”的要求。

没有发现该路径会绕过业务 status/claim 检查造成第二次出站。interview/teaching 服务及仓储仍拒绝再次 launch，这正是 P2 而非已证重复收费的原因。现有三路径 ACK 的零重发事实保留。

最小修正为在投影及 operator 续批中单独核原 PG 已领取/终态，已领取只读并拒新批准；保留合法 worker 领取后的发送路径，不把可变 launch 状态粗暴加入整个冻结快照全等比较。补一个“PG claim 已 COMMIT、Q claim 未记”的投影与到期续批拒绝检查即可。

## 4. C01—C15 对照与继承

以下“通过”只覆盖写明的检查事实和快照，不覆盖 F01—F05，也不表示当前完整工程切片通过。

1. C01，三类 COMMIT 丢确认的持久事实与只读恢复通过。finalization-05 的 ACK-accepted-COMMIT、ACK-launch-claim-COMMIT、ACK-result-COMMIT 三份 checkpoint 对应不同注入边界。方法先 await 原真实事务返回再抛 ACK 异常。前两例均7次/1750000不变，分别 accepted/unclaimed 与 started/claimed，007 为空；结果例只增一笔至8/2000000，007 received 摘要一致，恰一次 transport，两次 GET 不增动作。F05 为这些事实之外的批准投影缺陷。

2. C02，列明11项全请求反例通过，整个批准有效性门仍受 F04 阻断。final05.permissions 的 actual PG snapshot/provenance 拒绝 answer、goal、memory、title、history，准确字段路径均落在被改文字处；foreign parent 为 q_parent_unqualified，不同现有实例为 q_instance_mismatch，字节/endpoint 为 q_prepared_changed，missing artifact 为 FileNotFoundError.2，重复批准保持同决定和 event_seq。前后金融相同、claim/admission为空，不把任意403/409/503充数。模型 schema 的合法性与真实全文来源证明分开评价。

3. C03，wire 兼容的列明路径通过。OneCallInput 原v3省略新增空字段，原v4仍沿原分支；新v4授权引用不进入 provider payload。现有 test_wire3_original_bytes_have_no_new_default_fields、test_wire4_carries_private_authorization_without_provider_message_change、v1/v2额度分支与旧S08原件按其原层级继承，实际模型/embedding请求组装和最终 send_frozen 使用同一已核 bytes 的代码链已审。本审计未重新运行兼容单测。

4. C04，不通过。副本根的 q_instance_identity、残尾 control_tail_unconfirmed、missing artifact、source/memory 资格变化和 readonly 根拒绝的原记录成立；ControlHub 每次在真锁内重新读完整当前字节与文件身份，新 Q cache 仍经 assert_writable/check_root，不绕过原S控制核验。但 F02 的实际成员能力和 F03 的副本清理未满足，不能扩大成完整权限及删除合同通过。

5. C05，获批工程范围的冻结/零真实外发通过。惰性示例保持关闭，returned_models 未核不放行，TESTONLY 根与最低 transport 的 is_external=false 分支分开；真实 provider、费用、preview、Git 在本工程记录均为0。此结论不提供正式账户或外部计价 readiness。

6. C06，精确合成资源和采用范围通过。一个原CID/卷内新增批准源逻辑库，一份生产工厂创建的隔离恢复目标；preflight、create前计数、实际CID返回登记、镜像/limits/mount/ports/labels的代码与原件对应。未要求新目标伪装旧源label，未迁移旧四库。015 的权限正确性另按 F01/F02 判不通过。

7. C07，零重发/原UNKNOWN/原预留保留的事实通过；批准投影与续批的完整合同未通过，见F05。最新见证保留原三个键的事件子序列，新源三个批准未领取意图没有变成新执行权；源frozen、selector选只读目标后未重绑grant。不能把没有Q claim等同PG尚未领取。

8. C08，列明真实检索及 query→model 接线通过。两域的生产 retrieval freeze/claim、实际 embedding、received/ref、模型等待及原键继续原件可继承；缓存限原source/version/revision/space和合格当前结果。未用未批准新文字或跨活动父替代完整请求。严格权限和时间缺陷不因检索正例通过而消失。

9. C09，原教学练习和记忆显示的有限事实通过。validation-04/original-exercise-positive.json 的原accepted/unclaimed练习 cd632dfd-8a25-465b-895e-375b0ce1d48e 在根21提交；根24及 memory-display-PG 对无记忆 teaching.v3 与仍有选择的 budget02 分开核证。最终只改变读取显示，不宣称删除后记忆仍可作模型父，亦不宣称真实供应商语义已验证。

10. C10，五入口有限正常UI可继承。根23原文件为PARTIAL，保留面试query/model、legacy followup、HTML的三个已保存子例；根24补教学query/model，检索入口由其中实际RetrievalPanel交互覆盖。owner/view晚到及重开仅GET、同键显式继续按各自case和方法接受，没有把根23/24整根FAIL改绿。旧bundle仅证明当时路径；最终context.tsx普通响应门加严由根46的新正式bundle补证，不把旧bundle直接冒称最终全UI。

11. C11，K2并发一致性的列明范围通过。真实transport返回后释放shared，独立actor提交head/revoke/source/scope新增/memory，再由结果事务重取exclusive；原007及预扣保留，迟到不推进改变后的head。新scope收缩的before为scope4/head5、actor COMMIT后scope5/head6，007当时dispatched，最终received且实际摘要等于2ef25ef0b1e2dbc8f97def352e77736bc91b02a22f533f08a6344e6d1c0a4e82，head保持6，费用仅从3/750000到4/1000000。新scope只删差集，CAS/来源锁/版本upsert与其他活动不变的原件成立。

12. C12，真实PG共同99→100门通过。budget.py 经真实生产admission累积99笔，roster为47/28/24、24750000；实际两个等待advisory的backend为3923和3925。同一A1有效lease、不同合法model/embedding请求竞争，最终100/25000000，model rejected、embedding unknown，新operation与一次合成transport对应，输方不出站；达限后两provider准确拒outbound_grant_exhausted，同库重开保留100/25000000。最终015/R03和readonly读取分支未改变该金融SQL及正常源admit/mark调用关系，无需重刷99笔。对照见 budget-evidence-comparison.json。

13. C13，列明最终UI与只读恢复列表通过。两份真实normal GET200的headers/body/can_continue已捕获，批准未领取；同namespace下真实freeze改变mode/read_only后才释放第一份，真实verified目标及selector/rebind完成后才释放第二份。原生fetch确已fulfilled，业务JSON未被消费，前后页面/输入/存储相同且无自动POST，区别于传输取消。authenticated capabilities请求在生产local_session检查后、构造body前被屏障暂停，原请求header跨过提交后获得新生产body；后续session bootstrap和新namespace存储读取一致，没有setter/body/token注入。根50/51封闭最终pure-read增量，不能替代根46的两条异步证明。对照见 ui-evidence-comparison.json。

14. C14，规定历史时点的精确停止证据通过。070于2026-10-20 23:08:53.727173+08:00记录622组PID/birth、135个Job、两精确CID Running=false/Pid0和55480/55481/18120无监听；原070、071均exit0/tree_empty，071为文件保存。已保存事件序列未显示070后业务再起。没有运行Docker、进程或端口探针验证现在状态。对照见 stop-record-comparison.json。

15. C15，不通过。候选身份、范围和原始子事实可审，集中独审也已实际交付，但四项P1及F05未关闭，权限、清理、时间门缺少对应反例。不能把工程JSON中的engineering_complete/stable_for_independent_audit当本审计批准，更不能签STEP018整体、019/020、M1、项目、发布或Q启用。

memory窗口的证明特别限定如下。根35原trace、共享释放屏障、独立actor COMMIT、最终007和后续PG对账足以支持“实际撤销/purge发生、late head未推进、007和原reservation保留、GET无动作”。该根没有即时保存before-financial快照，不能补写它，也不能声称单靠该轮精确证明了全部金融差值；后续核证用原operation条数和reserved_cost对齐，范围明确。本缺口不要求整套memory重跑。F03是另外的私有正文副本清理缺陷。

旧scope503按原精确命令缺失、scope_revision仍1及另一个模型45b8d0b4-dd77-44d7-8cdd-370ef475c7b3已committed/received判其原scope变更未提交；不是从503反推回滚。根43 invalid-source 的500保留为真实旧缺陷，最终interview_repository锁内补current_version/revision，根44准确409/source_invalid且业务/金融前后不变，按修后字节接受。

R01/R02/R03兼容亦分层。001—014及旧常量未改只是B层依据；另有旧四库真实新只读连接与R03正常backup/verified restore/seal原件。067整体FAIL保留其独立R01文件域子例；068修正为真正进入PackageReader上下文后，错误迁移hash为codec_mismatch，未知profile为unsupported_format，合法R02包读取和真实R03包读取成立。没有把ZIP reader说成真实R01数据库恢复。

## 5. 执行控制重建

工程账重建见 [engineering-control-reconstruction.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/engineering-control-reconstruction.json)。实际核对5121条events、51根、70份已执行command回执；038原未执行，不补造第71份历史回执。按各许可生效分段核对，不套最后宽上限追认以前行为。

1. 初始许可根1—8，root/PG/API cap为8/8/8，wall14400，持有10800。
2. continuation01实际采纳后根9—16，cap16/16/16，wall21600，持有14400。
3. repair03实际采纳后根17—20，cap20/20/20，wall25200；validation04根21—24，cap24/24/24，wall28800，持有仍14400。浏览器512MiB门仅从04前向采用，不追认早先768MiB门未过为已启动。
4. finalization05实际采纳后根25—40，cap64/64/96，wall57600，持有21600；新增matrix-final仅用于批准的独立TESTONLY反例。
5. continuation06实际登记后根41—51，root/PG/API等额度未重开，只按批准将对象/卷cap各1→2；新增scope-ui-final和工厂目标各在精确许可内。已有失败、余量和unknown未归零。

已保存各根的入口计数未超当期cap、未早于该期实际采用登记；已保存单根elapsed均小于1800秒，回执wall未超各自声明限额，51根结束清理记录均确认。该检查不等于每个未观测历史瞬间都合规，也不代替同问题失败次数的原始保留。

最终累计为roots51/64、PGstarts52/64、API55/96、Browser14/16、build5/8、Native64/128、HTTP1459/10000；PG/卷create尝试各2/2、实际对象/卷各2/2。125条失败记录和TASK117旧81条分别保留，不把记录条数冒充独立缺陷数。active_root/active_command为空只说明末态。

wall逐字段复算为50243.003003/57600秒，与唯一账相同；50299.862003是含071预留60秒的旧报告时点，以071实测3.141替换，差56.859秒。持有为2667.078295/21600秒，根9的79.139295不确定性上界等仍保留。两个7200预留、其他中断不确定性未核销为0；这些是保守上界，不叫CPU或精确工作量，人工实际总时长unknown。

控制轴不通过的原因是接收/计时登记合同未全满足，而非发现最终资源仍在运行。06自身adoption.json明确初次合同读取工具早于登记，13:36:43Z是读卡期间首次采钟，登记为13:38:10.345685Z，未满足permit要求“实际接收在首次新工具前登记”。3秒边界的精确首工具起点没有独立原回执，不能把采钟当接收首点；该微小差异不影响本次实际业务都远早于次日01:06:43Z停止的事实，也不能被后来的登记追认为先登记。

05的精确接收时间未保存，采用签发时刻作更早保守下界并登记finish_deadline=2026-10-20 20:04:46.848938+08:00。059仅文件保存的结束为20:12:01.236510+08:00，晚于该登记期限约434.388秒。真实接收至多24h是否越界仍缺原首点，不虚构连续CPU工作，也不将这份晚保存回执当作业务重启或新24h许可。历史控制限制由主控留账，不能通过改写旧收据消除。TASK117既有控制不通过同样继续保留，不传成TASK120代码已坏，也不被本次技术子项通过洗掉。

源精确CID为b89522070d4b64fc67efed810852ccc21948058f154bf4fa1889f4d8d69a102f，卷retrolume-task120-qprep-data；目标CID为4eb5be54b713e5412be702e27684d98d2b7de92a77f9085b3ce84a5f4b124332，name为retrolume-task120-scopeui-ro1，卷为同名-data。原件核对同一完整镜像sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f、1CPU/512MiB/pids128/restart=no、loopback55480/55481、API18120、无host bind。只接受原停止时点，没有探测当前机器。

财务按实例核对。flow为25/6250000，budget01为100/25000000，budget02为8/2000000，matrix-final为23/5750000，新源为5/1250000；各实例当前已保存快照R均0，工具预留未增加。恢复副本的5/1250000是备份时点历史，不能与源相加成新预算。真实PG新连接/production readonly读取是这些余额事实的依据，Q journal仅作身份、关闭与事件见证。

未发现本工程原记录中的批删、prune/drop、真实provider/实际付费、preview或Git写。独立GitHub同步具有单独授权，未混入本工程0新增Git计数。无法从只读证据确认的整个宿主外部活动没有冒称为0。

## 6. 审计投入、未验证与最小后续

本审计首批先读入口和卡面，未在第一条工具前单独采钟；首个可信时点为2026-10-21 07:44:23+08:00。精确人工接收秒值unknown，保守采用早于该点的卡面签发2026-10-21 07:41:23.826587+08:00作为8h下界，截止15:41:23.826587+08:00，没有用签发冒称实际接收。

实际命令、退出码、wall、非零退出和投入保留在 [audit-command-log.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/audit-command-log.json) 与 [audit-session-receipt.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-121/audit/audit-session-receipt.json)。专门的逐命令台账从第9条文件命令开始；启动期8条按本窗工具回执和用途汇编，完整命令串未在专门台账保存，不能冒称精确重放清单。其中一份大输出截断导致对应wall的精确回执未完整保留，按60秒保守预留，不记0；其他可见收据与后续逐命令数据保留。另有自己的元数据脚本一次因permit_history字段不统一KeyError退出，已按真实id/permit_id结构修正；若干rg不存在路径、初始Python控制台编码及输出截断也如实登记。没有以这些元数据问题触发产品运行、改工程原件或重置投入。

本次实际访问两页官方文档，未安装或联网下载。自身写入仅本审计证据目录与本统一结果；报告落盘后核可读和身份，产品/工程输入再次冻结核验结果另存。人工实际思考/阅读耗时与模型token用量无法可靠取得，均为unknown，不编造。

最小下一步由主控把F01—F05一次合并交回原TASK120工程窗口。修正方案与验证预算须按主控后续合同执行，本审计没有自动建立任何业务运行额度。

1. 修F01/F02后，只补迁移缺权与实际角色继承/SET反例、准确失败回滚和受影响profile/backup/restore识别；原001—014、R01/R02、旧四库及金融事实保持原适用边界。
2. 修F03后，用新批准合成对象补源与memory的精确Q副本清理、失败关闭及原摘要/007/费用保留，不删除本次封存原件，不重跑整套memory竞态。
3. 修F04/F05后，只补批准时间回退/域不明、合法继续、PG已领取未Q claim的投影与续批拒绝及零重发。若只改服务端时限/投影且前端未变，不要求重建bundle。
4. 本TASK121和本独审窗口后续只增量复核修正与直接影响。当前C12、三ACK、列明K2、UI和停止等证据按对象复用，不重新启动本轮完整审计。主控负责共享状态、验收与编号。

真实Q仍待原采用合同所留的当前官方及账户适用性、价格/税费币种、token/framing/reasoning上界、严格返回身份、正常secret loader非敏感readiness、实际新normal实例与固定roster、全部Must可容纳的剩余语义矩阵、集中独审修正关闭及主控首次启用回执；T0/72h未在本轮建立。这些后续事项未运行不另判成本卡事故，也没有被上述工程子事实授权。

报告保存并回传到此为本卡终点。除了人工带回此结果，不需要用户提供密钥、SQL、截图、额外放开Q或再次批准本次只读审查。

