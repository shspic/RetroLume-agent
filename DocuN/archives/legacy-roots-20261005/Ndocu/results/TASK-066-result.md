# TASK-066 结果（R-060，父TASK-065，关联064/061、FR-001、DR-003、NFR-002）

- 执行者：Work Buddy / GLM（GLM-5.3-Flash），B档，新会话，与卡内路由一致。
- 日期：2026-09-21（本机 GMT+8）。
- 建议状态：**完成（离线交付）**。未运行 Docker/应用/浏览器/数据库（本卡不授权真实运行）；语法通过不等于运行正确，已按卡补显式依赖核对。

## 1. 实际文件与差异

只改 `tests/task054_pdf_materials_integration.mjs`（修改前副本与 hash：Ndocu/evidence/task-066/）。差异共两类：

1. **pdfBuffer 作用域修正（065 s4 ReferenceError 根因）**：`const pdfBuffer = makePdf(["PDF FIRST PAGE", "PDF SECOND PAGE"]);` 从浏览器 try 块内（原 :1123）提升到 main 局部作用域（`let token = await sessionToken();` 之后），s2/s4/s6 共用同一合成两页PDF；**未用 globalThis 补洞**。s4/s6 引用变量的声明/赋值路径已核对，无同类未定义残留。
2. **新增 `--remaining-s4-s6` 显式入口**（main 的 token 获取之后）：
   - 模块级参数解析：未知参数 `console.error` 后 `process.exit(2)` 明确拒绝，不静默跳过；无参数=全套七场景，行为不变。
   - 剩余模式分支：全新合成库+原监督机制（ensureContainer/ensureMigrations/startAppBounded 原样），**不启动 Edge、不执行 s1a/s2/s3/s1b/s5**；浏览器整段用 `else` 包裹（块内代码保持原缩进、逐行零改动）。Edge 存在性检查改为仅全套模式强制。
   - API 最小准备（失败即抛出、失败关闭，走真实产品接口，不直写数据库、不复用065库）：上传同一 pdfBuffer → `POST /api/pdf-candidates/{id}/confirm`（pages 均 reviewed，第2页 `supplement:"第二页用户补充"`）→ 回查资料列表与 content，核对 query_ready/pages=2/第2页 supplements 恰1条且 identity=user_supplement、text、physical_page=2；成功后 `globalThis.__pdfRow = prepRow`（与全套模式 s3 同一通道，s4/s6 使用同一真实 pdfRow）。准备仅此一项，不重做前五场景边界矩阵、不冒称再次验证。
   - 摘要：writeSummary 各路径（4个正常路径+catch路径）追加 `...SUMMARY_MODE`（mode/selected/not_selected）；浏览器字段改为按模式：剩余模式 `{started:false, elapsed_ms:0, version:null, note:"剩余模式未启动浏览器（准确记录，非异常/遗留）"}`；成功 outcome 剩余模式为 `passed-remaining-s4-s6`，console 输出 `REMAINING PASS (s4/s6 only; overall verdict by Astra)`，不冒称全套通过。s4/s6 断言一条未删；未选场景不会出现 scenario 行（不会标 passed）。
   - 未变更：容器唯一名/镜像/资源/端口/停止条件、10分钟总窗、监督与归属、47条业务断言、六类语义。

## 2. 变量依赖表（离线静态核对，两模式逐项）

| 变量 | 全套模式来源 | 剩余模式来源 |
|---|---|---|
| pdfBuffer | main 局部 const，token 后生成一次 → s2（UI上传）/s4/s6（API raw 体） | 同一 main 局部 const → 准备/s4/s6（API raw 体） |
| pdfRow | globalThis.__pdfRow ← s3 设置（UI确认后回查）；s4 前 :1289 读取 | globalThis.__pdfRow ← 剩余准备设置（API上传+确认+回查核对响应后才进入 s4/s6）；同一 :1289 行读取 |
| newer TXT（s6 读取） | s4 内创建（POST /api/materials?filename=newerName&source_id=old.id…） | 同一 s4 代码路径原样创建（s4 在剩余模式照常执行） |
| pending 候选（s6） | s6 内创建（source_id=pdfRow.id…） | 同一 s6 代码路径 |
| token | main `let token=sessionToken()`；s6 重启后闭包内重新赋值 | 同一来源；s6 同样重启后重新赋值 |

核对结论：s4/s6 的直接依赖在剩余模式下全部有真实来源，无历史 ID、无未赋值全局、无 globalThis 补洞；无"修一处再暴露同类未定义"的残留引用（grep 全文 pdfBuffer 共 5 处引用均落在 main 作用域内）。

## 3. 47条断言保留核对

- 空白不敏感 diff（diff-check.txt）：55 行变更全部为本卡事项（Edge条件化、pdfBuffer移动、剩余分支、if/else包裹2行、browserSummary、4+1个 writeSummary、PASS行、参数块）；**七场景块内部无任何一行出现在差异中**。
- assert 计数：pre=47 → current=52；+5 全部为剩余模式准备断言（prep*），场景内 47 条业务断言未增未删。

## 4. 验证记录（B档一次离线批次）

```
node --check tests/task054_pdf_materials_integration.mjs  → exit 0（一次通过，无需复检；Node v24.15.0）
空白不敏感 diff：55 行，全为本卡事项；场景断言零差异（Ndocu/evidence/task-066/diff-check.txt）
未运行主脚本/容器/应用/浏览器；未复现065旧错误。
```

- hash：修改前 `1e2e86e6f60b949f917a645881cd3e0f5c53a4ee8ed01b8fee29d5f96377cd01`（与卡一致，核对后才改）；修改后 `130a5bc9998bb8b2be049ebbd44c9d34b13518c050900c8b36295557121ff8e2`。

## 5. 未验证 / 风险

- **剩余模式与全套模式的运行行为均未验证**（本卡不授权真实运行）。剩余模式准备断言依赖的接口形状已对照 backend/app/pdf_review/contracts.py（ReviewPage.supplement 支持）与 materials/api.py（PDF 上传走 create_pdf_candidate 返回 pending）只读确认，但未实跑。
- 风险：若确认接口对 supplement 的响应结构或上传返回结构与只读核对结论不符，剩余模式准备会失败关闭（不会伪通过）；此时由运行卡暴露，修码属后续卡。
- 065 五项通过证据保留有效；本卡不重测、不变更其结论。

## 6. 文档建议 / 下一步

- 建议 Astra 登记 TASK-066"已返回/完成（离线）"，冻结新 hash 后**另出一次 s4/s6 运行卡**（命令：`node tests/task054_pdf_materials_integration.mjs --remaining-s4-s6`；065 运行次数已用尽，本卡未续跑）。
- 运行卡验收注意：该模式成功仅称"剩余场景通过候选"，整体判定由 Astra 合并 065（s1a/s2/s3/s1b/s5 passed）与本轮证据。
- 无必须人工操作。
