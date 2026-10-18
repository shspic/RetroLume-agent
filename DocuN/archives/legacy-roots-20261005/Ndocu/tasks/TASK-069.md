你是执行Agent，完成后交用户带回Astra。
TASK-069 / R-063；开发（G-1测试清理修正）；STEP-008；父TASK-068；关联DR-003、NFR-002。
执行者Work Buddy（GLM或KIMI K3），B档，新会话。外键清理顺序已定位，边界单文件，中档足够。
根D:/shspic/project_NO3_RetroLume-agent；需求v1.1、架构v0.21、执行状态v1.13；已有开发授权，本卡不运行PG。

目标/现状：
068生产代码已冻结待验证。test_activity_recovery.py的asyncTearDown删除material_versions前未解除本例material_sources.current_version引用，违反001的material_current_version_source立即外键；不能直接交运行卡。
本卡仅修测试资源追踪与清理，生产方法不动。

上下文：
根AGENTS.md、docu/AGENTS.MD、当前执行状态入口；
backend/tests/test_activity_recovery.py；
只读backend/migrations/001_materials.sql、002_activities.sql；
Ndocu/evidence/task-068/原始hash及差异。
原测试SHA256 c7450f088235945281c0c25bdf4a57337bd671d34ea10e3de258fb36220896e2。

范围/约束：
只写该测试文件、本卡Ndocu/evidence/task-069/及Ndocu/results/TASK-069-result.md。不改生产代码、DDL、依赖/锁、正式docu、旧证据、Git；不运行数据库、Docker、应用、模型，不安装。
清理仅本例实际创建的ID：先操作/模型许可/活动来源关联/活动，再将本例source.current_version置NULL，然后版本，再来源。WHERE必须限制本例ID，不能全表UPDATE/DELETE，不删除他人数据。
test04创建第二活动在try/finally之前存在失败窗口：建立本例创建ID登记及统一收尾，或等价局部方式，保证创建中途失败也能清理本例第二活动；不得扩大为通用测试框架。重复清理无害，错误如实报告不吞掉。
不变更5组业务断言、generation规则、DSN仅专用变量及无DSN skip规则；不把清理成功当产品验证。

验收/验证：
保存原副本及新旧hash；给出每条外键的删除顺序及第二活动创建失败路径说明。
仅一次现有项目backend/.venv/Scripts/python.exe读取源码compile语法检查，不写pyc，最多60秒；无需重做3.13检查，不运行unittest/PG。若项目解释器不可用明确记录，不安装。
静态验证不证明真实清理通过，后续运行卡负责。达到范围即停，两次有据修正仍失败交回。

协作：
可与TASK070并行，070不读本卡变动测试。独占本测试文件，禁止改生产对象。生产hash冻结不受影响。
返回TASK/R、建议状态、文件差异/清理顺序、真实命令及证据、hash、未运行/风险、文档建议和下一步；保存结果并回复完整可复制块，不填Astra验收。
