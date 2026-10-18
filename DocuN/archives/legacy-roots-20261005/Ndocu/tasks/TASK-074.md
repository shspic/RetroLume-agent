你是执行Agent，完成后输出供用户带回Astra的结果包。
TASK-074 / R-068；类型：测试夹具定向修复＋同卡真实PG验证；STEP-008局部；父TASK-073，关联068/069/071/072、NFR-002/003、SEC-002、FLOW-005、DATA-007。
执行者Work Buddy / GLM-5.3-Flash，B档，新会话或沿073会话接续均可。本次只补一个查询字段并运行既定六例，难度有限；产品代码安全审计072仍适用，不重审。
根D:/shspic/project_NO3_RetroLume-agent；需求v1.1、架构v0.24、执行状态v1.17。原07本地合成验证授权；不付费、不外发。

目标/背景：
073真实运行test_01在195行KeyError: execution_generation；其182行SELECT没有该字段。failfast使test_02—06未执行。不是已证实产品缺陷；test01本身未通过，不能因前置断言成功标完整通过。
只补test_01的SELECT字段，保留原断言，然后一次真实运行六例及清理核对。修复与这次紧密验证已一并授权，无须另等运行卡。

上下文：
根AGENTS.md、docu/AGENTS.MD；当前执行状态R-067；backend/tests/test_activity_recovery.py的test01及清理；001/002迁移、runtime.py按需读取。
失败证据Ndocu/evidence/task-073/20260921T1254-wbA1/test-output-utf8.txt。
可复用该目录run_task073.py的限时运行/收尾结构，复制到本次证据目录并只更换任务、runTag、输出、新容器标识和DSN。禁止直接再运行旧控制脚本或覆盖旧证据。旧run-result.json含本地合成口令，不输出全文或外传，不读取真实凭据。
不要重新复现旧KeyError；不要加载整个项目历史。

冻结输入：
backend/tests/test_activity_recovery.py
ef705113fbf6af83a0a29e99b40dfdb68109282c0ae8b724790e1d440575d246
backend/app/activities/repository.py
50ec537b07533c68194651b008d275176430effeb67126391ef43b96155cfce6
backend/migrations/001_materials.sql
767f47c331ba1e0322e48ffcedfb46619ba53b175b9c0aa69ae267a6d5f07a8d
backend/migrations/002_activities.sql
3a9c5855aa9ddc54a03666327267ff3b7cb81eafa931a9f260c5637922b2dda6
不符先查差异，不覆盖不明改动。

允许修改：
仅test_activity_recovery.py中test_01读取操作结果的SELECT增加execution_generation列。
保存修改前副本、新旧hash和最小diff到Ndocu/evidence/task-074/<唯一runTag>/；只在该目录写本次运行控制/证据，结果写Ndocu/results/TASK-074-result.md。
所有断言、其余五用例、清理顺序、生产代码、DDL、依赖锁、正式docu、Git和旧证据保持。不得改SELECT为*、删除断言、降低门槛或顺手重构。

修复验证：
差异确认只补字段；用项目backend/.venv/Scripts/python.exe对该测试文件compile一次，不写pyc，最多60秒。
随即执行下述同卡PG验证；不再单独制造修复批准环节。发现别的实际缺陷留证交回，不扩大修复范围。

运行资源：
一个全新容器retrolume-task-074-pg-<runTag>，标签retrolume-task=074、retrolume-run=<runTag>。
固定本机镜像sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f；不拉取/构建。
1CPU、512MiB、pids128、restart=no、无宿主挂载、非host网络、仅127.0.0.1:55435→5432。
全新库retrolume_task074_synthetic，专用合成账号/口令。停止后保留容器/卷，不删除。
绝不接管旧073容器da18c806a871780500df3bdf2b612632afa7c5721e122e80437b6c248c1d2a62或任何历史容器/用户库。55435占用即阻塞，不换端口或杀占用者。
源码/测试本卡独占；无并行写入或共享数据库。

一次运行：
1. 只读预检Docker可达、镜像在位、55435空闲、项目venv可用、新旧hash符合。Docker未运行则报告，不自行启动Desktop/循环等待；缺镜像不下载。
2. 先设命令限时与finally收尾，创建唯一容器，记录ID/标签/镜像/资源/端口/挂载；后续按已核实ID操作，新库就绪最多30秒。同名冲突即阻塞。
3. 新库001、002各执行一次，经stdin传给psql -v ON_ERROR_STOP=1 -f -，失败即停；不跑003，不调用旧run_ledger_check.py。
4. 仅本次子进程环境设置RETROLUME_TASK_068_DATABASE_URL指向新库。cwd=backend，用项目venv运行：
./.venv/Scripts/python.exe -B -m unittest -f -v tests.test_activity_recovery
唯一一次实际测试启动，failfast，失败不改码、不重试。六例均需运行：073的test01不完整，02—06未运行，故本次不是重跑已通过六例。
5. 成功后只读查新库material_sources、material_versions、activities、activity_scope_sources、activity_allowed_models、activity_operations六表均为0；失败保留现场，不手动清空。
6. 所有路径收尾：测试进程退出，停止本次容器并确认Running=false，容器/卷保留。未知或停止未确认必须报cleanup_incomplete，不能PASS。

限量与停止权限：
一次compile＋一次PG测试批次；不重跑055/资料/PDF/模型，不做EXPLAIN/并发/压力或时钟测试，不扩模拟器。
首次创建起正常总窗10分钟；创建30秒、就绪30秒、测试硬超时120秒，所有命令不超过剩余时间并预留收尾。采用073已有受监督方式，不能仅阶段前后看时间。
只停止本次直接创建的进程句柄或核实PID+创建时间及归属的后代；不能按名称/端口/裸PID杀进程。
容器停止前核对ID/名称/本次标签；正常stop失败允许对同一ID一次kill并inspect，应急额外最多60秒，记录超时，不冒称准时。
不改变全局环境/代理，不启动应用/浏览器，不读真实配置，不安装、不联网或付费。监督方式不足时报告具体缺口，不造新的通用平台。

验收与证据：
修复仅一处查询投影，原断言保留；六例实际运行、0失败/错误/skip，test06的2/2/1/0通过；六表清理核对成功、自有资源停止确认，方可建议通过。
保存diff/hash、真实命令/退出码、原始stdout/stderr、Python/psycopg/PG版本、迁移结果、逐例状态、起止/单调耗时、六表计数和容器停止证据。记录相关导入源码hash；不要为日志转码重跑。
失败区分夹具/产品/环境，不把前置断言通过当整例通过。未选范围如实not_run。产品代码未变不要求重跑072审计。
完成即停；发现额外缺陷、快照冲突或超时收尾后交回，不继续试错。

回传：
TASK/R/STEP、实际模型/会话、建议状态、唯一改动和新hash、实际启动次数、六例状态/命令/证据、清理及保留资源、未验证与风险、文档建议、必要人工操作、下一步。
保存指定结果并回复完整可复制块，不填Astra最终验收，不宣告完整G-1/STEP008/项目完成。
