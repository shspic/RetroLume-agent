# TASK-112 / R-106 review-01 — 独立增量终审结果

裁定：DEF-031、DEF-032、DEF-033 可关闭；E112-01 漏计账段已一次核销，历史超限 626.566 秒保留、不追认。代码轴和对应证据轴在本次范围内通过；执行控制轴的本次前向计数、账务和清场成立，历史整体合规仍不能签通过。当前候选具备交编排关闭既定 G11 有限切片的条件，没有发现本次变更引入的新确定阻断。

本结论只替代首轮对上述四项及其实际传导的未闭判断。后文首轮全文是历史原件，其当时未通过结论没有被改写。本结果不直接填写编排最终验收，不签全部 STEP、项目或发布；真实 provider、任意脚本、跨浏览器等原有限合同之外的范围仍未验证。

## 接续、身份和操作边界

项目根 D:/shspic/project_NO3_RetroLume-agent；规则入口 AGENTS.md；task_model / V4.0 / 公共 AGENTS CHG-0003，WORK 适用 2/6/8 章，阶段 07；需求 v1.2、架构 v1.21、执行动态 v2.43。本卡许可 TASK-112-G11-REVIEW01-20261012，TASK/R 没有重置。七份锁定规则身份已核，同窗未变正文复用，没有改公共库或 DocuS。

实际客户端为 Codex desktop，系统身份为基于 GPT-6；精确部署后缀和推理档未暴露，A+ 是责任配置标签。按用户请求继续原 112 独立审计会话，没有新建工程会话、没有子 Agent；平台没有提供可核窗口 ID，不冒工具确认。未参与 111 续作 07 产品修复，未继承其聊天或思考；未读 TASK-111 结果文件、candidate-summary 文件或编排本轮缺陷评价。必要 finalize 夹具差分含其输出文本模板，仅读其统计修正传播，自述没有作为通过依据。

先形成 [独立代码检查点](/D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/review-01-20261012/checkpoint-01.md)，再核原件并形成 [四项裁定检查点](/D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/review-01-20261012/checkpoint-02.md)。只读实际三产品 diff、pre/post、必要调用链、对应夹具和已有原件；只用标准库作 hash、有限 diff、JSON 日志和数值核算。产品 import/compile/test/build、PG/SQL、Docker/Job、浏览器/模型、旧 runner、Git 写操作均为零；未读取真实配置或凭据文件，registry 的加密控制字段未解密、使用或复制到结果正文。没有用剩余额度作完整终审第二轮。

## 对象身份与继承

新冻结导航含 112 项源码/必要夹具、255 份 C07 证据、5 个主要输入及 7 份规则身份，去重后 379 个对象，开工与交付前均独立重算相符。实际原有源变 5 项：三产品及 control/core；新增 7 个 C07 夹具。100 个未变原冻结源、四 runtime、最终 Panel/前端 bundle、SQL012/ACL/角色、四账与 worker、隔离规范按首轮限域结论继承，没有重验全部数学、故障或 UI。

三产品当前 SHA256：

- production_supervisor.py：71564962f3e58e57932a5859d971eeb764c81177e7c2821015c326e22e55dc8b。
- pipe.py：db2a742a559d7905012273e9fd9acaec441a549e12d71fa8ac77a3f486d3f974。
- renderer-protocol.cjs：d7907b8eb2414098162a03e7adc8d9f8953f026ad33a0ebbee8330a834755e24。

新生产 v2-08 image 为 sha256:ec3c70c7a8a8894c647a69b08b0c296727bb052f639e487567e9cd4624766789，load 为 8a047050ffe584dffa6e85222c16c8f400c0ab4db82f72a32812c2befd082b3f；四 runtime 集合仍为 6cc300164a6cb364d9bd0bae4897f06d3f6a65cf5d4272477d2bccde67312597。已独立重算本地 load 的 651 个资源 hash，全部相符；build-context 协议文件与当前产品原字节一致，原 build、实际 ready、精确容器及持久收据绑定同一新 image/load。此为已保存原件核对，没有运行新的镜像查询。

五份 pre/post hash 及独立重算 diff 相符。保存 diff 为 CRLF、重算为 LF，统一换行后全文相等；本体字节没有被改写。详见 [差分核对](/D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/review-01-20261012/actual-diff-verification.json)、[load 核对](/D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/review-01-20261012/load-manifest-independent.json) 及 frozen-start.json / frozen-end.json。

## DEF-031 / F112-01：关闭

[production_supervisor.py:286](/D:/shspic/project_NO3_RetroLume-agent/backend/app/preview/production_supervisor.py:286) 在 Event.wait 成功后核完整包接收 mono、原 min(t0+8秒,D-10秒)、当前时窗和 stop，保存观察后再鲜取时刻复核，边界相等拒绝。[接收路径:327](/D:/shspic/project_NO3_RetroLume-agent/backend/app/preview/production_supervisor.py:327) 先验身份，收到事实和接受资格分开；迟到合法包的 kernel 仍保存，置 stop，不把已 resume 对象改成未启动。实际调用在 attach resume/init 之后、ready 事务之前，t0/D 与次数没有延长或返还。

六个已有离线样本直接走产品 _read/_wait_ready 和匿名管道，全部为成功 wait：及时样本接受；8 秒相等、成功 wait 后迟到、stop 已置、收到及时但当前调度窗已闭、D-10 相等均拒绝。它们使用确定替身单调时钟，属于门级证据，不冒作真实调度。

真实 root19/late_ready 延迟同一 attach stdout 的 body 读取，合法 ready 原体 9647 字节、SHA f99ebe3e96801263c969c96616cd5112932bcfc3bc827aa009aa2758e2b39200。t0=1013201812000000，原 ready 截止=1013209812000000，完整接收=1013209875000000，即 t0 后 8.063 秒；接受时刻为空。事件 3547—3567 的状态为 registered/start_requested/stopping/stopped，没有 ready、running 或 failed_unstarted；拒输入 source_invalid、submitted_to_pipe=false。收到 ready/frame 包不等于取得 ready 资格。真实 kernel 被保留并参与完整停止，DB elapsed/settled=11、R0、starts=1，仍按原 D。

及时对照 normal_bom_header 真实接收=1013196484000000、接受=1013196515000000；合法 ACK seq1、steps6，m=2、h=4 的独立 oracle 为 78.4 J，读数及 figure 一致；实际 PNG seq2 为 640×480、20592 字节、SHA ebda4241b28d16177962a34fe553a7e246f41fb39106d60a204e9ed00b9876ae。该对照足以支持本次门修复与新 image 传播，不声称重做两 Native 或所有 UI。

## DEF-032 / F112-03：关闭

[pipe.py:64](/D:/shspic/project_NO3_RetroLume-agent/backend/app/preview/pipe.py:64) 将底层 OSError/ValueError 包成 PipeReadError，与真实空读 EOFError 分开；它仍属于 PipeError/ValueError，原 framing、限长、identity/hash 与调用者协议拒绝不放宽。[stdout/stderr:357](/D:/shspic/project_NO3_RetroLume-agent/backend/app/preview/production_supervisor.py:357) 保留读取错误，即使后续排空观察到 EOF 也不擦除；stderr 最多保存前 8192，继续排空并统计全部，空读才置 EOF，异常或线程退出不冒 EOF。[停止与持久结算门:303](/D:/shspic/project_NO3_RetroLume-agent/backend/app/preview/production_supervisor.py:303) 对已启动对象共同要求实际双 EOF、无读异常、attach/线程结束及原 StopProof/原 D；未启动路径仍按原事实判定。

九组已有离线门方法覆盖空流、8192、8193、分块 10000、9216 后真实读异常、线程结束无 EOF、缺 stdout EOF、EOF 后仍有读错、stdout PipeReadError。前四组排空且无错才可结算；缺 EOF/错误组不结算。该证据没有被提升为 Linux/Job 或 PG 事务证明。

真实 root19/stderr_overflow 对准确 CID、Node PID7 和 birth ticks3781 写入有限 12289 个 x 字节；原调用 code0，完整统计 12289、文件恰为前 8192 个 x、overflow=true，停止后两 EOF=true、两 error=null。准确内核、wait/die、两 Job 和持久确认原件相符；elapsed/settled=8、R0、starts=1。

最终 root20/stderr_no_eof 对真实关闭的同一 stderr 读端执行 read，得到 ValueError，stderr EOF=false；supervisor confirmed=false、tree unconfirmed，DB cleanup_unconfirmed、R60、elapsed null、settled0、starts1，拒新 start 为 cleanup_unconfirmed 且保留60。父进程退出后，触发前已持有的真实读副本才取得双 EOF；观测者只有读/同步句柄，无 Job/写端，不与存活 reader 争读，也没有外部物理 kill。其 EOF 原件、parent/attach birth、private Job 前提及 job_destroyed/error2/实例结束证据逐项对应，再同一控制根恢复为 stopped、elapsed/settled60、R0、starts1，消费全 R，没有 UNKNOWN 退款。

首个 root19 同名方法失败是 ClosedActualStderr 缺 closed 属性：真实读错已进入 UNKNOWN，但 JobChild.close 读属性时报 AttributeError，未产生 supervisor-result；该失败及同根满 R60 恢复全部保留，没有退尝试。actor 保存 before SHA 0e14f0b5e2be619c0e07aabdc9f0384e2bb6fffd876f3147ba2bd540c9054ce8，当前 33fdf59fa8dbf4aad9729c851f382110e04245ac7d493c027b016da544240625，真实 diff 只有转发 raw.closed 的 property。七方法 as-run 的 111 项源快照与当前源相比，只有 root19 actor 的该差异；前五方法不调用此 wrapper，可继承，root20 只复验未 EOF 方法。

七个新 session 的 elapsed 为 9/11/8/6/7/60/60；准确 CID/image/nonce、private PID/init、outer UID/capability/seccomp、kernel hash、wait/die、两 Job 真实零或严格销毁、实际 EOF、DB confirmation 与源 proof 相等均成立。精确终端原 stdout 含 47 个停止对象（含 PG 与新七对象），39 个准确进程实例已结束或 PID 已换 birth；两个端口无监听，active_batch=null。只证明原件观测时点及自有工作树，不冒 cgroup 删除、完全释放或当前查询。

旧25（542b0750-6e02-418a-b216-5dfbd3b93047）仍 cleanup_unconfirmed、R60、elapsed null。当前新标志、清场或恢复没有解除旧缺 kernel/EOF，也没有向首轮正常收据补填新字段。详见 [七停止独立核对](/D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/review-01-20261012/seven-stops-independent.json) 和 [夹具 as-run 核对](/D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/review-01-20261012/fixture-as-run-independent.json)。

## DEF-033 / F112-02：关闭

[renderer-protocol.cjs:9](/D:/shspic/project_NO3_RetroLume-agent/deploy/preview/renderer-protocol.cjs:9) 比较 canonical UTF-8 Buffer 与原始 bytes，TextDecoder 的 BOM 去除不再形成漏口；[validateInit:19](/D:/shspic/project_NO3_RetroLume-agent/deploy/preview/renderer-protocol.cjs:19) 对存在 constraints 键要求数组，之后仍走原 runtime.validate、description hash、renderer 身份链。缺省/[] 合法，显式 null 及其他非数组拒绝，字符串内 U+FEFF 保持数据。

真实宿主 [stdin 入口:153](/D:/shspic/project_NO3_RetroLume-agent/deploy/preview/renderer-host.cjs:153) 顺序为 prefix/header → decodeHeader → body 长度/hash → boundedJSON → initialize/validateInit → browser 身份与 launch，两个新防线均在实际路径；没有另接旁路 helper、放宽 Python 前置、四 runtime、编译包或 SQL 身份。

已有 Python/Node 十组接受域一致：缺省、[]、内部 U+FEFF 通过；null、string、object、number、bool、BOM header/body 拒绝。初次 cross-realm VM 使合法对象在 runtime 原型检查失败，保留原失败；同 realm CJS wrapper 只修夹具，实际宿主源码通过 stdin event 走到固定 browser 边界，真实浏览器未启动。wrapper 的 new Function 是离线加载固定宿主源码的方法，不是产品新增任意 JS 能力。

真实 root19 三 wire 的长度、hash、identity/canonical 原字节均独立核对：null init body1595/总1990，constraints=null 的 description hash也正确，但实际 Node 在 description_constraints_type 拒绝且无 ready；DB 合法 terminal artifact 的 identity/hash 前后保留，变动仅在 wire。BOM header 为 input seq2，先有合法 ready 和 ACK seq1；BOM body 为 input seq1，先有 ready，二者均停止于 protocol_failed 并完整结算。这是实际输入协议拒绝，不混为非法模型成果提交。详见 [入口十例核对](/D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/review-01-20261012/node-ingress-originals-verification.json) 及 [真实 wire/门/oracle 核对](/D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/review-01-20261012/live-packets-and-gates-independent.json)。

## E112-01、执行控制及真实剩余

原 root6 事件109结束 mono869276343000000，独立 cleanup 的 PG stop code0、确认 mono871556046000000；原 PG inspect raw hash 相符、准确唯一 PG 在 cleanup 前仍 running/PID945。两端相减为2279.703秒。连续持有基于唯一 PG 与无中间停启记录的保守推断，物理停机瞬时未采；没有拿最终 Stopped 倒填精确历史。

pre budget SHA bdb3af4d02a052f05ee284fe04d5e002cb62d2baf186345ce1fca030343f2ae6 相符。adjustment 文件、唯一事件3508内 adjustment、最终与现 budget 的唯一 execution_time_adjustments 全文相等，counter_changes=false。14546.863+2279.703=16826.566，旧上限16200仍超626.566，not_retroactively_authorized=true。漏记项可核销关闭，历史超限事实不能签通过，没有再加一次或返 counts。

3668 条原事件连续，计数独立重算与当前/最终账一致；继承首轮已定位的三笔迟记 internal 与两批事后 offline，没有伪造事前 reserved。真实 root19=155.328、root20=13.329，共168.657/2400，余2231.343；累计16826.566+168.657=16995.223/20400，余3404.777。两根 start/期限、PG start、停止确认与并集顺序相符，中间 PG 实际停止；cleanup 的0.860与0.969已从 cleanup 分类扣回、包含在各根 real，不双计。batch elapsed 先采样再落盘，事件时戳的外围延迟不替代计时终点。

真实次数及余额：

- 根20/20、PG starts16/16；两者余0。image8/9余1；create52/55、start48/51各余3。名字56—62各分配一次，63—65未用，失败61没有退次数。
- API12/12、主 browser11/11余0；模型/OneCall9/10各余1，frontend4/5余1，均未增加。HTTP1611/5000余3389、PNG182/3000余2818、public68/300余232、internal30/500余470；offline分组34、Reaper2按原口径，PG容器/卷各1、preview同时最多1。

这些是工程冻结时的数值余额，不恢复已结束许可、已用根/PG次数或本审计业务权限。

C07 首两只读工具未采钟，首采样 UTC2026-10-11T17:44:05.806977Z / mono1012109906000000，accepted_ns另扣300秒，保守收紧14400秒综合窗和600秒清场预留；accepted_utc仍标首采样，不能冒作与 accepted_ns 同一次精确首读。实采后 phase 共1828.453秒，保守窗消耗2128.453，未到业务截止。metadata562.500含工程实现混分，implementation/offline965.562、real phase168.891、cleanup131.500；real phase较资源根多0.234秒属阶段外围。分类误差保留，权限本来覆盖三修复及定向原件，未因此扩授权或新增产品硬门。

finalize 首次重算漏加历史三笔输入；原失败保留，后续仅补统计和 source/index，finish_only 分支不重新调用 PG/物理查询、产品或资源根，不改历史 ledger。旧失败、历史超限、采样/pre 缺口、offline27缺终点、13元等首轮限制仍保留。详见 [独立预算核对](/D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/review-01-20261012/execution-budget-independent.json)、[阶段与离线核对](/D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/review-01-20261012/phase-and-offline-independent.json) 和 operation-notes.md。

## 交付、投入与最少下一步

首个实际接收工具 UTC2026-10-12T00:48:53.3841165Z，QPC10375971557863、频率10000000，换算同基准 mono1037597155786300。原已观测3347.3488145秒及首采样前准备unknown继承，未清零；本轮窗口7200秒、累计观测上限10800秒。报告保存前采样为 {{SAVE_UTC}} / mono{{SAVE_MONO}}，本轮已观测{{REVIEW_SECONDS}}秒，累计{{CUMULATIVE_SECONDS}}秒；本轮余额{{REVIEW_REMAINING}}秒、累计余额{{CUMULATIVE_REMAINING}}秒。最终完整复读投入及对象 hash 见 [交付收据](/D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/review-01-20261012/delivery-receipt.json)，首采样前 unknown 不填0。

本轮实际读入的路径、bytes、SHA256、UTC/mono 见 reads.jsonl；元数据命令参数及调用时刻见 commands.jsonl，独立工具为 review_metadata.py / review_checks.py。解析器假设纠正及 CRLF 差异详见 operation-notes.md；未发生业务运行、补跑或产品修复。新写入仅本 TASK112 结果与本 review-01 证据目录。

原结果36048字节，SHA ea51e0f49f556fd6f07aea11741d26099a534550850c0c68dfa49a9ab4c3b522，交付时按完整原字节后缀拼接并复读校验；原副本另存本轮证据。以下原报告的旧版签字与未闭条目保留其历史性质。

建议编排维护者在唯一执行动态账记录 review-01 的四项关闭、采用新 image/load 身份及原限域证据、保留旧 UNKNOWN 和626.566秒历史偏差，再作 G11 已采用有限切片的关闭裁定；必要文档变更记录只登记这次差异。没有新要求补跑，正式文档和最终验收未由本审计代改。

---

以下为首轮 TASK-112 / R-106 原36048字节全文，原字节保留。
