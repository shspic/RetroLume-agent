from metadata import *
save('source-prelog.md','''# TASK104源码独立初判

依据原102 A—D及用户批准固定澄清、当前33项产品变化和原前字节；先形成本记录，再采用103运行原件。仅接触104/103合同给定背景和执行动态前8行路由，不采用103实现报告、work-decision、聊天或思考。会话有101独立审计历史，未参与102/103，已如实披露而不冒称空白会话。

## 已核源码链

010完整445行、memory六模块、全部21项既有文件的初始到当前diff、MemoryWorkspace/memoryIntents/memoryApi/TeachingCitations完整源码已审读；较大旧模块只补直接调用上下文，不重审旧平台。当前291与完整post逐字节一致，20保护对象及9规则合同相同。010 CRLF原件33df4bcd…与LF文本915f0ed9…分域；12个函数源码的去空白hash逐一与应用指纹相同。实际catalog和旧运行适用性仍待原件核对，hash本身不证明行为。

七表、组合FK、不可变metadata、单向头、M3限定清理角色、受限definer/search_path及精确逐PK删除未见明显跨记忆删除、007/009删除或动态目标注入路径。M5/头/版本/依赖/正文按一次事务形成；失败rollback和两阶段清理需实际证据补强。固定上游闭包和选择摘要来自服务端，用户输入不提供依赖/观察权威。v2持久recipe不含学习记忆正文，消息从持久事实及同一固定选择复建；服务、adapter、gateway/binding及准入/mark/result继续核资格。UNKNOWN/terminal-confirmation主体保留，不被新成功正文gate一概堵死。旧无选择规范v1模型字段未新增None键。

公开读主干在同一结果SQL核资格；teaching相关正文/state_after/payload CASE与memory_invalid公开区域相连。G7/普通continue/通用工具对选择活动拒绝，teach8t前缀还需原锁内教学command绑定，不能只凭字符串前缀获得工具资格。来源/事实后继资格、清理故障与最终v2链的具体动态覆盖仍待原件配对。

DEF019局部改成同单位保留原Decimal、跨单位在256有效位/指数域内Fraction精确比例比较，超支持域unknown；原F01全文肯定文法不改，不重开该门。

## R104-F01候选P1

MemoryWorkspace.execute 123—145行在用户边保存边继续输入时，133行仅在第一次比较readSequence；134—135分支随后await refresh，返回后无再次身份比较便select原identity。等待这个列表GET期间，用户可点一直可用的其他memory-open，再在冲突区明确载入B（该按钮只禁reading、不禁busy）；新绑定B且无本机B草稿时dirty=false。旧refresh返回后select(A)递增序号/abort新读，并载入A正文/版本，抢回当前编辑身份。完整UI可达，不需要改组件状态、坏ID或业务越权。它是已保存回应的后续异步链遗漏，不是当前已有两个late-edit/late-switch分别测试就能排除的组合。

本记录只做B级源码确定推导，未新运行POST；最后citation GET补证不依赖这条记忆保存链，可继续在受权只读范围完成。需再核最终bundle和原已有场景的时序边界后裁定；不在104修业务。

## 非阻断观察待归类

memory/repository._memory_capture 394—395将当前answer_record_id加入用于闭包的answer_ids，429—432又把整个集合标作independent_answer_ids；当实际progress独立集合为空而当前答案assisted/错误时会多标一个。它不增加本活动progress独立计数，但受检摘要字段命名与真实独立资格不同，需分离闭包和显示集合。

activities/repository的read_committed_result/list SQL CASE仍只按来源/scope取payload，新增memory资格由同语句给bool，再在Python按INVALIDATED_MEMORY丢正文；公开结果不会因这点自动泄露，但没有在这两处SQL CASE本身抑制失效派生正文。其余operation/teaching CASE需实际SQL与读面证据核对。

revoke与普通用户revise/self-report save也进入_memory_lock_prefix，从上下游闭包锁源/头/相关活动，宽于原合同要求revoke只本头/收据的最小锁域。当前没有证明死锁或不能撤销，不拿可能的全图成本当P1。

以上观察不以猜测增加PG/业务POST或大套验证，严重度与适用性在后续原件核对中明确。
''')
save('R104-F01-static-finding.md','''# R104-F01 保存确认后列表读取晚到抢回旧记忆编辑身份

候选P1，关联102 C2/D1 V15及104第5类；共享DEF归属留编排统一，未自行占号。对象是MemoryWorkspace.tsx SHA aebaf2e520177519e53f34699558ab780e72f4c636157284ac15d27ef7610684，源定位123—145、72—105、216及230行。

正常可达时序如下。

1. 编辑A并提交save/revise；执行记录submittedSequence、submittedEdit、identity=A。输入栏仍可编辑。
2. POST未确认时继续输入，editSequence增加。回执到达且readSequence未改，133行通过，134进入保留新输入分支。
3. 135行的refresh GET尚未返回。用户点击B的memory-open；dirty的A先触发pendingView/冲突，随后点击明确载入新版，使B实际detail已读取完成，binding=B，且B无本机草稿时dirty=false。两控件未因旧busy禁用。
4. 旧refresh返回，135无再次比较submittedSequence、binding/owner或mounted，调用select(A)。select把读序号增加并abort当前读；A真实正文返回后不遇dirty/编辑变化拦截，94—99把binding、view、标题/正文改回A。

这是当前代码的B级确定路径，未运行新POST、不声称已发生真实误写。可以使后续用户编辑落回错误记忆；原contract明确晚回应不得抢完整编辑身份。现有仅在回执前切换、或仅继续输入的两类运行，不能覆盖这条await之间的窗口。

最小统一修正建议是在每个await后、任何select/清稿/notice副作用前重新比较提交序号、完整编辑绑定与owner；不因旧保存确认而主动select已离开的ID。将来回103修复时只补“回执已确认，旧列表GET挂起期间显式载入B，再释放旧GET”的定向有辨别力场景，不重跑G3—G8。104不修改业务。
''')
finish('source-prelog-before-raw-evidence',{'source_prelog_sha256':sha(OWN/'source-prelog.md'),'candidate_blocking_finding':'R104-F01','grade':'B，仅源码路径，未新POST','business_execution':0,'metadata_read_failure':{'command':'rg TASK-102-work-decision at tasks instead of neutral-index results path','exit_code':1,'tool_seconds':0.5047092,'correct_path_read':True}})
