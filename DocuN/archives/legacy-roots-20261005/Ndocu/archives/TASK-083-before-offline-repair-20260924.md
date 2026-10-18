# TASK-083 / R-077 — Windows内部单窗监督切片：实现与合成验证
你是执行Agent，按本卡连续完成实现、相关验证、范围内修正并统一回传，不接管编排。
STEP008；父082，关联076—081、NFR002/003、SEC002、FLOW005、DATA007。接收：沿TASK082原独立诊断窗口转增强实施（实际GPT-6标签如实登记），因掌握协议与官方依据优先复用；082历史诊断独立性不变，但此窗口从本卡起是实现者，不得承担本实现的后续独立安全审计。原窗口不可用才换同等增强新窗口；不沿081未闭合方案实施。
根D:/shspic/project_NO3_RetroLume-agent。需求v1.1、架构v0.35、执行状态v1.40；基线提交45951501d2741630a229762d6b2d3f4b34d7f702及未提交文档差异保护。用户2026-09-24明确“批准”082-work-decision所列内部监督切片与合成验证；不需要再次批准该范围。

## 输入与目标
读取根AGENTS.md、公共D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD（已读未变复用），本卡及Ndocu/results/TASK-082-work-decision.md全部批准条款、TASK-082-result.md的协议与官方事实；需求NFR002/003/SEC002及架构FLOW005/DATA007。必要源码repository/activities导出、001—004迁移、gateway/transport、pdf_import/_windows_job.py及对应活动测试。只加载直接依赖，不通读所有历史任务。
交付完整内部组件：持久关闭门、先预扣后启动的单窗Job监督、不可重开本地发送门、整树退出后可信结算、恢复失败关闭及合成测试；外部产品入口保持未接线。不能只做004账本或模型空壳后声称监督切片完成。
冻结repository SHA256=045a3cf8b1c81d7a1336c3bd2e90e891e4e53934027c9fea9727fafde7202534；004=8f04f57c743c260f5081e0c6f232860301b30c7b03fef69498d7c0704c0a97cc。其他允许改文件先存hash/必要副本，新增文件若已存在先查归属；未知漂移不得覆盖。

## 固定实现合同
1. 新backend/migrations/005_activities_dispatch_closed.sql，仅dispatch_closed BOOLEAN NOT NULL DEFAULT FALSE；单事务先锁activities再判空，非空异常全回滚；001—004不改、不执行迁移。不开会话计数两列。
2. claim成功在同一原事务建立新代次并置false；这是唯一可为新代次开DB门的动作。create无执行资格，默认false不是许可；折叠耗尽关闭、cancel、settle将门置true。其余原锁序/额度/冲突/None含义保留，不新增同代次重新开门API。
3. begin_window_close(activity_id,executor_id,generation)：同原来源→活动锁序，参数校验与既有接口一致，当前running身份代次匹配时仅false→true；返回明确closed/already_closed，不改变R/S/G。当前代次重复幂等，未知/过时/身份不符拒绝不写；不得拿旧close影响新窗。admit与mark_dispatch_started均检查门；关门后原合法record/UNKNOWN及恢复仍可收敛，不因共用helper误挡结果记录。
4. settle正常分支新增已关闭前置；最近G/C受限幂等仍先于当前状态/门检查，合法旧确认不动新窗。仓储C0基础合同保留，真实SUP对成功认领会话只可结算1≤ceil(t1-t0)≤W_eff；不钳制、不伪造0，越界记录违例并停止新工。失败无部分退款，残留按原规则保守折叠，不能为腾余额擅自取消活动。
5. 活动级排他所有权覆盖旧树核对/认领/创建/交接，防迟到创建与重复实例。t0在claim前，结果明确后才创建唯一Job、悬停worker、Assign、固定截止/受信交接、Resume/armed；回应丢失绝不spawn或盲目再认领。SUP/启动器自身管理进程有单独有限运行界限，不宣称管理墙钟全计M。每会话单窗，旧Job未确认空、命名/权限/归属未知均拒绝新窗。
6. Job精确身份绑定活动UUID与G，命名空间/ACL/碰撞/无继承/无breakaway/最后句柄交接明确。ActiveProcesses结构及返回码用本地Windows适用官方事实；确认0只来自可查询的确切Job，主进程退出/Job signaled/查询失败不等于0。必要时有限核对082四页官方文档，不扩展研究。Job不存在分支必须排除错误命名空间/权限失败/迟到创建，无法证明就失败关闭。
7. 本地关闭者先原子阻断新共享令牌，再join已注册调用，不能writer饥饿；令牌从admit前覆盖mark/send/传输及结果收尾。DB关门与本地排空不互相阻塞到失去硬截止；SUP可超时精确kill。已mark未send的交错不能退款后仍发送。Job整树退出正证据后，Job外可信SUP取t1并调用begin_window_close/settle必要流程；worker不能自报停止或自行退款。关闭接口可在退出前发起，但退款必须退出后。生产SUP不得消费模型生成的退出/耗时证据。
8. q/g/s与W关系及停止期限写入实现并可校验，正常参数由工程选择，不让用户逐项配置确认。partial W太小或认领耗时耗尽本窗时拒绝开工，不延后截止。所有kill等待、DB等待、管道/进程等待有限；新窗不因重启获得免费时间。真实超窗如实记录ε与失败关闭，不宣称Windows硬实时。结算提交响应丢失复用原G/C幂等；整机重启不比较旧t0，旧预扣保守处理。

## 文件/资源边界
允许修改：backend/app/activities/repository.py及必要__init__.py；新增005；新增backend/app/worker/内部组件；backend/tests/test_activity_ledger.py、test_activity_recovery.py、test_activity_time_budget.py中因新门真正必要的适配；新增backend/tests/test_activity_dispatch_close.py、test_worker_session.py及必要合成子进程夹具（放backend/tests/fixtures/task083/）；Ndocu/evidence/task-083/、Ndocu/results/TASK-083-result.md。合成夹具不能成为产品运行依赖。
不改gateway/transport主体、PDF监督器、HTTP/main/runtime/前端、001—004、依赖锁、用户配置/数据、正式docu/公共库、旧证据；不Git提交/推送/reset/clean，不安装/下载，不启动Docker/PG/模型/应用服务，不访问真实网络。若必须改gateway主体或新增持久字段才能正确接线，完成不受阻部分后带具体差异交回，不扩大范围。内部worker通过明确注入/合成入口与既有受控gateway契约相容，真实供应商路径本卡不接通。
本卡独占允许源码和测试，无并行实现/测试。无端口、DB、账号、付费预算；本机仅本卡直接创建的合成子进程/Job，不能按进程名或端口杀进程。记录runTag、准确句柄/Job与PID归属，异常也必须finally收尾，原件/日志保留不删除。

## 局部测试子项（增强执行，同卡连续，真实PG另卡）
先实现并完成一次静态覆盖/差异/无秘密与无真实外发检查，再运行有限离线单元及本机Job批次。项目backend/.venv/Scripts/python.exe -B；未知具体测试标识由实现定位并在manifest预先列出，不能用发现式全仓测试。
A. 内部调用门/状态次序：C0禁止、partial W、claim响应丢失不spawn、关门阻止新令牌、已mark未send的交错、关门时在途传输、结算响应丢失、旧代次确认/取消/异常关闭。替身仓储只证调用序，不冒充DB事务/约束通过。
B. Windows真实受控合成Job：正常早停后退款调用顺序；超时/挂死退出；主进程先退而后代仍存活；SUP死亡与句柄关闭；恢复/身份未知或同名碰撞失败关闭。总计最多8个Job场景，每次唯一归属、串行，单Job最多4进程/256MiB，若项目解释器转发器需调整进程数先查事实，不擅自扩大。合成任务只sleep/可控本地计算/管道回执，无外发、文件业务动作或真实模型。
每批墙钟总窗≤10分钟（从首个受控进程创建起，不按part或重启重置），单场景≤30秒且为最后清理预留≤60秒，测试命令≤60秒、所有等待受剩余总预算约束。每场景开始先有独立于被挂起worker的测试控制者持精确对象/截止，不能先放行再补监督。停止失败只对已确认归属对象有限应急终止并报告cleanup_incomplete，不启动后续场景。
最多一次初始批次；明确的范围内实现/夹具缺陷允许一次修正及仅失败/受影响场景复检，单复检批次也≤10分钟，总Job启动数≤16，两个批次单独如实记账，不冒称同一次。连续第二次失败、根因不明、资源归属或清理失败立即停交回；不得按新增脚本/窗口清零修正次数。环境不可用零启动即可交回，不无限预检。已有充分证据不补“放心”测试。
C. 准备真实PG测试但不运行：005空表成功/非空回滚，关门与admit/mark的并发序列，settle关闭前拒绝/关闭后成功/旧幂等不伤新窗、cancel/恢复结果纪律。既有测试只按新门前置适配，保留原业务断言；专用测试DSN缺失明确skip不回退用户DSN。列将来受影响用例标识及原因，不机械全跑或宣称079证据覆盖新行为。

## 交付/审计/停止
提供产品接口/职责清单、增量diff及新旧hash、005未执行声明、有限测试manifest与真实命令/退出码、Job身份与整树结束证据、失败/修正预算账、剩余原始未验证风险、独立审计所需纯合同/最终源码/原始证据导航。截图或文字PASS不能代替对象事实；未运行必须not_run。
后续独立增强审计另新窗口，覆盖发送门与退款竞态、DB锁序、Job归属/重启/未知退出以及预算不重置；本实现者不签安全通过。真实PG及组合验证另卡明确预算。达到本卡范围即停，不宣告M-1/STEP008/项目完成。
允许完成整卡内部常规修正与上述一次复检；新权限/字段/实际无法保证停止语义则提前交回具体缺口，不自行接受风险或增加看门层。结果保存D:/shspic/project_NO3_RetroLume-agent/Ndocu/results/TASK-083-result.md，按TASK/R/STEP、完成/部分/阻塞建议、差异/证据/风险/文档建议/下一步完整回传，不写编排最终验收；只回复一句话结论与可点击绝对路径。
