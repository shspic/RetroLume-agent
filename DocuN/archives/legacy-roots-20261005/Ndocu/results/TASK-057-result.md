# TASK-057 结果：接续并修复资料/PDF组合检查脚本（本卡不启动环境）

- 任务：TASK-057 / R-051 / STEP-004-005 / 父TASK-054；类型：测试脚本修复（只读审查+修脚本，不运行）。
- 执行时间：2026-09-20 +08:00。
- 结论：**完成（候选交付）**。TASK-054 脚本已按本卡逐项修复为可交下一张运行卡的候选；本卡唯一实际检查为一次 `node --check`（两脚本，均通过）。静态正确不等于真实通过；六类场景均未运行，运行卡执行前一律按未验证对待。

## 实际变更

| 文件 | 动作 | 说明 |
| --- | --- | --- |
| `tests/task054_pdf_materials_integration.mjs` | 重写（业务代码零改动） | SHA-256 `a636b1553ef1887124f5ebb2e0a2f35990b6fd8ca9ec27d90c5b8d3c2d9d9dd1` |
| `tests/task057_watchdog.mjs` | 新增 | 独立看门狗；SHA-256 `f792372570a958e35cee610df65328d3f984682e093073269220b9d7a31aaa2f` |
| `Ndocu/evidence/task-057/task054-original-script-copy.mjs` | 新增 | 原脚本字节级副本 |
| `Ndocu/evidence/task-057/task057-original-script-sha256.txt` | 新增 | 原脚本 SHA-256 `7ce7e5df5d022c0f47ab17b00b67baf8ca67943698f01b674b9f642ecf798f88`（原件与副本一致） |
| `Ndocu/evidence/task-057/task057-node-check.log` | 新增 | 本卡唯一实际检查的输出与退出码 |

未改业务源码、迁移、依赖/锁、正式docu、旧结果、旧日志；无Docker操作、无应用/浏览器启动、无安装下载、无Git操作。项目无Git基线，未声称干净工作树。

## 六项目标 → 实际断言/证据映射

1. **TXT原换行摘录 / 重复选择 / 晚到不污染**（场景 s1a+s1b）
   - s1a：UI上传→批次行"已保存"；摘录第3–4行后断言 `excerpt.textContent === "第二段甲\n第二段乙"`（原换行精确裁切，非归一化文本）。
   - s1b：TXT↔PDF往返切换后再开TXT，断言正文重现；三轮受控晚到——旧正文请求挂起→切资料→放行500（错误不污染）、放行200（成功不污染）、旧摘录请求挂起→切资料→放行（位置/摘录不污染，断言摘录区不存在）。每轮断言：无旧正文文本、无错误提示、当前PDF正文仍在。
   - 机制说明：UI防御为"abort+身份校验"，晚到响应送达的是已被中止的fetch；断言的是端到端"不污染"结果。若要单独观察"响应已派发但身份校验拦截"需改业务代码，超出本卡。
2. **两页PDF实际绘制并截图**（s2）：等待"勾选框解除禁用"（UI渲染完成信号）后对第1/2物理页 canvas 做像素采样（`getImageData`，断言非白像素>150且离散色档≥3，仅尺寸不再作为证据）；逐页元素截图+整页截图+`task057-canvas-stats.json`；候选详情断言 `page_count=2` 且第1/2物理页提取文字与页号对应。
3. **缺页/重复/越界/陈旧确认拒绝 + 补充身份**（s3）：API确认分别断言 422/422/422/409；UI逐页勾选+第2页用户补充→确认成功；回查断言 `query_ready=true`、所有页 `identity=pdf_extracted_text` 且 `version_id` 绑定当前版、`raw_text` 含第2页文字、补充 `identity=user_supplement`（text/physical_page/version_id 匹配）、补充未混入 raw_text。
4. **替换/跳过/失败保留旧版 + 并发CAS**（s4，真实PG事务路径）：PDF替换候选pending期间旧版可读；TXT再更新后陈旧候选 confirm→409 且正文不被覆盖；第二个替换候选 skip→`skipped` 且正文不变；坏PDF替换→422 且正文不变。
5. **混合坏文件隔离**（s5，UI同批）：一次 setInputFiles 两个文件→bad 行显示"失败"且错误消息非空、good 行"已保存"；列表含 good 不含 bad；good 内容可读。
6. **真正重启后持久状态**（s6）：重启前再建一个 pending 候选；数据库六表+activities 计数快照→按自有PID停止应用（SIGTERM 8秒有界，未退则 `taskkill /T /F` 兜底）→确认8000端口释放→重开应用→快照对比必须一致→确认PDF版本/页面文字/补充身份、newer TXT 正文、pending 候选均在。摘要中的重启场景由本真实停止/重开支撑，不再用名称冒充。

## 运行资源与监督（保持原卡上限）

- 容器 `retrolume-task-054-pg`、镜像固定 `sha256:cf134a…f8e6f`、127.0.0.1:55434、CPU1/512MiB/PID128/restart=no、无宿主挂载；应用8000占用即拒绝（绑定探测），不杀他人进程。
- 同名容器：运行中→阻塞拒绝接管；已停止且镜像身份一致→按**唯一容器ID**启动复用，并核对迁移状态（三表全缺→按序执行001/002/003一次；全在→复用不重迁移；部分存在→阻塞）。镜像不符→阻塞。容器与证据保留不删除。
- 监督：主进程全部命令异步化并带超时；`checkDeadline` 阶段检查+绝对10分钟期限；`tests/task057_watchdog.mjs` 独立进程持状态文件（唯一容器ID+应用PID），超期强制 `taskkill /T /F`+`docker stop` 并写 `task057-watchdog-fired.json`；正常结束自动退出。停止均按ID/自有PID并确认（容器 `State.Running=false` 有界确认、应用退出确认），清理错误不吞掉；失败路径仍收尾并以非零退出码结束，绝不打印 PASS。
- 证据（运行时产出，050 M-1补证口径）：`task057-env.json`（Node/Playwright/Edge/Docker/Python/pypdf 实际版本与 sys.executable）、`task057-source-hashes.txt`（脚本/看门狗/迁移/核心源码/dist/package.json+lock）、`task057-commands.log`（每条命令+退出码+stderr）、`app-stdout/ stderr.log`、`task057-summary.json`（逐场景 passed/failed + 未执行项 **not_run**、容器名称/ID/停止确认、浏览器版本与阶段耗时）。证据目录默认 `Ndocu/evidence/task-057`，可用 `RETROLUME_TASK_EVIDENCE` 覆盖。运行级文件名带唯一后缀（runTag），复用含历史数据的容器时断言不假设空库。

## 唯一实际检查与退出码

```
node --check tests/task054_pdf_materials_integration.mjs  -> exit 0（无输出）
node --check tests/task057_watchdog.mjs                   -> exit 0（无输出）
node v22.22.2（受管运行时）；原日志记录 Node 24.15.0，两者均满足 import.meta.dirname 的 >=20.11
```

本卡未运行脚本/业务测试，未用mock扩建模拟器。

## 未验证与风险

- 全部六类场景为候选断言，未运行；运行卡结论以其实际证据为准。
- 合成PDF使用Base-14 Helvetica；pdf.js无标准字体数据时通常有canvas回退渲染，但未实测。若渲染失败，UI会按业务行为阻止该页确认并判 s2 失败——那是真实证据；pypdf提取文字断言独立于canvas渲染仍可成立。
- 浏览器120秒预算内含三轮晚到（各1.5秒settle）与两页渲染等待；静态评估在预算内，超期按失败处理（不抬高上限），为实测项。
- Windows venv python.exe 为launcher时 SIGTERM 可能只杀launcher，已用有界等待+`taskkill /T /F` 兜底并记录实际路径。
- 复用历史容器时若历史数据与本卡运行级唯一文件名冲突（概率极低），断言按唯一名匹配仍成立；若历史库处于部分迁移状态，脚本按卡阻塞而非覆盖。

## 需求或架构偏差

无。未改需求、架构、业务代码、阈值或上限；所有修复在测试脚本与监督辅助脚本范围内。

## 文档建议与下一入口

- 建议 Astra 登记 `CHG-XXXX`（本卡按分工不改 `docu/CHANGE.MD`），并为下一张**运行卡**分配编号；本卡不自行开启运行。
- 运行卡建议（唯一窗口）：前置=Docker可用、55434/8000空闲、前端dist为当前构建（本次hash清单已含dist三文件）；命令 `node tests/task054_pdf_materials_integration.mjs`（建议与054一致的 Node 24.15.0）；总期限10分钟、浏览器120秒不抬高；同次证据落 `Ndocu/evidence/task-057`（或以 `RETROLUME_TASK_EVIDENCE` 指定新目录）；首次失败即停该流程并保留证据。
- 与 TASK-058 无冲突：058只读账本，不读取本卡测试脚本。
