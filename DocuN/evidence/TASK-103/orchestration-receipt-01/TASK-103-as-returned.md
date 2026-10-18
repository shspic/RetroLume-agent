# TASK-103 / R-097 部分实现、定向证据与按限额停止结果

本卡部分完成并按获准次数上限停止；源码、实际成果、断点和资源收尾已保存，但完整G9候选验证尚未闭合，末尾修正未做PG/HTTP复验，不签独立审计、G9、STEP013、M-1或项目通过。

2026-10-06，Asia/Shanghai。执行根为 D:/shspic/project_NO3_RetroLume-agent，许可 TASK-103-G9-20261006，父 TASK-102 / R-096。接收为本业务窗口A+执行职责，实际Codex desktop，具体部署型号不可见；没有子Agent、独立审计窗口接管、Git写入、依赖安装、真实provider或用户库操作。

## 停止事实与本次接续

真实入口24/24、browser与driver各3/3、构建3/3已到上限。原固定首读、单调截止和所有旧失败均保留，未因中断或续作清零。中断前real-10浏览器已在16:35左右结束并停止自有服务器/PG；续作先核持久结果、进程和端口，未重开已结束的测试。工具旧session返回Unknown process id只表示工具会话已关闭，实际结束依据为已落盘结果和资源见证。

没有形成全绿的最终候选。多次夹具错误实际消耗了额度，其中浏览器三批均失败。real-24发现的普通继续错误码映射缺口已修源码，随后仅完成许可内的源码收尾、离线检查和只读封装。没有用余下SUP或时间额度绕过真实入口上限。

所有主要证据在 [TASK-103证据目录](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/)。最终文件、差异及每次执行身份见 [pre-diff-post.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/final/pre-diff-post.json)、[product.patch](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/final/product.patch)、[runs-ledger.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/final/runs-ledger.json)。不能把某批中已通过的性质升级为该批PASS。

## 已保存实现与最终字节

初始233个产品文件有原字节pre副本。最终24项变化包含21个既有源码/配置/README文件，以及生成dist的index变更和两个旧生成资产移除；209项初始对象未变。34项新增包含32个源码/本卡测试材料与2个最终生成资产。旧生成资产仍保留在pre，产品源码缺失0。既有pdfjs版权文件未被初始业务枚举覆盖，最终另列为既有观察对象，未冒称新建。完整逐文件pre/post/hash以最终manifest为准。

主要实际改动如下。

- [010迁移](D:/shspic/project_NO3_RetroLume-agent/backend/migrations/010_learning_memory.sql)新增M1—M7、复合FK、版本/数量/digest约束、不可变与正文guard、资格函数和精确清理。最终SHA-256为3ffe743b64037039512df683b1e21386b8869fc1726fcc9e3da04a4dac2d1194。
- [memory仓储](D:/shspic/project_NO3_RetroLume-agent/backend/app/memory/repository.py)与同目录contracts/service/api/context模块实施严格命令、元数据分页、有限详情、CAS与同槽回放、固定选择、观察闭包和v2复建。仓储最终SHA为cb4bd4adc8e2d3744692b6577fc51cd2bd9a43dba522472a24a55ee90ce4a5d5。
- activities repository/service/api和teaching_repository接入同连接前缀锁及读/写资格；[活动API](D:/shspic/project_NO3_RetroLume-agent/backend/app/activities/api.py)最终SHA为8207d7bea2f22e7167c02aad0b4c31cc8e223ac06e92d3be378014a44f8863d3。[教学仓储](D:/shspic/project_NO3_RetroLume-agent/backend/app/activities/teaching_repository.py)最终SHA为9a8d5f89ed99aa1ffc437c469799a7a2726f26cd222bb9ab818fed80b4ac3e63。
- teaching_contracts/service/adapter/api/views、capabilities contracts/gateway实施独立v2类型与受信绑定，v1字段没有添加新默认记忆键。main挂记忆router；service_config与activity.example新增默认关闭的memory_context；旧learning入口拒绝选记忆活动绕行。
- [MemoryWorkspace](D:/shspic/project_NO3_RetroLume-agent/frontend/src/activities/MemoryWorkspace.tsx)、memoryApi/Intents与专用CSS实施列表、详情、明确保存/修订/撤销/清理、草稿与未确认动作；已有两个workspace、teachingApi/Citations接线。组件最终SHA为4d1a449e175c8107f3dfc8882151b05a62c358a4a7f1b83cd4c5950d6477d79d。
- DEF019只修[teaching_policy](D:/shspic/project_NO3_RetroLume-agent/backend/app/learning/teaching_policy.py)单位比较。最终SHA为55a638531b22e7b046ea51a799ced1d74a26330225f7cd3a216d6fe005eabbde。全文肯定文法和原progress算法未改。

001—009、资料/原件/PDF/retrieval主体、全部worker/launcher/SUP/Job/关闭/结算主体和依赖锁保持初始字节，见manifest的unchanged_protected。未改正式DocuS、根入口、公共库、原始需求、私有activity.local.json、旧证据或归档；本卡不维护第二份项目总状态。锁定规则7项、102合同2项及103卡面10项再核一致，见 [inputs-after.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/final/inputs-after.json)。

函数范围继承以带class/外层function限定名的 [function-diff.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/final/function-diff.json)辅助判断，完整文件字节与diff为主证据。

## 实际接口、锁序和删除边界

新增GET为memories列表、单条/历史版本、commands收据、impact预览、活动memory-selection和progress memory-preview；唯一记忆写入口为POST /api/memories/commands。所有GET只读，经local_session与Origin保护。列表SQL仅投影元数据/有资格短标题，不先取全正文到应用后删；真实50项Unicode响应25641字节，详情及依赖另取。命令规范hash排除business_key，UTF8、递归重复键、确认布尔、数量与大小均有封闭校验。

create_activity新增关键字选择，在一个事务固定具体ID/version/revision/body hash；不提供执行后补选。无选择沿旧路径，所选任一背景/来源/原观察/上游失效时活动派生成果停用。背景不作lc_正确性引用、不升级掌握、也不授模型/工具权限。

前缀锁先定位闭包及活动，再按来源UUID、记忆头UUID、相关活动UUID，进入旧操作/教学对象和M5/版本/正文。头/范围提示锁后再核，不逆序补锁。普通修订/撤销补上该前缀，同时首次INSERT竞争仅做一次有限赢家收据核对。真实同键并发和不同键同槽分别为1与2个持久收据，均只1个有效效果。锁序全部竞争排列尚未穷尽验证。

retrolume_memory_owner/app/purger为本卡独立cluster中的NOLOGIN角色。普通retrolume_task103_app有选择/插入及限定头列更新，无M3 DELETE/TRUNCATE、owner/purger成员权；清理为受限definer，固定可信search_path、撤PUBLIC执行、显式public对象。真实普通app/denied角色证明多种直写、DDL、GUC伪授权与未授权执行拒绝，superuser只用于获准合成准备/故障。

撤销第一事务提交墓碑、全部本条M3版本/hash/bytes清单和无正文收据；第二事务至多一次精确清M3。失败时墓碑保留、正文清理整笔回滚；原键回放不自动补清，用户显式purge只引用原清单。不删除001—009事实、资料、原件、WAL、备份、其它记忆或其它资源。真实清理正常、错清单、缺/额外清单项、正文hash篡改和第二版删除中途故障已分别留证。

## 最终版本与已运行版本的差异

以下末尾源码变更发生在真实额度耗尽后，只有最终离线语法/合同检查与差异证据，必须补实际PG/HTTP验证。

1. activities/api补memory_profile_required与memory_dependency_invalid的409和中文映射。real-24真实收到HTTP200、status=memory_profile_required、business/supervision为空，没有启动SUP；原来业务拒绝生效，但HTTP映射漏项。
2. activity_memory_eligible补M6头不存在而007结果或持久context具有v2残迹时失败关闭；仓储无选择行与schema absent分支也补该检查。缺009表的旧路径不强加查询不存在表，相关占位参数数目已同步。
3. purge_learning_memory的result_meta改为固定键序/无空白canonical TEXT，并更新上述两个函数的源码指纹。未修改已存不可变收据。

已保留的pg1/pg3仍是之前实测的函数版本；最终源码的严格指纹会使其先失败关闭。后续在明确运行许可中先核当前CID与数据，再向前更新这两个本包函数并补差异验证，不能重跑010创建、清空库、改001—009或改旧收据。最后变更不能借之前绿证据签最终DDL和读面。

## 验证口径与V01—V24

四批离线均通过，方法执行数20、7、8、23，共58次，stderr识别28个不同方法身份。最后23方法检查最终Python语法、严格DTO/容量/内通道、preserved pre模块的v1规范字节与DEF019。子测试成功项没有逐例输出，不编造总数。方法数不是业务窗或验收性质数。

构建01失败，02修复通过，03最终typecheck/Vite通过。24份frontend src与build03快照一致。浏览器02/03缓存中完整JS/CSS字节与最终dist均一致，见 [bundle-chain.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/final/bundle-chain.json)。JS index-BQAB3kOg.js的SHA为06fc8a7b35b975e21be2c5649bba8c5d137d2dd7e2a16197d951bee20662a5a8。构建和实际加载不是整批浏览器通过。

真实16次SUP均为原Windows链，最低HttpxModelTransport.send合成替身及透明profile观察，不替代准入/mark/record/UUID/Job/单调钟。没有真正tool业务launch；合法选记忆教学calc因最后测试提前失败未执行。真实入口24个不等于24个成功测试，real06只是受控只读诊断。

以下逐性质说明真实范围。root简称对应runs-ledger的real编号，原件各在相应runs目录与组合结果；部分批失败仍只继承明确完成的性质。

- V01 部分A级成立。root08及19真实G8 progress→显式观察保存，self_report/limited分层，source/event/所选upstream闭包留证。最终SQL差异待复验，不签整个性质完成。
- V02 部分A级成立。root07真实3版、旧版superseded可读、同内容无效应与原键回放、撤销后正文空。不可改旧版本；最终清理收据格式待实测。
- V03 部分A级成立。root07/08固定选择与相同创建身份重放；root19错误body hash零activities创建。1..4全部组合和创建竞争未全跑；最终缺M6残迹分支未实测。
- V04 有限A级成立。root19两种背景、persisted v2 recipe无messages/记忆正文、同key复建后恰1 SUP；超容量/缺配置在accept前0新命令/0 SUP。最后离线实测输入估算、模型identity、UTF8背景和OneCall真实字节限额。不是供应商tokenizer容量证明。
- V05 部分A级成立。root09真正source replacement使记忆所选活动失效，含无source依赖的自报选择仍受活动资料快照约束。新PDF候选/确认后记忆传播未新增动态例，原PDF主体仅按未改字节继承。
- V06 部分A级成立。root08/19版本改动后派生读失效、原预算不改、旧选择不换新版。所有时窗组合未全覆盖。
- V07 部分A级成立。root09 correction使原观察与target失效且preview抑制；root19 answer后继同样使原观察/target失效。另种新feedback与无关事件反例未全部执行。
- V08 部分A级成立。root19源/至少4个事件/2个所选上游形成观察，另活动固定选用；观察后继与上游修订传播。循环、遗漏闭包、自引用等完整PG攻击组未全部执行。
- V09 部分A级成立。透明SQL记录中memory-detail/list各11次execute、selection18次、workspace/history各25次；每面业务资格/正文快照SELECT恰1次，其余为超时设置和schema元数据，见 [sql-snapshot-evidence.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/final/sql-snapshot-evidence.json)。8个并发详情都观察到revision1完整前态、正文hash一致，没有观察到后态或源切换竞争，不称覆盖所有并发快照。
- V10 部分A级成立。root07同键回放，root09同键异内容409，root19同键同时首次保存及不同键同槽唯一效果、每键持久收据成立。COMMIT丢浏览器响应场景未执行。
- V11 部分A级成立。root09真正两线程同revision的不同修订返回200/409，revision2且原数据保留。最终浏览器双标签CAS未完成。
- V12 部分A级成立。root09 UTF8/重复键/字节/auth/跨站零写，root16普通app直写/DDL/SET ROLE/GUC及denied清理执行拒绝。全部伪关联/扩域PG组未全执行。
- V13 部分A级成立。root09 accept未claim后背景变动，原命令只读且0 SUP；root19有效persisted recipe同key恢复1 SUP，再POST只读确认0新增。GET不重发已claim未知，根源遵守原G8纪律。
- V14 部分A级成立。accept→launch失效有root09；root19 after-admit真实窗口未mark、0新007/派生事实、预留1/1000/0与原树零结算；root20已mark后拒新正文，外部UNKNOWN而operation先保留dispatched。root21原生record_outcome显式UNKNOWN诊断已提交，root22只读核state unknown、费用/次数不退、GET无新SUP。旧相同终态确认ALREADY_PRESENT仍可用。窗口组合未穷尽。
- V15 未闭合。browser03最终bundle已实际保存、刷新仅GET、同owner草稿身份核对及复制标签owner分离；三整批均FAIL，双标签修订/CAS后续、晚到切换、清引用、选用/删除、响应丢失、XSS和浏览器SUP场景未执行。脚本在第二标签详情未等待完成便输入，存在竞态推断；缺第二页输入值/DOM原件，不据此认定产品无缺陷。
- V16 部分A级成立。root19 workspace/record/command/007/list_operations/G7 seed/lc引用均无失效派生正文，seed/citation409，用户unknown答文仍读；root09不可变原progress未改，root16真实009行UPDATE拒绝。answer_reference全组合未补完。
- V17 部分A级成立。root19依赖失效、撤销正文仍在、已清理三个状态下清本活动mutable projection后原重建函数拒绝、nodes为空，原fact ID/hash不变。不是全库重建或STEP017验收。
- V18 部分A级成立。root07三版M3变0、M2留3；root16两版M3变0、M2留2、清理收据有效效果1、其它被比对表不变。最终canonical收据变化未PG验证。
- V19 部分A级成立。root16中途删除异常全回滚，墓碑revoked/pending、M3仍2；坏正文hash/清单缺版本/额外版本拒绝，临时同名对象不改变目标。错manifest见root09。物理缺正文、其它事务攻击和数据库不可读清理场景未全部执行。
- V20 部分A级成立。root03空001—009→010；pg2 14个旧表32行逐字段前后相等，含真实G8 v1及007模型正文/UNKNOWN，空010精确反向DDL39条且无外部FK。该007种子是普通账本合成结果，未冒完整G7学习profile。pg3坏CHECK/007列类型/009trigger身份/新表/角色残迹均失败全回滚。PG17.11/UTF8/core SHA真实；缺sha256分支NOT_RUN，不破坏pg_catalog。最终两函数新字节尚未迁移实测。
- V21 未闭合。缺memory配置/超容量0 accept、选记忆G7拒409；普通继续业务已拒但HTTP200映射漏项，末尾改409待实测。通用tool与合法教学calc、浏览器配置门没有完成。当前damaged schema分支保守关闭派生读面，包含legacy；角色/结构损坏时旧无选择路径的降级边界也未按V21闭合。
- V22 有限A级/B级证据。 [content-oracle-final.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/content-oracle-final.json)冻结原文SHA、实际lc位置与120米/120秒=1米每秒的支持判断；背景不增加引用。unknown答文真实support_checks为answer_status=unchecked、reference_status=matched，原件保留。root19原断言误取numeric_status，已改answer_status但未重跑；最终纯函数F01相关支持由离线实测补充，不能把原弱断言签整项。来源冲突/同名概念完整组合未执行，无真实provider质量结论。
- V23 部分A级成立。root22把本卡M1改名造成当前墓碑权威不可用时workspace失效/正文API503，前向恢复原表后仍revoked/无正文。只核当前在线库隔离/重开；最终M6及accepted-v2残迹守卫未实测，完整离线整库回滚检测/合并墓碑与备份器属于后续门。
- V24 有限A级成立。最后离线使用保留pre模块逐字节比较旧goal命令及model/tool frozen，hash相同；OneCall to/from wire限额实测。pg2安装/精确反向迁移前后旧v1读取成立。原G3—G8未改函数/文件范围继承，末尾fallback SQL与新增HTTP映射待补直接验证，不称全旧套件重跑通过。

主要组合原件为 [windows-v2-normal-result.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/windows-v2-normal-result.json)、[memory-boundaries-result.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/memory-boundaries-result.json)、[migration-upgrade-resume-result.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/migration-upgrade-resume-result.json)、[migration-fault-resume-result.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/migration-fault-resume-result.json)和 [root22组合断点](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/failures/root22-integration-resume-result.json)。最后组合文件为FAIL，不能用18个已完成性质覆盖其失败。

## DEF019及原证据继承

同单位直接保留原Decimal差异，1与1加10的负65次方分别matched/conflict；跨单位60m/min与1m/s用Fraction比例可靠比较；超过256位/指数支持域给unchecked。否定/未知答文、原F01实例去重/两个正确实例和辅助纪律定向回归有效。未做通用算术改造或其他政策改写，也未自行在共享账关闭DEF019。

原G8有限合同已验关闭、F01/DEF008及未变G3—G7停止/预算/原件等证据只按真实未改范围继承；F02—F09/E02/E01、DEF005和原项目Must未变。102文档指纹/批准包保持；102主动3122/10800保守、元数据300/600和未知、100修复04的1/3批及1.6463436离线/1779.265主动、101 review03的2002.341/180保守元数据和更早FAIL/漏5.940/未知均保留，不借余额。

## 失败与修正原件

31个受控执行的argv/cwd/时间/退出及as-run副本见runs-ledger；各次源码前后一致。原工具输出经过UTF8解码及脱敏，最早两离线批另有Windows写text导致CR重复，原落盘保留，不冒原始管道字节完全等同。每次真正失败计数未撤销。

- real01保存路径TypeError，内部SQL最终结果未成功落盘，未知不记0；real02定位010多余右括号42601，real03修复后七表/角色成功。
- real04发现活动memory_selection未投影，修SQL接线；real05清理pending，real06只读日志定位42702 revocation_key歧义；real07限定列名后正常清理成立，保留向前函数before/after。
- build01 JSX结构错误，build02修复通过；build03为最终工作区修正后通过。
- browser01读取编辑框超时；browser02初始列表尚未渲染便判找不到；browser03第二标签修正按钮禁用超时。03前的明确子步骤保留，三批整体失败且额度用尽。
- real11旧种子夹具把ActivityLease.execution_generation写成generation；real12从已有v1事实断点续作，不重跑3 SUP，完成升级/反向DDL。
- real13坏列样本bigint与旧octet_length CHECK冲突，改varchar；real14 ALTER TRIGGER语法错误，修明确语句；real15在空teaching表UPDATE没有触发器效果，real16补真实行后权限/清理组合成立。
- real19两项count无别名被dict_row覆盖，修别名后仅从断点核剩余；real20原状态语义误期待已自动persist unknown，保持原协议并核显式诊断；real21诊断已COMMIT，证据Datetime序列化失败，修证据转换；real22核旧诊断/恢复成功后继续DTO夹具缺new_operation_id；real23工具续作误引用未绑定old_aid；real24更正夹具后发现真正HTTP映射漏项。所有原异常在runs及failures中保留，实际诊断与已有事实没有重新启动模型。

最后known缺口不是以“fixture错误”免除验收；原弱断言、未取第二页DOM、未完成tool以及末尾SQL/HTTP变更都列为真实未验证。

## 配置、账与资源收尾

各根启动前计数并冻结实际源码，原first_read_utc为2026-10-06T05:57:35Z；start_ns=537666346814000，deadline_ns=566466346814000，首读映射另保守扣60秒。全部读取、编码、失败、中断等待及封装计入该主动窗口。封装尾段值见 [accounting-final.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/final/accounting-final.json)。

次数为offline4/6、build3/3、真实根24/24、container create3/3、volume create3/3、start23/24、监听进程3/12、SUP16/64、browser3/3、driver3/3。没有再启动下游。离线与构建合计15.453秒；真实保守539.251秒，独立清理22.018秒，封装前元数据保守360加已测辅助，未知精确细分保留。真实内根与外Control.run有重叠保守重复计时，不能据此退额。

合成配置使用缓存实际PG17.11和UTF8、指定镜像ID，memory容量4项/4096bytes/2048chars与固定受控model identity；模型、用量、价格均为合成值，非供应商测量或真实扣费。SessionConfig的W20/请求2/grace2，原默认startup5/manager_db5/cleanup5/mutex3/manager_overhead30、single_host恢复声明false冻结在脚本，管理上限实际50秒且不超过卡面120秒。现有监督链把lease_seconds绑定window_seconds，真实SUP lease为20而不是卡面建议60；普通低层pg2旧账本种子lease60。没有为此改worker协议/监督主体，偏差未冒满足，后续复验须由编排明确沿用真实类型口径。

三个新实例全部保留停止，CID分别为

- pg1 4889202d9a58c622fb7cd2bd3087e5bceb7ad20a049c6550f4bd3588ff66ac11，卷retrolume-task-103-g9-pg1-data。
- pg2 f96ac8dcb64648c76a2bc70f3f8b75969ada0ea0ea69b5896fe5ecb71affab85，卷retrolume-task-103-g9-pg2-data。
- pg3 4b813f9e4317aef9c613eb140fcb2d40c55a6bd98ee5d79807ea5851975d7f68，卷retrolume-task-103-g9-pg3-data。

最终只读核Running=false/Pid0，镜像/标签/卷、1CPU/512MiB/pids128/restart=no/非privileged一致。55443—55445、18103、18104均可绑定；三个自有应用停止，browser context在finally关闭，16个SUP的32份manager/worker PID出生见证均无原身份运行，原返回树计数0且cleanup_incomplete=false。详见 [resources-after.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/final/resources-after.json)。没有删容器、卷、数据库、原件、profile或合成事实，未停其它进程。服务被明确终止的Exit1不冒正常Exit0。

## 可执行的下一断点与审计输入

首先保持当前源码/证据冻结，本许可不再启真实根或浏览器。编排在同TASK/R及全部历史不清零的前提下明确下一段许可/预算，不把本结果当稳定候选或先签审计。

下一段优先按最终diff向前更新并验证两个010函数及缺M6/accepted-v2残迹、普通继续409；复用已确认M1/007/009事实、CAS/清理故障和原Windows收尾证据，仅补差异。补合法选记忆教学calc和通用tool拒绝。浏览器先修实际详情完成/身份确认的等待与第二页取证，再一次集中覆盖固定选择、修改/CAS、撤销/原清单重试、丢响应、晚到/清引用、XSS及实际服务器SUP。不要机械重跑全部过去场景或重新创建已保留的PG实例。

还应补未闭合的PDF记忆传播、关联后继/无关事件、闭包攻击与源切换并发等性质。当前B1—B8/C1—C3源码接线不能签全部完成；缺口有明确最终文件及已执行样本，不需要用户提供密钥或用户库来推进后续合成复验。

稳定完整G9后才由编排给一次隔离增强独立审计。输入为批准102合同/澄清、103卡面、本结果、最终post/hash/diff、31次as-run/输出、组合checkpoint/failures、PG迁移/角色/清理原件、SQL快照记录、最终bundle加载原字节链、资源/预算账。待同步的唯一执行动态、架构/CHG/DEF由主控维护，执行者未代写或自占号。
