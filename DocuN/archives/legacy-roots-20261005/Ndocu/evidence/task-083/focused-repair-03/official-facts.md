# TASK-083 focused-repair-03 官方事实与边界

本轮只读以下 6 个 Microsoft Learn 页面，未作本机系统探针；适用目标为本项目 Windows 内部 SUP。文档事实不能替代本机 Job/进程验证。

1. [CreateProcessW](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw)（Windows 桌面 API）：显式 `lpApplicationName` 绑定可执行映像，`PROCESS_INFORMATION` 返回进程及主线程句柄，`bInheritHandles=FALSE` 禁止普通句柄继承；创建函数返回成功前没有可由本调用者使用的 `PROCESS_INFORMATION`。本文未证明任意内核挂死时的硬墙钟，也未给出父进程死亡后悬停线程绝不被其他有权限进程恢复的安全保证。因此设计只在受信本地进程模型下依赖固定悬停与父端唯一 Resume；内核永久阻塞、同权限恶意操纵不算已证。
2. [CreateFileMappingW](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-createfilemappingw)（Windows 桌面 API）：pagefile-backed 命名映射可由双方打开；同名对象已存在时返回句柄并置 `ERROR_ALREADY_EXISTS`，创建者须拒绝碰撞并关闭自己取得的句柄。默认安全描述符取自 token；不是跨本机恶意同用户进程的认证。固定 16 KiB 两槽和长度/校验帧仅界定用户态序列化与读取量，未证明任意内核调用的绝对完成时间。
3. [Kernel Object Namespaces](https://learn.microsoft.com/en-us/windows/win32/termserv/kernel-object-namespaces)（Windows 会话命名空间）：`Local` 对象位于各登录会话命名空间，同字符串可指不同对象；`Global` 创建有特定权限要求。跨会话 `OpenJobObjectW` 的找不到不能证明旧 Job 消失。
4. [ProcessIdToSessionId](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-processidtosessionid)（Windows 会话 API）：可取进程所属 numeric session ID，失败须查 GetLastError；页面不保证该数在登录会话结束后的唯一性或不复用。因此单存该数不是登录会话化身证明。
5. [GetTickCount64](https://learn.microsoft.com/en-us/windows/win32/api/sysinfoapi/nf-sysinfoapi-gettickcount64)（Vista/Server 2008 及后续）：返回系统启动后计时长度；这是持续时间而非唯一启动纪元 ID，不能用相等/不等证明两个进程是否同一启动。页面亦未给出可作为数据库持久启动身份的唯一性承诺。
6. [System Power States](https://learn.microsoft.com/en-us/windows/win32/power/system-power-states)（Windows 电源状态）：Fast Startup 属 S4，用户会话注销而内核会话保存；休眠/恢复和完全关机不同。不能把墙钟、开机时刻推算、登录会话数或 uptime 作为跨快速启动/休眠的可靠化身证据。

082 既有只读取证见 `Ndocu/results/TASK-082-result.md` 官方依据段（Job 对象、ActiveProcesses、对象命名与 Python monotonic），本轮未重复打开页面。

## D3 最窄候选及决定性未证事实

目标只是在旧 G 租约届满且证据足够时按原合同**折叠全额 W**，不追溯部分退款。若存在可信、跨冷启动/快速启动/休眠且能区分 Windows 登录会话重用的命名空间化身标识，受信 SUP 可在 claim 原活动锁事务中随 G 原子写入 `running_owner_boot_id` 与 `running_owner_session_id`，响应丢失不得创建 Job。恢复持同一活动互斥并读回 G/标识：同化身同会话且无迟到创建者时，对精确 Job `ActiveProcesses=0` 或经明确 `ERROR_FILE_NOT_FOUND` 且可证明最后句柄已消失，才允许以原 W 全额折叠并尝试下一窗；旧 G 迟到 settle/cancel 仍由原 CAS/status/G 保护。跨可信启动化身变化时，仅在官方事实能证前化身所有受控进程已灭后折叠 W；同启动不同会话、旧行空值、标识失真、API 权限错误/未知错误或提交响应不明均失败关闭。

**当前缺一项决定性事实**：可持久且官方支持的 Windows Job `Local` 命名空间化身身份及其跨冷启动、快速启动、休眠、登录会话 ID 复用时的语义。上述六页只给 uptime 与 numeric session ID，未给唯一化身保证；因此两列候选目前不足以批准为安全恢复证明，也不实施迁移/接口。现行 `OpenJobObjectW` 合并错误并失败关闭；本轮没有因此放行任何旧 G。

D1 静态实现使用固定 base Python/固定 `app.worker.supervisor_main`、禁继承句柄、父取进程/线程句柄及创建时间后才 Resume；父在 Resume 前死亡时本代码没有迟到后台线程去 Resume。真实 Windows 中 venv redirector、父死亡/句柄关闭后的悬停进程生命周期、同权限旁路以及任意内核阻塞均未动态验证，不将静态推导写成安全通过。
