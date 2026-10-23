# TASK-123 / R-117 修正轮01 继续理由错误映射收口

## 完整成果与接收安排

你是本卡执行者，沿原TASK123窗口，一次撤销F124-01错误操作映射，保存两份更正文档及原有progress理由持久化的准确核对合同，统一结果置顶回传。任务号仍TASK123/R117，不新开产品工程线，不要求中间逐项确认。

本轮是低影响交付文档修正，常规档A−足够；原窗口若固定使用A+可直接延续，不为档位另开会话。真实客户端/模型如实记，不占TASK124独审窗，不委派。

根D:/shspic/project_NO3_RetroLume-agent，入口同根AGENTS.md。task_model、V4.0/公共AGENTS CHG-0003、阶段07；需求v1.4、架构v1.63、执行动态v2.91。公共只读根D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4；七锁定指纹在DocuN/evidence/v4-migration-20260930/rules-snapshot.json。同窗未变规则复用，只补变更，不自动采用新版。

关联TASK124/R118的F124-01、FR010/DR002、STEP018及原116 L01/L05/L10。授权为原项目开发与TASK123未验收交付范围内的准确文档修正。没有新接口、schema、费用或权限决定，不需要用户再次批准原100/25、候选或本次文字修正。

## 已核清的原因与本次唯一修正路线

独审确认新的readiness产品代码、最终13方法原始证据及本轮控制在各自限定范围通过；P1来自finite-inputs和deployment-handoff把中性理由交给correct。correct不是注释保存：它产生correction，重建进度时相关反馈被视为有争议，空disputed_dimensions也不能避免。这会损失独立作答依据。主控此前复核合同沿用该映射的假设有误，本轮撤销；不修改真实correct的争议保护。

主控实读原需求与116合同后，明确FR010原本要求依据复测保存可观察的继续/保留/调整理由及进度，不要求另设一个任意用户手写中性备注接口。116 integration-contract的M06和学习主链已经约定evaluate同事务保存progress及理由。

当前已有真实承载为activities/teaching_repository.py中的evaluate正常当前结果分支：构造progress_body，含feedback_record_id、answer_record_id、reason、advance、node_before/node_after、observations/support_checks，经_teaching_insert_record保存kind=progress和body_sha256，更新head.reason_record_id及state_after。read_teaching_workspace/read_teaching_record可读该事实，页面“更新或保留理由”显示body.reason。此为B级当前源码事实，不是本轮真实PG或真实Q的验证结论。

因此本轮路线固定为撤掉correct/手写备注的执行映射，将“保存理由”准确落到既有evaluate COMMIT的progress.reason和原读取/展示/恢复核对。不能把错误改成select_node、answer、goal或其它有副作用动作，不能新增reason action/字段/表、改进度算法、削弱纠错、清账或修改Must。参考理由的159字节原文可以作为被撤销的非执行说明保留，但不得再声称该精确文字已经或将由现有中性备注接口持久化。

## 最小输入

先读本卡、同目录permit.json和input-manifest.json，再读DocuN/results/TASK-124-result.md中F124-01与A—F已通过范围、主控TASK124-work-decision及TASK123-work-decision的本轮段。原独审已完成，本轮是获准工程交付修正，可读报告，不冒充独审。

原错误输入只作pre与历史：DocuN/evidence/TASK-123/execution/finite-inputs.json、deployment-handoff.md；原13方法/batch3、post快照及其他48产物全部冻结复用。

只读DocuS/最终需求文档.MD的FR010/DR002，DocuN/evidence/TASK-116/design/acceptance-contract.md的L01/L05/L10和integration-contract.md的M06/主链；必要源码为backend/app/activities/teaching_repository.py的_progress_reason、evaluate进度写入、correct、read_teaching_workspace/read_teaching_record，backend/app/learning/teaching_progress.py，以及frontend/src/activities/TeachingWorkspace.tsx“更新或保留理由”的现有投影。主控已存函数级定位与hash到本轮root-cause-and-scope.md，不通读全仓或重新研究供应商。

若发现原批准需求有明确“另存用户任意手写继续理由”的条文而非本轮错误自评，列出准确文件/原句并暂停相应解释；不得凭已废弃映射反推新需求。没有该真实反证就按上面已裁定路线完成，不分散设计新承载。

## 允许产物与历史保留

仅新写D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/correction-01/，并在DocuN/results/TASK-123-result.md置顶本轮完整结果，旧报告原字节作为后缀保留。原execution下全部48证据、错误两文档、manifest/失败日志不改，不伪造旧结论已经正确。

在correction-01保存以下实际更正，构成一个完整成果。

1. finite-inputs.json。以旧文件为pre保留完整新版本。HTML focus的原文、405字节hash、父顺序和未运行状态不变。撤销allowed_local_projection及一切“correct不影响进度”的指引。理由参考文本如保留，明确非执行/未持久化/不加入模型上下文，使用withdrawn_reference等可辨状态；删除它的现有写入接口承诺。
2. 在新finite-inputs中明确progress_reason_readback_contract，指向真正已存在的evaluate提交与kind=progress.body.reason。真实record/feedback/answer/原business_key/body hash、scope/goal/revision及DataContext仍null，等未来获准真实链发生后填证；不得填假UUID或把参考159字节当实际reason。
3. deployment-handoff.md。保留其余正确关闭状态说明，替换错误继续理由段，链接本轮新finite-inputs。说明先从原evaluate命令/对应progress核COMMIT及理由，取得原record后只读核对；活动下一明确动作必须按真实阶段进行，不能为保存理由额外POST纠错/选节点。新一轮动作可能改变head指针时，先保存这次实际progress的ID/hash，之后读历史准确记录，不拿新head替代旧理由。
4. original-to-corrected.json及有限diff，列旧两文件与新两文件hash、HTML未变、错误映射已撤销、旧事实未改及当前有效文档路径。主控后续按此新版本裁定，不让未来执行者误用历史目录中旧映射。
5. 一次document-consistency.json，包含当前六产品/测试/README/deploy hash未变、旧48产物/原两文档未变、原报告后缀保留、JSON关闭、引用/长度/hash/字段/意图一致、上述实际函数级关系。仅文件/JSON/文档核对，不运行或导入产品。

新读回合同须保留以下验收含义。

- progress必须与该次真实evaluate的feedback/answer、业务键、来源/版本和当前绑定对应，kind/body/hash/事务提交可核；不能只截一张理由页面就当持久化成立。
- 记录reason、observations中的独立/辅助/争议依据、advance和node_before/after。单次复测可保留节点，两份合格独立实例及前置都满足才按原规则处理。没有满足前置的可推进节点时原理由应如实解释，不能伪造推进。
- 下一动作前GET准确workspace/record并读取页面已有理由；未来实际重开仍需读取同记录/进度。这里只写未来核对合同，不执行PG/HTTP/browser，也不称已补真实语义证据。
- 不新增correction，不把任何作答从依据集合剔除，不用额外模型/query占89矩阵或已批准分额。L01/L05真实语义、恢复及Q等未跑门继续原样，不能因更正文档就签通过。

## 冻结与运行边界

六个原产品/测试/说明全部保持原post hash；teaching仓储/契约/进度/前端及全部其他产品同样只读。不改README、deploy/q-approval.md、原有限矩阵、固定样本、配置、DDL、Grant/费用、原始/正式DocuS、公共库和主控orchestration。审计OBS124-01保持非阻塞配置风险，只在新交接明确身份栏只填可公开模型别名，不扩写产品修补任务。

产品导入/compile/unittest/TestClient/build/PG/SQL/Docker/API/browser/Job/联网/下载/安装/模型/Embedding/计量接口/费用/Git/委派全0。原13方法和已有独审直接继承，不复现correct破坏场景，不跑原失败，不重查tokenizer/模板/账号，不启动或探测旧资源。

本轮只使用原TASK123剩余工具许可。保守已用3554.557411/7200、剩余3645.442589秒；原三测试批3/3封存。原日历截止2026-10-23T00:19:11.451055+08:00不延长。本轮新增工具至多600秒，含120秒保存，单命令通常60秒；实际起点、命令wall与未测项如实登记。等待主控/用户/独审的静默日历不会变成工具wall，不再把从原签发到本轮结束的整段等待一股脑扣工具额度；原已封存保守账和预留不退款、不伪称精确实测。

## 交回与本轮终点

只要两文档执行含义更正、原源码/证据保持、一次文档一致性通过，就保存结果交回，不扩大范围。遇确切合同反证、冻结漂移、必须改产品或到原门，就停止依赖部分并列准确差异；不得自行扩权或机械重试。

统一结果置顶“修正轮01”，先说明撤错映射、FR010实际理由承载及未运行范围，再列新有效文件/原字节保护/差异/hash/检查命令/退出与累计剩余账。不要把原159字节参考文案说成已被产品保存，不能虚构中性备注能力。原报告和审计不通过原文保留。

本轮没有新增高风险代码，完成后由主控对照已有独立代码结论、F124-01原证据和准确需求作限定文档复核并裁定，不预设再派完整独审或重跑13方法。独立结论仍据原TASK124，不冒称主控复核为新独审。若越出此文档范围则相关放行暂停，新的真实影响另行裁定。

Q和真实normal/首次T0仍冻结，外部计量/账号材料缺口不会因本修正自动关闭；不签STEP018/019/020、M1、项目或发布通过。保存并复读后仅回复一句话结论和D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-123-result.md的可点击绝对路径，供用户带回。
