# TASK-126 / R-120 review-01 增量复核 当前结论

## 三轴结论与放行边界

本轮独立增量复核完成。F126-01 P1、F126-02 P2 在本轮冻结修正字节上均可关闭，当前首次安装前的代码门可通过。本轮没有运行测试、产品或真实资源，没有发现由这两处修正直接引出的新增阻断问题。TASK125 最终关闭和真实安装许可仍由主控另行裁定，真实安装及付费调用继续关闭。

- 代码轴通过本次修正及其直接影响复核。connect 显式固定 host 和 hostaddr，new_output 先拒绝原路径重解析点，再严格归一现存父目录和项目根，归一失败关闭。首轮其他未变代码结论继承；受信父目录下的并发替换条件风险及 server_major 类型观察保留。
- 证据轴在离线适用范围内通过。batch03 确为已选 9 方法、9 条 ok、0 fail/error/skip、exit 0，三个产品最终字节与受测身份和 post 副本一致。9 方法是 6 个旧方法加 3 个新方法，另 12 个方法按实际影响分析继承；当前文件共有 21 个方法，没有宣称在最终字节上全跑 21 项，也不把旧 18 和新批 9 相加为 27 个不同方法。参数记录、文件元数据及控制流不能证明真实 TCP、认证、PG、ACL 或安装成功。
- 执行控制轴继续为部分可核、完整精确 unknown。本轮工程 batch03 在原截止前且小于 600 秒，累计 3/4 批，batch04 未运行；工程保守累计 4200/10800 秒的记录与可恢复短调用相容，完整工具总 wall 仍 unknown。旧批1失败、中间版完整副本不足及平台原审批回执缺失均保留，不因代码门转为可通过而追改历史控制结论。

首轮六步最小真实验证清单无功能性增项，原清单沿用。后续运行卡应将对象绑定更新为本轮修后 hash，并使用已有清单要求的受信配置/输出父目录；原完整安装观察仍核实际 loopback 连接及合法服务端 NAT 身份。无需新增外连、认证对手、NTFS 探针、独立集群或重复离线 18/9 项来再次证明本次两条静态修正。

本轮不签真实 PG、认证、ACL、正常安装或启动，不启用 Q，T0 继续为空，不宣布 STEP018/019/020、M1 或项目通过。

## 独立性、合同与精确身份

继续本聊天的原 TASK126 独审窗口，未参与 TASK125 修复实施、普通修复或新增测试设计；首轮审计提出的修正建议不作为工程自评输入。接收时间为 2026-10-22 15:33:43.9662495，中国标准时间，接收前本轮入口读取同计投入。客户端 Codex desktop，平台身份 GPT-6，实际后端变体未知；A+ 是资源档。没有读取 TASK125 统一结果、工程 result-prefix.md、实现聊天、思考或自评；预快照中列出的结果路径/hash 仅为卡面允许的身份元数据，没有打开对应正文。

项目根 D:/shspic/project_NO3_RetroLume-agent，模式 task_model，V4.0/公共 AGENTS CHG-0003。入口和新合同已读，同窗公共 AGENTS/WORK 指纹不变，复用原读取，未采用后来版本或其他模式。需求 v1.4、架构 v1.68、执行动态 v2.96，本轮仍 TASK126/R120，父 TASK125/R119，不新占号、不维护共享状态。

当前完整合同 SHA256 为 56edadf7257c526db7db4adbd3595126ebf2855e2671c7c8f7883a784e78703b，input-manifest 为 741a967428c8b617ac4a8781c1bbc7a3eeca10b37f4f7f649634869ada6ce5b3，raw-evidence-index 为 82eda0bda470a61ef5f63a8d757c6507071c6eefe2e27d889f2cc83dbce45be0，三个许可绑定均独立重算吻合。本轮 input-manifest 的 50 项原件均核大小及 hash，50/50 相符，父路径无重解析边界。

三个变更对象如下，接收、受测、最终与 post 原字节副本均一致，repair-01 的 pre 副本也与首轮审计字节一致。

- D:/shspic/project_NO3_RetroLume-agent/deploy/initialize_normal.py，29403 字节，68d7b71fc7296111e894df4cba21a4ed7830f9cff069c1fc500dfbd7734c0a09。
- D:/shspic/project_NO3_RetroLume-agent/backend/tests/test_normal_install.py，32786 字节，93dabd4887760641884fc7ca5d5c83e520522563ea2d44be4dc2e72db320c3b7。
- D:/shspic/project_NO3_RetroLume-agent/deploy/normal-install.md，10845 字节，fb553199dafb11be8608a3608ff2f18778f07acbff265badb2994855c0fd6ddb。

本轮必要标准库来源为清单明确给出的实际路径，仅读源码，未执行其中产品调用。

- C:/Users/28432/AppData/Local/Programs/Python/Python312/Lib/pathlib.py，52487 字节，cd1557dedcaa1be0459cd59760c5ebac83a3e412e0e1b5bc0b1a82a19563a090。
- C:/Users/28432/AppData/Local/Programs/Python/Python312/Lib/ntpath.py，32762 字节，e62526627fe0129120e452f99b05b84965a57451e5ad8d29f0d5f3276cc2c489。

四个 psycopg 必要源文件的绝对路径及 hash 见本轮接收证据，与首轮所读四文件相同。额外仅对原 SQL、原 schema/profile/角色检查、原启动入口及原关闭模板共 30 项做 hash 继承核对，均与首轮相同，没有重读重审业务逻辑。

本轮证据只保存在 [review-01 目录](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-126/audit/review-01)。其中 [reception-identity.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-126/audit/review-01/reception-identity.json) 保存接收和 50 项身份，[static-review.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-126/audit/review-01/static-review.json) 保存字节、AST、日志及限定元数据核证，[独立差异](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-126/audit/review-01/independent-changes.patch) 与工程 changes.patch 正文相符，[closure.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-126/audit/review-01/closure.json) 保存最终复读、历史后缀 hash 链和本轮投入账。

## F126-01 关闭依据

当前 [connect 第324行](D:/shspic/project_NO3_RetroLume-agent/deploy/initialize_normal.py:324) 将同一 target.host 同时作为 host、hostaddr 传给 psycopg.connect，原 load_config 第156行仍只允许 127.0.0.1。端口、库名、安装登录、密码及其余连接限制未变，没有新增产品全局环境写入或读取旧 PGHOSTADDR 的纠偏分支。

当前驱动 _conninfo_utils.py 第73—82行先取显式参数，存在 hostaddr 时不进入相应环境读取；_conninfo_attempts.py 第85—96行不再用其他环境地址替代显式 hostaddr。connection.py 第97—108行沿同一参数进入连接过程。修正发生在驱动认证入口之前，并非依靠后续身份查询补救目的地。

apply 第414行和 verify 第483行的 connector 默认值仍共享同一 connect，函数主体未变；原 observe_identity、preflight、system_identifier/OID/数据库名/会话登录校验也未变。没有把服务端地址限制为 127.0.0.1 或要求两端端口一致，原合法 NAT 语义保留。

新增 test19 在调用产品 connect/direct、apply 和 verify 之前先替换 psycopg.connect，再建立本地合成 PGHOSTADDR=203.0.113.77、PGHOST=synthetic.invalid 及合成凭据环境。记录器逐次断言实际 kwargs 的 host=hostaddr=127.0.0.1、端口55464、精确库/登录及连接限制，并调用当前驱动 get_param 检查显式值优先。三用途观察与 summary 对应；测试末还核合成环境未被产品修改、verify 无写请求及收据字节不变。服务端 172.18.0.2:5432 与客户端 127.0.0.1:55464 的观察仍使用 Recorder，未冒称真实认证。

结论为已消除首轮确定的环境地址覆盖路径，F126-01 在本轮代码和离线参数证据范围关闭。真实 TCP/认证、实际管理员身份及 PG 安装仍未验证，不影响这个源级缺陷关闭，也不能借关闭取得真实操作权。

## F126-02 关闭依据

当前 [new_output 第213—228行](D:/shspic/project_NO3_RetroLume-agent/deploy/initialize_normal.py:213) 先调用原 safe_path 对原始拼写逐级 lstat，排除 reparse/junction、UNC、ADS、设备及不安全尾点等；已有输出仍先拒绝。随后分别对现存父目录和项目根执行 resolve(strict=True)，归一的父目录再与原末级文件名组合，并对归一后的目录重新做安全检查。受保护目录与两个根文件的判断都以归一后的 project 为基准。OSError/RuntimeError 统一停止为 output_identity_unavailable，没有回退字面比较。

当前 Windows Python 源码支持这一解释。pathlib.py 第1228—1253行将 strict 传给实际 realpath，异常会传播；ntpath.py 第705—765行使用 _getfinalpathname，strict 模式不走原拼写或非严格回退，普通本地路径的扩展前缀只在可核同一身份后去掉。结合 test20 在当前机器上真实取得 8.3 元数据并实际调用产品 new_output 的证据，原 D:/shspic/PROJEC~3/backend、deploy、config 三类路径进入与长路径相同的保护。只针对当前 Windows 实现下结论，没有新增 Linux 平台承诺。

test20 使用实际 GetShortPathNameW/GetLongPathNameW，核短根不同拼写、两个根及三个子目录的 os.path.samefile，没有伪造 lstat、resolve 或实际目录身份，也没有预先把危险输入改为安全路径。Path.open 探针只阻断写模式并将读模式交回原 open；三个真实别名仍原样送入 new_output、plan 输出、Journal 和 apply 收据入口。每个入口都要求明确 unsafe_output，计划入口还核 JSON reason，而不是只接收任意非零退出。写探针调用为空、假设输出不存在，与先拒绝后打开的源码顺序相符。

test21 将目录归一抛出的 OSError 定向注入，要求固定 output_identity_unavailable 且不得 open。它只证明该异常控制流，不能代替 test20 的实际目录身份；两者证据没有混用。原 test07 的允许输出和冲突拒绝、test08 的现存真实 junction 拒绝，以及 test11/12/13 和17，均包含在本批实际9方法内。

plan 第529行、Journal 第234行和 apply 第416行共用 new_output；返回的规范路径进入原 x 排他新建，未改为可覆盖写。verify 仍仅读完整既有收据，未经过新增写入分支。由此 F126-02 的原别名触发及直接传播路径可关闭。父目录在检查后被对手并发替换仍是首轮条件风险，本轮无此实际触达证据，不升级成新的 P1，也不宣称已核对手竞态。

## 九方法证据、继承及控制事实

原始材料仍位于 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/repair-01/，本轮只读取，没有启动其中 harness、runner 或 CLI。独立重建三文件 pre/post 文本差异，与 changes.patch 相同；产品 AST 只有 connect、new_output 两函数变化，其余函数、类及模块数据不变。测试仅新增观察字典及 test19/20/21，剥除这些增项后模块 AST 与 pre 相同，原18方法正文逐项相同。

batch03-selection 于 2026-10-22 13:55:55.157647 固定，早于 13:58:23.475411 启动。start 与 command 的共同字段相同，输出、selection、summary 及 records 的9方法名称和次序一致，逐行都是 ok，summary 为9/0/0/0，进程 exit0。tested-before-batch03 中三产品及 selection/harness/runner 共6项的实际原字节 hash/大小均吻合；三产品 post 副本也逐字节相同，不只采信作者 match 布尔。

- 07、08覆盖新增目录身份路径对正常输出、冲突及原真实 junction 的影响。
- 11、12、13覆盖 Journal/apply/verify 的收据路径、阶段、未知提交、重复拒绝及只读复核。
- 17覆盖稳定异常脱敏和依赖边界。
- 19覆盖真实产品共享 connect 的三个用途及显式参数优先。
- 20覆盖实际短别名的四个输出入口及无产品目录写入。
- 21覆盖归一异常失败关闭。

未重跑的12项为01—06、09、10、14—16、18。继承依据不止是方法正文相同。

- 01—06的默认/help/无输出计划、清单/SQL原件、配置与标识逻辑没有调用新的输出归一分支，相关输入身份不变；显式输出路径另由07和20实际覆盖。
- 09的关闭输入拒绝仍在 new_output 与凭据之前，逻辑不变；10的预检及 Recorder 分支不变，其正常输出前置由07、11和19覆盖，拒绝路径没有新增数据库写分支。
- 14—16的角色纯函数、生产 verifier、profile、SQL和职责分工未变，原检查依赖 hash 未变；本次没有新角色或 ACL 变化。
- 18的 argparse、start_local 参数接口未变，说明仅准确补充地址与路径修正，没有增删 CLI 参数。

原批2的18方法证据依上述适用性复用，原批1失败照留。没有重审未变 SQL/业务，也未运行原13方法或安全矩阵。应用/授权构造、真实 PG 事务与角色权限等首轮未知仍保留。

harness 在导入测试模块前替换 psycopg.connect 和 Connection.connect，并设置 Python socket/DNS/进程及相关 runtime import 审计守卫；test19仅把顶层驱动别名临时替换成参数记录器，未恢复真实连接。runner 的 -I -S -B、白名单环境、预先绑定 hash、600秒超时及避免覆盖旧批文件的检查均与原日志相符。denied 数组为空不能单独证明全系统无副作用，Recorder 和文件观察也不能签真实 SQL、ACL 或网络通过。

原进程时长1.7951588000287302秒，harness0.6536168999737129秒，工程工具外层2.6215342秒，是包含关系不同的测量层级，不相加。工程本轮许可最多2400秒含360秒收尾、原总cap10800和原截止2026-10-23 09:12:14.276888均未重置，batch03及13:59:31封存时间在许可内。账中13组可恢复调用主要为一至数秒短前台操作，支持本轮600秒、累计4200秒的保守列支合理性；完整总工具wall仍unknown，不由日历间隔推导精确合规。

summary登记11个新目录，即一个本轮随机根、9个case及test08的target。本轮仅对这11个明确路径逐级看目录属性，均存在且无reparse，没有枚举旧scratch或读取case正文。只读 lstat/readlink 的原junction设备、inode、mtime和目标与junction-before完全相符，没有跟随递归、重建或删除。此观察不证明旧case全过程未被访问。

工程账明确披露曾一次将旧scratch纳入 rg 文件名枚举。原始命令和输出没有另附，本轮将其保留为受限的只读范围偏差记录，不虚构精确命令、不认定未获证实的正文读取、跨junction或改删；不将它伪成完全合规，也不把这条控制观察升级为安装产品缺陷。原平台审批回执、首批中间版正文缺失等未知仍然有效。

## 本轮操作、预算与交回

实际操作仅为有界 PowerShell 读取/hash/JSON、标准库源码定位，以及自编 static-review.py 的文本差异、AST及所列文件元数据分析。脚本使用现有 Python -I -S -B，exit0，工具wall2.1566343秒；未导入产品或驱动，没有执行测试/harness/runner。原始长展示有截断，随后只按必要固定片段补读。到本轮保存前没有命令失败；最终保存和复读状态见closure。

本轮保守列支600/1200秒，含240秒保存额度；加原首轮保守1800秒，审计累计2400/3600秒。精确完整工具wall仍unknown，可恢复各次短命令样本保存在本轮closure，不把推理或人工回传等待当工具实测。原许可截止2026-10-23 09:56:00.006928保持，未重开其他封存余量。本轮未用额度不自动授权后续任务。

产品/驱动导入、CLI/help/plan/apply、compile/unittest、PG、Docker/Compose、端口/服务、浏览器/Job/预览、provider/Embedding/网络、安装依赖、费用、Git写入、委派均为零。未读实际local/private配置、.runtime、凭据、账号后台或用户资料/库；未改产品、测试、SQL、模板、README、DocuS、公共库、主控orchestration、首轮audit或工程证据，也未新建短别名/junction或修改系统设置。

仅在原结果置顶增加本review，首轮33379字节全文作为原样后缀保留，原SHA256为b1f52e0284e37b5e67f28ef1a1c2dee7d1c7d255a3e090d1478bc5747d72b1d3，收尾复读再次核后缀同hash。原不通过结论仍是其当时对象的历史结论，不追改为首轮通过。

请主控在唯一状态账登记review-01返回、两发现独立关闭依据及当前代码门可通过，并另行裁定TASK125最终验收和后续真实资源许可；本执行者不代写共享状态。后续最小真实清单沿用，无新增验证设计或重复测试要求。唯一人工动作是用户把本结果路径带回主控，无须提供key、开服务、释放内存或删文件。

## 以下为R120首轮报告原字节全文，保留历史结论

# TASK-126 / R-120 正常首次安装工具链独立审计结果

## 结论、差异与证据导航

本轮审计交付完成，当前冻结候选的首次真实 apply 前代码门不通过，暂不能进入首次安装执行放行。发现 F126-01 一项 P1 和 F126-02 一项 P2，均归原 TASK125 工程窗口修复。本报告没有修改产品，也没有执行安装、测试或真实资源操作；报告完成不代表主控最终验收。

三轴结论如下。

- 代码轴不通过。连接只固定 host，没有固定 hostaddr，PGHOSTADDR 可改变实际连接地址；安装管理员认证发生在数据库身份查询之前。另有已取得本机文件元数据支持的 NTFS 短路径别名输出保护绕过。除这两项外，本轮未从冻结代码发现合法新空库安装必败、遗漏控制行、角色职责混授或自动重放的确定问题；这不代表真实安装已经成功。
- 证据轴在既有离线范围内核证通过。第二批确为 18 方法、0 失败、0 错误、0 skip、exit 0；实际受测六文件、当前文件和 post 原字节副本一致。首批 18 方法中 junction 夹具创建失败一项、exit 1 的历史保留。原方法未覆盖上述两条缺陷路径，不能以 18 项通过放行代码门，也不能据此签真实 PG、ACL、事务或正常启动通过。
- 执行控制轴部分可核，完整精确合规无法判断。两批及可恢复的封存时间在许可内，单批实测远低于 600 秒，2/3 批有依据；工程工具总 wall 仍为 unknown，3600/10800 秒保守列支有现存短命令记录和首小时封存时间支持，但不是逐工具精确总计。现有材料没有证实越权运行或超额；未留存的调用和原始平台审批记录不能补成已核事实。

主控可安排范围内普通修复和定向离线补证。F126-01 关闭并核对冻结差异之前，不建议批准真实 apply。F126-02 可在同一普通修复批完成，不需要耗用 PG 资源。后续真实安装仍需另行冻结目标与精确运行许可，本卡不提供该许可。

本轮产物仅为本报告及 [审计证据目录](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-126/audit)。关键证据如下。

- [接收、规则和 71 项身份核对](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-126/audit/reception-identity.json)。TASK126 合同、输入清单及原始证据索引三个许可绑定均吻合，71/71 项的原字节大小及 SHA256 均吻合，父路径未遇 reparse。
- [首次静态核证](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-126/audit/static-analysis.json) 和 [补充核证](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-126/audit/static-analysis-02.json)。后者补足 012 动态创建的 HTML 两组和 diff 标签差异，保存六文件交叉绑定、18 个方法、两批事实、实际 junction 元数据、短路径别名及驱动源文件 hash。
- [README 独立差异](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-126/audit/readme-independent.diff)。只有第 33 行安装说明改变，其余 README 原字节逐行保留；与工程 changes.patch 的实际 hunk 相符。
- [收尾核对与本轮操作账](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-126/audit/closure.json)。其保存最终身份复核、额外直接依赖身份、资源零操作边界及本轮保守投入。

## 接收、独立性与适用对象

项目根为 D:/shspic/project_NO3_RetroLume-agent。按用户本次人工转交的 TASK126 接收，接收记录时间为 2026-10-22 10:01:04，中国标准时间；更早的本轮入口读取计入同一审计投入。新隔离审计会话没有参与 TASK125 实现、普通修复或测试设计，不是原工程窗口自审。客户端为 Codex desktop，平台给定身份为 GPT-6，实际后端变体及不能核实的 UI 模型型号为未知；A+ 只表示合同资源档。

已读取项目入口、TASK126、TASK125 原始合同、同版公共 AGENTS 及 WORK 第 6、8、9 节。锁定 V4.0、公共 AGENTS CHG-0003。公共 AGENTS 的 SHA256 为 e7e6b1a806d80a19294c5d6b95f93c7a004dc254029c7c01256910df479d4514，WORK 为 96211d15f0affef4846784d56330ce4a9a25d6be622ff67828c92f1897b3461a，均与锁定快照相同。没有采用后来规则，没有读取其他模式替换合同。

TASK126 合同 SHA256 为 e456d9c73b04fd8a9c631fc5bf755f741c19d8d45a6d9d1193cba13b889618fc；其 input-manifest 为 0e21b57ec7c368786d436fdd81adc24fefab9e823cdf34580f66593cc3baaaea；raw-evidence-index 为 3d563560715dfb272c3f42255ae25ec8293b7fada9bcc14b0b585386d9e6aa34。TASK125 原合同为 10a1ce45367f50045faca8393d67fe32aacfc5df1653b97e2fa377c4b0e3e0a5。

没有读取 TASK125-result、实现聊天、完整思考或工程自评。先读原合同、入口源码、固定清单、配置、迁移所需职责和原校验实现，再全文读测试与执行记录。按卡读取 changes.patch 时其中含测试片段，它是允许的最终差异输入，未接触被排除的工程结果。没有用测试作者的推断替代源码判断。

关联 STEP-018、STEP-020 和未来 STEP-019 的适用安全证据，需求 v1.4、架构 v1.66、执行动态 v2.94，父 TASK125/R119。本轮只读核证对象，不维护第二份总状态账，不填写主控验收，不签 Q、T0、真实安装、真实权限、语义、M1 或项目通过。

六个冻结最终文件的当前身份如下，大小单位为字节。

- D:/shspic/project_NO3_RetroLume-agent/deploy/initialize_normal.py，28872，e112ce498f73371e6d788ed834c4c0414f3c8728579ec1ddc9df6c4942ffce5d。
- D:/shspic/project_NO3_RetroLume-agent/deploy/normal_install_manifest.json，4325，f2ed126daa1c5a982b490a9343d6c17053c0f385e7a2f55676ecf4132dd2abf0。
- D:/shspic/project_NO3_RetroLume-agent/deploy/normal-install.md，10496，dc46e05bb8e01873c5ce359a9d2665d57e27e4c9a5d89c11ade18fd4128c61cc。
- D:/shspic/project_NO3_RetroLume-agent/config/normal-install.example.json，869，95c97092a95fd39b116fe4e85fd4d5d4c7bb6757fc45efe76cc600863b55df3b。
- D:/shspic/project_NO3_RetroLume-agent/backend/tests/test_normal_install.py，26021，ca2fb5fa09776a73e6e8983dd2a47f9be399dcc141ea196f31ec8a6cf69e4633。
- D:/shspic/project_NO3_RetroLume-agent/README.md，27130，7ebb7d680949ce10c9c63f2e31b26f318145eba3309ab42e1891783526602db8。pre 为 0410c7573027f7f6e75635c3a8d050e2be375d98ab0a4b503ddf3e076104d938；其余五文件 pre 记不存在。

主要产品直接依赖位于 D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/，SHA256 如下。15 份 SQL、五个既有配置示例及原运行入口的逐项绝对路径、大小和完整 hash 另见接收证据；静态核证对 001—015 逐项重算，并与正式 R03 migration_chain 对上，不只是比较作者的 match 字段。

- schema_profiles.py，d25b4f4dcfdf11319384ee05acb90dda6123de696dfbed59019a1f64a10daff9。
- schema_checks.py，0e67661a05cdf42aa798485888ab1ff7a26be24342616a41e0048a7c56270540。
- q_roles.py，fbc4534b899a40c1b5ce6d596c45e2b20d088e1ddfb1e3bd58ed703ab9dca30e。
- files.py，fd85a1918e43c201435c9f28c963ab4dfdaf32fa1317db1a805ebe271eaa609e。
- config.py，f3582c2bca0db6dadc8fd5cfb3dfb9caa25b951848eb046861f04a21a856e38f。
- schema.py，e4f2103cd2b0d858973026c268db015c52d81675cca06a76b303aa566fb73c4e。
- contracts.py，db6aed89d5917fc53f124e34be88d0ab8803ce40fcf33836d5103d5fb80d9054。

为核定实际驱动处理路径，额外只读了已安装 psycopg 的四个源文件，没有导入驱动或连接 PG。依赖锁声明 psycopg 与 psycopg-binary 均为 3.3.5；当前源文件另按 hash 绑定，不冒称这些额外文件已在原批次逐一取过 hash。四个文件位于 D:/shspic/project_NO3_RetroLume-agent/backend/.venv/Lib/site-packages/psycopg/。

- connection.py，5dfacd2ef35f748c5a60c07c8bf5d6e6a2fa25438ee1794591b4a4e4e70afd7e。
- _connection_base.py，c235d3bdab18c7cd9ddefa4104515ba8f4dc031346f2d72d6c44ee98f393f429。
- _conninfo_attempts.py，9e081d1fe49a639f4cf0f2d54bce359ac6b7524acc2ed9b170cc0dd004fec7d3。
- _conninfo_utils.py，008bda02cdd0a7c7b029fcfced01ba9fdbbd67da0e862f1089306c799b013575。

包初始化直接依赖也只读确认，D:/shspic/project_NO3_RetroLume-agent/backend/app/__init__.py 为空文件，SHA256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855；data_exit/__init__.py 仅有说明字符串，SHA256 44155c2ce1953545c02b7e4029fe3f70c1ecb32872fdd1ed3c3473566e5b3fdc。

## 确定缺陷与最小修正

### F126-01，P1，连接未固定 hostaddr，精确 loopback 边界可被环境参数改变

来源为 TASK125 的精确本地连接及凭据边界。定位 [安装连接函数](D:/shspic/project_NO3_RetroLume-agent/deploy/initialize_normal.py:311)、[目标校验](D:/shspic/project_NO3_RetroLume-agent/deploy/initialize_normal.py:278)，以及当前已安装驱动的 connection.py 第 97—108 行、_conninfo_utils.py 第 67—82 行、_conninfo_attempts.py 第 85—96 行。

安装配置只允许 host 为 127.0.0.1。实际 psycopg.connect 提供 host、port、dbname、user、password 等参数，却没有 hostaddr。驱动对缺少的参数读取相应 PG 环境变量；如果 hostaddr 已由环境提供，解析函数直接返回原参数，不再把数值 host 转成固定 hostaddr。后续将参数交给 libpq 连接。因此，未来进程若残留非 loopback 的 PGHOSTADDR，仅固定 host 字符串不能固定实际网络目的地址。此条件不要求修改产品或拥有系统管理员权限，普通启动 shell 的旧 PG 配置即可触发。

影响发生在 preflight 之前。安装管理员认证已经向该连接地址发起，之后的 system_identifier、OID、数据库名和角色查询无法撤回认证行为；身份不符时虽可阻止 DDL，仍没有满足连接范围边界。若错误端点提供匹配的复制集群身份，现有 observe_identity 只要求服务端地址是合法 IP，也不会据地址拒绝。这里没有要求服务端地址等于 127.0.0.1 或两端端口相同，合法容器 NAT 应继续允许。

这是静态可确定的连接约束缺陷，实际错误连接或凭据泄露在本轮均未发生、未尝试；没有读取当前 PGHOSTADDR 或任何真实凭据。证据来自被冻结入口和当前驱动源码，不依赖 Mock 宣称真实外连成功。

最小修正是在连接参数中同时显式固定 hostaddr 为配置允许的 127.0.0.1，继续保留真实数据库身份核对与 NAT 地址记录，避免靠修改全局 os.environ 纠偏。由工程窗口补一个零网络连接参数记录用例，在合成非 loopback PGHOSTADDR 条件下确认真正提交给驱动的 hostaddr 仍是 loopback；不用启动另一个 PG 或尝试向外连接。apply 和 verify 共用 connect，应同时受保护。

### F126-02，P2，NTFS 短路径别名绕过产品输出目录保护

定位 [路径检查](D:/shspic/project_NO3_RetroLume-agent/deploy/initialize_normal.py:63)、[输出目录保护](D:/shspic/project_NO3_RetroLume-agent/deploy/initialize_normal.py:213)、[计划文件写入](D:/shspic/project_NO3_RetroLume-agent/deploy/initialize_normal.py:520) 和 Journal 第 225—226 行。

safe_path 对原路径逐级 lstat，正确拒绝 reparse、UNC、ADS、尾点空格及设备名。new_output 随后只以 Path.is_relative_to 对 ROOT/backend、deploy、config 等目录做字面包含比较，没有统一现存父目录的物理长路径身份。

本机只读 GetShortPathNameW/GetLongPathNameW 已确认 D:/shspic/PROJEC~3 与项目根为同一目录。例如 D:/shspic/PROJEC~3/backend/audit-hypothetical-not-created.json 的现存父目录均非 reparse，目标文件不存在，却不在长拼写 ROOT/backend 的字面包含关系内。该判断还同时适用于 deploy 和 config。元数据及比较保存于 static-analysis-02.json；没有调用安装器、没有创建这些假设文件。

因此，将来 plan --output 或 apply --receipt 使用此别名，可在声明受保护的产品目录新建部署元数据文件。排他 x 模式仍防止覆盖既有文件，本轮未证实覆盖、任意内容注入或权限提升，所以定 P2，不将其夸大为数据破坏。使用正常长路径且位于产品外的受信输出目录是现存替代办法。

最小修正是在逐级拒绝链接之后，将现存父目录和受保护根统一到可信的实际长路径或文件对象身份，再做包含判断，并保留末级排他新建。不得先 resolve 再检查而掩盖 junction。新增一个实际可用短路径别名的离线拒绝用例，和已有正常输出、已有文件冲突、junction 用例一起定向核对即可。此问题不应留到真实 PG 批再确认。

## 其余代码审查事实、条件与未知

### 默认关闭、本地计划和固定对象

入口顶层仅标准库导入及常量；默认、帮助和坏参数路径未到 connect/read_credentials/product_checks。plan 仅 load_config/load_bundle 后生成计划，没有调用 app、ControlHub、QAuthority、子进程或驱动。显式 --output 是单独的计划文件输出，不能混称安装成功收据。

计划区分 plan_only、local_inputs_complete、missing、installed=false、verified=false、database_observed=false；观察身份保持 null。示例 enabled=false，目标和身份未填，不会仅凭字符串长度或示例格式变为实际 ready。config 为安装器专用结构，不送入旧 loader。server_major 的本地检查采用值等于 17，17.0 也会通过，类型并未完全严格；真实身份另核整数版本范围，当前没有由此推出错误版本安装，作为非阻塞类型观察，不增设真实资源门。

清单原字节 hash 被入口常量固定，调用者不能通过 --manifest 替换信任根。15 个文件的固定顺序、大小、原字节 hash 和 R03 正式 profile 均独立对上。目录枚举只用于拒绝额外 SQL，不自动吸纳未来文件。所有 SQL 首个有效语句为 BEGIN、末个为 COMMIT，执行仅 utf-8-sig 解码，未发现 SQL 改写、规范化 hash、删除 010/011 guard、tests 或 DocuN 产品运行依赖。

路径检查和后续打开之间仍有时间窗口。若父目录可被其他主体并行替换，存在 TOCTOU 条件风险；目前没有观察到可写对手、并发替换或已触达损害，不机械定为另一个 P1。未来输出应在精确许可冻结的受信目录。既有文件排他拒绝和最终文件类型检查有效，不能用它们替代 F126-02 的别名修正。

### 身份、空库和迁移阶段

apply 在本地输入齐全、输出新建检查及正式 profile 对账后才读四份凭据。intent 本地收据在 PG 连接前保存，它是部署元数据副作用，不等于数据库 DDL、DCL 或业务账本写入。

preflight 使用 BEGIN READ ONLY，依次核数据库名、OID、system_identifier、current_user/session_user、bootstrap superuser、PG17/UTF8，核全局职责组及两个新登录不存在、其他库和客户端、额外 schema/对象/扩展/default ACL 等，并核 vector 默认版本恰为 0.8.6，最后 ROLLBACK。任一检查拒绝时，源控制流没有进入第一个迁移写请求。F126-01 是这些查询之前的实际连接缺口，不能被这段正确的查询顺序抵消。

GLOBAL_ROLES 完整覆盖原 SQL 创建的 13 个职责组，包含 012 通过 FOREACH/format 创建的两个 HTML 组；没有将其宽松角色复用逻辑带入安装器预检。独占是预检时观察和未来运维约束，并非整个安装期间跨集群的持锁保证。其他会话在预检后加入或系统管理员改动不属本轮已观测失败；未来运行需确实独占新集群。

001—013 各原事务确认后，单独事务插入 normal/R01 控制行。013 第 8—17 行所需 singleton、created_at、reference_epoch 有原默认，其余必需身份及 maintenance_key_sha256 均由明确输入提供。随后原 014 将 normal 行推进 R02，原 015 在原 R02/guard/ACL 前置成立时推进 R03，最后另一个事务创建登录。没有遗漏控制行造成后续写 guard 永久只读的静态问题。新工具没有覆盖就地升级，这与本卡只支持独立新集群空库相符。

committed_sql 逐个耗尽多结果集，要求末状态 COMMIT 且 transaction_status idle。Journal 在每阶段操作之前 fsync submitted，操作及确认收据成功后才加入 confirmed；中断、驱动错误或确认保存失败保留 pending 为提交未知。最后 schema/role 检查失败没有 complete，不返回 installed。收据初始化写失败发生在连接之前；阶段确认写失败保守记未知；最终 complete 写失败不宣称成功。异常只返回固定原因，没有自动重试、清空或续迁移分支。数据库已经提交但收据缺失时需要带回事实，不能补签成功。

重复原收据在本地被拒；换收据仍要重新做空库/角色检查。完整收据严格核 17 个阶段的 37 条记录，verify 仅读取成功序列、只读查询目标和现有 schema/角色/控制行，并不写收据或恢复未完成安装。断线与 COMMIT 应答处理的真实驱动行为、实际保存故障和断电持久性本轮没有动态验证。

### 登录、权限、凭据及启动相容

create_logins 使用 psycopg.sql Identifier/Literal，创建两个新非超级登录，不 ALTER/DROP 既有角色、不重置旧密码。业务只继承 data_app、memory_app、interview_app、html_app、retrieval_app，快照只继承 data_snapshot；每条授予显式 INHERIT TRUE、SET FALSE、ADMIN FALSE，另授精确目标 CONNECT，没有额外 PUBLIC 授权，没有登录 owner、purger 或 restore_loader。

verify_installed 第 376—396 行确实复用原 assert_data_schema_sync、正式 profile、ROLE_CAPABILITIES/MEMBERSHIPS 和 check_role_capabilities。原 schema_checks 第 53—66 行自身已调用真实能力检查并核固定 shape、函数、trigger、ACL 和 R03 增量；q_roles 第 31—95 行跟踪 SET、INHERIT、ADMIN 及 owner 能力，不是只检查直接 membership。安装器又核两个登录的管理标志、owner 路径和精确成员选项，控制行身份也对上。当前未发现业务连接与快照职责静态混授；真实 PG 语法、认证、实际继承权限和业务连接可用性仍待运行。

四份秘密只在 apply 后续路径按显式环境引用读取，verify 只读管理员密码。凭据、DSN、维护密钥及维护摘要未进入计划或安装收据；维护摘要只用于 data_control INSERT。未知驱动异常被稳定原因遮蔽。F126-01 所述风险属于连接前认证目的地约束，不能以输出脱敏视为已关闭。

活动示例的额度/输出占位仍为零，integration/q-approval 仍 false，preview 保持原无效镜像和票据占位，未新增旧 loader 不支持的 enabled 字段；data-exit 原示例仍 false。新示例没有构造 grant、operator、Q 根或 T0。新文件没有修改原 start_local、initialize-materials、Compose 或运行 app；旧 001 初始化不是完整链，也不能在完整安装后再执行。README 及新说明的 plan/apply/verify、--config/--output/--receipt 与实际 argparse 一致，start_local 的 --container/--port/--shutdown-stdin 也一致。

安装器不生成全部正常 source 的私有配置和四根绑定，这是合同保留的后续部署工作。当前 README 的旧 R01/R02 恢复槽位说明及历史业务成果仍按原适用范围继承，不能因本次 R03 安装工具就宣布原 source/readonly 恢复资格或全部部署验收更新。真实正常 source loader、同库重开和停止组合仍为未知，不以外部账号/计量缺口要求本轮重复研究。

## 原离线证据与执行控制核证

原始材料位于 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-125/execution/。本轮读取两批 command/output/summary、两个 harness 和 runner、两个 tested-before、pre/post-snapshot、source-preservation、changes.patch、command-ledger、junction-diagnostic 及 correction-01，未运行这些文件。

第一批开始于 2026-10-22 09:35:49.129139，进程 1.7728173999930732 秒，harness 0.5608052000170574 秒，exit 1。原文为 test_08 中 DeviceIoControl 的 junction_create_failed 断言失败；其余 17 方法通过。失败发生在夹具创建，未到安装器 junction 拒绝断言，不算产品拒绝断言已经通过。

第二批开始于 09:39:07.559512，进程 1.0162982000038028 秒，harness 0.4948959000175819 秒，exit 0。输出逐项 18 条 ok，summary 的 tests_run/failures/errors/skipped 为 18/0/0/0，18 个方法名与最终测试文件 AST 一致。原两批进程实测合计约 2.789116 秒，仅代表这两个进程，绝非整个工程投入。

各方法的实际证明边界如下。

- 01—02 覆盖默认、help、坏参数和计划的本地控制流、重复计划、null 身份及关闭状态。环境访问守卫、导入守卫、Popen/连接替身只覆盖其观察路径，不能据此证明整个操作系统无副作用。
- 03—07 覆盖缺/额外 SQL、清单改序/增项/摘要、SQL 原件漂移、profile/标识/配置/角色重叠、输出冲突及若干危险拼写。07 没有覆盖实际存在的 8.3 别名。
- 08 第二批实际读取预建 reparse 的属性及目标范围，再调用 safe_path 与计划入口拒绝。当前只读元数据再次确认 link 为 junction，目标仅是同一 scratch/junction-fixture/target。没有重建、删除或递归穿过 junction。原 native 分支的 NT 前缀经 AST 看是正确的四字符前缀，未发现应延后到真实资源验证的确定夹具编码错误。
- 09—13 使用 Recorder 覆盖关闭拒绝、四类预检零写请求、001—015/控制行/登录顺序、002 未知提交停止、原收据拒绝重放、完整收据 verify 只读。Recorder 的 COMMIT 和 transaction_status 是常量，空库是一项合成 bool，verifier 在主成功路径被替换；不能证明 PG 事务、真实 SQL、空库查询完整性、认证或 ACL。
- 14—16 调用现有纯角色检查器，覆盖意图角色方案、SET/INHERIT/ADMIN/owner/快照写能力反例，以及生产 verifier 确实接上能力检查。样本并非 PG 真实能力查询；16 的 schema checker 被替身替换，不能签真实 R03 shape。
- 17—18 覆盖哨兵异常脱敏、产品依赖字符串边界及参数/说明一致性；它们没有测试实际 connect 的 hostaddr 环境交互。

runner 白名单构造系统环境，重建 PATH，以 -I -S -B 启动 harness，未继承 provider key、PG/DSN、私配和旧 PYTHONPATH；harness 加 socket/Popen 等 Python 审计钩子，替换 psycopg.connect 并禁止相关 runtime import。denied_effect_attempts 为空与现存源码控制流相符，但 real_pg_connections/network_operations 是硬编码零，钩子也不覆盖任意本地 C 调用；不能把两个零计数字段单独当全系统无副作用的独立证明。

两个 tested-before 清单之间，入口、说明和测试三项 hash 改变，清单、示例和 README 不变。最终入口允许容器服务端实际 IP，第二批成功样本为服务端 172.18.0.2:5432、配置映射 127.0.0.1:55464；这支持当前 NAT 修正语义。原始失败与后续证据没有互相覆盖。批一候选正文未在所列材料中另存完整副本，只有 hash，故不能独立重建那一版到当前版的逐行中间 diff；此限制不影响第二批最终字节绑定，也不伪称已核该中间 diff。

junction-diagnostic 记录 WinError 5。它支持 native 夹具操作被拒绝这个观察，不能单凭错误码确定一定是沙箱策略根因；correction-01 的因果说明为作者推断。command-ledger 报告通过自动审查后由 PowerShell 预建同 scratch 的 junction，当前元数据与此范围一致。原平台批准工具回执未包含在本包，本轮不能独立签平台审批经过，仅保留报告事实与此证据缺口；没有据此认定另一次未经授权操作。

source-preservation 的 61 项与 pre 元数据对照，60 项 hash 不变，唯一允许改变为 README；当前独立核到的冻结产品、原 SQL、校验实现和启动入口没有出现未声明漂移。此为限定输入保护核证，不是全仓未修改证明。post 副本六项原字节也均与当前和第二批一致。

TASK125 许可为 2026-10-22 09:12:14.276888 至次日同刻，工具上限 10800 秒含 900 秒收尾，最多三批、每批 600 秒。post-snapshot/source-preservation 为 09:41:10，command-ledger 文件为 09:43:40，rules-and-inputs 记 09:44:54，均早于用于 3600 秒包络的 10:12:14。恢复样本主要是约一秒的前台短命令，支持保守列支的合理性；缺少调用和 apply_patch wall，不能从封存日历时间直接推出严格的总工具 wall，也不能将未知改成违规。

工程记录的旧路径误猜、manifest 键误猜、PowerShell 通配路径错误及输出截断保留为执行元数据失败，不混成产品通过。批一夹具失败和 NAT 普通修正也保留。旧 TASK120 的 149 失败、TASK117 的 81 失败、TASK123 的 3710.557411/7200 与 3/3 测试批封存、TASK124 结束状态均按原合同继承，不重置、不挪用余量，也没有为复用而重跑原 13 方法或安全矩阵。

## 后续最小真实验证清单

以下只是供主控编排的清单，本卡没有编写或执行真实用例。须先在原工程窗口关闭确定代码问题，冻结修后源码、定向离线补证及适用独审结果，然后另行给真实运行卡。无需为 F126-01/F126-02 先耗真实 PG 资源。

资源尽量限定为一个主正常安装新集群及一个串行的中断新集群，固定同一已接受镜像/vector，使用各自独立新卷；正常安装前的拒绝反例复用主集群，不按每个反例创建容器。不访问旧 TESTONLY/用户库，不清空或自动重建失败对象。两个初始状态分别用于成功收据与中断保留，避免以删除部分安装来获得第二次空库。最终精确 CID、卷、端口、库名、OID、system_identifier、管理员/业务/快照登录、三个安装 UUID、受信配置和收据绝对路径、四根、时长及收尾权限均须在后续卡实际冻结。

1. 安装前的身份、非空和角色碰撞拒绝。入口是 D:/shspic/project_NO3_RetroLume-agent/deploy/initialize_normal.py 的 apply --config 与独立的新 --receipt。先在同一个主新空库上使用错误 OID 或 system_identifier，再由运行卡明确预构造一个非空对象、一个碰撞角色，各自观察确切拒绝原因。每次用新拒绝收据，比较安装器前后的精确目录/角色/对象状态，确认没有安装器 DDL/DCL/业务写，允许本地 intent/stopped。临时反例对象的建立与撤销由运行卡明确授权，只处理这些本轮对象；不能让另一常驻检查会话导致所有样本都只命中 other_clients 而假称测到非空/碰撞。低成本可在受控单事务核验相同查询，但完整入口的拒绝证据仍需匹配实际前置状态。

2. 新正常空库的完整安装。以修后入口显式 apply，一次执行原始 001—015，实际检查 013 后 normal/R01、014/R02、015/R03、最终原 schema_checks/q_roles 返回、vector=0.8.6 和原业务/控制表无伪造业务数据。核本地 37 条完整成功收据的每个 submitted/confirmed 阶段及文件 hash；不只观察末行 installed。身份查询实际匹配配置，连接目的地址确为 loopback，服务端 NAT IP/端口可以不同。此步才补足真实 SQL、PG 语法和多结果集 COMMIT 确认的当前缺口。

3. 新业务与快照登录的实际可用性及隔离。在同一已安装正常库分别认证，核 current_user/session_user、CONNECT、业务基本读取和快照列/导出视图读取，用实际 ROLE_CAPABILITIES/MEMBERSHIPS 核无管理、owner、传递 SET/INHERIT/ADMIN 越权。用有限只读比较、has_table_privilege、has_column_privilege 或有界事务中的拒绝检查确认 snapshot 无业务写、无维护秘密读取及无 SET 到业务/owner；不重跑原全安全矩阵。不得让安装管理员 DSN 进入业务进程。

4. 关闭配置的正常启动、同库重开和停止。使用原 D:/shspic/project_NO3_RetroLume-agent/deploy/start_local.py 的真实 --container、--port、--shutdown-stdin 接口，以业务身份和既有原生 loader 的受信配置启动。活动、integration、Q 和 preview 保持关闭，正常 source 的根与安装 UUID 对应；不能把 reader 示例当正常 source。观察实际 capabilities/readiness 和关闭原因，没有 provider/Embedding/预览请求。正常停止，再以同一库、同一身份重开，核无重迁移、控制行和业务身份不变；停止只影响本次拥有的进程/容器，保留卷和证据。无需浏览器全流程或启用外部账号。

5. 一次中断或提交未知。使用第二个独立新空状态和同一固定 SQL，选择一个已冻结阶段，以一个有界受控故障制造进程中断或 COMMIT 应答未确认。若用连接包装器，须真实执行该原 SQL，只在一次指定确认边界隐藏响应，不以 Recorder 替代事务。观察此前 confirmed、当前 submitted/unknown、真实数据库已经或可能提交的状态，无 complete/installed、无自动下一阶段/重放/清空。以原收据重复 apply 应在连接前拒绝，verify 应拒绝不完整收据；换收据对真实部分库也应零写拒绝。保留失败集群和未知事实，不自动续装。

6. 成功收据的只读 verify。回到主成功库，用同一完整成功收据执行 verify --config 与 --receipt；只提供管理员密码引用所需环境，不提供另三份秘密。实际观察 READ ONLY 查询及 schema/role/身份一致，收据原字节不变、无 DDL/DCL/业务写；另用一个错误收据绑定输入确认在连接前拒绝。若最终检查或收据故障另有具体新风险，合并到同一有限批，不默认增加新集群或全项目回归。

每步的真实进程退出、时间、对象 hash、操作归属、正常停止与失败保留均须留原始证据。实际动态失败才按其影响回到唯一修复路线，不把外部 token/计量尚缺变为上述关闭安装验证必须重复调查的前置。

## 本轮操作、偏差及交回事项

本轮仅进行 PowerShell Get-Content/rg、文件大小/hash/JSON/元数据核对，以及两个自编标准库分析脚本的文本 diff、AST 字面量和 Windows 只读文件名元数据分析。两个分析脚本分别以现有 Python -I -S -B 执行，exit 0，工具 wall 分别为 1.1195286 和 0.8942487 秒；它们没有导入或执行产品、安装器 CLI、compile/unittest、驱动连接、测试/harness/runner。原脚本及输出均保存在 audit 目录，便于复核。

本轮有一条已安装依赖的元数据读取命令因 PowerShell 数组加法拼接成单一路径而 exit 1，wall 1.2005285 秒；随后改为逐项 Join-Path 定位成功，wall 1.390684 秒。没有因此重复产品检查。部分长工具展示截断，随后按必要片段补读，不假称截断文本已完整展示。首次自编分析器只匹配字面 CREATE ROLE 而漏计 012 动态两组，且将 diff 文件标签不同当整体不等；初始 JSON 原样保留，补充 JSON明确修正两项分析器局限，未将它们当产品缺陷。

收尾格式核对首次因权限函数的通配写法含星号而 exit 1，wall 1.9528218 秒，未写 closure；已改为确切函数名。该失败只涉及本报告格式，不涉及产品或原始证据，随后继续完成保存及复读。

本卡工具 wall 精确总计为 unknown，按 1800/3600 秒保守列支，保留至少 480 秒收尾预算，闭合时刻和最终身份核对见 closure.json；1800 是列支包络，不是实测耗时。审计在许可截止 2026-10-23 09:56:00.006928 之前完成。产品导入/CLI/编译/测试、PG、Docker/Compose、端口、服务、浏览器、Job、预览、模型、Embedding、网络、费用、Git 写入、委派均为零，没有读取实际 local/private 配置、.runtime、凭据、账号后台或用户库。

只写了 TASK126/audit 内证据和本报告。源码、测试、SQL、模板、README、原证据、原结果、主控 orchestration、DocuS 和公共库均未改动。没有创建或删除 junction，没有管理既有进程，没有新增产品 Must、授权或调用额度。当前未知没有被标为通过。

主控需在唯一执行动态中登记本卡实际接收与返回、R120 的三轴结论和两个缺陷归属，按必要性同步架构/部署交接、任务登记及文档变更记录；本执行者不代写这些共享文档。原125窗口集中修正后只补受影响的连接参数和路径离线验证，保留原两批及失败账，再提交相应冻结差异核证，不重开未变业务和旧安全矩阵。

没有已解决且实际验证的新错误经验候选需要写入外部经验库。当前唯一人工动作是用户把本报告路径带回主控；不需要提供 key、开服务、释放内存、删除文件或批准当前真实安装。本文件保留为 R120 原审计结果，后续补证按轮次追加，不覆盖本轮发现，也不代替主控最终裁定。
