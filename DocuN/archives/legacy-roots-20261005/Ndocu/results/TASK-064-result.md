# TASK-064 结果（R-058，父TASK-063，关联061/059/052、FR-001、DR-03）

- 执行者：Work Buddy / GLM（GLM-5.3-Flash），B档，与卡内路由一致。
- 日期：2026-09-21（本机 GMT+8）。
- 建议状态：**完成（夹具离线通过）**。仅消除谓词误报；六业务场景仍未运行，真实运行卡另出。

## 1. 结论与根因

TASK-063 exit1 的直接根因确认为：`tests/task054_pdf_materials_integration.mjs` 旧谓词（修改前第883行）要求 `pdf_review_candidates` 的同一 CHECK 同时含 `'confirmed'`、`'skipped'`、`decided_at`；而 003 固定 DDL 在 PostgreSQL `pg_get_constraintdef` 导出中是两条独立 CHECK：

- `pdf_review_candidates_status_check`：`CHECK ((status = ANY (ARRAY['pending'::text, 'confirmed'::text, 'skipped'::text])))`
- `pdf_review_candidates_check`：`CHECK ((((status = 'pending'::text) AND (decided_at IS NULL)) OR ((status <> 'pending'::text) AND (decided_at IS NOT NULL))))`

旧谓词因此对正确迁移必然误报。本次只改该谓词核对逻辑，未改任何业务 DDL。

## 2. 实际文件与差异

| 文件 | 动作 |
|---|---|
| tests/task054_pdf_materials_integration.mjs | 修改：仅2处——新增1行 `import { candidateConstraintProblems } from "./task064_candidate_constraints.mjs"`；将原第883行谓词替换为 `problems.push(...candidateConstraintProblems(cons));`（含2行注释）。diff 已核对，**47条业务断言与六场景块零变化** |
| tests/task064_candidate_constraints.mjs | 新增：纯函数模块（主脚本与离线检查共用同一实现）。对约束 def 做有限空白规范化（连续空白折叠为单空格）后与固定导出结构**精确比对**；值域与一致性分别核对、不要求同处一条 CHECK；未知表示、关键词拼凑、IS NULL/IS NOT NULL 反转一律拒绝 |
| tests/task064_candidate_constraints.test.mjs | 新增：node:test + node:assert/strict 离线4例，无新依赖；复用 063 原始结构JSON（只读），反例仅在内存副本构造 |
| Ndocu/evidence/task-064/ | 新增：pre-task054_pdf_materials_integration.mjs（修改前副本）、pre-hash.txt、verify-log.txt（实际命令与退出码）、diff-and-posthash.txt（diff与新旧hash） |
| Ndocu/results/TASK-064-result.md | 新增：本结果文档 |

未触碰：业务源码、迁移、其他结构校验、旧证据、docu 正式文档、Git；未运行主脚本、未查询/启动 Docker 或任何进程、未联网、未读凭据。

## 3. hash 记录

- 主脚本修改前 SHA256：`12888be4d3faa2b8c583308301e0e2f370ee964c63a048314b4b58c9df5eb493`（与卡内给定一致，已核对后才修改）
- 主脚本修改后 SHA256：`1e2e86e6f60b949f917a645881cd3e0f5c53a4ee8ed01b8fee29d5f96377cd01`
- tests/task064_candidate_constraints.mjs：`（见 Ndocu/evidence/task-064/diff-and-posthash.txt）`
- tests/task064_candidate_constraints.test.mjs：`（见 Ndocu/evidence/task-064/diff-and-posthash.txt）`

## 4. 验证记录（单批，2026-09-21T09:20:44+08:00，总时长<1秒，上限60秒内）

实际命令（node 为受管 22.22.2）与退出码（证据：Ndocu/evidence/task-064/verify-log.txt）：

```
node --check tests/task054_pdf_materials_integration.mjs      → exit 0
node --check tests/task064_candidate_constraints.mjs          → exit 0
node --check tests/task064_candidate_constraints.test.mjs     → exit 0
node --test tests/task064_candidate_constraints.test.mjs      → exit 0
```

4例结果（node --test TAP：tests 4 / pass 4 / fail 0）：

- a 原始真实清单（063原始结构JSON constraints）通过局部谓词：**通过**
- b 去掉 status 值域约束（内存副本移除 pdf_review_candidates_status_check）→ 仅报值域缺失：**失败（符合预期）**
- c 去掉 decided_at 一致性约束（内存副本移除 pdf_review_candidates_check）→ 仅报一致性缺失：**失败（符合预期）**
- d pending分支 IS NULL 与非pending分支 IS NOT NULL 反转（内存副本替换def）→ 被拒绝，且不被当成值域正确形式：**失败（符合预期）**

## 5. 未运行 / 风险 / 边界说明

- **未运行**：主脚本、六业务场景、任何数据库/容器/浏览器。本卡为夹具离线通过，**不等于六业务场景通过**；063 停止日志中除该误报外的运行事实未重新核验。
- 谓词精确匹配仅覆盖本项目固定 DDL 的实际导出形式（依据 063 原始结构JSON）；若未来 DDL 等价改写导致导出形式变化，将按"未知表示明确拒绝"报缺失——这是设计行为（宁拒绝不默过），不是缺陷。
- 未复现 063 旧失败，未触碰保留容器 65b7ebcb…。

## 6. 文档建议与下一步

- 建议 Astra 在 PROJECT_EXECUTE_STATE 将 TASK-064 登记为"已返回/建议通过（夹具离线）"，TASK-063 阻塞原因关闭。
- 下一步：由 Astra 另出真实运行卡（063 一次运行已用尽，本卡未续跑环境）执行六业务场景；运行时 verifyMigrationStructure 将自动使用修正后的谓词。
- 无必须人工操作。
