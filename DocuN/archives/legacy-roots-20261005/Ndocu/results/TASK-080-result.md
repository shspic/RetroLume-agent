# TASK-080 / R-074 结果：Git本地仓库准备与纳管边界

## 续作02：已授权本地首提交（2026-09-23，本节置顶；下方为续作01与首轮历史，均保留）

执行者：Work Buddy 续作02（沿续作01同一 Work Buddy 工程窗口常规执行），实际模型 GLM-5.3-Flash，如实登记。基线：需求 v1.1、架构 v0.33、执行状态 v1.34（提交前冻结，本轮未改）。授权：用户 2026-09-23 对"冻结清单 599 文件提交到本地 main，不设远端、不推送"明确回复"确认"；本卡取代 TASK-080.md"未授权提交"限制，仅本轮优先；本卡与本轮结果/证据均不入首提交。未 push、未 amend、未设远端、未做第二次提交。

### 结论：本地首提交已完成并核验通过

1. 提交与树：root-commit `45951501d2741630a229762d6b2d3f4b34d7f702`，tree `9126846ac139047a37aa9297e3c2c5e307c76dd9`，分支 main，全仓库提交数=1，无远端；提交信息 `chore: initial import of RetroLume-agent working tree (TASK-080/R-074 rev01 snapshot)`；git commit 退出码 0，599 files changed, 71223 insertions(+)。身份：仅确认 global user.name/user.email 存在即用（存在性核验，未读取未打印未修改 global/system/local）。
2. 暂存前核验：三份关键 hash 复核 MATCH（manifest.json 938dbfbd…01b32、pathspec-first-commit.txt 06f0d263…9e2699、.gitignore 7b56964c…030db）；Git 状态五项达标（根=项目根、main、0 提交、无远端、暂存空）；verify_revision01.py 13/13 PASS 且 JSON all_passed=true（manifest 599 条逐条 hash 一致、忽略正反例、004 在案 8f04f57c…97cc、status−manifest 逐项有排除原因）。
3. 精确暂存：`git add --pathspec-from-file=…pathspec-first-commit.txt --pathspec-file-nul` 一次执行退出码 0；未用 git add -A / git add . / 强制纳入。暂存后核验：`git diff --cached --name-only -z` 字节路径集合恰 599 且与 manifest 逐条精确相等（多=0 少=0）；`git ls-files -s -z` + `git cat-file --batch` 读取全部暂存 blob 原字节，SHA256 逐条对照 manifest 全部一致（覆盖过滤器/换行变换，不只核工作树）；暂存区与凭据证据/079证据/29项判定排除/动态产物交集为空。
4. 提交后核验（11/11 PASS）：HEAD 树路径恰 599 且与 manifest 精确相等；HEAD 树 blob 原字节 SHA256 逐项对应 manifest（ls-tree 全为 blob，无异常）；暂存区空、已跟踪工作树无变化；剩余 untracked 47 项逐项有归类理由——judged 28 项（excluded.json 判定排除 29 项中 task-079 的 test-raw-output.bin 同时被 /Ndocu/evidence/task-079/ 忽略规则覆盖故不出现 status，双重成立与续作01口径一致）+ revision-01 动态产物 18 项 + 本轮结果文档 TASK-080-result.md 1 项；未删除任何文件。

### 偏差与脚本缺陷登记（均不涉及核验对象漂移，未动 599 文件与规则）

- D-R02-2：原 verify_revision01.py `check_ignore()` 内存在一次无 input 调用 `git check-ignore --stdin` 的无用 `run()`（返回值从未使用），本环境 stdin 不关闭导致 50s 超时，pre-stage 模式无法完成。按卡允许的"明确核验脚本缺陷一次修正复检"，生成修正副本 `verify_revision01_r02.py`（仅删除该无用调用，其余逐行一致），复检 13/13 PASS。--staged 模式复用该副本时另暴露卡面已预警的 quotepath 显示缺陷（`git diff --cached --name-only` 无 quotepath=off/-z，中文路径转义致集合假差异），改由本轮新脚本以 -z 字节路径完成同等检查。
- 本轮新增（均在已排除 revision-01/ 内，不改旧证据）：scripts/verify_revision01_r02.py、scripts/verify_staged_r02.py、scripts/verify_postcommit_r02.py、staged-check-r02.json、post-commit-check-r02.json、verify-r02-prestage.json（空）与 verify-r02-prestage-stderr.txt（原脚本超时 traceback，缺陷证据）。verify_staged_r02.py 自身两处小缺陷（cat-file header 字段序、bytes/str 集合类型）与 verify_postcommit_r02.py 一处 set 切片错误均当场修正复检通过。
- 首提交时点 manifest/指令/日志本身未入提交（授权不含动态产物随后补交）；TASK-080.md、docu/CHANGE、执行状态均未改动，待编排验收后同步。

### 编排最终验收（续作02）

（由 Astra 填写，本卡不填。）

---

## 续作01：首提交范围冻结准备（2026-09-23，本节置顶；下方为首轮历史，均保留）

执行者：Work Buddy 续作01（承接完成首轮 080 的同一 Work Buddy 新工程窗口），实际模型 GLM-5.3-Flash，如实登记。基线：需求 v1.1、架构 v0.33、执行状态 v1.34。未重新初始化、未重跑首轮 13 项检查；未 add/commit/push；未读取或打印凭据值；未复跑 079。

### 结论与建议状态

1. 忽略边界补齐：根 .gitignore 纯追加三条根相对精确规则——`/Ndocu/evidence/task-073/20260921T1254-wbA1/run-result.json`、`/Ndocu/evidence/task-074/20260921T1319-wbB1/run-result.json`（凭据证据，编排裁定永久排除原件纳管，原件保留不改，不以容器据称销毁作为公开依据）、`/Ndocu/evidence/task-079/`（仅首提交整体暂缓追踪，原始文件保留；未来选择性纳管须另查敏感信息并调整规则）。追加前后 sha256：63cd46bb84701d3db560ca9513be13d857546a5616517d898482c9ce932701fe（522B）→ 7b56964c67acb3b39a2e2e7c01280e984d0ce726558ecab4db8e265b7fe030db；diff 见 revision-01/gitignore-diff-rev01.txt。
2. 全量精确首提交 manifest 已生成：599 个候选，逐条含相对路径、字节数、SHA256、类别（25 类）。集合账：旧候选 598 + 新增 1（Ndocu/archives/TASK-080-before-revision01-20260923.md，编排写入的旧合同归档）＝599；移除 0；两份凭据证据（旧为 withheld）与 079 证据 35 件转规则排除共 37 条逐条在案；原 29 项二进制/生成物维持判定排除不纳管（其中含 079 目录下 1 份 .bin，同时被 079 目录规则覆盖，双重成立）。本轮动态产物（revision-01/ 全部 + TASK-080-result.md 当前版）不进 manifest（自引用矛盾），放独立排除列表，提交时定稿后按当时 hash 纳入或次轮提交。
3. 敏感复检：候选文本重扫命中 10 处，全部与首轮人工裁定逐条一致（127.0.0.1 本地合成测试标识、运行期生成 DSN 模板、SecretStr 字段声明），0 处新增不确定项；只记录路径/模式/裁定，未回显任何值。
4. 迁移文案纠正落实：4 份迁移实为 001—004（001_materials / 002_activities / 003_pdf_review / 004_activities_time_budget.sql），004 已逐项核验在 manifest 且 hash 在案（sha256 8f04f57c743c260f5081e0c6f232860301b30c7b03fef69498d7c0704c0a97cc）。
5. literal pathspec 与首提交方案已备：pathspec-first-commit.txt（UTF-8、NUL 分隔、每条 :(literal) 前缀防魔法扩围）；first-commit-playbook.md 给出暂存/逐条 hash 复验/暂存后精确比对/提交信息/身份/main 仅本地/动态产物与 079 解禁后续的完整操作说明（本轮只写不执行）。verify_revision01.py 支持 --staged 模式供暂存后精确比对。
6. 一次静态清单/忽略边界核验：13 项全 PASS（manifest 599 条逐条 hash 复算一致；两份凭据证据与 079 证据均被忽略；必要源码/锁/004/脱敏样例/079 卡与结果未误排除；未暂存/未提交/无远端/无提交）。首轮核验发现 1 处校验公式缺陷（079 目录下 .bin 同时属判定排除与规则忽略，被我方公式误判为"应出现在 status"），属核验工具缺陷非清单缺陷，按卡修正后复检一次通过，已达一次复检限额即停。

建议状态：首提交范围冻结准备就绪，可提交编排审批；首提交仍未执行（显式剩余项），版本历史未建立。

### 续作01 证据导航（均在 Ndocu/evidence/task-080/revision-01/）

manifest.json（599 候选逐条 path/bytes/sha256/category）、excluded.json（规则排除 37 逐条带规则行、判定排除 29 逐条原因、动态排除、目录级排除）、sensitive-review.json（10 处命中+裁定，无匹配值）、pathspec-first-commit.txt、first-commit-playbook.md、gitignore-change-rev01.json、gitignore-diff-rev01.txt、revision-check.json（13/13 PASS）、scripts/{build_manifest_rev01.py,verify_revision01.py}。

### 未验证与风险（续作01）

- manifest 为采集时刻快照（2026-09-23T17:17:52+08:00）；采集后任何 Agent 改动即漂移，提交前必须按 playbook 复跑 verify_revision01.py，漂移即刷新受影响清单交回，不得凭数量判断。
- 079 证据整体暂缓为编排本轮裁定；解除须另查敏感并调规则、另行授权。
- 首提交动作须编排在具体清单（本 manifest）核对后取得用户覆盖该范围的授权，再沿本卡续作执行。

### 编排最终验收（续作01）

（由 Astra 填写，本卡不填。）

---

日期：2026-09-23（Asia/Shanghai）
执行者：Work Buddy 常规执行；实际模型 GLM-5.3-Flash，如实登记。
窗口：TASK-043 原工程整理窗口为 2026-09-13 历史会话，本会话无法续用，按卡回退为新窗口执行；未占用 079 窗口（079 证据在本轮全部标记为动态排除，未冻结）。
关联：STEP-002 工程准备补项；CON-002、SEC-001；关联 TASK-043，独立于 TASK-079。
基线：需求 v1.1、架构 v0.32、执行状态 v1.33。

## 结论与建议状态

1. Git 2.53.0.windows.2 可用。初始化前只读核实：项目根及上级（D:/shspic、D:/）均无 .git，无 junction/symlink/重解析点，无嵌套仓库。据此在本根执行 `git init -b main`，仓库根即项目根 D:/shspic/project_NO3_RetroLume-agent。
2. 仅改仓库局部配置一项：`core.autocrlf=false`。依据：本机 system 级 autocrlf=true（只读探得），若沿用，未来提交时会对文本做换行归一化；false 使文件按字节原样入库，符合"不为统一换行批量改源码"。未触碰 global/system、用户身份、凭据、hooks、safe.directory；未设远端；未执行任何 git add / git commit（含 -A）。
3. 根 .gitignore 完成纯追加维护：原 12 行规则一字未动，追加 config/local.env、.workbuddy/、synthetic-runtime/ 三条规则及注释；CRLF 保留。
4. 首批纳管候选清单已生成并逐条可核：598 个候选，25 类；排除边界全部有规则或理由；2 份疑似凭据值文件按卡不纳管、交回判断。
5. 一致性核验 13 项全部通过（含修正本卡核验脚本自身两处缺陷后复检：check-ignore 的 stdin 在 Windows text 模式被 `\n→\r\n` 污染、-v 输出方向解析反了；status 输出截断与 quotepath 转义。均为核验工具缺陷，仓库与规则本身未发现错误）。

建议状态：仓库准备就绪、忽略边界可解释、首批清单可审阅；**首提交未完成，为本卡显式剩余项**，待编排核对清单并取得覆盖提交范围的授权后在原卡继续。未提交前不称版本历史已建立。

## 差异（.gitignore）

| 项 | 值 |
| --- | --- |
| 改前 sha256 | 86820295b443a618e0730b028ff73ed66bede4fa73692ac9a2cab122da18f866（140 字节，12 行） |
| 改后 sha256 | 63cd46bb84701d3db560ca9513be13d857546a5616517d898482c9ce932701fe（522 字节） |
| 变更性质 | 纯追加（原规则字节不变，CRLF 保留） |
| 追加规则 | `config/local.env`（本地私有运行配置，占位样例 config/local.env.example 可纳管）；`.workbuddy/`（IDE/Agent 会话、本地记忆与凭据）；`synthetic-runtime/`（浏览器/应用运行时合成快照，含 profile 二进制，可由脚本重建） |
| diff 位置 | Ndocu/evidence/task-080/gitignore-diff.txt；改前副本 gitignore-before.txt；登记 gitignore-change.json |

未新增 .gitattributes；未加全局过滤器；未批量改动任何源码换行。

## 实际命令与证据导航

| 步骤 | 实际命令（均经托管 Python subprocess，cwd=项目根） | 结果 |
| --- | --- | --- |
| 环境检查 | git --version；git rev-parse --show-toplevel（预期失败）；上级 .git 探测；重解析点扫描 | env-check.json |
| 初始化 | git init -b main；git config --local core.autocrlf false；git config --local --list；git rev-parse --show-toplevel；git remote -v（空）；git log --oneline -1（预期 128=无提交） | init-log.json |
| 忽略维护 | 读原 .gitignore→副本+hash→追加→新 hash→unified diff | gitignore-change.json |
| 清单扫描 | 全树分类 + git -c core.quotepath=off check-ignore -v --stdin（字节模式）+ 有限敏感检查 | candidates.json / candidates.md |
| 一致性核验 | rev-parse / remote / rev-list --all --count=0 / diff --cached 空 / status --porcelain -uall / check-ignore 正反例 | verify-log.json（13/13 PASS） |

可复现脚本（候选纳管）：Ndocu/evidence/task-080/scripts/{env_check,git_init,manage_gitignore,candidates_scan,verify_boundary}.py。
证据目录：D:/shspic/project_NO3_RetroLume-agent/Ndocu/evidence/task-080/。

## 首批纳管候选清单（快照采集时刻 2026-09-23T15:47+08:00 前后，以 candidates.json 为准）

- 汇总：扫描 664 文件；候选 598；单文件排除 29；动态排除（079）35；疑似秘密待裁定 2；check-ignore 冲突 0。
- 工程与产品：后端源代码 28（backend/app）、后端测试 11、数据库迁移 4（001—003 系列 .sql）、依赖清单/锁 2（backend requirements.txt+requirements.lock）、部署脚本 3（deploy/，pyc 已排除）、工程级测试/看门狗 7（tests/）、前端源代码 7、前端配置/入口 3、前端依赖清单 1 + 依赖锁 1（package-lock.json）、根入口 4（.gitignore、AGENTS.md、README.md、start-local.cmd）、样例配置 1（config/local.env.example，脱敏占位）。
- 正式文档：docu/ 10 份 .MD 全部候选。
- 追溯材料：任务卡（合同）38、任务结果 38、任务证据 278、交接 1、归档快照 17（manual-handoff 规则历史副本）、阶段提示词副本 10、顶层历史证据 10（evidence/task-041 复制件）、实验材料 123（spikes 文本）、Ndocu其他 1。
- 全量逐文件清单（相对路径+类别+字节+裁定标记）：candidates.md（人读）/ candidates.json（机读）。

## 排除边界（原位置一律保留，不删除任何旧证据）

- 目录级：backend/.venv（2741 文件 50.5MB）、frontend/node_modules（1673 文件 167MB）、frontend/dist（构建输出）、__pycache__×11、synthetic-runtime×4（task-054/063/065/067 下，含 edge-profile 浏览器快照）、.workbuddy、.git。task-043 的 synthetic-backup/synthetic-data 为空目录，git 不跟踪空目录，无需规则。
- 单文件 29：png/pdf/pyc/map/bcmap 等二进制/生成物（含证据内截图与 PDF）；逐条见 candidates.md"单文件排除"节。
- 动态排除：Ndocu/evidence/task-079/ 全部 35 文件——079 窗口可能继续写入，本轮快照不冻结；正式提交前须停写或逐文件快照。
- 疑似秘密待裁定（不纳管、原文件未动）：
  1. Ndocu/evidence/task-073/20260921T1254-wbA1/run-result.json
  2. Ndocu/evidence/task-074/20260921T1319-wbB1/run-result.json
  两份含运行期生成的 db_password 与 DSN 实际值（合成容器一次性口令，仅回环、容器已销毁，但属凭据值材料）。按卡不纳管并交回编排判断；不擅自脱敏或改动业务/证据文件。
- 敏感检查其余 10 处命中已逐文件裁定为良性并保留候选：tests 与 4 份证据脚本副本中的 127.0.0.1 本地合成测试标识；run_task073/074.py 的运行期生成 DSN 模板（脚本无硬编码口令）；backend/app/capabilities/contracts.py 的 Pydantic SecretStr 字段声明；gateway.py 的 get_secret_value() 取值调用。裁定表见 candidates.md（仅路径与模式名，匹配值未记录）。

## 未验证与风险

- 未执行 git add/commit/push；"版本历史已建立"不成立。git log 预期失败（无提交）已作为证据记录。
- 候选清单为采集时刻快照：079 证据动态、本卡清单工件（candidates.json/md 等）自身在复扫中数量会随证据增减；正式提交前须以当时清单复核，不得把本轮清单冒称永久冻结。
- 首提交若误用 `git add -A`：会把 2 份 withheld 文件、29 个二进制/生成物一并带入。首提交必须按清单显式 pathspec。
- 换行：工作树零改动；局部 autocrlf=false 下未来提交按字节原样；多平台检出行为未验证（本卡不涉及）。
- Ndocu/archives 快照含中文文件名：git 默认 quotepath 显示为八进制转义（显示层），已核 -c core.quotepath=off 列举正常，非功能缺陷。
- global user.name 存在（存在性登记，未读值未改动）；届时提交身份以实际环境为准。

## 首提交剩余授权与建议（原卡继续，不另起编号）

1. 范围：以 candidates.json 候选（598 条）为 pathspec 显式暂存（建议 `git add --pathspec-from-file`），排除 withheld 2 份与全部排除项；不用 `git add -A`。
2. 079 证据处置需编排二选一：a) 首提交不含 079 证据，待 079 完成后随其结果一并提交（推荐，最少纠缠）；b) 提交前 079 停写并逐文件快照后纳入。
3. 身份：沿用用户现有 global 配置；如需专用提交身份由用户/编排明示（本卡不得擅设）。
4. 提交信息建议：`chore: initial import of RetroLume-agent working tree (TASK-080/R-074 snapshot)`，或由编排指定。
5. 提交时点复核：`git diff --cached --stat` 与清单一致后再 commit；提交后由编排登记 docu/CHANGE.MD。
6. 分支：main（init -b main 已定；无提交前可零成本更名，如编排另有约定）。

## 文档建议（本卡未改 docu/公共库，仅建议）

- PROJECT_EXECUTE_STATE.MD：TASK-080 登记为"已返回/待编排验收"；"Git尚未初始化"表述可更新为"本地仓库已初始化（main，无提交、无远端），首提交待授权"。
- PROJECT_ARCHITECTURE.MD 工具交付安排：同上口径微调，历史 002 验收结论不变。
- docu/CHANGE.MD：由编排为 .gitignore 变更、080 证据与结果登记 CHG。

## 必要人工操作

本轮无必须的用户操作。2 份 withheld 证据文件的纳管/排除/脱敏裁定属编排职责，裁定前它们保持未纳管状态。

## 编排最终验收

（由 Astra 填写，本卡不填。）
