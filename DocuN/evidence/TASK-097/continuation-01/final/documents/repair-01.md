# 09失败原文与一次合并夹具修正

产品文件/最终dist未改变。累计09整体exit1，cleanup_ok=true，原始日志/FAIL/截图和as-run完整保留。

1. lost/unknown UI：原夹具从整页刷新进入未选活动状态，却等待只为当前选中活动展示的调用通知。真实POST/意图更新已发生，页面正确避免把别的活动通知写入当前详情。补选中真实活动，再等待通知与持久意图。未改产品提示/权限/DTO。
2. poll：实际GET列表为 `/api/activities`，原glob要求问号查询，未拦截，未形成running UI前提，原生Promise未超时。观察窗不能成立；记录FAIL，定向终止已核PID/创建时间匹配的本卡Node子树。finally确认所有本卡进程zero与精确容器停止。修为URL pathname判定、真实HTTP响应屏障、Node侧15秒有界屏障、finally释放hold。该项未把原FAIL填PASS。
3. 竞争计数器：观察文件在CreateProcess之后更新时使用非原子write，另一线程读取到截断JSON，第二业务候选在实际SUP创建前被夹具JSONDecodeError关闭。原竞争仍唯一send/目标绑定，但不能用它独立证明两个真实SUP竞争。计数/回执文件改为临时写后os.replace原子落位，复验不同目标竞争两份真实SUP回执与唯一send。
4. HTTP恢复：原SessionConfig.single_host_single_session_recovery默认false，真实硬停后HTTP按现有停止权威失败关闭，R=90不退，树真实0；不是夹具可绕过的自动退款。合成环境已明确同主机/会话、旧树/旧SUP零与来源有效，定向用现有受信内部run_one_call入口的显式已有恢复前提配置完成合法恢复。学习profile/目录/父凭证仍从真实持久事实和当前产品构造器取得，真实launcher/SUP/worker/Job/gateway不变，不开启产品HTTP恢复或改停止参数/写锁。随后同键HTTP仅返原持久事实，验证折叠一次。

下一入口只测以上失败/受影响与未覆盖的引用切换、活动慢回包、当前HTTP限额/伪引用。09当前正向、冷读/刷新、四产物、坏台账/缺配/XSS/主动网络、操作与引用卸载/核对迟到、真实硬停/来源撤销及confirmed成功子项直接复用。新增SUP最多3（恢复1、竞争2）；09已用5，新增总8封顶。旧初轮一份SessionOutcome缺件继续披露。
