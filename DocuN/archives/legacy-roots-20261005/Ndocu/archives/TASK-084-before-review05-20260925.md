# TASK-084 / R-078 — review-04 夹具完整流程增量诊断
接收原084独立增强审计窗口，未参与083实施，不接管编排或修复。实际客户端/模型如实登记；增强要求来自控制流程与证据裁定难度，不因已完成任务模型标签重审。STEP008，父083，关联082、NFR002/003、SEC002。根D:/shspic/project_NO3_RetroLume-agent；需求v1.1、架构v0.38、执行状态v1.49；Git基础45951501d2741630a229762d6b2d3f4b34d7f702及全部现存差异保护。

## 唯一成果
一次审完整个新增生命周期夹具与05时钟替身的实际调用流程，裁定04控制器候选是否满足句柄合同，给出能合并实施的最小完整修正清单及精确验证范围，避免逐个入口错误试跑。083修正04/05连续停批，本轮不再给实施窗口新运行额度；本卡只读、运行额度0。
已知：04轮碰撞两例与D1期限PASS；新增生命周期两例因API绑定方法不能设argtypes失败；05轮partial修复后首例进入真实身份校验报Job/G/runTag不匹配，failfast实际只运行1例且失败，第二生命周期及offline05均not_run。不得写成实际运行2例或已证明生产生命周期失败。旧05根因仍未证，不循环追复现。D1旧用户态无界路径的review-03静态结论继续有效；Job/PG冻结，D3恢复未闭合。

## 规则与独立输入
根D:/shspic/project_NO3_RetroLume-agent/AGENTS.md；公共D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD；已读未变复用。原批准Ndocu/results/TASK-082-work-decision.md，自己的TASK-084-result.md review-03。原审计卡归档Ndocu/archives/TASK-084-before-review04-20260925.md。
先读fixture-repair-04/pre、incremental.diff、final-hashes.txt和stub-fix-05/pre、incremental.diff、final-hashes.txt，及当前三个文件/必要直接依赖，形成独立初判留证；再读两轮原始失败、manifest/meta、05轮静态三尝试日志。最后可读083结果当前两段作待评陈述，披露接触顺序，不把实现自评当证明，不读取实现聊天。
冻结当前：
- backend/tests/fixtures/task083/focused_unit.py 4a633aff536f833cdbf3a266be2d44de70b8e01105a204b68d7947995627a1ca
- backend/tests/fixtures/task083/job_control.py 5bc35bf185de71e3ce94aa1a12e3e2a1466e6fd372e5c3f5d6aca196233980d2
- backend/tests/fixtures/task083/offline_unit.py 3029a709f615ab068d65004d1083568d0a96e577417380b26109defaf0a64c5c
独立hash复核；其余直接依赖沿两轮final-hashes及自己review-03证据，未变不用展开全仓。未知漂移停对应结论。

## 连续四项，一次交回
1. 生命周期夹具完整核对：从真实verify_last_handle生成UUID/runTag、spawn参数、子回执、Job名/G、PID/creation_time、事件与句柄、等待/退出、finally逐步映射替身值。确认随机身份与固定回执不匹配是否确定根因；比较从spawn实参派生回执或局部固定uuid的最小方案，不取消任何身份校验。继续静态走到成功退出与提前异常/空回执收尾，检查partial属性面/返回/ctypes输出指针/重复等待/同句柄关系/清理记录/patch作用域是否还有可静态定位的不相容。只覆盖这条流程，不扩mock框架或产品审计。给一次能整体修好的具体清单，不只报告当前首错。
2. 04真实控制器增量：Start是否一直持有到已确认子Open并回执身份，所有异常出口是否恰一次释放、是否存在try前资源泄漏或掩盖原错、收尾是否保留原deadline及精确身份；观察Job的释放时点不可破坏最后句柄场景。确定产品式控制器缺陷与纯替身缺陷分列，不因为新测试失败直接判控制器有错，也不以意向代码签通过。
3. 05最终时钟替身静态可运行性：局部patch session.time与脚本__main__.time的作用域/恢复；实际被调monotonic与advance、清理等待是否可终止；asyncio和其他用例不能被替身全局时钟误伤。核对t1>t0/C1/W6、树0后关门及两次同G结算断言是否真连实际流程；纯测试注入不改变生产C0/C>W契约。只能给静态结论，not_run不升级。
4. 证据与下一最小批：D1期限/碰撞方法及直接依赖未变，判其旧PASS适用性，不能按全文件hash变化机械全部失效。核05轮静态三尝试与原卡一次额度，区分检查脚本缺陷、临时编辑问题及最终源码；如实记录偏差而非据此丢弃全部证据或重跑。给完整窄修正边界与三个剩余方法验证建议、停止条件；未改D1/仓储/D3结论复用。不要再追加D3来源研究、OS探针或新持久模型。本卡不解除Job/PG冻结。

## 权限、交付和停止
仅写Ndocu/evidence/task-084/review-04/有限diff/hash/初判与Ndocu/results/TASK-084-result.md置顶review-04，保留所有历史原文。源码/测试/迁移/正式docu/公共库/旧证据/Git只读；不AST/import/compile/单元/Job/spawn/PG/Docker/网络/安装/模型/配置/凭据；不运行实现者脚本。源码冻结，无并行写入，不占端口数据库。
一次完成上述范围即停，若不能判定留最少具体缺证，不自行修复或要求无穷复现。输出TASK/R/STEP、真实身份/独立性、读入hash/范围、逐项结论、确定触发及影响/最小完整修正、局部证据复用、未验证风险、建议下一卡及必要文档更新；代码/替身/真实OS/PG四类结论分清，不宣告M-1/STEP008完成、不填写编排最终验收。保存并确认可读后只回复一句结论和绝对结果路径。
