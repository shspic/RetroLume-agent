# TASK-083 D3-10 验证预算与资源账
- 执行者：Codex desktop / GPT-6（可见标签；具体后缀未核实）。
- 离线：最多3命令批、累计5分钟、单命令60秒。
- 真实：最多3批（首次+两轮有因修正）、Windows场景启动≤12、PG测试进程≤3；场景≤30秒、一般命令≤60秒、纯PG命令≤120秒、每批≤10分钟并留60秒收尾；全部真实运行及资源操作累计≤30分钟。
- 资源：只允许1个新容器，固定镜像 sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f，127.0.0.1:55439。
- 环境/runner前置尝试计入账；失败保留独立attempt目录；runner进程失去口令后不得再创建容器。
- 预列：新D3迁移空/旧行与CHECK；claim/恢复PG；纯单元身份/错误码/顺序/丢响应；一个旧Job消失后经固定SUP与真实PG接续的Windows合成场景。
- 首次真实批：尚未启动。
实际首验场景：migration_empty、migration_old、migration_rollback、ledger_new_g、ledger_exhausted、windows_recovery（固定 run_supervised_window→可信 SUP→idle worker）。
离线批：01 系统解释器缺 pydantic（环境错误）；02 项目 venv D3 6项、旧 Protocol 2项、offline 3项通过；03 最终语法、D3 6项、offline 05、精确 diff check 通过。累计离线三命令批。
runner 一次进程持随机密码；真实批最多3次，修正只选失败受影响部分；Windows场景每批最多1次，PG测试进程每批1个。

## 真实资源前置尝试（当前结论）
- 一次预检通过：Docker server 29.7.2、固定本地镜像、127.0.0.1:55439 空闲。
- 创建唯一容器 1086a37d40c34841d373487c10b278c5cfb771b81af7d70251fcb260c69421f0，run=20260925-191110；配置/标签/镜像/端口均按卡。镜像声明的匿名 PG 数据卷出现于 Mounts；首版 runner 错把“无宿主挂载”检查写成 Mounts 必须为空，资源核验前置失败。
- 原 runner 进程 7.859 秒退出，首次真实测试批未启动：PG 测试进程 0、Windows 场景 0、真实修正复验 0。随机口令只在原 runner 内存中，现已不可安全复用；遵守卡面停止，不重建或重新启动容器，不从容器取回口令。
- 原 runner 记录 cleanup_incomplete；随后读取精确 ID 与标签确认归属，docker stop 同 ID exit=0，inspect Running=false；容器及匿名卷保留。见 cleanup-after-identity-check.txt。
- 首版 runner 原字节、哈希保存在 attempt-00-resource-check；当前 runner 仅修正允许镜像声明匿名卷的检查及 stop 参数，未经运行。
- 真实 PG/Windows 恢复与006事务证据未取得；原084独立审计尚未启动，M-1/STEP008不得据此完成。

## 2026-09-25 替补容器接续（新裁定，当前事实）
- 用户粘贴裁定明确授权替补1容器，使D3累计上限为2；原容器1086a37d...保持停止。替补run=20260925-195448，ID=85242648b70dc11839a93de29a51bc7e492390d8ad479036c141f37b26f4f6a7。
- 所有新原始证据在replacement-20260925-195448/；旧attempt-00/runner-log/runner-state/container-created原文件未覆盖。as-run runner SHA256=56e698a7f98b2732596153c26247a41e017420fc4c7e2af9d8d06ac80435ce8e。
- 本次runner单调计时81.765秒，包含预检、资源创建、就绪、一次PG测试子进程、等待修正信号及stop。加原前置7.859秒及其后精确收尾，资源累计仍低于30分钟；容器数量已达硬上限2。
- 替补预检通过：固定镜像和镜像声明匿名/var/lib/postgresql/data卷、端口空闲；新卷CreatedAt与本轮创建相符、无HostConfig宿主bind/mount；PG身份为retrolume_task083_d3/task083_d3/容器内5432，宿主127.0.0.1:55439绑定已核。
- attempt-01：唯一真实PG测试进程PID31624、创建时间134348108976985801；exit1、0.891秒、stdout仅schema(empty)相位；实际006空表迁移已执行，随后SQL按预期对-1返回CheckViolation，但夹具误捕获psycopg.CheckViolation导致AttributeError。其余上界/旧行/回滚/claim/Windows均未运行，Windows启动0。失败schema task083_d3_empty_0b5945b9保留。
- 夹具将异常路径修为psycopg.errors.CheckViolation，最终hash=5f256503807b8945fbe4381466f22fb6be735d5ebcaa3d8d99bdfc69b0289651；仅修改测试，尚未复验。
- 同一runner收到attempt-02.go内容migration,ledger,windows，但复验白名单遗漏该全量选择；在创建第二测试进程前以invalid correction selection退出。attempt-02未创建，复验实际0。此后runner精确核ID/标签，docker stop exit0、inspect Running=false，cleanup_incomplete=false；替补容器及匿名卷停止保留。
- runner白名单已补全（hash=39e5917e0173aced0391f9729a4a3ce2f492ed41b8bb2c41e7cd205cc735a27f），仅为未运行候选。原runner进程已退出，口令不可安全复用；不得读容器口令、接管或创建第3容器。
- D3所要求的完整真实PG事务与Windows旧Job恢复证据仍未取得；原084独立审计不提前启动，STEP008/M-1及one_call不宣称完成。
