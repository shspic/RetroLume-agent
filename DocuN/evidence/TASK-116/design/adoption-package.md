# STEP018具体采用包（待主控串行处理）

本包是TASK116设计产物，尚未采用、实施、出卡或开启费用。主控可在既有开发授权内直接编排资料/目标/领域命令/UI接线、当前能力的普通修复、文档维护及获准的合成验证；这些不因新阶段再请用户批准。真正新增模型/公开接口/权限/外发/费用只收在下面两个决定中。原TASK114/115关闭、所有失败/计数/费用不变。

## AP1：受控向量与前向兼容包

推荐采用[integration-contract.md](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-116/design/integration-contract.md)B2—B5的**单一完整方案**：014、新embedding kind、OneCall wire v4/v3兼容、3张检索表、R02与R01并存、learning.v2/teaching.v3/interview.v2严格绑定、现主体预算与监督复用。必要性：架构已定pgvector融合当前仅有词项通道；Embedding目前没有类型/准入/事实承载；现恢复器固定十三链/28表，不能无声插表；当前面试明确拒记忆，不能假称已有跨链背景。

改变范围：新增retrieval三HTTP入口（命令POST/命令GET/status GET）、受信Embedding配置及typed能力；新role/profile/准确DDL与旧函数fingerprint增量；面试v2允许创建时可选学习记忆低信任背景。面试读学习记忆是为本卡“两链记忆贯穿”的**新建议**，不是原FR011单独明确的已缺Must；作为推荐集成包一并采用，不将旧v1有限验收降为无效。所有现model/tool旧行、旧领域profile/hash、旧R01包/只读副本保留，不改001—013或固定renderer。

AP1并增`activities.outbound_grant_sha256 text NULL CHECK(NULL或64位sha)`（旧行NULL）用于新真实外发许可归属。create由受信服务器配置填，浏览器不能选择/重绑定；已有活动不可改grant去借新额度。R02明确导出/恢复该列，R01投影仍是原列集。纯合成transport不要求真实外发grant；所有新真实chat/embedding准入要求受信`OutboundGrant`，未知或过期失败关闭。此列属于014/profile采用影响，不用第四张通用预算表。

`OutboundGrant`仅为固定operator部署配置，不存key，字段封闭：`schema,grant_id,approved_receipt_sha256,valid_from_utc,valid_until_utc,provider_capabilities,allowed_activity_ids,global_max_requests,global_max_cost_microunits,price_snapshot_sha256,data_class='synthetic',source_manifest_sha256`。hash进入activity，固定活动roster的价额合计不大于global cap。新收费准入先取grant advisory lock，再依现source→memory→activity→domain→operation锁序，PG查询该grant所有活动的累计request/cost预留（含unknown）核门；随后每activity原admit再次核四账。kind=embedding也走该锁，不能用浏览器另建活动、换供应商或换grant重置本次许可。received结算不倒减已用请求；旧unknown未核不折回。无需Redis/新SDK/通用Agent框架/新增常驻看门服务。

安全与失败影响：API仍localhost session + DataContext + mutation gate；snapshot只读、loader仅loading、seal后全部新写拒；embedding007不能作任何领域父。迁移仅新正常合成库先证非空兼容，失败保留旧链/资源，不能降R02到R01丢事实。R01/R02恢复均永久只读；本包没有“恢复副本继续执行”变更。独立审计覆盖新kind/公开入口/角色/R02/memory域传播稳定成果一次集中完成，旧充分原件复用。

若AP1未采用，可继续现有领域/词项合成接线与文档；hybrid、新profile/权限及完整STEP018门保持未实施。这个有限替代保留成果，不是降低原Must或把词项自称向量；不另提平台选型。

## AP2：真实服务合成验收许可（一次20元封顶，待核后开启）

推荐先仅合成必要片段，不包含真实履历、学习记录/原件、旧库私配或整库；仅固定下面两个候选能力，不自动换模型。

| 能力/服务配置 | 推荐候选与采用前必须确认 | 运行上限 |
|---|---|---|
| Chat / 现DeepSeek适配器 | provider `deepseek_chat_completions`；候选configured_model `deepseek-chat`、既有固定base `https://api.deepseek.com`及chat-completions路径；thinking disabled。精确当前ID/返回别名、无额外思考账单、结构输出能力/账户条款/价目必须官方现行核，不用旧Flash/Pro实验担保 | 一次POST、timeout≤10s、request/response各≤65536bytes；learning v2≤256输出tokens，teaching v3/interview v2≤2048，HTML≤4096且沿原固定描述schema；无隐式重试/额外tool服务。 |
| Embedding / 新typed adapter | provider `zhipu_embeddings`，candidate `embedding-3`、512维、候选`https://open.bigmodel.cn/api/paas/v4/embeddings`；须核当前批量/维度/输出identity/usage/账户/条款，资料仅本JSON合成片段 | 一次POST，≤4inputs/每项≤2048codepoints（query单项≤1024chars/4096bytes）、timeout≤10s、body≤65536bytes；不调用reranker/后台索引/其它模型。 |

本卡不联网，因此上述候选不是已核当前产品承诺。主控在获得相应联网核查范围后记录官方能力/价目/条款日期、具体页面、账户适用性及模型别名；若候选缺必需能力或任一次10s无法完成，失败留证回主控，不能延timeout或换供应商当普通夹具修正。

收费许可建议从未来明确生效时起72小时；仅以下三固定新合成活动ID：`01800000-0000-4000-8000-000000000001`学习、`...0002`面试、`...0003`剩余语义补证（真实完整UUID在实施卡）。每activity deadline24h、max_running_seconds3600、max_request_bytes65536、common max_output_tokens4096；每次model/embedding预留0.25元人民币（250000 microunits，1元=1000000 microunits）。学习max40requests/max10元，面试24/6元，补证16/4元；合计80requests/**最多20元新余额**，含全部失败、超时与unknown，旧13元耗尽/旧626.566秒等不追认或抵扣。单activity finite_calculate≤8次，允许工具只有finite_calculate，无外部收费工具；预览仍3次/180s、一次30—60s。所有模型/嵌入共享每activity次数/时间/费用；不按两家各80次。

0.25是建议安全预留，不是报价。只有**已核当前最坏成本≤0.25元**的具体request可发；按官方当前单价、已核token计数或保守上界（不能把UTF8bytes声称精确token）、output cap、币种/必要汇率/税及至少25%裕量向上取整核算。缺价格/计量/税汇率边界即关闭真实能力；超0.25拒该动作，不自行提reserve/global20门。这个用量上限允许完整链与普通失败余地但不保证全部质量场景成功；不足停止回主控给精确剩余矩阵，不能购买额外额度/开新活动借余额。

真实故障/UNKNOWN测试使用最低transport替身，避免向供方故意发失败付费。Q语义以验收合同L/I冻结rubric逐项记录，通过与失败都保留。主控可先发零网络合成实施卡，AP2核价与授权未就绪只封收费部分，AP1后的正常合成实现不被阻塞。确认AP2后仅后续完整实施卡可激活本grant；TASK116上限始终0。

## SEC001及本机配置的具体交接

现model key继续服务器`RETROLUME_MODEL_API_KEY`，新embedding key仅服务器`RETROLUME_EMBEDDING_API_KEY`；本地activity/retrieval/operator配置放用户已授权private位置，由正常secret loader读取环境名，不写浏览器/日志/证据/导出，不向对话索key。provider告知包括用途（必要片段索引/问题检索/路径题反馈/面试/描述生成）、资料类synthetic、所选scope与bytes/有限调用/成本；本地确认不能越过服务端批准grant。provider现条款未核时连合成付费也不自动发。

真正本人资料以后若要外发，需要另一个**数据范围决定**：明确资料类别/范围、同一已核供应商用途与保留/训练条款、账号适用性及费用模板；不是重新审批项目或本地只读导入。AP2不包含这一权限，不提前把真实资料贴进合成许可。STEP020可以本人在本机用冻结合成资料完成启动/继续/停止运行交接；真实个人内容只在相应范围有效时使用。

## 推荐串行节点及最终通过条件

1. 主控采用AP1，按完整实施卡草案发**一个**工程成果合同：两链、hybrid/新kind/R02、normal重开、本机启动/文档、有限验证及普通修复连续完成。不预占TASK/R或把每次准备/修夹具/重试另转卡。
2. 在该工程窗口达到稳定完整合成候选后交一个独立窗口集中核新增安全/权限/预算/兼容/最终bundle传播，可作为适用STEP019主体原件；关键新边界未通过前不开AP2。AP2核实和许可形成后原工程窗口补真实合成语义，再由同一独立窗口只补语义/实际变更和剩余项目验收项，沿用未变审计，避免整套重审。实际缺陷可范围内连续修复，不能承诺固定余卡数。
3. STEP018只有两链真实对应层、全部本合同Must样本及normal同库继续成立才提交通过；无AP2只提交合成成果和Q未验证，不能签STEP018全部完成。适用STEP019集中收口SEC001/002/003、persistent预算/unknown、R01/R02及最终bundle、新供应商证据和整体剩余Must；必要审计独立于工程，不由本窗口自签。
4. STEP020依赖STEP018/019通过且未有阻断缺陷，再本人运行正常本机交付，确认一次启动/能力就绪/两链保存/重开明确继续/停止自有资源/可读退出与readonly隔离查看。本人真实数据需已有效数据范围，不借pilot；Should/Could/未来Linux/Nginx公开发布未纳入不阻首版。主控串行维护DocuS/编号/裁定，本窗口只回传保存路径。
