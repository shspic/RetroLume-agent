### C1 STEP017-P1修正后唯一采用包

状态仍recommended_pending。先交主控核证完整合同，再由主控提交用户一个包，本窗口不现在索批准、不代批准、不发TASK114。当前合成实施权/真实删除/切换没有由设计新增。

1. 原首轮只有备份共享/清理排他，改为全部put/幂等复用/新引用/最后unlink的跨线程进程RootLease，源PG shared/exclusive事务围栏与持久reference ticket/epoch取消；加入材料引用guard及必填pin调用点。新引用结果未知不删、已成功共享原件受保、可留原有孤儿。代价为触及导入/替换/PDF/元数据和恢复publication的定向修改/验证，但不新增分布式平台或自动GC。
2. 原snapshot仅写28表读取，改为同一T读28业务加3控制安全投影，三个明确metadata/checkpoint载体，源snapshot仅SELECT，target control身份可信新建、历史/tombstones受限加载并有readonly view。仍3提议表/4NOLOGIN角色、九加载分支和两FK，增加引用相关列/函数/guard、source frozen及profile指纹；无需第四业务控制库。代价是十三版真实身份/权限/元数据闭包验证，活票据/包mode不能迁执行权。
3. 原long job依赖源PG且selector/工厂不闭合，改为独立可信RETROLUME_CONTROL_ROOT的ControlHub journal唯一权威；PG只是T观察/引用事实。明确profile工厂allocate/prepare/verify/seal/activate/reconcile/get-by-key、DPAPI凭据生命周期、跨切换原key查询和所有新写/自有收尾fence。代价是新的私有控制根/控制文件协议和失败关闭；不可读时不能凭缓存/包/旧源推权，不赋任意DSN/命令/路径能力。
4. 保留可携独立解读、隔离新PG恢复、状态/预算保留、控制排除、资料墓碑/准确清理、默认删除覆盖，以及永久只读副本的推荐有限支持。原库普通本机重开不改；旧任务/持续付费/tool/preview/学习活动执行恢复不在本切片，STEP017-P1不替完整NFR005/持续使用/STEP018—020/M-1。真实用户库迁移、真实数据/删除/覆盖/切换仍另有明确授权及风险门，不能以本设计默许。

采用后下一实施卡只按合成source/target、可信profile/固定目录/role/次数/故障余量执行完整成果与集中独审；没有当前产品运行权。不提出多套技术/一串选择，备份频率/介质/有界参数沿推荐由编排冻结，不自动定时/外发。若主控/用户要求付费执行恢复扩围，必须另收敛最新账/拥有者/持续使用门，不能偷偷把只读副本当达成该Must。
