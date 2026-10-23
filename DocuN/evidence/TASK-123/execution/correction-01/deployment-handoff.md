# TASK123 修正01 关闭状态部署交接

本文件为本轮当前有效交接，配套[新finite-inputs.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/correction-01/finite-inputs.json)。旧execution目录同名两文件及原报告仅作原字节历史；F124-01的继续理由操作映射已撤销，不沿旧指引执行。

本交接保持 disabled，不创建 normal、grant、T0、operator 批准或首次启用回执。主体沿 [TASK122 runbook](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-122/preparation/operation-runbook.md)，原件 hash 为 8cd01070d1d1eaf9556941f43d63773d9706c46ea2e93a651259759ba3bafcd6。原第3—8节的冻结、精确资源、摘要顺序、逐请求批准、原键对账和真实验收保持；本轮只补以下实际增量。旧 runner、TESTONLY 根及运行许可不恢复。

## 已有入口的新投影

现有同源 session 下的 GET /api/activities/capabilities 增加 diagnostics.readiness，schema 为 retrolume.q-readiness.v1，原字段和 q_approval 含义不变。main.create_app 在原正常装载链中保存候选对象、embedding key 的当次存在布尔及最终有效对象；GET 只深复制启动快照，不读私配、不扫描环境、不执行 configure_application/ControlHub/QAuthority/批准，也不新增 PG 查询。完整 GET 仍会执行原 storage/memory probe，不能在零 PG 的准备合同中当离线检查命令运行。

candidate 与 effective 分别显示 model/embedding 装载和执行门、身份、配置的 returned_models、服务 timeout/request/response/output 限额、活动默认限额与按动作有效输出限额，以及 embedding 512维、4项、字符/查询字节限额。load.available 只表示装载，不等于 execution.available 或真实服务资格。既有活动冻结的实际 quota 不由启动默认值代替。configured_not_observed 表示允许集合已配置而没有真实返回证据，不扩大该集合。

key_presence.model 为 true 仅在候选服务已装载时成立；明确缺 key 为 false，坏/缺配置导致装载器未保留 key 事实时为 null。embedding 为启动当次固定变量的存在布尔，不返回变量值、名字映射、密钥摘要或其它环境信息。未知原异常只给稳定 reason，不返回私有路径、DSN、正文或用户名。改配置后的新事实只能在未来获准正常重启后取得，重复 GET 不热加载。

loaded_evidence 的 grant/manifest 可说明已装载形状、摘要及彼此是否相同。price/activation 是已装载 grant 的引用摘要，内容匹配仍为 null；instance 只有引用摘要，不构造实例或伪造 CID/OID/SID。未取得实际部署事实时 normal_deployment、deployment_match 均 null。qualification 保持 unknown，账号、计量和真实返回均未在该投影核证；grant 内自报 verified 不升级其资格。authorizes_requests=false 说明诊断行为不授调用权，q_approval 仍按原装载结果如实投影。


OBS124-01沿原独审作为非阻塞配置风险保留。模型及returned_models身份栏只填可公开模型别名，不填密钥、密钥hash或私有标签；字符正则不保证识别任意误填秘密，未知别名也不构成真实返回资格。本轮不改产品。

## 计量与账号剩余门

本轮 [计量结论](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/metering-verdict.md) 补齐了当前 DeepSeek 输出/生成/包含 reasoning 明细的文档关系，仍缺两个服务的分词/预处理、完整服务模板及当前版本对应，以及 Embedding 单项和整批容量。原 W+F 公式没有被证明为假，但仍无当前启用资格。未执行模型、Embedding 或计量接口；无有限 token 实测结果。

用户声明 DeepSeek 额度充足仅按 C 级用户声明继承。本人模型 API 权限、币种/含税价/特约、智谱权限/余额等仍 null；沿122已有条款披露，不新加零留存或不训练的必需标准。主控已集中询问，本卡不再弹问。供应商待问原文已保存在 metering-evidence.json，未发送联系邮件或消息。

## 精确文字与真实父的剩余冻结

[finite-inputs.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-123/execution/correction-01/finite-inputs.json) 的HTML focus原文、405 UTF8字节/hash、Q01.03.model当前合格feedback父、Q01.04.query前的顺序及未运行状态保持。真实record/body/point/config、业务键、typed/payload、description/artifact和控件ID仍null。原159字节继续理由文字仅在withdrawn_reference保留，非执行、未持久化、不加入模型上下文，也不承诺存在保存该任意文字的中性备注接口。

FR010/DR002及116 M06/主链已有承载是原evaluate正常当前结果COMMIT时同事务保存kind=progress、body.reason、feedback/answer、observations/support_checks、advance及node_before/node_after，记录body_sha256和state_after，更新head.reason_record_id。这是当前源码的B级事实，尚不是本轮真实PG/Q或重开验证。保存理由不需另发POST；不得用correct、select_node、answer、goal或新增reason动作替代。现有correct保留其真实争议保护。

未来获准链按progress_reason_readback_contract先GET原evaluate业务键及对应progress，核COMMIT、kind/body/hash、原feedback/answer、来源/版本、scope/goal/revision和DataContext。读取reason、observations的独立/辅助/争议依据、support_checks、advance及前后节点；一次复测可以保留节点。两份合格独立实例且推进前置都满足才按原规则处理，没有可推进节点时保存真实保留理由。

下一明确动作按当时真实阶段进行。动作前保存该次progress的准确record ID/hash，再GETworkspace/record核对页面已有“更新或保留理由”。下一动作若改变head.reason_record_id，之后读取已保存ID对应的历史准确记录，不拿新head替代原理由；未来实际重开仍核同条记录/body/hash及进度。页面截图不能单独证明事务持久化。本轮这些实际记录、理由、绑定和重开值全部null/未运行，不预写参考文案或假UUID，不额外增加模型/query次数。未来 IDs、24片实际排序与6批真实批号仍待获准 normal 导入后冻结。

89动作、28Must、24片/6索引直接复用主控已采纳基线，预计22.25元预留。学习43/48、面试28/28、补证18/24；面试无失败余量。它们不是已发生扣账或语义成功保证，真实使用仍0，不换键、借额或省 Must。

## 原部署入口的实际能力与不足

deploy/start_local.py 的公开参数只有 --container、--port 和 --shutdown-stdin，隐藏的 --serve-owned 为其内部启动路径。它会启动 PG/API 并访问正常控制对象，当前没有运行授权。本卡未调用。它没有 --profile、--initialize、--migrate；不从旧设计抄这些参数当可执行命令。

deploy/initialize-materials.py 没有这些初始化参数。仅在另行获准的新库、由安全环境提供 RETROLUME_DATABASE_URL 时执行 backend/migrations/001_materials.sql，不能完成002—015、角色和当前 normal profile。未来真正部署须由主控固定精确库/卷/根/角色及可信迁移链和受信执行动作，本卡不生成通用迁移器、不读取或操作用户库。不能运行旧 DocuN 临时 runner 代替产品部署入口。

当前 receipt.TASK 允许谱系保持原样。首次回执尚未冻结，主控确定真实授权谱系后再判断是否需要定向适配；不预加 TASK123 或任意白名单，不把新操作写成旧120。真实正常实例身份、绑定、权限、服务实际返回、独审及主控首次启用都必须在以后实际发生时留证。

## 稳定候选与下一步

工程的13项离线方法已通过，普通 Review 及原始日志、测试字节、前后副本和统一 diff 可供主控核证；两个先前夹具超时/诊断退出不删。没有重跑原120/121安全矩阵或122分片与预算算术。

TASK124独立增量审查的readiness代码、13方法原证据及可核控制通过范围直接继承，原报告、失败和unknown保留。本轮只撤销F124-01错误指引并补已有progress理由的读回合同，由主控对照原独审和准确需求限定核文档；不把此次核证冒充新独审，不预设再派完整审计或重跑13方法。Q外部计量/账号缺口、L01/L05真实语义及恢复门继续保留。外部门齐备后才由主控给精确资源与实际部署/真实语义合同，按122 runbook继续；不再派同样浏览/批准协议设计卡。本交接不签 STEP018/019/020、M1、项目或发布通过。
