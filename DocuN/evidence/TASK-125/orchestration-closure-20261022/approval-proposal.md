# AP-125-NORMAL-INSTALL-01 关闭外发的本地真实安装验证采用包

状态为待用户采用，不可执行。本包只提前把后续新资源、写入及验证边界列完整，不占新的TASK/R，不创建资源或恢复旧运行许可。当前TASK125离线工程与TASK126代码门已由主控关闭；真实安装和Q从未因此获得执行权。

## 本次需要的一项决定

是否采用下述一个合并包，授权新建至多两个彼此隔离的本地PG容器及独立数据卷，使用已独审的正式安装器执行新空库001—015和角色创建，完成首轮独审规定的六项真实检查，以及主正常库的关闭配置启动、同库重开和停止。全部合成、零外网模型/Embedding/费用，不涉及旧库、用户资料或用户库。只有此一项决定，无新的模型/供应商/业务或费用取舍。

之所以需要确认，是原125/126执行合同的PG、容器、角色和实际apply均明确为0；公共AGENTS第2节还要求权限调整等高影响动作有覆盖对象和范围的明确授权。代码门通过不是新资源或DDL/DCL授权。批准后主控才按本包登记下一正式任务卡并给执行许可，不让工程者凭本草案开工。

## 固定对象及资源上限

只使用本机已缓存并核对的pgvector/pgvector@sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f，不拉取/构建/升级。目标PG17、vector0.8.6；首次预检不匹配就带回实际差异，不能换镜像碰运气。

两个槽位串行运行，任何时刻最多一个PG容器活跃。

- source槽位，容器retrolume-q-first-normal，卷retrolume-q-first-normal-data，逻辑库retrolume_q_first_normal；Compose项目retrolume-first-install-source。它是未来正常源的持久安装候选，先保持所有外发关闭，不重建或换库重置任何未来预算。
- interrupted槽位，容器retrolume-install-interrupted，卷retrolume-install-interrupted-data，逻辑库retrolume_install_interrupted；Compose项目retrolume-first-install-interrupted。只作真实SQL一次提交未知/中断保留验证，不作为可运行正常源，不自动续装或清空。

每槽位至多一次容器创建尝试和一个专有新卷；若名字已有对象，先只读核归属，非本次对象就停止该槽位，不覆盖/删除/接管或静默换名。最多两个Compose专属bridge网络，不使用host网络或host bind。CPU1、内存512MiB、pids128、restart=no、仅127.0.0.1映射、pull_policy=never。使用既有deploy/compose.local.yml的pg服务，两个项目隔离；不启用renderer-build profile、不构建或启动预览。未启用预览变量如需Compose插值，使用明确无激活作用的本机占位，不读取旧私有预览配置。

source的PG端口按顺序在55482、55484、55486中只读检查并短时bind核可用后一次选定，interrupted在55483、55485、55487中选定；本地API在18122、18124、18126中选定。只选择已批准候选，选定即写本任务身份账，不因后续失败轮换端口绕计数。没有可用项则停止相关段，不改Windows排除范围、不重启宿主网络或Docker服务、不结束他人进程。

新私有根仅D:/shspic/project_NO3_RetroLume-agent/.runtime/normal-first-install/source及interrupted。source内分别建立独立data/backup/control/restore、私有安装/原生关闭配置和新收据目录；根须原先不存在，拒绝已有归属不明、junction、重叠和越界。既有.gitignore已排除/.runtime/，不将凭据或实际私有配置写进可公开证据。

实际CID、卷/网络ID、选定端口、system_identifier、数据库OID、当前Windows SID和根device/file-id只在获准创建后读取并绑定；未发生时为空，不能在本草案伪造。三个安装UUID由受信新根绑定产生并一次记录；应用身份与正常控制行保持同一来源，不造Q InstanceBinding或grant。

仅新集群bootstrap管理员用于短时安装；source登录固定为retrolume_normal_app与retrolume_normal_snapshot，interrupted预定retrolume_interrupt_app与retrolume_interrupt_snapshot。两个新集群的13个NOLOGIN职责组由原001—015按原文创建，登录通过已审权限分工创建，不给业务管理员权限，不复用或修改任何旧集群角色。随机密码/维护秘密只经安全stdin或进程环境注入，无值进入argv、日志、证据或报告。禁止输出docker inspect Env或Compose展开后的凭据配置。

## 六项合并检查

1. 同一source新空库的精确错误OID/system_identifier拒绝，以及非空/职责组碰撞拒绝。允许在这个本次新空库建立并精确撤销public.retrolume_install_probe_nonempty表和retrolume_data_app NOLOGIN碰撞组，先记录它们原本不存在及创建OID，只撤销本轮同身份对象，不清空库、不碰别的对象。反例每次用独立拒绝收据，确认真实入口命中对应原因和零安装器数据库写；先关闭旁观元数据连接，不能所有反例只命中other_clients就冒充覆盖。
2. source空库用正式deploy/initialize_normal.py真实apply，原样执行001—015，观察013后R01、014/R02、015/R03、原schema/role验证及37条完整成功收据。可用测试连接包装器观察真实COMMIT后的阶段，不替代SQL或核验函数。安装器代码冻结为29403字节/hash68d7b71fc7296111e894df4cba21a4ed7830f9cff069c1fc500dfbd7734c0a09。
3. 同库分别用新业务/快照真实登录，核权限、控制行和实际可读性；用真实权限查询或有界事务拒绝检查，确认snapshot不能业务写、读维护秘密或SET到业务/owner，业务无管理/owner/传递SET/INHERIT/ADMIN越权。不重跑旧全安全矩阵，不给应用安装管理员连接。
4. 使用现有start_local.py的--container、--port、--shutdown-stdin和原生配置，关闭model/integration/Q/preview，建立真正normal源绑定与ControlHub，仅启动一个本机API。读取实际capabilities/readiness，正常停止后用同一库/根再开一次，核无自动迁移/新身份/重置和原记录不变，再正常停止。无需浏览器、业务worker、模型、索引、活动或付费账。关闭配置的真实部署可在账号/token等待期间独立验证，但不冒称Q外部门通过。
5. interrupted槽位真实执行同一原SQL，在事先固定的002提交应答边界制造一次提交未知。包装器必须先真实执行并提交该SQL才隐藏一次确认；记录真实DB状态与001已确认、002 submitted/unknown、无003/complete/自动重放。原收据重用和verify在本地拒绝，新收据对部分库也应零写拒绝。保留部分库和卷，不续装、清空或退款。
6. 回source成功库真实verify，仅注入安装管理员密码引用、不提供另三秘密；核READ ONLY、schema/roles/身份和收据不变。错误收据绑定在连接前拒绝。各步骤共享身份和检查点，一次合并回传。

## 资源、失败与停止

低内存明确采用本包的串行门，不恢复一般2GiB要求。Docker已可用后，每次启动PG或API前可用物理内存至少512MiB；约2秒采样，连续两次低于256MiB时停止新动作并有界关闭本任务自有API/PG。不要求用户反复释放内存，不启用浏览器/renderer/第二活跃PG。

总工具最多10800秒含900秒保存/收尾，获准正式签发后日历24h；PG累计持有最多1800秒，API累计持有最多900秒。PG source启动最多4次，interrupted最多2次，API最多3次，其中source安装/正常开/同库重开为既定需要，其余只能针对具体有据修正。至多一个合并初验入口及两次只恢复失败/未完成段的有据续验；不会为文件读取、未执行的审批拒绝或单方法拆根次数。准备和入口失败如实留账，不把失败清零。

新建容器/卷/网络/库和反例对象的授权仅覆盖上述固定范围。所有成功对象和失败卷保留，收尾只有精确CID/创建ID核对后的停止和本卡API树关闭，不docker prune、不compose down -v、不DROP DATABASE或清理旧资料。本包不允许重复创建同槽位、换名重试、重置角色密码、扩内存、拉镜像或改系统。已完成阶段用原始检查点/受测版本证据继承，不能因重开runner重放DDL。

先离线准备完整runner和身份/预算/原始日志控制，再一次进入真实段；不因切到下一正常步骤就回传。若纯测试夹具明确出错，保留失败并仅修本卡验证夹具，在预算内定向复检后继续余段。若发现产品确定缺陷、安装器未知提交、同根因两次有据修正仍失败、需要扩大权限/改SQL/新平台或限额到门，则停止受影响段，完成不受阻项后一次回传。不承诺未运行必过，也不再用大量小续卡机械重试。

## 绝不包含的授权

Q仍关闭，T0/72h为空，不创建三固定业务活动或grant，不绑定QAuthority，不索引/查询/生成，不访问真实provider或Embedding/计量接口；100次25元及分额原封不动。无网络下载/依赖安装/镜像构建/浏览器/业务Job/HTML预览/用户资料或用户库操作，Git写入为0。现有两个provider与计量/账号/token/模板/容量外部缺口继续保留，不以真实安装成功代替。

不修改已审安装器、001—015、业务app/角色/profile/Grant/现启动入口或正式Compose。实现/验证辅助脚本只属本任务证据，产品运行继续走正式工具。可按真实已验证结果最小更新README和normal-install.md的用户说明，不预写通过。独审已通过的未变代码不再审一遍；主控核最终真实原件，新增安全差异才决定相应集中审查。

批准本包只使上述关闭式验证具备授权依据。主控仍需登记正式任务及启用范围后，用户再转交原TASK125工程窗口；本草案本身不执行。完成不等于STEP018/019/020、M1或项目通过。
