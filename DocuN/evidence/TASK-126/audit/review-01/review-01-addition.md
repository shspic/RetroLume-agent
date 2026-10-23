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

