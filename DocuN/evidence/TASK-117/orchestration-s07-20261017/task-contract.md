# TASK-117 / R-111 — S07 集中独审四项缺陷合并修正与定向验证

## 一个完整成果与接收安排

你是本卡 A+ 增强工程执行者。继续 TASK117 S06 原工程窗口，一次完成 TASK118 独审 D01—D04 的必要实现、相关离线验证、正式前端包定向浏览器检查与证据收口。普通步骤在卡内连续完成，不逐项回传；不是再交一份设计提案，不重做全部 STEP018，不启用 Q，不自签独审或项目验收。

优先刚交回 S06 的原 A+ 工程窗。仅原账号资源确实不可用时，允许一个可用 A+ 接续窗独占；原窗停止，TASK/R/历史失败/投入不重置。资源档位不冒充真实模型身份。仍由用户人工转卡，禁止再委派子 Agent、另开并行实施或借 TASK118 审计窗实施修复。

根目录 D:/shspic/project_NO3_RetroLume-agent，入口 D:/shspic/project_NO3_RetroLume-agent/AGENTS.md。模式 task_model/V4.0，公共 AGENTS CHG-0003，阶段 07；需求 v1.3、架构 v1.41、执行动态 v2.68。公共只读根 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4。读取其 DocuS/AGENTS.MD，七项锁定身份见本项目 DocuN/evidence/v4-migration-20260930/rules-snapshot.json；适用公共 WORK 第2章 task_model、第4—6、8—9章和 task_model/prompts/07_开发执行循环.md。同窗未变正文复用，不能暗中采用新公共版本。

授权依据是用户已批准 TASK116 AP1/AP2、连续开发及本次 TASK118 真实回传，主控核证见 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-118-work-decision.md。四项均修复已批准边界，不新增需求、持久模型或公开写接口。当前只授权零外网合成修正与取证；80次/20元是尚未启用的未来 Q 条件许可，不能用本卡伪造其启用回执或重置旧13元账。

## 必要输入与真实断点

按顺序补读以下实际文件，同窗有效原件不全文重读。

1. 本入口与公共适用规则；D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-118-result.md 第四节四项缺陷、第一节三轴、第五至八节继承/历史/未来 Q 门。报告41590字节，SHA256 dd0a5f1d2ddb2ffcd9a168496e4cca5b8292b7221977c76b8ff417f9ff0f21f1。独审只读零业务运行，报告交付可接收，所审产品代码仍不通过。
2. D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-117-work-decision.md 本次置顶裁定；D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/orchestration-s07-20261017/received-audit.json、input-manifest.json、continuation-permit.json。
3. D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-116/design/ 的原采用包、integration、acceptance、sample-inputs，及 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/orchestration-s06-20261016/X02-contract-correction.md，仅取四项依赖。最终需求 SEC001、NFR005、DR002 及原 synthetic-only 边界不降低。
4. 四项实际源码和直接调用方，见下文允许文件；已有 backend/tests/test_step018_control_snapshot.py、test_step018_flows.py、test_step018_embedding_contracts.py，frontend/tests/step018-s05.mjs 只借用正式 bundle 装载、网络时间线和 owner 观察方法，不运行其原 PG/业务链。
5. 原 S06 只按所需原件复用。D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/execution/continuation-05/ 的 final-source-manifest.json 163项、final-binding.json 27项、final-budget-observed.json、final-resource-stop-binding.json；D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-118/audit/ 的 final-freeze.json、source-review-before-runtime.md、raw-bindings.json 和相关缺陷定位。审计有效结论与证据不重采。

主控本轮重算独审256组身份均匹配。关键源码 control.py=38f3cecdb47170f62b7535bc08b297ce47144f873c721b7403f9b55870c6a281，embedding.py=add2b66759bf19475010dd6e68ce7ceef322f608f4a8bdd30781caeb119a7c80，gateway.py=5e915fd642e2c7e80dea04dbac7f472fd56f2ee92a2c64f596177f2af8c36a9f，TeachingWorkspace.tsx=a0c85185a025c77a4f912ff7f7f8c6f68e4154781745295b6f705da986e60b31，其余以 input-manifest 为准。开工比对；不符先查归属，不覆盖别人改动。

原工程报告 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-117-result.md 为79709字节，SHA256 b596ab87ae3facc605dab65acbf9c708c784c11b1f8581b75ddc6611ad802ac9。本轮置顶 S07，整段旧字节保持精确后缀。原账 execution/budget.json phase=S06_returned_engineering_candidate，active_root=null；仅文件状态，不代表本轮实时系统查询。

原累计 roots24、PG创建尝试/对象/卷各6、PGstart46、产品API33、Browser16、build7、Native140、HTTP2324、preview创建/启动各2、provider/费用0。S01/S03活动与持有等超额、S04/S05离线超额、漏采/unknown/失败63条及所有原许可保持，不拿新许可追认旧控制通过。S06活动12244.341136、持有139.233、离线进程保守257.6443102秒只属该段。

## 四项一次修复的完成合同

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

允许修改既有三个定向测试 test_step018_control_snapshot.py、test_step018_flows.py、test_step018_embedding_contracts.py，新增 backend/tests/test_step018_audit_repairs.py 与必要的 backend/tests/fixtures/step018/s07_ 前缀离线夹具；新增 frontend/tests/step018-s07.mjs 及必要的同前缀loopback夹具。fixtures只能测实际产品，不替换实现。README.md、config/integration.example.json 仅更新实际manifest/告知限制及本轮精确状态。frontend/dist 仅由获准正式构建生成，旧bundle7先另存完整字节和hash，不手改构建产物。

新工程证据仅入 D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-117/execution/continuation-06/，原 execution/budget.json、events.jsonl、case-index.json 按原机制追加本段，不回写旧段。原报告只置顶 S07 保留79709字节后缀。局部文件锁测试的自建合成hub与测试浏览器profile必须归本轮准确目录，关闭句柄/进程并保留文件；不要批量删除任何旧证据或临时目录。

禁止修改001—014、数据库/持久模型、来源资料/已sealed包、全部旧控制根与selector/fence、权限/退款/停止/preview安全语义、固定镜像/renderer/签票器、依赖/锁、公共提示词、原始需求/DocuS/任务卡/主控裁定/独审原件、Git HEAD/index/config及远端。不得安装/联网/读取真实密钥/用户配置或DB，不解DPAPI，不commit/push。GitHub origin现有https://github.com/shspic/RetroLume-agent.git保持；公开候选清单可按本轮源/README变化更新，但不上传。

原source已frozen，正式selector已永久readonly，全部六PG容器和原owned/preview都不得启动、修改或清理。本卡PG/SQL/Docker/产品API/Windows业务监督/真实provider/费用的新增执行额度全部0。D01用隔离真实本地文件锁，D02用实际gateway+合成ledger/最低transport，D03/D04用正式dist+本机合成HTTP；不需要配置真实key，也不需要新normal数据库。真实PG roster SUM/两provider持久预扣共同提交的组合补证保留在后续Q前置，不用本卡替身结果冒充它已通过。

## 新段前向预算、完整验证与自动停止

许可 TASK-117-STEP018-AUDIT-REPAIR-S07-20261017，从本卡实际接收首次工具同步UTC和宿主单调时钟起算，有效日历48小时、活动21600秒含最后1200秒清场保存。到20400秒不再开启新修改/验证族。所有阅读、思考、编写、验证、等待观察与保存计活动；账号/平台意外中断无预记暂停则保守保留，不能事后追造暂停。确需等待外部输入，先停止全部自有资源、采钟并写pause后才停活动，恢复先写resume；48小时日历不延。保存时预留末尾复读开销。

本段离线子进程wall-time总上限3600秒，包含compile/typecheck/build/定向测试实际进程耗时，不是CPU；不另设跨账号中断的第二滚动offline门。实际runtime持有总上限3600秒，持有指本轮loopback静态/合成HTTP服务器或浏览器任一存活的区间并集，不能让资源等人；其它未持有区间与历史保守口径分别记录。旧全部时间/超额不重算。

最多3个完整合成浏览器验证根，编号继续25—27，历史roots24保持。每根最多1500秒检查+300秒清场，仍受本段活动/持有先到门约束。普通修正可在原根原截止内继续；根是一次完整受控会话，不把每个单元测试/语法检查算新根，也不把独立启动藏为同一根。没有修正或新证据不得重跑，同一缺陷两次有据修正仍失败即停相应依赖。

本段 Browser启动最多3次，累计至19；frontend正式build最多2次，累计至9；合成HTTP服务器启动最多3次独立记fixture_server_starts，不能冒充原产品API调用或从账中消失；本轮全部实际HTTP至多600，累计至2924。PG创建/对象/卷各6、PGstart46、产品API33、Native140、preview各2、provider/费用0均冻结不加。Q旧预留根不挪给S07，未来仍须独立明确许可。本段不变成“用满预算”的目标，全过即停。

浏览器与本机HTTP只监听127.0.0.1:18119；启动前只读核空闲且无本任务旧进程，已占用不杀用户进程/不偷偷换端口。测试浏览器profile只存本轮目录，显式拒绝外部URL/请求，若实际出现外部尝试即阻断并留证。合成fixture响应须封闭且不取用户数据，敏感配置不进argv/日志。最低768MiB物理可用内存才启浏览器，单HTTP夹具512MiB；约2秒采样，连续两次低于256MiB即停止新增并关闭本轮准确进程树，禁止杀用户进程或全局清场。Docker不需要暖机，不能再要求用户腾2GiB。达不到仅停物理依赖，其它实现与离线交付继续。

开首个runtime根前先完成三件事。其一，计时/计数控制器用本段许可明确识别S07、读取原账和新剩余，不能fallback旧S06/初卡门。其二，静态检查browser脚本的路由、字段、实际按钮、owner/view窗口和准确后置请求计数，避免把显式POST计为自动重复；必要的纯函数自检不启动浏览器。其三，启动前已接好独立截止/压力清场、stdin/父退出处理和准确PID+birth登记，根finally等待异步观察结束后再关context并完整写日志。控制器超时必须能关掉自身fixture/server/browser；Agent会话断开不能让它们一直持有。

验证按完整修正集中运行一次。定向后端测试与typecheck先做，成功后一次正式build，再以该bundle覆盖D03/D04的最小场景。若真实失败，先保存原件、明确产品/夹具/环境归属，有具体修正才在原边界内复检；不要因几十秒失败就另开新卡。只有最终源码变化影响已测断言才复检相关项，不重新跑旧28场景、PDF/Job/恢复/两域全业务链。

最小证据含D01三条写入口foreign日志拒绝和合法对照；D02批准正常send/不批准各正文类别零send/准入后变化保守/旧Embedding和wire兼容；D03同activity late owner、view及scope或DataContext反例、正常一次POST、原键草稿保留；D04三处确认前provider/model用途额度告知与缺字段门。正式JS/CSS和页面实际fetch哈希、合成路由契约、请求时间线、截图、命令退出码/as-run/pre/post必须能相互对应。不把mock、typecheck或build单独称目标行为通过，不伪造真实PG/外网证据。

结束按原唯一工程账累计。新段delta与原累计并列，审计指出历史偏差留史不赦免；每次失败/修正/耗时/拒启动均记录，剩余不是原cap减本段从零。封存最终源清单与受影响旧结论继承说明，当前源码与被测字节的差异要明确。仅确认本轮已登记PID+birth、浏览器子树、服务器、18119无监听；原六CID/原业务停止只引用旧时点原件，不启动Docker求“更放心”，也不把本轮未查现场说成原PG实时停止。

## 停止、回传与独立增量复核

四项完整交付或真实硬门先到即保存，必要时间给清场和复读；同缺陷两次有据修正仍败、根因不稳、范围扩大、必须DDL/权限/费用变更、并行身份不明时停止对应依赖，其它不受阻部分完成后统一回传。不能为了绿色删测试、弱化身份校验或把必需动态项标成已过；达限不暗增根、监听、build或账号预算。

保存并完整复读 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-117-result.md，S07置顶、旧79709字节精确后缀。先一句真实结论，再逐项D01—D04修正/有效验证/未验证、actual接口/manifest与兼容边界、完整差异/pre/post/as-run、原始失败和合成层限制、资源停止及段/累计账、待同步与下一步。建议状态候选，不填主控最终验收。

完整稳定后交回原TASK118独立审计上下文作一次增量复核，只看四项实际diff和必要反例，继续复用本轮独审其余有效结论；你不向其转实现聊天/思考/自评。本卡不代审，不重开全面审计，不启用Q。后续Q仍需官方当前条件/正常本地secret loader、新normal合成库/控制根、真实持久共享总门组合证、实际清单/费率/72h及主控启用回执。

必要用户动作仅转交本卡，无需提供密钥、删除资料或手工运行代码。DocuS/编号/总状态由主控串行维护；经验只报已解且已验证的候选，不写公共库或错误经验共享编号。确认结果真实保存可读后，回复只给一句结论与可点击的完整结果绝对路径。
