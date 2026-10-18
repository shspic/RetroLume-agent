# review-03 源码先验记录

本记录先于读取repair-04运行原件、作者grammar/applicability/propagation说明。已读当前代码、合成实例、相关测试及真正pre/diff；原review-02报告只按字节复制，不重新采用实现自评。共享执行动态前18行已偶然包含编排合计判断，仅作版本/路由，不作为通过依据。

## 原F01触发与有限语法

policy 88—134：有单位仅允许首子句完整数值+已知单位；后续每一个逗号/分号子句都须精确属于8个固定肯定短语，或完整非负且精确成立的分钟转秒等式。全串去外围空白，最多一个末尾句号；无单位只允许单值及可选“约”。没有finditer、首末量值筛选、关键词黑名单或开放尾文豁免。

两个原触发“平均速度不等于1m/s”“答案未知，可能1m/s”都在首子句完整匹配失败。引号、问句、假设、额外答案量值、不确定前后文、空尾子句、辅助说明后开放文字同理不满足有限语法。辅助等式精度取两侧文本长度之和+2（至少64），足以精确检查允许的有限十进制整数/小数乘60；负值、科学计数和不成立等式均拒绝。不在这套语法的普通正确自然语言也留unknown，属于批准的可靠解析不足边界。

support主体未变：合法参考120/120=1时reference matched，而上述回答actual None使answer/status unchecked，数值dimension_ids为value，既不生成answer_value_decimal也不伪造conflict。非法/非有限参考或除零原路径unchecked；不认识的参考unit不进入有单位/无单位分支；program不解析用户原文。DTO答案真实上限4096字符/12288字节，先拒NUL/孤立代理与错误类型；不会把任意dict/list当用户text可达输入。

## 测试辨别力与传播

new-test 20—50、148—179采用ExerciseOutput/FeedbackOutput实际DTO校验和distinct UUID；两个实例是120米/2分钟与180米/3分钟、reference操作数分别120/120和180/180，initial/retest且父练习/反馈ID衔接。答案kind initial、无exposures，模型四维故意全met。检查实例不同和数值依据一致，再比较真实rebuild_progress的independent_answers/status/contested/assisted，不检查不存在的advance/opinion字段。单正确+未知期望最多一个，双正确期望两个且evidence_sufficient，因而有正常推进对照，不能依靠坏结构挡反例。

teaching_progress 46—57将status非matched的value意见收紧unknown；62—70只收满足必需维度的不同instance_data观察。仓储410及结果提交处读取同一个support/progress，未变字节不能自动排除新语法传播。实际函数运行是否对应上述源码、18方法/81回调/64样本及最终版身份仍待后续原件配对。

正常1m/s、单位空白/中文、60m/min及封闭肯定说明可保留；单位为空的约0.5保留。60m/s、0.01m/s、1m有可识别量值再由数值/量纲核查给conflict；参考自身不成立与answer unknown保持独立。

## 待定边界观察

检查到既有support单位换算在policy200—202固定precision64，而新有限数值文法本身不限制有效位数。合法短文本可写成1. + 64个0 + 1 + m/s（精确1+10^-65），参考1m/s且tolerance=None；同单位乘/除1也进入该64位上下文，可能舍掉差值。此为未执行的源码数值精度观察，需区分原F01否定/不确定根因与既有微小数值舍入，核实是否构成新增回归及严重度；不因此扩大业务验证。

两处原方法只增加文本、answer_status断言和合法实例；其他policy函数和测试方法正在做精确源码段对照。自己的纯元数据diff对照脚本暂因新文件diff头约定报错，尚未将其错误解释为产品变化，修正只在自有证据目录进行。
