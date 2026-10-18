# TASK-084 / R-078 — review-05 三处替身修正最终增量确认
接收原084独立增强审计窗口；未参与083修改，沿独立上下文，不接管实现或编排。STEP008，父083、关联082/NFR002/003/SEC002。根D:/shspic/project_NO3_RetroLume-agent；需求v1.1、架构v0.38、执行状态v1.51；Git基础45951501d2741630a229762d6b2d3f4b34d7f702。实际身份如实登记，不因模型标签重审有效工作。

## 成果与输入
只确认review-04三处既有缺陷已按最终diff关闭、三例通过适用性以及下一真实验证的具体剩余门；不是全面审计、不是再次研究夹具设计。
根D:/shspic/project_NO3_RetroLume-agent/AGENTS.md；公共D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD，已读未变复用。原批准Ndocu/results/TASK-082-work-decision.md、自己的review-04结论及证据有效。先读fixture-completion-06/pre/、incremental.diff、final-hashes.txt、focused_unit当前StartLifecycleTests及必要调用位置，形成独立差异判断；再读manifest-final.txt、unit-lifecycle-06.log/meta、offline-05-06.log/meta及static-check.txt；最后可读083结果当前段作待评陈述，披露接触范围，不继承实现聊天。
冻结：focused_unit.py= dfaaf814bb6abeea0a7f82d8499b1e03915c87bad50aa4a50295fcfde3995259；其pre=4a633aff536f833cdbf3a266be2d44de70b8e01105a204b68d7947995627a1ca，均位于backend/tests/fixtures/task083/。同目录job_control.py=5bc35bf185de71e3ce94aa1a12e3e2a1466e6fd372e5c3f5d6aca196233980d2，offline_unit.py=3029a709f615ab068d65004d1083568d0a96e577417380b26109defaf0a64c5c。独立hash复核，未变依赖沿review-04/本轮final-hashes，不全仓重采；未知漂移停对应结论。

## 三项一次交回
1. 三缺陷闭合：身份从真实spawn实参派生、回执/断言同源且字段类型匹配；失败分支不靠错误元组产生恒真；两Kernel句柄空间分离且原关闭次数/时序断言保留。没有patch uuid4或削弱控制器身份校验，改动只在StartLifecycleTests区段。review-04已核过的控制器与05静态流程不重审；只查新差异造成的实际传导。
2. 证据确认：两生命周期与05各实际运行、日志/meta退出0、最终源码与运行快照适用。05导入session/offline hash绑定和C1/W6断言适用；两例为真实控制函数+OS替身，不是Windows实测。旧D1期限/碰撞等方法及直接依赖未变，沿review-04局部不变性延续。旧05原始失败原因仍未唯一证实，不为此要求循环复现。静态本轮再次使用托管3.13.12而非卡定项目venv，记录偏差和证据适用范围，不把纯AST偏差自动变成重跑产品测试门槛；项目venv已执行的三例不因此失效。
3. 更新运行门结论，限增量：夹具问题若均关闭，说清现有Job01—05的准备是否仍有确定阻断；分别列已有Job场景、未准备的新D1固定launcher入口、PG六例、D3旧G恢复的前置，不把D3泛化为干净新活动/独立PG的永久前置。沿原精确清单，不新造压力/时钟/全仓回归。不要求本卡补新入口、查新API、运行或承诺真实通过；新D1入口须有独立外层精确身份/期限/未知停批，正常结算若需PG保持单独准备。下一步优先给可执行的最小路由，避免笼统“继续补证”。

## 权限与停止
仅写Ndocu/evidence/task-084/review-05/有限hash/diff/初判及Ndocu/results/TASK-084-result.md置顶review-05，历史保留。源码/测试/迁移/正式docu/公共库/旧证据/Git只读；不AST/import/compile/测试/Job/spawn/PG/Docker/网络/模型/安装/真实配置，不运行实现脚本。源码冻结、无并行写入，不占端口/DB；本卡运行额度0，Job/PG仍冻结，不能自行解冻。
一次覆盖即停，不重新审D1完整结构/仓储/恢复方案。输出TASK/R/STEP、实际身份/独立性、hash与范围、三缺陷关闭或具体未闭合、日志适用性、运行门分项、必要下一卡和文档建议。不签真实OS/PG通过或M-1/STEP008最终验收。保存可读后只回一句结论和绝对路径。
