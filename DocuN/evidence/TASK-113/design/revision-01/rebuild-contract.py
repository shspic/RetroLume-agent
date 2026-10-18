"""仅重写完整设计文档并保留首轮原字节，不import产品或执行方案。"""
from pathlib import Path
import hashlib,json,os

ROOT=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent

def replace_section(text,start,end,body):
    a=text.index(start);b=text.index(end,a)
    return text[:a]+body.rstrip()+'\n\n'+text[b:]

def main():
    raw=(OUT/'prior-result.md').read_bytes()
    assert len(raw)==59137 and hashlib.sha256(raw).hexdigest()=='1ca9cda00bcfb7f01bfd5630d909cea211f90e8951011159be984fb1925dff06'
    old=raw.decode('utf-8');text=old
    intro='''# TASK-113 / R-107 修正轮01完整当前合同

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

'''
    text=intro+text[text.index('## A 当前数据与信任边界'):]
    k1=(OUT/'k1-reference-protocol.md').read_text(encoding='utf-8')
    k1=k1[k1.index('拟新增OriginalReferenceCoordinator'):]
    a3='''### A3 同一逻辑时点与统一引用围栏

推荐新增SnapshotCoordinator、OriginalReferenceCoordinator和RootLease，尚未实现。快照先取同根RootLease共享面，再用一个专用REPEATABLE READ READ ONLY连接，首个非事务控制SELECT确定T。流式读取28业务表及A4的三控制表安全投影，最多60秒写受控spool；事务中不等模型、渲染、用户或大量文件copy。事务结束后仅按T不可变内容键复制/hash，共享面持至复制完成。不能拼多个READ COMMITTED GET为全库快照。[已读PostgreSQL事务说明](https://www.postgresql.org/docs/16/transaction-iso.html)仅支持该稳定语义，不冒现场主版本或运行通过。

上传/替换可以并行追加不可变文件；其新引用必须按下面相同根协议保护，所以幂等命中现有hash也不能越过最后清理窗口。模型/tool/preview在途按T原样保未知/预留，不因快照退款。记忆body的并发DELETE由MVCC保T，T后的删除另有恢复覆盖时点，不无痕改已完成包。

'''+k1
    control=(OUT/'control-and-snapshot.md').read_text(encoding='utf-8')
    a4=control[control.index('三个同T载体'):control.index('内部闭包签名')]
    a4='### A4 三控制表与T闭包\n\n'+a4
    a3+='\n\n'+a4
    text=replace_section(text,'### A3 同一逻辑时点','## B 唯一最小实施合同',a3)
    b0='''### B0 一个推荐方案与采用关系

采用现有Python标准库、PostgreSQL/psycopg、不可变原件库、ZIP_STORED和单机受信私有ControlHub。没有新控制数据库或分布式服务。28业务表是现状，三控制表、31安全域、ControlHub及恢复工厂是拟新增。可携与checkpoint共用严格包，不执行包内SQL/角色/命令；新隔离PG集群先受信schema后数据，避免010/011集群角色碰撞。

长期export/backup/restore/activation job由ControlHub唯一裁定；data_operation_jobs的业务库行只含同T观察/归档史，另有K1引用票据是源PG元数据准入事实，不把两者互作权威。该分工与DB mode屏障/只读范围均列入一个STEP017-P1，仍recommended_pending。项目TASK/STEP状态仍只在DocuS执行动态，不由产品控制日志维护。

'''
    text=replace_section(text,'### B0 推荐及权限包关系','### B1 包、独立解读和完整性',b0)
    text=text.replace('checkpoint另有checkpoint/固定table_id.jsonl及codec_description.json；',
       '两kind均另含metadata/source_control.json、metadata/operation_history.jsonl、metadata/tombstones.jsonl及其manifest hashes，来自同一个T；checkpoint另有checkpoint/固定table_id.jsonl及codec_description.json和B5的三控制域受限映射；')
    text=text.replace('格式为retrolume.data-package v1，后缀.rldata',
       '格式仍是未采用的retrolume.data-package v1草案，本轮codec/schema_profile明确为data_exit.v1.r01，首轮无产品包可追认兼容；后缀.rldata')
    text=text.replace('原件不重编码，用户/模型文字按纯文本处理；',
       'ControlHub日志、selector、目标私有注册器、活引用票据/nonce不入包，metadata中的mode/instance仅观察字段，不是loading许可。后续删除/最新账旁证放单独overlays及明确T2，不伪装T。原件不重编码，用户/模型文字按纯文本处理；')
    b2='''### B2 权威、发布、目标工厂和完整恢复切换

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

'''
    text=replace_section(text,'### B2 备份、验证、恢复和切换','### B3 状态、额度和控制转换',b2)
    text=text.replace('可在外部私有控制区保存根hash收据用于核对；收据/密钥不打包',
       '由ControlHub保存根hash完成收据用于核对；Hub live journal/注册器/选择/密钥不打包')
    # B3/B4未变业务语义复用，名称与K1/K3新权威一体替换。
    text=text.replace('先取源文件清理排他租约，再按原源→记忆→活动锁序完成短事务',
       '先按A3取得RootLease排他及PG根exclusive，再按原源→记忆→活动锁序完成短事务')
    text=text.replace('之后按准确hash/size清单逐个核根、普通文件、hash、共用引用并unlink；',
       '后续精确清理每键先按A3持久取消旧未决引用ticket/确认COMMIT，再重取PG根exclusive和最新READ COMMITTED查询，保持RootLease排他直到unlink与结果核对。之后按准确hash/size清单逐个核根、普通文件、hash、共用引用并unlink；')
    text=text.replace('外部本机删除索引', 'ControlHub中带来源/时点的本机删除索引')
    b5=(OUT/'b5-permissions.md').read_text(encoding='utf-8')
    text=replace_section(text,'### B5 拟新增持久模型、权限和具体修改','### B6 API、路径、限额和用户入口',b5)
    text=text.replace('GET /jobs/{job_id}、GET /jobs/by-key/{business_key}、GET /packages给只读进度/原收据；',
       'GET /jobs/{job_id}、GET /jobs/by-key/{business_key}、GET /packages固定从ControlHub给只读进度/原收据，不查当前选中PG来恢复job；')
    text=text.replace('新导航“数据与备份”',
       '切换后资料/学习/面试/记忆按钮须按永久只读caps禁写，文案“仅恢复记录与只读查看，未恢复继续学习或调用的执行资格；原数据保留，持续使用需后续验收”，不称全部恢复并继续Must通过。GET进度/包走持久Hub；无法核模式就拒业务写，不回退源。新导航“数据与备份”')
    c1=(OUT/'c1-adoption.md').read_text(encoding='utf-8')
    text=replace_section(text,'### C1 STEP017-P1唯一采用包','### C2 文件与资源清单',c1)
    text=text.replace('拟增文件为B5列出的data_exit十模块', '拟增文件为B5完整名单的data_exit模块，新增reference.py和control.py')
    text=text.replace('第三个恢复根建议RETROLUME_RESTORE_ROOT，已存在本机绝对目录，与data_dir/backup_dir互不包含；',
       '恢复根RETROLUME_RESTORE_ROOT与私有控制根RETROLUME_CONTROL_ROOT均为受信已存在Windows本机绝对目录，与data_dir/backup_dir及相互之间不包含；')
    text=text.replace('先核role/DDL身份，再加载历史；',
       '先实现全部引用入口/持久取消epoch围栏，再启用精确清理；先核role/DDL及三控制投影身份，再加载历史；ControlHub与target角色撤销验证齐备才测只读切换/丢响应。')
    text=text.replace('无关G3—G11继承仅在同版本/边界处适用。',
       '无关G3—G11继承仅在同版本/边界处适用。只读副本不会完成持续使用/执行恢复Must，矩阵通过只支持该切片。')
    v04='''- V04，DR003/K1，真实最后检查窗口与新引用并发。准确停在D的最终无引用检查后、unlink前，并发B上传同hash/替换/PDF候选/直接元数据/target发布。B先得shared时D等B COMMIT并保共用F；D先排他时B在put前等待、之后重发布再提交。再覆盖COMMIT丢回包、客户端进程死而PG迟到事务、ticket取消COMMIT未知：未决不删，旧epoch SQL拒新引用，第二次READ COMMITTED查全部历史/待PDF保留引用。记录真实RootLease/PG锁、ticket/epoch/事务/文件hash前后；孤立内存锁、两次hash或一空SELECT不能通过。失败保旧成功项/未知，不能换根。
'''
    a=text.index('- V04，');b=text.index('- V05，',a);text=text[:a]+v04+text[b:]
    text=text.replace('- V12，NFR003，', '- V12，NFR003/K3，')
    text=text.replace('- V22，DR002/SEC002，只读切换及源仍活。', '- V22，DR002/SEC002/K3，只读切换及源仍活。')
    text=text.replace('选择器发布失败原源继续。', '选择器提交失败保旧选择和源完整数据，维护围栏不自动解除；只读核对后受信解围才能继续原源写。')
    a=text.index('### D2 四条手工轨迹')
    extra='''- V27，K2/DR002/SEC001，真实同T31域及最小权限。T前后两连接变墓碑/操作观察，snapshot专用角色在同一REPEATABLE READ读28业务+三安全投影，文件载体/hash/缺活票据匹配；snapshot DML/写删除EXEC/控制秘密读取被拒。target新data_control由工厂生成、history/tombstones受限装载，seal后readonly安全view可读/loader权限已撤，包mode/instance不自授loading。
- V28，K3/NFR002，ControlHub跨切换及部分发布。source明确停止/不可连、dataset切新target后，GET原restore key/job/完成收据/包和旁证仍由同journal权威；只坏cache可read-only重放，断尾不算COMMIT、中段坏失败关闭。target注册半落、selector_commit已成功但响应丢失返回同generation，不二次分配/激活、不从旧PG或包重建权限。
- V29，K3/SEC002/NFR005，覆盖全写入口/fence失效/永久只读。源公开POST及内部producer、后续引用、admit/dispatch/preview和后台清理在fence后零新动作，已有登记收尾按原证明；unknown不解除围栏。核source frozen/target readonly/Hub选择一致，旧nonce、owner、draft、ledger或模式未知不能写，原源不毁。明确仍未覆盖恢复后付费/工具/预览/持续学习，不签全部恢复并继续Must。

'''
    text=text[:a]+extra+text[a:]
    a=text.index('轨迹二，');b=text.index('轨迹三，',a)
    text=text[:a]+'''轨迹二，K1修正前后与丢提交。当前源码put/幂等命中与save分两阶段，只有source行锁。旧提议推演D查A外无引用→B复用F/提交vB→D unlink，B刚成功却缺原件，未实际发生。修正后B先shared则D等其COMMIT、最终见B保F；D先排他则B在put前等、删后重发布F再提交。B死/丢COMMIT回包时OS放锁不等于DB没提交，D须PG等待、旧ticket取消/epoch提交确认及第二次最新查询；取消结果未知不unlink。失败可留孤儿，不清旧成功件，全部为方案手工推演。

'''+text[b:]
    text=text.replace('方案推演为T读上述关系→', '方案推演为同T读28业务和三安全投影→')
    text=text.replace('→用户明确切换只读。', '→Hub持久job/target/seal→源写fence和自有收尾→selector_commit→只读绑定，GET原job仍走Hub。')
    text=text.replace('## 实际操作、核对和交回', '## K对照、实际操作及交回')
    a=text.index('## K对照、实际操作及交回')
    text=text[:a]+'''## K对照、实际操作及交回

K1用统一OS根共享/排他、PG事务围栏、持久引用票据/取消epoch、两阶段最新查询及必填pin调用点关闭首轮设计缺口，覆盖幂等命中/全部新引用/迟到COMMIT/进程退出；不靠复查hash。K2增加三安全投影的同T只读权限、metadata/checkpoint载体、target可信新身份与history/tombstones载入/readonlyview，活票据不迁权。K3把长期job/selector/私有注册/旁证权威移到ControlHub，source PG仅观察及引用事实，补工厂/停线/切换/半发布/GET闭包及永久只读代价。均是当前合同设计闭合建议，不是实现/独审PASS或已采用。

原首轮44输入/4补充/7规则，正文未变处复用；新架构1.23/执行2.45头与主控gap补读，原件put及资料/PDF链重读。源码/迁移/配置/正式文档/旧证据写0，当前28表无变；新证据只入revision01。资料索引图/格式例在本轮新建，不覆盖首轮九原件。官方补读LockFileEx/PG explicit-locking两页为关键协议依据，累计6/6，未下载工具、import产品、构造真实包或运行任何产品命令。一次Select-Object只读数字参数误写英文，相关confirm正文用标准库文本切片补足，无产品动作。

本轮真实时长、累计观测/旧余额/unknown、文档一次一致性核对、源/规则未变与旧59137后缀证明见revision01/delivery.json。产品及未来V01—V29未运行；独审仍在完整稳定实现及必要高风险权限门，当前不宣STEP017产品/持续恢复/项目完成。原G11和旧UNKNOWN不作新前置，不重审或复跑。

建议主控先核证本完整修正合同及STEP017-P1差异，再提交用户一个真实必要采用包。尚未批准、未占TASK114，不代主控维护DocuS/CHG/共享状态或授权合成资源。实施另卡冻结精确对象/角色/路径/预算、未来运行/删除/切换边界；用户库/真实数据/私配/真实删除/覆盖/切换/新费用均不在本轮。普通不变内容不再问选择，无新测试经验入库。

以下为首轮59137字节完整原字节历史。当前实施只取以上完整A—D，不执行旧冲突设计或旧到期许可。

'''
    target=ROOT/'DocuN/results/TASK-113-result.md'
    previous=target.read_bytes()
    assert previous==raw or previous==(OUT/'current-contract.md').read_text(encoding='utf-8').encode('utf-8')+raw
    (OUT/'current-contract.md').write_text(text,encoding='utf-8')
    candidate=text.encode('utf-8')+raw
    temp=OUT/'result-candidate.bin'
    with temp.open('wb') as stream:stream.write(candidate);stream.flush();os.fsync(stream.fileno())
    os.replace(temp,target)
    assert target.read_bytes()==candidate and target.read_bytes()[-59137:]==raw
    (OUT/'publication-initial.json').write_text(json.dumps(dict(path=str(target),current_bytes=len(text.encode('utf-8')),total_bytes=len(candidate),sha256=hashlib.sha256(candidate).hexdigest(),old_suffix_bytes=59137,old_suffix_sha256=hashlib.sha256(raw).hexdigest(),product_operations=0),ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(status='CURRENT_COMPLETE_AD_CONTRACT_SAVED_WITH_ORIGINAL_SUFFIX',bytes=len(candidate),prefix_bytes=len(text.encode('utf-8')))))

if __name__=='__main__':main()
