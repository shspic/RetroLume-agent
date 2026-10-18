# TASK-084 / R-078 — review-06 09完整成果独立增量终审
接收原084独立增强审计窗口，未参与083代码/测试实施；沿原独立上下文，不接管实现。TASK084/R078，STEP008，父083、关联082/NFR002/003/SEC002/FLOW005/DATA007。根D:/shspic/project_NO3_RetroLume-agent；需求v1.1、架构v0.39、执行状态v1.56。Git基础45951501d2741630a229762d6b2d3f4b34d7f702及现存差异保护。实际身份如实登记；本卡属于尚未完成的进程停止/退款/恢复高风险裁定，必须具备增强审计能力，不按旧模型名称重审既有结果。

## 一次终审成果
对09新增真实固定launcher验证链及D3一列提案给出可供编排直接裁定的统一报告：各场景真正证明什么、最终代码是否新增确定缺陷、资源/证据偏差影响边界、D3能否提交用户批准及最小具体实施合同。不要再拆“读证据→补审→拟清单”多轮；能从现有证据回答的一次完成，只有决定性缺失才给最少补项。已验Job07/PG08/纯单元与review05静态结论按未变范围复用，不重审全仓不重跑。

## 独立输入及冻结
根D:/shspic/project_NO3_RetroLume-agent/AGENTS.md；公共D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD，已读未变复用。读TASK083现行09完整合同、082-work-decision与自己的review03/05相关边界。
先读新增原始源码backend/tests/fixtures/task083/launcher_control.py、launcher_scenario.py，必要生产launcher/supervisor_ipc/supervisor_main/session/windows_job直接依赖及09 manifest/实际runner，独立形成控制/注入/观察判断留证；再读Ndocu/evidence/task-083/launcher-complete-09/的results.json、batch-meta/stdout/stderr、两轮p-evidence/p-stderr、post-run-check和脱敏inspect。不要读取/打印凭据环境或DSN。最后读d3-sources-and-decision.md及083结果当前段作为待评提案/声明，披露接触顺序，不加载实现聊天。
当前新增文件hash：launcher_control.py=142a5699ec91017a2c6452fee6390b34670ebb140d80e703dd34b6a951a09af5；launcher_scenario.py=17f1bc8ade1c57eb8981a3c91df55b305bd7fc3374fb7a6cbde8325e2232cc8d。独立重算，原生产冻结沿Job07/PG08/09真实快照核适用性；未知漂移停对应结论。不得将本轮pre/post相等误当历史未改证明，不补造丢失首批汇总日志。

## 完整审查四块
1. 固定launcher真实覆盖：A真实run_supervised_window→SUP→idle worker→PG的调用/版本/venv/身份/计时/关闭/结算证据链是否成立；B注入是否真实进入claim后deadline分支，是否只是强迫wait返回值却绕过真实等待；C1/C2屏障精确位置、父/子身份/创建时间、进程树收尾与DB事实是否对应最终hash。把确定PASS、只能局部证明、缺证、确定缺陷分开。2秒负观察仅证明观测窗，不上升永久不会迟到；C2正常早退不能凭短运行自动证明到截止时一定终止。
2. 观察者效应及停止权限：逐个列测试控制者持有的Job/进程/映射句柄、取得/释放时点。B中SUP死而worker仍活是否因控制者保持最后Job句柄，不能据受测行为被改变的实验宣称生产KILL_ON_JOB_CLOSE失效或证明其有效。确切区分被测系统安全行为、外层控制者注入/接管/最终清理，A/B/C各自哪里有真实物理停止证明、哪里只保守账面。B结果None/cleanup_incomplete和无退款可独立成立则保留，不能因一项证据解释错把全批作废。若需要一个不保活Job的最小补证，给具体对象句柄、注入点、判定及必要性，不扩全套重跑。
3. 尝试与证据：09卡定1容器/真实≤3批12场景、每批10分钟、命令60秒、两轮针对性修正及累计限制；实际4容器/4runner尝试（其中2无场景）、2真实批8场景、TOTAL_WINDOW=660、首批汇总覆盖、复验重跑A/B/C1均须按真实命令/时间与剩余日志核对，不以最终exit0抹去偏差，不把配置660自动等同实际超时。最后全部停容器的正证据强弱逐项标明。已有成功证据可保留，无法恢复的日志明确缺失，禁止为补美观重跑。结论区分功能证据与执行合规，不凭模型标签作结论。
4. D3一列方案终审：独立核对“同numeric session id⇒可安全沿Local命名空间折叠”的充分性，特别同一会话、注销后ID复用、跨boot/快速启动/休眠、会话仍活或断开、同共享数据库跨主机/服务登录上下文、迟到创建与Local互斥的覆盖范围。若本项目实际限定单机，则写成明确可执行前提而不是隐含永真；同号只标命名空间编号，不先假定唯一化身，也不能反向无理由否定可通过旧进程必灭建立的证明。ERROR_FILE_NOT_FOUND与其他错误、无权限、碰撞、旧行NULL、新G写入/claim响应丢失、旧SUP晚到与G原CAS/租约必须逐路径说明；全额折叠不是部分退款，不能要求不必要的退款证明。
对提案官方S1—S5只核决定性原文：允许最多6个Microsoft官方页面只读取证（引用近原论据），不跑系统探针/实验。区分文档直接事实与推论；“没找到boot GUID”不能写成官方不存在；logoff文档是否足证全部session复用情形必须解释。输出一个推荐：充分则给最小字段/迁移/claim/recovery/旧行行为与部署前提供用户具体批准；不充分则给最窄修正/限制及代价，不泛泛再要研究，不默认加长期服务。不能自行批准或实施006。

## 权限与交付
只写Ndocu/evidence/task-084/review-06/有限hash/diff/官方来源摘录/初判与Ndocu/results/TASK-084-result.md置顶review-06保留历史。源码/测试/迁移/正式docu/公共库/Git/旧证据只读，不AST/import/compile/单元/Job/spawn/PG/Docker/安装/模型/私有配置，不运行实现者脚本；官方网页读取是唯一网络范围。实际运行额度0，源码冻结无并行写入。
完成后给统一结论：D1各场景有效范围、确定缺陷/最少补项及其完整修正验证边界；D3可批准的具体提案或唯一关键缺口；旧证据复用；四容器/日志覆盖等偏差与验收影响；下一步必要用户决定。无需重述全部历史。若需要修复，给一张完整成果可用的最小合同，避免单点发卡循环；无必要补项则明确允许推进后续，不制造新硬门槛。
不签全项目M-1/STEP008或未验证one_call/旧G动态恢复通过。保存可读后只回一句审查结论及结果绝对路径，由编排最终裁定。
