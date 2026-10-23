# TASK-120 / R-114 — AP-120-06 最小合并采用包（待用户决定，未生效）

## 当前结论与采用事项

完整收尾05已真实返回。原正常五入口、练习、共同100门、11项全请求权限反例、三种COMMIT丢确认、head/revoke/scope新增/source竞态和列明memory不变量已有适用证据；这些不重做。范围实际移除仍缺权限，namespace/完整DataContext迟到UI未通过，TASK120总验收部分通过，Q继续冻结。

本包只有一个合并决定：**是否采用以下单表权限修正、对应严格指纹/兼容适配，以及两项剩余UI所需的最小隔离资源和续验时窗。** 它是工程与合成验证授权，不包含用户库迁移、真实provider/key/费用、生产部署、preview、Git或正常Q启用。

## 1. 推荐的唯一权限路线

用新增前向迁移015向既有NOLOGIN应用组角色retrolume_data_app，增加且只增加public.activity_scope_sources这一张表的DELETE权限。权限核心为：

```sql
GRANT DELETE ON public.activity_scope_sources TO retrolume_data_app;
```

这张表保存活动与资料版本的绑定，不是资料正文或模型成果表。已有013已授同角色该表SELECT/INSERT/UPDATE；repository的范围修改原本就要替换/移除绑定。真实移除在scope-removal-blocker.json明确命中42501，原命令不存在、head/scope/费用不变。绕开无必要全量删除已修复新增/更新，不能代替真正的移除。

015须事务化、校验预期旧schema/角色/trigger，只在本包隔离合成实例实际执行；001—014原字节不改，不授TRUNCATE、其他表DELETE、PUBLIC权限或管理能力，不变更旧登录角色密码/成员关系。

新增权限会改变严格权限指纹，允许为这个精确前向差异更新版本化schema/profile/迁移链检查；必要的新profile标识只用于已确认的新权限版本。业务表列、金融语义、公开HTTP接口、备份包格式/编码不变，旧R01/R02只读包与恢复识别兼容。不得把白名单改成“有足够权限就行”，不得接受任意额外ACL、放开所有profile或自动升级旧实例。

现有data_runtime_write trigger仍覆盖本表INSERT/UPDATE/DELETE，非normal模式抛data_runtime_readonly；现有仓储来源锁→活动锁→CAS/资格→操作序不变。**这仍是表级权限，不是行级权限。** 可信应用角色若脱离仓储直接执行SQL，可删除本库任意活动的绑定；CAS/活动边界由应用事务与现有guard承担，不能虚构为数据库行级授权。该角色原已具表级INSERT/UPDATE，没有新增SQL入口或把凭据提供给浏览器。

相比新增SECURITY DEFINER范围替换函数，推荐本路线因它保持现有受信应用角色/仓储模型，只补一个缺失DML能力；后者可缩小直接表权，但会新增数据库接口、参数/锁/CAS实现和更多同步审计范围。本包不同时实施两套路线，不新增通用权限平台。

## 2. 必须验证的安全及兼容边界

- 正常完整移除：同活动预期scope_revision匹配，实际只删除被移除绑定，scope恰增一次；未选活动和其他表/财务不变。
- 旧CAS、来源失效、未知活动、跨活动父/请求身份不符等在既有入口准确拒绝，无部分绑定/版本变化。不是要求表级DELETE在任意裸SQL中自动实现CAS。
- frozen/restored_readonly依旧拒绝写；readonly/snapshot/restore-loader不能因本次授权得到正常DELETE权；表级ACL与预期版本精确匹配。
- 受影响的真实scope收缩K2：shared发送段释放后完成真实移除，随后结果事务保留007与费用、抑制旧head推进；不重跑已过所有K2。
- 新权限版本的初始化、指纹不符失败关闭，以及直接受影响的旧profile读取/恢复识别；不全量复跑旧数据出口所有用例。

回退：在新合成实例事务内REVOKE该单表DELETE，并恢复其匹配的权限版本检查/配置；保留全部业务记录。回退不声称能自动撤销已经合法提交的范围移除，故本包不在用户数据上运行。指纹不匹配时必须失败关闭，不关闭guard来维持可写。

## 3. 两项UI证明的真实目标与操作顺序

原matrix-final已永久frozen，原三库grant过期；不解冻、不重建、不重绑、不刷新它们的授权。仅靠原frozen库的HTTP拒绝不能证明真实正常批准响应的UI迟到隔离。

准许在原CID/卷新增唯一合成源库retrolume_task120_scope_ui_final，fixture槽scope-ui-final；必要时仅建本库最小应用角色retrolume_task120_scopeui_app。沿TASK116冻结8份文字/有限输入、固定三UUID/48-28-24与100/25合成上限、最低传输替身，建立独立TESTONLY根。旧四库/旧余额/旧root不变。015及匹配profile仅在此新合成源与下面正常恢复目标初始化/验证，不迁移旧四库或用户库。

真实生产TargetFactory.allocate会创建独立Docker恢复目标，并要求verified restore job和restored_readonly身份；旧frozen源不能直接冒充该目标。故同时准许**至多一只**该工厂创建的恢复目标容器及一只命名卷：

- 名称retrolume-task120-scopeui-ro1，卷同名加-data；数据库retrolume_task120_scopeui_ro。
- 固定原本机镜像sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f；不下载镜像。
- 1CPU/512MiB/pids128/restart=no、仅named volume、无host bind，仅127.0.0.1发布；55481和55482中预检实际可绑定的第一个在创建前固化，碰撞不杀进程/改系统/乱换名字。
- 必须通过原正常备份/恢复/验证/activate_readonly及readonly probe，实际CID/镜像/卷/端口/目标身份在创建前后登记；不得伪造verified receipt、手写selector或以保存JSON代替正常激活。复用现有合格fixture，无新恢复平台。

这两个目标仅用于新的最小实验，旧四库不写、不复跑正常五入口。固定镜像工厂及其原命名卷/readonly角色边界不放宽；如果实际预检不能满足，就在创建前带具体不符返回，不消耗创建额度碰运气。

UI测试先完成范围移除与正常准备，再进行不可逆freeze/selector。关键修正是：**旧正常批准GET应先在实例仍normal且合法时完整取回并暂停交付，然后才切换上下文。** 不再先冻结源、再尝试取得旧正常Q响应，避免再次在q_root_changed处正确拒绝而根本没走到UI。

准备两个独立的真实GET响应/握手点，每项立即checkpoint：

1. 完整DataContext子例：抓到真实正常200/批准投影后，源经生产维护机制变成readonly/frozen；观察完整control_id/selection_generation/dataset_id/instance_id/current_mode/read_only。对命名空间未改变但mode/read_only改变的路径单独验，确认新状态已入UI后释放旧响应，旧正文/输入/可继续资格/意图台账不得污染当前状态。
2. namespace子例：另一个在normal阶段已合法取回并暂停的真实响应，在原生产activate_readonly切到verified恢复目标、selection_generation/实例身份和storage namespace确已变化后释放。核新身份内容/草稿/资格/台账不被旧响应覆盖、零自动POST。

可在同一normal阶段先捕获两个真实响应，分开释放；源冻结/选择目标的真实先后必须与checkpoint一致。若生产客户端取消了旧请求，准确记录取消分支，不谎称旧响应已被消费；原验收需要的实际迟到处理路径仍须按相应真实UI路径证明。只用正常正式bundle/认证/响应头；不调用前端内部setter造身份、不伪造body、不用普通标签切换代替DataContext。

## 4. 采用后的许可及终点

采用后由主控签发原TASK120/R114同号续作06给**刚完成05的原A工程窗口**，不再换窗。先实现/检查015候选与精确指纹，后在上述隔离资源验证移除和两项UI；普通修正同卡完成。已有权限反例/ACK/竞态/head-scope/UI正常链全按原对象复用，memory缺即时before-financial快照的限制原样交终审，不自动强迫重跑memory。

真实操作前必须完成权限差异风险检查；最终稳定包按原118独立归属另卡集中增强终审，重点新DELETE/profile/兼容和最后UI。工程不自签独审，必要审计不因“必须完成”省略。

拟新增的是一个至多12小时、受原96h截止2026-10-22T08:41:08.5687758Z/末1800保存期限制的补证窗，从实际接收续作06起计。**目前尚未授予这段运行时间或任何GRANT。** 原05窗已于2026-10-20T20:04:46.848938+08到期，不能重开；原task首点/失败/预算不重置。

不增加现有root64/PGstart64/API96/Browser16/build8/Native128/HTTP10000及wall57600/持有21600上限，按实际余量和新增资源计数运行。新增实际PG对象/卷各至多1（累计各2）；保留原创建尝试cap2（已用各1），仅余1次；源逻辑库新增对象/尝试各1单列记账。所有旧已用/未知预留保持。

每根1800含末120、每测试子批300、metadata60秒保持；单headless/context/page、512MiB启动门、1秒采样连续两次<256精确清场，无sandbox/认证/外网守卫放宽。两个PG仅在恢复/激活确有需要时最短重叠，其余串行，不能持源空等UI。最终精确停原CID和新目标，PID/birth/Job/两组端口/Running=false/Pid0逐个留证，保留数据/容器/卷，不prune/drop/truncate。

## 决定状态

**待用户对上述合并包明确采用。** 主控已完成源级边界/实际失败和资源工厂核对，只写本提案、后续草案及共享状态；没有运行SQL/Docker/API/Browser/模型，没有修改产品或工程账。此前“下一次必须完成”没有明确涵盖这项新的应用角色DELETE权限，不能用提示词替代权限采用。

依据锁定公共DocuS/AGENTS.MD第2节：权限调整“须有覆盖动作及范围的明确授权”。若不采用，原角色/profile的范围移除不能承诺通过，Must不自行降级；其余已完成成果与Q冻结保持。
