# TASK-103 / R-097 审计修复03结果

修复候选完成：R104-F01/P1准确“保存已确认、列表refresh仍在await”窗口不再抢回干净B；正常保存／新草稿／回执前切换／卸载重开保持；最后真实引用GET200迟到在卸载及新活动面板被抑制，业务POST增量0。最终源码／构建／加载／PG及资源已绑定。交回原104作本次差异的增量复核，不自签DEF023关闭、独立终审、G9／STEP013／M-1或项目。

沿原103业务窗口A+，实际Codex客户端，具体部署标签不可见；无子Agent、没有使用104窗口修产品。锁定V4.0／CHG-0003、阶段07及已读公共规则同版复用，新增卡／审计原件／work-decision与执行动态v2.15已读。297基线逐项核对；原42真实根及全部失败／未知保留，不借旧余额。DEF019—022按主控和104既有有限关闭范围继承，O01—03不在本卡改动。

## 审计发现到最小修正

原MemoryWorkspace SHA aebaf2e520177519e53f34699558ab780e72f4c636157284ac15d27ef7610684、旧JS index-D7dvfnOT.js均有“初次seq比较→新编辑分支await refresh→直接select A”链。原104只作B级确定推导，未声称实测误写；其不通过报告和原件不改。

仅修改MemoryWorkspace.tsx和必要memoryIntents.ts，完整pre／diff／post保留。

- execute捕获组件生命周期、owner、绑定ID／version／revision／SHA及read／edit epoch。回执可确认自己的持久事实，任何随后选择／清稿／notice前重核；新输入分支的列表refresh返回后再次重核，已离开的A不再select。
- refresh接受该续处理的授权谓词并核生命周期，旧列表结果与读取错误不写新身份。select不同ID清旧notice；回执catch同样不能把旧错误写B。全局intent核对仍只确认原键，不授重发。
- 清原editor draft新增removeMemoryDraftIfCurrent，在IDB打开后及get回调的同一事件内核同一身份／edit epoch；新编辑的后续事务不会被旧删除吞掉。已确认intent自己的唯一草稿仍按原逻辑清理，不扫其他owner／ID。
- 生命周期在effect启动／清理变化，旧owner／caps／draft异步返回不污染新实例；finally只释放所属实例busy。自身合法select递增read序号后不再有编辑身份副作用，正常保存没有被误判为用户切换而全拒。

未改TeachingCitations／TeachingWorkspace／ActivityWorkspace、后端、001—010、权限／锁域、worker／SUP／协议、gateway／transport、材料／PDF／local_session、依赖锁／许可证、Git、公共库、正式DocuS或原始需求。无新持久模型／字段。完整差异见 [product.patch](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/audit-repair-03/final/product.patch)。

## 准确P1窗口直接验证

本轮专用A=3f6c33b3-ed59-4358-9cd1-63ad2636cbe8，B=9ca75481-a170-48b8-8e6b-6ebd3fa17b62。两者均经真实产品save登记，不被旧activity_memory_choices选择；B每个验证profile没有旧editor draft，干净正文“B干净正文”。只修订本轮A，引用目标及其依赖未改变。

最终主性质取real03。真实revise POST取得COMMIT后暂停交付；用户输入增加edit epoch，然后交付POST。代码进入新输入分支，针对它发出的真实列表GET取得200后再暂停。控制器原件分别保存POST和列表请求／收到服务器响应／交付时间，不混成回执未到窗口。

列表GET挂起期间实际点击B并明确载入，DOM确认B完整ID／version1／revision1／SHA／owner及干净正文，IDB无旧B草稿。直到B读取完成才释放旧列表响应。之后仍为同一B完整身份，正文没有切回A；网络中A详情GET增量0，A旧notice不留在B。随后输入的B新草稿实际进入IDB且仍绑B。

A的新提交key6d84c0ed-5565-4ee0-8a88-6962a443fa49、request SHA ddcaf538e1395cb5d868af9f66119d5591c4d7c63d13cae44f24786c4ac1186f，真实回执与PG均确认一次effect、A version6／revision6。原键GET只读核对，不重发或退款。最后一次PG保留A六个有效版本／正文和B一个，八次POST八个唯一业务键，其中七次有效效果，一次合法同内容无新效果另留证。

为何能检出原路径：在POST确认后的列表await期间才切B，B干净且没有dirty草稿，旧135行返回后会直接select A并发A详情GET，旧select不会被dirty条件挡住。本用例明确断言B完整绑定及A详情请求0，不能靠最后文本相同或宽sleep误通过。没有额外运行旧bundle反例，旧源码／实际编译片段按104原件对照。

直接原件在 [real03浏览器结果](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/audit-repair-03/groups/real-03-r03-p1-unique-effect/browser/result.json)、同目录p1-post-controller.json、p1-confirmed-refresh-controller.json、p1-clean-B-before-release／p1-after的DOM／控件／draft／截图。real03整根PASS及persistent-command-proof.json保存真实后批PG核。

## 同链回归与最后引用

以下取real02实际运行，最终产品／bundle未再改，real03明确继承它们，没有重做效果。

- 正常新建A/B均显示version1，只有本次原editor draft被清；这项real01已执行且在后批只读核。未切换／未追加编辑的正常revise显示新正文及版本，原对应draft已清，确认一次。
- 回执已确认后的列表GET挂起时导航“我的资料”卸载，重新打开活动面板并明确载入B，然后释放旧GET。旧实例没有抢身份／覆盖新输入或提示；当时的真实新实例／owner／绑定／draft原件保存。
- 真实POST回执尚未交付时明确切B并输入，释放后B输入及完整绑定保持，验证execute改动没有破坏C02已验的早窗。既有COMMIT丢响应只读核对／未确认保留／不自动重发路径按未改tracking及当前身份catch范围继承；本轮未新增全旧恢复测试。
- 最后引用使用现有activity a29a945b-a58f-4798-b4b3-93cc1e736aed，record e6964ce9-7686-45c3-b8b2-8e247cd25dcf，citation lc_c0655a9aed2099f2e0d9f328。根启动时真实GET200及workspace资格先核；浏览器选择后确认实际activity／record及viewToken，再点击真实引用按钮。

引用route.fetch取得200的原文及位置后暂停交付。实际导航卸载旧面板，重开另一明确活动（原C02 no_evidence活动0643576f-0c29-46ce-aff8-2e0653a03b6f），等待新workspace/head完成，才尝试释放原响应。控制器记录delivered-at；页面请求的Abort／身份变更使旧原文与位置没有在新面板复活，当前DOM及新身份正确，引用阶段POST增量0。没有伪citation、fake ready、patch序列变量或新教学／模型。

引用业务表及四账由该根前后真实PG快照核相等，除本轮专用记忆的允许写域外旧行不变。原expired overlay不授执行许可，本项只证明合法历史引用读取／迟到抑制。

所有原件见 [real02浏览器结果](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/audit-repair-03/groups/real-02-r03-preloaded-targets/browser/result.json)、同目录unmount-confirmed-refresh／late-post／late-citation-controller及截图／DOM。它的浏览器批PASS，总根因末后fixture旧行域误判仍FAIL，不改原总批。

## 所有失败、真实COMMIT和修正范围

offline01新许可／harness两方法及node语法通过；build01 typecheck／Vite通过。源码未再改，没有第二build。

real01已创建A/B并实际追加A version2。列表refresh挂起期间B尚不在已加载按钮列表，分页使用旧view token收到409，等待增加行数超时。原因有真实请求／DOM，不归咎泛泛竞态。保存这三个效果及原键，下根复用A/B，先预载B真实按钮，不创建同一效果或重发。

real02全部六类浏览器断言PASS。原末后检查错误地把本轮已登记A头的合法revision更新也当“旧行改变”，总根FAIL；完整PG after已在断言前保存。修正核对排除仅本轮M1头允许字段revision／current_version／updated_at，其余旧字段／旧表保持，并按本根POST增量，不把累计7与本根4混同。

offline03对快照核时遇到M5 effect=false。真实原因是real02 P1复用与real01相同正文，产品按原合同返回同内容无新效果，合法收据不应被夹具一律要求effect=true。该窗口仍有浏览器辨别力，但不扩大其“本次唯一effect”性质。修正后保留该合法no-op；real03只用本次不同正文nonce补P1一次真实新effect，不重做卸载／正常／引用等已过链。real03整根PASS，offline05对三根真实捕获快照核八键／七effect／no-op／旧行保留通过。

offline02、04只核各次确证fixture修正语法，原失败和八份受控执行原件保留。源改后新窗口、同因次数、预算都没有清零；没有运行旧103／104control或交互stdin stop。最终fixture的离线核逻辑修正不追认此前失败根为PASS。

## 最终身份与原104增量输入

完整308份当前文件post保存；297基线内只两前端源码及dist入口改变，旧JS被构建替换，新JS及本轮11份fixture／test新增。所有禁止域逐字节不变，旧dist四份pre原字节保留，没有手工清目录或改版权。actual as-run每批完整保存，源码／SQL／测试与运行条件可独立复建。

24份前端源码与build01快照全部一致；实际最终JS index-GgrE4smT.js，773924字节，SHA cdb6fa381256cb3128433f4ab1dfbe1b6c0fd4087e379b9bfcfed002e2abd52d。CSS index-COpEVDbn.css及pdf.worker保持原SHA，三次新浏览器六份完整JS／CSS实际加载副本匹配最终dist。不能借旧index-D7dvfnOT签新guard。

010原CRLF文件SHA33df4bcd8c040035f360cfc21c845e8f54e426832959e41477e67496f733c83c，统一LF文本SHA915f0ed9bbfd0a4263434dc431c8bd7b8c8d3c40a17b901eead46fe98946ebc6分别标示；三根实际catalog相同。SQL／后端／权限未改，12函数与旧104实际绑定直接继承，没部署／DDL／改trigger或ACL。

入口文件见 [pre-diff-post.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/audit-repair-03/final/pre-diff-post.json)、[product.patch](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/audit-repair-03/final/product.patch)、[bundle-chain.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/audit-repair-03/final/bundle-chain.json)、[runs-ledger.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/audit-repair-03/final/runs-ledger.json)、[捕获PG有限核对](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/audit-repair-03/captured-pg-verification.json)。辅助核对不是独立审计；实际末后PG原件也在real03根，独审不依赖汇总自评。

原104只需增量看两文件身份／await／删除事务／lifecycle差异、准确P1六个控制点、新bundle加载、正常及卸载回归、当前合法引用迟到和本轮许可／原件／资源。104其余已核源码、权限、legacy、SQL、费用／停树与非阻断观察直接继承；不重做集中审计，不重开DEF019—022。

## 原新账、未知和收尾

@@ACCOUNTING@@

本轮仅通过实际产品记忆commands，对已登记独立A/B发八次显式POST（两save、六revise），八个不同key、七个有效effect和一同内容no-op，没删除旧行。A末版6、B1，旧活动选择它们为0，不失效原引用上游。没有revoke／purge／cancel、新活动／教学POST、SUP／model／tool／provider／外网／付费、角色创建／迁移或安装。

本卡app两次口令设置均先核旧服务停止，首次随机，后次由owned随机bootstrap及本许可专用域在RAM派生，后继根重取后不再重置；值只RAM／子进程Env，不入argv或报告，属性／membership／ACL不变。不重置其他账户。真实bootstrap /api/session未带不支持Origin；业务保持真实session及同源Origin，认证头不保存。

旧command a392c565-1731-4314-b22e-6cee9458f862、requests4／cost4000／tool1／settled12／R20、UNKNOWN在每根before／after逐字段不变，树零不退款／结算／重发。旧submitted意图、非规范M5、pg2反向落点、pg3 pending墓碑／正文、profiles及所有失败／原结果不改。C01晚计／旧未知／104三根前置失败原样。

服务用产品Selector兼容循环，原SessionConfig window20／request2／grace2／startup5／manager_db5／cleanup5／mutex3／overhead30／manager50／lease20／single_host_recovery=false，无真实监督调用。三个API明确停止Exit1照实，driver real01退出1、real02／03退出0；Chrome context终于关闭。

三个精确CID及命名卷／库／数据／role保留，最终Stopped／Pid0，pg2／3只有inspect不连PG；1CPU／512MiB／pids128／restart=no及loopback／旧permit标签保持。18103／18104／55443—55445均可绑定，六份API／driver出生身份无原身份运行，C03 profile／server／driver精确当前扫描为空，没有杀其它服务。见 [resources-after.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-103/audit-repair-03/final/resources-after.json)。

当前52856字节旧结果全文作为下文历史后缀，SHA8b544e505c574b0bc666ca8ebd651bf4275000848dbb9b2af8ad386cb835aa18；其中41022／24351两层历史原字节也保留。本轮任务足够即停，待编排送原104增量，不自签最终关闭。

---

