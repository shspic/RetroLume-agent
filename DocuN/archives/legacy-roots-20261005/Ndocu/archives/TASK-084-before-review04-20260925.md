# TASK-084 / R-078 — review-03 定向独立复核
接收原084独立增强审计窗口，未参与083实施；不回实现窗口，不接管编排。类型：只读增量审计；STEP008，父083，关联082、NFR002/003、SEC002。实际客户端/模型如实登记，不因名称变化重审有效证据。根D:/shspic/project_NO3_RetroLume-agent；需求v1.1、架构v0.38、执行状态v1.46。Git基础45951501d2741630a229762d6b2d3f4b34d7f702，保护全部未提交改动。

## 完整成果与前置
一次完成focused-repair-03增量审查，给出D1/04及两项失败的确定结论、D3最窄剩余事实和唯一下一执行路径。083已按最终失败停批：05诊断一次PASS但旧失败未解释；最终10项9过1失败，后续第12项not_run。Job/PG本轮0，005未执行。原运行预算不恢复；本卡运行额度0。未变D2/D5/D6及D7条件结论复用；D8受新D1影响的传导需查。

## 规则、独立输入与快照
根入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md；公共D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD。已读未变内容复用。原合同Ndocu/results/TASK-082-work-decision.md、Ndocu/tasks/TASK-083.md及自己的TASK-084-result.md review-02有效；旧审计卡已存Ndocu/archives/TASK-084-before-review03-20260924.md。
先读原发现、focused-repair-03/pre/真实副本、pre-hashes.txt、incremental.diff、final-hashes.txt及七份当前源码，形成独立初判留证；再对照05-diagnostic.log/meta、unit-final-01.log、unit-stop-analysis.md、manifest-final.txt/manifest-source-hashes.txt及static-final.log。最后可读official-facts.md作为待评证据、083结果当前段作为待评陈述，披露接触顺序；不把实现自评当证明。不加载实现聊天。
独立重算final-hashes.txt所列七文件及repository/005冻结值，未知漂移停对应结论。源码七文件：launcher.py、supervisor_ipc.py、supervisor_main.py、session.py（均backend/app/worker/下）；job_control.py、offline_unit.py、focused_unit.py（均backend/tests/fixtures/task083/下）。未变直接依赖按需读，不全仓重审。session diff有大量空行，按实质变化核对，不把格式噪声当协议重写。

## 连续审查四项
1. D1新结构：固定base解释器/固定模块、悬停创建→精确身份→截止检查→Resume→确切SUP退出后读结果；16KiB映射帧的创建碰撞、长度/完整性/身份验证、默认访问及句柄继承、异常清理与敏感DSN泄漏风险；父子单调deadline传递是否真正约束子端session，启动/等待/终止是否同总期限。父在Resume前死亡无迟到创建与悬停遗留的区别必须明示；父在Resume后失败/终止SUP时Job及退款的安全性须有源码依据。不要以进程退出等同工作树空。限既定受信本地有限故障模型，不以任意内核永久阻塞或同权限恶意代码要求无限监督层。
2. 最终失败：静态核focused_unit的剩余时间序列及launcher检查点，确认是否纯夹具错排，还是实现遗漏。若确属夹具，给最小修正和唯一需验证断言，不能只改期望字符串而不证明Resume前截止确实不Resume。05核本轮是否仅增加观测、是否改变monotonic/sleep来源或场景；日志固定数值不能凭观感判伪，须追代码/原副本。区分本次PASS、旧失败根因、最终session变更各自适用范围；不能以未复现证明旧故障消失，也不要求无限复现。确定旧测试环境原因若可静态证实，给证据，否则列最少欠缺事实。
3. 04碰撞：Start/Arm同链新建/已有183/失败时拒绝、只关闭本次句柄、不触发外来事件。结合已存在控制链确定实际可运行性，不重做无关场景。D8未知账字段/cleanup_incomplete在新路径是否保守；未变PG静态隔离条件沿用，不声称动态通过。
4. D3事实与最小出口：评估official-facts本轮六页摘要能否支撑命名空间/启动与会话化身结论，明确“来源尚未找到”不等于“机制不存在”。本卡不再查新网页/运行探针。两列尚不充分则不能推荐批准迁移；给决定性缺口及当前失败关闭的功能影响。不要重新引入未证必要的独立长期服务/逐阶段见证表。区分代码安全、恢复可用性和后续运行门；若D3只阻塞恢复场景，说明其他已隔离场景是否可独立验证及所需前提，由编排裁定，不能自行解除冻结。

## 交付、权限与停止
完成四项后统一交回：增量状态/确定缺陷与最小修正/两失败根因或证据限度/D3决定/下一最小纯单元及Job、PG矩阵。每项标明现有标识、前置门、证据复用，区分代码通过与运行门；不机械重跑079或全套。真正需要模型/架构扩展须给具体差异与必要性，不能只请用户接受泛化风险。
仅写Ndocu/evidence/task-084/review-03/及Ndocu/results/TASK-084-result.md置顶本轮并保留全部历史。源码/测试/迁移/正式docu/公共库/Git只读。本批源码冻结、无并行写入，不占端口/DB；不import/AST/compile/unittest/Job/spawn/PG/Docker/联网/模型/安装/真实配置，不运行诊断脚本。允许只读diff/hash。达到覆盖即停；不能闭合则带最少决定性证据交回，不自行修复或新增测试预算。
完整报告写TASK/R/STEP、实际身份和独立性、读入快照、事实定位与触发影响、命令/证据、未验证风险、文档建议、仅必要人工操作及下一步。不填编排最终验收，不宣告M-1/STEP008完成。确认保存可读后仅回一句结论及结果绝对路径。
