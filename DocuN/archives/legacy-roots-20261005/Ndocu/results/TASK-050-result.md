# TASK-050 PDF 资源监督独立审计结果

## 结论

独立定向审计结论：在本次冻结版本上，`pdf_import` 的实现逻辑满足 TASK-047 要求的 Windows 资源监督主路径，未发现必须阻塞 TASK-052 等后续非发布开发的实现缺陷。它以挂起状态创建进程，先加入 Windows Job Object，再恢复执行；建立限制失败时不降级；超时终止 Job；句柄关闭启用 kill-on-close；输入、页数、文字、输出协议和墙钟均有硬上限；成功结果固定为 `pending_human_review`。

现有通过日志不是与当前代码 hash 绑定的完整执行证据。因此，本报告可以独立给出“代码审计通过、后续开发可继续”的建议，但不能写成“审计者已在当前 hash 和 pypdf 6.17.0 上独立重跑通过”。建议在依赖该安全边界的功能发布或最终验收前补齐一次最小证据封装。最终状态由 Astra 裁定。

## 独立性、范围和操作声明

- 这是 TASK-050 首次实际派发的新 Session。审计者没有接收或读取 TASK-047 执行聊天、推理或执行者自评，也没有读取 `Ndocu/results/TASK-047-result.md`。
- 判断仅依据 `AGENTS.md`、`docu/AGENTS.MD`、原始目标 `Ndocu/tasks/TASK-047.md`、审计卡 `Ndocu/tasks/TASK-050.md`、冻结的 `backend/app/pdf_import/`、`backend/tests/test_pdf_import.py`、两份原始 unittest 日志，以及固定依赖的清单、锁和许可证。
- TASK-052 卡明确禁止修改冻结的 `pdf_import` 核心；本审计未扩大到新增的 `pdf_review`、API、数据库、前端或整库。
- 本次只读检查没有运行测试、没有安装依赖、没有启动 Docker/API、没有修改源码、锁、数据或共享 `docu/`；唯一写入是本结果文件。
- 目标目录没有 `.git`，不能取得提交 hash。以下用逐文件 SHA-256 固定本次检查版本。

## 检查版本 hash

### 规则和目标

| 文件 | SHA-256 |
|---|---|
| `AGENTS.md` | `2b7f6a06417d36ff093a2edbea6c583c981003f8d599f0e2dc41b7b835522aab` |
| `docu/AGENTS.MD` | `312262964fa101a8e9c34d3b51e34c0262c196a5b09b451a02d5139453a6661a` |
| `Ndocu/tasks/TASK-047.md` | `128f62af1134d14c7ac27a2e4d01711c8939b9c388a134affbab9fff57b4c7ac` |
| `Ndocu/tasks/TASK-050.md` | `737f871e20512a9f87e2f48f587d2e0aad5a8ead12ae68a6827f7edcc7c5b449` |

### 冻结实现和测试

| 文件 | SHA-256 |
|---|---|
| `backend/app/pdf_import/__init__.py` | `21a2c9df1669ea4cabd1be77ab3a0b1530669a5c635f9e2c209d4485ce6b9bda` |
| `backend/app/pdf_import/contracts.py` | `12f886da0302cefba30b9511bfc433b7d75e0276e44ec15d5cabf1b030449fca` |
| `backend/app/pdf_import/errors.py` | `9418f0d65ec69336d04e9e5e9e55f79181b9a84f2d2bf2ca6ef98e86751a7033` |
| `backend/app/pdf_import/_windows_job.py` | `797f445f807d7d9264ea33bddb3388b4848b5d01c10498c221b352b24a236425` |
| `backend/app/pdf_import/supervisor.py` | `95f914830a615feb9be45c083b1460874c6bb5db83514f3963470b880a16527d` |
| `backend/app/pdf_import/worker.py` | `bf3ac59ab350eff203f0474781eb266ed1f7d61a6e0ea9bea05ad13f87d251bf` |
| `backend/tests/test_pdf_import.py` | `447d960929f77bdb78975474f65cef6f44e222fccc79077a202ccd19c4ef1238` |

### 依赖和原始证据

| 文件 | SHA-256 |
|---|---|
| `backend/requirements.txt` | `4bd7c5e809a51ed2a5cedd86c584d691ddd7054da680ef33e1fcf6d18849bd7e` |
| `backend/requirements.lock` | `431cb4736b3abfffb447c59b3298a3b29e65bb9eb268c7a67e9985b37f3fa579` |
| `backend/app/pdf_import/THIRD_PARTY_LICENSES/pypdf-6.17.0-LICENSE.txt` | `a97ac230e5f33ef10a5367a850eb01f91f1a0b064e34742c7794d2294557f524` |
| `Ndocu/results/TASK-047-unittest.log` | `fd9ddbc0012c7aa784a1a55ebe976c21c6f5b7996af8e8d547c911f0b2965342` |
| `Ndocu/results/TASK-047-unittest-pass.log` | `8ceef8730802e56ef7fd0f1c5aa024997b88376832db5cecff05e98b9763bb94` |

## 可复用原始证据

- `TASK-047-unittest.log` 保存了一个真实失败阶段：6 个测试均进入执行，7 个错误（含两个 subtest）都落在 `PdfWorkerError: PDF worker exited with code 101`。这说明测试组并非仅被跳过或空跑；但日志自身没有记录当时的代码 hash、命令和根因，不能从本日志单独断言错误 101 的原因。
- `TASK-047-unittest-pass.log` 列出同名 6 个测试全部 `ok`，`Ran 6 tests in 2.304s`，末尾为 `OK`。它覆盖普通两页、损坏、加密、空白/无可提取文字、页数与 UTF-8 文字超界、受控超时进程停止。
- 当前测试代码中的超时用例使用真实 `run_in_job`，只替换 worker 命令；脚本写出实际解释器 PID，超时后轮询并断言该 PID 不再活动（`test_pdf_import.py:80-104`）。这比完全 mock Windows Job API 更有价值。
- 依赖清单和锁都固定 `pypdf==6.17.0`，项目内保留 BSD 类许可证文本。审计对象未发现额外 PDF/OCR/外部解析器依赖。

## 发现及严重度

### M-1 中：通过日志没有绑定当前代码和运行环境，限制独立运行结论

`TASK-047-unittest-pass.log` 没有记录实际命令、进程退出码、`sys.executable`、Windows/Python 版本、运行时 `pypdf.__version__`，也没有记录源码和测试 hash。当前文件时间顺序与“修改后通过”相容，但文件时间不是内容绑定证据。

影响：相同日志可以在源码、测试或虚拟环境变化后继续存在；`PdfImportResult.extraction_method` 又固定写成 `pypdf-6.17.0`（`contracts.py:38`），所以仅凭现有日志不能独立确认通过测试时实际加载的就是 6.17.0，也不能确认它由上表当前 hash 产生。这是证据缺口，不是已发现的实现故障。

最小补证：另开一张只做证据的卡，在不改源码、不安装依赖的前提下，先记录上述源码/测试 SHA-256、Windows/Python、`sys.executable` 和 `pypdf.__version__`，再只运行当前 6 项 unittest 一次，同时保存原始 stdout/stderr、完整命令和 shell 退出码。该补证应在最终安全验收/发布前完成，不需要阻塞 TASK-052 的非发布开发。

### L-1 低：256 MiB 是每进程限制，不是整个 Job 的聚合内存上限

`run_in_job` 设置的是 `JOB_OBJECT_LIMIT_PROCESS_MEMORY` 和 `ProcessMemoryLimit`，同时允许最多 2 个活动进程（`_windows_job.py:115-123`）。因此 `process_memory_bytes=256 MiB` 的含义是每个进程最多约 256 MiB；它不保证整个 Job 的进程合计低于 256 MiB。

反例：在不使用 venv 转发器的解释器下，worker 和它启动的一个子进程可同时各自接近该上限；聚合提交内存可接近两倍上限并另有系统开销。当前命名 `process_memory_bytes` 与此行为一致，且活动进程数和 10 秒墙钟仍有界，所以本项不作为阻塞缺陷。若架构实际想表达“整个解析 Job 共用 256 MiB”，后续实现卡应改用并验证 Job 聚合内存限制，并相应更新契约名称或说明。

### I-1 信息：资源监督不是文件、网络或权限沙箱

Job Object 在这里限制活动进程数、每进程内存并提供 kill-on-close；worker 仍继承运行账户、环境和工作目录权限。若解析库本身发生任意代码执行，Job 不会阻止其读取同账户可读文件或访问网络。`PdfSandboxSetupError` 这个错误名不能据此解释成全面沙箱。

当前冻结代码没有调用 JavaScript、URI、附件提取、网络客户端或外部解析器；worker 的实际 PDF 操作只有从受控临时输入读取 bytes、构造 `PdfReader`、遍历物理页并调用 `extract_text()`（`worker.py:40-87`）。因此“组件没有主动执行 PDF 脚本/链接/附件”的静态要求成立，但这不等于证明对所有恶意 PDF 或 pypdf 漏洞都安全。

## 已验证边界

- 公共入口只接受 `bytes`，不接受用户路径；空输入和大于 5 MiB 的输入在建 worker 前拒绝，非 Windows 明确失败（`supervisor.py:40-53`）。输入只被复制到随机临时目录；源 bytes 不被修改。
- 默认限制为 5 MiB 输入、50 个物理页、2 MiB UTF-8 提取文字、10 秒墙钟、8 MiB 输出协议和每进程 256 MiB；调用方只能在硬上限以内收紧或调整（`contracts.py:8-23`）。
- Windows 进程顺序为 `CREATE_SUSPENDED` 创建、`AssignProcessToJobObject`、`ResumeThread`（`_windows_job.py:132-154`），不存在未入 Job 便先运行 PDF 的窗口。
- Job 同时启用活动进程数、每进程内存和 kill-on-close；默认最多 2 个活动进程，以容纳 venv 转发器与真实解释器。成员进程创建的普通子进程继承同一 Job；没有设置 breakaway 标志。
- 超时后调用 `TerminateJobObject`，随后有界等待根进程；所有路径最终关闭 Job 句柄。创建后尚未成功分配 Job 的挂起进程会单独 `TerminateProcess`（`_windows_job.py:156-177`）。Job 建立、分配或恢复失败均上抛并在监督器映射为 `PdfSandboxSetupError`，没有线程或无界进程回退。
- worker 非零退出、无输出、超大输出、非 UTF-8/非 JSON、未知错误码、页号/页数/警告/文字越界、成功却无可提取文字均在父进程失败关闭（`supervisor.py:74-85,106-153`）。
- 加密、不可读、无可提取文字、页数超界、文字超界分别映射为稳定错误。任何页无文字会带页级警告；全部无文字则整个结果失败，不伪造 OCR 文本（`worker.py:40-78`）。
- 成功结果的提取方法固定为 `pypdf-6.17.0`，状态固定为 `pending_human_review`；worker 不能通过输出协议把状态改成已批准。全局警告还要求人工核对后才能学习使用（`contracts.py:33-39`、`worker.py:79-87`）。

## 未验证及不得外推的边界

- 本审计没有独立重跑测试；现有通过日志也没有与当前 hash/环境做密码学或同一日志封装绑定。
- 没有独立动态验证 venv 转发器、真实解释器和额外孙进程组成的完整进程树。当前超时用例至少验证了被执行脚本的实际解释器 PID 退出；其余子进程覆盖判断来自 Job 配置和继承语义的静态审查。
- 没有证明整个 Job 的聚合内存低于 `process_memory_bytes`；代码明确只提供每进程内存上限。
- 没有文件系统 ACL、低权限令牌、网络隔离、CPU Job 配额、磁盘配额、反病毒、漏洞扫描或全面恶意 PDF 样本验证。墙钟提供 CPU/挂起的外部停止边界，但不能替代这些控制。
- `worker.py` 的 CLI 接受路径参数，但它是未导出的内部入口并由监督器传入随机临时路径。若未来把它直接暴露给不可信调用方，任意路径读写和缺少入口输入大小校验将超出本次已审边界，必须重新审计。
- 未验证 TASK-052 的人工原页核对、候选确认、数据库/API/前端接入，也未验证完整 STEP-005、功能发布或生产部署。

## 阻塞与放行建议

- 建议放行 TASK-052 及其他不宣称发布完成的后续开发；本次没有发现需要修改冻结 `pdf_import` 核心的高/严重问题。
- R-044 可登记为“独立代码审计通过，运行证据有 M-1 限制”；不能登记成审计者独立重跑通过，也不能据此宣称全面恶意文档安全。
- 在最终安全验收或功能发布依赖本资源边界前，按 M-1 做一次最小、同日志封装的证据补充即可。除非补证失败、冻结 hash 变化或产品把 256 MiB 定义为 Job 聚合上限，不建议扩大全库测试或重复已有 6 类验证。
