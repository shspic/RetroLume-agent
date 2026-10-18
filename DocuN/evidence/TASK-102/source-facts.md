# TASK-102 真实源码事实与读取范围

本文件只有B级源码/文档事实及定位，不是第二份实施合同。契约正文唯一位于 [TASK-102-result.md](D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-102-result.md)。函数元数据来自文本读取，不导入模块。59项文件指纹见 [read-hashes.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-102/read-hashes.json)，函数行定位见同目录 function-facts.json。

## 规则、父成果与读取性质

锁定七规则全部hash一致，实际必要正文为公共AGENTS、WORK4/6/8/9、阶段07和TASK_TEMPLATE。00/05/06仅hash核对，未替代当前合同。入口与任务卡完整读，输入snapshot/rules-snapshot完整读。

执行动态读取当前v2.09顶部及相关定位，最终需求读取当前Must、数据/安全与第13节参数门，架构读取当前G8/G9定位、FLOW004/007、DATA006/API005及必要源码地图。原始需求正文未读、未改；没有用历史ARCH文字覆盖当前源码。

TASK099按当前业务/不可变事实/持久职责/锁序/公开读面/退出及批准包的必要节读取；TASK100读取最终修复04及修复03的真实差异/限制，TASK101读取review-03结论/继承/精度观察。未重读2618原件或旧全审，不重新hash它们。R03-O01仅源码观察，数值函数没有调用。

40项snapshot项目对象与七规则和任务卡初核48匹配。补充11个直接依赖为local_session.py、main.py、activities/api.py、teaching_adapter.py、capabilities/contracts.py/gateway.py、worker/one_call.py、service_config.py，以及test_teaching_repository.py/recovery.py/api.py。补读是定向职责/函数/字段，不宣称每个大文件逐行通读。001—009 DDL完整读入，其余文件按下述范围读取或函数定位。

## 数据、身份和锁序

[001_materials.sql](D:/shspic/project_NO3_RetroLume-agent/backend/migrations/001_materials.sql:3) 为source/current_version/revision与version哈希，FK防来源/版本串用。002第4/34/52行建立活动、来源范围、操作。004/005有空activities门，007允许非空新增而不回填旧正文，008区分model/tool域及工具次数。不能把这些不同迁移政策混成一种。

[007正文](D:/shspic/project_NO3_RetroLume-agent/backend/migrations/007_activity_operation_results.sql:10) payload为TEXT、非空/限字节，PK为activity/operation，FK到operations。009模型派生事实body=NULL，经FK引用007，零费本地事实body非空。

[009事实与trigger](D:/shspic/project_NO3_RetroLume-agent/backend/migrations/009_teaching.sql:139) 含source_refs、body_sha256、不可变applied_revision/state_after。第208—219行任何UPDATE/DELETE拒绝，注释明确尚无获准删除事务。第220—241行固定命令身份/context_body/context_sha256及一次launch_claim；第242行仅REVOKE PUBLIC，没有现成app/purger角色或获准清理函数。

[同连接事务](D:/shspic/project_NO3_RetroLume-agent/backend/app/activities/repository.py:304) 每次打开psycopg AsyncConnection、transaction及statement/lock/idle超时，不自动设repeatable read；不能以这个包裹证明多SELECT一致。

[来源锁](D:/shspic/project_NO3_RetroLume-agent/backend/app/activities/repository.py:395) _source_rows按source_id读，_lock_sources逐项FOR UPDATE核current_version/revision，_verify_scope_hint在活动锁后比原集合。revise_scope第459行旧新来源并集UUID排序→活动，revision单调增加。create_activity第494行先来源后活动、插活动/范围/模型授权，同一个_transaction；没有现存memory_selection。

[教学锁](D:/shspic/project_NO3_RetroLume-agent/backend/app/activities/teaching_repository.py:122) 实际顺序为来源→活动→operations键排序→teaching_heads→commands键排序。原记录来源还并入来源锁。第186行是head/goal/scope CAS，第202行取消/到期本地写门。新的上游锁必须在第一次活动锁之前，而非拿到head后再锁记忆。

[模型准入](D:/shspic/project_NO3_RetroLume-agent/backend/app/activities/repository.py:1053) teach8m在operations锁后调用_locked_teaching_binding；模型父项必须model、received/同scope/完整正文，不接受tool父项。第1430行_locked_operation也是来源→活动→operations，第1483行mark再次核教学绑定/关门/租约。

[工具准入](D:/shspic/project_NO3_RetroLume-agent/backend/app/activities/repository.py:1187) admit_tool_operation先来源→活动→operation，预扣一次工具，不预扣模型费用。mark_tool_started第1302行和record_tool_outcome第1360行各有自己的来源→活动→operation路径，不能只改模型_locked_operation就称工具也生效。结果第1411行先_terminal_confirmation，再current/UNKNOWN/关门，最后同事务教学hook。

[模型结果](D:/shspic/project_NO3_RetroLume-agent/backend/app/activities/repository.py:1649) 原终态确认优先、失效成功拒、允许UNKNOWN诊断；_write_outcome写007，_write_teaching_outcome在同connection同COMMIT形成事实/曝光/进度。教学第1177—1303行中历史分支不写progress，current反馈才更新投影；新的记忆失效不能冒充旧教学版本变动的历史例外。

## 冻结、结果、公开读取与来源

[教学接受/launch](D:/shspic/project_NO3_RetroLume-agent/backend/app/activities/teaching_repository.py:950) 存完整context_body/hash；同键先核原收据，accepted/claim资格一次性，恢复不换上下文。_locked_teaching_binding第1134行核head、command、request/context hash；_teaching_verify_current第326行核引用种类/hash/goal/scope及PDFready。

[真实上下文](D:/shspic/project_NO3_RetroLume-agent/backend/app/learning/teaching_service.py:220) _freeze_model_context调用read_learning_snapshot、_load_teaching_entities、load_units、有限词项catalog及messages_for_teaching，把messages写入TeachingFrozenContext。实体装配第268行真实读取目标、路径、题/参考、答案、纠错、核算和至多2048字节前史，最多12引用。_build_profile第487行绑定实际身份及消息SHA，不存在个人记忆消费。

[现存DTO](D:/shspic/project_NO3_RetroLume-agent/backend/app/learning/teaching_contracts.py:491) TeachingProfile固定teaching.v1；第571行FrozenContext固定teaching.context.v1且model带messages；第614行stored_teaching_result不保存整个输入消息，但007仍可能有模型输出复述。v1摘要函数按完整model_dump，默认新增字段会改变旧hash。

[adapter](D:/shspic/project_NO3_RetroLume-agent/backend/app/learning/teaching_adapter.py:11) 核消息形状/hash和catalog来源；gateway第100/141/423行做profile验证、构造准入binding、规范教学结果。OneCallInput.to_wire第59行和from_wire第84行按ModelCallRequest重校验，外层监督协议无需因业务profile新增而重新设计。

[教学单SQL](D:/shspic/project_NO3_RetroLume-agent/backend/app/activities/teaching_repository.py:1339) 一条CTE取得活动/head/sources/每记录来源/history/bodies/007/citation payload/exposures。第1417行用同结果算每记录source_qualified。当前仅source资格，没有memory资格。

[公开投影](D:/shspic/project_NO3_RetroLume-agent/backend/app/learning/teaching_views.py:102) public_record抑制失效来源的派生记录，goal/answer/correction/exposure区别对待；regions的nodes来自head投影，第156行按来源/坏path抑制。它没有长期记忆撤销判定。view_token第46行目前不含memory版本。

[引用](D:/shspic/project_NO3_RetroLume-agent/backend/app/learning/teaching_api.py:439) 先public_record资格，再核公开citation集合及原版本/位置/片段。第487行answer_reference是有hash的原作答读，不赋正确性。_STATUS_MAP第28行未含新memory code，_teaching_error第44行未命中默认422。

[007普通读](D:/shspic/project_NO3_RetroLume-agent/backend/app/activities/repository.py:1690) _RESULT_READ_SQL及payload CASE核binding/scope/sources。_OPERATIONS_SELECT第2061行和LIST第2087行分别控制正文和候选资格。只给教学workspace加UI过滤会留下007旁路。

[旧业务](D:/shspic/project_NO3_RetroLume-agent/backend/app/learning/service.py:30) LearningService.execute用有限目标/catalog/单个previous_result，prompt.messages_for第17行没有个人记忆。ActivityService.continue_from_result第104行拒教学前缀且要求父COMMITTED_CURRENT，execute_tool_action第191行独立工具路径，都是直接消费边界，未建立新profile前不能静默忽略选择。

[资料替换](D:/shspic/project_NO3_RetroLume-agent/backend/app/materials/repository.py:54) save在来源行锁内插新version并增revision；confirm_pdf_candidate第183行先source再candidate、完整确认后才切当前版。get_active_pdf_pages/original按当前版拒旧版。materials/api.py实际router只有session/list/upload/content，没有删除/revoke路由。

[原件](D:/shspic/project_NO3_RetroLume-agent/backend/app/storage/originals.py:27) OriginalStore拒符号链接/reparse，按64hex定位原件，put原子不覆盖、verify/read核size/hash。第92行只清本调用临时文件，不是发布原件清理。retrieval/evidence.py是片段校验/词项排序；teaching_evidence.py第8行最多4片段/4000字符/8000字节，未有完整向量记忆索引。

## 前端与权限

[真实认证](D:/shspic/project_NO3_RetroLume-agent/backend/app/local_session.py:21) local_request拒cross-site/未知origin，local_session比较x-retrolume-session与app token；main.create_app第55行随机token/no-store。不是账号库，不证明实际PG角色。

[活动创建](D:/shspic/project_NO3_RetroLume-agent/backend/app/activities/api.py:277) CreateActivityInput只有activity_id/source_ids，额度与deadline由配置生成；capabilities第190行只含旧层。ActivityWorkspace.submitCreate第403行发送这两个字段，reconcileCreate第357行只比较source_ids，新选择恢复必须补digest与版本身份。

[教学编辑](D:/shspic/project_NO3_RetroLume-agent/frontend/src/activities/TeachingWorkspace.tsx:174) refresh以goal/path/node/exercise/answer身份加head.revision保存编辑绑定，旧草稿不改绑；submit第295行canonical→IDB正文→意图摘要→submitted→POST；reconcile/explicit resume区别只读与重发。切页迟到保护与view_token已有，但不含memory状态。

[owner与台账](D:/shspic/project_NO3_RetroLume-agent/frontend/src/activities/teachingIntents.ts:16) owner同时依赖sessionStorage和活跃Web Lock，复制标签不能共用活跃owner。Web Locks缺失写台账返回false，不回退竞态。现存≤16摘要/32768字节、≤16草稿/262144字节。teachingDrafts规范对象不含business_key，包含activity/action/CAS/body，不自动保存业务。

[引用组件](D:/shspic/project_NO3_RetroLume-agent/frontend/src/activities/TeachingCitations.tsx:21) identity目前activity/record/citation IDs，变化取消读取并清展开正文；新memory/view_token需进入身份，不能仅保留旧引用ID。

测试只读真实依赖。test_teaching_repository第128行不可变UPDATE/DELETE及效果字段拒绝，第148行重建有限状态；test_teaching_recovery核claim/UNKNOWN/保守not-admitted；test_teaching_api核公开投影/引用/真实API依赖。没有执行测试或作者helper，旧证据适用性依100/101有限结论继承。

## 官方只读与未知

四页PG16官方必要语义和每页短原文/日期保存于结果唯一附录，不下载网页完整正文。官方页证明规范设计依据，不证明本机PG16/角色/结构运行。实际DSN、用户库、账号、缓存、配置正文、原件和用户资料未读取；版本/拥有者须下一获准合成卡核实。

读取中三个命令含错误候选路径和部分输出截断已在结果/计量账保留，依据实际目录改路由或补缺，不变成产品失败。当前没有资料、PG、工具、provider或付费行为证据。

