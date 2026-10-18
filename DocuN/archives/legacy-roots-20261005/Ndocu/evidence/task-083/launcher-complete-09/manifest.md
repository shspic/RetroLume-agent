# TASK-083 / launcher-complete-09 证据清单（manifest）

日期：2026-09-25；执行窗口：GLM-5.3-Flash（接续原083实现窗口，非独立审计）。
根：D:/shspic/project_NO3_RetroLume-agent；合同：Ndocu/results/TASK-082-work-decision.md（2026-09-24批准记录）+ 本卡（09完整成果）。

## 授权与边界
- 卡面授权：可运行的真实 run_supervised_window→固定SUP→worker 组合验证夹具 + 专用真实PG账本 + 场景A/B/C（D不适用）+ D3 有限事实收敛；范围内夹具/必要修复连做；完成后一次交原084独立增量终审。
- 本卡写入：仅 backend/tests/fixtures/task083/{launcher_control.py, launcher_scenario.py}（新增）与本目录、Ndocu/results/TASK-083-result.md 置顶段。产品源码/迁移/正式docu/公共库/Git/旧证据零写入（hash 冻结与 post 核验佐证）。

## 新增文件（字节副本=交付本体）
- backend/tests/fixtures/task083/launcher_control.py — 外层控制者+批入口（A/B/C1/C2；hash冻结19文件；DB断言；精确清理网）。
- backend/tests/fixtures/task083/launcher_scenario.py — P子进程（c1/c2 父边界屏障；NamedMapping.create/resume/wait 三个真实调用边界包装；DSN读后即pop）。

## 预检与静态（≤3命令批纪律内）
- precheck.py / precheck-output.txt：Docker 29.7.2、镜像 sha256:cf134a76… 在位、127.0.0.1:55438 空闲、venv Python 3.12.10 + psycopg 3.3.5。PRECHECK_OK。
- static_check_09.py（内容并入本目录）：py_compile×2、导入、SessionConfig 不变量、launcher 调用边界文本核对 6 项（main_wait/terminate wait0/sup_exit wait/mapping.create/resume/None账目）。**三次运行**：前两次失败均为检查脚本自身缺陷（needle未去空格、IPC正则转义层级写错），第三次 ALL PASS——如实留档。

## 资源史（4容器，全 Exited(0)/stop 保留/未删除；处置权留编排）
| runTag | 用途 | 结果 |
| --- | --- | --- |
| 20260925-1652 | runner首启 | BLOCKED_BUDGET_EXHAUSTED_BEFORE_BATCH：runner预算算术缺陷（总窗560s vs 要求675s），0场景启动。修正：TOTAL_WINDOW=660、批前检查=540+75。 |
| 20260925-1653 | 批#0（预备） | 批内 scenario A 预备阶段 InterfaceError：asyncio.run 默认 ProactorEventLoop，psycopg 异步需项目 loop factory。0场景启动。修正：build_activity 改 loop_factory=psycopg_compatible_loop_factory。 |
| 20260925-1655 | 批#1（首验） | A/B/C1 通过；C2 失败（确定性缺陷：at_wait 屏障于父端wait进入即触发，早于子端claim；断言见 pending/G0）。SUP 由控制者安全网精确终止、P 树杀兜底、无泄漏（p-evidence-c2-…899644f4 证实 at_wait 已达）。另发现 results.json datetime 序列化 TypeError（exit=1）。 |
| 20260925-1658 | 批#2（复验） | 修正 c2 触发时序（claim+Job含worker的有界轮询）与序列化后重跑。runner 不支持场景参数，实际全批四场景——**全部通过，exit=0，批用时8.80s，all_pass=true，批内hash零漂移**。 |

预算账：真实批 2（≤3）；场景启动 4+4=8（≤12）；P覆盖证据 runTag 维度两轮全留存（c1-d67d4cae/c2-899644f4 + c1-1d809452/c2-43b75769）。

## 最终批（20260925-1658）关键产物
- results.json — 四场景逐项事实（本manifest不复制，直接读）。
- batch-stdout.log / batch-stderr.log / batch-meta.txt — 批进程原始输出与命令（DSN脱敏；批进程环境仅5个白名单变量+DSN）。
- container-inspect-created.json / container-final-inspect.json — 容器身份/标签/端口绑定（127.0.0.1:55438→5432）与最终 Running=false。
- post-run-check.json — 独立收尾核验：4+3容器状态、端口释放、场景启动账、偏差登记。
- d3-sources-and-decision.md — D3 五项新增官方事实 + 恢复决策建议（一列 running_owner_session_id；同号折叠/异号失败关闭；不实施待批）。

## 覆盖与不覆盖（沿卡，不扩）
- 覆盖：A正常完整入口（真实PG认领/关门/结算）、B父级管理截止/无可信子结果、C1父在Resume前退出（悬停不迟到Resume）、C2父在Resume后退出（SUP独立完成自身截止与映射生命周期）。
- 不覆盖/不宣告：不覆盖 Job01—05 旧场景与 PG 六例（各自证据独立在案）；不解决 D3 实施（仅决策）；不签 M-1/STEP008；非独立安全验收（交原084终审）。
- 注入纪律披露：B 的管理截止经 _SuspendedSupervisor.wait 真实调用边界的确定性注入触发（触发前提=claim已提交且业务Job在管，均为真实可观察事实；真实16s截止下SUP结构上必然先完成，非注入无法确定性命中——卡面B授权"确定性控制点注入"即此）。C1/C2 的父死亡经 P 进程内 resume/wait 边界屏障+精确句柄终止实现，无睡眠碰运气。
