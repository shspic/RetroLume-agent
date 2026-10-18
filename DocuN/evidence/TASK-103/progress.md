# TASK-103 当前续作定位

当前目标为完整实施与受控验证，未完成，不能最终回传。用户明确转103并批准G9-P，沿实际完成102的本窗口，禁止子Agent。固定许可与完整上下文在 DocuN/tasks/TASK-103.md、TASK-102-result.md、TASK-102-work-decision.md；公共V4/CHG0003、阶段07，同窗正文已读复用。

根目录 D:/shspic/project_NO3_RetroLume-agent。receipt.json/session.json在DocuN/evidence/TASK-103。原start_ns/deadline_ns固定，首读2026-10-06T05:57:35Z映射并保守扣60秒，主动28800秒，不清零。当前约15:12 +08，仍有约6h45。初核243一致，233原文件pre已保存。正式DocuS/根入口/公共库/001—009/旧资料/原件/监督/退款/依赖锁只读。

已经实际写入
- backend/migrations/010_learning_memory.sql（约400行），七表、角色/FK/guards/资格和purge函数。
- memory/__init__,contracts,repository,service,api,context 六模块。
- activities/repository（MemoryMixin、创建选择、五处锁前缀、七个显式读SQL资格）；service旧consumer拒绕行；activities/api创建选择/有界JSON/能力/选择元数据。
- main加memory router；service_config加默认关闭memory层/容量。
- teaching_contracts另立v2 frozen/profile/binding；capabilities contracts/gateway受信联合及绑定。
- teaching_repository前缀锁/parser/接受v2/当前资格/读面抑制/进度重建门；teaching_service frozen recipe/materialize/profile；teaching_adapter复建真实消息。
- teaching_views memory_invalid、token/nodes；teaching_api新错误与workspace标记；旧learning_service拒选记忆活动。
- DEF019只改teaching_policy单位比较，同单位保留Decimal，跨单位有限256位/指数域内Fraction精确比较。
- tests/fixtures/task103/{control,resources,bootstrap_pg}.py、test_task103_control.py、test_task103_memory.py。

实际检查与资源
- offline-01通过，1.421秒，tests.test_task103_control / test_task103_memory / 原test_task100_answer_support；需最终按stderr核方法/子测试真实数。首两批日志写text在Windows产生重复CR，原记录保留，已改今后write_bytes，不冒原始字节完全等同。
- offline-02-control通过7方法，1.375秒，含新入口纯import、资源精确归属、严格预算/固定截止/exit0不掩fail及脱敏。
- real-01-bootstrap FAIL，9.562秒，结果保存路径EVIDENCE/'bootstrap-pg'+str(slot)产生TypeError；内部SQL结局未保存，未知不得填0。首次新容器成功创建且finally真实停核Running=false/Pid0。stdout/stderr原件在该runs目录。
- real-02-bootstrap-resume FAIL，010 SQLSyntaxError42601 near')'，PG17.11/UTF8/SHA核成功；新PG停保留。元数据定位activity_memory_eligible多一闭括号，已定向修。
- real-03-bootstrap-syntax-fix PASS，010执行七表成功；app LOGIN retrolume_task103_app非owner member、M3 DELETE=false、限定purge EXEC=true。PG17.11/UTF8/coreSHA真实。PG已停保留，CID4889202d9a58c622fb7cd2bd3087e5bceb7ad20a049c6550f4bd3588ff66ac11；卷retrolume-task-103-g9-pg1-data。
- 当前offline2/6，real entry3/24、container create1/3、volume1/3、start3/24、listener/SUP/browser/driver/build全0。时间看session；root内real与外壳real保守重叠收费，目前很小。metadata尚未入累计，须保守登记，不能当0。旧102/100/101历史在卡，不借余额。
- bootstrap_pg latest result会更新，旧每根stdout/stderr与execution保留，FAIL不被最后PASS覆盖。

仍需完成
1. 验证/修复backend真实CRUD、角色/精确清理、选择/失效；现存PG1停着，只能通过新root入口及Control计数start/owned CID，不在driver外直接SQL/诊断。root4可新CRUD/HTTP TestClient；新app密码随机RAM，不输出。每次角色密码重置须先证本卡所有app/worker停（目前listener0/SUP0）。
2. 需要写新 bootstrap/sitecustomize + fixture runtime最低transport，仅fake HttpxModelTransport.send。其他权威不能mock/patch；可sys/threading profile记录run_one_call/SUP/Job真实call/return并动作前计SUP。旧task100 bootstrap/runner不可执行。原runtime loop_factory已读。
3. 实际正常Windows v2 plan/exercise/evaluate、G8事实与记忆观察、accept/launch/admit/mark/result失效、UNKNOWN/预算保留；同一新API18103/PG。loop Selector，固定Session参数与卡配额，配置无密钥，key随机Env。
4. 新frontend MemoryWorkspace/memoryApi/memoryIntents、已有两workspace接线/TeachingCitations身份，独立owner/IDB/恢复，创建记忆选择与精确create fingerprint（后端已经添加）。代码尚未写。
5. README/config/activity.example.json default null memory_context与无secret说明，必要CSS/导航（查实际main/src）。
6. PG2非空升级+PG3坏前置/清理故障/空010精确反向DDL；一次最多一PG运行。角色固定cluster唯一，三个cluster独立。
7. 最终build/真实browser/HTTP/PG、V01—V24实际oracle/继承、最终字节pre-diff-post/资源收尾与TASK103结果候选（等待集中独立审计）。

已知代码审阅注意，尚未动态证
- purge参数与列同名可能PL/pgSQL歧义；已对revocation_key首WHERE限定，真正调用后检查，diag保存position。
- memory_current_revision SQL此前LEFT JOIN USING重复memory_id已改ON。
- MemoryService同键race需要有界赢家核对，当前没有AdmissionUnavailable重放处理；sameKey已有row标replayed，不重复phase2。
- capture preview目前多读原progress/关联链，必须在首SQL抑制来源/已选记忆失效派生body；event/closureNative最终save已核资格，但preview公开不能泄漏。
- schemaInfo现在只数表/fn/guard，权限probe缺完整read/公共purge ACL/owner结构验证，需针对实际风险补完。
- read_memory_selection schemaabsent当前直接legacy True，要对既存v2残迹失败关闭（其他result SQL已有此）。
- 原activity/meta SQL替换都写了，真实PG尚未验证；_memory_result_sql macro guard必须每读真正出现，避免默认True掩遗漏。
- 新TeachMemoryFrozen无messages，旧v1未加字段；parser只repo/service改到parse_frozen_context。v2recipe实际参数/header/frozen digest在真链核。
- _memory_capture关联progress最多8events；两个独立题可7event，超限明拒，不丢依赖。
- 原数字文法没改，tests已确认1+10^-65同单位conflict、60m/min matched、跨单位超256位unknown及F01否定未知。

现有控制脚本只本卡stdlib控制，不导入产品或用户配置。Control.run动作前计offline/build，真实root自己reserve entry；每根限900/真实总7200、off每180/1800、cleanup900。真实依赖/自己树安全还需后续薄helper并先pure检查。一次同rootcause两次有据修仍失败须停止该部分，不机械追加。产品当前还未形成完整候选，不要提前收尾只交runner或部分功能。

