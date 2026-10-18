# RetroLume 本地工程入口

本目录为 RetroLume 本地工程。下列启动说明沿用 STEP-024 已交付的本地资料入口；后续内部业务切片和未完成范围以 [架构动态文档](DocuS/架构动态文档.MD) 与 [执行动态文档](DocuS/执行动态文档.MD) 为准。内部调用验证通过不代表公开业务页面、真实模型服务或完整产品已经交付。

## 环境与依赖恢复

使用 Python 3.12、Node 24 和 npm 11。后端依赖由 `backend/requirements.lock` 固定；在 `backend/` 创建项目内 `.venv` 后执行：

```powershell
.\.venv\Scripts\python.exe -m pip install --only-binary=:all: -r requirements.lock
```

前端在 `frontend/` 使用精确 `package-lock.json`：

```powershell
npm.cmd ci --ignore-scripts --no-audit --no-fund
```

这些命令只重建项目内依赖，不升级锁版本。已安装包随自身发布的许可证与版权声明保留在项目内依赖目录；仓库不提交 `.venv` 或 `node_modules`。

## 本地配置与启动

设置两个互相独立、已存在的绝对目录：`RETROLUME_DATA_DIR` 与 `RETROLUME_BACKUP_DIR`。资料与备份可位于项目外，但它们是数据配置，不能指向外部源码。可参考 `config/local.env.example`，不要提交真实路径、连接串或密码。

若要连接既有本地 PostgreSQL，再在当前会话设置 `RETROLUME_DATABASE_URL`，或在 `config/database.local.json` 保存仅本机使用的私有配置（该文件已忽略）。应用不会创建数据库、执行迁移或调用模型。`deploy/initialize-materials.py` 仅供另行明确批准的新库首次初始化。

开发健康检查可在设置上述两个目录后运行：

```powershell
.\deploy\start-backend.ps1
```

访问 `http://127.0.0.1:8000/health`。`start-local.cmd` 会在数据库配置有效且容器镜像一致时启动既有本地容器；它只停止本次启动的容器和应用。构建后的前端由后端同源提供；开发前端可在 `frontend/` 运行 `npm.cmd run dev`。

## 已有范围与证据

`evidence/task-041/` 保留脱敏的最终 hash、执行导航和限定独立审查，适用范围见其中说明。它不替代本项目的完整产品验收。真实资料、数据库、备份、私有配置、缓存和旧工程都未复制到此目录。
