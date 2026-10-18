# TASK-109 / R-103 续作02 — 直接运行已构建镜像的最小真实诊断

## 目标与交付

你继续担任原109执行者。OCI导出/构建/加载已经有成功原件，不再save/build或更换镜像。本轮只补一个被控制误判截断的完整动作：核验现有immutable image → 创建/启动一个受限preview → 实际Node/browser/sandbox、可信手势新页及自身导航最小诊断 → 精确停止与回传。

仍TASK109/R103，结果置顶 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-109-result.md，标题续作02。当前27219字节/SHA 692c6dcea596315047983a2b7a23447cd6510aa72495a7f6844fc3560e12617f保作新前缀后原字节历史，内含原15176报告不改；新原件 DocuN/evidence/TASK-109/execution/continuation-02/。旧R01/R02/R03、session、cache/OCI、build logs/metadata/镜像与as-run全部只读。

完成标准是取得确切真实层：加载环境成立或具体失败；动作真实触发及引擎观察；首个权限反证/未确认；资源收尾与最低后续改变。当前固定镜像是诊断器，没有生产NavigationGate，即便无反证也NOT_FULL_H0，四表/PG/profile/模型/API/UI业务继续冻结。不能靠改终态、metadata表示或某个display字符串签B-01/SEC003/G11/M-1/项目。

## 项目、规则与接收安排

根 D:/shspic/project_NO3_RetroLume-agent，入口同根AGENTS.md。task_model/V4.0/公共AGENTS CHG-0003，需求v1.1、架构v1.04、唯一执行动态v2.26，阶段07。公共根 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4；同窗已读未变正文复用，补本卡/新裁定，七指纹仍项目v4-migration-20260930/rules-snapshot.json。新增文稿/注释简体中文、不用星号/表格，旧历史保字节。

接收A+，沿实际109原业务窗口，保实际客户端/模型与旧失败/预算；107不实施/不泛审未实现候选。G11-P仍已采用，普通控制修正和复用本卡镜像无需重复采用批准，本卡不授权新组件/新引擎、页面或系统权限。

原累计73真实入口不是73PASS；109 root3/8、H0已修订3/3、imagebuild2/2，R01/R02 FAIL/R03 ERROR保持。R03 build exit0/image成功和root误判分层，C01 root53.922秒含save30.172/build2.438，累计real81.141含累计build27.017；C01 active1693.1上界/metadata600保守/cleanup30保守/offline0.297、首轮2700.7重叠/4官方页/H0研究1535.6、13元均保留，不能以成功子事实返还根。

补充action许可TASK-109-G11-C02-20261009，新增根1/preview create1/start1/controller1，save/build/SQL/app/native/model0。计原总root8/preview16/controller2，H0累计3→4；首读固定≤1800秒子窗，原start774301594189000/deadline795901594189000不改，不越原总截止。过期禁止新真实动作，只保存不受阻准备；原许可名义余额不自动运行。

## 背景与最小充分上下文

只读原109续作01的registry-classification、proposed-control-fix、root03/build metadata/loaded image/OCI-identity、as-run/source-diff及已构建host/counter/原观测协议和监督救援。491基线中8允许差异和2新源，当前493对象匹配；363旧业务保护对象未改。完整输入在 DocuN/evidence/TASK-109/orchestration-continuation-02-20261009/continuation-input.json，不全文重采108或旧官方研究。

真实build source是命名oci-layout context和唯一pkg:oci/task109_cached_base material/c091 digest，日志“OCI load from client”。docker.io/library/task109_cached_base和image tag标准化展示名不是网络请求；buildType文档URI、VCS属性也不能作为registry访问。原R03错误guard照实保留，不能再执行这一build链/guard使当前image再次被误拒。

基础ID在本机是OCI manifest c091…，引用config fee853fafa59550d162cef52bca02d907694b44ebf6ef9fb075bcc0c65d8dedb及七层，严格原字节/hash/rootfs顺序链已验证。前卡“config==基础ID”的字面要求在此类型下不成立，本轮按实际descriptor类型绑定，不能虚写相等；这只是标识类型澄清，不更换基础或layer。

直接使用派生manifest/image ID sha256:aa824fa25eb0aae09cee50c10372fb218a7d86ffb10124b46074a5c1e977cc66，config sha256:e881d12c9e682de7e535386b9db353bfc95838c3bcea04332bcdffd9cc30e6ea，linux/amd64、User10001:10001、entrypoint node /opt/preview/h0-counter.cjs。tag retrolume-task-109-g11-h0:c01只是导航，create只传immutable ID；不重新load/save/build/改tag/复制包或修镜像内host/counter。

主控已经只读核镜像实际descriptor、User、entrypoint/labels与构建原件一致，本卡容器/18109-55449监听为空；这是观察时点，执行前重核，不创造“浏览器已加载”。归档/layout/成功构建/111包和117输入的身份复用，不重复GB级导出或整体解压校验来消耗窗口。

## 执行边界与资源

只写本轮新fixture/控制入口backend/tests/fixtures/task109/中的h0-run-loaded.py等明确必要文件及本轮证据；必要受信Python控制帮助函数可最小参数化并留diff，默认backend/app/preview原protocol/supervisor/reaper保持。不得改镜像内JS/wrapper/seccomp/包/版本/权限或镜像内容，save/build/newimage0；旧h0-root和c01入口/计数/日志只读，不绕len上限或追认结束根存活。

新入口从现有已读根的create/start/read/cleanup段提取必要真实控制流程，删除export/build和错误registry display-name分支；直接引用主控核定image/config及已保存metadata。可另保存一项纯离线证据分类核对，使用R03真实metadata/成功日志与一个确实remote source的拒绝反例，不从通用字符串、HTTPS说明URI推网络，不能把这项check写成browser测试或重新build。

一次源/控制检查把全部实际同链前置确认：阶段area/action permit/R04与累计74、ROOT路径/JSON类字段、base/image manifest和config的不同语义、现有readonly白名单/tmpfs表示、metadata8秒/create15秒/有界inspect、UTF8输出、前计数/截止、包分片有序及16KB/hash/队列上界、events和reaper ready/bind/parent出生、异常finally。纯compile/syntax≤一个60秒offline批，仅本轮变更控制源，不重跑JS语法、原G10或缓存构建。

唯一容器名 retrolume-task-109-g11-preview-01，已确认尚未存在；若出现冲突，不改名盲跑，先核实际归属，不碰别的实例。label保持TASK-109/原permit归属，action-permit为C02、phase H0-C02与随机nonce，创建即冻结完整CID/image/label/flags。旧image的action-permit=C01是构建出处，不给新运行许可，也不要求重建成C02。

create明确pull=never（本机支持的语法先核），镜像缺失或身份/源码映射不符即停，不拉取。所有原约束保持：UID10001、networknone、cap-drop ALL/no-new-privileges、read-only、restartno/init/CPU1/768MiB等swap/pids128/privateIPC/SHM64MiB、固定有限tmpfs、无hostbind/socket/port/secret和真sandbox；不加root/no-sandbox/SYS_ADMIN、不增PIDs/Mem、不换版本或seccomp解决启动。

新增真实根H0-R04最多1/≤300秒；create最多1/start最多1/preview runtime≤60/诊断≤15/controller≤1。metadata≤300、offline≤60、独立cleanup≤180秒，首读子窗≤1800且不越原总截止；新研究页面0，bootstrap/官方源码/旧包证据同窗复用。原累计preview0/controller0，本轮新实际开始后才累加；其他root/JS重测/build/包导出/PG/API/main浏览器/native/模型/费用/安装/Git0。所有预检/失败/未到browser也计本根，不开第二根/第二容器。

秘密和运行应用凭据不入此容器，stdin/stdout只有受控测试协议；raw完整inspect只内存解析并白名单持久化，Env不输出。原OCI/cache/image/原件以及新container停止保留，无rm/prune/DROP/DELETE/旧106103100088资源启动/系统时钟或daemon/store改变。

## 验证、证据与审计关系

本轮用途是一次有辨别力的真实诊断，不是现有无同步守卫的产品放行测试。先实际Node/package/binary/Chromium版本/argv/UID/sandbox/进程namespace，再正对照与受限新页，然后自身data/blob/hash/child，按冻结镜像原counter首个反证即停。固定JS动作与2秒观察代码已经入image，不能在controller里伪造“触发/拒绝/成功”。

原bytes/as-run→successful build/material/manifest→actual image/config→create参数→real Node/browser观测完整对应。分片包逐seq/hash/长度还原原observations，records/packets原件保存，丢序/截断/observer缺失视未确认，不能靠root exit0补PASS。若browser startup因环境/sandbox失败，记录准确层级，不叫导航反证；若真实URL/loader/document/新目标发生，记录第一因果动作后止，不跑余下全矩阵。

即使探针没观察变化，counter末态NOT_FULL_H0仍如实保留，缺生产NavigationGate和完整安全证明，不写PASS_FULL_H0、不进入业务或安排110泛审。popup对照/受限form的触发与拒绝层不同，trusted input、受控页面辅助标记及独立引擎集合分别记；没有真实触发不PASS。容器内自己的提示/console仍不是命令，不能授予宿主工具权。

诊断后有真实关键反证时，同轮最多给一页必要最低差异：哪项原必须性质不成立、现有固定组件缺哪个实际锚、对原G11的影响、一个最小推荐处置及需改变的schema/信任边界/组件/成本。可以提出数据驱动的受控生成或具体原生拒绝层等方案，但不能删FR009、降低权限/偷改输出合同，不能未经采用实现新引擎或替代运行。只有环境不足则交精确条件，不泛称所有浏览器不可行。该小交接不要求再做完整研究或另写一份未授权代码。

原73入口、三原失败、成功build子事实/误判错误各自保持。C01的base类型澄清与metadata成功不能当新Root/Gate通过；原collector未运行的性质也不能继承成当前成功。充分旧未改源码/构建无需重跑，当前新增真实观测不能用旧Windows Job或数据库字段替代Linux物理树空。

## 停止与回传

新root在预检前前计数，序号R04/累计第74入口，旧R01/R02/R03不返不改，不写旧session。许可C02独立账只记新增且计原总root8/preview16/controller2；H0累计3→4为本卡明确修订，不代表其他名义余额获准。

第一次runtime/协议/身份/启动错误、首真实权限反证、unknown归属/停止或任何限额到达即进入finally并收尾，不临时扩大环境、补root或改镜像再试。已超过原总deadline不得启动，仅保存不受阻控制准备。能够正常完成观测和精确停止即结束，不因quota还余继续。

stop/kill只针对完整CID/image/nonce/labels与本root/attach/events/reaper的PID出生/命令身份。创建回包丢失在既有一次create范围内按name/nonce/image找回只为确认与停止，不二create。running false/Pid0/no restart、真实事件/wait/attach与协议线程闭合/host namespace依据分别保存；未知不能猜空。recording process不存在需核“已退出/不可访问”等准确层，别因退出console拒kill再重复业务。独立180秒只用于必要精确清理和记录，不触其他服务。

报告先准确构建继承、是否真正Node/browser启动、首次真实观测/反证或环境错误、物理收尾；再本轮控制差异/prepost/as-run/实际resource/counter原文、源/镜像绑定、原新计数秒数重叠、不支持层及最低必要后续。不把局部失败与整个运行无差异混同，保持原build成功和根ERROR原文。

保存109结果置顶续作02、保27219旧字节与旧session/Root03原件；回读结果字节/hash/链接后一句真实结论+原绝对路径返回，不自签B-01/SEC003/STEP015016/独立审计/M-1或项目，不修改共享DocuS/DEF/正式预算账。

## 必要人工与待同步信息

用户仅把本卡当前前缀转给原109 A+窗并带回同一109结果路径。无需重新批准G11-P、构建、用户库、密钥或恢复旧SPIKE；真正超包组件/主要信任模型才给具体差异另裁。共享状态、失败与有效子事实/原deadline/最终验收由编排统一维护，当前卡待转交、新实际使用0。
