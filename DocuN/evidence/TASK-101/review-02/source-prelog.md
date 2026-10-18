# TASK-101 review-02 独立增量源码初判

本文件在本轮运行日志/作者内容oracle读取前保存，实际产品和测试字节的读取及差异已独立记录；初核2934对象匹配，包括132当前源码/夹具/dist、18保护对象、120pre、36diff、7规则、3合同及2618原件。七规则与首轮相同，正文复用。首轮结果原字节b5db0b2e6f787fd6a3fb78ee1e4c1f6ee54b98114731890fb889accd88bd71b4已另存first-audit-original.md，尚未改变结果文件。

本轮同原独立审计对话，没有参加100实施，无子Agent或业务/浏览器/构建运行。读任务卡和共享状态顶部必然看到编排回收摘要，披露而不采为结论；原首轮独立性偶然暴露继续保留。用户续执行要求未改变目标/权限，断点核对确认只有本卡元数据读写已完成，没有待运行的业务资源。

## 已定位变化与待核判定

- F01原先不使用answer_text已修为分离reference_status/answer_status，数值冲突及解析不足通过dimension_ids收紧progress；60m/s、0.01m/s及1m对1m/s可静态证明不合格。仍有确定解析问题候选R02-F01：teaching_policy.py的_answer_quantity 92—108行对整段任意文字finditer，单个量即返回，没有判定该量是否为用户肯定的答案。“平均速度不等于1m/s”或“答案未知，可能1m/s”仍将命中1m/s并matched；两个不同实例加错误模型全met仍可进入独立集合。按批准合同不可可靠解析应unknown，不能只提取数字便称支持核查。静态B，未执行新反例；后续需核原实际样本是否覆盖。
- F09 NumericRef现按字段区分value≤1e18/operand≤1e12/容差0..1且12小数；instance_data拒JSON数字/科学计数，源域修正有直接B依据。G5原主体未改。源政策计算仍需在有限精度语义中解释，不将程序或开放概念关键词变为产品评分。
- F02读取CTE加入所有记录绑定version的实际源资格，逐body布尔source_qualified，history也逐项判，view_token含绑定源。expose先按旧/当前来源全体排序锁、再按原引用version/revision/hash及PDFready核。公开四读均经过共同快照并得到真实布尔，来源换新有效范围不再单独恢复旧派生正文；用户文字不抑制。public_record自身仅is False拒绝，对缺失/非法source_qualified不独立拒绝，但目前实际公开调用链总填布尔；列为条件观察，不能仅用纯函数伪row升级运行缺陷。
- F03 stream逐chunk在append前限32768，strict UTF-8、所有层object_pairs_hook拒重复、非有限常量拒绝，认证仍在读取前。待核实际ASGI/HTTP零写原件。
- F04 model/tool均只对accepted且未claim/未obsolete/未abandoned恢复，重建持久原request和原frozen，校context摘要、operation和kind，复用原T-launch CAS；不重新freeze。claimed/UNKNOWN只读边界保留，待核并发和真实两个资源类型。
- F05 paths计数及32限在活动锁内、重放先返回；F06有效G7 seed GET/保存事务校operation类型/收据、hash、goal、scope/sources/catalog原文hash，seed身份保存而无观察，UI显式沿用通过只读资格获取。旧first未重入，待核实际正反例。
- F07已有路径/公开参考/反馈/历史TeachingCitations，独立sequence/abort防迟到，绑定源回查；历史cursor及view_token/409接线。原PDF控件复用，模拟物理页不推广真实全部组合。
- F08 context纳answer并以revision绑定编辑，保旧dirty输入、显式换绑，历史序号和abort独立；owner经sessionStorage加原生Web Lock唯一，克隆候选有活锁则新UUID，草稿按owner隔离。需核失败共享槽原字节与最终bundle/原生双标签、reload和IDB失败，纯JS替身不算原生证明。
- E02夹具改按每节点/point的实际资料内容选择citation、目录不足返回no_evidence，不再evidence[0]；actual片段/论点逐项独立核之后才读作者oracle。负面false_met是故意屏障输入，不归正常内容通过。
- E01新runner保存完整as-run/manifest及after，明确选择原方法/补验范围；不因新29计数自动升级旧中间证据或整29/4全量通过，具体后续逐方法核查。

## 控制与剩余读取

新repair_runner使用外层有界worker和独立finally，repair permit/账与旧轮隔离，bootstrap只接当前明确许可，原模型transport为唯一语义替身。新readonly分支不启动app，用真实PG投影合成request上下文生成快照再浏览器回放，须严格分层。尚需完成其实际时序、账/失败/资源原件及完整源码后半段，不能按函数存在签控制通过。

下一步只读原101329/103020/110007、最终offline/build、实际目录/007/teaching/HTTP及Windows/原生浏览器原件，按最终字节与真实断言裁定F/E和受影响V/H；无任何新业务运行许可。
