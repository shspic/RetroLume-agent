# TASK-052 结果：PDF候选、逐页原图核对与确认准入接续

- 执行时间：2026-09-14 +08:00
- 当前编号：TASK-052 / R-046 / STEP-005
- 父映射：接续未完成的 TASK-049 / R-043；未伪造 `TASK-049-result.md`，本结果承接其原目标、允许范围和未完成项。
- 结论：卡内候选版本、受控原件读取、完整逐页确认门禁、用户补充身份、工作台核对界面及限定验证已完成。结果不表示真实 PostgreSQL 迁移/事务、真实浏览器 PDF 渲染与乱序交互、047 安全审计、后续检索或整个 STEP-005 已完成。

## 已实现行为

PDF 和 TXT/Markdown 共用原有逐文件上传入口。PDF 仍按流式 5 MiB 接收上限保存原件，再通过线程池调度冻结的 `parse_pdf_bytes`；该函数内部仍使用 TASK-047 的受限子进程，不把普通线程当超时终止。解析成功只创建 `pending` 候选，返回不可变 `version_id`、SHA-256、物理页数和提取方法；首次 PDF 不进入 `/api/materials`，替换期间旧活动版本继续可用。解析或候选保存失败不会切换当前版本，已落位而未引用的内容寻址原件按既有存储规则保留。

确认事务按来源后候选的顺序加锁，并同时比较上传时的 `expected_version` 与 `expected_revision`。确认版本不一致、候选已处理或当前资料在其间被更新均返回 409，不覆盖第三方更新。完整页列表由服务端验证：空列表、重复页、越界页、缺页及未明确勾选均拒绝；只有 1 到 `page_count` 的全部物理页通过后，事务才保存逐页核对记录和可选用户补充、切换 `current_version` 并增加来源修订号。跳过只把候选标为 `skipped`，保留原件和旧活动版。

`003_pdf_review.sql` 在原 001 历史之上把资料版本格式扩展为 `pdf`，新增候选、逐页原始提取、逐页确认和用户补充表及版本/页外键。当前版仍是唯一可用版；候选表与分页表不成为资料列表或后续活动的可用回退。迁移文件只准备，未在用户数据库执行。

稳定的后续查询契约不把 PDF 拼成 TXT 行号：已确认 PDF 的 `/api/materials/{source_id}/content` 返回 `material.version_id`，每页返回同一 `version_id`、`physical_page`、`raw_text` 和 `identity=pdf_extracted_text`；每条补充另带 `version_id`、`physical_page` 和 `identity=user_supplement`。`query_ready=true` 只会出现在当前且已确认的 PDF。接口不读取或 UTF-8 解码 PDF 原字节，也不插入可被误当原文的位置分隔文字。

## 实际接口

| 方法与路径 | 行为 |
| --- | --- |
| `POST /api/materials` | TXT/MD 保持原行为；PDF 保存原件、有限解析并返回待核对候选。PDF 替换同时要求当前版本及修订号。 |
| `GET /api/pdf-candidates` | 只列出待核对候选，包括首次尚无活动版的 PDF。 |
| `GET /api/pdf-candidates/{candidate_id}` | 返回绑定候选版本的完整物理页列表及 pypdf 原始提取文字，固定 `query_ready=false`。 |
| `GET /api/pdf-candidates/{candidate_id}/original` | 本地会话保护、内容寻址校验后返回 `application/pdf` 字节，不接受文件路径。 |
| `POST /api/pdf-candidates/{candidate_id}/confirm` | 接收绑定 `version_id` 的完整逐页核对列表，事务 CAS 后激活。 |
| `POST /api/pdf-candidates/{candidate_id}/skip` | 保留原件及旧活动版，只关闭该候选。 |
| `GET /api/materials/{source_id}/content` | TXT/MD 仍返回行段；当前 PDF 返回已确认的物理页/原始提取/用户补充身份。 |
| `GET /api/materials/{source_id}/original` | 按来源与当前版本 CAS 返回已激活 PDF 原件。 |

所有上述接口沿用本地 Origin、Host、随机会话令牌和 `no-store` 保护。错误信息为中文；实现不记录原始字节或正文日志。

## 前端逐页核对

工作台现支持选择 PDF，并把返回状态显示为“待核对”。候选区并列显示当前物理页 canvas 与该页原始提取文字，提供上一页/下一页、逐页明确勾选、每页独立用户补充、跳过和最终确认。只有每个物理页均成功渲染且被明确勾选后确认按钮才可用；页面渲染开始或失败会撤销该页勾选，不能自动确认。

PDF.js 只用分页 canvas API：不加载完整 viewer、注释/活动链接层、附件或 XFA 界面；文档只从会话 API 取得的内存 bytes 加载。worker 由 Vite 打包为本地同源资源；`enableXfa=false`、`useSystemFonts=false`、`useWorkerFetch=false`，关闭范围/流式/自动外取，并把单图和 canvas 都限制为 4,000,000 像素。切换候选销毁 loading task/worker，切页取消旧 render task。固定版本的类型中已不存在旧 `isEvalSupported` 参数，实际构建文件也未发现该旧 eval 路径。未提供 CMap/标准字体远端 URL；需要缺失资源而无法渲染的 PDF 会明确失败并阻止该页确认。

## 依赖安装与许可

只执行一次：

```text
npm.cmd install --save-exact --ignore-scripts --no-audit --no-fund pdfjs-dist@6.3.289
```

退出码 0，输出 `added 3 packages in 32s`。`package.json` 精确固定 `pdfjs-dist: 6.3.289`；锁元数据来源为 `https://registry.npmjs.org/pdfjs-dist/-/pdfjs-dist-6.3.289.tgz`，integrity 为 `sha512-ZHjSVpDa3D6izMq8/04lvkhkATUmL9px6ChPaXc1k6nU2Mrhlg1/7F0bdUqCwUjw3NsPTfPZsMDUU6ZIcRaeQw==`，Node 要求 `>=22.13.0 || >=24`，本机 Node 24.15.0/npm 11.17.0。React 19.3.0、react-dom 19.3.0、TypeScript 7.0.2、Vite 8.3.0 均保持原版本。

标准 npm 解析同时安装 PDF.js 声明的可选 `@napi-rs/canvas@1.0.9` 及当前 Windows 二进制包，两者锁元数据为 MIT；未使用会删除既有 Vite/Rolldown 平台包的全局 `--omit=optional`，未手工改锁或制造假包。浏览器构建使用 `pdfjs-dist`，不调用 Node canvas。PDF.js 为 Apache-2.0，完整许可证从实际安装包原样复制到 `frontend/src/pdf/THIRD_PARTY_LICENSES/pdfjs-dist-6.3.289-LICENSE.txt`；安装包自身许可证仍保留在项目本地 `node_modules`。

来源：固定发布 `https://github.com/mozilla/pdf.js/releases/tag/v6.3.289`，固定 NPM 元数据 `https://registry.npmjs.org/pdfjs-dist/6.3.289`。本卡未调用 CDN、模型、Docker、真实数据库、真实资料或付费服务。

## 限定验证

局部 HTTP/领域组只执行一次：

```text
D:\shspic\project_NO3_RetroLume-agent\backend\.venv\Scripts\python.exe -m unittest tests.test_pdf_review -v
```

退出码 0，6 个测试在 0.460 秒内通过：首次 PDF 待核对且不可激活；缺页/重复/越界拒绝及用户补充身份；陈旧确认冲突；跳过与解析失败保留旧版；原件仅经会话受控端点；已确认 PDF 转 TXT/MD 的 CAS。解析结果和仓储为合成契约替身，不代表真实 pypdf 重测或真实 PostgreSQL 事务通过。日志有既存 TestClient/httpx2 弃用提示，不影响这组断言。

前端首次构建退出码 1，只发现固定 PDF.js 6 类型差异：旧 `isEvalSupported` 参数不存在，销毁入口属于 loading task。依据本地类型与构建文件修正一次后重跑：

```text
npm.cmd run build
```

最终退出码 0：TypeScript 检查通过，Vite 8.3.0 共转换 21 个模块，并产出本地 `pdf.worker.min-*.mjs`。构建有主 JS 超过 500 kB 的警告；这是体积风险，不影响本卡编译结果，后续若首屏性能实测不达标再评估动态加载。

按卡停止：未重跑 TASK-047 解析器、TASK-045 后端、全项目套件；未执行 003；未使用真实 PostgreSQL；未做真实浏览器原页渲染、快速乱序切页/切候选、复杂字体/CMap PDF、键盘/焦点或真实混合批次集成。这些仍由后续真实 PG 与浏览器集成卡验证，不能据本结果标为通过。TASK-050 对 `pdf_import` 冻结核心的独立安全审计仍是单独门槛。

## 冻结范围与证据

`Ndocu/evidence/task-052/frozen-scope-hashes.txt` 显示 TASK-047 的 `backend/app/pdf_import/` 7 个文件以及后端 requirements 两个锁文件 SHA-256 与 `TASK-047-result.md` 完全一致；本卡没有修改冻结核心或后端锁。`activities/` 和 002 迁移属于 TASK-051 独占，本卡未写。

- `Ndocu/evidence/task-052/file-hashes.sha256`：本卡代码、迁移、前端源码、许可证和前端锁哈希。
- `Ndocu/evidence/task-052/evidence-hashes.sha256`：安装、测试、两次构建、依赖记录、冻结范围及文件哈希清单自身的哈希。
- `Ndocu/evidence/task-052/npm-install.log`、`pdf-review-tests.log`、`frontend-build.log`、`frontend-build-pass.log`：原始输出。
- `Ndocu/evidence/task-052/dependency-record.txt`：固定版本、来源、integrity、许可与实际可选依赖记录。

项目根没有 `.git`，因此没有提交、差异或干净工作树结论。正式 `docu/CHANGE.MD` 由 Astra 统一登记且不在本卡允许范围，本结果未修改它。
