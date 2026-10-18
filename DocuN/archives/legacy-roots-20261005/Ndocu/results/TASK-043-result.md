# TASK-043 结果候选：工程归并与可重建入口

日期：2026-09-13（Asia/Shanghai）  
范围：STEP-024 / R-037；本结果只说明工程归并，不构成完整产品验收、生产发布或 Astra 最终状态。

## 结果

已将旧工程的白名单自维护源码、锁清单、后端自包含测试、启动脚本、配置模板和最小脱敏历史证据复制到本项目。旧目录 `D:/shuice12/RetroLume` 未修改、未移动；未读取或复制 `config/database.local.json`、`database.env`、真实资料、PG 数据/备份、`.venv`、`node_modules` 或缓存。

运行时源码目录不含旧工程、旧 SPIKE、`Ndocu` 或参考库的绝对路径引用，也未发现重解析点。资料与备份仍是显式的外部数据配置，但启动器不再硬编码旧目录：`deploy/start_local.py` 与 `deploy/start-backend.ps1` 都要求当前环境提供 `RETROLUME_DATA_DIR`、`RETROLUME_BACKUP_DIR`，数据库连接优先从 `RETROLUME_DATABASE_URL` 取得，才回退到项目内受忽略的私有配置。`config/local.env.example` 已改为通用占位路径。

## 实际归并内容与差异

- `backend/app/`、`backend/migrations/001_materials.sql`、`backend/requirements.txt`、`backend/requirements.lock` 和 `backend/tests/`：白名单复制。12 项历史 hash 中，业务源码、迁移、两份后端清单、前端入口和锁文件均与 `evidence/task-041/final-hashes.json` 一致。
- `frontend/`：复制 `src/`、Vite/TS 配置、`package.json` 和 `package-lock.json`；未复制旧 `dist/` 或依赖目录。构建产物仅在本项目的被忽略目录生成。
- `deploy/`、`start-local.cmd`、`.gitignore`、`config/local.env.example`：白名单复制；仅 `deploy/start_local.py`、`deploy/start-backend.ps1` 和配置模板为消除硬编码旧路径而改动。`start-local.cmd` 与历史 hash 一致。
- `README.md`：新项目说明，按代码事实写明已实现资料功能及尚未实现的能力；列出精确锁重建、私有配置和启动边界。
- `evidence/task-041/`：复制最终 hash、证据导航、限定独立审查，以及导航直接引用的最小脱敏执行结果、构建/pip 记录和合成截图。未复制应用完整日志、迁移日志、私有配置或数据库内容。

旧根目录的浏览器脚本依赖外部 `RetroLume-SPIKE-017` 的 Playwright，真实 PG 集成脚本读取私有配置；它们不满足本项目自包含边界，因此未归并。其历史限定结果由已复制的脱敏 TASK-041 证据定位，不把这些结果称为本轮重跑。

旧工程未提供独立仓库许可证文件；依赖版本由两份锁文件定位，安装包自带的许可证/版权声明随本项目 `.venv`、`node_modules` 重建，二者均不提交版本库。

## 实际命令和证据

| 项目 | 实际动作与结果 |
| --- | --- |
| 后端重建 | 以项目内 `backend/.venv` 按 `requirements.lock` 执行一次精确安装；随后 `pip check` 成功，无损坏依赖输出。使用旧工程包缓存仅作安装缓存，不形成运行依赖。 |
| 前端重建 | 在项目 `frontend/` 按 `package-lock.json` 执行一次 `npm ci --ignore-scripts --no-audit --no-fund`，成功安装 23 个包。 |
| 前端构建 | 一次 `npm run build` 完成 TypeScript 检查和 Vite 构建，15 个模块转换成功，耗时 5.08 秒。 |
| 局部入口 | 使用 `Ndocu/evidence/task-043/` 下两个合成空目录、无数据库 URL、无模型调用启动一次 uvicorn。`/health` 返回 `{"status":"ok","mode":"development"}`；`/` 含 RetroLume 静态入口，`/assets/index-p503RHpb.js` 返回 227268 字节。该自有进程已停止。原始结果见 `Ndocu/evidence/task-043/local-entry-20260913.json`。 |
| 完整性 | 12 项历史 hash 中 9 项未改文件一致；两份启动器 hash 不同仅因上述路径/配置重建调整。未发现运行源码树中的外部源码绝对路径或重解析点。 |

## 未验证、风险与后续建议

- 本卡没有启动 Docker、旧 PostgreSQL、真实资料、旧测试套件或模型；因此未验证真实 DB 连接、资料写入、浏览器流程、迁移和完整业务链。TASK-041 的历史证据仍只适用于其限定资料功能范围。
- `start-local.cmd` 的完整容器流程需要用户在本机设置独立资料/备份路径和私有数据库连接；本轮不需要人工操作，后续实际使用时按 README 设置即可，且不要回传凭据。
- 建议 Astra 仅据本结果裁定 STEP-024/R-037，并保持后续 STEP-004 的局部功能验证与本卡入口证据分开；不要将本结果写成项目完成或生产放行。
