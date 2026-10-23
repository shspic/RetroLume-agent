# TASK-125 / R-119 工程结果

## 本次结论

已完成正常首次安装工具链工程候选：新增正式安装入口、001—015固定原件清单、默认关闭的安装输入示例、运行说明和18项离线方法；README仅修改第33行。第二批18/18通过，首批夹具失败及普通自查修正均保留。最终六份产品字节与第二批受测摘要一致，接收时61项输入除获准修改的README外均保持原字节。

交付层为本地工程及离线验证，待主控核收。没有执行真实安装器CLI apply，没有连接或查询PG、创建数据库/角色/容器/卷、启动服务、调用供应商/Embedding/计量服务或写Git。没有生成实际实例、活动、模型结果、grant、operator批准、激活回执或T0。本次记录器调用内部apply控制流只观察本地顺序与停止分支，不证明真实PG安装、事务、ACL或正常启动成功。

首次真实apply前的一次安装迁移及角色权限独立审查尚未进行，正常部署及启动组合动态验证也尚未发生；本次普通自查不代替独审，不签Q启用、STEP018/019/020、M1或项目通过。

## 实际产品差异

项目根为D:/shspic/project_NO3_RetroLume-agent。接收时五个新增路径均不存在，README原字节已存pre。变更仅为以下六份产品文件，以及本卡execution证据和本结果。

- [initialize_normal.py](D:/shspic/project_NO3_RetroLume-agent/deploy/initialize_normal.py)：默认仅帮助；plan纯本地核验；未来显式apply只支持独立新集群已创建的全新空库；verify只接受同一完整成功收据后只读核验。固定原件、关闭模板、严格输入及逐级路径检查均先于连接。未来只读预检拒绝身份不符、非空/非独占目标、已有全局角色或不适用版本；013后插入normal/R01控制行，014推进R02，015推进R03。两个分离的新登录按既有NOLOGIN职责组、INHERIT TRUE/SET FALSE/ADMIN FALSE授必要权限，并复用schema_checks/schema_profiles/q_roles的现有实际核验接口。逐阶段收据保留确认与提交未知，无续迁移、重放或清空路径。
- [normal_install_manifest.json](D:/shspic/project_NO3_RetroLume-agent/deploy/normal_install_manifest.json)：按固定顺序锁定15份原SQL的原字节大小/hash、R03目标、PG17/vector0.8.6、职责分工及四份关闭原生模板摘要；清单原字节摘要同时冻结在入口。仅utf-8-sig正常解码，不改换行、正文、角色碰撞guard或事务边界，不吸纳未来SQL。
- [normal-install.example.json](D:/shspic/project_NO3_RetroLume-agent/config/normal-install.example.json)：安装器自有retrolume.normal-install.v1输入，不冒称应用loader支持。enabled=false；身份、端口、两个登录及runtime_configs均未绑定，只列四个未来安全环境变量名，不含凭据或维护摘要。
- [normal-install.md](D:/shspic/project_NO3_RetroLume-agent/deploy/normal-install.md)：记录真实帮助对应的plan/apply/verify参数、关闭结果、未来输入、分阶段失败保留、独审及运行门；区分旧001入口、完整首次安装、只读复核和原正常启动。连接端保持loopback，服务端实际地址及端口允许容器映射并如实记录。私有副本要求放项目外受信位置，不误称新配置路径已被Git忽略。
- [test_normal_install.py](D:/shspic/project_NO3_RetroLume-agent/backend/tests/test_normal_install.py)：18项定向离线方法，包含实际Windows junction入口拒绝及既有纯角色检查样本。记录器不执行SQL、不模拟为真实PG事务结论。
- [README.md](D:/shspic/project_NO3_RetroLume-agent/README.md:33)：只替换一段，说明旧入口仅001，链接新完整工具及未来许可/独审门。其余原字节和换行保持不变。

未修改backend/app、15份SQL、start_local、initialize-materials、compose、现有原生配置示例、依赖、前端、DocuS、公共规则或旧证据。产品运行无tests、DocuN、个人绝对路径或公共提示词库依赖；测试及取证脚本可使用本卡execution scratch。

## 定向验证与原始证据

证据根为[D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution)。未重跑TASK123原13方法或旧055/074/079/120 runner。

第一批命令为现有backend/.venv/Scripts/python.exe -I -S -B，执行本卡run-offline-batch.py。子进程完整argv、白名单环境名和隔离方式在[batch-01-command.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/batch-01-command.json)，原输出在[batch-01-output.txt](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/batch-01-output.txt)，逐方法时间在[batch-01-summary.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/batch-01-summary.json)。退出1；集中进程wall为1.7728173999930732秒，测试器内wall为0.5608052000170574秒；18项中17通过，1失败，error/skip均0。

唯一失败发生在test08的原生junction夹具创建，尚未进入安装器拒绝断言。[junction-diagnostic.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/junction-diagnostic.json)记录DeviceIoControl的WinError5。经工具自动审查获准，仅在本卡scratch/junction-fixture内用New-Item创建link指向同目录空target，无越界或服务动作；没有自动审批拒绝。测试随后可显式读取该预建夹具，在原沙箱中执行真实入口拒绝检查，未用假的lstat结果替代。夹具留在本卡scratch，没有递归删除或清理用户资源。

普通自查另发现最初将PG服务端地址固定为127.0.0.1会误拒绝容器NAT；在第二批前修正，host仍固定127.0.0.1，system_identifier/OID/数据库/管理员身份仍严格核对，记录服务端实际地址和端口。顺序样本使用172.18.0.2:5432对应主机55464，不将主机映射端口当服务端监听端口。修正说明在[correction-01.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/correction-01.json)。这是本地自查发现，未发生真实安装失败。

第二批命令同上，改为本卡run-offline-batch-02.py及其冻结harness。完整记录在[batch-02-command.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/batch-02-command.json)、[batch-02-output.txt](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/batch-02-output.txt)和[batch-02-summary.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/batch-02-summary.json)。退出0；集中进程wall为1.0162982000038028秒，测试器内wall为0.4948959000175819秒；18/18通过，fail/error/skip均0。两批均无网络/连接/子进程/应用运行时审计阻断事件；实际PG及网络操作均0。

实际覆盖如下。

- 默认、真实argparse帮助、坏参数及plan不读取凭据环境、不连接、不调用子进程、不导入应用/控制运行时；重复plan保持缺项、观察身份null、不写安装收据。
- 缺SQL、额外SQL、清单重排/增项/hash变更、SQL原件漂移、错误profile、非法标识符、身份重叠及runtime启用拒绝；排他输出冲突不覆盖，..、源码输出、NTFS流/设备别名和真实junction拒绝。
- 显式apply须输入完整且开关打开；记录器观察READ ONLY预检先于所有写请求，身份不符/非空/角色碰撞/vector版本不符均零写请求。原链顺序、013后控制行、014/015后新登录及最终只读核验边界均有观察。
- 002响应丢失样本保留001确认、002未知，不尝试003；同收据再次apply立即拒绝，部分收据不能verify。完整收据仅只读复核，核身份与原观察且不改收据，不读取另三份秘密。
- 既有check_role_capabilities接受分离业务/快照方案；拒绝传递SET、INHERIT管理权限、ADMIN、owner以及快照跨业务写权限样本。生产verifier复用现有schema/profile/role核验接口，纯样本不能证明实际数据库权限成立。
- 收据及错误无合成密码、DSN或维护摘要；产品无测试/证据/个人路径/公共库依赖；说明参数与实际帮助及原启动参数一致。

测试仅用标准库及现有已安装psycopg。父测试启动器只读取必要系统变量，PATH明确重建；不读取或继承实际provider key、DSN、私配路径、旧PYTHONPATH或TESTONLY注入。-I -S阻止用户site和sitecustomize，随后显式加入现有backend及venv依赖目录；-B避免pyc。测试内凭据全为合成哨兵，实际生产凭据未读。未安装依赖或联网。

## 冻结字节与保存位置

以下六份摘要均与[第二批受测前快照](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/tested-before-batch-02.json)和[post-snapshot.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/post-snapshot.json)一致。

- deploy/initialize_normal.py：28872字节，SHA256 e112ce498f73371e6d788ed834c4c0414f3c8728579ec1ddc9df6c4942ffce5d。
- deploy/normal_install_manifest.json：4325字节，SHA256 f2ed126daa1c5a982b490a9343d6c17053c0f385e7a2f55676ecf4132dd2abf0。
- deploy/normal-install.md：10496字节，SHA256 dc46e05bb8e01873c5ce359a9d2665d57e27e4c9a5d89c11ade18fd4128c61cc。
- config/normal-install.example.json：869字节，SHA256 95c97092a95fd39b116fe4e85fd4d5d4c7bb6757fc45efe76cc600863b55df3b。
- backend/tests/test_normal_install.py：26021字节，SHA256 ca2fb5fa09776a73e6e8983dd2a47f9be399dcc141ea196f31ec8a6cf69e4633。
- README.md：27130字节，SHA256 7ebb7d680949ce10c9c63f2e31b26f318145eba3309ab42e1891783526602db8。pre为26915字节，SHA256 0410c7573027f7f6e75635c3a8d050e2be375d98ab0a4b503ddf3e076104d938。

[pre-snapshot.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/pre-snapshot.json)记录五个新增文件不存在、README原件及61输入pre hash；pre/README.md保存原字节。post/按项目相对路径保存六份最终副本。[changes.patch](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/changes.patch)是相对本卡pre的统一diff，不混入接收前Git改动；比较文本时统一行终结符用于展示，原字节单独保存。[source-preservation.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/source-preservation.json)确认61输入无意外变化；README仅第33行有字节差异，其他行及原换行原样保留。

## 输入、规则与继承

入口[AGENTS.md](D:/shspic/project_NO3_RetroLume-agent/AGENTS.md) SHA256 b5288a35dd6281a2253ebaceab61ac37a72e7e55d41b2724044fa2479c5c07f1。模式task_model，V4.0，公共AGENTS CHG-0003；沿原窗口已读规则，七份公共锁定文件当前hash全部与rules-snapshot.json一致，不采用后续版本。具体绝对路径、七份指纹及当前输入在[rules-and-inputs.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/rules-and-inputs.json)。当前合同采用需求v1.4、架构v1.65和执行动态v2.93的相关范围，不维护第二份总进度账。

TASK125卡SHA256 10a1ce45367f50045faca8393d67fe32aacfc5df1653b97e2fa377c4b0e3e0a5；input-manifest SHA256 664cd7ef5ae35cf63665dece24e0deea62e47d21584ef926bdad16859833302e；permit SHA256 8f6542b2a246334c3b2b531d981800dd2984af76fe5dac7c20002365608091bc。许可签发为2026-10-22T09:12:14.276888+08:00，截止2026-10-23同刻。本轮资源A+为任务标签；实际使用Codex桌面工程窗口，系统说明为GPT-6家族，具体后端变体未可见，不捏造。未派子Agent，未使用原TASK124独审窗口实现。

当前唯一有效关闭交接为TASK123/execution/correction-01中的deployment-handoff.md及finite-inputs.json，分别SHA256 8ece65467fbc9c1ec59b0878c8dbf9564a9605324920c140d19c8879979e5f79、79e843d4ccad235c85d24e01cd508160597cb0196baa56e686f9f96d8da0b1e5。[主控关闭收据](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/orchestration-closure-20261022/closure-receipt.json) SHA256 5c8334a9977333c42a50e32c5764918de08aa4030ee0fe6a1b44e763393dcaf6，已经PASS_AND_CLOSED并关闭F124-01。沿现有evaluate→progress.reason保存理由，没有新接口、迁移或correct映射。

复用TASK123原代码/13方法与TASK124独审已接受范围，原报告不改；TASK120/121原迁移/profile/权限证据仅沿原适用对象继承，不扩张为本卡新正常实例已验证。TASK122 runbook/deployment-package/readiness只供配置准备参考，不是本卡执行许可。

TASK120根/PG64/64、149失败及旧TASK117的81失败保持原账；TASK123保守3710.557411/7200秒及3/3批已封存，TASK124已结束，历史预算不恢复。当前Q未启用、T0=null及真实调用费用0沿主控有效声明继承，本卡不扫描私有根以另造实时外部验证。100次/25元、48/28/24分额、28Must/89动作/24片/6索引均未改变。

## 失败、预算与偏差

[command-ledger.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/command-ledger.json)保存可恢复工具wall/退出、完整批次命令导航及定位错误。前期曾误猜manifest键、两个迁移文件名、activity配置复数名、Git状态独立文件名，以及PowerShell通配路径；均为只读定位错误，随后按实际结构补读。长输出有截断，按目标片段补读，不将其记为产品通过或隐藏失败。

本卡新功能批2/3已使用，单批均远低于600秒；新测试失败总计1，已修正且原件保留，第二批新失败0。原生夹具WinError5诊断不是PG失败。初版NAT误拒绝为普通自查修正。无同根因两次修正仍失败、关键方案推翻或范围扩张。

工具总wall无法从全部早期调用逐项精确恢复，记unknown；不将两批实测进程秒数冒称完整工程投入。按许可签发至封存首小时范围，对已恢复短命令、文件修改及未逐项持久计时部分保守列支3600/10800秒，含收尾，未动用900秒保留门。封存早于2026-10-22T02:12:14.276888Z且远早于24小时截止；账面余量7200秒不自动变成后续任务许可。实际预算事实与包络依据在command-ledger，不复用旧任务余额。

唯一额外平台动作是为实际junction用例创建卡内空夹具，经工具审查获准，范围未越过本地离线文件操作；无审批拒绝或待用户操作。其余偏差均为卡内普通修复，没有公共规则、DocuS或冻结源码改动。

## 留给主控的收口与后继输入

主控可登记六份候选文件、两批离线证据及当前失败关闭情况，安排一次首次apply前独立风险审查，并在唯一执行动态/必要CHG中串行同步；本执行窗口未代写共享状态或裁定STEP完成。

后继真实运行卡仍须给独立新集群/数据库及容器/卷的精确资源身份和边界、实际system_identifier/OID、端口及短时管理员、三个安装UUID的来源与根绑定、两个新登录、受信私有配置/新收据路径、安全环境注入方式、真实运行额度与停止证。工具不创建这些资源；独审通过及精确运行许可后，才可调用已实现apply并取得PG原件执行、R03/角色、应用关闭配置读取、正常启动/同库重开/停止的真实组合证据。

四根/ACL/file-id、账号计量/分词/模板/Embedding容量和其他Q外部门继续保持原精确缺口，不重复试跑或研究。本卡不需要用户提供key、开服务、清内存或清理资源。工程结果和证据已保存，交主控核收。
