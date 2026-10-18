# TASK-084 review-04 独立初判（留证）

记录时间：2026-09-25 00:30—01:10 窗口；审计窗口：GLM-5.3-Flash（原084独立审计窗口接续，未参与083实施）。

## 接触顺序（如实披露）

1. 卡面冻结三文件 SHA-256 独立复算（托管 Python，只读 hashlib）：focused_unit.py=4a633aff…7a1ca、job_control.py=5bc35bf1…980d2、offline_unit.py=3029a709…4c5c，**三值与卡面冻结一致，零漂移**。
2. fixture-repair-04 与 stub-fix-05 两轮 pre-hashes.txt、final-hashes.txt、incremental.diff。
3. 当前三个冻结源文件全文 + 必要直接依赖 backend/app/worker/session.py（run_once 全路径）；windows_job.py 未重读全文（两轮 final-hashes 均 FROZEN_OK d05ca259…，job_name 纯字符串构造沿 review-02/03 结论）。
4. **本文件以下初判在第 3 步完成后、读取任何运行/静态日志之前已成形。**
5. 之后才读：fixture-repair-04/unit-final-01.log+meta、stub-fix-05/unit-lifecycle-01.log+meta、stub-fix-05 静态三尝试日志（static-attempt-01-fail/02-fail/static.log）、两份 manifest-final.txt。
6. 最后读 TASK-083-result.md 置顶两段（待评陈述）、TASK-084-result.md review-03、TASK-082-work-decision.md 批准记录、归档卡 TASK-084-before-review04-20260925.md。未读实现聊天，未运行任何实现者脚本。

## 初判正文（读日志前完成）

### A. 生命周期替身 vs 真实 verify_last_handle 逐步映射

- job_control.py:34-35 verify_last_handle 自生成 `activity_id=str(uuid4())`、`run_tag="job-death-"+uuid4().hex[:8]`；generation 固定 7（:36）。
- 夹具 _identity_lines（focused_unit.py:68-77）回执硬编码 activity="11111111-1111-1111-1111-111111111111"、run_tag="lifecycle-unit"、job_name=job_name(固定activity,7)。
- job_control.py:97-100 身份校验 expected=(phase, **随机activity**, 7, **随机run_tag**, job_name(随机activity,7)) vs created=（phase, **固定activity**, 7, **固定run_tag**, job_name(固定activity,7)）→ phase/generation/pid/created_100ns 匹配但 activity_id/run_tag/job_name 三字段**必然**不匹配。
- **裁定：随机身份 vs 固定回执是确定性根因（结构性必然，非概率、非环境）。**
- spawn 实参携带完整身份：job_control.py:82-84 args=(exe,"-B",fixture,"controller",activity_id,str(generation),run_tag,start_name)，索引 4/5/6 即身份三元组。
- 产物回执 created_100ns=0 与 GetProcessTimes 替身（不动 byref _FILETIME，全零 stamp=0）对齐；resumed 行 pid=123 与 created["pid"]=123 对齐——此两处夹具已对齐，无缺陷。

### B. 静态新发现（读日志前已定位，与根因 A 同流程）

- B1：成功例 focused_unit.py:215 `log.index(("open_existing", activity, 7))` 用**硬编码** activity 查 log，而 FakeNamedJob.open_existing 记录的是控制器内部随机 activity（job_control.py:116）→ ValueError（测试 ERROR）。与 A 同源，修 A 时必须同步改用派生身份；分支 B（:237 assertNotIn）因 open_existing 未被调用而侥幸恒真，语义仍错。
- B2：starter 与 kernel 是两次独立 fake_windll 调用（kernels[0]/kernels[1]），两个 Kernel 各自 `_next=100` 起编号：start_event=100（starter）、worker_handle=100（kernel.OpenProcess）。成功例 finally 中 kernel.CloseHandle(worker_handle=100)（job_control.py:171）与 starter.CloseHandle(start_event=100)（:104）混入同一 log → `log.count(("close_handle", start_handle))==1`（focused_unit.py:210）必败为 2。**修 A 后成功例必撞此断言**。最小修法：两个替身 Kernel 分配不相交句柄基址。

### C. 已检查并排除的疑点（避免误报）

- partial 包装覆盖面：job_control.py:49-71 赋值面 8 个 API（CreateEventW/SetEvent/CloseHandle/OpenProcess/GetProcessTimes/OpenEventW/WaitForSingleObject/TerminateProcess）与夹具 8 个 partial 一一闭合；SetEvent/CloseHandle 在 starter/kernel 两实例上均被赋值，partial 在实例上各自包装，无遗漏。
- _new_event_or_reject 的 ctypes.set_last_error(0)（job_control.py:24）先行执行 → 纯 Python CreateEventW 不触碰 last error → get_last_error() 确定性返 0，183 误判碰撞不存在，无需补 patch。
- asyncio.wait_for 用事件循环内建时钟（OS monotonic），不受模块属性 patch 影响；替身路径全部瞬时完成，无超时风险。
- patch("job_control.ctypes.WinDLL") 实为真实 ctypes 模块属性替换，with 结束恢复；job_control.asyncio.create_subprocess_exec 同理，asyncio 内部机制不调用它，无越界误伤。
- time 引用：job_control 顶层 import time 仅真实只读（deadline/remaining），替身下 20s 预算充足。

### D. 修复方案比较（都保留全部身份校验，不取消任何校验）

- 方案A（推荐）：夹具 fake_spawn 从 spawn 实参 args[4]/[5]/[6] 派生 activity_id/generation/run_tag，动态构造 created/resumed 行；_run 返回派生身份供断言使用。与真实协议数据流一致（真实 SUP 子进程从 argv 接收身份并回执），不耦合源码内部 uuid4 调用次数/顺序。
- 方案B（083 置顶段提议）：patch("job_control.uuid4") 确定性序列 + 同步 _identity_lines 常量。可行但测试耦合源码两处 uuid4 调用顺序与返回值形状（str() 包裹 + .hex 属性），源码微调即碎。
- 两方案均只涉 focused_unit.py；job_control.py / offline_unit.py / 产品源码零改动。

### E. 04 真实控制器（job_control.verify_last_handle）资源纪律预判

- Start 持有至身份回执后释放（:103-105，start_released 防重标志 + finally :151-154 恰一次互补）——04 轮已按 review-03 竞态裁定修复。
- 收尾保留原 deadline（:163）与精确身份（kill 用 proc 对象、Terminate 用精确 worker 句柄）。
- 观察 Job 释放时点：:135-136 父观察句柄先关、parent_job=None 后才 SetEvent Exit，SUP 独占最后句柄场景保持；finally 无二次 close。
- 预判备注（非阻塞）：start_event 创建于 :56、try 起于 :80，:57-71（第二个 kernel 构造/argtypes 赋值）若抛异常则 start_event 无 finally 覆盖——但该段为确定性 ctypes 属性赋值，真实不可触发；:88-92 except 内 proc.kill()/wait 无独立保护，kill 失败会覆盖原异常——低概率备注级。

## 日志证实记录（读日志后补充）

- 根因 A 被运行日志证实：stub-fix-05/unit-lifecycle-01.log 首例 `AssertionError('Job/G/runTag身份不匹配')`，Ran 1 test（failfast），与初判路径逐字吻合；04 轮 unit-final-01.log 两例 AttributeError（argtypes）发生在 :49-71 赋值行，未触及身份校验——两轮失败点互补，均与初判映射一致。
- 静态三尝试：attempt-01 assigned=[]（检查脚本 ast.AsyncFunctionDef 漏扫）+ docstring 误判 FAIL，源码中间态 144335c4（44 diff 行）；attempt-02 assigned=8 但 docstring 仍 FAIL、同一中间态；attempt-03 ALL_PASS、最终 4a633aff（40 diff 行）。中间态未运行未交付。检查脚本缺陷两次，不丢弃最终证据。
- 083 置顶段对首例的定位陈述与本初判一致；其提议方案 B 可行，本窗裁定方案 A 更稳（理由见 D）。
