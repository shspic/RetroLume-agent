# TASK-083 / R-077 — 定向夹具修正04（review-03后）
接收原083增强实施窗口；继续原任务，不承担独立审计。STEP008，父082，关联084/R078、NFR002/003、SEC002。目标是交付可独立复核的三处夹具修正及一次最终离线证据。根D:/shspic/project_NO3_RetroLume-agent；需求v1.1、架构v0.38、执行状态v1.47；Git基础45951501d2741630a229762d6b2d3f4b34d7f702，保护既有全部差异。授权沿用户批准082内部切片，本轮仅在既有范围修夹具；不新增持久模型。

## 入口与最小输入
根D:/shspic/project_NO3_RetroLume-agent/AGENTS.md；公共D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD。同窗口未变已读复用。
读Ndocu/results/TASK-084-result.md当前review-03（至历史分隔线）、review-03/hashes.txt、Ndocu/results/TASK-082-work-decision.md批准边界、focused-repair-03最终源码/失败日志及05诊断；当前卡替代上一轮运行额度，历史卡存Ndocu/archives/TASK-083-before-fixture-repair04-20260924.md。不重读整个历史报告。
冻结以review-03/hashes.txt为准，重点三个改动对象：
- backend/tests/fixtures/task083/job_control.py F76F0A4E598A5B9ACB8524697FBC0A4F5C1F95D52D16526D20B6FAF3463DCB95
- backend/tests/fixtures/task083/focused_unit.py 0887ADEE55BFFBCB7DBEBC1FDD3A5514620711DDFB4DD12FAF1B6529A8CFF6D4
- backend/tests/fixtures/task083/offline_unit.py 3E79CE9715BB3F66AA5F91E37A8432FBF75E519797111F33CA65F15B1795CB04
不符先查差异、停受影响项；改前真实字节副本与hash必须齐备，不能对空假作新增。

## 三项连续完成
1. 04 Start生命周期：保留父Start句柄，直到子已Open并发回可验证悬停身份回执；不在SetEvent后立刻关掉唯一父句柄。失败出口归入有限精确收尾，不漏句柄、不重复关闭、不触发碰撞对象。不能延长原总deadline，不能为此使观察Job句柄跨越最后句柄死亡测试。检查提前异常与身份回执失败两分支。纯替身证明真实控制流程中关闭在回执之后、失败时最终释放，不以手写事件序列代替调用实际函数。
2. D1期限用例：第三次运行窗检查返回0（前两次仍有余额），后续清理保有合理预算；保留manager_startup_deadline_unconfirmed，断言create_suspended→identity后无Resume、精确SUP terminate/退出确认、账字段未知、不读结果、不claim。不得改生产launcher来迁就夹具，不能只改期望状态文字。
3. 05确定正耗时：仅在该纯替身用例局部注入明确单调时序，或有界可证明推进；推荐测试局部可控时钟，patch须在结束恢复，避免影响asyncio/其他测试全局时钟。t1>t0，ceil差值=1，W=6；断言先树0再关门与同G结算/重试。生产C0拒退及C>W拒绝不变。旧失败原因仍未唯一确定，如实保留；修正消除测试对2ms睡眠跨时钟刻度的依赖，不宣称重现并解释旧失败。诊断中间源码字节未保留，不能用其PASS签最终快照。

## 文件与资源
只修改上述三文件；若生命周期测试确需新小辅助测试，可新增于backend/tests/fixtures/task083/，必须调用真实控制流程并完全替身化OS接口。不改backend/app任何产品代码、fixture.py/scenario_child.py生产式控制入口、仓储/001—005、PG夹具、HTTP/gateway/PDF/runtime、锁/依赖、正式docu/公共库/Git。若三项确需越界，完成不受阻项后带具体差异交回，不自行扩大。
写证据Ndocu/evidence/task-083/fixture-repair-04/；结果Ndocu/results/TASK-083-result.md置顶并保留历史。本卡独占三文件；无并行测试/源码修改。不占端口、DB、服务；禁止真实事件/Job/spawn/子进程/PG/Docker/应用/网络/模型/安装/私有配置读取。D3本轮不再调查、不新增字段或服务；旧G未知继续失败关闭，不为了通关放行恢复。

## 最小验证与明确新增额度
这是针对已定位缺陷的新小批，不重置旧失败/费用/Job额度。先完成三项改动、差异检查和最终AST/hash（不import、不写pyc），然后冻结再运行。仅项目backend/.venv/Scripts/python.exe -B；明确列manifest精确ID、预期、hash和选用命令后执行。
一次最终定向离线批：04原碰撞两例+新增生命周期成功/异常两分支（可同一参数化用例）；D1 Resume前截止一例；05一例。合计不超过6个测试方法，累计≤120秒、每命令≤60秒。必须先确认所有真实OS启动接口被替身覆盖，否则停止不运行。首命令一旦失败停止后续命令，不追加修正复检；不得让测试默认发现把其他用例带入。记录真实退出码及单一计时来源，避免meta与分析用不同数字。
第12项不重跑：command/worker_main/gate未变且084确认既有PASS可复用；其他9项只按未受影响依赖沿用。旧05不再循环取证。若本批通过且无代码再改，结果绑定最终hash；若后补代码则对应测试not_run，不能沿用通过。静态检查≤60秒一次；必要纯文档整理不追加运行。

## 交付、停止与下一门
提供三项原→新、改前后hash/有限diff、Start句柄成功/失败释放次序、期限断言与确定时钟注入范围、精确命令/退出码/耗时/证据、复用项、未完成风险。不得宣告真实Job/PG通过、D3恢复已解决或M-1/STEP008完成。Job/PG仍冻结；新D1固定launcher真实入口尚无运行证据，现有Job01—05不能替代它。
达到三项成果即停；失败/范围扩大/预算到达带证据交回。后续由原084窗口只复核本三处差异与日志，不全量重审；再由编排分别裁定受控Job和PG窗口。D3仅阻断旧G恢复和整体交付，不把它泛化为所有干净新活动验证的永久前置。结果保存后只回复一句结论及可点击绝对路径，不填写编排最终验收。
