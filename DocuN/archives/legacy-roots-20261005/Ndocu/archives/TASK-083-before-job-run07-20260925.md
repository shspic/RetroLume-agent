# TASK-083 / R-077 — 生命周期夹具完整修正06
接收原083增强实现窗口，沿原任务，不担任独立审计。STEP008，父082，关联084/R078、NFR002/003、SEC002。根D:/shspic/project_NO3_RetroLume-agent；需求v1.1、架构v0.38、执行状态v1.50；Git基础45951501d2741630a229762d6b2d3f4b34d7f702与全部未提交差异保护。授权沿已批准082内部切片，仅测试夹具范围。

## 成果与输入
一次合并修复review-04已定位三处同链缺陷，交付最终三例纯离线证据；不是逐错试跑。根入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md，公共D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD，已读未变复用。读TASK-084-result.md当前review-04、review-04/hashes.txt与初判，stub-fix-05原始失败/差异、当前三个夹具文件和必要直接依赖。原批准Ndocu/results/TASK-082-work-decision.md有效；上一卡归档Ndocu/archives/TASK-083-before-fixture-completion06-20260925.md。
review-04确认04控制器句柄合同静态满足、05局部时钟静态可运行；不重写它们，不升级为动态通过。D1期限/碰撞已PASS且依赖未改，复用；第12及其余未变证据不重跑。旧05根因保留未证。

## 冻结与完整三项修正
仅修改backend/tests/fixtures/task083/focused_unit.py的StartLifecycleTests局部，当前hash=4a633aff536f833cdbf3a266be2d44de70b8e01105a204b68d7947995627a1ca。先保存真实字节副本/hash。漂移先查明，不覆盖。
1. fake_spawn从真实spawn实参派生活动UUID/G/runTag，按真实job_name函数构造created/resumed回执；类型与子进程协议一致，不patch控制器uuid4、不固定控制器内部随机身份、不取消任何身份校验。保持pid/creation_time及现有协议字段。参数索引以实际调用核对，不能仅机械照抄报告数字。
2. _run带回本次派生身份，open_existing及相关正反断言改用该身份；成功、spawn异常、空回执分支均须定义清晰，不让未产生身份变量造成新异常。断言须能发现不应发生的任何open_existing调用，不以检查错误的硬编码元组掩盖行为。
3. 两次fake_windll生成的Kernel用互不相交句柄基址/空间；保持每类API的返回、指针输出与调用记录语义，Start句柄和worker句柄不再撞号。继续验证Start回执后关闭及恰一次释放、观察Job先释放再Exit、失败清理，不改断言迎合错误次序。
三项一次完成后静态沿真实verify_last_handle整条成功和两种失败分支核对：协议数据流、替身API/属性面、身份/句柄、wait/exit、finally与patch恢复。若出现其他确定同链问题，记录具体不相容；仅局部替身且不改契约的必要修正可一并完成，不将普通实现细节逐次退回。需改生产控制器、扩大授权或弱化断言则停相关项交回。

## 禁止与资源
job_control.py冻结5bc35bf185de71e3ce94aa1a12e3e2a1466e6fd372e5c3f5d6aca196233980d2；offline_unit.py冻结3029a709f615ab068d65004d1083568d0a96e577417380b26109defaf0a64c5c。禁止修改二者、backend/app、迁移、PG夹具、其他测试方法/公共初始化行为、HTTP/gateway/PDF/runtime/锁、正式docu/公共库/Git。其余冻结沿stub-fix-05/final-hashes.txt及review-04证据，不全仓重采。
证据Ndocu/evidence/task-083/fixture-completion-06/；结果Ndocu/results/TASK-083-result.md置顶本轮，原历史保留。仅本卡独占focused_unit，串行无其他写入；不占服务/端口/DB。不真实事件/Job/spawn/子进程/PG/Docker/应用/网络/模型/安装/配置凭据；测试前确保全部OS边界由替身覆盖。D3不研究、不实现，旧G未知保持失败关闭。

## 一次最终验证与停止
新增且仅一次定向批，不重置旧尝试/费用/Job额度。先完成全流程文本一致性核对、有限diff和一次AST/hash（≤60秒），冻结后运行。统一项目backend/.venv/Scripts/python.exe -B，不写pyc；先存manifest的命令、ID、预期和源hash。
项目根下两条命令（首条失败不得启动第二条）：
1. backend/.venv/Scripts/python.exe -B backend/tests/fixtures/task083/focused_unit.py --failfast StartLifecycleTests.test_04_start_handle_closes_after_identity_receipt StartLifecycleTests.test_04_start_handle_release_exactly_once_on_failure
2. backend/.venv/Scripts/python.exe -B backend/tests/fixtures/task083/offline_unit.py OfflineRepairTests.test_05_early_success_uses_tree_zero_close_then_same_g_settle_retry
只这三方法，累计≤120秒、单命令≤60秒；首失败/意外真实OS调用立即停止，禁止追加修正复跑。静态脚本亦只有一次执行额度，脚本失败如实交回，不以脚本错误自动豁免尝试。先充分读代码再运行，不能用试跑探索未核对的替身行为。
预期生命周期两例确实通过真实控制函数验证成功及异常释放；05最终时钟例首次通过，t1>t0/C1/W6/树0后close与同G重试成立。日志记录实际已运行个数、failfast跳过、退出码和单一计时来源；PASS仅绑定最终快照。若失败，保留原始事实，不再新增本轮尝试。旧D1期限/碰撞方法及直接依赖不变，用有限diff证明局部证据延续，不机械全文件失效复跑。

## 回传与后续
交付三处修正前后、身份流与句柄唯一性、pre/post hash/有限diff、实际命令/耗时/退出码、复用/未运行/风险及文档建议。真实Job与PG仍冻结，D3和新D1固定入口OS证据缺口保留；不宣告M-1/STEP008完成，不填写编排最终验收。三例及差异经原084增量确认后，编排再分别安排受控真实验证；不在本卡追加运行。实际身份如实登记。保存结果并确认可读后只回一句结论和绝对路径。
