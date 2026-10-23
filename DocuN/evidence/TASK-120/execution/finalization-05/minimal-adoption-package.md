# TASK-120 完整收尾05：最小采用包（未执行）

当前工程未达到完整稳定候选，Q 继续冻结。本文件供主控判断必要范围变更，不形成新授权或独审结论。

## 范围移除权限

实际角色 task120_flow_app 在 public.activity_scope_sources 上没有 DELETE。新增/版本更新已通过；真实移除返回 503，SQLSTATE42501，事务回滚，命令不存在且 head/scope/费用未变。精确原件是 scope-removal-blocker.json。源修补只避免无必要的全量删除，没有绕过权限门。

最小直接候选为在新的前向迁移中向 retrolume_data_app 授予这一张表的 DELETE；候选 SQL 为 GRANT DELETE ON public.activity_scope_sources TO retrolume_data_app。它会扩大该角色在此表的删除能力，不能按普通代码修正自动采用。另一候选为限定 activity、CAS、normal data mode 的可信范围替换函数，固定 search_path、撤销 PUBLIC EXECUTE、仅授应用角色 EXECUTE，配套 schema/profile 指纹与函数守卫审查。后者需要更多设计，但可缩小直接表权限。

主控应选择并明确采用权限/持久合同增量，再安排隔离安全审查；随后才可落新迁移、匹配 profile 和应用调用，并仅补真实移除、CAS/异活动/只读拒绝及受影响 K2。001—014 原字节不改。本包没有应用上述 SQL、创建函数或更改角色。

## namespace 与完整 DataContext 晚到

根33的 head 子例和根34的 scope 子例通过，正常五入口及 owner/view 证据直接继承。根36已将唯一新增矩阵库永久 frozen；界面切换前的缓存 Q 核证触发正确 q_root_changed，旧批准响应并未完整交付给新上下文，因此不得签 UI PASS。

续验需要明确授权一个可形成正常、当前、尚未 claim 的批准 GET 的独立有限测试目标及精确目标切换流程。原三库过期，不续 grant；matrix-final 不解冻、不重建、不重绑；不能复制批准或恢复旧响应冒充新的实测。现卡仅一个新逻辑库的额度已实际使用，不能自行新增第五库。采用时写清精确实例/根/期限/次数与清场上限，继续仅冻结合成输入、最低传输替身、单 Browser/context/page、真实 provider/费用/preview/Git 为零。

先形成合法正常响应并实际延迟，再通过生产 DataContext 机制切换 namespace/只读身份，记录真实路由、业务键、身份前后、当前内容/输入/可继续资格/新身份台账及零自动 POST；两个独立子例逐项 checkpoint。不得用标签切换、HTTP 只读拒绝或保存过的 JSON 替代此 UI 证明。

## 交回与终审

先完成上述采用及受影响工程验证，代码、证据稳定且无并行写后，再由主控按原118独立归属集中终审。本工程未启动或自签独审。建议主控在唯一执行动态账记录本轮局部完成、两个真实缺口和精确清场；本窗口未修改 DocuS、未新建 TASK、未分配 CHG。
