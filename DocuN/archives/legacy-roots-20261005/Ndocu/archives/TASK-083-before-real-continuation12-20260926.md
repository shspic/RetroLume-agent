# TASK-083 / R-077 — D3审计问题合并修复11
接收原083增强实现窗口（当前Codex desktop/GPT-6，实际标签如实登记）；原窗口不可用才同等能力新窗口接续。涉及事务截止、停止证据和验证进程控制，须增强执行；不得自担独立审计。TASK083/R077，STEP008局部；父082，关联084/R078、NFR002/003、SEC002、FLOW005、DATA007。
项目根D:/shspic/project_NO3_RetroLume-agent；需求v1.1、架构v0.43、执行状态v1.61；Git基础45951501d2741630a229762d6b2d3f4b34d7f702及全部后续差异保护。
授权：用户已批准D3一列恢复；编排现接受review07确定问题，授权本卡一次合并范围内修复和定向离线验证。覆盖旧083“全部冻结”的写入限制，但真实PG/Windows/容器仍冻结。本卡待转交；普通修正卡内连续完成，不逐项交回。

## 唯一完整成果
交付可供独立增量审查的完整D3修正版：P1/P2产品修复、F1夹具修复、保留F2/F3、R1/R2/R3运行控制修复、实际影响定向离线证据，以及一次性剩余真实验证所需的场景/资源生命周期准备。不是单点补丁，不停在方案；本卡不启动真实资源。
本批必需分界仅为已明确不安全的Windows运行控制在真实进程启动前须由原084核过修正增量。后续仅审改动和新证据，不重审review07已通过部分；不得要求重跑Job07/PG08/09以美化证据。

## 最小充分输入
入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md；
公共D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD（同窗已读未变复用）。
读Ndocu/results/TASK-083-D3-work-decision.md批准合同；
Ndocu/results/TASK-084-result.md仅置顶review07全文及Ndocu/evidence/task-084/review-07/对应定位/差异，review06既有Windows条件按有效上下文复用；
Ndocu/archives/TASK-083-before-review07-repair11-20260925.md保留原10完整契约与实际停止门；
必要原始产品/测试/runner、d3-implementation-10/pre、offline-01、replacement-20260925-195448的失败与停止证据。不展开全部项目史。
先核review07/hashes.txt九文件作为基线，真实hash一致再保存本轮pre字节/hash。未知外来漂移报告且不覆盖。两项已经修而未运行的F2/F3不是历史通过证据。

## 合并修复契约
1. P1（repository.py claim/inspect）：采用审计给出的最窄方案，恢复原claim“所需来源/活动锁已取得后采样主机UTC墙钟”的口径；inspect同口径在取得锁后判租约/活动截止，删除用事务开始时间充当当前时间的控制判断。保留updated_at等无关SQL原语义，不改其他时钟路径，不采用未经本卡批准的新DB时钟模型。低层参数、来源→活动锁序、SID/G CAS、原额度/折叠/None提交/关闭门/受限幂等保持。墙钟仅资格判断，不是实际单调耗时保证；锁后再采样不宣称绝对硬实时。准备真实来源行锁屏障跨deadline及旧租约边界的定向PG断言，本卡只准备。
2. P2（session.py）：明确跟踪本次处理的旧树/旧句柄确认状态；terminate失败、查询异常、wait_empty=False、close失败、Open错误无法确认存在性时不可返回cleanup_incomplete=False。旧running未获得已确认新claim/折叠结果时，返回账目None表达未知，不把初始0当旧账实际事实。SID不符/NULL/部署前提缺失/有效租约有意拒接的语义明确区分，不宣称整活动已清理，不误杀有效树；允许保留已有state并补清晰诊断，无需为每个分支新建平台。未证树零不能以最后句柄已close替代实测正证；失败关闭不退款、不spawn。保留取消/已settled结果持久事实，不能因清理异常把已经提交的结算伪装未提交。检查launcher/supervisor结果消费者是否已正确接收None和cleanup状态，只有必要直接适配才改并列明diff。
3. F1：d3_pg_windows合法旧G接续保持原SID=0；DWORD上界在另一pending活动初领并查询持久值，不把跨SID拒绝误写成合法成功。F2 errors.CheckViolation和F3全部合法parts白名单保留，静态检查同链异常/rollback/选项解析，不为迁就失败削弱断言。
4. R1：修复真实验证控制者先Popen运行后取身份的窗口。所有可启动受测SUP/worker的子进程先悬停创建，精确句柄/PID创建时间及外层受控进程树归属建成后才Resume；使用已有项目控制原语为先，只在本测试范围补必要机制。外层独立绝对截止必须不依赖被测进程响应，runner死亡也有已建立的OS归属收尾机制；需终止时确认外层自有整树，不以taskkill返回码、父进程退出或业务Job句柄close当树零。控制者持有外层隔离对象不得保活被测业务Job最后句柄，不干扰所证明的D3语义。归属/清理证据缺失置unknown、停全部后续启动，active_proc不可未清理就丢引用。精确说明悬停创建失败/Assign失败/身份读取失败/超时/close异常全出口，禁止按名称、端口或裸PID清理。允许测试专用小控制模块，不改生产进程框架或再加常驻平台。
5. R2：建立明确的所选场景→唯一结果契约。所选各场景逐项完成且真实断言成功、exit0、清理确认才PASS；缺项/重复/未知场景、部分complete、all_pass缺失或矛盾、非零退出均失败。保留stdout+stderr原文并按约定判，不把stderr是否为空当唯一依据；顶层不能吞BaseException后exit0。每attempt独立目录，运行脚本字节/hash固定，原错误和cleanup错误分栏，实际未运行与失败严格区分。删除把固定mutex_release文本冒作观察证据的声明；可标为源码/单元证据，若采真实事件则不得改变互斥语义。
6. R3：每一步使用同一绝对总deadline/批deadline及必要场景deadline的最早值，耗尽/不足收尾余量直接拒绝启动，不用max(1,...)复活期限。≤30秒真实场景应由控制者主动截止，不是结束后才assert；单命令≤60秒包括启动、等待及该命令收尾，批≤10分钟含60秒总收尾预留。所有communicate/等待/终止共享剩余额度。明确禁用子进程PYTHONOPTIMIZE，核sys.flags.optimize或用不会被优化删除的raise断言；不修改用户环境。相同要求覆盖资源命令与认证，不能通过换helper另起无限deadline。

## 真实资源续接准备（只写代码/方案，不运行）
优选只复用已停止的精确替补CID：
85242648b70dc11839a93de29a51bc7e492390d8ad479036c141f37b26f4f6a7
run=20260925-195448；phase=d3-10；retrolume-task=083；
image sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f；
唯一匿名卷11140b6c41401e2cef58ef2743357938db543c5891a3a8d68fce87a60cb85e07；
loopback55439→5432，1CPU512MiB/pids128/restart=no/bridge，无宿主bind；
数据库retrolume_task083_d3、测试角色task083_d3。
准备一次连续runner的可审查路径：核完整CID/标签/镜像/卷/端口/无其他任务→在未来明确授权下启动→仅尝试容器内本地认证与测试身份/权限核对→内存生成新随机口令、通过标准输入安全轮换该测试角色→loopback新凭据身份核对→剩余PG/Windows→精确停止并复核。必须承认当前未证明本地认证/改密权限可用；失败就同CID收尾，不读旧secret、不关认证、不换账号扩大权限、不创建容器。新凭据不进入argv/日志/文件；同runner持续持有至允许定向复验结束，任何退出不得引出隐式restart或读回口令。
本卡不授权上述启动/认证/轮换执行，仅让代码与具体条件一次准备齐。第三容器仍禁止；另一个首容器不触碰；不删除旧库/schema/卷。若不读旧secret无法成立，精确报告阻塞，不自设绕过。
原真实预算已用1批/1PG/0Windows，上限3/3/12；原离线3批及资源2容器全保留。真实累计30分钟不重置；记录7.859秒+首次另行收尾（未知精确数不得补造）+81.765秒。后续编排另定保守剩余窗；本卡动态资源额度0。

## 最小定向验证与投入
本轮新增离线授权专用于上述新修正：使用backend/.venv/Scripts/python.exe，-B、不写pyc；首次一批+最多两次有明确修正依据的受影响复检，共≤3命令批，每批≤60秒，合计≤180秒。每批可在单入口顺序包含必要compile和多个定向单元，预列精确ID、运行hash、预期与依赖。原3批不是清零，本轮独立记repair11离线账。
- P1用已有仓储结构的定向逻辑/采样顺序检查，不造SQL字符串断言或mock声称事务通过；核心跨锁证据仅准备真实PG用例。
- P2补真实生产run_once控制流的替身例：旧wait false、查询异常、close失败、SID不符/NULL、Open5/87、有效租约拒接，核None/cleanup/state及无claim/spawn/退款；避免复制实现自证。
- F1合法同SID与pending上界的断言准备核对；已有D3六项仅实际受影响者运行，未变Open错误码与offline05不机械重跑。
- R1—R3必要纯替身验证最危险的失败控制流：身份/归属未成不得Resume、超时/未知停止阻断下一项、期限耗尽不得启动、非零/缺项/伪complete不能PASS、assert优化保护；不靠字符串检索代替行为测试。本卡不启动真实进程/Job/Docker，禁止把替身PASS记真实控制已验。
- 真实待运行清单一次准备：migration_empty/old/rollback及完整域；ledger_active_lease_rejected/new_g/exhausted；P1来源锁屏障；旧G/C幂等不污染新SID；windows_recovery精确旧Job销毁/Open2/固定SUP/新G真实PG结算。按parts/逐项结果/failfast可执行，已有仅空迁移与-1局部事实保留但不假定整项通过。
三批耗尽、连续两次修正仍失败、根因不稳或需要扩大信任/持久模型，停止对应工作并一次带全部成果返回。不为每个helper重新计额度。无本卡真实资源许可，任何离线修复成功也不能自动进入PG/Windows。

## 写入与保护
允许产品：backend/app/activities/repository.py、backend/app/worker/session.py及必要结果消费者适配；如必须更改windows_job底层合同而非复用现接口，先交具体差异，不扩大生产进程框架。
允许测试：backend/tests/test_d3_recovery.py、test_worker_session.py、直接受影响task083 fixtures、必要测试专用控制模块；新本轮runner/辅助代码只在Ndocu/evidence/task-083/d3-repair-11/，不要覆盖d3-implementation-10任何旧runner或证据。
允许结果Ndocu/results/TASK-083-result.md置顶11保留历史。所有目标先pre/hash，最终diff/hash与审计基线相连。
禁止改001—006迁移、gateway/transport/HTTP/PDF/runtime、依赖锁、正式docu/公共库/记忆、用户配置或用户库；不联网安装、Docker/PG/Job/真实spawn、真实模型、Git提交/推送。除本卡离线测试外无运行授权，不触用户进程。

## 交付与停止
统一报告P1/P2/F1/R1—R3逐项实现、F2/F3保留、完整接口/结果语义及消费者、产品与测试边界、每批真实命令/耗时/exit/hash、尚未验证的真实行为、确切资源续接条件。修复可编写/可离线验证≠运行门已开。
给原084准备最小可复核包：pre→post完整有限diff、冻结hash、必要新单元原始日志、最终runner从入口到清理完整路径、剩余真实场景ID表；不要求审计重读已不变的D3全部模块。
达到上述完整成果即停，等原084实际增量复核和编排资源授权；不签M-1/STEP008、产品接线或安全最终通过。完整结果保存并确认可读后仅回复一句结论与绝对路径，由用户带回编排。