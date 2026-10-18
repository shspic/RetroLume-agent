# TASK-117 / R-111 — S08 保留初版、补齐四项修复与定向验证

## 完整成果、窗口与授权

你是 A+ 增强工程执行者，继续刚交回 S07 的 TASK117 原工程窗口。以已经保存的六份初版源码为起点，完成 D01—D03 的普通复查、必要修正和测试，完成 D04，再集中完成后端/typecheck/build及正式 bundle 的最小浏览器验证，交回一个稳定可审候选。不要重新研究全部 STEP018、重写现有初版、再交只读提案或逐个普通步骤回传。

沿用原 A+ 窗；仅原资源不可用时由一个 A+ 接续窗独占，原窗停止。标签不冒充真实模型身份，记录真实客户端/可知型号。仍人工转卡，不再委派子 Agent，不向审计窗转实施聊天。TASK仍117、R仍111，无新TASK119，原118独审仅在稳定后复核实际增量。

根目录 D:/shspic/project_NO3_RetroLume-agent；入口 D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。task_model/V4.0、公共AGENTS CHG-0003、阶段07；需求v1.3、架构v1.42、执行动态v2.69。公共只读根 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4，读其DocuS/AGENTS.MD，适用WORK第2章task_model、第4—6、8—9章和task_model/prompts/07_开发执行循环.md；七锁定身份仍本项目DocuN/evidence/v4-migration-20260930/rules-snapshot.json。同窗已经读取、未变正文直接复用，不混入后来版本。

用户已批准116 AP1/AP2及继续开发，四项仍是原批准边界的缺陷修复。主控本次前向许可为 TASK-117-STEP018-AUDIT-REPAIR-S08-20261017，见 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/orchestration-s08-20261017/continuation-permit.json。许可只向前生效，不赦免S07或其它历史超额。Q/真实provider/真实费用始终0，80次20元仍为未来条件许可，不要求用户再次批准，也不得自制正式启用文件。

## 先核断点，只补剩余

1. 原结果 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-117-result.md，88265字节，SHA256 fc600e1381e44542fc933bdd294e471e2e1a5d4b70b979a5a2be708878993aab。S07明确未完成；末79709字节与原S06精确相同。本轮置顶S08时保留全部88265旧字节，不改失败、时间、not_run或旧结论。
2. D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/execution/continuation-06/ 的 receipt.json、post-source-manifest.json、changes.json/preimages、S07-product.diff、as-run.json、final-timing.json、final-binding.json、bundle-7-post.json、final-stop-observation.json；本次主控核证、输入和许可在orchestration-s08-20261017/received-s07.json、input-manifest.json、continuation-permit.json。同窗只补本次增量。
3. 原TASK118结果 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-118-result.md 第四节及证据继承/Q门，41590字节/dd0a5f1d2ddb2ffcd9a168496e4cca5b8292b7221977c76b8ff417f9ff0f21f1；原TASK116批准合同、X02纠正和原S06有效证据按四项实际依赖复用，不重采。
4. D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-117-work-decision.md 本次置顶，以及原源码和直接测试。原S07完整卡已备份在本次before-documents/TASK-117.md，作为历史合同，不恢复其已到限运行权。

本次核证S07清单15项均匹配、旧原件前缀/后缀保持，确实只有6个产品文件变化。D01 control.py 已抽取_validated_locked，当前SHA256 0db51f9ff61f4005854f32007d3c0727d966c062f33e0a64c0a56af8b926bf7e。D02 embedding.py=09e788f3e2207349b6bd5a11df2ec25a09893e8b0a504399332fbd44c5863e41，gateway.py=07f38bf2e4c11a7ca6be31b2cf9290e6a9db9ee349299f992d93bc692149bfc7。D03 TeachingWorkspace.tsx=8e1b851ceba2180755b61925f6c8ad6551eba0190a93b2cf7811c6b3cf947dd6，teachingIntents.ts=031464bac96413c8c72cb068e0a82555b0d17a131470dc2a55174f11e0f0a2ce，teachingApi.ts=1bca0ed927e1b03fc8b893b732d527841d7efb29d68b29f51cd04e6daf330afd。不能据“已落盘”声称修复通过；先定向普通复查和补测试，发现具体问题直接修。

D02初版增加有限model_requests批准对，结合完整payload及typed request摘要，空字段拟保持旧Embedding清单hash；还缺实际装载/私有传递、旧wire/Embedding兼容、正常批准send和拒绝反例。D03初版已捕获owner/view/head/scope/DataContext并调整草稿、POST和domain_sent时序，类型/原键恢复及真实竞态尚未核实。D04完全未实施。测试、typecheck、build、浏览器、控制器边界自检全部not_run；不要把未执行的修正计为第二次失败，也不要为了确认缺口原样运行已知不兼容夹具。

当前dist四项仍为原bundle7，主JS 58a87abf5ff4b02b33aab5dc3735507f4f097791e021aeb4ddfbf0b62ac115e8，不包含S07教学源码。旧bundle文件和原件继续保存，本轮必须在实现收齐后生成并实载新正式产物。

当前唯一工程账execution/budget.json phase=S07_returned_incomplete_activity_limit、active_root=null。S07未开任何根或浏览器/服务器：累计root24、Browser16、build7、fixture_server0、HTTP2324；PG创建尝试/对象/卷6、PGstart46、产品API33、Native140、preview各2、provider费用0保持。本卡仅重新授权未消费的3根/3Browser/2build/3fixture server/600HTTP，累计cap不增加，不挪未来Q预留。

S07首点2026-10-17T01:14:01.395492Z，最终复读2026-10-17T09:38:56.049183Z，保守活动30294.653691秒/21600，超8694.653691秒。宿主单调值低于起点，连续时钟域未知，不能把差值变负数、重置旧起点或补造pause。没有新测试根，不是“验证又失败”。旧63条失败前缀保持，新增三条控制/观察事实累计66；metadata wall漏记仍unknown，受控验证0秒不代表全部进程0耗时。

下面四项验收正文沿用有效S07合同。各“现状”指118审计基线，不要求撤回S07六份初版；以本卡当前hash接续。原要求不降低，本轮实际目标是把它们全部实现并验证。


## 四项有效验收合同


### D01 / P1 控制日志全部写入口绑定当前 hub

现状是 _current_snapshot 在锁内校验完整当前字节、文件身份、首 hub.init.control_id，commit、create_or_get_job、change_job 却直接 _read/replay/append。有效 foreign hub B 日志替换 hub A 日志后，写方法能混入 B，same-key 还可能返回 B 的事实。

抽取或复用一个真实锁内的完整字节、文件身份、首事件和当前 control_id 校验入口，让上述读写路径在同一已校验快照上 replay/CAS/append。不能只在调用者提前 assert_writable 后再进另一次锁，也不能只修一个写方法。保留合法完整前缀 GET、写残尾拒绝、同size/mtime篡改检查、fsync、取消/fence/CAS、容量上限和返回副本；不改日志格式或旧日志本身。

在本轮自建的局部临时 hub 上沿真实 ControlHub/FileLock 加三个外来有效日志反例，分别调用 commit、create_or_get_job、change_job；后者包含相同业务键/可命中 foreign job 的情形。先可建立合法读缓存，再换成格式/hash链完整的另一个 hub。必须拒绝，替换后的字节零追加、零返回外来 job，错误归属清楚。同时跑原 SnapshotTests 的直接受影响分支及至少一条合法写/peer取消正例。不要替换任何真实 S 控制根，不重跑617行恢复或真实预览。

### D02 / P1 仅未来 Q 的 synthetic-only 全消息范围

现状 check_model 只核资料 catalog/source，而目标、answer、corrections/history、selected memory 等实际模型正文未被 manifest 约束。目前没有真实泄露，本缺陷只阻断 Q；本地保存正常用户文字本身合法。

在原受信 operator manifest/网关边界做最小完整收口。允许给本地 manifest 增加有限、严格校验的完整受控 payload 摘要，或能闭合全部实际发送正文的有限模板/正文与记忆版本hash规则；由你选择符合现实现的最小方法。覆盖实际发出的 system/user/history/selected memory/派生上下文；固定受信协议模板可单列绑定，不能只声明“synthetic”或只核来源列表。任何会发送的自由正文都必须有清晰的受信批准来源。说明动态ID、服务生成上下文及后续有限 Q 样本如何取得可执行批准，不能把所有请求一律拒绝当完成，也不能收到任意正文后自动将其加入白名单。

准入前以及 dispatch 前核对实际将发送的完整对象与同一受信清单。await 期间对象或配置变化不能使已核对象与最终 transport payload 不同。旧 grant/manifest 缺少完整范围时外发失败关闭；无 grant 的本地非外网合成路径和普通本地保存不删功能。保持当前 typed wire v3/v4、model/tool/embedding隔离、原账面语义；新 manifest hash 必须贯通既有配置装载、grant绑定和私有传递，不偷偷复用旧 hash。

验证调用实际网关与其最低 transport 接口，ledger/响应可用已有有限替身。正常已批准合成 model 请求能抵达一次替身 send；不批准 answer、goal/history、selected memory正文或版本、完整payload篡改均零外发。至少一个反例直接绑定真实 teaching/interview 消息装配形状，不只测 SimpleNamespace 的 catalog。未批准内容应在准入前拒绝；若测试覆盖准入后才变化，则保守已预扣保持、dispatch/send不继续，不退款/不重发。原 embedding/query 范围、旧 wire 和 grant失效用例按受影响方法回归。所谓 send 只准本机替身，不得向真实供方故意发隐私或错误请求。

测试grant/费率/receipt只能是明确test-only的隔离夹具；不能写入正常operator配置、伪造正式Q启用文件，或将夹具的capabilities_verified当作官方能力已核。真实Q仍关闭。

本地 manifest 的必要验证字段收紧属于原合成范围修复，允许同步公开无秘密样例和直接解析处；不需要新数据库列，不改 HTTP 写合同或持久 grant字段。若确实必须改变主要模型/公开接口，先交具体冲突并完成其它三项，不自行实施。

### D03 / P2 教学 query→domain 原身份与晚到围栏

现状 contextKey 不含 view_token/scope/head，最后重读 currentOwner 与同样已变化的 editorOwner 比较，会使原 owner A 链在同 activity owner B 中继续发 domain POST。服务器拒绝不能替代客户端未发送。

在一次显式意图起点捕获不可变 activity、owner、view_token、scope/head revision、DataContext/namespace 及原 key；所有相关 await 后及最终 POST 前核对同一身份，不能拿两个新值互比。参考当前 InterviewWorkspace 的捕获模式，只改实际教学链及直接依赖。query 已提交事实、原键 GET、完整草稿与尚未发出的 domain 动作保留；不得提前标 domain_sent 后身份失效却让界面误称已交付。不能自动重发、改绑新owner或删除原意图。

检查真正的时间窗。query 已返回之后，在 build/save draft/intent 等可控 await 暂停，再只改变同 activity owner，或只改变 view_token；旧实现仍可走到的分支，修后均无后续 domain POST。再覆盖scope/head或DataContext变化，至少一条身份不变成功对照能恰一次发送，原意图可只读核对。浏览器必须装载正式构建 bundle，不靠注入更改产品 guard 或伪造组件内部已通过；可延迟 IndexedDB/合成HTTP回包并驱动正常刷新/页面事件来构成窗口，说明替身边界和辨别力。

### D04 / P2 显示真实配置的供应商告知

从服务端受信只读 retrieval/status 和 activities/capabilities 的现有 public 字段接入实际 provider/model。索引确认前显示其向量供应商/模型/用途/单批预算；教学和面试 query+model 确认前同时显示向量服务与后续聊天服务、用途、两笔请求/费用/时间。不得硬编码展示“已配置服务”替代真实身份，不暴露key、DSN、私有空间、SQL/内部路径。

字段缺失、坏格式或资格未知时明确无法核对，不静默猜测供应商；缺告知的相关外发动作不应悄悄启用。本地零费保存、取消、只读查看保持原资格。优先前端消费现有字段，不新增API或后台配置能力。正式 bundle 的定向合成浏览器场景验证索引、教学、面试三处确认前内容；provider/model来自受控只读fixture字段，至少一项改值对照证明没有写死文案。记录这是真实浏览器/正式产物与合成HTTP，不冒真实 provider 或PG集成。


## 写入范围与隔离


本卡唯一工程写入者。审计窗保持产品只读；无其它卡可同时写本范围。修改前逐文件存pre原字节/hash，形成有限统一diff和最终/post/as-run清单。

允许的产品改动是 D:/shspic/project_NO3_RetroLume-agent/ 下 backend/app/data_exit/control.py，backend/app/capabilities/embedding.py、gateway.py，frontend/src/activities/TeachingWorkspace.tsx、InterviewWorkspace.tsx、RetrievalPanel.tsx、retrieval-api.ts、ActivityWorkspace.tsx；backend/app/service_config.py、backend/app/retrieval/service.py 仅在受信manifest装载或现有public字段确需适配时最小修改；frontend/src/activities/teachingIntents.ts、teachingDrafts.ts、teachingApi.ts 与 frontend/src/data/context.tsx 仅在原身份/草稿恢复直接依赖确需时最小修改。每个文件标明 D 编号和因果。不要为修D03顺手重写面试流程。

允许修改既有三个定向测试 test_step018_control_snapshot.py、test_step018_flows.py、test_step018_embedding_contracts.py，新增 backend/tests/test_step018_audit_repairs.py 与必要的 backend/tests/fixtures/step018/s08_ 前缀离线夹具；新增 frontend/tests/step018-s08.mjs 及必要的同前缀loopback夹具。fixtures只能测实际产品，不替换实现。README.md、config/integration.example.json 仅更新实际manifest/告知限制及本轮精确状态。frontend/dist 仅由获准正式构建生成，旧bundle7先另存完整字节和hash，不手改构建产物。

新工程证据仅入 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/execution/continuation-07/，原 execution/budget.json、events.jsonl、case-index.json 按原机制追加本段，不回写旧段。原报告只置顶 S07 保留88265字节后缀。局部文件锁测试的自建合成hub与测试浏览器profile必须归本轮准确目录，关闭句柄/进程并保留文件；不要批量删除任何旧证据或临时目录。

禁止修改001—014、数据库/持久模型、来源资料/已sealed包、全部旧控制根与selector/fence、权限/退款/停止/preview安全语义、固定镜像/renderer/签票器、依赖/锁、公共提示词、原始需求/DocuS/任务卡/主控裁定/独审原件、Git HEAD/index/config及远端。不得安装/联网/读取真实密钥/用户配置或DB，不解DPAPI，不commit/push。GitHub origin现有https://github.com/shspic/RetroLume-agent.git保持；公开候选清单可按本轮源/README变化更新，但不上传。

原source已frozen，正式selector已永久readonly，全部六PG容器和原owned/preview都不得启动、修改或清理。本卡PG/SQL/Docker/产品API/Windows业务监督/真实provider/费用的新增执行额度全部0。D01用隔离真实本地文件锁，D02用实际gateway+合成ledger/最低transport，D03/D04用正式dist+本机合成HTTP；不需要配置真实key，也不需要新normal数据库。真实PG roster SUM/两provider持久预扣共同提交的组合补证保留在后续Q前置，不用本卡替身结果冒充它已通过。


## 前向计时修正、剩余许可与最小运行门

本段采取48小时日历有效期，加实际命令进程wall-time、runtime持有和次数硬门。明确不再以“从首工具到封存的跨中断UTC总差”作为本段活动硬停止门；该差值继续记录为上界，未知空档不称实际工作或0。旧S07活动门、超额和其它历史控制判断完全保留，这不是回溯修改。阅读/思考/编写投入尽可能按可观测段登记，平台中断只能据已有记录说明，不能制造精确CPU/在线时长。

许可从实际收到本卡后的首工具采样起48小时；首工具同步UTC、宿主单调值及本次控制器时钟身份，保存真实接收点，不拿签发时间冒首工具。日历剩余少于1200秒停止新实施/检查，只清场保存。离线子进程累计wall-time上限3600秒，运行资源持有并集上限3600秒；每次运行都取日历、进程、持有、原根剩余中最短者作实际截止。所有read/hash/编辑辅助/测试/typecheck/build等命令耗时入子账，无法包住的工具命令以真实工具收据补记，缺收据就unknown，不能全部挂0。嵌套已计进程不为省账退时，不重复称精确CPU。

未消费次数保持原cap。最多3个完整合成浏览器根，编号25—27，每根1500秒检查+300秒清场；Browser最多3次累计19，正式build最多2次累计9，loopback fixture server最多3次累计3，全部实际HTTP新增最多600累计2924。PG创建/对象/卷6、PGstart46、产品API33、Native140、preview各2、provider费用0冻结不加。没有失败依据不为了用满次数加试；纯离线检查不占真实根。根内正常步骤和有据普通修正可在原截止内连续，不能几十秒失败就换根；同问题两次有据修正仍失败即停依赖。

本段仅监听127.0.0.1:18119。沿原低内存门，fixture server最低512MiB、Browser最低768MiB；约2秒采样，连续两次低于256MiB触发准确自有清场。无PG/Docker/产品API，不需要Docker暖机或2GiB，不再让用户释放内存。端口被他人占用不杀进程或偷换端口；环境门只阻断对应真实检查，其余离线交付继续。外网请求显式阻断，原六CID/旧控制根不启动、不解密、不变更。

### 先完成有限控制修补，不能再原样使用S07 guard

S07初版guard直接比较持久start_mono_ns，跨宿主域会出现负值；run的超时只包单进程，没有本次完整browser/server独立清场和准确pid/birth闭包，边界自检也没跑。本轮先在continuation-07构造明确S08入口，保留旧controller只读，不能靠fallback旧permit或把负耗时当剩余许可。

1. 重启/恢复后先核active_root、原登记pid/birth、18119与资源归属，再建立本段当前宿主anchor。每次持久化最后可信UTC/mono/控制器实例身份；mono倒退、时钟域无法确认或UTC明显倒退时拒绝沿旧mono继续。旧采样保留，按UTC记录未知上界；只能在本卡原48h及剩余次数/进程/持有许可内重新锚定当前本机检查，不能重置本段首点、日历、累计次数或给在途根新截止。
2. 若发现可能在途根/进程，先按准确归属收尾；旧运行截止不能映射时停止该运行，不带着unknown继续业务。无资源且active_root空时才可从已存检查点恢复本卡余项。没有可核边界就交具体阻断，不自行推断重启原因或动用户进程。
3. 运行前安装独立截止/压力清场及stdin/父退出机制，登记准确pid+birth和浏览器子树；Agent中断后仍能在原根截止收掉自有server/browser。实现限本卡测试控制器，不新增产品看门平台。异常、超时、压力退出或finally都先停止新增，等待观察任务、关context/Browser、关server，核18119释放，再封存输出。CIM不可用可用当前普通权限可核的进程/句柄/StartTime办法；不为观察而请求升权或杀同名所有进程。
4. 使用纯时钟替身做一次有限自检，覆盖许可身份、日历到限、mono倒退/跨域、未结束进程、累计次数和持有到限、子进程超时后的关闭闭包；不改系统时间。自检仅验证本卡控制层，不冒产品安全通过。首次自检和普通修正按本段真实记录，确认后再做产品检查。

### 连续实施与集中检查顺序

先普通复查六份初版，补D04、D01/D02测试及旧夹具必要适配、D02本地无秘密样例/README；类型检查包含草稿和意图新增字段及guard调用者，不能只凭文本替换完成。实现收齐后集中运行实际受影响的后端方法与typecheck，成功后正式build，再一根跑D03/D04最小合成浏览器矩阵。不增加新的研究阶段或提前独审，不跑旧28场景、真实两域全链、PG、恢复、PDF、preview。

复用原严格边界而补足辨别力。D01验证三写入口拒外来有效hub且零追加；D02正常批准最低transport恰一次send、不批准answer/history/memory零send及await变化保守、旧Embedding与wire；D03必须是同activity、query确认之后、草稿/意图await期间owner/view/head/scope或DataContext变化后的下一POST抑制，而不是换另一个activity；还要正常一次POST和草稿/原键可恢复；D04正式bundle三处确认前真实配置provider/model/用途预算、缺字段门和至少一处改值对照。

浏览器HTTP允许封闭合成fixture，数据库真实验证本段0。测试前先按当前组件/返回类型检查脚本字段/按钮/路由，异步观察窗不得把显式POST自身算自动重发。按源码和脚本交点安排暂停屏障，不注入产品guard或伪造内部通过；无法构成某个理论owner变换时给真实可达性依据及同风险替代检查，不编造浏览器场景已发生。scope/head/选择器CAS仍不能替代前端未发送证据。

每个实际失败先保存日志、定归产品/夹具/环境，有具体修正才复检受影响项。所有检查有命令、退出码、当前源码hash、正式bundle实际fetch hash、请求/响应时间线和原键；typecheck/build/mock各自分层，不冒真实PG/供方、完整语义或独审通过。已充分未变事实直接继承，涉及改动的原断言必须重新绑定，不能把bundle7拿来覆盖本轮新源码。

## 统一收口、独审与回传

新工程证据只写 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/execution/continuation-07/，唯一execution/budget.json、events.jsonl、case-index.json只追加S08段和真实累计；旧S07完整对象和unknown不改。允许本段产生自己的control/runner/测试夹具，但产品不得依赖DocuN实现。首份S08源preimage从当前六份初版起，另引用S07原preimage形成链，不覆盖初版或审计基线。

完成四项、相应最小验证和精确清场即停，剩余额度不追加实验。硬门到、同问题两次有据修正仍失败、新高风险/持久模型/公开写接口/权限费用改变、并行写冲突时停止依赖并完成可独立部分，统一交回真实缺口。本段不保证永不失败，不用到限替代原因定位。

结果仍保存 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-117-result.md，S08置顶，原88265字节精确后缀保留。给出四项完成/未完成与实际接口/manifest兼容、pre/diff/post/as-run及最终bundle加载、正常/反例与局限、全部失败/修正、S08时钟政策和观察/unknown、实际进程与资源耗时/累计次数、精确本轮停止，不能把没有查过的原PG说成实时停机。逐项可重建，保存后完整复读。

工程候选稳定后由主控回原TASK118独立上下文一次增量复核四项及影响，不重开全范围审计；本卡不自签。Q仍需官方当前能力/价格/条款、正常本地secret loader、新normal合成库/控制根、真实持久共享总门组合证、实际受信清单/72h和主控启用回执；不重问原80次20元批准，不消费它，不解冻原source/selector。

无需用户密钥、删除资料或手工运行命令。DocuS/共享编号/总进度/主控裁定不由工程修改；不修改TASK118结果或历史原件。确认完整结果真实保存且可读后，只回一句真实结论及完整可点击绝对路径。
