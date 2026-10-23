# TASK-123 / R-117 修正轮01

本轮已撤销F124-01的错误操作映射，保存两份当前有效交付文档。原“继续理由交给correct”的指引有误；FR010/DR002及116 M06/学习主链已有的承载为原evaluate正常当前结果COMMIT时，同事务保存kind=progress的body.reason及进度事实。无需新增中性备注接口、字段、迁移或写入动作。原correct的争议保护、进度算法和Must均保持。

{{DOCUMENT_CHECK_OUTCOME}} 本轮只核文件/JSON/文档，没有导入、compile或运行产品，没有新增测试、PG/SQL/HTTP/browser、联网、下载、模型或费用。原13方法及TASK124独立审查的readiness代码、证据和可核控制通过范围直接继承；它们不证明本轮尚未运行的真实Q语义或重开。

## 当前有效交付与准确读回合同

- [新finite-inputs.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/correction-01/finite-inputs.json)，8949字节，SHA256 79e843d4ccad235c85d24e01cd508160597cb0196baa56e686f9f96d8da0b1e5。HTML对象完整保留，原文405字节/hash、父顺序与未运行状态不变；移除allowed_local_projection。原159字节仅保留于withdrawn_reference，明确非执行、未持久化、不加入模型上下文，不把它当成实际progress.reason或任意备注接口的未来保存承诺。
- [新deployment-handoff.md](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/correction-01/deployment-handoff.md)，8781字节，SHA256 8ece65467fbc9c1ec59b0878c8dbf9564a9605324920c140d19c8879979e5f79。撤销correct映射，使用上述新finite-inputs；补齐准确progress记录、历史指针及重开读回说明。其余关闭状态、HTML、预算矩阵与外部门沿原有效范围。
- [旧到新身份与有效路径](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/correction-01/original-to-corrected.json)、[两文档有限diff](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/correction-01/documents.diff)、[函数级关系](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/correction-01/source-relations.json)。旧execution目录同名文档只作历史，不再按其错误指引操作。

progress_reason_readback_contract指向已有evaluate→progress.body.reason→原read_teaching_command/read_teaching_workspace/read_teaching_record→页面“更新或保留理由”的链。当前源码关系为B级事实，位置为teaching_repository.py的_progress_reason第19—24行、evaluate第1311—1336行及读取第1501—1544行，页面第805—807行读取reasonBody.reason；未执行产品或PG验证。

未来获准真实链先按原evaluate业务键GET已有提交事实，定位同事务COMMIT的kind=progress及准确record ID/hash，核反馈/作答/练习、来源/版本、scope/goal/revision、DataContext与state_after。记录真实reason、observations的独立/辅助/争议依据、support_checks、advance及node_before/node_after。单次复测可以保留节点；满足原独立实例与推进前置才按既有规则处理，没有可推进节点时保存真实保留理由。

下一明确动作前保存本次progress ID/hash并GET workspace/record核既有页面。后续动作如改变head.reason_record_id，读取这条准确历史记录，不能用新head替代旧理由；未来实际重开仍核同记录/body/hash及进度。只截理由页面不证明持久化。本轮真实record/feedback/answer/原business_key、body hash及全部绑定仍null，不写假UUID或参考reason，不为保存理由额外POST纠错、选节点、作答、目标或其它动作，不新增模型/query次数，也不剔除任何真实独立作答依据。

OBS124-01按原独审维持非阻塞配置风险。新交接只明确模型及returned_models身份栏应填可公开模型别名，不能填密钥、密钥hash或私有标签；字符正则不能保证识别任意误填秘密。本轮没有因此修改产品或扩大门槛。

## 原字节与通过范围保护

开工核35项锁定输入匹配；pre/保存旧两文档与原报告原字节。旧finite-inputs为5065字节/hash9fd4b9fcfb2b800ceb62a5668a197aeeada71baf9c3d058e7f78abed60b63c90，旧handoff为6797字节/hashe972c8c96c7443bd7c71a4f92a602b9177caee5fc7d95a524661bdca5169637c，两者均保留，未追改原错误结论。

原六个产品/测试/README/deploy文件维持各自post hash；原execution下49个文件（含旧manifest/save-proof）不动。原delivery-manifest的48条身份按47个原文件加原报告原字节后缀保留。原TASK124报告及主控裁定、原13方法、旧失败/unknown、122矩阵和固定样本均未改。没有写共享DocuS、公共规则或记忆。

一次document-consistency.json记录这些身份保护、原报告后缀、两份JSON/文档意图与引用、HTML/撤销参考的长度/hash、真实字段全null以及函数级关系；同根save-proof.json保存复读结果。它们只证明本轮文档与静态源码关系，不冒称新独审或产品运行。

## 真实命令、退出与预算

在项目根仅执行本轮标准库文档脚本，实际命令为以下三类。

```text
python -I -S DocuN/evidence/TASK-123/execution/correction-01/correct_documents.py prepare
python -I -S DocuN/evidence/TASK-123/execution/correction-01/correct_documents.py write
python -I -S DocuN/evidence/TASK-123/execution/correction-01/correct_documents.py check
```

prepare首次退出1，原因是把permit的contract_sha256误用于含历史整卡；实际许可绑定10235字节contract.md，dispatch-readback及实读确认其为当前整卡精确前缀。按此实际对象更正后prepare退出0、35输入匹配，没有冻结漂移。write退出0。check为本轮唯一一次文档一致性核对，真实退出和逐项判定记录在同根document-consistency.json，未重试旧失败或重跑产品测试。

[本轮工具账](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/correction-01/tool-ledger.json) 与 [预算](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/correction-01/budget.json) 保留实际命令wall和未测项。进入收尾前命令wall观测13.0404908秒、文档工具观测2.573秒，另保守20秒未测开销及120秒保存/唯一核对预留，本轮保守新增156/600秒；并非精确全量实测。原保守3554.557411秒不退款，累计3710.557411/7200，剩余3489.442589秒。人工转交/独审等待未计为本轮工具wall，原三测试批3/3封存、原截止2026-10-23 00:19:11.451055+08不延长。客户端Codex desktop，具体模型ID与累计token未知，原窗口承接常规文档修正，未委派。

## 交回与本轮终点

两文档执行含义更正后交主控限定文档核对收口。执行者未自签F124-01关闭或TASK123整包通过；原独立代码结论直接继承，不预设新增全面独审或重跑13方法。旧审计的不通过原文与原控制/失败/unknown原样保留。

Q分词/模板、Embedding容量和本人账号适用性等外部门继续缺失，Q/normal/T0仍冻结，真实provider与费用0。89动作/28Must/24片6批、100/25及固定分额不变；L01/L05真实语义、恢复和STEP018/019/020、M1、项目、发布均未因本文修正而通过。唯一状态账及正式文档同步和最终裁定由主控维护。

## 原报告原字节保留

以下为修正前15558字节报告的完整原字节后缀，SHA256 d64c3abb832589ab9f826e0327f97a64bd1c2df7c62a9d4b63684f2549886c36。其旧correct映射已被本轮两份有效文档撤销，只作历史，不能按旧操作指引执行。


