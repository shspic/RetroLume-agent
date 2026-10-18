# TASK-083 / R-077 — 夹具替身修正05与剩余三例验证
接收原083增强实现窗口，继续原任务；不承担独立审计。STEP008，父082、关联084/R078、NFR002/003、SEC002。项目根D:/shspic/project_NO3_RetroLume-agent；需求v1.1、架构v0.38、执行状态v1.48；Git基础45951501d2741630a229762d6b2d3f4b34d7f702，保护所有已有差异。授权沿用户批准082内部切片，本卡仅修既有纯测试替身，不扩产品范围。

## 输入与成果
根入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md，公共D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD；同窗口已读未变复用。原合同Ndocu/results/TASK-082-work-decision.md；TASK-084-result.md review-03、fixture-repair-04/pre与incremental.diff/final-hashes.txt/unit-final-01.log/manifest-final.txt；上一卡完整存Ndocu/archives/TASK-083-before-stub-fix05-20260924.md。
唯一完整成果：修正StartLifecycleTests的API替身属性兼容性，完成两项生命周期测试及尚未运行的05，形成可交084独立复核的最终快照。D1本轮已PASS；碰撞两例PASS。两失败共同为绑定方法不能设argtypes/restype，不能据此宣布job_control生命周期正确或错误。

## 冻结及允许修改
仅backend/tests/fixtures/task083/focused_unit.py允许修改：当前SHA256=1e58eb039eb54e0400a8a730b649fb7e450bb558bb983d27e1db1a24c2a8ce08。只改StartLifecycleTests局部Kernel API替身及必须的标准库导入；API可用支持属性赋值的可调用包装/partial，保留原参数、返回值、指针输出、事件记录及故障注入语义。先静态逐项核对实际verify_last_handle对替身API的调用与属性设置，补齐同一确定兼容缺陷，不能只遮蔽AttributeError或跳过生命周期断言。不改LauncherTests/EventControlTests及其依赖，不改其他用例期望；不新增通用mock框架。
不动job_control.py（5bc35bf185de71e3ce94aa1a12e3e2a1466e6fd372e5c3f5d6aca196233980d2）、offline_unit.py（3029a709f615ab068d65004d1083568d0a96e577417380b26109defaf0a64c5c），更不改任何backend/app产品代码、迁移、PG夹具、fixture/scenario、正式docu/公共库/Git。其他冻结沿fixture-repair-04/final-hashes.txt。未知漂移先查明并停受影响项，不覆盖。
先存focused_unit真实pre字节/hash；证据写Ndocu/evidence/task-083/stub-fix-05/，结果写Ndocu/results/TASK-083-result.md置顶保留各轮历史。本卡独占该文件，无并行源码/测试写入。禁止真实事件/Job/进程启动/PG/Docker/网络/安装/模型/应用/私有配置；OS接口完全替身化后才可执行纯测试。

## 验证与本轮有限新增额度
原04批已用且失败停批合规保留，本卡明确新增一次定向批，非重置旧预算。先完成修改、静态差异/API兼容核对及一次AST/hash（≤60秒，不import、不写pyc），冻结后执行以下精确三方法，各命令≤60秒，总≤120秒：
1. focused_unit.py StartLifecycleTests.test_04_start_handle_closes_after_identity_receipt
2. focused_unit.py StartLifecycleTests.test_04_start_handle_release_exactly_once_on_failure
3. offline_unit.py OfflineRepairTests.test_05_early_success_uses_tree_zero_close_then_same_g_settle_retry
统一用backend/.venv/Scripts/python.exe -B，工作目录和完整参数写manifest。首两例可同一命令，但启用failfast；任何失败/意外真实OS调用即停所有后续命令，不再修正复跑。三例之后无额外测试。若05本身失败，也只留证交回，不授权在本卡改offline_unit。
04成功须进入真实verify_last_handle流程，验证身份回执先于Start关闭及恰一次释放；异常/空回执分支保留原异常并有限收尾，不能用替身预排字符串冒充流程调用。05须实际执行最终确定时钟用例，证明t1>t0、ceil=1/W6、树0后关门及同G结算重试；生产C0/C>W约束不变，旧失败原因仍未唯一确定。
三项旧PASS（碰撞两项、D1期限一项）不重跑：只要本轮有限diff证其测试方法、直接依赖及全局初始化行为均未受影响，保留旧hash和日志，明确按局部不变性延续证据。文件hash变化本身不等于所有方法失效。若实际修正触及这些共享依赖，则停止并指出具体影响，不擅自扩大复跑。第12项及其他未变证据沿084口径复用。
静态如再次用托管解释器代替项目venv，必须先说明不可用事实及契约偏差，本卡默认使用指定项目解释器；不为纠正上一轮静态解释器偏差重跑旧AST。

## 交回及停止
记录实际身份、前后hash/diff、替身修正作用、三例命令/单一来源耗时/退出码、未运行项及PASS适用范围。上一轮静态用托管3.13.12而非卡定venv的偏差如实保留，不冒称完全按原命令执行。已完成即停；本批再失败直接交原084独立窗口审视夹具与具体失败，不开启无限修正批。
完成后由原084窗口一次复核04轮至本轮累积三文件增量和有效日志，不全面重审D1/仓储。真实Job/PG仍冻结；D3恢复未闭合、新D1固定入口OS证据缺口保留。不得宣告M-1/STEP008完成，不填写编排最终验收。保存结果可读后仅回复一句结论及可点击绝对路径。
