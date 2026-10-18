# TASK-079 / R-073 — 时间账本定向真实PG验证

你是执行Agent；完成准备、迁移检查、既定用例及收尾后统一回传，不接管编排。
接收：Work Buddy常规执行Agent，优先继续TASK077修正轮02运行构造检查的窗口；不是TASK078独立审计窗口。若原实现窗口不可用，新窗口按本卡最小上下文接续，保持编号/预算。实际模型如实登记，不以型号不同重做成果。方案、断言和资源边界已明确，可用常规执行完成；产品根因不明或需扩大修复时停止交编排，不自行处理复杂高风险改动。
关联：STEP008；父TASK077；审计TASK078 review02+03；NFR002/003、SEC002、FLOW005、DATA007。需求v1.1、架构v0.30、执行状态v1.31。
项目根D:/shspic/project_NO3_RetroLume-agent；根入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。
公共规则D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD（2026-09-23T09:02:19.8371311+08:00）。编排依据同公共根docu/WORK.MD（2026-09-23T09:04:14.5455941+08:00），无需执行者全文读。公共库只读。
授权：当前07本地合成验证范围内，编排本卡明确新增一次限量PG验证批次；不是复用073/074已耗额度。用户库/真实账号/付费模型/发布均不授权。独立代码复核已经回收，N1已修；本卡取得此前缺失的004及事务行为证据，不证明worker/M-1或整项目完成。

## 最小上下文与冻结
读取本卡、根入口/公共AGENTS；同窗口未变已读材料不用重载。读三测试文件中DSN、loop factory、初始化/清理和选定用例，001/002/004迁移及必要repository/runtime依赖；078结果只需review03的PG清单及未验证范围，不读整段历史。复用Ndocu/evidence/task-074/20260921T1319-wbB1/run_task074.py的命令限时/finally收尾结构，复制到本卡证据目录再适配；不能直接运行旧脚本或接管旧资源，不读/输出旧run-result.json（含合成口令）。无须重建通用测试平台。
冻结SHA256（开始前一次核对，结束再次绑定）：
- backend/app/activities/repository.py：045a3cf8b1c81d7a1336c3bd2e90e891e4e53934027c9fea9727fafde7202534
- backend/app/activities/__init__.py：6bdb960912ea3fc7ddd8730f37a44e580b73768e1067d23facc9983ca04a46dd
- backend/migrations/001_materials.sql：767f47c331ba1e0322e48ffcedfb46619ba53b175b9c0aa69ae267a6d5f07a8d
- backend/migrations/002_activities.sql：3a9c5855aa9ddc54a03666327267ff3b7cb81eafa931a9f260c5637922b2dda6
- backend/migrations/004_activities_time_budget.sql：8f04f57c743c260f5081e0c6f232860301b30c7b03fef69498d7c0704c0a97cc
- backend/tests/test_activity_time_budget.py：63a19d1f2a99236d56bd1cc1841953908fa8c1f955ff0c6d5d61b4ee84621a86
- backend/tests/test_activity_ledger.py：fb174d4c29355bb0e57ac013d4e8555ef9ac342e9be804e0edbf732112de63da
- backend/tests/test_activity_recovery.py：0e5d9c89a7a3fce490cc60deb7c0a608b8c54356edd7c4b18ee66165bf88bf7a
其他实际导入的项目文件记录hash，不要求重审。不明漂移先报告，不覆盖/测未知快照。构造check/compile已有证据，不再运行。

## 读写及运行资源
只写Ndocu/evidence/task-079/<唯一runTag>/下运行控制、合成检查脚本、日志和证据；结果Ndocu/results/TASK-079-result.md。业务代码/现有测试/迁移/依赖锁/正式docu/公共库/旧证据/Git均不得修改。仅允许本卡最小运行器与SQL反例脚本，无通用框架。
一个全新容器retrolume-task-079-pg-<runTag>；标签retrolume-task=079、retrolume-run=<runTag>。固定本机镜像sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f，不拉取/构建/安装。1CPU、512MiB、pids128、restart=no、无宿主挂载、非host网络、仅127.0.0.1:55436→5432；端口占用即报告，不杀占用者或随意换端口。
本新容器内三专用数据库：retrolume_task079_budget（新时间测试+recovery）、retrolume_task079_ledger（旧ledger测试）、retrolume_task079_reject（非空拒绝样本）。全新合成账号/口令，仅进本次子进程环境，不读取用户DSN/真实配置，不输出明文口令/完整含口令DSN，不改全局环境/代理。
旧ledger的asyncSetUp会DELETE其专用库测试表、DROP指定测试触发器/函数；这些现成测试动作只允许在新ledger库内执行，不得指向其他库。本卡不删除数据库、容器或卷；测试结束停止后保留全部本卡资源。
本卡串行独占测试库和自身证据路径；源码冻结，不与实现任务并行。历史073/074及其他容器一律不接管、不启动、不停止、不删除。

## 连续步骤及可观察标准
1. 一次只读预检Docker可达、固定镜像在位、55436空闲、项目backend/.venv/Scripts/python.exe可用、冻结hash相符。Docker不可达即返回环境阻塞，不自行启动Desktop/循环等；缺镜像不下载。记录Python/psycopg与PG实际版本。
2. 先建立命令超时和finally收尾，再创建唯一容器；同名冲突停止、不复用。保存准确容器ID、标签、镜像、资源和端口绑定/挂载的脱敏inspect，后续只操作核实ID。创建三新库，连接身份/current_database/server_port等校验与清单一致；未确认新库身份不得跑测试。就绪最多30秒。
3. 三库先分别应用001、002各一次；budget/ledger在activities确为空时应用004各一次。使用原SQL全文经stdin给psql -v ON_ERROR_STOP=1 -f -，不得删BEGIN/COMMIT或改写迁移。003无本卡依赖不运行，未跑003不宣称完整用户数据库升级通过。budget/ledger实际目录检查新增五列的类型、3个NOT NULL、2个DEFAULT 0及004新增8个CHECK；002既有CHECK也会存在，不能错误断言全表总共只有8条。记录pg_catalog定义并按逻辑分别核对，不用脆弱整串相等误报。
4. reject库仅001/002，插入一行符合旧模式的合成activities（pending、有效原必填限额、无来源依赖），保存行及DDL前快照。尝试004一次：预期非空拒绝；psql本次非零属预期，须捕获具体拒绝原因，不能把连接/权限/语法错误当预期成功。结束连接使异常事务回滚后，用新连接核对原行保留、五新列均不存在、约束/表结构与前快照一致、无部分DDL。保留此库样本不清空、不重跑004。
5. budget库内一个最小SQL/psycopg约束批次：使用全新合成活动ID；每个反例用保存点或独立事务，成功正例验证后也回滚，保证进入业务测试前六业务表均空。反例不得破坏001/002原约束而误命中错误对象，running样本须同时有executor/lease。记录SQLSTATE及实际constraint_name/定义，确认击中预期约束；只见异常不够。
   - M=0、M=2147483648；R=-1；S=-1；generation=-1且seconds=0；seconds=-1且generation=0。
   - balance：合法running形状和非负数，但R>M-S。
   - running_shape两向：pending且R>0；running且R=0（其他身份/lease合法）。
   - pair：generation有值/seconds NULL，以及反向。
   - 正例NULL/NULL和0/0，各自满足其余约束。
   - NOT NULL分别将M/R/S设NULL应拒绝；省略R/S的合法行读回两者0。M有效上界可在正例中使用，不增加随机压力样本。
   每个选定样本一次；关联约束冲突应在运行前设计避免。不得用SQL字符串断言/mock替代DB执行。
6. 一次现成unittest启动，cwd=D:/shspic/project_NO3_RetroLume-agent/backend，项目解释器：
   ./.venv/Scripts/python.exe -B -m unittest -f -v tests.test_activity_time_budget tests.test_activity_recovery tests.test_activity_ledger
   仅子进程环境：RETROLUME_TIME_BUDGET_TEST_DATABASE_URL和RETROLUME_TASK_068_DATABASE_URL指向本次budget库；RETROLUME_TASK_048_DATABASE_URL指向本次ledger库。缺任一变量或身份不符即拒绝启动，绝不回退用户DSN。保持项目已有Selector loop，不改循环。预期8+6+8=22方法实际执行，0失败/错误/skip；time test08使用fold_reclaim_partial_window现名。恢复test06的2/2/1/0断言保留，ledger test02现有并发重复准入属于既定用例，不额外做压力或锁测试。这22例均直接依赖改变后的claim/cancel或新夹具，旧074证据不能替代当前快照。
7. 成功后只读查六表material_sources、material_versions、activities、activity_scope_sources、activity_allowed_models、activity_operations：budget库应全0（新测试/recovery有定向tearDown）；ledger原套件只有setUp、最后例可能留下合成行，不误判为必须全0，记录实际行数/本卡归属并保留，不手工删除凑0。reject样本按第4步保留。任一失败保留现场和已通过/未运行项，停止后续步骤并收尾。
8. 无论成功失败均确认测试自有进程退出，停止本次容器并inspect Running=false；容器/卷/库保留。无法确认报cleanup_incomplete，不判整体通过。

## 限量、失败与停止
本卡新增一个运行批次、一个容器、最多一次unittest启动；不跑基线/构造/compile/旧浏览器/资料/PDF/真实模型。总正常运行窗自首次创建起10分钟，创建≤30秒、就绪≤30秒、单迁移/DB检查命令≤30秒、约束批次≤90秒、unittest硬超时180秒；所有命令不能超过剩余总窗，至少预留60秒收尾。准备脚本允许一次静态覆盖/资源一致性检查，不单开“准备验收”卡。
使用现有有限subprocess超时/受监督机制，不能仅口头或阶段前后计时。仅停止本次直接创建的进程句柄或有PID+创建时间/归属证明的后代，不按名称、端口或裸PID杀进程。每次容器停止前核对ID/名称/本次标签；stop失败可对同一核实ID一次kill并inspect，应急额外最多60秒并如实报超时，不冒称准时。归属未知不触碰外来资源。
任何非预期实际失败/skip/超时/清理失败，保留原始证据、分类产品/夹具/环境，停止且不改产品/旧测试、不重试。预期SQL约束拒绝和非空迁移拒绝按上面明确标准算检查通过，不触发误停。零启动环境阻塞不算业务失败，不自行反复预检或换端口。方案/资源不足以受控运行则报告具体缺口，不无监督启动。
达到覆盖即停，不加并发压力/时钟回拨/worker/EXPLAIN/故障恢复实验。旧073/074各一次及13元费用额度仍已耗尽，不能挪用或重置。

## 回报与验收
保存真实命令（口令脱敏）、退出码、UTF-8/原字节stdout/stderr、起止及单调耗时、运行计数、版本/hash、迁移/目录约束、逐反例SQLSTATE/命中约束、22例逐项状态、三库行数和容器收尾身份/状态。执行成功证据与not_run分开；单例通过保留但不能覆盖整体失败。
结果写D:/shspic/project_NO3_RetroLume-agent/Ndocu/results/TASK-079-result.md，先结论/证据导航后必要详情；列实际模型/窗口、资源保留清单、未验证边界、偏差/风险及文档建议。不得填编排最终验收，不宣告M-1/worker/STEP008或08通过。
确认结果可读后，只回复一句结论和可点击绝对路径，由用户回传；不展开全文。正式状态和CHANGE由编排维护。
