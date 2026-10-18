你是本卡执行 Agent，完成后交用户带回 Astra，不接管编排。
任务：TASK-062 / R-056；类型：开发；STEP-006；父TASK-060，关联058/046、SEC-002、NFR-003、MOD-007、API-006。
执行者：Work Buddy（GLM或KIMI K3），B档，新会话；记录实际模型标签。两个局部契约/诊断缺陷，边界明确，可用离线替身验证，中档足够；不承担安全审计。
根目录：D:/shspic/project_NO3_RetroLume-agent。
基线：需求文档v1.1、架构v0.18、执行状态v1.5；原范围开发已授权，无真实模型调用授权。

目标与现状：
完成受控模型入口的ID契约一致性与准入异常可诊断性（058/L-1、L-3）。CallContext目前只限长度，真实账本要求activity_id可解析为UUID，operation_id/executor_id匹配^[A-Za-z0-9._:/-]+$。gateway把预期AdmissionUnavailable与意外异常统一折叠，缺诊断线索。保持失败关闭和不发送。
L-2请求体字节差异已否定，不改transport/序列化/预留。M-1时钟问题未解决，本卡不碰；不声称完成STEP-006或真实供应商兼容。

上下文：
先读根AGENTS.md、docu/AGENTS.MD、Ndocu/TASK_TEMPLATE.md和当前执行状态入口。
按需读docu/LATER_REQUIREMENTS.MD的SEC-002/NFR-003、架构MOD-007/API-006/FLOW-005；读取capabilities/contracts.py、gateway.py、transport.py、backend/tests/test_capabilities.py。
只读activities/repository.py中ID校验，Ndocu/results/TASK-060-result.md的F-1/F-3及L-3相关058发现；既有046证据只作未变化部分参考。不加载全历史，不读061变动脚本。

允许写：
backend/app/capabilities/contracts.py、gateway.py、backend/tests/test_capabilities.py；
Ndocu/evidence/task-062/、Ndocu/results/TASK-062-result.md。
禁止账本/迁移/应用接线/worker/transport/依赖锁/正式docu/真实配置/Git；不安装、不运行Docker/浏览器/应用、不联网、不调用供应商。

实现约束：
1. 保持CallContext三个ID字段的字符串外部类型和现有长度限制。activity_id验证与仓储UUID可解析语义一致；operation/executor使用仓储相同字符集。无效输入在契约校验时明确拒绝，不自动改名或静默规范化标识。相应旧替身activity-1样本换成固定合成UUID，仅改本测试文件。
2. 明确区分AdmissionDenied、AdmissionUnavailable和真正意外异常。保留前两类既有错误码；意外异常返回稳定独立码，例如admission_internal_error，仍REJECTED且不发送。
3. 意外异常记录最少脱敏诊断：稳定事件码、随机关联标识、阶段（admit/permit_check/mark_dispatch）及异常类型即可。不得记录异常消息/traceback局部变量、密钥、请求正文、资料或完整ID；不用logger.exception直接输出可能含秘密的异常文本。不新增公共结果字段；用现有error_code与本地日志定位。
4. 已预留但mark失败保持现有保守账本语义，不退款、不重发、不假记业务成功；不顺手处理其他异常路径，不改费用口径。

协作：独占上述三个产品/测试文件；与TASK-061可并行，无共享端口/服务/数据或写入。发现其他人正在修改同一文件先停止冲突部分并回报。

交付与验收：
有效UUID和合法operation/executor保持通过；非法UUID、空白/中文ID明确拒绝。预期准入不可用保留原码；意外admit/mark异常可区分且transport发送次数为0。日志能区分阶段，带合成秘密的异常文本不泄漏。相关既有离线行为不回归。

验证子项：
B档，使用项目现有Python虚拟环境和现有测试框架；先读取test_capabilities.py确定实际入口，记录准确命令，不猜测并安装pytest。
仅运行test_capabilities相关离线测试一批，追加上述实际边界反例；transport/ledger均替身，使用合成数据、不启动PG或外网。
单批最长120秒；最多一次有依据修正后的受影响复检，仍失败即交回；不要扩大全量回归。既有051/055 PG证据不重跑且不拿来证明本次新契约。
保存改动前后hash、命令/退出码、必要脱敏日志于本卡目录。不能运行时如实部分完成，勿以语法通过代替行为验证。

审计与停止：
本卡为实现及局部验证，不能自称独立审计；整体受控入口审计/真实组合门槛保留。超出允许文件、需变更公开数据类型或依赖，停止相关部分交回；达到验收立即停止。
返回：TASK/R/STEP、建议状态、实际差异、真实命令与结果、证据路径、未验证、风险、需求/架构影响、文档建议、必须人工操作及下一步。保存指定结果文件并回复完整可复制结果块，不填Astra最终验收结论。
