# TASK-097 / R-091 原始证据导航

本卡产品实现已保存，卡内验证部分完成。全部8个集成入口整体exit=1；本文保留失败和有效单项证据，不出独立验收结论。所有路径位于D:/shspic/project_NO3_RetroLume-agent，证据根为DocuN/evidence/TASK-097。

## 1. 先读文件

- [结果回传](D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-097-result.md)：用户流程、A—D差异、计数、未完成和正式文档建议。
- [冻结合同](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097/implementation-contract.md)：实施前预期、样例、信任和幂等边界；末尾有实施前勘误01。
- [实施差异](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097/implementation-notes.md)：实际公开/私有profile、最后修正及不能复用的范围。
- [T01—T18矩阵](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097/acceptance-matrix.md)：方法、预期、实际、版本导航和not_run。
- [版本适用性](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097/evidence-applicability.json)：每批原件与最终文件的相等/不同及双向SHA256。不同字节保留观察版本，不自动追认最终通过。

## 2. 输入、pre、post与有限差异

input-snapshot.json为给定身份导航，SHA256=91110dbd7563b1a170f5605cb3fc42b164dd2224ec8db327f3c8e9add5f2605c；input-verification.json记录71项初始匹配，post-index-check.json标出授权产品变化和未动输入。DocuS状态流水是导航，不冒充冻结产品。

pre-manifest.json及pre/保留40个直接目标的初始原字节。pre-dist-manifest.json指向第一次离线入口保存的4个原dist原件；首次build前快照也有同摘要。原pre导航未回写。

post-manifest.json与final/files/是最终产品、定向测试、必要直接依赖和证据脚本的实际快照；不含私有配置、凭据、node_modules、.venv或旧证据。original-fixture-snapshot.json及final/fixtures/只复制本卡内容地址原件，未打包运行配置。changes.json给出完整新增/修改/删除和pre/post SHA256；limited.diff只含可审阅源码/测试，dist另外用四类原件和hash表示，避免把minified bundle塞进diff。

core-freeze-check.json核对原写/锁/恢复主体和11个禁止变更模块；repository旧末尾只读函数有CRLF→LF，归一后全部旧正文为当前前缀，写主体未变。不把AST或前缀核查当真实PG验证。

integration-01-pg-to-final.diff至integration-08-browser-to-final.diff均从对应as-run原件计算，保留各失败后的修正事实；绝不覆盖失败运行原文。

## 3. 离线检查与构建

所有离线和构建命令、开始/耗时/退出码见attempt-ledger.json和as-run/{标签}/manifest.json、run.json。每个stdout.bin/stderr.bin保留子进程原字节；不是只给汇总PASS。

- offline-01：30个方法通过，子exit=0；外层最初显示输出因GBK遇UTF-8字符失败，随后修复证据输出器，不重跑30项制造绿色。原stderr中的OK仍是子进程事实。
- offline-02-fixture-protocol：7个网络夹具/protocol3/4直接方法通过；没有真实SUP或浏览器启动。
- offline-03-stored-binding：12个合同/gateway方法通过，公开StoredProfile修正后复验。
- offline-04-preflight：实际AST、DTO和脚本语法检查通过；这种检查没有发现后续运行时JS变量错误，其限度保留。
- offline-05-worker-authority：5个gateway/profile方法通过，含worker准入前复核。
- offline-06-browser-module、offline-08-browser-final：Node模块/索引预检，无Chromium启动，不能算浏览器行为通过。
- offline-07-final-guards：6个方法通过，覆盖最终confirmed严格布尔及保留命名空间无profile拒绝。
- offline-09-intents：真实意图函数和目标/父键匹配的离线断言通过，fake localStorage仅用于纯函数，不能替代UI恢复。
- offline-10-resources及offline-11-final-evidence内的收尾只读核查：不启动容器/应用/SUP/浏览器。
- build-01至04、build-05-complete-inputs：npm --prefix frontend run build，含typecheck及Vite构建，均exit=0。最后一次针对早期遗漏HTML模板/tsconfig前置原件补起源链，没有产品变化。

build-binding.json列每次构建的真实输入、命令、raw输出及四类产物。最终build-05输出和04一致；浏览器实际服务的是build-02，07取得HTML/CSS/JS/PDF worker字节逐一匹配。最终build-05未浏览器服务，不能把同目录最终产物和早期截图拼成一条不存在的动态链。

## 4. 集成入口与失败原文

每批目录都有run.json、stdout.bin、stderr.bin、container-pre.json/container-post.json及cleanup相关原件，as-run/{批次}/manifest和files固化实际被测源码/测试/runner/fixture。首次001—008迁移原始输出仅在01；以后没有重跑迁移或动旧库。

1. integration-01-pg：整体exit=1，业务10.125秒、清理0.656秒。新097库/schema/最小角色已建立；unused ActivityService导入和Windows Selector selfpipe被网络守卫误拒导致测试错误，三份本卡来源滞留。finally物理收尾成立。
2. integration-02-pg：整体exit=1，业务11.516秒、清理0.578秒。前5个真实PG和2个HTTP方法通过；最后HTTP把产品200猜成201，异常发生在登记新活动前又引发定向FK清理错误。pg-summary仍含failure/error，不改汇总。03按明确ID修复仅本卡滞留对象。
3. integration-03-business：整体exit=1，业务9.328秒、清理0.656秒。定向修复旧本卡FK后，公开正文原子PG复验通过；HTTP把真实activity.activity_id猜成顶层activity_id，KeyError，无SUP。
4. integration-04-business：整体exit=1，业务10.391秒、清理0.640秒。失败HTTP复验通过，真实首次及学习续问2 SUP/2 send、原子正文成立；后续旧继续路由夹具误写/continue得到404，产品实际是/continuations。
5. integration-05-business：整体exit=1，业务89.094秒、清理0.578秒。11 SUP/10合成send入口，11项business-checks包括复用正常首续、真并发一次send、同槽异文、UNKNOWN/非法/NOT_SENT、三种结构结果、普通model旧继续、取消晚到；随后Node声明错误在Chromium启动前失败。driver尝试仍保守计1，实际browser启动0。
6. integration-06-browser：整体exit=1，业务41.484秒、清理0.594秒。实际browser1，零费新建实际成功，但夹具等待“活动已创建”而真实文案为“活动已零费创建”，首次学习未发。该零操作活动与来源在07仅按自有ID清理。
7. integration-07-browser：整体exit=1，业务41.890秒、清理0.610秒。实际browser1/SUP2，6项真实浏览器check通过：选资料/零费新建、显式首次、文本/XSS、PDF原文、PDF补充、显式续问；刷新后的活动定位器误用UUID而列表用来源标题，超时。真实持久首/续结果保留供08冷恢复。
8. integration-08-browser：整体exit=1，业务12.484秒、清理0.625秒。实际browser1/SUP0，新应用+新context只GET读07真实首/续，learning_posts=0；下一次刷新期间资源body观察Promise拒绝，Node退出。未执行后续UI反例或专门Job硬停。8个入口/start已用尽；修正脚本不再运行。

batch计时包含预检和准备，异常/abort不漏计；业务与finally清理分开。整批失败和其中的通过断言并列保留，不用新的无失败汇总抹平历史。

## 5. 原子/进程/浏览器的直接导航

- 数据库：integration-02-pg/stdout.bin、pg-summary.json；integration-03/04-business/affected-pg-summary.json及stdout.bin。
- 真实首续：integration-04-business/business-checks.json的normal_first_followup_atomic，received_xmin/body_xmin=2858。
- 真并发/未知/取消：integration-05-business/business-checks.json及每个transport/session、真实sup-launch、job-close、gate-close原件。
- 真实导入：每批import/boot记录与source原件由bootstrap保存；对应hash可核到as-run文件。最终只读资源和台账源为supervision-ledger.json。
- 浏览器行为：integration-07/08-browser/browser-report.json、browser.stdout.bin、browser.stderr.bin。06及07报告均有错误原文，08的Promise错误在stderr。
- 截图：[首次成果](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097/integration-07-browser/browser-first-result.png)、[文本引用](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097/integration-07-browser/browser-text-citation.png)、[PDF原页](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097/integration-07-browser/browser-pdf-original.png)、[失败现场](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-097/integration-07-browser/browser-failure-context-0.png)。截图对应build-02，不是最终bundle。

## 6. 资源与保存核验

attempt-ledger、budget-final、execution-ledger是本卡账，不并行维护项目总状态。主动投入用自02:43:52.161 UTC起全部墙钟的保守上界；普通阅读/写文在内。离线实测与初轮未独立计时的证据核对60秒保守额分别展示，不冒充精确实际时长。业务226.312秒、清理4.937秒，所有入口失败都计入。

资源为唯一获准CID e49d3acc3c1be13d670af68bca2b082fea4faeeb9b9babe69df7f1d3941696a4；身份/镜像/卷/端口/权限在完整inspect内存白名单核查，Env不输出。097角色和库归属见resource-ownership.json；口令只有stdin/短期内存/本卡子进程环境，无文件/argv/报告。旧库/卷/容器Env不读取以找密码。

resources-final.json保存最后只读时点Running=false/Pid=0、18097/15197/55441释放、自有PID+创建时刻身份及后代树零。对象的alive旧字段是启动记录，own_process_active才是最后核查。097库和原获准命名卷保留、不drop。integration-08-browser/retained-fixture.json列一活动三来源及真实首/续身份，未来沿本卡续作不能盲删或重放调用。

supervision-ledger记录15个实际SUP启动和14份SessionOutcome；一个旧普通直接调用观察器安装顺序造成缺件，不能漏记启动/claim。真实Job、worker导入及transport仍保留。Python守卫仅本卡loopback地址和线程局部stdlib selfpipe；离线实际验证拒绝非本卡地址。browser有明确路由白名单，但未执行主动外网探针，不能宣称全机全网阻断。

delivery-proof.json核结果及引用文件可读、最终快照/hash、as-run保存、构建源/产物与累计账；closing-run.json及原始stdout/stderr保留这次文件核对和资源只读核查。它不是新集成runner，不启动任何业务资源，更不构成独立审计。
