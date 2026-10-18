# TASK-083 / R-077 — 005及关闭门六例真实PG验证08
接收原083增强执行窗口，沿原任务/实现上下文，不承担独立审计。STEP008，父082、关联084/R078、079/DATA007/FLOW005/NFR002/003/SEC002。根D:/shspic/project_NO3_RetroLume-agent；需求v1.1、架构v0.38、执行状态v1.53；Git基础45951501d2741630a229762d6b2d3f4b34d7f702及全部既有差异保护。
授权：用户082内部切片批准、真实PG另卡明确预算；084 review-03至05已确认PG六例隔离/静态准备可单独安排。本卡由编排仅解冻下述六例及其新合成容器，预算独立登记，不恢复079旧额度，不运行Job或新D1入口，不解决D3恢复。

## 成果与最小输入
完成005空/非空迁移及关闭门实际事务六例，成功或首次失败/环境阻塞后连同精确收尾统一交回。不是实现卡，不修产品/测试，不重跑079全部22例。
入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md；公共D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD，已读未变复用。读TASK-082-work-decision.md批准记录、TASK-084-result.md review-03 PG精确清单及review-05分项门、当前pg_migration.py/pg_close.py的DSN/初始化/清理/六例与必要仓储依赖。TASK-079.md仅复用已批准合成资源隔离和有限runner经验，不能运行旧runner或接管旧资源；不得读输出旧含口令run-result.json。Job07有效证据复用，无重测。
冻结：
backend/tests/fixtures/task083/pg_migration.py 85d27efd9d73ed4c7736b0a0a0268c8dd852b19e29334173426a15c862a105ac
backend/tests/fixtures/task083/pg_close.py 00b58fe7d091a6ef40c1406c81faf211c83da50b79a432e205d8c2677f130970
backend/app/activities/repository.py 929320baf55d625e897324aa76ebe543bda86e73a4bf1c4766c7e552721c5b20
backend/migrations/005_activities_dispatch_closed.sql 26b71a836355fa9620401f6bbb76e9a42668a1ce52077aa91ecb2f61ebeb50eb
其余直接依赖/001—004沿已审冻结记录；新漂移停对应运行，不覆盖。不全仓审计。

## 精确新资源
新容器retrolume-task-083-pg08-<runTag>，标签retrolume-task=083、retrolume-phase=pg08、retrolume-run=<runTag>。固定已在本机使用过的镜像sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f；本卡先查在位，不拉取/构建/安装。1CPU、512MiB、pids128、restart=no、无宿主挂载、非host网络，仅127.0.0.1:55437→5432。占用即停，不杀占用者、不换端口。旧073/074/079及任何其他容器不接管、不启动、不停止、不删除。
本新容器创建单一专用库retrolume_task083_pg08；合成账号随机口令，只在本次子进程环境/受控Docker创建中注入，日志脱敏，不输出完整含口令DSN、不读取真实配置、不改全局环境。只设置RETROLUME_TASK_083_DATABASE_URL指向本新库；每例由已审夹具创建独立随机schema，同一search_path贯穿仓储/查询/并发/清理。缺DSN或身份不明不得启动，不把skip当通过。连接核对current_database/current_user/server_port与容器身份，错配即停。
测试夹具成功时既有按合成UUID/FK清理允许执行；schema全部保留，失败数据保留。不得新增DROP schema/database、删容器/卷或全表清理；不执行用户库迁移。005仅由夹具在新schema内执行。

## 唯一批次与精确用例
先存manifest：hash/版本/命令/资源限制/超时及finally停止办法，文本核对runner后一次静态准备检查≤60秒（无需编译产品或补纯单元）。允许只在本轮证据目录准备脱敏、有限超时runner，不改生产/夹具或新建通用平台。
一次只读预检Docker可达、镜像在位、55437空闲、项目venv可用、冻结匹配。不可达/缺镜像即环境阻塞，不自行启动Docker Desktop或循环重试。创建唯一容器前先完成超时与finally收尾；记录准确容器ID及脱敏inspect：名称/标签/镜像/限制/绑定/无挂载。创建≤30秒、就绪≤30秒，到期即停。
仅一次unittest进程、failfast，精确六方法；在backend/tests工作目录，以绝对项目backend/.venv/Scripts/python.exe -B -m unittest -v -f依次指定：
fixtures.task083.pg_migration.PGMigrationTests.test_pg_migration_01_empty_table_adds_only_closed_column
fixtures.task083.pg_migration.PGMigrationTests.test_pg_migration_02_nonempty_table_rolls_back_whole_005
fixtures.task083.pg_close.PGCloseTests.test_pg01_close_settle_and_old_gc_does_not_touch_new_window
fixtures.task083.pg_close.PGCloseTests.test_pg02_closed_gate_rejects_admit_mark_but_records_outcomes
fixtures.task083.pg_close.PGCloseTests.test_pg03_close_commits_before_concurrent_admit_and_mark
fixtures.task083.pg_close.PGCloseTests.test_pg04_cancel_closes_gate_and_old_dispatched_unknown_converges
保留夹具现有兼容loop_factory，不切换循环/改依赖。预期6实际运行、0失败/错误/skip；并发例仅既有锁序交错，不增加压力。任一失败/超时/skip/身份或清理未知立即停批，无修正重跑，无第二容器、第二unittest进程。
新正常总窗自创建起≤10分钟，所有等待受剩余deadline；单独资源/DB检查命令≤30秒，unittest整体硬超时120秒，至少预留60秒finally收尾。不把tool yield当命令结束。超时仅结束本次准确进程句柄/可证创建时间归属的后代，不按名称/端口查杀。
无论成败确认测试子进程退出，核实本次容器ID/标签后stop并inspect Running=false；stop失败只可对同一已核实ID一次kill再inspect，应急≤60秒如实记超限。停止后保留容器、库/schema/数据供后续取证。不能确认则cleanup_incomplete，不签整体通过。

## 交付、权限与后续
只写Ndocu/evidence/task-083/pg-run-08/和Ndocu/results/TASK-083-result.md置顶保留历史；源码/测试/迁移/正式docu/公共库/旧证据/Git零写入。串行独占新库和本卡进程，禁止其他运行/源码并行。无模型、HTTP业务、外网/安装、Job、浏览器/资料测试。不改本机或DB系统时间。
保存脱敏命令、原始输出/退出码、单一来源耗时、Python/psycopg/PG版本、前后hash、六例实际状态、schema清单/失败保留、容器身份与最终Running=false。重点区分005空库成功与非空回滚、关门对admit/mark的实际拒绝、关门后合法outcome、旧G/C幂等不碰新窗、锁序与取消UNKNOWN；不额外写重复SQL测试证明既有断言。
通过也只确认这六个当前真实PG用例；不把它扩成新D1真实launcher或跨恢复时间保证。Job07已验局部行为不重测，D3恢复/新D1入口仍是后续独立路线。实际身份如实登记，不自行签M-1/STEP008或独立安全通过。结果保存可读后只回一句结论及绝对路径。
