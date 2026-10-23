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

