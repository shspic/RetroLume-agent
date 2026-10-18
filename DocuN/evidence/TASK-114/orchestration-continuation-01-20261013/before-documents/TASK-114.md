# TASK-114 / R-108 — 数据退出、备份、隔离只读恢复与资料删除完整实现

## 目标与交付

你是本卡执行Agent。按用户已采用的STEP017-P1和TASK113修正轮01完整A—D合同，在一个执行窗口内连续完成源码、迁移、配置样例、用户界面、相关验证和范围内修复，交付可供集中独立审计的稳定完整成果。不要停在设计、测试准备或每个普通子步骤回传。

用户可观察成果为：能够导出可独立解读的已保存资料，保存一致的恢复备份，在新隔离PG集群验证并只读查看恢复副本，核对和准确删除一条资料的回查内容；刷新/丢响应能按原业务键只读核对，原数据和历史预算保留。

结果保存 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-114-result.md；原始证据只入 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/。源/被测最终字节、差异、迁移与角色身份、真实矩阵、资源和尝试账必须可独立重建。本卡不担任独立审计，不填写编排最终验收。

## 项目、规则与接收安排

项目根 D:/shspic/project_NO3_RetroLume-agent；入口 D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。task_model，V4.0，公共AGENTS修订CHG-0003；七锁定指纹见 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/v4-migration-20260930/rules-snapshot.json。公共根 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，读取DocuS/AGENTS.MD及WORK适用2/6/8章；本卡已内含完整回传要求。同窗未变正文和证据复用，只补变更与缺失。

需求v1.2、架构v1.25、执行动态v2.47、阶段07。TASK114/R108/STEP017，父TASK113/R107，关联MOD008/FLOW007/API005、DR001—003、NFR002/003/005、SEC001/002及已有限关闭的G3—G11。原始需求 D:/shspic/project_NO3_RetroLume-agent/DocuS/原始需求文档.MD 用户维护，Agent只读；最终需求在同目录最终需求文档.MD。

授权依据：用户2026-10-12明确回复“确认采用”，采用的是TASK-113-work-decision.md的STEP017-P1完整包。当前有效主控决定位于 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-114-work-decision.md。授权终点为此包的完整合成实施与定向验证；真实用户库迁移、真实用户资料删除/覆盖/切换、真实provider/密钥/费用不包含。

接收A+增强执行，优先刚完成TASK113修正轮01的原设计/工程窗口。该窗口自报Codex desktop/GPT-6，精确子型号与窗口ID无可核工具，不冒确认。涉及角色、事务、原件竞态、控制权威、恢复和全应用写围栏，需要增强资源。原窗口确实不可用才使用同等胜任A+新窗口，按本卡恢复，不重研究已验收设计，不把已完成工作因型号重做。不派子Agent，不交TASK112审计窗实施。本卡独占允许产品文件及新资源，无并行业务测试或共享账写入。

TASK113已验收关闭：修正轮2995.156秒，设计累计6256.265/10800秒、准备unknown、官方资料6/6页、产品运行0；余额不是本卡许可。旧G11全部失败/预算/历史13元/626.566超限、旧unknown25/R60/count1等保持，不复活旧卡或取证旧25。本任务实际执行尚未开始；新额度是前向授权，旧投入仍在历史账，不追认既往偏差。

## 背景与最小充分上下文

按以下顺序读取，同窗已读未变部分不全文重读。

1. 本卡、根入口、锁定规则必要正文、本项目执行动态/架构的当前头段与本卡work-decision。
2. D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-113/design/revision-01/current-contract.md，81813字节，SHA-256 8a56ebf3c1715895e3ee7a0dcf1f621b591335400e9898aa00df8cb2b7a61aaa。这是唯一完整当前A—D合同。它也是TASK-113-result.md的精确前缀；结果140950字节/SHA-256 37ba578fa653f778ab60f38b008c3c570e1e106a9237d55829cd21b5f47e19d0，后缀首轮只作历史，不拼接冲突段。
3. 同revision-01的b5-permissions.md、format-example.json、control-format-example.json、relationships.mmd；主控核证 DocuN/evidence/TASK-113/orchestration-receipt-02/design-acceptance.md及received.json。必要采用已生效，不再问相同技术选择。
4. 最终需求中DR001—003/NFR002/003/005/SEC001/002，架构MOD008/FLOW007/API005及G11有限边界；按113事实地图读取当前001—012、28表、OriginalStore/materials/PDF/五领域仓储、worker/preview管理、main/start_local与前端意图模块的直接受影响函数。不重读全部历史TASK或实验库。
5. 本卡 DocuN/evidence/TASK-114/orchestration-20261012/input-manifest.json、resource-allocation.json、window-assignment.json。改文件前核当前身份；若有未登记漂移先查明，不能覆盖其他人的改动。当前Git工作区有长期累积修改和旧目录归档删除，不以HEAD复原或把整仓差异算本卡。

必要当前合同可从113结果前缀或revision-01/current-contract.md互核恢复；其他关键材料仍不可读则完成不依赖部分、交回精确缺口，不假称已加载。公共库只读；产品运行不import本设计脚本、DocuN/公共库或临时实验实现。

## 必须形成的完整产品成果

以下是已采用合同的执行要点；细节和29项未来矩阵以113当前A—D为准，主控授权与本卡资源边界优先。

1. 013与最小角色。新增backend/migrations/013_data_exit.sql，三控制表data_control/data_operation_jobs/data_tombstones、四NOLOGIN角色及固定安全view/函数。九个受信新目标loading INSERT分支精确绑定SESSION_USER/TG_OP/目标身份；只将teaching_commands两条指定FK改DEFERRABLE INITIALLY IMMEDIATE。原不可变UPDATE/DELETE、hash/关系/CHECK和普通在线规则不放宽，001—012原件零改动。补实际必要schema/codec和memory/preview指纹，ACL撤PUBLIC/固定search_path，不信包expected hash或SET变量自授loader。
2. 统一引用围栏。RootLease以固定不可替换文件对象的LockFileEx共享/排他跨线程进程锁实现；所有put、幂等复用、上传/替换/PDF候选/确认及直接元数据提交必须带live ReferencePin/预分配ID。PG根事务围栏与源持久ticket/epoch同COMMIT准入；进程死/提交未知不能借OS锁释放推断未提交。取消旧票据/推进epoch须先独立COMMIT确认，再取PG排他以新的READ COMMITTED语句核全部未删除来源的历史/待PDF保留引用，持共同排他到准确unlink。不能在同一可回滚事务里取消票据后删文件。
3. 一致快照与包。一个专用非超级snapshot LOGIN、一个REPEATABLE READ READ ONLY连接、同T读28业务和3安全控制投影；快照事务有界spool后，RootLease共享持续到原件copy结束。ZIP_STORED/data_exit.v1.r01、固定codec/manifest/README/独立文本关系与hash；不自引用root hash，不把hash当可信作者或执行权。metadata三载体纳入同T，后续删除/最新账旁证明确T2及unknown。保当前/旧/待PDF、教学/面试修正、模型正文、引用、记忆/工具/HTML状态，合法原因缺失与损坏区分。
4. 私有ControlHub与发布。独立可信RETROLUME_CONTROL_ROOT，有界稳定文件锁、顺序journal/hash链/完整COMMIT尾标/flush/fsync；journal为长期job/selector唯一权威，cache不授新权。源PG progress是带control_seq_observed的T观察，reference_fence仍是实际准入事实。原键同hash回原收据、异hash409；所有GET/reconcile只读核原件，不再创建/恢复/重发。完整包文件和Hub收据分开明确发布点，半发布补准确收据而不复制第二包。控制区不可读/中段坏时新写失败关闭。
5. 可信工厂与隔离恢复。固定profile由可信host给，不接浏览器或包内DSN/命令/路径。allocate/prepare/verify/seal/activate-readonly/get-by-key/reconcile按113签名实现。新独立PG集群先受信001—013，再原件/28业务与3受限控制codec；target身份可信新建，history转archive_history不复活source活ticket/job。源无loader权，目标加载权精确，seal后撤成员/票据并用真实readonly LOGIN验证可读/拒DML/旧退款函数。Bootstrap/loader新凭据受控撤销；只读凭据DPAPI私有引用，缺配置/不可解密503，不默认安装服务或改现有角色。
6. 状态/账与删除覆盖。请求/费用/工具/时间/预览四类原账、代次、终态、原正文hash/依赖与UNKNOWN原样保快照事实；活owner/key/hash/nonce/PID/CID/单调时钟不可迁执行资格。必要存储占位要有精确变换清单并立即丢弃控制秘密，不把archive clock当真实时刻。默认respect_current_deletions并集当前同谱系删除覆盖；snapshot_only_readonly须显式动作，源墓碑不撤。永久只读副本不认领/折叠/结算/退款/启动旧任务。
7. 源停线与只读选择。MutationPermit绑定control/selection_generation/dataset/instance，覆盖全部公开业务写、内部producer、新引用、admit/dispatch、preview及清理；spawn前登记真正自有树与原管理归属。维护先持久拒新permit，再按原SUP/ClosingCallGate/preview.stop关闭自有工作，允许已有结果/结算收尾lane而不许新出站。原证明齐备后源frozen，持围栏跨selector_commit及新只读绑定；模式/拥有者未知不切，超时不自动normal，已切换丢响应GET同generation。只读绑定skip旧worker/preview recover、换会话与编辑身份，不能因新target不可用回退旧源开写。
8. 删除资料与记忆。新增资料影响预览和明确确认，业务键/修订/impact hash锁内复核；墓碑current_version=NULL/revision+1后所有版本/PDF/引用回查失效。精确清单只unlink本条已无共享引用的hash，失败pending/unknown，历史/WAL/旧包不删。停止只针对本条影响的准确当前自有预览，不拿删除当退款。记忆沿原revoke/M3，只补墓碑/删除索引和恢复view，未purged不冒done。
9. HTTP与工作区。实现113 B6的/api/data只读caps、jobs及按key查询、包下载/流式上传、恢复计划/验证/显式只读切换、cancel以及材料删除影响/确认。复用原本地会话/来源认证，响应不漏DSN/路径/内部控制。挂载“数据与备份”完整用户流；清楚区别可携导出/备份保存/副本已验证/已选择只读。跨选择所有旧业务入口按caps与服务端/DB门拒写，四类意图/草稿/迟到响应按dataset/instance隔离，刷新只GET原key、不自动POST。界面不要显示内部TASK/表/role。
10. 配置与维护。新增安全config/data-exit.example.json、deploy/data_restore.py、必要start_local/main绑定及README；无缺省自动运行/定时备份/真实用户库升级。12版尚未启清理时保持既有行为；13版开启清理必须全部writer使用围栏，不允许同根旧无pin writer混用。告知永久只读不完成完整NFR005/恢复后持续学习执行，后续Must保留，不暗中缩原目标。

## 允许文件和独占范围

允许新增 backend/app/data_exit/ 的生产模块：__init__、contracts、codec、repository、snapshot、files、packages、restore、deletions、maintenance、reference、control、api及同职责必要内部文件；新增013_data_exit.sql、deploy/data_restore.py、config/data-exit.example.json、frontend/src/data/ 的工作区/API/选择上下文/样式。

既有文件只为上述接线、围栏、只读投影/模式、指纹与归属登记做必要定向修改：backend/app/main.py、storage/originals.py、materials/api.py与repository.py、pdf_review/api.py；activities的api/service/repository/teaching_repository/interview_repository；learning的api/service/teaching_api/teaching_service；memory的api/service/repository/context；interview的api/service；worker的launcher/session/one_call/one_tool/worker_main/supervisor_main；preview的api/production_supervisor/supervisor/reaper/production_reaper/repository及schema-fingerprint.json。不得顺手重写这些模块原预算、结算、停止证明、解析或业务状态算法。确需超此文件边界/主要语义时报告具体影响并停相关部分。

前端允许main.tsx、PdfReviewPanel.tsx及activities/explanations中直接受选择上下文、只读caps、意图namespace/迟到保护影响的Workspace/Panel/Intents/Drafts/API文件；保教学/面试/HTML/记忆原正文和验证纪律。允许deploy/start_local.py、README.md与.gitignore中仅新增私有data-exit.local.json及新runtime私密文件规则。

测试允许新增backend/tests/下以test_data_exit开头的Python文件、backend/tests/fixtures/task114/、frontend/tests/下以task114开头的mjs文件与本卡验证入口。既有测试仅适配必需新参数/角色/模式/身份，保原业务断言与定向FK清理，变化留pre/diff/post。允许生成frontend/dist作为本卡被测bundle，依赖/锁文件原件不改。

修改前为每个既有目标留原字节副本与hash，新增文件登记此前不存在；批级as-run和最终字节各留独立快照。其他代码只读。禁止修改公共库、AGENTS、DocuS、原始/最终需求、旧TASK结果/证据/归档，禁止重建旧四根目录；shared TASK/R/CHG/最终裁定由主控维护。

禁止Git add/commit/reset/clean/stash/checkout、依赖安装/锁变更、镜像pull/build、迁移包内SQL、session_replication_role或关闭CHECK/FK/触发器、递归GC/删除旧包或整个目录、真实provider/网络/费用/用户私配/任何旧库和旧容器操作。只读Git diff/status可留本卡差异；Git累计已有修改不回滚。

## 精确新资源与凭据

主控已只读确认本地PG镜像 sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f，linux/amd64，image声明PG17/17.11；实际server_version_num须在本卡新合成实例记录。仅按此完整image ID创建，不pull、不用活动tag代替。所有旧容器/卷/端口/role预算不借。

- source：唯一名称retrolume-task-114-data-source，唯一新卷retrolume-task-114-data-source-data，127.0.0.1:55461→5432，库retrolume_task114_source。
- target01—08：固定依次使用retrolume-task-114-data-target01至target08，卷对应名称后加-data，端口127.0.0.1:55462—55469，库retrolume_task114_target。每slot为新独立cluster，不是同集群换库；只用实际需要的slot。source/target各固定专用retrolume_task114_admin/app/snapshot/loader/readonly等LOGIN，成员按013角色身份精确给，随机合成口令。本卡目标工厂的固定profile只给这些slot与可信目录，不能取包的指令。源不授loader。
- 每PG对象固定1CPU/512MiB/pids128、restart=no、一份named data volume挂/var/lib/postgresql/data，无host bind、无docker.sock/privileged/host network；只公布上述loopback PG端口。创建前核slot/卷/端口未占，成功后取完整CID/image/name/volume/label绑定再首个SQL，后续只用该CID。发生碰撞/返回身份未知不改名绕过、不DROP/recreate同slot。
- 仅在新维护围栏确实影响自有preview收尾时，允许最多2个全新合成preview，namespace retrolume-task-114-data-preview-，动态preview_id/name由真实生产registry生成后精确登记CID/boot/birth。固定G11已接受镜像 sha256:ec3c70c7a8a8894c647a69b08b0c296727bb052f639e487567e9cd4624766789，load8a047050ffe584dffa6e85222c16c8f400c0ab4db82f72a32812c2befd082b3f；权限、网络、readonly、限额仍完整沿原已接受HostPolicy/真实控制链，只可改变本卡namespace/控制根和合成关联，不换8秒ready、D、停止/双EOF/退款门。不build新镜像或重测G11全矩阵，不碰旧25及旧preview。若只读门/新增围栏可用既有未变停止链与定向非渲染证据充分验证，则不消费preview。
- Docker同时Running最多2个本卡容器，PG检查用source+一个target，preview检查用source+一个preview，其余目标保持stopped。禁止为赶进度并开8目标。PG生命周期和Job/浏览器均串行，不能启动无限后台keepalive。
- API仅127.0.0.1:18114，必要Vite仅127.0.0.1:15114，前端测试使用本机已有Playwright/Chromium，不下载。真实Windows业务/受控Job窗口最多12个，只合成传输/有限工具；不复验未变G11整套。

本卡四类工作根是D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/synthetic/下互不包含的source-root、backup-root、restore-root、control-root；另scratch与sentinel-root。目标按受信job UUID在restore-root下建，禁止用户/包路径输入与reparse/UNC。所有新目录实际有内容才创建；private ControlHub/凭据不出包/公开DTO。本卡synthetic只作测试数据/运行配置，不作为产品实现import来源。

唯一本卡资源登记位于DocuN/evidence/TASK-114/implementation/control/。在实际接收首工具固化UTC/monotonic及许可TASK-114-STEP017-IMPLEMENT-20261012；源/targets/preview/API/Vite/Job/Browser每个记录准确身份、owner与begin/end/异常/状态。admin/DSN只经stdin、限定环境或DPAPI私有引用；argv只变量名而非secret值，日志不dump Env、connection、注册器或真实密钥。缺专用DSN明确not_run/skip不fallback用户DSN。

主控出卡只读观察：上述TASK114命名和18114/15114/55461—55469无已知占用；本机16线程/约16GiB RAM，采样可用约521MiB，D盘可用约204GiB。这只是采样，不是运行前提已经通过。资源runner实际启动前复核可用内存，两容器/浏览器组合建议可用至少2GiB；不足先完成源码/离线不占用容器，不停用户软件/daemon、不以新slot绕过。本卡接受暂时资源不足的精确事实，实施者不能冒已验证或靠盲重启解决。

## 预算、连续批次和异常处理

从实际首工具UTC/monotonic接收起，本卡总前向工作窗口28800秒；实施/阅读/文档在此总窗内，不用发卡时间设置短时失效，正常步骤不逐次问用户。离线检查/测试/build子进程累计7200秒；本卡真实资源持有时间合计10800秒，其中最后1200秒只用于清场，真实业务持有门为9600秒。清场仍计真实持有，到该业务门后只允许必要准确收尾。总窗口同样提前预留1200秒清场时间，禁止新消费者。

资源持有为各本卡容器从实际Running到确认Stopped的区间、API/Vite/Browser/受控Job从ready/进程存在到准确结束的区间分别求和；并行对象均计，不因只跑GET/在等修码暂停计费。成功create后到首次start前另记准备时长；未知end保守记至确认或标unknown，不能填0。商业费用新增0，模型/provider新调用0，公网0，localhost仅本卡端口。

真实批次根最多12，PG create尝试最多12/成功slot最多9，PG start尝试最多32（只本卡精确已登记stopped对象），preview create/start各最多2，API/Vite启动各最多8，Browser启动最多6，真实Windows窗口最多12，frontend build最多6。数字是各自独立上限，不自动用满，不以秒余额替超次数许可。失败命令实际接触create/start/SQL/HTTP业务或真实browser时计入其根与对应计数；同根内连续的既定方法不逐命令新开根。只读本机元数据/静态脚本准备不算真实根，旧预检失败计数不追返。

使用一个小型可审阅合并runner即可：先离线parse/参数/路径/loop-factory/环境存在性自检，再完整inspect JSON解析白名单（不输出Env），之后统一包围真实PG/文件/HTTP/UI和finally收尾。不要复制旧已失效runner/控制账或扩建通用平台。Windows psycopg采用项目已有Selector兼容loop factory，不靠默认Proactor；session token bootstrap、admin DSN与CLI形态在首次业务前核齐。包装器异常也保原日志和根计数。

先实现稳定全部链和场景，再尽可能在一个资源会话中完成一组完整矩阵；PG/文件真值成立后同最终字节接HTTP/UI。普通包装/夹具/范围内产品缺陷查明根因后在本卡修复并定向复验，不每次普通失败即转交；保失败原件、所有pre/as-run/post和新预算账。同一因果经两次有证据修正仍失败、关键前提被推翻、根因不稳、新高风险/越界或任一实上限到达，停止受影响消费者并交回；不换根/slot/模型清次数，不自动降低断言。已经充分且对象不变的通过项直接复用，修订只补实际影响。

## 验证、证据与审计关系

现在验证的是新增迁移/最小权限、全域codec/原件并发、一致恢复和停线/选择/删除行为；设计阶段未测，既有G3—G11不变部分已有证据，不能拿构建或mock当真实恢复通过。当前运行层权限仅合成，新数据角色/删除最终产品放行仍待隔离集中独审。

必须逐条映射113 D1的V01—V29，保其实际子分支和关键异常；可以把共享fixture/同资源会话合并为以下组，不删真正受影响行为、不为了方法数扩压力测试。

- 迁移/角色：source在001—012合法非空数据上升级013，旧业务值/原账不改；新空target先完整可信001—013。九guard加载/在线拒绝、两FK循环、view与最小权限/撤loader后的真实read/拒write、13指纹；独立fault slot验证非空004/005、已有010/011角色或错误profile明确拒绝，源不动。V07—09/V27。
- 快照/可携：真实28表闭包+3安全控制域+原件/关系/正文，独立JSON/文本工具可解读；T前后两连接变来源/范围/outcome/settle/墓碑证明一个T，非法断开不拼新T；PDF pending/confirmed/skipped和supplement真实保持。V01—03/V05/V27。
- 引用/删除竞态：真实跨线程与进程RootLease/PG围栏；D最后查询后unlink前的准确窗口、B先shared和D先exclusive两序、同hash导入/替换/PDF候选/直接metadata、COMMIT丢回包/进程死PG迟到/epoch取消未知，核保共享历史文件与已成功提交、不生成悬空引用。真实路径/文件hash/锁和ticket事实留证。资料墓碑即回查不可用，清理pending/幂等；M3撤销/旧备份删除覆盖分层。V04/V14—16/V29。
- 完整恢复：受信factory真实新cluster、全31域受限load/原件/关系/record文本对账，既有合法旧received无正文也保留；非零四账/预览unknown/R及控制占位变换明示、旧key/StopProof不授权。验证后撤权的readonly HTTP真实可读，源最新账不被旧备份覆盖。V06/V08—13/V27。
- 不可信输入/失败：真实文件系统白名单拒路径/ADS/reparse/链接/重名/压缩/截断/错SHA/缺原件、目录/行/总量/深度/组件/时长边界、取消/崩溃/部分发布；包容量上限可在测试专用可信profile降低以精确测边界，报告实际低值，不声称真跑2GiB吞吐。失败封存原target，源和旧包不变。V17—21/V23。
- 权威/只读切换：真实ControlHub完整尾标/坏cache/断尾/中段坏/半注册，source不可连之后原key/jobs/包/收据仍GET可核；已有selector_commit丢响应同generation。fence覆盖每类公开和内部写，不把ClosingCallGate当全应用；准确登记自有工作原证明收尾后才source frozen/selector，未confirmed不切不自动开源，新readonly启动不recover旧worker/preview。V12/V22/V28/V29。
- 浏览器用户流：同最终bundle、认证caps/导出/备份/下载/上传计划/验证/只读选择/资料删除影响确认及损坏/不可用文案；丢响应/同键hash冲突/刷新只GET、选择切换后的旧draft/晚到不污染当前、按钮和恶意POST均不能写readonly。用户浏览器草稿不冒服务器已存数据，已删除覆盖和永久只读文案明确。V24/V25，加各HTTP/权限矩阵。
- 证据/收尾：每方法普通raw日志、SQLSTATE/文件/端口/确切身份、截图/请求线/as-run源与bundle hash、失败/修复/最终映射及source/target保留列值。方法PASS须真的执行且关键分支观察成立，skip/not_run不是PASS。V26及全部方法。

同因修复后按实际改变层复验：改变DDL/加载guard要最终版真实PG；改界面渲染/意图/选择要最终bundle浏览器；改准确锁窗口要重验相关真实竞态，compile或一般样例不替代。不改变的领域原同COMMIT/预算/StopProof/数学/界面证据按版本/配置/边界继承，给具体身份，不重跑G11全矩阵/原支付实验。不得为最终通过编造旧夹具、倒改旧FAIL或只给执行者自评。

原始证据只存一份在implementation，对引用外部/旧项目路径按AGENTS归档映射。本卡稳定完整成果后由主控另派TASK115/R109隔离A+集中独立审计一次，当前仅计划未占号；输入为原需求/已采用合同、最终差异与原件、角色/DDL/as-run和资源账，不输入本窗口完整聊天或思考。你只提供可审证据，不自审代签。

## 精确清场、停止与回传

每个真实根都有finally及外层有界收尾，能停止本次准确拥有的job/app/browser/container；不发全局kill/docker prune/stop-all/递归Remove-Item。停止前核CID/image/label/name/volume或PID/birth/boot/父链，未知身份不碰。合成文件准确删除只走已实现source清理或测试明确恶意输入的准确已登记单文件，先核绝对目标留在本卡根/本条清单；禁止跨shell拼删除命令。角色/DML只有本卡新cluster/schema，不能用旧管理员凭据。

根结束记录准确Running=false/Pid=0、端口无监听与本卡树/EOF/句柄事实；需要PG退出确认时实际检查，不能仅凭runner退出。所有新容器、卷、source/target合成数据、失败包、manifest和控制journal保留，不DROP/REMOVE/删除证据。未知停止不能造退款/完成收据，留确切unknown交回。本卡不为了清场更改旧未知25或其他任务对象。

完整成果到达立即保存并停止，不以额度剩余继续研究/加特性。边界不变的未验收修正仍沿TASK114/R108和同结果追加历史；跨批失败/旧结果原文保留。先完成不受阻部分，真正越界或额度/同因停止门出现时给主控最小完整剩余清单、已就位修码/资源真实状态，不要求用户重复技术采用。

结果开头写一句真实结论、完成范围和建议候选状态、实际文件差异及作用、关键证据导航；再列合同V01—V29逐项实际观察/版本/未验证、真实命令与退出码/时长、pre/as-run/post和最终原字节快照、ACL/源码/包/bundle身份、完整尝试/投入/资源余额/异常/历史影响、未完成/风险/偏差、正式文档待同步、必要人工及下一步。不能把永久只读代替全部NFR005或宣STEP018—020/M-1/发布/项目完成，不自签TASK114或STEP017。

完整结果真实保存且复读后只回复一句话结论与可点击 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-114-result.md，供用户带回编排。没有保存才明确未保存及原因，不伪造路径。

当前必要用户操作仅人工转交本卡；不需要用户密钥、资料、现有库凭据或重复批准STEP017-P1。源码/配置/README变化及合格经验候选只报告主控，DocuS/共享编号/CHG/最终放行统一由主控维护。
