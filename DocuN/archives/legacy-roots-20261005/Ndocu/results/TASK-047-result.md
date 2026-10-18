# TASK-047 结果：文字 PDF 有界解析组件

- 执行时间：2026-09-14 04:42:12 +08:00
- 关联：TASK-047 / R-041 / STEP-005 局部组件
- 结论：卡内组件及其局部测试已完成；结果只表示有界文字提取候选可供后续接入，不表示 PDF 人工原页核对、资料 API 接入或完整学习主链已完成。

## 调用契约

正式入口为 `app.pdf_import.parse_pdf_bytes(data: bytes, *, limits: PdfImportLimits | None = None) -> PdfImportResult`。入口只接收调用方已经取得并限制的不可变 `bytes`，不接收文件路径；原字节不修改。监督器在自身临时目录写入工作副本，由项目 `.venv` 的独立 Python 子进程调用 pypdf，父进程只接收有限 JSON 协议。

默认和硬上限如下：输入 5 MiB、50 个物理页、提取文字合计 2 MiB（UTF-8 字节）、墙钟 10 秒、输出协议 8 MiB（可配硬上限 16 MiB）、单进程内存 256 MiB（可配硬上限 512 MiB）。Windows Job Object 先以挂起状态创建进程，再设置单进程内存、最多 2 个 Job 内进程及关闭即终止；2 个名额用于 Windows venv 转发器和实际 Python 解释器。Job 建立或分配失败时拒绝解析，不回退到无界线程或普通子进程。

成功结果含总页数、从 1 开始的物理页号、pypdf 原样返回的各页文字、逐页和全局警告，并固定带 `extraction_method=pypdf-6.17.0`、`review_status=pending_human_review`。警告明确说明文字无版面保真保证，且进入学习前必须人工对照原页核对。组件不自动重排、纠字或声称印刷页码/精确坐标。

## 失败和限制

稳定错误码包括：

- `pdf_input_too_large`
- `pdf_invalid`
- `pdf_encrypted`
- `pdf_no_extractable_text`
- `pdf_page_limit_exceeded`
- `pdf_text_limit_exceeded`
- `pdf_timeout`
- `pdf_unsupported_platform`
- `pdf_sandbox_setup_failed`
- `pdf_worker_protocol_invalid`
- `pdf_worker_failed`

加密、损坏、全页无可提取文字、页数/文本超界均拒绝整次结果，不生成替代文本。超时终止本次 Job 内自有进程。worker 不调用网络、外部解析器、链接、附件或 PDF JavaScript；pypdf 的纯文字提取也不会主动执行这些内容。

本边界只是资源监督，不是恶意文档的完整权限沙箱：子进程仍继承当前 Windows 用户的文件和网络权限。复杂布局、表格、阅读顺序、字形映射和语义正确性仍需人工原页核对；OCR、Office、扫描件识别、Linux/cgroup、浏览器原页预览、取消令牌、持久业务状态、替换/跳过及版本切换不在本卡实现或验证范围。

## 实际差异和依赖

- 新增 `backend/app/pdf_import/`：公开契约、错误、Windows Job 监督、子进程提取器和 pypdf 固定许可证副本。
- 新增 `backend/tests/test_pdf_import.py`。
- 仅在 `backend/requirements.txt` 与 `backend/requirements.lock` 末尾追加 `pypdf==6.17.0`，原项目条目不变。
- 未修改 `backend/app/main.py`、`backend/app/materials/`、前端、数据库、Docker 或共享正式设计文档。

项目 `.venv` 精确安装使用 `--require-hashes --only-binary=:all: --no-deps`，固定 SHA256 `5bd827266a21553b74d910e350131a6227b72f2ab4209bf372814b8195fa11c5`。实际安装 `pypdf 6.17.0`，`pip show` 显示无基础依赖、许可证表达式 BSD-3-Clause。许可证原文保存在 `backend/app/pdf_import/THIRD_PARTY_LICENSES/pypdf-6.17.0-LICENSE.txt`。

第一次安装命令尝试通过 `pip -r -` 读取标准输入，本机 pip 在下载前以“Could not open requirements file: '-'”退出 1，未安装内容。确认原因后改为单行临时哈希清单，安装退出 0；未升级 pip，未安装 extra 或其他库，临时清单已删除。

## 测试证据

实际命令：

```text
D:\shspic\project_NO3_RetroLume-agent\backend\.venv\Scripts\python.exe -m unittest tests.test_pdf_import -v
```

最终退出码 0，6 个测试在 2.304 秒内通过：普通两页及物理页号/待核对状态、损坏、加密、空白/无文本、页数及 UTF-8 文本超界、受控超时进程停止。普通/损坏/加密/空白/超界测试使用真实 pypdf 读写或小型自构造 PDF；超时测试用受控睡眠子进程验证真实 Job 终止，不代表恶意 PDF 行为覆盖。

首次测试退出 1，6 类均在解析前返回 worker 退出码 101。最小诊断确认 Windows venv 启动器需要再创建实际解释器，而原 Job 进程上限 1 拒绝了第二个进程；将有限上限修正为 2 后，同一测试组一次通过。失败原始日志为 `Ndocu/results/TASK-047-unittest.log`，通过原始日志为 `Ndocu/results/TASK-047-unittest-pass.log`。按卡内停止条件未运行前端、旧资料套件、全项目测试、真实资料或压力样本。

未覆盖项：5 MiB 输入实测、输出协议畸形/超界、Job API 建立失败、256 MiB 内存命中、非 Windows 拒绝分支、复杂或恶意真实 PDF、浏览器原页核对和业务接入。这些不影响本卡已覆盖的局部行为，但在 API 接入、安全独立审计和完整 FR-001 验收前仍需按各自任务验证。

## 文件 SHA256

```text
21a2c9df1669ea4cabd1be77ab3a0b1530669a5c635f9e2c209d4485ce6b9bda  backend/app/pdf_import/__init__.py
12f886da0302cefba30b9511bfc433b7d75e0276e44ec15d5cabf1b030449fca  backend/app/pdf_import/contracts.py
9418f0d65ec69336d04e9e5e9e55f79181b9a84f2d2bf2ca6ef98e86751a7033  backend/app/pdf_import/errors.py
797f445f807d7d9264ea33bddb3388b4848b5d01c10498c221b352b24a236425  backend/app/pdf_import/_windows_job.py
95f914830a615feb9be45c083b1460874c6bb5db83514f3963470b880a16527d  backend/app/pdf_import/supervisor.py
bf3ac59ab350eff203f0474781eb266ed1f7d61a6e0ea9bea05ad13f87d251bf  backend/app/pdf_import/worker.py
a97ac230e5f33ef10a5367a850eb01f91f1a0b064e34742c7794d2294557f524  backend/app/pdf_import/THIRD_PARTY_LICENSES/pypdf-6.17.0-LICENSE.txt
447d960929f77bdb78975474f65cef6f44e222fccc79077a202ccd19c4ef1238  backend/tests/test_pdf_import.py
4bd7c5e809a51ed2a5cedd86c584d691ddd7054da680ef33e1fcf6d18849bd7e  backend/requirements.txt
431cb4736b3abfffb447c59b3298a3b29e65bb9eb268c7a67e9985b37f3fa579  backend/requirements.lock
```

这些哈希记录的是写本结果前的最终代码、测试、依赖清单和许可证内容。任务根无 `.git`，因此没有提交或干净工作树结论。`docu/CHANGE.MD` 属于 Astra 统一状态登记且不在本卡可写范围，本结果未修改它。

## 后续门槛

下一卡仍需把组件接入资料候选版本、API 和人工核对/原页对照，再验证替换、跳过、历史版本及失败隔离。资源边界和不可信 PDF 处理按 R-041 仍需独立安全审计；本次实现、自测及结果文档不具备独立性，不能替代该审计或 Astra 验收。
