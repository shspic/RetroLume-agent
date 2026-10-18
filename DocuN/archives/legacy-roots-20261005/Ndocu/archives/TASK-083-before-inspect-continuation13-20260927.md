# TASK-083 / R-077 — D3同容器受控真实验证12（编排已授权）
接收原083增强执行窗口（Codex desktop/GPT-6或该窗实际标签，如实登记），沿TASK/R和原预算；不可用才同等能力窗口接续，不自行承担独立审计。STEP008局部，父082，关联084/R078、NFR002/003、SEC002、FLOW005、DATA007。
根D:/shspic/project_NO3_RetroLume-agent；需求v1.1、架构v0.45、执行状态v1.63；Git基础45951501d2741630a229762d6b2d3f4b34d7f702及现存差异保护。本卡待转交，不代表已经执行。

## 具体授权与一次成果
用户D3一列恢复批准持续有效；review08已关闭P1/P2/F1/F2/F3/R1/R2/R3，编排接受静态运行条件。现在明确授权：只对下述完整CID完成停止状态/归属核对、一次启动、既定本地测试角色认证、新随机口令经stdin轮换、loopback身份核对，在同一runner生命周期执行完整剩余真实PG/Windows链及最多一次有依据定向复验，最后精确停止保留并统一回传。
此段覆盖旧卡对该精确资源start/认证/轮换及真实验证的冻结；不扩到第三容器、其他资源、真实模型或用户库。无需再就已经明确的步骤问用户许可。运行控制静态已通过，不先重跑离线或再出准备卡。完成/失败按本卡停止门统一返回。

## 读取与冻结
入口D:/shspic/project_NO3_RetroLume-agent/AGENTS.md；
公共D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V3/docu/AGENTS.MD；同窗未变已读复用。
读Ndocu/results/TASK-084-result.md仅review08有效段及review-08/postlog-assessment.md对应分级；
Ndocu/evidence/task-083/d3-repair-11/runner-walkthrough.md、contracts.py场景表、runner.py入口/收尾及final-hashes.txt；原D3批准合同和修复11未变上下文复用，不加载全史。
首次运行前一次只读核13项hash与review08/hashes.txt相符。未知漂移停相关运行，不覆盖外来改动；结果文档追加不构成代码漂移。
关键八冻结：
repository.py BCA8283316F62216F5BA94959F5C36F8C3395301AEB9DC7F21A9B376F92E29A3
worker/session.py EB514B5F76B0DC8B43ED8DFE116D2DC7BE5A181011E1516FAAA4D8005461D71C
tests/test_d3_recovery.py D5A5389D175E08EBEF01AD8CE1D7851745A3612271A30533E84108B146CF0C44
tests/fixtures/task083/d3_pg_windows.py A1E419F34C6464FC588B5812A9AE95545E4074C8732130CC85D2251AF57CE3A1
tests/test_d3_runner_control.py FC157323CDEF15E473FC847221E25DCA1CE382C10531F74C6F47922595402C66
d3-repair-11/controlled_child.py 14E20FCB63DB913E22FF05F4C8286C0A3D56FEE946A06DBB17E044635CF0E401
d3-repair-11/contracts.py A344AC5FBDF7C838C08C18FC1816D5D8E823C3FF67B1A98976CF11129257CBCD
d3-repair-11/runner.py 26ECB423DF5524EC834FFB96366ECC599F62764D648EDA63F30FB6EC73D3F731
前五项根为backend/，后三项根为Ndocu/evidence/task-083/；其余5项按final-hashes UNCHANGED行。所有已通过离线按review08方法级结论复用，不机械重测中间版三项。

## 精确资源许可
唯一CID：85242648b70dc11839a93de29a51bc7e492390d8ad479036c141f37b26f4f6a7
name=retrolume-task-083-d3-20260925-195448；
labels：retrolume-task=083，phase=d3-10，run=20260925-195448；
image=sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f；
volume=11140b6c41401e2cef58ef2743357938db543c5891a3a8d68fce87a60cb85e07，仅/var/lib/postgresql/data；
loopback127.0.0.1:55439→5432；1CPU/512MiB/pids128/restart=no/bridge，无host bind；
db=retrolume_task083_d3；role=task083_d3。
运行前必须由已审runner重核完整身份、停止状态、无其他活动083容器、端口空闲。当前未知，不能把旧停止日志当当前事实；不符合即BLOCKED，不清占用、不停止其他任务、不擅改端口、不另建容器。首容器1086a37d…和其余旧资源均不触碰。
授权仅按已审runner：容器OS postgres→本地socket以指定DB角色/库核身份→内存新随机口令经stdin自改密→loopback以新口令核数据库/用户/内端口。认证及权限未知，尝试失败即精确停止，不读Config.Env/旧secret、不改认证、不用管理员替代、不开外网、不建角色。口令/DSN不得写日志/argv/报告，子进程仅环境传递；runner退出后不再次启动取口令或重试认证。

## 启用入口与连续执行
工作目录项目根。仅一次启动已审runner：
backend/.venv/Scripts/python.exe -B Ndocu/evidence/task-083/d3-repair-11/runner.py --authorized-reuse --total-seconds 900
本卡就是该旗标所指的编排具体授权。不要再运行--help/import/compile/单元探针、旧runner或裸夹具绕过外层控制。命令长于工具一次返回时保留原运行会话，使用可继续读取的进程会话取结果；不因工具yield重启命令。执行窗须能在同runner等待期接收失败、完成允许的具体修正并写go；不能启动后遗弃，再等口令丢失申请新资源。
runner输出自动写d3-repair-11/continuation-<UTC tag>-<uuid>/。允许创建该新证据子目录，不覆盖repair11静态/离线证据和旧运行日志。记录本卡、runner hash、精确命令、整体/批/场景原始计时、修正前后fixture字节/hash、stdout+stderr/exit/结果协议/停止记录。

## 精确场景与判定（共8个，不是报告笔误9个）
初验parts固定migration,ledger,windows，按contracts顺序：
1 migration_empty：NULL/0/上界合法、负/超界拒绝；
2 migration_old：旧行NULL保留；
3 migration_rollback：失败事务无部分006列；
4 ledger_active_lease_rejected：有效租约不抢占、不误杀；
5 ledger_new_g：同SID0旧R全额折叠、新G/SID；另一pending测上界；旧G/C重试按真实分支拒绝或确认，不污染新窗SID/关门/R/S，不扩大声称幂等覆盖；
6 ledger_exhausted：折叠提交后None且关闭/清身份；
7 ledger_lock_barrier：真实来源锁等待在deadline/lease时间边界前已发生，锁后UTC判断，按夹具原始证据判别；
8 windows_recovery：真实旧Job/PID创建时间/可信SID、树空close/Open2、生产固定SUP新G与PG结算，外层控制器树零及句柄收尾。
每个所选ID须唯一start/result、精确parts/complete/all_pass、子进程exit0、无超时和cleanup不明；runner顶层exit0不是单独通过证据。没有到达的场景明确not_run。PG失败failfast，不进入Windows。不补测Job07/PG08/09旧全套；不另造Create/Assign猝死实验。外层真实进程及嵌套Job事实随本次实际链采集，不能据成功路径宣称所有崩溃分支实测。

## 次数、时间和修正界限
D3原总限30分钟不清零；既往已知7.859+81.765秒及另行收尾保留。首次收尾没有完整单调统计，本卡历史资源部分保守占账900秒（不是声称实耗900秒，原始未知仍披露），余下仅授权本runner900秒；这样不把未知历史当0，也不给新30分钟。初次资源/认证、测试、等待修正及全部收尾都在本900秒，启动后不得改deadline。每批≤600秒含60秒收尾、单命令≤60秒含相应清理、每场景主动≤30秒，最早deadline优先。
已用1真实批/1PG进程/0Windows；本runner最多再2批/2PG进程，原3批/3进程/12Windows总上限不变；本卡实际只计划至多一次windows_recovery。容器总2，无新增。
仅当初批在Windows开始之前失败，且外层树零/句柄清理确认、根因明确、不涉及产品安全/运行控制改动，允许同窗一次普通夹具修正（例如真实观察窗慢环境适配），保留pre/diff/hash；不得削弱锁等待正证、绕开断言、改系统/DB时钟或增加重试直到碰巧过。
在同runner尚活且尚余足够deadline时，把必要parts写入本continuation目录的唯一attempt-02.go。parts必须覆盖失败部分及尚未运行后继：migration失败通常migration,ledger,windows；ledger失败用ledger,windows；不要只复验ledger就把从未跑的Windows遗漏。已通过part不重跑，part内部因现有契约不可拆的复跑如实记录。不能复用旧go文件。开始第二批后无第三批。
runner的PASS可只代表第二批所选parts；最后报告必须把第一/二批证据按各自hash合并核八场景全覆盖，不能据局部PASS签完整链通过。两批间如改共享行为导致原PASS失效，报告影响，不擅自追加批次。
若修复需改产品、控制器/contracts/runner、身份/权限/资源模型，或根因不稳，停止本卡测试并收尾，带具体差异交回；不在活资源期间重新设计控制机制。Windows已经启动后失败、timeout、任何unknown树/清理即FAILED_STOP，不再复验，即使剩额度。完整成功即收尾返回，不消耗剩余预算补美观。
本卡新增离线额度0。hash/diff及修改后的必要静态阅读不算启动测试；不另开compile/unittest。

## 精确收尾与有限故障模型
只允许已审控制器对本次精确进程句柄/PID+创建时间和外层自有Job终止，需正证树0及句柄完成。Assign前runner意外死亡若留下悬停进程，不会执行SUP不等于已清理：停止全部后续运行；只在PID+创建时间或仍持有精确句柄能确认归属时清理，禁止按裸PID/名称/端口杀。无法确认则报unknown，不追求伪成功。
容器按已审finally核CID/标签→stop；失败才同CID一次kill→inspect停止，全部共享剩余截止。失败不得覆盖原错；结束保留容器/匿名卷/新旧schema，不DROP/删除，不把停止记录推断成今后永久停止。若runner已退出且其cleanup不明，只允许在本卡剩余期限内核精确身份作必要补收尾，无新测试/新runner启动；超限或身份不明交回。

## 统一交付
仅写新continuation运行证据、本卡允许的必要夹具修正及Ndocu/results/TASK-083-result.md置顶12，旧历史完整保留。禁止正式docu/公共规则/记忆、产品代码/001—006、依赖、HTTP/gateway/模型/用户库、Git提交推送改动；不联网安装、不启Docker Desktop、不新增容器。
返回完整八场景实况、PG事务及Windows身份/停止关键证据、资源身份/认证路径（不含secret）、真实命令/exit/计时/尝试累计、改动与hash适用、容器终态、运行控制偏差/未知及未验。单机单会话是部署前提，不冒充跨机证明。
全部真实证据回收后原084仅核新动态证据及本卡实际夹具修正；本执行者不自签独立安全验收，不宣告M-1/STEP008/one_call完成。保存可读后只回复一句结论及结果绝对路径，用户带回编排。