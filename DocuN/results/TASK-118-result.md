# TASK-118 / R-112 — review-01 独立增量复核结果

D01—D04 四项合并修正均建议关闭；S 合成工程候选已具备交主控验收条件，历史执行控制不通过仍保留，Q 继续冻结，完整多步 Q 请求批准机制尚待明确。

本轮只复核首轮四项发现、直接影响和 S07/S08 控制原件，没有重做七族审计，没有实施修复或新增产品运行。报告完成不等于主控已验收；不签 Q、STEP018/019整体、M-1、项目或发布通过。以下是当前增量结论，后附首轮41590字节正文完整原样保留；首轮 D01—D04 状态由本轮更新，其余有效事实和限制继续适用。

## 一、四项状态及三轴结论

- D01 原 P1：建议关闭。三个写入口均在自己的真实锁内进行当前完整字节、文件身份、首事件与绑定 control_id 校验，foreign 日志同键返回和 change 回调均先被拒；12个实际已完成方法支持其直接风险边界。
- D02 原 P1、仅未来 Q：原“资料获批即可顺带发送任意模型正文”的安全缺陷建议关闭。完整 payload 与 typed request 双摘要、当前资料核对和多阶段 scope 复核均已落地，最低 transport 正负例适用。该关闭只认安全收口，不能认原 Q 多步流程已可执行。
- D03 原 P2：建议关闭。同 activity 的原 owner/view/head/scope/namespace/DataContext 现在不可变绑定，风险 await 后仍复核；正式 bundle8 的原生 IDB 屏障三类失效均无后续领域 POST，正常对照恰一次。
- D04 原 P2：建议关闭。索引、教学和面试确认前均消费实际只读配置身份并告知，缺字段时相关外发关闭，本地保存资格保留；合成改值只证明配置投影，未新增正式供应商支持。

代码轴：本次四项修正及直接影响范围通过，未发现新的确定缺陷。首轮其余代码结论按原版本和适用性继承，不以本轮覆盖未审新范围。

证据轴：四项修正所需的源码、方法级真实完成记录和正式 bundle 定向证据充分，允许与首轮工程原件组合继承。没有“整批 backend exit0”或“真实 PG/外部服务全通过”的结论。真实 PG roster SUM/双 provider 持久预扣组合和真实语义仍属 Q 前置缺口，不因其未开启再次判成 S 外发事故。

执行控制轴：S01—S07 的历史不通过保持。S08 按其前向48小时/命令wall/持有并集/次数许可核对，未发现已记录活动中的新超额；不能套用旧21600秒活动硬门，也不能用该段结果追认旧违规。S08真实持续工作量仍为 unknown，19项控制自检只有其有限替身层证明力。

因此，建议主控可接收并关闭有限 S 工程成果，另保留历史控制偏差与 Q 未启用状态；本报告不代填 TASK117 全过程合规通过或任何项目最终验收类别。

## 二、冻结、差异和证据导航

项目根 D:/shspic/project_NO3_RetroLume-agent；模式 task_model/V4.0、公共 AGENTS CHG-0003、阶段07。入口及七项锁定规则指纹与首轮相同，已按指纹复用原正文。本轮卡面需求v1.3、架构v1.43、执行动态v2.70；仍 TASK118/R112、review-01，父117/R111，关联116 AP1/AP2、STEP018及适用 NFR002/003/005、SEC001/002/003、DR002。

先读更新卡、原独审发现、实际 preimage/diff/源码及直接测试方法，再读运行原件。以下 C 指 [continuation-07 原证据目录](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/execution/continuation-07/)，A/B/C/D 等级沿首轮锁定定义，不把 fixture 的 passed 或工程自评当独立通过证据。

- [本轮卡](D:/shspic/project_NO3_RetroLume-agent/DocuN/tasks/TASK-118.md)、[review许可](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/orchestration-review01-20261018/review-permit.json)、[独立输入身份](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/orchestration-review01-20261018/audit-inputs.json)。没有读取 received-candidate.json 的工程评价。
- [初次冻结](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/audit/review-01/freeze-initial.json)、[最终冻结](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/audit/review-01/freeze-final.json)：各208组身份全部匹配。
- [源码链及有限差异](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/audit/review-01/scope-chain.json)、[运行记录前源码观察](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/audit/review-01/source-before-runtime.md)。
- [原方法完成与绑定核对](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/audit/review-01/method-bindings.json)、[精确 fixture 历史重建](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/audit/review-01/fixture-history.json)。均只用字节、日志和 AST，不运行测试。
- [浏览器请求/资产/图片交叉核对](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/audit/review-01/browser-facts.json)、[原账和历史前缀](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/audit/review-01/ledger-review.json)、[控制时限/收据重算](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/audit/review-01/control-facts.json)。
- [本轮读取记录](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/audit/review-01/commands.jsonl)、[本轮封存和完整复读收据](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/audit/review-01/review-execution-receipt.json)。

20项 post-source 中18项相对首次可用 preimage 有变化，14项在 S08 有变化。两个阶段备份均按原字节 hash 核准，当前 Python AST 无错误。没有只审 S08-delta 而漏 S07 已作修改；阅读用 diff 可规整换行，原字节身份单独保留。16项可直接与首轮自身绑定记录对上；teachingIntents 的首轮独立访问 hash 未留在旧记录，基线限于 S07 保存的 preimage，当前完整实现及直接影响已审，不补造其首轮独立 hash；三个新增测试/fixture 按新增处理。config 示例和 teachingDrafts 未变。

关键当前 SHA256：control.py 为0db51f9ff61f4005854f32007d3c0727d966c062f33e0a64c0a56af8b926bf7e；embedding.py 为09e788f3e2207349b6bd5a11df2ec25a09893e8b0a504399332fbd44c5863e41；gateway.py 为07f38bf2e4c11a7ca6be31b2cf9290e6a9db9ee349299f992d93bc692149bfc7；TeachingWorkspace 为1e6adfd581569aee7833f19b78b1ba8e60cbd893bb85cc4b1fdbe7cc5344bc1f。其余20项完整身份见 scope-chain.json。

正式 bundle8 的主JS index-BuUoTjO5.js 为855765字节、SHA256 bc2768fdd2d1878b44decfabd6912fdd2df7469198f9b563bca5b34edfa3c0c1。四项磁盘资产均匹配；浏览器实际16次资产响应是同一 JS/CSS 的重复加载，不扩称四项均实载。旧 bundle7 只支持原未变行为，不用其截图替代当前 UI。

工程结果仅按 bytes/hash 检查：104337字节、90b4ebc77c34cf7886f5e4bb624a9912c14df9b5a7b53ac2528826487bd771e2；C/before-result 的88265字节为当前精确后缀。二者均未解码，未读工程聊天、思考、自评或记忆。

## 三、D01 控制日志写身份

B：[control.py:110](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/control.py:110) 的 _validated_locked 将原快照校验抽成共同内部方法。commit153、create_or_get_job186、change_job233 均在各自 acquire(True) 的同一次真实锁内先校验，再取已验 events 与 JSON 副本作 replay/CAS/append。缓存命中仍读取当前完整字节/文件身份/digest；tail 在 same-key 查找之前拒绝，外来 hub.init.control_id 不得返回旧缓存或 foreign job。

返回 state、execution_job、写回执不暴露可变缓存；commit 的 validate 与 change 的 decide 使用 JSON 副本。_append 仍沿原帧/hash链、容量限制和 flush/fsync；peer cancel/fence、revision、deadline 和 clock authority 的逻辑未放宽。

A：backend-targeted-v2.log 的12个 SnapshotTests 方法实际逐项 ok，包括三个有效 foreign 日志反例、同键命中、change 命中外来job但 decide 零调用、写入口残尾、同size/mtime篡改、peer取消/fence、文件替换及期限/修订。该批测试文件和产品 hash 均与当前一致；无需借一份后续自述补足版本。

该命令随后在另一个 async 夹具构造处超时，故只继承已完成12方法，不签整批 exit0；初批尾帧 fixture ERROR、两次 async 构造超时都保留。D01 的触发路径现已直接封闭，建议关闭，不要求再装载 R01/R02 或重跑旧恢复链。

## 四、D02 完整模型范围批准

B：[embedding.py:129](D:/shspic/project_NO3_RetroLume-agent/backend/app/capabilities/embedding.py:129) 的批准项只允许 payload_sha256/request_sha256 两个严格64位摘要，最多128项，重复 pair/非法值/额外字段拒绝。非空批准进入 manifest hash；空新增字段从 hash 排除，旧 Embedding 清单身份不变，但缺完整批准的模型请求失败关闭。原 source/version/fragment/catalog 校验继续执行，完整 payload 批准不能替它绕过资料范围。

B：[gateway.py:100](D:/shspic/project_NO3_RetroLume-agent/backend/app/capabilities/gateway.py:100) 深复制 request/config 并保存原对象身份快照，构造并编码完整 payload。初始准入前、await admit 之后/mark之前以及 await mark 之后都核同一受信 grant、manifest、完整 payload/typed request 和有效期；实际 send 为已编码对象的 JSON 副本。原对象、配置或 intent 私有范围变化均不能偷换发送正文。已预扣后的拒绝保守留账；mark后实际 send 前变化记 NOT_SENT，发出后 timeout/失联仍 UNKNOWN，不退款、不自动重发。

B：[正常 loader](D:/shspic/project_NO3_RetroLume-agent/backend/app/retrieval/service.py:48) 核实际清单、grant、价格/回执文件身份，新的非空清单摘要必须一致；旧v3不携新授权字段，私有wire v4携同一批准，未把批准来源交给浏览器。正常私配/key 未读取。

A：实际 approved-model-final.log 的正例进入真实 TeachingService._stored_document、教学 prompt 与 typed Message、真实 ControlledModelGateway，只替换账本和最低 transport；admit/mark/send 各一次，实际发送对象逐值等于 JSON 规范化批准体，返回 SUCCEEDED，并回读 v4 完整范围。它不是只调用 SimpleNamespace，也没有替换网关准入或装配。selected memory 背景由夹具明确加入，用于测正文边界，不冒 v2 真实 PG 记忆资格。

A：model-scope-v2.log 的其他6个方法实际完成，覆盖目标、回答、纠错、历史、所选记忆正文/版本变化零准入/零发送，system/完整请求变化、admit后的原request/config/intent变化、mark后变化、过期、旧空批准及无grant本地transport。Model v2 原正例先在 tuple/list 比较失败，后来只改 JSON list 预期重检一个正例；独立逆向该单行得到记录的精确 d9df63e2… hash，其他方法 AST 与公共 helper 均未变。no-io 旧体7ab0eab1…也按字节精确重建：差异限 typed Message 规范化 helper/调用和该 JSON list 预期，loader/strict 方法未变。

原日志可独立去重得到33个完成 ok 的方法：D01为12，模型/清单为10，兼容 flow为6，Embedding为5。多批重复方法不加计，子测试不当独立方法，typecheck/build/browser不混入这个数量。backend-no-io 旧多项FAIL、model v2正例FAIL、初loader ERROR和后续修正均保留。

无 I/O 夹具 s08_loop 只去掉当前环境阻塞的 socketpair self-pipe；真实fd注册直接拒绝，保留 asyncio调度/timeout，不替换产品协程、网关、消息装配或未知语义。async-stack 原件实际停在 socket._fallback_socketpair accept；不外推成生产 Windows 事件循环、真实 PG或外网已验证。

结论：D02原安全缺陷可关闭。新的精确白名单故意拒绝未批准的后续消息，Q多步可执行性仍有合同缺口，见第八节；没有自动加白或已启用 Q。

## 五、D03 同 activity 的晚到门

B：[TeachingWorkspace.tsx:325](D:/shspic/project_NO3_RetroLume-agent/frontend/src/activities/TeachingWorkspace.tsx:325) 的 origin 捕获 activity/owner/view/head/scope/namespace/DataContext；query、规范构造、IDB完整草稿、摘要锁之后均重核，最终读取 owner 必须等于原 owner。[teachingApi:120](D:/shspic/project_NO3_RetroLume-agent/frontend/src/activities/teachingApi.ts:120) 再核同一 guard，到 dataFetch 的 fetch 之间没有新增 await。先发起 POST 函数再写 domain_sent/submitted，原 key/正文在发送前保存。

共享 teachingEditorOwner 对 sessionStorage 身份更换返回 null，保持原 lease 的旧链只读，不自动取得 B lease。摘要锁同时冻结 storage key 并在锁内核 guard。该函数的 memory/interview 直接别名和调用者已读：正常未变 session 的唯一 owner 行为不变，身份不准时收紧为只读；未声称重跑两域/记忆旧业务全链。默认 guard 参数保留旧调用兼容。

A：正式 bundle8 的四例均使用同一 activity018…0001；每例 query 确认并持久化后，夹具仅包装原生 IDB put/oncomplete，原生事务确已 commit，产品 oncomplete 回调被暂留。其后通过正常只读刷新驱动 owner、view 或 head 变化，再放行回调；未修改组件 guard 或 React 内部状态，也未切去另一 activity。

实际请求重核结果：正常对照一个 source_index、一个 query、一个 plan；owner/view/head 各一个 query、零领域 POST。后3例 domain_sent=false，正常为true；四例原 key GET200、query key一致、完整草稿仍在且正文相等。owner例仅证 A因会话A→B失效为只读，不说成功拿到B lease；head例只证 head变化，不冒 DataContext 动态变更。DataContext/namespace 分支本次为 B 代码复核，未新造动态覆盖。

原 key GET 是浏览器显式 fetch 到封闭合成 HTTP，不称本次真实后端资格链；未改 GET 实现及首轮实际后端原键/unknown证据按原适用性继承。时间线只给确切请求时间和完成窗口，不追造精确响应完成时刻。D03建议关闭。

## 六、D04 供应商告知与直接影响

B：[RetrievalPanel](D:/shspic/project_NO3_RetroLume-agent/frontend/src/activities/RetrievalPanel.tsx:8) 与 [retrieval-api](D:/shspic/project_NO3_RetroLume-agent/frontend/src/activities/retrieval-api.ts:8) 校验有界 provider/model、用途、次数/费用/窗口和余量；服务器 public 直接取实际 service 身份，未配置为 null。ActivityWorkspace 将 caps.provider 传入两域，确认前分别显示向量/聊天身份及用途，相关按钮和实际 retrieveForCommand 都核字段。缺失/空/坏格式不能由按钮绕过；terms模式只要求适用聊天身份，不把向量关闭扩大为本地保存、取消和只读全部关闭。

A：八例真实浏览器请求162条，与 network-timeline 原条目完全一致；16次 JS/CSS响应 hash匹配，浏览器 as-run八个直接文件与当前逐项一致。九张原PNG全部hash/bytes匹配，本审计静态查看索引/教学确认前、改值面试和缺聊天教学三张：用途、provider/model、250000预留、30秒单窗口及两次请求/500000/60秒均在相关位置可见。

缺vector、缺教学chat、缺面试chat三例均零POST，模型动作关闭，本地保存按钮仍按原资格可用；这只证明资格与显示，不冒已经实际提交保存。changed-interview 显示 synthetic_vector_b/s08-vector-model-b 与 synthetic_chat_b/s08-chat-model-b，只证明字段被消费，未调用它们，不代表产品支持新增 provider。截图中其它新建quota区域的 undefined 来自本封闭fixture未填字段，既不认全页通过，也不无据上升为产品缺陷。

结论：D04建议关闭。当前有限告知与客户端门通过，不替代服务端 grant、真实费用及官方能力核验。

## 七、历史及 S07/S08 控制审查

S07原许可21600秒，实际保存复读的 UTC保守扣30294.653691，超8694.653691；pause0、单调域比旧起点低、域身份unknown、metadata wall未完整入账。首点/后点不能相减冒实际工作量，也不能把controlled validation0称全部metadata进程零。该段控制不通过，不重构中断暂停、不退款，首轮 S01—S06 红轴亦保持。

S08许可是48小时日历、子进程wall3600、持有并集3600和精确次数，无跨中断活动硬门。真实首点2026-10-18T01:30:39.437716Z、QPC806993274664/freq1e7，日历止2026-10-20T01:30:39.437716Z。guard检查许可/状态、UTC/mono倒退及boot域、上一命令未结、命令/持有/原root截止；受控子树挂起后入Job、期限/低内存/父退出清场源码已核。19项自检是有限纯替身，其中超时Job也是FakeJob，不冒产品业务监督或全部真实异常已跑。

独立重算：offline子进程事件256.514秒加三次driver持有上界30.11，合计286.624；外层工具53条收据加首三批保守10.7，上界127.0752712；再保留最终wrapper60秒，through-readback共473.6992712/3600。嵌套重叠保守相加，不当CPU、不退时。汇总采样的 UTC跨度2133.185536秒；以其后 final_readback_sample 重算，观察上界延至2213.351516秒，均不是实际连续工作量或新增活动硬门，属于时间标签边界，未影响许可结论。

累计 roots25、PGcreate/对象/卷6、PGstart46、产品API33、Browser19、build8、Native140、HTTP2486、fixture server3、preview各2、provider/费用0；相对S08基线只新增根1、Browser尝试3、build1、fixture server3及HTTP162。Browser/server次数已用满，根26/27未用不授权本审计。fixture生命周期Job只属准确自有清场，不能因看到Job API就认产品Native预算偷增。

root25的三次attempt原业务截止均为2026-10-18T02:17:26.096340Z和同一mono值，未延期；持有4.063/8.031/18.016秒，均在原截止内结束。attempt01缓存路径错未建Browser，attempt02实际回环 ERR_NETWORK_ACCESS_DENIED，attempt03沿平台批准的同根范围成功；三次计数不清零、不安装新浏览器，也不把平台权限误说成新增产品权限。

attempt03停止原件2026-10-18T01:54:55.272724Z为child exit0、12个准确PID/birth已不存活、18119无监听、Job句柄关闭；最终2026-10-18T02:06:12.601520Z对登记30个自有birth复核，same_birth_alive/current_lookup_unknown均空。TCP表API返回5保留，普通netstat于02:05:25Z退出0且18119无匹配是有界只读替代，未因此另求升权。

以上只证明其时点和归属。本独审未实时查Docker/PG或进程；旧六CID仍只引用2026-10-16T15:45:05Z停止原件。S source frozen/permanent readonly未恢复执行资格。

旧segments、原24根、66条failure前缀均精确保持；795761字节events旧体为当前精确前缀，SHA256 f2ecf948bdfe6b01ec5789800568dc8d11466eb2cd528dccf67f3143c194814c。S08新增15条、累计81；包括控制夹具/prepare错误、两次测试构造超时、诊断超时、旧no-io/tuple断言失败、两次Browser失败及原工具失败补记，不等于15个产品缺陷。旧FAIL、UNKNOWN、原预留和旧预览首次UNCONFIRMED均未改写。

## 八、Q 的剩余最小门

四项修正关闭不等于 Q 可立即付费。新的精确完整请求批准会拒绝未知后续正文；当前没有证据证明既定 L01/I01 等多步语义链已可在这一批准方式下执行。

1. 必须先明确后续完整请求如何获批，同时保持原活动 grant不可重绑、固定roster、全局80次/20元不清零。非空 model_requests 改变manifest摘要，进而改变绑定grant；上一模型输出、持久记录ID/正文、派生上下文和新key可改变下一typed request/payload，不能先把任意未来摘要加入白名单，也不能用新grant/活动绕共享总额。最小待决定是符合这些不变量的有限分阶段/派生请求批准合同及其实际可执行证明。本轮未采用任何新批准协议，未删改原学习/面试语义目标；单个固定批准正例不能代替此门。

2. 保留首轮真实 PG 最小组合补证：获准的新normal合成库/控制根，最低transport、零外部调用，两provider均走生产 admission，真实 roster SUM+同一锁+活动/操作持久预扣+COMMIT及边界竞争、unknown不退款/重开不清零。现有真实PG锁+内存SUM仍不足，不要求重跑七族或旧28场景。

3. 后续明确联网范围中核官方当前provider/model/返回身份、智谱512维/批量/usage、现行价格/币种/条款、账号适用性及最坏调用费用；正常本地secret loader配置给非敏感readiness。不得向对话索key。本卡未联网、未读实际私配，不能签现行能力或密钥状态。

4. 在原80次/20元条件批准内形成逐动作最坏调用及剩余矩阵、固定活动40/24/16次与10/6/4元分额、失败/超时/UNKNOWN保留、72小时实际生效起点及主控Q启用回执；旧13元已用账不复活。S原根readonly/frozen不能回normal，Q新normal资源须后续精确卡许可，不能借新根清零。

5. 上述前置具备后仅补既定真实模型逐例语义及受影响实际改动，按冻结rubric继续L01、L02—L04、L06—L09、I01—I03和当前解释至L10；从已COMMIT处GET继续。结构/引用位置不冒语义支持，安全故障不向真实供方付费重放，长期效果不冒通过。

## 九、本轮执行、边界及交回

本轮继续首轮真正独立的 collaboration上下文，没有继承117工程聊天或更换为工程执行者；A+仍为资源路由标签，实际精确模型变体未确认，不冒另一个客户端、不同模型家族或新桌面侧栏chat。主控只路由/核可访问性，未给工程评价，本窗没有再委派代理，也没有读个人memory。

本轮首工具直接采2026-10-18T02:25:42.1180680Z、host ticks840019757189/freq1e7，48小时止2026-10-20T02:25:42.1180680Z，最后1200秒仅保存。父路由首点不替代本点，不跨未知域追造活动。当前可观测段/UTC上界、命令收据另封存；首轮活动保守3017.5108645秒及metadata116.9280809秒原值保留。

本轮只运行标准库 read/hash/JSON/AST/有限diff/账目核对，未import产品或执行任何原runner；静态图片查看没有启动Browser。新增产品/测试/compile/build/Node/PG/SQL/Docker/业务Job/API/Browser/provider/网络/费用/Git写均0。只写 review-01 证据和统一结果路径，旧audit原件不改，原首轮41590字节必须作为当前结果精确后缀。

本轮metadata单批均远低于60秒，总额及原累计见review-execution-receipt.json，新增上限1200秒、保守累计许可1316.9280809秒不清零。一次context.ts路径猜错和一次rg多目录中不存在路径的非零退出均保留，已用实际文件索引补读context.tsx；早期大输出截断改用定向段/摘要。没有同一问题两次有据修正仍失败后机械重试，没有冻结漂移、越界运行或待清理自有产品资源。

建议主控在唯一执行动态账记录本轮四项关闭建议、有限S工程成果待主控验收、历史控制偏差保留及Q未启用/完整请求批准待解决；架构/README如采用后续Q批准合同再同步其实际边界，用户原始需求不改。本窗不写共享状态、不签最终验收。必要用户动作无，无需重新审批80次/20元或提交凭据。

下一步由主控裁定有限S成果，再将Q最小前置在原工程归属中编排；本独审窗只保留实际新变化/剩余证明的必要增量复核，不为已关闭普通修正重开全面审计。

以下为首轮原始41590字节正文，原字节和历史结论不改写；四项当前状态以上述 review-01 为准。

---

# TASK-118 / R-112 执行结果

本轮已完成 STEP018 S01—S06 稳定候选的集中独立审计；建议代码轴不通过、证据轴部分满足、历史执行控制轴不通过，S 成果可交主控合并缺陷后回原工程窗修正，当前不具备无保留验收条件，Q 仍不得启用。

本报告是独立审计建议，不填写主控最终验收，不签 STEP018 整体、STEP019 整体、M-1、项目交付或发布通过。关联 TASK117/R111、TASK116/R110、STEP006/008/009—018、FR001—012 中适用 Must、NFR002/003/005、SEC001/002/003、DR002 及相关 DATA/FLOW。需求 v1.3、架构 v1.40、执行动态 v2.67 是卡面合同身份。

## 一、三轴、S 候选与 Q 的分别结论

1. 代码轴：不通过。当前源码存在控制日志写入口未核当前 hub 身份的关键完整性缺口 D01；另有教学 query→domain 链的 owner/view 晚到门缺口 D03，以及新入口供应商告知缺失 D04。D02 是未来 Q 启用路径的合成数据范围缺口，目前默认关闭且没有真实泄露证据，不能把它写成已经发生的 S 外发事故。

2. 证据轴：部分满足。实际 PG/HTTP/Windows Job/正式 bundle、617 行恢复包、真实预览输入与停止、PDF 受限 worker 等大量原件可按下述精确对象继承。跨 provider 全局门已有真实 PG 锁竞争，尚没有真实 PG roster SUM、两类生产准入及持久预扣共同提交的组合证据。该项是 Q 前置补证，不是因为 Q 尚未配置就判 S 产品失败。模型逐结论语义全部仍是 Q 未验证，合成 transport 不能替代。

3. 执行控制轴：不通过。S01/S03 的活动或持有超额、S03 首点漏采及 S04/S05 离线投入超额均有原账依据；后来许可只向前生效。S06 自身的新门、计数和结算在其已批准上限内，不能洗去旧偏差。历史偏差不自动推翻有完整身份和原始回执的行为证据，也不能以行为成功追认控制合规。

S 已形成可供主控裁定的完整工程候选及集中审计材料；D01 修正前不建议验收为通过。将 D01—D04 一并合并回原 TASK117 工程窗处理，保持原账和已成功对象，再由本独审环境只复核实际修正及必要补证即可，无需逐个普通修正重开全面审计。

Q 前置尚未具备。已有 80 次、人民币 20 元的条件批准有效，不重新索取该批准；旧 13 元耗尽账不复活。官方当前能力、价格、条款、正常本地账号配置、72 小时有效起点和主控 Q 启用回执等条件见第八节。当前未联网核验，也没有真实 provider 调用或费用。

## 二、实际差异、范围与证据导航

本审计只新增本结果和 [audit 目录](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/audit/) 内有限元数据脚本、读取记录和交叉核验文件。没有修改产品、测试、SQL、dist、配置、README、原运行证据、任务卡、DocuS 或 Git。

证据等级沿锁定规则：A 为真实运行或测试，B 为源码、配置、差异和文档，C 为 Agent 声明，D 为推断。本报告的 A 是读取既存原始运行记录所得，并非审计期间新跑产品。fixture 的“passed”、case-index 状态和 cleanup 自述只作 C 导航；A 结论取其真实请求、响应、SQL、进程、输入 ACK、包字节及结束记录。代码安全缺口由 B 直接定位，未编造动态复现。

主要导航如下。

- [审计合同与身份入口](D:/shspic/project_NO3_RetroLume-agent/DocuN/tasks/TASK-118.md)、[audit-inputs](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/orchestration-20261017/audit-inputs.json)、[contract-index](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/orchestration-20261017/contract-index.json)。
- [运行前源码独立观察](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/audit/source-review-before-runtime.md)、[首次 preimage 到当前的差异索引](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/audit/delta-inventory.json) 及同目录 diffs。
- [首次冻结核验](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/audit/freeze-initial.json)、[最终冻结核验](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/audit/final-freeze.json)、[217 项最终绑定核验](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/audit/raw-bindings.json)。
- [014 与真实目录独立核对](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/audit/raw-sql.json)、[源库目录和正常重开交叉定位](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/audit/final-cross.json)。
- [包、as-run、PNG、清理和确认原件核验](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/audit/artifact-facts.json)、[历史失败及分段投入事实](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/audit/ledger-facts.json)。
- [原运行证据 E](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/execution/)；下文 C 指 [S06 continuation-05](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/execution/continuation-05/)，continuation-01/02/03/04 分别为 S02/S03/S04/S05。符号只缩短正文，不产生第二份原账。
- [本审计命令读取记录](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/audit/metadata-commands.jsonl)、[执行封存及报告复读收据](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/audit/audit-execution-receipt.json)。

根目录为 D:/shspic/project_NO3_RetroLume-agent；规则入口为同根 AGENTS.md。按 task_model/V4.0、公共 AGENTS CHG-0003、阶段 07 审计，读取公共 WORK 第 2/6 章适用内容、TASK_TEMPLATE 结果要求和正确的 07_开发执行循环.md。公共根为 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4；[rules-snapshot](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/v4-migration-20260930/rules-snapshot.json) 的七项锁定身份全部匹配，没有采用后续版本。

按合同先读取最终需求及 TASK116 四份原始设计、采用回执、X02 更正，再重建实际源码差异并形成独立观察，之后才读取原始运行记录。184 份 preimage 均匹配，重建索引含 100 个产品/测试/前端/配置对象，AST 读取无语法错误。最早可用 preimage 不总是 TASK117 前基线：部分初轮新增文件到 continuation-01 才首备份，test_lifecycle.py 等只有 manifest 身份，最终部分资产也只有 manifest；相应内容可审当前源码，但不能宣称拥有其完整实施前字节。初轮 diff 和各轮 diff 未简单相加冒充最终总 diff。

初次和最终冻结均为 256 组身份零不匹配。C 的 163 项 final-source、27 项 final-binding、四项 bundle 与 fixture manifest 合计 217 个绑定检查全部匹配。config.py 为 f3582c2bca0db6dadc8fd5cfb3dfb9caa25b951848eb046861f04a21a856e38f；正式 JS 为 58a87abf5ff4b02b33aab5dc3735507f4f097791e021aeb4ddfbf0b62ac115e8。

四项 bundle 均按字节核封存；Browser14—16 proof 直接登记实载的是主 JS，Browser11 另登记 CSS。不能把四资产 manifest 都匹配写成三个 Browser 都实际 fetch 了四资产。

TASK117 结果正文从未解码。仅核其 79709 字节、SHA256 b596ab87ae3facc605dab65acbf9c708c784c11b1f8581b75ddc6611ad802ac9。保护回读里旧 63687 字节身份与当前不同，是 S06 获准追加形成；字节比较证明旧体为当前精确后缀，记录在 [报告身份核对](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/audit/scope-and-report-identity.json)。不能把该预期差异误报为产品冻结漂移。

## 三、七个审查族的事实与继承边界

### 1. Embedding 类型、wire 与出站约束

B：逐读 [embedding.py](D:/shspic/project_NO3_RetroLume-agent/backend/app/capabilities/embedding.py)，包括 512 维有限非零向量、L2、little-endian float32/hash、1—4 项容量、查询 1024 字符/4096 字节、固定 provider/model/endpoint、独立 key 映射、单 POST/10 秒/65536 字节及严格返回身份。wire v4 按 capability_kind 显式分流，旧 v3 保留旧体；model/tool/embedding credential 与 007 消费闭包没有相互冒充，embedding 007 不成为领域或 HTML 父。聊天配置仍只允许 DeepSeek 路径，不能用 Embedding 配置伪装聊天。未知或确认被拒的结果不自动重发、不退款。

A：E/root02-retrieval-proof.json、实际 007 与 pgvector 回读证实合成 transport 经真实 PG/Windows 管道存入 512 维向量，缓存命中不新增操作。旧协议和未改 SUP/launcher/session 的保护可沿准确调用链继承；这不证明当前真实供方能力或语义。D02 指出模型消息其余正文尚未受 synthetic-only manifest 约束；Embedding 对资料和 query 的 digest 校验本身没有同样漏洞。

结论：类型/协议及父消费闭包具备 B 和相应 A；Q 数据范围仍受 D02 阻断。

### 2. 跨 provider 总门和当前资格

B：[retrieval/repository.py](D:/shspic/project_NO3_RetroLume-agent/backend/app/retrieval/repository.py:41) 的 _outbound_lock 在固定全局 advisory 锁后，取 source/memory/activity 等原锁序，执行真实 activities roster SUM；model 的 admit 与 embedding 的 admit 均在原 connection.transaction 内调用它，再写活动预留和操作。request、cost 包含 unknown，费用保留不倒减；整步预览不等于实际已扣费，实际调用还逐笔准入。grant 受信配置、固定三活动、80 次/20 元、分活动 40/24/16 次和 10/6/4 元、72 小时、日期、价率及默认关闭均有封闭校验。浏览器不能指定 grant 或改绑旧活动借额度。

A 的准确边界：C/shared_gate_check.py 实际调用生产门，但锁、manifest、grant、SUM 和预扣为内存替身。C/root24_global_gate.py 的两个连接、backend PID 34/35 和相同 advisory SQL 是真实 PG，存在约 0.109 秒竞争等待；Proxy 仍从内存提供 manifest/grant/SUM 并在 Python 中更新预算。故已有“生产函数 + 真实 PG 锁”证据，没有“两 provider 真实 PG roster + 持久预扣提交”的完整证据。首次 45 秒超时原样保留；后一次 8 秒有界检查不能追造首次超时根因。

结论：真实事务实现的 B 路径成立，未发现据此可断言的费用绕门；组合 A 缺口只列入 Q 前置，最小补证见第八节。

### 3. 检索、014 和兼容升级

B：当前 freeze/claim/admit/result 均绑定 scope、domain revision、源版本、领域父和 memory dependency。received、007 与对应向量同短事务；semantic slot/CAS、同键冲突、缓存和 exact-space 过滤明确。cosine 与词项各最多 32 候选，RRF60/稳定破同分，最终原片段再次 verify，不以高分证明结论。准备最多 128 批/每批 4，有限目录 512，不误把合成 8 片段上限变成文件类型上限。

014 当前 SHA256 为 3a919b2562ded5765de132519b841c1d1439c65c001795cfbd608cbc03586e78。审计由 SQL 原文独立抽取的 11 个函数体均与当前 registry 规范化摘要一致；NOLOGIN、最小列权限、固定 pg_catalog/pg_temp search_path、PUBLIC EXECUTE 撤销、runtime guard 均逐层核对。未知 DDL 不进入已批准 profile；001—013 原字节保护不变。

A：S03 source-SQL-after 与 compat-SQL-after 两个真实目录均匹配受信 R02 extra shape 5b7dc68a94101307bcbd63a16607c5b2ee79906b5f32669d764853a55172dc12；两库 11 个函数体对应当前 014。前后 legacy 三行相同，tool 行 tokens NULL、cost0 合法，旧 model received/unknown 预算不变。初轮 r02-frozen-catalog 和 first-commit 目录并非最终 shape，保留其当时失败/前向修补身份，不能拿当前源目录倒当初始可信基线。

A：C/semantic-slot-race 两个不同 key 同争 revision0，仅一个 200 committed、另一个 409；C/inflight-goal-invalidation 确为先 dispatch 再 goal1→2，晚到 invalidated/current=false、record_denied/unknown、250000 预留保留。S03 源删除后 chunks0/相应 embedding 0070、tombstone1，最小费用元数据保留。可继承其真实分支；不宣称已跑所有域×所有失效原因的笛卡尔组合。

结论：该族工程链和非空迁移有可继承 A+B，供方语义和完整 Q 总账 A 不在其通过范围。

### 4. 两域、记忆、意图和正式 UI

B：teaching.v3/interview.v2 复用持久领域记录、CAS、当前 retrieval_ref，记忆只作低信任背景而不进入资料证据或已证履历；旧 v1 不因新接线放开记忆。进度 policy 未被替换，暴露/独立 exercise/重复命令和保守理由链可继承未变保护，当前“证据足够但无下一节点”的理由有对应修正。

A：S03 正常库真实 HTTP 保存了学习路径、初答/针对练习/复测/进度理由，以及面试问题、probe、回答、反馈和 finish；重开仍是同 CID/volume/profile。I01-after-normal-reopen 的 activity06c8a779… 最终 head revision7/ended，question cc4167bd…、answer c46c693d… 和 feedback00c06779… 持久可读。X09 原预算逐项一致，unknown 的操作、状态和 250000 预留不变、显式继续前 POST0。完整 JSON 投影不字节相等：重开 GET 不再附旧 supervision，学习视图 read_at/budgets 投影也有差异；不能把它报成持久事实重置。

A：S03 X02 revise/revoke 都是在旧 query dispatch 后变更记忆，晚到 current=false/invalidated，record_denied/unknown 保留预留。按有效 X02 更正，不再要求不存在的独立 delete 命令。C/X02-current-physical-deletion 的 memory c110aa4b… 为 revision3/current version2/revoked/done，body_rows0、GET body null；两个版本 hash/bytes 和撤销清单摘要独立核准，六个旧 selection 身份保留。它证明原 revoke+purge 的真实物理效果，没有新造第三次命令或 delete 事件。

A：Browser11 正式 bundle7 的教学 answer 与 query/evaluate 有真实 200 committed/received 和 feedback/exposure/progress，面试 goal 正文未就绪时按钮禁用、就绪后才新 query/ask。其 observation_errors4、drained=false 保留，不以结尾自评抹掉；关键已捕获回执仍可采信。

A：Browser12 同 key 同正文重交三次总计同一事实、异正文409；真实晚到的是切换到另一 activity 的 workspace，两个复制 session owner 不同。Browser13 真实余量1 request、整步需2时 posts[]，刷新 GET-only。它们与 S03 完整业务链可以组合继承，不要求同一 Browser 重做整链。它们没有覆盖 D03 所指“同一 activity、query 已返回后保存草稿期间 owner/view 改变”的新分支。

结论：L01—L09、I01—I03 的协议、持久性、有限确定计算可按已实测对象继承；支持/冲突/等价表达等真实模型语义仍全部未由 Q 证明。X02 的三种效果已按有效合同分清；X03/X04/X07/X08/X09 的证据只能覆盖其原命令和回执类型，不把一个丢响应代表例写成所有 COMMIT 丢响应分支均已重跑。D03/D04 待修正。

### 5. R01/R02、包/codec 和控制完整性

B：R01 精确 28 表/1..13，R02 31 表/1..14，vector0.8.6 注册明确；所有受影响列、float32、007、unknown、预留与删除 overlay 进入受信 codec/snapshot/package/load。恢复保留 row/component 事务、容量/时限、逐列 canonical 比较、loader 撤回和 seal 后 readonly，未以数量相同代替值相同，也没有允许未知 profile/DDL。

A：实际 3938960 字节包 7a10f64c… 的 SHA256 fe404fc4527634394ca8291e7279f89f81dc8a3816d71abc14bd560680a2987e；root b040841394dfa82a14c2b180e60393b3b7f0d222b11016b468a81d6f17c3a347。审计自行核 canonical root、101 个 ZIP member（100 内容加 manifest）、所有内容 hash/bytes、31 表/617 行、22 个合法 512 维向量及 84 个 007 绑定，其中 42 个 embedding；两个 space 含一个 unused metadata，不是混空间向量。两笔 unknown 各保留250000。包内 memory body0、PDF page0、HTML artifact0，不能把后来 PDF/L10 新事实说成已经装进这个旧包。

A：S04 success01 为 restore job55957ddd…、target634aa034-51f6-4510-b075-38cb005481d8，CIDf2e65dc…，617 行/22 component/7 files，22.454 秒，1..14 可信链、逐列回读、seal、loader 撤销以及 34 读/三次 SQL42501 有原件。两个 failed target/CID5e5e…、9a222… 保留并停止；C 没有 success02 或重新装载。旧 failed 不因 success01 消失。

B：ControlHub 的新 _current_snapshot 在真实锁内读完整当前字节并核文件身份/摘要，缓存包括 digest；同 size/mtime 篡改、尾帧、换文件和返回可变对象等读取路径有明确防护。但该防护没有用于全部写入口，见 D01。恢复包事实可继承，不代表控制日志所有写身份已经合格。

结论：包和恢复/永久只读切片有 A+B；D01 阻断该族无保留完整性通过。

### 6. owned/StopProof 与两种 readonly 入口

A：旧 preview5c508… 第一次 StopProof 仍是 UNCONFIRMED；S05 正常恢复另取得 never_started 并保守结算60秒。C 的旧对象当前 OpenJob error2 只表示当时不存在，不能补填第一次 ActiveProcesses0。此次新 preview 的 confirmed=true 单独成立，不覆盖旧未知。

A：L10 的真实 ACK seq1 d120/t120→1、seq2 t240→0.5；t0 和未定义字段均422且不消耗 seq3，reset seq3→1。标准图片工具查看 actual-frame.png，画面属于 seq2 的0.5，SHA256 b29cee640344838f3856d09444a547019afad602f092cee2711f331aa1081321；没有将它说成 reset 后1。

A+B：生产 supervisor 的 t0/3/4.5/8/D 门未放宽；reaper ready 约1.484秒，完整 ready 包收齐约6.031秒、判定接纳约6.047秒，未因启动快慢改8秒门。新 CID8605642e…、noncefc193…、固定 image、private PID/init/network none/readonly 和原隔离身份完整；die/wait0、双 EOF、SUP/REAP Job ActiveProcesses0、owned reaper ended 有原证。最终 elapsed11、reserved0、settled累计71、starts2。中间未确认状态也保留。

B：_end_recovered_owned 只对唯一 preview/native registry、parent/birth/generation/boot 和 proof 的 CID/image/nonce 收口；当前链可由原 owned 登记及正常恢复来源核准推导 scope。函数没有单独再比较 owned.origin，列为条件风险而非已发生误杀，见第六节，不据此要求重做 G11 全套。

A+B：隔离 sealed-reader 由受信本地配置选目标，真实 dataset/instance/profile/只读角色及写拒绝先核，壳不持 source 写、factory、loader、maintenance、provider、preview 执行能力；没有 HTTP 任意 DSN/本机路径入口。R01 七类 GET、四类写409 和 Browser14 原 JS 实载可继承。Browser14 早于最后 caps.format 补丁，但该补丁只从已验证目标 profile 显示格式，未改变 R01 reader_profile 的兼容分支；API29—33 as-run 与当前源绑定已经核对。

A：正常 source 控制根6871594a… 的正式 activation55e4e1dc-e956-4a8d-801f-234580d6870e，generation0→1，target47369…/instance4259…；源 PG 先停止再目标启动，当前 overlay 所需 memory/source 两个 tombstone 均进入计划，current_missing[]、outstanding_owned[]。源 frozen、selector 永久 readonly、无 fallback、无换 target。隔离 reader 的只读事实不能代替这次正常激活事实，二者均有各自原件。

A 的失败边界：Browser15 整体 FAIL 保留。它的实际 activate200、原数据200响应被持有后释放、新 selector 下无后续 POST 可采信；write probe 使用非 canonical JSON header 得到 selection_changed，不能冒充 data_readonly 通过。Browser16 在原 selector/config/同目标重开，正确 canonical header 得到409 data_readonly，GET-only 且撤销记忆 body null；它补的是头部修正后的证明，不新建激活/恢复。

结论：正常新预览停止及两类只读入口的具体行为可以继承；旧首次未知和 Browser15 FAIL 保持，不能提升为历史全程均停止。

### 7. PDF 和 Windows 本机入口

A+B：C/PDF-diagnostic-admission 先冻结942字节样本和探针身份后才准入。pdf_probe.py 包装并返回原 parse/build/job/kernel 分支，不改原解析输出，不记录正文或 env；只在显式诊断夹具启用。原 supervisor/worker/Job 主体未改，10秒/256MiB/两进程未放宽。

A：真实 HTTP→parse entered→实际 Python/13 argv→Create/SetInfo/CreateProcess/Assign/Resume/Wait/GetExit 的受限 worker 链有阶段原件，worker约0.422秒退出0、341字节两页合法 payload，完整约0.453秒。PDF-two-page-confirmed 指向真实确认回执及 content GET，两物理页均 confirmed/ready，第二页补充仍是 user_supplement。确认后错误 GET404 是夹具路径错误，不推翻先前 COMMIT；旧两次422原因为未证，不能因新成功宣称已找出旧根因。

B：start_local.py 维持 Windows 原生 API/SUP/Job 与 Compose PG 分工，精确 CID、真实 DSN readiness、普通角色 schema 检查、回环和会话/同源认证、owned stdin 关闭和170/5/3收尾；Web 无 Docker socket，readonly 与错误脱敏调用链没有新放宽。

结论：PDF 新观察能力和本次成功链可继承 A+B，不要求未来 Linux/Nginx/公开部署的动态证明。原116所述 --profile/--initialize/--migrate 与启动前完整端口分类未全部成为 start_local 产品命令；这应在 STEP020/正常库迁移交接说明中明确，是交付边界观察，不把工程 runner 的检查冒产品功能，也不在本审计临时新增全平台门。

## 四、确定缺陷及最小修正

### D01 / P1：控制日志写入口可接受外来 hub 的有效日志

定位：[control.py:110](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/control.py:110) 的当前快照路径会验证首 hub.init.control_id；但 [commit:148](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/control.py:148)、[create_or_get_job:183](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/control.py:183) 和 [change_job:232](D:/shspic/project_NO3_RetroLume-agent/backend/app/data_exit/control.py:232) 均直接 _read/replay/_append，不比较当前实例 self.control_id。_read 只验证帧、hash 链及 canonical，不验证实例身份。

触发：实例已绑定 hub A 后，将其 journal 替换为另一个格式完整、hash 链有效的 hub B 日志，再调用上述持锁写入口。即使 assert_writable/state 会拒绝，写方法仍可追加到 B；create_or_get_job 还可能先返回 B 的同键事实。即使上层先做快照检查，检查与写之间没有同一次锁内身份承诺。

影响：控制事实可以跨 hub 混入，影响长期操作/selector/owned/fence 的权威归属。触发涉及私有日志被替换或恢复错配，不等同远程匿名可利用；审计没有实际替换任何日志或观察到跨库事故。按关键控制完整性 Must 评为 P1。

最小修正：抽出同一个锁内的完整当前字节/文件身份/首事件/control_id 校验，供所有读写入口调用；在该验证结果上 replay/CAS/append，保持尾帧拒绝、fsync 与 detached return，不只在调用者写前另调 assert_writable。最小验证沿现有 control snapshot 用例增加三条写路径的外来有效 hub 替换反例，确认日志零追加且不返回外来 job；保留原尾帧、同 size/mtime 篡改和取消/fence 证据，无需全量恢复重跑。

### D02 / P1（仅未来 Q）：合成外发 manifest 未约束模型消息中的用户/记忆正文

定位：[embedding.py:171](D:/shspic/project_NO3_RetroLume-agent/backend/app/capabilities/embedding.py:171) 的 OutboundSourceManifest.check_model 只核 catalog 的 fragment/source。实际模型消息另外包含 [teaching_service.py:509](D:/shspic/project_NO3_RetroLume-agent/backend/app/learning/teaching_service.py:509) 的 goal、answer_text、corrections/历史，以及 [interview/service.py:54](D:/shspic/project_NO3_RetroLume-agent/backend/app/interview/service.py:54) 的回答链 body 和 selected memory 背景。

触发：将来在有效 Q grant/固定活动内，资料与 query 均使用批准的合成项，但在本地保存另一段未批准真实回答，或选择未被 Q manifest 绑定的记忆，再 evaluate/review。现有源片段校验仍可通过，而实际模型 user 正文含这段内容。当前 Q 未启用、grant 默认关闭，但不能在未来启用时证明 synthetic-only；本审计没有读取私配或判定实际密钥状态。

影响：AP2 仅合成必要片段、不含本人学习记录/履历的权限边界未被实际模型请求闭合。没有实际出网或泄露证据；此项只阻断 Q，不能把正常本地保存本人文字本身列为产品缺陷。

最小修正：受信 Q manifest 同时约束可外发用户输入、selected memory 的版本/body hash 和必要派生上下文，或对已冻结合成动作的完整受控 user payload 建立可验证摘要/模板规则；在准入与 dispatch 前核完整范围，拒绝未批准正文。不能靠浏览器 synthetic 声明，也不应简单删除正常领域功能。用最低 transport 的不批准 answer/memory 反例证明零外发，保留正常合成样本；不需要向真实供方故意发送隐私或故障请求。

### D03 / P2：教学新 query→domain 链最后比较的是可变 owner，且缺 view 绑定

定位：[TeachingWorkspace.tsx:209](D:/shspic/project_NO3_RetroLume-agent/frontend/src/activities/TeachingWorkspace.tsx:209) 的 contextKey 不含 view_token、scope/head revision；[submit:320](D:/shspic/project_NO3_RetroLume-agent/frontend/src/activities/TeachingWorkspace.tsx:320) 的 stillCurrent 只核 mounted/activity/contextKey。query 初段捕获 owner，但后续 build/save/intent 等 await 后，[390 行](D:/shspic/project_NO3_RetroLume-agent/frontend/src/activities/TeachingWorkspace.tsx:390) 用新读取 currentOwner 比较可变 editorOwner.current，而不是原 owner。

触发：同一 activity 的 query 已确认后，在保存草稿/意图等 await 间从 owner A 变成 B，refresh 同时把 editorOwner.current 更新为 B，原 contextKey 又未变化；最后 B==B 可继续发 A 链的 domain POST。只有 view_token 改变也不会使 stillCurrent 失效。

影响：违反新检索链“原 owner/view 仍有效才发下一 POST”。服务器 scope/head/资格 CAS 能限制过期业务效果，不能把服务器拒绝当成前端从未发送。已有 Browser12 是另一 activity 的晚读，不能覆盖这个同 activity 分支；本审计未启动浏览器制造动态复现。

最小修正：在一次明确意图开始时捕获 owner/view_token/scope/head/DataContext，并让所有 await 后及紧接最终 POST 前都核同一份不可变身份；参考 [InterviewWorkspace.tsx:66](D:/shspic/project_NO3_RetroLume-agent/frontend/src/activities/InterviewWorkspace.tsx:66) 的现有做法。保留原 key 的 GET 和草稿，未发领域命令保持明确可恢复状态。只需定向晚 query/草稿保存后换同 activity owner/view 的正式 bundle 反例；不要求两域完整链重跑。

### D04 / P2：新检索和两域动作没有显示实际供应商

定位：[RetrievalPanel.tsx:12](D:/shspic/project_NO3_RetroLume-agent/frontend/src/activities/RetrievalPanel.tsx:12) 显示用途、请求、费用和时间，却没有 provider/model；前端 RetrievalStatus 也没有接入服务端 public 返回的 provider/model。TeachingWorkspace/InterviewWorkspace 的新动作没有补充该告知。旧 ActivityWorkspace 的 learning provider 展示不覆盖资料索引及这两个新入口。

触发/影响：用户在新入口点击确认索引或 query+model 时，看不到要发送给哪家供应商；不满足 SEC001 及116 B3 的告知要求。本地受信配置和文档可供人工核对，故按有替代的 P2 处理；这不能自动视为用户已接受 UI 限制，也不能签 Q 已满足告知。

最小修正：从受信只读 status/capabilities 展示索引/query 的实际 provider/model，以及整步后续聊天 provider、用途和有限预算，在确认前可见；不显示 key、内部 space/SQL 等实现细节。定向检查正式 bundle 对固定两 provider 的展示即可，既有零 provider 合成浏览器记录不能证明真实供应商告知已实现。

## 五、证据继承、FAIL 和 unknown 保留

28 场景不等同28个新根，也不等同28项都已在 Q 通过。本次按相应层次继承如下。

- L01—L05：学习链、确定 parser/手算、exposure、独立 exercise、同键及进度持久性，沿未改 policy、S03 真 PG/HTTP 和 S04/S05 UI 增量组合继承；实际供方对等价、否定、未知和数量级解释的语义仍未验证。
- L06—L09、I01—I03：概念/程序/歧义/冲突、面试 probe/支持边界的封闭结构和引用资格可继承；不能用固定合成回应证明开放语义、真实认可或真实缺证推断。无执行用户程序的新工具权限。
- L10：继承本次真实输入 ACK、seq2 PNG、reset ACK、ready 时点、Job/双EOF及结算；不外推原 G11 全部边界或长期学习效果。
- X01/X02/X10：PDF 两页确认和补充身份、记忆修订/撤销晚到、原 revoke 的物理 purge、源删除/overlay/向量失效，各采实际回执；旧422、清理失败和未知保留，不能改造为新 delete 命令。
- X03—X09/X12：同键/semantic slot、先 dispatch 后 invalidation、欠额整步拒、GET/显式继续和实际父消费闭包按具体分支继承；D03/D04 为当前未满足增量。真实 provider unknown 不做付费故障注入，原合成 unknown 原预留照留。
- X11：已有真实资源/端口/内存/迁移失败原件保持其工程层意义，不能把 runner 检查泛化成完整 start_local 产品 UX；未来交接说明按实际能力完成。
- P01—P03：采用真实两个目录/legacy、R01 reader、617行成功包及失败目标、正式 selector/readonly 重开，保留精确 profile/as-run 身份；不要求或声称恢复副本可继续 normal 执行。

原 events 中 63 条 failure 和 budget 中全部旧失败未改写；完整事实导航在 ledger-facts.json。特别保留：原45秒全局锁检查超时；迁移/恢复前向修补与两个失败目标；旧预览首次 UNCONFIRMED；Browser11 四个 observer error；Browser15 整体 FAIL；旧 PDF 两次422；确认后错误GET404；所有 dispatched→unknown、record_denied/late invalidated 和费用预留。后续成功各有新身份，不用其状态覆盖旧记录。

S06 当前读取原件显示各类未知不因刷新/重开恢复资格或退款。包中两笔 unknown 各250000、S03晚到 unknown、旧预览60秒保守项和新预览11秒分别保持。当前没有 PID/CID 或当前文件 frozen 不是历史 StopProof。

## 六、条件风险和非阻断观察

1. _end_recovered_owned 的 origin/scope 没有在函数内独立再比较。当前可验证正常链及唯一 owned 身份不显示误收口；因此是受限条件风险，不是第二个已证错杀缺陷。若修正接触该链，可顺手显式绑定原 scope 并只补唯一匹配/错 scope 定向反例，不重做32项宿主全套。

2. 未持有首次修改前字节的文件，只签当前源码审查，不补造基线。Browser proof 对 bundle 的实际 fetch 覆盖和四项磁盘 hash 也分开；没有由此要求无关重构建或浏览器全量重跑。

3. start_local 的初始化/迁移/端口诊断交付范围应在正常本机交接前明确。当前没有采用 Linux 全应用/Nginx/公网发布批次，不把它们升为 S 必需动态门。

4. 恢复副本永久只读、S06 原 source 已 frozen，是已批准切片边界。Q 需要新 normal 合成资源属于后续启用安排，不能误写成 S 恢复不能持续执行的缺陷。

## 七、S01—S06 执行控制事实

原 budget/events 是唯一工程账。本审计只归并读取，不写第二份可执行全局状态。最终 phase 为 returned_engineering_candidate、active_root null；roots24、PG create尝试/对象/卷均6、PGstart46、API33、Browser16、build7、Native140、HTTP2324、preview create/start2、provider0、费用0。未用 S根25/API34/PG47 不授本审计。

按各有效 permit 的当时上限核账，后续 scheduling amendments 只对应其明示未来计数，不套原初 caps 给后来已批准新增，也不反向赦免旧超额。

- S01：活动37651.0027854/28800秒；PG实际持有16216.391/14400，保守计16219.36；offline1724.875/7200。最早硬门事件已记录 activity36673.425，最后返还包含后续保存。平台审批/账号中断时资源仍被持有的区间不能豁免，也不能断言全程行为均有观察。
- S02：活动17303.702146/28800；新增持有5705.063/10800；offline821.686/3600。计数按已采用 scheduling amendments 核，不回零旧根和失败。该段数值合规不改变 S01 结论。
- S03：活动31724.280143/21600；新增持有1555.313/10800；offline3682.780117/3000。首工具漏采钟，账用许可发出时刻作保守更早下界，后续可靠同步点单存；不能把该下界写成真正首工具时钟。
- S04：活动4127.187/14400；持有1344.734/7200；offline2782.296/2400，累计9011.637117/9000，累计超11.637117。超额保留。
- S05：活动16611.729874/21600；持有159.953/7200；offline16451.527874/10800，段超5651.527874；累计25463.164991/19812，超5651.164991。大段未观察空档按规则保守计入，不称真实 CPU，也不因账号中断追减。
- S06：活动12244.341136/14400；持有139.233/5400；离线进程保守257.6443102/1800。连续无资源12104.874136没有第二滚动 offline cap，null 不是0，也不能退回旧段上限。其真实首点为2026-10-16T13:00:19.1708422Z、host QPC885179903576/freq1e7；controller起点88517923864000ns另有保守20ms时钟桥说明，不把不同字段硬当完全相同。pause0；resume-gap 未找到预记暂停，未知空档保留活动/无资源投入。没有据此宣称完整持续监控。

审计独立比较证明：S06以前 segments 原对象、最初21个root、failure原前缀均完整保持；events旧730929字节、SHA2560ef0646bdd2855f9fc9dc1cc2a0622c0d5c6e125cc82d7acc5642e81a0d59c0e 为当前精确前缀。没有用 S06 新门重算旧违规。

最终停止记录是2026-10-16T15:45:05Z 的六个准确 PG CID 非 running/Pid0、无占用端口和42个已登记 birth 的当时观测；新预览另有 Job0/双EOF证明。主控与本审计均未重新查询实时 Docker/PG，故只签该次原始停止记录和当前文件封存，不能声称2026-10-17实时系统全部停止。

## 八、Q 仍缺的可验证启用条件

Q 必须继续单列未启用，现有 AP2 条件批准无需重复询问。以下条件只影响后续付费启用及相应语义，不冻结已充分证明的普通合成实现。

1. 合并修正 D01—D04，尤其 synthetic-only 完整模型消息范围与真实供应商告知。此后独审只核实际改动和最小反例，保留本次有效结论。

2. 获得后续卡的精确联网范围后，核官方现行 DeepSeek chat configured/returned model、thinking disabled/结构输出与无额外思考账单，以及智谱 embedding-3 的512维/批量/返回身份/usage、端点、账号适用性、保留/训练条款和现行币种价格。候选字符串和旧官方快照不是今天可用性承诺；本卡没有公网额度，未作此核验。

3. 形成逐动作最坏调用矩阵与费率摘要。单次 model/embedding 保守预留250000 microunits，价率上界留至少25%余量；总额80次/20000000 microunits，学习40/10元、面试24/6元、补证16/4元，失败/超时/unknown全计。按实际剩余语义用例计算 index批次、query+chat、追问和HTML所需次数，80内不足就交缺口，不能偷偷加额度或换模型/延10秒。

4. 在获准的新 normal 合成库/控制根，用最低合成 transport、零外部请求，补一批真实 PG 组合证据：两种 provider 都经原生产 admission，真实 roster SUM、同一全局锁、活动/操作持久预扣与 COMMIT 共同成立；边界竞争只允许一个提交，失败/unknown不退款、重开不归零。无需故意向供方发错请求，也无需重跑旧28场景或重装载617行恢复目标。

5. 账号/key 通过正常本地 secret loader 配置，模型和 embedding 环境名隔离，不能把 key 发到对话/浏览器/证据/包。由后续正常配置自检给非敏感 readiness，而不是本审计读取私配或索凭据。

6. 固定 Q 新活动 roster 和受信 source/input manifest、price snapshot、official checks、72小时 valid_from/valid_until 与主控明确 Q 启用回执形成一致身份后才启用。72小时从未来 grant 生效起算，不能用本审计日期代填。

7. 当前 S source 控制根已永久 readonly、源库 frozen，不可回 normal 或往该根写新 Q roster。后续卡明确新 normal 合成库/控制根及资源许可，保留所有历史而不借新根清零。已有80次/20元条件批准继续受总账约束；旧13元失败已用账不抵扣。

8. Q 启用后仅补真实服务语义：至少 L01、L02—L04关键正反、L06三答、L07二答、L08/L09、I01—I03及当前题解释至L10的逐例 rubric。封闭结构、位置正确不等于语义支持；不足、冲突、部分认可和自报分别记录，长期效果不冒通过。只从已 COMMIT 处 GET 继续，不付费重放安全故障。

## 九、本审计独立性、投入、偏差与交回

实际执行环境是 Codex desktop 会话中的内置 collaboration 新独立执行上下文，fork_turns=none，共享文件系统但未继承父聊天/TASK117实施历史。它不是新建桌面侧栏 chat，也不是另一个外部客户端。A+ 是用户资源路由标签，精确后台模型 ID/变体及是否不同家族无法确认，未发明身份。父会话只给原始任务路由、状态请求和可读性要求，没有给实现自评或审计预判；本审计没有再委派代理。

未读 TASK117结果正文、备份正文、实施聊天/推理、其他 Agent 记忆或个人 memory 文件。TASK117 结果只按原始 bytes/hash 和旧体后缀比较；原账的 failure/permit 是控制事实，不用其实施者自评段作证明。路由详情见 [isolation-dispatch.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/audit/isolation-dispatch.json)。父路由会话首工具先读卡、第二工具才采钟的偏差已在该文件披露，未追造其首点；本独审首工具确实直接同步 UTC/host monotonic。

本独审首点为2026-10-17T00:03:14.5869924Z，host ticks1282926956509，freq10000000。所有读取、思考、保存和复读计入本段活动；没有预记暂停或外部等待、没有启动在途产品资源。最终活动与 metadata 进程 wall-time 汇总及报告复读 hash 见 audit-execution-receipt.json，均远低于14400/1800秒；没有进入10800新族停止或13200只保存门。进程 wall-time 是保守元数据命令耗时，不称 CPU，也不算工程第25根。产品真实运行、外部网络、provider和费用均为0。

实际验证仅用 PowerShell 的定向读取/rg/当前钟，及已有 Python 标准库的 read/hash/JSON/AST/有限 diff/ZIP/账目归并；图片只由标准本地图片查看工具读取。未 import 产品、执行原 runner、compile/unittest/SQL/PG/Docker/WindowsJob/API/Browser/Node，不安装依赖、不读取 env值/私配/密钥、不解DPAPI、不执行 Git 写入。

元数据失败保留：初次 stdout 编码乱码后固定UTF-8并针对性重读；初次缺失文件 bytes=null 与原记录0造成8个假不匹配，按原语义修正为0后重核；若干路径猜测/不存在目录及一次误选 JSON summary 字段得到非零退出，随后用文件索引/实际 keys 定位。大型输出截断仅作定位，核心断言改用小范围/摘要核对。四个 audit_meta 读取/选择错误留在 metadata-commands.jsonl，其余 rg/路径错误保留在工具记录；这些不是产品失败、也未删除历史。没有出现同一问题两次有据修正仍失败后机械重试，冻结稳定，未触发受影响对象停止门。

主控必要同步建议：在 [执行动态文档](D:/shspic/project_NO3_RetroLume-agent/DocuS/执行动态文档.MD) 登记本 R112 已返回、三轴建议、S未验收/Q未启用及合并修正归属；在 [架构动态文档](D:/shspic/project_NO3_RetroLume-agent/DocuS/架构动态文档.MD) 仅按实际修正更新完整出站范围和控制写身份说明；正常运行交接时使 README 与真实 startup/迁移能力一致。由主控在其串行维护时记录 UTC/Asia-Shanghai 时间、最终状态及需要的文档变更记录，本窗没有改共享文档。需求不因审计降低，用户原始需求不改。

必要用户动作：无。本卡不索凭据、不让用户执行代码、不重新请求80次/20元条件许可。下一步由主控合并 D01—D04 派回原工程窗；修正后本窗作必要增量复核，再由后续明确 Q 卡处理官方核验、正常配置、真实 PG 组合补证及启用回执。没有额外编号/经验入库写入，未以未证根因申请合格经验。

本报告与审计证据已保存；最终复读收据只证明文件可访问及内容核对，不替代主控裁定。
