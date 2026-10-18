# TASK-084 review-05 独立初判（读运行日志前落笔）

记录时间：2026-09-25 上午窗口；审计窗口：GLM-5.3（原084独立增强审计窗口接续为 review-05；未参与083任何修改，不接管实现或编排）。

## 接触顺序（如实披露）

1. 项目根 AGENTS.md（入口）、公共 docu/AGENTS.MD（本窗重读，规则与 review-04 窗所载一致）。
2. 自身 review-04 基线：Ndocu/evidence/task-084/review-04/{prelog-assessment.md, hashes.txt}、Ndocu/results/TASK-084-result.md review-04 段（自己的前轮结论，作为本增量确认的比较基线）。
3. 卡面冻结三文件 + 083 fixture-completion-06/pre/ 三副本共六项独立 SHA-256 复算（托管 Python 3.13.12 hashlib，只读）：全部 MATCH，见同目录 hashes.txt。
4. fixture-completion-06/{pre/pre-hashes.txt, final-hashes.txt, incremental.diff}。
5. backend/tests/fixtures/task083/focused_unit.py 当前全文（484行）、job_control.py 当前全文（338行，核对 verify_last_handle 与 spawn 实参/身份校验/open_existing 调用点）、offline_unit.py 的 _TestClock/FakeJob/test_05 区段（:58-130/:185-224，05 运行证据适用性所需调用位置）。
6. 用托管 Python 内联 difflib（自写只读比对代码，非实现者脚本）独立比对 pre__focused_unit.py vs 当前 focused_unit.py。
7. **本文件初判在第 6 步完成后、读取任何运行/静态日志（manifest-final.txt、unit-lifecycle-06.log/meta、offline-05-06.log/meta、static-check.txt）之前已成形。**
8. 之后才读上列日志/meta/manifest/静态检查输出；最后读 TASK-083-result.md 当前段（仅作待评陈述，不继承实现聊天）。

## 边界声明

本卡运行额度 0：未运行 AST/import/compile/单元/Job/spawn/PG/Docker/网络/模型/安装/真实配置，未运行任何实现者脚本（static_check_06.py/run_batch_06.py/prep_evidence.py 只读其文本与输出，不执行）。唯一执行的两条命令为托管 Python 内联只读取证：hashlib 哈希复算、difflib 文本比对（均为自写代码、零写入）。源码/测试/迁移/正式docu/公共库/旧证据/Git 零写入。

## 初判正文（读日志前完成）

### 一、diff 完整性与改动范围（独立 difflib 比对结论）

- pre(4a633aff…7a1ca) → 当前(dfaaf814…5259)：+51 行 / −30 行，全部差异操作均落在 StartLifecycleTests 区段内（pre 第57—240行 / 当前第57—261行）；**区段外 head（第1—56行）与 tail（当前第262行起）字节级相等**。EventControlTests、FrameTests、ConfigFactory、Mapping、Process、LauncherTests 及 `__main__` 尾部全部未动。
- incremental.diff 的 hunks 与我独立比对所得差异操作逐块对应（_identity_lines 删除、_run 签名改派生、fake_spawn 派生逻辑新增、fake_windll 基址分离、两测试改用派生断言），diff 忠实反映 pre→post。
- job_control.py / offline_unit.py 两文件 hash 未变（5bc35bf1…/3029a709…），控制器与 05 用例零改动——与 final-hashes.txt 声明一致。

### 二、缺陷一闭合判断：身份从真实 spawn 实参派生、回执/断言同源且字段类型匹配

- **实参索引跨文件核对**：job_control.py:82-84 `create_subprocess_exec(sys._base_executable, "-B", str(fixture), "controller", activity_id, str(generation), run_tag, start_name, …)` → args[4]=activity_id、args[5]=str(generation)="7"、args[6]=run_tag、args[7]=start_name。fake_spawn 注释（focused_unit.py:167-168）与取值（:173-175）与此逐位一致。
- **类型匹配**：args[4] 为 str（控制器 :34 `str(uuid4())`）；`int(args[5])`=7 为 int（:36 固定 `generation = 7`）；args[6] 为 str。回执经 json.dumps/loads 往返：int 7 → 7 → int 7、str → str，与 :97-100 expected 五元组 `("suspended", activity_id, generation, run_tag, job_name(activity_id, generation))` 逐字段同型同值。
- **job_name 同源**：回执用真实导入的 `job_name(identity["activity_id"], identity["generation"])`（纯字符串构造，review-02/03 已核）与控制器 expected 用同一函数同一实参值 → 必然相等。
- **其余协议字段对齐沿 review-04 已核结论**：created_100ns=0 ↔ GetProcessTimes 替身不动 byref _FILETIME（:109-114 stamp=0）；pid=123 ↔ resumed 回执（:133 `("resumed", created["pid"])`）；active_processes=1 ↔ FakeOpened 返回 1（:117-118）。
- **不 patch uuid4、不削弱控制器**：本区段 patch 面仅三处（focused_unit.py:207-209：job_control.ctypes.WinDLL、job_control.asyncio.create_subprocess_exec、job_control.NamedJob）；job_control.py hash 未变，:34-36 随机身份生成与 :97-100 身份校验原样。随机身份 vs 派生回执从"结构性必败"变"结构性必过"是协议数据流对齐（真实 SUP 子进程正是从 argv 接收身份再回执），不是绕过校验。
- review-04 方案比较中本窗（review-04）已裁定方案A（实参派生）优于方案B（patch uuid4）；本轮实施即方案A，与 review-04 修正清单①完全一致。

### 三、缺陷二闭合判断：open_existing 断言改派生身份，失败分支不恒真

- FakeNamedJob.open_existing 记录 `("open_existing", activity_id, generation)`（focused_unit.py:195-196）；控制器 :116 传入其内部随机 activity_id 与 generation=7。
- 成功例断言（:233-234）：`log.index(("open_existing", identity["activity_id"], 7))` —— identity["activity_id"]==args[4]==控制器随机 activity，元组必然匹配；generation 用字面量 7，与 int(args[5])（:36 固定 7）恒等（卡面②即如此规定）。review-04 B1 的"硬编码 identity 查 log 必 ValueError"关闭。
- 分支B（:258）：`assertNotIn(("open_existing", identity["activity_id"], 7), log)` —— receipt="empty" 时 spawn 已成功、identity 已派生，若控制器意外调用 open_existing（传其随机 activity）必被此断言发现，**不再恒真**。review-04 指出的"分支B侥幸恒真、语义错"关闭。
- 分支A（:238-246）：spawn 异常 → identity 保持空 dict，显式断言 `identity == {}`，其后断言全部不引用 identity 字段（close 恰一次/notIn readline/open_process/kill）。失败分支不以错误元组制造恒真断言。

### 四、缺陷三闭合判断：句柄基址分离，原关闭次数/时序断言保留

- fake_windll（:199-205）：`Kernel(base=100 + 100000 * len(kernels))` —— 第一次 WinDLL（starter，job_control.py:48）base=100，第二次（kernel，:57）base=100100。
- 分配面推演：starter 仅 CreateEventW → start_handle=100；kernel OpenProcess → worker_handle=100100、OpenEventW×2 → 100101/100102。区间 [100,101) 与 [100100,100103) 互不相交（间隔 10 万，无碰撞可能）。
- **原断言全部保留**（对照 review-04 要求）：成功例 set_event(start_handle)==1（:226）、close_handle(start_handle)==1（:227）、readline < close_handle(start)（:229）、close_handle(start) < open_process（:231）、close_handle(start) < open_existing（:233-234）——次序语义与 review-04 修正前完全一致；kernel.CloseHandle(worker_handle=100100)（job_control.py:171）与 starter.CloseHandle(start_event=100)（:104）不再撞号混入同一计数。
- 成功例全流程静态推演（替身值逐行映射）：create_event(100) → spawn → set_event(100) → readline → close_handle(100) → open_process → process_times → open_existing(随机activity, 7) → active_processes → open_event×2 → set_event(100101) → readline → job_close → set_event(100102) → proc_wait → wait_object×2 → close_handle(100100) → close_handle(100101) → close_handle(100102)。五条次序断言与三条计数断言在此序列下全部成立；身份校验（:97-100）经派生回执通过。

### 五、静态推演预期（供读日志后比对，不作为运行证据）

- Command 1（`focused_unit.py --failfast StartLifecycleTests` 两例）：预期 2 ok、exit 0。
- Command 2（`offline_unit.py OfflineRepairTests.test_05_…` 单例）：预期 ok、exit 0；TASK083_05_DIAGNOSTIC 行应含 t1>t0、delta_ns=400_000_000、observed=1、window=6、state=settled，imports 内 session.py sha256 应=502a3743…（沿 review-04 carried final-hashes）、offline_unit.py sha256 应=3029a709…（冻结值）。
- 两例为真实控制函数（verify_last_handle / run_once）+ OS 全替身，不是 Windows 实测——静态通过不升级为真实 OS 证据。

## 日志证实记录（读日志后补充）

- Command 1 证实：unit-lifecycle-06.log 两例 ok、Ran 2 tests、OK；meta exit_code=0、2.478099s、项目 venv、cwd=项目根——与第五节静态推演预期（2 ok、exit 0）逐项吻合。
- Command 2 证实：offline-05-06.log test_05 ok、Ran 1 test、OK；meta exit_code=0、0.883416s；诊断行 t0=1e12、t1=1.0004e12、delta=4e8、observed=1、window=6、state=settled、job_events 四步、imports session=502a3743…f16c / offline=3029a709…4c5c——与冻结值逐一吻合，预期全部兑现。
- static-check.txt 34 项 ALL_PASS（单次 0.036s），其中 head/tail 字节级相等、派生索引跨文件核对、无 uuid4 patch、基址 100/100100 分离等关键项与我的独立 difflib/手工核对结论互为印证；该脚本以托管 3.13.12 执行（083 如实登记的偏差），纯结构检查不影响项目 venv 三例有效性。
- manifest-final.txt 的命令文本、预期与两份 meta/log 一致；"Old PASS carried by local invariance"主张与我的区段外字节级相等独立验证一致。
- 083 结果当前段（fixture-completion-06 段）对本轮改动与运行的陈述与我的独立判断一致，无未披露差异；082 批准决定重读核对，原批准边界无变化。
- 最终结论：三缺陷全部关闭、三例证据适用、零未闭合项——详见 Ndocu/results/TASK-084-result.md review-05 置顶段。
