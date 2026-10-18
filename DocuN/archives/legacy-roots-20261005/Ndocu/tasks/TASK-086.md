> 2026-09-28：TASK-086 已由编排验收关闭其批准成果。最终裁定见Ndocu/results/TASK-085-086-final-acceptance.md。以下为原合同/历史状态，不再授权运行或修改；无阻断补项。

# TASK-086 / R-080 — 受控one_call接线独立增强审计
状态：待用户转交；2026-09-28。你是独立审计Agent，不接管编排，不修改实现、不运行测试。完成整卡后回传一句结论及完整结果绝对路径。

## 1. 目标与路由
一次审完TASK-085实际新增接线、原始动态证据及运行控制，裁定其在批准的内部切片内是否具备编排验收条件，并一次列全阻断项和最小修正/补证范围。不是D3重新设计、全仓审计或生产供应商连通测试。
TASK-086/R-080；STEP006/008局部；父085/R079，关联已关闭083/084、INT-002、NFR002/003、SEC001/002、FLOW005、DATA007。
接收当前客户端最强可用模型/最高可用推理档，增强执行。必须全新隔离会话，未参与085实现，不使用085执行窗口，不继承实现聊天/推理/自评。实际模型如实记录，不因标签重新审查已完工作。新窗理由是新增跨进程凭据、身份、停止/结果通道必须独立审计；用户手动转交，编排未自动派发。
根D:/shspic/project_NO3_RetroLume-agent；需求v1.1、架构v0.49、执行状态v1.69（本轮编排同步）；Git初始45951501d2741630a229762d6b2d3f4b34d7f702，保留未提交差异。
用户已授权转向接线及卡内实现验证，本卡为085合同要求的必要独立审计。代码/测试/资源全部冻结。无新运行额度，不因未用秒数重启服务。

## 2. 独立输入与快照
先读根D:/shspic/project_NO3_RetroLume-agent/AGENTS.md；
公共D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD。
仅需本卡和Ndocu/tasks/TASK-085.md完整原合同；按需读架构FLOW005的原需求/批准边界，不读顶部085回收裁定。无需WORK/其他阶段提示词。
禁止读取TASK-085-result.md、实现聊天/自评、delivery-check.json结论、完整共享状态/客户端项目记忆。意外接触如实说明，结论必须自行由源码/原始证据形成。
源码范围：
- worker的one_call.py新增；__init__.py、command.py、launcher.py、session.py、supervisor_main.py、supervisor_ipc.py、worker_main.py实际改动。
- gate.py、windows_job.py、activities/repository.py、capabilities/{contracts,gateway,transport,tools}.py、runtime.py只读直接依赖，先按差异定位读取，必要处完整上下文；不重审其未受影响的既有实现。
- backend/tests/test_worker_one_call.py、fixtures/task085/全六文件；直接依赖的test_worker_session.py/test_capabilities.py按使用读取。
原始输入位于Ndocu/evidence/task-085/：
pre/、pre-hashes.json（数组path/sha256，路径含混合斜杠，比较时规范化）；task085.diff；post-hashes.json（path→hash）；offline-01..05的meta/stdout/stderr；20260928T001119Z-77ba1b/{as-run-hashes.json,post-hashes.json,manifest.json,stdout.log,stderr.log}。
不以git空diff证明无变化，worker此前未跟踪。以pre副本、实际源码及新增文件组成完整差异；diff不覆盖的依赖自行只读核对。
输入清单冻结：
post-hashes.json SHA256=4694d1e42ce1b20bc5358a4c0810c30423ee3166a4970b4d1b52cfdd7cdda6df
pre-hashes.json SHA256=8253cc4b6de523821fdcbf08ddcefb5b4a0095567396d03975e55b8ca70d31e7
task085.diff SHA256=6177a07ad32ca4ca15790a477ec4597530514f86b3d0131520ba99dd2eeccd17
真实批manifest.json SHA256=5e1327028abfabfb67b18d3fd0ccfab763bd0ff9080fb8a41a6e13c2f47f16bb
post清单52项是当前内容基准，独立重算实际所审文件；清单相符不替代审查。冻结漂移停受影响结论，不对旧快照签当前通过。
真实批后两个测试文件run_offline.py/test_worker_one_call.py有变化，finalize_evidence.py后增；审查按各次as-run和最终差异分级，不能把最终测试hash反向绑定早先运行。需证明变化何以不影响被引用结论，不为hash变化机械全重跑。

## 3. 审查标准（逐项形成结论）
1. 入口到实际执行身份：有限输入/固定模块/固定cwd/固定命令；SUP成功claim后产生G/scope/W_eff/stop_ns；请求不能自授代次或延长窗口。无余额、旧租约、取消、来源失效、短窗与缺配置是否在正确节点阻止出站。实际生产入口与测试自举的差别须逐层还原。
2. 消息与秘密：两层IPC的版本/strict schema/未知字段/类型（含bool整数）/重复键/非有限数/身份绑定/封套和槽容量/转义膨胀。明确默认服务限额与64KiB入口限额是否一致拒绝，不能静默截断。纯数据、无任意模块/路径/代码加载；密钥/DSN/正文不得泄露argv/log/repr/异常。检查Windows DACL/所有者含义、非继承、创建/打开权限、视图/句柄及清零顺序、失败路径所有权，不将随机名/SHA当认证或声称抵御同用户恶意进程。
3. 生命周期与时间：t0先预扣后启动、实际W_eff、stop_ns不可后移；网络/准入/记账/排空与总期限/清理余量相容；Gate实际包住业务调用、不可重开。新回执读取/IPC关闭引入的异常或耗时不能绕过树零/自有句柄关闭、begin_window_close、settle的既有顺序。杀进程/缺回执/解析失败不得误退款或伪成功；worker不代SUP结算。
4. 真实gateway和账本调用：admit→mark→send→record保持，至多一次调用，无工具自动执行、换operation重发或UNKNOWN降格；事件循环兼容。取消/旧G/来源变化的晚到结果遵循既有记录纪律。代码文本未变的仓储也需分析新调用影响，不能自动排除相关回归。
5. 结果语义：ModelCallResult与SessionOutcome区分；临时回执绑定所有必要身份，缺失/畸形/超限/旧回执失败关闭。模型SUCCEEDED/进程exit0/结算成功各自代表什么必须清楚；not_committed非业务写入授权。G3原子持久提交/重启读取未实现是批准边界，不要求本卡新增表；不得暗中发布被取消或过时代次成果。
6. 兼容与范围：协议2明确接受/拒绝，idle及原导出保留；现有所有实际调用位置不遗漏。只读仓储、001—006、runtime、gateway/transport、旧证据及无关文件未被暗改；未接HTTP/用户库/真实provider/工具循环。D3结论仅复用未变或未受新路径影响的范围，不将旧批准自动覆盖本次session/IPC。
7. 测试辨别力和证据：对照085六组要求逐项查源码断言、真实原始日志、pre/as-run/post适用性。特别检查测试专属SUP模块/worker argv/transport替换是否绕过需要证明的产品逻辑；固定生产入口拒绝场景到底证明了什么，成功替身链到底证明了什么。成功链使用替身是原合同允许条件，不能因未付费provider调用自动否决。
8. 运行控制与收尾：原始start/result/scenario_complete/总complete、批exit与外层进程exit、skip/失败记录、精确PID+创建时间、外层Job树零/句柄、CID/配置/卷/停止证据一致。代码资源控制是否真实有界且只接触任务资源；审查硬超时/异常退出的控制能力，但未触发分支不虚称动态覆盖。
9. 账目与异常分层：单真实批12场景不等于12次成功出站，12个SUP会话与7个实际worker分别核实；lease_conflict的cleanup_incomplete与“夹具仅DB旧租约、未创建旧树”前提分开判断，不能凭摘要清除unknown，也不机械当真实遗留进程。离线03失败及04修正、05新增断言不漏记；普通tuple/list语义修正不能弱化实质内容/身份断言。

关于API不确定性：先以源码/原始证据判断；如确实需要Windows/Python官方原文佐证DACL/映射生命周期，可有限只读官方文档≤4页（不向外发送项目内容），记录具体URL与支持范围。不扩展全网调研，不用论坛替代权威语义，不为已明确行为强制浏览。

## 4. 只读边界、额度与停止
只读上述目标和必要直接依赖；仅写Ndocu/evidence/task-086/、Ndocu/results/TASK-086-result.md。
允许有限文件读取/hash/diff与文档证据写入。禁止import/compile/unittest/PG/Docker查询或启动/EXPLAIN/应用/模型/联网安装，不读私有配置/凭据、不改产品/测试/正式docu/公共库/旧证据/项目记忆、不Git提交。
真实PG/Windows/模型预算全部0，本卡不动容器。083已关闭余量不继承，085返回后的余量不自动授权续跑。
覆盖本范围即停止，不做重复全面审计。确定严重数据破坏/越权先留证回报；普通问题完成全卡一次列全，给最小完整修正清单，不把每一条分成新轮。
非阻断观察须有现实触发/影响，不以理论无限防护、同用户恶意进程、完整G3/worker平台或Linux未实现升级本切片硬门槛。确定缺陷与证据不足分别标记；不能以接受风险替代必须独立判断。

## 5. 交付
结果必须回答：
- 独立性/实际身份/接触范围/冻结是否稳定；与085原合同逐项对应。
- 当前切片的代码结论、动态证据适用结论、资源控制结论分别通过/有条件通过/不通过/证据不足；最后给是否可由编排验收关闭085的建议，不签编排最终验收。
- 每一问题的严重度、文件定位、触发、影响、确定性、最小修正和必需验证；没有阻断明确写无阻断。非阻断单列，未验证不冒充失败。
- 区分生产固定入口与测试成功链；真实供应商0费用/0验证、G3未闭合及单机/会话边界保持。
- 如必须补验，逐项精确test/场景/证据缺口，只覆盖实际影响；未发现需补项则结束，不默认重跑12场景/全套D3。
保存D:/shspic/project_NO3_RetroLume-agent/Ndocu/results/TASK-086-result.md；
证据D:/shspic/project_NO3_RetroLume-agent/Ndocu/evidence/task-086/。
完成后仅回复一句结论和可点击绝对路径，由用户转交编排。