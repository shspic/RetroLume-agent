# 下一实施合同完整草案（未编号、未派发、未生效）

这是TASK116/R110的设计附件，不能凭路径执行。主控采用AP1后填写唯一新TASK/R/permit、实际接收者/日历首点/独审窗口再人工转卡。用户既有自有应用开发授权覆盖常规实现；AP1主要模型/接口/权限和AP2实际付费/外发需要其对应明确采用。本草案不自动继承TASK114/115/111或早期runner许可。

## 成果目标与前置

一个稳定完整STEP018工程成果：资料导入/全部PDF核对与范围→必要澄清/目标→路径→练习/作答→有据反馈/固定交互解释→复测→保存理由更新/保留路径；资料/目标→文字面试问题→回答→必要追问→有据反馈。hybrid检索、可选低信任记忆、持久预算/引用/取消未知、同normal库重开明确继续贯穿。包括014与R02增量、R01旧包兼容、本机启动/文档、有限验证与范围内普通修复，完成后交适用独立审计，不签项目/发布。

根`D:/shspic/project_NO3_RetroLume-agent`，入口AGENTS.md；公共只读根V4，task_model/V4.0 CHG0003/阶段07；七锁定指纹在rules-snapshot.json；需求v1.2、架构v1.32、执行动态v2.56为本设计基线，派发时主控只补实际已生效增量，不追认未读规则。接收原A+工程窗口优先，不派子Agent/并行改产品。实际后端型号如实记录，A+仅资源标签。

最小输入：[TASK116结果](D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-116-result.md)、同design/integration-contract.md、acceptance-contract.md、sample-inputs.json、adoption-package.md、source-identities.json、git-baseline.json、consistency.json；TASK116 input-manifest及原115终审/114稳定原件、111/112 G11有限已关闭原件。源关键身份来自设计实际读范围，不重拷243件，不凭历史表未开始推翻当前裁定。上述设计冻结后原产品变化需针对相关文件核冲突；冻结审计时另登记最终候选实际hash。

AP1未采用时不发包含014/profile/新接口运行权的卡；可自主常规接线不能冒混合已采用。AP2未核/未授权时真实网络/provider/fee均0，但同卡合成实现/验证连续完成。不要再拆“准备、跑一条、修夹具、再试”或前置全仓验证卡。

## 精确允许产品写入（派发采用AP1后）

只允许下列现有文件及明确新增文件。需更改未列新高风险主体先给准确影响交主控；普通漏列同功能适配由主控更新卡面，不能自行广泛重构。

- backend现有：`app/main.py`；`app/service_config.py`；`app/capabilities/contracts.py,gateway.py,transport.py`；`app/worker/one_call.py,worker_main.py,launcher.py,session.py`；`app/activities/api.py,service.py,repository.py,teaching_repository.py,interview_repository.py`；`app/learning/contracts.py,service.py,evidence.py,adapter.py,prompt.py,teaching_contracts.py,teaching_service.py,teaching_evidence.py,teaching_adapter.py,teaching_prompt.py,teaching_views.py`；`app/interview/contracts.py,service.py,evidence.py,prompt.py,policy.py,views.py`；`app/memory/context.py,repository.py`；`app/data_exit/contracts.py,schema.py,schema_checks.py,codec.py,packages.py,snapshot.py,readability.py,restore.py,reference.py,deletions.py,repository.py,control.py,config.py`。只改本合同函数/profile适配，runtime Selector机制无须变化。
- backend新增：`app/capabilities/embedding.py`；`app/retrieval/contracts.py,repository.py,service.py,api.py`；`app/data_exit/schema_profiles.py`；`migrations/014_step018_retrieval.sql`。retrieval现有`evidence.py`仅为封闭排序/目录共用接线允许最小改，原片段identity不变。
- frontend现有：`src/main.tsx`；`src/activities/ActivityWorkspace.tsx,TeachingWorkspace.tsx,InterviewWorkspace.tsx,MemoryWorkspace.tsx,LearningResult.tsx,TeachingExercise.tsx,TeachingFeedback.tsx,TeachingCitations.tsx,InterviewCitations.tsx,teachingApi.ts,interviewApi.ts,memoryApi.ts,pendingIntents.ts,teachingIntents.ts,teachingIntentMatch.ts,teachingDrafts.ts,interviewIntents.ts,interviewDrafts.ts,memoryIntents.ts,learningIntentMatch.ts`（仅为本合同profile/ref字段及C03保护）；`src/data/dataApi.ts,ReadonlyRecords.tsx`仅适配R02新表/元数据查看，`src/data/context.tsx`的canonical身份/晚到规则不削弱。新增`src/activities/RetrievalPanel.tsx`和`src/activities/retrieval-api.ts`。`src/style.css`及`src/activities/activity-workspace.css,interview-workspace.css,memory-workspace.css`仅新增步骤/就绪/反馈样式，不能全仓格式化。
- 部署/公开文档：`deploy/start_local.py`、`deploy/start-backend.ps1`、`deploy/compose.local.yml`（PG参数/本机profile，不新增常驻renderer/Redis/API容器）、`README.md`、`deploy/preview/README.md`、`config/activity.example.json,preview.example.json,data-exit.example.json`；新增`config/integration.example.json`（正常部署/egress grant配置示例，不含secret）。配置字段/读取仍项目自包含。
- 前端`dist/**`只由本卡允许的正式build生成最终bundle，旧bundle hash保留用于对照，不手写补丁。依赖锁不改、不联网install。许可材料只引用原件；确实新依赖需另给采用影响，不能偷装。

测试只新增`backend/tests/test_step018_embedding_contracts.py,test_step018_retrieval_pg.py,test_step018_profiles_pg.py,test_step018_flows.py`、`backend/tests/fixtures/step018/**`和`frontend/tests/step018-flow.mjs`。可只读引用旧方法源码/冻结原件；不得运行旧已结束runner、改旧任务报告/计数/夹具以追认授权。本卡合成资源初始化/故障工具放新fixture，不成产品依赖。资源与证据归本卡实际TASK（派发后替换下述TASK-NEW），`DocuN/evidence/TASK-NEW/execution/**`、`DocuN/results/TASK-NEW-result.md`。

禁止：DocuS/AGENTS/公共库/用户需求/经验记忆、旧TASK/R/审计/证据/control/private、原001—013、固定四runtime及renderer ingress/SUP停止退款主体、整仓Git写/commit/push、删除/移卷/系统服务/网络端口调整、用户库/真实资料/旧frozen/failed/sealed对象、下载/pull/安装/新image build、自由模型HTMLJS/导航/新页面权限、跨恢复开写、新Agent/替补/新任务号。旧Git633行差异保护。

## 前向资源profile与实际归属

建议permit前缀`STEP018-INTEGRATION-SYN-v1`，绑定派发唯一TASK/receipt/hash，不沿用旧号。缓存PG17/pgvector image严格`sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f`，pull_policy=never；后续实核扩展版本才纳入R02。CPU1、memory512MiB、pids128、restart=no、127.0.0.1；每次创建先登记name/volume/port/image和许可，在途同名只能精确匹配CID/labels后继续，不重建清计数。

| 资源 | 固定新名字/卷/端口/用途 |
|---|---|
| source PG | `retrolume-step018-syn-source` / `retrolume-step018-syn-source-data` /15481 /DB `step018_syn`，新正常R02合成库，两链/重开/预算；不是原55461或旧本人库。 |
| compat PG | `retrolume-step018-syn-compat` /对应`-data` /15482 /DB `step018_compat`，001—013非空model/tool/域/unknown样本，先出R01包再014升级。 |
| readonly R01 target | `retrolume-step018-syn-r01` /对应`-data` /15483 /DB `step018_r01`；factory slot固定r01，仅可信1..13，核对后永久只读。 |
| readonly R02 target | `retrolume-step018-syn-r02` /对应`-data` /15484 /DB `step018_r02`；factory slot固定r02，可信1..14，核对后永久只读；反例失败对象仍保留。 |
| API | 127.0.0.1:18118，Windows hidden uvicorn/Selector loop，≤1同在，PID+birth+launch handle/receipt登记。使用正式dist同源，Vite服务上限0。 |
| preview | 仅已核v2-08 image `sha256:ec3c70c7a8a8894c647a69b08b0c296727bb052f639e487567e9cd4624766789`与load `8a047050ffe584dffa6e85222c16c8f400c0ab4db82f72a32812c2befd082b3f`，新registry/本活动动态对象，每CID精确登记；不得启动111旧对象/借未完unknown资格。当前global owner/SUP有冲突则关能力并留证。 |

新source/compat normal login为本fixture创建的非super runtime，仅取得当前data_app/领域app与新retrieval_app；迁移管理员仅该新cluster初始化短窗，业务/API不持管理角色；snapshot只read；恢复每target独立loader/readonly/snapshot，seal撤销写。秘密在本卡新合成private/control根正常安全生成，证据只存字段存在/角色/脱敏身份，禁止向对话/浏览器/log输出。数据root、backup、incoming、restore、preview registry均在新`DocuN/evidence/TASK-NEW/execution/synthetic/`子目录，物理独立、canonical+root_id核；**只作测试配置**。产品正常配置使用用户已批准正式data/backup/private位置，不能依赖DocuN。

同在PG≤2、preview≤1、API≤1、主browser≤1；禁止几批并行争budget或写源码。内存门≥2GiB按Docker已唤醒后的实时采，启动依赖前复核；无达标不创建/启动，仅做离线实现/证据，用户通知后继续原计数。所有15481—15484/18118端口按B6全状态核，冲突不换名/端口绕失败账。先登记创建尝试，再核实际CID；snapshot/恢复使用新source数据，不触碰旧对象。不能把同库重开偷换成重建volume/新DB，失败/unknown都留原对象。

## 足够且有限的工程预算（建议主控填卡采用，不是当前许可）

- 接收首工具UTC/mono同步，漏点保守扣减；活动时间≤28800s含准备/普通等待、编译/测试/PG持有及最后1800s保存清场；接收后72h日历。到25200s不扩大范围，到27000s只收尾。未登记时段UNKNOWN或保守计，不填0；所有项目旧投入保持。
- 运行根最多8个：按“完整目标批次”的实际首运行到所属自有资源精确停机计根，不把只读文件/hash命令当根，不把API/PG后台持有藏组外。建议根：协议/有限纯逻辑；真实检索/014非空；学习整链；面试整链；异常/权限传播；normal重开+R01/R02；获准真实语义；一次有据定向复检。源码实现不是运行根；每根必须写实际入口/开始结束/对象和失败。一根可连续普通修夹具和该批必要复测但不能归并无限运行，记录每次尝试。
- 新真实运行及背景持有累计≤14400s、离线产品测试/构建累计≤7200s（与活动总窗重叠分类不双加）；同一PG从start到精确stop（含根间等待）全记持有，超门立即收尾，不用活动秒数余量越runtime cap。
- PG成功对象≤4、创建尝试≤6（失败也占），volume≤4、PG start尝试≤16；API启动尝试≤8、主browser生命周期≤8；frontend正式build≤3、Windows Native/SUP窗口≤160（含失败）、dynamic preview create/start各≤12且每活动仍3次/180s；HTTP≤3000、原件/引用/PNG等响应记录保存必要有限内容。任何次数字段为上限而非要求跑满。
- fee/network默认0、install/pull/Git写/真实用户资料0。只有AP2明确成立才可对两固定官方候选发最多80单次HTTP/20元（包括上述160窗口内部分），无retry/其它外网；价目/条款核查由另有明确范围的主控处理，不让工程顺手上网探测。
- 最多28冻结场景，以样本JSON为准；旧未变充分方法引用不重跑。普通夹具修正和一次**有理由**增量复检在同卡预算内；每次失败/保存错误都留，不能为了PASS改正确预期。超cap/根因不稳/新主要模型/外部能力失配停止依赖部分，完成不受阻成果并回传精确余缺。

paid三个固定新活动UUID及额度：学习`01800000-0000-4000-8000-000000000001`40requests/10元；面试`01800000-0000-4000-8000-000000000002`24/6元；语义补证`01800000-0000-4000-8000-000000000003`16/4元。AP2 grant PG合计核80/20；每call reserve0.25元且当前最坏核价不得超，timeout10s/窗口90s/总管理120s，正文/输出/finite工具/preview上限见采用包。合成故障活动用同有限默认模板（40/24或边界特小值）及最低transport，收费0；这不复制真实许可。创建新活动不会使grant预算归零。

## 一卡内实施、验证、普通修复与保存

1. 接收并核卡面/关键实际span/本卡scope与Git保护，写receipt、预算、profile、phase；不要全仓hash。实现B3/B4前向代码/精确shape/旧profile兼容与配置门，先不启真实服务。
2. 只在已登记新合成资源完成protocol/finite逻辑、真实PG非空/检索原子与角色、新两链/异常/最终bundle及normal重开/R01/R02定向传播。技术故障用最小transport；真实Native/WINDOWS/SUP/公开API/bundle不能被纯mock代替。保存每个场景真实层和准确事实；已有成功方法输入/源码不变就续下个未完成处。
3. 按未变G11宿主签票启用新合成预览（票据正常部署，不伪签），补当前题/feedback的真实ACK/计算/引用。没有票只交缺口，不改宿主authorization绕门。全部新安全边界稳定后封候选交集中独审。
4. AP2只有在当前能力/条款/价额/账号许可及新边界审查就绪后激活grant；原工程窗口完成C的真实合成语义及必要范围内修复，保存cost与supplier/returned_model事实，不让审计自行承担付费实验。未获许可保Q未验证，合成成果照常交回。
5. 每次stop遵B6精确PID/birth/CID/nonce/EOF/Job及PG实际profile，收尾采端口/StopProof/预算/活动所有事实。没有证据标unknown保预留/阻断，不用Pid0或异步启动命令返回冒已停。保持卷/库/镜像/失败文件不删，不停Docker daemon/他人对象。最后真正保存UTF8结果并复读/hash，记录未改主体/所有失败/投入/旧账继承，给独审增量导航。

## 产物与完成标准

结果须能脱离聊天审阅：唯一结果文件、28场景case-index（状态/真实层/新证与继承/输入hash/失败与复检）、最终关键source-identity/change-index与dist/load/role/profile、实际phase/资源receipt/四账/费用/unknown、normal重开连续记录、R01/R02可读包及永久readonly核对/拒写、真实语义rubric、资源停止/保留索引、README与本机运行交接说明。操作计数/time允许缺口保守写，旧账与新grant分开导航不重写。

工程交付不是验收裁定：合成候选完整可评、实际运行收尾、Q许可不足如实列未验证；全部Must对应层通过才提交STEP018完整验收请求。新kind/R02/域权限集中独审及必要整体SEC/预算验收作为STEP019条件，既有充分组件不重复。STEP020本人自用运行交接仅在018/019通过、无阻断且真实数据/费用范围有效时编排；未纳入Should/Could/未来Linux公开发布不阻首版。新TASK/R/DEF/CHG/共享总账/正式裁定由主控串行维护，不在工程窗口自行分派依赖卡。
