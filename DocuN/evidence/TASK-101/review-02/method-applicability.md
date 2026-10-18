# 新原方法对最终字节的适用性

本结论由原stderr逐方法结果、完整as-run副本、manifest、after-files、当前完整文件hash与实际断言形成。最终机器清单为independent-method-bindings-v2.json，早期解析漏掉跨行docstring及警告后的单独ok，已修正；早期清单保留，不作为方法总数依据。没有执行任何测试。

## B1的29个PG方法

- 8个TeachingLedgerPGTests：本地原子写、同键幂等/异文冲突、head CAS、首goal0、语义槽、投影封闭枚举、command身份守卫、needs_plan动作。测试完整字节与当前相同；后端产品与009相同。投影名称含rebuildable的测试实际只核封闭枚举/无mastered，不能代完整重建。
- 7个RecoveryPgTests：未admit失败、cancel无receipt UNKNOWN、UNKNOWN占槽、claimed无operation不得重发、committed收据保留、obsolete不得启动、冻结摘要损坏拒绝。完整测试和仓储/依赖字节相同；其合成前提固定n1，最终只缩短n2题干不改变这些身份/claim状态断言。
- 9个IntegrationPGTests：完整冻结绑定、pending_closed可启动、预算耗尽仍零费保答、trusted binding前置、answer在admit后改变拒mark、非法结果007与terminal回滚、真实并发答案一效果无分叉、ALREADY_PRESENT只读、纠错/相反反馈保争议。测试、support、seed_helpers、repair_cases和产品完整字节相同。MATERIAL、GOAL、plan/n1及反馈输出分支未被B1之后的n2题干修订改变，实际读取调用中没有n2题干/应用create_app设置断言；所证具体性质可采。
- 5个RepairPGTests：seed正反例、numeric commit、原来源/单快照、新路径32/33/重放、4方claim及claimed服务只读。后3中的numeric/source/seed另由B3原方法在最终夹具字节补验；路径容量/claim不依赖n2题干/app设置，B1当前产品字节证据可采。

B1后bootstrap纠正app子进程的当前许可安装条件；B1仓储段直接启动unittest，位于application建立bootstrap环境前，不依赖应用许可安装。它使用明确的数据库合成前提，没有实际SUP/模型发送；原29成功可采其事务断言，不能冒称B1动态传输链通过。B1/B2失败app不能采为应用通过。runner目录调整位于application分支，仓储Fixture直接用显式root/OriginalStore/DSN，不调用load_settings；B3成功app及最终offline sibling-settings另证明该分支。完整差异为independent-B1-fixture-deltas.json，不以三个backend hash相同替代夹具分析。

## B3和最终离线

- B3补3个PG及3个RepairHttpTests，均完整源码/直接夹具/后端与当前一致；B3以后仅browser_budget、repair_runner及两个前端编辑文件改变。仓储/HTTP方法不导入浏览器预算或上级调度器，不消费前端dist。正常请求调用真正产品api；HTTP边界、来源、引用、历史、seed的断言可采。
- 最终offline实际58个common加18个repair，共76，零skip/exit0。完整as-run含124对象（120源码/测试/控制/导航加4dist），每份副本与manifest、当前匹配；离线原summary和实际post drift检查符合。方法AST只作定位辅助，签字节采用完整文件，不靠AST忽略改动。
- B1独特PG共29，B3的3个是重复受影响方法，不相加称32独特PG。B1有24个旧方法与5个新增，不能替换旧29PG名单。旧HTTP4个HttpTests本轮也未按旧名单全部重跑。

## 原证据的保留和等价替代

- 原teaching_records immutable与final009四类旧行兼容未新跑，继承首轮核定的009/迁移原件，并用本轮009完整hash、原函数/触发器及app/denied最小权限实际读核对约束。没有新DDL或扩大角色权限。
- 原each_public_read一SQL由新source_scope方法的workspace/record/history/command四公开读，三种旧源失效后新范围场景作更直接补证。两个事务set_config未当业务SQL。
- 原reference暴露/只读引用、other_activity隔离，由当前新HTTP隐藏引用404、已公开引用位置、跨活动404、来源失效，以及PG expose零写和原未变offset守卫组合支撑，不宣称相同旧方法已新执行。
- 原旧25中间模块完整原件无法恢复的历史限制继续保留。新绑定解决当前所用方法的可追溯性，不能追认旧报告“最终29/4全量绿”。完整投影丢失后的全重建未动态验证，仍按首轮范围保留，不新加总批通过硬门槛。

E01/DEF-018建议就本次批准有限补证关闭；DEF-005原剩余“当前方法与最终依赖绑定”可按上述具体范围解除，原历史缺原字节、未测全面重建、真实provider层不随之解除。
