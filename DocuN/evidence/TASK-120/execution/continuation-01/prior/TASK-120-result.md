# TASK-120 / R-114 工程结果与停止断点

**工程候选尚未完成。协议、五入口接线、前端与最终正式构建已保存；真实 PG 通过一条索引及两条查询链，教学模型链、其余业务链、100 临界和最终浏览器验证未通过／未运行。8 个运行根额度已用完，已精确停止；真实 Q 继续冻结，不能作为稳定完整采用包放行。**

接收者：主控，后续独审仍由主控另卡安排。客户端为 Codex desktop 原工程会话；A+ 为路由标签，实际精确型号未可靠暴露。保存日期：2026-10-19（Asia/Shanghai）。本结果没有修改 DocuS 或共享任务状态。

## 1. 本轮交付与可复核身份

项目根 `D:/shspic/project_NO3_RetroLume-agent`。依据 TASK-120、TASK-119 采用修订 K1/K2、100／25／48-28-24 及原用户批准；V4.0／CHG-0003 七个锁定规则指纹最终复核一致。不读取公共库后来版本代替合同，不生成真实 T0、正常激活根或可部署票据。

- [最终文件身份](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/execution/final-file-identities.json)：首点 616 项匹配，保留 94 份可编辑源 preimage；最终 40 项既有文件变化、26 项新增文件，无未解释的基线漂移。001—014、依赖和锁文件、固定 renderer／host、旧证据和归档原件未改。
- [完整源差异](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/execution/source.diff)、[审阅文件包](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/execution/final-review-files.zip)。ZIP SHA256：`462f0c57bda62dfdbbb946d9af497f951b0e295c3c0aa8e8d6c7516781a07ffe`。包内含源 pre/post、差异及完整最终 dist，不含本机秘密、私有配置或可用 Q 批准权。旧 dist 原字节未预先复制，只保留原哈希；源 preimage 为原字节，不能把最终 dist 哈希冒作旧构建身份。
- [用例—合同索引](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/execution/case-index.json)、[启用及工程余缺](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/execution/remaining-readiness.json)、[规则核对](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/execution/final-rules-check.json)。A 为实际运行，B 为隔离／结构证明，C 为未执行声明；推断不替代真实 PG 或浏览器结果。

## 2. A—D 实现范围

**A：协议与本机权限。** 新增 `q_protocol.py`、`q_context.py`、`q_gateway.py`、`q_store.py`、`q_kernel.py` 和 operator 模块。严格解析重复 key／非有限值，绑定 typed request、provider 对象及规范发送字节；有限文本用途、来源、当前父与实例资格分别检查。K1 在真实 journal 锁内确定 event_seq，DecisionBody 不含自身 approval_id；批准、过期、续批、撤销及 claim 有界处理。批准只经本机 operator inspect／approve／revoke，不新增 HTTP 批准接口。

Q admission intent 的 PID/birth 与短生命周期 Windows kernel event 只用于识别在途或丢确认；observed、关闭及缺尾不能提供余额。事件在实际准入完成／失败后关闭，不能仅凭仍活着的进程恢复新权利。私有目录及 SID／ACL 是实际信任边界；同 principal 的受信代码不是被 Python API 隔离的攻击者。

**B：五入口。** 教学、面试、检索、旧 learning、HTML description 均接入 accepted／freeze 后准备、GET 投影、等待及原键显式继续。检索先准备全部批；legacy first 保留私有 intent 和原单槽。五处 UI 已接入状态和实际 provider／用途告知，保留 IDB 与原键；本轮补了教学恢复和旧 learning 在异步 GET 后的身份检查。新 UI 行为尚无最终浏览器实证。

**C：锁与 PG。** 双 provider 的生产准入仍使用原固定全局 advisory 锁、真实 roster SUM、活动和 operation 同事务预扣；无新金融模型、退款或 SUP 触账。Q shared lease 在 transport 完成／异常后、结果事务前释放，结果写回先排他 policy、再 MutationGate／PG；释放间隔失效时保留不可变结果而抑制 head。

为消除实测父进程等待子进程时的 Q 排他锁阻塞，`main.selection_guard` 的 Q 分支改为短身份检查后释放再 await，并在返回前核当前身份；`worker.launcher` 的 Q 分支在交接后、等待前释放父 data permit。`owned_service` 的 Q 注册段缩短，非 Q 原持锁生命周期保留。这些是 K2 的实际运行改动，须由后续独审重点核查，不能仅凭注释认定安全。实际 embedding 的结果事务已经完成；模型结果与释放间隔并发仍未证实。

**D：惰性配置与说明。** 示例使用候选 deepseek-flash／thinking disabled，embedding-3／512 不变，returned_models 仍为空且 Q 默认关闭。未填写真实价格／账号／审计／T0。新增 [operator 部署说明](D:/shspic/project_NO3_RetroLume-agent/deploy/q-approval.md)，README 已关联。v1 的 80／20 与原 wire3 保留；v2 为共同 100／25、48-28-24，不叠加旧额。旧 wire4 全边界没有重新跑，不宣称完整新增兼容通过。

## 3. 实际验证与未验证部分

| 范围 | 实际结果 | 直接证据 |
|---|---|---|
| K1、规范字节、有限用途、旧 wire3／Q wire4、私有根失效、锁与清场 | 19 项定向检查通过；其中多数是隔离证明，不能冒 PG currentness | `command-025.log`、receipt |
| 正常惰性配置、非法 operator 路径类型 | 新增 2 项通过；未读取用户配置或环境秘密 | `command-028.log`、receipt |
| 最终 TypeScript／正式 build | 通过；最后构建为 command-027 | `command-026`、`command-027`、`final-bundle-identities.json` |
| R02 隔离初始化 | flow、budget-01 均完成，源绑定与三个活动通过生产仓储建立，无金融行 seed | `bootstrap-result.json`、两份 bootstrap／q-binding |
| 原教学等待与批准 | accepted、GET、真实 operator approve、可继续投影曾通过；原启动转 UNKNOWN | root-06 timeline、root-07 原 PG 只读观察 |
| 实际检索 | 一次 source_index、两次 query 经真实 HTTP／Windows SUP／PG admit、mark、007 和领域结果提交；最低 transport 为零外发合成替身 | root-08 两份 HTTP timeline、`flow-committed-receipts.json`、events |
| 教学 query→model→领域 COMMIT | 查询已提交；模型前被原 UNKNOWN 父槽拒绝，未通过 | root-08 batch-01／02 failure、child.log |
| 面试 query→model、旧 learning、HTML description | 代码已接线，合并 fixture 在教学处退出后未执行 | case C10；不写通过 |
| K2 release-gap／source／memory／head 并发 | 保存了定向 fixture；模型并发和失效结果保留未运行 | case C11；不以隔离锁测试替代 |
| 99→100 两 provider 共同预算 | 未证明；旧失败窗口保留，修复版预算子批未执行 | root-07 batch-03、`root08-unexecuted-next-batch.json` |
| 最终 browser JS/CSS 响应 hash、五 UI 流与迟到围栏 | Browser start=0，未运行；只固定正式 build 文件哈希 | case C13 |

完整身份、原命令、exit、耗时、源 as-run 和失败原件均在 execution 目录；上述短文件名相对于该目录。三份真实 embedding 成功回执不是停止后的全库 SUM 回读，不能据此重建金融权威或声称最终预算总账已重新核实。

HTML TESTONLY 部署票据得到用户本轮明确许可，采用原正常验签器与已核固定 host 身份，签名密钥只在内存／子进程环境中。`command-021` host 检查通过，但 HTML 模型链未执行。preview create／start 均为 0。

有限模板正例仍不包括本轮实际已选记忆的完整模型链；未批准 answer／history／memory／外部 parent 的全部真实 PG 反例、ACK 丢失、复制实例、导出恢复权利关闭等矩阵未补齐。旧 S08 和原恢复有效证据只继承未变边界，不代表新 v2 已通过。

## 4. 失败、修正与确切停止原因

历史失败未擦除。早期记录包括 Windows hardlink／Selector socketpair、测试 Job 进程计数、fixture atoms 越界、构建命令／类型错误、Docker 管道权限、同簇角色初始化与 PG 控制门等。对应成功修正有原 exit、receipt 和 as-run，不将原失败改绿。第二库沿既有角色初始化时，仅在隔离 fixture 核同名非登录角色后跳过已存在的 CREATE ROLE／碰撞 guard；001—014 文件未改，细节在 `budget01-root02-migration-reconciliation.json` 和 setup.py。

本次断点补做：

1. command-025 通过新增短期 admission kernel witness 等 19 项检查；command-026／027 固定最终前端；command-028 通过正常配置 2 项。
2. Root07 实际回读：原教学键 `1f5c659f-4a5a-4fee-bfbe-3f245eb5bc7e` 已 claim、status=unknown，当时 operation 与请求／费用预留均为 0。该键没有再发。API 启动门实测 470081536 bytes，低于 512 MiB，未启动该批 API。
3. Root07 budget 先领取真实 300 秒窗口、再 accept 教学命令，被生产仓储拒绝“运行窗口尚未收尾”。因此未建立 99 次基线；遗留窗口不能写成已结算或 0。离线已保存逐笔 accept／claim／真实耗时 settle 的修正，以及过期旧窗口仅通过生产折叠核销的逻辑，但修正未执行；未创建 budget-02。
4. Root08 API 门恢复达标，三次实际 embedding 成功。新教学键仍遇 unknown_slot：显式 abandon 只保留旧未知事实，不释放其 semantic slot；同正文保存目标是无效果提交，原 head 仍 revision=1／goal_version=1。夹具“同目标保存就能新建父槽”的假设错误，不能通过改 SQL、松断言或借新批准重发解决。两份错误路径保留，正常教学／下游链未完成。
5. Root08 manager 的下一子批等待于 23:42:10 UTC 左右到期，运行根在 **2026-10-18 23:42:12.078833 UTC** 完成清场。预算 batch-03 文件实际最后写入 **23:42:21.319665 UTC**，晚于退出，没有 child／receipt，也没有执行效果。执行者未及时提交子批是本轮遗漏，不能把已保存指令算成已执行，更不能以该文件重开第 9 根。时间原件见 `root08-next-batch-timing.json`。
6. 最终只读停止脚本先暴露 JobOpenError 类型和早期 metadata 事件 shape 两处诊断错误，均保留后修正；最终证明成功。其它元数据读取／引用纠正见 `resume-metadata-corrections.json`。

## 5. 累计预算与精确清场

原首工具 UTC：`2026-10-18T08:41:08.5687758Z`；原 96 小时截止：`2026-10-22T08:41:08.5687758Z`，最后 1800 秒仅清场保存。中断／审批等待没有计成活动 wall；活动与 TESTONLY grant 自身 deadline 仍单独有效，不能因续接延期。

| 项目 | 本卡累计／上限 |
|---|---:|
| 运行根 | **8／8，硬门已达** |
| PG create 尝试／实际对象 | 1／2；1／1 |
| volume create 尝试／实际卷 | 1／2；1／1 |
| PG start、API start、Browser start | 7／8；5／8；0／8 |
| 正式 build | **4／4**，含首个命令失败 |
| native 业务会话、HTTP | 4／32；31／3000 |
| preview create／start、真实 provider、实际费用、Git 写 | 均 0 |

HTTP 31 与五份原始 timeline 的请求数合计一致。新失败账为 **25 条登记**，包括根与其子批重复引用、诊断和元数据纠正，不等于 25 个独立产品缺陷。原 TASK117 的 81 条失败及 root25、PG对象6、PGstart46、API33、Browser19、build8、Native140、HTTP2486、preview各2 原账只读保留，不能把本卡的 0 外发写成全项目计数清零。

受控离线命令 wall 累计 208.516 秒、runtime 命令 290.079 秒；资源持有并集 267.641 秒。另保留首控制器前 1840.326332 秒上界与未聚合元数据 7200 秒不确定性预留，命令 wall 保守总上界 **9538.921332／14400 秒**。这些上界不是精确实测投入；手工阅读／编辑总投入 unknown。时间仍有余量不恢复已用完的根和 build 次数。

[最终实时停止证明](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-120/execution/final-stop-proof.json) 核对 8 个精确命名 Job、23 个登记 PID/birth：原身份均不在运行，自有 Job 不存在或无进程；active_root／active_command 均为空。

CID `b89522070d4b64fc67efed810852ccc21948058f154bf4fa1889f4d8d69a102f`，名称 retrolume-task120-qprep-pg1，标签及镜像身份一致，**Running=false／Pid=0**；PG 55480、API 18120 均未监听。容器、retrolume-task120-qprep-data 卷、flow／budget-01 数据库、原 journal、未知预留和失败保留。旧六 CID 本轮未实时查验，不声称“所有历史对象已实时停止”。

## 6. 续接与主控建议

本卡运行根硬门已经构成真实阻塞；当前不再启动 PG／API／Browser 或正式 build。剩余工作需要主控登记新的明确许可，沿用本 TASK／R、首点、原截止、旧成果、所有失败和累计账，不按新窗口清零。没有要求用户提供 key、重新批准 100／25 或释放内存的必要动作。

续接先核 final-stop-proof、budget 与 root08 未执行指令，**不要整批重跑**。必须先解决正常教学 fixture 的合法新父槽，保持原 UNKNOWN 及原键只读；复用已通过的三次检索与全部离线原件。然后完成教学／面试 query→model、legacy／HTML、K2 并发、真实共同预算和最终 UI 的未完成项；不得直接重发原 claimed 教学键，或把旧 300 秒预留清零。后续是否修改产品／前端，应以新失败事实决定；当前最终 bundle 已固定，源改动后不能继承未加载的新行为证明。

正常账号／价格税币／token-framing-reasoning／returned identity／适用增强独审和真实首次启用回执均仍 UNKNOWN。复用 TASK119 官方事实，不重复联网研究；81 次设计矩阵和 L05／F 未知继续保留。源码包仅供接续和范围审阅，**尚未达到卡面要求的稳定完整集中独审点**。

建议主控仅登记“TASK120 工程候选未完成、根额度耗尽、已停止；Q 冻结”，保留有限 S 的既有验收，不将 STEP018／019／020、M1 或项目标为通过。本窗未改正式总进度、未启动独审、未提交或发布 GitHub。
