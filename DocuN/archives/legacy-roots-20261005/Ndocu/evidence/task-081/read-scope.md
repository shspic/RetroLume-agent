# TASK-081 / R-075 读取范围（只读声明）

- 日期：2026-09-24（Asia/Shanghai）；执行者：Work Buddy 新窗口（GLM-5.3，增强执行）。
- 本卡为只读设计：除本证据目录与结果文件外，未写任何源码/迁移/正式 docu/旧证据；未运行 compile/测试/PG/Docker/应用/模型/网络/安装；未读私有配置或凭据；无费用与运行预算消耗。
- 读取清单与 SHA-256 见同目录 read-hashes.txt（由 make_read_hashes.py 生成，可复算）。
- 冻结核对：repository.py=045a3cf8…2534 与卡面一致；004=8f04f57c…97cc 与卡面一致，无漂移。
- 读取定位（关键依据行号）：
  - repository.py：ActivitySpec L54-67、ActivityLease L70-77（window_seconds 第六字段）、claim_lease L297-392（折叠/W_eff/耗尽关闭）、settle_execution_window L394-478（受限幂等/C>W 拒绝）、cancel_activity L480-510（全额折叠）、_activity_allows L691-707、record_outcome 旧代次仅 UNKNOWN L890-891、_transaction 超时默认 L100-119。
  - _windows_job.py：Job 限制/挂起创建/关联/恢复 L115-153、TerminateJobObject+5000ms 等待 L156-161、未关联兜底终止 L169-172。
  - supervisor.py：parse_pdf_bytes 一次性 Job 用法 L40-85（本卡仅作机制参考，不改）。
  - gateway.py：admit→mark→出站→record 三段式 L115-162、取消 best-effort unknown L149-151、意外异常不发送 L126-135。
  - transport.py：无重试单次 POST L40-92、RequestNotSent/DeliveryUnknown 边界 L89-92。
  - 004 DDL：五列+八 CHECK、空表前置锁保护。
  - TASK-079-result.md：22 例真实 PG 已验证账本行为与运行偏差边界（未重测，按原证据引用）。
- 072/074 恢复证据未引用（本设计无直接依赖），未重审。
