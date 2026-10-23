# TASK-125 / R-119 审计修复01 当前工程回传

## 当前结论

两项确定缺陷已合并完成最小工程修正，累计batch03的9项定向离线方法全部通过，退出0。当前交付为修复候选，等待原TASK126对F126-01/F126-02、最终字节和直接影响作增量复核，不能由工程窗口自签缺陷关闭或首次安装放行。原TASK125验收失败历史及原TASK126分轴结论保留。

本轮没有运行安装器CLI apply、真实PG连接/查询/认证、服务、容器、角色创建、网络、付费调用或Git写入。Q继续冻结，T0=null。真实安装、PG事务/ACL、正常启动组合以及受信父目录的对手竞态均未验证，不能由本次参数和文件元数据记录器推出通过。

本置顶修复说明优先于下方原工程候选说明。原结果15686字节完整保留为后缀，SHA256仍为78a80de9633ad13b703262850782ddbcbef3d4ef50632b255e319147a3715404；原两批、post副本、失败与独审原件未改写。

## 缺陷触发与实际修正

F126-01 P1原触发是connect只固定host，没有显式hostaddr；当前psycopg 3.3.5的未显式参数可取PGHOSTADDR，可能在身份预检前改变管理员认证目的地。本次[initialize_normal.py](D:/shspic/project_NO3_RetroLume-agent/deploy/initialize_normal.py)同时显式提交host和hostaddr，均取已被原配置校验限定为127.0.0.1的值。保留精确端口、数据库、管理员及全部真实数据库身份检查，不读原PGHOSTADDR，不修改全局环境纠偏；apply和verify仍共享该connect，无新增CLI参数或配置字段。

新增test19在驱动入口先替换为零网络参数记录器，再局部设置合成PGHOSTADDR=203.0.113.77、PGHOST=synthetic.invalid和合成安装凭据。真实产品connect的direct、内部apply和verify三条调用均观察到host=hostaddr=127.0.0.1、port=55464及既定其余参数；现有驱动get_param也取显式hostaddr，合成环境未被产品改写。服务端172.18.0.2:5432的容器NAT样本继续通过。记录器未发起实际TCP、DNS或认证，没有将驱动原异常或凭据写入结果。

F126-02 P2原触发是new_output只用原路径字面拼写比较受保护目录，真实D:/shspic/PROJEC~3别名可绕过长拼写保护。本次保留safe_path先逐级核用户原拼写的全部祖先、拒绝reparse/junction/UNC/ADS/设备及尾点逻辑；其后对现存父目录和受保护项目根使用Path.resolve(strict=True)取得实际目录长路径身份，再对同一实际根派生的固定产品目录作包含判定。当前Python 3.12.10的ntpath.realpath严格分支调用_getfinalpathname，失败不回退字面比较；归一失败转固定output_identity_unavailable。返回实际目录下的末级文件，保留x模式排他新建，已有输出不能覆盖。

新增test20用本机只读GetShortPathNameW/GetLongPathNameW及samefile确认PROJEC~3仍与项目根、backend/deploy/config为同一真实目录；没有伪造lstat或字符串等价。三个短别名目录下，共用new_output、实际plan、Journal和内部apply入口全部拒绝unsafe_output。写入探针包住文件打开，即便回归也不能在产品目录落盘；本批探针写调用0，假设输出均不存在。新增test21覆盖实际目录归一异常失败关闭。原test07确认允许输出与已有输出冲突，test08只读复用原junction，未再执行失败的DeviceIoControl或重建夹具。

[normal-install.md](D:/shspic/project_NO3_RetroLume-agent/deploy/normal-install.md)仅同步上述连接和路径说明，并保留受信父目录下TOCTOU条件风险。没有修改原SQL、职责组、角色能力模型、业务、配置schema、loader或Q边界，也没有新建路径授权平台。server_major接受17.0的原非阻塞观察未扩大修复范围。

## 受测对象、方法与原始证据

本轮证据根为[D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/repair-01](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/repair-01)。

- [pre-snapshot.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/repair-01/pre-snapshot.json)及pre/保存三份允许产品和原结果的完整原字节、53项输入及七份锁定规则指纹。接收时全部与本轮manifest一致。
- [changes.patch](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/repair-01/changes.patch)仅比较本轮pre与修后产品；post/保存三个最终副本，不混入已有Git差异。
- [batch-03-selection.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/repair-01/batch-03-selection.json)在运行前固定9项：原test07/08/11/12/13/17及新增test19/20/21。前六项覆盖目录身份、正常输出/冲突/junction、Journal/部分提交/重复拒绝/只读收据及脱敏；后三项覆盖新驱动地址、真实别名和归一失败。未机械全跑原18项。
- [tested-before-batch-03.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/repair-01/tested-before-batch-03.json)绑定实际安装器、测试、说明、名单、harness及runner六份受测字节；[post-snapshot.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/repair-01/post-snapshot.json)核对测后相符、53输入允许差异、26份原证据/旧post及原18个方法正文AST均未变。原未运行的12项只沿不受影响范围继承，不声称它们在新字节上重跑。
- [batch-03-command.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/repair-01/batch-03-command.json)、[batch-03-output.txt](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/repair-01/batch-03-output.txt)和[batch-03-summary.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/repair-01/batch-03-summary.json)保存实际argv/环境隔离、原输出、逐项用时及真实别名/参数观察。启动为现有backend/.venv/Scripts/python.exe -I -S -B执行本轮runner，子进程再以-I -S -B -u执行本轮harness；名单只含上述9项。

batch03于2026-10-22T05:58:23.475411+00:00开始，进程wall为1.7951588000287302秒，harness为0.6536168999737129秒，工具外层wall为2.6215342秒，属于不同计时层，不相加。9/9通过，fail/error/skip均0；未启用batch04。本轮没有测试失败，原批1的一项失败和原批2有效证据继续保留。

隔离只传必要系统变量名，PATH明确重建，不读取或继承真实PGHOSTADDR/PGHOST/DSN/provider key、私配路径、旧PYTHONPATH或sitecustomize。-I -S -B后只显式加入现有backend和venv依赖，不安装包。harness对Python socket/DNS/进程及运行时导入设观察阻断，并阻断psycopg.connect及Connection.connect；只有test19将顶层驱动别名换为参数记录器。摘要中相关阻断尝试为空，原始观察可核；这限定于本地控制流，不冒称零字段本身证明全平台安全。

[junction-before.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/repair-01/junction-before.json)及post快照核对原link的device/inode/mtime/readlink、target的device/inode均未变。本批11个新增目录均登记在summary，只在原execution/scratch下新建本轮随机子树，不写删旧case/link/target，也不递归清理scratch。

最终三个产品与本批受测字节一致：

- deploy/initialize_normal.py：29403字节，SHA256 68d7b71fc7296111e894df4cba21a4ed7830f9cff069c1fc500dfbd7734c0a09。
- backend/tests/test_normal_install.py：32786字节，SHA256 93dabd4887760641884fc7ca5d5c83e520522563ea2d44be4dc2e72db320c3b7。
- deploy/normal-install.md：10845字节，SHA256 fb553199dafb11be8608a3608ff2f18778f07acbff265badb2994855c0fd6ddb。

README、normal_install_manifest.json、normal-install.example.json、001—015、所有原生关闭模板/角色/profile、backend/app、依赖、原入口、DocuS、公共库、TASK126原件和旧125证据均保持原字节。

## 合同、预算与历史限制

仍为TASK125/R119、原A+工程窗口，无子Agent、无原TASK126窗口自修。项目根D:/shspic/project_NO3_RetroLume-agent；AGENTS入口及V4.0/task_model/公共AGENTS CHG-0003按七份不变锁定规则复用。需求v1.4、架构v1.67、执行动态v2.95，本执行窗口不维护共享状态。

本轮完整卡SHA256 bd7fa297a5d87bf0383c7c17e826ccd33f2b3cc5c88b154ec8b96cf7bd8ba044，permit记录有效前缀SHA256 363028f13e1cc04590e5566ac5435ea041444ff2e723f120d595a9e15bb9d5d7，input-manifest SHA256 3e45a6a5170f7145921e427f379038b42b5cd53fdecdd96740ee3e0df34a4671。主控orchestration-repair01-20261022只读，未写入。

[command-ledger.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/repair-01/command-ledger.json)保存已恢复命令wall/退出、修改调用计时、测试层次及偏差。原3600/10800秒与精确总wall unknown不改；本轮在恢复2400秒、含360秒收尾的许可内，按可核短调用和尾部保存调用上界保守列支600秒，累计4200/10800秒，未把等待或推理时间充作工具实测。原24小时截止2026-10-23T09:12:14.276888+08:00不重置，当前在截止前；当前累计3/4批，未用额度和批次随本次交回封存，不自动授权后继任务。

初始范围定位的rg --files误包含原scratch文件名递归枚举，出现少数旧case路径；未读case文件正文、未写删旧对象，随即改固定路径读取，不隐去这次定位偏差。原长输出截断后按必要片段补读。其余无范围扩张或新真实资源，也未因本轮再请求平台审批或创建junction。

原批1中间产品完整副本缺失、原平台junction审批回执未纳入原包、原总wall精确unknown，均继续保留，不补造原件；WinError5只证明原生操作被拒绝，不单凭错误码确定策略根因。TASK126审计交付通过、原代码门不通过、原证据轴限定通过、控制轴部分可核/精确unknown的历史均不重写。旧TASK120根/PG64/64及149失败、117旧81、123/124和126预算/失败/unknown保持原账。

## 交主控与原独审的最小收口

主控可按本轮最终三份hash、batch03原件和精确diff，另签原TASK126增量复核，只确认F126-01/F126-02修正及直接影响，其他已接受结论继承；原126余额不自动恢复。工程候选不自签两项关闭、125最终验收或首次安装门，不增加新TASK/DEF编号。

真实PG/认证、安装迁移/角色、正常启动/停止及Q外部门仍待各自精确运行许可与原独审门。100次25元、两供应商、固定48/28/24分额、28Must/89动作/24片6索引不变，账号/分词/模板/Embedding容量和真实normal绑定缺口未关闭，也未重复研究或试跑。不需要用户提供key、开服务、清内存或删文件。共享状态/CHG及最终裁定由主控串行维护。

## 以下为原工程结果 原15686字节完整后缀

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
