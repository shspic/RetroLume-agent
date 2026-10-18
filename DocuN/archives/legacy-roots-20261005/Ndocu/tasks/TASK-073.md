你是本卡执行Agent，完成后输出供用户带回Astra的结果包。
TASK-073 / R-067；类型：定向真实PG测试；STEP-008局部；父TASK-071，关联068/069/070/072、NFR-002/003、SEC-002、FLOW-005、DATA-007。
执行者：Work Buddy / GLM-5.3-Flash，B档，新会话。六个现成用例、固定合成环境，中档负责运行与收尾；独立代码审计已由072强档完成，不由本卡替代。
项目根D:/shspic/project_NO3_RetroLume-agent；需求文档v1.1、架构v0.24、执行状态v1.16。原07授权内的本地合成验证，不调用付费服务。

目标/前置：
072差异审计无确定缺陷；071仅编译通过，六个PG用例均未运行。
一次运行test_activity_recovery的test_01—06，验证发现/隔离、旧代次收敛、终态与预留、晚到保护、分批2/2/1/0及定向清理。
不重跑055旧套件、资料/PDF、模型、性能/压力、EXPLAIN；不证明M-1、完整worker或整项目完成。

最小上下文：
读根AGENTS.md、docu/AGENTS.MD；本卡和当前执行状态R-066段。
读backend/tests/test_activity_recovery.py及runtime.py的loop factory；按需读activities/repository.py、001_materials.sql、002_activities.sql。
复用069外键清理、071批次实现、072差异审计结论，不重写已完成内容。
冻结：
backend/app/activities/repository.py
50ec537b07533c68194651b008d275176430effeb67126391ef43b96155cfce6
backend/tests/test_activity_recovery.py
ef705113fbf6af83a0a29e99b40dfdb68109282c0ae8b724790e1d440575d246
backend/migrations/001_materials.sql
767f47c331ba1e0322e48ffcedfb46619ba53b175b9c0aa69ae267a6d5f07a8d
backend/migrations/002_activities.sql
3a9c5855aa9ddc54a03666327267ff3b7cb81eafa931a9f260c5637922b2dda6
不符报告差异，不覆盖或继续测不明快照。记录其余实际导入的activities/capabilities/runtime文件hash供证据绑定。

授权资源/独占边界：
仅一个全新合成容器retrolume-task-073-pg-<唯一runTag>，标签retrolume-task=073及retrolume-run=<runTag>。
仅用已在机镜像sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f；不拉取/构建。
1 CPU、512MiB、pids-limit128、restart=no、无宿主挂载、非host网络，仅127.0.0.1:55435→5432。新端口隔离历史55433/55434；不得绑定0.0.0.0或换占用端口。
数据库retrolume_task073_synthetic；合成专用账号/密码仅用于本容器，不读用户配置或真实凭据。自动产生的数据卷随容器停止保留。
不接管/启动/停止/删除任何历史容器或用户数据库，不改全局环境/代理。
允许只读源码；仅写Ndocu/evidence/task-073/<唯一runTag>/和Ndocu/results/TASK-073-result.md。可在本证据目录放最小运行控制脚本，用于命令限时、证据和finally收尾，不新增通用测试框架/业务夹具。
生产、测试、迁移、依赖/锁、正式docu、Git及旧证据禁止修改；不安装，不启动应用/浏览器，不使用真实资料。期间源码冻结，无共享库并行写入。

执行步骤：
1. 一次只读预检Docker可达、固定镜像在位、55435空闲、项目backend/.venv/Scripts/python.exe可用、hash一致。Docker不可用即阻塞，不自行启动Desktop或循环等环境；镜像缺失不下载。记录项目Python/psycopg与PG实际版本，不做3.13重复测试。
2. 先安排限时和失败收尾，再创建上述唯一容器；同名冲突即停止，不复用。保存实际ID、标签、镜像及资源/端口/挂载inspect。后续操作仅用核实ID。新库就绪等待最多30秒。
3. 仅新库按顺序执行001、002各一次；原文件经stdin传给psql -v ON_ERROR_STOP=1 -f -，避免长命令/引号改写DDL。失败即停止，不修改/重复迁移；不执行003或旧run_ledger_check.py（它运行其他套件）。
4. 仅在本次测试子进程环境设置RETROLUME_TASK_068_DATABASE_URL，指向新库127.0.0.1:55435。不得回退用户DSN。cwd为backend，用项目venv执行：
   ./.venv/Scripts/python.exe -B -m unittest -f -v tests.test_activity_recovery
   唯一一次测试启动，failfast；不先跑基线、不复现旧失败、不失败后改码重试。既有测试使用项目Selector loop factory，不另改循环。
5. 全部成功后，仅在新库只读核对material_sources、material_versions、activities、activity_scope_sources、activity_allowed_models、activity_operations六表测试行数均为0，证明该批测试清理；失败时保留库现场，不手动清空。
6. 无论成功失败，停止本次测试进程及容器，确认容器State.Running=false、测试自有进程退出；保留容器/卷、日志。未能确认必须报cleanup_incomplete，不判通过。

限量/监督：
从首次创建起总正常窗口10分钟；单次创建30秒，PG就绪30秒，测试子进程硬超时120秒；命令均有超时且不超过剩余窗口，预留停止时间。
采用工具可强制终止的受监督子进程/最小控制脚本，不能只有阶段前后检查或仅口头计时。记录单调耗时与墙钟起止；超时不继续下一用例。
停止仅针对本次直接创建的进程句柄或核验PID+创建时间的自有进程及其已证明后代；可只读复用tests/task059_proc_tree.mjs及task059_proc.ps1，不修改，不按名称/端口杀进程。
容器停止前核对本次ID/名称/标签。正常停止失败时允许对同一核实ID一次docker kill并inspect；额外应急最多60秒，记超时/应急，不伪报准时成功。未知身份不停止外来资源，具体记录并交回。
不为测试再构建监督平台；现有工具无法满足有限收尾时报告具体缺口，禁止无监督启动。
任何实际测试失败，记录原始错误和未运行项后收尾即停；不得扩大诊断/运行次数。零启动的环境阻塞不冒充测试失败或测试通过。

验收/证据：
六个test方法实际运行、0失败/错误/skip；test06实际2/2/1/0通过；六表清理核对通过；资源收尾确认，才可建议本卡通过。
若skip、超时、部分运行或清理失败，不能凭exit0宣告通过。
保存实际命令、退出码、原始stdout/stderr、版本、hash、迁移输出、逐例状态、运行起止/耗时、六表计数、容器ID和停止证据。日志采用明确UTF-8或字节级重定向；不要为转码重跑。
无独立并发/时钟/性能验证，不把六例成功外推成相应保证。没有代码改动，无需重跑审计。

停止/回传：
达验收即停。产品或测试缺陷都不在本卡修；两类明确区分。保留现场，交Astra决定。
返回TASK/R/STEP、实际客户端/模型、建议结果、唯一运行次数、六例状态与退出码、命令/证据路径、清理及保留资源、失败/未验证/限制、文档建议、必要人工操作、下一步。
保存指定结果文件并回复完整可复制结果块。不填Astra最终验收，不宣告G-1、STEP008、08或项目完成。
