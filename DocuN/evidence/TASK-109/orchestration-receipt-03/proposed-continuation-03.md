# TASK-109 / R-103 续作03 — Crashpad启动环境收口与同卡真实诊断

## 目标与交付

你继续担任原109执行者，本轮合并补齐完整有界启动错误、受限运行目录环境与一次有依据修正；Browser可用后在同一有效容器内直接完成冻结counter的真实最小探针和精确停止，不再拿到启动子事实就交回另开卡。

仍TASK109/R103，报告置顶 D:/shspic/project_NO3_RetroLume-agent/DocuN/results/TASK-109-result.md，标题续作03，原37685字节/SHA 5a82ac39a8af1f483ccbdb055f5746bb94e0941b400908fd94281d6206c73741完整保作后缀；原27219/15176嵌套历史、R01—04/旧sessions/OCI/build/image及old as-run不改。新证据 DocuN/evidence/TASK-109/execution/continuation-03/。

完成标准是准确环境层因果、限定目录修正真实生效或具体阻断、能运行时取得当前Browser/手势/新页与导航原件、每次精确收尾。现image无生产NavigationGate，即使无反证也NOT_FULL_H0；业务四表/SQL/profile/模型/API/UI继续冻结，不自签B-01/SEC003/STEP/M-1/项目。需要超包能力就停依赖交精确差异，不绕启动去禁sandbox或crash组件。

## 项目、规则与接收安排

根 D:/shspic/project_NO3_RetroLume-agent；入口同根AGENTS.md。task_model/V4.0/AGENTS CHG-0003，需求v1.1、架构v1.05、唯一执行动态v2.27、阶段07。公共根 D:/spiritice/AA文件/MS_spi knowledge libraay/obsidian_1/&职业相关/项目流程/项目开发提示词V4；同窗未变规则/合同复用，补本卡与work-decision，七锁定指纹仍项目v4-migration-20260930/rules-snapshot.json。新正文/注释简体中文、不用星号/表格，旧原字节保留。

接收A+强推理，沿实际109业务窗口，实际身份如实登记；原107仍独立、不实施或泛审未齐业务。原G11-P采用和权限仍有效，本卡只既有tmpfs内目录/环境与诊断控制细节，不新增引擎/页面系统权限/用户数据/费用/Git。普通修正无需重复采用。

原root74非74PASS，TASK109 roots4/8、H0修订4/4、imagebuild2/2封存，preview/controller各1。原C02 R04 ERROR/4.656秒含stop1秒、窗口3.047、active958.5上界/metadata300保守/cleanup30保守/offline0.015、旧真实85.797含build27.017子段/全部FAIL/UNKNOWN/13元/旧重叠保持，不返失败。新action许可TASK-109-G11-C03-20261009，只补一个root、至多两个有明确用途的preview尝试；第二个只新完整错误支持的普通环境修正，不是自动再试。

原start774301594189000/deadline795901594189000保持不可延，首读固定≤1800秒子窗且不越旧总期；过旧deadline禁止真实启动，保存不受阻准备交回，不换日期/执行者延限。当前待转交，新使用0。

## 背景与最小充分上下文

C02真实Node v24.18.1/Playwright1.62.1/UID10001、二进制0b20b130e7edd9dd51873be867761295fe0cfad490c2b9a64f95bd3cfc08fa71、私有PID namespace/NoNewPrivs1/Seccomp2已观察。Chrome pid19确启动过，但没有Browser/CDP；“chrome_crashpad_handler: --database is required”可见，message正好2000字符截断，stderr空。不能断言HOME/XDG或权限唯一根因，container过滤状态不签浏览器自身sandbox。

原CID 5bd9e24d2a8ba06403f4daf4120aedcd7fe0ef4f0e3ae5f162b723918f189059 已kill9/die137/wait137/attach与线程结束，Stopped/Pid0/restartno/原PID核退出；namespace结束为推断待审，不假称已直接读停后cgroup空。该容器及image/cache/原件保留，不重启它。

现image aa824fa25eb0aae09cee50c10372fb218a7d86ffb10124b46074a5c1e977cc66/config e881d12c9e682de7e535386b9db353bfc95838c3bcea04332bcdffd9cc30e6ea仍固定。无新save/build/load/tag/包复制，host/counter/wrapper/包/seccomp/browser字节不改，旧111依赖与OCI/build子事实直接继承。

本轮输入 DocuN/evidence/TASK-109/orchestration-continuation-03-20261009/continuation-input.json给494当前对象、旧reports、selected HOME/XDG声明与tmpfs参数、真实error和stop指针。Config声明/目录未观测分开：旧tmpfs没有显式uid/gid，镜像XDG已指定，但活进程路径/归属/可写性未取，不根据stopped inspector推活目录。

[Crashpad手册](https://chromium.googlesource.com/crashpad/crashpad/+/76a67a37b1d01128ff21b900f49912753dc49d1e/handler/crashpad_handler.md)说明handler需要database和已有父目录；[Chromium旧版Linux文档](https://chromium.googlesource.com/chromium/src/+/refs/tags/133.0.6846.2/docs/linux/debugging_minidump.md)将目录放在XDG_CONFIG_HOME产品子目录。仅机制指引，不冒当前151的唯一根因或实际启动证明，不另做系列官方研究。

## 执行边界与资源

只新增本轮控制fixture及deploy/preview/runtime-bootstrap.cjs等固定可信运行目录初始化帮助源，必要Python helper极小提取/参数化留diff；不改变镜像内JS、不重build，也不直接修改包/原protocol/Sandbox/资源。全部old阶段source/session/as-run/证据只读，新as-run单存。源码/测试不依赖DocuN实验实现或用户私配。

普通修正先一次完整准备：HOME/XDG目录归属及stderr可观测性，不按每个目录再发卡。配置有限容量保持/tmp128MiB和/home/preview32MiB，明确tmpfs uid=10001/gid=10001，home mode0700；/tmp仍提供安全公共临时语义并由同UID建立private0700子目录。不给host bind、新volume/容量或root写权，read-only根和nosuid/nodev/noexec均保持。

容器环境显式HOME=/home/preview、XDG_CONFIG_HOME=/home/preview/.config、XDG_CACHE_HOME=/home/preview/.cache、XDG_RUNTIME_DIR=/home/preview/.runtime，必要TMPDIR指向同/tmp容量内private目录。只这些实际语义键，不把宿主HOME或真实配置传进去；脚本变量用runtime_home_dir等任务名，不改宿主全局环境。

固定受信bootstrap仅做上述tmpfs内mkdir/同UID mode校验和小额独占写probe、记录uid/gid/路径/stat/可写成功或errno，随后require镜像内/opt/preview/h0-counter.cjs。禁止chown系统目录/改/etc权限/任意路径/删除旧数据，probe最多1KiB/独占新文件不unlink；tmpfs随停止释放不宣其内容永久保留。目录不足记录事实，不仅access标记当实际写成功。

为保持同镜像且提供预初始化，本卡明确允许create时将entrypoint固定为node，并以冻结bootstrap源码作-e的唯一受信诊断程序；源码/argv hash在root前登记，不能从HTTP/页面/模型接cmd、路径或JS。程序不执行原件/资料，初始化后只进入原image counter；原正常入口/程序权限语义不变，image本身不写。捕获数据走原host.emit私有封包，bootstrap不能console.log原文本到协议stdout。

Playwright browser stderr日志只开本地已核pw:browser类别（或其实际必要error类别），在首次require前设置DEBUG，限定stderr≤65536字节，独立保存末尾≤16384和截断标记；不打印全部Env、source/用户数据/秘密，不启网络/所有类别。当前counter仍截2000，完整下层stderr另捕获；不能把这2000末尾再补猜成原生errno。若本地debug会写stdout，先固定到stderr而不破坏二进制协议，源码依据/限定类别一次核清。

不手动伪启动Crashpad、不给Chromium胡拼handler的database参数，不加禁crashpad/禁sandbox/ignore-default安全标志解决启动。Chrome profile继续由实际Playwright在已批准私有TMPDIR创建，路径/uid/实际创建结果可核。普通目录环境纠错不改Browser二进制、版本、NoNewPrivileges、capdrop、seccomp、CPU/PIDs/Mem/IPCs等原边界。

本轮最多两个新容器，固定名preview-02/preview-03（完整前缀retrolume-task-109-g11-），原preview01保留停止；每个不同nonce、同image ID、父TASK109/原permit归属和actionC03/attempt，create即冻结所有参数与输入源码hash。只第一个默认使用；第二个只有完整错误明确指出另一项在本卡目录/普通环境范围的纠正依据且第一容器stop已确认，才能启动，不复用结束根或复活旧CID。

新root最多1，编号R05/累计第75入口，预检前计。每个preview create/start≤1、runtime≤60/诊断≤15，两次序列总runtime≤120。controller/Reaper最多2，每次截止固定在同root与旧期内；原controller累计上限2→3明确修订，原已用1不返，未用第二个不必启动。计原root8/preview16，H0累计4→5，不允许另Root“继续读错误”。

首读active≤1800、metadata≤500、realroot≤600、offline≤120（最多2批各60，只确实变过本轮source）、独立cleanup≤300秒，原总截止不延；新官方研究0。save/build/SQL/PG/role/API/frontend/main-browser/native-model/provider/费用/install/Git0。任何类触顶/同因两修仍败/根因不稳/新权限即停，不借名义其他额。

每个容器保持pullnever/UID10001/networknone/read-only/cap-dropALL/no-new-privileges/seccomp原hash/privateIPC/SHM64MiB/CPU1/768MiB等swap/pids128/init/restartno/无hostbindsocketportsecret，仅现有tmpfs目录所有权/普通环境和诊断入口按本卡明确收紧。不可为了Chrome启动加root/no-sandbox/SYS_ADMIN/ptrace能力、取消seccomp或换镜像/引擎。旧资源不启不删。

## 验证、证据与审计关系

先完整准备并冻结首个规范环境及stderr，不机械重复原C02。活进程的目录UID/gid/mode与写probe、Node环境键、实际profile路径、Chrome filehash/argv/版本/sandbox、完整startup stderr分别记录，不把声明值或container Seccomp2当Browser通过。

首个规范环境能创建Browser，就在本容器同root直接沿counter进入正对照/B01/导航最小观测和停止；不交“Browser准备通过”再要卡。仍保首反证即停、真实2秒观察/目标frame/loader/document和可信手势辨别力。counter无完整同步否决器，一切无反证仍NOT_FULL_H0，不写PASS_FULL_H0/解冻业务。

首attempt失败时，先依据完整错误/目录事实分类：若明确剩余普通路径/权限条件在本卡内，给唯一最小修正，停止并确认第一CID后可在同root一次复验；新二进制版本不符、kernel/sandbox权限/资源不足或不可核错误不在目录修正域，直接交准确差异，不猜第二环境更好。不得同样Crashpad消息却无新因果依据再试；第二次仍败即收尾，原两轮错误不清零。

所有根及attempt的stdout、stderr、参数/源码、真实受控初始化、原packet/chunk/hash与时序、metadata/UID/cgroup/进程出生、错误层、旧build原件与actualimage/bootstrap绑定齐全。日志消息、退出码、版本宣称、Node运行及Chrome spawn/Browser/CDP/实际page成功四层分开；准备错误不冒权限反证，image版本不合不能修改version()骗检查。

编排原109完整任务仍未验收，C03充分完成环境与探针就停。本轮不签完整物理平台停止或独立审计；联合kill/wait/die/PIDnamespace/attach线程事实与推断明确保留，未直接cgroup证据不补造。原G3—G10/001—011/worker/Job/四账充分未改证明继承不复测。

如果真实导航反证成立，同轮只给必要一页最低推荐差异与需改变的信任/输出/组件/成本，不取消FR009或冒完成新引擎研究；如果是环境不足，给具体可核条件。不能因stage未齐派110泛审或扩新业务，原107保持独立。

## 停止与回传

新C03独立账追加，不写old R04/C02session/C01或原首轮；原TASK109 roots4/8、历史global74，实际本轮root发生后才为5/8与global75。旧FAIL/ERROR/UNKNOWN/13元及build2/2封存，所有秒数重叠保守保持。预检失败也计本root，两个attempt必须分别记create/start/controller/chrono/退出结果，不能把第一次叫免费probe。

单root内合理有据普通修复可连续到本卡第二个明确attempt，不延根/preview/old总deadline；同一错误无新依据或超scope即停止。过期不启动，保存不受阻准备；不换日期/模型/窗口重开额度。无需用户开Docker/跑命令或再次采用G11-P。

精确停止本卡02/03的CID/image/nonce/label和root/reaper/attach/events出生/命令树；kill/wait/原events/EOF/线程/Running-Pid-Restarting分层，没确认保unknown。no rm/prune/DROP/DELETE、daemon/store/sysctl/全局Chrome kill或旧106103100088启动，所有旧对象和新容器/image/cache/原件保留。

报告置顶C03，先准确启动根因/环境差异与前后证据、实际Browser阶段/首次真实探针或阻断、必要后续与停止；后源diff/as-run/参数/日志尾与截断、每attempt和原新预算/秒数、物理证明限度、所有业务not_run。不能以DEBUG开启或目录可写代Chrome成功，不能隐匿有据复验原错。

保存并核原37685字节精确历史后缀/旧sessions、当前source/image/links和新report hash，完成一次回传原绝对结果路径。共享DocuS/DEF/编号/最终验收仅编排维护，不自签B01/SEC003/STEP/G11/M-1/项目。

## 必要人工与待同步信息

用户仅转本卡当前C03前缀给原109 A+并带回原109结果；目录收口与完整stderr普通修正无需再批G11-P。真正新权限/新组件/主要信任方案变化先准确差异另裁。当前待人工转交、新实际0，原107不实施，110未占未派。
