# TASK-080 续作01 — 本地首提交操作说明（仅说明，本轮未执行任何 git add/commit）

采集时刻：2026-09-23T17:17:52+08:00（manifest.json/excluded.json/sensitive-review.json/pathspec-first-commit.txt 同批生成）。
前置事实：本地仓库 main、无提交、无远端、无暂存；.gitignore sha256 7b56964c67ac…（续作01 追加后）；现有 global user.name 存在（存在性核验，未读取未改动）。

## 一、暂存前必须完成的核验（漂移即刷新受影响清单交回，不得凭候选数量判断）

1. `git rev-parse --show-toplevel` → 必须＝ D:/shspic/project_NO3_RetroLume-agent。
2. `git rev-list --all --count` → 0；`git remote -v` → 空；`git diff --cached --name-only` → 空。
3. 逐条核验 manifest hash（全量 599 条）：
   `"C:/Users/28432/.workbuddy/binaries/python/versions/3.13.12/python.exe" Ndocu/evidence/task-080/revision-01/scripts/verify_revision01.py`
   该脚本一次完成：manifest 逐文件 sha256 复算、与 git status -uall 精确集合比对（status−manifest 必须恰等于"判定排除+本轮动态"集合）、忽略边界正反例、004 迁移在案。任何 FAIL → 修正或刷新受影响清单后交回编排，不得继续。

## 二、暂存（严禁 git add -A / git add .）

```
git add --pathspec-from-file=Ndocu/evidence/task-080/revision-01/pathspec-first-commit.txt --pathspec-file-nul
```

说明：pathspec 文件为 UTF-8、NUL 分隔、每条带 `:(literal)` 前缀——字面匹配，禁用通配/魔法扩围；中文文件名按字节直传。

## 三、暂存后范围精确比对（提交前最后一道闸）

```
"C:/Users/28432/.workbuddy/binaries/python/versions/3.13.12/python.exe" Ndocu/evidence/task-080/revision-01/scripts/verify_revision01.py --staged
```

--staged 模式：`git -c core.quotepath=off diff --cached --name-only` 的路径集合必须与 manifest.json 候选路径**逐条精确相等**（多一条少一条都 FAIL），并确认两份凭据证据、079 证据、29 项二进制/生成物、本轮动态产物均不在暂存区。

## 四、提交（须编排取得用户对精确范围的授权后执行）

- 分支：main（仅本地，不设远端、不推送）。
- 身份：沿用现有 global 配置（已存在）；如需专用提交身份由用户明示后另行配置。
- 推荐提交信息（可由编排改写）：

```
chore: initial import of RetroLume-agent working tree (TASK-080/R-074 rev01 snapshot)
```

- 提交后核验：`git log --oneline -1` 有且仅有一条；`git status --porcelain -uall` 剩余条目应恰为排除集（2 份凭据证据与 079 证据被忽略规则覆盖不再出现，剩余为 29 项二进制/生成物 + 本轮动态产物）。

## 五、本轮动态产物的后续处理（不在本首提交内）

- `Ndocu/evidence/task-080/revision-01/` 全部文件与 `Ndocu/results/TASK-080-result.md` 当前版为本轮动态产物，不进 manifest（自引用矛盾）；首提交时点定稿后按当时 hash 复核并纳入（可并入首提交授权范围由编排定，或次轮提交）。
- 079 证据解除暂缓：须另查敏感信息并调整 `/Ndocu/evidence/task-079/` 规则后另行授权。
- 两份 073/074 凭据证据原件永久排除纳管（编排裁定），规则不得移除；如未来需要纳管必须先脱敏另存新文件。
