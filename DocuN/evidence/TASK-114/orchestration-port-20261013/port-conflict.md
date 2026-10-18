# TASK114续作01 source端口阻塞事实

2026-10-13T11:24:47.358892+08:00，Codex编排Agent。用户截图说明原114窗口已实际继续，source 127.0.0.1:55461绑定报WinError10013；本轮对系统和容器元数据及端口作检查，没有停止服务、改变防火墙/排除范围、Docker启动或产品执行。

## 已观察事实

- netsh interface ipv4/ipv6 show excludedportrange protocol=tcp均未列出覆盖55461的排除区间；不据错误码假称系统保留。
- Get-NetTCPConnection -LocalPort 55461显示LocalAddress=0.0.0.0、RemotePort=0、State=Bound、OwningProcess=7912。只筛Listen会漏此记录。
- 临时IPv4 TCP Socket ExclusiveAddressUse绑定Loopback:55461复现NativeErrorCode10013，2026-10-13T11:12:04.3195014+08:00；finally立即Dispose，无持久端口或设置改变。
- PID7912为gdphost.exe，创建于2026-09-30，父PID6328为gdpsvc.exe；父对应服务gdpsvc，Running/Auto，PathName为C:/Program Files (x86)/Common Files/Glodon Shared/GDP/4.0.0.123/x86/gdpsvc.exe。来源为本机CIM，不根据文件名猜软件或解密私配。
- source CID2659f71b56015c0de1be5a3d5790a47e0362139bbbaae45ad3a45bf562706c22仍Running=false/Pid0，原image/卷/127.0.0.1:55461不变。当前task namespace只见source、target04、target05均exited；不是停止证明或完整目标验收。
- current receipt此刻counts为real_roots12、PG create/success3、start12、Windows1、build2，累计次数只是账观察，不签合规/业务通过。主控不修改该执行账。

## 裁定与最小操作

source当前端口由项目外广联达后台进程绑定，是可证的当前占用事实；未监听不等于空闲。10013可由其他应用独占绑定产生，微软说明：https://learn.microsoft.com/en-us/windows/win32/winsock/windows-sockets-error-codes-2 。不据此推断该进程的所有网络策略或恶意性。

本任务仅授权准确停止自有工作，主控未获停广联达软件/服务的对应许可，不自行kill PID7912/父服务，也不重启HNS/Winnat/Docker或清Windows端口排除。若用户当前不使用广联达，先保存退出其软件，再在services.msc临时停止gdpsvc；后续可以启动恢复，启动类型不改。服务正在被使用则先保留，需另决定连接安排，不能执行Agent自行改原CID/卷/端口。

服务释放后由主控或原执行窗口先重查所有TCP状态、临时bind并立即释放、内存及准确source身份；真正通过才在现行C01计数/预算内一次启动原source。未知/仍失败不反复重试，继续不依赖source的独立目标和HTTP工作。现行许可允许所有自有资源准确停妥且外部等待有UTC/mono/原因/断点时暂停活动工时；真实资源持有永远不暂停，不能清零失败或宣source已验证。

无需新技术采用、预算或另派任务；当前TASK114在途，TASK115仍待稳定，不以截图代验收。
