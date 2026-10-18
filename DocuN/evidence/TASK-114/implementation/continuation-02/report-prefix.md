# 续作02／审计修复 — TASK-114 / R-108

四项 P1 的合并实现及卡内定向验证已完成，提交稳定候选给原 TASK-115 / R-109 窗口做 review-01 增量复核。DEF034—037、STEP017/M-1 和项目总体结论仍由主控与独立审计裁定，本报告不自签关闭。全部自有消费者已停止；PG 成功物理对象 9/9、start 37/37 已到原累计门，不继续业务运行。旧结果全文 53842 字节作为本报告后缀原字节保留。

## 接收、字节与范围

许可 TASK-114-STEP017-C02-20261013；task_model / V4.0 / 公共 AGENTS CHG-0003，七锁定指纹实核相同。客户端为 Codex desktop，本窗口基于 GPT-6；平台未提供更细后端型号，A+ 只作资源安排标签。本轮没有子 Agent、独立审计接管、Git 写、安装、pull/build 镜像、真实 provider/模型调用、费用或公网。

接受锚点用首批 UTC 2026-10-13T08:54:00.903Z 向前取整至 08:54:00Z；mono 在 bootstrap 按同点观察推导，明确不是首批同时采样。全部读取、实现、等待间隔与清场连续计活动，没有登记暂停或扣除用户释放内存的间隔。原锚点、C01 历史、失败与计数保留在同一执行账。

原 C01 manifest 的 216 当前文件和 1 已移除输出均在改前核对；原 TASK-115 报告 37767 字节 / 7d34ec7e7f433effe3bf51367c68229a566dc525361a30c4b2c496702f4ca67a 未动。原完整 A—D 采用包不重写。唯一总账仍为 implementation/control；新的业务 Hub、资料、备份和恢复根都在 continuation-02/synthetic，旧业务控制/selector/凭据/包不使用为新执行权。

- [接收与改前原件](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-02/accepted.json)、[pre 清单](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-02/pre-manifest.json)。原结果、副本、旧 execution receipt/events 也在 pre。
- [最终产品与测试字节清单](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-02/final/manifest.json)、[最终原件与 diff](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-02/final/)、[每批 as-run](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-02/as-run/)。新增文件改前不存在，不冒已有 pre。
- [方法、离线 argv/exit/耗时与运行原件导航](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-02/final/method-index.json)。PG 方法的阶段 JSON、资源 UTC/mono 即时保存；部分 PG argv/exit 最终依工具回包回补，未独立同点采样的方法墙时保持未精确测定，不把 as-run UTC 冒成入口时间。

## 四项修复与合同

| 问题 | 最终正确行为 | 当前证据及实际层 |
|---|---|---|
| DEF034 / F01 | cancel 先记录 cancel_requested；执行者等准确同步消费者、撤权/停妥后才 cancelled。成功同时核 revision、前状态、kind/阶段与准入票据。文件、upload、restore seal、source tombstone、maintenance/selector 短 CAS 准入先胜后返回 operation_not_cancelable，不临终取 latest revision 覆盖取消。 | 六种 kind 的真实私有日志顺序；真实 ZIP/no-replace、ASGI EOF；实际新 PG last-load 后取消、source 两个先胜顺序和 activate/selector 拒绝点。 |
| DEF035 / F02 | 首次真正消费固定 process-clock-domain、started_ns、deadline_ns；每阶段传同 D，重试不刷新。connect/lock/statement/组件/文件和 source mirror 消费剩余时间；成功帧真实 COMMIT 返回过期，保留实际事实为未确认。新 completion_protocol=1 在成功帧返回后记录完成确认点，确认前 GET/列表不授成功；未知进程时钟域/旧 inflight 不补 D。 | 真实新 PG capture + 精确发布前延迟 2.1 秒、实际文件失败；迟到成功日志返回和 source mirror 延迟的最终真实日志/文件断言；allocation/加载边界低 profile 的受控工厂断言。 |
| DEF036 / F03 | refresh 序号、Abort 与完整生命周期保护全部提交；同 control 代次不降，同代异实例拒绝，异 control 仅受信新会话 bootstrap。数据依赖读/动作与稳定 Hub GET 区分，旧键仍可读。主页面材料与阅读缓存同步清理，旧草稿不串写。 | 最终 dist 实际 Chromium 反序回包、错误实例/control、旧计划、类别变化、unmount；另实际 TCP + sealed PG + 最终 bundle 身份/正文/旧 Hub 键。 |
| DEF037 / F04 | 同一 READ ONLY / RR 中复用 memory_revision_readable，并覆盖 source/event/upstream 与墓碑；false/unknown 不给 body。派生历史核原 source_refs/catalog/reference_hashes/memory_refs 和所选记忆资格。读取入口固定 ledger/身份，再在同 T 核库身份。头、版本、存储正文、原 hash/purge 不改。 | 实际 normal 新 PG 有效样本、替换失效、上游更新、事件修正、source deletion；真实 HTTP learning/teaching/interview/memories；默认 overlay 恢复后删除依赖正文为空，有效样本仍可读。 |

新增 operations.py / readability.py；必要改动集中在 data_exit 的 api/control/packages/snapshot/restore/repository/deletions/reference/config/maintenance/files，前端 data/context、workspace、records、dataApi、main，README 补取消与不可回查文案。001—013、schema/codec、角色 ACL、业务表/列、原生成/预算/StopProof 核心和依赖锁未改。frontend/dist 两次有计数构建均 typecheck/build exit0，最终 index-NDc3grUN.js 已由两类实际 Chromium 使用。

新增私有字段：execution_protocol=2、completion_protocol=1、execution.clock_domain/actor_id/started_ns/deadline_ns/admission.phase+ticket、completion_confirmed_ns；均不进包或普通 DTO。旧真正 terminal 只读保留，包括本轮较早已完成且有真实证据的 terminal；不倒填字段追认许可。旧 prepared/inflight 缺新闭包或时钟域不符，不能启动或重新发 D；旧清理只在原 D/时钟域有效且原票据对应时才可继续。

状态增加 cancel_requested、committing、completion_unconfirmed 的投影及 restore_unconfirmed/activation_unconfirmed/cleanup_unconfirmed 等；cancelled 是已确认收尾。upload 收据补 upload_id 与 file_publication=confirmed，仅核现有文件，不将未知时钟结果改成 received；saved-records 返回固定 data_context。稳定 Hub GET/原键、包/计划历史保留；数据依赖读的旧身份 409 selection_changed。data API 输入校验固定 422 invalid_input，避免默认 validation 的 input 回显秘密。

签名变化完整以 final/diff 为准：ControlHub.update_job 的 expected_states/validate、change_job；PackageReader/hash_file/publish/artifact 的 check；capture、allocate/start/initialize/load/seal/probe、DataRepository.connection/state/latest/observe_job、source validation/observer、MutationGate.acquire/permit、reference cleanup 的可选 Operation；joined_thread 等准确消费者返回后才传播重复协程取消。原 Native/模型/preview 调用省略 Operation 的行为继承，无原时钟重置。

## 分层验证与导航

### A — 最终真实文件、私有日志和受控边界

[离线日志及 cases](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-02/offline/) 保留全部版本和 FAIL。最终受影响复验 exit0：六 kind 两种顺序、三个原反例点、低 D 后段、真实成功帧返回点与 mirror 迟到、真实 spool/copy/fsync 故障、同键文件/上传补确认不重复制或重流、未知 clock-domain、JSON depth/component 恰界超一、重复 coroutine cancel 等真实消费者返回。半注册、seal 后故障与 allocation D 用受控工厂，不冒物理 PG 故障。

Windows 实际 junction/reparse 与有效 ZIP 经重定向父路径均拒绝，10a-external-before 与 10b-external-after 分别保存哨兵文件集合、长度和 SHA；不是“目标外零写”的字符串断言。链接保留供审核，没有全目录清扫。

### B — 实际 PG / 角色 / 文件闭包

- [源最小依赖、取消、九 guard、默认计划](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-02/batches/c02-pg-source-resume-1159215656000000/result.json)。normal 共同 data_mutation_enter 通过、data_loading_allowed=false；九个指定 guard 均实际 P0001 并核函数 context，非 frozen/42501 或零行 UPDATE 捷径。负例采用新合成 admin 验证连接，未给普通 app 加 owner/admin/loader；普通权限层继承原已通过范围。
- [target02 实际加载后取消](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-02/batches/c02-pg-cancel-1159293593000000/03-cancelled-stopped.json)。在既有管理连接核实际 loader/admin NOLOGIN、密码清空；准确停止，failed 对象不复用，未 seal/verified。
- [target01 默认 overlay 正常恢复](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-02/batches/c02-pg-normal-1159441609000000/03-verified-sealed-stopped.json)。实际载入 64 行、2 原件、9 组件，完整链同 D，31 域读/原拒写 probe、撤 loader/admin 后封存。它是必要传播，不替代或重跑旧 94 行/4 原件/14 组件证据。
- [维护/selector/正常只读选择](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-02/batches/c02-activate-1159966015000000/result.json)。cancel 先胜不进 fence；实际冻结 source、目标 probe 后精确 journal selector 拒绝，保持 frozen、selection=None、目标停止。随后新明确确认完成本新域唯一 generation1 选择，准入后取消正确拒绝。没有冒真正 lost COMMIT 或自动回 normal。

### C — 原管理与停止链继承

001—013、codec/角色指纹和原执行核心未改；旧 C01 同 T、两锁序、共享引用/迟到 COMMIT、正常准确删除、真实 SUP/双 EOF/四账、永久只读和 115 认可归约继续引用原件。新增 optional Operation 的 default=None 路径不改 Native/工具/preview 原 ready/D/StopProof 或执行账，没有重审 G11、原 25 或制造新物理停止证明。

### D — 真实 TCP / 最终 bundle / 读取资格

- [source 真实 HTTP、低 D、TCP 中断、秘密扫描](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-02/batches/c02-http-source-1159676406000000/result.json)。Selector loop、实际 18114：memory false/true 与 head/body/hash 保留，learning/interview 删除来源正文抑制，合法 teaching 正文可读；Content-Length 未完断 TCP，准确 job failed、无 received 文件；同键 hash 冲突实际 409。
- [最终 dist 反序/生命周期/草稿](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-02/batches/c02-browser-1156168718000000/result.json)。实际 Chromium、受控 route 输入，不冒实际 selector。旧 localStorage/IDB 与独立草稿导出保持；refresh GET、错误回包不降身份。
- [当前 sealed 副本实际 TCP + Browser](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-02/batches/c02-final-http-1160210203000000/browser-result.json)。无受控响应 fixture，真实 sealed PG/current identity/最终 bundle；删除 memory body=null，有效 memory 可读、旧 Hub 键可达、刷新零 POST。旧 dataset header 的 saved-records 实际 409，而同 header 旧 Hub key 200。截图和 DOM 同目录。

秘密扫描用实际新合成 DSN/password/maintenance、实际 session/private marker 的内存 needles，普通 HTTP DTO/错误与真实 API log 零命中，不写 needle；session bootstrap 的命名 token 为明确认证出口，不冒普通 DTO 洩漏。未扫真实用户秘密，旧包扫描不扩大成所有公开面故障都覆盖。

最终后补的成功日志确认、source mirror/Gate 同 D 和 upload 只读补确认属于私有控制/文件适配：最终真实 Hub/文件断言已复验，未改 SQL、codec、ACL 或 frontend bundle。PG 正常 SQL/封存证据按作用继承，不冒在 start 37/37 后重跑新签名全链。实际磁盘/驱动卡死可强制终止、每个输入组合与全部半注册物理点均未声称动态通过。

### E — 范围一致性与保存

[AST/入口导入](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-02/offline/c02-final-imports.log)：158 Python 文件解析、必要入口导入通过，PG/API启动0。两次 frontend build/typecheck exit0，既有动态 import/大 chunk 提示保留。最终 source/manifest/diff、方法索引及原字节后缀保存并复读，没有维护第二共享状态账。

## 失败、投入与准确收尾

原 114/115 FAIL、异步两次60秒 timeout、G11/25/UNKNOWN/R60/count1/13元/626.566 全保留，不追认或抹去。F04 未第三次机械重跑旧未知异步诊断，改 Selector loop + 明确新 PG + 实际 TCP 取得动态结果。

本轮新增失败保留：默认沙箱 hardlink WinError5；一次离线 upload 方法超时，升级精确授权文件调用后通过，未签产品延迟；系统 Python 缺 psycopg 在创建前失败，改既有 venv，无安装；Docker 唤醒后内存门两次不足，均未创建/扣 PG create；夹具将已选记忆活动用于无 memory profile admission，产品正确拒绝，核3 source/4 memory/唯一 goal/零 model op前缀后接续，无重种或清零。自动审批一次因使用额度未能完成（非安全判定），操作未执行，超过提示恢复时间后原精确调用获准，没有绕过审批。

累计/本轮：root21/24（本轮3）；PG create9/12、success9/9（本轮3物理）、start37/37（本轮10）；Windows11/12且新业务Native窗口0；API8/11（本轮3）、Browser5/9（本轮2）、build5/6（本轮2）。preview/Vite/真实provider/模型/费用/公网/Git0。真实持有462.047秒：旧377.280、本轮84.767，含 Browser 控制进程与 Chrome 并记的保守上界。offline172.317秒：旧51.238、本轮121.079；余额未转账。

原 C01 活动最终9739.953、旧日历55525.796与旧净投入unknown保历史；115 root3/API3/Browser2/offline125.610/保守hold14.874/活动上界5490.683454独立保留。本轮最终活动与48h日历锚点见 [delivery.json](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-02/final/delivery.json) 和唯一总账，未记录间隔连续保守计，不暂停生产 D。

[准确闭场](D:/shspic/project_NO3_RetroLume-agent/DocuN/evidence/TASK-114/implementation/continuation-02/closure.json)：九个旧/新准确 CID/image/name/label/volume 均 Running=false/Pid0；十七个 PID/birth 原消费者结束；相关全部 TCP 状态为空。新对象、成功/failed 数据、卷、包、墓碑、selector/证据保留。原 Hub target07/generation1 未写；本新 Hub target01/generation1、新 source frozen 的实际事实另存。

## 交原115增量复核与正式文档建议

只核四P1、必要 V08/V18/V19/V20/V21/V22/V23/V24/V28 补证及真正传播，原已独审认可正常链/归约复用。本轮正常真实层证据、最终纯控制收口证据与限制均已列明，不把受控工厂/延迟冒物理故障。主控据 review-01 再更新唯一 DocuS任务/DEF状态和正式变更记录。本窗口未写 DocuS/AGENTS/原始最终需求/公共库，没有预派新任务。

---

以下为续作02之前原 TASK-114 结果全文原字节后缀，既有结论、失败、路径和预算不改。

