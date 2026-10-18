你是执行Agent，完成后输出结果供用户带回Astra，不接管编排。
TASK-067 / R-061；类型：测试；STEP-004/005；父TASK-066，关联065/064/061、FR-001、DR-001/003、NFR-002。
执行者：Work Buddy（GLM或KIMI K3），B档，新会话，记录实际标签。冻结脚本仅两个明确API/重启场景及资源收尾，中档足够，不是独立安全审计。
项目根：D:/shspic/project_NO3_RetroLume-agent；需求文档v1.1、架构v0.19、执行状态v1.11。原07开发及合成测试授权；本卡仅授权新的一次剩余场景运行，无模型费用。

目标/已有事实：
065已有s1a/s2/s3/s1b/s5成功证据，保留不重测；s4因样本作用域错误失败、s6未运行。066已将pdfBuffer提升至main局部，并提供--remaining-s4-s6真实API最小准备及准确摘要；仅离线验收通过。
本卡只补s4替换/CAS与s6真实应用重启持久化，不启动浏览器、不重跑五个场景，不把它们写成本轮passed。

上下文：
先读根AGENTS.md、docu/AGENTS.MD、Ndocu/TASK_TEMPLATE.md、当前执行状态入口。
读TASK066结果和主脚本的参数/准备/s4/s6/监督收尾；复用Ndocu/evidence/task-065/task065-run1-20260921T0136Z/已有环境、源码与构建证据，未变部分不重跑检查。
必要上下文读取被执行环境拒绝时按正常机制处理，不能绕过。

冻结SHA256：
tests/task054_pdf_materials_integration.mjs 130a5bc9998bb8b2be049ebbd44c9d34b13518c050900c8b36295557121ff8e2
tests/task064_candidate_constraints.mjs 2c050cbc2f36c6f076a33b9b4550ad346a75713c877f1d74620b2d993e48a619
tests/task057_watchdog.mjs 13512a7054a38769f178e6bd70267b35b8d65a7ced680cdfdfdbd0dff8efcfe9
tests/task059_proc_tree.mjs 4523063ae0f72641dd5acb5db8a7a86b03808c7883671427d13d2ef9006e53b7
tests/task059_proc.ps1 281aa07cdc9ef9f722244a2482f64c18cd4065c2612684a996768085a0c711e3
只核对一次；不符或被测源码正在修改即阻塞，不能覆盖匹配。将新增纯函数hash一并保存。

前置/资源：
只读核对当次Docker daemon、固定镜像sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f在本机、55434/8000空闲，以及现有Node24.15.0、backend/.venv和powershell.exe可用。
使用脚本创建的本次runTag唯一合成PG容器：1CPU/512MiB/PID128/restart=no、无宿主挂载、仅127.0.0.1:55434；新库001/002/003一次；应用8000、本次独立合成数据/备份。旧065容器2340202877caabce67cd390090be72f13b6abfa908fae3503e4463432d0940a2及其他旧容器/用户库不接管、不启动、不删除。
缺daemon/镜像或端口占用即阻塞，不循环等待、不拉取、不安装、不停止他人进程。剩余模式不依赖浏览器启动，不要求重建前端。

允许写：
Ndocu/evidence/task-067/<本次唯一目录>/、Ndocu/results/TASK-067-result.md及脚本生成的本次合成数据/监督状态/新容器数据。
禁止实现/夹具/迁移/依赖锁/正式docu/旧证据修改；禁止模型、外部发送、凭据读取、Git和清理。无并行占用本次端口或改动被测源码的任务。

唯一执行：
设置本执行进程RETROLUME_TASK_EVIDENCE指向新唯一目录，在项目根运行：
node tests/task054_pdf_materials_integration.mjs --remaining-s4-s6
只能一次；失败即停，不现场修码、不重试、不转全套模式。
复用065已经成功的启动方式；若PowerShell Start-Process出现大小写重复环境键，不删除系统环境变量或更改全局代理。优先直接调用现有Node并保存原始输出，不为日志编码重跑。

验收：
准备：通过真实API创建并确认两页PDF及第二页user_supplement，核对返回后进入s4/s6；不得直写数据库或用旧库预置。
s4：待核对替换时旧版可读；陈旧候选CAS拒绝；跳过及失败保留更新后的TXT，不降低原断言。
s6：真实确认本次应用停止，再启动应用；数据库计数、PDF版本/页文字/补充身份、更新TXT、pending候选保留，最终应用停止确认。
只有s4/s6实际passed且自有资源收尾确认，才报剩余场景通过候选；其他五个标识保持本轮not_run/not_selected。准备不计作重验s2/s3，整体由Astra合并旧证据。

限额/停止：
总窗口最多10分钟，无浏览器；不提高既有监督/资源上限。应急停止仅自有已核实资源，既有期限后5分钟应急硬上限单独记录，超时/监督触发/停止未知不得通过。
不能用外层超时杀主脚本后声称资源清理完成；读取最终监督和停止记录。达到硬上限仍未确认，带具体ID/进程身份及最少人工恢复步骤回报，不无限等待。
容器及卷停止后保留，不删除。没有浏览器就写未启动，不补截图、不触碰个人浏览器。

返回：
保存指定结果文件，回复完整结果块：TASK/R/STEP、唯一运行次数、环境/冻结hash、准备与s4/s6实际结果、其余未选场景、准确命令/退出码/单调及墙钟时间、原始日志/摘要/监督与停止证据、自有残留、未验证/风险、文档建议、必须人工操作和下一步。用UTF-8保存新增文字，原始输出保留。不要宣告STEP/项目/08完成，不填Astra验收结论。
