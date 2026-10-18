# 10真实结果、观察器修正02和停止边界

2026-10-02 +08:00。10整体exit1、finally cleanup_ok=true。浏览器五个失败/未覆盖场景全部PASS，真实恢复声明/折叠和HTTP边界/伪引用PASS。没有重复09主链/硬停/来源撤销。

不同目标同时进入first、唯一成功槽位/目标、唯一send、不套旧正文这些基础业务断言成立；额外两份完整SUP生命周期断言FAIL。第二个SUP已由真实CreateProcessW创建（PID35868、真实创建时间在未替换成功的tmp原件），尚未Resume，观察器os.replace既存sup-launch文件时与计数器读者的Windows共享删除权限冲突，PermissionError使完整回执缺失。原FAIL、tmp及真实输出不改；不能把这个案例充作两份正常SUP竞争通过。

累计SUP启动尝试23=初轮15+续作8（包括尚未claim/在Resume前失败），新增额度已用完，停止所有SUP业务新启动，不借旧余量。09的JSON失败发生于计数器读者阶段、未CreateProcess，不另算真实SUP，但另列业务尝试。10那个已创建未Resume的会话按真实启动计入，不能漏记。最终只读核实其PID/创建时间已退出；全体树/容器/端口最终记录在C/resources-final.json。

定向修正02：sup-launch只一次发布为不可变计数记录，真正CreateProcess身份另以sup-created独立记录发布；计数器只读不可变记录，不再替换Windows读者正在打开的文件。创建后观察落位若异常，将已创建的partial句柄交给原launcher清理，停止主体不改。进程收尾同时读取sup-created真实身份。

此修正只允许离线真实Windows文件并发验证：两写线程/读者、150个发布、禁止覆盖、真实文件内容完整，0SUP/Job/进程/端口；产品字节不改。**完整Windows业务链对修正02 not_run**，额度停止，不用文件并发检查冒充SUP运行通过。竞争的两份完整生命周期补证仍未关闭；本卡不自签完整/终审。

业务默认HTTP的旧running恢复仍关闭，09因此失败关闭符合既有权威；10测试通过受信内部入口显式声明既有同主机/会话前提，只证明该声明路径，不表示HTTP已具备新恢复配置。
