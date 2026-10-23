# 断点纠正02有限场景与依赖（执行前冻结）

原资源许可不变，原根15计划留作未执行原件，本目录计划优先。stage≤300秒，根业务队列1240秒，另120秒清场。每个实际阶段记录源as-run、真实previous exit、独立结果；失败只阻真实依赖。不存在PG运行期间聊天投批。根16仅在具体新失败或UI增量需要时另存有限计划，不预写通过。

| 用例 | 场景与对象 | 执行入口 / 依赖 | 继承 / 判定边界 |
|---|---|---|---|
| C01/C02/C03 | 原批准/finite/wire/v1与两产品修补 | 继承command025/036 | 旧通过原件不重跑；实际PG新请求需下面实链 |
| C06 | 原CID与两库、原有效期、A3资格 | c02_observe；教学阶段只读前提 | 实时identity/StopProof成功后才开根；不重复C12 |
| C07/C09 | flow A3新教学头→索引/查询→逐请求批准→原键plan→接受路径→exercise | c02_core.teaching_A3；不依赖面试 | 原A1未知键及槽完全保留；A3冲突立即停该例 |
| C10 | flow A2合法新goal→query→批准→ask→007/领域；原UNKNOWN不重发 | c02_core.interview | 校验真实父及catalog修补；COMMIT ACK故障沿真实原record_outcome |
| C10 HTML | 原learning原件→description待批/GET/原键继续 | c02_core.HTML | 不重跑旧learning、不再应用EOL补丁、preview零 |
| C02/C04 | 未批准answer/history/memory/title、完整foreign请求、跨真实库、字节/endpoint、缺artifact、复制/尾损坏 | probe_approved；仅首个新flow面试请求批准后 | 实际PG快照与完整request；负例不得claim/发送/改金融行 |
| C01/C11 | accepted/claim COMMIT ACK丢失；GET核证；新合法model真实release gap中head+Q revoke | c02_core.ACK_K2；仅依赖面试 | 真实原事务后抛ACK错误；已claim不二发；原007/费用留账 |
| C02/C10 | budget02 A2活动创建前生产memory save/selection绑定；真实完整memory model COMMIT | c02_bootstrap_memory→c02_memory | 原CID第三库、固定三UUID/分额；有效期≤原flow截止；不重复100门 |
| C11 | budget02 A3 scope、A1 source、A2 memory revoke在真实worker释放shared锁后先COMMIT | c02_races；仅依赖memory正例 | 真实独立HTTP线程/PG/worker窗口；结果007与费用不退；head不误推；失效inspect不返回正文 |
| C12 | 原共同100门、达限拒绝、同库重开 | 原root11/12/14继承 | 本轮禁止重跑/退款/恢复旧余额 |
| C13 五入口 | 最终dist教学/query、面试/query、旧learning followup、HTML description待批/GET/原键继续 | c02_ui三个独立有限模式 | 实际响应JS/CSS hash、真实HTTP/SUP；刷新只GET；owner/view迟到围栏；preview零 |
| C13余项 | 新v2 head/scope/namespace/DataContext迟到、草稿保持 | 根16仅按根15实际状态补未成项 | 当前代码未覆盖的维度不得以已有UI owner/view或旧S代替，不预签通过 |
| C04余项 | 只读/删除后副本正文不泄露、丢准备ACK | 根16按原权限与真实依赖补证 | 不用复制实例更早拒绝冒只读模式专属证明；不改变source/readonly权利 |
| C05/C14/C15 | 惰性真实启用门继续关闭、清场及身份差异包 | 继承正常loader；每根精确清场和最终保存 | 任何不可见维度标unknown，不签真实Q/整卡完成 |

三场race只能在各自未claim新意图运行一次，记录原键；任何已claim/unknown不重送。所有传输由最低transport封闭为TESTONLY，非回环socket拒绝；真实provider/实际费用/preview/Git新增均零。正常审批服务容量未恢复时本表不生效为运行事实。
