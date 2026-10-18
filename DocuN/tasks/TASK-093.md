# TASK-093 / R-087 G5有限工具完整成果集中独立审计

## 目标、角色与完成标准

你是本卡独立增强审计者，不接管实现或编排。一次审查G5完整批准切片的最终差异、相关直接依赖与真实证据，回答：实现是否满足原合同；每项必要验证是否有适用证据；是否存在阻断缺陷；是否具备交编排验收条件。不得以报告声称通过代替独立判断，不重复已充分验证的未变行为。

交付D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-093-result.md及DocuN/evidence/TASK-093/中的独立发现/覆盖索引。结论分别说明代码、证据、执行控制以及整体切片；不宣告整个STEP006/008、M-1或发布通过，不填写编排最终验收。

## 项目、规则、身份与授权

根D:/shspic/project_NO3_RetroLume-agent，根入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。task_model，锁定V4.0/公共AGENTS CHG-0003。公共根D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，读取DocuS/AGENTS.MD；指纹见项目DocuN/evidence/v4-migration-20260930/rules-snapshot.json。WORK第2节task_model、第6/8/9节委派/隔离/核证由编排承担，执行者只补本职责所需，勿读取其他模式。公共库只读。

需求v1.1，架构v0.63，执行v1.85。父TASK092/R086、原设计TASK091/R085；关联STEP006/008、FLOW005、DATA007、NFR002/003、SEC002，以及原G3、G4和单机D3既有边界。用户2026-09-30批准G5合并包，2026-10-01继续编排；高风险完整成果的独立审计为既定交付门。

接收A+增强执行，全新隔离会话，未参与091方案设计或092实现/修复。优先与092实现窗口不同模型家族的合格资源，但如实记录实际身份，不把A+冒称型号。不得将本卡发回092实现窗口或继承其完整聊天。无隔离条件时报告缺口；偶然读到实现自评/共享记忆如实披露范围，不能伪称未接触。不得为找上下文主动读取客户端共享MEMORY或完整历史聊天，不自动创建子Agent。

路由原因：持久工具次数、原子正文提交、类型隔离、版本协议和停止退款跨模块耦合，需要独立增强判断。不是纯文档校对，不为减少卡数用实现者自查替代。

当前审计首次开始，审计运行0，主动投入上限180分钟；读文件/diff/hash不属产品运行。达到覆盖即可提前结束，不消耗额度空转。TASK092既有失败/投入保留，本审计不重新计算为零、不借其剩余额度启动测试。

## 独立输入与读取顺序

1. 根入口、公共AGENTS、本卡全文、锁定规则索引。
2. D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-093/approved-contract.md。这是已批准TASK091修正轮01 B1—B10/C1—C12的原样合同摘录，不含092实现自评。源hash a6dfdd231ea1cac76497c1a6c3dd77a77e7b653cac2231850d95d49128c92866；设计时标题时态保留，不拿时态推断实现现状。不要读取TASK091首轮废弃方案。必要需求只定向读DocuS/最终需求文档.MD对应目标/安全/预算条款。
3. DocuN/evidence/TASK-093/input-snapshot.json（产品21条、证据文件身份）；DocuN/evidence/TASK-092/pre/实际原件、final-diff.patch、final-product-hashes.json；最终源码和必要直接依赖。21条含未变4条，独立确认实际差异，不机械以条目数当改动数。Git旧提交不等于实施前快照，不checkout或覆盖工作树。
4. 原始证据按实际断言阅读：offline-01/02、real-01—05各自manifest/as-run/post/loaded-source、case-summary、标准输出与错误、bootstrap捕获、upgrade-summary；attempt-ledger/budget/scenario清单；runner/child_control及tool_pg_child、upgrade_child、win_chain、bootstrap、legacy_probe；continuation-01/02的冻结/pre/diff/检查原件。文件路径从索引定位，别一次无差别全文转储120个文件；先按C目标定位，再读支持关键结论的实际原件。
5. 旧D3/G3/G4证据仅在直接未变机制需要复用时定向读取Ndocu/evidence/task-084/review-09、task-090及其原始记录，选择实际存在的相关文件。旧独立报告可用作已验边界索引，不能代替本次新增差异判断；不回溯审全部历史。

禁止读DocuN/results/TASK-092-result.md、TASK-092-work-decision.md、实现者聊天和编排自评，以及本卡input-snapshot索引中的orchestration-review文件正文。索引只是身份导航，不授权读取自评。092任务卡含实现与续作裁定，不作为审计主要输入；所需原始技术合同和运行授权全部在本卡与批准摘录中给出。架构/总状态包含实现自评汇总，非必要不要读，必要时只读具体不含自评的批准边界并披露。

## 审计范围与判据

A. 008及持久次数：NULL未配置、0禁用、bool/整数范围、计数非负和上界/加法安全；成功工具准入才+1，未知/未执行不自动退款；模型次数/成本不混用；所有model/tool条件约束显式防NULL绕过、历史model字段及NULL usage兼容。旧成本约束唯一识别、同事务回滚、重复拒绝、空/非空基线及schema/search_path隔离。001—007不改。核实迁移负例确中目标而非别的前序错误。

B. 输入和授权：调用方可变Mapping到私有规范字节再到实际execute的链；2048边界、重复键/非规范/NaN等；专用intent/permit与DB kind/name/call_id/digest/activity/G/scope/executor绑定，旧模型凭证与工具凭证不能互换。受信显式finite_calculate之外无任意工具、命令、IO、自动计划执行。检查scope/来源排序及锁后集合复核，不能把资格失效等同撤回已在途执行。

C. 状态与原子性：admit/mark/execute/record各提交前后响应丢失的持久事实；同键并发至多资格而非保证恰一次；成功正文与received原子、失败无伪正文、unknown终态纪律和受限幂等；model共享record核心真实影响；原时间计费、close与sameG/W/C确认重试不被工具路径绕过。必要并发证据看实际屏障和执行计数，不能以sleep或模拟返回代替PG事务。

D. 消费隔离与服务：read/list的权威kind与工具语义/hash、失效范围抑制、list尺寸预算；service早拒tool父，仓储锁内再次拒，即使调用者构造正确引用且allowed_tools空；合法model父对照。service不持租约直算/settle，取消与阻塞线程清理有界，同键恢复只读不重新运算。正文有效性、业务提交成功和时间结算成功分开判定。

E. 固定受控链与协议：新增one_tool仍经固定launcher/SUP/worker、命名Job身份与旧树恢复；门覆盖admit至record，真实Job硬停/树零/私有句柄/close/settle顺序成立；截止使用实际预扣并失败关闭。外2内3严格兼容与工具外3内4精确字段，无弱化解析或泄漏secret/正文；旧端拒新协议的时间预扣事实如实。禁止重审未变windows_job/gate等全部实现，但必须看新调用路径是否破坏原前提。

F. 原始证据完整性：逐项建立C1—C12子断言→测试方法/场景→真实输出→加载hash→环境与局限的映射；不要将单方法PASS外推整类全覆盖，也不要假定执行者宣称全部子目标成立。识别用例未真正到达目标分支、反例同源错误、缺必需断言、mock替代真实事务等。确定缺陷、覆盖缺口和非阻断观察分开；不要求全学科/全故障或合同外行为。

G. 包装与证据适用：真实工具计算、真实PG、SUP/worker加载捕获、同步阻塞替身、合成model transport、旧版本行为副本分别定界；核对包装是否保留实际身份/序列/停止控制，非仅看名字。旧版局部探针不是完整跨版本部署。当前源码与每批as-run不一致时判定影响，不用最终hash回填旧批。未变证据复用，不为通过次数少强行补测。

H. 尝试账和收尾：首批失败、runner预检失败、修正、场景清单时间异常不得删除或追认；批、子批、测试实例/唯一方法、Windows会话分开计数。约定场景冻结时间与实际文件/日志矛盾须核影响。审查有无超许可资源、清理不全、敏感字段落日志/argv/报告；控制偏差与产品缺陷分别评价，不因可解释偏差自动否定全部证据，也不因产品通过掩盖执行违规。

## 被审运行授权参照 不是本审计运行许可

092原卡总主动8小时、离线1800秒、真实累计3600秒；最初3批/3容器启动、单批至多1200秒、Windows12次、单会话总截止至多120秒。续作01仅增加real04一批/一次启动，业务300秒+清理120秒总420秒，Windows新增最多6，先修夹具后运行；续作02上限增加至累计6批/6启动，仅升级库，单批180+120总300秒，第二批仅首批有明确有据夹具修正需要时使用，Windows新增0，全过即止。所有历史累计保留，不因换卡清零；完成后许可结束。

唯一授权CID e49d3acc3c1be13d670af68bca2b082fea4faeeb9b9babe69df7f1d3941696a4，retrolume-task-088-g3-w1，镜像sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f，卷retrolume-task-088-g3-w1-data，loopback55441/1CPU/512MiB/pids128/no restart/非privileged、无host bind。合成DB仅retrolume_task092_tools、retrolume_task092_upgrade，专用角色retrolume_task092_synth，原容器内本地管理通道retrolume_task088_synth只用于本卡对象；续作02只触upgrade数据。可以确认归属后重建本卡三个task092_upgrade_happy/rollback/missing schema，禁止触旧用户库/卷。新容器/卷/镜像、安装/真实provider/付费/Git/公开接口运行均0。审计只能查看这些资源原始记录，不能现在inspect或连接。

## 写权、预算与停止

业务、测试、迁移、旧证据、Git、公共库、DocuS、其他卡/结果、审批配置全部只读。仅写D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-093-result.md及DocuN/evidence/TASK-093/新审计文件，不覆盖编排approved-contract.md/input-snapshot.json。不修业务或092夹具，不把建议直接实施。

允许有限只读hash、文本搜索、diff和不执行被审代码的结构核对；不import产品、不compile/unittest/应用/PG/Windows/Job/Docker/EXPLAIN/模型，不联网或读取私有配置/凭据。运行预算0。无需先重跑才能读取已有原始证据；确有无法从原件裁定的动态缺口，明确具体最小补证对象交回，不擅自运行或标通过。

审计批期产品及证据冻结，没有并行写者。真实漂移先核具体文件/新旧hash及影响，停止受影响结论，完成独立不受影响部分，不对旧快照签当前通过。最多180分钟，覆盖充分即停；到限保留已覆盖与未覆盖，不假称完成。不接管共享编号、状态或编排。

## 交付与回传

结果先写限定结论（通过/不通过/无法判断；必要条件须具体且不替代Must），再写审计身份/隔离及意外接触披露、快照、实际差异范围、A—H与C1—C12覆盖索引、确定问题严重度/触发/影响/精确定位/最小修复与最小复验范围、证据不足及非阻断观察、预算/执行控制/收尾事实、未验证和建议下一步。

无阻断时明确可交编排验收的具体G5边界，不自行签项目最终通过。有多个问题一次合并完整回传，不逐个开修复卡，不顺手改实现。后续修复由编排沿唯一实现路线处理，增量复核仅问题及实际影响，未变结论可复用。

保存结果并核可读后回复一句结论与可点击完整绝对路径，供用户带回主控。必要用户操作当前仅转交本卡到合格隔离A+新窗口；不要求用户操作数据库或发送凭据。正式文档建议列路径/章节，由编排串行维护。