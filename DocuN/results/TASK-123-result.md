# TASK-123 / R-117 修正轮01

本轮已撤销F124-01的错误操作映射，保存两份当前有效交付文档。原“继续理由交给correct”的指引有误；FR010/DR002及116 M06/学习主链已有的承载为原evaluate正常当前结果COMMIT时，同事务保存kind=progress的body.reason及进度事实。无需新增中性备注接口、字段、迁移或写入动作。原correct的争议保护、进度算法和Must均保持。

一次文档一致性核对通过，真实退出0。 本轮只核文件/JSON/文档，没有导入、compile或运行产品，没有新增测试、PG/SQL/HTTP/browser、联网、下载、模型或费用。原13方法及TASK124独立审查的readiness代码、证据和可核控制通过范围直接继承；它们不证明本轮尚未运行的真实Q语义或重开。

## 当前有效交付与准确读回合同

- [新finite-inputs.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/correction-01/finite-inputs.json)，8949字节，SHA256 79e843d4ccad235c85d24e01cd508160597cb0196baa56e686f9f96d8da0b1e5。HTML对象完整保留，原文405字节/hash、父顺序与未运行状态不变；移除allowed_local_projection。原159字节仅保留于withdrawn_reference，明确非执行、未持久化、不加入模型上下文，不把它当成实际progress.reason或任意备注接口的未来保存承诺。
- [新deployment-handoff.md](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/correction-01/deployment-handoff.md)，8781字节，SHA256 8ece65467fbc9c1ec59b0878c8dbf9564a9605324920c140d19c8879979e5f79。撤销correct映射，使用上述新finite-inputs；补齐准确progress记录、历史指针及重开读回说明。其余关闭状态、HTML、预算矩阵与外部门沿原有效范围。
- [旧到新身份与有效路径](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/correction-01/original-to-corrected.json)、[两文档有限diff](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/correction-01/documents.diff)、[函数级关系](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/correction-01/source-relations.json)。旧execution目录同名文档只作历史，不再按其错误指引操作。

progress_reason_readback_contract指向已有evaluate→progress.body.reason→原read_teaching_command/read_teaching_workspace/read_teaching_record→页面“更新或保留理由”的链。当前源码关系为B级事实，位置为teaching_repository.py的_progress_reason第19—24行、evaluate第1311—1336行及读取第1501—1544行，页面第805—807行读取reasonBody.reason；未执行产品或PG验证。

未来获准真实链先按原evaluate业务键GET已有提交事实，定位同事务COMMIT的kind=progress及准确record ID/hash，核反馈/作答/练习、来源/版本、scope/goal/revision、DataContext与state_after。记录真实reason、observations的独立/辅助/争议依据、support_checks、advance及node_before/node_after。单次复测可以保留节点；满足原独立实例与推进前置才按既有规则处理，没有可推进节点时保存真实保留理由。

下一明确动作前保存本次progress ID/hash并GET workspace/record核既有页面。后续动作如改变head.reason_record_id，读取这条准确历史记录，不能用新head替代旧理由；未来实际重开仍核同记录/body/hash及进度。只截理由页面不证明持久化。本轮真实record/feedback/answer/原business_key、body hash及全部绑定仍null，不写假UUID或参考reason，不为保存理由额外POST纠错、选节点、作答、目标或其它动作，不新增模型/query次数，也不剔除任何真实独立作答依据。

OBS124-01按原独审维持非阻塞配置风险。新交接只明确模型及returned_models身份栏应填可公开模型别名，不能填密钥、密钥hash或私有标签；字符正则不能保证识别任意误填秘密。本轮没有因此修改产品或扩大门槛。

## 原字节与通过范围保护

开工核35项锁定输入匹配；pre/保存旧两文档与原报告原字节。旧finite-inputs为5065字节/hash9fd4b9fcfb2b800ceb62a5668a197aeeada71baf9c3d058e7f78abed60b63c90，旧handoff为6797字节/hashe972c8c96c7443bd7c71a4f92a602b9177caee5fc7d95a524661bdca5169637c，两者均保留，未追改原错误结论。

原六个产品/测试/README/deploy文件维持各自post hash；原execution下49个文件（含旧manifest/save-proof）不动。原delivery-manifest的48条身份按47个原文件加原报告原字节后缀保留。原TASK124报告及主控裁定、原13方法、旧失败/unknown、122矩阵和固定样本均未改。没有写共享DocuS、公共规则或记忆。

一次document-consistency.json记录这些身份保护、原报告后缀、两份JSON/文档意图与引用、HTML/撤销参考的长度/hash、真实字段全null以及函数级关系；同根save-proof.json保存复读结果。它们只证明本轮文档与静态源码关系，不冒称新独审或产品运行。

## 真实命令、退出与预算

在项目根仅执行本轮标准库文档脚本，实际命令为以下三类。

```text
python -I -S DocuN/evidence/TASK-123/execution/correction-01/correct_documents.py prepare
python -I -S DocuN/evidence/TASK-123/execution/correction-01/correct_documents.py write
python -I -S DocuN/evidence/TASK-123/execution/correction-01/correct_documents.py check
```

prepare首次退出1，原因是把permit的contract_sha256误用于含历史整卡；实际许可绑定10235字节contract.md，dispatch-readback及实读确认其为当前整卡精确前缀。按此实际对象更正后prepare退出0、35输入匹配，没有冻结漂移。write退出0。check为本轮唯一一次文档一致性核对，真实退出和逐项判定记录在同根document-consistency.json，未重试旧失败或重跑产品测试。

[本轮工具账](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/correction-01/tool-ledger.json) 与 [预算](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/correction-01/budget.json) 保留实际命令wall和未测项。进入收尾前命令wall观测13.0404908秒、文档工具观测2.573秒，另保守20秒未测开销及120秒保存/唯一核对预留，本轮保守新增156/600秒；并非精确全量实测。原保守3554.557411秒不退款，累计3710.557411/7200，剩余3489.442589秒。人工转交/独审等待未计为本轮工具wall，原三测试批3/3封存、原截止2026-10-23 00:19:11.451055+08不延长。客户端Codex desktop，具体模型ID与累计token未知，原窗口承接常规文档修正，未委派。

## 交回与本轮终点

两文档执行含义更正后交主控限定文档核对收口。执行者未自签F124-01关闭或TASK123整包通过；原独立代码结论直接继承，不预设新增全面独审或重跑13方法。旧审计的不通过原文与原控制/失败/unknown原样保留。

Q分词/模板、Embedding容量和本人账号适用性等外部门继续缺失，Q/normal/T0仍冻结，真实provider与费用0。89动作/28Must/24片6批、100/25及固定分额不变；L01/L05真实语义、恢复和STEP018/019/020、M1、项目、发布均未因本文修正而通过。唯一状态账及正式文档同步和最终裁定由主控维护。

## 原报告原字节保留

以下为修正前15558字节报告的完整原字节后缀，SHA256 d64c3abb832589ab9f826e0327f97a64bd1c2df7c62a9d4b63684f2549886c36。其旧correct映射已被本轮两份有效文档撤销，只作历史，不能按旧操作指引执行。


# TASK-123 / R-117 计量与正常readiness工程结果

## 交付结论与范围

工程交付完成。本卡允许的版本化只读 readiness、精确有限输入、关闭状态部署交接和稳定差异包均已保存；最终13项离线方法通过。计量结论为当前不具备 Q 启用依据，输入分词/完整服务模板的版本适用性、Embedding 单项与保守整批容量及账号适用事实仍缺。该外部阻塞不撤销独立完成的工程交付，也没有被填写为 verified。

本轮接收身份为 A+ 增强工程执行者，项目根 D:/shspic/project_NO3_RetroLume-agent，task_model/07、V4.0/公共AGENTS CHG-0003，父STEP018，NFR002/003/005、SEC001/002/003、DR002沿卡面。客户端为 Codex desktop，具体模型 ID 与累计 token 未知；A+ 是用户资源标签。用户要求继续TASK122窗口，当前可见上下文没有原执行聊天，已按固定结果与指纹接续，不声称恢复缺失上下文。未委派，不使用独审窗口。

工程为内部候选及真实离线证据，最终验收归主控；本结果不自签独立审计、Q启用、STEP018/019/020、M1、项目或发布通过。

## 证据导航与实际差异

证据根为 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/。

- [计量逐项证据](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/metering-evidence.json) 与 [简短结论](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/metering-verdict.md)。
- [精确输入](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/finite-inputs.json) 与 [部署交接](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/deployment-handoff.md)。
- [统一产品diff](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/product.diff)、[pre副本索引](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/pre-snapshot.json)、[post字节与hash](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/post-snapshot.json)。pre/ 下保留四个原文件原字节，两个新增文件的pre明确不存在。
- [最终离线批次](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/batch3/summary.json)、[实际命令与测试字节](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/batch3/command.json)、[原始stderr字节](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/batch3/stderr.bin)。
- [最终文件一致性](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/final-consistency.json)、[失败与限制](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/deviations-and-limits.json)、[资源预算](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/budget.json)。保存复读及全包身份以同根 delivery-manifest.json、save-proof.json 为准，二者不自引用。

产品/测试/用户说明仅变化六个允许文件。

- backend/app/main.py 从11707到12346字节。保留原装载/关闭/绑定顺序，只留存候选对象、启动当次embedding key存在性和最终脱敏快照。post SHA256 da3f864b469dcf38d5fa699044fca454b2844f1e9ead93c44bade74f0896a41e。
- backend/app/activities/api.py 从26985到27107字节。现GET只增加 diagnostics.readiness，原认证、q_approval及storage/memory probe保留。post SHA256 865583497763dd7c853b6dbbcb5aa14bc7be69f508a3bc357b86f022dec2fdb9。
- backend/app/q_readiness.py 新增9549字节。纯启动投影与快照复制，校验已装载对象的形状/相互一致性，错误只给稳定原因。post SHA256 9644904e802283adb9ac575fcdf59ab6c7bd02fb8083ae58f48c8c37a0f2d063。
- backend/tests/test_q_readiness.py 新增15510字节。七个新行为方法与合成夹具。post SHA256 612acc3f77011b15cffb94409104b916a9c96852ed329b5560fcce2d95340a96。
- README.md 从26346到26915字节，仅补诊断说明。post SHA256 0410c7573027f7f6e75635c3a8d050e2be375d98ab0a4b503ddf3e076104d938。
- deploy/q-approval.md 从5499到6400字节，解释字段分层、未知与原GET探测。post SHA256 0a3a44dd445de0b92fbdf5f9aea21c40b8ad7a42969b3f46e94885322c33cb60。

未修改service_config、retrieval loader、Grant/manifest schema、审批/计费协议、gateway/transport/worker、001—015、repository/费用事务、前端/dist、selector/runtime/profile权限、依赖锁、DocuS或公共库。原TASK120/121、TASK122准备原件与主控orchestration保持。

## 计量的已证关系与外部阻塞

已证B级产品关系是完整线上canonical JSON字节W和原始文本UTF8字节U的 U≤W。分词预处理、文本token T、完整模板/特殊token开销F必须另证，不能直接把W叫token。逐阶段非扩张所需条件及容量逻辑反例在metering-evidence.json，未把假设机制说成当前服务实现。

本轮当前官方API/价格定义补到一项有用结论。thinking.type=disabled选择非思考；reasoning_tokens属于completion明细，max_tokens限制生成总量，公开扣费按输入/输出总token。按该契约推导，输出预算覆盖reasoning明细，无须在max_tokens外再放无界reasoning预算。该项是文档推论，不是服务实测，不断言实际reasoning为零，不补齐本人账号报价。原始返回与一手链接见 [计量结论](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/metering-verdict.md)。

DeepSeek当前价格页把deepseek-flash对应1017，官方同名仓库存在；尚未取得其tokenizer、normalize/pretokenize和模板原件，完整commit、原件hash和服务部署字节对应为null。官方元数据脚本先受限执行、后经正常平台审批执行，均URLError，分别0.047和42.14秒；脚本外层退出0仅说明已保存失败记录。分词/模板三个网页正文也不可访问。没有模型权重、解包、依赖下载/安装或远程代码执行。原件下载累计0字节；web工具返回记录作为新原始取得材料保存，不冒充源文件hash。许可证只有官方页面的MIT标注线索，没有取得LICENSE原件，未正式采用第三方分词资产。

因此不能证明全域W≤65536时prompt_tokens≤W+F或F≤4096。原公式未被证明为假，当前属于缺适用依据。增加margin、短样本、字数比例和余额不能补齐。Embedding-3的单项与保守整批≤3072两个门也均未闭合；四项、2048字符、4096查询字节、费用预留分别不能代替容量。限定官方文档与官方源码的两类检索没有给出可采用的专属分词依据，错误API页面路径也未取得正文，不由此断言供方资料不存在。没有用其它供应商tokenizer代替。

本轮6次web工具调用、17个子请求、4个搜索字符串；将失败文档与metadata也算入后，新增官方身份保守6/12。两家候选版本分别1/2及0/2。4个网页不可访问返回、两次下载失败保留在web-request-ledger.json、web-responses/与download-ledger.jsonl。逐项绝对请求时间没有采齐，保留unknown；实际资料日期为北京时间2026-10-22，工具wall和返回原件可核。原122的11个官方文档身份与两次已失败元数据/未知原子退出不清零。

当前外部阻塞是供应商现行分词/模板或等价计量依据，以及本人API权限、币种含税/特约、智谱权限与余额。用户只声明DeepSeek额度充足，未访问后台。供应商问题原文已保存但未发送，不重复弹问用户。沿122公开数据条款披露，未新加零留存/不训练条件。没有可填写true的完整token上界资格或启用回执。

若以后只能得到有限精确计数，最小条件方案是在现payload builder生成规范字节之后、原grant.check/准入/发送之前拒绝未覆盖payload，并独立核Embedding逐项与整批容量；本卡没有修改这些门或接口。下一步取得外部依据，不再建议同样浏览/协议设计卡。

## readiness实际行为与证据边界

diagnostics.readiness 的schema为retrolume.q-readiness.v1。candidate/effective区分装载前置与最终外发关闭原因，保留严格配置allowlist、服务timeout/request/response/output、活动默认输出与按动作输出门、Embedding维度/批量/文本限额。未装载或装载器未保留的事实用null/unknown，不把示例配置投影成已装载候选。

两个key只显示启动存在性；model坏/缺配置时可为null，明确缺key时false，存在也不产生资格。只读GET复制启动快照，重复读取不重读配置、环境或授权材料。已装载grant/manifest只说明形状与相互摘要/对象匹配，price/activation/instance仅摘要引用，内容和实际部署匹配未核则null。qualification保持unknown，不因声明verified、TESTONLY或key存在升级为真实外发合格。正常实例未创建，不伪造CID/OID/SID。

认证/同源/DataContext与R01/R02只读边界不改；新增投影不查询PG、不调用configure_application/QAuthority.bind/ControlHub/operator_ledger，不写批准或事件日志。原GET的storage/memory探测保持，所以完整入口只在未来获准正常运行时使用。已测错误响应与诊断/日志无合成秘密、DSN/私有路径、异常原文或key字段；不是对任意未来代码的无限泄露保证。

## 精确输入与后续部署

finite-inputs.json补齐171字符/405 UTF8字节的HTML focus与53字符/159字节的继续理由。各自SHA256分别c4c8ff9522d7e5522858d764133050bf012826a48877151c8f016c7128e4e6fb、9563a959fa373da25d4b347c84d2b1f5aa198cfe026d9945e750715ba9b5bf2a。文本逐字绑定116 L10和L01/L05 rubric、原N及numeric/retest输入，未修改原文/答案/要求或编造已成功输出。

HTML映射到现HtmlCommand.focus，父仅允许Q01.03.model当前合格feedback，位于Q01.04.query前。继续理由沿现correct文本保存，当前真实父/业务键/CAS等为null，不新造advance接口、不改变进度判据。真实source/version/fragment排序、父record/hash、typed/payload、config、description/artifact/控件ID与批准均待获准部署后冻结。

28Must、89动作、24片/6索引及22.25元预留按主控已采用基线引用，没有运行分片或重算已充分预算。学习43/48、面试28/28、补证18/24，面试无失败余量，尚未运行的真实语义不保证通过。真实调用/费用仍0。

deployment-handoff.md以122原runbook为主体补差异。真实start_local只有--container/--port/--shutdown-stdin等现存参数；initialize-materials仅应用001，不能完成当前normal迁移链与角色。没有编造--profile/--initialize/--migrate命令，没有运行旧runner或创建资源。首次receipt.TASK谱系未定，原白名单未改，后续由主控固定真实授权再判断定向兼容。

## 离线方法、失败与资源账

实际命令均从项目根执行，原始子进程argv、cwd、仅四个系统/临时路径变量的白名单环境、运行时包版本和六个测试输入文件的准确字节/hash保存在各batch的command.json。测试专用配置只含合成数据；不读不传真实provider key、DSN或私配，不启动真实Q loader/QAuthority。backend原有venv只读复用，不修改锁或安装产品依赖。

```text
python -I -S DocuN/evidence/TASK-123/execution/run_offline_tests.py batch1
python -I -S DocuN/evidence/TASK-123/execution/run_offline_tests.py batch2
python -I -S DocuN/evidence/TASK-123/execution/run_offline_tests.py batch3
```

首批120.031秒在首个TestClient入口超时，父进程按timeout处理，completion中的124是超时状态映射，工具外层退出1，不冒充原生子进程退出码或通过。第二批只诊断同一首方法，20秒faulthandler产生真实线程栈后退出1，父计20.453秒。栈在Windows socket._fallback_socketpair.accept和事件循环初始化，尚未进入API请求。

最后一批经平台正常require_escalated审批运行，产品及测试源码保持最终字节，白名单环境和全部tripwire保持；父计1.828秒、退出0，13方法无failure/error/skip。成功支持前两批是沙箱内事件循环内部socketpair受阻的判断，不删除原超时。原schema遮蔽及Starlette/httpx弃用警告保留，未升级依赖。没有第四批行为测试。

通过覆盖缺/坏/关闭配置、任一key缺失、key存在无grant仍关闭、候选与最终门/限额/严格allowlist、声明verified和TESTONLY不升级资格、重复GET不增加loader/bind/批准/PG操作、原storage/memory各一次probe保持、session/跨站拒绝、合成R01/R02只读上下文GET与stale/readonly POST拒绝、错误与秘密脱敏。新增7方法加直接影响的既有配置/活动6方法。所有11个外执行tripwire计数为0，包括PG connect、ControlHub、Q loader/bind/approve、operator_ledger、真实transport及AsyncClient.send。R01/R02是合成上下文方法，不冒充真实PG profile验证。

初始列表中旧capabilities_without_storage方法尚未运行；其原断言与pre main既有关闭覆盖冲突，最终改选原guard_rejections，并由新方法分别验证candidate缺key与effective关闭。未改写/删除旧测试，未将未运行项称通过。另有4个猜测源文件路径不存在和系统Python缺fastapi元数据的资料读取失败，均记录；随后用实际存在路径和已接受venv，未记成新产品失败。

最终post源码与batch3测试字节一致，43项开工输入指纹均匹配；未变化输入重新核身份保持。最终只作文件/JSON/AST/文档一致性与保存复读，没有复跑122分片/算术、120/121安全矩阵、构建或真实服务。

预算见budget.json。新许可7200工具秒，精确工具总wall因早期截断/未逐项记录为unknown，未伪报全量实测。以permit签发至收尾2654.557411秒，加并行/未记录300秒及600秒收尾预留，保守记账3554.557411秒，尚余3645.442589秒；此为包络而非实测工具wall。日历截止北京时间2026-10-23 00:19:11.451055未到，收尾实际间隔由save-proof记录。具体模型与新增token累计未知。

原TASK122保守1340.9775537/2400、已知实测37.4398905秒、至少2元数据失败及未知子退出/计时保持。原120 wall69357.418110、holding2943.704295、149失败及117旧81、root/PG64/64均不恢复或清零。当前新增provider/实际费用/PG/SQL/Docker/API服务/browser/Job/preview/Git写/委派均0；TestClient为获准的进程内合成请求，未启动HTTP服务器。未扫描或操作旧运行资源，不冒称重新核齐旧停止状态。

## 交回主控的事项

建议采用本卡工程与有限文字作为稳定候选，保留上述计量/账号外部阻塞。新增秘密投影、资格解释和后续计量依据的采用由主控按实际风险安排相应一次独立增量审查；执行者普通Review不替代独审，旧120/121不重审。本轮没有可写入外部经验库的已核新经验提交，未改公共库或记忆。

待主控在唯一执行动态、架构动态和变更记录同步实际接收/工程交付、计量部分已证与仍缺、13方法及两次夹具退出、新字段、有限输入、预算和下一外部门；编号由主控串行维护，本卡未写共享账。最终账号答复和供应商适用材料齐备前保持disabled。正常部署、真实Must矩阵与首次启用须主控另给精确资源和实际授权，不再派同样查核设计卡，也不从草案推导已通过。
