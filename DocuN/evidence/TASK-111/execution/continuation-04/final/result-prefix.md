# TASK-111 / R-105 续作04 — 资格与启动根因已补证，正常业务已完成，完整剩余矩阵未闭合

## 本轮结论与三轴

本轮继续 TASK-111-G11-C04-20261011，沿原续作03唯一工程窗口，无子 Agent。六列资格权限和启动前关键登记失败窗口已修并取得实际生产路径证据。最终生产 v2-07 下两个新 Native 成果与正常 UI 链均完成；记忆与 cancel 的精确缓存竞态均通过。Node 忙死、Reaper 死亡及其假 console/postMessage 入口有新的真实证据。

完整任务仍为部分完成。客户端迟到组合在 stop 路由已被处理时抛错，旧已解码 bitmap 的释放及最终不复活断言、实际隐藏与卸载、活跃刷新均未完整验证。owner_control_lost 实际已完整停止，但停止原因被后来的 user 覆盖，断言失败；修复后仅取得实际生产解码器的定向协议回归。pipe_corrupt、SUP 死亡、双监督死亡、控制路径失联和硬 D 五个场景未跑。本轮没有稳定完整候选，完整验收、集中隔离终审与放行仍待这些缺口收口，生产 HTML 默认关闭。

实现轴 PARTIAL_WITH_TARGETED_REAL_PROOFS；证据轴 PARTIAL；执行控制轴 FAIL_RECORDED。角色权限、启动、两正常链及四类资格屏障的限定通过均可复用，整张 M01—M12 不通过。未把改后的最终文件 hash 反推所有早先进程使用过，也未把协议回归当成最终新生命周期通过。

机器分界在 [delivery-boundaries.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/execution/continuation-04/final/delivery-boundaries.json)；逐项方法在 [matrix-actual.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/execution/continuation-04/final/matrix-actual.json)。全部本轮原件在 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/execution/continuation-04/。

## 接收与历史

本窗口为 Codex desktop / GPT-6 系列，精确服务变体与推理档不可读取，A+ 为工程安排标签。沿 TASK-111/R-105、task_model、V4.0/公共 AGENTS CHG-0003，需求 v1.2、架构 v1.16、执行动态 v2.38/07。原同窗规则正文复用，七指纹重新核相等；78 项回收源和报告开工时相等，记录 [entry-identity.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/execution/continuation-04/entry-identity.json)。未写公共库、DocuS、原始需求、001—011、依赖锁，未重跑旧109或充分未变的 G3—G10。

本报告以下完整保留原97401字节，SHA256 6cf13c149027f0af9ab0c0529d924a6d27d1aa88d7097cd37b23439d0de39091。C03及更早失败、旧13元、UNKNOWN、时钟/超时/迟记与投入保留。没有为换窗、续作或隔离清账。

## 六列权限与资格闭包

仅在012安装声明及本合成main库增加 html_owner 的三表六列 SELECT：pdf_review_candidates 的 id/version_id/status/page_count，pdf_review_pages 的 candidate_id，pdf_extracted_pages 的 version_id。没有表级SELECT、GRANT OPTION、正文 extracted_text/warnings、DML、LOGIN或角色成员变动；010/011函数 owner、SECURITY INVOKER、search_path和ACL未改。已应用012未整份重跑。

实际检索六个资格/摘要函数，并额外列出 dependency_line 与 html_parent_eligible 两个入口/辅助，完整追至三个PDF COUNT/确认状态依赖。补丁前后所有表 relacl、旧角色、成员关系与函数定义/owner/ACL相等，只有指定六项 attacl 改变。HTML schema指纹加入这三表的列ACL与表ACL，后续差异继续失败关闭。证据 [qualification-patch.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/execution/continuation-04/root-14/step-01-qualify/qualification-patch.json)、column-role-rejections.json、schema-shape.json。

真实 SET ROLE retrolume_html_owner 的完整 memory_revision_readable/eligible 取得 confirmed完整2页正例、未确认反例、已抽取3页但只核对2页反例，以及声明3页而抽取/核对各2页反例。review到extracted的FK禁止伪造“核对3页/抽取2页”，实际23503原件保留；缺抽取页反例使用该真实模式允许的同时缺核对页状态。所有记忆试验行及候选临时状态用事务ROLLBACK保原件，没有删除旧行；新合成PDF候选保留，属于资格数据夹具，未冒PDF解析验证。

owner与html_app读取正文/警告及三个表 INSERT/UPDATE/DELETE均42501；六列逐项核 owner可读、html_app没有新直接读权。表级旧主体原合法权没有撤销。PDF证据分别在 step-02-pdf_verify/pdf-observed-progress.json 和 [PDF缺页核证](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/execution/continuation-04/root-14/step-03-pdf_missing/pdf-complete-qualification-cases.json)。初次pending夹具未清 decided_at 触发CHECK，随后不可能的缺抽取孤页触发FK，两次失败均保留。

实际完整HTML资格正例及记忆失效反例还由 step-09-races 的真实 teaching.v2/选用记忆产物和预览补证，不以单 selection=false 代替公开资格。

## 启动登记、管道与停止

JobChild支持受控挂起创建：先准确出生、归属HostJob和三个匿名管道，读线程准备与关键 registry 发布后才一次Resume。DB start_requested转移放在关键登记成功后，保留原 t0/ready8、reserve30—60、3次/180、D-10、soft-stop2和外部kill限制。注册中的 attach_suspended 表示恢复前准备事实；是否真实启动仍核Created/StartedAt及完整停止收据。

真实Windows自有读句柄阻止实际 registry.json 替换，得到 PermissionError/errno13/WinError5/stage suspended_attach_registry。两个读者当时已建立、CLI仍挂起归Job；Docker为Created/StartedAt0001/Pid0，没有真实start。挂起CLI终止、Job零任务与never_started均有实际证据。首次此场景还揭示旧SQL不允许start_requested直接转failed_unstarted，形成一次新cleanup_unconfirmed。按该对象已取得的完整未启动证明在同一C04根真实恢复，结算满60秒、一次使用不退，没有换目录解封；原failure/supervisor-result不覆盖。

有据修正后的新锁场景正确 failed_unstarted，elapsed3/starts_used1/reserved0。释放后同一路径真正ready，随后对实际 engine-observation-1.json 再持读句柄，观察发布失败触发停止；reader继续排空到真实EOF，精确kill/wait/die/private PID/init与两个Job零任务完整，elapsed9。分别见 [实际挂起启动拒绝](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/execution/continuation-04/root-14/step-05-startup/real-suspended-start-rejection.json) 和 [ready后日志拒绝与完整停止](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/execution/continuation-04/root-14/step-05-startup/real-postready-log-rejection.json)。

错误诊断仅固定阶段、类型、errno/winerror和路径别名。观察写或事件写失败不阻物理清场，异常协议之后也继续读取到真实EOF；无kernel/EOF仍不能签完整树空。已确认未启动的同根重启可复用严格CID/image/nonce/Created/已结束出生与Job证明；一般死亡恢复新增实际Job结束要求，但双死亡/控制失联完整动态仍未验证。

owner_control_lost的实际最终原因被status:user覆盖，是另外发现的元数据缺陷。最后修成保留已存在的首个原因，control_lost/reaper_lost/source_invalid及无既有原因四个实际生产解码器封包回归通过。[primary-cause-protocol-regression.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/execution/continuation-04/final/primary-cause-protocol-regression.json)明确是内存管道协议范围，修后真实owner生命周期未跑。最终源码与先前实际生命周期分开。

## 最终部署与两正常业务

生产始终使用固定v2-07 image sha256:c23c7489d56fa2cc955dc15e86e0b710b476589997d57ee33c9eb9f3949e826f，load bea3f1ebc033635fdac71e1134ed66632947d994b701c9a7b76d942ff036ad00，四runtime renderer SHA 6cc300164a6cb364d9bd0bae4897f06d3f6a65cf5d4272477d2bccde67312597。故障仅冻结v2-06 image 8d3811cdf4b9d6edd00a5dd438e382d1700335fb0109084a59e69813fbc97016；它不替签v2-07正常安全或帧率。没有新image、依赖或frontend产品源改动；实际加载的C03最终frontend bundle逐字节核相等。

C03 N1的包 verify_package真实通过、budget行0，生成时v2-05与当前v2-07分别记录；实际活动截止2026-10-11T00:45:11.079741Z已过，资格为false，因此新建真实合成活动及父，没有因镜像变化宣布包失效，也没有重写旧deadline或预算。结果 prior-Native-reuse-check.json。

新N1 activity a3367315-4492-4eee-9fec-ca3008628624，artifact 20e41d2b-d093-4858-a948-68b9d95f73da，真实Windows OneCall/worker/Job/PG结果terminal succeeded，native结束ActiveProcesses0。新N2 activity 68afa820-66f1-4dcb-88b4-eba032ae9d9b，artifact c974afd5-c4fa-40a8-bd30-49f292d8b268，同样一次真正Native。仅两次受控合成transport，不是付费provider或真实模型质量结论。

N1真实number/range/reset给58.800000000000004，按合同误差1e-9核为58.8；h=0、m=0均0，负h返回422并保完整PNG与上次参数。N2实际.375、四柱 .125/.375/.375/.125；p0/p1、n0/n1/n20和21柱按独立oracle核，k>n、非整数、p>1均422。两类XSS/闭合script字符串原样文字，panel没有script/img/svg/iframe节点。真实参考展示后来源回查成功，两项UI停止和回父均完成；正常停止后刷新只有GET，无自动新生成/预览。

N1同键并发只一次synthetic发送；不同focus同键409。N2实际POST成功回包被route丢弃后，UI只读GET原business_key核回同一artifact，未重新发送。实际artifact资格读与每次start用既有commands/artifact/op/result资格JOIN成功；本轮未另保存四表原始JOIN行，不补造原始SQL证据。汇总 [Native-and-normal-UI.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/execution/continuation-04/final/Native-and-normal-UI.json) 和 step-08-ui/ui-attempt-01/ui-effects.json：21个真实公开ACK记录、43份PNG及两normal_complete。

UI夹具保留所有失败：首个reset误用浮点严格相等；引用等待早于当前工作区加载导致未展示参考；跨attempt恢复覆盖preview字段致数值片段继承未触发，N1累计真实3次没有重置；一次在已用3次活动上尝试打开被产品预算拒绝。原键、产物、窗口和失败原件均保留。

## 资格竞态与停止场景

新增记忆/cancel均准确暂停在生产frame已有candidate、_owner_row资格查询未开始的屏障；实际选用记忆revision改变或cancel COMMIT后释放，frame/body/input拒绝并取得完整停止。C03 source/parent屏障直接继承。新证据 [race-results.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/execution/continuation-04/root-14/step-09-races/race-results.json)及两个 exact-barrier-result.json/stop-and-budget.json。

Node忙死先真正READY并保存kernel/nonce/CID/pid/birth/Job/真实管道，固定v2-06 Node beforeInput忙循环触发ACK不确认，最终完整停止。Reaper死亡场景先实际fake console/postMessage与真正ACK，原D不变，然后终止精确Reaper，存活SUP完成完整停止。独立取证者在触发前复制实际匿名管道并预持同一Job句柄，actor结束后实读EOF、Job查询零任务；这个取证者会改变“最后句柄关闭”的时点，已注明，不能冒双监督自主停止。[fault-results.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/execution/continuation-04/root-14/step-10-faults/fault-results.json)只有这两个PASS。

owner_control_lost确实READY、停止owner heartbeat、只有ownerless读，原D没有延期，最终stopped/elapsed9和完整kernel/EOF/wait/die/Job证明。它的原因断言却见user，所以场景FAIL_REASON_ASSERT，最终代码原因修复只离线回归。其后五故障NOT_RUN。不能用Node/Reaper/正常stop替签这些不同事件。

客户端迟到使用N2的第二/三生命周期，经真实activity/父视图切换再换owner/generation。旧PNG和引用route.fulfill已返回，stop路由报already handled提前关闭context；旧已解码bitmap未resolve，最终不复活、隐藏、卸载等后置断言未执行。此是测试未闭合，不把已捕获图像或成功新ACK冒完整guard通过；当前pending事实保存在 step-08-ui/ui-attempt-02及browser-paused.json。

## M01—M12实际范围

M01 PASS_NORMAL_UI_SCOPED：上述真实N1全部正常操作/来源/停止回父，并复用已核DEF-027核心。

M02 PASS_NORMAL_UI_SCOPED：上述真实N2数值/21柱/输入拒绝/文字XSS及来源/停止回父；不推一般数学或全部安全承诺。

M03 INHERITED：32类两端拒绝、非法/unknown原生与生产纯protocol既有充分未变部分不重跑。

M04 INHERITED_CORE_PLUS_NEW_LIMITED：冻结v2-07完整frame/document/target与新正常输入观测可复用，未作任意脚本导航前保证。

M05 INHERITED_PLUS_NATIVE_XSS_SCOPED：固定textContent/Canvas/CSP/能力拒绝复用，加上述真实N2文字展示与禁节点断言；不签总安全。

M06 INHERITED_PLUS_PASS_INPUTS：C03定义域/50000步/拒绝整帧证据复用，加实际正常控件格点/整数/p与k>n拒绝。

M07 PARTIAL：owner/hash/序列/duplicate-init/PNG codec与纯protocol继承，fake console/postMessage新证据；实际pipe_corrupt仍未跑。

M08 INHERITED_PLUS_HTTP_KEYS_SCOPED：原同COMMIT rollback/权限/UNKNOWN充分部分复用；新同键竞争、不同输入409、丢HTTP回包GET恢复与两Native资格JOIN补证，原始四表JOIN行未另采。

M09 PARTIAL：source/parent继承、memory/cancel两个准确屏障新通过。客户端整组迟到stop/已解码bitmap/隐藏/卸载未完整闭合。

M10 PARTIAL：C03三次/180、并发same-start-key/create丢回包/min30/四账不变复用；新同根never_started保满R60恢复与真实停止后刷新GET已证。活跃刷新与双死亡/控制失联UNKNOWN持久救援缺。

M11 PARTIAL：核心及renderer_busy/browser_busy按未变镜像/物理路径限定继承，Node/Reaper两个新PASS。owner真实树已停但原因断言FAIL，修后真实未跑；其余五项NOT_RUN。

M12 PARTIAL：六列ACL与旧主体/函数不变、启动前后异常、实际Native/教学参考读等受影响部分已补；531材料、限定upgrade和充分G3—G10继承。最终原因修复缺动态、fingerprint原字节pre缺失、完整矩阵与终审仍欠。

## 执行控制、时间与余额

累计真实根14/14，旧global78加111十四根为92入口，非92PASS。本轮根13预检失败2.297秒，没有启动PG/preview；原已退出的两个Windows pid在单次OpenProcess返回5，独立CIM与Toolhelp枚举缺席并匹配原同出生已退出证据后核正，没有把5直接当退出。根14实际1656.703秒；根结束到精确PG停机核证的整个1.000秒区间再保守计入real，根14覆盖1657.703秒，累计real12382.158、新增1660.000秒，均未超真实时间门，固定deadline未延。

执行控制错误明确保留：在races/faults/final_data尚未结果时提前排了stop命令；faults遇owner原因断言失败，未先有据修正续跑便自动关闭组合。之后原根固定deadline已过，不能重开根14、复活旧C03或自行出根15。API8/8、主browser7/7已达上限。尚有五个新名字40—44及model/Windows各一次、PG一次等额度，也不能越根/时钟/监听门单独消费。不是新增许可不足代替本轮夹具和调度错误。

当前preview create29/34、start27/32，本轮各14，名字26—39各一次。两个悬停拒绝也占原使用/工程start尝试，不退款。PG start10/11，仍同一个CID1791a2d…和同卷；API8/8、browser7/7，model9/10、Windows9/10，frontend3/5、image7/7没有新增。HTTP882/5000、公开inputs57/300、内部inputs26/500、PNG149/3000。offline批24为记录项。完整实际账见 [execution-receipt.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/execution/continuation-04/final/execution-receipt.json)。

首次读C04没有同步精确时钟采样，未追认为精确首读；用04:26:35.535170Z实测前300秒的保守下界固定截止2026-10-11T08:21:35.535170Z，业务早600秒。这次缺口保留，未用后续读卡后移截止。C03旧超1800原件实际为root10的1800.047秒；卡写root09时仍以原事件/报告保事实。其余旧缺口/迟记/unknown/13元不改。

原78源未包含 schema-fingerprint.json，本轮应用列补丁前未另存该文件原字节pre。旧C03函数补丁收据可作值参考，不能伪造为本次pre。缺口见 final/pre-gap.json。其它改变有开工pre或修正前逐次复制、diff/post/as-run；新增文件明确为本次新建。最后停止原因变动仅协议回归，早先真实生命周期绑定各自as-run SHA。

## 清场与旧未知

新场景始终同一 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/execution/continuation-04/synthetic/control/。它是本卡明确的开发隔离，启用前十二旧对象停止、登记Windows结束及实际Global排他已核，旧C03根没有写入或解封。旧preview25/CID742543c2…依旧cleanup_unconfirmed/R60，一次使用和缺kernel/EOF不变；新node_busy通过不替换它。没有把Stopped/Pid0补为旧完整树空。

本轮14行全部terminal：两failed_unstarted（一次保满60恢复、一次elapsed3），十二stopped，已保存confirmation_receipt原件。新合成未留下当前UNKNOWN；原旧25仍保留。[session-proof-index.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/execution/continuation-04/final/session-proof-index.json)列每个CID、image、kernel hash/EOF/Job及费用秒数。

PG精确stop，两个API、两个主browser及登记Windows实例均结束；十二旧对象加十四新对象共26个精确容器Running=false/Pid0/restart0，18111/55451无监听，Global owner可独占。[exact-resource-final.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/execution/continuation-04/final/exact-resource-final.json)、ports-final.json。核对只覆盖登记对象，不停daemon、不清用户进程，不删除库/卷/image/资料/行/证据，没有Git写或发布。对旧25仍只保物理metadata证据，不宣cgroup目录或全部内存释放。

## 剩余具体方法与复用入口

后续仍同TASK111/R105与同C04控制根，不能在本已到期许可直接重启runner。原Normal两Native、六列权限、启动锁与后ready日志锁、四准确屏障、核心/数值/权限/rollback充分部分直接复用。迟到夹具先区分已取消route与实际回包释放，保存跨attempt preview/数值证据且不再重复消费旧活动3次预算；完成实际bitmap release、stop、hidden/unload和活跃刷新。

停止侧先核最后一行owner原因的最终代码，再按已准备方法补pipe_corrupt、SUP死亡、双死亡、控制失联、硬D。死亡触发前的实际kernel、管道/Job持有和同根持久救援方法已准备但未全部执行；新UNKNOWN仍须本对象完整证明与持久恢复，不能再换根。故障runner应在有完整物理证明的独立诊断失败时先留原件并精确清场，再决定修正与后续，而不是未读结果就排终止命令。

正式执行动态、DEF-029/030最终裁定及新增许可由主控串行维护。本工程窗口只回真实部分与剩余范围，完整稳定后仍需一次新隔离增强终审。

## 以下原字节保留续作03及此前报告

