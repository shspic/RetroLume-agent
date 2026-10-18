# TASK-055 Windows运行循环兼容与账本剩余验证
任务开发/定向验证；STEP-008；R-049；父TASK-051；NFR-002/003、SEC-002、MOD-003/007/008、FLOW-005。内部Sol强档：异步驱动兼容、事务并发证据需要强推理；不是独立审计。
根D:/shspic/project_NO3_RetroLume-agent；有效需求v1.1、架构v0.15。用户07/08本地授权，无新增费用。
目标：修正已确诊Windows Proactor与psycopg异步不兼容，补七类未执行账本反例；保留051合法路径证据，不重写账本。此前失败依次为测试发现、循环及清理外键；Astra重新规划明确两处根因，不是原样第三次试错。
上下文：根AGENTS、docu/AGENTS.MD、TASK-051卡/结果、evidence/task-051原始日志；activities及002、tests/run_ledger_check.py、backend/tests/test_activity_ledger.py；deploy/start_local.py、start-backend.ps1；当前安装uvicorn/config.py get_loop_factory支持自定义module:factory，Windows默认Proactor。
范围：新增backend/app/runtime.py显式loop factory；修改两份deploy启动器接入自定义factory；既有账本测试及runner仅调整指定用例选择/使用正式factory，结果与自身证据。activities/002只读，发现业务缺陷停回Astra；不动main、materials、PDF、前端、锁、真实配置或docu。不换依赖、不使用全局策略冒充正式启动接线；Linux保持兼容默认loop。必要核对CLI是否接受自定义factory再实现；若不接受，提交具体可兼容最小入口调整。
协作：052独占PDF/main/前端；本卡不读其变动实现运行。只用051已保留专用retrolume-task-048-pg，精确ID/镜像/端口/限制继承051，先inspect验证，不重建；127.0.0.1:55433、CPU1/512MiB/PID128/restart=no/no host mount，镜像sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f。仅合成库，不读用户库凭据。结束停止保留并确认。
验收：两正式启动器调用同一个psycopg兼容loop；用实际Uvicorn配置选择该factory，在其生成循环中运行真实PG异步连接/账本；七类反例独立成功，无自动重试/退款/越权。明确Selector无async subprocess支持，现有同步受监督子进程不改变，后续worker需遵循该边界。
验证子项强档：先只读确认清理current_version置空顺序已修；一个loop选择检查+仅剩七类真实PG测试，总10分钟，最多一次主运行及一次有明确夹具修正后的受影响重跑；业务异常即停。不得为了计数重跑051合法路径，不启动真实应用用户库或模型。原始命令/退出码/时间/版本/最终hash/日志/容器停止状态统一存Ndocu/evidence/task-055。现有独立审计仍待最终候选证据，不能以本卡自查替代。
停止：超时、范围变化、身份不符、业务失败或一次修正仍失败交回，保留证据，不删容器/数据，不提交git。
返回Ndocu/results/TASK-055-result.md：实际变更、运行与未运行、风险、启动兼容边界、关联ID、文档建议及下一步。只建议结果不写Work结论。
