# TASK-097 / R-091 实施差异与复用边界

本文件补充实施前冻结合同，不改写冻结预期。2026-10-02，Asia/Shanghai；操作者为Codex desktop执行者。当前交付是部分完成的候选实现，8次集成入口和8次精确容器start已经用完。不得据此签G7、全STEP或独立验收。

## 1. 合同细化的实际落点

- 首次入口为POST /api/activities/{activity_id}/learning/first，输入仅business_key、goal、confirmed。
- 学习续问入口为POST /api/activities/{activity_id}/learning/followups，输入仅business_key、parent_operation_id、question、confirmed。
- 恢复入口为GET /api/activities/{activity_id}/learning/intents/{business_key}?action=first或followup。GET不发模型调用。
- 引用入口为GET /api/activities/{activity_id}/learning/operations/{operation_id}/citations/{citation_id}。URL内是应用分配的lc_引用ID，原evidence ID在目录内保留；冻结正文的evidence_id参数名以此细化。
- operation_id实际为learn-first-v1.加规范请求SHA256，或learn-next-v1.UUID.加SHA256；冻结合同已有实施前勘误01，使用点分隔满足既有单路径段读取。
- confirmed实际要求JSON布尔true，数字1和字符串true也拒绝。这项严格类型补强在offline-07中检查，最终HTTP/Windows正向主链未为此再跑。

上述外部DTO拒绝额外字段；客户端不能提供来源、scope/source_revision、ready、原件、system、预算、模型服务或profile。内部LearningProfile与持久StoredProfile分开，不能由模型或资料启用。

## 2. 来源、检索与提交

来源由活动仓储一次只读快照给出。先验证整个实际活动范围，任何失效或未就绪源会关闭新动作，然后有界读取及排名；不把未就绪来源静默混入包。范围外高频近似候选不会参与排名。仓储发布值在真实PG中为revision=1，纯函数额外覆盖revision=0和其他非零值；不把1写成产品常量。

原件最多10源、累计5 MiB；PDF最多50物理页、100文字单元；候选片段最多512。terms.v1查询最多24词项，top-k最多8，证据文本总量最多12000字符和24000 UTF-8字节。包超限明确拒绝或要求缩小范围，不截断出一个伪造的新片段。

catalog由应用形成，包括本次lc_不透明ID、原ev_ ID、来源及版本、实际revision、title/format、原件/unit/片段SHA256、字符offset、行段、PDF物理页、origin_kind和supplement_id、有限文本。目录与目标随规范JSON在原record_outcome短事务中和received一起提交。没有新增表、迁移或提交后的第二笔目录写入。

内部profile有父payload摘要及有限history，用于现有G4准入和内部适配；持久正文及浏览器没有parent_payload_sha256、history或父消费凭证。公开正文保留parent_operation_id、goal/question、scope/sources、输出上限、规范摘要、目录、result、固定能力限制。读正文时还核实际activity_id和operation_id，普通model正文自报learning.v1不获得学习成果身份。

gateway在admit前复核严格profile及活动/来源；在原子record前校验输出。资料/历史正文只作低信任文本。正常调用无工具，原protocol3/4外层和回执字段不改。后补的保留学习命名空间却没有profile的内部调用拒绝，在offline-07中验证；它没有最终真实Windows复验。

## 3. 幂等与恢复的具体取舍

规范摘要绑定profile/action/activity、goal/question、scope及排序来源、父operation/内部摘要和输出上限。首次稳定槽位由既有operation_id前缀和独占执行租约实现，与客户端UUID无关。worker取得租约后再查槽位，覆盖两客户端真正竞争；同请求返回持久事实，异文409，不套用旧正文。

已经形成操作的UNKNOWN、NOT_SENT和received非法正文也占首次槽位，只能查询事实；同键重试不再发送。尚未admit、没有持久操作的显式重试才可能形成新调用。目标变化应显式续问或新活动，不能覆盖历史。未知调用继续保留原预留；不把已知非法正文冒充远端未知。

客户端在显式POST前保存业务键和规范输入，不缓存成果正文或授权物。刷新/切换只GET，核对/同键重试/放弃分离。放弃仅去掉本机意图，不能取消远端、退款或删除服务器成果。

在最后一次集成后，新增compareLearningIntent核对持久目标、问题和父操作；未取得可核正文时不清理未确认意图，冲突明确保留。还补了核对回包的活动切换、序号和卸载保护。这两处只有offline-09真实意图纯函数及build-03/04/05证据，最终UI动态not_run。

## 4. 原主体与文件字节

活动repository只追加read_learning_snapshot和find_learning_operation两个单SELECT只读助手。既有末尾read_operation的CRLF转LF导致原字节prefix检查false；CRLF规范化后整个旧文件是当前前缀，旧正文、所有写/锁/恢复及ActivitySpec/ActivityLease均未改变。不能把这项静态检查称为事务测试。

11个冻结停止/传输/工具/认证模块pre/post原字节相同。原001—008迁移、materials/pdf写及来源认证、依赖锁和正式DocuS未改。worker/one_call、worker_main、command实际无需产品修改；真实链通过可选ModelCallRequest字段及gateway应用适配复用。

pre-manifest保留初始40个直接目标原件，不回写历史。原dist的4个原件在第一次离线快照及首次build前均已保存，pre-dist-manifest另列实际起源。changes及有限diff据两类真实原件计算；不以Git基础提交替代当前基线。

## 5. 构建、运行与证据适用

每个资源入口有as-run原件、SHA256、命令/预期、原始stdout/stderr、运行后指纹。bootstrap在真实worker导入时读取原字节编译并记录摘要，绑定到入口前as-run保存的相同原件，不只记事后当前文件。失败不覆盖，integration-01至08均保留整体exit=1。已通过的单场景与失败后未执行场景分别记录。

build-02的四类产物在browser-07实际取得字节并校验摘要，包括PDF worker。browser-08新应用和新浏览器上下文只读取07持久成果，没有重造父结果或发送新模型请求。

build-04后源码没有再改产品。发现早期构建快照遗漏frontend/index.html和tsconfig.json后，build-05-complete-inputs补齐真实前置输入再正式构建；输出与build-04相同。此前缺失不追认为已经保存。最终bundle仍未在真实浏览器服务，补构建只补来源链，不替代行为复验。

已收到但伪引用/非法JSON的实际Windows操作是received且无正文；真正UNKNOWN操作保留次数/费用预留；真实并发两监督会话只有一个合成send。取消晚到场景保留此前合法首成果，当前新操作没有正文；监督本次R=90保守全额折叠进入活动S=92、R=0。页面即时返回的R=90/P=90是先前观察时点，不能写成未结算的最终账。

## 6. 未完成的动态范围

- 最终意图匹配/迟到保护、同键恢复/放弃、损坏台账下读取与取消的组合UI、缺配置UI、坏引用/替换后UI、慢回包切换/隐藏轮询/卸载场景未完成真实浏览器验证。
- browser-07刷新后的选活动定位器错误和browser-08响应体观察Promise错误导致整体失败。最后修正的脚本只有模块预检或静态修正，不能记浏览器通过。
- 专门挂死后由自有Job强制硬停的120秒场景未执行；已执行取消/异常退出并核树零不等同于该硬停场景。
- 真实PG删除来源、全部数值上界逐项触发、不同目标的并发竞争并未全部执行；已有实际revision失效、未核PDF、范围外资料、同摘要并发和顺序异文拒绝证据，不能扩写成全部反例通过。
- tool凭证隔离未新增真实Windows场景，只复用未改协议4/工具主体与直接协议用例；未重跑整套D3/G5/G6。
- 真实provider语义质量、Embedding/向量融合、完整STEP-006/007/008/009、M-1、用户库、发布和独立终审均不在本次通过范围。

资源入口与start达到上限是本次停止条件。剩余秒数、监督或浏览器名义余量不授权第9次入口，当前结果不能写成“候选实现与卡内验证完成”。
