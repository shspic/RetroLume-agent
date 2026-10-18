# TASK-112 / R-106 review-01 — 三缺陷与账段的独立增量复核

## 目标与交付

你沿原TASK-112集中终审的A+独立窗口接续，不再完整重审G11。只裁定DEF-031/F112-01、DEF-032/F112-03、DEF-033/F112-02及E112-01是否已闭合，并核新image/load、必要私有pipe/停止门和夹具的实际变化传播。先前终审成立的限域结论和充分原件直接复用。

结果仍存 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-112-result.md，置顶review-01，原36048字节/SHA ea51e0f49f556fd6f07aea11741d26099a534550850c0c68dfa49a9ab4c3b522全文作为原字节后缀保留。新证据只入 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/review-01-20261012/。一次交付代码/证据/控制三轴、四项关闭判断、真实剩余和是否具备交编排关闭G11有限切片条件；不直接改产品或自签项目/所有STEP/发布。

## 项目、规则、窗口与许可

项目根 D:/shspic/project_NO3_RetroLume-agent；入口 D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。task_model、V4.0、公共AGENTS CHG-0003；公共根 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，DocuS/AGENTS.MD及WORK适用2/6/8章，同窗未变正文复用。七锁定指纹仍在项目DocuN/evidence/v4-migration-20260930/rules-snapshot.json。需求v1.2、架构v1.21、执行动态v2.43，阶段07。

父TASK111/R105，关联TASK110已采用G11-P110、FR009/SEC003/NFR002003/B01/STEP015016。本卡是既定终审问题的限域增量，不改变Must，不追加工程/业务运行。接收原112 A+审计窗口，未参与111续作07产品修复，不继承工程聊天/思考；不沿工程窗口，不派子Agent，不并行产品写入或运行资源。真实客户端/型号如实登记，无法核窗口ID不冒工具确认，但须披露实际接续与实现接触。

111工程已返回并冻结，112当前旧结论仍未关闭。新任务号/R不变，许可 TASK-112-G11-REVIEW01-20261012 是本次只读增量。原已观测审计投入3347.3488145/10800秒、首采样前准备unknown保留。本轮从首个实际接收工具UTC/mono新固化7200秒窗口；累计已观测投入上限仍10800，不清零，最大投影10547.3488145，原剩余7452.6511855仅允许本卡用7200。不恢复旧已经结束的时窗或业务余量。

## 基线与独立输入

你已独立形成首轮结论，本轮复用原TASK112报告、checkpoint及读入hash；原合同完整正文保存在 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/orchestration-receipt-09/prior-TASK-112.md，原始110有效Must和首轮判断不必全部重读。先看本卡与新冻结清单，再独立读实际三产品diff、原字节pre/post和必要直接调用路径，然后核本次对应原件。不要先读TASK111结果/候选摘要/主控回收结论作为修正通过依据。

新对象清单 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-112/orchestration-review01-20261012/frozen-inputs.json：112项源码/必要夹具及255份C07证据的hash导航，不要求每份全文通读。相对原105源实际变5项，产品仅production_supervisor.py、pipe.py、renderer-protocol.cjs，另外control/core及7个C07新夹具。允许按真实传导扩读，不审未变前端/四账/全部SQL/所有故障或数学。

关键新产品SHA如下。

- production_supervisor.py = 71564962f3e58e57932a5859d971eeb764c81177e7c2821015c326e22e55dc8b；原f757477cf2ac9cc321c036383f9b06a7cb18e88a174ae5197d2753fa4c99f9c9。
- pipe.py = db2a742a559d7905012273e9fd9acaec441a549e12d71fa8ac77a3f486d3f974；原9a2f2b0a717ed9326b65f422d5b18c8486fdd781bffed9ad5104fec0b5e2f22e。
- renderer-protocol.cjs = d7907b8eb2414098162a03e7adc8d9f8953f026ad33a0ebbee8330a834755e24；原dd2ffb52f3ddf505e31de6cc47fb3db7504788fa6ba589f1851ff79a4c3469bb。

新生产v2-08 image sha256:ec3c70c7a8a8894c647a69b08b0c296727bb052f639e487567e9cd4624766789，load8a047050ffe584dffa6e85222c16c8f400c0ab4db82f72a32812c2befd082b3f；四runtime集合仍6cc300164a6cb364d9bd0bae4897f06d3f6a65cf5d4272477d2bccde67312597。最终Panel/前端bundle、SQL012/ACL/角色、原四账/worker与隔离规范没有新增改动。开工独立重算必要身份，漂移停相关判断，不对旧快照签新通过。

## 四项复核标准

### DEF-031 / F112-01 ready时窗

核完整ready接收时刻、身份、收到事实与接受资格分开、Event.wait成功后仍复核原min(t0+8秒,D-10)、当前时窗及stop；边界相等关闭。保存迟到包的kernel供物理停止，不把已resume对象伪成从未启动。原t0/D不延、次数不退，拒绝ready/输入与结算要对应实际started事实。

读C07 offline-01/ready的六样本和实际产品调用，区分替身单调门级与真实调度证据；读root-19/late_ready的实际packet/hash、接收/接受时刻、state事件、输入拒绝及完整停止。真实合法包约8.063秒到达是否未进入ready/running，由原数据独立判断，不能只看PASS。及时ready对照在normal_bom_header，核新image/load、实际78.4 ACK/PNG；不要求再生成两Native。

### DEF-032 / F112-03 双EOF、异常和退款门

核实际空读EOF与读取异常分开、stderr超8192有限保存但继续排空、线程退出不冒EOF，以及最终确认/持久结算共同要求双EOF、无读异常和原StopProof。PipeReadError只把真实读取失败与EOF区别，须审它对read_packet异常/排空和原调用者的真实影响；不能因函数文字局部没变就忽略传导。保存/取证失败不能破坏精确清理或补造退款资格。

核九组离线实际读取/结算门方法，真实root19 stderr_overflow的12289字节进入准确Node stderr、捕获8192、stop后真实双EOF、Linux/Job和DB确认。未EOF最终方法在root20/stderr_no_eof，必须先看到stderr EOF=false/真实读异常、cleanup_unconfirmed/R60/elapsed null及拒新start，随后原parent结束、触发前持有的真实读副本取得双EOF，再同根全R60恢复。观测者不持Job/写端、不与存活reader争读，外部清理与自主事实分开。

root19同名方法因夹具缺closed属性失败原件/同根满R恢复保留；root20只修该属性后复验。独立判断该夹具文件hash变动是否只影响未EOF方法、此前五方法as-run是否仍适用，不机械全重跑。旧25缺kernel/EOF的UNKNOWN不被本次新标志或恢复解除；旧完整正常收据按原112限域，不往旧数据填新字段。

### DEF-033 / F112-02 Node实际入口

核validateInit对存在constraints键要求数组、缺省/空数组仍合法、显式null和其它非数组拒绝；纯JSON解码对原始UTF-8和canonical UTF-8 bytes比较，而非只比已去BOM的文本。字符串内合法U+FEFF不删，Python前置防线和四runtime/编译包/SQL期望身份不放宽。

审整个真实Node入口调用序列，确认新防线处于实际header/body解码及init/hash/runtime链，不能只接旁路helper。核Python/Node十组一致性，包括缺省/[]/null/非数组、BOM header/body、内部U+FEFF；同realm CJS wrapper修正仅夹具，与最初cross-realm失败分层。

核新宿主root19/null_init、bom_body、normal_bom_header的真实wire、正确长度/hash及拒绝位置；BOM在READY后拒绝不能混作模型产物非法提交，null只变wire不造非法DB成果。load651资源及实际ready中的Node/PW/Chrome/内核/隔离、新image绑定独立核hash，固定四runtime/计算/前端字节未变则按旧结论继承，不重新做全部32例/六故障/主UI。

### E112-01和本次执行控制

核原root6事件109/869276343000000至PG stop871556046000000的保守2279.703只记一次，旧14546.863→16826.566、旧16200超626.566保留不追认；adjustment文件、唯一事件3508与预算execution_time_adjustments一致，不返counts。物理停机瞬时/连续持有推断限制保留，不把当前Stopped补历史账。

本次工程C07前向许可规范性预算在原111卡或orchestration-receipt-08/continuation-budget。根20/20、新real168.657/2400、累计16995.223/20400；image8/9、PG16/16、create52/55/start48/51，名字56—62各一次、63—65未用；API12、主browser11、模型/OneCall9、frontend4和HTTP1611/PNG182/public68不增加，internal30、offline分组34/Reaper2。按原事件核，不以方法数量或现有47对象倒算尝试，也不把失败退次数。

根19=155.328、根20=13.329，PG保持及两次停机是否全在真实区间并集，root之间是否实际停，cleanup是否重分类无双计；E112-01和旧漏计校正不能又加一次。最后finalize原次数重算遗漏三迟记输入，补统计与实际产品/资源是否分离由原失败和最终事件独立判断。C07首两只读工具未采时刻/扣300秒的保守收紧及阶段混分类，不得冒精确首读或全metadata；按真实权限影响评估，不因收紧自行新增产品门。

只核已保存精确47对象/新7行停止、准确进程birth/Job/端口与active_batch，新未EOF首失败也必须满R恢复；当前物理停止事实不替代之前未知阶段。历史旧失败/超限/采样/pre/offline27缺终点/13元仍保留；执行控制历史偏差不抹去有效产品证据，也不得把旧整体合规签为通过。

## 原件导航与允许操作

所有C07文件根为 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-111/execution/continuation-07/，各索引已给绝对路径。优先final/change-index、source-diff及pre/post，offline-01/ready和stderr、offline-02-node的Python/Node实际入口，root19/build/production-build及final/load-manifest-verification，final/case-index/stop-index/sessions-final/evidence-manifest和对应六方法原件。再读E112-01-adjustment、timing/accepted、final/budget-final/timing-final、root19/20和repair01/交付统计修正的实际输出，缺链才扩相关文件。

本轮只读新产品/对应夹具/直接依赖/旧自有审计证据及新原件，只写本TASK112结果和review01证据。允许纯元数据hash/有限diff/JSON日志解析/计时与oracle核算；禁止产品import/compile/test/build、PG/SQL、Docker/Job/浏览器/模型/安装/Git/旧runner执行、凭据/真实配置、源/测试/DocuS/公共库或111证据修改。业务运行额度0，不恢复工程秒数或次数。机制已清楚不另做广泛官方资料研究。

独立结论先形成并留checkpoint；主控已核结果身份不是你的通过依据。不要先读111结果/候选摘要/主控本轮缺陷评价；需要比对披露仅在独立判断后读必要段并记时点，不能把实现自评当证据。你原112结论可复用，不因同一窗口已知缺陷重新证明独立性，实际参与实现则不得兼审，应交具体缺口。

## 停止和回传

达到四项及必要传导覆盖即停，不用剩余额度做完整终审第二轮。不添加BFCache/跨浏览器/真实provider/任意脚本等未采用Must。发现新确定问题给路径/行/触发/影响/最小修正及它与此次改变的关系；非阻断观察不升级硬门。关键对象漂移、缺不可替代原件/实际独立性失效或本轮/累计时限到达，停相关判断并完成独立部分，不自行修复或补跑。

回传TASK/R/review、真实身份/接触与窗口安排、三个DEF逐项关闭或未闭及证据、E112-01核销/历史偏差、本次差异/版本/限域继承、新阻断/非阻断/未验证、实际读入hash/命令/时长、正式文档建议与最少下一步。代码、证据、执行控制三轴分开，明确当前G11有限切片是否具备交编排关闭条件；不直接填编排最终验收，不签全部STEP/项目/发布。旧首轮36048字节保留原字节并复读校验，保存后回复一句话和完整结果绝对路径。
