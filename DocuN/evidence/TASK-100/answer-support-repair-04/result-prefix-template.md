# TASK-100 / R-094 定向修复04 — F01 有限答案可靠解析（2026-10-06）

结论：F01 剩余解析遗漏已形成稳定修复候选，受影响离线验证通过，证据与最终字节已冻结；实现交付完成，待编排安排原101窗口增量复核，不自行关闭DEF-008或签G8。

## 实际修复及语法边界

产品仅修改 backend/app/learning/teaching_policy.py 中 `_answer_quantity` 及必要局部常量/辅助函数。旧整段finditer+同量纲唯一候选改为全文匹配：有单位答案必须以单个明确量值开头，逗号/分号尾段仅允许八个固定肯定说明短语或经Decimal精确验证的非负分钟→秒等式；无单位只允许单值及可选“约”。外围空白及一个句末句号可接受。整段中任何额外开放、否定、猜测、引用、问句或多值内容均未知，不用关键词黑名单、首末值选择或任意尾段兜底。

完整单位集合、数字语法、八短语、等式、句末处理和拒绝边界见 [grammar-and-applicability.md](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/answer-support-repair-04/grammar-and-applicability.md)。参考计算域、derive_support_checks、其余policy函数、teaching_progress、teaching_repository、DTO/持久模型/服务/API/工具gate/前端及dist均原字节不变。test_task100_repair只改两个指定离线方法，修正其第二实例数据与参考的一致性并增加反例；新增一个真实函数的纯离线 test_task100_answer_support.py；test_teaching_policy未改。

## F01 真实逐样本及进度结果

本轮只运行一个最终字节离线主批：18个方法、81次成功子测试回调；失败、错误、skip、expected-failure和unexpected-success均0。新增矩阵的64条实际样本原件见 [case-results.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/answer-support-repair-04/case-results.json)，逐条来自stdout，不把样本/子测试冒充方法数。

| 实际输入/组合 | 参考/实际支持及真实投影 |
| --- | --- |
| 平均速度不等于1m/s | reference matched；answer/status unchecked；两个合法不同实例为 practising，independent_answers=[]，contested/assisted=[] |
| 答案未知，可能1m/s | 同上，不伪造conflict，也不进入独立计数 |
| 否定/猜测在值前后、引用/示例/假设/问句、开放尾段、多值、科学计数及非法辅助说明（31条） | 实际答案unchecked；对应numeric check仍绑定value维度 |
| 明确1m/s、单位/空白写法、60m/min及有限说明（15条） | reference/answer/status均matched；换算后值为1 |
| 60m/s、0.01m/s、1m | reference matched，answer/status conflict；单位冲突和数值冲突仍分离 |
| 参考120/2却自报1；实际明确1或未知答案 | reference conflict，answer分别matched/unchecked，综合conflict |
| 无单位约0.5及空白（6条正反例） | 明确0.5/约0.5 matched；否定/开放/指数unchecked |
| 正常程序题+数值或含raise的用户原文（2条） | 不执行；reference matched，answer/status unchecked |
| 一个明确正确+一个未知（两个顺序） | 仅1个独立答案，practising |
| 两个明确正确、不同实例且含retest | 2个独立答案，evidence_sufficient |

两条确定反例各在真实rebuild_progress中使用合同校验成功的120米/2分钟、180米/3分钟实例；reference.left/right分别120/120、180/180，value=1m/s。练习/答案/反馈UUID不同，初题initial、复题retest且父ID合法，无曝光，模型四维度故意全met，排除了结构非法或重复实例天然阻断的伪证据。所有实际完整事实、支持检查和投影随样本保存。

对应value意见的unknown赋值来自未改的真实rebuild_progress收紧分支；该返回值不公开内部opinion，因此本轮不虚构observation或advance字段。真实函数返回值为A级本地证据；内部赋值与仓储读取/提交继续使用同一函数的调用依据为B级源码证据，见 [propagation-source.md](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/answer-support-repair-04/propagation-source.md)。本轮未执行PG提交或公开SQL读。

## 版本绑定与证据导航

- [pre-identities.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/answer-support-repair-04/pre-identities.json)：全部158条编排基线（132 current、18 protected、7 rules、1 audit_result），并核16条关键输入及4条接收上下文；有重叠，合计153个唯一绝对路径，首核全部一致。七项V4.0/CHG-0003锁定规则同窗正文复用，不采用后来版本。
- [pre-targets.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/answer-support-repair-04/pre-targets.json)及pre目录：实际写权目标的完整修改前副本/hash；新增测试原不存在。旧结果49113字节，SHA 18819a4b8851ab4bb8ecf3eb98ab524ec980bffe680e0cb7d212601a7408c0e3，新增前缀外逐字节保留。
- [batch-01/as-run-identities.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/answer-support-repair-04/batch-01/as-run-identities.json)、as-run完整副本及after-identities.json：132旧对象加1新增测试，共133个不重复当前/保护对象，实际测试前后全部一致，最终适用性再核，没有用旧局部回放冒称新字节通过。
- [batch-01/unittest-result.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/answer-support-repair-04/batch-01/unittest-result.json)、stdout.txt、stderr.txt：全部18方法及81次真实子测试、逐样本返回值、真实零skip退出0原件。
- [changes.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/answer-support-repair-04/changes.json)、diff及post目录：3个实际源码/测试文件的完整正确统一diff与最终副本/hash；未修改的test_teaching_policy也单列。结果前缀独立保存，原历史在同一文件完整保留。
- [protected-method-byte-check.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/answer-support-repair-04/protected-method-byte-check.json)、[final-identities.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/answer-support-repair-04/final-identities.json)、[delivery-check.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/answer-support-repair-04/delivery-check.json)：其余9个policy函数、26个测试函数和指定修改区域之外字节均原样；全部范围外冻结对象、规则、审计和关键原证据零漂移；最终字节与as-run一致。本轮改变只有policy、两个离线方法所在测试文件、新增纯离线测试和本结果的新增前缀。

最终源码身份：

| 对象 | SHA-256 |
| --- | --- |
| teaching_policy.py | @@POLICY_SHA@@ |
| test_task100_repair.py | @@REPAIR_SHA@@ |
| test_task100_answer_support.py | @@NEW_TEST_SHA@@ |
| teaching_progress.py（未变） | edb9d4ac91711d8be82443b3ba8a38f114bfb3df885faedc1ea8c2aa0fb68bb6 |
| teaching_repository.py（未变） | 7d9e28575780e4ac3665f3197b022ff1a3a5c27fc49877067de8f55aef4fe127 |

hash只证明身份，反例判定依据真实断言和返回值。没有重复2618旧原件全hash，旧证据身份与适用性沿已核101 review-02原件和索引继承。

## 实际命令、计量及失败账

许可 TASK-100-F01-repair-04-20261005，不因跨日、换卡或接续清零旧账。实际客户端Codex desktop，系统标识GPT-6，具体部署型号未暴露，执行标签A+；没有子Agent或并行实现/审计。

实际cwd D:/shspic/project_NO3_RetroLume-agent/backend，既有 .venv/Scripts/python.exe，`-B`。通过标准unittest加载下列四个目标；小型结果观察器只记录实际startTest/addSubTest回调，没有mock产品函数、Decimal、解析结果或数据库。真实argv、观察器完整正文、开始/结束墙钟及单调时点、Python版本及可执行文件hash、退出码见 [batch-01/execution.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/answer-support-repair-04/batch-01/execution.json)、unittest-invocation.txt和python-identity.json。

```text
tests.test_teaching_policy
tests.test_task100_answer_support
tests.test_task100_repair.RepairOfflineTests.test_answer_value_unit_and_ambiguous_input_are_separate_from_reference
tests.test_task100_repair.RepairOfflineTests.test_misleading_model_met_cannot_advance_numeric_conflict_or_unknown
```

主批动作前登记，使用1/3批，未复检；内部55秒超时控制，实际含壳和工具等待1.6463436秒（内层单调1.297秒），离线计入完整1.6463436/600秒，整批低于60秒。没有单独compile或机械重跑原76项。

主动计时起于2026-10-05T23:49:09.571051+08，单调基点486821.281；首读至固定计时的逐段开销未知，保守额外计180秒；全部读取、修复、取证与封装连续计入。最终交付主动计费上界 @@ACTIVE_CHARGE@@ /3600秒，含已测到最终封装的 @@ACTIVE_MEASURED@@ 秒、首读180秒及最终记录/回传未逐段测量的15秒保守额度。最终冻结时点、实测与保守部分分列在 [session-accounting.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-100/answer-support-repair-04/session-accounting.json)，未将未知开销填0。

测试失败/超时/业务修正次数均0。一次只读检索包含不存在的历史候选文件windows_cases.py，退出1，其他有效源已返回；随后以实际repair_windows/repair_cases/seed_helpers/IntegrationPG源码完成文字映射，未改产品或增加测试批。该元数据读取错误单列，未冒称业务失败或略去。没有其他本轮偏差。

新增真实入口、PG/HTTP服务器或连接、Docker/inspect/start、应用/SUP/Job、browser/driver、frontend-build、真实模型/工具/付费、联网安装/Git写入均0。原库、卷、数据和私有配置未读写；历史2026-10-05T19:43:39+08停止观察仅作为历史，不假称本轮查询了资源当前状态。

旧100修复03保留entry4/4、container-start4/4、app3/3、SUP12/18、browser2/3、driver2/3、build2/2；离线78.735、真实199.422、清理26.906、主动10059.821秒。B1/B2/B3总批FAIL、B4只读专项PASS原样保留。续02/续01/初轮原入口、漏计5.940、未知开销和失败全留在下方旧49113字节中，不借名义余额；101 review-02资源0、主动6778.853/10800及元数据3.725/600秒、未逐段开销未知及已结束许可不转借。

## 继承、限制及待同步

卡内指定已验正常文字，包括两个真实Windows时间等式、repair_cases两题、原PG有限辅助说明、60m/min与约0.5，本轮已逐字用实际函数验证。F02—F09/E02/E01、DEF-005有限公开读面及原未变身份/事务/停止/正文/界面性质继续沿101有限结论，不因本修复撤销。

部分旧开放表达不再支持当前有限核定，具体为 `120÷2=60m/s`、`新答案：1m/s`、`并发同一修正版 1m/s`、多量值计算推导。映射为unknown是全文语法的B级源码判断，未另增测试批或重签这些旧PG总体PASS；存储/准入/并发事实不受影响。完整文字及直接依赖性质见grammar-and-applicability.md。

原FAIL、旧25中间原件不可恢复、完整丢投影重建未动态验证、007完整payload未独立导出、额外一个正常输出无新HTTP引用证明、合成只读浏览器不证明新的认证/写入、真实provider质量和其他分层限制继续保留。本轮A级仅证明纯函数的本地结果，B级仅证明源码传播；没有新的PG/HTTP/Windows、V19、长期记忆、删除、部署或发布签字。

剩余工作由编排维护DEF/共享总状态/CHG并另更新原TASK-101/R-095合同，仅核F01差异、实际离线原件和未变调用传播；本实现者没有签其独立结论或修改101/DocuS/公共规则/归档。没有必要提供密钥、启动容器或追加资源批准。唯一人工事项是带回本结果路径，供编排安排增量复核。可复用经验候选：有限数值识别必须匹配整个肯定答案，unknown与conflict分离；验证须同时保留合法不同实例、模型全met的反例和两次明确正确的正例，不用无效数据天然阻断。未占共享经验编号或写公共库。

## 以下为本轮接收时原49113字节历史（逐字节保留）

