# R104-F01 保存确认后列表读取晚到抢回旧记忆编辑身份

候选P1，关联102 C2/D1 V15及104第5类；共享DEF归属留编排统一，未自行占号。对象是MemoryWorkspace.tsx SHA aebaf2e520177519e53f34699558ab780e72f4c636157284ac15d27ef7610684，源定位123—145、72—105、216及230行。

正常可达时序如下。

1. 编辑A并提交save/revise；执行记录submittedSequence、submittedEdit、identity=A。输入栏仍可编辑。
2. POST未确认时继续输入，editSequence增加。回执到达且readSequence未改，133行通过，134进入保留新输入分支。
3. 135行的refresh GET尚未返回。用户点击B的memory-open；dirty的A先触发pendingView/冲突，随后点击明确载入新版，使B实际detail已读取完成，binding=B，且B无本机草稿时dirty=false。两控件未因旧busy禁用。
4. 旧refresh返回，135无再次比较submittedSequence、binding/owner或mounted，调用select(A)。select把读序号增加并abort当前读；A真实正文返回后不遇dirty/编辑变化拦截，94—99把binding、view、标题/正文改回A。

这是当前代码的B级确定路径，未运行新POST、不声称已发生真实误写。可以使后续用户编辑落回错误记忆；原contract明确晚回应不得抢完整编辑身份。现有仅在回执前切换、或仅继续输入的两类运行，不能覆盖这条await之间的窗口。

最小统一修正建议是在每个await后、任何select/清稿/notice副作用前重新比较提交序号、完整编辑绑定与owner；不因旧保存确认而主动select已离开的ID。将来回103修复时只补“回执已确认，旧列表GET挂起期间显式载入B，再释放旧GET”的定向有辨别力场景，不重跑G3—G8。104不修改业务。
