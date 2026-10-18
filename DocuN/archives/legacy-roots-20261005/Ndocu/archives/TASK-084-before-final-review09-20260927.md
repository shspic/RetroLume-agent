# TASK-084 / R-078 — review-08 修复11独立增量复核与真实运行门裁定
接收原084独立增强审计窗口，承接review07，未参与083代码/夹具/runner实现。沿原隔离上下文；原窗不可用才新独立增强窗口。不按模型名称重做有效工作，记录实际身份。TASK084/R078，STEP008局部，父083，关联082、NFR002/003、SEC002、FLOW005、DATA007。
根D:/shspic/project_NO3_RetroLume-agent；需求v1.1、架构v0.44、执行状态v1.62；Git基础45951501d2741630a229762d6b2d3f4b34d7f702及全部现有差异保护。本卡待转交，零动态资源许可。

## 一次完整成果
只审修复11实际增量：给P1/P2/F1、R1—R3逐项关闭或明确剩余缺陷结论，核F2/F3与有效旧证据适用性，裁定完整剩余PG/Windows链的静态运行条件是否具备。审查一次覆盖新controller/contracts/runner的完整可达流程，不能每发现一个首错即返回；不重审未变006/Windows基础/D3批准模型和全项目。
本卡是已要求的修后独立门，不是新一轮探索。若无确定阻断，明确哪些剩余事实只能在受控真实验证取得，不能因它们尚未运行再要求相同前置准备。若有阻断，给合并最小修正及受影响复验范围。不要把非阻塞观察或有限故障模型外假设自动升级为新平台要求。

## 入口与独立读取顺序
D:/shspic/project_NO3_RetroLume-agent/AGENTS.md；
公共D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD。同窗已读未变复用。
先读Ndocu/tasks/TASK-083.md修复11完整合同、自己的review07问题和prelog、已批准TASK-083-D3-work-decision.md必要边界。
随后独立读d3-repair-11/pre及incremental.diff、runner-old-to-new.diff与最终八份源文件，必要直接依赖；先形成代码/控制初判留证，再读三批原始meta/stdout/stderr、offline_check三个检查入口以核证据覆盖及修正时点；最后读runner-walkthrough.md和083结果置顶11作为待核声明。不得读实现聊天或把执行者自评当证明。
证据根Ndocu/evidence/task-083/d3-repair-11/；原基线Ndocu/evidence/task-084/review-07/。同窗旧结论按未变方法/依赖复用，不全量复读旧07/08/09日志。有限hash/diff允许；未列直接依赖先说明其为何必需。
禁止读取/打印任何容器Env、完整DSN、口令、用户私有配置；只看脱敏源码和原始证据中非敏感字段，不执行被审脚本。

## 当前冻结SHA256（编排已现场核八项一致）
backend/app/activities/repository.py BCA8283316F62216F5BA94959F5C36F8C3395301AEB9DC7F21A9B376F92E29A3
backend/app/worker/session.py EB514B5F76B0DC8B43ED8DFE116D2DC7BE5A181011E1516FAAA4D8005461D71C
backend/tests/test_d3_recovery.py D5A5389D175E08EBEF01AD8CE1D7851745A3612271A30533E84108B146CF0C44
backend/tests/fixtures/task083/d3_pg_windows.py A1E419F34C6464FC588B5812A9AE95545E4074C8732130CC85D2251AF57CE3A1
backend/tests/test_d3_runner_control.py FC157323CDEF15E473FC847221E25DCA1CE382C10531F74C6F47922595402C66
Ndocu/evidence/task-083/d3-repair-11/controlled_child.py 14E20FCB63DB913E22FF05F4C8286C0A3D56FEE946A06DBB17E044635CF0E401
Ndocu/evidence/task-083/d3-repair-11/contracts.py A344AC5FBDF7C838C08C18FC1816D5D8E823C3FF67B1A98976CF11129257CBCD
Ndocu/evidence/task-083/d3-repair-11/runner.py 26ECB423DF5524EC834FFB96366ECC599F62764D648EDA63F30FB6EC73D3F731
其余006/windows_job/test_worker_session/offline_unit/旧runner沿review07及final-hashes.txt的UNCHANGED行；先核适用性，不运行旧检查。未知漂移仅停对应结论；结果文档本身后续编辑不等于源码漂移。

## 审查与验收
1. P1：claim与inspect确在必要来源/活动锁及fetch后采主机UTC，同口径判断deadline/lease；不再使用事务起点时间充当前时间，不顺改其他路径。检查新增FOR UPDATE对锁序/异常返回的直接影响。ledger_lock_barrier夹具是否确证真实来源锁等待、等待开始早于所需两时间边界、释放后断言具有辨别力；审查按固定超时是否可运行，不能用纯替身采样顺序代替PG事务证据。
2. P2：旧running拒接、SID/配置/来源/租约、Open2/5/87、terminate/query/wait false/close失败、claim响应丢失、新窗成功/耗尽及已提交结算各路径，None/cleanup/state语义是否真实一致；是否误退款或误spawn、泄漏句柄或把未知判clean。launcher/supervisor既有透传是否足够，必要直接核对，不要求无关重构。正常有意拒接与不确定收尾可保守报告，但不能错称旧账0或全活动安全。
3. F1/F2/F3：同SID0接续与独立pending上界分离；最近旧G/C分支是否真的覆盖原承诺（同G同C确认/冲突或更旧拒绝按实际分支命名），不得把仅异常拒绝夸成所有幂等通过。迁移/ledger/windows每个selected场景与contracts所需ID严格闭合，错误捕获、事务rollback、完整消息先后顺序均可达。
4. R1新控制层：悬停→身份/精确句柄→外层Job归属→Resume顺序；Assign失败/身份失败/超时/查询/close异常均可确认自身对象或准确unknown；外层Job无业务Job句柄观察者效应，不允许breakaway绕开收尾；正常/故障的树零与句柄完成正证是否足够。
针对“Create悬停后尚未Assign时runner猝死可能留下悬停进程”的声明，明确区分不会执行SUP与清理完整两种保证。依据本卡有限故障模型和真实控制门判断是否是阻断、可管理的未知停止边界或仅声明不充分；给具体触发/影响与最窄处置，不能仅凭有极端崩溃点要求再造无限看门层，也不能把潜在孤儿算已清理。真实嵌套Job行为尚未实测，给出一次受控运行中的验证位置，不自动要求重跑旧Job全套。
5. R2/R3：exact selected starts/results/parts/all_pass/exit/clean一致，缺项/重复/未知/部分complete不得PASS；是否有生产或控制失败被吞后exit0。每步使用绝对总/批/命令/场景最早deadline且真正预留收尾，读取管道、docker子进程、等待修正信号等不得绕过；优化保护真正覆盖执行子进程。原始输出、脱敏、哈希/脚本快照、attempt不覆盖及异常清理各自如实。无需扩建通用runner。
6. 离线证据：三批16/5/2项、exit0、2.7286574+0.7178588+0.9456941=4.3922103秒；后两批确有具体代码修正依据，最终hash对应哪些已执行方法、哪些仅静态结构检查须分明。一次核定有效证据及未验，不重新运行compile/测试，也不把不同批次计数求和冒充23个独立用例。
7. 资源复用路径：只读审runner中精确CID85242648b70dc11839a93de29a51bc7e492390d8ad479036c141f37b26f4f6a7的身份/唯一卷/loopback55439/限制/停止前置、显式授权门、本地认证身份与测试角色自改密路径、stdin新凭据/日志脱敏、同runner持有直到受限复验、失败同CID收尾。旧secret不取回、无第三容器、无降认证或扩大数据库权限。认证可用性/当前资源状态尚未知，只能未来一次有界试验，不要求本审计通过运行去证明。
给编排具体可启用的现有命令入口/必填参数、前置、剩余场景/结果ID及停止规则；若证据不支持安全复用，精确指出原因，不能暗中解冻或泛泛再提新容器。

## 预算与边界
本卡只读，写入仅Ndocu/evidence/task-084/review-08/和Ndocu/results/TASK-084-result.md置顶review08保留全部历史；产品/测试/runner/公共库/正式docu/记忆/Git/旧证据禁改。
禁止import/AST/compile/unittest、Docker/PG/Job/spawn/进程探针、联网安装/模型；动态0。本轮公共规则已核mtime未变，官方Windows依据沿有效review06，不额外广泛研究。
083暂停修改且真实冻结。旧D3已用两容器、1真实批/1PG进程/0Windows；尚余2批/2PG/12Windows仅账面；总30分钟不清零，首次另行收尾时长未知不得补造。新repair11三离线批已用完且通过，不再补跑无关检查。所有资源启用由编排收到本结论后具体授权，本审计不得自行start/轮换/创建。

## 一次交付
按P1/P2/F1/R1—R3给“关闭/仍阻断/证据不足”，说明代码层与运行准备层结论及范围；新增发现须事实定位/最短触发/影响/最小修正/必需验证，不把建议升级硬门槛。列可直接保留的旧结论、离线最终适用范围、不可声称的动态事实。
若满足静态门，明确“可在编排授权的精确资源和预算内进入受控真实验证”；PG/Windows实际通过仍待真实证据，不能用其未跑无限否决准备成果。若不满足，一次给完整最小修复清单，不提无关平台/重审/全测。完成即停，不签D3动态验收、M-1/STEP008或产品one_call。
保存可读后仅回复一句结论与绝对路径，用户带回编排最终裁定。