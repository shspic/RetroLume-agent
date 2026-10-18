# TASK-042 / R-036 独立审查

日期：2026-09-12。范围：资料上传、PostgreSQL版本事务、原件库和本地接口权限；关联FR-001/003、DR-001/003、SEC-001/002。审查会话仅接收任务、约束、指定实现与运行证据，未接收执行过程聊天或自评。应用目录不是Git仓库，本次以指定文件快照审查，不能提供Git最终差异证明。

## 结论

本批限定范围审查通过：发现的1项P2版本展示错配已修正，并有针对性浏览器反例通过证据；最终指定实现未发现未关闭的阻塞问题。真实PostgreSQL并发、失败回滚和正常重启保留有执行侧原始逐项结果支持，审查者未自行重跑。权限结论限指定代码与已有API测试；不延伸为完整产品验收、断电恢复保证或任意部署方式的安全认证。未改动业务文件或共享项目文档，只创建及更新本报告；CHANGE及共享状态由规划角色登记。

## 已关闭P2：正文与标注的版本可能错配

- 位置：`frontend/src/main.tsx:47-48`、`:93`；对应API `backend/app/materials/api.py:103-107`。
- 条件：标签页A保留来源v1列表；标签页B成功替换为v2；A再选择旧列表条目。API按source_id返回当前v2正文及元数据，前端只接收text，标题和版本仍来自selected(v1)，因此新正文被展示成旧版。列表刷新也未同步selected。
- 影响：违背DR-001可辨版本要求，原文界面给出错误的版本对应关系。此结论来自明确的数据流静态审查，未运行新增复现测试。
- 最小修正：以同一次content响应的material和text共同构成预览状态；请求切换期间不展示上一份正文。也可使请求明确指定版本并在服务端校验，不能继续把未校验的旧列表元数据与当前正文拼接。修正后用两标签或等价替换时序验证正文、标题、revision和version_id一致。
- 最终复核：main.tsx:47-54将同一次响应的正文与元数据分别保存到text和loaded，并同步列表对应项，保留取消检查；不再修改读取effect依赖selected，避免同步版本触发第二次读取闪烁。:90替换使用loaded，:99加载期间禁替换，:100显示loaded版本。tests/browser_materials.cjs:24-37先保留旧列表、经API模拟另一窗口替换，再选中旧条目，等待新正文并断言“版本3”；最终browser-final.json的content_and_display_version_match、list_version_synced、replace_enabled_after_loaded均为true（revision为4）。build-final.log证明最终类型检查及构建通过。该原缺陷关闭。

## 静态检查结果及边界

- repository.py:40、44、49、56、58-60使用绑定参数；49行锁与52版本比对位于同一连接事务中，失败回滚不更新旧current_version。backend/migrations/001_materials.sql:19-20的复合外键约束当前版本属于本来源；旧版本未被UPDATE/DELETE覆盖。
- originals.py:67-94先写临时文件、flush/fsync，再以不覆盖硬链接发布；原件成功发布后才保存数据库元数据。数据库失败可留下未引用原件，但不删除旧版。本判断限应用独占可信本地目录，不声称已完成断电耐久性或跨存储恢复验证。
- 原件寻址只接受64位十六进制指纹，上传文件名不用于构造磁盘路径；内容读取有界并校验指纹。API限制UTF-8文本、大小与接收时限；前端以React纯文本节点展示正文。
- main.py:40的Host白名单、api.py:15-26的Origin/Fetch-Metadata和随机本地会话令牌构成浏览器访问边界；未发现远程网页直接取得令牌并读写资料的静态路径。此会话令牌用于本地浏览器授权，不是供应商密钥。部署仍须保持本地访问范围，此次未检查启动配置。
- 数据库异常转固定脱敏信息；原件错误返回通用信息。未读取真实环境变量、凭据或config/database文件，未执行API、Docker、安装或新增测试。

## 已读证据及不足

- evidence/task-040/api-tests.log：7项通过，有Starlette/httpx弃用警告。仅凭此日志不能认定真实PostgreSQL事务、并发锁或约束已经验证。
- evidence/task-040/frontend-build-final.log：类型检查及Vite构建成功；不证明浏览器时序和版本显示正确。
- evidence/task-041/pip-check.log：No broken requirements found；不证明数据库连接和事务有效。
- evidence/task-041/migration.log：输出编码异常，不能据此独立确认具体建表和约束结果。
- 补充授权后已读取integration.json：上传、列表、读取、坏文件隔离、失败替换保留、事务失败回滚均true，并发CAS结果为200/409；读取integration-resume.json：应用与数据库正常重启持久性为true。它们是独立于七项API测试的执行侧集成结果，不将单元替身作为PostgreSQL证据。当前授权未包含集成测试脚本和数据库逐条查询输出，因此对其细节仅确认所提供结果，不声称独立重跑或审计全部数据库运行环境。
- browser.json、browser.log：浏览器上传、读取、替换及版本展示反例通过，无页面异常。build-version-fix-final.log：修正后类型检查及构建通过。完整产品活动关联、历史版本回查入口、异常断电耐久性不属于本批覆盖范围。
- loaded最终修改后仅增量复核main.tsx及最终证据：browser-final.json保留上述针对性成功结果，build-final.log类型检查与构建成功；final-stop.json记录应用及数据库已停止。本次未重复测试或重审未改动代码。

下一步：规划角色按上述范围登记R-036结论及CHG，并按原定阶段继续。没有扩大到模型或HTML功能，也未变更架构、需求或依赖；本审查无需用户额外操作。

