# TASK-098 唯一入口准备决定

2026-10-02 18:58（UTC+8），入口尚未启动。独立初判见initial-assessment.md。

自己的唯一纯计算准备已经通过，offline-preparation/preparation-result.json为原件。命令为backend/.venv/Scripts/python.exe -B DocuN/evidence/TASK-098/offline_preparation.py，退出码0，脚本0.578000秒，外部调用1.101653秒。没有真实CreateProcess、数据库连接、容器start或业务入口。并发不可变发布、覆盖拒绝、创建后身份/发布失败partial交回、配置纯校验、self-pipe及外网早拒绝均满足预期。原始输出在控制台受编码显示影响，UTF-8保存原件正常；未据此重复执行。

真实入口代码已将准备及内层业务/finally保守共用300秒，外层另限120秒收尾，总上界420秒；每项收尾等待受剩余真期限限制。记录器GetProcessTimes也在partial保护内，关闭Job的前置观察失败仍调用原关闭函数。应用GET session先无Origin取得会话，再对活动接口设置本卡同源Origin。旧业务七表仅保存计数/摘要，自己的FK行清理后逐表核未改旧事实。

18:57:57只读核对没有097运行进程、没有18098/55441监听、没有既有run-01目录。前一精确容器inspect为Stopped/Pid0；真实入口内仍核一次，不符合就abort且占入口。专用角色实际权限、会话和库身份只能在已占唯一start后核验，任何不符合均停止，不补DDL或权限。

下一命令唯一为：RETROLUME_TASK098_PERMIT=g7-audit-01，backend/.venv/Scripts/python.exe -B DocuN/evidence/TASK-098/controlled_entry.py --permit g7-audit-01 --business-seconds 300 --cleanup-seconds 120 --sup-limit 2。

当前新增入口/start/SUP/browser/driver/build/provider/付费均0。已有静态重建12.292219秒、初始hash核对0.538167秒、本次准备0.578000秒；已计离线13.408386秒。只读文件阅读与资源元数据检查分列，不伪造成业务尝试。没有使用第二次准备复检额度。

预期与断言见case_run.py和controlled_entry.py。两方准备合法输入后中性屏障推进原参数，所有出站/租约/首槽/Job权威不改。失败后不重启，按实际阶段回传证据缺口；成功也不扩展followup、浏览器、hardstop或真实模型实验。
